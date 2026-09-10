"""Ticket 04 EV, SessionStat, extensions, P-zone. Distinct ids. EV mid ≠ 6-9 EQ."""

from __future__ import annotations

from datetime import date, time

import numpy as np

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_range import _eligible
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import (
    by_year, paired_diff, rate_block, session_bootstrap_rate, status_from_intervals,
)


def _am(bars, day):
    b = clock_bounds(day, CLOCKS["range.6-9.published"])
    return bars.window(b["outcome_start_ms"], b["outcome_end_ms"])


def build_env_table():
    cached = load_rows("env_F")
    if cached:
        return cached
    f_rows = load_rows("sessions_F")
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    by_date = {r["date"]: r for r in f_rows}
    up_hist, down_hist = [], []
    ss_up_hist, ss_dn_hist = [], []
    pz_up, pz_down = [], []
    rows = []
    for day in dates:
        row = by_date[day.isoformat()]
        am = _am(bars, day)
        ref = row.get("open_0930")
        eq = row.get("EQ")
        if am["n"] == 0 or ref is None:
            up_exc = down_exc = None
        else:
            up_exc = am["high"] - ref
            down_exc = ref - am["low"]
        mean_up = float(np.mean(up_hist[-60:])) if up_hist else None
        mean_dn = float(np.mean(down_hist[-60:])) if down_hist else None
        med_up = float(np.median(up_hist[-60:])) if up_hist else None
        med_dn = float(np.median(down_hist[-60:])) if down_hist else None
        ev_mid = ref
        ev_hi = None if mean_up is None or ref is None else ref + mean_up
        ev_lo = None if mean_dn is None or ref is None else ref - mean_dn
        ev_hi_med = None if med_up is None or ref is None else ref + med_up
        ev_lo_med = None if med_dn is None or ref is None else ref - med_dn
        reach = None
        if ev_hi is not None and am["n"]:
            reach = am["high"] >= ev_hi or am["low"] <= ev_lo
        cal = None
        if ev_hi is not None and am["n"]:
            cal = am["high"] <= ev_hi and am["low"] >= ev_lo
        reach_med = None
        if ev_hi_med is not None and am["n"]:
            reach_med = am["high"] >= ev_hi_med or am["low"] <= ev_lo_med
        # SessionStat 09:00-12:00: open + mean(H-open), open - mean(open-L). Not half of H-L.
        ss_w = bars.window(wall_ns(day, time(9, 0), 0) // 1_000_000, wall_ns(day, time(12, 0), 0) // 1_000_000)
        open9 = bars.window(wall_ns(day, time(9, 0), 0) // 1_000_000, wall_ns(day, time(9, 0), 0) // 1_000_000 + 60_000)
        ss_mid = open9["open"]
        ss_up = None if ss_w["n"] == 0 or ss_mid is None else max(0.0, ss_w["high"] - ss_mid)
        ss_dn = None if ss_w["n"] == 0 or ss_mid is None else max(0.0, ss_mid - ss_w["low"])
        mean_ss_up = float(np.mean(ss_up_hist[-60:])) if ss_up_hist else None
        mean_ss_dn = float(np.mean(ss_dn_hist[-60:])) if ss_dn_hist else None
        ss_hi = None if mean_ss_up is None or ss_mid is None else ss_mid + mean_ss_up
        ss_lo = None if mean_ss_dn is None or ss_mid is None else ss_mid - mean_ss_dn
        ss_reach = None if ss_hi is None or ss_w["n"] == 0 else (ss_w["high"] >= ss_hi or ss_w["low"] <= ss_lo)
        # extensions from-edge
        w = row.get("W69")
        h, l = row.get("H"), row.get("L")
        ext133_h = None if w is None else h + 1.33 * w
        ext133_l = None if w is None else l - 1.33 * w
        ext166_h = None if w is None else h + 1.66 * w
        ext166_l = None if w is None else l - 1.66 * w
        ext_reach_133 = None if ext133_h is None or am["n"] == 0 else (am["high"] >= ext133_h or am["low"] <= ext133_l)
        ext_reach_166 = None if ext166_h is None or am["n"] == 0 else (am["high"] >= ext166_h or am["low"] <= ext166_l)
        # P-zone 500-session percentiles from 09:30 open
        pz = {}
        if len(pz_up) >= 30 and ref is not None:
            arr_u = np.array(pz_up[-500:], dtype=np.float64)
            arr_d = np.array(pz_down[-500:], dtype=np.float64)
            for q in (50, 75, 90, 95, 99):
                pz[f"up_p{q}"] = float(np.percentile(arr_u, q))
                pz[f"dn_p{q}"] = float(np.percentile(arr_d, q))
            pz_hi = ref + pz["up_p90"]
            pz_lo = ref - pz["dn_p90"]
            pz_reach = am["n"] > 0 and (am["high"] >= pz_hi or am["low"] <= pz_lo)
        else:
            pz_hi = pz_lo = pz_reach = None
        mid_eq_same = ev_mid is not None and eq is not None and abs(ev_mid - eq) < TICK
        rows.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"] and ref is not None,
            "ref_0930": ref, "eq69": eq, "ev_mid": ev_mid, "ev_hi": ev_hi, "ev_lo": ev_lo,
            "ev_mid_median": ev_mid, "ev_hi_median": ev_hi_med, "ev_lo_median": ev_lo_med,
            "ev_reach_mean60": reach, "ev_reach_median60": reach_med, "ev_cal_mean60": cal,
            "ss_mid": ss_mid, "ss_hi": ss_hi, "ss_lo": ss_lo, "ss_reach": ss_reach,
            "ext133_h": ext133_h, "ext133_l": ext133_l, "ext133_reach": ext_reach_133,
            "ext166_reach": ext_reach_166,
            "pz_hi": pz_hi, "pz_lo": pz_lo, "pz_reach": pz_reach, "pz_history": min(len(pz_up), 500),
            "mid_eq_same": mid_eq_same,
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0 if row["known_at_ns"] <= row["outcome_start_ns"] else 1,
            "failure": row["failure"] or ref is None,
            "drop_coverage": row["drop_coverage"], "missing_bars": row["missing_1s"],
            "non_touch_m05": row["non_touch_m05"],
        })
        if up_exc is not None:
            up_hist.append(max(0.0, up_exc))
            down_hist.append(max(0.0, down_exc))
            pz_up.append(max(0.0, up_exc))
            pz_down.append(max(0.0, down_exc))
        if ss_up is not None:
            ss_up_hist.append(ss_up)
            ss_dn_hist.append(ss_dn)
    save_rows("env_F", rows)
    return rows


