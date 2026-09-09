"""Independent durable account/timer lane; optional inference runs in processes."""

from dataclasses import asdict, dataclass
import heapq
import json
import multiprocessing
import resource
from threading import Event, RLock, Thread
import time
from typing import Callable

from trading_research.errors import ContractError
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import canonical_json
from trading_research.operations.journal import Journal
from trading_research.runtime.publication import ComputationRequest, VersionStore
from trading_research.runtime.scheduling import CostSample, QueuePolicy, RuntimeCosts


@dataclass(frozen=True)
class CriticalEvent:
    id: str
    lane: str
    received_at: int
    due_at: int
    payload: bytes

    def __post_init__(self):
        timestamp(self.received_at)
        timestamp(self.due_at)
        if not self.id or self.lane not in {"account", "timer"} or not isinstance(self.payload, bytes):
            raise ContractError("critical events require durable identity, account/timer lane and immutable bytes")


class CriticalReactor:
    """Handlers must be bounded, idempotent state transitions with no model work.

    A crash between handler commit and acknowledgement deliberately replays the
    same event ID. External exactly-once delivery is not asserted by this class.
    """

    def __init__(self, journal: Journal, handler: Callable[[CriticalEvent], None], *, clock=time.time_ns):
        self.journal, self.handler, self.clock = journal, handler, clock
        self._pending, self._ids = [], set()
        self._wake, self._stop, self._lock = Event(), Event(), RLock()
        self._thread = None
        self.failure = None
        events, applied = [], set()
        for entry in journal.read():
            if entry["kind"] == "critical_received":
                p = entry["payload"]
                events.append((entry["sequence"], CriticalEvent(p["id"], p["lane"], p["received_at"],
                                                               p["due_at"], bytes.fromhex(p["payload_hex"]))))
            elif entry["kind"] == "critical_applied":
                applied.add(entry["payload"]["id"])
        self._ids.update(e.id for _, e in events)
        for sequence, e in events:
            if e.id not in applied:
                heapq.heappush(self._pending, (max(e.due_at, e.received_at), sequence, e))

    def submit(self, event: CriticalEvent) -> None:
        p = {"id": event.id, "lane": event.lane, "received_at": event.received_at,
             "due_at": event.due_at, "payload_hex": event.payload.hex()}
        with self._lock:
            _, inserted = self.journal.append(key=f"critical:{event.id}", kind="critical_received", payload=p)
            if inserted:
                self._ids.add(event.id)
                # Unique sequence is deterministic for equal-time deliveries.
                sequence = next(e["sequence"] for e in self.journal.read() if e["key"] == f"critical:{event.id}")
                heapq.heappush(self._pending, (max(event.due_at, event.received_at), sequence, event))
        self._wake.set()

    def run_due(self, at: int | None = None) -> int:
        now, count = timestamp(self.clock() if at is None else at), 0
        with self._lock:
            while self._pending and self._pending[0][0] <= now:
                _, _, event = self._pending[0]
                self.handler(event)
                self.journal.append(key=f"applied:{event.id}", kind="critical_applied", payload={"id": event.id})
                heapq.heappop(self._pending)
                count += 1
        return count

    def start(self) -> None:
        if self._thread is not None:
            raise ContractError("critical reactor already started")
        self._thread = Thread(target=self._loop, name="account-boundary-reactor", daemon=True)
        self._thread.start()

    def _loop(self):
        try:
            while not self._stop.is_set():
                self._wake.clear()
                self.run_due()
                with self._lock:
                    delay = min(0.1, max(0, (self._pending[0][0] - self.clock()) / 1e9)) if self._pending else 0.1
                self._wake.wait(delay)
        except BaseException as exc:
            # The caller can observe a fault and inhibit entries. No silent loss.
            self.failure = exc
            self._stop.set()

    def close(self):
        self._stop.set()
        self._wake.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
            if self._thread.is_alive():
                raise ContractError("critical handler is stalled; risk lane has not safely stopped")


@dataclass(frozen=True)
class WorkerBudget:
    wall_ns: int
    cpu_seconds: int
    memory_bytes: int
    output_bytes: int = 1_048_576

    def __post_init__(self):
        if any(type(v) is not int or v <= 0 for v in (self.wall_ns, self.cpu_seconds, self.memory_bytes, self.output_bytes)):
            raise ContractError("optional worker requires positive enforced resource limits")


