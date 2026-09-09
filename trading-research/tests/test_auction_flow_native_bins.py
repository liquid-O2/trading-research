from fractions import Fraction
import unittest

import numpy as np
import pyarrow as pa

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_native_bins import NativeEventBins, NativeSourceOwnership
from trading_research.research.auction_flow_quotes import QuoteWindow, prepare_quote_batch
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


def _independent_exposure(intervals, start, end, width):
    count = (end - start + width - 1) // width
    standing = [0] * count
    imbalance = [Fraction(0)] * count
    spread = [Fraction(0)] * count
    for s, e, bid, ask, bid_size, ask_size in intervals:
        ratio = Fraction(bid_size - ask_size, bid_size + ask_size)
        ticks = ask - bid
        first = (s - start) // width
        last = (e - 1 - start) // width
        for bin in range(first, last + 1):
            cell_start = start + bin * width
            cell_end = min(cell_start + width, end)
            duration = min(e, cell_end) - max(s, cell_start)
            standing[bin] += duration
            imbalance[bin] += duration * ratio
            spread[bin] += duration * ticks
    return standing, imbalance, spread


def _interval_columns(intervals):
    names = ('starts', 'ends', 'bid', 'ask', 'bid_size', 'ask_size')
    return {name: np.array([row[i] for row in intervals], dtype=np.int64) for i, name in enumerate(names)}


class NativeQuoteExposureReducerTests(unittest.TestCase):
    INTERVALS = (
        (5, 45, 10, 12, 3, 1),
        (50, 60, 8, 9, 1, 1),
        (60, 70, 4, 8, 3, 1),
        (75, 95, 5, 8, 1, 3),
    )

    def apply(self, origin, *, compiled=None):
        from trading_research.data import compact_native

        start, end, width = origin, origin + 95, 20
        intervals = tuple((s + origin, e + origin, bid, ask, qb, qa)
                          for s, e, bid, ask, qb, qa in self.INTERVALS)
        previous = compact_native._EXPOSURE
        if compiled is False:
            compact_native._EXPOSURE = None
        try:
            native = NativeEventBins(instrument_id=1, start_ns=start, end_ns=end, width_ns=width)
            native.quote_exposure(**_interval_columns(intervals))
            return native, _independent_exposure(intervals, start, end, width)
        finally:
            compact_native._EXPOSURE = previous

    def assert_exact(self, native, expected):
        standing, imbalance, spread = expected
        self.assertEqual(native.columns['standing_ns'].tolist(), standing)
        self.assertEqual([Fraction(float(v)).limit_denominator() for v in native.columns['duration_imbalance_ns']],
                         imbalance)
        self.assertEqual([Fraction(float(v)).limit_denominator() for v in native.columns['duration_spread_ticks_ns']],
                         spread)

    def test_crossings_gaps_and_partial_final_cell_match_independent_elapsed_mass(self):
        empty = NativeEventBins(instrument_id=1, start_ns=0, end_ns=95, width_ns=20)
        none = np.array([], dtype=np.int64)
        empty.quote_exposure(starts=none, ends=none, bid=none, ask=none, bid_size=none, ask_size=none)
        self.assertEqual(empty.columns['standing_ns'].tolist(), [0, 0, 0, 0, 0])
        for origin in (0, 10**18):
            native, expected = self.apply(origin)
            self.assert_exact(native, expected)
            standing, imbalance, spread = expected
            self.assertEqual(standing, [15, 20, 15, 15, 15])
            self.assertEqual(imbalance, [Fraction(15, 2), Fraction(10), Fraction(5, 2), Fraction(5, 2), Fraction(-15, 2)])
            self.assertEqual(spread, [Fraction(30), Fraction(40), Fraction(20), Fraction(55), Fraction(45)])

    def test_compiled_and_numpy_fallback_agree_when_backend_is_selected(self):
        from trading_research.data import compact_native

        fallback, expected = self.apply(0, compiled=False)
        self.assert_exact(fallback, expected)
        current, _ = self.apply(0)
        self.assert_exact(current, expected)
        standing = np.zeros(5, dtype=np.int64)
        imbalance = np.zeros(5, dtype=np.longdouble)
        spread = np.zeros(5, dtype=np.longdouble)
        kwargs = dict(_interval_columns(self.INTERVALS), start=0, end=95, width=20,
                      standing_ns=standing, duration_imbalance_ns=imbalance,
                      duration_spread_ticks_ns=spread)
        previous = compact_native._EXPOSURE
        compact_native._EXPOSURE = None
        try:
            self.assertFalse(compact_native.reduce_quote_exposure(**kwargs))
            self.assertEqual(standing.tolist(), [0, 0, 0, 0, 0])
        finally:
            compact_native._EXPOSURE = previous
        if compact_native._EXPOSURE is None:
            return
        before = compact_native.execution_counts()
        compiled, _ = self.apply(0)
        after = compact_native.execution_counts()
        self.assert_exact(compiled, expected)
        self.assertEqual(after['compiled_exposure_calls'], before['compiled_exposure_calls'] + 1)
        self.assertEqual(after['compiled_exposure_intervals'], before['compiled_exposure_intervals'] + 4)
        self.assertEqual(after['compiled_exposure_cells'], before['compiled_exposure_cells'] + 7)
        self.assertEqual(compiled.columns['standing_ns'].tolist(), fallback.columns['standing_ns'].tolist())
        self.assertTrue(np.allclose(compiled.columns['duration_imbalance_ns'].astype(np.float64),
                                    fallback.columns['duration_imbalance_ns'].astype(np.float64),
                                    atol=1e-6, rtol=1e-12))
        self.assertTrue(np.allclose(compiled.columns['duration_spread_ticks_ns'].astype(np.float64),
                                    fallback.columns['duration_spread_ticks_ns'].astype(np.float64),
                                    atol=1e-6, rtol=1e-12))
        self.assertTrue(compact_native.reduce_quote_exposure(**kwargs))
        sentinel = np.full(5, 7, dtype=np.int64)
        poisoned_imbalance = np.full(5, 3, dtype=np.longdouble)
        poisoned_spread = np.full(5, 4, dtype=np.longdouble)
        with self.assertRaises(IntegrityError):
            compact_native.reduce_quote_exposure(
                starts=np.array([0, 5], dtype=np.int64), ends=np.array([10, 15], dtype=np.int64),
                bid=np.array([1, 1], dtype=np.int64), ask=np.array([2, 2], dtype=np.int64),
                bid_size=np.array([1, 1], dtype=np.int64), ask_size=np.array([1, 1], dtype=np.int64),
                start=0, end=95, width=20,
                standing_ns=sentinel, duration_imbalance_ns=poisoned_imbalance,
                duration_spread_ticks_ns=poisoned_spread)
        self.assertEqual(sentinel.tolist(), [7, 7, 7, 7, 7])
        self.assertTrue(np.all(poisoned_imbalance == 3) and np.all(poisoned_spread == 4))


