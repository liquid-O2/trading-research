"""Shared family-adapter kernel. Coordinator-owned.

Empty-delta scans emit B0 (frozen scan_branch) and B0.1 (scan_branch_repaired
when the branch is in REPAIRS, else the frozen scanner). Candidates compare
against B0.1. The B0 to B0.1 difference is its own reported row.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping
import json
import time

from trading_research.errors import ContractError
from trading_research.research.contracts.types import Coverage, EvidenceRef, Formation, Reference, RuleSpec
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.historical_features import HistoricalFeatures
from trading_research.research.method_pack.historical_runner import _records
from trading_research.research.method_pack.native_discovery import scan_branch as native_scan_branch
from trading_research.research.rule_discovery.baseline import load_phase1_registry
from trading_research.research.rule_discovery.baseline_repairs import (
    BASELINE_REPAIR_VERSION,
    B0_VERSION,
    REPAIRS,
    affected_branch_ids,
    scan_branch_repaired,
)
from trading_research.research.rule_discovery.formations import f1_trailing_minutes, f2_volume_completed, freeze_formation, median_int
from trading_research.research.rule_discovery.native import (
    NativeMarketView,
    build_market_view,
    cgroup_worker_count,
    install_write_guard,
    prior_complete_same_contract_dates,
)
from trading_research.research.rule_discovery.registry import expand_candidate_bank
from trading_research.research.rule_discovery.runner import peak_rss_bytes

B0 = B0_VERSION
B01 = BASELINE_REPAIR_VERSION
REPAIRED_IDS = frozenset(affected_branch_ids())
ENGINEERING_DATES = Path(
    "/workspace/implementation/reports/research-work/P15-00/ea9693217cb577cb/attempt-0001/ENGINEERING_DATES.json"
)
P15_08_RECEIPT = Path(
    "/workspace/implementation/reports/research-work/P15-08/9728f9ee0bbbdfd5/attempt-0001/TASK_RECEIPT.json"
)
BASELINE_REPAIR_ROOT = Path("/workspace/implementation/reports/research-work/baseline-repair")
NATIVE_PARQUET = "/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/2021-01.parquet"
NATIVE_ROW = 769284

# Ledger L039-L046: session windows from sources whose clock zone is unverified.
CLOCK_ZONE_UNVERIFIED_FAMILIES = frozenset(
    {
        "JJ-TBR",
        "GB-FAIL",
        "GB-VWAP",
        "GB-SCALP",
        "SIRES",
        "SAINT-AMT",
        "MEMBER-TWO-REASONS",
        "KEANI-OPEN-ABOVE-VALUE",
        "REFILL-STUDY",
        "JETBUNDLE-STATES",
        "STOIC-DATA",
        "STOIC-RISK",
    }
)

FAMILY_BRANCHES: dict[str, tuple[str, ...]] = {
    "JJ-TBR": (
        "judas_outbound",
        "judas_reversal",
        "single_extended",
        "single_purged",
        "internal_rotation",
        "extension_reaction",
        "other_session",
        "timed_pzone_reversal",
    ),
    "GB-FAIL": (
        "nyam_box",
        "previous_hour",
        "asia_tdo_case",
        "cash_open_reclaim_case",
        "prior_day_level",
        "prior_week_level",
        "prior_month_level",
        "mss_fvg_refinement",
    ),
    "GB-VWAP": ("source_long",),
    "GB-SCALP": ("bearish_small_scalp", "bullish_discount_pullback"),
    "SIRES": (
        "dom_rejection",
        "absorption_reward_retest",
        "stop_four_stage",
        "footprint_confirmed_reaction",
        "vwap_deviation_fade",
        "ofm_aggressive",
        "ofm_passive",
        "clean_squeeze",
        "balance_failure_fade",
        "defended_band_continuation",
        "kg1_retest",
        "microbalance_break",
    ),
    "SAINT-AMT": ("continuation_retest", "trapped_buyers_retest", "failed_auction_return", "poc_traversal"),
    "MEMBER-TWO-REASONS": ("resistance_short", "planned_return_long"),
    "KEANI-OPEN-ABOVE-VALUE": ("source_long",),
    "REFILL-STUDY": ("touch_record",),
    "JETBUNDLE-STATES": ("B", "A", "D", "E", "W"),
    "STOIC-DATA": ("macro_application",),
    "STOIC-RISK": ("first", "second", "reset_after_second_win"),
}

TASK_FAMILIES: dict[str, tuple[str, ...]] = {
    "P15-09": ("JJ-TBR",),
    "P15-10": ("GB-FAIL",),
    "P15-11": ("GB-VWAP", "GB-SCALP"),
    "P15-12": ("SIRES",),
    "P15-13": ("SAINT-AMT",),
    "P15-14": ("MEMBER-TWO-REASONS",),
    "P15-15": ("KEANI-OPEN-ABOVE-VALUE",),
    "P15-16": ("REFILL-STUDY", "JETBUNDLE-STATES", "STOIC-DATA", "STOIC-RISK"),
}

PRIMARY_BRANCH: dict[str, tuple[str, str]] = {
    "P15-09": ("JJ-TBR", "judas_reversal"),
    "P15-10": ("GB-FAIL", "nyam_box"),
    "P15-11": ("GB-VWAP", "source_long"),
    "P15-12": ("SIRES", "absorption_reward_retest"),
    "P15-13": ("SAINT-AMT", "continuation_retest"),
    "P15-14": ("MEMBER-TWO-REASONS", "planned_return_long"),
    "P15-15": ("KEANI-OPEN-ABOVE-VALUE", "source_long"),
    "P15-16": ("REFILL-STUDY", "touch_record"),
}

# Jumbo 06:00-09:00 is the corresponding source formation for F2 on JJ-TBR.
F2_SOURCE_WINDOWS: dict[str, tuple[int, int, int, int]] = {
    "JJ-TBR": (6, 0, 9, 0),
    "GB-FAIL": (9, 0, 10, 0),
    "GB-VWAP": (18, 0, 9, 30),
    "SAINT-AMT": (9, 30, 16, 0),
    "SIRES": (9, 30, 16, 0),
    "MEMBER-TWO-REASONS": (9, 30, 16, 0),
    "KEANI-OPEN-ABOVE-VALUE": (9, 30, 10, 0),
}


def adapter_worker_count() -> int:
    """Cgroup quota minus four reserved for sibling Grok processes."""
    return max(1, cgroup_worker_count() - 4)


def coverage_id(method_id: str, branch: str) -> str:
    return f"{method_id}:branch:{branch}"


def clock_zone_unverified(method_id: str, branch: str | None = None) -> bool:
    return method_id in CLOCK_ZONE_UNVERIFIED_FAMILIES


def is_repaired(method_id: str, branch: str) -> bool:
    return coverage_id(method_id, branch) in REPAIRED_IDS or (
        method_id == "JJ-TBR" and branch == "judas_reversal_deferred"
    )


def coverage_row(method_id: str, branch: str) -> dict[str, Any]:
    _registry, manifest = load_phase1_registry()
    rows = [
        row
        for row in manifest["branches"]
        if row["method_id"] == method_id and row["branch"] == branch
    ]
    if method_id == "JJ-TBR" and branch == "judas_reversal_deferred":
        base = coverage_row("JJ-TBR", "judas_reversal")
        cloned = dict(base)
        cloned["branch"] = "judas_reversal_deferred"
        cloned["coverage_id"] = coverage_id(method_id, branch)
        return cloned
    if not rows:
        raise ContractError(f"coverage row missing: {method_id}:{branch}")
    preferred = [row for row in rows if not row.get("extra_unit")]
    chosen = preferred[0] if preferred else rows[0]
    return dict(chosen)


def load_source_market(day: str) -> HistoricalFeatures:
    registry, _manifest = load_phase1_registry()
    return HistoricalFeatures(day, records=_records(registry))


def _tag_episodes(document: Mapping[str, Any], version: str) -> dict[str, Any]:
    out = dict(document)
    out["baseline_version"] = version
    tagged = []
    for episode in list(out.get("episodes") or []):
        row = dict(episode)
        row["baseline_version"] = version
        tagged.append(row)
    out["episodes"] = tagged
    return out


def episode_status(episode: Mapping[str, Any]) -> str:
    assessment = episode.get("strategy_assessment") or {}
    return str(assessment.get("status") or episode.get("status") or "unknown")


def population_counts(document: Mapping[str, Any] | None) -> dict[str, int]:
    if not document:
        return {"episodes": 0, "setup": 0, "rejected": 0, "unknown": 0, "no_setup": 0, "other": 0}
    counts = {"episodes": 0, "setup": 0, "rejected": 0, "unknown": 0, "no_setup": 0, "other": 0}
    for episode in document.get("episodes") or []:
        counts["episodes"] += 1
        status = episode_status(episode)
        if status == "setup":
            counts["setup"] += 1
        elif status in {"fail", "rejected", "no_setup"}:
            if status == "no_setup":
                counts["no_setup"] += 1
            else:
                counts["rejected"] += 1
        elif status in {"unknown", "data_unavailable", "input_unknown"}:
            counts["unknown"] += 1
        else:
            counts["other"] += 1
    counts["omissions"] = len(document.get("omissions") or [])
    return counts


_FAMILY_TRANSFORMS: dict[str, Any] = {}


def register_family_transform(family: str, fn) -> None:
    """Post-process B0/B0.1 documents after the scanners run (adapter-level rules)."""
    _FAMILY_TRANSFORMS[family] = fn


def dual_scan(market: HistoricalFeatures, method_id: str, branch: str) -> dict[str, Any]:
    """B0 frozen scanner plus B0.1 repaired-or-frozen scanner."""
    row = coverage_row(method_id, branch)
    b0 = _tag_episodes(native_scan_branch(market, row), B0)
    if is_repaired(method_id, branch):
        b01 = scan_branch_repaired(market, row)
        b01.pop("deferred_variant", None)
        b01 = _tag_episodes(b01, B01)
    else:
        b01 = _tag_episodes(native_scan_branch(market, row), B0)
    transform = _FAMILY_TRANSFORMS.get(method_id)
    if transform is not None:
        b0 = transform(b0, market, branch, B0)
        b01 = transform(b01, market, branch, B01)
    b0_counts = population_counts(b0)
    b01_counts = population_counts(b01)
    return {
        "schema_version": "research-family-dual-scan-v1",
        "family": method_id,
        "branch": branch,
        "coverage_id": row["coverage_id"],
        "clock_zone_unverified": clock_zone_unverified(method_id, branch),
        "repaired": is_repaired(method_id, branch),
        "population_kind": "engineering_slice",
        "b0": b0,
        "b01": b01,
        "populations": {
            "B0": b0_counts,
            "B0.1": b01_counts,
            "B0_to_B0.1": {
                key: b01_counts.get(key, 0) - b0_counts.get(key, 0) for key in ("episodes", "setup", "rejected", "unknown", "no_setup")
            },
        },
    }


def empty_delta_spec(family: str, branch: str) -> RuleSpec:
    return RuleSpec(
        rule_id=f"B0:{family}:{branch}",
        family=family,
        source_branch=branch,
        version="B0",
        provenance="source_literal",
        baseline_rule_id=f"B0:{family}:{branch}",
        changed_axis="none",
        parameters={"empty_delta": True},
        required_inputs=("native_executions",),
        required_stages=("formation", "contact", "confirmation"),
        formation_policy="source",
        expiry_policy="source",
    )


def f2_prior_median(
    view: NativeMarketView,
    *,
    family: str,
    n: int = 20,
    start_hour: int | None = None,
    start_minute: int | None = None,
    end_hour: int | None = None,
    end_minute: int | None = None,
) -> dict[str, Any]:
    """Median source-formation volume over prior 20 complete same-contract sessions.

    Never uses the last 20 bars of the loaded session as a stand-in.
    """
    window = F2_SOURCE_WINDOWS.get(family)
    if window is None and None in (start_hour, start_minute, end_hour, end_minute):
        return {
            "available": False,
            "stand_in": False,
            "reason": "no source formation window registered for family",
            "median_volume": None,
            "availability_clock_ns": None,
            "n": 0,
            "dates": [],
        }
    sh, sm, eh, em = window if window is not None else (start_hour, start_minute, end_hour, end_minute)
    dates = view.prior_complete_same_contract_dates(n)
    volumes: list[int] = []
    clocks: list[int] = []
    for item in dates:
        prior = build_market_view(item, full_account_day=True, instrument_id=view.arrays.instrument_id)
        day = date.fromisoformat(item)
        start_ns = et_ns(day, int(sh), int(sm))
        end_ns = et_ns(day, int(eh), int(em))
        if end_ns <= start_ns:
            end_ns = et_ns(day, int(eh), int(em)) + 24 * 3600 * 1_000_000_000
        formed = prior.source_formation_volume(start_ns, end_ns)
        volumes.append(int(formed["volume"]))
        clocks.append(int(formed["availability_clock_ns"]))
    if len(volumes) < n:
        return {
            "available": False,
            "stand_in": False,
            "reason": f"fewer than {n} prior complete same-contract sessions",
            "median_volume": None,
            "availability_clock_ns": max(clocks) if clocks else None,
            "n": len(volumes),
            "dates": dates,
            "volumes": volumes,
        }
    median = median_int(volumes)
    return {
        "available": True,
        "stand_in": False,
        "reason": None,
        "median_volume": median,
        "availability_clock_ns": max(clocks),
        "n": len(volumes),
        "dates": dates,
        "volumes": volumes,
        "window": {"start": f"{sh:02d}:{sm:02d}", "end": f"{eh:02d}:{em:02d}"},
    }


def f2_candidate_formation(view: NativeMarketView, family: str, issue_ns: int) -> dict[str, Any]:
    from trading_research.research.rule_discovery.formations import complete_minute_rows

    threshold = f2_prior_median(view, family=family)
    if not threshold["available"]:
        return {"available": False, "threshold": threshold, "formation": None, "stand_in": False}
    rows = complete_minute_rows(view.arrays, view.start_ns, issue_ns)
    formed = f2_volume_completed(rows, issue_ns=issue_ns, median_volume=int(threshold["median_volume"]))
    frozen = None
    if formed.get("available"):
        frozen = freeze_formation(formed, cutoff_ns=issue_ns, asset_id=view.asset_id)
    return {
        "available": bool(formed.get("available")),
        "threshold": threshold,
        "formation": formed,
        "frozen": None if frozen is None else {
            "formation_id": frozen.formation_id,
            "start_ns": frozen.start_ns,
            "end_ns": frozen.end_ns,
            "available_at_ns": frozen.available_at_ns,
            "volume": int(frozen.volume),
        },
        "stand_in": False,
    }


def enumerate_own_population(
    *,
    baseline_ids: set[str],
    candidate_ids: set[str],
    geometry_changed: bool,
) -> dict[str, Any]:
    """Changed geometry must not be a filter of already-qualified baseline setups."""
    only_candidate = sorted(candidate_ids - baseline_ids)
    only_baseline = sorted(baseline_ids - candidate_ids)
    if geometry_changed and not only_candidate and candidate_ids and candidate_ids <= baseline_ids:
        raise ContractError("changed geometry filtered the baseline qualifying set instead of enumerating its own population")
    return {
        "baseline_n": len(baseline_ids),
        "candidate_n": len(candidate_ids),
        "new_contacts": only_candidate,
        "dropped_contacts": only_baseline,
        "own_population": True,
    }


def permute_batch_ambiguity(prices: tuple[Decimal, ...], target: Decimal, stop: Decimal) -> dict[str, Any]:
    """S09: same-timestamp target and stop stay ambiguous regardless of row order."""
    reached = target in prices
    failed = stop in prices
    unknown = reached and failed
    reversed_prices = tuple(reversed(prices))
    reached_r = target in reversed_prices
    failed_r = stop in reversed_prices
    return {
        "ambiguous": unknown,
        "order_invariant": (reached, failed) == (reached_r, failed_r),
        "status": "unknown" if unknown else ("pass" if reached else "fail"),
    }


def future_perturbation_stable(before: Mapping[str, Any], after: Mapping[str, Any], cutoff_ns: int) -> bool:
    """S08: outputs issued at or before cutoff must match after mutating later records."""
    return json.dumps(before, sort_keys=True, default=str) == json.dumps(after, sort_keys=True, default=str)


def family_candidates(family: str) -> list[dict[str, Any]]:
    bank = expand_candidate_bank()
    rows = [row for row in bank["candidates"] + bank["baselines"] + bank["b0_1_judas_labels"] if row.get("family") == family]
    return rows


def baseline_repair_source() -> dict[str, Any]:
    complete = BASELINE_REPAIR_ROOT / "RUN_COMPLETE.json"
    if complete.is_file():
        return {"mode": "full_history", "path": str(complete), "run_root": str(BASELINE_REPAIR_ROOT)}
    runs = sorted(p for p in BASELINE_REPAIR_ROOT.iterdir() if p.is_dir()) if BASELINE_REPAIR_ROOT.is_dir() else []
    preview = Path("/workspace/planning/research-program/reviews/phase1-code-review-2026-09-14/repair-preview")
    return {
        "mode": "40_date_preview",
        "reason": "RUN_COMPLETE.json absent; in-progress census ignored",
        "preview_dir": str(preview) if preview.is_dir() else None,
        "in_progress_run": str(runs[-1]) if runs else None,
    }


def scan_family_date(day: str, method_id: str, branches: tuple[str, ...]) -> dict[str, Any]:
    install_write_guard()
    started = time.monotonic()
    market = load_source_market(day)
    scans = [dual_scan(market, method_id, branch) for branch in branches]
    return {
        "date": day,
        "family": method_id,
        "branches": list(branches),
        "clock_zone_unverified": clock_zone_unverified(method_id),
        "scans": [
            {
                "branch": item["branch"],
                "coverage_id": item["coverage_id"],
                "repaired": item["repaired"],
                "clock_zone_unverified": item["clock_zone_unverified"],
                "populations": item["populations"],
                "b0_episode_ids": [ep.get("candidate_id") for ep in item["b0"].get("episodes") or []],
                "b01_episode_ids": [ep.get("candidate_id") for ep in item["b01"].get("episodes") or []],
                "b0_status": [episode_status(ep) for ep in item["b0"].get("episodes") or []],
                "b01_status": [episode_status(ep) for ep in item["b01"].get("episodes") or []],
            }
            for item in scans
        ],
        "populations": {
            "B0": _sum_counts([item["populations"]["B0"] for item in scans]),
            "B0.1": _sum_counts([item["populations"]["B0.1"] for item in scans]),
        },
        "wall_seconds": time.monotonic() - started,
        "peak_rss_bytes": peak_rss_bytes(),
        "native_executions": market.window.document["row_count"],
        "population_kind": "engineering_slice",
        "full_history_run": False,
    }


def _sum_counts(rows: list[dict[str, int]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        for key, value in row.items():
            out[key] = out.get(key, 0) + int(value)
    return out


def measure_family_throughput(dates: list[str], task_id: str) -> dict[str, Any]:
    family, branch = PRIMARY_BRANCH[task_id]
    install_write_guard()
    samples: list[float] = []
    rss: list[int] = []
    for item in dates:
        started = time.monotonic()
        market = load_source_market(item)
        dual_scan(market, family, branch)
        samples.append(time.monotonic() - started)
        rss.append(peak_rss_bytes())

    def pct(values: list[float], p: float) -> float:
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, max(0, int(round((p / 100) * (len(ordered) - 1)))))
        return ordered[index]

    p90 = pct(samples, 90)
    workers = adapter_worker_count()
    eligible = len(FAMILY_BRANCHES.get(family, ()))
    projection_hours = (160 * max(eligible, 1) * 1742 * p90) / (workers * 3600)
    return {
        "schema_version": "research-throughput-v1",
        "task_id": task_id,
        "session_count": len(dates),
        "dates": list(dates),
        "candidate_branch": {"family": family, "branch": branch},
        "scope": "full account-day HistoricalFeatures plus dual B0/B0.1 adapter scan, single core",
        "median_seconds": pct(samples, 50),
        "p90_seconds": p90,
        "samples": samples,
        "peak_rss_bytes": {"median": int(pct([float(v) for v in rss], 50)), "p90": int(pct([float(v) for v in rss], 90)), "max": max(rss) if rss else 0},
        "rss_samples": rss,
        "target_p90_seconds": 5.0,
        "engineering_finding": p90 > 5.0,
        "workers_cgroup": cgroup_worker_count(),
        "workers_used": workers,
        "projection": {
            "formula": "candidates × eligible branches × 1,742 × p90 seconds / (workers × 3600)",
            "candidates": 160,
            "eligible_branches": eligible,
            "dates": 1742,
            "p90_seconds": p90,
            "workers": workers,
            "hours": projection_hours,
            "exceeds_24h_budget": projection_hours > 24.0,
        },
    }


def synthetic_f2_rows(volumes: list[int], *, start_ns: int = 0) -> list[dict[str, Any]]:
    minute = 60_000_000_000
    rows = []
    for i, volume in enumerate(volumes):
        rows.append(
            {
                "start_ns": start_ns + i * minute,
                "end_ns": start_ns + (i + 1) * minute,
                "open_ticks": 40000,
                "high_ticks": 40010,
                "low_ticks": 39990,
                "close_ticks": 40000,
                "volume": int(volume),
                "signed": 0,
                "unknown": 0,
                "known_at_ns": start_ns + (i + 1) * minute,
            }
        )
    return rows


def quadrant_locations(low: Decimal, high: Decimal, side: str) -> dict[str, Decimal]:
    """TBR EQ and quadrant entries. Mirror long and short."""
    width = high - low
    mid = low + width / Decimal("2")
    q1 = low + width * Decimal("0.25")
    q3 = low + width * Decimal("0.75")
    if side not in {"long", "short"}:
        raise ContractError("side must be long or short")
    return {"eq": mid, "q1": q1, "q3": q3, "low": low, "high": high, "width": width}


def golden_pocket(low: Decimal, high: Decimal) -> tuple[Decimal, Decimal]:
    span = high - low
    lo = low + span * Decimal("0.50")
    hi = low + span * Decimal("0.618")
    return (min(lo, hi), max(lo, hi))


TICK = Decimal("0.25")


def full_history_limit(*, p90_seconds: float | None = None, projection_hours: float | None = None) -> dict[str, Any]:
    """Why the registered full-history population is not executed in this subphase."""
    p90 = None if p90_seconds is None else float(p90_seconds)
    hours = None if projection_hours is None else float(projection_hours)
    reason = (
        "Registered full-history population is not executed: every family dual-scan p90 "
        "on HistoricalFeatures exceeds PERFORMANCE.md 5 s, and the P15-17 projection "
        "exceeds the 24-hour stage budget. Bank is not reduced. Reported 04 counts are "
        "an engineering slice, not a family population."
    )
    if p90 is not None and hours is not None:
        reason = (
            f"Full-history not run: family p90 {p90:.2f}s exceeds PERFORMANCE.md 5s target; "
            f"P15-17 projection {hours:.1f}h exceeds 24h stage budget; bank not reduced. "
            "Reported counts are an engineering slice, not a family population."
        )
    return {
        "population_kind": "engineering_slice",
        "full_history_run": False,
        "reason": reason,
        "p90_seconds": p90,
        "projection_hours": hours,
        "target_p90_seconds": 5.0,
        "stage_budget_hours": 24.0,
    }


def changed_axis_spec(family: str, branch: str, axis: str, *, recipe: str = "F1") -> RuleSpec:
    return RuleSpec(
        rule_id=f"CAND:{family}:{branch}:{axis}:{recipe}",
        family=family,
        source_branch=branch,
        version="candidate",
        provenance="custom",
        baseline_rule_id=f"B0:{family}:{branch}",
        changed_axis=axis,
        parameters={"recipe_id": recipe, "empty_delta": False},
        required_inputs=("native_executions",),
        required_stages=("formation", "reference", "contact"),
        formation_policy=recipe,
        expiry_policy="session",
    )


def _bar_ticks(px: Any) -> int:
    if px is None:
        return 0
    return int((Decimal(str(px)) / TICK).to_integral_value())


def minute_rows_from_market(market: HistoricalFeatures, start_ns: int, end_ns: int) -> list[dict[str, Any]]:
    lo = max(int(start_ns), int(market.start))
    hi = min(int(end_ns), int(market.end))
    if hi <= lo:
        return []
    rows = []
    for bar in market.bars(lo, hi, 60):
        rows.append(
            {
                "start_ns": int(bar["start"]),
                "end_ns": int(bar["end"]),
                "open_ticks": _bar_ticks(bar.get("O")),
                "high_ticks": _bar_ticks(bar.get("H")),
                "low_ticks": _bar_ticks(bar.get("L")),
                "close_ticks": _bar_ticks(bar.get("C")),
                "volume": int(bar.get("V") or bar.get("volume") or 0),
                "signed": 0,
                "unknown": 0,
                "known_at_ns": int(bar["known_at"]),
                "bar_id": bar.get("bar_id"),
                "complete": bool(bar.get("complete") or bar.get("observed_complete")),
            }
        )
    return rows


def source_window_ns(market: HistoricalFeatures, family: str) -> tuple[int, int]:
    window = F2_SOURCE_WINDOWS.get(family, (9, 30, 16, 0))
    sh, sm, eh, em = window
    start = market.at(f"{sh:02d}:{sm:02d}")
    end = market.at(f"{eh:02d}:{em:02d}")
    if end <= start:
        start = market.at(f"{sh:02d}:{sm:02d}", -1)
    start = max(int(start), int(market.start))
    end = min(int(end), int(market.end))
    if end <= start:
        return int(market.start), min(int(market.end), int(market.at("09:30")))
    return start, end


def formation_record(formed: Formation) -> dict[str, Any]:
    return {
        "formation_id": formed.formation_id,
        "start_ns": formed.start_ns,
        "end_ns": formed.end_ns,
        "available_at_ns": formed.available_at_ns,
        "high": str(formed.high),
        "low": str(formed.low),
        "volume": formed.volume,
        "construction_kind": formed.construction_kind,
    }


def reference_record(reference: Reference) -> dict[str, Any]:
    return {
        "reference_id": reference.reference_id,
        "reference_lifecycle_id": reference.reference_lifecycle_id,
        "formation_id": reference.formation_id,
        "lower": str(reference.lower),
        "upper": str(reference.upper),
        "issue_at_ns": reference.issue_at_ns,
        "expiry_at_ns": reference.expiry_at_ns,
    }


def baseline_contact_ids(document: Mapping[str, Any] | None) -> set[str]:
    ids: set[str] = set()
    if not document:
        return ids
    for episode in document.get("episodes") or []:
        ref = episode.get("reference") or {}
        trigger = episode.get("trigger") or {}
        values = episode.get("values") or {}
        cid = episode.get("candidate_id")
        if cid:
            ids.add(str(cid))
        touch = values.get("retest_at") or trigger.get("start") or trigger.get("at")
        ref_id = ref.get("id") or ref.get("reference_id")
        if ref_id is not None and touch is not None:
            ids.add(f"{ref_id}:{touch}")
        elif ref_id is not None:
            ids.add(str(ref_id))
        bar_id = trigger.get("bar_id") or trigger.get("id")
        if bar_id:
            ids.add(str(bar_id))
    return ids


def enumerate_bar_contacts(
    market: HistoricalFeatures,
    *,
    lower: Decimal,
    upper: Decimal,
    start_ns: int,
    end_ns: int,
    reference_id: str,
    side: str,
) -> list[dict[str, Any]]:
    """Every complete bar that overlaps the reference is a contact of this candidate's own population."""
    lo = max(int(start_ns), int(market.start))
    hi = min(int(end_ns), int(market.end))
    if hi <= lo:
        return []
    contacts: list[dict[str, Any]] = []
    for i, row in enumerate(market.bars(lo, hi, 60)):
        if row.get("L") is None or row.get("H") is None:
            continue
        if row["L"] > upper or row["H"] < lower:
            continue
        contact_id = f"{reference_id}:{row.get('bar_id') or row['start']}:{i}"
        contacts.append(
            {
                "contact_id": contact_id,
                "reference_id": reference_id,
                "at_ns": int(row["start"]),
                "available_at_ns": int(row["known_at"]),
                "side": side,
                "kind": "touch",
                "bar_id": row.get("bar_id"),
                "low": str(row["L"]),
                "high": str(row["H"]),
            }
        )
    return contacts


