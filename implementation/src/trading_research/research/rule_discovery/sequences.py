"""S1–S4 response machines and causal CASE/OR evaluation."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

import numpy as np

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


FROZEN_CASE_REF = {
    "path": "implementation/src/trading_research/research/method_pack/expressions.py",
    "start_line": 150,
    "end_line": 153,
    "symbol": "evaluate.walk CASE",
    "code": "selected = next((body for key, body in node[2] if key[1] == selector.value), node[3])",
}
FROZEN_OR_REF = {
    "path": "implementation/src/trading_research/research/method_pack/expressions.py",
    "start_line": 171,
    "end_line": 175,
    "symbol": "evaluate.walk OR",
    "code": "if operator == 'OR' and left.value is True: return left",
}


def observe_frozen_case_unknown_selector() -> dict[str, Any]:
    """Call frozen expressions.evaluate() with CASE selector None. expressions.py is not edited."""
    from unittest.mock import patch

    from trading_research.research.method_pack.expressions import Parser, evaluate

    tree = Parser("CASE selector WHEN 'x' THEN TRUE ELSE FALSE END").parse()
    with patch("trading_research.research.method_pack.expressions.expression_for", return_value=tree):
        frozen = evaluate("JJ-TBR", "confirmation", {"selector": None})
    primitive = causal_case(
        Eval(None, ("selector",), ("selector",)),
        [("x", Eval(True, ("when_x",), ()))],
        Eval(False, ("else",), ()),
    )
    return {
        "frozen_value": frozen.value,
        "frozen_unknown": list(frozen.unknown),
        "frozen_fields": sorted(frozen.fields),
        "primitive_value": primitive.value,
        "primitive_operands": list(primitive.operands),
        "defect": "CASE selector None matches no WHEN key and takes ELSE instead of propagating unknown",
        "frozen_ref": dict(FROZEN_CASE_REF),
    }


def observe_frozen_or_operand_drop() -> dict[str, Any]:
    """Call frozen expressions.evaluate() on OR whose left side is True. expressions.py is not edited."""
    from unittest.mock import patch

    from trading_research.research.method_pack.expressions import Parser, evaluate

    tree = Parser("left_field OR right_field").parse()
    with patch("trading_research.research.method_pack.expressions.expression_for", return_value=tree):
        frozen = evaluate("JJ-TBR", "confirmation", {"left_field": True, "right_field": False})
    primitive = causal_or(Eval(True, ("left_field",), ()), Eval(False, ("right_field",), ()))
    return {
        "frozen_value": frozen.value,
        "frozen_fields": sorted(frozen.fields),
        "frozen_dropped_right": "right_field" not in frozen.fields,
        "primitive_value": primitive.value,
        "primitive_operands": list(primitive.operands),
        "defect": "OR short-circuits on True left and drops the right operands from the causality check",
        "frozen_ref": dict(FROZEN_OR_REF),
    }


def cohort_signed_mean(markout_result: Mapping[str, Any], side: int) -> float | None:
    """S3 120 s gate consumes the volume-weighted M_h from cohorts.markout, not an unweighted trade mean."""
    key = "buy" if int(side) > 0 else "sell"
    mean = markout_result[key]["mean"]
    return None if mean is None else float(mean)


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
                markout_result = inputs.get("cohort_120")
                if cohort is None and markout_result is not None:
                    cohort = cohort_signed_mean(markout_result, side)
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


KERNEL_STATE_NAME = {
    0: "contacted",
    1: "swept",
    2: "reclaimed",
    3: "confirmed",
    4: "expired",
    5: "invalidated",
    6: "input_unknown",
    7: "pressure_observed",
    8: "stalled",
}


def advance_on_bars(
    recipe_id: str,
    high,
    low,
    close,
    *,
    lo: int,
    hi: int,
    side: int,
    contact_i: int,
    deadline_i: int,
    c1_value: float | None = None,
    cohort_mean: float | None = None,
    cohort_after: bool = False,
    opposing=None,
    quantile: int = 0,
    adverse_ticks=None,
    cap_ticks: int = 2,
    contact_extreme: int = 0,
    pressure_last_i: int = 0,
) -> dict[str, Any]:
    """Drive S1–S4 over bar arrays in one @njit pass. No Python per-bar state."""
    from trading_research.research.rule_discovery.kernels import (
        s1_machine_kernel,
        s2_machine_kernel,
        s3_machine_kernel,
        s4_machine_kernel,
    )

    high_a = np.asarray(high, dtype=np.int64)
    low_a = np.asarray(low, dtype=np.int64)
    close_a = np.asarray(close, dtype=np.int64)
    lo_i = np.int64(lo)
    hi_i = np.int64(hi)
    side_i = np.int64(side)
    contact = np.int64(contact_i)
    deadline = np.int64(deadline_i)
    if recipe_id == "S1":
        state, sweep_i, confirm_i = s1_machine_kernel(high_a, low_a, close_a, lo_i, hi_i, side_i, contact, deadline)
        extra = {"sweep_i": int(sweep_i), "confirm_i": int(confirm_i)}
    elif recipe_id == "S2":
        state, sweep_i, reclaim_i, confirm_i = s2_machine_kernel(high_a, low_a, close_a, lo_i, hi_i, side_i, contact, deadline)
        extra = {"sweep_i": int(sweep_i), "reclaim_i": int(reclaim_i), "confirm_i": int(confirm_i)}
    elif recipe_id == "S3":
        c1_ok = 0 if c1_value is None else 1
        cohort_ok = 0 if cohort_mean is None else 1
        state, sweep_i, confirm_i = s3_machine_kernel(
            high_a,
            low_a,
            close_a,
            lo_i,
            hi_i,
            side_i,
            contact,
            deadline,
            0.0 if c1_value is None else float(c1_value),
            np.int64(c1_ok),
            0.0 if cohort_mean is None else float(cohort_mean),
            np.int64(cohort_ok),
            np.int64(1 if cohort_after else 0),
        )
        extra = {"sweep_i": int(sweep_i), "confirm_i": int(confirm_i)}
    elif recipe_id == "S4":
        n = close_a.size
        opp = np.zeros(n, dtype=np.int64) if opposing is None else np.asarray(opposing, dtype=np.int64)
        adv = np.zeros(n, dtype=np.int64) if adverse_ticks is None else np.asarray(adverse_ticks, dtype=np.int64)
        state, event_i = s4_machine_kernel(
            opp,
            np.int64(quantile),
            adv,
            np.int64(cap_ticks),
            close_a,
            np.int64(contact_extreme),
            side_i,
            contact,
            np.int64(pressure_last_i),
            deadline,
        )
        extra = {"event_i": int(event_i)}
    else:
        raise ContractError(f"unknown recipe {recipe_id}")
    return {"recipe_id": recipe_id, "state": KERNEL_STATE_NAME[int(state)], **extra}


def slice_p15_07(day: str) -> dict[str, Any]:
    from trading_research.research.rule_discovery.engine_slice import run_candidate_branch_session

    result = run_candidate_branch_session(day)
    result["mirror_ok"] = mirror(4, 1) == -mirror(4, -1)
    result["state"] = next(iter(result.get("sequence_states", {}).values()), None)
    return result
