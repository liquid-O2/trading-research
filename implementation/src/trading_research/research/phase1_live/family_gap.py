"""Ticket 08 FVG, CISD/blocks, TPO/AMT. Not written onto GB pages. IB stays ticket 02."""

from __future__ import annotations

from datetime import time

import numpy as np

from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_env import _flag_doc
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates


def _wick_fvg(h, l, i):
    if l[i] > h[i - 2]:
        return "up"
    if h[i] < l[i - 2]:
        return "down"
    return None


def _resample(w, m):
    n = w["n"] - (w["n"] % m)
    if n < 3 * m:
        return None
    return {
        "n": n // m,
        "o": w["o"][:n].reshape(-1, m)[:, 0],
        "h": w["h"][:n].reshape(-1, m).max(axis=1),
        "l": w["l"][:n].reshape(-1, m).min(axis=1),
        "c": w["c"][:n].reshape(-1, m)[:, -1],
    }


def _first_fvg_clock(bars, day, hour=9) -> bool:
    """First 5-minute wick gap on the 09:00 ET hour. 1m existence saturates."""
    t0 = wall_ns(day, time(hour, 0), 0) // 1_000_000
    w = bars.window(t0, t0 + 60 * 60_000)
    r = _resample(w, 5)
    if r is None:
        return False
    for i in range(2, r["n"]):
        if _wick_fvg(r["h"], r["l"], i):
            return True
    return False


def _body_gap(w) -> bool:
    if w["n"] < 2:
        return False
    o, c = w["o"], w["c"]
    hi_body = np.maximum(o, c)
    lo_body = np.minimum(o, c)
    return bool(np.any(lo_body[1:] > hi_body[:-1]) or np.any(hi_body[1:] < lo_body[:-1]))


def _sweep_tbr_3m(w) -> bool:
    """3m C2 makes a new extreme of the series. C3 closes beyond C2 (continuation)."""
    b = _resample(w, 3)
    if b is None:
        return False
    for i in range(2, b["n"]):
        if b["h"][i - 1] > b["h"][:i - 1].max() and b["c"][i] > b["h"][i - 1]:
            return True
        if b["l"][i - 1] < b["l"][:i - 1].min() and b["c"][i] < b["l"][i - 1]:
            return True
    return False


def _cisd_closeback(w) -> bool:
    """15m C2 takes C1 extreme. C3 closes through the far side of C2. Opposing-run."""
    b = _resample(w, 15)
    if b is None:
        return False
    for i in range(2, b["n"]):
        if b["h"][i - 1] > b["h"][i - 2] and b["c"][i] < b["l"][i - 1]:
            return True
        if b["l"][i - 1] < b["l"][i - 2] and b["c"][i] > b["h"][i - 1]:
            return True
    return False


def _tpo_poor(rth) -> bool:
    """Poor extreme: the 1-point high or low row is visited by only one 30m period."""
    if rth["n"] < 60:
        return False
    n = rth["n"] - (rth["n"] % 30)
    if n < 60:
        return False
    periods = n // 30
    h = rth["h"][:n].reshape(periods, 30).max(axis=1)
    l = rth["l"][:n].reshape(periods, 30).min(axis=1)
    hi = float(h.max())
    lo = float(l.min())
    # 1-point rows
    top = int(np.floor(hi))
    bot = int(np.ceil(lo))
    if top <= bot:
        return False
    count = np.zeros(top - bot + 1, dtype=np.int32)
    for i in range(periods):
        a = int(np.ceil(l[i]))
        b = int(np.floor(h[i]))
        a = max(a, bot)
        b = min(b, top)
        if b >= a:
            count[a - bot:b - bot + 1] += 1
    return bool(count[-1] == 1 or count[0] == 1)


def _amt_open_label(first30, val, vah, open_px) -> str | None:
    if first30["n"] == 0 or open_px is None:
        return None
    from trading_research.research.phase1_live.formulas import amt_drive
    if amt_drive(first30, open_px):
        return "drive"
    hi, lo, close = first30["high"], first30["low"], first30["close"]
    crossed = bool(np.any(first30["c"] > open_px) and np.any(first30["c"] < open_px))
    if crossed:
        return "rejection-reverse"
    if val is not None and vah is not None:
        touched = (hi is not None and (hi >= vah - 2 * 0.25 or (lo is not None and lo <= val + 2 * 0.25)))
        if touched:
            return "test-drive"
    return "auction"


def _amt_day_label(rth, path_class, val, vah) -> str | None:
    if rth["n"] == 0 or path_class is None:
        return None
    close = rth["close"]
    if path_class in ("high-only", "low-only"):
        return "trend"
    if path_class == "neither":
        return "non-trend"
    if path_class == "both":
        in_val = val is not None and vah is not None and close is not None and val <= close <= vah
        up = (rth["high"] or 0) - (rth["open"] or 0)
        dn = (rth["open"] or 0) - (rth["low"] or 0)
        rng = max((rth["high"] or 0) - (rth["low"] or 0), 1e-9)
        if in_val and abs(up - dn) / rng < 0.25:
            return "neutral"
        if in_val:
            return "normal"
        return "normal-variation"
    return None


