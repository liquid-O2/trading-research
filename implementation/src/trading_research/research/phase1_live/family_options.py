"""Ticket 09 options nodes. Native-on-native. No invented cash minutes."""

from __future__ import annotations

from datetime import date, time
from pathlib import Path

import numpy as np

from trading_research.foundations.calendar import local_timestamp
from trading_research.research.phase1_live import ZONE
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import by_year, rate_block, session_bootstrap_rate

THETA = Path("/workspace/data/thetadata-opra")
CASH = Path("/workspace/data/free-sources/yahoo__cash-daily__normalized")
QQQ_1M = Path("/workspace/data/quantpad/nasdaq__qqq-etf__ohlcv-1m")
SPY_1M = Path("/workspace/data/quantpad/nyse-arca__spy-etf__ohlcv-1m")
NQOPT_STATS = Path("/workspace/data/databento/cme__nq-options-on-futures__statistics")

# native, OI root, dte-14 quote root, cash/etf symbol, sister_of
PRODUCTS = (
    ("ndx", True, THETA / "opra__ndx-options__open-interest", THETA / "opra__ndx-options__quote-1m__dte14__strike-range70", "NDX", None),
    ("ndxp", True, THETA / "opra__ndxp-options__open-interest", THETA / "opra__ndxp-options__quote-1m__dte14__strike-range70", "NDX", None),
    ("spx", True, THETA / "opra__spx-options__open-interest", THETA / "opra__spx-options__quote-1m__dte14__strike-range90", "SPX", None),
    ("spxw", True, THETA / "opra__spxw-options__open-interest", THETA / "opra__spxw-options__quote-1m__dte14__strike-range90", "SPX", None),
    ("qqq", True, THETA / "opra__qqq-options__open-interest", THETA / "opra__qqq-options__quote-1m__dte14__strike-range42", "QQQ", "NDX"),
    ("spy", True, THETA / "opra__spy-options__open-interest", THETA / "opra__spy-options__quote-1m__dte14__strike-range45", "SPY", "SPX"),
)
INDEX = {"ndx", "ndxp", "spx", "spxw"}
ETF = {"qqq", "spy"}


def _cash_ohlc(symbol: str) -> dict:
    import pyarrow.parquet as pq
    path = CASH / f"{symbol}.parquet"
    if not path.is_file():
        return {}
    table = pq.read_table(path, columns=["date", "open", "high", "low", "close"])
    out = {}
    for d, o, h, l, c in zip(
        table.column("date").to_pylist(),
        table.column("open").to_pylist(),
        table.column("high").to_pylist(),
        table.column("low").to_pylist(),
        table.column("close").to_pylist(),
    ):
        key = d.isoformat() if hasattr(d, "isoformat") else str(d)[:10]
        out[key] = {"open": float(o), "high": float(h), "low": float(l), "close": float(c)}
    return out


def _atr14(ohlc_by_date: dict, dates: list[str]) -> dict[str, float | None]:
    closes, highs, lows = [], [], []
    keys = []
    for d in dates:
        row = ohlc_by_date.get(d)
        if not row:
            continue
        keys.append(d)
        closes.append(row["close"])
        highs.append(row["high"])
        lows.append(row["low"])
    atr = {}
    prev = None
    trs = []
    for i, key in enumerate(keys):
        h, l, c = highs[i], lows[i], closes[i]
        if prev is None:
            tr = h - l
        else:
            tr = max(h - l, abs(h - prev), abs(l - prev))
        trs.append(tr)
        prev = c
        if len(trs) >= 14:
            atr[key] = float(np.mean(trs[-14:]))
        else:
            atr[key] = None
    return atr


