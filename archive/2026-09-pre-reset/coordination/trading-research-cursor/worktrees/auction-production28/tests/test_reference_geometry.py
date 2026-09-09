"""Complete M12 measurement vectors over actual calendar/trade/reference ports."""

import json
import unittest
from dataclasses import replace
from datetime import date, timedelta
from fractions import Fraction as F
from pathlib import Path

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.bars import WindowCoverage
from trading_research.foundations.calendar import Calendar, Session
from trading_research.foundations.object_graph import ObjectGraph, RegistryDefinition, PublicationClock
from trading_research.measurements.reference_geometry import (
    ReferenceLimits, observe_open, validate_open, bind_open, bind_session_reference, bind_official_reference,
    validate_reference, period_identity, period_open, prior_reference_scale, normalized_gap, reference_status,
    ReferenceGraph, bind_reference_coordinate, bridge_gap, interpolate_references, floor_pivots, pivot_interval_bands,
    gap_target, gap_targets, gap_outcome, validate_gap_target, validate_gap_outcome, GapOutcomeLedger, publish_open_reference,
)
from trading_research.measurements.reference_prices import OfficialSettlement
from trading_research.measurements.tape import Trade, TradeLedger
from trading_research.research.object_labels import ExactPoint
from trading_research.research.labels import ObservationWindow
from tests.measurement_sources import Sources, INSTRUMENT
from tests.measurement_fixtures import row, ledger
from references import reference_geometry_literal as literal


GOLD={c['id']:c for c in json.loads((Path(__file__).parent/'golden/m12_complete_reference_measurement_v1.json').read_text())['cases']}


