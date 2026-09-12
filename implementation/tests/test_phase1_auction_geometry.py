"""Exact auction geometry and route invariants for O078--O097."""

from datetime import date
from decimal import Decimal
from types import MappingProxyType

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.native_resolution import ResolvedMembers
from trading_research.research.method_pack.objects.auction_geometry import (
    HALF_HOUR_NS, OUTPUT_SCHEMAS, REGISTRATION_OVERRIDES, TPOProfile, derived_auction,
    native_o083,
    o078, o079, o080, o081, o082, o083, o084, o085, o086, o087, o088,
    o089, o090, o091, o092, o093, o094, o095, o096, o097,
)


DAY = date(2026, 1, 15)
OPEN = et_ns(DAY, 9, 30)
MIN = 60 * 1_000_000_000


def _assert_schema(result):
    if result.state == "invalid" and not result.value:
        return
    schema = OUTPUT_SCHEMAS[result.recipe_id]
    assert schema.keys() <= result.value.keys()
    for name, field in schema.items():
        value = result.value[name]
        assert value is not None or field.nullable, (result.recipe_id, name)
        if value is not None:
            assert type(value) in field.types, (result.recipe_id, name, type(value), field.types)


def _base_rows():
    return {"100": ["A", "B"], "101": ["C"], "102": ["C"],
            "103": ["C", "D"], "104": ["D"]}


def test_tpo_distinct_period_membership_and_whole_A_are_dated_and_causal():
    events = [
        {"event_id": "a1", "price": 100, "letter": "A", "t": OPEN+5*MIN},
        {"event_id": "a2", "price": 100, "letter": "A", "t": OPEN+10*MIN},
        {"event_id": "a3", "price": 99, "letter": "A", "t": OPEN+29*MIN},
        {"event_id": "b1", "price": 100, "letter": "B", "t": OPEN+35*MIN},
    ]
    result = o078({"profile_id": "p", "instrument_id": 7, "instrument_definition_id": "d",
        "session_date_et": DAY.isoformat(), "price_step": 1, "construction": "trade_visited",
        "visits": events, "price": 100, "as_of": OPEN+60*MIN, "coverage_ok": True})
    assert result.value["members"] == [f"{DAY}:A", f"{DAY}:B"]
    assert result.value["count"] == 2
    assert result.value["a_low"] == 99
    assert result.value["a_period_complete"] is True
    assert result.value["a_end_at"] == OPEN+30*MIN
    _assert_schema(result)

    early = o078({"profile_id": "p", "instrument_id": 7, "instrument_definition_id": "d",
        "session_date_et": DAY.isoformat(), "price_step": 1, "construction": "trade_visited",
        "visits": events, "as_of": OPEN+29*MIN, "coverage_ok": True})
    assert early.value["a_period_complete"] is False
    assert early.value["a_low"] is None


def test_tpo_period_range_requires_selected_complete_grid_construction():
    result = o078({"profile_id": "p", "instrument_id": "NQ", "instrument_definition_id": "nq-def",
        "session_date_et": DAY.isoformat(), "price_step": Decimal(".25"), "construction": "period_range",
        "observations": [{"bar_id": "A", "start": OPEN, "end": OPEN+30*MIN,
                          "L": 100, "H": Decimal("100.5"), "complete": True}],
        "as_of": OPEN+30*MIN, "coverage_ok": True})
    assert result.value["memberships"] == {
        "100.00": [f"{DAY}:A"], "100.25": [f"{DAY}:A"], "100.50": [f"{DAY}:A"]}
    no_construction = o078({"session_date_et": DAY.isoformat(), "price_step": 1,
        "visits": [{"price": 100, "t": OPEN+MIN}], "as_of": OPEN+30*MIN, "coverage_ok": True})
    assert "HOLE:O078:construction" in no_construction.hole_ids


