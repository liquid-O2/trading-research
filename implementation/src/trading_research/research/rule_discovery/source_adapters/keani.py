"""P15-15 Keani ordered opening-value branch."""
from __future__ import annotations

from typing import Any, Mapping

from trading_research.research.contracts.types import RuleSpec
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
    register_family_transform,
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


def apply_keani_rules(document: Mapping[str, Any], market, branch: str, version: str) -> dict[str, Any]:
    """C4: A-period trade below VAH invalidates; value after the break cannot satisfy a before-break gate."""
    out = dict(document)
    kept = []
    for episode in list(out.get("episodes") or []):
        row = dict(episode)
        values = dict(row.get("values") or {})
        a_low = values.get("a_low")
        vah = values.get("prior_vah")
        values["a_period_below_vah_invalidates"] = a_period_trade_below_vah_invalidates(a_low, vah)
        if values["a_period_below_vah_invalidates"]:
            values["whole_period_above_vah"] = False
        break_at = values.get("breakout_at")
        value_at = values.get("dev_vah_known_at")
        if break_at is not None and value_at is not None:
            values["value_known_before_break"] = value_after_break_cannot_satisfy_before(value_at, break_at)
            if values["value_known_before_break"] is False:
                values["value_after_break_rejected"] = True
        n = values.get("support_n") or values.get("n") or (row.get("geometry") or {}).get("support_n")
        if n is not None:
            values["low_support_inconclusive"] = low_support_inconclusive(int(n))
        values["c4_rejection_levels"] = (row.get("geometry") or {}).get("rejection_level")
        values["keani_adapter_rules"] = True
        row["values"] = values
        kept.append(row)
    out["episodes"] = kept
    out["keani_adapter_rules"] = True
    out["baseline_version"] = version
    return out


register_family_transform(FAMILY, apply_keani_rules)


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-15"
    payload["findings"] = list(FINDINGS)
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["population_kind"] = "engineering_slice"
    payload["adapter_rules_applied"] = True
    return payload
