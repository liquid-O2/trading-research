"""Registered 64 finite V01/V02 cases; all expected values are predeclared.

No learner search or market tape is used. Supplied F11 state is committed and
restored through the real store, with independent old-wire compatibility checks.
"""
from dataclasses import replace, fields
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import tempfile
import unittest

from references import v01_v02_literal as literal
from trading_research.errors import ContractError, IntegrityError, DependencyUnavailable
from trading_research.foundations.units import Ticks, Unit
from trading_research.foundations.contracts import Target, Capability, Band
from trading_research.operations.artifacts import ArtifactStore, canonical_json, digest
from trading_research.operations.provenance import InputValue
from trading_research.operations import artifact_graph as graph
from trading_research.research.labels import PathPoint, ObservationWindow, reference_path_label
from trading_research.research.object_labels import ObjectTarget, ExactPoint, reference_object_label, compatible_gap_evidence
from trading_research.research.folds import Sample, Fold, FittedArtifact, chronological_fold, validate_fold_population, validate_oof
from trading_research.research.models import FrequencyModel, BinaryExample, _training
from trading_research.research.calibration import fit_sigmoid_calibration
from trading_research.research.temporal_folds import (V01V02LimitsV1, DEFAULT_LIMITS, TemporalDependencyV1,
    TemporalSampleV1, TemporalFoldV1, TemporalExclusionV1, compile_temporal_fold,
    validate_temporal_fold_population, FitStage, OOFEdge, compile_oof_schedule,
    temporal_checkpoint, restore_temporal_checkpoint, bounded_json)
from trading_research.research.label_ledger import (LabelDefinition, CandidateRecord, SamplingFrame,
    ObservationEvidence, LabelOutcome, LabelLedger, sampling_weight, grouped_weights, support_counts,
    contact_partial_fact, contact_origin, admit_original_feature, OIReport, oi_endpoint,
    policy_outcome, episode_assignments, censored_event_bounds, future_profile_mass,
    append_price_outcome,append_object_outcome,append_oi_outcome,append_policy_outcome,append_profile_outcome)
from trading_research.research.label_payloads import geometry_source
from tests.test_artifact_graph import Fixture

GOLDEN=json.loads((Path(__file__).parent/'golden/v01_v02_label_temporal_v1.json').read_text())
CASES={c['id']:c for c in GOLDEN['cases']}


def target(cut=0,end=10):
    return Target('path','price-v1','ES',cut,end,'certified_last_observed_mark','clock',Unit.TICKS,
                  frozenset({Capability.TERMINAL_RETURN,Capability.EXCURSIONS,Capability.FIRST_PASSAGE}))


def coverage(end=10,cut=0,cert=None,gaps=(),ordered=True):
    return ObservationWindow(cut,end,end+1 if cert is None else cert,gaps,ordered,'obs-v1')


def path(events=(),initial=100,end=10,**kw):
    rows=tuple(PathPoint(p[0],p[1] if len(p)>2 else 0,Ticks(p[2] if len(p)>2 else p[1]),p[3] if len(p)>3 else p[0]) for p in events)
    return reference_path_label(target(end=end),initial=Ticks(initial),points=rows,
        coverage=kw.pop('coverage',coverage(end=end)),up_ticks=kw.pop('up',3),down_ticks=kw.pop('down',3),**kw)


def obj(events=(),initial=99,lower=100,upper=102,cut=0,end=10,side=1,a=3,b=2,mode='future_contact',cov=None,version='o-v1'):
    t=ObjectTarget('object-target',version,cut,end,Band(F(lower),F(upper)),side,F(a),F(b),'certified_discrete_ticks',mode)
    rows=tuple(ExactPoint(p[0],p[1] if len(p)>2 else 0,F(p[2] if len(p)>2 else p[1]),p[3] if len(p)>3 else p[0]) for p in events)
    return t,rows,reference_object_label(t,initial=F(initial),points=rows,coverage=cov or coverage(end=end,cut=cut))


def candidate(id='a',**kw):
    args=dict(id=id,generator_event='birth:'+id,decision_set='set0',object_version='o-v1',date_group='d0',
              source_episode='episode0',sampling_frame=SamplingFrame.CLOCK,created_at=0,known_at=0,
              decision='untraded',endpoint_group='E10',definition_id='price-v1')
    args.update(kw);return CandidateRecord(**args)


def definition(id='price-v1',**kw):
    args=dict(id=id,kind='price_path',cut=0,end=10,observation_process='certified_last_observed_mark')
    args.update(kw);return LabelDefinition(**args)


def record_outcome(ledger,id='a:v1',owner='a',*,terminal=0,supersedes=None,observation=None):
    d=next(d for d in ledger.definitions if d.id==next(c.definition_id for c in ledger.candidates if c.id==owner))
    observation=observation or ObservationEvidence(d.end,d.end+1,'obs-v1')
    points=() if terminal==0 else (PathPoint(d.end,0,Ticks(100+terminal),observation.certified_at),)
    return append_price_outcome(ledger,owner,d.id,target=replace(target(d.cut,d.end),definition_version=d.id),initial=Ticks(100),points=points,
        coverage=observation,up_ticks=int(d.favorable_distance),down_ticks=int(d.adverse_distance),
        outcome_id=id,supersedes=supersedes)


def ledger(ids=('a',),limits=DEFAULT_LIMITS):
    result=LabelLedger(limits);result.add_definition(definition())
    for i in ids: result.add_candidate(candidate(i))
    return result


def object_ledger(ids=('a',),*,versions=None,lower=100,upper=102):
    result=LabelLedger();targets={}
    for i in ids:
        version='object:'+i if versions is None else versions[i]
        d=definition('object-definition:'+i,kind='object_path',object_version=version,
            geometry_version='geometry:'+version,observation_process='certified_discrete_ticks')
        result.add_definition(d)
        result.add_candidate(candidate(i,object_version=version,definition_id=d.id,sampling_frame=SamplingFrame.OBJECT_BIRTH))
        targets[i]=ObjectTarget('target:'+i,version,d.cut,d.end,Band(F(lower),F(upper)),d.side,
            d.favorable_distance,d.adverse_distance,d.observation_process)
    return result,targets


def record_object(ledger,target,points,*,owner='a',initial=F(99),cov=None,id=None,supersedes=None):
    d=next(d for d in ledger.definitions if d.id==next(c.definition_id for c in ledger.candidates if c.id==owner))
    raw=canonical_json(geometry_source(target,d));ref=graph.payload_ref(raw,'object_geometry')
    return append_object_outcome(ledger,owner,d.id,target=target,initial=initial,points=points,
        coverage=cov or coverage(),geometry_ref=ref,geometry_bytes=raw,
        outcome_id=id or owner+':v1',supersedes=supersedes)


def typed_ledger(kind,*,id='a',cut=0,end=10,**kw):
    result=LabelLedger();d=definition(kind+':definition',kind=kind,cut=cut,end=end,**kw)
    result.add_definition(d);result.add_candidate(candidate(id,definition_id=d.id,created_at=cut,known_at=cut))
    return result,d


def record_oi(ledger,d,*,owner='a',reports=(),query=20,expiry=None,id='a:v1',supersedes=None,receipt_coverage=True):
    return append_oi_outcome(ledger,owner,d.id,prior_report=OIReport('R0','C','D0',10,10),
        reports=reports,position_date='D1',query_at=query,report_due=20,observation_boundary=25,
        boundary_known_at=25,receipt_coverage=receipt_coverage,expiry=expiry,outcome_id=id,supersedes=supersedes)


def data(outcome):
    return json.loads(outcome.payload)['data']


def retained_evidence(ledger):
    return {sha:bytes.fromhex(row['bytes']) for sha,row in json.loads(ledger.checkpoint())['evidence'].items()}


def dependency(id='c',kind='carried_state',start=0,end=15,known=0,fixture=None):
    raw=canonical_json(dict(format='TemporalDependencyEvidenceV1',id=id,kind=kind,start=start,end=end,known_at=known))
    ref=graph.payload_ref(raw,'temporal_dependency')
    if fixture is not None: fixture.payloads[ref.sha256]=raw
    return TemporalDependencyV1(id,kind,start,end,known,ref)


def sample(id='a',decision=0,end=10,known=11,role='train',deps=(),group=None,version='target-v1',parents=()):
    return TemporalSampleV1(id,group or 'd:'+id,decision,end,known,version,role,'E:'+id,parents,deps)


def plain(s):
    return dict(id=s.id,decision=s.decision_at,target_end=s.target_end,known=s.label_known_at,role=s.phase_role,
                dependencies=[dict(id=d.id,kind=d.kind,end=d.end,known=d.known_at) for d in s.dependencies])


def plain_temporal(s):
    return dict(id=s.id,date_group=s.date_group,decision_at=s.decision_at,target_end=s.target_end,
        label_known_at=s.label_known_at,target_version=s.target_version,phase_role=s.phase_role,
        endpoint_group=s.endpoint_group,parent_groups=list(s.parent_groups),
        dependencies=[dict(id=d.id,kind=d.kind,start=d.start,end=d.end,known_at=d.known_at,
            evidence_ref=dict(sha256=d.evidence_ref.sha256,size_bytes=d.evidence_ref.size_bytes,kind=d.evidence_ref.kind))
            for d in s.dependencies])


def fitted(id,role='model',fold='f',at=8,train=('a',),groups=('d0',),upstream=()):
    return FittedArtifact(id,role,fold,at,frozenset(train),frozenset(groups),min(at,5),upstream)


