from decimal import Decimal

import pytest

from trading_research.research.method_pack.contracts import OUTPUT_SCHEMAS as CONTRACT_SCHEMAS
from trading_research.research.method_pack.contracts import validate_output
from trading_research.research.method_pack.objects.lifecycles import (
    DERIVED_PRODUCERS,
    LIFECYCLE_SCHEMAS,
    OUTPUT_SCHEMAS,
    REGISTRATION_OVERRIDES,
)


def run(recipe_id, **inputs):
    return REGISTRATION_OVERRIDES[recipe_id](inputs)


def parent(object_id, recipe_id, value, *, known_at=10, instrument_id="NQ"):
    return {
        "object_id": object_id, "recipe_id": recipe_id, "value": value,
        "known_at": known_at, "instrument_id": instrument_id,
        "state": "computed", "recipe_base_ok": True, "recipe_coverage_ok": True,
    }


def source_policy(**overrides):
    policy = {
        "policy_id": "refill-v1",
        "source_id": "refill",
        "method_id": "M09",
        "stop_ticks": 32,
        "target_ticks": 96,
        "cancel_minutes": 30,
        "one_position_at_a_time": True,
    }
    policy.update(overrides)
    return policy


def order_input(events, *, use_at=30, **overrides):
    values = {
        "candidate_id": "c1", "order_id": "o1", "position_id": "p1",
        "instrument_id": "NQ", "source_id": "refill", "method_id": "M09", "side": "long",
        "order_type": "limit", "limit": 100, "q": Decimal("0.25"),
        "quantity": 3, "placed_at": 10, "events": events,
        "source_policy": source_policy(), "other_open_positions": 0,
        "use_at": use_at,
    }
    values.update(overrides)
    # These are fully identified synthetic control records. Explicit event
    # overrides (including a foreign identity or unknown clock) stay intact.
    values["events"] = [{
        "event_id": f"order-event-{index}",
        **{key: values[key] for key in ("candidate_id", "order_id", "position_id", "instrument_id")},
        "known_at": event.get("at"), **event,
    } for index, event in enumerate(events)]
    return values


def test_every_owned_result_has_a_complete_typed_output_schema():
    previous = dict(CONTRACT_SCHEMAS)
    try:
        CONTRACT_SCHEMAS.update(OUTPUT_SCHEMAS)
        for recipe_id, producer in REGISTRATION_OVERRIDES.items():
            result = producer({})
            assert set(LIFECYCLE_SCHEMAS[recipe_id]) <= set(result.value)
            assert validate_output(result) is result
    finally:
        CONTRACT_SCHEMAS.clear()
        CONTRACT_SCHEMAS.update(previous)


def test_thin_lifecycle_inputs_never_receive_fabricated_record_identity():
    thesis = run("O138", close=99, close_at=10, death_close=100, known_at=10, use_at=11)
    assert thesis.state == "hole"
    assert thesis.value["thesis_id"] is None
    assert thesis.value["alive_at_decision"] is None

    reentry = run("O144", prior_exit_at=10, return_at=11, fresh_confirm_at=12,
                  entry_at=13, same_thesis_band=True, daily_r=-3)
    assert reentry.state == "hole"
    assert reentry.value["new_candidate_id"] is None
    assert reentry.value["reentry_permission"] is None

    transition = run("O166", counts={state: 1 for state in "BADEW"},
                     conditioning_known_at=9)
    assert transition.state == "hole"
    assert transition.value["conditioning_evidence"] == []
    assert transition.value["transition_valid"] is None


def test_scalar_results_and_fills_preserve_arithmetic_without_claiming_causal_records():
    daily = run("O145", results_r=[-1, -1], limit_r=-4, known_at=10, use_at=11)
    assert daily.value["sum_r"] == -2
    assert daily.value["daily_R_before"] is None
    assert daily.value["entry_permission"] is None
    assert "HOLE:O145:result_records" in daily.hole_ids

    order = run("O150", limit=100, fill_qtys=[1], quantity=2, placed_at=10,
                side="long", order_type="limit")
    assert order.value["filled_quantity"] is None
    assert order.value["position_open"] is None
    assert order.value["lifecycle_valid"] is None
    assert order.value["unclocked_fill_quantities"] == [Decimal(1)]
    assert "HOLE:O150:fill_event_records" in order.hole_ids


