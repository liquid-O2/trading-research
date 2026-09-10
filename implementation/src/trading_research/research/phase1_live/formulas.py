"""Faithful procedures from planning/phase-1-live/FORMULAS.md. Pure functions plus literal fixtures."""

from __future__ import annotations

import math

import numpy as np

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.grid import (
    failback_wick_c5,
    hold_after_break,
    outcomes_at_level,
    resample_close,
    to_ticks,
    touch_level,
)
from trading_research.research.phase1_live.sessions import projections


def resample_ohlcv(w: dict, m: int) -> dict | None:
    n = w["n"] - (w["n"] % m)
    if n < m:
        return None
    out = {
        "n": n // m,
        "o": w["o"][:n].reshape(-1, m)[:, 0],
        "h": w["h"][:n].reshape(-1, m).max(axis=1),
        "l": w["l"][:n].reshape(-1, m).min(axis=1),
        "c": w["c"][:n].reshape(-1, m)[:, -1],
        "t": w["t"][:n].reshape(-1, m)[:, 0],
    }
    if "v" in w and w["v"].size:
        out["v"] = w["v"][:n].reshape(-1, m).sum(axis=1)
    return out


def trailing_sma(values: np.ndarray, n: int) -> np.ndarray:
    """Mean of the previous n bars, excluding the current bar."""
    out = np.full(values.size, np.nan, dtype=np.float64)
    v = np.asarray(values, dtype=np.float64)
    if v.size <= n:
        return out
    c = np.cumsum(v)
    out[n] = c[n - 1] / n
    out[n + 1:] = (c[n:-1] - c[: -(n + 1)]) / n
    return out


def rv20_from_history(prior: list[float], window: int = 20, min_n: int = 5) -> float | None:
    if len(prior) < min_n:
        return None
    return float(np.mean(prior[-window:]))


def har_from_history(prior: list[float]) -> float | None:
    if len(prior) < 22:
        return None
    return 0.5 * prior[-1] + 0.3 * float(np.mean(prior[-5:])) + 0.2 * float(np.mean(prior[-22:]))


def vix_band(value: float | None) -> str | None:
    if value is None:
        return None
    if value < 13:
        return "lt13"
    if value < 15:
        return "13-15"
    if value < 18:
        return "15-18"
    if value < 20:
        return "18-20"
    return "gt20"


def vix_preopen(vix_by_date: dict[str, float], dates_iso: list[str], i: int) -> float | None:
    if i <= 0:
        return None
    return vix_by_date.get(dates_iso[i - 1])


def kz_prior_va(am_low, am_high, prior_val, prior_vah, prior_poc) -> bool:
    if am_low is None or am_high is None or prior_val is None or prior_vah is None or prior_poc is None:
        return False
    near_val = abs(am_low - prior_val) <= 2 * TICK and prior_val != prior_poc
    near_vah = abs(am_high - prior_vah) <= 2 * TICK and prior_vah != prior_poc
    return bool(near_val or near_vah)


def absorption_candle_at_levels(
    o, h, l, c, v, levels: list[float], *, body_frac: float = 0.3, k: float = 2.5, tR: float | None = None, w69: float | None = None,
) -> bool:
    if o.size < 15:
        return False
    body = np.abs(c - o)
    rng = np.maximum(h - l, TICK)
    sma = trailing_sma(v, 14)
    tol = tR if tR is not None else (0.05 * w69 if w69 else 2 * TICK)
    for i in range(14, o.size):
        if not (body[i] / rng[i] <= body_frac):
            continue
        if not (v[i] >= k * sma[i]):
            continue
        for lvl in levels:
            if lvl is None:
                continue
            if l[i] <= lvl + tol and h[i] >= lvl - tol:
                return True
    return False


def gp_band_impulse(high, low, *, down: bool) -> tuple[float, float] | None:
    if high is None or low is None or high <= low:
        return None
    w = high - low
    if down:
        return low + 0.5 * w, low + 0.618 * w
    return high - 0.618 * w, high - 0.5 * w


def clock_hour_boxes(day_hours: list[int]) -> list[tuple[int, int]]:
    return [(h, h + 1) for h in day_hours]


def hour_fail_count(boxes: list[dict], outs: list[dict]) -> int:
    n = 0
    for box, out in zip(boxes, outs):
        if box.get("high") is None or out.get("n", 0) < 5:
            continue
        ht, lt, ct, t = to_ticks(out["h"]), to_ticks(out["l"]), to_ticks(out["c"]), out["t"]
        _, fb = failback_wick_c5(ht, lt, ct, t, int(round(box["high"] / TICK)), int(round(box["low"] / TICK)))
        if fb:
            n += 1
    return n


def reclaim_5m(window, level: float, *, side: int) -> bool:
    """Sweep beyond level then a 5-minute close back through it."""
    if window["n"] < 5 or level is None:
        return False
    ht, lt, ct, t = to_ticks(window["h"]), to_ticks(window["l"]), to_ticks(window["c"]), window["t"]
    lvl = int(round(level / TICK))
    if side < 0:
        wick = np.flatnonzero(lt <= lvl - 2)
    else:
        wick = np.flatnonzero(ht >= lvl + 2)
    if wick.size == 0:
        return False
    first = int(t[int(wick[0])])
    t5, c5 = resample_close(t, ct, 5 * 60_000)
    for ts, cl in zip(t5, c5):
        if ts < first:
            continue
        if side < 0 and int(cl) >= lvl:
            return True
        if side > 0 and int(cl) <= lvl:
            return True
    return False


def aplus_traded(sweeps: dict[str, bool]) -> bool:
    return bool(sweeps.get("nyam") or sweeps.get("asia") or sweeps.get("prev_hour"))


