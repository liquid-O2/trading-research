#!/usr/bin/env python3
"""Member (K10) ticket replay on the ES tape.

The K10 case study charts ES-202609 (Deepchart, ET). Its two trades are dated
2026-08-03 by the tape (the PDF was generated 2026-08-04 11:52 UTC; the
September contract prints the chart's balance under 7,564 from 06:30, the
09:29 drop to 7,544.75, the 7,542.75 low at 09:30, 7,596 at 10:16 and the
left panel's last price 7,614.50 at 12:16). The levels are his drawn pairs
(record ``levels``); the mechanics are the same one-minute fills Sires' and
Saint's tickets reproduce on (replay_sires.py): a sweep of the level that
fails, a defended band, a reclaim, a break-and-retest. A ticket is reproduced
when a fill on his side lands within 10 points of the printed price on the
printed five-minute bar.

ES one-minute bars come straight from the quantpad continuous-futures parquet
(instrument 42140870 = ESU6 on that date), so no NQ market view is involved.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pyarrow.compute as pc
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[1]
ET = ZoneInfo("America/New_York")
NS = 1_000_000_000
MINUTE = 60 * NS
ES_BARS = Path("/workspace/data/quantpad/cme__es-continuous-futures__ohlcv-1m")


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rs = _module("replay_sires")


def ns_at(day: str, hhmm: str) -> int:
    y, m, d = (int(x) for x in day.split("-"))
    return int(datetime(y, m, d, int(hhmm[:2]), int(hhmm[3:5]), tzinfo=ET).timestamp() * NS)


def es_bars(day: str, start_ns: int, end_ns: int) -> list[dict]:
    """One-minute ES bars in [start, end) as the row dicts the mechanics read."""
    table = pq.read_table(ES_BARS / f"{day[:4]}.parquet")
    t = table["t"]
    unit = NS if pc.max(t).as_py() > 10**15 else 1_000_000
    lo, hi = start_ns // unit * 1, end_ns // unit * 1
    sub = table.filter(pc.and_(pc.greater_equal(t, lo), pc.less(t, hi))).to_pandas().sort_values("t")
    rows = []
    for row in sub.itertuples(index=False):
        start = int(row.t) * unit
        rows.append({"start": start, "end": start + MINUTE, "O": Decimal(str(row.o)), "H": Decimal(str(row.h)), "L": Decimal(str(row.l)), "C": Decimal(str(row.c))})
    return rows


def et_str(ns: int) -> str:
    return datetime.fromtimestamp(ns / NS, tz=ET).strftime("%H:%M")


def levels_from(record: dict) -> list[dict]:
    out = []
    for name, value in (record.get("levels") or {}).items():
        if isinstance(value, list) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value):
            lo, hi = sorted(Decimal(str(v)) for v in value)
            out.append({"name": name, "low": lo, "high": hi})
    return out


def candidates(rows: list[dict], levels: list[dict], side: str) -> list[dict]:
    out = []
    for lvl in levels:
        lo, hi = lvl["low"], lvl["high"]
        line = hi if side == "short" else lo
        for cycle in rs.sweep_fail_cycles(rows, line, side):
            for fill in rs.fills_after_failure(rows, cycle, line, side, box_low=lo, box_high=hi):
                out.append({**fill, "level": lvl["name"], "level_px": line, "play": "failure", "cycle": cycle["cycle"]})
        near = hi if side == "long" else lo
        for fill in rs.defended_band_fills(rows, lo, hi, side):
            out.append({**fill, "level": lvl["name"], "level_px": near, "play": "defence"})
        for fill in rs.reclaim_fills(rows, lo, hi, side):
            out.append({**fill, "level": lvl["name"], "level_px": near, "play": "reclaim"})
        for fill in rs.break_stop_fills(rows, near, side):
            out.append({**fill, "level": lvl["name"], "level_px": near, "play": "break"})
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--example", default="MB-2026-07-K10")
    args = parser.parse_args(argv)
    examples = json.loads(rs.EXAMPLES.read_text())["examples"]
    record = next(e for e in examples if e["id"] == args.example)
    day = record["date"]
    rows = es_bars(day, ns_at(day, "00:00"), ns_at(day, "16:00"))
    levels = levels_from(record)
    table = []
    for action in rs.entry_windows(record):
        first, _, last = str(action["time_et"]).partition("-")
        window = (ns_at(day, first.strip()[:5]), ns_at(day, (last or first).strip()[:5]))
        price = Decimal(str(action["price"]))
        scored = []
        for c in candidates([r for r in rows if r["end"] <= window[1] + 60 * MINUTE], levels, action["side"]):
            bars = rs.bars_from_window(int(c["at"]), window)
            delta = abs(c["entry"] - price)
            scored.append({**c, "bars": bars, "delta": delta, "strict_10": bars <= rs.BARS_ALLOWED and delta <= rs.TOLERANCE})
        hits = [c for c in scored if c["strict_10"]]
        best = min(hits, key=lambda c: (c["delta"], c["bars"])) if hits else (min(scored, key=lambda c: (c["bars"], c["delta"])) if scored else None)
        row = {
            "example_id": record["id"], "session": day, "time_et": action["time_et"], "side": action["side"], "price": float(price),
            "strict_10": bool(hits), "n_candidates_side": len(scored),
            "best": None if best is None else {"mode": best["mode"], "play": best["play"], "level": best["level"], "level_px": float(best["level_px"]), "entry": float(best["entry"]), "at": et_str(int(best["at"])), "delta": float(best["delta"]), "bars": best["bars"]},
            "in_window": [{"mode": c["mode"], "play": c["play"], "level": c["level"], "entry": float(c["entry"]), "at": et_str(int(c["at"])), "delta": float(c["delta"])} for c in sorted((c for c in scored if c["bars"] <= rs.BARS_ALLOWED), key=lambda c: c["delta"])[:8]],
        }
        table.append(row)
        print(json.dumps(row, default=str), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    summary = {"example": record["id"], "session": day, "instrument": record.get("instrument"), "n_entries": len(table), "n_strict_10": sum(1 for r in table if r["strict_10"]), "levels": [{k: (float(v) if isinstance(v, Decimal) else v) for k, v in l.items()} for l in levels], "rows": table}
    (args.out / "REPLAY_MEMBER.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    lines = ["# Member (K10) ticket replay on the ES-202609 tape, 2026-08-03", "", f"{summary['n_strict_10']} of {summary['n_entries']} ticketed fills reproduced within 10 points on the printed five-minute bar by a source-supported fill at one of his drawn levels, on his side.", "", "| ticket | side | printed | our fill | mode / play | level | d | bars | ok |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in table:
        b = r["best"] or {}
        lines.append(f"| {r['time_et']} | {r['side']} | {r['price']} | {b.get('entry')} at {b.get('at')} | {b.get('mode')} / {b.get('play')} | {b.get('level')} {b.get('level_px')} | {b.get('delta')} | {b.get('bars')} | {'yes' if r['strict_10'] else 'no'} |")
    (args.out / "REPLAY_MEMBER.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"event": "replay_complete", "n": len(table), "strict_10": summary["n_strict_10"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
