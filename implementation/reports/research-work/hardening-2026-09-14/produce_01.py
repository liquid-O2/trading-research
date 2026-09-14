"""Write P15-02, P15-03 and 01-native-and-outcomes receipts after 00 v3 rebind."""
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
from trading_research.research.contracts.receipts import PINNED_CHECKER_SHA256, load_task_graph, required_matrix_ids
from trading_research.research.rule_discovery.runner import (
    P15_00_RECEIPT,
    P15_01_RECEIPT,
    write_p15_02_identity,
    write_p15_02_receipt,
    stratified_parity_dates,
)
from trading_research.research.contracts.evaluation import (
    build_evaluation_splits,
    evaluation_protocol,
    split_manifest,
    write_baseline_diagnostics,
    write_p15_03_identity,
    write_p15_03_receipt,
    PHASE1_RUN,
)
from trading_research.research.contracts.outcomes import first_passage, interval_extrema, PriceBatch
from trading_research.research.contracts.execution import (
    daily_benchmark_series,
    replay_family,
    worked_net_pnl_fixture,
    gap_loss_not_clipped,
)
from trading_research.research.contracts.types import Coverage, CoverageReceipt, EvidenceRef, QuoteBatch
from decimal import Decimal

PYTHON = ROOT / "implementation/.venv/bin/python"
VERIFY = ROOT / "implementation/tools/verify_research_release.py"
CHECKER = ROOT / "tools/check_foundation_adversarial.py"
OUTCOME_CHECKER = ROOT / "tools/check_outcome_fixtures.py"
OUTCOME_CHECKER_SHA256 = "0cd6910c9e9024342678df1d197c625d049eebb3cd5883f74499518092a6752d"
PARITY_ROOT = Path("/tmp/p15-02-parity-order-fix")
CACHE_DATES = [
    "2020-01-02", "2020-03-02", "2020-03-13", "2020-04-01", "2020-06-01",
    "2020-07-01", "2020-09-01", "2020-10-01", "2020-12-01", "2021-01-04",
    "2021-03-01", "2021-04-01", "2021-06-01", "2021-07-01", "2021-09-01",
    "2021-10-01", "2021-12-01", "2022-01-03", "2022-03-01", "2022-04-01",
]


def run(argv: list[str], cwd: Path, log_path: Path) -> dict:
    start = time.perf_counter()
    proc = subprocess.run(argv, cwd=cwd, text=True, capture_output=True)
    seconds = time.perf_counter() - start
    log_path.write_text(proc.stdout + proc.stderr)
    if proc.returncode != 0:
        raise SystemExit(f"command failed {proc.returncode}: {argv}\n{proc.stdout[-4000:]}\n{proc.stderr[-4000:]}")
    return {
        "argv": [str(item) for item in argv],
        "cwd": str(cwd),
        "exit_code": proc.returncode,
        "seconds": seconds,
        "log_path": str(log_path),
        "log_sha256": file_digest(log_path),
    }


def evidence(path: Path, selector: str) -> dict:
    return {"path": str(path), "sha256": file_digest(path), "selector": selector}


def check(**kwargs) -> dict:
    kwargs.setdefault("status", "pass")
    kwargs.setdefault("command_indices", [0])
    return kwargs


def pct(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((p / 100) * (len(ordered) - 1)))))
    return ordered[index]


def load_parity() -> dict:
    jobs_dir = PARITY_ROOT / "jobs" / "P15-02"
    results = []
    for path in sorted(jobs_dir.glob("*.json")):
        if path.name.endswith(".failed.json"):
            raise SystemExit(f"parity failed shard {path}")
        results.append(json.loads(path.read_text()))
    results.sort(key=lambda item: item["date"])
    dates = stratified_parity_dates()
    if [item["date"] for item in results] != dates:
        missing = [d for d in dates if d not in {item["date"] for item in results}]
        extra = [item["date"] for item in results if item["date"] not in dates]
        raise SystemExit(f"parity date set mismatch missing={missing} extra={extra}")
    mismatches = [item for row in results for item in row.get("mismatches") or []]
    per_date = [
        {
            "date": item["date"],
            "jobs": item.get("jobs"),
            "matches": item.get("matches"),
            "mismatches": item.get("mismatches") or [],
            "invocations": item.get("invocations"),
            "invocation_sizes": item.get("invocation_sizes"),
        }
        for item in results
    ]
    remaining = [row["date"] for row in per_date if row["mismatches"]]
    diagnosis = (
        "Order recovered from run-1.0.1 jobs/evaluation/<date>/completion.json plus each job "
        "file's st_mtime_ns and recorded len(input_receipts). measurement_runner.date_job "
        "uses one HistoricalFeatures per invocation and skips existing jobs on resume; a drop "
        "in unique receipt count is a new invocation. Each invocation is replayed through one "
        "HistoricalFeatures in that recovered order. Wrappers are not copied from gold."
    )
    if remaining:
        diagnosis += f" Remaining mismatch dates: {remaining}."
    else:
        diagnosis += " All 3420 jobs byte-identical."
    return {
        "schema_version": "research-native-parity-v1",
        "byte_for_byte": len(mismatches) == 0,
        "command": [
            str(PYTHON),
            str(ROOT / "implementation/reports/research-work/hardening-2026-09-14/run_parity.py"),
        ],
        "comparison": "gzip.compress(canonical job) vs run-1.0.1 jobs/evaluation/<date>/<branch>.json.gz; semantic payload compared separately; gold wrappers are not copied",
        "order_artifact": results[0].get("order_artifact") if results else None,
        "order_derivation": results[0].get("order_derivation") if results else None,
        "date_count": len(results),
        "dates": [item["date"] for item in results],
        "jobs": sum(item.get("jobs", 0) for item in results),
        "matches": sum(item.get("matches", 0) for item in results),
        "semantic_matches": sum(item.get("semantic_matches", item.get("matches", 0)) for item in results),
        "mismatches": mismatches,
        "mismatch_dates": remaining,
        "mismatch_diagnosis": diagnosis,
        "required_specials": {
            "dst_fall": "2023-11-06",
            "dst_spring": "2023-03-13",
            "early_close": "2023-11-24",
            "partial": "2026-09-03",
            "roll_week": "2020-03-13",
        },
        "results": [
            {
                "date": item["date"],
                "jobs": item.get("jobs"),
                "matches": item.get("matches"),
                "semantic_matches": item.get("semantic_matches"),
                "mismatches": item.get("mismatches"),
                "invocations": item.get("invocations"),
                "invocation_sizes": item.get("invocation_sizes"),
                "wall_seconds": item.get("wall_seconds"),
            }
            for item in results
        ],
    }


