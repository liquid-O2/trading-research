from dataclasses import FrozenInstanceError, asdict, replace
from datetime import date, datetime, time, timedelta
import json
from pathlib import Path
import tempfile
import unittest

from references.calendar_literal import intersection as literal_intersection, wall_contains
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import Calendar, FormationWindow, Session, local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar, CashDay, VenueBoundary, e0_window, zone_version
from trading_research.foundations.intervals import (
    BoundaryRule, CalendarEvent, Intersection, IntervalGraph, NamedInterval, Span,
    WallRule, intersect_spans, session_graph, session_union, union_spans,
)
from trading_research.foundations.time import MINUTE, NS, datetime_ns
from trading_research.operations.artifacts import code_manifest, file_digest

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / 'tests/golden/f03-intervals.json').read_text())
DAY = date(2026, 7, 1)


def interval(name='a', spans=((0, 10), (20, 30)), *, known_at=0):
    return NamedInterval(name, 'range', tuple(Span(*s) for s in spans), known_at,
                         'synthetic-rules-v1', 'synthetic_utc_ns', 'synthetic-zone-v1', (DAY,))


def wall(name='w', start='09:00', end='09:30', *, day=DAY, end_day=None, zone='America/New_York', **kw):
    return WallRule(name, 'range', kw.pop('trading_date', day), day, end_day or day,
                    start, end, zone, kw.pop('clock_variant', zone), zone_version(zone),
                    0, 'source-clock-fixture-v1', **kw)


def session(**kw):
    fields = dict(id='NQ-synthetic-date', trading_date=DAY, instrument_root='NQ', open_at=10, close_at=100,
                  required_boundaries=(('firm', 90), ('platform', 80)), execution_margin_ns=5,
                  known_at=1, source_version='synthetic-calendar-v1', timezone_version='synthetic-tz-v1',
                  eligible=True, eligibility_reason='synthetic interval only')
    fields.update(kw)
    return Session(**fields)


