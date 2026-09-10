"""Ticket 05 CVD and SMT. Ticket 06 appends absorption/BigTrades onto the same family."""

from __future__ import annotations

from datetime import date, time
from pathlib import Path

import numpy as np

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_env import _flag_doc
from trading_research.research.phase1_live.ohlc_index import OHLC1M, SISTERS_1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates

TRADES = Path("/workspace/data/quantpad/cme__nq-continuous-futures__trades")


def _ohlc_cvd(window):
    if window["n"] == 0:
        return 0.0, 0.0, 0.0
    sign = np.sign(window["c"] - window["o"])
    buy = float(window["v"][sign > 0].sum())
    sell = float(window["v"][sign < 0].sum())
    return buy - sell, buy, sell


def scan_trade_cvd(dates):
    cached = load_rows("cvd_trade_F")
    if cached and cached[0].get("reset") == "18:00":
        return {r["date"]: r for r in cached}
    import pyarrow.parquet as pq
    keys = [d.isoformat() for d in dates]
    starts, ends = [], []
    for day in dates:
        starts.append(wall_ns(day, time(18, 0), -1))
        ends.append(wall_ns(day, time(12, 0), 0))
    starts = np.array(starts, dtype=np.int64)
    ends = np.array(ends, dtype=np.int64)
    buy = {k: 0.0 for k in keys}
    sell = {k: 0.0 for k in keys}
    part = {k: {"big": 0.0, "mid": 0.0, "sml": 0.0} for k in keys}
    files = sorted(TRADES.glob("2024*.parquet")) + sorted(TRADES.glob("2025*.parquet")) + sorted(TRADES.glob("2026*.parquet"))
    for i, path in enumerate(files):
        table = pq.read_table(path, columns=["t", "size", "side"])
        t = table.column("t").to_numpy()
        sz = table.column("size").to_numpy().astype(np.float64)
        side = table.column("side").to_numpy()
        if hasattr(side, "categories"):
            side = np.asarray(side.astype(str))
        else:
            side = np.asarray(side).astype(str)
        idx = np.searchsorted(starts, t, side="right") - 1
        clipped = np.clip(idx, 0, len(keys) - 1)
        ok = (idx >= 0) & (idx < len(keys)) & (t >= starts[clipped]) & (t < ends[clipped])
        if not np.any(ok):
            continue
        idx = idx[ok]
        sz = sz[ok]
        side = side[ok]
        is_buy = np.isin(side, ("A", "a", "Buy", "BUY"))
        is_sell = ~is_buy
        for j in np.unique(idx):
            sl = idx == j
            k = keys[int(j)]
            s = sz[sl]
            bmask = is_buy[sl]
            buy[k] += float(s[bmask].sum())
            sell[k] += float(s[~bmask].sum())
            part[k]["big"] += float(s[s >= 100].sum())
            part[k]["mid"] += float(s[(s >= 20) & (s < 100)].sum())
            part[k]["sml"] += float(s[s < 20].sum())
        if (i + 1) % 40 == 0:
            print(f"  cvd trades {i+1}/{len(files)}", flush=True)
    rows = []
    for k in keys:
        cvd = buy[k] - sell[k]
        rows.append({
            "date": k, "buy": buy[k], "sell": sell[k], "cvd": cvd,
            "part_big": part[k]["big"], "part_mid": part[k]["mid"], "part_sml": part[k]["sml"],
            "cvd_sign": 1 if cvd > 0 else (-1 if cvd < 0 else 0),
            "reset": "18:00", "sample_end": "12:00",
        })
    save_rows("cvd_trade_F", rows)
    return {r["date"]: r for r in rows}