def test_tpo_period_range_aggregates_every_complete_member_and_freezes_asof():
    observations = []
    for minute in range(30):
        low = Decimal("99.00") if minute == 3 else Decimal("100.00")
        high = Decimal("101.00") if minute == 7 else Decimal("100.25")
        observations.append({"bar_id": f"A-{minute}", "start": OPEN+minute*MIN,
            "end": OPEN+(minute+1)*MIN, "L": low, "H": high,
            "complete": True, "known_at": OPEN+(minute+1)*MIN})
    inputs = {"profile_id": "p", "instrument_id": "NQ", "instrument_definition_id": "nq-def",
        "session_date_et": DAY.isoformat(), "price_step": Decimal(".25"),
        "construction": "period_range", "observations": observations,
        "as_of": OPEN+30*MIN, "coverage_ok": True}
    result = o078(inputs)
    assert result.value["a_low"] == Decimal("99.00")
    assert result.value["a_high"] == Decimal("101.00")
    assert result.value["period_ranges"][0]["L"] == Decimal("99.00")
    assert len(result.value["event_ids"]) == 30

    future = [*observations, {"bar_id": "B-future", "start": OPEN+30*MIN,
        "end": OPEN+31*MIN, "L": 1, "H": 999, "complete": True,
        "known_at": OPEN+31*MIN}]
    assert o078({**inputs, "observations": future}).value == result.value

    late = [dict(row) for row in observations]
    late[3]["known_at"] = OPEN+31*MIN
    clipped = o078({**inputs, "observations": late})
    assert clipped.value["completed_periods"] == []
    assert clipped.value["memberships"] == {}
    assert clipped.coverage_ok is None
    assert "HOLE:O078:coverage" in clipped.hole_ids
    uncovered = o078({**inputs, "coverage_ok": None})
    assert uncovered.value["completed_periods"] == []
    assert uncovered.value["memberships"] == {}
    _assert_schema(result); _assert_schema(clipped); _assert_schema(uncovered)


def test_single_prints_only_use_supplied_interior_and_later_repair_snapshot():
    base = {"memberships": _base_rows(), "interior_band": [101, 102],
            "lower_accepted_id": "lower", "upper_accepted_id": "upper",
            "formation_known_at": 10, "repair_policy": "any_later_letter", "as_of": 15}
    result = o079(base)
    assert [row["price"] for row in result.value["single_letter_rows"]] == [101, 102]
    assert result.value["letter_ids"] == ["C"]
    assert result.value["outer_tail_excluded"] is True
    repaired = o079({**base, "repairs": [{"price": 101, "letter": "D", "at": 20}], "as_of": 21})
    assert [row["price"] for row in repaired.value["single_letter_rows"]] == [102]
    assert repaired.value["repair_state"] == "repaired"
    _assert_schema(repaired)


def test_excess_and_poor_extremes_are_side_specific_and_grid_adjacent():
    high = o080({"memberships": {"102": ["B", "D"], "103": ["D"], "104": ["D"]},
        "side": "high", "price_step": 1, "source_criterion": "same_letter_tail_min_2",
        "instrument_id": "NQ", "grid_id": "tick", "known_at": 10})
    assert high.value["tail_length_rows"] == 2 and high.value["source_excess"] is True
    mixed = o080({"memberships": {"102": ["B", "D"], "103": ["C"], "104": ["D"]},
        "side": "high", "price_step": 1, "source_criterion": "same_letter_tail_min_2",
        "instrument_id": "NQ", "grid_id": "tick"})
    assert mixed.value["source_excess"] is False
    poor = o081({"memberships": {"103": ["B", "D"], "104": ["D"]}, "side": "high",
        "price_step": 1, "instrument_root": "NQ", "criterion": "nq_one_row_tail",
        "source_grid_compatible": True})
    assert poor.value["poor_high"] is True and poor.value["poor_low"] is False
    unknown_es = o081({"memberships": {"103": ["B", "D"], "104": ["D"]}, "side": "high",
        "price_step": 1, "instrument_root": "ES", "source_grid_compatible": True})
    assert unknown_es.value["poor_high"] is None and "HOLE:O081:criterion" in unknown_es.hole_ids
    _assert_schema(high); _assert_schema(poor); _assert_schema(unknown_es)


