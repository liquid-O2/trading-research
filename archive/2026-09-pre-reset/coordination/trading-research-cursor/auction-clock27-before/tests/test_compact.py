from decimal import Decimal
import json
import unittest

import pyarrow as pa

from trading_research.data.book import BookReducer
from trading_research.data.compact import CompactProjector
from trading_research.data.events import decode_fields
from trading_research.errors import ContractError,IntegrityError
from tests.test_market_data import event


class CompactProjectionTests(unittest.TestCase):
    def project(self,events):
        projector=CompactProjector(tick_denominator=4,maximum_rows=1000)
        qs=[];ts=[]
        # Deliberately split the gap from later clean-looking quotes.
        for i in range(0,len(events),2):
            batch=pa.RecordBatch.from_pylist([decode_fields(e.raw_fields) for e in events[i:i+2]])
            q,t=projector.project(batch,source_part=f'fixture:{i}');qs.extend(q);ts.extend(t)
        return projector,[r for t in qs for r in t.to_pylist()],[r for t in ts for r in t.to_pylist()]

    def test_vector_projection_matches_literal_quotes_and_flow_across_gap_and_clear(self):
        events=(event(0),event(1,action='T',flags=0,size=3),event(2,action='T',flags=0,side='N',size=4),
                event(3,bid_size=8),event(4,flags=132),event(5),event(6,action='R'),event(7,flags=168),event(8))
        p,quotes,trades=self.project(events);literal=BookReducer();expected=[]
        for e in events:
            state=literal.apply(e).after
            if e.action in ('A','M','C','R') or int(e.flags)&4:expected.append(state.trusted)
        self.assertEqual([bool(q['book_valid']) for q in quotes],expected)
        self.assertEqual(p.manifest()['counts']['volume'],literal.states[1].total_volume)
        self.assertEqual(p.counts['unknown_volume'],4);self.assertEqual(len(trades),2)
        self.assertFalse(quotes[-1]['book_valid']);self.assertFalse(p.flow_complete[1])

    def test_duplicate_prints_off_grid_price_and_snapshot_flags_preserve_distinct_channels(self):
        events=(event(0),event(1,action='T',flags=0,at=12,size=2),event(2,action='T',flags=0,at=12,size=2),
                event(3,action='T',flags=32,size=9),event(4,action='T',flags=0,side='?',price=100.1,size=3))
        p,q,t=self.project(events)
        self.assertEqual((p.counts['volume'],p.counts['trades'],p.counts['unpriced_volume'],p.counts['unknown_volume']),(7,3,3,3))
        self.assertEqual(p.counts['snapshot_trade_rows'],1);self.assertEqual(t[0]['t'],t[1]['t']);self.assertNotEqual(t[0]['source_order'],t[1]['source_order'])
        self.assertEqual(t[-1]['price_valid'],0);self.assertEqual(q[0]['bid'],400)

    def test_unused_column_changes_raw_identity_and_out_of_order_or_unbounded_scan_is_rejected(self):
        raw=decode_fields(event(0).raw_fields);a=CompactProjector(tick_denominator=4,maximum_rows=10);b=CompactProjector(tick_denominator=4,maximum_rows=10)
        a.project(pa.RecordBatch.from_pylist([{**raw,'unused':'first'}]),source_part='same')
        b.project(pa.RecordBatch.from_pylist([{**raw,'unused':'second'}]),source_part='same')
        self.assertNotEqual(a.manifest()['all_selected_field_stream_hash'],b.manifest()['all_selected_field_stream_hash'])
        with self.assertRaises(IntegrityError):a.project(pa.RecordBatch.from_pylist([{**raw,'t':1}]),source_part='later')
        c=CompactProjector(tick_denominator=4,maximum_rows=1)
        with self.assertRaises(ContractError):c.project(pa.RecordBatch.from_pylist([raw,raw]),source_part='too-long')

    def test_one_instruments_gap_does_not_invalidate_another_contract(self):
        events=(event(0,flags=132,instrument=1),event(1,instrument=2),event(2,instrument=1),event(3,instrument=2))
        p,q,t=self.project(events)
        self.assertEqual({r['instrument_id']:bool(r['book_valid']) for r in q},{1:False,2:True})
        self.assertEqual(set(p.blocked),{1})


