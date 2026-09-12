"""Persistent process, risk, order, position, and transition ledgers.

The recipes in this module are registration overrides.  They are intentionally
not decorated with :func:`register`: the method-pack integrator can replace the
older compact implementations atomically with ``REGISTRATION_OVERRIDES``.

Every producer is an audit of observations supplied by a source-case/native
assembler.  None of them places an order, discovers an entry, trains a model,
or turns an unknown source rule into a Boolean pass.
"""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
from functools import wraps
from hashlib import sha256
import json
from typing import Any, Callable

from trading_research.research.method_pack.contracts import OutputField
from trading_research.research.method_pack.logic import dec, kleene_and
from trading_research.research.method_pack.protocol import RecipeResult, guard


STATES = ("B", "A", "D", "E", "W")


LIFECYCLE_SCHEMAS: dict[str, tuple[str, ...]] = {
    "O137": ("model_version", "definition_hash", "frozen_at", "observation_ids", "revision_parent", "changed_fields"),
    "O138": ("state", "first_death_at", "death_reason", "replacement_id", "alive_at_decision", "condition_ledger"),
    "O139": ("structural_stop", "stop_distance_points", "stop_distance_ticks", "stop_side_ok", "risk_known_before_entry", "policy_holes",
             "invalidation_ref", "planned_stop", "planned_stop_side", "planned_stop_method", "planned_stop_known_at", "planned_stop_comparison"),
    "O140": ("unit_risk_money", "position_risk_money", "aggregate_risk_money", "cap_ok", "quantity_policy_ok", "missing_units"),
    "O141": ("selected_objective", "target_distance_points", "objective_preknown", "active_at_selection", "later_outcome", "policy_holes"),
    "O142": ("management_actions", "position_quantity_after", "stop_versions", "target_versions", "action_policy_ok", "initial_risk_unchanged", "exit_reason"),
    "O143": ("protected_price", "price_at", "confirmation_at", "protected_known_at", "side", "trail_allowed_at"),
    "O144": ("parent_exit_at", "new_candidate_id", "same_thesis_band", "fresh_confirmation_at", "full_branch_verdict", "reentry_permission"),
    "O145": ("daily_R_before", "daily_r_before", "policy_limit", "session_finished", "entry_permission", "rule_breach", "ledger_ids"),
    "O146": ("journal_rows", "pre_entry_fields_valid", "eligible_ids_accounted_for", "missing_ids", "breach_records", "review_links", "outcomes_separated_from_inputs"),
    "O147": ("native_first_use_times", "source_object_correspondence", "first_instrument", "iod_reaction_revision", "rfz_target_revision"),
    "O148": ("cohort_hash", "eligible_count", "selected_count", "order_count", "filled_order_count", "unselected_ids", "split_direction", "cohort_causal", "inclusion_rule_fixed", "uniform_schema"),
    "O149": ("supplied_grade", "model_known_before_use", "max_feature_known_at", "feature_causal", "selected_by_supplied_rule", "automatic_grade", "label_uses_only_post_touch_observations"),
    "O150": ("order_state_timeline", "remaining_quantity", "filled_quantity", "position_open", "bracket_versions", "lifecycle_valid", "source_policy_ok", "decision_at", "side", "order_at", "stop_ticks", "target_ticks", "cancel_minutes", "one_position_policy", "order_inside_ticks"),
    "O151": ("first_modeled_fill_at", "modeled_fill_rule", "actual_fill_at", "actual_fill_quantity", "queue_verified", "fill_eligibility"),
    "O152": ("trade_cost_ticks", "stop_slippage_ticks", "currency_cost", "supplied_gross_net_consistency", "account_fees_separate"),
    "O155": ("printed_stage", "planned_risk_units", "planned_reward_units", "cumulative_baseline_units", "next_stage", "activation_holes", "base_risk_fraction", "fixed_baseline_equity", "fixed_baseline_unit", "prior_results", "decision_at", "next_risk_units", "first_trade_closed", "first_trade_result_units", "first_trade_close_at", "second_trade_result_units"),
    "O156": ("scenario_id", "assumptions", "reported_pass_rate", "reported_time_to_pass", "source_causal_status", "missing_path_rules"),
    "O165": ("state_label", "state_evidence_complete", "automatic_state", "missing_criteria", "state_at"),
    "O166": ("from_state", "to_state", "state_at", "next_state_at", "conditioning_causal", "transition_valid", "supplied_row_count", "reported_probability", "conditioning_evidence", "max_conditioning_known_at"),
}

LEGACY_REQUIRED = {
    "O137": ("v1", "v2"), "O138": ("known_at",),
    "O139": ("entry", "stop", "side"), "O140": ("D", "quantity"),
    "O141": ("entry", "target", "selected_at", "decision_at"),
    "O142": ("position", "entry_at"), "O143": ("high", "confirm_at"),
    "O144": ("entry_at",), "O145": ("results_r", "limit_r"),
    "O146": ("eligible", "journal"), "O147": ("objects",),
    "O148": ("eligible", "selected", "orders", "filled"),
    "O149": ("score", "threshold", "features_known_at", "order_at"),
    "O150": ("limit",), "O151": ("limit", "side", "active_at", "trades"),
    "O152": ("r_unit", "target_outcome", "quantity"),
    "O155": ("E0", "B"), "O156": ("currency_per_r",),
    "O165": ("state_label", "state_at"), "O166": ("counts",),
}

RICH_MARKERS = {
    "O137": {"definition", "prior_definition", "model_version"},
    "O138": {"thesis_id", "death_conditions", "declared_at"},
    "O139": {"E", "S", "stop_policy", "controlling_structure_id"},
    "O140": {"stop_distance_points", "account_policy", "source_policy"},
    "O141": {"objective", "objective_id", "entry_id"},
    "O142": {"entry_id", "initial_quantity", "management_actions", "actions"},
    "O143": {"pivot", "break_event", "protected_price"},
    "O144": {"parent_entry_id", "new_candidate_id"},
    "O145": {"source_policy", "policy", "result_records"},
    "O146": {"process_version", "process_config", "journal_rows", "eligible_ids"},
    "O147": {"amt_objects", "events", "revisions"},
    "O148": {"candidates", "order_records", "fill_records", "process_version"},
    "O149": {"features", "model_id", "model_version"},
    "O150": {"order_id", "candidate_id", "position_id", "order_events"},
    "O151": {"order_id", "placed_at", "fill_reports"},
    "O152": {"trade_cost_ticks", "account_fees"},
    "O155": {"prior_results", "validated_process"},
    "O156": {"scenario_id", "source_causal_status", "path_design"},
    "O165": {"criteria", "evidence", "observation_id"},
    "O166": {"current_observation", "next_observation", "cadence"},
}


def _schema(rid: str, **values: Any) -> dict[str, Any]:
    out = {key: None for key in LIFECYCLE_SCHEMAS[rid]}
    out.update(values)
    return out


def _result(rid: str, state: str, value: dict[str, Any], **kwargs: Any) -> RecipeResult:
    complete = _schema(rid)
    complete.update(value)
    return RecipeResult(rid, state, complete, **kwargs)


def _holes(rid: str, names: list[str] | tuple[str, ...]) -> list[str]:
    return list(dict.fromkeys(f"HOLE:{rid}:{name}" for name in names))


def _max_time(*values: Any) -> int | None:
    ints = [value for value in values if type(value) is int]
    return max(ints) if ints else None


def _at(row: dict[str, Any]) -> int | None:
    for key in ("available_at", "known_at", "at", "t", "event_at", "time"):
        if type(row.get(key)) is int:
            return row[key]
    return None


def _event_at(row: dict[str, Any]) -> int | None:
    for key in ("at", "t", "event_at", "time"):
        if type(row.get(key)) is int:
            return row[key]
    return None


def _kind(row: dict[str, Any]) -> str:
    raw = row.get("kind", row.get("action", row.get("type", "")))
    return str(raw).strip().lower().replace("-", "_").replace(" ", "_")


def _qty(row: dict[str, Any], *, filled_only: bool = False) -> Decimal | None:
    keys = ("filled_qty", "filled_quantity", "executed_qty", "executed_quantity")
    if not filled_only:
        keys += ("qty", "quantity", "size", "amount")
    for key in keys:
        if row.get(key) is not None:
            return dec(row[key])
    return None


def _ordered(rows: list[dict[str, Any]], rid: str) -> tuple[list[dict[str, Any]], list[str]]:
    """Order records without silently resolving same-time ambiguity."""
    errors: list[str] = []
    prepared: list[tuple[int, int, dict[str, Any]]] = []
    seen: set[tuple[int, int]] = set()
    times: dict[int, list[dict[str, Any]]] = {}
    for index, source in enumerate(rows):
        row = deepcopy(source)
        at = _event_at(row)
        if at is None:
            errors.append("event_at")
            continue
        times.setdefault(at, []).append(row)
        sequence = row.get("sequence", row.get("event_sequence", row.get("seq")))
        if sequence is None:
            sequence = index
        elif type(sequence) is not int:
            errors.append("event_sequence")
            continue
        if (at, sequence) in seen:
            errors.append("event_order")
        seen.add((at, sequence))
        prepared.append((at, sequence, row))
    for at, same_time in times.items():
        if len(same_time) > 1 and any(
            r.get("sequence", r.get("event_sequence", r.get("seq"))) is None
            for r in same_time
        ):
            errors.append("event_order")
    return [row for _, _, row in sorted(prepared, key=lambda item: (item[0], item[1]))], list(dict.fromkeys(errors))


def _override(rid: str) -> Callable[[Callable[[dict], RecipeResult]], Callable[[dict], RecipeResult]]:
    """Apply shared C08 dependency/identity guards while retaining full schema."""
    def decorate(fn: Callable[[dict], RecipeResult]) -> Callable[[dict], RecipeResult]:
        @wraps(fn)
        def wrapped(inp: dict) -> RecipeResult:
            use_legacy_required = not any(marker in inp for marker in RICH_MARKERS[rid])
            blocked = guard(inp, rid, LEGACY_REQUIRED[rid] if use_legacy_required else ())
            if blocked is not None:
                if blocked.reason in {"dependency available after use", "dependency available after claimed snapshot"}:
                    observed = fn(inp)
                    observed.base_ok = False
                    observed.state = "invalid"
                    observed.hole_ids = list(dict.fromkeys(observed.hole_ids + blocked.hole_ids))
                    observed.reason = blocked.reason
                    return observed
                complete = _schema(rid)
                complete.update(blocked.value)
                blocked.value = complete
                return blocked
            try:
                return fn(inp)
            except (ArithmeticError, TypeError, ValueError) as exc:
                return _result(
                    rid, "invalid", {}, base_ok=False, coverage_ok=None,
                    hole_ids=_holes(rid, ["input_type"]), known_at=inp.get("known_at"),
                    reason=f"invalid lifecycle input: {exc}",
                )
        return wrapped
    return decorate


def _definition_payload(inp: dict, prefix: str) -> dict | None:
    direct = inp.get(prefix)
    if isinstance(direct, dict):
        return deepcopy(direct)
    keys = ("author_id", "process_id", "model_version", "products", "allowed_features",
            "contexts", "regimes", "inclusion_constraints", "risk_constraints",
            "review_block")
    payload = {key: deepcopy(inp.get(key)) for key in keys if inp.get(key) is not None}
    return payload or None


@_override("O137")
def o137(inp: dict) -> RecipeResult:
    current = _definition_payload(inp, "definition") or _definition_payload(inp, "v2")
    prior = _definition_payload(inp, "prior_definition") or _definition_payload(inp, "v1")
    frozen_at = inp.get("frozen_at", current.get("frozen_at") if current else None)
    version = inp.get("model_version", inp.get("version", current.get("version") if current else None))
    missing = [name for name, value in (("definition", current), ("model_version", version),
                                         ("frozen_at", frozen_at)) if value is None]
    observations = deepcopy(inp.get("observation_ids", []))
    observation_rows = inp.get("observations", []) or []
    if observation_rows:
        observations = [row.get("observation_id", row.get("id")) for row in observation_rows]
        if any(value is None for value in observations) or len(set(observations)) != len(observations):
            return _result("O137", "invalid", {"observation_ids": observations},
                           base_ok=False, reason="observation identities are absent or duplicated")
        if any(row.get("model_version") not in {None, version} for row in observation_rows):
            return _result("O137", "invalid", {"observation_ids": observations},
                           base_ok=False, reason="observation was relabeled to another model version")
        if frozen_at is not None and any(_at(row) is not None and _at(row) < frozen_at for row in observation_rows):
            return _result("O137", "invalid", {"observation_ids": observations},
                           base_ok=False, reason="definition frozen after an admitted observation")
    ignored = {"version", "model_version", "frozen_at", "known_at", "revision_at",
               "definition_hash", "observation_ids", "review_block_id"}
    changed: list[str] = []
    if prior is not None and current is not None:
        changed = sorted(key for key in set(prior) | set(current)
                         if key not in ignored and prior.get(key) != current.get(key))
    revision_parent = inp.get("revision_parent")
    review_id = inp.get("review_block_id")
    revision_at = inp.get("revision_at", frozen_at)
    comparison_at = inp.get("comparison_at", inp.get("sample_end_at"))
    revision_causal = None if revision_at is None or comparison_at is None else comparison_at < revision_at
    one_variable = None if prior is None else len(changed) == 1
    errors = []
    if prior is not None and inp.get("one_variable_review", True) and not one_variable:
        errors.append("one-variable revision changed zero or multiple strategy fields")
    if revision_parent is not None and review_id is not None and revision_parent != review_id:
        errors.append("revision parent does not identify the completed review block")
    if revision_causal is False:
        errors.append("revision predates completed review evidence")
    if missing:
        return _result("O137", "hole", {"model_version": version, "frozen_at": frozen_at,
                       "observation_ids": observations, "revision_parent": revision_parent,
                       "changed_fields": changed, "count": len(changed),
                       "one_variable": one_variable}, hole_ids=_holes("O137", missing),
                       base_ok=None, coverage_ok=None, known_at=frozen_at, reason="model definition is incomplete")
    canonical = json.dumps(current, sort_keys=True, separators=(",", ":"), default=str)
    value = {"model_version": version, "definition_hash": sha256(canonical.encode()).hexdigest(),
             "frozen_at": frozen_at, "observation_ids": observations,
             "revision_parent": revision_parent, "changed_fields": changed,
             "changed_field_count": len(changed), "one_variable_revision": one_variable,
             "revision_causal": revision_causal, "encoding": "canonical-json-v1"}
    value.update({"count": len(changed), "one_variable": one_variable})
    if errors:
        return _result("O137", "invalid", value, base_ok=False, known_at=revision_at,
                       reason="; ".join(errors))
    return _result("O137", "computed", value, known_at=revision_at or frozen_at)


def _condition_value(condition: dict, event: dict | None) -> bool | None:
    if event is None:
        return None
    if type(event.get("observed")) is bool:
        return event["observed"]
    if type(event.get("result")) is bool:
        return event["result"]
    value = dec(event.get("value", event.get("price")))
    threshold = dec(condition.get("threshold", condition.get("level")))
    comparator = condition.get("comparator", condition.get("operator"))
    if value is None or threshold is None or comparator is None:
        return None
    return {"<": value < threshold, "<=": value <= threshold, ">": value > threshold,
            ">=": value >= threshold, "==": value == threshold, "!=": value != threshold}.get(comparator)