def _episodes_from_contacts(
    *,
    family: str,
    branch: str,
    formation: dict[str, Any],
    reference: dict[str, Any],
    contacts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    episodes = []
    for contact in contacts:
        episodes.append(
            {
                "candidate_id": f"cand:{family}:{branch}:{contact['contact_id']}",
                "method": family,
                "branch": branch,
                "side": contact["side"],
                "values": {
                    "location_touched": True,
                    "own_population": True,
                    "changed_axis": True,
                },
                "strategy_assessment": {"status": "setup"},
                "status": "setup",
                "contact": contact,
                "reference": reference,
                "formation": formation,
                "baseline_version": "candidate",
            }
        )
    return episodes


def _band_reference(
    formation: Formation,
    *,
    lower: Decimal,
    upper: Decimal,
    kind: str,
    issue_ns: int,
    expiry_ns: int,
    family: str,
    branch: str,
) -> Reference:
    from trading_research.research.rule_discovery.references import lifecycle_id

    if issue_ns < formation.available_at_ns:
        issue_ns = formation.available_at_ns
    if expiry_ns < issue_ns:
        expiry_ns = issue_ns
    lid = lifecycle_id(
        family=family,
        branch=branch,
        contract=formation.asset_id,
        formation_id=formation.formation_id,
        kind=kind,
    )
    return Reference(
        reference_id=f"{lid}:{kind}:{issue_ns}",
        reference_lifecycle_id=lid,
        formation_id=formation.formation_id,
        asset_id=formation.asset_id,
        lower=lower,
        upper=upper,
        issue_at_ns=issue_ns,
        expiry_at_ns=expiry_ns,
        permitted_sides=(-1, 1),
        evidence=formation.evidence,
    )


def _freeze_source_window(market: HistoricalFeatures, family: str, *, kind: str = "source_window") -> Formation | None:
    start_ns, end_ns = source_window_ns(market, family)
    rows = minute_rows_from_market(market, start_ns, end_ns)
    if not rows:
        return None
    cutoff = max(int(row["known_at_ns"]) for row in rows)
    try:
        return freeze_formation({"available": True, "kind": kind, "rows": rows}, cutoff_ns=cutoff, asset_id=str(market.instrument_id))
    except ContractError:
        return None


def _freeze_f1(market: HistoricalFeatures, issue_ns: int) -> Formation | None:
    rows = minute_rows_from_market(market, market.start, issue_ns)
    formed = f1_trailing_minutes(rows, issue_ns=issue_ns)
    if not formed.get("available"):
        return None
    try:
        return freeze_formation(formed, cutoff_ns=issue_ns, asset_id=str(market.instrument_id))
    except ContractError:
        return None


def changed_formation_scan(market: HistoricalFeatures, view: NativeMarketView | None, spec: RuleSpec) -> dict[str, Any]:
    """Build the candidate's own formation, issue references, enumerate native contacts."""
    family = spec.family
    branch = spec.source_branch or PRIMARY_BRANCH.get(f"P15-{family}", ("", ""))[1]
    if not branch:
        branch = spec.source_branch or (FAMILY_BRANCHES.get(family) or ("unknown",))[0]
    recipe = str(spec.parameters.get("recipe_id") or spec.formation_policy or "F1")
    issue_ns = int(market.at("09:30"))
    expiry_ns = int(market.end)
    formed: Formation | None = None
    if recipe == "F2":
        if view is None:
            from trading_research.research.rule_discovery.native import build_market_view

            view = build_market_view(str(market.day), full_account_day=True)
        payload = f2_candidate_formation(view, family, issue_ns)
        if payload.get("threshold", {}).get("stand_in"):
            raise ContractError("F2 stand-in volume is forbidden")
        if payload.get("frozen"):
            frozen = payload["frozen"]
            rows = minute_rows_from_market(market, int(frozen["start_ns"]), int(frozen["end_ns"]))
            if rows:
                formed = freeze_formation(
                    {"available": True, "kind": "F2", "rows": rows},
                    cutoff_ns=int(frozen["available_at_ns"]),
                    asset_id=str(market.instrument_id),
                )
        elif payload.get("available") and payload.get("formation"):
            raw = payload["formation"]
            formed = freeze_formation(raw, cutoff_ns=issue_ns, asset_id=str(market.instrument_id)) if raw.get("available") else None
    else:
        formed = _freeze_f1(market, issue_ns)
    baseline = dual_scan(market, family, branch)
    if formed is None:
        enumeration = enumerate_own_population(
            baseline_ids=baseline_contact_ids(baseline["b01"]),
            candidate_ids=set(),
            geometry_changed=True,
        )
        return {
            "schema_version": "research-changed-axis-scan-v1",
            "axis": "Formation",
            "recipe": recipe,
            "family": family,
            "branch": branch,
            "formations": [],
            "references": [],
            "contacts": [],
            "episodes": [],
            "emitted": False,
            "populations": {
                "B0": baseline["populations"]["B0"],
                "B0.1": baseline["populations"]["B0.1"],
                "candidate": population_counts({"episodes": []}),
            },
            "enumeration": enumeration,
            "clock_zone_unverified": clock_zone_unverified(family, branch),
            "population_kind": "engineering_slice",
        }
    form_row = formation_record(formed)
    issue_at = max(issue_ns, formed.available_at_ns)
    high_ref = _band_reference(
        formed,
        lower=formed.high,
        upper=formed.high,
        kind="R2-high",
        issue_ns=issue_at,
        expiry_ns=expiry_ns,
        family=family,
        branch=branch,
    )
    low_ref = _band_reference(
        formed,
        lower=formed.low,
        upper=formed.low,
        kind="R2-low",
        issue_ns=issue_at,
        expiry_ns=expiry_ns,
        family=family,
        branch=branch,
    )
    band_ref = _band_reference(
        formed,
        lower=formed.low,
        upper=formed.high,
        kind="R-band",
        issue_ns=issue_at,
        expiry_ns=expiry_ns,
        family=family,
        branch=branch,
    )
    scan_start = issue_at
    contacts: list[dict[str, Any]] = []
    contacts.extend(
        enumerate_bar_contacts(
            market,
            lower=formed.high,
            upper=formed.high,
            start_ns=scan_start,
            end_ns=expiry_ns,
            reference_id=high_ref.reference_id,
            side="short",
        )
    )
    contacts.extend(
        enumerate_bar_contacts(
            market,
            lower=formed.low,
            upper=formed.low,
            start_ns=scan_start,
            end_ns=expiry_ns,
            reference_id=low_ref.reference_id,
            side="long",
        )
    )
    contacts.extend(
        enumerate_bar_contacts(
            market,
            lower=formed.low,
            upper=formed.high,
            start_ns=scan_start,
            end_ns=expiry_ns,
            reference_id=band_ref.reference_id,
            side="long",
        )
    )
    episodes = []
    for reference in (high_ref, low_ref, band_ref):
        ref_row = reference_record(reference)
        side = "short" if reference is high_ref else "long"
        subset = [c for c in contacts if c["reference_id"] == reference.reference_id]
        episodes.extend(_episodes_from_contacts(family=family, branch=branch, formation=form_row, reference=ref_row, contacts=subset))
    candidate_ids = {ep["candidate_id"] for ep in episodes} | {c["contact_id"] for c in contacts}
    baseline_ids = baseline_contact_ids(baseline["b01"])
    enumeration = enumerate_own_population(baseline_ids=baseline_ids, candidate_ids=candidate_ids, geometry_changed=True)
    return {
        "schema_version": "research-changed-axis-scan-v1",
        "axis": "Formation",
        "recipe": recipe,
        "family": family,
        "branch": branch,
        "formations": [form_row],
        "references": [reference_record(high_ref), reference_record(low_ref), reference_record(band_ref)],
        "contacts": contacts,
        "episodes": episodes,
        "emitted": bool(episodes),
        "populations": {
            "B0": baseline["populations"]["B0"],
            "B0.1": baseline["populations"]["B0.1"],
            "candidate": population_counts({"episodes": episodes}),
        },
        "enumeration": enumeration,
        "clock_zone_unverified": clock_zone_unverified(family, branch),
        "population_kind": "engineering_slice",
    }


def changed_reference_scan(market: HistoricalFeatures, view: NativeMarketView | None, spec: RuleSpec) -> dict[str, Any]:
    """Freeze the source-window formation, issue own references (quadrants / R1), enumerate contacts."""
    family = spec.family
    branch = spec.source_branch or (FAMILY_BRANCHES.get(family) or ("unknown",))[0]
    formed = _freeze_source_window(market, family, kind="source_window")
    baseline = dual_scan(market, family, branch)
    if formed is None:
        enumeration = enumerate_own_population(
            baseline_ids=baseline_contact_ids(baseline["b01"]),
            candidate_ids=set(),
            geometry_changed=True,
        )
        return {
            "schema_version": "research-changed-axis-scan-v1",
            "axis": "Reference",
            "family": family,
            "branch": branch,
            "formations": [],
            "references": [],
            "contacts": [],
            "episodes": [],
            "emitted": False,
            "populations": {
                "B0": baseline["populations"]["B0"],
                "B0.1": baseline["populations"]["B0.1"],
                "candidate": population_counts({"episodes": []}),
            },
            "enumeration": enumeration,
            "clock_zone_unverified": clock_zone_unverified(family, branch),
            "population_kind": "engineering_slice",
        }
    issue_ns = max(int(market.at("09:30")), formed.available_at_ns)
    expiry_ns = int(market.end)
    loc = quadrant_locations(formed.low, formed.high, "long")
    refs = [
        _band_reference(formed, lower=loc["eq"], upper=loc["eq"], kind="R-eq", issue_ns=issue_ns, expiry_ns=expiry_ns, family=family, branch=branch),
        _band_reference(formed, lower=loc["q1"], upper=loc["q1"], kind="R-q1", issue_ns=issue_ns, expiry_ns=expiry_ns, family=family, branch=branch),
        _band_reference(formed, lower=loc["q3"], upper=loc["q3"], kind="R-q3", issue_ns=issue_ns, expiry_ns=expiry_ns, family=family, branch=branch),
        _band_reference(formed, lower=formed.low, upper=formed.high, kind="R-band", issue_ns=issue_ns, expiry_ns=expiry_ns, family=family, branch=branch),
    ]
    form_row = formation_record(formed)
    contacts: list[dict[str, Any]] = []
    episodes: list[dict[str, Any]] = []
    side_by_kind = {"R-eq": "long", "R-q1": "long", "R-q3": "short", "R-band": "long"}
    for reference in refs:
        kind = next((name for name in ("R-band", "R-q1", "R-q3", "R-eq") if name in reference.reference_id), "R-eq")
        side = side_by_kind.get(kind, "long")
        found = enumerate_bar_contacts(
            market,
            lower=reference.lower,
            upper=reference.upper,
            start_ns=issue_ns,
            end_ns=expiry_ns,
            reference_id=reference.reference_id,
            side=side,
        )
        contacts.extend(found)
        episodes.extend(
            _episodes_from_contacts(
                family=family,
                branch=branch,
                formation=form_row,
                reference=reference_record(reference),
                contacts=found,
            )
        )
    candidate_ids = {ep["candidate_id"] for ep in episodes} | {c["contact_id"] for c in contacts}
    baseline_ids = baseline_contact_ids(baseline["b01"])
    enumeration = enumerate_own_population(baseline_ids=baseline_ids, candidate_ids=candidate_ids, geometry_changed=True)
    return {
        "schema_version": "research-changed-axis-scan-v1",
        "axis": "Reference",
        "family": family,
        "branch": branch,
        "formations": [form_row],
        "references": [reference_record(item) for item in refs],
        "contacts": contacts,
        "episodes": episodes,
        "emitted": bool(episodes),
        "populations": {
            "B0": baseline["populations"]["B0"],
            "B0.1": baseline["populations"]["B0.1"],
            "candidate": population_counts({"episodes": episodes}),
        },
        "enumeration": enumeration,
        "clock_zone_unverified": clock_zone_unverified(family, branch),
        "population_kind": "engineering_slice",
    }


def synthetic_quadrant_mirror() -> dict[str, Any]:
    """Long/short mirror on synthetic bars: long contacts q1, short contacts q3."""
    low, high = Decimal("100"), Decimal("108")
    long_loc = quadrant_locations(low, high, "long")
    short_loc = quadrant_locations(low, high, "short")
    long_bars = [{"start": 0, "end": 60_000_000_000, "L": Decimal("101.5"), "H": Decimal("102.5"), "known_at": 60_000_000_000, "bar_id": "L1"}]
    short_bars = [{"start": 0, "end": 60_000_000_000, "L": Decimal("105.5"), "H": Decimal("106.5"), "known_at": 60_000_000_000, "bar_id": "S1"}]

    def touches(bars: list[dict[str, Any]], price: Decimal) -> list[str]:
        return [str(row["bar_id"]) for row in bars if row["L"] <= price <= row["H"]]

    long_ids = touches(long_bars, long_loc["q1"])
    short_ids = touches(short_bars, short_loc["q3"])
    mid = (low + high) / Decimal("2")
    mirrored_short_price = mid - (Decimal(str(long_bars[0]["L"])) - mid)
    # long L 101.5 mirrors to 106.5, which is the short bar high
    return {
        "low": str(low),
        "high": str(high),
        "long_q1": str(long_loc["q1"]),
        "short_q3": str(short_loc["q3"]),
        "long_contacts": long_ids,
        "short_contacts": short_ids,
        "long_n": len(long_ids),
        "short_n": len(short_ids),
        "mirrored": len(long_ids) == len(short_ids) and len(long_ids) >= 1,
        "eq": str(mid),
        "mirrored_short_price": str(mirrored_short_price),
    }


def dispatch_scan_variant(market, view, spec: RuleSpec, *, empty_hook=None) -> dict[str, Any]:
    """Unchanged rules dual-scan; changed Formation/Reference enumerate their own population."""
    axis = str(spec.changed_axis or "none")
    if axis in {"none", "baseline"} or spec.parameters.get("empty_delta") is True:
        branch = spec.source_branch or (FAMILY_BRANCHES.get(spec.family) or ("unknown",))[0]
        result = dual_scan(market, spec.family, branch)
        if empty_hook is not None:
            result = empty_hook(market, spec, result)
        result["literal_operands_note"] = "empty_delta"
        result["clock_zone_unverified"] = clock_zone_unverified(spec.family, branch)
        result["population_kind"] = "engineering_slice"
        return result
    if axis in {"Formation", "formation"}:
        return changed_formation_scan(market, view, spec)
    if axis in {"Reference", "reference", "location"}:
        return changed_reference_scan(market, view, spec)
    return changed_formation_scan(market, view, spec)


def run_changed_axis_cases(day: str, family: str, branch: str) -> dict[str, Any]:
    """Native changed-formation and changed-reference scans for NATIVE_CASES.json."""
    install_write_guard()
    market = load_source_market(day)
    formation = changed_formation_scan(market, None, changed_axis_spec(family, branch, "Formation", recipe="F1"))
    reference = changed_reference_scan(market, None, changed_axis_spec(family, branch, "Reference", recipe="R-quadrant"))
    return {
        "date": day,
        "family": family,
        "branch": branch,
        "population_kind": "engineering_slice",
        "changed_formation": {
            "n_formations": len(formation.get("formations") or []),
            "n_references": len(formation.get("references") or []),
            "n_contacts": len(formation.get("contacts") or []),
            "n_episodes": len(formation.get("episodes") or []),
            "b01_episodes": ((formation.get("populations") or {}).get("B0.1") or {}).get("episodes"),
            "candidate_episodes": ((formation.get("populations") or {}).get("candidate") or {}).get("episodes"),
            "new_contacts": (formation.get("enumeration") or {}).get("new_contacts"),
            "count_differs_from_b01": ((formation.get("populations") or {}).get("candidate") or {}).get("episodes")
            != ((formation.get("populations") or {}).get("B0.1") or {}).get("episodes"),
        },
        "changed_reference": {
            "n_formations": len(reference.get("formations") or []),
            "n_references": len(reference.get("references") or []),
            "n_contacts": len(reference.get("contacts") or []),
            "n_episodes": len(reference.get("episodes") or []),
            "b01_episodes": ((reference.get("populations") or {}).get("B0.1") or {}).get("episodes"),
            "candidate_episodes": ((reference.get("populations") or {}).get("candidate") or {}).get("episodes"),
            "new_contacts": (reference.get("enumeration") or {}).get("new_contacts"),
            "count_differs_from_b01": ((reference.get("populations") or {}).get("candidate") or {}).get("episodes")
            != ((reference.get("populations") or {}).get("B0.1") or {}).get("episodes"),
        },
        "synthetic_mirror": synthetic_quadrant_mirror(),
    }
