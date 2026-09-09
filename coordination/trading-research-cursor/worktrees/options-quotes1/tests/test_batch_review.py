"""Discriminating cases from the frozen whole-implementation review.

Expected behaviors and original failing observations are retained in
validation/BATCH_REVIEW_2026_09_06.md and reports/batch-review-before.json.
"""

from dataclasses import FrozenInstanceError, asdict, replace
from decimal import Decimal, localcontext
from fractions import Fraction
import json
from pathlib import Path
import tempfile
from threading import RLock
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pyarrow as pa

from trading_research.data.arrow_audit import audit_arrow, nominate_profiles
from trading_research.data.compact import CompactProjector
from trading_research.data.events import decode_fields
from trading_research.errors import ContractError, IntegrityError
from trading_research.execution.columnar import ColumnarVenuePath
from trading_research.execution.orders import OrderLedger
from trading_research.execution.replay import BracketPlan, OrderTiming, reference_bracket
from trading_research.execution.venue import FillScenario, VenuePath, VenueQuote
from trading_research.foundations.bars import ActivityBars, BarEngine, Watermark, bar_reference
from trading_research.foundations.contracts import Decision, Opportunity, _json_payload
from trading_research.foundations.graph import Graph, Port
from trading_research.foundations.objects import ObjectRegistry
from trading_research.foundations.time import AvailabilityBasis, Clocks, derived_clocks
from trading_research.foundations.units import NQ_REFERENCE, Quantity, Unit
from trading_research.measurements.auction import tpo_reference
from trading_research.measurements.structure import pivot_reference
from trading_research.measurements.tape import RowGrid, TradeLedger, WeightedMoments, vwap_two_pass
from trading_research.operations.artifacts import artifact_ref, canonical_json, digest
from trading_research.operations.journal import Journal
from trading_research.operations.trials import TrialRegistry
from trading_research.research.folds import chronological_fold
from trading_research.research.models import fit_frequency, fit_logistic
from trading_research.risk.reservations import AtomicEntryGate
from trading_research.runtime.reactor import OptionalWorkers, WorkerBudget
from tests.test_foundations import clocks
from tests.test_market_data import event as raw_event
from tests.test_measurements import coverage, ledger, trade
from tests.test_objects import lifecycle, object_
from tests.test_orders_accounting import event as broker_event, spec
from tests.test_quality import examples
from tests.test_risk import fee_schedule, intent, snapshot


ROOT = Path(__file__).resolve().parents[1]


class FoundationReviewTests(unittest.TestCase):
    def test_integral_quantities_are_independent_of_decimal_precision(self):
        with localcontext() as context:
            context.prec = 3
            for value in ('123456789', '-123456789.00', '1E+40'):
                self.assertEqual(Quantity(Decimal(value), Unit.CONTRACTS).value, Decimal(value))
            with self.assertRaises(ContractError):
                Quantity(Decimal('123456789.01'), Unit.CONTRACTS)

    def test_availability_cannot_bypass_supplied_publication_or_computation(self):
        for field in ('computed_at', 'published_at'):
            with self.subTest(field=field), self.assertRaises(ContractError):
                Clocks(5, 10, 'raw', AvailabilityBasis.RECEIVED, received_at=10, **{field:20})
        # A source-clock lead remains explicit; event/provider clocks are not
        # silently max-clamped into the actual local receipt domain.
        observed = Clocks(20, 10, 'raw', AvailabilityBasis.RECEIVED, received_at=10, provider_received_at=19)
        self.assertTrue(observed.available(10))
        result = derived_clocks((clocks(10), clocks(12)), source_version='derived', actual_completion_at=20, confirmation_known_at=25)
        self.assertEqual((result.known_at, result.computed_at), (25, 20))

    def test_json_overflow_and_duplicate_members_are_rejected_recursively(self):
        for payload in (b'{"x":1e400}', b'[1,-1e400]', b'{"x":1,"x":2}', b'{"outer":{"x":1,"x":2}}', b'{"x":NaN}'):
            with self.subTest(payload=payload), self.assertRaises(ContractError):
                _json_payload(payload)
        _json_payload(b'{"x":1e300,"rows":[{"x":1},{"x":2}]}')

    def test_versioned_common_messages_reject_mutable_collection_aliases(self):
        with self.assertRaises(ContractError):
            replace(object_(), role_candidates=['support'])
        with self.assertRaises(ContractError):
            replace(lifecycle(), initial_states={'active'})
        with self.assertRaises(ContractError):
            replace(lifecycle(), transitions=(['active', 'expired'],))
        args = ('d', 10, ('a',), 'wait', (('a','risk'),), 'state', ('model',), None, None, 'veto', 10, None)
        valid = Decision(*args)
        for change in ({'candidate_ids':['a']}, {'model_versions':['m']}, {'rejected_reasons':(['a','risk'],)}):
            with self.subTest(change=change), self.assertRaises(ContractError):
                replace(valid, **change)
        with self.assertRaises(ContractError):
            Opportunity('o','set','object',(),1,(),(),(),clocks(10),[],None)

    def test_compiled_graph_cannot_change_ports_edges_or_versioned_attributes(self):
        graph = Graph((Port('root','F01',0,'S',frozenset({'x'})),))
        version = graph.version
        with self.assertRaises(TypeError):
            graph.ports['root'] = replace(graph.ports['root'], schema='other')
        with self.assertRaises(AttributeError):
            graph.children['root'].add('undeclared')
        with self.assertRaises(FrozenInstanceError):
            graph.ports = {}
        self.assertEqual(graph.version, version)


