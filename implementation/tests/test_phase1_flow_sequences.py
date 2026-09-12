from decimal import Decimal

from trading_research.research.method_pack.contracts import OUTPUT_SCHEMAS as CONTRACT_SCHEMAS
from trading_research.research.method_pack.contracts import validate_output
from trading_research.research.method_pack.objects.flow_sequences import (
    DERIVED_PRODUCERS, FLOW_SEQUENCE_SCHEMAS, OUTPUT_SCHEMAS, REGISTRATION_OVERRIDES,
)


def run(rid, **values):
    return REGISTRATION_OVERRIDES[rid](values)


def test_every_flow_sequence_payload_is_complete_and_typed_even_when_unavailable():
    prior=dict(CONTRACT_SCHEMAS)
    try:
        CONTRACT_SCHEMAS.update(OUTPUT_SCHEMAS)
        for rid, producer in REGISTRATION_OVERRIDES.items():
            result=producer({})
            assert set(FLOW_SEQUENCE_SCHEMAS[rid]) <= set(result.value)
            validate_output(result)
    finally:
        CONTRACT_SCHEMAS.clear(); CONTRACT_SCHEMAS.update(prior)


def test_dom_rejection_needs_all_local_checks_and_required_stage_order():
    result=run("O121", branch_id="dom", band_id="b", band=[100,101], side="long",
        stage_ledger={"aggression":1,"rejection":2,"added_participation":3,"decision":4},
        checks={"arriving_aggression":True,"little_progress":True,"local_rejection":True,"source_dom_confirmation":True})
    assert result.value["branch_ok"] is True
    missing=run("O121", branch_id="dom", band_id="b", stage_ledger={"aggression":1,"rejection":2,"decision":4},
        checks={"arriving_aggression":True,"little_progress":True,"local_rejection":True,"source_dom_confirmation":True})
    assert missing.value["branch_ok"] is None


def test_strict_absorption_keeps_directional_reward_return_and_new_defense_distinct():
    checks={"passive_wall_confirmed":True,"opposing_effort_no_result":True,"own_reward_confirmed":True,
        "reward_near_origin":True,"fresh_reward_retest_defended":True,"cvd_filter_ok":True,"delta_filter_ok":True}
    good=run("O122", branch_id="abs", band_id="b", side="long", support=100,
        stage_ledger={"absorption":1,"reward":2,"reward_return":3,"renewed_defense":4,"decision":5}, checks=checks)
    assert good.value["strict_reversal_sequence"] is True
    tied=run("O122", branch_id="abs", band_id="b", side="long", support=100,
        stage_ledger={"absorption":1,"reward":2,"reward_return":2,"renewed_defense":4,"decision":5}, checks=checks)
    assert tied.state == "invalid"


def test_stop_branch_enforces_two_to_four_reward_zero_to_two_entry_and_daily_gate_p17():
    flags={"defense":True,"replenishment":True,"opponent_thinning":True,"absorber_aggressive":True,"lift_off":True}
    base=dict(branch_id="stop", band_id="b", side="long", origin=100, confirm_price=Decimal("100.75"),
        entry=101, q=Decimal("0.25"), daily_r_before=-3,
        stage_ledger={"defense":1,"replenishment":2,"exhaustion":3,"liftoff":4,"decision":5}, checks=flags)
    assert run("O123",**base).value["branch_ok"] is True
    assert run("O123",**{**base,"confirm_price":100}).value["reward_gate_ok"] is False
    assert run("O123",**{**base,"confirm_price":Decimal("101.25")}).value["reward_gate_ok"] is False
    assert run("O123",**{**base,"entry":Decimal("101.5")}).value["entry_gate_ok"] is False
    assert run("O123",**{**base,"daily_r_before":-4}).value["daily_stop_ok"] is False


def test_footprint_route_requires_same_candle_all_checks_and_order():
    flags={"candle_delta_disagreement":True,"local_absorption":True,"intrabar_poc_flip":True,"source_flow_confirmation":True}
    good=run("O124",branch_id="fp",candle_id="k",footprint_snapshot_ids=["s1","s2"],
        stage_ledger={"disagreement":1,"poc_flip":2,"flow_confirmation":3,"decision":4},checks=flags)
    assert good.value["route_ok"] is True
    wrong=run("O124",branch_id="fp",candle_id="k",poc_candle="other",footprint_snapshot_ids=["s1","s2"],
        stage_ledger={"disagreement":1,"poc_flip":2,"flow_confirmation":3,"decision":4},checks=flags)
    assert wrong.state == "invalid"


