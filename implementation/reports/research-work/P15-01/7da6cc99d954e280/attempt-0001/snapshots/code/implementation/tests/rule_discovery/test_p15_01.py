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
    code_doc = code_snapshot_document(
        code_files,
        {code_rel: f"snapshots/code/{code_rel}"},
        runtime={"python": "3.12"},
        dependency_lock_sha256="b" * 64,
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
    blob.write_text("{}\n")
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
    blob.write_text("{}\n")
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
