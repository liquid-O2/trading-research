"""F05 frozen synthetic cases: raw receipt oracle, exact deltas and consumers."""
from dataclasses import asdict, replace
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
from itertools import permutations
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from references.transactions_literal import aggregate as literal_aggregate, replay as literal_replay
from trading_research.data.transactions import (ConditionContract, ConditionRule, MBPInstrumentMapping, NonTransaction, TransactionDelta,
    TransactionKey, TransactionLedger, TransactionReceipt, TransactionValue, transaction_from_mbp)
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.contracts import InstrumentKey
from trading_research.foundations.instruments import InstrumentDefinition, instrument_identity
from trading_research.foundations.bars import Watermark, WindowCoverage, bar_reference
from trading_research.foundations.time import AvailabilityBasis, Clocks
from trading_research.foundations.units import NQ_REFERENCE, Ticks
from trading_research.measurements.auction import bounded_dwell, tpo_reference
from trading_research.measurements.footprint import footprint
from trading_research.measurements.tape import Cohort, RowGrid, TradeLedger, cvd_bar, cvd_reference, profile_reference, vwap_two_pass
from trading_research.measurements.transaction_reducers import (TransactionReducer, TransactionTapeView,
    restore_transaction_checkpoint, trade_from_transaction, transaction_checkpoint)
from trading_research.operations.artifacts import canonical_json
from trading_research.runtime.merge import PartitionMerge, ReplayEvent
from trading_research.runtime.ports import reference_graph
from tests.test_market_data import event as mbp_event

GOLDEN = json.loads((Path(__file__).parent / 'golden/f05-transactions.json').read_text())
INSTRUMENT = 'SYNTH-1'


def key(root='x', **changes):
    values = dict(provider='synthetic', dataset='synthetic/trades', publisher_or_venue='venue', channel='channel',
                  source_session='session', instrument_key=INSTRUMENT, ownership_id=root,
                  ownership_basis='provider_transaction', ownership_evidence_id='identity-v1')
    return TransactionKey(**{**values, **changes})


def value(*, price=100, ticks='same', quantity=3, side=1, event_at=5, **changes):
    values = dict(event_at=event_at, price_decimal=None if price is None else Decimal(str(price)),
                  price_ticks=price if ticks == 'same' else ticks, quantity=quantity, quantity_unit='contracts',
                  reported_aggressor=side, aggregation_unit='provider-reported-trade-record', instrument_kind='futures_outright',
                  terms_version='synthetic-terms-v1', usd_multiplier=Decimal(1), money_role='synthetic_notional_USD',
                  volume_eligibility=True, directional_eligibility=True, condition_contract_id='synthetic-condition-v1',
                  raw_condition='NORMAL', quality_reasons=(), history_complete=True, source_order=None)
    return TransactionValue(**{**values, **changes})


def receipt(root='x', version='x0', *, op='insert', previous=None, known=10, data='default', identity=None, receipt_id=None):
    identity = key(root) if identity is None else identity
    data = (None if op == 'cancel' else value()) if data == 'default' else data
    rid = receipt_id or 'r-' + version
    raw = ('synthetic-original:' + version).encode()
    return TransactionReceipt(rid, 'source-' + version, identity, version, previous, op,
                              Clocks(None if data is None else data.event_at, known, 'receipt-content-v1',
                                     AvailabilityBasis.RECEIVED, received_at=known),
                              'synthetic-source-row:' + rid, hashlib.sha256(raw).hexdigest(), raw, data,
                              data.condition_contract_id if data is not None else 'synthetic-condition-v1', 'identity-v1')


def reducer(**changes):
    return TransactionReducer(**{**dict(instrument=INSTRUMENT, instrument_kind='futures_outright', quantity_unit='contracts',
        terms_version='synthetic-terms-v1', aggregation_unit='provider-reported-trade-record', usd_multiplier=Decimal(1),
        money_role='synthetic_notional_USD'), **changes})


def mbp_mapping(event):
    definition = InstrumentDefinition(InstrumentKey('synthetic', 'synthetic-venue', str(event.instrument_id),
        'NQH0', 'NQ', NQ_REFERENCE.definition_version, 1000),
        Clocks(0, 0, 'synthetic-definition', AvailabilityBasis.RECEIVED, received_at=0,
               valid_from=0, valid_until=1000), 'future', NQ_REFERENCE.usd_per_point, NQ_REFERENCE.tick_size)
    return MBPInstrumentMapping(event.address.dataset_id, event.address.schema_version,
                                definition, 'synthetic-mapping-evidence')


def mbp_key(event, mapping):
    return key(dataset=event.address.dataset_id, instrument_key=instrument_identity(mapping.definition),
               publisher_or_venue=None if event.publisher_id is None else str(event.publisher_id), channel=None,
               source_session=event.address.acquisition_version, ownership_id=event.address.id,
               ownership_basis='source_row')


def timeline():
    result = []
    for row in GOLDEN['arithmetic_timeline']['inputs']:
        data = None if row['op'] == 'cancel' else value(price=row['price'], quantity=row['quantity'], side=row['side'], event_at=row['event_at'])
        result.append((receipt(row['root'], row['version'], op=row['op'], previous=row['predecessor'], known=row['known_at'],
                               data=data, receipt_id=row['receipt_id']), row['completion_at']))
    return tuple(result)


