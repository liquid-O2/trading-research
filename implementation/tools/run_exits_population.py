#!/usr/bin/env python3
"""P15-19 on the rebuilt entries: the fixed-entry exit policies E0-E4 of
``exits.py`` evaluated on every session's B0.3 executed entries (exported by
run_jj_gb_population.py --export-executed).

Per session: the native view is built once (full account day), compacted,
and every executed entry is frozen (side, fill, initial stop, objective, the
source deadline at the session's close, flatten a minute before the account
day ends). ``evaluate_entries_compact`` returns one paired record per entry
with the five policies' results; the session's net points per policy go to
the session line, so evaluate_variants.py can judge E1-E4 against E0 on the
year folds like any other candidate.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from decimal import Decimal
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "implementation/src"))

MINUTE_NS = 60_000_000_000


def load_sessions(rows_path: Path) -> list[dict]:
    out = []
    with rows_path.open() as handle:
        for line in handle:
            if '"kind": "session"' not in line:
                continue
            row = json.loads(line)
            if row.get("executed"):
                out.append(row)
    return out


def exits_one(day: str, executed: list[dict]) -> dict:
    from trading_research.research.rule_discovery import exits
    from trading_research.research.rule_discovery.native import account_day_window, build_market_view

    started = time.monotonic()
    start_ns, end_ns = account_day_window(__import__("datetime").date.fromisoformat(day))
    flatten = int(end_ns) - MINUTE_NS
    frozen = []
    items = []
    for i, item in enumerate(executed):
        if item.get("entry") is None or item.get("stop") is None:
            continue
        try:
            frozen.append(
                exits.FrozenEntry(
                    entry_id=f"{day}:{item['family']}:{i}:{item.get('candidate_id')}",
                    family=item["family"],
                    branch=str(item.get("branch")),
                    side=1 if item["side"] == "long" else -1,
                    fill_price=Decimal(str(item["entry"])),
                    fill_at_ns=int(item["decision_at"]),
                    initial_stop=Decimal(str(item["stop"])),
                    objective=None if item.get("target") is None else Decimal(str(item["target"])),
                    source_deadline_ns=flatten,
                    flatten_at_ns=flatten,
                    account_day=day,
                )
            )
            items.append(item)
        except Exception:
            continue
    if not frozen:
        return {"date": day, "entries": 0, "variants": {}, "seconds": round(time.monotonic() - started, 1)}
    view = build_market_view(day, full_account_day=True)
    tape = exits.compact_from_view(view)
    paired = exits.evaluate_entries_compact(frozen, tape)
    per_policy: dict = defaultdict(lambda: defaultdict(lambda: {"net_points": 0.0, "n_executed": 0, "wins": 0, "losses": 0, "open": 0, "ambiguous": 0, "n_round_trips": 0}))
    records = []
    for entry, item, pair in zip(frozen, items, paired):
        rec = exits.paired_to_json(pair, entry)
        records.append(
            {
                "kind": "entry",
                "date": day,
                "entry_id": entry.entry_id,
                "family": entry.family,
                "branch": entry.branch,
                "play": item.get("play"),
                "mode": item.get("mode"),
                "reference": item.get("reference"),
                "side": item["side"],
                "entry": str(entry.fill_price),
                "decision_at": int(entry.fill_at_ns),
                "stop": str(entry.initial_stop),
                "target": None if entry.objective is None else str(entry.objective),
                "policies": {
                    policy_id: (
                        {"net_points": result.get("net_points"), "reason": result.get("reason"), "exit_at_ns": result.get("exit_at_ns"), "complete": bool(result.get("complete"))}
                        if isinstance(result, dict)
                        else {"net_points": None, "reason": None, "exit_at_ns": None, "complete": False}
                    )
                    for policy_id, result in (rec.get("records") or {}).items()
                },
            }
        )
        for policy_id, result in (rec.get("records") or {}).items():
            agg = per_policy[policy_id][entry.family]
            agg["n_executed"] += 1
            agg["n_round_trips"] += 1
            if not isinstance(result, dict) or not result.get("complete"):
                agg["open"] += 1  # incomplete (no quote) or unsupported (undefined R for E3/E4)
                continue
            points = float(result.get("net_points") or 0)
            agg["net_points"] += points
            if points > 0:
                agg["wins"] += 1
            elif points < 0:
                agg["losses"] += 1
    variants = {policy: {family: {**agg, "net_points": round(agg["net_points"], 2)} for family, agg in fams.items()} for policy, fams in per_policy.items()}
    return {"date": day, "entries": len(frozen), "variants": variants, "records": records, "record_sample": exits.paired_to_json(paired[0], frozen[0]) if paired else None, "seconds": round(time.monotonic() - started, 1)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=Path, required=True, help="rows.jsonl of a population run made with --export-executed")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)
    sessions = load_sessions(args.rows)
    if args.limit:
        sessions = sessions[: args.limit]
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    failures = []
    done = 0
    with (args.out / "rows.jsonl").open("w") as sink:
        with ProcessPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {pool.submit(exits_one, s["date"], s["executed"]): s["date"] for s in sessions}
            for future in as_completed(futures):
                day = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    failures.append({"date": day, "error": f"{type(exc).__name__}: {exc}"})
                    continue
                done += 1
                for record in result.get("records") or []:
                    sink.write(json.dumps(record, default=str) + "\n")
                sink.write(json.dumps({"kind": "session", "date": result["date"], "reads": {}, "variants": result["variants"], "entries": result["entries"]}, default=str) + "\n")
                if done == 1 and result.get("record_sample"):
                    (args.out / "RECORD_SAMPLE.json").write_text(json.dumps(result["record_sample"], indent=1, default=str) + "\n")
                if done % 25 == 0:
                    print(json.dumps({"event": "progress", "done": done, "of": len(sessions), "elapsed_s": round(time.monotonic() - started, 1)}), flush=True)
    summary = {"schema": "exits-on-b03-executed-v2", "sessions": done, "failures": failures, "wall_seconds": round(time.monotonic() - started, 1)}
    (args.out / "EXITS.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({"event": "exits_complete", **summary}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
