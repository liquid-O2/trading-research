from fractions import Fraction
import unittest

import numpy as np

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.units import Ticks
from trading_research.measurements.cvd import fixed_source_cohort
from trading_research.measurements.tape import (
    Cohort, RowGrid, Trade, cvd_bar, profile_reference, vwap_two_pass,
)
from trading_research.research.auction_flow_measurements import OrderedFlow, SOURCE_FILTERS, SparseSideMass


class AuctionFlowMeasurementTests(unittest.TestCase):
    def values(self):
        sizes = [10, 20, 10, 30, 60, 61, 75, 99, 100, 100, 7]
        sides = [1, -1, 1, -1, 1, 1, -1, 1, -1, -1, 0]
        prices = [400, 401, 400, 402, 398, 402, 400, 398, 403, 403, None]
        return tuple(Trade(f"raw:{i}", "literal-v1", "NQH0", i // 2 + 1, i // 2 + 2,
                           None if p is None else Ticks(p), q, None if s == 0 else s,
                           i, "provider-reported-trade-record", True)
                     for i, (q, s, p) in enumerate(zip(sizes, sides, prices, strict=True)))

    def arrays(self, values):
        return {"size": np.array([t.size for t in values], dtype=np.int64),
                "side": np.array([t.side or 0 for t in values], dtype=np.int64),
                "event_ns": np.array([t.event_at for t in values], dtype=np.int64),
                "source_order": np.array([t.order for t in values], dtype=np.int64)}

    def test_all_source_filters_match_literal_ordered_path_and_mass_across_batches(self):
        values = self.values()
        for name in SOURCE_FILTERS:
            lower, upper = 1, None
            if name != "all":
                channel = next(c for c in fixed_source_cohort(name).channels if c.id == "included")
                lower, upper = channel.lower_inclusive, channel.upper_exclusive
            cohort = Cohort(name, lower, upper, name, "provider-reported-trade-record")
            literal = cvd_bar(values, opening_cvd=13, cohort=cohort, coverage_complete=True)
            for split in (1, 3, len(values)):
                actual = OrderedFlow(name, opening=13)
                for first in range(0, len(values), split):
                    actual.add(**self.arrays(values[first:first + split]))
                row = actual.record(coverage_complete=True)
                self.assertEqual((row["open"], row["close"], row["high"], row["low"],
                                  row["high_at_ns"], row["low_at_ns"]),
                                 (literal.open, literal.close, literal.high_bounds[0], literal.low_bounds[0],
                                  literal.high_at, literal.low_at))
                self.assertEqual((row["buy"], row["sell"], row["unknown"]),
                                 (literal.flow.buy, literal.flow.sell, literal.flow.unknown))
                self.assertEqual(row["volume"] + row["excluded_volume"], sum(t.size for t in values))
                self.assertEqual(row["prints"] + row["excluded_prints"], len(values))

    def test_zero_close_does_not_erase_true_extrema_and_prefix_is_not_revised(self):
        actual = OrderedFlow(opening=30)
        values = self.values()[:3]
        actual.add(**self.arrays(values[:1]))
        prefix = actual.record(coverage_complete=True)
        actual.add(**self.arrays(values[1:]))
        row = actual.record(coverage_complete=True)
        self.assertEqual((row["open"], row["high"], row["low"], row["close"]), (30, 40, 20, 30))
        self.assertEqual((prefix["high"], prefix["close"]), (40, 40))
        self.assertEqual((row["high_source_order"], row["low_source_order"]), (0, 1))

    def test_empty_cohort_missing_coverage_unknown_sign_and_source_order_are_distinct(self):
        actual = OrderedFlow("ny_ge100", opening=9)
        actual.add(**self.arrays(self.values()[:3]))
        self.assertTrue(actual.record(coverage_complete=True)["empty_observed_cohort"])
        self.assertFalse(actual.record(coverage_complete=False)["empty_observed_cohort"])
        self.assertIsNone(actual.record(coverage_complete=False)["true_signed_lower"])
        unknown = OrderedFlow()
        unknown.add(**self.arrays(self.values()[-1:]))
        row = unknown.record(coverage_complete=True)
        self.assertEqual((row["close"], row["true_signed_lower"], row["true_signed_upper"]), (0, -7, 7))
        with self.assertRaises(IntegrityError):
            unknown.add(**self.arrays(self.values()[-1:]))
        with self.assertRaises(ContractError):
            OrderedFlow().add(size=np.array([1.5]), side=np.array([1]), event_ns=np.array([1]), source_order=np.array([0]))

    def test_sparse_profile_and_exact_moments_match_literal_original_prices(self):
        values = self.values()
        for width, origin in ((1, 0), (2, 0), (2, 1), (4, -3)):
            actual = SparseSideMass(row_ticks=width, origin_ticks=origin)
            for part in (values[:4], values[4:]):
                a = self.arrays(part)
                actual.add(price_ticks=np.array([0 if t.price is None else t.price.value for t in part]),
                           price_valid=np.array([t.price is not None for t in part]), size=a["size"], side=a["side"])
            row = actual.record(coverage_complete=True)
            literal = profile_reference(values, grid=RowGrid(width, origin, "fixture-grid"),
                                        anchor_id="fixture", coverage_complete=True)
            self.assertEqual(row["rows"], literal.rows)
            self.assertEqual(sum(row["unpriced_buy_sell_unknown"]), literal.unpriced_volume)
            self.assertEqual(row["total_volume"], sum(t.size for t in values))
            if width == 1:
                m = actual.weighted_price()
                self.assertEqual((m["vwap_ticks"], m["variance_ticks_squared"]),
                                 vwap_two_pass(tuple(t for t in values if t.price is not None)))
            else:
                with self.assertRaises(ContractError):
                    actual.weighted_price()

    def test_exact_weighted_moments_preserve_small_dispersion_at_large_prices(self):
        actual = SparseSideMass()
        actual.add(price_ticks=np.array([10**12, 10**12 + 1]), price_valid=np.array([1, 1]),
                   size=np.array([1, 1]), side=np.array([1, -1]))
        moments = actual.weighted_price()
        self.assertEqual(moments["vwap_ticks"], Fraction(2 * 10**12 + 1, 2))
        self.assertEqual(moments["variance_ticks_squared"], Fraction(1, 4))

    def test_poc_plateau_and_untraded_gap_keep_mass_and_geometry_distinct(self):
        actual = SparseSideMass()
        actual.add(price_ticks=np.array([400, 402]), price_valid=np.array([1, 1]),
                   size=np.array([5, 5]), side=np.array([1, -1]))
        lower = actual.geometry(value_fraction=Fraction(7, 10), tie_rule="lower")
        upper = actual.geometry(value_fraction=Fraction(68, 100), tie_rule="upper")
        self.assertEqual(lower["poc_maximizers"], (400, 402))
        self.assertEqual((lower["poc_row"], upper["poc_row"]), (400, 402))
        self.assertEqual((lower["value_low_row"], lower["value_high_row"]), (400, 402))
        self.assertEqual(len(actual.record(coverage_complete=True)["rows"]), 2)
        self.assertEqual(lower["value_achieved_fraction"], 1)


if __name__ == "__main__":
    unittest.main()
