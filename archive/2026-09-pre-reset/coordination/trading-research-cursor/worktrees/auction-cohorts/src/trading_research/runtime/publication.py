"""Freeze version vectors, then publish complete results at actual completion."""

from dataclasses import asdict, dataclass
from threading import RLock

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.graph import Graph, PublishedVersion
from trading_research.foundations.time import AvailabilityBasis, Clocks, derived_clocks, timestamp
from trading_research.operations.artifacts import digest
from trading_research.operations.journal import Journal


@dataclass(frozen=True)
class ValueVersion:
    metadata: PublishedVersion
    payload: bytes

    def __post_init__(self) -> None:
        if (not isinstance(self.metadata, PublishedVersion) or not isinstance(self.payload, bytes)
                or digest(self.payload) != self.metadata.payload_hash):
            raise ContractError("published payload does not match immutable version content")


@dataclass(frozen=True)
class ComputationRequest:
    id: str
    producer: str
    cut: int
    submitted_at: int
    inputs: tuple[ValueVersion, ...]
    expires_at: int
    horizon_end: int | None
    code_version: str
    parameter_version: str

    def __post_init__(self) -> None:
        for at in (self.cut, self.submitted_at, self.expires_at):
            timestamp(at)
        if (any(type(v) is not str or not v for v in (self.id, self.producer, self.code_version, self.parameter_version))
                or self.submitted_at < self.cut or self.expires_at <= self.submitted_at
                or not isinstance(self.inputs, tuple) or any(not isinstance(v, ValueVersion) for v in self.inputs)):
            raise ContractError("request needs frozen inputs, code/parameters and a future deadline")
        if self.horizon_end is not None:
            timestamp(self.horizon_end)
            if self.horizon_end <= self.cut:
                raise ContractError("forecast keeps its original fixed endpoint")