class CompiledCompactProjectionTests(unittest.TestCase):
    def acquired(self, rows):
        types = {'t': pa.int64(), 'action': pa.dictionary(pa.int8(), pa.string()),
                 'side': pa.dictionary(pa.int8(), pa.string()), 'price': pa.float64(),
                 'size': pa.int32(), 'bid_px': pa.float64(), 'ask_px': pa.float64(),
                 'bid_sz': pa.int32(), 'ask_sz': pa.int32(), 'instrument_id': pa.int32(), 'flags': pa.int16()}
        return pa.table({name: pa.array([row[name] for row in rows], type=dtype) for name, dtype in types.items()})

    def compare(self, batches):
        from trading_research.data import compact_native
        if compact_native._FUNCTION is None:
            self.skipTest('compiled backend is activated by the registered family runner')
        native = compact_native._FUNCTION
        candidate = CompactProjector(tick_denominator=4, maximum_rows=100000)
        reference = CompactProjector(tick_denominator=4, maximum_rows=100000)
        for index, batch in enumerate(batches):
            got = candidate.project(batch, source_part=str(index))
            try:
                compact_native._FUNCTION = None
                expected = reference.project(batch, source_part=str(index))
            finally:
                compact_native._FUNCTION = native
            for left, right in zip(got, expected, strict=True):
                self.assertEqual(len(left), len(right))
                for a, b in zip(left, right, strict=True):
                    self.assertTrue(a.equals(b, check_metadata=True), (a, b))
            self.assertEqual(candidate.manifest(), reference.manifest())
        return candidate

    def test_fused_acquired_schema_preserves_price_boundaries_and_all_event_channels(self):
        import math
        from trading_research.data import compact_native
        before = compact_native.execution_counts()['fused_rows']
        prices = (100., 100.1, 0., -1., float('nan'), float('inf'), -float('inf'),
                  2.**51, math.nextafter(2.**51, 0.), .25)
        rows = []
        for i in range(180):
            rows.append(dict(t=i//2, action=('A','M','C','T','T','T','N','R','?',None)[i%10],
                side=('B','A','N','?',None)[i%5], price=prices[i%len(prices)],
                size=(1,2,0,-1,2**31-1)[i%5], bid_px=prices[(i+1)%len(prices)],
                ask_px=prices[(i+2)%len(prices)], bid_sz=(1,0,-1,2**31-1)[i%4], ask_sz=7,
                instrument_id=1, flags=(0,32,4,128,36)[i%5]))
        self.compare([self.acquired(rows[:37]), self.acquired(rows[37:])])
        self.assertEqual(compact_native.execution_counts()['fused_rows']-before, 180)

    def test_fused_quotes_trades_and_reference_fallback_keep_original_global_addresses(self):
        rows = [dict(t=i, action='T' if i%3==0 else 'M', side='A' if i%2 else 'B',
                     price=100.25, size=3, bid_px=100., ask_px=100.25,
                     bid_sz=7+i, ask_sz=9, instrument_id=1, flags=0) for i in range(24)]
        mixed = [dict(row, instrument_id=1+i%2) for i,row in enumerate(rows[8:16])]
        nullable = [dict(row, bid_sz=None if i==0 else row['bid_sz']) for i,row in enumerate(rows[16:])]
        value = self.compare([self.acquired(rows[:8]), self.acquired(mixed), self.acquired(nullable)])
        self.assertEqual(value.counts['trades'], 8)
        self.assertEqual(value.counts['volume'], 24)