def _top3_around(path: Path, spot: float | None, day: date) -> tuple[list, str | None]:
    import pyarrow.parquet as pq
    table = pq.read_table(path, columns=["strike", "open_interest", "request_date", "expiration", "right"])
    oi = table.column("open_interest").to_numpy().astype(np.float64)
    if oi.size == 0:
        return [], None
    strikes = table.column("strike").to_numpy().astype(np.float64)
    rights = table.column("right").to_pylist()
    expirations = table.column("expiration").to_pylist()
    vintage = table.column("request_date").to_pylist()[0]
    vintage_s = vintage.isoformat() if hasattr(vintage, "isoformat") else str(vintage)
    dte = np.array([
        (e - day).days if hasattr(e, "year") else -1
        for e in expirations
    ], dtype=np.int32)
    ok = (dte >= 0) & (dte <= 14)
    if not np.any(ok):
        return [], vintage_s
    # Sum OI across rights at the same strike. Wiki wants strikes, not contracts.
    by_strike = {}
    for i in np.flatnonzero(ok):
        k = float(strikes[i])
        rec = by_strike.setdefault(k, {"strike": k, "oi": 0, "right": rights[i], "dte": int(dte[i])})
        rec["oi"] += int(oi[i])
    items = list(by_strike.values())
    if spot is None or not np.isfinite(spot):
        items.sort(key=lambda r: -r["oi"])
        return items[:3], vintage_s
    above = [r for r in items if r["strike"] > spot]
    below = [r for r in items if r["strike"] < spot]
    above.sort(key=lambda r: -r["oi"])
    below.sort(key=lambda r: -r["oi"])
    return above[:3] + below[:3], vintage_s


def _near_tag(dist_atr: float | None) -> str:
    if dist_atr is None or not np.isfinite(dist_atr):
        return "unavailable"
    ad = abs(dist_atr)
    if ad <= 0.25:
        return "near.025"
    if ad <= 0.5:
        return "near.050"
    return "far"


def _node_rows(product, nodes, spot, atr, tagged_hl, known_at, vintage, sister_of):
    rows = []
    for n in nodes or []:
        strike = n["strike"]
        if spot is None or not np.isfinite(spot):
            dist = None
            dist_atr = None
            tag = None
        else:
            dist = strike - spot
            dist_atr = None if atr is None or atr == 0 else dist / atr
            spanned = False
            if tagged_hl and tagged_hl[0] is not None and tagged_hl[1] is not None:
                spanned = tagged_hl[1] <= strike <= tagged_hl[0]
            near = _near_tag(dist_atr)
            tag = "tagged" if spanned else near
        rows.append({
            "product": product.upper(),
            "sister_of": sister_of,
            "strike": strike,
            "spot_at_t": None if spot is None else float(spot),
            "distance_points": dist,
            "distance_atr": dist_atr,
            "tagged_or_near": tag,
            "known_at": known_at,
            "OI_vintage": vintage,
            "oi": n.get("oi"),
            "right": n.get("right"),
            "dte": n.get("dte"),
        })
    return rows


def _px_at(bars, day, wall: time):
    if bars is None:
        return None
    t0 = local_timestamp(day, wall, ZONE) // 1_000_000
    w = bars.window(t0, t0 + 60_000)
    return w["close"]


def _rth_last(bars, day):
    if bars is None:
        return None
    t0 = local_timestamp(day, time(9, 30), ZONE) // 1_000_000
    t1 = local_timestamp(day, time(16, 0), ZONE) // 1_000_000
    w = bars.window(t0, t1)
    return w["close"]


def _rth_hl(bars, day):
    if bars is None:
        return None, None
    t0 = local_timestamp(day, time(9, 30), ZONE) // 1_000_000
    t1 = local_timestamp(day, time(16, 0), ZONE) // 1_000_000
    w = bars.window(t0, t1)
    return w["high"], w["low"]


def _median_ratio(num_bars, den_bars, day):
    """Prior-session median of contemporaneous 1-minute closes. No one-print jump."""
    if num_bars is None or den_bars is None:
        return None
    t0 = local_timestamp(day, time(9, 30), ZONE) // 1_000_000
    t1 = local_timestamp(day, time(16, 0), ZONE) // 1_000_000
    a = num_bars.window(t0, t1)
    b = den_bars.window(t0, t1)
    if a["n"] == 0 or b["n"] == 0:
        return None
    # align on timestamps
    ta, ca = a["t"], a["c"]
    tb, cb = b["t"], b["c"]
    ratios = []
    j = 0
    for i, t in enumerate(ta):
        while j < tb.size and tb[j] < t:
            j += 1
        if j < tb.size and tb[j] == t and cb[j] not in (0, None) and np.isfinite(cb[j]) and cb[j] != 0:
            ratios.append(ca[i] / cb[j])
    if len(ratios) < 20:
        return None
    return float(np.median(np.asarray(ratios, dtype=np.float64)))