def test_o139_derived_stop_retains_selected_invalidation_identity_and_clock():
    entry = parent("entry-1", "O150", {"order_price": Decimal("105"), "side": "long",
                                             "candidate_id": "candidate-1", "decision_at": 20}, known_at=20)
    structure = parent("rejection-1", "O089", {"rejection_band": [Decimal("99"), Decimal("101")]},
                       known_at=15)
    result = DERIVED_PRODUCERS["O139"](
        {"parent_roles": {"entry": "entry-1", "structure": "rejection-1"},
         "q": Decimal("0.25"), "stop_policy": {"policy_id": "behind-rejection-v1"},
         "policy_selected_at": 18},
        [entry, structure],
    )
    assert result.state == "computed"
    assert result.value["invalidation_ref"] == {
        "object_id": "rejection-1", "recipe_id": "O089", "field": "bounds.low",
        "value": Decimal("99"), "known_at": 15,
    }
    assert result.value["planned_stop"] == Decimal("99")
    assert result.value["planned_stop_side"] == "long"
    assert result.value["planned_stop_method"] == "behind-rejection-v1"
    assert result.value["planned_stop_known_at"] == 18
    assert result.value["planned_stop_comparison"]["on_adverse_side"] is True


def test_cancel_ends_working_quantity_but_preserves_filled_position_p21():
    result = REGISTRATION_OVERRIDES["O150"](order_input([
        {"event_id": "f1", "kind": "fill", "qty": 1, "at": 15},
        {"event_id": "c1", "kind": "cancel", "at": 20},
    ]))
    assert result.base_ok is True
    assert result.value["remaining_quantity"] == 0
    assert result.value["filled_quantity"] == 1
    assert result.value["position_quantity"] == 1
    assert result.value["position_open"] is True
    assert result.value["order_state"] == "canceled"
    assert result.state == "computed"


def test_exit_after_entry_order_cancel_closes_only_filled_position_p22():
    result = REGISTRATION_OVERRIDES["O150"](order_input([
        {"kind": "fill", "qty": 1, "at": 15},
        {"kind": "cancel", "at": 20},
        {"kind": "exit_fill", "qty": 1, "at": 25},
    ]))
    assert result.base_ok is True
    assert result.value["remaining_quantity"] == 0
    assert result.value["position_quantity"] == 0
    assert result.value["position_open"] is False
    assert result.value["filled_quantity"] == 1


def test_expiry_prohibits_fill_until_explicit_reopen_p23():
    expired = REGISTRATION_OVERRIDES["O150"](order_input([
        {"kind": "expire", "at": 14}, {"kind": "fill", "qty": 1, "at": 15},
    ]))
    assert expired.state == "invalid"
    assert "fill without valid working order" in expired.reason

    reopened = REGISTRATION_OVERRIDES["O150"](order_input([
        {"kind": "expire", "at": 14},
        {"kind": "reopen", "new_quantity": 2, "new_price": 99, "at": 15},
        {"kind": "fill", "qty": 2, "at": 16},
    ]))
    assert reopened.base_ok is True
    assert reopened.value["filled_quantity"] == 2
    assert reopened.value["order_price"] == 99


def test_amended_quantity_and_price_reconcile_and_reject_below_fills_p24():
    amended = REGISTRATION_OVERRIDES["O150"](order_input([
        {"kind": "amend", "new_quantity": 5, "new_price": "100.50", "at": 12},
        {"kind": "fill", "qty": 1, "at": 15},
    ]))
    assert amended.value["authorized_quantity"] == 5
    assert amended.value["remaining_quantity"] == 4
    assert amended.value["order_price"] == Decimal("100.50")

    invalid = REGISTRATION_OVERRIDES["O150"](order_input([
        {"kind": "fill", "qty": 2, "at": 11},
        {"kind": "amend", "new_quantity": 1, "at": 12},
    ]))
    assert invalid.state == "invalid"
    assert "below cumulative fills" in invalid.reason


