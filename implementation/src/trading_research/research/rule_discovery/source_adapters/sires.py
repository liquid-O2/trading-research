"""P15-12 Sires thesis and flow branches."""
from __future__ import annotations

from typing import Any, Mapping

from trading_research.research.contracts.types import RuleSpec
from trading_research.research.rule_discovery.baseline_repairs import _thesis_direction
from trading_research.research.rule_discovery.source_adapters.common import (
    FAMILY_BRANCHES,
    clock_zone_unverified,
    dispatch_scan_variant,
    register_family_transform,
    scan_family_date,
)

FAMILY = "SIRES"
BRANCHES = FAMILY_BRANCHES[FAMILY]
FINDINGS = ("P1", "P6", "C5", "three_tick_replenishment", "ofm_1r_3r")


def family_document() -> dict[str, Any]:
    return {
        "schema_version": "research-family-spec-v1",
        "family": FAMILY,
        "task_id": "P15-12",
        "branches": list(BRANCHES),
        "findings": list(FINDINGS),
        "clock_zone_unverified": True,
        "adapter_rules": {
            "P1": "compare effort with the immediately preceding equal-duration window; empty counts as zero",
            "P6": "dedup key-gamma contacts on reference_lifecycle_id",
            "C5": "thesis direction from larger-balance half, None on the midpoint",
            "replenishment": "three-tick passive replenishment filter",
            "ofm": "1R to 3R objective",
        },
    }


def independent_thesis_direction(micro: dict | None, htf: dict | None) -> int | None:
    """C5 operational rule, labelled as such."""
    return _thesis_direction(micro, htf)


def p1_preceding_equal_window(current_effort, previous_effort) -> dict[str, Any]:
    """P1: compare with the immediately preceding equal-duration window; empty is zero."""
    previous = 0 if previous_effort is None else previous_effort
    current = 0 if current_effort is None else current_effort
    return {"previous": previous, "current": current, "empty_as_zero": True}


def three_tick_replenishment(passive_ticks: int) -> bool:
    return int(passive_ticks) >= 3


def ofm_objective_r(entry: int, stop: int, r_multiple: int) -> int:
    width = abs(int(entry) - int(stop))
    if r_multiple not in {1, 2, 3}:
        raise ValueError("OFM objective is 1R, 2R or 3R")
    return width * int(r_multiple)


def four_stage_order() -> tuple[str, ...]:
    return ("locate", "provoke", "absorb", "continue")


def swapped_middle_rejected(stages: tuple[str, ...]) -> bool:
    return stages != four_stage_order()


def _lifecycle_id(episode: Mapping[str, Any]) -> str:
    values = episode.get("values") or {}
    ref = episode.get("reference") or {}
    if values.get("reference_lifecycle_id"):
        return str(values["reference_lifecycle_id"])
    if ref.get("reference_lifecycle_id"):
        return str(ref["reference_lifecycle_id"])
    ident = ref.get("id") or ref.get("reference_id") or episode.get("candidate_id") or ""
    return str(ident).rsplit(":", 1)[0] if ident else ""


def _passive_ticks(episode: Mapping[str, Any]) -> int:
    values = episode.get("values") or {}
    if values.get("passive_replenishment_ticks") is not None:
        return int(values["passive_replenishment_ticks"])
    geometry = episode.get("geometry") or {}
    flow = geometry.get("local_flow") or []
    ticks = 0
    for chunk in flow:
        ticks += int(chunk.get("passive_adds") or chunk.get("displayed_defense_ticks") or 0)
    return ticks


