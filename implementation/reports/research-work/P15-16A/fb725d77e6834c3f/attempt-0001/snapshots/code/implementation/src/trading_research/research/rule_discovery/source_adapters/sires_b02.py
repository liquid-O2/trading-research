"""SIRES B0.2 scan. Independent of frozen B0 / B0.1 scanners."""
from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Mapping
import inspect
import re

import numpy as np

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.rule_discovery.formations import complete_minute_rows, f3_balance
from trading_research.research.rule_discovery.native import NS, NativeMarketView, bars_reduceat, build_market_view
from trading_research.research.rule_discovery.profiles import build_profile

B02_VERSION = "B0.2-2026-09-15"
STAGE_ORDER = ("context", "reference", "location", "trigger", "confirmation", "risk", "objective", "management")
ELIGIBLE_LOCATION_KINDS = frozenset(
    {
        "shelf",
        "ledge",
        "lvn",
        "minor_volume_node",
        "real_extreme",
        "vwap_band",
        "kg1",
        "microbalance",
        "control_zone",
    }
)
FORBIDDEN_LOCATION_KINDS = frozenset({"poc", "inside_balance", "current_day_vah", "current_day_val"})
IDENTITY_KEYS = frozenset({"method_id", "family", "branch", "source_branch", "coverage_id", "b02_now_ns"})
AUTHOR_CONTEXT_KEYS = frozenset(
    {
        "location_kind",
        "defended_ticks",
        "gamma_regime",
        "thesis_killer",
        "entry_variant",
        "entry_ticks",
        "stop_ticks",
        "control_zone_far_ticks",
        "fade_variant",
        "account_daily_r",
        "vwap_price_ticks",
        "vwap_sd_ticks",
        "objective_variant",
        "side",
    }
)
CONTACT_DEPARTURE_TICKS = 4
CONTACT_BAND_TICKS = 2
MAX_CONTACTS_PER_LOCATION = 1
MAX_LOCATIONS = 16
MAX_SWING_PIVOTS = 8
PIVOT_RADIUS = 1
PROFILE_BANDWIDTH = 2
STRUCTURE_BREAK_TICKS = 8
FEATURE_WINDOW_NS = 20 * NS
GAMMA_UNOBSERVABLE = "gamma regime not observable in Phase 1.5 inputs; Phase 2 options boards supply it"
DAILY_R_UNOBSERVABLE = "account daily R not observable in Phase 1.5 inputs"
NEWS_UNOBSERVABLE = "new information (news) not observable in Phase 1.5 inputs"
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


@_register("F03_fresh_reward_retest")
def fresh_reward_retest_ok(reward: int | None, retest: bool | None) -> str:
    """ABS pp.5-13: own 3-tick reward then a distinct return to the rewarded area."""
    rewarded = reward_ok(reward)
    if rewarded != "pass":
        return rewarded
    if retest is None:
        return "unknown"
    return "pass" if retest else "fail"


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
def control_zone_target_ok(far_ticks: int | None, entry_ticks: int | None = None, side: str | None = None) -> str:
    """BIG pp.10, 15-16: far side of the last control zone, beyond the entry."""
    if far_ticks is None:
        return "unknown"
    if entry_ticks is None or side not in {"long", "short"}:
        return "pass"
    if side == "short":
        return "pass" if int(far_ticks) < int(entry_ticks) else "fail"
    return "pass" if int(far_ticks) > int(entry_ticks) else "fail"


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
    "F03_fresh_reward_retest": {
        "kind": "literal",
        "source": "ABS pp.5-13",
        "finding": "F03",
        "fn": fresh_reward_retest_ok,
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


def _identity_rec(rec: Mapping[str, Any] | None) -> dict[str, Any]:
    src = dict(rec or {})
    out: dict[str, Any] = {}
    for key in IDENTITY_KEYS:
        if key in src and src[key] is not None:
            out[key] = src[key]
    return out


def _cutoff(arrays, rec: Mapping[str, Any]) -> int:
    if rec.get("b02_now_ns") is not None:
        return int(rec["b02_now_ns"])
    known = getattr(arrays, "known_at_ns", None)
    if known is not None and getattr(known, "size", 0):
        return int(known.max())
    return 2**62


def _cash_open_ns(view: NativeMarketView, arrays) -> int:
    day = getattr(view, "account_day", "") or ""
    try:
        if day:
            return et_ns(date.fromisoformat(str(day)[:10]), 9, 30)
    except ValueError:
        pass
    if arrays.t_ns.size:
        return int(arrays.t_ns[0])
    return 0


def _gamma_from_market(market, at_ns: int | None) -> str | None:
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


def replenishment_ticks(
    arrays,
    level_ticks: int,
    side: str,
    cutoff: int,
    *,
    start_ns: int | None = None,
    end_ns: int | None = None,
) -> int | None:
    """Count executed passive refills in an OD tick band. STOP pp.10, 14."""
    n = arrays.t_ns.size
    if n == 0:
        return None
    band = replenishment_band_ticks()
    trade = arrays.is_trade & (arrays.known_at_ns <= cutoff)
    if start_ns is not None:
        trade = trade & (arrays.t_ns >= int(start_ns))
    if end_ns is not None:
        trade = trade & (arrays.t_ns <= int(end_ns))
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


def reward_area_retest(
    arrays,
    origin_ticks: int,
    side: str,
    start_ns: int,
    cutoff: int,
) -> bool | None:
    """After a 3-tick own reward, price returns to origin ± 2. ABS pp.5-13.

    Look-ahead is the already-registered reward window after the first reward print,
    clipped by the feature window from the contact. Not a new fitted horizon.
    """
    sg = 1 if side == "long" else -1
    end = min(int(cutoff), int(start_ns) + FEATURE_WINDOW_NS + reward_window_ns())
    trade = arrays.is_trade & (arrays.t_ns >= int(start_ns)) & (arrays.t_ns <= end) & (arrays.known_at_ns <= int(cutoff))
    if not np.any(trade):
        return None
    px = arrays.price_ticks[trade].astype(np.int64)
    t = arrays.t_ns[trade]
    origin = int(origin_ticks)
    reward_i = None
    for i in range(px.size):
        if sg * (int(px[i]) - origin) >= REWARD_MIN_TICKS:
            reward_i = i
            break
    if reward_i is None:
        return False
    retest_end = min(int(end), int(t[reward_i]) + reward_window_ns())
    for i in range(reward_i + 1, px.size):
        if int(t[i]) > retest_end:
            break
        if abs(int(px[i]) - origin) <= CONTACT_BAND_TICKS:
            return True
    return False


def same_price_imbalance(arrays, cutoff: int) -> float | None:
    return same_price_imbalance_at(arrays, None, cutoff)


def same_price_imbalance_at(arrays, price_ticks: int | None, cutoff: int, *, start_ns: int | None = None, end_ns: int | None = None) -> float | None:
    trade = arrays.is_trade & (arrays.known_at_ns <= cutoff)
    if start_ns is not None:
        trade = trade & (arrays.t_ns >= int(start_ns))
    if end_ns is not None:
        trade = trade & (arrays.t_ns <= int(end_ns))
    if not np.any(trade):
        return None
    px = arrays.price_ticks[trade]
    sd = arrays.side[trade]
    sz = arrays.size[trade]
    prices = np.unique(px) if price_ticks is None else np.array([int(price_ticks)])
    best = None
    for price in prices:
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


def footprint_ratio_at(arrays, price_ticks: int, cutoff: int, *, start_ns: int | None = None, end_ns: int | None = None) -> float | None:
    return same_price_imbalance_at(arrays, price_ticks, cutoff, start_ns=start_ns, end_ns=end_ns)


def vwap_at(arrays, start_ns: int, end_ns: int, cutoff: int) -> tuple[float | None, float | None]:
    trade = arrays.is_trade & (arrays.t_ns >= int(start_ns)) & (arrays.t_ns <= int(end_ns)) & (arrays.known_at_ns <= cutoff)
    if not np.any(trade):
        return None, None
    px = arrays.price_ticks[trade].astype(np.float64)
    sz = arrays.size[trade].astype(np.float64)
    total = float(sz.sum())
    if total <= 0:
        return None, None
    mean = float((px * sz).sum() / total)
    var = float((sz * (px - mean) ** 2).sum() / total)
    sd = var ** 0.5
    return mean, sd


def path_features(
    arrays,
    cutoff: int,
    side: str,
    start_ns: int | None = None,
    origin_ticks: int | None = None,
) -> dict[str, Any]:
    sg = 1 if side == "long" else -1
    trade = arrays.is_trade & (arrays.known_at_ns <= cutoff)
    if start_ns is not None:
        trade = trade & (arrays.t_ns >= int(start_ns)) & (arrays.t_ns <= int(start_ns) + FEATURE_WINDOW_NS)
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
        "wick_ticks": None,
    }
    if not np.any(trade):
        return empty
    t = arrays.t_ns[trade]
    px = arrays.price_ticks[trade].astype(np.int64)
    sz = arrays.size[trade].astype(np.int64)
    sd = arrays.side[trade].astype(np.int8)
    origin = int(origin_ticks) if origin_ticks is not None else int(px[0])
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
        if pullback:
            drive_retest = True
            if fill_ns is None and absorption_ns is not None:
                fill_ticks = absorption_ticks
                fill_ns = absorption_ns
            if fill_ns is None:
                fill_ticks = int(px[-1])
                fill_ns = int(t[-1])
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
    """Keep later stages after unknown. Stop after the first fail."""
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(row)
        if row.get("verdict") == "fail":
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


