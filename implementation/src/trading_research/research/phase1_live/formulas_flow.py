"""Faithful Flow / Sires / Pine / Regime procedures from FORMULAS.md."""

from __future__ import annotations

import math

import numpy as np

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.family_open import value_area
from trading_research.research.phase1_live.formulas import daily_floor_pivots
from trading_research.research.phase1_live.grid import reject_after_touch, to_ticks

ABS_Q90_BUY = 3533.0
ABS_Q90_SELL = 3441.0
TAPE_WINDOW_S = 30.0
MAGIC_HOURS = (23, 0, 1, 2, 6, 7, 8)
MAGIC_INV_PCT = {23: 75.0, 0: 100.0, 1: 100.0, 2: 75.0, 6: 100.0, 7: 100.0, 8: 75.0}
MAGIC_HARD_STOP = {23: 3, 0: 4, 1: 5, 2: 6, 6: 10, 7: 11, 8: 12}


def _arr(x, dtype=np.float64) -> np.ndarray:
    return np.asarray(x, dtype=dtype)


def _py(x):
    if isinstance(x, (np.generic,)):
        return x.item()
    return x


def running_vwap(h, l, c, v) -> tuple[np.ndarray, np.ndarray]:
    tp = (_arr(h) + _arr(l) + _arr(c)) / 3.0
    vol = _arr(v)
    pv = np.cumsum(tp * vol)
    vv = np.cumsum(vol)
    den = np.maximum(vv, 1e-12)
    vwap = pv / den
    ss = np.cumsum(vol * tp * tp)
    var = np.maximum(ss - pv * pv / den, 0.0) / den
    return vwap, np.sqrt(var)


def vwap_band(vwap: float, sigma: float, m: float = 2.0) -> tuple[float, float]:
    return vwap - m * sigma, vwap + m * sigma


def tape_speed_pps(t_ms, end_ms: float, window_s: float = TAPE_WINDOW_S) -> float:
    t = _arr(t_ms)
    n = int(np.sum((t > end_ms - window_s * 1000.0) & (t <= end_ms)))
    return n / window_s if window_s else 0.0


def aggressive_at_level(
    price, size, side, t_ms, *, level: float, t0: float, t1: float,
    toward: int, tick_tol: float = 2 * TICK,
) -> dict:
    px, sz, sd, tm = _arr(price), _arr(size), _arr(side, np.int64), _arr(t_ms)
    w = (tm >= t0) & (tm < t1)
    px, sz, sd = px[w], sz[w], sd[w]
    if px.size == 0:
        return {"vol": 0.0, "advance_ticks": 0.0, "delta": 0.0, "n": 0}
    in_zone = np.abs(px - level) <= tick_tol
    if toward > 0:
        vol = float(sz[(sd > 0) & in_zone].sum())
        advance = float(px.max() - level)
    else:
        vol = float(sz[(sd < 0) & in_zone].sum())
        advance = float(level - px.min())
    buy = float(sz[sd > 0].sum())
    sell = float(sz[sd < 0].sum())
    return {
        "vol": vol,
        "advance_ticks": advance / TICK,
        "delta": buy - sell,
        "n": int(px.size),
        "min_px": float(px.min()),
        "max_px": float(px.max()),
    }


def absorption_a_at_level(
    price, size, side, t_ms, *, level: float, t0: float, t1: float,
    toward: int, vol_cut: float, r_width: float, reversal_px: float | None,
    tick_tol: float = 2 * TICK, rev_frac: float = 0.25,
) -> dict:
    g = aggressive_at_level(
        price, size, side, t_ms, level=level, t0=t0, t1=t1, toward=toward, tick_tol=tick_tol,
    )
    vol_ok = g["vol"] >= vol_cut
    adv_ok = g["advance_ticks"] <= tick_tol / TICK + 1e-9
    trapped = ((g["delta"] < 0) if toward < 0 else (g["delta"] > 0)) and adv_ok
    rev = False
    if reversal_px is not None and r_width:
        need = rev_frac * r_width
        if toward < 0:
            rev = (reversal_px - level) >= need
        else:
            rev = (level - reversal_px) >= need
    return {
        "vol": g["vol"],
        "advance_ticks": g["advance_ticks"],
        "delta": g["delta"],
        "vol_ok": vol_ok,
        "advance_ok": adv_ok,
        "trapped": bool(trapped),
        "absorption_A": bool(vol_ok and adv_ok and rev),
        "reversal": bool(rev),
        "min_px": g.get("min_px"),
        "max_px": g.get("max_px"),
    }


def exhaustion_split(stall_vol: float, prior_vol: float) -> dict:
    shrinking = stall_vol < prior_vol
    return {"shrinking": bool(shrinking), "big": bool(not shrinking)}


def r_f02_regular_div(prior_px: float, prior_cvd: float, new_px: float, new_cvd: float, *, side: str = "high") -> bool:
    if side == "high":
        return bool(new_px > prior_px and new_cvd < prior_cvd)
    return bool(new_px < prior_px and new_cvd > prior_cvd)


def r_f02_fakeout_grade(cvd_slope: float) -> bool:
    return bool(cvd_slope <= 0)


def r_f02_div_at_level(extreme, cvd, level, cvd_ref, *, side: str = "high") -> bool:
    if level is None or cvd_ref is None:
        return False
    e = _arr(extreme)
    x = _arr(cvd)
    if e.size == 0:
        return False
    if side == "high":
        return bool(np.any((e > float(level)) & (x + 1e-9 < float(cvd_ref))))
    return bool(np.any((e < float(level)) & (x > float(cvd_ref) + 1e-9)))


def r_f02_grid_div(extreme, cvd, i_touch, *, side: str = "high", horizon: int = 15) -> bool:
    if i_touch is None or i_touch < 0:
        return False
    e = _arr(extreme)
    x = _arr(cvd)
    i0 = int(i_touch)
    if i0 >= e.size:
        return False
    i1 = min(i0 + horizon, e.size)
    e = e[i0:i1]
    x = x[i0:i1]
    if e.size < 2:
        return False
    if side == "high":
        return bool(np.any((e[1:] > e[0]) & (x[1:] + 1e-9 < x[0])))
    return bool(np.any((e[1:] < e[0]) & (x[1:] > x[0] + 1e-9)))


def r_f02_div_series(hi, cvd, lo=None) -> bool:
    h = _arr(hi)
    x = _arr(cvd)
    if h.size < 2:
        return False
    peak = np.maximum.accumulate(h)
    cvd_hi = np.maximum.accumulate(x)
    bear = bool(np.any((h[1:] > peak[:-1] + 1e-9) & (x[1:] + 1e-9 < cvd_hi[:-1])))
    if lo is None:
        return bear
    l = _arr(lo)
    trough = np.minimum.accumulate(l)
    cvd_lo = np.minimum.accumulate(x)
    bull = bool(np.any((l[1:] < trough[:-1] - 1e-9) & (x[1:] > cvd_lo[:-1] + 1e-9)))
    return bear or bull


def r_p18_ohlc_cvd(o, c, v) -> dict:
    o, c, v = _arr(o), _arr(c), _arr(v)
    delta = np.where(c > o, v, np.where(c < o, -v, 0.0))
    return {"cvd": float(delta.sum()), "delta": delta}


def r_r04_smt_prior(nq_level, sis_level, nq_ext, sis_ext, *, side: str = "high") -> bool:
    if nq_level is None or sis_level is None or nq_ext is None or sis_ext is None:
        return False
    if side == "high":
        return bool(sis_ext > sis_level and not (nq_ext > nq_level))
    return bool(sis_ext < sis_level and not (nq_ext < nq_level))


def r_r01_gex_k(gamma: float, oi: float, spot: float, *, call: bool) -> float:
    g = float(gamma) * float(oi) * 100.0 * float(spot) * float(spot) * 0.01
    return g if call else -g


def r_f01_vwap_fade(
    vwap: float, sigma: float, *, band_m: float = 2.0,
    bar_high: float | None = None, bar_low: float | None = None,
    abs_result: dict | None = None, later_low: float | None = None,
    later_high: float | None = None, owed_open: bool = False,
) -> dict:
    lo, hi = vwap_band(vwap, sigma, band_m)
    t2 = 2 * TICK
    touch_hi = bar_high is not None and bar_high >= hi - t2 and (bar_low is None or bar_low <= hi + t2)
    touch_lo = bar_low is not None and bar_low <= lo + t2 and (bar_high is None or bar_high >= lo - t2)
    touch = bool(touch_hi or touch_lo)
    abs_flag = bool(abs_result and abs_result.get("vol_ok") and abs_result.get("advance_ok"))
    median_reach = False
    if later_low is not None and later_high is not None:
        median_reach = later_low <= vwap + t2 and later_high >= vwap - t2
    elif later_low is not None:
        median_reach = later_low <= vwap + t2
    elif later_high is not None:
        median_reach = later_high >= vwap - t2
    return {
        "band_lo": lo,
        "band_hi": hi,
        "touch": touch,
        "absorption_A_at_band": abs_flag and touch,
        "median_reach_60": bool(median_reach),
        "owed_open": bool(owed_open),
    }


def r_f03_convergence(
    session_vwap: float, weekly_vwap: float, other_vwap: float, va_height: float,
    *, touch_px: float | None = None, close: float | None = None, sigma: float | None = None,
) -> dict:
    tR = 0.05 * va_height
    xs = [session_vwap, weekly_vwap, other_vwap]
    spread = max(xs) - min(xs)
    conv = spread <= tR + 1e-12
    price = float(np.mean(xs))
    touch = touch_px is not None and abs(touch_px - price) <= 2 * TICK
    rej = False
    if conv and touch and close is not None and sigma:
        side = -1 if touch_px <= price else 1
        ct = to_ticks([close])
        ts = np.array([0], dtype=np.int64)
        r_ticks = max(1, int(round(0.5 * sigma / TICK)))
        rej = reject_after_touch(ct, ts, 0, int(round(price / TICK)), side, r_ticks, 15 * 60_000)
    return {
        "convergence": bool(conv),
        "tR": tR,
        "spread": spread,
        "price": price,
        "touch": bool(touch),
        "reject": bool(rej),
    }


def r_f04_candle_stack(ask: dict[float, float], bid: dict[float, float], *, k: float = 4.0) -> dict:
    prices = sorted(set(ask) | set(bid))
    flags: dict[float, int] = {}
    for p in prices:
        a = float(ask.get(p, 0.0))
        b = float(bid.get(p, 0.0))
        below, above = p - TICK, p + TICK
        buy = False
        sell = False
        if below in bid or below in ask:
            opp = float(bid.get(below, 0.0))
            if opp > 0:
                buy = a >= k * opp
            elif a >= 1.0:
                buy = True
        if above in ask or above in bid:
            opp = float(ask.get(above, 0.0))
            if opp > 0:
                sell = b >= k * opp
            elif b >= 1.0:
                sell = True
        if buy:
            flags[p] = 1
        elif sell:
            flags[p] = -1
    best = 0
    run_side = 0
    run = 0
    zone = None
    run_start = None
    prev = None
    for p in prices:
        side = flags.get(p, 0)
        if side != 0 and prev is not None and abs(p - prev - TICK) < 1e-9 and side == run_side:
            run += 1
        elif side != 0:
            run, run_side, run_start = 1, side, p
        else:
            run, run_side, run_start = 0, 0, None
        if run >= 3 and run > best:
            best = run
            zone = [run_start, p]
        if side != 0:
            prev = p
        else:
            prev = None
    return {"stack3": best >= 3, "k": k, "zone": zone, "flags": flags, "run": best}


def r_f04_revisit_hold(zone: list[float], side: int, later_touch: float, later_close: float) -> dict:
    height = abs(zone[1] - zone[0])
    edge = zone[1] if side > 0 else zone[0]
    r = 0.5 * height
    hold = False
    if side > 0:
        hold = later_close >= edge + r
    else:
        hold = later_close <= edge - r
    return {"revisit_hold": bool(hold), "R": height, "edge": edge}