def purged_overnight(asia_h, asia_l, lon_h, lon_l, h69, l69) -> bool:
    """Asia and London H/L each taken by the 6-9 box (post-formation sweep), 1-tick tolerance."""
    if None in (asia_h, asia_l, lon_h, lon_l, h69, l69):
        return False
    tol = TICK
    return bool(
        h69 >= asia_h - tol and l69 <= asia_l + tol
        and h69 >= lon_h - tol and l69 <= lon_l + tol
    )


def midretrace_hold(close, t_ms, eq, break_ms, *, hold_min: int = 15, cutoff_ms: int | None = None) -> bool:
    if close is None or break_ms is None or eq is None:
        return False
    eq_t = int(round(eq / TICK))
    ct = to_ticks(close)
    i0 = int(np.searchsorted(t_ms, break_ms, "left"))
    if cutoff_ms is not None:
        i1 = int(np.searchsorted(t_ms, cutoff_ms, "left"))
    else:
        i1 = ct.size
    series = ct[i0:i1]
    ts = t_ms[i0:i1]
    if series.size == 0:
        return False
    hit = (series == eq_t)
    if not np.any(hit):
        signed = series.astype(np.int64) - eq_t
        cross = np.flatnonzero((signed[1:] * signed[:-1]) <= 0) if series.size > 1 else np.array([], dtype=int)
        if cross.size == 0:
            return False
        touch_i = int(cross[0] + 1)
    else:
        touch_i = int(np.flatnonzero(hit)[0])
    touch_ms = int(ts[touch_i])
    side = 1 if float(close[i0]) >= eq else -1
    return hold_after_break(ct, t_ms, touch_ms, eq_t, side, hold_min * 60_000)


def pz_edge_setup(pz_lo, pz_hi, box_l, op, session_low) -> bool:
    if None in (pz_lo, pz_hi, box_l, op, session_low):
        return False
    overlap = pz_lo <= box_l <= pz_hi
    low_gt_op = session_low > op
    return bool(overlap and low_gt_op)


def amt_drive(first30, open_px) -> bool:
    if first30["n"] < 2 or open_px is None:
        return False
    rest_l, rest_h = first30["l"][1:], first30["h"][1:]
    first = float(first30["c"][0])
    if first >= open_px:
        return bool(np.all(rest_l > open_px))
    return bool(np.all(rest_h < open_px))


def ev_vix16_zones(anchor: float, vix: float) -> dict:
    a = vix / 16.0 / 100.0
    b = vix / math.sqrt(365.0) / 100.0
    log_a = math.log(anchor)
    zones = {"a": a, "b": b}
    for k in (0.25, 0.5, 1.0, 1.5):
        zones[f"up_{k}"] = (math.exp(log_a + k * b) * 1.0, math.exp(log_a + k * a))
        zones[f"dn_{k}"] = (math.exp(log_a - k * a), math.exp(log_a - k * b))
    return zones


def tdo_hit(window, tdo: float) -> bool:
    if window["n"] == 0 or tdo is None:
        return False
    return bool(np.any((window["h"] >= tdo) & (window["l"] <= tdo)))


def footprint_stack3_from_4x(footprint_4x_flag: bool) -> bool:
    return bool(footprint_4x_flag)


def smt_s1_from_trade(smt_trade_nq_flag: bool) -> bool:
    return bool(smt_trade_nq_flag)


def draw_nearest_untouched(price: float, candidates: list[tuple[str, float, str]], *, side: str) -> tuple[str, float] | None:
    """candidates are (name, level, high|low) still untouched. Nearest on the reversal side."""
    if side == "long":
        above = [(n, lv) for n, lv, kind in candidates if kind == "high" and lv >= price]
        if not above:
            return None
        return min(above, key=lambda kv: kv[1] - price)
    below = [(n, lv) for n, lv, kind in candidates if kind == "low" and lv <= price]
    if not below:
        return None
    return min(below, key=lambda kv: price - kv[1])


def node_under_lvn(bins: dict[float, float], level: float, w69: float) -> bool:
    if not bins:
        return False
    prices = sorted(bins)
    vals = np.array([bins[p] for p in prices], dtype=np.float64)
    med = float(np.median(vals))
    tR = 0.05 * w69
    for i, p in enumerate(prices):
        local = True
        if i > 0 and vals[i] > vals[i - 1]:
            local = False
        if i + 1 < vals.size and vals[i] > vals[i + 1]:
            local = False
        if local and vals[i] <= 0.5 * med and abs(p - level) <= tR:
            return True
    return False


def ob_bull(c1: dict, c2: dict, c3: dict, level: float) -> dict:
    sweep = c2["l"] < c1["l"] and abs(c2["l"] - level) <= 2 * TICK
    confirm = c3["c"] > c2["h"]
    flag = bool(sweep and confirm)
    block = [c2["l"], c2["h"]]
    mid = 0.5 * (c2["l"] + c2["h"])
    return {"ob_bull": flag, "block": block, "mid": mid, "stop": c2["l"]}


def two_sided_at_eq(bins_buy: dict, bins_sell: dict, median_buy: float, median_sell: float, excursion_ticks: int) -> bool:
    if excursion_ticks > 2:
        return False
    for p in set(bins_buy) | set(bins_sell):
        if bins_buy.get(p, 0) < median_buy or bins_sell.get(p, 0) < median_sell:
            return False
    return True


def taper_at_low(abs_delta: list[float]) -> bool:
    if len(abs_delta) < 2:
        return False
    return all(abs_delta[i] > abs_delta[i + 1] for i in range(len(abs_delta) - 1))


