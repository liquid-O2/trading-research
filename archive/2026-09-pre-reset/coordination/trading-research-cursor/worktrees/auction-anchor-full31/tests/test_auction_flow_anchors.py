import copy
from datetime import date, time
from fractions import Fraction as F
import unittest

import pyarrow as pa
import pyarrow.compute as pc

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashDay
from trading_research.research.auction_flow_anchors import (
    AuctionAnchor, MINUTE_NS as M, composite_anchor, named_clock_anchors,
)
from trading_research.research.auction_flow_anchor_trades import AnchorTrades, AtomicTrades, FlowPath, RollingAnchorTrades
from trading_research.research.auction_flow_anchor_tpo import AnchorTPO, required_atom_cuts
from trading_research.research.auction_flow_anchor_profiles import PIN069BarClose, bar_proxy_atoms, profile_catalogue
from trading_research.measurements.profiles import FrozenGrid
from trading_research.research.auction_flow_measurements import SOURCE_FILTERS
from trading_research.research.auction_flow_windows import TapeWindow
from tests.test_auction_flow_windows import AuctionFlowWindowTests


SCOPE = dict(root='NQ', instrument_id=1, contract_key='NQ:NQH0', source_lineage='one-physical-acquisition')


def anchor(start, end, **kwargs):
    return AuctionAnchor(variant=kwargs.pop('variant', 'specified_clock'), kind=kwargs.pop('kind', 'day'),
        spans=((start, end),), source_versions=('fixed-fixture-clock-v1',),
        selection_known_at_ns=kwargs.pop('selection_known_at_ns', 0), **SCOPE, **kwargs)


def trade_atoms(values, cuts, *, incomplete=(), coordinate_incomplete=(), cursor=None):
    tables = AuctionFlowWindowTests().trades(values, end_ns=cuts[-1]) if values else []
    table = pa.concat_tables(tables) if tables else None
    atoms, records = [], []
    for index, (a, b) in enumerate(zip(cuts[:-1], cuts[1:], strict=True)):
        tape = TapeWindow(instrument_id=1, start_ns=a, end_ns=b, latency_ns=250)
        if table is not None:
            chosen = table.filter(pc.and_(pc.greater_equal(table['t'], a), pc.less(table['t'], b)))
            if cursor is not None and index == 0:
                chosen = chosen.filter(pc.greater_equal(chosen['source_order'], cursor))
            tape.add(chosen)
        record = tape.record(source_coverage_complete=index not in incomplete, coordinate_complete=index not in coordinate_incomplete)
        records.append(record)
        atoms.append(AtomicTrades.from_record(record, evidence_id='source-atom-' + str(index),
            start_source_order=cursor if index == 0 else None, **{k: v for k, v in SCOPE.items() if k != 'instrument_id'}))
    return tuple(atoms), records


def finish(value, end, cut=None):
    return value.record(event_end_ns=end, decision_cut_ns=end + 250 if cut is None else cut, latency_ns=250)


class CalendarFixture:
    """Independent expected cash publications, not a futures venue calendar."""
    def resolve(self, day, *, cut):
        if day.year != 2024 or cut < 1:
            raise DependencyUnavailable('fixture cash publication unavailable')
        closed = day.weekday() >= 5 or day == date(2024, 7, 4)
        early = day == date(2024, 7, 3)
        opened = None if closed else local_timestamp(day, time(9, 30), 'America/New_York')
        ended = None if closed else local_timestamp(day, time(13 if early else 16), 'America/New_York')
        return CashDay(day, 'closed' if closed else 'early_close' if early else 'regular', opened, ended,
            1, ('declared-cash-fixture',), 'timezone-fixture', 'cash-fixture')


