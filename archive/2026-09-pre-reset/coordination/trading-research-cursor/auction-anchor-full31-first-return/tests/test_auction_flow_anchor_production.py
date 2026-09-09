from datetime import date
from pathlib import Path
import tempfile
import unittest

from trading_research.research.auction_flow_anchors import MINUTE_NS as M, AuctionAnchor
from trading_research.research.auction_flow_anchor_production import (
    REQUEST_KIND, WINDOW_CACHE_KIND, consume_anchor_schedule,
)
from trading_research.research.auction_flow_anchor_trades import admit_source_order_domain
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.auction_flow_windows import TapeWindow
from tests.test_auction_flow_anchor_trades import SCOPE, eligible_table, make_atom
from tests.test_auction_flow_anchors import CalendarFixture


COLLECTION = 'date-named-fixture'
CUT = 2**62


def window(*, source_key, lineage, start, end, values, path='glbx-mdp3-2020-03-16.dbn.zst',
           complete=True, receipt='a' * 64):
    return {
        'root': 'NQ', 'contract_key': 'NQ:NQH0', 'instrument_id': 1,
        'source_key': source_key, 'source_lineage': lineage, 'source_path': path,
        'collection': COLLECTION, 'event_start_ns': start, 'event_end_ns': end,
        'source_coverage_complete': complete, 'coordinate_complete': complete,
        'receipt_sha256': receipt, 'coordinate_identity': 'NQ:NQH0', 'latency_ns': 250,
        'trade_tables': (eligible_table(values, source_key=source_key),),
    }


def consume(schedule, catalog, *, outputs):
    return consume_anchor_schedule(
        schedule, catalog={'kind': WINDOW_CACHE_KIND, 'windows': catalog},
        calendar=CalendarFixture(), outputs=outputs)


def schedule(**kwargs):
    row = {
        'kind': REQUEST_KIND, 'collection': COLLECTION,
        'decision_cuts': ({'civil_date': date(2024, 1, 8), 'cut_ns': CUT},),
        'raw_contracts': (dict(SCOPE),),
        'named_clock_variants': (),
        'latency_ns': 250,
    }
    row.update(kwargs)
    return row


