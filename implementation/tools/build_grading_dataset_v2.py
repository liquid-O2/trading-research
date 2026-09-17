#!/usr/bin/env python3
"""Grading dataset v2: the v1 rows (one per admitted opportunity on the dated
Jumbo and Green Bird sessions, label = the ticket) with the shared object
layer's features added (grading_features.py: profiles and nodes, delta,
aggression boxes, memory, location, room to the next major level)."""
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


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v1 = _module("build_grading_dataset")
gf = _module("grading_features")

from trading_research.research.rule_discovery.source_adapters import green_b02 as gb  # noqa: E402
from trading_research.research.rule_discovery.source_adapters import jumbo as jj  # noqa: E402
from trading_research.research.rule_discovery.source_adapters.common import load_source_market  # noqa: E402

MAJOR_JJ = ("d1_high", "d1_low", "onh", "onl", "asia_high", "asia_low", "london_high", "london_low", "prth_hi", "prth_lo", "pwh", "pwl", "box_low", "box_high")
MAJOR_GB = ("prior_day", "prior_week", "asia_box", "london_box", "tdo", "ny_box_09_10")


def majors_for(family: str, market) -> list[tuple[str, Decimal]]:
    if family == "JJ":
        return [(k, px) for k, px in v1.jj_context_levels(market) if any(k.startswith(m) for m in MAJOR_JJ)]
    return [(k, px) for k, px in v1.gb_context_levels(market) if any(k.startswith(m) for m in MAJOR_GB)]


def augment(family: str, market, rows: list[dict]) -> list[dict]:
    session_open = int(market.start)
    prior = gf.prior_day_profile(market)
    majors = majors_for(family, market)
    cache: dict = {}
    out = []
    for row in rows:
        at = int(row.get("decision_at") or 0)
        level = gf._d(row.get("reference_px"))
        if not at or level is None:
            out.append(row)
            continue
        minute = at // gf.MINUTE
        if minute not in cache:
            cache[minute] = gf.developing_profile(market, session_open, at)
        developing = cache[minute]
        features = {}
        features.update(gf.profile_features(level, prior, developing))
        features.update(gf.delta_features(market, at, None))
        features.update(gf.aggression_features(level, at, session_open))
        features.update(gf.memory_location_features(market, level, str(row.get("side")), at, session_open, majors))
        features.update(gf.author_profile_features(market, level, str(row.get("side")), at, prior))
        out.append({**row, **features})
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--only", default=None)
    args = parser.parse_args(argv)
    jj.NY_ROUND_TRIPS = 99; jj.LONDON_ROUND_TRIPS = 99; gb.ROUND_TRIPS_PER_SEGMENT = 99
    examples = json.loads(v1.EXAMPLES.read_text())["examples"]
    wanted = set(args.only.split(",")) if args.only else None
    rows = []
    for ex in examples:
        if not ex.get("inside_tape") or not ex["id"].startswith(("JJ", "GB")):
            continue
        if wanted and ex["id"] not in wanted:
            continue
        family = ex["id"][:2]
        module = jj if family == "JJ" else gb
        entries = module.proper_entries(ex)
        if not entries:
            continue
        day = v1.session_day(ex, entries[0]) if family == "GB" else ex["date"]
        market = load_source_market(day)
        if family == "JJ":
            doc = jj.scan_b02(market, {"branch": "all"}); episodes = [e for e in doc["episodes"] if e["research_verdict"] == "pass"]
            read = doc.get("day_read") or {}
            selection = jj.selection_for(market, episodes, primary_play=read.get("primary_play"))
        else:
            episodes = []
            for item in ("GB-FAIL", "GB-VWAP", "GB-SCALP"):
                episodes.extend(e for e in gb.scan_b02(market, {"family": item, "branch": "all"})["episodes"] if e["research_verdict"] == "pass")
            read = gb.session_read(market)
            selection = gb.selection_for(market, episodes)
        day_rows = augment(family, market, v1.rows_for(family, ex, entries, market, episodes, selection, read))
        rows.extend(day_rows)
        print(json.dumps({"id": ex["id"], "candidates": len(day_rows), "positives": sum(r["label"] for r in day_rows), "with_profile": sum(1 for r in day_rows if r.get("prior_day_poc_distance") is not None)}), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "rows.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r, default=str) + "\n")
    print(json.dumps({"event": "dataset_complete", "rows": len(rows), "positives": sum(r["label"] for r in rows), "days": len({r["example_id"] for r in rows})}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