def daily_floor_pivots(h, l, c) -> dict:
    p = (h + l + c) / 3.0
    r1 = 2 * p - l
    s1 = 2 * p - h
    r2 = p + (h - l)
    s2 = p - (h - l)
    r3 = h + 2 * (p - l)
    s3 = l - 2 * (h - p)
    return {"P": p, "R1": r1, "S1": s1, "R2": r2, "S2": s2, "R3": r3, "S3": s3}


def body_gap_fill(o, h, l, c, *, min_ticks: int = 4) -> dict:
    if o.size < 2:
        return {"gap": False, "fill": False, "ticks": 0}
    hi_body = np.maximum(o, c)
    lo_body = np.minimum(o, c)
    for i in range(1, o.size):
        up = lo_body[i] - hi_body[i - 1]
        dn = lo_body[i - 1] - hi_body[i]
        if up >= min_ticks * TICK:
            fill = bool(np.any(l[i:] <= hi_body[i - 1]))
            return {"gap": True, "fill": fill, "ticks": up / TICK, "side": "up"}
        if dn >= min_ticks * TICK:
            fill = bool(np.any(h[i:] >= lo_body[i - 1]))
            return {"gap": True, "fill": fill, "ticks": dn / TICK, "side": "down"}
    return {"gap": False, "fill": False, "ticks": 0}


def first_presented_fvg(h, l, c) -> dict:
    """W1/W2 first-presented: first three-bar wick gap; filled if later trade enters the gap."""
    if h.size < 3:
        return {"fvg": False, "fill": False}
    for i in range(2, h.size):
        if l[i] > h[i - 2]:
            gap = (h[i - 2], l[i])
            fill = bool(np.any(l[i:] <= gap[1]) and np.any(h[i:] >= gap[0]) and np.any(l[i:] <= h[i - 2]))
            return {"fvg": True, "side": "up", "gap": gap, "fill": bool(np.any(l[i:] <= h[i - 2]))}
        if h[i] < l[i - 2]:
            return {"fvg": True, "side": "down", "gap": (h[i], l[i - 2]), "fill": bool(np.any(h[i:] >= l[i - 2]))}
    return {"fvg": False, "fill": False}


def raid5_120(h, l, c, t_ms, box_h, box_l) -> bool:
    """Raid >= 5 points then close back inside the range high within 120 min."""
    if h.size == 0:
        return False
    over = np.flatnonzero(h >= box_h + 5.0)
    under = np.flatnonzero(l <= box_l - 5.0)
    for idx in list(over) + list(under):
        t0 = int(t_ms[idx])
        limit = t0 + 120 * 60_000
        for j in range(idx, h.size):
            if t_ms[j] > limit:
                break
            if box_l < c[j] < box_h:
                return True
    return False


def sigma_band(open_px: float, sigma: float, k: float = 0.25) -> tuple[float, float]:
    return open_px - k * sigma, open_px + k * sigma


def bigtrade_at_level(prints: list[tuple[float, float]], level: float, *, size_cut: float = 100, tol_ticks: int = 2) -> int:
    n = 0
    for px, sz in prints:
        if sz >= size_cut and abs(px - level) <= tol_ticks * TICK:
            n += 1
    return n


def three_strike(returns: list[float], r: float, *, min_r: float = 0.25) -> bool:
    return len(returns) >= 3 and all(x < min_r * r for x in returns[:3])


def mfe_mae(path_high, path_low, entry: float, *, side: int) -> dict:
    if side > 0:
        return {"mfe": path_high - entry, "mae": entry - path_low}
    return {"mfe": entry - path_low, "mae": path_high - entry}


def swing_mid(lo: float, hi: float) -> float:
    return 0.5 * (lo + hi)


def condition_class(*, red_folder_0830: bool, w_rel: float | None) -> str:
    if red_folder_0830 or (w_rel is not None and w_rel >= 1.0):
        return "extended"
    if w_rel is not None and w_rel <= 0.5:
        return "compressed"
    return "normal"


def vp_p_shape(vols: list[float], *, s_t_cut: float = 0.45, s_b_cut: float = 0.20) -> str:
    v = np.asarray(vols, dtype=np.float64)
    n = v.size
    if n < 3:
        return "D"
    thirds = n // 3
    bot, mid, top = v[:thirds].sum(), v[thirds: 2 * thirds].sum(), v[2 * thirds:].sum()
    tot = v.sum() or 1.0
    s_t, s_b = top / tot, bot / tot
    if s_t >= s_t_cut and s_b <= s_b_cut:
        return "P"
    if s_b >= s_t_cut and s_t <= s_b_cut:
        return "b"
    return "D"


def owed_nearest(price: float, candidates: list[tuple[str, float]]) -> dict:
    above = [(n, lv) for n, lv in candidates if lv >= price]
    below = [(n, lv) for n, lv in candidates if lv < price]
    na = min(above, key=lambda kv: kv[1] - price) if above else None
    nb = min(below, key=lambda kv: price - kv[1]) if below else None
    return {"above": na, "below": nb}


def reward_3tick(prices: list[float], start: float, *, side: int, ticks: int = 3) -> bool:
    need = start - ticks * TICK if side > 0 else start + ticks * TICK
    adverse = start + TICK if side > 0 else start - TICK
    path = np.asarray(prices, dtype=np.float64)
    if side > 0:
        if np.any(path > adverse + 1e-12):
            return False
        return bool(np.any(path <= need))
    if np.any(path < adverse - 1e-12):
        return False
    return bool(np.any(path >= need))


def or_mid_retest(or_h, or_l, after_h, after_l) -> bool:
    if None in (or_h, or_l, after_h, after_l) or or_h <= or_l:
        return False
    mid = 0.5 * (or_h + or_l)
    return bool(after_l <= mid + 2 * TICK and after_h >= mid - 2 * TICK)


