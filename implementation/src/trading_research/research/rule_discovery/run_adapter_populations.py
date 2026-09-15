"""Adapter-population full-history runner. Does not edit adapters or baseline_repairs."""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from decimal import Decimal as D
from pathlib import Path
import argparse
import json
import math
import os
import sys
import time
import traceback

from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.historical_outcomes import observe_outcome
from trading_research.research.method_pack.measurement_outcomes import measure_setup
from trading_research.research.method_pack.measurement_runner import (
    configure_runtime,
    measurement_scope,
    session_accounting,
)
from trading_research.research.rule_discovery.baseline import PHASE1_RUN
from trading_research.research.rule_discovery.baseline_repairs import (
    BASELINE_REPAIR_VERSION,
    _attach,
)
from trading_research.research.rule_discovery.native import cgroup_worker_count, install_write_guard
from trading_research.research.rule_discovery.run_baseline_repair import (
    achieved_concurrency,
    canonical_json,
    counts,
    evaluation_dates,
    peak_rss_bytes,
    read_job,
    sha256_bytes,
    sha256_file,
    write_job_atomic,
    write_json_atomic,
)
from trading_research.research.rule_discovery.source_adapters.common import FAMILY_BRANCHES, coverage_row, dual_scan
from trading_research.research.rule_discovery.source_adapters import green_failure, green_vwap_scalp

WORKTREE = Path(__file__).resolve().parents[5]
RUNNER_PATH = Path(__file__).resolve()
REPORTS_PARENT = WORKTREE / "implementation/reports/research-work/adapter-populations"
B02_REPORTS_PARENT = WORKTREE / "implementation/reports/research-work/P15-16A"
B02_VERSION = "B0.2-2026-09-15"
CENSUS_RUN_ID = "20def36e065c13d7"
CENSUS_ROOT = Path("/workspace/implementation/reports/research-work/baseline-repair") / CENSUS_RUN_ID
CENSUS_UNKNOWN_TOTAL = 628
MANIFEST_SCHEMA = "adapter-populations-full-history-manifest-v1"
COMPLETION_SCHEMA = "adapter-populations-date-completion-v1"
SUMMARY_SCHEMA = "adapter-populations-full-history-summary-v1"
COMPLETE_SCHEMA = "adapter-populations-run-complete-v1"
RUNNER_RELATIVE = "implementation/src/trading_research/research/rule_discovery/run_adapter_populations.py"
STAGE_KEYS = ("arrival_read_recorded", "alignment_ok", "profile_allows_trade")
VWAP_COVERAGE_ID = "GB-VWAP:branch:source_long"
VWAP_CENSUS_JOB = "GB-VWAP--branch--source_long.json.gz"
JOB_PATH_SCHEME = "coverage_id--json.gz"

_STATE: dict = {}


def _branch(family: str, branch: str, scan_kind: str) -> dict[str, str]:
    return {
        "family": family,
        "branch": branch,
        "coverage_id": f"{family}:branch:{branch}",
        "scan_kind": scan_kind,
    }


BRANCH_RECORDS: tuple[dict[str, str], ...] = (
    _branch("GB-FAIL", "london_box", "gb_fail_0930"),
    _branch("GB-FAIL", "asia_box", "gb_fail_0930"),
    _branch("GB-FAIL", "overnight_scan", "overnight"),
    _branch("GB-SCALP", "golden_pocket_continuation", "golden_pocket"),
    _branch("SAINT-AMT", "continuation_retest", "dual_b01"),
    _branch("SAINT-AMT", "trapped_buyers_retest", "dual_b01"),
    _branch("SAINT-AMT", "failed_auction_return", "dual_b01"),
    _branch("SAINT-AMT", "poc_traversal", "dual_b01"),
    _branch("GB-VWAP", "source_long", "dual_b01"),
)
BRANCH_IDS = tuple(row["coverage_id"] for row in BRANCH_RECORDS)


def b02_branch_records() -> tuple[dict[str, str], ...]:
    from trading_research.research.rule_discovery.source_adapters.green_b02 import B02_BRANCHES

    rows: list[dict[str, str]] = []
    families = (
        ("JJ-TBR", FAMILY_BRANCHES["JJ-TBR"]),
        ("GB-FAIL", B02_BRANCHES["GB-FAIL"]),
        ("GB-VWAP", B02_BRANCHES["GB-VWAP"]),
        ("GB-SCALP", B02_BRANCHES["GB-SCALP"]),
        ("SIRES", FAMILY_BRANCHES["SIRES"]),
        ("SAINT-AMT", FAMILY_BRANCHES["SAINT-AMT"]),
        ("MEMBER-TWO-REASONS", FAMILY_BRANCHES["MEMBER-TWO-REASONS"]),
        ("KEANI-OPEN-ABOVE-VALUE", FAMILY_BRANCHES["KEANI-OPEN-ABOVE-VALUE"]),
        ("REFILL-STUDY", FAMILY_BRANCHES["REFILL-STUDY"]),
    )
    for family, branches in families:
        for branch in branches:
            rows.append(_branch(family, branch, "b02"))
    return tuple(rows)


def records_for_baseline(baseline: str) -> tuple[dict[str, str], ...]:
    if baseline == "B0.2":
        return b02_branch_records()
    return BRANCH_RECORDS

