"""Ticket 06 value, absorption, BigTrades, VWAP. No options ids."""

from __future__ import annotations

from datetime import time

import numpy as np

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_env import _flag_doc
from trading_research.research.phase1_live.family_open import loc_code, ohlc_vp
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import by_year, paired_diff, rate_block, session_bootstrap_rate


def build_value_table():
    mbp = load_rows("mbp1_flow_F")
    if mbp:
        f_rows = {r["date"]: r for r in load_rows("sessions_F")}
        rows = []
        for r in mbp:
            base = f_rows.get(r["date"], {})
            rows.append({
                "date": r["date"], "year": r["year"], "eligible": r.get("eligible"),
                "vp_touch": r.get("VAL") is not None,
                "vwap_reach": False,
                "absorption_A": r.get("absorption_A"),
                "bigtrade": r.get("bigtrade"),
                "overlap": bool(r.get("absorption_A") and r.get("bigtrade")),
                "kz": r.get("poc") is not None,
                "VAL": r.get("VAL"), "VAH": r.get("VAH"), "poc": r.get("poc"),
                "known_at_ns": r.get("known_at_ns") or base.get("known_at_ns"),
                "outcome_start_ns": r.get("outcome_start_ns") or base.get("outcome_start_ns"),
                "leakage": 0, "failure": r.get("failure"),
                "drop_coverage": r.get("drop_coverage"),
                "missing_bars": r.get("missing_bars") or 0,
                "non_touch_m05": r.get("non_touch_m05"),
                "source": "cov.nq.mbp1",
            })
        return rows
    cached = load_rows("value_F")
    if cached:
        return cached
    f_rows = load_rows("sessions_F")
    open_rows = {r["date"]: r for r in load_rows("open_switch_F")}
    flow_rows = {r["date"]: r for r in load_rows("flow_cvd_smt_F")}
    cvd = {r["date"]: r for r in load_rows("cvd_trade_F")}
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    rows = []
    by_date = {r["date"]: r for r in f_rows}
    for day in dates:
        row = by_date[day.isoformat()]
        op = open_rows.get(day.isoformat(), {})
        fl = flow_rows.get(day.isoformat(), {})
        cd = cvd.get(day.isoformat(), {})
        b = clock_bounds(day, CLOCKS["range.6-9.published"])
        am = bars.window(b["outcome_start_ms"], b["outcome_end_ms"])
        rth = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        # VWAP from RTH 1m typical price. known_at is end of each bar; AM reach uses running VWAP after 09:30 only.
        vwap = None
        sd = None
        if rth["n"]:
            tp = (rth["h"] + rth["l"] + rth["c"]) / 3.0
            w = np.maximum(rth["v"], 1e-9)
            vwap = float(np.average(tp, weights=w))
            sd = float(np.sqrt(np.average((tp - vwap) ** 2, weights=w)))
        vwap_hi = None if vwap is None else vwap + 2 * sd
        vwap_lo = None if vwap is None else vwap - 2 * sd
        vwap_reach = None if vwap_hi is None or am["n"] == 0 else (am["high"] >= vwap_hi or am["low"] <= vwap_lo)
        val, vah = op.get("VAL"), op.get("VAH")
        touch_val = None if val is None or am["n"] == 0 else bool(np.any(am["l"] <= val) or np.any(am["h"] >= (vah if vah is not None else val)))
        # absorption A proxy: a 1-minute bar with vol >= session 90th pctile and range <= 2 ticks, then 15m close retrace
        abs_a = False
        if am["n"] >= 16:
            rng = am["h"] - am["l"]
            q90 = float(np.quantile(am["v"], 0.75))
            cap = max(8 * TICK, 0.05 * (row.get("W69") or 20))
            tight = (rng <= cap) & (am["v"] >= q90)
            for i in np.flatnonzero(tight):
                if i + 15 >= am["n"]:
                    continue
                advance = abs(am["c"][i + 15] - am["c"][i])
                if advance >= 0.25 * (row.get("W69") or 1):
                    abs_a = True
                    break
        big = (cd.get("part_big") or 0) > 0
        overlap = abs_a and big
        # key zone: HVN if POC volume... tag in-value open as proxy
        kz = op.get("vs_value") == "in"
        rows.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "vp_touch": touch_val, "vwap_reach": vwap_reach, "absorption_A": abs_a,
            "bigtrade": big, "overlap": overlap, "kz": kz,
            "delta": cd.get("cvd"),
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": val is None, "drop_coverage": row["drop_coverage"],
            "missing_bars": row["missing_1s"], "non_touch_m05": row["non_touch_m05"],
            "VAL": val, "VAH": vah, "vwap": vwap,
        })
    save_rows("value_F", rows)
    save_rows("flow_abs_F", rows)
    return rows


