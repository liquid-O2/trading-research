"""SIRES B0.2 scan. Independent of frozen B0 / B0.1 scanners."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Mapping
import inspect
import re

import numpy as np

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.rule_discovery.native import NS, NativeMarketView, build_market_view

B02_VERSION = "B0.2-2026-09-15"
STAGE_ORDER = ("context", "reference", "location", "trigger", "confirmation", "risk", "objective", "management")
ELIGIBLE_LOCATION_KINDS = frozenset({"shelf", "ledge", "lvn", "minor_volume_node", "real_extreme"})
FORBIDDEN_LOCATION_KINDS = frozenset({"poc", "inside_balance", "current_day_vah", "current_day_val"})
THESIS_KILLERS = ("structure_break", "value_shift", "new_information")
LEVEL_TOLERANCE_TICKS = 8
REWARD_WINDOW_NS = 30 * NS
FAST_RELEASE_TICKS = 8
FAST_RELEASE_NS = 5 * NS
PULLBACK_TICKS = 4
AGGRESSION_MIN = 30
AGGRESSION_MAX = 60
IMBALANCE_PCT = 3.5
FOOTPRINT_FLAG_MIN = 3.0
FOOTPRINT_FLAG_MAX = 4.0
VWAP_BANDS = (1.0, 2.0, 2.5)
OFM_TARGET_TICKS = 40
OFM_STOP_TICKS_MIN = 7
OFM_STOP_TICKS_MAX = 27
DAILY_STOP_R = -4
REPLENISHMENT_MIN_TICKS = 3
REWARD_MIN_TICKS = 3
ENTRY_NEAR_TICKS = 2
REPLENISHMENT_BAND_TICKS = 2
TICK_POINTS = 0.25
STOP_ENTRY_BRANCHES = frozenset({"stop_four_stage", "absorption_reward_retest"})
FADE_UNPAID = "unpaid"
FADE_OWN_AGGRESSION = "own_aggression"

_IMPL: dict[str, Any] = {}


def _file_line(fn) -> str:
    try:
        _lines, start = inspect.getsourcelines(fn)
        path = inspect.getsourcefile(fn) or ""
        return f"{Path(path).name}:{start}"
    except (OSError, TypeError):
        return ""


def _register(rule_id: str):
    def wrap(fn):
        _IMPL[rule_id] = fn
        return fn

    return wrap


@_register("F02_clean_squeeze_no_retest")
def classify_clean_squeeze(features: Mapping[str, Any]) -> str:
    """CONT p.11: fast aggression, no retest, no false start."""
    if features.get("release") is not True:
        return "fail"
    if features.get("failure") is True:
        return "fail"
    if features.get("pullback") is True:
        return "fail"
    if features.get("opposite_absorbed") is not True:
        return "fail"
    return "pass"


@_register("F03_replenishment_ticks")
def replenishment_ok(count: int | None) -> str:
    """STOP pp.10, 14: at least three refreshes at the defended price."""
    if count is None:
        return "unknown"
    return "pass" if int(count) >= REPLENISHMENT_MIN_TICKS else "fail"


@_register("F03_reward_ticks")
def reward_ok(ticks: int | None) -> str:
    """ABS p.6: price moves at least three ticks from the absorption print."""
    if ticks is None:
        return "unknown"
    return "pass" if int(ticks) >= REWARD_MIN_TICKS else "fail"


@_register("F09_location_eligibility")
def location_ok(kind: str | None) -> str:
    """ABS pp.6-7; VP2 p.7; BIG p.10. Never POC or inside balance."""
    if kind is None or kind == "":
        return "unknown"
    if kind in FORBIDDEN_LOCATION_KINDS:
        return "fail"
    if kind in ELIGIBLE_LOCATION_KINDS:
        return "pass"
    return "fail"


@_register("F09_thesis_killers")
def thesis_dead(killer: str | None) -> bool:
    """C1 p.4: structure break, value shift, new information."""
    return killer in THESIS_KILLERS


@_register("RR20_aggression_band")
def aggression_in_band(size: int | None) -> str:
    """OFM p.4; BIG p.3: 30-60 contracts NY AM NQ."""
    if size is None:
        return "unknown"
    return "pass" if AGGRESSION_MIN <= int(size) <= AGGRESSION_MAX else "fail"


@_register("RR20_imbalance_350")
def imbalance_ok(ratio: float | None) -> str:
    """BIG p.5: 350 percent same-price imbalance."""
    if ratio is None:
        return "unknown"
    return "pass" if float(ratio) >= IMBALANCE_PCT else "fail"


@_register("F09_gamma_permission")
def gamma_ok(needed: str | None, actual: str | None) -> str:
    """BIG p.14. Missing Phase 2 options record is unknown, not pass."""
    if needed is None:
        return "pass"
    if actual is None or actual == "":
        return "unknown"
    return "pass" if actual == needed else "fail"


@_register("RR18_resting_stop_entry")
def resting_stop_fill(wick_ticks: int | None, fill_ticks: int | None, side: str) -> str:
    """K2345 p.9; OFM pp.11-14: stop-limit resting beyond the failed-squeeze wick."""
    if wick_ticks is None or fill_ticks is None:
        return "unknown"
    if side == "short":
        return "pass" if int(fill_ticks) <= int(wick_ticks) - 1 else "fail"
    return "pass" if int(fill_ticks) >= int(wick_ticks) + 1 else "fail"


@_register("RR19_daily_stop")
def daily_stop_ok(daily_r: float | None) -> str:
    """STOP p.15: no trade at or below -4R."""
    if daily_r is None:
        return "unknown"
    return "fail" if float(daily_r) <= DAILY_STOP_R else "pass"


@_register("RR20_footprint_flag")
def footprint_flag_ok(ratio: float | None) -> str:
    """FP8 p.5: generic footprint flag 3-4x."""
    if ratio is None:
        return "unknown"
    value = float(ratio)
    return "pass" if FOOTPRINT_FLAG_MIN <= value <= FOOTPRINT_FLAG_MAX else "fail"


@_register("RR20_vwap_bands")
def vwap_band_ok(beyond_1: bool | None, absorption: bool | None) -> str:
    """VWAP p.4: beyond the 1 band, ideally at 2, with absorption."""
    if beyond_1 is None:
        return "unknown"
    if beyond_1 is not True:
        return "fail"
    if absorption is None:
        return "unknown"
    return "pass" if absorption else "fail"


@_register("RR18_ofm_40_tick_target")
def ofm_40_tick_target(entry_ticks: int | None, side: str) -> int | None:
    """OFM pp.7-8: fixed 40-tick target price."""
    if entry_ticks is None:
        return None
    if side == "short":
        return int(entry_ticks) - OFM_TARGET_TICKS
    return int(entry_ticks) + OFM_TARGET_TICKS


@_register("RR18_control_zone_target")
def control_zone_target_ok(far_ticks: int | None) -> str:
    """BIG pp.10, 15-16: far side of the last control zone."""
    if far_ticks is None:
        return "unknown"
    return "pass"


@_register("RR19_partial_1to1_be")
def partial_1to1_ok(entry_ticks: int | None, stop_ticks: int | None) -> str:
    """C2 p.5: partial at 1:1, stop to breakeven. Requires a defined R."""
    if entry_ticks is None or stop_ticks is None:
        return "unknown"
    if int(entry_ticks) == int(stop_ticks):
        return "fail"
    return "pass"


@_register("RR19_trail_protected_swing")
def trail_protected_ok(closed_past: bool | None, aggression: bool | None, protected_ticks: int | None) -> str:
    """RD p.4; K18 pp.8-9: trail behind protected highs/lows after a close past the prior swing with aggression."""
    if protected_ticks is None or closed_past is None or aggression is None:
        return "unknown"
    return "pass" if closed_past and aggression else "fail"


@_register("OD_level_tolerance_ticks")
def level_tolerance_ticks() -> int:
    """OD replay band. Not the STOP 1-2 tick entry literal."""
    return LEVEL_TOLERANCE_TICKS


@_register("OD_fast_release")
def fast_release_ok(displacement_ticks: int | None, dt_ns: int | None) -> bool:
    """OD stand-in for CONT p.11 'fast'."""
    if displacement_ticks is None or dt_ns is None:
        return False
    return abs(int(displacement_ticks)) >= FAST_RELEASE_TICKS and int(dt_ns) <= FAST_RELEASE_NS


@_register("OD_reward_window")
def reward_window_ns() -> int:
    """OD window for the ABS p.6 three-tick reward."""
    return REWARD_WINDOW_NS


@_register("A3_entry_one_to_two_ticks")
def entry_near_ok(entry_ticks: int | None, level_ticks: int | None) -> str:
    """STOP pp.9-15: entry 1 or 2 ticks from the defended level. 0 and wider are OD variants."""
    if entry_ticks is None or level_ticks is None:
        return "unknown"
    dist = abs(int(entry_ticks) - int(level_ticks))
    return "pass" if 1 <= dist <= ENTRY_NEAR_TICKS else "fail"


@_register("F09_balance_fade_unpaid")
def balance_fade_unpaid(failure: bool | None, retest: bool | None) -> str:
    """BIG pp.14-15: fade on failure of aggression; own side need not be rewarded."""
    if failure is None or retest is None:
        return "unknown"
    return "pass" if failure and retest else "fail"


@_register("F09_balance_fade_own_aggression")
def balance_fade_own_aggression(failure: bool | None, retest: bool | None, own_aggression: bool | None) -> str:
    """GEX p.18: long-gamma fade confirmed with real own-side aggression."""
    unpaid = balance_fade_unpaid(failure, retest)
    if unpaid != "pass":
        return unpaid
    if own_aggression is None:
        return "unknown"
    return "pass" if own_aggression else "fail"


@_register("OD_replenishment_band")
def replenishment_band_ticks() -> int:
    """OD tick band around the defended level for executed passive refills."""
    return REPLENISHMENT_BAND_TICKS


RULES: dict[str, dict[str, Any]] = {
    "F02_clean_squeeze_no_retest": {
        "kind": "literal",
        "source": "CONT p.11",
        "finding": "F02",
        "fn": classify_clean_squeeze,
    },
    "F03_replenishment_ticks": {
        "kind": "literal",
        "source": "STOP pp.10, 14",
        "finding": "F03",
        "fn": replenishment_ok,
    },
    "F03_reward_ticks": {
        "kind": "literal",
        "source": "ABS p.6",
        "finding": "F03",
        "fn": reward_ok,
    },
    "RR21_es_ticks_not_nq": {
        "kind": "literal",
        "source": "STOP pp.11-13; FP9 pp.3-4",
        "finding": "RR-21",
        "fn": reward_ok,
    },
    "F09_location_eligibility": {
        "kind": "literal",
        "source": "ABS pp.6-7; VP2 p.7; BIG p.10",
        "finding": "F09",
        "fn": location_ok,
    },
    "F09_thesis_killers": {
        "kind": "literal",
        "source": "C1 p.4",
        "finding": "F09",
        "fn": thesis_dead,
    },
    "F09_gamma_permission": {
        "kind": "literal",
        "source": "BIG p.14",
        "finding": "F09",
        "fn": gamma_ok,
    },
    "RR20_aggression_band": {
        "kind": "literal",
        "source": "OFM p.4; BIG p.3",
        "finding": "RR-20",
        "fn": aggression_in_band,
    },
    "RR20_imbalance_350": {
        "kind": "literal",
        "source": "BIG p.5",
        "finding": "RR-20",
        "fn": imbalance_ok,
    },
    "RR20_footprint_flag": {
        "kind": "literal",
        "source": "FP8 p.5",
        "finding": "RR-20",
        "fn": footprint_flag_ok,
        "parameters": {"min": FOOTPRINT_FLAG_MIN, "max": FOOTPRINT_FLAG_MAX},
    },
    "RR20_vwap_bands": {
        "kind": "literal",
        "source": "VWAP p.4",
        "finding": "RR-20",
        "fn": vwap_band_ok,
        "parameters": {"bands": list(VWAP_BANDS)},
    },
    "RR18_resting_stop_entry": {
        "kind": "literal",
        "source": "K2345 p.9; OFM pp.11-14",
        "finding": "RR-18",
        "fn": resting_stop_fill,
    },
    "RR18_ofm_40_tick_target": {
        "kind": "literal",
        "source": "OFM pp.7-8",
        "finding": "RR-18",
        "fn": ofm_40_tick_target,
        "parameters": {"ticks": OFM_TARGET_TICKS},
    },
    "RR18_control_zone_target": {
        "kind": "literal",
        "source": "BIG pp.10, 15-16",
        "finding": "RR-18",
        "fn": control_zone_target_ok,
    },
    "RR19_partial_1to1_be": {
        "kind": "literal",
        "source": "C2 p.5",
        "finding": "RR-19",
        "fn": partial_1to1_ok,
    },
    "RR19_trail_protected_swing": {
        "kind": "literal",
        "source": "RD p.4; K18 pp.8-9",
        "finding": "RR-19",
        "fn": trail_protected_ok,
    },
    "RR19_daily_stop": {
        "kind": "literal",
        "source": "STOP p.15",
        "finding": "RR-19",
        "fn": daily_stop_ok,
    },
    "OD_level_tolerance_ticks": {
        "kind": "OD",
        "source": "OD:LEVEL_TOLERANCE_TICKS=8",
        "finding": "RR-17",
        "fn": level_tolerance_ticks,
        "parameters": {"ticks": LEVEL_TOLERANCE_TICKS},
    },
    "OD_fast_release": {
        "kind": "OD",
        "source": "OD:FAST_RELEASE_TICKS=8,FAST_RELEASE_NS=5s",
        "finding": "F02",
        "fn": fast_release_ok,
        "parameters": {"ticks": FAST_RELEASE_TICKS, "window_ns": FAST_RELEASE_NS},
    },
    "OD_reward_window": {
        "kind": "OD",
        "source": "OD:REWARD_WINDOW_NS=30s",
        "finding": "F03",
        "fn": reward_window_ns,
        "parameters": {"window_ns": REWARD_WINDOW_NS},
    },
    "A3_entry_one_to_two_ticks": {
        "kind": "literal",
        "source": "STOP pp.9-15",
        "finding": "F09",
        "fn": entry_near_ok,
        "parameters": {"ticks": ENTRY_NEAR_TICKS},
    },
    "F09_balance_fade_unpaid": {
        "kind": "literal",
        "source": "BIG pp.14-15",
        "finding": "F09",
        "fn": balance_fade_unpaid,
    },
    "F09_balance_fade_own_aggression": {
        "kind": "literal",
        "source": "GEX p.18",
        "finding": "F09",
        "fn": balance_fade_own_aggression,
    },
    "OD_replenishment_band": {
        "kind": "OD",
        "source": "OD:REPLENISHMENT_BAND_TICKS=2",
        "finding": "F03",
        "fn": replenishment_band_ticks,
        "parameters": {"ticks": REPLENISHMENT_BAND_TICKS},
    },
}


def rules_payload() -> list[dict[str, Any]]:
    rows = []
    for rule_id, spec in RULES.items():
        fn = spec.get("fn") or _IMPL.get(rule_id)
        source = spec["source"]
        kind = spec["kind"]
        if kind == "OD" and not str(source).startswith("OD:"):
            source = f"OD:{source}"
        rows.append(
            {
                "rule_id": rule_id,
                "kind": kind,
                "source": source,
                "file_line": _file_line(fn) if fn is not None else f"sires_b02.py:RULES[{rule_id}]",
            }
        )
    return rows


def _as_view(market) -> NativeMarketView | None:
    if market is None:
        return None
    if isinstance(market, NativeMarketView) or hasattr(market, "arrays"):
        return market
    attached = getattr(market, "_native_view", None)
    if attached is not None:
        return attached
    day = getattr(market, "day", None)
    if day is None:
        return None
    try:
        return build_market_view(str(day), full_account_day=True)
    except Exception:
        return None


def _cutoff(arrays, rec: Mapping[str, Any]) -> int:
    if rec.get("b02_now_ns") is not None:
        return int(rec["b02_now_ns"])
    known = getattr(arrays, "known_at_ns", None)
    if known is not None and getattr(known, "size", 0):
        return int(known.max())
    return 2**62


def _gamma_from_market(market, rec: Mapping[str, Any], at_ns: int | None) -> str | None:
    if rec.get("gamma_regime") is not None:
        value = rec.get("gamma_regime")
        return None if value in {"", "none", "None"} else str(value)
    if market is None or at_ns is None:
        return None
    supplied = getattr(market, "supplied", None)
    if supplied is None:
        return None
    try:
        rows = supplied("gamma", at_ns)
    except Exception:
        return None
    if not rows:
        return None
    return rows[-1].get("regime")


def replenishment_ticks(arrays, level_ticks: int, side: str, cutoff: int) -> int | None:
    """Count executed passive refills in an OD tick band. STOP pp.10, 14."""
    n = arrays.t_ns.size
    if n == 0:
        return None
    band = replenishment_band_ticks()
    trade = arrays.is_trade & (arrays.known_at_ns <= cutoff)
    if not np.any(trade):
        return None
    px = arrays.price_ticks.astype(np.int64)
    sd = arrays.side
    in_band = np.abs(px - int(level_ticks)) <= int(band)
    if side == "long":
        refill = trade & in_band & (sd < 0)
    else:
        refill = trade & in_band & (sd > 0)
    return int(np.count_nonzero(refill))


def reward_ticks(arrays, origin_ticks: int, side: str, start_ns: int, cutoff: int) -> int | None:
    end = min(int(cutoff), int(start_ns) + reward_window_ns())
    trade = arrays.is_trade & (arrays.t_ns >= start_ns) & (arrays.t_ns <= end) & (arrays.known_at_ns <= cutoff)
    if not np.any(trade):
        return 0
    px = arrays.price_ticks[trade].astype(np.int64)
    if side == "long":
        return int(px.max() - origin_ticks)
    return int(origin_ticks - px.min())


def same_price_imbalance(arrays, cutoff: int) -> float | None:
    trade = arrays.is_trade & (arrays.known_at_ns <= cutoff)
    if not np.any(trade):
        return None
    px = arrays.price_ticks[trade]
    sd = arrays.side[trade]
    sz = arrays.size[trade]
    best = None
    for price in np.unique(px):
        at = px == price
        buys = int(sz[at & (sd > 0)].sum())
        sells = int(sz[at & (sd < 0)].sum())
        lo, hi = min(buys, sells), max(buys, sells)
        if lo <= 0:
            continue
        ratio = hi / lo
        if best is None or ratio > best:
            best = ratio
    return best


def path_features(arrays, cutoff: int, side: str) -> dict[str, Any]:
    sg = 1 if side == "long" else -1
    trade = arrays.is_trade & (arrays.known_at_ns <= cutoff)
    empty = {
        "release": False,
        "pullback": False,
        "failure": False,
        "opposite_absorbed": False,
        "origin_ticks": None,
        "extreme_ticks": None,
        "extreme_ns": None,
        "absorption_ns": None,
        "absorption_ticks": None,
        "aggression_size": None,
        "fill_ticks": None,
        "fill_ns": None,
        "drive_retest": False,
        "own_aggression": False,
    }
    if not np.any(trade):
        return empty
    t = arrays.t_ns[trade]
    px = arrays.price_ticks[trade].astype(np.int64)
    sz = arrays.size[trade].astype(np.int64)
    sd = arrays.side[trade].astype(np.int8)
    origin = int(px[0])
    extreme = origin
    extreme_i = 0
    for i in range(px.size):
        cur = int(px[i])
        if sg * (cur - extreme) > 0:
            extreme = cur
            extreme_i = i
        if sg * (extreme - cur) >= PULLBACK_TICKS:
            break
        if int(t[i] - t[0]) > FAST_RELEASE_NS:
            break
    release = fast_release_ok(abs(extreme - origin), int(t[extreme_i] - t[0]))
    pullback = False
    failure = False
    failure_i = None
    in_band = (sz >= AGGRESSION_MIN) & (sz <= AGGRESSION_MAX) & (sd * sg > 0)
    first_band = int(sz[int(np.flatnonzero(in_band)[0])]) if np.any(in_band) else (int(sz[0]) if sz.size else None)
    if release:
        for i in range(extreme_i + 1, px.size):
            cur = int(px[i])
            if sg * (extreme - cur) >= PULLBACK_TICKS:
                pullback = True
            if sg * (cur - origin) <= 0:
                failure = True
                if failure_i is None:
                    failure_i = i
    opposite = False
    absorption_ns = None
    absorption_ticks = None
    if release:
        after = np.arange(px.size) > extreme_i
        opp = after & (sd * sg < 0) & (np.abs(px.astype(np.int64) - extreme) <= 2)
        if np.any(opp):
            first_opp = int(np.flatnonzero(opp)[0])
            absorption_ticks = int(px[first_opp])
            absorption_ns = int(t[first_opp])
            later = (t >= t[first_opp]) & (t <= t[first_opp] + reward_window_ns())
            if np.any(later):
                if sg < 0:
                    moved = int(px[later].max()) - absorption_ticks
                else:
                    moved = absorption_ticks - int(px[later].min())
                opposite = moved < REWARD_MIN_TICKS
            else:
                opposite = True
    fill_ticks = None
    fill_ns = None
    drive_retest = False
    wick = extreme if release else None
    if failure:
        stop = wick + 1 if side == "long" else wick - 1
        start_i = failure_i if failure_i is not None else extreme_i + 1
        for i in range(start_i, px.size):
            cur = int(px[i])
            if side == "short" and cur <= stop:
                fill_ticks = cur
                fill_ns = int(t[i])
                break
            if side == "long" and cur >= stop:
                fill_ticks = cur
                fill_ns = int(t[i])
                break
        if pullback and opposite:
            drive_retest = True
            if fill_ns is None and absorption_ns is not None:
                fill_ticks = absorption_ticks
                fill_ns = absorption_ns
    elif release and opposite and not pullback:
        fill_ticks = absorption_ticks
        fill_ns = absorption_ns
    own_aggression = False
    if first_band is not None and release:
        after_ext = np.arange(px.size) > extreme_i
        own = after_ext & (sd * sg > 0) & (sz >= AGGRESSION_MIN) & (sz <= AGGRESSION_MAX)
        own_aggression = bool(np.any(own))
    return {
        "release": release,
        "pullback": pullback,
        "failure": failure,
        "opposite_absorbed": opposite,
        "origin_ticks": origin,
        "extreme_ticks": extreme,
        "extreme_ns": int(t[extreme_i]) if px.size else None,
        "absorption_ns": absorption_ns,
        "absorption_ticks": absorption_ticks,
        "aggression_size": first_band,
        "fill_ticks": fill_ticks,
        "fill_ns": fill_ns,
        "drive_retest": drive_retest,
        "wick_ticks": wick if failure else None,
        "own_aggression": own_aggression,
    }


def _combine(stage_rows: list[dict[str, Any]]) -> tuple[str, list[str], list[str]]:
    failed: list[str] = []
    unknown: list[str] = []
    for row in stage_rows:
        if row["verdict"] == "fail":
            failed.extend(str(k) for k in (row.get("operands") or {}) if (row.get("operands") or {})[k] is False)
            if not any(str(k) for k in (row.get("operands") or {}) if (row.get("operands") or {})[k] is False):
                failed.append(row["stage"])
        elif row["verdict"] == "unknown":
            unknown.extend(str(k) for k in (row.get("operands") or {}) if (row.get("operands") or {})[k] is None)
            if row["stage"] not in unknown:
                unknown.append(row["stage"])
    if failed:
        return "fail", failed, unknown
    if unknown:
        return "unknown", failed, unknown
    return "pass", failed, unknown


def _status(verdict: str, *, observation: bool = False) -> str:
    if observation:
        return {"pass": "condition_present", "fail": "condition_absent", "unknown": "data_unavailable"}[verdict]
    return {"pass": "setup", "fail": "no_setup", "unknown": "data_unavailable"}[verdict]


def _stage(name: str, verdict: str, at_ns: int | None, operands: dict[str, Any]) -> dict[str, Any]:
    return {"stage": name, "verdict": verdict, "at_ns": at_ns, "operands": operands}


def cascade_stages(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop later stages once an earlier stage is not pass."""
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(row)
        if row.get("verdict") != "pass":
            break
    return out