class ObjectReviewTests(unittest.TestCase):
    def registry(self, root):
        result = ObjectRegistry(Path(root)/'objects.sqlite', lifecycles=(lifecycle(),))
        result.anchor(id='bar', known_at=5, evidence_version='observed-bar')
        return result

    def test_candidate_cut_uses_exact_instrument_namespace(self):
        with tempfile.TemporaryDirectory() as root:
            registry = self.registry(root)
            a = object_('a')
            b = replace(object_('b'), instrument=replace(a.instrument, provider='other', venue='elsewhere'))
            registry.append(a, state='active', event_id='a', reason='formed')
            registry.append(b, state='active', event_id='b', reason='formed')
            first = registry.freeze_candidates(id='cut-a', at=10, instrument=a.instrument)
            second = registry.freeze_candidates(id='cut-b', at=10, instrument=b.instrument)
            self.assertEqual(first['candidate_versions'], (a.version_id,))
            self.assertEqual(second['candidate_versions'], (b.version_id,))
            self.assertNotEqual(first['instrument'], second['instrument'])

    def test_candidate_frontier_survives_restart_and_blocks_backdated_admission(self):
        with tempfile.TemporaryDirectory() as root:
            registry = self.registry(root); a = object_('a')
            registry.append(a, state='active', event_id='a', reason='formed')
            frozen = registry.freeze_candidates(id='cut', at=100, instrument=a.instrument)
            restored = ObjectRegistry(Path(root)/'objects.sqlite', lifecycles=(lifecycle(),))
            for at in (99,100):
                with self.subTest(at=at), self.assertRaises(ContractError):
                    restored.append(object_('late',at=at), state='active', event_id='late', reason='late publication')
            restored.append(object_('later',at=101),state='active',event_id='later',reason='current publication')
            self.assertEqual(tuple(o.version_id for o,_ in restored.asof(100,active_only=True)), frozen['candidate_versions'])
            self.assertEqual(restored.freeze_candidates(id='cut',at=100,instrument=a.instrument),frozen)

    def test_candidate_freeze_rejects_a_concurrent_object_admission(self):
        with tempfile.TemporaryDirectory() as root:
            registry = self.registry(root); a = object_('a')
            registry.append(a,state='active',event_id='a',reason='formed')
            original = registry.journal.append
            injected = False
            def racing_append(**kwargs):
                nonlocal injected
                if kwargs['kind']=='candidate_cut' and not injected:
                    injected=True
                    registry.append(object_('b',at=12),state='active',event_id='b',reason='arrived before commit')
                return original(**kwargs)
            with patch.object(registry.journal,'append',side_effect=racing_append), self.assertRaises(ContractError):
                registry.freeze_candidates(id='cut',at=20,instrument=a.instrument)
            self.assertEqual(registry.freeze_candidates(id='cut',at=20,instrument=a.instrument)['candidate_count'],2)


