#!/usr/bin/env python3
"""Backfill identified FRED series and their ALFRED revisions, preserving the raw archive."""

import argparse
from datetime import datetime, timezone
import getpass
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_research.research.method_pack.macro_backfill import DEFAULT_SERIES, acquire


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--reference-start", help="Observation reference period, separate from vintage start")
    parser.add_argument("--reference-end", help="Observation reference period, separate from vintage end")
    parser.add_argument("--series", nargs="+", choices=DEFAULT_SERIES, default=DEFAULT_SERIES)
    args = parser.parse_args()
    key = os.environ.get("FRED_API_KEY") or getpass.getpass("FRED API key (hidden): ")
    try:
        result = acquire(args.data_root, args.output_root, key, start=args.start, end=args.end,
                         reference_start=args.reference_start, reference_end=args.reference_end,
                         series_ids=tuple(args.series), progress=lambda row: print(json.dumps(row, sort_keys=True), flush=True))
    except (OSError, ValueError, RuntimeError) as exc:
        # Do not print exception text; HTTP exceptions can contain authenticated URLs.
        print(json.dumps({"status": "failed", "error_type": type(exc).__name__}), file=sys.stderr)
        return 2
    finally:
        key = None
    print(json.dumps({k: result[k] for k in ("output_dir", "all_series_succeeded", "source_references_unchanged", "http_requests")}), flush=True)
    return 0 if result["all_series_succeeded"] and result["source_references_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