class AuctionFlowAnchorTests(unittest.TestCase):
    def test_profile_catalogue_source_bar_proxy_and_pin069_actual_bar_publication(self):
        values = [(1, 110, 1, 'B'), (2, 100, 1, 'A'), (11, 109, 1, 'B'), (12, 105, 1, 'A'),
                  (21, 111, 1, 'B'), (22, 106, 1, 'A'), (31, 120, 1, 'B'), (32, 108, 1, 'A')]
        atoms, _ = trade_atoms(values, (0, 10, 20, 30, 40))
        formation = anchor(0, 40)
        value = AnchorTrades(formation)
        for atom in atoms:
            value.add(atom)
        catalogue = profile_catalogue(value.profile, anchor=formation, known_at_ns=290, coverage_complete=True)
        self.assertEqual(len(catalogue['variants']), 14)
        self.assertFalse(catalogue['cartesian_parameter_search'])
        grid = FrozenGrid(0, 1, 100, 120, 'observed-fixture-grid', 290)
        proxy = bar_proxy_atoms(atoms, anchor=formation, grid=grid, variant='close', coverage_complete=True)
        self.assertEqual(tuple((r.row, r.mass) for r in proxy['allocation']['rows'] if r.mass),
                         ((100, 2), (105, 2), (106, 2), (108, 2)))
        self.assertEqual(proxy['retained_total_mass'], 8)
        source_window = anchor(10, 30, variant='source_06_09_fixed_utc_minus4', kind='jumbo_named_range')
        source = PIN069BarClose(source_window)
        records = [source.add(a) for a in atoms]
        self.assertEqual(tuple(r['origin_ns'] for r in records), (0, 0, 20, 20))
        self.assertEqual(tuple(r['observed_bar_close_vwap_ticks'] for r in records), (100, F(205, 2), 106, 107))
        self.assertEqual(records[2]['selection_known_at_ns'], 280)
        self.assertFalse(records[-1]['reset'])
        broken, _ = trade_atoms([(1, 110, 1, 'B'), (11, None, 1, 'A'), (21, 120, 1, 'B')], (0, 10, 20, 30))
        source = PIN069BarClose(source_window)
        result = [source.add(a) for a in broken]
        self.assertEqual(result[-1]['status'], 'unavailable_source_high_state')
        self.assertFalse(result[-1]['source_recovery_inferred'])

    def test_named_clocks_keep_actual_cash_holidays_dst_and_prior_early_close_separate(self):
        def clocks(day):
            return named_clock_anchors(day=day, cut_ns=2**62, calendar=CalendarFixture(), **SCOPE)
        holiday = clocks(date(2024, 7, 4))
        records = {a.variant: a for a in holiday['anchors']}
        self.assertNotIn('cash_rth', records)
        self.assertEqual(holiday['unavailable'][0]['reason'], 'published_closed_cash_date')
        prior = records['prior_cash_rth']
        self.assertEqual(prior.end_ns - prior.start_ns, 210 * M)
        self.assertEqual(prior.end_ns, local_timestamp(date(2024, 7, 3), time(17), 'UTC'))
        self.assertFalse(holiday['or15_default_anchor'])
        winter = {a.variant: a for a in clocks(date(2024, 1, 8))['anchors']}
        summer = {a.variant: a for a in clocks(date(2024, 7, 8))['anchors']}
        self.assertEqual(winter['morning_06_09_ny'].start_ns - winter['source_06_09_fixed_utc_minus4'].start_ns, 60 * M)
        self.assertEqual(summer['morning_06_09_ny'].spans, summer['source_06_09_fixed_utc_minus4'].spans)
        self.assertIn('source_monday_22_21_utc', winter)
        self.assertNotIn('source_tuesday_22_21_utc', winter)
        self.assertEqual(winter['civil_ny_week'].start_ns, local_timestamp(date(2024, 1, 8), time(0), 'America/New_York'))
        quarter = {a.variant: a for a in clocks(date(2024, 12, 31))['anchors']}['civil_ny_quarter']
        self.assertEqual(quarter.end_ns, local_timestamp(date(2025, 1, 1), time(0), 'America/New_York'))

    def test_flow_composition_preserves_intraminute_extrema_cohort_exclusions_and_price_mass(self):
        values = [(1, 400, 100, 'B'), (2, 404, 100, 'A'), (11, 404, 100, 'B'),
                  (12, 401, 100, 'B'), (13, 402, 100, 'A'), (21, None, 30, 'N'), (22, 400, 60, 'B')]
        atoms, _ = trade_atoms(values, (0, 10, 20, 30))
        value = AnchorTrades(anchor(0, 30))
        for atom in atoms:
            value.add(atom)
        result = finish(value, 30)
        all_flow = result['flows']['all']
        self.assertEqual(tuple(all_flow[k] for k in ('open', 'high', 'low', 'close')), (0, 200, 0, 160))
        self.assertEqual((all_flow['high_at_ns'], all_flow['high_source_order']), (12, 3))
        self.assertIsNone(all_flow['low_at_ns'])
        self.assertEqual((all_flow['buy'], all_flow['sell'], all_flow['unknown'], all_flow['volume']), (360, 200, 30, 590))
        self.assertEqual(result['flows']['ny_ge100']['excluded_volume'], 90)
        self.assertEqual(result['flows']['inclusive30_through60']['close'], 60)
        self.assertEqual(result['flows']['inclusive30_through60']['count_occupancy'], F(2, 7))
        self.assertEqual(result['weighted_price']['vwap_ticks'], F(225100, 560))
        self.assertEqual(result['sparse_profile']['rows'], ((400, 160, 0, 0), (401, 100, 0, 0), (402, 0, 100, 0), (404, 100, 100, 0)))
        self.assertEqual(result['sparse_profile']['unpriced_buy_sell_unknown'], (0, 0, 30))
        self.assertEqual(result['high_price_at_order'], (404, 2, 1))
        self.assertEqual(result['low_price_at_order'], (400, 1, 0))
        self.assertTrue(result['flow_history_complete'])
        self.assertFalse(result['price_history_complete'])
        _, whole = trade_atoms(values, (0, 30))
        for name in SOURCE_FILTERS:
            for key in FlowPath.__dataclass_fields__:
                self.assertEqual(result['flows'][name][key], whole[0]['flows'][name][key], (name, key))
        for a, b, c in zip(*(x.paths for x in atoms), strict=True):
            self.assertEqual(a.then(b).then(c), a.then(b.then(c)))

    def test_missing_coordinates_quiet_zeros_and_constituent_integrity_are_distinct(self):
        atoms, records = trade_atoms([(1, 400, 1, 'B'), (21, 404, 1, 'A')], (0, 10, 20, 30), coordinate_incomplete=(2,))
        value = AnchorTrades(anchor(0, 30))
        value.add(atoms[0])
        value.add(atoms[2])
        result = finish(value, 30)
        self.assertEqual(result['missing_spans'], ((10, 20),))
        self.assertEqual(result['coordinate_failure_spans'], ((20, 30),))
        self.assertIsNone(result['count_intensity_per_second'])
        quiet = AnchorTrades(anchor(10, 20))
        quiet.add(atoms[1])
        quiet_result = finish(quiet, 20)
        self.assertTrue(quiet_result['empty_observed_formation'])
        self.assertEqual(quiet_result['count_intensity_per_second'], 0)
        self.assertIsNone(quiet_result['weighted_price']['vwap_ticks'])
        bad = copy.deepcopy(records[0])
        bad['sparse_profile']['rows'] = ((400, 2, 0, 0),)
        with self.assertRaises(IntegrityError):
            AtomicTrades.from_record(bad, evidence_id='changed', **{k: v for k, v in SCOPE.items() if k != 'instrument_id'})
        records[0]['first_trade']['price_ticks'] = 999
        self.assertEqual(atoms[0].first[2], 400)
        with self.assertRaises(IntegrityError):
            value.add(atoms[0])
        with self.assertRaises(IntegrityError):
            finish(value, 30)

    def test_selected_anchor_publication_composite_union_and_exact_event_cursor(self):
        a, b = anchor(0, 20), anchor(10, 30)
        selected = composite_anchor((a, b), variant='selected_union', selection_known_at_ns=500,
            selection_evidence='actual-selection-event')
        self.assertEqual(selected.spans, ((0, 30),))
        self.assertEqual(selected.members, (a.id, b.id))
        value = AnchorTrades(selected)
        atoms, _ = trade_atoms([(1, 400, 1, 'B'), (21, 404, 1, 'A')], (0, 10, 20, 30))
        for atom in atoms:
            value.add(atom)
        with self.assertRaises(ContractError):
            finish(value, 30, cut=499)
        self.assertEqual(finish(value, 30, cut=500)['known_at_ns'], 500)
        with self.assertRaises(ContractError):
            value.record(event_end_ns=30, decision_cut_ns=600, latency_ns=0)
        other = AuctionAnchor('other', 'day', 'NQ', 1, 'NQ:NQH0', 'overlapping-other-acquisition', ((0, 30),), 0, ('source',))
        with self.assertRaises(ContractError):
            composite_anchor((a, other), variant='not-an-alias', selection_known_at_ns=500, selection_evidence='decision')
        event = anchor(1, 30, kind='event', selection_known_at_ns=10, selection_evidence='known-trigger', start_source_order=1)
        before, _ = trade_atoms([(1, 400, 100, 'B'), (1, 404, 2, 'A')], (1, 30))
        with self.assertRaises(IntegrityError):
            AnchorTrades(event).add(before[0])
        after, _ = trade_atoms([(1, 400, 100, 'B'), (1, 404, 2, 'A')], (1, 30), cursor=1)
        value = AnchorTrades(event)
        value.add(after[0])
        self.assertEqual(finish(value, 30)['flows']['all']['close'], -2)

    def test_large_exact_moments_and_rolling_removals_match_literal_tape(self):
        values = [(M * i + 1, 10**12 + i, (100 if i % 2 else 30), ('A' if i % 3 else 'B')) for i in range(7)]
        atoms, _ = trade_atoms(values, tuple(i * M for i in range(8)))
        rolling = RollingAnchorTrades(minutes=5, source_versions=('clock',), **SCOPE)
        for atom in atoms[:5]:
            rolling.add(atom)
        for step in range(5, 8):
            if step > 5:
                rolling.add(atoms[step - 1])
            result = finish(rolling, step * M)
            _, literal = trade_atoms([v for v in values if (step - 5) * M <= v[0] < step * M], ((step - 5) * M, step * M))
            # The independent fixture projector renumbers source order; all
            # original order checks above use the single original projection.
            for name in SOURCE_FILTERS:
                for key in ('open', 'high', 'low', 'close', 'high_at_ns', 'low_at_ns', 'prints', 'volume', 'unknown', 'excluded_volume'):
                    self.assertEqual(result['flows'][name][key], literal[0]['flows'][name][key], (step, name, key))
            self.assertEqual(result['weighted_price']['vwap_ticks'], literal[0]['weighted_price']['vwap_ticks'])
            self.assertEqual(result['weighted_price']['variance_ticks_squared'], literal[0]['weighted_price']['variance_ticks_squared'])
            self.assertEqual(result['sparse_profile']['rows'], literal[0]['sparse_profile']['rows'])
            self.assertEqual(result['formation_exposure_ns'], 5 * M)
        self.assertEqual(tuple(rolling.profile.rows), tuple(10**12 + i for i in range(2, 7)))
        with self.assertRaises(IntegrityError):
            finish(rolling, 7 * M + M // 2)
        with self.assertRaises(IntegrityError):
            finish(rolling, 8 * M)
        big, _ = trade_atoms([(1, 2**53 - 2, 2**31 - 1, 'B'), (11, 2**53 - 1, 2**31 - 1, 'A')], (0, 10, 20))
        value = AnchorTrades(anchor(0, 20))
        for atom in big:
            value.add(atom)
        measured = finish(value, 20)['weighted_price']
        self.assertEqual(measured['vwap_ticks'], F(2**54 - 3, 2))
        self.assertEqual(measured['variance_ticks_squared'], F(1, 4))
        self.assertEqual(measured['sd_ticks_decimal50'], '0.5')
        self.assertEqual(measured['weighted_median_ticks'], 2**53 - 2)
        self.assertEqual(measured['weighted_mad_ticks'], 0)

    def test_tpo_actual_visits_provisional_final_single_prints_and_initial_balance(self):
        values = [(1, 100, 1, 'B'), (15 * M + 1, 104, 1, 'A'),
                  (30 * M + 1, 104, 1, 'B'), (45 * M + 1, 108, 1, 'A')]
        atoms, _ = trade_atoms(values, tuple(i * 15 * M for i in range(5)))
        formation = anchor(0, 60 * M)
        exact, proxy = AnchorTPO(formation), AnchorTPO(formation, representation='ohlc_range_proxy')
        for atom in atoms[:2]:
            exact.add(atom)
            proxy.add(atom)
        first = finish(exact, 30 * M)
        self.assertEqual(first['rows'], ((100, 1, 1), (104, 1, 1)))
        self.assertIsNone(first['final_single_print_rows'])
        self.assertEqual(first['initial_balance']['30']['complete_high_low_ticks'], (104, 100))
        self.assertEqual(len(finish(proxy, 30 * M)['rows']), 5)
        for atom in atoms[2:]:
            exact.add(atom)
            proxy.add(atom)
        last = finish(exact, 60 * M)
        self.assertEqual(last['rows'], ((100, 1, 1), (104, 2, 3), (108, 1, 2)))
        self.assertEqual(last['final_single_print_rows'], (100, 108))
        self.assertEqual(last['initial_balance']['60']['complete_high_low_ticks'], (108, 100))
        self.assertEqual(last['initial_balance']['60']['high'], (108, 45 * M + 1, 3))
        self.assertEqual(last['low_tail_rows'], (100,))
        self.assertEqual(last['high_tail_rows'], (108,))
        self.assertEqual(required_atom_cuts(formation, event_end_ns=60 * M), tuple(i * 15 * M for i in range(5)))
        self.assertEqual(len(finish(proxy, 60 * M)['rows']), 9)

    def test_tpo_missing_unpriced_and_boundary_crossing_never_certify_final_geometry(self):
        formation = anchor(0, 60 * M)
        atoms, _ = trade_atoms([(1, 100, 1, 'B'), (30 * M + 1, None, 1, 'A')], (0, 30 * M, 60 * M))
        exact = AnchorTPO(formation)
        for atom in atoms:
            exact.add(atom)
        result = finish(exact, 60 * M)
        self.assertFalse(result['price_history_complete'])
        self.assertIsNone(result['final_single_print_rows'])
        self.assertFalse(result['initial_balance']['60']['complete'])
        finer = AnchorTPO(formation, bracket_minutes=15)
        with self.assertRaises(IntegrityError):
            finer.add(atoms[0])
        with self.assertRaises(IntegrityError):
            finish(finer, 60 * M)
        quiet_atoms, _ = trade_atoms([], (0, 30 * M, 60 * M))
        quiet = AnchorTPO(formation)
        for atom in quiet_atoms:
            quiet.add(atom)
        record = finish(quiet, 60 * M)
        self.assertEqual(record['rows'], ())
        self.assertEqual(record['final_single_print_rows'], ())
        self.assertTrue(record['initial_balance']['60']['empty_observed_initial_balance'])


if __name__ == '__main__':
    unittest.main()
