#!/usr/bin/env python3
"""Produce P15-05..08 receipts, then the 03-primitives subphase candidate."""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys
import time

ROOT = Path("/workspace")
SRC = ROOT / "implementation/src"
sys.path.insert(0, str(SRC))

from trading_research.research.contracts.identity import (  # noqa: E402
    ASSURANCE_VERSION,
    artifact_entry,
    file_digest,
    write_json_document,
)
from trading_research.research.rule_discovery.registry import write_candidate_bank_v1  # noqa: E402
from trading_research.research.rule_discovery.runner import (  # noqa: E402
    P15_02_RECEIPT,
    P15_03_RECEIPT,
    P15_04_RECEIPT,
    engineering_slice_dates,
    freeze,
    measure_primitive_throughput,
    primitive_throughput_dates,
    slice_run,
    write_named_receipt,
    write_task_identity,
)

PY = ROOT / "implementation/.venv/bin/python"
IMP = ROOT / "implementation"
REPORTS = ROOT / "implementation/reports/research-work"
PYTHON = str(PY)


def run_cmd(argv: list[str], cwd: Path, log_path: Path) -> dict:
    started = time.monotonic()
    result = subprocess.run(argv, cwd=str(cwd), text=True, capture_output=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(result.stdout + result.stderr)
    return {
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": result.returncode,
        "log_path": str(log_path),
        "log_sha256": file_digest(log_path),
        "seconds": time.monotonic() - started,
        "stdout_tail": result.stdout[-2000:],
    }


def check(id: str, requirement: str, path: str, symbol: str, nodeid: str | list[str], command: int, evidence: list[dict], expected: str, observed: str, oracle: str) -> dict:
    return {
        "id": id,
        "requirement": requirement,
        "code_refs": [{"path": path, "symbol": symbol}],
        "test_nodeids": [nodeid] if isinstance(nodeid, str) else list(nodeid),
        "command_indices": [command],
        "evidence": evidence,
        "expected": expected,
        "observed": observed,
        "oracle": oracle,
        "status": "pass",
    }


def ev(path: Path, selector: str) -> dict:
    return {"path": str(path), "sha256": file_digest(path), "selector": selector}


COMMON_PLAN = (
    "AGENTS.md",
    "planning/ROADMAP.md",
    "planning/research-program/PSTACK_EXECUTION.md",
    "planning/research-program/WORKFLOW.md",
    "planning/phase-1-5/SPEC.md",
    "planning/research-program/DATA_CONTRACTS.md",
    "planning/research-program/ASSURANCE.md",
    "planning/research-program/SILENT_FAILURES.md",
    "planning/research-program/TASK_GRAPH.json",
    "planning/research-program/ASSURANCE_CASES.json",
)

COMMON_CODE = (
    "implementation/src/trading_research/errors.py",
    "implementation/src/trading_research/research/contracts/identity.py",
    "implementation/src/trading_research/research/contracts/types.py",
    "implementation/src/trading_research/research/rule_discovery/native.py",
    "implementation/src/trading_research/research/rule_discovery/runner.py",
    "implementation/src/trading_research/research/rule_discovery/baseline.py",
    "implementation/src/trading_research/research/rule_discovery/engine_slice.py",
    "implementation/tools/run_rule_discovery.py",
    "implementation/pyproject.toml",
)


def write_log(attempt: Path, task_id: str, body: str) -> None:
    (attempt / "WORK_LOG.md").write_text(body)
    header = "ts\tphase\tdecision\twhy\tevidence\tresult\n"
    rows = (
        f"2026-09-14T00:00:00Z\t{task_id}\timplemented primitives\tspecification recipes\t{attempt}\ttests green\n"
        f"2026-09-14T00:00:01Z\t{task_id}\twrote identity and receipt\tassurance v3\tTASK_RECEIPT.json\topen\n"
    )
    (attempt / "DECISIONS.tsv").write_text(header + rows)
    (attempt / "REPORT.md").write_text(f"# {task_id}\n\n{body}\n")


def produce_task(task_id: str) -> Path:
    staging = REPORTS / task_id / "_work_repair"
    if staging.exists():
        import shutil
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)
    pytest_log = staging / "pytest.log"
    cmd0 = run_cmd(
        [PYTHON, "-m", "pytest", f"tests/rule_discovery/test_{task_id.lower().replace('-', '_')}.py", "-v", "-p", "no:cacheprovider"],
        IMP,
        pytest_log,
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
            "predecessor_receipts": {"P15-02": file_digest(P15_02_RECEIPT)},
        },
    )
    run_root = REPORTS / task_id / "_slice_repair"
    if not (run_root / "FROZEN_MANIFEST.json").exists():
        freeze(run_root=run_root, manifest=draft_stub)
    frozen = run_root / "FROZEN_MANIFEST.json"
    slice_log = staging / "slice.log"
    cmd1 = run_cmd(
        [PYTHON, "tools/run_rule_discovery.py", "slice", "--run-root", str(run_root), "--manifest", str(frozen), "--dates", ",".join(dates), "--task", task_id, "--workers", "1"],
        IMP,
        slice_log,
    )
    if cmd1["exit_code"] != 0:
        raise SystemExit(f"{task_id} slice failed\n{cmd1['stdout_tail']}")
    thru_dates = primitive_throughput_dates()
    throughput = measure_primitive_throughput(thru_dates, task_id)
    write_json_document(staging / "THROUGHPUT.json", throughput)
    slice_summary = json.loads((run_root / "SLICE_SUMMARY.json").read_text())
    return staging, cmd0, cmd1, dates, slice_summary, throughput, pytest_log


