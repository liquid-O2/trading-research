from trading_research.research.method_pack.catalog import BRANCHES, objects_for
from trading_research.research.method_pack.method_slices import m05


def _rows():
    return {row["id"]: row for row in m05.method_fixtures()}


def test_m05_inventory_and_printed_acceptance_cases():
    assert len(objects_for("SIRES")) == 117
    assert len(BRANCHES["SIRES"]) == 12
    rows = _rows()
    assert len(rows) == 35
    assert all(row["status"] == "pass" for row in rows.values())
    assert rows["M05-F1"]["actual_value"]["verdict"] == "pass"
    for fid in ("M05-F2-stale-confirm", "M05-F2-ofm-omit", "M05-F2-ofm-early",
                "M05-F2-absorption", "M05-F2-stop-r"):
        assert rows[fid]["actual_value"]["verdict"] == "fail"
    assert rows["M05-F2-fade-no-own-reward"]["actual_value"]["verdict"] == "pass"
    stale = rows["M05-F2-stale-confirm"]
    stale_assertions = {item["field"]: item for item in stale["inputs"]["assertions"]}
    assert stale_assertions["fresh_same_side_defense"]["value"] is True
    assert stale_assertions["fresh_same_side_defense"]["evidence_ids"] == \
        stale_assertions["prior_band_control"]["evidence_ids"]
    assert any("reuses the prior-defense evidence" in hole["reason"]
               for hole in stale["actual_value"]["holes"])


def test_all_m05_objects_have_passing_numeric_and_c08_fixtures():
    from trading_research.research.method_pack.objects import FIXTURES, RECIPES, run_object_fixtures

    object_ids = objects_for("SIRES")
    fixture_recipes = {fixture["recipe"] for fixture in FIXTURES}
    assert set(object_ids) <= set(RECIPES)
    assert set(object_ids) <= fixture_recipes
    rows = run_object_fixtures(object_ids)
    assert len(rows) >= len(object_ids) * 4
    assert all(row["status"] == "pass" for row in rows)


def test_m05_f1_keeps_literal_geometry_and_actual_stage_times():
    row = _rows()["M05-F1"]
    document = row["inputs"]
    payload = document["evidence"][0]["payload"]
    assert payload["band"] == ["109", "110"]
    assert payload["stop_px"] == "111"
    assert payload["objective_px"] == "103"
    candidate = document["candidates"][0]
    assert candidate["branch"] == "defended_band_continuation"
    assert candidate["side"] == "short"
    assert candidate["decision_at"] == m05._t(9, 48)
    assertions = {item["field"]: item for item in document["assertions"]}
    assert assertions["prior_band_control"]["known_at"] == m05._t(9, 30)
    assert assertions["same_band_retest"]["known_at"] == m05._t(9, 45)
    assert assertions["fresh_same_side_defense"]["known_at"] == m05._t(9, 47)


def test_m05_f3_and_c08_mutations_preserve_false_unknown_and_identity():
    rows = _rows()
    for fid in ("M05-F3-refresh", "M05-F3-cvd", "M05-F3-depth",
                "M05-F3-gamma", "M05-F3-kg1", "M05-F3-thesis-death",
                "M05-F1:missing"):
        assert rows[fid]["actual_value"]["verdict"] == "unknown"
        assert rows[fid]["actual_value"]["hole_ids"]
    late = rows["M05-F1:late"]["actual_value"]
    assert late["verdict"] == "fail"
    assert late["detected_causal_violations"] == 2
    identity = rows["M05-F1:identity"]["actual_value"]
    assert identity["verdict"] == "fail"
    assert any(hole["kind"] == "identity" for hole in identity["holes"])


def test_m05_all_confirmed_execution_branches_are_independently_complete():
    rows = _rows()
    expected = {
        "M05-F1": "defended_band_continuation",
        "M05-F1-dom": "dom_rejection",
        "M05-F1-ofm": "ofm_aggressive",
        "M05-F1-ofm-passive": "ofm_passive",
        "M05-F1-absorption": "absorption_reward_retest",
        "M05-F1-footprint": "footprint_confirmed_reaction",
        "M05-F1-vwap": "vwap_deviation_fade",
        "M05-F1-clean-squeeze": "clean_squeeze",
        "M05-F1-balance-fade": "balance_failure_fade",
        "M05-F1-stop": "stop_four_stage",
        "M05-F1-microbalance": "microbalance_break",
        "M05-F1-kg1": "kg1_retest",
    }
    for fid, branch in expected.items():
        actual = rows[fid]["actual_value"]
        assert actual["branch"] == branch
        assert actual["verdict"] == "pass"


