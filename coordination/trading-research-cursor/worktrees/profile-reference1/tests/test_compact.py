from decimal import Decimal
import json
import unittest

import pyarrow as pa

from trading_research.data.book import BookReducer
from trading_research.data.compact import (
    SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1,
    SOURCE_CLOCK_STRICT,
    CompactProjector,
    classify_redundant_backward_snapshots,
)
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


def _mbp(t, *, action='A', side='B', flags=128, source_row=0, instrument=1, bid=100.0, ask=100.25,
         bid_sz=7, ask_sz=9, price=100.0, size=1):
    return {'t': t, 'action': action, 'side': side, 'price': price, 'size': size,
            'bid_px': bid, 'ask_px': ask, 'bid_sz': bid_sz, 'ask_sz': ask_sz,
            'instrument_id': instrument, 'flags': flags, 'source_row': source_row}


_NEIGHBOR_SEQUENCES = (
    ({'action': 'C', 'ask_px': 2964.25, 'ask_sz': 13, 'bid_px': 2964.0, 'bid_sz': 45, 'flags': 128, 'instrument_id': 21336, 'price': 2964.0, 'side': 'B', 'size': 1, 't': 1590019199738625451}, 69407577),
    ({'action': 'C', 'ask_px': 2964.25, 'ask_sz': 12, 'bid_px': 2964.0, 'bid_sz': 45, 'flags': 128, 'instrument_id': 21336, 'price': 2964.25, 'side': 'A', 'size': 1, 't': 1590019199738810747}, 69407578),
    ({'action': 'C', 'ask_px': 2964.25, 'ask_sz': 11, 'bid_px': 2964.0, 'bid_sz': 45, 'flags': 128, 'instrument_id': 21336, 'price': 2964.25, 'side': 'A', 'size': 1, 't': 1590019199738810971}, 69407579),
    ({'action': 'A', 'ask_px': 2964.25, 'ask_sz': 11, 'bid_px': 2964.0, 'bid_sz': 45, 'flags': 168, 'instrument_id': 21336, 'price': 2960.0, 'side': 'N', 'size': 1, 't': 1590019199532974571}, 69407580),
    ({'action': 'A', 'ask_px': 2964.25, 'ask_sz': 11, 'bid_px': 2964.0, 'bid_sz': 46, 'flags': 128, 'instrument_id': 21336, 'price': 2964.0, 'side': 'B', 'size': 1, 't': 1590019200006488911}, 69407581),
    ({'action': 'A', 'ask_px': 2964.25, 'ask_sz': 11, 'bid_px': 2964.0, 'bid_sz': 47, 'flags': 128, 'instrument_id': 21336, 'price': 2964.0, 'side': 'B', 'size': 1, 't': 1590019200006778597}, 69407582),
), (
    ({'action': 'A', 'ask_px': 4791.0, 'ask_sz': 43, 'bid_px': 4790.75, 'bid_sz': 30, 'flags': 128, 'instrument_id': 17077, 'price': 4790.75, 'side': 'B', 'size': 1, 't': 1702943999836618063}, 56231633),
    ({'action': 'A', 'ask_px': 4791.0, 'ask_sz': 44, 'bid_px': 4790.75, 'bid_sz': 30, 'flags': 128, 'instrument_id': 17077, 'price': 4791.0, 'side': 'A', 'size': 1, 't': 1702943999906448999}, 56231634),
    ({'action': 'C', 'ask_px': 4791.0, 'ask_sz': 44, 'bid_px': 4790.75, 'bid_sz': 29, 'flags': 128, 'instrument_id': 17077, 'price': 4790.75, 'side': 'B', 'size': 1, 't': 1702943999906553119}, 56231635),
    ({'action': 'A', 'ask_px': 4791.0, 'ask_sz': 44, 'bid_px': 4790.75, 'bid_sz': 29, 'flags': 168, 'instrument_id': 17077, 'price': 4791.0, 'side': 'N', 'size': 1, 't': 1702943999906448999}, 56231636),
    ({'action': 'C', 'ask_px': 4791.0, 'ask_sz': 42, 'bid_px': 4790.75, 'bid_sz': 28, 'flags': 128, 'instrument_id': 17077, 'price': 4791.0, 'side': 'N', 'size': 1, 't': 1702944000000019461}, 56231637),
    ({'action': 'C', 'ask_px': 4791.0, 'ask_sz': 38, 'bid_px': 4790.75, 'bid_sz': 28, 'flags': 128, 'instrument_id': 17077, 'price': 4791.0, 'side': 'A', 'size': 1, 't': 1702944000000021977}, 56231638),
), (
    ({'action': 'C', 'ask_px': 5341.25, 'ask_sz': 36, 'bid_px': 5341.0, 'bid_sz': 13, 'flags': 128, 'instrument_id': 5602, 'price': 5341.0, 'side': 'B', 'size': 1, 't': 1716422399946391495}, 77086821),
    ({'action': 'C', 'ask_px': 5341.25, 'ask_sz': 36, 'bid_px': 5341.0, 'bid_sz': 12, 'flags': 128, 'instrument_id': 5602, 'price': 5341.0, 'side': 'B', 'size': 1, 't': 1716422399946486817}, 77086822),
    ({'action': 'C', 'ask_px': 5341.25, 'ask_sz': 36, 'bid_px': 5341.0, 'bid_sz': 7, 'flags': 128, 'instrument_id': 5602, 'price': 5341.0, 'side': 'B', 'size': 5, 't': 1716422399946587075}, 77086823),
    ({'action': 'A', 'ask_px': 5341.25, 'ask_sz': 36, 'bid_px': 5341.0, 'bid_sz': 7, 'flags': 168, 'instrument_id': 5602, 'price': 5339.25, 'side': 'N', 'size': 2, 't': 1716422399924792147}, 77086824),
    ({'action': 'A', 'ask_px': 5341.25, 'ask_sz': 37, 'bid_px': 5341.0, 'bid_sz': 7, 'flags': 128, 'instrument_id': 5602, 'price': 5341.25, 'side': 'A', 'size': 1, 't': 1716422400003669589}, 77086825),
    ({'action': 'A', 'ask_px': 5341.25, 'ask_sz': 37, 'bid_px': 5341.0, 'bid_sz': 8, 'flags': 128, 'instrument_id': 5602, 'price': 5341.0, 'side': 'B', 'size': 1, 't': 1716422400020389433}, 77086826),
), (
    ({'action': 'C', 'ask_px': 15031.0, 'ask_sz': 2, 'bid_px': 15030.0, 'bid_sz': 3, 'flags': 128, 'instrument_id': 3522, 'price': 15031.0, 'side': 'A', 'size': 1, 't': 1686787199841862507}, 48737764),
    ({'action': 'A', 'ask_px': 15031.0, 'ask_sz': 3, 'bid_px': 15030.0, 'bid_sz': 3, 'flags': 128, 'instrument_id': 3522, 'price': 15031.0, 'side': 'A', 'size': 1, 't': 1686787199842402341}, 48737765),
    ({'action': 'C', 'ask_px': 15031.0, 'ask_sz': 2, 'bid_px': 15030.0, 'bid_sz': 3, 'flags': 128, 'instrument_id': 3522, 'price': 15031.0, 'side': 'A', 'size': 1, 't': 1686787199904458533}, 48737766),
    ({'action': 'A', 'ask_px': 15031.0, 'ask_sz': 2, 'bid_px': 15030.0, 'bid_sz': 3, 'flags': 168, 'instrument_id': 3522, 'price': 15046.0, 'side': 'N', 'size': 1, 't': 1686787199862119295}, 48737767),
    ({'action': 'A', 'ask_px': 15031.0, 'ask_sz': 3, 'bid_px': 15030.0, 'bid_sz': 3, 'flags': 128, 'instrument_id': 3522, 'price': 15031.0, 'side': 'A', 'size': 1, 't': 1686787200002958349}, 48737768),
    ({'action': 'C', 'ask_px': 15031.0, 'ask_sz': 2, 'bid_px': 15030.0, 'bid_sz': 3, 'flags': 128, 'instrument_id': 3522, 'price': 15031.0, 'side': 'A', 'size': 1, 't': 1686787200066201611}, 48737769),
), (
    ({'action': 'C', 'ask_px': 20881.5, 'ask_sz': 6, 'bid_px': 20881.0, 'bid_sz': 1, 'flags': 128, 'instrument_id': 4358, 'price': 20881.5, 'side': 'A', 'size': 1, 't': 1720655997903208749}, 43015634),
    ({'action': 'A', 'ask_px': 20881.25, 'ask_sz': 1, 'bid_px': 20881.0, 'bid_sz': 1, 'flags': 128, 'instrument_id': 4358, 'price': 20881.25, 'side': 'A', 'size': 1, 't': 1720655999552364217}, 43015635),
    ({'action': 'C', 'ask_px': 20881.5, 'ask_sz': 6, 'bid_px': 20881.0, 'bid_sz': 1, 'flags': 128, 'instrument_id': 4358, 'price': 20881.25, 'side': 'A', 'size': 1, 't': 1720655999672987901}, 43015636),
    ({'action': 'A', 'ask_px': 20881.5, 'ask_sz': 6, 'bid_px': 20881.0, 'bid_sz': 1, 'flags': 168, 'instrument_id': 4358, 'price': 20880.75, 'side': 'N', 'size': 1, 't': 1720655999672874991}, 43015637),
    ({'action': 'A', 'ask_px': 20881.25, 'ask_sz': 1, 'bid_px': 20881.0, 'bid_sz': 1, 'flags': 128, 'instrument_id': 4358, 'price': 20881.25, 'side': 'A', 'size': 1, 't': 1720656000022892929}, 43015638),
    ({'action': 'C', 'ask_px': 20881.5, 'ask_sz': 7, 'bid_px': 20881.0, 'bid_sz': 1, 'flags': 128, 'instrument_id': 4358, 'price': 20881.25, 'side': 'A', 'size': 1, 't': 1720656000040343267}, 43015639),
)
_OFFENDING_SOURCE_ROWS = (69407580, 56231636, 77086824, 48737767, 43015637)


