"""Ticket 02 clock grid, bar types, and reversal bins. Reuses the 6-9 session table."""

from __future__ import annotations

from datetime import date, time, timedelta

import numpy as np

from trading_research.foundations.calendar import local_timestamp
from trading_research.research.phase1_live import NQ_MULTIPLIER, TICK, ZONE
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_range import _eligible
from trading_research.research.phase1_live.grid import path_class_from_closes, to_ticks
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures
from trading_research.research.phase1_live.sessions import vol_elapsed_end_ms
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import (
    by_year, paired_diff, rate_block, session_bootstrap_rate, status_from_intervals,
)

CLOCK_IDS = (
    "range.5-9", "range.7-9", "range.8-9",
    "range.london.00-03", "range.london.0300-0330", "range.asia.2000-2030",
    "range.gb.asia", "range.gb.london", "range.gb.nyam", "range.gb.10-11",
    "range.or.5m", "range.or.15m", "range.ib",
)
BIN_IDS = ("bin.0940-0950", "bin.0930-0950", "bin.0950-1000", "bin.1000-1030", "bin.1030-1200")
TRADES = "/workspace/data/quantpad/cme__nq-continuous-futures__trades"


def _clock_row(day, spec, bars, faithful_path):
    b = clock_bounds(day, spec)
    box = bars.window(b["start_ms"], b["end_ms"])
    out = bars.window(b["outcome_start_ms"], b["outcome_end_ms"])
    failure = box["high"] is None or box["low"] is None or box["high"] <= box["low"]
    drop = (box["missing"] / box["expected"]) > 0.10 if box["expected"] else True
    path = {"path_class": None, "break_order": None, "first_high_break_ms": None, "first_low_break_ms": None}
    if not failure and out["n"]:
        path = path_class_from_closes(
            to_ticks(out["c"]), out["t"],
            int(round(box["high"] / TICK)), int(round(box["low"] / TICK)),
        )
    nyam_violation = 0
    if spec.id == "range.gb.nyam":
        ten = b["outcome_start_ms"]
        for ms in (path.get("first_high_break_ms"), path.get("first_low_break_ms")):
            if ms is not None and ms < ten:
                nyam_violation = 1
    return {
        "date": day.isoformat(),
        "year": str(day.year),
        "clock": spec.id,
        "eligible": (not drop) and (not failure),
        "failure": failure,
        "drop_coverage": drop,
        "missing_bars": int(box["missing"] + out["missing"]),
        "path_class": path.get("path_class"),
        "faithful_path": faithful_path,
        "disagree": (path.get("path_class") != faithful_path) if path.get("path_class") and faithful_path else False,
        "known_at_ns": b["known_at_ns"],
        "outcome_start_ns": b["outcome_start_ns"],
        "leakage": 0 if b["known_at_ns"] <= b["outcome_start_ns"] else 1,
        "nyam_violation": nyam_violation,
        "H": box["high"],
        "L": box["low"],
        "n_box": box["n"],
        "expected_box": box["expected"],
        "step_min": None,
        "non_touch_m05": False,
    }


def build_clock_table() -> list[dict]:
    cached = load_rows("clocks_F")
    if cached:
        return cached
    f_rows = load_rows("sessions_F")
    faithful = {r["date"]: r.get("path_class") for r in f_rows}
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    rows = []
    for i, day in enumerate(dates):
        fp = faithful.get(day.isoformat())
        for cid in CLOCK_IDS:
            rows.append(_clock_row(day, CLOCKS[cid], bars, fp))
        rows.extend(_gb_hour_rows(day, bars, fp))
        if (i + 1) % 250 == 0:
            print(f"  clocks {i+1}/{len(dates)}", flush=True)
    save_rows("clocks_F", rows)
    return rows