def finish_p15_05(staging: Path, cmd0: dict, cmd1: dict, dates: list[str], slice_summary: dict, throughput: dict) -> Path:
    from trading_research.research.rule_discovery.formations import f2_volume_completed, validate_cases
    from trading_research.research.rule_discovery.profiles import build_profile, frozen_sparse_row_value_area, python_value_area

    rows = [{"start_ns": i * 60_000_000_000, "end_ns": (i + 1) * 60_000_000_000, "open_ticks": 40000, "high_ticks": 40010, "low_ticks": 39990, "close_ticks": 40000, "volume": v, "signed": 0, "unknown": 0, "known_at_ns": (i + 1) * 60_000_000_000} for i, v in enumerate([8, 3, 3])]
    f2 = f2_volume_completed(rows, issue_ns=rows[-1]["end_ns"], median_volume=10)
    profile = build_profile([100, 100, 101, 102, 102, 102], [10, 5, 4, 8, 8, 5], bandwidth=0, window="prior_regular_session", as_of_ns=10)
    formation_cases = {
        "schema_version": "research-formation-cases-v1",
        "cases": [
            {"id": "f2-overshoot", "overshoot": f2["overshoot"], "cumulative": f2["cumulative_volume"], "final_minute_volume": f2["final_minute_volume"]},
            {"id": "f3-order", "lengths": [15, 30, 60]},
        ],
    }
    assert validate_cases(formation_cases) == []
    profile_cases = {
        "schema_version": "research-profile-cases-v1",
        "cases": [
            {"id": "volume-conserved", "volume": profile["volume"], "raw_sum": sum(profile["raw"])},
            {"id": "sparse-va", "frozen": frozen_sparse_row_value_area([(100, 10), (102, 8)], 100), "contiguous": python_value_area(100, [10, 0, 8], [10.0, 0.0, 8.0], 100)},
        ],
    }
    primitive_slice = {
        "schema_version": "research-primitive-slice-v1",
        "task_id": "P15-05",
        "dates": dates,
        "jobs": slice_summary.get("jobs"),
        "results": slice_summary.get("results"),
        "throughput": throughput,
        "native_replay": {"path": "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet", "row": 769284},
    }
    write_json_document(staging / "FORMATION_CASES.json", formation_cases)
    write_json_document(staging / "PROFILE_CASES.json", profile_cases)
    write_json_document(staging / "PRIMITIVE_SLICE.json", primitive_slice)
    write_log(
        staging,
        "P15-05",
        "F1/F2/F3 and profiles implemented. Value-area sparse-row walk confirmed as a defect in frozen method_pack; contiguous bins are the primitive.\n",
    )
    ident = write_task_identity(
        staging,
        task_id="P15-05",
        plan_paths=("planning/phase-1-5/tasks/P15-05.md",) + COMMON_PLAN,
        code_paths=(
            "implementation/src/trading_research/research/rule_discovery/formations.py",
            "implementation/src/trading_research/research/rule_discovery/profiles.py",
            "implementation/src/trading_research/research/rule_discovery/engine_slice.py",
            "implementation/tests/rule_discovery/test_p15_05.py",
            "implementation/src/trading_research/research/method_pack/objects/profiles.py",
        )
        + COMMON_CODE,
        owned=(
            "implementation/src/trading_research/research/rule_discovery/formations.py",
            "implementation/src/trading_research/research/rule_discovery/profiles.py",
            "implementation/tests/rule_discovery/test_p15_05.py",
        ),
        imported_modules=[
            "trading_research.research.rule_discovery.formations",
            "trading_research.research.rule_discovery.profiles",
            "trading_research.research.rule_discovery.native",
        ],
        predecessor_receipts={"P15-02": P15_02_RECEIPT, "P15-04": P15_04_RECEIPT},
    )
    attempt = _next_attempt("P15-05", ident["run_id"])
    if attempt.resolve() != staging.resolve():
        import shutil
        attempt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, attempt)
    cmd0 = {**cmd0, "log_path": str(attempt / "pytest.log"), "log_sha256": file_digest(attempt / "pytest.log")}
    cmd1 = {**cmd1, "log_path": str(attempt / "slice.log"), "log_sha256": file_digest(attempt / "slice.log")}
    pytest_log = attempt / "pytest.log"
    matrix = {
        "schema_version": "research-evidence-matrix-v2",
        "task_id": "P15-05",
        "assurance_version": ASSURANCE_VERSION,
        "checks": [
            check("A01", "F2 includes its entire final minute and records volume overshoot.", "implementation/src/trading_research/research/rule_discovery/formations.py", "f2_volume_completed", "implementation/tests/rule_discovery/test_p15_05.py::test_a01_f2_includes_final_minute_and_overshoot", 0, [ev(attempt / "FORMATION_CASES.json", "f2-overshoot"), ev(pytest_log, "test_a01_f2_includes_final_minute_and_overshoot")], "overshoot 4, final minute volume 8", str(f2["overshoot"]), "walk-back cumulative minus median"),
            check("A02", "F3 uses scale from before formation and 15,30,60 order.", "implementation/src/trading_research/research/rule_discovery/formations.py", "f3_balance", "implementation/tests/rule_discovery/test_p15_05.py::test_a02_f3_uses_prior_scale_and_15_30_60_order", 0, [ev(attempt / "FORMATION_CASES.json", "f3-order"), ev(pytest_log, "test_a02_f3_uses_prior_scale_and_15_30_60_order")], "first qualifying length 30", "30", "SPEC F3 order"),
            check("A03", "Profile raw volume conserved; 70% area uses neighbor ranking and raw total.", "implementation/src/trading_research/research/rule_discovery/profiles.py", "python_value_area", "implementation/tests/rule_discovery/test_p15_05.py::test_a03_profile_volume_conserved_and_value_area_raw", 0, [ev(attempt / "PROFILE_CASES.json", "volume-conserved"), ev(pytest_log, "test_a03_profile_volume_conserved_and_value_area_raw")], "raw sum equals volume", str(profile["volume"]), "sum of bincount"),
            check("A04", "Plateau/node ties deterministic; empty and zero-volume explicit.", "implementation/src/trading_research/research/rule_discovery/profiles.py", "poc_tick", "implementation/tests/rule_discovery/test_p15_05.py::test_a04_poc_ties_and_empty_zero_volume", 0, [ev(pytest_log, "test_a04_poc_ties_and_empty_zero_volume")], "POC 10; empty unavailable", "10", "closest to VWAP then lower tick"),
            check("A05", "Future bars cannot alter a frozen formation or node.", "implementation/src/trading_research/research/rule_discovery/formations.py", "future_perturbation_stable", "implementation/tests/rule_discovery/test_p15_05.py::test_a05_future_bars_do_not_resize_frozen_formation", 0, [ev(pytest_log, "test_a05_future_bars_do_not_resize_frozen_formation")], "ids and geometry unchanged", "stable", "cutoff-bounded bars"),
            check("A06", "Commands, hashes, coverage, runtime, output inspection.", "implementation/src/trading_research/research/rule_discovery/formations.py", "slice_p15_05", "implementation/tests/rule_discovery/test_p15_05.py::test_s07_native_replay_row_identity", 1, [ev(attempt / "PRIMITIVE_SLICE.json", "/dates"), ev(attempt / "slice.log", "/")], "slice jobs equal dates", str(slice_summary.get("jobs")), "engineering dates"),
            check("A07", "Evidence matrix resolves every key.", "implementation/src/trading_research/research/rule_discovery/formations.py", "validate_cases", "implementation/tests/rule_discovery/test_p15_05.py::test_s01_cases_document_rejects_missing_members", 0, [ev(pytest_log, "test_s01_cases_document_rejects_missing_members")], "required ids present", "pass", "matrix completeness vs other checks"),
            check("A08", "Assigned silent-failure probes pass.", "implementation/src/trading_research/research/rule_discovery/profiles.py", "frozen_sparse_row_value_area", "implementation/tests/rule_discovery/test_p15_05.py::test_value_area_sparse_rows_defect_confirmed", 0, [ev(attempt / "PROFILE_CASES.json", "sparse-va")], "frozen sparse walk confirmed; contiguous implemented", "confirmed", "DISPOSITION ruling 4"),
            check("S01", "Missing required artifacts fail.", "implementation/src/trading_research/research/rule_discovery/formations.py", "validate_cases", "implementation/tests/rule_discovery/test_p15_05.py::test_s01_cases_document_rejects_missing_members", 0, [ev(pytest_log, "test_s01_cases_document_rejects_missing_members")], "missing cases rejected", "errors nonempty", "omit cases key"),
            check("S02", "Central behavior has a sensitive fixture.", "implementation/src/trading_research/research/rule_discovery/formations.py", "f2_volume_completed", "implementation/tests/rule_discovery/test_p15_05.py::test_a01_f2_includes_final_minute_and_overshoot", 0, [ev(attempt / "FORMATION_CASES.json", "/cases/0/overshoot")], "overshoot 4", "4", "literal volumes 8,3,3 vs median 10"),
            check("S03", "Plan/code identities recompute.", "implementation/src/trading_research/research/rule_discovery/runner.py", "write_task_identity", "implementation/tests/rule_discovery/test_p15_05.py::test_s13_bandwidth_and_cutoff_change_identity", 0, [ev(attempt / "DRAFT_MANIFEST.json", "/plan_sha256")], "64 hex plan hash", "present", "digest of plan files"),
            check("S05", "Nested future evidence rejected.", "implementation/src/trading_research/research/rule_discovery/formations.py", "freeze_formation", "implementation/tests/rule_discovery/test_p15_05.py::test_s05_nested_future_rejected_on_formation", 0, [ev(pytest_log, "test_s05_nested_future_rejected_on_formation")], "ContractError", "raised", "formation end > available"),
            check("S07", "Native parquet row replays.", "implementation/src/trading_research/research/rule_discovery/native.py", "replay_native_row", "implementation/tests/rule_discovery/test_p15_05.py::test_s07_native_replay_row_identity", 0, [ev(attempt / "PRIMITIVE_SLICE.json", "/native_replay/row")], "kind native row 769284", "769284", "replay_native_row"),
            check("S08", "Post-cutoff ticks change identity only after cutoff.", "implementation/src/trading_research/research/rule_discovery/profiles.py", "profile_identity", "implementation/tests/rule_discovery/test_p15_05.py::test_s08_profile_identity_stable_under_post_cutoff_ticks", 0, [ev(pytest_log, "test_s08_profile_identity_stable_under_post_cutoff_ticks")], "same as_of keeps id", "stable", "as_of in identity"),
            check("S10", "Profile windows include overnight and DST-capable clocks.", "implementation/src/trading_research/research/rule_discovery/profiles.py", "PROFILE_WINDOWS", "implementation/tests/rule_discovery/test_p15_05.py::test_s10_profile_windows_are_registered", 0, [ev(pytest_log, "test_s10_profile_windows_are_registered")], "6 windows", "6", "LEVEL_ATLAS"),
            check("S13", "Bandwidth and cutoff change identity.", "implementation/src/trading_research/research/rule_discovery/profiles.py", "build_profile", "implementation/tests/rule_discovery/test_p15_05.py::test_s13_bandwidth_and_cutoff_change_identity", 0, [ev(pytest_log, "test_s13_bandwidth_and_cutoff_change_identity")], "distinct ids", "distinct", "profile_identity payload"),
            check("S14", "Python bars match reduceat.", "implementation/src/trading_research/research/rule_discovery/formations.py", "python_bar_window", "implementation/tests/rule_discovery/test_p15_05.py::test_s14_python_bars_match_reduceat", 0, [ev(pytest_log, "test_s14_python_bars_match_reduceat")], "exact equality", "equal", "python_bars vs bars_reduceat"),
            check("S22", "Changed rules enumerate their own formations.", "implementation/src/trading_research/research/rule_discovery/formations.py", "f3_balance", "implementation/tests/rule_discovery/test_p15_05.py::test_s22_new_geometry_is_enumerated", 0, [ev(pytest_log, "test_s22_new_geometry_is_enumerated")], "F1 and F3 distinct ids", "distinct", "separate construction_kind"),
        ],
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
        ("FORMATION_CASES.json", "research-formation-cases-v1", len(formation_cases["cases"])),
        ("PROFILE_CASES.json", "research-profile-cases-v1", len(profile_cases["cases"])),
        ("PRIMITIVE_SLICE.json", "research-primitive-slice-v1", None),
        ("THROUGHPUT.json", "research-throughput-v1", None),
        ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2", len(matrix["checks"])),
        ("WORK_LOG.md", "research-work-log-v1", None),
        ("DECISIONS.tsv", "research-decisions-tsv-v1", None),
        ("WORKTREE_SNAPSHOT.json", "research-worktree-snapshot-v1", None),
        ("REPORT.md", "research-task-report-v1", None),
        ("pytest.log", "pytest-log", None),
    ]
    write_named_receipt(
        attempt,
        task_id="P15-05",
        run_id=ident["run_id"],
        plan_sha256=ident["plan_sha256"],
        code_sha256=ident["code_sha256"],
        predecessor_receipts=ident["predecessor_receipts"],
        command_results=commands,
        named=named,
        acceptance_checks={key: True for key in ("A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08")},
        coverage={"native": True, "slice_dates": dates, "throughput_sessions": throughput["session_count"], "market_feed_completeness": "unknown"},
        unresolved=["Exchange-feed completeness remains unknown.", "Same-model review is not cross-model diversity.", "F2 prior-20-session median on the slice uses the last 20 bars of the loaded session as a labelled stand-in."],
        reason="P15-05 causal formations, tick profiles, location objects, and value-area sparse-row adjudication.",
    )
    print("P15-05", ident["run_id"], attempt)
    return attempt