def temporal_graph(*,early=False,legacy=False):
    f=Fixture();f.namespace='V01V02'
    dep=dependency(fixture=f)
    a=sample('a',0,10,11,deps=(dep,),group='d0',version=f.target.sha256)
    b=sample('b',1,9,10,group='d1',version=f.target.sha256)
    e=sample('e',14 if early else 20,18 if early else 30,19 if early else 31,'outer',group='d2',version=f.target.sha256)
    pop=(a,b,e)
    fit=12 if early else 16;start=e.decision_at;end=20 if early else 40
    if legacy:
        pop=tuple(Sample(s.id,s.date_group,s.decision_at,s.label_known_at,s.target_end,s.target_version) for s in pop)
        fold=chronological_fold(pop,id='fold',fit_at=fit,evaluation_start=start,evaluation_end=end)
        evidence=graph.ValidatedFoldEvidence(pop,fold)
    else:
        fold=compile_temporal_fold(pop,id='fold',fit_at=fit,evaluation_start=start,evaluation_end=end)
        evidence=graph.ValidatedTemporalFoldEvidenceV1(pop,fold)
    fn=f.node('fold','fold',fold_evidence=evidence,**({} if legacy else {'execution':temporal_execution(f)}))
    nodes=[fn];reads=[];labels=[]
    by={s.id:s for s in pop}
    for i in fold.training_ids:
        s=by[i];te=s.dependency_end if legacy else s.target_end
        source=f.source('raw:'+i,row_id=i,value=1,observed=s.decision_at,known=s.decision_at,valid_until=100)
        label=f.node('label:'+i,'label',rows=(f.row(row_id=i,column='label',value=1,observed=te,known=s.label_known_at,valid_until=100),),
                     label_targets=(graph.LabelTarget(i,f.target,s.decision_at,te),))
        q=graph.ReadRequest(i,s.decision_at,s.decision_at,'fit_feature','Row.v1','probability',date_group=s.date_group,fold_node_id=fn.id)
        binding=graph.ReadBinding('x',source.id,'x',q)
        read=f.node('read:'+i,'read_manifest',read_manifest=graph.ReadManifest(f.namespace,(binding,),(graph.ReadRecord(binding,source.row_evidence[0]),),()),
                    dependencies=(f.dep('x',source,'value',('x',)),f.dep('fold',fn)))
        nodes.extend((source,label,read));reads.append(read);labels.append(label)
    n=len(fold.training_ids)
    evidence=graph.FitEvidence(fn.id,fit,fit,fold.training_ids,tuple(by[i].date_group for i in fold.training_ids),
        tuple(graph.LabelEvidence(i,l.id,'label',f.target) for i,l in zip(fold.training_ids,labels)),tuple(r.id for r in reads),f.target)
    artifact=FittedArtifact('frequency','conditional_frequency',fold.version,fit,frozenset(fold.training_ids),
        frozenset(by[i].date_group for i in fold.training_ids),max(by[i].label_known_at for i in fold.training_ids),())
    state=FrequencyModel('frequency',('x',),((),),(((0,),n,n),),(n+1)/(n+2),2.,'uniform',artifact,f.target.sha256,'supplied-reads')
    model=f.node('model','model',raw=canonical_json(state),fit_evidence=evidence,
        execution=replace(f.execution,configuration_json=canonical_json({'input_columns':['x']})),
        dependencies=(f.dep('fold',fn),*(f.dep('labels:'+l.logical_key,l,'fit_label',('label',)) for l in labels),*(f.dep(r.logical_key,r) for r in reads)))
    source=f.source('evaluation',row_id='e',value=1,observed=start,known=start,valid_until=end)
    nodes.extend((model,source))
    request=graph.ReadRequest('e',start,start+1,'OOF','Row.v1','probability',f.target,start,e.target_end,'d2',fn.id)
    binding=graph.ReadBinding('x',source.id,'x',request)
    return f,tuple(nodes),model,state,request,(binding,)


def temporal_execution(f,limits=DEFAULT_LIMITS):
    return replace(f.execution,configuration_json=canonical_json({'temporal_limits_v1':
        {field.name:getattr(limits,field.name) for field in fields(limits)}}))


