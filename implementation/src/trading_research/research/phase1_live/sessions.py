"""Per-session 6-9 box, path class, and width metrics. Reused by later tickets."""

from __future__ import annotations

from datetime import date, time, timedelta

import numpy as np

from trading_research.research.phase1_live import COVERAGE_MAX_MISSING, TICK
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.grid import (
    G_DEFAULT, path_class_from_closes, to_ticks, touch_level,
)
from trading_research.research.phase1_live.ohlc_index import BarIndex

XF_WIDTH_BINS = ((0.0, 0.3), (0.3, 0.5), (0.5, 0.8), (0.8, 1.2), (1.2, None))
REL_BINS = XF_WIDTH_BINS


def _bin_label(lo, hi):
    def fmt(x):
        if x == int(x):
            return str(int(x))
        return str(x)
    if hi is None:
        return f"{fmt(lo)}+"
    return f"{fmt(lo)}-{fmt(hi)}"


def width_bin(value: float | None, bins=XF_WIDTH_BINS) -> str | None:
    if value is None or not np.isfinite(value):
        return None
    for lo, hi in bins:
        if hi is None:
            if value >= lo:
                return _bin_label(lo, hi)
        elif lo <= value < hi:
            return _bin_label(lo, hi)
    return _bin_label(bins[-1][0], bins[-1][1])


def projections(high: float, low: float) -> dict:
    width = high - low
    eq = (high + low) / 2.0
    return {
        "H": high,
        "L": low,
        "W": width,
        "EQ": eq,
        "Q25": low + 0.25 * width,
        "Q75": low + 0.75 * width,
        "m05_low": low - 0.5 * width,
        "m05_high": high + 0.5 * width,
        "mr01_low": low - 0.1 * width,
        "mr01_high": high + 0.1 * width,
        "mr02_low": low - 0.2 * width,
        "mr02_high": high + 0.2 * width,
        "mr03_low": low - 0.3 * width,
        "mr03_high": high + 0.3 * width,
        "ext100_low": low - 1.0 * width,
        "ext100_high": high + 1.0 * width,
        "ext133_low": low - 1.33 * width,
        "ext133_high": high + 1.33 * width,
        "ext166_low": low - 1.66 * width,
        "ext166_high": high + 1.66 * width,
        "band133_166_low_far": low - 1.66 * width,
        "band133_166_low_near": low - 1.33 * width,
        "band133_166_high_near": high + 1.33 * width,
        "band133_166_high_far": high + 1.66 * width,
        "overshoot_d": 0.1 * width,
    }


def _close_ticks_window(bars: BarIndex, start_ms: int, end_ms: int):
    w = bars.window(start_ms, end_ms)
    if w["n"] == 0:
        return w, None, None
    return w, to_ticks(w["c"]), w["t"]


def _judas_from_ohlc(h, l, c, t_ms, box, require_m05: bool) -> bool:
    if c is None or c.size == 0:
        return False
    high_t = int(round(box["H"] / TICK))
    low_t = int(round(box["L"] / TICK))
    eq_t = int(round(box["EQ"] / TICK))
    m05h_t = int(round(box["m05_high"] / TICK))
    m05l_t = int(round(box["m05_low"] / TICK))
    ht = to_ticks(h)
    lt = to_ticks(l)
    ct = to_ticks(c)
    broken = False
    side = None
    reached_m05 = False
    for i in range(ct.size):
        if not broken:
            if ct[i] > high_t:
                broken, side = True, "high"
            elif ct[i] < low_t:
                broken, side = True, "low"
            else:
                continue
        if side == "high" and int(ht[i]) >= m05h_t:
            reached_m05 = True
        if side == "low" and int(lt[i]) <= m05l_t:
            reached_m05 = True
        through = (side == "high" and int(ct[i]) <= eq_t) or (side == "low" and int(ct[i]) >= eq_t)
        if through and (not require_m05 or reached_m05):
            return True
    return False


def _midretrace(close_ticks, t_ms, high, low, eq, path) -> bool:
    if close_ticks is None or path["path_class"] in ("neither", None):
        return False
    if path["path_class"] == "low-only":
        first = path["first_low_break_ms"]
    elif path["path_class"] == "high-only":
        first = path["first_high_break_ms"]
    elif path["break_order"] == "low-then-high":
        first = path["first_low_break_ms"]
    else:
        first = path["first_high_break_ms"]
    if first is None:
        return False
    eq_t = int(round(eq / TICK))
    i0 = int(np.searchsorted(t_ms, first, "left"))
    series = close_ticks[i0:]
    if series.size == 0:
        return False
    if np.any(series == eq_t):
        return True
    signed = series.astype(np.int64) - eq_t
    return bool(np.any((signed[1:] * signed[:-1]) <= 0))


