#!/usr/bin/env python3
"""Verify research task, subphase, phase and lineage receipts."""

from __future__ import annotations

from argparse import ArgumentParser, Namespace
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "implementation/src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from trading_research.research.contracts.receipts import (  # noqa: E402
    FailureCode,
    VerificationResult,
    dumps_result,
    verify_lineage_manifest,
    verify_phase_receipt,
    verify_subphase_receipt,
    verify_task_receipt,
)


class _Parser(ArgumentParser):
    def error(self, message: str) -> None:
        sys.stdout.write(json.dumps([{"code": FailureCode.USAGE, "path": "", "detail": message}], sort_keys=True) + "\n")
        sys.exit(2)


def _build_parser() -> _Parser:
    parser = _Parser(description="Verify research receipts against TASK_GRAPH and file bytes")
    sub = parser.add_subparsers(dest="command", required=True)
    task = sub.add_parser("task", help="verify a TASK_RECEIPT.json")
    task.add_argument("--receipt", required=True)
    task.add_argument("--graph")
    task.add_argument("--receipts-root")
    subphase = sub.add_parser("subphase", help="verify a SUBPHASE_RECEIPT.json")
    subphase.add_argument("--receipt", required=True)
    subphase.add_argument("--graph")
    subphase.add_argument("--receipts-root")
    subphase.add_argument("--gate-review")
    phase = sub.add_parser("phase", help="verify a phase receipt")
    phase.add_argument("--receipt", required=True)
    phase.add_argument("--graph")
    phase.add_argument("--receipts-root")
    phase.add_argument("--gate-review")
    lineage = sub.add_parser("lineage", help="verify a lineage manifest")
    lineage.add_argument("--manifest", required=True)
    return parser


def _path_or_none(value: str | None) -> Path | None:
    return Path(value) if value else None


def dispatch(args: Namespace) -> VerificationResult:
    if args.command == "task":
        return verify_task_receipt(
            Path(args.receipt),
            graph_path=_path_or_none(args.graph),
            receipts_root=_path_or_none(args.receipts_root),
        )
    if args.command == "subphase":
        return verify_subphase_receipt(
            Path(args.receipt),
            graph_path=_path_or_none(args.graph),
            receipts_root=_path_or_none(args.receipts_root),
            gate_review=_path_or_none(getattr(args, "gate_review", None)),
        )
    if args.command == "phase":
        return verify_phase_receipt(
            Path(args.receipt),
            graph_path=_path_or_none(args.graph),
            receipts_root=_path_or_none(getattr(args, "receipts_root", None)),
            gate_review=_path_or_none(getattr(args, "gate_review", None)),
        )
    return verify_lineage_manifest(Path(args.manifest))


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    result = dispatch(args)
    sys.stdout.write(dumps_result(result))
    return 0 if result.ok else 2


if __name__ == "__main__":
    sys.exit(main())