def build(rows, *, state=None, consumer=None):
    state = TransactionLedger() if state is None else state
    consumer = reducer() if consumer is None else consumer
    for row, completed in rows:
        admission = state.admit(row, actual_completion_at=completed)
        consumer.apply_batch(admission.deltas)
    return state, consumer


class TransactionTests(unittest.TestCase):
    def test_frozen_timeline_matches_literal_raw_replay_and_all_exact_channels(self):
        rows = timeline()
        ledger, online = build(rows)
        for expected in GOLDEN['arithmetic_timeline']['snapshots']:
            cut = expected['cut']
            with self.subTest(cut=cut):
                actual = online.snapshot(cut)
                literal = literal_aggregate(literal_replay(rows, cut=cut), instrument=INSTRUMENT, cut=cut)
                for name in ('live_versions', 'buy', 'sell', 'unknown', 'total', 'signed', 'prints', 'profile',
                             'tick_first', 'tick_second', 'notional', 'signed_notional', 'vwap', 'variance', 'signed_bounds'):
                    self.assertEqual(getattr(actual, name), literal[name], name)
                    if name in expected:
                        wanted = expected[name]
                        if name in ('notional', 'signed_notional'):
                            wanted = Fraction(wanted)
                        elif name in ('vwap', 'variance'):
                            wanted = None if wanted is None else Fraction(*wanted)
                        elif name in ('live_versions', 'signed_bounds'):
                            wanted = tuple(wanted)
                        elif name == 'profile':
                            wanted = tuple(tuple(row) for row in wanted)
                        self.assertEqual(getattr(actual, name), wanted, name)
                self.assertEqual(ledger.asof(instrument=INSTRUMENT, cut=cut), literal_replay(rows, cut=cut).live)
        revision = next(d for d in ledger.deltas if d.next_version_id == 'x1')
        self.assertEqual((revision.before_value.quantity, revision.after_value.quantity), (3, 2))
        self.assertEqual(revision.affected_event_intervals, ((5, 6),))
        self.assertTrue({'quantity', 'reported_aggressor', 'price_ticks', 'lineage'} <= revision.affected_fields)

    def test_legitimate_same_time_prints_duplicates_and_conflicts_preserve_multiplicity(self):
        first, second = receipt('p', 'p0'), receipt('q', 'q0')
        ledger, online = build(((first, 10), (second, 10)))
        before = ledger.checkpoint()
        self.assertEqual(ledger.admit(first, actual_completion_at=99).status, 'duplicate_receipt')
        self.assertEqual(ledger.checkpoint(), before)
        copied = replace(first, receipt_id='copy', source_address='copied-locator',
                         clocks=replace(first.clocks, known_at=12, received_at=12))
        duplicate = ledger.admit(copied, actual_completion_at=12)
        self.assertEqual((duplicate.status, duplicate.deltas), ('duplicate_version', ()))
        snap = online.snapshot(12)
        self.assertEqual((snap.prints, snap.buy, snap.total, snap.notional), (2, 6, 6, Fraction(600)))
        before = ledger.checkpoint()
        for conflict in (replace(first, source_event_id='changed'),
                         replace(copied, receipt_id='bad-revision', value=value(quantity=4))):
            with self.assertRaises(IntegrityError):
                ledger.admit(conflict, actual_completion_at=12)
        self.assertEqual(ledger.checkpoint(), before)
        self.assertEqual(TransactionLedger.restore(before).checkpoint(), before)

    def test_original_delivered_after_pending_correction_uses_actual_resolution_time(self):
        correction = receipt(version='x1', op='revise', previous='x0', known=10,
                             data=value(price=101, quantity=2, side=-1))
        original = receipt(known=20)
        ledger = TransactionLedger()
        pending = ledger.admit(correction, actual_completion_at=10)
        self.assertEqual((pending.status, pending.pending_version_ids, pending.deltas), ('pending_dependency', ('x1',), ()))
        ledger = TransactionLedger.restore(ledger.checkpoint())
        committed = ledger.admit(original, actual_completion_at=22)
        self.assertEqual(tuple(d.next_version_id for d in committed.deltas), ('x0', 'x1'))
        self.assertEqual(tuple(d.known_at for d in committed.deltas), (22, 22))
        self.assertEqual(ledger.asof(instrument=INSTRUMENT, cut=21), ())
        self.assertEqual(ledger.pending(cut=21), ('x1',))
        online = reducer()
        online.apply_batch(committed.deltas)
        self.assertEqual((online.snapshot(22).total, online.snapshot(22).signed, online.snapshot(22).notional),
                         (2, -2, Fraction(202)))
        self.assertEqual(ledger.asof(instrument=INSTRUMENT, cut=22), literal_replay(((correction, 10), (original, 22)), cut=22).live)

    def test_pending_cancel_and_missing_middle_predecessor_resolve_without_resurrection(self):
        for prior in (False, True):
            with self.subTest(original_already_present=prior):
                ledger, online = TransactionLedger(), reducer()
                if prior:
                    online.apply_batch(ledger.admit(receipt(), actual_completion_at=10).deltas)
                    pending = receipt(version='x2', op='cancel', previous='x1', known=20)
                    trigger = receipt(version='x1', op='revise', previous='x0', known=30, data=value(price=101, quantity=2, side=-1))
                else:
                    pending = receipt(version='x1', op='cancel', previous='x0', known=10)
                    trigger = receipt(known=20)
                self.assertEqual(ledger.admit(pending, actual_completion_at=pending.clocks.known_at).deltas, ())
                self.assertEqual(online.snapshot(pending.clocks.known_at).total, 3 if prior else 0)
                committed = ledger.admit(trigger, actual_completion_at=trigger.clocks.known_at)
                self.assertEqual(len(committed.deltas), 2)
                online.apply_batch(committed.deltas)
                self.assertEqual((online.snapshot(trigger.clocks.known_at).total, ledger.pending()), (0, ()))
                self.assertEqual(ledger.asof(instrument=INSTRUMENT, cut=100), ())

    def test_forks_cycles_cross_root_and_reinstatement_fail_atomically(self):
        cases = [
            ((receipt(), receipt(version='x1', previous='x0', op='revise', known=20)),
             receipt(version='x2', previous='x0', op='revise', known=30), IntegrityError),
            ((receipt(),), receipt(version='second-insert', known=20), IntegrityError),
            ((receipt(),), receipt('y', 'y1', previous='x0', op='revise', known=20), ContractError),
            ((receipt(version='x1', previous='x2', op='revise', known=10),),
             receipt(version='x2', previous='x1', op='revise', known=20), ContractError),
            ((receipt(), receipt(version='x1', previous='x0', op='cancel', known=20)),
             receipt(version='x2', previous='x1', op='revise', known=30), ContractError)]
        for initial, invalid, failure in cases:
            with self.subTest(invalid=invalid.version_id, error=failure.__name__):
                ledger = TransactionLedger()
                for r in initial:
                    ledger.admit(r, actual_completion_at=r.clocks.known_at)
                before = ledger.checkpoint()
                with self.assertRaises(failure):
                    ledger.admit(invalid, actual_completion_at=invalid.clocks.known_at)
                self.assertEqual(ledger.checkpoint(), before)
                with self.assertRaises(failure):
                    literal_replay(tuple((r, r.clocks.known_at) for r in (*initial, invalid)), cut=100)

    def test_identical_value_revision_changes_lineage_and_event_time_moves_both_windows(self):
        ledger, online = build(((receipt(), 10),))
        prior = online.snapshot(10)
        same = receipt(version='x1', previous='x0', op='revise', known=20)
        admission = ledger.admit(same, actual_completion_at=20)
        self.assertEqual(admission.deltas[0].affected_fields, frozenset({'lineage'}))
        online.apply_batch(admission.deltas)
        self.assertEqual(online.snapshot(20).total, 3)
        self.assertNotEqual(prior.id, online.snapshot(20).id)
        self.assertEqual(prior, online.snapshot(10))
        moved = receipt(version='x2', previous='x1', op='revise', known=30, data=value(event_at=15))
        delta = ledger.admit(moved, actual_completion_at=30).deltas[0]
        self.assertEqual(delta.affected_event_intervals, ((5, 6), (15, 16)))
        early, late = reducer(start=0, end=10), reducer(start=10, end=20)
        for target in (early, late):
            target.apply_batch(ledger.deltas)
        self.assertEqual((early.snapshot(10).total, late.snapshot(10).total), (3, 0))
        self.assertEqual((early.snapshot(30).total, late.snapshot(30).total), (0, 3))
        self.assertEqual(len(ledger.changes(instrument=INSTRUMENT, cut=30, start=10, end=20)), 1)

    def test_scope_identity_is_not_global_sequence_and_units_are_not_silently_changed(self):
        identities = (key('sequence7'), key('sequence7', instrument_key='SYNTH-2'),
                      key('sequence7', source_session='session2'), key('sequence7', channel='channel2'))
        self.assertEqual(len({k.id for k in identities}), 4)
        ledger = TransactionLedger()
        for n, identity in enumerate(identities):
            ledger.admit(receipt(version=f'v{n}', identity=identity), actual_completion_at=10)
        self.assertEqual(ledger.metrics()['version_count'], 4)
        with self.assertRaises(ContractError):
            ledger.admit(receipt(version='unit-change', identity=identities[0], op='revise', previous='v0', known=20,
                                 data=value(usd_multiplier=Decimal(2))), actual_completion_at=20)
        for quantity in (0, -1):
            with self.assertRaises(ContractError):
                value(quantity=quantity)
        spread = receipt(data=value(instrument_kind='spread', quantity_unit='spread_units'))
        spread_ledger = TransactionLedger()
        batch = spread_ledger.admit(spread, actual_completion_at=10).deltas
        target = reducer()
        before = target.checkpoint()
        with self.assertRaises(ContractError):
            target.apply_batch(batch)
        self.assertEqual(target.checkpoint(), before)

    def test_unpriced_profiles_and_exact_option_premium_are_separate_operation_channels(self):
        rows = ((receipt('a', 'a0', data=value(price=None, ticks=None)), 10),
                (receipt('b', 'b0', data=value(price='100.1', ticks=None, quantity=2, side=None)), 10))
        _, online = build(rows)
        snap = online.snapshot(10)
        self.assertEqual((snap.total, snap.buy, snap.unknown, snap.profile, snap.profile_unpriced_volume,
                          snap.money_unpriced_volume, snap.notional), (5, 3, 2, (), 5, 3, Fraction('200.2')))
        initial = value(price='1.25', ticks=125, quantity=2, instrument_kind='single_option', usd_multiplier=Decimal(100), money_role='option_premium_USD')
        revised = replace(initial, price_decimal=Decimal('1.50'), price_ticks=150, quantity=3, reported_aggressor=-1)
        target = reducer(instrument_kind='single_option', usd_multiplier=Decimal(100), money_role='option_premium_USD')
        with localcontext() as context:
            context.prec = 2
            ledger, target = build(((receipt(data=initial), 10),
                                    (receipt(version='x1', previous='x0', op='revise', known=20, data=revised), 20)), consumer=target)
        self.assertEqual((target.snapshot(10).notional, target.snapshot(20).notional, target.snapshot(20).signed_notional),
                         (Fraction(250), Fraction(450), Fraction(-450)))

    def test_synthetic_conditions_preserve_unknown_observation_and_do_not_create_native_rules(self):
        contract = ConditionContract('synthetic', 'quantpad11-v1', 0, 1000, 'synthetic-only-evidence',
            (ConditionRule('NORMAL', True, True, 'regular'), ConditionRule('AUCTION', True, False, 'auction_unknown_sign'),
             ConditionRule('EXCLUDED', False, False, 'excluded')), True)
        unknown = contract.decide('UNLISTED', event_at=10)
        self.assertEqual((unknown.volume_eligible, unknown.directional_eligible, unknown.reason),
                         (None, False, 'unresolved_condition_contract'))
        raw = value(quantity=7, volume_eligibility=None, directional_eligibility=False,
                    condition_contract_id=contract.id, raw_condition='UNLISTED')
        ledger, online = build(((receipt(data=raw), 10),))
        snap = online.snapshot(10)
        self.assertEqual((snap.observed_volume, snap.condition_unresolved_volume, snap.total, snap.certified_total, snap.signed_bounds),
                         (7, 7, 0, None, None))
        with self.assertRaises(DependencyUnavailable):
            TransactionTapeView(ledger).asof(instrument=INSTRUMENT, cut=10)
        with self.assertRaises(ContractError):
            replace(contract, provider='native-OPRA')
        with self.assertRaises(ContractError):
            contract.decide('NORMAL', event_at=1000)

    def test_mbp_adapter_keeps_action_side_flags_raw_identity_and_snapshots_distinct(self):
        contract = ConditionContract('synthetic', 'quantpad11-v1', 0, 1000, 'synthetic-only',
                                     (ConditionRule('NORMAL', True, True, 'fixture'),), True)
        wrapped = []
        for n, (action, side, flags, size) in enumerate((('T','B',0,3), ('T','A',132,2), ('T','N',0,4),
                                                        ('A','B',128,5), ('C','A',128,6), ('T','B',168,4))):
            event = mbp_event(n, action=action, side=side, flags=flags, size=size)
            mapping = mbp_mapping(event)
            ownership = mbp_key(event, mapping)
            result = transaction_from_mbp(event, root_key=ownership, mapping=mapping, terms=NQ_REFERENCE, instrument_kind='futures_outright',
                money_role='futures_notional_USD', condition_contract=contract, condition_code='NORMAL', order=None, history_complete=True)
            if n < 3:
                self.assertEqual((result.receipt_id, result.source_event_id), (event.id, event.id))
                self.assertEqual(json.loads(result.raw_payload)['raw_fields_hex'], event.raw_fields.hex())
            else:
                self.assertIsInstance(result, NonTransaction)
            wrapped.append(result)
        target = reducer(instrument=wrapped[0].root_key.instrument_key, terms_version=NQ_REFERENCE.definition_version,
                         usd_multiplier=Decimal(20), money_role='futures_notional_USD')
        ledger = TransactionLedger()
        for r in wrapped[:3]:
            target.apply_batch(ledger.admit(r, actual_completion_at=r.clocks.known_at).deltas)
        snap = target.snapshot(100)
        self.assertEqual((snap.buy, snap.sell, snap.unknown, snap.total, snap.signed, snap.signed_bounds), (3,2,4,9,1,None))
        self.assertEqual(wrapped[-1].reason, 'snapshot_initialization')
        self.assertNotIn('participant_identity', asdict(wrapped[0].value))
        self.assertIsNone(wrapped[2].value.reported_aggressor)

    def test_auction_exclusion_and_unresolved_condition_keep_separate_mass(self):
        contract = ConditionContract('synthetic', 'fixture', 0, 100, 'synthetic-only',
            (ConditionRule('AUCTION', True, False, 'auction_sign_unknown'),
             ConditionRule('EXCLUDED', False, False, 'excluded_from_volume')), True)
        inputs = []
        for root, code, quantity in (('auction','AUCTION',5), ('excluded','EXCLUDED',2), ('unknown','UNKNOWN',7)):
            decision = contract.decide(code,event_at=5)
            data = value(quantity=quantity,volume_eligibility=decision.volume_eligible,
                         directional_eligibility=decision.directional_eligible,
                         condition_contract_id=contract.id,raw_condition=code)
            inputs.append((receipt(root,root+'0',data=data),10))
        ledger, target = build(tuple(inputs))
        snap = target.snapshot(10)
        self.assertEqual((snap.observed_volume,snap.total,snap.unknown,snap.excluded_volume,
                          snap.condition_unresolved_volume,snap.signed_bounds), (14,5,5,2,7,None))
        cancel = receipt('unknown','unknown1',op='cancel',previous='unknown0',known=20)
        target.apply_batch(ledger.admit(cancel,actual_completion_at=20).deltas)
        snap = target.snapshot(20)
        self.assertEqual((snap.observed_volume,snap.total,snap.excluded_volume,snap.signed_bounds), (7,5,2,(-5,5)))

    def test_record_byte_pending_resolution_and_consumer_bounds_are_atomic(self):
        original = receipt()
        ledger = TransactionLedger(max_records=5)
        ledger.admit(original, actual_completion_at=10)
        self.assertEqual(ledger.metrics()['retained_records'], 5)
        before = ledger.checkpoint()
        with self.assertRaises(ContractError):
            ledger.admit(receipt('y', 'y0'), actual_completion_at=10)
        self.assertEqual(ledger.checkpoint(), before)
        state = json.loads(before)['state']
        bytes_expected = len(json.dumps(state, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())
        exact = TransactionLedger(max_bytes=bytes_expected)
        exact.admit(original, actual_completion_at=10)
        with self.assertRaises(ContractError):
            TransactionLedger(max_bytes=bytes_expected-1).admit(original, actual_completion_at=10)
        pending = receipt(version='x1', previous='x0', op='revise')
        narrow = TransactionLedger(max_pending=1, max_resolution_deltas=1)
        narrow.admit(pending, actual_completion_at=10)
        before = narrow.checkpoint()
        with self.assertRaises(ContractError):
            narrow.admit(receipt('y', 'y1', previous='y0', op='cancel'), actual_completion_at=10)
        with self.assertRaises(ContractError):
            narrow.admit(receipt(known=20), actual_completion_at=20)
        self.assertEqual(narrow.checkpoint(), before)
        target = reducer(max_profile_rows=1, max_snapshot_versions=1)
        target.apply_batch(ledger.deltas)
        target.snapshot(10)
        before = target.checkpoint()
        with self.assertRaises(ContractError):
            target.snapshot(11)
        other = TransactionLedger()
        delta = other.admit(receipt('y', 'y0', data=value(price=101)), actual_completion_at=10).deltas
        with self.assertRaises(ContractError):
            target.apply_batch(delta)
        self.assertEqual(target.checkpoint(), before)

    def test_forged_delta_and_checkpoints_reject_without_partial_state(self):
        ledger, online = build(timeline()[:2])
        correction = ledger.admit(timeline()[2][0], actual_completion_at=20).deltas[0]
        before = online.checkpoint()
        with self.assertRaises(IntegrityError):
            online.apply(replace(correction, before_value=value(quantity=99)))
        with self.assertRaises(IntegrityError):
            online.apply(replace(correction, prior_version_id='skipped'))
        self.assertEqual(online.checkpoint(), before)
        forged = correction.record()
        forged['after_value']['quantity'] = 99
        with self.assertRaises(IntegrityError):
            TransactionDelta.restore(forged)
        online.apply(correction)
        bundle = transaction_checkpoint(ledger, {'flow': online})
        restored, consumers = restore_transaction_checkpoint(bundle)
        self.assertEqual(transaction_checkpoint(restored, consumers), bundle)
        broken = json.loads(ledger.checkpoint()); broken['metrics']['retained_records'] += 1
        with self.assertRaises(IntegrityError):
            TransactionLedger.restore(canonical_json(broken))
        broken = json.loads(online.checkpoint()); broken['state']['totals']['buy'] += 1
        with self.assertRaises(IntegrityError):
            TransactionReducer.restore(canonical_json(broken))
        with self.assertRaises(IntegrityError):
            transaction_checkpoint(ledger, {'skipped-consumer': reducer()})

    def test_future_prefix_and_same_cut_insertion_permutations_preserve_snapshots(self):
        rows = timeline()
        baseline_ledger, baseline = build(rows)
        expected = {cut: baseline.snapshot(cut) for cut in (9,10,20,25,30,40)}
        for prefix_cut in expected:
            for order in permutations(rows[:2]):
                admitted = tuple(pair for pair in (*order, *rows[2:]) if pair[1] <= prefix_cut)
                with self.subTest(cut=prefix_cut, first=order[0][0].version_id):
                    ledger, target = build(admitted)
                    self.assertEqual(target.snapshot(prefix_cut), expected[prefix_cut])
                    self.assertEqual(ledger.asof(instrument=INSTRUMENT, cut=prefix_cut),
                                     baseline_ledger.asof(instrument=INSTRUMENT, cut=prefix_cut))

    def test_finite_cvd_profile_footprint_vwap_bars_tpo_and_dwell_consumers(self):
        ledger, online = build(timeline())
        view = TransactionTapeView(ledger)
        grid = RowGrid(1, 0, 'synthetic-grid')
        coverage = WindowCoverage(INSTRUMENT, 0, 10, ((0,10),), 10, 'synthetic-full')
        expected_case = next(c for c in GOLDEN['cases'] if c['id']=='F05-G26')['expected']
        for cut in (10,20):
            trades = view.asof(instrument=INSTRUMENT, cut=cut)
            expected, snap = expected_case[f'cut{cut}'], online.snapshot(cut)
            cvd = cvd_reference(trades, coverage_complete=True)
            profile = profile_reference(trades, grid=grid, anchor_id='fixed', coverage_complete=True)
            fp = footprint(trades, row_ticks=1)
            self.assertEqual((cvd.buy,cvd.sell,cvd.unknown,cvd.total), (snap.buy,snap.sell,snap.unknown,snap.total))
            self.assertEqual(profile.rows, snap.profile)
            self.assertEqual(tuple((r.price,r.buy,r.sell,r.unknown) for r in fp['rows']), snap.profile)
            self.assertEqual(vwap_two_pass(trades), (snap.vwap,snap.variance))
            bar = bar_reference(view, instrument=INSTRUMENT,start=0,end=10,cut=cut,definition_version='fixed',
                                coverage=coverage,watermark=Watermark(10,10,'watermark'))
            self.assertEqual((bar.volume,bar.high_ticks,bar.low_ticks,bar.prints),
                             tuple(expected[k] for k in ('bar_volume','bar_high','bar_low','bar_prints')))
            tpo = tpo_reference(view,instrument=INSTRUMENT,start=0,end=10,cut=cut,bracket_ns=5,grid=grid,
                                coverage=coverage,definition_version='tpo',minimum_brackets=2,watermark=Watermark(10,10,'w'))
            self.assertEqual(tpo.visits, tuple((p,tuple(b)) for p,b in expected['tpo_rows']))
            dwell = bounded_dwell(view,instrument=INSTRUMENT,start=0,end=10,cut=cut,stale_cap_ns=2,grid=grid)
            self.assertEqual(dwell.duration_by_row, tuple(tuple(r) for r in expected['dwell_rows']))
            self.assertEqual(dwell.missing_or_stale_duration_ns,expected['dwell_missing_duration'])
        old = TradeLedger()
        for t in view.asof(instrument=INSTRUMENT,cut=10):
            old.add(t)
        self.assertEqual(old.changes(instrument=INSTRUMENT,cut=10,start=0,end=10), ())
        self.assertEqual(bar_reference(old,instrument=INSTRUMENT,start=0,end=10,cut=10,definition_version='fixed',coverage=coverage),
                         bar_reference(view,instrument=INSTRUMENT,start=0,end=10,cut=10,definition_version='fixed',coverage=coverage))

    def test_f04_redelivery_after_consumer_commit_before_ack_is_idempotent(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary)/'merge.sqlite'
            domains = {'transactions':frozenset({'source'})}
            source = PartitionMerge(path,domains)
            rows = (receipt(), receipt(version='x1',op='revise',previous='x0',known=20,data=value(quantity=2,side=-1)))
            for n,r in enumerate(rows):
                source.append(ReplayEvent(r.receipt_id,'source',n,r.clocks,canonical_json(r.record())))
            source.advance('source',before=30,known_at=30,evidence_id='complete')
            batch = source.peek('transactions',at=30)
            ledger, target = TransactionLedger(), reducer()
            received = TransactionReceipt.restore(json.loads(batch.events[0].payload))
            target.apply_batch(ledger.admit(received,actual_completion_at=30).deltas)
            checkpoint = transaction_checkpoint(ledger,{'flow':target})
            reopened = PartitionMerge(path,domains)
            self.assertEqual(reopened.peek('transactions',at=30).id,batch.id)
            ledger, consumers = restore_transaction_checkpoint(checkpoint)
            self.assertEqual(ledger.admit(received,actual_completion_at=30).deltas,())
            self.assertEqual(consumers['flow'].snapshot(30).total,3)
            reopened.acknowledge(batch,at=30)
            next_batch = PartitionMerge(path,domains).peek('transactions',at=30)
            self.assertEqual(next_batch.known_at,20)

    def test_transaction_ports_preserve_raw_semantic_order_and_optional_vendor_isolation(self):
        graph = reference_graph()
        order = {name:i for i,name in enumerate(graph.order)}
        chain = ['F01.RAW','F06.RAW','F05.NORMALIZED','F05.TRANSACTIONS','F06.SEMANTIC','F07.ELIGIBLE','F09.BARS']
        self.assertEqual(sorted(chain,key=order.get),chain)
        edge = next(e for e in graph.ports['F06.SEMANTIC'].inputs if e.source=='F05.RECONCILIATION')
        self.assertTrue(edge.optional)
        self.assertNotIn('P10.EMERGENCY',graph.descendants(['F05.RECONCILIATION']))
        self.assertNotIn('O15.RAW_FLOW',graph.descendants(['O02.IV']))

    def test_configuration_cannot_mutate_or_reassign_and_snapshots_bind_definitions(self):
        ledger, target = build(((receipt(), 10),))
        prior = target.snapshot(10)
        checkpoints = ledger.checkpoint(), target.checkpoint()
        for state, name, changed in ((ledger, 'definition_version', 'changed'), (target, 'start', 9),
                                     (target, 'row_ticks', 3), (ledger, 'max_records', 1)):
            with self.subTest(state=type(state).__name__, field=name):
                with self.assertRaises(TypeError):
                    state.config[name] = changed
                with self.assertRaises(AttributeError):
                    state.config = {**state.config, name: changed}
        self.assertEqual((ledger.checkpoint(), target.checkpoint()), checkpoints)
        self.assertEqual(target.snapshot(10), prior)
        self.assertEqual(dict(prior.configuration)['start'], None)
        alternatives = (reducer(), reducer(start=1), reducer(row_ticks=2), reducer(grid_origin=1),
                        reducer(terms_version='other-terms'), reducer(usd_multiplier=Decimal(2)))
        empty = tuple(r.snapshot(10) for r in alternatives)
        self.assertEqual({s.total for s in empty}, {0})
        self.assertEqual(len({s.id for s in empty}), len(empty))
        self.assertEqual(len({s.configuration_hash for s in empty}), len(empty))
        # Coincident finite values also remain distinct definitions.
        wide = reducer(row_ticks=2)
        wide.apply_batch(ledger.deltas)
        self.assertEqual(wide.snapshot(10).profile, prior.profile)
        self.assertNotEqual(wide.snapshot(10).id, prior.id)

    def test_snapshot_restart_preserves_original_admitted_prefix_at_same_or_future_cut(self):
        for captured_cut, second_at in ((10, 10), (30, 20)):
            with self.subTest(captured_cut=captured_cut, second_at=second_at):
                ledger, target = build(((receipt('a', 'a0'), 10),))
                old = target.snapshot(captured_cut)
                target.apply_batch(ledger.admit(receipt('b', 'b0', known=second_at),
                                               actual_completion_at=second_at).deltas)
                later = target.snapshot(captured_cut)
                self.assertEqual((old.total, later.total), (3, 6))
                self.assertNotEqual(old.id, later.id)
                payload = transaction_checkpoint(ledger, {'flow': target})
                reopened, consumers = restore_transaction_checkpoint(payload)
                restored = consumers['flow']
                self.assertEqual(transaction_checkpoint(reopened, consumers), payload)
                self.assertEqual(restored._snapshots[old.id], old)
                self.assertEqual(restored._snapshots[later.id], later)
                self.assertEqual(restored.snapshot(captured_cut), later)

    def test_partial_pending_resolution_batch_cannot_publish_transient_mass(self):
        ledger, target = TransactionLedger(), reducer()
        ledger.admit(receipt(version='x1', op='cancel', previous='x0'), actual_completion_at=10)
        admission = ledger.admit(receipt(known=20), actual_completion_at=22)
        first, cancel = admission.deltas
        self.assertEqual(first.batch_versions, ('x0', 'x1'))
        self.assertEqual((first.batch_index, cancel.batch_index), (0, 1))
        self.assertEqual(first.batch_id, cancel.batch_id)
        initial = target.snapshot(22)
        before = target.checkpoint()
        for partial in ((first,), (cancel,), (cancel, first)):
            with self.assertRaises(IntegrityError):
                target.apply_batch(partial)
            self.assertEqual(target.checkpoint(), before)
        with self.assertRaises(IntegrityError):
            target.apply(first)
        self.assertEqual(target.checkpoint(), before)
        target.apply_batch(admission.deltas)
        self.assertEqual(target.snapshot(22).total, 0)
        self.assertNotEqual(target.snapshot(22).id, initial.id)
        after = target.checkpoint()
        self.assertEqual(target.apply_batch(admission.deltas), 0)
        self.assertEqual(target.checkpoint(), after)
        self.assertEqual(TransactionReducer.restore(after).checkpoint(), after)

    def test_cross_domain_ties_do_not_certify_bar_cvd_or_dwell_order(self):
        for scope in ({'channel': 'other'}, {'source_session': 'other'},
                      {'publisher_or_venue': 'other'}, {'channel': None}):
            with self.subTest(scope=scope):
                rows = ((receipt('a', 'a0', data=value(source_order=1)), 10),
                        (receipt('b', 'b0', identity=key('b', **scope),
                                 data=value(price=101, side=-1, source_order=2)), 10))
                ledger, _ = build(rows)
                view = TransactionTapeView(ledger)
                trades = view.asof(instrument=INSTRUMENT, cut=10)
                self.assertTrue(all(t.order is None for t in trades))
                self.assertTrue(all(trade_from_transaction(r).order is None
                                    for r in ledger.asof(instrument=INSTRUMENT, cut=10)))
                coverage = WindowCoverage(INSTRUMENT, 0, 10, ((0,10),), 10, 'full')
                bar = bar_reference(view, instrument=INSTRUMENT, start=0, end=10, cut=10,
                                    definition_version='bar', coverage=coverage)
                self.assertEqual((bar.open_ticks, bar.close_ticks, bar.order_exact), (None, None, False))
                cohort = Cohort('all', 1, None, 'all-v1', 'provider-reported-trade-record')
                cvd = cvd_bar(trades, opening_cvd=0, cohort=cohort, coverage_complete=True)
                self.assertEqual((cvd.high_bounds, cvd.low_bounds, cvd.order_exact), ((0,3), (-3,0), False))
                dwell = bounded_dwell(view, instrument=INSTRUMENT, start=0, end=10, cut=10,
                                      stale_cap_ns=2, grid=RowGrid(1,0,'grid'))
                self.assertEqual((dwell.duration_by_row, dwell.uncertain_order_duration_ns), ((), 2))
        same, _ = build(((receipt('a','a0',data=value(source_order=1)),10),
                         (receipt('b','b0',data=value(price=101,source_order=2)),10)))
        self.assertEqual({t.order for t in TransactionTapeView(same).asof(instrument=INSTRUMENT,cut=10)}, {1,2})

    def test_mbp_mapping_rejects_wrong_raw_instrument_terms_and_invented_source_fields(self):
        event = mbp_event(0, action='T')
        mapping = mbp_mapping(event)
        ownership = mbp_key(event, mapping)
        condition = ConditionContract('synthetic', 'quantpad11-v1', 0, 1000, 'synthetic-only',
                                      (ConditionRule('NORMAL', True, True, 'fixture'),), True)
        arguments = dict(root_key=ownership, mapping=mapping, terms=NQ_REFERENCE,
                         instrument_kind='futures_outright', money_role='futures_notional_USD',
                         condition_contract=condition, condition_code='NORMAL', order=None, history_complete=True)
        wrapped = transaction_from_mbp(event, **arguments)
        self.assertEqual((wrapped.root_key.publisher_or_venue, wrapped.root_key.channel, wrapped.value.source_order),
                         (None, None, None))
        self.assertEqual(json.loads(wrapped.raw_payload)['instrument_mapping_id'], mapping.id)
        for changes in ({'root_key': replace(ownership, instrument_key='another-contract')},
                        {'terms': replace(NQ_REFERENCE, root='ES')},
                        {'terms': replace(NQ_REFERENCE, usd_per_point=Decimal(50))},
                        {'root_key': replace(ownership, publisher_or_venue='invented')},
                        {'root_key': replace(ownership, channel='invented')},
                        {'root_key': replace(ownership, provider='other')},
                        {'mapping': replace(mapping, dataset_id='other')}, {'order': 0}):
            with self.subTest(changes=changes):
                with self.assertRaises(ContractError):
                    transaction_from_mbp(event, **{**arguments, **changes})
        with self.assertRaises(ContractError):
            transaction_from_mbp(mbp_event(0, action='T', instrument=2), **arguments)
        # A native publisher/sequence is retained when it is actually supplied.
        from trading_research.data.events import normalize_mbp
        from tests.test_market_data import SCENARIO
        fields = dict(ts_event=10, ts_recv=11, action='T', side='B', price=100000000000,
                      size=3, flags=0, instrument_id=1, publisher_id=7, sequence=42, depth=0,
                      bid_px_00=100000000000, ask_px_00=100250000000, bid_sz_00=10, ask_sz_00=10)
        native = normalize_mbp(fields, event.address, native=True, scenario=SCENARIO)
        native_key = mbp_key(native, mapping)
        good = transaction_from_mbp(native, **{**arguments, 'root_key':native_key, 'order':42})
        self.assertEqual((good.root_key.publisher_or_venue, good.value.source_order), ('7',42))
        with self.assertRaises(ContractError):
            transaction_from_mbp(native, **{**arguments, 'order':42})

    def test_nontrivial_grid_profile_parity_uses_explicit_row_coordinate_conversion(self):
        rows = ((receipt('a','a0',data=value(price=-2,quantity=2)),10),
                (receipt('b','b0',data=value(price=3,quantity=4,side=-1)),10),
                (receipt('a','a1',op='revise',previous='a0',known=20,
                         data=value(price=7,quantity=3,side=None)),20))
        grid = RowGrid(4, 1, 'nontrivial-grid')
        ledger, target = build(rows, consumer=reducer(row_ticks=4,grid_origin=1))
        for cut in (10,20):
            with self.subTest(cut=cut):
                snap = target.snapshot(cut)
                literal = literal_aggregate(literal_replay(rows,cut=cut), instrument=INSTRUMENT,
                                            cut=cut,row_ticks=4,grid_origin=1)
                profile = profile_reference(TransactionTapeView(ledger).asof(instrument=INSTRUMENT,cut=cut),
                                             grid=grid,anchor_id='full',coverage_complete=True)
                converted = tuple((grid.lower_tick(row),buy,sell,unknown) for row,buy,sell,unknown in profile.rows)
                self.assertEqual(snap.profile, literal['profile'])
                self.assertEqual(snap.profile, converted)
                self.assertNotEqual(snap.profile, profile.rows)
                self.assertEqual((dict(snap.configuration)['row_ticks'],dict(snap.configuration)['grid_origin']), (4,1))

    def test_frozen_g20_unknown_observation_empty_complete_and_missing_history_are_distinct(self):
        expected = next(c for c in GOLDEN['cases'] if c['id']=='F05-G20')['expected']
        _, observed = build(((receipt(data=value(quantity=4,side=None)),10),))
        snap = observed.snapshot(10)
        self.assertEqual((snap.total,snap.unknown,snap.signed_bounds),
                         (expected['observed_unknown']['total'],expected['observed_unknown']['unknown'],
                          tuple(expected['observed_unknown']['signed_bounds'])))
        empty, missing = reducer().snapshot(10), reducer(coverage_complete=False).snapshot(10)
        self.assertEqual((empty.total,empty.certified_total,empty.signed_bounds,empty.complete_history), (0,0,(0,0),True))
        self.assertEqual((missing.total,missing.certified_total,missing.signed_bounds),
                         (expected['missing_gap']['observed_total'],expected['missing_gap']['true_total'],
                          expected['missing_gap']['signed_bounds']))
        self.assertEqual((missing.profile,missing.observed_volume,missing.condition_unresolved_volume), ((),0,0))
        self.assertFalse(missing.complete_history)
        self.assertNotEqual(empty.id,missing.id)
