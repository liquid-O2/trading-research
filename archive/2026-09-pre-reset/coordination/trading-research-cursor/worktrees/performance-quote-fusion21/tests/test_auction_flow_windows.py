from fractions import Fraction as F
from array import array
import unittest

import pyarrow as pa

from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_windows import TapeWindow, exact_sample_quantiles
from tests.test_auction_flow_quotes import AuctionFlowQuoteTests, raw


class AuctionFlowWindowTests(unittest.TestCase):
    def test_exact_quantiles_and_same_side_runs_cross_batches_with_unknown_breaks(self):
        result = self.measure([(1, 400, 1, 'B'), (2, 400, 3, 'B'), (3, 400, 5, 'B'),
            (4, 400, 7, 'N'), (5, 400, 9, 'B'), (6, 400, 11, 'B'), (7, 400, 13, 'A')])
        self.assertEqual(result['observed_maximum_same_side_run'], 3)
        self.assertEqual(result['observed_terminal_same_side_run'], 1)
        self.assertTrue(result['terminal_run_right_censored'])
        self.assertEqual(result['count_weighted_size_quantiles']['1/2'], F(7))
        self.assertEqual(result['observed_interarrival_quantiles_ns']['1/2'], F(1))
        values = array('q', [2**60 + 3, 2**60, 2**60 + 2, 2**60 + 1])
        q = exact_sample_quantiles(values, (F(0), F(1, 4), F(1, 2), F(1)))
        self.assertEqual(q, {'0': F(2**60), '1/4': F(2**60) + F(3, 4),
                             '1/2': F(2**60) + F(3, 2), '1': F(2**60 + 3)})
        self.assertEqual(list(values), [2**60 + 3, 2**60, 2**60 + 2, 2**60 + 1])

    def trades(self, values, *, end_ns=100):
        rows = []
        for at, price, size, side in values:
            row = raw(at, action="T", flags=0, size=size, side=side)
            row["price"] = None if price is None else price / 4
            rows.append(row)
        _, _, batches = AuctionFlowQuoteTests().projected(rows, end_ns=end_ns)
        return [t for b in batches for t in b.trades]

    def measure(self, values, **kwargs):
        result = TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        for part in self.trades(values):
            result.add(part)
        return result.record(source_coverage_complete=True, coordinate_complete=True, **kwargs)

    def test_actual_ordered_prices_do_not_bridge_unpriced_prints_or_erase_extrema(self):
        values = [(10, 400, 2, "B"), (20, 403, 3, "A"), (30, 400, 4, "B"),
                  (40, None, 5, "N"), (60, 500, 6, "B"), (70, 499, 7, "A")]
        result = self.measure(values)
        self.assertEqual((result["observed_price_variation_ticks"], result["observed_squared_price_variation_ticks_squared"],
                          result["observed_up_variation_ticks"], result["observed_down_variation_ticks"]), (7, 19, 3, 4))
        self.assertEqual(result["observed_adjacent_priced_pairs"], 3)
        self.assertEqual((result["observed_high_ticks"], result["observed_high_at_ns"], result["observed_low_ticks"], result["observed_low_at_ns"]),
                         (500, 60, 400, 10))
        self.assertEqual(result["observed_endpoints_displacement_ticks"], 99)
        self.assertIsNone(result["complete_path_displacement_ticks"])
        self.assertTrue(result["flow_history_complete"])
        self.assertFalse(result["price_history_complete"])
        self.assertEqual((result["flows"]["all"]["buy"], result["flows"]["all"]["sell"], result["flows"]["all"]["unknown"]), (12, 10, 5))
        self.assertEqual(result["sparse_profile"]["total_volume"], 27)
        self.assertEqual(result["sum_squared_trade_sizes"], sum(i * i for i in range(2, 8)))

    def test_equal_time_source_order_and_count_versus_size_cohort_occupancy(self):
        values = [(10, 400, 1, "B"), (10, 404, 100, "A"), (10, 401, 30, "B"), (20, 402, 75, "N")]
        result = self.measure(values)
        self.assertEqual(result["same_time_adjacent_prints"], 2)
        self.assertEqual((result["flows"]["all"]["open"], result["flows"]["all"]["high"], result["flows"]["all"]["low"], result["flows"]["all"]["close"]),
                         (0, 1, -99, -69))
        selected = result["flows"]["ny_ge100"]
        self.assertEqual((selected["count_occupancy"], selected["volume_occupancy"]), (F(1, 4), F(100, 206)))
        self.assertEqual(result["observed_price_variation_ticks"], 8)
        self.assertEqual(result["last_trade"]["source_row"], 3)

    def test_large_exact_price_and_size_products_do_not_overflow_or_cancel(self):
        result = self.measure([(10, 1, 2**31 - 1, "B"), (20, 2**53 - 1, 2**31 - 1, "A")])
        self.assertEqual(result["observed_squared_price_variation_ticks_squared"], (2**53 - 2)**2)
        self.assertEqual(result["sum_squared_trade_sizes"], 2 * (2**31 - 1)**2)
        self.assertEqual(result["weighted_price"]["variance_ticks_squared"], F((2**53 - 2)**2, 4))
        small = self.measure([(10, 10**12, 1, "B"), (20, 10**12 + 1, 1, "A")])
        self.assertEqual(small["weighted_price"]["variance_ticks_squared"], F(1, 4))

    def test_quiet_missing_and_unavailable_coordinate_windows_remain_distinct(self):
        empty = TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        observed = empty.record(source_coverage_complete=True, coordinate_complete=True)
        missing = empty.record(source_coverage_complete=False, coordinate_complete=False)
        self.assertTrue(observed["empty_observed_window"])
        self.assertEqual(observed["count_intensity_per_second"], 0)
        self.assertIsNone(observed["observed_high_ticks"])
        self.assertFalse(missing["empty_observed_window"])
        self.assertIsNone(missing["count_intensity_per_second"])
        value = TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        value.add(self.trades([(10, 400, 1, "B")])[0])
        unresolved = value.record(source_coverage_complete=True, coordinate_complete=False)
        self.assertTrue(unresolved["flow_history_complete"])
        self.assertFalse(unresolved["price_history_complete"])

    def test_bad_identity_or_repeated_physical_order_poisons_the_whole_window(self):
        table = pa.concat_tables(self.trades([(10, 400, 1, "B"), (20, 401, 1, "A")]))
        value = TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250)
        value.add(table)
        with self.assertRaises(IntegrityError):
            value.add(table)
        with self.assertRaises(IntegrityError):
            value.record(source_coverage_complete=True, coordinate_complete=True)
        bad = table.set_column(table.schema.get_field_index("instrument_id"), "instrument_id", pa.array([2] * len(table)))
        with self.assertRaises(IntegrityError):
            TapeWindow(instrument_id=1, start_ns=0, end_ns=100, latency_ns=250).add(bad)


if __name__ == "__main__":
    unittest.main()