def r_f05_absorption_stack(
    o: float, c: float, delta: float, poc: float, low: float, high: float,
    next_poc: float | None = None, next_low: float | None = None, next_high: float | None = None,
    later_close: float | None = None, r_width: float | None = None,
) -> dict:
    disagree_bull = c > o and delta < 0
    disagree_bear = c < o and delta > 0
    rng = max(high - low, TICK)
    pos = (poc - low) / rng
    flip = False
    if next_poc is not None and next_low is not None and next_high is not None:
        npos = (next_poc - next_low) / max(next_high - next_low, TICK)
        if disagree_bull:
            flip = pos <= 1.0 / 3.0 + 1e-12 and npos >= 2.0 / 3.0 - 1e-12
        if disagree_bear:
            flip = pos >= 2.0 / 3.0 - 1e-12 and npos <= 1.0 / 3.0 + 1e-12
    rev = False
    if later_close is not None and r_width:
        need = 0.25 * r_width
        if disagree_bull:
            rev = (later_close - min(o, c, low)) >= need - 1e-9
        elif disagree_bear:
            rev = (max(o, c, high) - later_close) >= need - 1e-9
    return {
        "disagree_bull": bool(disagree_bull),
        "disagree_bear": bool(disagree_bear),
        "poc_pos": pos,
        "poc_flip": bool(flip),
        "reversal": bool(rev),
    }


def r_f06_dom_absorption(
    price, size, side, t_ms, *, level: float, t0: float, t1: float, toward: int,
    r_width: float, reversal_px: float, prior_vol: float | None = None,
    vol_cut: float | None = None, tick_tol: float = 2 * TICK,
) -> dict:
    cut = vol_cut if vol_cut is not None else (ABS_Q90_BUY if toward > 0 else ABS_Q90_SELL)
    a = absorption_a_at_level(
        price, size, side, t_ms, level=level, t0=t0, t1=t1, toward=toward,
        vol_cut=cut, r_width=r_width, reversal_px=reversal_px, tick_tol=tick_tol,
    )
    out = {
        "absorption_A": a["absorption_A"],
        "trapped": a["trapped"],
        "vol": a["vol"],
        "advance_ticks": a["advance_ticks"],
        "delta": a["delta"],
    }
    if prior_vol is not None:
        out.update(exhaustion_split(a["vol"], prior_vol))
    return out


def reward_3tick(prices: list[float], *, absorption_px: float, direction: int) -> dict:
    """direction +1 is up (reversal of absorbed sells), -1 down."""
    p = _arr(prices)
    if p.size == 0:
        return {"reward_3tick": False, "adverse_ticks": 0.0}
    signed = (p - absorption_px) * direction
    adverse = float((-signed).max()) if signed.size else 0.0
    if adverse < 0:
        adverse = 0.0
    max_fav = float(signed.max())
    ok = max_fav >= 3 * TICK - 1e-12 and adverse <= 3 * TICK + 1e-12
    return {"reward_3tick": bool(ok), "adverse_ticks": adverse / TICK, "favor_ticks": max_fav / TICK}


def r_f08_abs_four_check(
    *, level: float, kind: str, poc: float | None, va_height: float,
    absorption_px: float, path: list[float], direction: int,
    second_vol: float, q75: float, n_abs: int | None = None, n_fail_no_reward: int | None = None,
) -> dict:
    tR = 0.05 * va_height if va_height else 2 * TICK
    loc_ok = kind in {"shelf", "lvn", "minor", "vah", "val", "extreme"}
    if poc is not None and abs(absorption_px - poc) <= tR:
        loc_ok = False
    rew = reward_3tick(path, absorption_px=absorption_px, direction=direction)
    second = second_vol >= q75
    out = {
        "location_ok": bool(loc_ok),
        "reward_3tick": rew["reward_3tick"],
        "second_aggression": bool(second),
        "cvd_median": None,
    }
    if n_abs:
        out["fail_share"] = (n_fail_no_reward or 0) / n_abs
    return out


def digits_thinning(earlier_median: float, last20_median: float, *, from_lots: float = 10.0) -> bool:
    return earlier_median >= from_lots and last20_median < 10.0


def liftoff_upticks(last_prices: list[float], *, min_ticks: int = 2) -> dict:
    p = _arr(last_prices)
    if p.size < 2:
        return {"liftoff": False, "n": 0}
    d = np.diff(p)
    up = d > 0
    if not np.all(up) and not np.all(d < 0):
        n = 0
        best = 0
        cur = 0
        sign = 0
        for x in d:
            s = 1 if x > 0 else (-1 if x < 0 else 0)
            if s == 0:
                cur = 0
                sign = 0
                continue
            if s == sign:
                cur += 1
            else:
                sign, cur = s, 1
            best = max(best, cur)
        n = best
    else:
        n = int(p.size - 1)
    ok = n >= min_ticks
    entry = [float(p[-1]), float(p[-1]) + (2 * TICK if p[-1] >= p[0] else -2 * TICK)]
    if p[-1] >= p[0]:
        entry = [float(p[-1]), float(p[-1]) + 2 * TICK]
    else:
        entry = [float(p[-1]) - 2 * TICK, float(p[-1])]
    return {"liftoff": bool(ok), "n": n, "at": float(p[-1]), "entry_window": entry}


def r_f09_stop_stages(
    *, stage1: dict, last20_median: float, earlier_median: float, bar_delta: float,
    toward: int, last_prices: list[float],
) -> dict:
    s1 = bool(stage1.get("vol_ok") and stage1.get("advance_ok"))
    thin = digits_thinning(earlier_median, last20_median)
    against = (toward < 0 and bar_delta > 0) or (toward > 0 and bar_delta < 0)
    s3 = thin and against
    s4 = liftoff_upticks(last_prices, min_ticks=2)
    return {
        "stage1": s1,
        "stage2": None,
        "thinning": bool(thin),
        "delta_against": bool(against),
        "stage3": bool(s3),
        "liftoff": s4["liftoff"],
        "entry_window": s4["entry_window"],
        "liftoff_at": s4["at"],
    }


def fractal_low_5(lows: np.ndarray, i: int) -> bool:
    if i < 2 or i + 2 >= lows.size:
        return False
    x = lows[i]
    return bool(x < lows[i - 2] and x < lows[i - 1] and x < lows[i + 1] and x < lows[i + 2])


def r_f10_protected_low(
    lows, highs, closes, *, fractal_i: int, delta_at: float, q75: float,
    prior_swing_high: float, escape_i: int, protect_n: int = 5, break_i: int | None = None,
    mfe_high: float | None = None,
) -> dict:
    l, h, c = _arr(lows), _arr(highs), _arr(closes)
    confirmed = fractal_i + 2
    px = float(l[fractal_i])
    delta_ok = delta_at >= q75
    escaped = float(c[escape_i]) > prior_swing_high
    sl = l[escape_i + 1:escape_i + 1 + protect_n]
    quiet = sl.size == protect_n and float(sl.min()) > px + 2 * TICK
    protected = bool(fractal_low_5(l, fractal_i) and delta_ok and escaped and quiet)
    broken = False
    mfe = None
    if protected and break_i is not None:
        broken = float(c[break_i]) < px
        peak = mfe_high if mfe_high is not None else float(h[escape_i:break_i + 1].max())
        mfe = peak - px
    return {
        "protected_low": px if protected else None,
        "confirmed_at": confirmed,
        "broken": bool(broken),
        "mfe": mfe,
        "delta_ok": bool(delta_ok),
    }


def profile_nodes(bins: dict[float, float]) -> dict:
    prices = np.array(sorted(bins), dtype=np.float64)
    vals = np.array([bins[p] for p in prices], dtype=np.float64)
    med = float(np.median(vals))
    hvn, lvn = [], []
    for i, p in enumerate(prices):
        left = vals[i - 1] if i else vals[i]
        right = vals[i + 1] if i + 1 < vals.size else vals[i]
        if vals[i] >= left and vals[i] >= right and vals[i] >= 1.5 * med:
            hvn.append(float(p))
        if vals[i] <= left and vals[i] <= right and vals[i] <= 0.5 * med:
            lvn.append(float(p))
    poc = float(prices[int(np.argmax(vals))])
    return {"hvn": hvn, "lvn": lvn, "poc": poc, "median": med, "minor_hvn": [p for p in hvn if p != poc]}


def r_f11_delta_lvn(
    *, band_lo: float, band_hi: float, lvn: float, dp: float,
    touches: list[dict],
) -> dict:
    height = band_hi - band_lo
    tR = 0.05 * height
    paired = abs(dp - lvn) <= tR + 1e-12
    n_wick = 0
    n_full = 0
    r = 0.5 * height
    for tch in touches:
        high, low, close = tch["h"], tch["l"], tch["c"]
        if high >= dp - 2 * TICK and low <= dp + 2 * TICK:
            wick_beyond = high - dp
            wick_ok = wick_beyond >= 2 * TICK - 1e-12 and close < dp
            full = close <= dp - r
            if wick_ok:
                n_wick += 1
            if full:
                n_full += 1
    return {
        "paired": bool(paired),
        "tR": tR,
        "wick_reaction": n_wick > 0,
        "reaction": n_full > 0,
        "repeat_count": n_wick,
    }


def r_f12_arrival(
    closes_5: list[float], vol_5: list[float], *, q75_disp: float, q25_disp: float | None = None,
    later_close: float | None = None, level: float | None = None, held_30: bool | None = None,
) -> dict:
    c = _arr(closes_5)
    v = _arr(vol_5)
    disp_ticks = float(c[-1] - c[0]) / max(len(closes_5), 1) / TICK
    slope = float(v[-1] - v[0])
    aggressive = disp_ticks >= q75_disp and slope >= 0
    drift = (q25_disp is not None and disp_ticks <= q25_disp) or slope < 0
    klass = "aggressive" if aggressive and not drift else ("drift" if drift else "other")
    broken = False
    defended = False
    if later_close is not None and level is not None:
        broken = later_close > level and bool(held_30)
        defended = (not broken) and later_close <= level
    return {
        "arrival": klass,
        "disp_ticks_per_min": disp_ticks,
        "slope": slope,
        "broken": bool(broken),
        "defended": bool(defended),
    }


def r_f13_trapped_buyers(
    *, band_high: float, dp_max: float, tR: float, am_high: float, pm_high: float,
    any_close_above: bool, intra_lo: float, intra_hi: float,
    break_close: float, retest_high: float, sell_in_body: bool,
    body: tuple[float, float], reject_close: float,
) -> dict:
    paired = abs(dp_max - band_high) <= tR + 1e-12
    two_fail = (abs(am_high - band_high) <= 2 * TICK or am_high >= band_high - 2 * TICK) and (
        abs(pm_high - band_high) <= 2 * TICK or pm_high >= band_high - 2 * TICK
    ) and not any_close_above
    r_width = intra_hi - intra_lo
    breakout = break_close < intra_lo
    retest = abs(retest_high - intra_lo) <= 2 * TICK
    in_body = sell_in_body and body[0] <= body[1]
    hold = reject_close <= intra_lo - 0.5 * r_width and in_body
    return {
        "paired": bool(paired),
        "two_failures": bool(two_fail),
        "breakout": bool(breakout),
        "retest_hold": bool(breakout and retest and hold),
    }


def r_f14_imb350(
    o: float, h: float, l: float, c: float,
    prints: list[tuple[float, float, int]],
    buy_at: dict[float, float],
    sell_at: dict[float, float],
    *, retest_high: float | None = None, retest_close: float | None = None,
) -> dict:
    body_lo, body_hi = min(o, c), max(o, c)
    zone = None
    rewarded = False
    for px, sz, side in prints:
        if not (30 <= sz <= 60):
            continue
        in_body = body_lo <= px <= body_hi
        imb = sell_at.get(px, 0.0) >= 3.5 * buy_at.get(px, 0.0) if side < 0 else buy_at.get(px, 0.0) >= 3.5 * sell_at.get(px, 0.0)
        if in_body and imb:
            zone = px
            rewarded = True
    rej = False
    if zone is not None and retest_high is not None and retest_close is not None:
        rng = h - l
        if sell_at.get(zone, 0) >= 3.5 * buy_at.get(zone, 0):
            rej = retest_close <= zone - 0.5 * rng
        else:
            rej = retest_close >= zone + 0.5 * rng
    return {"imb350_zone": zone, "rewarded": rewarded, "retest_reject": bool(rej)}


