"""Literal numerical checks for observed-date statistics and uncertainty."""

import json
import unittest

from trading_research.errors import ContractError
from trading_research.research.date_statistics import (
    DEFAULT_BLOCK_LENGTH,
    DEFAULT_REPLICATES,
    DEFAULT_SEED,
    observed_date_statistics,
    paired_score_gain_interval,
)
from trading_research.research.scoring import IntervalSpec, block_interval, quantile


def dates(count):
    return tuple(f"d{index}" for index in range(count))


class DateStatisticsTests(unittest.TestCase):
    def test_type7_quantile_and_json_safe_summary(self):
        self.assertEqual(quantile((0.0, 10.0, 20.0, 30.0), .25), 7.5)
        intended = dates(5)
        summary = observed_date_statistics(
            {"score": {"d0": 2.0, "d1": None, "d2": 4.0, "d3": 0.0, "d4": 6.0}},
            intended,
            minimum_independent_dates=1,
            minimum_events=1,
        )
        metric = summary["metrics"]["score"]
        self.assertEqual(metric["estimate"], 3.0)
        self.assertEqual((metric["actual_valid_date_count"], metric["actual_valid_event_count"]), (4, 4))
        self.assertEqual(metric["missing_date_count"], 1)
        self.assertEqual(json.loads(json.dumps(summary))["schema"], "observed-date-statistics-v1")

    def test_missing_cells_are_not_zero_and_ratio_uses_metric_denominators(self):
        intended = dates(5)
        summary = observed_date_statistics(
            {
                "numerator": {"d0": 2.0, "d1": None, "d2": 4.0, "d3": 0.0, "d4": 6.0},
                "denominator": {"d0": 1.0, "d1": 1.0, "d2": 2.0, "d3": 1.0, "d4": 2.0},
            },
            intended,
            ratios={"n_over_d": ("numerator", "denominator")},
            minimum_independent_dates=1,
            minimum_events=1,
        )
        self.assertEqual(summary["metrics"]["numerator"]["estimate"], 3.0)
        self.assertEqual(summary["metrics"]["denominator"]["estimate"], 1.4)
        self.assertAlmostEqual(summary["ratios"]["n_over_d"]["estimate"], 3.0 / 1.4)
        self.assertEqual(summary["metrics"]["numerator"]["actual_valid_date_count"], 4)

    def test_shared_deterministic_weights_have_no_circular_end_wrap(self):
        intended = dates(12)
        metrics = {
            "a": {day: float(index) for index, day in enumerate(intended)},
            "b": {day: float(100 + index) for index, day in enumerate(intended)},
        }
        first = observed_date_statistics(metrics, intended, include_weights=True,
                                         minimum_independent_dates=1, minimum_events=1)
        second = observed_date_statistics(metrics, intended, include_weights=True,
                                          minimum_independent_dates=1, minimum_events=1)
        self.assertEqual(first, second)
        weights = first["bootstrap_weights"]
        self.assertEqual((weights["seed"], weights["block_length"], weights["replicates"]),
                         (DEFAULT_SEED, DEFAULT_BLOCK_LENGTH, DEFAULT_REPLICATES))
        self.assertFalse(weights["circular_end_wrap"])
        self.assertTrue(all(sum(row) == len(intended) for row in weights["weights"]))
        self.assertTrue(all(0 <= start <= len(intended) - DEFAULT_BLOCK_LENGTH
                            for starts in weights["block_starts"] for start in starts))
        self.assertEqual(first["metrics"]["a"]["bootstrap"]["replicate_estimates"],
                         second["metrics"]["a"]["bootstrap"]["replicate_estimates"])

    def test_all_valid_reference_interval_matches_scoring_block_interval(self):
        intended = dates(100)
        values = {day: float((index * 3) % 17) for index, day in enumerate(intended)}
        summary = observed_date_statistics({"x": values}, intended, validate_reference=True)
        metric = summary["metrics"]["x"]
        reference = block_interval(
            {day: (values[day],) for day in intended},
            IntervalSpec(.95, 1000, DEFAULT_SEED, DEFAULT_BLOCK_LENGTH, 2, "equal_date"),
            ordered_dates=intended,
        )
        self.assertTrue(metric["bootstrap"]["reference_parity_checked"])
        self.assertTrue(metric["bootstrap"]["reference_parity_matches"])
        self.assertEqual((metric["bootstrap"]["lower"], metric["bootstrap"]["upper"]),
                         (reference["lower"], reference["upper"]))

    def test_zero_denominator_replicates_are_null_and_counted(self):
        intended = dates(10)
        summary = observed_date_statistics(
            {
                "numerator": {day: 1.0 for day in intended},
                "denominator": {"d0": 0.0},
            },
            intended,
            ratios={"ratio": ("numerator", "denominator")},
            minimum_independent_dates=1,
            minimum_events=1,
        )
        ratio = summary["ratios"]["ratio"]
        self.assertIsNone(ratio["estimate"])
        self.assertEqual(ratio["bootstrap"]["invalid_denominator_replicates"], DEFAULT_REPLICATES)
        self.assertEqual(ratio["bootstrap"]["valid_replicates"], 0)
        self.assertTrue(all(value is None for value in ratio["bootstrap"]["replicate_estimates"]))

    def test_sparse_support_is_flagged_by_dates_and_events(self):
        intended = dates(10)
        summary = observed_date_statistics(
            {"x": {day: [1.0, 2.0] for day in intended}}, intended,
        )
        support = summary["metrics"]["x"]["support"]
        self.assertTrue(support["sparse"])
        self.assertEqual((support["independent_dates"], support["events"]), (10, 20))
        self.assertIn("fewer_than_minimum_independent_dates", support["reasons"])

    def test_date_clustered_paired_constant_gain_and_pair_missingness(self):
        intended = dates(10)
        baseline = {day: 10.0 for day in intended}
        challenger = {day: 8.0 for day in intended}
        result = paired_score_gain_interval(baseline, challenger, intended,
                                            minimum_independent_dates=1, minimum_events=1)
        self.assertEqual(result["kind"], "date_clustered_paired_score_gain")
        self.assertEqual(result["estimate"], 2.0)
        self.assertEqual((result["bootstrap"]["lower"], result["bootstrap"]["upper"]), (2.0, 2.0))
        self.assertEqual((result["actual_valid_date_count"], result["actual_valid_event_count"]), (10, 10))

        missing = paired_score_gain_interval(
            {"d0": 10.0, "d1": 10.0}, {"d0": 8.0}, dates(5),
            minimum_independent_dates=1, minimum_events=1,
        )
        self.assertEqual(missing["missing_pair_date_count"], 4)
        self.assertEqual(missing["estimate"], 2.0)

    def test_invalid_pair_event_cardinality_and_unregistered_inputs_fail_closed(self):
        with self.assertRaises(ContractError):
            paired_score_gain_interval({"d0": [1.0, 2.0]}, {"d0": [0.0]}, dates(5))
        with self.assertRaises(ContractError):
            observed_date_statistics({"x": {"outside": 1.0}}, dates(5))


if __name__ == "__main__":
    unittest.main()