def _dedupe_locations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = (row.get("kind"), int(row["ticks"]), row.get("role"))
        prior = seen.get(key)
        if prior is None or int(row["known_at_ns"]) < int(prior["known_at_ns"]):
            seen[key] = row
    out = list(seen.values())
    rank = {
        "real_extreme": 0,
        "lvn": 1,
        "minor_volume_node": 2,
        "shelf": 3,
        "ledge": 4,
        "control_zone": 5,
        "microbalance": 6,
        "kg1": 7,
        "vwap_band": 8,
    }
    out.sort(key=lambda r: (rank.get(str(r.get("kind")), 9), int(r["known_at_ns"]), int(r["ticks"])))
    swings = [row for row in out if row.get("kind") == "real_extreme" and row.get("window") == "swing"]
    rest = [row for row in out if not (row.get("kind") == "real_extreme" and row.get("window") == "swing")]
    swings.sort(key=lambda r: int(r["known_at_ns"]))
    if len(swings) > MAX_SWING_PIVOTS:
        half = MAX_SWING_PIVOTS // 2
        swings = swings[:half] + swings[-half:]
    micros = [row for row in rest if row.get("kind") == "microbalance"]
    rest = [row for row in rest if row.get("kind") != "microbalance"]
    if len(micros) > 4:
        micros = micros[:4]
    merged = rest + micros + swings
    merged.sort(key=lambda r: (rank.get(str(r.get("kind")), 9), int(r["known_at_ns"]), int(r["ticks"])))
    return merged[:MAX_LOCATIONS]


def _add_extreme(out: list[dict[str, Any]], arrays, mask, *, window: str) -> None:
    if not np.any(mask):
        return
    px = arrays.price_ticks[mask].astype(np.int64)
    kn = arrays.known_at_ns[mask]
    hi = int(px.max())
    lo = int(px.min())
    hi_i = int(np.argmax(px))
    lo_i = int(np.argmin(px))
    out.append(
        {
            "kind": "real_extreme",
            "ticks": hi,
            "known_at_ns": int(kn[hi_i]),
            "role": "high",
            "window": window,
        }
    )
    out.append(
        {
            "kind": "real_extreme",
            "ticks": lo,
            "known_at_ns": int(kn[lo_i]),
            "role": "low",
            "window": window,
        }
    )