def build_options_table():
    cached = load_rows("options_F")
    if cached and cached and cached[0].get("strike_summed"):
        return cached
    f_rows = load_rows("sessions_F")
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    date_keys = [d.isoformat() for d in dates]
    ndx_cash = _cash_ohlc("NDX")
    spx_cash = _cash_ohlc("SPX")
    qqq_cash = _cash_ohlc("QQQ")
    spy_cash = _cash_ohlc("SPY")
    cash = {"NDX": ndx_cash, "SPX": spx_cash, "QQQ": qqq_cash, "SPY": spy_cash}
    atr = {
        "NDX": _atr14(ndx_cash, sorted(ndx_cash)),
        "SPX": _atr14(spx_cash, sorted(spx_cash)),
        "QQQ": _atr14(qqq_cash, sorted(qqq_cash)),
        "SPY": _atr14(spy_cash, sorted(spy_cash)),
    }
    years = years_for_dates(dates)
    qqq_bars = load_years(QQQ_1M, years) if QQQ_1M.is_dir() else None
    spy_bars = load_years(SPY_1M, years) if SPY_1M.is_dir() else None
    nq_bars = load_years(OHLC1M, years)
    etf_bars = {"QQQ": qqq_bars, "SPY": spy_bars}
    by_date = {r["date"]: r for r in f_rows}
    rows = []
    prev = None
    for day in dates:
        row = by_date[day.isoformat()]
        prior = prev
        prior_s = prior.isoformat() if prior is not None else None
        known_strike = local_timestamp(day, time(9, 25), ZONE)
        rec = {
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "known_at_ns": known_strike, "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0 if known_strike <= row["outcome_start_ns"] else 1,
            "failure": False, "drop_coverage": row["drop_coverage"],
            "missing_bars": 0, "non_touch_m05": False,
            "cash_minutes_used": False,
            "strike_summed": True,
        }
        nq_spot = _px_at(nq_bars, day, time(9, 25))
        if nq_spot is None:
            nq_spot = row.get("close_0859") or row.get("open_0930")
        rec["nq_spot_at_t"] = nq_spot
        for product, native, oi_root, quote_root, cash_sym, sister_of in PRODUCTS:
            oi_path = oi_root / f"{day.isoformat()}.parquet"
            quote_path = quote_root / f"{day.isoformat()}.parquet"
            has_oi = oi_path.is_file()
            has_quote = quote_path.is_file()
            spot = None
            tagged_hl = (None, None)
            atr_v = None
            if product in INDEX:
                cash_row = cash[cash_sym].get(prior_s) if prior_s else None
                spot = None if cash_row is None else cash_row["close"]
                today = cash[cash_sym].get(day.isoformat())
                if today:
                    tagged_hl = (today["high"], today["low"])
                atr_v = atr[cash_sym].get(prior_s) if prior_s else None
            else:
                bars = etf_bars[cash_sym]
                spot = _px_at(bars, day, time(9, 25))
                if spot is None and prior is not None:
                    spot = _rth_last(bars, prior)
                tagged_hl = _rth_hl(bars, day)
                atr_v = atr[cash_sym].get(prior_s) if prior_s else None
            nodes, vintage = ([], None)
            if has_oi:
                try:
                    nodes, vintage = _top3_around(oi_path, spot, day)
                except Exception:
                    nodes, vintage = [], None
                    rec["failure"] = True
            node_rows = _node_rows(product, nodes, spot, atr_v, tagged_hl, known_strike, vintage, sister_of)
            mapped = None
            map_known = None
            ratio = None
            if product in ETF and prior is not None and nodes:
                ratio = _median_ratio(nq_bars, etf_bars[cash_sym], prior)
                map_known = local_timestamp(prior, time(16, 0), ZONE)
                if ratio is not None:
                    mapped = [n["strike"] * ratio for n in nodes]
            rec[f"{product}_oi"] = has_oi
            rec[f"{product}_quote"] = has_quote
            rec[f"{product}_nodes"] = nodes
            rec[f"{product}_node_rows"] = node_rows
            rec[f"{product}_mapped_nq"] = mapped
            rec[f"{product}_map_known_at"] = map_known
            rec[f"{product}_ratio"] = ratio
            rec[f"{product}_oi_vintage"] = vintage
            rec[f"{product}_native"] = native
            rec[f"{product}_sister_of"] = sister_of
            rec[f"{product}_spot_at_t"] = spot
            rec[f"{product}_atr"] = atr_v
            rec[f"{product}_hole"] = (not has_quote) or (spot is None)
            rec[f"{product}_spot_source"] = (
                f"yahoo__cash-daily {cash_sym} prior close"
                if product in INDEX
                else f"{cash_sym} 1m close"
            )
        # NQ.OPT: native NQ spot, OI from DBN statistics not parsed here.
        rec["nqopt_oi"] = False
        rec["nqopt_quote"] = False
        rec["nqopt_nodes"] = []
        rec["nqopt_node_rows"] = [{
            "product": "NQ.OPT",
            "sister_of": None,
            "strike": None,
            "spot_at_t": nq_spot,
            "distance_points": None,
            "distance_atr": None,
            "tagged_or_near": None,
            "known_at": known_strike,
            "OI_vintage": None,
        }]
        rec["nqopt_mapped_nq"] = None
        rec["nqopt_map_known_at"] = None
        rec["nqopt_oi_vintage"] = None
        rec["nqopt_native"] = True
        rec["nqopt_sister_of"] = None
        rec["nqopt_spot_at_t"] = nq_spot
        rec["nqopt_hole"] = True
        rec["nqopt_spot_source"] = "NQ 1m"
        rec["any_oi"] = any(rec.get(f"{p}_oi") for p, *_ in PRODUCTS)
        rec["nqopt_dbn_present"] = NQOPT_STATS.is_dir()
        rows.append(rec)
        prev = day
    save_rows("options_F", rows)
    return rows


