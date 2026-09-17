#!/usr/bin/env python3
"""Slice/run context-expert jobs for P2-09, P2-10 and P2-03."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "implementation" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trading_research.research.experts.options.slice_runner import (  # noqa: E402
    engineering_dates_document,
    run_p2_03_slice,
    run_p2_09_slice,
    run_p2_10_slice,
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _dates_from_args(args) -> list[str]:
    if args.dates:
        return [item.strip() for item in args.dates.split(",") if item.strip()]
    if args.manifest:
        document = _load_json(Path(args.manifest))
        if "dates" in document:
            return list(document["dates"])
        groups = document.get("input_groups") or []
        dates = []
        for group in groups:
            for value in (group.get("year_slots") or {}).values():
                if value and value not in dates:
                    dates.append(value)
            dst = group.get("dst_slot")
            if dst and dst not in dates:
                dates.append(dst)
        return dates
    eng = engineering_dates_document()
    dates = list(eng.get("classified_dates") or [])
    return dates


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument("command", choices=("freeze", "slice", "run", "resume", "summarize"))
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--dates")
    parser.add_argument("--task", required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    run_root = Path(args.run_root)
    run_root.mkdir(parents=True, exist_ok=True)
    if args.command == "freeze":
        document = engineering_dates_document()
        path = run_root / "ENGINEERING_DATES.json"
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"ok": True, "path": str(path), "n_dates": len(document.get("classified_dates") or [])}))
        return 0
    dates = _dates_from_args(args)
    if args.command in {"run", "resume"}:
        print(json.dumps({"ok": False, "detail": "full run is not registered for this early track; use slice"}))
        return 2
    if args.command == "summarize":
        print(json.dumps({"ok": True, "run_root": str(run_root), "dates": dates}))
        return 0
    if args.task == "P2-09":
        result = run_p2_09_slice(run_root, dates)
    elif args.task == "P2-10":
        result = run_p2_10_slice(run_root, dates)
        result["atlas"] = True
    elif args.task == "P2-03":
        result = run_p2_03_slice(run_root, dates)
    else:
        print(json.dumps({"ok": False, "detail": f"unsupported task {args.task}"}))
        return 2
    print(json.dumps({"ok": True, "task": args.task, "dates": dates, "result": result}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