def enumerate_locations(view: NativeMarketView, cutoff: int) -> list[dict[str, Any]]:
    """Source-literal locations from the market. F09 / RR-20. Never POC or inside balance as a kind."""
    arrays = view.arrays
    out: list[dict[str, Any]] = []
    trade = arrays.is_trade & (arrays.known_at_ns <= cutoff)
    if not np.any(trade):
        return out
    cash = _cash_open_ns(view, arrays)
    on_mask = trade & (arrays.t_ns < cash)
    rth_mask = trade & (arrays.t_ns >= cash)
    _add_extreme(out, arrays, on_mask, window="overnight")
    _add_extreme(out, arrays, rth_mask if np.any(rth_mask) else trade, window="session")
    start = int(arrays.t_ns[trade][0])
    try:
        bars = bars_reduceat(arrays, start, int(cutoff) + 1, 60)
    except Exception:
        bars = []
    radius = PIVOT_RADIUS
    for i in range(radius, len(bars) - radius):
        highs = [int(bars[j]["high_ticks"]) for j in range(i - radius, i + radius + 1)]
        lows = [int(bars[j]["low_ticks"]) for j in range(i - radius, i + radius + 1)]
        known = int(bars[i + radius]["known_at_ns"])
        if known > cutoff:
            continue
        if cash and known > int(cash) + 2 * 3600 * NS:
            continue
        if int(bars[i]["high_ticks"]) >= max(highs):
            out.append(
                {
                    "kind": "real_extreme",
                    "ticks": int(bars[i]["high_ticks"]),
                    "known_at_ns": known,
                    "role": "high",
                    "window": "swing",
                }
            )
        if int(bars[i]["low_ticks"]) <= min(lows):
            out.append(
                {
                    "kind": "real_extreme",
                    "ticks": int(bars[i]["low_ticks"]),
                    "known_at_ns": known,
                    "role": "low",
                    "window": "swing",
                }
            )
        if i >= 2:
            prev_h = int(bars[i - 1]["high_ticks"])
            prev_l = int(bars[i - 1]["low_ticks"])
            cur_h = int(bars[i]["high_ticks"])
            cur_l = int(bars[i]["low_ticks"])
            if cur_h < prev_h and cur_l > prev_l:
                out.append(
                    {
                        "kind": "microbalance",
                        "ticks": int((prev_h + prev_l) // 2),
                        "known_at_ns": known,
                        "role": "high" if abs(cur_h - prev_h) <= abs(cur_l - prev_l) else "low",
                        "window": "microbalance",
                        "high_ticks": prev_h,
                        "low_ticks": prev_l,
                    }
                )
    va_low = va_high = None
    if np.any(on_mask):
        try:
            profile = build_profile(
                arrays.price_ticks[on_mask],
                arrays.size[on_mask],
                bandwidth=PROFILE_BANDWIDTH,
                window="overnight",
                as_of_ns=int(cash) - 1 if cash else int(cutoff),
            )
        except Exception:
            profile = {"available": False}
        if profile.get("available"):
            va = profile.get("value_area") or {}
            va_low = va.get("val_ticks")
            va_high = va.get("vah_ticks")
            if va_low is not None and va_high is not None:
                out.append(
                    {
                        "kind": "control_zone",
                        "ticks": int(va_high),
                        "known_at_ns": int(cash) if cash else int(cutoff),
                        "role": "high",
                        "window": "overnight_va",
                        "far_ticks": int(va_low),
                    }
                )
                out.append(
                    {
                        "kind": "control_zone",
                        "ticks": int(va_low),
                        "known_at_ns": int(cash) if cash else int(cutoff),
                        "role": "low",
                        "window": "overnight_va",
                        "far_ticks": int(va_high),
                    }
                )
            for item in profile.get("lvn") or []:
                tick = item.get("tick")
                if tick is None:
                    continue
                out.append(
                    {
                        "kind": "lvn",
                        "ticks": int(tick),
                        "known_at_ns": int(cash) if cash else int(cutoff),
                        "role": "both",
                        "window": "overnight",
                    }
                )
                if item.get("prominence") is not None and float(item["prominence"]) < 0.4:
                    out.append(
                        {
                            "kind": "minor_volume_node",
                            "ticks": int(tick),
                            "known_at_ns": int(cash) if cash else int(cutoff),
                            "role": "both",
                            "window": "overnight",
                        }
                    )
            for item in profile.get("shelves") or []:
                lo = item.get("low_ticks")
                hi = item.get("high_ticks")
                if lo is None or hi is None:
                    continue
                mid = int((int(lo) + int(hi)) // 2)
                out.append(
                    {
                        "kind": "shelf",
                        "ticks": mid,
                        "known_at_ns": int(cash) if cash else int(cutoff),
                        "role": "both",
                        "window": "overnight",
                        "low_ticks": int(lo),
                        "high_ticks": int(hi),
                    }
                )
            for item in profile.get("ledges") or []:
                tick = item.get("tick")
                if tick is None:
                    continue
                out.append(
                    {
                        "kind": "ledge",
                        "ticks": int(tick),
                        "known_at_ns": int(cash) if cash else int(cutoff),
                        "role": "both",
                        "window": "overnight",
                    }
                )
    try:
        rows = complete_minute_rows(arrays, int(arrays.start_ns), int(cutoff))
        formed = f3_balance(rows, issue_ns=min(int(cutoff), int(cash) if cash else int(cutoff)))
        if formed.get("available") and formed.get("rows"):
            window = formed["rows"]
            hi = max(int(r["high_ticks"]) for r in window)
            lo = min(int(r["low_ticks"]) for r in window)
            known = max(int(r["known_at_ns"]) for r in window)
            out.append(
                {
                    "kind": "microbalance",
                    "ticks": hi,
                    "known_at_ns": known,
                    "role": "high",
                    "window": "f3",
                    "high_ticks": hi,
                    "low_ticks": lo,
                    "far_ticks": lo,
                }
            )
            out.append(
                {
                    "kind": "microbalance",
                    "ticks": lo,
                    "known_at_ns": known,
                    "role": "low",
                    "window": "f3",
                    "high_ticks": hi,
                    "low_ticks": lo,
                    "far_ticks": hi,
                }
            )
            out.append(
                {
                    "kind": "control_zone",
                    "ticks": hi,
                    "known_at_ns": known,
                    "role": "high",
                    "window": "f3",
                    "far_ticks": lo,
                }
            )
            out.append(
                {
                    "kind": "control_zone",
                    "ticks": lo,
                    "known_at_ns": known,
                    "role": "low",
                    "window": "f3",
                    "far_ticks": hi,
                }
            )
    except Exception:
        pass
    vwap_start = int(cash) if np.any(rth_mask) else start
    snapshots = [int(cash) + 15 * 60 * NS]
    for at in snapshots:
        if at > cutoff or at < vwap_start:
            continue
        mean, sd = vwap_at(arrays, vwap_start, at, cutoff)
        if mean is None or sd is None or sd <= 0:
            continue
        for mult in VWAP_BANDS:
            out.append(
                {
                    "kind": "vwap_band",
                    "ticks": int(round(mean + mult * sd)),
                    "known_at_ns": at,
                    "role": "high",
                    "window": "vwap",
                    "band": float(mult),
                    "vwap_ticks": mean,
                    "vwap_sd_ticks": sd,
                }
            )
            out.append(
                {
                    "kind": "vwap_band",
                    "ticks": int(round(mean - mult * sd)),
                    "known_at_ns": at,
                    "role": "low",
                    "window": "vwap",
                    "band": float(mult),
                    "vwap_ticks": mean,
                    "vwap_sd_ticks": sd,
                }
            )
    supplied = getattr(view, "supplied", None)
    if supplied is not None:
        try:
            rows = supplied("kg1", cutoff)
        except Exception:
            rows = []
        for row in rows or []:
            low = row.get("low")
            high = row.get("high")
            known = int(row.get("known_at") or cutoff)
            if known > cutoff:
                continue
            if low is not None:
                out.append(
                    {
                        "kind": "kg1",
                        "ticks": int(round(float(low) / TICK_POINTS)),
                        "known_at_ns": known,
                        "role": "low",
                        "window": "kg1",
                    }
                )
            if high is not None:
                out.append(
                    {
                        "kind": "kg1",
                        "ticks": int(round(float(high) / TICK_POINTS)),
                        "known_at_ns": known,
                        "role": "high",
                        "window": "kg1",
                    }
                )
    for row in out:
        row["va_low"] = va_low
        row["va_high"] = va_high
    return _dedupe_locations(out)


def enumerate_contacts(arrays, loc: Mapping[str, Any], cutoff: int) -> list[dict[str, Any]]:
    """One contact per approach with a 4-tick departure. B0.1 lifecycle rule."""
    level = int(loc["ticks"])
    known = int(loc["known_at_ns"])
    trade = arrays.is_trade & (arrays.known_at_ns <= cutoff) & (arrays.t_ns >= known)
    idx = np.flatnonzero(trade)
    if idx.size == 0:
        return []
    px = arrays.price_ticks[idx].astype(np.int64)
    t = arrays.t_ns[idx]
    kn = arrays.known_at_ns[idx]
    band = CONTACT_BAND_TICKS
    dep = CONTACT_DEPARTURE_TICKS
    contacts: list[dict[str, Any]] = []
    armed = True
    for j in range(px.size):
        p = int(px[j])
        if armed:
            if abs(p - level) <= band:
                contacts.append({"at_ns": int(t[j]), "price_ticks": p, "known_at_ns": int(kn[j])})
                armed = False
                if len(contacts) >= MAX_CONTACTS_PER_LOCATION:
                    break
        elif abs(p - level) >= dep:
            armed = True
    return contacts


def _location_inside_balance(loc: Mapping[str, Any]) -> bool:
    va_low = loc.get("va_low")
    va_high = loc.get("va_high")
    if va_low is None or va_high is None:
        return False
    tick = int(loc["ticks"])
    kind = loc.get("kind")
    if kind in {"lvn", "shelf", "ledge", "minor_volume_node", "vwap_band", "kg1", "microbalance", "control_zone"}:
        return False
    return int(va_low) < tick < int(va_high)


def _structure_broke(arrays, loc: Mapping[str, Any], contact_ns: int, cutoff: int) -> bool:
    role = loc.get("role")
    level = int(loc["ticks"])
    start = int(loc["known_at_ns"])
    if contact_ns <= start:
        return False
    try:
        bars = bars_reduceat(arrays, start, int(contact_ns), 60)
    except Exception:
        return False
    for bar in bars:
        if int(bar["end_ns"]) > int(contact_ns):
            continue
        close = int(bar["close_ticks"])
        if role == "high" and close > level + STRUCTURE_BREAK_TICKS:
            return True
        if role == "low" and close < level - STRUCTURE_BREAK_TICKS:
            return True
    return False


def _sides_for(loc: Mapping[str, Any]) -> tuple[str, ...]:
    role = loc.get("role")
    if role == "low":
        return ("long",)
    return ("short",)


def _control_far(locations: list[dict[str, Any]], loc: Mapping[str, Any], side: str) -> int | None:
    far = loc.get("far_ticks")
    if far is not None:
        return int(far)
    zones = [row for row in locations if row.get("kind") == "control_zone" and int(row["known_at_ns"]) <= int(loc["known_at_ns"])]
    if not zones:
        return None
    if side == "short":
        lows = [int(z["ticks"]) for z in zones if z.get("role") == "low"]
        return min(lows) if lows else None
    highs = [int(z["ticks"]) for z in zones if z.get("role") == "high"]
    return max(highs) if highs else None


def _geometry(branch: str, side: str, features: Mapping[str, Any], loc_ticks: int, control_far: int | None) -> dict[str, Any]:
    entry = features.get("fill_ticks")
    if entry is None:
        entry = features.get("absorption_ticks")
    wick = features.get("wick_ticks") or features.get("extreme_ticks")
    stop = None
    target = None
    if entry is not None:
        if branch == "ofm_aggressive" and wick is not None:
            stop = int(wick) + OFM_STOP_TICKS_MIN if side == "short" else int(wick) - OFM_STOP_TICKS_MIN
        elif side == "short":
            stop = int(entry) + 8
        else:
            stop = int(entry) - 8
        target = ofm_40_tick_target(int(entry), side)
    return {
        "entry": entry,
        "stop": stop,
        "target": target,
        "ofm_target_40_ticks": target,
        "control_zone_far_ticks": control_far,
        "wick_ticks": wick,
        "reference_level": loc_ticks,
        "reference_px": None if loc_ticks is None else loc_ticks * TICK_POINTS,
    }


def _stop_entry_fill(arrays, loc_ticks: int, side: str, start_ns: int, cutoff: int) -> tuple[int | None, int | None]:
    trade = arrays.is_trade & (arrays.known_at_ns <= cutoff) & (arrays.t_ns >= int(start_ns))
    idx = np.flatnonzero(trade)
    for j in idx:
        px = int(arrays.price_ticks[j])
        dist = px - int(loc_ticks) if side == "long" else int(loc_ticks) - px
        if 1 <= dist <= ENTRY_NEAR_TICKS:
            return px, int(arrays.t_ns[j])
    if idx.size:
        return int(arrays.price_ticks[idx[0]]), int(arrays.t_ns[idx[0]])
    return None, None


def _branch_stages(
    branch: str,
    side: str,
    loc: Mapping[str, Any],
    features: Mapping[str, Any],
    replenish: int | None,
    reward: int | None,
    gamma_actual: str | None,
    imb_ratio: float | None,
    footprint: float | None,
    vwap_mean: float | None,
    vwap_sd: float | None,
    control_far: int | None,
    geometry: Mapping[str, Any],
    structure_break: bool,
    at_ns: int | None,
    retest: bool | None = None,
) -> list[dict[str, Any]]:
    kind = loc.get("kind")
    if _location_inside_balance(loc) and kind == "real_extreme" and loc.get("window") == "swing":
        loc_verdict = "fail"
        kind_for_ok = "inside_balance"
    else:
        kind_for_ok = kind
        loc_verdict = location_ok(None if kind is None else str(kind))
    needed = _needed_gamma(branch)
    gamma = gamma_ok(needed, gamma_actual)
    dead = structure_break
    context_operands = {
        "thesis_alive": not dead,
        "structure_break": structure_break,
        "value_shift": False,
        "new_information": None,
        "new_information_reason": NEWS_UNOBSERVABLE,
    }
    context_verdict = "fail" if dead else "pass"
    if needed:
        context_operands["gamma_regime"] = gamma_actual
        context_operands["gamma_needed"] = needed
        context_operands["gamma_reason"] = GAMMA_UNOBSERVABLE
        if gamma == "fail":
            context_verdict = "fail"
        elif gamma == "unknown":
            context_verdict = "unknown"
    rows = [_stage("context", context_verdict, at_ns, context_operands)]
    origin = features.get("origin_ticks")
    rows.append(_stage("reference", "pass" if origin is not None else "unknown", at_ns, {"origin_ticks": origin, "location_ticks": loc.get("ticks")}))
    rows.append(
        _stage(
            "location",
            loc_verdict,
            at_ns,
            {
                "location_kind": kind,
                "eligible": kind in ELIGIBLE_LOCATION_KINDS if kind else None,
                "inside_balance": kind_for_ok == "inside_balance",
                "ticks": loc.get("ticks"),
            },
        )
    )
    entry = geometry.get("entry")
    stop = geometry.get("stop")
    target = geometry.get("target")
    if branch == "clean_squeeze":
        trig = classify_clean_squeeze(features)
        rows.append(_stage("trigger", trig, features.get("extreme_ns"), {"release": features.get("release"), "pullback": features.get("pullback"), "failure": features.get("failure")}))
        conf = "pass" if features.get("opposite_absorbed") else "fail"
        rows.append(_stage("confirmation", conf, features.get("absorption_ns"), {"opposite_absorbed": features.get("opposite_absorbed")}))
    elif branch == "ofm_aggressive":
        rest = resting_stop_fill(features.get("wick_ticks"), features.get("fill_ticks"), side)
        drive = "pass" if features.get("drive_retest") else "fail"
        trig = rest if rest == "pass" else drive
        rows.append(_stage("trigger", trig, features.get("fill_ns"), {"resting_stop": rest == "pass", "drive_retest": features.get("drive_retest"), "failure": features.get("failure")}))
        rows.append(_stage("confirmation", "pass" if features.get("failure") else "fail", features.get("fill_ns"), {"squeeze_failed": features.get("failure")}))
    elif branch == "ofm_passive":
        no_aggr = features.get("aggression_size") is None
        trig = "pass" if features.get("failure") and no_aggr else "fail"
        rows.append(_stage("trigger", trig, features.get("fill_ns") or at_ns, {"failure": features.get("failure"), "no_aggression_at_failure": no_aggr}))
        rows.append(_stage("confirmation", "pass" if features.get("failure") else "fail", at_ns, {"squeeze_failed": features.get("failure")}))
    elif branch == "absorption_reward_retest":
        trig = "pass" if features.get("opposite_absorbed") else "fail"
        rows.append(
            _stage(
                "trigger",
                trig,
                at_ns,
                {"opposite_absorbed": features.get("opposite_absorbed")},
            )
        )
        rows.append(
            _stage(
                "confirmation",
                fresh_reward_retest_ok(reward, retest),
                features.get("absorption_ns") or at_ns,
                {"reward_ticks": reward, "retest": retest},
            )
        )
    elif branch in {"stop_four_stage", "dom_rejection"}:
        trig = replenishment_ok(replenish) if branch == "stop_four_stage" else ("pass" if features.get("opposite_absorbed") else "fail")
        if branch == "dom_rejection":
            trig = aggression_in_band(features.get("aggression_size"))
            if features.get("release"):
                trig = "fail"
        rows.append(_stage("trigger", trig, at_ns, {"replenishment_ticks": replenish, "aggression_size": features.get("aggression_size")}))
        rows.append(_stage("confirmation", reward_ok(reward), features.get("absorption_ns") or at_ns, {"reward_ticks": reward}))
    elif branch == "footprint_confirmed_reaction":
        flag = footprint_flag_ok(footprint)
        rows.append(_stage("trigger", flag, at_ns, {"footprint_ratio": footprint, "imbalance_ratio": imb_ratio}))
        rows.append(_stage("confirmation", "pass" if features.get("opposite_absorbed") else "fail", at_ns, {"absorption": features.get("opposite_absorbed")}))
    elif branch == "vwap_deviation_fade":
        px = features.get("fill_ticks") or features.get("extreme_ticks") or loc.get("ticks")
        beyond = None
        if vwap_mean is not None and vwap_sd not in {None, 0} and px is not None:
            beyond = abs(float(px) - float(vwap_mean)) >= float(vwap_sd)
        flag = footprint_flag_ok(footprint)
        band = vwap_band_ok(beyond, features.get("opposite_absorbed"))
        rows.append(_stage("trigger", band, at_ns, {"beyond_1_band": beyond, "bands": list(VWAP_BANDS), "footprint_flag": flag, "vwap_ticks": vwap_mean, "vwap_sd_ticks": vwap_sd}))
        rows.append(_stage("confirmation", "pass" if features.get("opposite_absorbed") else "fail", at_ns, {"absorption": features.get("opposite_absorbed")}))
    elif branch == "balance_failure_fade":
        unpaid = balance_fade_unpaid(features.get("failure"), features.get("pullback"))
        own = balance_fade_own_aggression(features.get("failure"), features.get("pullback"), features.get("own_aggression"))
        rows.append(_stage("trigger", "pass" if features.get("failure") else "fail", at_ns, {"failed_aggression": features.get("failure")}))
        rows.append(_stage("confirmation", unpaid, at_ns, {"retest": features.get("pullback"), "own_aggression": features.get("own_aggression"), "unpaid": unpaid, "own_aggression_variant": own}))
    elif branch == "kg1_retest":
        kg = "pass" if loc.get("kind") == "kg1" else "fail"
        rows.append(_stage("trigger", kg, at_ns, {"kg1": loc.get("kind") == "kg1"}))
        rows.append(_stage("confirmation", aggression_in_band(features.get("aggression_size")), at_ns, {"aggression_size": features.get("aggression_size")}))
    elif branch == "microbalance_break":
        mb = "pass" if loc.get("kind") == "microbalance" else "fail"
        rows.append(_stage("trigger", mb, at_ns, {"microbalance": loc.get("kind") == "microbalance"}))
        broke = features.get("release") is True
        rows.append(_stage("confirmation", "pass" if broke else "fail", at_ns, {"breakout": broke}))
    elif branch == "defended_band_continuation":
        rows.append(_stage("trigger", replenishment_ok(replenish), at_ns, {"replenishment_ticks": replenish}))
        rows.append(_stage("confirmation", reward_ok(reward), at_ns, {"reward_ticks": reward}))
    else:
        rows.append(_stage("trigger", "pass" if features.get("release") or features.get("fill_ns") else "unknown", at_ns, {"release": features.get("release")}))
        rows.append(_stage("confirmation", "pass" if features.get("opposite_absorbed") or features.get("fill_ns") else "unknown", at_ns, {"absorbed": features.get("opposite_absorbed")}))
    risk_operands = {"daily_r": None, "daily_stop_r": DAILY_STOP_R, "daily_r_reason": DAILY_R_UNOBSERVABLE}
    risk_verdict = "pass"
    if branch == "ofm_aggressive" and stop is not None and entry is not None:
        stop_dist = abs(int(stop) - int(entry))
        ok_stop = OFM_STOP_TICKS_MIN <= stop_dist <= OFM_STOP_TICKS_MAX
        risk_operands["stop_ticks"] = stop_dist
        if not ok_stop:
            risk_verdict = "fail"
    if branch in STOP_ENTRY_BRANCHES:
        near = entry_near_ok(entry, int(loc["ticks"]) if loc.get("ticks") is not None else None)
        risk_operands["entry_distance_ticks"] = None if entry is None or loc.get("ticks") is None else abs(int(entry) - int(loc["ticks"]))
        risk_operands["entry_near_1_2"] = near == "pass"
        risk_verdict = _and_verdicts(risk_verdict, near)
    rows.append(_stage("risk", risk_verdict, at_ns, risk_operands))
    forty = ofm_40_tick_target(entry, side)
    far_verdict = control_zone_target_ok(control_far, entry, side)
    obj_verdict = "pass" if target is not None or forty is not None else "unknown"
    if branch == "ofm_aggressive":
        obj_verdict = "pass" if forty is not None else "unknown"
        if control_far is not None:
            obj_verdict = _and_verdicts(obj_verdict, far_verdict)
    rows.append(
        _stage(
            "objective",
            obj_verdict,
            at_ns,
            {
                "target": target if target is not None else forty,
                "target_price_ticks": target if target is not None else forty,
                "ofm_target_40_ticks": OFM_TARGET_TICKS,
                "control_zone_far_ticks": control_far,
            },
        )
    )
    partial = partial_1to1_ok(entry, stop)
    trail = trail_protected_ok(
        True if features.get("release") else False,
        True if features.get("aggression_size") is not None else False,
        features.get("extreme_ticks"),
    )
    mg_verdict = _and_verdicts(partial, trail)
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
                "daily_r_reason": DAILY_R_UNOBSERVABLE,
                "partial_verdict": partial,
                "trail_verdict": trail,
            },
        )
    )
    return cascade_stages(rows)


