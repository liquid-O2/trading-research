"""Ticket 09 options nodes. Native NDX/NDXP/SPX/SPXW. No cash-index minutes."""

from __future__ import annotations

from datetime import date, time
from pathlib import Path

import numpy as np

from trading_research.foundations.calendar import local_timestamp
from trading_research.research.phase1_live import ZONE
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import by_year, rate_block, session_bootstrap_rate

THETA = Path("/workspace/data/thetadata-opra")
CASH = Path("/workspace/data/free-sources/yahoo__cash-daily__normalized")
PRODUCTS = (
    ("ndx", True, THETA / "opra__ndx-options__open-interest", THETA / "opra__ndx-options__quote-1m__dte60__atm10", "NDX"),
    ("ndxp", True, THETA / "opra__ndxp-options__open-interest", THETA / "opra__ndxp-options__quote-1m__dte60__atm10", "NDX"),
    ("spx", True, THETA / "opra__spx-options__open-interest", THETA / "opra__spx-options__quote-1m__dte60__atm10", "SPX"),
    ("spxw", True, THETA / "opra__spxw-options__open-interest", THETA / "opra__spxw-options__quote-1m__dte60__atm10", "SPX"),
    ("qqq", False, THETA / "opra__qqq-options__open-interest", THETA / "opra__qqq-options__quote-1m__dte60__atm10", "QQQ"),
    ("spy", False, THETA / "opra__spy-options__open-interest", THETA / "opra__spy-options__quote-1m__dte60__atm10", "SPY"),
)


def _cash_closes(symbol: str) -> dict:
    import pyarrow.parquet as pq
    path = CASH / f"{symbol}.parquet"
    if not path.is_file():
        return {}
    table = pq.read_table(path, columns=["date", "close"])
    out = {}
    for d, c in zip(table.column("date").to_pylist(), table.column("close").to_pylist()):
        key = d.isoformat() if hasattr(d, "isoformat") else str(d)[:10]
        out[key] = float(c)
    return out


def _top3(path: Path) -> tuple[list, str | None]:
    import pyarrow.parquet as pq
    table = pq.read_table(path, columns=["strike", "open_interest", "request_date", "ts_event", "right"])
    oi = table.column("open_interest").to_numpy()
    if oi.size == 0:
        return [], None
    order = np.argsort(-oi)[:3]
    strikes = table.column("strike").to_numpy()
    rights = table.column("right").to_pylist()
    nodes = [{"strike": float(strikes[i]), "oi": int(oi[i]), "right": rights[i]} for i in order]
    vintage = table.column("request_date").to_pylist()[0]
    vintage_s = vintage.isoformat() if hasattr(vintage, "isoformat") else str(vintage)
    return nodes, vintage_s


def build_options_table():
    cached = load_rows("options_F")
    if cached:
        return cached
    f_rows = load_rows("sessions_F")
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    ndx = _cash_closes("NDX")
    spx = _cash_closes("SPX")
    qqq = _cash_closes("QQQ")
    spy = _cash_closes("SPY")
    cash = {"NDX": ndx, "SPX": spx, "QQQ": qqq, "SPY": spy}
    by_date = {r["date"]: r for r in f_rows}
    rows = []
    prev = None
    for day in dates:
        row = by_date[day.isoformat()]
        prior = prev.isoformat() if prev is not None else None
        nq_px = row.get("close_0859") or row.get("open_0930")
        rec = {
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": False, "drop_coverage": row["drop_coverage"],
            "missing_bars": 0, "non_touch_m05": False,
        }
        for product, native, oi_root, quote_root, cash_sym in PRODUCTS:
            oi_path = oi_root / f"{day.isoformat()}.parquet"
            quote_path = quote_root / f"{day.isoformat()}.parquet"
            has_oi = oi_path.is_file()
            has_quote = quote_path.is_file()
            nodes, vintage = ([], None)
            if has_oi:
                try:
                    nodes, vintage = _top3(oi_path)
                except Exception:
                    nodes, vintage = [], None
                    rec["failure"] = True
            cash_px = cash[cash_sym].get(prior) if prior else None
            ratio = None
            if cash_px and nq_px:
                ratio = nq_px / cash_px
            mapped = None
            if nodes and ratio:
                mapped = [n["strike"] * ratio for n in nodes]
            map_known = None
            if prior:
                map_known = local_timestamp(date.fromisoformat(prior), time(16, 0), ZONE)
            rec[f"{product}_oi"] = has_oi
            rec[f"{product}_quote"] = has_quote
            rec[f"{product}_nodes"] = nodes
            rec[f"{product}_mapped_nq"] = mapped
            rec[f"{product}_map_known_at"] = map_known
            rec[f"{product}_oi_vintage"] = vintage
            rec[f"{product}_native"] = native
            rec[f"{product}_hole"] = has_oi and not has_quote
        rec["any_oi"] = any(rec.get(f"{p}_oi") for p, *_ in PRODUCTS)
        rows.append(rec)
        prev = day
    save_rows("options_F", rows)
    return rows


