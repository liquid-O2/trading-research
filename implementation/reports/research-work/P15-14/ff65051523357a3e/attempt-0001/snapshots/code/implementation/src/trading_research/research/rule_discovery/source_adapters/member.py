"""P15-14 Member independent-reasons branches."""
from __future__ import annotations

from typing import Any, Sequence

from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    scan_family_date,
)

FAMILY = "MEMBER-TWO-REASONS"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("balance_adoption", "vacuous_all")


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-14",
        "branches": list(BRANCHES),
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
    }


def hvn_from_reaction_period_fails(reaction_window: tuple[int, int], hvn_window: tuple[int, int]) -> bool:
    """Using the reaction period to form the purported independent HVN fails."""
    return not (hvn_window[0] >= reaction_window[1])


def two_records_same_parent_are_not_two_reasons(parent_ids: Sequence[str]) -> bool:
    return len(set(parent_ids)) >= 2


def vacuous_all(rows: Sequence[Any], predicate) -> bool | None:
    """Empty collections cannot certify a conjunct. Unknown, not True."""
    if not rows:
        return None
    return all(predicate(row) for row in rows)


def rearm_requires_departure(*, departed: bool, outside_complete_bar: bool) -> bool:
    return bool(departed and outside_complete_bar)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-14"
    payload["findings"] = list(FINDINGS)
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["vacuous_all"] = "empty window is unknown, not True"
    return payload