def _values_common(branch, side, loc, features, replenish, reward, imb_ratio, gamma_actual, geo, variant=None):
    return {
        "branch": branch,
        "side": side,
        "location_kind": loc.get("kind"),
        "location_ticks": loc.get("ticks"),
        "gamma_regime": gamma_actual,
        "replenishment_ticks": replenish,
        "reward_ticks": reward,
        "three_tick_replenishment": replenish is not None and replenish >= REPLENISHMENT_MIN_TICKS,
        "aggression_size": features.get("aggression_size"),
        "aggression_in_band": features.get("aggression_size") is not None
        and AGGRESSION_MIN <= int(features["aggression_size"]) <= AGGRESSION_MAX,
        "imbalance_ratio": imb_ratio,
        "pullback": features.get("pullback"),
        "release": features.get("release"),
        "failure": features.get("failure"),
        "opposite_absorbed": features.get("opposite_absorbed"),
        "thesis_killer": None,
        "vwap_bands": list(VWAP_BANDS),
        "partial_1_to_1": partial_1to1_ok(geo.get("entry"), geo.get("stop")) == "pass",
        "trail_after_close_with_aggression": trail_protected_ok(
            features.get("release"), features.get("aggression_size") is not None, features.get("extreme_ticks")
        )
        == "pass",
        "daily_stop_r": DAILY_STOP_R,
        "target": geo.get("target"),
        "fade_variant": variant,
        "own_aggression": features.get("own_aggression"),
        "entry_variant": variant,
        "ofm_entry_variant": variant,
    }