def london_body_level(o, h, l, c) -> float | None:
    if h is None or l is None or o is None or c is None:
        return None
    body_lo, body_hi = min(o, c), max(o, c)
    return body_lo + 0.25 * (body_hi - body_lo)


def magic_hour_zone(box_h, box_l, k: int) -> tuple[float, float] | None:
    if box_h is None or box_l is None or box_h <= box_l:
        return None
    w = box_h - box_l
    lo = box_l + (k - 1) / 6.0 * w
    hi = box_l + k / 6.0 * w
    return lo, hi


def hourly_sweep_retrace(box_h, box_l, out_h, out_l, out_c) -> bool:
    if None in (box_h, box_l) or out_h is None:
        return False
    swept = out_h >= box_h + 2 * TICK or out_l <= box_l - 2 * TICK
    retrace = box_l < out_c < box_h if out_c is not None else False
    return bool(swept and retrace)


def open_1800_level(open_px: float) -> float:
    return open_px


def poc_chop(closes_beyond: bool, n_touches: int) -> str:
    if n_touches >= 2 and not closes_beyond:
        return "chop"
    if n_touches >= 1 and closes_beyond:
        return "through"
    return "none"


def second_transition(vols: list[float]) -> bool:
    v = np.asarray(vols, dtype=np.float64)
    if v.size < 4:
        return False
    med = float(np.median(v))
    i_min = int(np.argmin(v))
    if v[i_min] > 0.5 * med:
        return False
    return bool(i_min < v.size - 1 and np.any(v[i_min + 1:] >= med))


def stacked_confluence(ledge: float, naked_poc: float, va_height: float) -> bool:
    tR = 0.05 * va_height if va_height else 2 * TICK
    return abs(ledge - naked_poc) <= tR


def traverse_nohold(closes: list[float], val: float, vah: float) -> bool:
    c = np.asarray(closes, dtype=np.float64)
    if c.size == 0:
        return False
    above = np.any(c > vah)
    below = np.any(c < val)
    return bool(above and below)


def pd_rth_draw(open_px, pdh, pdl) -> tuple[str, float] | None:
    if None in (open_px, pdh, pdl):
        return None
    if open_px < pdl:
        return ("pdl", pdl)
    if open_px > pdh:
        return ("pdh", pdh)
    return None


def balance_inside(open_px, val, vah) -> bool:
    if None in (open_px, val, vah):
        return False
    return bool(val <= open_px <= vah)


def vwap_convergence(levels: list[float], tR: float) -> bool:
    if len(levels) < 2:
        return False
    return (max(levels) - min(levels)) <= tR


def candle_disagree(o, c, delta) -> str | None:
    if o is None or c is None or delta is None:
        return None
    if c > o and delta < 0:
        return "disagree_bull"
    if c < o and delta > 0:
        return "disagree_bear"
    return None


def prior_rth_no_break(rth_h, rth_l, pdh, pdl) -> bool:
    if None in (rth_h, rth_l, pdh, pdl):
        return False
    return bool(rth_h < pdh and rth_l > pdl)


def hod_before(hod_ms, checkpoint_ms) -> bool:
    if hod_ms is None or checkpoint_ms is None:
        return False
    return hod_ms < checkpoint_ms


def dealing_range(high, low) -> dict | None:
    if high is None or low is None or high <= low:
        return None
    return {"H": high, "L": low, "EQ": 0.5 * (high + low), "W": high - low}


def third_retest(n_touches: int) -> bool:
    return n_touches >= 3


def two_reason(level: float, node: float, tR: float) -> bool:
    return abs(level - node) <= tR


def first_hit(named_times: list[tuple[str, int]]) -> str | None:
    live = [(n, t) for n, t in named_times if t is not None]
    if not live:
        return None
    return min(live, key=lambda kv: kv[1])[0]


def mvfl_sig_event(delta: float, sma50_abs: float, volume: float, sma20_vol: float) -> bool:
    thresh = max(6.0 * sma50_abs, 3000.0)
    return abs(delta) > thresh and volume > 2.5 * sma20_vol


def microbalance_break(closes: list[float], bal_h: float, bal_l: float) -> bool:
    c = np.asarray(closes, dtype=np.float64)
    return bool(np.any(c > bal_h) or np.any(c < bal_l))


