#!/usr/bin/env python3
"""The selection study's dataset: one row per executed trade of a population
(the per-entry records of ``run_exits_population.py``, schema v2), with the
trade's own descriptors (branch, play, mode, reference kind, geometry, clock),
the object-layer features of ``build_grading_dataset_v2.augment`` at its
decision time, and its outcome under every exit policy as the labels. The
grading datasets label the author's dated tickets (a few dozen positives);
this one labels every trade with what it earned, over the whole tape, so a
selection feature can be judged on the year folds per family.

    build_selection_dataset.py --records exits/rows.jsonl --population pop/rows.jsonl \
        --out <dir> [--families JJ-TBR,GB-FAIL] [--workers 4] [--dates a,b] [--limit N]

Every feature is computed from data at or before the trade's decision time
(``augment`` builds the developing profile up to ``decision_at``); the labels
are the only forward-looking fields and all carry the ``label_`` prefix.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHORT = {"JJ-TBR": "JJ", "GB-FAIL": "GB"}
MINUTE = 60 * 1_000_000_000


def _module(name: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_inputs(records: Path, population: Path, families: set[str], dates: set[str] | None):
    """{date: [record]} for the wanted families, and {(date, candidate_id, mode): detail row}."""
    per_day: dict[str, list[dict]] = defaultdict(list)
    with records.open() as handle:
        for line in handle:
            if '"kind": "entry"' not in line:
                continue
            row = json.loads(line)
            if row["family"] in families and (dates is None or row["date"] in dates):
                per_day[row["date"]].append(row)
    wanted = {(d, r["entry_id"].split(":", 3)[3], r.get("mode")) for d, rs in per_day.items() for r in rs}
    details: dict = {}
    with population.open() as handle:
        for line in handle:
            if '"candidate_id"' not in line or '"kind": "session"' in line:
                continue
            row = json.loads(line)
            key = (row.get("date"), row.get("candidate_id"), row.get("mode"))
            if key in wanted:
                details[key] = row
    return per_day, details


def rows_one(day: str, records: list[dict], details: dict) -> dict:
    from trading_research.research.rule_discovery.native import install_write_guard
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market

    install_write_guard()
    v2 = _module("build_grading_dataset_v2")
    context = _module("day_context_features")
    started = time.monotonic()
    market = load_source_market(day)
    open_ns = int(market.at("09:30"))
    out = []
    by_family: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        candidate_id = rec["entry_id"].split(":", 3)[3]
        detail = details.get((day, candidate_id, rec.get("mode"))) or {}
        entry, stop = float(rec["entry"]), float(rec["stop"])
        target = None if rec.get("target") is None else float(rec["target"])
        level = detail.get("reference_px")
        row = {
            "family": rec["family"],
            "session": day,
            "entry_id": rec["entry_id"],
            "decision_at": int(rec["decision_at"]),
            "side": rec["side"],
            "branch": rec.get("branch"),
            "play": detail.get("play"),
            "mode": rec.get("mode"),
            "reference_kind": detail.get("reference"),
            "segment": detail.get("segment"),
            "cycle": detail.get("cycle"),
            # the level the trade is taken at; the entry where the population row carries none
            "reference_px": level if level is not None else entry,
            "entry_px": entry,
            "minutes_from_open": round((int(rec["decision_at"]) - open_ns) / MINUTE, 1),
            "stop_points": round(abs(entry - stop), 2),
            "objective_points": None if target is None else round(abs(target - entry), 2),
            "rr": None if target is None or entry == stop else round(abs(target - entry) / abs(entry - stop), 3),
            "entry_minus_level": None if level is None else round((entry - float(level)) * (1 if rec["side"] == "long" else -1), 2),
        }
        for policy, result in (rec.get("policies") or {}).items():
            complete = bool(result.get("complete")) and result.get("net_points") is not None
            row[f"label_net_{policy}"] = float(result["net_points"]) if complete else None
            row[f"label_reason_{policy}"] = result.get("reason") if complete else None
        by_family[rec["family"]].append(row)
    for family, rows in by_family.items():
        rows.sort(key=lambda r: r["decision_at"])
        # the position in the day's executed list is known at the decision (earlier trades only)
        for i, row in enumerate(rows):
            row["nth_trade_of_session"] = i
        out.extend(context.context_rows(SHORT.get(family, family), market, v2.augment(SHORT.get(family, family), market, rows)))
    return {"date": day, "rows": out, "seconds": round(time.monotonic() - started, 1)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--records", type=Path, required=True)
    parser.add_argument("--population", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--families", default="JJ-TBR,GB-FAIL")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--dates", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)
    families = set(args.families.split(","))
    dates = None if not args.dates else set(args.dates.split(","))
    per_day, details = load_inputs(args.records, args.population, families, dates)
    days = sorted(per_day)
    if args.limit:
        days = days[: args.limit]
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    failures = []
    n_rows = n_joined = 0
    done = 0
    with (args.out / "rows.jsonl").open("w") as sink:
        with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {}
            for day in days:
                keys = {(day, r["entry_id"].split(":", 3)[3], r.get("mode")) for r in per_day[day]}
                futures[pool.submit(rows_one, day, per_day[day], {k: details[k] for k in keys if k in details})] = day
            for future in as_completed(futures):
                day = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    failures.append({"date": day, "error": f"{type(exc).__name__}: {exc}"})
                    continue
                done += 1
                for row in result["rows"]:
                    sink.write(json.dumps(row, default=str) + "\n")
                    n_rows += 1
                    n_joined += 1 if row.get("play") is not None or row.get("reference_kind") is not None else 0
                if done % 25 == 0:
                    print(json.dumps({"event": "progress", "done": done, "of": len(days), "rows": n_rows, "elapsed_s": round(time.monotonic() - started, 1)}), flush=True)
    summary = {"schema": "selection-dataset-v1", "sessions": done, "sessions_requested": len(days), "rows": n_rows, "rows_joined_to_population_detail": n_joined, "failures": failures, "wall_seconds": round(time.monotonic() - started, 1)}
    (args.out / "DATASET.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({"event": "dataset_complete", **{k: v for k, v in summary.items() if k != "failures"}, "n_failures": len(failures)}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