def scan_b02(market, rec) -> dict[str, Any]:
    rec = _identity_rec(rec)
    family = rec.get("method_id") or rec.get("family") or "SIRES"
    branch = rec.get("branch") or rec.get("source_branch") or "clean_squeeze"
    view = _as_view(market)
    arrays = None if view is None else view.arrays
    empty = {
        "schema_version": "research-family-b02-scan-v1",
        "baseline_version": B02_VERSION,
        "family": family,
        "branch": branch,
        "coverage_id": rec.get("coverage_id") or f"{family}:branch:{branch}",
        "episodes": [],
        "omissions": [],
        "rules": rules_payload(),
    }
    if arrays is None or arrays.t_ns.size == 0:
        empty["omissions"] = [{"reason": "operands_unavailable", "operand": "native_executions"}]
        return empty
    cutoff = _cutoff(arrays, rec)
    cached = getattr(view, "_sires_b02_locations", None)
    if cached is not None and getattr(view, "_sires_b02_cutoff", None) == cutoff:
        locations = cached
    else:
        locations = enumerate_locations(view, cutoff)
        view._sires_b02_locations = locations
        view._sires_b02_cutoff = cutoff
    if branch == "kg1_retest":
        locations = [row for row in locations if row.get("kind") == "kg1"]
        if not locations:
            empty["omissions"] = [{"reason": "operands_unavailable", "operand": "source_kg1_level_known"}]
            return empty
    if branch == "microbalance_break":
        locations = [row for row in locations if row.get("kind") == "microbalance"]
    if branch == "vwap_deviation_fade":
        preferred = [row for row in locations if row.get("kind") == "vwap_band"]
        if preferred:
            locations = preferred
    cash = _cash_open_ns(view, arrays)
    episodes: list[dict[str, Any]] = []
    for loc in locations:
        contacts = enumerate_contacts(arrays, loc, cutoff)
        if not contacts:
            continue
        for contact in contacts:
            at_ns = int(contact["at_ns"])
            loc_ticks = int(loc["ticks"])
            gamma_actual = _gamma_from_market(market, at_ns)
            vwap_mean, vwap_sd = vwap_at(arrays, int(cash), at_ns, cutoff)
            imb_ratio = same_price_imbalance_at(arrays, loc_ticks, cutoff, end_ns=min(int(cutoff), int(at_ns) + 2 * NS))
            footprint = footprint_ratio_at(arrays, loc_ticks, cutoff, start_ns=max(0, at_ns - 60 * NS), end_ns=min(int(cutoff), int(at_ns) + 2 * NS))
            structure_break = _structure_broke(arrays, loc, at_ns, cutoff)
            for side in _sides_for(loc):
                features = path_features(arrays, cutoff, side, start_ns=at_ns, origin_ticks=loc_ticks)
                replenish = replenishment_ticks(
                    arrays,
                    loc_ticks,
                    side,
                    cutoff,
                    start_ns=int(at_ns) - 30 * NS,
                    end_ns=min(int(cutoff), int(at_ns) + 2 * NS),
                )
                origin = features.get("absorption_ticks") or loc_ticks
                start = features.get("absorption_ns") or at_ns
                reward = reward_ticks(arrays, int(origin), side, int(start), cutoff)
                retest = reward_area_retest(arrays, loc_ticks, side, int(start), cutoff)
                if branch in STOP_ENTRY_BRANCHES:
                    fill, fill_ns = _stop_entry_fill(arrays, loc_ticks, side, at_ns, cutoff)
                    if fill is not None:
                        features = dict(features)
                        features["fill_ticks"] = fill
                        features["fill_ns"] = fill_ns
                control_far = _control_far(locations, loc, side)
                geo = _geometry(branch, side, features, loc_ticks, control_far)
                variants: list[str | None]
                if branch == "ofm_aggressive":
                    variants = []
                    if features.get("failure") and features.get("fill_ticks") is not None:
                        variants.append("resting_stop")
                    if features.get("drive_retest"):
                        variants.append("drive_retest")
                    if not variants:
                        variants = [None]
                elif branch == "balance_failure_fade":
                    variants = [FADE_UNPAID, FADE_OWN_AGGRESSION]
                else:
                    variants = [None]
                for variant in variants:
                    feats = features
                    if branch == "ofm_aggressive" and variant == "drive_retest":
                        feats = dict(features)
                    st = _branch_stages(
                        branch,
                        side,
                        loc,
                        feats,
                        replenish,
                        reward,
                        gamma_actual,
                        imb_ratio,
                        footprint,
                        vwap_mean,
                        vwap_sd,
                        control_far,
                        geo,
                        structure_break,
                        at_ns=feats.get("fill_ns") or feats.get("absorption_ns") or feats.get("extreme_ns") or at_ns,
                        retest=retest,
                    )
                    if branch == "balance_failure_fade" and variant == FADE_OWN_AGGRESSION:
                        conf = next((row for row in st if row["stage"] == "confirmation"), None)
                        if conf is not None and conf.get("verdict") == "pass":
                            own = balance_fade_own_aggression(feats.get("failure"), feats.get("pullback"), feats.get("own_aggression"))
                            conf["verdict"] = own
                            conf["operands"] = {**(conf.get("operands") or {}), "own_aggression_variant": own}
                            st = cascade_stages(st)
                    verdict, failed, unknown = _combine(st)
                    if branch == "clean_squeeze":
                        squeeze = classify_clean_squeeze(feats)
                        if squeeze == "fail" and "trigger" not in failed:
                            failed.append("first_pullback" if feats.get("pullback") else "clean_squeeze")
                            verdict = "fail"
                    values = _values_common(branch, side, loc, feats, replenish, reward, imb_ratio, gamma_actual, geo, variant)
                    if structure_break:
                        values["thesis_killer"] = "structure_break"
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
                            decision_at=feats.get("fill_ns") or feats.get("absorption_ns") or feats.get("extreme_ns") or at_ns,
                            geometry=geo,
                            reference={"kind": loc.get("kind"), "ticks": loc_ticks, "role": loc.get("role")},
                            trigger={"at_ns": at_ns, "ticks": feats.get("fill_ticks") or contact.get("price_ticks")},
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