def test_future_fill_is_not_backdated_into_snapshot_p25():
    result = REGISTRATION_OVERRIDES["O150"](order_input([
        {"event_id": "future-fill", "kind": "fill", "qty": 1, "at": 15},
    ], use_at=12, known_at=10))
    assert result.value["filled_quantity"] == 0
    assert result.value["position_open"] is False
    assert result.known_at == 10
    assert [row.get("event_id") for row in result.value["pending_events"] if row.get("event_id")] == ["future-fill"]


def test_requested_partial_does_not_change_position_until_execution_fill():
    common = {
        "entry_id": "entry", "entry_at": 10, "initial_quantity": 3,
        "initial_risk": 2, "policy_frozen_at": 9,
        "source_policy": {"allowed_actions": ["partial"]},
    }
    requested = run("O142", **common, actions=[{"kind": "partial_request", "qty": 1, "at": 11}])
    assert requested.value["position_quantity_after"] == 3
    assert requested.value["management_actions"][0]["applied_quantity"] == 0
    filled = run("O142", **common, actions=[
        {"kind": "partial_request", "qty": 1, "at": 11},
        {"kind": "partial_fill", "filled_qty": 1, "at": 12},
    ])
    assert filled.value["position_quantity_after"] == 2


def test_same_timestamp_order_events_require_declared_sequence():
    tied = REGISTRATION_OVERRIDES["O150"](order_input([
        {"kind": "fill", "qty": 1, "at": 15}, {"kind": "cancel", "at": 15},
    ]))
    assert tied.state == "invalid"
    ordered = REGISTRATION_OVERRIDES["O150"](order_input([
        {"kind": "fill", "qty": 1, "at": 15, "sequence": 1},
        {"kind": "cancel", "at": 15, "sequence": 2},
    ]))
    assert ordered.base_ok is True
    assert ordered.value["position_quantity"] == 1


def test_source_caps_and_account_result_resets_do_not_leak_across_scope():
    mismatched = REGISTRATION_OVERRIDES["O150"](order_input([], source_id="other"))
    assert mismatched.value["stop"] is None
    assert mismatched.value["target"] is None
    assert "HOLE:O150:source_policy_scope" in mismatched.hole_ids

    result = run(
        "O145", source_id="sires", account_id="a", session_id="today",
        policy_id="daily-v1", decision_at=30, session_finished=False,
        source_policy={"source_id": "sires", "account_id": "a", "session_id": "today",
                       "policy_id": "daily-v1", "limit_r": -4, "frozen_at": 5,
                       "r_definition_id":"sires-original-r","prior_ledger_coverage_complete":True},
        result_records=[
            {"result_id": "old-session", "source_id": "sires", "account_id": "a",
             "session_id": "yesterday", "policy_id": "daily-v1", "result_r": -8,
             "close_at":9,"available_at":10,"r_definition_id":"sires-original-r"},
            {"result_id": "other-account", "source_id": "sires", "account_id": "b",
             "session_id": "today", "policy_id": "daily-v1", "result_r": -8,
             "close_at":10,"available_at":11,"r_definition_id":"sires-original-r"},
            {"result_id": "today", "source_id": "sires", "account_id": "a",
             "session_id": "today", "policy_id": "daily-v1", "result_r": -1,
             "close_at":11,"available_at":12,"r_definition_id":"sires-original-r"},
        ],
    )
    assert result.value["daily_R_before"] == -1
    assert result.value["ledger_ids"] == ["today"]
    assert result.value["entry_permission"] is True


