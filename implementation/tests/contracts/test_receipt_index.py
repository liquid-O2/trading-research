"""Verifier receipt index, failure de-duplication, and directory-owned inventory."""

from __future__ import annotations

from pathlib import Path

from trading_research.research.contracts.identity import file_digest
from trading_research.research.contracts.receipts import (
    DEFAULT_AMENDMENTS_PATH,
    FailureCode,
    _VerifyState,
    _index_task_receipts,
    _unpinned_owned_paths,
    _unique_failures,
    locate_all_task_receipts,
    load_task_graph,
    verify_task_receipt,
)
from tests.rule_discovery.test_p15_01 import write_graph, write_tiny_task


def _write_receipt(tree: Path, rel: str) -> Path:
    path = tree / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}\n")
    return path


def test_receipt_index_skips_jobs_snapshots_and_work_dirs(tmp_path: Path):
    tree = tmp_path / "reports"
    real = [
        _write_receipt(tree, "P15-09/abc/attempt-0001/TASK_RECEIPT.json"),
        _write_receipt(tree, "P15-10/def/attempt-0001/TASK_RECEIPT.json"),
        _write_receipt(tree, "P15-11.json"),
    ]
    _write_receipt(tree, "P15-09/abc/attempt-0001/jobs/2020-01-01/TASK_RECEIPT.json")
    _write_receipt(tree, "P15-09/abc/attempt-0001/snapshots/code/TASK_RECEIPT.json")
    _write_receipt(tree, "P15-09/_work_16a/TASK_RECEIPT.json")
    _write_receipt(tree, "P15-09/abc/decoded/TASK_RECEIPT.json")
    _write_receipt(tree, "P15-09/abc/__pycache__/TASK_RECEIPT.json")
    (tree / "P15-12").write_text("{}\n")

    indexed = _index_task_receipts(tree)
    rglob = locate_all_task_receipts(tree)
    skip = {"jobs", "snapshots", "decoded", "__pycache__"}

    def is_real(path: Path) -> bool:
        parts = path.relative_to(tree).parts
        if any(part in skip for part in parts):
            return False
        if any(part.startswith("_work") for part in parts):
            return False
        return path.name == "TASK_RECEIPT.json"

    restricted = tuple(sorted(path for path in rglob if is_real(path)))
    assert indexed == restricted
    names = {path.relative_to(tree).as_posix() for path in indexed}
    assert "P15-09/abc/attempt-0001/TASK_RECEIPT.json" in names
    assert "P15-10/def/attempt-0001/TASK_RECEIPT.json" in names
    assert "P15-09/abc/attempt-0001/jobs/2020-01-01/TASK_RECEIPT.json" not in names
    assert "P15-09/_work_16a/TASK_RECEIPT.json" not in names

    state = _VerifyState(receipts_root=tree, graph=None, amendments_path=DEFAULT_AMENDMENTS_PATH)
    assert state.all_receipts() == indexed
    p15_09 = state.receipts_for("P15-09")
    assert all(path.relative_to(tree).parts[0] == "P15-09" for path in p15_09)
    assert all("jobs" not in path.parts for path in p15_09)


def test_unique_failures_keeps_first_occurrence():
    from trading_research.research.contracts.receipts import CheckFailure

    first = CheckFailure("IDENTITY", "/a", "one")
    second = CheckFailure("INVENTORY", "/b", "two")
    dup = CheckFailure("IDENTITY", "/a", "one")
    third = CheckFailure("IDENTITY", "/a", "other")
    unique = _unique_failures([first, second, dup, third])
    assert unique == (first, second, third)


def _diamond_graph(path: Path) -> Path:
    keys = [f"A{index:02d}" for index in range(1, 14)]
    return write_graph(
        path,
        [
            {
                "id": "FAIL-ROOT",
                "phase": "phase-1-5",
                "subphase": "00-foundation",
                "dependencies": [],
                "required_acceptance_keys": keys,
                "allowed_terminal_statuses": ["implemented_verified"],
                "native": False,
                "artifacts": [],
            },
            {
                "id": "MID-A",
                "phase": "phase-1-5",
                "subphase": "00-foundation",
                "dependencies": ["FAIL-ROOT"],
                "required_acceptance_keys": keys,
                "allowed_terminal_statuses": ["implemented_verified"],
                "native": False,
                "artifacts": [],
            },
            {
                "id": "MID-B",
                "phase": "phase-1-5",
                "subphase": "00-foundation",
                "dependencies": ["FAIL-ROOT"],
                "required_acceptance_keys": keys,
                "allowed_terminal_statuses": ["implemented_verified"],
                "native": False,
                "artifacts": [],
            },
            {
                "id": "TOP",
                "phase": "phase-1-5",
                "subphase": "00-foundation",
                "dependencies": ["MID-A", "MID-B"],
                "required_acceptance_keys": keys,
                "allowed_terminal_statuses": ["implemented_verified"],
                "native": False,
                "artifacts": [],
            },
        ],
    )


def test_diamond_predecessor_failure_appears_once(tmp_path: Path):
    graph = _diamond_graph(tmp_path / "graph.json")
    root = write_tiny_task(tmp_path, "FAIL-ROOT", exit_code=1)
    mid_a = write_tiny_task(tmp_path, "MID-A", predecessors={"FAIL-ROOT": file_digest(root)})
    mid_b = write_tiny_task(tmp_path, "MID-B", predecessors={"FAIL-ROOT": file_digest(root)})
    top = write_tiny_task(
        tmp_path,
        "TOP",
        predecessors={"MID-A": file_digest(mid_a), "MID-B": file_digest(mid_b)},
    )
    loaded, _ = load_task_graph(graph)
    result = verify_task_receipt(top, graph=loaded, graph_path=graph, receipts_root=tmp_path)
    triples = [(item.code, item.path, item.detail) for item in result.failures]
    assert len(triples) == len(set(triples))
    root_failures = [item for item in result.failures if item.path == str(root) or "FAIL-ROOT" in item.detail]
    codes = [item.code for item in result.failures if item.path == str(root)]
    assert codes.count(FailureCode.COMMAND_EXIT) <= 1
    assert any(item.code == FailureCode.COMMAND_EXIT for item in result.failures)
    assert root_failures


def test_directory_owned_entry_satisfied_when_all_files_pinned(tmp_path: Path):
    owned = tmp_path / "pack/"
    owned.mkdir()
    (owned / "one.py").write_text("x = 1\n")
    (owned / "sub").mkdir()
    (owned / "sub" / "two.py").write_text("y = 2\n")
    (owned / "__pycache__").mkdir()
    (owned / "__pycache__" / "one.cpython-312.pyc").write_bytes(b"pyc")
    files = {
        (owned / "one.py").relative_to(tmp_path).as_posix(): "a",
        (owned / "sub" / "two.py").relative_to(tmp_path).as_posix(): "b",
    }
    assert _unpinned_owned_paths(("pack/",), files, tmp_path) == []


def test_directory_owned_entry_names_unpinned_file(tmp_path: Path):
    owned = tmp_path / "pack/"
    owned.mkdir()
    (owned / "one.py").write_text("x = 1\n")
    (owned / "missing.py").write_text("z = 3\n")
    files = {(owned / "one.py").relative_to(tmp_path).as_posix(): "a"}
    missing = _unpinned_owned_paths(("pack/",), files, tmp_path)
    assert missing == [(owned / "missing.py").relative_to(tmp_path).as_posix()]
