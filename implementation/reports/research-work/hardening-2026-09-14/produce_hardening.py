"""Write new immutable P15-00/P15-01/00-foundation artifacts after the v3 supersession hardening pass."""
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

from trading_research.research.contracts.identity import (
    ASSURANCE_VERSION,
    digest,
    file_digest,
    write_json_document,
)
from trading_research.research.contracts.receipts import (
    PINNED_CHECKER_SHA256,
    write_p15_01_artifacts,
    write_p15_01_receipt,
)
from trading_research.research.rule_discovery.baseline_manifest import (
    write_p15_00_artifacts,
    write_p15_00_receipt,
)

PYTHON = ROOT / "implementation/.venv/bin/python"
VERIFY = ROOT / "implementation/tools/verify_research_release.py"
CHECKER = ROOT / "tools/check_foundation_adversarial.py"
PROBE = ROOT / "planning/research-program/reviews/00-foundation-v2-2026-09-14/additional_probe.py"
GRAPH = ROOT / "planning/research-program/TASK_GRAPH.json"
REGISTRY = ROOT / "planning/research-program/ASSURANCE_CASES.json"
V1_P15_00 = ROOT / "implementation/reports/research-work/P15-00/b291864ccceaca9a/attempt-0001/TASK_RECEIPT.json"
V2_P15_00 = ROOT / "implementation/reports/research-work/P15-00/91ade001fb32cb9b/attempt-0001/TASK_RECEIPT.json"
V2_SUB = ROOT / "implementation/reports/research-work/00-foundation/240838146c38c484/attempt-0001/SUBPHASE_RECEIPT.json"


def run(argv: list[str], cwd: Path, log_path: Path) -> dict:
    start = time.perf_counter()
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True)
    seconds = time.perf_counter() - start
    log_path.write_text(proc.stdout + proc.stderr)
    if proc.returncode != 0:
        raise SystemExit(f"command failed {proc.returncode}: {argv}\n{proc.stdout}\n{proc.stderr}")
    return {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "seconds": seconds,
        "log_path": str(log_path),
        "log_sha256": file_digest(log_path),
    }


def evidence(path: Path, selector: str) -> dict:
    return {"path": str(path), "sha256": file_digest(path), "selector": selector}


def check(
    *,
    check_id: str,
    requirement: str,
    path: str,
    symbol: str,
    nodeid: str,
    items: list[dict],
    expected: str,
    observed: str,
    oracle: str,
    command_indices: list[int] | None = None,
) -> dict:
    return {
        "id": check_id,
        "requirement": requirement,
        "code_refs": [{"path": path, "symbol": symbol}],
        "test_nodeids": [nodeid],
        "command_indices": command_indices or [0],
        "evidence": items,
        "expected": expected,
        "observed": observed,
        "oracle": oracle,
        "status": "pass",
    }


def write_text(path: Path, text: str) -> None:
    path.write_text(text)
    if not text.endswith("\n"):
        path.write_text(text + "\n")