DECISIONS = [
    "Default --baseline B0.1 keeps the frozen BRANCH_RECORDS table and does not recompute B0/B0.1.",
    "--baseline B0.2 dispatches every family's scan_b02; B0 and B0.1 rows are read from run-1.0.1 and census 20def36e065c13d7.",
    "gb_fail_0930/overnight redirect to green_failure.scan_b02; golden_pocket redirects to green_vwap_scalp.scan_b02.",
    "Jobs are jobs/<date>/<coverage_id with ':' replaced by '--'>.json.gz (JOB_PATH_SCHEME=coverage_id--json.gz). Branch names may collide across families.",
    "cpu_quota reads cgroup v1 cpu.cfs_quota_us/period first, then v2 cpu.max.",
    "default_workers is floor(quota/period)-5, at least 1 (12 on this machine).",
    "install_write_guard is on. A cache miss fails the date.",
    "load_registry(..., check_software=False) because this runner sits beside frozen baseline_repairs.py.",
    "SIRES and REFILL-STUDY B0.2 use the R3 NativeMarketView array plane attached once per date.",
    "Resume skips a date with a valid completion.json. Existing job gz files are kept.",
    "SUMMARY.json and RUN_COMPLETE.json are written only when all 1742 dates have a valid completion.",
]


def ensure_transforms() -> None:
    import trading_research.research.rule_discovery.source_adapters.jumbo  # noqa
    import trading_research.research.rule_discovery.source_adapters.green_failure  # noqa
    import trading_research.research.rule_discovery.source_adapters.green_vwap_scalp  # noqa
    import trading_research.research.rule_discovery.source_adapters.sires  # noqa
    import trading_research.research.rule_discovery.source_adapters.saint  # noqa
    import trading_research.research.rule_discovery.source_adapters.member  # noqa
    import trading_research.research.rule_discovery.source_adapters.keani  # noqa
    import trading_research.research.rule_discovery.source_adapters.processes  # noqa


def cpu_quota():
    v1_quota = Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us")
    v1_period = Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us")
    if v1_quota.is_file() and v1_period.is_file():
        quota = int(v1_quota.read_text().strip())
        period = int(v1_period.read_text().strip())
        if quota > 0 and period > 0:
            return {"cpu_quota_us": quota, "cpu_period_us": period, "cpu_quota_cpus": quota / period}
    v2 = Path("/sys/fs/cgroup/cpu.max")
    if v2.is_file():
        text = v2.read_text().strip().split()
        if len(text) == 2 and text[0] != "max":
            quota, period = int(text[0]), int(text[1])
            return {"cpu_quota_us": quota, "cpu_period_us": period, "cpu_quota_cpus": quota / period}
    return {"cpu_quota_us": None, "cpu_period_us": None, "cpu_quota_cpus": None}


def default_workers() -> int:
    quota = cpu_quota()
    amount = quota.get("cpu_quota_us")
    period = quota.get("cpu_period_us")
    if not amount or not period or amount <= 0 or period <= 0:
        return 1
    return max(1, math.floor(amount / period) - 5)


def code_identity():
    return {
        "python": sys.version.split()[0],
        "runner_path": RUNNER_RELATIVE,
        "runner_sha256": sha256_file(RUNNER_PATH),
    }


def build_manifest(registry, dates, workers, *, baseline="B0.1", rows=None):
    records = [dict(row) for row in (rows if rows is not None else BRANCH_RECORDS)]
    return {
        "baseline": baseline,
        "branch_records": records,
        "branches": [row["coverage_id"] for row in records],
        "census_run_id": CENSUS_RUN_ID,
        "census_summary_sha256": sha256_file(CENSUS_ROOT / "SUMMARY.json"),
        "code_identity": code_identity(),
        "dates": list(dates),
        "registry_sha256": registry["registry_sha256"],
        "schema": MANIFEST_SCHEMA,
        "worker_count": workers,
        "job_path_scheme": JOB_PATH_SCHEME,
    }


def job_filename(coverage_id: str) -> str:
    return coverage_id.replace(":", "--") + ".json.gz"


def job_path(run_root: Path, day: str, coverage_id: str) -> Path:
    return run_root / "jobs" / day / job_filename(coverage_id)


def resolve_recorded_job_path(run_root: Path, item: dict) -> Path:
    """Resolve a job from a completion/manifest record, not from JOB_PATH_SCHEME."""
    recorded = Path(item["path"])
    if recorded.is_file():
        return recorded
    return run_root / "jobs" / recorded.parent.name / recorded.name