class MeasurementReviewTests(unittest.TestCase):
    def test_older_bar_cut_cannot_replace_more_current_publication(self):
        engine=BarEngine(instrument='NQH5',definition_version='bar')
        engine.add(trade(0,100,at=1));engine.add(trade(1,110,at=7))
        expected=engine.publish(start=0,end=10,cut=8,published_at=9,coverage=coverage(0,10,cut=8,intervals=((0,8),)))
        for state in (engine,BarEngine.restore(engine.checkpoint())):
            with self.assertRaises(ContractError):
                state.publish(start=0,end=10,cut=5,published_at=10,coverage=coverage(0,10,cut=5,intervals=((0,5),)))
            self.assertEqual(state.asof(start=0,end=10,cut=10),expected)

    def test_unpriced_edge_trades_do_not_become_other_prints_or_confirm_pivots(self):
        tape=ledger((trade(0,None,at=1),trade(1,100,at=2),trade(2,None,at=3)))
        bar=bar_reference(tape,instrument='NQH5',start=0,end=10,cut=10,definition_version='bar',coverage=coverage(0,10))
        self.assertEqual((bar.open_ticks,bar.close_ticks,bar.high_ticks,bar.low_ticks),(None,None,100,100))
        self.assertEqual((bar.volume,bar.prints,bar.unpriced_volume),(3,3,2))
        self.assertFalse(bar.coverage_complete)
        tape=ledger((trade(0,100,at=1),trade(1,None,at=11),trade(2,1000,at=12),trade(3,100,at=21)))
        bars=tuple(replace(bar_reference(tape,instrument='NQH5',start=i,end=i+10,cut=i+10,definition_version='bar',coverage=coverage(i,i+10),
                                       watermark=Watermark(i+10,i+10,'watermark')),published_at=i+10) for i in (0,10,20))
        self.assertEqual(pivot_reference(bars,left=1,right=1,cut=30),())

    def test_activity_boundaries_survive_restart_even_without_pending_trades(self):
        for nonempty in (False,True):
            with self.subTest(nonempty=nonempty):
                state=ActivityBars(kind='events',threshold=2)
                if nonempty:state.add(trade(0,at=10))
                state.boundary(known_at=100,reason='session ended')
                restored=ActivityBars.restore(state.checkpoint())
                for run in (state,restored):
                    with self.assertRaises(ContractError):run.add(trade(1,at=20))
                    with self.assertRaises(ContractError):run.boundary(known_at=99,reason='old timer')
                    run.add(trade(2,at=101));finished=run.add(trade(3,at=102))
                    self.assertEqual((finished.minimum_known_at,finished.event_ids),(102,('trade:2','trade:3')))
                self.assertEqual(state.checkpoint(),restored.checkpoint())

    def test_tpo_boundary_visits_and_opportunities_use_the_same_cut(self):
        for cut,expected in ((0,1),(9,1),(10,2),(19,2),(20,2)):
            at=min(cut,19);tape=ledger((trade(0,at=at),))
            result=tpo_reference(tape,instrument='NQH5',start=0,end=20,cut=cut,bracket_ns=10,grid=RowGrid(1,0,'g'),
                                 coverage=coverage(0,20,cut=cut,intervals=() if cut==0 else ((0,cut),)),definition_version='tpo',minimum_brackets=1)
            self.assertEqual(result.bracket_opportunities,expected)
            self.assertLess(max(result.visits[0][1]),result.bracket_opportunities)

    def test_correction_replacement_cannot_cross_bar_instrument_namespace(self):
        tape=TradeLedger();tape.add(replace(trade(0,at=1),instrument='ESH5'))
        tape.correct(id='es',original_id='trade:0',known_at=5,reason='correction',replacement=replace(trade(1,at=2,known=5),instrument='ESH5'))
        result=bar_reference(tape,instrument='NQH5',start=0,end=10,cut=10,definition_version='bar',coverage=coverage(0,10))
        self.assertEqual((result.source_event_ids,result.correction_ids,result.volume),((),(),0))

    def test_correction_requires_new_replacement_identity_and_failure_is_atomic(self):
        a,b=trade(0,100,7,at=1,known=10),trade(1,101,9,at=2,known=10)
        tape=ledger((a,b));before=tape.checkpoint()
        with self.assertRaises(ContractError):
            tape.correct(id='correction',original_id=a.id,known_at=10,reason='replacement',replacement=b)
        self.assertEqual(tape.checkpoint(),before)
        replacement=trade(2,102,3,at=2,known=11)
        tape.correct(id='valid',original_id=a.id,known_at=11,reason='provider correction',replacement=replacement)
        tape.correct(id='valid',original_id=a.id,known_at=11,reason='provider correction',replacement=replacement)
        self.assertEqual(sum(t.size for t in tape.asof(instrument='NQH5',cut=11)),12)

    def test_online_vwap_rejects_mixed_contracts_and_changed_identity_after_restart(self):
        a=trade(0,100,2);b=replace(trade(1,200,3),instrument='ESH5')
        online=WeightedMoments();online.add(a)
        for state in (online,WeightedMoments.restore(online.checkpoint())):
            before=state.checkpoint()
            with self.assertRaises(ContractError):state.add(b)
            with self.assertRaises(IntegrityError):state.add(replace(a,source_content_version='changed'))
            self.assertEqual(state.checkpoint(),before)
            state.add(a)
            self.assertEqual((state.mean,state.variance),vwap_two_pass((a,)))
            state.remove(a.id)
            with self.assertRaises(ContractError):state.add(b)


