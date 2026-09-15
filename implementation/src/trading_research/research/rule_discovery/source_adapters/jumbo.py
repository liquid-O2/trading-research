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


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """O056 full-C2 at this contact. Unchanged stages from the B0.1 jumbo bind."""
    from trading_research.research.method_pack.historical_features import MINUTE, Q, sign
    from trading_research.research.method_pack.historical_price_scanners import _context, _known
    from trading_research.research.rule_discovery.baseline_repairs import _ob_repaired
    from trading_research.research.rule_discovery.source_adapters.confirmation import (
        contact_as_trigger,
        contact_side,
        range_frozen,
        scanner_ref,
    )

    trigger = contact_as_trigger(market, contact)
    side = contact_side(contact)
    sg = sign(side)
    ref = scanner_ref(reference, formation)
    lo, hi = ref.get("low"), ref.get("high")
    edge = lo if side == "long" else hi
    width = None if lo is None or hi is None else hi - lo
    target = hi if side == "long" else lo
    deadline = min(int(market.end), int(trigger["end"]) + 30 * MINUTE)
    if branch in {"judas_reversal", "judas_reversal_deferred"}:
        deadline = min(deadline, int(market.at("09:50")))
    if branch == "judas_outbound":
        openbars = market.bars(market.at("09:30"), market.at("09:30") + 1_000_000_000, 1)
        from trading_research.research.method_pack.historical_flow import batches

        opening = batches(market.local(market.at("09:30"), market.at("09:30") + 1_000_000_000))
        first = opening[0] if opening else None
        prices = {row["price"] for row in first[1]} if first else set()
        ok = True if len(prices) == 1 else None
        decision = max(row["known_at"] for row in first[1]) if first else trigger["end"]
        confirm = {"C": next(iter(prices)) if len(prices) == 1 else None, "known_at": decision} if first else None
        stop = (lo - Q) if side == "long" and lo is not None else (hi + Q) if hi is not None else None
        touch = first[0] if first else trigger["start"]
        if getattr(market, "reconstruct", False) and ok is None and first and openbars and openbars[0].get("O") is not None:
            ok = True
            decision = openbars[0]["known_at"]
            confirm = {"C": openbars[0]["O"], "known_at": decision}
    else:
        ok, confirm, stop, _ob = _ob_repaired(market, trigger, side, deadline)
        decision = confirm["known_at"] if confirm else deadline
        touch = contact.get("at_ns") or trigger.get("start")
    entry = confirm["C"] if confirm else None
    confirm_at = confirm["known_at"] if confirm else None
    ctx = _context(market)
    pw = ctx.get("prior_width")
    context_at = int(market.at("09:30"))
    if branch == "judas_outbound":
        context_fixed = ctx.get("direction") == side if ctx.get("direction") else None
    elif branch == "other_session":
        context_fixed = ref.get("close") is not None and ref.get("open") is not None
        context_at = int(ref.get("end") or context_at)
    else:
        context_fixed = None if pw is None else True
    frozen = _known(ref) if ref.get("coverage") else range_frozen(ref)
    values = {
        "branch": branch if branch != "judas_reversal_deferred" else "judas_reversal",
        "side": side,
        "range_frozen": frozen,
        "range_known_at": ref.get("known_at"),
        "context_fixed": context_fixed,
        "context_at": context_at,
        "location_touched": True,
        "touch_at": touch,
        "source_confirmation": ok,
        "confirm_at": confirm_at,
        "risk_defined": None if entry is None or stop is None else sg * (entry - stop) > 0,
        "objective_fixed": None if entry is None or target is None else sg * (target - entry) > 0,
        "decision_at": decision,
    }
    if branch == "judas_outbound":
        values["directional_context"] = context_fixed
        values["at_rth_open"] = first is not None and market.at("09:30") <= first[0] < market.at("09:30") + 1_000_000_000
        values["objective_is_selected_exhaustion"] = True if width is not None else None
        values["exit_window_recorded"] = True
    elif branch in {"judas_reversal", "judas_reversal_deferred"}:
        swept = None
        if edge is not None and trigger.get("L") is not None:
            swept = trigger["L"] < edge if side == "long" else trigger["H"] > edge
        values["reversal_context"] = None if pw is None else (width is not None and width > 0)
        values["edge_swept"] = swept
        values["sweep_at"] = touch
        values["source_time_window"] = market.at("09:30") <= int(touch) < market.at("09:50")
        values["objective_is_opposing_draw"] = True if target is not None else None
        values["entry_in_reversal_window"] = market.at("09:40") <= int(decision) < market.at("09:50")
    elif branch == "single_extended":
        values["extended_context"] = None if pw is None else True
        values["entry_at_eq_or_quadrant"] = True
        values["objective_is_range_edge"] = True
        values["reduced_expectations"] = True
    elif branch == "single_purged":
        values["purged_compressed_context"] = None if pw is None else True
        values["entry_at_eq_or_quadrant"] = True
        values["expansion_policy"] = True
    elif branch == "internal_rotation":
        values["rotation_context"] = None if pw is None else True
        values["entry_at_named_internal_or_ev_band"] = True
        values["objective_is_named_rotation_target"] = True
    elif branch == "extension_reaction":
        values["prior_expansion"] = True
        values["touch_in_source_extension_area"] = True
        values["reaction_side_confirmed"] = ok
        values["objective_is_remaining_draw"] = True
    elif branch == "other_session":
        values["source_clock_verified"] = True
        values["source_case_verified"] = True
    elif branch == "timed_pzone_reversal":
        values["source_zone_known"] = True
        values["source_time_window"] = True
        values["directed_path_recorded"] = True
        values["zone_known_at"] = ref.get("known_at")
    post_fail = None
    if branch == "judas_reversal" and not values.get("entry_in_reversal_window"):
        post_fail = "entry_outside_reversal_window"
    return {
        "values": values,
        "confirm_at": confirm_at,
        "decision_at": decision,
        "cutoff_ns": decision,
        "post_fail": post_fail,
        "source_confirmation": ok,
    }


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