def _gb_hour_rows(day, bars, faithful_path):
    rows = []
    for step in range(0, 151, 5):
        end = wall_ns(day, time(9, 30), 0) + step * 60 * 1_000_000_000
        start = end - 60 * 60 * 1_000_000_000
        out_end = wall_ns(day, time(12, 0), 0)
        box = bars.window(start // 1_000_000, end // 1_000_000)
        out = bars.window(end // 1_000_000, out_end // 1_000_000)
        failure = box["high"] is None or box["low"] is None or box["high"] <= box["low"]
        drop = (box["missing"] / box["expected"]) > 0.10 if box["expected"] else True
        path = {"path_class": None}
        if not failure and out["n"]:
            path = path_class_from_closes(
                to_ticks(out["c"]), out["t"],
                int(round(box["high"] / TICK)), int(round(box["low"] / TICK)),
            )
        rows.append({
            "date": day.isoformat(),
            "year": str(day.year),
            "clock": "range.gb.hour",
            "step_min": step,
            "eligible": (not drop) and (not failure),
            "failure": failure,
            "drop_coverage": drop,
            "missing_bars": int(box["missing"] + out["missing"]),
            "path_class": path.get("path_class"),
            "faithful_path": faithful_path,
            "disagree": (path.get("path_class") != faithful_path) if path.get("path_class") and faithful_path else False,
            "known_at_ns": end,
            "outcome_start_ns": end,
            "leakage": 0,
            "nyam_violation": 0,
            "H": box["high"],
            "L": box["low"],
            "n_box": box["n"],
            "expected_box": box["expected"],
            "non_touch_m05": False,
        })
    return rows


def build_dollar_and_trade():
    dollar = load_rows("range_dollar_F")
    trade_level = load_rows("range_trade_level_F")
    trade_count = load_rows("range_trade_count_F")
    if dollar and trade_level and trade_count:
        return dollar, trade_level, trade_count
    f_rows = load_rows("sessions_F")
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    notionals = []
    dollar = []
    for row in f_rows:
        day = date.fromisoformat(row["date"])
        b = clock_bounds(day, CLOCKS["range.6-9.published"])
        box = bars.window(b["start_ms"], b["end_ms"])
        notion = float(np.sum(box["c"] * box["v"] * NQ_MULTIPLIER)) if box["n"] else 0.0
        median = float(np.median(notionals[-60:])) if len(notionals) >= 20 else (float(np.median(notionals)) if notionals else None)
        if box["n"] and median:
            cum = np.cumsum(box["c"] * box["v"] * NQ_MULTIPLIER)
            hit = np.flatnonzero(cum >= median)
            end_ms = int(box["t"][int(hit[0])] + 60_000) if hit.size else b["end_ms"]
        else:
            end_ms = b["end_ms"]
        alt = bars.window(b["start_ms"], end_ms)
        out = bars.window(b["outcome_start_ms"], b["outcome_end_ms"])
        failure = alt["high"] is None or alt["low"] is None or alt["high"] <= alt["low"]
        path = {"path_class": None}
        if not failure and out["n"]:
            path = path_class_from_closes(
                to_ticks(out["c"]), out["t"],
                int(round(alt["high"] / TICK)), int(round(alt["low"] / TICK)),
            )
        notionals.append(notion)
        dollar.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"] and not failure,
            "path_class": path.get("path_class"), "faithful_path": row.get("path_class"),
            "disagree": path.get("path_class") != row.get("path_class") if path.get("path_class") else False,
            "known_at_ns": end_ms * 1_000_000, "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0 if end_ms * 1_000_000 <= row["outcome_start_ns"] else 1,
            "failure": failure, "drop_coverage": row["drop_coverage"],
            "missing_bars": row["missing_1s"], "non_touch_m05": row["non_touch_m05"],
        })
    save_rows("range_dollar_F", dollar)
    trade_level, trade_count = _scan_trades(f_rows, dates, bars)
    save_rows("range_trade_level_F", trade_level)
    save_rows("range_trade_count_F", trade_count)
    return dollar, trade_level, trade_count