def _purged(h69, l69, asia, london) -> bool:
    if asia["high"] is None or london["high"] is None:
        return False
    tol = 2 * TICK
    return (
        abs(h69 - asia["high"]) <= tol or abs(h69 - london["high"]) <= tol
        or abs(l69 - asia["low"]) <= tol or abs(l69 - london["low"]) <= tol
    )


def build_session(
    day: date,
    bars_1m: BarIndex,
    bars_1s: BarIndex | None,
    *,
    prior_rth: dict | None,
    early_close: time | None = None,
) -> dict:
    spec = CLOCKS["range.6-9.published"]
    b69 = clock_bounds(day, spec)
    source = bars_1s or bars_1m
    box_w = source.window(b69["start_ms"], b69["end_ms"])
    box_1m = bars_1m.window(b69["start_ms"], b69["end_ms"])
    out_1m = bars_1m.window(b69["outcome_start_ms"], b69["outcome_end_ms"])
    open_0930 = bars_1m.window(b69["outcome_start_ms"], b69["outcome_start_ms"] + 60_000)
    asia = CLOCKS["range.gb.asia"]
    london = CLOCKS["range.london.00-03"]
    asia_w = source.window(*[clock_bounds(day, asia)[k] for k in ("start_ms", "end_ms")])
    london_w = source.window(*[clock_bounds(day, london)[k] for k in ("start_ms", "end_ms")])
    expected_1s = (b69["end_ms"] - b69["start_ms"]) // 1000
    if source.bar_ms == 1000:
        n_1s = box_w["n"]
        missing_1s = box_w["missing"]
    else:
        n_1s = box_1m["n"] * 60
        missing_1s = max(0, expected_1s - n_1s)
    # OHLCV-1s omits empty seconds. Coverage uses 1-minute occupancy of needed windows.
    drop_box = (box_1m["missing"] / box_1m["expected"]) > COVERAGE_MAX_MISSING if box_1m["expected"] else True
    drop_out = (out_1m["missing"] / out_1m["expected"]) > COVERAGE_MAX_MISSING if out_1m["expected"] else True
    drop = drop_box or drop_out
    failure = box_w["high"] is None or box_w["low"] is None or box_w["high"] <= box_w["low"]
    levels = None if failure else projections(box_w["high"], box_w["low"])
    path = {"path_class": None, "break_order": None, "first_high_break_ms": None, "first_low_break_ms": None}
    if not failure and out_1m["n"]:
        path = path_class_from_closes(
            to_ticks(out_1m["c"]), out_1m["t"],
            int(round(levels["H"] / TICK)), int(round(levels["L"] / TICK)),
        )
    w69 = None if failure else levels["W"]
    close_0859 = box_w["close"]
    open_0930_px = open_0930["open"]
    prior_w = None if prior_rth is None or prior_rth.get("high") is None else prior_rth["high"] - prior_rth["low"]
    w_pct_0859 = None if failure or not close_0859 else 100.0 * w69 / close_0859
    w_pct_0930 = None if failure or not open_0930_px else 100.0 * w69 / open_0930_px
    w_rel = None if failure or not prior_w else w69 / prior_w
    extended = w_rel is not None and w_rel >= 1.0
    compressed = w_rel is not None and w_rel <= 0.5
    purged = False if failure else _purged(box_w["high"], box_w["low"], asia_w, london_w)
    judas = False if failure else _judas_from_ohlc(out_1m["h"], out_1m["l"], out_1m["c"], out_1m["t"], levels, False)
    judas_m05 = False if failure else _judas_from_ohlc(out_1m["h"], out_1m["l"], out_1m["c"], out_1m["t"], levels, True)
    if path["path_class"] == "neither":
        day_type = "neither"
    elif judas:
        day_type = "judas"
    elif path["path_class"] in ("high-only", "low-only") and extended:
        day_type = "single-extended"
    elif path["path_class"] in ("high-only", "low-only") and purged:
        day_type = "single-purged"
    else:
        day_type = "unmatched"
    mid = False if failure else _midretrace(to_ticks(out_1m["c"]) if out_1m["n"] else None, out_1m["t"], *( (levels["H"], levels["L"], levels["EQ"], path) if levels else (0, 0, 0, path)))
    known_at = b69["known_at_ns"]
    outcome_start = b69["outcome_start_ns"]
    leakage = 0 if known_at <= outcome_start else 1
    # reversal first-touch of -0.5 in outcome window
    rev = _reversal_times(out_1m, levels) if levels and out_1m["n"] else {}
    return {
        "date": day.isoformat(),
        "year": str(day.year),
        "eligible": not drop and not failure,
        "drop_coverage": drop,
        "failure": failure,
        "n_1s": int(n_1s),
        "expected_1s": int(expected_1s),
        "missing_1s": int(missing_1s),
        "n_1m_box": int(box_1m["n"]),
        "n_1m_outcome": int(out_1m["n"]),
        "H": None if failure else box_w["high"],
        "L": None if failure else box_w["low"],
        "open": None if failure else box_w["open"],
        "close": None if failure else box_w["close"],
        "EQ": None if failure else levels["EQ"],
        "Q25": None if failure else levels["Q25"],
        "Q75": None if failure else levels["Q75"],
        "W69": w69,
        "volume": box_w["volume"],
        "close_0859": close_0859,
        "open_0930": open_0930_px,
        "w_pct_0859close": w_pct_0859,
        "w_pct_0930open": w_pct_0930,
        "WpriorRTH": prior_w,
        "w_rel_prior_rth": w_rel,
        "width_bin_pct": width_bin(w_pct_0859),
        "width_bin_rel": width_bin(w_rel),
        "prior_rth_high": None if prior_rth is None else prior_rth.get("high"),
        "prior_rth_low": None if prior_rth is None else prior_rth.get("low"),
        "asia_high": asia_w["high"],
        "asia_low": asia_w["low"],
        "london_high": london_w["high"],
        "london_low": london_w["low"],
        "path_class": path["path_class"],
        "break_order": path["break_order"],
        "first_high_break_ms": path["first_high_break_ms"],
        "first_low_break_ms": path["first_low_break_ms"],
        "judas": judas,
        "judas_m05": judas_m05,
        "extended": extended,
        "compressed": compressed,
        "purged": purged,
        "day_type": day_type,
        "midretrace": mid,
        "known_at_ns": known_at,
        "outcome_start_ns": outcome_start,
        "leakage": leakage,
        "levels": levels,
        "m05_touch_ms": rev.get("m05_touch_ms"),
        "m05_side": rev.get("side"),
        "reversal_bin": rev.get("bin"),
        "non_touch_m05": rev.get("touch") is False if rev else True,
        "source_bar_ms": source.bar_ms,
    }