class IntervalGraphTests(unittest.TestCase):
    def test_summer_ny_fixed_est_and_nine_vs_nine_thirty_match_frozen_utc(self):
        points = {'summer_ny_09_00_utc': local_timestamp(DAY, time(9), 'America/New_York'),
                  'summer_ny_09_30_utc': local_timestamp(DAY, time(9, 30), 'America/New_York'),
                  'summer_fixed_est_09_30_utc': local_timestamp(DAY, time(9, 30), 'Etc/GMT+5')}
        for name, value in points.items():
            self.assertEqual(value, datetime_ns(datetime.fromisoformat(GOLDEN[name])))
        ny, fixed = wall().compile(), wall(zone='Etc/GMT+5').compile()
        self.assertNotEqual(ny.version, fixed.version)
        self.assertNotEqual(ny.clock_variant, fixed.clock_variant)

    def test_dst_gap_fold_and_non_24_hour_calendar_days(self):
        with self.assertRaises(ContractError):
            wall(start='02:00', end='03:00', day=date(2026, 3, 8)).compile()
        with self.assertRaises(ContractError):
            wall(start='01:00', end='02:00', day=date(2026, 11, 1)).compile()
        a = wall(start='01:30', end='02:00', day=date(2026, 11, 1), start_fold=0).compile()
        b = wall(start='01:30', end='02:00', day=date(2026, 11, 1), start_fold=1).compile()
        self.assertEqual(b.spans[0].start - a.spans[0].start, GOLDEN['fall_fold_difference_hours'] * 3600 * NS)
        for day, hours in ((date(2026, 3, 8), GOLDEN['spring_day_hours']),
                           (date(2026, 11, 1), GOLDEN['fall_day_hours'])):
            node = wall(start='00:00', end='00:00', day=day, end_day=day + timedelta(days=1)).compile()
            self.assertEqual(node.duration_ns, hours * 3600 * NS)

    def test_sunday_midnight_interval_keeps_declared_trading_date_and_last_nanosecond(self):
        monday = date(2026, 9, 7)
        rule = wall(start='20:00', end='00:00', day=date(2026, 9, 6), end_day=monday, trading_date=monday)
        node = rule.compile()
        self.assertEqual(node.trading_dates, (monday,))
        self.assertEqual(node.duration_ns, GOLDEN['overnight_hours'] * 3600 * NS)
        start, end = node.spans[0].start, node.spans[0].end
        self.assertTrue(node.contains(start, cut=0))
        self.assertTrue(node.contains(end - 1, cut=0))
        self.assertFalse(node.contains(end, cut=0))

    def test_compiled_intersections_match_literal_and_preserve_inactive_gaps(self):
        a, b = interval(), interval('b', ((5, 25),), known_at=2)
        spec = Intersection('overlap', 'consumer', ('a', 'b'), 'intersection-v1', 3)
        graph = IntervalGraph('scope', (a, b), intersections=(spec,))
        expected = tuple(tuple(v) for v in GOLDEN['intersection'])
        self.assertEqual(tuple((s.start, s.end) for s in graph.intervals['overlap'].spans), expected)
        self.assertEqual(literal_intersection(((0, 10), (20, 30)), ((5, 25),)), expected)
        for at in range(-1, 32):
            self.assertEqual(graph.query('overlap', at, cut=3), any(x <= at < y for x, y in expected))
        self.assertEqual(intersect_spans((Span(0, 5),), (Span(5, 10),)), ())
        self.assertEqual(union_spans((Span(5, 10), Span(0, 5))), (Span(0, 10),))
        with self.assertRaises(DependencyUnavailable):
            graph.query('overlap', 6, cut=2)
        with self.assertRaises(DependencyUnavailable):
            graph.query('unregistered', 6, cut=3)

    def test_weekly_dated_union_keeps_a_holiday_and_short_session(self):
        rows = []
        for n, (start, end, eligible) in enumerate(((10, 20, True), (30, 40, True), (41, 49, False), (50, 55, True))):
            rows.append(session(id=f'synthetic-day-{n}', trading_date=DAY + timedelta(days=n),
                                open_at=start, close_at=end, required_boundaries=(), execution_margin_ns=0,
                                eligible=eligible, eligibility_reason='explicit synthetic closed date' if not eligible else 'synthetic open date'))
        node = session_union('week', 'weekly-anchor', tuple(rows), source_version='literal-week-v1')
        self.assertEqual(tuple((s.start, s.end) for s in node.spans), tuple(tuple(v) for v in GOLDEN['weekly_segments']))
        self.assertEqual(node.duration_ns, GOLDEN['weekly_duration'])
        self.assertEqual(len(node.trading_dates), 4)
        self.assertFalse(node.contains(45, cut=1))
        with self.assertRaises(ContractError):
            session_union('week', 'x', (rows[0], rows[0]), source_version='v')

    def test_session_cutoff_and_eligibility_do_not_depend_on_opening_prints(self):
        row = session()
        graph = session_graph(row)
        deadline = next(e for e in graph.events if e.kind == 'flatten_deadline')
        self.assertEqual(deadline.effective_at, GOLDEN['initial_flatten_at'])
        self.assertTrue(graph.query('eligible_entry', 10, cut=1))
        self.assertFalse(graph.query('eligible_entry', deadline.effective_at, cut=1))
        blocked = session_graph(replace(row, eligible=False, eligibility_reason='explicit ineligible fixture'))
        self.assertFalse(blocked.query('eligible_entry', 10, cut=1))
        self.assertTrue(blocked.query('session', 10, cut=1))
        # There is no market-price field or first-print fallback in a calendar node.
        self.assertNotIn('open_price', vars(graph.intervals['session']))
        self.assertEqual(graph.events, session_graph(row).events)

    def test_literal_source_clock_variants_and_all_endpoint_queries(self):
        clocks = [('18:00', '19:01'), ('19:01', '23:04'), ('23:04', '03:00'),
                  ('03:00', '03:44'), ('03:44', '05:20'), ('05:20', '06:39'), ('06:39', '09:30'),
                  ('09:55', '10:20'), ('10:20', '11:10'), ('11:10', '11:49'),
                  ('12:35', '14:09'), ('14:09', '16:00'),
                  ('18:00', '22:00'), ('22:00', '02:00'), ('02:00', '06:00'),
                  ('06:00', '10:00'), ('10:00', '14:00'), ('14:00', '17:00'),
                  ('20:00', '20:30'), ('00:00', '00:30'), ('03:00', '03:30'), ('06:00', '09:00'),
                  ('09:30', '10:00'), ('10:00', '10:30'), ('12:00', '12:30'), ('15:00', '15:30'),
                  ('18:00', '02:00'), ('19:00', '02:00'), ('20:00', '02:00'),
                  ('00:00', '04:00'), ('01:00', '05:00'), ('02:00', '06:00'),
                  ('06:00', '10:00'), ('07:00', '11:00'), ('08:00', '12:00'), ('23:00', '03:00')]
        nodes = []
        for n, (start, end) in enumerate(clocks):
            rule = wall(str(n), start, end, end_day=DAY + timedelta(days=int(end <= start)))
            node = rule.compile()
            ref = asdict(rule)
            for key in ('start_day', 'end_day'):
                ref[key] = ref[key].isoformat()
            for at in (node.spans[0].start - 1, node.spans[0].start, node.spans[0].end - 1, node.spans[0].end):
                self.assertEqual(node.contains(at, cut=0), wall_contains(ref, at))
            nodes.append(node)
        graph = IntervalGraph('source-clocks', tuple(nodes))
        self.assertFalse(graph.query('6', local_timestamp(DAY, time(9, 40), 'America/New_York'), cut=0))
        self.assertFalse(graph.query('7', local_timestamp(DAY, time(9, 40), 'America/New_York'), cut=0))
        self.assertEqual(nodes[17].duration_ns, GOLDEN['three_hour_block_minutes'] * MINUTE)
        self.assertEqual(nodes[-1].duration_ns, GOLDEN['magic_23_to_03_hours'] * 3600 * NS)

    def test_boundary_order_empty_intersections_and_duplicate_reset_owners(self):
        nodes = (interval('old', ((0, 10),)), interval('new', ((10, 20),)))
        boundaries = (BoundaryRule('start', 'a', 'formation_start', 'new', 'start', 0, 'v'),
                      BoundaryRule('reset', 'a', 'reset', 'old', 'end', 0, 'v'),
                      BoundaryRule('publish', 'a', 'publication', 'old', 'end', 0, 'v'),
                      BoundaryRule('close', 'a', 'formation_close', 'old', 'end', 0, 'v'))
        graph = IntervalGraph('s', nodes, boundaries=boundaries)
        self.assertEqual([e.kind for e in graph.events], ['formation_close', 'publication', 'reset', 'formation_start'])
        with self.assertRaises(ContractError):
            IntervalGraph('s', nodes, boundaries=(boundaries[0], boundaries[0]))
        empty = interval('empty', ())
        empty_rule = BoundaryRule('reset', 'a', 'reset', 'empty', 'end', 0, 'v')
        self.assertEqual(IntervalGraph('s', (empty,), boundaries=(empty_rule,)).events, ())
        with self.assertRaises(ContractError):
            IntervalGraph('s', (empty,), boundaries=(empty_rule, empty_rule))
        with self.assertRaises(ContractError):
            IntervalGraph('s', nodes, intersections=(Intersection('x', 'o', ('old', 'missing'), 'v', 0),))

    def test_graph_intervals_and_source_dependencies_are_immutable(self):
        node = interval()
        graph = IntervalGraph('s', (node,))
        with self.assertRaises((AttributeError, FrozenInstanceError)):
            graph._known_at = 99
        with self.assertRaises(TypeError):
            graph.intervals['a'] = interval('b')
        with self.assertRaises(FrozenInstanceError):
            node.known_at = 99
        with self.assertRaises(ContractError):
            replace(node, spans=[Span(0, 10)])
        with self.assertRaises(ContractError):
            replace(node, trading_dates=(datetime(2026, 7, 1),))
        with self.assertRaises(ContractError):
            CalendarEvent('s', 'r', 'a', 'reset', 10, 0, ['mutable'])
        restored = IntervalGraph.from_record(json.loads(json.dumps(graph.record())))
        self.assertEqual(restored.version, graph.version)
        for at in (0, 9, 10, 19, 20, 29, 30):
            self.assertEqual(restored.query('a', at, cut=0), graph.query('a', at, cut=0))
        detached = graph.record()
        detached['definition']['intervals'][0]['known_at'] = 99
        with self.assertRaises(IntegrityError):
            IntervalGraph.from_record(detached)
        self.assertEqual(graph.known_at, 0)
        self.assertEqual(code_manifest(ROOT)['references/calendar_literal.py'], file_digest(ROOT / 'references/calendar_literal.py'))

    def test_invalid_public_clock_types_and_unknown_timezone_bytes_fail(self):
        for day, at, zone, fold in ((datetime(2026, 7, 1), time(9), 'America/New_York', None),
                                     (DAY, time(9), 'America/New_York', True),
                                     (DAY, time(9), 'missing/not-a-zone', None)):
            with self.assertRaises(ContractError):
                local_timestamp(day, at, zone, fold=fold)
        for kw in ({'start_fold': True}, {'start_wall': '09:00+05:00'}, {'known_at': 1.0}):
            with self.assertRaises(ContractError):
                replace(wall(), **kw).compile()
        with self.assertRaises(DependencyUnavailable):
            replace(wall(), timezone_version='unavailable-zone-bytes').compile()
        for kwargs in ({'known_at': True}, {'kind': []}, {'details': [('x', 'mutable')]}):
            fields = dict(scope='s', key='r', owner='o', kind='reset', effective_at=10, known_at=0, source_versions=('v',))
            fields.update(kwargs)
            with self.assertRaises(ContractError):
                CalendarEvent(**fields)

    def test_calendar_rows_have_stable_identity_and_frozen_known_time_queries(self):
        calendar = Calendar()
        row = session()
        calendar.append(row)
        revised = replace(row, required_boundaries=(('platform', 55),), known_at=20, source_version='new-cutoff-v2')
        calendar.append(revised)
        calendar.append(revised)
        self.assertEqual(calendar.resolve(DAY, 'NQ', cut=19).flatten_at, GOLDEN['initial_flatten_at'])
        self.assertEqual(calendar.resolve(DAY, 'NQ', cut=20).flatten_at, GOLDEN['revised_flatten_at'])
        with self.assertRaises(ContractError):
            calendar.append(replace(row, id='a-different-logical-session'))
        with self.assertRaises(ContractError):
            calendar.append(replace(row, trading_date=DAY + timedelta(days=1)))
        for kwargs in ({'required_boundaries': [('firm', 80)]}, {'eligible': 'yes'},
                       {'trading_date': '2026-07-01'}, {'eligibility_reason': 3},
                       {'required_boundaries': (('firm', 80), ('firm', 90))}):
            with self.assertRaises(ContractError):
                replace(row, **kwargs)
        with self.assertRaises(ContractError):
            calendar.resolve(DAY, 'NQ', cut=True)
        with self.assertRaises(ContractError):
            FormationWindow('x', 'not-a-date', 0, 10, 'z', 'v')


