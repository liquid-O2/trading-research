from decimal import Decimal

from trading_research.research.method_pack.catalog import BRANCHES, objects_for
from trading_research.research.method_pack.method_slices import m11


def _rows():
    return {row["id"]: row for row in m11.method_fixtures()}


def test_m11_inventory_and_separate_process_macro_units():
    assert len(objects_for("STOIC-DATA")) == 14
    assert BRANCHES["STOIC-DATA"] == ["process_review", "macro_application"]
    rows = _rows()
    assert len(rows) == 12
    assert all(row["status"] == "pass" for row in rows.values())
    assert rows["M11-F1"]["predicate"] == "process"
    assert rows["M11-F1-macro"]["predicate"] == "macro_application"
    assert rows["M11-F1"]["actual_value"]["verdict"] == "pass"
    assert rows["M11-F1-macro"]["actual_value"]["verdict"] == "pass"


def test_m11_f1_has_exact_frozen_100_id_january_process():
    row = _rows()["M11-F1"]
    payload = row["inputs"]["evidence"][0]["payload"]
    assert payload["process_version"] == "stoic-process-v1"
    assert payload["inclusion_frozen_at"] == m11._at(m11.JAN1)
    assert len(payload["eligible_ids"]) == len(payload["retained_ids"]) == 100
    assert payload["eligible_ids"] == payload["retained_ids"]
    assert len(payload["sample_records"]) == 100
    assert {record["schema_version"] for record in payload["sample_records"]} == {"stoic-process-v1"}
    assert all(record["feature_known_at"] <= record["decision_at"] < record["outcome_at"]
               for record in payload["sample_records"])
    assert payload["comparison_groups"] == {"winner": 80, "loser": 20}
    assert payload["comparison_at"] == m11._at(m11.FEB1)
    assert payload["revision_at"] == m11._at(m11.FEB2)
    assert payload["revision_input_ids"] == payload["eligible_ids"]
    assert payload["trading_sequence_created"] is False
    assert payload["pnl_computed"] is False
    assert payload["model_trained"] is False


def test_m11_negative_process_controls_use_actual_ids_and_dates():
    rows = _rows()
    dropped = rows["M11-F2-drop-losers"]["actual_value"]
    assert dropped["sequence_ok"] is True and dropped["verdict"] == "fail"
    assert any("all 100 eligible" in hole["reason"] for hole in dropped["holes"])
    late = rows["M11-F2-late-inclusion"]["actual_value"]
    assert late["sequence_ok"] is True and late["verdict"] == "fail"
    assert any("after the sample" in hole["reason"] for hole in late["holes"])


def test_m11_macro_rejects_march_vintage_and_zscore_substitution():
    rows = _rows()
    march = rows["M11-F2-march-vintage"]["actual_value"]
    assert march["sequence_ok"] is True and march["verdict"] == "fail"
    assert any("March revision" in hole["reason"] for hole in march["holes"])
    zscore = rows["M11-F2-zscore"]["actual_value"]
    assert zscore["sequence_ok"] is True and zscore["verdict"] == "fail"
    assert any("replaced by z-score" in hole["reason"] for hole in zscore["holes"])
    positive = rows["M11-F1-macro"]["inputs"]["evidence"][0]["payload"]
    assert positive["custom_metric_kind"] == "c_score"
    assert positive["c_score"] != positive["z_score"]
    assert positive["automatic_current_verdict"] is None


def test_m11_macro_holes_do_not_invalidate_complete_process_unit():
    rows = _rows()
    for fid in ("M11-F3-vintage", "M11-F3-history", "M11-F3-rules"):
        actual = rows[fid]["actual_value"]
        assert actual["verdict"] == "unknown"
        assert actual["hole_ids"]
        payload = rows[fid]["inputs"]["evidence"][0]["payload"]
        assert payload["process_spec_frozen"] is True
        assert payload["all_eligible_observations_retained"] is True