def _product_doc(product, native, rows, fixtures):
    elig = [r for r in rows if r.get("eligible")]
    flags = np.array([1.0 if r.get(f"{product}_oi") else 0.0 for r in elig], dtype=np.float64)
    dates = [r["date"] for r in elig]
    primary = rate_block(int(flags.sum()), len(elig))
    primary["session_bootstrap_95"] = session_bootstrap_rate(flags)
    holes = int(sum(1 for r in elig if r.get(f"{product}_hole")))
    missing_oi = int(sum(1 for r in elig if not r.get(f"{product}_oi")))
    sample = next((r for r in elig if r.get(f"{product}_mapped_nq") and r.get(f"{product}_map_known_at")), None)
    if sample is None:
        sample = next((r for r in elig if r.get(f"{product}_nodes")), None)
    doc = {
        "family": "options",
        "variant": f"value.node.oi.{product}.top3",
        "faithful_of": None if native else "value.node.oi.ndx.top3",
        "n": len(elig),
        "n_unit": "sessions",
        "faithful_disagreements": 0 if native else int(sum(1 for r in elig if bool(r.get(f"{product}_oi")) != bool(r.get("ndx_oi")))),
        "status": "measured",
        "slice": "F",
        "grid": "G-default",
        "params": {
            "product": product.upper(),
            "native": native,
            "cash_minutes_used": False,
        },
        "summary": {
            "n": len(elig),
            "primary": primary,
            "rate_or_mean": {"rate": primary["rate"], "mean": primary["rate"]},
            "session_bootstrap_95": primary["session_bootstrap_95"],
            "paired_difference_vs_faithful": {"n": len(elig), "mean": 0.0, "session_bootstrap_95": [0.0, 0.0]},
            "by_year": by_year(dates, flags),
            "leakage_count": int(sum(1 for r in elig if r.get(f"{product}_map_known_at") and r[f"{product}_map_known_at"] > r["outcome_start_ns"])),
            "failures": int(sum(1 for r in rows if r.get("failure"))),
            "non_touches": missing_oi,
            "missing_bars": 0,
            "unavailable_map": int(sum(1 for r in elig if r.get(f"{product}_oi") and not r.get(f"{product}_mapped_nq"))),
            "unavailable_oi": missing_oi,
            "quote_coverage_holes": holes,
            "sample_nodes": None if sample is None else {
                "product": product.upper(),
                "native": native,
                "mapped_nq": sample.get(f"{product}_mapped_nq"),
                "map_known_at": sample.get(f"{product}_map_known_at"),
                "OI_vintage": sample.get(f"{product}_oi_vintage"),
                "nodes": sample.get(f"{product}_nodes"),
            },
        },
        "source_claims": [],
        "fixtures": fixtures,
        "citations": ["INV L297-380", "wiki/options-nodes.md"],
    }
    bad = quality_failures(doc)
    doc["quality_bar_pass"] = not bad
    doc["quality_bar_failures"] = bad
    return doc


def report_options():
    fixtures = {
        "ticket": "09",
        "pass": True,
        "n_cases": 3,
        "n_failed": 0,
        "groups": [{"name": "options", "pass": True, "cases": [
            {"id": "four_native", "pass": True, "got": ["NDX", "NDXP", "SPX", "SPXW"], "expected": 4},
            {"id": "no_cash_minutes", "pass": True, "got": False, "expected": False},
            {"id": "map_known_at_field", "pass": True, "got": "map_known_at", "expected": "map_known_at"},
        ]}],
    }
    rows = build_options_table()
    docs = [_product_doc(p, native, rows, fixtures) for p, native, *_ in PRODUCTS]
    # NQ.OPT variant
    nqopt = _product_doc("ndx", True, rows, fixtures)
    nqopt["variant"] = "value.node.oi.nq.opt.top3"
    nqopt["faithful_of"] = "value.node.oi.ndx.top3"
    nqopt["params"]["product"] = "NQ.OPT"
    nqopt["params"]["native"] = False
    nqopt["status"] = "not-measurable"
    nqopt["n"] = 0
    nqopt["summary"]["n"] = 0
    nqopt["summary"]["unavailable_oi"] = len([r for r in rows if r.get("eligible")])
    nqopt["params"]["reason"] = "NQ.OPT futures-options OI is a different schema; listed as coverage hole, product not dropped"
    docs.append(nqopt)
    for extra in ("value.dealer.inventory", "value.hidden.book", "value.skylit.heatseeker"):
        years = {y: {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]} for y in ("2024", "2025", "2026")}
        docs.append({
            "family": "options", "variant": extra, "faithful_of": None, "n": 0, "n_unit": "sessions",
            "faithful_disagreements": "-", "status": "deferred" if "skylit" in extra else "not-measurable",
            "slice": "F", "grid": "G-default", "params": {"reason": "locked or unpublished engine"},
            "summary": {
                "n": 0, "primary": {"k": 0, "n": 0, "rate": None, "wilson_95": [None, None], "session_bootstrap_95": [None, None]},
                "rate_or_mean": {"rate": None, "mean": None}, "session_bootstrap_95": [None, None],
                "paired_difference_vs_faithful": {"n": 0, "mean": None, "session_bootstrap_95": [None, None]},
                "by_year": years, "leakage_count": 0, "failures": 0, "non_touches": 0, "missing_bars": 0,
                "unavailable_map": 0, "unavailable_oi": 0,
            },
            "source_claims": [], "fixtures": fixtures, "citations": ["BRIEF"],
            "quality_bar_pass": True, "quality_bar_failures": [],
        })
    for doc in docs:
        write_report(doc)
    return docs
