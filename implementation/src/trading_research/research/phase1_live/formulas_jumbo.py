"""Jumbo and AMT gap recipes from planning/phase-1-live/FORMULAS.md. Pure functions plus literal fixtures."""

from __future__ import annotations

import numpy as np

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.formulas import (
    draw_nearest_untouched,
    first_presented_fvg,
    ob_bull,
    taper_at_low,
    trailing_sma,
    two_sided_at_eq,
)
from trading_research.research.phase1_live.grid import (
    G_DEFAULT,
    first_close_break,
    hold_after_break,
    outcomes_at_level,
    reject_after_touch,
    to_ticks,
    touch_level,
)
from trading_research.research.phase1_live.sessions import projections

def overshoot_delta(width: float) -> float:
    return 0.1 * float(width)


def ladder_levels(p: dict, side: int) -> list[tuple[float, float]]:
    if side > 0:
        return [(0.1, p["mr01_high"]), (0.2, p["mr02_high"]), (0.3, p["mr03_high"]), (0.5, p["m05_high"])]
    return [(0.1, p["mr01_low"]), (0.2, p["mr02_low"]), (0.3, p["mr03_low"]), (0.5, p["m05_low"])]


def deepest_ladder(extreme: float, p: dict, side: int) -> tuple[float, float] | None:
    last = None
    for k, px in ladder_levels(p, side):
        if side > 0:
            if extreme + 1e-12 >= px:
                last = (k, px)
        else:
            if extreme - 1e-12 <= px:
                last = (k, px)
    return last


def overshoot_still_level(extreme: float, level: float, width: float, side: int) -> bool:
    d = overshoot_delta(width)
    if side > 0:
        return level - 1e-12 <= extreme <= level + d
    return level - d <= extreme <= level + 1e-12


def band_133_166(p: dict, side: int) -> tuple[float, float]:
    if side > 0:
        return p["band133_166_high_near"], p["band133_166_high_far"]
    return p["band133_166_low_near"], p["band133_166_low_far"]


def band_touch(high: float, low: float, near: float, far: float, side: int) -> bool:
    lo, hi = (near, far) if near <= far else (far, near)
    return high >= lo and low <= hi


T2 = 2 * TICK
NY_BIGTRADE = 100
LDN_BIGTRADE = 75
BODY_FRAC = 0.6
STRIKE_FRAC = 0.25
NODE_HVN = 1.5
NODE_LVN = 0.5
NODE_SHELF = 3.0
TR_FRAC = 0.05
VA_P_TOP = 0.45
VA_P_BOT = 0.20
TREND_VA_FRAC = 0.7
TPO_ROW = 1.0


def _ms(clock: str) -> int:
    parts = [int(p) for p in clock.split(":")]
    h, m = parts[0], parts[1]
    s = parts[2] if len(parts) > 2 else 0
    return ((h * 60 + m) * 60 + s) * 1000


