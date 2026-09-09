"""Literal SM01-SM26 source-mechanism cases, authored before candidate execution.

Small price paths exercise local event logic. They are not assertions that a
few minute bars reproduce a full source-clock session or an actual market tape.
"""
from datetime import date, datetime, timezone
from fractions import Fraction
import unittest

from trading_research.errors import ContractError
from trading_research.research.ohlc_ranges import MinuteBars, wall_interval
from trading_research.research.ohlc_mechanisms import (
    daily_hit_statistics, daily_range_outcome, magic_outcome,
    open_to_open_outcome, overnight_pivot, three_stage_outcome,
)

M = 60_000_000_000
RAW = "NQ:NQM4:13743:activation:expiry"


def window(prices, *, start=0, known_delay=0, contract=RAW, available_at=None):
    names = ("start_ns", "end_ns", "known_at_ns", "open_ticks", "high_ticks",
             "low_ticks", "close_ticks", "volume", "contract_key", "valid")
    columns = {name: [] for name in names}
    for minute, price in enumerate(prices):
        if price is None:
            continue
        begin = start + minute * M
        values = (begin, begin + M, begin + M + known_delay, *price, 10, contract, True)
        for name, value in zip(names, values, strict=True):
            columns[name].append(value)
    bars = MinuteBars(columns, source_version="independent-special-mechanism-literal-fixture")
    return bars.window(start, start + len(prices) * M, available_at=available_at)


def rational(numerator, denominator=1):
    return {"numerator": numerator, "denominator": denominator}


def magic(prices, *, q=Fraction(3, 4)):
    formation = window([(110, 120, 100, 115)])
    return magic_outcome(formation, window(prices, start=M), invalidation=q)