def test_daily_r_requires_complete_unique_closed_ledger_and_fixed_original_r():
    base={"source_id":"sires","account_id":"a","session_id":"today","policy_id":"daily-v1",
          "decision_at":30,"session_finished":False,
          "source_policy":{"source_id":"sires","account_id":"a","session_id":"today",
              "policy_id":"daily-v1","limit_r":-4,"frozen_at":5,
              "r_definition_id":"original-r"}}
    empty=run("O145",**base,result_records=[])
    assert empty.value["daily_R_before"] is None
    assert "HOLE:O145:prior_ledger_coverage" in empty.hole_ids

    complete=run("O145",**{**base,"prior_ledger_coverage_complete":True},result_records=[])
    assert complete.value["daily_R_before"]==0
    assert complete.value["entry_permission"] is True

    row={"result_id":"r1","source_id":"sires","account_id":"a","session_id":"today",
         "policy_id":"daily-v1","close_at":10,"available_at":11,"result_r":-1,
         "r_definition_id":"original-r"}
    stable=run("O145",**{**base,"prior_ledger_coverage_complete":True},result_records=[row])
    noisy=run("O145",**{**base,"prior_ledger_coverage_complete":True},result_records=[
        row,{**row,"close_at":35,"available_at":36},
        {"account_id":"other","malformed":"unrelated"}])
    assert noisy.state==stable.state=="computed"
    assert noisy.value["daily_R_before"]==stable.value["daily_R_before"]==Decimal(-1)
    assert noisy.value["ledger_ids"]==stable.value["ledger_ids"]==["r1"]

    missing_id=run("O145",**{**base,"prior_ledger_coverage_complete":True},
                   result_records=[{**row,"result_id":None}])
    assert missing_id.value["daily_R_before"] is None
    assert "HOLE:O145:prior_result_identity_time_value_or_r_definition" in missing_id.hole_ids

    duplicate=run("O145",**{**base,"prior_ledger_coverage_complete":True},
                  result_records=[row,{**row,"result_r":1}])
    assert duplicate.state=="invalid"
    assert "duplicated" in duplicate.reason

    wrong_r=run("O145",**{**base,"prior_ledger_coverage_complete":True},
                result_records=[{**row,"r_definition_id":"rebased-r"}])
    assert wrong_r.state=="invalid"
    assert "different original R" in wrong_r.reason


def test_persistent_thesis_records_first_death_and_never_silent_revives():
    result = run(
        "O138", thesis_id="t1", declared_at=1, decision_at=20,
        death_conditions=[
            {"condition_id": "price", "comparator": "<", "threshold": 100, "coverage_complete": True},
            {"condition_id": "news", "coverage_complete": False},
        ],
        events=[
            {"condition_id": "price", "price": 99, "at": 10},
            {"condition_id": "price", "price": 102, "at": 15},
        ],
    )
    assert result.value["state"] == "dead"
    assert result.value["first_death_at"] == 10
    assert result.value["alive_at_decision"] is False
    assert result.value["stopout_is_death"] is False


def test_reentry_requires_linked_exit_same_live_thesis_and_fresh_branch():
    valid = run(
        "O144", parent_entry_id="e1", parent_position_id="p1", parent_exit_id="x1",
        parent_exit_at=10, new_candidate_id="c2", parent_thesis_id="t", new_thesis_id="t",
        parent_band_id="b", new_band_id="b", thesis_state="alive", return_at=11,
        fresh_confirmation_at=12, decision_at=13, full_branch_verdict=True,
        account_permission=True, risk_state_known_at=12,
    )
    assert valid.value["reentry_permission"] is True
    dead = run("O144", **{**{
        "parent_entry_id": "e1", "parent_position_id": "p1", "parent_exit_id": "x1",
        "parent_exit_at": 10, "new_candidate_id": "c2", "parent_thesis_id": "t",
        "new_thesis_id": "t", "parent_band_id": "b", "new_band_id": "b",
        "return_at": 11, "fresh_confirmation_at": 12, "decision_at": 13,
        "full_branch_verdict": True, "account_permission": True,
    }, "thesis_state": "dead"})
    assert dead.state == "invalid"