def _worker_main(connection, function, request: ComputationRequest, budget: WorkerBudget):
    start = time.process_time_ns()
    try:
        resource.setrlimit(resource.RLIMIT_AS, (budget.memory_bytes, budget.memory_bytes))
        resource.setrlimit(resource.RLIMIT_CPU, (budget.cpu_seconds, budget.cpu_seconds))
        payload = function(request)
        if not isinstance(payload, bytes) or len(payload) > budget.output_bytes:
            raise ContractError("optional worker result must be bytes within its registered output bound")
        result = {"success": True, "payload_hex": payload.hex()}
    except BaseException as exc:
        result = {"success": False, "exception": f"{type(exc).__name__}: {exc}"[:2000]}
    result.update(completed_at=time.time_ns(), cpu_ns=time.process_time_ns() - start,
                  peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)
    try:
        connection.send_bytes(canonical_json(result))
    finally:
        connection.close()


class OptionalWorkers:
    """Bounded queue, no market/order/timer events accepted here.

    One supervisor services isolated processes. It never owns the critical lane.
    Coalescing changes the decision population and is therefore always recorded.
    Unfinished accepted requests are explicitly abandoned on restart/shutdown.
    """

    def __init__(self, store: VersionStore, *, max_workers: int = 1, max_pending: int = 8,
                 queue_policy: QueuePolicy = QueuePolicy()):
        if any(type(v) is not int or v <= 0 for v in (max_workers, max_pending)):
            raise ContractError("optional worker and queue bounds must be positive")
        self.store, self.max_workers, self.max_pending = store, max_workers, max_pending
        if not isinstance(queue_policy, QueuePolicy):
            raise ContractError("typed optional queue policy required")
        self.queue_policy, self.costs = queue_policy, RuntimeCosts()
        self._context = multiprocessing.get_context("spawn")
        self._pending, self._running, self._accepted = [], {}, set()
        self._lock, self._wake, self._stop = RLock(), Event(), Event()
        self.failure = None
        # A callable is code, never an unversioned serialized checkpoint object.
        # Restore input requests in VersionStore; scheduler records name the work
        # that was interrupted and requires explicit re-submission at a new cut.
        accepted, finished = {}, set()
        for event in store.journal.read():
            if event["kind"] == "optional_accepted":
                accepted[event["payload"]["request_id"]] = event["payload"]
            elif event["kind"] == "request_finished":
                finished.add(event["payload"]["request_id"])
            elif event["kind"] == "optional_resource_result":
                p = event["payload"]
                r = p.get("result")
                producer = store.restore_request(p["request_id"]).producer
                self.costs.add(CostSample(p["request_id"], producer, p["parent_received_at"], p["wall_ns"],
                                         r["cpu_ns"] if r else 0, not r or not r["success"] or p["failure_reason"] is not None))
        for id in accepted.keys() - finished:
            store.abandon(store.restore_request(id), at=max(time.time_ns(), accepted[id]["submitted_at"]),
                          reason="optional worker interrupted before a durable result; restart requires a fresh cut")
        self._thread = Thread(target=self._loop, name="optional-worker-supervisor", daemon=True)
        self._thread.start()

    def submit(self, request: ComputationRequest, function: Callable, *, budget: WorkerBudget,
               coalesce_key: str | None = None) -> bool:
        if (not isinstance(budget, WorkerBudget) or not callable(function)
                or (coalesce_key is not None and (type(coalesce_key) is not str or not coalesce_key))):
            raise ContractError("optional admission needs a typed budget, callable and immutable coalescing identity")
        with self._lock:
            if self._stop.is_set() or self.failure is not None:
                raise ContractError("optional supervisor is stopped or faulted")
            self.store._validate_request(request)
            if self.store.graph.ports[request.producer].lane != "optional":
                raise ContractError("optional worker cannot accept raw market, account, order or timer work")
            at = timestamp(time.time_ns())
            if request.submitted_at > at:
                raise ContractError("optional request has not arrived at admission time")
            if request.id in self._accepted:
                return False
            if self.store.is_terminal(request.id):
                raise ContractError("cannot schedule a terminal request")
            try:
                multiprocessing.reduction.ForkingPickler.dumps((function, request, budget))
            except Exception as exc:
                raise ContractError("optional request and callable must support isolated process submission") from exc
            superseded = [old for old in self._pending if coalesce_key is not None
                          and old[3] == coalesce_key and old[0].producer == request.producer]
            accepted_payload = {"request_id": request.id, "submitted_at": request.submitted_at,
                                "admitted_at": at, "coalesce_key": coalesce_key, "budget": asdict(budget),
                                "policy": asdict(self.queue_policy), "policy_version": self.queue_policy.version,
                                "superseded_request_ids": [old[0].id for old in superseded]}
            canonical_json(accepted_payload)
            if at >= min(request.expires_at, request.horizon_end if request.horizon_end is not None else request.expires_at):
                self.store.abandon(request, at=at, reason="expired before optional queue admission")
                return False
            for old in superseded:
                if request.cut < old[0].cut:
                    self.store.abandon(request, at=at, reason=f"older than queued optional cut {old[0].id}")
                    return False
            if len(self._pending) - len(superseded) >= self.max_pending:
                self.store.abandon(request, at=at, reason="bounded optional queue capacity exceeded")
                return False
            # Record the replacement and its policy before removing any old work.
            # Restart explicitly abandons accepted work interrupted at this boundary.
            self.store.journal.append(key=f"optional:{request.id}", kind="optional_accepted",
                                      payload=accepted_payload)
            for old in superseded:
                self.store.abandon(old[0], at=at, reason=f"superseded queued optional cut by {request.id}")
                self._pending.remove(old)
            self._accepted.add(request.id)
            self._pending.append((request, function, budget, coalesce_key))
            self._wake.set()
            return True

    def _loop(self):
        try:
            while not self._stop.is_set():
                self._wake.clear()
                self.poll()
                self._wake.wait(0.01)
        except BaseException as exc:
            self.failure = exc
            self._stop.set()

    def poll(self):
        with self._lock:
            at = time.time_ns()
            for id, (request, process, conn, budget, start) in list(self._running.items()):
                reason, result = None, None
                if time.monotonic_ns() - start >= budget.wall_ns:
                    reason = "enforced optional worker wall-time budget exceeded"
                elif at >= min(request.expires_at, request.horizon_end if request.horizon_end is not None else request.expires_at):
                    reason = "original forecast horizon/deadline elapsed during computation"
                elif conn.poll():
                    try:
                        result = json.loads(conn.recv_bytes(budget.output_bytes * 2 + 8192))
                    except (EOFError, OSError, ValueError) as exc:
                        reason = f"worker output protocol failed: {type(exc).__name__}"
                elif not process.is_alive():
                    reason = f"worker exited without a result (exitcode={process.exitcode})"
                else:
                    continue
                at = time.time_ns()
                wall_ns = time.monotonic_ns() - start
                if result is not None and wall_ns>=budget.wall_ns:
                    reason="enforced optional worker wall-time budget exceeded while receiving result"
                if result is not None and at>=min(request.expires_at,request.horizon_end if request.horizon_end is not None else request.expires_at):
                    reason="original forecast horizon/deadline elapsed while receiving result"
                sample = CostSample(id, request.producer, at, wall_ns,
                                    result["cpu_ns"] if result else 0,
                                    reason is not None or not result or not result["success"])
                if result is not None and result["success"] and reason is None:
                    # Parent receipt is the actual publication time. Child finish
                    # is retained as telemetry, never used to backdate visibility.
                    self.store.complete(request, payload=bytes.fromhex(result["payload_hex"]), completed_at=at)
                else:
                    self.store.abandon(request, at=at, reason=reason or result["exception"])
                self.store.journal.append(key=f"worker-result:{id}", kind="optional_resource_result",
                                          payload={"request_id": id, "parent_received_at": at,
                                                   "wall_ns": sample.wall_ns, "result": result,
                                                   "failure_reason": reason})
                self.costs.add(sample)
                if process.is_alive():
                    process.terminate()
                process.join(timeout=1)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=1)
                conn.close()
                del self._running[id]
            while self._pending and len(self._running) < self.max_workers:
                selected, choice = self.queue_policy.select([item[0] for item in self._pending],
                                                            at=time.time_ns(), costs=self.costs)
                request, function, budget, key = self._pending.pop(selected)
                self.store.journal.append(key=f"optional-choice:{request.id}", kind="optional_schedule_choice", payload=choice)
                if time.time_ns() >= min(request.expires_at, request.horizon_end if request.horizon_end is not None else request.expires_at):
                    self.store.abandon(request, at=time.time_ns(), reason="original deadline elapsed while queued")
                    continue
                parent, child = self._context.Pipe(duplex=False)
                process = self._context.Process(target=_worker_main, args=(child, function, request, budget), daemon=True)
                start = time.monotonic_ns()
                try:
                    process.start()
                except BaseException:
                    parent.close()
                    child.close()
                    self.store.abandon(request, at=time.time_ns(), reason="optional process could not start")
                    raise
                child.close()
                self._running[request.id] = (request, process, parent, budget, start)

    def close(self):
        self._stop.set()
        self._wake.set()
        self._thread.join(timeout=5)
        if self._thread.is_alive():
            raise ContractError("optional supervisor did not stop")
        with self._lock:
            for request, _, _, _ in self._pending:
                self.store.abandon(request, at=time.time_ns(), reason="optional queued work abandoned at shutdown")
            self._pending.clear()
            for request, process, conn, _, _ in self._running.values():
                process.terminate()
                process.join(timeout=1)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=1)
                conn.close()
                if not self.store.is_terminal(request.id):
                    self.store.abandon(request, at=time.time_ns(), reason="optional in-flight work interrupted at shutdown")
            self._running.clear()