class NativeCompiledQuoteChannelTests(unittest.TestCase):
    def _backend(self, compiled=None):
        from trading_research.data import compact_native

        previous = (compact_native._SLICE, compact_native._NATIVE_QUOTES, compact_native._EXPOSURE)
        if compiled is False:
            compact_native._SLICE = compact_native._NATIVE_QUOTES = compact_native._EXPOSURE = None
        return previous

    def _restore(self, previous):
        from trading_research.data import compact_native

        compact_native._SLICE, compact_native._NATIVE_QUOTES, compact_native._EXPOSURE = previous

    def _measure_table(self, rows, *, compiled=None, origin=-11, start=0, end=100, width=20):
        table = source_fixture.make_quote_table(rows)
        previous = self._backend(compiled)
        try:
            native = NativeEventBins(instrument_id=1, start_ns=start, end_ns=end, width_ns=width)
            window = QuoteWindow(instrument_id=1, start_ns=start, end_ns=end, latency_ns=250,
                                 maximum_events=100, origin_ticks=origin, row_ticks=2, native_sink=native)
            with prepare_quote_batch(table) as prepared:
                for _, left, right in prepared.atomic_slices(start=start, width=width):
                    window.add_prepared(prepared, left, right)
            record = window.finish(coverage_complete=True)
            published = native.table(source_eligible=np.ones(native.count, dtype=bool),
                                     coordinate_eligible=np.ones(native.count, dtype=bool), latency_ns=250)
            return record, published, native
        finally:
            self._restore(previous)

    def test_compiled_native_tables_match_reference_across_ties_boundaries_and_negative_origin(self):
        from trading_research.data import compact_native

        rows = [
            source_fixture.quote_row(5, source_order=0, bid=400, ask=403, bid_size=8, ask_size=2),
            source_fixture.quote_row(18, source_order=1, bid=400, ask=403, bid_size=9, ask_size=1),
            source_fixture.quote_row(20, source_order=2, bid=396, ask=399, bid_size=1, ask_size=6),
            source_fixture.quote_row(20, source_order=3, bid=396, ask=399, bid_size=2, ask_size=5),
            source_fixture.quote_row(45, source_order=4, bid=410, ask=411, bid_size=4, ask_size=4),
            source_fixture.quote_row(80, source_order=5, snapshot=1, bid=410, ask=411, bid_size=7, ask_size=1),
            source_fixture.quote_row(95, source_order=6, bid=410, ask=411, bid_size=6, ask_size=2),
        ]
        fallback_record, fallback_table, fallback_native = self._measure_table(rows, compiled=False)
        current_record, current_table, current_native = self._measure_table(rows)
        self.assertEqual(current_record, fallback_record)
        self.assertEqual(current_table.to_pylist(), fallback_table.to_pylist())
        self.assertEqual(current_record['ofi_path']['high_source_order'],
                         fallback_record['ofi_path']['high_source_order'])
        self.assertEqual(current_record['displayed_midpoint_occupancy']['origin_ticks'], -11)
        self.assertEqual(current_native.columns['quote_rows'].tolist(), fallback_native.columns['quote_rows'].tolist())
        self.assertEqual(current_native.columns['ofi_high'].tolist(), fallback_native.columns['ofi_high'].tolist())
        self.assertEqual(current_native.columns['ofi_high_source_order'].tolist(),
                         fallback_native.columns['ofi_high_source_order'].tolist())
        self.assertEqual(current_native.columns['ofi_low_source_order'].tolist(),
                         fallback_native.columns['ofi_low_source_order'].tolist())
        if compact_native._NATIVE_QUOTES is None:
            return
        before = compact_native.execution_counts()
        self._measure_table(rows)
        after = compact_native.execution_counts()
        self.assertGreater(after['compiled_native_quote_calls'], before['compiled_native_quote_calls'])
        self.assertGreater(after['compiled_quote_slice_calls'], before['compiled_quote_slice_calls'])

    def test_invalid_kernel_input_does_not_mutate_outputs_and_fallback_stays_explicit(self):
        from trading_research.data import compact_native
        from trading_research.errors import IntegrityError

        sentinel = np.full(5, 7, dtype=np.int64)
        extras = [np.full(5, 3, dtype=np.int64) for _ in range(11)]
        kwargs = dict(start=0, end=95, width=20, quote_rows=sentinel,
                      fresh_quotes=extras[0], pressure_transitions=extras[1],
                      same_price_ofi=extras[2], price_change_ofi=extras[3],
                      ofi_close=extras[4], ofi_high=extras[5], ofi_low=extras[6],
                      ofi_high_at=extras[7], ofi_low_at=extras[8],
                      ofi_high_order=extras[9], ofi_low_order=extras[10])
        previous = compact_native._NATIVE_QUOTES
        compact_native._NATIVE_QUOTES = None
        try:
            self.assertFalse(compact_native.fuse_native_quote_updates(
                np.array([1, 2], dtype=np.int64), np.array([1, 2], dtype=np.int64),
                np.ones(2, dtype=bool), np.ones(2, dtype=bool),
                np.array([1, 1], dtype=np.int64), np.array([0, 0], dtype=np.int64), **kwargs))
            self.assertEqual(sentinel.tolist(), [7, 7, 7, 7, 7])
        finally:
            compact_native._NATIVE_QUOTES = previous
        if compact_native._NATIVE_QUOTES is None:
            return
        with self.assertRaises(IntegrityError):
            compact_native.fuse_native_quote_updates(
                np.array([-1, 2], dtype=np.int64), np.array([1, 2], dtype=np.int64),
                np.ones(2, dtype=bool), np.ones(2, dtype=bool),
                np.array([1, 1], dtype=np.int64), np.array([0, 0], dtype=np.int64), **kwargs)
        self.assertEqual(sentinel.tolist(), [7, 7, 7, 7, 7])
        self.assertTrue(np.all(extras[4] == 3))
        native = NativeEventBins(instrument_id=1, start_ns=0, end_ns=95, width_ns=20)
        before_rows = native.columns['quote_rows'].copy()
        with self.assertRaises(IntegrityError):
            native.apply_compiled_quote_channels(
                at=np.array([1, 1], dtype=np.int64), order=np.array([1, 1], dtype=np.int64),
                fresh=np.ones(2, dtype=bool), measured=np.ones(2, dtype=bool),
                ofi=np.array([1, 1], dtype=np.int64), same=np.array([0, 0], dtype=np.int64),
                starts=np.array([], dtype=np.int64), ends=np.array([], dtype=np.int64),
                bid=np.array([], dtype=np.int64), ask=np.array([], dtype=np.int64),
                bid_size=np.array([], dtype=np.int64), ask_size=np.array([], dtype=np.int64))
        self.assertEqual(native.columns['quote_rows'].tolist(), before_rows.tolist())
        with self.assertRaises(IntegrityError):
            native.table(source_eligible=np.ones(5, dtype=bool),
                         coordinate_eligible=np.ones(5, dtype=bool), latency_ns=250)
        if compact_native._SLICE is None:
            return
        n = 2
        poisoned = np.full(n, 9, dtype=np.int64)
        poisoned_ld = np.full(n, 4, dtype=np.longdouble)
        poisoned_u8 = np.full(n, 5, dtype=np.uint8)
        stats = np.full(22, 8, dtype=np.int64)
        with self.assertRaises(IntegrityError):
            compact_native.fuse_quote_slice(
                t=np.array([10, 20], dtype=np.int64), order=np.array([0, 1], dtype=np.int64),
                bid=np.array([1, 1], dtype=np.int64), ask=np.array([2, 2], dtype=np.int64),
                bid_size=np.array([1, 1], dtype=np.int64), ask_size=np.array([1, 1], dtype=np.int64),
                flags=np.array([0, 0], dtype=np.int64),
                valid=np.ones(2, dtype=np.uint8), snapshot=np.zeros(2, dtype=np.uint8),
                updates=np.ones(2, dtype=np.uint8), clears=np.zeros(2, dtype=np.uint8),
                previous=None, window_start=0, window_end=0, maximum_age=None,
                origin_ticks=0, row_ticks=1,
                exp_starts=poisoned, exp_ends=poisoned, exp_bid=poisoned, exp_ask=poisoned,
                exp_qb=poisoned, exp_qa=poisoned, exp_duration=poisoned,
                exp_dur_imbalance=poisoned_ld, exp_dur_spread=poisoned_ld, exp_mid=poisoned,
                meas_ofi=poisoned, meas_same=poisoned, meas_depth=poisoned_ld,
                meas_imbalance=poisoned_ld, meas_micro=poisoned_ld, meas_spread=poisoned,
                fresh_out=poisoned_u8, measured_out=poisoned_u8, stats=stats)
        self.assertEqual(poisoned.tolist(), [9, 9])
        self.assertTrue(np.all(poisoned_ld == 4) and np.all(poisoned_u8 == 5))
        self.assertEqual(stats.tolist(), [8] * 22)


