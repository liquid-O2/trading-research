"""Literal date-population and timing checks for the Jumbo report adapter."""

import json
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.jumbo_report import (
    BINARY,
    CONTINUOUS,
    formation_statistics,
    path_statistics,
    special_statistics,
)


def _dates(count=5):
    return tuple(f"2024-01-{index:02d}" for index in range(1, count + 1))


def _plan(*, minimum_dates=1, minimum_events=1):
    return {
        "statistics": {
            "bootstrap_seed": 20260907,
            "block_length": 5,
            "replicates": 1000,
            "confidence": 0.95,
            "minimum_dates": minimum_dates,
            "minimum_events": minimum_events,
            "descriptive_quantiles": (0.5,),
        }
    }


def _row(day, *, status="observed", width=4, planned=5, path="no_break",
         upper=False, lower=False, both=False, prefix_upper=False,
         prefix_lower=False, prefix_both=False, prefix_first_upper=None,
         observed_prefix=5, continuous=None):
    values = {field: 1.0 for field in CONTINUOUS}
    values.update({field: False for field in BINARY})
    values.update(
        upper_breach=upper,
        lower_breach=lower,
        both_breach=both,
        no_breach=not (upper or lower),
        prefix_upper_breach=prefix_upper,
        prefix_lower_breach=prefix_lower,
        prefix_both_breach=prefix_both,
        prefix_first_upper_minutes=prefix_first_upper,
    )
    if continuous:
        values.update(continuous)
    return {
        "date": day,
        "clock": "cash_clock",
        "horizon": "after_5m",
        "status": status,
        "path": path,
        "x_width_ticks": width,
        "planned_minutes": planned,
        "observed_prefix_minutes": observed_prefix,
        "exclusion_reasons": "" if status == "observed" else "prefix_incomplete",
        **values,
    }


def _record(rows, dates=None, *, minimum_dates=1, minimum_events=1):
    dates = _dates() if dates is None else dates
    reports = path_statistics(rows, dates, plan=_plan(
        minimum_dates=minimum_dates, minimum_events=minimum_events,
    ))
    assert len(reports) == 1
    return reports[0]


def _formation_row(day, clock="formation_clock"):
    return {
        "date": day,
        "clock": clock,
        "status": "complete",
        "zero_width": False,
        "exclusion_reasons": "",
        "width_ticks": 4,
        "volume": 10,
        "open_position": 0.5,
        "formation_up_ticks": 2,
        "formation_down_ticks": 2,
        "x_width_prior_ratio": 1.0,
        "x_formation_minutes": 5.0,
        "x_prior_20_mean_width_ticks": 4.0,
    }


def _special_row(day, clock="special_clock"):
    return {
        "date": day,
        "clock": clock,
        "payload": json.dumps({"status": "formation_unavailable", "candidate_available": False}),
    }