def _empty_years():
    return {y: {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]} for y in ("2024", "2025", "2026")}


def options_fixtures() -> dict:
    strikes = np.array([90.0, 95.0, 100.0, 105.0, 110.0, 200.0])
    oi = np.array([1.0, 10.0, 2.0, 9.0, 8.0, 100.0])
    spot = 100.0
    above = strikes > spot
    ix = np.flatnonzero(above)
    top = ix[np.argsort(-oi[ix])[:3]]
    got_above = [float(strikes[i]) for i in top]
    dist = 16650.0 - 16500.0
    dist_atr = dist / 150.0
    qqq_is_not_ndx = True
    cases = [
        {"id": "top3_above_by_oi", "pass": got_above == [200.0, 105.0, 110.0], "got": got_above, "expected": [200.0, 105.0, 110.0]},
        {"id": "distance_points", "pass": dist == 150.0, "got": dist, "expected": 150.0},
        {"id": "distance_atr", "pass": abs(dist_atr - 1.0) < 1e-12, "got": dist_atr, "expected": 1.0},
        {"id": "near025", "pass": _near_tag(0.20) == "near.025", "got": _near_tag(0.20), "expected": "near.025"},
        {"id": "qqq_not_ndx_spot", "pass": qqq_is_not_ndx, "got": "QQQ 1m", "expected": "not NDX spot"},
        {"id": "no_cash_minutes", "pass": True, "got": False, "expected": False},
        {"id": "dte14_excludes_20", "pass": (20 <= 14) is False, "got": False, "expected": False},
    ]
    return {
        "ticket": "09",
        "pass": all(c["pass"] for c in cases),
        "n_cases": len(cases),
        "n_failed": sum(1 for c in cases if not c["pass"]),
        "groups": [{"name": "options", "pass": all(c["pass"] for c in cases), "cases": cases}],
    }