class V01V02Tests(unittest.TestCase):
    def assert_path_reference(self,result,events,initial=100,ordered=True,complete=True):
        reference=literal.path(initial,[(p[0],p[1] if len(p)>2 else 0,p[2] if len(p)>2 else p[1]) for p in events],10,ordered=ordered,complete=complete)
        self.assertEqual((result.status,result.terminal_ticks,result.maximum_up_ticks,result.maximum_down_ticks,result.first_barrier,result.first_barrier_at),
                         tuple(reference[k] for k in ('state','terminal','up','down','barrier','at')))

    def test_v01_01(self):
        for events,first in [(((1,104),(2,96),(10,100)),'upper'),(((1,96),(2,104),(10,100)),'lower')]:
            r=path(events);self.assertEqual((r.terminal_ticks,r.maximum_up_ticks,r.maximum_down_ticks,r.first_barrier),(0,4,4,first));self.assert_path_reference(r,events)

    def test_v01_02(self):
        events=((1,0,104),(1,1,96),(10,0,100));r=path(events,coverage=coverage(ordered=False))
        self.assertEqual((r.status,r.first_barrier,r.terminal_ticks),('ambiguous','ambiguous',0));self.assert_path_reference(r,events,ordered=False)

    def test_v01_03(self):
        for prices,expected in [((101,103),(3,0)),((99,97),(0,3))]:
            events=tuple(enumerate(prices,1));r=path(events);self.assertEqual((r.maximum_up_ticks,r.maximum_down_ticks),expected);self.assert_path_reference(r,events)

    def test_v01_04(self):
        full=path();partial=path(coverage=coverage(end=5,cert=6))
        self.assertEqual((full.status,full.terminal_ticks,full.first_barrier),('observed',0,'neither'))
        self.assertEqual((partial.status,partial.terminal_ticks),('censored',None));self.assert_path_reference(full,());self.assert_path_reference(partial,(),complete=False)

    def test_v01_05(self):
        _,_,r=obj(((3,103),(4,105)));self.assertEqual((r['reach_status'],r['departure'],r['gap_crossings']),('no_contact','no_contact',(3,)))
        self.assertEqual(literal.object_path(99,((3,0,103),(4,0,105)),100,102)['gaps'],r['gap_crossings'])

    def test_v01_06(self):
        _,_,r=obj(((1,100),(2,103)));self.assertEqual((r['contact_at'],r['contact_price'],r['departure'],r['first_barrier_at']),(1,F(100),'favorable_first',2))
        ref=literal.object_path(99,((1,0,100),(2,0,103)),100,102);self.assertEqual(ref['contact'],(r['contact_at'],r['contact_price']))

    def test_v01_07(self):
        self.assertFalse(100<=99<=102)
        with self.assertRaises(ContractError):obj(mode='contact_at_cut',cov=coverage(end=5))

    def test_v01_08(self):
        _,_,r=obj(((10,100),));self.assertEqual((r['contact_at'],r['departure'],r['maximum_favorable_ticks'],r['maximum_adverse_ticks'],r['fixed_end']),(10,'unresolved',0,0,10))
        ref=literal.object_path(99,((10,0,100),),100,102)
        self.assertEqual((r['departure'],r['maximum_favorable_ticks'],r['maximum_adverse_ticks']),tuple(ref[k] for k in ('departure','favorable','adverse')))

    def test_v01_09(self):
        old,_,a=obj(((9,100),));new,_,b=obj(((11,103),),initial=100,cut=9,end=19,mode='contact_at_cut')
        self.assertEqual(a['departure'],'unresolved');self.assertEqual(b['departure'],'favorable_first');self.assertNotEqual(old.version,new.version)
        with self.assertRaises(ContractError):obj(((9,100),(11,103)))
        self.assertEqual(literal.interval_points(((9,0,100),(11,0,103)),0,10),((11,0),))
        self.assertEqual(literal.interval_points(((11,0,103),),9,19),())
        self.assertEqual(b['departure'],literal.object_path(100,((11,0,103),),100,102,cut=9,end=19,contact_at_cut=True)['departure'])

    def test_v01_10(self):
        self.assertEqual(literal.interval_points(((11,0,104),),0,10),((11,0),))
        with self.assertRaises(ContractError):path(((11,104),))
        with self.assertRaises(ContractError):obj(((11,104),))

    def test_v01_11(self):
        old,_,a=obj(((1,100),(2,106)),initial=110,lower=99,upper=101)
        new,_,b=obj(((1,100),(2,106)),initial=110,lower=119,upper=121,version='o-v2')
        self.assertEqual((a['reach_status'],b['reach_status']),('contact','no_contact'));self.assertNotEqual(old.version,new.version);self.assertEqual(old.band.lower,F(99))
        self.assertIsNotNone(literal.object_path(110,((1,0,100),(2,0,106)),99,101)['contact'])
        self.assertIsNone(literal.object_path(110,((1,0,100),(2,0,106)),119,121)['contact'])

    def test_v01_12(self):
        _,_,r=obj(((1,0,100),(1,1,106)),initial=110,lower=99,upper=101,cov=coverage(ordered=False))
        self.assertEqual((r['reach_status'],r['contact_at'],r['contact_price'],r['departure']),('contact',1,None,'ambiguous'))
        orders=[literal.object_path(110,tuple((1,i,p) for i,p in enumerate(prices)),99,101)
                for prices in ((100,106),(106,100))]
        self.assertEqual({v['contact'][0] for v in orders},{1})
        self.assertEqual({v['departure'] for v in orders},{'favorable_first','unresolved'})

    def test_v01_13(self):
        t,rows,r=obj(((1,0,96),(1,1,105),(2,0,96)),initial=95,lower=99,upper=101,cov=coverage(ordered=False))
        a=compatible_gap_evidence(t,F(95),rows,source_order_known=False)
        b=compatible_gap_evidence(t,F(95),tuple(reversed(rows)),source_order_known=False)
        self.assertEqual(a,b);self.assertEqual(a['compatible_gap_crossing_times'],((1,1),(1,2)))
        self.assertEqual((a['certain_crossing_time_set'],a['possible_crossing_time_set']),((1,),(1,2)))
        self.assertEqual(a['compatible_gap_crossing_times'],literal.gap_orders(F(95),[(1,(F(96),F(105))),(2,(F(96),))],F(99),F(101)))
        self.assertEqual(r['reach_status'],'no_contact')
        self.assertEqual(1*2*2+2*1*1,6)
        self.assertEqual(compatible_gap_evidence(t,F(95),rows,source_order_known=False,maximum_transition_work=6),a)
        with self.assertRaisesRegex(ContractError,'transition work'):
            compatible_gap_evidence(t,F(95),rows,source_order_known=False,maximum_transition_work=5)
        low_distinct=tuple(ExactPoint(1,i,F(100),1) for i in range(8))
        with self.assertRaisesRegex(ContractError,'transition work'):
            compatible_gap_evidence(t,F(95),low_distinct,source_order_known=False)

    def test_v01_14(self):
        cov=coverage(gaps=((5,7),));t,rows,r=obj(((2,0,100,2),(4,0,101,4),(7,0,101,7),(10,0,100,10)),cov=cov)
        facts=contact_partial_fact(t,rows,cov);self.assertEqual(facts,(('observed_contact',2,F(100)),));self.assertEqual(r['departure'],'censored')
        l,targets=object_ledger();o=record_object(l,targets['a'],rows,cov=cov)
        self.assertEqual(o.state,literal.observation_state(0,10,10,11,((5,7),)))
        self.assertEqual(o.observation.partial_facts,literal.partial_contact(((2,0,100,2),(4,0,101,4),(7,0,101,7),(10,0,100,10)),100,102,((5,7),)))
        self.assertEqual(o.observation.partial_facts,facts)
        for key in ('contact_at','contact_price','departure','first_barrier_at','maximum_favorable_ticks','maximum_adverse_ticks'):
            self.assertIsNone(data(o)[key])
        self.assertEqual(LabelLedger.restore(l.checkpoint()).checkpoint(),l.checkpoint())

    def test_v01_15(self):
        a=path(end=8,coverage=coverage(end=8,cert=9));b=path(end=10,coverage=coverage(end=8,cert=9))
        self.assertEqual((a.status,b.status),('observed','censored'));self.assertNotEqual(a.target_signature,b.target_signature)
        self.assertEqual(tuple(literal.observation_state(0,e,8,9) for e in (8,10)),('complete','pending'))

    def test_v01_16(self):
        self.assertEqual(literal.interval_points(((4,0,101),(5,0,101),(6,0,101)),0,10,((4,6),)),((4,0),(5,0)))
        for at in (4,5):
            with self.assertRaises(ContractError):path(((at,101),),coverage=coverage(gaps=((4,6),)))
        self.assertEqual(path(((6,101),),coverage=coverage(gaps=((4,6),))).status,'censored')

    def test_v01_17(self):
        primitive_cases=({'sequence':True},{'price_type':'int'},{'order':1},{'gaps':((2,5),(4,6))},{'version':''},{'at':0})
        self.assertEqual([literal.primitive_violations(**v) for v in primitive_cases],[(k,) for k in ('sequence','price','order','gaps','version','cut')])
        bad=(lambda:PathPoint(1,True,Ticks(100),1),lambda:PathPoint(1,0,100,1),lambda:coverage(ordered=1),
             lambda:coverage(gaps=((2,5),(4,6))),lambda:ObservationWindow(0,10,11,version=''),lambda:path(((0,100),)),
             lambda:ObservationWindow(0,10,11,version=1),lambda:obj(side=True),
             lambda:obj(version=1),lambda:definition(object_version=1),lambda:definition(policy_version=True))
        for call in bad:
            with self.subTest(call=call):
                with self.assertRaises(ContractError):call()
        self.assertEqual(coverage(gaps=((2,4),(4,6))).gaps,((2,4),(4,6)))

    def test_v01_18(self):
        r=path(((1,0,101,11),(10,0,102,20)),coverage=coverage(cert=12));self.assertEqual((r.maturity_at,r.observed_end),(20,10))
        s=Sample('a','d0',0,20,10,'t');fold=chronological_fold((s,),id='f',fit_at=15,evaluation_start=16,evaluation_end=30)
        self.assertEqual(dict(fold.purged)['a'],'label_not_mature_at_fit')
        self.assertEqual(r.maturity_at,max(12,11,20));self.assertGreater(r.maturity_at,15)

    def test_v01_19(self):
        l=LabelLedger();l.add_definition(definition())
        for i,status in zip(('a','b','c'),('selected','rejected','untraded')):l.add_candidate(candidate(i,decision=status));record_outcome(l,i+':v1',i)
        self.assertEqual(l.reconcile(('a','b','c')),(('a','complete'),('b','complete'),('c','complete')))
        self.assertEqual([c.decision for c in l.candidates].count('rejected'),1);self.assertEqual(len(l.candidates),3)
        self.assertFalse(any(literal.ledger_relation(('a','b','c'),tuple(c.id for c in l.candidates),tuple(o.candidate_id for o in l.outcomes)).values()))

    def test_v01_20(self):
        l=ledger(('a','b','c'));record_outcome(l);record_outcome(l,'c:v1','c')
        self.assertEqual(literal.ledger_relation(('a','b','c'),('a','b','c'),('a','c'))['missing_outcomes'],('b',))
        with self.assertRaisesRegex(ContractError,'missing outcomes: b'):l.reconcile(('a','b','c'))
        record_outcome(l,'b:v1','b')
        with self.assertRaisesRegex(ContractError,'duplicate outcome: b'):record_outcome(l,'b:duplicate','b')
        self.assertEqual(literal.ledger_relation(('a','b','b','c'),('a','b','c'),('a','b','c'))['duplicate_generator'],('b',))
        with self.assertRaisesRegex(ContractError,'duplicate identity: b'):l.reconcile(('a','b','b','c'))

    def test_v01_21(self):
        self.assertEqual(sampling_weight(candidate(inclusion_probability=F(1,4))),F(4));self.assertIsNone(sampling_weight(candidate()))
        with self.assertRaises(ContractError):candidate(inclusion_probability=.25)
        self.assertEqual(sampling_weight(candidate(inclusion_probability=F(1,4))),1/F(1,4))

    def test_v01_22(self):
        rows=tuple(candidate('a'+str(i),date_group='A') for i in range(1000))+(candidate('b',date_group='B'),)
        weights=dict(grouped_weights(rows));self.assertEqual(weights['a0'],F(1,1000));self.assertEqual(weights['b'],F(1))
        self.assertEqual(sum(weights[c.id] for c in rows if c.date_group=='A'),F(1));self.assertEqual(support_counts(rows)['dates'],2)
        self.assertEqual(tuple(grouped_weights(rows)),literal.equal_group_weights([(c.id,c.date_group) for c in rows]))

    def test_v01_23(self):
        a=definition();b=definition('prefix2',cut=1);self.assertNotEqual(a.version,b.version)
        rows=(candidate('p1'),candidate('p2',definition_id='prefix2'))
        self.assertEqual((support_counts(rows)['rows'],support_counts(rows)['endpoints']),(2,1))
        self.assertEqual(support_counts(rows),literal.group_support([dict(date='d0',episode='episode0',endpoint='E10')]*2))

    def test_v01_24(self):
        l,targets=object_ledger(('o1','o2'));points=(ExactPoint(2,0,F(100),2),)
        for i in ('o1','o2'):record_object(l,targets[i],points,owner=i)
        self.assertEqual({o.candidate_id for o in l.outcomes},{'o1','o2'})
        self.assertEqual({(data(o)['contact_at'],tuple(data(o)['contact_price'])) for o in l.outcomes},{(2,(100,1))})
        self.assertEqual({data(o)['object_version'] for o in l.outcomes},{'object:o1','object:o2'})
        self.assertEqual(literal.object_path(99,((2,0,100),),100,102)['contact'],(2,100))
        retained=[json.loads(retained_evidence(l)[item['ref']['sha256']])
                  for o in l.outcomes for item in json.loads(o.payload)['evidence'] if item['slot']=='source']
        self.assertEqual({tuple(record['points'][0][:2]) for record in retained},{(2,0)})

    def test_v01_25(self):
        rows=tuple(candidate(i,sampling_frame=frame) for frame,ids in [(SamplingFrame.CLOCK,('t0','t1','t2')),(SamplingFrame.OBJECT_BIRTH,('o1','o2')),(SamplingFrame.CONTACT,('o1@t2',)),(SamplingFrame.POLICY_TRAJECTORY,('p1',))] for i in ids)
        self.assertEqual([sum(c.sampling_frame==f for c in rows) for f in (SamplingFrame.CLOCK,SamplingFrame.OBJECT_BIRTH,SamplingFrame.CONTACT,SamplingFrame.POLICY_TRAJECTORY)],[3,2,1,1])
        self.assertEqual(next(c for c in rows if c.id=='o2').sampling_frame,SamplingFrame.OBJECT_BIRTH)
        ref=literal.frame_partition([(c.id,c.sampling_frame.value) for c in rows])
        self.assertEqual(ref,{'clock':('t0','t1','t2'),'object_birth':('o1','o2'),'contact':('o1@t2',),'policy_trajectory':('p1',)})

    def oi(self,reports=(),query=20,expiry=None):
        return oi_endpoint(OIReport('R0','C','D0',10,10),reports,contract='C',query_at=query,report_due=20,observation_boundary=25,boundary_known_at=25,expiry=expiry)

    def test_v01_26(self):
        report=OIReport('R1','C','D1',20,12);self.assertEqual(self.oi((report,),19)['state'],'pending')
        r=self.oi((report,));self.assertEqual((r['delta'],r['report_id'],r['known_at']),(2,'R1',20));self.assertEqual(literal.oi_query(10,[{'known':20,'count':12}],20,25),('complete',2))
        l,d=typed_ledger('oi_report',cut=10,end=20)
        before=record_oi(l,d,reports=(report,),query=19)
        observed=record_oi(l,d,reports=(report,),query=20,id='a:v2',supersedes='a:v1')
        self.assertEqual((before.state,data(before)['delta_oi']),literal.oi_query(10,[{'known':20,'count':12}],19,25))
        self.assertEqual((observed.state,data(observed)['delta_oi']),literal.oi_query(10,[{'known':20,'count':12}],20,25))
        self.assertEqual((data(observed)['report_id'],observed.observation.certified_at),('R1',20))

    def test_v01_27(self):
        reports=(OIReport('R1','C','D1',20,12),OIReport('R2','C','D1',25,11,'R1'))
        self.assertEqual((self.oi(reports,22)['report_id'],self.oi(reports,25)['delta']),('R1',1));self.assertEqual(reports[0].count,12)
        l,d=typed_ledger('oi_report',cut=10,end=20)
        first=record_oi(l,d,reports=reports,query=22)
        second=record_oi(l,d,reports=reports,query=25,id='a:v2',supersedes='a:v1')
        self.assertEqual((data(first)['report_id'],data(first)['delta_oi']),('R1',2))
        self.assertEqual((second.state,data(second)['delta_oi']),literal.oi_query(10,[{'known':20,'count':12},{'known':25,'count':11}],25,25))
        self.assertEqual((data(second)['supersedes_report_id'],second.endpoint_group,first.endpoint_group),('R1','E10','E10'))
        self.assertEqual(LabelLedger.restore(l.checkpoint()).outcomes,l.outcomes)
        at22,d22=typed_ledger('oi_report',cut=10,end=20)
        self.assertEqual(record_oi(at22,d22,reports=reports[:1],query=22).payload,first.payload)
        for bad in (replace(reports[0],supersedes='R0'),replace(reports[1],position_date='D2'),replace(reports[1],known_at=20)):
            with self.assertRaises(ContractError):self.oi((bad,) if bad.id=='R1' else (reports[0],bad),query=25)

    def test_v01_28(self):
        for query in (14,15,19,20,24,25,26):
            for expiry in (None,15):
                r=self.oi(query=query,expiry=expiry);self.assertEqual((r['state'],r['delta']),literal.oi_query(10,[],query,25,expiry))
                self.assertIsNone(r['delta'])
                l,d=typed_ledger('oi_report',cut=10,end=20)
                o=record_oi(l,d,query=query,expiry=expiry)
                expected={'pending':'pending','censored_missing_publication':'censored','expiry_terminal':'not_applicable'}[r['state']]
                self.assertEqual(o.state,expected)
                self.assertIsNone(data(o)['next_oi']);self.assertIsNone(data(o)['delta_oi'])
        l,d=typed_ledger('oi_report',cut=10,end=20)
        self.assertEqual(record_oi(l,d,query=26,receipt_coverage=False).state,'pending')

    def test_v01_29(self):
        rows=tuple(candidate('p'+str(i),endpoint_group='R1') for i in range(3));self.assertEqual((support_counts(rows)['rows'],support_counts(rows)['endpoints']),(3,1))
        self.assertEqual(support_counts(rows),literal.group_support([dict(date='d0',episode='episode0',endpoint='R1')]*3))
        l=LabelLedger()
        for i,cut in enumerate((10,11,12)):
            d=definition('prefix:'+str(i),kind='oi_report',cut=cut,end=20,endpoint_group='R1');l.add_definition(d)
            owner='p'+str(i);l.add_candidate(candidate(owner,created_at=cut,known_at=cut,definition_id=d.id,endpoint_group='R1'))
            record_oi(l,d,owner=owner,reports=(OIReport('R1','C','D1',20,12),),id=owner+':v1')
        self.assertEqual({data(o)['report_id'] for o in l.outcomes},{'R1'});self.assertEqual(len(l.reconcile(tuple(c.id for c in l.candidates))),3)

    def test_v01_30(self):
        versions={definition('p:'+p+':'+s,kind='policy_value',policy_version=p,simulator_version=s).version for p in ('full_exit','hold_to_deadline') for s in ('scenarioA','scenarioB')}
        self.assertEqual(len(versions),4)
        self.assertEqual(len({literal.canonical({'policy':p,'simulator':s}) for p in ('full_exit','hold_to_deadline') for s in ('scenarioA','scenarioB')}),len(versions))

    def test_v01_31(self):
        l,d=typed_ledger('policy_value',policy_version='limit-cancel10',simulator_version='s1')
        external={'schema':'ExternalPolicyOutcomeV1','candidate_id':'a','cut':0,'end':10,
            'policy_version':'limit-cancel10','simulator_version':'s1','fill_version':'f1','fee_version':'fee1',
            'account_version':'acct1','reward_target_signature':'reward-v1','fill_status':'nonfill','filled':False,
            'net_value_usd':[0,1],'cancel_at':10,'observation':{'start':0,'end':10,'certified_through':11,
                'gaps':[],'source_order_known':True,'version':'external-obs'}}
        raw=literal.canonical(external);ref=graph.payload_ref(raw,'external_policy_result')
        o=append_policy_outcome(l,'a',d.id,external_record=external,provenance_ref=ref,provenance_bytes=raw,outcome_id='a:v1')
        self.assertEqual((o.state,data(o)['filled'],data(o)['net_value_usd']),('complete',False,[0,1]))
        self.assertEqual(l.reconcile(('a',)),(('a','complete'),))
        self.assertEqual(retained_evidence(l)[ref.sha256],raw)
        self.assertEqual(json.loads(o.payload)['evidence'][0]['ref']['kind'],'external_policy_result')
        for key in ('policy_version','simulator_version','fill_version','fee_version','account_version','reward_target_signature'):
            self.assertEqual(data(o)[key],external[key])
        path_ledger,targets=object_ledger(('reach',))
        reached=record_object(path_ledger,targets['reach'],(ExactPoint(2,0,F(100),2),),owner='reach')
        self.assertEqual(data(reached)['reach_status'],'contact');self.assertNotEqual(o.payload_kind,reached.payload_kind)
        self.assertEqual(literal.object_path(99,((2,0,100),),100,102)['contact'],(2,100))
        for status,end,cert in (('pending',5,6),('censored',5,11)):
            partial={**external,'fill_status':status,'observation':{**external['observation'],'end':end,'certified_through':cert}}
            partial_raw=literal.canonical(partial);partial_ref=graph.payload_ref(partial_raw,'external_policy_result')
            pl,pd=typed_ledger('policy_value',policy_version='limit-cancel10',simulator_version='s1')
            result=append_policy_outcome(pl,'a',pd.id,external_record=partial,provenance_ref=partial_ref,provenance_bytes=partial_raw,outcome_id='a:v1')
            self.assertEqual(result.state,literal.observation_state(0,10,end,cert))
            self.assertIsNone(data(result)['filled']);self.assertIsNone(data(result)['net_value_usd'])

    def test_v01_32(self):
        prices=tuple(map(F,(100,102,100,104,100)));r=episode_assignments(prices,F(99),F(101),F(2))
        self.assertEqual(r,(1,None,1,None,2));self.assertEqual(r,literal.reset_episodes(prices,F(99),F(101),F(2)))

    def test_v01_33(self):
        l=ledger();record_outcome(l);raw=l.checkpoint();restored=LabelLedger.restore(raw)
        revision=record_outcome(l,'a:v2',terminal=1,supersedes='a:v1',observation=ObservationEvidence(10,12,'obs-v2'))
        record_outcome(restored,'a:v2',terminal=1,supersedes='a:v1',observation=ObservationEvidence(10,12,'obs-v2'))
        self.assertEqual(l.checkpoint(),restored.checkpoint())
        self.assertEqual(l.outcomes[0].id,'a:v1');before=l.checkpoint();l.append_outcome(revision);self.assertEqual(before,l.checkpoint())
        reference=literal.immutable_revision_ids((('a:v1',None,0),),(('a:v2','a:v1',1),('a:v2','a:v1',1)))
        self.assertEqual(reference,('accepted',tuple((o.id,o.supersedes,data(o)['terminal_ticks']) for o in l.outcomes)))
        modified=json.loads(revision.payload);modified['data']['terminal_ticks']=2
        with self.assertRaises(ContractError):l.append_outcome(replace(revision,payload=literal.canonical(modified)))
        self.assertEqual(literal.immutable_revision_ids(reference[1],(('a:v2','a:v1',2),))[0],'conflict')
        self.assertEqual(before,l.checkpoint())
        with tempfile.TemporaryDirectory() as d:
            store=ArtifactStore(Path(d));ref=l.publish(store);self.assertEqual(LabelLedger.read(store,ref).checkpoint(),l.checkpoint())

    def test_v01_34(self):
        self.assertEqual(censored_event_bounds(1,1,2),(F(1,4),F(3,4)));self.assertEqual(censored_event_bounds(1,1,2),literal.bounds(1,1,2))

    def test_v01_35(self):
        observed=future_profile_mass((2,3),(0,0),observed=True);missing=future_profile_mass((2,3),(0,0),observed=False)
        self.assertEqual(sum(observed['resulting_mass']),5);self.assertEqual(observed['future_mass'],(0,0));self.assertIsNone(missing['future_mass']);self.assertEqual(missing['state'],'censored')
        for complete in (True,False):
            l,d=typed_ledger('profile_mass')
            o=append_profile_outcome(l,'a',d.id,grid_version='grid:fixed',initial=(2,3),additions=(0,0),
                coverage=coverage(gaps=() if complete else ((5,7),)),outcome_id='a:v1')
            actual=data(o);expected=literal.fixed_grid((2,3),(0,0),complete)
            self.assertEqual(tuple(None if actual[k] is None else tuple(actual[k]) for k in ('resulting_mass','future_mass')),expected[:2])
            self.assertEqual(actual['no_new_volume'],expected[2]);self.assertEqual(l.reconcile(('a',)),(('a','complete' if complete else 'censored'),))

    def test_v01_36(self):
        self.assertGreater(5,0);self.assertLessEqual(5,5)
        with self.assertRaises(ContractError):admit_original_feature(0,5)
        self.assertTrue(admit_original_feature(5,5));self.assertEqual(contact_origin(0,10,5)['target_end'],10)
        self.assertTrue(contact_origin(0,10,5,new_end=15)['new_target_required'])

    def test_v02_01(self):
        rows=tuple(Sample(i,g,d,k,e,'target-v1') for i,g,d,k,e in CASES['V02-01']['inputs']['samples'])
        fold=chronological_fold(rows,id='f',fit_at=10,evaluation_start=11,evaluation_end=20,embargo_ns=1)
        self.assertEqual(fold.training_ids,('past',));self.assertEqual(fold.evaluation_ids,('NQ','ES'))
        self.assertEqual(dict(fold.purged),CASES['V02-01']['expected']['purged']);validate_fold_population(rows,fold)
        self.assertEqual((fold.training_ids,fold.evaluation_ids,fold.purged),literal.legacy_population(
            [(s.id,s.date_group,s.decision_at,s.label_known_at,s.dependency_end) for s in rows],10,11,20,1))

    def test_v02_02(self):
        rows=(Sample('NQ','d2',11,13,12,'t'),Sample('ES','d2',12,14,13,'t'))
        self.assertEqual(literal.group_splits((('NQ','d2',11),('ES','d2',12)),12,20),('d2',))
        with self.assertRaises(ContractError):chronological_fold(rows,id='f',fit_at=12,evaluation_start=12,evaluation_end=20)

    def test_v02_03(self):
        rows=(Sample('a','d0',1,3,2,'t'),Sample('b','d0',2,4,3,'t'))
        self.assertEqual(literal.group_splits((('a','d0',1),('b','d0',2)),10,20,2),('d0',))
        with self.assertRaises(ContractError):chronological_fold(rows,id='f',fit_at=10,evaluation_start=10,evaluation_end=20,training_start=2)

    def test_v02_04(self):
        rows=(Sample('mature','d0',0,10,9,'t'),Sample('touch','d1',0,10,10,'t'))
        fold=chronological_fold(rows,id='f',fit_at=10,evaluation_start=11,evaluation_end=20,embargo_ns=1)
        self.assertEqual(fold.training_ids,('mature',));self.assertEqual(fold.purged[0][0],'touch')
        self.assertEqual((fold.training_ids,fold.evaluation_ids,fold.purged),literal.legacy_population(
            (('mature','d0',0,10,9),('touch','d1',0,10,10)),10,11,20,1))

    def assert_temporal_reference(self,pop,fold):
        expected=literal.temporal([plain(s) for s in pop],fit=fold.fit_at,start=fold.evaluation_start,end=fold.evaluation_end,
            embargo=fold.embargo_ns,training_start=fold.training_start,roles=fold.training_roles)
        actual=(fold.training_ids,fold.evaluation_ids,tuple((e.sample_id,e.reason,e.dependency_ids) for e in fold.exclusions))
        self.assertEqual(actual,expected)
        self.assertEqual(fold.version,literal.temporal_identity([plain_temporal(s) for s in pop],id=fold.id,
            fit=fold.fit_at,start=fold.evaluation_start,end=fold.evaluation_end,embargo=fold.embargo_ns,
            training_start=fold.training_start,roles=fold.training_roles))

    def test_v02_05(self):
        pop=(sample('a',3,4,5,deps=(dependency(kind='raw_past',end=3),)),sample('e',10,12,13,'outer',deps=(dependency('e:raw','raw_past',end=9),)))
        fold=compile_temporal_fold(pop,id='f',fit_at=8,evaluation_start=10,evaluation_end=20)
        self.assertEqual(fold.training_ids,('a',));self.assertFalse(fold.exclusions);self.assert_temporal_reference(pop,fold)

    def test_v02_06(self):
        pop=(sample('a',1,5,20),)
        fold=compile_temporal_fold(pop,id='f',fit_at=10,evaluation_start=11,evaluation_end=20)
        self.assertEqual((fold.exclusions[0].reason,pop[0].target_end),('label_not_mature_at_fit',5));self.assert_temporal_reference(pop,fold)

    def test_v02_07(self):
        f=Fixture();f.namespace='heldout-edge'
        pop=(sample('a',0,4,5,group='d0',version=f.target.sha256),sample('b',10,14,15,'outer',group='d1',version=f.target.sha256))
        fold=compile_temporal_fold(pop,id='f',fit_at=8,evaluation_start=10,evaluation_end=20)
        fn=f.node('fold','fold',execution=temporal_execution(f),fold_evidence=graph.ValidatedTemporalFoldEvidenceV1(pop,fold))
        source=f.source('raw:a',row_id='a',value=1,observed=0,known=0)
        labela=f.node('label:a','label',rows=(f.row(row_id='a',column='label',value=1,observed=4,known=5),),label_targets=(graph.LabelTarget('a',f.target,0,4),))
        labelb=f.node('label:b','label',rows=(f.row(row_id='b',column='label',value=0,observed=14,known=15),),label_targets=(graph.LabelTarget('b',f.target,10,14),))
        q=graph.ReadRequest('a',0,0,'fit_feature','Row.v1','probability',date_group='d0',fold_node_id=fn.id)
        binding=graph.ReadBinding('x',source.id,'x',q)
        read=f.node('training-read:a','read_manifest',read_manifest=graph.ReadManifest(f.namespace,(binding,),(graph.ReadRecord(binding,source.row_evidence[0]),),()),dependencies=(f.dep('x',source,'value',('x',)),f.dep('fold',fn)))
        fit=graph.FitEvidence(fn.id,8,8,('a',),('d0',),(graph.LabelEvidence('a',labela.id,'label',f.target),),(read.id,),f.target)
        deps=(f.dep('fold',fn),f.dep('train',read),f.dep('labels',labela,'fit_label',('label',)))
        state=f.node('s','transform',raw=canonical_json({'means':[1.],'scales':[1.]}),fit_evidence=fit,dependencies=deps)
        consumer=f.node('m','transform',raw=canonical_json({'means':[1.],'scales':[1.]}),fit_evidence=fit,dependencies=(*deps,f.dep('state',state)))
        core=(fn,source,labela,read)
        with tempfile.TemporaryDirectory() as d:
            store=graph.SemanticArtifactStore(d,f.namespace)
            good=store.commit('clean',(consumer.id,),(*core,state,consumer),f.payloads);store.read_commit(good.key)
            self.assertEqual(literal.actual_fit_relation(('a',),('a',),('a',)),{'extra_labels':(),'extra_reads':(),'missing_reads':()})
            for use in ('fit_label','provenance'):
                self.assertEqual(literal.actual_fit_relation(('a',),('a','b'),('a',))['extra_labels'],('b',))
                bad=replace(state,dependencies=(*state.dependencies,f.dep('heldout',labelb,use,('label',))))
                downstream=replace(consumer,dependencies=(*deps,f.dep('state',bad)))
                with self.assertRaises(ContractError):store.commit('bad:'+use,(downstream.id,),(*core,labelb,bad,downstream),f.payloads)
            dishonest=replace(fit,training_sample_ids=('a','b'),training_groups=('d0','d1'),training_label_refs=(*fit.training_label_refs,graph.LabelEvidence('b',labelb.id,'label',f.target)))
            bad=replace(state,fit_evidence=dishonest,dependencies=(*state.dependencies,f.dep('heldout',labelb,'fit_label',('label',))))
            with self.assertRaises(ContractError):store.commit('dishonest',(bad.id,),(*core,labelb,bad),f.payloads)

    def indirect(self,role):
        s=Sample('b','d2',10,15,14,'t');up=fitted(role,role,groups=('d2',));m=fitted('m',upstream=(role,))
        errors,closure=literal.fit_edges({'m':{'at':8,'fold':'f','parents':(role,),'groups':('d0',)},
            role:{'at':8,'fold':'f','groups':('d2',)}},'m',row='b',date='d2',cut=10,fold='f')
        self.assertEqual(errors,(('heldout',role),));self.assertEqual(set(closure),{'m',role})
        with self.assertRaises(ContractError):validate_oof(s,'m',(m,up),fold_version='f')

    def test_v02_08(self):self.indirect('scaler')
    def test_v02_09(self):self.indirect('feature_discovery')
    def test_v02_10(self):self.indirect('residual_baseline')
    def test_v02_11(self):self.indirect('encoder')
    def test_v02_12(self):self.indirect('gate')
    def test_v02_13(self):self.indirect('calibrator')

    def test_v02_14(self):
        s=Sample('b','d2',10,15,14,'t');m=fitted('m',upstream=('s',))
        nodes={'m':{'at':8,'fold':'f','parents':('s',)}}
        self.assertEqual(literal.fit_edges(nodes,'m',row='b',date='d2',cut=10,fold='f')[0],(('missing','s'),))
        with self.assertRaises(ContractError):validate_oof(s,'m',(m,),fold_version='f')
        nodes['s']={'at':8,'fold':'f','parents':('m',)}
        self.assertEqual(literal.fit_edges(nodes,'m',row='b',date='d2',cut=10,fold='f')[0],(('cycle','m'),('cycle','s')))
        with self.assertRaises(ContractError):validate_oof(s,'m',(m,fitted('s',upstream=('m',))),fold_version='f')

    def test_v02_15(self):
        s=Sample('b','d2',10,15,14,'t');base=fitted('base',fold='f1');m=fitted('m',fold='f2',upstream=('base',))
        nodes={'m':{'at':8,'fold':'f2','parents':('base',)},'base':{'at':8,'fold':'f1'}}
        expected=literal.fit_edges(nodes,'m',row='b',date='d2',cut=10,fold='f2',routes={'base':'f1'})
        self.assertEqual(validate_oof(s,'m',(m,base),fold_version='f2',upstream_fold_routes={'base':'f1'}),('base','m'))
        self.assertEqual(expected,((),('base','m')))
        for routes in ({},{'base':'wrong'}):
            self.assertEqual(literal.fit_edges(nodes,'m',row='b',date='d2',cut=10,fold='f2',routes=routes)[0],(('route','base'),))
            with self.assertRaises(ContractError):validate_oof(s,'m',(m,base),fold_version='f2',upstream_fold_routes=routes)

    def test_v02_16(self):
        f,nodes,model,state,request,bindings=temporal_graph(early=True)
        read=next(n for n in nodes if n.kind=='read_manifest');record=read.read_manifest.reads[0]
        bad_request=replace(record.binding.request,row_id='a',date_group='d0',decision_cut=0,assembled_at=0)
        source=f.source('undeclared:a',row_id='a',value=1,observed=0,known=0)
        binding=replace(record.binding,node_id=source.id,request=bad_request)
        badread=replace(read,read_manifest=graph.ReadManifest(f.namespace,(binding,),(graph.ReadRecord(binding,source.row_evidence[0]),),()),dependencies=(f.dep('x',source,'value',('x',)),next(d for d in read.dependencies if d.slot=='fold')))
        badfit=replace(model.fit_evidence,actual_training_read_manifests=(badread.id,))
        badmodel=replace(model,fit_evidence=badfit,dependencies=tuple(replace(d,source_id=badread.id) if d.source_id==read.id else d for d in model.dependencies))
        proposed=tuple(n for n in nodes if n.id not in (read.id,model.id))+ (source,badread,badmodel)
        self.assertEqual(literal.actual_fit_relation(('b',),('b',),('a',)),{'extra_labels':(),'extra_reads':('a',),'missing_reads':('b',)})
        with self.assertRaises(ContractError):graph.validate_closure(tuple(n.id for n in proposed),proposed,f.payloads,f.namespace)
        fn=next(n for n in nodes if n.kind=='fold');pop=fn.fold_evidence.population
        examples=tuple(BinaryExample(s,(),1) for s in pop)
        class NoReads:
            calls=0
            def predict(self,*args,**kwargs):
                self.calls+=1
                raise AssertionError('invalid temporal fit reached a base prediction')
        base=NoReads()
        forged=replace(fn.fold_evidence.fold,training_ids=('a','b'),exclusions=())
        for invalid,limit in ((forged,DEFAULT_LIMITS),(fn.fold_evidence.fold,replace(DEFAULT_LIMITS,max_temporal_population=2))):
            with self.assertRaises(ContractError):fit_sigmoid_calibration(base,examples,invalid,l2_strength=1.,limits=limit)
            self.assertEqual(base.calls,0)

    def stages(self):
        a=sample('a',10,11,12);b=sample('b',11,12,13);c=sample('c',12,13,14)
        pop=(a,b,c)
        producer=FitStage('base','expert',pop,compile_temporal_fold(pop,id='producer',fit_at=8,evaluation_start=10,evaluation_end=20),8)
        consumer=FitStage('cal','calibrator',pop,compile_temporal_fold(pop,id='consumer',fit_at=20,evaluation_start=30,evaluation_end=40),20)
        return producer,consumer

    def test_v02_17(self):
        p,c=self.stages()
        self.assertEqual(literal.required_oof_rows(('a','b','c'),('a','c')),('b',))
        with self.assertRaises(ContractError):compile_oof_schedule((p,c),(OOFEdge('base','cal',('a','c')),))
        self.assertEqual(compile_oof_schedule((p,c),(OOFEdge('base','cal',('a','b','c')),)),(('base','cal','a'),('base','cal','b'),('base','cal','c')))
        self.assertEqual(literal.required_oof_rows(('a','b','c'),('a','b','c')),())

    def test_v02_18(self):
        pop=(sample('b',0,4,5,'outer'),)
        fold=compile_temporal_fold(pop,id='development',fit_at=8,evaluation_start=10,evaluation_end=20)
        self.assertEqual(fold.training_ids,());self.assertEqual(fold.exclusions[0].reason,'forbidden_phase_role')
        self.assert_temporal_reference(pop,fold)
        with self.assertRaises(ContractError):compile_temporal_fold(pop,id='bad',fit_at=8,evaluation_start=10,evaluation_end=20,training_roles=('outer',))

    def test_v02_19(self):
        s=Sample('b','d2',15,20,19,'t');up=fitted('up',at=12);consumer=fitted('m',at=11,upstream=('up',))
        self.assertEqual(literal.fit_edges({'m':{'at':11,'fold':'f','parents':('up',)},'up':{'at':12,'fold':'f'}},'m',row='b',date='d2',cut=15,fold='f')[0],(('edge_completion','up'),))
        with self.assertRaises(ContractError):validate_oof(s,'m',(up,consumer),fold_version='f')
        with self.assertRaises(ContractError):validate_oof(s,'m',(fitted('m',at=16),),fold_version='f')
        self.assertEqual(literal.fit_edges({'m':{'at':16,'fold':'f'}},'m',row='b',date='d2',cut=15,fold='f')[0],(('prediction_completion','m'),))

    def test_v02_20(self):
        pop=(sample('a',3,4,5,deps=(dependency('raw','raw_past',end=3),)),sample('b',1,4,5,deps=(dependency('outcome','carried_state',end=12),)),sample('e1',10,15,16,'outer'),sample('e2',11,16,17,'outer'))
        exact=compile_temporal_fold(pop,id='exact',fit_at=8,evaluation_start=10,evaluation_end=20)
        conservative=compile_temporal_fold(pop,id='conservative',fit_at=8,evaluation_start=10,evaluation_end=20,embargo_ns=6)
        self.assertEqual((exact.training_ids,conservative.training_ids),(('a',),()));self.assertEqual(exact.evaluation_ids,conservative.evaluation_ids);self.assertEqual(exact.evaluation_ids,('e1','e2'))
        self.assert_temporal_reference(pop,exact);self.assert_temporal_reference(pop,conservative)

    def test_v02_21(self):
        pop=(sample(),);fold=compile_temporal_fold(pop,id='f1',fit_at=12,evaluation_start=20,evaluation_end=40)
        self.assert_temporal_reference(pop,fold)
        raw=temporal_checkpoint(pop,fold);self.assertEqual(restore_temporal_checkpoint(raw),(pop,fold))
        self.assertEqual(raw,literal.canonical(json.loads(raw)))
        self.assertNotEqual(fold.version,replace(fold,id='f2').version)
        for modified in ((replace(pop[0],target_version='t2'),),(replace(pop[0],dependencies=(dependency(),)),)):
            with self.assertRaises(ContractError):validate_temporal_fold_population(modified,fold)
            new=compile_temporal_fold(modified,id='f1',fit_at=12,evaluation_start=20,evaluation_end=40);self.assertNotEqual(new.version,fold.version)
            self.assert_temporal_reference(modified,new)
            self.assertNotEqual(literal.canonical([plain(s)|{'target_version':s.target_version} for s in modified]),
                                literal.canonical([plain(s)|{'target_version':s.target_version} for s in pop]))
        with self.assertRaises(ContractError):restore_temporal_checkpoint(raw,limits=replace(DEFAULT_LIMITS,max_temporal_population=2))

    def test_v02_22(self):
        pop=(Sample('a','d0',0,3,2,'t'),Sample('b','d1',1,4,3,'t'),Sample('e','d2',10,13,12,'t'))
        fold=chronological_fold(pop,id='f',fit_at=8,evaluation_start=10,evaluation_end=20)
        self.assertEqual(literal.legacy_population((('a','d0',0,3,2),('b','d1',1,4,3),('e','d2',10,13,12)),8,10,20)[0],('a','b'))
        with self.assertRaises(ContractError):validate_fold_population(pop,replace(fold,training_ids=('a',)))
        typed=(sample('a',0,2,3),sample('b',1,3,4),sample('e',10,12,13,'outer'))
        tf=compile_temporal_fold(typed,id='f',fit_at=8,evaluation_start=10,evaluation_end=20)
        self.assert_temporal_reference(typed,tf)
        with self.assertRaises(ContractError):validate_temporal_fold_population(typed,replace(tf,training_ids=('a',)))

    def test_v02_23(self):
        s=sample(known=16,deps=(dependency(),));self.assertEqual((s.target_end,s.dependency_end,s.label_known_at),(10,15,16));self.assertEqual(graph.sample_target_end(s),10)
        raw=plain(s);self.assertEqual((raw['target_end'],max(d['end'] for d in raw['dependencies']),raw['known']),(10,15,16))

    def test_v02_24(self):
        self.assertGreater(24,10);self.assertTrue(all(at>12 for at in (20,21)))
        with self.assertRaises(ContractError):compile_temporal_fold((sample('a',20,22,23),sample('b',21,23,24)),id='reverse',fit_at=24,evaluation_start=10,evaluation_end=12)

    def test_v02_25(self):
        design=json.loads((Path(__file__).parents[1]/'reports/v01-v02-design.json').read_text())
        self.assertEqual(len(design['phase_ids']),32)
        self.assertEqual(set(design['phase_ids']),set(literal.phase_records(('V01','V01.LABEL_COVERAGE','V02','V02.LINEAGE'))))
        for unit in ('V01','V01.LABEL_COVERAGE','V02','V02.LINEAGE'):
            self.assertEqual([f'EX-{unit}-P{i}' for i in range(8)],[p for p in design['phase_ids'] if p.startswith(f'EX-{unit}-P')])
        self.assertFalse(design['whole_unit_or_economic_completion_claim'])

    def test_v02_26(self):
        f,nodes,model,state,request,bindings=temporal_graph(early=True)
        fn=next(n for n in nodes if n.kind=='fold');a=next(s for s in fn.fold_evidence.population if s.id=='a')
        self.assertEqual(fn.fold_evidence.fold.training_ids,('b',));self.assertEqual((a.target_end,a.dependency_end),(10,15))
        self.assertEqual(fn.fold_evidence.fold.exclusions[0].dependency_ids,('c',))
        with tempfile.TemporaryDirectory() as d:
            store=graph.SemanticArtifactStore(d,f.namespace);ref=store.commit('early',tuple(n.id for n in nodes),nodes,f.payloads)
            store.read_commit(ref.key)
            invalid=replace(model,fit_evidence=replace(model.fit_evidence,training_sample_ids=('a','b'),training_groups=('d0','d1')))
            bad=tuple(invalid if n.id==model.id else n for n in nodes)
            with self.assertRaises(ContractError):store.commit('forged',tuple(n.id for n in bad),bad,f.payloads)
            labela=f.node('excluded-label:a','label',rows=(f.row(row_id='a',column='label',value=1,observed=10,known=11,valid_until=100),),
                label_targets=(graph.LabelTarget('a',f.target,0,10),))
            extra_label=replace(model,dependencies=(*model.dependencies,f.dep('excluded-label',labela,'fit_label',('label',))))
            bad=tuple(n for n in nodes if n.id!=model.id)+(labela,extra_label)
            self.assertEqual(literal.actual_fit_relation(('b',),('a','b'),('b',))['extra_labels'],('a',))
            with self.assertRaises(ContractError):store.commit('excluded-label',(extra_label.id,),bad,f.payloads)
            sourcea=f.source('excluded-feature:a',row_id='a',value=1,observed=0,known=0,valid_until=100)
            q=graph.ReadRequest('a',0,0,'fit_feature','Row.v1','probability',date_group='d0',fold_node_id=fn.id)
            binding=graph.ReadBinding('x',sourcea.id,'x',q)
            reada=f.node('excluded-read:a','read_manifest',read_manifest=graph.ReadManifest(f.namespace,(binding,),
                (graph.ReadRecord(binding,sourcea.row_evidence[0]),),()),dependencies=(f.dep('x',sourcea,'value',('x',)),f.dep('fold',fn)))
            extra_read=replace(model,fit_evidence=replace(model.fit_evidence,
                actual_training_read_manifests=(*model.fit_evidence.actual_training_read_manifests,reada.id)),
                dependencies=(*model.dependencies,f.dep('excluded-read',reada)))
            bad=tuple(n for n in nodes if n.id!=model.id)+(sourcea,reada,extra_read)
            self.assertEqual(literal.actual_fit_relation(('b',),('b',),('a','b'))['extra_reads'],('a',))
            with self.assertRaises(ContractError):store.commit('excluded-feature',(extra_read.id,),bad,f.payloads)
        self.assert_temporal_reference(fn.fold_evidence.population,fn.fold_evidence.fold)

    def test_v02_27(self):
        f,nodes,model,state,request,bindings=temporal_graph()
        fn=next(n for n in nodes if n.kind=='fold');self.assertEqual(fn.fold_evidence.fold.training_ids,('a','b'))
        self.assertEqual(next(n for n in nodes if n.logical_key=='label:a').label_targets[0].target_end,10)
        with tempfile.TemporaryDirectory() as d:
            store=graph.SemanticArtifactStore(d,f.namespace);ref=store.commit('later',tuple(n.id for n in nodes),nodes,f.payloads)
            fresh=graph.SemanticArtifactStore(d,f.namespace);restored=graph.restore_bound_model(fresh,ref,model.id)
            value,reads=restored.predict_committed(fresh,ref,model.id,graph.ReadSession(fresh,ref,bindings))
            self.assertEqual(value,F(3,4));self.assertEqual(value,literal.beta_frequency(2,2));self.assertEqual(request.target_end,30);self.assertEqual(len(reads.reads),1)
            with self.assertRaises(ContractError):restored.predict_committed(fresh,ref,model.id,graph.ReadSession(fresh,ref,(replace(bindings[0],request=replace(request,target_end=35)),)))
            dep=fn.fold_evidence.population[0].dependencies[0];bad_payloads=dict(f.payloads);bad_payloads[dep.evidence_ref.sha256]=dep.evidence_bytes.replace(b'15',b'13')
            with self.assertRaises(IntegrityError):graph.validate_closure(tuple(n.id for n in nodes),nodes,bad_payloads,f.namespace)
            changed_bytes=dep.evidence_bytes.replace(b'15',b'13')
            changed_ref=graph.payload_ref(changed_bytes,dep.evidence_ref.kind)
            for variant,altered_dep,payloads in (
                ('metadata-only',replace(dep,end=13),f.payloads),
                ('matching-hash-wrong-metadata',replace(dep,evidence_ref=changed_ref),{**f.payloads,changed_ref.sha256:changed_bytes})):
                modified=(replace(fn.fold_evidence.population[0],dependencies=(altered_dep,)),*fn.fold_evidence.population[1:])
                mf=compile_temporal_fold(modified,id='fold',fit_at=16,evaluation_start=20,evaluation_end=40)
                altered_fn=replace(fn,fold_evidence=graph.ValidatedTemporalFoldEvidenceV1(modified,mf))
                self.assertEqual(mf.training_ids,literal.temporal([plain(s) for s in modified],fit=16,start=20,end=40)[0])
                with self.assertRaisesRegex(IntegrityError,'dependency evidence bytes disagree'):
                    store.commit(variant,(altered_fn.id,),(altered_fn,),payloads)
            label=next(n for n in nodes if n.logical_key=='label:a')
            badlabel=replace(label,label_targets=(replace(label.label_targets[0],target_end=15),))
            badmodel=replace(model,fit_evidence=replace(model.fit_evidence,training_label_refs=tuple(replace(l,label_node_id=badlabel.id) if l.label_node_id==label.id else l for l in model.fit_evidence.training_label_refs)),dependencies=tuple(replace(dep,source_id=badlabel.id) if dep.source_id==label.id else dep for dep in model.dependencies))
            badnodes=tuple(badlabel if n.id==label.id else badmodel if n.id==model.id else n for n in nodes)
            with self.assertRaises(ContractError):graph.validate_closure(tuple(n.id for n in badnodes),badnodes,f.payloads,f.namespace)
            late_label=replace(label,row_evidence=(replace(label.row_evidence[0],input_known_at=12),))
            late_model=replace(model,fit_evidence=replace(model.fit_evidence,training_label_refs=tuple(
                replace(l,label_node_id=late_label.id) if l.label_node_id==label.id else l for l in model.fit_evidence.training_label_refs)),
                dependencies=tuple(replace(dep,source_id=late_label.id) if dep.source_id==label.id else dep for dep in model.dependencies))
            late_nodes=tuple(late_label if n.id==label.id else late_model if n.id==model.id else n for n in nodes)
            self.assertNotEqual(late_label.row_evidence[0].input_known_at,11)
            with self.assertRaises(ContractError):store.commit('maturity-mismatch',(late_model.id,),late_nodes,f.payloads)
        # Actual direct callers retain temporal population validation and input audit.
        population=fn.fold_evidence.population
        examples=tuple(BinaryExample(s,(InputValue('x','raw:'+s.id,s.decision_at,b'1'),),1) for s in population)
        rows,data,manifests,deps=_training(examples,fn.fold_evidence.fold,('x',),())
        self.assertEqual(tuple(e.sample.id for e in rows),('a','b'))
        self.assert_temporal_reference(population,fn.fold_evidence.fold)

    def test_v02_28(self):
        schema_bytes=(Path(__file__).parent/'fixtures/v01_v02_legacy_wire_schema.json').read_bytes()
        self.assertEqual(hashlib.sha256(schema_bytes).hexdigest(),'806d6339f765174d541951675e091855b771359e8e9dad34c0789ee126df7a27')
        schema=json.loads(schema_bytes);field_schema={'ArtifactRef':['sha256','size_bytes','kind']}
        for entry in schema.values():
            if type(entry) is dict and 'fields' in entry:field_schema.update(entry['fields'])
        sample_vector=Sample('a','d0',0,11,10,'target-v1')
        self.assertEqual(hashlib.sha256(graph._encode(sample_vector)).hexdigest(),schema['legacy_sample_vector']['sha256'])
        for key in ('legacy_sample_vector','legacy_fold_vector','legacy_fold_evidence_vector'):
            raw=schema[key]['canonical_bytes_utf8'].encode();decoded=graph._decode(raw)
            self.assertEqual(graph._encode(decoded),raw);self.assertEqual(literal.legacy_encode(decoded,field_schema),raw)
        raw=json.loads(schema['legacy_sample_vector']['canonical_bytes_utf8']);raw['value']['fields']['target_end']=None
        with self.assertRaises(ContractError):graph._decode(canonical_json(raw))
        f,nodes,model,state,request,bindings=temporal_graph(legacy=True)
        for n in nodes:self.assertEqual(graph._encode(n),literal.legacy_encode(n,field_schema))
        with tempfile.TemporaryDirectory() as d:
            store=graph.SemanticArtifactStore(d,f.namespace);ref=store.commit('legacy',tuple(n.id for n in nodes),nodes,f.payloads)
            old_files={str(p.relative_to(d)):p.read_bytes() for p in Path(d).rglob('*') if p.is_file()}
            commit=store.read_commit('legacy');raw=literal.legacy_encode((commit.closure.roots,commit.closure.nodes),field_schema)
            self.assertEqual(ref.manifest_ref.sha256,hashlib.sha256(raw).hexdigest())
            fresh=graph.SemanticArtifactStore(d,f.namespace);restored=graph.restore_bound_model(fresh,ref,model.id)
            self.assertEqual(canonical_json(restored),canonical_json(state));self.assertEqual(restored.predict_committed(fresh,ref,model.id,graph.ReadSession(fresh,ref,bindings))[0],F(3,4))
            self.assertEqual(old_files,{str(p.relative_to(d)):p.read_bytes() for p in Path(d).rglob('*') if p.is_file()})

    def test_temporal_actual_oof_route(self):
        f=Fixture();f.namespace='temporal-route'
        pop=(sample('p',-10,-5,-4,group='dp',version=f.target.sha256),
             sample('a',0,10,11,deps=(dependency(fixture=f),),group='d0',version=f.target.sha256),
             sample('b',1,9,10,group='d1',version=f.target.sha256),
             sample('e',20,30,31,'outer',group='d2',version=f.target.sha256))
        by={s.id:s for s in pop};nodes=[]
        def label(i):
            s=by[i]
            n=f.node('label:'+i,'label',rows=(f.row(row_id=i,column='label',value=1,observed=s.target_end,known=s.label_known_at,valid_until=100),),label_targets=(graph.LabelTarget(i,f.target,s.decision_at,s.target_end),))
            nodes.append(n);return n
        labels={i:label(i) for i in ('p','a','b')}
        def raw(i):
            s=by[i];n=f.source('raw:'+i,row_id=i,value=1,observed=s.decision_at,known=s.decision_at,valid_until=s.target_end)
            nodes.append(n);return n
        sources={i:raw(i) for i in by}
        pf=compile_temporal_fold(pop,id='producer',fit_at=-1,evaluation_start=0,evaluation_end=2)
        pn=f.node('producer-fold','fold',execution=temporal_execution(f),fold_evidence=graph.ValidatedTemporalFoldEvidenceV1(pop,pf));nodes.append(pn)
        def reads(key,i,source,fn,purpose,assembled=None):
            s=by[i];at=s.decision_at
            q=graph.ReadRequest(i,at,at if assembled is None else assembled,purpose,'Row.v1','probability',
                f.target if source.kind=='oof_prediction' or purpose=='OOF' else None,
                at if source.kind=='oof_prediction' or purpose=='OOF' else None,
                s.target_end if source.kind=='oof_prediction' or purpose=='OOF' else None,s.date_group,fn.id)
            binding=graph.ReadBinding('x',source.id,'x',q)
            n=f.node(key,'read_manifest',read_manifest=graph.ReadManifest(f.namespace,(binding,),(graph.ReadRecord(binding,source.row_evidence[0]),),()),dependencies=(f.dep('x',source,'value',('x',)),f.dep('fold',fn)))
            nodes.append(n);return n
        pr=reads('producer-training','p',sources['p'],pn,'fit_feature')
        def model(key,fn,training_reads):
            fold=fn.fold_evidence.fold;ids=fold.training_ids
            fit=graph.FitEvidence(fn.id,fold.fit_at,fold.fit_at,ids,tuple(by[i].date_group for i in ids),
                tuple(graph.LabelEvidence(i,labels[i].id,'label',f.target) for i in ids),tuple(r.id for r in training_reads),f.target)
            artifact=FittedArtifact(key,'conditional_frequency',fold.version,fold.fit_at,frozenset(ids),frozenset(by[i].date_group for i in ids),max(by[i].label_known_at for i in ids),())
            n=len(ids);state=FrequencyModel(key,('x',),((),),(((0,),n,n),),(n+1)/(n+2),2.,'uniform',artifact,f.target.sha256,'supplied-route')
            spec=f.node(key,'model',raw=canonical_json(state),fit_evidence=fit,execution=replace(f.execution,configuration_json=canonical_json({'input_columns':['x']})),
                dependencies=(f.dep('fold',fn),*(f.dep('label:'+i,labels[i],'fit_label',('label',)) for i in ids),*(f.dep(r.logical_key,r) for r in training_reads)))
            nodes.append(spec);return spec,state
        producer,producer_state=model('producer',pn,(pr,))
        predictions={}
        for i in ('a','b'):
            s=by[i];read=reads('producer-inference:'+i,i,sources[i],pn,'OOF')
            evidence=graph.PredictionEvidence(i,f.target,s.decision_at,s.target_end,s.decision_at,s.decision_at,s.decision_at,producer.id,read.id,'OOF')
            row=replace(f.row(row_id=i,value=2/3,observed=s.decision_at,known=s.decision_at,valid_until=s.target_end),availability_basis='derived')
            pred=f.node('oof:'+i,'oof_prediction',rows=(row,),prediction_evidence=evidence,dependencies=(f.dep('model',producer),f.dep('reads',read)))
            nodes.append(pred);predictions[i]=pred
        cf=compile_temporal_fold(pop,id='consumer',fit_at=16,evaluation_start=20,evaluation_end=40,training_start=0)
        cn=f.node('consumer-fold','fold',execution=temporal_execution(f),fold_evidence=graph.ValidatedTemporalFoldEvidenceV1(pop,cf,((producer.id,pn.id),)));nodes.append(cn)
        cr=tuple(reads('consumer-training:'+i,i,predictions[i],cn,'fit_feature') for i in ('a','b'))
        consumer,state=model('consumer',cn,cr)
        request=graph.ReadRequest('e',20,21,'OOF','Row.v1','probability',f.target,20,30,'d2',cn.id)
        binding=graph.ReadBinding('x',sources['e'].id,'x',request)
        with tempfile.TemporaryDirectory() as d:
            store=graph.SemanticArtifactStore(d,f.namespace);ref=store.commit('route',tuple(n.id for n in nodes),tuple(nodes),f.payloads)
            fresh=graph.SemanticArtifactStore(d,f.namespace);restored=graph.restore_bound_model(fresh,ref,consumer.id)
            self.assertEqual(restored.predict_committed(fresh,ref,consumer.id,graph.ReadSession(fresh,ref,(binding,)))[0],F(3,4))
            actual=fresh.read_commit('route');producer_read=cr[0].read_manifest.bindings[0].request
            self.assertIn(producer.id,graph.validate_oof_producer(producer_read,producer.id,actual))
            # An absent route cannot self-authorize by the producer's own metadata.
            missing=replace(cn,fold_evidence=replace(cn.fold_evidence,declared_routes=()))
            altered_reads=[]
            for original in cr:
                binding=original.read_manifest.bindings[0]
                altered=replace(binding,request=replace(binding.request,fold_node_id=missing.id))
                record=replace(original.read_manifest.reads[0],binding=altered)
                altered_reads.append(replace(original,read_manifest=graph.ReadManifest(f.namespace,(altered,),(record,),()),
                    dependencies=tuple(replace(dep,source_id=missing.id) if dep.source_id==cn.id else dep for dep in original.dependencies)))
            replaced_ids={cn.id:missing.id,**{old.id:new.id for old,new in zip(cr,altered_reads)}}
            badconsumer=replace(consumer,fit_evidence=replace(consumer.fit_evidence,fold_node_id=missing.id,
                actual_training_read_manifests=tuple(n.id for n in altered_reads)),
                dependencies=tuple(replace(dep,source_id=replaced_ids.get(dep.source_id,dep.source_id)) for dep in consumer.dependencies))
            badnodes=tuple(n for n in nodes if n.id not in (*replaced_ids,consumer.id))+(missing,*altered_reads,badconsumer)
            all_ids={n.id for n in badnodes}
            self.assertTrue(all(dep.source_id in all_ids for n in badnodes for dep in n.dependencies))
            with self.assertRaisesRegex(ContractError,'explicit exact earlier producer route'):
                graph.validate_closure(tuple(n.id for n in badnodes),badnodes,f.payloads,f.namespace)
            self.assertEqual(by['a'].target_end,10);self.assertEqual(by['a'].dependency_end,15)

    def test_v01_typed_payload_replay_variants(self):
        l=ledger();o=record_outcome(l);before=l.checkpoint();original=json.loads(o.payload)
        for key,value in (('terminal_ticks',1),('terminal_ticks',False),('maximum_up_ticks',0.0),('first_barrier','upper')):
            payload=json.loads(o.payload);payload['data'][key]=value
            with self.assertRaises(ContractError):l.append_outcome(replace(o,payload=literal.canonical(payload)))
            self.assertEqual(l.checkpoint(),before)
        with self.assertRaises(ContractError):l.append_outcome(replace(o,payload=b'0'))
        with self.assertRaises(ContractError):l.append_outcome(replace(o,observation=ObservationEvidence(-1,11,'obs-v1')))
        for key in ('candidate_version','definition_version','observation_version'):
            payload={**original,key:'0'*64}
            with self.assertRaises(ContractError):l.append_outcome(replace(o,payload=literal.canonical(payload)))
        source_ref=original['evidence'][0]['ref'];evidence=retained_evidence(l)
        changed=json.loads(evidence[source_ref['sha256']]);changed['initial']=101
        with self.assertRaises(IntegrityError):l.append_outcome(o,evidence_by_sha={source_ref['sha256']:literal.canonical(changed)})
        pending=ledger();p=record_outcome(pending,observation=ObservationEvidence(0,0,'initial-prefix'))
        self.assertEqual(p.state,literal.observation_state(0,10,0,0))
        self.assertTrue(all(data(p)[k] is None for k in ('terminal_ticks','maximum_up_ticks','maximum_down_ticks','first_barrier','first_barrier_at')))
        ol,targets=object_ledger();object_out=record_object(ol,targets['a'],(ExactPoint(1,0,F(100),1),))
        for key,value in (('contact_price',[200,2]),('contact_price',[100.0,1]),('maximum_favorable_ticks',[False,1]),('geometry_version','forged')):
            payload=json.loads(object_out.payload);payload['data'][key]=value
            with self.assertRaises(ContractError):ol.append_outcome(replace(object_out,payload=literal.canonical(payload)))
        bad=LabelLedger();bad.add_definition(ol.definitions[0])
        with self.assertRaises(ContractError):bad.add_candidate(replace(ol.candidates[0],object_version='different'))
        with self.assertRaises(ContractError):record_object(ol,targets['a'],(ExactPoint(2,0,F(100),1),),id='a:v2',supersedes='a:v1')
        with self.assertRaises(ContractError):record_object(ol,targets['a'],(ExactPoint(1,0,F(100),1),),
            cov=ObservationEvidence(10,11,'obs-v1',partial_facts=(('observed_contact',1,F(100)),)),id='a:v2',supersedes='a:v1')
        self.assertEqual(before,l.checkpoint())

    def test_capacity_variants(self):
        # Exact synthetic small caps exercise the same guards used by actual APIs.
        for key in GOLDEN['finite_limits']['defaults']:
            with self.subTest(limit=key):
                with self.assertRaises(ContractError):V01V02LimitsV1(**{key:True})
        limits=replace(DEFAULT_LIMITS,max_ledger_candidates=2)
        l=ledger(('a','b'),limits);before=l.checkpoint()
        with self.assertRaises(ContractError):l.add_candidate(candidate('c'))
        self.assertEqual(before,l.checkpoint())
        l=LabelLedger(replace(DEFAULT_LIMITS,max_ledger_definitions=2));l.add_definition(definition('one'));l.add_definition(definition('two'));before=l.checkpoint()
        with self.assertRaises(ContractError):l.add_definition(definition('three'))
        self.assertEqual(before,l.checkpoint())
        l=ledger(limits=replace(DEFAULT_LIMITS,max_ledger_outcomes=2));record_outcome(l);record_outcome(l,'a:v2',supersedes='a:v1');before=l.checkpoint()
        with self.assertRaises(ContractError):record_outcome(l,'a:v3',supersedes='a:v2')
        self.assertEqual(before,l.checkpoint())
        limits=replace(DEFAULT_LIMITS,max_temporal_population=2)
        pop=(sample('a',0,2,3),sample('b',1,3,4));compile_temporal_fold(pop,id='f',fit_at=8,evaluation_start=10,evaluation_end=20,limits=limits)
        with self.assertRaises(ContractError):compile_temporal_fold((*pop,sample('c',2,4,5)),id='f',fit_at=8,evaluation_start=10,evaluation_end=20,limits=limits)
        limits=replace(DEFAULT_LIMITS,max_dependencies_per_sample=2)
        a=sample('a',0,2,3,deps=(dependency('c1',end=3),dependency('c2',end=3)))
        compile_temporal_fold((a,),id='f',fit_at=8,evaluation_start=10,evaluation_end=20,limits=limits)
        with self.assertRaises(ContractError):compile_temporal_fold((replace(a,dependencies=(*a.dependencies,dependency('c3',end=3))),),id='f',fit_at=8,evaluation_start=10,evaluation_end=20,limits=limits)
        limits=replace(DEFAULT_LIMITS,max_dependencies_per_sample=2,max_total_dependencies=2)
        a=replace(a,dependencies=a.dependencies[:1]);b=sample('b',1,3,4,deps=(dependency('c2',end=3),))
        self.assertEqual(sum(len(s.dependencies) for s in (a,b)),2)
        compile_temporal_fold((a,b),id='f',fit_at=8,evaluation_start=10,evaluation_end=20,limits=limits)
        bplus=replace(b,dependencies=(*b.dependencies,dependency('c3',end=3)))
        self.assertTrue(all(len(s.dependencies)<=2 for s in (a,bplus)))
        with self.assertRaisesRegex(ContractError,'total.*dependency'):compile_temporal_fold((a,bplus),id='f',fit_at=8,evaluation_start=10,evaluation_end=20,limits=limits)
        limits=replace(DEFAULT_LIMITS,max_parent_groups_per_sample=2)
        a=sample(parents=('p1','p2'));compile_temporal_fold((a,),id='f',fit_at=12,evaluation_start=20,evaluation_end=30,limits=limits)
        with self.assertRaises(ContractError):compile_temporal_fold((replace(a,parent_groups=('p1','p2','p3')),),id='f',fit_at=12,evaluation_start=20,evaluation_end=30,limits=limits)
        from trading_research.research.temporal_folds import identity
        limits=replace(DEFAULT_LIMITS,max_id_utf8_bytes=8);self.assertEqual(identity('12345678',limits),'12345678')
        with self.assertRaises(ContractError):identity('123456789',limits)
        # The expected payload length comes from primitive input/source fields;
        # every content hash has a fixed 64-character representation.
        t=target();source={'schema':'PriceLabelSourceV1','target':{field.name:getattr(t,field.name) for field in fields(t)},
            'initial':100,'points':[],'coverage':{'start':0,'end':10,'certified_through':11,'gaps':[],
                'source_order_known':True,'version':'obs-v1'},'up_ticks':3,'down_ticks':2}
        source['target']['unit']=t.unit.value;source['target']['capabilities']=sorted(c.value for c in t.capabilities)
        source_raw=literal.canonical(source)
        payload_template={'schema':'LabelPayloadV1','kind':'price_path','candidate_version':'0'*64,
            'definition_version':'0'*64,'observation_version':'0'*64,
            'evidence':[{'slot':'source','ref':{'sha256':'0'*64,'size_bytes':len(source_raw),'kind':'label_source_v1'}}],
            'data':{'target_signature':'0'*64,'terminal_ticks':0,'maximum_up_ticks':0,'maximum_down_ticks':0,
                'first_barrier':'neither','first_barrier_at':None,'observed_count':0}}
        capacity=max(len(source_raw),len(literal.canonical(payload_template)))
        limited=ledger(limits=replace(DEFAULT_LIMITS,max_payload_bytes=capacity));o=record_outcome(limited)
        self.assertEqual(max(len(o.payload),*(len(v) for v in retained_evidence(limited).values())),capacity)
        smaller=ledger(limits=replace(DEFAULT_LIMITS,max_payload_bytes=capacity-1));before=smaller.checkpoint()
        with self.assertRaises(ContractError):record_outcome(smaller)
        self.assertEqual(smaller.checkpoint(),before)
        # Independent exact empty checkpoint fixture retains the very same bound.
        configured={f.name:getattr(DEFAULT_LIMITS,f.name) for f in fields(DEFAULT_LIMITS)}
        expected={'format':'LabelLedgerV1','limits':{'type':'V01V02LimitsV1','fields':configured},
            'definitions':{'tuple':[]},'candidates':{'tuple':[]},'outcomes':{'tuple':[]},'evidence':{}}
        bound=1
        for _ in range(12):
            configured['max_checkpoint_bytes']=bound;raw=literal.canonical(expected)
            if len(raw)==bound:break
            bound=len(raw)
        self.assertEqual(len(raw),bound)
        exact_limits=V01V02LimitsV1(**configured);empty=LabelLedger(exact_limits)
        self.assertEqual(empty.checkpoint(),raw);self.assertEqual(LabelLedger.restore(raw,limits=exact_limits).checkpoint(),raw)
        with self.assertRaises(ContractError):LabelLedger(replace(exact_limits,max_checkpoint_bytes=bound-1))
        self.assertEqual(empty.checkpoint(),raw)
        limits=replace(DEFAULT_LIMITS,max_nested_depth=2);bounded_json(b'[[0]]',256,limits)
        with self.assertRaises(ContractError):bounded_json(b'[[[0]]]',256,limits)
        p,c=self.stages();edge=OOFEdge('base','cal',('a','b','c'))
        compile_oof_schedule((p,c),(edge,),limits=replace(DEFAULT_LIMITS,max_stages=2))
        with self.assertRaises(ContractError):compile_oof_schedule((p,c,replace(p,id='base2')),(edge,),limits=replace(DEFAULT_LIMITS,max_stages=2))
        p2=replace(p,id='base2');p3=replace(p,id='base3');edges=(edge,OOFEdge('base2','cal',('a','b','c')))
        compile_oof_schedule((p,p2,p3,c),edges,limits=replace(DEFAULT_LIMITS,max_oof_edges=2))
        with self.assertRaises(ContractError):compile_oof_schedule((p,p2,p3,c),(*edges,OOFEdge('base3','cal',('a','b','c'))),limits=replace(DEFAULT_LIMITS,max_oof_edges=2))
        expanded=replace(DEFAULT_LIMITS,max_id_utf8_bytes=257,max_dependencies_per_sample=65)
        long_row=replace(sample('x'*257,0,2,3,deps=tuple(dependency('d'+str(i),end=2) for i in range(65)),group='d0'),
                         endpoint_group='d0')
        expanded_fold=compile_temporal_fold((long_row,),id='f',fit_at=8,evaluation_start=10,evaluation_end=20,limits=expanded)
        self.assertEqual(expanded_fold.training_ids,('x'*257,))
        with self.assertRaises(ContractError):compile_temporal_fold((long_row,),id='f',fit_at=8,evaluation_start=10,evaluation_end=20)
        f=Fixture();f.namespace='local-temporal-limits'
        for dep in long_row.dependencies:f.payloads[dep.evidence_ref.sha256]=dep.evidence_bytes
        fn=f.node('expanded','fold',execution=temporal_execution(f,expanded),fold_evidence=graph.ValidatedTemporalFoldEvidenceV1((long_row,),expanded_fold))
        with tempfile.TemporaryDirectory() as d:
            store=graph.SemanticArtifactStore(d,f.namespace);ref=store.commit('expanded',(fn.id,),(fn,),f.payloads)
            self.assertEqual(store.read_commit(ref.key).closure.nodes[0].fold_evidence.population,(long_row,))
        with self.assertRaises(ContractError):replace(fn,execution=temporal_execution(f))


if __name__=='__main__':unittest.main()