def test_m11_c08_late_missing_and_identity_mutations():
    rows = _rows()
    late = rows["M11-F1:late"]["actual_value"]
    assert late["verdict"] == "fail" and late["detected_causal_violations"] == 2
    assert rows["M11-F1:missing"]["actual_value"]["verdict"] == "unknown"
    identity = rows["M11-F1:identity"]["actual_value"]
    assert identity["verdict"] == "fail"
    assert any(hole["kind"] == "identity" for hole in identity["holes"])


def test_all_m11_objects_have_passing_numeric_and_c08_fixtures():
    from trading_research.research.method_pack.objects import FIXTURES, RECIPES, run_object_fixtures

    ids = objects_for("STOIC-DATA")
    assert set(ids) <= set(RECIPES)
    assert set(ids) <= {fixture["recipe"] for fixture in FIXTURES}
    rows = run_object_fixtures(ids)
    assert all(row["status"] == "pass" for row in rows)
    for oid in ids:
        kinds = {row["kind"] for row in rows if row["recipe"] == oid}
        assert {"c08_missing", "c08_late", "c08_identity"} <= kinds


def test_m11_owned_primitives_keep_custom_engines_as_holes():
    from trading_research.research.method_pack.objects import RECIPES

    indicators = RECIPES["O157"]({
        "required_n": 4,
        "available": [{"id": "credit", "at": m11._at(m11.JAN1), "value": "1.5"},
                      {"id": "housing", "at": m11._at(m11.JAN1), "value": "3"},
                      {"id": "valuation", "at": m11._at(m11.JAN1), "value": "2"}],
        "as_of": m11._at(m11.JAN2), "known_at": m11._at(m11.JAN1),
        "use_at": m11._at(m11.JAN2),
    })
    assert indicators.value["available_series_count"] == 3
    assert indicators.value["required_series_present"] is None
    assert indicators.value["automatic_verdict"] is None
    cycle = RECIPES["O158"]({"source_cycle_label": "contraction", "indicator_count": 3,
                              "known_at": m11._at(m11.JAN1), "use_at": m11._at(m11.JAN2)})
    assert cycle.value["source_cycle_label"] == "contraction"
    assert cycle.value["majority_vote"] is False and cycle.value["automatic_cycle"] is None
    assert cycle.state == "hole"
    custom = RECIPES["O159"]({"c_score": "2.4", "z_score": "1.2",
                               "known_at": m11._at(m11.JAN1), "use_at": m11._at(m11.JAN2)})
    assert custom.value["source_c_score"] == Decimal("2.4")
    assert custom.value["distinct"] is True and custom.value["z_is_c"] is False
    assert custom.value["automatic_c_score"] is None and custom.state == "hole"
    substituted = RECIPES["O159"]({"c_score": "1.2", "z_score": "1.2", "metric_kind": "z_score",
                                    "known_at": m11._at(m11.JAN1), "use_at": m11._at(m11.JAN2)})
    assert substituted.state == "invalid" and substituted.base_ok is False
    comparison = RECIPES["O160"]({"baseline": [1, 3], "x": 4, "convention": "population",
                                   "known_at": m11._at(m11.JAN1), "use_at": m11._at(m11.JAN2)})
    assert comparison.value["baseline_mean"] == 2
    assert comparison.value["baseline_sd"] == 1
    assert comparison.value["standardized"] == 2
    empty = RECIPES["O160"]({"baseline": [], "x": 4, "convention": "population",
                              "known_at": m11._at(m11.JAN1), "use_at": m11._at(m11.JAN2)})
    assert empty.state == "hole" and empty.value['standardized_deviation'] is None
    assert 'HOLE:O160:baseline_values' in empty.hole_ids
    strength = RECIPES["O161"]({"regression_slope": "0.5",
                                 "known_at": m11._at(m11.JAN1), "use_at": m11._at(m11.JAN2)})
    assert strength.state == "hole" and strength.value["automatic_strength"] is None


def test_m11_semantic_audit():
    assert m11.semantic_audit() == {
        "fixture_count": 12,
        "all_pass": True,
        "process_cases": 6,
        "macro_cases": 6,
    }