def test_vwap_deviation_fade_is_mirrored_and_target_is_frozen():
    checks={"source_vwap_known":True,"selected_deviation_touched":True,"absorption_at_that_band":True,"ladder_confirmation":True}
    common=dict(branch_id="vwap",vwap_snapshot_id="v",band_snapshot_id="b",target_snapshot_id="t",vwap=100,sigma=2,k=2,
        target=100,stage_ledger={"band_known":1,"touch":2,"absorption":3,"ladder_confirmation":4,"decision":5},checks=checks)
    assert run("O125",**common,side="short",selected_band="upper").value["selected_band_price"] == 104
    lower=run("O125",**common,side="long",selected_band="lower",later_vwap=101)
    assert lower.value["selected_band_price"] == 96 and lower.value["target"] == 100
    assert lower.value["later_rewrites_target"] is False


def test_passive_ofm_is_long_only_and_false_dying_tape_cannot_qualify_p18():
    checks={"source_squeeze_failed":True,"tape_died_at_failure":False,"no_aggression_at_failure":True,
        "buyers_area_identified":True,"entry_above_buyers":True,"stop_below_aggression":True}
    result=run("O127",branch_id="passive",buyers_area_id="buyers",buyers_area=[100,101],side="long",
        entry=Decimal("101.25"),stop=Decimal("99.75"),aggression_low=100,
        stage_ledger={"failure":1,"entry_trigger":2,"decision":3},checks=checks,r_multiple=2)
    assert result.value["qualification"] is False and result.value["branch_ok"] is False
    assert run("O127",**{**result.value,"branch_id":"passive","side":"short","entry":99,"stop":101,
        "stage_ledger":{"failure":1,"entry_trigger":2,"decision":3},"checks":{**checks,"tape_died_at_failure":True}}).value["branch_ok"] is False


def test_clean_squeeze_reads_only_complete_prior_failure_history_p19():
    flags={"catalyst_known":True,"fast_release":True,"opposing_pullback_aggression_absorbed":True,"continuation_confirmed":True}
    common=dict(branch_id="clean",origin_id="o",side="long",stage_ledger={"catalyst":1,"release":2,"pullback":3,"confirmation":4,"decision":5},checks=flags)
    unknown=run("O128",**common,failure_history={"coverage_complete":False,"events":[]})
    assert unknown.value["no_prior_failure"] is None
    prior=run("O128",**common,failure_history={"coverage_complete":True,"events":[{"failure_id":"f","at":2,"failed":True}]})
    assert prior.value["no_prior_failure"] is False and prior.value["branch_ok"] is False
    clear=run("O128",**common,failure_history={"coverage_complete":True,"events":[]},later_failure_at=9)
    assert clear.value["branch_ok"] is True and clear.value["later_failure_invalidates"] is False


def test_long_gamma_failure_does_not_inherit_own_reward_requirement():
    checks={"balance_context":True,"failed_aggression_at_extreme":True,"left_failed_area":True,
        "retest_same_failed_area":True,"aggression_still_unrewarded":True,"target_is_prior_opposite_control":True}
    result=run("O129",branch_id="fade",balance_id="bal",failed_area_id="f",band=[100,110],side="short",long_gamma=True,
        stage_ledger={"failure":1,"departure":2,"same_area_return":3,"decision":4},checks=checks,target=103,target_id="control")
    assert result.value["branch_ok"] is True and result.value["requires_lift"] is False


def test_continuation_requires_fresh_same_band_defense_and_current_thesis_side():
    flags={"prior_band_control":True,"same_band_retest":True,"fresh_same_side_defense":True,
        "executed_aggression":True,"refresh_consistent":True,"control_side_matches_thesis":False}
    result=run("O130",branch_id="cont",thesis_id="th",band_id="b",band=[109,110],side="short",
        stage_ledger={"prior_defense":1,"same_band_return":2,"fresh_defense":3,"decision":4},checks=flags)
    assert result.value["branch_ok"] is False


def test_microbalance_target_must_be_preexisting_and_dated_p20():
    common=dict(branch_id="micro",microbalance_id="m",target_id="t",micro_low=100,micro_high=102,
        side="long",stop=Decimal("99.75"),target=120,directional_strength=True,breakout_in_thesis_direction=True,
        microbalance_frozen=True)
    missing=run("O131",**common,stage_ledger={"target_known":None,"microbalance_known":2,"breakout":3,"decision":4})
    assert missing.value["objective_preexists"] is False or missing.value["objective_preexists"] is None
    good=run("O131",**common,target_known_at=1,
        stage_ledger={"target_known":1,"microbalance_known":2,"breakout":3,"decision":4})
    assert good.value["branch_ok"] is True and good.value["stop_side_ok"] is True
    late=run("O131",**common,target_known_at=5,
        stage_ledger={"target_known":5,"microbalance_known":2,"breakout":3,"decision":4})
    assert late.state == "invalid"

    thin = run("O131", micro_lo=100, micro_hi=102, microbalance_known_at=2,
               entry=103, stop=Decimal("99.75"), target=120, side="long")
    assert thin.value["microbalance_frozen"] is None
    assert thin.value["branch_ok"] is None
    assert "HOLE:O131:microbalance_frozen" in thin.hole_ids


