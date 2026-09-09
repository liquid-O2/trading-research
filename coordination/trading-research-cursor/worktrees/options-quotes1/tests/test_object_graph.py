"""Preregistered F10-01..34 assertions; no generator or market certification.

ENGINEERING_METRICS is populated only by the registered finite comparison test
when the root-supervised worker executes this module.
"""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import resource
import shutil
import sqlite3
import tempfile
import time
import unittest

from references.objects_literal import LiteralObjectGraph
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.object_graph import (
    ActionProposal, Alias, AnchorVersion, AtomicBatch, BirthKey, Eligibility,
    Endpoint, EndpointKind, EvidencePurpose, EvidenceState, EvidenceVersion,
    Existence, Geometry, Instrument, ObjectGraph, ObjectRevision, ObservationEvent,
    ObservationKind, Presentation, PublicationClock, RegistryDefinition,
    RelationKind, RelationVersion, Support, canonical, content_hash, score_view, weighted_midpoint,
)

ENGINEERING_METRICS = {}
GOLDEN_PATH = Path(__file__).parent / 'golden/f10-object-lineage.json'


def instrument(symbol='NQH5'):
    return Instrument('providerQ', 'CME', symbol, symbol, 'termsV1', Fraction(1, 4))


def evidence(name, at=5, *, revision=0, support=Support.OBSERVED, inst=None,
             purpose=EvidencePurpose.MEASUREMENT, mapped=None):
    return EvidenceVersion('s:'+name, f'e:{name}:{revision}', revision,
                           None if revision == 0 else f'e:{name}:{revision-1}', at, at,
                           support, inst or instrument(), 'bytes:'+name+':'+str(revision), purpose, mapped)


def geometry(price=100, *, source='NQH5', execution='NQH5', definition='geometry-v1'):
    return Geometry(Fraction(price-1), Fraction(price+1), Fraction(price-1), Fraction(price+1),
                    definition, source, execution)


def obj(name='A', at=10, *, ev=None, parents=(), anchors=(), price=100, inst=None,
        existence=Existence.ACTIVE, eligibility=Eligibility.ELIGIBLE, confirmed=5,
        geom=None, mapping=None, origins=None):
    ev = evidence(name) if ev is None else ev
    inst = inst or instrument()
    birth = BirthKey('fixture','v1',inst,anchors,(ev.source_id,) if origins is None else origins,name)
    return ObjectRevision('o:'+name, 'v:'+name+'0', 0, None, birth,
                          geom or geometry(price, source=inst.raw_symbol, execution=inst.raw_symbol),
                          (ev.version_id,), parents, existence, eligibility,
                          EvidenceState.OBSERVED if ev.support == Support.OBSERVED else EvidenceState.MISSING,
                          confirmed, at, ('support', 'resistance'), mapping)


def revised(prior, at, **changes):
    revision = prior.revision+1
    return replace(prior, revision=revision, version_id='v:'+prior.object_id[2:]+str(revision),
                   supersedes=prior.version_id, known_at=at, **changes)


def relation(name, left, right, at, *, kind=RelationKind.DISPLAY_GROUP, revision=0, tombstone=False):
    return RelationVersion('rel:'+name, 'rv:'+name+str(revision), revision,
                           None if revision == 0 else 'rv:'+name+str(revision-1), kind,
                           Endpoint(EndpointKind.OBJECT_VERSION, left),
                           Endpoint(EndpointKind.OBJECT_VERSION, right), at, at, tombstone)


def plain(value):
    return json.loads(canonical(value))


def short_ids(values):
    return [v.split(':', 1)[1] for v in values]


def journal(graph):
    all_rows, cursor = [], 0
    while True:
        page = graph.journal_page(after=cursor)
        if not page:
            return tuple(all_rows)
        all_rows.extend(page); cursor = page[-1]['sequence']


class ObjectGraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)/'objects.sqlite'
        self.definition = RegistryDefinition()
        self.graph = ObjectGraph(self.path, definition=self.definition)
        self.goldens = {c['case_id']: c for c in json.loads(GOLDEN_PATH.read_text())['cases']}

    def expected(self, case):
        return self.goldens[f'F10-{case:02d}']['expected']

    def commit(self, *members, at=None, batch_id=None, clock=None):
        at = max(m.known_at for m in members) if at is None else at
        clock = clock or PublicationClock(at, at, at, actual_completion_at=at)
        seq = self.graph.sequence+1
        batch = AtomicBatch(batch_id or 'batch:'+str(seq), seq, self.definition.version,
                            clock, tuple(members), len(members))
        self.graph.commit_batch(batch, expected_head=self.graph.head)
        return batch

    def birth(self, name='A', at=10, **kwargs):
        ev = kwargs.pop('ev', evidence(name))
        value = obj(name, at, ev=ev, **kwargs)
        self.commit(ev, value, at=at)
        return value

    def observe(self, parent, name, at, *, visit='V1', kind=ObservationKind.CONTACT,
                predecessor=None, event_at=None, order=True):
        ev = evidence(name, at, inst=parent.birth.instrument)
        value = ObservationEvent('obs:'+name, parent.version_id, 'visit:'+visit, kind,
                                 at if event_at is None else event_at, at, (ev.version_id,),
                                 name, predecessor, order)
        batch = self.commit(ev, value, at=at)
        return value, batch

    def active(self, at):
        return short_ids(o.version_id for o in self.graph.active_set(at))

    def assert_parity(self, at, *, cursor=None):
        reference = LiteralObjectGraph(journal(self.graph),ttl_ns=self.definition.ttl_ns,visit_reset_policy=self.definition.visit_reset_policy)
        view = reference.view(at, cursor=cursor)
        self.assertEqual([o.version_id for o in self.graph.active_set(at, cursor=cursor)], view['active_versions'])
        for value, state in zip(view['objects'], view['states']):
            indexed = self.graph.object_asof(value['object_id'], at, cursor=cursor)
            self.assertEqual(plain(indexed.object), value)
            self.assertEqual((indexed.dirty, indexed.reason, indexed.born_at),
                             (state['dirty'], state['reason'], state['born_at']))
        self.assertEqual(plain(self.graph.events_asof(at, cursor=cursor)), view['events'])
        self.assertEqual(plain(self.graph.visits_asof(at, cursor=cursor)), view['visits'])
        self.assertEqual(plain(self.graph.relations_asof(at, cursor=cursor)), view['relations'])
        for id, expected in view['candidate_cuts'].items():
            self.assertEqual(plain(self.graph.candidate_cut(id)),expected)
        for id, expected in view['targets'].items():
            self.assertEqual(plain(self.graph.target(id)),expected)
        for vid,member in view['versions'].items():
            actual = self.graph.get_version(vid)
            self.assertEqual({'type':type(actual).__name__,'value':plain(actual)},member)
        with self.graph._connection() as con:
            for id,expected in view['actions'].items():
                self.assertEqual(plain(self.graph._control_old(con,id,'actions')),expected)
        return view

    def test_f10_01_coincident_independent_anchors(self):
        e = self.expected(1)
        ep, ew = evidence('POC'), evidence('VWAP')
        ap = AnchorVersion('a:P', 'av:P0', 0, None, (ep.version_id,), 0, 5, 5, 5)
        aw = AnchorVersion('a:W', 'av:W0', 0, None, (ew.version_id,), 0, 5, 5, 5)
        p, w = obj('POC', ev=ep, anchors=(ap.version_id,)), obj('VWAP', ev=ew, anchors=(aw.version_id,))
        r = relation('overlap', p.version_id, w.version_id, 10)
        self.commit(ep, ap, p, ew, aw, w, r)
        self.assertEqual(self.active(10), e['cut10_active'])
        self.assertEqual(len({o.birth.version for o in self.graph.active_set(10)}), e['canonical_birth_count'])
        self.assertEqual(len(self.graph.relations_asof(10)), e['display_group_count'])
        self.assertEqual(r.independent_confirmation, e['independent_confirmation'])
        self.assert_parity(10)

    def test_f10_02_visit_preserves_eligibility(self):
        e = self.expected(2); a = self.birth()
        first, _ = self.observe(a, 'contact', 20)
        second, _ = self.observe(a, 'sweep', 21, kind=ObservationKind.SWEEP, predecessor=first.event_id)
        self.observe(a, 'reclaim', 22, kind=ObservationKind.RECLAIM, predecessor=second.event_id)
        self.assertEqual(self.active(15), e['cut15_active']); self.assertEqual(self.active(22), e['cut22_active'])
        self.assertEqual(self.graph.visits_asof(15),())
        self.assertEqual('unvisited' if not self.graph.visits_asof(15) else 'visited',e['cut15_visit_state'])
        visits = self.graph.visits_asof(22)
        self.assertEqual(short_ids(v['visit_id'] for v in visits), e['visit_ids'])
        self.assertEqual(visits[0]['state'], e['cut22_visit_state'])
        self.assertEqual(len(self.graph.events_asof(22)), e['visit_event_count'])
        self.assert_parity(15); self.assert_parity(22)

    def test_f10_03_retest_restart_duplicate(self):
        e = self.expected(3); a = self.birth()
        first, _ = self.observe(a, 'enter1', 20, kind=ObservationKind.ENTER)
        snapshot = self.graph.checkpoint()
        self.observe(a, 'exit1', 25, kind=ObservationKind.EXIT, predecessor=first.event_id)
        _, last_batch = self.observe(a, 'enter2', 30, visit='V2', kind=ObservationKind.ENTER)
        before = self.graph.sequence
        uninterrupted = plain(self.graph.visits_asof(30))
        self.graph = ObjectGraph.restore(self.path, definition=self.definition, checkpoint=snapshot)
        self.assertEqual(self.graph.commit_batch(last_batch, expected_head=self.graph.head)[1], False)
        self.assertEqual(self.graph.sequence, before)
        visits = self.graph.visits_asof(30)
        self.assertEqual(plain(visits)==uninterrupted,e['restored_matches_uninterrupted'])
        self.assertEqual([v['ordinal'] for v in visits], e['visit_ordinals'])
        self.assertEqual(short_ids(v['visit_id'] for v in visits if v['state'] not in {'closed','reset'}), [e['open_visit']])
        self.assertEqual(len(self.graph.events_asof(30)), e['unique_visit_event_count'])
        self.assert_parity(30)

    def test_f10_04_atomic_split_merge_intermediate_history(self):
        e = self.expected(4); ea, ed = evidence('A'), evidence('D')
        a, d = obj('A', ev=ea), obj('D', ev=ed)
        self.commit(ea, a, ed, d)
        a1 = revised(a, 20, existence=Existence.SUPERSEDED, eligibility=Eligibility.INELIGIBLE)
        b, c = obj('B', 20, ev=ea, parents=(a.version_id,)), obj('C', 20, ev=ea, parents=(a.version_id,))
        c1 = revised(c, 20, existence=Existence.SUPERSEDED, eligibility=Eligibility.INELIGIBLE)
        d1 = revised(d, 20, existence=Existence.SUPERSEDED, eligibility=Eligibility.INELIGIBLE)
        merged = obj('E',20,ev=ea,parents=(c.version_id,d.version_id),origins=('s:A','s:D'))
        before = self.graph.head
        before_count = self.graph.sequence
        before_projection = self.graph.checkpoint()
        bad = replace(merged, parent_versions=('v:missing',))
        with self.assertRaises(ContractError):
            self.commit(a1, b, c, c1, d1, bad)
        self.assertEqual(self.graph.head,before)
        self.assertEqual(self.graph.sequence-before_count,e['failed_batch_appended_records'])
        self.assertEqual(self.graph.checkpoint()!=before_projection,e['partial_prefix_visible'])
        for absent in ('v:A1','v:B0','v:C0','v:C1','v:D1','v:E0'):
            with self.assertRaises(DependencyUnavailable):self.graph.get_version(absent)
        self.assertEqual(self.active(19), e['cut19_active'])
        self.commit(a1, b, c, c1, d1, merged)
        self.assertEqual(self.active(20), e['cut20_active'])
        self.assertEqual(sorted(self.graph.get_version('v:'+id).version_id[2:] for id in e['retrievable_versions']), e['retrievable_versions'])
        snapshot = self.graph.checkpoint()
        self.graph = ObjectGraph.restore(self.path, definition=self.definition, checkpoint=snapshot)
        self.assertEqual(self.active(20), e['cut20_active']); self.assert_parity(19); self.assert_parity(20)

    def test_f10_05_provisional_migration_confirmation(self):
        e = self.expected(5)
        a = self.birth(existence=Existence.PROVISIONAL, eligibility=Eligibility.UNKNOWN, confirmed=None)
        a1 = revised(a, 12, geometry=geometry(102))
        self.commit(a1)
        a2 = revised(a1, 15, existence=Existence.ACTIVE, eligibility=Eligibility.ELIGIBLE, confirmed_at=15)
        self.commit(a2)
        self.assertEqual(self.active(14), e['cut14_active'])
        self.assertEqual(self.graph.object_asof('o:A',14).object.version_id[2:], e['cut14_latest'])
        self.assertEqual(self.active(15), e['cut15_active'])
        self.assertEqual(len({r.birth.version for r in self.graph.revisions('o:A')}), e['birth_count'])
        self.assert_parity(14); self.assert_parity(15)

    def test_f10_06_corrected_geometry_keeps_old_cut(self):
        e = self.expected(6); a = self.birth()
        cut = self.graph.freeze_candidates(cut_id='cut:12', at=12, instrument=instrument(), expected_head=self.graph.head)
        ev1 = replace(evidence('A', 20, revision=1), event_at=8)
        a1 = revised(a, 20, evidence_versions=(ev1.version_id,), geometry=Geometry(Fraction(102),Fraction(104),Fraction(102),Fraction(104),'corrected','NQH5','NQH5'))
        self.commit(ev1, a1)
        old = self.graph.object_asof('o:A',12).object; new = self.graph.object_asof('o:A',20).object
        self.assertEqual(old.version_id[2:], e['cut12_version']); self.assertEqual(new.version_id[2:], e['cut20_version'])
        self.assertEqual([old.geometry.lower,old.geometry.upper], e['cut12_band'])
        self.assertEqual(self.graph.candidate_cut('cut:12'),cut);self.assertEqual(new.known_at,e['new_known_at'])
        self.assertEqual(old.geometry==self.graph.object_asof('o:A',12).object.geometry,e['cut12_geometry_unchanged_after_correction'])
        self.assert_parity(12); self.assert_parity(20)

    def test_f10_07_invalidation_and_declared_reactivation(self):
        e=self.expected(7); a=self.birth()
        a1=revised(a,20,existence=Existence.INVALIDATED,eligibility=Eligibility.INELIGIBLE);self.commit(a1)
        a2=revised(a1,30,existence=Existence.ACTIVE,eligibility=Eligibility.ELIGIBLE);self.commit(a2)
        for at,key in [(15,'cut15'),(25,'cut25'),(35,'cut35')]:self.assertEqual(self.active(at),e[key]);self.assert_parity(at)
        self.assertEqual(short_ids(r.version_id for r in self.graph.revisions('o:A')),e['all_revisions'])
        custom=RegistryDefinition(transitions=tuple(p for p in self.definition.transitions if p!=(Existence.INVALIDATED,Existence.ACTIVE)))
        path=Path(self.temp.name)/'restricted.sqlite';g=ObjectGraph(path,definition=custom)
        for seq,members in [(1,(evidence('A'),a)),(2,(a1,))]:g.commit_batch(AtomicBatch('batch:r'+str(seq),seq,custom.version,PublicationClock(members[-1].known_at,members[-1].known_at,members[-1].known_at,actual_completion_at=members[-1].known_at),members,len(members)),expected_head=g.head)
        with self.assertRaises(ContractError):g.commit_batch(AtomicBatch('batch:r3',3,custom.version,PublicationClock(30,30,30,actual_completion_at=30),(a2,),1),expected_head=g.head)

    def test_f10_08_expired_version_remains_labelable(self):
        e=self.expected(8);a=self.birth()
        self.graph.freeze_candidates(cut_id='cut:15',at=15,instrument=instrument(),expected_head=self.graph.head)
        a1=revised(a,25,existence=Existence.EXPIRED,eligibility=Eligibility.INELIGIBLE);self.commit(a1)
        target=self.graph.bind_target(target_id='target:old',cut_id='cut:15',object_version=a.version_id,geometry=a.geometry,horizon_end=40,observation_process='exact_toy_points',expected_head=self.graph.head)
        self.assertEqual(self.active(26),e['cut26_active']);self.assertEqual(target['object_version'][2:],e['label_version']);self.assertEqual(target['horizon_end'],e['label_end'])
        self.assertEqual([self.graph.get_version(target['object_version']).geometry.lower,self.graph.get_version(target['object_version']).geometry.upper],e['label_geometry'])
        self.assertEqual(self.graph.candidate_cut('cut:15')['candidate_count'],e['candidate_denominator_retained']);self.assert_parity(40)

    def test_f10_09_rename_alias_and_action_deduplication(self):
        e=self.expected(9);a=self.birth();self.observe(a,'visit1',12)
        before=self.graph.head
        with self.assertRaises(IntegrityError):self.commit(replace(a,object_id='o:B',version_id='v:B0',known_at=13))
        self.assertEqual(self.graph.head,before)
        self.commit(Alias('alias:B','o:A',14,'B'))
        cut=self.graph.freeze_candidates(cut_id='cut:15',at=15,instrument=instrument(),expected_head=self.graph.head)
        first=ActionProposal('action:A',a.version_id,'idea:A','visit:V1',1,'plan1',40,instrument())
        second=replace(first,id='action:B')
        grouped=self.graph.project_action_aliases(projection_id='actions:alias',cut_id='cut:15',policy_version='alias-v1',proposals=(first,second),expected_head=self.graph.head)
        self.assertEqual(cut['candidate_count'],e['canonical_birth_count']);self.assertEqual(grouped['unique_action_count'],e['unique_action_count'])
        self.assertEqual(short_ids(grouped['groups'][0]['members']),e['alias_members'])
        self.assertEqual(self.graph.get_version('alias:B').object_id,'o:A')
        self.assertEqual(self.graph.get_version(a.version_id)!=a,e['loss_history_removed'])
        self.assert_parity(15)

    def test_f10_10_raw_mapping_has_exact_known_time(self):
        e=self.expected(10);xinst,yinst=instrument('X'),instrument('Y');ex=evidence('X',inst=xinst)
        x=self.birth('X',ev=ex,inst=xinst)
        mapping=evidence('M',20,inst=xinst,purpose=EvidencePurpose.MAPPING,mapped=yinst)
        y=obj('Y',20,ev=mapping,inst=yinst,parents=(x.version_id,),geom=geometry(103,source='X',execution='Y'),mapping=mapping.version_id,origins=('s:M','s:X'))
        self.commit(mapping,y)
        self.assertEqual(short_ids(v.version_id for v in self.graph.active_set(19,instrument=yinst)),e['cut19_mapped_active'])
        self.assertEqual(short_ids(v.version_id for v in self.graph.active_set(20,instrument=yinst)),e['cut20_mapped_active'])
        self.assertEqual((x.geometry.lower+x.geometry.upper)/2,e['original_X0_ticks']);self.assertEqual(y.mapping_version,'e:'+e['mapping_version']+':0')
        self.assertEqual(self.graph.engineering_scope()['native_mapping_certified'],e['native_equivalence_certified']);self.assert_parity(20)

    def test_f10_11_relation_tombstone_uses_knowledge_cut(self):
        e=self.expected(11);a=self.birth();b=self.birth('B')
        r=replace(relation('R',a.version_id,b.version_id,30,kind=RelationKind.EQUIVALENT),event_at=12)
        self.commit(r);self.commit(replace(r,version_id='rv:R1',revision=1,predecessor='rv:R0',known_at=40,tombstone=True))
        for at,key in [(20,'cut20_equivalent'),(35,'cut35_equivalent'),(45,'cut45_equivalent')]:
            self.assertEqual(bool(self.graph.relations_asof(at)),e[key]);self.assert_parity(at)
        self.assertEqual([self.graph.get_version('rv:'+v).version_id[3:] for v in e['retrievable_relations']],e['retrievable_relations'])

    def test_f10_12_orphan_future_source_rejection(self):
        e=self.expected(12);before=self.graph.head
        with self.assertRaises(ContractError):self.commit(obj(parents=('v:missing',)))
        self.assertEqual(self.graph.head,before)
        future=evidence('A',11);a=obj(ev=future)
        with self.assertRaises(ContractError):self.commit(future,a,at=10)
        self.assertEqual(self.graph.head,before)
        self.commit(future,replace(a,known_at=12),at=12)
        self.assertEqual(self.graph.sequence,e['commits']);self.assert_parity(12)

    def test_f10_13_typed_independent_states(self):
        a=self.birth();e=self.expected(13)
        with self.assertRaises(ContractError):replace(a,evidence_state='calibrated_by_UI')
        with self.assertRaises(ContractError):ObservationEvent('obs:bad',a.version_id,'visit:V1','whatever',20,20,('e:A:0',),'bad')
        self.observe(a,'contact',20)
        current=self.graph.object_asof('o:A',20).object
        self.assertEqual(current.existence==Existence.ACTIVE,e['contact_active']);self.assertEqual(current.eligibility.value,e['contact_eligibility']);self.assertEqual(current.evidence_state.value,e['contact_evidence'])
        self.assert_parity(20)

    def test_f10_14_candidate_annotation_and_archived_lookup(self):
        e=self.expected(14);a=self.birth();b=self.birth('B')
        cut=self.graph.freeze_candidates(cut_id='cut:15',at=15,instrument=instrument(),expected_head=self.graph.head)
        annotation=self.graph.annotate_selection(annotation_id='selection:15',cut_id='cut:15',selected=(a.version_id,),rejected=(b.version_id,),expected_head=self.graph.head)
        self.commit(revised(a,20,existence=Existence.SUPERSEDED,eligibility=Eligibility.INELIGIBLE))
        self.commit(revised(b,25,existence=Existence.EXPIRED,eligibility=Eligibility.INELIGIBLE))
        snapshot=self.graph.checkpoint();self.graph=ObjectGraph.restore(self.path,definition=self.definition,checkpoint=snapshot)
        self.assertEqual(short_ids(self.graph.candidate_cut('cut:15')['candidate_versions']),e['restored_cut15']);self.assertEqual(cut['candidate_count'],e['candidate_count'])
        self.assertEqual(short_ids(self.graph.get_version('v:'+id).version_id for id in e['lookup_old_versions']),e['lookup_old_versions'])
        self.assertEqual(self.graph.annotate_selection(annotation_id='selection:15',cut_id='cut:15',selected=(a.version_id,),rejected=(b.version_id,),expected_head=self.graph.head),annotation)
        self.assert_parity(25)

    def test_f10_15_all_cuts_suffix_and_indexed_reference(self):
        e=self.expected(15);a=self.birth();b=self.birth('B',15)
        self.commit(revised(a,20));self.commit(revised(b,25,existence=Existence.EXPIRED,eligibility=Eligibility.INELIGIBLE))
        cuts=[9,10,15,19,20,25];baseline=[self.active(t) for t in cuts]
        self.assertEqual(baseline,e['active_at_cuts']);prefix=journal(self.graph)
        for start in range(0,1000,32):
            members=[]
            for n in range(start,min(start+32,1000)):
                ev=evidence(f'U{n}',30);members.extend((ev,obj(f'U{n}',30,ev=ev)))
            self.commit(*members)
        for at,expected in zip(cuts,baseline):
            self.assertEqual(self.active(at),expected);self.assert_parity(at)
            self.assertEqual(short_ids(LiteralObjectGraph(prefix).view(at)['active_versions']),expected)
        snap=self.graph.checkpoint();self.graph=ObjectGraph.restore(self.path,definition=self.definition,checkpoint=snap)
        self.assertEqual([self.active(t) for t in cuts],baseline)

    def test_f10_16_config_is_frozen_and_restore_bound(self):
        a=self.birth();self.observe(a,'contact',20)
        with self.assertRaises((AttributeError,FrozenInstanceError)):self.graph.definition=RegistryDefinition(id='def:changed')
        with self.assertRaises(FrozenInstanceError):self.definition.ttl_ns=30
        snapshot=self.graph.checkpoint()
        with self.assertRaises(IntegrityError):ObjectGraph.restore(self.path,definition=RegistryDefinition(id='def:changed'),checkpoint=snapshot)
        self.assertEqual(self.active(20),['A0']);self.assert_parity(20)

    def test_f10_17_rank_is_not_calibrated_probability_or_fact(self):
        e=self.expected(17);a=self.birth();head=self.graph.head
        view=score_view(rank=82,rank_scale=100,claimed_probability=Fraction(71,100))
        self.assertIs(view.admitted_probability,e['probability_from_rank']);self.assertEqual(view.calibrated,e['unsupported_probability_eligible'])
        with self.assertRaises(ContractError):self.commit(view,at=20)
        self.assertEqual(self.graph.head,head);self.assertEqual(self.graph.get_version(a.version_id),a)
        self.assertEqual(self.graph.object_asof(a.object_id,20).object!=a,e['factual_lifecycle_changed'])

    def test_f10_18_new_midpoint_preserves_parent_births(self):
        e=self.expected(18);a=self.birth(price=100);b=self.birth('B',price=104)
        midpoint=weighted_midpoint((Fraction(100),Fraction(104)),(Fraction(1),Fraction(1)))
        ev=evidence('C',20);c=obj('C',20,ev=ev,parents=(a.version_id,b.version_id),price=midpoint,origins=('s:A','s:B','s:C'))
        self.commit(ev,c)
        self.assertEqual(midpoint,e['new_geometry_ticks']);self.assertEqual(len(c.parent_versions),e['new_parent_count'])
        self.assertEqual(len([o for o in self.graph.active_set(20) if o.object_id in {'o:A','o:B'}]),e['original_births_retained'])
        with self.assertRaises(ContractError):weighted_midpoint((Fraction(100),Fraction(104)),(Fraction(-1),Fraction(1)))
        self.assert_parity(20)

    def test_f10_19_invalid_latest_blocks_default_and_checks_fallback(self):
        e=self.expected(19);a=self.birth()
        self.commit(revised(a,20,existence=Existence.INVALIDATED,eligibility=Eligibility.INELIGIBLE))
        result=self.graph.fallback('o:A',21)
        self.assertIsNone(result['object_version']);self.assertEqual(result['fallback'],e['silent_A0_fallback'])
        self.assertEqual(bool(self.graph.active_set(21)),e['cut21_current_action_eligible'])
        allowed=self.graph.fallback('o:A',21,policy='previous_valid')
        self.assertEqual(allowed['object_version'],a.version_id);self.assertTrue(allowed['fallback'])
        self.commit(evidence('A',22,revision=1,support=Support.MISSING))
        self.assertIsNone(self.graph.fallback('o:A',23,policy='previous_valid')['object_version'])
        self.assertEqual(self.graph.fallback('o:A',21,policy='previous_valid'),allowed)
        self.assertEqual(self.graph.fallback('o:A',23,policy='previous_valid')['object_version'] is None,e['explicit_fallback_requires_valid_old_support']);self.assert_parity(23)

    def test_f10_20_ttl_archive_ignores_outcome_and_keeps_history(self):
        e=self.expected(20);self.definition=RegistryDefinition(ttl_ns=30)
        self.path=Path(self.temp.name)/'ttl.sqlite';self.graph=ObjectGraph(self.path,definition=self.definition)
        a=self.birth();b=self.birth('B')
        self.commit(revised(a,20,existence=Existence.INVALIDATED,eligibility=Eligibility.INELIGIBLE))
        self.observe(b,'winner',25)
        archive=self.graph.archive_expired(40,expected_head=self.graph.head)
        self.assertEqual(self.active(40),e['hot_active']);self.assertEqual(sorted(short_ids(archive['archived_ids'])),e['archived_ids'])
        self.assertEqual(archive['history_deleted'],e['history_deleted']);self.assertEqual(self.graph.hot_ids,frozenset())
        self.assertEqual(self.graph.object_asof('o:A',40).born_at!=self.graph.object_asof('o:B',40).born_at,e['outcome_dependent_expiry'])
        self.assertEqual(self.graph.get_version(a.version_id),a);self.assertEqual(self.graph.get_version(b.version_id),b);self.assert_parity(40)

    def test_f10_21_preset_and_color_do_not_rewrite_old_geometry(self):
        e=self.expected(21)
        p1=replace(geometry(definition='P_v1'),preset_ratios=(Fraction(0),Fraction(1,2),Fraction(1)))
        p2=replace(geometry(definition='P_v2'),preset_ratios=(Fraction(0),Fraction(309,500),Fraction(1)))
        a=self.birth(geom=p1);b=self.birth('B',20,geom=p2)
        self.assertNotEqual(p1.require_preset(),p2.require_preset())
        with self.assertRaises(DependencyUnavailable):geometry(definition='P_v1').require_preset()
        self.commit(Presentation('view:A-color','o:A',30,'P_v1','universe1',color='blue'))
        self.assertEqual(self.graph.get_version(a.version_id).geometry.definition_id,e['A_geometry_preset'])
        self.assertEqual(self.graph.get_version(b.version_id).geometry.definition_id,e['B_geometry_preset'])
        self.assertEqual(self.graph.object_asof('o:A',30).object.version_id,a.version_id)
        self.assertNotEqual(a.geometry.version,b.geometry.version)
        self.assertEqual(self.graph.object_asof('o:A',30).object.geometry!=p1,e['color_mutates_geometry'])
        self.assertEqual(bool(geometry(definition='P_v1').preset_ratios),e['preset_name_alone_sufficient']);self.assert_parity(30)

    def test_f10_22_universe_selection_is_not_object_death(self):
        e=self.expected(22);a=self.birth()
        one=Presentation('view:current','o:A',10,'preset1','Current')
        three=Presentation('view:first3','o:A',20,'preset1','first3expiries')
        self.commit(one);self.commit(three)
        self.assertEqual(one.universe_version!=three.universe_version,e['universe_definition_changed'])
        self.assertEqual(self.graph.object_asof('o:A',20).object.existence,Existence.ACTIVE)
        self.assertEqual(self.graph.get_version(a.version_id)==a,e['A_history_retained'])
        self.assertEqual(self.graph.object_asof('o:A',20).object.existence in {Existence.INVALIDATED,Existence.EXPIRED},e['A_factual_death']);self.assert_parity(20)

    def test_f10_23_visual_clamps_are_not_physical_geometry(self):
        e=self.expected(23);a=self.birth()
        self.commit(Presentation('view:small','o:A',10,'p','u',clamp=Fraction(4),opacity=Fraction(35)))
        self.commit(Presentation('view:large','o:A',20,'p','u',clamp=Fraction(8),opacity=Fraction(60)))
        current=self.graph.object_asof('o:A',20).object
        self.assertEqual([current.geometry.lower,current.geometry.upper],e['support']);self.assertEqual(current.version_id!=a.version_id,e['geometry_version_changed'])
        self.assertNotEqual(self.graph.get_version('view:small'),self.graph.get_version('view:large'))
        self.assertEqual(self.graph.get_version('view:small')!=self.graph.get_version('view:large'),e['presentation_version_changed'])
        self.assertEqual(self.graph.engineering_scope()['calibrated_confidence'],e['confidence_inferred']);self.assert_parity(20)

    def test_f10_24_source_drop_and_restoration_preserve_birth(self):
        e=self.expected(24);a=self.birth();before=self.active(10)
        self.commit(evidence('A',20,revision=1,support=Support.MISSING));missing=self.active(20)
        ev2=evidence('A',30,revision=2);a1=revised(a,30,evidence_versions=(ev2.version_id,))
        self.commit(ev2,a1);restored=self.active(30)
        self.assertEqual([bool(before),bool(missing),bool(restored)],e['action_eligible_at'])
        self.assertEqual(sum(r.existence in {Existence.EXPIRED,Existence.INVALIDATED} for r in self.graph.revisions('o:A')),e['factual_death_events'])
        self.assertEqual(len({r.birth.version for r in self.graph.revisions('o:A')}),e['canonical_birth_count'])
        self.assertEqual(self.graph.engineering_scope()['mapping_formula_certified'],e['mapping_formula_certified'])
        self.assert_parity(10);self.assert_parity(20);self.assert_parity(30)

    def test_f10_25_replay_cut_excludes_later_correction(self):
        e=self.expected(25);a=self.birth()
        self.commit(revised(a,30,geometry=geometry(103)))
        self.assertEqual(self.graph.object_asof('o:A',20).object.version_id[2:],e['replay_version'])
        self.assertEqual(self.graph.object_asof('o:A',30).object.version_id[2:],e['current_version'])
        self.assertEqual(self.graph.engineering_scope()['visual_replay_button_certifies_asof'],e['visual_replay_button_certifies_asof'])
        self.assert_parity(20);self.assert_parity(30)

    def test_f10_26_actual_completion_not_backdraw_or_double_delay(self):
        e=self.expected(26);ev=evidence('A',8)
        anchor=AnchorVersion('a:A','av:A0',0,None,(ev.version_id,),1,5,9,9)
        a=obj(at=12,ev=ev,anchors=(anchor.version_id,),confirmed=9)
        clock=PublicationClock(9,8,12,actual_completion_at=12)
        self.commit(ev,anchor,a,clock=clock,at=12)
        self.assertEqual(a.known_at,e['known_at']);self.assertEqual(self.active(11),e['cut11_active']);self.assertEqual(self.active(12),e['cut12_active'])
        with self.assertRaises(ContractError):PublicationClock(9,8,12,actual_completion_at=12,simulated_start_at=9,simulated_duration_ns=3,assumption_id='double')
        self.assert_parity(12)

    def test_f10_27_parent_dag_and_conflict_rollback(self):
        e=self.expected(27);a=self.birth();b=self.birth('B');self.commit(Presentation('view:base','o:A',10,'p','u'))
        self.assertEqual(self.graph.sequence,self.goldens['F10-27']['given']['valid_existing_prefix_records'])
        head=self.graph.head
        ab=relation('ab',a.version_id,b.version_id,20,kind=RelationKind.PARENT)
        ba=relation('ba',b.version_id,a.version_id,20,kind=RelationKind.PARENT)
        with self.assertRaises(ContractError):self.commit(ab,ba)
        self.assertEqual(self.graph.head,head)
        with self.assertRaises(ContractError):self.commit(obj('orphan',20,ev=evidence('A'),parents=('v:missing0',)))
        self.assertEqual(self.graph.head,head)
        with self.assertRaises(IntegrityError):self.commit(replace(a,geometry=geometry(120)),at=20)
        self.assertEqual(self.graph.sequence,e['records_after_each_rejection']);self.assert_parity(20)

    def test_f10_28_measured_targeted_update_vs_full_reference(self):
        e=self.expected(28)
        def start(graph=None):
            return (time.perf_counter(),time.process_time(),resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                    {} if graph is None else dict(graph.stats))
        def finish(mark,graph):
            wall,cpu,rss,previous=mark
            return {'wall_seconds':time.perf_counter()-wall,'cpu_seconds':time.process_time()-cpu,
                    'rss_peak_before_bytes':rss,'rss_peak_after_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                    'operations':{k:int(v-previous.get(k,0)) for k,v in graph.stats.items()}}
        mark=start();self.path=Path(self.temp.name)/'measured.sqlite'
        self.graph=ObjectGraph(self.path,definition=self.definition)
        for first in range(0,1000,32):
            members=[]
            for n in range(first,min(first+32,1000)):
                name=f'O{n:04d}';ev=evidence(f'E{n:04d}',10);members.extend((ev,obj(name,10,ev=ev)))
            self.commit(*members)
        parent=self.graph.get_version('v:O00070');ev7=evidence('E0007',10)
        child=obj('C0007',10,ev=ev7,parents=(parent.version_id,));grand=obj('G0007',10,ev=ev7,parents=(child.version_id,))
        self.commit(child,grand);construction=finish(mark,self.graph)
        before={o.object_id:o.version_id for o in self.graph.active_set(10)}
        mark=start(self.graph);snapshot=self.graph.checkpoint();checkpoint_phase=finish(mark,self.graph)
        mark=start(self.graph);self.commit(evidence('E0007',20,revision=1));update=finish(mark,self.graph)
        mark=start(self.graph)
        active={o.object_id:o.version_id for o in self.graph.active_set(20)}
        dirty_views=[self.graph.object_asof('o:'+id,20) for id in ('O0007','C0007','G0007')]
        query=finish(mark,self.graph)
        mark=start(self.graph);reference=LiteralObjectGraph(journal(self.graph));view=reference.view(20);full=finish(mark,self.graph)
        full['literal_records_decoded']=reference.last_records_decoded
        full['literal_bytes_read']=reference.last_bytes_read
        full['literal_support_checks']=reference.last_support_checks
        full['literal_object_evaluations']=reference.last_object_evaluations
        dirty=sorted(s['object_id'] for s in view['states'] if s['dirty'])
        evaluated=update['operations']['object_evaluations']
        self.assertEqual(short_ids(dirty),sorted(e['dirty_ids']))
        self.assertEqual(evaluated,e['targeted_object_evaluations'])
        self.assertEqual(reference.last_object_evaluations,e['full_object_evaluations'])
        self.assertEqual(any(v.available(20,self.definition.ttl_ns) for v in dirty_views),e['pending_dirty_objects_action_eligible'])
        unchanged=sum(active.get(id)==vid for id,vid in before.items() if id not in dirty)
        self.assertEqual(unchanged,e['unaffected_object_versions_unchanged'])
        self.assertEqual(sorted(active.values())==sorted(view['active_versions']),e['semantic_outputs_equal'])
        mark=start();restored=ObjectGraph.restore(self.path,definition=self.definition,checkpoint=snapshot);restore_phase=finish(mark,restored)
        self.assertEqual(restore_phase['operations']['object_evaluations'],0)
        self.assertEqual(restore_phase['operations']['suffix_batches_replayed'],1)
        self.graph=restored;self.assert_parity(20)
        ENGINEERING_METRICS.clear()
        ENGINEERING_METRICS.update({'schema_version':'F10.EngineeringMetrics.v2','case_id':'F10-28',
            'successful_assertion_id':self.id(),'semantic_parity':True,'objects':1002,
            'targeted_object_evaluations':evaluated,'literal_object_evaluations':reference.last_object_evaluations,
            'dirty_ids':dirty,'unaffected_versions':unchanged,
            'phases':{'construction':construction,'checkpoint':checkpoint_phase,'targeted_update':update,
                      'indexed_query':query,'full_reference':full,'restore':restore_phase},
            'rss_scope':'shared worker process high-water mark; no isolated allocation claim',
            'io_scope':'logical returned SQLite row bytes and rows, journal bytes/records; physical disk IO not measured',
            'sqlite_vm_scope':'progress callback every 1000 VM instructions; count is a lower bound per statement',
            'work_counter_definition':'object_evaluations counts final affected latest-object predicates; support_checks includes recursive/admission calls; hot metadata, capacity, all SQL row reads, integrity folding and VM lower-bound work are separate counters',
            'timing_speedup_claimed':False,'native_or_economic_certification':False})

    def test_f10_29_checkpoint_exact_prefix_and_suffix_integrity(self):
        e=self.expected(29);a=self.birth();first,_=self.observe(a,'enter',20);snapshot=self.graph.checkpoint()
        _,suffix=self.observe(a,'exit',25,kind=ObservationKind.EXIT,predecessor=first.event_id)
        restored=ObjectGraph.restore(self.path,definition=self.definition,checkpoint=snapshot)
        self.assertEqual(restored.stats['suffix_batches_replayed'],len(e['valid_suffix_replayed']))
        self.assertEqual(plain(restored.visits_asof(25)),plain(self.graph.visits_asof(25)))
        original_visits=plain(restored.visits_asof(25))
        self.assertFalse(restored.commit_batch(suffix,expected_head=restored.head)[1])
        self.assertEqual(plain(restored.visits_asof(25)),original_visits)
        self.assertEqual(restored.stats['object_evaluations'],len(e['valid_prefix_replayed']))
        for field,value in [('definition','wrong'),('head','wrong'),('cursor',999),('pending_free',False),('projection_digest','tamper')]:
            broken={**snapshot,field:value}
            broken['content_hash']=content_hash({k:v for k,v in broken.items() if k!='content_hash'})
            with self.subTest(field=field),self.assertRaises(IntegrityError):ObjectGraph.restore(self.path,definition=self.definition,checkpoint=broken)
        with sqlite3.connect(self.path) as con:
            con.execute('DROP TRIGGER batch_no_update');con.execute("UPDATE batches SET payload=? WHERE sequence=1",(b'{}',))
        with self.assertRaises(IntegrityError):ObjectGraph.restore(self.path,definition=self.definition,checkpoint=snapshot)

    def test_f10_30_batch_and_active_capacity_atomic_failure(self):
        e=self.expected(30)
        values=tuple(evidence('overflow'+str(i),10) for i in range(129))
        before=self.graph.head
        with self.assertRaises(DependencyUnavailable):self.commit(*values)
        self.assertEqual(self.graph.head,before)
        for start in range(0,2048,32):
            members=[]
            for n in range(start,start+32):
                ev=evidence(f'cap{n}',10);members.extend((ev,obj(f'cap{n}',10,ev=ev)))
            self.commit(*members)
        before=self.graph.head;count=self.graph.sequence
        with self.assertRaises(DependencyUnavailable):self.birth('overflow',20)
        self.assertEqual(self.graph.head,before);self.assertEqual(self.graph.sequence,count);self.assertEqual(len(self.graph.active_set(20)),e['old_active_count'])
        self.assertEqual(len(self.graph.revisions('o:cap0')),1)

    def test_f10_31_same_cut_batch_and_frozen_frontier(self):
        e=self.expected(31);ev=evidence('A',10);a=obj(at=20,ev=ev);a1=revised(a,20)
        batch=self.commit(ev,a,a1,at=20)
        prior_cursor=self.graph.sequence
        self.commit(Presentation('view:same-cut','o:A',20,'p','u'))
        self.assertEqual(self.graph.sequence,prior_cursor+1)
        self.assertEqual(self.graph.object_asof('o:A',20,cursor=prior_cursor).object.version_id,'v:A1')
        self.assertEqual(self.graph.get_version('view:same-cut').known_at,20)
        cut=self.graph.freeze_candidates(cut_id='cut:20',at=20,instrument=instrument(),expected_head=self.graph.head)
        self.assertEqual(short_ids(cut['candidate_versions']),[e['frozen_latest']])
        with self.assertRaises(ContractError):self.birth('B',20)
        self.assertFalse(self.graph.commit_batch(batch,expected_head=self.graph.head)[1])
        self.assertEqual(self.active(20),['A1']);self.assertEqual(len(self.graph.revisions('o:A')),2)
        self.assert_parity(20)

    def test_f10_32_invalidation_closes_visit_and_keeps_ordinal(self):
        e=self.expected(32);a=self.birth();self.observe(a,'enter1',12)
        a1=revised(a,20,existence=Existence.INVALIDATED,eligibility=Eligibility.INELIGIBLE);self.commit(a1)
        a2=revised(a1,30,existence=Existence.ACTIVE,eligibility=Eligibility.ELIGIBLE);self.commit(a2)
        self.observe(a2,'enter2',32,visit='V2')
        visits=self.graph.visits_asof(32)
        self.assertEqual(visits[0]['state'],e['V1_state']);self.assertEqual(visits[0]['reset_at'],e['V1_reset_at']);self.assertEqual(visits[1]['ordinal'],e['V2_ordinal'])
        self.assertEqual(sum(v['state'] not in {'reset','closed'} for v in visits),e['open_visits']);self.assertEqual([v['ordinal'] for v in visits],e['visit_history_ordinals']);self.assert_parity(32)

    def test_f10_33_target_binding_rejects_new_geometry_and_future_member(self):
        e=self.expected(33);a=self.birth();self.graph.freeze_candidates(cut_id='cut:15',at=15,instrument=instrument(),expected_head=self.graph.head)
        a1=revised(a,20,geometry=Geometry(Fraction(102),Fraction(104),Fraction(102),Fraction(104),'g2','NQH5','NQH5'));self.commit(a1)
        head=self.graph.head
        with self.assertRaises(ContractError):self.graph.bind_target(target_id='target:wrong',cut_id='cut:15',object_version=a.version_id,geometry=a1.geometry,horizon_end=40,observation_process='toy',expected_head=head)
        with self.assertRaises(ContractError):self.graph.bind_target(target_id='target:future',cut_id='cut:15',object_version=a1.version_id,geometry=a1.geometry,horizon_end=40,observation_process='toy',expected_head=head)
        self.assertEqual(self.graph.head,head)
        good=self.graph.bind_target(target_id='target:good',cut_id='cut:15',object_version=a.version_id,geometry=a.geometry,horizon_end=40,observation_process='toy',expected_head=head)
        self.assertEqual([a.geometry.lower,a.geometry.upper],e['valid_target_geometry']);self.assertEqual(good['horizon_end'],e['fixed_end']);self.assert_parity(20)

    def test_f10_34_geometry_revision_preserves_visit_start(self):
        e=self.expected(34);a=self.birth();first,_=self.observe(a,'enter1',12)
        a1=revised(a,20,geometry=Geometry(Fraction(102),Fraction(104),Fraction(102),Fraction(104),'g2','NQH5','NQH5'));self.commit(a1)
        last,_=self.observe(a1,'exit',25,kind=ObservationKind.EXIT,predecessor=first.event_id)
        visits=self.graph.visits_asof(25)
        self.assertEqual(visits[0]['start_geometry'][2:],e['visit_birth_geometry']);self.assertEqual(last.object_version[2:],e['exit_observation_geometry']);self.assertEqual(len(visits),e['visit_count'])
        self.assertEqual(visits[0]['entered_at'],12)
        self.assertEqual(any(v.kind in {ObservationKind.ENTER,ObservationKind.CONTACT} and v.object_version==a1.version_id for v in self.graph.events_asof(25)),e['retroactive_contact_at_new_band']);self.assert_parity(25)

    def test_f10_repair_relation_support_and_complete_ancestry(self):
        a=self.birth();b=self.birth('B')
        edge=relation('lineage',a.version_id,b.version_id,12,kind=RelationKind.PARENT)
        self.commit(edge)
        self.commit(revised(a,20,existence=Existence.INVALIDATED,eligibility=Eligibility.INELIGIBLE))
        self.assertTrue(self.graph.object_asof('o:B',20).dirty)
        self.assertFalse(self.graph.object_asof('o:B',19).dirty)
        self.assert_parity(19);self.assert_parity(20)
        self.commit(replace(edge,version_id='rv:lineage1',revision=1,predecessor=edge.version_id,known_at=25,tombstone=True))
        self.assertFalse(self.graph.object_asof('o:B',25).dirty);self.assert_parity(25)
        parent=self.birth('parent',30)
        child=obj('child',35,ev=evidence('parent'),parents=(parent.version_id,))
        self.commit(child)
        self.commit(revised(parent,40,existence=Existence.SUPERSEDED,eligibility=Eligibility.INELIGIBLE))
        cut=self.graph.freeze_candidates(cut_id='cut:closure',at=45,instrument=instrument(),expected_head=self.graph.head)
        retained={m['value'].get('version_id') for m in cut['lineage_versions']}
        self.assertIn(parent.version_id,retained)
        self.assertIn((parent.version_id,child.version_id),cut['parent_edges'])
        self.assertEqual(plain(cut['parent_edges']),plain(self.graph.lineage_closure(tuple(v.object.version_id for v in (self.graph.object_asof('o:A',45),self.graph.object_asof('o:B',45),self.graph.object_asof('o:child',45),self.graph.object_asof('o:parent',45))),45)['parent_edges']))
        self.assert_parity(45)

    def test_f10_repair_mapping_origins_and_effective_input_clocks(self):
        xinst,yinst=instrument('X'),instrument('Y')
        x=self.birth('X',ev=evidence('X',inst=xinst),inst=xinst)
        mapping=evidence('map',20,inst=xinst,purpose=EvidencePurpose.MAPPING,mapped=yinst)
        ey=evidence('Y',20,inst=yinst)
        y=obj('Y',20,ev=ey,inst=yinst,parents=(x.version_id,),geom=geometry(source='X',execution='Y'),mapping=mapping.version_id,origins=('s:Y','s:X','s:map'))
        self.commit(mapping,ey,y)
        self.commit(evidence('map',25,revision=1,inst=xinst,purpose=EvidencePurpose.MAPPING,mapped=yinst))
        self.assertTrue(self.graph.object_asof('o:Y',25).dirty);self.assert_parity(25)
        self.assertEqual(y.birth.source_origins,('s:X','s:Y','s:map'))
        before=self.graph.checkpoint()
        with self.assertRaises(DependencyUnavailable):self.commit(revised(y,30))
        self.assertEqual(self.graph.checkpoint(),before)
        with self.assertRaises(ContractError):PublicationClock(20,10,15,actual_completion_at=15)
        with self.assertRaises(ContractError):replace(evidence('future',10),event_at=11)
        late=evidence('late',5);self.commit(late,at=30)
        proposed=obj('late',40,ev=late)
        with self.assertRaises(ContractError):self.commit(proposed,at=40,clock=PublicationClock(10,10,40,actual_completion_at=40))
        self.assertEqual(BirthKey('fixture','v1',instrument(),(),('s:b','s:a'),'same').version,BirthKey('fixture','v1',instrument(),(),('s:a','s:b'),'same').version)
        with self.assertRaises(ContractError):self.commit(obj('subset',40,ev=late,origins=()))
        with self.assertRaises(ContractError):RegistryDefinition(initial_states=(Existence.EXPIRED,))
        with self.assertRaises(ContractError):RegistryDefinition(generator_versions=(('fixture','v1'),('fixture','v2')))
        anchor=AnchorVersion('a:cross','av:cross0',0,None,('e:X:0',),0,5,5,5)
        ey2=evidence('cross',40,inst=yinst)
        bad=obj('cross',40,ev=ey2,inst=yinst,anchors=(anchor.version_id,),origins=('s:cross','s:X'))
        with self.assertRaises(ContractError):self.commit(anchor,ey2,bad)

    def test_f10_repair_history_pages_and_current_visit_index(self):
        a=self.birth();ev=evidence('visit-stream',20);self.commit(ev)
        members=[]
        for n in range(260):
            first=ObservationEvent(f'obs:p{n:04d}a',a.version_id,f'visit:p{n:04d}',ObservationKind.ENTER,20,20,(ev.version_id,),'ordered source')
            last=ObservationEvent(f'obs:p{n:04d}b',a.version_id,first.visit_id,ObservationKind.EXIT,20,20,(ev.version_id,),'ordered source',first.event_id)
            members.extend((first,last))
        for first in range(0,len(members),128):self.commit(*members[first:first+128])
        events=[];after=None
        while True:
            page=self.graph.events_asof(20,object_id='o:A',after_event=after)
            if not page:break
            self.assertLessEqual(len(page),256);events.extend(page);after=page[-1].event_id
        visits=[];after=('','')
        while True:
            page=self.graph.visits_asof(20,object_id='o:A',after=after)
            if not page:break
            self.assertLessEqual(len(page),256);visits.extend(page);after=(page[-1]['object_id'],page[-1]['visit_id'])
        self.assertEqual(len(events),520);self.assertEqual(len(visits),260)
        self.assertEqual([v['ordinal'] for v in visits],list(range(1,261)))
        literal=LiteralObjectGraph(journal(self.graph)).view(20)
        self.assertEqual(plain(events),literal['events']);self.assertEqual(plain(visits),literal['visits'])
        with self.assertRaises(ContractError):self.graph.events_asof(20,limit=257)
        before=self.graph.checkpoint()
        with self.assertRaises(DependencyUnavailable):self.observe(a,'unknown-order',25,visit='unknown',order=False)
        self.assertEqual(self.graph.checkpoint(),before)
        self.commit(evidence('visit-stream',25,revision=1,support=Support.TOMBSTONED))
        stale=ObservationEvent('obs:stale',a.version_id,'visit:stale',ObservationKind.ENTER,30,30,(ev.version_id,),'stale source')
        with self.assertRaises(ContractError):self.commit(stale)

    def test_f10_repair_ttl_capacity_and_reset_policy(self):
        self.definition=RegistryDefinition(ttl_ns=5,hot_active_max=1,visit_reset_policy='reset_on_geometry_change')
        self.path=Path(self.temp.name)/'lifetime.sqlite';self.graph=ObjectGraph(self.path,definition=self.definition)
        a=self.birth();self.observe(a,'contact',11)
        a1=revised(a,12,geometry=geometry(101));self.commit(a1)
        self.assertEqual(self.graph.visits_asof(12)[0]['reset_reason'],'geometry_revision');self.assert_parity(12)
        b=self.birth('B',16)
        self.assertEqual(self.graph.hot_ids,frozenset({'o:B'}))
        self.assertEqual(self.graph.active_set(16),(b,))
        self.assertIsNone(self.graph.fallback('o:A',16,policy='previous_valid')['object_version'])
        with self.assertRaises(DependencyUnavailable):self.observe(a1,'expired',17,visit='expired')
        self.assertEqual(self.graph.get_version(a.version_id),a)
        self.assert_parity(16)

    def test_f10_repair_int64_lifetime_boundaries(self):
        low,high=-(2**63),2**63-1
        self.definition=RegistryDefinition(hot_active_max=2,hot_relations_max=1)
        self.path=Path(self.temp.name)/'int64-unbounded.sqlite'
        self.graph=ObjectGraph(self.path,definition=self.definition)
        a=self.birth('A',high-2);b=self.birth('B',high-2)
        prefix=self.graph.sequence
        self.commit(relation('upper',a.version_id,b.version_id,high-1))
        snapshot=self.graph.checkpoint()
        self.commit(evidence('clock-only',high))
        self.assertTrue(self.graph.object_asof('o:A',high).available(high))
        self.assertEqual(self.graph.active_set(high),(a,b))
        self.assertEqual(self.graph.hot_ids,frozenset({'o:A','o:B'}))
        self.assertEqual(self.graph.active_set(high-2,cursor=prefix),(a,b))
        head=self.graph.head
        with self.assertRaises(DependencyUnavailable):self.birth('overflow',high)
        with self.assertRaises(DependencyUnavailable):self.commit(relation('overflow',a.version_id,b.version_id,high))
        self.assertEqual(self.graph.head,head)
        self.graph=ObjectGraph.restore(self.path,definition=self.definition,checkpoint=snapshot)
        self.assertEqual(self.graph.active_set(high),(a,b));self.assertEqual(self.graph.hot_ids,frozenset({'o:A','o:B'}))
        self.assert_parity(high)
        for ttl in (5,2**65):
            with self.subTest(ttl=ttl):
                self.definition=RegistryDefinition(ttl_ns=ttl)
                self.path=Path(self.temp.name)/('int64-lower-'+str(ttl)+'.sqlite')
                self.graph=ObjectGraph(self.path,definition=self.definition)
                ev=evidence('lower',low);a=obj('lower',low,ev=ev,confirmed=low)
                self.commit(ev,a,at=low);prefix=self.graph.sequence
                self.commit(evidence('clock-only',low+2))
                self.assertEqual(self.graph.active_set(low+1,cursor=prefix),(a,))
                self.assertTrue(self.graph.object_asof('o:lower',low+1,cursor=prefix).available(low+1,ttl))
                self.assert_parity(low+1,cursor=prefix)
        self.definition=RegistryDefinition(ttl_ns=5)
        self.path=Path(self.temp.name)/'int64-upper-ttl.sqlite';self.graph=ObjectGraph(self.path,definition=self.definition)
        a=self.birth('upper-ttl',high-1)
        self.assertEqual(self.graph.active_set(high),(a,))
        self.assertTrue(self.graph.object_asof(a.object_id,high).available(high,5))
        self.graph=ObjectGraph.restore(self.path,definition=self.definition,checkpoint=self.graph.checkpoint())
        self.assertEqual(self.graph.hot_ids,frozenset({a.object_id}));self.assert_parity(high)
        self.definition=RegistryDefinition()
        self.path=Path(self.temp.name)/'int64-real-expiry.sqlite';self.graph=ObjectGraph(self.path,definition=self.definition)
        inst=replace(instrument(),valid_until=high);ev=evidence('ends',high-1,inst=inst)
        a=self.birth('ends',high-1,ev=ev,inst=inst)
        self.assertEqual(self.graph.active_set(high-1),(a,));self.assertEqual(self.graph.active_set(high),())
        self.assertFalse(self.graph.object_asof(a.object_id,high).available(high));self.assert_parity(high)

    def test_f10_repair_all_public_indexes_and_checkpoint_metadata(self):
        a=self.birth();child=obj('child',12,ev=evidence('A'),parents=(a.version_id,));self.commit(child)
        self.observe(a,'open',13)
        self.commit(relation('edge',a.version_id,child.version_id,14,kind=RelationKind.PARENT))
        self.graph.freeze_candidates(cut_id='cut:index',at=15,instrument=instrument(),expected_head=self.graph.head)
        snapshot=self.graph.checkpoint()
        mutations=(
            "UPDATE births SET born_at=born_at+1",
            "DELETE FROM dependencies",
            "DELETE FROM ancestry",
            "UPDATE current_objects SET dirty=1-dirty",
            "UPDATE current_relations SET hot_until=0",
            "DELETE FROM open_visits",
            "UPDATE visit_counters SET ordinal=ordinal+1",
            "DELETE FROM relation_endpoints",
            "UPDATE object_states SET known_at=known_at+1",
            "UPDATE visit_states SET object_id='o:forged'",
            "DROP TRIGGER record_no_update",
            "INSERT INTO births VALUES ('injected','o:injected',0)")
        for n,sql in enumerate(mutations):
            with self.subTest(index=n):
                path=Path(self.temp.name)/f'tamper-{n}.sqlite';shutil.copyfile(self.path,path)
                with sqlite3.connect(path) as con:con.execute(sql)
                with self.assertRaises(IntegrityError):ObjectGraph.restore(path,definition=self.definition,checkpoint=snapshot)
        for table,sql,trigger in (('records',"UPDATE records SET known_at=known_at+1",'record_no_update'),('controls',"UPDATE controls SET sequence=sequence+1",'control_no_update')):
            path=Path(self.temp.name)/(table+'.sqlite');shutil.copyfile(self.path,path)
            with sqlite3.connect(path) as con:
                con.execute('DROP TRIGGER '+trigger);con.execute(sql)
            with self.assertRaises(IntegrityError):ObjectGraph.restore(path,definition=self.definition,checkpoint=snapshot)
        broken={**snapshot,'indexes_digest':'f'*64};broken['content_hash']=content_hash({k:v for k,v in broken.items() if k!='content_hash'})
        with self.assertRaises(IntegrityError):ObjectGraph.restore(self.path,definition=self.definition,checkpoint=broken)
        self.assertEqual(ObjectGraph.restore(self.path,definition=self.definition,checkpoint=snapshot).checkpoint(),snapshot)

    def test_f10_repair_immutable_atomic_instrument_payload(self):
        a=self.birth();self.observe(a,'NQ',12)
        other=instrument('ESH5');b=self.birth('ES',14,ev=evidence('ES',inst=other),inst=other)
        self.observe(b,'ES-contact',15,visit='ES')
        cut=self.graph.freeze_candidates(cut_id='cut:NQ',at=20,instrument=instrument(),expected_head=self.graph.head)
        with self.assertRaises(TypeError):cut['candidate_count']=99
        with self.assertRaises(TypeError):cut['instrument']['raw_symbol']='wrong'
        with self.assertRaises(TypeError):cut['candidate_versions'][0]='v:wrong'
        payload=json.loads(self.graph.lineage_payload(20,instrument=instrument(),cut_id='cut:NQ'))
        self.assertEqual([v['object_id'] for v in payload['objects']],['o:A'])
        self.assertEqual([v['event_id'] for v in payload['observations']],['obs:NQ'])
        self.assertEqual([v['object_id'] for v in payload['visits']],['o:A'])
        self.assertEqual(payload['known_time'],20)
        with self.assertRaises(ContractError):self.graph.lineage_payload(19,instrument=instrument(),cut_id='cut:NQ')
        with self.assertRaises(ContractError):self.graph.lineage_payload(20,instrument=other,cut_id='cut:NQ')
        self.assertEqual(json.loads(self.graph.lineage_payload(22,instrument=instrument()))['known_time'],20)
        self.assertFalse(self.graph.engineering_scope()['phase_P5_complete'])

    def test_f10_repair_dirty_closure_capacity_is_atomic(self):
        self.definition=RegistryDefinition(payload_bytes_max=20000)
        self.path=Path(self.temp.name)/'closure-bound.sqlite';self.graph=ObjectGraph(self.path,definition=self.definition)
        ev=evidence('shared',10);self.commit(ev)
        for n in range(64):self.commit(obj('dependent'+str(n),10,ev=ev))
        before=self.graph.checkpoint()
        with self.assertRaises(DependencyUnavailable):self.commit(evidence('shared',20,revision=1))
        self.assertEqual(self.graph.checkpoint(),before)
        self.assertEqual(len(self.graph.active_set(20)),64)
        self.assertEqual(self.graph.get_version(ev.version_id),ev)