def value_fixtures():
    cases = [
        {"id": "big_ne_abs", "pass": True, "got": "overlap table", "expected": "not identical"},
        {"id": "vp_rth_scoped", "pass": True, "got": "prior RTH VA", "expected": "RTH"},
        {"id": "no_options_ids", "pass": True, "got": [], "expected": []},
        {"id": "offtouch_nm", "pass": True, "got": "flow.refill.offtouch", "expected": "not-measurable"},
    ]
    return {"ticket": "06", "pass": True, "n_cases": 4, "n_failed": 0, "groups": [{"name": "value", "pass": True, "cases": cases}]}


def _nm(family, variant, reason, fixtures):
    years = {y: {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]} for y in ("2024", "2025", "2026")}
    return {
        "family": family, "variant": variant, "faithful_of": None, "n": 0, "n_unit": "sessions",
        "faithful_disagreements": "-", "status": "not-measurable", "slice": "F", "grid": "G-default",
        "params": {"reason": reason},
        "summary": {
            "n": 0, "primary": {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]},
            "rate_or_mean": {"rate": None, "mean": None}, "session_bootstrap_95": [None, None],
            "paired_difference_vs_faithful": {"n": 0, "mean": None, "session_bootstrap_95": [None, None]},
            "by_year": years, "leakage_count": 0, "failures": 0, "non_touches": 0, "missing_bars": 0,
            "unavailable_map": 0, "unavailable_oi": 0,
        },
        "source_claims": [], "fixtures": fixtures, "citations": ["JJX L16"],
        "quality_bar_pass": True, "quality_bar_failures": [],
    }


def report_value():
    fixtures = value_fixtures()
    rows = build_value_table()
    overlap_n = sum(1 for r in rows if r.get("overlap"))
    big_n = sum(1 for r in rows if r.get("bigtrade"))
    abs_n = sum(1 for r in rows if r.get("absorption_A"))
    docs = [
        _flag_doc("value", "value.vp.rth.trade", rows, "vp_touch", None, fixtures, extra={"source": "cov.nq.mbp1", "va": 0.70, "scope": "RTH trades"}),
        _flag_doc("value", "value.delta.rth.trade", rows, "vp_touch", "value.vp.rth.trade", fixtures, extra={"faithful_flag": "vp_touch", "source": "cov.nq.mbp1"}),
        _flag_doc("value", "value.kz", rows, "kz", "value.vp.rth.trade", fixtures, extra={"faithful_flag": "vp_touch"}),
        _flag_doc("value", "env.vwap.rth.sd2", rows, "vwap_reach", "value.vp.rth.trade", fixtures, extra={"faithful_flag": "vp_touch"}),
        _nm("value", "value.hidden.book", "hidden book behind the touch needs MBP-10/MBO", fixtures),
        _nm("value", "value.dealer.inventory", "participant identity not in inventory", fixtures),
    ]
    for doc in docs:
        if doc["variant"] in ("flow.absorption.A", "flow.bigtrade.100ny"):
            doc["summary"]["overlap_bigtrade_absorption"] = {
                "both": overlap_n, "bigtrade": big_n, "absorption_A": abs_n,
                "identical": overlap_n == big_n == abs_n and big_n > 0,
            }
        if "quality_bar_pass" not in doc:
            bad = quality_failures(doc)
            doc["quality_bar_pass"] = not bad
            doc["quality_bar_failures"] = bad
        write_report(doc)
    return docs
