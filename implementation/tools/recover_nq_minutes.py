#!/usr/bin/env python3
"""Reconstruct audited missing NQ minute bars from native second bars."""

from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_research.research.method_pack.minute_recovery import gap_requests, recover_minutes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--gap-manifest", type=Path, required=True, help="audit missing-minute JSON or array of {t, instrument_id} with UTC-ms t")
    args = parser.parse_args()
    try:
        requests = gap_requests(json.loads(args.gap_manifest.read_text()))
        result = recover_minutes(args.data_root, args.output_root, requests, gap_manifest=str(args.gap_manifest.resolve()))
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({key: result[key] for key in ("status", "output_dir", "requested_keys", "already_present_keys", "recovered_keys", "unresolved_keys", "artifact", "raw_source_signatures_unchanged")}, sort_keys=True))
    return 0 if not result["unresolved_keys"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