@_override("O138")
def o138(inp: dict) -> RecipeResult:
    thesis_id = inp.get("thesis_id")
    declared_at = inp.get("declared_at", inp.get("thesis_known_at", inp.get("known_at")))
    decision_at = inp.get("decision_at", inp.get("as_of", inp.get("use_at")))
    conditions = inp.get("death_conditions")
    events = inp.get("events", inp.get("death_events", [])) or []
    missing = []
    if thesis_id is None:
        missing.append("thesis_id")
    if declared_at is None:
        missing.append("declared_at")
    if not isinstance(conditions, list) or not conditions:
        missing.append("death_conditions")
        conditions = []
    if decision_at is None:
        missing.append("decision_at")
    event_by_condition: dict[str, list[dict]] = {}
    for event in events:
        key = event.get("condition_id", event.get("death_condition_id"))
        if key is not None:
            event_by_condition.setdefault(str(key), []).append(event)
    ledger, deaths = [], []
    coverage_unknown = False
    for index, condition in enumerate(conditions):
        cid = str(condition.get("condition_id", condition.get("id", index)))
        candidates = sorted(event_by_condition.get(cid, []), key=lambda row: _at(row) or -1)
        eligible = [row for row in candidates if decision_at is None or (_at(row) is not None and _at(row) <= decision_at)]
        evaluated = [(row, _condition_value(condition, row)) for row in eligible]
        first_true = next((row for row, observed_value in evaluated if observed_value is True), None)
        latest = first_true or (eligible[-1] if eligible else None)
        observed = True if first_true is not None else _condition_value(condition, latest)
        complete = condition.get("coverage_complete")
        if complete is None and latest is not None:
            complete = latest.get("coverage_complete", latest.get("coverage_ok"))
        if observed is None or complete is not True:
            coverage_unknown = True
        row = {"condition_id": cid, "producer_id": condition.get("producer_id"),
               "comparison": condition.get("comparator"), "evidence_scope": condition.get("evidence_scope"),
               "observed": observed, "observed_at": _at(latest) if latest else None,
               "coverage_complete": complete}
        ledger.append(row)
        if observed is True:
            deaths.append(row)
    deaths.sort(key=lambda row: row["observed_at"] if row["observed_at"] is not None else 10**30)
    first = deaths[0] if deaths else None
    if first is not None:
        thesis_state, alive = "dead", False
    elif missing or coverage_unknown:
        thesis_state, alive = "unknown", None
    else:
        thesis_state, alive = "alive", True
    replacement_id = inp.get("replacement_id")
    replacement_at = inp.get("replacement_at")
    errors = []
    if declared_at is not None and decision_at is not None and declared_at > decision_at:
        errors.append("thesis declared after use")
    if replacement_id is not None and first is None:
        errors.append("replacement supplied before an observed thesis death")
    if first and replacement_at is not None and replacement_at <= first["observed_at"]:
        errors.append("replacement does not follow thesis death")
    value = {"state": thesis_state, "first_death_at": first["observed_at"] if first else None,
             "death_reason": first["condition_id"] if first else None,
             "replacement_id": replacement_id, "alive_at_decision": alive,
             "condition_ledger": ledger, "thesis_id": thesis_id,
             "stopout_is_death": False}
    value.update({"first_death": value["first_death_at"], "alive": alive,
                  "revived": False, "stop_kills_thesis": False})
    if errors:
        return _result("O138", "invalid", value, base_ok=False, coverage_ok=None,
                       hole_ids=_holes("O138", ["ordering"]), known_at=_max_time(declared_at, *[_at(e) for e in events]),
                       reason="; ".join(errors))
    holes = _holes("O138", missing + (["condition_coverage"] if coverage_unknown and first is None else []))
    return _result("O138", "computed" if not holes else "hole", value, base_ok=True if first or not holes else None,
                   coverage_ok=True if not holes or first else None, hole_ids=holes,
                   known_at=_max_time(declared_at, *[_at(e) for e in events if decision_at is None or (_at(e) or 10**30) <= decision_at]))