def _and_verdicts(*values: str) -> str:
    if "fail" in values:
        return "fail"
    if "unknown" in values:
        return "unknown"
    return "pass"


def _episode(
    *,
    family: str,
    branch: str,
    side: str,
    verdict: str,
    failed: list[str],
    unknown: list[str],
    values: dict[str, Any],
    stages: list[dict[str, Any]],
    decision_at: int | None,
    geometry: dict[str, Any],
    reference: dict[str, Any],
    trigger: dict[str, Any],
) -> dict[str, Any]:
    return {
        "candidate_id": f"b02:{family}:{branch}:{side}:{decision_at}",
        "method": family,
        "branch": branch,
        "side": side,
        "research_verdict": verdict,
        "status": _status(verdict),
        "failed": failed,
        "unknown": unknown,
        "values": values,
        "decision_at": decision_at,
        "geometry": geometry,
        "reference": reference,
        "trigger": trigger,
        "stages": stages,
        "rules": rules_payload(),
        "baseline_version": B02_VERSION,
    }


def _needed_gamma(branch: str) -> str | None:
    if branch == "ofm_aggressive":
        return "short"
    if branch == "balance_failure_fade":
        return "long"
    return None


def _branch_stages(
    branch: str,
    side: str,
    rec: Mapping[str, Any],
    features: Mapping[str, Any],
    replenish: int | None,
    reward: int | None,
    loc: str,
    gamma: str,
    daily: str,
    imb: str,
    at_ns: int | None,
    geometry: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    geo = dict(geometry or {})
    entry = geo.get("entry")
    stop = geo.get("stop")
    target = geo.get("target")
    killer = rec.get("thesis_killer")
    dead = thesis_dead(None if killer in {None, ""} else str(killer))
    context_operands = {
        "thesis_alive": (not dead) if killer not in {None, ""} else True,
        "structure_break": killer == "structure_break",
        "value_shift": killer == "value_shift",
        "new_information": killer == "new_information",
    }
    context_verdict = "fail" if dead else "pass"
    if _needed_gamma(branch):
        context_operands["gamma_regime"] = rec.get("gamma_regime")
        context_operands["gamma_needed"] = _needed_gamma(branch)
        if gamma == "fail":
            context_verdict = "fail"
        elif gamma == "unknown":
            context_verdict = "unknown"
    rows = [_stage("context", context_verdict, at_ns, context_operands)]
    rows.append(_stage("reference", "pass" if features.get("origin_ticks") is not None else "unknown", at_ns, {"origin_ticks": features.get("origin_ticks")}))
    loc_kind = rec.get("location_kind")
    loc_operands = {"location_kind": loc_kind, "eligible": loc_kind in ELIGIBLE_LOCATION_KINDS if loc_kind else None}
    rows.append(_stage("location", loc, at_ns, loc_operands))
    if branch == "clean_squeeze":
        trig = classify_clean_squeeze(features)
        rows.append(_stage("trigger", trig, features.get("extreme_ns"), {"release": features.get("release"), "pullback": features.get("pullback"), "failure": features.get("failure")}))
        conf = "pass" if features.get("opposite_absorbed") else "fail"
        rows.append(_stage("confirmation", conf, features.get("absorption_ns"), {"opposite_absorbed": features.get("opposite_absorbed")}))
    elif branch == "ofm_aggressive":
        variant = rec.get("entry_variant")
        rest = resting_stop_fill(features.get("wick_ticks"), features.get("fill_ticks"), side)
        drive = "pass" if features.get("drive_retest") else "fail"
        if variant == "drive_retest":
            trig = drive
        elif variant == "resting_stop":
            trig = rest
        else:
            trig = rest if rest == "pass" else drive
        rows.append(_stage("trigger", trig, features.get("fill_ns"), {"resting_stop": rest == "pass", "drive_retest": features.get("drive_retest"), "failure": features.get("failure")}))
        rows.append(_stage("confirmation", "pass" if features.get("failure") else "fail", features.get("fill_ns"), {"squeeze_failed": features.get("failure")}))
    elif branch in {"stop_four_stage", "absorption_reward_retest", "dom_rejection"}:
        trig = replenishment_ok(replenish) if branch == "stop_four_stage" else ("pass" if features.get("opposite_absorbed") else "fail")
        rows.append(_stage("trigger", trig, at_ns, {"replenishment_ticks": replenish}))
        rows.append(_stage("confirmation", reward_ok(reward), features.get("absorption_ns") or at_ns, {"reward_ticks": reward}))
    elif branch == "vwap_deviation_fade":
        vwap = rec.get("vwap_price_ticks")
        sd = rec.get("vwap_sd_ticks")
        px = features.get("fill_ticks") or features.get("extreme_ticks")
        beyond = None
        if vwap is not None and sd not in {None, 0} and px is not None:
            beyond = abs(int(px) - int(vwap)) >= int(sd)
        flag = footprint_flag_ok(rec.get("imbalance_ratio"))
        band = vwap_band_ok(beyond, features.get("opposite_absorbed"))
        rows.append(_stage("trigger", band, at_ns, {"beyond_1_band": beyond, "bands": list(VWAP_BANDS), "footprint_flag": flag}))
        rows.append(_stage("confirmation", "pass" if features.get("opposite_absorbed") else "fail", at_ns, {"absorption": features.get("opposite_absorbed")}))
    elif branch == "balance_failure_fade":
        fade_variant = rec.get("fade_variant") or FADE_UNPAID
        unpaid = balance_fade_unpaid(features.get("failure"), features.get("pullback"))
        own = balance_fade_own_aggression(features.get("failure"), features.get("pullback"), features.get("own_aggression"))
        conf = own if fade_variant == FADE_OWN_AGGRESSION else unpaid
        rows.append(_stage("trigger", "pass" if features.get("failure") else "fail", at_ns, {"failed_aggression": features.get("failure"), "fade_variant": fade_variant}))
        rows.append(_stage("confirmation", conf, at_ns, {"retest": features.get("pullback"), "own_aggression": features.get("own_aggression"), "unpaid": unpaid, "own_aggression_variant": own}))
    else:
        rows.append(_stage("trigger", "pass" if features.get("release") or features.get("fill_ns") else "unknown", at_ns, {"release": features.get("release")}))
        rows.append(_stage("confirmation", "pass" if features.get("opposite_absorbed") or features.get("fill_ns") else "unknown", at_ns, {"absorbed": features.get("opposite_absorbed")}))
    stop_ticks = rec.get("stop_ticks")
    risk_operands = {"daily_r": rec.get("account_daily_r"), "daily_stop_r": DAILY_STOP_R}
    risk_verdict = daily
    if branch == "ofm_aggressive" and stop_ticks is not None:
        ok_stop = OFM_STOP_TICKS_MIN <= int(stop_ticks) <= OFM_STOP_TICKS_MAX
        risk_operands["stop_ticks"] = stop_ticks
        if not ok_stop:
            risk_verdict = "fail"
    if branch in STOP_ENTRY_BRANCHES:
        level = rec.get("defended_ticks")
        if level is None:
            level = features.get("absorption_ticks") or features.get("extreme_ticks")
        entry_for_near = rec.get("entry_ticks") if rec.get("entry_ticks") is not None else entry
        near = entry_near_ok(entry_for_near, None if level is None else int(level))
        risk_operands["entry_distance_ticks"] = None if entry_for_near is None or level is None else abs(int(entry_for_near) - int(level))
        risk_operands["entry_near_1_2"] = near == "pass"
        risk_verdict = _and_verdicts(risk_verdict, near)
    rows.append(_stage("risk", risk_verdict, at_ns, risk_operands))
    forty = ofm_40_tick_target(entry, side)
    far = rec.get("control_zone_far_ticks")
    far_verdict = control_zone_target_ok(far)
    obj_verdict = "pass" if target is not None else "unknown"
    if branch == "ofm_aggressive":
        obj_verdict = "pass" if forty is not None else "unknown"
        if far is not None:
            obj_verdict = _and_verdicts(obj_verdict, far_verdict)
    obj_ops = {
        "target": target if target is not None else forty,
        "target_price_ticks": target if target is not None else forty,
        "ofm_target_40_ticks": OFM_TARGET_TICKS,
        "control_zone_far_ticks": far,
    }
    rows.append(_stage("objective", obj_verdict, at_ns, obj_ops))
    partial = partial_1to1_ok(entry, stop)
    trail = trail_protected_ok(
        True if features.get("release") else False,
        True if features.get("aggression_size") is not None else False,
        features.get("extreme_ticks"),
    )
    mg_verdict = _and_verdicts(daily, partial, trail)
    rows.append(
        _stage(
            "management",
            mg_verdict,
            at_ns,
            {
                "partial_1_to_1": partial == "pass",
                "stop_to_breakeven": partial == "pass",
                "trail_after_close_with_aggression": trail == "pass",
                "daily_stop_r": DAILY_STOP_R,
                "partial_verdict": partial,
                "trail_verdict": trail,
            },
        )
    )
    return cascade_stages(rows)


def _geometry(branch: str, side: str, features: Mapping[str, Any], rec: Mapping[str, Any]) -> dict[str, Any]:
    entry = features.get("fill_ticks")
    if entry is None:
        entry = features.get("absorption_ticks")
    wick = features.get("wick_ticks") or features.get("extreme_ticks")
    stop = None
    target = None
    if entry is not None:
        if side == "short":
            stop = int(entry) + int(rec.get("stop_ticks") or (OFM_STOP_TICKS_MIN if branch == "ofm_aggressive" else 8))
        else:
            stop = int(entry) - int(rec.get("stop_ticks") or (OFM_STOP_TICKS_MIN if branch == "ofm_aggressive" else 8))
        target = ofm_40_tick_target(int(entry), side)
        if rec.get("control_zone_far_ticks") is not None and rec.get("objective_variant") == "control_zone":
            target = int(rec["control_zone_far_ticks"])
    far = rec.get("control_zone_far_ticks")
    return {
        "entry": entry,
        "stop": stop,
        "target": target,
        "ofm_target_40_ticks": target,
        "control_zone_far_ticks": far,
        "wick_ticks": wick,
    }


def scan_b02(market, rec) -> dict[str, Any]:
    rec = dict(rec or {})
    family = rec.get("method_id") or rec.get("family") or "SIRES"
    branch = rec.get("branch") or rec.get("source_branch") or "clean_squeeze"
    view = _as_view(market)
    arrays = None if view is None else view.arrays
    if arrays is None or arrays.t_ns.size == 0:
        return {
            "schema_version": "research-family-b02-scan-v1",
            "baseline_version": B02_VERSION,
            "family": family,
            "branch": branch,
            "coverage_id": rec.get("coverage_id") or f"{family}:branch:{branch}",
            "episodes": [],
            "omissions": [{"reason": "operands_unavailable", "operand": "native_executions"}],
            "rules": rules_payload(),
        }
    cutoff = _cutoff(arrays, rec)
    sides = (rec.get("side"),) if rec.get("side") in {"long", "short"} else ("long", "short")
    loc = location_ok(rec.get("location_kind"))
    daily = daily_stop_ok(None if rec.get("account_daily_r") is None else float(rec["account_daily_r"]))
    imb_ratio = same_price_imbalance(arrays, cutoff)
    imb = imbalance_ok(imb_ratio)
    rec = {**rec, "imbalance_ratio": imb_ratio}
    episodes = []
    for side in sides:
        features = path_features(arrays, cutoff, side)
        at_ns = features.get("fill_ns") or features.get("absorption_ns") or features.get("extreme_ns")
        gamma_actual = _gamma_from_market(market, rec, at_ns)
        gamma = gamma_ok(_needed_gamma(branch), gamma_actual)
        level = rec.get("defended_ticks")
        if level is None:
            level = features.get("absorption_ticks") or features.get("extreme_ticks")
        replenish = replenishment_ticks(arrays, int(level), side, cutoff) if level is not None else None
        origin = features.get("absorption_ticks") or features.get("extreme_ticks")
        start = features.get("absorption_ns") or features.get("extreme_ns") or 0
        if branch in STOP_ENTRY_BRANCHES and rec.get("defended_ticks") is not None:
            origin = int(rec["defended_ticks"])
            start = int(arrays.t_ns[0]) if arrays.t_ns.size else 0
        reward = reward_ticks(arrays, int(origin), side, int(start), cutoff) if origin is not None else None
        geo = _geometry(branch, side, features, rec)
        stages = _branch_stages(branch, side, rec, features, replenish, reward, loc, gamma, daily, imb, at_ns, geometry=geo)
        if branch == "ofm_aggressive":
            variants = []
            if features.get("failure") and features.get("fill_ticks") is not None and not features.get("drive_retest"):
                variants.append("resting_stop")
            if features.get("drive_retest"):
                variants.append("drive_retest")
            if rec.get("entry_variant"):
                variants = [rec["entry_variant"]]
            if not variants:
                variants = [None]
            for variant in variants:
                rec_v = dict(rec)
                rec_v["entry_variant"] = variant
                st = _branch_stages(branch, side, rec_v, features, replenish, reward, loc, gamma, daily, imb, at_ns, geometry=geo)
                verdict, failed, unknown = _combine(st)
                values = {
                    "branch": branch,
                    "side": side,
                    "location_kind": rec.get("location_kind"),
                    "gamma_regime": gamma_actual,
                    "replenishment_ticks": replenish,
                    "reward_ticks": reward,
                    "aggression_size": features.get("aggression_size"),
                    "imbalance_ratio": imb_ratio,
                    "entry_variant": variant or ("resting_stop" if features.get("failure") else None),
                    "ofm_entry_variant": variant or ("resting_stop" if features.get("failure") else None),
                    "pullback": features.get("pullback"),
                    "release": features.get("release"),
                    "failure": features.get("failure"),
                    "thesis_killer": rec.get("thesis_killer"),
                    "vwap_bands": list(VWAP_BANDS),
                    "partial_1_to_1": partial_1to1_ok(geo.get("entry"), geo.get("stop")) == "pass",
                    "trail_after_close_with_aggression": trail_protected_ok(features.get("release"), features.get("aggression_size") is not None, features.get("extreme_ticks")) == "pass",
                    "daily_stop_r": DAILY_STOP_R,
                    "target": geo.get("target"),
                }
                episodes.append(
                    _episode(
                        family=family,
                        branch=branch,
                        side=side,
                        verdict=verdict,
                        failed=failed,
                        unknown=unknown,
                        values=values,
                        stages=st,
                        decision_at=at_ns,
                        geometry=geo,
                        reference={"kind": rec.get("location_kind"), "ticks": origin},
                        trigger={"at_ns": at_ns, "ticks": features.get("fill_ticks")},
                    )
                )
            continue
        if branch == "balance_failure_fade":
            fade_variants = [rec["fade_variant"]] if rec.get("fade_variant") else [FADE_UNPAID, FADE_OWN_AGGRESSION]
            for fade_variant in fade_variants:
                rec_v = dict(rec)
                rec_v["fade_variant"] = fade_variant
                st = _branch_stages(branch, side, rec_v, features, replenish, reward, loc, gamma, daily, imb, at_ns, geometry=geo)
                verdict, failed, unknown = _combine(st)
                values = {
                    "branch": branch,
                    "side": side,
                    "location_kind": rec.get("location_kind"),
                    "gamma_regime": gamma_actual,
                    "fade_variant": fade_variant,
                    "own_aggression": features.get("own_aggression"),
                    "failure": features.get("failure"),
                    "pullback": features.get("pullback"),
                    "target": geo.get("target"),
                    "daily_stop_r": DAILY_STOP_R,
                }
                episodes.append(
                    _episode(
                        family=family,
                        branch=branch,
                        side=side,
                        verdict=verdict,
                        failed=failed,
                        unknown=unknown,
                        values=values,
                        stages=st,
                        decision_at=at_ns,
                        geometry=geo,
                        reference={"kind": rec.get("location_kind"), "ticks": origin},
                        trigger={"at_ns": at_ns, "ticks": features.get("fill_ticks") or origin},
                    )
                )
            continue
        verdict, failed, unknown = _combine(stages)
        if branch == "clean_squeeze":
            squeeze = classify_clean_squeeze(features)
            if squeeze == "fail" and "trigger" not in failed:
                failed.append("first_pullback" if features.get("pullback") else "clean_squeeze")
                verdict = "fail"
        values = {
            "branch": branch,
            "side": side,
            "location_kind": rec.get("location_kind"),
            "gamma_regime": gamma_actual,
            "replenishment_ticks": replenish,
            "reward_ticks": reward,
            "three_tick_replenishment": replenish is not None and replenish >= REPLENISHMENT_MIN_TICKS,
            "aggression_size": features.get("aggression_size"),
            "aggression_in_band": features.get("aggression_size") is not None and AGGRESSION_MIN <= int(features["aggression_size"]) <= AGGRESSION_MAX,
            "imbalance_ratio": imb_ratio,
            "pullback": features.get("pullback"),
            "release": features.get("release"),
            "failure": features.get("failure"),
            "opposite_absorbed": features.get("opposite_absorbed"),
            "thesis_killer": rec.get("thesis_killer"),
            "vwap_bands": list(VWAP_BANDS),
            "partial_1_to_1": partial_1to1_ok(geo.get("entry"), geo.get("stop")) == "pass",
            "trail_after_close_with_aggression": trail_protected_ok(features.get("release"), features.get("aggression_size") is not None, features.get("extreme_ticks")) == "pass",
            "daily_stop_r": DAILY_STOP_R,
            "target": geo.get("target"),
            "fade_variant": rec.get("fade_variant"),
            "own_aggression": features.get("own_aggression"),
        }
        episodes.append(
            _episode(
                family=family,
                branch=branch,
                side=side,
                verdict=verdict,
                failed=failed,
                unknown=unknown,
                values=values,
                stages=stages,
                decision_at=at_ns,
                geometry=geo,
                reference={"kind": rec.get("location_kind"), "ticks": origin},
                trigger={"at_ns": at_ns, "ticks": features.get("fill_ticks") or origin},
            )
        )
    return {
        "schema_version": "research-family-b02-scan-v1",
        "baseline_version": B02_VERSION,
        "family": family,
        "branch": branch,
        "coverage_id": rec.get("coverage_id") or f"{family}:branch:{branch}",
        "episodes": episodes,
        "omissions": [],
        "rules": rules_payload(),
    }


def _parse_window(day: str, text: str | None) -> tuple[int | None, int | None]:
    if not text:
        return None, None
    match = re.search(r"(\d{1,2}):(\d{2})\s*[-–]\s*(\d{1,2}):(\d{2})", text)
    if not match:
        return None, None
    d = date.fromisoformat(day)
    start = et_ns(d, int(match.group(1)), int(match.group(2)))
    end = et_ns(d, int(match.group(3)), int(match.group(4)))
    if end <= start:
        end = et_ns(d, int(match.group(3)), int(match.group(4))) + 24 * 3600 * NS
    return start, end


def _author_side(example: Mapping[str, Any]) -> str | None:
    expected = (example.get("expected_detection") or {}).get("side")
    actions = example.get("actions") or []
    token = None
    if actions:
        token = (actions[0].get("action") or "").lower()
    if token in {"sell", "sell_stop", "short"}:
        return "short"
    if token in {"buy", "buy_stop", "long"}:
        return "long"
    if expected:
        text = str(expected).lower()
        if "short" in text and "long" not in text:
            return "short"
        if "long" in text and "short" not in text:
            return "long"
    return None


def _author_level(example: Mapping[str, Any]) -> float | None:
    for action in example.get("actions") or []:
        price = action.get("price")
        if isinstance(price, (int, float)):
            return float(price)
    levels = example.get("levels") or {}
    for value in levels.values():
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, list) and value and isinstance(value[0], (int, float)):
            return float(value[0])
    return None