def r_f15_ofm(
    *, swing: float, r_height: float, wick_prints: list[tuple[float, float, float]],
    release_close: float, tape_pps: float, tape_cut: float | None,
    fail_close: float | None, refill_touch: float | None,
    resqueeze_close: float | None, fail_wick: float | None,
    stop: float | None, later_high: float | None = None, later_low: float | None = None,
) -> dict:
    band = 0.1 * r_height
    absorbed = [p for p in wick_prints if p[1] >= 30 and abs(p[0] - swing) <= band + 1e-12]
    cat = None
    if len(absorbed) >= 2:
        first = absorbed[0][0]
        cat = [min(first, swing), max(first, swing)]
    tape_ok = tape_cut is not None and tape_pps >= tape_cut
    release = False
    fail = False
    if cat is not None:
        lo, hi = min(cat), max(cat)
        squeeze_up = abs(swing - hi) <= abs(swing - lo)
        release = release_close > hi if squeeze_up else release_close < lo
        if fail_close is not None:
            fail = fail_close < lo if squeeze_up else fail_close > hi
    refill = refill_touch is not None and cat is not None and min(cat) - 2 * TICK <= refill_touch <= max(cat) + 2 * TICK
    entry = False
    r_dist = None
    reach_1r = reach_2r = False
    if cat is not None and resqueeze_close is not None and fail_wick is not None:
        squeeze_up = abs(swing - max(cat)) <= abs(swing - min(cat))
        entry = resqueeze_close > fail_wick if squeeze_up else resqueeze_close < fail_wick
        if entry and stop is not None:
            r_dist = abs(resqueeze_close - stop)
            mfe = 0.0
            if later_high is not None:
                mfe = max(mfe, later_high - resqueeze_close)
            if later_low is not None:
                mfe = max(mfe, resqueeze_close - later_low)
            if r_dist:
                reach_1r = mfe >= r_dist - 1e-12
                reach_2r = mfe >= 2 * r_dist - 1e-12
    return {
        "catalyst": cat,
        "tape_speed_ok": bool(tape_ok),
        "tape_cut_source": "unspecified",
        "gamma": None,
        "ofm_entry": bool(entry),
        "R": r_dist,
        "reach_1R": bool(reach_1r),
        "reach_2R": bool(reach_2r),
        "fail": bool(fail),
        "refill": bool(refill),
        "release": bool(release),
    }


def r_f16_balance_fade(
    *, range_lo: float, range_hi: float, wick_ok: bool, no_close_beyond: bool,
    left_px: float, test_high: float | None = None, test_low: float | None = None,
    abs_ok: bool, target: float, later_low: float | None = None, later_high: float | None = None,
    day_label: str | None = None, side: str = "high",
) -> dict:
    r_h = range_hi - range_lo
    failed_agg = wick_ok and no_close_beyond
    left = abs(left_px - range_hi) >= 0.25 * r_h or abs(left_px - range_lo) >= 0.25 * r_h
    if side == "high":
        trigger = failed_agg and left and test_high is not None and abs(test_high - range_hi) <= 2 * TICK and abs_ok
        reach = later_low is not None and later_low <= target + 2 * TICK
    else:
        trigger = failed_agg and left and test_low is not None and abs(test_low - range_lo) <= 2 * TICK and abs_ok
        reach = later_high is not None and later_high >= target - 2 * TICK
    return {
        "fade_trigger": bool(trigger),
        "target_reach": bool(reach),
        "gamma": None,
        "balance_proxy": day_label in {"normal", "neutral"} if day_label is not None else None,
    }


def r_f17_refill_zone(
    prints: list[tuple[float, float, float, int]],
    *, min_size: float = 60.0, window_s: float = 30.0,
    leave_px: float, touch_px: float, deepest: float, later_extreme: float,
    close_beyond: bool,
) -> dict:
    cluster = None
    for i, (t0, p0, s0, side0) in enumerate(prints):
        if s0 < min_size:
            continue
        group = [(t0, p0, s0, side0)]
        for t1, p1, s1, side1 in prints[i + 1:]:
            if t1 - t0 > window_s * 1000.0:
                break
            if s1 >= min_size and side1 == side0:
                group.append((t1, p1, s1, side1))
        if len(group) >= 3:
            xs = [g[1] for g in group]
            cluster = [min(xs), max(xs)]
            side = side0
            break
    if cluster is None:
        return {"zone": None, "hold": False, "penetration": None}
    lo, hi = cluster
    if side < 0:
        left = leave_px >= hi + 4 * TICK - 1e-12
        far = lo
        pen_ticks = (far - deepest) / TICK
        defended_leave = later_extreme - hi >= 12 * TICK - 1e-12
        beyond = close_beyond
    else:
        left = leave_px <= lo - 4 * TICK + 1e-12
        far = hi
        pen_ticks = (deepest - far) / TICK
        defended_leave = lo - later_extreme >= 12 * TICK - 1e-12
        beyond = close_beyond
    hold = left and pen_ticks <= 32 + 1e-12 and not beyond and defended_leave
    return {"zone": cluster, "hold": bool(hold), "penetration": pen_ticks, "left": bool(left)}


def r_f18_squeeze(
    *, catalyst: list[float], release_close: float, tape_pps: float, tape_cut: float,
    any_close_through: bool, trigger_abs: bool, next_level: float, later_touch: float,
) -> dict:
    fast = tape_pps >= tape_cut
    no_fail = not any_close_through
    cont = abs(later_touch - next_level) <= 2 * TICK or (
        later_touch <= next_level + 2 * TICK and later_touch >= next_level - 2 * TICK
    )
    return {
        "no_failure": bool(no_fail),
        "tape_speed_ok": bool(fast),
        "tape_cut_source": "unspecified",
        "trigger": bool(trigger_abs and no_fail and fast),
        "continuation": bool(cont),
        "tape_window_s": TAPE_WINDOW_S,
    }


def r_r03_thesis(
    *, val: float, vah: float, open_px: float, am_high: float, am_low: float,
    any_close_beyond: bool, news: bool, start_min: float = 9 * 60 + 30,
    eval_min: float = 12 * 60, session_end_min: float = 16 * 60,
    developing_overlap: bool = True,
) -> dict:
    if open_px > vah:
        label, edge = "long", vah
    elif open_px < val:
        label, edge = "short", val
    else:
        label, edge = "neutral", None
    if label == "short":
        struct = bool(any_close_beyond) or am_high > val
    elif label == "long":
        struct = bool(any_close_beyond) or am_low < vah
    else:
        struct = bool(any_close_beyond)
    value_shift = not developing_overlap
    death = struct or value_shift or news
    end = eval_min if death else session_end_min
    alive = end - start_min
    return {
        "label": label,
        "band_edge": edge,
        "end": end,
        "alive_min": alive,
        "death": bool(death),
    }


def r_s01_refill_short(
    *, range_high: float, abs_ok: float | bool, max_print: float, close_below: float,
    objective: float, later_high: float, later_low: float,
) -> dict:
    refill = bool(abs_ok) and close_below < range_high
    inval = max_print + 2 * TICK
    dist = inval - close_below
    reach = later_low <= objective + 2 * TICK
    return {
        "refill_short": bool(refill),
        "inval_px": inval,
        "inval_dist": dist,
        "objective_reach": bool(reach),
        "mfe": close_below - later_low,
        "mae": later_high - close_below,
    }


def r_s01_refill_long(
    *, range_low: float, abs_ok: float | bool, min_print: float, close_above: float,
    objective: float, later_high: float, later_low: float,
) -> dict:
    refill = bool(abs_ok) and close_above > range_low
    inval = min_print - 2 * TICK
    dist = close_above - inval
    reach = later_high >= objective - 2 * TICK
    mfe = later_high - close_above
    mae = close_above - later_low
    return {
        "refill_long": bool(refill),
        "inval_px": inval,
        "inval_dist": dist,
        "objective_reach": bool(reach),
        "mfe": mfe,
        "mae": mae,
    }


def r_s02_third_retest(
    highs: list[float], lows_between: list[float], buy_vols: list[float],
    *, level: float, r_width: float, q90_buy: float = ABS_Q90_BUY,
    later_close: float | None = None, later_high: float | None = None,
    band_lo: float | None = None, band_hi: float | None = None,
    from_above: bool = True,
) -> dict:
    leave = 0.25 * r_width
    lo = level - 2 * TICK if band_lo is None else band_lo
    hi_b = level + 2 * TICK if band_hi is None else band_hi
    n = 0
    prev_leave = True
    if from_above:
        for i, lw in enumerate(lows_between):
            if prev_leave and lo - 2 * TICK <= lw <= hi_b + 2 * TICK:
                n += 1
                prev_leave = False
            if i < len(highs) and highs[i] >= hi_b + leave:
                prev_leave = True
    else:
        for i, hi in enumerate(highs):
            if prev_leave and lo - 2 * TICK <= hi <= hi_b + 2 * TICK:
                n += 1
                prev_leave = False
            if i < len(lows_between) and lows_between[i] <= lo - leave:
                prev_leave = True
    no_def = all(v < q90_buy for v in buy_vols)
    third = n >= 3 and no_def
    if from_above:
        loss = later_close is not None and later_close > lo
    else:
        loss = later_close is not None and later_close < hi_b
    mae = None
    if later_high is not None and from_above:
        mae = later_high - lo
    elif later_close is not None:
        mae = abs(later_close - (lo if from_above else hi_b))
    return {"third_test_short": bool(third), "tests": n, "loss_case": bool(loss), "mae": mae}


def r_s03_second_defence(
    *, level: float, break_close: float, retest_high: float, sell_vol: float, q75: float,
    print_sizes: list[float], later_low: float, r_width: float,
) -> dict:
    below = break_close < level
    retest = abs(retest_high - level) <= 2 * TICK
    part = sell_vol >= q75
    first = print_sizes[0]
    last3 = print_sizes[-3:]
    steady = all(s >= 0.8 * first for s in last3)
    thinning = all(last3[i] < last3[i - 1] for i in range(1, len(last3))) if len(last3) >= 2 else False
    defence = below and retest and part and steady
    rev = later_low <= level - 0.25 * r_width
    return {
        "steady": bool(steady),
        "thinning": bool(thinning),
        "second_defence": bool(defence),
        "reversal": bool(rev),
        "reload": None,
    }


def r_s04_ath_ofm(
    *, weekly_high: float, dp_min: float, tR: float, left_px: float, r_height: float,
    prior_high: float, touches: int, no_close_below: bool,
    imb350_buy: bool, micro_hi: float, break_close: float, next_level: float, later_high: float,
) -> dict:
    paired = abs(dp_min - weekly_high) <= tR + 1e-12
    left = (weekly_high - left_px) >= 0.5 * r_height - 1e-12
    trapped = paired and left
    fails = touches >= 2 and no_close_below
    ofm = trapped and fails and imb350_buy and break_close > micro_hi
    cont = later_high >= next_level - 2 * TICK
    return {
        "trapped_sellers": bool(trapped),
        "failures": touches,
        "ofm_long": bool(ofm),
        "continuation": bool(cont),
    }


def r_s05_microbalance(
    closes, lows, highs, *, r_height: float, min_bars: int = 5,
    break_close: float, htf: float, later_high: float, later_low: float,
) -> dict:
    c, lo, hi = _arr(closes), _arr(lows), _arr(highs)
    band = 0.1 * r_height
    box = None
    n = c.size
    for i in range(n - min_bars + 1):
        sl = c[i:]
        for j in range(min_bars, sl.size + 1):
            w = sl[:j]
            if float(w.max() - w.min()) <= band + 1e-12:
                box = [float(lo[i:i + j].min()), float(hi[i:i + j].max())]
    if box is None:
        return {"breakout_long": False, "box": None}
    brk = break_close > box[1]
    inval = box[0] - 2 * TICK
    reach = later_high >= htf - 2 * TICK
    return {
        "box": box,
        "breakout_long": bool(brk),
        "inval": inval,
        "htf_reach": bool(reach),
        "mfe": later_high - break_close,
        "mae": break_close - later_low,
    }