class RedundantBackwardSnapshotOwnershipTests(unittest.TestCase):
    def test_authenticated_replay_counts_in_its_raw_bin_and_never_becomes_ordinary(self):
        table = pa.table({
            't': pa.array([100, 90, 110], type=pa.int64()),
            'flags': pa.array([128, 168, 0], type=pa.int64()),
            'instrument_id': pa.array([1, 1, 1], type=pa.int64()),
            'source_order': pa.array([0, 1, 2], type=pa.int64()),
            'action': pa.array(['A', 'A', 'T'], type=pa.string()),
            'size': pa.array([1, 1, 3], type=pa.int64()),
        })
        ownership = NativeSourceOwnership(start_ns=0, end_ns=200, width_ns=20)
        with self.assertRaises(IntegrityError):
            ownership.add(table)
        ownership = NativeSourceOwnership(start_ns=0, end_ns=200, width_ns=20)
        ownership.add(table, replay_mask=np.array([False, True, False]))
        self.assertEqual(int(ownership.raw_count[90 // 20]), 1)
        self.assertEqual(int(ownership.raw_count[100 // 20]), 2)
        self.assertEqual(int(ownership.ordinary_count[90 // 20]), 0)
        self.assertEqual(int(ownership.ordinary_count[100 // 20]), 2)
        self.assertEqual(ownership.replay_raw_rows, 1)
        eligible = ownership.eligible(1, ((0, 200),))
        self.assertFalse(bool(eligible[90 // 20]))
        self.assertTrue(bool(eligible[100 // 20]))

    def test_repeated_backward_bins_keep_every_raw_row(self):
        table = pa.table({'t': [100, 90, 110, 95, 120], 'flags': [128, 168, 128, 168, 128],
                          'instrument_id': [1] * 5, 'source_order': list(range(5)),
                          'action': ['A'] * 5, 'side': ['B', 'N', 'B', 'N', 'B'], 'size': [1] * 5})
        ownership = NativeSourceOwnership(start_ns=0, end_ns=200, width_ns=20)
        ownership.add(table, replay_mask=np.array([False, True, False, True, False]))
        self.assertEqual(ownership.raw_count.tolist(), [0, 0, 0, 0, 2, 2, 1, 0, 0, 0])
        self.assertEqual(ownership.ordinary_count.tolist(), [0, 0, 0, 0, 0, 2, 1, 0, 0, 0])



if __name__ == '__main__':
    unittest.main()