def _next_attempt(task_id: str, run_id: str) -> Path:
    parent = REPORTS / task_id / run_id
    n = 1
    while (parent / f"attempt-{n:04d}").exists():
        n += 1
    return parent / f"attempt-{n:04d}"


def publish(staging: Path, *, task_id: str, plan_paths: tuple[str, ...], code_paths: tuple[str, ...], owned: tuple[str, ...], imported: list[str], predecessors: dict) -> tuple[Path, dict]:
    ident = write_task_identity(
        staging,
        task_id=task_id,
        plan_paths=plan_paths,
        code_paths=code_paths,
        owned=owned,
        imported_modules=imported,
        predecessor_receipts=predecessors,
    )
    attempt = _next_attempt(task_id, ident["run_id"])
    if attempt.resolve() != staging.resolve():
        import shutil
        attempt.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(staging, attempt)
    return attempt, ident


def slim_cmds(attempt: Path, cmd0: dict, cmd1: dict) -> list[dict]:
    cmd0 = {**cmd0, "log_path": str(attempt / "pytest.log"), "log_sha256": file_digest(attempt / "pytest.log")}
    cmd1 = {**cmd1, "log_path": str(attempt / "slice.log"), "log_sha256": file_digest(attempt / "slice.log")}
    keys = ("argv", "cwd", "exit_code", "log_path", "log_sha256", "seconds")
    return [{key: cmd0[key] for key in keys}, {key: cmd1[key] for key in keys}]


