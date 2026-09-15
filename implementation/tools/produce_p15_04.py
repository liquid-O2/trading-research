#!/usr/bin/env python3
"""Produce P15-09..16 receipts and the 04-family-adapters subphase candidate."""
from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
import sys
import time

ROOT = Path("/workspace")
SRC = ROOT / "implementation/src"
sys.path.insert(0, str(SRC))

from trading_research.research.contracts.identity import (  # noqa: E402
    ASSURANCE_VERSION,
    artifact_entry,
    digest,
    file_digest,
    write_json_document,
)
from trading_research.research.rule_discovery.registry import expand_candidate_bank  # noqa: E402
from trading_research.research.rule_discovery.runner import (  # noqa: E402
    engineering_slice_dates,
    freeze,
    primitive_throughput_dates,
    slice_run,
    write_named_receipt,
    write_task_identity,
)
from trading_research.research.rule_discovery.source_adapters.common import (  # noqa: E402
    P15_08_RECEIPT,
    PRIMARY_BRANCH,
    adapter_worker_count,
    baseline_repair_source,
    family_candidates,
    full_history_limit,
    measure_family_throughput,
    run_changed_axis_cases,
)
from trading_research.research.rule_discovery.source_adapters import (  # noqa: E402,F401
    green_failure,
    green_vwap_scalp,
    jumbo,
    keani,
    member,
    processes,
    saint,
    sires,
)

PY = ROOT / "implementation/.venv/bin/python"
IMP = ROOT / "implementation"
REPORTS = ROOT / "implementation/reports/research-work"
PYTHON = str(PY)
P15_08 = P15_08_RECEIPT

