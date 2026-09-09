"""Frozen F06/F07 finite source-quality and support comparisons.

These exercise synthetic contract analogues, not the historical market cohorts
or downstream P5/P6/P7 scope preserved in the source-preparation report.
"""
from collections import Counter
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import json
from pathlib import Path
import resource
import time
import unittest
from unittest.mock import patch

from references.quality_join_literal import aggregate_reference, field_reference, snapshot_reference
from trading_research.data.book import BookReducer, RecoveryCertificate
from trading_research.data.events import LatencyScenario, decode_fields, normalize_mbp
from trading_research.errors import ContractError
from trading_research.foundations.graph import Graph, InputPort, Port
from trading_research.foundations.joined import (
    CoverageFieldRole, EligibilityIndex, JointMovementEvidence, JointPolicy, OICoverageContract,
    UniverseMember, joint_snapshot, observed_oi_coverage,
)
from trading_research.foundations.quality import (
    OPERATIONS, FieldFact, FieldKey, FieldRef, ObservedSpan, OperationPolicy, QualityDependencies,
    QualityIncident, QualityRecovery, SourceLiveness, aggregate_support, classify_stream,
    incident_interval, interval_union, plan_repair,
)
from trading_research.foundations.time import AvailabilityBasis, Clocks
from trading_research.operations.artifacts import canonical_json, json_value
from tests.test_market_data import event as raw_event

GOLDEN = {row['id']: row for row in json.loads((Path(__file__).parent / 'golden/f06-f07-quality.json').read_text())['cases']}


def key(field='bid', *, producer='book', instrument='NQH5', definition='definition:v1', unit='ticks',
        asset='NQ', chain=None, expiry=None):
    return FieldKey(producer, field, instrument, definition, unit, asset, chain, expiry)


def fact(id, field, at, value, *, known=None, receipt=None, revision=0, origin=None,
         operations=OPERATIONS, eligible=True, estimated=False, uncertainty=0, source='source:fixture'):
    known = at if known is None else known
    receipt = known if receipt is None else receipt
    clocks = Clocks(at, known, 'source-content:v1', AvailabilityBasis.RECEIVED,
                    received_at=receipt, clock_uncertainty_ns=uncertainty)
    return FieldFact(id, field, source, at, clocks, canonical_json(value), revision,
                     operations, origin, eligible, estimated)


def pulse(id, field, at, *, healthy=True):
    return SourceLiveness(id, 'source:fixture', field.instrument, at, at, healthy, 'heartbeat', 'evidence:' + id)


def incident(id, fields, at, *, start=None, end=None, stage='semantic', kind='corrupt_field',
             severity='dependent-feature-block', operations=OPERATIONS, scope='state', recovery=False):
    return QualityIncident(id, stage, frozenset(fields), at, at if start is None else start,
                           end, kind, severity, operations, 'evidence:' + id, scope, recovery)


def observed_span(id, field, start, end, *, operation='valuation', known=None):
    return ObservedSpan(id, field, operation, start, end, end if known is None else known, 'evidence:' + id)


def toy_coverage_contract():
    # The fixture explicitly defines this single field as a complete synthetic
    # quote; no vendor quote schema or execution capability is inferred.
    return OICoverageContract('synthetic-composite-quote:v1',
                             CoverageFieldRole(FieldRef('options', 'oi'), 'contracts', 'valuation'),
                             (CoverageFieldRole(FieldRef('options', 'quote'), 'ticks', 'valuation'),))


def graph():
    return Graph([
        Port('trade', 'F01', 0, 'trade.v1', frozenset({'buy', 'sell'}), lane='market'),
        Port('oi', 'F01', 0, 'oi.v1', frozenset({'contracts'})),
        Port('account', 'P01', 0, 'account.v1', frozenset({'position'}), lane='account'),
        Port('timer', 'F03', 0, 'timer.v1', frozenset({'due'}), lane='timer'),
        Port('cvd', 'M01', 1, 'cvd.v1', frozenset({'value'}),
             (InputPort('trade', 'trade.v1', frozenset({'buy', 'sell'})),)),
        Port('exposure', 'O09', 1, 'exposure.v1', frozenset({'value'}),
             (InputPort('oi', 'oi.v1', frozenset({'contracts'})),)),
        Port('decision', 'P01', 2, 'decision.v1', frozenset({'value'}),
             (InputPort('cvd', 'cvd.v1', frozenset({'value'})),
              InputPort('exposure', 'exposure.v1', frozenset({'value'}), optional=True))),
    ])


def comparison_fixture():
    spec = GOLDEN['QJ-17']['inputs']
    keys = {'buy': key('buy', producer='trade', unit='contracts'),
            'sell': key('sell', producer='trade', unit='contracts'),
            'oi': key('contracts', producer='oi', unit='contracts')}
    policy = OperationPolicy('comparison', 'forecasting', spec['max_age_ns'])
    bindings = tuple((keys[name], policy) for name in spec['field_order'])
    events = tuple(fact(row['id'], keys[row['field']], row['observed_at'], row['value'], known=row['known_at'])
                   for row in spec['facts'])
    joint = JointPolicy('comparison-joint', spec['max_joint_span_ns'])
    return bindings, events, joint


def arithmetic(snapshot, counts):
    values = [json.loads(field.payload_json) for field in snapshot.fields]
    counts['subtract'] += 1
    net = values[0] - values[1]
    counts['add'] += 1
    return net + values[2]