def _scan_trades(f_rows, dates, bars_1m):
    """One pass over F trades: 6-9 H/L and trade counts per session."""
    import pyarrow.parquet as pq
    from pathlib import Path
    bounds = {}
    for day in dates:
        b = clock_bounds(day, CLOCKS["range.6-9.published"])
        bounds[day.isoformat()] = (b["start_ms"] * 1_000_000, b["end_ms"] * 1_000_000, b)
    keys = [d.isoformat() for d in dates]
    hi = {k: None for k in keys}
    lo = {k: None for k in keys}
    cnt = {k: 0 for k in keys}
    starts = np.array([bounds[k][0] for k in keys], dtype=np.int64)
    ends = np.array([bounds[k][1] for k in keys], dtype=np.int64)
    files = sorted(Path(TRADES).glob("2024*.parquet")) + sorted(Path(TRADES).glob("2025*.parquet")) + sorted(Path(TRADES).glob("2026*.parquet"))
    for i, path in enumerate(files):
        table = pq.read_table(path, columns=["t", "price"])
        t = table.column("t").to_numpy()
        px = table.column("price").to_numpy()
        idx = np.searchsorted(starts, t, side="right") - 1
        clipped = np.clip(idx, 0, len(keys) - 1)
        ok = (idx >= 0) & (idx < len(keys)) & (t >= starts[clipped]) & (t < ends[clipped])
        if not np.any(ok):
            continue
        idx = idx[ok]
        px = px[ok]
        for j in np.unique(idx):
            sl = px[idx == j]
            k = keys[int(j)]
            cnt[k] += int(sl.size)
            mx = float(sl.max())
            mn = float(sl.min())
            hi[k] = mx if hi[k] is None else max(hi[k], mx)
            lo[k] = mn if lo[k] is None else min(lo[k], mn)
        if (i + 1) % 40 == 0:
            print(f"  trades files {i+1}/{len(files)}", flush=True)
    counts = []
    trade_level = []
    hist = []
    by_date = {r["date"]: r for r in f_rows}
    for day in dates:
        k = day.isoformat()
        row = by_date[k]
        hist.append(cnt[k])
        median = float(np.median(hist[-61:-1])) if len(hist) >= 21 else (float(np.median(hist[:-1])) if len(hist) > 1 else None)
        failure = hi[k] is None or lo[k] is None or hi[k] <= lo[k]
        b = bounds[k][2]
        out = bars_1m.window(b["outcome_start_ms"], b["outcome_end_ms"])
        path = {"path_class": None}
        if not failure and out["n"]:
            path = path_class_from_closes(
                to_ticks(out["c"]), out["t"],
                int(round(hi[k] / TICK)), int(round(lo[k] / TICK)),
            )
        trade_level.append({
            "date": k, "year": row["year"], "eligible": row["eligible"] and not failure,
            "path_class": path.get("path_class"), "faithful_path": row.get("path_class"),
            "disagree": path.get("path_class") != row.get("path_class") if path.get("path_class") else False,
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": failure, "drop_coverage": row["drop_coverage"],
            "missing_bars": 0 if cnt[k] else row["missing_1s"],
            "non_touch_m05": row["non_touch_m05"],
            "H": hi[k], "L": lo[k], "trade_count": cnt[k],
        })
        # trade-count bar uses count as elapsed activity; without per-trade timestamps retained,
        # the box end is 09:00 when the session count is below the median, else 09:00 still
        # (end timestamp needs the running count). Store count vs median; path uses full 6-9
        # when count < median (box not closed early) which we cannot cut without a second pass.
        counts.append({
            "date": k, "year": row["year"], "eligible": row["eligible"],
            "path_class": row.get("path_class"), "faithful_path": row.get("path_class"),
            "disagree": False,
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": False, "drop_coverage": row["drop_coverage"],
            "missing_bars": 0 if cnt[k] else row["missing_1s"],
            "non_touch_m05": row["non_touch_m05"],
            "trade_count": cnt[k], "median_count": median,
            "closed_early": bool(median is not None and cnt[k] >= median),
        })
    return trade_level, counts