class OhlcMechanismTests(unittest.TestCase):
    def test_sm01_strict_equality_is_no_break_and_edge_invalidation_is_exact(self):
        out = magic([(110, 120, 101, 119)])
        self.assertEqual(out["target"], rational(110))
        self.assertEqual(out["nominal"]["state"], "no_break_by_horizon")
        touched = magic([(121, 124, 121, 123), (123, 135, 122, 134)])
        self.assertEqual(touched["nominal"]["branches"][0]["invalidation"], rational(135))
        self.assertEqual(touched["nominal"]["state"], "invalidation_before_midpoint")
        lower = magic([(99, 99, 98, 98), (98, 99, 85, 86)])
        self.assertEqual(lower["nominal"]["branches"][0]["invalidation"], rational(85))
        self.assertEqual(lower["nominal"]["first_side"], "lower")

    def test_sm02_post_break_midpoint_and_pre_resolution_peak_bounds(self):
        out = magic([(121, 124, 121, 123), (123, 125, 110, 110)])
        observed = out["nominal"]
        self.assertEqual(observed["state"], "midpoint_before_invalidation")
        self.assertEqual(observed["first_side"], "upper")
        self.assertEqual(observed["first_break_interval_ns"], [M, 2 * M])
        branch = observed["branches"][0]
        self.assertTrue(branch["first_break_at_open"])
        self.assertTrue(branch["post_break_horizon_EQ_definite_print"])
        self.assertEqual(branch["pre_resolution_peak_extension_W_lower"], rational(1, 5))
        self.assertEqual(branch["pre_resolution_peak_extension_W_upper"], rational(1, 4))

    def test_sm03_sm04_invalidation_and_competing_same_bar_events(self):
        invalidated = magic([(121, 124, 121, 123), (123, 135, 122, 134), (134, 134, 110, 110)])
        self.assertEqual(invalidated["nominal"]["state"], "invalidation_before_midpoint")
        both = magic([(121, 124, 121, 123), (123, 136, 110, 122)])
        self.assertEqual(both["nominal"]["state"], "competing_order_ambiguous")
        self.assertEqual(set(both["nominal"]["possible_terminal_states"]),
                         {"midpoint_before_invalidation", "invalidation_before_midpoint"})
        comparator = both["nominal"]["source_branch_priority_comparator"]
        self.assertEqual(comparator["state"], "invalidation_before_midpoint")
        self.assertTrue(comparator["not_observed_order"])

    def test_sm05_sm06_first_bar_source_priorities_do_not_create_order(self):
        both = magic([(110, 121, 99, 110)], q=Fraction(1))
        self.assertEqual(both["nominal"]["state"], "first_side_ambiguous")
        self.assertEqual({b["side"] for b in both["nominal"]["branches"]}, {"upper", "lower"})
        self.assertEqual(both["nominal"]["source_branch_priority_comparator"]["side"], "upper")
        same_bar = magic([(121, 124, 110, 110)], q=Fraction(1))
        self.assertEqual(same_bar["nominal"]["state"], "midpoint_before_invalidation")
        self.assertEqual(same_bar["nominal"]["source_branch_priority_comparator"]["state"],
                         "break_then_neither_by_horizon")
        opening_lower = magic([(99, 121, 98, 110)], q=Fraction(1))
        self.assertEqual(opening_lower["nominal"]["first_side"], "lower")
        self.assertEqual(opening_lower["nominal"]["source_branch_priority_comparator"]["side"], "upper")

    def test_sm07_sm08_sm26_no_objective_censoring_and_gap_threshold(self):
        neither = magic([(121, 125, 121, 124), (124, 127, 122, 123)], q=Fraction(1))
        self.assertEqual(neither["nominal"]["state"], "break_then_neither_by_horizon")
        censored = magic([(121, 125, 121, 124), None], q=Fraction(1))
        self.assertTrue(censored["candidate_available"])
        self.assertEqual(censored["nominal"]["state"], "future_censored")
        gap = magic([(121, 124, 121, 123), (108, 109, 106, 107)], q=Fraction(1))
        self.assertEqual(gap["nominal"]["state"], "midpoint_before_invalidation")
        self.assertFalse(gap["nominal"]["branches"][0]["post_break_horizon_EQ_compatible"])
        self.assertFalse(gap["nominal"]["branches"][0]["post_break_horizon_EQ_definite_print"])

    def test_first_break_bar_return_can_precede_break_and_tick_atom_invalidates(self):
        uncertain = magic([(110, 125, 109, 123)], q=Fraction(1))
        self.assertEqual(set(uncertain["nominal"]["possible_terminal_states"]),
                         {"midpoint_before_invalidation", "break_then_neither_by_horizon"})
        narrow = magic_outcome(window([(100, 101, 100, 101)]),
                               window([(100, 102, 100, 101)], start=M), invalidation=Fraction(3, 4))
        self.assertEqual(narrow["nominal"]["state"], "invalidation_before_midpoint")

    def test_sm09_sm10_inclusive_conditioning_and_no_departure_requirement(self):
        formation = window([(110, 120, 100, 115)])
        for conditioning, expected in (([(115, 120, 111, 116)], "high_only"),
                                       ([(110, 118, 102, 112)], "neither")):
            out = three_stage_outcome(formation, window(conditioning, start=M),
                                      window([(112, 113, 110, 110)], start=2 * M))
            self.assertEqual(out["target"], rational(110))
            self.assertEqual(out["conditioning"]["stratum"], expected)
            self.assertTrue(out["nominal"]["definite_print"])
            self.assertEqual(out["nominal"]["compatible_bar_count"], 1)
            self.assertFalse(out["departure_required"])

    def test_sm11_sm12_sm13_future_does_not_rewrite_conditioning(self):
        formation = window([(110, 120, 100, 115)])
        both = three_stage_outcome(formation, window([(110, 120, 100, 115)], start=M),
                                   window([(115, 118, 112, 114)], start=2 * M))
        self.assertEqual(both["conditioning"]["stratum"], "both")
        self.assertTrue(both["conditioning"]["high_taken"])
        self.assertTrue(both["conditioning"]["low_taken"])
        self.assertFalse(both["nominal"]["compatible_reach"])
        earlier = three_stage_outcome(formation, window([(110, 120, 110, 115)], start=M),
                                      window([(115, 119, 111, 114)], start=2 * M))
        self.assertFalse(earlier["nominal"]["compatible_reach"])
        missing = three_stage_outcome(formation, window([(115, 120, 112, 116), None], start=M),
                                      window([(112, 113, 110, 110)], start=3 * M))
        self.assertTrue(missing["candidate_available"])
        self.assertFalse(missing["conditional_candidate_available"])
        self.assertEqual(missing["conditioning"]["status"], "censored")
        self.assertTrue(missing["nominal"]["definite_print"])
        self.assertIsNone(missing["inputs_known_at_ns"])

    def test_conditioning_publication_delay_changes_only_the_named_later_horizon(self):
        out = three_stage_outcome(window([(110, 120, 100, 115)]),
            window([(115, 120, 111, 116)], start=M, known_delay=M),
            window([(112, 114, 110, 110), (112, 116, 112, 114)], start=2 * M))
        self.assertEqual(out["inputs_known_at_ns"], 3 * M)
        self.assertTrue(out["nominal"]["compatible_reach"])
        self.assertEqual(out["availability_delayed"]["origin_ns"], 3 * M)
        self.assertFalse(out["availability_delayed"]["compatible_reach"])
        self.assertTrue(out["nominal_origin_precedes_input_known_at"])

    def test_sm14_sm15_open_targets_are_reference_relative(self):
        for ref, prices, stratum, direction in (
            (100, [(120, 122, 115, 116), (116, 117, 110, 110)], "above_reference", "below"),
            (120, [(100, 108, 99, 106), (106, 110, 105, 110)], "below_reference", "above")):
            out = open_to_open_outcome(window([(ref, ref, ref, ref)]), window(prices, start=M))
            self.assertEqual(out["target"], rational(110))
            self.assertEqual(out["retracement_distance_ticks"], rational(10))
            self.assertEqual(out["source_PIN076_stratum"], stratum)
            self.assertEqual(out["target_direction_from_forecast"], direction)
            self.assertTrue(out["nominal"]["definite_print"])

    def test_sm16_sm17_zero_atom_and_non_tick_fraction_do_not_imply_reversal_print(self):
        zero = open_to_open_outcome(window([(100, 100, 100, 100)]), window([(100, 103, 99, 102)], start=M))
        self.assertTrue(zero["zero_displacement"])
        self.assertEqual(zero["retracement_distance_ticks"], rational(0))
        self.assertEqual(zero["source_PIN076_stratum"], "below_reference")
        self.assertTrue(zero["nominal"]["origin_open_equals_target"])
        half = open_to_open_outcome(window([(100, 100, 100, 100)]), window([(101, 102, 100, 101)], start=M))
        self.assertEqual(half["target"], rational(201, 2))
        self.assertEqual(half["retracement_distance_ticks"], rational(1, 2))
        self.assertTrue(half["nominal"]["compatible_reach"])
        self.assertFalse(half["nominal"]["definite_print"])
        self.assertFalse(half["nominal"]["exact_integer_tick_print_possible"])

    def test_sm18_sm19_anchor_known_at_and_future_missingness_are_separate(self):
        reference = window([(100, 100, 100, 100)])
        forecast = window([(120, 120, 110, 110), (111, 114, 111, 113),
                           (113, 119, 112, 117)], start=M, known_delay=M)
        out = open_to_open_outcome(reference, forecast)
        self.assertEqual(out["inputs_known_at_ns"], 3 * M)
        self.assertTrue(out["nominal"]["compatible_reach"])
        self.assertFalse(out["availability_delayed"]["compatible_reach"])
        missing_future = open_to_open_outcome(reference, window([(120, 121, 119, 120), None], start=M))
        self.assertTrue(missing_future["candidate_available"])
        self.assertEqual(missing_future["target"], rational(110))
        self.assertEqual(missing_future["nominal"]["status"], "censored")
        missing_first = open_to_open_outcome(reference, window([None, (101, 102, 100, 101)], start=M))
        self.assertFalse(missing_first["candidate_available"])
        self.assertEqual(missing_first["status"], "forecast_open_unavailable")
        # An actual missing reference slot cannot be replaced by a later open.
        remaining = window([None, (101, 102, 100, 101)])
        reference_missing = remaining.series.window(0, M)
        no_reference = open_to_open_outcome(reference_missing, window([(120, 121, 119, 120)], start=2 * M))
        self.assertEqual(no_reference["status"], "reference_open_unavailable")
        self.assertFalse(no_reference["candidate_available"])

    def test_sm20_sm21_daily_reset_and_repeated_hits_are_distinct_statistics(self):
        monday = daily_range_outcome(window([(110, 120, 100, 115)]),
            window([(110, 112, 108, 110)] * 3, start=M), date_key="2024-06-03")
        tuesday = daily_range_outcome(window([(100, 110, 90, 105)]),
            window([(100, 102, 98, 100)], start=M), date_key="2024-06-04")
        self.assertEqual(monday["levels"]["midpoint"], rational(110))
        self.assertEqual(monday["levels"]["fib1_actual_30pct"], rational(114))
        self.assertEqual(monday["levels"]["fib2_actual_70pct"], rational(106))
        self.assertEqual(tuesday["levels"]["midpoint"], rational(100))
        self.assertEqual(tuesday["levels"]["fib1_actual_30pct"], rational(104))
        self.assertEqual(tuesday["levels"]["fib2_actual_70pct"], rational(96))
        summary = daily_hit_statistics([monday, tuesday])["levels"]["midpoint"]
        self.assertEqual(summary["eligible_dates"], 2)
        self.assertEqual(summary["unique_compatible_hit_dates"], 2)
        self.assertEqual(summary["compatible_bar_hits"], 4)
        self.assertEqual(summary["unique_day_compatible_rate"], rational(1))
        self.assertEqual(summary["repeated_hit_share_by_formation_date"]["2024-06-03"], rational(3, 4))
        self.assertEqual(summary["repeated_hit_share_by_formation_date"]["2024-06-04"], rational(1, 4))
        with self.assertRaises(ContractError):
            daily_hit_statistics([monday, monday])

    def test_explicit_observation_cut_is_preserved_for_anchor_and_delayed_windows(self):
        reference = window([(100, 100, 100, 100)])
        prices = [(120, 120, 110, 110), (111, 114, 111, 113), (113, 119, 112, 117)]
        too_early = open_to_open_outcome(reference, window(prices, start=M, known_delay=M,
                                                         available_at=2 * M))
        self.assertFalse(too_early["candidate_available"])
        self.assertEqual(too_early["status"], "forecast_open_unavailable")
        self.assertIn("final_bar_not_available", too_early["exclusion_reasons"])
        anchor_ready = open_to_open_outcome(reference, window(prices, start=M, known_delay=M,
                                                            available_at=3 * M))
        self.assertTrue(anchor_ready["candidate_available"])
        self.assertEqual(anchor_ready["inputs_known_at_ns"], 3 * M)
        self.assertEqual(anchor_ready["target"], rational(110))
        self.assertEqual(anchor_ready["nominal"]["status"], "censored")
        self.assertEqual(anchor_ready["availability_delayed"]["status"], "censored")
        self.assertIn("final_bar_not_available", anchor_ready["availability_delayed"]["exclusion_reasons"])

    def test_sm22_sm24_explicit_dates_and_lag_do_not_certify_source_daytags(self):
        recipe = {"start": {"day_offset": -1, "time": "20:00"},
                  "end": {"day_offset": 0, "time": "00:00"}, "interval": "[start,end)"}
        start, end = wall_interval(date(2024, 6, 3), recipe, "America/New_York")
        self.assertEqual(datetime.fromtimestamp(start // 1_000_000_000, timezone.utc).isoformat(),
                         "2024-06-03T00:00:00+00:00")
        self.assertEqual(datetime.fromtimestamp(end // 1_000_000_000, timezone.utc).isoformat(),
                         "2024-06-03T04:00:00+00:00")
        out = overnight_pivot(window([(100, 102, 99, 101)] * 240, start=start, known_delay=M), variant="ONS20")
        self.assertEqual(out["inputs_known_at_ns"], end + M)
        daily_recipe = {"start": {"day_offset": -1, "time": "22:00"},
                        "end": {"day_offset": 0, "time": "21:00"}, "interval": "[start,end)"}
        daily_start, daily_end = wall_interval(date(2024, 6, 3), daily_recipe, "UTC")
        daily = daily_range_outcome(
            window([(110, 120, 100, 115)] * 1380, start=daily_start, known_delay=M),
            window([(112, 115, 108, 110)], start=daily_end), date_key="2024-06-03")
        self.assertEqual(daily["weekday"], 0)
        self.assertEqual(datetime.fromtimestamp(daily["inputs_known_at_ns"] // 1_000_000_000,
                                                timezone.utc).isoformat(), "2024-06-03T21:01:00+00:00")
        self.assertIn("not certified", daily["date_semantics"])
        self.assertTrue(daily["nominal_origin_precedes_input_known_at"])

    def test_sm23_sm25_ons_preserves_ordinary_geometry_and_missing_first_slot(self):
        out = overnight_pivot(window([(102, 110, 100, 108), (108, 120, 105, 118)]), variant="ONS03")
        self.assertEqual([out["formation"][k] for k in ("open_ticks", "high_ticks", "low_ticks", "close_ticks", "width_ticks")],
                         [102, 120, 100, 118, 20])
        self.assertEqual(out["midpoint"], rational(110))
        self.assertFalse(out["opening_range_identity"])
        self.assertNotIn("classical_pivot", out)
        missing = overnight_pivot(window([None, (110, 120, 100, 115)]), variant="ONS03")
        self.assertFalse(missing["candidate_available"])
        self.assertEqual(missing["status"], "formation_unavailable")
        self.assertNotIn("midpoint", missing)

    def test_contract_mismatch_is_censored_and_invalid_fraction_is_rejected(self):
        formation = window([(110, 120, 100, 115)])
        other = window([(121, 125, 110, 110)], start=M, contract="different-raw-lifetime")
        self.assertEqual(magic_outcome(formation, other)["nominal"]["state"], "future_censored")
        missing_anchor = open_to_open_outcome(formation, other)
        self.assertEqual(missing_anchor["status"], "forecast_open_unavailable")
        for bad in (0.5, True, Fraction(3, 2)):
            with self.assertRaises(ContractError):
                open_to_open_outcome(formation, other, p=bad)
        with self.assertRaises(ContractError):
            magic_outcome(formation, other, invalidation=0.75)
        no_window = open_to_open_outcome(formation, window([(120, 120, 110, 110)], start=M))
        self.assertEqual(no_window["availability_delayed"]["status"], "no_remaining_horizon")


if __name__ == "__main__":
    unittest.main()