class QualityJoinTests(unittest.TestCase):
    def test_fresh_equal_and_copied_observations_preserve_four_clocks(self):
        g = GOLDEN['QJ-01']; k = key()
        p = OperationPolicy('freshness', 'valuation', g['inputs']['max_economic_age_ns'],
                            g['inputs']['max_source_silence_ns'])
        rows = tuple(fact(r['id'], k, r['observed_at'], r['value'], known=r['known_at'],
                          receipt=r['receipt_at'], origin=r.get('content_origin_id')) for r in g['inputs']['facts'])
        for health in ('healthy', 'dead'):
            with self.subTest(health=health):
                live = g['inputs'][health + '_liveness']
                events = rows + (pulse(live['id'], k, live['source_observed_at']),)
                index = EligibilityIndex(((k, p),)); index.extend(events)
                support = index.field(k, p.id, cut=g['inputs']['cut'])
                self.assertEqual(support, field_reference(events, k, p, cut=35))
                for name in ('last_value_change_at', 'last_source_observation_at', 'last_local_receipt_at', 'age_ns'):
                    self.assertEqual(getattr(support, name), g['expected'][name])
                self.assertEqual(support.observed_at, g['expected']['economic_observed_at'])
                self.assertEqual(support.origin_id, g['expected']['content_origin_id'])
                for name in ('liveness_at', 'liveness_age_ns', 'state'):
                    self.assertEqual(getattr(support, name), g['expected'][health][name])
                if health == 'dead':
                    self.assertEqual(support.reasons, (g['expected'][health]['reason'],))
                a, b = index.field(k, p.id, cut=10), index.field(k, p.id, cut=20)
                self.assertNotEqual(a.version_vector_entry, b.version_vector_entry)
                self.assertEqual(a.last_value_change_at, b.last_value_change_at)
        # Every malformed QJ-02 origin variant rejects before the proposed state
        # becomes visible, even though the copy has a later local receipt.
        ask = key('ask'); bindings = ((k, p), (ask, p))
        base = fact('a', k, 10, 100)
        bad = [fact('copy', k, 10, 100, known=30, origin='missing'),
               fact('copy', k, 10, 101, known=30, origin='a'),
               fact('copy', ask, 10, 100, known=30, origin='a'),
               fact('copy', k, 20, 100, known=30, origin='a'),
               replace(base, payload_json=b'101')]
        for invalid in bad:
            index = EligibilityIndex(bindings); index.append(base); before = index.checkpoint()
            with self.subTest(invalid=invalid.id, origin=invalid.content_origin_id), self.assertRaises(ContractError):
                index.append(invalid)
            self.assertEqual(index.checkpoint(), before)
        index = EligibilityIndex(bindings); index.append(fact('late-origin', k, 10, 100, known=30))
        before = index.checkpoint()
        with self.assertRaises(ContractError):
            index.append(fact('early-copy', k, 10, 100, known=20, origin='late-origin'))
        self.assertEqual(index.checkpoint(), before)

    def test_operation_policies_have_separate_age_capability_and_uncertainty(self):
        g = GOLDEN['QJ-03']; k = key('quote')
        policies = tuple(OperationPolicy(name, name, age, 5) for name, age in g['inputs']['operation_max_age_ns'].items())
        events = (fact('q', k, 10, 100, operations=frozenset(g['inputs']['source_available_operations'])), pulse('live', k, 20))
        index = EligibilityIndex(tuple((k, p) for p in policies)); index.extend(events)
        for policy in policies:
            with self.subTest(operation=policy.operation):
                result = index.field(k, policy.id, cut=20)
                self.assertEqual(result, field_reference(events, k, policy, cut=20))
                self.assertEqual(result.state, g['expected'][policy.operation])
                self.assertEqual(result.age_ns, g['expected']['age_ns'])
                if policy.operation == 'execution':
                    self.assertEqual(result.reasons, (g['expected']['execution_reason'],))
        g = GOLDEN['QJ-18']
        p = OperationPolicy('uncertain', 'valuation', 10, max_clock_uncertainty_ns=2)
        event = fact('uncertain', k, 10, 100, known=12, uncertainty=2)
        index = EligibilityIndex(((k, p),)); index.append(event)
        result = index.field(k, p.id, cut=20)
        self.assertEqual((result.age_lower_ns, result.age_upper_ns), (g['expected']['age_lower_ns'], g['expected']['age_upper_ns']))
        self.assertEqual((result.state, result.reasons), ('stale', (g['expected']['reason'],)))
        self.assertEqual(result.cut, 20)
        self.assertEqual(result, field_reference((event,), k, p, cut=20))
        strict = replace(p, id='strict', max_clock_uncertainty_ns=1)
        index = EligibilityIndex(((k, strict),)); index.append(event)
        self.assertEqual(index.field(k, strict.id, cut=12).reasons, ('clock_uncertainty_exceeded',))

    def test_raw_semantic_incidents_propagate_fields_and_optional_omissions(self):
        g = GOLDEN['QJ-04']; k = key('contracts', producer='oi', unit='contracts')
        bad = incident('bad-oi', (k,), 10, end=20, stage='raw', operations=frozenset({'valuation', 'forecasting'}))
        compiled = graph(); result = QualityDependencies(compiled).propagate(bad, cut=15, operation='forecasting')
        self.assertEqual({r.producer + '.' + r.field for r in result.blocked}, set(g['expected']['blocked_fields']))
        self.assertEqual(list(result.dirty_consumers), g['expected']['dirty_consumers'])
        self.assertEqual([r.producer + '.' + r.field for consumer, r in result.optional_omissions if consumer == 'decision'],
                         g['expected']['decision_optional_omissions'])
        self.assertEqual({compiled.ports[p].lane for p in result.unconditional}, set(g['expected']['unconditional_lanes']))
        self.assertEqual(list(result.affected_interval), g['expected']['blocked_interval'])
        self.assertFalse(QualityDependencies(compiled).propagate(bad, cut=9, operation='forecasting').blocked)
        self.assertFalse(QualityDependencies(compiled).propagate(bad, cut=20, operation='forecasting').blocked)
        self.assertFalse(QualityDependencies(compiled).propagate(bad, cut=15, operation='execution').blocked)
        # A raw quality port cannot depend on a later normalized port.
        with self.assertRaises(ContractError):
            Graph([Port('raw_quality', 'F06', 1, 'q.v1', frozenset({'q'}),
                        (InputPort('normalized', 'n.v1', frozenset({'n'})),)),
                   Port('normalized', 'F05', 2, 'n.v1', frozenset({'n'}))])
        q = key('quote'); p = OperationPolicy('execution', 'execution', 100)
        hard = incident('hard', (q,), 10, kind='crossed_continuous_quote', severity='execution-block')
        advisory = incident('advisory', (q,), 10, kind='anomaly_score_zero', severity='informational')
        events = (fact('q', q, 10, 100), hard, advisory)
        index = EligibilityIndex(((q, p),)); index.extend(events)
        result = index.field(q, p.id, cut=10)
        self.assertEqual(result.state, GOLDEN['QJ-05']['expected']['execution_state'])
        self.assertEqual(result.incident_ids, ('advisory', 'hard'))
        self.assertIn('crossed_continuous_quote', result.reasons)
        self.assertEqual(result, field_reference(events, q, p, cut=10))

    def test_book_recovery_preserves_history_gap_and_snapshot_age(self):
        g = GOLDEN['QJ-06']; book, flow = key(), key('volume', producer='flow', unit='contracts')
        p = OperationPolicy('quality', 'execution', 100)
        book_gap = incident('book-gap', (book,), 10, kind='book_gap', recovery=True)
        flow_gap = incident('flow-gap', (flow,), 10, kind='flow_gap', scope='history', recovery=True)
        recovery = QualityRecovery('book-recovered', book_gap.id, frozenset({book}), 12, 12,
                                   'documented_book_snapshot', 'source-snapshot-certificate')
        events = (fact('book9', book, 9, 100), fact('flow9', flow, 9, 0), book_gap, flow_gap,
                  fact('clean-copy11', book, 9, 100, known=11, origin='book9'), recovery,
                  fact('snapshot12', book, 9, 100, known=12, origin='book9'))
        index = EligibilityIndex(((book, p), (flow, p))); index.extend(events)
        for cut in (9, 10, 11, 12, 14):
            for field in (book, flow):
                self.assertEqual(index.field(field, p.id, cut=cut), field_reference(events, field, p, cut=cut))
        self.assertFalse(index.field(book, p.id, cut=11).admitted)
        self.assertTrue(index.field(book, p.id, cut=12).admitted)
        self.assertFalse(index.field(flow, p.id, cut=12).admitted)
        self.assertEqual(index.field(book, p.id, cut=12).observed_at, g['expected']['at12']['economic_observed_at'])
        flow_witness = (observed_span('flow-window', flow, 8, 14, operation='execution'),)
        support = aggregate_support((book_gap, flow_gap), (recovery,), field=flow, operation='execution',
                                    start=8, end=14, cut=14, observed_spans=flow_witness)
        self.assertEqual(support, aggregate_reference(events, field=flow, operation='execution',
                                                     start=8, end=14, cut=14, observed_spans=flow_witness))
        self.assertEqual((support.invalid_duration_ns, support.supported_duration_ns),
                         (g['expected']['flow_invalid_duration_ns'], g['expected']['flow_supported_duration_ns']))
        book_support = aggregate_support((book_gap,), (recovery,), field=book, operation='execution', start=8, end=14, cut=14,
                                         observed_spans=(observed_span('book-window', book, 8, 14, operation='execution'),))
        self.assertEqual(book_support.invalid_intervals, tuple(map(tuple, g['expected']['book_unavailable_intervals'])))
        # Existing MBP consumer: clean-looking quotes are insufficient; only the
        # matching certificate restores trust, and observed flow stays incomplete.
        def mbp(row, **kwargs):
            raw = raw_event(row, **kwargs)
            return normalize_mbp(decode_fields(raw.raw_fields), raw.address, native=False,
                                 scenario=LatencyScenario('quality-zero-lag-toy', 'event', 0, 0))
        reducer = BookReducer(); reducer.apply(mbp(0, at=9))
        gap = mbp(1, at=10, action='T', flags=132, size=2); reducer.apply(gap)
        reducer.apply(mbp(2, at=11))
        self.assertFalse(reducer.states[1].trusted)
        before_age = reducer.states[1].economic_quote_at
        snapshot = mbp(3, at=12, flags=168)
        reducer.apply(snapshot, recovery=RecoveryCertificate(1, gap.id, snapshot.id,
                                                            'documented_full_snapshot', 'quality-toy-certificate'))
        self.assertTrue(reducer.states[1].trusted)
        self.assertFalse(reducer.states[1].flow_complete)
        self.assertEqual(reducer.states[1].economic_quote_at, before_age)
        self.assertEqual(reducer.states[1].fresh_book_events, 1)
        before = index.checkpoint()
        with self.assertRaises(ContractError):
            index.append(QualityRecovery('wrong-flow-recovery', flow_gap.id, frozenset({flow}), 13, 13,
                                         'documented_book_snapshot', 'wrong-kind'))
        self.assertEqual(index.checkpoint(), before)

    def test_affected_intervals_union_and_partial_support_are_exact(self):
        g = GOLDEN['QJ-07']; k, independent = key(), key('trade_count', producer='flow', unit='contracts')
        events = tuple(incident(f'fault:{n}', (k,), right, start=left, end=right)
                       for n, (left, right) in enumerate(g['inputs']['incidents']))
        witness = (observed_span('full-window', k, 8, 22),)
        actual = aggregate_support(events, (), field=k, operation='valuation', start=8, end=22, cut=22, observed_spans=witness)
        expected = aggregate_reference(events, field=k, operation='valuation', start=8, end=22, cut=22, observed_spans=witness)
        self.assertEqual(actual, expected)
        self.assertEqual(actual.invalid_intervals, tuple(map(tuple, g['expected']['union'])))
        self.assertEqual((actual.invalid_duration_ns, actual.supported_duration_ns),
                         (g['expected']['invalid_duration_ns'], g['expected']['supported_duration_ns']))
        self.assertIsNone(actual.missing_contribution_upper_bound)
        separate = aggregate_support(events, (), field=independent, operation='valuation', start=8, end=22, cut=22,
                                     observed_spans=(observed_span('independent-window', independent, 8, 22),))
        self.assertEqual(separate.invalid_duration_ns, g['expected']['independent_field_invalid_duration_ns'])
        # The last fault's later receipt cannot invalidate the earlier visible cut.
        self.assertEqual(aggregate_support(events, (), field=k, operation='valuation', start=8, end=14, cut=14).invalid_duration_ns, 0)
        with self.assertRaises(ContractError):
            interval_union(((20, 10),))

    def test_quiet_gap_halt_snapshot_and_timeout_are_distinct(self):
        g = GOLDEN['QJ-08']
        inputs = [dict(expected_stream=True, recent_liveness=True, trade_count=0),
                  dict(expected_stream=True, recent_liveness=False, trade_count=0),
                  dict(expected_stream=True, recent_liveness=False, trade_count=0, halted=True),
                  dict(expected_stream=True, recent_liveness=True, trade_count=0, stale_copy=True),
                  dict(expected_stream=True, recent_liveness=True, trade_count=0, computation_timeout=True)]
        self.assertEqual([classify_stream(**row) for row in inputs], g['expected']['classifications'])
        self.assertEqual(classify_stream(expected_stream=False, recent_liveness=False, trade_count=0), 'not_expected_unobserved')
        self.assertEqual(classify_stream(expected_stream=False, recent_liveness=True, trade_count=0), 'observed_no_event')
        self.assertEqual(classify_stream(expected_stream=False, recent_liveness=False, trade_count=2), 'observed_events')
        self.assertEqual(classify_stream(expected_stream=True, recent_liveness=True, trade_count=2), 'observed_events')
        with self.assertRaises(ContractError):
            SourceLiveness('copy', 'source', 'NQH5', 10, 20, True, 'copied_snapshot', 'copy')
        compiled = graph()
        q = incident('timeout', (key('contracts', producer='oi', unit='contracts'),), 10,
                     kind='computation_timeout', severity='informational')
        result = QualityDependencies(compiled).propagate(q, cut=10, operation='forecasting')
        self.assertFalse(result.blocked)
        self.assertEqual({compiled.ports[id].lane for id in result.unconditional}, {'market', 'account', 'timer'})

    def test_revision_future_suffix_and_late_older_join_are_causal(self):
        g = GOLDEN['QJ-09']; k = key('oi', producer='options', unit='contracts')
        p = OperationPolicy('asof', 'valuation', g['inputs']['max_age_ns'])
        events = tuple(fact(row['id'], k, row['observed_at'], row['value'], known=row['known_at'],
                            revision=row['revision'], eligible=row['eligible']) for row in g['inputs']['facts'])
        index = EligibilityIndex(((k, p),)); index.extend(events)
        reversed_index = EligibilityIndex(((k, p),)); reversed_index.extend(tuple(reversed(events)))
        suffix_deleted = EligibilityIndex(((k, p),)); suffix_deleted.extend(events[:-1])
        ids = []
        for cut in g['inputs']['cuts']:
            result = index.field(k, p.id, cut=cut)
            ids.append(result.candidate_id if result.admitted else None)
            self.assertEqual(result, field_reference(events, k, p, cut=cut))
            self.assertEqual(result, reversed_index.field(k, p.id, cut=cut))
            if cut < 40:
                self.assertEqual(result, suffix_deleted.field(k, p.id, cut=cut))
        self.assertEqual(ids, g['expected']['admitted_ids'])
        result = index.field(k, p.id, cut=35)
        self.assertEqual(result.candidate_id, g['expected']['candidate_at35'])
        self.assertIsNone(result.payload_json)

    def test_availability_and_inclusive_ttl_endpoints(self):
        g = GOLDEN['QJ-10']; k = key()
        p = OperationPolicy('short', 'valuation', g['inputs']['max_age_ns'])
        value = fact('q', k, g['inputs']['observed_at'], 100, known=g['inputs']['known_at'])
        index = EligibilityIndex(((k, p),)); index.append(value)
        actual = [index.field(k, p.id, cut=cut) for cut in g['inputs']['cuts']]
        self.assertEqual([r.state for r in actual], g['expected']['states'])
        self.assertEqual([r.age_ns for r in actual], g['expected']['ages_ns'])
        self.assertEqual([(r.start, r.end) for r in index.intervals(k, p.id) if r.support.admitted],
                         [tuple(g['expected']['eligible_interval_half_open'])])
        for result in actual:
            self.assertEqual(result, field_reference((value,), k, p, cut=result.cut))
        # Future-paired quote cannot enter a sign operation even if it is nearest.
        sign = OperationPolicy('sign', 'signing', 2)
        index = EligibilityIndex(((k, sign),)); index.extend((fact('prior', k, 9, 100), fact('future', k, 11, 101)))
        self.assertEqual(index.field(k, sign.id, cut=10).candidate_id, 'prior')
        # Publication/receipt, not a daily label or assumed morning schedule, gates OI.
        late = fact('daily-report', k, 0, 100, known=20)
        index = EligibilityIndex(((k, OperationPolicy('daily', 'valuation', 100)),)); index.append(late)
        self.assertFalse(index.field(k, 'daily', cut=19).admitted)
        self.assertTrue(index.field(k, 'daily', cut=20).admitted)

    def test_joint_span_and_complete_movement_support_are_explicit(self):
        g = GOLDEN['QJ-11']; a, b = key('call'), key('put')
        p = OperationPolicy('joint-field', 'valuation', g['inputs']['max_field_age_ns'])
        bindings = ((a, p), (b, p)); events = (fact('call', a, 10, 100), fact('put', b, 18, 100))
        index = EligibilityIndex(bindings); index.extend(events)
        requests = tuple((k, policy.id) for k, policy in bindings)
        joint = JointPolicy('strict-span', g['inputs']['max_joint_observation_span_ns'])
        actual = index.snapshot(requests, cut=20, joint_policy=joint)
        self.assertEqual(actual, snapshot_reference(events, bindings, cut=20, joint_policy=joint))
        self.assertEqual([r.age_ns for r in actual.fields], g['expected']['individual_ages_ns'])
        self.assertTrue(all(f.admitted for f in actual.fields))
        self.assertEqual(actual.observation_span_ns, g['expected']['observation_span_ns'])
        self.assertEqual(actual.reasons, (g['expected']['joint_span_reason'],))
        joint = JointPolicy('movement-guard', 10, 5, 'NQH5')
        for row in g['inputs']['movement_witnesses']:
            witness = JointMovementEvidence(row['id'], 'NQH5', row['from'], row['until'], row['known_at'],
                                            row['complete'], row['min_ticks'], row['max_ticks'], 'path-proof:v1')
            with self.subTest(witness=row['id']):
                actual = index.snapshot(requests, cut=20, joint_policy=joint, movement=witness)
                self.assertEqual(actual, snapshot_reference(events, bindings, cut=20, joint_policy=joint, movement=witness))
                result = 'supported' if actual.supported else actual.reasons[0]
                self.assertEqual(result, g['expected']['with_span_limit10_movement_results'][row['id']])
        absent = index.snapshot(requests, cut=20, joint_policy=joint)
        self.assertEqual(absent.reasons, (g['expected']['missing_witness_if_required'],))
        future = JointMovementEvidence('future-proof', 'NQH5', 10, 20, 21, True, 100, 104, 'future')
        unsupported = index.snapshot(requests, cut=20, joint_policy=joint, movement=future)
        self.assertFalse(unsupported.supported)
        self.assertIsNone(unsupported.movement_id)

    def test_stale_field_does_not_refresh_with_new_row_or_block_independent_field(self):
        g = GOLDEN['QJ-12']; oi, quote = key('oi', producer='options', unit='contracts'), key('quote')
        policies = (OperationPolicy('oi-policy', 'forecasting', 5), OperationPolicy('quote-policy', 'forecasting', 2))
        bindings = tuple(zip((oi, quote), policies))
        events = (fact('old-oi-in-new-row', oi, 10, 100, known=20), fact('new-quote', quote, 19, 100, known=20))
        index = EligibilityIndex(bindings); index.extend(events)
        joint = JointPolicy('optional-oi', 100)
        actual = index.snapshot(tuple((k, p.id) for k, p in bindings), cut=20, joint_policy=joint, optional=frozenset({oi}))
        self.assertEqual(actual, snapshot_reference(events, bindings, cut=20, joint_policy=joint, optional=frozenset({oi})))
        for name, support in zip(('oi', 'quote'), actual.fields):
            self.assertEqual((support.age_ns, support.state), (g['expected'][name]['age_ns'], g['expected'][name]['state']))
            self.assertEqual(support.last_local_receipt_at, 20)
        self.assertTrue(actual.supported)
        self.assertEqual(actual.optional_omissions, (oi,))
        self.assertEqual(actual.values, ((quote, b'100'),))

    def test_overlap_union_preserves_aliases_and_rejects_conflict_atomically(self):
        g = GOLDEN['QJ-13']; k = key('oi', producer='options', instrument='c1', definition='d1', unit='contracts')
        p = OperationPolicy('alias', 'valuation', 100)
        events = tuple(fact(r['id'], k, r['observed_at'], r['value'], known=r['known_at']) for r in g['inputs']['equivalent_aliases'])
        a, b = EligibilityIndex(((k, p),)), EligibilityIndex(((k, p),))
        a.extend(events); b.extend(tuple(reversed(events)))
        result = a.field(k, p.id, cut=10)
        self.assertEqual(result, b.field(k, p.id, cut=10))
        self.assertEqual(result, field_reference(events, k, p, cut=10))
        self.assertEqual(json.loads(result.payload_json), g['expected']['economic_value'])
        self.assertEqual([id for id, _ in result.acquisition_versions], g['expected']['retained_acquisition_ids'])
        before = a.checkpoint()
        for invalid in (replace(events[1], payload_json=b'101'), fact('conflicting-new-id', k, 10, 101)):
            with self.subTest(id=invalid.id), self.assertRaises(ContractError):
                a.append(invalid)
            self.assertEqual(a.checkpoint(), before)

    def test_point_in_time_universe_and_known_oi_fraction(self):
        g = GOLDEN['QJ-14']; p = OperationPolicy('coverage', 'valuation', 100)
        def option_key(id, field):
            return key(field, producer='options', instrument=id, definition='d1', unit='contracts' if field == 'oi' else 'ticks',
                       asset='NDX', chain='NDXP', expiry='expiry:v1')
        members = tuple(UniverseMember(r['id'], 'd1', 'NDX', 'NDXP', 'expiry:v1', r['known_at'], r['active_from'],
                                       None, r['dte'], 'listing:' + r['id']) for r in g['inputs']['universe'])
        oi_keys = tuple(option_key(id, 'oi') for id in g['inputs']['observed_oi'])
        quote_key = option_key('c1', 'quote')
        events = tuple(fact('oi:' + k.instrument, k, 10, g['inputs']['observed_oi'][k.instrument]) for k in oi_keys)
        events += (fact('near:c1', quote_key, 10, 100), fact('broad:c1', quote_key, 10, 100))
        index = EligibilityIndex(tuple((k, p) for k in oi_keys + (quote_key,))); index.extend(events)
        oi_fields = tuple(index.field(k, p.id, cut=10) for k in oi_keys)
        quote_fields = (index.field(quote_key, p.id, cut=10),)
        result = observed_oi_coverage(members, contract=toy_coverage_contract(), oi_fields=oi_fields,
                                      quote_fields=quote_fields, cut=10, universe_version='PIT:v1')
        for name in ('eligible_contract_ids', 'missing_quote_ids'):
            self.assertEqual(list(getattr(result, name)), g['expected'][name])
        for name in ('known_oi_contract_count', 'missing_oi_contract_count', 'quoted_known_oi', 'total_reported_known_oi'):
            self.assertEqual(getattr(result, name), g['expected'][name])
        self.assertEqual(len(result.quoted_contract_ids), g['expected']['quoted_contract_count'])
        self.assertEqual(len(result.eligible_contract_ids), g['expected']['universe_count'])
        fraction = g['expected']['observed_oi_quote_fraction']
        self.assertEqual(result.observed_oi_quote_fraction, Fraction(fraction['numerator'], fraction['denominator']))
        self.assertIsNone(result.true_total_exposure_fraction)
        self.assertEqual(len(quote_fields[0].acquisition_versions), 2)
        # Two equal aliases still provide one stock observation, not twice its OI.
        again = observed_oi_coverage(members, contract=toy_coverage_contract(),
                                     oi_fields=oi_fields + oi_fields[:1], quote_fields=quote_fields * 2,
                                     cut=10, universe_version='PIT:v1')
        self.assertEqual(again, result)

    def test_no_eligible_monthly_expiry_is_not_outage(self):
        g = GOLDEN['QJ-15']
        universe = (UniverseMember('monthly', 'd1', 'NDX', 'NDX', 'month-end', 1, 1, None, 30, 'listing'),)
        result = observed_oi_coverage(universe, contract=toy_coverage_contract(),
                                      oi_fields=(), quote_fields=(), cut=10, universe_version='scope:v1', max_dte=14)
        self.assertEqual(len(result.eligible_contract_ids), g['expected']['expected_contract_count'])
        self.assertEqual((result.state, result.reason), (g['expected']['state'], g['expected']['reason']))
        broader = observed_oi_coverage(universe, contract=toy_coverage_contract(),
                                       oi_fields=(), quote_fields=(), cut=10, universe_version='scope:v2', max_dte=60)
        self.assertEqual(broader.eligible_contract_ids, ('monthly',))
        self.assertEqual(broader.missing_quote_ids, ('monthly',))
        self.assertNotEqual(broader.universe_version, result.universe_version)

    def test_definition_and_measured_source_capabilities_do_not_expand(self):
        g = GOLDEN['QJ-16']; p = OperationPolicy('capability', 'valuation', 100)
        for label in g['inputs']['unsupported_promotions']:
            with self.subTest(label=label):
                k = key(label, producer='source')
                index = EligibilityIndex(((k, p),)); index.append(fact(label, k, 10, 100, operations=frozenset()))
                self.assertEqual(index.field(k, p.id, cut=10).state, 'ineligible')
        a = key('quote', producer='options', instrument='NDX-monthly', definition='am-cash', asset='NDX', chain='NDX', expiry='same-date')
        b = key('quote', producer='options', instrument='NDXP-weekly', definition='pm-cash', asset='NDX', chain='NDXP', expiry='same-date')
        index = EligibilityIndex(((a, p), (b, p))); index.extend((fact('am', a, 10, 100), fact('pm', b, 10, 101)))
        fields = tuple(index.field(k, p.id, cut=10) for k in (a, b))
        self.assertNotEqual(fields[0].key, fields[1].key)
        self.assertEqual(len({f.key.instrument for f in fields}), g['expected']['distinct_contract_count'])
        empty = observed_oi_coverage((), contract=toy_coverage_contract(),
                                     oi_fields=(), quote_fields=fields, cut=10, universe_version='explicit-empty')
        self.assertEqual(empty.eligible_contract_ids, ())
        self.assertEqual(set(empty.outside_universe_ids), {'NDX-monthly', 'NDXP-weekly'})
        estimate = fact('scenario', a, 11, 103, estimated=True)
        index.append(estimate)
        self.assertEqual(index.field(a, p.id, cut=11).state, 'ineligible')
        admitted_estimate = replace(p, id='estimated-only', allow_estimated=True)
        separate = EligibilityIndex(((a, admitted_estimate),)); separate.append(estimate)
        self.assertEqual(separate.field(a, admitted_estimate.id, cut=11).state, 'estimated')

    def test_full_scan_and_interval_join_equal_every_cut_and_actual_operation_count(self):
        g = GOLDEN['QJ-17']; bindings, events, joint = comparison_fixture()
        index = EligibilityIndex(bindings); index.extend(events)
        requests = tuple((k, p.id) for k, p in bindings)
        reference_counts, full_ops, incremental_ops = Counter(), Counter(), Counter()
        rows, prior_vector, reused_value = [], None, None
        # Failure on a builder call proves lookup is not an alias for a full scan.
        with patch.object(index, '_resolve_build', side_effect=AssertionError('query called source resolver')):
            for cut in g['inputs']['cuts']:
                full = snapshot_reference(events, bindings, cut=cut, joint_policy=joint, counts=reference_counts)
                incremental = index.snapshot(requests, cut=cut, joint_policy=joint)
                self.assertEqual(incremental, full)
                full_value = arithmetic(full, full_ops)
                if incremental.version_vector != prior_vector:
                    reused_value = arithmetic(incremental, incremental_ops)
                    prior_vector = incremental.version_vector
                self.assertEqual(reused_value, full_value)
                rows.append({'cut': cut, 'ids': [f.candidate_id for f in incremental.fields],
                             'values': [json.loads(f.payload_json) for f in incremental.fields],
                             'ages': [f.age_ns for f in incremental.fields], 'output': reused_value})
        self.assertEqual(rows, g['expected']['rows'])
        self.assertEqual(reference_counts['candidate_row_checks'], g['expected']['reference_candidate_row_checks'])
        self.assertEqual(index.stats['query_interval_lookups'], g['expected']['interval_query_lookup_calls'])
        self.assertEqual(index.stats['query_source_candidate_scans'], g['expected']['interval_query_source_candidate_scans'])
        self.assertEqual(dict(full_ops), g['expected']['full_toy_arithmetic_operations'])
        self.assertEqual(dict(incremental_ops), g['expected']['incremental_toy_arithmetic_operations'])
        self.assertGreater(index.stats['build_candidate_checks'], 0)
        self.assertGreater(index.stats['build_intervals'], 0)
        print('F06_F07_JOIN_COMPARISON ' + json.dumps({'rows': rows, 'reference': dict(reference_counts),
              'interval_build_and_query': dict(index.stats), 'full_arithmetic': dict(full_ops),
              'incremental_arithmetic': dict(incremental_ops)}, sort_keys=True))

    def test_contract_and_bounded_storage_failures_leave_state_unchanged(self):
        k = key(); p = OperationPolicy('valid', 'valuation', 5)
        constructors = [lambda: QualityIncident('mutable', 'raw', {k}, 10, 10, 20, 'bad', 'dependent-feature-block', OPERATIONS, 'e'),
                        lambda: fact('bool-time', k, True, 100), lambda: OperationPolicy('negative', 'valuation', -1),
                        lambda: OperationPolicy('unknown', 'magic', 5),
                        lambda: incident('reverse', (k,), 10, start=20, end=10),
                        lambda: key(definition=''), lambda: fact('no-source', k, 10, 100, source='')]
        for number, constructor in enumerate(constructors):
            with self.subTest(number=number), self.assertRaises(ContractError):
                constructor()
        index = EligibilityIndex(((k, p),)); original = fact('a', k, 10, 100); index.append(original)
        before = index.checkpoint()
        for action in (lambda: index.append(replace(original, payload_json=b'101')),
                       lambda: index.extend((fact('candidate', k, 11, 101), fact('forged-copy', k, 11, 999, known=12, origin='a'))),
                       lambda: EligibilityIndex.restore(before, bindings=((k, replace(p, max_age_ns=6)),))):
            with self.assertRaises(ContractError):
                action()
            self.assertEqual(index.checkpoint(), before)
        for obj, attribute, value in ((original, 'id', 'changed'), (k, 'definition_version', 'changed'),
                                      (p, 'max_age_ns', 10), (before, 'events', ())):
            with self.subTest(attribute=attribute), self.assertRaises(FrozenInstanceError):
                setattr(obj, attribute, value)
        with self.assertRaises(ContractError):
            Graph([Port('a', 'F06', 0, 'a.v1', frozenset({'v'}), (InputPort('b', 'b.v1', frozenset({'v'})),)),
                   Port('b', 'F06', 0, 'b.v1', frozenset({'v'}), (InputPort('a', 'a.v1', frozenset({'v'})),))])
        bounded = EligibilityIndex(((k, p),), max_events=1); bounded.append(original); state = bounded.checkpoint()
        with self.assertRaises(ContractError):
            bounded.append(fact('overflow', k, 20, 101))
        self.assertEqual(bounded.checkpoint(), state)
        bounded = EligibilityIndex(((k, p),), max_intervals=1); state = bounded.checkpoint()
        with self.assertRaises(ContractError):
            bounded.append(original)
        self.assertEqual(bounded.checkpoint(), state)
        with self.assertRaises(ContractError):
            index.append(fact('int64-end-overflow', k, 2**63 - 1, 100))
        self.assertEqual(index.checkpoint(), before)
        wrong_field = key('ask'); broader = EligibilityIndex(((k, p), (wrong_field, p)))
        gap = incident('gap', (k,), 10, kind='book_gap', recovery=True); broader.append(gap); state = broader.checkpoint()
        with self.assertRaises(ContractError):
            broader.append(QualityRecovery('wrong-scope', gap.id, frozenset({wrong_field}), 12, 12,
                                            'documented_book_snapshot', 'wrong'))
        self.assertEqual(broader.checkpoint(), state)

    def test_checkpoint_suffix_and_repair_require_preceding_original_support(self):
        g = GOLDEN['QJ-20']; oi, independent = key('oi', producer='options', unit='contracts'), key('buy', producer='trade', unit='contracts')
        p = OperationPolicy('repair', 'forecasting', 100); bindings = ((oi, p), (independent, p))
        prefix = (fact('oi8', oi, 8, 100), fact('trade8', independent, 8, 9))
        suffix = (fact('oi10', oi, 10, 110), fact('oi-correction', oi, 10, 120, known=20, revision=1))
        index = EligibilityIndex(bindings); index.extend(prefix); checkpoint = index.checkpoint()
        index.extend(suffix)
        restored = EligibilityIndex.restore(checkpoint, bindings=bindings)
        initial_builds = restored.stats['rebuilt_fields']; restored.extend(suffix)
        self.assertEqual(restored.stats['rebuilt_fields'] - initial_builds, 1)
        self.assertFalse(restored.append(suffix[-1]))
        self.assertEqual(restored.checkpoint(), index.checkpoint())
        for cut in g['inputs']['query_cuts']:
            for field in (oi, independent):
                expected = field_reference(prefix + suffix, field, p, cut=cut)
                self.assertEqual(restored.field(field, p.id, cut=cut), expected)
                self.assertEqual(index.field(field, p.id, cut=cut), expected)
        request = dict(affected_from=10, checkpoint_cut=8, correction_known_at=20, cut=20,
                       affected_fields=frozenset({oi}), retained_intervals=((8, 20),))
        self.assertEqual(plan_repair(**request).state, 'ready')
        self.assertEqual(plan_repair(**dict(request, cut=15)).state, 'not_yet_known')
        missing = plan_repair(**dict(request, retained_intervals=((8, 10), (12, 20))))
        self.assertEqual((missing.state, missing.missing_intervals, missing.affected_fields),
                         ('unavailable', ((10, 12),), frozenset({oi})))
        with self.assertRaises(ContractError):
            plan_repair(**dict(request, checkpoint_cut=12))
        old_cut = index.field(oi, p.id, cut=15)
        index.append(incident('missing-originals', (oi,), 20, start=10, kind='missing_original_support', scope='history'))
        self.assertFalse(index.field(oi, p.id, cut=20).admitted)
        self.assertTrue(index.field(independent, p.id, cut=20).admitted)
        self.assertEqual(index.field(oi, p.id, cut=15), old_cut)

    def test_positive_coverage_witnesses_partition_unknown_and_invalid_time(self):
        k, other = key(), key('ask')
        request = dict(field=k, operation='valuation', start=0, end=20, cut=20)
        unknown = aggregate_support((), (), **request)
        self.assertEqual(unknown, aggregate_reference((), **request))
        self.assertEqual((unknown.supported_duration_ns, unknown.invalid_duration_ns, unknown.unknown_duration_ns),
                         (0, 0, 20))
        self.assertEqual(unknown.unknown_intervals, ((0, 20),))
        bad = incident('known-invalid', (k,), 15, start=5, end=15)
        witnesses = (observed_span('first', k, 0, 8), observed_span('overlap', k, 6, 12),
                     observed_span('last', k, 18, 20), observed_span('wrong-field', other, 0, 20),
                     observed_span('wrong-operation', k, 0, 20, operation='execution'),
                     observed_span('not-yet-known', k, 0, 20, known=21))
        result = aggregate_support((bad,), (), **request, observed_spans=witnesses)
        self.assertEqual(result, aggregate_reference((bad,), **request, observed_spans=witnesses))
        self.assertEqual(result.supported_intervals, ((0, 5), (18, 20)))
        self.assertEqual(result.invalid_intervals, ((5, 15),))
        self.assertEqual(result.unknown_intervals, ((15, 18),))
        self.assertEqual((result.supported_duration_ns, result.invalid_duration_ns, result.unknown_duration_ns), (7, 10, 3))
        self.assertEqual(result.observation_evidence_ids, ('evidence:first', 'evidence:last', 'evidence:overlap'))
        # Repeated witness identities are idempotent; absence of an incident
        # cannot turn a future, unrelated or unregistered-operation span into data.
        self.assertEqual(result, aggregate_support((bad,), (), **request, observed_spans=witnesses + witnesses[:1]))
        for supplied in ([witnesses[0]], witnesses + (replace(witnesses[0], end=7),)):
            with self.subTest(supplied=type(supplied).__name__), self.assertRaises(ContractError):
                aggregate_support((bad,), (), **request, observed_spans=supplied)
            with self.assertRaises(ContractError):
                aggregate_reference((bad,), **request, observed_spans=supplied)
        with self.assertRaises(FrozenInstanceError):
            witnesses[0].end = 20
        with self.assertRaises(ContractError):
            observed_span('future-completion', k, 0, 20, known=19)

    def test_copy_and_late_old_revision_cannot_resurrect_invalid_content(self):
        k = key('oi', producer='options', unit='contracts'); p = OperationPolicy('revision', 'valuation', 100)
        original = fact('z-original', k, 10, 100)
        invalid = fact('revision-2-invalid', k, 10, 120, known=20, revision=2, eligible=False)
        copied = fact('aaa-later-copy', k, 10, 100, known=30, origin=original.id)
        late_old = fact('late-revision-1', k, 10, 110, known=40, revision=1)
        events = (original, invalid, copied, late_old)
        index = EligibilityIndex(((k, p),)); index.extend(events)
        for cut in (20, 30, 40):
            support = index.field(k, p.id, cut=cut)
            self.assertEqual(support, field_reference(events, k, p, cut=cut))
            self.assertEqual((support.candidate_id, support.origin_id, support.state, support.payload_json),
                             (invalid.id, invalid.id, 'invalid', None))
            self.assertEqual(support.observed_at, 10)
            self.assertEqual(support.last_local_receipt_at, cut)
        restored = EligibilityIndex.restore(index.checkpoint(), bindings=((k, p),))
        self.assertEqual(restored.field(k, p.id, cut=40), index.field(k, p.id, cut=40))
        prefix = EligibilityIndex(((k, p),)); prefix.extend(events[:2])
        self.assertEqual(prefix.field(k, p.id, cut=20), index.field(k, p.id, cut=20))
        correction = fact('revision-3-valid', k, 10, 125, known=50, revision=3)
        fresh = fact('new-economic-observation', k, 11, 130, known=60)
        old_correction = fact('old-observation-revision-4', k, 10, 126, known=70, revision=4)
        index.extend((correction, fresh, old_correction))
        self.assertEqual(index.field(k, p.id, cut=50).candidate_id, correction.id)
        self.assertEqual(index.field(k, p.id, cut=70).candidate_id, fresh.id)
        self.assertEqual(index.field(k, p.id, cut=70),
                         field_reference(events + (correction, fresh, old_correction), k, p, cut=70))
        copy_only = EligibilityIndex(((k, p),)); copy_only.extend((original, copied))
        support = copy_only.field(k, p.id, cut=30)
        self.assertEqual((support.candidate_id, support.origin_id, support.age_ns), (original.id, original.id, 20))
        self.assertEqual({id for id, _ in support.acquisition_versions}, {original.id, copied.id})

    def test_alias_economic_identity_ignores_receipt_but_preserves_all_lineage(self):
        k = key('oi', producer='options', unit='contracts'); p = OperationPolicy('aliases', 'valuation', 100)
        first = fact('a-first', k, 10, 100)
        second = fact('b-second', k, 10, 100, known=20)
        second = replace(second, clocks=replace(second.clocks, source_version='second-acquisition:v1'))
        events = first, second
        index = EligibilityIndex(((k, p),)); index.extend(events)
        reordered = EligibilityIndex(((k, p),)); reordered.extend(tuple(reversed(events)))
        for cut in (10, 19, 20, 30):
            support = index.field(k, p.id, cut=cut)
            self.assertEqual(support, reordered.field(k, p.id, cut=cut))
            self.assertEqual(support, field_reference(events, k, p, cut=cut))
            self.assertEqual(support.observed_at, 10)
            self.assertEqual(len(support.acquisition_versions), 1 if cut < 20 else 2)
        support = index.field(k, p.id, cut=30)
        self.assertEqual(support.acquisition_versions,
                         ((first.id, 'source-content:v1'), (second.id, 'second-acquisition:v1')))
        self.assertEqual((support.last_source_observation_at, support.last_value_change_at,
                          support.last_local_receipt_at, support.age_ns), (10, 10, 20, 20))
        before = index.checkpoint()
        conflicts = (fact('late-conflicting-price', k, 10, 101, known=30),
                     fact('late-conflicting-status', k, 10, 100, known=30, eligible=False))
        for bad in conflicts:
            with self.subTest(id=bad.id), self.assertRaises(ContractError):
                index.append(bad)
            self.assertEqual(index.checkpoint(), before)
            with self.assertRaises(ContractError):
                field_reference(events + (bad,), k, p, cut=30)

    def test_undeclared_fact_capabilities_admit_no_operation(self):
        k = key(); declared = fact('declared', k, 10, 100)
        unproven = FieldFact('no-capability-evidence', k, declared.source, 10, declared.clocks, b'100')
        self.assertEqual(unproven.available_operations, frozenset())
        policies = tuple(OperationPolicy(operation, operation, 100) for operation in sorted(OPERATIONS))
        index = EligibilityIndex(tuple((k, p) for p in policies)); index.append(unproven)
        for policy in policies:
            support = index.field(k, policy.id, cut=10)
            self.assertEqual((support.state, support.reasons), ('ineligible', ('source_capability_missing',)))
            self.assertEqual(support, field_reference((unproven,), k, policy, cut=10))

    def test_oi_coverage_requires_oi_role_and_every_declared_quote_component(self):
        member = UniverseMember('c1', 'd1', 'NDX', 'NDXP', 'expiry', 1, 1, None, 5, 'listing:c1')
        def option(field, unit='ticks'):
            return key(field, producer='options', instrument='c1', definition='d1', unit=unit,
                       asset='NDX', chain='NDXP', expiry='expiry')
        oi, volume, bid, ask, trade = option('oi', 'contracts'), option('volume', 'contracts'), option('bid'), option('ask'), option('trade')
        oi_policy = OperationPolicy('stock', 'valuation', 100)
        quote_policy = OperationPolicy('quote', 'valuation', 2)
        execution_policy = OperationPolicy('execution', 'execution', 100)
        contract = OICoverageContract('two-sided-valuation:v1', CoverageFieldRole(oi.ref, 'contracts', 'valuation'),
                                      (CoverageFieldRole(bid.ref, 'ticks', 'valuation'),
                                       CoverageFieldRole(ask.ref, 'ticks', 'valuation')))
        bindings = ((oi, oi_policy), (volume, oi_policy), (bid, quote_policy), (ask, quote_policy),
                    (trade, quote_policy), (bid, execution_policy))
        events = (fact('oi', oi, 10, 100), fact('volume', volume, 10, 999), fact('bid', bid, 10, 100),
                  fact('old-ask', ask, 7, 102), fact('late-ask', ask, 10, 102, known=11), fact('trade', trade, 10, 101))
        index = EligibilityIndex(bindings); index.extend(events)
        request = dict(contract=contract, cut=10, universe_version='pit:v1')
        oi_support = (index.field(oi, oi_policy.id, cut=10),)
        bid_support = index.field(bid, quote_policy.id, cut=10)
        ask_support = index.field(ask, quote_policy.id, cut=10)
        self.assertEqual(ask_support.state, 'stale')
        partial = observed_oi_coverage((member,), oi_fields=oi_support,
                                       quote_fields=(bid_support, ask_support), **request)
        self.assertEqual((partial.total_reported_known_oi, partial.quoted_known_oi), (100, 0))
        self.assertEqual(partial.quoted_contract_ids, ())
        self.assertEqual(partial.missing_quote_fields, (('c1', ask.ref),))
        self.assertEqual(partial.coverage_contract_version, contract.version)
        for wrong_oi, wrong_quotes in (
            ((index.field(volume, oi_policy.id, cut=10),), (bid_support, ask_support)),
            (oi_support, (index.field(trade, quote_policy.id, cut=10),)),
            (oi_support, (index.field(bid, execution_policy.id, cut=10), ask_support)),
        ):
            with self.assertRaises(ContractError):
                observed_oi_coverage((member,), oi_fields=wrong_oi, quote_fields=wrong_quotes, **request)
        complete = observed_oi_coverage((member,), contract=contract,
                                        oi_fields=(index.field(oi, oi_policy.id, cut=11),),
                                        quote_fields=tuple(index.field(k, quote_policy.id, cut=11) for k in (bid, ask)),
                                        cut=11, universe_version='pit:v1')
        self.assertEqual(complete.quoted_contract_ids, ('c1',))
        self.assertEqual(complete.missing_quote_fields, ())
        self.assertEqual(complete.observed_oi_quote_fraction, Fraction(1, 1))
        with self.assertRaises(ContractError):
            OICoverageContract('mutable', contract.oi_role, list(contract.required_quote_components))
        with self.assertRaises(FrozenInstanceError):
            contract.required_quote_components = ()
        with self.assertRaises(ContractError):
            observed_oi_coverage((member,), contract=None, oi_fields=oi_support,
                                 quote_fields=(bid_support,), cut=10, universe_version='pit:v1')

    def test_index_configuration_remains_read_only_across_queries_and_restore(self):
        k = key(); p = OperationPolicy('configuration', 'valuation', 100)
        index = EligibilityIndex(((k, p),), max_events=10, max_intervals=100); index.append(fact('original', k, 10, 100))
        before, support = index.checkpoint(), index.field(k, p.id, cut=20)
        changes = (('bindings', ((k, replace(p, max_age_ns=1)),)), ('max_events', 1000),
                   ('max_intervals', 1000), ('configuration_version', 'forged'),
                   ('_configuration', None))
        for name, value in changes:
            with self.subTest(attribute=name), self.assertRaises(AttributeError):
                setattr(index, name, value)
            self.assertEqual(index.checkpoint(), before)
            self.assertEqual(index.field(k, p.id, cut=20), support)
        with self.assertRaises(AttributeError):
            del index._configuration
        with self.assertRaises(FrozenInstanceError):
            index._configuration.max_events = 1
        restored = EligibilityIndex.restore(before, bindings=index.bindings)
        self.assertEqual(restored.checkpoint(), before)
        self.assertEqual((restored.bindings, restored.max_events, restored.max_intervals, restored.configuration_version),
                         (index.bindings, 10, 100, index.configuration_version))
        self.assertEqual(restored.field(k, p.id, cut=20), support)

    def test_direct_interval_helpers_validate_recovery_scope_and_duplicates(self):
        flow, other = key('volume', producer='flow', unit='contracts'), key('other', producer='flow', unit='contracts')
        gap = incident('flow-gap', (flow,), 10, kind='flow_gap', scope='history', recovery=True)
        witness = (observed_span('known-flow-span', flow, 8, 16, operation='execution'),)
        valid = QualityRecovery('flow-replay', gap.id, frozenset({flow}), 15, 14,
                                'certified_flow_replay', 'retained-trades')
        invalid = (replace(valid, method='documented_book_snapshot'), replace(valid, incident_id='other-incident'),
                   replace(valid, fields=frozenset({other})), replace(valid, effective_at=10),
                   replace(valid, known_at=9, effective_at=9))
        request = dict(field=flow, operation='execution', start=8, end=16, cut=16, observed_spans=witness)
        for recovery in invalid:
            with self.subTest(recovery=recovery), self.assertRaises(ContractError):
                incident_interval(gap, (recovery,), field=flow, cut=16)
            with self.assertRaises(ContractError):
                aggregate_support((gap,), (recovery,), **request)
            with self.assertRaises(ContractError):
                aggregate_reference((gap, recovery), **request)
            with self.assertRaises(ContractError):
                field_reference((gap, recovery), flow, OperationPolicy('flow', 'execution', 100), cut=16)
        duplicate = replace(valid, id='duplicate-proof')
        for recoveries in ((valid, duplicate), (valid, replace(valid, evidence_id='conflicting-proof'))):
            with self.assertRaises(ContractError):
                incident_interval(gap, recoveries, field=flow, cut=16)
            with self.assertRaises(ContractError):
                aggregate_support((gap,), recoveries, **request)
            with self.assertRaises(ContractError):
                aggregate_reference((gap,) + recoveries, **request)
        self.assertEqual(incident_interval(gap, (valid,), field=flow, cut=14), (10, None))
        self.assertEqual(incident_interval(gap, (valid, valid), field=flow, cut=16), (10, 14))
        repaired = aggregate_support((gap, gap), (valid, valid), **request)
        self.assertEqual(repaired, aggregate_reference((gap, valid, gap, valid), **request))
        self.assertEqual((repaired.invalid_intervals, repaired.supported_intervals, repaired.unknown_intervals),
                         (((10, 14),), ((8, 10), (14, 16)), ()))

    def test_malformed_support_cannot_forge_admission_or_mutable_lineage(self):
        k = key(); p = OperationPolicy('support', 'valuation', 100)
        index = EligibilityIndex(((k, p),)); index.extend((fact('q', k, 10, 100), pulse('live', k, 10)))
        support = index.field(k, p.id, cut=10)
        mutations = ({'observed_at': None}, {'last_source_observation_at': None}, {'last_value_change_at': None},
                     {'candidate_id': None}, {'origin_id': None}, {'origin_id': 'unavailable-origin'},
                     {'acquisition_versions': (['q', 'source-content:v1'],)},
                     {'acquisition_versions': (('q', 'v1'), ('q', 'v2'))},
                     {'acquisition_versions': (('q', ''),)}, {'payload_json': None},
                     {'state': 'invalid'}, {'state': []}, {'operation': []},
                     {'reasons': ([],)}, {'incident_ids': ('fault', 'fault')},
                     {'liveness_at': None}, {'liveness_id': None}, {'liveness_at': 11},
                     {'last_value_change_at': 11}, {'policy_version': ''})
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(ContractError):
                replace(support, **mutation)
        snapshot = joint_snapshot((support,), joint_policy=JointPolicy('supported', 0))
        for mutation in ({'fields': [support]}, {'fields': (support, support)},
                         {'observation_span_ns': None}, {'cut': 9}, {'optional_omissions': (k,)},
                         {'supported': False}):
            with self.subTest(snapshot_mutation=mutation), self.assertRaises(ContractError):
                replace(snapshot, **mutation)
        # Documented publication can support a value without an actual local
        # receipt timestamp; this is distinct from missing observation lineage.
        published = FieldFact('published', k, 'source:published', 10,
                              Clocks(10, 12, 'publication:v1', AvailabilityBasis.PUBLISHED, published_at=12),
                              b'100', available_operations=frozenset({'valuation'}))
        publication_index = EligibilityIndex(((k, p),)); publication_index.append(published)
        published_support = publication_index.field(k, p.id, cut=12)
        self.assertTrue(published_support.admitted)
        self.assertIsNone(published_support.last_local_receipt_at)
        self.assertEqual(published_support, field_reference((published,), k, p, cut=12))

    def test_provenance_edges_propagate_unavailability_without_lagged_or_field_spill(self):
        compiled = Graph([
            Port('raw', 'F01', 0, 'raw.v1', frozenset({'bad', 'good'}), lane='market'),
            Port('account', 'P01', 0, 'account.v1', frozenset({'position'}), lane='account'),
            Port('timer', 'F03', 0, 'timer.v1', frozenset({'due'}), lane='timer'),
            Port('required', 'F06', 1, 'required.v1', frozenset({'value'}), (InputPort('raw', 'raw.v1', frozenset()),)),
            Port('optional', 'F06', 1, 'optional.v1', frozenset({'value'}), (InputPort('raw', 'raw.v1', frozenset(), optional=True),)),
            Port('audit', 'F06', 1, 'audit.v1', frozenset(), (InputPort('raw', 'raw.v1', frozenset()),)),
            Port('select-good', 'F06', 1, 'good.v1', frozenset({'value'}), (InputPort('raw', 'raw.v1', frozenset({'good'})),)),
            Port('select-bad', 'F06', 1, 'bad.v1', frozenset({'value'}), (InputPort('raw', 'raw.v1', frozenset({'bad'})),)),
            Port('lagged', 'F06', 1, 'lagged.v1', frozenset({'value'}),
                 (InputPort('raw', 'raw.v1', frozenset(), lag_ns=1, max_age_ns=100),)),
            Port('audit-consumer', 'F07', 2, 'audit-consumer.v1', frozenset({'value'}), (InputPort('audit', 'audit.v1', frozenset()),)),
            Port('audit-optional', 'F07', 2, 'audit-optional.v1', frozenset({'value'}),
                 (InputPort('audit', 'audit.v1', frozenset(), optional=True),)),
            Port('optional-child', 'F07', 2, 'optional-child.v1', frozenset({'value'}),
                 (InputPort('optional', 'optional.v1', frozenset({'value'})),)),
            Port('required-child', 'F07', 2, 'required-child.v1', frozenset({'value'}),
                 (InputPort('required', 'required.v1', frozenset({'value'})),)),
        ])
        bad = incident('raw-fault', (key('bad', producer='raw'),), 10, end=20, stage='raw')
        result = QualityDependencies(compiled).propagate(bad, cut=10, operation='forecasting')
        self.assertEqual(result.unavailable_producers,
                         frozenset({'raw', 'required', 'audit', 'audit-consumer', 'select-bad', 'required-child'}))
        self.assertEqual(result.blocked, frozenset({FieldRef('raw', 'bad'), FieldRef('required', 'value'),
                                                   FieldRef('audit-consumer', 'value'), FieldRef('select-bad', 'value'),
                                                   FieldRef('required-child', 'value')}))
        self.assertEqual(set(result.dirty_consumers),
                         {'required', 'optional', 'audit', 'audit-consumer', 'audit-optional',
                          'select-bad', 'optional-child', 'required-child'})
        self.assertEqual(result.optional_provenance_omissions, (('audit-optional', 'audit'), ('optional', 'raw')))
        self.assertEqual(result.optional_omissions, ())
        self.assertEqual(set(result.unconditional), {'raw', 'account', 'timer'})
        for cut in (9, 20):
            inactive = QualityDependencies(compiled).propagate(bad, cut=cut, operation='forecasting')
            self.assertFalse(inactive.blocked or inactive.unavailable_producers or inactive.dirty_consumers
                             or inactive.optional_provenance_omissions)

    def test_actual_timed_toy_join_reports_build_and_query_wall_cpu_rss(self):
        bindings, events, joint = comparison_fixture(); requests = tuple((k, p.id) for k, p in bindings)
        records = []
        for repeat in range(5):
            build_wall, build_cpu = time.perf_counter_ns(), time.process_time_ns()
            index = EligibilityIndex(bindings); index.extend(events)
            build_cpu = time.process_time_ns() - build_cpu; build_wall = time.perf_counter_ns() - build_wall
            query_wall, query_cpu = time.perf_counter_ns(), time.process_time_ns()
            outputs, operations = [], Counter()
            for cut in GOLDEN['QJ-17']['inputs']['cuts']:
                outputs.append(arithmetic(index.snapshot(requests, cut=cut, joint_policy=joint), operations))
            query_cpu = time.process_time_ns() - query_cpu; query_wall = time.perf_counter_ns() - query_wall
            self.assertEqual(outputs, [row['output'] for row in GOLDEN['QJ-17']['expected']['rows']])
            self.assertEqual(dict(operations), {'subtract': 5, 'add': 5})
            self.assertEqual(index.stats['query_interval_lookups'], 15)
            records.append({'id':f'actual-toy:{repeat}', 'recorded_at':time.time_ns(),
                            'build_wall_ns':build_wall, 'build_cpu_ns':build_cpu,
                            'query_wall_ns':query_wall, 'query_cpu_ns':query_cpu,
                            'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                            'work':dict(index.stats), 'arithmetic':dict(operations)})
        print('F06_F07_ACTUAL_TOY_TIMING ' + json.dumps({'workload':'frozen synthetic operations; actual process timing',
              'live_latency_claim':False, 'samples':records}, sort_keys=True))


if __name__ == '__main__':
    unittest.main()