def _level_of(ep: Mapping[str, Any]) -> float | None:
    geo = ep.get("geometry") or {}
    values = ep.get("values") or {}
    ref = ep.get("reference") or {}
    for raw in (
        ref.get("ticks"),
        geo.get("reference_level"),
        values.get("location_ticks"),
        geo.get("entry"),
        geo.get("wick_ticks"),
    ):
        if raw is None:
            continue
        try:
            ticks = float(raw)
        except (TypeError, ValueError):
            continue
        if ticks > 10000:
            return ticks * TICK_POINTS
        return ticks
    if geo.get("reference_px") is not None:
        try:
            return float(geo["reference_px"])
        except (TypeError, ValueError):
            return None
    return None


def _failing_operand(ep: Mapping[str, Any]) -> dict[str, Any] | None:
    for row in ep.get("stages") or []:
        if row.get("verdict") != "pass":
            return {"stage": row.get("stage"), "verdict": row.get("verdict"), "operands": row.get("operands")}
    return None


def _date_outside_tape(example: Mapping[str, Any]) -> bool:
    from trading_research.research.rule_discovery.source_adapters.common import is_native_session

    if example.get("inside_tape") is False:
        return True
    raw = example.get("date")
    if not raw:
        return True
    try:
        day = date.fromisoformat(str(raw)[:10])
    except ValueError:
        return True
    return not is_native_session(day)


