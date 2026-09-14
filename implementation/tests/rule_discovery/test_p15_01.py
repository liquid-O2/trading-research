"""P15-01 receipt verifier checks. Tests call the CLI the way operators do."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from trading_research.research.contracts.identity import (
    ASSURANCE_VERSION,
    artifact_entry,
    code_snapshot_document,
    digest,
    file_digest,
    make_task_receipt,
    plan_snapshot_document,
    write_json_document,
    write_task_receipt,
)
from trading_research.research.contracts.receipts import (
    CheckFailure,
    FailureCode,
    LineageManifestView,
    PINNED_CHECKER_CASE_IDS,
    PINNED_CHECKER_SHA256,
    PhaseReceiptView,
    SubphaseReceiptView,
    TaskReceiptView,
    TaskRef,
)

PYTHON = Path("/workspace/implementation/.venv/bin/python")
TOOL = Path("/workspace/implementation/tools/verify_research_release.py")
P15_00_RECEIPT = Path(
    "/workspace/implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json"
)
P15_00_SHA = "a4c5e6bcecdae8af24b69021bf3d9da50f084ee4a2e96c18857e621d69785d20"


def invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(PYTHON), str(TOOL), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def failure_codes(proc: subprocess.CompletedProcess[str]) -> set[str]:
    payload = json.loads(proc.stdout)
    assert isinstance(payload, list), proc.stdout
    assert all("code" in item and "path" in item and "detail" in item for item in payload)
    return {item["code"] for item in payload}


def acceptance_true() -> dict[str, bool]:
    return {f"A{index:02d}": True for index in range(1, 14)}


def write_graph(path: Path, tasks: list[dict], **extra: object) -> Path:
    payload = {"schema": "research-task-graph-v1", "tasks": tasks}
    payload.update(extra)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return path


def write_tiny_task(
    root: Path,
    task_id: str,
    *,
    predecessors: dict[str, str] | None = None,
    acceptance: dict[str, bool] | None = None,
    disposition: str = "implemented_verified",
    coverage: dict | None = None,
    unresolved: list | None = None,
    report_text: str = "PASS\nall checks passed\n",
    exit_code: int = 0,
    commands: list[dict] | None = None,
    extra_artifacts: list[Path] | None = None,
) -> Path:
    attempt = root / task_id / "attempt-0001"
    attempt.mkdir(parents=True, exist_ok=True)
    note = attempt / "note.txt"
    note.write_text("ok\n")
    report = attempt / "REPORT.md"
    report.write_text(report_text)
    log = attempt / "pytest.log"
    log.write_text("1 passed\n")
    if commands is None:
        commands = [
            {
                "argv": [str(PYTHON), "-m", "pytest", f"tests/rule_discovery/test_{task_id.lower().replace('-', '_')}.py", "-q"],
                "cwd": "/workspace/implementation",
                "exit_code": exit_code,
                "seconds": 0.25,
                "log_path": str(log),
                "log_sha256": file_digest(log),
            }
        ]
    manifest = [
        artifact_entry(note, schema="text"),
        artifact_entry(report, schema="research-task-report-v1"),
        artifact_entry(log, schema="pytest-log"),
    ]
    for extra in extra_artifacts or []:
        manifest.append(artifact_entry(extra, schema="extra"))
    receipt = make_task_receipt(
        task_id=task_id,
        run_id=digest({"task": task_id, "root": str(attempt)})[:16],
        plan_sha256=digest({"plan": task_id}),
        code_sha256=digest({"code": task_id}),
        predecessor_receipts=predecessors or {},
        command_results=commands,
        artifact_manifest=manifest,
        acceptance_checks=acceptance or acceptance_true(),
        disposition=disposition,
        reason="tiny fixture",
        coverage=coverage or {"native": False, "unknown": 0},
        unresolved=unresolved or [],
    )
    path = attempt / "TASK_RECEIPT.json"
    write_task_receipt(path, receipt)
    return path


def clone_p15_00(tmp_path: Path) -> Path:
    src = P15_00_RECEIPT.parent
    dest = tmp_path / "P15-00" / "b291864ccceaca9a" / "attempt-0001"
    shutil.copytree(src, dest)
    receipt_path = dest / "TASK_RECEIPT.json"
    receipt = json.loads(receipt_path.read_text())
    for entry in receipt["artifact_manifest"]:
        new_path = dest / Path(entry["path"]).name
        payload = new_path.read_bytes()
        entry["path"] = str(new_path)
        entry["sha256"] = file_digest(new_path)
        entry["bytes"] = len(payload)
    for command in receipt["command_results"]:
        if command.get("log_path"):
            log = dest / Path(command["log_path"]).name
            command["log_path"] = str(log)
            command["log_sha256"] = file_digest(log)
    receipt_path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    return receipt_path


def foundation_tasks() -> list[dict]:
    keys = [f"A{index:02d}" for index in range(1, 14)]
    return [
        {
            "id": "P15-00",
            "phase": "phase-1-5",
            "subphase": "00-foundation",
            "dependencies": [],
            "required_acceptance_keys": keys,
            "allowed_terminal_statuses": ["implemented_verified"],
            "native": False,
            "artifacts": [],
        },
        {
            "id": "P15-01",
            "phase": "phase-1-5",
            "subphase": "00-foundation",
            "dependencies": ["P15-00"],
            "required_acceptance_keys": keys,
            "allowed_terminal_statuses": ["implemented_verified"],
            "native": False,
            "artifacts": [],
        },
    ]


def test_a01_missing_predecessor_fails_even_if_report_says_pass(tmp_path: Path) -> None:
    receipt = write_tiny_task(
        tmp_path,
        "P15-01",
        predecessors={},
        report_text="PASS\nAll predecessor checks passed.\n",
    )
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.PREDECESSOR_MISSING in failure_codes(proc)
    assert "PASS" in receipt.with_name("REPORT.md").read_text()


def test_a02_tampering_one_artifact_byte_fails(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    cloned = write_tiny_task(tmp_path, "P15-00")
    log = cloned.parent / "pytest.log"
    original = log.read_bytes()
    log.write_bytes(original + b"X")
    proc = invoke("task", "--receipt", str(cloned), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.ARTIFACT_HASH in failure_codes(proc)


def test_a02_flipping_required_acceptance_flag_fails(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    cloned = write_tiny_task(tmp_path, "P15-00")
    receipt = json.loads(cloned.read_text())
    receipt["acceptance_checks"]["A03"] = False
    cloned.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    proc = invoke("task", "--receipt", str(cloned), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.ACCEPTANCE in failure_codes(proc)


def test_a03_blocked_implementation_never_passes_a_phase_gate(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        [
            {
                "id": "P15-00",
                "phase": "phase-1-5",
                "subphase": "00-foundation",
                "dependencies": [],
                "required_acceptance_keys": [f"A{index:02d}" for index in range(1, 14)],
                "allowed_terminal_statuses": ["implemented_verified"],
                "native": False,
                "artifacts": [],
            }
        ],
    )
    dummy = tmp_path / "blocked.json"
    dummy.write_text("{}\n")
    phase = {
        "schema_version": "research-phase-receipt-v2",
        "phase": "phase-1-5",
        "gate": "pass",
        "task_receipts": {
            "P15-00": {
                "path": str(dummy),
                "sha256": file_digest(dummy),
                "disposition": "blocked_implementation",
            }
        },
        "phase_1_5_gate": "pass",
    }
    phase_path = tmp_path / "PHASE_RECEIPT.json"
    phase_path.write_text(json.dumps(phase, indent=2) + "\n")
    proc = invoke("phase", "--receipt", str(phase_path), "--graph", str(graph))
    assert proc.returncode == 2, proc.stdout
    codes = failure_codes(proc)
    assert FailureCode.BLOCKED_IMPLEMENTATION in codes
    assert FailureCode.GATE in codes


def test_a03_input_limits_cannot_excuse_missing_software(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    dummy = tmp_path / "p15-00.json"
    dummy.write_text("{}\n")
    phase = {
        "schema_version": "research-phase-receipt-v2",
        "phase": "phase-1-5",
        "gate": "closed_with_limits",
        "task_receipts": {
            "P15-00": {
                "path": str(dummy),
                "sha256": file_digest(dummy),
                "disposition": "implemented_verified",
            }
        },
        "phase_1_5_gate": "closed_with_limits",
        "unresolved": ["owned MBP-1 gap on 2022-01-03"],
    }
    phase_path = tmp_path / "PHASE_RECEIPT.json"
    phase_path.write_text(json.dumps(phase, indent=2) + "\n")
    proc = invoke("phase", "--receipt", str(phase_path), "--graph", str(graph))
    assert proc.returncode == 2, proc.stdout
    codes = failure_codes(proc)
    assert FailureCode.TASK_MISSING in codes
    assert FailureCode.SOFTWARE_MISSING in codes
    assert FailureCode.GATE in codes


def test_a04_phase_2_without_complete_phase_1_5_gate_fails(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        [
            {
                "id": "P2-00",
                "phase": "phase-2",
                "subphase": "00-entry-gate",
                "dependencies": ["P15-20"],
                "required_acceptance_keys": [f"A{index:02d}" for index in range(1, 14)],
                "allowed_terminal_statuses": ["implemented_verified"],
                "native": False,
                "artifacts": [],
            }
        ],
    )
    dummy = tmp_path / "p2-00.json"
    dummy.write_text("{}\n")
    phase = {
        "schema_version": "research-phase-receipt-v2",
        "phase": "phase-2",
        "gate": "pass",
        "task_receipts": {
            "P2-00": {
                "path": str(dummy),
                "sha256": file_digest(dummy),
                "disposition": "implemented_verified",
            }
        },
        "phase_1_5_gate": "missing",
    }
    phase_path = tmp_path / "PHASE_RECEIPT.json"
    phase_path.write_text(json.dumps(phase, indent=2) + "\n")
    proc = invoke("phase", "--receipt", str(phase_path), "--graph", str(graph))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.PHASE_1_5_GATE in failure_codes(proc)


def test_a05_valid_bootstrap_p15_00_receipt_verifies(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    receipt = write_tiny_task(tmp_path, "P15-00")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["kind"] == "task"


def test_a06_command_exit_codes_hashes_and_coverage_recorded(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    path = write_tiny_task(tmp_path, "P15-00", coverage={"native": False, "unknown": 73})
    proc = invoke("task", "--receipt", str(path), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 0, proc.stdout
    receipt = json.loads(path.read_text())
    command = receipt["command_results"][0]
    assert command["exit_code"] == 0
    assert command["seconds"] > 0
    assert command["log_sha256"] == file_digest(Path(command["log_path"]))
    assert receipt["coverage"]["unknown"] == 73
    assert receipt["coverage"]["native"] is False
    assert receipt["artifact_manifest"]
    assert all(len(entry["sha256"]) == 64 for entry in receipt["artifact_manifest"])


def test_independent_negative_omitted_acceptance_key(tmp_path: Path) -> None:
    checks = acceptance_true()
    del checks["A04"]
    receipt = write_tiny_task(tmp_path, "P15-00", acceptance=checks)
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.ACCEPTANCE in failure_codes(proc)


def test_lineage_future_available_at_fails(tmp_path: Path) -> None:
    blob = tmp_path / "feature.bin"
    blob.write_bytes(b"abc")
    manifest = {
        "schema_version": "research-lineage-manifest-v1",
        "records": [
            {
                "id": "future-perturbation",
                "available_at_ns": 40,
                "issue_at_ns": 20,
                "decision_at_ns": 30,
                "path": str(blob),
                "sha256": file_digest(blob),
            }
        ],
    }
    path = tmp_path / "LINEAGE.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    proc = invoke("lineage", "--manifest", str(path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.LINEAGE_CLOCK in failure_codes(proc)


def test_lineage_valid_clocks_and_hashes_pass(tmp_path: Path) -> None:
    blob = tmp_path / "feature.bin"
    blob.write_bytes(b"abc")
    manifest = {
        "schema_version": "research-lineage-manifest-v1",
        "records": [
            {
                "id": "causal",
                "available_at_ns": 10,
                "issue_at_ns": 20,
                "decision_at_ns": 30,
                "path": str(blob),
                "sha256": file_digest(blob),
                "features": [{"name": "x", "available_at_ns": 10}],
            }
        ],
    }
    path = tmp_path / "LINEAGE.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    proc = invoke("lineage", "--manifest", str(path))
    assert proc.returncode == 0, proc.stdout
    view = LineageManifestView(
        path=str(path),
        schema_version="research-lineage-manifest-v1",
        records=tuple(manifest["records"]),
        document=manifest,
    )
    assert view.records[0]["available_at_ns"] <= view.records[0]["decision_at_ns"]


def test_does_not_demand_market_profitability(tmp_path: Path) -> None:
    receipt = write_tiny_task(
        tmp_path,
        "P15-00",
        coverage={"native": False, "unknown": 0, "pnl": -12.5, "sharpe": -3.0},
    )
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 0, proc.stdout
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True


def test_p15_01_predecessor_must_hash_actual_p15_00_file(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    parent = write_tiny_task(tmp_path, "P15-00")
    receipt = write_tiny_task(
        tmp_path,
        "P15-01",
        predecessors={"P15-00": file_digest(parent)},
        report_text="PASS\n",
    )
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 0, proc.stdout
    wrong = write_tiny_task(
        tmp_path / "wrong",
        "P15-01",
        predecessors={"P15-00": digest({"forged": True})},
        report_text="PASS\n",
    )
    bad = invoke("task", "--receipt", str(wrong), "--graph", str(graph), "--receipts-root", str(tmp_path / "wrong"))
    assert bad.returncode == 2, bad.stdout
    assert FailureCode.PREDECESSOR_HASH in failure_codes(bad)


def test_nonzero_command_without_unresolved_fails(tmp_path: Path) -> None:
    receipt = write_tiny_task(tmp_path, "P15-00", exit_code=1)
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.COMMAND_EXIT in failure_codes(proc)


def test_subphase_pass_and_report_text_is_not_the_gate(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    first = write_tiny_task(tmp_path, "P15-00")
    child = write_tiny_task(tmp_path, "P15-01", predecessors={"P15-00": file_digest(first)})
    log = child.parent / "pytest.log"
    subphase = {
        "schema_version": "research-subphase-receipt-v2",
        "assurance_version": "research-assurance-2026-09-14-v2",
        "subphase_id": "00-foundation",
        "run_id": digest({"sub": "00-foundation"})[:16],
        "task_receipts": {
            "P15-00": {"path": str(first), "sha256": file_digest(first)},
            "P15-01": {"path": str(child), "sha256": file_digest(child)},
        },
        "accepted_schema_versions": ["research-task-receipt-v2"],
        "native_slice_ids": ["2020-01-02", "2023-11-06"],
        "test_evidence": [
            {
                "argv": [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_01.py", "-q"],
                "cwd": "/workspace/implementation",
                "exit_code": 0,
                "seconds": 0.4,
                "log_path": str(log),
                "log_sha256": file_digest(log),
            }
        ],
        "coverage": {"native": False, "unknown": 0},
        "single_writer_audit": {"writer": "p15-01-tests", "checkout": "/workspace"},
        "gate": "pass",
        "unresolved": [],
        "reason": "foundation fixtures",
    }
    path = tmp_path / "SUBPHASE_RECEIPT.json"
    path.write_text(json.dumps(subphase, indent=2) + "\n")
    proc = invoke(
        "subphase",
        "--receipt",
        str(path),
        "--graph",
        str(graph),
        "--receipts-root",
        str(tmp_path),
    )
    assert proc.returncode == 0, proc.stdout
    view = SubphaseReceiptView(
        path=str(path),
        schema_version=subphase["schema_version"],
        subphase_id=subphase["subphase_id"],
        run_id=subphase["run_id"],
        task_receipts={
            "P15-00": TaskRef("P15-00", str(first), file_digest(first)),
            "P15-01": TaskRef("P15-01", str(child), file_digest(child)),
        },
        accepted_schema_versions=tuple(subphase["accepted_schema_versions"]),
        native_slice_ids=tuple(subphase["native_slice_ids"]),
        test_evidence=tuple(subphase["test_evidence"]),
        coverage=subphase["coverage"],
        single_writer_audit=subphase["single_writer_audit"],
        gate="pass",
        unresolved=(),
        reason=subphase["reason"],
        document=subphase,
    )
    assert view.gate == "pass"
    phase_view = PhaseReceiptView(
        path=str(path),
        schema_version="research-phase-receipt-v2",
        phase="phase-1-5",
        gate="fail",
        task_receipts=view.task_receipts,
        phase_1_5_gate="missing",
        document={},
    )
    assert phase_view.phase_1_5_gate == "missing"
    task_view = TaskReceiptView(path=str(first), document=json.loads(first.read_text()))
    assert task_view.document["task_id"] == "P15-00"
    failure = CheckFailure(FailureCode.ACCEPTANCE, str(first), "flag")
    assert failure.to_dict()["code"] == FailureCode.ACCEPTANCE


def write_bound_task(root: Path, task_id: str, *, extra_files: dict[str, str] | None = None) -> Path:
    attempt = root / task_id / "attempt-0001"
    attempt.mkdir(parents=True, exist_ok=True)
    report = attempt / "REPORT.md"
    report.write_text("PASS\n")
    log = attempt / "pytest.log"
    log.write_text("1 passed\n")
    work = attempt / "WORK_LOG.md"
    work.write_text("# log\n")
    decisions = attempt / "DECISIONS.tsv"
    decisions.write_text("ts\tphase\tdecision\twhy\tevidence\tresult\n")
    plan_src = Path("/workspace/planning/phase-1-5/tasks/P15-00.md")
    rel = "planning/phase-1-5/tasks/P15-00.md"
    copy = attempt / "snapshots/plan" / rel
    copy.parent.mkdir(parents=True, exist_ok=True)
    copy.write_bytes(plan_src.read_bytes())
    files = {rel: file_digest(plan_src)}
    plan_doc = plan_snapshot_document(files, {rel: f"snapshots/plan/{rel}"})
    write_json_document(attempt / "PLAN_SNAPSHOT.json", plan_doc)
    code_src = Path("/workspace/implementation/src/trading_research/research/contracts/types.py")
    code_rel = "implementation/src/trading_research/research/contracts/types.py"
    code_copy = attempt / "snapshots/code" / code_rel
    code_copy.parent.mkdir(parents=True, exist_ok=True)
    code_copy.write_bytes(code_src.read_bytes())
    code_files = {code_rel: file_digest(code_src)}
    lock = Path("/workspace/implementation/uv.lock")
    code_doc = code_snapshot_document(
        code_files,
        {code_rel: f"snapshots/code/{code_rel}"},
        runtime={"python": "3.12"},
        dependency_lock_sha256=file_digest(lock if lock.is_file() else Path("/workspace/implementation/pyproject.toml")),
        imported_modules=["trading_research.errors"],
    )
    write_json_document(attempt / "CODE_SNAPSHOT.json", code_doc)
    plan_sha = digest(files)
    code_sha = digest(code_doc)
    draft = {
        "schema_version": "research-draft-manifest-v2",
        "task_id": task_id,
        "assurance_version": ASSURANCE_VERSION,
        "plan_sha256": plan_sha,
        "code_sha256": code_sha,
        "predecessor_receipts": {},
        "input_identities": {},
        "coverage_identity": None,
        "registered_candidate_config": None,
        "declared_study_dates": None,
    }
    write_json_document(attempt / "DRAFT_MANIFEST.json", draft)
    matrix = {
        "schema_version": "research-evidence-matrix-v2",
        "task_id": task_id,
        "assurance_version": ASSURANCE_VERSION,
        "checks": [
            {
                "id": f"A{index:02d}",
                "requirement": f"check A{index:02d}",
                "code_refs": [{"path": "implementation/src/trading_research/research/contracts/receipts.py", "symbol": "verify_task_receipt"}],
                "test_nodeids": ["implementation/tests/rule_discovery/test_p15_01.py::test_a05_valid_bootstrap_p15_00_receipt_verifies"],
                "command_indices": [0],
                "evidence": [{"path": str(report), "sha256": file_digest(report), "selector": "/"}],
                "expected": "true",
                "observed": "true",
                "oracle": "fixture",
                "status": "pass",
            }
            for index in range(1, 14)
        ],
    }
    write_json_document(attempt / "EVIDENCE_MATRIX.json", matrix)
    for name, text in (extra_files or {}).items():
        (attempt / name).write_text(text)
    commands = [
        {
            "argv": [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_01.py", "-q"],
            "cwd": "/workspace/implementation",
            "exit_code": 0,
            "seconds": 0.25,
            "log_path": str(log),
            "log_sha256": file_digest(log),
        }
    ]
    manifest = [
        artifact_entry(attempt / name, schema=schema)
        for name, schema in (
            ("DRAFT_MANIFEST.json", "research-draft-manifest-v2"),
            ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2"),
            ("CODE_SNAPSHOT.json", "research-code-snapshot-v2"),
            ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2"),
            ("WORK_LOG.md", "research-work-log-v1"),
            ("DECISIONS.tsv", "research-decisions-tsv-v1"),
            ("REPORT.md", "research-task-report-v1"),
            ("pytest.log", "pytest-log"),
        )
    ]
    receipt = make_task_receipt(
        task_id=task_id,
        run_id=digest(draft)[:16],
        plan_sha256=plan_sha,
        code_sha256=code_sha,
        predecessor_receipts={},
        command_results=commands,
        artifact_manifest=manifest,
        acceptance_checks=acceptance_true(),
        disposition="implemented_verified",
        reason="bound fixture",
        coverage={"native": False, "unknown": 0},
        unresolved=[],
    )
    path = attempt / "TASK_RECEIPT.json"
    write_task_receipt(path, receipt)
    return path


def bound_graph_tasks() -> list[dict]:
    keys = [f"A{index:02d}" for index in range(1, 14)]
    common = {
        "phase": "phase-1-5",
        "subphase": "00-foundation",
        "required_acceptance_keys": keys,
        "allowed_terminal_statuses": ["implemented_verified"],
        "native": False,
        "artifacts": ["BASELINE_BINDING.json"] if False else [],
        "assurance_cases": [],
    }
    return [
        {"id": "P15-00", "dependencies": [], **common},
        {"id": "P15-01", "dependencies": ["P15-00"], **{k: v for k, v in common.items() if k != "id"}},
    ]


def test_s01_empty_manifest_fails_inventory(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        foundation_tasks(),
        required_task_artifacts=["REPORT.md"],
    )
    receipt = write_tiny_task(tmp_path, "P15-00")
    payload = json.loads(receipt.read_text())
    payload["artifact_manifest"] = []
    receipt.write_text(json.dumps(payload, indent=2) + "\n")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.INVENTORY in failure_codes(proc)


def test_s01_required_task_artifact_omitted_fails(tmp_path: Path) -> None:
    tasks = foundation_tasks()
    tasks[0]["artifacts"] = ["BASELINE_BINDING.json"]
    graph = write_graph(tmp_path / "graph.json", tasks)
    receipt = write_tiny_task(tmp_path, "P15-00")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.INVENTORY in failure_codes(proc)


def test_s01_row_count_mismatch_fails(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    receipt = write_tiny_task(tmp_path, "P15-00")
    rows = receipt.parent / "rows.json"
    rows.write_text(json.dumps([{"a": 1}, {"a": 2}]) + "\n")
    payload = json.loads(receipt.read_text())
    payload["artifact_manifest"].append(
        {"path": str(rows), "sha256": file_digest(rows), "bytes": rows.stat().st_size, "rows": 9, "schema": "rows"}
    )
    receipt.write_text(json.dumps(payload, indent=2) + "\n")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.INVENTORY in failure_codes(proc)


def test_s03_replaced_identities_fail(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        foundation_tasks(),
        required_task_artifacts=[
            "DRAFT_MANIFEST.json",
            "PLAN_SNAPSHOT.json",
            "CODE_SNAPSHOT.json",
            "EVIDENCE_MATRIX.json",
            "WORK_LOG.md",
            "DECISIONS.tsv",
            "REPORT.md",
        ],
        assurance_version=ASSURANCE_VERSION,
    )
    receipt = write_bound_task(tmp_path, "P15-00")
    good = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert good.returncode == 0, good.stdout
    payload = json.loads(receipt.read_text())
    payload["plan_sha256"] = "0" * 64
    receipt.write_text(json.dumps(payload, indent=2) + "\n")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.IDENTITY in failure_codes(proc)


def test_s03_non_hex_plan_identity_fails(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    receipt = write_tiny_task(tmp_path, "P15-00")
    payload = json.loads(receipt.read_text())
    payload["plan_sha256"] = "g" * 64
    receipt.write_text(json.dumps(payload, indent=2) + "\n")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.SCHEMA in failure_codes(proc)


def test_s04_child_of_failed_parent_fails(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    parent = write_tiny_task(tmp_path, "P15-00", acceptance={**acceptance_true(), "A01": False}, disposition="blocked_implementation")
    child = write_tiny_task(tmp_path, "P15-01", predecessors={"P15-00": file_digest(parent)})
    proc = invoke("task", "--receipt", str(child), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    codes = failure_codes(proc)
    assert FailureCode.PREDECESSOR_HASH in codes or FailureCode.ACCEPTANCE in codes
    assert FailureCode.BLOCKED_IMPLEMENTATION in codes or FailureCode.ACCEPTANCE in codes


def test_s04_unknown_subphase_fails(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    first = write_tiny_task(tmp_path, "P15-00")
    child = write_tiny_task(tmp_path, "P15-01", predecessors={"P15-00": file_digest(first)})
    log = child.parent / "pytest.log"
    subphase = {
        "schema_version": "research-subphase-receipt-v2",
        "assurance_version": ASSURANCE_VERSION,
        "subphase_id": "00-foundaton",
        "run_id": digest({"sub": "x"})[:16],
        "task_receipts": {},
        "accepted_schema_versions": ["research-task-receipt-v2"],
        "native_slice_ids": [],
        "test_evidence": [],
        "coverage": {"native": False, "unknown": 0},
        "single_writer_audit": {"writer": "test"},
        "gate": "pass",
        "unresolved": [],
        "reason": "unknown",
    }
    path = tmp_path / "SUBPHASE_RECEIPT.json"
    path.write_text(json.dumps(subphase, indent=2) + "\n")
    proc = invoke("subphase", "--receipt", str(path), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.UNKNOWN_SUBPHASE in failure_codes(proc)
    del log


def test_s04_subphase_reuses_wrong_task_receipt(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    first = write_tiny_task(tmp_path, "P15-00")
    child = write_tiny_task(tmp_path, "P15-01", predecessors={"P15-00": file_digest(first)})
    log = child.parent / "pytest.log"
    subphase = {
        "schema_version": "research-subphase-receipt-v2",
        "assurance_version": ASSURANCE_VERSION,
        "subphase_id": "00-foundation",
        "run_id": digest({"sub": "wrong"})[:16],
        "task_receipts": {
            "P15-00": {"path": str(first), "sha256": file_digest(first)},
            "P15-01": {"path": str(first), "sha256": file_digest(first)},
        },
        "accepted_schema_versions": ["research-task-receipt-v2"],
        "native_slice_ids": [],
        "test_evidence": [
            {
                "argv": [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_01.py", "-q"],
                "cwd": "/workspace/implementation",
                "exit_code": 0,
                "seconds": 0.1,
                "log_path": str(log),
                "log_sha256": file_digest(log),
            }
        ],
        "coverage": {"native": False, "unknown": 0},
        "single_writer_audit": {"writer": "test"},
        "gate": "pass",
        "unresolved": [],
        "reason": "wrong task",
    }
    path = tmp_path / "SUBPHASE_RECEIPT.json"
    path.write_text(json.dumps(subphase, indent=2) + "\n")
    proc = invoke("subphase", "--receipt", str(path), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.TASK_MISMATCH in failure_codes(proc)


def test_s04_phase_2_without_release_fails(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        [
            {
                "id": "P2-00",
                "phase": "phase-2",
                "subphase": "00-entry-gate",
                "dependencies": ["P15-20"],
                "required_acceptance_keys": [f"A{index:02d}" for index in range(1, 14)],
                "allowed_terminal_statuses": ["implemented_verified"],
                "native": False,
                "artifacts": [],
            }
        ],
    )
    dummy = write_tiny_task(tmp_path, "P15-00")
    phase = {
        "schema_version": "research-phase-receipt-v2",
        "phase": "phase-2",
        "gate": "pass",
        "phase_1_5_gate": "pass",
        "task_receipts": {
            "P2-00": {"path": str(dummy), "sha256": file_digest(dummy), "disposition": "implemented_verified"}
        },
    }
    path = tmp_path / "PHASE_RECEIPT.json"
    path.write_text(json.dumps(phase, indent=2) + "\n")
    proc = invoke("phase", "--receipt", str(path), "--graph", str(graph))
    assert proc.returncode == 2, proc.stdout
    codes = failure_codes(proc)
    assert FailureCode.PHASE_1_5_GATE in codes
    assert FailureCode.TASK_MISMATCH in codes


def test_s04_valid_phase_1_5_miniature(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    first = write_tiny_task(tmp_path, "P15-00")
    child = write_tiny_task(tmp_path, "P15-01", predecessors={"P15-00": file_digest(first)})
    phase = {
        "schema_version": "research-phase-receipt-v2",
        "phase": "phase-1-5",
        "gate": "pass",
        "phase_1_5_gate": "pass",
        "task_receipts": {
            "P15-00": {"path": str(first), "sha256": file_digest(first), "disposition": "implemented_verified"},
            "P15-01": {"path": str(child), "sha256": file_digest(child), "disposition": "implemented_verified"},
        },
    }
    path = tmp_path / "PHASE_RECEIPT.json"
    path.write_text(json.dumps(phase, indent=2) + "\n")
    proc = invoke("phase", "--receipt", str(path), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 0, proc.stdout


def test_command_logs_omitted_fail(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    receipt = write_tiny_task(tmp_path, "P15-00")
    payload = json.loads(receipt.read_text())
    for command in payload["command_results"]:
        command.pop("log_path", None)
        command.pop("log_sha256", None)
    receipt.write_text(json.dumps(payload, indent=2) + "\n")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.COMMAND_MISSING in failure_codes(proc)


def test_failed_command_not_excused_by_unresolved(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    receipt = write_tiny_task(tmp_path, "P15-00", exit_code=1, unresolved=["pytest failed with exit 1; it has not been fixed"])
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.COMMAND_EXIT in failure_codes(proc)


def test_lineage_child_cannot_relax_ancestor_cutoff(tmp_path: Path) -> None:
    blob = tmp_path / "row.json"
    blob.write_text(json.dumps({"row_id": "native-1"}) + "\n")
    manifest = {
        "schema_version": "research-lineage-manifest-v1",
        "records": [
            {
                "record_id": "decision-1",
                "issue_at_ns": 10,
                "parents": [
                    {
                        "record_id": "native-1",
                        "event_at_ns": 100,
                        "issue_at_ns": 100,
                        "available_at_ns": 100,
                        "artifact_path": str(blob),
                        "artifact_sha256": file_digest(blob),
                        "row_ids": ["native-1"],
                    }
                ],
            }
        ],
    }
    path = tmp_path / "LINEAGE.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    proc = invoke("lineage", "--manifest", str(path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.LINEAGE_CLOCK in failure_codes(proc)


def test_lineage_invalid_clock_and_missing_hash_fail(tmp_path: Path) -> None:
    blob = tmp_path / "row.json"
    blob.write_text(json.dumps({"row_id": "native-1"}) + "\n")
    base = {
        "schema_version": "research-lineage-manifest-v1",
        "records": [
            {
                "record_id": "decision-1",
                "issue_at_ns": 10,
                "parents": [
                    {
                        "record_id": "native-1",
                        "event_at_ns": 5,
                        "issue_at_ns": 5,
                        "available_at_ns": 5,
                        "artifact_path": str(blob),
                        "artifact_sha256": file_digest(blob),
                        "row_ids": ["native-1"],
                    }
                ],
            }
        ],
    }
    good = tmp_path / "good.json"
    good.write_text(json.dumps(base, indent=2) + "\n")
    assert invoke("lineage", "--manifest", str(good)).returncode == 0
    bad_clock = json.loads(json.dumps(base))
    bad_clock["records"][0]["parents"][0]["available_at_ns"] = "tomorrow"
    clock_path = tmp_path / "bad-clock.json"
    clock_path.write_text(json.dumps(bad_clock, indent=2) + "\n")
    clock = invoke("lineage", "--manifest", str(clock_path))
    assert clock.returncode == 2
    assert FailureCode.LINEAGE_CLOCK in failure_codes(clock)
    no_hash = json.loads(json.dumps(base))
    no_hash["records"][0]["parents"][0].pop("artifact_sha256")
    hash_path = tmp_path / "no-hash.json"
    hash_path.write_text(json.dumps(no_hash, indent=2) + "\n")
    missing = invoke("lineage", "--manifest", str(hash_path))
    assert missing.returncode == 2
    assert FailureCode.LINEAGE_HASH in failure_codes(missing)


def test_forged_evidence_matrix_fails(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        foundation_tasks(),
        required_task_artifacts=[
            "DRAFT_MANIFEST.json",
            "PLAN_SNAPSHOT.json",
            "CODE_SNAPSHOT.json",
            "EVIDENCE_MATRIX.json",
            "WORK_LOG.md",
            "DECISIONS.tsv",
            "REPORT.md",
        ],
        assurance_version=ASSURANCE_VERSION,
    )
    receipt = write_bound_task(tmp_path, "P15-00")
    matrix_path = receipt.parent / "EVIDENCE_MATRIX.json"
    matrix = json.loads(matrix_path.read_text())
    matrix["checks"][0]["evidence"] = []
    matrix_path.write_text(json.dumps(matrix, indent=2) + "\n")
    payload = json.loads(receipt.read_text())
    for entry in payload["artifact_manifest"]:
        if Path(entry["path"]).name == "EVIDENCE_MATRIX.json":
            entry["sha256"] = file_digest(matrix_path)
            entry["bytes"] = matrix_path.stat().st_size
    receipt.write_text(json.dumps(payload, indent=2) + "\n")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.INVENTORY in failure_codes(proc)


def test_gate_review_missing_and_stale_fail(tmp_path: Path) -> None:
    graph = write_graph(tmp_path / "graph.json", foundation_tasks())
    first = write_tiny_task(tmp_path, "P15-00")
    child = write_tiny_task(tmp_path, "P15-01", predecessors={"P15-00": file_digest(first)})
    log = child.parent / "pytest.log"
    subphase = {
        "schema_version": "research-subphase-receipt-v2",
        "assurance_version": ASSURANCE_VERSION,
        "subphase_id": "00-foundation",
        "run_id": digest({"sub": "gate"})[:16],
        "task_receipts": {
            "P15-00": {"path": str(first), "sha256": file_digest(first)},
            "P15-01": {"path": str(child), "sha256": file_digest(child)},
        },
        "accepted_schema_versions": ["research-task-receipt-v2"],
        "native_slice_ids": [],
        "test_evidence": [
            {
                "argv": [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_01.py", "-q"],
                "cwd": "/workspace/implementation",
                "exit_code": 0,
                "seconds": 0.1,
                "log_path": str(log),
                "log_sha256": file_digest(log),
            }
        ],
        "coverage": {"native": False, "unknown": 0},
        "single_writer_audit": {"writer": "test"},
        "gate": "pass",
        "unresolved": [],
        "reason": "gate tests",
    }
    path = tmp_path / "SUBPHASE_RECEIPT.json"
    path.write_text(json.dumps(subphase, indent=2) + "\n")
    missing = invoke(
        "subphase",
        "--receipt",
        str(path),
        "--graph",
        str(graph),
        "--receipts-root",
        str(tmp_path),
        "--gate-review",
        str(tmp_path / "missing.json"),
    )
    assert missing.returncode == 2, missing.stdout
    assert FailureCode.JSON_PARSE in failure_codes(missing) or FailureCode.GATE_REVIEW in failure_codes(missing)
    review = {
        "schema_version": "research-gate-review-v2",
        "assurance_version": ASSURANCE_VERSION,
        "subphase_id": "00-foundation",
        "verdict": "pass",
        "candidate": {"path": str(path), "sha256": "0" * 64},
        "reviewed_task_ids": ["P15-00", "P15-01"],
        "findings": [],
        "independent_suite": {"checker_sha256": "0" * 64, "results_path": str(tmp_path / "no-results.json")},
    }
    review_path = tmp_path / "GATE_REVIEW.json"
    review_path.write_text(json.dumps(review, indent=2) + "\n")
    stale = invoke(
        "subphase",
        "--receipt",
        str(path),
        "--graph",
        str(graph),
        "--receipts-root",
        str(tmp_path),
        "--gate-review",
        str(review_path),
    )
    assert stale.returncode == 2, stale.stdout
    assert FailureCode.GATE_REVIEW in failure_codes(stale)


REGISTRY = Path("/workspace/planning/research-program/ASSURANCE_CASES.json")


def _refresh_named(receipt: Path, name: str) -> dict:
    payload = json.loads(receipt.read_text())
    for entry in payload["artifact_manifest"]:
        if Path(entry["path"]).name == name:
            path = Path(entry["path"])
            entry["sha256"] = file_digest(path)
            entry["bytes"] = path.stat().st_size
    receipt.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    return payload


def _rebind_draft(receipt: Path, **draft_updates: object) -> None:
    payload = json.loads(receipt.read_text())
    named = {Path(entry["path"]).name: entry for entry in payload["artifact_manifest"]}
    draft_path = Path(named["DRAFT_MANIFEST.json"]["path"])
    draft = json.loads(draft_path.read_text())
    draft.update(draft_updates)
    draft_path.write_text(json.dumps(draft, sort_keys=True, indent=2) + "\n")
    named["DRAFT_MANIFEST.json"].update(sha256=file_digest(draft_path), bytes=draft_path.stat().st_size)
    payload["run_id"] = digest(draft)[:16]
    if "code_sha256" in draft_updates:
        payload["code_sha256"] = draft["code_sha256"]
    if "plan_sha256" in draft_updates:
        payload["plan_sha256"] = draft["plan_sha256"]
    if "predecessor_receipts" in draft_updates:
        payload["predecessor_receipts"] = draft["predecessor_receipts"]
    receipt.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")


def _write_pinned_results(path: Path, *, candidate: Path, graph: Path, extra: dict[str, str] | None = None) -> Path:
    inputs = {str(candidate): file_digest(candidate), str(graph): file_digest(graph)}
    if extra:
        inputs.update(extra)
    document = {
        "schema": "foundation-adversarial-results-v1",
        "harness_sha256": PINNED_CHECKER_SHA256,
        "input_hashes": inputs,
        "cases": [{"case": name, "kind": "cli", "passed": True} for name in PINNED_CHECKER_CASE_IDS],
        "status": "pass",
    }
    path.write_text(json.dumps(document, sort_keys=True, indent=2) + "\n")
    return path


def _write_pair(tmp_path: Path) -> tuple[Path, Path, Path]:
    graph = write_graph(
        tmp_path / "graph.json",
        bound_graph_tasks(),
        required_task_artifacts=[
            "DRAFT_MANIFEST.json",
            "PLAN_SNAPSHOT.json",
            "CODE_SNAPSHOT.json",
            "EVIDENCE_MATRIX.json",
            "WORK_LOG.md",
            "DECISIONS.tsv",
            "REPORT.md",
        ],
        assurance_version=ASSURANCE_VERSION,
    )
    first = write_bound_task(tmp_path, "P15-00")
    child = write_bound_task(tmp_path, "P15-01")
    _rebind_draft(child, predecessor_receipts={"P15-00": file_digest(first)})
    return graph, first, child


def _write_subphase(tmp_path: Path, graph: Path, first: Path, child: Path) -> Path:
    log = child.parent / "pytest.log"
    subphase = {
        "schema_version": "research-subphase-receipt-v2",
        "assurance_version": ASSURANCE_VERSION,
        "subphase_id": "00-foundation",
        "run_id": digest({"sub": str(tmp_path)})[:16],
        "task_receipts": {
            "P15-00": {"path": str(first), "sha256": file_digest(first)},
            "P15-01": {"path": str(child), "sha256": file_digest(child)},
        },
        "accepted_schema_versions": ["research-task-receipt-v2"],
        "native_slice_ids": [],
        "test_evidence": [
            {
                "argv": [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_01.py", "-q"],
                "cwd": "/workspace/implementation",
                "exit_code": 0,
                "seconds": 0.1,
                "log_path": str(log),
                "log_sha256": file_digest(log),
            }
        ],
        "coverage": {"native": False, "unknown": 0},
        "single_writer_audit": {"writer": "test"},
        "gate": "pass",
        "unresolved": [],
        "reason": "focused repair tests",
    }
    path = tmp_path / "SUBPHASE_RECEIPT.json"
    path.write_text(json.dumps(subphase, indent=2) + "\n")
    return path


def _snapshot_binding(receipt: Path, name: str) -> dict[str, str]:
    payload = json.loads(receipt.read_text())
    for entry in payload["artifact_manifest"]:
        if Path(entry["path"]).name == name:
            binding = {"path": entry["path"], "sha256": entry["sha256"]}
            if name == "CODE_SNAPSHOT.json":
                binding["code_sha256"] = payload["code_sha256"]
            return binding
    raise AssertionError(name)


def _write_review(tmp_path: Path, *, subphase: Path, graph: Path, first: Path, child: Path) -> Path:
    results = _write_pinned_results(
        tmp_path / "INDEPENDENT_RESULTS.json",
        candidate=subphase,
        graph=graph,
        extra={str(first): file_digest(first), str(child): file_digest(child)},
    )
    review = {
        "schema_version": "research-gate-review-v2",
        "assurance_version": ASSURANCE_VERSION,
        "subphase_id": "00-foundation",
        "verdict": "pass",
        "candidate": {"path": str(subphase), "sha256": file_digest(subphase)},
        "reviewed_task_ids": ["P15-00", "P15-01"],
        "reviewed_at": "2026-09-14T12:00:00Z",
        "reviewer": "p15-01-tests",
        "findings": [],
        "graph": {"path": str(graph), "sha256": file_digest(graph)},
        "registry": {"path": str(REGISTRY), "sha256": file_digest(REGISTRY)},
        "commands": [{"argv": [str(PYTHON), "-m", "pytest", "-q"], "exit_code": 0}],
        "code_snapshots": {
            "P15-00": _snapshot_binding(first, "CODE_SNAPSHOT.json"),
            "P15-01": _snapshot_binding(child, "CODE_SNAPSHOT.json"),
        },
        "evidence_matrices": {
            "P15-00": _snapshot_binding(first, "EVIDENCE_MATRIX.json"),
            "P15-01": _snapshot_binding(child, "EVIDENCE_MATRIX.json"),
        },
        "independent_suite": {
            "checker_sha256": PINNED_CHECKER_SHA256,
            "results_path": str(results),
            "results_sha256": file_digest(results),
        },
    }
    path = tmp_path / "GATE_REVIEW.json"
    path.write_text(json.dumps(review, indent=2) + "\n")
    return path


def test_gate_review_accepted_control_passes(tmp_path: Path) -> None:
    graph, first, child = _write_pair(tmp_path)
    subphase = _write_subphase(tmp_path, graph, first, child)
    review = _write_review(tmp_path, subphase=subphase, graph=graph, first=first, child=child)
    proc = invoke("subphase", "--receipt", str(subphase), "--graph", str(graph), "--receipts-root", str(tmp_path), "--gate-review", str(review))
    assert proc.returncode == 0, proc.stdout


def test_gate_review_nonobject_fails_closed(tmp_path: Path) -> None:
    graph, first, child = _write_pair(tmp_path)
    subphase = _write_subphase(tmp_path, graph, first, child)
    path = tmp_path / "list-review.json"
    path.write_text("[]\n")
    proc = invoke("subphase", "--receipt", str(subphase), "--graph", str(graph), "--receipts-root", str(tmp_path), "--gate-review", str(path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.GATE_REVIEW in failure_codes(proc)
    assert "JSON object" in proc.stdout


def test_gate_review_null_cases_and_wrong_results_hash_fail(tmp_path: Path) -> None:
    graph, first, child = _write_pair(tmp_path)
    subphase = _write_subphase(tmp_path, graph, first, child)
    review_path = _write_review(tmp_path, subphase=subphase, graph=graph, first=first, child=child)
    review = json.loads(review_path.read_text())
    forged = tmp_path / "forged-results.json"
    forged.write_text(json.dumps({"status": "pass", "cases": [None] * 27, "input_hashes": {"arbitrary": file_digest(subphase)}}, indent=2) + "\n")
    review["independent_suite"]["results_path"] = str(forged)
    review_path.write_text(json.dumps(review, indent=2) + "\n")
    proc = invoke("subphase", "--receipt", str(subphase), "--graph", str(graph), "--receipts-root", str(tmp_path), "--gate-review", str(review_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.GATE_REVIEW in failure_codes(proc)
    assert "results_sha256" in proc.stdout or "pinned" in proc.stdout or "object" in proc.stdout
    review["independent_suite"]["results_sha256"] = file_digest(forged)
    review_path.write_text(json.dumps(review, indent=2) + "\n")
    hashed = invoke("subphase", "--receipt", str(subphase), "--graph", str(graph), "--receipts-root", str(tmp_path), "--gate-review", str(review_path))
    assert hashed.returncode == 2, hashed.stdout
    assert FailureCode.GATE_REVIEW in failure_codes(hashed)
    assert "not an object" in hashed.stdout or "pinned" in hashed.stdout or "harness" in hashed.stdout


def test_gate_review_missing_bindings_fail_per_field(tmp_path: Path) -> None:
    graph, first, child = _write_pair(tmp_path)
    subphase = _write_subphase(tmp_path, graph, first, child)
    review_path = _write_review(tmp_path, subphase=subphase, graph=graph, first=first, child=child)
    review = json.loads(review_path.read_text())
    for key in ("code_snapshots", "evidence_matrices", "graph", "registry", "commands", "reviewed_at", "reviewer"):
        mutated = json.loads(json.dumps(review))
        mutated.pop(key)
        path = tmp_path / f"missing-{key}.json"
        path.write_text(json.dumps(mutated, indent=2) + "\n")
        proc = invoke("subphase", "--receipt", str(subphase), "--graph", str(graph), "--receipts-root", str(tmp_path), "--gate-review", str(path))
        assert proc.returncode == 2, (key, proc.stdout)
        assert FailureCode.GATE_REVIEW in failure_codes(proc)
        assert key.split("[")[0] in proc.stdout
    unknown = json.loads(json.dumps(review))
    unknown["subphase_id"] = "no-such-subphase"
    unknown["reviewed_task_ids"] = []
    unknown_path = tmp_path / "unknown-subphase-review.json"
    unknown_path.write_text(json.dumps(unknown, indent=2) + "\n")
    proc = invoke("subphase", "--receipt", str(subphase), "--graph", str(graph), "--receipts-root", str(tmp_path), "--gate-review", str(unknown_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.GATE_REVIEW in failure_codes(proc)
    assert "unknown review subphase" in proc.stdout or "reviewed_task_ids" in proc.stdout


def test_matrix_failed_checks_rejected_when_accepted(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        bound_graph_tasks(),
        required_task_artifacts=["DRAFT_MANIFEST.json", "PLAN_SNAPSHOT.json", "CODE_SNAPSHOT.json", "EVIDENCE_MATRIX.json", "WORK_LOG.md", "DECISIONS.tsv", "REPORT.md"],
        assurance_version=ASSURANCE_VERSION,
    )
    receipt = write_bound_task(tmp_path, "P15-00")
    control = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert control.returncode == 0, control.stdout
    matrix_path = receipt.parent / "EVIDENCE_MATRIX.json"
    matrix = json.loads(matrix_path.read_text())
    for check in matrix["checks"]:
        check.update(status="fail", evidence=[], code_refs=[], test_nodeids=[], command_indices=[])
    matrix_path.write_text(json.dumps(matrix, indent=2) + "\n")
    _refresh_named(receipt, "EVIDENCE_MATRIX.json")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.ACCEPTANCE in failure_codes(proc)


def test_matrix_nonexistent_symbol_node_and_selector_fail(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        bound_graph_tasks(),
        required_task_artifacts=["DRAFT_MANIFEST.json", "PLAN_SNAPSHOT.json", "CODE_SNAPSHOT.json", "EVIDENCE_MATRIX.json", "WORK_LOG.md", "DECISIONS.tsv", "REPORT.md"],
        assurance_version=ASSURANCE_VERSION,
    )
    receipt = write_bound_task(tmp_path, "P15-00")
    matrix_path = receipt.parent / "EVIDENCE_MATRIX.json"

    def mutate_and_run(mutator) -> subprocess.CompletedProcess[str]:
        matrix = json.loads(Path(receipt.parent / "EVIDENCE_MATRIX.json").read_text())
        mutator(matrix)
        matrix_path.write_text(json.dumps(matrix, indent=2) + "\n")
        _refresh_named(receipt, "EVIDENCE_MATRIX.json")
        return invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))

    symbol = mutate_and_run(lambda matrix: matrix["checks"][0]["code_refs"].__setitem__(0, {"path": matrix["checks"][0]["code_refs"][0]["path"], "symbol": "definitely_nonexistent_review_probe_symbol"}))
    assert symbol.returncode == 2, symbol.stdout
    assert FailureCode.INVENTORY in failure_codes(symbol)
    assert "definitely_nonexistent_review_probe_symbol" in symbol.stdout

    receipt = write_bound_task(tmp_path / "nodes", "P15-00")
    matrix_path = receipt.parent / "EVIDENCE_MATRIX.json"
    node = mutate_and_run(lambda matrix: matrix["checks"][0].__setitem__("test_nodeids", ["implementation/tests/rule_discovery/test_p15_00.py::test_definitely_nonexistent_review_probe"]))
    assert node.returncode == 2, node.stdout
    assert FailureCode.INVENTORY in failure_codes(node)
    assert "test_definitely_nonexistent_review_probe" in node.stdout

    receipt = write_bound_task(tmp_path / "selector", "P15-00")
    matrix_path = receipt.parent / "EVIDENCE_MATRIX.json"
    json_evidence = receipt.parent / "EVIDENCE_MATRIX.json"
    selector = mutate_and_run(lambda matrix: matrix["checks"][0]["evidence"].__setitem__(0, {"path": str(json_evidence), "sha256": file_digest(json_evidence), "selector": "/definitely_nonexistent_review_probe_pointer"}))
    assert selector.returncode == 2, selector.stdout
    assert FailureCode.INVENTORY in failure_codes(selector)
    assert "/definitely_nonexistent_review_probe_pointer" in selector.stdout

    receipt = write_bound_task(tmp_path / "omitted", "P15-00")
    matrix_path = receipt.parent / "EVIDENCE_MATRIX.json"
    omitted = mutate_and_run(lambda matrix: matrix["checks"][0]["evidence"][0].__delitem__("selector"))
    assert omitted.returncode == 2, omitted.stdout
    assert FailureCode.INVENTORY in failure_codes(omitted)
    assert "selector" in omitted.stdout


def test_code_false_file_hash_and_plan_copies_fail(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        bound_graph_tasks(),
        required_task_artifacts=["DRAFT_MANIFEST.json", "PLAN_SNAPSHOT.json", "CODE_SNAPSHOT.json", "EVIDENCE_MATRIX.json", "WORK_LOG.md", "DECISIONS.tsv", "REPORT.md"],
        assurance_version=ASSURANCE_VERSION,
    )
    receipt = write_bound_task(tmp_path, "P15-00")
    control = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert control.returncode == 0, control.stdout
    code_path = receipt.parent / "CODE_SNAPSHOT.json"
    code = json.loads(code_path.read_text())
    target = next(iter(code["files"]))
    code["files"][target] = "0" * 64
    code_path.write_text(json.dumps(code, indent=2) + "\n")
    _refresh_named(receipt, "CODE_SNAPSHOT.json")
    _rebind_draft(receipt, code_sha256=digest(code))
    false_hash = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert false_hash.returncode == 2, false_hash.stdout
    assert FailureCode.IDENTITY in failure_codes(false_hash)

    receipt = write_bound_task(tmp_path / "plan", "P15-00")
    plan_path = receipt.parent / "PLAN_SNAPSHOT.json"
    plan = json.loads(plan_path.read_text())
    plan["snapshot_paths"] = {}
    plan_path.write_text(json.dumps(plan, indent=2) + "\n")
    _refresh_named(receipt, "PLAN_SNAPSHOT.json")
    missing_copies = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path / "plan"))
    assert missing_copies.returncode == 2, missing_copies.stdout
    assert FailureCode.ARTIFACT_MISSING in failure_codes(missing_copies)

    receipt = write_bound_task(tmp_path / "omitted-paths", "P15-00")
    plan_path = receipt.parent / "PLAN_SNAPSHOT.json"
    plan = json.loads(plan_path.read_text())
    plan.pop("snapshot_paths")
    plan_path.write_text(json.dumps(plan, indent=2) + "\n")
    _refresh_named(receipt, "PLAN_SNAPSHOT.json")
    omitted = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path / "omitted-paths"))
    assert omitted.returncode == 2, omitted.stdout
    assert FailureCode.ARTIFACT_MISSING in failure_codes(omitted) or FailureCode.SCHEMA in failure_codes(omitted)

    receipt = write_bound_task(tmp_path / "bare-input", "P15-00")
    _rebind_draft(receipt, input_identities={"census_file_sha256": "a" * 64})
    bare = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path / "bare-input"))
    assert bare.returncode == 2, bare.stdout
    assert FailureCode.IDENTITY in failure_codes(bare)
    assert "path" in bare.stdout


def test_artifact_wrong_schema_and_unrelated_contents_fail(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        bound_graph_tasks(),
        required_task_artifacts=["DRAFT_MANIFEST.json", "PLAN_SNAPSHOT.json", "CODE_SNAPSHOT.json", "EVIDENCE_MATRIX.json", "WORK_LOG.md", "DECISIONS.tsv", "REPORT.md"],
        assurance_version=ASSURANCE_VERSION,
    )
    receipt = write_bound_task(tmp_path, "P15-00")
    examples = receipt.parent / "SCHEMA_EXAMPLES.json"
    examples.write_text(json.dumps({"schema_version": "research-wrong-v900", "unrelated": True}, indent=2) + "\n")
    payload = json.loads(receipt.read_text())
    payload["artifact_manifest"].append(
        {"path": str(examples), "sha256": file_digest(examples), "bytes": examples.stat().st_size, "rows": None, "schema": "research-schema-examples-v2"}
    )
    receipt.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    wrong = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert wrong.returncode == 2, wrong.stdout
    assert FailureCode.SCHEMA in failure_codes(wrong)

    receipt = write_bound_task(tmp_path / "contents", "P15-00")
    examples = receipt.parent / "SCHEMA_EXAMPLES.json"
    examples.write_text(json.dumps({"schema_version": "research-schema-examples-v2", "unrelated": True}, indent=2) + "\n")
    payload = json.loads(receipt.read_text())
    payload["artifact_manifest"].append(
        {"path": str(examples), "sha256": file_digest(examples), "bytes": examples.stat().st_size, "rows": None, "schema": "research-schema-examples-v2"}
    )
    receipt.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    contents = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path / "contents"))
    assert contents.returncode == 2, contents.stdout
    assert FailureCode.SCHEMA in failure_codes(contents)

    receipt = write_bound_task(tmp_path / "missing-label", "P15-00")
    examples = receipt.parent / "SCHEMA_EXAMPLES.json"
    examples.write_text(json.dumps({"native_replay": {"kind": "native"}}, indent=2) + "\n")
    payload = json.loads(receipt.read_text())
    payload["artifact_manifest"].append(
        {"path": str(examples), "sha256": file_digest(examples), "bytes": examples.stat().st_size, "rows": None, "schema": "research-schema-examples-v2"}
    )
    receipt.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    missing = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path / "missing-label"))
    assert missing.returncode == 2, missing.stdout
    assert FailureCode.SCHEMA in failure_codes(missing)

    receipt = write_bound_task(tmp_path / "ok-schema", "P15-00")
    examples = receipt.parent / "SCHEMA_EXAMPLES.json"
    examples.write_text(json.dumps({"schema": "research-schema-examples-v2", "native_replay": {"kind": "native"}}, indent=2) + "\n")
    payload = json.loads(receipt.read_text())
    payload["artifact_manifest"].append(
        {"path": str(examples), "sha256": file_digest(examples), "bytes": examples.stat().st_size, "rows": None, "schema": "research-schema-examples-v2"}
    )
    receipt.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    ok_schema = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path / "ok-schema"))
    assert ok_schema.returncode == 0, ok_schema.stdout


def test_lineage_missing_clock_path_and_row_fail(tmp_path: Path) -> None:
    leaf = tmp_path / "lineage-evidence.json"
    leaf.write_text(json.dumps({"records": [{"row_id": "real-row", "value": 1}]}) + "\n")
    digest_value = file_digest(leaf)
    valid_leaf = {
        "artifact_path": str(leaf),
        "artifact_sha256": digest_value,
        "row_ids": ["real-row"],
        "available_at_ns": 5,
        "event_at_ns": 5,
    }

    def run(name: str, leaf_doc: dict, expected: int) -> subprocess.CompletedProcess[str]:
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps({"schema_version": "research-lineage-manifest-v1", "records": [{"issue_at_ns": 10, "features": [{"evidence": [leaf_doc]}]}]}, indent=2) + "\n")
        return invoke("lineage", "--manifest", str(path))

    control = run("valid", valid_leaf, 0)
    assert control.returncode == 0, control.stdout
    late = run("late", {**valid_leaf, "available_at_ns": 100}, 2)
    assert late.returncode == 2, late.stdout
    assert FailureCode.LINEAGE_CLOCK in failure_codes(late)
    missing = run("missing", {"artifact_sha256": digest_value, "row_ids": ["no-such-row"], "event_at_ns": 100}, 2)
    assert missing.returncode == 2, missing.stdout
    assert FailureCode.LINEAGE_CLOCK in failure_codes(missing)
    assert FailureCode.LINEAGE_HASH in failure_codes(missing)
    omitted_clock = run("omitted-clock", {**valid_leaf, "available_at_ns": "tomorrow"}, 2)
    assert omitted_clock.returncode == 2
    assert FailureCode.LINEAGE_CLOCK in failure_codes(omitted_clock)
    bad_row = run("bad-row", {**valid_leaf, "row_ids": ["no-such-row"]}, 2)
    assert bad_row.returncode == 2, bad_row.stdout
    assert FailureCode.LINEAGE_HASH in failure_codes(bad_row)
    assert "row_ids" in bad_row.stdout
    outcome = {
        "schema_version": "research-lineage-manifest-v1",
        "records": [{
            "issue_at_ns": 10,
            "outcomes": [{
                "artifact_path": str(leaf),
                "artifact_sha256": digest_value,
                "row_ids": ["real-row"],
                "available_at_ns": 5,
                "event_at_ns": 100,
            }],
        }],
    }
    outcome_path = tmp_path / "outcome.json"
    outcome_path.write_text(json.dumps(outcome, indent=2) + "\n")
    future_ok = invoke("lineage", "--manifest", str(outcome_path))
    assert future_ok.returncode == 0, future_ok.stdout
    predictor = {
        "schema_version": "research-lineage-manifest-v1",
        "records": [{
            "issue_at_ns": 10,
            "features": [{
                "artifact_path": str(leaf),
                "artifact_sha256": digest_value,
                "row_ids": ["real-row"],
                "available_at_ns": 5,
                "event_at_ns": 100,
            }],
        }],
    }
    predictor_path = tmp_path / "predictor.json"
    predictor_path.write_text(json.dumps(predictor, indent=2) + "\n")
    future_bad = invoke("lineage", "--manifest", str(predictor_path))
    assert future_bad.returncode == 2, future_bad.stdout
    assert FailureCode.LINEAGE_CLOCK in failure_codes(future_bad)


def test_matrix_unsupported_cannot_close_accepted_task(tmp_path: Path) -> None:
    graph = write_graph(
        tmp_path / "graph.json",
        bound_graph_tasks(),
        required_task_artifacts=["DRAFT_MANIFEST.json", "PLAN_SNAPSHOT.json", "CODE_SNAPSHOT.json", "EVIDENCE_MATRIX.json", "WORK_LOG.md", "DECISIONS.tsv", "REPORT.md"],
        assurance_version=ASSURANCE_VERSION,
    )
    receipt = write_bound_task(tmp_path, "P15-00")
    control = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert control.returncode == 0, control.stdout
    matrix_path = receipt.parent / "EVIDENCE_MATRIX.json"
    matrix = json.loads(matrix_path.read_text())
    for row in matrix["checks"]:
        row.update(status="unsupported", evidence=[], code_refs=[], test_nodeids=[], command_indices=[])
    matrix_path.write_text(json.dumps(matrix, indent=2) + "\n")
    _refresh_named(receipt, "EVIDENCE_MATRIX.json")
    proc = invoke("task", "--receipt", str(receipt), "--graph", str(graph), "--receipts-root", str(tmp_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.ACCEPTANCE in failure_codes(proc)
    assert "unsupported" in proc.stdout


def test_gate_review_input_hash_must_pair_path_and_digest(tmp_path: Path) -> None:
    graph, first, child = _write_pair(tmp_path)
    subphase = _write_subphase(tmp_path, graph, first, child)
    review_path = _write_review(tmp_path, subphase=subphase, graph=graph, first=first, child=child)
    control = invoke("subphase", "--receipt", str(subphase), "--graph", str(graph), "--receipts-root", str(tmp_path), "--gate-review", str(review_path))
    assert control.returncode == 0, control.stdout
    review = json.loads(review_path.read_text())
    forged = {
        "schema": "foundation-adversarial-results-v1",
        "harness_sha256": PINNED_CHECKER_SHA256,
        "status": "pass",
        "cases": [{"case": name, "kind": "cli", "passed": True} for name in PINNED_CHECKER_CASE_IDS],
        "input_hashes": {
            str(subphase): "0" * 64,
            "decoy_candidate": file_digest(subphase),
            str(graph): file_digest(graph),
            str(first): file_digest(first),
            str(child): file_digest(child),
        },
    }
    results_path = tmp_path / "split-results.json"
    results_path.write_text(json.dumps(forged, indent=2) + "\n")
    review["independent_suite"]["results_path"] = str(results_path)
    review["independent_suite"]["results_sha256"] = file_digest(results_path)
    review_path.write_text(json.dumps(review, indent=2) + "\n")
    proc = invoke("subphase", "--receipt", str(subphase), "--graph", str(graph), "--receipts-root", str(tmp_path), "--gate-review", str(review_path))
    assert proc.returncode == 2, proc.stdout
    assert FailureCode.GATE_REVIEW in failure_codes(proc)
    assert "bound together" in proc.stdout or "candidate" in proc.stdout