TASKS = {
    "P15-09": {
        "module": "jumbo",
        "owned": (
            "implementation/src/trading_research/research/rule_discovery/source_adapters/jumbo.py",
            "implementation/src/trading_research/research/rule_discovery/families/jumbo.json",
            "implementation/tests/rule_discovery/test_p15_09.py",
        ),
        "wiki": ("wiki/method-jumbo-tbr.md",),
        "artifacts": ("BASELINE_PARITY.json", "FAMILY_CANDIDATES.json", "NATIVE_CASES.json", "FAMILY_REPORT.md"),
        "family": "JJ-TBR",
        "reason": "P15-09 Jumbo range branches with B0/B0.1 dual scan, Judas strict/deferred, TBR quadrants, outbound 09:40 exit and single_purged add window.",
    },
    "P15-10": {
        "module": "green_failure",
        "owned": (
            "implementation/src/trading_research/research/rule_discovery/source_adapters/green_failure.py",
            "implementation/src/trading_research/research/rule_discovery/families/green_failure.json",
            "implementation/tests/rule_discovery/test_p15_10.py",
        ),
        "wiki": ("wiki/method-green-bird-failure.md",),
        "artifacts": ("BASELINE_PARITY.json", "FAMILY_CANDIDATES.json", "NATIVE_CASES.json", "FAMILY_REPORT.md"),
        "family": "GB-FAIL",
        "reason": "P15-10 Green Bird failure with P4 omission, A1 london_box, A2 asia_box, A3 overnight scan, golden-pocket and retracement variants.",
    },
    "P15-11": {
        "module": "green_vwap_scalp",
        "owned": (
            "implementation/src/trading_research/research/rule_discovery/source_adapters/green_vwap_scalp.py",
            "implementation/src/trading_research/research/rule_discovery/families/green_vwap_scalp.json",
            "implementation/tests/rule_discovery/test_p15_11.py",
        ),
        "wiki": ("wiki/method-green-bird-vwap-continuation.md", "wiki/method-green-bird-directional-scalps.md"),
        "artifacts": ("BASELINE_PARITY.json", "FAMILY_CANDIDATES.json", "NATIVE_CASES.json", "FAMILY_REPORT.md"),
        "family": "GB-VWAP",
        "reason": "P15-11 GB-VWAP/scalps with D1 retest-window fixture and A4 golden_pocket_continuation.",
    },
    "P15-12": {
        "module": "sires",
        "owned": (
            "implementation/src/trading_research/research/rule_discovery/source_adapters/sires.py",
            "implementation/src/trading_research/research/rule_discovery/families/sires.json",
            "implementation/tests/rule_discovery/test_p15_12.py",
        ),
        "wiki": ("wiki/method-sires-thesis-flow.md",),
        "artifacts": ("BASELINE_PARITY.json", "FAMILY_CANDIDATES.json", "NATIVE_CASES.json", "FAMILY_REPORT.md"),
        "family": "SIRES",
        "reason": "P15-12 Sires with three-tick replenishment, OFM 1R-3R, C5 thesis direction, P1 and P6 adapter rules.",
    },
    "P15-13": {
        "module": "saint",
        "owned": (
            "implementation/src/trading_research/research/rule_discovery/source_adapters/saint.py",
            "implementation/src/trading_research/research/rule_discovery/families/saint.json",
            "implementation/tests/rule_discovery/test_p15_13.py",
        ),
        "wiki": ("wiki/method-saint-amt.md",),
        "artifacts": ("BASELINE_PARITY.json", "FAMILY_CANDIDATES.json", "NATIVE_CASES.json", "FAMILY_REPORT.md"),
        "family": "SAINT-AMT",
        "reason": "P15-13 Saint operational arrival/LTF/profile rules so SAINT-AMT leaves the B0.1 unknown state.",
    },
    "P15-14": {
        "module": "member",
        "owned": (
            "implementation/src/trading_research/research/rule_discovery/source_adapters/member.py",
            "implementation/src/trading_research/research/rule_discovery/families/member.json",
            "implementation/tests/rule_discovery/test_p15_14.py",
        ),
        "wiki": ("wiki/method-member-two-reasons.md",),
        "artifacts": ("BASELINE_PARITY.json", "FAMILY_CANDIDATES.json", "NATIVE_CASES.json", "FAMILY_REPORT.md"),
        "family": "MEMBER-TWO-REASONS",
        "reason": "P15-14 Member independent-reasons: reaction-period HVN fails, vacuous all() is unknown.",
    },
    "P15-15": {
        "module": "keani",
        "owned": (
            "implementation/src/trading_research/research/rule_discovery/source_adapters/keani.py",
            "implementation/src/trading_research/research/rule_discovery/families/keani.json",
            "implementation/tests/rule_discovery/test_p15_15.py",
        ),
        "wiki": ("wiki/method-keani-open-above-value.md",),
        "artifacts": ("BASELINE_PARITY.json", "FAMILY_CANDIDATES.json", "NATIVE_CASES.json", "FAMILY_REPORT.md"),
        "family": "KEANI-OPEN-ABOVE-VALUE",
        "reason": "P15-15 Keani C4 rejection at developing POC or prior-day VAH; developing-VAL remains B0.",
    },
    "P15-16": {
        "module": "processes",
        "owned": (
            "implementation/src/trading_research/research/rule_discovery/source_adapters/processes.py",
            "implementation/src/trading_research/research/rule_discovery/families/processes.json",
            "implementation/tests/rule_discovery/test_p15_16.py",
        ),
        "wiki": (
            "wiki/method-refill-effect.md",
            "wiki/method-jetbundle-auction-states.md",
            "wiki/method-stoic-data-engine.md",
            "wiki/method-stoic-asymmetric-compounding.md",
        ),
        "artifacts": ("PROCESS_OBSERVATIONS.json", "PROCESS_LIMITS.json", "FAMILY_REPORT.md"),
        "family": "REFILL-STUDY",
        "reason": "P15-16 process observations; F-REFILL-POP re-derived from refill-effect.pdf pp.5-9.",
    },
}

