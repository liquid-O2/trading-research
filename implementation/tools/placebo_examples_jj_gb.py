#!/usr/bin/env python3
"""Fake Jumbo and Green Bird tickets for the placebo control of
``replay_jj_gb.py``: every proper entry of every inside-tape example moved by
a fixed number of minutes on its own day, side, branch and play, and repriced
at the market's one-minute close at that minute. The replay is then run on the
result with ``--examples``; the share of fake tickets it "reproduces" is the
chance rate its real count must beat (see ``replay_placebo.py`` for the Sires
and Saint version).

    placebo_examples_jj_gb.py --shift 40 --out fake.json

A fake ticket stays inside its own part of the account day (evening, overnight
or cash session). Fields that belong to the real ticket only (stop, target,
reference price, owner decisions) are dropped so nothing but the mechanics can
match it.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
MINUTE = 60 * 1_000_000_000
DROP = ("stop", "target", "reference_price", "scored_by_decision", "accepted_by_owner", "author_documented_mistake", "note")


def _module(name: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shift", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    placebo = _module("replay_placebo")
    rs = _module("replay_sires")
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    doc = json.loads(rs.EXAMPLES.read_text())
    markets: dict = {}
    out = []
    kept = skipped = 0
    for ex in doc["examples"]:
        if not ex.get("inside_tape") or not str(ex.get("id", "")).startswith(("JJ", "GB")):
            continue
        new_ex = copy.deepcopy(ex)
        actions = []
        for action in ex.get("actions") or []:
            if not isinstance(action, dict) or not action.get("proper_entry") or not action.get("time_et"):
                continue
            raw_day = str(action.get("date") or ex.get("date"))[:10]
            first = str(action["time_et"]).split("-")[0].split("(")[0].strip()
            day = date.fromisoformat(raw_day)
            if int(first[:2]) >= 18:
                day += timedelta(days=1)
                while day.weekday() >= 5:
                    day += timedelta(days=1)
            key = day.isoformat()
            try:
                if key not in markets:
                    markets[key] = load_source_market(key)
                moved = placebo.shifted_action(rs, markets[key], {**action, "time_et": str(action["time_et"]).split("(")[0].strip()}, args.shift)
            except Exception:
                moved = None
            if moved is None:
                skipped += 1
                continue
            for field in DROP:
                moved.pop(field, None)
            actions.append(moved)
            kept += 1
        if actions:
            # the other fills of the record describe the real trade; a fake ticket has none
            new_ex["actions"] = actions
            out.append(new_ex)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"examples": out}, default=str) + "\n")
    print(json.dumps({"shift": args.shift, "examples": len(out), "fake_tickets": kept, "skipped_out_of_segment": skipped, "out": str(args.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