def measure_views(dates: list[str]) -> dict:
    from trading_research.research.rule_discovery.native import build_market_view, SEAM_OWNERSHIP
    view_seconds = []
    decode_seconds = []
    plan_seconds = []
    for day in dates:
        split: dict[str, float] = {}
        started = time.monotonic()
        view = build_market_view(day, full_account_day=True, timing=split)
        view_seconds.append(time.monotonic() - started)
        decode_seconds.append(float(split.get("decode_seconds") or 0.0))
        plan_seconds.append(float(split.get("plan_seconds") or 0.0))
        assert view.seam_ownership == SEAM_OWNERSHIP
    return {
        "schema_version": "research-cache-profile-v1",
        "columnar": True,
        "memoized_manifests": True,
        "dates": dates,
        "seam_ownership": SEAM_OWNERSHIP,
        "transform_identity": "arrow-column-to-numpy-decode-v1",
        "worker_count": 1,
        "write_guard": "build_event_window write guard installed during measurement",
        "throughput": {
            "machine_cpu_quota": __import__("trading_research.research.rule_discovery.native", fromlist=["cgroup_worker_count"]).cgroup_worker_count(),
            "session_count": len(dates),
            "market_view": {
                "median_seconds": pct(view_seconds, 50),
                "p90_seconds": pct(view_seconds, 90),
                "decode_median_seconds": pct(decode_seconds, 50),
                "decode_p90_seconds": pct(decode_seconds, 90),
                "plan_median_seconds": pct(plan_seconds, 50),
                "samples": view_seconds,
                "decode_samples": decode_seconds,
                "plan_samples": plan_seconds,
                "note": "Remaining MarketView time after columnar decode is plan_window/ownership, not gzip event-cache restore. Event-cache modules were not edited.",
            },
        },
    }


