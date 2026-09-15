"""P15-14 Member independent-reasons branches."""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from trading_research.research.contracts.types import RuleSpec
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
    register_family_transform,
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


def apply_member_rules(document: Mapping[str, Any], market, branch: str, version: str) -> dict[str, Any]:
    """Reaction-period HVN fails; vacuous all() is unknown; same-parent records are not two reasons."""
    out = dict(document)
    kept = []
    for episode in list(out.get("episodes") or []):
        row = dict(episode)
        values = dict(row.get("values") or {})
        geometry = row.get("geometry") or {}
        reaction = geometry.get("reaction_window") or values.get("reaction_window")
        hvn = geometry.get("hvn_window") or values.get("hvn_window")
        if isinstance(reaction, (list, tuple)) and isinstance(hvn, (list, tuple)) and len(reaction) == 2 and len(hvn) == 2:
            values["hvn_from_reaction_period_fails"] = hvn_from_reaction_period_fails((int(reaction[0]), int(reaction[1])), (int(hvn[0]), int(hvn[1])))
            if values["hvn_from_reaction_period_fails"]:
                values["independent_hvn"] = False
        window_rows = geometry.get("reaction_bars") or values.get("window_rows") or []
        values["vacuous_all"] = vacuous_all(window_rows, lambda item: True)
        parents = list(row.get("parent_ids") or values.get("parent_ids") or geometry.get("parent_ids") or [])
        derivations = row.get("operand_derivations") or {}
        if not parents:
            for item in derivations.values() if isinstance(derivations, dict) else []:
                parents.extend(item.get("parents") or [])
        if parents:
            values["two_independent_reasons"] = two_records_same_parent_are_not_two_reasons([str(p) for p in parents])
        values["member_adapter_rules"] = True
        row["values"] = values
        kept.append(row)
    out["episodes"] = kept
    out["member_adapter_rules"] = True
    out["baseline_version"] = version
    return out


register_family_transform(FAMILY, apply_member_rules)


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-14"
    payload["findings"] = list(FINDINGS)
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["vacuous_all"] = "empty window is unknown, not True"
    payload["population_kind"] = "engineering_slice"
    payload["adapter_rules_applied"] = True
    return payload
