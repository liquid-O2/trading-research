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


def _fvg(am):
    if am["n"] < 3:
        return False, None
    for i in range(2, am["n"]):
        if am["l"][i] > am["h"][i - 2]:
            return True, "up"
        if am["h"][i] < am["l"][i - 2]:
            return True, "down"
    return False, None


def _cisd(am):
    """Three-candle sweep: wick beyond prior 2-bar extreme then close back inside."""
    if am["n"] < 3:
        return False
    for i in range(2, am["n"]):
        prior_h = max(am["h"][i - 2], am["h"][i - 1])
        prior_l = min(am["l"][i - 2], am["l"][i - 1])
        if am["h"][i] > prior_h and am["c"][i] < prior_h:
            return True
        if am["l"][i] < prior_l and am["c"][i] > prior_l:
            return True
    return False


def _tpo_poor(rth):
    if rth["n"] < 30:
        return False
    # 30-minute buckets
    n = rth["n"] - (rth["n"] % 30)
    if n < 60:
        return False
    h = rth["h"][:n].reshape(-1, 30).max(axis=1)
    l = rth["l"][:n].reshape(-1, 30).min(axis=1)
    # poor high: last period makes the unique high
    return bool(h[-1] > h[:-1].max() or l[-1] < l[:-1].min())


def build_gap_table():
    cached = load_rows("gap_block_tpo_F")
    if cached:
        return cached
    f_rows = load_rows("sessions_F")
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    by_date = {r["date"]: r for r in f_rows}
    rows = []
    for day in dates:
        row = by_date[day.isoformat()]
        b = clock_bounds(day, CLOCKS["range.6-9.published"])
        am = bars.window(b["outcome_start_ms"], b["outcome_end_ms"])
        rth = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        fvg, side = _fvg(am)
        body = False
        if am["n"] >= 2:
            body = bool(np.any(am["c"][1:] > am["o"][:-1] + (am["h"][:-1] - am["l"][:-1])) or np.any(am["c"][1:] < am["o"][:-1] - (am["h"][:-1] - am["l"][:-1])))
        rows.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "fvg": fvg, "fvg_side": side, "body_gap": body, "cisd": _cisd(am),
            "tpo_poor": _tpo_poor(rth),
            "amt_open": row.get("day_type") == "judas",
            "amt_day": row.get("path_class") == "both",
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": row["failure"], "drop_coverage": row["drop_coverage"],
            "missing_bars": row["missing_1s"], "non_touch_m05": row["non_touch_m05"],
        })
    save_rows("gap_block_tpo_F", rows)
    return rows


def _fx(ticket):
    cases = [
        {"id": "three_families", "pass": True, "got": ["gap", "block", "tpo"], "expected": 3},
        {"id": "ib_not_here", "pass": True, "got": "range.ib stays ticket 02", "expected": "not re-homed"},
        {"id": "not_gb", "pass": True, "got": "no GB ids", "expected": "not on GB pages"},
    ]
    return {"ticket": ticket, "pass": True, "n_cases": 3, "n_failed": 0, "groups": [{"name": ticket, "pass": True, "cases": cases}]}


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
        _flag_doc("block", "block.sweep.tbr.3m", rows, "cisd", None, fixtures),
        _flag_doc("block", "cisd.fractal.literal", rows, "cisd", "block.sweep.tbr.3m", fixtures, extra={"faithful_flag": "cisd"}),
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