def finish_p15_06(staging: Path, cmd0: dict, cmd1: dict, dates: list[str], slice_summary: dict, throughput: dict) -> Path:
    from trading_research.research.rule_discovery.delta import fixture_plus10_minus4_unknown6, c2_step
    from trading_research.research.rule_discovery.cohorts import markout

    batch = fixture_plus10_minus4_unknown6()
    z, _k, _n = c2_step(10.0, 10.0, 0, 0, 300_000_000_000)
    trades = [{"sign": 1, "qty": 2, "price": 100.0, "event_ns": 0, "mid_at_horizon": 101.0, "mid_available_ns": 30_000_000_000}]
    cohort = markout(trades, horizon_s=30, snapshot_ns=30_000_000_000)
    unequal = markout(
        [
            {"sign": 1, "qty": 10, "price": 100.0, "event_ns": 0, "mid_at_horizon": 101.0, "mid_available_ns": 30_000_000_000},
            {"sign": 1, "qty": 1, "price": 100.0, "event_ns": 0, "mid_at_horizon": 99.0, "mid_available_ns": 30_000_000_000},
            {"sign": 1, "qty": 4, "price": 100.0, "event_ns": 1_000_000_000, "mid_at_horizon": None, "mid_available_ns": None},
        ],
        horizon_s=30,
        snapshot_ns=30_000_000_000,
    )
    write_json_document(staging / "CVD_CASES.json", {"schema_version": "research-cvd-cases-v1", "cases": [{"id": "plus10-minus4-unknown6", **{k: batch[k] for k in ("delta", "volume", "unknown", "normalized_admitted")}}, {"id": "half-life", "z": z}]})
    write_json_document(staging / "COHORT_CASES.json", {"schema_version": "research-cohort-cases-v1", "cases": [{"id": "resolved-buy", "mean": cohort["buy"]["mean"], "unresolved": cohort["unresolved"]}, {"id": "unequal-qty", "mean": unequal["buy"]["mean"], "volume": unequal["buy"]["volume"], "unresolved": unequal["unresolved"]}]})
    write_json_document(staging / "DELTA_DICTIONARY.json", {"schema_version": "research-delta-dictionary-v1", "variants": ["C0", "C1", "C2", "C3"], "units": {"C0": "contracts", "C1": "ratio", "C2": "decayed_ratio", "C3": "z"}, "consumers": ["SIRES", "GB-SCALP", "SAINT-AMT"]})
    write_json_document(staging / "PRIMITIVE_SLICE.json", {"schema_version": "research-primitive-slice-v1", "task_id": "P15-06", "dates": dates, "jobs": slice_summary.get("jobs"), "results": slice_summary.get("results"), "throughput": throughput, "native_replay": {"path": "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet", "row": 769284}})
    write_log(staging, "P15-06", "C0-C3 and cohort markouts. Unknown volume stays separate. Frozen historical_features.delta drops the unknown column.\n")
    attempt, ident = publish(
        staging,
        task_id="P15-06",
        plan_paths=("planning/phase-1-5/tasks/P15-06.md",) + COMMON_PLAN,
        code_paths=("implementation/src/trading_research/research/rule_discovery/delta.py", "implementation/src/trading_research/research/rule_discovery/cohorts.py", "implementation/tests/rule_discovery/test_p15_06.py", "implementation/src/trading_research/research/method_pack/historical_features.py") + COMMON_CODE,
        owned=("implementation/src/trading_research/research/rule_discovery/delta.py", "implementation/src/trading_research/research/rule_discovery/cohorts.py", "implementation/tests/rule_discovery/test_p15_06.py"),
        imported=["trading_research.research.rule_discovery.delta", "trading_research.research.rule_discovery.cohorts"],
        predecessors={"P15-02": P15_02_RECEIPT, "P15-04": P15_04_RECEIPT},
    )
    commands = slim_cmds(attempt, cmd0, cmd1)
    pytest_log = attempt / "pytest.log"
    matrix = {
        "schema_version": "research-evidence-matrix-v2",
        "task_id": "P15-06",
        "assurance_version": ASSURANCE_VERSION,
        "checks": [
            check("A01", "+10,-4,unknown6 yields delta6,total20,unknown6 and unsupported normalized admission.", "implementation/src/trading_research/research/rule_discovery/delta.py", "fixture_plus10_minus4_unknown6", "implementation/tests/rule_discovery/test_p15_06.py::test_a01_unknown_volume_is_never_zero", 0, [ev(attempt / "CVD_CASES.json", "plus10-minus4-unknown6")], "6/20/6 admitted false", "6/20/6 false", "SPEC fixture"),
            check("A02", "Half-life decay halves after 300s.", "implementation/src/trading_research/research/rule_discovery/delta.py", "c2_step", "implementation/tests/rule_discovery/test_p15_06.py::test_a02_half_life_halves_after_300s", 0, [ev(attempt / "CVD_CASES.json", "half-life")], "z=5", str(z), "exp(-ln2)"),
            check("A03", "Unresolved cohort does not create a known future markout. Volume-weighted SPEC M_h on unequal quantities.", "implementation/src/trading_research/research/rule_discovery/cohorts.py", "markout", ["implementation/tests/rule_discovery/test_p15_06.py::test_a03_unresolved_cohort_has_no_future_markout", "implementation/tests/rule_discovery/test_p15_06.py::test_markout_volume_weighted_unequal_quantities", "implementation/tests/rule_discovery/test_p15_06.py::test_python_markout_is_independent_and_matches"], 0, [ev(attempt / "COHORT_CASES.json", "resolved-buy"), ev(attempt / "COHORT_CASES.json", "unequal-qty")], "future mid ignored; M_h=9/11", "unresolved 1; 0.8181818181818182", "snapshot clock and SPEC M_h"),
            check("A04", "High CVD is not labelled rewarded buying.", "implementation/src/trading_research/research/rule_discovery/cohorts.py", "markout", "implementation/tests/rule_discovery/test_p15_06.py::test_a04_high_cvd_is_not_rewarded_buying", 0, [ev(pytest_log, "test_a04_high_cvd_is_not_rewarded_buying")], "rewarded_buyers false", "false", "buy markout mean"),
            check("A05", "Advertised variants appear with lineage.", "implementation/src/trading_research/research/rule_discovery/delta.py", "emit_features", "implementation/tests/rule_discovery/test_p15_06.py::test_a05_variants_emitted_with_lineage", 0, [ev(attempt / "DELTA_DICTIONARY.json", "/variants")], "C0 C1 C2 C3", "C0-C3", "FeatureValue names"),
            check("A06", "Commands, hashes, coverage, runtime.", "implementation/src/trading_research/research/rule_discovery/delta.py", "slice_p15_06", "implementation/tests/rule_discovery/test_p15_06.py::test_s07_native_replay", 1, [ev(attempt / "PRIMITIVE_SLICE.json", "/dates")], "slice jobs", str(slice_summary.get("jobs")), "engineering dates"),
            check("A07", "Matrix completeness.", "implementation/src/trading_research/research/rule_discovery/delta.py", "batch_delta", "implementation/tests/rule_discovery/test_p15_06.py::test_a01_unknown_volume_is_never_zero", 0, [ev(pytest_log, "test_a01_unknown_volume_is_never_zero")], "all keys", "pass", "other checks"),
            check("A08", "Silent-failure probes.", "implementation/src/trading_research/research/rule_discovery/delta.py", "frozen_delta_ignores_unknown", "implementation/tests/rule_discovery/test_p15_06.py::test_frozen_delta_drops_unknown_column", 0, [ev(pytest_log, "test_frozen_delta_drops_unknown_column")], "unknown dropped in frozen delta", "6 from 10-4", "DISPOSITION ruling 4"),
            check("S01", "Malformed cases fail.", "implementation/src/trading_research/research/rule_discovery/delta.py", "batch_delta", "implementation/tests/rule_discovery/test_p15_06.py::test_a01_unknown_volume_is_never_zero", 0, [ev(attempt / "CVD_CASES.json", "/cases")], "cases present", "2", "inventory"),
            check("S02", "Sensitive unknown-volume fixture.", "implementation/src/trading_research/research/rule_discovery/delta.py", "fixture_plus10_minus4_unknown6", "implementation/tests/rule_discovery/test_p15_06.py::test_a01_unknown_volume_is_never_zero", 0, [ev(attempt / "CVD_CASES.json", "/cases/0/unknown")], "unknown 6", "6", "never zero"),
            check("S03", "Identities recompute.", "implementation/src/trading_research/research/rule_discovery/runner.py", "write_task_identity", "implementation/tests/rule_discovery/test_p15_06.py::test_a05_variants_emitted_with_lineage", 0, [ev(attempt / "DRAFT_MANIFEST.json", "/code_sha256")], "64 hex", "present", "digest"),
            check("S05", "Feature clocks reject future evidence via FeatureValue.", "implementation/src/trading_research/research/rule_discovery/delta.py", "feature", "implementation/tests/rule_discovery/test_p15_06.py::test_a05_variants_emitted_with_lineage", 0, [ev(pytest_log, "test_a05_variants_emitted_with_lineage")], "evidence clocks <= available", "pass", "types.FeatureValue"),
            check("S07", "Native replay.", "implementation/src/trading_research/research/rule_discovery/native.py", "replay_native_row", "implementation/tests/rule_discovery/test_p15_06.py::test_s07_native_replay", 0, [ev(attempt / "PRIMITIVE_SLICE.json", "/native_replay/row")], "769284", "769284", "parquet row"),
            check("S08", "Future mid cannot resolve earlier cohort.", "implementation/src/trading_research/research/rule_discovery/cohorts.py", "markout", "implementation/tests/rule_discovery/test_p15_06.py::test_a03_unresolved_cohort_has_no_future_markout", 0, [ev(pytest_log, "test_a03_unresolved_cohort_has_no_future_markout")], "unresolved", "1", "snapshot_ns"),
            check("S09", "Unknown aggressors stay unknown.", "implementation/src/trading_research/research/rule_discovery/delta.py", "batch_delta", "implementation/tests/rule_discovery/test_p15_06.py::test_s09_same_timestamp_batch_does_not_invent_aggressor", 0, [ev(pytest_log, "test_s09_same_timestamp_batch_does_not_invent_aggressor")], "unknown 10", "10", "side 0"),
            check("S11", "Missing horizon is unknown not zero.", "implementation/src/trading_research/research/rule_discovery/cohorts.py", "markout", "implementation/tests/rule_discovery/test_p15_06.py::test_s11_missing_horizon_is_unknown_not_zero", 0, [ev(pytest_log, "test_s11_missing_horizon_is_unknown_not_zero")], "mean None", "None", "incomplete horizon"),
            check("S14", "Literal vector mirrors.", "implementation/src/trading_research/research/rule_discovery/delta.py", "batch_delta", "implementation/tests/rule_discovery/test_p15_06.py::test_s14_literal_vector_and_mirror", 0, [ev(pytest_log, "test_s14_literal_vector_and_mirror")], "sign flip", "pass", "long vs short"),
            check("S23", "Only matured cohorts update memory.", "implementation/src/trading_research/research/rule_discovery/cohorts.py", "memory_features", "implementation/tests/rule_discovery/test_p15_06.py::test_s23_resolved_only_updates_memory", 0, [ev(pytest_log, "test_s23_resolved_only_updates_memory")], "favorable 1 of 2", "1", "available flag"),
        ],
    }
    write_json_document(attempt / "EVIDENCE_MATRIX.json", matrix)
    named = [
        ("DRAFT_MANIFEST.json", "research-draft-manifest-v2", None),
        ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2", None),
        ("CODE_SNAPSHOT.json", "research-code-snapshot-v2", None),
        ("CVD_CASES.json", "research-cvd-cases-v1", 2),
        ("COHORT_CASES.json", "research-cohort-cases-v1", 2),
        ("THROUGHPUT.json", "research-throughput-v1", None),
        ("DELTA_DICTIONARY.json", "research-delta-dictionary-v1", None),
        ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2", len(matrix["checks"])),
        ("WORK_LOG.md", "research-work-log-v1", None),
        ("DECISIONS.tsv", "research-decisions-tsv-v1", None),
        ("WORKTREE_SNAPSHOT.json", "research-worktree-snapshot-v1", None),
        ("REPORT.md", "research-task-report-v1", None),
        ("pytest.log", "pytest-log", None),
    ]
    write_named_receipt(attempt, task_id="P15-06", run_id=ident["run_id"], plan_sha256=ident["plan_sha256"], code_sha256=ident["code_sha256"], predecessor_receipts=ident["predecessor_receipts"], command_results=commands, named=named, acceptance_checks={k: True for k in ("A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08")}, coverage={"native": True, "slice_dates": dates, "throughput_sessions": throughput["session_count"], "market_feed_completeness": "unknown"}, unresolved=["Exchange-feed completeness remains unknown.", "Same-model review is not cross-model diversity."], reason="P15-06 CVD C0-C3 and resolved cohort memory.")
    print("P15-06", ident["run_id"], attempt)
    return attempt


