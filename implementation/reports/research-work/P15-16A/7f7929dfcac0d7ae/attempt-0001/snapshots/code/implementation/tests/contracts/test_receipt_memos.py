"""Memoization inside one _VerifyState: successor verify, file digests, predecessor cache key."""
from __future__ import annotations

from pathlib import Path

from trading_research.research.contracts import receipts as rec
from trading_research.research.contracts.identity import file_digest as identity_file_digest
from trading_research.research.contracts.receipts import (
    _VerifyState,
    file_digest,
    verify_task_receipt,
)


def test_file_digest_memo_per_resolved_path(monkeypatch, tmp_path: Path):
    blob = tmp_path / "large.bin"
    blob.write_bytes(b"abc" * 10000)
    calls = []
    real = rec._identity_file_digest

    def counting(path):
        calls.append(str(path))
        return real(path)

    monkeypatch.setattr(rec, "_identity_file_digest", counting)
    state = _VerifyState(
        receipts_root=tmp_path,
        graph=None,
        amendments_path=tmp_path / "missing.json",
    )
    token = rec._DIGEST_STATE.set(state)
    try:
        first = file_digest(blob)
        second = file_digest(blob)
        third = file_digest(blob.resolve())
    finally:
        rec._DIGEST_STATE.reset(token)
    assert first == second == third == identity_file_digest(blob)
    assert len(calls) == 1


def test_successor_verify_memo_per_resolved_path(monkeypatch, tmp_path: Path):
    path = tmp_path / "TASK_RECEIPT.json"
    path.write_text("{}\n")
    state = _VerifyState(
        receipts_root=tmp_path,
        graph=None,
        amendments_path=tmp_path / "missing.json",
    )
    calls = {"n": 0}
    real = rec.load_json_document

    def counting(document_path):
        calls["n"] += 1
        return real(document_path)

    monkeypatch.setattr(rec, "load_json_document", counting)
    first = verify_task_receipt(path, _state=state)
    n_first = calls["n"]
    second = verify_task_receipt(path, _state=state)
    assert first.ok is False
    assert second.ok is False
    assert first.failures == second.failures
    assert calls["n"] == n_first
    assert n_first >= 1


def test_predecessor_cache_key_includes_receipt_path(monkeypatch, tmp_path: Path):
    predecessor = tmp_path / "pred.json"
    predecessor.write_text('{"task_id": "P15-W"}\n')
    digest = identity_file_digest(predecessor)
    graph = rec.TaskGraph(
        path=str(tmp_path / "graph.json"),
        tasks={},
        cycles=(),
        required_task_artifacts=(),
        assurance_version="test",
        coordinator_artifacts={},
    )
    state = _VerifyState(
        receipts_root=tmp_path,
        graph=graph,
        amendments_path=tmp_path / "missing.json",
    )
    calls = {"n": 0}
    real = rec.verify_task_receipt

    def counting(path, **kwargs):
        calls["n"] += 1
        return real(path, **kwargs)

    monkeypatch.setattr(rec, "verify_task_receipt", counting)
    rec._VERIFY_CACHE.clear()
    spec = rec.TaskSpec(
        id="P15-X",
        phase="1.5",
        subphase="05",
        dependencies=("P15-W",),
        required_acceptance_keys=(),
        allowed_terminal_statuses=frozenset({"implemented_verified"}),
        native=False,
        artifacts=(),
        assurance_cases=(),
    )
    receipt = {
        "predecessor_receipts": {"P15-W": {"path": str(predecessor), "sha256": digest}},
        "artifact_manifest": [],
    }
    failures = []
    rec._check_predecessors(receipt, spec, tmp_path / "child.json", tmp_path, failures, graph=graph, state=state)
    first = calls["n"]
    rec._check_predecessors(receipt, spec, tmp_path / "child.json", tmp_path, failures, graph=graph, state=state)
    assert first >= 1
    assert calls["n"] == first
    keys = [key for key in rec._VERIFY_CACHE if key[0] == str(predecessor)]
    assert keys
    assert keys[0][1] == digest
