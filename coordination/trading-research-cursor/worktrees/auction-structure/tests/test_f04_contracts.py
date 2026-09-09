"""Consolidated F04 review regressions, fixed before the first batch execution."""
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from threading import RLock
import unittest
from unittest.mock import patch

from references.replay_literal import full_recompute
from trading_research.errors import ContractError
from trading_research.foundations.availability import Observation, AvailabilityIndex, JoinPolicy
from trading_research.foundations.graph import Graph, Port, InputPort
from trading_research.operations.journal import Journal
from trading_research.runtime.merge import PartitionMerge
from trading_research.runtime.publication import VersionStore
from trading_research.runtime.reactor import OptionalWorkers, WorkerBudget
from trading_research.runtime.scheduling import CostSample, DirtyPlanner, FieldChange, RuntimeCosts
from tests.test_foundations import clocks
from tests import test_replay_merge as merge_examples
from tests.test_runtime import graph, request
from tests import test_scheduling as scheduling_examples
from tests.test_scheduling import job


class F04ContractReviewTests(unittest.TestCase):
    def test_mutable_source_payload_and_request_lineage_are_rejected_before_registration(self):
        for changes in ({'source_version':['v1']}, {'source_version':3}, {'known_at':None}, {'assumption_id':['latency']}):
            with self.subTest(changes=changes),self.assertRaises(ContractError): replace(clocks(10),**changes)
        observation=Observation('q','id',0,clocks(10),b'1',10)
        for changes in ({'payload_json':bytearray(b'1')},{'eligible':1},{'session':[]},{'clocks':{}},{'key':['q']}):
            with self.subTest(changes=changes),self.assertRaises(ContractError): replace(observation,**changes)
        with TemporaryDirectory() as root:
            store=VersionStore(graph(),Journal(Path(root)/'versions.sqlite'))
            req=request(store)
            before=store.journal.read()
            for changes in ({'code_version':['v1']},{'parameter_version':['p']},{'inputs':(object(),)},{'horizon_end':True}):
                with self.subTest(changes=changes),self.assertRaises(ContractError): replace(req,**changes)
            with self.assertRaises(ContractError):
                store.freeze('context',cut=10,submitted_at=10,input_ids=(req.inputs[0].metadata.id,),
                             expires_at=100,horizon_end=100,code_version=['v1'],parameter_version='p')
            self.assertEqual(store.journal.read(),before)

    def test_merge_configuration_cannot_omit_a_partition_or_relax_registered_bounds(self):
        with TemporaryDirectory() as root:
            merge=PartitionMerge(Path(root)/'merge.sqlite',{'core':frozenset({'A','B'})})
            for name,value in [('domains',{'core':frozenset({'A'})}),('partitions',frozenset({'A'})),
                               ('max_records',10**9),('max_bytes',10**12),('max_batch',10**6),('version','changed'),('path',Path(root)/'elsewhere')]:
                with self.subTest(name=name),self.assertRaises((AttributeError,TypeError)): setattr(merge,name,value)
            self.assertEqual(merge.domains['core'],frozenset({'A','B'}))
            with self.assertRaises(TypeError): merge.domains['core']=frozenset({'A'})

    def test_acknowledgement_receipt_prevents_historical_cursor_regression_after_restart(self):
        with TemporaryDirectory() as root:
            path=Path(root)/'merge.sqlite';domains={'core':frozenset({'A'})}
            merge=PartitionMerge(path,domains)
            merge.append(merge_examples.ReplayMergeTests.event('first','A',0,10));merge.append(merge_examples.ReplayMergeTests.event('second','A',1,20))
            merge.advance('A',before=30,known_at=30,evidence_id='sealed')
            first=merge.peek('core',at=30);merge.acknowledge(first,at=100)
            restored=PartitionMerge(path,domains)
            with self.assertRaises(ContractError): restored.peek('core',at=99)
            with self.assertRaises(ContractError): restored.acknowledge(first,at=99)
            self.assertFalse(restored.acknowledge(first,at=100))
            second=restored.peek('core',at=100)
            with self.assertRaises(ContractError): restored.acknowledge(second,at=30)
            restored.acknowledge(second,at=100)
            self.assertIsNone(PartitionMerge(path,domains).peek('core',at=100))

    def test_future_runtime_sample_eviction_cannot_change_an_earlier_cost_to_fallback(self):
        costs=RuntimeCosts(max_samples=1)
        costs.add(CostSample('old','surface',10,7,2))
        self.assertEqual(costs.estimate('surface',at=15,fallback_ns=99),7)
        costs.add(CostSample('new','surface',20,3,1))
        with self.assertRaises(ContractError): costs.estimate('surface',at=15,fallback_ns=99)
        self.assertEqual(costs.estimate('surface',at=20,fallback_ns=99),3)

    def test_evidence_only_edge_is_invalidated_by_lineage_or_optional_outage(self):
        raw=Port('evidence','F04',0,'proof',frozenset())
        dependent=Port('forecast','C01',1,'f',frozenset({'p'}),(InputPort('evidence','proof',frozenset(),optional=True),))
        planner=DirtyPlanner(Graph([raw,dependent]))
        self.assertEqual(planner.plan({'evidence':FieldChange(frozenset())}).optional,())
        self.assertEqual(planner.plan({'evidence':FieldChange(frozenset(),True)}).optional,('forecast',))
        outage=planner.plan({},unavailable=frozenset({'evidence'}))
        self.assertEqual((outage.optional,outage.blocked),(('forecast',),frozenset({'evidence'})))

    def test_full_reference_rejects_stale_derived_seed_and_current_lagged_state(self):
        g=graph();kernels={'context':lambda v:{'p':1},'decision':lambda v:{'action':1}}
        with self.assertRaises(ContractError): full_recompute(g,{'context':{'p':99}},kernels)
        values,calls=full_recompute(g,{},kernels)
        self.assertEqual((values,calls),({},()))
        raw=Port('raw','F01',0,'s',frozenset({'x'}))
        model=Port('model','C01',1,'m',frozenset({'p'}),(InputPort('raw','s',frozenset({'x'}),lag_ns=1,max_age_ns=5),))
        with self.assertRaises(ContractError): full_recompute(Graph([raw,model]),{'raw':{'x':1}},{'model':lambda v:{'p':1}})

    def test_zero_endpoint_is_expired_and_cpi_revision_preserves_past_decision_view(self):
        with TemporaryDirectory() as root:
            store=VersionStore(graph(),Journal(Path(root)/'versions.sqlite'))
            req=request(store,at=-10,end=10)
            zero=store.freeze('context',cut=-10,submitted_at=-10,input_ids=(req.inputs[0].metadata.id,),
                              expires_at=10,horizon_end=0,code_version='c',parameter_version='p')
            self.assertIsNone(store.complete(zero,payload=b'late',completed_at=1))
            self.assertIsNone(store.latest('context',available_at=1,observation_cut=1,max_age_ns=100))
        original=Observation('CPI','first-report',0,clocks(10),b'100',5)
        revision=replace(original,id='revised-report',revision=1,clocks=clocks(20),payload_json=b'110')
        index=AvailabilityIndex.restore([original,revision])
        self.assertEqual(index.asof('CPI',cut=15,policy=JoinPolicy(100)),original)
        self.assertEqual(index.asof('CPI',cut=20,policy=JoinPolicy(100)),revision)

    def test_invalid_or_future_optional_admission_preserves_already_accepted_work(self):
        worker,records,abandoned=scheduling_examples.QueueSchedulingTests().worker_without_threads()
        budget=WorkerBudget(100,1,1_000_000)
        old=job('old','cvd');new=job('new','cvd',cut=11)
        with patch('trading_research.runtime.reactor.time.time_ns',return_value=20):
            worker.submit(old,bytes,budget=budget,coalesce_key='same')
            for function,bad_budget,key,req in [(bytes,None,'same',new),(None,budget,'same',new),
                                               (bytes,budget,['same'],new),(bytes,budget,'same',job('future','cvd',submitted_at=21,cut=21))]:
                with self.subTest(function=function,budget=bad_budget,key=key),self.assertRaises(ContractError):
                    worker.submit(req,function,budget=bad_budget,coalesce_key=key)
                self.assertEqual([r[0].id for r in worker._pending],['old'])
                self.assertEqual(abandoned,[])
                self.assertEqual(len(records),1)

    def test_worker_uses_one_receipt_duration_for_persisted_and_restored_runtime_cost(self):
        tick={'now':5};records=[]
        def complete(*args,**kwargs): tick['now']+=500  # publication work is after result receipt
        journal=SimpleNamespace(append=lambda **row:records.append(row))
        worker=object.__new__(OptionalWorkers);worker._lock=RLock();worker._pending=[];worker.max_workers=1
        worker.costs=RuntimeCosts();worker.store=SimpleNamespace(journal=journal,complete=complete,abandon=lambda *a,**k:None)
        result=b'{"success":true,"payload_hex":"31","completed_at":1,"cpu_ns":2,"peak_rss_bytes":1}'
        conn=SimpleNamespace(poll=lambda:True,recv_bytes=lambda n:result,close=lambda:None)
        proc=SimpleNamespace(is_alive=lambda:False,join=lambda **kwargs:None)
        req=job('r','toy',submitted_at=0,deadline=1000)
        worker._running={'r':(req,proc,conn,WorkerBudget(100,1,1_000_000),0)}
        with patch('trading_research.runtime.reactor.time.time_ns',return_value=10),patch('trading_research.runtime.reactor.time.monotonic_ns',side_effect=lambda:tick['now']):
            worker.poll()
        payload=next(r['payload'] for r in records if r['kind']=='optional_resource_result')
        self.assertEqual(payload['wall_ns'],5)
        restored=RuntimeCosts();restored.add(CostSample('r','toy',payload['parent_received_at'],payload['wall_ns'],payload['result']['cpu_ns']))
        self.assertEqual(worker.costs.estimate('toy',at=10,fallback_ns=99),restored.estimate('toy',at=10,fallback_ns=99))
        self.assertEqual(worker.costs.estimate('toy',at=10,fallback_ns=99),5)
