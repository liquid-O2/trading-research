from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import sqlite3
import tempfile
from threading import Event
import time
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.graph import Graph, InputPort, Port
from trading_research.operations.journal import Journal
from trading_research.runtime.publication import VersionStore
from trading_research.runtime.reactor import CriticalEvent, CriticalReactor, OptionalWorkers, WorkerBudget
from tests.test_foundations import clocks


def graph():
    return Graph([Port("tape", "F01", 0, "tape.v1", frozenset({"price"}), lane="market"),
                  Port("context", "C01", 1, "forecast.v1", frozenset({"p"}),
                       (InputPort("tape", "tape.v1", frozenset({"price"})),)),
                  Port("decision", "P01", 2, "decision.v1", frozenset({"action"}),
                       (InputPort("context", "forecast.v1", frozenset({"p"})),))])


def request(store, at=10, *, end=100, marker=b"100"):
    root = store.publish_root("tape", cut=at, clocks=clocks(at), payload=marker, source_evidence_ids=(f"row:{at}",))
    return store.freeze("context", cut=at, submitted_at=at, input_ids=(root.metadata.id,),
                        expires_at=end, horizon_end=end, code_version="test-implementation", parameter_version="frozen")


def blocked_optional(req):
    # Deliberately held open, with an observable handshake before the timer test.
    marker = Path(req.inputs[0].payload.decode())
    marker.write_text("started")
    while not marker.with_suffix(".release").exists():
        time.sleep(0.01)
    return b"complete"


def successful_optional(req):
    return b"result: " + req.inputs[0].payload


def huge_optional(req):
    return b"x" * 100