def order_ledger(root):
    result=OrderLedger(Path(root)/'orders.sqlite',account_id='synthetic')
    result.reconcile(id='initial',known_at=0,positions={},open_order_ids=(),open_orders_complete=True,execution_history_complete=True,evidence_version='fixture')
    return result


def compact_tables(*,tied=False):
    def ints(values):return pa.array(values,type=pa.int64())
    q=pa.table({'t':ints([1,1] if tied else [1,2]),'source_order':ints([2,1]),'instrument_id':ints([1,1]),
                'bid':ints([100,90]),'ask':ints([101,91]),'bid_size':ints([1,1]),'ask_size':ints([1,1]),
                'book_valid':pa.array([1,1],type=pa.uint8()),'snapshot':pa.array([0,0],type=pa.uint8())})
    t=pa.table({'t':ints([3]),'source_order':ints([3]),'instrument_id':ints([1]),'price':ints([100]),'size':ints([1]),'side':ints([1]),'price_valid':pa.array([1],type=pa.uint8())})
    return q,t


def columnar(q,t):
    return ColumnarVenuePath(instrument='NQH5',instrument_id=1,quotes=q,trades=t,source_version='fixture',feed_delay_ns=0,
                             latency_scenario='synthetic-zero',market_state='continuous',market_state_version='fixture-state',
                             complete_intervals=((0,100),),coverage_version='fixture-coverage')