def test_journal_enforces_source_configured_confidence_and_review_example():
    config = {
        "required_pre_entry_fields": ["thesis_id", "reason", "confidence", "context", "regime"],
        "confidence": {"min": 1, "max": 5, "observed_at": "session_start"},
        "review": {"example_sessions": 30, "universal_sufficiency": False},
        "mfe_mae_collection": {"min_trades": 40, "max_trades": 80, "scope": "research_step"},
    }
    row = {
        "candidate_id": "c", "decision_at": 20, "session_start_at": 10,
        "thesis_id": "t", "reason": "r", "confidence": 4, "context": "balance", "regime": "quiet",
        "feature_known_at": 10, "confidence_known_at": 10,
        "input_record_id": "input", "outcome_record_id": "outcome", "outcome_at": 30,
        "known_at": 30,
    }
    result = run("O146", process_version="v1", process_config=config,
                 eligible_ids=["c"], journal_rows=[row])
    assert result.value["pre_entry_fields_valid"] is True
    assert result.value["confidence_config"]["max"] == 5
    assert result.value["review_config"]["example_sessions"] == 30
    late = run("O146", process_version="v1", process_config=config,
               eligible_ids=["c"], journal_rows=[{**row, "confidence_known_at": 11}])
    assert late.state == "invalid"


def test_amt_triad_uses_native_instrument_objects_and_ordered_first_use():
    objects = [
        {"object_id": "es", "instrument_id": "ES", "bounds": [1, 2], "known_at": 5},
        {"object_id": "nq", "instrument_id": "NQ", "bounds": [3, 4], "known_at": 5},
        {"object_id": "ym", "instrument_id": "YM", "bounds": [5, 6], "known_at": 5},
    ]
    events = [
        {"event_id": "nq-use", "object_id": "nq", "kind": "reaction", "at": 8},
        {"event_id": "es-use", "object_id": "es", "kind": "reaction", "at": 9},
        {"event_id": "ym-use", "object_id": "ym", "kind": "reaction", "at": 10},
    ]
    result = run("O147", objects=objects, events=events,
                 source_object_correspondence={"basis": "same AMT role"},
                 revisions=[{"kind": "iod_reaction_revision", "trigger_event_id": "nq-use", "at": 8}])
    assert result.value["first_instrument"] == "NQ"
    assert result.value["native_first_use_times"] == {"ES": 9, "NQ": 8, "YM": 10}
    assert result.value["iod_reaction_revision"] is True


def test_grade_needs_validation_on_both_sides_of_threshold_and_full_provenance():
    common = {
        "model_id": "g", "model_version": "v", "model_known_at": 5,
        "training_cutoff_at": 4, "features": [{"feature_id": "f", "value": 1, "known_at": 6}],
        "transform_versions": {"f": "v1"}, "threshold": Decimal("0.7"),
        "comparator": ">=", "grade_available_at": 7, "order_at": 8,
    }
    assert run("O149", **common, score=Decimal("0.8")).value["selected_by_supplied_rule"] is True
    assert run("O149", **common, score=Decimal("0.6")).value["selected_by_supplied_rule"] is False
    assert run("O149", **{**common, "transform_versions": None}, score=Decimal("0.8")).state == "hole"


def test_fill_model_enforces_cancel_expiry_and_one_position_scope():
    common = {
        "order_id": "o", "side": "buy", "limit": 100, "active_at": 10,
        "fill_convention": "touch_or_through", "trades": [{"trade_id": "t", "price": 100, "at": 20}],
        "source_id": "refill", "method_id": "M09", "source_policy": source_policy(),
        "use_at": 30,
    }
    assert run("O151", **common, other_position_open=False).value["first_modeled_fill_at"] == 20
    assert run("O151", **common, cancel_at=19, other_position_open=False).value["first_modeled_fill_at"] is None
    assert run("O151", **common, expiry_at=19, other_position_open=False).value["first_modeled_fill_at"] is None
    assert run("O151", **common, other_position_open=True).value["fill_eligibility"] is False


def test_stoic_ladder_and_refill_scenario_keep_source_holes_explicit():
    ladder = run("O155", E0=10000, B=100, validated_process=True, risk_stage="second",
                 decision_at=20, prior_results=[{"result_id": "r1", "baseline_units": 3, "at": 10}])
    assert ladder.value["planned_risk_units"] == 4
    assert ladder.value["planned_reward_units"] == 12
    assert ladder.value["activation_holes"]
    assert run("O155", E0=10000, B=101, validated_process=True, risk_stage="first").state == "invalid"

    scenario = run("O156", scenario_id="80-per-r", currency_per_r=80, target=3000,
                   drawdown=2000, daily_r=-4, paths=4000, pass_n=3680,
                   source_causal_status="corrected", known_at=50)
    assert scenario.value["reported_pass_rate"] == Decimal("0.92")
    assert scenario.value["daily_stop_currency"] == -320
    assert scenario.value["missing_path_rules"]
    assert run("O156", currency_per_r=0).state == "invalid"