class ReferenceGeometryTests(unittest.TestCase):
    def setUp(self):
        self.s=Sources(self)

    def opening(self, price=100, *, start=0,end=100,at=10,known=None,cut=11,published=12,
                spans=None,horizon=200,day=date(2026,1,5),name='session',rows=None,calendar=None,semantic='session_first_eligible_trade'):
        rows=[row('first',at=at,known=known,price=price,instrument=self.s.instrument.raw_symbol)] if rows is None else rows
        view=ledger(rows)
        cal,graph,selection=self.s.clock(start,end,day=day,cut=cut,name=name,calendar=calendar)
        cov=WindowCoverage(self.s.instrument.raw_symbol,start,end,((start,cut),) if spans is None else spans,cut,'opening-coverage')
        obs=observe_open(selection,view,coverage=cov,cut=cut,published_at=published,horizon_end=horizon,semantic=semantic)
        return obs,view,cal,graph,selection

    def official(self, value, *, name='settlement',observed=-3,known=-2,cut=-2,published=None,horizon=10**14,messages=None):
        published=cut if published is None else published
        messages=(OfficialSettlement(name,name+':v1',0,None,self.s.instrument,observed,known,known,F(value),name+':source'),) if messages is None else messages
        result=bind_official_reference(messages,cut=cut,clocks=PublicationClock(cut,min(known,cut),published,actual_completion_at=published),horizon_end=horizon)
        return result,messages

    @staticmethod
    def _trade_ticks(value):
        exact=F(value)
        if exact.denominator != 1:
            raise ValueError('fixture trade price must be an exact integral tick')
        return exact.numerator

    def pair(self, initial=110,reference=100, *,cut=0,horizon=10**14):
        obs,*_=self.opening(self._trade_ticks(initial),start=cut-3,end=cut+1,at=cut-1,cut=cut,published=cut,horizon=horizon)
        prior,_=self.official(reference,observed=cut-3,known=cut-2,cut=cut-2,horizon=horizon)
        return bind_open(obs),prior

    def test_MR01_MR02_early_open_and_quiet_prefix(self):
        for case in ('MR01','MR02'):
            x=GOLD[case]['inputs'];r=x['trades'][0]
            obs,*_=self.opening(r[2],start=x['window'][0],end=x['window'][1],at=r[0],known=r[1],cut=x['cut'],
                published=x['published_at'],spans=tuple(map(tuple,x['coverage'])))
            expected=literal.opening(x['trades'],x['window'][0],x['cut'],x['coverage'])
            self.assertEqual((obs.reference.value_ticks,obs.first_observed.value_ticks,obs.possible_first_prices),expected)
            self.assertEqual(obs.incomplete_open,case=='MR02');self.assertFalse(obs.enclosing_session_complete)
        healthy,*_=self.opening(103,at=30,cut=40,published=41)
        self.assertEqual(healthy.reference.value_ticks,103)
        self.assertEqual((healthy.reference.observed_at,healthy.reference.known_at),(30,41))

    def test_MR03_MR08_future_suffix_and_date_identity(self):
        values=[self.opening(100,start=i*100,end=(i+1)*100,at=i*100+10,cut=i*100+11,published=i*100+12,
            horizon=1000,day=date(2026,1,5)+timedelta(days=i),rows=[] if i==2 else None)[0] for i in range(3)]
        self.assertEqual(values[0].reference.value_ticks,values[1].reference.value_ticks)
        self.assertNotEqual(values[0].reference.version,values[1].reference.version)
        self.assertIsNone(values[2].reference.value_ticks)
        obs,view,cal,*_=self.opening(101,at=20,known=20,cut=10,published=11)
        before=obs.record();self.assertIsNone(obs.reference.value_ticks)
        old=cal.resolve(date(2026,1,5),'NQ',cut=10)
        cal.append(replace(old,known_at=20,close_at=200,source_version='future-calendar'))
        validate_open(obs);self.assertEqual(obs.record(),before)
        empty,*_=self.opening(rows=[],cut=10,published=11)
        self.assertEqual((empty.reference.value_ticks,empty.possible_first_prices),(obs.reference.value_ticks,obs.possible_first_prices))

    def period_fixture(self, statuses, *, start_day,current_date,observed_values,missing=False):
        cal=Calendar();observations=[]
        for i,status in enumerate(statuses):
            day=start_day+timedelta(days=i);start=i*100;end=start+50
            if status=='missing':continue
            value=observed_values.get(day)
            if status=='closed':
                cal.append(Session('s:'+day.isoformat(),day,'NQ',start,end,(),0,-1,'cal:'+day.isoformat(),'synthetic',False,'closed'))
                continue
            rows=[] if value is None else [row('trade:'+day.isoformat(),at=start+2,price=value,instrument=self.s.instrument.raw_symbol)]
            obs,_,cal,*_=self.opening(start=start,end=end,at=start+2,cut=end,published=end,horizon=10000,day=day,rows=rows,calendar=cal,
                spans=() if missing and i==0 else ((start,end),))
            observations.append(obs)
        return cal,tuple(observations)

    def test_MR04_MR05_MR06_MR07_period_calendar_traversal(self):
        monday=date(2026,1,5);wednesday=date(2026,1,7)
        for first in ('missing','closed'):
            cal,obs=self.period_fixture([first,'eligible','eligible'],start_day=monday,current_date=wednesday,
                observed_values={monday+timedelta(days=1):101,wednesday:105})
            out=period_open(calendar=cal,instrument_root='NQ',current_date=wednesday,period='iso_week',observations=obs,cut=300)
            if first=='missing':self.assertEqual((out['status'],out['selected_date'],out['producer_reads']),('calendar_unavailable',None,0))
            else:
                self.assertEqual((out['period_key'],out['selected_date'],out['open'].value_ticks),('2026-W02','2026-01-06',101))
                self.assertEqual(tuple(x[0] for x in out['traversed']),('2026-01-05','2026-01-06'))
        first=date(2026,1,1);current=date(2026,1,2)
        cal,obs=self.period_fixture(['closed','eligible'],start_day=first,current_date=current,observed_values={current:102})
        for period,key in (('month','2026-01'),('quarter','2026-Q1'),('year','2026')):
            out=period_open(calendar=cal,instrument_root='NQ',current_date=current,period=period,observations=obs,cut=300)
            self.assertEqual((out['period_key'],out['selected_date'],out['open'].value_ticks),(key,current.isoformat(),102))
        first=date(2025,12,29)
        cal,obs=self.period_fixture(['eligible'],start_day=first,current_date=current,observed_values={first:99})
        out=period_open(calendar=cal,instrument_root='NQ',current_date=current,period='iso_week',observations=obs,cut=300)
        self.assertEqual((out['period_key'],out['selected_date'],out['open'].value_ticks),('2026-W01',first.isoformat(),99))
        self.assertEqual(period_identity(current,'month')[0],'2026-01')

    def test_MR09_quiet_session_does_not_mean_missing_session(self):
        monday=date(2026,1,5);tuesday=monday+timedelta(days=1)
        for missing in (False,True):
            cal,obs=self.period_fixture(['eligible','eligible'],start_day=monday,current_date=tuesday,observed_values={tuesday:101},missing=missing)
            out=period_open(calendar=cal,instrument_root='NQ',current_date=tuesday,period='iso_week',observations=obs,cut=300)
            self.assertEqual(out['first_observed'].value_ticks,101)
            self.assertEqual(out['open'].value_ticks if out['open'] else None,None if missing else 101)

    def test_MR10_MR11_MR12_actual_prior_normalization_and_types(self):
        for current,prior,scale,expected in ((110,100,5,2),(-10,-20,5,2),(100,100,5,0),(110,100,0,None)):
            a,b=self.pair(current,prior,cut=12)
            view,c,_=self.s.capture([row('scale1',at=1,price=100),row('scale2',at=2,price=100+scale)],end=9,cut=9,published=11)
            s=prior_reference_scale(c,view=view)
            value=normalized_gap(a,b,scale=s,cut=12,published_at=13,maximum_age_ns=100)
            self.assertEqual((value['gap_ticks'],value['normalized_gap']),(current-prior,expected))
            self.assertEqual(value['direction'],0 if current==prior else 1)
        with self.assertRaises(IntegrityError):
            changed=replace(s,value_ticks=F(-1));object.__setattr__(changed,'_recipe',s._recipe)
            normalized_gap(a,b,scale=changed,cut=12,published_at=13,maximum_age_ns=100)
        future=replace(s,published_at=13);object.__setattr__(future,'_recipe',s._recipe)
        with self.assertRaises(IntegrityError):normalized_gap(a,b,scale=future,cut=12,published_at=13,maximum_age_ns=100)
        a,b=self.pair(110,100,cut=12)
        settle,_=self.official(102,name='settlement-secondary',observed=1,known=10,cut=10)
        g=ReferenceGraph((a,b,settle),edges=((a.reference.id,b.reference.id),(a.reference.id,settle.reference.id)),cut=12,published_at=13,maximum_age_ns=100)
        self.assertEqual(tuple(e[2] for e in g.edges),(10,8))
        self.assertNotEqual(a.reference.kind,settle.reference.kind)
        with self.assertRaises(DependencyUnavailable):self.official(102,known=20,cut=10)

    def test_MR13_MR14_MR15_MR16_graph_consensus_triangle_and_age(self):
        bindings=tuple(bind_open(self.opening(v,at=2,cut=20,published=20,name='venue'+str(i))[0]) for i,v in enumerate((100,102,104)))
        graph=ReferenceGraph(bindings,edges=(),cut=22,published_at=23,maximum_age_ns=100)
        self.assertEqual(tuple(r[1:] for r in graph.ages()),((20,2,23),)*3)
        self.assertFalse(graph.available(22));self.assertTrue(graph.available(23))
        ids=tuple(b.reference.id for b in bindings)
        for weights in ((1,1,1),(1,2,1)):
            out=graph.consensus(ids,weights=weights);self.assertEqual((out['mean'],out['spread'],out['member_count']),(102,4,3))
        with self.assertRaises(ContractError):graph.consensus(ids,weights=(0,0,0))
        other,_=self.official(102,observed=2,known=20,cut=20,published=20)
        mixed=ReferenceGraph((bindings[0],other),edges=((other.reference.id,ids[0]),),cut=22,published_at=23,maximum_age_ns=100)
        self.assertIsNone(mixed.consensus((ids[0],other.reference.id),weights=(1,1))['mean']);self.assertEqual(mixed.edges[0][2],2)
        refs=tuple(self.official(v,name=k)[0] for k,v in (('a',100),('b',110),('c',115)))
        ids=tuple(r.reference.id for r in refs);edges=((ids[1],ids[0]),(ids[2],ids[1]),(ids[2],ids[0]))
        g=ReferenceGraph(refs,edges=edges,cut=0,published_at=1,maximum_age_ns=100)
        self.assertEqual(tuple(e[2] for e in g.edges),(10,5,15));self.assertEqual(g.edges[0][2]+g.edges[1][2]-g.edges[2][2],0)
        restored=ReferenceGraph.restore(g.checkpoint(),refs,edges=edges,cut=0,published_at=1,maximum_age_ns=100)
        self.assertEqual(restored.checkpoint(),g.checkpoint())
        reference,_=self.official(100,observed=2,known=10,cut=10,horizon=20)
        self.assertEqual([reference_status(reference.reference,c,5) for c in (15,16,20)],['observed','stale','expired'])

    def test_MR17_graph_exact_bounds_idempotence_and_conflict(self):
        refs=tuple(self.official(v,name=str(v))[0] for v in (100,110,115,120))
        ids=tuple(r.reference.id for r in refs);edges=((ids[1],ids[0]),(ids[2],ids[1]),(ids[2],ids[0]))
        limits=ReferenceLimits(max_references=3,max_edges=3)
        kwargs=dict(edges=edges,cut=0,published_at=1,maximum_age_ns=100,limits=limits)
        self.assertEqual(len(ReferenceGraph(refs[:3],**kwargs).references),3)
        with self.assertRaises(ContractError):ReferenceGraph(refs,**kwargs)
        with self.assertRaises(ContractError):ReferenceGraph(refs[:3],**dict(kwargs,edges=edges+(edges[0],)))
        duplicate=ReferenceGraph((refs[0],refs[0]),edges=(),cut=0,published_at=1,maximum_age_ns=100,limits=limits)
        self.assertEqual(len(duplicate.references),1)
        for invalid in (True,0):
            with self.assertRaises(ContractError):ReferenceLimits(max_references=invalid)

    def bridge_fixture(self):
        from trading_research.foundations.rolls import PriceObservation,BridgePolicy,build_bridge
        from trading_research.foundations.time import Clocks,AvailabilityBasis
        prior=self.s
        current=Sources(self,instrument=replace(INSTRUMENT,raw_id='2',raw_symbol='NQ.next',definition_version='terms.next'))
        _,old_definition=prior.mapping();_,new_definition=current.mapping()
        bindings=[bind_reference_coordinate(s.instrument,d,currency='USD',currency_evidence_id='currency') for s,d in ((prior,old_definition),(current,new_definition))]
        observations=[]
        for i,(binding,price) in enumerate(zip(bindings,(100,110))):
            clocks=Clocks(18,19,'quote-clock',AvailabilityBasis.RECEIVED,received_at=19,valid_from=18,valid_until=40)
            observations.append(PriceObservation('quote'+str(i),binding.coordinate,18,clocks,F(price),True,'common-clock'))
        bridge=build_bridge(id='bridge',old=observations[0],new=observations[1],policy=BridgePolicy('policy',0,10),
            uncertainty_points=F(1,4),cut=20,completed_at=20,horizon_end=30)
        a,_=self.official(396,observed=1,known=2,cut=2)
        old_s=self.s;self.s=current
        try:b,_=self.official(452,observed=18,known=19,cut=19)
        finally:self.s=old_s
        return a,b,bindings[0],bindings[1],bridge

    def test_MR18_MR19_MR20_actual_bridge_decomposition_and_namespace(self):
        a,b,old,new,bridge=self.bridge_fixture()
        kwargs=dict(current_binding=new,prior_binding=old,bridge=bridge,cut=20,published_at=21)
        output=bridge_gap(b,a,**kwargs)
        for key,expected in GOLD['MR18']['expected'].items():self.assertEqual(output[key],F(*expected))
        for field,changed in (('provider','wrong'),('valid_until',100),('tick_size_points',F(1))):
            with self.assertRaises(ContractError):bind_reference_coordinate(replace(new.instrument,**{field:changed}),new.definition,currency='USD',currency_evidence_id='currency')
        altered=replace(new,currency='EUR')
        with self.assertRaises(IntegrityError):bridge_gap(b,a,**dict(kwargs,current_binding=altered))
        with self.assertRaises(DependencyUnavailable):bridge_gap(b,a,**dict(kwargs,cut=19,published_at=19))
        with self.assertRaises(DependencyUnavailable):bridge_gap(b,a,**dict(kwargs,cut=29,published_at=30))
        with self.assertRaises((ContractError,DependencyUnavailable)):
            bridge_gap(b,a,**dict(kwargs,bridge=replace(bridge,timing=replace(bridge.timing,actual_completion_at=22))))
        with self.assertRaises((ContractError,DependencyUnavailable)):
            bridge_gap(b,a,**dict(kwargs,bridge=replace(bridge,timing=replace(bridge.timing,horizon_end=21))))
        with self.assertRaises(ContractError):
            OfficialSettlement('display','display:v1',0,None,old.instrument,1,2,2,F(99),'display',kind='causally_adjusted_display')

    def test_MR21_reference_interpolation_and_bounded_extrapolation(self):
        a,b=self.pair()
        for fraction,expected in ((F(0),110),(F(1,2),105),(F(1),100)):
            result=interpolate_references(a,b,fraction=fraction,cut=0)
            self.assertEqual(result['target_ticks'],expected);self.assertEqual(result['formation_displacement_ticks'],10)
        for fraction,expected in ((F(-1,2),115),(F(3,2),95)):
            with self.assertRaises(ContractError):interpolate_references(a,b,fraction=fraction,cut=0)
            self.assertEqual(interpolate_references(a,b,fraction=fraction,cut=0,extrapolation=True)['target_ticks'],expected)
        a,b=self.pair(100,100)
        result=interpolate_references(a,b,fraction=F(1,2),cut=0)
        self.assertEqual((result['target_ticks'],result['direction_from_forecast'],result['direction_from_reference']),(100,0,0))

    def test_MR22_MR23_MR24_actual_completed_floor_pivots(self):
        rows=[row(str(i),at=i,price=p) for i,p in enumerate((100,120,90,105))]
        primitive,*_=self.s.primitive(rows)
        clocks=PublicationClock(10,10,11,actual_completion_at=11)
        out=floor_pivots(primitive,clocks=clocks,horizon_end=100)
        self.assertEqual(dict(out['levels']),literal.pivots(120,90,105))
        self.assertEqual(dict(out['levels']),{k:F(*v) for k,v in GOLD['MR22']['expected'].items()})
        bands=pivot_interval_bands(primitive,clocks=clocks,horizon_end=100)
        for key,source in (('daily_from_low','daily_from_low'),('daily_from_high','daily_from_high_sorted'),('P_to_R1','P_to_R1_sorted'),('P_to_S1','P_to_S1_sorted')):
            self.assertEqual(bands[key],tuple(F(*v) for v in GOLD['MR23']['expected'][source]))
        self.assertEqual(len(bands['adjacent_intervals']),10)
        bad=replace(primitive,close_ticks=99)
        with self.assertRaises((ContractError,IntegrityError)):floor_pivots(bad,clocks=clocks,horizon_end=100)
        flat,*_=self.s.primitive([row('flat',at=1,price=100)])
        result=floor_pivots(flat,clocks=clocks,horizon_end=100)
        self.assertTrue(result['degenerate']);self.assertEqual(dict(result['levels'])['P'],100)

    def test_MR25_MR26_actual_scheduled_variants_and_close_boundary(self):
        from trading_research.measurements.source_clocks import scheduled_reference_windows,SCHEDULED_OPENS
        day=date(2026,1,5)
        for source,count in (('PIN012',16),('PIN025',11),('PIN074',5)):
            windows=scheduled_reference_windows(source,day=day,zone='America/New_York',known_at=-1)
            self.assertEqual(len(windows),count);self.assertEqual(len(SCHEDULED_OPENS[source]),count)
        source=scheduled_reference_windows('PIN074',day=day,zone='America/New_York',known_at=-1,variant='source')[-1]
        corrected=scheduled_reference_windows('PIN074',day=day,zone='America/New_York',known_at=-1)[-1]
        self.assertEqual((source.duration_ns//60000000000,corrected.duration_ns//60000000000),(1321,1));self.assertNotEqual(source.version,corrected.version)
        rows=[row('first',at=14,price=102),row('next',at=15,price=99)]
        first,_,_,_=self.s.primitive(rows,start=0,end=15,cut=15,published=16)
        second,_,_,_=self.s.primitive(rows,start=15,end=16,cut=16,published=17)
        a=bind_session_reference(first,field_name='close',clocks=PublicationClock(16,16,16,actual_completion_at=16),horizon_end=100)
        b=bind_session_reference(second,field_name='close',clocks=PublicationClock(17,17,17,actual_completion_at=17),horizon_end=100)
        self.assertEqual((a.reference.value_ticks,b.reference.value_ticks),(102,99));self.assertFalse(a.reference.available(15));self.assertTrue(a.reference.available(16))
        self.assertNotEqual(a.reference.version,b.reference.version)

    def gold_gap(self, case, *,query=None,limits=ReferenceLimits()):
        x=GOLD[case]['inputs'];a,b=self.pair(F(*x['initial']),F(*x['reference']),cut=x['cut'])
        target=gap_target(a,b,cut=x['cut'],end=x['end'])
        points=tuple(ExactPoint(at,seq,F(*price),known) for at,seq,price,known in x['points'])
        cov=x.get('coverage')
        coverage=None if cov is None else ObservationWindow(x['cut'],cov['end'],cov['certified_at'],tuple(map(tuple,cov['gaps'])),cov['source_order_known'],case)
        query=x.get('query_at',max([x['end'],*(p.known_at for p in points)])) if query is None else query
        out=gap_outcome(target,points=points,coverage=coverage,query_at=query,published_at=query,limits=limits)
        return out,target,points,coverage

    def test_MR27_MR28_MR29_MR30_MR31_MR32_MR33_MR34_MR35_gap_outcomes(self):
        for case in ('MR27','MR28','MR29','MR30','MR31','MR32','MR33','MR34','MR35'):
            with self.subTest(case=case):
                out,target,points,cov=self.gold_gap(case)
                for key,expected in GOLD[case]['expected'].items():
                    if key not in dict(out.fields):continue
                    if key=='terminal_ticks' and expected is not None:expected=F(*expected)
                    elif key=='compatible_terminal_ticks':expected=tuple(F(*p) for p in expected)
                    elif isinstance(expected,list):expected=tuple(expected)
                    self.assertEqual(out[key],expected,key)
                if out['status'] in ('observed','ambiguous'):
                    alternatives=literal.gap_paths(target.initial,target.reference,tuple((p.at,p.sequence,p.price) for p in points),ordered=cov.source_order_known)
                    self.assertEqual(out['compatible_terminal_ticks'],tuple(sorted({v['terminal'] for v in alternatives})))
                    self.assertEqual(out['gap_traversed'],all(v['gap_traversed'] for v in alternatives))
                    self.assertEqual(out['gap_held'],all(v['gap_held'] for v in alternatives))
        late,*_=self.gold_gap('MR35',query=11);self.assertEqual(late['status'],'pending');self.assertIsNone(late['touched'])
        out,target,points,cov=self.gold_gap('MR34')
        with self.assertRaises(ContractError):gap_outcome(target,points=points+(ExactPoint(11,0,F(100),11),),coverage=cov,query_at=11,published_at=11)

    def test_MR29_MR33_gap_reflection_zero_direction_and_work_limits(self):
        a,b=self.pair(90,100);target=gap_target(a,b,cut=0,end=10)
        points=(ExactPoint(5,0,F(100),5),ExactPoint(8,0,F(95),8));cov=ObservationWindow(0,10,10,version='mirror')
        out=gap_outcome(target,points=points,coverage=cov,query_at=10,published_at=10)
        self.assertEqual((out['touched'],out['closed_through'],out['held_after_contact']),(True,False,False))
        a,b=self.pair(100,100);target=gap_target(a,b,cut=0,end=10,contact_mode='contact_at_cut')
        out=gap_outcome(target,points=(),coverage=cov,query_at=10,published_at=10)
        self.assertEqual((out['contact_at'],out['touched'],out['gap_held'],out['gap_traversed']),(0,True,None,None))
        accepted,*_=self.gold_gap('MR33',limits=ReferenceLimits(max_transition_work=18))
        self.assertEqual((accepted['permutations'],accepted['transition_work']),(6,18))
        with self.assertRaises(ContractError):self.gold_gap('MR33',limits=ReferenceLimits(max_transition_work=17))
        with self.assertRaises(ContractError):ReferenceLimits(max_batch=True)

    def test_MR36_correction_keeps_frozen_target_and_replay(self):
        current,_=self.pair(cut=10)
        prior,messages=self.official(100,observed=1,known=2,cut=2)
        revised=replace(messages[0],version_id='settlement:v2',revision=1,predecessor=messages[0].version_id,
                        published_at=20,received_at=20,price_ticks=F(101))
        old=gap_target(current,prior,cut=10,end=30)
        new_binding,_=self.official(101,known=20,cut=20,messages=messages+(revised,))
        new=gap_target(current,new_binding,cut=20,end=30)
        self.assertEqual((old.reference,new.reference),(100,101));self.assertNotEqual(old.version,new.version)
        book=GapOutcomeLedger();recipes=[]
        for target in (old,new):
            cov=ObservationWindow(target.cut,30,30,version='revision:'+str(target.cut))
            out=gap_outcome(target,points=(ExactPoint(25,0,F(100),25),),coverage=cov,query_at=30,published_at=30)
            book.append(out);recipes.append(out._recipe)
        restored=GapOutcomeLedger.restore(book.checkpoint(),recipes=tuple(recipes))
        self.assertEqual(restored.checkpoint(),book.checkpoint());validate_gap_target(old)
        changed=replace(old,reference=F(999));object.__setattr__(changed,'_recipe',old._recipe)
        with self.assertRaises(IntegrityError):validate_gap_target(changed)

    def test_MR37_actual_F10_early_open_correction_original_ttl(self):
        obs,view,_,_,selection=self.opening(horizon=32)
        definition=RegistryDefinition(generator_versions=(('measurement-open-v1','v1'),),ttl_ns=20)
        graph=ObjectGraph(self.s.root/'open.sqlite',definition=definition)
        first=publish_open_reference(obs,graph=graph,clocks=PublicationClock(12,12,12,actual_completion_at=12),
            generator='measurement-open-v1',generator_version='v1',object_id='o:open')
        anchor=graph.get_version(first.birth.anchors[0]);self.assertEqual((anchor.start,anchor.end),(10,10))
        self.assertEqual(graph.object_asof('o:open',12).born_at,12)
        replacement=Trade.restore(row('replacement',at=10,known=14,price=101))
        view.correct(id='opening-correction',original_id='first',known_at=14,reason='source',replacement=replacement)
        corrected=observe_open(selection,view,coverage=WindowCoverage(self.s.instrument.raw_symbol,0,100,((0,14),),14,'corrected-coverage'),
            cut=14,published_at=15,horizon_end=32)
        second=publish_open_reference(corrected,graph=graph,clocks=PublicationClock(15,15,15,actual_completion_at=15),
            generator='measurement-open-v1',generator_version='v1',object_id='o:open',previous=first)
        current=graph.object_asof('o:open',31);self.assertEqual(current.born_at,12);self.assertTrue(current.available(31,20));self.assertFalse(current.available(32,20))
        self.assertEqual((first.geometry.lower,second.geometry.lower),(100,101))
        reopened=ObjectGraph(self.s.root/'open.sqlite',definition=definition)
        self.assertEqual(reopened.object_asof('o:open',31),current)

    def test_MR38_MR39_forgery_and_opening_tie_support(self):
        obs,*_=self.opening()
        changed=replace(obs,reference=replace(obs.reference,value_ticks=F(999)));object.__setattr__(changed,'_recipe',obs._recipe)
        with self.assertRaises(IntegrityError):validate_open(changed)
        from trading_research.foundations.units import Ticks
        source=obs._recipe['view'];original=source.trades['first']
        source.trades['first']=replace(original,price=Ticks(999))
        try:
            with self.assertRaises(IntegrityError):validate_open(obs)
        finally:source.trades['first']=original
        for changed_recipe in (
            dict(obs._recipe,coverage=replace(obs._recipe['coverage'],observed_intervals=((0,5),))),
            dict(obs._recipe,aggregation_unit='different-unit'),
            dict(obs._recipe,selection=replace(obs._recipe['selection'],selected_at=12)),
            dict(obs._recipe,selection=replace(obs._recipe['selection'],instrument=replace(self.s.instrument,raw_symbol='wrong'))),
        ):
            forged=replace(obs);object.__setattr__(forged,'_recipe',changed_recipe)
            with self.assertRaises((ContractError,IntegrityError)):validate_open(forged)
        for prices,orders,expected in (((100,101),(None,None),None),((100,100),(None,None),100),((100,101),(0,1),100)):
            rows=[row(str(i),at=10,price=p,order=o) for i,(p,o) in enumerate(zip(prices,orders))]
            value,*_=self.opening(rows=rows,cut=20,published=21)
            self.assertEqual(value.reference.value_ticks,expected)
            if expected is None:self.assertEqual(value.possible_first_prices,(100,101));self.assertEqual(value.status,'ambiguous')
        rows=[row('first',at=10,price=100),row('a',at=11,price=99),row('b',at=11,price=101)]
        value,*_=self.opening(rows=rows,cut=20,published=21);self.assertEqual(value.reference.value_ticks,100)
        with self.assertRaises(ContractError):self.opening(rows=[row('unobserved',at=10,price=100)],spans=((20,40),),cut=40,published=41)

    def test_MR40_point_period_identity_and_checkpoint_capacity(self):
        limits=ReferenceLimits(max_points=2)
        out,target,points,cov=self.gold_gap('MR27',limits=limits)
        self.assertEqual(out['observed_count'],2)
        with self.assertRaises(ContractError):gap_outcome(target,points=points+(ExactPoint(9,0,F(99),9),),coverage=cov,query_at=10,published_at=10,limits=limits)
        touched=[]
        def stream():
            touched.append(True);yield points[0]
        with self.assertRaises(ContractError):gap_outcome(target,points=stream(),coverage=cov,query_at=10,published_at=10,limits=limits)
        self.assertFalse(touched)
        book=GapOutcomeLedger(limits=limits);book.append(out)
        with self.assertRaises((ContractError,IntegrityError)):
            GapOutcomeLedger.restore(book.checkpoint(),recipes=(out._recipe,),limits=replace(limits,max_points=3))
        from trading_research.measurements.reference_geometry import _name
        self.assertEqual(_name('abc',ReferenceLimits(max_identity_bytes=3)),'abc')
        with self.assertRaises(ContractError):_name('abcd',ReferenceLimits(max_identity_bytes=3))
        first=date(2026,1,1);second=first+timedelta(days=1)
        cal,observations=self.period_fixture(['closed','closed'],start_day=first,current_date=second,observed_values={})
        kwargs=dict(calendar=cal,instrument_root='NQ',period='month',observations=observations,cut=300,
                    limits=ReferenceLimits(max_period_days=2,max_identity_bytes=3))
        period=period_open(current_date=second,**kwargs);self.assertEqual(len(period['traversed']),2)
        with self.assertRaises(ContractError):period_open(current_date=second+timedelta(days=1),**kwargs)
        with self.assertRaises(ContractError):period_open(current_date=second,**dict(kwargs,instrument_root='abcd'))
        # Solve the decimal-length fixed point using primitive JSON bytes;
        # digest values retain their fixed 64-character wire width.
        raw=json.loads(book.checkpoint())
        def set_bound(value,bound):
            if type(value) is dict:return {k:bound if k=='max_bytes' else set_bound(v,bound) for k,v in value.items()}
            if type(value) is list:return [set_bound(v,bound) for v in value]
            return value
        bound=len(book.checkpoint())
        for _ in range(10):
            next_bound=len(json.dumps(set_bound(raw,bound),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
            if next_bound==bound:break
            bound=next_bound
        exact_limits=replace(limits,max_bytes=bound)
        exact=gap_outcome(**dict(out._recipe,limits=exact_limits))
        exact_book=GapOutcomeLedger(limits=exact_limits);exact_book.append(exact)
        self.assertEqual(len(exact_book.checkpoint()),bound)
        before=exact_book.checkpoint()
        with self.assertRaises(ContractError):
            tight=replace(exact_limits,max_bytes=bound-1)
            tight_out=gap_outcome(**dict(out._recipe,limits=tight))
            GapOutcomeLedger(limits=tight).append(tight_out)
        self.assertEqual(exact_book.checkpoint(),before)

    def test_MR41_all_four_actual_calendar_gap_horizons(self):
        a,b=self.pair();end=7200000000000
        _,_,selection=self.s.clock(0,end,cut=0)
        targets=gap_targets(a,b,selection=selection,cut=0)
        self.assertEqual(tuple(t.end for t in targets),tuple(GOLD['MR41']['expected']['fixed_ends']))
        self.assertEqual(len({t.version for t in targets}),4)
        outcomes=[]
        for target in targets:
            points=tuple(ExactPoint(m*60000000000,0,F(p),m*60000000000) for m,p in GOLD['MR41']['inputs']['points_minutes'] if m*60000000000 <= target.end)
            cov=ObservationWindow(0,target.end,target.end,version='horizon:'+str(target.end))
            outcomes.append(gap_outcome(target,points=points,coverage=cov,query_at=target.end,published_at=target.end))
        for key in ('gap_held','touched','gap_traversed','closed_through','held_after_contact'):
            self.assertEqual([o[key] for o in outcomes],GOLD['MR41']['expected'][key])
        self.assertEqual([o['terminal_ticks'] for o in outcomes],[F(*x) for x in GOLD['MR41']['expected']['terminal_ticks']])
        self.assertEqual([o['contact_at'] for o in outcomes],GOLD['MR41']['expected']['first_contact_at'])