class ExecutionReviewTests(unittest.TestCase):
    def test_contingent_exit_requires_matching_live_parent(self):
        with tempfile.TemporaryDirectory() as root:
            orders=order_ledger(root);orders.submit(spec())
            with self.assertRaises(ContractError):
                orders.submit(replace(spec('cross',-1,'protective_stop',2,'entry'),instrument='ESH5'))
            orders.observe(broker_event('cancel','entry','cancelled',3))
            with self.assertRaises(ContractError):orders.submit(spec('stale',-1,'protective_stop',4,'entry'))

    def test_closed_entry_cannot_be_parent_of_a_later_position_stop(self):
        with tempfile.TemporaryDirectory() as root:
            orders=order_ledger(root);orders.submit(spec())
            orders.observe(broker_event('first-fill',kind='fill',at=2,execution='e1',qty=1,price=100))
            orders.submit(spec('exit',-1,'full_exit',3))
            orders.observe(broker_event('exit-fill','exit','fill',4,'x1',1,101))
            orders.reconcile(id='flat',known_at=5,positions={},open_order_ids=(),open_orders_complete=True,execution_history_complete=True,evidence_version='flat')
            orders.submit(spec('second',at=6))
            orders.observe(broker_event('second-fill','second','fill',7,'e2',1,102))
            with self.assertRaises(ContractError):orders.submit(spec('old-parent',-1,'protective_stop',8,'entry'))
            orders.submit(spec('right-parent',-1,'protective_stop',8,'second'))

    def test_limit_role_string_cannot_manufacture_protective_stop_coverage(self):
        with self.assertRaises(ContractError):
            replace(spec('false-stop',-1,'protective_stop',3,'entry'),order_type='limit',price_ticks=150)
        self.assertEqual(spec('stop',-1,'protective_stop',3,'entry').order_type,'stop_market')

    def test_columnar_rejects_unordered_ties_then_matches_literal_order(self):
        q,t=compact_tables(tied=True)
        with self.assertRaises(ContractError):columnar(q,t)
        path=columnar(q.sort_by([('t','ascending'),('source_order','ascending')]),t)
        literal=VenuePath(instrument=path.instrument,quotes=tuple(path.quotes),trades=tuple(path.trades),complete_intervals=path.complete_intervals,coverage_version=path.coverage_version)
        for clock in ('venue','strategy'):
            self.assertEqual(path.quote_at(5,clock=clock)[0],literal.quote_at(5,clock=clock)[0])
            self.assertEqual(path.quote_at(5,clock=clock)[0].bid,100)

    def test_versioned_columnar_path_owns_readonly_content_and_scenario(self):
        q,t=compact_tables();path=columnar(q,t);version=path.version
        memoryview(q['bid'].chunk(0).buffers()[1]).cast('q')[0]=80
        self.assertEqual(path.quote_at(1,clock='venue',same_time_ordering='venue_first')[0].bid,100)
        with self.assertRaises(TypeError):path.q['bid'][0]=70
        with self.assertRaises(TypeError):memoryview(path.qtable['bid'].chunk(0).buffers()[1]).cast('q')[0]=70
        with self.assertRaises(AttributeError):path.market_state='closed'
        self.assertEqual(path.version,version)
        self.assertNotEqual(columnar(q,t).version,version)

    def test_marked_drawdown_includes_standing_liquidation_at_entry(self):
        fees=fee_schedule()
        path=VenuePath(instrument='NQH5',quotes=(VenueQuote('before','NQH5',1,1,1,100,110,1,1,True,'continuous','q1'),
                                               VenueQuote('exit','NQH5',10,10,2,120,130,1,1,True,'continuous','q2')),
                       trades=(),complete_intervals=((0,100),),coverage_version='coverage')
        plan=BracketPlan('p','NQH5',1,5,110,109,120,10,50,60,Decimal(0),'geometry')
        result=reference_bracket(path,plan,terms=NQ_REFERENCE,fees=fees,fill_scenario=FillScenario('s',0,'venue_first','strict_trade_through','coverage',fees.version),
                                 timing=OrderTiming('synthetic-zero',0,0,0,'trigger_first'),daily_budget=Decimal(50))
        self.assertEqual(result.minimum_marked_net_usd,Decimal('-52.88'))
        self.assertTrue(result.daily_loss_breach)
        self.assertEqual(result.net_usd,Decimal('44.24'))


