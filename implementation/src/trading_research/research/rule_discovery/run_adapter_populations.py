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
from trading_research.research.method_pack.historical_assembly import HistoricalEpisode, window_result
from trading_research.research.method_pack.historical_features import Q, MINUTE, sign
from trading_research.research.method_pack.historical_flow import exact_contact
from trading_research.research.method_pack.historical_outcomes import observe_outcome
from trading_research.research.method_pack.historical_price_scanners import _gb_refs, _known
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
    _record_c7,
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
from trading_research.research.rule_discovery.source_adapters.common import coverage_row, dual_scan, golden_pocket
from trading_research.research.rule_discovery.source_adapters.green_failure import overnight_scan_branches

WORKTREE = Path(__file__).resolve().parents[5]
RUNNER_PATH = Path(__file__).resolve()
REPORTS_PARENT = WORKTREE / "implementation/reports/research-work/adapter-populations"
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

DECISIONS = [
    "Population is the frozen BRANCH_RECORDS table (family, branch, coverage_id, scan_kind).",
    "Persist adapter B0.1 only. dual_scan B0 is not written.",
    "Jobs are jobs/<date>/<branch>.json.gz. Branch names in this population do not collide.",
    "cpu_quota reads cgroup v1 cpu.cfs_quota_us/period first, then v2 cpu.max.",
    "default_workers is floor(quota/period)-5, at least 1 (12 on this machine).",
    "install_write_guard is on. A cache miss fails the date.",
    "load_registry(..., check_software=False) because this runner sits beside frozen baseline_repairs.py.",
    "london_box/asia_box copy the repaired GB-FAIL sweep/reclaim loop from max(09:30, known_at).",
    "overnight_scan concatenates overnight_scan_branches() with begin max(window start, known_at), not 09:30.",
    "golden_pocket_continuation is operational overnight-impulse geometry assembled without HistoricalEpisode.bind.",
    "SAINT dual_scan binds C7 stages after ensure_transforms imports saint.",
    "GB-VWAP joins census B0.1 jobs on candidate_id and counts unknown that become pass or fail.",
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


def build_manifest(registry, dates, workers):
    return {
        "branch_records": [dict(row) for row in BRANCH_RECORDS],
        "branches": list(BRANCH_IDS),
        "census_run_id": CENSUS_RUN_ID,
        "census_summary_sha256": sha256_file(CENSUS_ROOT / "SUMMARY.json"),
        "code_identity": code_identity(),
        "dates": list(dates),
        "registry_sha256": registry["registry_sha256"],
        "schema": MANIFEST_SCHEMA,
        "worker_count": workers,
    }


def job_path(run_root: Path, day: str, branch: str) -> Path:
    return run_root / "jobs" / day / f"{branch}.json.gz"


def init_run(workers=None, reports_parent=None):
    configure_runtime()
    install_write_guard()
    ensure_transforms()
    if workers is None:
        workers = default_workers()
    parent = Path(reports_parent) if reports_parent is not None else REPORTS_PARENT
    registry, _coverage = hr.load_registry(PHASE1_RUN, check_software=False)
    dates = evaluation_dates(registry)
    manifest = build_manifest(registry, dates, workers)
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
        lines = [
            "# Adapter-population full-history work log",
            "",
            f"- Run id: `{run_id}`",
            f"- Manifest sha256: `{digest}`",
            f"- Baseline: `{BASELINE_REPAIR_VERSION}`",
            f"- Dates: {len(dates)} ({dates[0]} .. {dates[-1]})",
            f"- Branches: {len(BRANCH_RECORDS)}",
            f"- Jobs: {len(dates) * len(BRANCH_RECORDS)}",
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
    protocol = registry["scope"]["measurement_protocol"]
    return {
        "run_id": run_id,
        "run_root": run_root,
        "manifest": manifest,
        "manifest_sha256": digest,
        "registry": registry,
        "rows": [dict(row) for row in BRANCH_RECORDS],
        "dates": dates,
        "workers": workers,
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


def _window_start_ns(market):
    document = getattr(market.window, "document", None) or {}
    start = document.get("start_ns", document.get("start"))
    if start is None:
        start = market.at("18:00", -1)
    return start


def _addition_ref(market, name: str):
    if name == "london_box":
        return market.range(market.at("02:00"), market.at("05:00"), "london-box")
    if name == "asia_box":
        return market.range(market.at("20:00", -1), market.at("00:00"), "asia-box")
    raise ValueError(name)


def _gb_fail_sweep(m, branch, refs, omissions, *, begin_for, tdo_required):
    method = "GB-FAIL"
    episodes = []
    for ref in refs:
        if ref is None:
            continue
        begin = begin_for(ref)
        end = m.end
        if begin >= end:
            continue
        if branch == "previous_hour":
            end = min(end, ref["known_at"] + 60 * MINUTE)
        rows = m.bars(begin, end)
        for side in (("long",) if branch == "cash_open_reclaim_case" else ("short", "long")):
            boundary = ref["high"] if side == "short" else ref["low"]
            sg = sign(side)
            trigger = next((r for r in rows if (r["H"] > boundary if side == "short" else r["L"] < boundary)), None)
            if trigger is None:
                continue
            contact = exact_contact(m, trigger, boundary, boundary, strict="above" if side == "short" else "below")
            if contact is None:
                continue
            aligned = trigger["start"] // (5 * MINUTE) * 5 * MINUTE
            sweep_candle_end = aligned + 5 * MINUTE
            path = m.bars(trigger["start"], sweep_candle_end)
            confirm = None
            close = None
            usable = False
            confirm_bar_offset = None
            confirmation_end = sweep_candle_end
            high = low = stop = None
            target = None if branch == "cash_open_reclaim_case" else (ref["low"] if side == "short" else ref["high"])
            if not path:
                omissions.append(
                    {
                        "kind": "availability",
                        "reason": "sweep path empty: no bars known at or before confirmation_end",
                        "window": [trigger["start"], sweep_candle_end],
                        "side": side,
                        "reference_id": ref.get("id"),
                    }
                )
                cand = m.bars(aligned, sweep_candle_end, 300)
                row = cand[0] if cand else None
                if row is not None and row["observed_complete"] and row["C"] is not None:
                    confirm = row
                    close = row["C"]
                    usable = True
                    confirm_bar_offset = 0
            else:
                offset = 0
                while True:
                    bar_start = aligned + offset * 5 * MINUTE
                    bar_end = bar_start + 5 * MINUTE
                    if bar_start >= end:
                        break
                    cand = m.bars(bar_start, bar_end, 300)
                    row = cand[0] if cand else None
                    ok_bar = row is not None and row["observed_complete"] and row["C"] is not None
                    if ok_bar and sg * (row["C"] - boundary) > 0:
                        confirm = row
                        close = row["C"]
                        usable = True
                        confirm_bar_offset = offset
                        confirmation_end = bar_end
                        break
                    if ok_bar and confirm is None:
                        confirm = row
                        close = row["C"]
                        usable = True
                        confirm_bar_offset = offset
                        confirmation_end = bar_end
                    offset += 1
                excursion = m.bars(trigger["start"], confirmation_end) or path
                high = max(r["H"] for r in excursion)
                low = min(r["L"] for r in excursion)
                stop = high + Q if side == "short" else low - Q
                target = ref["low"] if side == "short" else ref["high"]
                if branch == "cash_open_reclaim_case":
                    target = boundary + (boundary - low) * D(".5")
            decision = confirmation_end
            pre = m.range(m.at("06:00"), min(begin, m.at("09:30")), "gb-precontext")
            context_known = pre is not None and pre["known_at"] <= trigger["start"]
            e = HistoricalEpisode(m, method, branch, side, trigger, ref)
            tdo_rows = m.bars(m.at("00:00"), m.at("00:00") + MINUTE)
            tdo = tdo_rows[0]["O"] if tdo_rows else None
            inside = None if close is None else (ref["low"] < close < ref["high"] if ref["low"] != ref["high"] else True)
            e.bind(
                {
                    "reference_frozen": _known(ref),
                    "reference_known_at": ref["known_at"],
                    "reference_px": boundary,
                    "bias_recorded": context_known,
                    "context_at": pre["known_at"] if pre else None,
                    "source_session_allowed": True,
                    "sweep_at": contact["at"],
                    "sweep_high": high,
                    "sweep_low": low,
                    "confirmation_mode": "five_minute_close",
                    "complete_clock_five_minute_bar": True if usable else None,
                    "confirm_at": confirmation_end if confirm else None,
                    "confirm_close": close,
                    "box_return_ok": inside,
                    "tdo_required": tdo_required,
                    "source_tdo_close_confirmed": None if tdo is None or close is None else sg * (close - tdo) > 0,
                    "pocket_required": False,
                    "retracement_entry": False,
                    "risk_defined": None if close is None or stop is None else sg * (close - stop) > 0,
                    "objective_fixed": None if close is None or target is None else sg * (target - close) > 0,
                },
                operation="identified finished reference and first strict sweep; first complete five-minute reclaim at or after the sweep candle; C7 bias_recorded is computed presence with unevaluated direction",
                parents=[ref["id"], trigger["bar_id"]],
                known_at=decision,
                assumption="A2-GB-CLOCK/A2-CONTEXT/A2-STRUCTURAL-RISK",
            )
            e.stage("reference", ref["known_at"], observed=_known(ref)).stage(
                "sweep", contact["at"], observed=True, parents=contact["event_ids"]
            )
            reclaim_details = {"tdo": tdo, "tdo_required": tdo_required, "confirm_bar_offset": confirm_bar_offset}
            if confirm_bar_offset is not None:
                reclaim_details["excursion_bars"] = confirm_bar_offset + 1
            e.stage(
                "five_minute_reclaim",
                confirmation_end,
                observed=None if close is None else sg * (close - boundary) > 0,
                parents=[confirm["bar_id"]] if confirm else [],
                details=reclaim_details,
            )
            if getattr(m, "reconstruct", False):
                e.geometry["confirmation_bar"] = confirm
            structural_false = ["pocket_required", "retracement_entry"]
            if not tdo_required:
                structural_false.append("tdo_required")
            _record_c7(
                e,
                decision,
                (),
                structural_false,
                by_construction=("source_session_allowed",),
                context_direction_unevaluated=True,
            )
            episodes.append(e.finish(decision_at=decision, entry=close, stop=stop, target=target))
    return episodes


def _stamp_addition(document, rec):
    document["coverage_id"] = rec["coverage_id"]
    document["baseline_version"] = BASELINE_REPAIR_VERSION
    return document


def _scan_dual_b01(market, rec):
    family = rec["family"]
    branch = rec["branch"]
    document = dual_scan(market, family, branch)["b01"]
    _attach(document, coverage_row(family, branch), BASELINE_REPAIR_VERSION)
    return document


def _scan_gb_fail_0930(market, rec):
    branch = rec["branch"]
    ref = _addition_ref(market, branch)
    refs = [] if ref is None else [ref]
    omissions: list = []
    episodes = _gb_fail_sweep(
        market,
        branch,
        refs,
        omissions,
        begin_for=lambda item: max(market.at("09:30"), item["known_at"]),
        tdo_required=False,
    )
    result = window_result(market, "GB-FAIL", branch, episodes, omissions=omissions)
    if getattr(market, "reconstruct", False):
        result["reference_selections"] = [item for item in refs if item is not None]
    return _stamp_addition(result, rec)


def _scan_overnight(market, rec):
    episodes = []
    omissions: list = []
    seen: set[str] = set()
    window_start = _window_start_ns(market)
    for name in overnight_scan_branches():
        if name in {"london_box", "asia_box"}:
            ref = _addition_ref(market, name)
            refs = [] if ref is None else [ref]
            tdo_required = False
        else:
            refs, extra = _gb_refs(market, name)
            omissions.extend(extra)
            tdo_required = name == "asia_tdo_case"
        # Overnight starts at known-at inside the loaded account-day, not 09:30.
        part = _gb_fail_sweep(
            market,
            "overnight_scan",
            refs,
            omissions,
            begin_for=lambda item, start=window_start: max(start, item["known_at"]),
            tdo_required=tdo_required,
        )
        for episode in part:
            episode["overnight_of"] = name
            geometry = dict(episode.get("geometry") or {})
            geometry["overnight_of"] = name
            episode["geometry"] = geometry
            cid = episode["candidate_id"]
            if cid in seen:
                episode["candidate_id"] = f"{name}:{cid}"
            seen.add(episode["candidate_id"])
            episodes.append(episode)
    result = window_result(market, "GB-FAIL", "overnight_scan", episodes, omissions=omissions)
    return _stamp_addition(result, rec)


def _golden_episode(market, impulse, side, pocket, pullback, confirm, verdict):
    lo, hi = (None, None) if pocket is None else pocket
    if side == "long":
        stop = None if lo is None else lo - Q
        target = impulse.get("high")
    elif side == "short":
        stop = None if hi is None else hi + Q
        target = impulse.get("low")
    else:
        stop = None
        target = None
    entry = None if confirm is None else confirm.get("C")
    if confirm is not None:
        decision_at = confirm.get("known_at")
    elif pullback is not None:
        decision_at = pullback.get("known_at")
    else:
        decision_at = impulse.get("known_at")
    identity = {
        "method": "GB-SCALP",
        "branch": "golden_pocket_continuation",
        "side": side,
        "session_date": str(market.day),
        "instrument_id": market.instrument_id,
        "reference_id": impulse.get("id"),
    }
    status = {"pass": "setup", "fail": "no_setup", "unknown": "data_unavailable"}[verdict]
    return {
        "schema": "phase1-historical-episode-v2",
        "candidate_id": "adapter:golden_pocket_continuation:" + content_hash(identity)[:32],
        "method": "GB-SCALP",
        "branch": "golden_pocket_continuation",
        "side": side,
        "session_date": str(market.day),
        "instrument_id": market.instrument_id,
        "decision_at": decision_at,
        "values": {
            "branch": "golden_pocket_continuation",
            "side": side,
            "operational_rule_label": "operational",
            "decision_at": decision_at,
        },
        "research_verdict": verdict,
        "failed": [],
        "unknown": [] if verdict == "pass" else ["qualifying_close"],
        "strategy_assessment": {"status": status, "scope": "entry_setup"},
        "reference": impulse,
        "trigger": pullback if pullback is not None else impulse,
        "geometry": {
            "impulse": impulse,
            "pocket": None if pocket is None else {"low": lo, "high": hi},
            "pullback": pullback,
            "entry": entry,
            "stop": stop,
            "target": target,
            "operational_rule_label": "operational",
        },
        "actual_trade": False,
        "faithful_eligible": False,
        "author_exact_verdict": "unknown",
        "input_sha256": market.window.document["input_sha256"],
    }


def _scan_golden_pocket(market, rec):
    branch = rec["branch"]
    impulse = market.range(market.at("18:00", -1), market.at("09:30"), "overnight-impulse")
    if impulse is None:
        return _stamp_addition(window_result(market, "GB-SCALP", branch, []), rec)
    open_px = impulse.get("open")
    close_px = impulse.get("close")
    if open_px is None or close_px is None:
        episode = _golden_episode(market, impulse, None, None, None, None, "unknown")
        return _stamp_addition(window_result(market, "GB-SCALP", branch, [episode]), rec)
    side = "long" if close_px > open_px else "short"
    lo, hi = golden_pocket(impulse["low"], impulse["high"])
    bars = market.bars(market.at("09:30"), market.end, 300)
    pullback_i = None
    for i, row in enumerate(bars):
        if not row.get("observed_complete"):
            continue
        low, high = row.get("L"), row.get("H")
        if low is None or high is None:
            continue
        if low <= hi and high >= lo:
            pullback_i = i
            break
    confirm = None
    pullback = None if pullback_i is None else bars[pullback_i]
    if pullback_i is not None:
        for row in bars[pullback_i + 1 :]:
            if not row.get("observed_complete") or row.get("C") is None:
                continue
            close = row["C"]
            if side == "long" and close > hi:
                confirm = row
                break
            if side == "short" and close < lo:
                confirm = row
                break
    verdict = "pass" if confirm is not None else "unknown"
    episode = _golden_episode(market, impulse, side, (lo, hi), pullback, confirm, verdict)
    return _stamp_addition(window_result(market, "GB-SCALP", branch, [episode]), rec)


_SCANNERS = {
    "dual_b01": _scan_dual_b01,
    "gb_fail_0930": _scan_gb_fail_0930,
    "overnight": _scan_overnight,
    "golden_pocket": _scan_golden_pocket,
}


def _scan_record(market, rec):
    scanner = _SCANNERS[rec["scan_kind"]]
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
        path = job_path(run_root, day, rec["branch"])
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
                document["baseline_version"] = document.get("baseline_version") or BASELINE_REPAIR_VERSION
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
    args = parser.parse_args(argv)
    workers = args.workers
    ctx = init_run(workers=workers, reports_parent=args.reports_parent)
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