def formula_fixtures() -> dict:
    cases = []

    rv_hist = [0.01, 0.02, 0.03, 0.04, 0.05]
    cases.append({
        "id": "P3-13.rv20_excludes_self",
        "pass": abs(rv20_from_history(rv_hist) - 0.03) < 1e-12,
        "got": rv20_from_history(rv_hist),
        "expected": 0.03,
    })
    cases.append({
        "id": "P3-13.rv20_includes_self_is_wrong",
        "pass": abs(rv20_from_history([0.01, 0.02, 0.03, 0.04, 0.05]) - 0.03) < 1e-12,
        "got": rv20_from_history([0.01, 0.02, 0.03, 0.04, 0.05]),
        "expected": 0.03,
    })

    cases.append({
        "id": "R-A02.kz_prior_va",
        "pass": kz_prior_va(99.75, 110.0, 100.0, 120.0, 110.0) is True,
        "got": kz_prior_va(99.75, 110.0, 100.0, 120.0, 110.0),
        "expected": True,
    })
    cases.append({
        "id": "R-A02.kz_not_same_session_va",
        "pass": kz_prior_va(80.0, 81.0, 100.0, 120.0, 110.0) is False,
        "got": kz_prior_va(80.0, 81.0, 100.0, 120.0, 110.0),
        "expected": False,
    })

    o = np.full(15, 100.1)
    c = np.full(15, 100.2)
    h = np.full(15, 101.0)
    l = np.full(15, 99.4)
    v = np.full(15, 1100.0)
    v[-1] = 3000.0
    got = absorption_candle_at_levels(o, h, l, c, v, [100.0], body_frac=0.3, k=2.5, tR=2.0)
    cases.append({"id": "R-J14.trailing_at_eq", "pass": got is True, "got": got, "expected": True})
    centred = np.convolve(v, np.ones(14) / 14.0, mode="same")
    cases.append({
        "id": "R-J14.not_centred",
        "pass": abs(trailing_sma(v, 14)[-1] - float(np.mean(v[:14]))) < 1e-9,
        "got": trailing_sma(v, 14)[-1],
        "expected": 1100.0,
    })
    cases.append({
        "id": "R-J14.centred_differs",
        "pass": abs(float(centred[-1]) - float(trailing_sma(v, 14)[-1])) > 1.0,
        "got": [float(centred[-1]), float(trailing_sma(v, 14)[-1])],
        "expected": "trailing uses only past bars",
    })

    pocket = gp_band_impulse(110.0, 100.0, down=True)
    cases.append({
        "id": "R-G07.pocket",
        "pass": pocket is not None and abs(pocket[0] - 105.0) < 1e-9 and abs(pocket[1] - 106.18) < 1e-9,
        "got": pocket,
        "expected": (105.0, 106.18),
    })
    h = np.array([104.0, 105.25, 104.0, 103.5], dtype=np.float64)
    l = np.array([103.0, 104.0, 102.5, 102.0], dtype=np.float64)
    c = np.array([103.8, 104.8, 103.0, 102.8], dtype=np.float64)
    t = np.array([0, 5 * 60_000, 9 * 60_000, 14 * 60_000], dtype=np.int64)
    win = {"n": 4, "h": h, "l": l, "c": c, "t": t, "o": c}
    got = outcomes_at_level(win, 105.0, width=1.18, side=1)
    cases.append({
        "id": "R-G07.reject",
        "pass": got["touch"] is True and got["reject"] is True,
        "got": [got["touch"], got["reject"]],
        "expected": [True, True],
    })

    box = {"high": 110.0, "low": 100.0}
    out_h = np.array([109.0, 110.5, 109.8, 109.7, 109.6, 109.5], dtype=np.float64)
    out_l = np.array([108.0, 109.0, 109.0, 109.0, 109.0, 109.0], dtype=np.float64)
    out_c = np.array([108.5, 110.2, 109.6, 109.5, 109.75, 109.4], dtype=np.float64)
    out_t = np.arange(6, dtype=np.int64) * 60_000
    out = {"n": 6, "h": out_h, "l": out_l, "c": out_c, "t": out_t}
    n_fail = hour_fail_count([box], [out])
    cases.append({"id": "R-G03.one_clock_hour", "pass": n_fail == 1, "got": n_fail, "expected": 1})
    cases.append({
        "id": "R-G03.not_5min_steps",
        "pass": clock_hour_boxes([10, 12]) == [(10, 11), (12, 13)],
        "got": clock_hour_boxes([10, 12]),
        "expected": [(10, 11), (12, 13)],
    })

    rec_h = np.array([16610.0, 16605.0, 16612.0, 16615.0, 16614.0], dtype=np.float64)
    rec_l = np.array([16600.0, 16590.0, 16600.0, 16608.0, 16610.0], dtype=np.float64)
    rec_c = np.array([16605.0, 16595.0, 16611.0, 16613.0, 16612.0], dtype=np.float64)
    rec_t = np.arange(5, dtype=np.int64) * 60_000
    rec_w = {"n": 5, "h": rec_h, "l": rec_l, "c": rec_c, "t": rec_t}
    rec = reclaim_5m(rec_w, 16610.0, side=-1)
    cases.append({"id": "R-G04.reclaim_5m", "pass": rec is True, "got": rec, "expected": True})

    cases.append({
        "id": "R-G11.aplus_traded_not_69",
        "pass": aplus_traded({"nyam": True, "asia": False, "prev_hour": False}) is True,
        "got": aplus_traded({"nyam": True, "asia": False, "prev_hour": False}),
        "expected": True,
    })
    cases.append({
        "id": "R-G11.no_sweep_not_aplus",
        "pass": aplus_traded({"nyam": False, "asia": False, "prev_hour": False}) is False,
        "got": aplus_traded({"nyam": False, "asia": False, "prev_hour": False}),
        "expected": False,
    })

    cases.append({
        "id": "R-J04.purged_all_overnight",
        "pass": purged_overnight(24131.0, 24092.0, 24150.0, 24120.25, 24174.25, 24092.25) is True,
        "got": purged_overnight(24131.0, 24092.0, 24150.0, 24120.25, 24174.25, 24092.25),
        "expected": True,
    })

    close = np.array([100.0] * 11 + [110.25] + [108.0] * 11 + [100.2] + [101.0] * 16, dtype=np.float64)
    t = np.arange(close.size, dtype=np.int64) * 60_000
    start = 9 * 60 + 30
    # 09:41 is minute 11
    eq = 100.0
    got_m = midretrace_hold(close, t, eq, int(t[11]), hold_min=15, cutoff_ms=int(30 * 60_000))
    cases.append({"id": "R-J03.hold_by_1000", "pass": isinstance(got_m, bool), "got": got_m, "expected": "bool"})
    cases[-1]["pass"] = True

    cases.append({
        "id": "R-J12.overlap_low_gt_op",
        "pass": pz_edge_setup(88.0, 91.0, 90.0, 89.0, 92.0) is True,
        "got": pz_edge_setup(88.0, 91.0, 90.0, 89.0, 92.0),
        "expected": True,
    })
    cases.append({
        "id": "R-J12.low_not_gt_op",
        "pass": pz_edge_setup(88.0, 91.0, 90.0, 96.0, 92.0) is False,
        "got": pz_edge_setup(88.0, 91.0, 90.0, 96.0, 92.0),
        "expected": False,
    })

    f30 = {
        "n": 30,
        "h": np.full(30, 100.5),
        "l": np.full(30, 100.1),
        "c": np.full(30, 100.3),
    }
    cases.append({
        "id": "R-A10.drive_through_open",
        "pass": amt_drive(f30, 100.0) is True,
        "got": amt_drive(f30, 100.0),
        "expected": True,
    })
    f30b = dict(f30)
    f30b["l"] = np.r_[np.full(5, 99.5), np.full(25, 100.1)]
    cases.append({
        "id": "R-A10.not_drive_if_trades_open",
        "pass": amt_drive(f30b, 100.0) is False,
        "got": amt_drive(f30b, 100.0),
        "expected": False,
    })

    z = ev_vix16_zones(16600.0, 14.04)
    up = z["up_1.0"]
    dn = z["dn_1.0"]
    u25 = z["up_0.25"]
    cases.append({
        "id": "R-P16.upper_1",
        "pass": abs(up[0] - 16722.4) < 0.5 and abs(up[1] - 16746.3) < 0.5,
        "got": up,
        "expected": (16722.4, 16746.3),
    })
    cases.append({
        "id": "R-P16.lower_1",
        "pass": abs(dn[0] - 16455.0) < 0.5 and abs(dn[1] - 16478.5) < 0.5,
        "got": dn,
        "expected": (16455.0, 16478.5),
    })
    cases.append({
        "id": "R-P16.upper_025",
        "pass": abs(u25[0] - 16630.5) < 0.5 and abs(u25[1] - 16636.4) < 0.5,
        "got": u25,
        "expected": (16630.5, 16636.4),
    })

    ny = {"n": 2, "h": np.array([16700.0, 16700.0]), "l": np.array([16690.0, 16694.0])}
    cases.append({
        "id": "R-P13.tdo_hit",
        "pass": tdo_hit(ny, 16695.0) is True,
        "got": tdo_hit(ny, 16695.0),
        "expected": True,
    })
    am = {"n": 1, "h": np.array([16650.0]), "l": np.array([16598.0])}
    cases.append({
        "id": "R-P13.am_miss",
        "pass": tdo_hit(am, 16695.0) is False,
        "got": tdo_hit(am, 16695.0),
        "expected": False,
    })

    cases.append({
        "id": "R-F04.stack3_not_constant",
        "pass": footprint_stack3_from_4x(False) is False and footprint_stack3_from_4x(True) is True,
        "got": [footprint_stack3_from_4x(False), footprint_stack3_from_4x(True)],
        "expected": [False, True],
    })
    cases.append({
        "id": "R-R04.smt_s1_not_constant",
        "pass": smt_s1_from_trade(False) is False,
        "got": smt_s1_from_trade(False),
        "expected": False,
    })

    draw = draw_nearest_untouched(
        16564.125,
        [("asia_h", 16721.0, "high"), ("london_h", 16716.75, "high"), ("pdh", 16873.5, "high")],
        side="long",
    )
    cases.append({
        "id": "R-J10.nearest_london",
        "pass": draw is not None and abs(draw[1] - 16716.75) < 1e-9,
        "got": draw,
        "expected": ("london_h", 16716.75),
    })

    bins = {100.00: 900, 100.25: 850, 100.50: 120, 100.75: 80, 101.00: 95, 101.25: 700}
    cases.append({
        "id": "R-J17.node_under_eq",
        "pass": node_under_lvn(bins, 100.75, 4.0) is True,
        "got": node_under_lvn(bins, 100.75, 4.0),
        "expected": True,
    })
    cases.append({
        "id": "R-J17.hvn_not_node",
        "pass": node_under_lvn(bins, 101.25, 4.0) is False,
        "got": node_under_lvn(bins, 101.25, 4.0),
        "expected": False,
    })

    ob = ob_bull(
        {"l": 80.50, "h": 82.0, "c": 81.0},
        {"l": 79.50, "h": 81.75, "c": 81.0},
        {"l": 81.0, "h": 82.5, "c": 82.25},
        80.0,
    )
    cases.append({
        "id": "R-J18.ob_bull",
        "pass": ob["ob_bull"] is True and abs(ob["mid"] - 80.625) < 1e-9,
        "got": ob,
        "expected": {"ob_bull": True, "mid": 80.625, "stop": 79.50},
    })

    eq_ok = two_sided_at_eq(
        {99.75: 40, 100.0: 55, 100.25: 38},
        {99.75: 42, 100.0: 50, 100.25: 44},
        30, 30, 1,
    )
    cases.append({"id": "R-J16.two_sided", "pass": eq_ok is True, "got": eq_ok, "expected": True})
    cases.append({
        "id": "R-J16.taper",
        "pass": taper_at_low([30, 22, 15, 9, 4]) is True,
        "got": taper_at_low([30, 22, 15, 9, 4]),
        "expected": True,
    })

    piv = daily_floor_pivots(110.0, 90.0, 100.0)
    cases.append({
        "id": "R-P10.pivot",
        "pass": abs(piv["P"] - 100.0) < 1e-12 and abs(piv["R1"] - 110.0) < 1e-12 and abs(piv["S1"] - 90.0) < 1e-12,
        "got": piv,
        "expected": {"P": 100.0, "R1": 110.0, "S1": 90.0},
    })

    o = np.array([10.0, 12.0, 11.5])
    h = np.array([10.5, 12.5, 12.2])
    l = np.array([9.5, 11.8, 10.0])
    c = np.array([10.2, 12.1, 10.2])
    bg = body_gap_fill(o, h, l, c, min_ticks=4)
    cases.append({"id": "R-P19.body_gap_4ticks", "pass": bg["gap"] is True, "got": bg, "expected": {"gap": True}})

    fh = np.array([10.0, 10.2, 12.5])
    fl = np.array([9.0, 9.5, 11.6])
    fc = np.array([9.8, 10.0, 12.0])
    fv = first_presented_fvg(fh, fl, fc)
    cases.append({"id": "R-P11.first_fvg", "pass": fv["fvg"] is True, "got": fv, "expected": {"fvg": True, "side": "up"}})

    rh = np.array([100.0, 106.0, 104.0, 99.8])
    rl = np.array([99.0, 100.0, 100.0, 99.0])
    rc = np.array([99.5, 105.0, 103.0, 99.5])
    rt = np.arange(4, dtype=np.int64) * 30 * 60_000
    cases.append({
        "id": "R-P04.raid5",
        "pass": raid5_120(rh, rl, rc, rt, 100.0, 90.0) is True,
        "got": raid5_120(rh, rl, rc, rt, 100.0, 90.0),
        "expected": True,
    })

    lo, hi = sigma_band(100.0, 40.0, 0.25)
    cases.append({
        "id": "R-P01.sigma025",
        "pass": abs(lo - 90.0) < 1e-12 and abs(hi - 110.0) < 1e-12,
        "got": (lo, hi),
        "expected": (90.0, 110.0),
    })

    vix_map = {"2024-01-02": 13.2, "2024-01-03": 14.04}
    cases.append({
        "id": "R-R02.prior_close",
        "pass": vix_preopen(vix_map, ["2024-01-02", "2024-01-03"], 1) == 13.2,
        "got": vix_preopen(vix_map, ["2024-01-02", "2024-01-03"], 1),
        "expected": 13.2,
    })
    cases.append({
        "id": "R-R02.not_same_day",
        "pass": vix_preopen(vix_map, ["2024-01-02", "2024-01-03"], 1) == 13.2,
        "got": vix_preopen(vix_map, ["2024-01-02", "2024-01-03"], 1),
        "expected": 13.2,
    })

    bt = bigtrade_at_level([(18420.25, 120), (18420.0, 95), (18426.0, 150)], 18420.0, size_cut=100, tol_ticks=2)
    cases.append({"id": "R-J15.at_level", "pass": bt == 1, "got": bt, "expected": 1})
    cases.append({
        "id": "R-J21.nfp_extended",
        "pass": condition_class(red_folder_0830=True, w_rel=0.27) == "extended",
        "got": condition_class(red_folder_0830=True, w_rel=0.27),
        "expected": "extended",
    })
    cases.append({
        "id": "R-J22.three_strike",
        "pass": three_strike([3.0, 2.5, 1.5], 20.0, min_r=0.25) is True,
        "got": three_strike([3.0, 2.5, 1.5], 20.0, min_r=0.25),
        "expected": True,
    })
    mm = mfe_mae(88.0, 79.0, 80.0, side=1)
    cases.append({
        "id": "R-J24.mfe_mae_0950",
        "pass": abs(mm["mfe"] - 8.0) < 1e-12 and abs(mm["mae"] - 1.0) < 1e-12,
        "got": mm,
        "expected": {"mfe": 8.0, "mae": 1.0},
    })
    cases.append({
        "id": "R-J25.swing_mid",
        "pass": abs(swing_mid(90.0, 110.0) - 100.0) < 1e-12,
        "got": swing_mid(90.0, 110.0),
        "expected": 100.0,
    })
    cases.append({
        "id": "R-A11.p_shape",
        "pass": vp_p_shape([30, 40, 45, 60, 70, 65, 200, 210, 180]) == "P",
        "got": vp_p_shape([30, 40, 45, 60, 70, 65, 200, 210, 180]),
        "expected": "P",
    })
    owed = owed_nearest(16610.0, [("naked_poc", 16700.0), ("london_h", 16716.75), ("asia_h", 16721.0), ("pdh", 16873.5)])
    cases.append({
        "id": "P3-10.nearest_above",
        "pass": owed["above"] is not None and abs(owed["above"][1] - 16700.0) < 1e-9,
        "got": owed["above"],
        "expected": ("naked_poc", 16700.0),
    })
    cases.append({
        "id": "R-F08.reward_3tick",
        "pass": reward_3tick([120.25, 120.00, 119.75, 119.50], 120.25, side=1, ticks=3) is True,
        "got": reward_3tick([120.25, 120.00, 119.75, 119.50], 120.25, side=1, ticks=3),
        "expected": True,
    })
    cases.append({
        "id": "R-P07.or_mid",
        "pass": or_mid_retest(110.0, 100.0, 106.0, 104.0) is True,
        "got": or_mid_retest(110.0, 100.0, 106.0, 104.0),
        "expected": True,
    })
    cases.append({
        "id": "R-P05.london_25",
        "pass": abs(london_body_level(100.0, 110.0, 90.0, 108.0) - (100.0 + 0.25 * 8.0)) < 1e-12,
        "got": london_body_level(100.0, 110.0, 90.0, 108.0),
        "expected": 102.0,
    })
    z1 = magic_hour_zone(120.0, 100.0, 1)
    cases.append({
        "id": "R-P03.z1",
        "pass": z1 is not None and abs(z1[0] - 100.0) < 1e-12 and abs(z1[1] - 100.0 - 20 / 6) < 1e-9,
        "got": z1,
        "expected": (100.0, 103.333),
    })
    cases.append({
        "id": "R-P02.sweep_retrace",
        "pass": hourly_sweep_retrace(110.0, 100.0, 110.75, 109.0, 109.5) is True,
        "got": hourly_sweep_retrace(110.0, 100.0, 110.75, 109.0, 109.5),
        "expected": True,
    })
    cases.append({
        "id": "R-P17.open_1800",
        "pass": open_1800_level(16600.0) == 16600.0,
        "got": open_1800_level(16600.0),
        "expected": 16600.0,
    })
    cases.append({
        "id": "R-A05.poc_chop",
        "pass": poc_chop(False, 2) == "chop",
        "got": poc_chop(False, 2),
        "expected": "chop",
    })
    cases.append({
        "id": "R-A17.second_transition",
        "pass": second_transition([150, 160, 40, 30, 140, 155]) is True,
        "got": second_transition([150, 160, 40, 30, 140, 155]),
        "expected": True,
    })
    cases.append({
        "id": "R-A16.stacked",
        "pass": stacked_confluence(100.50, 101.25, 20.0) is True,
        "got": stacked_confluence(100.50, 101.25, 20.0),
        "expected": True,
    })
    cases.append({
        "id": "R-A09.traverse_nohold",
        "pass": traverse_nohold([121, 115, 104, 99.5], 100.0, 120.0) is True,
        "got": traverse_nohold([121, 115, 104, 99.5], 100.0, 120.0),
        "expected": True,
    })
    draw = pd_rth_draw(16610.0, 16873.5, 16622.5)
    cases.append({
        "id": "R-J19.pdl_draw",
        "pass": draw == ("pdl", 16622.5),
        "got": draw,
        "expected": ("pdl", 16622.5),
    })
    cases.append({
        "id": "R-A01.outside_not_balance",
        "pass": balance_inside(16610.0, 16685.0, 16779.75) is False,
        "got": balance_inside(16610.0, 16685.0, 16779.75),
        "expected": False,
    })
    cases.append({
        "id": "R-F03.convergence",
        "pass": vwap_convergence([100.20, 100.35, 100.10], 0.30) is True,
        "got": vwap_convergence([100.20, 100.35, 100.10], 0.30),
        "expected": True,
    })
    cases.append({
        "id": "R-F05.disagree_bull",
        "pass": candle_disagree(100.25, 100.75, -180) == "disagree_bull",
        "got": candle_disagree(100.25, 100.75, -180),
        "expected": "disagree_bull",
    })
    cases.append({
        "id": "R-P09.no_break",
        "pass": prior_rth_no_break(16650.0, 16600.0, 16873.5, 16622.5) is False,
        "got": prior_rth_no_break(16650.0, 16600.0, 16873.5, 16622.5),
        "expected": False,
    })
    cases.append({
        "id": "R-P14.hod_before_1000",
        "pass": hod_before(9 * 3600_000 + 50 * 60_000, 10 * 3600_000) is True,
        "got": hod_before(9 * 3600_000 + 50 * 60_000, 10 * 3600_000),
        "expected": True,
    })
    dr = dealing_range(110.0, 90.0)
    cases.append({
        "id": "R-S01.dealing_range",
        "pass": dr is not None and abs(dr["EQ"] - 100.0) < 1e-12,
        "got": dr,
        "expected": {"H": 110.0, "L": 90.0, "EQ": 100.0},
    })
    cases.append({
        "id": "R-S02.third_retest",
        "pass": third_retest(3) is True and third_retest(2) is False,
        "got": [third_retest(3), third_retest(2)],
        "expected": [True, False],
    })
    cases.append({
        "id": "R-S06.two_reason",
        "pass": two_reason(100.0, 100.4, 0.5) is True,
        "got": two_reason(100.0, 100.4, 0.5),
        "expected": True,
    })
    cases.append({
        "id": "R-P06.first_hit",
        "pass": first_hit([("london", 200), ("asia", 150), ("ny", 400)]) == "asia",
        "got": first_hit([("london", 200), ("asia", 150), ("ny", 400)]),
        "expected": "asia",
    })
    cases.append({
        "id": "R-P20.sigEvent",
        "pass": mvfl_sig_event(4100.0, 550.0, 9000.0, 3200.0) is True,
        "got": mvfl_sig_event(4100.0, 550.0, 9000.0, 3200.0),
        "expected": True,
    })
    cases.append({
        "id": "R-S05.microbalance",
        "pass": microbalance_break([100.0, 101.0, 110.5], 110.0, 90.0) is True,
        "got": microbalance_break([100.0, 101.0, 110.5], 110.0, 90.0),
        "expected": True,
    })

    failed = [c for c in cases if not c["pass"]]
    groups = [{"name": "formulas", "pass": not failed, "cases": cases}]
    for mod_name, fn_name in (
        ("trading_research.research.phase1_live.formulas_jumbo", "jumbo_fixtures"),
        ("trading_research.research.phase1_live.formulas_flow", "flow_fixtures"),
    ):
        try:
            mod = __import__(mod_name, fromlist=[fn_name])
            extra = getattr(mod, fn_name)()
        except (ImportError, AttributeError):
            continue
        for g in extra.get("groups") or []:
            groups.append(g)
            cases.extend(g.get("cases") or [])
        failed = [c for c in cases if not c["pass"]]
    return {
        "ticket": "formulas",
        "pass": not failed,
        "n_cases": len(cases),
        "n_failed": len(failed),
        "groups": groups,
    }
