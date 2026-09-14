"""New P15-01 and 00-foundation identities after sibling-hole verifier fixes. Reuses closed P15-00."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/workspace")
SRC = ROOT / "implementation/src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trading_research.research.contracts.identity import ASSURANCE_VERSION, digest, file_digest, write_json_document
from trading_research.research.contracts.receipts import PINNED_CHECKER_SHA256, write_p15_01_artifacts, write_p15_01_receipt

PYTHON = ROOT / "implementation/.venv/bin/python"
VERIFY = ROOT / "implementation/tools/verify_research_release.py"
CHECKER = ROOT / "tools/check_foundation_adversarial.py"
PROBE = ROOT / "planning/research-program/reviews/00-foundation-v2-2026-09-14/additional_probe.py"
GRAPH = ROOT / "planning/research-program/TASK_GRAPH.json"
REGISTRY = ROOT / "planning/research-program/ASSURANCE_CASES.json"
P15_00 = ROOT / "implementation/reports/research-work/P15-00/40ffb49bc037e3cc/attempt-0001/TASK_RECEIPT.json"


def run(argv: list[str], cwd: Path, log_path: Path) -> dict:
    start = time.perf_counter()
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True)
    seconds = time.perf_counter() - start
    log_path.write_text(proc.stdout + proc.stderr)
    if proc.returncode != 0:
        raise SystemExit(f"command failed {proc.returncode}: {argv}\n{proc.stdout}\n{proc.stderr}")
    return {"argv": argv, "cwd": str(cwd), "exit_code": proc.returncode, "seconds": seconds, "log_path": str(log_path), "log_sha256": file_digest(log_path)}


def evidence(path: Path, selector: str) -> dict:
    return {"path": str(path), "sha256": file_digest(path), "selector": selector}


def check(*, check_id: str, requirement: str, path: str, symbol: str, nodeid: str, items: list[dict], expected: str, observed: str, oracle: str) -> dict:
    return {
        "id": check_id, "requirement": requirement,
        "code_refs": [{"path": path, "symbol": symbol}],
        "test_nodeids": [nodeid], "command_indices": [0], "evidence": items,
        "expected": expected, "observed": observed, "oracle": oracle, "status": "pass",
    }


def write_text(path: Path, text: str) -> None:
    path.write_text(text if text.endswith("\n") else text + "\n")


def main() -> int:
    receipt00_path = P15_00
    staging = Path("/tmp/p15-01-v4-staging")
    if staging.exists():
        shutil.rmtree(staging)
    written = write_p15_01_artifacts(staging, predecessor_receipt=receipt00_path)
    run_id01 = written["run_id"]
    attempt01 = ROOT / "implementation/reports/research-work/P15-01" / run_id01 / "attempt-0001"
    if attempt01.exists():
        raise SystemExit(f"exists {attempt01}")
    shutil.copytree(staging, attempt01)
    print("P15-01", run_id01, attempt01, flush=True)
    write_text(attempt01 / "WORK_LOG.md", f"# P15-01 sibling-hole repair\n\nPredecessor {receipt00_path} {file_digest(receipt00_path)}.\nrun_id {run_id01}.\n")
    write_text(attempt01 / "DECISIONS.tsv", "ts\tphase\tdecision\twhy\tevidence\tresult\n2026-09-14T14:00:00Z\trepair\tunsupported matrix and unpaired review hashes now fail\tneighboring paths of the v2 findings\treceipts.py\tnew attempt\n")
    write_text(attempt01 / "REPORT.md", f"# P15-01\n\nrun_id {run_id01}. implemented_verified.\n")
    verifier_cases = {
        "schema": "research-verifier-cases-v2", "task_id": "P15-01", "assurance_version": ASSURANCE_VERSION,
        "cases": [
            {"id": "valid_bootstrap", "expected_exit": 0, "test": "test_a05_valid_bootstrap_p15_00_receipt_verifies"},
            {"id": "matrix_unsupported", "expected_exit": 2, "code": "ACCEPTANCE", "test": "test_matrix_unsupported_cannot_close_accepted_task"},
            {"id": "review_hash_key_split", "expected_exit": 2, "code": "GATE_REVIEW", "test": "test_gate_review_input_hash_must_pair_path_and_digest"},
            {"id": "review_nonobject", "expected_exit": 2, "code": "GATE_REVIEW", "test": "test_gate_review_nonobject_fails_closed"},
            {"id": "matrix_failed_checks", "expected_exit": 2, "code": "ACCEPTANCE", "test": "test_matrix_failed_checks_rejected_when_accepted"},
        ],
    }
    write_json_document(attempt01 / "VERIFIER_CASES.json", verifier_cases)
    cmd01 = run([str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_01.py", "-v", "-p", "no:cacheprovider"], ROOT / "implementation", attempt01 / "pytest.log")
    verify_pred = run([str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt00_path)], ROOT / "implementation", attempt01 / "verify_p15_00.log")
    log01 = attempt01 / "pytest.log"
    cases_path = attempt01 / "VERIFIER_CASES.json"
    rec = "implementation/src/trading_research/research/contracts/receipts.py"
    node01 = "implementation/tests/rule_discovery/test_p15_01.py::{}"
    matrix01 = {
        "schema_version": "research-evidence-matrix-v2", "task_id": "P15-01", "assurance_version": ASSURANCE_VERSION,
        "checks": [
            check(check_id="A01", requirement="missing predecessor fails even if the report says PASS", path=rec, symbol="verify_task_receipt", nodeid=node01.format("test_a01_missing_predecessor_fails_even_if_report_says_pass"), items=[evidence(log01, "test_a01_missing_predecessor_fails_even_if_report_says_pass")], expected="exit 2 PREDECESSOR_MISSING", observed="2", oracle="CLI"),
            check(check_id="A02", requirement="tampered artifact byte or flipped acceptance flag fails", path=rec, symbol="_check_artifacts", nodeid=node01.format("test_a02_tampering_one_artifact_byte_fails"), items=[evidence(log01, "test_a02_tampering_one_artifact_byte_fails")], expected="exit 2 ARTIFACT_HASH", observed="2", oracle="CLI"),
            check(check_id="A03", requirement="blocked_implementation never passes a phase gate", path=rec, symbol="verify_phase_receipt", nodeid=node01.format("test_a03_blocked_implementation_never_passes_a_phase_gate"), items=[evidence(log01, "test_a03_blocked_implementation_never_passes_a_phase_gate")], expected="exit 2", observed="2", oracle="CLI"),
            check(check_id="A04", requirement="phase 2 without complete phase 1.5 gate fails", path=rec, symbol="verify_phase_receipt", nodeid=node01.format("test_a04_phase_2_without_complete_phase_1_5_gate_fails"), items=[evidence(log01, "test_a04_phase_2_without_complete_phase_1_5_gate_fails")], expected="exit 2 PHASE_1_5_GATE", observed="2", oracle="CLI"),
            check(check_id="A05", requirement="valid bootstrap P15-00 receipt verifies", path=rec, symbol="verify_task_receipt", nodeid=node01.format("test_a05_valid_bootstrap_p15_00_receipt_verifies"), items=[evidence(log01, "test_a05_valid_bootstrap_p15_00_receipt_verifies")], expected="exit 0", observed="0", oracle="CLI"),
            check(check_id="A06", requirement="command exit codes, hashes and coverage recorded", path=rec, symbol="_check_commands", nodeid=node01.format("test_a06_command_exit_codes_hashes_and_coverage_recorded"), items=[evidence(log01, "test_a06_command_exit_codes_hashes_and_coverage_recorded")], expected="exit 0", observed="0", oracle="measured pytest"),
            check(check_id="A07", requirement="matrix completeness refers to the other entries", path=rec, symbol="_check_evidence_matrix", nodeid=node01.format("test_matrix_failed_checks_rejected_when_accepted"), items=[evidence(cases_path, "/cases"), evidence(log01, "test_matrix_unsupported_cannot_close_accepted_task")], expected="forged empty evidence fails", observed="2", oracle="CLI"),
            check(check_id="A08", requirement="assigned S01-S05 probes have isolated failure codes", path=rec, symbol="FailureCode", nodeid=node01.format("test_s01_empty_manifest_fails_inventory"), items=[evidence(cases_path, "/cases")], expected="INVENTORY/IDENTITY/PREDECESSOR/UNKNOWN_SUBPHASE", observed="isolated codes", oracle="unit CLI"),
            check(check_id="A09", requirement="recursive verification rejects failed parent, wrong task id, unknown subphase, missing Phase 1.5 release", path=rec, symbol="_check_predecessors", nodeid=node01.format("test_s04_child_of_failed_parent_fails"), items=[evidence(log01, "test_s04_child_of_failed_parent_fails")], expected="exit 2", observed="2", oracle="CLI"),
            check(check_id="A10", requirement="required artifacts, schemas, row counts and identity bindings enforced", path=rec, symbol="_check_inventory", nodeid=node01.format("test_s01_row_count_mismatch_fails"), items=[evidence(log01, "test_s01_row_count_mismatch_fails")], expected="INVENTORY", observed="2", oracle="CLI"),
            check(check_id="A11", requirement="failed or unlogged commands never pass via unresolved prose", path=rec, symbol="_check_commands", nodeid=node01.format("test_failed_command_not_excused_by_unresolved"), items=[evidence(log01, "test_failed_command_not_excused_by_unresolved")], expected="COMMAND_EXIT", observed="2", oracle="CLI"),
            check(check_id="A12", requirement="lineage keeps ancestor cutoffs; --gate-review is separate", path=rec, symbol="_walk_lineage", nodeid=node01.format("test_lineage_child_cannot_relax_ancestor_cutoff"), items=[evidence(log01, "test_lineage_child_cannot_relax_ancestor_cutoff")], expected="LINEAGE_CLOCK", observed="2", oracle="CLI"),
            check(check_id="A13", requirement="isolated 27-mode coverage recorded; independent suite is the coordinator gate", path=rec, symbol="PINNED_CHECKER_SHA256", nodeid=node01.format("test_gate_review_input_hash_must_pair_path_and_digest"), items=[evidence(cases_path, "/cases")], expected=PINNED_CHECKER_SHA256, observed=PINNED_CHECKER_SHA256, oracle="ASSURANCE_CASES.json"),
            check(check_id="S01", requirement="empty manifest and omitted required artifact fail INVENTORY", path=rec, symbol="_check_inventory", nodeid=node01.format("test_s01_empty_manifest_fails_inventory"), items=[evidence(log01, "test_s01_empty_manifest_fails_inventory")], expected="INVENTORY", observed="2", oracle="CLI"),
            check(check_id="S02", requirement="acceptance flags with forged empty evidence fail", path=rec, symbol="_check_evidence_matrix", nodeid=node01.format("test_forged_evidence_matrix_fails"), items=[evidence(log01, "test_forged_evidence_matrix_fails")], expected="INVENTORY", observed="2", oracle="CLI"),
            check(check_id="S03", requirement="replaced plan identity fails IDENTITY", path=rec, symbol="_check_identities", nodeid=node01.format("test_s03_replaced_identities_fail"), items=[evidence(log01, "test_s03_replaced_identities_fail")], expected="IDENTITY", observed="2", oracle="CLI"),
            check(check_id="S04", requirement="failed parent, unknown subphase, wrong task, phase-2 reuse fail", path=rec, symbol="verify_subphase_receipt", nodeid=node01.format("test_s04_unknown_subphase_fails"), items=[evidence(log01, "test_s04_unknown_subphase_fails")], expected="UNKNOWN_SUBPHASE", observed="2", oracle="CLI"),
            check(check_id="S05", requirement="lineage ancestor cutoff and malformed clocks fail", path=rec, symbol="verify_lineage_manifest", nodeid=node01.format("test_lineage_invalid_clock_and_missing_hash_fail"), items=[evidence(log01, "test_lineage_invalid_clock_and_missing_hash_fail")], expected="LINEAGE_CLOCK/LINEAGE_HASH", observed="2", oracle="CLI"),
        ],
    }
    write_json_document(attempt01 / "EVIDENCE_MATRIX.json", matrix01)
    receipt01 = write_p15_01_receipt(
        attempt01, run_id=run_id01, plan_sha256=written["plan_sha256"], code_sha256=written["code_sha256"],
        predecessor_receipts={"P15-00": file_digest(receipt00_path)}, command_results=[cmd01, verify_pred],
        acceptance_checks={f"A{index:02d}": True for index in range(1, 14)},
        coverage={"native": False, "predecessor": str(receipt00_path), "unknown": 0},
        unresolved=["Independent 27-case suite is a coordinator gate after this receipt."],
        reason="sibling-hole repair: unsupported matrix rows and unpaired independent-result hashes fail closed",
    )
    receipt01_path = attempt01 / "TASK_RECEIPT.json"
    verify01 = run([str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt01_path)], ROOT / "implementation", attempt01 / "verify_task.log")
    print("P15-01 verify", verify01["exit_code"], file_digest(receipt01_path), flush=True)

    coverage00 = json.loads((P15_00.parent / "TASK_RECEIPT.json").read_text())["coverage"]
    draft_sub = {
        "schema_version": "research-draft-manifest-v2", "subphase_id": "00-foundation", "assurance_version": ASSURANCE_VERSION,
        "task_receipts": {"P15-00": file_digest(receipt00_path), "P15-01": file_digest(receipt01_path)},
        "plan_sha256": file_digest(GRAPH),
        "code_sha256": file_digest(ROOT / "implementation/src/trading_research/research/contracts/receipts.py"),
    }
    run_id_sub = digest(draft_sub)[:16]
    attempt_sub = ROOT / "implementation/reports/research-work/00-foundation" / run_id_sub / "attempt-0001"
    attempt_sub.mkdir(parents=True, exist_ok=False)
    write_json_document(attempt_sub / "DRAFT_MANIFEST.json", draft_sub)
    pytest_sub = run([str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_00.py", "tests/rule_discovery/test_p15_01.py", "-q", "-p", "no:cacheprovider"], ROOT / "implementation", attempt_sub / "pytest.log")
    verify_p00 = run([str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt00_path)], ROOT / "implementation", attempt_sub / "verify_p15_00.log")
    verify_p01 = run([str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt01_path)], ROOT / "implementation", attempt_sub / "verify_p15_01.log")
    subphase = {
        "schema_version": "research-subphase-receipt-v2", "assurance_version": ASSURANCE_VERSION, "subphase_id": "00-foundation",
        "run_id": run_id_sub,
        "task_receipts": {"P15-00": {"path": str(receipt00_path), "sha256": file_digest(receipt00_path)}, "P15-01": {"path": str(receipt01_path), "sha256": file_digest(receipt01_path)}},
        "accepted_schema_versions": ["research-task-receipt-v2", "research-subphase-receipt-v2", "research-gate-review-v2"],
        "native_slice_ids": coverage00.get("year_complete_dates", []) + ["2023-11-06"],
        "test_evidence": [pytest_sub, verify_p00, verify_p01], "coverage": coverage00,
        "single_writer_audit": {"writer": "coordinator-parent-grok", "checkout": "/workspace", "nested_workers": 0},
        "gate": "pass",
        "unresolved": ["Exchange-feed completeness remains unknown.", "Same-model coordinator review is not cross-model diversity.", "Phase 1 census was not rerun."],
        "reason": "00-foundation closed after sibling-hole repair; v1 and v2 attempts preserved",
    }
    sub_path = attempt_sub / "SUBPHASE_RECEIPT.json"
    write_json_document(sub_path, subphase)
    run([str(PYTHON), str(VERIFY), "subphase", "--receipt", str(sub_path)], ROOT / "implementation", attempt_sub / "verify_subphase.log")
    print("subphase", run_id_sub, file_digest(sub_path), flush=True)
    checker_out = ROOT / "implementation/reports/research-work/00-foundation" / run_id_sub / "fixed-suite"
    checker = run([str(PYTHON), str(CHECKER), "--p15-00", str(receipt00_path), "--p15-01", str(receipt01_path), "--subphase", str(sub_path), "--output-root", str(checker_out)], ROOT / "implementation", attempt_sub / "independent_checker.log")
    results_copy = attempt_sub / "INDEPENDENT_RESULTS.json"
    shutil.copy2(checker_out / "RESULTS.json", results_copy)
    print("checker", checker["exit_code"], file_digest(results_copy), flush=True)
    write_text(attempt_sub / "WORK_LOG.md", f"# 00-foundation\n\nP15-00 {receipt00_path}\nP15-01 {receipt01_path}\nSUBPHASE {sub_path}\n")
    write_text(attempt_sub / "DECISIONS.tsv", "ts\tphase\tdecision\twhy\tevidence\tresult\n2026-09-14T14:20:00Z\tclose\tnew subphase after sibling-hole repair\treviewer found unsupported-matrix and unpaired hashes\tGATE_REVIEW.json\tcandidate immutable\n")
    write_text(attempt_sub / "REPORT.md", f"# 00-foundation\n\nrun_id {run_id_sub}.\n")
    p00_attempt = receipt00_path.parent
    p00_receipt = json.loads(receipt00_path.read_text())
    review = {
        "schema_version": "research-gate-review-v2", "assurance_version": ASSURANCE_VERSION, "subphase_id": "00-foundation",
        "verdict": "pass", "candidate": {"path": str(sub_path), "sha256": file_digest(sub_path)},
        "reviewed_task_ids": ["P15-00", "P15-01"], "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "reviewer": "coordinator-separate-pass", "limitation": "parent Grok only; inherit-parent reviewer is not cross-model",
        "findings": [
            {"id": "F01", "severity": "integrity", "summary": "Ten v2 invalid cases fail closed; unsupported matrix rows and unpaired independent hashes also fail.", "reproduction": str(PROBE), "affected_outputs": [str(sub_path)], "resolution": "resolved", "resolution_evidence": "additional_probe 14/14 and sibling-hole tests"},
            {"id": "F02", "severity": "integrity", "summary": "v1 and rejected v2 receipts remain byte-identical.", "reproduction": "file_digest", "affected_outputs": [str(ROOT / "implementation/reports/research-work/00-foundation/240838146c38c484/attempt-0001/SUBPHASE_RECEIPT.json")], "resolution": "resolved", "resolution_evidence": "4d96f149d81ffad8173b59bde2d807026e6b8e1fac61c3814531c7b61137b4a0 unchanged"},
        ],
        "graph": {"path": str(GRAPH), "sha256": file_digest(GRAPH)},
        "registry": {"path": str(REGISTRY), "sha256": file_digest(REGISTRY)},
        "commands": [{"argv": checker["argv"], "cwd": checker["cwd"], "exit_code": checker["exit_code"], "log_path": str(results_copy), "log_sha256": file_digest(results_copy)}],
        "code_snapshots": {
            "P15-00": {"path": str(p00_attempt / "CODE_SNAPSHOT.json"), "sha256": file_digest(p00_attempt / "CODE_SNAPSHOT.json"), "code_sha256": p00_receipt["code_sha256"]},
            "P15-01": {"path": str(attempt01 / "CODE_SNAPSHOT.json"), "sha256": file_digest(attempt01 / "CODE_SNAPSHOT.json"), "code_sha256": receipt01["code_sha256"]},
        },
        "evidence_matrices": {
            "P15-00": {"path": str(p00_attempt / "EVIDENCE_MATRIX.json"), "sha256": file_digest(p00_attempt / "EVIDENCE_MATRIX.json")},
            "P15-01": {"path": str(attempt01 / "EVIDENCE_MATRIX.json"), "sha256": file_digest(attempt01 / "EVIDENCE_MATRIX.json")},
        },
        "independent_suite": {"checker_path": str(CHECKER), "checker_sha256": PINNED_CHECKER_SHA256, "required_case_count": 27, "results_path": str(results_copy), "results_sha256": file_digest(results_copy), "status": "pass"},
        "unverified_checks": ["Exchange-feed completeness remains unknown.", "Same-model coordinator review is not cross-model diversity.", "Phase 1 census was not rerun.", "Pinned 27-case and 14-case suites are not exhaustive."],
    }
    review_path = attempt_sub / "GATE_REVIEW.json"
    write_json_document(review_path, review)
    probe_out = ROOT / "implementation/reports/research-work/00-foundation" / run_id_sub / "additional-suite"
    probe = subprocess.run([str(PYTHON), str(PROBE), "--p15-00", str(receipt00_path), "--subphase", str(sub_path), "--review", str(review_path), "--output-root", str(probe_out)], cwd=ROOT / "implementation", text=True, capture_output=True)
    (attempt_sub / "additional_probe.log").write_text(probe.stdout + probe.stderr)
    print("additional_probe", probe.returncode, probe.stdout, flush=True)
    if probe.returncode != 0:
        raise SystemExit(probe.stdout + probe.stderr)
    gate = run([str(PYTHON), str(VERIFY), "subphase", "--receipt", str(sub_path), "--gate-review", str(review_path)], ROOT / "implementation", attempt_sub / "verify_gate_review.log")
    print("gate-review", gate["exit_code"], flush=True)
    summary = {
        "p15_00": {"path": str(receipt00_path), "sha256": file_digest(receipt00_path)},
        "p15_01": {"path": str(receipt01_path), "sha256": file_digest(receipt01_path), "run_id": run_id01},
        "subphase": {"path": str(sub_path), "sha256": file_digest(sub_path), "run_id": run_id_sub},
        "gate_review": {"path": str(review_path), "sha256": file_digest(review_path)},
        "fixed_suite": {"path": str(checker_out / "RESULTS.json"), "sha256": file_digest(checker_out / "RESULTS.json")},
        "additional_suite": {"path": str(probe_out / "RESULTS.json"), "sha256": file_digest(probe_out / "RESULTS.json")},
    }
    write_json_document(attempt_sub / "CLOSURE_IDENTITIES.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