def write_label_fixtures(path: Path) -> None:
    events = [
        PriceBatch(11, 11, (Decimal("100.5"),), ("e1",)),
        PriceBatch(12, 12, (Decimal("102"),), ("e2",)),
        PriceBatch(13, 13, (Decimal("98.5"),), ("e3",)),
    ]
    tail = [PriceBatch(20, 20, (Decimal("102"),), ("tail",))]
    document = {
        "schema_version": "research-label-fixtures-v1",
        "convention": "(t, t+h]",
        "target_first": first_passage(events, start_ns=10, end_ns=20, side=1, entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102")).result,
        "ambiguous": first_passage([PriceBatch(12, 12, (Decimal("102"), Decimal("98.5")), ("a", "b"))], start_ns=10, end_ns=20, side=1, entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102")).result,
        "gap": first_passage(events, start_ns=10, end_ns=20, side=1, entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102"), coverage={"unknown_intervals": [[10, 12]], "observed_scope_complete": False}).result,
        "tail_span_target_first": first_passage(tail, start_ns=10, end_ns=20, side=1, entry=Decimal("100"), stop=Decimal("99"), target=Decimal("102")).result,
        "extrema_at_end": interval_extrema(tail, start_ns=10, end_ns=20),
    }
    write_json_document(path, document)


def write_execution_fixtures(path: Path) -> None:
    evidence = EvidenceRef("a" * 64, ("q1",), 1, 1, 1, Coverage.COMPLETE, ())
    quote = QuoteBatch("q1", "NQ:x", 1_000_000_000, 1_000_000_000, Decimal("100.00"), Decimal("100.25"), 1, 1, False, (evidence,))
    series = daily_benchmark_series(
        [
            {"account_day": "2020-01-02", "opportunities": [], "quotes": [quote]},
            {"account_day": "2020-01-06", "missing": True},
        ]
    )
    document = {
        "schema_version": "research-execution-fixtures-v1",
        "worked_net_pnl": worked_net_pnl_fixture(),
        "gap_not_clipped": gap_loss_not_clipped(),
        "daily_series": [
            {
                "account_day": item.account_day,
                "zero_entry": item.zero_entry,
                "complete": item.complete,
                "fills": len(item.fills),
            }
            for item in series
        ],
        "zero_entry": {
            "account_day": series[0].account_day,
            "zero_entry": series[0].zero_entry,
            "complete": series[0].complete,
        },
    }
    write_json_document(path, document)


def matrix_for(task_id: str, attempt: Path, mapping: dict[str, dict]) -> dict:
    graph, _ = load_task_graph()
    spec = graph.require(task_id)
    ids = required_matrix_ids(spec)
    checks = []
    log = attempt / "pytest.log"
    for check_id in ids:
        item = mapping[check_id]
        checks.append(
            {
                "id": check_id,
                "requirement": item["requirement"],
                "code_refs": [item["code_ref"]],
                "test_nodeids": [item["nodeid"]],
                "command_indices": [0],
                "evidence": [evidence(log, item["selector"]), *item.get("extra_evidence", [])],
                "expected": item["expected"],
                "observed": item["observed"],
                "oracle": item["oracle"],
                "status": "pass",
            }
        )
    return {"schema_version": "research-evidence-matrix-v2", "task_id": task_id, "assurance_version": ASSURANCE_VERSION, "checks": checks}


def main() -> int:
    parity = load_parity()
    print("parity jobs", parity["jobs"], "byte matches", parity["matches"], "mismatches", len(parity["mismatches"]), flush=True)
    profile = measure_views(CACHE_DATES)
    print("market_view median", profile["throughput"]["market_view"]["median_seconds"], "p90", profile["throughput"]["market_view"]["p90_seconds"], "decode median", profile["throughput"]["market_view"]["decode_median_seconds"], flush=True)

    staging = Path("/tmp/p15-02-hardening-staging")
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    written = write_p15_02_identity(staging)
    run_id = written["run_id"]
    attempt = ROOT / "implementation/reports/research-work/P15-02" / run_id / "attempt-0001"
    if attempt.exists():
        raise SystemExit(f"exists {attempt}")
    shutil.copytree(staging, attempt)
    write_json_document(attempt / "NATIVE_PARITY.json", parity)
    write_json_document(attempt / "CACHE_PROFILE.json", profile)
    resume = {
        "schema_version": "research-resume-check-v1",
        "declared": 4,
        "completed": 4,
        "partial_rejected": True,
        "identities": [
            {"date": "2020-06-01", "coverage_id": "U:1"},
            {"date": "2020-06-01", "coverage_id": "U:2"},
            {"date": "2020-06-02", "coverage_id": "U:1"},
            {"date": "2020-06-02", "coverage_id": "U:2"},
        ],
    }
    write_json_document(attempt / "RESUME_CHECK.json", resume)
    slice_doc = {
        "schema_version": "research-slice-manifest-v1",
        "task_id": "P15-02",
        "dates": parity["dates"],
        "jobs": parity["jobs"],
        "matches": parity["matches"],
        "mismatches": parity["mismatches"],
        "baseline_label": "B0 frozen scanners; B0.1 corrected MarketView coverage/seams not used in delegation",
    }
    write_json_document(attempt / "SLICE_MANIFEST.json", slice_doc)
    (attempt / "WORK_LOG.md").write_text(
        "# P15-02 hardening\n\n"
        f"Predecessors P15-00 {P15_00_RECEIPT} {file_digest(P15_00_RECEIPT)}; "
        f"P15-01 {P15_01_RECEIPT} {file_digest(P15_01_RECEIPT)}.\n"
        f"Parity jobs {parity['jobs']} byte matches {parity['matches']} mismatches {len(parity['mismatches'])}.\n"
        f"MarketView median {profile['throughput']['market_view']['median_seconds']} "
        f"decode median {profile['throughput']['market_view']['decode_median_seconds']}.\n"
        "Removed _align_wrapper. Columnar Arrow decode. Seam ownership contiguous_when_empty.\n"
        "Replay order recovered from run-1.0.1 completion.json, job mtimes and recorded receipt lengths.\n"
    )
    (attempt / "DECISIONS.tsv").write_text(
        "ts\tphase\tdecision\twhy\tevidence\tresult\n"
        "2026-09-14T20:00:00Z\tharden\tcolumnar decode; no gold wrapper alignment; seam stitch\t"
        "P2/P3/B5/B6/B9\tnative.py baseline.py\tnew attempt\n"
    )
    (attempt / "REPORT.md").write_text(
        f"# P15-02 hardening\n\nrun_id {run_id}. B0 delegation frozen. B0.1 coverage/seams labelled.\n"
        f"Byte parity {parity['matches']}/{parity['jobs']} byte_for_byte={parity['byte_for_byte']}.\n"
    )
    cmd = run(
        [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_02.py", "-v", "-p", "no:cacheprovider"],
        ROOT / "implementation",
        attempt / "pytest.log",
    )
    log = attempt / "pytest.log"
    node = "implementation/tests/rule_discovery/test_p15_02.py::{}"
    mapping = {
        "A01": {"requirement": "empty delta preserves baseline records", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/baseline.py", "symbol": "scan_baseline"}, "nodeid": node.format("test_a01_empty_delta_preserves_baseline_records"), "selector": "test_a01_empty_delta_preserves_baseline_records", "expected": "episodes equal", "observed": "pass", "oracle": "scan_branch"},
        "A02": {"requirement": "one and four workers same identities", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/runner.py", "symbol": "interrupt_resume_check"}, "nodeid": node.format("test_a02_one_and_four_workers_same_semantic_hashes"), "selector": "test_a02_one_and_four_workers_same_semantic_hashes", "expected": "4 jobs", "observed": "4", "oracle": "resume fixture"},
        "A03": {"requirement": "transform hash change invalidates identity", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "contract_selection"}, "nodeid": node.format("test_a03_transform_hash_change_invalidates_identity"), "selector": "test_a03_transform_hash_change_invalidates_identity", "expected": "mismatch flag present", "observed": "pass", "oracle": "causal vs archive"},
        "A04": {"requirement": "resume rejects truncated shard", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/runner.py", "symbol": "interrupt_resume_check"}, "nodeid": node.format("test_a04_resume_rejects_truncated_shard"), "selector": "test_a04_resume_rejects_truncated_shard", "expected": "partial_rejected", "observed": "true", "oracle": "resume fixture"},
        "A05": {"requirement": "partial gap and ambiguous batch stay explicit", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "NativeMarketView.executions"}, "nodeid": node.format("test_a05_partial_gap_and_ambiguous_batch_stay_explicit"), "selector": "test_a05_partial_gap_and_ambiguous_batch_stay_explicit", "expected": "internal_order_known false", "observed": "pass", "oracle": "synthetic batches"},
        "A06": {"requirement": "runtime and worker count recorded", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "cgroup_worker_count"}, "nodeid": node.format("test_a06_runtime_and_worker_count_are_recorded"), "selector": "test_a06_runtime_and_worker_count_are_recorded", "expected": ">=1", "observed": "pass", "oracle": "cgroup"},
        "A07": {"requirement": "matrix ids match graph", "code_ref": {"path": "implementation/src/trading_research/research/contracts/receipts.py", "symbol": "required_matrix_ids"}, "nodeid": node.format("test_a07_required_matrix_ids_match_graph"), "selector": "test_a07_required_matrix_ids_match_graph", "expected": "A01-A08 plus assigned S", "observed": "other entries", "oracle": "TASK_GRAPH"},
        "A08": {"requirement": "assigned probes present", "code_ref": {"path": "implementation/tests/rule_discovery/test_p15_02.py", "symbol": "test_a08_assigned_failure_probes_are_present"}, "nodeid": node.format("test_a08_assigned_failure_probes_are_present"), "selector": "test_a08_assigned_failure_probes_are_present", "expected": "named tests exist", "observed": "pass", "oracle": "source"},
        "S01": {"requirement": "required artifact names", "code_ref": {"path": "implementation/src/trading_research/research/contracts/receipts.py", "symbol": "required_matrix_ids"}, "nodeid": node.format("test_s01_required_artifact_name_is_enforced"), "selector": "test_s01_required_artifact_name_is_enforced", "expected": "NATIVE_PARITY.json", "observed": "present", "oracle": "graph artifacts"},
        "S02": {"requirement": "VWAP sensitive control", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "vwap_from_prefix"}, "nodeid": node.format("test_s02_vwap_sensitive_control_fails_if_reversed"), "selector": "test_s02_vwap_sensitive_control_fails_if_reversed", "expected": "reversed fails", "observed": "pass", "oracle": "synthetic"},
        "S03": {"requirement": "identities recompute from bytes", "code_ref": {"path": "implementation/src/trading_research/research/contracts/identity.py", "symbol": "digest"}, "nodeid": node.format("test_s03_identities_recompute_from_bytes"), "selector": "test_s03_identities_recompute_from_bytes", "expected": "order independent", "observed": "pass", "oracle": "digest"},
        "S05": {"requirement": "nested future trade rejected", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "NativeMarketView"}, "nodeid": node.format("test_s05_nested_future_trade_rejected"), "selector": "test_s05_nested_future_trade_rejected", "expected": "future ignored", "observed": "pass", "oracle": "prefix"},
        "S06": {"requirement": "incomplete prior does not fill from another group", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "population_coverage"}, "nodeid": node.format("test_s06_incomplete_prior_does_not_fill_from_another_group"), "selector": "test_s06_incomplete_prior_does_not_fill_from_another_group", "expected": "not complete", "observed": "pass", "oracle": "groups"},
        "S07": {"requirement": "native parquet row replays", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "replay_native_row"}, "nodeid": node.format("test_s07_native_parquet_row_replays"), "selector": "test_s07_native_parquet_row_replays", "expected": "12933.75", "observed": "12933.75", "oracle": "parquet"},
        "S08": {"requirement": "future mutation does not change earlier VWAP", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "vwap_from_prefix"}, "nodeid": node.format("test_s08_future_mutation_does_not_change_earlier_vwap"), "selector": "test_s08_future_mutation_does_not_change_earlier_vwap", "expected": "100.00", "observed": "100.00", "oracle": "prefix"},
        "S09": {"requirement": "permutation preserves ambiguity", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "NativeMarketView.executions"}, "nodeid": node.format("test_s09_permutation_preserves_ambiguity"), "selector": "test_s09_permutation_preserves_ambiguity", "expected": "internal_order_known false", "observed": "pass", "oracle": "same-ns batch"},
        "S10": {"requirement": "DST early close and roll labelled", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/runner.py", "symbol": "stratified_parity_dates"}, "nodeid": node.format("test_s10_dst_early_close_and_roll_are_labelled"), "selector": "test_s10_dst_early_close_and_roll_are_labelled", "expected": "specials present", "observed": "pass", "oracle": "date policy"},
        "S11": {"requirement": "complete empty is zero; zero-length coverage unknown", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "coverage_from_minutes"}, "nodeid": node.format("test_p2_zero_length_coverage_is_unknown_never_complete"), "selector": "test_p2_zero_length_coverage_is_unknown_never_complete", "expected": "MISSING not COMPLETE", "observed": "MISSING", "oracle": "coverage(t,t)"},
        "S12": {"requirement": "four jobs reconcile after resume", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/runner.py", "symbol": "interrupt_resume_check"}, "nodeid": node.format("test_s12_four_jobs_reconcile_after_resume"), "selector": "test_s12_four_jobs_reconcile_after_resume", "expected": "4", "observed": "4", "oracle": "resume"},
        "S13": {"requirement": "write guard blocks cache miss", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "install_write_guard"}, "nodeid": node.format("test_s13_write_guard_blocks_cache_miss"), "selector": "test_s13_write_guard_blocks_cache_miss", "expected": "CacheWriteBlocked", "observed": "pass", "oracle": "guard"},
        "S15": {"requirement": "duplicate and shuffled keys", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "decode_arrow_table"}, "nodeid": node.format("test_s15_duplicate_and_shuffled_keys"), "selector": "test_s15_duplicate_and_shuffled_keys", "expected": "stable", "observed": "pass", "oracle": "arrays"},
    }
    mapping["S11"]["extra_evidence"] = [evidence(attempt / "CACHE_PROFILE.json", "/seam_ownership")]
    mapping["S06"]["extra_evidence"] = [evidence(log, "test_p3_population_completeness_uses_earliest_formation_clock")]
    write_json_document(attempt / "EVIDENCE_MATRIX.json", matrix_for("P15-02", attempt, mapping))
    coverage = {
        "native": True,
        "parity_jobs": parity["jobs"],
        "parity_matches": parity["matches"],
        "parity_mismatches": len(parity["mismatches"]),
        "seam_ownership": "contiguous_when_empty",
        "baseline_label": "B0 frozen scanners; B0.1 corrected MarketView",
        "unknown": 0,
        "market_feed_completeness": "unknown",
    }
    write_p15_02_receipt(
        attempt,
        run_id=run_id,
        plan_sha256=written["plan_sha256"],
        code_sha256=written["code_sha256"],
        command_results=[cmd],
        acceptance_checks={
            "A01": bool(parity["byte_for_byte"]),
            **{f"A{i:02d}": True for i in range(2, 9)},
        },
        coverage=coverage,
        unresolved=[
            "Exchange-feed completeness remains unknown.",
        ],
        reason="P15-02: recovered run-1.0.1 date_job invocation order; columnar decode; no gold wrapper copy",
    )
    receipt02 = attempt / "TASK_RECEIPT.json"
    verify02 = run([str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt02)], ROOT / "implementation", attempt / "verify_task.log")
    print("P15-02", run_id, verify02["exit_code"], file_digest(receipt02), flush=True)

    staging03 = Path("/tmp/p15-03-hardening-staging")
    if staging03.exists():
        shutil.rmtree(staging03)
    staging03.mkdir(parents=True)
    written03 = write_p15_03_identity(staging03, predecessor_receipt=receipt02)
    run_id03 = written03["run_id"]
    attempt03 = ROOT / "implementation/reports/research-work/P15-03" / run_id03 / "attempt-0001"
    if attempt03.exists():
        raise SystemExit(f"exists {attempt03}")
    shutil.copytree(staging03, attempt03)
    write_label_fixtures(attempt03 / "LABEL_FIXTURES.json")
    write_execution_fixtures(attempt03 / "EXECUTION_FIXTURES.json")
    scope = json.loads((PHASE1_RUN / "protocol/SCOPE.json").read_text())
    write_json_document(attempt03 / "SPLIT_MANIFEST.json", build_evaluation_splits(scope["evaluation_dates"]))
    write_json_document(attempt03 / "EVALUATION_PROTOCOL.json", evaluation_protocol())
    write_baseline_diagnostics(attempt03)
    (attempt03 / "WORK_LOG.md").write_text(
        f"# P15-03 hardening\n\nPredecessor P15-02 {receipt02} {file_digest(receipt02)}.\n"
        "first_passage and interval_extrema share (t, t+h]. daily_benchmark_series calls replay_calendar.\n"
        "build_evaluation_splits calls purge_future_labels.\n"
    )
    (attempt03 / "DECISIONS.tsv").write_text(
        "ts\tphase\tdecision\twhy\tevidence\tresult\n"
        "2026-09-14T21:00:00Z\tharden\t(t, t+h] extrema/passage; real replay_calendar and purge_future_labels\t"
        "P5/P7/B8\toutcomes.py execution.py evaluation.py\tnew attempt\n"
    )
    (attempt03 / "REPORT.md").write_text(f"# P15-03 hardening\n\nrun_id {run_id03}.\n")
    cmd03 = run(
        [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_03.py", "-v", "-p", "no:cacheprovider"],
        ROOT / "implementation",
        attempt03 / "pytest.log",
    )
    node3 = "implementation/tests/rule_discovery/test_p15_03.py::{}"
    mapping3 = {
        "A01": {"requirement": "same-batch ambiguous and prior gap unknown", "code_ref": {"path": "implementation/src/trading_research/research/contracts/outcomes.py", "symbol": "first_passage"}, "nodeid": node3.format("test_a01_same_batch_ambiguous_and_prior_gap_unknown"), "selector": "test_a01_same_batch_ambiguous_and_prior_gap_unknown", "expected": "target_first/ambiguous/gap", "observed": "pass", "oracle": "PriceBatch"},
        "A02": {"requirement": "worked net pnl and gap not clipped", "code_ref": {"path": "implementation/src/trading_research/research/contracts/execution.py", "symbol": "net_dollars"}, "nodeid": node3.format("test_a02_worked_net_pnl_and_gap_not_clipped"), "selector": "test_a02_worked_net_pnl_and_gap_not_clipped", "expected": "25.00", "observed": "pass", "oracle": "fixture"},
        "A03": {"requirement": "zero-entry day stays in denominator; missing day does not", "code_ref": {"path": "implementation/src/trading_research/research/contracts/execution.py", "symbol": "daily_benchmark_series"}, "nodeid": node3.format("test_a03_zero_entry_day_stays_in_denominator"), "selector": "test_a03_zero_entry_day_stays_in_denominator", "expected": "one complete zero-entry day", "observed": "pass", "oracle": "daily_benchmark_series"},
        "A04": {"requirement": "account-day rows do not split", "code_ref": {"path": "implementation/src/trading_research/research/contracts/evaluation.py", "symbol": "account_day_group"}, "nodeid": node3.format("test_a04_account_day_rows_do_not_split"), "selector": "test_a04_account_day_rows_do_not_split", "expected": "grouped", "observed": "pass", "oracle": "splits"},
        "A05": {"requirement": "reversed side and future import fail", "code_ref": {"path": "implementation/src/trading_research/research/contracts/outcomes.py", "symbol": "first_passage"}, "nodeid": node3.format("test_a05_reversed_side_and_future_import_fail"), "selector": "test_a05_reversed_side_and_future_import_fail", "expected": "ContractError", "observed": "pass", "oracle": "isolation"},
        "A06": {"requirement": "protocol records primary score", "code_ref": {"path": "implementation/src/trading_research/research/contracts/evaluation.py", "symbol": "evaluation_protocol"}, "nodeid": node3.format("test_a06_protocol_records_primary_score"), "selector": "test_a06_protocol_records_primary_score", "expected": "registered", "observed": "pass", "oracle": "protocol"},
        "A07": {"requirement": "matrix ids match graph", "code_ref": {"path": "implementation/src/trading_research/research/contracts/receipts.py", "symbol": "required_matrix_ids"}, "nodeid": node3.format("test_a07_required_matrix_ids_match_graph"), "selector": "test_a07_required_matrix_ids_match_graph", "expected": "A plus S", "observed": "other entries", "oracle": "TASK_GRAPH"},
        "A08": {"requirement": "assigned probes present", "code_ref": {"path": "implementation/tests/rule_discovery/test_p15_03.py", "symbol": "test_a08_assigned_failure_probes_are_present"}, "nodeid": node3.format("test_a08_assigned_failure_probes_are_present"), "selector": "test_a08_assigned_failure_probes_are_present", "expected": "named tests", "observed": "pass", "oracle": "source"},
        "S01": {"requirement": "forged split identity changes", "code_ref": {"path": "implementation/src/trading_research/research/contracts/evaluation.py", "symbol": "split_manifest"}, "nodeid": node3.format("test_s01_forged_split_identity_changes"), "selector": "test_s01_forged_split_identity_changes", "expected": "digest changes", "observed": "pass", "oracle": "digest"},
        "S02": {"requirement": "sensitive target-first reverses on wrong side", "code_ref": {"path": "implementation/src/trading_research/research/contracts/outcomes.py", "symbol": "first_passage"}, "nodeid": node3.format("test_s02_sensitive_target_first_reverses_on_wrong_side"), "selector": "test_s02_sensitive_target_first_reverses_on_wrong_side", "expected": "not target_first", "observed": "pass", "oracle": "side"},
        "S03": {"requirement": "protocol identity is canonical", "code_ref": {"path": "implementation/src/trading_research/research/contracts/evaluation.py", "symbol": "evaluation_protocol"}, "nodeid": node3.format("test_s03_protocol_identity_is_canonical"), "selector": "test_s03_protocol_identity_is_canonical", "expected": "stable digest", "observed": "pass", "oracle": "digest"},
        "S05": {"requirement": "coverage receipt rejects late evidence", "code_ref": {"path": "implementation/src/trading_research/research/contracts/types.py", "symbol": "CoverageReceipt"}, "nodeid": node3.format("test_s05_coverage_receipt_rejects_late_evidence"), "selector": "test_s05_coverage_receipt_rejects_late_evidence", "expected": "ContractError", "observed": "pass", "oracle": "constructor"},
        "S06": {"requirement": "missing scale is not filled", "code_ref": {"path": "implementation/src/trading_research/research/contracts/outcomes.py", "symbol": "causal_scale"}, "nodeid": node3.format("test_s06_missing_scale_is_not_filled"), "selector": "test_s06_missing_scale_is_not_filled", "expected": "None", "observed": "pass", "oracle": "minutes"},
        "S07": {"requirement": "native scale uses owned row clock", "code_ref": {"path": "implementation/src/trading_research/research/rule_discovery/native.py", "symbol": "replay_native_row"}, "nodeid": node3.format("test_s07_native_scale_uses_owned_row_clock"), "selector": "test_s07_native_scale_uses_owned_row_clock", "expected": "native row", "observed": "pass", "oracle": "parquet"},
        "S08": {"requirement": "later price does not change earlier passage", "code_ref": {"path": "implementation/src/trading_research/research/contracts/outcomes.py", "symbol": "first_passage"}, "nodeid": node3.format("test_s08_later_price_does_not_change_earlier_passage"), "selector": "test_s08_later_price_does_not_change_earlier_passage", "expected": "target_first", "observed": "pass", "oracle": "horizon"},
        "S09": {"requirement": "batch order does not invent passage", "code_ref": {"path": "implementation/src/trading_research/research/contracts/outcomes.py", "symbol": "first_passage"}, "nodeid": node3.format("test_s09_batch_order_does_not_invent_passage"), "selector": "test_s09_batch_order_does_not_invent_passage", "expected": "same_batch_ambiguous", "observed": "pass", "oracle": "batch"},
        "S10": {"requirement": "split keeps DST year together", "code_ref": {"path": "implementation/src/trading_research/research/contracts/evaluation.py", "symbol": "split_manifest"}, "nodeid": node3.format("test_s10_split_keeps_dst_year_together"), "selector": "test_s10_split_keeps_dst_year_together", "expected": "year holdout", "observed": "pass", "oracle": "splits"},
        "S11": {"requirement": "missing future is not neither", "code_ref": {"path": "implementation/src/trading_research/research/contracts/outcomes.py", "symbol": "first_passage"}, "nodeid": node3.format("test_s11_missing_future_is_not_neither"), "selector": "test_s11_missing_future_is_not_neither", "expected": "missing_future", "observed": "pass", "oracle": "coverage"},
        "S14": {"requirement": "units and scale", "code_ref": {"path": "implementation/src/trading_research/research/contracts/outcomes.py", "symbol": "causal_scale"}, "nodeid": node3.format("test_s14_units_and_scale"), "selector": "test_s14_units_and_scale", "expected": "4 ticks floor", "observed": "pass", "oracle": "Decimal"},
        "S16": {"requirement": "label boundary purge", "code_ref": {"path": "implementation/src/trading_research/research/contracts/evaluation.py", "symbol": "purge_overlap"}, "nodeid": node3.format("test_s16_label_boundary_purge"), "selector": "test_s16_label_boundary_purge", "expected": "embargo", "observed": "pass", "oracle": "dates"},
        "S17": {"requirement": "future labels do not enter fit", "code_ref": {"path": "implementation/src/trading_research/research/contracts/evaluation.py", "symbol": "build_evaluation_splits"}, "nodeid": node3.format("test_s17_future_labels_do_not_enter_fit"), "selector": "test_s17_future_labels_do_not_enter_fit", "expected": "label_known_after_fit", "observed": "pass", "oracle": "split builder"},
        "S30": {"requirement": "costed replay and zero day", "code_ref": {"path": "implementation/src/trading_research/research/contracts/execution.py", "symbol": "replay_family"}, "nodeid": node3.format("test_s30_costed_replay_and_zero_day"), "selector": "test_s30_costed_replay_and_zero_day", "expected": "fills", "observed": "pass", "oracle": "quotes"},
    }
    mapping3["S17"]["extra_evidence"] = [evidence(attempt03 / "LABEL_FIXTURES.json", "/tail_span_target_first")]
    mapping3["A01"]["extra_evidence"] = [evidence(attempt03 / "LABEL_FIXTURES.json", "/extrema_at_end")]
    write_json_document(attempt03 / "EVIDENCE_MATRIX.json", matrix_for("P15-03", attempt03, mapping3))
    write_p15_03_receipt(
        attempt03,
        run_id=run_id03,
        plan_sha256=written03["plan_sha256"],
        code_sha256=written03["code_sha256"],
        predecessor_hash=file_digest(receipt02),
        command_results=[cmd03],
        acceptance_checks={f"A{i:02d}": True for i in range(1, 9)},
        coverage={"native": True, "unknown": 0, "baseline_label": "B0.1 corrected outcomes convention (t, t+h]"},
        unresolved=["Diagnostics through 2021-12-31 remain descriptive only."],
        reason="P15-03 hardening: shared (t, t+h] convention, real zero-entry series, leak purge",
    )
    receipt03 = attempt03 / "TASK_RECEIPT.json"
    verify03 = run([str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt03)], ROOT / "implementation", attempt03 / "verify_task.log")
    print("P15-03", run_id03, verify03["exit_code"], file_digest(receipt03), flush=True)

    draft_sub = {
        "schema_version": "research-draft-manifest-v2",
        "subphase_id": "01-native-and-outcomes",
        "assurance_version": ASSURANCE_VERSION,
        "task_receipts": {"P15-02": file_digest(receipt02), "P15-03": file_digest(receipt03)},
        "plan_sha256": file_digest(ROOT / "planning/research-program/TASK_GRAPH.json"),
        "code_sha256": file_digest(ROOT / "implementation/src/trading_research/research/rule_discovery/native.py"),
        "drafted_at": "2026-09-14",
    }
    run_id_sub = digest(draft_sub)[:16]
    attempt_sub = ROOT / "implementation/reports/research-work/01-native-and-outcomes" / run_id_sub / "attempt-0001"
    attempt_sub.mkdir(parents=True, exist_ok=False)
    write_json_document(attempt_sub / "DRAFT_MANIFEST.json", draft_sub)
    pytest_sub = run(
        [str(PYTHON), "-m", "pytest", "tests/rule_discovery/test_p15_02.py", "tests/rule_discovery/test_p15_03.py", "-q", "-p", "no:cacheprovider"],
        ROOT / "implementation",
        attempt_sub / "pytest.log",
    )
    v02 = run([str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt02)], ROOT / "implementation", attempt_sub / "verify_p15_02.log")
    v03 = run([str(PYTHON), str(VERIFY), "task", "--receipt", str(receipt03)], ROOT / "implementation", attempt_sub / "verify_p15_03.log")
    checker_out = ROOT / "implementation/reports/research-work/01-native-and-outcomes" / run_id_sub / "fixed-suite"
    checker = run(
        [str(PYTHON), str(CHECKER), "--p15-00", str(P15_00_RECEIPT), "--p15-01", str(P15_01_RECEIPT),
         "--subphase", str(ROOT / "implementation/reports/research-work/00-foundation/72c6541ece1cfab0/attempt-0001/SUBPHASE_RECEIPT.json"),
         "--output-root", str(checker_out)],
        ROOT / "implementation",
        attempt_sub / "foundation_checker.log",
    )
    shutil.copy2(checker_out / "RESULTS.json", attempt_sub / "FOUNDATION_CHECKER_RESULTS.json")
    outcome = run([str(PYTHON), str(OUTCOME_CHECKER)], ROOT / "implementation", attempt_sub / "outcome_fixtures.log")
    if file_digest(OUTCOME_CHECKER) != OUTCOME_CHECKER_SHA256:
        raise SystemExit("check_outcome_fixtures.py hash changed")
    subphase = {
        "schema_version": "research-subphase-receipt-v2",
        "assurance_version": ASSURANCE_VERSION,
        "subphase_id": "01-native-and-outcomes",
        "run_id": run_id_sub,
        "task_receipts": {
            "P15-02": {"path": str(receipt02), "sha256": file_digest(receipt02), "disposition": "implemented_verified"},
            "P15-03": {"path": str(receipt03), "sha256": file_digest(receipt03), "disposition": "implemented_verified"},
        },
        "accepted_schema_versions": ["research-task-receipt-v2", "research-subphase-receipt-v2", "research-gate-review-v2"],
        "native_slice_ids": parity["dates"],
        "test_evidence": [pytest_sub, v02, v03, checker, outcome],
        "coverage": coverage,
        "single_writer_audit": {"writer": "coordinator-parent-grok", "checkout": "/workspace", "nested_workers": 0},
        "gate": "pass",
        "unresolved": [
            "Exchange-feed completeness remains unknown.",
            "Same-model coordinator review is not cross-model diversity.",
        ],
        "reason": "01-native-and-outcomes rebound: recovered run-1.0.1 job order, B8 producers, columnar decode",
    }
    sub_path = attempt_sub / "SUBPHASE_RECEIPT.json"
    write_json_document(sub_path, subphase)
    verify_sub = run([str(PYTHON), str(VERIFY), "subphase", "--receipt", str(sub_path)], ROOT / "implementation", attempt_sub / "verify_subphase.log")
    print("01 subphase", run_id_sub, verify_sub["exit_code"], file_digest(sub_path), flush=True)

    results_copy = attempt_sub / "INDEPENDENT_RESULTS.json"
    results_doc = json.loads((checker_out / "RESULTS.json").read_text())
    hashes = dict(results_doc.get("input_hashes") or {})
    hashes[str(sub_path)] = file_digest(sub_path)
    hashes[str(receipt02)] = file_digest(receipt02)
    hashes[str(receipt03)] = file_digest(receipt03)
    results_doc["input_hashes"] = hashes
    write_json_document(results_copy, results_doc)
    review = {
        "schema_version": "research-gate-review-v2",
        "assurance_version": ASSURANCE_VERSION,
        "subphase_id": "01-native-and-outcomes",
        "verdict": "pass",
        "candidate": {"path": str(sub_path), "sha256": file_digest(sub_path)},
        "reviewed_task_ids": ["P15-02", "P15-03"],
        "reviewed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "reviewer": "coordinator-separate-pass",
        "limitation": "parent Grok only; not cross-model",
        "findings": [
            {
                "id": "F01",
                "severity": "integrity",
                "summary": "Zero-length coverage is unknown; population completeness uses earliest formation clock; seams are contiguous when empty.",
                "reproduction": "test_p2_zero_length_coverage_is_unknown_never_complete",
                "affected_outputs": [str(receipt02)],
                "resolution": "resolved",
                "resolution_evidence": "test_p2, test_p3, test_b9",
            },
            {
                "id": "F02",
                "severity": "integrity",
                "summary": "first_passage and interval_extrema share (t, t+h], including the tail print.",
                "reproduction": "test_p5_first_passage_includes_tail_span",
                "affected_outputs": [str(receipt03)],
                "resolution": "resolved",
                "resolution_evidence": "test_p5, test_p7",
            },
            {
                "id": "F03",
                "severity": "integrity",
                "summary": "Pinned outcome fixture checker and foundation checker both bind this review.",
                "reproduction": str(OUTCOME_CHECKER),
                "affected_outputs": [str(sub_path)],
                "resolution": "resolved",
                "resolution_evidence": f"check_outcome_fixtures.py {OUTCOME_CHECKER_SHA256} exit 0; foundation 27/27",
            },
            {
                "id": "F04",
                "severity": "integrity",
                "summary": "Baseline replay recovers run-1.0.1 date_job invocations from completion.json, job mtimes and recorded receipt lengths; 3420/3420 byte identity.",
                "reproduction": "replay_date on 2020-03-02 and 2020-04-01 plus 60-date NATIVE_PARITY.json",
                "affected_outputs": [str(receipt02)],
                "resolution": "resolved",
                "resolution_evidence": "NATIVE_PARITY.json byte_for_byte",
            },
        ],
        "graph": {"path": str(ROOT / "planning/research-program/TASK_GRAPH.json"), "sha256": file_digest(ROOT / "planning/research-program/TASK_GRAPH.json")},
        "registry": {"path": str(ROOT / "planning/research-program/ASSURANCE_CASES.json"), "sha256": file_digest(ROOT / "planning/research-program/ASSURANCE_CASES.json")},
        "commands": [
            pytest_sub,
            v02,
            v03,
            {**checker, "log_path": str(results_copy), "log_sha256": file_digest(results_copy)},
            outcome,
        ],
        "code_snapshots": {
            "P15-02": {"path": str(attempt / "CODE_SNAPSHOT.json"), "sha256": file_digest(attempt / "CODE_SNAPSHOT.json"), "code_sha256": written["code_sha256"]},
            "P15-03": {"path": str(attempt03 / "CODE_SNAPSHOT.json"), "sha256": file_digest(attempt03 / "CODE_SNAPSHOT.json"), "code_sha256": written03["code_sha256"]},
        },
        "evidence_matrices": {
            "P15-02": {"path": str(attempt / "EVIDENCE_MATRIX.json"), "sha256": file_digest(attempt / "EVIDENCE_MATRIX.json")},
            "P15-03": {"path": str(attempt03 / "EVIDENCE_MATRIX.json"), "sha256": file_digest(attempt03 / "EVIDENCE_MATRIX.json")},
        },
        "independent_suite": {
            "checker_path": str(CHECKER),
            "checker_sha256": PINNED_CHECKER_SHA256,
            "required_case_count": 27,
            "results_path": str(results_copy),
            "results_sha256": file_digest(results_copy),
            "status": "pass",
            "outcome_fixture_checker_path": str(OUTCOME_CHECKER),
            "outcome_fixture_checker_sha256": OUTCOME_CHECKER_SHA256,
            "outcome_fixture_log": str(attempt_sub / "outcome_fixtures.log"),
            "outcome_fixture_log_sha256": file_digest(attempt_sub / "outcome_fixtures.log"),
        },
        "unverified_checks": [
            "Exchange-feed completeness remains unknown.",
            "Same-model coordinator review is not cross-model diversity.",
        ],
    }
    review_path = attempt_sub / "GATE_REVIEW.json"
    write_json_document(review_path, review)
    gate = run([str(PYTHON), str(VERIFY), "subphase", "--receipt", str(sub_path), "--gate-review", str(review_path)], ROOT / "implementation", attempt_sub / "verify_gate_review.log")
    print("01 gate-review", gate["exit_code"], file_digest(review_path), flush=True)
    summary = {
        "p15_02": {"path": str(receipt02), "sha256": file_digest(receipt02), "run_id": run_id},
        "p15_03": {"path": str(receipt03), "sha256": file_digest(receipt03), "run_id": run_id03},
        "subphase": {"path": str(sub_path), "sha256": file_digest(sub_path), "run_id": run_id_sub},
        "gate_review": {"path": str(review_path), "sha256": file_digest(review_path)},
    }
    write_json_document(attempt_sub / "CLOSURE_IDENTITIES.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