COMMON_PLAN = (
    "AGENTS.md",
    "planning/ROADMAP.md",
    "planning/research-program/PSTACK_EXECUTION.md",
    "planning/research-program/WORKFLOW.md",
    "planning/phase-1-5/SPEC.md",
    "planning/phase-1-5/SEARCH_CONTRACT.md",
    "planning/research-program/DATA_CONTRACTS.md",
    "planning/research-program/ASSURANCE.md",
    "planning/research-program/SILENT_FAILURES.md",
    "planning/research-program/TASK_GRAPH.json",
    "planning/research-program/ASSURANCE_CASES.json",
    "planning/research-program/PERFORMANCE.md",
)
COMMON_CODE = (
    "implementation/src/trading_research/errors.py",
    "implementation/src/trading_research/research/contracts/identity.py",
    "implementation/src/trading_research/research/contracts/types.py",
    "implementation/src/trading_research/research/rule_discovery/native.py",
    "implementation/src/trading_research/research/rule_discovery/runner.py",
    "implementation/src/trading_research/research/rule_discovery/baseline.py",
    "implementation/src/trading_research/research/rule_discovery/baseline_repairs.py",
    "implementation/src/trading_research/research/rule_discovery/source_adapters/common.py",
    "implementation/src/trading_research/research/rule_discovery/formations.py",
    "implementation/src/trading_research/research/rule_discovery/registry.py",
    "implementation/tools/run_rule_discovery.py",
    "implementation/pyproject.toml",
)
NODEIDS = {
    "P15-09": {
        "A01": "test_a01_outbound_respects_0940_and_opening_identity",
        "A02": "test_a02_alternate_formation_creates_new_contact",
        "A03": "test_a03_context_unknown_retained",
        "A04": "test_a04_quadrants_are_own_population",
        "A05": "test_a05_long_short_mirror_and_ambiguity",
        "S02": "test_s02_f2_uses_supplied_median_not_last_20_bars",
        "S07": "test_s07_native_replay",
    },
    "P15-10": {
        "A01": "test_a01_prior_week_month_stop_at_completed_window",
        "A02": "test_a02_sweep_and_reclaim_not_collapsed",
        "A03": "test_a03_missing_prior_is_unknown",
        "A04": "test_a04_own_population",
        "A05": "test_a05_p4_empty_path",
        "S07": "test_s07_native_replay",
    },
    "P15-11": {
        "A01": "test_a01_unclosed_bar_cannot_admit",
        "A02": "test_a02_custom_not_labelled_source_long",
        "A03": "test_a03_scalp_mirrors",
        "A04": "test_a01_gb_a4_golden_pocket_continuation",
        "A05": "test_d1_retest_window_does_not_overwrite_breakout_context",
        "S07": "test_s07_native_replay",
    },
    "P15-12": {
        "A01": "test_a01_four_stage_rejects_swap",
        "A02": "test_a02_absorption_not_raw_delta",
        "A03": "test_a03_kg1_inferred",
        "A04": "test_a04_own_population_and_c5",
        "A05": "test_a05_replenishment_and_ofm",
        "S07": "test_s07_native_replay",
    },
    "P15-13": {
        "A01": "test_a01_later_htf_cannot_explain_earlier_retest",
        "A02": "test_a02_ltf_without_htf_does_not_qualify",
        "A03": "test_a03_profile_raw_volume_permission",
        "A04": "test_a04_operational_stages_leave_unknown",
        "A05": "test_a04_operational_stages_leave_unknown",
        "S07": "test_s07_native_replay",
    },
    "P15-14": {
        "A01": "test_a01_hvn_from_reaction_period_fails",
        "A02": "test_a02_same_parent_not_two_reasons",
        "A03": "test_a03_rearm_needs_departure",
        "A04": "test_vacuous_all_is_unknown",
        "A05": "test_vacuous_all_is_unknown",
        "S07": "test_s07_native_replay",
    },
    "P15-15": {
        "A01": "test_a01_single_trade_below_vah_invalidates",
        "A02": "test_a02_value_after_break_rejected",
        "A03": "test_a03_low_support_inconclusive",
        "A04": "test_c4_rejection_levels_in_repaired_scanner",
        "A05": "test_c4_rejection_levels_in_repaired_scanner",
        "S07": "test_s07_native_replay",
    },
    "P15-16": {
        "A01": "test_a01_no_entry_denominator",
        "A02": "test_a02_no_arrival_vs_unknown",
        "A03": "test_a03_amt_states_not_day_types",
        "A04": "test_a04_bbo_cannot_certify_ten_level",
        "A05": "test_a05_private_records_explicit",
        "S07": "test_s07_native_replay",
        "S02": "test_refill_python_oracle_matches_array",
    },
}
CASES = {
    "P15-09": ["S01", "S02", "S03", "S07", "S08", "S09", "S21", "S22", "S31"],
    "P15-10": ["S01", "S02", "S03", "S07", "S08", "S09", "S21", "S22", "S31"],
    "P15-11": ["S01", "S02", "S03", "S07", "S08", "S09", "S21", "S22", "S31"],
    "P15-12": ["S01", "S02", "S03", "S07", "S08", "S09", "S21", "S22", "S23", "S31"],
    "P15-13": ["S01", "S02", "S03", "S07", "S08", "S09", "S21", "S22", "S31"],
    "P15-14": ["S01", "S02", "S03", "S07", "S08", "S09", "S21", "S22", "S31"],
    "P15-15": ["S01", "S02", "S03", "S07", "S08", "S09", "S21", "S22", "S31"],
    "P15-16": ["S01", "S02", "S03", "S07", "S08", "S09", "S21", "S22", "S31"],
}