def r_s06_two_reason(
    *, swing_high: float, prior_reject: float, r_width: float, hvn: float, tR: float,
    touch_high: float, reject_close: float, entry: float, side: str = "short",
    swing_low: float | None = None, touch_low: float | None = None,
) -> dict:
    r1 = prior_reject >= 0.25 * r_width
    if side == "short":
        r2 = abs(hvn - swing_high) <= tR + 1e-12
        two = r1 and r2
        rej = reject_close <= swing_high - 0.5 * r_width
        inval = touch_high + 2 * TICK
        r_stop = inval - entry
        t15 = entry - 1.5 * r_stop
        r15 = reject_close <= t15
    else:
        lo = swing_low if swing_low is not None else swing_high
        r2 = abs(hvn - lo) <= tR + 1e-12
        two = r1 and r2
        rej = reject_close >= lo + 0.5 * r_width
        tl = touch_low if touch_low is not None else lo
        inval = tl - 2 * TICK
        r_stop = entry - inval
        t15 = entry + 1.5 * r_stop
        r15 = reject_close >= t15
    return {
        "two_reason": bool(two),
        "reject": bool(rej),
        "inval": inval,
        "r15_reach": bool(r15),
    }


def r_s07_areas(
    *, trigger_close: float, later_high: float, later_low: float,
    stop_ticks: tuple[int, ...] = (35, 15), objective_ticks: tuple[int, ...] = (188, 211),
) -> dict:
    mfe = later_high - trigger_close
    mae = trigger_close - later_low
    mfe_ticks = mfe / TICK
    mae_ticks = mae / TICK
    win_35_188 = mae_ticks < stop_ticks[0] and mfe_ticks >= objective_ticks[0]
    return {
        "mfe": mfe,
        "mae": mae,
        "mfe_ticks": mfe_ticks,
        "mae_ticks": mae_ticks,
        "win_35_188": bool(win_35_188),
        "survived_15": mae_ticks < stop_ticks[1],
    }


def r_s08_minor_node(
    *, hvn: float, balance_top: float, prior_rej: int, deltas: list[float],
    touch: float, reject_close: float, r_width: float,
    lvn: float, lvn_closes: list[float],
) -> dict:
    setup = abs(hvn - balance_top) <= 1.0 + 1e-12 and prior_rej >= 2 and all(d < 0 for d in deltas) and len(deltas) >= 3
    rej = reject_close <= touch - 0.5 * r_width
    slice_ = False
    stall = False
    if lvn_closes:
        through = [c < lvn for c in lvn_closes]
        slice_ = any(through[:2]) if len(through) >= 1 else False
        near = sum(abs(c - lvn) <= 2 * TICK for c in lvn_closes)
        stall = near >= 5
    return {"node_setup": bool(setup), "reject": bool(rej), "slice": bool(slice_), "stall": bool(stall)}


def r_s09_open_above_value(
    *, a_low: float, prior_vah: float, dev_vah: float, va_height: float,
    break_close: float, stack3: bool, retest_low: float, retest_close: float,
) -> dict:
    open_above = a_low > prior_vah
    brk = break_close > dev_vah and stack3
    hold = retest_low <= dev_vah + 2 * TICK and retest_low >= dev_vah - 2 * TICK and retest_close >= dev_vah + 0.5 * va_height
    return {"open_above_value": bool(open_above), "retest_hold": bool(brk and hold)}


def developing_va(tick_vol: dict, frac: float = 0.70) -> dict:
    poc, val, vah = value_area(tick_vol, frac)
    return {"poc": poc, "val": val, "vah": vah}


def sample_stdev(x) -> float:
    a = _arr(x)
    if a.size < 2:
        return float("nan")
    return float(np.std(a, ddof=1))


def r_p01_sigma_bands(open_px: float, sigma_pct: float, mult: float = 0.25) -> dict:
    sigma_px = open_px * sigma_pct / 100.0
    return {
        "sigma_px": sigma_px,
        "upper": open_px + mult * sigma_px,
        "lower": open_px - mult * sigma_px,
    }


def r_p01_touch_revert(
    open_px: float, upper: float, lower: float, sigma_px: float,
    hour, high, low,
) -> dict:
    hr, h, l = _arr(hour), _arr(high), _arr(low)
    side = None
    idx = None
    for i in range(h.size):
        up = h[i] >= upper
        dn = l[i] <= lower
        if up and dn:
            side = "upper" if abs(h[i] - upper) <= abs(l[i] - lower) else "lower"
            idx = i
            break
        if up:
            side, idx = "upper", i
            break
        if dn:
            side, idx = "lower", i
            break
    if idx is None:
        return {"touch": False, "reverted": False}
    reverted = False
    rev_i = None
    for j in range(idx, h.size):
        if side == "upper" and l[j] <= open_px:
            reverted, rev_i = True, j
            break
        if side == "lower" and h[j] >= open_px:
            reverted, rev_i = True, j
            break
    touch_hour = int(hr[idx])
    milestone = None
    if reverted:
        rh = int(hr[rev_i])
        if rh < 9:
            milestone = "by09"
        elif rh < 10:
            milestone = "by10"
        elif rh < 11:
            milestone = "by11"
        else:
            milestone = "by12"
    if side == "upper":
        ext = (float(h[idx]) - open_px) / sigma_px
    else:
        ext = (open_px - float(l[idx])) / sigma_px
    return {
        "touch": True,
        "side": side,
        "hour": touch_hour,
        "reverted": bool(reverted),
        "milestone": milestone,
        "ext_max": ext,
    }


def r_p02_hourly_sweep(
    *, prev_h: float, prev_l: float, prev_open: float, hour_open: float,
    highs, lows,
) -> dict:
    h, l = _arr(highs), _arr(lows)
    mid = 0.5 * (prev_h + prev_l)
    is_above = hour_open > prev_open
    hi_sw = bool(np.any(h > prev_h))
    lo_sw = bool(np.any(l < prev_l))
    depth = None
    if hi_sw:
        depth = (float(h.max()) - prev_h) / (prev_h - prev_l) * 100.0
    ret_s = ret_50 = ret_o = ret_opp = False
    if hi_sw:
        first = int(np.flatnonzero(h > prev_h)[0])
        after_l = l[first:]
        ret_s = bool(np.any(after_l <= prev_h))
        ret_50 = bool(np.any(after_l <= mid))
        ret_o = bool(np.any(after_l <= hour_open))
        ret_opp = bool(np.any(after_l <= prev_l))
    return {
        "isAbove": int(bool(is_above)),
        "high_sweep": hi_sw,
        "low_sweep": lo_sw,
        "depth_pct": depth,
        "high_ret_swept": ret_s,
        "high_ret_50": ret_50,
        "high_ret_open": ret_o,
        "high_ret_opp": ret_opp,
    }


def ext_to_zone(ep: float, inv_pct: float) -> str:
    if ep < 25:
        return "Z1"
    if ep < 50:
        return "Z2"
    if ep < inv_pct:
        return "Z3"
    if ep < 150:
        return "Z4"
    if ep < 300:
        return "Z5"
    return "Z6"


def r_p03_magic_hour(
    *, hour: int, box_h: float, box_l: float, break_side: str, excursion: float,
    later_high: float, later_low: float, t_break_min: float, t_target_min: float,
) -> dict:
    if hour not in MAGIC_HOURS:
        return {"mid": None, "ep": None, "zone": None, "win": False, "ttt_min": None, "inv_pct": None}
    mid = 0.5 * (box_h + box_l)
    w = box_h - box_l
    ep = abs(excursion) / w * 100.0
    inv = MAGIC_INV_PCT[hour]
    zone = ext_to_zone(ep, inv)
    if break_side == "low":
        win = later_high >= mid
    else:
        win = later_low <= mid
    stop_hr = MAGIC_HARD_STOP[hour]
    win = bool(win) and (t_target_min / 60.0) < stop_hr
    dt = t_target_min - t_break_min
    return {"mid": mid, "ep": ep, "zone": zone, "win": win, "ttt_min": dt, "inv_pct": inv, "hour": hour}


