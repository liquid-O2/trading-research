"""Static contract tests for source-specific model views.

These tests deliberately use the retained special-payload fixture and the
prepared path identity.  They verify that censoring/unavailability stays out
of event classes while intended populations remain in each PreparedPaths
view.  The registered worker owns execution of this module.
"""
import unittest

import numpy as np

from trading_research.research.jumbo_special_models import prepare_special_model_views
from trading_research.research.jumbo_special_targets import (
    MECHANISM_BY_CLOCK,
    SPECIAL_CLOCK_IDS,
    prepare_special_targets,
)
from trading_research.research.jumbo_targets import Target
from tests.test_jumbo_special_targets import magic_payload, synthetic_population


class JumboSpecialModelViewTests(unittest.TestCase):
    def _views(self, *, ambiguous_magic=False):
        shard, path_matrix = synthetic_population()
        if ambiguous_magic:
            magic_row = next(row for row in shard["special_rows"] if row["clock"] == "magic_00")
            magic_row["payload"] = magic_payload(ambiguous=True)
            # This positive ambiguity case has known formation inputs at its
            # nominal origin. The separate exclusion cases retain late inputs.
            magic_row["payload"]["inputs_known_at_ns"] = 100
        prepared = prepare_special_targets(
            None, [shard], plan={"expected_special_clock_ids": SPECIAL_CLOCK_IDS},
            path_matrix=path_matrix,
        )
        return prepare_special_model_views(
            path_matrix, prepared, plan={"expected_special_clock_ids": SPECIAL_CLOCK_IDS},
        )

    def test_flat_and_nested_mechanism_branch_lookup_are_available(self):
        views = self._views()
        magic = MECHANISM_BY_CLOCK["magic_00"]
        self.assertIn(f"{magic}/nominal", views)
        self.assertIn("nominal", views[magic])
        self.assertIs(views[f"{magic}/nominal"], views[magic]["nominal"])

    def test_magic_ambiguity_is_compatible_set_not_event_class(self):
        views = self._views(ambiguous_magic=True)
        magic = MECHANISM_BY_CLOCK["magic_00"]
        _, targets = views[f"{magic}/nominal"]
        point = targets["magic_00.nominal.state"]
        possible = targets["magic_00.nominal.possible_states"]
        self.assertIsInstance(point, Target)
        self.assertFalse(point.eligible[0])
        self.assertNotIn("competing_order_ambiguous", point.metadata["classes"])
        self.assertNotIn("future_censored", possible.metadata["classes"])
        self.assertTrue(possible.eligible[0])
        self.assertEqual(possible.values.shape[1], len(possible.metadata["classes"]))

    def test_three_stage_strata_are_features_and_censoring_is_excluded(self):
        mechanism = MECHANISM_BY_CLOCK["PIN073_1"]
        views = self._views()
        view, targets = views[f"{mechanism}/availability_delayed"]
        self.assertEqual(view.features.shape[1], 13)
        self.assertEqual(view.features[0, 6], 1.0)  # source conditioning-known gate
        target = targets["PIN073_1.availability_delayed.eq_intersection"]
        self.assertNotIn("censored", target.metadata["classes"])
        self.assertIn("PIN073_1.availability_delayed.stratum_eq_intersection", targets)
        self.assertFalse(targets["PIN073_1.availability_delayed.stratum_eq_intersection"].metadata["model_head"])

    def test_daily_rate_heads_are_distinct_model_targets(self):
        mechanism = MECHANISM_BY_CLOCK["PIN078_daily_not_combined"]
        _, targets = self._views()[f"{mechanism}/nominal"]
        for side in ("upper", "lower", "both"):
            name = f"PIN078_daily_not_combined.nominal.{side}_daily_rate"
            self.assertIn(name, targets)
            self.assertEqual(targets[name].metadata["aggregation"], "unique_date_rate")
            self.assertEqual(targets[name].metadata["denominator"], "one formation date per source row")

    def test_prepared_targetspec_model_heads_close_exactly(self):
        shard, path_matrix = synthetic_population()
        prepared = prepare_special_targets(
            None, [shard], plan={"expected_special_clock_ids": SPECIAL_CLOCK_IDS},
            path_matrix=path_matrix,
        )
        views = prepare_special_model_views(
            path_matrix, prepared, plan={"expected_special_clock_ids": SPECIAL_CLOCK_IDS},
        )
        declared = {
            spec.target_id for spec in prepared.targetspecs
            if spec.metadata.get("model_head", True)
        }
        actual = {
            target_name
            for _, (_, targets) in views.items()
            for target_name, target in targets.items()
            if target.metadata.get("model_head", True)
        }
        self.assertEqual(actual, declared)

    def test_known_measurements_have_explicit_dispositions_and_are_not_fit_heads(self):
        views = self._views()
        overnight = MECHANISM_BY_CLOCK["ONS03"] + "/formation"
        open_domain = MECHANISM_BY_CLOCK["PIN076_00_08"] + "/availability_delayed"
        self.assertIn("ONS03.formation.midpoint", views.measurement_dispositions[overnight])
        self.assertIn("ONS03.formation.zero_width", views.measurement_dispositions[overnight])
        self.assertIn("PIN076_00_08.availability_delayed.target_direction",
                      views.measurement_dispositions[open_domain])
        self.assertTrue(views.measurement_dispositions[overnight]["ONS03.formation.midpoint"]["rows_by_year"])
        _, open_targets = views[open_domain]
        self.assertFalse(open_targets["PIN076_00_08.availability_delayed.target_direction"].metadata["model_head"])

    def test_open_delayed_branch_binds_forecast_open_cut_and_keeps_zero_atom(self):
        mechanism = MECHANISM_BY_CLOCK["PIN076_00_08"]
        view, targets = self._views()[f"{mechanism}/availability_delayed"]
        displacement = targets["PIN076_00_08.availability_delayed.displacement_sign"]
        self.assertTrue(displacement.metadata["forecast_open_availability_required"])
        self.assertFalse(displacement.metadata["model_head"])
        self.assertTrue(targets["PIN076_00_08.availability_delayed.zero_displacement"].metadata["zero_atom"])
        self.assertEqual(targets["PIN076_00_08.availability_delayed.target_direction"].metadata["classes"],
                         ["below", "above", "equal"])
        self.assertTrue(np.all(view.fields["special_cut_ns"] >= 0))

    def test_no_censoring_or_unavailability_is_encoded_as_a_market_event(self):
        views = self._views()
        for _, targets in views.values():
            for target in targets.values():
                classes = target.metadata.get("classes", ())
                self.assertNotIn("censored", classes)
                self.assertNotIn("future_censored", classes)
                self.assertNotIn("not_applicable", classes)


if __name__ == "__main__":
    unittest.main()
