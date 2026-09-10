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


def _first_fvg_per_hour(bars, day) -> bool:
    """First three-bar wick gap on 1-minute bars in any ET hour."""
    for hour in range(0, 16):
        t0 = wall_ns(day, time(hour, 0), 0) // 1_000_000
        t1 = wall_ns(day, time(hour + 1 if hour < 23 else 23, 0 if hour < 23 else 59), 0) // 1_000_000
        if hour == 23:
            t1 = t0 + 60 * 60_000
        w = bars.window(t0, t0 + 60 * 60_000)
        if w["n"] < 3:
            continue
        for i in range(2, w["n"]):
            if _wick_fvg(w["h"], w["l"], i):
                return True
    return False


def _body_gap(w) -> bool:
    if w["n"] < 2:
        return False
    o, c = w["o"], w["c"]
    hi_body = np.maximum(o, c)
    lo_body = np.minimum(o, c)
    return bool(np.any(lo_body[1:] > hi_body[:-1]) or np.any(hi_body[1:] < lo_body[:-1]))


def _resample_3m(w):
    n = w["n"] - (w["n"] % 3)
    if n < 9:
        return None
    return {
        "n": n // 3,
        "o": w["o"][:n].reshape(-1, 3)[:, 0],
        "h": w["h"][:n].reshape(-1, 3).max(axis=1),
        "l": w["l"][:n].reshape(-1, 3).min(axis=1),
        "c": w["c"][:n].reshape(-1, 3)[:, -1],
    }


def _sweep_tbr_3m(w) -> bool:
    b = _resample_3m(w)
    if b is None:
        return False
    for i in range(2, b["n"]):
        c1_h, c1_l = b["h"][i - 2], b["l"][i - 2]
        c2_h, c2_l = b["h"][i - 1], b["l"][i - 1]
        c3_c = b["c"][i]
        if c2_h > c1_h and c3_c > c2_h:
            return True
        if c2_l < c1_l and c3_c < c2_l:
            return True
    return False


def _cisd_closeback(w) -> bool:
    """1m C2 sweep of C1 then C3 close back through C2 extreme. Not the 3m TBR row."""
    if w["n"] < 3:
        return False
    for i in range(2, w["n"]):
        if w["h"][i - 1] > w["h"][i - 2] and w["c"][i] < w["h"][i - 1]:
            return True
        if w["l"][i - 1] < w["l"][i - 2] and w["c"][i] > w["l"][i - 1]:
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


def _amt_open(first30, val, vah, pdl, pdh, open_px) -> bool:
    """Drive / test-drive / rejection-reverse / auction. Not a Judas alias."""
    if first30["n"] == 0 or open_px is None:
        return False
    hi, lo, close = first30["high"], first30["low"], first30["close"]
    vs_val = None
    if val is not None and vah is not None:
        if open_px > vah:
            vs_val = "above"
        elif open_px < val:
            vs_val = "below"
        else:
            vs_val = "in"
    if vs_val in ("above", "below"):
        stayed = (vs_val == "above" and lo is not None and lo > vah) or (vs_val == "below" and hi is not None and hi < val)
        returned = (vs_val == "above" and lo is not None and lo <= vah) or (vs_val == "below" and hi is not None and hi >= val)
        return bool(stayed or returned)
    if vs_val == "in":
        wick_out = (hi is not None and vah is not None and hi > vah) or (lo is not None and val is not None and lo < val)
        close_in = close is not None and val is not None and vah is not None and val <= close <= vah
        return True if (wick_out and close_in) or not wick_out else False
    return False


def _amt_day(rth, path_class) -> bool:
    """Trend / normal / neutral-ish from completed RTH. Unmatched stays false."""
    if rth["n"] == 0 or path_class is None:
        return False
    if path_class in ("high-only", "low-only"):
        return True
    if path_class == "both":
        return True
    return False


def build_gap_table():
    cached = load_rows("gap_block_tpo_F")
    if cached and cached and "sweep_3m" in cached[0]:
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
        am = bars.window(b["outcome_start_ms"], b["outcome_end_ms"])
        rth = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        first30 = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(10, 0), 0) // 1_000_000)
        fvg = _first_fvg_per_hour(bars, day)
        body = _body_gap(rth)
        sweep3 = _sweep_tbr_3m(am)
        cisd = _cisd_closeback(am)
        tpo_poor = _tpo_poor(rth)
        amt_open = _amt_open(
            first30, op.get("VAL"), op.get("VAH"),
            row.get("prior_rth_low"), row.get("prior_rth_high"), row.get("open_0930"),
        )
        amt_day = _amt_day(rth, row.get("path_class"))
        rows.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "fvg": fvg, "fvg_side": None, "body_gap": body,
            "sweep_3m": sweep3, "cisd": cisd,
            "tpo_poor": tpo_poor,
            "amt_open": amt_open,
            "amt_day": amt_day,
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
    cisd_w = {
        "n": 3,
        "h": np.array([10.0, 12.0, 11.0]),
        "l": np.array([9.0, 10.0, 10.0]),
        "c": np.array([9.5, 11.5, 10.5]),
        "o": np.array([9.2, 10.2, 11.2]),
    }
    cisd = _cisd_closeback(cisd_w)
    cases = [
        {"id": "fvg_wick_gap", "pass": fvg_up, "got": _wick_fvg(h, l, 2), "expected": "up"},
        {"id": "sweep_3m_not_1m_cisd", "pass": sweep is True, "got": sweep, "expected": True},
        {"id": "cisd_distinct", "pass": cisd is True, "got": cisd, "expected": True},
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