def replay_example(market, example) -> dict[str, Any]:
    example = dict(example or {})
    author_level = _author_level(example)
    author_side = _author_side(example)
    expected = example.get("expected_detection") or {}
    wanted = _branch_tokens(expected.get("branch"))
    day = example.get("date")
    empty = {
        "detected": None,
        "reached_location": False,
        "branch": None,
        "our_side": None,
        "our_level": None,
        "our_entry_ns": None,
        "author_level": author_level,
        "author_side": author_side,
        "failing_operand": None,
        "divergence": "date outside the tape",
    }
    if _date_outside_tape(example):
        return empty
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
    from trading_research.research.rule_discovery.source_adapters.common import FAMILY_BRANCHES

    hits = []
    scanned = []
    for branch in FAMILY_BRANCHES["SIRES"]:
        if wanted and not any(branch in token or token in branch for token in wanted):
            if not any(token.split()[0] == branch for token in wanted):
                continue
        doc = scan_b02(view, {"method_id": "SIRES", "branch": branch})
        scanned.append(branch)
        for ep in doc.get("episodes") or []:
            hits.append(ep)
    if not hits:
        for branch in FAMILY_BRANCHES["SIRES"]:
            if branch in scanned:
                continue
            doc = scan_b02(view, {"method_id": "SIRES", "branch": branch})
            hits.extend(doc.get("episodes") or [])
    if not hits:
        return {
            "detected": False,
            "reached_location": False,
            "branch": None,
            "our_side": None,
            "our_level": None,
            "our_entry_ns": None,
            "author_level": author_level,
            "author_side": author_side,
            "failing_operand": None,
            "divergence": "miss:no_episode",
        }

    def at_author_level(ep) -> bool:
        our = _level_of(ep)
        if author_level is None or our is None:
            return False
        return abs(our - author_level) / TICK_POINTS <= level_tolerance_ticks()

    def location_pass(ep) -> bool:
        for row in ep.get("stages") or []:
            if row.get("stage") == "location":
                return row.get("verdict") == "pass"
        return False

    reached = [ep for ep in hits if at_author_level(ep) and location_pass(ep)]
    if author_side:
        reached_side = [ep for ep in reached if ep.get("side") == author_side]
        if reached_side:
            reached = reached_side
    best = None
    reason = "miss:no_episode"
    pool = reached or hits
    for ep in pool:
        branch = ep.get("branch")
        side = ep.get("side")
        our_level = _level_of(ep)
        entry_ns = ep.get("decision_at")
        if wanted and not any(branch in token or token.split()[0] == branch for token in wanted):
            reason = "miss:branch"
            continue
        if author_side and side != author_side and "," not in str(expected.get("side") or "") and "then" not in str(expected.get("side") or "").lower():
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
    reached_location = bool(reached)
    if best is None and reached:
        best = reached[0]
        reason = "reached_location"
    if best is None:
        return {
            "detected": False,
            "reached_location": reached_location,
            "branch": hits[0].get("branch") if hits else None,
            "our_side": hits[0].get("side") if hits else None,
            "our_level": _level_of(hits[0]) if hits else None,
            "our_entry_ns": hits[0].get("decision_at") if hits else None,
            "author_level": author_level,
            "author_side": author_side,
            "failing_operand": _failing_operand(hits[0]) if hits else None,
            "divergence": reason,
        }
    detected = bool(reached_location and best.get("research_verdict") == "pass")
    fail_op = None if detected else _failing_operand(best)
    divergence = "match" if detected else (reason if reason != "miss:no_episode" else "reached_location_not_detected")
    if reached_location and not detected and fail_op:
        divergence = f"reached_location;fail:{fail_op.get('stage')}"
    return {
        "detected": detected,
        "reached_location": reached_location,
        "branch": best.get("branch"),
        "our_side": best.get("side"),
        "our_level": _level_of(best),
        "our_entry_ns": best.get("decision_at"),
        "author_level": author_level,
        "author_side": author_side,
        "failing_operand": fail_op,
        "divergence": divergence,
    }
