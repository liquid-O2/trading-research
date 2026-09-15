"""P15-09 Jumbo range branches."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Mapping

from trading_research.research.contracts.types import RuleSpec
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
    dual_scan,
    enumerate_own_population,
    quadrant_locations,
    scan_family_date,
)

FAMILY = "JJ-TBR"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("C1", "C2", "C7", "A2-TBR-PROJ", "judas_strict", "judas_deferred", "outbound_exit", "single_purged_add")
LITERAL_OPERANDS = {
    "exit_window_recorded": "by_construction",
    "source_clock_verified": "by_construction",
    "source_case_verified": "by_construction",
    "location_touched": "by_construction",
    "reduced_expectations": "by_construction",
    "expansion_policy": "by_construction",
    "source_zone_known": "by_construction",
}


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-09",
        "branches": list(BRANCHES),
        "b0_1_variants": ["judas_reversal", "judas_reversal_deferred"],
        "source_additions": ["quadrant_entry", "outbound_exit_09:40", "single_purged_add_09:40-09:50"],
        "findings": list(FINDINGS),
        "literal_operands": LITERAL_OPERANDS,
        "clock_zone_unverified": True,
        "pzone_recipe": "unchanged",
    }


def outbound_expiry_ns(market, day_open_ns: int | None = None) -> int:
    """Unchanged outbound respects the 09:40 expiry."""
    return int(market.at("09:40"))


def one_source_opening(episode: Mapping[str, Any]) -> bool:
    values = episode.get("values") or {}
    return bool(values.get("at_rth_open") is True or values.get("at_rth_open") is False)


def quadrant_population(low: Decimal, high: Decimal, side: str, baseline_eq_only: bool) -> dict[str, Any]:
    loc = quadrant_locations(low, high, side)
    baseline = {f"{side}:eq"}
    candidate = {f"{side}:eq", f"{side}:q1", f"{side}:q3"}
    return {
        "locations": {key: str(value) for key, value in loc.items()},
        "baseline_ids": sorted(baseline),
        "candidate_ids": sorted(candidate),
        "enumeration": enumerate_own_population(baseline_ids=baseline, candidate_ids=candidate, geometry_changed=True),
        "mirrored": quadrant_locations(low, high, "short" if side == "long" else "long"),
        "source": "A2-TBR-PROJ EQ/quadrant entries",
    }


def _empty_hook(market, spec: RuleSpec, result: dict[str, Any]) -> dict[str, Any]:
    branch = spec.source_branch or "judas_reversal"
    if branch == "judas_outbound":
        result["outbound_expiry_ns"] = outbound_expiry_ns(market)
        episodes = result["b0"].get("episodes") or []
        result["one_source_opening"] = None if not episodes else all(one_source_opening(ep) for ep in episodes)
    if branch == "judas_reversal":
        deferred = dual_scan(market, FAMILY, "judas_reversal_deferred")
        result["deferred_variant"] = deferred["populations"]
        result["judas_labels"] = {"strict": "judas_reversal", "deferred": "judas_reversal_deferred"}
    result["literal_operands"] = LITERAL_OPERANDS
    result["clock_zone_unverified"] = clock_zone_unverified(FAMILY, branch)
    return result


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec, empty_hook=_empty_hook)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-09"
    payload["findings"] = list(FINDINGS)
    payload["literal_operands"] = LITERAL_OPERANDS
    payload["b0_1_judas"] = {"strict": "judas_reversal", "deferred": "judas_reversal_deferred"}
    payload["population_kind"] = "engineering_slice"
    return payload