class GateReviewTests(unittest.TestCase):
    def make(self,root):
        return AtomicEntryGate(Journal(Path(root)/'gate.sqlite'),account_id='one-account',fee_schedule=fee_schedule(),quote_ttl_ns=30,broker_ttl_ns=40,feed_ttl_ns=20)

    def test_dispatch_and_broker_availability_cannot_regress_after_restart(self):
        with tempfile.TemporaryDirectory() as root:
            gate=self.make(root);s=snapshot();gate.observe(s);i=intent(s);gate.reserve(i,at=20)
            restored=self.make(root)
            with self.assertRaises(ContractError):restored.dispatch(i,at=12)
            self.assertIsNotNone(restored.dispatch(i,at=21))
            restored.broker_state(i.id,event_id='unknown',state='unknown',evidence_id='timeout',at=25)
            with self.assertRaises(ContractError):self.make(root).broker_state(i.id,event_id='old',state='working',evidence_id='old-message',at=24)

    def test_pre_dispatch_snapshot_cannot_release_reservation_but_current_truth_can(self):
        with tempfile.TemporaryDirectory() as root:
            gate=self.make(root);s=snapshot();gate.observe(s);i=intent(s);gate.reserve(i,at=11);gate.dispatch(i,at=12)
            with self.assertRaises(ContractError):gate.broker_state(i.id,event_id='bad',state='cancelled',evidence_id='reported',at=13,snapshot=s)
            self.assertFalse(gate.reserve(intent(s,id='second'),at=14).approved)
            current=replace(s,at=15,broker_observed_at=15,source_version='current-complete-broker-truth')
            gate.broker_state(i.id,event_id='confirmed',state='cancelled',evidence_id='complete-after-dispatch',at=15,snapshot=current)
            self.assertTrue(self.make(root).reserve(intent(current,id='third'),at=16).approved)


class WorkerReviewTests(unittest.TestCase):
    def run_ready(self,elapsed):
        calls=[]
        class Store:
            journal=SimpleNamespace(append=lambda **kwargs:None)
            def complete(self,*args,**kwargs):calls.append(('completed',None))
            def abandon(self,*args,**kwargs):calls.append(('abandoned',kwargs['reason']))
        class Connection:
            def poll(self):return True
            def recv_bytes(self,n):return canonical_json({'success':True,'payload_hex':'7b7d','completed_at':10,'cpu_ns':1,'peak_rss_bytes':1})
            def close(self):pass
        class Process:
            def is_alive(self):return False
            def join(self,**kwargs):pass
        worker=object.__new__(OptionalWorkers);worker._lock=RLock();worker.store=Store();worker._pending=[];worker.max_workers=1
        from trading_research.runtime.scheduling import RuntimeCosts
        worker.costs=RuntimeCosts()
        request=SimpleNamespace(id='r',producer='toy',expires_at=1000,horizon_end=None)
        worker._running={'r':(request,Process(),Connection(),WorkerBudget(50,1,1_000_000),0)}
        with patch('trading_research.runtime.reactor.time.time_ns',return_value=10),patch('trading_research.runtime.reactor.time.monotonic_ns',return_value=elapsed):
            worker.poll()
        return calls

    def test_ready_worker_results_still_obey_wall_budget(self):
        self.assertEqual(self.run_ready(49),[('completed',None)])
        for elapsed in (50,100):
            calls=self.run_ready(elapsed)
            self.assertEqual(calls[0][0],'abandoned')
            self.assertIn('wall-time budget',calls[0][1])


class LearnedIdentityReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=examples(days=10,per_day=3)
        cls.fold=chronological_fold((e.sample for e in cls.rows),id='fixed',fit_at=600,evaluation_start=601,evaluation_end=1000)

    def test_fitted_frequency_bins_and_training_membership_are_immutable(self):
        for cuts in ([[0.]],([0.],)):
            with self.subTest(cuts=cuts),self.assertRaises(ContractError):fit_frequency(self.rows,self.fold,('x',),cuts=cuts)
        model=fit_frequency(self.rows,self.fold,('x',),cuts=((0.,),))
        with self.assertRaises(FrozenInstanceError):model.cuts=((1000.,),)
        with self.assertRaises(ContractError):replace(model.artifact,training_ids=set(model.artifact.training_ids))

    def test_contradictory_fitted_identity_is_not_silently_removed(self):
        model=fit_logistic(self.rows,self.fold,('x',),l2_strength=.1)
        held=next(e for e in self.rows if e.sample.id in self.fold.evaluation_ids)
        forged=replace(model.fit_artifacts[0],training_ids=frozenset({held.sample.id}),training_groups=frozenset({held.sample.date_group}))
        with self.assertRaises(ContractError):model.predict(held,upstream=(forged,))
        self.assertEqual(model.predict(held)[0],model.predict(held,upstream=(model.fit_artifacts[0],))[0])