@_override("O139")
def o139(inp: dict) -> RecipeResult:
    entry, stop = dec(inp.get("entry", inp.get("E"))), dec(inp.get("stop", inp.get("S")))
    side, q = inp.get("side"), dec(inp.get("q", inp.get("tick_size")))
    structure_at = inp.get("structure_confirmed_at", inp.get("confirmation_at"))
    policy_at = inp.get("policy_selected_at", inp.get("stop_policy_at", inp.get("known_at")))
    decision_at = inp.get("decision_at", inp.get("entry_at", inp.get("use_at")))
    policy = inp.get("stop_policy", inp.get("invalidation_policy"))
    provenance = inp.get("provenance", inp.get("order_provenance"))
    invalidation_ref = deepcopy(inp.get("invalidation_ref"))
    if invalidation_ref is None and inp.get("controlling_structure_id") is not None:
        invalidation_ref = {"object_id": inp["controlling_structure_id"],
                            "field": inp.get("invalidation_field"), "value": stop,
                            "known_at": structure_at}
    method = deepcopy(inp.get("planned_stop_method", inp.get("stop_method")))
    if method is None and isinstance(policy, dict):
        method = policy.get("method", policy.get("policy_id"))
    elif method is None and isinstance(policy, str):
        method = policy
    missing = [name for name, value in (("entry", entry), ("stop", stop), ("side", side),
                                         ("q", q), ("structure_confirmation", structure_at),
                                         ("stop_policy", policy), ("provenance", provenance)) if value is None]
    direction = Decimal(1) if side == "long" else Decimal(-1) if side == "short" else None
    distance = direction * (entry - stop) if None not in (direction, entry, stop) else None
    stop_ok = None if distance is None else distance > 0
    risk_preknown = None if None in (structure_at, policy_at, decision_at) else max(structure_at, policy_at) <= decision_at
    errors = []
    if side not in {None, "long", "short"}: errors.append("invalid side")
    if q is not None and q <= 0: errors.append("non-positive tick size")
    if stop_ok is False: errors.append("structural stop is not on the adverse side")
    if risk_preknown is False: errors.append("risk structure or policy selected after entry")
    if provenance == "drawing" and inp.get("claimed_actual_order") is True:
        errors.append("drawing is not actual order evidence")
    planned_known = _max_time(structure_at, policy_at)
    value = {"structural_stop": stop, "stop_distance_points": distance,
             "stop_distance_ticks": distance / q if distance is not None and q and q > 0 else None,
             "stop_side_ok": stop_ok, "risk_known_before_entry": risk_preknown,
             "policy_holes": _holes("O139", missing), "candidate_id": inp.get("candidate_id"),
             "controlling_structure_id": inp.get("controlling_structure_id"),
             "stop_policy": deepcopy(policy), "provenance": provenance,
             "invalidation_ref": invalidation_ref, "planned_stop": stop,
             "planned_stop_side": side, "planned_stop_method": method,
             "planned_stop_known_at": planned_known,
             "planned_stop_comparison": {"entry": entry, "planned_stop": stop, "side": side,
                                         "on_adverse_side": stop_ok}}
    value.update({"risk_points": distance, "risk_ticks": value["stop_distance_ticks"],
                  "valid_initial_stop": stop_ok, "wick_breaches_close_policy": False})
    if errors:
        return _result("O139", "invalid", value, base_ok=False, coverage_ok=None,
                       hole_ids=_holes("O139", ["policy"]), known_at=_max_time(structure_at, policy_at), reason="; ".join(errors))
    return _result("O139", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O139", missing), known_at=_max_time(structure_at, policy_at))


@_override("O140")
def o140(inp: dict) -> RecipeResult:
    distance = dec(inp.get("D", inp.get("stop_distance_points")))
    multiplier = dec(inp.get("M", inp.get("multiplier")))
    ticks = dec(inp.get("stop_distance_ticks"))
    tick_value = dec(inp.get("tick_value"))
    qty = dec(inp.get("quantity"))
    costs = dec(inp.get("included_costs", inp.get("costs", 0)))
    reserves = dec(inp.get("included_reserves", inp.get("reserves", 0)))
    existing = dec(inp.get("existing_exposure", inp.get("existing_risk_money", 0)))
    unit = distance * multiplier if distance is not None and multiplier is not None else (
        ticks * tick_value if ticks is not None and tick_value is not None else None)
    missing_units = []
    if distance is None and ticks is None: missing_units.append("stop_distance")
    if multiplier is None and tick_value is None: missing_units.append("multiplier_or_tick_value")
    if qty is None: missing_units.append("quantity")
    policy = inp.get("source_policy", inp.get("account_policy"))
    if policy is None: missing_units.append("source_policy")
    errors = []
    for name, value in (("stop distance", distance if distance is not None else ticks),
                        ("unit risk", unit), ("quantity", qty), ("cost", costs),
                        ("reserve", reserves), ("existing exposure", existing)):
        if value is not None and value < 0: errors.append(f"negative {name}")
    position = None if unit is None or qty is None else unit * qty + costs + reserves
    aggregate = None if position is None else position + existing
    cap = dec(inp.get("cap", policy.get("risk_cap") if isinstance(policy, dict) else None))
    cap_ok = None if cap is None or aggregate is None else aggregate <= cap
    if cap is None: missing_units.append("risk_cap")
    alloc_kind = inp.get("allocation_rule", policy.get("allocation_rule") if isinstance(policy, dict) else None)
    if inp.get("integer_max") is True:
        alloc_kind = "integer_max"
    max_qty = None
    quantity_ok = None
    if alloc_kind in {"integer_max", "maximum_integer_under_cap"} and cap is not None and unit and unit > 0:
        available = cap - existing - costs - reserves
        max_qty = max(0, int(available // unit))
        quantity_ok = None if qty is None else qty <= max_qty
    elif inp.get("quality_allocation_ok") is not None:
        quantity_ok = inp["quality_allocation_ok"]
    if inp.get("is_add") is True:
        secured = inp.get("earlier_risk_secured")
        quantity_ok = kleene_and(quantity_ok, secured)
        if secured is None: missing_units.append("earlier_risk_secured")
        if secured is False: errors.append("add attempted before earlier risk was secured")
    value = {"unit_risk_money": unit, "position_risk_money": position,
             "aggregate_risk_money": aggregate, "cap_ok": cap_ok,
             "quantity_policy_ok": quantity_ok, "missing_units": list(dict.fromkeys(missing_units)),
             "integer_max_contracts": max_qty, "included_costs": costs,
             "included_reserves": reserves, "existing_exposure": existing}
    value.update({"unit_risk": unit, "position_risk": position})
    if errors:
        return _result("O140", "invalid", value, base_ok=False, coverage_ok=None,
                       hole_ids=_holes("O140", ["risk_inputs"]), known_at=inp.get("known_at"), reason="; ".join(errors))
    holes = _holes("O140", list(dict.fromkeys(missing_units)))
    return _result("O140", "computed" if not holes else "hole", value,
                   base_ok=True if not holes else None, coverage_ok=True if not holes else None,
                   hole_ids=holes, known_at=inp.get("known_at"))


@_override("O141")
def o141(inp: dict) -> RecipeResult:
    objective = deepcopy(inp.get("objective")) if isinstance(inp.get("objective"), dict) else {}
    oid = inp.get("objective_id", objective.get("objective_id", objective.get("id")))
    otype = inp.get("objective_type", objective.get("type"))
    entry_id = inp.get("entry_id")
    side = inp.get("side")
    entry = dec(inp.get("entry", inp.get("entry_price")))
    target = dec(inp.get("target", objective.get("price")))
    selected_at = inp.get("selected_at", inp.get("selection_at"))
    objective_at = inp.get("objective_known_at", objective.get("known_at"))
    decision_at = inp.get("decision_at", inp.get("entry_at"))
    active = inp.get("active_at_selection", objective.get("active_at_selection"))
    direction = Decimal(1) if side == "long" else Decimal(-1) if side == "short" else None
    distance = direction * (target - entry) if None not in (direction, target, entry) else None
    preknown = None if None in (selected_at, objective_at, decision_at) else max(selected_at, objective_at) <= decision_at
    if active is None and objective.get("consumed_at") is not None and selected_at is not None:
        active = objective["consumed_at"] > selected_at
    outcome = None
    outcome_known = inp.get("outcome_coverage_complete")
    prints = inp.get("prints", inp.get("outcome_events", [])) or []
    eligible = [row for row in prints if _event_at(row) is not None and decision_at is not None and _event_at(row) > decision_at]
    if target is not None and direction is not None and eligible:
        reached = any((dec(row.get("price")) >= target if side == "long" else dec(row.get("price")) <= target)
                      for row in eligible if dec(row.get("price")) is not None)
        outcome = "reached" if reached else ("not_reached" if outcome_known is True else None)
    missing = [name for name, value in (("objective_id", oid), ("objective_type", otype),
                                         ("entry_id", entry_id), ("side", side), ("selection_at", selected_at),
                                         ("objective_known_at", objective_at)) if value is None]
    errors = []
    if side not in {None, "long", "short"}: errors.append("invalid side")
    if distance is not None and distance <= 0: errors.append("objective is not in the trade direction")
    if preknown is False: errors.append("objective selected after entry")
    if active is False: errors.append("objective was inactive when selected")
    value = {"selected_objective": {**objective, "objective_id": oid, "type": otype},
             "target_distance_points": distance, "objective_preknown": preknown,
             "active_at_selection": active, "later_outcome": outcome,
             "policy_holes": _holes("O141", missing), "entry_id": entry_id,
             "outcome_known_at": _max_time(*[_at(row) for row in eligible])}
    legacy_distance = abs(target - entry) if target is not None and entry is not None else None
    legacy_hit = target is not None and decision_at is not None and any(
        _event_at(row) is not None and _event_at(row) > decision_at and dec(row.get("price")) == target
        for row in prints
    )
    value.update({"distance": distance if distance is not None else legacy_distance,
                  "pre_entry_print_counts": False,
                  "post_entry_hit": outcome == "reached" or legacy_hit})
    if errors:
        return _result("O141", "invalid", value, base_ok=False, coverage_ok=None,
                       hole_ids=_holes("O141", ["objective_policy"]), known_at=_max_time(selected_at, objective_at), reason="; ".join(errors))
    return _result("O141", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O141", missing), known_at=_max_time(selected_at, objective_at))


def _allowed_action(policy: Any, kind: str) -> bool | None:
    if policy is None:
        return None
    allowed = policy.get("allowed_actions") if isinstance(policy, dict) else policy
    if isinstance(allowed, str): allowed = [allowed]
    if not isinstance(allowed, (list, tuple, set)): return None
    normalized = {str(item).lower().replace("-", "_").replace(" ", "_") for item in allowed}
    families = {"partial": {"partial_request", "partial_fill", "exit_fill"},
                "trail": {"trail", "stop_amend", "breakeven"},
                "add": {"add_fill"}, "static": {"exit_fill"}}
    return kind in normalized or any(kind in families.get(item, set()) for item in normalized)


@_override("O142")
def o142(inp: dict) -> RecipeResult:
    entry_id, entry_at = inp.get("entry_id"), inp.get("entry_at")
    initial_qty = dec(inp.get("position", inp.get("initial_quantity")))
    initial_stop = dec(inp.get("initial_stop")); initial_target = dec(inp.get("initial_target"))
    initial_risk = dec(inp.get("initial_risk"))
    policy = deepcopy(inp.get("source_policy", inp.get("policy")))
    policy_at = inp.get("policy_frozen_at", inp.get("policy_known_at"))
    raw_actions = list(inp.get("management_actions", inp.get("actions", [])) or [])
    for fill in inp.get("fills", []) or []:
        row = deepcopy(fill) if isinstance(fill, dict) else {"filled_qty": fill}
        row.setdefault("kind", "partial_fill")
        raw_actions.append(row)
    if inp.get("trail_at") is not None:
        raw_actions.append({"kind": "trail", "at": inp["trail_at"],
                            "protected_known_at": inp.get("protected_at")})
    actions, ordering_errors = _ordered(raw_actions, "O142")
    position = initial_qty
    stop_versions = ([{"version": 0, "at": entry_at, "price": initial_stop}] if initial_stop is not None else [])
    target_versions = ([{"version": 0, "at": entry_at, "price": initial_target}] if initial_target is not None else [])
    rendered, checks, errors, missing = [], [], list(ordering_errors), []
    if entry_id is None: missing.append("entry_id")
    if entry_at is None: missing.append("entry_at")
    if initial_qty is None: missing.append("initial_quantity")
    if policy is None: missing.append("source_policy")
    if policy_at is None: missing.append("policy_frozen_at")
    if initial_risk is None: missing.append("initial_risk")
    if policy_at is not None and entry_at is not None and policy_at > entry_at: errors.append("policy selected after entry")
    for action in actions:
        kind, at = _kind(action), _event_at(action)
        row = deepcopy(action); row["kind"] = kind; row["applied_quantity"] = Decimal(0)
        if entry_at is not None and at is not None and at < entry_at: errors.append("management action before entry")
        policy_check = _allowed_action(policy, kind)
        checks.append(policy_check)
        explicit_execution = _qty(action, filled_only=True) is not None
        is_request = kind in {"partial", "partial_request", "exit_request", "reduce_request", "requested_partial", "exit"} and not explicit_execution
        is_exit_fill = kind in {"partial_fill", "exit_fill", "fill_exit", "close_fill", "scale_out_fill"} or (
            explicit_execution and kind in {"partial", "exit", "partial_exit", "close", "reduce", "scale_out"}
        )
        is_add_fill = kind in {"add_fill", "scale_in_fill"}
        quantity = _qty(action, filled_only=not (kind in {"partial_fill", "exit_fill", "fill_exit", "close_fill", "scale_out_fill", "add_fill", "scale_in_fill"}))
        if is_request:
            row["requested_quantity"] = _qty(action)
        elif is_exit_fill or is_add_fill:
            if quantity is None: missing.append("filled_quantity")
            elif quantity <= 0: errors.append("non-positive management fill")
            elif position is not None:
                if is_exit_fill:
                    if quantity > position: errors.append("management exit exceeds open position")
                    else: position -= quantity; row["applied_quantity"] = quantity
                else:
                    secured = action.get("earlier_risk_secured")
                    if secured is not True:
                        (errors if secured is False else missing).append("earlier_risk_secured")
                    else: position += quantity; row["applied_quantity"] = quantity
        if kind in {"trail", "stop_amend", "breakeven"}:
            support_at = action.get("protected_known_at", action.get("support_known_at"))
            if support_at is None: missing.append("protected_confirmation")
            elif at is not None and support_at > at: errors.append("trail support confirmed after action")
            price = dec(action.get("new_stop", action.get("stop")))
            if price is not None: stop_versions.append({"version": len(stop_versions), "at": at, "price": price,
                                                        "support_known_at": support_at})
        if kind in {"target_amend", "target_move", "amend"}:
            price = dec(action.get("new_target", action.get("target")))
            if price is not None: target_versions.append({"version": len(target_versions), "at": at, "price": price})
        row["position_quantity_after"] = position
        rendered.append(row)
    computed_policy = False if any(check is False for check in checks) else None if any(check is None for check in checks) or not checks else True
    # A supplied Boolean may add a failure, but can never override a computed contradiction.
    supplied_policy = inp.get("action_policy_ok")
    policy_ok = kleene_and(computed_policy, supplied_policy) if supplied_policy is not None else computed_policy
    if policy_ok is None: missing.append("action_policy")
    if policy_ok is False: errors.append("action not allowed by frozen source policy")
    rewritten = [dec(row.get("initial_risk")) for row in actions if row.get("initial_risk") is not None]
    risk_unchanged = None if initial_risk is None else all(value == initial_risk for value in rewritten)
    if risk_unchanged is False: errors.append("management rewrote original risk")
    latest = _max_time(entry_at, *[_at(row) for row in actions])
    value = {"management_actions": rendered, "position_quantity_after": position,
             "stop_versions": stop_versions, "target_versions": target_versions,
             "action_policy_ok": policy_ok, "initial_risk_unchanged": risk_unchanged,
             "exit_reason": inp.get("exit_reason"), "entry_id": entry_id,
             "initial_quantity": initial_qty, "initial_stop": initial_stop,
             "initial_target": initial_target, "initial_risk": initial_risk}
    trail_checks = [
        row.get("protected_known_at") <= row.get("at")
        for row in rendered if row.get("kind") in {"trail", "stop_amend", "breakeven"}
        and row.get("protected_known_at") is not None and row.get("at") is not None
    ]
    value.update({"remaining": position,
                  "trail_supported": False if any(check is False for check in trail_checks)
                  else True if trail_checks else None})
    if errors:
        return _result("O142", "invalid", value, base_ok=False, coverage_ok=None,
                       hole_ids=_holes("O142", ["lifecycle"]), known_at=latest, reason="; ".join(dict.fromkeys(errors)))
    missing = list(dict.fromkeys(missing))
    return _result("O142", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O142", missing), known_at=latest)


@_override("O143")
def o143(inp: dict) -> RecipeResult:
    if inp.get("protected_price") is None and inp.get("protected_high") is not None:
        # Retain the old supplied-scalar spelling as an explicitly incomplete
        # confirmation record.  Rich records below remain required for a full
        # computed object.
        confirm = inp.get("confirm_at")
        usable = None if confirm is None or inp.get("use_at") is None else confirm <= inp["use_at"]
        value = {"protected_price": dec(inp["protected_high"]), "price_at": inp.get("high_priced_at"),
                 "confirmation_at": confirm, "protected_known_at": confirm, "side": "high",
                 "trail_allowed_at": usable, "protected_high": dec(inp["protected_high"]), "usable": usable}
        if usable is False:
            return _result("O143", "invalid", value, base_ok=False, coverage_ok=None,
                           known_at=confirm, reason="protected structure confirmation is after use")
        return _result("O143", "hole", value, base_ok=None, coverage_ok=None,
                       hole_ids=_holes("O143", ["native_confirmation_evidence"]), known_at=confirm)
    if inp.get("high") is not None and inp.get("confirm_at") is not None:
        confirm = inp["confirm_at"]
        usable = None if inp.get("use_at") is None else confirm <= inp["use_at"]
        value = {"protected_price": None, "price_at": inp.get("high_priced_at"),
                 "confirmation_at": confirm, "protected_known_at": confirm, "side": "high",
                 "trail_allowed_at": usable, "protected_high": None, "usable": usable}
        if usable is False:
            return _result("O143", "invalid", value, base_ok=False, coverage_ok=None,
                           known_at=confirm, reason="protected structure confirmation is after use")
    side = inp.get("side")
    pivot = inp.get("pivot", {}) if isinstance(inp.get("pivot"), dict) else {}
    price = dec(inp.get("protected_price", inp.get("price", pivot.get("price"))))
    price_at = inp.get("price_at", pivot.get("at"))
    band_id = inp.get("band_id", pivot.get("band_id"))
    break_event = inp.get("break_event", {}) if isinstance(inp.get("break_event"), dict) else {}
    close_event = inp.get("close_event", {}) if isinstance(inp.get("close_event"), dict) else {}
    aggression = inp.get("aggression_event", {}) if isinstance(inp.get("aggression_event"), dict) else {}
    required = [("protected_price", price), ("price_at", price_at), ("side", side), ("band_id", band_id),
                ("break_event", break_event or None), ("completed_close", close_event or None),
                ("aggression_event", aggression or None)]
    missing = [name for name, value in required if value is None]
    evidence_times = [_at(row) for row in (break_event, close_event, aggression) if row]
    confirmation = _max_time(*evidence_times)
    expected_break = "low" if side == "high" else "high" if side == "low" else None
    errors = []
    if side not in {None, "high", "low", "protected_high", "protected_low"}: errors.append("invalid protected side")
    normalized_side = "high" if side in {"high", "protected_high"} else "low" if side in {"low", "protected_low"} else side
    expected_break = "low" if normalized_side == "high" else "high" if normalized_side == "low" else None
    if break_event and break_event.get("break_side") not in {None, expected_break}: errors.append("wrong confirming break side")
    if close_event and close_event.get("complete") is not True: errors.append("confirming close is incomplete")
    if aggression and aggression.get("real_aggression") is not True: errors.append("aggression evidence does not confirm control")
    if price_at is not None and any(t is not None and t <= price_at for t in evidence_times): errors.append("confirmation does not follow pivot")
    trail_at = inp.get("trail_at", inp.get("stop_action_at"))
    trail_allowed = None if confirmation is None or trail_at is None else confirmation <= trail_at
    value = {"protected_price": price, "price_at": price_at, "confirmation_at": confirmation,
             "protected_known_at": confirmation, "side": normalized_side,
             "trail_allowed_at": trail_allowed, "band_id": band_id,
             "evidence_ids": [row.get("event_id", row.get("id")) for row in (break_event, close_event, aggression) if row]}
    if errors:
        return _result("O143", "invalid", value, base_ok=False, coverage_ok=None,
                       hole_ids=_holes("O143", ["confirmation"]), known_at=confirmation, reason="; ".join(errors))
    return _result("O143", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O143", missing), known_at=confirmation)


@_override("O144")
def o144(inp: dict) -> RecipeResult:
    parent_entry = inp.get("parent_entry_id")
    parent_position = inp.get("parent_position_id")
    parent_exit = inp.get("parent_exit_id")
    exit_at = inp.get("parent_exit_at", inp.get("exit_at"))
    candidate = inp.get("new_candidate_id", inp.get("candidate_id"))
    old_thesis, new_thesis = inp.get("parent_thesis_id", inp.get("thesis_id")), inp.get("new_thesis_id", inp.get("thesis_id"))
    old_band, new_band = inp.get("parent_band_id", inp.get("band_id")), inp.get("new_band_id", inp.get("band_id"))
    fresh_at = inp.get("fresh_confirmation_at", inp.get("confirmation_at"))
    decision_at = inp.get("decision_at")
    returned_at = inp.get("return_at")
    branch = inp.get("full_branch_verdict", inp.get("branch_verdict"))
    risk_permission = inp.get("account_permission", inp.get("daily_permission"))
    thesis_state = inp.get("thesis_state", "alive" if inp.get("thesis_alive") is True else None)
    same = None if None in (old_thesis, new_thesis, old_band, new_band) else old_thesis == new_thesis and old_band == new_band
    ordering = None if None in (exit_at, returned_at, fresh_at, decision_at) else exit_at < returned_at <= fresh_at <= decision_at
    branch_check = branch if type(branch) is bool else None
    permission = kleene_and(same, thesis_state == "alive" if thesis_state is not None else None,
                            ordering, branch_check, risk_permission)
    missing = [name for name, value in (("parent_entry_id", parent_entry), ("parent_position_id", parent_position),
                                         ("parent_exit_id", parent_exit), ("parent_exit_at", exit_at),
                                         ("new_candidate_id", candidate), ("thesis_ids", None if None in (old_thesis,new_thesis) else True),
                                         ("band_ids", None if None in (old_band,new_band) else True), ("return_at", returned_at),
                                         ("fresh_confirmation_at", fresh_at), ("decision_at", decision_at),
                                         ("full_branch_verdict", branch), ("account_permission", risk_permission),
                                         ("thesis_state", thesis_state)) if value is None]
    errors = []
    if same is False: errors.append("re-entry does not use the same live thesis and band")
    if thesis_state == "dead": errors.append("dead thesis requires a new thesis, not re-entry")
    if ordering is False: errors.append("re-entry sequence is not causal")
    if branch is False: errors.append("fresh branch did not qualify")
    if risk_permission is False: errors.append("source account policy prohibits re-entry")
    value = {"parent_exit_at": exit_at, "new_candidate_id": candidate,
             "same_thesis_band": same, "fresh_confirmation_at": fresh_at,
             "full_branch_verdict": branch, "reentry_permission": permission,
             "parent_entry_id": parent_entry, "parent_position_id": parent_position,
             "parent_exit_id": parent_exit, "return_at": returned_at}
    value.update({"fresh": permission, "freshness_ok": ordering,
                  "blocked": None if risk_permission is None else risk_permission is False})
    if errors:
        return _result("O144", "invalid", value, base_ok=False, coverage_ok=True,
                       known_at=_max_time(fresh_at, inp.get("risk_state_known_at")), reason="; ".join(errors))
    return _result("O144", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O144", missing), known_at=_max_time(fresh_at, inp.get("risk_state_known_at")))


def _scope_matches(row: dict, inp: dict, policy: dict) -> bool:
    for key in ("source_id", "account_id", "session_id", "policy_id"):
        expected = inp.get(key, policy.get(key))
        if expected is not None and row.get(key) != expected:
            return False
    return True


@_override("O145")
def o145(inp: dict) -> RecipeResult:
    policy = deepcopy(inp.get("source_policy", inp.get("policy"))) if isinstance(inp.get("source_policy", inp.get("policy")), dict) else {}
    policy_id = inp.get("policy_id", policy.get("policy_id"))
    policy_at = inp.get("policy_frozen_at", policy.get("frozen_at"))
    attempt_at = inp.get("attempt_at", inp.get("decision_at", inp.get("use_at")))
    limit = dec(inp.get("limit_r", policy.get("limit_r")))
    definition=inp.get("original_r_definition",policy.get("original_r_definition"))
    if isinstance(definition,dict):
        r_definition_id=definition.get("definition_id",definition.get("r_definition_id"))
    else:
        r_definition_id=inp.get("r_definition_id",policy.get("r_definition_id"))
    ledger_complete=inp.get("prior_ledger_coverage_complete",policy.get("prior_ledger_coverage_complete"))
    session_finished = inp.get("session_finished")
    rows = deepcopy(inp.get("result_records", inp.get("results", [])) or [])
    reported_total = (sum((dec(value) for value in inp["results_r"]), Decimal(0))
                      if not rows and isinstance(inp.get("results_r"), list) else None)
    included, unresolved = [], []
    excluded_other_scope=0; seen_ids=set(); errors=[]
    for row in rows:
        if not _scope_matches(row, inp, policy):
            excluded_other_scope+=1
            continue
        result_id=row.get("result_id",row.get("id"))
        expected_scope={key:inp.get(key,policy.get(key)) for key in ("source_id","account_id","session_id","policy_id")}
        if any(value is not None and row.get(key) is None for key,value in expected_scope.items()):
            unresolved.append(result_id)
            continue
        close_at=row.get("close_at",row.get("closed_at")); available_at=row.get("available_at",row.get("known_at"))
        if type(close_at) is not int or type(available_at) is not int:
            unresolved.append(result_id)
            continue
        if attempt_at is not None and (close_at>=attempt_at or available_at>=attempt_at):
            continue
        if available_at<close_at:
            errors.append("prior result is available before it closes")
            continue
        if result_id is None:
            unresolved.append(None)
            continue
        if str(result_id) in seen_ids:
            errors.append("prior result identities are duplicated")
            continue
        seen_ids.add(str(result_id))
        row_definition=row.get("r_definition_id",row.get("original_r_definition_id"))
        if row_definition is None or r_definition_id is None:
            unresolved.append(result_id)
            continue
        if str(row_definition)!=str(r_definition_id):
            errors.append("prior result uses a different original R definition")
            continue
        value = dec(row.get("result_r", row.get("r")))
        if value is None:
            unresolved.append(result_id)
        else:
            included.append((row, value))
    total = sum((value for _, value in included), Decimal(0)) if ledger_complete is True and not unresolved and not errors else None
    permission = None if total is None or limit is None or type(session_finished) is not bool else total > limit and not session_finished
    breach = None if total is None or limit is None else total <= limit
    missing = []
    if policy_id is None: missing.append("policy_id")
    if policy_at is None: missing.append("policy_frozen_at")
    if attempt_at is None: missing.append("attempt_at")
    if limit is None: missing.append("policy_limit")
    if r_definition_id is None: missing.append("original_r_definition")
    if ledger_complete is not True: missing.append("prior_ledger_coverage")
    if type(session_finished) is not bool: missing.append("session_finished")
    if reported_total is not None: missing.append("result_records")
    if unresolved: missing.append("prior_result_identity_time_value_or_r_definition")
    for key in ("source_id","account_id","session_id"):
        if inp.get(key,policy.get(key)) is None: missing.append(key)
    if policy_at is not None and attempt_at is not None and policy_at > attempt_at: errors.append("policy frozen after attempt")
    if limit is not None and limit >= 0: errors.append("loss limit must be a negative R boundary")
    if session_finished is not None and type(session_finished) is not bool: errors.append("session_finished must be Boolean")
    for key in ("source_id","account_id","session_id","policy_id"):
        if inp.get(key) is not None and policy.get(key) is not None and str(inp[key])!=str(policy[key]):
            errors.append(f"source policy {key} conflicts with requested scope")
    value = {"daily_R_before": total, "daily_r_before": total, "policy_limit": limit,
             "session_finished": session_finished, "entry_permission": permission,
             "rule_breach": True if session_finished is True else breach,
             "ledger_ids": [row.get("result_id", row.get("id")) for row, _ in included],
             "excluded_other_scope_count": excluded_other_scope,
             "policy_id": policy_id, "reported_daily_R": reported_total,
             "r_definition_id":r_definition_id,"prior_ledger_coverage_complete":ledger_complete}
    value.update({"sum_r": total if total is not None else reported_total})
    if errors:
        return _result("O145", "invalid", value, base_ok=False, coverage_ok=None,
                       known_at=_max_time(policy_at, *[row.get("available_at",row.get("known_at")) for row, _ in included]), reason="; ".join(dict.fromkeys(errors)))
    return _result("O145", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O145", missing), known_at=_max_time(policy_at, *[row.get("available_at",row.get("known_at")) for row, _ in included]))


@_override("O146")
def o146(inp: dict) -> RecipeResult:
    process_version = inp.get("process_version", inp.get("model_version"))
    config = deepcopy(inp.get("process_config", {}))
    eligible_supplied = "eligible_ids" in inp or "eligible" in inp
    eligible = list(inp.get("eligible_ids", inp.get("eligible", [])) or [])
    supplied = inp.get("journal_rows", inp.get("journal", [])) or []
    if isinstance(supplied, dict):
        rows = [dict(value, candidate_id=value.get("candidate_id", key)) if isinstance(value, dict)
                else {"candidate_id": key, "outcome": value}
                for key, value in supplied.items()]
    else:
        rows = [deepcopy(row) for row in supplied if isinstance(row, dict)]
    row_map = {row.get("candidate_id", row.get("attempt_id", row.get("id"))): row for row in rows}
    duplicates = len(row_map) != len(rows) or None in row_map
    missing_ids = [candidate_id for candidate_id in eligible if candidate_id not in row_map]
    accounted = [candidate_id for candidate_id in eligible if candidate_id in row_map]
    pre_checks, breaches, reviews, normalized = [], [], [], []
    confidence_cfg = config.get("confidence") if isinstance(config.get("confidence"), dict) else {}
    field_names = tuple(config.get("required_pre_entry_fields", ("thesis_id", "reason", "confidence", "context", "regime")))
    for candidate_id in accounted:
        row = deepcopy(row_map[candidate_id]); decision = row.get("decision_at")
        fields = []
        if row.get("feature_known_at") is not None and decision is not None:
            fields.append(row["feature_known_at"] <= decision)
        for field in field_names:
            value = row.get(field)
            field_at = row.get(f"{field}_known_at", row.get("feature_known_at", row.get("reason_at")))
            ok = None if value is None or decision is None or field_at is None else field_at <= decision
            fields.append(ok)
        # Source-configured confidence example: 1-5 observed at session start.
        if confidence_cfg:
            confidence = row.get("confidence")
            session_start = row.get("session_start_at")
            confidence_at = row.get("confidence_known_at")
            if confidence is None or session_start is None or confidence_at is None:
                fields.append(None)
            else:
                fields.append(type(confidence) is int and confidence_cfg.get("min", 1) <= confidence <= confidence_cfg.get("max", 5)
                              and confidence_at == session_start)
        outcome_at = row.get("outcome_at")
        input_id, output_id = row.get("input_record_id"), row.get("outcome_record_id")
        if input_id is not None and input_id == output_id: fields.append(False)
        if outcome_at is not None and decision is not None and outcome_at <= decision: fields.append(False)
        pre_checks.extend(fields)
        breaches.extend(deepcopy(row.get("breaches", [])))
        reviews.extend(deepcopy(row.get("review_links", [])))
        normalized.append(row)
    review_cfg = config.get("review") if isinstance(config.get("review"), dict) else {}
    review_example = review_cfg.get("example_sessions")
    if review_example is not None and review_example != 30:
        pre_checks.append(False)
    errors = []
    if duplicates: errors.append("duplicate or absent journal identity")
    holes = []
    if process_version is None: holes.append("process_version")
    if not isinstance(inp.get("process_config"), dict) or not inp.get("process_config"):
        holes.append("process_config")
    if not eligible_supplied: holes.append("eligible_ids")
    if any(check is False for check in pre_checks): errors.append("late, malformed, or conflated pre-entry field")
    pre_valid = False if any(check is False for check in pre_checks) else None if any(check is None for check in pre_checks) or not pre_checks else True
    lineage_complete = bool(normalized) and all(
        row.get("input_record_id") is not None and row.get("outcome_record_id") is not None
        for row in normalized
    )
    separated = (all(row["input_record_id"] != row["outcome_record_id"] for row in normalized)
                 if lineage_complete else None)
    value = {"journal_rows": normalized, "pre_entry_fields_valid": pre_valid,
             "eligible_ids_accounted_for": accounted, "missing_ids": missing_ids,
             "breach_records": breaches, "review_links": reviews,
             "process_version": process_version, "confidence_config": confidence_cfg or None,
             "review_config": review_cfg or None,
             "mfe_mae_collection": deepcopy(config.get("mfe_mae_collection")),
             "completeness": (not missing_ids) if eligible_supplied else None,
             "inputs_outcomes_separate": separated,
             "outcomes_separated_from_inputs": separated}
    value.update({"accounted": len(accounted), "of": len(eligible), "missing": missing_ids,
                  "later_explanation": inp.get("reason_at") is not None and inp.get("entry_at") is not None
                  and inp["reason_at"] > inp["entry_at"]})
    if errors:
        return _result("O146", "invalid", value, base_ok=False, coverage_ok=None,
                       hole_ids=_holes("O146", ["journal"]), known_at=_max_time(*[_at(row) for row in rows]), reason="; ".join(errors))
    if missing_ids: holes.append("eligible_records")
    if pre_valid is None: holes.append("pre_entry_fields")
    if not lineage_complete: holes.append("record_lineage")
    return _result("O146", "computed" if not holes else "hole", value,
                   base_ok=True if not holes else None, coverage_ok=True if not holes else None,
                   hole_ids=_holes("O146", holes), known_at=_max_time(*[_at(row) for row in rows]))


@_override("O147")
def o147(inp: dict) -> RecipeResult:
    instruments = tuple(inp.get("required_instruments", ("ES", "NQ", "YM")))
    objects = [deepcopy(row) for row in inp.get("objects", inp.get("amt_objects", [])) or [] if isinstance(row, dict)]
    events = [deepcopy(row) for row in inp.get("events", inp.get("use_events", [])) or [] if isinstance(row, dict)]
    revisions = [deepcopy(row) for row in inp.get("revisions", []) or [] if isinstance(row, dict)]
    object_map = {row.get("object_id", row.get("id")): row for row in objects}
    errors, missing = [], []
    if None in object_map or len(object_map) != len(objects): errors.append("object identities absent or duplicated")
    by_instrument = {symbol: [row for row in objects if row.get("instrument_id", row.get("symbol", row.get("root"))) == symbol] for symbol in instruments}
    for symbol, rows in by_instrument.items():
        if not rows: missing.append(f"native_object_{symbol}")
        for row in rows:
            bounds = row.get("bounds")
            if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
                missing.append(f"native_bounds_{symbol}")
            if _at(row) is None:
                missing.append(f"native_known_at_{symbol}")
    correspondence = inp.get("source_object_correspondence")
    if correspondence is None: correspondence = inp.get("correspondence_rationale")
    if correspondence is None: missing.append("source_object_correspondence")
    first_times: dict[str, int | None] = {}
    for symbol in instruments:
        matches = []
        for event in events:
            oid = event.get("object_id")
            obj = object_map.get(oid)
            if obj and obj.get("instrument_id", obj.get("symbol")) == symbol and _at(obj) is not None and _event_at(event) is not None:
                if _at(obj) <= _event_at(event): matches.append(event)
        first_times[symbol] = min((_event_at(row) for row in matches), default=None)
        if first_times[symbol] is None: missing.append(f"first_use_{symbol}")
    available = [(at, symbol) for symbol, at in first_times.items() if at is not None]
    first_instrument = min(available)[1] if available else None
    if len(available) > 1 and sum(at == min(a for a, _ in available) for at, _ in available) > 1:
        first_instrument = None; missing.append("first_use_tie")
    def revision_valid(kind: str) -> bool | None:
        rows = [row for row in revisions if _kind(row) == kind]
        if not rows: return None
        row = rows[0]; trigger = row.get("trigger_event_id"); event = next((e for e in events if e.get("event_id", e.get("id")) == trigger), None)
        return event is not None and _event_at(event) is not None and _event_at(row) is not None and _event_at(event) <= _event_at(row)
    iod = revision_valid("iod_reaction_revision")
    rfz = revision_valid("rfz_target_revision")
    value = {"native_first_use_times": first_times,
             "source_object_correspondence": deepcopy(correspondence),
             "first_instrument": first_instrument, "iod_reaction_revision": iod,
             "rfz_target_revision": rfz, "native_objects": objects,
             "first_use_events": events, "revision_records": revisions,
             "native_count": len(objects)}
    peer_test = inp.get("peer_test_at"); decision = inp.get("decision_at")
    value.update({"reread_ok": None if peer_test is None or decision is None else peer_test <= decision,
                  "peer_fill_revises": False if inp.get("peer_fill_at") is not None else None,
                  "edge_inequality_relevant": False})
    if errors:
        return _result("O147", "invalid", value, base_ok=False, coverage_ok=None,
                       known_at=_max_time(*[_at(row) for row in objects + events + revisions]), reason="; ".join(errors))
    return _result("O147", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O147", missing), known_at=_max_time(*[_at(row) for row in objects + events + revisions]))


@_override("O148")
def o148(inp: dict) -> RecipeResult:
    if not inp.get("candidates") and inp.get("eligible") is not None and not isinstance(inp.get("eligible"), list):
        eligible_n = int(inp.get("eligible", 0)); selected_n = int(inp.get("selected", 0))
        order_n = int(inp.get("orders", 0)); filled_n = int(inp.get("filled", 0))
        value = {"cohort_hash": None, "eligible_count": eligible_n, "selected_count": selected_n,
                 "order_count": order_n, "filled_order_count": filled_n,
                 "unselected_ids": None, "split_direction": inp.get("split_direction"),
                 "cohort_causal": None, "inclusion_rule_fixed": None, "uniform_schema": None,
                 "eligible": eligible_n, "selected": selected_n,
                 "orders": order_n, "filled": filled_n, "unselected": eligible_n - selected_n,
                 "missing_orders": selected_n - order_n, "completeness": selected_n == order_n,
                 "pairable": False if filled_n != selected_n else None}
        if min(eligible_n, selected_n, order_n, filled_n) < 0 or not eligible_n >= selected_n >= order_n >= filled_n:
            return _result("O148", "invalid", value, base_ok=False, coverage_ok=None,
                           reason="cohort lifecycle counts are inconsistent")
        selected_ids = inp.get("selected_ids")
        filled_ids = inp.get("filled_candidate_ids")
        common_ids = inp.get("common_ids")
        if isinstance(inp.get("order_records"), list) and isinstance(inp.get("fill_records"), list):
            order_map = {row.get("order_id"): row.get("candidate_id") for row in inp["order_records"]}
            filled_order_ids = {row.get("order_id") for row in inp["fill_records"]}
            if filled_order_ids <= set(order_map):
                filled_ids = sorted({order_map[order_id] for order_id in filled_order_ids}, key=str)
        if isinstance(selected_ids, list) and isinstance(filled_ids, list) and isinstance(common_ids, list):
            value["pairable"] = (
                len(set(selected_ids)) == selected_n == len(selected_ids)
                and len(set(filled_ids)) == filled_n == len(filled_ids)
                and set(selected_ids) == set(filled_ids) == set(common_ids)
            )
        if inp.get("claim_paired") is True and not (
            isinstance(selected_ids, list) and isinstance(filled_ids, list) and isinstance(common_ids, list)
            and len(set(selected_ids)) == selected_n == len(selected_ids)
            and len(set(filled_ids)) == filled_n == len(filled_ids)
            and set(selected_ids) == set(filled_ids) == set(common_ids)
        ):
            value["pairable"] = False
            return _result("O148", "invalid", value, base_ok=False, coverage_ok=None,
                           reason="cohorts lack complete common candidate identities")
        return _result("O148", "hole", value, base_ok=None, coverage_ok=None,
                       hole_ids=_holes("O148", ["candidate_manifest"]), known_at=inp.get("known_at"))
    process = inp.get("process_version", inp.get("model_version")); frozen = inp.get("frozen_at")
    candidates = deepcopy(inp.get("candidates", []))
    if not candidates and isinstance(inp.get("eligible_ids"), list):
        candidates = [{"candidate_id": cid, "selected": cid in set(inp.get("selected_ids", []))} for cid in inp["eligible_ids"]]
    ids = [row.get("candidate_id", row.get("id")) for row in candidates]
    orders = deepcopy(inp.get("order_records", [])); fills = deepcopy(inp.get("fill_records", []))
    order_ids = [row.get("order_id") for row in orders]; fill_ids = [row.get("fill_id") for row in fills]
    errors, missing = [], []
    if not candidates: missing.append("candidate_manifest")
    if None in ids or len(ids) != len(set(ids)): errors.append("candidate identities absent or duplicated")
    if None in order_ids or len(order_ids) != len(set(order_ids)): errors.append("order identities absent or duplicated")
    if None in fill_ids or len(fill_ids) != len(set(fill_ids)): errors.append("fill identities absent or duplicated")
    selected_ids = [row.get("candidate_id", row.get("id")) for row in candidates if row.get("selected") is True]
    if inp.get("selected_ids") is not None: selected_ids = list(inp["selected_ids"])
    if any(row.get("candidate_id") not in selected_ids for row in orders): errors.append("order lacks selected candidate")
    if any(row.get("order_id") not in set(order_ids) for row in fills): errors.append("fill lacks linked order")
    filled_orders = {row.get("order_id") for row in fills}
    observed_times = [_at(row) for row in candidates + orders + fills]
    causal = None if frozen is None or any(at is None for at in observed_times) else all(at >= frozen for at in observed_times)
    if causal is False: errors.append("cohort manifest frozen after observations began")
    unselected = sorted(set(ids) - set(selected_ids), key=str)
    manifest = {"process_version": process, "frozen_at": frozen, "scope": inp.get("scope"),
                "candidates": candidates, "orders": orders, "fills": fills,
                "split_boundaries": inp.get("split_boundaries")}
    digest = sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    if process is None: missing.append("process_version")
    if frozen is None: missing.append("frozen_at")
    if inp.get("inclusion_rule") is None: missing.append("inclusion_rule")
    uniform_schema = None if not candidates else len({tuple(sorted(row)) for row in candidates}) == 1
    value = {"cohort_hash": digest, "eligible_count": len(ids), "selected_count": len(selected_ids),
             "order_count": len(orders), "filled_order_count": len(filled_orders),
             "unselected_ids": unselected, "split_direction": inp.get("split_direction"),
             "cohort_causal": causal,
             "inclusion_rule_fixed": None if frozen is None or inp.get("inclusion_rule") is None else True,
             "uniform_schema": uniform_schema, "eligible_ids": ids, "selected_ids": selected_ids,
             "order_ids": order_ids, "filled_order_ids": sorted(filled_orders, key=str)}
    if errors:
        return _result("O148", "invalid", value, base_ok=False, coverage_ok=None,
                       known_at=_max_time(frozen, *observed_times), reason="; ".join(errors))
    return _result("O148", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O148", missing), known_at=_max_time(frozen, *observed_times))


@_override("O149")
def o149(inp: dict) -> RecipeResult:
    score, threshold = dec(inp.get("score")), dec(inp.get("threshold"))
    comparator = inp.get("comparator", ">=" if inp.get("inclusive", True) else ">")
    feature_rows = inp.get("features", []) or []
    feature_times = [_at(row) for row in feature_rows]
    if not feature_rows and inp.get("features_known_at") is not None: feature_times = [inp["features_known_at"]]
    max_feature = _max_time(*feature_times)
    order_at = inp.get("order_at"); model_at = inp.get("model_known_at"); grade_at = inp.get("grade_available_at")
    training = inp.get("training_cutoff_at")
    selected = None
    if score is not None and threshold is not None:
        selected = {">=": score >= threshold, ">": score > threshold,
                    "<=": score <= threshold, "<": score < threshold}.get(comparator)
    feature_causal = None if None in (max_feature, order_at) else max_feature <= order_at
    model_causal = None if None in (model_at, order_at) else model_at <= order_at
    if training is not None and model_at is not None: model_causal = kleene_and(model_causal, training <= model_at)
    if grade_at is not None and order_at is not None: model_causal = kleene_and(model_causal, grade_at <= order_at)
    touch_at = inp.get("touch_at")
    label_post_touch = None if touch_at is None or grade_at is None or any(at is None for at in feature_times) else (
        touch_at <= min(feature_times) and max(feature_times) <= grade_at
    )
    missing = [name for name, value in (("model_id", inp.get("model_id")), ("model_version", inp.get("model_version")),
                                         ("training_cutoff", training), ("features", feature_rows or None),
                                         ("transform_versions", inp.get("transform_versions")), ("score", score),
                                         ("threshold", threshold), ("comparator", comparator),
                                         ("grade_available_at", grade_at), ("order_at", order_at)) if value is None]
    transform_versions = inp.get("transform_versions")
    for index, feature in enumerate(feature_rows):
        feature_id = feature.get("feature_id", feature.get("id", feature.get("name")))
        if feature_id is None: missing.append(f"feature_{index}_id")
        if _at(feature) is None: missing.append(f"feature_{index}_known_at")
        if feature.get("value") is None: missing.append(f"feature_{index}_value")
        if isinstance(transform_versions, dict) and feature_id is not None and transform_versions.get(feature_id) is None:
            missing.append(f"feature_{feature_id}_transform")
    if inp.get("later_ofm_causal_status") not in {"negative", "corrected"}:
        missing.append("causal_correction")
    errors = []
    if selected is None and score is not None and threshold is not None: errors.append("unsupported comparator")
    if feature_causal is False: errors.append("feature available after order")
    if model_causal is False: errors.append("model, training, or grade available after order")
    value = {"supplied_grade": inp.get("supplied_grade"), "model_known_before_use": model_causal,
             "max_feature_known_at": max_feature, "feature_causal": feature_causal,
             "selected_by_supplied_rule": selected, "automatic_grade": None,
             "label_uses_only_post_touch_observations": label_post_touch,
             "score": score, "threshold": threshold, "comparator": comparator}
    value.update({"selection": selected})
    if errors:
        return _result("O149", "invalid", value, base_ok=False, coverage_ok=None,
                       known_at=_max_time(model_at, max_feature, grade_at), reason="; ".join(errors))
    return _result("O149", "supplied" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O149", missing), known_at=_max_time(model_at, max_feature, grade_at))


def _source_policy(inp: dict, rid: str) -> tuple[dict, list[str]]:
    policy = deepcopy(inp.get("source_policy"))
    if not isinstance(policy, dict):
        # A label records provenance but activates no numeric source defaults.
        return ({"policy_id": policy} if policy is not None else {}), (["source_policy_definition"] if policy is not None else ["source_policy"])
    applicable = True
    for key in ("source_id", "method_id", "account_id"):
        if policy.get(key) is not None and inp.get(key) is not None and policy[key] != inp[key]: applicable = False
    return (policy, []) if applicable else ({}, ["source_policy_scope"])


@_override("O150")
def o150(inp: dict) -> RecipeResult:
    order_id = inp.get("order_id"); candidate_id = inp.get("candidate_id"); position_id = inp.get("position_id")
    side = inp.get("side"); order_type = inp.get("order_type")
    price = dec(inp.get("limit", inp.get("price"))); quantity = dec(inp.get("quantity"))
    placed = inp.get("placed_at", inp.get("placement_at")); as_of = inp.get("as_of", inp.get("use_at", inp.get("known_at")))
    placement_available = inp.get("placement_known_at", inp.get("order_known_at", placed))
    policy, policy_holes = _source_policy(inp, "O150")
    q = dec(inp.get("q", inp.get("tick_size")))
    stop = dec(inp.get("stop")); target = dec(inp.get("target"))
    stop_ticks = dec(inp.get("stop_ticks", policy.get("stop_ticks"))); target_ticks = dec(inp.get("target_ticks", policy.get("target_ticks")))
    cancel_minutes = dec(inp.get("cancel_minutes", policy.get("cancel_minutes")))
    if stop is None and None not in (price, q, stop_ticks) and side in {"long", "short"}:
        stop = price - q * stop_ticks if side == "long" else price + q * stop_ticks
    if target is None and None not in (price, q, target_ticks) and side in {"long", "short"}:
        target = price + q * target_ticks if side == "long" else price - q * target_ticks
    cancel_at = inp.get("cancel_at")
    if cancel_at is None and placed is not None and cancel_minutes is not None:
        cancel_at = placed + int(cancel_minutes * 60 * 1_000_000_000)
    raw_events = [deepcopy(row) for row in inp.get("events", inp.get("order_events", [])) or [] if isinstance(row, dict)]
    unclocked_fill_quantities = []
    for qty in inp.get("fill_qtys", []) or []:
        if not isinstance(qty, dict):
            unclocked_fill_quantities.append(dec(qty))
            continue
        row = deepcopy(qty)
        row.setdefault("kind", "fill")
        raw_events.append(row)
    for key, kind in (("triggered_at", "trigger"), ("expired_at", "expire"), ("exit_at", "exit_fill")):
        if inp.get(key) is not None: raw_events.append({"kind": kind, "at": inp[key], "qty": inp.get("exit_quantity")})
    if cancel_at is not None and not any(_kind(row) in {"cancel", "canceled"} and _event_at(row) == cancel_at for row in raw_events):
        raw_events.append({"kind": "cancel", "at": cancel_at, "synthetic_from_policy": inp.get("cancel_at") is None})
    unclocked_events = [row for row in raw_events if _event_at(row) is None]
    raw_events = [row for row in raw_events if _event_at(row) is not None]
    events, order_errors = _ordered(raw_events, "O150")
    # Replay only facts available at the requested snapshot. Future supplied
    # rows remain visible in pending_events and cannot leak into the result.
    available, pending = [], []
    for row in events:
        available_at = _at(row)
        if as_of is not None and available_at is not None and available_at > as_of: pending.append(row)
        else: available.append(row)
    state = "resting" if placed is not None and placement_available is not None and (
        as_of is None or placement_available <= as_of
    ) else "unplaced"
    authorized = quantity; working = quantity if state == "resting" else Decimal(0)
    filled = Decimal(0); generation_filled = Decimal(0); position = Decimal(0); timeline = []; bracket_versions = []
    if stop is not None or target is not None:
        bracket_versions.append({"version": 0, "at": placed, "stop": stop, "target": target})
    errors = list(order_errors); missing = list(policy_holes)
    if unclocked_fill_quantities: missing.append("fill_event_records")
    if unclocked_events: missing.append("event_at")
    if order_id is None: missing.append("order_id")
    if candidate_id is None: missing.append("candidate_id")
    if position_id is None: missing.append("position_id")
    if price is None: missing.append("order_price")
    if quantity is None: missing.append("quantity")
    if placed is None: missing.append("placed_at")
    if order_type is None: missing.append("order_type")
    if side is None: missing.append("side")
    identified_events = [row for row in [*raw_events, *unclocked_events]
                         if row.get("synthetic_from_policy") is not True]
    event_ids = [row.get("event_id", row.get("id")) for row in identified_events]
    if raw_events and any(event_id is None for event_id in event_ids): missing.append("event_identity")
    if len([event_id for event_id in event_ids if event_id is not None]) != len(set(event_id for event_id in event_ids if event_id is not None)):
        errors.append("duplicate order event identity")
    if quantity is not None and quantity <= 0: errors.append("order quantity must be positive")
    for row in available:
        kind, at, before = _kind(row), _event_at(row), state
        event_qty = _qty(row)
        if placed is not None and at is not None and at < placed: errors.append("event precedes order placement")
        if kind in {"trigger", "triggered"}:
            if state not in {"resting", "partially_filled"}: errors.append("trigger on nonworking order")
            else: state = "triggered"
        elif kind in {"amend", "amend_quantity", "replace"}:
            if state not in {"resting", "triggered", "partially_filled"}: errors.append("amend on nonworking order")
            new_quantity = dec(row.get("new_quantity", row.get("quantity")))
            new_price = dec(row.get("new_price", row.get("price")))
            if new_quantity is not None:
                if new_quantity < generation_filled: errors.append("amended quantity below cumulative fills")
                elif new_quantity <= 0: errors.append("amended quantity must be positive")
                else: authorized = new_quantity; working = new_quantity - generation_filled
            if new_price is not None: price = new_price
            if row.get("new_stop") is not None or row.get("new_target") is not None:
                stop = dec(row.get("new_stop", stop)); target = dec(row.get("new_target", target))
                bracket_versions.append({"version": len(bracket_versions), "at": at, "stop": stop, "target": target})
        elif kind in {"cancel", "canceled"}:
            if state in {"resting", "triggered", "partially_filled"}: state = "canceled"; working = Decimal(0)
            elif state not in {"canceled", "filled"}: errors.append("cancel on nonworking order")
        elif kind in {"expire", "expired"}:
            if state in {"resting", "triggered", "partially_filled"}: state = "expired"; working = Decimal(0)
            else: errors.append("expiry on nonworking order")
        elif kind in {"reopen", "new_order"}:
            new_quantity = dec(row.get("new_quantity", row.get("quantity")))
            if state not in {"canceled", "expired"} or new_quantity is None or new_quantity <= 0:
                errors.append("invalid explicit order reopen")
            else:
                # A reopened order is a new authorization; prior fills remain
                # in the position but are not charged against its quantity.
                authorized = new_quantity; generation_filled = Decimal(0); working = new_quantity; state = "resting"
                if row.get("new_price") is not None: price = dec(row["new_price"])
        elif kind in {"fill", "partial_fill"}:
            if state not in {"resting", "triggered", "partially_filled"}: errors.append("fill without valid working order")
            elif event_qty is None or event_qty <= 0: errors.append("fill quantity missing or non-positive")
            elif working is None or event_qty > working: errors.append("fill exceeds working quantity")
            else:
                filled += event_qty; generation_filled += event_qty; working -= event_qty; position += event_qty
                state = "filled" if working == 0 else "partially_filled"
        elif kind in {"exit", "exit_fill", "position_exit", "partial_exit_fill"}:
            # Exit belongs to the filled position and remains valid after
            # cancellation or expiry of the entry order.
            if event_qty is None: event_qty = position
            if event_qty is None or event_qty <= 0 or event_qty > position: errors.append("exit exceeds filled position")
            else: position -= event_qty
        elif kind in {"exit_request", "partial_exit_request", "requested_partial"}:
            pass
        else:
            missing.append("event_kind")
        timeline.append({"event_id": row.get("event_id", row.get("id")), "at": at,
                         "available_at": _at(row), "kind": kind, "state_before": before,
                         "state_after": state, "authorized_quantity": authorized,
                         "working_quantity_after": working, "position_quantity_after": position,
                         **({"quantity": event_qty} if event_qty is not None else {})})
    one_position = policy.get("one_position_at_a_time")
    source_policy_ok = True if policy and policy.get("policy_id") is not None and not policy_holes else None
    if policy and policy.get("policy_id") is None: missing.append("source_policy_id")
    if policy_holes: source_policy_ok = None
    open_positions = inp.get("other_open_positions")
    if one_position is True:
        if open_positions is None: missing.append("other_open_positions"); source_policy_ok = None
        elif int(open_positions) > 0 and position > 0: errors.append("source one-position cap violated"); source_policy_ok = False
    latest = _max_time(placement_available, *[_at(row) for row in available])
    ambiguous_fills = bool(unclocked_events or unclocked_fill_quantities)
    value = {"order_state_timeline": timeline, "remaining_quantity": None if ambiguous_fills else working,
             "filled_quantity": None if ambiguous_fills else filled,
             "position_open": None if ambiguous_fills else position > 0,
             "bracket_versions": bracket_versions,
             "lifecycle_valid": False if errors else None if ambiguous_fills or any(
                 name in missing for name in ("event_identity", "event_at", "order_id", "candidate_id",
                                              "position_id", "order_price", "quantity", "placed_at",
                                              "order_type", "side")) else True,
             "source_policy_ok": source_policy_ok, "order_state": state,
             "position_quantity": None if ambiguous_fills else position, "authorized_quantity": authorized,
             "order_id": order_id, "candidate_id": candidate_id, "position_id": position_id,
             "order_price": price, "stop": stop, "target": target,
             "decision_at": placed, "side": side, "order_at": placed,
             "stop_ticks": stop_ticks, "target_ticks": target_ticks,
             "cancel_minutes": cancel_minutes,
             "one_position_policy": one_position,
             "order_inside_ticks": dec(inp.get("order_inside_ticks", policy.get("order_inside_ticks"))),
             "pending_events": pending, "snapshot_at": as_of,
             "unclocked_events": unclocked_events,
             "unclocked_fill_quantities": unclocked_fill_quantities}
    value.update({"remaining": None if ambiguous_fills else working,
                  "filled": None if ambiguous_fills else filled, "cancel_at": cancel_at})
    if errors:
        return _result("O150", "invalid", value, base_ok=False, coverage_ok=None,
                       hole_ids=_holes("O150", ["lifecycle"]), known_at=latest, reason="; ".join(dict.fromkeys(errors)))
    missing = list(dict.fromkeys(missing))
    return _result("O150", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O150", missing), known_at=latest)


@_override("O151")
def o151(inp: dict) -> RecipeResult:
    order_id = inp.get("order_id"); side = inp.get("side"); limit = dec(inp.get("limit", inp.get("price")))
    active = inp.get("active_at", inp.get("placed_at")); cancel = inp.get("cancel_at"); expiry = inp.get("expiry_at")
    convention = inp.get("fill_convention", inp.get("modeled_fill_rule"))
    as_of = inp.get("as_of", inp.get("use_at", inp.get("known_at")))
    trades = [row for row in inp.get("trades", []) or [] if isinstance(row, dict)]
    qualifying = []
    ambiguous = False
    missing_trade_identity = any(row.get("event_id", row.get("trade_id")) is None for row in trades)
    missing_trade_availability = any(_event_at(row) is None or _at(row) is None for row in trades)
    for trade in trades:
        at = _event_at(trade); available = _at(trade)
        if at is None or available is None: continue
        if as_of is not None and available > as_of: continue
        if active is None or at < active: continue
        if at == active: ambiguous = True; continue
        if cancel is not None and at >= cancel: continue
        if expiry is not None and at >= expiry: continue
        price = dec(trade.get("price"))
        if price is not None and ((side == "buy" and price <= limit) or (side == "sell" and price >= limit)):
            qualifying.append(trade)
    first = min(qualifying, key=lambda row: _event_at(row)) if qualifying else None
    actual_reports = [row for row in inp.get("fill_reports", []) or [] if row.get("order_id") == order_id]
    if inp.get("fill_report") is not None:
        actual_reports.append(inp["fill_report"] if isinstance(inp["fill_report"], dict) else {"at": inp.get("actual_fill_at")})
    actual_at = min((_at(row) for row in actual_reports if _at(row) is not None), default=None)
    actual_quantity = sum((_qty(row, filled_only=True) or Decimal(0) for row in actual_reports), Decimal(0)) if actual_reports else None
    queue_flags = ([inp.get("queue_evidence")] if type(inp.get("queue_evidence")) is bool else []) + [
        row.get("queue_verified") for row in actual_reports if type(row.get("queue_verified")) is bool
    ]
    queue = True if any(flag is True for flag in queue_flags) else False if queue_flags and all(flag is False for flag in queue_flags) else None
    policy, policy_holes = _source_policy(inp, "O151")
    other_position = inp.get("other_position_open")
    eligibility = None if ambiguous and first is None else first is not None
    missing = list(policy_holes)
    for name, value in (("order_id", order_id), ("side", side), ("limit", limit), ("active_at", active),
                        ("fill_convention", convention)):
        if value is None: missing.append(name)
    if policy.get("one_position_at_a_time") is True:
        if other_position is None: missing.append("one_position_state"); eligibility = None
        elif other_position: eligibility = False
    if ambiguous and first is None: missing.append("same_key_order")
    if missing_trade_identity: missing.append("trade_identity")
    if missing_trade_availability: missing.append("trade_availability")
    if queue is None: missing.append("queue_evidence")
    report_ids = [row.get("fill_id", row.get("event_id", row.get("id"))) for row in actual_reports]
    if actual_reports and any(value is None for value in report_ids): missing.append("fill_report_identity")
    errors = []
    if side not in {None, "buy", "sell"}: errors.append("invalid passive side")
    if actual_at is not None and ((cancel is not None and actual_at >= cancel) or (expiry is not None and actual_at >= expiry)):
        errors.append("actual fill report occurs after cancellation or expiry")
    value = {"first_modeled_fill_at": _event_at(first) if first else None,
             "modeled_fill_rule": convention, "actual_fill_at": actual_at,
             "actual_fill_quantity": actual_quantity,
             "queue_verified": queue, "fill_eligibility": eligibility,
             "actual_fill_unknown": not actual_reports, "order_id": order_id}
    value.update({"modeled_fill_at": value["first_modeled_fill_at"],
                  "actual_unknown": value["actual_fill_unknown"]})
    if errors:
        return _result("O151", "invalid", value, base_ok=False, coverage_ok=None,
                       known_at=_max_time(_at(first) if first else None, actual_at), reason="; ".join(errors))
    return _result("O151", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O151", missing), known_at=_max_time(_at(first) if first else None, actual_at))


@_override("O152")
def o152(inp: dict) -> RecipeResult:
    cost_ticks = dec(inp.get("trade_cost_ticks", inp.get("round_trip_cost_ticks")))
    stop_slippage = dec(inp.get("stop_slippage_ticks"))
    tick_value = dec(inp.get("tick_value")); qty = dec(inp.get("quantity"))
    currency = None if None in (cost_ticks, tick_value, qty) else cost_ticks * tick_value * qty
    gross_target = dec(inp.get("gross_target_ticks")); gross_stop = dec(inp.get("gross_stop_ticks"))
    target_outcome = dec(inp.get("target_outcome")); stop_outcome = dec(inp.get("stop_outcome"))
    expected_target = None if None in (gross_target, cost_ticks) else gross_target - cost_ticks
    expected_stop = None if None in (gross_stop, cost_ticks, stop_slippage) else -(gross_stop + cost_ticks + stop_slippage)
    consistency_checks = []
    if target_outcome is not None and expected_target is not None: consistency_checks.append(target_outcome == expected_target)
    if stop_outcome is not None and expected_stop is not None: consistency_checks.append(stop_outcome == expected_stop)
    consistent = None if not consistency_checks else all(consistency_checks)
    r_unit = dec(inp.get("r_unit", gross_stop))
    account_fees = deepcopy(inp.get("account_fees", []))
    fees_separate = inp.get("account_fees_separate")
    missing = []
    if cost_ticks is None: missing.append("trade_cost_ticks")
    if stop_slippage is None: missing.append("stop_slippage_ticks")
    if currency is None: missing.append("tick_value_or_quantity")
    if fees_separate is None: missing.append("account_fees_policy")
    errors = []
    if any(value is not None and value < 0 for value in (cost_ticks, stop_slippage, tick_value, qty)): errors.append("negative cost unit")
    if consistent is False: errors.append("supplied gross/net arithmetic is inconsistent")
    if fees_separate is False: errors.append("account fees were allocated per trade without source policy")
    value = {"trade_cost_ticks": cost_ticks, "stop_slippage_ticks": stop_slippage,
             "currency_cost": currency, "supplied_gross_net_consistency": consistent,
             "account_fees_separate": fees_separate, "account_fee_ledger": account_fees,
             "target_r": target_outcome / r_unit if target_outcome is not None and r_unit else None,
             "stop_r": stop_outcome / r_unit if stop_outcome is not None and r_unit else None,
             "round_trip_cost": currency}
    if errors:
        return _result("O152", "invalid", value, base_ok=False, coverage_ok=None,
                       known_at=inp.get("known_at"), reason="; ".join(errors))
    return _result("O152", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O152", missing), known_at=inp.get("known_at"))


@_override("O155")
def o155(inp: dict) -> RecipeResult:
    e0, baseline = dec(inp.get("E0")), dec(inp.get("B")); stage = inp.get("risk_stage", inp.get("printed_stage"))
    decision_at = inp.get("decision_at"); validated = inp.get("validated_process")
    prior = [row for row in inp.get("prior_results", []) or [] if isinstance(row, dict)]
    stage_map = {"first": (Decimal(1), Decimal(3), "second_after_win"),
                 "second": (Decimal(4), Decimal(12), None),
                 "reset_after_second_win": (Decimal(1), Decimal(3), "first")}
    printed = stage_map.get(stage)
    risk_units = printed[0] if printed else None; reward_units = printed[1] if printed else None
    cumulative = sum((dec(row.get("baseline_units", row.get("result_units"))) or Decimal(0) for row in prior), Decimal(0))
    holes, errors = [], []
    if e0 is None or baseline is None: holes.append("baseline")
    elif e0 <= 0 or baseline <= 0 or baseline / e0 > Decimal("0.01"): errors.append("baseline unit must be positive and no more than one percent of E0")
    if validated is not True: (errors if validated is False else holes).append("validated_process")
    if printed is None: holes.append("printed_stage")
    known_prior = [row for row in prior if _at(row) is not None and (decision_at is None or _at(row) < decision_at)]
    if len(known_prior) != len(prior): errors.append("risk stage uses unresolved or future prior result")
    if stage == "second":
        if len(known_prior) != 1 or dec(known_prior[0].get("baseline_units", known_prior[0].get("result_units"))) != Decimal(3):
            errors.append("second stage requires one closed +3B first win")
    next_stage = None
    if stage == "second" and prior:
        latest = dec(prior[-1].get("baseline_units", prior[-1].get("result_units")))
        if latest == Decimal(12): next_stage = "first"
        elif latest == Decimal(-4): holes.append("second_loss_next")
    if stage == "reset_after_second_win":
        if [dec(row.get("baseline_units", row.get("result_units"))) for row in prior[-2:]] != [Decimal(3), Decimal(12)]:
            errors.append("printed reset requires first +3B and second +12B")
        else: next_stage = "first"
    holes.extend(["activation", "rebase"])
    value = {"printed_stage": stage, "planned_risk_units": risk_units,
             "planned_reward_units": reward_units, "cumulative_baseline_units": cumulative,
             "next_stage": next_stage, "activation_holes": _holes("O155", holes),
             "fixed_baseline_equity": e0, "fixed_baseline_unit": baseline,
             "prior_results": deepcopy(prior), "decision_at": decision_at,
             "next_risk_units": (stage_map[next_stage][0] if next_stage in stage_map else None),
             "first_trade_closed": bool(prior) and _at(prior[0]) is not None,
             "first_trade_result_units": dec(prior[0].get("baseline_units", prior[0].get("result_units"))) if prior else None,
             "first_trade_close_at": _at(prior[0]) if prior else None,
             "second_trade_result_units": dec(prior[1].get("baseline_units", prior[1].get("result_units"))) if len(prior)>1 else None,
             "planned_risk_money": risk_units * baseline if None not in (risk_units, baseline) else None,
             "planned_reward_money": reward_units * baseline if None not in (reward_units, baseline) else None}
    first_win = baseline * 3 if baseline is not None else None
    second_risk = baseline * 4 if baseline is not None else None
    second_target = baseline * 12 if baseline is not None else None
    alternative = None if baseline is None or e0 is None or inp.get("alt_pct") is None else dec(inp["alt_pct"]) * (e0 + first_win)
    value.update({"base_risk_fraction": baseline / e0 if e0 and baseline is not None else None,
                  "first_win": first_win, "second_risk": second_risk,
                  "second_target": second_target,
                  "net_second_loss": first_win - second_risk if None not in (first_win, second_risk) else None,
                  "net_second_win": first_win + second_target if None not in (first_win, second_target) else None,
                  "next_risk": baseline, "alt_not_printed": None if alternative is None else alternative != second_risk,
                  "activation": None, "entry_created": False, "profitability_asserted": False})
    supplied_risk = dec(inp.get("risk_units")); supplied_reward = dec(inp.get("planned_reward_r"))
    if stage == "second" and ((supplied_risk is not None and supplied_risk != Decimal(4))
                              or (supplied_reward is not None and supplied_reward != Decimal(3))):
        return _result("O155", "invalid", value, base_ok=False, coverage_ok=None,
                       known_at=inp.get("known_at"), reason="supplied sizing is not the printed fixed-baseline stage")
    if stage == "reset_after_second_win" and inp.get("second_trade_result_units") is None:
        return _result("O155", "hole", value, base_ok=None, coverage_ok=None,
                       hole_ids=["HOLE:O155:second_loss_next"], known_at=inp.get("known_at"),
                       reason="the next state after a second loss is unpublished")
    if errors:
        return _result("O155", "invalid", value, base_ok=False, coverage_ok=None,
                       known_at=_max_time(*[_at(row) for row in prior]), reason="; ".join(errors))
    return _result("O155", "computed" if not holes else "hole", value, base_ok=None,
                   coverage_ok=None, hole_ids=_holes("O155", holes), known_at=_max_time(*[_at(row) for row in prior]))


@_override("O156")
def o156(inp: dict) -> RecipeResult:
    per_r = dec(inp.get("currency_per_r")); target = dec(inp.get("target"))
    drawdown = dec(inp.get("drawdown"))
    daily_r = dec(inp.get("daily_r"))
    paths, pass_n = inp.get("paths"), inp.get("pass_n")
    rate = None
    errors, missing = [], []
    if inp.get("scenario_id") is None: missing.append("scenario_id")
    if per_r is None: missing.append("currency_per_r")
    elif per_r <= 0: errors.append("currency per R must be positive")
    if paths is not None or pass_n is not None:
        if type(paths) is not int or paths <= 0 or type(pass_n) is not int or not 0 <= pass_n <= paths:
            errors.append("invalid supplied path counts")
        else: rate = Decimal(pass_n) / Decimal(paths)
    else: rate = dec(inp.get("reported_pass_rate", inp.get("rounded_pct")))
    for name in ("path_design", "trailing_drawdown_rule", "consistency_rule"):
        if inp.get(name) is None: missing.append(name)
    causal = inp.get("source_causal_status", inp.get("later_ofm_causal_status"))
    if causal is None: missing.append("source_causal_status")
    elif causal not in {"corrected", "negative", "causal"}: errors.append("source cohort still contains the uncorrected causal entry error")
    assumptions = {"currency_per_r": per_r, "target_currency": target,
                   "trailing_drawdown_currency": drawdown, "daily_stop_r": daily_r,
                   "path_count": paths, "consistency_rule": inp.get("consistency_rule"),
                   "path_design": inp.get("path_design")}
    value = {"scenario_id": inp.get("scenario_id"), "assumptions": assumptions,
             "reported_pass_rate": rate, "reported_time_to_pass": inp.get("reported_time_to_pass"),
             "source_causal_status": causal, "missing_path_rules": _holes("O156", missing),
             "target_r": target / per_r if target is not None and per_r and per_r > 0 else None,
             "drawdown_r": drawdown / per_r if drawdown is not None and per_r and per_r > 0 else None,
             "daily_stop_currency": daily_r * per_r if daily_r is not None and per_r is not None else None,
             "reconstruct_from_rounded": False, "simulation_run": False}
    value.update({"path_rate": rate})
    if errors:
        return _result("O156", "invalid", value, base_ok=False, coverage_ok=None,
                       known_at=inp.get("known_at"), reason="; ".join(errors))
    return _result("O156", "supplied" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O156", missing), known_at=inp.get("known_at"))


STATE_MEANINGS = {
    "B": ("two_sided_executions", "recent_revisits", "low_aggression_both_sides"),
    "A": ("high_aggression", "low_response_efficiency", "opposite_liquidity_holds_and_refills"),
    "D": ("aggression", "efficient_displacement"),
    "E": ("prior_absorption_or_effort", "replenishment_stops", "level_gives_way"),
    "W": ("cancellations_dominate",),
}


@_override("O165")
def o165(inp: dict) -> RecipeResult:
    label = inp.get("state_label", inp.get("state")); state_at = inp.get("state_at")
    instrument = inp.get("instrument_id", inp.get("source_symbol")); observation_id = inp.get("observation_id", inp.get("source_observation_id"))
    required_depth = inp.get("required_depth_levels"); depth = inp.get("depth_levels", inp.get("depth_coverage"))
    evidence = inp.get("evidence", []) or []
    criteria = inp.get("criteria", []) or []
    if not criteria and label in STATE_MEANINGS:
        criteria = [{"criterion": name, "observed": inp.get(name),
                     "known_at": (inp.get("criteria_known_at") or {}).get(name, inp.get("known_at"))}
                    for name in STATE_MEANINGS[label]]
    missing, errors = [], []
    if label not in STATES: errors.append("unknown state label")
    if state_at is None: missing.append("state_at")
    if instrument is None: missing.append("instrument")
    if observation_id is None: missing.append("observation_id")
    if type(required_depth) is not int or required_depth < 1: missing.append("required_depth_levels")
    if type(depth) is not int or (type(required_depth) is int and depth < required_depth): missing.append("depth_coverage")
    failed = []
    criterion_names = {row.get("criterion", row.get("name")) for row in criteria}
    if label in STATE_MEANINGS:
        missing.extend(name for name in STATE_MEANINGS[label] if name not in criterion_names)
    for criterion in criteria:
        name = criterion.get("criterion", criterion.get("name"))
        observed = criterion.get("observed")
        at = _at(criterion)
        if name is None or observed is None or at is None: missing.append(str(name or "criterion"))
        elif type(observed) is not bool: errors.append(f"criterion {name} is not Boolean")
        elif observed is False: failed.append(name)
        if at is not None and state_at is not None and at > state_at: errors.append(f"criterion {name} uses future evidence")
        if criterion.get("instrument_id", instrument) != instrument: errors.append(f"criterion {name} instrument mismatch")
    evidence_ids = [row.get("evidence_id", row.get("id")) for row in evidence]
    if not evidence: missing.append("evidence")
    if evidence and (None in evidence_ids or len(evidence_ids) != len(set(evidence_ids))): errors.append("evidence identities absent or duplicated")
    complete = None if missing else not failed
    value = {"state_label": label, "state_evidence_complete": complete,
             "automatic_state": None, "missing_criteria": list(dict.fromkeys(missing)),
             "failed_criteria": failed, "state_at": state_at,
             "instrument_id": instrument, "observation_id": observation_id,
             "required_depth_levels": required_depth, "depth_levels": depth,
             "criteria_ledger": deepcopy(criteria), "evidence_ids": evidence_ids}
    if errors:
        return _result("O165", "invalid", value, base_ok=False, coverage_ok=None,
                       known_at=_max_time(*[_at(row) for row in criteria + evidence]), reason="; ".join(errors))
    return _result("O165", "supplied" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O165", missing), known_at=_max_time(state_at, *[_at(row) for row in criteria + evidence]))


@_override("O166")
def o166(inp: dict) -> RecipeResult:
    counts = inp.get("counts")
    errors, missing = [], []
    probabilities = {state: None for state in STATES}; total = None
    if counts is not None:
        if not isinstance(counts, dict) or set(counts) != set(STATES) or any(type(v) is not int or v < 0 for v in counts.values()):
            errors.append("counts must be one complete non-negative integer state row")
        else:
            total = sum(counts.values())
            probabilities = {state: None if total == 0 else Decimal(counts[state]) / Decimal(total) for state in STATES}
            supplied_total = inp.get("row_count", inp.get("supplied_row_count"))
            if supplied_total is not None and supplied_total != total: errors.append("supplied row total does not reconcile")
    current = deepcopy(inp.get("current_observation", inp.get("current_state_record", {})))
    nxt = deepcopy(inp.get("next_observation", inp.get("next_state_record", {})))
    if not current and any(inp.get(key) is not None for key in ("from_state", "state_at", "current_state_id")):
        current = {"state_label": inp.get("from_state"), "state_at": inp.get("state_at"),
                   "state_id": inp.get("current_state_id"), "known_at": inp.get("current_known_at"),
                   "sequence": inp.get("current_sequence"), "instrument_id": inp.get("source_symbol"),
                   "cohort_id": inp.get("cohort_id"), "reset_id": inp.get("reset_id")}
    if not nxt and any(inp.get(key) is not None for key in ("to_state", "next_state_at", "next_state_id")):
        nxt = {"state_label": inp.get("to_state"), "state_at": inp.get("next_state_at"),
               "state_id": inp.get("next_state_id"), "known_at": inp.get("next_known_at"),
               "sequence": inp.get("next_sequence"), "instrument_id": inp.get("source_symbol"),
               "cohort_id": inp.get("cohort_id"), "reset_id": inp.get("reset_id")}
    cadence = inp.get("cadence", inp.get("next_observation_definition"))
    if cadence == "" or cadence == {}:
        cadence = None
    conditioning = inp.get("conditioning_evidence", inp.get("conditioning", [])) or []
    from_state = current.get("state_label", current.get("state")); to_state = nxt.get("state_label", nxt.get("state"))
    state_at = current.get("state_at", current.get("at")); next_at = nxt.get("state_at", nxt.get("at"))
    cseq = current.get("sequence"); nseq = nxt.get("sequence")
    for name, value in (("current_observation", current or None), ("next_observation", nxt or None),
                        ("next_observation_definition", cadence)):
        if value is None: missing.append(name)
    for name, value in (("current_state_id", current.get("state_id", current.get("id"))),
                        ("next_state_id", nxt.get("state_id", nxt.get("id"))),
                        ("state_at", state_at), ("next_state_at", next_at),
                        ("current_known_at", _at(current)), ("next_known_at", _at(nxt)),
                        ("current_sequence", cseq), ("next_sequence", nseq)):
        if value is None: missing.append(name)
    if from_state not in STATES and from_state is not None: errors.append("invalid from state")
    if to_state not in STATES and to_state is not None: errors.append("invalid to state")
    if None not in (state_at, next_at) and not state_at < next_at: errors.append("next state does not follow current state")
    if None not in (cseq, nseq) and nseq != cseq + 1: errors.append("state observations are not adjacent")
    for key in ("instrument_id", "cohort_id", "reset_id"):
        if current.get(key) is None or nxt.get(key) is None: missing.append(key)
        elif current[key] != nxt[key]: errors.append(f"transition crosses {key} boundary")
    conditioning_causal = None
    if state_at is not None and conditioning:
        times = [_at(row) for row in conditioning]
        evidence_ids = [row.get("evidence_id", row.get("id")) for row in conditioning]
        if any(value is None for value in evidence_ids): missing.append("conditioning_identity")
        elif len(evidence_ids) != len(set(evidence_ids)): errors.append("duplicate conditioning evidence identity")
        if any(at is None for at in times): missing.append("conditioning_availability")
        else: conditioning_causal = all(at <= state_at for at in times)
    elif not conditioning: missing.append("conditioning_evidence")
    if conditioning_causal is False: errors.append("conditioning uses future evidence")
    source_counts_symbol = inp.get("source_counts_symbol")
    observation_symbol = current.get("instrument_id", inp.get("source_symbol"))
    if counts is not None:
        if source_counts_symbol is None: missing.append("source_counts_symbol")
        elif observation_symbol is not None and source_counts_symbol != observation_symbol: errors.append("count instrument does not match transition cohort")
    actual_complete = not any(name in missing for name in (
        "current_observation", "next_observation", "next_observation_definition", "current_state_id",
        "next_state_id", "state_at", "next_state_at", "current_known_at", "next_known_at",
        "current_sequence", "next_sequence",
        "instrument_id", "cohort_id", "reset_id", "conditioning_evidence", "conditioning_availability"))
    transition_valid = False if errors else True if actual_complete and conditioning_causal is True else None
    known_at = _max_time(_at(current), _at(nxt), *[_at(row) for row in conditioning])
    reported = inp.get("reported_probability")
    if reported is None and from_state is not None and to_state is not None and probabilities.get(to_state) is not None:
        reported = probabilities[to_state]
    value = {"from_state": from_state, "to_state": to_state, "state_at": state_at,
             "next_state_at": next_at, "conditioning_causal": conditioning_causal,
             "transition_valid": transition_valid, "supplied_row_count": total,
             "reported_probability": reported, "probabilities": probabilities,
             "row_sum": None if total in {None, 0} else sum(probabilities.values(), Decimal(0)),
             "cadence": deepcopy(cadence), "current_observation": current or None,
             "next_observation": nxt or None, "conditioning_evidence": deepcopy(conditioning),
             "max_conditioning_known_at": _max_time(*[_at(row) for row in conditioning]),
             "automatic_transition": None, "trained_matrix": False}
    value.update({"p_dd": probabilities.get("D"), "p_da": probabilities.get("A")})
    if errors:
        return _result("O166", "invalid", value, base_ok=False, coverage_ok=None,
                       hole_ids=_holes("O166", ["transition"]), known_at=known_at, reason="; ".join(errors))
    missing = list(dict.fromkeys(missing))
    return _result("O166", "computed" if not missing else "hole", value,
                   base_ok=True if not missing else None, coverage_ok=True if not missing else None,
                   hole_ids=_holes("O166", missing), known_at=known_at,
                   reason=None if not missing else "actual adjacent transition evidence is incomplete")


REGISTRATION_OVERRIDES: dict[str, Callable[[dict], RecipeResult]] = {
    rid: globals()[rid.lower()] for rid in LIFECYCLE_SCHEMAS
}


class LifecycleDerivationError(ValueError):
    """A lifecycle object cannot be reconstructed from its declared parents."""


_STRUCTURE_IDS = {
    "O002", "O020", "O026", "O028", "O047", "O048", "O051", "O052",
    "O054", "O055", "O056", "O057", "O060", "O064", "O066", "O068",
    "O071", "O072", "O076", "O080", "O086", "O087", "O089", "O090",
    "O091", "O092", "O093", "O094", "O095", "O096", "O101", "O104",
    "O115", "O116", "O118", "O119",
}
_BRANCH_IDS = {f"O{number:03}" for number in range(121, 137)}
_FLOW_IDS = {f"O{number:03}" for number in range(98, 121)}
_OBSERVATION_IDS = _STRUCTURE_IDS | _BRANCH_IDS | _FLOW_IDS


# A plural role contains an ordered list of object IDs.  Every actual parent
# must appear in exactly one role, which prevents an unselected parent from
# leaking into a ledger or a state transition.
DERIVED_PARENT_ROLES: dict[str, dict[str, set[str]]] = {
    "O138": {"definition": {"O137"}, "condition_events": _OBSERVATION_IDS | {"O029"}},
    "O139": {"entry": {"O150"}, "structure": _STRUCTURE_IDS},
    "O140": {"risk": {"O139"}, "position": {"O150"}, "definition": {"O137"}},
    "O141": {"entry": {"O150"}, "objective": _STRUCTURE_IDS, "outcome_tape": {"O098"}},
    "O142": {"position": {"O150"}, "definition": {"O137"}, "protected_structure": {"O143"}},
    "O143": {"position": {"O150"}, "structure": _STRUCTURE_IDS},
    "O144": {"prior_position": {"O150"}, "thesis": {"O138"}, "fresh_branch": _BRANCH_IDS, "daily_risk": {"O145"}},
    "O147": {"es_object": _STRUCTURE_IDS, "nq_object": _STRUCTURE_IDS,
             "ym_object": _STRUCTURE_IDS, "es_first_use": _OBSERVATION_IDS,
             "nq_first_use": _OBSERVATION_IDS, "ym_first_use": _OBSERVATION_IDS},
    "O148": {"definition": {"O137"}, "candidates": _BRANCH_IDS, "orders": {"O150"}},
    "O149": {"definition": {"O137"}, "features": _OBSERVATION_IDS, "order": {"O150"}},
    "O150": {"definition": {"O137"}, "instruction_ledger": {"O148"},
             "fills": {"O151"}, "position_actions": {"O142"}},
    "O151": {"order": {"O150"}, "trades": {"O098"}},
    "O152": {"definition": {"O137"}, "orders": {"O150"}},
    "O155": {"definition": {"O137"}, "closed_results": {"O150", "O153", "O154"}},
    "O156": {"cohort": {"O148"}, "grade": {"O149"}, "costs": {"O152"}},
    "O165": {"participation": {"O098", "O103", "O105", "O106", "O107", "O111"},
             "response": {"O101", "O104", "O113", "O115"},
             "depth": {"O100", "O102", "O112", "O114"}},
    "O166": {"current_state": {"O165"}, "next_state": {"O165"},
             "conditioning": _FLOW_IDS},
}

_PLURAL_PARENT_ROLES = {
    ("O138", "condition_events"), ("O148", "candidates"), ("O148", "orders"),
    ("O149", "features"), ("O150", "fills"), ("O150", "position_actions"),
    ("O152", "orders"), ("O155", "closed_results"), ("O166", "conditioning"),
}


def _derived_roles(recipe_id: str, config: dict, parents: list[dict]) -> dict[str, Any]:
    selected = config.get("parent_roles")
    required = DERIVED_PARENT_ROLES[recipe_id]
    if not isinstance(selected, dict) or set(selected) != set(required):
        raise LifecycleDerivationError(
            f"{recipe_id} requires exact semantic parent_roles {sorted(required)}"
        )
    index = {str(parent.get("object_id")): parent for parent in parents}
    if len(index) != len(parents) or None in {parent.get("object_id") for parent in parents}:
        raise LifecycleDerivationError("parent object identities are absent or duplicated")
    used: list[str] = []
    roles: dict[str, Any] = {}
    for role, allowed in required.items():
        plural = (recipe_id, role) in _PLURAL_PARENT_ROLES
        raw = selected[role]
        ids = raw if plural else [raw]
        if not isinstance(ids, list) or (not plural and len(ids) != 1):
            raise LifecycleDerivationError(f"{role} must select {'a list of' if plural else 'one'} actual parent IDs")
        if plural and not ids:
            raise LifecycleDerivationError(f"{role} must select at least one actual parent")
        if len({str(item) for item in ids}) != len(ids):
            raise LifecycleDerivationError(f"{role} repeats a parent identity")
        matches = []
        for object_id in ids:
            parent = index.get(str(object_id))
            if parent is None:
                raise LifecycleDerivationError(f"{role} selects an absent parent")
            if parent.get("recipe_id") not in allowed:
                raise LifecycleDerivationError(f"{role} parent has the wrong producer identity")
            if parent.get("state") == "invalid" or parent.get("recipe_base_ok") is False:
                raise LifecycleDerivationError(f"{role} parent is invalid")
            matches.append(parent)
            used.append(str(object_id))
        roles[role] = matches if plural else matches[0]
    if len(used) != len(set(used)) or set(used) != set(index):
        raise LifecycleDerivationError("semantic parent roles must cover each actual parent exactly once")
    return roles


def _parent_value(parent: dict, *fields: str) -> Any:
    value = parent.get("value", {})
    for field in fields:
        if isinstance(value, dict) and field in value and value[field] is not None:
            return deepcopy(value[field])
    return None


def _parent_time(parent: dict, *fields: str) -> int | None:
    value = _parent_value(parent, *fields)
    return value if type(value) is int else parent.get("known_at")


def _parent_bounds(parent: dict) -> list[Any] | None:
    value = parent.get("value", {})
    for field in ("bounds", "band", "zone", "balance_band", "dealing_band",
                  "rejection_band", "origin_band", "hvn_band", "shelf_band"):
        candidate = value.get(field)
        if isinstance(candidate, (list, tuple)) and len(candidate) == 2:
            return [deepcopy(candidate[0]), deepcopy(candidate[1])]
    lo = _parent_value(parent, "L", "low", "box_low", "prior_low", "micro_low", "val")
    hi = _parent_value(parent, "H", "high", "box_high", "prior_high", "micro_high", "vah")
    return [lo, hi] if lo is not None and hi is not None else None


def _policy_from_definition(parent: dict, config: dict, key: str = "source_policy") -> dict | None:
    requested = config.get(key)
    definition = _parent_value(parent, "definition", "process_definition")
    if requested is None and isinstance(definition, dict):
        requested = definition.get(key)
    if requested is not None and not isinstance(requested, dict):
        raise LifecycleDerivationError(f"{key} must be a scoped source definition")
    return deepcopy(requested)


def _position_exit_at(position: dict) -> int | None:
    timeline = _parent_value(position, "order_state_timeline") or []
    exits = [row.get("at") for row in timeline
             if row.get("kind") in {"exit", "exit_fill", "position_exit", "partial_exit_fill"}
             and row.get("position_quantity_after") == 0 and type(row.get("at")) is int]
    return min(exits) if exits else None


def _derive_lifecycle(recipe_id: str, config: dict, parents: list[dict]) -> RecipeResult:
    try:
        role = _derived_roles(recipe_id, config, parents)
        inp: dict[str, Any]
        if recipe_id == "O138":
            definition = role["definition"]
            conditions = deepcopy(config.get("death_conditions"))
            if not isinstance(conditions, list) or not conditions:
                raise LifecycleDerivationError("death_conditions must declare each condition and parent_id")
            event_index = {str(parent["object_id"]): parent for parent in role["condition_events"]}
            if {str(row.get("parent_id")) for row in conditions} != set(event_index):
                raise LifecycleDerivationError("death condition declarations must select every event parent exactly once")
            events = []
            normalized = []
            for condition in conditions:
                item = deepcopy(condition)
                parent = event_index[str(item.pop("parent_id"))]
                field = item.pop("parent_field", None)
                if not isinstance(field, str) or field not in parent.get("value", {}):
                    raise LifecycleDerivationError("each death condition needs an actual parent output field")
                observed = _parent_value(parent, field)
                event = {"condition_id": item.get("condition_id"), "at": parent.get("known_at"),
                         "coverage_complete": parent.get("recipe_coverage_ok")}
                event["result" if type(observed) is bool else "value"] = observed
                item["producer_id"] = parent["recipe_id"]
                normalized.append(item); events.append(event)
            inp = {"thesis_id": config.get("thesis_id"), "declared_at": _parent_time(definition, "frozen_at"),
                   "decision_at": config.get("decision_at"), "death_conditions": normalized,
                   "events": events, "replacement_id": config.get("replacement_id"),
                   "replacement_at": config.get("replacement_at")}
        elif recipe_id == "O139":
            entry, structure = role["entry"], role["structure"]
            side = _parent_value(entry, "side")
            bounds = _parent_bounds(structure)
            structure_value = structure.get("value", {})
            selected_field = next((field for field in ("selected_stop", "structural_stop", "stop", "extreme")
                                   if isinstance(structure_value, dict) and structure_value.get(field) is not None), None)
            stop = deepcopy(structure_value[selected_field]) if selected_field is not None else None
            if stop is None and bounds is not None and side in {"long", "short"}:
                stop = bounds[0] if side == "long" else bounds[1]
                selected_field = "bounds.low" if side == "long" else "bounds.high"
            invalidation_ref = {"object_id": structure["object_id"], "recipe_id": structure["recipe_id"],
                                "field": selected_field, "value": stop, "known_at": structure.get("known_at")}
            planned_stop = _parent_value(entry, "planned_stop", "stop")
            inp = {"entry": _parent_value(entry, "order_price", "entry"), "stop": stop if planned_stop is None else planned_stop,
                   "side": side, "q": config.get("q"), "candidate_id": _parent_value(entry, "candidate_id"),
                   "controlling_structure_id": structure["object_id"],
                   "invalidation_ref": invalidation_ref,
                   "structure_confirmed_at": structure.get("known_at"),
                   "stop_policy": deepcopy(config.get("stop_policy")),
                   "planned_stop_method": deepcopy(config.get("stop_method")),
                   "policy_selected_at": config.get("policy_selected_at"),
                   "decision_at": _parent_time(entry, "decision_at", "order_at"),
                   "provenance": "actual_order"}
        elif recipe_id == "O140":
            risk, position, definition = role["risk"], role["position"], role["definition"]
            policy = _policy_from_definition(definition, config)
            inp = {"stop_distance_points": _parent_value(risk, "stop_distance_points"),
                   "stop_distance_ticks": _parent_value(risk, "stop_distance_ticks"),
                   "multiplier": config.get("multiplier"), "tick_value": config.get("tick_value"),
                   "quantity": _parent_value(position, "authorized_quantity", "position_quantity", "filled_quantity"),
                   "source_policy": policy, "included_costs": config.get("included_costs", 0),
                   "included_reserves": config.get("included_reserves", 0),
                   "existing_exposure": config.get("existing_exposure", 0),
                   "known_at": _max_time(risk.get("known_at"), position.get("known_at"), definition.get("known_at"))}
        elif recipe_id == "O141":
            entry, objective, tape = role["entry"], role["objective"], role["outcome_tape"]
            bounds = _parent_bounds(objective)
            side = _parent_value(entry, "side")
            target = _parent_value(objective, "target", "price", "poc", "selected_edge", "reward_price")
            if target is None and bounds is not None and side in {"long", "short"}:
                target = bounds[1] if side == "long" else bounds[0]
            records = _parent_value(tape, "event_records") or []
            inp = {"objective": {"objective_id": objective["object_id"], "type": objective["recipe_id"],
                                 "price": target, "known_at": objective.get("known_at"),
                                 "active_at_selection": _parent_value(objective, "active_at_decision", "remaining_objective")},
                   "entry_id": _parent_value(entry, "order_id", "candidate_id"), "side": side,
                   "entry": _parent_value(entry, "order_price", "entry"), "selected_at": config.get("selected_at"),
                   "decision_at": _parent_time(entry, "decision_at", "order_at"),
                   "prints": [{"price": row.get("price"), "at": row.get("event_at", row.get("at")),
                               "known_at": row.get("available_at", row.get("known_at"))} for row in records],
                   "outcome_coverage_complete": tape.get("recipe_coverage_ok")}
        elif recipe_id == "O142":
            position, definition, protected = role["position"], role["definition"], role["protected_structure"]
            actions = deepcopy(_parent_value(position, "order_state_timeline") or [])
            protected_at = _parent_value(protected, "protected_known_at", "confirmation_at")
            for action in actions:
                if action.get("kind") in {"trail", "stop_amend", "breakeven"}:
                    action["protected_known_at"] = protected_at
            brackets = _parent_value(position, "bracket_versions") or []
            first = brackets[0] if brackets else {}
            entry_at = _parent_time(position, "decision_at", "order_at")
            initial_stop = first.get("stop"); entry_price = _parent_value(position, "order_price")
            inp = {"entry_id": _parent_value(position, "order_id"), "entry_at": entry_at,
                   "initial_quantity": _parent_value(position, "filled_quantity", "authorized_quantity"),
                   "initial_stop": initial_stop, "initial_target": first.get("target"),
                   "initial_risk": abs(dec(entry_price) - dec(initial_stop)) if None not in (entry_price, initial_stop) else None,
                   "source_policy": _policy_from_definition(definition, config),
                   "policy_frozen_at": _parent_time(definition, "frozen_at"), "actions": actions}
        elif recipe_id == "O143":
            position, structure = role["position"], role["structure"]
            quantity = _parent_value(position, "position_quantity")
            if quantity is None or dec(quantity) <= 0:
                raise LifecycleDerivationError("protected structure requires an actually open parent position")
            position_side = _parent_value(position, "side")
            side = "low" if position_side == "long" else "high" if position_side == "short" else position_side
            bounds = _parent_bounds(structure)
            protected = _parent_value(structure, "protected_price", "swing_mid", "extreme")
            if protected is None and bounds is not None and side in {"low", "high"}:
                protected = bounds[0] if side == "low" else bounds[1]
            inp = {"protected_price": protected, "side": side,
                   "price_at": structure.get("known_at"), "confirmation_at": structure.get("known_at"),
                   "protected_known_at": structure.get("known_at"),
                   "entry_at": _parent_time(position, "decision_at", "order_at"),
                   "break_at": config.get("break_at"), "decision_at": config.get("decision_at"),
                   "band_id": structure["object_id"],
                   "position_id": _parent_value(position, "position_id"),
                   "bracket_versions": _parent_value(position, "bracket_versions"),
                   "actual_quantity": quantity}
        elif recipe_id == "O144":
            position, thesis, branch, daily = (role[name] for name in ("prior_position", "thesis", "fresh_branch", "daily_risk"))
            exit_at = _position_exit_at(position)
            if exit_at is None:
                raise LifecycleDerivationError("re-entry requires an actual zero-quantity parent exit")
            inp = {"parent_entry_id": _parent_value(position, "order_id"),
                   "parent_position_id": _parent_value(position, "position_id"),
                   "parent_exit_id": config.get("parent_exit_id"), "parent_exit_at": exit_at,
                   "new_candidate_id": config.get("new_candidate_id", branch["object_id"]),
                   "parent_thesis_id": config.get("parent_thesis_id"), "new_thesis_id": config.get("new_thesis_id"),
                   "parent_band_id": config.get("parent_band_id"), "new_band_id": config.get("new_band_id"),
                   "thesis_state": _parent_value(thesis, "state"),
                   "return_at": config.get("return_at"),
                   "fresh_confirmation_at": branch.get("known_at"), "decision_at": config.get("decision_at"),
                   "full_branch_verdict": _parent_value(branch, "branch_ok", "qualification", "qualifies", "case_ok"),
                   "account_permission": _parent_value(daily, "entry_permission"),
                   "risk_state_known_at": daily.get("known_at"),
                   "bracket_versions": _parent_value(position, "bracket_versions"),
                   "actual_quantity": _parent_value(position, "position_quantity")}
        elif recipe_id == "O147":
            objects, events = [], []
            for symbol in ("ES", "NQ", "YM"):
                obj = role[f"{symbol.lower()}_object"]
                use = role[f"{symbol.lower()}_first_use"]
                actual_symbol = obj.get("instrument_id")
                if str(actual_symbol).upper() != symbol:
                    raise LifecycleDerivationError(f"{symbol} role does not contain a native {symbol} object")
                objects.append({"object_id": obj["object_id"], "instrument_id": symbol,
                                "bounds": _parent_bounds(obj), "known_at": obj.get("known_at")})
                events.append({"event_id": use["object_id"], "object_id": obj["object_id"],
                               "kind": "first_use", "at": use.get("known_at"), "known_at": use.get("known_at")})
            inp = {"objects": objects, "events": events,
                   "source_object_correspondence": deepcopy(config.get("source_object_correspondence")),
                   "required_instruments": ("ES", "NQ", "YM")}
        elif recipe_id == "O148":
            definition = role["definition"]; candidates = role["candidates"]; orders = role["orders"]
            order_candidate_ids = {_parent_value(order, "candidate_id") for order in orders}
            candidate_rows = [{"candidate_id": candidate["object_id"],
                               "selected": candidate["object_id"] in order_candidate_ids,
                               "known_at": candidate.get("known_at")} for candidate in candidates]
            order_rows, fill_rows = [], []
            for order in orders:
                oid = _parent_value(order, "order_id")
                order_rows.append({"order_id": oid, "candidate_id": _parent_value(order, "candidate_id"),
                                   "known_at": order.get("known_at")})
                for index, event in enumerate(_parent_value(order, "order_state_timeline") or []):
                    if event.get("kind") in {"fill", "partial_fill"}:
                        fill_rows.append({"fill_id": event.get("event_id") or f"{oid}:fill:{index}",
                                          "order_id": oid, "known_at": event.get("available_at", event.get("at"))})
            inp = {"process_version": _parent_value(definition, "model_version"),
                   "frozen_at": _parent_value(definition, "frozen_at"), "candidates": candidate_rows,
                   "order_records": order_rows, "fill_records": fill_rows,
                   "inclusion_rule": deepcopy(config.get("inclusion_rule")),
                   "scope": deepcopy(config.get("scope")), "split_direction": config.get("split_direction"),
                   "split_boundaries": deepcopy(config.get("split_boundaries"))}
        elif recipe_id == "O149":
            definition, order = role["definition"], role["order"]
            fields = config.get("feature_fields")
            if not isinstance(fields, dict) or set(map(str, fields)) != {str(p["object_id"]) for p in role["features"]}:
                raise LifecycleDerivationError("feature_fields must select one actual output from every feature parent")
            features = []
            for parent in role["features"]:
                field = fields.get(parent["object_id"], fields.get(str(parent["object_id"])))
                if not isinstance(field, str) or field not in parent.get("value", {}):
                    raise LifecycleDerivationError("feature field is absent from its selected parent")
                features.append({"feature_id": parent["object_id"], "value": _parent_value(parent, field),
                                 "known_at": parent.get("known_at")})
            policy = deepcopy(config.get("grade_policy"))
            if not isinstance(policy, dict):
                raise LifecycleDerivationError("grade_policy must be a scoped source definition")
            inp = {"model_id": policy.get("model_id"), "model_version": _parent_value(definition, "model_version"),
                   "model_known_at": definition.get("known_at"), "training_cutoff_at": policy.get("training_cutoff_at"),
                   "features": features, "transform_versions": deepcopy(policy.get("transform_versions")),
                   "score": policy.get("score"), "threshold": policy.get("threshold"),
                   "comparator": policy.get("comparator", ">="), "grade_available_at": policy.get("grade_available_at"),
                   "order_at": _parent_time(order, "order_at", "decision_at"),
                   "touch_at": policy.get("touch_at"),
                   "supplied_grade": policy.get("supplied_grade"),
                   "later_ofm_causal_status": policy.get("later_ofm_causal_status")}
        elif recipe_id == "O150":
            definition, ledger = role["definition"], role["instruction_ledger"]
            order = deepcopy(config.get("source_order"))
            if not isinstance(order, dict):
                raise LifecycleDerivationError("source_order must be the scoped order instruction record")
            if order.get("candidate_id") not in (_parent_value(ledger, "eligible_ids") or []):
                raise LifecycleDerivationError("source order candidate is absent from the frozen instruction ledger")
            events = []
            for fill in role["fills"]:
                at = _parent_value(fill, "actual_fill_at")
                qty = _parent_value(fill, "actual_fill_quantity")
                if at is not None:
                    events.append({"event_id": fill["object_id"], "kind": "fill", "at": at,
                                   "available_at": fill.get("known_at"), "filled_qty": qty})
            for action_parent in role["position_actions"]:
                events.extend(deepcopy(_parent_value(action_parent, "management_actions") or []))
            inp = {key: deepcopy(order.get(key)) for key in ("candidate_id", "order_id", "position_id", "source_id",
                   "method_id", "side", "order_type", "limit", "q", "quantity", "placed_at", "placement_known_at",
                   "stop", "target", "other_open_positions", "as_of", "use_at", "order_inside_ticks")}
            inp.update(source_policy=_policy_from_definition(definition, config), events=events)
        elif recipe_id == "O151":
            order, trades = role["order"], role["trades"]
            side = _parent_value(order, "side")
            inp = {"order_id": _parent_value(order, "order_id"),
                   "side": "buy" if side == "long" else "sell" if side == "short" else side,
                   "limit": _parent_value(order, "order_price"),
                   "active_at": _parent_time(order, "order_at", "decision_at"),
                   "cancel_at": _parent_value(order, "cancel_at"),
                   "fill_convention": config.get("fill_convention"),
                   "trades": deepcopy(_parent_value(trades, "event_records") or []),
                   "source_policy": deepcopy(config.get("source_policy")),
                   "source_id": config.get("source_id"), "method_id": config.get("method_id"),
                   "other_position_open": config.get("other_position_open"), "use_at": config.get("use_at")}
        elif recipe_id == "O152":
            definition = role["definition"]; orders = role["orders"]
            policy = deepcopy(config.get("cost_policy"))
            if not isinstance(policy, dict):
                raise LifecycleDerivationError("cost_policy must be a scoped source definition")
            quantities = [_parent_value(order, "filled_quantity", "authorized_quantity") for order in orders]
            quantity = quantities[0] if len(quantities) == 1 else sum((dec(v) or Decimal(0) for v in quantities), Decimal(0))
            inp = {"trade_cost_ticks": policy.get("trade_cost_ticks"),
                   "stop_slippage_ticks": policy.get("stop_slippage_ticks"),
                   "tick_value": policy.get("tick_value"), "quantity": quantity,
                   "gross_target_ticks": policy.get("gross_target_ticks"),
                   "gross_stop_ticks": policy.get("gross_stop_ticks"),
                   "target_outcome": policy.get("target_outcome"), "stop_outcome": policy.get("stop_outcome"),
                   "r_unit": policy.get("r_unit"), "account_fees": deepcopy(policy.get("account_fees", [])),
                   "account_fees_separate": policy.get("account_fees_separate"),
                   "known_at": _max_time(definition.get("known_at"), *[p.get("known_at") for p in orders])}
        elif recipe_id == "O155":
            definition = role["definition"]
            result_fields = config.get("result_fields")
            if not isinstance(result_fields, dict) or set(map(str, result_fields)) != {str(p["object_id"]) for p in role["closed_results"]}:
                raise LifecycleDerivationError("result_fields must select each actual closed-result output")
            results = []
            for parent in role["closed_results"]:
                field = result_fields.get(parent["object_id"], result_fields.get(str(parent["object_id"])))
                value = _parent_value(parent, field) if isinstance(field, str) else None
                results.append({"result_id": parent["object_id"], "baseline_units": value,
                                "at": parent.get("known_at"), "close_at": parent.get("known_at")})
            ladder = deepcopy(config.get("ladder_policy"))
            if not isinstance(ladder, dict):
                raise LifecycleDerivationError("ladder_policy must be the scoped source ladder definition")
            inp = {"E0": ladder.get("E0"), "B": ladder.get("B"), "risk_stage": ladder.get("risk_stage"),
                   "validated_process": _parent_value(definition, "definition_hash") is not None,
                   "decision_at": ladder.get("decision_at"), "prior_results": results}
        elif recipe_id == "O156":
            cohort, grade, costs = role["cohort"], role["grade"], role["costs"]
            scenario = deepcopy(config.get("source_scenario"))
            if not isinstance(scenario, dict):
                raise LifecycleDerivationError("source_scenario must be a scoped historical scenario record")
            inp = {key: deepcopy(scenario.get(key)) for key in ("scenario_id", "currency_per_r", "target", "drawdown",
                   "daily_r", "paths", "pass_n", "reported_pass_rate", "reported_time_to_pass", "path_design",
                   "trailing_drawdown_rule", "consistency_rule")}
            inp["source_causal_status"] = scenario.get("source_causal_status", "corrected" if
                _parent_value(grade, "feature_causal") is True and _parent_value(grade, "model_known_before_use") is True else None)
            inp["source_config_id"] = cohort["object_id"]
            inp["known_at"] = _max_time(cohort.get("known_at"), grade.get("known_at"), costs.get("known_at"))
        elif recipe_id == "O165":
            label = config.get("state_label")
            if label not in STATES:
                raise LifecycleDerivationError("state_label must be one supplied B/A/D/E/W observation")
            participation, response, depth = role["participation"], role["response"], role["depth"]
            criterion_sources = {
                "two_sided_executions": _parent_value(participation, "total") is not None,
                "recent_revisits": None,
                "low_aggression_both_sides": None,
                "high_aggression": _parent_value(participation, "source_spike", "replenishment_hypothesis"),
                "low_response_efficiency": _parent_value(response, "source_absorption", "absorption"),
                "opposite_liquidity_holds_and_refills": _parent_value(depth, "hold", "defense_interpretation"),
                "aggression": _parent_value(participation, "aggressive_arrival", "source_spike"),
                "efficient_displacement": _parent_value(response, "directional_reward", "geometry_ok"),
                "prior_absorption_or_effort": _parent_value(response, "source_absorption", "absorption"),
                "replenishment_stops": _parent_value(depth, "declining", "source_classification"),
                "level_gives_way": _parent_value(response, "directional_reward", "geometry_ok"),
                "cancellations_dominate": None,
            }
            evidence_parents = [participation, response, depth]
            state_at = config.get("state_at")
            criteria = [{"criterion": name, "observed": criterion_sources[name],
                         "known_at": max(p.get("known_at") for p in evidence_parents),
                         "instrument_id": participation.get("instrument_id")}
                        for name in STATE_MEANINGS[label]]
            instruments = {str(p.get("instrument_id")) for p in evidence_parents}
            if len(instruments) != 1:
                raise LifecycleDerivationError("state evidence parents must share one native instrument")
            inp = {"state_label": label, "state_at": state_at,
                   "instrument_id": participation.get("instrument_id"),
                   "observation_id": config.get("observation_id"),
                   "required_depth_levels": config.get("required_depth_levels"),
                   "depth_levels": _parent_value(depth, "depth_coverage"),
                   "criteria": criteria,
                   "evidence": [{"evidence_id": p["object_id"], "known_at": p.get("known_at")} for p in evidence_parents]}
        elif recipe_id == "O166":
            current, nxt = role["current_state"], role["next_state"]
            cv, nv = deepcopy(current.get("value", {})), deepcopy(nxt.get("value", {}))
            if cv.get("instrument_id") != nv.get("instrument_id"):
                raise LifecycleDerivationError("adjacent state parents use different instruments")
            current_record = {"state_label": cv.get("state_label"), "state_at": cv.get("state_at"),
                              "state_id": cv.get("observation_id"), "known_at": current.get("known_at"),
                              "sequence": config.get("current_sequence"), "instrument_id": cv.get("instrument_id"),
                              "cohort_id": config.get("cohort_id"), "reset_id": config.get("reset_id")}
            next_record = {"state_label": nv.get("state_label"), "state_at": nv.get("state_at"),
                           "state_id": nv.get("observation_id"), "known_at": nxt.get("known_at"),
                           "sequence": config.get("next_sequence"), "instrument_id": nv.get("instrument_id"),
                           "cohort_id": config.get("cohort_id"), "reset_id": config.get("reset_id")}
            conditioning = [{"evidence_id": p["object_id"], "known_at": p.get("known_at"),
                             "recipe_id": p.get("recipe_id")} for p in role["conditioning"]]
            inp = {"current_observation": current_record, "next_observation": next_record,
                   "cadence": deepcopy(config.get("cadence")), "conditioning_evidence": conditioning,
                   "counts": deepcopy(config.get("counts")), "source_counts_symbol": config.get("source_counts_symbol"),
                   "reported_probability": config.get("reported_probability")}
        else:
            raise LifecycleDerivationError(f"{recipe_id} has no parent-derived lifecycle adapter")
        result = REGISTRATION_OVERRIDES[recipe_id](inp)
        result.parent_ids = [parent["object_id"] for parent in parents]
        return result
    except (ArithmeticError, KeyError, LifecycleDerivationError, TypeError, ValueError) as exc:
        return _result(recipe_id, "invalid", {}, base_ok=False, coverage_ok=None,
                       hole_ids=_holes(recipe_id, ["parents"]), reason=str(exc))


DERIVED_PRODUCERS = {
    recipe_id: (lambda config, parents, recipe_id=recipe_id:
                _derive_lifecycle(recipe_id, config, parents))
    for recipe_id in DERIVED_PARENT_ROLES
}

REQUIRED_INPUTS = {recipe_id: () for recipe_id in LIFECYCLE_SCHEMAS}


_T = {
    "O137": ((str,), (str,), (int,), (list,), (str,), (list,)),
    "O138": ((str,), (int,), (str,), (str,), (bool,), (list,)),
    "O139": ((Decimal,), (Decimal,), (Decimal,), (bool,), (bool,), (list,),
             (dict,), (Decimal,), (str,), (str, dict), (int,), (dict,)),
    "O140": ((Decimal,), (Decimal,), (Decimal,), (bool,), (bool,), (list,)),
    "O141": ((dict,), (Decimal,), (bool,), (bool,), (str,), (list,)),
    "O142": ((list,), (Decimal,), (list,), (list,), (bool,), (bool,), (str,)),
    "O143": ((Decimal,), (int,), (int,), (int,), (str,), (bool,)),
    "O144": ((int,), (str, int), (bool,), (int,), (bool,), (bool,)),
    "O145": ((Decimal,), (Decimal,), (Decimal,), (bool,), (bool,), (bool,), (list,)),
    "O146": ((list,), (bool,), (list,), (list,), (list,), (list,), (bool,)),
    "O147": ((dict,), (dict, str), (str,), (bool,), (bool,)),
    "O148": ((str,), (int,), (int,), (int,), (int,), (list,), (str,), (bool,), (bool,), (bool,)),
    "O149": ((str, int, Decimal), (bool,), (int,), (bool,), (bool,), (type(None),), (bool,)),
    "O150": ((list,), (Decimal,), (Decimal,), (bool,), (list,), (bool,), (bool,), (int,), (str,), (int,), (Decimal,), (Decimal,), (Decimal,), (bool,), (Decimal,)),
    "O151": ((int,), (str,), (int,), (Decimal,), (bool,), (bool,)),
    "O152": ((Decimal,), (Decimal,), (Decimal,), (bool,), (bool,)),
    "O155": ((str,), (Decimal,), (Decimal,), (Decimal,), (str,), (list,), (Decimal,), (Decimal,), (Decimal,), (list,), (int,), (Decimal,), (bool,), (Decimal,), (int,), (Decimal,)),
    "O156": ((str,), (dict,), (Decimal,), (int, Decimal, str), (str,), (list,)),
    "O165": ((str,), (bool,), (type(None),), (list,), (int,)),
    "O166": ((str,), (str,), (int,), (int,), (bool,), (bool,), (int,), (Decimal,), (list,), (int,)),
}

# All documented keys are explicit even when evidence is unavailable.  The
# nullable flag represents a source/data unknown; a non-null value must still
# have its declared type.
OUTPUT_SCHEMAS = {
    rid: {
        field: OutputField(types, nullable=True)
        for field, types in zip(LIFECYCLE_SCHEMAS[rid], _T[rid], strict=True)
    }
    for rid in LIFECYCLE_SCHEMAS
}


__all__ = ["DERIVED_PARENT_ROLES", "DERIVED_PRODUCERS", "LIFECYCLE_SCHEMAS",
           "LifecycleDerivationError", "OUTPUT_SCHEMAS", "REGISTRATION_OVERRIDES",
           "REQUIRED_INPUTS"]