def test_initial_balance_waits_for_complete_A_and_B_and_keeps_later_extension_separate():
    result = o082({"ib_id": "ib", "A": {"H": 110, "L": 100, "complete": True, "end": OPEN+30*MIN},
        "B": {"H": 108, "L": 99, "complete": True, "end": OPEN+60*MIN},
        "later_high": 112, "later_low": 98, "later_known_at": OPEN+90*MIN})
    assert result.value["ibh"] == 110 and result.value["ibl"] == 99 and result.value["ibw"] == 11
    assert result.value["upper_extension"] == 2 and result.value["lower_extension"] == 1
    assert result.value["later_break_flags"]["both_broken"] is True
    incomplete = o082({"A": {"H": 110, "L": 100, "complete": True},
                       "B": {"H": 108, "L": 99, "complete": False}})
    assert incomplete.coverage_ok is None and "HOLE:O082:complete_A_B" in incomplete.hole_ids
    _assert_schema(result); _assert_schema(incomplete)


def test_open_type_uses_full_elapsed_path_and_never_backdates_label():
    result = o083({"cash_open": 100, "open_at": OPEN, "as_of": OPEN+2*MIN,
        "path": [{"t": OPEN+20*1_000_000_000, "price": 99}, {"t": OPEN+2*MIN, "price": 102}],
        "claim_side": "long", "coverage_ok": True, "observation_end": OPEN+2*MIN,
        "source_type_criterion": "supplied_case", "source_open_type": "open_drive",
        "type_known_at": OPEN+2*MIN, "final": False})
    assert result.value["crossed_open_by_asof"] is True
    assert result.value["provisional"] is True
    future = o083({**{k: v for k, v in result.value.items() if k in ()},
        "cash_open": 100, "open_at": OPEN, "as_of": OPEN+MIN, "path": [], "claim_side": "long",
        "coverage_ok": True, "observation_end": OPEN+MIN, "source_type_criterion": "x",
        "source_open_type": "open_drive", "type_known_at": OPEN+2*MIN})
    assert future.state == "invalid"
    _assert_schema(result)


def test_native_open_price_is_unknown_when_first_timestamp_has_unordered_prices():
    rows = [
        {"event_ns": OPEN+1, "event_id": "first-a", "action": "T", "price": Decimal("100"),
         "known_at": OPEN+1},
        {"event_ns": OPEN+1, "event_id": "first-b", "action": "T", "price": Decimal("101"),
         "known_at": OPEN+1},
        {"event_ns": OPEN+2, "event_id": "later", "action": "T", "price": Decimal("102"),
         "known_at": OPEN+2},
    ]
    resolved = ResolvedMembers(tuple(MappingProxyType(row) for row in rows), "NQ", OPEN,
                               OPEN+MIN, OPEN+MIN, True, ())
    result = native_o083({"as_of": OPEN+MIN}, resolved)
    assert result.state == "hole"
    assert result.value["cash_open"] is None
    assert result.value["crossed_open_by_asof"] is None
    assert result.hole_ids == ["HOLE:O083:cash_open_order"]
    assert result.evidence_ids == ["first-a", "first-b"]
    _assert_schema(result)


def test_provisional_and_final_day_types_are_separate_observations():
    result = o084({"author": "Sires", "taxonomy": "Sires-AMT", "provisional_type": "balance",
        "provisional_known_at": OPEN+30*MIN, "evidence_until": OPEN+30*MIN,
        "final_type": "trend", "final_known_at": OPEN+13*30*MIN,
        "as_of": OPEN+45*MIN, "permission_reference": "wait"})
    assert result.value["provisional_type"] == "balance"
    assert result.value["final_type"] is None
    _assert_schema(result)


def test_shape_permission_does_not_invent_P_or_b_direction():
    result = o085({"author": "Sires", "profile_id": "p", "source_shape": "P",
        "source_permission": "context_only", "known_at": 10, "decision_at": 10})
    assert result.value["automatic_shape_direction"] is None
    assert result.value["break_retest_complete"] is False
    double = o085({"author": "Saint", "profile_id": "p", "source_shape": "double_distribution",
        "source_permission": "balance_route", "subbalance_ids": ["a"], "known_at": 10})
    assert "HOLE:O085:two_subbalances" in double.hole_ids
    _assert_schema(result); _assert_schema(double)


