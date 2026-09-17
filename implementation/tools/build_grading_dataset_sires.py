#!/usr/bin/env python3
"""The grading study's dataset for Sires and Saint: one row per fill the
entry mechanics admit at every box generated from order-level prints on the
dated sessions, labelled with the author's tickets.

Boxes are the aggression clusters of ``sires_levels_fit.py`` (session-adaptive
size cut, generated from the prior session's cash open so the prior day's
bands exist). A fill counts only after its box is known. Features are what the
author says he reads on a box and what the Refill paper found to carry
selection (memory, construction, location, flow), all observable at the fill:

* the play and mode (sweep-and-fail, defended band, reclaim, break-retest),
  the cycle index, minutes from the cash open, the side;
* construction: box width, number of orders, contracts, largest order, the
  aggressor side, whether the aggression was absorbed, the box's age, whether
  it was carried in from the prior session, the side against the aggressor;
* memory: how many one-minute bars touched the box before the fill;
* location: the box against the RTH open and its position in the session's
  range so far;
* risk: stop points of the fill.

Label: a ticket on the session with the same side within 10 points of the
fill on the fill's five-minute bar. Output rows.jsonl for fit_grading.py.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[1]
sys.path.insert(0, str(WORKTREE / "implementation/src"))

from trading_research.research.rule_discovery.source_adapters.common import load_source_market  # noqa: E402


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rs = _module("replay_sires")
fit = _module("sires_levels_fit")

NS = 1_000_000_000
MINUTE = 60 * NS
TOLERANCE = Decimal("10")
PARAMS = {"min_size": 30, "band": 6.0, "window_s": 180, "min_orders": 2, "adaptive": {"quantile": 0.995, "lookback_s": 3600, "floor": 20}, "follow_s": 120, "give": 1.5}
FAMILY_CODE = {"SIRES": "SI", "SAINT": "ST"}


def _d(value):
    return None if value is None else Decimal(str(value))


def boxes_for(day: str, end_ns: int) -> list[dict]:
    start = fit.ns_at(day, "09:30", -1)
    orders = fit.orders_between(day, start, end_ns)
    if orders is None or orders.empty:
        return []
    boxes = fit.cluster_orders(orders, min_size=PARAMS["min_size"], band=PARAMS["band"], window_s=PARAMS["window_s"], min_orders=PARAMS["min_orders"], adaptive=PARAMS["adaptive"])
    kept = fit.absorbed(orders, boxes, follow_s=PARAMS["follow_s"], give=PARAMS["give"], give_in_ranges=True)
    absorbed_keys = {(b["lo"], b["hi"], int(b["known_at"])) for b in kept}
    for box in boxes:
        box["absorbed"] = (box["lo"], box["hi"], int(box["known_at"])) in absorbed_keys
    return boxes


def fills_for_box(rows: list[dict], box: dict, side: str) -> list[dict]:
    """Every fill the mechanics admit at the box on one side (the same calls
    as replay_sires.candidates_for for a box level)."""
    lo, hi = _d(box["lo"]), _d(box["hi"])
    out = []
    line = hi if side == "short" else lo
    for cycle in rs.sweep_fail_cycles(rows, line, side):
        for fill in rs.fills_after_failure(rows, cycle, line, side, box_low=lo, box_high=hi):
            out.append({**fill, "play": "failure", "cycle": cycle["cycle"], "level_px": line})
    near = hi if side == "long" else lo
    for fill in rs.defended_band_fills(rows, lo, hi, side):
        out.append({**fill, "play": "defence", "cycle": 0, "level_px": near})
    for fill in rs.reclaim_fills(rows, lo, hi, side):
        out.append({**fill, "play": "reclaim", "cycle": 0, "level_px": near})
    for fill in rs.break_stop_fills(rows, near, side):
        out.append({**fill, "play": "break", "cycle": 0, "level_px": near})
    return [fill for fill in out if int(fill["at"]) > int(box["known_at"])]


def session_features(rows: list[dict], open_ns: int, at_ns: int, box: dict) -> dict:
    lo, hi = _d(box["lo"]), _d(box["hi"])
    mid = (lo + hi) / 2
    before = [row for row in rows if int(row["end"]) <= at_ns]
    touched = sum(1 for row in before if int(row["start"]) >= int(box["known_at"]) and row["L"] <= hi and row["H"] >= lo)
    rth = [row for row in before if int(row["start"]) >= open_ns]
    rth_open = rth[0]["O"] if rth else None
    highs = [row["H"] for row in before]
    lows = [row["L"] for row in before]
    span = (max(highs) - min(lows)) if highs and lows else None
    return {
        "prior_touches": touched,
        "level_vs_rth_open": None if rth_open is None else float(mid - rth_open),
        "range_position": None if not span else float((mid - min(lows)) / span),
    }


def rows_for(example: dict, day: str, tickets: list[dict], market) -> list[dict]:
    rows = rs.bars_between(market, int(market.start), int(market.end))
    open_ns = int(market.at("09:30"))
    boxes = boxes_for(day, int(market.end))
    windows = [(t, rs.parse_window(market, t)) for t in tickets]
    out = []
    for index, box in enumerate(boxes):
        lo, hi = _d(box["lo"]), _d(box["hi"])
        for side in ("long", "short"):
            for fill in fills_for_box(rows, box, side):
                at = int(fill["at"])
                entry = _d(fill["entry"])
                stop = _d(fill.get("stop"))
                label = 0
                for ticket, window in windows:
                    price = _d(ticket.get("price"))
                    if ticket["side"] == side and price is not None and abs(entry - price) <= TOLERANCE and rs.bars_from_window(at, window) <= rs.BARS_ALLOWED:
                        label = 1
                aggressor = box.get("aggressor") or box.get("sides")
                out.append(
                    {
                        "family": FAMILY_CODE.get(example.get("family"), "SI"),
                        "example_id": example["id"],
                        "session": day,
                        "label": label,
                        "box": f"gen[{index}] {box['first']}-{box['last']}",
                        "play": fill["play"],
                        "mode": fill.get("mode"),
                        "side": side,
                        "cycle": fill.get("cycle"),
                        "minutes_from_open": round((at - open_ns) / MINUTE, 1),
                        "box_width": float(hi - lo),
                        "n_orders": int(box["n_orders"]),
                        "contracts": int(box["contracts"]),
                        "largest_order": int(box["largest"]),
                        "aggressor": str(aggressor),
                        "absorbed": bool(box.get("absorbed")),
                        "box_age_minutes": round((at - int(box["known_at"])) / MINUTE, 1),
                        "from_prior_session": bool(int(box["known_at"]) < int(market.start)),
                        "side_with_aggressor": None if aggressor not in ("B", "S") else ((side == "long") == (aggressor == "B")),
                        "stop_points": None if stop is None else float(abs(entry - stop)),
                        **session_features(rows, open_ns, at, box),
                    }
                )
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--only", default=None)
    args = parser.parse_args(argv)
    examples = json.loads(rs.EXAMPLES.read_text())["examples"]
    wanted = set(args.only.split(",")) if args.only else None
    rows: list[dict] = []
    for example in examples:
        if example.get("family") not in FAMILY_CODE or not example.get("inside_tape"):
            continue
        if wanted and example["id"] not in wanted:
            continue
        by_day: dict[str, list[dict]] = {}
        for action in rs.entry_windows(example):
            by_day.setdefault(rs.session_day(example, action), []).append(action)
        for day, tickets in by_day.items():
            market = load_source_market(day)
            day_rows = rows_for(example, day, tickets, market)
            rows.extend(day_rows)
            print(json.dumps({"id": example["id"], "session": day, "candidates": len(day_rows), "positives": sum(r["label"] for r in day_rows), "tickets": len(tickets)}), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "rows.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, default=str) + "\n")
    print(json.dumps({"event": "dataset_complete", "rows": len(rows), "positives": sum(r["label"] for r in rows), "sessions": len({(r['example_id'], r['session']) for r in rows})}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