class VersionStore:
    def __init__(self, graph: Graph, journal: Journal):
        self.graph, self.journal = graph, journal
        self._lock = RLock()
        self._by_id: dict[str, ValueVersion] = {}
        self._requests: dict[str, dict] = {}
        self._terminal: dict[str, dict] = {}
        for e in journal.read():
            if e["kind"] in {"published", "request_finished"}:
                terminal = e["payload"] if e["kind"] == "request_finished" else None
                if terminal is not None:
                    if terminal["request_id"] not in self._requests:
                        raise ContractError("terminal computation has no preceding frozen request")
                    self._terminal[terminal["request_id"]] = terminal
                p = terminal["publication"] if terminal is not None else e["payload"]
                if p is None:
                    continue
                if p["graph_version"] != graph.version:
                    raise ContractError("runtime graph changed; checkpoint requires explicit replay/migration")
                c = p["metadata"]["clocks"]
                clocks = Clocks(**{**c, "basis": AvailabilityBasis(c["basis"])})
                metadata = PublishedVersion(**{**p["metadata"], "clocks": clocks,
                                              "input_versions": tuple(p["metadata"]["input_versions"])})
                self._accept(ValueVersion(metadata, bytes.fromhex(p["payload_hex"])))
            elif e["kind"] == "requested":
                if e["payload"]["graph_version"] != graph.version:
                    raise ContractError("pending request belongs to a different runtime graph")
                self._requests[e["payload"]["id"]] = e["payload"]

    def _accept(self, value: ValueVersion) -> None:
        if value.metadata.port_id not in self.graph.ports:
            raise ContractError("unknown producer publication")
        old = self._by_id.get(value.metadata.id)
        if old is not None and old != value:
            raise ContractError("immutable publication ID reused")
        self._by_id[value.metadata.id] = value

    def publish_root(self, port: str, *, cut: int, clocks: Clocks, payload: bytes,
                     source_evidence_ids: tuple[str, ...]) -> ValueVersion:
        producer = self.graph.ports.get(port)
        if producer is None or producer.inputs or not source_evidence_ids:
            raise ContractError("only declared roots may publish source/frozen state directly")
        if not clocks.available(cut):
            raise ContractError("root observation was unavailable at its captured cut")
        metadata = PublishedVersion(port, digest([port, cut, clocks, payload, source_evidence_ids]), cut, clocks,
                                    source_evidence_ids, digest(payload))
        return self._commit(ValueVersion(metadata, payload))

    def _commit(self, value: ValueVersion) -> ValueVersion:
        with self._lock:
            prior = self._by_id.get(value.metadata.id)
            if prior is not None:
                if prior != value:
                    raise ContractError("publication ID conflict")
                return prior
            self.journal.append(key=f"publish:{value.metadata.id}", kind="published",
                                payload={"metadata": asdict(value.metadata), "payload_hex": value.payload.hex(),
                                         "graph_version": self.graph.version})
            self._accept(value)
        return value

    def freeze(self, producer: str, *, cut: int, submitted_at: int, input_ids: tuple[str, ...],
               expires_at: int, horizon_end: int | None, code_version: str, parameter_version: str) -> ComputationRequest:
        with self._lock:
            if (any(type(v) is not str or not v for v in (producer, code_version, parameter_version))
                    or producer not in self.graph.ports or not isinstance(input_ids, tuple)
                    or any(type(v) is not str or not v for v in input_ids)):
                raise ContractError("request needs declared producer and immutable string identities")
            if len(set(input_ids)) != len(input_ids):
                raise ContractError("duplicate evidence in request input vector")
            try:
                values = tuple(self._by_id[id] for id in input_ids)
            except KeyError as exc:
                raise DependencyUnavailable("requested publication is missing") from exc
            by_port = {v.metadata.port_id: v.metadata for v in values}
            if len(by_port) != len(values):
                raise ContractError("two versions of one producer cannot silently coexist in a captured cut")
            self.graph.validate_inputs(producer, by_port, cut=cut, available_at=submitted_at)
            id = digest([self.graph.version, producer, cut, submitted_at, input_ids, expires_at, horizon_end, code_version, parameter_version])
            request = ComputationRequest(id, producer, cut, submitted_at, values, expires_at, horizon_end, code_version, parameter_version)
            manifest = {"id": id, "producer": producer, "cut": cut,
                                "submitted_at": submitted_at, "input_ids": list(input_ids), "expires_at": expires_at,
                                "horizon_end": horizon_end, "code_version": code_version, "parameter_version": parameter_version,
                                "graph_version": self.graph.version}
            self.journal.append(key=f"request:{id}", kind="requested", payload=manifest)
            self._requests[id] = manifest
            return request

    def complete(self, request: ComputationRequest, *, payload: bytes, completed_at: int) -> ValueVersion | None:
        timestamp(completed_at)
        with self._lock:
            self._validate_request(request)
            if completed_at < request.submitted_at:
                raise ContractError("completion precedes actual task submission")
            if completed_at >= min(request.expires_at, request.horizon_end if request.horizon_end is not None else request.expires_at):
                return self._finish(request, completed_at, "expired", None,
                                    "result completed at or after its original deadline")
            clocks = derived_clocks([v.metadata.clocks for v in request.inputs], source_version=request.id,
                                     actual_completion_at=completed_at)
            metadata = PublishedVersion(request.producer, digest([request.id, clocks, payload]), request.cut, clocks,
                                        tuple(v.metadata.id for v in request.inputs), digest(payload), request.horizon_end)
            return self._finish(request, completed_at, "completed", ValueVersion(metadata, payload), "")

    def _validate_request(self, request: ComputationRequest) -> None:
        if not isinstance(request, ComputationRequest):
            raise ContractError("typed frozen computation request required")
        expected = {"id": request.id, "producer": request.producer, "cut": request.cut,
                    "submitted_at": request.submitted_at, "input_ids": [v.metadata.id for v in request.inputs],
                    "expires_at": request.expires_at, "horizon_end": request.horizon_end,
                    "code_version": request.code_version, "parameter_version": request.parameter_version,
                    "graph_version": self.graph.version}
        if self._requests.get(request.id) != expected or any(self._by_id.get(v.metadata.id) != v for v in request.inputs):
            raise ContractError("completion does not match an actually registered frozen request")

    def _finish(self, request: ComputationRequest, at: int, status: str,
                value: ValueVersion | None, reason: str) -> ValueVersion | None:
        publication = None if value is None else {"metadata": asdict(value.metadata), "payload_hex": value.payload.hex(),
                                                  "graph_version": self.graph.version}
        terminal = {"request_id": request.id, "completed_at": at, "status": status, "reason": reason,
                    "original_horizon_end": request.horizon_end, "publication": publication}
        # Publication and the unique terminal state are one durable transaction. A
        # racing process can neither publish twice nor resurrect an expired task.
        self.journal.append(key=f"finish:{request.id}", kind="request_finished", payload=terminal)
        self._terminal[request.id] = terminal
        if value is not None:
            self._accept(value)
        return value

    def abandon(self, request: ComputationRequest, *, at: int, reason: str) -> None:
        timestamp(at)
        if not reason or at < request.submitted_at:
            raise ContractError("abandoning work needs its actual time and explicit reason")
        with self._lock:
            self._validate_request(request)
            self._finish(request, at, "abandoned", None, reason)

    def is_terminal(self, request_id: str) -> bool:
        with self._lock:
            return request_id in self._terminal

    def restore_request(self, request_id: str) -> ComputationRequest:
        with self._lock:
            p = self._requests[request_id]
            return ComputationRequest(p["id"], p["producer"], p["cut"], p["submitted_at"],
                                      tuple(self._by_id[id] for id in p["input_ids"]), p["expires_at"],
                                      p["horizon_end"], p["code_version"], p["parameter_version"])

    def latest(self, port: str, *, available_at: int, observation_cut: int, max_age_ns: int) -> ValueVersion | None:
        with self._lock:
            values = [v for v in self._by_id.values() if v.metadata.port_id == port
                      and v.metadata.clocks.available(available_at) and v.metadata.decision_cut <= observation_cut
                      and 0 <= available_at - v.metadata.decision_cut <= max_age_ns
                      and (v.metadata.horizon_end is None or available_at < v.metadata.horizon_end)]
            return max(values, key=lambda v: (v.metadata.decision_cut, v.metadata.clocks.known_at, v.metadata.id), default=None)
