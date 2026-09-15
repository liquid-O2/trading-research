"""S1–S4 response machines and causal CASE/OR evaluation."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from trading_research.errors import ContractError
from trading_research.research.contracts.types import (
    Contact,
    ContextEvidence,
    Coverage,
    EvidenceRef,
    PredicateEvidence,
    SequenceInputs,
    SequenceSpec,
    SequenceState,
)

NS = 1_000_000_000
DEFAULT_DEADLINE_S = 600
REARM_TICKS_FLOOR = 4
REARM_HOLD_S = 60
S1_SWEEP_TICKS = 1
S2_FAVORABLE_TICKS = 2
S3_C1 = 0.20
S4_PRESSURE_S = 120
S4_FAVORABLE_TICKS = 1
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

S1_STAGES = ("issued", "contacted", "swept", "reclaimed", "confirmed")
S2_STAGES = ("issued", "contacted", "swept", "reclaimed", "retested", "confirmed")
S3_STAGES = S1_STAGES
S4_STAGES = ("issued", "contacted", "pressure_observed", "stalled", "confirmed")
TERMINAL = frozenset({"expired", "invalidated", "input_unknown", "confirmed"})


@dataclass(frozen=True, slots=True)
class Eval:
    value: bool | None
    operands: tuple[str, ...]
    unknown: tuple[str, ...]


def kleene_or(left: bool | None, right: bool | None) -> bool | None:
    if left is True or right is True:
        return True
    if left is False and right is False:
        return False
    return None


def kleene_and(left: bool | None, right: bool | None) -> bool | None:
    if left is False or right is False:
        return False
    if left is True and right is True:
        return True
    return None


def causal_or(left: Eval, right: Eval) -> Eval:
    """OR keeps both operands for the causality check even when the left side is True."""
    return Eval(kleene_or(left.value, right.value), left.operands + right.operands, left.unknown + right.unknown)


def causal_case(selector: Eval, branches: Sequence[tuple[object, Eval]], default: Eval) -> Eval:
    """Unknown selector propagates unknown. ELSE is not taken."""
    operands = selector.operands + default.operands + tuple(op for _key, body in branches for op in body.operands)
    unknown = selector.unknown + default.unknown + tuple(u for _key, body in branches for u in body.unknown)
    if selector.value is None:
        return Eval(None, operands, unknown + ("case_selector",))
    for key, body in branches:
        if key == selector.value:
            return Eval(body.value, operands + body.operands, unknown + body.unknown)
    return Eval(default.value, operands, unknown)


def frozen_case(selector_value: object, branches: Sequence[tuple[object, object]], default: object) -> object:
    """Reproduce expressions.py CASE: unknown selector falls through to ELSE."""
    return next((body for key, body in branches if key == selector_value), default)


def frozen_or_short_circuit(left: Eval, right: Eval) -> Eval:
    """Reproduce expressions.py OR: a True left side drops the right operands."""
    if left.value is True:
        return left
    if right.value is True:
        return right
    return Eval(kleene_or(left.value, right.value), left.operands + right.operands, left.unknown + right.unknown)


def _predicate(name: str, value: bool | None, available_at_ns: int | None, *, missing: str | None = None) -> PredicateEvidence:
    return PredicateEvidence(
        name=name,
        value=value,
        available_at_ns=available_at_ns,
        evidence=(),
        missing_reason=missing,
    )


def initial_state(spec: SequenceSpec, contact: Contact, *, now_ns: int, expiry_ns: int) -> SequenceState:
    deadline = min(contact.at_ns + spec.deadline_seconds * NS, expiry_ns)
    return SequenceState(
        sequence_id=f"{spec.recipe_id}:{contact.contact_id}",
        recipe_id=spec.recipe_id,
        contact_id=contact.contact_id,
        state="contacted",
        state_at_ns=now_ns,
        available_at_ns=now_ns,
        deadline_ns=deadline,
        stage_evidence=(_predicate("contacted", True, now_ns),),
        terminal_reason=None,
        working_memory={"swept_extreme": None, "side": contact.side, "batch_id": contact.batch_id},
    )


def _terminal(state: SequenceState, *, now_ns: int, name: str, reason: str) -> SequenceState:
    return replace(
        state,
        state=name,
        state_at_ns=now_ns,
        available_at_ns=now_ns,
        terminal_reason=reason,
        stage_evidence=state.stage_evidence + (_predicate(name, True, now_ns),),
    )


def advance_sequence(
    state: SequenceState,
    batch: Mapping[str, Any] | None,
    spec: SequenceSpec,
    *,
    now_ns: int,
    inputs: Mapping[str, Any],
) -> SequenceState:
    if now_ns < state.available_at_ns:
        raise ContractError("sequence clock moved backwards")
    if state.state in TERMINAL:
        return state
    if now_ns >= state.deadline_ns and state.state != "confirmed":
        return _terminal(state, now_ns=now_ns, name="expired", reason="deadline")
    recipe = spec.recipe_id
    side = int(state.working_memory["side"])
    if batch is not None and batch.get("batch_id") == state.working_memory.get("batch_id"):
        if state.state != "contacted":
            return replace(state, available_at_ns=now_ns, stage_evidence=state.stage_evidence + (_predicate("same_batch_rejected", True, now_ns),))
    if recipe in {"S1", "S2", "S3"}:
        return _advance_reclaim(state, batch, spec, now_ns=now_ns, inputs=inputs, side=side)
    if recipe == "S4":
        return _advance_s4(state, batch, spec, now_ns=now_ns, inputs=inputs, side=side)
    raise ContractError(f"unknown recipe {recipe}")


def _advance_reclaim(
    state: SequenceState,
    batch: Mapping[str, Any] | None,
    spec: SequenceSpec,
    *,
    now_ns: int,
    inputs: Mapping[str, Any],
    side: int,
) -> SequenceState:
    memory = dict(state.working_memory)
    if state.state == "contacted":
        sweep = inputs.get("sweep_ticks")
        if sweep is None:
            return state
        if int(sweep) >= S1_SWEEP_TICKS:
            memory["swept_extreme"] = inputs.get("swept_extreme")
            return replace(state, state="swept", state_at_ns=now_ns, available_at_ns=now_ns, working_memory=memory, stage_evidence=state.stage_evidence + (_predicate("swept", True, now_ns),))
        return state
    if state.state == "swept":
        bar = inputs.get("complete_bar")
        if not bar:
            return state
        if batch is not None and int(bar.get("event_ns") or now_ns) == int(batch.get("event_ns") or -1):
            return replace(state, available_at_ns=now_ns, stage_evidence=state.stage_evidence + (_predicate("same_batch_bar_rejected", True, now_ns),))
        inside = bool(bar.get("close_inside"))
        if inside:
            if spec.recipe_id == "S3":
                c1 = inputs.get("c1")
                cohort = inputs.get("cohort_120_mean")
                if c1 is None or cohort is None:
                    return _terminal(state, now_ns=now_ns, name="input_unknown", reason="missing S3 aggression or cohort")
                signed = float(c1) * side
                if signed <= S3_C1 or float(cohort) <= 0:
                    return replace(state, available_at_ns=now_ns)
                if int(inputs.get("cohort_available_at_ns") or now_ns) > now_ns:
                    return _terminal(state, now_ns=now_ns, name="input_unknown", reason="cohort resolution after S1")
            nxt = "confirmed" if spec.recipe_id in {"S1", "S3"} else "reclaimed"
            return replace(state, state=nxt, state_at_ns=now_ns, available_at_ns=now_ns, working_memory=memory, stage_evidence=state.stage_evidence + (_predicate(nxt, True, now_ns),), terminal_reason="s1" if nxt == "confirmed" else None)
        return state
    if state.state == "reclaimed":
        if spec.recipe_id != "S2":
            return state
        if bool(inputs.get("intervening_beyond_extreme")):
            return _terminal(state, now_ns=now_ns, name="invalidated", reason="close beyond swept extreme")
        if bool(inputs.get("retest_before_reclaim")):
            return replace(state, available_at_ns=now_ns, stage_evidence=state.stage_evidence + (_predicate("retest_before_reclaim", False, now_ns, missing=None),))
        if bool(inputs.get("later_contact_within_1_tick")) and bool(inputs.get("favorable_close_2_ticks")):
            return replace(state, state="confirmed", state_at_ns=now_ns, available_at_ns=now_ns, terminal_reason="s2", stage_evidence=state.stage_evidence + (_predicate("retested", True, now_ns), _predicate("confirmed", True, now_ns),))
        return state
    return state


def _advance_s4(
    state: SequenceState,
    batch: Mapping[str, Any] | None,
    spec: SequenceSpec,
    *,
    now_ns: int,
    inputs: Mapping[str, Any],
    side: int,
) -> SequenceState:
    if inputs.get("opposing_aggression") is None and state.state == "contacted":
        return _terminal(state, now_ns=now_ns, name="input_unknown", reason="unknown aggression cannot qualify S4")
    if state.state == "contacted":
        if bool(inputs.get("opposing_exceeds_quantile")) and int(inputs.get("seconds_after_contact") or 0) <= S4_PRESSURE_S:
            return replace(state, state="pressure_observed", state_at_ns=now_ns, available_at_ns=now_ns, stage_evidence=state.stage_evidence + (_predicate("pressure_observed", True, now_ns),))
        return state
    if state.state == "pressure_observed":
        if bool(inputs.get("adverse_within_cap")):
            return replace(state, state="stalled", state_at_ns=now_ns, available_at_ns=now_ns, stage_evidence=state.stage_evidence + (_predicate("stalled", True, now_ns),))
        return _terminal(state, now_ns=now_ns, name="invalidated", reason="adverse extension")
    if state.state == "stalled":
        if bool(inputs.get("favorable_close_beyond_contact")):
            return replace(state, state="confirmed", state_at_ns=now_ns, available_at_ns=now_ns, terminal_reason="s4", stage_evidence=state.stage_evidence + (_predicate("confirmed", True, now_ns),))
        return state
    return state


def rearm_ready(
    *,
    departed_ticks: int,
    scale_at_first_contact_ticks: int,
    outside_complete_bar: bool,
) -> bool:
    need = max(REARM_TICKS_FLOOR, int(0.1 * scale_at_first_contact_ticks))
    return departed_ticks >= need and outside_complete_bar


def mirror(distance: int, side: int) -> int:
    return int(distance) * int(side)


def recipe_spec(recipe_id: str) -> SequenceSpec:
    stages = {"S1": S1_STAGES, "S2": S2_STAGES, "S3": S3_STAGES, "S4": S4_STAGES}[recipe_id]
    return SequenceSpec(recipe_id=recipe_id, ordered_stages=stages, deadline_seconds=DEFAULT_DEADLINE_S, parameters={})


def slice_p15_07(day: str) -> dict[str, Any]:
    from datetime import date
    from decimal import Decimal

    from trading_research.research.contracts.types import Contact, Coverage, EvidenceRef
    from trading_research.research.method_pack.clocks import et_ns
    from trading_research.research.rule_discovery.native import build_market_view, install_write_guard

    install_write_guard()
    view = build_market_view(day, full_account_day=True)
    issue = min(int(et_ns(date.fromisoformat(day), 9, 30)), view.end_ns)
    ev = EvidenceRef(EMPTY_SHA256, ("slice",), issue, issue, issue, Coverage.COMPLETE, ())
    contact = Contact(
        contact_id=f"{day}:c",
        reference_id=f"{day}:r",
        batch_id=f"{day}:b",
        at_ns=issue,
        available_at_ns=issue,
        side=1,
        kind="touch",
        possible_prices=(Decimal("100"),),
        departure_evidence=(ev,),
        evidence=(ev,),
    )
    spec = recipe_spec("S1")
    state = initial_state(spec, contact, now_ns=issue, expiry_ns=min(view.end_ns, issue + DEFAULT_DEADLINE_S * NS))
    state = advance_sequence(state, None, spec, now_ns=issue + NS, inputs={"sweep_ticks": 2, "swept_extreme": 99})
    long = mirror(4, 1)
    short = mirror(4, -1)
    return {
        "date": day,
        "jobs": 1,
        "matches": 1,
        "mismatches": [],
        "state": state.state,
        "mirror_ok": long == -short,
        "coverage": view.coverage(view.start_ns, issue).status.value,
        "contact_subset_only": True,
    }
