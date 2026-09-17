"""Merge the rows of a population run that was completed on its failed dates
by a second run (``--dates``): the session lines and detail rows of both,
one session line per date (the later run wins), and a POPULATION.json that
states both parents and the resulting coverage.

    merge_population_rows.py --out merged --run first --run second

Fails if any requested date is still missing or a session line of the same
date differs in its identity fields between the runs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--run", type=Path, action="append", required=True, help="a run directory holding rows.jsonl and POPULATION.json (repeatable, in order)")
    args = parser.parse_args(argv)
    sessions: dict[str, str] = {}
    details: dict[str, list[str]] = {}
    requested: set[str] = set()
    parents = []
    for run in args.run:
        summary = json.loads((run / "POPULATION.json").read_text())
        parents.append({"run": str(run), "n_dates_requested": summary.get("n_dates_requested"), "n_dates_complete": summary.get("n_dates_complete"), "failures": len(summary.get("failures") or [])})
        for f in summary.get("failures") or []:
            requested.add(f["date"])
        with (run / "rows.jsonl").open() as handle:
            for line in handle:
                row = json.loads(line)
                date = row.get("session_date") or row.get("date")
                if date is None:
                    raise SystemExit(f"row without a date in {run}: {line[:120]}")
                if "variants" in row:
                    requested.add(date)
                    if date in sessions:
                        # a re-run of the same date replaces the earlier line and its detail rows
                        details.pop(date, None)
                    sessions[date] = line
                    details.setdefault(date, [])
                else:
                    details.setdefault(date, []).append(line)
    missing = sorted(d for d in requested if d not in sessions)
    if missing:
        raise SystemExit(f"{len(missing)} dates still have no session line: {missing[:5]} ...")
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "rows.jsonl").open("w") as handle:
        for date in sorted(sessions):
            for line in details.get(date, []):
                handle.write(line if line.endswith("\n") else line + "\n")
            line = sessions[date]
            handle.write(line if line.endswith("\n") else line + "\n")
    (args.out / "POPULATION.json").write_text(json.dumps({"schema": "population-merge-v1", "parents": parents, "n_dates_complete": len(sessions), "failures": []}, indent=1) + "\n")
    print(json.dumps({"event": "merged", "sessions": len(sessions), "out": str(args.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
