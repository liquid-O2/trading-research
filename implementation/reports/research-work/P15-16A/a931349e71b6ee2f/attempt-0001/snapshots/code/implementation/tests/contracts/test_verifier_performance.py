"""Bound repeated verifier work without weakening byte or successor checks."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from trading_research.research.contracts import receipts as rec
from trading_research.research.contracts.identity import file_digest
from tests.rule_discovery.test_p15_01 import (
    _bound_graph, _stale_code, _write_pair, write_bound_task,
)


@pytest.fixture
def read_state(tmp_path):
    state = rec._VerifyState(receipts_root=tmp_path, graph=None,
                             amendments_path=tmp_path / "absent.json")
    token = rec._DIGEST_STATE.set(state)
    try:
        yield state
    finally:
        rec._DIGEST_STATE.reset(token)


def test_cached_reads_detect_same_size_edit_with_restored_mtime(tmp_path, read_state):
    path = tmp_path / "input.json"
    path.write_text('{"value":1}')
    old_stat = path.stat()
    old_digest = rec.file_digest(path)
    assert rec.load_json_document(path)[0] == {"value": 1}
    path.write_text('{"value":2}')
    os.utime(path, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns))
    assert rec.file_digest(path) != old_digest
    assert rec.load_json_document(path)[0] == {"value": 2}
    path.unlink()
    assert rec.load_json_document(path)[0] is None
    with pytest.raises(FileNotFoundError):
        rec.file_digest(path)


def test_cached_reads_detect_symlink_retarget_and_invalid_json(tmp_path, read_state):
    first, second = tmp_path / "first.json", tmp_path / "second.json"
    first.write_text('{"v":1}')
    second.write_text('{"v":2}')
    link = tmp_path / "link.json"
    link.symlink_to(first)
    assert rec.load_json_document(link)[0] == {"v": 1}
    assert rec.file_digest(link) == file_digest(first)
    link.unlink()
    link.symlink_to(second)
    assert rec.load_json_document(link)[0] == {"v": 2}
    assert rec.file_digest(link) == file_digest(second)
    second.write_text('{"v":NaN}')
    document, failures = rec.load_json_document(link)
    assert document is None
    assert failures[0].code == rec.FailureCode.JSON_PARSE


def test_parse_cache_is_reused_and_scoped_to_one_verification(tmp_path, read_state, monkeypatch):
    path = tmp_path / "input.json"
    path.write_text('{"value":1}')
    calls = []
    original = rec.json.loads

    def read(text, *args, **kwargs):
        calls.append(text)
        return original(text, *args, **kwargs)

    monkeypatch.setattr(rec.json, "loads", read)
    for _ in range(10):
        assert rec.load_json_document(path)[0] == {"value": 1}
    assert len(calls) == 1
    token = rec._DIGEST_STATE.set(None)
    try:
        rec.load_json_document(path)
    finally:
        rec._DIGEST_STATE.reset(token)
    assert len(calls) == 2


def test_symbol_cache_does_not_keep_removed_symbol(tmp_path, read_state):
    path = tmp_path / "module.py"
    path.write_text('def present(): pass\n')
    assert 'present' in rec._module_symbols(path)
    path.write_text('def missing(): pass\n')
    assert 'present' not in rec._module_symbols(path)


def test_new_public_call_rechecks_predecessor_artifact_bytes(tmp_path):
    graph, parent, child = _write_pair(tmp_path)
    good = rec.verify_task_receipt(child, graph_path=graph, receipts_root=tmp_path)
    assert good.ok, good.failures
    # Receipt hash is unchanged; only a referenced artifact was corrupted.
    report = parent.parent / "REPORT.md"
    report.write_text("tampered\n")
    bad = rec.verify_task_receipt(child, graph_path=graph, receipts_root=tmp_path)
    assert not bad.ok
    assert any(f.code == rec.FailureCode.ARTIFACT_HASH and f.path == str(report) for f in bad.failures)


def test_wrong_code_candidates_do_not_expand_dependency_search(tmp_path, monkeypatch):
    graph = _bound_graph(tmp_path)
    parent = write_bound_task(tmp_path, "P15-00")
    rel, old, live = _stale_code(parent)
    child = write_bound_task(tmp_path, "P15-01", predecessors={"P15-00": file_digest(parent)})
    distractors = set()
    for index in range(40):
        folder = tmp_path / f"distractor-{index:03d}"
        folder.mkdir()
        snapshot = folder / "CODE_SNAPSHOT.json"
        snapshot.write_text(json.dumps({"files": {rel: old}}))
        path = folder / "TASK_RECEIPT.json"
        path.write_text(json.dumps({
            "task_id": "P15-01", "predecessor_receipts": {"P15-00": file_digest(parent)},
            "artifact_manifest": [{"name": "CODE_SNAPSHOT.json", "path": str(snapshot)}],
        }))
        distractors.add(path)
    original = rec._receipt_lists_predecessor

    def check(document, document_path, *args, **kwargs):
        assert document_path not in distractors, "irrelevant code traversed the predecessor DAG"
        return original(document, document_path, *args, **kwargs)

    monkeypatch.setattr(rec, "_receipt_lists_predecessor", check)
    result = rec.verify_task_receipt(parent, graph_path=graph, receipts_root=tmp_path)
    assert result.ok, result.failures
    # The matching successor remains fully checked, not just its advertised hash.
    (child.parent / "REPORT.md").write_text("tampered\n")
    result = rec.verify_task_receipt(parent, graph_path=graph, receipts_root=tmp_path)
    assert not result.ok
    assert any(f.code == rec.FailureCode.IDENTITY for f in result.failures)


def test_all_task_lookups_resolve_index_paths_only_once(tmp_path, monkeypatch):
    for name in ("A", "B", "C"):
        folder = tmp_path / name
        folder.mkdir()
        (folder / "TASK_RECEIPT.json").write_text("{}")
    state = rec._VerifyState(receipts_root=tmp_path, graph=None, amendments_path=tmp_path / "absent")
    original = Path.resolve
    calls = []

    def resolve(self, *args, **kwargs):
        calls.append(self)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    for _ in range(4):
        for name in ("A", "B", "C"):
            assert state.receipts_for(name) == (tmp_path / name / "TASK_RECEIPT.json",)
    assert len(calls) == 4  # root plus three indexed receipts, across every lookup
