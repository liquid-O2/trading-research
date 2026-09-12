"""M10's native participation and auction-state object recipes.

The JETBUNDLE source describes a native order/depth event process and a
supplied five-state heuristic.  These recipes keep those observations typed
and source-bound.  They deliberately do not train a classifier or a
transition matrix from the compact fixtures.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.protocol import RecipeResult, add_fixture, register


DAY = date(2026, 1, 15)


def _t(hour: int, minute: int = 0, second: int = 0) -> int:
    return et_ns(DAY, hour, minute, second)


def _r(recipe_id: str, state: str, value: dict, **kwargs) -> RecipeResult:
    return RecipeResult(recipe_id, state, value, **kwargs)


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, float):
        return None
    try:
        result = value if isinstance(value, Decimal) else Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None
    return result if result.is_finite() else None


def _event_time(event: dict) -> int | None:
    value = event.get("event_ns", event.get("t"))
    return value if type(value) is int else None


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


_ACTIONS = {
    "add": "add", "provide": "add", "submit": "add", "A": "add",
    "cancel": "cancel", "withdraw": "cancel", "remove": "cancel", "C": "cancel",
    "execute": "execute", "consume": "execute", "fill": "execute", "E": "execute",
}


@register("O163", ("events",))
def o163(inp: dict) -> RecipeResult:
    """Validate and aggregate native provide/withdraw/consume events.

    A compact snapshot is not treated as a lifecycle.  Every event therefore
    needs its native identity, exchange order, action, side, price, size and
    depth level.  Missing depth coverage is a data hole; malformed or
    impossible lifecycle records are witnessed invalidity.
    """

    raw_events = inp.get("events")
    if not isinstance(raw_events, list) or not raw_events:
        return _r(
            "O163", "hole",
            {"provided": None, "withdrawn": None, "consumed": None,
             "remaining": None, "source_process_complete": None,
             "all_unknown": True},
            hole_ids=["HOLE:O163:log"], base_ok=None, coverage_ok=None,
            known_at=inp.get("known_at"), reason="native lifecycle log is absent",
        )

    errors: list[str] = []
    holes: list[str] = []
    events: list[dict] = []
    required_fields = (
        "event_id", "order_id", "exchange_seq", "instrument_id", "side",
        "price", "size", "depth_level",
    )
    expected_instrument = inp.get("instrument_id")
    seen_event_ids: set[str] = set()
    observed_instrument: str | None = None
    previous_seq: int | None = None
    previous_time: int | None = None
    observed_at: list[int] = []

    for index, event in enumerate(raw_events):
        if not isinstance(event, dict):
            errors.append(f"event_{index}_not_record")
            continue
        missing = [name for name in required_fields if event.get(name) is None]
        if _event_time(event) is None:
            missing.append("event_ns")
        action = _ACTIONS.get(event.get("action", event.get("kind")))
        if action is None:
            missing.append("action")
        if missing:
            holes.extend(f"HOLE:O163:{name}" for name in dict.fromkeys(missing))
            continue

        seq = event["exchange_seq"]
        event_ns = _event_time(event)
        size = _decimal(event["size"])
        price = _decimal(event["price"])
        depth = event["depth_level"]
        if (type(seq) is not int or seq < 0 or type(depth) is not int
                or depth < 1 or depth > 10 or size is None or size <= 0
                or price is None or price <= 0):
            errors.append(f"event_{index}_typed_value")
        if not _nonempty_text(event["event_id"]):
            errors.append(f"event_{index}_event_id")
        elif event["event_id"] in seen_event_ids:
            errors.append("duplicate_event_id")
        else:
            seen_event_ids.add(event["event_id"])
        if not _nonempty_text(event["order_id"]):
            errors.append(f"event_{index}_order_id")
        if not _nonempty_text(event["instrument_id"]):
            errors.append(f"event_{index}_instrument_id")
        if event.get("side") not in {"buy", "sell", "bid", "ask"}:
            errors.append(f"event_{index}_side")
        if expected_instrument is not None and event["instrument_id"] != expected_instrument:
            errors.append("instrument_identity")
        if observed_instrument is None:
            observed_instrument = event["instrument_id"]
        elif event["instrument_id"] != observed_instrument:
            errors.append("mixed_event_instrument")
        if previous_seq is not None and seq <= previous_seq:
            errors.append("exchange_order")
        if previous_time is not None and event_ns < previous_time:
            errors.append("event_time_order")
        previous_seq, previous_time = seq, event_ns

        event_known = event.get("known_at", event_ns)
        if type(event_known) is not int:
            holes.append("HOLE:O163:availability")
        else:
            observed_at.append(event_known)
            if event_known < event_ns:
                errors.append("availability_before_event")
            if inp.get("known_at") is not None and event_known > inp["known_at"]:
                errors.append("availability_after_snapshot")
            if inp.get("use_at") is not None and event_known > inp["use_at"]:
                errors.append("availability_after_use")

        events.append({**event, "action": action, "event_ns": event_ns,
                       "size_decimal": size, "price_decimal": price,
                       "known_at": event_known})

    if errors:
        return _r(
            "O163", "invalid",
            {"provided": None, "withdrawn": None, "consumed": None,
             "remaining": None, "source_process_complete": False,
             "native_event_count": len(events)},
            hole_ids=[f"HOLE:O163:{name}" for name in dict.fromkeys(errors)],
            known_at=inp.get("known_at"), base_ok=False, coverage_ok=True,
            reason="; ".join(dict.fromkeys(errors)),
        )

    # Replay the native lifecycle by order.  A cancel/execute against an
    # unseen or already exhausted order cannot be inferred from a snapshot.
    remaining_by_order: dict[str, Decimal] = {}
    provided = withdrawn = consumed = Decimal(0)
    per_side: dict[str, Decimal] = {"buy": Decimal(0), "sell": Decimal(0)}
    action_counts = {"add": 0, "cancel": 0, "execute": 0}
    for event in events:
        action = event["action"]
        size = event["size_decimal"]
        order_id = event["order_id"]
        side = event["side"]
        action_counts[action] += 1
        if action == "add":
            remaining_by_order[order_id] = remaining_by_order.get(order_id, Decimal(0)) + size
            provided += size
            per_side["buy" if side in {"buy", "bid"} else "sell"] += size
        elif order_id not in remaining_by_order or remaining_by_order[order_id] < size:
            errors.append("lifecycle_quantity")
        elif action == "cancel":
            remaining_by_order[order_id] -= size
            withdrawn += size
        else:
            remaining_by_order[order_id] -= size
            consumed += size

    if errors:
        return _r(
            "O163", "invalid",
            {"provided": provided, "withdrawn": withdrawn, "consumed": consumed,
             "remaining": provided - withdrawn - consumed,
             "source_process_complete": False, "native_event_count": len(events)},
            hole_ids=[f"HOLE:O163:{name}" for name in dict.fromkeys(errors)],
            known_at=inp.get("known_at"), base_ok=False, coverage_ok=True,
            reason="native lifecycle quantity does not reconcile",
        )

    source_symbol = inp.get("source_symbol", inp.get("symbol"))
    depth_coverage = inp.get("depth_coverage", inp.get("depth_levels"))
    depth_complete = inp.get("depth_complete", inp.get("depth_ok"))
    if type(depth_coverage) is not int or depth_coverage < 10:
        holes.append("HOLE:O163:depth_coverage")
    if depth_complete is not True:
        holes.append("HOLE:O163:depth")
    if source_symbol is None:
        holes.append("HOLE:O163:source_instrument")
    elif source_symbol != "AAPL":
        holes.append("HOLE:O163:source_instrument")
    if inp.get("coverage_complete") is False:
        holes.append("HOLE:O163:coverage")

    known_at = inp.get("known_at")
    if known_at is None:
        known_at = max(observed_at) if observed_at else None
    value = {
        "provided": provided,
        "withdrawn": withdrawn,
        "consumed": consumed,
        "remaining": provided - withdrawn - consumed,
        "provide_events": action_counts["add"],
        "withdraw_events": action_counts["cancel"],
        "consume_events": action_counts["execute"],
        "per_side_volumes": per_side,
        "depth_coverage": depth_coverage,
        "native_event_count": len(events),
        "native_event_ids": [event["event_id"] for event in events],
        "source_process_complete": not holes,
        "snapshot_reconstruction": False,
    }
    return _r(
        "O163", "computed" if not holes else "hole", value,
        hole_ids=list(dict.fromkeys(holes)), known_at=known_at,
        base_ok=True, coverage_ok=True if not holes else None,
        reason=None if not holes else "native depth/source coverage is incomplete",
    )


_STATE_CRITERIA = {
    "B": ("two_sided_executions", "recent_revisits", "low_aggression_both_sides"),
    "A": ("high_aggression", "low_response_efficiency",
          "opposite_liquidity_holds_and_refills"),
    "D": ("aggression", "efficient_displacement"),
    "E": ("prior_absorption_or_effort", "replenishment_stops", "level_gives_way"),
    "W": ("cancellations_dominate",),
}


@register("O165", ("state_label", "state_at"))
def o165(inp: dict) -> RecipeResult:
    """Audit one supplied B/A/D/E/W label without building a classifier."""

    label = inp.get("state_label", inp.get("state"))
    state_at = inp.get("state_at")
    if not _nonempty_text(label) or label not in _STATE_CRITERIA:
        return _r("O165", "invalid", {"state_label": label,
                                       "state_evidence_complete": False,
                                       "automatic_state": None,
                                       "missing_criteria": []},
                  base_ok=False, coverage_ok=True,
                  hole_ids=["HOLE:O165:state_label"], reason="unknown state label")
    if type(state_at) is not int:
        return _r("O165", "hole", {"state_label": label,
                                    "state_evidence_complete": None,
                                    "automatic_state": None,
                                    "missing_criteria": ["state_at"]},
                  base_ok=None, coverage_ok=None,
                  hole_ids=["HOLE:O165:state_at"], reason="state observation time is absent")

    criteria = _STATE_CRITERIA[label]
    missing: list[str] = []
    failed: list[str] = []
    errors: list[str] = []
    criterion_times = inp.get("criteria_known_at", {})
    if criterion_times is None:
        criterion_times = {}
    if not isinstance(criterion_times, dict):
        errors.append("criteria_known_at_type")
        criterion_times = {}
    for criterion in criteria:
        value = inp.get(criterion)
        if value is None:
            missing.append(criterion)
        elif type(value) is not bool:
            errors.append(f"{criterion}_type")
        elif value is False:
            failed.append(criterion)
        known = criterion_times.get(criterion, inp.get("known_at"))
        if known is not None and type(known) is not int:
            errors.append(f"{criterion}_known_at_type")
        elif known is not None and known > state_at:
            errors.append(f"{criterion}_future")

    known_at = inp.get("known_at")
    if known_at is not None and type(known_at) is not int:
        errors.append("known_at_type")
    elif known_at is not None and known_at > state_at:
        errors.append("known_at_future")
    elif known_at is None:
        missing.append("known_at")
    observation_end = inp.get("observation_end", inp.get("as_of"))
    if observation_end is not None and type(observation_end) is not int:
        errors.append("observation_end_type")
    elif observation_end is not None and observation_end > state_at:
        errors.append("observation_after_state")
    later = inp.get("later_state_at")
    if later is not None and type(later) is not int:
        errors.append("later_state_at_type")
    elif later is not None and later <= state_at and inp.get("later_used_for_current") is True:
        errors.append("future_state_reused")

    source_symbol = inp.get("source_symbol", inp.get("symbol"))
    depth_levels = inp.get("depth_levels", inp.get("depth_coverage"))
    if source_symbol is None:
        missing.append("source_instrument")
    elif source_symbol != "AAPL":
        missing.append("source_instrument")
    if depth_levels is None:
        missing.append("depth_coverage")
    elif type(depth_levels) is not int or depth_levels < 10:
        missing.append("depth_coverage")
    if inp.get("source_observation_id") is None and inp.get("observation_id") is None:
        missing.append("source_observation")
    if inp.get("evidence_complete") is False:
        missing.append("source_observation")

    if errors:
        return _r("O165", "invalid", {
            "state_label": label, "state_evidence_complete": False,
            "automatic_state": None, "missing_criteria": missing,
            "failed_criteria": failed,
        }, hole_ids=[f"HOLE:O165:{name}" for name in dict.fromkeys(errors)],
            known_at=known_at, base_ok=False, coverage_ok=True,
            reason="; ".join(dict.fromkeys(errors)))
    if missing:
        return _r("O165", "hole", {
            "state_label": label, "state_evidence_complete": None,
            "automatic_state": None, "missing_criteria": missing,
            "failed_criteria": failed,
        }, hole_ids=[f"HOLE:O165:{name}" for name in dict.fromkeys(missing)],
            known_at=known_at, base_ok=True, coverage_ok=None,
            reason="source state observations or criteria are incomplete")

    complete = not failed
    return _r("O165", "supplied", {
        "state_label": label,
        "state_evidence_complete": complete,
        "automatic_state": None,
        "missing_criteria": [],
        "failed_criteria": failed,
        "source_illustration": inp.get("source_symbol", inp.get("symbol")) == "AAPL",
        "unbiased_nq_cohort": False,
    }, known_at=known_at,
        base_ok=True, coverage_ok=True)


_STATES = ("B", "A", "D", "E", "W")


@register("O166", ("counts",))
def o166(inp: dict) -> RecipeResult:
    """Compute one supplied transition row with causal current conditioning."""

    counts = inp.get("counts")
    if not isinstance(counts, dict) or not counts:
        return _r("O166", "hole", {"row_sum": None, "total": None,
                                    "conditioning_causal": None,
                                    "trained_matrix": False},
                  hole_ids=["HOLE:O166:counts"], base_ok=None,
                  coverage_ok=None, reason="transition counts are absent")

    holes: list[str] = []
    errors: list[str] = []
    unknown_states = sorted(set(counts) - set(_STATES))
    missing_states = [state for state in _STATES if state not in counts]
    if unknown_states:
        errors.append("count_state")
    if missing_states:
        holes.extend(f"HOLE:O166:row_{state}" for state in missing_states)
    exact_counts: dict[str, int] = {}
    for state in _STATES:
        if state not in counts:
            continue
        value = counts[state]
        if type(value) is not int or value < 0:
            errors.append(f"count_{state}_type")
        else:
            exact_counts[state] = value

    from_state = inp.get("from_state", inp.get("current_state", inp.get("state")))
    to_state = inp.get("to_state", inp.get("next_state"))
    if from_state is not None and from_state not in _STATES:
        errors.append("from_state")
    if to_state is not None and to_state not in _STATES:
        errors.append("to_state")
    state_at = inp.get("state_at")
    next_state_at = inp.get("next_state_at")
    conditioning_at = inp.get("conditioning_known_at", inp.get("feature_at"))
    for field, value in (("state_at", state_at), ("next_state_at", next_state_at),
                         ("conditioning_known_at", conditioning_at)):
        if value is not None and type(value) is not int:
            errors.append(f"{field}_type")
    known_at = inp.get("known_at")
    if known_at is None:
        holes.append("HOLE:O166:known_at")
    elif type(known_at) is not int:
        errors.append("known_at_type")
    if state_at is not None and next_state_at is not None:
        if next_state_at < state_at:
            errors.append("next_before_current")
        elif next_state_at == state_at:
            holes.append("HOLE:O166:ordering")
    if conditioning_at is not None and state_at is not None and conditioning_at > state_at:
        errors.append("conditioning_after_current")

    total = sum(exact_counts.values())
    row_count = inp.get("row_count", inp.get("supplied_row_count"))
    if row_count is not None:
        if type(row_count) is not int or row_count < 0:
            errors.append("row_count_type")
        elif row_count != total:
            errors.append("row_total_mismatch")
    cohort_id = inp.get("cohort_id", inp.get("cohort"))
    source_symbol = inp.get("source_symbol", inp.get("symbol"))
    if cohort_id is None:
        holes.append("HOLE:O166:cohort")
    elif not _nonempty_text(cohort_id):
        errors.append("cohort_type")
    if source_symbol is None:
        holes.append("HOLE:O166:source_instrument")
    elif source_symbol != "AAPL":
        # The printed 84/12 row belongs to the AAPL source illustration and
        # is not allowed to become an NQ probability claim.
        printed = exact_counts == {"B": 4, "A": 12, "D": 84, "E": 0, "W": 0}
        if printed or inp.get("source_counts_symbol") == "AAPL":
            errors.append("cohort_identity")
    source_counts_symbol = inp.get("source_counts_symbol")
    if source_counts_symbol is not None and source_counts_symbol != source_symbol:
        errors.append("cohort_symbol_mismatch")
    if inp.get("cohort_fixed") is False:
        holes.append("HOLE:O166:cohort")

    probabilities = {state: (None if total == 0 else Decimal(value) / Decimal(total))
                     for state, value in exact_counts.items()}
    row_sum = None if total == 0 or missing_states else sum(probabilities.values(), Decimal(0))
    if errors:
        return _r("O166", "invalid", {
            "from_state": from_state, "to_state": to_state,
            "row_sum": row_sum, "total": total,
            "conditioning_causal": False if "conditioning_after_current" in errors else None,
            "trained_matrix": False,
        }, hole_ids=[f"HOLE:O166:{name}" for name in dict.fromkeys(errors)],
            known_at=known_at, base_ok=False, coverage_ok=True,
            reason="; ".join(dict.fromkeys(errors)))
    if holes:
        return _r("O166", "hole", {
            "from_state": from_state, "to_state": to_state,
            "row_sum": row_sum, "total": total,
            "conditioning_causal": None if "HOLE:O166:ordering" in holes else True,
            "trained_matrix": False,
        }, hole_ids=list(dict.fromkeys(holes)), known_at=known_at,
            base_ok=None if "HOLE:O166:ordering" in holes else True,
            coverage_ok=None, reason="transition row or cohort coverage is incomplete")

    return _r("O166", "computed", {
        "from_state": from_state,
        "to_state": to_state,
        "p_dd": probabilities.get("D"),
        "p_da": probabilities.get("A"),
        "probabilities": probabilities,
        "row_sum": row_sum,
        "total": total,
        "conditioning_causal": True,
        "cohort_id": cohort_id,
        "source_symbol": source_symbol,
        "trained_matrix": False,
        "automatic_transition": None,
        "reported_probability": None,
    }, known_at=known_at, base_ok=True,
        coverage_ok=True)


_EVENTS = [
    {"event_id": "a1", "order_id": "book-1", "exchange_seq": 1,
     "instrument_id": "AAPL-fixture", "event_ns": _t(9, 59, 50),
     "known_at": _t(9, 59, 50), "action": "add", "side": "buy",
     "price": "100", "size": 10, "depth_level": 1},
    {"event_id": "c1", "order_id": "book-1", "exchange_seq": 2,
     "instrument_id": "AAPL-fixture", "event_ns": _t(9, 59, 55),
     "known_at": _t(9, 59, 55), "action": "cancel", "side": "buy",
     "price": "100", "size": 3, "depth_level": 1},
    {"event_id": "e1", "order_id": "book-1", "exchange_seq": 3,
     "instrument_id": "AAPL-fixture", "event_ns": _t(10, 0),
     "known_at": _t(10, 0), "action": "execute", "side": "buy",
     "price": "100", "size": 4, "depth_level": 1},
]


add_fixture({
    "id": "O163-F1", "recipe": "O163",
    "inputs": {"events": _EVENTS, "instrument_id": "AAPL-fixture",
                "source_symbol": "AAPL", "depth_coverage": 10,
                "depth_complete": True, "known_at": _t(10, 0),
                "use_at": _t(10, 1)},
    "expected": {"provided": Decimal("10"), "withdrawn": Decimal("3"),
                 "consumed": Decimal("4"), "remaining": Decimal("3"),
                 "source_process_complete": True},
})

add_fixture({
    "id": "O165-F1", "recipe": "O165",
    "inputs": {"state_label": "A", "state_at": _t(10, 0),
                "known_at": _t(10, 0), "source_symbol": "AAPL",
                "depth_levels": 10, "source_observation_id": "state-A-1000",
                "high_aggression": True, "low_response_efficiency": True,
                "opposite_liquidity_holds_and_refills": True,
                "criteria_known_at": {"high_aggression": _t(10, 0),
                                       "low_response_efficiency": _t(10, 0),
                                       "opposite_liquidity_holds_and_refills": _t(10, 0)}},
    "expected": {"state_label": "A", "state_evidence_complete": True,
                 "automatic_state": None},
})

add_fixture({
    "id": "O165-F1b", "recipe": "O165",
    "inputs": {"state_label": "A", "state_at": _t(10, 0),
                "known_at": _t(10, 0), "source_symbol": "AAPL",
                "depth_levels": 10, "source_observation_id": "state-A-1000",
                "high_aggression": True, "low_response_efficiency": True,
                "opposite_liquidity_holds_and_refills": False},
    "expected": {"state_evidence_complete": False, "automatic_state": None},
})

add_fixture({
    "id": "O166-F1", "recipe": "O166",
    "inputs": {"counts": {"D": 84, "A": 12, "B": 4, "E": 0, "W": 0},
                "from_state": "D", "to_state": "D", "state_at": _t(10, 0),
                "next_state_at": _t(10, 1),
                "conditioning_known_at": _t(9, 59), "cohort_id": "AAPL-20000",
                "source_symbol": "AAPL", "row_count": 100,
                "known_at": _t(10, 1), "use_at": _t(10, 2)},
    "expected": {"p_dd": Decimal("0.84"), "p_da": Decimal("0.12"),
                 "row_sum": Decimal("1"), "trained_matrix": False},
})

add_fixture({
    "id": "O166-F1b", "recipe": "O166",
    "inputs": {"counts": {"D": 84, "A": 12, "B": 4, "E": 0, "W": 0},
                "from_state": "D", "to_state": "D", "state_at": _t(10, 0),
                "next_state_at": _t(10, 2),
                "conditioning_known_at": _t(10, 1), "cohort_id": "AAPL-20000",
                "source_symbol": "AAPL", "row_count": 100,
                "known_at": _t(10, 2), "use_at": _t(10, 2)},
    "expected": {"conditioning_causal": False, "base_ok": False},
})


__all__ = ["o163", "o165", "o166"]
