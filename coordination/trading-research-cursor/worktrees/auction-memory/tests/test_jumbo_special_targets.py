"""Literal and schema checks for the standalone special-target adapter.

This test module is written alongside the adapter and is intentionally not
executed in the implementation tranche.  It uses one synthetic Monday and
the exact source field names; no market data or generic path target is used as
a special mechanism substitute.
"""
import unittest
from datetime import date

import numpy as np

from trading_research.research.jumbo_special_targets import (
    DAILY_CLOCKS,
    INDEPENDENT_CASE_IDS,
    MAGIC_CLOCKS,
    MECHANISM_BY_CLOCK,
    OPEN_TO_OPEN_CLOCKS,
    OVERNIGHT_CLOCKS,
    SPECIAL_CLOCK_IDS,
    SpecialTargetInputError,
    compact_special_payload,
    prepare_special_targets,
)


def formation(width=20, observed=60):
    return {"expected_minutes": 60, "observed_minutes": observed, "width_ticks": width,
            "zero_width": width == 0}


def contact(status="complete", reach=False, definite=False, origin=100, maturity=200):
    return {"status": status, "origin_ns": origin, "endpoint_ns": 300,
            "maturity_at_ns": maturity, "compatible_reach": reach,
            "definite_print": definite}


def magic_payload(*, ambiguous=False, nominal_precedes=False):
    nominal = contact(reach=True, definite=False)
    nominal.update({"state": "competing_order_ambiguous" if ambiguous else "midpoint_before_invalidation",
                    "possible_terminal_states": ["midpoint_before_invalidation", "invalidation_before_midpoint"]
                    if ambiguous else ["midpoint_before_invalidation"],
                    "first_side": "ambiguous" if ambiguous else "upper",
                    "source_branch_priority_comparator": {"state": "invalidation_before_midpoint"}})
    delayed = contact(reach=True, definite=True, origin=250, maturity=300)
    delayed.update({"state": "midpoint_before_invalidation", "possible_terminal_states": ["midpoint_before_invalidation"],
                    "first_side": "upper", "source_branch_priority_comparator": {"state": "midpoint_before_invalidation"}})
    return {"mechanism": MECHANISM_BY_CLOCK["magic_00"], "version": "test-v1",
            "formation": formation(), "candidate_available": True,
            "inputs_known_at_ns": 200, "context_known_at_ns": 50,
            "nominal_origin_precedes_input_known_at": nominal_precedes,
            "nominal": nominal, "availability_delayed": delayed}


def payload_for(clock):
    mechanism = MECHANISM_BY_CLOCK[clock]
    base = {"mechanism": mechanism, "version": "test-v1", "formation": formation(),
            "candidate_available": True, "inputs_known_at_ns": 200, "context_known_at_ns": 50}
    if clock in MAGIC_CLOCKS:
        payload = magic_payload()
        payload["mechanism"] = mechanism
        return payload
    if clock.startswith("PIN073_"):
        base.update({"target": {"numerator": 110, "denominator": 1},
                     "conditioning": {"status": "complete", "stratum": "both", "high_taken": True,
                                       "low_taken": True, "known_at_ns": 200},
                     "nominal": contact(reach=True, definite=True),
                     "availability_delayed": contact(reach=True, definite=False, origin=250, maturity=300)})
        return base
    if clock in OPEN_TO_OPEN_CLOCKS:
        base.update({"target": {"numerator": 110, "denominator": 1}, "zero_displacement": True,
                     "displacement_sign": 0, "target_direction_from_forecast": "equal",
                     "source_PIN076_stratum": "below_reference",
                     "nominal": contact(reach=True, definite=True),
                     "availability_delayed": contact(reach=True, definite=True, origin=250, maturity=300)})
        return base
    if clock in DAILY_CLOCKS:
        levels = {name: contact(reach=name in {"high", "low"}, definite=name == "high")
                  for name in ("high", "low", "midpoint", "fib1_actual_30pct", "fib2_actual_70pct")}
        delayed = {name: contact(reach=name == "high", definite=False, origin=250, maturity=300)
                    for name in levels}
        base.update({"date_key": "2024-01-01", "weekday": 0,
                     "levels": {name: {"numerator": 1, "denominator": 1} for name in levels},
                     "nominal": levels, "availability_delayed": delayed})
        return base
    if clock in OVERNIGHT_CLOCKS:
        base.update({"status": "candidate_available", "midpoint": {"numerator": 221, "denominator": 2},
                     "zero_width": False, "variant": clock})
        return base
    raise AssertionError(clock)