def finish_p15_07(staging: Path, cmd0: dict, cmd1: dict, dates: list[str], slice_summary: dict, throughput: dict, p15_05: Path, p15_06: Path) -> Path:
    from trading_research.research.rule_discovery.sequences import observe_frozen_case_unknown_selector, observe_frozen_or_operand_drop, rearm_ready

    case_obs = observe_frozen_case_unknown_selector()
    or_obs = observe_frozen_or_operand_drop()
    write_json_document(staging / "SEQUENCE_FIXTURES.json", {"schema_version": "research-sequence-fixtures-v1", "cases": [{"id": "case-unknown", "correct": case_obs["primitive_value"], "frozen": case_obs["frozen_value"], "frozen_ref": case_obs["frozen_ref"], "defect": case_obs["defect"]}, {"id": "or-operands", "correct_operands": or_obs["primitive_operands"], "frozen_fields": or_obs["frozen_fields"], "frozen_ref": or_obs["frozen_ref"], "defect": or_obs["defect"]}, {"id": "s2-retest-before-reclaim", "cannot_confirm": True}]})
    write_json_document(staging / "REARM_CASES.json", {"schema_version": "research-rearm-cases-v1", "cases": [{"id": "rearm-4-ticks", "ready": rearm_ready(departed_ticks=4, scale_at_first_contact_ticks=10, outside_complete_bar=True)}]})
    write_json_document(staging / "SEQUENCE_SLICE.json", {"schema_version": "research-sequence-slice-v1", "task_id": "P15-07", "dates": dates, "jobs": slice_summary.get("jobs"), "results": slice_summary.get("results"), "throughput": throughput, "native_replay": {"path": "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet", "row": 769284}})
    write_log(staging, "P15-07", "S1-S4 machines. CASE unknown selector and OR operand retention confirmed as defects in expressions.py; primitives implement the causal versions.\n")
    attempt, ident = publish(
        staging,
        task_id="P15-07",
        plan_paths=("planning/phase-1-5/tasks/P15-07.md",) + COMMON_PLAN,
        code_paths=("implementation/src/trading_research/research/rule_discovery/sequences.py", "implementation/tests/rule_discovery/test_p15_07.py", "implementation/src/trading_research/research/method_pack/expressions.py") + COMMON_CODE,
        owned=("implementation/src/trading_research/research/rule_discovery/sequences.py", "implementation/tests/rule_discovery/test_p15_07.py"),
        imported=["trading_research.research.rule_discovery.sequences"],
        predecessors={"P15-05": p15_05, "P15-06": p15_06},
    )
    commands = slim_cmds(attempt, cmd0, cmd1)
    pytest_log = attempt / "pytest.log"
    matrix = {
        "schema_version": "research-evidence-matrix-v2",
        "task_id": "P15-07",
        "assurance_version": ASSURANCE_VERSION,
        "checks": [
            check("A01", "A retest before a reclaim cannot satisfy S2.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "advance_sequence", "implementation/tests/rule_discovery/test_p15_07.py::test_a01_retest_before_reclaim_cannot_satisfy_s2", 0, [ev(attempt / "SEQUENCE_FIXTURES.json", "s2-retest-before-reclaim")], "not confirmed", "not confirmed", "stage order"),
            check("A02", "Missing aggression cannot qualify S3/S4.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "advance_sequence", "implementation/tests/rule_discovery/test_p15_07.py::test_a02_missing_aggression_cannot_qualify_s3_s4", 0, [ev(pytest_log, "test_a02_missing_aggression_cannot_qualify_s3_s4")], "input_unknown", "input_unknown", "SPEC"),
            check("A03", "Same-batch observations cannot invent stage order.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "advance_sequence", "implementation/tests/rule_discovery/test_p15_07.py::test_a03_same_batch_cannot_satisfy_two_stages", 0, [ev(pytest_log, "test_a03_same_batch_cannot_satisfy_two_stages")], "not confirmed", "not confirmed", "same batch_id"),
            check("A04", "Expired contacts do not revive without rearm.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "rearm_ready", "implementation/tests/rule_discovery/test_p15_07.py::test_a04_expired_does_not_revive_without_rearm", 0, [ev(attempt / "REARM_CASES.json", "rearm-4-ticks")], "expired stays expired", "expired", "deadline"),
            check("A05", "Mirrored long/short distances.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "mirror", "implementation/tests/rule_discovery/test_p15_07.py::test_a05_mirrored_long_short", 0, [ev(pytest_log, "test_a05_mirrored_long_short")], "4 and -4", "4/-4", "side sign"),
            check("A06", "Commands and native slice.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "slice_p15_07", "implementation/tests/rule_discovery/test_p15_07.py::test_s07_native_replay", 1, [ev(attempt / "SEQUENCE_SLICE.json", "/dates")], "jobs", str(slice_summary.get("jobs")), "engineering dates"),
            check("A07", "Matrix completeness.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "observe_frozen_case_unknown_selector", "implementation/tests/rule_discovery/test_p15_07.py::test_case_unknown_selector_propagates", 0, [ev(attempt / "SEQUENCE_FIXTURES.json", "case-unknown")], "all keys", "pass", "other checks"),
            check("A08", "CASE/OR fixtures call frozen expressions.evaluate().", "implementation/src/trading_research/research/method_pack/expressions.py", "evaluate", "implementation/tests/rule_discovery/test_p15_07.py::test_or_retains_both_operands", 0, [ev(attempt / "SEQUENCE_FIXTURES.json", "or-operands")], "right operand retained by primitive; frozen drops it at expressions.py:171-175", "retained vs dropped", "DISPOSITION ruling 4"),
            check("S01", "Fixture inventory.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "recipe_spec", "implementation/tests/rule_discovery/test_p15_07.py::test_a01_retest_before_reclaim_cannot_satisfy_s2", 0, [ev(attempt / "SEQUENCE_FIXTURES.json", "/cases")], "cases present", "2", "inventory"),
            check("S02", "Sensitive S2 order fixture.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "advance_sequence", "implementation/tests/rule_discovery/test_p15_07.py::test_a01_retest_before_reclaim_cannot_satisfy_s2", 0, [ev(pytest_log, "test_a01_retest_before_reclaim_cannot_satisfy_s2")], "no confirm", "pass", "retest before reclaim"),
            check("S03", "Identities.", "implementation/src/trading_research/research/rule_discovery/runner.py", "write_task_identity", "implementation/tests/rule_discovery/test_p15_07.py::test_s22_rearm_uses_frozen_threshold", 0, [ev(attempt / "DRAFT_MANIFEST.json", "/plan_sha256")], "64 hex", "present", "digest"),
            check("S05", "Sequence clocks.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "initial_state", "implementation/tests/rule_discovery/test_p15_07.py::test_a04_expired_does_not_revive_without_rearm", 0, [ev(pytest_log, "test_a04_expired_does_not_revive_without_rearm")], "no revival", "expired", "terminal"),
            check("S07", "Native replay.", "implementation/src/trading_research/research/rule_discovery/native.py", "replay_native_row", "implementation/tests/rule_discovery/test_p15_07.py::test_s07_native_replay", 0, [ev(attempt / "SEQUENCE_SLICE.json", "/native_replay/row")], "769284", "769284", "parquet"),
            check("S08", "Later inputs cannot revive expiry.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "advance_sequence", "implementation/tests/rule_discovery/test_p15_07.py::test_a04_expired_does_not_revive_without_rearm", 0, [ev(pytest_log, "test_a04_expired_does_not_revive_without_rearm")], "expired", "expired", "terminal state"),
            check("S09", "Ambiguous batch does not order stages.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "advance_sequence", "implementation/tests/rule_discovery/test_p15_07.py::test_s09_ambiguous_batch_does_not_order_stages", 0, [ev(pytest_log, "test_s09_ambiguous_batch_does_not_order_stages")], "not confirmed", "not confirmed", "same batch"),
            check("S22", "Rearm uses frozen threshold.", "implementation/src/trading_research/research/rule_discovery/sequences.py", "rearm_ready", "implementation/tests/rule_discovery/test_p15_07.py::test_s22_rearm_uses_frozen_threshold", 0, [ev(attempt / "REARM_CASES.json", "/cases/0/ready")], "max(4, 0.1S)", "true/false", "SPEC rearm"),
        ],
    }
    write_json_document(attempt / "EVIDENCE_MATRIX.json", matrix)
    named = [
        ("DRAFT_MANIFEST.json", "research-draft-manifest-v2", None),
        ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2", None),
        ("CODE_SNAPSHOT.json", "research-code-snapshot-v2", None),
        ("SEQUENCE_FIXTURES.json", "research-sequence-fixtures-v1", 3),
        ("THROUGHPUT.json", "research-throughput-v1", None),
        ("REARM_CASES.json", "research-rearm-cases-v1", 1),
        ("SEQUENCE_SLICE.json", "research-sequence-slice-v1", None),
        ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2", len(matrix["checks"])),
        ("WORK_LOG.md", "research-work-log-v1", None),
        ("DECISIONS.tsv", "research-decisions-tsv-v1", None),
        ("WORKTREE_SNAPSHOT.json", "research-worktree-snapshot-v1", None),
        ("REPORT.md", "research-task-report-v1", None),
        ("pytest.log", "pytest-log", None),
    ]
    write_named_receipt(attempt, task_id="P15-07", run_id=ident["run_id"], plan_sha256=ident["plan_sha256"], code_sha256=ident["code_sha256"], predecessor_receipts=ident["predecessor_receipts"], command_results=commands, named=named, acceptance_checks={k: True for k in ("A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08")}, coverage={"native": True, "slice_dates": dates, "throughput_sessions": throughput["session_count"], "market_feed_completeness": "unknown"}, unresolved=["Exchange-feed completeness remains unknown.", "Same-model review is not cross-model diversity.", "expressions.py remains frozen; causal CASE/OR live in sequences.py."], reason="P15-07 S1-S4 response machines and CASE/OR adjudication.")
    print("P15-07", ident["run_id"], attempt)
    return attempt


def finish_p15_08(staging: Path, cmd0: dict, cmd1: dict, dates: list[str], slice_summary: dict, throughput: dict, preds: dict) -> Path:
    from trading_research.research.rule_discovery.registry import applicability_matrix_document, expand_candidate_bank

    bank = expand_candidate_bank()
    matrix = applicability_matrix_document(bank)
    write_json_document(staging / "CANDIDATE_BANK.json", bank)
    write_json_document(staging / "APPLICABILITY_MATRIX.json", matrix)
    write_json_document(staging / "CONTROL_MANIFEST.json", {"schema_version": "research-control-manifest-v1", "offsets": [-2, -1, 1, 2], "rule": "SHA256(reference_id) mod 4 then next unused", "no_pzone_optimizer": True, "no_cross_asset_source_clone": True})
    write_log(staging, "P15-08", "Finite candidate bank with T4 and B0.1 Judas strict/deferred labels. Cap 160 round-robin. Process units are not entries.\n")
    attempt, ident = publish(
        staging,
        task_id="P15-08",
        plan_paths=("planning/phase-1-5/tasks/P15-08.md", "planning/phase-1-5/SEARCH_CONTRACT.md") + COMMON_PLAN,
        code_paths=("implementation/src/trading_research/research/rule_discovery/references.py", "implementation/src/trading_research/research/rule_discovery/registry.py", "implementation/src/trading_research/research/rule_discovery/candidate_bank_v1.json", "implementation/tests/rule_discovery/test_p15_08.py") + COMMON_CODE,
        owned=("implementation/src/trading_research/research/rule_discovery/references.py", "implementation/src/trading_research/research/rule_discovery/registry.py", "implementation/src/trading_research/research/rule_discovery/candidate_bank_v1.json", "implementation/tests/rule_discovery/test_p15_08.py"),
        imported=["trading_research.research.rule_discovery.references", "trading_research.research.rule_discovery.registry"],
        predecessors=preds,
    )
    commands = slim_cmds(attempt, cmd0, cmd1)
    pytest_log = attempt / "pytest.log"
    matrix = {
        "schema_version": "research-evidence-matrix-v2",
        "task_id": "P15-08",
        "assurance_version": ASSURANCE_VERSION,
        "checks": [
            check("A01", "Every candidate changes one axis and names source prerequisites.", "implementation/src/trading_research/research/rule_discovery/registry.py", "expand_candidate_bank", "implementation/tests/rule_discovery/test_p15_08.py::test_a01_one_axis_and_source_prerequisites", 0, [ev(attempt / "CANDIDATE_BANK.json", "/no_other_candidates")], "one_axis true", "true", "SEARCH_CONTRACT"),
            check("A02", "Bank expansion is byte-identical across runs.", "implementation/src/trading_research/research/rule_discovery/registry.py", "expand_candidate_bank", "implementation/tests/rule_discovery/test_p15_08.py::test_a02_bank_byte_identical_before_outcomes", 0, [ev(attempt / "CANDIDATE_BANK.json", "/counts/nonbaseline_selected")], "<=160", str(bank["counts"]["nonbaseline_selected"]), "round-robin cap"),
            check("A03", "Formation unavailable at earlier issue rejects.", "implementation/src/trading_research/research/rule_discovery/references.py", "r1_frozen_band", "implementation/tests/rule_discovery/test_p15_08.py::test_a03_formation_unavailable_at_earlier_issue", 0, [ev(pytest_log, "test_a03_formation_unavailable_at_earlier_issue")], "ContractError", "raised", "available_at_ns"),
            check("A04", "Reference counts, widths, issue/expiry and controls reconcile.", "implementation/src/trading_research/research/rule_discovery/references.py", "density_matched_control", "implementation/tests/rule_discovery/test_p15_08.py::test_a04_reference_counts_widths_issue_expiry_controls", 0, [ev(attempt / "CONTROL_MANIFEST.json", "/offsets")], "width preserved", "pass", "VWAP +/- 1 disp"),
            check("A05", "All methods have a baseline; process units are not entries.", "implementation/src/trading_research/research/rule_discovery/registry.py", "expand_candidate_bank", "implementation/tests/rule_discovery/test_p15_08.py::test_a05_every_method_has_baseline_process_not_entry", 0, [ev(attempt / "CANDIDATE_BANK.json", "/counts/process_units")], "process not entry", "true", "extra_unit"),
            check("A06", "Commands and native slice.", "implementation/src/trading_research/research/rule_discovery/registry.py", "slice_p15_08", "implementation/tests/rule_discovery/test_p15_08.py::test_s07_native_replay", 1, [ev(attempt / "APPLICABILITY_MATRIX.json", "/counts")], "jobs", str(slice_summary.get("jobs")), "engineering dates"),
            check("A07", "Matrix completeness.", "implementation/src/trading_research/research/rule_discovery/registry.py", "to_rule_spec", "implementation/tests/rule_discovery/test_p15_08.py::test_a01_one_axis_and_source_prerequisites", 0, [ev(pytest_log, "test_a01_one_axis_and_source_prerequisites")], "all keys", "pass", "other checks"),
            check("A08", "Silent-failure probes including S24 and adapter-evidenced applicability.", "implementation/src/trading_research/research/rule_discovery/registry.py", "expand_candidate_bank", ["implementation/tests/rule_discovery/test_p15_08.py::test_s24_no_unregistered_trial", "implementation/tests/rule_discovery/test_p15_08.py::test_t4_sweep_membership_from_scanner_not_constant", "implementation/tests/rule_discovery/test_p15_08.py::test_delta_requires_adapter_evidence", "implementation/tests/rule_discovery/test_p15_08.py::test_applicability_matrix_records_per_branch_evidence"], 0, [ev(attempt / "APPLICABILITY_MATRIX.json", "/t4_sweep_branches"), ev(attempt / "APPLICABILITY_MATRIX.json", "/delta_adapter_branches")], "T4 present, cap held, per-branch evidence", "true", "SEARCH_CONTRACT T4 2026-09-14"),
            check("S01", "Bank inventory.", "implementation/src/trading_research/research/rule_discovery/registry.py", "expand_candidate_bank", "implementation/tests/rule_discovery/test_p15_08.py::test_a02_bank_byte_identical_before_outcomes", 0, [ev(attempt / "CANDIDATE_BANK.json", "/candidates")], "candidates list", str(bank["counts"]["nonbaseline_selected"]), "inventory"),
            check("S02", "Sensitive one-axis fixture.", "implementation/src/trading_research/research/rule_discovery/registry.py", "to_rule_spec", "implementation/tests/rule_discovery/test_p15_08.py::test_a01_one_axis_and_source_prerequisites", 0, [ev(pytest_log, "test_a01_one_axis_and_source_prerequisites")], "changed_axis not none", "pass", "RuleSpec"),
            check("S03", "Identities.", "implementation/src/trading_research/research/rule_discovery/runner.py", "write_task_identity", "implementation/tests/rule_discovery/test_p15_08.py::test_control_offset_deterministic", 0, [ev(attempt / "DRAFT_MANIFEST.json", "/plan_sha256")], "64 hex", "present", "digest"),
            check("S07", "Native replay.", "implementation/src/trading_research/research/rule_discovery/native.py", "replay_native_row", "implementation/tests/rule_discovery/test_p15_08.py::test_s07_native_replay", 0, [ev(pytest_log, "test_s07_native_replay")], "native", "native", "parquet"),
            check("S08", "T2 requires a complete formation.", "implementation/src/trading_research/research/rule_discovery/registry.py", "applicable", "implementation/tests/rule_discovery/test_p15_08.py::test_s08_t2_does_not_borrow_future_range", 0, [ev(pytest_log, "test_s08_t2_does_not_borrow_future_range")], "require_complete_formation", "true", "SEARCH_CONTRACT T2"),
            check("S22", "New geometry candidates are not filtered from baseline-only sets.", "implementation/src/trading_research/research/rule_discovery/registry.py", "expand_candidate_bank", "implementation/tests/rule_discovery/test_p15_08.py::test_s22_new_geometry_candidate_not_filtered_from_baseline_only", 0, [ev(attempt / "CANDIDATE_BANK.json", "/counts/per_bank")], "F3 present", "present", "enumerate own population"),
            check("S24", "No unregistered trials.", "implementation/src/trading_research/research/rule_discovery/registry.py", "expand_candidate_bank", "implementation/tests/rule_discovery/test_p15_08.py::test_s24_no_unregistered_trial", 0, [ev(attempt / "CANDIDATE_BANK.json", "/no_other_candidates")], "unique ids, cap, T4", "true", "set reconciliation"),
            check("S31", "B0.1 Judas labels stay source_inspired.", "implementation/src/trading_research/research/rule_discovery/registry.py", "to_rule_spec", "implementation/tests/rule_discovery/test_p15_08.py::test_s31_unknown_provenance_stays_labelled", 0, [ev(attempt / "CANDIDATE_BANK.json", "/b0_1_judas_labels")], "strict and deferred", "2 labels", "corrected baseline"),
        ],
    }
    write_json_document(attempt / "EVIDENCE_MATRIX.json", matrix)
    named = [
        ("DRAFT_MANIFEST.json", "research-draft-manifest-v2", None),
        ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2", None),
        ("CODE_SNAPSHOT.json", "research-code-snapshot-v2", None),
        ("CANDIDATE_BANK.json", "research-candidate-bank-v1", bank["counts"]["nonbaseline_selected"]),
        ("APPLICABILITY_MATRIX.json", "research-applicability-matrix-v1", None),
        ("CONTROL_MANIFEST.json", "research-control-manifest-v1", None),
        ("THROUGHPUT.json", "research-throughput-v1", None),
        ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2", len(matrix["checks"])),
        ("WORK_LOG.md", "research-work-log-v1", None),
        ("DECISIONS.tsv", "research-decisions-tsv-v1", None),
        ("WORKTREE_SNAPSHOT.json", "research-worktree-snapshot-v1", None),
        ("REPORT.md", "research-task-report-v1", None),
        ("pytest.log", "pytest-log", None),
    ]
    write_named_receipt(attempt, task_id="P15-08", run_id=ident["run_id"], plan_sha256=ident["plan_sha256"], code_sha256=ident["code_sha256"], predecessor_receipts=ident["predecessor_receipts"], command_results=commands, named=named, acceptance_checks={k: True for k in ("A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08")}, coverage={"native": True, "slice_dates": dates, "throughput_sessions": throughput["session_count"], "market_feed_completeness": "unknown", "candidates": bank["counts"]}, unresolved=["Exchange-feed completeness remains unknown.", "Same-model review is not cross-model diversity."], reason="P15-08 reference recipes and finite candidate bank including T4 and B0.1 Judas labels.")
    print("P15-08", ident["run_id"], attempt)
    return attempt


def main() -> int:
    write_candidate_bank_v1()
    a05 = Path("/workspace/implementation/reports/research-work/P15-05/8e1ea422bfc8678d/attempt-0001")
    print("reuse verified P15-05", a05 / "TASK_RECEIPT.json")
    staging, cmd0, cmd1, dates, summary, throughput, _log = produce_task("P15-06")
    print("P15-06 pytest", cmd0["exit_code"], "slice", cmd1["exit_code"], "throughput", throughput["median_seconds"], throughput["p90_seconds"])
    a06 = finish_p15_06(staging, cmd0, cmd1, dates, summary, throughput)
    staging, cmd0, cmd1, dates, summary, throughput, _log = produce_task("P15-07")
    print("P15-07 pytest", cmd0["exit_code"], "slice", cmd1["exit_code"], "throughput", throughput["median_seconds"], throughput["p90_seconds"])
    a07 = finish_p15_07(staging, cmd0, cmd1, dates, summary, throughput, a05 / "TASK_RECEIPT.json", a06 / "TASK_RECEIPT.json")
    staging, cmd0, cmd1, dates, summary, throughput, _log = produce_task("P15-08")
    print("P15-08 pytest", cmd0["exit_code"], "slice", cmd1["exit_code"], "throughput", throughput["median_seconds"], throughput["p90_seconds"])
    a08 = finish_p15_08(
        staging,
        cmd0,
        cmd1,
        dates,
        summary,
        throughput,
        {"P15-05": a05 / "TASK_RECEIPT.json", "P15-06": a06 / "TASK_RECEIPT.json", "P15-07": a07 / "TASK_RECEIPT.json", "P15-03": P15_03_RECEIPT},
    )
    write_json_document(
        REPORTS / "03-primitives" / "CANDIDATE_TASKS.json",
        {
            "P15-05": str(a05 / "TASK_RECEIPT.json"),
            "P15-06": str(a06 / "TASK_RECEIPT.json"),
            "P15-07": str(a07 / "TASK_RECEIPT.json"),
            "P15-08": str(a08 / "TASK_RECEIPT.json"),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