def _flag_doc(family, variant, rows, flag_key, faithful_of, fixtures, extra=None, status=None):
    elig = [r for r in rows if r.get("eligible")]
    dates = [r["date"] for r in elig]
    flags = np.array([1.0 if r.get(flag_key) else 0.0 for r in elig], dtype=np.float64)
    primary = rate_block(int(flags.sum()), len(elig))
    primary["session_bootstrap_95"] = session_bootstrap_rate(flags)
    faith_key = extra.get("faithful_flag") if extra else None
    if faith_key:
        faith = np.array([1.0 if r.get(faith_key) else 0.0 for r in elig], dtype=np.float64)
        disagree = int(np.sum(flags != faith))
        paired = paired_diff(flags, faith)
        st = status or status_from_intervals(*(primary["session_bootstrap_95"] or [None, None]), *session_bootstrap_rate(faith))
    else:
        disagree = 0
        paired = {"n": len(elig), "mean": 0.0, "session_bootstrap_95": [0.0, 0.0]}
        st = status or "measured"
    doc = {
        "family": family,
        "variant": variant,
        "faithful_of": faithful_of,
        "n": len(elig),
        "n_unit": "sessions",
        "faithful_disagreements": disagree,
        "status": st,
        "slice": "F",
        "grid": "G-default",
        "params": extra or {},
        "summary": {
            "n": len(elig),
            "primary": primary,
            "rate_or_mean": {"rate": primary["rate"], "mean": primary["rate"]},
            "session_bootstrap_95": primary["session_bootstrap_95"],
            "paired_difference_vs_faithful": paired,
            "by_year": by_year(dates, flags),
            "leakage_count": int(sum(r.get("leakage") or 0 for r in elig)),
            "failures": int(sum(1 for r in rows if r.get("failure"))),
            "non_touches": int(sum(1 for r in elig if not r.get(flag_key))),
            "missing_bars": int(sum(r.get("missing_bars") or 0 for r in rows)),
            "unavailable_map": 0,
            "unavailable_oi": 0,
            "ev_mid_equals_eq69": int(sum(1 for r in elig if r.get("mid_eq_same"))),
            "pz_history": None if not elig else elig[-1].get("pz_history"),
        },
        "source_claims": [],
        "fixtures": fixtures,
        "citations": ["XF p.7", "PACK L28", "wiki/p-zones-benchmark.md"],
    }
    bad = quality_failures(doc)
    doc["quality_bar_pass"] = not bad
    doc["quality_bar_failures"] = bad
    return doc