def synthetic_population():
    rows = []
    for clock in SPECIAL_CLOCK_IDS:
        rows.append({"date": "2024-01-01", "year": 2024, "root": "ROOT-A", "clock": clock,
                     "formation_id": f"formation-{clock}", "payload": payload_for(clock)})
    fields = {
        "date": np.full(len(rows), date(2024, 1, 1).toordinal(), dtype=np.int64),
        "root": np.zeros(len(rows), dtype=np.int16),
        "clock": np.asarray([SPECIAL_CLOCK_IDS.index(row["clock"]) for row in rows], dtype=np.int16),
        "horizon": np.zeros(len(rows), dtype=np.int16),
        "origin_ns": np.full(len(rows), 100, dtype=np.int64),
        "maturity_at_ns": np.full(len(rows), 300, dtype=np.int64),
    }
    path_matrix = {"features": np.arange(len(rows) * 2, dtype=float).reshape(len(rows), 2),
                   "fields": fields,
                   "categories": {"root": ("ROOT-A",), "clock": SPECIAL_CLOCK_IDS,
                                  "horizon": ("after_180m",)},
                   "manifest": {"feature_columns": ("x_f0", "x_f1")}}
    shard = {"root": "ROOT-A", "year": 2024, "special_rows": rows}
    return shard, path_matrix


