"""Evidence-matrix rows must resolve under the receipt verifier's own resolvers.

The producer builds the matrix from TASK_GRAPH.json; this guards the binding
rules the verifier enforces (code_refs, test nodeids, evidence selectors) plus
the two ways the producer is allowed to fail loudly: an unknown case id and a
case with no uniquely named test.
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
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
RUN_ROOT = WORKTREE / "implementation/reports/research-work/phase2-early/run-2026-09-16"
_spec = spec_from_file_location("phase2_early_produce_receipts", PRODUCER_PATH)
assert _spec is not None and _spec.loader is not None
producer = module_from_spec(_spec)
sys.modules[_spec.name] = producer
_spec.loader.exec_module(producer)

INDICES = {"pytest": 0, "slice": 1, "predecessors": [2]}
PROBE_STUB = {
    "schema_version": producer.PROBES_SCHEMA,
    "control": {"ok": True, "codes": []},
    "mutations": {
        name: {"ok": False, "codes": [code], "expected_code": code, "expected_code_present": True, "rejected": True}
        for name, _fn, code, _desc in producer.MUTATIONS
    },
    "n_rejected": len(producer.MUTATIONS),
    "n_mutations": len(producer.MUTATIONS),
    "ok": True,
}


def _stage(tmp_path: Path, task_id: str, spec: dict) -> Path:
    attempt = tmp_path / task_id
    attempt.mkdir()
    (attempt / "pytest.log").write_text("17 passed in 0.40s\n")
    (attempt / "slice.log").write_text(json.dumps({"ok": True, "task": task_id}) + "\n")
    (attempt / "predecessor_verify.log").write_text(json.dumps({"kind": "task", "ok": True, "path": "x"}) + "\n")
    (attempt / "REPORT.md").write_text("# report\n\n## Inspected output\n\n- one native row\n")
    (attempt / producer.PROBES_NAME).write_text(json.dumps(PROBE_STUB) + "\n")
    source = RUN_ROOT / spec["slice_dir"]
    for name in list(spec["artifacts"]) + ["THROUGHPUT.json"]:
        if (source / name).is_file():
            shutil.copy2(source / name, attempt / name)
    return attempt


@pytest.mark.parametrize("task_id", ["P2-09", "P2-10", "P2-03"])
def test_matrix_rows_resolve_for_verifier(task_id, tmp_path):
    spec = producer.load_spec(task_id, WORKTREE)
    attempt = _stage(tmp_path, task_id, spec)
    matrix = producer.build_matrix(spec, attempt, WORKTREE, INDICES)
    checks = matrix["checks"]
    assert [check["id"] for check in checks] == spec["cases"]
    by_id = {check["id"]: check for check in checks}

    assert by_id["A07"]["test_nodeids"] == []
    selectors = [item["selector"] for item in by_id["A07"]["evidence"]]
    assert "/control/ok" in selectors
    assert sum(1 for item in selectors if item.startswith("/mutations/")) == len(producer.MUTATIONS)
    assigned = [case for case in spec["cases"] if case.startswith("S")]
    assert len(by_id["A08"]["test_nodeids"]) == len(assigned)
    assert any(item["selector"] == "/ok" for item in by_id["A06"]["evidence"])

    for check in checks:
        assert check["status"] in {"pass", "accepted-limit"}
        assert check["command_indices"]
        assert check["evidence"]
        for ref in check["code_refs"]:
            assert "/tests/" not in str(ref["path"]).replace("\\", "/")
            code_path = _resolve_workspace_file(str(ref["path"]), WORKTREE)
            assert code_path is not None, ref
            symbols = _module_symbols(code_path)
            assert symbols is not None and ref["symbol"] in symbols, ref
        for nodeid in check["test_nodeids"]:
            file_part, _, test_part = nodeid.partition("::")
            test_path = _resolve_workspace_file(file_part, WORKTREE)
            assert test_path is not None
            names = _test_node_names(test_path)
            assert names is not None and test_part in names, nodeid
        for item in check["evidence"]:
            assert _selector_resolves(Path(item["path"]), item["selector"]), (check["id"], item)


def test_unknown_case_id_raises(tmp_path):
    spec = producer.load_spec("P2-09", WORKTREE)
    spec["cases"] = list(spec["cases"]) + ["S99"]
    attempt = _stage(tmp_path, "P2-09", spec)
    with pytest.raises(RuntimeError, match="S99"):
        producer.build_matrix(spec, attempt, WORKTREE, INDICES)


def test_ambiguous_case_binding_raises():
    with pytest.raises(RuntimeError, match="test_s0"):
        producer._bind_test_function(["test_s07_one", "test_s07_two"], "S07")