class AuctionFlowAnchorProductionTests(unittest.TestCase):
    def test_mid_minute_event_excludes_earlier_equal_time_orders_and_keeps_duplicates(self):
        event = AuctionAnchor(
            variant='causal_print', kind='event', spans=((10, 30),), selection_known_at_ns=10,
            source_versions=('trigger',), selection_evidence='known-trigger',
            start_source_order=1, **SCOPE)
        values = [(10, 400, 1, 'B', 0), (10, 400, 1, 'B', 1), (10, 400, 1, 'B', 2), (20, 404, 1, 'A', 3)]
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=4 * 1024**2,
                                     maximum_file_bytes=2 * 1024**2)
            result = consume(schedule(caller_anchors=(event,), products=('anchor_trades',)),
                             (window(source_key='physical-a', lineage=SCOPE['source_lineage'],
                                     start=0, end=40, values=values),), outputs=outputs)
        row = result['results'][0]
        flow = row['trades']['flows']['all']
        self.assertEqual(row['disposition'], 'completed')
        self.assertEqual((flow['prints'], flow['buy'], flow['sell'], flow['close'], flow['volume']),
                         (3, 2, 1, 1, 3))
        self.assertEqual(row['trades']['first_trade'][1], 1)
        self.assertEqual(row['trades']['sparse_profile']['rows'], ((400, 2, 0, 0), (404, 0, 1, 0)))
        self.assertFalse(row['whole_minute_used_across_cut'])
        self.assertEqual(len(row['reconstruction']), 1)
        self.assertEqual(row['reconstruction'][0]['start_source_order'], 1)
        independent = TapeWindow(instrument_id=1, start_ns=10, end_ns=30, latency_ns=250)
        independent.add(eligible_table(values[1:], source_key='physical-a'))
        literal = independent.record(source_coverage_complete=True, coordinate_complete=True)
        self.assertEqual(flow['prints'], literal['prints'])
        self.assertEqual(flow['close'], literal['flows']['all']['close'])

    def test_tpo_bracket_inside_source_atom_is_reconstructed(self):
        formation = AuctionAnchor(
            variant='specified_clock', kind='day', spans=((0, 20 * M),),
            selection_known_at_ns=0, source_versions=('clock',), **SCOPE)
        values = [(1, 100, 1, 'B', 0), (15 * M + 1, 104, 1, 'A', 1)]
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=4 * 1024**2,
                                     maximum_file_bytes=2 * 1024**2)
            result = consume(schedule(caller_anchors=(formation,), products=('anchor_trades', 'tpo')),
                             (window(source_key='physical-a', lineage=SCOPE['source_lineage'],
                                     start=0, end=20 * M, values=values),), outputs=outputs)
        tpo = result['results'][0]['tpo']['15']
        self.assertEqual(tpo['rows'], ((100, 1, 1), (104, 1, 2)))
        self.assertEqual(tpo['complete_brackets'], 1)
        self.assertGreaterEqual(len(result['results'][0]['reconstruction']), 1)
        self.assertTrue(any(item['start_ns'] == 15 * M or item['end_ns'] == 15 * M
                            for item in result['results'][0]['reconstruction']))

    def test_developing_prefix_excludes_future_mass(self):
        formation = AuctionAnchor(
            variant='specified_clock', kind='day', spans=((0, 40),),
            selection_known_at_ns=0, source_versions=('clock',), **SCOPE)
        values = [(1, 400, 1, 'B', 0), (11, 404, 1, 'A', 1), (21, 500, 8, 'B', 2), (31, 501, 8, 'A', 3)]
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=8 * 1024**2,
                                     maximum_file_bytes=4 * 1024**2)
            result = consume(schedule(
                caller_anchors=(
                    {'anchor': formation, 'formation': 'developing_prefix', 'event_end_ns': 20,
                     'decision_cut_ns': CUT},
                    {'anchor': formation, 'formation': 'closed', 'event_end_ns': 40,
                     'decision_cut_ns': CUT},
                ),
                products=('anchor_trades',)),
                (window(source_key='physical-a', lineage=SCOPE['source_lineage'],
                        start=0, end=40, values=values),), outputs=outputs)
        by_id = {row['request_id']: row for row in result['results']}
        prefix = next(row for row in result['results'] if row['formation'] == 'developing_prefix')
        closed = next(row for row in result['results'] if row['formation'] == 'closed')
        self.assertEqual(prefix['trades']['flows']['all']['volume'], 2)
        self.assertEqual(prefix['trades']['high_price_at_order'][0], 404)
        self.assertNotIn(500, [row[0] for row in prefix['trades']['sparse_profile']['rows']])
        self.assertEqual(closed['trades']['flows']['all']['volume'], 18)
        self.assertEqual(closed['trades']['high_price_at_order'][0], 501)
        self.assertEqual(len(by_id), 2)

    def test_disjoint_physical_files_and_catalog_overlap_reject(self):
        domain = admit_source_order_domain((
            {'source_key': 'file-a', 'source_lineage': 'lineage-a', 'event_start_ns': 0, 'event_end_ns': 10,
             'receipt_sha256': 'a' * 64, 'coordinate_identity': 'NQ:NQH0', 'instrument_id': 1,
             'contract_key': 'NQ:NQH0', 'collection': COLLECTION,
             'source_path': 'glbx-mdp3-2020-03-16.dbn.zst'},
            {'source_key': 'file-b', 'source_lineage': 'lineage-b', 'event_start_ns': 10, 'event_end_ns': 20,
             'receipt_sha256': 'b' * 64, 'coordinate_identity': 'NQ:NQH0', 'instrument_id': 1,
             'contract_key': 'NQ:NQH0', 'collection': COLLECTION,
             'source_path': 'glbx-mdp3-2020-03-17.dbn.zst'},
        ), collection=COLLECTION, raw_contract='NQ:NQH0', root='NQ')
        formation = AuctionAnchor(
            variant='civil_ny_week', kind='week', spans=((0, 20),),
            selection_known_at_ns=0, source_versions=('clock',), **{**SCOPE, 'source_lineage': COLLECTION})
        catalog = (
            window(source_key='file-a', lineage='lineage-a', start=0, end=10,
                   values=[(1, 400, 10, 'B', 0, 8), (2, 404, 10, 'A', 1, 9)]),
            window(source_key='file-b', lineage='lineage-b', start=10, end=20,
                   values=[(11, 401, 5, 'B', 0, 3), (12, 402, 5, 'A', 1, 4)],
                   path='glbx-mdp3-2020-03-17.dbn.zst', receipt='b' * 64),
        )
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=4 * 1024**2,
                                     maximum_file_bytes=2 * 1024**2)
            result = consume(schedule(caller_anchors=(formation,), products=('anchor_trades',),
                                      source_order_domain=domain.record()), catalog, outputs=outputs)
        row = result['results'][0]
        self.assertEqual(row['disposition'], 'completed')
        self.assertEqual(row['trades']['flows']['all']['volume'], 30)
        self.assertEqual(row['trades']['first_trade'][3:], ('file-a', 8))
        self.assertEqual(row['trades']['last_trade'][3:], ('file-b', 4))
        self.assertEqual((row['trades']['first_trade'][1], row['trades']['last_trade'][1]), (0, 1))
        overlap = (
            window(source_key='file-a', lineage='lineage-a', start=0, end=15,
                   values=[(1, 400, 1, 'B', 0)]),
            window(source_key='file-b', lineage='lineage-b', start=10, end=20,
                   values=[(11, 401, 1, 'A', 0)], path='glbx-mdp3-2020-03-17.dbn.zst', receipt='b' * 64),
        )
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'over', maximum_total_bytes=4 * 1024**2,
                                     maximum_file_bytes=2 * 1024**2)
            overlapped = consume(schedule(caller_anchors=(formation,), products=('anchor_trades',)),
                                 overlap, outputs=outputs)
        self.assertEqual(overlapped['results'][0]['disposition'], 'rejected')

    def test_missing_interval_is_not_quiet_or_complete(self):
        formation = AuctionAnchor(
            variant='specified_clock', kind='day', spans=((0, 30),),
            selection_known_at_ns=0, source_versions=('clock',), **SCOPE)
        catalog = (
            window(source_key='physical-a', lineage=SCOPE['source_lineage'], start=0, end=10,
                   values=[(1, 400, 1, 'B', 0)]),
            window(source_key='physical-a', lineage=SCOPE['source_lineage'], start=20, end=30,
                   values=[(21, 404, 1, 'A', 1)]),
        )
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=4 * 1024**2,
                                     maximum_file_bytes=2 * 1024**2)
            result = consume(schedule(caller_anchors=(formation,), products=('anchor_trades',)),
                             catalog, outputs=outputs)
        row = result['results'][0]
        self.assertEqual(row['trades']['missing_spans'], ((10, 20),))
        self.assertFalse(row['trades']['source_coverage_complete'])
        self.assertFalse(row['trades']['empty_observed_formation'])
        self.assertIsNone(row['trades']['count_intensity_per_second'])
        self.assertEqual(row['trades']['flows']['all']['volume'], 2)
        self.assertNotEqual(row['disposition'], 'no_volume')

    def test_rolling_removal_and_source_proxy_mass_tie(self):
        values = [(M * i + 1, 100 if i % 2 == 0 else 104, 2, ('B' if i % 2 == 0 else 'A'), i) for i in range(7)]
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=8 * 1024**2,
                                     maximum_file_bytes=4 * 1024**2)
            rolling = consume(schedule(
                rolling_minutes=(5,), rolling_event_ends=(7 * M,), products=('anchor_trades',)),
                (window(source_key='physical-a', lineage=SCOPE['source_lineage'],
                        start=0, end=7 * M, values=values),), outputs=outputs)
        row = rolling['results'][0]
        kept = [item for item in values if 2 * M <= item[0] < 7 * M]
        tape = TapeWindow(instrument_id=1, start_ns=2 * M, end_ns=7 * M, latency_ns=250)
        tape.add(eligible_table(kept, source_key='physical-a'))
        literal = tape.record(source_coverage_complete=True, coordinate_complete=True)
        self.assertEqual(row['trades']['flows']['all']['volume'], literal['flows']['all']['volume'])
        self.assertEqual(row['trades']['sparse_profile']['rows'], literal['sparse_profile']['rows'])
        self.assertEqual(row['trades']['formation_exposure_ns'], 5 * M)
        formation = AuctionAnchor(
            variant='specified_clock', kind='day', spans=((0, 20),),
            selection_known_at_ns=0, source_versions=('clock',), **SCOPE)
        bars = [(1, 100, 2, 'B', 0), (11, 104, 2, 'A', 1)]
        atoms = (
            make_atom([(1, 100, 2, 'B', 0)], 0, 10, source_key='physical-a',
                      source_lineage=SCOPE['source_lineage'], evidence='bar-0'),
            make_atom([(11, 104, 2, 'A', 1)], 10, 20, source_key='physical-a',
                      source_lineage=SCOPE['source_lineage'], evidence='bar-1'),
        )
        catalog_row = window(source_key='physical-a', lineage=SCOPE['source_lineage'],
                             start=0, end=20, values=bars)
        catalog_row['atoms'] = atoms
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'proxy', maximum_total_bytes=8 * 1024**2,
                                     maximum_file_bytes=4 * 1024**2)
            proxy = consume(schedule(
                caller_anchors=(formation,),
                products=('anchor_trades', 'profile_catalogue', 'bar_proxy_atoms')),
                (catalog_row,), outputs=outputs)
        measured = proxy['results'][0]
        variants = {item['variant']: item for item in measured['profiles']['variants']}
        self.assertEqual(variants['source-one-tick-value-7/10']['geometry']['poc_set'], (100, 104))
        self.assertEqual(variants['source-one-tick-value-7/10']['geometry']['scalar_poc'], 100)
        self.assertEqual(variants['value70-poc-tie-upper']['geometry']['scalar_poc'], 104)
        close = next(item for item in measured['bar_proxies'] if item['variant'] == 'close')
        self.assertEqual(tuple((r.row, r.mass) for r in close['allocation']['rows'] if r.mass),
                         ((100, 2), (104, 2)))
        self.assertEqual(close['retained_total_mass'], 4)

    def test_closed_cash_pending_selection_and_source_utc_day_dispositions(self):
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=4 * 1024**2,
                                     maximum_file_bytes=2 * 1024**2)
            result = consume(schedule(
                decision_cuts=({'civil_date': date(2024, 7, 4), 'cut_ns': CUT},),
                named_clock_variants=('cash_rth',),
                pending_selection_kinds=('swing',),
                requests=(
                    {'request_id': 'named-cash_rth-2024-07-04-NQ_NQH0-' + str(CUT) + '-closed',
                     'kind': 'named_clock'},
                    {'request_id': 'pending-swing-2024-07-04-NQ_NQH0-' + str(CUT),
                     'kind': 'swing'},
                    {'request_id': 'utc-source-day', 'kind': 'source_utc_day'},
                ),
                products=('anchor_trades',)), (), outputs=outputs)
        dispositions = {row['request_id']: row['disposition'] for row in result['results']}
        self.assertEqual(len(result['results']), 3)
        self.assertEqual(dispositions['named-cash_rth-2024-07-04-NQ_NQH0-' + str(CUT) + '-closed'],
                         'unavailable')
        self.assertEqual(result['results'][0]['availability']['reason'], 'published_closed_cash_date')
        self.assertEqual(dispositions['pending-swing-2024-07-04-NQ_NQH0-' + str(CUT)],
                         'pending_selection_producer')
        self.assertFalse(result['results'][1]['availability']['hindsight_pivot_manufactured'])
        self.assertEqual(dispositions['utc-source-day'], 'source_utc_day_is_not_a_scientific_formation')
        self.assertFalse(result['receipt']['family_statistics_or_model_complete'])
        self.assertEqual(result['request_count'], result['result_count'])


if __name__ == '__main__':
    unittest.main()