class CashCalendarContractTests(unittest.TestCase):
    def test_public_cash_source_views_cannot_mutate_frozen_versions(self):
        calendar = CashCalendar(ROOT / 'configs/cash-rth-calendar.json')
        day = date(2024, 11, 29)
        cut = local_timestamp(day, time(0), 'America/New_York')
        before, version = calendar.resolve(day, cut=cut), calendar.version
        exposed = calendar.payload
        exposed['regular_open'] = '00:00'
        for _, release in calendar.releases:
            release['years'].clear()
        for _, override in calendar.overrides:
            override['date'] = '2024-11-29'
        self.assertEqual(calendar.resolve(day, cut=cut), before)
        self.assertEqual(calendar.version, version)
        with self.assertRaises(AttributeError):
            calendar.version = 'invented-version'

    def test_cash_and_venue_clocks_reject_invalid_types_and_margins(self):
        calendar = CashCalendar(ROOT / 'configs/cash-rth-calendar.json')
        day = date(2024, 11, 29)
        cut = local_timestamp(day, time(0), 'America/New_York')
        row = calendar.resolve(day, cut=cut)
        boundary = VenueBoundary(day, 'NQ', row.open_at, row.close_at, row.close_at, row.known_at,
                                 'synthetic-venue-v1', 'synthetic_research_window')
        for kw in ({'known_at': True}, {'valid_start': 1.2}, {'day': '2024-11-29'}, {'source_version': []}):
            with self.assertRaises(ContractError):
                replace(boundary, **kw)
        for buffer in (True, 0, 1.5, -(2 ** 63)):
            with self.assertRaises(ContractError):
                e0_window(row, boundary=boundary, cut=cut, safety_buffer_ns=buffer, require_verified_venue=False)
        with self.assertRaises(ContractError):
            e0_window(row, boundary=boundary, cut=True, safety_buffer_ns=MINUTE, require_verified_venue=False)
        with self.assertRaises(ContractError):
            replace(row, state='closed')
        with self.assertRaises(ContractError):
            replace(row, source_versions=['mutable'])
        with self.assertRaises(ContractError):
            calendar.resolve(datetime(2024, 11, 29), cut=cut)
        with self.assertRaises(ContractError):
            calendar.quarter_dates(2024, True)

    def test_malformed_published_cash_rows_fail_at_ingestion(self):
        payload = json.loads((ROOT / 'configs/cash-rth-calendar.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'calendar.json'
            for mutate in (lambda p: p.update(regular_open='09:30+00:00'),
                           lambda p: p['releases'][0]['years'].update({'2024': {'closed': ['99-01'], 'early': {}}}),
                           lambda p: p['overrides'].append({'published_date': '2024-12-30', 'date': '2025-01-09', 'state': 'open'})):
                value = json.loads(json.dumps(payload))
                mutate(value)
                path.write_text(json.dumps(value))
                with self.assertRaises(ContractError):
                    CashCalendar(path)
            path.write_text('{"schema":"first", "schema":"second"}')
            with self.assertRaises(ContractError):
                CashCalendar(path)
