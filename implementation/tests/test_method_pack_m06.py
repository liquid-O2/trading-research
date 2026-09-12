from trading_research.research.method_pack.catalog import BRANCHES, objects_for
from trading_research.research.method_pack.method_slices import m06


def _rows():
    return {row["id"]: row for row in m06.method_fixtures()}


def test_m06_inventory_and_all_four_route_positives():
    assert len(objects_for("SAINT-AMT")) == 36
    assert BRANCHES["SAINT-AMT"] == [
        "continuation_retest", "trapped_buyers_retest",
        "failed_auction_return", "poc_traversal",
    ]
    rows = _rows()
    assert len(rows) == 13
    assert all(row["status"] == "pass" for row in rows.values())
    positives = [rows[fid]["actual_value"] for fid in (
        "M06-F1", "M06-F1-continuation", "M06-F1-failed-auction", "M06-F1-poc")]
    assert {row["branch"] for row in positives} == set(BRANCHES["SAINT-AMT"])
    assert all(row["verdict"] == "pass" for row in positives)


def test_m06_f1_uses_distinct_prior_failures_and_fresh_current_control():
    row = _rows()["M06-F1"]
    doc = row["inputs"]
    payload = doc["evidence"][0]["payload"]
    failures = payload["prior_failures"]
    assert [(item["failure_id"], item["resolved_at"]) for item in failures] == [
        ("prior-AM", m06._t(7, 0)), ("prior-PM", m06._t(7, 30))]
    assert len({(item["failure_id"], item["resolved_at"]) for item in failures}) == 2
    actual = row["actual_value"]
    values = {field: binding["value"] for field, binding in actual["operands"].items()}
    assert values["prior_failures_known_at"] < values["breakout_at"]
    assert values["breakout_at"] < values["retest_at"] <= values["confirm_at"]
    assert values["confirm_at"] <= values["decision_at"]
    assert payload["breakout_band_id"] == payload["retest_band_id"] == "SAINT-HTF-100-110"
    assert payload["htf_control_side"] == payload["ltf_control_side"] == "short"


def test_m06_negative_controls_are_observed_relationship_failures():
    rows = _rows()
    duplicate = rows["M06-F2-duplicate-failure"]["actual_value"]
    assert duplicate["sequence_ok"] is True and duplicate["verdict"] == "fail"
    assert any("not distinct resolved episodes" in hole["reason"] for hole in duplicate["holes"])
    chop = rows["M06-F2-free-chop"]["actual_value"]
    assert chop["sequence_ok"] is True and chop["verdict"] == "fail"
    assert any("two-sided chop" in hole["reason"] for hole in chop["holes"])
    chased = rows["M06-F2-no-retest"]["actual_value"]
    assert chased["sequence_ok"] is True and chased["verdict"] == "fail"
    assert any("no observed current boundary retest" in hole["reason"] for hole in chased["holes"])


def test_m06_holes_and_c08_mutations_preserve_three_valued_logic():
    rows = _rows()
    for fid in ("M06-F3-current-control", "M06-F3-profile-selection",
                "M06-F3-hold-procedure", "M06-F1:missing"):
        assert rows[fid]["actual_value"]["verdict"] == "unknown"
        assert rows[fid]["actual_value"]["hole_ids"]
    assert rows["M06-F1:late"]["actual_value"]["verdict"] == "fail"
    assert rows["M06-F1:late"]["actual_value"]["detected_causal_violations"] == 2
    identity = rows["M06-F1:identity"]["actual_value"]
    assert identity["verdict"] == "fail"
    assert any(hole["kind"] == "identity" for hole in identity["holes"])


def test_m06_failed_auction_does_not_import_sires_older_poc_rule():
    row = _rows()["M06-F1-failed-auction"]
    assert row["actual_value"]["verdict"] == "pass"
    assert "older_poc" not in row["inputs"]["evidence"][0]["payload"]


def test_all_m06_objects_have_passing_numeric_and_c08_fixtures():
    from trading_research.research.method_pack.objects import FIXTURES, RECIPES, run_object_fixtures

    object_ids = objects_for("SAINT-AMT")
    fixture_recipes = {fixture["recipe"] for fixture in FIXTURES}
    assert set(object_ids) <= set(RECIPES)
    assert set(object_ids) <= fixture_recipes
    rows = run_object_fixtures(object_ids)
    assert all(row["status"] == "pass" for row in rows)
    for oid in object_ids:
        kinds = {row["kind"] for row in rows if row["recipe"] == oid}
        assert {"c08_missing", "c08_late", "c08_identity"} <= kinds


def test_m06_semantic_audit():
    assert m06.semantic_audit() == {
        "fixture_count": 13,
        "all_pass": True,
        "branches": ["continuation_retest", "failed_auction_return",
                     "poc_traversal", "trapped_buyers_retest"],
    }


def test_m06_owned_object_recipes_preserve_source_holes_and_ordering():
    from trading_research.research.method_pack.objects import RECIPES

    asia = RECIPES["O089"]({
        "entry": 110, "stop": 112, "target": 105, "asia_range": 8,
        "known_at": m06._t(8, 0), "use_at": m06._t(9, 53),
    })
    assert asia.value["stop_distance"] == 2
    assert asia.value["target_distance"] == 5
    assert asia.value["source_range_reference"] == 8
    assert asia.value["automatic_target"] is None
    assert asia.state == "hole" and "HOLE:O089:selector" in asia.hole_ids

    future = RECIPES["O089"]({
        "entry": 110, "stop": 112, "target": 105, "asia_range": 8,
        "range_known_at": m06._t(10, 0), "decision_at": m06._t(9, 53),
        "known_at": m06._t(8, 0), "use_at": m06._t(10, 0),
    })
    assert future.state == "invalid" and future.base_ok is False

    route = RECIPES["O094"]({
        "orig_lo": 100, "orig_hi": 110,
        "explore_at": m06._t(9, 40), "failure_at": m06._t(9, 45),
        "return_at": m06._t(9, 48), "reaccept_at": m06._t(9, 50),
        "control_at": m06._t(9, 52), "decision_at": m06._t(9, 53),
        "known_at": m06._t(9, 20), "use_at": m06._t(9, 53),
    })
    assert route.value["route_ok"] is True
    assert route.state == "hole"
    assert set(route.hole_ids) == {"HOLE:O094:original_balance_id", "HOLE:O094:tested_value_id"}