def test_state_evidence_checks_both_sides_depth_and_availability():
    common = {
        "state_label": "A", "state_at": 10, "instrument_id": "NQ",
        "observation_id": "a1", "required_depth_levels": 4, "depth_levels": 4,
        "criteria": [
            {"criterion": "high_aggression", "observed": True, "known_at": 10},
            {"criterion": "low_response_efficiency", "observed": True, "known_at": 10},
            {"criterion": "opposite_liquidity_holds_and_refills", "observed": True, "known_at": 10},
        ],
        "evidence": [{"evidence_id": "state-evidence", "known_at": 10}],
    }
    assert run("O165", **common).value["state_evidence_complete"] is True
    assert run("O165", **{**common, "criteria": [*common["criteria"][:-1],
               {**common["criteria"][-1], "observed": False}]}).value["state_evidence_complete"] is False
    assert run("O165", **{**common, "depth_levels": 3}).state == "hole"
    assert run("O165", **{**common, "criteria": [{**common["criteria"][0], "known_at": 11}, *common["criteria"][1:]]}).state == "invalid"


def test_derived_cohort_uses_actual_candidate_order_and_fill_identities():
    definition = parent("definition", "O137", {"model_version": "v1", "frozen_at": 1}, known_at=1)
    candidate = parent("candidate", "O121", {"branch_ok": True}, known_at=5)
    order = parent("order", "O150", {
        "order_id": "order-1", "candidate_id": "candidate",
        "order_state_timeline": [{"event_id": "fill-1", "kind": "fill", "at": 8, "available_at": 8}],
    }, known_at=8)
    result = DERIVED_PRODUCERS["O148"]({
        "parent_roles": {"definition": "definition", "candidates": ["candidate"], "orders": ["order"]},
        "inclusion_rule": {"rule_id": "all-source-candidates"},
    }, [definition, candidate, order])
    assert result.state == "computed"
    assert result.value["eligible_count"] == 1
    assert result.value["selected_count"] == 1
    assert result.value["filled_order_count"] == 1
    assert result.value["filled_order_ids"] == ["order-1"]


def test_derived_order_lifecycle_uses_selected_fill_and_position_action_parents():
    definition = parent("definition", "O137", {"model_version": "v1", "frozen_at": 1}, known_at=1)
    ledger = parent("ledger", "O148", {"eligible_ids": ["candidate"]}, known_at=2)
    fill = parent("fill", "O151", {"actual_fill_at": 10, "actual_fill_quantity": Decimal(2),
                                    "order_id": "order", "position_id": "position",
                                    "candidate_id": "candidate", "instrument_id": "NQ"}, known_at=10)
    action = parent("action", "O142", {
        "position_id": "position", "candidate_id": "candidate", "instrument_id": "NQ",
        "management_actions": [{"event_id": "exit", "kind": "exit_fill", "filled_qty": 2, "at": 15,
                                "known_at": 15, "position_id": "position", "instrument_id": "NQ"}],
    }, known_at=15)
    result = DERIVED_PRODUCERS["O150"]({
        "parent_roles": {"definition": "definition", "instruction_ledger": "ledger",
                         "fills": ["fill"], "position_actions": ["action"]},
        "source_policy": {"policy_id": "order-v1"},
        "source_order": {"candidate_id": "candidate", "order_id": "order", "position_id": "position",
                         "instrument_id": "NQ",
                         "side": "long", "order_type": "limit", "limit": 100, "q": Decimal("0.25"),
                         "quantity": 2, "placed_at": 5, "placement_known_at": 5, "as_of": 20},
    }, [definition, ledger, fill, action])
    assert result.state == "computed"
    assert result.value["filled_quantity"] == 2
    assert result.value["position_open"] is False
    assert [row["kind"] for row in result.value["order_state_timeline"]] == ["fill", "exit_fill"]


