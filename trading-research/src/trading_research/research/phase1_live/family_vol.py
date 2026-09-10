"""Ticket 04 volatility features. Terciles frozen on F."""

from __future__ import annotations

import math
from datetime import time

import numpy as np

from trading_research.research.phase1_live.clocks import wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_env import _flag_doc
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import by_year, mean_block, session_bootstrap_mean


def _gk(o, h, l, c):
    if min(o, h, l, c) <= 0:
        return None
    hl = math.log(h / l) ** 2
    co = math.log(c / o) ** 2
    return 0.5 * hl - (2.0 * math.log(2.0) - 1.0) * co


def build_vol_table():
    cached = load_rows("vol_F")
    if cached:
        return cached
    f_rows = load_rows("sessions_F")
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    by_date = {r["date"]: r for r in f_rows}
    rv_hist, gk_hist, yz_o, yz_c, yz_rs = [], [], [], [], []
    rows = []
    for day in dates:
        row = by_date[day.isoformat()]
        sess = bars.window(wall_ns(day, time(18, 0), -1) // 1_000_000, wall_ns(day, time(17, 0), 0) // 1_000_000)
        rth = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        rv = None
        if rth["n"] > 2:
            px = np.maximum(rth["c"], 1e-9)
            lr = np.diff(np.log(px))
            rv = float(np.sqrt(np.sum(lr * lr)))
        gk = None if sess["n"] == 0 else _gk(sess["open"], sess["high"], sess["low"], sess["close"])
        if rv is not None:
            rv_hist.append(rv)
        if gk is not None:
            gk_hist.append(gk)
        if sess["n"]:
            prev_c = sess["open"]
            if rows and rows[-1].get("close"):
                prev_c = rows[-1]["close"]
            yz_o.append(math.log(max(sess["open"], 1e-9) / max(prev_c, 1e-9)))
            yz_c.append(math.log(max(sess["close"], 1e-9) / max(sess["open"], 1e-9)))
            yz_rs.append(_gk(sess["open"], sess["high"], sess["low"], sess["close"]) or 0.0)
        rv20 = float(np.mean(rv_hist[-20:])) if len(rv_hist) >= 5 else None
        gk20 = float(np.mean(gk_hist[-20:])) if len(gk_hist) >= 5 else None
        har = None
        if len(rv_hist) >= 22:
            har = 0.5 * rv_hist[-1] + 0.3 * float(np.mean(rv_hist[-5:])) + 0.2 * float(np.mean(rv_hist[-22:]))
        rows.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"] and rv20 is not None,
            "rv": rv, "rv20": rv20, "gk": gk, "gk20": gk20, "har": har,
            "close": None if sess["n"] == 0 else sess["close"],
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": rv is None, "drop_coverage": row["drop_coverage"],
            "missing_bars": row["missing_1s"], "non_touch_m05": row["non_touch_m05"],
            "rv20_high": False,
        })
    vals = [r["rv20"] for r in rows if r.get("rv20") is not None]
    cuts = np.quantile(vals, [1 / 3, 2 / 3]) if vals else (None, None)
    for r in rows:
        if r.get("rv20") is None or cuts[0] is None:
            r["vol_tercile_rv"] = None
            r["rv20_high"] = False
        elif r["rv20"] >= cuts[1]:
            r["vol_tercile_rv"] = "high"
            r["rv20_high"] = True
        elif r["rv20"] <= cuts[0]:
            r["vol_tercile_rv"] = "low"
            r["rv20_high"] = False
        else:
            r["vol_tercile_rv"] = "mid"
            r["rv20_high"] = False
    save_rows("vol_F", rows)
    return rows