def _reversal_times(out_1m: dict, levels: dict) -> dict:
    if out_1m["n"] == 0 or levels is None:
        return {"touch": False, "m05_touch_ms": None, "side": None, "bin": None}
    ht = to_ticks(out_1m["h"])
    lt = to_ticks(out_1m["l"])
    t = out_1m["t"]
    m05h = int(round(levels["m05_high"] / TICK))
    m05l = int(round(levels["m05_low"] / TICK))
    up = touch_level(ht, lt, t, m05h, 2)
    down = touch_level(ht, lt, t, m05l, 2)
    if up is None and down is None:
        return {"touch": False, "m05_touch_ms": None, "side": None, "bin": None}
    if up is None:
        ms, side = down, "low"
    elif down is None:
        ms, side = up, "high"
    else:
        ms, side = (up, "high") if up <= down else (down, "low")
    return {"touch": True, "m05_touch_ms": ms, "side": side, "bin": reversal_bin(ms, t[0])}


def reversal_bin(touch_ms: int | None, outcome_start_ms: int) -> str | None:
    if touch_ms is None:
        return None
    # Bins are clock-based, not offset-based. Map via minute-of-day proxy from
    # the first outcome bar (09:30).
    delta_min = (touch_ms - outcome_start_ms) / 60_000.0
    # 09:30 + delta.
    clock_min = 9 * 60 + 30 + delta_min
    if 9 * 60 + 40 <= clock_min < 9 * 60 + 50:
        return "bin.0940-0950"
    if 9 * 60 + 30 <= clock_min < 9 * 60 + 50:
        return "bin.0930-0950"
    if 9 * 60 + 50 <= clock_min < 10 * 60:
        return "bin.0950-1000"
    if 10 * 60 <= clock_min < 10 * 60 + 30:
        return "bin.1000-1030"
    if 10 * 60 + 30 <= clock_min < 12 * 60:
        return "bin.1030-1200"
    return "bin.other"


def vol_elapsed_end_ms(box_1s_or_1m: dict, median_volume: float, start_ms: int, end_ms: int) -> int:
    if box_1s_or_1m["n"] == 0 or median_volume is None or not np.isfinite(median_volume):
        return end_ms
    cum = np.cumsum(box_1s_or_1m["v"])
    hit = np.flatnonzero(cum >= median_volume)
    if hit.size == 0:
        return end_ms
    t = box_1s_or_1m["t"]
    bar_ms = int(t[1] - t[0]) if t.size > 1 else 60_000
    return int(t[int(hit[0])] + bar_ms)


def prior_rth_window(day: date, bars: BarIndex, prev_day: date | None, early_close: time | None) -> dict | None:
    if prev_day is None:
        return None
    start = wall_ns(prev_day, time(9, 30), 0)
    end = wall_ns(prev_day, early_close or time(16, 0), 0)
    return bars.window(start // 1_000_000, end // 1_000_000)
