"""REFILL-STUDY B0.2 scan. Does not change JETBUNDLE or STOIC."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import inspect

import numpy as np

from trading_research.errors import ContractError
from trading_research.research.rule_discovery.native import NS, NativeMarketView, build_market_view

FAMILY_REFILL = "REFILL-STUDY"
PRINT_THRESHOLD = 40
CLUSTER_SECONDS = 5
CLUSTER_MIN_SIZE = 80
DEPARTURE_TICKS = 4
PRINTED_TOUCHES_PER_SESSION = 175

B02_VERSION = "B0.2-2026-09-15"
LITERAL_CLUSTER_SIZES = (60, 80, 100)
HOLD_BOUNDARY_TICKS = 8
HOLD_WINDOW_NS = 30 * 60 * NS
BRACKET_INSIDE_TICKS = 12
BRACKET_STOP_TICKS = 32
BRACKET_TARGET_TICKS = 96
BRACKET_CANCEL_NS = 30 * 60 * NS
BRACKET_COST_TICKS = 1
BRACKET_SLIPPAGE_TICKS = 1


def cluster_size_family() -> tuple[int, ...]:
    """REF pp.5-7: sixty, eighty, a hundred contracts in seconds."""
    return LITERAL_CLUSTER_SIZES


def _file_line(fn) -> str:
    try:
        _lines, start = inspect.getsourcelines(fn)
        path = inspect.getsourcefile(fn) or ""
        return f"{Path(path).name}:{start}"
    except (OSError, TypeError):
        return ""


def actual_departure_ns(arrays, zone: Mapping[str, Any], cutoff: int) -> int | None:
    lo, hi = int(zone["low_ticks"]), int(zone["high_ticks"])
    formed = int(zone["formed_at_ns"])
    trade = arrays.is_trade & (arrays.t_ns > formed) & (arrays.known_at_ns <= cutoff)
    idx = np.flatnonzero(trade)
    for j in idx:
        px = int(arrays.price_ticks[j])
        ts = int(arrays.t_ns[j])
        if zone["side"] == "long" and px >= hi + DEPARTURE_TICKS:
            return ts
        if zone["side"] == "short" and px <= lo - DEPARTURE_TICKS:
            return ts
    return None


def touches_after_departure(arrays, zone: Mapping[str, Any], departure_at: int, cutoff: int) -> list[dict[str, Any]]:
    lo, hi = int(zone["low_ticks"]), int(zone["high_ticks"])
    out: list[dict[str, Any]] = []
    armed = True
    trade = arrays.is_trade
    for i in range(arrays.t_ns.size):
        if not bool(trade[i]):
            continue
        ts = int(arrays.t_ns[i])
        kn = int(arrays.known_at_ns[i])
        if ts <= departure_at:
            continue
        if kn > cutoff:
            continue
        px = int(arrays.price_ticks[i])
        outside = px >= hi + DEPARTURE_TICKS if zone["side"] == "long" else px <= lo - DEPARTURE_TICKS
        inside = lo <= px <= hi
        if not armed:
            if outside:
                armed = True
            continue
        if inside:
            out.append({"touch_at_ns": ts, "known_at_ns": kn, "price_ticks": px})
            armed = False
    return out


def hold_label(arrays, zone: Mapping[str, Any], touch_at: int, cutoff: int) -> bool | None:
    lo, hi = int(zone["low_ticks"]), int(zone["high_ticks"])
    end = min(int(touch_at) + HOLD_WINDOW_NS, int(cutoff))
    trade = arrays.is_trade & (arrays.t_ns > touch_at) & (arrays.t_ns <= end) & (arrays.known_at_ns <= cutoff)
    if not np.any(trade) and end < int(touch_at) + HOLD_WINDOW_NS:
        return None
    px = arrays.price_ticks[trade]
    if zone["side"] == "long":
        through = np.any(px <= lo - HOLD_BOUNDARY_TICKS)
    else:
        through = np.any(px >= hi + HOLD_BOUNDARY_TICKS)
    return not bool(through)


def adverse_dip_ticks(arrays, zone: Mapping[str, Any], touch_at: int, entry_ticks: int, cutoff: int) -> int:
    lo, hi = int(zone["low_ticks"]), int(zone["high_ticks"])
    end = min(int(touch_at) + HOLD_WINDOW_NS, int(cutoff))
    trade = arrays.is_trade & (arrays.t_ns >= touch_at) & (arrays.t_ns <= end) & (arrays.known_at_ns <= cutoff)
    if not np.any(trade):
        return 0
    px = arrays.price_ticks[trade].astype(np.int64)
    if zone["side"] == "long":
        return max(0, int(entry_ticks - int(px.min())))
    return max(0, int(int(px.max()) - entry_ticks))


def bracket_for(zone: Mapping[str, Any]) -> dict[str, int]:
    lo, hi = int(zone["low_ticks"]), int(zone["high_ticks"])
    if zone["side"] == "long":
        entry = hi - BRACKET_INSIDE_TICKS
        stop = entry - BRACKET_STOP_TICKS
        target = entry + BRACKET_TARGET_TICKS
    else:
        entry = lo + BRACKET_INSIDE_TICKS
        stop = entry + BRACKET_STOP_TICKS
        target = entry - BRACKET_TARGET_TICKS
    return {
        "entry_ticks": entry,
        "stop_ticks": stop,
        "target_ticks": target,
        "inside_ticks": BRACKET_INSIDE_TICKS,
        "stop_distance_ticks": BRACKET_STOP_TICKS,
        "target_distance_ticks": BRACKET_TARGET_TICKS,
        "cancel_ns": BRACKET_CANCEL_NS,
        "cost_ticks": BRACKET_COST_TICKS,
        "slippage_ticks": BRACKET_SLIPPAGE_TICKS,
    }


def zone_construction_ok(zone: Mapping[str, Any]) -> str:
    if zone.get("low_ticks") is None or zone.get("high_ticks") is None:
        return "unknown"
    if zone.get("print_count") is None and zone.get("size") is None:
        return "unknown"
    return "pass"


def zone_known_ok(zone_known_at: int | None) -> str:
    return "pass" if zone_known_at is not None else "unknown"


def departure_ok(departure_at: int | None) -> str:
    return "pass" if departure_at is not None else "unknown"


def touch_inside_ok(zone: Mapping[str, Any], price_ticks: int | None) -> str:
    if price_ticks is None or zone.get("low_ticks") is None or zone.get("high_ticks") is None:
        return "unknown"
    return "pass" if int(zone["low_ticks"]) <= int(price_ticks) <= int(zone["high_ticks"]) else "fail"


def bracket_fillable(arrays, zone: Mapping[str, Any], touch_at: int, cutoff: int) -> str:
    """REF p.12: 12-tick inside limit fillable inside the 30-minute cancel."""
    br = bracket_for(zone)
    entry = br["entry_ticks"]
    window_end = int(touch_at) + BRACKET_CANCEL_NS
    observed_end = min(window_end, int(cutoff))
    trade = arrays.is_trade & (arrays.t_ns > touch_at) & (arrays.t_ns <= observed_end) & (arrays.known_at_ns <= cutoff)
    if not np.any(trade):
        if observed_end < window_end:
            return "unknown"
        return "fail"
    px = arrays.price_ticks[trade].astype(np.int64)
    filled = bool(np.any(px == int(entry)))
    if filled:
        return "pass"
    if observed_end < window_end:
        return "unknown"
    return "fail"


def cascade_stages(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(row)
        if row.get("verdict") != "pass":
            break
    return out


def _combine(stage_rows: list[dict[str, Any]]) -> tuple[str, list[str], list[str]]:
    failed: list[str] = []
    unknown: list[str] = []
    for row in stage_rows:
        if row["verdict"] == "fail":
            failed.append(row["stage"])
        elif row["verdict"] == "unknown":
            unknown.append(row["stage"])
    if failed:
        return "fail", failed, unknown
    if unknown:
        return "unknown", failed, unknown
    return "pass", failed, unknown


def simulate_fade_r(arrays, zone: Mapping[str, Any], touch_at: int, cutoff: int) -> float | None:
    br = bracket_for(zone)
    entry, stop, target = br["entry_ticks"], br["stop_ticks"], br["target_ticks"]
    end = min(int(touch_at) + BRACKET_CANCEL_NS, int(cutoff))
    trade = arrays.is_trade & (arrays.t_ns > touch_at) & (arrays.t_ns <= end) & (arrays.known_at_ns <= cutoff)
    if not np.any(trade):
        return 0.0
    px = arrays.price_ticks[trade].astype(np.int64)
    t = arrays.t_ns[trade]
    side = 1 if zone["side"] == "long" else -1
    for i in range(px.size):
        p = int(px[i])
        hit_stop = p <= stop if side > 0 else p >= stop
        hit_target = p >= target if side > 0 else p <= target
        if hit_stop and hit_target:
            return None
        if hit_stop:
            pnl = -BRACKET_STOP_TICKS - BRACKET_COST_TICKS - BRACKET_SLIPPAGE_TICKS
            return pnl / BRACKET_STOP_TICKS
        if hit_target:
            pnl = BRACKET_TARGET_TICKS - BRACKET_COST_TICKS
            return pnl / BRACKET_STOP_TICKS
    last = int(px[-1])
    pnl = side * (last - entry) - BRACKET_COST_TICKS
    return pnl / BRACKET_STOP_TICKS


RULES: dict[str, dict[str, Any]] = {
    "F10_zone_from_aggressive_clusters": {
        "kind": "OD",
        "source": "OD:PRINT_THRESHOLD=40,CLUSTER_SECONDS=5,CLUSTER_MIN_SIZE=80",
        "finding": "F10",
        "fn": zone_construction_ok,
        "parameters": {
            "print_threshold": PRINT_THRESHOLD,
            "cluster_seconds": CLUSTER_SECONDS,
            "cluster_min_size": CLUSTER_MIN_SIZE,
        },
    },
    "F10_literal_cluster_size_family": {
        "kind": "literal",
        "source": "REF pp.5-7",
        "finding": "F10",
        "parameters": {"sizes": list(LITERAL_CLUSTER_SIZES)},
        "fn": cluster_size_family,
    },
    "F10_actual_departure": {
        "kind": "literal",
        "source": "REF pp.5-7",
        "finding": "F10",
        "fn": actual_departure_ns,
    },
    "F10_distinct_later_touches": {
        "kind": "literal",
        "source": "REF pp.5-7",
        "finding": "F10",
        "fn": touches_after_departure,
    },
    "F20_printed_bracket": {
        "kind": "literal",
        "source": "REF p.12",
        "finding": "F20",
        "fn": bracket_for,
        "parameters": {
            "inside_ticks": BRACKET_INSIDE_TICKS,
            "stop_ticks": BRACKET_STOP_TICKS,
            "target_ticks": BRACKET_TARGET_TICKS,
            "cancel_ns": BRACKET_CANCEL_NS,
            "one_position": True,
            "cost_ticks": BRACKET_COST_TICKS,
            "slippage_ticks": BRACKET_SLIPPAGE_TICKS,
        },
    },
    "RR21_hold_label_boundary": {
        "kind": "OD",
        "source": "OD:HOLD_BOUNDARY_TICKS=8,HOLD_WINDOW_NS=30m",
        "finding": "RR-21",
        "fn": hold_label,
        "parameters": {"ticks": HOLD_BOUNDARY_TICKS, "window_ns": HOLD_WINDOW_NS},
    },
    "RR21_population_175": {
        "kind": "literal",
        "source": "REF p.8",
        "finding": "RR-21",
        "parameters": {"printed_touches_per_session": PRINTED_TOUCHES_PER_SESSION, "printed_sessions": 235, "printed_touches": 41152},
    },
}


def rules_payload() -> list[dict[str, Any]]:
    rows = []
    for rule_id, spec in RULES.items():
        fn = spec.get("fn")
        source = spec["source"]
        rows.append(
            {
                "rule_id": rule_id,
                "kind": spec["kind"],
                "source": source,
                "file_line": _file_line(fn) if fn is not None else f"refill_b02.py:RULES[{rule_id}]",
            }
        )
    return rows


def _as_view(market) -> NativeMarketView | None:
    if market is None:
        return None
    if isinstance(market, NativeMarketView) or hasattr(market, "arrays"):
        return market
    day = getattr(market, "day", None)
    if day is None:
        return None
    return build_market_view(str(day), full_account_day=True)


def scan_b02(market, rec) -> dict[str, Any]:
    rec = dict(rec or {})
    family = rec.get("method_id") or rec.get("family") or FAMILY_REFILL
    if family != FAMILY_REFILL:
        raise ContractError(f"B0.2 scan does not own {family}; JETBUNDLE and STOIC are unchanged")
    branch = rec.get("branch") or "touch_record"
    view = _as_view(market)
    payload = {
        "schema_version": "research-family-b02-scan-v1",
        "baseline_version": B02_VERSION,
        "family": family,
        "branch": branch,
        "coverage_id": rec.get("coverage_id") or f"{family}:branch:{branch}",
        "episodes": [],
        "omissions": [],
        "rules": rules_payload(),
        "od_parameters": {
            "print_threshold": PRINT_THRESHOLD,
            "cluster_seconds": CLUSTER_SECONDS,
            "cluster_min_size": CLUSTER_MIN_SIZE,
        },
        "literal_cluster_sizes": list(LITERAL_CLUSTER_SIZES),
        "hold_boundary_ticks": HOLD_BOUNDARY_TICKS,
    }
    if view is None or view.arrays.t_ns.size == 0:
        payload["omissions"].append({"reason": "operands_unavailable", "operand": "native_executions"})
        return payload
    arrays = view.arrays
    cutoff = rec.get("b02_now_ns")
    if cutoff is None:
        cutoff = int(arrays.known_at_ns.max()) if arrays.known_at_ns.size else 0
    cutoff = int(cutoff)
    from trading_research.research.rule_discovery.source_adapters.processes import form_refill_zones

    formed = form_refill_zones(view)
    episodes = []
    for zone in formed.get("zones") or []:
        zone_known = int(zone.get("known_at_ns") or zone["formed_at_ns"])
        if zone_known > cutoff:
            continue
        dep = actual_departure_ns(arrays, zone, cutoff)
        if dep is None:
            continue
        for touch in touches_after_departure(arrays, zone, dep, cutoff):
            touch_at = int(touch["touch_at_ns"])
            if touch_at > cutoff:
                continue
            feature_max = max(zone_known, int(dep))
            if feature_max > touch_at:
                continue
            br = bracket_for(zone)
            hold = hold_label(arrays, zone, touch_at, cutoff)
            dip = adverse_dip_ticks(arrays, zone, touch_at, br["entry_ticks"], cutoff)
            fade_r = simulate_fade_r(arrays, zone, touch_at, cutoff)
            values = {
                "branch": branch,
                "side": zone["side"],
                "zone_known_at": zone_known,
                "departure_at": int(dep),
                "touch_at": touch_at,
                "feature_max_known_at": feature_max,
                "hold_label": hold,
                "hold_boundary_ticks": HOLD_BOUNDARY_TICKS,
                "dip_ticks": dip,
                "fade_R": fade_r,
                "print_threshold": PRINT_THRESHOLD,
                "cluster_seconds": CLUSTER_SECONDS,
                "cluster_min_size": CLUSTER_MIN_SIZE,
                "literal_cluster_sizes": list(LITERAL_CLUSTER_SIZES),
            }
            ref_v = zone_construction_ok(zone)
            loc_v = zone_known_ok(zone_known)
            trig_v = departure_ok(dep)
            conf_v = touch_inside_ok(zone, touch.get("price_ticks"))
            risk_v = "pass" if br.get("stop_ticks") is not None else "unknown"
            obj_v = bracket_fillable(arrays, zone, touch_at, cutoff)
            stages = cascade_stages(
                [
                    {"stage": "reference", "verdict": ref_v, "at_ns": zone_known, "operands": {"zone_low": zone.get("low_ticks"), "zone_high": zone.get("high_ticks"), "print_count": zone.get("print_count"), "size": zone.get("size")}},
                    {"stage": "location", "verdict": loc_v, "at_ns": zone_known, "operands": {"zone_known_at": zone_known}},
                    {"stage": "trigger", "verdict": trig_v, "at_ns": None if dep is None else int(dep), "operands": {"departure_at": dep}},
                    {"stage": "confirmation", "verdict": conf_v, "at_ns": touch_at, "operands": {"touch_at": touch_at, "touch_ticks": touch.get("price_ticks"), "feature_max_known_at": feature_max}},
                    {"stage": "risk", "verdict": risk_v, "at_ns": touch_at, "operands": {"stop_ticks": br.get("stop_ticks"), "entry_ticks": br.get("entry_ticks")}},
                    {"stage": "objective", "verdict": obj_v, "at_ns": touch_at, "operands": {"target_ticks": br.get("target_ticks"), "target": br.get("target_ticks"), "cancel_ns": BRACKET_CANCEL_NS, "fillable": obj_v == "pass"}},
                ]
            )
            verdict, failed, unknown = _combine(stages)
            episodes.append(
                {
                    "candidate_id": f"b02:{family}:{branch}:{touch_at}:{zone['low_ticks']}",
                    "method": family,
                    "branch": branch,
                    "side": zone["side"],
                    "research_verdict": verdict,
                    "status": {"pass": "condition_present", "fail": "condition_absent", "unknown": "data_unavailable"}[verdict],
                    "failed": failed,
                    "unknown": unknown,
                    "values": values,
                    "decision_at": touch_at,
                    "geometry": br,
                    "reference": {"low_ticks": zone["low_ticks"], "high_ticks": zone["high_ticks"], "side": zone["side"]},
                    "trigger": {"at_ns": touch_at, "ticks": touch["price_ticks"]},
                    "stages": stages,
                    "rules": rules_payload(),
                    "baseline_version": B02_VERSION,
                }
            )
    payload["episodes"] = episodes
    payload["n_zones"] = len(formed.get("zones") or [])
    payload["n_touches"] = len(episodes)
    return payload


def replay_example(market, example) -> dict[str, Any]:
    return {
        "detected": None,
        "branch": "touch_record",
        "our_side": None,
        "our_level": None,
        "our_entry_ns": None,
        "author_level": None,
        "author_side": None,
        "divergence": "no_refill_author_example",
    }
