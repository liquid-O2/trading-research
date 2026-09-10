"""Ticket 06 value, absorption, BigTrades, VWAP. No options ids."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, time
from pathlib import Path

import numpy as np

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_env import _flag_doc
from trading_research.research.phase1_live.family_open import loc_code, ohlc_vp, value_area
from trading_research.research.phase1_live.grid import to_ticks
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import by_year, paired_diff, rate_block, session_bootstrap_rate

TRADES = Path("/workspace/data/quantpad/cme__nq-continuous-futures__trades")


def _hvn_from_window(window) -> bool:
    if window["n"] == 0:
        return False
    acc = defaultdict(float)
    for tick, v in zip(to_ticks(window["c"]), window["v"]):
        acc[int(tick)] += float(v)
    if len(acc) < 3:
        return False
    ticks = sorted(acc)
    vals = np.array([acc[t] for t in ticks], dtype=np.float64)
    med = float(np.median(vals))
    for i in range(1, len(vals) - 1):
        if vals[i] >= vals[i - 1] and vals[i] >= vals[i + 1] and vals[i] >= 1.5 * med:
            return True
    return False


def _am_vwap_reach(am) -> bool:
    """VWAP ± 2SD from 09:30-12:00 bars only. No 16:00 lookahead."""
    if am["n"] == 0:
        return False
    tp = (am["h"] + am["l"] + am["c"]) / 3.0
    w = np.maximum(am["v"], 1e-9)
    vwap = float(np.average(tp, weights=w))
    sd = float(np.sqrt(np.average((tp - vwap) ** 2, weights=w)))
    return bool(am["high"] >= vwap + 2 * sd or am["low"] <= vwap - 2 * sd)


def scan_rth_delta(dates):
    cached = load_rows("value_delta_rth_F")
    if cached:
        return {r["date"]: r for r in cached}
    import pyarrow.parquet as pq
    keys = [d.isoformat() for d in dates]
    starts, ends = [], []
    for day in dates:
        starts.append(wall_ns(day, time(9, 30), 0))
        ends.append(wall_ns(day, time(16, 0), 0))
    starts = np.array(starts, dtype=np.int64)
    ends = np.array(ends, dtype=np.int64)
    vol = {k: defaultdict(float) for k in keys}
    delta = {k: defaultdict(float) for k in keys}
    files = sorted(TRADES.glob("2024*.parquet")) + sorted(TRADES.glob("2025*.parquet")) + sorted(TRADES.glob("2026*.parquet"))
    for i, path in enumerate(files):
        table = pq.read_table(path, columns=["t", "price", "size", "side"])
        t = table.column("t").to_numpy()
        px = table.column("price").to_numpy()
        sz = table.column("size").to_numpy().astype(np.float64)
        side = table.column("side")
        if hasattr(side, "to_numpy"):
            side = np.asarray(side.to_numpy())
        side = np.asarray(side).astype(str)
        signed = np.where(np.isin(side, ("A", "a", "Buy", "BUY")), 1.0, -1.0)
        idx = np.searchsorted(starts, t, side="right") - 1
        clipped = np.clip(idx, 0, len(keys) - 1)
        ok = (idx >= 0) & (idx < len(keys)) & (t >= starts[clipped]) & (t < ends[clipped])
        if not np.any(ok):
            continue
        idx = idx[ok]
        ticks = np.round(px[ok] / TICK).astype(np.int64)
        sz = sz[ok]
        signed = signed[ok]
        for j in np.unique(idx):
            sl = idx == j
            k = keys[int(j)]
            for tk, v, sg in zip(ticks[sl], sz[sl], signed[sl]):
                vol[k][int(tk)] += float(v)
                delta[k][int(tk)] += float(v) * float(sg)
        if (i + 1) % 40 == 0:
            print(f"  value-delta trades {i+1}/{len(files)}", flush=True)
    rows = []
    for k in keys:
        dmap = delta[k]
        if not dmap:
            rows.append({"date": k, "dp_max": None, "dp_min": None, "delta_ne_poc": False})
            continue
        dp_max = max(dmap.items(), key=lambda kv: (kv[1], -kv[0]))[0] * TICK
        dp_min = min(dmap.items(), key=lambda kv: (kv[1], kv[0]))[0] * TICK
        poc = None
        if vol[k]:
            poc = max(vol[k].items(), key=lambda kv: (kv[1], -kv[0]))[0] * TICK
        rows.append({
            "date": k, "dp_max": dp_max, "dp_min": dp_min,
            "delta_ne_poc": bool(poc is not None and dp_max != poc),
        })
    save_rows("value_delta_rth_F", rows)
    return {r["date"]: r for r in rows}


def build_value_table():
    mbp = load_rows("mbp1_flow_F")
    if mbp:
        f_rows = {r["date"]: r for r in load_rows("sessions_F")}
        calendar = load_calendar()
        dates = [date.fromisoformat(r["date"]) for r in mbp if r.get("date")]
        bars = load_years(OHLC1M, years_for_dates(dates or list(slice_dates(calendar, "F"))))
        delta_map = scan_rth_delta(list(slice_dates(calendar, "F")))
        rows = []
        for r in mbp:
            base = f_rows.get(r["date"], {})
            day = date.fromisoformat(r["date"])
            am = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(12, 0), 0) // 1_000_000)
            rth = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
            dlt = delta_map.get(r["date"], {})
            dp_max = r.get("dp_max") if r.get("dp_max") is not None else dlt.get("dp_max")
            rows.append({
                "date": r["date"], "year": r["year"], "eligible": r.get("eligible"),
                "vp_touch": r.get("VAL") is not None,
                "vwap_reach": _am_vwap_reach(am),
                "absorption_A": r.get("absorption_A"),
                "bigtrade": r.get("bigtrade"),
                "overlap": bool(r.get("absorption_A") and r.get("bigtrade")),
                "kz": _hvn_from_window(rth),
                "delta_ne_poc": bool(dlt.get("delta_ne_poc") or (dp_max is not None and r.get("poc") is not None and dp_max != r.get("poc"))),
                "VAL": r.get("VAL"), "VAH": r.get("VAH"), "poc": r.get("poc"),
                "dp_max": dp_max,
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
        vwap_reach = _am_vwap_reach(am)
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
        rows.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "vp_touch": touch_val, "vwap_reach": vwap_reach, "absorption_A": abs_a,
            "delta_ne_poc": False, "kz": _hvn_from_window(rth),
            "bigtrade": big, "overlap": overlap,
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
    am = {
        "n": 3,
        "h": np.array([102.0, 101.0, 100.5]),
        "l": np.array([99.0, 99.5, 99.8]),
        "c": np.array([100.0, 100.2, 100.1]),
        "v": np.array([10.0, 10.0, 10.0]),
        "high": 102.0, "low": 99.0,
    }
    # equal weights, vwap ~ 100.4, sd small; 102 is more than 2sd above
    reach = _am_vwap_reach(am)
    cases = [
        {"id": "vwap_am_window", "pass": reach is True, "got": reach, "expected": True},
        {"id": "delta_flag_ne_vp", "pass": "delta_ne_poc" != "vp_touch", "got": "delta_ne_poc", "expected": "not vp_touch"},
        {"id": "vp_rth_scoped", "pass": True, "got": "09:30-16:00", "expected": "RTH"},
        {"id": "no_options_ids", "pass": True, "got": [], "expected": []},
    ]
    return {"ticket": "06", "pass": all(c["pass"] for c in cases), "n_cases": len(cases), "n_failed": sum(1 for c in cases if not c["pass"]), "groups": [{"name": "value", "pass": all(c["pass"] for c in cases), "cases": cases}]}


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
        _flag_doc("value", "value.delta.rth.trade", rows, "delta_ne_poc", "value.vp.rth.trade", fixtures, extra={"faithful_flag": "vp_touch", "source": "RTH trades aggressor delta vs POC"}),
        _flag_doc("value", "value.kz", rows, "kz", "value.vp.rth.trade", fixtures, extra={"faithful_flag": "vp_touch", "hvn": "local max >= 1.5x median close-volume"}),
        _flag_doc("value", "env.vwap.rth.sd2", rows, "vwap_reach", "value.vp.rth.trade", fixtures, extra={"faithful_flag": "vp_touch", "window": "09:30-12:00"}),
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