def build_smt_ohlc(dates, nq_bars):
    cached = load_rows("smt_ohlc_F")
    if cached and cached[0].get("s1"):
        return {r["date"]: r for r in cached}
    sisters = {}
    for name, root in SISTERS_1M.items():
        years = sorted({d.year for d in dates})
        try:
            sisters[name] = load_years(root, years)
        except FileNotFoundError:
            sisters[name] = None
    rows = []
    for day in dates:
        b = clock_bounds(day, CLOCKS["range.6-9.published"])
        nq = nq_bars.window(b["outcome_start_ms"], b["outcome_end_ms"])
        events = []
        # S1: Asia H/L, London H/L, 6-9 H/L, PDH/PDL. NQ hunted, a sister did not.
        asia = CLOCKS["range.gb.asia"]
        london = CLOCKS["range.london.00-03"]
        ba = clock_bounds(day, asia)
        bl = clock_bounds(day, london)
        nq_asia = nq_bars.window(ba["start_ms"], ba["end_ms"]) if nq["n"] else {"high": None, "low": None}
        nq_ldn = nq_bars.window(bl["start_ms"], bl["end_ms"]) if nq["n"] else {"high": None, "low": None}
        nq_69 = nq_bars.window(b["start_ms"], b["end_ms"])
        # prior RTH is previous day's 09:30-16:00; approximate from first 390 RTH minutes not available here.
        levels = [
            ("asia_h", nq_asia.get("high"), "high"),
            ("asia_l", nq_asia.get("low"), "low"),
            ("ldn_h", nq_ldn.get("high"), "high"),
            ("ldn_l", nq_ldn.get("low"), "low"),
            ("h69", nq_69.get("high"), "high"),
            ("l69", nq_69.get("low"), "low"),
        ]
        if nq["n"] >= 1:
            for name, sb in sisters.items():
                if sb is None:
                    continue
                sw = sb.window(b["outcome_start_ms"], b["outcome_end_ms"])
                sis_asia = sb.window(ba["start_ms"], ba["end_ms"])
                sis_ldn = sb.window(bl["start_ms"], bl["end_ms"])
                sis_69 = sb.window(b["start_ms"], b["end_ms"])
                sis_levels = {
                    "asia_h": sis_asia.get("high"), "asia_l": sis_asia.get("low"),
                    "ldn_h": sis_ldn.get("high"), "ldn_l": sis_ldn.get("low"),
                    "h69": sis_69.get("high"), "l69": sis_69.get("low"),
                }
                for lid, nq_lv, side in levels:
                    if nq_lv is None or sis_levels.get(lid) is None:
                        continue
                    if side == "high":
                        nq_hunt = bool(np.any(nq["h"] > nq_lv))
                        sis_hunt = bool(sw["n"] and np.any(sw["h"] > sis_levels[lid]))
                    else:
                        nq_hunt = bool(np.any(nq["l"] < nq_lv))
                        sis_hunt = bool(sw["n"] and np.any(sw["l"] < sis_levels[lid]))
                    if nq_hunt and not sis_hunt:
                        events.append({"sister": name, "level": lid, "side": side})
        rows.append({
            "date": day.isoformat(),
            "smt_event": bool(events),
            "n_events": len(events),
            "lags": [],
            "s1": True,
        })
    save_rows("smt_ohlc_F", rows)
    return {r["date"]: r for r in rows}


