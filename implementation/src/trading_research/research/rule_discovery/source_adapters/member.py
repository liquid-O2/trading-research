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


def _member_prior_reasons(market, side: str) -> dict[str, Any]:
    """Prior-day reaction and disjoint HVN, same recipe as scan_member_repaired."""
    from datetime import date
    from decimal import Decimal as D

    from trading_research.research.method_pack.branch_coverage import setting
    from trading_research.research.method_pack.empirical_market import clock
    from trading_research.research.method_pack.historical_features import Q, pivots

    prior = market.prior("day")
    empty = {"reaction": None, "node": None, "independent": None, "profile": None, "confluence": None}
    if not prior.get("sessions"):
        return empty
    day = prior["sessions"][-1]
    win = day["window"]
    split = clock(date.fromisoformat(day["day"]), setting("auction_selection")["member_prior_split"])
    reactionbars = win.bars(win.start, split, 300)
    qualified = []
    for reaction in pivots(reactionbars):
        after = [row for row in reactionbars if row["start"] >= reaction["at"] and row["known_at"] <= reaction["known_at"]]
        if not after:
            continue
        distance = (
            reaction["price"] - min(row["L"] for row in after)
            if reaction["side"] == "high"
            else max(row["H"] for row in after) - reaction["price"]
        )
        if distance >= Q * setting("reaction")["reaction_ticks"]:
            qualified.append(dict(reaction, reaction_distance=distance))
    wanted = "high" if side == "short" else "low"
    reactions = [row for row in qualified if row["side"] == wanted]
    profile = win.profile(split, win.end)
    levels = {row["price"]: row["total_volume"] for row in profile["rows"]}
    radius = setting("reaction")["hvn_radius_ticks"]
    nodes = [
        price
        for price, volume in levels.items()
        if volume > 0 and all(volume > levels.get(price + Q * i, D(0)) for i in range(-radius, radius + 1) if i)
    ]
    pairs = []
    for reaction in reactions:
        matching = [price for price in nodes if abs(price - reaction["price"]) <= Q * setting("reaction")["confluence_ticks"]]
        if not matching:
            continue
        node = min(matching, key=lambda price: (abs(price - reaction["price"]), price))
        pairs.append((reaction, node))
    if not pairs:
        return {"reaction": None, "node": None, "independent": False, "profile": profile, "confluence": False}
    reaction, node = pairs[-1]
    independent = reaction["known_at"] <= split and profile["formation_start"] >= split
    confluence = abs(node - reaction["price"]) <= Q * setting("reaction")["confluence_ticks"]
    return {"reaction": reaction, "node": node, "independent": independent, "profile": profile, "confluence": confluence}


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """Defense (long) or rejection (short) after the candidate contact."""
    from trading_research.research.method_pack.historical_features import MINUTE, Q, sign
    from trading_research.research.method_pack.historical_flow import flow_stages
    from trading_research.research.rule_discovery.baseline_repairs import flow_absent_repaired, local_observations_repaired
    from trading_research.research.rule_discovery.source_adapters.confirmation import (
        bounds,
        contact_as_trigger,
        contact_side,
        scanner_ref,
    )

    trigger = contact_as_trigger(market, contact)
    side = contact_side(contact)
    sg = sign(side)
    ref = scanner_ref(reference, formation)
    lo, hi = bounds(ref)
    if lo is None or hi is None:
        decision = trigger.get("known_at") or trigger.get("end")
        return {
            "values": {"branch": branch, "side": side, "source_confirmation": None, "decision_at": decision, "location_touched": True},
            "confirm_at": None,
            "decision_at": decision,
            "cutoff_ns": decision,
            "source_confirmation": None,
        }
    from trading_research.research.method_pack.historical_flow import exact_contact

    exact = exact_contact(market, trigger, lo, hi)
    touch_at = exact["at"] if exact else (contact.get("at_ns") or trigger.get("start"))
    obs = local_observations_repaired(market, touch_at, [lo, hi], side)
    stages = flow_stages(obs)
    defense = stages["defense"]
    selected = defense if side == "long" else stages["reward"]
    decision = selected["known_at"] if selected else obs["end"]
    entry = selected.get("entry_px", selected["last"]) if selected else None
    observed = [row for row in obs["chunks"] if row["end"] <= decision]
    high = max((row["high"] for row in observed), default=hi)
    low = min((row["low"] for row in observed), default=lo)
    stop = high + Q if side == "short" else low - Q
    missing = flow_absent_repaired(market, trigger["start"], min(int(market.end), ((int(decision) + MINUTE - 1) // MINUTE) * MINUTE), observed)
    prior = _member_prior_reasons(market, side)
    reaction = prior.get("reaction")
    profile = prior.get("profile")
    reaction_at = None if reaction is None else reaction.get("known_at")
    hvn_at = None if profile is None else profile.get("known_at")
    prior_known = None if reaction is None or touch_at is None else int(reaction_at) < int(touch_at)
    values = {
        "branch": branch,
        "side": side,
        "thesis_predefined": None if ref.get("known_at") is None or touch_at is None else int(ref["known_at"]) < int(touch_at),
        "objective_fixed": None if entry is None else sg * ((entry + sg * abs(entry - stop)) - entry) > 0,
        "risk_defined": None if entry is None else sg * (entry - stop) > 0,
        "prior_reaction_area_known": prior_known,
        "area_known_at": reaction_at if reaction_at is not None else ref.get("known_at"),
        "independent_minor_hvn_known": prior.get("independent"),
        "hvn_known_at": hvn_at,
        "confluence_band_defined": prior.get("confluence"),
        "actual_band_contact": True,
        "touch_at": touch_at,
        "reaction_at": selected["known_at"] if selected else None,
        "confirm_at": selected["known_at"] if selected else None,
        "decision_at": decision,
        "source_confirmation": True if selected else missing,
    }
    if side == "short":
        values["resistance_rejection"] = selected is not None or missing
        values["stop_above_rejection_high"] = stop > high
    else:
        values["planned_return_to_structure"] = prior_known
        values["buyers_absorb_and_hold"] = defense["held"] if defense else missing
        values["stop_behind_long_invalidation"] = stop < low
    return {"values": values, "confirm_at": values["confirm_at"], "decision_at": decision, "cutoff_ns": decision, "source_confirmation": values["source_confirmation"]}


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