class JournalTests(unittest.TestCase):
    def test_concurrent_keys_duplicate_conflict_restart_and_optimistic_guard(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "events.sqlite"
            journal = Journal(path)
            with ThreadPoolExecutor(max_workers=4) as pool:
                results = list(pool.map(lambda _: journal.append(key="same", kind="x", payload={"value": 1}), range(8)))
            self.assertEqual(sum(created for _, created in results), 1)
            self.assertEqual(len(Journal(path).read()), 1)
            with self.assertRaises(IntegrityError):
                journal.append(key="same", kind="x", payload={"value": 2})
            with self.assertRaises(ContractError):
                journal.append(key="stale", kind="x", payload={}, expected_head=None, check_head=True)
            self.assertEqual(len(journal.read()), 1)

    def test_journal_rejects_sql_mutation_and_detects_tampering(self):
        with tempfile.TemporaryDirectory() as d:
            journal = Journal(Path(d) / "events.sqlite")
            journal.append(key="a", kind="x", payload={})
            with sqlite3.connect(journal.path) as con:
                with self.assertRaises(sqlite3.IntegrityError):
                    con.execute("DELETE FROM events")
                con.execute("DROP TRIGGER no_event_updates")
                con.execute("UPDATE events SET hash='corrupt'")
            with self.assertRaises(IntegrityError):
                journal.read()


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.journal = Journal(Path(self.temp.name) / "versions.sqlite")
        self.store = VersionStore(graph(), self.journal)

    def test_frozen_cut_completion_latency_original_endpoint_and_restart(self):
        req = request(self.store, end=40)
        request(self.store, 20, end=50, marker=b"future changed price")
        result = self.store.complete(req, payload=b"forecast", completed_at=25)
        self.assertEqual((result.metadata.decision_cut, result.metadata.clocks.known_at, result.metadata.horizon_end), (10, 25, 40))
        self.assertEqual(result.metadata.input_versions, (req.inputs[0].metadata.id,))
        downstream = self.store.freeze("decision", cut=10, submitted_at=26, input_ids=(result.metadata.id,),
                                       expires_at=40, horizon_end=40, code_version="v1", parameter_version="p1")
        self.assertEqual(downstream.inputs[0], result)
        restored = VersionStore(graph(), self.journal)
        self.assertEqual(restored.restore_request(req.id), req)
        self.assertEqual(restored.latest("context", available_at=30, observation_cut=30, max_age_ns=30), result)
        self.assertIsNone(restored.latest("context", available_at=40, observation_cut=40, max_age_ns=40))

    def test_forecast_cannot_be_published_twice_or_resurrected_after_expiry(self):
        req = request(self.store, end=30)
        first = self.store.complete(req, payload=b"same", completed_at=20)
        self.assertEqual(self.store.complete(req, payload=b"same", completed_at=20), first)
        for payload, at in ((b"changed", 20), (b"same", 21), (b"same", 30)):
            with self.assertRaises(IntegrityError):
                self.store.complete(req, payload=payload, completed_at=at)
        req2 = request(self.store, 11, end=30)
        self.assertIsNone(self.store.complete(req2, payload=b"late", completed_at=30))
        with self.assertRaises(IntegrityError):
            VersionStore(graph(), self.journal).complete(req2, payload=b"backdated", completed_at=20)
        self.assertEqual(sum(e["kind"] == "request_finished" for e in self.journal.read()), 2)

    def test_forged_requests_future_roots_and_changed_graph_are_rejected(self):
        req = request(self.store)
        with self.assertRaises(ContractError):
            self.store.complete(replace(req, parameter_version="mutated"), payload=b"bad", completed_at=15)
        with self.assertRaises(ContractError):
            self.store.publish_root("tape", cut=10, clocks=clocks(11), payload=b"future", source_evidence_ids=("row-future",))
        with self.assertRaises(ContractError):
            self.store.freeze("context", cut=9, submitted_at=12, input_ids=(req.inputs[0].metadata.id,),
                              expires_at=20, horizon_end=20, code_version="c", parameter_version="p")
        altered = Graph([replace(p, owner="changed") for p in graph().ports.values()])
        with self.assertRaises(ContractError):
            VersionStore(altered, self.journal)

    def test_same_valued_snapshot_does_not_gain_observation_freshness(self):
        req = request(self.store, at=10, end=80)
        old = self.store.complete(req, payload=b"same", completed_at=60)
        self.assertIsNone(self.store.latest("context", available_at=61, observation_cut=61, max_age_ns=20))
        req2 = request(self.store, at=55, end=80)
        fresh = self.store.complete(req2, payload=b"same", completed_at=62)
        self.assertNotEqual(fresh.metadata.id, old.metadata.id)
        self.assertEqual(self.store.latest("context", available_at=63, observation_cut=63, max_age_ns=20), fresh)


class ReactorTests(unittest.TestCase):
    def test_boundary_without_next_tick_and_crash_replays_only_unacknowledged_event(self):
        with tempfile.TemporaryDirectory() as d:
            journal = Journal(Path(d) / "critical.sqlite")
            applied, failed = set(), []

            def handler(event):
                applied.add(event.id)  # Idempotent account transition stand-in.
                if event.id == "boundary" and not failed:
                    failed.append(True)
                    raise RuntimeError("crash after durable handler, before acknowledgement")

            reactor = CriticalReactor(journal, handler, clock=lambda: 0)
            reactor.submit(CriticalEvent("fill", "account", 5, 5, b"one mini"))
            reactor.submit(CriticalEvent("boundary", "timer", 1, 10, b"flatten"))
            self.assertEqual(reactor.run_due(9), 1)
            with self.assertRaises(RuntimeError):
                reactor.run_due(10)
            restored = CriticalReactor(journal, handler)
            self.assertEqual(restored.run_due(10), 1)
            self.assertEqual(applied, {"fill", "boundary"})
            self.assertEqual(CriticalReactor(journal, handler).run_due(100), 0)
            restored.submit(CriticalEvent("boundary", "timer", 1, 10, b"flatten"))
            self.assertEqual(restored.run_due(100), 0)

    def test_received_events_are_not_processed_before_receipt(self):
        with tempfile.TemporaryDirectory() as d:
            received = []
            r = CriticalReactor(Journal(Path(d) / "c.sqlite"), received.append)
            r.submit(CriticalEvent("late-fill", "account", 20, 10, b"fill"))
            self.assertEqual(r.run_due(15), 0)
            self.assertEqual(r.run_due(20), 1)

    def test_blocked_optional_inference_does_not_block_boundary_and_deadline_is_enforced(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            store = VersionStore(graph(), Journal(root / "v.sqlite"))
            workers = OptionalWorkers(store)
            self.addCleanup(workers.close)
            marker = root / "worker.started"
            now = time.time_ns()
            req = request(store, now, end=now + 10_000_000_000, marker=str(marker).encode())
            workers.submit(req, blocked_optional, budget=WorkerBudget(1_000_000_000, 3, 256 * 1024 ** 2))
            deadline = time.monotonic() + 3
            while not marker.exists() and time.monotonic() < deadline:
                time.sleep(0.005)
            self.assertTrue(marker.exists(), f"worker handshake missing: {workers.failure}")
            boundary = Event()
            critical = CriticalReactor(Journal(root / "critical.sqlite"), lambda event: boundary.set())
            self.addCleanup(critical.close)
            critical.start()
            now = time.time_ns()
            critical.submit(CriticalEvent("flatten", "timer", now, now + 20_000_000, b"flatten"))
            self.assertTrue(boundary.wait(0.5), "boundary waited for optional computation")
            self.assertFalse(marker.with_suffix(".release").exists())
            deadline = time.monotonic() + 3
            while not store.is_terminal(req.id) and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(store.is_terminal(req.id))
            end = next(e["payload"] for e in store.journal.read() if e["kind"] == "request_finished")
            self.assertIn("wall-time budget", end["reason"])
            self.assertIsNone(workers.failure)
            self.assertIsNone(critical.failure)

    def test_optional_coalescing_retains_dropped_ids_and_output_bounds(self):
        with tempfile.TemporaryDirectory() as d:
            store = VersionStore(graph(), Journal(Path(d) / "v.sqlite"))
            workers = OptionalWorkers(store, max_pending=2)
            self.addCleanup(workers.close)
            now = time.time_ns()
            budget = WorkerBudget(2_000_000_000, 3, 256 * 1024 ** 2, output_bytes=10)
            old = request(store, now, end=now + 5_000_000_000)
            new = request(store, now + 1, end=now + 5_000_000_000)
            # Prevent queue consumption until both requests are submitted.
            with workers._lock:
                workers.submit(old, successful_optional, budget=budget, coalesce_key="same-cut-family")
                workers.submit(new, huge_optional, budget=budget, coalesce_key="same-cut-family")
            deadline = time.monotonic() + 3
            while not store.is_terminal(new.id) and time.monotonic() < deadline:
                time.sleep(0.01)
            results = {e["payload"]["request_id"]: e["payload"] for e in store.journal.read() if e["kind"] == "request_finished"}
            self.assertIn("superseded queued", results[old.id]["reason"])
            self.assertIn("output bound", results[new.id]["reason"])
            self.assertIsNone(workers.failure)

    def test_successful_worker_publishes_at_parent_receipt_and_restart_marks_interruption(self):
        with tempfile.TemporaryDirectory() as d:
            store = VersionStore(graph(), Journal(Path(d) / "v.sqlite"))
            now = time.time_ns()
            pending = request(store, now, end=now + 10_000_000_000)
            store.journal.append(key="accepted-interrupted", kind="optional_accepted",
                                 payload={"request_id": pending.id, "submitted_at": now})
            workers = OptionalWorkers(store)
            self.addCleanup(workers.close)
            self.assertTrue(store.is_terminal(pending.id))
            req = request(store, now + 1, end=now + 10_000_000_000)
            workers.submit(req, successful_optional, budget=WorkerBudget(3_000_000_000, 3, 256 * 1024 ** 2))
            deadline = time.monotonic() + 4
            rows = []
            while time.monotonic() < deadline:
                rows = [e["payload"] for e in store.journal.read()
                        if e["kind"] == "optional_resource_result" and e["payload"]["request_id"] == req.id]
                if store.is_terminal(req.id) and rows:
                    break
                time.sleep(0.01)
            self.assertEqual(len(rows),1,"worker resource telemetry did not finish its separate durable write")
            self.assertIsNone(workers.failure)
            value = store.latest("context", available_at=time.time_ns(), observation_cut=time.time_ns(), max_age_ns=10_000_000_000)
            self.assertIsNotNone(value)
            self.assertEqual(value.payload, b"result: 100")
            self.assertEqual(value.metadata.clocks.known_at, rows[0]["parent_received_at"])
            self.assertGreaterEqual(rows[0]["parent_received_at"], rows[0]["result"]["completed_at"])


if __name__ == "__main__":
    unittest.main()
