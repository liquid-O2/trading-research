from decimal import Decimal

from trading_research.research.method_pack.catalog import BRANCHES, objects_for
from trading_research.research.method_pack.method_slices import m09


def _rows():
    return {row["id"]: row for row in m09.method_fixtures()}


def test_m09_inventory_and_separate_units():
    assert len(objects_for("REFILL-STUDY")) == 27
    assert BRANCHES["REFILL-STUDY"] == ["touch_record", "supplied_selected_order"]
    rows = _rows()
    assert len(rows) == 10
    assert all(row["status"] == "pass" for row in rows.values())
    assert rows["M09-F1"]["predicate"] == "touch_causality"
    assert rows["M09-F1-order"]["predicate"] == "selected_order_configuration"
    assert rows["M09-F1"]["actual_value"]["verdict"] == "pass"
    assert rows["M09-F1-order"]["actual_value"]["verdict"] == "pass"


def test_m09_f1_actual_zone_departure_return_and_label_timing():
    row = _rows()["M09-F1"]
    payload = row["inputs"]["evidence"][0]["payload"]
    assert payload["zone"] == ["100", "101"]
    assert payload["zone_id"] == payload["departure_zone_id"] == payload["touch_zone_id"]
    assert payload["formation_id"] != payload["touch_id"]
    assert payload["departure_price"] == "102" and payload["touch_price"] == "100.5"
    actual = row["actual_value"]
    values = {field: binding["value"] for field, binding in actual["operands"].items()}
    assert values["zone_known_at"] < values["departure_at"] < values["touch_at"]
    assert values["feature_max_known_at"] < values["touch_at"]
    assert payload["prior_touch_records"][0]["resolved_at"] <= values["feature_max_known_at"]
    assert payload["label_resolved_at"] > values["touch_at"]


def test_m09_selected_order_preserves_literal_configuration_and_cohorts():
    row = _rows()["M09-F1-order"]
    actual = row["actual_value"]
    values = {field: binding["value"] for field, binding in actual["operands"].items()}
    assert [values[name] for name in ("order_inside_ticks", "stop_ticks", "target_ticks",
                                      "cancel_minutes", "round_trip_cost_ticks",
                                      "stop_slippage_ticks")] == ["12", "32", "96", "30", "1", "1"]
    assert values["one_position_policy"] is True
    payload = row["inputs"]["evidence"][0]["payload"]
    candidates = {candidate["candidate_id"]: candidate for candidate in row["inputs"]["candidates"]}
    order = candidates["M09-F1-order"]
    parent = candidates[order["parent_attempt_id"]]
    assert order["predicate"] == "selected_order_configuration"
    assert parent["predicate"] == "touch_causality"
    assert order["touch_id"] == parent["touch_id"] == payload["parent_touch_id"]
    assert payload["parent_touch_id"] == payload["touch_id"]
    assert (payload["signal_count"], payload["fill_count"]) == (312, 64)
    assert payload["signal_cohort_id"] != payload["fill_cohort_id"]
    assert payload["paired_cohort_claim"] is False
    assert payload["later_ofm_causal_status"] == "negative"
    assert payload["profit_reconstructed"] is False


def test_m09_observed_negative_controls_fail_without_flat_false_flags():
    rows = _rows()
    future = rows["M09-F2-future-memory"]["actual_value"]
    assert future["sequence_ok"] is True and future["verdict"] == "fail"
    assert any("current/future" in hole["reason"] for hole in future["holes"])
    grade = rows["M09-F2-future-grade"]["actual_value"]
    assert grade["sequence_ok"] is True and grade["verdict"] == "fail"
    assert any("not frozen" in hole["reason"] for hole in grade["holes"])
    paired = rows["M09-F2-paired-cohorts"]["actual_value"]
    assert paired["sequence_ok"] is True and paired["verdict"] == "fail"
    assert any("distinct cohorts" in hole["reason"] for hole in paired["holes"])


def test_m09_holes_and_c08_mutations_keep_unknown_fail_distinction():
    rows = _rows()
    for fid in ("M09-F3-zone", "M09-F3-grade", "M09-F1:missing"):
        assert rows[fid]["actual_value"]["verdict"] == "unknown"
        assert rows[fid]["actual_value"]["hole_ids"]
    late = rows["M09-F1:late"]["actual_value"]
    assert late["verdict"] == "fail" and late["detected_causal_violations"] == 2
    identity = rows["M09-F1:identity"]["actual_value"]
    assert identity["verdict"] == "fail"
    assert any(hole["kind"] == "identity" for hole in identity["holes"])


def test_all_m09_objects_have_passing_numeric_and_c08_fixtures():
    from trading_research.research.method_pack.objects import FIXTURES, RECIPES, run_object_fixtures

    ids = objects_for("REFILL-STUDY")
    assert set(ids) <= set(RECIPES)
    assert set(ids) <= {fixture["recipe"] for fixture in FIXTURES}
    rows = run_object_fixtures(ids)
    assert all(row["status"] == "pass" for row in rows)
    for oid in ids:
        kinds = {row["kind"] for row in rows if row["recipe"] == oid}
        assert {"c08_missing", "c08_late", "c08_identity"} <= kinds


def test_m09_owned_recipes_preserve_holes_and_no_profit_reconstruction():
    from trading_research.research.method_pack.objects import RECIPES

    grade = RECIPES["O149"]({
        "score": "0.8", "threshold": "0.7", "features_known_at": m09._t(9, 59),
        "order_at": m09._t(10, 1), "known_at": m09._t(8, 0), "use_at": m09._t(10, 1),
    })
    assert grade.value["selection"] is True and grade.value["automatic_grade"] is None
    assert grade.state == "hole" and grade.coverage_ok is None
    assert "HOLE:O149:causal_correction" in grade.hole_ids

    fill = RECIPES["O151"]({
        "limit": 100, "side": "buy", "active_at": m09._t(10, 0),
        "trades": [{"t": m09._t(10, 2), "price": 100}],
        "known_at": m09._t(10, 2), "use_at": m09._t(10, 2),
    })
    assert fill.value["modeled_fill_at"] == m09._t(10, 2)
    assert fill.value["actual_unknown"] is True and fill.value["queue_verified"] is False
    assert fill.state == "hole"

    scenario = RECIPES["O156"]({
        "currency_per_r": 80, "rounded_pct": "0.92",
        "known_at": m09._t(16, 0), "use_at": m09._t(16, 1),
    })
    assert scenario.value["reported_pass_rate"] == Decimal("0.92")
    assert scenario.value["reconstruct_from_rounded"] is False
    assert scenario.state == "hole"


def test_m09_semantic_audit():
    assert m09.semantic_audit() == {
        "fixture_count": 10,
        "all_pass": True,
        "touch_cases": 6,
        "selected_order_cases": 4,
    }