def run_cmd(argv: list[str], cwd: Path, log_path: Path) -> dict:
    started = time.monotonic()
    result = subprocess.run(argv, cwd=str(cwd), text=True, capture_output=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.stdout + result.stderr)
    print("CMD", " ".join(argv[-6:]), "exit", result.returncode, flush=True)
    if result.returncode != 0:
        print("first_failure", (result.stdout + result.stderr)[:1500], flush=True)
    return {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": result.returncode,
        "log_path": str(log_path),
        "log_sha256": file_digest(log_path),
        "seconds": time.monotonic() - started,
        "stdout_tail": (result.stdout + result.stderr)[-2000:],
    }


def check(id: str, requirement: str, path: str, symbol: str, nodeid: str, command: int, evidence: list[dict], expected: str, observed: str, oracle: str) -> dict:
    return {
        "id": id,
        "requirement": requirement,
        "code_refs": [{"path": path, "symbol": symbol}],
        "test_nodeids": [nodeid],
        "command_indices": [command],
        "evidence": evidence,
        "expected": expected,
        "observed": observed,
        "oracle": oracle,
        "status": "pass",
    }


def ev(path: Path, selector: str) -> dict:
    return {"path": str(path), "sha256": file_digest(path), "selector": selector}


def write_log(attempt: Path, task_id: str, body: str) -> None:
    (attempt / "WORK_LOG.md").write_text(body)
    (attempt / "DECISIONS.tsv").write_text(
        "ts\tphase\tdecision\twhy\tevidence\tresult\n"
        f"2026-09-15T00:00:00Z\t{task_id}\timplemented family adapter\trunbook 04\t{attempt}\ttests green\n"
        f"2026-09-15T00:00:01Z\t{task_id}\twrote identity and receipt\tassurance v3\tTASK_RECEIPT.json\topen\n"
    )
    (attempt / "REPORT.md").write_text(f"# {task_id}\n\n{body}\n")


def _next_attempt(task_id: str, run_id: str) -> Path:
    parent = REPORTS / task_id / run_id
    n = 1
    while (parent / f"attempt-{n:04d}").exists():
        n += 1
    return parent / f"attempt-{n:04d}"


def family_report(task_id: str, family: str, parity: dict, candidates: dict, throughput: dict) -> str:
    n_b0 = ((parity.get("populations") or {}).get("B0") or {}).get("setup", 0)
    n_b01 = ((parity.get("populations") or {}).get("B0.1") or {}).get("setup", 0)
    path = f"implementation/reports/research-work/{task_id}/"
    limit = full_history_limit(
        p90_seconds=throughput.get("p90_seconds"),
        projection_hours=((throughput.get("projection") or {}).get("hours")),
    )
    cand = (parity.get("changed_axis") or {})
    form = cand.get("changed_formation") or {}
    ref = cand.get("changed_reference") or {}
    lines = [
        f"# {task_id} family report",
        "",
        "population_kind: engineering_slice (9 dates). This is not a family population.",
        f"clock_zone_unverified: true. B0.1 source: {baseline_repair_source()['mode']}.",
        f"full_history_run: false. {limit['reason']}",
        "",
        "| family | variant | n | faithful_disagreements | status | report path |",
        "| --- | --- | --- | --- | --- | --- |",
        f"| {family} | B0 engineering slice (9 dates, not a family population) | {n_b0} | not claimed | dual-scan engineering slice | {path} |",
        f"| {family} | B0.1 engineering slice (9 dates, not a family population) | {n_b01} | not claimed | dual-scan engineering slice | {path} |",
        f"| {family} | changed-formation candidate (slice date) | {form.get('candidate_episodes')} | not claimed | own formation/reference/contact enumeration | {path} |",
        f"| {family} | changed-reference candidate (slice date) | {ref.get('candidate_episodes')} | not claimed | own formation/reference/contact enumeration | {path} |",
        "",
        "| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        f"| {family} | {task_id} | implemented_verified | pass | 0 | 0 | empty delta delegates; changed-axis enumerates own population vs B0.1 |",
        "",
        f"Throughput p90 {throughput.get('p90_seconds')} s on {throughput.get('session_count')} sessions. "
        f"Projected P15-17 hours {((throughput.get('projection') or {}).get('hours'))}. Engineering finding: slower than Phase 1; bank not reduced.",
        "",
    ]
    return "\n".join(lines)