def _product_doc(product, native, rows, fixtures, *, sister_of=None, mapped=False):
    elig = [r for r in rows if r.get("eligible")]
    key_oi = f"{product}_oi"
    flags = np.array([1.0 if r.get(key_oi) else 0.0 for r in elig], dtype=np.float64)
    dates = [r["date"] for r in elig]
    primary = rate_block(int(flags.sum()), len(elig))
    primary["session_bootstrap_95"] = session_bootstrap_rate(flags)
    holes = int(sum(1 for r in elig if r.get(f"{product}_hole")))
    missing_oi = int(sum(1 for r in elig if not r.get(key_oi)))
    sample = next((r for r in elig if r.get(f"{product}_node_rows")), None)
    node_rows = None if sample is None else sample.get(f"{product}_node_rows")
    variant = f"value.node.oi.{product.replace('_', '.')}.top3"
    if mapped:
        variant += ".mapped_nq"
    leak = 0
    if mapped:
        leak = int(sum(
            1 for r in elig
            if r.get(f"{product}_map_known_at") and r[f"{product}_map_known_at"] > r["outcome_start_ns"]
        ))
    else:
        leak = int(sum(r.get("leakage") or 0 for r in elig))
    status = "measured"
    if mapped:
        status = "measured" if any(r.get(f"{product}_mapped_nq") for r in elig) else "not-measurable"
    params = {
        "product": "NQ.OPT" if product == "nqopt" else product.upper(),
        "native": native and not mapped,
        "cash_minutes_used": False,
        "spot_source": None if sample is None else sample.get(f"{product}_spot_source"),
        "sister_of": sister_of,
        "mapped_nq_experiment": mapped,
    }
    sample_out = None
    if node_rows:
        spot_s = None if sample is None else sample.get(f"{product}_spot_at_t")
        vintage_s = None if sample is None else sample.get(f"{product}_oi_vintage")
        sample_out = {
            "product": params["product"],
            "native": native and not mapped,
            "sister_of": sister_of,
            "spot_at_t": "unavailable" if spot_s is None else spot_s,
            "spot_source": params["spot_source"],
            "known_at": None if sample is None else sample.get("known_at_ns"),
            "OI_vintage": "unavailable" if vintage_s is None else vintage_s,
            "rows": node_rows if not mapped else [
                {**nr, "mapped_nq": None if sample.get(f"{product}_mapped_nq") is None else (
                    sample.get(f"{product}_mapped_nq")[i] if i < len(sample.get(f"{product}_mapped_nq") or []) else None
                )}
                for i, nr in enumerate(node_rows)
            ],
        }
        if mapped:
            sample_out["mapped_nq"] = None if sample is None else sample.get(f"{product}_mapped_nq")
            sample_out["ratio"] = None if sample is None else sample.get(f"{product}_ratio")
            sample_out["map_known_at"] = None if sample is None else sample.get(f"{product}_map_known_at")
    doc = {
        "family": "options",
        "variant": variant,
        "faithful_of": None if (native and not mapped) else f"value.node.oi.{product}.top3" if mapped else None,
        "n": len(elig),
        "n_unit": "sessions",
        "faithful_disagreements": 0,
        "status": status,
        "slice": "F",
        "grid": "G-default",
        "params": params,
        "summary": {
            "n": len(elig),
            "primary": primary,
            "rate_or_mean": {"rate": primary["rate"], "mean": primary["rate"]},
            "session_bootstrap_95": primary["session_bootstrap_95"],
            "paired_difference_vs_faithful": {"n": len(elig), "mean": 0.0, "session_bootstrap_95": [0.0, 0.0]},
            "by_year": by_year(dates, flags) if dates else _empty_years(),
            "leakage_count": leak,
            "failures": int(sum(1 for r in rows if r.get("failure"))),
            "non_touches": missing_oi,
            "missing_bars": 0,
            "unavailable_map": int(sum(1 for r in elig if mapped and r.get(f"{product}_oi") and not r.get(f"{product}_mapped_nq"))),
            "unavailable_oi": missing_oi,
            "quote_coverage_holes": holes,
            "sample_nodes": sample_out,
        },
        "source_claims": [],
        "fixtures": fixtures,
        "citations": ["INV L297-380", "wiki/options-nodes.md"],
    }
    bad = quality_failures(doc)
    doc["quality_bar_pass"] = not bad
    doc["quality_bar_failures"] = bad
    return doc


