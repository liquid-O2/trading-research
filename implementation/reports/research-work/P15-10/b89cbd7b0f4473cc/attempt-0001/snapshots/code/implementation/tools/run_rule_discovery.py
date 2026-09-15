#!/usr/bin/env python3
"""Freeze, slice, run, resume and summarize rule-discovery jobs."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "implementation/src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trading_research.research.rule_discovery.runner import (  # noqa: E402
    freeze,
    resume,
    slice_run,
    summarize,
)


def main() -> int:
    parser = ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    common = {"run_root": None, "manifest": None}
    freeze_p = sub.add_parser("freeze")
    freeze_p.add_argument("--run-root", required=True)
    freeze_p.add_argument("--manifest")
    slice_p = sub.add_parser("slice")
    slice_p.add_argument("--run-root", required=True)
    slice_p.add_argument("--manifest", required=True)
    slice_p.add_argument("--dates")
    slice_p.add_argument("--task", required=True)
    slice_p.add_argument("--workers", type=int)
    run_p = sub.add_parser("run")
    run_p.add_argument("--run-root", required=True)
    run_p.add_argument("--manifest", required=True)
    run_p.add_argument("--task")
    run_p.add_argument("--workers", type=int)
    resume_p = sub.add_parser("resume")
    resume_p.add_argument("--run-root", required=True)
    resume_p.add_argument("--manifest", required=True)
    resume_p.add_argument("--task", required=True)
    resume_p.add_argument("--workers", type=int)
    sum_p = sub.add_parser("summarize")
    sum_p.add_argument("--run-root", required=True)
    sum_p.add_argument("--manifest")
    args = parser.parse_args()
    if args.command == "freeze":
        result = freeze(run_root=Path(args.run_root), manifest=Path(args.manifest) if args.manifest else None)
    elif args.command == "slice":
        dates = args.dates.split(",") if args.dates else None
        result = slice_run(
            run_root=Path(args.run_root),
            manifest=Path(args.manifest),
            dates=dates,
            task_id=args.task,
            workers=args.workers,
        )
    elif args.command == "run":
        result = slice_run(
            run_root=Path(args.run_root),
            manifest=Path(args.manifest),
            dates=None,
            task_id=args.task or "P15-02",
            workers=args.workers,
        )
    elif args.command == "resume":
        result = resume(run_root=Path(args.run_root), manifest=Path(args.manifest), task_id=args.task, workers=args.workers)
    else:
        result = summarize(run_root=Path(args.run_root))
    print(json.dumps(result, sort_keys=True, default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
