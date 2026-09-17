#!/usr/bin/env python3
"""The Sires grading dataset on the population's own candidate list: one row
per admitted opportunity of ``run_sires_population.py --export-candidates``
(a fill the mechanics admit at an alive generated box, after the box is
known, with a stop and an objective of at least the minimum reward), on the
dated sessions, labelled with the author's tickets (same side, within ten
points of the fill on the ticket's bars) and augmented with the object layer
(profiles and nodes, delta, aggression, memory, location, composite, weekly
delta). Output rows.jsonl for fit_grading.py.

    build_grading_dataset_sires_v2.py --population <rows.jsonl> --out <dir>
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


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _d(value):
    return None if value is None else Decimal(str(value))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    gf = _module("grading_features")
    v1 = _module("build_grading_dataset_sires")
    rs = v1.rs
    doc = json.loads(EXAMPLES.read_text())
    examples = doc["examples"] if isinstance(doc, dict) and "examples" in doc else doc
    by_day = {}
    for example in examples:
        if example.get("family") != "SIRES":
            continue
        tickets = [a for a in example.get("actions") or [] if a.get("proper_entry")]
        if tickets:
            by_day[str(example.get("session_date") or example.get("date"))] = (example, tickets)
    args.out.mkdir(parents=True, exist_ok=True)
    n_rows = n_pos = 0
    with (args.out / "rows.jsonl").open("w") as sink, args.population.open() as source:
        for line in source:
            session = json.loads(line)
            day = session.get("date")
            if session.get("kind") != "session" or day not in by_day or "candidates" not in session:
                continue
            example, tickets = by_day[day]
            market = load_source_market(day)
            open_ns = int(market.at("09:30"))
            session_open = int(market.start)
            windows = [(t, rs.parse_window(market, t)) for t in tickets]
            prior = gf.prior_day_profile(market)
            cache = {}
            rows = []
            for cand in session["candidates"]:
                at = int(cand["decision_at"])
                side = cand["side"]
                geometry = cand.get("geometry") or {}
                entry, stop, target = _d(geometry.get("entry")), _d(geometry.get("stop")), _d(geometry.get("target"))
                values = cand.get("values") or {}
                level = _d(values.get("reference_px"))
                label = 0
                for ticket, window in windows:
                    price = _d(ticket.get("price"))
                    if ticket["side"] == side and price is not None and entry is not None and abs(entry - price) <= v1.TOLERANCE and rs.bars_from_window(at, window) <= rs.BARS_ALLOWED:
                        label = 1
                risk = None if entry is None or stop is None else float(abs(entry - stop))
                reward = None if entry is None or target is None else float(abs(target - entry))
                row = {
                    "family": "SI",
                    "example_id": example["id"],
                    "session": day,
                    "label": label,
                    "box": (cand.get("reference") or {}).get("id"),
                    "play": cand.get("branch"),
                    "mode": values.get("confirmation_mode"),
                    "side": side,
                    "cycle": values.get("cycle"),
                    "decision_at": at,
                    "reference_px": None if level is None else float(level),
                    "entry_px": None if entry is None else float(entry),
                    "minutes_from_open": round((at - open_ns) / MINUTE, 1),
                    "stop_points": risk,
                    "reward_points": reward,
                    "reward_to_risk": None if not risk or reward is None else round(reward / risk, 3),
                }
                if level is not None:
                    minute = at // MINUTE
                    if minute not in cache:
                        cache[minute] = gf.developing_profile(market, session_open, at)
                    developing = cache[minute]
                    row.update(gf.profile_features(level, prior, developing))
                    row.update(gf.delta_features(market, at, None))
                    row.update(gf.aggression_features(level, at, session_open))
                    row.update(gf.memory_location_features(market, level, side, at, session_open, []))
                    row.update(gf.author_profile_features(market, level, side, at, prior))
                    row.update(gf.context_profile_features(market, level, side, at))
                    row.update(gf.weekly_delta_features(market, level, side))
                rows.append(row)
            for row in rows:
                sink.write(json.dumps(row, default=str) + "\n")
            n_rows += len(rows)
            n_pos += sum(r["label"] for r in rows)
            print(json.dumps({"id": example["id"], "session": day, "candidates": len(rows), "positives": sum(r["label"] for r in rows), "tickets": len(tickets)}), flush=True)
    print(json.dumps({"event": "dataset_complete", "rows": n_rows, "positives": n_pos}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