class JumboSpecialTargetTests(unittest.TestCase):
    def test_all_frozen_special_clocks_have_distinct_mechanism_specs(self):
        self.assertEqual(len(SPECIAL_CLOCK_IDS), 22)
        self.assertEqual(INDEPENDENT_CASE_IDS, tuple(f"SM{at:02d}" for at in range(1, 27)))
        self.assertEqual(set(MECHANISM_BY_CLOCK), set(SPECIAL_CLOCK_IDS))
        self.assertEqual(len(set(MECHANISM_BY_CLOCK.values())), 5)

    def test_magic_union_ambiguity_and_nominal_causal_exclusion(self):
        payload = magic_payload(ambiguous=True, nominal_precedes=True)
        row = compact_special_payload("magic_00", payload)
        self.assertEqual(row["nominal_state"], "competing_order_ambiguous")
        self.assertEqual(set(row["nominal_allowed_states"]), {
            "midpoint_before_invalidation", "invalidation_before_midpoint", "competing_order_ambiguous"})
        self.assertFalse(row["nominal_eligible"])
        self.assertIn("nominal_origin_precedes_input_known_at", row["causal_exclusion_reasons"])
        self.assertEqual(row["availability_delayed_raw_source_state"], "midpoint_before_invalidation")

    def test_three_stage_delayed_eq_intersection_keeps_all_four_strata(self):
        row = compact_special_payload("PIN073_1", payload_for("PIN073_1"))
        self.assertEqual(row["conditioning_stratum"], "both")
        self.assertEqual(row["nominal_eq_intersection"], "definite_print")
        self.assertEqual(row["availability_delayed_eq_intersection"], "compatible_reach")
        self.assertEqual(row["availability_delayed_stratum_eq_intersection"], "both|compatible_reach")
        self.assertEqual(len({"neither", "high_only", "low_only", "both"}), 4)

    def test_open_to_open_delayed_direction_and_zero_atom_are_separate(self):
        row = compact_special_payload("PIN076_00_08", payload_for("PIN076_00_08"))
        self.assertTrue(row["zero_displacement"])
        self.assertEqual(row["displacement_sign"], 0)
        self.assertEqual(row["target_direction_from_forecast"], "equal")
        self.assertEqual(row["availability_delayed_eq_intersection"], "definite_print")

    def test_daily_180m_upper_lower_both_intersections(self):
        row = compact_special_payload("PIN078_daily_not_combined", payload_for("PIN078_daily_not_combined"))
        self.assertEqual(row["horizon"], "after_180m")
        self.assertEqual(row["planned_minutes"], 180)
        self.assertTrue(row["nominal_upper_intersection_180m"])
        self.assertTrue(row["nominal_lower_intersection_180m"])
        self.assertTrue(row["nominal_both_intersection_180m"])
        self.assertFalse(row["availability_delayed_both_intersection_180m"])

    def test_overnight_midpoint_is_exact_rational_and_not_floor_pivot(self):
        row = compact_special_payload("ONS03", payload_for("ONS03"))
        self.assertEqual(row["horizon"], "formation")
        self.assertEqual(row["midpoint_numerator"], 221)
        self.assertEqual(row["midpoint_denominator"], 2)
        self.assertTrue(row["target_metadata"]["generic_range_path_is_not_source_mechanism"])

    def test_prepared_population_joins_exact_after_180m_and_retains_source_rows(self):
        shard, path_matrix = synthetic_population()
        prepared = prepare_special_targets(None, [shard], plan={"expected_special_clock_ids": SPECIAL_CLOCK_IDS},
                                           path_matrix=path_matrix)
        compactrows, features, targetspecs = prepared
        self.assertEqual(len(compactrows), 22)
        self.assertEqual(features.shape, (22, 5))
        self.assertEqual(compactrows[0]["feature_join_horizon"], "after_180m")
        self.assertEqual(compactrows[0]["source_row_index"], 0)
        self.assertIn("nominal_target_known_at_ns", compactrows[0])
        self.assertIn("availability_delayed_label_known_at_ns", compactrows[0])
        self.assertEqual(compactrows[0]["horizon"], "formation")
        self.assertIn("magic_00.nominal.raw_source_state", {spec.target_id for spec in targetspecs})
        self.assertIn("PIN078_daily_not_combined.nominal.both_daily_rate", {spec.target_id for spec in targetspecs})

    def test_model_specs_exclude_censoring_but_retain_source_states(self):
        shard, path_matrix = synthetic_population()
        prepared = prepare_special_targets(None, [shard], plan={"expected_special_clock_ids": SPECIAL_CLOCK_IDS},
                                           path_matrix=path_matrix)
        specs = {spec.target_id: spec for spec in prepared.targetspecs}
        stratum = specs["PIN073_1.nominal.stratum_eq_intersection"]
        self.assertNotIn("censored", stratum.classes)
        self.assertNotIn("not_applicable", stratum.classes)
        self.assertIn("censored", stratum.metadata["retained_observation_states"])
        feature = specs["PIN073_1.conditioning.stratum"]
        self.assertFalse(feature.metadata["model_head"])
        daily = specs["PIN078_daily_not_combined.nominal.both_daily_rate"]
        self.assertEqual(daily.metadata["aggregation"], "unique_date_rate")

    def test_missing_exact_feature_identity_is_not_replaced_by_nearest_prefix(self):
        shard, path_matrix = synthetic_population()
        path_matrix["categories"]["horizon"] = ("after_60m",)
        prepared = prepare_special_targets(None, [shard], plan={"expected_special_clock_ids": SPECIAL_CLOCK_IDS},
                                           path_matrix=path_matrix)
        self.assertTrue(np.isnan(prepared.features[:, :2]).all())
        self.assertTrue(all(row["feature_join_status"] == "missing_exact_after_180m" for row in prepared.compactrows))
        self.assertTrue(all(not row["causal_eligible"] for row in prepared.compactrows))

    def test_missing_clock_and_wrong_mechanism_fail_closed(self):
        shard, path_matrix = synthetic_population()
        shard["special_rows"] = shard["special_rows"][:-1]
        with self.assertRaises(SpecialTargetInputError):
            prepare_special_targets(None, [shard], plan={"expected_special_clock_ids": SPECIAL_CLOCK_IDS},
                                   path_matrix=path_matrix)
        shard, path_matrix = synthetic_population()
        shard["special_rows"][0]["payload"] = payload_for("magic_00")
        with self.assertRaises(SpecialTargetInputError):
            prepare_special_targets(None, [shard], plan={"expected_special_clock_ids": SPECIAL_CLOCK_IDS},
                                   path_matrix=path_matrix)

    def test_unavailable_formation_has_null_metadata_and_nan_features_not_a_zero_range(self):
        shard, path_matrix = synthetic_population()
        row = next(r for r in shard["special_rows"] if r['clock'] == 'magic_00')
        row['payload'] = {'mechanism': MECHANISM_BY_CLOCK['magic_00'], 'formation': {},
                          'candidate_available': False, 'status': 'formation_unavailable'}
        prepared = prepare_special_targets(None, [shard], plan={'expected_special_clock_ids': SPECIAL_CLOCK_IDS},
                                           path_matrix=path_matrix)
        at = next(i for i,r in enumerate(prepared.compactrows) if r['clock'] == 'magic_00')
        compact = prepared.compactrows[at]
        self.assertIsNone(compact['formation_observed_fraction'])
        self.assertIsNone(compact['formation_width_ticks'])
        self.assertIsNone(compact['formation_zero_width'])
        self.assertTrue(np.isnan(prepared.features[at,-3:]).all())
        self.assertFalse(compact['causal_eligible'])
        self.assertEqual(len(prepared.manifest['row_sha256']),64)

    def test_feature_publication_is_independent_of_future_label_maturity(self):
        shard, path_matrix = synthetic_population()
        path_matrix['fields']['anchor_observation_known_at_ns'] = np.full(len(SPECIAL_CLOCK_IDS),90)
        first = prepare_special_targets(None,[shard],plan={'expected_special_clock_ids': SPECIAL_CLOCK_IDS},
                                         path_matrix=path_matrix)
        path_matrix['fields']['maturity_at_ns'][:] = 900
        second = prepare_special_targets(None,[shard],plan={'expected_special_clock_ids': SPECIAL_CLOCK_IDS},
                                          path_matrix=path_matrix)
        self.assertTrue(all(r['feature_available_at_ns']==100 for r in first.compactrows))
        self.assertEqual([r['feature_available_at_ns'] for r in first.compactrows],
                         [r['feature_available_at_ns'] for r in second.compactrows])
        np.testing.assert_equal(first.features,second.features)


if __name__ == "__main__":
    unittest.main()