def apply_sires_rules(document: Mapping[str, Any], market, branch: str, version: str) -> dict[str, Any]:
    """Adapter-level P6 lifecycle dedup, three-tick replenishment, OFM 1R–3R, C5 thesis."""
    out = dict(document)
    seen: set[str] = set()
    kept: list[dict[str, Any]] = []
    ofm = branch in {"ofm_aggressive", "ofm_passive"}
    replenish_branches = ofm | (branch in {"absorption_reward_retest", "dom_rejection"})
    for episode in list(out.get("episodes") or []):
        row = dict(episode)
        values = dict(row.get("values") or {})
        if branch == "kg1_retest":
            key = _lifecycle_id(row)
            values["reference_lifecycle_id"] = key
            values["p6_lifecycle_dedup"] = True
            if key and key in seen:
                continue
            if key:
                seen.add(key)
        if replenish_branches:
            ticks = _passive_ticks(row)
            values["passive_replenishment_ticks"] = ticks
            values["three_tick_replenishment"] = three_tick_replenishment(ticks)
            if values["three_tick_replenishment"] is False and ofm:
                continue
        if ofm:
            geometry = row.get("geometry") or {}
            entry = geometry.get("entry")
            stop = geometry.get("stop")
            if entry is None:
                entry = values.get("entry")
            if stop is None:
                stop = values.get("stop")
            if entry is not None and stop is not None:
                values["ofm_objective_1r"] = ofm_objective_r(int(entry), int(stop), 1)
                values["ofm_objective_2r"] = ofm_objective_r(int(entry), int(stop), 2)
                values["ofm_objective_3r"] = ofm_objective_r(int(entry), int(stop), 3)
        flow = (row.get("geometry") or {}).get("local_flow") or []
        if flow:
            prev_effort = None
            compared = []
            for chunk in flow:
                effort = chunk.get("effort")
                compared.append(p1_preceding_equal_window(effort, prev_effort))
                prev_effort = 0 if effort is None else effort
            values["p1_preceding_windows"] = compared
        values["p1_empty_window_counts_as_zero"] = True
        if branch == "microbalance_break":
            micro = (row.get("geometry") or {}).get("microbalance") or values.get("micro")
            htf = (row.get("geometry") or {}).get("htf_balance") or row.get("reference")
            if isinstance(micro, dict) and isinstance(htf, dict):
                values["thesis_direction"] = independent_thesis_direction(micro, htf)
                values["c5_operational"] = True
        row["values"] = values
        kept.append(row)
    out["episodes"] = kept
    out["sires_adapter_rules"] = True
    out["baseline_version"] = version
    return out


register_family_transform(FAMILY, apply_sires_rules)


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """B0.1 flow-stage confirmation at this contact."""
    from trading_research.research.rule_discovery.baseline_repairs import _flow_episode_repaired
    from trading_research.research.rule_discovery.source_adapters.confirmation import (
        bounds,
        contact_as_trigger,
        contact_side,
        scanner_ref,
    )

    trigger = contact_as_trigger(market, contact)
    side = contact_side(contact)
    ref = scanner_ref(reference, formation)
    lo, hi = bounds(ref)
    if lo is None or hi is None:
        lo, hi = ref.get("low"), ref.get("high")
    band = [lo, hi]
    episode = None
    if lo is not None and hi is not None:
        episode = _flow_episode_repaired(market, branch, ref, trigger, side, band)
    if episode is not None:
        values = dict(episode.get("values") or {})
        confirm_at = values.get("confirm_at") or episode.get("decision_at")
        decision = episode.get("decision_at")
        return {
            "values": values,
            "confirm_at": confirm_at,
            "decision_at": decision,
            "cutoff_ns": decision,
            "source_confirmation": values.get("source_confirmation", True if episode.get("research_verdict") == "pass" else False if episode.get("research_verdict") == "fail" else None),
        }
    decision = trigger.get("known_at") or trigger.get("end")
    touch_at = contact.get("at_ns") or trigger.get("start")
    known = ref.get("known_at")
    gamma_branch = branch in {"ofm_aggressive", "balance_failure_fade"}
    values = {
        "branch": branch,
        "side": side,
        "thesis_alive": None,
        "auction_route_ok": ref.get("complete", True),
        "branch_regime_allowed": None if gamma_branch else True,
        "location_fixed": None if known is None or touch_at is None else int(known) <= int(touch_at),
        "location_touched": True,
        "objective_fixed": None,
        "risk_defined": None,
        "thesis_known_at": known,
        "location_known_at": known,
        "touch_at": touch_at,
        "confirm_at": None,
        "decision_at": decision,
        "source_confirmation": None,
    }
    return {"values": values, "confirm_at": None, "decision_at": decision, "cutoff_ns": decision, "source_confirmation": None}


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-12"
    payload["findings"] = list(FINDINGS)
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["population_kind"] = "engineering_slice"
    payload["adapter_rules_applied"] = True
    return payload