class JumboReportTests(unittest.TestCase):
    def test_complete_intended_date_denominator_is_retained(self):
        days = _dates()
        report = _record([_row(day) for day in days], days)
        self.assertEqual(
            (report["intended_dates"], report["actual_candidate_rows"],
             report["available_formation_dates"], report["complete_target_dates"]),
            (5, 5, 5, 5),
        )
        metric = report["metrics"]["upper_breach"]
        self.assertEqual((metric["actual_valid_date_count"], metric["actual_valid_event_count"]), (5, 5))
        self.assertEqual(metric["estimate"], 0.0)

    def test_missing_truth_is_excluded_while_false_events_remain_negative(self):
        days = _dates()
        rows = [_row(day, upper=False) for day in days[:4]]
        rows.append(_row(days[4], status="censored", width=None, upper=None))
        report = _record(rows, days)
        self.assertEqual((report["complete_target_dates"], report["available_formation_dates"],
                          report["unavailable_or_zero_width_dates"]), (4, 4, 1))
        metric = report["metrics"]["upper_breach"]
        self.assertEqual((metric["actual_valid_date_count"], metric["actual_valid_event_count"]), (4, 4))
        self.assertEqual((metric["positive_events"], metric["negative_events"]), (0, 4))
        self.assertEqual(metric["estimate"], 0.0)

    def test_partial_prefix_timing_keeps_unresolved_horizons_missing(self):
        days = _dates()
        rows = [
            _row(days[0], prefix_first_upper=2, observed_prefix=2),
            _row(days[1], prefix_first_upper=None, observed_prefix=5),
            _row(days[2], prefix_first_upper=None, observed_prefix=2),
            _row(days[3], prefix_first_upper=6, observed_prefix=5),
            _row(days[4], planned=3, prefix_first_upper=None, observed_prefix=3),
        ]
        report = _record(rows, days)
        metric = report["metrics"]["first_breach_by_5m"]
        self.assertEqual((metric["actual_valid_date_count"], metric["actual_valid_event_count"]), (3, 3))
        self.assertAlmostEqual(metric["estimate"], 1 / 3)
        self.assertEqual((metric["positive_events"], metric["negative_events"]), (1, 2))

    def test_full_population_bounds_keep_unresolved_truth_between_zero_and_one(self):
        days = _dates()
        rows = [
            _row(days[0], prefix_upper=True, upper=True),
            _row(days[1], prefix_upper=True, upper=True),
            _row(days[2], prefix_upper=False, upper=False),
            _row(days[3], status="censored", prefix_upper=False, upper=None),
            _row(days[4], width=0, prefix_upper=False, upper=False),
        ]
        report = _record(rows, days)
        lower = report["metrics"]["upper_full_population_rate_lower"]
        upper = report["metrics"]["upper_full_population_rate_upper"]
        self.assertEqual((lower["actual_valid_date_count"], upper["actual_valid_date_count"]), (4, 4))
        self.assertEqual((lower["estimate"], upper["estimate"]), (0.5, 0.75))

    def test_sparse_positive_events_are_flagged_separately_from_missingness(self):
        days = _dates()
        rows = [_row(day, upper=(index == 0)) for index, day in enumerate(days)]
        report = _record(rows, days, minimum_events=2)
        metric = report["metrics"]["upper_breach"]
        self.assertEqual((metric["positive_events"], metric["negative_events"]), (1, 4))
        self.assertTrue(metric["event_support_sparse"])
        self.assertFalse(metric["support"]["sparse"])

    def test_duplicate_clock_horizon_date_is_rejected(self):
        days = _dates()
        rows = [_row(day) for day in days]
        rows[-1] = _row(days[-2])
        with self.assertRaises(IntegrityError):
            path_statistics(rows, days, plan=_plan())

    def test_row_date_identity_mismatch_is_rejected(self):
        days = _dates()
        rows = [_row(day) for day in days[:-1]] + [_row("2024-01-06")]
        with self.assertRaises(ContractError):
            path_statistics(rows, days, plan=_plan())

    def test_missing_formation_date_is_rejected(self):
        days = _dates()
        rows = [_formation_row(day) for day in days[:-1]]
        with self.assertRaises(IntegrityError):
            formation_statistics(rows, days, plan=_plan())

    def test_missing_special_date_or_configured_clock_is_rejected(self):
        days = _dates()
        date_plan = _plan()
        date_plan["expected_special_clock_ids"] = ("special_clock",)
        with self.assertRaises(IntegrityError):
            special_statistics([_special_row(day) for day in days[:-1]], days, plan=date_plan)

        clock_plan = _plan()
        clock_plan["expected_special_clock_ids"] = ("special_clock", "missing_clock")
        with self.assertRaises(IntegrityError):
            special_statistics([_special_row(day) for day in days], days, plan=clock_plan)

    def test_scalar_date_bootstrap_is_integrated_and_compacted(self):
        days = _dates()
        rows = [
            _row(day, continuous={"upper_overshoot_W": float(index)})
            for index, day in enumerate(days, start=1)
        ]
        report = _record(rows, days)
        metric = report["metrics"]["upper_overshoot_W"]
        self.assertEqual(metric["estimate"], 3.0)
        self.assertEqual((metric["bootstrap"]["lower"], metric["bootstrap"]["upper"]), (3.0, 3.0))
        self.assertEqual(metric["bootstrap"]["valid_replicates"], 1000)
        self.assertNotIn("replicate_estimates", metric["bootstrap"])


if __name__ == "__main__":
    unittest.main()