def _branch_tokens(text: str | None) -> set[str]:
    if not text:
        return set()
    parts = re.split(r"[/,;]| then ", str(text))
    return {p.strip() for p in parts if p.strip()}


def replay_example(market, example) -> dict[str, Any]:
    example = dict(example or {})
    author_level = _author_level(example)
    author_side = _author_side(example)
    expected = example.get("expected_detection") or {}
    wanted = _branch_tokens(expected.get("branch"))
    day = example.get("date")
    empty = {
        "detected": None,
        "branch": None,
        "our_side": None,
        "our_level": None,
        "our_entry_ns": None,
        "author_level": author_level,
        "author_side": author_side,
        "divergence": "date_outside_tape",
    }
    view = _as_view(market)
    if view is None or view.arrays.t_ns.size == 0:
        if day:
            try:
                view = build_market_view(str(day), full_account_day=True)
            except Exception:
                return empty
        else:
            return empty
    if view is None or view.arrays.t_ns.size == 0:
        return empty
    start_ns, end_ns = _parse_window(str(day), expected.get("entry_window_et"))
    rec_base = {
        "method_id": "SIRES",
        "location_kind": "real_extreme",
        "gamma_regime": None,
    }
    from trading_research.research.rule_discovery.source_adapters.common import FAMILY_BRANCHES

    hits = []
    scanned = []
    for branch in FAMILY_BRANCHES["SIRES"]:
        if wanted and not any(branch in token or token in branch for token in wanted):
            if not any(token.split()[0] == branch for token in wanted):
                continue
        doc = scan_b02(view, {**rec_base, "branch": branch})
        scanned.append(branch)
        for ep in doc.get("episodes") or []:
            hits.append(ep)
    if not hits:
        for branch in FAMILY_BRANCHES["SIRES"]:
            if branch in scanned:
                continue
            doc = scan_b02(view, {**rec_base, "branch": branch})
            hits.extend(doc.get("episodes") or [])
    if not hits:
        unknown_only = True
        return {
            "detected": None if unknown_only else False,
            "branch": None,
            "our_side": None,
            "our_level": None,
            "our_entry_ns": None,
            "author_level": author_level,
            "author_side": author_side,
            "divergence": "operands_unavailable" if view.arrays.t_ns.size == 0 else "miss:no_episode",
        }

    def level_of(ep):
        geo = ep.get("geometry") or {}
        values = ep.get("values") or {}
        ref = ep.get("reference") or {}
        for raw in (
            geo.get("entry"),
            geo.get("reference_level"),
            geo.get("reference_px"),
            values.get("entry"),
            values.get("reference_px"),
            ref.get("ticks"),
            geo.get("wick_ticks"),
        ):
            if raw is None:
                continue
            try:
                return float(raw) * TICK_POINTS
            except (TypeError, ValueError):
                continue
        return None

    best = None
    reason = "miss:no_episode"
    for ep in hits:
        branch = ep.get("branch")
        side = ep.get("side")
        our_level = level_of(ep)
        entry_ns = ep.get("decision_at")
        if wanted and not any(branch in token or token.split()[0] == branch for token in wanted):
            reason = "miss:branch"
            continue
        if author_side and side != author_side and author_side not in str((example.get("expected_detection") or {}).get("side") or ""):
            reason = "miss:side"
            continue
        if author_side and side != author_side and "," not in str((example.get("expected_detection") or {}).get("side") or "") and "then" not in str((example.get("expected_detection") or {}).get("side") or "").lower():
            reason = "miss:side"
            continue
        if author_level is not None and our_level is not None:
            ticks = abs(our_level - author_level) / TICK_POINTS
            if ticks > level_tolerance_ticks():
                reason = "miss:level"
                continue
        if start_ns is not None and end_ns is not None and entry_ns is not None:
            if not (start_ns <= int(entry_ns) < end_ns):
                reason = "miss:window"
                continue
        best = ep
        break
    if best is None:
        # Multi-side examples: accept first episode of a wanted branch
        for ep in hits:
            branch = ep.get("branch")
            if wanted and not any(branch in token or token.split()[0] == branch for token in wanted):
                continue
            best = ep
            reason = "match_branch_only"
            break
    if best is None:
        return {
            "detected": False,
            "branch": hits[0].get("branch") if hits else None,
            "our_side": hits[0].get("side") if hits else None,
            "our_level": level_of(hits[0]) if hits else None,
            "our_entry_ns": hits[0].get("decision_at") if hits else None,
            "author_level": author_level,
            "author_side": author_side,
            "divergence": reason,
        }
    return {
        "detected": True if reason != "match_branch_only" else False,
        "branch": best.get("branch"),
        "our_side": best.get("side"),
        "our_level": level_of(best),
        "our_entry_ns": best.get("decision_at"),
        "author_level": author_level,
        "author_side": author_side,
        "divergence": _replay_divergence(reason, best.get("side"), author_side),
    }


def _replay_divergence(reason: str, our_side, author_side) -> str:
    if reason != "match_branch_only":
        return "match"
    if author_side and our_side and our_side != author_side:
        return f"match_branch_only;miss:side our={our_side} author={author_side}"
    return "match_branch_only"
