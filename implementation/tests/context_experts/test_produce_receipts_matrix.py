"""Evidence matrix rows must resolve under the receipt verifier."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import ast
import json
import shutil
import sys

import pytest

from trading_research.research.contracts.receipts import (
    _module_symbols,
    _resolve_workspace_file,
    _selector_resolves,
    _test_node_names,
)

WORKTREE = Path(__file__).resolve().parents[3]
PRODUCER_PATH = WORKTREE / "implementation/reports/research-work/phase2-early/produce_receipts.py"
SLICE = WORKTREE / "implementation/reports/research-work/phase2-early"
_spec = spec_from_file_location("phase2_early_produce_receipts", PRODUCER_PATH)
assert _spec is not None and _spec.loader is not None
producer = module_from_spec(_spec)
sys.modules[_spec.name] = producer
_spec.loader.exec_module(producer)


def _def_class_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        names.add(f"{node.name}.{child.name}")
    return names


MATRIX_ARTIFACTS = (
    "INSTRUMENT_LEDGER.json",
    "SURFACE_INPUT_SLICE.json",
    "OPTIONS_AVAILABILITY.json",
    "PUBLICATION_SENSITIVITY.json",
    "PRICING_FIXTURES.json",
    "EXPOSURE_BOARDS.json",
    "VOLATILITY_FIXTURES.json",
    "VOLATILITY_TARGETS.json",
)

PROBE_STUB = {
    "ok": True,
    "control": {"ok": True, "codes": []},
    "mutations": {
        "remove_artifact": {"ok": False, "codes": ["ARTIFACT_MISSING"]},
        "substitute_file": {"ok": False, "codes": ["SCHEMA"]},
        "row_count": {"ok": False, "codes": ["INVENTORY"]},
        "invalid_json": {"ok": False, "codes": ["JSON_PARSE"]},
        "plan_digest": {"ok": False, "codes": ["IDENTITY"]},
        "code_digest": {"ok": False, "codes": ["IDENTITY"]},
        "draft_digest": {"ok": False, "codes": ["IDENTITY"]},
        "omit_owned_file": {"ok": False, "codes": ["INVENTORY"]},
    },
}


def _stage_attempt(tmp_path: Path, task_id: str) -> Path:
    spec = producer.TASKS[task_id]
    attempt = tmp_path / task_id
    attempt.mkdir()
    (attempt / "pytest.log").write_text("17 passed in 0.40s\n")
    (attempt / "VERIFY_TASK.json").write_text(json.dumps({"ok": True, "kind": "task", "path": "TASK_RECEIPT.json"}) + "\n")
    (attempt / "PROBES_S01_S03.json").write_text(json.dumps(PROBE_STUB) + "\n")
    slice_dir = SLICE / spec["slice_dir"]
    for name in MATRIX_ARTIFACTS:
        src = slice_dir / name
        if src.is_file():
            shutil.copy2(src, attempt / name)
    return attempt


def _assert_code_ref(ref: dict) -> None:
    raw = str(ref["path"])
    assert "/tests/" not in raw.replace("\\", "/")
    code_path = _resolve_workspace_file(raw, WORKTREE)
    assert code_path is not None and code_path.is_file()
    symbols = _module_symbols(code_path)
    assert symbols is not None
    assert ref["symbol"] in symbols
    assert ref["symbol"] in _def_class_names(code_path)


@pytest.mark.parametrize("task_id", ["P2-09", "P2-10", "P2-03"])
def test_matrix_rows_resolve_for_verifier(task_id, tmp_path):
    spec = producer.TASKS[task_id]
    attempt = _stage_attempt(tmp_path, task_id)
    matrix = producer._matrix(task_id, spec, attempt, 0, audit_index=1)
    checks = matrix["checks"]
    assert {check["id"] for check in checks} == set(spec["cases"])
    assert len(checks) == len(spec["cases"])
    by_id = {check["id"]: check for check in checks}
    for key in ("A06", "A07", "A08"):
        row = by_id[key]
        assert row["test_nodeids"] == []
        assert row["command_indices"] == [1]
        assert row["status"] == "pass"
        selectors = [item["selector"] for item in row["evidence"]]
        assert "/ok" in selectors
        if key == "A08":
            assert any("passed" in item for item in selectors)
    for key in ("S01", "S03"):
        row = by_id[key]
        assert row["test_nodeids"] == []
        assert row["command_indices"] == [1]
        assert row["status"] == "pass"
        selectors = [item["selector"] for item in row["evidence"]]
        assert "/control/ok" in selectors
        assert any(item.startswith("/mutations/") for item in selectors)
    if "S07" in by_id and task_id == "P2-03":
        node = by_id["S07"]["test_nodeids"][0]
        assert node.endswith("::test_s07_native_minute_close_is_tagged_not_bbo")
        assert by_id["S07"]["code_refs"][0]["symbol"] != "future_prices_do_not_enter"
    for check in checks:
        if check.get("status") not in {"pass", "accepted-limit"}:
            continue
        assert check.get("command_indices")
        assert check.get("evidence")
        refs = check.get("code_refs")
        assert refs
        for ref in refs:
            _assert_code_ref(ref)
        nodes = check.get("test_nodeids")
        assert isinstance(nodes, list)
        prefix = f"test_{str(check['id']).lower()}"
        for nodeid in nodes:
            assert "::" in nodeid
            file_part, _, test_part = nodeid.partition("::")
            wanted = test_part.split("::")[-1]
            assert wanted == prefix or wanted.startswith(prefix + "_")
            test_path = _resolve_workspace_file(file_part, WORKTREE)
            assert test_path is not None
            names = _test_node_names(test_path)
            assert names is not None
            assert wanted in names
        for item in check["evidence"]:
            evidence_path = Path(item["path"])
            assert _selector_resolves(evidence_path, item["selector"])


def test_unmatched_check_id_raises(tmp_path):
    spec = dict(producer.TASKS["P2-09"])
    spec["cases"] = list(spec["cases"]) + ["S99"]
    attempt = _stage_attempt(tmp_path, "P2-09")
    with pytest.raises(RuntimeError, match="S99"):
        producer._matrix("P2-09", spec, attempt, 0, audit_index=1)
