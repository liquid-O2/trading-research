"""Capture B0/B0.1 dual_scan hashes before B0.2 adapter edits."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from trading_research.research.rule_discovery.source_adapters import keani as _keani  # noqa: F401
from trading_research.research.rule_discovery.source_adapters import member as _member  # noqa: F401
from trading_research.research.rule_discovery.source_adapters import saint as _saint  # noqa: F401
from trading_research.research.rule_discovery.source_adapters.common import dual_scan, load_source_market

DATES = ("2021-01-04", "2022-01-03")
FAMILIES = {
    "SAINT-AMT": ("continuation_retest", "trapped_buyers_retest", "failed_auction_return", "poc_traversal"),
    "MEMBER-TWO-REASONS": ("resistance_short", "planned_return_long"),
    "KEANI-OPEN-ABOVE-VALUE": ("source_long",),
}
OUT = Path(__file__).resolve().parent / "B0_B01_HASHES.json"


def dump(obj) -> str:
    return json.dumps(obj, sort_keys=True, default=str, separators=(",", ":"))


def digest(obj) -> str:
    return hashlib.sha256(dump(obj).encode()).hexdigest()


def main() -> None:
    rows = []
    for day in DATES:
        market = load_source_market(day)
        for family, branches in FAMILIES.items():
            for branch in branches:
                dual = dual_scan(market, family, branch)
                rows.append(
                    {
                        "date": day,
                        "family": family,
                        "branch": branch,
                        "b0_sha256": digest(dual["b0"]),
                        "b01_sha256": digest(dual["b01"]),
                        "b0_episodes": len(dual["b0"].get("episodes") or []),
                        "b01_episodes": len(dual["b01"].get("episodes") or []),
                    }
                )
                print(f"{day} {family} {branch} b0={rows[-1]['b0_sha256'][:12]} b01={rows[-1]['b01_sha256'][:12]} n={rows[-1]['b0_episodes']}/{rows[-1]['b01_episodes']}", flush=True)
    payload = {"schema": "p15-16a-b0-b01-hashes-v1", "when": "before-b02-edits", "rows": rows}
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT}", flush=True)


if __name__ == "__main__":
    main()