def test_m05_incomplete_cases_and_secondary_units_are_separate():
    rows = _rows()
    cases = [row for row in rows.values() if row["kind"] == "case_description"]
    assert {row["actual_value"]["branch"] for row in cases} == {
        "pre_file_early", "third_retest_case", "late_resistance_fade_case",
        "ofm_early_refill_case",
    }
    assert all(row["predicate"] == "case_description" for row in cases)
    assert all(row["actual_value"]["verdict"] == "pass" for row in cases)

    management = rows["M05-management-pass"]["actual_value"]
    reentry = rows["M05-reentry-pass"]["actual_value"]
    assert management["predicate"] == "management" and management["verdict"] == "pass"
    assert reentry["predicate"] == "reentry" and reentry["verdict"] == "pass"
    assert any(object_id.endswith(":parent:o:decision_at") for object_id in management["used_object_ids"])
    assert any(object_id.endswith(":parent:o:decision_at") for object_id in reentry["used_object_ids"])
    assert reentry["operands"]["prior_exit_at"]["value"] < reentry["operands"]["touch_at"]["value"]
    assert reentry["operands"]["prior_exit_at"]["value"] < reentry["operands"]["retest_at"]["value"]

    reused = rows["M05-reentry-reused"]["actual_value"]
    assert reused["verdict"] == "fail"
    assert any("before the actual prior exit" in hole["reason"] for hole in reused["holes"])


def test_m05_semantic_audit_and_stop_boundaries():
    audit = m05.semantic_audit()
    assert audit == {
        "fixture_count": 35,
        "all_pass": True,
        "predicates": ["case_description", "management", "reentry", "sequence"],
        "case_descriptions": 4,
        "management_cases": 2,
        "reentry_cases": 2,
    }
    rows = _rows()
    stop_ok = rows["M05-F1-stop"]["actual_value"]
    assert stop_ok["operands"]["reward_ticks"]["value"] == "3"
    assert stop_ok["operands"]["entry_distance_ticks"]["value"] == "1"
    assert rows["M05-F2-stop-r"]["actual_value"]["verdict"] == "fail"


def test_m05_object_holes_do_not_become_favorable_defaults():
    from trading_research.research.method_pack.objects import RECIPES

    cvd = RECIPES["O105"]({"trades": [{"side": "B", "size": 2}], "known_at": 10})
    assert cvd.state == "hole" and cvd.coverage_ok is None
    assert "HOLE:O105:reference" in cvd.hole_ids

    depth = RECIPES["O121"]({"band": 110, "arrival_at": 1, "rejection_at": 2,
                              "decision_at": 3, "known_at": 0, "use_at": 3})
    assert depth.state == "hole" and depth.value["evidence"] is None

    stop = RECIPES["O123"]({"origin": 100, "confirm_px": "100.75", "entry": 101,
                             "q": "0.25", "known_at": 3, "use_at": 4})
    assert stop.state == "hole" and stop.value["daily_stop_ok"] is None
    at_limit = RECIPES["O123"]({"origin": 100, "confirm_px": "100.75", "entry": 101,
                                 "q": "0.25", "daily_r": -4, "known_at": 3, "use_at": 4})
    assert at_limit.value["daily_stop_ok"] is False

    gamma = RECIPES["O129"]({"lo": 100, "hi": 110, "target": 103,
                              "known_at": 3, "use_at": 4})
    assert gamma.state == "hole" and gamma.value["long_gamma"] is None

    thesis = RECIPES["O138"]({"known_at": 3, "use_at": 4})
    assert thesis.value["alive"] is None and thesis.coverage_ok is None

    reentry = RECIPES["O144"]({"fresh_confirm_at": 3, "entry_at": 4,
                                "known_at": 4, "use_at": 4})
    assert reentry.state == "hole" and reentry.value["fresh"] is None