def test_derived_state_and_transition_require_exact_native_parent_roles():
    participation = parent("participation", "O107", {"source_spike": True}, known_at=10)
    response = parent("response", "O101", {"source_absorption": True}, known_at=10)
    depth = parent("depth", "O100", {"defense_interpretation": True, "depth_coverage": 4}, known_at=10)
    state = DERIVED_PRODUCERS["O165"]({
        "parent_roles": {"participation": "participation", "response": "response", "depth": "depth"},
        "state_label": "A", "state_at": 10, "observation_id": "state-1", "required_depth_levels": 4,
    }, [participation, response, depth])
    assert state.state == "supplied"
    assert state.value["state_evidence_complete"] is True

    current = parent("current", "O165", {**state.value, "observation_id": "state-1", "instrument_id": "NQ"}, known_at=10)
    nxt = parent("next", "O165", {**state.value, "state_label": "D", "state_at": 20,
                                   "observation_id": "state-2", "instrument_id": "NQ"}, known_at=20)
    condition = parent("condition", "O111", {"automatic_speed": None}, known_at=10)
    transition = DERIVED_PRODUCERS["O166"]({
        "parent_roles": {"current_state": "current", "next_state": "next", "conditioning": ["condition"]},
        "current_sequence": 4, "next_sequence": 5, "cohort_id": "cohort", "reset_id": "reset",
        "cadence": {"kind": "next-observation"},
    }, [current, nxt, condition])
    assert transition.state == "computed"
    assert transition.value["transition_valid"] is True
    assert transition.value["max_conditioning_known_at"] == 10

    swapped = DERIVED_PRODUCERS["O166"]({
        "parent_roles": {"current_state": "next", "next_state": "current", "conditioning": ["condition"]},
        "current_sequence": 4, "next_sequence": 5, "cohort_id": "cohort", "reset_id": "reset",
        "cadence": {"kind": "next-observation"},
    }, [current, nxt, condition])
    assert swapped.state == "invalid"


def test_counts_alone_never_certify_actual_transition_p27():
    counts = {"B": 4, "A": 12, "D": 84, "E": 0, "W": 0}
    arithmetic_only = run("O166", counts=counts, row_count=100,
                          source_symbol="AAPL", source_counts_symbol="AAPL", known_at=30)
    assert arithmetic_only.value["probabilities"]["D"] == Decimal("0.84")
    assert arithmetic_only.value["conditioning_causal"] is None
    assert arithmetic_only.value["transition_valid"] is None
    assert arithmetic_only.state == "hole"


def test_transition_requires_actual_adjacent_state_records_declared_cadence_and_current_conditioning():
    counts = {"B": 4, "A": 12, "D": 84, "E": 0, "W": 0}
    current = {"state_id": "s10", "state_label": "D", "state_at": 10, "known_at": 10,
               "sequence": 10, "instrument_id": "AAPL", "cohort_id": "cohort", "reset_id": "r"}
    nxt = {"state_id": "s11", "state_label": "A", "state_at": 20, "known_at": 20,
           "sequence": 11, "instrument_id": "AAPL", "cohort_id": "cohort", "reset_id": "r"}
    result = run("O166", counts=counts, source_counts_symbol="AAPL",
                 current_observation=current, next_observation=nxt,
                 cadence={"kind": "next_source_observation", "version": "v1"},
                 conditioning_evidence=[{"evidence_id": "pace", "known_at": 9}])
    assert result.value["transition_valid"] is True
    assert result.value["conditioning_causal"] is True
    assert result.known_at == 20

    gap = run("O166", counts=counts, source_counts_symbol="AAPL",
              current_observation=current, next_observation={**nxt, "sequence": 12},
              cadence="next", conditioning_evidence=[{"known_at": 9}])
    assert gap.state == "invalid"
    future = run("O166", counts=counts, source_counts_symbol="AAPL",
                 current_observation=current, next_observation=nxt, cadence="next",
                 conditioning_evidence=[{"known_at": 11}])
    assert future.state == "invalid"
    assert future.value["conditioning_causal"] is False