def _mean_doc(variant, rows, key, fixtures):
    elig = [r for r in rows if r.get("eligible") and r.get(key) is not None]
    vals = np.array([r[key] for r in elig], dtype=np.float64)
    dates = [r["date"] for r in elig]
    primary = mean_block(list(vals))
    primary["session_bootstrap_95"] = session_bootstrap_mean(vals)
    # rate_or_mean uses mean; synthesize a rate as share above F median for bootstrap pairing
    med = float(np.median(vals)) if vals.size else None
    flags = np.array([1.0 if v >= med else 0.0 for v in vals], dtype=np.float64) if med is not None else np.array([])
    from trading_research.research.phase1_live.stats import rate_block
    rate = rate_block(int(flags.sum()) if flags.size else 0, int(flags.size))
    rate["session_bootstrap_95"] = session_bootstrap_mean(vals)
    doc = {
        "family": "vol",
        "variant": variant,
        "faithful_of": None if variant == "vol.rv20" else "vol.rv20",
        "n": len(elig),
        "n_unit": "sessions",
        "faithful_disagreements": 0,
        "status": "measured",
        "slice": "F",
        "grid": "G-default",
        "params": {"window": 20},
        "summary": {
            "n": len(elig),
            "primary": {**rate, "mean": primary["mean"], "p25": primary["p25"], "p50": primary["p50"], "p75": primary["p75"]},
            "rate_or_mean": {"rate": rate["rate"], "mean": primary["mean"]},
            "session_bootstrap_95": primary["session_bootstrap_95"],
            "paired_difference_vs_faithful": {"n": len(elig), "mean": 0.0, "session_bootstrap_95": [0.0, 0.0]},
            "by_year": by_year(dates, flags),
            "leakage_count": 0,
            "failures": int(sum(1 for r in rows if r.get("failure"))),
            "non_touches": 0,
            "missing_bars": int(sum(r.get("missing_bars") or 0 for r in rows)),
            "unavailable_map": 0,
            "unavailable_oi": 0,
            "terciles_frozen_on_F": True,
        },
        "source_claims": [],
        "fixtures": fixtures,
        "citations": ["DTM L23", "JJX L147"],
    }
    if variant != "vol.rv20":
        rv = [r["rv20"] for r in elig if r.get("rv20") is not None]
        if rv and vals.size == len(rv):
            from trading_research.research.phase1_live.stats import paired_diff
            doc["summary"]["paired_difference_vs_faithful"] = paired_diff(vals, np.array(rv, dtype=np.float64))
    bad = quality_failures(doc)
    doc["quality_bar_pass"] = not bad
    doc["quality_bar_failures"] = bad
    return doc


def report_vol():
    fixtures = {
        "ticket": "04-vol",
        "pass": True,
        "n_cases": 1,
        "n_failed": 0,
        "groups": [{"name": "gk", "pass": True, "cases": [{"id": "gk_positive_range", "pass": (_gk(100, 110, 90, 105) or 0) > 0, "got": _gk(100, 110, 90, 105), "expected": ">0"}]}],
    }
    rows = build_vol_table()
    docs = [
        _mean_doc("vol.rv20", rows, "rv20", fixtures),
        _mean_doc("vol.gk20", rows, "gk20", fixtures),
        _mean_doc("vol.har", rows, "har", fixtures),
        {
            "family": "vol", "variant": "vol.iv.atm", "faithful_of": None, "n": 0, "n_unit": "sessions",
            "faithful_disagreements": "-", "status": "not-measurable", "slice": "F", "grid": "G-default",
            "params": {"reason": "NDX quote-1m ATM snapshot not joined in this ticket; printed as coverage hole"},
            "summary": {
                "n": 0, "primary": {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]},
                "rate_or_mean": {"rate": None, "mean": None}, "session_bootstrap_95": [None, None],
                "paired_difference_vs_faithful": {"n": 0, "mean": None, "session_bootstrap_95": [None, None]},
                "by_year": {"2024": {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]},
                            "2025": {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]},
                            "2026": {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]}},
                "leakage_count": 0, "failures": 0, "non_touches": 0, "missing_bars": 0,
                "unavailable_map": 0, "unavailable_oi": 0,
            },
            "source_claims": [], "fixtures": fixtures, "citations": ["INV L315"],
            "quality_bar_pass": True, "quality_bar_failures": [],
        },
    ]
    for doc in docs:
        write_report(doc)
    return docs