def test_kg1_management_keeps_initial_risk_and_later_action_time():
    result=run("O132",branch_id="kg1",kg1_level_id="kg",kg1_known_at=1,side="long",
        stage_ledger={"kg1_known":1,"retest":2,"confirmation":3,"decision":4},entry=100,stop=90,target=Decimal("106.9"),
        management_records=[{"action_id":"a","at":5,"stop":95,"target":Decimal("109.15")}])
    assert result.value["ratio"] == Decimal("0.69") and result.value["later_ratio"] == Decimal("1.83")
    assert result.value["original_risk"] == 10


def test_early_loss_and_third_test_loss_remain_in_case_cohort():
    early=run("O133",branch_id="early",case_id="c",thesis_id="thesis",checks={"thesis_alive":True,"preconfirmation_entry":True,
        "small_risk_declared":True,"stop_predefined":True,"explicitly_early_entry":True,"source_refill_return":True,"source_risk_predefined":True},
        stage_ledger={"risk_declared":1,"early_choice":2,"entry":3,"full_confirmation":5,"outcome":4})
    assert early.value["case_fidelity"] is True and early.value["full_confirmed_branch_pass"] is False
    tests=[{"test_id":"a","return_at":1,"departure_at":2,"band_id":"b"},
           {"test_id":"b","return_at":3,"departure_at":4,"band_id":"b"},
           {"test_id":"c","return_at":5,"departure_at":6,"band_id":"b"}]
    third=run("O134",branch_id="third",case_id="c",band_id="b",test_episodes=tests,
              no_new_buyer_defense=True,stopped_out=True)
    assert third.value["distinct_test_count"] == 3 and third.value["case_fidelity"] is True
    assert third.value["in_cohort"] is True


def test_late_resistance_case_preserves_upward_approach_and_source_hole():
    result=run("O135",branch_id="late",case_id="c",resistance_id="r",resistance=110,
        resistance_known_at=1,entry_at=5,approach_events=[{"at":2,"price":109},{"at":3,"price":110}],
        source_exhaustion=True,side="short",small_risk=True,session_end_at=6)
    assert result.value["short_case_fidelity"] is True
    assert result.value["automatic_entry_selector"] is None and result.state == "hole"


def test_directional_read_requires_support_identity_and_never_uses_later_event():
    missing = run("O136", bias_at=2, use_at=4)
    assert missing.state == "hole"
    assert missing.value["bias_recorded"] is None

    result=run("O136",bias_at=2,direction="long",origin_reference_id="pdl",support_event_id="reclaim",
        linked_candidate_ids=["c"],candidate_side="long",use_at=4,later_event_at=9)
    assert result.value["bias_recorded"] is True and result.value["later_event_explains_bias"] is False
    late=run("O136",bias_at=5,direction="long",origin_reference_id="pdl",support_event_id="reclaim",use_at=4)
    assert late.state == "invalid"


def test_thin_legacy_stage_flags_do_not_create_a_stop_branch_p17():
    result = run("O123", origin=100, confirm_px=Decimal("100.75"), entry=101,
                 q=Decimal("0.25"), daily_r=-3)
    assert result.state == "hole"
    assert result.value["stage_evidence_ok"] is None
    assert result.value["branch_ok"] is None
    assert result.value["branch_id"] is None


def test_clean_squeeze_without_complete_failure_history_stays_unknown_p19():
    result = run("O128", first_pullback_at=3, entry_at=5,
                 catalyst_at=1, release_at=2, confirm_at=4)
    assert result.state == "hole"
    assert result.value["no_prior_failure"] is None
    assert result.value["branch_ok"] is None
    assert result.value["branch_id"] is None


def test_derived_flow_does_not_copy_unproven_output_fields_from_config():
    support={"object_id":"support-1","recipe_id":"O047","value":{"side":"long"},
             "known_at":2,"state":"computed","recipe_base_ok":True,"recipe_coverage_ok":True}
    result=DERIVED_PRODUCERS["O136"](
        {"parent_roles":{"support":"support-1"},"candidate_side":"long","use_at":4,
         "direction":"short","revision_history":[{"injected":True}],
         "linked_candidate_ids":["injected"],"later_event_at":3}, [support])
    assert result.value["direction"] == "long"
    assert result.value["revision_history"] == []
    assert result.value["linked_candidate_ids"] == []
    assert result.value["later_event_at"] is None
