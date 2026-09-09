"""Frozen F04 scheduler assertions; toy arithmetic is not a forecasting trial."""
from collections import Counter
from dataclasses import FrozenInstanceError, replace
import json
from pathlib import Path
import resource
from threading import Event, RLock
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from references.replay_literal import full_recompute
from trading_research.errors import ContractError
from trading_research.foundations.graph import Graph, InputPort, Port
from trading_research.runtime.reactor import OptionalWorkers, WorkerBudget
from trading_research.runtime.scheduling import CostSample, DirtyPlanner, FieldChange, QueuePolicy, RuntimeCosts

GOLDEN = json.loads((Path(__file__).parent / 'golden/f04-replay.json').read_text())


def toy_graph():
    return Graph([
        Port('trade', 'F01', 0, 'trade.v1', frozenset({'buy', 'sell', 'price'}), lane='market'),
        Port('oi', 'C01', 0, 'oi.v1', frozenset({'contracts', 'multiplier'})),
        Port('account', 'R01', 0, 'account.v1', frozenset({'position'}), lane='account'),
        Port('timer', 'F04', 0, 'timer.v1', frozenset({'due'}), lane='timer'),
        Port('cvd', 'F02', 1, 'cvd.v1', frozenset({'value'}),
             (InputPort('trade', 'trade.v1', frozenset({'buy', 'sell'})),)),
        Port('exposure', 'C02', 1, 'exposure.v1', frozenset({'value'}),
             (InputPort('oi', 'oi.v1', frozenset({'contracts', 'multiplier'})),)),
        Port('decision', 'P01', 2, 'decision.v1', frozenset({'value'}),
             (InputPort('cvd', 'cvd.v1', frozenset({'value'})),
              InputPort('exposure', 'exposure.v1', frozenset({'value'}), optional=True))),
    ])


def job(id, producer=None, *, submitted_at=10, deadline=100, horizon=None, cut=10):
    return SimpleNamespace(id=id, producer=producer or id, submitted_at=submitted_at,
                           expires_at=deadline, horizon_end=horizon, cut=cut)


def measured_kernels(operations):
    # Count the arithmetic performed inside each invoked operation. Both paths
    # receive the same definitions; the independent literal reference selects all.
    def cvd(inputs):
        operations['subtract'] += 1
        row = inputs['trade']
        return {'value': row['buy'] - row['sell'], 'lineage': (row['lineage'],)}

    def exposure(inputs):
        operations['multiply'] += 1
        row = inputs['oi']
        return {'value': row['contracts'] * row['multiplier'], 'lineage': (row['lineage'],)}

    def decision(inputs):
        operations['add'] += 1
        cvd_row = inputs['cvd']
        exposure_row = inputs.get('exposure', {'value': 0, 'lineage': ()})
        return {'value': cvd_row['value'] + exposure_row['value'],
                'lineage': cvd_row['lineage'] + exposure_row['lineage'],
                'omitted_exposure': 'exposure' not in inputs}

    return {'cvd': cvd, 'exposure': exposure, 'decision': decision}


