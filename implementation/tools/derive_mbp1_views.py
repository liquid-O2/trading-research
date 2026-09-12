#!/usr/bin/env python3
"""Export bounded NQ MBP-1 views without writing to the acquired data root."""

from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_research.research.method_pack.adapters import timestamp_ns
from trading_research.research.method_pack.mbp1_views import export_views, TapeError, VIEWS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--start", required=True, help="inclusive UTC/offset ISO timestamp")
    parser.add_argument("--end", required=True, help="exclusive UTC/offset ISO timestamp")
    parser.add_argument("--views", nargs="+", choices=VIEWS, default=list(VIEWS))
    parser.add_argument("--instrument-id", help="optional native contract ID")
    args = parser.parse_args()
    try:
        result = export_views(args.data_root, args.output_root, timestamp_ns(args.start), timestamp_ns(args.end),
                              views=args.views, instrument_id=args.instrument_id)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": result["status"], "output_dir": result["output_dir"],
                      "artifacts": result["artifacts"], "unowned_intervals": result["plan"]["unowned_intervals"],
                      "raw_source_signatures_unchanged": result["raw_source_signatures_unchanged"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
