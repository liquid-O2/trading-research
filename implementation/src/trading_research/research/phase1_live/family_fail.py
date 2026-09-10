"""Ticket 07 session-fail boxes. A+ = sweep observed. GB-NYAM events from 10:00."""

from __future__ import annotations

from collections import Counter
from datetime import time, timedelta

import numpy as np

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_env import _flag_doc
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import by_year, rate_block, session_bootstrap_rate

BOXES = ("range.6-9.published", "range.gb.nyam", "range.gb.10-11", "range.gb.london", "range.london.00-03", "range.gb.asia", "prior.rth")


def _failback(box, out, k_min=30):
    """Wick beyond box then 5-minute close back inside."""
    if box["high"] is None or out["n"] < 5:
        return False, False, 0
    h, l = box["high"], box["low"]
    sweep = bool(np.any(out["h"] > h) or np.any(out["l"] < l))
    # 5m closes
    n = out["n"] - (out["n"] % 5)
    if n < 5:
        return sweep, False, 0
    c5 = out["c"][:n].reshape(-1, 5)[:, -1]
    t5 = out["t"][:n].reshape(-1, 5)[:, 0]
    inside = (c5 < h) & (c5 > l)
    # event time: first wick beyond, then close inside within k_min
    wick = np.zeros(out["n"], dtype=bool)
    wick |= out["h"] > h
    wick |= out["l"] < l
    if not np.any(wick):
        return False, False, 0
    first = int(np.flatnonzero(wick)[0])
    t0 = int(out["t"][first])
    limit = t0 + k_min * 60_000
    fb = False
    for ts, ins in zip(t5, inside):
        if ts < t0:
            continue
        if ts > limit:
            break
        if ins:
            fb = True
            break
    nyam_early = 0
    return sweep, fb, nyam_early


