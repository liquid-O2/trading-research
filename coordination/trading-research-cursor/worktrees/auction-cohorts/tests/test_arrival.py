"""Registered F12 finite assertions. Only the supervised shared worker runs these."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import time
import resource
from contextlib import ExitStack
import trading_research.runtime.arrival as arrival_module

from trading_research.errors import ContractError, IntegrityError
from trading_research.runtime.arrival import (
    ArrivalRecord, ArrivalReplay, CallbackSpec, RawArrivalJournal, DecodeAfterCommit,
    UncertainCommit, TornTail, JournalCorruption, MAGIC, FRAME_HEADER, MAX_RECORDS,
    fixture_trace, inspect_journal, quarantine_torn_tail, frame_bytes, content_hash,
    market_callback, transaction_callback, quality_callback, publication_callback, order_callback,
    compare_observations, first_divergence, delay_one, monotonic_elapsed,
    receipt_lag, completion_lag, latency_summary, drop_summary,
)
from references.arrival_literal import literal_replay
from trading_research.foundations.graph import Graph, InputPort, Port
from trading_research.foundations.quality import FieldKey, OperationPolicy
from trading_research.foundations.time import AvailabilityBasis, Clocks, derived_clocks
from trading_research.execution.orders import OrderSpec, BrokerEvent
from trading_research.data.transactions import TransactionLedger

ENGINEERING_METRICS = {}
GOLDEN_PATH = Path(__file__).parent / 'golden' / 'f12-arrival-trace.json'


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def source(ordinal, value=None, *, receipt=None, monotonic=None, event=None, provider=None,
           raw=None, decoder='market', semantic_kind='other', economic_id=None,
           source_id='fixture', generation='A', provider_sequence=None, delivery=None,
           trace_id='toy', provenance='synthetic_fixture', boot='A', instrument='ES', definition='toy-terms'):
    receipt = ordinal if receipt is None else receipt
    raw = encoded({'value': value}) if raw is None else raw
    return ArrivalRecord(trace_id=trace_id, arrival_ordinal=ordinal, delivery_id=delivery or f'd{ordinal}', kind='source',
        boot_id=boot, receipt_utc_ns=receipt, receipt_monotonic_ns=receipt if monotonic is None else monotonic,
        provenance=provenance, source_event_utc_ns=event, provider_published_utc_ns=provider,
        payload={'source_id': source_id, 'instrument': instrument, 'definition': definition,
                 'stream_generation': generation, 'provider_sequence': provider_sequence, 'provider_cursor': None,
                 'economic_id': economic_id, 'semantic_kind': semantic_kind, 'raw_hex': raw.hex(),
                 'raw_sha256': hashlib.sha256(raw).hexdigest(), 'decoder_id': decoder})


def marker(kind, ordinal, payload, *, receipt=None, monotonic=None, boot='A', delivery=None, trace_id='toy'):
    receipt = ordinal if receipt is None else receipt
    return ArrivalRecord(trace_id=trace_id, arrival_ordinal=ordinal, delivery_id=delivery or f'{kind}{ordinal}', kind=kind,
        boot_id=boot, receipt_utc_ns=receipt, receipt_monotonic_ns=receipt if monotonic is None else monotonic,
        provenance='synthetic_fixture', payload=payload)


def decision(ordinal, *, receipt=None, callback='market', versions=(), delivery=None):
    return marker('decision', ordinal, {'decision_id': delivery or f'decision{ordinal}', 'callback_id': callback,
        'served_version_ids': list(versions), 'action': 'supplied-offline-evidence'}, receipt=receipt, delivery=delivery)


def timer(ordinal, *, callback='market', receipt=None, monotonic=None, due=None, delivery=None):
    actual = ordinal if receipt is None else receipt
    mono = actual if monotonic is None else monotonic
    return marker('timer', ordinal, {'timer_id': delivery or f'timer{ordinal}', 'callback_id': callback,
        'due_boot_id': 'A', 'due_monotonic_ns': mono if due is None else due},
        receipt=actual, monotonic=mono, delivery=delivery)


def complete(ordinal, version, *, receipt=None, start=10):
    return marker('completion', ordinal, {'job_id': 'job:' + version, 'callback_id': 'publication',
        'input_version_ids': [version], 'start_boot_id': 'A', 'start_monotonic_ns': start,
        'result': {'value': 100 if version == 'v1' else 101}}, receipt=receipt)


def published_source(ordinal, version, *, receipt=None, event=None, provider=None):
    return source(ordinal, raw=encoded({'version_id': version, 'value': 100 if version == 'v1' else 101,
        'job_id': 'job:' + version, 'expires_at_ordinal': 1000}), decoder='publication',
        receipt=receipt, event=event, provider=provider)


def transaction_source(ordinal, quantity, *, economic='x', version='x:v1', operation='insert', predecessor=None,
                       event=1, delivery=None):
    body = {'transaction_key': {'provider': 'fixture', 'dataset': 'synthetic', 'publisher_or_venue': None,
        'channel': 'trade', 'source_session': 'session1', 'instrument_key': 'ES', 'ownership_id': economic,
        'ownership_basis': 'provider_transaction', 'ownership_evidence_id': 'fixture-ownership'},
        'version_id': version, 'operation': operation, 'predecessor_version_id': predecessor,
        'condition_contract_id': 'fixture-condition', 'identity_evidence_id': 'fixture-ownership',
        'value': {'event_at': event, 'price_decimal': None, 'price_ticks': 100, 'quantity': quantity,
            'quantity_unit': 'contracts', 'reported_aggressor': None, 'aggregation_unit': 'synthetic-record',
            'instrument_kind': 'futures_outright', 'terms_version': 'toy-terms', 'usd_multiplier': None,
            'money_role': None, 'volume_eligibility': True, 'directional_eligibility': False,
            'condition_contract_id': 'fixture-condition', 'raw_condition': 'synthetic-eligible',
            'quality_reasons': [], 'history_complete': False, 'source_order': None}}
    return source(ordinal, raw=encoded(body), decoder='transactions', semantic_kind='trade',
                  economic_id=economic, event=event, delivery=delivery)


def quality_bindings(names):
    return tuple((n, FieldKey(n, 'value', 'ES', 'toy-terms', 'ticks', 'futures'),
                  OperationPolicy(n + '-execution', 'execution', 1000)) for n in names)


def quality_source(ordinal, field_name, value, *, observed, receipt=None, revision=0, extra=None):
    body = {'quality_kind': 'fact', 'field_name': field_name, 'value': value, 'observed_at': observed, 'revision': revision, 'available_operations': ['execution']}
    body.update(extra or {})
    return source(ordinal, raw=encoded(body), decoder='quality', receipt=receipt, event=observed,
                  source_id=field_name + '-source')


def ack(ordinal, *, economic_known=None, state='acknowledged', state_version=1, ack_id='ackO'):
    return marker('order_ack', ordinal, {'order_id': 'O', 'ack_id': ack_id, 'state_version': state_version,
        'economic_known_at': ordinal if economic_known is None else economic_known,
        'simulated_boundary': True, 'callback_id': 'orders', 'state': state})


def order_spec():
    return OrderSpec('O', 'A', 'ES', 1, 1, 'entry', 'market', None, 10, 100, 'supplied-synthetic-authorization')


class ArrivalTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.golden = {c['case_id']: c for c in json.loads(GOLDEN_PATH.read_text())['cases']}

    def expected(self, id):
        return self.golden[id]['expected']

    def replay(self, records, callbacks=None):
        callbacks = (market_callback(),) if callbacks is None else callbacks
        driver = ArrivalReplay(callbacks, trace_id=records[0].trace_id if records else 'toy')
        driver.consume_all(fixture_trace(records))
        return driver

    def reference_equal(self, records, callbacks, driver):
        reference = literal_replay(tuple(r.record() for r in records), callbacks)
        self.assertEqual(driver.states, reference['states'])
        self.assertEqual(driver.observations, reference['observations'])
        return reference

    def test_identical_bytes(self):
        e = self.expected('F12-T01')
        records = (source(0, 100, receipt=10), source(1, 101, receipt=20))
        callbacks = (market_callback(),)
        historical = self.replay(records, callbacks)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'arrivals.bin'
            with RawArrivalJournal(path) as journal:
                for record in records:
                    journal.append(record)
                captured = ArrivalReplay(callbacks, trace_id='toy')
                captured.consume_all(journal.committed)
                self.assertEqual(tuple(r.canonical_bytes for r in journal.records), tuple(r.canonical_bytes for r in records))
                size = path.stat().st_size
            self.assertEqual([historical.observation_at_utc(cut, mapping_policy='single_boot_nondecreasing_utc')['semantic']['states']['market']['value'] for cut in (15, 20)], e['historical'])
            self.assertEqual([captured.observation_at_utc(cut, mapping_policy='single_boot_nondecreasing_utc')['semantic']['states']['market']['value'] for cut in (15, 20)], e['captured'])
            self.assertEqual(historical.observations, captured.observations)
            reference = self.reference_equal(records, callbacks, captured)
            self.assertEqual(first_divergence(historical.observations, captured.observations, original_records=records)['status'] == 'equal', e['semantic_parity'])
            ENGINEERING_METRICS['same_bytes_comparison'] = {'measured_local_journal_bytes': size,
                'candidate_callback_calls': captured.stats['callback_calls'], **reference['metrics'],
                'synthetic_records': 2, 'actual_live_evidence': False}

    def test_actual_receipt(self):
        e = self.expected('F12-T02')
        records = (published_source(7, 'v1', event=1, provider=2), complete(11, 'v1', start=7))
        driver = self.replay(records, (publication_callback(),))
        self.assertIsNone(driver.observation_at_utc(6, mapping_policy='single_boot_nondecreasing_utc'))
        self.assertEqual(driver.observations[0]['timing']['receipt_utc_ns'], e['first_known'])
        published = driver.states['publication']['published']
        self.assertEqual(published[0]['published_ordinal'], e['published'])
        self.assertEqual(any(x['published_ordinal'] == 14 for x in published), e['published_14'])
        clocks = Clocks(1, 7, 'fixture', AvailabilityBasis.RECEIVED, received_at=7)
        with self.assertRaises(ContractError):
            derived_clocks((clocks,), source_version='j', actual_completion_at=11,
                           simulated_start_at=7, simulated_duration_ns=3, assumption_id='forbidden-double-charge')
        self.assertEqual(completion_lag(records[1], source_id='worker', session_id='toy')['value_ns'], 4)

    def test_missing_receipt(self):
        e = self.expected('F12-T03')
        record = source(0, 100, receipt=5, event=1, provider=2, provenance='modeled_scenario')
        lag = receipt_lag(record, source_id='fixture', session_id='toy', comparable_clock_evidence_id='synthetic-clock-pair', uncertainty_ns=0)
        actual = latency_summary((lag,), source_id='fixture', session_id='toy', method='source_to_receipt', provenance='actual_capture')
        self.assertEqual(record.receipt_utc_ns, e['modeled_receipt'])
        self.assertIsNone(e['actual_receipt'])
        self.assertEqual(record.provenance, 'modeled_scenario')
        self.assertFalse(lag['actual_qualified'])
        self.assertEqual([lag['value_ns']] if lag['actual_qualified'] else [], e['actual_lag_samples'])
        self.assertEqual(actual['n'], 0)
        self.assertFalse(actual['actual_live_evidence'])

    def test_clock_adjust(self):
        e = self.expected('F12-T04')
        records = (source(0, 1, receipt=1000, monotonic=100),
            marker('clock_adjust', 1, {'old_utc_ns': 1000, 'new_utc_ns': 900, 'old_monotonic_ns': 100,
                'new_monotonic_ns': 110, 'evidence_id': 'paired-clock-observation'}, receipt=900, monotonic=110),
            timer(2, receipt=900, monotonic=110, due=105))
        driver = self.replay(records)
        diagnostic = driver.control['clock_diagnostics'][0]
        self.assertEqual(diagnostic['monotonic_elapsed_ns'], e['elapsed'])
        self.assertEqual(diagnostic['utc_step_ns'], e['utc_step'])
        self.assertEqual(diagnostic['kind'] == 'clock_adjust', e['clock_adjust'])
        self.assertEqual(records[1].receipt_utc_ns != 900, e['rewritten_utc'])
        self.assertEqual(driver.states['market']['timers'], ['timer2'])
        with self.assertRaises(ContractError):
            driver.observation_at_utc(950, mapping_policy='single_boot_nondecreasing_utc')

    def test_boot_epoch(self):
        e = self.expected('F12-T05')
        records = (marker('boot', 0, {'previous_boot_id': None, 'new_boot_id': 'A'}, receipt=1000, monotonic=100),
                   marker('boot', 1, {'previous_boot_id': 'A', 'new_boot_id': 'B'}, receipt=2000, monotonic=5, boot='B'))
        driver = self.replay(records, ())
        result = monotonic_elapsed('A', 100, 'B', 5)
        self.assertEqual(result['elapsed_ns'], e['elapsed'])
        self.assertEqual(result['reason'], e['reason'])
        self.assertEqual(set(driver.control['boots']), {'A', 'B'})

    def test_reconnect_reset(self):
        e = self.expected('F12-T06')
        records = (source(1, 100, generation='A', provider_sequence=9),
            marker('connection', 2, {'source_id': 'fixture', 'generation': 'A', 'status': 'disconnected', 'reason': 'fixture drop'}),
            marker('connection', 3, {'source_id': 'fixture', 'generation': 'B', 'status': 'connected', 'reason': 'fixture reconnect'}),
            source(4, 101, generation='B', provider_sequence=1))
        driver = self.replay(records)
        self.assertEqual(driver.states['market']['raw_deliveries'], e['retained'])
        self.assertEqual([r.payload['stream_generation'] for r in records if r.kind == 'source'], e['generations'])
        self.assertEqual(driver.control['sources']['fixture']['last_sequence'], 1)
        self.assertTrue(e['sequence_reset'])
        with self.assertRaises(ContractError):
            self.replay((records[0], source(2, 101, generation='A', provider_sequence=1)))

    def test_reconnect_duplicate(self):
        e = self.expected('F12-T07')
        records = (transaction_source(10, 2, delivery='d1'), transaction_source(15, 2, delivery='d2'))
        driver = self.replay(records, (transaction_callback(),))
        state = driver.states['transactions']
        for key in ('raw_deliveries', 'economic_applications', 'quantity'):
            self.assertEqual(state[key], e[key])
        ledger = TransactionLedger.restore(bytes.fromhex(state['checkpoint_hex']))
        self.assertEqual(ledger.metrics()['receipt_count'], 2)
        self.assertEqual(len(ledger.deltas), 1)

    def test_snapshot_trades(self):
        e = self.expected('F12-T08')
        records = (source(10, raw=encoded({'quantity': 5}), semantic_kind='snapshot', economic_id='s1'),
                   source(11, raw=encoded({'quantity': 5}), semantic_kind='snapshot', economic_id='s1'),
                   source(12, raw=encoded({'quantity': 2}), semantic_kind='trade', economic_id='t1'))
        state = self.replay(records).states['market']
        self.assertEqual(state['quantity'], e['quantity'])
        self.assertEqual(state['raw_deliveries'], e['raw_deliveries'])
        trades = self.replay((transaction_source(12, 2, economic='t1'),), (transaction_callback(),))
        self.assertEqual(trades.states['transactions']['quantity'], e['economic_trade_quantity'])

    def test_sequence_tie(self):
        e = self.expected('F12-T09')
        records = (source(4, 1, source_id='A', provider_sequence=1), source(5, 2, source_id='B', provider_sequence=1))
        driver = self.replay(records)
        self.assertEqual([o['arrival_ordinal'] for o in driver.observations], e['order'])
        self.assertEqual(driver.states['market']['raw_deliveries'], e['retained'])

    def test_batch_boundary(self):
        e = self.expected('F12-T10')
        records = tuple(source(n, raw=encoded({'quantity': value}), semantic_kind='trade') for n, value in enumerate((1, 2, 3)))
        committed = fixture_trace(records)
        callbacks = (market_callback(),)
        a = ArrivalReplay(callbacks, trace_id='toy'); b = ArrivalReplay(callbacks, trace_id='toy')
        a.consume_all(committed[:1]); a.consume_all(committed[1:])
        b.consume_all(committed[:2]); b.consume_all(committed[2:])
        self.assertEqual([o['semantic']['states']['market']['quantity'] for o in a.observations], e['prefix_sums'])
        self.assertEqual(a.states['market']['quantity'], e['final'])
        self.assertEqual(a.observations == b.observations, e['parity'])
        reference = self.reference_equal(records, callbacks, a)
        ENGINEERING_METRICS['batch_boundary_comparison'] = {'candidate_records_applied': a.stats['records_applied'],
            'candidate_callback_calls': a.stats['callback_calls'], **reference['metrics'], 'actual_live_evidence': False}

    def test_quiet_gap(self):
        e = self.expected('F12-T11')
        records = (source(10, raw=encoded({'quantity': 1}), semantic_kind='trade'),
            marker('connection', 15, {'source_id': 'fixture', 'generation': 'A', 'status': 'connected', 'reason': 'keepalive'}),
            marker('connection', 16, {'source_id': 'fixture', 'generation': 'A', 'status': 'disconnected', 'reason': 'transport loss'}),
            marker('gap', 17, {'source_id': 'fixture', 'generation': 'A', 'gap_id': 'gap1', 'status': 'open', 'reason': 'disconnect'}, receipt=16))
        driver = self.replay(records)
        self.assertEqual(driver.control['sources']['fixture']['gap_started_ordinal'], e['gap_start'])
        self.assertEqual(driver.observations[1]['semantic']['states']['market']['quantity'] - 1, e['keepalive_trade_count'])
        self.assertEqual(driver.states['market']['raw_deliveries'], 1)
        self.assertEqual(records[2].receipt_utc_ns, e['quiet_until'])
        self.assertNotIn('expected_count', driver.control['gaps']['gap1'])

    def test_subscription(self):
        e = self.expected('F12-T12')
        records = tuple(marker('subscription', at, {'source_id': 'fixture', 'subscription_id': symbol,
            'generation': 'g' + symbol, 'operation': operation, 'instruments': [symbol]})
            for operation, symbol, at in [('subscribe', 'A', 10), ('denied', 'B', 15), ('unsubscribe', 'A', 20)])
        driver = self.replay(records, ())
        subscriptions = {r['subscription_id']: r for r in driver.control['subscriptions'].values()}
        self.assertEqual(subscriptions['B']['operation'] == 'subscribe', e['B_eligible'])
        self.assertEqual(subscriptions['A']['ended_ordinal'], e['A_generation_ends'])
        self.assertEqual(subscriptions['B']['operation'] == 'denied', e['denial_retained'])

    def test_delayed_bbo(self):
        e = self.expected('F12-T13')
        callbacks = (quality_callback(quality_bindings(('trade', 'bbo')), entry_fields=('trade', 'bbo')),)
        records = (quality_source(6, 'trade', 101, observed=5), decision(7, callback='quality'),
                   quality_source(9, 'bbo', 100, observed=4), decision(10, receipt=9, callback='quality'))
        driver = self.replay(records, callbacks)
        decisions = [o for o in driver.observations if o['kind'] == 'decision']
        self.assertEqual([o['semantic']['states']['quality']['support']['bbo']['admitted'] for o in decisions], e['bbo_eligible'])
        prefix = self.replay(records[:2], callbacks)
        self.assertEqual(prefix.observations != driver.observations[:2], e['decision7_rewritten'])
        self.reference_equal(records, callbacks, driver)

    def test_dropped_chain(self):
        e = self.expected('F12-T14')
        graph = Graph((Port('chain', 'F01', 0, 'chain.v1', frozenset({'value'}), lane='market'),
            Port('protection', 'P07', 0, 'protection.v1', frozenset({'value'}), lane='account'),
            Port('entry', 'P01', 1, 'entry.v1', frozenset({'eligible'}),
                 (InputPort('chain', 'chain.v1', frozenset({'value'})),))))
        callbacks = (quality_callback(quality_bindings(('chain', 'protection')), entry_fields=('chain',),
                                      protection_fields=('protection',), graph=graph),)
        records = (quality_source(10, 'chain', 1, observed=10),
                   quality_source(11, 'protection', 1, observed=10, receipt=10),
                   marker('gap', 12, {'source_id': 'chain-source', 'generation': 'A', 'gap_id': 'chain-loss',
                       'status': 'open', 'reason': 'critical feed loss', 'quality_fields': ['chain']}),
                   decision(13, receipt=12, callback='quality'))
        state = self.replay(records, callbacks).states['quality']
        self.assertEqual(state['entry_eligible'], e['entry_eligible_at12'])
        self.assertEqual(state['protection_eligible'], e['independent_protection_eligible_at12'])
        self.assertIn('entry', state['blocked_ports'])
        self.assertIn('protection', state['unconditional_ports'])
        self.assertNotIn('protection', state['blocked_ports'])

    def test_timer_alone(self):
        e = self.expected('F12-T15')
        records = (source(10, 100), timer(15), source(20, 101))
        callbacks = (market_callback(),)
        driver = self.replay(records, callbacks)
        timer_output = driver.observations[1]['timing']['outputs']['market'][0]
        self.assertEqual(timer_output['fired_ordinal'], e['timer_fired'])
        self.assertEqual(driver.states['market']['raw_deliveries'] - 2, e['synthetic_trades'])
        self.reference_equal(records, callbacks, driver)

    def test_interrupted_compute(self):
        e = self.expected('F12-T16')
        records = (published_source(10, 'v1'), timer(15, callback='publication'), complete(20, 'v1'))
        callbacks = (publication_callback(),)
        committed = fixture_trace(records)
        interrupted = ArrivalReplay(callbacks, trace_id='toy')
        interrupted.consume_all(committed[:2])
        restored = ArrivalReplay.restore(interrupted.checkpoint(), callbacks=callbacks, retained_prefix=committed[:2], trace_id='toy')
        restored.consume_all(committed[2:])
        self.assertEqual([[p['input_version'], p['published_ordinal']] for p in restored.states['publication']['published']], e['publications'])
        self.assertEqual(len(restored.states['publication']['published']), e['publication_count'])
        uninterrupted = self.replay(records, callbacks)
        self.assertEqual(restored.checkpoint(), uninterrupted.checkpoint())
        self.assertEqual(restored.observations, uninterrupted.observations)
        self.reference_equal(records, callbacks, restored)
        self.assertFalse(e['used_live_wall_clock'])

    def test_served_version(self):
        e = self.expected('F12-T17')
        records = (published_source(10, 'v1'), published_source(15, 'v2'), complete(20, 'v1'),
                   decision(22, callback='publication', versions=('v1',)), complete(25, 'v2', start=15),
                   decision(26, receipt=25, callback='publication', versions=('v2',)))
        callbacks = (publication_callback(),)
        driver = self.replay(records, callbacks)
        self.assertEqual([r['served'][0] for r in driver.states['publication']['served']], e['served'])
        self.assertTrue(all(r['matches_recorded_versions'] for r in driver.states['publication']['served']))
        self.reference_equal(records, callbacks, driver)
        self.assertEqual([p['published_ordinal'] for p in driver.states['publication']['published']], [20, 25])

    def test_order_restart(self):
        e = self.expected('F12-T18')
        callbacks = (order_callback((order_spec(),), account_id='A'), market_callback())
        records = (timer(12), ack(14), ack(15, economic_known=14))
        committed = fixture_trace(records)
        before = ArrivalReplay(callbacks, trace_id='toy'); before.consume(committed[0])
        restored = ArrivalReplay.restore(before.checkpoint(), callbacks=callbacks, retained_prefix=committed[:1], trace_id='toy')
        before13 = restored.observation_at_utc(13, mapping_policy='single_boot_nondecreasing_utc')
        self.assertEqual(bool(before13['semantic']['states']['orders']['states']), e['ack_known_at13'])
        restored.consume_all(committed[1:])
        state = restored.states['orders']
        self.assertEqual(len(state['states']), e['order_count'])
        self.assertEqual(state['states']['O']['observed_state'], e['state'])
        self.assertEqual(state['states']['O']['kernel_state'], 'working')
        self.assertEqual(state['submissions'], e['submissions'])
        self.assertEqual(state['duplicates'], 1)
        self.reference_equal(records, callbacks, restored)
        self.assertEqual(restored.checkpoint(), self.replay(records, callbacks).checkpoint())
        # Additional existing-position restart boundary: the supplied fill is
        # observed once by the existing kernel, without calling submit.
        fill = BrokerEvent('fill0', 'O', 'fill', 11, 11, 'synthetic-fill-proof',
                           execution_id='execution0', filled_quantity=1, fill_ticks=100)
        position_callbacks = (order_callback((order_spec(),), account_id='A', initial_events=(fill,)), market_callback())
        positioned = ArrivalReplay(position_callbacks, trace_id='toy'); positioned.consume(committed[0])
        recovered = ArrivalReplay.restore(positioned.checkpoint(), callbacks=position_callbacks, retained_prefix=committed[:1], trace_id='toy')
        recovered.consume(committed[1])
        self.assertEqual(recovered.states['orders']['positions'], {'ES': 1})
        self.assertEqual(recovered.states['orders']['submissions'], 0)

    def test_stale_order(self):
        e = self.expected('F12-T19')
        records = (ack(20, state_version=2, ack_id='new'),
                   ack(25, economic_known=15, state='pending', state_version=1, ack_id='stale'))
        state = self.replay(records, (order_callback((order_spec(),), account_id='A'),)).states['orders']
        self.assertEqual(state['states']['O']['observed_state'], e['state'])
        self.assertEqual(state['raw_acks'], e['raw_acks'])
        self.assertEqual(state['stale_rejections'], e['stale_rejections'])
        self.assertEqual(state['states']['O']['kernel_state'], 'working')

    def test_suffix(self):
        e = self.expected('F12-T20')
        callbacks = (quality_callback(quality_bindings(('bbo',)), entry_fields=('bbo',)),)
        prefix = (quality_source(10, 'bbo', 100, observed=10), decision(20, callback='quality'))
        suffix = (quality_source(30, 'bbo', 90, observed=10, revision=1),
                  quality_source(40, 'bbo', 9999, observed=40))
        short = self.replay(prefix, callbacks)
        full = self.replay(prefix + suffix, callbacks)
        self.assertEqual(short.observations != full.observations[:2], e['outputs_through20_changed'])
        self.reference_equal(prefix + suffix, callbacks, full)
        tx = self.replay((transaction_source(10, 2, event=10),
            transaction_source(30, 3, event=10, version='x:v2', operation='revise', predecessor='x:v1')),
            (transaction_callback(),))
        ledger = TransactionLedger.restore(bytes.fromhex(tx.states['transactions']['checkpoint_hex']))
        self.assertEqual([r.value.quantity for r in ledger.asof(instrument='ES', cut=20)], [2])
        self.assertEqual([r.value.quantity for r in ledger.asof(instrument='ES', cut=30)], [3])

    def test_poll_stream(self):
        e = self.expected('F12-T21')
        streaming = (source(0, 100, receipt=10), source(1, 110, receipt=15), source(2, 100, receipt=20))
        polling = (source(0, 100, receipt=10), source(1, 100, receipt=20))
        a, b = self.replay(streaming), self.replay(polling)
        oa = a.observation_at_utc(20, mapping_policy='single_boot_nondecreasing_utc')
        ob = b.observation_at_utc(20, mapping_policy='single_boot_nondecreasing_utc')
        self.assertEqual([o['semantic']['states']['market']['value'] for o in (oa, ob)], e['endpoint_values'])
        self.assertEqual(compare_observations(oa, ob)['semantic_equal'], e['endpoint_parity'])
        self.assertEqual(any(o['semantic']['states']['market']['value'] == 110 for o in b.observations), e['poll_peak110_certified'])
        self.assertFalse(any(o['timing']['receipt_utc_ns'] == 15 for o in b.observations))
        self.assertEqual('unsupported', e['cut15_parity'])
        self.assertFalse(compare_observations(oa, ob)['parity'])

    def test_fault_diagnosis(self):
        e = self.expected('F12-T22')
        # Three source deliveries; the explicit decision occupies its own
        # arrival slot between source delivery2 and source delivery3.
        records = (source(1, 100, receipt=10), source(2, 110, receipt=20),
                   decision(3, receipt=25, delivery='decision25'), source(4, 100, receipt=30))
        transformed, plan = delay_one(records, seed=7, target_utc_ns=30, target_monotonic_ns=30)
        again, second_plan = delay_one(records, seed=7, target_utc_ns=30, target_monotonic_ns=30)
        self.assertEqual([r.arrival_ordinal for r in records if r.kind == 'source'], [1, 2, 4])
        self.assertEqual(len([r for r in records if r.kind == 'source']), 3)
        self.assertEqual(plan['selected_index'], e['selected_index'])
        self.assertEqual(plan['selected_original_ordinal'], e['selected_original_ordinal'])
        self.assertEqual((transformed, plan) == (again, second_plan), e['repeat_seed_same_schedule'])
        self.assertEqual(bool(plan['origin_mapping']), e['derived_trace_has_origin_mapping'])
        a = self.replay(records)
        b = self.replay(transformed)
        report = first_divergence(a.observations, b.observations, original_records=records, scope='decisions')
        self.assertEqual(report['diagnostic_receipt_utc_ns'], e['first_divergence_cut'])
        self.assertEqual(report['minimal_leading_prefix'][-1]['delivery_id'], e['minimal_prefix_ends_at'])
        self.assertEqual(len(report['minimal_leading_prefix']), 3)
        self.assertEqual(records[1].receipt_utc_ns, 20)
        self.reference_equal(transformed, (market_callback(),), b)
        with self.assertRaises(ContractError):
            delay_one(records, seed=7, target_utc_ns=19, target_monotonic_ns=19)

    def test_latency_denominator(self):
        e = self.expected('F12-T23')
        records = tuple(source(i, 1, receipt=20 + i, event=20 + i - lag) for i, lag in enumerate((1, 2, 9)))
        samples = tuple(receipt_lag(r, source_id='fixture', session_id='toy', comparable_clock_evidence_id='toy-clock-pair', uncertainty_ns=0) for r in records)
        summary = latency_summary(samples, source_id='fixture', session_id='toy', method='source_to_receipt', provenance='synthetic_fixture')
        drops = drop_summary(('a', 'b', 'c'), source_id='fixture', generation='A', window_id='W',
            identity_contract='synthetic-provider-delivery-id', expected_count=4, expected_evidence_id='fixture-count')
        for key in ('p50', 'p95', 'p99', 'n', 'actual_live_evidence'):
            self.assertEqual(summary[key], e[key])
        self.assertEqual(drops['missing'], e['missing'])
        self.assertEqual(drops['drop_rate'], e['drop_rate'])
        ENGINEERING_METRICS['synthetic_latency_arithmetic'] = {'summary': summary, 'drops': drops,
            'measurement_scope': 'hand-specified clock arithmetic, not measured live transport or worker elapsed time'}

    def test_bar_open(self):
        e = self.expected('F12-T24')
        callbacks = (quality_callback(quality_bindings(('bar',)), entry_fields=('bar',)),)
        records = (decision(1, receipt=30, callback='quality'), decision(2, receipt=60, callback='quality'),
            quality_source(3, 'bar', 110, observed=0, receipt=65, extra={'bar_open': 0, 'bar_end': 60, 'finalized': True}),
            decision(4, receipt=65, callback='quality'))
        driver = self.replay(records, callbacks)
        observed = [o['semantic']['states']['quality']['support']['bar']['admitted'] for o in driver.observations if o['kind'] == 'decision']
        self.assertEqual(observed, e['high_eligible'])
        no_data = self.replay((source(0, raw=encoded({'quality_kind': 'no_data', 'field_name': 'bar'}),
                                      decoder='quality', receipt=65),), callbacks)
        self.assertEqual(no_data.states['quality']['support']['bar']['value'] == 0, e['no_data_implies_zero'])
        self.assertIsNone(no_data.states['quality']['support']['bar']['value'])

    def test_raw_before_decode(self):
        e = self.expected('F12-T25')
        record = source(0, raw=bytes.fromhex('ff00'))
        operations = []
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'raw.bin'
            with RawArrivalJournal(path, hook=operations.append) as journal:
                operations.clear()
                with self.assertRaises(DecodeAfterCommit) as failure:
                    journal.append_and_decode(record, lambda raw: raw.decode('utf-8'))
                self.assertEqual(operations, e['operation_order'])
                self.assertEqual(journal.records[0].raw_bytes.hex(), e['raw_retained_hex'])
                self.assertEqual(len(journal.records), e['committed_raw_records'])
                self.assertEqual(isinstance(failure.exception.cause, UnicodeDecodeError), e['decode_failed'])
                before = path.read_bytes()
                with self.assertRaises(ContractError):
                    RawArrivalJournal(path)
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(e['second_writer'], 'rejected_before_write')
                ENGINEERING_METRICS['durable_raw_boundary'] = {'measured_local_journal_bytes': path.stat().st_size,
                    'retained_raw_bytes': len(journal.records[0].raw_bytes), 'ordered_operations': list(operations),
                    'scope': 'POSIX local fault harness; no power-loss or live-capture claim'}

    def test_append_fsync_failure(self):
        e = self.expected('F12-T26')
        calls, armed = [], {'active': False}
        def hook(operation):
            if armed['active'] and operation == 'fsync':
                raise OSError('injected fsync failure')
        record = source(0, 1, delivery='d1')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'uncertain.bin'
            with RawArrivalJournal(path, hook=hook) as journal:
                armed['active'] = True
                with self.assertRaises(UncertainCommit):
                    journal.append_and_decode(record, lambda raw: calls.append(raw))
                self.assertEqual(len(calls), e['initial_dispatch_count'])
                self.assertEqual(journal.records, ())
                with self.assertRaises(UncertainCommit):
                    journal.append(record)
            with RawArrivalJournal(path) as recovered:
                self.assertEqual(len(recovered.records), e['recovered_records'])
                _, created, _ = recovered.append_and_decode(record, lambda raw: calls.append(raw))
                self.assertEqual(int(created), e['exact_retry_new_records'])
                self.assertEqual(len(calls), e['final_dispatch_count'])
                driver = ArrivalReplay((market_callback(),), trace_id='toy')
                driver.consume_all(recovered.committed); driver.consume(recovered.committed[0])
                self.assertEqual(driver.states['market']['raw_deliveries'], 1)
        self.assertEqual(e['initial_result'], 'uncertain_commit')

    def test_torn_tail(self):
        e = self.expected('F12-T27')
        first, second = source(0, 1), source(1, 2)
        partial = frame_bytes(second)[:-7]
        with tempfile.TemporaryDirectory() as directory:
            path, clean = Path(directory) / 'torn.bin', Path(directory) / 'clean.bin'
            with RawArrivalJournal(path) as journal:
                journal.append(first)
            with path.open('ab') as file:
                file.write(partial)
            original = path.read_bytes()
            inspection = inspect_journal(path)
            self.assertEqual(len(inspection.records), e['verified_prefix_records'])
            self.assertEqual(inspection.tail_classification, e['tail_classification'])
            self.assertEqual(inspection.tail, partial)
            with self.assertRaises(TornTail):
                RawArrivalJournal(path)
            evidence = quarantine_torn_tail(path, clean)
            self.assertEqual(Path(evidence['evidence_path']).exists(), e['tail_quarantined'])
            self.assertEqual(path.read_bytes() != original, e['original_mutated'])
            self.assertEqual(len(inspect_journal(clean).records), 1)
            self.assertEqual(path.read_bytes() == original, not e['silent_truncation'])

    def test_interior_corruption(self):
        e = self.expected('F12-T28')
        records = tuple(source(n, n) for n in range(3))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'corrupt.bin'
            with RawArrivalJournal(path) as journal:
                for record in records:
                    journal.append(record)
            offset = len(MAGIC) + len(frame_bytes(records[0]))
            raw = bytearray(path.read_bytes())
            raw[offset + FRAME_HEADER.size + 3] ^= 1
            path.write_bytes(raw)
            with self.assertRaises(JournalCorruption) as failure:
                inspect_journal(path)
            self.assertEqual(failure.exception.frame_index, e['first_bad_frame'])
            with self.assertRaises(JournalCorruption):
                RawArrivalJournal(path)
            self.assertEqual(e['recovery'], 'rejected')
            self.assertFalse(e['frame3_dispatched'])

    def test_delivery_id_conflict(self):
        e = self.expected('F12-T29')
        record = source(0, raw=bytes.fromhex('aa'), delivery='d1')
        changed = source(0, raw=bytes.fromhex('bb'), delivery='d1')
        with tempfile.TemporaryDirectory() as directory:
            with RawArrivalJournal(Path(directory) / 'dedup.bin') as journal:
                self.assertTrue(journal.append(record)[1])
                self.assertFalse(journal.append(record)[1])
                with self.assertRaises(IntegrityError):
                    journal.append(changed)
                self.assertEqual(len(journal.records), e['committed_unique_deliveries'])
                self.assertEqual(journal.records[0].raw_bytes, bytes.fromhex('aa'))
        self.assertEqual(e['exact_retry'], 'idempotent')
        self.assertEqual(e['changed_retry'], 'conflict')

    def test_economic_id_conflict(self):
        e = self.expected('F12-T30')
        records = (transaction_source(10, 2, economic='econ1', delivery='d1'),
                   transaction_source(15, 3, economic='econ1', delivery='d2'))
        state = self.replay(records, (transaction_callback(),)).states['transactions']
        for key in ('raw_deliveries', 'economic_applications', 'quantity'):
            self.assertEqual(state[key], e[key])
        self.assertEqual(bool(state['incidents']), e['integrity_incident'])
        self.assertEqual(TransactionLedger.restore(bytes.fromhex(state['checkpoint_hex'])).metrics()['receipt_count'], 1)

    def test_callback_atomicity(self):
        e = self.expected('F12-T31')
        def increment(state, record):
            state['value'] += 1
            return state, [{'semantic': {'value': state['value']}}]
        def fail(state, record):
            state['value'] = 99
            raise ValueError('injected pure callback failure')
        callbacks = (CallbackSpec('increment', content_hash('v1'), frozenset({'source'}), 'Counter.v1', {'value': 0}, increment),
                     CallbackSpec('raise', content_hash('v1'), frozenset({'source'}), 'Counter.v1', {'value': 0}, fail))
        driver = ArrivalReplay(callbacks, trace_id='toy')
        before = driver.checkpoint()
        with self.assertRaises(ValueError):
            driver.consume(fixture_trace((source(0, 1, decoder='increment'),))[0])
        self.assertEqual(driver.states['increment']['value'], e['published_state'])
        self.assertEqual(driver.next_ordinal, e['next_ordinal'])
        self.assertEqual(list(driver.observations), e['outputs'])
        self.assertEqual(driver.checkpoint() != before, e['committed_state_mutated'])
        self.assertFalse(e['external_effects_permitted'])
        self.assertEqual(driver.stats['records_applied'], 0)

    def test_checkpoint_restore(self):
        e = self.expected('F12-T32')
        records = tuple(source(n, raw=encoded({'quantity': value}), semantic_kind='trade') for n, value in enumerate((1, 2, 3)))
        callbacks, committed = (market_callback(),), fixture_trace(records)
        before = ArrivalReplay(callbacks, trace_id='toy'); before.consume_all(committed[:2])
        raw = before.checkpoint()
        self.assertEqual(before.states['market']['quantity'], e['checkpoint_state'])
        self.assertEqual(raw == before.checkpoint(), e['checkpoint_bytes_same_state_equal'])
        restored = ArrivalReplay.restore(raw, callbacks=callbacks, retained_prefix=committed[:2], trace_id='toy')
        restored.consume(committed[2])
        uninterrupted = self.replay(records, callbacks)
        self.assertEqual(restored.states['market']['quantity'], e['restored_final'])
        self.assertEqual(uninterrupted.states['market']['quantity'], e['uninterrupted_final'])
        self.assertEqual(restored.checkpoint(), uninterrupted.checkpoint())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'checkpoint.json'
            before.write_checkpoint(path)
            original = path.read_bytes()
            def hook(operation):
                if operation == 'replace':
                    raise OSError('interrupt before checkpoint replacement')
            with self.assertRaises(OSError):
                restored.write_checkpoint(path, hook=hook)
            self.assertEqual(path.read_bytes() == original, e['prior_checkpoint_survives'])
            restored.write_checkpoint(path)
            self.assertEqual(path.read_bytes(), restored.checkpoint())
        ENGINEERING_METRICS['restart_comparison'] = {'restore_validation_records': restored.stats['restore_validation_records'],
            'candidate_callback_calls_including_prefix_verification': restored.stats['callback_calls'],
            'measured_checkpoint_bytes': len(restored.checkpoint()), 'scope': 'finite synthetic replay checkpoint'}

    def test_checkpoint_mismatch(self):
        e = self.expected('F12-T33')
        records = (source(0, 1), source(1, 2))
        callbacks = (market_callback(version='v1'),)
        driver = self.replay(records, callbacks)
        raw, retained = driver.checkpoint(), fixture_trace(records)
        with self.assertRaises(ContractError):
            ArrivalReplay.restore(raw, callbacks=(market_callback(version='v2'),), retained_prefix=retained, trace_id='toy')
        changed = fixture_trace((source(0, 999), records[1]))
        for payload, prefix in ((raw, changed), (raw[:-2] + b'xx', retained), (raw, retained[:1])):
            with self.assertRaises((ContractError, IntegrityError)):
                ArrivalReplay.restore(payload, callbacks=callbacks, retained_prefix=prefix, trace_id='toy')
        self.assertEqual(e['restore'], 'rejected')
        self.assertFalse(e['state_exposed'])
        self.assertEqual(e['all_additional_scenarios'], 'rejected_before_state_exposure')

    def test_registry_and_bounds(self):
        e = self.expected('F12-T34')
        driver = ArrivalReplay((market_callback('safe'),), trace_id='toy')
        with self.assertRaises(ContractError):
            driver.consume(fixture_trace((source(0, 1, decoder='missing'),))[0])
        self.assertEqual(driver.next_ordinal, 0)
        record = source(0, 1)
        with self.assertRaises(ContractError):
            fixture_trace((record,) * 4097)
        self.assertEqual(MAX_RECORDS, 4096)
        with self.assertRaises(ContractError):
            ArrivalReplay(tuple(market_callback('c' + str(n)) for n in range(65)), trace_id='toy')
        for changed in (record.record() | {'receipt_utc_ns': True}, record.record() | {'receipt_monotonic_ns': -1},
                        record.record() | {'schema_version': 2},
                        record.record() | {'payload': record.payload | {'raw_sha256': '0' * 64}}):
            with self.assertRaises((ContractError, IntegrityError)):
                ArrivalRecord.from_record(changed)
        with self.assertRaises(ContractError):
            self.replay((source(0, 1, receipt=100, monotonic=100), source(1, 2, receipt=101, monotonic=99)))
        self.assertEqual(e['unknown_callback'], 'rejected_before_advance')
        self.assertEqual(e['overflow'], 'explicit_saturation')
        self.assertEqual(len(driver.observations), e['silent_evictions'])

    def test_unknown_drop_denominator(self):
        e = self.expected('F12-T35')
        drops = drop_summary(('a', 'b', 'c', 'a', 'b'), source_id='fixture', generation='A', window_id='W', identity_contract='supplied-provider-delivery')
        summary = latency_summary((), source_id='fixture', session_id='toy', method='source_to_receipt', provenance='actual_capture')
        for key in ('drop_rate', 'reason', 'unique_received', 'duplicate_receipts'):
            self.assertEqual(drops[key], e[key])
        for key in ('p50', 'p95', 'p99'):
            self.assertEqual(summary[key], e[key])
        record = source(0, 1, receipt=8, event=10, provenance='actual_capture')
        lag = receipt_lag(record, source_id='fixture', session_id='toy')
        actual = latency_summary((lag,), source_id='fixture', session_id='toy', method='source_to_receipt', provenance='actual_capture')
        self.assertEqual(lag['value_ns'], e['utc_lag_signed_diagnostic'])
        self.assertEqual(lag['value_ns'] == 0, e['clamped_to_zero'])
        self.assertEqual(actual['actual_qualified_count'], e['actual_qualified_samples_without_sync_evidence'])
        with self.assertRaises(IntegrityError):
            drop_summary(('a', 'b'), source_id='fixture', generation='A', window_id='W', identity_contract='provider-id',
                         expected_count=1, expected_evidence_id='small-universe')

    def test_semantic_versus_transport(self):
        e = self.expected('F12-T36')
        a, b = self.replay((source(0, 5, receipt=10),)), self.replay((source(0, 5, receipt=12),))
        result = compare_observations(a.observations[0], b.observations[0])
        self.assertEqual(result['semantic_equal'], e['semantic_equal'])
        self.assertEqual(result['timing_equal'], e['timing_equal'])
        self.assertEqual(result['parity'], e['unconditional_parity'])
        self.assertEqual(result['difference_kind'], e['difference_kind'])
        self.assertNotEqual(a.observations[0]['transport'], b.observations[0]['transport'])

    def test_repair_boundaries(self):
        # Concrete assertions supplement the frozen cases without changing them.
        record = source(0, 1)
        driver = self.replay((record,))
        for key, value in (('callbacks', ()), ('trace_id', 'other'), ('definition', 'other'), ('policy_version', 'other')):
            with self.assertRaises(ContractError):
                setattr(driver, key, value)
        bad = arrival_module.CommittedArrival(record, '0' * 64, 'synthetic_fixture', 'fixture:toy')
        with self.assertRaises(IntegrityError):
            driver.consume(bad)
        with self.assertRaises(ContractError):
            arrival_module.CommittedArrival(record, record.sha256, 'durable_local_journal', '/invented')
        with self.assertRaises(ContractError):
            quality_callback(quality_bindings(('bbo',)), entry_fields=['bbo'])
        for changed in (record.record() | {'provenance': []}, record.record() | {'trace_id': '\ud800'},
                        decision(1).record() | {'payload': decision(1).payload | {'served_version_ids': [[]]}}):
            with self.assertRaises(ContractError):
                ArrivalRecord.from_record(changed)
        tx = transaction_source(10, 2)
        snapshot = ArrivalRecord.from_record(tx.record() | {'payload': tx.payload | {'semantic_kind': 'snapshot'}})
        with self.assertRaises(ContractError):
            self.replay((snapshot,), (transaction_callback(),))
        with self.assertRaises(ContractError):
            self.replay((record, source(1, 2, instrument='NQ')))
        with self.assertRaises(ContractError):
            delay_one((source(2, 1), source(1, 2)), seed=7, target_utc_ns=3, target_monotonic_ns=3)
        with self.assertRaises(ContractError):
            delay_one((record, source(1, 2, trace_id='other')), seed=7, target_utc_ns=3, target_monotonic_ns=3)
        for callbacks, original in (((transaction_callback(),), tx), ((publication_callback(),), published_source(10, 'v1')),
                                     ((order_callback((order_spec(),), account_id='A'),), ack(14))):
            actual = ArrivalRecord.from_record(original.record() | {'provenance': 'actual_capture'})
            with tempfile.TemporaryDirectory() as directory:
                with RawArrivalJournal(Path(directory) / 'actual.bin') as journal:
                    committed, _ = journal.append(actual)
                    trial = ArrivalReplay(callbacks, trace_id='toy')
                    with self.assertRaises(ContractError):
                        trial.consume(committed)
                    self.assertEqual(trial.next_ordinal, 0)
                    self.assertEqual(journal.records, (actual,))
        first = ack(20, state='cancelled', ack_id='a')
        conflict = ack(21, economic_known=20, state='rejected', ack_id='b')
        with self.assertRaises(IntegrityError):
            self.replay((first, conflict), (order_callback((order_spec(),), account_id='A'),))
        fill = BrokerEvent('initial-fill', 'O', 'fill', 30, 11, 'fixture', execution_id='initial-exec', filled_quantity=1, fill_ticks=100)
        state = self.replay((ack(14, economic_known=20),),
            (order_callback((order_spec(),), account_id='A', initial_events=(fill,)),)).states['orders']
        self.assertEqual(state['stale_rejections'], 1)
        self.assertEqual(state['positions'], {'ES': 1})
        bad_start = complete(20, 'v1', start=9)
        with self.assertRaises(ContractError):
            self.replay((published_source(10, 'v1'), bad_start), (publication_callback(),))
        timer1 = timer(15)
        timer2 = ArrivalRecord.from_record(timer(16).record() | {'payload': timer1.payload | {'due_monotonic_ns': 14}})
        with self.assertRaises(IntegrityError):
            self.replay((timer1, timer2))
        sample = receipt_lag(source(1, 1, event=0), source_id='fixture', session_id='toy', comparable_clock_evidence_id='fixture-clock', uncertainty_ns=0)
        summary = latency_summary((sample, sample), source_id='fixture', session_id='toy', method='source_to_receipt', provenance='synthetic_fixture')
        self.assertEqual((summary['n'], summary['duplicate_samples']), (1, 1))
        with self.assertRaises(IntegrityError):
            latency_summary((sample | {'actual_qualified': True},), source_id='fixture', session_id='toy', method='source_to_receipt', provenance='synthetic_fixture')
        with self.assertRaises(ContractError):
            receipt_lag(record, source_id='mislabelled', session_id='toy')
        connect = lambda at, generation, status: marker('connection', at, {'source_id': 'fixture', 'generation': generation, 'status': status, 'reason': 'fixture'})
        outage = self.replay((record, connect(1, 'A', 'disconnected'), connect(2, 'A', 'disconnected')))
        self.assertEqual(outage.control['sources']['fixture']['gap_started_ordinal'], 1)
        with self.assertRaises(ContractError):
            self.replay((record, connect(1, 'B', 'connected'), connect(2, 'A', 'connected')))
        with self.assertRaises(ContractError):
            self.replay((record, marker('boot', 1, {'previous_boot_id': 'A', 'new_boot_id': 'A'})))
        q = quality_source(10, 'bbo', 1, observed=10)
        body = json.loads(q.raw_bytes); del body['available_operations']
        with self.assertRaises(ContractError):
            self.replay((source(10, raw=encoded(body), decoder='quality', event=10, source_id='bbo-source'),),
                        (quality_callback(quality_bindings(('bbo',)), entry_fields=('bbo',)),))
        with self.assertRaises(IntegrityError):
            self.replay((published_source(10, 'v1'), complete(20, 'v1'), complete(21, 'v1', start=11)), (publication_callback(),))
        first_timer = timer(15, callback='publication')
        duplicate_timer = ArrivalRecord.from_record(timer(16, callback='publication').record() | {'payload': first_timer.payload})
        published = self.replay((first_timer, duplicate_timer), (publication_callback(),))
        self.assertEqual(published.states['publication']['timers'], [first_timer.payload['timer_id']])
        # Full raw receipt survives a semantic sequence violation; replay rejects it.
        records = (source(0, 1, provider_sequence=5), source(1, 2, provider_sequence=4))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sequence.bin'
            with RawArrivalJournal(path) as journal:
                for row in records:
                    journal.append(row)
                with self.assertRaises(ContractError):
                    ArrivalReplay((market_callback(),), trace_id='toy').consume_all(journal.committed)
            self.assertEqual(inspect_journal(path).records, records)
            empty = Path(directory) / 'empty.bin'; empty.write_bytes(b'')
            with self.assertRaises(JournalCorruption):
                RawArrivalJournal(empty)
            self.assertEqual(empty.read_bytes(), b'')
        # Full and partial writes poison the handle without decoder execution.
        for partial in (False, True):
            calls = []
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'failed.bin'
                with RawArrivalJournal(path) as journal:
                    def broken(file, raw):
                        if partial:
                            file.write(raw[:7])
                        raise OSError('injected write failure')
                    with patch.object(arrival_module, '_write_all', broken):
                        with self.assertRaises(UncertainCommit):
                            journal.append_and_decode(record, calls.append)
                    with self.assertRaises(UncertainCommit):
                        journal.append(record)
                    self.assertEqual(calls, [])
                    self.assertEqual(journal.records, ())
                inspection = inspect_journal(path)
                self.assertEqual(bool(inspection.tail), partial)
        def malformed(state, record):
            state['value'] = 10
            return state, [{'transport': {}}]
        callback = CallbackSpec('market', content_hash('malformed'), frozenset({'source'}), 'Counter.v1', {'value': 0}, malformed)
        trial = ArrivalReplay((callback,), trace_id='toy'); before = trial.checkpoint()
        with self.assertRaises(ContractError):
            trial.consume(fixture_trace((record,))[0])
        self.assertEqual(trial.checkpoint(), before)
        self.assertEqual((trial.stats['callback_attempts'], trial.stats['callback_calls']), (1, 0))
        # Recorded actions cannot be hidden by callback projections.
        a = self.replay((decision(1),)).observations[0]
        changed = ArrivalRecord.from_record(decision(1).record() | {'payload': decision(1).payload | {'action': 'buy'}})
        b = self.replay((changed,)).observations[0]
        self.assertFalse(compare_observations(a, b)['semantic_equal'])
        a = self.replay((source(1, 1),)).observations[0]
        b = self.replay((source(1, 2),)).observations[0]
        self.assertTrue(compare_observations(a, b)['numeric_differences'])
        b = self.replay((source(1, 1, definition='other'),)).observations[0]
        self.assertFalse(compare_observations(a, b)['semantic_equal'])
        # Fail closed on live effects or clock acquisition in the deterministic fold.
        with ExitStack() as stack:
            for target in ('time.time', 'time.time_ns', 'time.sleep', 'time.monotonic', 'time.monotonic_ns',
                           'threading.Thread', 'socket.socket', 'trading_research.execution.orders.OrderLedger.submit'):
                stack.enter_context(patch(target, side_effect=AssertionError('forbidden live boundary: ' + target)))
            self.replay((source(1, 1), timer(2), decision(3)))
            self.replay((ack(14),), (order_callback((order_spec(),), account_id='A'),))

    def test_local_resource_measurements(self):
        # Measurements are collected outside candidate transitions and never
        # enter replay/checkpoint identity. RSS is process peak, not a delta.
        callback_totals = {'cpu_seconds': 0.0, 'wall_seconds': 0.0, 'calls': 0}
        base = market_callback()
        def measured(state, record):
            cpu, wall = time.process_time(), time.perf_counter()
            try:
                return base.transition(state, record)
            finally:
                callback_totals['cpu_seconds'] += time.process_time() - cpu
                callback_totals['wall_seconds'] += time.perf_counter() - wall
                callback_totals['calls'] += 1
        spec = CallbackSpec(base.id, base.version_hash, base.accepted_kinds, base.state_schema, base.initial_state,
            measured, semantic_projection=base.semantic_projection, projection_id=base.projection_id)
        records = tuple(source(i, i) for i in range(8))
        cpu, wall = time.process_time(), time.perf_counter()
        driver = self.replay(records, (spec,))
        restored = ArrivalReplay.restore(driver.checkpoint(), callbacks=(spec,), retained_prefix=fixture_trace(records), trace_id='toy')
        driver_measure = {'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall,
            'process_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'counts': dict(restored.stats), 'scope': '8 synthetic rows; replay plus full-prefix restore; includes nested callback work'}
        cpu, wall = time.process_time(), time.perf_counter()
        with tempfile.TemporaryDirectory() as directory:
            with RawArrivalJournal(Path(directory) / 'measured.bin') as journal:
                for row in records:
                    journal.append_and_decode(row, lambda raw: json.loads(raw))
                io = dict(journal.stats)
        journal_measure = {'cpu_seconds': time.process_time() - cpu, 'wall_seconds': time.perf_counter() - wall,
            'process_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'counts': io, 'scope': 'local POSIX constructor, 8 durable appends/decodes and cleanup; IO counts cover append/decode only'}
        callback_measure = {**callback_totals, 'process_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'scope': 'nested callback transition time for original replay and prefix validation; RSS is shared process peak'}
        self.assertEqual((driver.stats['callback_attempts'], restored.stats['callback_calls'], restored.stats['restore_validation_records']), (8, 8, 8))
        self.assertEqual((io['write_attempts'], io['committed_appends'], io['decode_attempts']), (8, 8, 8))
        self.assertEqual(callback_totals['calls'], 16)
        for measurement in (driver_measure, journal_measure, callback_measure):
            self.assertGreaterEqual(measurement['cpu_seconds'], 0)
            self.assertGreaterEqual(measurement['wall_seconds'], 0)
            self.assertGreater(measurement['process_peak_rss_bytes'], 0)
        ENGINEERING_METRICS['local_resource_measurements'] = {'driver': driver_measure, 'callback': callback_measure,
            'journal': journal_measure, 'actual_live_evidence': False,
            'scope': 'measured local engineering work; CPU scopes overlap; never a live transport latency distribution'}