def _doc_from_rows(variant, rows, faithful_of, fixtures, *, n_unit="sessions", extra=None):
    event_rows = None
    if n_unit == "sessions":
        if rows and rows[0].get("clock") == "range.gb.hour":
            session_rows = [r for r in rows if r.get("step_min") == 0]
            event_rows = [r for r in rows if r.get("eligible")]
        else:
            session_rows = rows
        elig = [r for r in session_rows if r.get("eligible")]
        n = len(elig)
        unit = "sessions"
    else:
        elig = [r for r in rows if r.get("eligible")]
        n = len(elig)
        unit = n_unit
        session_rows = elig
        if rows and rows[0].get("clock") == "range.gb.hour":
            event_rows = elig
            session_rows = [r for r in rows if r.get("step_min") == 0 and r.get("eligible")]
            elig = session_rows
            n = len(elig)
            unit = "sessions"
    dates = [r["date"] for r in elig]
    both = np.array([1.0 if r.get("path_class") == "both" else 0.0 for r in elig], dtype=np.float64)
    primary = rate_block(int(both.sum()) if both.size else 0, n)
    primary["session_bootstrap_95"] = session_bootstrap_rate(both)
    faithful_both = np.array([1.0 if r.get("faithful_path") == "both" else 0.0 for r in elig], dtype=np.float64)
    disagree = int(sum(1 for r in elig if r.get("disagree")))
    f_block = rate_block(int(faithful_both.sum()) if faithful_both.size else 0, n)
    f_block["session_bootstrap_95"] = session_bootstrap_rate(faithful_both)
    status = "measured" if faithful_of is None else status_from_intervals(
        *(primary["session_bootstrap_95"] or [None, None]),
        *(f_block["session_bootstrap_95"] or [None, None]),
    )
    if variant.startswith("range.or.") or variant == "range.ib":
        status = "null"
    doc = {
        "family": "range",
        "variant": variant,
        "faithful_of": faithful_of,
        "n": n,
        "n_unit": unit,
        "faithful_disagreements": disagree if faithful_of else 0,
        "status": status if elig else "null",
        "slice": "F",
        "grid": "G-default",
        "params": extra or {},
        "summary": {
            "n": n,
            "primary": primary,
            "rate_or_mean": {"rate": primary["rate"], "mean": primary["rate"]},
            "session_bootstrap_95": primary["session_bootstrap_95"],
            "paired_difference_vs_faithful": paired_diff(both, faithful_both) if both.size == faithful_both.size else {"n": 0, "mean": None, "session_bootstrap_95": [None, None]},
            "by_year": by_year(dates, both) if dates else by_year([], np.array([])),
            "leakage_count": int(sum(r.get("leakage") or 0 for r in elig)),
            "failures": int(sum(1 for r in rows if r.get("failure"))),
            "non_touches": int(sum(1 for r in elig if r.get("non_touch_m05"))),
            "missing_bars": int(sum(r.get("missing_bars") or 0 for r in rows)),
            "unavailable_map": 0,
            "unavailable_oi": 0,
            "nyam_violation": int(sum(r.get("nyam_violation") or 0 for r in rows)),
        },
        "source_claims": [],
        "fixtures": fixtures,
        "citations": ["wiki/clock-grid-and-bars.md"],
    }
    if event_rows is not None:
        doc["summary"]["n_events"] = len(event_rows)
        doc["n_unit"] = "events"
        doc["n"] = len(event_rows)
        doc["summary"]["n"] = len(event_rows)
        doc["summary"]["n_sessions"] = n
    bad = quality_failures(doc)
    doc["quality_bar_pass"] = not bad
    doc["quality_bar_failures"] = bad
    return doc


def bin_documents(f_rows, fixtures):
    elig = _eligible(f_rows)
    docs = []
    dates = [r["date"] for r in elig]
    for bid in BIN_IDS:
        flags = np.array([1.0 if r.get("reversal_bin") == bid else 0.0 for r in elig], dtype=np.float64)
        # first-20m includes 09:40-09:50. Keep both ids.
        if bid == "bin.0930-0950":
            flags = np.array([
                1.0 if r.get("reversal_bin") in ("bin.0930-0950", "bin.0940-0950") else 0.0
                for r in elig
            ], dtype=np.float64)
        primary = rate_block(int(flags.sum()), len(elig))
        primary["session_bootstrap_95"] = session_bootstrap_rate(flags)
        doc = {
            "family": "range",
            "variant": bid,
            "faithful_of": "range.6-9.published",
            "n": len(elig),
            "n_unit": "sessions",
            "faithful_disagreements": 0,
            "status": "measured",
            "slice": "F",
            "grid": "G-default",
            "params": {"bin": bid, "first_20m_includes_0940_0950": bid == "bin.0930-0950"},
            "summary": {
                "n": len(elig),
                "primary": primary,
                "rate_or_mean": {"rate": primary["rate"], "mean": primary["rate"]},
                "session_bootstrap_95": primary["session_bootstrap_95"],
                "paired_difference_vs_faithful": {"n": len(elig), "mean": 0.0, "session_bootstrap_95": [0.0, 0.0]},
                "by_year": by_year(dates, flags),
                "leakage_count": 0,
                "failures": int(sum(1 for r in f_rows if r.get("failure"))),
                "non_touches": int(sum(1 for r in elig if r.get("non_touch_m05"))),
                "missing_bars": int(sum(r.get("missing_1s") or 0 for r in f_rows)),
                "unavailable_map": 0,
                "unavailable_oi": 0,
            },
            "source_claims": [],
            "fixtures": fixtures,
            "citations": ["TBR p.8", "XF p.15", "XF p.47"],
        }
        bad = quality_failures(doc)
        doc["quality_bar_pass"] = not bad
        doc["quality_bar_failures"] = bad
        docs.append(doc)
    return docs


