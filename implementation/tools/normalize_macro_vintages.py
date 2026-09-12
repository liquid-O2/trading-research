#!/usr/bin/env python3
"""Validate a FRED backfill and attach individually verified BLS publication clocks."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from trading_research.research.method_pack.macro_backfill import normalize_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--clock-evidence", type=Path, required=True)
    args = parser.parse_args()
    result = normalize_bundle(args.bundle, args.data_root, args.clock_evidence)
    print(json.dumps({key: result[key] for key in ("output_dir", "all_series_normalized", "clock_records_verified", "clock_records_unresolved")}))
    return 0 if result["all_series_normalized"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
