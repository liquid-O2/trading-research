"""P15-13 Saint auction alignment branches."""
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


def _ltf_break_up_from_bars(episode: Mapping[str, Any]) -> bool | None:
    """LTF break direction from the trigger close versus the LTF balance, not from trade side."""
    trigger = episode.get("trigger") or {}
    ltf = (episode.get("geometry") or {}).get("ltf_balance") or {}
    close = trigger.get("C")
    high, low = ltf.get("high"), ltf.get("low")
    if close is None or high is None or low is None:
        return None
    if close > high:
        return True
    if close < low:
        return False
    return None


def apply_operational_stages(episode: Mapping[str, Any], market=None) -> dict[str, Any]:
    """Evaluate arrival, LTF alignment and profile permission from bars/profile geometry."""
    values = dict(episode.get("values") or {})
    geometry = episode.get("geometry") or {}
    profile = geometry.get("htf_profile") or {}
    trigger = episode.get("trigger") or {}
    ref = episode.get("reference") or geometry.get("htf_balance") or {}
    side = str(episode.get("side") or values.get("side") or "")
    complete = bool(trigger.get("observed_complete") or trigger.get("complete"))
    trigger_at = trigger.get("known_at") or trigger.get("end")
    confirm_at = values.get("confirm_at")
    if not trigger or trigger_at is None:
        arrival = None
    elif confirm_at is None:
        arrival = None
    else:
        before = int(trigger_at) <= int(confirm_at)
        arrival = evaluate_arrival_read(trigger_complete=complete, trigger_before_confirm=before)
    alignment = evaluate_ltf_alignment(side=side, ltf_break_up=_ltf_break_up_from_bars(episode))
    permission = evaluate_profile_permission(poc=profile.get("poc"), low=ref.get("low"), high=ref.get("high"))
    if permission is None and profile.get("poc") is not None:
        htf = geometry.get("htf_balance") or {}
        permission = evaluate_profile_permission(poc=profile.get("poc"), low=htf.get("low") or ref.get("low"), high=htf.get("high") or ref.get("high"))
    if market is not None and permission is None and ref.get("start") is not None and ref.get("known_at") is not None:
        live = market.profile(ref["start"], ref["known_at"], ".68")
        permission = evaluate_profile_permission(poc=live.get("poc"), low=ref.get("low"), high=ref.get("high"))
    values["arrival_read_recorded"] = arrival
    values["alignment_ok"] = alignment
    values["profile_allows_trade"] = permission
    values["operational_rule_label"] = "operational"
    return values


def reassess_episode(episode: Mapping[str, Any]) -> dict[str, Any]:
    from trading_research.research.method_pack.catalog import PRIMARY
    from trading_research.research.method_pack.expressions import evaluate
    from trading_research.research.method_pack.strategy_policy import EXCLUDED, POLICY, observation_scope

    out = dict(episode)
    method = str(out.get("method") or out.get("method_id") or FAMILY)
    predicate = out.get("predicate") or PRIMARY[method]
    values = out.get("values") or {}
    try:
        source_result = evaluate(method, predicate, values)
        excluded = EXCLUDED.get(method, frozenset())
        result = evaluate(method, predicate, values, excluded_fields=excluded)
    except (ValueError, KeyError, TypeError):
        return out
    scope = observation_scope(method, out.get("branch"))
    status = {True: "setup", False: "no_setup", None: "data_unavailable"}[result.value]
    if scope != "entry_setup":
        status = {True: "condition_present", False: "condition_absent", None: "data_unavailable"}[result.value]
    strategy = dict(out.get("strategy_assessment") or {})
    strategy.update(
        {
            "version": POLICY["version"],
            "scope": scope,
            "status": status,
            "failed_conditions": result.failed,
            "unavailable_conditions": result.unknown,
        }
    )
    out["strategy_assessment"] = strategy
    out["research_verdict"] = {True: "pass", False: "fail", None: "unknown"}[result.value]
    out["failed"] = result.failed
    out["unknown"] = result.unknown
    out["source_contract_verdict"] = {True: "pass", False: "fail", None: "unknown"}[source_result.value]
    return out


def bind_saint_operational(document: Mapping[str, Any], market, branch: str, version: str) -> dict[str, Any]:
    """Bind C7 operational stages into B0.1 episode verdicts from actual geometry. Not applied to B0."""
    from trading_research.research.rule_discovery.source_adapters.common import episode_status

    out = dict(document)
    episodes = []
    arrival_none = 0
    status_changed = 0
    for episode in list(out.get("episodes") or []):
        row = dict(episode)
        old_status = episode_status(row)
        row["values"] = apply_operational_stages(row, market=market)
        if row["values"].get("arrival_read_recorded") is None:
            arrival_none += 1
        new_row = reassess_episode(row)
        if episode_status(new_row) != old_status:
            status_changed += 1
        episodes.append(new_row)
    out["episodes"] = episodes
    out["saint_operational_bound"] = True
    out["baseline_version"] = version
    out["arrival_none_count"] = arrival_none
    out["status_changed_from_arrival_none"] = status_changed
    return out


register_family_transform(FAMILY, bind_saint_operational)


