"""P15-15 Keani ordered opening-value branch."""
from __future__ import annotations

from typing import Any

from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    scan_family_date,
)

FAMILY = "KEANI-OPEN-ABOVE-VALUE"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("C4",)


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-15",
        "branches": list(BRANCHES),
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
        "c4": "rejection wick into developing POC or prior-day VAH; developing-VAL remains B0",
    }


def a_period_trade_below_vah_invalidates(low, vah) -> bool:
    if low is None or vah is None:
        return False
    return low < vah


def value_after_break_cannot_satisfy_before(value_known_at: int, break_at: int) -> bool:
    return int(value_known_at) <= int(break_at)


def low_support_inconclusive(n: int, floor: int = 5) -> bool:
    return n < floor


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-15"
    payload["findings"] = list(FINDINGS)
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    return payload