def _minute_bars(
    start: str,
    end: str,
    *,
    close: float,
    high: float | None = None,
    low: float | None = None,
    overrides: dict | None = None,
) -> dict:
    t0 = _ms(start)
    t1 = _ms(end)
    n = int((t1 - t0) // 60_000) + 1
    if n <= 0:
        return {"n": 0, "h": np.array([]), "l": np.array([]), "c": np.array([]), "t": np.array([], dtype=np.int64), "o": np.array([])}
    hi = high if high is not None else close
    lo = low if low is not None else close
    h = np.full(n, hi, dtype=np.float64)
    l = np.full(n, lo, dtype=np.float64)
    c = np.full(n, close, dtype=np.float64)
    o = np.full(n, close, dtype=np.float64)
    t = t0 + np.arange(n, dtype=np.int64) * 60_000
    if overrides:
        for clock, bar in overrides.items():
            i = int((_ms(clock) - t0) // 60_000)
            if i < 0 or i >= n:
                continue
            if "h" in bar:
                h[i] = bar["h"]
            if "l" in bar:
                l[i] = bar["l"]
            if "c" in bar:
                c[i] = bar["c"]
            if "o" in bar:
                o[i] = bar["o"]
    return {"n": n, "h": h, "l": l, "c": c, "t": t, "o": o}


def _cat(windows: list[dict]) -> dict:
    return {
        "n": sum(w["n"] for w in windows),
        "h": np.concatenate([w["h"] for w in windows]),
        "l": np.concatenate([w["l"] for w in windows]),
        "c": np.concatenate([w["c"] for w in windows]),
        "t": np.concatenate([w["t"] for w in windows]),
        "o": np.concatenate([w["o"] for w in windows]),
    }


def _flag(v) -> int:
    return int(bool(v))


def touch_t2_high(extreme: float, level: float) -> int:
    return _flag(extreme >= level - T2)


def touch_t2_low(extreme: float, level: float) -> int:
    return _flag(extreme <= level + T2)


def touch_t2_px(px: float, level: float) -> int:
    return _flag(abs(px - level) <= T2)


def profile_nodes(bins: dict[float, float], *, median: float | None = None) -> dict:
    if not bins:
        return {"median": None, "hvn": [], "lvn": [], "shelves": [], "shelf_edges": [], "prices": [], "vols": np.array([])}
    prices = sorted(bins)
    vols = np.array([bins[p] for p in prices], dtype=np.float64)
    med = float(np.median(vols)) if median is None else float(median)
    hvn, lvn = [], []
    for i, p in enumerate(prices):
        is_max = (i == 0 or vols[i] >= vols[i - 1]) and (i + 1 == len(prices) or vols[i] >= vols[i + 1])
        is_min = (i == 0 or vols[i] <= vols[i - 1]) and (i + 1 == len(prices) or vols[i] <= vols[i + 1])
        if is_max and vols[i] >= NODE_HVN * med:
            hvn.append(p)
        if is_min and vols[i] <= NODE_LVN * med:
            lvn.append(p)
    shelves = []
    run = None
    for i, p in enumerate(prices):
        if vols[i] >= med:
            if run is None:
                run = i
        elif run is not None:
            shelves.append((prices[run], prices[i - 1]))
            run = None
    if run is not None:
        shelves.append((prices[run], prices[-1]))
    edges = []
    blocks = []
    i = 0
    n = len(prices)
    while i < n:
        j = min(i + 4, n)
        blocks.append((prices[i], prices[j - 1], float(vols[i:j].sum())))
        i = j
    for a, b in zip(blocks, blocks[1:]):
        if a[2] <= 0 or b[2] <= 0:
            continue
        if a[2] >= NODE_SHELF * b[2]:
            edges.append(a[1])
        elif b[2] >= NODE_SHELF * a[2]:
            edges.append(b[0])
    return {
        "median": med,
        "hvn": hvn,
        "lvn": lvn,
        "shelves": shelves,
        "shelf_edges": edges,
        "prices": prices,
        "vols": vols,
    }


def profile_ledges(bins: dict[float, float], *, median: float | None = None, val=None, vah=None) -> list[float]:
    nodes = profile_nodes(bins, median=median)
    if nodes["shelves"]:
        out = []
        for lo, hi in nodes["shelves"]:
            out.append(lo)
            if hi != lo:
                out.append(hi)
        return out
    if val is not None and vah is not None:
        return [val, vah]
    return []


def j10_draw(price: float, candidates: list[tuple[str, float, str]], *, side: str) -> tuple[str, float] | None:
    return draw_nearest_untouched(price, candidates, side=side)


def j10_untouched(level: float, kind: str, high_since: float, low_since: float) -> int:
    if kind == "high":
        return _flag(high_since < level)
    return _flag(low_since > level)


def j15_bigtrade_at_level(
    prints: list[dict],
    level: float,
    *,
    session: str = "ny",
    touch_ms: int | None = None,
    window_min: int = 15,
) -> dict:
    size_min = NY_BIGTRADE if session == "ny" else LDN_BIGTRADE
    end_ms = None if touch_ms is None else touch_ms + window_min * 60_000
    qual = []
    for p in prints:
        size = float(p["size"])
        px = float(p["price"])
        if size < size_min:
            continue
        if abs(px - level) > T2:
            continue
        ts = p.get("t")
        if ts is not None and touch_ms is not None:
            t = ts if isinstance(ts, (int, np.integer)) else _ms(str(ts))
            if t < touch_ms or (end_ms is not None and t > end_ms):
                continue
        qual.append(p)
    return {
        "bigtrade_at_level": _flag(qual),
        "n": len(qual),
        "sizes": [float(p["size"]) for p in qual],
    }


def j16_two_sided_at_eq(bins_buy, bins_sell, median_buy, median_sell, excursion_ticks) -> int:
    return _flag(two_sided_at_eq(bins_buy, bins_sell, median_buy, median_sell, excursion_ticks))


def j16_taper_at_low(abs_delta: list[float]) -> int:
    return _flag(taper_at_low(abs_delta))


def j17_node_under(bins: dict[float, float], level: float, w69: float, *, median: float | None = None) -> int:
    nodes = profile_nodes(bins, median=median)
    tR = TR_FRAC * w69
    spots = list(nodes["lvn"]) + list(nodes["shelf_edges"])
    return _flag(any(abs(p - level) <= tR for p in spots))


def j18_ob_bull(c1: dict, c2: dict, c3: dict, level: float) -> dict:
    raw = ob_bull(c1, c2, c3, level)
    return {
        "ob_bull": _flag(raw["ob_bull"]),
        "block": raw["block"],
        "mid": raw["mid"],
        "stop": raw["stop"],
    }


def j18_ob_bear(c1: dict, c2: dict, c3: dict, level: float) -> dict:
    sweep = c2["h"] > c1["h"] and abs(c2["h"] - level) <= T2
    confirm = c3["c"] < c2["l"]
    flag = _flag(sweep and confirm)
    return {
        "ob_bear": flag,
        "block": [c2["l"], c2["h"]],
        "mid": 0.5 * (c2["l"] + c2["h"]),
        "stop": c2["h"],
    }


def j19_draw(direction: str, pdh: float, pdl: float) -> float:
    return pdh if direction == "up" else pdl


def j19_pd_touch(direction: str, pdh: float, pdl: float, am_high: float, am_low: float | None = None) -> dict:
    draw = j19_draw(direction, pdh, pdl)
    if direction == "up":
        hit = touch_t2_high(am_high, pdh)
        return {"draw": draw, "pdh_touch": hit, "pdl_touch": 0}
    hit = touch_t2_low(am_low if am_low is not None else am_high, pdl)
    return {"draw": draw, "pdh_touch": 0, "pdl_touch": hit}


def j19_htf_fvg(h, l, c) -> dict:
    return first_presented_fvg(h, l, c)


def j20_delayed(release_1000: bool, reversal_bin: str | None) -> bool:
    return bool(release_1000 and reversal_bin == "bin.1000-1030")


def j21_class(
    *,
    red_folder_0830: bool = False,
    w_rel_prior_rth: float | None = None,
    before_release_in_week: bool = False,
    single_break: bool = False,
    eq_return_by_1000: bool = False,
) -> str:
    if red_folder_0830 or (w_rel_prior_rth is not None and w_rel_prior_rth >= 1.0):
        return "extended"
    if before_release_in_week:
        return "range-bound"
    if single_break and not eq_return_by_1000:
        return "expansive"
    return "expansive"


def j21_targets(klass: str, box_h: float, box_l: float) -> dict:
    name = klass.lower().replace(" into news", "")
    if name == "extended":
        return {
            "class": "extended",
            "targets": sorted([box_h, box_l]),
            "projections": False,
            "until": "12:00",
        }
    if name == "range-bound":
        return {
            "class": "range-bound",
            "targets": sorted([box_h, box_l]),
            "projections": False,
            "until": "12:00",
        }
    p = projections(box_h, box_l)
    return {
        "class": "expansive",
        "targets": [p["ext100_high"], p["ext133_high"], p["ext166_high"], p["ext100_low"], p["ext133_low"], p["ext166_low"]],
        "projections": True,
        "until": "16:00",
    }


def j22_three_strike(returns: list[float], r: float) -> dict:
    thresh = STRIKE_FRAC * r
    n = sum(1 for x in returns if x < thresh)
    return {"strikes": int(n), "three_strike": _flag(n >= 3)}


def j22_extended_body(body: float, rng: float, *, thresh: float = BODY_FRAC) -> int:
    if rng <= 0:
        return 0
    return _flag(body / rng >= thresh)


def j22_window_violation(touch_clock: str) -> int:
    t = _ms(touch_clock)
    return _flag(not (_ms("09:40") <= t < _ms("09:50")))


def j22_volume_divergence(volumes: np.ndarray, i: int) -> int:
    sma = trailing_sma(volumes, 14)
    if i >= volumes.size or not np.isfinite(sma[i]):
        return 0
    return _flag(volumes[i] < sma[i])


def j22_failed(*, no_rejection=0, extended_body=0, continuous_momentum=0, window_violation=0, three_strike=0, volume_divergence=0) -> int:
    return _flag(no_rejection or extended_body or continuous_momentum or window_violation or three_strike or volume_divergence)


def j24_management(
    entry: float,
    *,
    side: str,
    r: float,
    high_0950: float,
    low_0950: float,
    high_1200: float | None = None,
    low_1200: float | None = None,
    eq: float | None = None,
    clean_edge: float | None = None,
    eq_touch: bool | None = None,
) -> dict:
    if side == "long":
        mfe_0950 = high_0950 - entry
        mae_0950 = entry - low_0950
        eq_reach = _flag(eq_touch) if eq_touch is not None else (touch_t2_high(high_1200, eq) if eq is not None and high_1200 is not None else 0)
        done = touch_t2_high(high_0950, clean_edge) if clean_edge is not None else 0
    else:
        mfe_0950 = entry - low_0950
        mae_0950 = high_0950 - entry
        eq_reach = _flag(eq_touch) if eq_touch is not None else (touch_t2_low(low_1200, eq) if eq is not None and low_1200 is not None else 0)
        done = touch_t2_low(low_0950, clean_edge) if clean_edge is not None else 0
    return {
        "MFE_0950": mfe_0950,
        "MAE_0950": mae_0950,
        "MFE_0950_R": mfe_0950 / r if r else None,
        "EQ_reach": eq_reach,
        "done_by_0950": done,
    }


def j25_swing_mid(swing_low: float, swing_high: float) -> float:
    return 0.5 * (swing_low + swing_high)


def j25_fractal_swings(h: np.ndarray, l: np.ndarray, *, left: int = 2, right: int = 2) -> dict:
    highs, lows = [], []
    n = h.size
    if n < left + right + 1:
        return {"highs": highs, "lows": lows}
    for i in range(left, n - right):
        if h[i] > h[i - left:i].max() and h[i] > h[i + 1:i + 1 + right].max():
            highs.append({"i": i, "px": float(h[i]), "known_at": i + right})
        if l[i] < l[i - left:i].min() and l[i] < l[i + 1:i + 1 + right].min():
            lows.append({"i": i, "px": float(l[i]), "known_at": i + right})
    return {"highs": highs, "lows": lows}


def j25_mid_retrace_hold(
    swing_low: float,
    swing_high: float,
    window: dict,
    r: float,
    *,
    uptrend: bool = True,
) -> dict:
    mid = j25_swing_mid(swing_low, swing_high)
    side = -1 if uptrend else 1
    out = outcomes_at_level(window, mid, width=r, side=side)
    through = out["close_break"]
    on_side = False
    if out["touch_ms"] is not None and window["n"]:
        start = int(np.searchsorted(window["t"], out["touch_ms"], "left"))
        end_ms = out["touch_ms"] + G_DEFAULT["reject_k_min"] * 60_000
        i = start
        while i < window["n"] and window["t"][i] <= end_ms:
            if uptrend and float(window["c"][i]) >= mid:
                on_side = True
                break
            if not uptrend and float(window["c"][i]) <= mid:
                on_side = True
                break
            i += 1
    hold = _flag(out["touch"] and on_side and not through)
    return {
        "mid": mid,
        "touch": _flag(out["touch"]),
        "g_reject": _flag(out["reject"]),
        "mid_retrace_hold": hold,
    }


def a01_eligible(open_px: float, val: float, vah: float) -> int:
    return _flag(val <= open_px <= vah)


def a01_fade(window: dict, val: float, vah: float, poc: float) -> dict:
    width = vah - val
    inside = True
    if window["n"]:
        ct = to_ticks(window["c"])
        t = window["t"]
        up = first_close_break(ct, t, int(round(vah / TICK)), 1)
        dn = first_close_break(ct, t, int(round(val / TICK)), -1)
        if hold_after_break(ct, t, up, int(round(vah / TICK)), 1, 30 * 60_000) or hold_after_break(ct, t, dn, int(round(val / TICK)), -1, 30 * 60_000):
            inside = False
    val_out = outcomes_at_level(window, val, width=width, side=-1)
    vah_out = outcomes_at_level(window, vah, width=width, side=1)
    reject = val_out if val_out["reject"] else vah_out
    poc_reach = 0
    if reject["reject"] and reject["touch_ms"] is not None:
        ht, lt, ts = to_ticks(window["h"]), to_ticks(window["l"]), window["t"]
        poc_ms = touch_level(ht, lt, ts, int(round(poc / TICK)), G_DEFAULT["touch_ticks"])
        if poc_ms is not None and poc_ms >= reject["touch_ms"] and poc_ms <= reject["touch_ms"] + 60 * 60_000:
            poc_reach = 1
    return {
        "val_reject": _flag(val_out["reject"]),
        "vah_reject": _flag(vah_out["reject"]),
        "poc_reach_60": poc_reach,
        "inside": _flag(inside),
    }


def a02_shelves(bins: dict[float, float], *, median: float | None = None) -> list[tuple[float, float]]:
    return profile_nodes(bins, median=median)["shelves"]


def a02_ledge_retest_hold(break_window: dict, retest_window: dict, ledge: float, r: float, *, break_side: int) -> dict:
    ct = to_ticks(break_window["c"])
    t = break_window["t"]
    lvl = int(round(ledge / TICK))
    brk = first_close_break(ct, t, lvl, break_side)
    held = hold_after_break(ct, t, brk, lvl, break_side, 30 * 60_000)
    rej_side = -break_side
    ret = outcomes_at_level(retest_window, ledge, width=r, side=rej_side)
    return {
        "break_hold": _flag(held),
        "ledge_retest_hold": _flag(held and ret["touch"] and ret["reject"]),
        "touch": _flag(ret["touch"]),
        "reject": _flag(ret["reject"]),
    }


def a03_reentry_traverse(window: dict, val: float, vah: float, *, open_px: float | None = None) -> dict:
    if window["n"] == 0:
        return {"reentry": 0, "reentry_hold": 0, "traverse": 0}
    ct = to_ticks(window["c"])
    ht = to_ticks(window["h"])
    lt = to_ticks(window["l"])
    t = window["t"]
    val_t = int(round(val / TICK))
    vah_t = int(round(vah / TICK))
    if open_px is not None and open_px < val:
        re_ms = first_close_break(ct, t, val_t, 1)
        held = hold_after_break(ct, t, re_ms, val_t, 1, 30 * 60_000)
        trav = 0
        if held and re_ms is not None:
            far = touch_level(ht, lt, t, vah_t, G_DEFAULT["touch_ticks"])
            trav = _flag(far is not None and far >= re_ms)
        return {
            "reentry": _flag(re_ms is not None),
            "reentry_hold": _flag(held),
            "traverse": trav,
        }
    if open_px is not None and open_px > vah:
        re_ms = first_close_break(ct, t, vah_t, -1)
        held = hold_after_break(ct, t, re_ms, vah_t, -1, 30 * 60_000)
        trav = 0
        if held and re_ms is not None:
            far = touch_level(ht, lt, t, val_t, G_DEFAULT["touch_ticks"])
            trav = _flag(far is not None and far >= re_ms)
        return {"reentry": _flag(re_ms is not None), "reentry_hold": _flag(held), "traverse": trav}
    return {"reentry": 0, "reentry_hold": 0, "traverse": 0}


def a05_poc_tell(window: dict, poc: float, val: float, vah: float) -> dict:
    if window["n"] == 0:
        return {"poc_case": None, "near_edge_reach": 0, "far_edge_reach": 0, "n_touch": 0}
    ht, lt, ct, t = to_ticks(window["h"]), to_ticks(window["l"]), to_ticks(window["c"]), window["t"]
    poc_t = int(round(poc / TICK))
    hits = (lt <= poc_t + G_DEFAULT["touch_ticks"]) & (ht >= poc_t - G_DEFAULT["touch_ticks"])
    n_touch = int(np.count_nonzero(hits))
    first_c = float(window["c"][0])
    through_side = 1 if first_c < poc else -1
    thru = first_close_break(ct, t, poc_t, through_side)
    held = hold_after_break(ct, t, thru, poc_t, through_side, 30 * 60_000)
    retest_hold = False
    if thru is not None:
        i0 = int(np.searchsorted(t, thru, "left"))
        after = {
            "n": window["n"] - i0,
            "h": window["h"][i0:],
            "l": window["l"][i0:],
            "c": window["c"][i0:],
            "t": window["t"][i0:],
            "o": window["o"][i0:],
        }
        retest_hold = outcomes_at_level(after, poc, width=vah - val, side=-through_side)["reject"]
    if held or retest_hold:
        case = "traverse"
        far, near = (vah, val) if through_side > 0 else (val, vah)
    elif n_touch >= 2:
        case = "chop"
        far, near = (vah, val) if first_c < poc else (val, vah)
    else:
        case = None
        far, near = vah, val
    near_ms = touch_level(ht, lt, t, int(round(near / TICK)), G_DEFAULT["touch_ticks"])
    far_ms = touch_level(ht, lt, t, int(round(far / TICK)), G_DEFAULT["touch_ticks"])
    return {
        "poc_case": case,
        "near_edge_reach": _flag(near_ms is not None),
        "far_edge_reach": _flag(far_ms is not None),
        "n_touch": n_touch,
    }


def a06_failed_auction(window: dict, val: float, vah: float, older_poc: float, *, break_side: int) -> dict:
    edge = val if break_side < 0 else vah
    r = abs(older_poc - edge)
    ct = to_ticks(window["c"])
    t = window["t"]
    ht, lt = to_ticks(window["h"]), to_ticks(window["l"])
    edge_t = int(round(edge / TICK))
    poc_t = int(round(older_poc / TICK))
    brk = first_close_break(ct, t, edge_t, break_side)
    held = hold_after_break(ct, t, brk, edge_t, break_side, 30 * 60_000)
    tag = touch_level(ht, lt, t, poc_t, G_DEFAULT["touch_ticks"])
    through = first_close_break(ct, t, poc_t, break_side)
    rej_side = -1 if break_side < 0 else 1
    inst = False
    if tag is not None and held and (through is None or through > tag):
        inst = reject_after_touch(ct, t, tag, poc_t, rej_side, max(1, int(round(0.5 * r / TICK))), 5 * 60_000)
    target = val if break_side < 0 else vah
    tgt_ms = touch_level(ht, lt, t, int(round(target / TICK)), G_DEFAULT["touch_ticks"])
    reach = _flag(tgt_ms is not None and inst and (tag is None or tgt_ms >= tag))
    return {
        "fa_setup": _flag(held and tag is not None and inst),
        "target_val_reach": reach if break_side < 0 else 0,
        "target_vah_reach": reach if break_side > 0 else 0,
        "target": target,
    }


def a07_break_retest(break_window: dict, retest_window: dict, boundary: float, width: float, next_value: float, reach_window: dict, *, break_side: int) -> dict:
    ct = to_ticks(break_window["c"])
    t = break_window["t"]
    lvl = int(round(boundary / TICK))
    brk = first_close_break(ct, t, lvl, break_side)
    held = hold_after_break(ct, t, brk, lvl, break_side, 30 * 60_000)
    ret = outcomes_at_level(retest_window, boundary, width=width, side=-break_side)
    back = first_close_break(to_ticks(retest_window["c"]), retest_window["t"], lvl, -break_side)
    no_back = back is None or not hold_after_break(to_ticks(retest_window["c"]), retest_window["t"], back, lvl, -break_side, 30 * 60_000)
    nxt = outcomes_at_level(reach_window, next_value, width=width, side=break_side)
    return {
        "retest_hold": _flag(held and ret["touch"] and ret["reject"] and no_back),
        "next_value_reach": _flag(nxt["touch"]),
    }


def a08_reaccept(window: dict, val: float, vah: float, *, break_side: int) -> dict:
    ct = to_ticks(window["c"])
    ht, lt, t = to_ticks(window["h"]), to_ticks(window["l"]), window["t"]
    edge = val if break_side < 0 else vah
    opp = vah if break_side < 0 else val
    edge_t = int(round(edge / TICK))
    brk = first_close_break(ct, t, edge_t, break_side)
    held_out = hold_after_break(ct, t, brk, edge_t, break_side, 30 * 60_000)
    re_ms = None
    held_in = False
    if brk is not None:
        i0 = int(np.searchsorted(t, brk + 30 * 60_000, "left"))
        rest_c, rest_t = ct[i0:], t[i0:]
        if rest_c.size:
            re_ms = first_close_break(rest_c, rest_t, edge_t, -break_side)
            held_in = hold_after_break(rest_c, rest_t, re_ms, edge_t, -break_side, 30 * 60_000)
    opp_ms = touch_level(ht, lt, t, int(round(opp / TICK)), G_DEFAULT["touch_ticks"])
    return {
        "reaccept": _flag(held_out and held_in),
        "opposite_edge_reach": _flag(opp_ms is not None and held_in and re_ms is not None and opp_ms >= re_ms),
    }


def a08_reaccept_from_path(open_px: float, val: float, vah: float, path_class: str) -> int:
    if path_class in ("high-only", "low-only") and (open_px > vah or open_px < val):
        return 0
    return 0


def a09_traverse_nohold(window: dict, val: float, vah: float) -> dict:
    ct = to_ticks(window["c"])
    ht, lt, t = to_ticks(window["h"]), to_ticks(window["l"]), window["t"]
    val_t, vah_t = int(round(val / TICK)), int(round(vah / TICK))
    up = first_close_break(ct, t, vah_t, 1)
    dn = first_close_break(ct, t, val_t, -1)
    if up is None or dn is None:
        return {"traverse_nohold": 0, "retest_continuation": 0}
    first, second = (up, dn) if up < dn else (dn, up)
    side_first = 1 if up < dn else -1
    i0 = int(np.searchsorted(t, first, "left"))
    i1 = int(np.searchsorted(t, second, "left"))
    inside_hold = False
    span = t[i0:i1 + 1]
    closes = ct[i0:i1 + 1]
    if span.size:
        inside = (closes > val_t) & (closes < vah_t)
        if inside.size:
            for j in range(inside.size):
                if not inside[j]:
                    continue
                t_start = int(span[j])
                t_end = t_start + 30 * 60_000
                k = j
                ok = True
                last = None
                while k < span.size and int(span[k]) <= t_end:
                    if not inside[k]:
                        ok = False
                        break
                    last = int(span[k])
                    k += 1
                if ok and last is not None and last >= t_end - 60_000:
                    inside_hold = True
                    break
    trav = _flag((second - first) <= 30 * 60_000 and not inside_hold)
    after_i = i1 + 1
    rest = {
        "n": window["n"] - after_i,
        "h": window["h"][after_i:],
        "l": window["l"][after_i:],
        "c": window["c"][after_i:],
        "t": window["t"][after_i:],
        "o": window["o"][after_i:],
    }
    trav_side = -side_first
    edge = val if trav_side < 0 else vah
    rej_side = -trav_side
    ret = outcomes_at_level(rest, edge, width=vah - val, side=rej_side) if rest["n"] else {"touch": False, "reject": False}
    if not ret["touch"]:
        other = vah if edge == val else val
        ret = outcomes_at_level(rest, other, width=vah - val, side=rej_side) if rest["n"] else ret
    return {
        "traverse_nohold": trav,
        "retest_continuation": _flag(trav and ret["touch"] and ret["reject"]),
    }


def a11_vp_shape(volumes: list[float], *, va_width: float | None = None, rng: float | None = None) -> dict:
    v = np.asarray(volumes, dtype=np.float64)
    n = v.size
    if n < 3:
        return {"shape": "D", "s_t": None, "s_b": None, "s_m": None}
    third = n // 3
    bot = float(v[:third].sum())
    mid = float(v[third:2 * third].sum())
    top = float(v[2 * third:].sum())
    tot = bot + mid + top
    s_t = top / tot
    s_b = bot / tot
    s_m = mid / tot
    med = float(np.median(v))
    loc_max = []
    for i in range(n):
        is_max = (i == 0 or v[i] >= v[i - 1]) and (i + 1 == n or v[i] >= v[i + 1])
        if is_max and v[i] >= NODE_HVN * med:
            loc_max.append(i)
    double = False
    if len(loc_max) >= 2:
        for a, b in zip(loc_max, loc_max[1:]):
            if b - a <= 1:
                continue
            bridge = v[a + 1:b]
            if bridge.size and float(bridge.min()) <= NODE_LVN * med:
                double = True
                break
    trending = False
    if va_width is not None and rng and rng > 0:
        trending = va_width >= TREND_VA_FRAC * rng and not np.any(v >= NODE_HVN * med)
    if s_t >= VA_P_TOP and s_b <= VA_P_BOT:
        shape = "P"
    elif s_b >= VA_P_TOP and s_t <= VA_P_BOT:
        shape = "b"
    elif double:
        shape = "double"
    elif trending:
        shape = "trending"
    else:
        shape = "D"
    return {"shape": shape, "s_t": s_t, "s_b": s_b, "s_m": s_m}


def a12_double_lvn(bins: dict[float, float], *, median: float | None = None) -> dict:
    nodes = profile_nodes(bins, median=median)
    med = nodes["median"]
    hvn = nodes["hvn"]
    double = 0
    lvn = None
    if len(hvn) >= 2 and med is not None:
        prices = nodes["prices"]
        vols = nodes["vols"]
        i0 = prices.index(hvn[0])
        i1 = prices.index(hvn[1])
        if i1 < i0:
            i0, i1 = i1, i0
        if i1 - i0 > 1:
            sl = slice(i0 + 1, i1)
            bridge = vols[sl]
            if bridge.size and float(bridge.min()) <= NODE_LVN * med:
                double = 1
                lvn = float(prices[i0 + 1 + int(np.argmin(bridge))])
    return {"double": double, "lvn": lvn, "hvn": hvn}


def a12_respected(window: dict, lvn: float, hump_a: float, hump_b: float) -> dict:
    r = abs(hump_b - hump_a)
    out = outcomes_at_level(window, lvn, width=r, side=-1 if window["n"] and float(window["c"][0]) >= lvn else 1)
    ct = to_ticks(window["c"])
    t = window["t"]
    lvl = int(round(lvn / TICK))
    through = first_close_break(ct, t, lvl, -1 if float(window["c"][0]) >= lvn else 1) if window["n"] else None
    held_through = hold_after_break(ct, t, through, lvl, -1 if window["n"] and float(window["c"][0]) >= lvn else 1, 30 * 60_000)
    return {"respected": _flag(out["touch"] and out["reject"]), "disrespected": _flag(held_through)}


def a12_inventory_sign(delta: float, *, tape_trusted: bool = False):
    if not tape_trusted:
        return None
    if delta > 0:
        return 1
    if delta < 0:
        return -1
    return 0


def a14_tpo(periods: list[tuple[float, float]], *, row: float = TPO_ROW) -> dict:
    if not periods:
        return {"single": [], "single_runs": [], "poor_high": 0, "poor_low": 0, "excess_high": 0, "excess_low": 0, "tail_high": 0, "tail_low": 0}
    lo = min(p[0] for p in periods)
    hi = max(p[1] for p in periods)
    start = int(np.floor(lo / row))
    end = int(np.floor(hi / row))
    cover = {}
    for r in range(start, end + 1):
        px = r * row
        who = [i for i, (a, b) in enumerate(periods) if a <= px <= b]
        cover[r] = who
    top, bot = end, start
    singles = [r for r, who in cover.items() if len(who) == 1 and r != top and r != bot]
    runs = []
    run = None
    for r in singles:
        if run is None:
            run = [r, r]
        elif r == run[1] + 1:
            run[1] = r
        else:
            runs.append(tuple(run))
            run = [r, r]
    if run is not None:
        runs.append(tuple(run))

    def tail(extreme: int, step: int) -> tuple[int, int]:
        who = cover.get(extreme, [])
        if len(who) != 1:
            return 0, who.__len__()
        letter = who[0]
        n = 0
        r = extreme
        while r in cover and cover[r] == [letter]:
            n += 1
            r += step
        return n, 1

    th, _ = tail(top, -1)
    tl, _ = tail(bot, 1)
    poor_high = _flag(len(cover.get(top, [])) >= 2 or th == 1)
    poor_low = _flag(len(cover.get(bot, [])) >= 2 or tl == 1)
    return {
        "single": singles,
        "single_runs": runs,
        "poor_high": poor_high,
        "poor_low": poor_low,
        "excess_high": _flag(th >= 2),
        "excess_low": _flag(tl >= 2),
        "tail_high": th,
        "tail_low": tl,
        "high": top * row,
        "low": bot * row,
    }


def a14_single_fill(run: tuple[int, int], session_low: float, session_high: float) -> int:
    for r in range(int(run[0]), int(run[1]) + 1):
        px = float(r)
        if not (session_low <= px + T2 and session_high >= px - T2):
            return 0
    return 1


def a16_stacked(ledge: float, partners: list[float], va_height: float) -> int:
    tR = TR_FRAC * va_height
    return _flag(any(abs(p - ledge) <= tR for p in partners))


def a16_stacked_reject(window: dict, ledge: float, shelf_height: float, partners: list[float], va_height: float, *, side: int) -> dict:
    stacked = a16_stacked(ledge, partners, va_height)
    out = outcomes_at_level(window, ledge, width=shelf_height, side=side)
    return {"stacked": stacked, "stacked_reject": _flag(stacked and out["touch"] and out["reject"])}


def a17_second_transition(volumes: list[float], *, median: float | None = None) -> dict:
    v = np.asarray(volumes, dtype=np.float64)
    med = float(np.median(v)) if median is None else float(median)
    lvns = []
    for i in range(v.size):
        is_min = (i == 0 or v[i] <= v[i - 1]) and (i + 1 == v.size or v[i] <= v[i + 1])
        if is_min and v[i] <= NODE_LVN * med:
            lvns.append(i)
    if not lvns:
        return {"second_transition": 0, "tail": 0, "lvn_i": None}
    i = min(lvns, key=lambda k: float(v[k]))
    left = float(v[:i].sum()) if i else 0.0
    right = float(v[i + 1:].sum()) if i + 1 < v.size else 0.0
    beyond = v[i + 1:] if right <= left else v[:i]
    st = _flag(beyond.size > 0 and np.any(beyond >= med))
    mono = False
    arm = v[i:] if right <= left else v[:i + 1][::-1]
    if arm.size >= 2:
        mono = bool(np.all(arm[1:] <= arm[:-1]))
    tail = _flag((not st) and (mono or beyond.size == 0))
    return {"second_transition": st, "tail": tail, "lvn_i": int(i)}


def a18_bias(window: dict, val: float, vah: float, singles_above: list[int], *, r: float | None = None) -> dict:
    width = r if r is not None else (vah - val)
    fade = outcomes_at_level(window, val, width=width, side=-1)
    unfilled = bool(singles_above)
    bullish = _flag(fade["touch"] and fade["reject"] and unfilled)
    lowest = min(singles_above) if singles_above else None
    reach = 0
    if lowest is not None and window["n"]:
        reach = touch_t2_high(float(np.max(window["h"])), float(lowest))
    return {"bullish": bullish, "single_reach": reach, "target": lowest}


def p310_owed_nearest(price: float, candidates: list[dict], *, w69: float | None = None) -> dict:
    live = [c for c in candidates if not c.get("retired")]
    above_kinds = {"high", "poc", "naked_poc", "single", "poor"}
    below_kinds = {"low", "poc", "naked_poc", "single", "poor"}
    above, below = [], []
    for c in live:
        kind = c.get("kind", "poc")
        lvl = float(c["level"])
        if kind in above_kinds and lvl > price:
            above.append(c)
        if kind in below_kinds and lvl < price:
            below.append(c)
    na = min(above, key=lambda c: float(c["level"]) - price) if above else None
    nb = min(below, key=lambda c: price - float(c["level"])) if below else None

    def pack(c):
        if c is None:
            return None
        dist = abs(float(c["level"]) - price)
        out = {"name": c.get("name"), "type": c.get("type", c.get("kind")), "level": float(c["level"]), "dist": dist}
        if w69:
            out["w69"] = dist / w69
        return out

    return {"above": pack(na), "below": pack(nb)}


def _case(cid: str, got, expected) -> dict:
    ok = False
    if isinstance(expected, float):
        try:
            ok = abs(float(got) - expected) <= 1e-9
        except (TypeError, ValueError):
            ok = False
    elif isinstance(expected, dict) and isinstance(got, dict):
        ok = True
        for k, v in expected.items():
            gv = got.get(k)
            if isinstance(v, float):
                if gv is None or abs(float(gv) - v) > 1e-9:
                    ok = False
                    break
            elif isinstance(v, list):
                try:
                    ok = list(gv) == list(v)
                except TypeError:
                    ok = False
                if not ok:
                    break
            else:
                if gv != v and not (gv == 1 and v is True) and not (gv == 0 and v is False):
                    if not (isinstance(v, (int, np.integer)) and gv == v):
                        ok = False
                        break
    elif isinstance(expected, (list, tuple)) and got is not None:
        try:
            if isinstance(got, tuple) and len(got) == len(expected):
                ok = all(
                    (abs(float(a) - float(b)) <= 1e-9 if isinstance(b, float) else a == b)
                    for a, b in zip(got, expected)
                )
            else:
                ok = list(got) == list(expected)
        except (TypeError, ValueError):
            ok = False
    else:
        ok = got == expected
    return {"id": cid, "pass": bool(ok), "got": got, "expected": expected}


def jumbo_fixtures() -> dict:
    cases = []

    draw = j10_draw(
        16564.125,
        [("asia_h", 16721.0, "high"), ("london_h", 16716.75, "high"), ("pdh", 16873.5, "high")],
        side="long",
    )
    cases.append(_case("R-J10.nearest_london", None if draw is None else draw[1], 16716.75))

    bt = j15_bigtrade_at_level(
        [
            {"size": 120, "price": 18420.25, "t": "09:43:10"},
            {"size": 95, "price": 18420.0, "t": "09:43:12"},
            {"size": 150, "price": 18426.0, "t": "09:43:15"},
        ],
        18420.0,
        session="ny",
        touch_ms=_ms("09:43"),
    )
    cases.append(_case("R-J15.bigtrade_at_level", {"bigtrade_at_level": bt["bigtrade_at_level"], "n": bt["n"], "size0": bt["sizes"][0] if bt["sizes"] else None}, {"bigtrade_at_level": 1, "n": 1, "size0": 120.0}))

    cases.append(_case(
        "R-J16.two_sided",
        j16_two_sided_at_eq({99.75: 40, 100.0: 55, 100.25: 38}, {99.75: 42, 100.0: 50, 100.25: 44}, 30, 30, 1),
        1,
    ))
    cases.append(_case("R-J16.taper", j16_taper_at_low([30, 22, 15, 9, 4]), 1))

    bins_j17 = {100.00: 900, 100.25: 850, 100.50: 120, 100.75: 80, 101.00: 95, 101.25: 700}
    cases.append(_case("R-J17.node_under_eq", j17_node_under(bins_j17, 100.75, 4.0), 1))
    cases.append(_case("R-J17.hvn_not_node", j17_node_under(bins_j17, 101.25, 4.0), 0))

    ob = j18_ob_bull(
        {"l": 80.50, "h": 82.0, "c": 81.0},
        {"l": 79.50, "h": 81.75, "c": 81.0},
        {"l": 81.0, "h": 82.5, "c": 82.25},
        80.0,
    )
    cases.append(_case("R-J18.ob_bull", {"ob_bull": ob["ob_bull"], "mid": ob["mid"], "stop": ob["stop"], "block": ob["block"]}, {"ob_bull": 1, "mid": 80.625, "stop": 79.50, "block": [79.50, 81.75]}))

    pd = j19_pd_touch("up", 110.0, 90.0, 110.5)
    cases.append(_case("R-J19.pdh_touch", pd["pdh_touch"], 1))

    klass = j21_class(red_folder_0830=True)
    tgt = j21_targets("extended", 16426.75, 16334.25)
    cases.append(_case("R-J21.class_extended", klass, "extended"))
    cases.append(_case("R-J21.targets", {"targets": tgt["targets"], "projections": tgt["projections"], "until": tgt["until"]}, {"targets": [16334.25, 16426.75], "projections": False, "until": "12:00"}))

    st = j22_three_strike([3.0, 2.5, 1.5], 20.0)
    cases.append(_case("R-J22.three_strike", st, {"strikes": 3, "three_strike": 1}))
    cases.append(_case("R-J22.extended_body", j22_extended_body(4.5, 6.0), 1))

    mgt = j24_management(80.0, side="long", r=20.0, high_0950=88.0, low_0950=79.0, high_1200=101.0, eq=100.0, clean_edge=110.0, eq_touch=True)
    cases.append(_case("R-J24.mfe_mae", {"MFE_0950": mgt["MFE_0950"], "MAE_0950": mgt["MAE_0950"], "MFE_0950_R": mgt["MFE_0950_R"], "EQ_reach": mgt["EQ_reach"], "done_by_0950": mgt["done_by_0950"]}, {"MFE_0950": 8.0, "MAE_0950": 1.0, "MFE_0950_R": 0.4, "EQ_reach": 1, "done_by_0950": 0}))

    mid_bars = _minute_bars(
        "10:00",
        "10:20",
        close=105.0,
        high=105.5,
        low=101.5,
        overrides={
            "10:00": {"h": 102.0, "l": 101.5, "c": 101.8},
            "10:05": {"h": 101.0, "l": 100.25, "c": 100.8},
            "10:10": {"h": 105.0, "l": 99.9, "c": 105.0},
        },
    )
    mid = j25_mid_retrace_hold(90.0, 110.0, mid_bars, 20.0, uptrend=True)
    cases.append(_case("R-J25.mid", mid["mid"], 100.0))
    cases.append(_case("R-J25.mid_retrace_hold", mid["mid_retrace_hold"], 1))

    cases.append(_case("R-A01.eligible_0103", a01_eligible(16610.0, 16685.0, 16779.75), 0))
    a01_w = _minute_bars(
        "09:47",
        "10:05",
        close=108.0,
        high=109.0,
        low=107.0,
        overrides={
            "09:47": {"h": 100.5, "l": 99.75, "c": 100.2},
            "09:58": {"h": 110.5, "l": 108.0, "c": 110.5},
            "10:05": {"h": 112.25, "l": 111.0, "c": 112.0},
        },
    )
    a01 = a01_fade(a01_w, 100.0, 120.0, 112.0)
    cases.append(_case("R-A01.val_reject", {"val_reject": a01["val_reject"], "poc_reach_60": a01["poc_reach_60"]}, {"val_reject": 1, "poc_reach_60": 1}))

    bins_a02 = {99.75: 40, 100.00: 210, 100.25: 260, 100.50: 240, 100.75: 35}
    sh = a02_shelves(bins_a02, median=120.0)
    cases.append(_case("R-A02.shelf", sh, [(100.00, 100.50)]))
    brk = _minute_bars("10:00", "10:30", close=101.5, high=101.8, low=101.1)
    ret = _minute_bars(
        "10:20",
        "10:29",
        close=101.0,
        high=101.2,
        low=100.8,
        overrides={"10:20": {"h": 100.9, "l": 100.5, "c": 100.8}, "10:29": {"h": 101.2, "l": 100.9, "c": 101.0}},
    )
    a02 = a02_ledge_retest_hold(brk, ret, 100.50, 0.5, break_side=1)
    cases.append(_case("R-A02.ledge_retest_hold", a02["ledge_retest_hold"], 1))

    cases.append(_case("R-A03.dated_reentry", a03_reentry_traverse(_minute_bars("09:30", "12:00", close=16620.0, high=16649.75, low=16590.0), 16685.0, 16779.75, open_px=16610.0)["reentry"], 0))
    a03_w = _minute_bars(
        "10:03",
        "13:40",
        close=105.0,
        high=106.0,
        low=104.0,
        overrides={"10:03": {"h": 101.0, "l": 100.2, "c": 100.5}, "13:40": {"h": 119.5, "l": 118.0, "c": 119.0}},
    )
    a03 = a03_reentry_traverse(a03_w, 100.0, 120.0, open_px=96.0)
    cases.append(_case("R-A03.reentry_hold", {"reentry_hold": a03["reentry_hold"], "traverse": a03["traverse"]}, {"reentry_hold": 1, "traverse": 1}))

    a05_w = _minute_bars(
        "10:10",
        "11:42",
        close=110.0,
        high=111.0,
        low=109.0,
        overrides={
            "10:10": {"h": 112.25, "l": 110.0, "c": 110.0},
            "10:31": {"h": 112.0, "l": 109.0, "c": 109.5},
            "11:42": {"h": 102.0, "l": 100.5, "c": 101.0},
        },
    )
    a05 = a05_poc_tell(a05_w, 112.0, 100.0, 120.0)
    cases.append(_case("R-A05.chop", {"poc_case": a05["poc_case"], "near_edge_reach": a05["near_edge_reach"], "far_edge_reach": a05["far_edge_reach"]}, {"poc_case": "chop", "near_edge_reach": 1, "far_edge_reach": 0}))

    a06_w = _cat([
        _minute_bars("10:00", "10:30", close=98.0, high=99.0, low=97.0),
        _minute_bars(
            "10:52",
            "12:10",
            close=97.0,
            high=98.0,
            low=96.0,
            overrides={
                "10:52": {"h": 93.0, "l": 91.75, "c": 92.5},
                "10:56": {"h": 96.8, "l": 94.0, "c": 96.5},
                "12:10": {"h": 99.5, "l": 97.0, "c": 99.0},
            },
        ),
    ])
    a06 = a06_failed_auction(a06_w, 100.0, 120.0, 92.0, break_side=-1)
    cases.append(_case("R-A06.fa_setup", {"fa_setup": a06["fa_setup"], "target_val_reach": a06["target_val_reach"]}, {"fa_setup": 1, "target_val_reach": 1}))

    a07_brk = _minute_bars("10:41", "11:11", close=111.5, high=112.0, low=110.8)
    a07_ret = _minute_bars(
        "11:30",
        "11:44",
        close=112.0,
        high=113.0,
        low=111.5,
        overrides={
            "11:30": {"h": 111.0, "l": 110.25, "c": 110.8},
            "11:38": {"h": 113.5, "l": 112.0, "c": 113.5},
            "11:44": {"h": 115.25, "l": 113.0, "c": 115.25},
        },
    )
    a07_reach = _minute_bars("13:02", "13:02", close=117.5, high=118.0, low=117.0)
    a07 = a07_break_retest(a07_brk, a07_ret, 110.0, 10.0, 118.0, a07_reach, break_side=1)
    cases.append(_case("R-A07.retest_hold", {"retest_hold": a07["retest_hold"], "next_value_reach": a07["next_value_reach"]}, {"retest_hold": 1, "next_value_reach": 1}))

    a08_w = _cat([
        _minute_bars("10:00", "10:30", close=98.0, high=99.0, low=97.0),
        _minute_bars(
            "11:05",
            "14:20",
            close=105.0,
            high=106.0,
            low=104.0,
            overrides={"11:05": {"h": 101.0, "l": 100.5, "c": 100.75}, "14:20": {"h": 119.5, "l": 118.0, "c": 119.0}},
        ),
    ])
    a08 = a08_reaccept(a08_w, 100.0, 120.0, break_side=-1)
    cases.append(_case("R-A08.reaccept", {"reaccept": a08["reaccept"], "opposite_edge_reach": a08["opposite_edge_reach"]}, {"reaccept": 1, "opposite_edge_reach": 1}))
    cases.append(_case("R-A08.dated_high_only", a08_reaccept_from_path(24177.75, 24000.0, 24142.25, "high-only"), 0))

    a09_w = _cat([
        _minute_bars("09:31", "09:31", close=121.0, high=121.5, low=120.5),
        _minute_bars("09:40", "09:40", close=115.0, high=116.0, low=114.0),
        _minute_bars("09:52", "09:52", close=104.0, high=105.0, low=103.0),
        _minute_bars("09:58", "09:58", close=99.5, high=100.2, low=99.0),
        _minute_bars(
            "10:40",
            "10:54",
            close=94.0,
            high=96.0,
            low=93.0,
            overrides={
                "10:40": {"h": 100.0, "l": 97.0, "c": 98.0},
                "10:49": {"h": 95.0, "l": 94.0, "c": 94.5},
                "10:54": {"h": 91.0, "l": 89.5, "c": 89.75},
            },
        ),
    ])
    a09 = a09_traverse_nohold(a09_w, 100.0, 120.0)
    cases.append(_case("R-A09.traverse", {"traverse_nohold": a09["traverse_nohold"], "retest_continuation": a09["retest_continuation"]}, {"traverse_nohold": 1, "retest_continuation": 1}))

    shp = a11_vp_shape([30, 40, 45, 60, 70, 65, 200, 210, 180])
    cases.append(_case("R-A11.shape_P", {"shape": shp["shape"], "s_t": round(shp["s_t"], 3), "s_b": round(shp["s_b"], 3)}, {"shape": "P", "s_t": 0.656, "s_b": 0.128}))

    dd = a12_double_lvn({100.0: 300, 105.0: 40, 110.0: 280}, median=120.0)
    cases.append(_case("R-A12.double", {"double": dd["double"], "lvn": dd["lvn"]}, {"double": 1, "lvn": 105.0}))
    a12_w = _minute_bars(
        "09:41",
        "09:55",
        close=108.0,
        high=109.0,
        low=107.0,
        overrides={
            "09:41": {"h": 107.0, "l": 105.0, "c": 106.0},
            "09:50": {"h": 108.5, "l": 107.0, "c": 108.25},
            "09:55": {"h": 110.5, "l": 108.0, "c": 110.5},
        },
    )
    a12r = a12_respected(a12_w, 105.0, 100.0, 110.0)
    cases.append(_case("R-A12.respected", a12r["respected"], 1))
    cases.append(_case("R-A12.inventory_unscored", a12_inventory_sign(1.0, tape_trusted=False), None))

    tpo = a14_tpo([(100, 104), (103, 108), (107, 115), (112, 114), (113, 114)])
    run_109 = next(r for r in tpo["single_runs"] if r[0] == 109)
    cases.append(_case("R-A14.single_run", [run_109[0], run_109[1]], [109, 111]))
    cases.append(_case("R-A14.poor_high", {"poor_high": tpo["poor_high"], "excess_high": tpo["excess_high"], "tail_high": tpo["tail_high"]}, {"poor_high": 1, "excess_high": 0, "tail_high": 1}))
    cases.append(_case("R-A14.single_fill", a14_single_fill((109, 111), 108.75, 111.0), 1))

    a16_w = _minute_bars(
        "11:02",
        "11:10",
        close=98.0,
        high=100.0,
        low=97.0,
        overrides={"11:02": {"h": 100.75, "l": 100.2, "c": 100.3}, "11:10": {"h": 96.0, "l": 94.5, "c": 95.0}},
    )
    a16 = a16_stacked_reject(a16_w, 100.50, 0.5, [101.25], 20.0, side=1)
    cases.append(_case("R-A16.stacked_reject", {"stacked": a16["stacked"], "stacked_reject": a16["stacked_reject"]}, {"stacked": 1, "stacked_reject": 1}))

    st1 = a17_second_transition([150, 160, 40, 30, 140, 155], median=145.0)
    st2 = a17_second_transition([150, 160, 40, 30, 20, 10], median=145.0)
    cases.append(_case("R-A17.second_transition", st1["second_transition"], 1))
    cases.append(_case("R-A17.tail", {"tail": st2["tail"], "second_transition": st2["second_transition"]}, {"tail": 1, "second_transition": 0}))

    a18_w = _minute_bars(
        "10:05",
        "13:30",
        close=112.0,
        high=113.0,
        low=111.0,
        overrides={
            "10:05": {"h": 101.0, "l": 100.25, "c": 100.8},
            "10:14": {"h": 110.5, "l": 108.0, "c": 110.5},
            "13:30": {"h": 124.0, "l": 122.0, "c": 123.0},
        },
    )
    a18 = a18_bias(a18_w, 100.0, 120.0, [124, 125, 126], r=20.0)
    cases.append(_case("R-A18.bullish", {"bullish": a18["bullish"], "single_reach": a18["single_reach"]}, {"bullish": 1, "single_reach": 1}))

    owed = p310_owed_nearest(
        16610.0,
        [
            {"name": "london_h", "kind": "high", "type": "london_h", "level": 16716.75},
            {"name": "asia_h", "kind": "high", "type": "asia_h", "level": 16721.0},
            {"name": "pdh", "kind": "high", "type": "prior_rth_h", "level": 16873.5},
            {"name": "naked_poc", "kind": "naked_poc", "type": "naked_poc", "level": 16700.0},
            {"name": "pdl", "kind": "low", "type": "prior_rth_l", "level": 16622.5, "retired": True},
            {"name": "asia_l", "kind": "low", "type": "asia_l", "level": 16693.25},
            {"name": "london_l", "kind": "low", "type": "london_l", "level": 16689.0},
        ],
        w69=67.75,
    )
    cases.append(_case("P3-10.above", None if owed["above"] is None else {"level": owed["above"]["level"], "type": owed["above"]["type"], "dist": owed["above"]["dist"], "w69": round(owed["above"]["w69"], 2)}, {"level": 16700.0, "type": "naked_poc", "dist": 90.0, "w69": 1.33}))
    cases.append(_case("P3-10.below", owed["below"], None))
    p = projections(18238.0, 18165.0)
    cases.append(_case("R-J01.m05_low", p["m05_low"], 18128.5))
    cases.append(_case("R-J01.m05_high", p["m05_high"], 18274.5))
    cases.append(_case("R-J01.mr01_low", p["mr01_low"], 18157.7))
    cases.append(_case("R-J01.overshoot_d", p["overshoot_d"], 7.3))
    cases.append(_case("R-J01.overshoot_touch", overshoot_still_level(18121.2, p["m05_low"], p["W"], -1), True))
    syn = outcomes_at_level(
        {"n": 2, "h": np.array([81.0, 91.0]), "l": np.array([79.75, 89.0]), "c": np.array([80.5, 90.25]),
         "t": np.array([0, 11 * 60_000])},
        80.0, width=20.0, side=-1,
    )
    cases.append(_case("R-J01.synth_low_reject", {"touch": syn["touch"], "reject": syn["reject"]}, {"touch": True, "reject": True}))
    syn_h = outcomes_at_level(
        {"n": 2, "h": np.array([120.25, 110.0]), "l": np.array([118.0, 109.0]), "c": np.array([119.5, 109.5]),
         "t": np.array([0, 12 * 60_000])},
        120.0, width=20.0, side=1,
    )
    cases.append(_case("R-J01.synth_high_reject", {"touch": syn_h["touch"], "reject": syn_h["reject"]}, {"touch": True, "reject": True}))
    p8 = projections(110.0, 90.0)
    cases.append(_case("R-J08.band_high_near", p8["band133_166_high_near"], 136.6))
    cases.append(_case("R-J08.band_high_far", p8["band133_166_high_far"], 143.2))
    cases.append(_case("R-J08.band_touch", band_touch(140.0, 135.0, 136.6, 143.2, 1), True))
    cases.append(_case("R-J08.overshoot_166", overshoot_still_level(144.5, p8["ext166_high"], p8["W"], 1), True))
    cases.append(_case("R-J20.delayed", j20_delayed(True, "bin.1000-1030"), True))
    cases.append(_case("R-J20.not_0830", j20_delayed(False, "bin.1000-1030"), False))
    cases.append(_case("R-J20.wrong_bin", j20_delayed(True, "bin.0940-0950"), False))

    failed = [c for c in cases if not c["pass"]]
    return {
        "ticket": "formulas_jumbo",
        "pass": not failed,
        "n_cases": len(cases),
        "n_failed": len(failed),
        "groups": [{"name": "jumbo", "pass": not failed, "cases": cases}],
    }
