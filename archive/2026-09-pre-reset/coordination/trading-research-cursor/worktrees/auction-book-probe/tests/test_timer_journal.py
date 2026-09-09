from dataclasses import replace
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.intervals import CalendarEvent, IntervalGraph, NamedInterval, Span
from trading_research.foundations.timer_journal import TimerJournal
from datetime import date

GOLDEN = json.loads((Path(__file__).resolve().parents[1] / 'tests/golden/f03-intervals.json').read_text())


def event(at=80, known=1, *, key='reset', owner='range', kind='reset', source='v1'):
    return CalendarEvent('calendar-scope', key, owner, kind, at, known, (source,))


def graph(*events):
    return IntervalGraph('calendar-scope', (), points=tuple(events))


def count(state, e):
    return {**state, e.kind: state.get(e.kind, 0) + 1,
            'order': state.get('order', []) + [e.kind]}


class TimerJournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'timers.sqlite'

    def tearDown(self):
        self.temp.cleanup()

    def test_no_market_tick_is_needed_and_boundary_order_is_deterministic(self):
        points = [event(10, key=kind, kind=kind) for kind in
                  ('formation_start', 'reset', 'publication', 'formation_close')]
        with TimerJournal(self.path) as journal:
            journal.install(graph(*points), at=1)
            self.assertEqual(journal.next_due(), 10)
            self.assertEqual(journal.process_due(9, count), ())
            applied = journal.process_due(10, count)
            self.assertEqual(len(applied), 4)
            self.assertEqual(journal.state('range')['order'], ['formation_close', 'publication', 'reset', 'formation_start'])
            self.assertIsNone(journal.next_due())
            self.assertEqual(journal.process_due(11, count), ())
            self.assertTrue(all(a['applied_at'] == a['due_at'] == 10 for a in applied))

    def test_reducer_failure_rolls_back_state_application_and_clock_together(self):
        with TimerJournal(self.path) as journal:
            journal.install(graph(event(10, key='first'), event(20, key='second')), at=1)
            def fail(state, e):
                if e.key == 'second':
                    raise RuntimeError('fixed failure before transaction commit')
                return count(state, e)
            with self.assertRaises(RuntimeError):
                journal.process_due(20, fail)
            self.assertEqual(journal.state('range'), {})
            self.assertEqual(journal.applications(), ())
            self.assertEqual(journal.next_due(), 10)
            self.assertEqual(len(journal.process_due(10, count)), 1)
            self.assertEqual(len(journal.process_due(20, count)), 1)
            self.assertEqual(journal.state('range')['reset'], 2)

    def test_abrupt_process_exit_before_and_after_commit_is_restart_safe(self):
        script = '''
import os, sys
from trading_research.foundations.intervals import CalendarEvent, IntervalGraph
from trading_research.foundations.timer_journal import TimerJournal
journal = TimerJournal(sys.argv[1])
ev = CalendarEvent('calendar-scope', 'reset', 'range', 'reset', 10, 1, ('v1',))
journal.install(IntervalGraph('calendar-scope', (), points=(ev,)), at=1)
def reducer(state, e):
    if sys.argv[2] == 'before':
        os._exit(71)
    return {'reset': state.get('reset', 0) + 1}
journal.process_due(10, reducer)
os._exit(72)
'''
        for where, code in (('before', 71), ('after', 72)):
            path = self.path.with_name(where + '.sqlite')
            result = subprocess.run([sys.executable, '-c', script, str(path), where],
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, code, result.stderr)
            with TimerJournal(path) as journal:
                self.assertEqual(journal.state('range').get('reset', 0), int(where == 'after'))
                journal.process_due(10, count)
                self.assertEqual(journal.state('range')['reset'], GOLDEN['applications_per_logical_action'])
                self.assertEqual(len(journal.applications()), 1)
                self.assertEqual(journal.process_due(20, count), ())

    def test_future_calendar_change_replaces_pending_timer_and_keeps_old_history(self):
        old = event(75)
        new = replace(old, effective_at=GOLDEN['revised_flatten_at'], known_at=20, source_versions=('v2',))
        old_graph, new_graph = graph(old), graph(new)
        with TimerJournal(self.path) as journal:
            journal.install(old_graph, at=1)
            self.assertFalse(journal.install(old_graph, at=2))
            journal.install(new_graph, at=20)
            journal.process_due(20, count)
            self.assertEqual(journal.next_due(), 50)
            self.assertEqual(journal.state('range'), {})
            journal.process_due(50, count)
            self.assertEqual(journal.state('range')['reset'], 1)
            self.assertEqual(journal.process_due(75, count), ())
            self.assertTrue(any(v['event_id'] == old.event_id and v['status'] == 'superseded' for v in journal.history()))
            self.assertEqual(journal.plans()[0]['payload']['events'][0]['effective_at'], 75)
        self.assertEqual(old_graph.events[0].effective_at, 75)

    def test_past_revision_reconciles_at_installation_without_retroactive_reset(self):
        old = event(80)
        new = replace(old, effective_at=GOLDEN['past_revision_effective_at'],
                      known_at=GOLDEN['past_revision_installed_at'], source_versions=('past-correction',))
        with TimerJournal(self.path) as journal:
            journal.install(graph(old), at=1)
            journal.install(graph(new), at=60)
            journal.process_due(60, count)
            self.assertEqual(journal.state('range').get('reset', 0), 0)
            self.assertEqual(journal.state('range')['reconcile'], 1)
            row = next(a for a in journal.applications() if a['payload']['kind'] == 'reconcile')
            self.assertEqual(row['payload']['effective_at'], 60)
            self.assertEqual(dict(row['payload']['details'])['effective_at'], '40')
            self.assertEqual(row['applied_at'], 60)
            self.assertEqual(journal.process_due(80, count), ())

    def test_calendar_revision_never_repeats_an_already_committed_logical_reset(self):
        old = event(40)
        new = replace(old, effective_at=80, known_at=60, source_versions=('later-cutoff',))
        with TimerJournal(self.path) as journal:
            journal.install(graph(old), at=1)
            journal.process_due(40, count)
        with TimerJournal(self.path) as journal:
            journal.install(graph(new), at=60)
            journal.process_due(60, count)
            journal.process_due(80, count)
            self.assertEqual(journal.state('range')['reset'], 1)
            self.assertEqual(journal.state('range')['reconcile'], 1)
            self.assertEqual(sum(a['logical_id'] == old.logical_id for a in journal.applications()), 1)
        # A missed old deadline cannot be silently rescued by moving it later.
        with TimerJournal(self.path.with_name('overdue.sqlite')) as journal:
            journal.install(graph(old), at=1)
            journal.install(graph(new), at=60)
            journal.process_due(60, count)
            self.assertEqual(journal.state('range')['reconcile'], 1)
            self.assertEqual(journal.state('range').get('reset', 0), 0)
            self.assertEqual(journal.process_due(80, count), ())

    def test_removed_unapplied_action_can_be_explicitly_reintroduced(self):
        reset = event(100)
        marker = event(500, 20, key='holiday-notice', owner='calendar', kind='holiday', source='calendar-v2')
        with TimerJournal(self.path) as journal:
            journal.install(graph(reset), at=1)
            journal.install(graph(marker), at=20)
            journal.process_due(20, count)
            marker3 = replace(marker, known_at=30, source_versions=('calendar-v3',))
            journal.install(graph(reset, marker3), at=30)
            journal.process_due(30, count)
            journal.process_due(100, count)
            self.assertEqual(journal.state('range')['reset'], 1)
            self.assertEqual(sum(v['event_id'] == reset.event_id and v['status'] == 'pending' for v in journal.history()), 2)

    def test_separate_owners_share_clock_but_not_state_or_logical_identity(self):
        a, b = event(10, owner='profile'), event(10, owner='formation')
        self.assertNotEqual(a.logical_id, b.logical_id)
        with TimerJournal(self.path) as journal:
            journal.install(graph(a, b), at=1)
            self.assertEqual(len(journal.process_due(10, count, limit=1)), 1)
            self.assertEqual(journal.next_due(), 10)
            self.assertEqual(len(journal.process_due(10, count, limit=1)), 1)
            for owner in ('profile', 'formation'):
                self.assertEqual(journal.state(owner)['reset'], 1)
            state = journal.state('profile')
            state['reset'] = 100
            self.assertEqual(journal.state('profile')['reset'], 1)

    def test_initial_late_install_catches_up_at_available_cut_and_duplicate_is_inert(self):
        point = event(10, 20)
        node = NamedInterval('formation', 'range', (Span(0, 10),), 20, 'late-calendar',
                             'synthetic-ns', 'test-zone', (date(2026, 7, 1),))
        plan = IntervalGraph('calendar-scope', (node,), points=(point,))
        with TimerJournal(self.path) as journal:
            with self.assertRaises(DependencyUnavailable):
                journal.install(plan, at=19)
            journal.install(plan, at=30)
            journal.process_due(30, count)
            row = journal.applications()[0]
            self.assertEqual((row['payload']['effective_at'], row['payload']['known_at'], row['due_at'], row['applied_at']),
                             (10, 20, 30, 30))
            self.assertFalse(journal.install(plan, at=31))
            self.assertEqual(journal.process_due(31, count), ())
        with TimerJournal(self.path) as journal:
            restored = IntervalGraph.from_record(journal.plans()[0]['payload']['graph'])
            self.assertTrue(restored.query('formation', 9, cut=20))
            self.assertFalse(restored.query('formation', 10, cut=20))
            self.assertEqual(restored.version, plan.version)

    def test_conflicting_versions_clock_rewind_and_invalid_state_fail_atomically(self):
        base = graph(event(80))
        with TimerJournal(self.path) as journal:
            journal.install(base, at=10)
            with self.assertRaises(ContractError):
                journal.install(graph(event(70, source='same-time-conflict')), at=11)
            with self.assertRaises(ContractError):
                journal.process_due(9, count)
            for reducer in (lambda s, e: {'bad': float('nan')}, lambda s, e: {'bad': object()}, lambda s, e: []):
                with self.assertRaises(ContractError):
                    journal.process_due(80, reducer)
            self.assertEqual(journal.state('range'), {})
            self.assertEqual(journal.applications(), ())
            with self.assertRaises(ContractError):
                journal.process_due(80, count, limit=True)
            with self.assertRaises(ContractError):
                journal.process_due(80, count, limit=2 ** 63)
            self.assertEqual(len(journal.process_due(80, count)), 1)
        unrelated = self.path.with_name('unrelated.sqlite')
        with sqlite3.connect(unrelated) as db:
            db.execute('CREATE TABLE unrelated (value INTEGER)')
            db.execute('INSERT INTO unrelated VALUES (7)')
        with self.assertRaises(IntegrityError):
            TimerJournal(unrelated)
        with sqlite3.connect(unrelated) as db:
            self.assertEqual(db.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall(), [('unrelated',)])
            self.assertEqual(db.execute('SELECT value FROM unrelated').fetchone()[0], 7)
