#!/usr/bin/env python3
"""The Sires grading study at the box level: one row per alive generated
aggression box on each dated session (the box table of ``sires_box_table.py``
as ``run_sires_population.alive_boxes`` admits it), labelled by whether it
overlaps a box the author drew that session (the record's ``levels``: every
``[lo, hi]`` pair, single lines within three points), with the box's
construction, its memory and location at the moment it can be traded, and the
object layer at its midpoint. Section 12.3 recovers 11-13 of his 15 drawn
boxes at 13-34 generated a session: which of the generated boxes he draws is
the first grading cut, before which fill at a box.

    build_grading_dataset_sires_boxes.py --boxes boxes.parquet --out <dir>
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parents[1] / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json"
MINUTE = 60 * 1_000_000_000
LINE_TOLERANCE = Decimal("3")
BOX_WIDTH_LIMIT = Decimal("15")


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _d(value):
    return None if value is None else Decimal(str(value))


def drawn_boxes(levels: dict) -> list[tuple[Decimal, Decimal, str]]:
    """Every drawn band of the record as (lo, hi, name); a single line as a
    band of LINE_TOLERANCE either side."""
    out = []

    def add(name, value):
        if isinstance(value, (list, tuple)) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value):
            lo, hi = sorted(Decimal(str(v)) for v in value)
            out.append((lo, hi, name))
        elif isinstance(value, (list, tuple)):
            for i, item in enumerate(value):
                add(f"{name}[{i}]", item)
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            px = Decimal(str(value))
            out.append((px - LINE_TOLERANCE, px + LINE_TOLERANCE, name))

    for name, value in (levels or {}).items():
        add(name, value)
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--boxes", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    import pandas as pd

    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    gf = _module("grading_features")
    rp = _module("run_sires_population")
    rs = _module("replay_sires")
    table = pd.read_parquet(args.boxes)
    doc = json.loads(EXAMPLES.read_text())
    examples = doc["examples"] if isinstance(doc, dict) and "examples" in doc else doc
    args.out.mkdir(parents=True, exist_ok=True)
    n_rows = n_pos = 0
    with (args.out / "rows.jsonl").open("w") as sink:
        for example in examples:
            if example.get("family") != "SIRES":
                continue
            day = str(example.get("session_date") or example.get("date"))
            # his boxes are a few points wide; the wide drawn bands (balance,
            # dealing range, prior-day bands of 50-100 points) are context, not
            # boxes, and would label most of a session's generated boxes
            drawn = [b for b in drawn_boxes(example.get("levels") or {}) if b[1] - b[0] <= BOX_WIDTH_LIMIT]
            if not drawn:
                continue
            market = load_source_market(day)
            session_open = int(market.start)
            open_ns = int(market.at("09:30"))
            end_ns = int(market.at("16:00"))
            rows_bars = rs.bars_between(market, session_open, end_ns)
            boxes = rp.alive_boxes(table, session_open, end_ns)
            prior = gf.prior_day_profile(market)
            rows = []
            for box in boxes:
                lo, hi = _d(box["lo"]), _d(box["hi"])
                mid = (lo + hi) / 2
                known = int(box["known_at"])
                # the box can be traded once it is known and the cash session is open
                at = max(known, open_ns)
                if at >= end_ns:
                    continue
                overlap = [name for a, b, name in drawn if lo <= b and hi >= a]
                before = [r for r in rows_bars if int(r["end"]) <= at]
                touched = sum(1 for r in before if int(r["start"]) >= known and r["L"] <= hi and r["H"] >= lo)
                rth = [r for r in before if int(r["start"]) >= open_ns]
                rth_open = rth[0]["O"] if rth else None
                highs = [r["H"] for r in before]
                lows = [r["L"] for r in before]
                span = (max(highs) - min(lows)) if highs and lows else None
                aggressor = box.get("aggressor") or box.get("sides")
                row = {
                    "family": "SI",
                    "example_id": example["id"],
                    "session": day,
                    "label": 1 if overlap else 0,
                    "box": box["id"],
                    "drawn_as": ";".join(overlap) or None,
                    "decision_at": at,
                    "reference_px": float(mid),
                    "side": "long" if aggressor == "B" else ("short" if aggressor == "S" else "long"),
                    "box_width": float(hi - lo),
                    "n_orders": int(box.get("n_orders") or 0),
                    "contracts": int(box.get("contracts") or 0),
                    "largest_order": int(box.get("largest") or 0),
                    "aggressor": str(aggressor),
                    "box_age_minutes": round((at - known) / MINUTE, 1),
                    "from_prior_session": bool(known < session_open),
                    "minutes_from_open": round((at - open_ns) / MINUTE, 1),
                    "prior_touches": touched,
                    "level_vs_rth_open": None if rth_open is None else float(mid - rth_open),
                    "range_position": None if not span else float((mid - min(lows)) / span),
                }
                side = row["side"]
                developing = gf.developing_profile(market, session_open, at)
                row.update(gf.profile_features(mid, prior, developing))
                row.update(gf.delta_features(market, at, None))
                row.update(gf.aggression_features(mid, at, session_open))
                row.update(gf.author_profile_features(market, mid, side, at, prior))
                row.update(gf.context_profile_features(market, mid, side, at))
                row.update(gf.weekly_delta_features(market, mid, side))
                rows.append(row)
            for row in rows:
                sink.write(json.dumps(row, default=str) + "\n")
            n_rows += len(rows)
            n_pos += sum(r["label"] for r in rows)
            print(json.dumps({"id": example["id"], "session": day, "boxes": len(rows), "drawn": len(drawn), "positives": sum(r["label"] for r in rows)}), flush=True)
    print(json.dumps({"event": "dataset_complete", "rows": n_rows, "positives": n_pos}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