def test_shape_break_retest_requires_causal_order_and_decision_clock():
    reversed_sequence = o085({"author": "Sires", "profile_id": "p", "source_shape": "P",
        "source_permission": "break_retest", "known_at": 10, "break_at": 30,
        "retest_at": 20, "decision_at": 40})
    assert reversed_sequence.state == "invalid"
    assert reversed_sequence.base_ok is False
    assert reversed_sequence.hole_ids == ["HOLE:O085:ordering"]

    complete = o085({"author": "Sires", "profile_id": "p", "source_shape": "P",
        "source_permission": "break_retest", "known_at": 10, "break_at": 20,
        "retest_at": 30, "decision_at": 30})
    assert complete.value["break_retest_complete"] is True
    assert complete.known_at == 30

    no_decision = o085({"author": "Sires", "profile_id": "p", "source_shape": "P",
        "source_permission": "context_only", "known_at": 10})
    assert no_decision.state == "hole"
    assert "HOLE:O085:decision_at" in no_decision.hole_ids
    _assert_schema(complete); _assert_schema(no_decision)


def test_landmark_half_range_gap_is_distinct_from_close_gap():
    result = o086({"reference_id": "prior-high", "kind": "prior_rth_high", "price": 110,
        "period_id": "2026-01-14:RTH", "known_at": 10, "selected_role": "target",
        "current_open": 114, "prior_high": 110, "prior_low": 90, "prior_close": 105})
    assert result.value["half_range_gap"] == 112
    assert result.value["half_close_gap"] == Decimal("109.5")
    _assert_schema(result)


def test_objective_consumption_respects_scope_and_freezes_priority():
    result = o087({"objective_id": "x", "objective_type": "prior_high", "bounds": [120, 120],
        "original_known_at": 10, "decision_at": 30, "consumption_scope": "RTH",
        "consumption_rule": "touch", "history_coverage_ok": True, "priority_at_decision": 1,
        "visits": [{"objective_id": "x", "at": 20, "session": "ETH", "qualifies": True},
                   {"objective_id": "x", "at": 40, "session": "RTH", "qualifies": True}]})
    assert result.value["active_at_decision"] is True
    assert result.value["first_consumption_at"] is None
    assert result.value["subsequent_outcome"] == {"first_qualifying_visit_at": 40}
    _assert_schema(result)


def test_claim_registry_keeps_either_and_both_rates_distinct():
    cohort = ([{"onh_hit": True, "onl_hit": True}] * 3 +
              [{"onh_hit": True, "onl_hit": False}] * 3 +
              [{"onh_hit": False, "onl_hit": True}] * 2 +
              [{"onh_hit": False, "onl_hit": False}] * 2)
    result = o088({"source_claim": {"claim_id": "94", "literal_rate": Decimal(".94")},
        "claim_definition_complete": True, "observed_cohort": cohort, "known_at": 10})
    assert result.value["observed_hit_counts"] == {"n": 10, "onh": 6, "onl": 5, "both": 3, "either": 8}
    assert result.value["observed_rate"] == Decimal(".8")
    assert result.value["claim_is_trade_win_rate"] is False
    _assert_schema(result)


def test_asia_context_records_distances_without_creating_target_rule():
    result = o089({"entry": 110, "stop": 112, "target": 105, "side": "short",
        "source_case_id": "saint-case", "source_range_reference": Decimal(8),
        "rationale_known_at": 10, "source_ambition_ok": True})
    assert result.value["stop_distance"] == 2 and result.value["target_distance"] == 5
    assert result.value["automatic_target"] is None
    _assert_schema(result)


