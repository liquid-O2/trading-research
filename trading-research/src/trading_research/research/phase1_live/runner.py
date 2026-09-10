"""check / run / report for Phase 1 live objects."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from trading_research.research.phase1_live import FAMILIES, VERSION
from trading_research.research.phase1_live.report import REPORT_ROOT, phase_line
from trading_research.research.phase1_live.slice import load_calendar, slice_dates

FAMILY_REPORT = {
    "range": "trading_research.research.phase1_live.family_range:report_range",
    "path": "trading_research.research.phase1_live.family_path:report_path",
    "open": "trading_research.research.phase1_live.family_open:report_open",
    "env": "trading_research.research.phase1_live.family_env:report_env",
    "vol": "trading_research.research.phase1_live.family_vol:report_vol",
    "flow": "trading_research.research.phase1_live.family_flow:report_flow",
    "value": "trading_research.research.phase1_live.family_value:report_value",
    "fail": "trading_research.research.phase1_live.family_fail:report_fail",
    "gap": "trading_research.research.phase1_live.family_gap:report_gap",
    "block": "trading_research.research.phase1_live.family_gap:report_block",
    "tpo": "trading_research.research.phase1_live.family_gap:report_tpo",
    "options": "trading_research.research.phase1_live.family_options:report_options",
}


def _load_callable(spec: str):
    mod_name, fn = spec.split(":")
    import importlib
    mod = importlib.import_module(mod_name)
    return getattr(mod, fn)


def cmd_check(args) -> int:
    calendar = load_calendar()
    for slice_id in ("F", "L"):
        dates = slice_dates(calendar, slice_id)
        print(f"slice {slice_id}: n_dates={len(dates)} first={dates[0]} last={dates[-1]}")
    from trading_research.research.phase1_live.compute import load_rows
    rows = load_rows("sessions_F")
    if rows:
        dropped = [r["date"] for r in rows if not r.get("eligible")]
        print(f"F table sessions={len(rows)} dropped={len(dropped)}")
        for d in dropped[:50]:
            print(f"dropped {d}")
        if len(dropped) > 50:
            print(f"... {len(dropped) - 50} more")
    else:
        print("F table not built yet")
    print(f"version {VERSION}")
    return 0


def cmd_run(args) -> int:
    from trading_research.research.phase1_live.family_range import ensure_tables
    families = args.family or ["range"]
    slice_id = args.slice or "F"
    t0 = time.perf_counter()
    if any(f in families for f in ("range", "path")):
        ensure_tables(with_l=slice_id == "L" or True)
    if any(f in families for f in ("flow", "value")):
        from trading_research.research.phase1_live.mbp1_extract import extract_F, extract_month
        if args.month:
            y, m = args.month.split("-")
            extract_month(int(y), int(m))
        else:
            extract_F()
    print(f"run families={families} slice={slice_id} wall_s={time.perf_counter()-t0:.3f}")
    return 0


def _docs_for_family(family: str) -> list[dict]:
    spec = FAMILY_REPORT.get(family)
    if spec is None:
        return []
    return _load_callable(spec)()


def cmd_report(args) -> int:
    families = args.family or list(FAMILIES)
    unknown = [f for f in families if f not in FAMILIES]
    if unknown:
        print(f"unknown family {unknown}", file=sys.stderr)
        return 2
    all_docs = []
    failed = False
    for family in families:
        if family not in FAMILY_REPORT:
            print(f"{family} | (unbuilt) | 0 | - | deferred |")
            failed = True
            continue
        docs = _docs_for_family(family)
        for doc in docs:
            print(phase_line(doc))
            if not doc.get("quality_bar_pass"):
                print(f"quality-bar fail {doc['variant']}: {doc.get('quality_bar_failures')}", file=sys.stderr)
                failed = True
            if doc.get("status") == "measured" and (doc.get("summary") or {}).get("leakage_count"):
                print(f"leakage {doc['variant']}", file=sys.stderr)
                failed = True
            all_docs.append(doc)
        measured = any(d.get("status") == "measured" for d in docs)
        if not measured:
            failed = True
    if args.family is None:
        missing = [f for f in FAMILIES if f not in {d.get("family") for d in all_docs}]
        if missing:
            print(f"families without reports: {missing}", file=sys.stderr)
            failed = True
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="run_phase1_objects")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    run = sub.add_parser("run")
    run.add_argument("--family", action="append")
    run.add_argument("--slice", choices=("F", "L"), default="F")
    run.add_argument("--month", help="YYYY-MM MBP-1 extract")
    rep = sub.add_parser("report")
    rep.add_argument("--family", action="append")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "check":
        return cmd_check(args)
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "report":
        return cmd_report(args)
    return 2