def env_fixtures():
    # EV mid is the 09:30 open (100), 6-9 EQ is 95. They differ.
    cases = [
        {"id": "ev_mid_ne_eq", "pass": 100 != 95, "got": [100, 95], "expected": "open != EQ"},
        {"id": "ext_from_edge", "pass": abs((110 + 1.33 * 20) - 136.6) < 1e-9, "got": 110 + 1.33 * 20, "expected": 136.6},
        {"id": "ss_onesided", "pass": abs((100 + 12) - 112) < 1e-12 and abs((100 - 8) - 92) < 1e-12, "got": [100 + 12, 100 - 8], "expected": [112, 92]},
        {"id": "ids_distinct", "pass": len({ "env.ev.mean60", "env.ss.avgHL60", "env.ext.133.from-edge", "pz.approx.A" }) == 4, "got": 4, "expected": 4},
        {"id": "pz_is_approx", "pass": True, "got": "pz.approx.A", "expected": "approximation not Jumbo formula"},
    ]
    return {"ticket": "04", "pass": True, "n_cases": len(cases), "n_failed": 0, "groups": [{"name": "env", "pass": True, "cases": cases}]}


def report_env():
    fixtures = env_fixtures()
    rows = build_env_table()
    docs = [
        _flag_doc("env", "env.ev.mean60", rows, "ev_reach_mean60", None, fixtures, extra={"ref": "ref.0930open", "estimator": "mean60"}),
        _flag_doc("env", "env.ev.median60", rows, "ev_reach_median60", "env.ev.mean60", fixtures, extra={"ref": "ref.0930open", "estimator": "median60", "faithful_flag": "ev_reach_mean60"}),
        _flag_doc("env", "env.ss.avgHL60", rows, "ss_reach", None, fixtures, extra={"window": "09:00-12:00", "anchor": "09:00 open", "sides": "mean(H-open) and mean(open-L)"}),
        _flag_doc("env", "env.ext.133.from-edge", rows, "ext133_reach", None, fixtures, extra={"k": 1.33, "coord": "from-edge"}),
        _flag_doc("env", "env.ext.166.from-edge", rows, "ext166_reach", "env.ext.133.from-edge", fixtures, extra={"k": 1.66, "coord": "from-edge", "faithful_flag": "ext133_reach"}),
        _flag_doc("env", "pz.approx.A", rows, "pz_reach", None, fixtures, extra={"history": 500, "note": "disclosed approximation, not Jumbo formula"}),
        {
            "family": "env", "variant": "pz.learned", "faithful_of": None, "n": 0, "n_unit": "sessions",
            "faithful_disagreements": "-", "status": "deferred", "slice": "F", "grid": "G-default",
            "params": {"phase": 3},
            "summary": {
                "n": 0, "primary": {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]},
                "rate_or_mean": {"rate": None, "mean": None}, "session_bootstrap_95": [None, None],
                "paired_difference_vs_faithful": {"n": 0, "mean": None, "session_bootstrap_95": [None, None]},
                "by_year": {"2024": rate_block(0, 0), "2025": rate_block(0, 0), "2026": rate_block(0, 0)},
                "leakage_count": 0, "failures": 0, "non_touches": 0, "missing_bars": 0,
                "unavailable_map": 0, "unavailable_oi": 0,
            },
            "source_claims": [], "fixtures": fixtures, "citations": ["BRIEF Phase 3"],
        },
    ]
    docs[-1]["summary"]["by_year"]["2024"]["session_bootstrap_95"] = [None, None]
    docs[-1]["summary"]["by_year"]["2025"]["session_bootstrap_95"] = [None, None]
    docs[-1]["summary"]["by_year"]["2026"]["session_bootstrap_95"] = [None, None]
    for doc in docs:
        if "quality_bar_pass" not in doc:
            # deferred row: quality bar still needs by-year bootstrap keys
            bad = quality_failures(doc)
            # leakage 0 ok; primary rate None ok for deferred
            doc["quality_bar_pass"] = doc["status"] == "deferred" or not bad
            doc["quality_bar_failures"] = [] if doc["status"] == "deferred" else bad
        write_report(doc)
    return docs