def test_rotation_and_break_retest_require_actual_order_and_same_identity():
    rotation = o090({"balance_id": "bal", "lo": 100, "hi": 110, "edge_id": "bal:low", "side": "long",
        "balance_known_at": 10, "edge_arrival_at": 20, "local_confirm_at": 22, "decision_at": 23,
        "fair_value_id": "poc", "first_fair_value_event": {"at": 40}})
    assert rotation.value["rotation_sequence"] is True
    route = o091({"boundary_id": "ledge", "retest_boundary_id": "ledge", "direction": "up",
        "boundary_known_at": 10, "break_at": 20, "accept_at": 21, "depart_at": 22,
        "retest_at": 25, "defense_at": 26, "initiative_at": 27, "decision_at": 28,
        "source_retest_held": True})
    assert route.value["break_retest_sequence"] is True and route.value["same_boundary"] is True
    assert route.value["same_boundary_retest_held"] is True
    assert route.value["buyers_defend_same_imbalance_band"] is True
    assert route.value["ltf_balance_known_at"] == 10
    wrong = o091({"boundary_id": "ledge", "retest_boundary_id": "other", "direction": "up",
        "boundary_known_at": 10, "break_at": 20, "accept_at": 21, "depart_at": 22,
        "retest_at": 25, "defense_at": 26, "initiative_at": 27, "decision_at": 28,
        "source_retest_held": True})
    assert wrong.state == "invalid"
    _assert_schema(rotation); _assert_schema(route)


def test_reacceptance_needs_two_consecutive_complete_half_hours_and_both_bounds():
    periods = [
        {"L": 102, "H": 109, "start": OPEN, "end": OPEN+HALF_HOUR_NS, "complete": True},
        {"L": 101, "H": 108, "start": OPEN+HALF_HOUR_NS, "end": OPEN+2*HALF_HOUR_NS, "complete": True},
    ]
    result = o092({"area_id": "va", "val": 100, "vah": 110, "outside_before": "above",
        "return_at": OPEN+MIN, "inside_observations": periods,
        "acceptance_definition": "two_consecutive_complete_30m_whole_range_inside",
        "next_objective_id": "poc"})
    assert result.value["reacceptance_sequence"] is True
    outside = o092({**{k: v for k, v in {"area_id": "va", "val": 100, "vah": 110,
        "outside_before": "above", "return_at": OPEN+MIN,
        "acceptance_definition": "two_consecutive_complete_30m_whole_range_inside",
        "next_objective_id": "poc"}.items()},
        "inside_observations": [periods[0], {**periods[1], "H": 111}]})
    assert outside.value["reacceptance_sequence"] is False
    _assert_schema(result); _assert_schema(outside)


def test_failed_auction_routes_keep_sires_and_saint_sequences_distinct():
    sires = o093({"established_balance_id": "new", "older_profile_id": "old",
        "established_vah": 110, "established_val": 100, "older_poc": 115,
        "balance_known_at": 10, "break_at": 20, "older_poc_tag_at": 25, "tag_price": 115,
        "reject_at": 26, "decision_at": 27, "rejection_from": "above",
        "source_rejection_observed": True, "source_target_id": "new:vah", "source_target_price": 110})
    assert sires.value["fa_sequence"] is True and sires.value["source_target_price"] == 110
    saint = o094({"original_value_id": "original", "tested_value_id": "older",
        "explore_at": 20, "failure_at": 30, "return_at": 40, "reaccept_at": 45,
        "control_at": 47, "decision_at": 48, "source_failure_observed": True,
        "source_reacceptance_observed": True, "current_control_side": "long"})
    assert saint.value["saint_fa_sequence"] is True
    assert saint.value["older_poc_tag_required"] is False
    _assert_schema(sires); _assert_schema(saint)


def test_poc_attempts_are_distinct_and_retest_must_be_available():
    result = o095({"profile_id": "p", "poc": 105, "as_of": 55, "decision_at": 55,
        "tests": [{"attempt_id": "a", "at": 40, "failed": True},
                  {"attempt_id": "a", "at": 41, "failed": True},
                  {"attempt_id": "b", "at": 45, "failed": True}],
        "passage_at": 50, "held_retest_at": 52, "source_efficient_passage": True,
        "current_poc_read": "efficient_passage", "next_objective_id": "far"})
    assert result.value["test_ids"] == ["a", "b"] and result.value["failed_test_count"] == 2
    assert result.value["held_retest_at"] == 52
    future = o095({**{k: v for k, v in result.value.items() if k in ()}, "profile_id": "p", "poc": 105,
        "decision_at": 51, "passage_at": 50, "held_retest_at": 52,
        "source_efficient_passage": True, "current_poc_read": "efficient_passage", "next_objective_id": "far"})
    assert future.state == "invalid"
    _assert_schema(result)