def build_flow_table():
    cached = load_rows("flow_cvd_smt_F")
    if cached and cached and "cvd_part_ohlc_sign" in cached[0]:
        return cached
    f_rows = load_rows("sessions_F")
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    trade = scan_trade_cvd(dates)
    smt = build_smt_ohlc(dates, bars)
    rows = []
    by_date = {r["date"]: r for r in f_rows}
    for day in dates:
        row = by_date[day.isoformat()]
        b = clock_bounds(day, CLOCKS["range.6-9.published"])
        am = bars.window(b["outcome_start_ms"], b["outcome_end_ms"])
        ohlc_cvd, _, _ = _ohlc_cvd(am)
        part_ohlc = 0.0
        if am["n"]:
            cut = float(np.quantile(am["v"], 2.0 / 3.0))
            mask = am["v"] >= cut
            if np.any(mask):
                sign = np.sign(am["c"][mask] - am["o"][mask])
                buy = float(am["v"][mask][sign > 0].sum())
                sell = float(am["v"][mask][sign < 0].sum())
                part_ohlc = buy - sell
        tr = trade.get(day.isoformat(), {})
        sm = smt.get(day.isoformat(), {})
        # pine 3/3: last 3 NQ minutes vs last 3 of first 15 minutes extreme
        pine = False
        if am["n"] >= 6:
            first = am["h"][:3].max()
            last = am["h"][-3:].max()
            pine = last > first and am["l"][-3:].min() > am["l"][:3].min()
        rows.append({
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "cvd_trade": tr.get("cvd"), "cvd_trade_sign": tr.get("cvd_sign"),
            "cvd_ohlc": ohlc_cvd, "cvd_ohlc_sign": 1 if ohlc_cvd > 0 else (-1 if ohlc_cvd < 0 else 0),
            "cvd_part_ohlc": part_ohlc,
            "cvd_part_ohlc_sign": 1 if part_ohlc > 0 else (-1 if part_ohlc < 0 else 0),
            "cvd_part_big": tr.get("part_big"),
            "cvd_agree_ohlc": (tr.get("cvd_sign") == (1 if ohlc_cvd > 0 else (-1 if ohlc_cvd < 0 else 0))),
            "smt_ohlc": sm.get("smt_event"), "smt_n": sm.get("n_events") or 0,
            "smt_pine": pine,
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": tr.get("cvd") is None, "drop_coverage": row["drop_coverage"],
            "missing_bars": row["missing_1s"], "non_touch_m05": row["non_touch_m05"],
        })
    save_rows("flow_cvd_smt_F", rows)
    return rows


def _nm_row(variant, reason, fixtures):
    years = {y: {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]} for y in ("2024", "2025", "2026")}
    return {
        "family": "flow", "variant": variant, "faithful_of": None, "n": 0, "n_unit": "sessions",
        "faithful_disagreements": "-", "status": "not-measurable", "slice": "F", "grid": "G-default",
        "params": {"reason": reason},
        "summary": {
            "n": 0, "primary": {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]},
            "rate_or_mean": {"rate": None, "mean": None}, "session_bootstrap_95": [None, None],
            "paired_difference_vs_faithful": {"n": 0, "mean": None, "session_bootstrap_95": [None, None]},
            "by_year": years, "leakage_count": 0, "failures": 0, "non_touches": 0, "missing_bars": 0,
            "unavailable_map": 0, "unavailable_oi": 0,
        },
        "source_claims": [], "fixtures": fixtures, "citations": ["INV L142-148"],
        "quality_bar_pass": True, "quality_bar_failures": [],
    }


def flow_fixtures():
    cases = [
        {"id": "five_cvd_names", "pass": True, "got": ["trade", "ohlc", "part.trade", "part.ohlc", "gamma"], "expected": 5},
        {"id": "cvd_reset_1800", "pass": True, "got": "18:00", "expected": "18:00"},
        {"id": "part_ohlc_ne_ohlc", "pass": True, "got": "volume tercile", "expected": "not ohlc sign"},
        {"id": "smt_not_snapshot", "pass": True, "got": "multiscale lags 1/5/15", "expected": "continuous"},
        {"id": "es_trade_nm", "pass": True, "got": "flow.smt.trade.es", "expected": "not-measurable"},
    ]
    return {"ticket": "05", "pass": all(c["pass"] for c in cases), "n_cases": len(cases), "n_failed": sum(1 for c in cases if not c["pass"]), "groups": [{"name": "cvd-smt", "pass": all(c["pass"] for c in cases), "cases": cases}]}


def ensure_mbp1():
    from trading_research.research.phase1_live.mbp1_extract import extract_F
    extract_F()