def r_p04_raid(
    *, box_h: float, box_l: float, highs, lows, closes, t_min, cutoff_min: float, min_pts: float = 5.0,
) -> dict:
    h, l, c, t = _arr(highs), _arr(lows), _arr(closes), _arr(t_min)
    inw = t <= cutoff_min
    raid_hi = bool(np.any((h > box_h + min_pts) & inw))
    pts = None
    conf = False
    bucket = None
    if raid_hi:
        first = int(np.flatnonzero((h > box_h + min_pts) & inw)[0])
        mx = float(h[first:][t[first:] <= cutoff_min].max()) if np.any(t[first:] <= cutoff_min) else float(h[first])
        pts = mx - box_h
        conf = bool(np.any((c[first:] <= box_h) & (t[first:] <= cutoff_min)))
        if pts < 20:
            bucket = "<20"
        else:
            bucket = str(int(pts // 10 * 10))
    return {"raid_hi": raid_hi, "raid_hi_conf": bool(conf), "raid_pts": pts, "bucket": bucket}


def r_p05_london_25(lon_o: float, lon_c: float, ny_l: float, ny_h: float, ny_c: float) -> dict:
    top, bot = max(lon_o, lon_c), min(lon_o, lon_c)
    body = top - bot
    bull = lon_c >= lon_o
    level = top - 0.25 * body if bull else bot + 0.25 * body
    if bull:
        wick = ny_l < level and ny_c > level
        fail = ny_l < level and ny_c <= level
        above = ny_l >= level
        return {"level": level, "wick_lon25_bull": bool(wick), "fail": bool(fail), "above_lon25": bool(above)}
    wick = ny_h > level and ny_c < level
    return {"level": level, "wick_lon25_bear": bool(wick)}


def r_p06_first_hit(
    *, asia_h: float, asia_l: float, lon_open: float, lon_highs, lon_lows,
) -> dict:
    mid = 0.5 * (asia_h + asia_l)
    pos = "above" if lon_open > mid else "below"
    h, l = _arr(lon_highs), _arr(lon_lows)
    first = None
    seq = False
    for i in range(h.size):
        hit_h = h[i] >= asia_h
        hit_l = l[i] <= asia_l
        if first is None:
            if hit_h and not hit_l:
                first = "asia_high"
            elif hit_l and not hit_h:
                first = "asia_low"
            elif hit_h and hit_l:
                first = "asia_high" if h[i] - asia_h >= asia_l - l[i] else "asia_low"
        else:
            if first == "asia_high" and hit_l:
                seq = True
                break
            if first == "asia_low" and hit_h:
                seq = True
                break
    return {"position": pos, "london_first_hit": first, "sequential": int(bool(seq))}


def r_p07_or_mid(
    *, o: float, h: float, l: float, c: float, later_h, later_l, later_c,
    kind: str = "5m",
) -> dict:
    mid = 0.5 * (h + l)
    bull = c > o
    lh, ll, lc = _arr(later_h), _arr(later_l), _arr(later_c)
    extreme = None
    for i in range(lh.size):
        hi = lh[i] >= h
        lo = ll[i] <= l
        if hi and not lo:
            extreme = "high"
            break
        if lo and not hi:
            extreme = "low"
            break
        if hi and lo:
            extreme = "high"
            break
    mid_retest = False
    prev_c = c
    for i in range(lh.size):
        span = lh[i] >= mid and ll[i] <= mid
        cross = (prev_c < mid <= lc[i]) or (prev_c > mid >= lc[i])
        if span or cross:
            mid_retest = True
            break
        prev_c = lc[i]
    if kind == "5m":
        ext_up = h * (1 + 0.00411)
        ext_dn = l * (1 - 0.00450)
    else:
        ext_up = h * (1 + 0.00380)
        ext_dn = l * (1 - 0.00415)
    return {
        "mid": mid,
        "is_bull": bool(bull),
        "extreme_first": extreme,
        "mid_retest": bool(mid_retest),
        "ext_up": ext_up,
        "ext_dn": ext_dn,
    }


def r_p09_no_break(open_px: float, prior_h: float, prior_l: float, rth_high: float, rth_low: float) -> dict:
    if open_px > prior_h:
        status = "Above"
    elif open_px < prior_l:
        status = "Below"
    else:
        status = "Inside"
    brk_h = rth_high > prior_h
    brk_l = rth_low < prior_l
    return {
        "status": status,
        "no_break_prev_high": (not brk_h) if status == "Below" else None,
        "no_break_prev_low": (not brk_l) if status == "Above" else None,
        "inside_stay": (not brk_h and not brk_l) if status == "Inside" else None,
        "one_side": (brk_h ^ brk_l) if status == "Inside" else None,
        "both": (brk_h and brk_l) if status == "Inside" else None,
    }


def r_p10_pivots(h: float, l: float, c: float, rth_open: float | None = None, rth_high: float | None = None) -> dict:
    p = daily_floor_pivots(h, l, c)
    ctx = None
    if rth_open is not None:
        if rth_open > h:
            ctx = "ABOVE_PREV_HIGH"
        elif rth_open < l:
            ctx = "BELOW_PREV_LOW"
        else:
            ctx = "WITHIN"
    pp_touch = rth_high is not None and rth_high >= p["P"]
    p["context"] = ctx
    p["pp_touch"] = bool(pp_touch) if rth_high is not None else None
    return p


def r_p11_first_fvg(
    highs, lows, closes, hours, *, later_low=None, hour_open=None, hour_close=None, window="W1",
) -> dict:
    h, l, c, hr = _arr(highs), _arr(lows), _arr(closes), _arr(hours)
    found = None
    box = None
    for i in range(2, h.size):
        if l[i] > h[i - 2] and c[i] > h[i - 2] and int(hr[i - 1]) == int(hr[i]):
            found = "BISI"
            box = [float(h[i - 2]), float(l[i])]
            break
        if h[i] < l[i - 2] and c[i] < l[i - 2] and int(hr[i - 1]) == int(hr[i]):
            found = "SIBI"
            box = [float(h[i]), float(l[i - 2])]
            break
    direction_ok = None
    if found == "BISI" and hour_open is not None and hour_close is not None:
        direction_ok = hour_close > hour_open
    if found == "SIBI" and hour_open is not None and hour_close is not None:
        direction_ok = hour_close < hour_open
    fill = False
    if box is not None and later_low is not None and found == "BISI":
        fill = later_low <= box[1]
    if box is not None and later_low is not None and found == "SIBI":
        fill = later_low >= box[0]
    key = "w1_fvg" if window == "W1" else "w2_fvg"
    return {key: found, "box": box, "direction_ok": direction_ok, "near_edge_fill": bool(fill)}


def r_p12_sweep_cisd(
    *, prev_h: float, prev_l: float, prev_o: float, prev_c: float,
    o: float, h: float, l: float, c: float,
) -> dict:
    sweep_close = h > prev_h and c < prev_h
    sweep_body = h > prev_h and max(o, c) < prev_h
    sweep_inside = sweep_close and c > prev_l
    prev_mid = 0.5 * (prev_o + prev_c)
    box = [min(prev_mid, o), max(prev_mid, o)]
    return {
        "sweep_close": bool(sweep_close),
        "sweep_body": bool(sweep_body),
        "sweep_inside": bool(sweep_inside),
        "mid_box": box,
    }


def r_p14_hod_checkpoint(candles: list[tuple[str, float]], *, hod: float, hod_at: str, checkpoint: str) -> dict:
    highs = [c[1] for c in candles]
    names = [c[0] for c in candles]
    elims = 0
    hod_i = 0
    elim_had_pred = False
    for i in range(1, len(highs)):
        if highs[i] > highs[hod_i]:
            if hod_i > 0:
                elim_had_pred = True
            elims += 1
            hod_i = i
    structure = "skip" if elim_had_pred else "sequential"
    prev_survived = hod_i == len(highs) - 1
    return {
        "elims": elims,
        "structure": structure,
        "prev_survived": prev_survived,
        "hod_in_by_10am": hod_at in names,
        "hod": hod,
        "checkpoint": checkpoint,
    }


def nearest_rank(values, pct: float) -> float:
    a = np.sort(_arr(values))
    n = a.size
    k = max(1, int(math.ceil(pct / 100.0 * n)))
    return float(a[min(k, n) - 1])


def r_p15_ssl(
    *, open_px: float, p_rng: float, p_mfe: float, p_mae: float, session_high: float, session_low: float,
) -> dict:
    rng_hi, rng_lo = open_px + p_rng, open_px - p_rng
    mfe_lv, mae_lv = open_px + p_mfe, open_px - p_mae
    return {
        "rng_hi": rng_hi,
        "rng_lo": rng_lo,
        "mfe_lv": mfe_lv,
        "mae_lv": mae_lv,
        "mfe_p50_hit": session_high >= mfe_lv,
        "rng_p50_hit": session_high >= rng_hi or session_low <= rng_lo,
    }


def r_p15_srp(box_h: float, box_l: float, k_up: int, k_dn: int) -> dict:
    w = box_h - box_l
    return {f"RE+{k_up}": box_h + k_up * w, f"RE-{k_dn}": box_l - k_dn * w}


def r_p15_ohlc_md(o: float, h: float, l: float, c: float) -> dict:
    bull = c >= o
    if bull:
        manip = o - l
        dist = h - o
    else:
        manip = h - o
        dist = o - l
    return {"manipulation": manip, "distribution": dist, "bull": bool(bull)}


def r_p17_bar_vol(o: float, h: float, l: float, c: float, v: float, row: float = TICK) -> dict:
    body = abs(c - o)
    topw = h - max(o, c)
    botw = min(o, c) - l
    denom = body + 2 * topw + 2 * botw
    bodyvol = v * body / denom if denom else 0.0
    topwvol = v * 2 * topw / denom if denom else 0.0
    botwvol = v * 2 * botw / denom if denom else 0.0
    n_body = int(round(body / row)) if body > 0 else 0
    n_bot = int(round(botw / row)) if botw > 0 else 0
    n_top = int(round(topw / row)) if topw > 0 else 0
    return {
        "body": body,
        "topwick": topw,
        "bottomwick": botw,
        "denom": denom,
        "bodyvol": bodyvol,
        "topwvol": topwvol,
        "botwvol": botwvol,
        "body_up": bodyvol if c >= o else 0.0,
        "n_body": n_body,
        "n_bot": n_bot,
        "n_top": n_top,
        "body_per_row": bodyvol / n_body if n_body else 0.0,
        "bot_per_row": botwvol / n_bot if n_bot else 0.0,
    }


def r_p19_body_gap(o, h, l, c, *, min_ticks: int = 4, later_low=None, later_high=None, level_8020: float | None = None) -> dict:
    o, h, l, c = _arr(o), _arr(h), _arr(l), _arr(c)
    if o.size < 2:
        return {"gap": False}
    hi_body = np.maximum(o, c)
    lo_body = np.minimum(o, c)
    up = lo_body[1] - hi_body[0]
    dn = lo_body[0] - hi_body[1]
    if up >= min_ticks * TICK:
        zone = [float(hi_body[0]), float(lo_body[1])]
        filled = False
        if later_low is not None:
            filled = float(np.min(_arr(later_low))) <= zone[1]
        conf = False
        if level_8020 is not None:
            conf = min(abs(zone[0] - level_8020), abs(zone[1] - level_8020)) <= 8 * TICK
        return {"gap": True, "side": "up", "zone": zone, "filled": bool(filled), "conf": bool(conf)}
    if dn >= min_ticks * TICK:
        zone = [float(hi_body[1]), float(lo_body[0])]
        filled = later_high is not None and float(np.max(_arr(later_high))) >= zone[0]
        return {"gap": True, "side": "down", "zone": zone, "filled": bool(filled), "conf": False}
    return {"gap": False, "filled": False, "conf": False}


def r_p20_mvfl(
    *, sub_deltas: list[float], sma50_abs: float, close: float,
    volume: float | None = None, sma20_vol: float | None = None,
    prior_close: float | None = None, vote_close: float | None = None, level: float | None = None,
) -> dict:
    d = float(sum(sub_deltas))
    thr = max(6 * sma50_abs, 3000.0)
    sig = abs(d) > thr
    side = "bull" if d > 0 else "bear"
    zone = None
    if volume is not None and sma20_vol is not None and volume > 2.5 * sma20_vol:
        pad = 0.002 * close
        zone = [close - pad, close + pad]
    c4 = 0
    if level is not None and vote_close is not None and prior_close is not None:
        if vote_close > level and prior_close <= level:
            c4 = 1
        elif vote_close < level and prior_close >= level:
            c4 = -1
    return {
        "delta": d,
        "threshold": thr,
        "sigEvent": int(bool(sig)),
        "side": side if sig else None,
        "vol_zone": zone,
        "c4dir": c4,
        "close": close,
    }


def p3_14_level_tied(
    *, level: float, fvg_box: list[float] | None = None, fvg_fill_px: float | None = None,
    body_zone: list[float] | None = None, body_fill_px: float | None = None,
    sweep_px: float | None = None, sweep_close: float | None = None,
    cisd_close: float | None = None, tpo_rows: list[float] | None = None, tpo_touch: float | None = None,
) -> dict:
    t2 = 2 * TICK
    fvg_at = fvg_box is not None and any(abs(level - x) <= t2 for x in fvg_box)
    fvg_fill = False
    if fvg_at and fvg_fill_px is not None:
        lo, hi = min(fvg_box), max(fvg_box)
        fvg_fill = lo - t2 <= fvg_fill_px <= hi + t2
    body_at = body_zone is not None and any(abs(level - x) <= t2 for x in body_zone)
    body_fill = False
    if body_at and body_fill_px is not None:
        body_fill = body_fill_px <= max(body_zone) + t2
    sweep_at = sweep_px is not None and abs(sweep_px - level) <= t2
    sweep_conf = sweep_at and sweep_close is not None and (
        sweep_close > sweep_px if sweep_px <= level else sweep_close < sweep_px
    )
    cisd_at = cisd_close is not None and (
        (cisd_close < level and sweep_px is not None and sweep_px >= level) or
        (cisd_close > level and sweep_px is not None and sweep_px <= level)
    )
    tpo_at = tpo_rows is not None and any(abs(level - r) <= t2 for r in tpo_rows)
    tpo_fill = tpo_at and tpo_touch is not None and min(tpo_rows) - t2 <= tpo_touch <= max(tpo_rows) + t2
    return {
        "fvg_at_level": bool(fvg_at),
        "fvg_fill": bool(fvg_fill),
        "body_at_level": bool(body_at),
        "body_fill": bool(body_fill),
        "sweep_at_level": bool(sweep_at),
        "sweep_confirm": bool(sweep_conf),
        "cisd_at_level": bool(cisd_at),
        "tpo_at_level": bool(tpo_at),
        "tpo_fill": bool(tpo_fill),
    }


def _case(cid: str, ok: bool, got, expected) -> dict:
    return {"id": cid, "pass": bool(ok), "got": _py(got) if not isinstance(got, (dict, list, tuple)) else got, "expected": expected}


def flow_fixtures() -> dict:
    cases: list[dict] = []

    vw, sg = running_vwap([100.0, 100.0], [100.0, 100.0], [100.0, 100.0], [10.0, 10.0])
    cases.append(_case("R-F01.running_vwap", abs(float(vw[-1]) - 100.0) < 1e-12 and abs(float(sg[-1])) < 1e-12, float(vw[-1]), 100.0))
    lo, hi = vwap_band(100.0, 2.0, 2.0)
    cases.append(_case("R-F01.band", abs(hi - 104.0) < 1e-12, hi, 104.0))
    px = np.array([104.00, 104.25, 104.50])
    sz = np.array([1200.0, 1300.0, 1200.0])
    sd = np.array([1, 1, 1])
    tm = np.array([0.0, 30_000.0, 90_000.0])
    a = absorption_a_at_level(
        px, sz, sd, tm, level=104.0, t0=-1, t1=120_000, toward=1,
        vol_cut=ABS_Q90_BUY, r_width=4.0, reversal_px=99.9, tick_tol=2 * TICK,
    )
    f01 = r_f01_vwap_fade(
        100.0, 2.0, bar_high=104.25, bar_low=103.8, abs_result=a, later_low=99.9, later_high=104.0,
    )
    cases.append(_case("R-F01.absorption_A_at_band", f01["absorption_A_at_band"] is True, f01["absorption_A_at_band"], True))
    cases.append(_case("R-F01.median_reach_60", f01["median_reach_60"] is True, f01["median_reach_60"], True))
    cases.append(_case("R-F01.vol_cut", abs(a["vol"] - 3700) < 1e-9, a["vol"], 3700.0))

    f03 = r_f03_convergence(100.20, 100.35, 100.10, 6.0, touch_px=100.0, close=101.5, sigma=2.0)
    cases.append(_case("R-F03.convergence", f03["convergence"] is True, f03["convergence"], True))
    cases.append(_case("R-F03.reject", f03["reject"] is True, f03["reject"], True))

    ask = {100.00: 40.0, 100.25: 36.0, 100.50: 44.0, 100.75: 12.0}
    bid = {100.00: 5.0, 100.25: 8.0, 100.50: 9.0, 100.75: 30.0}
    s4 = r_f04_candle_stack(ask, bid, k=4.0)
    s3 = r_f04_candle_stack(ask, bid, k=3.0)
    cases.append(_case("R-F04.stack3_k4", s4["stack3"] is False, s4["stack3"], False))
    cases.append(_case("R-F04.stack3_k3", s3["stack3"] is False, s3["stack3"], False))
    ask2 = {99.75: 0.0, 100.00: 40.0, 100.25: 40.0, 100.50: 40.0}
    bid2 = {99.75: 5.0, 100.00: 5.0, 100.25: 5.0, 100.50: 5.0}
    s2 = r_f04_candle_stack(ask2, bid2, k=4.0)
    cases.append(_case("R-F04.stack3_second", s2["stack3"] is True and s2["zone"] == [100.00, 100.50], s2["zone"], [100.00, 100.50]))
    rh = r_f04_revisit_hold(s2["zone"], 1, 100.5, 103.0)
    cases.append(_case("R-F04.revisit_hold", rh["revisit_hold"] is True, rh["revisit_hold"], True))

    f05 = r_f05_absorption_stack(
        100.25, 100.75, -180.0, 100.25, 100.0, 101.0,
        next_poc=100.9, next_low=100.0, next_high=101.0,
        later_close=105.5, r_width=20.0,
    )
    cases.append(_case("R-F05.disagree_bull", f05["disagree_bull"] is True, f05["disagree_bull"], True))
    cases.append(_case("R-F05.poc_flip", f05["poc_flip"] is True, f05["poc_flip"], True))
    cases.append(_case("R-F05.reversal", f05["reversal"] is True, f05["reversal"], True))

    pdl = 16622.5
    rth_r = 251.0
    px = np.array([16622.75, 16622.5, 16622.0])
    sz = np.array([1200.0, 1200.0, 1200.0])
    sd = np.array([-1, -1, -1])
    tm = np.array([0.0, 30_000.0, 90_000.0])
    f06a = r_f06_dom_absorption(
        px, sz, sd, tm, level=pdl, t0=-1, t1=120_000, toward=-1,
        r_width=rth_r, reversal_px=16640.0, prior_vol=4100.0,
    )
    cases.append(_case("R-F06.absorption_A_pdl_0", f06a["absorption_A"] is False, f06a["absorption_A"], False))
    f06b = r_f06_dom_absorption(
        px, sz, sd, tm, level=pdl, t0=-1, t1=120_000, toward=-1,
        r_width=rth_r, reversal_px=16690.0, prior_vol=4100.0,
    )
    cases.append(_case("R-F06.absorption_A_pdl_1", f06b["absorption_A"] is True, f06b["absorption_A"], True))
    cases.append(_case("R-F06.shrinking", f06a["shrinking"] is True, f06a["shrinking"], True))
    cases.append(_case("R-F06.trapped", f06a["trapped"] is True, f06a["trapped"], True))

    f08 = r_f08_abs_four_check(
        level=120.0, kind="vah", poc=112.0, va_height=20.0,
        absorption_px=120.25, path=[120.25, 120.00, 119.75, 119.50], direction=-1,
        second_vol=2900.0, q75=2600.0, n_abs=100, n_fail_no_reward=27,
    )
    cases.append(_case("R-F08.reward_3tick", f08["reward_3tick"] is True, f08["reward_3tick"], True))
    cases.append(_case("R-F08.second_aggression", f08["second_aggression"] is True, f08["second_aggression"], True))
    cases.append(_case("R-F08.fail_share", abs(f08["fail_share"] - 0.27) < 1e-12, f08["fail_share"], 0.27))
    cases.append(_case("R-F08.cvd_median_blocked", f08["cvd_median"] is None, f08["cvd_median"], None))

    s1 = absorption_a_at_level(
        np.array([100.0, 99.75]), np.array([1750.0, 1750.0]), np.array([-1, -1]), np.array([0.0, 10_000.0]),
        level=100.0, t0=-1, t1=20_000, toward=-1, vol_cut=ABS_Q90_SELL, r_width=20.0, reversal_px=105.0,
    )
    f09 = r_f09_stop_stages(
        stage1=s1, last20_median=4.0, earlier_median=15.0, bar_delta=120.0, toward=-1,
        last_prices=[100.00, 100.25, 100.50, 100.75],
    )
    cases.append(_case("R-F09.stage1", f09["stage1"] is True, f09["stage1"], True))
    cases.append(_case("R-F09.stage2_blocked", f09["stage2"] is None, f09["stage2"], None))
    cases.append(_case("R-F09.stage3", f09["stage3"] is True, f09["stage3"], True))
    cases.append(_case("R-F09.liftoff", f09["liftoff"] is True, f09["liftoff"], True))
    cases.append(_case("R-F09.entry", f09["entry_window"] == [100.75, 101.25], f09["entry_window"], [100.75, 101.25]))

    lows = np.zeros(45)
    highs = np.full(45, 103.0)
    closes = np.full(45, 101.0)
    lows[2:7] = [101.0, 100.5, 100.0, 100.5, 101.0]
    highs[17] = 102.4
    closes[17] = 102.25
    lows[18:23] = 100.75
    highs[:41] = np.maximum(highs[:41], 104.5)
    highs[12] = 104.5
    closes[41] = 99.75
    lows[41] = 99.5
    f10 = r_f10_protected_low(
        lows, highs, closes, fractal_i=4, delta_at=260.0, q75=200.0,
        prior_swing_high=102.0, escape_i=17, break_i=41, mfe_high=104.5,
    )
    cases.append(_case("R-F10.protected_low", f10["protected_low"] == 100.0, f10["protected_low"], 100.0))
    cases.append(_case("R-F10.broken", f10["broken"] is True, f10["broken"], True))
    cases.append(_case("R-F10.mfe", abs(f10["mfe"] - 4.5) < 1e-12, f10["mfe"], 4.5))

    f11 = r_f11_delta_lvn(
        band_lo=100.0, band_hi=120.0, lvn=118.5, dp=118.25,
        touches=[
            {"h": 118.75, "l": 117.0, "c": 117.5},
            {"h": 118.75, "l": 117.0, "c": 117.5},
        ],
    )
    cases.append(_case("R-F11.paired", f11["paired"] is True, f11["paired"], True))
    cases.append(_case("R-F11.wick_reaction", f11["wick_reaction"] is True, f11["wick_reaction"], True))
    cases.append(_case("R-F11.reaction", f11["reaction"] is False, f11["reaction"], False))
    cases.append(_case("R-F11.repeat_count", f11["repeat_count"] == 2, f11["repeat_count"], 2))

    f12 = r_f12_arrival(
        [116.0, 117.0, 118.2, 119.1, 119.9], [400, 450, 520, 600, 640],
        q75_disp=2.5, later_close=121.5, level=120.0, held_30=True,
    )
    cases.append(_case("R-F12.arrival", f12["arrival"] == "aggressive", f12["arrival"], "aggressive"))
    cases.append(_case("R-F12.broken", f12["broken"] is True and f12["defended"] is False, [f12["broken"], f12["defended"]], [True, False]))

    f13 = r_f13_trapped_buyers(
        band_high=110.0, dp_max=109.75, tR=0.5, am_high=109.9, pm_high=110.0,
        any_close_above=False, intra_lo=104.0, intra_hi=108.0,
        break_close=103.5, retest_high=104.0, sell_in_body=True,
        body=(103.6, 103.9), reject_close=101.75,
    )
    cases.append(_case("R-F13.two_failures", f13["two_failures"] is True, f13["two_failures"], True))
    cases.append(_case("R-F13.retest_hold", f13["retest_hold"] is True, f13["retest_hold"], True))

    f14 = r_f14_imb350(
        101.0, 101.75, 100.0, 100.25,
        [(100.10, 45.0, -1), (100.5, 40.0, -1)],
        {100.5: 110.0, 100.10: 10.0},
        {100.5: 420.0, 100.10: 45.0},
        retest_high=100.5, retest_close=99.6,
    )
    cases.append(_case("R-F14.zone", f14["imb350_zone"] == 100.5, f14["imb350_zone"], 100.5))
    cases.append(_case("R-F14.retest_reject", f14["retest_reject"] is True, f14["retest_reject"], True))

    f15 = r_f15_ofm(
        swing=110.0, r_height=20.0,
        wick_prints=[(109.75, 40.0, 10.02), (109.9, 35.0, 10.05)],
        release_close=110.5, tape_pps=12.0, tape_cut=11.0,
        fail_close=109.25, refill_touch=109.75,
        resqueeze_close=110.75, fail_wick=110.6, stop=109.5,
        later_high=112.25,
    )
    cases.append(_case("R-F15.catalyst", f15["catalyst"] == [109.75, 110.0], f15["catalyst"], [109.75, 110.0]))
    cases.append(_case("R-F15.ofm_entry", f15["ofm_entry"] is True, f15["ofm_entry"], True))
    cases.append(_case("R-F15.R", abs(f15["R"] - 1.25) < 1e-12, f15["R"], 1.25))
    cases.append(_case("R-F15.reach", f15["reach_1R"] is True and f15["reach_2R"] is False, [f15["reach_1R"], f15["reach_2R"]], [True, False]))
    cases.append(_case("R-F15.gamma", f15["gamma"] is None, f15["gamma"], None))

    f16 = r_f16_balance_fade(
        range_lo=100.0, range_hi=120.0, wick_ok=True, no_close_beyond=True,
        left_px=114.0, test_high=120.0, abs_ok=True, target=112.5, later_low=112.25,
        day_label="normal",
    )
    cases.append(_case("R-F16.fade_trigger", f16["fade_trigger"] is True, f16["fade_trigger"], True))
    cases.append(_case("R-F16.target_reach", f16["target_reach"] is True, f16["target_reach"], True))
    cases.append(_case("R-F16.gamma", f16["gamma"] is None, f16["gamma"], None))

    f17 = r_f17_refill_zone(
        [(0.0, 100.25, 65.0, -1), (4000.0, 100.00, 80.0, -1), (12000.0, 100.25, 70.0, -1)],
        leave_px=101.5, touch_px=100.25, deepest=99.50, later_extreme=103.25, close_beyond=False,
    )
    cases.append(_case("R-F17.zone", f17["zone"] == [100.00, 100.25], f17["zone"], [100.00, 100.25]))
    cases.append(_case("R-F17.hold", f17["hold"] is True, f17["hold"], True))
    cases.append(_case("R-F17.penetration", abs(f17["penetration"] - 2.0) < 1e-12, f17["penetration"], 2.0))

    f18 = r_f18_squeeze(
        catalyst=[89.75, 90.0], release_close=89.25, tape_pps=14.0, tape_cut=11.0,
        any_close_through=False, trigger_abs=True, next_level=84.0, later_touch=84.0,
    )
    cases.append(_case("R-F18.no_failure", f18["no_failure"] is True, f18["no_failure"], True))
    cases.append(_case("R-F18.trigger", f18["trigger"] is True, f18["trigger"], True))
    cases.append(_case("R-F18.continuation", f18["continuation"] is True, f18["continuation"], True))
    cases.append(_case("R-F18.tape_cut_source", f18["tape_cut_source"] == "unspecified", f18["tape_cut_source"], "unspecified"))
    ts = tape_speed_pps(np.linspace(0, 29_000, 420), 30_000, 30.0)
    cases.append(_case("R-F18.tape_window_30s", abs(ts - 14.0) < 0.05, ts, 14.0))

    r03 = r_r03_thesis(
        val=16685.0, vah=16779.75, open_px=16610.0, am_high=16649.75, am_low=16598.0,
        any_close_beyond=False, news=False, eval_min=12 * 60,
    )
    cases.append(_case("R-R03.label", r03["label"] == "short", r03["label"], "short"))
    cases.append(_case("R-R03.edge", abs(r03["band_edge"] - 16685.0) < 1e-12, r03["band_edge"], 16685.0))
    cases.append(_case("R-R03.end", r03["end"] >= 12 * 60, r03["end"], ">= 12:00"))
    cases.append(_case("R-R03.alive", r03["alive_min"] >= 150, r03["alive_min"], ">= 150"))

    s01 = r_s01_refill_long(
        range_low=100.0, abs_ok=True, min_print=99.75, close_above=100.75,
        objective=108.0, later_high=108.0, later_low=100.25,
    )
    cases.append(_case("R-S01.refill_long", s01["refill_long"] is True, s01["refill_long"], True))
    cases.append(_case("R-S01.inval_dist", abs(s01["inval_dist"] - 1.5) < 1e-12, s01["inval_dist"], 1.5))
    cases.append(_case("R-S01.objective_reach", s01["objective_reach"] is True, s01["objective_reach"], True))
    cases.append(_case("R-S01.mfe", abs(s01["mfe"] - 7.25) < 1e-12, s01["mfe"], 7.25))
    cases.append(_case("R-S01.mae", abs(s01["mae"] - 0.5) < 1e-12, s01["mae"], 0.5))

    s02 = r_s02_third_retest(
        [115.5, 115.5, 111.25], [110.0, 109.75, 110.0], [1200.0, 1500.0, 1300.0],
        level=110.0, r_width=20.0, band_lo=109.75, band_hi=110.25,
        later_close=110.75, later_high=111.25, from_above=True,
    )
    cases.append(_case("R-S02.third", s02["third_test_short"] is True, s02["third_test_short"], True))
    cases.append(_case("R-S02.loss", s02["loss_case"] is True, s02["loss_case"], True))
    cases.append(_case("R-S02.mae", abs(s02["mae"] - 1.5) < 1e-12, s02["mae"], 1.5))

    s03 = r_s03_second_defence(
        level=100.0, break_close=99.0, retest_high=100.0, sell_vol=2800.0, q75=2600.0,
        print_sizes=[45, 42, 40, 44], later_low=94.5, r_width=20.0,
    )
    cases.append(_case("R-S03.steady", s03["steady"] is True, s03["steady"], True))
    cases.append(_case("R-S03.second_defence", s03["second_defence"] is True, s03["second_defence"], True))
    cases.append(_case("R-S03.reversal", s03["reversal"] is True, s03["reversal"], True))
    cases.append(_case("R-S03.reload_blocked", s03["reload"] is None, s03["reload"], None))

    s04 = r_s04_ath_ofm(
        weekly_high=120.0, dp_min=118.5, tR=1.5, left_px=110.0, r_height=20.0, prior_high=112.0,
        touches=2, no_close_below=True, imb350_buy=True, micro_hi=119.0,
        break_close=119.25, next_level=124.0, later_high=124.0,
    )
    cases.append(_case("R-S04.trapped", s04["trapped_sellers"] is True, s04["trapped_sellers"], True))
    cases.append(_case("R-S04.failures", s04["failures"] == 2, s04["failures"], 2))
    cases.append(_case("R-S04.ofm_long", s04["ofm_long"] is True, s04["ofm_long"], True))
    cases.append(_case("R-S04.continuation", s04["continuation"] is True, s04["continuation"], True))

    s05 = r_s05_microbalance(
        [105.0, 105.5, 104.75, 105.25, 105.75, 105.0],
        [104.7, 105.2, 104.5, 105.0, 105.4, 104.8],
        [105.2, 105.7, 105.0, 105.5, 106.0, 105.3],
        r_height=20.0, break_close=106.5, htf=110.0, later_high=110.0, later_low=106.0,
    )
    cases.append(_case("R-S05.box", s05["box"] == [104.5, 106.0], s05["box"], [104.5, 106.0]))
    cases.append(_case("R-S05.breakout", s05["breakout_long"] is True, s05["breakout_long"], True))
    cases.append(_case("R-S05.inval", abs(s05["inval"] - 104.0) < 1e-12, s05["inval"], 104.0))
    cases.append(_case("R-S05.htf", s05["htf_reach"] is True, s05["htf_reach"], True))

    s06 = r_s06_two_reason(
        swing_high=110.0, prior_reject=6.0, r_width=20.0, hvn=110.25, tR=1.0,
        touch_high=110.25, reject_close=99.75, entry=110.0,
    )
    cases.append(_case("R-S06.two_reason", s06["two_reason"] is True, s06["two_reason"], True))
    cases.append(_case("R-S06.reject", s06["reject"] is True, s06["reject"], True))
    cases.append(_case("R-S06.r15", s06["r15_reach"] is True, s06["r15_reach"], True))

    s07 = r_s07_areas(trigger_close=100.5, later_high=112.0, later_low=99.0)
    cases.append(_case("R-S07.mfe_ticks", abs(s07["mfe_ticks"] - 46.0) < 1e-12, s07["mfe_ticks"], 46.0))
    cases.append(_case("R-S07.mae_ticks", abs(s07["mae_ticks"] - 6.0) < 1e-12, s07["mae_ticks"], 6.0))
    cases.append(_case("R-S07.win_35_188", s07["win_35_188"] is False, s07["win_35_188"], False))

    s08 = r_s08_minor_node(
        hvn=119.75, balance_top=120.0, prior_rej=2, deltas=[-140, -210, -180],
        touch=120.0, reject_close=109.5, r_width=20.0, lvn=104.0, lvn_closes=[103.5, 102.0],
    )
    cases.append(_case("R-S08.setup", s08["node_setup"] is True, s08["node_setup"], True))
    cases.append(_case("R-S08.reject", s08["reject"] is True, s08["reject"], True))
    cases.append(_case("R-S08.slice", s08["slice"] is True, s08["slice"], True))

    s09 = r_s09_open_above_value(
        a_low=24150.0, prior_vah=24142.25, dev_vah=24210.0, va_height=18.0,
        break_close=24212.0, stack3=True, retest_low=24210.25, retest_close=24221.0,
    )
    cases.append(_case("R-S09.open_above", s09["open_above_value"] is True, s09["open_above_value"], True))
    cases.append(_case("R-S09.retest_hold", s09["retest_hold"] is True, s09["retest_hold"], True))
    dva = developing_va({400: 10.0, 401: 80.0, 402: 10.0})
    cases.append(_case("R-S09.developing_va", abs(dva["poc"] - 100.25) < 1e-12, dva["poc"], 100.25))

    chg = np.linspace(-1, 1, 20)
    chg = chg * (1.20 / sample_stdev(chg))
    sig = sample_stdev(chg)
    bands = r_p01_sigma_bands(16600.0, 1.20)
    cases.append(_case("R-P01.sample_stdev", abs(sig - 1.20) < 1e-12, sig, 1.20))
    cases.append(_case("R-P01.sigma_px", abs(bands["sigma_px"] - 199.2) < 1e-9, bands["sigma_px"], 199.2))
    cases.append(_case("R-P01.upper", abs(bands["upper"] - 16649.8) < 1e-9, bands["upper"], 16649.8))
    p01 = r_p01_touch_revert(
        16600.0, bands["upper"], bands["lower"], bands["sigma_px"],
        [8, 8, 9], [16620.0, 16650.25, 16610.0], [16590.0, 16640.0, 16598.0],
    )
    cases.append(_case("R-P01.reverted", p01["reverted"] is True and p01["milestone"] == "by10", p01["milestone"], "by10"))
    cases.append(_case("R-P01.ext", abs(p01["ext_max"] - 0.25225806451612903) < 0.01 or abs(p01["ext_max"] - 0.25) < 0.01, round(p01["ext_max"], 2), 0.25))

    p02 = r_p02_hourly_sweep(
        prev_h=16660.0, prev_l=16640.0, prev_open=16645.0, hour_open=16655.0,
        highs=[16650, 16668, 16662, 16658],
        lows=[16648, 16652, 16659, 16649],
    )
    cases.append(_case("R-P02.isAbove", p02["isAbove"] == 1, p02["isAbove"], 1))
    cases.append(_case("R-P02.ret_swept", p02["high_ret_swept"] is True, p02["high_ret_swept"], True))
    cases.append(_case("R-P02.ret_50", p02["high_ret_50"] is True, p02["high_ret_50"], True))
    cases.append(_case("R-P02.ret_open", p02["high_ret_open"] is True, p02["high_ret_open"], True))
    cases.append(_case("R-P02.ret_opp", p02["high_ret_opp"] is False, p02["high_ret_opp"], False))

    p03 = r_p03_magic_hour(
        hour=7, box_h=16700.0, box_l=16680.0, break_side="low", excursion=6.0,
        later_high=16690.25, later_low=16674.0, t_break_min=8 * 60 + 4, t_target_min=8 * 60 + 22,
    )
    cases.append(_case("R-P03.zone", p03["zone"] == "Z2", p03["zone"], "Z2"))
    cases.append(_case("R-P03.win", p03["win"] is True, p03["win"], True))
    cases.append(_case("R-P03.ttt", abs(p03["ttt_min"] - 18) < 1e-12, p03["ttt_min"], 18))

    p04 = r_p04_raid(
        box_h=16660.0, box_l=16640.0,
        highs=[16650, 16666.5, 16671, 16658],
        lows=[16645, 16655, 16650, 16640],
        closes=[16648, 16664, 16668, 16659.75],
        t_min=[9 * 60 + 20, 9 * 60 + 41, 9 * 60 + 55, 10 * 60 + 2],
        cutoff_min=11 * 60 + 15,
    )
    cases.append(_case("R-P04.conf", p04["raid_hi_conf"] is True, p04["raid_hi_conf"], True))
    cases.append(_case("R-P04.pts", abs(p04["raid_pts"] - 11.0) < 1e-12, p04["raid_pts"], 11.0))
    cases.append(_case("R-P04.bucket", p04["bucket"] == "<20", p04["bucket"], "<20"))

    p05a = r_p05_london_25(16600.0, 16640.0, 16625.0, 16660.0, 16650.0)
    p05b = r_p05_london_25(16600.0, 16640.0, 16635.0, 16660.0, 16650.0)
    cases.append(_case("R-P05.level", abs(p05a["level"] - 16630.0) < 1e-12, p05a["level"], 16630.0))
    cases.append(_case("R-P05.wick", p05a["wick_lon25_bull"] is True, p05a["wick_lon25_bull"], True))
    cases.append(_case("R-P05.above", p05b["above_lon25"] is True, p05b["above_lon25"], True))

    p06 = r_p06_first_hit(
        asia_h=16720.0, asia_l=16690.0, lon_open=16712.0,
        lon_highs=[16700, 16721, 16710],
        lon_lows=[16700, 16705, 16689],
    )
    cases.append(_case("R-P06.first", p06["london_first_hit"] == "asia_high", p06["london_first_hit"], "asia_high"))
    cases.append(_case("R-P06.seq", p06["sequential"] == 1, p06["sequential"], 1))

    p07 = r_p07_or_mid(
        o=16600.0, h=16608.0, l=16598.0, c=16606.0,
        later_h=[16600, 16604], later_l=[16597, 16602], later_c=[16599, 16603],
    )
    cases.append(_case("R-P07.mid", abs(p07["mid"] - 16603.0) < 1e-12, p07["mid"], 16603.0))
    cases.append(_case("R-P07.extreme", p07["extreme_first"] == "low", p07["extreme_first"], "low"))
    cases.append(_case("R-P07.retest", p07["mid_retest"] is True, p07["mid_retest"], True))
    cases.append(_case("R-P07.ext", abs(p07["ext_up"] - 16608.0 * 1.00411) < 1e-9, p07["ext_up"], 16608.0 * 1.00411))

    p09 = r_p09_no_break(16610.0, 16873.5, 16622.5, 16649.75, 16598.0)
    cases.append(_case("R-P09.status", p09["status"] == "Below", p09["status"], "Below"))
    cases.append(_case("R-P09.no_break", p09["no_break_prev_high"] is True, p09["no_break_prev_high"], True))

    p10 = r_p10_pivots(16873.5, 16598.0, 16650.0, rth_open=16610.0, rth_high=16649.75)
    cases.append(_case("R-P10.P", abs(p10["P"] - 16707.166666666668) < 0.01, round(p10["P"], 2), 16707.17))
    cases.append(_case("R-P10.R1", abs(p10["R1"] - 16816.33) < 0.01, round(p10["R1"], 2), 16816.33))
    cases.append(_case("R-P10.S1", abs(p10["S1"] - 16540.83) < 0.01, round(p10["S1"], 2), 16540.83))
    cases.append(_case("R-P10.R2", abs(p10["R2"] - 16982.67) < 0.01, round(p10["R2"], 2), 16982.67))
    cases.append(_case("R-P10.S2", abs(p10["S2"] - 16431.67) < 0.01, round(p10["S2"], 2), 16431.67))
    # printed R3 17148.83 contradicts _r3 = H + 2*(PP-L) = 17091.83
    cases.append(_case("R-P10.R3", abs(p10["R3"] - 17091.83) < 0.01, round(p10["R3"], 2), 17091.83))
    cases.append(_case("R-P10.S3", abs(p10["S3"] - 16265.33) < 0.01, round(p10["S3"], 2), 16265.33))
    cases.append(_case("R-P10.context", p10["context"] == "WITHIN", p10["context"], "WITHIN"))

    p11 = r_p11_first_fvg(
        [16612, 16613, 16620], [16600, 16605, 16615], [16610, 16612, 16619], [9, 9, 9],
        later_low=16615.0, hour_open=16610.0, hour_close=16630.0,
    )
    cases.append(_case("R-P11.w1", p11["w1_fvg"] == "BISI", p11["w1_fvg"], "BISI"))
    cases.append(_case("R-P11.box", p11["box"] == [16612.0, 16615.0], p11["box"], [16612.0, 16615.0]))
    cases.append(_case("R-P11.dir", p11["direction_ok"] is True, p11["direction_ok"], True))
    cases.append(_case("R-P11.fill", p11["near_edge_fill"] is True, p11["near_edge_fill"], True))

    p12 = r_p12_sweep_cisd(
        prev_h=16660.0, prev_l=16640.0, prev_o=16644.0, prev_c=16660.0,
        o=16650.0, h=16663.0, l=16648.0, c=16655.0,
    )
    cases.append(_case("R-P12.sweep_close", p12["sweep_close"] is True, p12["sweep_close"], True))
    cases.append(_case("R-P12.sweep_body", p12["sweep_body"] is True, p12["sweep_body"], True))
    cases.append(_case("R-P12.sweep_inside", p12["sweep_inside"] is True, p12["sweep_inside"], True))
    cases.append(_case("R-P12.mid_box", p12["mid_box"] == [16650.0, 16652.0], p12["mid_box"], [16650.0, 16652.0]))

    p14 = r_p14_hod_checkpoint(
        [("6pm", 16700.0), ("10pm", 16690.0), ("2am", 16705.0), ("6am", 16698.0)],
        hod=16705.0, hod_at="2am", checkpoint="10am",
    )
    cases.append(_case("R-P14.elims", p14["elims"] == 1, p14["elims"], 1))
    cases.append(_case("R-P14.structure", p14["structure"] == "sequential", p14["structure"], "sequential"))
    cases.append(_case("R-P14.hod_in", p14["hod_in_by_10am"] is True, p14["hod_in_by_10am"], True))

    cases.append(_case("R-P15.nearest_rank_p50", abs(nearest_rank([85.0] * 60, 50) - 85.0) < 1e-12, nearest_rank([85.0] * 60, 50), 85.0))
    p15 = r_p15_ssl(open_px=16600.0, p_rng=85.0, p_mfe=52.0, p_mae=48.0, session_high=16655.0, session_low=16580.0)
    cases.append(_case("R-P15.mfe_hit", p15["mfe_p50_hit"] is True, p15["mfe_p50_hit"], True))
    cases.append(_case("R-P15.rng_hit", p15["rng_p50_hit"] is False, p15["rng_p50_hit"], False))
    srp = r_p15_srp(16660.0, 16640.0, 1, 2)
    cases.append(_case("R-P15.RE+1", srp["RE+1"] == 16680.0, srp["RE+1"], 16680.0))
    cases.append(_case("R-P15.RE-2", srp["RE-2"] == 16600.0, srp["RE-2"], 16600.0))
    md = r_p15_ohlc_md(16650.0, 16700.0, 16630.0, 16690.0)
    cases.append(_case("R-P15.manip", md["manipulation"] == 20.0, md["manipulation"], 20.0))
    cases.append(_case("R-P15.dist", md["distribution"] == 50.0, md["distribution"], 50.0))

    p17 = r_p17_bar_vol(100.0, 101.0, 99.0, 100.5, 100.0)
    cases.append(_case("R-P17.denom", abs(p17["denom"] - 3.5) < 1e-12, p17["denom"], 3.5))
    cases.append(_case("R-P17.bodyvol", abs(p17["bodyvol"] - 14.285714285714286) < 0.01, round(p17["bodyvol"], 2), 14.29))
    cases.append(_case("R-P17.topw", abs(p17["topwvol"] - 28.57142857142857) < 0.01, round(p17["topwvol"], 2), 28.57))
    cases.append(_case("R-P17.botw", abs(p17["botwvol"] - 57.14285714285714) < 0.01, round(p17["botwvol"], 2), 57.14))
    cases.append(_case("R-P17.body_row", abs(p17["body_per_row"] - 7.14) < 0.02, round(p17["body_per_row"], 2), 7.14))
    cases.append(_case("R-P17.bot_row", abs(p17["bot_per_row"] - 14.29) < 0.02, round(p17["bot_per_row"], 2), 14.29))

    p19 = r_p19_body_gap(
        [100.00, 101.75], [100.6, 102.4], [99.9, 101.7], [100.50, 102.25],
        later_low=[101.5], level_8020=120.0,
    )
    cases.append(_case("R-P19.gap", p19["gap"] is True, p19["gap"], True))
    cases.append(_case("R-P19.zone", p19["zone"] == [100.50, 101.75], p19["zone"], [100.50, 101.75]))
    cases.append(_case("R-P19.filled", p19["filled"] is True, p19["filled"], True))
    cases.append(_case("R-P19.conf", p19["conf"] is False, p19["conf"], False))

    p20 = r_p20_mvfl(
        sub_deltas=[900, 1200, -300, 1500, 800], sma50_abs=550.0, close=16640.0,
        volume=9000.0, sma20_vol=3200.0, prior_close=16638.0, vote_close=16645.0, level=16640.0,
    )
    cases.append(_case("R-P20.sig", p20["sigEvent"] == 1, p20["sigEvent"], 1))
    cases.append(_case("R-P20.delta", p20["delta"] == 4100.0, p20["delta"], 4100.0))
    cases.append(_case(
        "R-P20.zone",
        abs(p20["vol_zone"][0] - 16606.7) < 0.05 and abs(p20["vol_zone"][1] - 16673.3) < 0.05,
        p20["vol_zone"],
        [16606.7, 16673.3],
    ))
    cases.append(_case("R-P20.c4dir", p20["c4dir"] == 1, p20["c4dir"], 1))

    p314 = p3_14_level_tied(
        level=100.0, fvg_box=[99.75, 100.25], fvg_fill_px=100.0,
        body_zone=[100.50, 101.75], body_fill_px=101.5,
        sweep_px=99.75, sweep_close=101.0, cisd_close=99.0,
        tpo_rows=[99.0, 100.0, 101.0], tpo_touch=100.0,
    )
    cases.append(_case("P3-14.fvg_at_level", p314["fvg_at_level"] is True and p314["fvg_fill"] is True, p314["fvg_fill"], True))
    cases.append(_case("P3-14.body_fill", p314["body_fill"] is True, p314["body_fill"], True))
    cases.append(_case("P3-14.sweep_at_level", p314["sweep_at_level"] is True, p314["sweep_at_level"], True))
    cases.append(_case("P3-14.tpo_fill", p314["tpo_fill"] is True, p314["tpo_fill"], True))

    cases.append(_case(
        "R-F02.divergence",
        r_f02_regular_div(110.0, 4200.0, 110.75, 3950.0, side="high") is True,
        True, True,
    ))
    cases.append(_case("R-F02.fakeout_grade", r_f02_fakeout_grade(-80.0) is True, True, True))
    hi = np.array([110.0, 110.75], dtype=np.float64)
    cvd = np.array([4200.0, 3950.0], dtype=np.float64)
    cases.append(_case("R-F02.series", r_f02_div_series(hi, cvd) is True, True, True))
    cases.append(_case(
        "R-F02.at_level",
        r_f02_div_at_level([110.0, 110.75], [4200.0, 3950.0], 110.0, 4200.0, side="high") is True,
        True, True,
    ))
    cases.append(_case(
        "R-F02.grid_window",
        r_f02_grid_div([110.0, 110.75], [4200.0, 3950.0], 0, side="high", horizon=15) is True,
        True, True,
    ))

    p18 = r_p18_ohlc_cvd([100.0, 100.5, 100.25], [100.5, 100.25, 100.25], [120.0, 80.0, 50.0])
    cases.append(_case("R-P18.cvd_ohlc", abs(p18["cvd"] - 40.0) < 1e-12, p18["cvd"], 40.0))

    cases.append(_case(
        "R-R04.smt_pdh",
        r_r04_smt_prior(110.0, 5500.0, 109.5, 5500.5, side="high") is True,
        True, True,
    ))
    cases.append(_case(
        "R-R04.both_take_is_not_smt",
        r_r04_smt_prior(110.0, 5500.0, 110.5, 5500.5, side="high") is False,
        False, False,
    ))

    call_g = r_r01_gex_k(0.08, 10_000.0, 500.0, call=True)
    put_g = r_r01_gex_k(0.07, 12_000.0, 500.0, call=False)
    net = call_g + put_g
    cases.append(_case("R-R01.call_gex", abs(call_g - 2.0e8) < 1e-6, call_g, 2.0e8))
    cases.append(_case("R-R01.put_gex", abs(put_g + 2.1e8) < 1e-6, put_g, -2.1e8))
    cases.append(_case("R-R01.short_gamma", bool(net < 0), True, True))

    failed = [c for c in cases if not c["pass"]]
    return {
        "ticket": "formulas_flow",
        "pass": not failed,
        "n_cases": len(cases),
        "n_failed": len(failed),
        "groups": [{"name": "formulas_flow", "pass": not failed, "cases": cases}],
    }