class RawProjectionReviewTests(unittest.TestCase):
    def test_failed_projection_cannot_publish_partial_state_or_continue(self):
        rows=[decode_fields(raw_event(0,at=1).raw_fields),{**decode_fields(raw_event(1,at=2).raw_fields),'flags':300}]
        projector=CompactProjector(tick_denominator=4,maximum_rows=100)
        with self.assertRaises(IntegrityError):projector.project(pa.RecordBatch.from_pylist(rows),source_part='bad')
        with self.assertRaises(IntegrityError):projector.manifest()
        with self.assertRaises(IntegrityError):projector.project(pa.RecordBatch.from_pylist(rows[:1]),source_part='retry')
        clean=CompactProjector(tick_denominator=4,maximum_rows=100)
        clean.project(pa.RecordBatch.from_pylist(rows[:1]),source_part='clean')
        self.assertEqual(clean.manifest()['counts']['raw_rows'],1)

    def test_repeated_physical_part_cannot_double_volume(self):
        batch=pa.RecordBatch.from_pylist([decode_fields(raw_event(0,at=1,action='T',flags=0,size=7).raw_fields)])
        projector=CompactProjector(tick_denominator=4,maximum_rows=100);projector.project(batch,source_part='one')
        self.assertEqual(projector.manifest()['counts']['volume'],7)
        with self.assertRaises(IntegrityError):projector.project(batch,source_part='one')
        with self.assertRaises(IntegrityError):projector.manifest()

    def test_missing_golden_profile_is_reported_without_inventing_a_prefix(self):
        profiles=json.loads((ROOT/'tests/fixtures/arrow-profiles.json').read_bytes())['profiles']
        missing='b382eec1322b80c1b624f952c81910ac7cd0b5c87bbea0bfceb739c3ea290590'
        catalog={key:[profile['fields']] for key,profile in profiles.items()}
        available=sorted(set(profiles)-{missing})
        def row(profile,index):
            return {'dataset':profile,'file':f'{profile}/{index:04}.parquet','footer_rows':1,'head':[{'fixture':'nonempty'}],
                    'schema':'\n'.join(f"{f['name']}: {f['type']}" for f in profiles[profile]['fields'])}
        prior=[row(available[i%len(available)],i) for i in range(216)]
        result=nominate_profiles(catalog,prior)
        self.assertEqual(len(result['choices']),21)
        self.assertEqual([p['profile_id'] for p in result['missing_profiles']],[missing])
        prior[-1]=row(missing,215)
        complete=nominate_profiles(catalog,prior)
        self.assertEqual((len(complete['choices']),complete['missing_profiles']),(22,[]))

    def test_audit_preflight_errors_are_recorded_as_failed_attempts(self):
        for bad_input in ('malformed','missing'):
            with self.subTest(bad_input=bad_input),tempfile.TemporaryDirectory() as root:
                root=Path(root);schemas=root/'schemas.json';prior=root/'prior.json';output=root/'attempts'
                schemas.write_text('{invalid json')
                if bad_input=='malformed':prior.write_text('[]')
                with self.assertRaises((ContractError,ValueError)):
                    audit_arrow(data_root=root,schemas_path=schemas,prior_audit=prior,output_root=output)
                registry=TrialRegistry(output);state=registry.state()
                self.assertEqual(len(state['attempts']),1)
                attempt=next(iter(state['attempts'].values()))
                self.assertEqual(attempt['status'],'failed')
                report=registry.artifacts.read_json(artifact_ref(attempt['result_artifacts'][0]))
                self.assertFalse(report['success'])
                self.assertEqual(report['completed_profiles'],[])

