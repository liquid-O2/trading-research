from fractions import Fraction
import unittest

import numpy as np
import pyarrow as pa

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_native_bins import NativeEventBins, NativeSourceOwnership
from trading_research.research.auction_flow_quotes import QuoteWindow
from tests import test_auction_flow_quotes as source_fixture


raw = source_fixture.raw


class NativeEventMeasurementTests(unittest.TestCase):
    def measure(self, rows, *, batch_rows=2, age=None, adjacent=False):
        quotes, _, batches = source_fixture.AuctionFlowQuoteTests().projected(rows, batch_rows=batch_rows)
        native = NativeEventBins(instrument_id=1, start_ns=0, end_ns=100, width_ns=20)
        ownership = NativeSourceOwnership(start_ns=0, end_ns=100, width_ns=20)
        for batch in batches:
            ownership.add(batch.raw)
            for trades in batch.trades:
                native.add_trades(trades)
        quote = QuoteWindow(instrument_id=1, start_ns=0, end_ns=40 if adjacent else 100,
                            latency_ns=250, maximum_age_ns=age, native_sink=native)
        quote_records = []
        for part in quotes:
            for row in part.to_pylist():
                while row['t'] >= quote.end:
                    quote_records.append(quote.finish(coverage_complete=True))
                    quote = quote.continue_window(end_ns=min(100, quote.end + 40))
                quote.add(pa.Table.from_pylist([row], schema=part.schema))
        while True:
            quote_records.append(quote.finish(coverage_complete=True))
            if quote.end == 100:
                break
            quote = quote.continue_window(end_ns=min(100, quote.end + 40))
        values = native.table(source_eligible=ownership.eligible(1, ((0, 100),)),
                              coordinate_eligible=np.ones(5, dtype=bool), latency_ns=250)
        return values.to_pylist(), quote_records, native

    def test_true_within_cell_cvd_and_price_extrema_retain_equal_time_source_addresses(self):
        rows = [raw(0, action='A'), raw(1, action='T', flags=0, size=100),
                raw(2, action='T', flags=0, size=150, side='A'),
                raw(2, action='T', flags=0, size=75), raw(3, action='T', flags=0, size=30, side='N'),
                raw(21, action='T', flags=0, size=60, side='A'), raw(99, action='N')]
        for r, price in zip(rows[1:6], (400, 410, 402, 404, 398), strict=True):
            r['price'] = price / 4
        values, _, native = self.measure(rows)
        a, b = values[:2]
        self.assertEqual([a['all__' + k] for k in ('prints', 'volume', 'unknown', 'high', 'low', 'close')],
                         [4, 355, 30, 100, -50, 25])
        self.assertEqual([a['all__' + k] for k in ('high_at_ns', 'low_at_ns', 'high_source_order', 'low_source_order')],
                         [1, 2, 1, 2])
        self.assertEqual([a['ny_ge100__' + k] for k in ('volume', 'high', 'low', 'close')], [250, 100, -50, -50])
        self.assertEqual(a['london_ge75__close'], 25)
        self.assertEqual([a['inclusive30_through60__' + k] for k in ('volume', 'unknown', 'close')], [30, 30, 0])
        self.assertEqual(b['inclusive30_through60__close'], -60)
        self.assertEqual([a[k] for k in ('first_price_ticks', 'last_price_ticks', 'high_price_ticks', 'low_price_ticks',
            'high_price_at_ns', 'high_price_source_order', 'first_trade_source_order', 'last_trade_source_order')],
            [400, 404, 410, 400, 2, 2, 1, 4])
        self.assertTrue(all(v['source_eligible'] for v in values))
        self.assertEqual([v['all__prints'] for v in values], [4, 1, 0, 0, 0])
        self.assertEqual(native.array_bytes, native.required_array_bytes(start_ns=0, end_ns=100, width_ns=20))
        with self.assertRaises(IntegrityError):
            native.table(source_eligible=np.ones(5, dtype=bool), coordinate_eligible=np.ones(5, dtype=bool), latency_ns=250)
        together, _, _ = self.measure(rows, batch_rows=100)
        self.assertEqual(values, together)

    def test_quote_transition_and_standing_time_splits_reconcile_across_quiet_atomic_windows(self):
        rows = [raw(0, flags=32, qb=7, qa=9), raw(10, qb=11, qa=5),
                raw(15, action='T', flags=0, qb=999, qa=1),
                raw(30, bid=100.25, ask=100.5, qb=6, qa=4),
                raw(35, flags=32, bid=100.25, ask=100.5, qb=9, qa=1),
                raw(40, bid=100.25, ask=100.5, qb=8, qa=2),
                raw(40, bid=100.25, ask=100.5, qb=7, qa=3),
                raw(50, flags=132), raw(99)]
        a, records, _ = self.measure(rows)
        self.assertEqual([v['ofi_close'] for v in a], [8, 11, -4, 0, 0])
        self.assertEqual([v['ofi_high'] for v in a], [8, 11, 0, 0, 0])
        self.assertEqual([v['ofi_low'] for v in a], [0, 0, -4, 0, 0])
        self.assertEqual(a[2]['ofi_low_source_order'], 6)
        self.assertEqual([v['standing_ns'] for v in a], [10, 20, 10, 0, 0])
        self.assertEqual([v['quote_pressure_complete'] for v in a], [False, True, False, False, False])
        self.assertAlmostEqual(sum(v['duration_imbalance_ns'] for v in a), 10 * .375 + 10 * .375 + 5 * .2 + 5 * .8 + 10 * .4)
        b, adjacent, _ = self.measure(rows, adjacent=True)
        self.assertEqual(a, b)
        self.assertEqual(sum(r['ofi_contracts'] for r in adjacent), records[0]['ofi_contracts'])
        # Snapshot quote values affect the retained normalized book, but do
        # not renew the original economic age or create a fresh transition.
        c, _, _ = self.measure([raw(10, qb=6, qa=2), raw(20, flags=32, qb=5, qa=3), raw(70)], age=15)
        self.assertEqual([v['standing_ns'] for v in c], [10, 5, 0, 10, 5])

    def test_unpriced_and_snapshot_only_cells_do_not_become_complete_price_or_activity_history(self):
        rows = [raw(0, flags=32), raw(25, action='T', size=100, flags=0), raw(99)]
        rows[1]['price'] = None
        values, _, _ = self.measure(rows)
        self.assertFalse(values[0]['source_eligible'])
        self.assertEqual(values[1]['all__volume'], 100)
        self.assertEqual(values[1]['priced_prints'], 0)
        self.assertFalse(values[1]['price_history_complete'])
        self.assertTrue(values[2]['price_history_complete'])
        self.assertEqual(values[2]['first_trade_at_ns'], -1)

    def test_raw_rolls_gaps_and_missing_archive_intervals_use_only_the_observed_prefix(self):
        rows = [raw(0), raw(21, flags=32), raw(65), raw(81), raw(99)]
        _, _, batches = source_fixture.AuctionFlowQuoteTests().projected(rows)
        original = pa.concat_tables([b.raw for b in batches])
        changed = original.set_column(original.schema.get_field_index('instrument_id'), 'instrument_id', pa.array([1, 1, 2, 2, 2]))
        owners = []
        for table in (original, changed):
            owner = NativeSourceOwnership(start_ns=0, end_ns=100, width_ns=20)
            owner.add(table)
            owners.append(owner)
        self.assertEqual(owners[0].eligible(1, ((0, 100),)).tolist(), [True, False, True, True, True])
        self.assertEqual(owners[1].eligible(1, ((0, 100),)).tolist(), [True, False, True, False, False])
        self.assertEqual(owners[1].eligible(2, ((0, 100),)).tolist(), [False, False, False, False, True])
        self.assertEqual(owners[1].eligible(2, ((0, 90),)).tolist(), [False] * 5)
        with self.assertRaises(IntegrityError):
            owners[0].add(original)
        with self.assertRaises(IntegrityError):
            owners[0].eligible(1, ((0, 100),))

    def test_extreme_integer_paths_and_invalid_callback_population(self):
        rows = [raw(1, action='T', flags=0, size=2**32 - 2), raw(2, action='T', flags=0, size=2**32 - 2, side='A')]
        rows[0]['price'], rows[1]['price'] = (2**53 - 2) / 4, (2**53 - 1) / 4
        values, _, _ = self.measure(rows)
        self.assertEqual(values[0]['all__volume'], 2 * (2**32 - 2))
        self.assertEqual(values[0]['high_price_ticks'], 2**53 - 1)
        for bad in ('overlap', 'order', 'population'):
            native = NativeEventBins(instrument_id=1, start_ns=0, end_ns=100, width_ns=20)
            with self.assertRaises(IntegrityError):
                if bad == 'overlap':
                    native.quote_exposure(starts=np.array([0, 5]), ends=np.array([10, 15]),
                        bid=np.array([1, 1]), ask=np.array([2, 2]), bid_size=np.array([1, 1]), ask_size=np.array([1, 1]))
                else:
                    native.quote_updates(at=np.array([1, 2]), order=np.array([1, 1] if bad == 'order' else [1, 2]),
                        fresh=np.ones(2, dtype=bool), measured=np.ones(2, dtype=bool),
                        ofi=np.array([1, 1] if bad == 'order' else [1]), same=np.array([0, 0] if bad == 'order' else [0]))
            with self.assertRaises(IntegrityError):
                native.table(source_eligible=np.ones(5, dtype=bool), coordinate_eligible=np.ones(5, dtype=bool), latency_ns=250)


if __name__ == '__main__':
    unittest.main()
