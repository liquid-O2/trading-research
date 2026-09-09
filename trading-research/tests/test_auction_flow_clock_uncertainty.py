from pathlib import Path
import copy
import tempfile
import unittest

import numpy as np

from trading_research.data import clock_uncertainty as clock
from trading_research.data.compact import SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1
from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_data import AuctionFlowStream
from trading_research.research.auction_flow_quotes import QuoteWindow
from trading_research.research.auction_flow_native_bins import NativeSourceOwnership, NativeEventBins
from tests import test_auction_flow_data as source

DATASET, raw = source.DATASET, source.raw


class ClockUncertaintyTests(unittest.TestCase):
    def test_uncertain_duration_is_subtracted_not_reported_as_zero_elapsed(self):
        a, b, owner = clock.certain_segments(np.array([10, 60]), np.array([50, 90]), ((20, 40),))
        self.assertEqual(list(zip(a, b, owner)), [(10, 20, 0), (40, 50, 0), (60, 90, 1)])
        self.assertEqual(int((b-a).sum()), 50)
        self.assertFalse(clock.clock_order_valid(np.array([10, 40, 19]), None, ((20, 40),)))

    def test_reset_keeps_raw_state_carry_and_exact_unaffected_duration_across_batches(self):
        rows = [raw(10), raw(40), raw(20, action='R', side='N', size=0), raw(50), raw(60, action='T', flags=0)]
        rows[2].update(bid_px=float('nan'), ask_px=float('nan'), bid_sz=0, ask_sz=0)
        saved = clock._plans
        try:
            for batch_rows in (1, 2, 64):
                with tempfile.TemporaryDirectory() as folder:
                    root = Path(folder)
                    index = source.AuctionFlowDataTests().write(root, rows)
                    record = index['datasets'][DATASET][0]
                    plan = dict(source_path=record['path'], source_metadata_sha256=digest(record),
                        event_start_ns=0, event_end_ns=100, interval=[20, 40],
                        predecessor=clock.original_record({**rows[1], 'source_row': 1}),
                        event=clock.original_record({**rows[2], 'source_row': 2}))
                    clock.configure([plan])
                    stream = AuctionFlowStream(data_root=root, index=index, dataset=DATASET,
                        start_ns=0, end_ns=100, maximum_scan_rows=100, latency_ns=250,
                        batch_rows=batch_rows, source_clock_policy=SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1)
                    native = NativeEventBins(instrument_id=1, start_ns=0, end_ns=100, width_ns=10)
                    native.clock_uncertain_intervals = ((20,40),)
                    quote = QuoteWindow(instrument_id=1, start_ns=0, end_ns=100,
                        latency_ns=250, maximum_events=100, native_sink=native)
                    quote.clock_uncertain_intervals = ((20, 40),)
                    ownership = NativeSourceOwnership(start_ns=0, end_ns=100, width_ns=10)
                    ownership.clock_uncertain_intervals = ((20, 40),)
                    observed = []
                    for batch in stream:
                        observed.extend((v['t'], v['source_order']) for v in batch.raw.to_pylist())
                        self.assertEqual(batch.replay_source_orders, ())
                        self.assertEqual(len(batch.temporal_raw), len(batch.raw))
                        ownership.add(batch.raw)
                        for part in batch.quotes:
                            quote.add(part)
                    result = quote.finish(coverage_complete=False)
                    self.assertEqual(observed, [(10, 0), (40, 1), (20, 2), (50, 3), (60, 4)])
                    self.assertEqual(result['observed_trusted_standing_duration_ns'], 10)
                    self.assertEqual(result['clear_rows'], 1)
                    self.assertEqual(int(native.columns['quote_rows'].sum()), 4)
                    self.assertEqual(int(native.columns['standing_ns'].sum()), 10)
                    self.assertEqual(int(ownership.raw_count.sum()), 5)
                    self.assertEqual(int(ownership.ordinary_count.sum()), 5)
                    self.assertEqual(stream.carry()['blocked']['1']['source_order'], 2)
                    self.assertEqual(stream.carry()['blocked']['1']['event_ns'], 20)
                    self.assertIn('source_clock_uncertainty', stream.manifest())
                    changed = copy.deepcopy(plan)
                    changed['event']['bid_sz'] = 9
                    clock.configure([changed])
                    with self.assertRaises(IntegrityError):
                        list(AuctionFlowStream(data_root=root, index=index, dataset=DATASET,
                            start_ns=0, end_ns=100, maximum_scan_rows=100, latency_ns=250,
                            source_clock_policy=SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1))
        finally:
            clock._plans = saved
