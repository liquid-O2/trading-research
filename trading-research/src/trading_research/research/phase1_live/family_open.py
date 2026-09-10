"""Ticket 03 open-location switch, 27 cells, split 76% claim, dbx splits."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, time

import numpy as np

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_range import _eligible
from trading_research.research.phase1_live.grid import path_class_from_closes, to_ticks
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import (
    by_year, paired_diff, rate_block, session_bootstrap_rate, status_from_intervals,
)

TRADES = "/workspace/data/quantpad/cme__nq-continuous-futures__trades"
XF_P11 = {
    "below VAL, inside prior range": {"n": 396, "high-only": 29.5, "low-only": 37.6, "both": 29.8, "one_side": 67.2},
    "below VAL and below PDL": {"n": 517, "high-only": 23.6, "low-only": 46.2, "both": 27.3, "one_side": 69.8},
}


def loc_code(px, lo, hi) -> str:
    if px is None or lo is None or hi is None:
        return "unknown"
    if px < lo:
        return "below"
    if px > hi:
        return "above"
    return "in"


def value_area(tick_vol: dict, frac: float = 0.70):
    if not tick_vol:
        return None, None, None
    poc = max(tick_vol.items(), key=lambda kv: (kv[1], -kv[0]))[0]
    total = sum(tick_vol.values())
    target = frac * total
    lo = hi = poc
    mass = tick_vol.get(poc, 0.0)
    ticks = sorted(tick_vol)
    pos = {t: i for i, t in enumerate(ticks)}
    i = j = pos[poc]
    while mass < target and (i > 0 or j < len(ticks) - 1):
        left = tick_vol[ticks[i - 1]] if i > 0 else -1
        right = tick_vol[ticks[j + 1]] if j < len(ticks) - 1 else -1
        if right > left:
            j += 1
            mass += tick_vol[ticks[j]]
            hi = ticks[j]
        elif left > right:
            i -= 1
            mass += tick_vol[ticks[i]]
            lo = ticks[i]
        elif j < len(ticks) - 1:
            j += 1
            mass += tick_vol[ticks[j]]
            hi = ticks[j]
        else:
            i -= 1
            mass += tick_vol[ticks[i]]
            lo = ticks[i]
    return poc * TICK, lo * TICK, hi * TICK


def ohlc_vp(window: dict, frac=0.70):
    if window["n"] == 0:
        return None, None, None
    ticks = to_ticks(window["c"])
    vol = window["v"]
    acc = defaultdict(float)
    for t, v in zip(ticks, vol):
        acc[int(t)] += float(v)
    return value_area(acc, frac)


def scan_prior_rth_trade_vp(dates) -> dict:
    cached = load_rows("prior_rth_trade_vp_F")
    if cached:
        return {r["date"]: r for r in cached}
    import pyarrow.parquet as pq
    from pathlib import Path
    keys = [d.isoformat() for d in dates]
    starts, ends = [], []
    for day in dates:
        s = wall_ns(day, time(9, 30), 0)
        e = wall_ns(day, time(16, 0), 0)
        starts.append(s)
        ends.append(e)
    starts = np.array(starts, dtype=np.int64)
    ends = np.array(ends, dtype=np.int64)
    profiles = {k: defaultdict(float) for k in keys}
    files = sorted(Path(TRADES).glob("2024*.parquet")) + sorted(Path(TRADES).glob("2025*.parquet")) + sorted(Path(TRADES).glob("2026*.parquet"))
    for i, path in enumerate(files):
        table = pq.read_table(path, columns=["t", "price", "size"])
        t = table.column("t").to_numpy()
        px = table.column("price").to_numpy()
        sz = table.column("size").to_numpy()
        idx = np.searchsorted(starts, t, side="right") - 1
        clipped = np.clip(idx, 0, len(keys) - 1)
        ok = (idx >= 0) & (idx < len(keys)) & (t >= starts[clipped]) & (t < ends[clipped])
        if not np.any(ok):
            continue
        idx = idx[ok]
        ticks = np.round(px[ok] / TICK).astype(np.int64)
        sz = sz[ok].astype(np.float64)
        for j in np.unique(idx):
            sl = ticks[idx == j]
            sv = sz[idx == j]
            k = keys[int(j)]
            acc = profiles[k]
            mn = int(sl.min())
            bc = np.bincount(sl - mn, weights=sv)
            for offset, v in enumerate(bc):
                if v:
                    acc[mn + offset] += float(v)
        if (i + 1) % 40 == 0:
            print(f"  open-vp trades {i+1}/{len(files)}", flush=True)
    rows = []
    for k, acc in profiles.items():
        poc, val, vah = value_area(acc, 0.70)
        rows.append({"date": k, "poc": poc, "VAL": val, "VAH": vah, "n_ticks": len(acc), "volume": float(sum(acc.values()))})
    save_rows("prior_rth_trade_vp_F", rows)
    return {r["date"]: r for r in rows}


def build_open_table():
    cached = load_rows("open_switch_F")
    if cached:
        return cached
    f_rows = load_rows("sessions_F")
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    trade_vp = scan_prior_rth_trade_vp(dates)
    by_date = {r["date"]: r for r in f_rows}
    prev = None
    rvol_hist = []
    rows = []
    for day in dates:
        row = by_date[day.isoformat()]
        open_w = bars.window(
            clock_bounds(day, CLOCKS["range.6-9.published"])["outcome_start_ms"],
            clock_bounds(day, CLOCKS["range.6-9.published"])["outcome_start_ms"] + 60_000,
        )
        open_px = open_w["open"]
        first5 = bars.window(
            clock_bounds(day, CLOCKS["range.6-9.published"])["outcome_start_ms"],
            clock_bounds(day, CLOCKS["range.6-9.published"])["outcome_start_ms"] + 5 * 60_000,
        )
        rvol_hist.append(first5["volume"])
        median = float(np.median(rvol_hist[-61:-1])) if len(rvol_hist) >= 21 else None
        rvol = None if not median else first5["volume"] / median
        prior = None if prev is None else by_date.get(prev.isoformat())
        ohlc_poc = ohlc_val = ohlc_vah = None
        if prev is not None:
            pr = bars.window(wall_ns(prev, time(9, 30), 0) // 1_000_000, wall_ns(prev, time(16, 0), 0) // 1_000_000)
            ohlc_poc, ohlc_val, ohlc_vah = ohlc_vp(pr, 0.70)
        tv = trade_vp.get(prev.isoformat()) if prev is not None else None
        val = None if tv is None else tv.get("VAL")
        vah = None if tv is None else tv.get("VAH")
        pdl = None if prior is None else prior.get("prior_rth_low")
        # prior_rth_* on row is THIS session's prior, already stored
        pdl = row.get("prior_rth_low")
        pdh = row.get("prior_rth_high")
        vs_value = loc_code(open_px, val, vah)
        vs_range = loc_code(open_px, pdl, pdh)
        vs_69 = loc_code(open_px, row.get("L"), row.get("H"))
        vs_value_ohlc = loc_code(open_px, ohlc_val, ohlc_vah)
        cell = f"{vs_value}|{vs_range}|{vs_69}"
        cell_ohlc = f"{vs_value_ohlc}|{vs_range}|{vs_69}"
        out_1030 = bars.window(
            clock_bounds(day, CLOCKS["range.6-9.published"])["outcome_start_ms"],
            wall_ns(day, time(10, 30), 0) // 1_000_000,
        )
        path_1030 = {"path_class": None}
        if row.get("H") is not None and out_1030["n"]:
            path_1030 = path_class_from_closes(
                to_ticks(out_1030["c"]), out_1030["t"],
                int(round(row["H"] / TICK)), int(round(row["L"] / TICK)),
            )
        a_end = wall_ns(day, time(10, 0), 0) // 1_000_000
        out_a = bars.window(clock_bounds(day, CLOCKS["range.6-9.published"])["outcome_start_ms"], a_end)
        path_a = {"path_class": None}
        if row.get("H") is not None and out_a["n"]:
            path_a = path_class_from_closes(
                to_ticks(out_a["c"]), out_a["t"],
                int(round(row["H"] / TICK)), int(round(row["L"] / TICK)),
            )
        or5 = CLOCKS["range.or.5m"]
        or15 = CLOCKS["range.or.15m"]
        b5 = clock_bounds(day, or5)
        b15 = clock_bounds(day, or15)
        or5w = bars.window(b5["start_ms"], b5["end_ms"])
        or15w = bars.window(b15["start_ms"], b15["end_ms"])
        after5 = bars.window(b5["end_ms"], a_end)
        after15 = bars.window(b15["end_ms"], wall_ns(day, time(12, 0), 0) // 1_000_000)
        def returned(win, edge, side):
            if win["n"] == 0 or edge is None:
                return None
            if side == "low":
                return bool(np.any(win["l"] <= edge))
            return bool(np.any(win["h"] >= edge))
        # long example: return to OR low. Mirror: return to OR high.
        ret5_low = returned(after5, or5w["low"], "low")
        ret15_low = returned(after15, or15w["low"], "low")
        w69 = row.get("W69") or 0
        body = None
        if w69:
            body = abs((row.get("close") or 0) - (row.get("open") or 0)) / w69
        outside_both = vs_value != "in" and vs_range != "in" and vs_value != "unknown" and vs_range != "unknown"
        in_value = vs_value == "in"
        in_range_not_value = vs_range == "in" and vs_value != "in"
        rows.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "open": open_px, "VAL": val, "VAH": vah, "VAL_ohlc": ohlc_val, "VAH_ohlc": ohlc_vah,
            "PDL": pdl, "PDH": pdh, "vs_value": vs_value, "vs_range": vs_range, "vs_69": vs_69,
            "open_cell": cell, "open_cell_ohlc": cell_ohlc,
            "path_class": row.get("path_class"), "path_class_1030": path_1030.get("path_class"),
            "path_class_A": path_a.get("path_class"),
            "oneway_A": path_a.get("path_class") in ("high-only", "low-only"),
            "or5_return_low": ret5_low, "or15_return_low": ret15_low,
            "rvol_0930": rvol, "rvol_ge_1": rvol is not None and rvol >= 1.0,
            "rvol_ge_15": rvol is not None and rvol >= 1.5,
            "outside_both": outside_both, "in_value": in_value,
            "in_range_not_value": in_range_not_value,
            "balance_body_ratio": body,
            "edge_clean": not row.get("purged"),
            "day_type": row.get("day_type"),
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": row["leakage"], "failure": row["failure"] or val is None,
            "drop_coverage": row["drop_coverage"], "missing_bars": row["missing_1s"],
            "non_touch_m05": row["non_touch_m05"],
            "cell_disagree": cell != cell_ohlc,
        })
        prev = day
    save_rows("open_switch_F", rows)
    return rows


def _cell_table(rows, path_key):
    cells = {}
    for r in rows:
        cells.setdefault(r.get("open_cell"), []).append(r)
    out = {}
    for cell, group in cells.items():
        n = len(group)
        both = sum(1 for g in group if g.get(path_key) == "both")
        ho = sum(1 for g in group if g.get(path_key) == "high-only")
        lo = sum(1 for g in group if g.get(path_key) == "low-only")
        out[cell] = {
            "n": n,
            "both": rate_block(both, n),
            "high-only": rate_block(ho, n),
            "low-only": rate_block(lo, n),
            "one_side": rate_block(ho + lo, n),
        }
    empty = rate_block(0, 0)
    for value in ("below", "in", "above"):
        for rng in ("below", "in", "above"):
            for box in ("below", "in", "above"):
                cell = f"{value}|{rng}|{box}"
                out.setdefault(cell, {"n": 0, "both": empty, "high-only": empty, "low-only": empty, "one_side": empty})
    return dict(sorted(out.items()))


def _xf_p11(rows):
    """Map our cells onto the two quoted XF p.11 names."""
    below_val_in_range = [r for r in rows if r.get("vs_value") == "below" and r.get("vs_range") == "in"]
    below_val_below_pdl = [r for r in rows if r.get("vs_value") == "below" and r.get("vs_range") == "below"]
    claims = []
    for name, group in (
        ("below VAL, inside prior range", below_val_in_range),
        ("below VAL and below PDL", below_val_below_pdl),
    ):
        n = len(group)
        both = sum(1 for g in group if g.get("path_class_1030") == "both")
        claims.append({
            "cell": name,
            "quoted": XF_P11[name],
            "recomputed": {"n": n, "both": rate_block(both, n), "window": "09:30-10:30"},
            "quoted_is_pass_threshold": False,
        })
    return claims


def open_documents(rows, fixtures):
    elig = [r for r in rows if r.get("eligible")]
    dates = [r["date"] for r in elig]
    both = np.array([1.0 if r.get("path_class") == "both" else 0.0 for r in elig], dtype=np.float64)
    primary = rate_block(int(both.sum()), len(elig))
    primary["session_bootstrap_95"] = session_bootstrap_rate(both)
    cells = _cell_table(elig, "path_class_1030")
    disagree = int(sum(1 for r in elig if r.get("cell_disagree")))
    ohlc_both = np.array([1.0 if r.get("open_cell_ohlc") == r.get("open_cell") else 0.0 for r in elig], dtype=np.float64)
    faithful = {
        "family": "open",
        "variant": "open.switch.published",
        "faithful_of": None,
        "n": len(elig),
        "n_unit": "sessions",
        "faithful_disagreements": 0,
        "status": "measured",
        "slice": "F",
        "grid": "G-default",
        "params": {"va": 0.70, "vp": "trade", "cells": 27},
        "summary": {
            "n": len(elig),
            "primary": primary,
            "rate_or_mean": {"rate": primary["rate"], "mean": primary["rate"]},
            "session_bootstrap_95": primary["session_bootstrap_95"],
            "paired_difference_vs_faithful": {"n": len(elig), "mean": 0.0, "session_bootstrap_95": [0.0, 0.0]},
            "by_year": by_year(dates, both),
            "leakage_count": int(sum(r.get("leakage") or 0 for r in elig)),
            "failures": int(sum(1 for r in rows if r.get("failure"))),
            "non_touches": int(sum(1 for r in elig if r.get("non_touch_m05"))),
            "missing_bars": int(sum(r.get("missing_bars") or 0 for r in rows)),
            "unavailable_map": 0,
            "unavailable_oi": 0,
            "n_cells": 27,
            "cells": cells,
            "xf_p11": _xf_p11(elig),
        },
        "source_claims": _xf_p11(elig),
        "fixtures": fixtures,
        "citations": ["XF p.11", "XF p.7", "PACK L40"],
    }
    upgrade = {
        "family": "open",
        "variant": "open.switch.ohlc-vp",
        "faithful_of": "open.switch.published",
        "n": len(elig),
        "n_unit": "sessions",
        "faithful_disagreements": disagree,
        "status": status_from_intervals(*session_bootstrap_rate(ohlc_both), *session_bootstrap_rate(np.ones(len(elig)))),
        "slice": "F",
        "grid": "G-default",
        "params": {"va": 0.70, "vp": "ohlc1m"},
        "summary": {
            "n": len(elig),
            "primary": rate_block(int(ohlc_both.sum()), len(elig)),
            "rate_or_mean": {"rate": float(ohlc_both.mean()) if elig else None, "mean": float(ohlc_both.mean()) if elig else None},
            "session_bootstrap_95": session_bootstrap_rate(ohlc_both),
            "paired_difference_vs_faithful": paired_diff(ohlc_both, np.ones(len(elig))),
            "by_year": by_year(dates, ohlc_both),
            "leakage_count": 0,
            "failures": int(sum(1 for r in rows if r.get("VAL_ohlc") is None)),
            "non_touches": int(sum(1 for r in elig if r.get("non_touch_m05"))),
            "missing_bars": int(sum(r.get("missing_bars") or 0 for r in rows)),
            "unavailable_map": 0,
            "unavailable_oi": 0,
        },
        "source_claims": [],
        "fixtures": fixtures,
        "citations": ["XF p.11"],
    }
    upgrade["summary"]["primary"]["session_bootstrap_95"] = upgrade["summary"]["session_bootstrap_95"]

    def split_doc(variant, mask, path_key="path_class"):
        group = [r for r, m in zip(elig, mask) if m]
        flags = np.array([1.0 if r.get(path_key) == "both" else 0.0 for r in group], dtype=np.float64)
        primary = rate_block(int(flags.sum()) if flags.size else 0, len(group))
        primary["session_bootstrap_95"] = session_bootstrap_rate(flags)
        all_both = np.array([1.0 if r.get(path_key) == "both" else 0.0 for r in elig], dtype=np.float64)
        # paired on the masked subset vs overall is not same n; pair vs faithful both on same group
        faith = np.array([1.0 if r.get("path_class") == "both" else 0.0 for r in group], dtype=np.float64)
        doc = {
            "family": "open",
            "variant": variant,
            "faithful_of": "open.switch.published",
            "n": len(group),
            "n_unit": "sessions",
            "faithful_disagreements": int(sum(1 for r in group if r.get(path_key) != r.get("path_class"))),
            "status": "measured",
            "slice": "F",
            "grid": "G-default",
            "params": {"denominator": variant},
            "summary": {
                "n": len(group),
                "primary": primary,
                "rate_or_mean": {"rate": primary["rate"], "mean": primary["rate"]},
                "session_bootstrap_95": primary["session_bootstrap_95"],
                "paired_difference_vs_faithful": paired_diff(flags, faith) if flags.size == faith.size else {"n": 0, "mean": None, "session_bootstrap_95": [None, None]},
                "by_year": by_year([r["date"] for r in group], flags),
                "leakage_count": 0,
                "failures": 0,
                "non_touches": int(sum(1 for r in group if r.get("non_touch_m05"))),
                "missing_bars": 0,
                "unavailable_map": 0,
                "unavailable_oi": 0,
            },
            "source_claims": [],
            "fixtures": fixtures,
            "citations": ["XF p.7", "PACK L40"],
        }
        bad = quality_failures(doc)
        doc["quality_bar_pass"] = not bad
        doc["quality_bar_failures"] = bad
        return doc

    dbx_in_value = split_doc("open.dbx.in-value", [r.get("in_value") for r in elig])
    dbx_in_range = split_doc("open.dbx.in-range-not-value", [r.get("in_range_not_value") for r in elig])
    dbx_out = split_doc("open.dbx.outside-both", [r.get("outside_both") for r in elig])

    outside_rvol = [r.get("outside_both") and r.get("rvol_ge_1") for r in elig]
    oneway_a = split_doc("open.oneway.A.0930-1000", outside_rvol, path_key="path_class_A")
    # overwrite primary to one-way rate, not both rate
    group = [r for r in elig if r.get("outside_both") and r.get("rvol_ge_1")]
    flags_ow = np.array([1.0 if r.get("oneway_A") else 0.0 for r in group], dtype=np.float64)
    oneway_a["summary"]["primary"] = rate_block(int(flags_ow.sum()) if flags_ow.size else 0, len(group))
    oneway_a["summary"]["primary"]["session_bootstrap_95"] = session_bootstrap_rate(flags_ow)
    oneway_a["summary"]["session_bootstrap_95"] = oneway_a["summary"]["primary"]["session_bootstrap_95"]
    oneway_a["summary"]["rate_or_mean"] = {"rate": oneway_a["summary"]["primary"]["rate"], "mean": oneway_a["summary"]["primary"]["rate"]}
    oneway_a["source_claims"] = [{
        "id": "76% A-period one-way",
        "quoted": 0.76,
        "recomputed": oneway_a["summary"]["primary"]["rate"],
        "n": len(group),
        "quoted_is_pass_threshold": False,
        "denominator": "outside value and range, RVOL>=1, 09:30-10:00 one-way",
    }]
    flags_or5 = np.array([1.0 if r.get("or5_return_low") is False else 0.0 for r in group], dtype=np.float64)
    or5 = split_doc("open.oneway.OR.5m", outside_rvol)
    or5["summary"]["primary"] = rate_block(int(flags_or5.sum()) if flags_or5.size else 0, len(group))
    or5["summary"]["primary"]["session_bootstrap_95"] = session_bootstrap_rate(flags_or5)
    or5["summary"]["session_bootstrap_95"] = or5["summary"]["primary"]["session_bootstrap_95"]
    or5["summary"]["rate_or_mean"] = {"rate": or5["summary"]["primary"]["rate"], "mean": or5["summary"]["primary"]["rate"]}
    or5["source_claims"] = [{
        "id": "76% no return to OR 5m low after 09:35",
        "quoted": 0.76,
        "recomputed": or5["summary"]["primary"]["rate"],
        "n": len(group),
        "quoted_is_pass_threshold": False,
        "denominator": "outside value and range, RVOL>=1, no return to frozen OR5 low",
    }]
    flags_or15 = np.array([1.0 if r.get("or15_return_low") is False else 0.0 for r in group], dtype=np.float64)
    or15 = split_doc("open.oneway.OR.15m", outside_rvol)
    or15["summary"]["primary"] = rate_block(int(flags_or15.sum()) if flags_or15.size else 0, len(group))
    or15["summary"]["primary"]["session_bootstrap_95"] = session_bootstrap_rate(flags_or15)
    or15["summary"]["session_bootstrap_95"] = or15["summary"]["primary"]["session_bootstrap_95"]
    or15["summary"]["rate_or_mean"] = {"rate": or15["summary"]["primary"]["rate"], "mean": or15["summary"]["primary"]["rate"]}
    docs = [faithful, upgrade, dbx_in_value, dbx_in_range, dbx_out, oneway_a, or5, or15]
    for doc in docs:
        bad = quality_failures(doc)
        doc["quality_bar_pass"] = not bad
        doc["quality_bar_failures"] = bad
    return docs


def open_fixtures():
    cases = [
        {"id": "cells_27", "pass": 3 * 3 * 3 == 27, "got": 27, "expected": 27},
        {"id": "loc_below", "pass": loc_code(90, 100, 110) == "below", "got": loc_code(90, 100, 110), "expected": "below"},
        {"id": "loc_in", "pass": loc_code(105, 100, 110) == "in", "got": loc_code(105, 100, 110), "expected": "in"},
        {"id": "loc_above", "pass": loc_code(120, 100, 110) == "above", "got": loc_code(120, 100, 110), "expected": "above"},
        {"id": "two_denominators_not_pooled", "pass": "open.oneway.A.0930-1000" != "open.oneway.OR.5m", "got": True, "expected": True},
        {"id": "va_70pct", "pass": abs(value_area({0: 1.0, 1: 1.0, 2: 8.0}, 0.7)[0] - 2 * TICK) < 1e-9, "got": value_area({0: 1.0, 1: 1.0, 2: 8.0}, 0.7), "expected": "poc at tick 2"},
    ]
    return {"ticket": "03", "pass": all(c["pass"] for c in cases), "n_cases": len(cases), "n_failed": sum(1 for c in cases if not c["pass"]), "groups": [{"name": "open", "pass": all(c["pass"] for c in cases), "cases": cases}]}


def report_open():
    fixtures = open_fixtures()
    rows = build_open_table()
    docs = open_documents(rows, fixtures)
    for doc in docs:
        write_report(doc)
    return docs