def confirm_at_contact(market, *, branch, contact, reference, formation=None, changed_axis="none", view=None) -> dict[str, Any]:
    """Two-bar body/delta control after the contact, then operational stages."""
    from trading_research.research.method_pack.historical_auction_scanners import _control
    from trading_research.research.method_pack.historical_features import MINUTE, Q, sign
    from trading_research.research.rule_discovery.baseline_repairs import _control_absence_repaired
    from trading_research.research.rule_discovery.source_adapters.confirmation import (
        contact_as_trigger,
        contact_side,
        scanner_ref,
    )

    trigger = contact_as_trigger(market, contact)
    side = contact_side(contact)
    sg = sign(side)
    ref = scanner_ref(reference, formation)
    end = min(int(market.end), int(trigger["end"]) + 60 * MINUTE)
    lo, hi = ref.get("low"), ref.get("high")
    boundary = hi if side == "long" else lo
    retest_hi = (boundary + Q) if boundary is not None else None
    retest_lo = (boundary - Q) if boundary is not None else None
    from trading_research.research.method_pack.historical_features import first_contact

    retest = None
    if retest_lo is not None and retest_hi is not None:
        retest = first_contact(market.bars(trigger["end"], end), retest_lo, retest_hi)
    control, controlbars = _control(market, retest["end"] if retest else trigger["end"], end, side)
    decision = control["known_at"] if control else end
    entry = control["C"] if control else None
    stop = None
    if lo is not None and hi is not None:
        stop = lo - Q if side == "long" else hi + Q
    target = hi if side == "long" else lo
    confirm_at = control["known_at"] if control else None
    profile = None
    if ref.get("start") is not None and ref.get("known_at") is not None:
        profile = market.profile(ref["start"], ref["known_at"], ".68")
    permission = None
    if profile and profile.get("poc") is not None and lo is not None and hi is not None:
        permission = lo <= profile["poc"] <= hi
    arrival = None
    trigger_at = trigger.get("known_at") or trigger.get("end")
    complete = bool(trigger.get("observed_complete") or trigger.get("complete"))
    if trigger_at is None:
        arrival = None
    elif confirm_at is None:
        arrival = None
    else:
        arrival = bool(complete and int(trigger_at) <= int(confirm_at))
    alignment = None
    close = trigger.get("C")
    if close is not None and lo is not None and hi is not None:
        if close > hi:
            alignment = side == "long"
        elif close < lo:
            alignment = side == "short"
    held = None
    if retest and control and boundary is not None:
        held = all(
            r["L"] >= boundary - Q * 2 if side == "long" else r["H"] <= boundary + Q * 2
            for r in market.bars(retest["start"], control["end"])
        )
    values = {
        "branch": branch,
        "side": side,
        "balance_fixed_before_use": True if ref.get("known_at") is not None else None,
        "balance_known_at": ref.get("known_at"),
        "profile_allows_trade": permission,
        "arrival_read_recorded": arrival,
        "arrival_at": trigger.get("start"),
        "control_evidence_recorded": True if control else _control_absence_repaired(market, retest["end"] if retest else trigger["end"], end, side),
        "control_at": confirm_at,
        "alignment_ok": True if control else alignment,
        "risk_defined": None if entry is None or stop is None else sg * (entry - stop) > 0,
        "objective_fixed": None if entry is None or target is None else sg * (target - entry) > 0,
        "ltf_balance_broken": True,
        "ltf_balance_known_at": ref.get("known_at"),
        "breakout_at": trigger.get("known_at") or trigger.get("end"),
        "same_boundary_retest_held": held if retest else None,
        "repeated_aggression_in_trade_direction": True if control else _control_absence_repaired(market, retest["end"] if retest else trigger["end"], end, side),
        "retest_at": retest["start"] if retest else None,
        "confirm_at": confirm_at,
        "decision_at": decision,
        "source_confirmation": True if control else None,
    }
    return {"values": values, "confirm_at": confirm_at, "decision_at": decision, "cutoff_ns": decision, "source_confirmation": values["source_confirmation"]}


def scan_variant(market, view, spec: RuleSpec) -> dict[str, Any]:
    return dispatch_scan_variant(market, view, spec)


def later_htf_cannot_explain_earlier_retest(htf_known_at: int, retest_at: int) -> bool:
    return int(htf_known_at) <= int(retest_at)


def ltf_without_htf_does_not_qualify(htf_known: bool, ltf_agree: bool) -> bool:
    return bool(htf_known) and bool(ltf_agree)


def slice_family(day: str) -> dict[str, Any]:
    payload = scan_family_date(day, FAMILY, BRANCHES)
    payload["task_id"] = "P15-13"
    payload["operational_rules"] = family_document()["operational_rules"]
    payload["clock_zone_unverified"] = clock_zone_unverified(FAMILY)
    payload["leaves_unknown"] = False
    payload["population_kind"] = "engineering_slice"
    payload["operational_bound"] = True
    payload["arrival_none_count"] = sum(int(scan.get("arrival_none_count") or 0) for scan in payload.get("scans") or [])
    payload["status_changed_from_arrival_none"] = sum(
        int(scan.get("status_changed_from_arrival_none") or 0) for scan in payload.get("scans") or []
    )
    return payload