def init_run(workers=None, reports_parent=None, baseline="B0.1"):
    configure_runtime()
    install_write_guard()
    ensure_transforms()
    if workers is None:
        workers = default_workers()
    if baseline not in {"B0", "B0.1", "B0.2"}:
        raise SystemExit(f"unsupported baseline {baseline}")
    rows = [dict(row) for row in records_for_baseline(baseline)]
    if reports_parent is not None:
        parent = Path(reports_parent)
    elif baseline == "B0.2":
        parent = B02_REPORTS_PARENT
    else:
        parent = REPORTS_PARENT
    registry, _coverage = hr.load_registry(PHASE1_RUN, check_software=False)
    dates = evaluation_dates(registry)
    manifest = build_manifest(registry, dates, workers, baseline=baseline, rows=rows)
    canonical = canonical_json(manifest)
    digest = sha256_bytes(canonical)
    run_id = digest[:16]
    run_root = parent / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    manifest_path = run_root / "MANIFEST.json"
    if manifest_path.exists():
        if manifest_path.read_bytes() != canonical:
            raise SystemExit(f"MANIFEST.json at {manifest_path} does not match current canonical bytes")
    else:
        manifest_path.write_bytes(canonical)
        if sha256_file(manifest_path) != digest:
            raise SystemExit("MANIFEST.json hash mismatch after write")
    log_path = run_root / "WORK_LOG.md"
    if not log_path.exists():
        quota = cpu_quota()
        version = B02_VERSION if baseline == "B0.2" else BASELINE_REPAIR_VERSION
        lines = [
            "# Adapter-population full-history work log",
            "",
            f"- Run id: `{run_id}`",
            f"- Manifest sha256: `{digest}`",
            f"- Baseline: `{version}`",
            f"- Dates: {len(dates)} ({dates[0]} .. {dates[-1]})",
            f"- Branches: {len(rows)}",
            f"- Jobs: {len(dates) * len(rows)}",
            f"- Workers requested: {workers}",
            f"- default_workers: {default_workers()}",
            f"- cgroup_worker_count: {cgroup_worker_count()}",
            f"- cpu quota: {quota}",
            f"- census_run_id: `{CENSUS_RUN_ID}`",
            "",
            "## Decisions",
            "",
        ]
        for item in DECISIONS:
            lines.append(f"- {item}")
        lines.append("")
        log_path.write_text("\n".join(lines))
    write_json_atomic(
        run_root / "RUN_META.json",
        {
            "job_path_scheme": JOB_PATH_SCHEME,
            "failed_dates": [],
            "achieved_concurrency": 0,
            "wall_seconds_orchestrator": 0.0,
            "worker_count": workers,
        },
    )
    protocol = registry["scope"]["measurement_protocol"]
    return {
        "run_id": run_id,
        "run_root": run_root,
        "manifest": manifest,
        "manifest_sha256": digest,
        "registry": registry,
        "rows": rows,
        "dates": dates,
        "workers": workers,
        "baseline": baseline,
        "software_sha256": content_hash(manifest["code_identity"]),
        "measurement_protocol_sha256": protocol["sha256"],
        "registry_sha256": registry["registry_sha256"],
    }