def test_whole_balance_traversal_has_no_30_minute_cap_and_control_is_causal():
    result = o096({"balance_id": "bal", "lo": 100, "hi": 110, "direction": "up",
        "traverse_start": 10, "traverse_end": 10+40*MIN, "entry_boundary_id": "low",
        "exit_boundary_id": "high", "path_coverage_ok": True, "hold_definition": "source",
        "no_source_hold": True, "retest_at": 10+45*MIN, "control_at": 10+46*MIN,
        "decision_at": 10+47*MIN})
    assert result.value["traverse_duration"] == 40*MIN
    assert result.value["whole_balance_crossed"] is True
    assert result.value["maximum_duration"] is None
    assert result.value["route_sequence"] is True
    _assert_schema(result)


def test_alignment_requires_live_thesis_current_control_and_same_area():
    common = {"author": "Saint", "htf_thesis_id": "t", "htf_side": "long",
        "htf_area_id": "area", "local_area_id": "area", "thesis_alive": True,
        "thesis_known_at": 10, "control_at": 20, "decision_at": 21,
        "free_two_sided_chop": False}
    opposed = o097({**common, "ltf_side": "short"})
    aligned = o097({**common, "ltf_side": "long"})
    dead = o097({**common, "ltf_side": "long", "thesis_died_at": 19})
    assert opposed.value["alignment_ok"] is False
    assert aligned.value["alignment_ok"] is True
    assert dead.value["thesis_alive"] is False and dead.value["alignment_ok"] is False
    _assert_schema(opposed); _assert_schema(aligned); _assert_schema(dead)


def test_every_assigned_recipe_has_an_override_and_complete_schema():
    ids = {f"O{number:03}" for number in range(78, 98)}
    assert REGISTRATION_OVERRIDES.keys() == ids
    assert OUTPUT_SCHEMAS.keys() == ids


def _parent(object_id, recipe_id, value, known_at=10, *, evidence_class="resolved_native",
            side=None, band_id=None):
    return {"object_id": object_id, "recipe_id": recipe_id, "value": value,
            "known_at": known_at, "state": "computed", "evidence_class": evidence_class,
            "evidence_ids": [f"ev:{object_id}"], "recipe_coverage_ok": True,
            "side": side, "band_id": band_id, "author": "Saint"}


def test_derived_single_prints_use_actual_tpo_and_cited_selection_parents():
    tpo = _parent("tpo", "O078", {"memberships": _base_rows(), "as_of": 20,
        "price_step": Decimal(1), "instrument_id": "NQ"}, 20)
    selection = _parent("selection", "O022", {"interior_band": [101, 102],
        "lower_accepted_id": "lower", "upper_accepted_id": "upper",
        "repair_policy": "any_later_letter"}, 10, evidence_class=None)
    selection["state"] = "supplied"
    result = derived_auction("O079", {"tpo_parent_id": "tpo", "selection_parent_id": "selection"},
                             [tpo, selection])
    assert [row["price"] for row in result.value["single_letter_rows"]] == [101, 102]
    assert result.parent_ids == ["tpo", "selection"]


def test_derived_alignment_uses_parent_sides_areas_and_availability():
    thesis = _parent("thesis", "O135", {"thesis_alive": True}, 10,
                     evidence_class=None, side="long", band_id="area")
    thesis["state"] = "supplied"
    control = _parent("control", "O120", {"free_two_sided_chop": False}, 20,
                      evidence_class=None, side="short", band_id="area")
    control["state"] = "supplied"
    result = derived_auction("O097", {"thesis_parent_id": "thesis",
        "control_parent_id": "control", "use_at": 21}, [thesis, control])
    assert result.value["same_area"] is True
    assert result.value["alignment_ok"] is False
    future = derived_auction("O097", {"thesis_parent_id": "thesis",
        "control_parent_id": "control", "use_at": 19}, [thesis, control])
    assert future.state == "invalid"