class DirtySchedulingTests(unittest.TestCase):
    def setUp(self):
        self.graph = toy_graph()
        self.planner = DirtyPlanner(self.graph)

    def test_oi_trade_and_unused_field_propagate_to_exact_descendants(self):
        oi = self.planner.plan({'oi': FieldChange(frozenset({'contracts'}))})
        trade = self.planner.plan({'trade': FieldChange(frozenset({'buy'}))})
        self.assertEqual(list(oi.optional), GOLDEN['dirty']['oi'])
        self.assertEqual(list(trade.optional), GOLDEN['dirty']['trade'])
        self.assertEqual(self.planner.plan({'trade': FieldChange(frozenset({'price'}))}).optional, ())
        self.assertEqual(oi.graph_version, self.graph.version)

    def test_same_value_new_source_lineage_recomputes_dependent_forecast(self):
        self.assertEqual(self.planner.plan({'oi': FieldChange(frozenset())}).optional, ())
        result = self.planner.plan({'oi': FieldChange(frozenset(), lineage_changed=True)})
        self.assertEqual(list(result.optional), GOLDEN['dirty']['oi'])
        operations = Counter()
        kernels = measured_kernels(operations)
        a = kernels['exposure']({'oi': {'contracts': 7, 'multiplier': 2, 'lineage': 'row:a'}})
        b = kernels['exposure']({'oi': {'contracts': 7, 'multiplier': 2, 'lineage': 'row:b'}})
        self.assertEqual(a['value'], b['value'])
        self.assertNotEqual(a['lineage'], b['lineage'])

    def test_missing_mandatory_exposure_allows_optional_decision_and_independent_cvd(self):
        outage = self.planner.plan({}, unavailable=frozenset({'oi'}))
        self.assertEqual(outage.optional, ('decision',))
        self.assertEqual(outage.blocked, frozenset({'oi', *GOLDEN['dirty']['unavailable_oi']}))
        trade = self.planner.plan({'trade': FieldChange(frozenset({'sell'}))}, unavailable=frozenset({'oi'}))
        self.assertEqual(trade.optional, ('cvd', 'decision'))
        missing_trade = self.planner.plan({}, unavailable=frozenset({'trade'}))
        self.assertEqual(missing_trade.blocked, frozenset({'trade', 'cvd', 'decision'}))
        self.assertNotIn('exposure', missing_trade.blocked)

    def test_integrity_lanes_are_unconditional_in_both_planning_modes(self):
        for mode in ('incremental', 'full'):
            for unavailable in (frozenset(), frozenset({'oi', 'trade'})):
                with self.subTest(mode=mode, unavailable=unavailable):
                    result = self.planner.plan({}, mode=mode, unavailable=unavailable)
                    self.assertEqual(set(result.unconditional), {'trade', 'account', 'timer'})
                    self.assertFalse(set(result.unconditional).intersection(result.optional))
        self.assertEqual(self.planner.plan({}, mode='full').optional, ('exposure', 'cvd', 'decision'))

    def test_field_and_policy_contracts_reject_mutability_and_invalid_values(self):
        for fields, lineage in (({'buy'}, False), (frozenset({''}), False), (frozenset({1}), False), (frozenset(), 1)):
            with self.subTest(fields=fields, lineage=lineage), self.assertRaises(ContractError):
                FieldChange(fields, lineage)
        for changes, kwargs in (({'absent': FieldChange(frozenset())}, {}),
                                ({'trade': FieldChange(frozenset({'unknown'}))}, {}),
                                ({'trade': {'buy'}}, {}), ({}, {'unavailable': {'oi'}}),
                                ({}, {'unavailable': frozenset({'absent'})}), ({}, {'mode': 'mystery'})):
            with self.subTest(changes=changes, kwargs=kwargs), self.assertRaises(ContractError):
                self.planner.plan(changes, **kwargs)
        with self.assertRaises(FrozenInstanceError):
            FieldChange(frozenset()).lineage_changed = True
        with self.assertRaises(FrozenInstanceError):
            self.planner.plan({}).optional = ('cvd',)
        for kwargs in ({'name': 'magic'}, {'priorities': [('cvd', 1)]},
                       {'priorities': (('cvd', True),)}, {'priorities': (('cvd', 1), ('cvd', 2))},
                       {'fallback_cost_ns': 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ContractError):
                QueuePolicy(**kwargs)

    def test_full_and_incremental_compare_every_output_lineage_and_operation_at_identical_cuts(self):
        trade = {'buy': 9, 'sell': 4, 'price': 100, 'lineage': 'trade:10'}
        oi = {'contracts': 3, 'multiplier': 2, 'lineage': 'oi:10'}
        # Frozen, finite sequence: initial, OI, trade, same-value new evidence,
        # no change, outage, recovery. Every oracle call starts from raw inputs.
        cuts = [
            (10, trade, oi, {'trade': FieldChange(frozenset({'buy', 'sell'})), 'oi': FieldChange(frozenset({'contracts'}))}, 3),
            (20, trade, dict(oi, contracts=5, lineage='oi:20'), {'oi': FieldChange(frozenset({'contracts'}))}, 2),
            (30, dict(trade, sell=6, lineage='trade:30'), dict(oi, contracts=5, lineage='oi:20'), {'trade': FieldChange(frozenset({'sell'}))}, 2),
            (40, dict(trade, sell=6, lineage='trade:30'), dict(oi, contracts=5, lineage='oi:40'), {'oi': FieldChange(frozenset(), True)}, 2),
            (50, dict(trade, sell=6, lineage='trade:30'), dict(oi, contracts=5, lineage='oi:40'), {}, 0),
            (60, dict(trade, sell=6, lineage='trade:30'), None, {}, 1),
            (70, dict(trade, sell=6, lineage='trade:30'), dict(oi, contracts=8, lineage='oi:70'), {'oi': FieldChange(frozenset(), True)}, 2),
        ]
        incremental, full_ops, incremental_ops = {}, Counter(), Counter()
        full_kernels, incremental_kernels = measured_kernels(full_ops), measured_kernels(incremental_ops)
        rows = []
        for cut, trade_row, oi_row, changes, expected_calls in cuts:
            roots = {'trade': dict(trade_row), 'account': {'position': 0}, 'timer': {'due': 100}}
            if oi_row is not None:
                roots['oi'] = dict(oi_row)
            unavailable = frozenset({'oi'}) if oi_row is None else frozenset()
            plan = self.planner.plan(changes, unavailable=unavailable)
            expected, full_calls = full_recompute(self.graph, roots, full_kernels)
            for key in plan.blocked:
                incremental.pop(key, None)
            incremental.update(roots)
            before = incremental_ops.total()
            for key in plan.optional:
                inputs = {edge.source: incremental[edge.source] for edge in self.graph.ports[key].inputs
                          if edge.source in incremental}
                incremental[key] = incremental_kernels[key](inputs)
            with self.subTest(cut=cut):
                self.assertEqual(incremental, expected)
                self.assertEqual(incremental_ops.total() - before, expected_calls)
                self.assertEqual(len(full_calls), 2 if oi_row is None else 3)
            rows.append({'cut': cut, 'incremental_operations': incremental_ops.total() - before,
                         'full_operations': len(full_calls), 'outputs': expected})
        self.assertEqual(full_ops, Counter(subtract=7, multiply=6, add=7))
        self.assertEqual(incremental_ops, Counter(subtract=2, multiply=4, add=6))
        print('F04_TOY_COMPARISON ' + json.dumps({'cuts': rows, 'full_operations': dict(full_ops),
                                               'incremental_operations': dict(incremental_ops)}, sort_keys=True))


class QueueSchedulingTests(unittest.TestCase):
    def test_fifo_deadline_and_cost_policies_have_explicit_priority_and_endpoint_order(self):
        costs = RuntimeCosts()
        costs.add(CostSample('slow:1', 'slow', 1, 9, 1))
        costs.add(CostSample('fast:1', 'fast', 2, 2, 1))
        pair = [job('slow'), job('fast')]
        for name, expected in (('fifo', GOLDEN['queue']['fifo']), ('deadline', 'slow'),
                               ('deadline_cost', GOLDEN['queue']['deadline_cost'])):
            policy = QueuePolicy(name, (('slow', 3), ('fast', 3)))
            index, record = policy.select(pair, at=10, costs=costs)
            self.assertEqual(pair[index].id, expected)
            self.assertEqual((record['policy'], record['policy_version'], record['at']), (name, policy.version, 10))
            self.assertEqual([r['estimated_wall_ns'] for r in record['candidates']], [9, 2])
        pair = [job('slow', deadline=100, horizon=20), job('fast', deadline=30)]
        priorities = (('slow', 1), ('fast', 2))
        self.assertEqual(QueuePolicy('deadline', priorities).select(pair, at=10, costs=costs)[0], 0)
        self.assertEqual(QueuePolicy('deadline_cost', priorities).select(pair, at=10, costs=costs)[0], 1)
        with self.assertRaises(ContractError):
            QueuePolicy().select([job('future', submitted_at=11)], at=10, costs=costs)
        with self.assertRaises(ContractError):
            QueuePolicy().select([], at=10, costs=costs)

    def test_future_cost_is_excluded_and_censored_evidence_uses_registered_fallback(self):
        costs = RuntimeCosts(producer_window=2)
        costs.add(CostSample('one', 'fast', 1, 2, 1))
        costs.add(CostSample('failed', 'fast', 2, 999, 3, True))
        costs.add(CostSample('future', 'fast', 20, 1, 1))
        self.assertEqual(costs.estimate('fast', at=10, fallback_ns=50), GOLDEN['queue']['future_sample_ignored'])
        self.assertEqual(costs.summary('fast', at=10), {'completed': 1, 'censored': 1, 'p95_wall_ns': 2,
                                                       'p99_wall_ns': 2, 'cpu_ns': 4, 'retained_from_exclusive': None})
        failed_only = RuntimeCosts()
        failed_only.add(CostSample('failed-only', 'slow', 1, 100, 7, True))
        index, record = QueuePolicy('deadline_cost', fallback_cost_ns=17).select([job('slow')], at=10, costs=failed_only)
        self.assertEqual((index, record['candidates'][0]['estimated_wall_ns']), (0, 17))
        self.assertEqual(failed_only.summary('slow', at=10)['censored'], 1)
        self.assertEqual(failed_only.summary('slow', at=10)['completed'], 0)

    def test_bounded_history_identity_retention_and_frozen_nearest_rank_percentiles(self):
        costs = RuntimeCosts(max_samples=8)
        for i, duration in enumerate(GOLDEN['percentiles']['samples']):
            costs.add(CostSample(str(i), 'toy', i, duration, 1))
        summary = costs.summary('toy', at=10)
        self.assertEqual((summary['p95_wall_ns'], summary['p99_wall_ns']),
                         (GOLDEN['percentiles']['p95'], GOLDEN['percentiles']['p99']))
        bounded = RuntimeCosts(max_samples=2, producer_window=1)
        first = CostSample('a', 'toy', 1, 4, 1)
        self.assertTrue(bounded.add(first))
        self.assertFalse(bounded.add(first))
        with self.assertRaises(ContractError):
            bounded.add(replace(first, wall_ns=5))
        bounded.add(CostSample('b', 'toy', 2, 6, 1))
        bounded.add(CostSample('c', 'toy', 3, 8, 1, True))
        with self.assertRaises(ContractError):
            bounded.summary('toy', at=1)
        self.assertEqual(bounded.estimate('toy', at=3, fallback_ns=50), 6)
        self.assertEqual(bounded.summary('toy', at=3)['censored'], 1)
        with self.assertRaises(ContractError):
            bounded.add(CostSample('out-of-order', 'toy', 2, 1, 0))
        for args in (('x', 'toy', 1, 0, 0), ('x', 'toy', 1, True, 0), ('x', 'toy', 1, 1, -1)):
            with self.subTest(args=args), self.assertRaises(ContractError):
                CostSample(*args)

    def test_actual_timed_deterministic_work_has_exact_operations_and_unthresholded_telemetry(self):
        costs, rows = RuntimeCosts(), []
        for i, count in enumerate((1000, 2000, 3000, 4000, 5000)):
            submitted = time.time_ns()
            wall_start, cpu_start = time.perf_counter_ns(), time.process_time_ns()
            total, operations = 0, 0
            for value in range(count):
                total += value
                operations += 1
            cpu_ns = time.process_time_ns() - cpu_start
            wall_ns = time.perf_counter_ns() - wall_start
            received = time.time_ns()
            self.assertEqual((total, operations), (count * (count - 1) // 2, count))
            sample = CostSample(f'timed:{i}', 'timed-toy', received, wall_ns, cpu_ns)
            costs.add(sample)
            rows.append({'id': sample.id, 'submitted_at': submitted, 'parent_received_at': received,
                         'wall_ns': wall_ns, 'cpu_ns': cpu_ns, 'operations': operations,
                         'peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024})
        summary = costs.summary('timed-toy', at=rows[-1]['parent_received_at'])
        self.assertEqual(summary['completed'], 5)
        self.assertEqual(summary['p95_wall_ns'], max(r['wall_ns'] for r in rows))
        self.assertEqual(summary['p99_wall_ns'], max(r['wall_ns'] for r in rows))
        print('F04_ACTUAL_TOY_TIMING ' + json.dumps({'samples': rows, 'summary': summary}, sort_keys=True))

    def worker_without_threads(self, policy=QueuePolicy()):
        records, abandoned = [], []
        store = SimpleNamespace(graph=toy_graph(), journal=SimpleNamespace(append=lambda **row: records.append(row)),
                                _validate_request=lambda request: None, is_terminal=lambda id: False,
                                abandon=lambda request, **kwargs: abandoned.append((request.id, kwargs)))
        worker = object.__new__(OptionalWorkers)
        worker.store, worker.queue_policy, worker.costs = store, policy, RuntimeCosts()
        worker._lock, worker._wake, worker._stop = RLock(), Event(), Event()
        worker._pending, worker._running, worker._accepted = [], {}, set()
        worker.max_workers, worker.max_pending, worker.failure = 1, 8, None
        return worker, records, abandoned

    def test_worker_coalescing_is_per_producer_and_invalid_replacement_is_atomic(self):
        worker, records, abandoned = self.worker_without_threads()
        budget = WorkerBudget(100, 1, 1_000_000)
        old, other, new = job('old', 'cvd'), job('other', 'exposure'), job('new', 'cvd', cut=11)
        with patch('trading_research.runtime.reactor.time.time_ns', return_value=20):
            self.assertTrue(worker.submit(old, bytes, budget=budget, coalesce_key='shared'))
            self.assertTrue(worker.submit(other, bytes, budget=budget, coalesce_key='shared'))
            self.assertEqual([r[0].id for r in worker._pending], ['old', 'other'])
            with patch.object(worker.store, '_validate_request', side_effect=ContractError('forged')):
                with self.assertRaises(ContractError):
                    worker.submit(new, bytes, budget=budget, coalesce_key='shared')
            self.assertEqual([r[0].id for r in worker._pending], ['old', 'other'])
            self.assertEqual(abandoned, [])
            self.assertTrue(worker.submit(new, bytes, budget=budget, coalesce_key='shared'))
            self.assertEqual([r[0].id for r in worker._pending], ['other', 'new'])
            self.assertEqual([r[0] for r in abandoned], ['old'])
            for lane in ('trade', 'account', 'timer'):
                with self.subTest(lane=lane), self.assertRaises(ContractError):
                    worker.submit(job('lane:' + lane, lane), bytes, budget=budget)
        self.assertEqual([r['payload']['request_id'] for r in records], ['old', 'other', 'new'])

    def test_worker_poll_applies_registered_cost_policy_and_records_actual_selection(self):
        policy = QueuePolicy('deadline_cost', (('cvd', 1), ('exposure', 1)))
        worker, records, abandoned = self.worker_without_threads(policy)
        worker.costs.add(CostSample('cvd:prior', 'cvd', 1, 9, 1))
        worker.costs.add(CostSample('exposure:prior', 'exposure', 2, 2, 1))
        budget = WorkerBudget(100, 1, 1_000_000)
        worker._pending = [(job('slow', 'cvd'), bytes, budget, None), (job('fast', 'exposure'), bytes, budget, None)]
        started, closed = [], []
        parent = SimpleNamespace(close=lambda: closed.append('parent'))
        child = SimpleNamespace(close=lambda: closed.append('child'))
        def process(**kwargs):
            return SimpleNamespace(start=lambda: started.append(kwargs['args'][2].id))
        worker._context = SimpleNamespace(Pipe=lambda **kwargs: (parent, child), Process=process)
        with patch('trading_research.runtime.reactor.time.time_ns', return_value=20), \
                patch('trading_research.runtime.reactor.time.monotonic_ns', return_value=5):
            worker.poll()
        self.assertEqual(started, ['fast'])
        self.assertEqual(list(worker._running), ['fast'])
        self.assertEqual([item[0].id for item in worker._pending], ['slow'])
        self.assertEqual(abandoned, [])
        self.assertEqual(closed, ['child'])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['kind'], 'optional_schedule_choice')
        self.assertEqual(records[0]['payload']['selected'], 'fast')
        self.assertEqual(records[0]['payload']['policy_version'], policy.version)


if __name__ == '__main__':
    unittest.main()