def _observe_outcomes(market, document):
    outcomes = []
    for episode in document.get("episodes") or []:
        try:
            outcomes.append(observe_outcome(market, episode))
        except Exception as exc:
            outcomes.append(
                {
                    "schema": "phase1-post-sequence-observation-v2",
                    "candidate_id": episode.get("candidate_id"),
                    "actual_trade": False,
                    "cost_or_fill_model": False,
                    "sequence_verdict": episode.get("research_verdict"),
                    "result": "not_applicable",
                    "resolved_at": None,
                    "event_ids": [],
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )
    return outcomes


def _setup_measurements(market, row, document):
    if measurement_scope(row["method_id"], row["branch"]) != "entry_setup":
        return []
    out = []
    for episode in document.get("episodes") or []:
        if (episode.get("strategy_assessment") or {}).get("status") != "setup":
            continue
        try:
            out.append(measure_setup(market, episode))
        except Exception as exc:
            out.append(
                {
                    "schema": "phase1-setup-price-measurement-v1",
                    "candidate_id": episode.get("candidate_id"),
                    "status": "measurement_error",
                    "reason": f"{type(exc).__name__}: {exc}",
                }
            )
    return out


def _session_accounting(market, document):
    try:
        return session_accounting(market, document)
    except Exception as exc:
        return {"status": "accounting_error", "reason": f"{type(exc).__name__}: {exc}"}


def _domain_receipts(market):
    receipts = {}
    for key, record in getattr(market, "domain_observations", {}).items():
        try:
            digest = content_hash(hr.serializable(record))
        except Exception:
            digest = None
        receipts[key] = {"recipe_id": record.get("recipe_id"), "sha256": digest}
    return receipts


def _finish_document(document, market, row, ctx, wall_seconds, rss):
    ids = [episode["candidate_id"] for episode in document.get("episodes") or []]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate candidate opportunity within branch/session")
    document["outcomes"] = _observe_outcomes(market, document)
    document["setup_measurements"] = _setup_measurements(market, row, document)
    document["session_accounting"] = _session_accounting(market, document)
    try:
        receipts = list({content_hash(r): r for r in market.input_receipts}.values())
    except Exception:
        receipts = list(market.input_receipts)
    document.update(
        registry_sha256=ctx["registry_sha256"],
        software_sha256=ctx["software_sha256"],
        cohort="evaluation",
        measurement_protocol_sha256=ctx["measurement_protocol_sha256"],
        input_receipts=receipts,
        domain_observations=_domain_receipts(market),
        job_state="completed",
        native_executions=market.window.document["row_count"],
        wall_seconds=wall_seconds,
        peak_rss_bytes=rss,
    )
    if "baseline_version" not in document:
        document["baseline_version"] = BASELINE_REPAIR_VERSION
    return document


def _scan_dual_b01(market, rec):
    family = rec["family"]
    branch = rec["branch"]
    document = dual_scan(market, family, branch)["b01"]
    _attach(document, coverage_row(family, branch), BASELINE_REPAIR_VERSION)
    return document


def _ensure_candidate_ids(document, rec):
    episodes = list(document.get("episodes") or [])
    seen = set()
    for index, episode in enumerate(episodes):
        cid = episode.get("candidate_id")
        if not cid:
            cid = f"b02:{rec.get('family')}:{rec.get('branch')}:{index}"
            episode["candidate_id"] = cid
        if cid in seen:
            episode["candidate_id"] = f"{cid}:{index}"
            cid = episode["candidate_id"]
        seen.add(cid)
    document["episodes"] = episodes
    return document


def _scan_b02(market, rec):
    family = rec["family"]
    branch = rec["branch"]
    payload = dict(rec)
    if family == "GB-FAIL":
        document = green_failure.scan_b02(market, payload)
    elif family in {"GB-VWAP", "GB-SCALP"}:
        document = green_vwap_scalp.scan_b02(market, payload)
    else:
        from trading_research.research.rule_discovery.source_adapters.common import family_scan_b02

        view = market
        if family in {"SIRES", "REFILL-STUDY"}:
            view = getattr(market, "_native_view", None) or market
        document = family_scan_b02(view, family, branch)
    document = dict(document)
    document.setdefault("coverage_id", rec["coverage_id"])
    document.setdefault("baseline_version", B02_VERSION)
    document.setdefault("method_id", family)
    document.setdefault("family", family)
    document.setdefault("branch", branch)
    return _ensure_candidate_ids(document, rec)


def _scan_gb_fail_redirect(market, rec):
    payload = dict(rec)
    payload.setdefault("family", "GB-FAIL")
    return _scan_b02(market, payload)


def _scan_overnight_redirect(market, rec):
    payload = dict(rec)
    payload["family"] = "GB-FAIL"
    payload["branch"] = "all"
    return _scan_b02(market, payload)


def _scan_golden_pocket_redirect(market, rec):
    payload = dict(rec)
    payload["family"] = "GB-SCALP"
    payload["branch"] = "golden_pocket_continuation"
    return _scan_b02(market, payload)


_SCANNERS = {
    "dual_b01": _scan_dual_b01,
    "b02": _scan_b02,
    "gb_fail_0930": green_failure.scan_b02,
    "overnight": _scan_overnight_redirect,
    "golden_pocket": _scan_golden_pocket_redirect,
}


def _scan_record(market, rec):
    kind = rec["scan_kind"]
    if kind == "gb_fail_0930":
        payload = dict(rec)
        payload.setdefault("family", "GB-FAIL")
        return _ensure_candidate_ids(green_failure.scan_b02(market, payload), payload)
    if kind == "golden_pocket":
        payload = dict(rec)
        payload["family"] = "GB-SCALP"
        payload["branch"] = "golden_pocket_continuation"
        return _ensure_candidate_ids(green_vwap_scalp.scan_b02(market, payload), payload)
    scanner = _SCANNERS[kind]
    return scanner(market, rec)


def _stage_counts(document):
    out = {key: {"false": 0, "none": 0} for key in STAGE_KEYS}
    for episode in document.get("episodes") or []:
        values = episode.get("values") or {}
        for key in STAGE_KEYS:
            raw = values[key] if key in values else episode.get(key)
            if raw is False:
                out[key]["false"] += 1
            elif raw is not True:
                out[key]["none"] += 1
    return out


def _vwap_census_transitions(day, document):
    path = CENSUS_ROOT / "jobs" / day / VWAP_CENSUS_JOB
    if not path.is_file():
        return {"census_unknown_to_pass": 0, "census_unknown_to_fail": 0, "census_job_missing": True}
    census = read_job(path)
    adapter = {episode["candidate_id"]: episode.get("research_verdict") for episode in document.get("episodes") or []}
    to_pass = 0
    to_fail = 0
    for episode in census.get("episodes") or []:
        if episode.get("research_verdict") != "unknown":
            continue
        now = adapter.get(episode["candidate_id"])
        if now == "pass":
            to_pass += 1
        elif now == "fail":
            to_fail += 1
    return {"census_unknown_to_pass": to_pass, "census_unknown_to_fail": to_fail, "census_job_missing": False}


def _branch_stats(day, rec, document, wall, rss):
    stats = counts(document)
    stats["wall_seconds"] = wall
    stats["peak_rss_bytes"] = rss
    stats["baseline_version"] = document.get("baseline_version")
    if rec["family"] == "SAINT-AMT":
        stats["stages"] = _stage_counts(document)
    if rec["coverage_id"] == VWAP_COVERAGE_ID:
        stats.update(_vwap_census_transitions(day, document))
    return stats


def _finish_row(rec):
    return {"method_id": rec["family"], "branch": rec["branch"], "coverage_id": rec["coverage_id"]}


def _init_worker(payload):
    install_write_guard()
    configure_runtime()
    ensure_transforms()
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    os.environ.setdefault("MKL_NUM_THREADS", "1")
    _STATE.clear()
    _STATE.update(payload)
    _STATE["run_root"] = Path(payload["run_root"])


def _completion_ok(path: Path, ctx, rows) -> bool:
    try:
        completion = json.loads(path.read_text())
    except Exception:
        return False
    if completion.get("schema") != COMPLETION_SCHEMA:
        return False
    if completion.get("manifest_sha256") != ctx["manifest_sha256"]:
        return False
    jobs = completion.get("jobs") or []
    if {item["coverage_id"] for item in jobs} != {row["coverage_id"] for row in rows}:
        return False
    for item in jobs:
        job = Path(item["path"])
        if not job.is_file():
            return False
        if sha256_file(job) != item["sha256"]:
            return False
    return True


def _process_date(day):
    install_write_guard()
    configure_runtime()
    started = time.time()
    monotonic0 = time.monotonic()
    ctx = _STATE
    run_root = Path(ctx["run_root"])
    rows = ctx["rows"]
    completion_path = run_root / "jobs" / day / "completion.json"
    if completion_path.exists() and _completion_ok(completion_path, ctx, rows):
        return {
            "date": day,
            "ok": True,
            "resumed": True,
            "wall_seconds": 0.0,
            "started_at": started,
            "finished_at": time.time(),
            "n_jobs": len(rows),
        }
    from trading_research.research.method_pack.historical_features import HistoricalFeatures

    try:
        registry, _manifest = hr.load_registry(PHASE1_RUN, check_software=False)
        market = HistoricalFeatures(day, records=hr._records(registry))
        if ctx.get("baseline") == "B0.2":
            from trading_research.research.rule_discovery.native import build_market_view

            try:
                market._native_view = build_market_view(day, full_account_day=True)
            except Exception:
                market._native_view = None
    except Exception as exc:
        payload = {
            "date": day,
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "wall_seconds": round(time.monotonic() - monotonic0, 4),
            "started_at": started,
            "finished_at": time.time(),
        }
        write_json_atomic(run_root / "jobs" / day / "FAILURE.json", payload)
        return payload
    jobs = []
    branch_stats = {}
    errors = []
    for rec in rows:
        cid = rec["coverage_id"]
        path = job_path(run_root, day, rec["coverage_id"])
        t0 = time.monotonic()
        try:
            if path.exists():
                document = read_job(path)
                digest = sha256_file(path)
                wall = float(document.get("wall_seconds") or round(time.monotonic() - t0, 4))
                rss = int(document.get("peak_rss_bytes") or peak_rss_bytes())
            else:
                document = _scan_record(market, rec)
                document = _finish_document(
                    document, market, _finish_row(rec), ctx, wall_seconds=0.0, rss=peak_rss_bytes()
                )
                wall = round(time.monotonic() - t0, 4)
                rss = peak_rss_bytes()
                document["wall_seconds"] = wall
                document["peak_rss_bytes"] = rss
                default_version = B02_VERSION if ctx.get("baseline") == "B0.2" else BASELINE_REPAIR_VERSION
                document["baseline_version"] = document.get("baseline_version") or default_version
                digest = write_job_atomic(path, document)
            branch_stats[cid] = _branch_stats(day, rec, document, wall, rss)
            jobs.append({"coverage_id": cid, "branch": rec["branch"], "path": str(path), "sha256": digest})
        except Exception as exc:
            errors.append(
                {
                    "coverage_id": cid,
                    "branch": rec["branch"],
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                }
            )
            break
    if errors or len(jobs) != len(rows):
        failure = {
            "date": day,
            "ok": False,
            "error": errors[0]["error"] if errors else f"wrote {len(jobs)}/{len(rows)} jobs",
            "traceback": errors[0]["traceback"] if errors else "",
            "errors": errors,
            "n_jobs_written": len(jobs),
            "wall_seconds": round(time.monotonic() - monotonic0, 4),
            "started_at": started,
            "finished_at": time.time(),
        }
        write_json_atomic(run_root / "jobs" / day / "FAILURE.json", failure)
        return failure
    completion = {
        "schema": COMPLETION_SCHEMA,
        "date": day,
        "manifest_sha256": ctx["manifest_sha256"],
        "registry_sha256": ctx["registry_sha256"],
        "jobs": jobs,
        "branch_stats": branch_stats,
        "native_executions": market.window.document["row_count"],
        "native_input_sha256": market.window.document["input_sha256"],
        "wall_seconds": round(time.monotonic() - monotonic0, 4),
        "peak_rss_bytes": peak_rss_bytes(),
    }
    write_json_atomic(completion_path, completion)
    fail_path = run_root / "jobs" / day / "FAILURE.json"
    if fail_path.exists():
        fail_path.unlink()
    try:
        from trading_research.research.method_pack.strategy_options import option_rows, spot_rows
        from trading_research.research.method_pack.strategy_measurements import vendor_rows

        option_rows.cache_clear()
        spot_rows.cache_clear()
        vendor_rows.cache_clear()
    except Exception:
        pass
    return {
        "date": day,
        "ok": True,
        "resumed": False,
        "wall_seconds": completion["wall_seconds"],
        "started_at": started,
        "finished_at": time.time(),
        "n_jobs": len(jobs),
        "native_executions": completion["native_executions"],
    }


def update_progress(run_root: Path, payload):
    write_json_atomic(run_root / "PROGRESS.json", payload)
    (run_root / "HEARTBEAT").write_text(f"{time.time()}\n")


def _handle_date_result(run_root, result, day, completed, failed, todo_n):
    if not result.get("ok"):
        failed.append(day)
    else:
        completed += 1
    print(
        json.dumps(
            {
                "event": "date_completed" if result.get("ok") else "date_failed",
                "date": day,
                "ok": result.get("ok"),
                "resumed": result.get("resumed"),
                "wall_seconds": result.get("wall_seconds"),
                "error": result.get("error"),
                "completed": completed,
                "failed": len(failed),
                "remaining": todo_n - completed - len(failed),
            }
        ),
        flush=True,
    )
    update_progress(
        run_root,
        {
            "event": "progress",
            "completed": completed,
            "failed": len(failed),
            "remaining": todo_n - completed - len(failed),
            "last_date": day,
            "last_ok": bool(result.get("ok")),
            "updated_at": time.time(),
            "failed_dates": list(failed),
        },
    )
    return completed


def run_dates(ctx, dates, workers):
    run_root = ctx["run_root"]
    rows = ctx["rows"]
    already = []
    todo = []
    for day in dates:
        if _completion_ok(run_root / "jobs" / day / "completion.json", ctx, rows):
            already.append(day)
        else:
            todo.append(day)
    started = time.monotonic()
    started_wall = time.time()
    results = [
        {
            "date": day,
            "ok": True,
            "resumed": True,
            "wall_seconds": 0.0,
            "started_at": started_wall,
            "finished_at": started_wall,
            "n_jobs": len(rows),
        }
        for day in already
    ]
    update_progress(
        run_root,
        {
            "event": "run_started",
            "declared_sessions": len(dates),
            "pending": len(todo),
            "workers": workers,
            "cgroup_worker_count": cgroup_worker_count(),
            "manifest_sha256": ctx["manifest_sha256"],
            "started_at": started_wall,
        },
    )
    print(
        json.dumps(
            {
                "event": "run_started",
                "declared_sessions": len(dates),
                "pending": len(todo),
                "workers": workers,
                "run_id": ctx["run_id"],
            }
        ),
        flush=True,
    )
    if not todo:
        return {
            "date_results": results,
            "wall_seconds_orchestrator": round(time.monotonic() - started, 4),
            "failed_dates": [],
            "achieved_concurrency": 0,
            "worker_count": workers,
        }
    worker_payload = {
        "run_root": str(run_root),
        "rows": rows,
        "manifest_sha256": ctx["manifest_sha256"],
        "registry_sha256": ctx["registry_sha256"],
        "software_sha256": ctx["software_sha256"],
        "measurement_protocol_sha256": ctx["measurement_protocol_sha256"],
        "baseline": ctx.get("baseline") or "B0.1",
    }
    failed = []
    completed = len(already)
    todo_n = len(todo) + len(already)

    def consume(result, day):
        nonlocal completed
        results.append(result)
        completed = _handle_date_result(run_root, result, day, completed, failed, todo_n)

    if workers <= 1:
        _init_worker(worker_payload)
        for day in todo:
            try:
                result = _process_date(day)
            except Exception:
                result = {
                    "date": day,
                    "ok": False,
                    "error": "worker_exception",
                    "traceback": traceback.format_exc(),
                    "started_at": time.time(),
                    "finished_at": time.time(),
                    "wall_seconds": 0.0,
                }
            consume(result, day)
    else:
        with ProcessPoolExecutor(
            max_workers=workers,
            initializer=_init_worker,
            initargs=(worker_payload,),
        ) as pool:
            futures = {pool.submit(_process_date, day): day for day in todo}
            for future in as_completed(futures):
                day = futures[future]
                try:
                    result = future.result()
                except Exception:
                    result = {
                        "date": day,
                        "ok": False,
                        "error": "worker_exception",
                        "traceback": traceback.format_exc(),
                        "started_at": time.time(),
                        "finished_at": time.time(),
                        "wall_seconds": 0.0,
                    }
                consume(result, day)
    return {
        "date_results": results,
        "wall_seconds_orchestrator": round(time.monotonic() - started, 4),
        "failed_dates": failed,
        "achieved_concurrency": achieved_concurrency(results),
        "worker_count": workers,
    }


def retry_failed(ctx, failed, workers):
    if not failed:
        return {"failed_dates": [], "date_results": [], "wall_seconds_orchestrator": 0.0, "achieved_concurrency": 0}
    print(json.dumps({"event": "retry_started", "dates": failed}), flush=True)
    for day in failed:
        completion = ctx["run_root"] / "jobs" / day / "completion.json"
        if completion.exists():
            completion.unlink()
    return run_dates(ctx, failed, workers)


def _census_by_coverage():
    payload = json.loads((CENSUS_ROOT / "SUMMARY.json").read_text())
    return {row["coverage_id"]: row for row in payload.get("branches") or []}


def aggregate(ctx, run_meta):
    run_root = ctx["run_root"]
    dates = ctx["manifest"]["dates"]
    rows = ctx["rows"]
    census_index = _census_by_coverage()
    by_branch = {}
    for rec in rows:
        cid = rec["coverage_id"]
        slot = {
            "coverage_id": cid,
            "family": rec["family"],
            "branch": rec["branch"],
            "scan_kind": rec["scan_kind"],
            "dates_run": 0,
            "dates_failed": 0,
            "episodes": 0,
            "pass": 0,
            "fail": 0,
            "unknown": 0,
            "no_setup": 0,
            "data_unavailable": 0,
            "census_b01_episodes": 0,
            "census_b01_pass": 0,
            "census_b01_fail": 0,
            "census_b01_unknown": 0,
            "delta_pass": 0,
            "delta_fail": 0,
            "delta_unknown": 0,
            "wall_seconds": 0.0,
            "peak_rss_bytes_max": 0,
        }
        census_row = census_index.get(cid)
        if census_row is not None:
            slot["census_b01_episodes"] = census_row.get("episodes_b01") or 0
            slot["census_b01_pass"] = census_row.get("pass_b01") or 0
            slot["census_b01_fail"] = census_row.get("fail_b01") or 0
            slot["census_b01_unknown"] = census_row.get("unknown_b01") or 0
        if rec["family"] == "SAINT-AMT":
            slot["stages"] = {key: {"false": 0, "none": 0} for key in STAGE_KEYS}
        if cid == VWAP_COVERAGE_ID:
            slot["census_unknown_to_pass"] = 0
            slot["census_unknown_to_fail"] = 0
            slot["census_unknown_total"] = CENSUS_UNKNOWN_TOTAL
        by_branch[cid] = slot
    missing = []
    for day in dates:
        path = run_root / "jobs" / day / "completion.json"
        if not path.exists():
            missing.append(day)
            continue
        completion = json.loads(path.read_text())
        stats = completion.get("branch_stats") or {}
        for cid, slot in by_branch.items():
            rec = stats.get(cid)
            if rec is None:
                missing.append(f"{day}:{cid}")
                continue
            slot["dates_run"] += 1
            for key in ("episodes", "pass", "fail", "unknown", "no_setup", "data_unavailable"):
                slot[key] += rec.get(key) or 0
            slot["wall_seconds"] += rec.get("wall_seconds") or 0
            rss = rec.get("peak_rss_bytes") or 0
            if rss > slot["peak_rss_bytes_max"]:
                slot["peak_rss_bytes_max"] = rss
            if "stages" in slot and rec.get("stages"):
                for key in STAGE_KEYS:
                    stage = rec["stages"].get(key) or {}
                    slot["stages"][key]["false"] += stage.get("false") or 0
                    slot["stages"][key]["none"] += stage.get("none") or 0
            if cid == VWAP_COVERAGE_ID:
                slot["census_unknown_to_pass"] += rec.get("census_unknown_to_pass") or 0
                slot["census_unknown_to_fail"] += rec.get("census_unknown_to_fail") or 0
    branches = []
    for rec in rows:
        slot = by_branch[rec["coverage_id"]]
        slot["wall_seconds"] = round(slot["wall_seconds"], 4)
        slot["delta_pass"] = slot["pass"] - slot["census_b01_pass"]
        slot["delta_fail"] = slot["fail"] - slot["census_b01_fail"]
        slot["delta_unknown"] = slot["unknown"] - slot["census_b01_unknown"]
        branches.append(slot)
    payload = {
        "schema": SUMMARY_SCHEMA,
        "run_id": ctx["run_id"],
        "run_root": str(run_root),
        "manifest_sha256": ctx["manifest_sha256"],
        "n_dates": len(dates),
        "n_branches": len(rows),
        "job_count": len(dates) * len(rows),
        "dates_first": dates[0],
        "dates_last": dates[-1],
        "branches": branches,
        "missing": missing,
        "census_run_id": CENSUS_RUN_ID,
        "census_unknown_total": CENSUS_UNKNOWN_TOTAL,
        "worker_count": ctx["workers"],
        "cgroup_worker_count": cgroup_worker_count(),
        "achieved_concurrency": (run_meta or {}).get("achieved_concurrency"),
        "wall_seconds_orchestrator": (run_meta or {}).get("wall_seconds_orchestrator"),
        "failed_dates": (run_meta or {}).get("failed_dates") or [],
        **cpu_quota(),
    }
    return payload


def render_md(payload):
    lines = [
        "# Adapter-population full-history summary",
        "",
        f"- Run id: `{payload['run_id']}`",
        f"- Dates: {payload['n_dates']} ({payload['dates_first']} .. {payload['dates_last']})",
        f"- Branches: {payload['n_branches']}",
        f"- Jobs: {payload['job_count']}",
        f"- Workers requested: {payload['worker_count']}; cgroup default {payload['cgroup_worker_count']}; achieved concurrency {payload.get('achieved_concurrency')}",
        f"- Orchestrator wall seconds: {payload.get('wall_seconds_orchestrator')}",
        f"- Census run: `{payload.get('census_run_id')}`",
        "",
        "| branch | dates | episodes | pass | fail | unknown | census B0.1 ep | census B0.1 pass | census B0.1 fail | census B0.1 unknown | delta pass | delta fail | delta unknown | wall s |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["branches"]:
        lines.append(
            f"| `{row['coverage_id']}` | {row['dates_run']} | {row['episodes']} | "
            f"{row['pass']} | {row['fail']} | {row['unknown']} | "
            f"{row['census_b01_episodes']} | {row['census_b01_pass']} | {row['census_b01_fail']} | {row['census_b01_unknown']} | "
            f"{row['delta_pass']} | {row['delta_fail']} | {row['delta_unknown']} | {row['wall_seconds']:.1f} |"
        )
    saint = [row for row in payload["branches"] if row.get("family") == "SAINT-AMT"]
    if saint:
        lines += [
            "",
            "## SAINT stages",
            "",
            "| branch | arrival false | arrival none | alignment false | alignment none | profile false | profile none |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for row in saint:
            stages = row.get("stages") or {}
            arrival = stages.get("arrival_read_recorded") or {}
            alignment = stages.get("alignment_ok") or {}
            profile = stages.get("profile_allows_trade") or {}
            lines.append(
                f"| `{row['coverage_id']}` | {arrival.get('false', 0)} | {arrival.get('none', 0)} | "
                f"{alignment.get('false', 0)} | {alignment.get('none', 0)} | "
                f"{profile.get('false', 0)} | {profile.get('none', 0)} |"
            )
    vwap = next((row for row in payload["branches"] if row.get("coverage_id") == VWAP_COVERAGE_ID), None)
    if vwap is not None:
        lines += [
            "",
            "## GB-VWAP unknowns resolved",
            "",
            (
                f"GB-VWAP source_long resolved {vwap.get('census_unknown_to_pass', 0)} census unknowns to pass "
                f"and {vwap.get('census_unknown_to_fail', 0)} to fail "
                f"(census B0.1 unknown total {payload.get('census_unknown_total', CENSUS_UNKNOWN_TOTAL)})."
            ),
            "",
        ]
    if payload.get("failed_dates"):
        lines += ["", "## Failed dates", "", ", ".join(payload["failed_dates"]), ""]
    if not lines[-1].endswith("\n") and lines[-1] != "":
        lines.append("")
    return "\n".join(lines)


def write_summary(ctx, run_meta):
    payload = aggregate(ctx, run_meta)
    run_root = ctx["run_root"]
    json_path = run_root / "SUMMARY.json"
    md_path = run_root / "SUMMARY.md"
    digest = write_json_atomic(json_path, payload)
    md_path.write_text(render_md(payload))
    if sha256_file(json_path) != digest:
        raise SystemExit("SUMMARY.json hash mismatch")
    return json.loads(json_path.read_text()), digest


def write_run_complete(ctx, payload, summary_sha256, run_meta):
    document = {
        "schema": COMPLETE_SCHEMA,
        "run_id": ctx["run_id"],
        "run_root": str(ctx["run_root"]),
        "manifest_sha256": ctx["manifest_sha256"],
        "summary_sha256": summary_sha256,
        "job_count": payload["job_count"],
        "n_dates": payload["n_dates"],
        "n_branches": payload["n_branches"],
        "failed_dates": payload.get("failed_dates") or [],
        "worker_count": payload["worker_count"],
        "cgroup_worker_count": payload["cgroup_worker_count"],
        "achieved_concurrency": payload.get("achieved_concurrency"),
        "wall_seconds_orchestrator": payload.get("wall_seconds_orchestrator"),
        "completed_at": time.time(),
        **cpu_quota(),
    }
    digest = write_json_atomic(ctx["run_root"] / "RUN_COMPLETE.json", document)
    return document, digest


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=default_workers())
    parser.add_argument("--dates", help="comma-separated subset; manifest still lists all 1742")
    parser.add_argument("--skip-run", action="store_true")
    parser.add_argument("--summarize-only", action="store_true")
    parser.add_argument("--reports-parent", type=Path, default=None)
    parser.add_argument("--baseline", default="B0.1", choices=("B0", "B0.1", "B0.2"))
    args = parser.parse_args(argv)
    workers = args.workers
    ctx = init_run(workers=workers, reports_parent=args.reports_parent, baseline=args.baseline)
    print(
        json.dumps(
            {
                "event": "manifest_ready",
                "run_id": ctx["run_id"],
                "run_root": str(ctx["run_root"]),
                "manifest_sha256": ctx["manifest_sha256"],
                "n_dates": len(ctx["dates"]),
                "n_branches": len(ctx["rows"]),
                "job_count": len(ctx["dates"]) * len(ctx["rows"]),
                "workers": workers,
                "cgroup_worker_count": cgroup_worker_count(),
                **cpu_quota(),
            }
        ),
        flush=True,
    )
    selected = ctx["dates"]
    if args.dates:
        selected = args.dates.split(",")
        unknown = set(selected) - set(ctx["dates"])
        if unknown:
            raise SystemExit(f"dates outside calendar: {sorted(unknown)}")
    run_meta = {
        "job_path_scheme": JOB_PATH_SCHEME,
        "failed_dates": [],
        "achieved_concurrency": 0,
        "wall_seconds_orchestrator": 0.0,
        "worker_count": workers,
    }
    if not args.skip_run and not args.summarize_only:
        first = run_dates(ctx, selected, workers)
        failed = list(first.get("failed_dates") or [])
        second = {
            "date_results": [],
            "failed_dates": failed,
            "wall_seconds_orchestrator": 0.0,
            "achieved_concurrency": 0,
        }
        if failed and not args.dates:
            second = retry_failed(ctx, failed, workers)
            failed = list(second.get("failed_dates") or [])
        run_meta = {
            "job_path_scheme": JOB_PATH_SCHEME,
            "failed_dates": failed,
            "achieved_concurrency": max(first.get("achieved_concurrency") or 0, second.get("achieved_concurrency") or 0),
            "wall_seconds_orchestrator": round(
                (first.get("wall_seconds_orchestrator") or 0) + (second.get("wall_seconds_orchestrator") or 0),
                4,
            ),
            "worker_count": workers,
        }
        write_json_atomic(ctx["run_root"] / "RUN_META.json", run_meta)
        if failed:
            print(json.dumps({"event": "run_incomplete", "failed_dates": failed}), flush=True)
            return 2
    remaining = [
        day
        for day in ctx["dates"]
        if not _completion_ok(ctx["run_root"] / "jobs" / day / "completion.json", ctx, ctx["rows"])
    ]
    if remaining:
        print(
            json.dumps({"event": "not_all_dates", "remaining": len(remaining), "sample": remaining[:12]}),
            flush=True,
        )
        if args.dates:
            return 0
        return 2
    summary, summary_sha = write_summary(ctx, run_meta)
    complete, complete_sha = write_run_complete(ctx, summary, summary_sha, run_meta)
    print(
        json.dumps(
            {
                "event": "run_complete",
                "run_id": ctx["run_id"],
                "manifest_sha256": ctx["manifest_sha256"],
                "summary_sha256": summary_sha,
                "run_complete_sha256": complete_sha,
                "job_count": complete["job_count"],
                "failed_dates": complete["failed_dates"],
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
