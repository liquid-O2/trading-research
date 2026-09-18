#!/usr/bin/env python3
"""The chance rate of a ticket replay. A replay calls a dated ticket
reproduced when the framework has a source-supported fill on his side within a
price tolerance and a bar or so of the printed time. With many levels and
fill modes a session that can happen by chance, so the reproduction count
means nothing without its placebo: the same replay run on FAKE tickets, each
real ticket moved by a fixed number of minutes on the same day and side and
repriced at the market's price at that minute. The share of fake tickets the
framework "reproduces" is the chance rate the real count must beat.

    replay_placebo.py --out <dir> [--shifts -90,-60,-40,-20,20,40,60,90]
        [--levels drawn|generated] [-- <extra replay_sires.py arguments>]

Sires and Saint (replay_sires.py) for now; the record's drawn levels are kept
on the fake tickets in ``drawn`` mode (the question there is whether his
levels at a random minute also produce a fill at the market's price).
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
MINUTE = 60 * 1_000_000_000


def _module(name: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _minutes(text: str) -> int:
    return int(text[:2]) * 60 + int(text[3:5])


def _fmt(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _segment(minutes: int) -> str:
    """The part of the account day a printed minute belongs to: a fake ticket stays in its own."""
    if minutes >= 18 * 60:
        return "evening"
    if minutes < 9 * 60 + 30:
        return "overnight"
    return "cash"


def shifted_action(rs, market, action: dict, shift: int) -> dict | None:
    text = str(action["time_et"])
    first, _, last = text.partition("-")
    a = _minutes(first.strip()[:5])
    b = _minutes(last.strip()[:5]) if last.strip()[:5].replace(":", "").isdigit() else a
    na, nb = a + shift, b + shift
    if na < 0 or nb >= 24 * 60 or _segment(na) != _segment(a) or _segment(nb) != _segment(b):
        return None
    if _segment(a) == "cash" and (na < 9 * 60 + 31 or nb > 15 * 60 + 55):
        return None
    new = copy.deepcopy(action)
    new["time_et"] = _fmt(na) if na == nb and "-" not in text else f"{_fmt(na)}-{_fmt(nb)}"
    off = -1 if na >= 18 * 60 else 0
    start = int(market.at(_fmt(na), off))
    bars = rs.bars_between(market, start, start + MINUTE)
    if not bars:
        return None
    new["price"] = float(bars[0]["C"])  # the market's price in the fake minute
    for key in ("stop", "target", "note"):
        new.pop(key, None)
    new["placebo_of"] = {"time_et": text, "price": action.get("price"), "shift_minutes": shift}
    return new


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--shifts", default="-90,-60,-40,-20,20,40,60,90")
    parser.add_argument("--levels", choices=("drawn", "generated"), default="drawn")
    parser.add_argument("extra", nargs="*", help="extra arguments passed to replay_sires.py (after --)")
    args = parser.parse_args(argv)
    rs = _module("replay_sires")
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    doc = json.loads(rs.EXAMPLES.read_text())
    examples = [e for e in doc["examples"] if e.get("inside_tape") and e["id"].startswith(("SI", "SA")) and any(a.get("proper_entry") for a in e.get("actions") or [])]
    args.out.mkdir(parents=True, exist_ok=True)
    markets: dict = {}
    results = []
    original = rs.EXAMPLES
    for shift in [0] + [int(s) for s in args.shifts.split(",") if s.strip()]:
        fake = []
        skipped = 0
        for ex in examples:
            new_ex = copy.deepcopy(ex)
            kept = []
            for action in ex.get("actions") or []:
                if not action.get("proper_entry"):
                    continue
                if shift == 0:
                    kept.append(copy.deepcopy(action))
                    continue
                day = rs.session_day(ex, action)
                if day not in markets:
                    markets[day] = load_source_market(day)
                moved = shifted_action(rs, markets[day], action, shift)
                if moved is None:
                    skipped += 1
                    continue
                kept.append(moved)
            if kept:
                new_ex["actions"] = kept
                fake.append(new_ex)
        run_dir = args.out / f"shift_{shift:+d}"
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "EXAMPLES.json"
        path.write_text(json.dumps({"examples": fake}, default=str) + "\n")
        rs.EXAMPLES = path
        try:
            rs.main(["--out", str(run_dir), "--levels", args.levels, *args.extra])
        finally:
            rs.EXAMPLES = original
        summary = json.loads((run_dir / "REPLAY_SIRES.json").read_text())
        rows = summary["rows"]
        results.append({"shift_minutes": shift, "tickets": len(rows), "reproduced": sum(1 for r in rows if r["strict_10"]), "skipped_out_of_segment": skipped, "median_candidates_on_side": sorted(r["n_candidates_side"] for r in rows)[len(rows) // 2] if rows else None, "median_in_window": sorted(r["n_in_window"] for r in rows)[len(rows) // 2] if rows else None})
        print(json.dumps(results[-1]), flush=True)
    real = results[0]
    fakes = results[1:]
    n_fake = sum(r["tickets"] for r in fakes)
    hit_fake = sum(r["reproduced"] for r in fakes)
    lines = [f"# Placebo control of the Sires and Saint ticket replay ({args.levels} levels)", "", f"Real tickets: {real['reproduced']} of {real['tickets']} reproduced. Fake tickets (each real ticket moved in time on its own day and side, repriced at the market): {hit_fake} of {n_fake} reproduced, a chance rate of {hit_fake / max(1, n_fake):.2f}.", "", "| shift (minutes) | tickets | reproduced | rate | median fills on his side | median fills in the window |", "| ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in results:
        lines.append(f"| {r['shift_minutes']:+d} | {r['tickets']} | {r['reproduced']} | {r['reproduced'] / max(1, r['tickets']):.2f} | {r['median_candidates_on_side']} | {r['median_in_window']} |")
    (args.out / "PLACEBO.md").write_text("\n".join(lines) + "\n")
    (args.out / "PLACEBO.json").write_text(json.dumps({"levels": args.levels, "extra": args.extra, "results": results, "chance_rate": hit_fake / max(1, n_fake)}, indent=1) + "\n")
    print(f"wrote {args.out / 'PLACEBO.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