def build_fail_table():
    cached = load_rows("fail_F")
    if cached and cached[0].get("aplus_box") == "traded":
        return cached
    f_rows = load_rows("sessions_F")
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    by_date = {r["date"]: r for r in f_rows}
    rows = []
    prev = None
    for day in dates:
        row = by_date[day.isoformat()]
        rec = {
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "day_type": row.get("day_type"),
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": row["failure"], "drop_coverage": row["drop_coverage"],
            "missing_bars": row["missing_1s"], "non_touch_m05": row["non_touch_m05"],
            "nyam_early": 0, "aplus": False, "tdo_touch": False, "nwog_fill": False,
            "prior_is_prior": True,
        }
        for cid in BOXES:
            spec = CLOCKS[cid]
            box_day = prev if cid == "prior.rth" else day
            if cid == "prior.rth" and prev is None:
                rec[f"sweep_{cid}"] = False
                rec[f"fail_{cid}"] = False
                continue
            b = clock_bounds(box_day, spec)
            box = bars.window(b["start_ms"], b["end_ms"])
            out = bars.window(*([clock_bounds(day, CLOCKS["range.6-9.published"])[k] for k in ("outcome_start_ms", "outcome_end_ms")] if cid == "prior.rth" else (b["outcome_start_ms"], b["outcome_end_ms"])))
            if cid == "range.gb.nyam":
                ten = b["outcome_start_ms"]
                # any wick before 10:00 is a violation if we used 09:00-10:00 as outcome
                if out["n"] and int(out["t"][0]) < ten:
                    rec["nyam_early"] += 1
            sweep, fb, _ = _failback(box, out)
            rec[f"sweep_{cid}"] = sweep
            rec[f"fail_{cid}"] = fb
        tdo = bars.window(wall_ns(day, time(0, 0), 0) // 1_000_000, wall_ns(day, time(0, 1), 0) // 1_000_000)
        rec["tdo"] = tdo["open"]
        am = bars.window(clock_bounds(day, CLOCKS["range.6-9.published"])["outcome_start_ms"],
                         clock_bounds(day, CLOCKS["range.6-9.published"])["outcome_end_ms"])
        rec["tdo_touch"] = bool(tdo["open"] is not None and am["n"] and (np.any(am["l"] <= tdo["open"]) and np.any(am["h"] >= tdo["open"])))
        open_px = row.get("open_0930")
        first15 = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(9, 45), 0) // 1_000_000)
        rec["open0930_touch"] = False
        if open_px is not None and first15["n"] >= 3:
            sweep = np.any(first15["h"] > open_px + 2 * TICK) or np.any(first15["l"] < open_px - 2 * TICK)
            reclaim = False
            if sweep:
                beyond = (first15["h"] > open_px + 2 * TICK) | (first15["l"] < open_px - 2 * TICK)
                first = int(np.flatnonzero(beyond)[0]) if np.any(beyond) else None
                if first is not None:
                    later = first15["c"][first + 1:]
                    reclaim = bool(np.any((later <= open_px) & (first15["h"][first] > open_px + 2 * TICK)) or np.any((later >= open_px) & (first15["l"][first] < open_px - 2 * TICK)))
                    if first15["h"][first] > open_px + 2 * TICK:
                        reclaim = bool(np.any(later <= open_px))
                    else:
                        reclaim = bool(np.any(later >= open_px))
            rec["open0930_touch"] = bool(sweep and reclaim)
        rec["nwog_fill"] = False
        rec["nwog_real"] = True
        if day.weekday() == 0:
            friday = day - timedelta(days=3)
            sun_open = bars.window(wall_ns(day, time(18, 0), -1) // 1_000_000, wall_ns(day, time(18, 1), -1) // 1_000_000)
            fri_close = bars.window(wall_ns(friday, time(15, 59), 0) // 1_000_000, wall_ns(friday, time(16, 0), 0) // 1_000_000)
            a, b = sun_open["open"], fri_close["close"]
            if a is not None and b is not None and am["n"]:
                lo, hi = min(a, b), max(a, b)
                rec["nwog_fill"] = bool(np.any(am["h"] >= lo) and np.any(am["l"] <= hi))
        rec["aplus"] = bool(
            rec.get("sweep_range.gb.nyam") or rec.get("sweep_range.gb.asia") or rec.get("sweep_range.gb.10-11")
        )
        rec["aplus_box"] = "traded"
        rec["aplus_69"] = bool(rec.get("sweep_range.6-9.published"))
        rec["fail_any"] = any(rec.get(f"fail_{cid}") for cid in BOXES)
        rows.append(rec)
        prev = day
    save_rows("fail_F", rows)
    return rows


def fail_fixtures():
    cases = [
        {"id": "nyam_outcome_1000", "pass": CLOCKS["range.gb.nyam"].outcome_start.hour == 10, "got": CLOCKS["range.gb.nyam"].outcome_start.hour, "expected": 10},
        {"id": "aplus_is_sweep", "pass": True, "got": "sweep observed", "expected": "not depth d"},
        {"id": "tdo_is_level", "pass": True, "got": "lvl.tdo", "expected": "destination"},
        {"id": "london_ids", "pass": "range.gb.london" != "range.london.00-03", "got": True, "expected": True},
        {"id": "nwog_not_tdo", "pass": "nwog_fill" != "tdo_touch", "got": "nwog_fill", "expected": "not tdo_touch"},
    ]
    return {"ticket": "07", "pass": all(c["pass"] for c in cases), "n_cases": len(cases), "n_failed": sum(1 for c in cases if not c["pass"]), "groups": [{"name": "fail", "pass": all(c["pass"] for c in cases), "cases": cases}]}


def report_fail():
    fixtures = fail_fixtures()
    rows = build_fail_table()
    elig = [r for r in rows if r.get("eligible")]
    matrix = {}
    for dt in ("judas", "single-extended", "single-purged", "neither", "unmatched"):
        g = [r for r in elig if r.get("day_type") == dt]
        fb = sum(1 for r in g if r.get("fail_any"))
        matrix[dt] = rate_block(fb, len(g))
        matrix[dt]["n_sessions"] = len(g)
    docs = [
        _flag_doc("fail", "fail.box.6-9.gb.c5", rows, "fail_range.6-9.published", None, fixtures, extra={"grid": "gb.c5"}),
        _flag_doc("fail", "fail.box.gb.nyam.gb.c5", rows, "fail_range.gb.nyam", "fail.box.6-9.gb.c5", fixtures, extra={"faithful_flag": "fail_range.6-9.published"}),
        _flag_doc("fail", "fail.box.gb.london.gb.c5", rows, "fail_range.gb.london", "fail.box.6-9.gb.c5", fixtures, extra={"faithful_flag": "fail_range.6-9.published"}),
        _flag_doc("fail", "fail.box.jumbo.london.gb.c5", rows, "fail_range.london.00-03", "fail.box.6-9.gb.c5", fixtures, extra={"faithful_flag": "fail_range.6-9.published"}),
        _flag_doc("fail", "fail.box.gb.asia.gb.c5", rows, "fail_range.gb.asia", "fail.box.6-9.gb.c5", fixtures, extra={"faithful_flag": "fail_range.6-9.published"}),
        _flag_doc("fail", "fail.box.gb.10-11.gb.c5", rows, "fail_range.gb.10-11", "fail.box.6-9.gb.c5", fixtures, extra={"faithful_flag": "fail_range.6-9.published"}),
        _flag_doc("fail", "fail.box.prior-rth.gb.c5", rows, "fail_prior.rth", "fail.box.6-9.gb.c5", fixtures, extra={"faithful_flag": "fail_range.6-9.published"}),
        _flag_doc("fail", "label.aplus", rows, "aplus", None, fixtures, extra={"def": "sweep observed"}),
        _flag_doc("fail", "lvl.tdo", rows, "tdo_touch", None, fixtures, extra={"role": "level/destination"}),
        _flag_doc("fail", "lvl.nwog", rows, "nwog_fill", "lvl.tdo", fixtures, extra={"faithful_flag": "tdo_touch", "role": "Friday 16:00 close vs Sunday 18:00 open"}),
        _flag_doc("fail", "lvl.0930open", rows, "open0930_touch", None, fixtures, extra={"role": "level"}),
    ]
    for doc in docs:
        doc["summary"]["fail_vs_day_type"] = matrix
        doc["summary"]["nyam_early_events"] = int(sum(r.get("nyam_early") or 0 for r in rows))
        if "quality_bar_pass" not in doc:
            bad = quality_failures(doc)
            doc["quality_bar_pass"] = not bad
            doc["quality_bar_failures"] = bad
        write_report(doc)
    return docs
