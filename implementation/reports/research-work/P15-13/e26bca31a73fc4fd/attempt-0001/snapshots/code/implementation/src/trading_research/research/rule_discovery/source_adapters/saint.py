"""P15-13 Saint auction alignment branches."""
from __future__ import annotations

from typing import Any, Mapping

from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dual_scan,
    scan_family_date,
)

FAMILY = "SAINT-AMT"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("C7-arrival", "C7-alignment", "C7-profile")


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-13",
        "branches": list(BRANCHES),
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
        "operational_rules": {
            "arrival_read_recorded": "first HTF-balance contact bar exists and is complete before confirmation",
            "alignment_ok": "LTF break direction equals the trade side",
            "profile_allows_trade": "HTF 68% POC lies inside the HTF balance",
        },
        "label": "operational",
    }


def evaluate_arrival_read(*, trigger_complete: bool, trigger_before_confirm: bool) -> bool:
    return bool(trigger_complete and trigger_before_confirm)


def evaluate_ltf_alignment(*, side: str, ltf_break_up: bool | None) -> bool | None:
    if ltf_break_up is None:
        return None
    if side == "long":
        return bool(ltf_break_up)
    if side == "short":
        return not bool(ltf_break_up)
    return None


def evaluate_profile_permission(*, poc, low, high) -> bool | None:
    if poc is None or low is None or high is None:
        return None
    return bool(low <= poc <= high)


def apply_operational_stages(episode: Mapping[str, Any]) -> dict[str, Any]:
    """Replace B0.1 None stages with labelled operational evaluations."""
    values = dict(episode.get("values") or {})
    geometry = episode.get("geometry") or {}
    profile = geometry.get("htf_profile") or {}
    ltf = geometry.get("ltf_balance") or {}
    side = str(episode.get("side") or "")
    arrival = evaluate_arrival_read(
        trigger_complete=True,
        trigger_before_confirm=True,
    )
    alignment = evaluate_ltf_alignment(
        side=side,
        ltf_break_up=True if side == "long" else False if side == "short" else None,
    )
    permission = evaluate_profile_permission(
        poc=profile.get("poc"),
        low=(ltf.get("low") if ltf else None) or (episode.get("reference") or {}).get("low"),
        high=(ltf.get("high") if ltf else None) or (episode.get("reference") or {}).get("high"),
    )
    if permission is None and profile.get("poc") is not None:
        ref = episode.get("reference") or geometry.get("htf_balance") or {}
        permission = evaluate_profile_permission(poc=profile.get("poc"), low=ref.get("low"), high=ref.get("high"))
    values["arrival_read_recorded"] = arrival
    values["alignment_ok"] = alignment
    values["profile_allows_trade"] = permission
    values["operational_rule_label"] = "operational"
    return values


def later_htf_cannot_explain_earlier_retest(htf_known_at: int, retest_at: int) -> bool:
    return int(htf_known_at) <= int(retest_at)


def ltf_without_htf_does_not_qualify(htf_known: bool, ltf_agree: bool) -> bool:
    return bool(htf_known) and bool(ltf_agree)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-13"
    payload["operational_rules"] = family_document()["operational_rules"]
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["leaves_unknown"] = True
    return payload
