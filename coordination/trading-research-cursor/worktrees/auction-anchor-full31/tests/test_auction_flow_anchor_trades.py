from fractions import Fraction as F
import unittest

import pyarrow as pa

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_anchors import AuctionAnchor
from trading_research.research.auction_flow_anchor_trades import (
    AnchorTrades, RollingAnchorTrades, _physical_order_allows,
    admit_source_order_domain, collection_packaging,
)
from trading_research.research.auction_flow_windows import TapeWindow


SCOPE = dict(root='NQ', instrument_id=1, contract_key='NQ:NQH0', source_lineage='date-named-fixture')


def eligible_table(values, *, source_key, instrument_id=1, latency_ns=250):
    rows = {name: [] for name in (
        't', 'source_order', 'instrument_id', 'price', 'size', 'side', 'price_valid',
        'source_row', 'source_key', 'raw_flags', 'raw_side', 'raw_action', 'known_at_ns')}
    for index, item in enumerate(values):
        at, price, size, side = item[:4]
        order = item[4] if len(item) > 4 else index
        source_row = item[5] if len(item) > 5 else index
        rows['t'].append(at)
        rows['source_order'].append(order)
        rows['instrument_id'].append(instrument_id)
        rows['price'].append(0 if price is None else price)
        rows['size'].append(size)
        rows['side'].append(1 if side == 'B' else -1 if side == 'A' else 0)
        rows['price_valid'].append(0 if price is None else 1)
        rows['source_row'].append(source_row)
        rows['source_key'].append(source_key)
        rows['raw_flags'].append(0)
        rows['raw_side'].append(side if side in ('B', 'A') else 'N')
        rows['raw_action'].append('T')
        rows['known_at_ns'].append(at + latency_ns)
    return pa.table(rows)


def make_atom(values, start, end, *, source_key, source_lineage, evidence, cursor=None):
    table = eligible_table(values, source_key=source_key)
    if cursor is not None:
        keep = [(t, o) for t, o in zip(table['t'].to_pylist(), table['source_order'].to_pylist())]
        mask = [(t > start or (t == start and o >= cursor)) and t < end for t, o in keep]
        table = table.filter(pa.array(mask))
    tape = TapeWindow(instrument_id=1, start_ns=start, end_ns=end, latency_ns=250)
    tape.add(table)
    return AtomicTrades.from_record(
        tape.record(source_coverage_complete=True, coordinate_complete=True),
        root='NQ', contract_key='NQ:NQH0', source_lineage=source_lineage,
        evidence_id=evidence, start_source_order=cursor)


def span(source_key, lineage, start, end, *, path):
    return {
        'source_key': source_key, 'source_lineage': lineage, 'event_start_ns': start, 'event_end_ns': end,
        'receipt_sha256': 'a' * 64 if source_key == 'file-a' else 'b' * 64,
        'coordinate_identity': 'NQ:NQH0', 'instrument_id': 1, 'contract_key': 'NQ:NQH0',
        'collection': 'date-named-fixture', 'source_path': path,
    }