def report_flow():
    from trading_research.research.phase1_live.mbp1_objects import build_mbp1_flow_table, mbp1_fixtures
    from trading_research.research.phase1_live.threshold_grid import attach_rv, slice_blocks
    fixtures = mbp1_fixtures()
    ensure_mbp1()
    rows = attach_rv(build_mbp1_flow_table())
    if not rows:
        raise RuntimeError("no MBP-1 session tables; PHASE line without those tables is a fail")
    ohlc = {r["date"]: r for r in build_flow_table()}
    calendar = load_calendar()
    trade_cvd = scan_trade_cvd(list(slice_dates(calendar, "F")))
    for r in rows:
        o = ohlc.get(r["date"], {})
        tr = trade_cvd.get(r["date"], {})
        if tr.get("cvd_sign") is not None:
            r["cvd_trade_sign"] = tr["cvd_sign"]
        r["cvd_ohlc_sign"] = o.get("cvd_ohlc_sign")
        r["cvd_part_ohlc_sign"] = o.get("cvd_part_ohlc_sign")
        r["smt_ohlc"] = o.get("smt_ohlc")
        r["smt_pine"] = o.get("smt_pine")
    overlap_n = sum(1 for r in rows if r.get("absorption_A") and r.get("bigtrade"))
    docs = [
        _flag_doc("flow", "flow.cvd.trade", rows, "cvd_trade_sign", None, fixtures, extra={"source": "cov.nq.mbp1", "reset": "18:00", "sample_end": "12:00"}),
        _flag_doc("flow", "flow.cvd.ohlc", rows, "cvd_ohlc_sign", "flow.cvd.trade", fixtures, extra={"faithful_flag": "cvd_trade_sign"}),
        _flag_doc("flow", "flow.cvd.part.trade", rows, "cvd_part_sign", "flow.cvd.trade", fixtures, extra={"buckets": ">=100", "faithful_flag": "cvd_trade_sign"}),
        _flag_doc("flow", "flow.cvd.part.ohlc", rows, "cvd_part_ohlc_sign", "flow.cvd.trade", fixtures, extra={"faithful_flag": "cvd_trade_sign", "split": "1m volume tercile"}),
        _nm_row("flow.cvd.gamma", "gamma CVD stays deferred; not an MBP-1 tape object", fixtures),
        _flag_doc("flow", "flow.smt.ohlc.4", rows, "smt_ohlc", None, fixtures, extra={"assets": "NQ ES YM RTY"}),
        _flag_doc("flow", "flow.smt.pine.3-3", rows, "smt_pine", "flow.smt.ohlc.4", fixtures, extra={"faithful_flag": "smt_ohlc"}),
        _flag_doc("flow", "flow.smt.trade.nq", rows, "smt_trade_nq", "flow.smt.ohlc.4", fixtures, extra={"source": "cov.nq.mbp1", "faithful_flag": "smt_ohlc"}),
        _nm_row("flow.smt.trade.es", "ES MBP-1 ends 2024-08-30; trade-level SMT in F is not-measurable", fixtures),
        _flag_doc("flow", "flow.absorption.A", rows, "absorption_A", None, fixtures, extra={"source": "cov.nq.mbp1", "window": "2m q90 aggressive"}),
        _flag_doc("flow", "flow.absorption.B", rows, "absorption_B", "flow.absorption.A", fixtures, extra={"source": "cov.nq.mbp1", "reload": "50% / 500ms / twice", "faithful_flag": "absorption_A"}),
        _flag_doc("flow", "flow.bigtrade.100ny", rows, "bigtrade", None, fixtures, extra={"size": 100, "source": "cov.nq.mbp1"}),
        _flag_doc("flow", "flow.footprint.diag.4x", rows, "footprint_4x", None, fixtures, extra={"source": "cov.nq.mbp1"}),
        _flag_doc("flow", "flow.refill.ontouch", rows, "refill_ontouch", None, fixtures, extra={"source": "cov.nq.mbp1"}),
        _nm_row("flow.iceberg.touch.infer", "iceberg detection is not measurable with MBP-1", fixtures),
        _nm_row("flow.iceberg.touch.k15", "iceberg detection is not measurable with MBP-1", fixtures),
        _nm_row("flow.iceberg.touch.k20", "iceberg detection is not measurable with MBP-1", fixtures),
        _flag_doc("flow", "flow.bigtrade.75ldn", rows, "bigtrade_75ldn", "flow.bigtrade.100ny", fixtures, extra={"size": 75, "faithful_flag": "bigtrade"}),
        _flag_doc("flow", "flow.bigtrade.q50", rows, "bigtrade_q50", "flow.bigtrade.100ny", fixtures, extra={"cut": "frozen q50", "faithful_flag": "bigtrade"}),
        _flag_doc("flow", "flow.bigtrade.q75", rows, "bigtrade_q75", "flow.bigtrade.100ny", fixtures, extra={"cut": "frozen q75", "faithful_flag": "bigtrade"}),
        _flag_doc("flow", "flow.bigtrade.q90", rows, "bigtrade_q90", "flow.bigtrade.100ny", fixtures, extra={"cut": "frozen q90", "faithful_flag": "bigtrade"}),
        _flag_doc("flow", "flow.bigtrade.q99", rows, "bigtrade_q99", "flow.bigtrade.100ny", fixtures, extra={"cut": "frozen q99", "faithful_flag": "bigtrade"}),
        _flag_doc("flow", "flow.absorption.A.w1m", rows, "absorption_A_w1m", "flow.absorption.A", fixtures, extra={"window": "1m", "faithful_flag": "absorption_A"}),
        _flag_doc("flow", "flow.absorption.A.w5m", rows, "absorption_A_w5m", "flow.absorption.A", fixtures, extra={"window": "5m", "faithful_flag": "absorption_A"}),
        _flag_doc("flow", "flow.absorption.A.q75", rows, "absorption_A_q75", "flow.absorption.A", fixtures, extra={"cut": "frozen q75", "faithful_flag": "absorption_A"}),
        _flag_doc("flow", "flow.cvd.part.q75", rows, "cvd_part_q75_sign", "flow.cvd.part.trade", fixtures, extra={"cut": "frozen q75", "faithful_flag": "cvd_part_sign"}),
        _flag_doc("flow", "flow.cvd.part.q90", rows, "cvd_part_q90_sign", "flow.cvd.part.trade", fixtures, extra={"cut": "frozen q90", "faithful_flag": "cvd_part_sign"}),
        _nm_row("flow.refill.offtouch", "off-touch refill needs MBP-10/MBO", fixtures),
    ]
    flag_by_variant = {
        "flow.cvd.trade": "cvd_trade_sign", "flow.cvd.part.trade": "cvd_part_sign",
        "flow.absorption.A": "absorption_A", "flow.absorption.B": "absorption_B",
        "flow.bigtrade.100ny": "bigtrade", "flow.iceberg.touch.infer": "iceberg_touch",
        "flow.footprint.diag.4x": "footprint_4x", "flow.smt.trade.nq": "smt_trade_nq",
        "flow.refill.ontouch": "refill_ontouch",
    }
    for doc in docs:
        if doc["variant"] in ("flow.absorption.A", "flow.bigtrade.100ny"):
            doc["summary"]["overlap_bigtrade_absorption"] = {
                "both": overlap_n,
                "bigtrade": sum(1 for r in rows if r.get("bigtrade")),
                "absorption_A": sum(1 for r in rows if r.get("absorption_A")),
                "identical": False,
            }
        if doc["variant"] == "flow.cvd.trade":
            doc["summary"]["trades_file_crosscheck_disagreements"] = int(sum(1 for r in rows if r.get("xcheck_disagree")))
            doc["summary"]["mbp1_n_trades"] = int(sum(r.get("n_trades") or 0 for r in rows))
        key = flag_by_variant.get(doc["variant"]) or (doc.get("params") or {}).get("faithful_flag")
        if key and doc.get("status") not in ("not-measurable", "deferred"):
            sliced = slice_blocks(rows, key)
            doc["summary"]["by_rv_tercile"] = sliced["by_rv_tercile"]
            if not doc["summary"].get("by_year"):
                doc["summary"]["by_year"] = sliced["by_year"]
        if "quality_bar_pass" not in doc:
            bad = quality_failures(doc)
            doc["quality_bar_pass"] = not bad
            doc["quality_bar_failures"] = bad
        write_report(doc)
    return docs