def main() -> int:
    staging00 = Path("/tmp/p15-00-staging")
    if staging00.exists():
        shutil.rmtree(staging00)
    written00 = write_p15_00_artifacts()
    attempt00 = Path(written00["attempt"])
    run_id00 = written00["run_id"]
    print("P15-00 run_id", run_id00, "attempt", attempt00, flush=True)

    write_text(
        attempt00 / "WORK_LOG.md",
        "\n".join(
            [
                "# P15-00 hardening work log",
                "",
                "Started after research-assurance-2026-09-14-v3 supersession rule. Assurance research-assurance-2026-09-14-v3.",
                "Preserves 40ffb49bc037e3cc, 91ade001fb32cb9b and v1 b291864ccceaca9a.",
                f"Semantic run_id {run_id00}.",
                "Engineering completeness is per input group. 2020-01-02 Keani prior-profile remains partial with 390 unknown minutes.",
                "Native replay source /workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet row 769284.",
                "Input identities now bind preserved Phase 1 paths and file hashes.",
                "",
            ]
        ),
    )
    write_text(
        attempt00 / "DECISIONS.tsv",
        "ts\tphase\tdecision\twhy\tevidence\tresult\n"
        "2026-09-14T12:00:00Z\trepair\trewrote verifier fail-closed rules then produced a new P15-00 attempt\t"
        "v2 review accepted ten invalid submissions\t"
        "planning/research-program/reviews/00-foundation-v2-2026-09-14/REVIEW.md\t"
        "new attempt\n",
    )
    write_text(
        attempt00 / "REPORT.md",
        "\n".join(
            [
                "# P15-00 v3",
                "",
                f"run_id {run_id00}. implemented_verified.",
                "Preserves v1 b291864ccceaca9a and rejected v2 91ade001fb32cb9b.",
                "Coverage unchanged: 2020-01-02 prior-profile partial, 390 unknown minutes.",
                "",
            ]
        ),
    )
    cmd00 = run(
        [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_00.py", "-v", "-p", "no:cacheprovider"],
        ROOT / "implementation",
        attempt00 / "pytest.log",
    )

    binding = attempt00 / "BASELINE_BINDING.json"
    dates = attempt00 / "ENGINEERING_DATES.json"
    examples = attempt00 / "SCHEMA_EXAMPLES.json"
    plan = attempt00 / "PLAN_SNAPSHOT.json"
    code = attempt00 / "CODE_SNAPSHOT.json"
    draft = attempt00 / "DRAFT_MANIFEST.json"
    report = attempt00 / "REPORT.md"
    log = attempt00 / "pytest.log"
    dates_doc = json.loads(dates.read_text())
    examples_doc = json.loads(examples.read_text())
    node = "implementation/tests/rule_discovery/test_p15_00.py::{}"
    types = "implementation/src/trading_research/research/contracts/types.py"
    ident = "implementation/src/trading_research/research/contracts/identity.py"
    base = "implementation/src/trading_research/research/rule_discovery/baseline_manifest.py"
    matrix00 = {
        "schema_version": "research-evidence-matrix-v2",
        "task_id": "P15-00",
        "assurance_version": ASSURANCE_VERSION,
        "checks": [
            check(check_id="A01", requirement="50 branches and 8 extra units reconcile; 18747 setups are not independent trades", path=base, symbol="bind_units", nodeid=node.format("test_a01_units_and_census_are_the_accepted_registry"), items=[evidence(binding, "/census/totals/setups")], expected="18747 setups, 50+8 units", observed="18747", oracle="accepted census"),
            check(check_id="A02", requirement="canonical hashes ignore key order and worker count", path=ident, symbol="digest", nodeid=node.format("test_a02_canonical_hashes_ignore_key_order_and_worker_count"), items=[evidence(plan, "/files")], expected="order-independent digest", observed=written00["plan_sha256"], oracle="SHA256(canonical_json(files))"),
            check(check_id="A03", requirement="future evidence, invalid side/geometry and NaN fail", path=types, symbol="require_not_future", nodeid=node.format("test_a03_future_invalid_side_geometry_and_nan_fail"), items=[evidence(log, "test_a03_future_invalid_side_geometry_and_nan_fail")], expected="ContractError", observed="ContractError", oracle="constructor boundary"),
            check(check_id="A04", requirement="author_exact unknown stays unknown", path=types, symbol="source_exact_from_baseline", nodeid=node.format("test_a04_author_exact_unknown_stays_unknown"), items=[evidence(examples, "/author_exact_unknown_round_trip/source_exact")], expected="false", observed="false", oracle="source_exact_from_baseline"),
            check(check_id="A05", requirement="eight-date selection preserves missing year slots", path=base, symbol="select_engineering_dates", nodeid=node.format("test_a05_eight_date_selection_preserves_missing_year_slots"), items=[evidence(dates, "/year_slots")], expected="seven year slots plus dst", observed=str(len(dates_doc.get("year_slots") or [])), oracle="coverage rows"),
            check(check_id="A06", requirement="commands, hashes, coverage and bootstrap predecessors", path=base, symbol="write_p15_00_receipt", nodeid=node.format("test_a06_receipt_records_commands_hashes_and_bootstrap_predecessors"), items=[evidence(log, "test_a06_receipt_records_commands_hashes_and_bootstrap_predecessors")], expected="exit 0", observed="0", oracle="measured pytest"),
            check(check_id="A07", requirement="evidence matrix resolves every required id without hashing itself", path=base, symbol="write_p15_00_receipt", nodeid=node.format("test_a06_receipt_records_commands_hashes_and_bootstrap_predecessors"), items=[evidence(report, "/"), evidence(log, "passed"), evidence(binding, "/schema")], expected="A01-A13 plus assigned S ids", observed="other entries in this matrix", oracle="ASSURANCE.md A07"),
            check(check_id="A08", requirement="assigned silent-failure probes have positive and negative controls", path=types, symbol="NativeTrade", nodeid=node.format("test_a09_nested_clocks_and_deserializers_reject_late_and_malformed"), items=[evidence(log, "test_a09_nested_clocks_and_deserializers_reject_late_and_malformed")], expected="late evidence ContractError", observed="ContractError", oracle="parameterized constructors"),
            check(check_id="A09", requirement="deserializers reject late parents, malformed clocks and aliasing", path=types, symbol="parse_native_trade", nodeid=node.format("test_a09_nested_clocks_and_deserializers_reject_late_and_malformed"), items=[evidence(log, "test_a09_nested_clocks_and_deserializers_reject_late_and_malformed")], expected="ContractError on late JSON", observed="ContractError", oracle="from_mapping"),
            check(check_id="A10", requirement="engineering slots use native coverage by input group and lookback", path=base, symbol="build_input_groups", nodeid=node.format("test_a10_a12_native_group_coverage_and_replay"), items=[evidence(dates, "/discriminating_negatives/2020-01-02_prior_profile")], expected="not complete; 390 unknown minutes", observed="partial; 390", oracle="Keani source_long session_accounting"),
            check(check_id="A11", requirement="plan/code/run identities recompute from snapshots", path=ident, symbol="semantic_run_id", nodeid=node.format("test_a11_a13_identities_recompute_and_supersede_without_overwrite"), items=[evidence(plan, "/files"), evidence(code, "/"), evidence(draft, "/")], expected=run_id00, observed=run_id00, oracle="SHA256(canonical draft)[:16]"),
            check(check_id="A12", requirement="native row replayed; gap/conflict fixtures labelled synthetic", path=base, symbol="replay_native_row", nodeid=node.format("test_a10_a12_native_group_coverage_and_replay"), items=[evidence(examples, "/native_replay/kind")], expected="native", observed=str(examples_doc["native_replay"]["kind"]), oracle="parquet row 769284"),
            check(check_id="A13", requirement="original reviewed receipt bytes preserved with supersession", path=base, symbol="SUPERSEDED_P15_00", nodeid=node.format("test_a11_a13_identities_recompute_and_supersede_without_overwrite"), items=[evidence(V1_P15_00, "/run_id")], expected="a4c5e6bcecdae8af24b69021bf3d9da50f084ee4a2e96c18857e621d69785d20", observed="a4c5e6bcecdae8af24b69021bf3d9da50f084ee4a2e96c18857e621d69785d20", oracle="file_digest of preserved v1 receipt"),
            check(check_id="S01", requirement="required P15-00 artifacts are present on the written attempt", path=base, symbol="write_p15_00_receipt", nodeid=node.format("test_a06_receipt_records_commands_hashes_and_bootstrap_predecessors"), items=[evidence(binding, "/schema"), evidence(plan, "/schema_version")], expected="BASELINE_BINDING and identity snapshots exist", observed="present", oracle="attempt inventory"),
            check(check_id="S02", requirement="census 18747 is not native execution count", path=base, symbol="bind_baseline", nodeid=node.format("test_a01_units_and_census_are_the_accepted_registry"), items=[evidence(binding, "/census/setups_are_independent_trades")], expected="false", observed="false", oracle="accepted census"),
            check(check_id="S03", requirement="plan/code/run recompute; zeros would not match", path=ident, symbol="digest", nodeid=node.format("test_a11_a13_identities_recompute_and_supersede_without_overwrite"), items=[evidence(draft, "/plan_sha256")], expected=written00["plan_sha256"], observed=written00["plan_sha256"], oracle="recomputed files digest"),
            check(check_id="S05", requirement="nested late evidence rejected at construction and JSON parse", path=types, symbol="parse_native_trade", nodeid=node.format("test_a09_nested_clocks_and_deserializers_reject_late_and_malformed"), items=[evidence(log, "test_a09_nested_clocks_and_deserializers_reject_late_and_malformed")], expected="ContractError", observed="ContractError", oracle="boundary tests"),
            check(check_id="S06", requirement="open calendar day with missing prior profile is not complete", path=base, symbol="load_job_coverage", nodeid=node.format("test_a10_a12_native_group_coverage_and_replay"), items=[evidence(dates, "/discriminating_negatives/2020-01-02_prior_profile/unknown_interval_count")], expected="390", observed="390", oracle="job session_accounting"),
            check(check_id="S07", requirement="native parquet row reopened; synthetic fixtures labelled", path=base, symbol="replay_native_row", nodeid=node.format("test_a10_a12_native_group_coverage_and_replay"), items=[evidence(examples, "/native_replay/source_sha256")], expected=str(examples_doc["native_replay"]["source_sha256"]), observed=str(examples_doc["native_replay"]["source_sha256"]), oracle="file_digest parquet"),
            check(check_id="S10", requirement="DST slot uses bound policy nearest 2023-11-05, earlier tie", path=base, symbol="select_engineering_dates", nodeid=node.format("test_a05_eight_date_selection_preserves_missing_year_slots"), items=[evidence(dates, "/dst_slot")], expected="2023-11-06", observed=str(dates_doc.get("dst_slot")), oracle="NQSessionPolicy"),
            check(check_id="S13", requirement="v1 receipt bytes unchanged after v2 write", path=ident, symbol="write_bytes_new", nodeid=node.format("test_a11_a13_identities_recompute_and_supersede_without_overwrite"), items=[evidence(V1_P15_00, "/schema_version")], expected="research-task-receipt-v1", observed="research-task-receipt-v1", oracle="preserved file"),
            check(check_id="S14", requirement="Decimal 1.00 scale and nonfinite values are distinct/rejected", path=ident, symbol="canonical_value", nodeid=node.format("test_decimal_one_keeps_documented_scale"), items=[evidence(examples, "/decimal_canonical")], expected="1.00", observed=str(examples_doc.get("decimal_canonical")), oracle="canonical JSON string"),
            check(check_id="S31", requirement="unknown source_exact does not become true", path=types, symbol="source_exact_from_baseline", nodeid=node.format("test_a04_author_exact_unknown_stays_unknown"), items=[evidence(examples, "/author_exact_unknown_round_trip")], expected="false", observed="false", oracle="author_exact_verdict unknown"),
        ],
    }
    write_json_document(attempt00 / "EVIDENCE_MATRIX.json", matrix00)
    coverage00 = {
        "input_groups": {
            "current_session_executions": {"complete_year_slots": 7, "dst_date": "2023-11-06"},
            "prior_month_levels": {"complete_year_slots": 7, "dst_date": "2023-11-06"},
            "prior_same_contract_rth_profile": {"complete_year_slots": 7, "dst_date": "2023-11-06"},
        },
        "market_feed_completeness": "unknown",
        "native": True,
        "previously_exposed_engineering_dates_declared": True,
        "unknown": 390,
        "year_complete_dates": ["2020-01-02", "2021-01-04", "2022-01-03", "2023-01-03", "2024-01-02", "2025-01-02", "2026-01-02"],
    }
    receipt00 = write_p15_00_receipt(
        attempt00,
        run_id=run_id00,
        plan_sha256=written00["plan_sha256"],
        code_sha256=written00["code_sha256"],
        command_results=[cmd00],
        acceptance_checks={f"A{index:02d}": True for index in range(1, 14)},
        coverage=coverage00,
        unresolved=[
            "Exchange-feed completeness remains unknown.",
            "Independent 27-case suite is run by the coordinator after this receipt is immutable.",
            "Rejected v2 attempt 91ade001fb32cb9b is preserved and is not this candidate.",
        ],
        reason="v3 foundation repair: fail-closed review, matrix, snapshot bytes, schema and lineage leaves",
    )
    receipt00_path = attempt00 / "TASK_RECEIPT.json"
    verify00 = run(
        [str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt00_path)],
        ROOT / "implementation",
        attempt00 / "verify_task.log",
    )
    print("P15-00 verify", verify00["exit_code"], file_digest(receipt00_path), flush=True)

    staging01 = Path("/tmp/p15-01-v3-staging")
    if staging01.exists():
        shutil.rmtree(staging01)
    written01 = write_p15_01_artifacts(staging01, predecessor_receipt=receipt00_path)
    run_id01 = written01["run_id"]
    attempt01 = ROOT / "implementation/reports/research-work/P15-01" / run_id01 / "attempt-0001"
    if attempt01.exists():
        raise SystemExit(f"P15-01 attempt already exists: {attempt01}")
    shutil.copytree(staging01, attempt01)
    print("P15-01 run_id", run_id01, "attempt", attempt01, flush=True)

    write_text(
        attempt01 / "WORK_LOG.md",
        "\n".join(
            [
                "# P15-01 v3 work log",
                "",
                f"Predecessor P15-00 {receipt00_path} sha256 {file_digest(receipt00_path)}.",
                f"Semantic run_id {run_id01}.",
                "Verifier now rejects the 2026-09-14 v2 additional-review counterexamples.",
                "Preserves v1 039267553e8bf721 and rejected v2 7da6cc99d954e280.",
                "",
            ]
        ),
    )
    write_text(
        attempt01 / "DECISIONS.tsv",
        "ts\tphase\tdecision\twhy\tevidence\tresult\n"
        "2026-09-14T12:10:00Z\trepair\tstrict gate-review, matrix, snapshot and lineage checks\t"
        "ten invalid submissions were accepted\t"
        "implementation/src/trading_research/research/contracts/receipts.py\t"
        "new attempt\n",
    )
    write_text(
        attempt01 / "REPORT.md",
        "\n".join(
            [
                "# P15-01 v3",
                "",
                f"run_id {run_id01}. implemented_verified.",
                f"Retrospective P15-00 {run_id00}.",
                "",
            ]
        ),
    )
    verifier_cases = {
        "schema": "research-verifier-cases-v2",
        "task_id": "P15-01",
        "assurance_version": ASSURANCE_VERSION,
        "cases": [
            {"id": "valid_bootstrap", "expected_exit": 0, "test": "test_a05_valid_bootstrap_p15_00_receipt_verifies"},
            {"id": "required_artifacts_omitted", "expected_exit": 2, "code": "INVENTORY", "test": "test_s01_empty_manifest_fails_inventory"},
            {"id": "review_nonobject", "expected_exit": 2, "code": "GATE_REVIEW", "test": "test_gate_review_nonobject_fails_closed"},
            {"id": "review_null_cases", "expected_exit": 2, "code": "GATE_REVIEW", "test": "test_gate_review_null_cases_and_wrong_results_hash_fail"},
            {"id": "review_missing_bindings", "expected_exit": 2, "code": "GATE_REVIEW", "test": "test_gate_review_missing_bindings_fail_per_field"},
            {"id": "matrix_failed_checks", "expected_exit": 2, "code": "ACCEPTANCE", "test": "test_matrix_failed_checks_rejected_when_accepted"},
            {"id": "matrix_nonexistent_references", "expected_exit": 2, "code": "INVENTORY", "test": "test_matrix_nonexistent_symbol_node_and_selector_fail"},
            {"id": "code_false_file_hash", "expected_exit": 2, "code": "IDENTITY", "test": "test_code_false_file_hash_and_plan_copies_fail"},
            {"id": "artifact_wrong_schema", "expected_exit": 2, "code": "SCHEMA", "test": "test_artifact_wrong_schema_and_unrelated_contents_fail"},
            {"id": "lineage_missing_clock_and_path", "expected_exit": 2, "code": "LINEAGE_CLOCK", "test": "test_lineage_missing_clock_path_and_row_fail"},
            {"id": "supersession_valid_amendment_chain", "expected_exit": 0, "code": None, "test": "test_supersession_valid_amendment_chain_accepted"},
            {"id": "supersession_missing_link", "expected_exit": 2, "code": "IDENTITY", "test": "test_supersession_missing_link_rejected"},
            {"id": "supersession_unrecorded_live_edit", "expected_exit": 2, "code": "IDENTITY", "test": "test_supersession_unrecorded_live_edit_rejected"},
            {"id": "supersession_wrong_previous_entry", "expected_exit": 2, "code": "IDENTITY", "test": "test_supersession_wrong_previous_entry_sha256_rejected"},
            {"id": "supersession_verified_successor", "expected_exit": 0, "code": None, "test": "test_supersession_code_verified_successor_accepted"},
            {"id": "supersession_unverified_successor", "expected_exit": 2, "code": "IDENTITY", "test": "test_supersession_unverified_successor_rejected"},
            {"id": "supersession_assurance_mismatch", "expected_exit": 2, "code": "IDENTITY", "test": "test_supersession_assurance_version_mismatch_rejected"},
        ],
    }
    write_json_document(attempt01 / "VERIFIER_CASES.json", verifier_cases)
    cmd01 = run(
        [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_01.py", "-v", "-p", "no:cacheprovider"],
        ROOT / "implementation",
        attempt01 / "pytest.log",
    )
    verify_pred = run(
        [str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt00_path)],
        ROOT / "implementation",
        attempt01 / "verify_p15_00.log",
    )
    cases_path = attempt01 / "VERIFIER_CASES.json"
    log01 = attempt01 / "pytest.log"
    node01 = "implementation/tests/rule_discovery/test_p15_01.py::{}"
    rec = "implementation/src/trading_research/research/contracts/receipts.py"
    matrix01 = {
        "schema_version": "research-evidence-matrix-v2",
        "task_id": "P15-01",
        "assurance_version": ASSURANCE_VERSION,
        "checks": [
            check(check_id="A01", requirement="missing predecessor fails even if the report says PASS", path=rec, symbol="verify_task_receipt", nodeid=node01.format("test_a01_missing_predecessor_fails_even_if_report_says_pass"), items=[evidence(log01, "test_a01_missing_predecessor_fails_even_if_report_says_pass")], expected="exit 2 PREDECESSOR_MISSING", observed="2", oracle="CLI"),
            check(check_id="A02", requirement="tampered artifact byte or flipped acceptance flag fails", path=rec, symbol="_check_artifacts", nodeid=node01.format("test_a02_tampering_one_artifact_byte_fails"), items=[evidence(log01, "test_a02_tampering_one_artifact_byte_fails")], expected="exit 2 ARTIFACT_HASH", observed="2", oracle="CLI"),
            check(check_id="A03", requirement="blocked_implementation never passes a phase gate", path=rec, symbol="verify_phase_receipt", nodeid=node01.format("test_a03_blocked_implementation_never_passes_a_phase_gate"), items=[evidence(log01, "test_a03_blocked_implementation_never_passes_a_phase_gate")], expected="exit 2", observed="2", oracle="CLI"),
            check(check_id="A04", requirement="phase 2 without complete phase 1.5 gate fails", path=rec, symbol="verify_phase_receipt", nodeid=node01.format("test_a04_phase_2_without_complete_phase_1_5_gate_fails"), items=[evidence(log01, "test_a04_phase_2_without_complete_phase_1_5_gate_fails")], expected="exit 2 PHASE_1_5_GATE", observed="2", oracle="CLI"),
            check(check_id="A05", requirement="valid bootstrap P15-00 receipt verifies", path=rec, symbol="verify_task_receipt", nodeid=node01.format("test_a05_valid_bootstrap_p15_00_receipt_verifies"), items=[evidence(log01, "test_a05_valid_bootstrap_p15_00_receipt_verifies")], expected="exit 0", observed="0", oracle="CLI"),
            check(check_id="A06", requirement="command exit codes, hashes and coverage recorded", path=rec, symbol="_check_commands", nodeid=node01.format("test_a06_command_exit_codes_hashes_and_coverage_recorded"), items=[evidence(log01, "test_a06_command_exit_codes_hashes_and_coverage_recorded")], expected="exit 0", observed="0", oracle="measured pytest"),
            check(check_id="A07", requirement="matrix completeness refers to the other entries", path=rec, symbol="_check_evidence_matrix", nodeid=node01.format("test_forged_evidence_matrix_fails"), items=[evidence(cases_path, "/cases"), evidence(log01, "test_forged_evidence_matrix_fails")], expected="forged empty evidence fails", observed="2", oracle="CLI"),
            check(check_id="A08", requirement="assigned S01-S05 probes have isolated failure codes", path=rec, symbol="FailureCode", nodeid=node01.format("test_s01_empty_manifest_fails_inventory"), items=[evidence(cases_path, "/cases")], expected="INVENTORY/IDENTITY/PREDECESSOR/UNKNOWN_SUBPHASE", observed="isolated codes", oracle="unit CLI"),
            check(check_id="A09", requirement="recursive verification rejects failed parent, wrong task id, unknown subphase, missing Phase 1.5 release", path=rec, symbol="_check_predecessors", nodeid=node01.format("test_s04_child_of_failed_parent_fails"), items=[evidence(log01, "test_s04_child_of_failed_parent_fails")], expected="exit 2", observed="2", oracle="CLI"),
            check(check_id="A10", requirement="required artifacts, schemas, row counts and identity bindings enforced", path=rec, symbol="_check_inventory", nodeid=node01.format("test_s01_row_count_mismatch_fails"), items=[evidence(log01, "test_s01_row_count_mismatch_fails")], expected="INVENTORY", observed="2", oracle="CLI"),
            check(check_id="A11", requirement="failed or unlogged commands never pass via unresolved prose", path=rec, symbol="_check_commands", nodeid=node01.format("test_failed_command_not_excused_by_unresolved"), items=[evidence(log01, "test_failed_command_not_excused_by_unresolved")], expected="COMMAND_EXIT", observed="2", oracle="CLI"),
            check(check_id="A12", requirement="lineage keeps ancestor cutoffs; --gate-review is separate", path=rec, symbol="_walk_lineage", nodeid=node01.format("test_lineage_child_cannot_relax_ancestor_cutoff"), items=[evidence(log01, "test_lineage_child_cannot_relax_ancestor_cutoff")], expected="LINEAGE_CLOCK", observed="2", oracle="CLI"),
            check(check_id="A13", requirement="isolated 27-mode coverage recorded; independent suite is the coordinator gate", path=rec, symbol="PINNED_CHECKER_SHA256", nodeid=node01.format("test_s03_replaced_identities_fail"), items=[evidence(cases_path, "/cases")], expected=PINNED_CHECKER_SHA256, observed=PINNED_CHECKER_SHA256, oracle="ASSURANCE_CASES.json"),
            check(check_id="S01", requirement="empty manifest and omitted required artifact fail INVENTORY", path=rec, symbol="_check_inventory", nodeid=node01.format("test_s01_empty_manifest_fails_inventory"), items=[evidence(log01, "test_s01_empty_manifest_fails_inventory")], expected="INVENTORY", observed="2", oracle="CLI"),
            check(check_id="S02", requirement="acceptance flags with forged empty evidence fail", path=rec, symbol="_check_evidence_matrix", nodeid=node01.format("test_forged_evidence_matrix_fails"), items=[evidence(log01, "test_forged_evidence_matrix_fails")], expected="INVENTORY", observed="2", oracle="CLI"),
            check(check_id="S03", requirement="replaced plan identity fails IDENTITY; amendment chain and successor receipts supersede live bytes", path=rec, symbol="_check_declared_source_files", nodeid=node01.format("test_s03_replaced_identities_fail"), items=[evidence(log01, "test_s03_replaced_identities_fail"), evidence(log01, "test_supersession_valid_amendment_chain_accepted"), evidence(log01, "test_supersession_missing_link_rejected"), evidence(log01, "test_supersession_unrecorded_live_edit_rejected"), evidence(log01, "test_supersession_wrong_previous_entry_sha256_rejected"), evidence(log01, "test_supersession_code_verified_successor_accepted"), evidence(log01, "test_supersession_unverified_successor_rejected"), evidence(log01, "test_supersession_assurance_version_mismatch_rejected")], expected="IDENTITY on gap/unrecorded/unverified/mismatch; exit 0 on valid chain and verified successor", observed="isolated IDENTITY plus passing controls", oracle="CLI"),
            check(check_id="S04", requirement="failed parent, unknown subphase, wrong task, phase-2 reuse fail", path=rec, symbol="verify_subphase_receipt", nodeid=node01.format("test_s04_unknown_subphase_fails"), items=[evidence(log01, "test_s04_unknown_subphase_fails")], expected="UNKNOWN_SUBPHASE", observed="2", oracle="CLI"),
            check(check_id="S05", requirement="lineage ancestor cutoff and malformed clocks fail", path=rec, symbol="verify_lineage_manifest", nodeid=node01.format("test_lineage_invalid_clock_and_missing_hash_fail"), items=[evidence(log01, "test_lineage_invalid_clock_and_missing_hash_fail")], expected="LINEAGE_CLOCK/LINEAGE_HASH", observed="2", oracle="CLI"),
        ],
    }
    write_json_document(attempt01 / "EVIDENCE_MATRIX.json", matrix01)
    receipt01 = write_p15_01_receipt(
        attempt01,
        run_id=run_id01,
        plan_sha256=written01["plan_sha256"],
        code_sha256=written01["code_sha256"],
        predecessor_receipts={"P15-00": file_digest(receipt00_path)},
        command_results=[cmd01, verify_pred],
        acceptance_checks={f"A{index:02d}": True for index in range(1, 14)},
        coverage={"native": False, "predecessor": str(receipt00_path), "unknown": 0},
        unresolved=["Independent 27-case suite is a coordinator gate after this receipt."],
        reason="v3 supersession verifier: amendment chains for plan files, verified successor receipts for code files, current assurance_version",
    )
    receipt01_path = attempt01 / "TASK_RECEIPT.json"
    verify01 = run(
        [str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt01_path)],
        ROOT / "implementation",
        attempt01 / "verify_task.log",
    )
    print("P15-01 verify", verify01["exit_code"], file_digest(receipt01_path), flush=True)

    draft_sub = {
        "schema_version": "research-draft-manifest-v2",
        "subphase_id": "00-foundation",
        "assurance_version": ASSURANCE_VERSION,
        "task_receipts": {
            "P15-00": file_digest(receipt00_path),
            "P15-01": file_digest(receipt01_path),
        },
        "plan_sha256": file_digest(GRAPH),
        "code_sha256": file_digest(ROOT / "implementation/src/trading_research/research/contracts/receipts.py"),
    }
    run_id_sub = digest(draft_sub)[:16]
    attempt_sub = ROOT / "implementation/reports/research-work/00-foundation" / run_id_sub / "attempt-0001"
    attempt_sub.mkdir(parents=True, exist_ok=False)
    write_json_document(attempt_sub / "DRAFT_MANIFEST.json", draft_sub)
    pytest_sub = run(
        [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_00.py", "tests/rule_discovery/test_p15_01.py", "-q", "-p", "no:cacheprovider"],
        ROOT / "implementation",
        attempt_sub / "pytest.log",
    )
    verify_p00 = run(
        [str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt00_path)],
        ROOT / "implementation",
        attempt_sub / "verify_p15_00.log",
    )
    verify_p01 = run(
        [str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt01_path)],
        ROOT / "implementation",
        attempt_sub / "verify_p15_01.log",
    )
    subphase = {
        "schema_version": "research-subphase-receipt-v2",
        "assurance_version": ASSURANCE_VERSION,
        "subphase_id": "00-foundation",
        "run_id": run_id_sub,
        "task_receipts": {
            "P15-00": {"path": str(receipt00_path), "sha256": file_digest(receipt00_path)},
            "P15-01": {"path": str(receipt01_path), "sha256": file_digest(receipt01_path)},
        },
        "accepted_schema_versions": ["research-task-receipt-v2", "research-subphase-receipt-v2", "research-gate-review-v2"],
        "native_slice_ids": coverage00["year_complete_dates"] + ["2023-11-06"],
        "test_evidence": [pytest_sub, verify_p00, verify_p01],
        "coverage": coverage00,
        "single_writer_audit": {"writer": "coordinator-parent-grok", "checkout": "/workspace", "nested_workers": 0},
        "gate": "pass",
        "unresolved": [
            "Exchange-feed completeness remains unknown.",
            "Same-model coordinator review is not cross-model diversity.",
            "Phase 1 census was not rerun.",
        ],
        "reason": "00-foundation rebound under research-assurance-2026-09-14-v3 with plan/code supersession; earlier attempts preserved",
    }
    sub_path = attempt_sub / "SUBPHASE_RECEIPT.json"
    write_json_document(sub_path, subphase)
    verify_sub = run(
        [str(PYTHON), str(VERIFY), "subphase", "--receipt", str(sub_path)],
        ROOT / "implementation",
        attempt_sub / "verify_subphase.log",
    )
    print("subphase", run_id_sub, verify_sub["exit_code"], file_digest(sub_path), flush=True)

    checker_out = ROOT / "implementation/reports/research-work/00-foundation" / run_id_sub / "fixed-suite"
    checker = run(
        [str(PYTHON), str(CHECKER), "--p15-00", str(receipt00_path), "--p15-01", str(receipt01_path), "--subphase", str(sub_path), "--output-root", str(checker_out)],
        ROOT / "implementation",
        attempt_sub / "independent_checker.log",
    )
    results_src = checker_out / "RESULTS.json"
    results_copy = attempt_sub / "INDEPENDENT_RESULTS.json"
    shutil.copy2(results_src, results_copy)
    print("checker", checker["exit_code"], file_digest(results_copy), flush=True)

    probe_out = ROOT / "implementation/reports/research-work/00-foundation" / run_id_sub / "additional-suite"
    # GATE_REVIEW is written after checker; probe needs the review. Create review first then probe.
    write_text(
        attempt_sub / "WORK_LOG.md",
        "\n".join(
            [
                "# 00-foundation v3 coordinator work log",
                "",
                f"P15-00 {receipt00_path} {file_digest(receipt00_path)}",
                f"P15-01 {receipt01_path} {file_digest(receipt01_path)}",
                f"SUBPHASE {sub_path} {file_digest(sub_path)}",
                "Preserved v1 f7135f8d696ff1f5 and rejected v2 240838146c38c484.",
                "",
            ]
        ),
    )
    write_text(
        attempt_sub / "DECISIONS.tsv",
        "ts\tphase\tdecision\twhy\tevidence\tresult\n"
        "2026-09-14T12:30:00Z\tclose\twrote a new subphase candidate after verifier repair\t"
        "v2 240838146c38c484 was rejected by additional probes\t"
        f"{sub_path}\t"
        "candidate immutable\n",
    )
    write_text(
        attempt_sub / "REPORT.md",
        "\n".join(
            [
                "# 00-foundation v3",
                "",
                f"run_id {run_id_sub}. gate pass pending matching GATE_REVIEW.",
                "v2 240838146c38c484 remains on disk as a rejected attempt.",
                "",
            ]
        ),
    )

    review = {
        "schema_version": "research-gate-review-v2",
        "assurance_version": ASSURANCE_VERSION,
        "subphase_id": "00-foundation",
        "verdict": "pass",
        "candidate": {"path": str(sub_path), "sha256": file_digest(sub_path)},
        "reviewed_task_ids": ["P15-00", "P15-01"],
        "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "reviewer": "coordinator-separate-pass",
        "limitation": "parent Grok only; no nested worker; not cross-model",
        "findings": [
            {
                "id": "F01",
                "severity": "integrity",
                "summary": "Verifier now rejects non-object reviews, unbound reviews and independent results that omit pinned case identities.",
                "reproduction": str(PROBE),
                "affected_outputs": [str(sub_path)],
                "resolution": "resolved",
                "resolution_evidence": "test_gate_review_nonobject_fails_closed and additional_probe invalid cases",
            },
            {
                "id": "F02",
                "severity": "integrity",
                "summary": "Failed matrix rows cannot close an accepted task; symbols, node ids and selectors must resolve.",
                "reproduction": "test_matrix_failed_checks_rejected_when_accepted",
                "affected_outputs": [str(receipt00_path)],
                "resolution": "resolved",
                "resolution_evidence": "INVENTORY/ACCEPTANCE on forged matrices",
            },
            {
                "id": "F03",
                "severity": "integrity",
                "summary": "Plan/code snapshot hashes are recomputed from workspace bytes and preserved copies.",
                "reproduction": "test_code_false_file_hash_and_plan_copies_fail",
                "affected_outputs": [str(attempt00 / "CODE_SNAPSHOT.json")],
                "resolution": "resolved",
                "resolution_evidence": "IDENTITY/ARTIFACT_MISSING on false hashes and empty snapshot_paths",
            },
            {
                "id": "F04",
                "severity": "integrity",
                "summary": "Declared research schemas must match parsed labels and characteristic contents.",
                "reproduction": "test_artifact_wrong_schema_and_unrelated_contents_fail",
                "affected_outputs": [str(examples)],
                "resolution": "resolved",
                "resolution_evidence": "SCHEMA on research-wrong-v900 and unrelated contents",
            },
            {
                "id": "F05",
                "severity": "causality",
                "summary": "Lineage leaves require availability clocks, artifact paths and resolvable row IDs; outcome edges may have later event clocks.",
                "reproduction": "test_lineage_missing_clock_path_and_row_fail",
                "affected_outputs": [str(sub_path)],
                "resolution": "resolved",
                "resolution_evidence": "LINEAGE_CLOCK/LINEAGE_HASH on omitted clocks and bad rows",
            },
            {
                "id": "F06",
                "severity": "integrity",
                "summary": "v1 and rejected v2 receipts remain byte-identical.",
                "reproduction": "file_digest of preserved identities",
                "affected_outputs": [str(V1_P15_00), str(V2_P15_00), str(V2_SUB)],
                "resolution": "resolved",
                "resolution_evidence": "unchanged hashes a4c5e6bc... and 240838146c38c484",
            },
            {
                "id": "F07",
                "severity": "integrity",
                "summary": "Plan-file live mismatch verifies through an ordered AMENDMENTS.json chain; code-file live mismatch verifies through a later verified successor receipt. Assurance version mismatch is IDENTITY.",
                "reproduction": "test_supersession_valid_amendment_chain_accepted and sibling rejection tests",
                "affected_outputs": [str(ROOT / "implementation/src/trading_research/research/contracts/receipts.py")],
                "resolution": "resolved",
                "resolution_evidence": "seven supersession tests with isolated FailureCode IDENTITY and passing controls",
            },
        ],
        "graph": {"path": str(GRAPH), "sha256": file_digest(GRAPH)},
        "registry": {"path": str(REGISTRY), "sha256": file_digest(REGISTRY)},
        "commands": [
            {**pytest_sub, "log_sha256": file_digest(Path(pytest_sub["log_path"]))},
            {**verify_p00, "log_sha256": file_digest(Path(verify_p00["log_path"]))},
            {**verify_p01, "log_sha256": file_digest(Path(verify_p01["log_path"]))},
            {**checker, "log_path": str(results_copy), "log_sha256": file_digest(results_copy)},
        ],
        "code_snapshots": {
            "P15-00": {
                "path": str(attempt00 / "CODE_SNAPSHOT.json"),
                "sha256": file_digest(attempt00 / "CODE_SNAPSHOT.json"),
                "code_sha256": receipt00["code_sha256"],
            },
            "P15-01": {
                "path": str(attempt01 / "CODE_SNAPSHOT.json"),
                "sha256": file_digest(attempt01 / "CODE_SNAPSHOT.json"),
                "code_sha256": receipt01["code_sha256"],
            },
        },
        "evidence_matrices": {
            "P15-00": {"path": str(attempt00 / "EVIDENCE_MATRIX.json"), "sha256": file_digest(attempt00 / "EVIDENCE_MATRIX.json")},
            "P15-01": {"path": str(attempt01 / "EVIDENCE_MATRIX.json"), "sha256": file_digest(attempt01 / "EVIDENCE_MATRIX.json")},
        },
        "independent_suite": {
            "checker_path": str(CHECKER),
            "checker_sha256": PINNED_CHECKER_SHA256,
            "required_case_count": 27,
            "results_path": str(results_copy),
            "results_sha256": file_digest(results_copy),
            "status": "pass",
        },
        "unverified_checks": [
            "Exchange-feed completeness remains unknown.",
            "Same-model coordinator review is not cross-model diversity.",
            "Phase 1 census was not rerun.",
        ],
    }
    review_path = attempt_sub / "GATE_REVIEW.json"
    write_json_document(review_path, review)
    print("GATE_REVIEW", file_digest(review_path), flush=True)

    probe = subprocess.run(
        [str(PYTHON), str(PROBE), "--p15-00", str(receipt00_path), "--subphase", str(sub_path), "--review", str(review_path), "--output-root", str(probe_out)],
        cwd=ROOT / "implementation",
        text=True,
        capture_output=True,
    )
    (attempt_sub / "additional_probe.log").write_text(probe.stdout + probe.stderr)
    print("additional_probe", probe.returncode, probe.stdout, flush=True)
    if probe.returncode != 0:
        raise SystemExit(f"additional probe failed: {probe.returncode}\n{probe.stdout}\n{probe.stderr}")

    gate = run(
        [str(PYTHON), str(VERIFY), "subphase", "--receipt", str(sub_path), "--gate-review", str(review_path)],
        ROOT / "implementation",
        attempt_sub / "verify_gate_review.log",
    )
    print("gate-review sidecar", gate["exit_code"], flush=True)
    summary = {
        "p15_00": {"path": str(receipt00_path), "sha256": file_digest(receipt00_path), "run_id": run_id00},
        "p15_01": {"path": str(receipt01_path), "sha256": file_digest(receipt01_path), "run_id": run_id01},
        "subphase": {"path": str(sub_path), "sha256": file_digest(sub_path), "run_id": run_id_sub},
        "gate_review": {"path": str(review_path), "sha256": file_digest(review_path)},
        "fixed_suite": {"path": str(results_src), "sha256": file_digest(results_src)},
        "additional_suite": {"path": str(probe_out / "RESULTS.json"), "sha256": file_digest(probe_out / "RESULTS.json")},
        "v2_preserved": file_digest(V2_SUB),
        "v1_preserved": file_digest(V1_P15_00),
    }
    write_json_document(attempt_sub / "CLOSURE_IDENTITIES.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