class AuctionFlowAnchorTradesDomainTests(unittest.TestCase):
    def test_collection_packaging_keeps_monthly_and_date_named_files_distinct(self):
        self.assertEqual(collection_packaging('data/glbx-mdp3-2020-03-16.dbn.zst'), 'civil-date-named')
        self.assertEqual(collection_packaging('data/glbx-mdp3-2020-03.dbn.zst'), 'civil-month-named')
        with self.assertRaises(ContractError):
            collection_packaging('data/unlabelled-source.dbn.zst')

    def test_disjoint_files_concatenate_path_and_keep_local_orders(self):
        domain = admit_source_order_domain((
            span('file-a', 'lineage-a', 0, 10, path='glbx-mdp3-2020-03-16.dbn.zst'),
            span('file-b', 'lineage-b', 10, 20, path='glbx-mdp3-2020-03-17.dbn.zst'),
        ), collection='date-named-fixture', raw_contract='NQ:NQH0', root='NQ')
        first = make_atom([(1, 400, 10, 'B', 0, 8), (2, 404, 10, 'A', 1, 9)], 0, 10,
                          source_key='file-a', source_lineage='lineage-a', evidence='a')
        second = make_atom([(11, 401, 5, 'B', 0, 3), (12, 402, 5, 'A', 1, 4)], 10, 20,
                           source_key='file-b', source_lineage='lineage-b', evidence='b')
        value = AnchorTrades(AuctionAnchor('week', 'week', spans=((0, 20),),
            selection_known_at_ns=0, source_versions=('clock',), **SCOPE), source_order_domain=domain)
        value.add(first)
        value.add(second)
        result = value.record(event_end_ns=20, decision_cut_ns=270, latency_ns=250)
        flow = result['flows']['all']
        self.assertEqual((flow['buy'], flow['sell'], flow['unknown'], flow['close'], flow['volume'], flow['prints']),
                         (15, 15, 0, 0, 30, 4))
        self.assertEqual(result['sparse_profile']['rows'],
                         ((400, 10, 0, 0), (401, 5, 0, 0), (402, 0, 5, 0), (404, 0, 10, 0)))
        self.assertEqual(result['high_price_at_order'], (404, 2, 1))
        self.assertEqual(result['low_price_at_order'], (400, 1, 0))
        self.assertEqual(result['first_trade'][3], 'file-a')
        self.assertEqual(result['last_trade'][3], 'file-b')
        self.assertEqual((result['first_trade'][1], result['last_trade'][1]), (0, 1))
        self.assertEqual((result['first_trade'][4], result['last_trade'][4]), (8, 4))
        self.assertEqual(result['source_order_domain']['collection'], 'date-named-fixture')
        self.assertFalse(result['source_order_domain']['original_source_order_renumbered'])
        self.assertFalse(result['source_order_domain']['quote_or_book_carry_composed'])
        self.assertEqual(result['weighted_price']['vwap_ticks'], F(12055, 30))

    def test_overlapping_sources_contracts_and_missing_domain_reject(self):
        overlapping = (
            span('file-a', 'lineage-a', 0, 15, path='glbx-mdp3-2020-03-16.dbn.zst'),
            span('file-b', 'lineage-b', 10, 20, path='glbx-mdp3-2020-03-17.dbn.zst'),
        )
        with self.assertRaises(IntegrityError):
            admit_source_order_domain(overlapping, collection='date-named-fixture',
                                      raw_contract='NQ:NQH0', root='NQ')
        selected = admit_source_order_domain(overlapping, collection='date-named-fixture',
                                             raw_contract='NQ:NQH0', root='NQ',
                                             disjoint_selection=('file-a',))
        self.assertEqual(tuple(item.source_key for item in selected.spans), ('file-a',))
        mixed = dict(span('file-b', 'lineage-b', 10, 20, path='glbx-mdp3-2020-03-17.dbn.zst'),
                     contract_key='NQ:NQM0')
        with self.assertRaises(IntegrityError):
            admit_source_order_domain((
                span('file-a', 'lineage-a', 0, 10, path='glbx-mdp3-2020-03-16.dbn.zst'), mixed,
            ), collection='date-named-fixture', raw_contract='NQ:NQH0', root='NQ')
        monthly = dict(span('file-m', 'lineage-m', 10, 20, path='glbx-mdp3-2020-03.dbn.zst'))
        with self.assertRaises(IntegrityError):
            admit_source_order_domain((
                span('file-a', 'lineage-a', 0, 10, path='glbx-mdp3-2020-03-16.dbn.zst'), monthly,
            ), collection='date-named-fixture', raw_contract='NQ:NQH0', root='NQ')
        first = make_atom([(1, 400, 1, 'B', 0)], 0, 10, source_key='file-a',
                          source_lineage='lineage-a', evidence='a')
        second = make_atom([(11, 401, 1, 'A', 0)], 10, 20, source_key='file-b',
                           source_lineage='lineage-b', evidence='b')
        value = AnchorTrades(AuctionAnchor('week', 'week', spans=((0, 20),),
            selection_known_at_ns=0, source_versions=('clock',), **SCOPE))
        value.add(first)
        with self.assertRaises(IntegrityError):
            value.add(second)
        with self.assertRaises(IntegrityError):
            admit_source_order_domain((
                span('file-a', 'lineage-a', 0, 10, path='glbx-mdp3-2020-03-16.dbn.zst'),
                span('unknown', 'lineage-b', 10, 20, path='glbx-mdp3-2020-03-17.dbn.zst'),
            ), collection='date-named-fixture', raw_contract='NQ:NQH0', root='NQ',
               disjoint_selection=('missing-key',))

    def test_equal_time_cross_file_join_and_unknown_key_reject(self):
        domain = admit_source_order_domain((
            span('file-a', 'lineage-a', 0, 10, path='glbx-mdp3-2020-03-16.dbn.zst'),
            span('file-b', 'lineage-b', 10, 20, path='glbx-mdp3-2020-03-17.dbn.zst'),
        ), collection='date-named-fixture', raw_contract='NQ:NQH0', root='NQ')
        with self.assertRaises(IntegrityError):
            _physical_order_allows((10, 7, 400, 'file-a', 8), (10, 0, 401, 'file-b', 3), domain)
        rolling = RollingAnchorTrades(minutes=5, source_versions=('clock',), source_order_domain=domain, **SCOPE)
        with self.assertRaises(IntegrityError):
            rolling.add(make_atom([(1, 400, 1, 'B', 0)], 0, 10, source_key='other',
                                  source_lineage='lineage-a', evidence='x'))


if __name__ == '__main__':
    unittest.main()
