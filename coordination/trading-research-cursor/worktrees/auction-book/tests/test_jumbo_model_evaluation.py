"""Independent array-level checks for the Jumbo evaluation draft.

This file is intentionally not executed in the implementation tranche.  It
uses literal small arrays and does not import any market reader, fold builder,
model fitter, or package implementation.
"""

from __future__ import annotations

import unittest

import numpy as np

from trading_research.research.jumbo_model_evaluation import (  # noqa: E402
    EvaluationInputError,
    binary_bound_metrics,
    categorical_metrics,
    grouped_date_evaluation,
    quantile_metrics,
)


class JumboEvaluationTests(unittest.TestCase):
    def test_sparse_bootstrap_matches_declared_reference(self):
        from trading_research.research.jumbo_model_evaluation import _moving_weights
        from trading_research.research.date_statistics import _moving_weights as reference
        for count in (5, 7, 9):
            actual = _moving_weights(count, seed=13, block_length=5, replicates=20)
            expected, _ = reference(np, count, seed=13, block_length=5, replicates=20)
            np.testing.assert_array_equal(actual, expected)

    def test_categorical_point_scores_and_simplex(self):
        probabilities = np.asarray([[.8, .2], [.25, .75], [0.0, 1.0], [0.0, 1.0]])
        result = categorical_metrics(probabilities, observed_class=np.asarray([0, 1, 1, 0]))
        np.testing.assert_allclose(result["per_row"]["log_loss"], -np.log([.8, .75, 1.0, 1e-15]))
        np.testing.assert_allclose(result["per_row"]["brier"], [.08, .125, 0.0, 2.0])
        self.assertEqual(result["summary"]["zero_probability_count"], 1)
        self.assertEqual(result["summary"]["log_floor_applied_count"], 1)
        self.assertEqual(result["simplex"]["rows_valid"], 4)

    def test_categorical_allowed_classes_keep_no_information_and_brier_bounds(self):
        probabilities = np.asarray([[.7, .2, .1], [.2, .3, .5], [.1, .4, .5]])
        allowed = np.asarray([[True, False, False], [True, True, False], [True, True, True]])
        result = categorical_metrics(probabilities, allowed_class_matrix=allowed)
        self.assertTrue(np.isfinite(result["per_row"]["brier"][0]))
        self.assertTrue(np.isnan(result["per_row"]["brier"][1]))
        self.assertTrue(np.isnan(result["per_row"]["interval_log_loss"][2]))
        self.assertEqual(result["summary"]["all_class_count"], 1)
        # Allowed classes in row two carry .2 + .3 probability.
        np.testing.assert_allclose(result["per_row"]["interval_probability"], [.7, .5, 1.0])

    def test_quantile_metrics_report_pinball_coverage_ties_and_final_crossings(self):
        targets = np.asarray([[0.0], [1.0], [2.0], [np.nan]])
        raw = np.asarray([
            [[1.0, 0.0, 2.0]],
            [[0.0, 1.0, 2.0]],
            [[0.0, 1.0, 3.0]],
            [[0.0, 1.0, 2.0]],
        ])
        emitted = np.asarray([
            [[0.0, 1.0, 2.0]],
            [[0.0, 1.0, 2.0]],
            [[0.0, 1.0, 3.0]],
            [[0.0, 1.0, 2.0]],
        ])
        result = quantile_metrics(targets, raw, (.1, .5, .9), final_predictions=emitted)
        self.assertEqual(result["crossings"]["raw_predictions"]["rows_with_crossing"], 1)
        self.assertEqual(result["crossings"]["final_predictions"]["rows_with_crossing"], 0)
        self.assertEqual(result["q_coverage"]["zero_atom_tie_count"][0, 0], 1)
        self.assertEqual(result["missingness"]["target_missing_cells"], 1)
        # Observed targets have final interval widths 2, 2 and 3; the missing
        # target does not contribute another width of 2 to this score.
        np.testing.assert_allclose(result["central_interval"]["width_mean"], [7.0/3.0])
        self.assertTrue(np.all(np.isfinite(result["per_row_mean_pinball"][:3])))
        self.assertTrue(np.isnan(result["per_row_mean_pinball"][3]))

    def test_binary_bounds_use_actual_endpoints_not_fractional_labels(self):
        result = binary_bound_metrics(
            np.asarray([.2, .8, .5, .0]),
            np.asarray([0.0, 0.0, 0.0, 0.0]),
            np.asarray([1.0, 1.0, 0.0, 0.0]),
        )
        self.assertFalse(result["summary"]["fractional_label_used"])
        self.assertEqual(result["summary"]["both_endpoint_count"], 2)
        np.testing.assert_allclose(
            result["per_row"]["log_loss_lower"][:2],
            np.minimum(-np.log([.8, .2]), -np.log([.2, .8])),
        )
        self.assertAlmostEqual(result["per_row"]["brier_lower"][2], .25)
        with self.assertRaises(EvaluationInputError):
            binary_bound_metrics(np.asarray([.5]), np.asarray([.2]), np.asarray([.8]))

    def test_grouped_dates_sort_once_preserve_missingness_pair_and_reliability(self):
        dates = np.asarray([0, 2, 1, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        groups = np.asarray([1] * 10 + [2] * 10)
        losses = np.asarray([1., 2., 3., 4., np.nan, 2., 2., 1., 3., 2.,
                             2., 1., 2., 3., 2., 2., 1., 2., 3., 2.])
        baseline = losses + 1.0
        candidate = losses
        probability = np.asarray([.1, .2, .3, .4, .5, .6, .7, .8, .9, 1.] * 2)
        observed = np.asarray([0, 0, 0, 1, 1, 1, 1, 1, 1, 1] * 2, dtype=float)
        result = grouped_date_evaluation(
            {"candidate_loss": losses}, dates, groups,
            {1: tuple(range(10)), 2: tuple(range(10))},
            paired_candidate=candidate, paired_baseline=baseline,
            probability=probability, observed_binary=observed,
            minimum_dates=1, minimum_events=1, replicates=200,
        )
        self.assertEqual(result["group_count"], 2)
        self.assertFalse(result["configuration"]["circular_end_wrap"])
        self.assertFalse(result["configuration"]["row_subsampling"])
        group_one = result["groups"]["1"]
        self.assertEqual(group_one["missing_intended_dates"], 0)
        self.assertEqual(group_one["metrics"]["candidate_loss"]["valid_dates"], 9)
        self.assertAlmostEqual(group_one["paired"]["estimate"], 1.0)
        self.assertEqual(group_one["paired"]["gain_definition"], "baseline_minus_candidate_loss")
        self.assertEqual(group_one["reliability"]["fractional_label_used"], False)
        self.assertEqual(len(group_one["reliability"]["bins"]), 10)

    def test_grouped_interval_reliability_reports_bounds(self):
        dates = np.arange(10)
        groups = np.ones(10, dtype=int)
        probability = np.linspace(.05, .95, 10)
        result = grouped_date_evaluation(
            {"loss": np.ones(10)}, dates, groups, {1: tuple(range(10))},
            probability=probability, lower=np.zeros(10), upper=np.ones(10),
            minimum_dates=1, minimum_events=1, replicates=200,
        )
        reliability = result["groups"]["1"]["reliability"]
        self.assertEqual(reliability["kind"], "interval_bounds")
        self.assertTrue(np.isnan(reliability["ece"]))
        self.assertLessEqual(reliability["ece_lower"], reliability["ece_upper"])
        self.assertFalse(reliability["fractional_label_used"])

    def test_grouped_classwise_calibration_cells_share_date_bootstrap(self):
        dates = np.arange(10)
        groups = np.ones(10, dtype=int)
        probabilities = np.column_stack((np.linspace(.05, .95, 10), np.linspace(.95, .05, 10)))
        observed = np.column_stack((np.asarray([0, 0, 0, 1, 1, 1, 1, 1, 1, 1], dtype=float),
                                    np.asarray([1, 1, 1, 0, 0, 0, 0, 0, 0, 0], dtype=float)))
        result = grouped_date_evaluation(
            {"loss": np.ones(10)}, dates, groups, {1: tuple(range(10))},
            probability_matrix=probabilities, observed_binary_matrix=observed,
            minimum_dates=1, minimum_events=1, replicates=200,
        )
        cells = result["groups"]["1"]["calibration_by_class"]["0"]["bins"]
        self.assertEqual(len(cells), 10)
        self.assertIn("predicted_mean", cells[0])
        self.assertIn("outcome_lower", cells[0])
        self.assertIn("outcome_upper", cells[0])
        self.assertIn("count", cells[0])
        self.assertTrue(cells[0]["date_bootstrap"]["shared_weights"])
        self.assertTrue(result["configuration"]["classwise_calibration"])

    def test_classwise_cells_report_equal_date_points_and_distinct_dates(self):
        dates = np.asarray([1, 1, 2], dtype=int)
        groups = np.ones(3, dtype=int)
        probabilities = np.asarray([[.21, .79], [.21, .79], [.29, .71]])
        observed = np.asarray([[0., 1.], [0., 1.], [1., 0.]])
        result = grouped_date_evaluation(
            {"loss": np.ones(3)}, dates, groups, {1: (1, 2)},
            probability_matrix=probabilities, observed_binary_matrix=observed,
            minimum_dates=1, minimum_events=1, replicates=200,
        )
        cell = result["groups"]["1"]["calibration_by_class"]["0"]["bins"][2]
        self.assertEqual(cell["count"], 3)
        self.assertEqual(cell["dates"], 2)
        self.assertAlmostEqual(cell["predicted_mean"], .25)
        self.assertAlmostEqual(cell["outcome_lower"], .5)
        self.assertAlmostEqual(cell["row_weighted_outcome_lower"], 1 / 3)

    def test_invalid_simplex_and_duplicate_intended_dates_fail_closed(self):
        with self.assertRaises(EvaluationInputError):
            categorical_metrics(np.asarray([[.6, .6]]), observed_class=np.asarray([0]))
        with self.assertRaises(EvaluationInputError):
            grouped_date_evaluation(
                {"loss": np.ones(2)}, np.asarray([0, 1]), np.asarray([1, 1]),
                {1: (0, 0)}, minimum_dates=1, minimum_events=1,
            )


if __name__ == "__main__":
    unittest.main()