class RedundantBackwardSnapshotTests(unittest.TestCase):
    def projector(self):
        return CompactProjector(tick_denominator=4, maximum_rows=1000,
                                source_clock_policy=SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1)

    def project(self, rows, *, split=None, source_key='src'):
        projector = self.projector()
        quotes, trades = [], []
        batches = [rows] if split is None else [rows[:split], rows[split:]]
        for index, batch in enumerate(batches):
            q, t = projector.project(pa.Table.from_pylist(batch), source_part=str(index),
                                     physical_source_key=source_key)
            quotes.extend(q)
            trades.extend(t)
        return projector, [r for table in quotes for r in table.to_pylist()], [r for table in trades for r in table.to_pylist()]

    def test_gap_predecessor_snapshot_preserves_invalidation_and_original_rows(self):
        rows = [_mbp(100, flags=132, source_row=0),
                _mbp(90, side='N', flags=168, source_row=1),
                _mbp(110, source_row=2), _mbp(120, action='T', flags=0, source_row=3)]
        together, quotes, trades = self.project(rows)
        split, split_quotes, split_trades = self.project(rows, split=1)
        self.assertEqual(together.counts['raw_rows'], 4)
        self.assertEqual(together.counts['gap_rows'], 1)
        self.assertEqual(together.disposed_snapshot_rows, 1)
        self.assertEqual([q['source_order'] for q in quotes], [0, 2])
        self.assertEqual([q['book_valid'] for q in quotes], [0, 0])
        self.assertEqual(together.blocked, {1: 0})
        self.assertFalse(together.flow_complete[1])
        self.assertEqual(split.counts, together.counts)
        self.assertEqual(split_quotes, quotes)
        self.assertEqual(split_trades, trades)
        with self.assertRaises(IntegrityError):
            self.project([rows[0], {**rows[1], 'ask_sz': 123}])

    def test_five_retained_neighbor_records_classify_original_addresses(self):
        found = []
        for sequence in _NEIGHBOR_SEQUENCES:
            events = [{'record': record, 'source_row': source_row} for record, source_row in sequence]
            disposed = classify_redundant_backward_snapshots(events, source_key="retained-physical-source")
            self.assertEqual(len(disposed), 1)
            found.append(disposed[0]['source_row'])
            self.assertEqual(disposed[0]['predecessor_source_row'], sequence[2][1])
            self.assertEqual(disposed[0]['predecessor_action'], sequence[2][0]['action'])
            self.assertEqual(disposed[0]['predecessor_flags'], 128)
            self.assertEqual(disposed[0]['flags'], 168)
        self.assertEqual(tuple(found), _OFFENDING_SOURCE_ROWS)

    def test_literal_sequence_keeps_raw_orders_and_suppresses_only_the_replay_quote(self):
        rows = [_mbp(100, source_row=0), _mbp(90, side='N', flags=168, source_row=1),
                _mbp(110, source_row=2), _mbp(110, action='T', flags=0, source_row=3, size=3)]
        together, quotes, trades = self.project(rows)
        split, split_quotes, split_trades = self.project(rows, split=1)
        self.assertEqual(together.counts['raw_rows'], 4)
        self.assertEqual(together.counts['quote_rows'], 2)
        self.assertEqual(together.counts['trades'], 1)
        self.assertEqual(together.disposed_snapshot_rows, 1)
        self.assertEqual([q['t'] for q in quotes], [100, 110])
        self.assertEqual([q['source_order'] for q in quotes], [0, 2])
        self.assertEqual([t['source_order'] for t in trades], [3])
        self.assertEqual(together.manifest()['counts']['disposed_snapshot_rows'], 1)
        self.assertEqual(together.manifest()['source_clock_policy'], SOURCE_CLOCK_REDUNDANT_BACKWARD_SNAPSHOT_V1)
        self.assertEqual([q['t'] for q in split_quotes], [100, 110])
        self.assertEqual(split.counts, together.counts)
        self.assertEqual(split.prior_time, 110)

    def test_highwater_after_replay_and_non_admitted_predecessors_remain_errors(self):
        base = [_mbp(100, source_row=0), _mbp(90, side='N', flags=168, source_row=1)]
        with self.assertRaises(IntegrityError):
            self.project(base + [_mbp(95, source_row=2)])
        with self.assertRaises(IntegrityError):
            self.project([_mbp(100, source_row=0), _mbp(90, side='N', flags=168, source_row=1, bid_sz=8),
                          _mbp(110, source_row=2)])
        with self.assertRaises(IntegrityError):
            self.project([_mbp(100, action='T', flags=128, source_row=0),
                          _mbp(90, side='N', flags=168, source_row=1)])
        with self.assertRaises(IntegrityError):
            self.project([_mbp(100, source_row=0), _mbp(90, side='N', flags=168, source_row=1, instrument=2)])
        with self.assertRaises(IntegrityError):
            self.project([_mbp(100, source_row=0), _mbp(90, side='N', flags=168, source_row=2)])
        with self.assertRaises(IntegrityError):
            self.project([_mbp(100, source_row=0), _mbp(90, side='N', flags=160, source_row=1)])
        with self.assertRaises(IntegrityError):
            self.project([_mbp(100, source_row=0), _mbp(90, side='B', flags=168, source_row=1)])
        with self.assertRaises(IntegrityError):
            self.project([_mbp(100, source_row=0), _mbp(90, action='M', side='N', flags=168, source_row=1)])
        with self.assertRaises(IntegrityError):
            self.project(base + [_mbp(80, side='N', flags=168, source_row=2)])
        missing = [{k: v for k, v in row.items() if k != 'source_row'} for row in base]
        with self.assertRaises(IntegrityError):
            self.project(missing)
        first = self.projector()
        first.project(pa.Table.from_pylist([_mbp(100, source_row=0)]), source_part='0', physical_source_key='src')
        with self.assertRaises(IntegrityError):
            first.project(pa.Table.from_pylist([_mbp(90, side='N', flags=168, source_row=1)]),
                          source_part='1', physical_source_key='other')

    def test_strict_default_clock_and_manifest_remain_unchanged(self):
        projector = CompactProjector(tick_denominator=4, maximum_rows=10)
        projector.project(pa.Table.from_pylist([_mbp(100)]), source_part='a')
        manifest = projector.manifest()
        self.assertEqual(projector.source_clock_policy, SOURCE_CLOCK_STRICT)
        self.assertNotIn('source_clock_policy', manifest)
        self.assertNotIn('disposed_snapshot_rows', manifest['counts'])
        with self.assertRaises(IntegrityError):
            projector.project(pa.Table.from_pylist([_mbp(90, side='N', flags=168)]), source_part='b')