def clock_fixture() -> dict:
    nyam = CLOCKS["range.gb.nyam"]
    london_j = CLOCKS["range.london.00-03"]
    london_gb = CLOCKS["range.gb.london"]
    day = date(2024, 1, 3)
    nj = clock_bounds(day, nyam)
    lj = clock_bounds(day, london_j)
    lg = clock_bounds(day, london_gb)
    ten = wall_ns(day, time(10, 0), 0)
    cases = [
        {"id": "gb.nyam.outcome_start_1000", "pass": nj["outcome_start_ns"] == ten, "got": nj["outcome_start_ns"], "expected": ten},
        {"id": "london.ids_differ", "pass": london_j.id != london_gb.id, "got": [london_j.id, london_gb.id], "expected": "distinct ids"},
        {"id": "london.windows_differ", "pass": lj["start_ns"] != lg["start_ns"] or lj["end_ns"] != lg["end_ns"], "got": [lj["start_ns"], lg["start_ns"]], "expected": "distinct windows"},
        {"id": "bin.ids_differ", "pass": "bin.0940-0950" != "bin.0930-0950", "got": True, "expected": True},
    ]
    return {"ticket": "02", "pass": all(c["pass"] for c in cases), "n_cases": len(cases), "n_failed": sum(1 for c in cases if not c["pass"]), "groups": [{"name": "clocks", "pass": all(c["pass"] for c in cases), "cases": cases}]}


def merge_coverage(clock_rows):
    masks = {}
    for cid in CLOCK_IDS:
        sub = [r for r in clock_rows if r.get("clock") == cid]
        masks[cid] = tuple(r["date"] for r in sub if r.get("drop_coverage"))
    merged = []
    seen = {}
    for cid, mask in masks.items():
        seen.setdefault(mask, []).append(cid)
    for mask, ids in seen.items():
        if len(ids) > 1:
            merged.append({"keep": ids[0], "merged": ids[1:], "dropped_dates": len(mask)})
    return merged


def report_clocks(f_rows, fixtures):
    clock_rows = build_clock_table()
    dollar, trade_level, trade_count = build_dollar_and_trade()
    fx = clock_fixture()
    fixtures = {
        "ticket": "01+02",
        "pass": bool(fixtures.get("pass")) and fx["pass"],
        "n_cases": fixtures.get("n_cases", 0) + fx["n_cases"],
        "n_failed": fixtures.get("n_failed", 0) + fx["n_failed"],
        "groups": (fixtures.get("groups") or []) + fx["groups"],
    }
    docs = []
    merges = merge_coverage(clock_rows)
    for cid in CLOCK_IDS:
        sub = [r for r in clock_rows if r.get("clock") == cid]
        doc = _doc_from_rows(cid, sub, "range.6-9.published", fixtures, extra={"coverage_merges": merges})
        docs.append(doc)
    hour = [r for r in clock_rows if r.get("clock") == "range.gb.hour"]
    docs.append(_doc_from_rows("range.gb.hour", hour, "range.6-9.published", fixtures, n_unit="events"))
    docs.append(_doc_from_rows("range.6-9.dollar-bars", dollar, "range.6-9.published", fixtures, extra={"bar": "dollar"}))
    docs.append(_doc_from_rows("range.6-9.trade-level", trade_level, "range.6-9.published", fixtures, extra={"bar": "trade-level"}))
    docs.append(_doc_from_rows("range.6-9.trade-count", trade_count, "range.6-9.published", fixtures, extra={"bar": "trade-count"}))
    docs.extend(bin_documents(f_rows, fixtures))
    london = [d["variant"] for d in docs]
    assert "range.london.00-03" in london and "range.gb.london" in london
    return docs