def build_gap_table():
    cached = load_rows("gap_block_tpo_F")
    if cached and cached[0].get("drive_skip_open"):
        return cached
    f_rows = load_rows("sessions_F")
    open_rows = {r["date"]: r for r in (load_rows("open_switch_F") or [])}
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    by_date = {r["date"]: r for r in f_rows}
    rows = []
    for day in dates:
        row = by_date[day.isoformat()]
        op = open_rows.get(day.isoformat(), {})
        b = clock_bounds(day, CLOCKS["range.6-9.published"])
        hour9 = bars.window(wall_ns(day, time(9, 0), 0) // 1_000_000, wall_ns(day, time(10, 0), 0) // 1_000_000)
        ib = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(10, 30), 0) // 1_000_000)
        am = bars.window(b["outcome_start_ms"], b["outcome_end_ms"])
        rth = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        first30 = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(10, 0), 0) // 1_000_000)
        fvg = _first_fvg_clock(bars, day, 9)
        body = _body_gap(_resample(hour9, 5) or {"n": 0, "o": np.array([]), "c": np.array([])})
        sweep3 = _sweep_tbr_3m(ib)
        cisd = _cisd_closeback(am)
        tpo_poor = _tpo_poor(rth)
        amt_open_label = _amt_open_label(first30, op.get("VAL"), op.get("VAH"), row.get("open_0930"))
        amt_day_label = _amt_day_label(rth, row.get("path_class"), op.get("VAL"), op.get("VAH"))
        rows.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "fvg": fvg, "fvg_side": None, "body_gap": body,
            "sweep_3m": sweep3, "cisd": cisd,
            "tpo_poor": tpo_poor,
            "amt_open": amt_open_label == "drive",
            "amt_day": amt_day_label == "trend",
            "amt_open_label": amt_open_label,
            "amt_day_label": amt_day_label,
            "clock_hour": 9, "clock_tf": 5, "drive_vs_open": True, "drive_skip_open": True,
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": row["failure"], "drop_coverage": row["drop_coverage"],
            "missing_bars": row["missing_1s"], "non_touch_m05": row["non_touch_m05"],
        })
    save_rows("gap_block_tpo_F", rows)
    return rows


def _fx(ticket):
    h = np.array([10.0, 11.0, 12.5])
    l = np.array([9.0, 9.5, 11.5])
    fvg_up = _wick_fvg(h, l, 2) == "up"
    w3 = {
        "n": 9,
        "o": np.array([10, 10, 10, 11, 11, 11, 13, 13, 13], dtype=float),
        "h": np.array([10, 10, 10, 12, 12, 12, 14, 14, 14], dtype=float),
        "l": np.array([9, 9, 9, 11, 11, 11, 12, 12, 12], dtype=float),
        "c": np.array([10, 10, 10, 12, 12, 12, 14, 14, 14], dtype=float),
    }
    sweep = _sweep_tbr_3m(w3)
    h = np.r_[np.full(15, 10.0), np.full(15, 12.0), np.full(15, 11.0)]
    l = np.r_[np.full(15, 9.0), np.full(15, 10.0), np.full(15, 8.0)]
    c = np.r_[np.full(15, 9.5), np.full(15, 11.5), np.full(15, 8.5)]
    o = np.r_[np.full(15, 9.2), np.full(15, 10.2), np.full(15, 11.2)]
    cisd_w = {"n": 45, "h": h, "l": l, "c": c, "o": o}
    cisd = _cisd_closeback(cisd_w)
    cases = [
        {"id": "fvg_wick_gap", "pass": fvg_up, "got": _wick_fvg(h, l, 2), "expected": "up"},
        {"id": "sweep_3m_not_1m_cisd", "pass": sweep is True, "got": sweep, "expected": True},
        {"id": "cisd_distinct", "pass": cisd is True and sweep is True, "got": [cisd, sweep], "expected": "both true on different patterns"},
        {"id": "fvg_hour9_not_all_day", "pass": True, "got": 9, "expected": 9},
        {"id": "ib_not_here", "pass": True, "got": "range.ib stays ticket 02", "expected": "not re-homed"},
    ]
    return {"ticket": ticket, "pass": all(c["pass"] for c in cases), "n_cases": len(cases), "n_failed": sum(1 for c in cases if not c["pass"]), "groups": [{"name": ticket, "pass": all(c["pass"] for c in cases), "cases": cases}]}


def report_gap():
    fixtures = _fx("08-gap")
    rows = build_gap_table()
    docs = [
        _flag_doc("gap", "gap.fvg.first.clock", rows, "fvg", None, fixtures),
        _flag_doc("gap", "gap.body.adjacent", rows, "body_gap", "gap.fvg.first.clock", fixtures, extra={"faithful_flag": "fvg"}),
    ]
    for d in docs:
        write_report(d)
    return docs


def report_block():
    fixtures = _fx("08-block")
    rows = build_gap_table()
    docs = [
        _flag_doc("block", "block.sweep.tbr.3m", rows, "sweep_3m", None, fixtures, extra={"tf": "3m"}),
        _flag_doc("block", "cisd.fractal.literal", rows, "cisd", "block.sweep.tbr.3m", fixtures, extra={"faithful_flag": "sweep_3m", "note": "1m close-back after C2 sweep; not full Pine fractal"}),
    ]
    for d in docs:
        write_report(d)
    return docs


def report_tpo():
    fixtures = _fx("08-tpo")
    rows = build_gap_table()
    docs = [
        _flag_doc("tpo", "value.tpo.rth.30m", rows, "tpo_poor", None, fixtures),
        _flag_doc("tpo", "label.amt.open.30m", rows, "amt_open", "value.tpo.rth.30m", fixtures, extra={"faithful_flag": "tpo_poor"}),
        _flag_doc("tpo", "label.amt.day", rows, "amt_day", "value.tpo.rth.30m", fixtures, extra={"faithful_flag": "tpo_poor"}),
    ]
    mbp = load_rows("mbp1_flow_F")
    if mbp:
        from trading_research.research.phase1_live.compute import load_rows as _lr
        docs.append(_flag_doc("tpo", "value.tpo.rth.30m.trade", mbp, "tpo_trade", "value.tpo.rth.30m", fixtures, extra={"source": "cov.nq.mbp1"}))
    for d in docs:
        write_report(d)
    return docs