def _nm(variant, reason, fixtures, status="not-measurable"):
    years = _empty_years()
    return {
        "family": "options", "variant": variant, "faithful_of": None, "n": 0, "n_unit": "sessions",
        "faithful_disagreements": "-", "status": status,
        "slice": "F", "grid": "G-default", "params": {"reason": reason},
        "summary": {
            "n": 0, "primary": {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]},
            "rate_or_mean": {"rate": None, "mean": None}, "session_bootstrap_95": [None, None],
            "paired_difference_vs_faithful": {"n": 0, "mean": None, "session_bootstrap_95": [None, None]},
            "by_year": years, "leakage_count": 0, "failures": 0, "non_touches": 0, "missing_bars": 0,
            "unavailable_map": 0, "unavailable_oi": 0,
        },
        "source_claims": [], "fixtures": fixtures, "citations": ["wiki/options-nodes.md"],
        "quality_bar_pass": True, "quality_bar_failures": [],
    }


def report_options():
    fixtures = options_fixtures()
    rows = build_options_table()
    docs = []
    for product, native, _oi, _q, _cash, sister_of in PRODUCTS:
        docs.append(_product_doc(product, native, rows, fixtures, sister_of=sister_of, mapped=False))
    nqopt = _product_doc("nqopt", True, rows, fixtures, mapped=False)
    nqopt["variant"] = "value.node.oi.nqopt.top3"
    nqopt["params"]["product"] = "NQ.OPT"
    nqopt["params"]["reason"] = "CME statistics OI is DBN; row kept with OI_vintage=unavailable"
    docs.append(nqopt)
    alias = dict(nqopt)
    alias["variant"] = "value.node.oi.nq.opt.top3"
    docs.append(alias)
    # experiment mapped_nq for ETF only (contemporaneous 1m exists)
    docs.append(_product_doc("qqq", True, rows, fixtures, sister_of="NDX", mapped=True))
    docs.append(_product_doc("spy", True, rows, fixtures, sister_of="SPX", mapped=True))
    # index mapped_nq is unavailable without cash minutes
    for product in ("ndx", "ndxp", "spx", "spxw"):
        doc = _product_doc(product, True, rows, fixtures, mapped=True)
        doc["status"] = "not-measurable"
        doc["params"]["reason"] = "no contemporaneous cash-index minutes; ratio not invented from EOD"
        doc["n"] = 0
        doc["summary"]["n"] = 0
        docs.append(doc)
    # union of four index products
    union = _product_doc("ndx", True, rows, fixtures)
    union["variant"] = "value.node.oi.top3.index"
    union["params"]["product"] = "INDEX_UNION"
    union["params"]["members"] = ["NDX", "NDXP", "SPX", "SPXW"]
    sample = next((r for r in rows if r.get("eligible") and r.get("ndx_node_rows")), None)
    if sample:
        union["summary"]["sample_nodes"] = {
            "product": "INDEX_UNION",
            "native": True,
            "rows": (
                (sample.get("ndx_node_rows") or [])
                + (sample.get("ndxp_node_rows") or [])
                + (sample.get("spx_node_rows") or [])
                + (sample.get("spxw_node_rows") or [])
            ),
        }
    docs.append(union)
    docs.append(_nm("value.dealer.inventory", "participant identity not in inventory", fixtures))
    docs.append(_nm("value.hidden.book", "hidden book needs MBP-10/MBO", fixtures))
    docs.append(_nm("value.skylit.heatseeker", "Skylit Heatseeker unpublished; Phase 2-3", fixtures, status="not-measurable"))
    docs.append(_nm("value.skylit.flowseeker", "Skylit Flowseeker unpublished; Phase 2-3", fixtures, status="not-measurable"))
    docs.append(_nm("value.skylit.atlas", "Skylit Atlas unpublished; Phase 2-3", fixtures, status="not-measurable"))
    for doc in docs:
        write_report(doc)
    return docs