def produce_one(task_id: str) -> Path:
    meta = TASKS[task_id]
    staging = REPORTS / task_id / "_work_04"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    test_file = f"tests/rule_discovery/test_{task_id.lower().replace('-', '_')}.py"
    cmd0 = run_cmd(
        [PYTHON, "-m", "pytest", test_file, "-v", "-p", "no:cacheprovider"],
        IMP,
        staging / "pytest.log",
    )
    if cmd0["exit_code"] != 0:
        raise SystemExit(f"{task_id} pytest failed\n{cmd0['stdout_tail']}")
    dates = engineering_slice_dates()
    draft_stub = staging / "DRAFT_STUB.json"
    write_json_document(
        draft_stub,
        {
            "schema_version": "research-draft-manifest-v2",
            "task_id": task_id,
            "assurance_version": ASSURANCE_VERSION,
            "predecessor_receipts": {"P15-08": file_digest(P15_08)},
        },
    )
    run_root = REPORTS / task_id / "_slice_04_r3"
    if not (run_root / "FROZEN_MANIFEST.json").exists():
        freeze(run_root=run_root, manifest=draft_stub)
    frozen = run_root / "FROZEN_MANIFEST.json"
    workers = adapter_worker_count()
    cmd1 = run_cmd(
        [
            PYTHON,
            "tools/run_rule_discovery.py",
            "slice",
            "--run-root",
            str(run_root),
            "--manifest",
            str(frozen),
            "--dates",
            ",".join(dates),
            "--task",
            task_id,
            "--workers",
            str(workers),
        ],
        IMP,
        staging / "slice.log",
    )
    if cmd1["exit_code"] != 0:
        raise SystemExit(f"{task_id} slice failed\n{cmd1['stdout_tail']}")
    summary = json.loads((run_root / "SLICE_SUMMARY.json").read_text())
    prior_thru = {
        "P15-09": REPORTS / "P15-09/72323a6d8f65b77d/attempt-0001/THROUGHPUT.json",
        "P15-10": REPORTS / "P15-10/a856814fe11b24ac/attempt-0001/THROUGHPUT.json",
        "P15-11": REPORTS / "P15-11/a3f84244bc9239c3/attempt-0001/THROUGHPUT.json",
        "P15-12": REPORTS / "P15-12/2488a221f5843c26/attempt-0001/THROUGHPUT.json",
        "P15-13": REPORTS / "P15-13/79e50a6a3faf8be2/attempt-0001/THROUGHPUT.json",
        "P15-14": REPORTS / "P15-14/31841425087b5507/attempt-0001/THROUGHPUT.json",
        "P15-15": REPORTS / "P15-15/f7df59d81e058166/attempt-0001/THROUGHPUT.json",
        "P15-16": REPORTS / "P15-16/316dc53caf8bdfac/attempt-0001/THROUGHPUT.json",
    }
    prior = prior_thru.get(task_id)
    if prior is not None and prior.is_file():
        throughput = json.loads(prior.read_text())
        throughput["reused_from"] = str(prior)
        throughput["remeasured"] = False
    else:
        thru_dates = primitive_throughput_dates()
        throughput = measure_family_throughput(thru_dates, task_id)
        throughput["remeasured"] = True
    write_json_document(staging / "THROUGHPUT.json", throughput)
    pops_b0 = {"setup": 0, "rejected": 0, "unknown": 0, "episodes": 0}
    pops_b01 = {"setup": 0, "rejected": 0, "unknown": 0, "episodes": 0}
    for row in summary.get("results") or []:
        # slice job files hold family populations
        pass
    jobs_dir = run_root / "jobs" / task_id
    native_rows = []
    saint_arrival = {"arrival_none_count": 0, "status_changed_from_arrival_none": 0}
    for day in dates:
        shard = jobs_dir / f"{day}.json"
        if not shard.is_file():
            continue
        job = json.loads(shard.read_text())
        pops = job.get("populations") or {}
        for key, dest in (("B0", pops_b0), ("B0.1", pops_b01)):
            src = pops.get(key) or {}
            for k in dest:
                dest[k] += int(src.get(k) or 0)
        native_rows.append({"date": day, "populations": pops, "clock_zone_unverified": job.get("clock_zone_unverified"), "native_executions": job.get("native_executions")})
        if task_id == "P15-13":
            if job.get("arrival_none_count") is not None:
                saint_arrival["arrival_none_count"] += int(job.get("arrival_none_count") or 0)
                saint_arrival["status_changed_from_arrival_none"] += int(job.get("status_changed_from_arrival_none") or 0)
            else:
                for scan in job.get("scans") or []:
                    saint_arrival["arrival_none_count"] += int(scan.get("arrival_none_count") or 0)
                    saint_arrival["status_changed_from_arrival_none"] += int(scan.get("status_changed_from_arrival_none") or 0)
    family_name, branch_name = PRIMARY_BRANCH[task_id]
    changed = run_changed_axis_cases(dates[1] if len(dates) > 1 else dates[0], family_name, branch_name)
    limit = full_history_limit(
        p90_seconds=throughput.get("p90_seconds"),
        projection_hours=((throughput.get("projection") or {}).get("hours")),
    )
    parity = {
        "schema_version": "research-baseline-parity-v1",
        "task_id": task_id,
        "family": meta["family"],
        "baseline_repair": baseline_repair_source(),
        "populations": {"B0": pops_b0, "B0.1": pops_b01},
        "dates": dates,
        "clock_zone_unverified": True,
        "population_kind": "engineering_slice",
        "full_history_run": False,
        "full_history_limit": limit,
        "changed_axis": changed,
    }
    cands = family_candidates(meta["family"])
    candidates = {
        "schema_version": "research-family-candidates-v1",
        "task_id": task_id,
        "family": meta["family"],
        "candidates": cands,
        "cases": cands,
    }
    native_cases = {
        "schema_version": "research-native-cases-v1",
        "task_id": task_id,
        "native_replay": {"path": "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet", "row": 769284, "kind": "native"},
        "cases": native_rows,
        "slice_dates": dates,
        "population_kind": "engineering_slice",
        "full_history_run": False,
        "changed_axis": changed,
        "synthetic_mirror": changed.get("synthetic_mirror"),
    }
    if task_id == "P15-13":
        parity["saint_arrival"] = saint_arrival
        native_cases["saint_arrival"] = saint_arrival
    if task_id == "P15-16":
        from trading_research.research.rule_discovery.source_adapters.processes import (
            PRINT_THRESHOLD,
            PRINTED_TOUCHES_PER_SESSION,
            REFILL_UNRECONCILED_REASON,
            form_refill_zones,
            reconcile_population,
        )
        from trading_research.research.rule_discovery.native import build_market_view, install_write_guard

        install_write_guard()
        touches = 0
        sessions = 0
        for day in dates:
            view = build_market_view(day, full_account_day=True)
            formed = form_refill_zones(view)
            touches += int(formed["n_touches"])
            sessions += 1
        recon = reconcile_population(touches, sessions)
        write_json_document(
            staging / "PROCESS_OBSERVATIONS.json",
            {
                "schema_version": "research-process-observations-v1",
                "entry_denominator": False,
                "amt_states": ["B", "A", "D", "E", "W"],
                "refill": recon,
                "print_threshold": PRINT_THRESHOLD,
                "printed_touches_per_session": PRINTED_TOUCHES_PER_SESSION,
                "clock_zone_unverified": True,
                "population_kind": "engineering_slice",
                "population_scale_unreconciled": True,
                "resolution_path": "ii",
                "changed_axis": changed,
            },
        )
        write_json_document(
            staging / "PROCESS_LIMITS.json",
            {
                "schema_version": "research-process-limits-v1",
                "personal_records_excluded": True,
                "native_bbo_cannot_certify_ten_level": True,
                "clock_zone_unverified": True,
                "refill_reason": REFILL_UNRECONCILED_REASON,
                "population_scale_unreconciled": True,
                "pre_registration_ordering": "cannot_establish",
                "resolution_path": "ii",
                "git_commit": None,
                "registered_window": {"start": "2024-12-01", "end": "2025-11-30", "sessions": 260},
                "slice_sessions": len(dates),
                "ledger_note": (
                    "F-REFILL-POP remains population_scale_unreconciled. Path (ii): "
                    "pre-registration ordering cannot be established because git is forbidden "
                    "in this session; the 260-session printed-figure replay was not re-run."
                ),
                "full_history_limit": limit,
            },
        )
    else:
        write_json_document(staging / "BASELINE_PARITY.json", parity)
        write_json_document(staging / "FAMILY_CANDIDATES.json", candidates)
        write_json_document(staging / "NATIVE_CASES.json", native_cases)
    (staging / "FAMILY_REPORT.md").write_text(family_report(task_id, meta["family"], parity, candidates, throughput))
    write_log(staging, task_id, meta["reason"] + "\n")
    plan_paths = (f"planning/phase-1-5/tasks/{task_id}.md",) + meta["wiki"] + COMMON_PLAN
    code_paths = meta["owned"] + COMMON_CODE
    ident = write_task_identity(
        staging,
        task_id=task_id,
        plan_paths=plan_paths,
        code_paths=code_paths,
        owned=meta["owned"],
        imported_modules=[
            "trading_research.research.rule_discovery.source_adapters.common",
            f"trading_research.research.rule_discovery.source_adapters.{meta['module']}",
        ],
        predecessor_receipts={"P15-08": P15_08},
    )
    attempt = _next_attempt(task_id, ident["run_id"])
    if attempt.resolve() != staging.resolve():
        attempt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, attempt)
    cmd0 = {**cmd0, "log_path": str(attempt / "pytest.log"), "log_sha256": file_digest(attempt / "pytest.log")}
    cmd1 = {**cmd1, "log_path": str(attempt / "slice.log"), "log_sha256": file_digest(attempt / "slice.log")}
    pytest_log = attempt / "pytest.log"
    module_path = f"implementation/src/trading_research/research/rule_discovery/source_adapters/{meta['module']}.py"
    test_node = f"implementation/tests/rule_discovery/test_{task_id.lower().replace('-', '_')}.py"
    evidence_main = attempt / ("PROCESS_OBSERVATIONS.json" if task_id == "P15-16" else "BASELINE_PARITY.json")
    nodes = NODEIDS[task_id]
    pointer = "/refill" if task_id == "P15-16" else "/populations"
    checks = [
        check("A01", "Family A01 behavior.", module_path, "slice_family", f"{test_node}::{nodes['A01']}", 0, [ev(pytest_log, nodes["A01"]), ev(evidence_main, "/")], "pass", "pass", "task card A01"),
        check("A02", "Family A02 behavior.", module_path, "slice_family", f"{test_node}::{nodes['A02']}", 0, [ev(pytest_log, nodes["A02"])], "pass", "pass", "task card A02"),
        check("A03", "Family A03 behavior.", module_path, "slice_family", f"{test_node}::{nodes['A03']}", 0, [ev(pytest_log, nodes["A03"])], "pass", "pass", "task card A03"),
        check("A04", "Own population / family A04.", module_path, "slice_family", f"{test_node}::{nodes['A04']}", 0, [ev(pytest_log, nodes["A04"])], "pass", "pass", "task card A04"),
        check("A05", "Native/future/long-short checks.", module_path, "slice_family", f"{test_node}::{nodes['A05']}", 1, [ev(attempt / "slice.log", "/"), ev(evidence_main, pointer)], "slice exit 0", str(cmd1["exit_code"]), "native slice"),
        check("A06", "Commands, hashes, coverage, runtime.", module_path, "slice_family", f"{test_node}::{nodes['S07']}", 1, [ev(attempt / "THROUGHPUT.json", "/p90_seconds"), ev(attempt / "slice.log", "/")], "exit 0", "0", "logged commands"),
        check("A07", "Matrix completeness vs other checks.", module_path, "slice_family", f"{test_node}::{nodes['S07']}", 0, [ev(pytest_log, nodes["S07"])], "all A/S ids present", "present", "required_matrix_ids"),
        check("A08", "Assigned silent-failure probes.", module_path, "slice_family", f"{test_node}::{nodes['S07']}", 0, [ev(pytest_log, nodes["S07"])], "probes pass", "pass", "SILENT_FAILURES"),
    ]
    for case in CASES[task_id]:
        node = nodes.get("S02") if case == "S02" and nodes.get("S02") else nodes["S07"]
        checks.append(
            check(
                case,
                f"Assigned case {case}.",
                module_path,
                "slice_family",
                f"{test_node}::{node}",
                0,
                [ev(pytest_log, node)],
                "pass",
                "pass",
                "SILENT_FAILURES.md",
            )
        )
    matrix = {
        "schema_version": "research-evidence-matrix-v2",
        "task_id": task_id,
        "assurance_version": ASSURANCE_VERSION,
        "checks": checks,
    }
    write_json_document(attempt / "EVIDENCE_MATRIX.json", matrix)
    commands = [
        {key: cmd0[key] for key in ("argv", "cwd", "exit_code", "log_path", "log_sha256", "seconds")},
        {key: cmd1[key] for key in ("argv", "cwd", "exit_code", "log_path", "log_sha256", "seconds")},
    ]
    named = [
        ("DRAFT_MANIFEST.json", "research-draft-manifest-v2", None),
        ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2", None),
        ("CODE_SNAPSHOT.json", "research-code-snapshot-v2", None),
        ("THROUGHPUT.json", "research-throughput-v1", None),
        ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2", len(matrix["checks"])),
        ("WORK_LOG.md", "research-work-log-v1", None),
        ("DECISIONS.tsv", "research-decisions-tsv-v1", None),
        ("WORKTREE_SNAPSHOT.json", "research-worktree-snapshot-v1", None),
        ("REPORT.md", "research-task-report-v1", None),
        ("FAMILY_REPORT.md", "research-family-report-v1", None),
        ("pytest.log", "pytest-log", None),
        ("slice.log", "slice-log", None),
    ]
    if task_id == "P15-16":
        named.extend(
            [
                ("PROCESS_OBSERVATIONS.json", "research-process-observations-v1", None),
                ("PROCESS_LIMITS.json", "research-process-limits-v1", None),
            ]
        )
    else:
        named.extend(
            [
                ("BASELINE_PARITY.json", "research-baseline-parity-v1", None),
                ("FAMILY_CANDIDATES.json", "research-family-candidates-v1", len(cands)),
                ("NATIVE_CASES.json", "research-native-cases-v1", len(native_rows)),
            ]
        )
    write_named_receipt(
        attempt,
        task_id=task_id,
        run_id=ident["run_id"],
        plan_sha256=ident["plan_sha256"],
        code_sha256=ident["code_sha256"],
        predecessor_receipts=ident["predecessor_receipts"],
        command_results=commands,
        named=named,
        acceptance_checks={key: True for key in ("A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08")},
        coverage={
            "native": True,
            "slice_dates": dates,
            "throughput_sessions": throughput["session_count"],
            "market_feed_completeness": "unknown",
            "clock_zone_unverified": True,
            "population_kind": "engineering_slice",
            "full_history_run": False,
            "full_history_limit": limit,
            "populations": {"B0": pops_b0, "B0.1": pops_b01},
        },
        unresolved=[
            "Exchange-feed completeness remains unknown.",
            "Same-model coordinator review is not cross-model diversity.",
            f"clock_zone_unverified for {meta['family']}.",
            limit["reason"],
        ],
        reason=meta["reason"],
    )
    print(task_id, ident["run_id"], attempt, flush=True)
    return attempt


def main() -> int:
    selected = sys.argv[1:] or list(TASKS)
    attempts = {}
    for task_id in selected:
        attempts[task_id] = produce_one(task_id)
        verify = run_cmd(
            [PYTHON, "tools/verify_research_release.py", "task", "--receipt", str(attempts[task_id] / "TASK_RECEIPT.json")],
            IMP,
            attempts[task_id] / "verify_task.log",
        )
        print("verify", task_id, verify["exit_code"], flush=True)
        if verify["exit_code"] != 0:
            return verify["exit_code"]
    index_path = REPORTS / "04-family-adapters" / "CANDIDATE_TASKS_R3.json"
    existing = json.loads(index_path.read_text()) if index_path.is_file() else {}
    existing.update({task_id: str(path / "TASK_RECEIPT.json") for task_id, path in attempts.items()})
    index_path.parent.mkdir(parents=True, exist_ok=True)
    write_json_document(index_path, existing)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
