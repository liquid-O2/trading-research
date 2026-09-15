"""Rerun identity, file, and pytest checks for P15-16A saint track."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from trading_research.research.rule_discovery.census_reader import sha256_file
from trading_research.research.rule_discovery.source_adapters import keani as _keani  # noqa: F401
from trading_research.research.rule_discovery.source_adapters import member as _member  # noqa: F401
from trading_research.research.rule_discovery.source_adapters import saint as _saint  # noqa: F401
from trading_research.research.rule_discovery.source_adapters.common import dual_scan, load_source_market

TRACK = Path(__file__).resolve().parent
REQUIRED = (
    "FUNNEL_SAINT-AMT.json",
    "FUNNEL_MEMBER-TWO-REASONS.json",
    "FUNNEL_KEANI-OPEN-ABOVE-VALUE.json",
    "REPLAY_SAINT.json",
    "REPLAY_MEMBER.json",
    "STATISTICS_SAINT.json",
    "RULES_SAINT-AMT.json",
    "RULES_MEMBER-TWO-REASONS.json",
    "RULES_KEANI.json",
    "MERGE_NOTES.md",
    "B0_B01_HASHES.json",
    "B0_B01_GZ_HASHES.json",
)


def dump(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=str, separators=(",", ":"))


def digest(obj) -> str:
    return hashlib.sha256(dump(obj).encode()).hexdigest()


def main() -> int:
    missing = [name for name in REQUIRED if not (TRACK / name).is_file()]
    print("missing", missing)
    hashes = json.loads((TRACK / "B0_B01_HASHES.json").read_text())
    mismatches = []
    market_by_day = {}
    for row in hashes["rows"]:
        day = row["date"]
        if day not in market_by_day:
            market_by_day[day] = load_source_market(day)
        dual = dual_scan(market_by_day[day], row["family"], row["branch"])
        b0 = digest(dual["b0"])
        b01 = digest(dual["b01"])
        if b0 != row["b0_sha256"] or b01 != row["b01_sha256"]:
            mismatches.append({**row, "b0_now": b0, "b01_now": b01})
            print("MISMATCH", row["date"], row["family"], row["branch"])
        else:
            print("ok dual", row["date"], row["family"], row["branch"])
    gz = json.loads((TRACK / "B0_B01_GZ_HASHES.json").read_text())
    for row in gz["rows"]:
        b0 = sha256_file(Path(row["b0_gz"]))
        b01 = sha256_file(Path(row["b01_gz"]))
        if b0 != row["b0_gz_sha256"] or b01 != row["b01_gz_sha256"]:
            mismatches.append({**row, "b0_now": b0, "b01_now": b01})
            print("MISMATCH gz", row["date"], row["family"], row["branch"])
        else:
            print("ok gz", row["date"], row["family"], row["branch"])
    print("mismatch_count", len(mismatches))
    return 1 if missing or mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
