"""The registered 25 B00.6 cases and frozen concrete variants."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import json
from pathlib import Path
import unittest

from references import decision_contracts_literal as literal
from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.contracts import Target, Forecast, Capability, Band, Geometry
from trading_research.foundations.object_graph import Geometry as GraphGeometry
from trading_research.foundations.time import Clocks, AvailabilityBasis
from trading_research.foundations.units import Unit, Ticks
from trading_research.research.labels import PathPoint, ObservationWindow, reference_path_label
from trading_research.research.object_labels import ObjectTarget, ExactPoint, reference_object_label
from trading_research.execution.venue import VenueQuote, VenuePath, FillScenario
from trading_research.research.decision_contracts import (
    FeeCharge, RewardDomain, NetMark, IncrementalRewards, incremental_rewards,
    RewardState, RewardSegment, RewardComposition, compose_rewards, compare_complete_rewards,
    EvidenceSeed, EvidenceFactor, EvidenceAdmission, EvidenceLedger, admit_evidence,
)

GOLD=json.loads((Path(__file__).parent/'golden/b00_6_decision_contracts_v1.json').read_text())
CASES={c['case_id']:c for c in GOLD['cases']}


def vector(case): return CASES[case]['fixture_vector']
def domain(row=None): return RewardDomain(**(row or GOLD['common_fixture_contract']['reward_domain']))
def target(row): return Target(**{**row,'unit':Unit(row['unit']),'capabilities':frozenset(Capability(c) for c in row['capabilities'])})
def state(row): return RewardState(**{**row,'domain':domain(row['domain'])})
def segment(row): return RewardSegment(row['id'],state(row['initial']),state(row['terminal']),Fraction(row['net_increment_usd']),tuple(row['fee_ids']))
def mark(row): return NetMark(row['at'],domain(row['domain']),Fraction(row['gross_marked_usd']),tuple(FeeCharge(c['id'],Fraction(c['amount_usd'])) for c in row['charges']))


def forecast(row, offered_target):
    c=row['clocks']; clocks=Clocks(**{**c,'basis':AvailabilityBasis(c['basis'])})
    return Forecast(**{**row,'target':offered_target,'clocks':clocks,'distribution_json':row['distribution_json'].encode(),
                       'upstream_prediction_ids':tuple(row['upstream_prediction_ids']),'coverage':tuple(row['coverage'])})


def object_label(row,scale=1):
    t=row['target']; band=Band(*(Fraction(x) for x in t['band']))
    obj=ObjectTarget(t['id'],t['object_version'],t['cut']*scale,t['end']*scale,band,t['side'],
                     Fraction(t['favorable_distance']),Fraction(t['adverse_distance']),t['observation_process'],t['contact_mode'])
    c=row['coverage']; coverage=ObservationWindow(c['start']*scale,c['end']*scale,c['certified_through']*scale,
                                                  tuple((a*scale,b*scale) for a,b in c['gaps']),c['source_order_known'],c['version'])
    points=tuple(ExactPoint(p['at']*scale,p['sequence'],Fraction(p['price']),p['known_at']*scale) for p in row['points'])
    return obj,reference_object_label(obj,initial=Fraction(row['initial']),points=points,coverage=coverage)


def evidence(case):
    v=vector(case); t=target(v['target']); s=v['seed']
    seed=EvidenceSeed(t.signature,tuple(s['atoms']),s['known_at'],s['likelihood_contract'])
    return v,t,EvidenceLedger(seed,**v.get('limits',{}))


def factor(row,signature):
    return EvidenceFactor(row['id'],signature,tuple(row['atoms']),row['payload_version'],row['known_at'],row['likelihood_contract'])


def venue(case):
    v=vector(case)
    path=VenuePath(instrument=v['instrument'],quotes=tuple(VenueQuote(**q) for q in v['quotes']),trades=(),
                   complete_intervals=tuple(tuple(x) for x in v['complete_intervals']),coverage_version=v['coverage_version'],max_events=v['max_events'])
    return v,path,FillScenario(**v['scenario'])


def geometry(row):
    return Geometry(Band(*(Fraction(x) for x in row['physical_support'])),Band(*(Fraction(x) for x in row['contact_region'])),
                    Fraction(row['estimation_uncertainty']),Fraction(row['mapping_uncertainty']),Fraction(row['entry_tolerance']),
                    row['definition_id'],row['source_coordinate'],row['execution_coordinate'])


class DecisionContractsTests(unittest.TestCase):
    def test_bc01_same_marginals_different_order(self):
        v=vector('BC01'); t=target(v['target']); c=v['coverage']; coverage=ObservationWindow(**{**c,'gaps':tuple(c['gaps'])})
        actual=[]
        for rows in v['paths']:
            points=tuple(PathPoint(p['at'],p['sequence'],Ticks(int(p['price'])),p['known_at']) for p in rows)
            label=reference_path_label(t,initial=Ticks(v['initial_ticks']),points=points,coverage=coverage,up_ticks=v['up_ticks'],down_ticks=v['down_ticks'])
            values=(label.terminal_ticks,label.maximum_up_ticks,label.maximum_down_ticks,label.first_barrier)
            self.assertEqual(values,literal.path_statistics(0,[int(p['price']) for p in rows],2,1)); actual.append(values)
        self.assertEqual(actual,[(1,2,1,'upper'),(1,2,1,'lower')])

    def test_bc02_capability_masks_cannot_identify_trajectory(self):
        v=vector('BC02')
        for mask in v['offered_masks']:
            t=target({**v['target_template'],'capabilities':mask}); f=forecast(v['forecast_fields'],t)
            with self.assertRaises(DependencyUnavailable):
                f.require(t,frozenset({Capability.TRAJECTORY}),cut=v['query_cut'])
        self.assertEqual(len(v['offered_masks']),5)

    def test_bc03_expiry_population_and_process(self):
        v=vector('BC03'); t=target(v['target']); f=forecast(v['forecast_fields'],t)
        for cut in (0,9): f.require(t,frozenset({Capability.FIRST_PASSAGE}),cut=cut)
        with self.assertRaises(DependencyUnavailable): f.require(t,frozenset({Capability.FIRST_PASSAGE}),cut=10)
        for change in v['mismatched_target_variants']:
            with self.assertRaises(ContractError): f.require(replace(t,**change),frozenset({Capability.FIRST_PASSAGE}),cut=0)

    def test_bc04_fixed_end_and_new_contact_origin(self):
        rows=vector('BC04')['variants']; values=[object_label(row,60000000000) for row in rows]
        self.assertNotEqual(values[0][0].version,values[1][0].version)
        for row,(t,label) in zip(rows,values):
            self.assertEqual(label['fixed_end'],row['expected']['fixed_end']*60000000000)
            self.assertEqual(label['departure'],row['expected']['departure'])
            self.assertEqual(label['contact_at'],row['expected']['contact_at']*60000000000)
            for key in ('contact_price','maximum_favorable_ticks','maximum_adverse_ticks'):
                self.assertEqual(label[key],Fraction(row['expected'][key]))
            hit=row['expected'].get('first_barrier_at')
            self.assertEqual(label['first_barrier_at'],None if hit is None else hit*60000000000)
            independent=literal.fixed_contact(Fraction(row['initial']),[(p['at'],Fraction(p['price'])) for p in row['points']],
                cut=row['target']['cut'],end=row['target']['end'],band=(99,101),favorable=3,adverse=3,contact_at_cut=row['target']['contact_mode']=='contact_at_cut')
            self.assertEqual(label['departure'],independent[2])
        contact=next(p for p in rows[0]['points'] if p['at']==9)
        self.assertEqual(contact['known_at'],9)
        self.assertTrue(all(p['at']>9 for p in rows[1]['points']))
        prefix=deepcopy(rows[1]); prefix['target']['end']=10
        prefix['points']=prefix['points'][:1]; prefix['coverage']['end']=10
        _,unresolved=object_label(prefix,60000000000)
        self.assertEqual(unresolved['departure'],'unresolved')
        self.assertEqual(literal.fixed_contact(Fraction(100),[(10,Fraction(101))],
            cut=9,end=10,band=(99,101),favorable=3,adverse=3,contact_at_cut=True)[2],'unresolved')

    def test_bc05_no_contact_versus_censor(self):
        v=vector('BC05'); labels=[]
        for variant in v['variants']:
            row={**variant,'target':v['target'],'initial':v['initial']}; _,label=object_label(row); labels.append(label)
            self.assertEqual(label['reach_status'],variant['expected_reach_status'])
        self.assertEqual([r['departure'] for r in labels],['no_contact','censored'])
        self.assertEqual(labels[0]['target_version'],labels[1]['target_version'])

    def test_bc06_jump_does_not_manufacture_contact(self):
        _,result=object_label(vector('BC06'))
        self.assertEqual(result['gap_crossings'],(2,)); self.assertEqual(result['reach_status'],'no_contact')
        self.assertIsNone(result['contact_at'])

    def test_bc07_reward_telescope_and_preexisting_fees(self):
        v=vector('BC07'); marks=tuple(mark(m) for m in v['marks']); result=incremental_rewards(marks)
        self.assertEqual(result.net_marks,tuple(Fraction(x) for x in CASES['BC07']['expected']['net_marks']))
        self.assertEqual((result.increments,result.net_change,result.cumulative_charged_fees,result.interval_new_fees),
                         ((Fraction(-5),Fraction(25),Fraction(80),Fraction(-5)),Fraction(95),Fraction(10),Fraction(10)))
        independent=literal.net_marks([(m.at,m.gross_marked_usd,[(f.id,f.amount_usd) for f in m.charges]) for m in marks])
        self.assertEqual(independent,(result.net_marks,result.increments,result.net_change,result.cumulative_charged_fees,result.interval_new_fees))
        baseline=incremental_rewards(tuple(mark(m) for m in v['fee_baseline_variant']['marks']))
        self.assertEqual((baseline.net_marks,baseline.increments,baseline.cumulative_charged_fees,baseline.interval_new_fees),
                         ((Fraction(-5),Fraction(5)),(Fraction(10),),Fraction(5),Fraction(0)))
        self.assertEqual(baseline.net_change,Fraction(v['fee_baseline_variant']['expected']['net_change']))

    def test_bc08_complete_common_boundary_comparison(self):
        v=vector('BC08'); left=compose_rewards(tuple(segment(s) for s in v['left'])); right=compose_rewards(tuple(segment(s) for s in v['right']))
        self.assertEqual((left.net_increment_usd,right.net_increment_usd,compare_complete_rewards(left,right)),(110,100,10))
        self.assertEqual(literal.compose([(s.initial.record(),s.terminal.record(),s.net_increment_usd,s.fee_ids) for s in left.segments]),110)

    def test_bc09_overlap_and_explicit_wait(self):
        v=vector('BC09'); macro=segment(v['macro'])
        for row in v['invalid_continuations']:
            with self.assertRaises(ContractError): compose_rewards((macro,segment(row)))
        explicit=compose_rewards(tuple(segment(row) for row in v['explicit_wait_variant']))
        self.assertEqual(explicit.net_increment_usd,170)

    def test_bc10_exact_pending_state_and_terminal_eligibility(self):
        v=vector('BC10')
        with self.assertRaises(ContractError): compose_rewards((segment(v['macro']),segment(v['mismatched_continuation'])))
        other=compose_rewards(tuple(segment(s) for s in v['comparison_other']))
        for row in v['terminal_boundary_variants']:
            with self.assertRaises(DependencyUnavailable): compare_complete_rewards(compose_rewards((segment(row),)),other)

    def test_bc11_fee_retry_and_conflicting_history(self):
        v=vector('BC11'); m=mark(v['duplicate_mark']); self.assertEqual(len(m.charges),1); self.assertEqual(m.net_marked_usd,-5)
        with self.assertRaises(ContractError): replace(m,charges=m.charges+(FeeCharge('f1',Fraction(6)),))
        with self.assertRaises(ContractError): incremental_rewards(tuple(mark(row) for row in v['lost_fee_marks']))
        with self.assertRaises(ContractError): compose_rewards(tuple(segment(row) for row in v['overlapping_segment_fees']))

    def test_bc12_domain_and_boundary_are_not_interchangeable(self):
        v=vector('BC12')
        with self.assertRaises(ContractError): segment(v['beyond_boundary'])
        baseline=tuple(segment(s) for s in v['baseline_segments'])
        marks=tuple(mark(m) for m in vector('BC07')['marks'])
        for change in v['domain_mismatch_variants']:
            changed=replace(baseline[1].domain,**change)
            altered=replace(baseline[1],initial=replace(baseline[1].initial,domain=changed),terminal=replace(baseline[1].terminal,domain=changed))
            with self.assertRaises(ContractError): compose_rewards((baseline[0],altered))
            with self.assertRaises(ContractError): incremental_rewards((marks[0],replace(marks[1],domain=changed)))

    def test_bc13_nonfill_has_no_foregone_winner_cash_charge(self):
        result=incremental_rewards(tuple(mark(m) for m in vector('BC13')['marks']))
        self.assertEqual((result.increments,result.net_change,result.cumulative_charged_fees),((Fraction(0),),0,0))

    def test_bc14_standing_venue_quote_at_arrival(self):
        v,path,scenario=venue('BC14'); q,_=path.quote_at(v['decision_cut'],clock='strategy')
        fill=path.marketable(order_id=v['order_id'],side=v['side'],arrival_at=v['arrival_at'],scenario=scenario)
        self.assertEqual((q.ask,fill.price_ticks,fill.at,fill.source_event_id),(100,102,5,'q4'))
        raw=[(q['id'],q['event_at'],q['known_at'],q['bid'],q['ask']) for q in v['quotes']]
        self.assertEqual(literal.standing_ask(raw,5),fill.price_ticks)

    def test_bc15_same_time_ordering_remains_explicit(self):
        v,path,scenario=venue('BC15'); prices=[]; statuses=[]
        for change in v['scenario_variants']:
            fill=path.marketable(order_id=v['order_id'],side=1,arrival_at=4,scenario=replace(scenario,**change))
            prices.append(fill.price_ticks); statuses.append(fill.status)
        self.assertEqual(prices,[100,102,None]); self.assertEqual(statuses,['filled_under_scenario','filled_under_scenario','uncertain'])

    def test_bc16_gap_does_not_certify_old_standing_quote(self):
        v,path,scenario=venue('BC16'); fill=path.marketable(order_id=v['order_id'],side=1,arrival_at=5,scenario=scenario)
        self.assertEqual(fill.status,'uncertain'); self.assertIsNone(fill.price_ticks)
        raw=[(q['id'],q['event_at'],q['known_at'],q['bid'],q['ask']) for q in v['quotes']]
        self.assertIsNone(literal.standing_ask(raw,5,coverage=((0,3),(5,20))))

    def test_bc17_physical_contact_and_scenario_geometry(self):
        v=vector('BC17'); g=geometry(v['geometry']); scenario=replace(g,contact_region=Band(Fraction(97),Fraction(103)))
        self.assertFalse(g.physical_support.contains(Fraction(103))); self.assertFalse(g.contact_region.contains(Fraction(103)))
        self.assertTrue(scenario.contact_region.contains(Fraction(103))); self.assertNotEqual(g.target_geometry_id,scenario.target_geometry_id)

    def test_bc18_contact_identity_is_distinct_from_full_geometry_version(self):
        v=vector('BC18'); g=geometry(v['geometry']); changed=replace(g,**{k:Fraction(x) for k,x in v['metadata_changes'].items()})
        self.assertEqual(g.target_geometry_id,changed.target_geometry_id)
        self.assertNotEqual(g.target_geometry_id,replace(g,**v['coordinate_changes']).target_geometry_id)
        full=GraphGeometry(Fraction(99),Fraction(101),Fraction(99),Fraction(101),'contact-definition-v1','raw-mini-v1-ticks','raw-mini-v1-ticks',Fraction(2),Fraction(3),Fraction(1))
        self.assertNotEqual(full.version,replace(full,estimation_uncertainty=Fraction(4),mapping_uncertainty=Fraction(5),entry_tolerance=Fraction(2)).version)

    def test_bc19_duplicate_admission_cannot_shrink_variance(self):
        v,t,ledger=evidence('BC19'); outcomes=[]
        for row in v['factors']:
            ledger,outcome=admit_evidence(ledger,factor(row,t.signature),cut=v['cut']); outcomes.append(outcome)
        self.assertEqual(outcomes,['accepted','duplicate']); self.assertEqual(ledger.consumed_atoms,('flow1',)); self.assertEqual(len(ledger.accepted_factors),1)
        self.assertEqual(literal.normal_posterior(0,1,[(1,1) for _ in ledger.accepted_factors]),(Fraction(1,2),Fraction(1,2)))
        raw=[(r['id'],tuple(r['atoms']),r['payload_version']) for r in v['factors']]
        self.assertEqual(literal.admission((),raw),(tuple(outcomes),ledger.consumed_atoms))

    def test_bc20_seeded_wrapper_redundancy_retains_id_binding(self):
        v,t,ledger=evidence('BC20'); outcomes=[]
        for row in v['factors']:
            ledger,outcome=admit_evidence(ledger,factor(row,t.signature),cut=v['cut']); outcomes.append(outcome)
        self.assertEqual(outcomes,['redundant_evidence','duplicate']); self.assertEqual(len(ledger.seen_factors),1); self.assertEqual(ledger.accepted_factors,())
        self.assertEqual(literal.normal_posterior(Fraction(1,2),Fraction(1,2),[(1,1) for _ in ledger.accepted_factors]),(Fraction(1,2),Fraction(1,2)))
        before=ledger.record()
        with self.assertRaises(ContractError): admit_evidence(ledger,factor(v['conflicting_redundant_id_retry'],t.signature),cut=5)
        self.assertEqual(ledger.record(),before)

    def test_bc21_partial_overlap_cannot_be_deleted_from_joint_factor(self):
        v,t,ledger=evidence('BC21'); before=ledger.record()
        with self.assertRaises(DependencyUnavailable): admit_evidence(ledger,factor(v['factor'],t.signature),cut=v['cut'])
        self.assertEqual(ledger.record(),before)

    def test_bc22_changed_payload_or_actual_target_rejects(self):
        v,t,ledger=evidence('BC22'); ledger,_=admit_evidence(ledger,factor(v['factors'][0],t.signature),cut=v['cut']); before=ledger.record()
        with self.assertRaises(ContractError): admit_evidence(ledger,factor(v['factors'][1],t.signature),cut=v['cut'])
        changed=target(v['changed_target_constructor']); self.assertNotEqual(changed.signature,t.signature)
        with self.assertRaises(ContractError): admit_evidence(ledger,replace(ledger.accepted_factors[0],target_signature=changed.signature),cut=v['cut'])
        self.assertEqual(ledger.record(),before)

    def test_bc23_future_seed_factor_and_ledger_cuts(self):
        v,t,ledger=evidence('BC23')
        with self.assertRaises(DependencyUnavailable): admit_evidence(ledger,factor(v['factor'],t.signature),cut=5)
        future=v['future_seed_variant']; seed=EvidenceSeed(t.signature,tuple(future['seed']['atoms']),6,future['seed']['likelihood_contract'])
        with self.assertRaises(DependencyUnavailable): admit_evidence(EvidenceLedger(seed),factor(future['factor'],t.signature),cut=5)
        back=v['backdated_ledger_variant']; later,_=admit_evidence(ledger,factor(back['admit_factor'],t.signature),cut=5)
        with self.assertRaises(DependencyUnavailable): admit_evidence(later,factor(back['next_factor'],t.signature),cut=4)
        self.assertEqual(ledger.known_at,0)

    def test_bc24_distinct_ids_do_not_prove_independence(self):
        v,t,ledger=evidence('BC24')
        with self.assertRaises(DependencyUnavailable): admit_evidence(ledger,factor(v['factor'],t.signature),cut=v['cut'])
        self.assertEqual(ledger.consumed_atoms,('flow1',))

    def test_bc25_strict_restore_resume_bounds_and_prefix(self):
        v=vector('BC25'); r=v['restore_ledger']; t=target(r['target']); s=r['seed']
        seed=EvidenceSeed(t.signature,tuple(s['atoms']),s['known_at'],s['likelihood_contract'])
        initial=EvidenceLedger(seed); f=factor(r['factor'],t.signature)
        ledger,_=admit_evidence(initial,f,cut=5); record=ledger.record(); old_version=ledger.version
        restore=lambda row,**kw: EvidenceLedger.from_record(row,expected_target_signature=kw.pop('expected_target_signature',t.signature),
            expected_likelihood_contract=kw.pop('expected_likelihood_contract',seed.likelihood_contract),**kw)
        restored=restore(record); duplicate,status=admit_evidence(restored,f,cut=5)
        self.assertEqual(status,'duplicate'); self.assertEqual(restored.version,old_version); self.assertEqual(duplicate.record(),record)
        second=replace(f,id='flow2',atoms=('flow2',),payload_version='y=2;noise=1',known_at=6)
        resumed,_=admit_evidence(restored,second,cut=6); uninterrupted,_=admit_evidence(ledger,second,cut=6)
        self.assertEqual(resumed.record(),uninterrupted.record()); self.assertEqual(ledger.record(),record); self.assertEqual(ledger.version,old_version)
        rewards=v['restore_rewards']; prefix=compose_rewards(tuple(segment(x) for x in rewards['prefix'])); suffix=tuple(segment(x) for x in rewards['suffix'])
        old_reward=prefix.record(); restored_reward=RewardComposition.from_record(old_reward)
        joined=compose_rewards(restored_reward.segments+suffix)
        self.assertEqual(joined,compose_rewards(prefix.segments+suffix)); self.assertEqual(joined.net_increment_usd,110)
        self.assertEqual(prefix.record(),old_reward); self.assertEqual(prefix.version,restored_reward.version)
        marks=tuple(mark(x) for x in vector('BC07')['marks']); increments=incremental_rewards(marks)
        self.assertEqual(IncrementalRewards.from_record(increments.record()),increments)
        for value in (FeeCharge('fee',Fraction(5)),domain(),marks[0],prefix.initial,prefix.segments[0],seed,f,ledger.seen_factors[0]):
            self.assertEqual(type(value).from_record(value.record()),value)
        changed_target=target(r['changed_expected_target_constructor'])
        with self.assertRaises(ContractError): restore(record,expected_target_signature=changed_target.signature)
        with self.assertRaises(ContractError): restore(record,expected_likelihood_contract='different-likelihood')
        for change in ({'max_factors':63},{'max_atoms':255}):
            with self.assertRaises(ContractError): restore(record,**change)
        for change in ({'max_segments':63},{'max_fee_ids':255}):
            with self.assertRaises(ContractError): RewardComposition.from_record(old_reward,**change)
        corrupt=[]
        bad=deepcopy(record); bad['schema']='other'; corrupt.append(bad)
        bad=deepcopy(record); bad['extra']=0; corrupt.append(bad)
        for derived in ('consumed_atoms','accepted_factors'):
            bad=deepcopy(record); bad['fields'][derived]=[]; corrupt.append(bad)
        bad=deepcopy(record); bad['fields']['seen_factors']*=2; corrupt.append(bad)
        bad=deepcopy(record); bad['fields']['known_at']=4; corrupt.append(bad)
        bad=deepcopy(record); bad['fields']['known_at']=True; corrupt.append(bad)
        bad=deepcopy(record); bad['fields']['seen_factors'][0]['fields']['factor']['fields']['known_at']=6; corrupt.append(bad)
        bad=deepcopy(record); bad['fields']['seen_factors'][0]['fields']['factor']['fields']['target_signature']=changed_target.signature; corrupt.append(bad)
        bad=deepcopy(record); bad['fields']['seen_factors'][0]['fields']['factor']['fields']['likelihood_contract']='other'; corrupt.append(bad)
        redundant_seed=replace(seed,atoms=('flow1',)); redundant,_=admit_evidence(EvidenceLedger(redundant_seed),f,cut=5)
        bad=redundant.record(); bad['fields']['seen_factors'][0]['fields']['outcome']='accepted'; corrupt.append(bad)
        for bad in corrupt:
            with self.assertRaises(ContractError): restore(bad)
        for rational in ([2,2],[1,0],[True,1]):
            bad=FeeCharge('f',Fraction(1)).record(); bad['fields']['amount_usd']=rational
            with self.assertRaises(ContractError): FeeCharge.from_record(bad)
        for suffix_change in (replace(suffix[0],fee_ids=prefix.segments[0].fee_ids),
                              replace(suffix[0],initial=replace(suffix[0].initial,state_version='changed'))):
            bad=deepcopy(old_reward); bad['fields']['segments'].append(suffix_change.record())
            with self.assertRaises(ContractError): RewardComposition.from_record(bad)
        for key,value in (('account_id','other-account'),('raw_definition_id','other-raw'),
                          ('scenario_id','other-scenario'),('common_boundary',21)):
            bad=deepcopy(old_reward)
            bad['fields']['segments'][0]['fields']['terminal']['fields']['domain']['fields'][key]=value
            with self.assertRaises(ContractError):
                RewardComposition.from_record(bad)
        bounded=replace(domain(),common_boundary=1000)
        many_marks=tuple(NetMark(i,bounded,Fraction(0),()) for i in range(65))
        self.assertEqual(incremental_rewards(many_marks[:64]).net_change,0)
        with self.assertRaises(ContractError): incremental_rewards(many_marks)
        states=tuple(RewardState(i,bounded,'flat'+str(i),0,False) for i in range(66))
        segments=tuple(RewardSegment('s'+str(i),states[i],states[i+1],Fraction(0),()) for i in range(65))
        self.assertEqual(len(compose_rewards(segments[:64]).segments),64)
        with self.assertRaises(ContractError): compose_rewards(segments)
        full=EvidenceLedger(replace(seed,atoms=('shared',)))
        for i in range(64):
            full,outcome=admit_evidence(full,replace(f,id='r'+str(i),atoms=('shared',)),cut=1)
            self.assertEqual(outcome,'redundant_evidence')
        self.assertEqual(len(full.seen_factors),64); before=full.record()
        with self.assertRaises(ContractError): admit_evidence(full,replace(f,id='r64',atoms=('shared',)),cut=1)
        self.assertEqual(full.record(),before)
        all_atoms=tuple('a'+str(i) for i in range(256)); admitted,_=admit_evidence(initial,replace(f,atoms=all_atoms),cut=1)
        self.assertEqual(len(admitted.consumed_atoms),256)
        with self.assertRaises(ContractError): admit_evidence(initial,replace(f,atoms=all_atoms+('a256',)),cut=1)
        fees=tuple(FeeCharge('fee'+str(i),Fraction(0)) for i in range(257))
        self.assertEqual(len(NetMark(0,bounded,Fraction(0),fees[:256]).charges),256)
        with self.assertRaises(ContractError): NetMark(0,bounded,Fraction(0),fees)
        self.assertEqual(len(compose_rewards((replace(segments[0],fee_ids=tuple(f.id for f in fees[:256])),)).fee_ids),256)
        with self.assertRaises(ContractError): compose_rewards((replace(segments[0],fee_ids=tuple(f.id for f in fees)),))
        first255=replace(f,id='union-first',atoms=all_atoms[:255])
        union,_=admit_evidence(initial,first255,cut=1); union_before=union.record()
        with self.assertRaises(ContractError):
            admit_evidence(union,replace(f,id='union-next',atoms=('last-one','last-two')),cut=1)
        self.assertEqual(union.record(),union_before)
        pair=(replace(segments[0],fee_ids=tuple(f.id for f in fees[:128])),
              replace(segments[1],fee_ids=tuple(f.id for f in fees[128:])))
        pair_before=tuple(value.record() for value in pair)
        with self.assertRaises(ContractError):
            compose_rewards(pair)
        self.assertEqual(tuple(value.record() for value in pair),pair_before)
        repeated=FeeCharge('single-fee',Fraction(1))
        at_limit=NetMark(0,bounded,Fraction(0),(repeated,)*4096)
        self.assertEqual(at_limit.charges,(repeated,))
        before=at_limit.record()
        with self.assertRaises(ContractError):
            NetMark(0,bounded,Fraction(0),(repeated,)*4097)
        self.assertEqual(at_limit.record(),before)
        small_marks=incremental_rewards(tuple(NetMark(i,bounded,Fraction(0),(),max_fee_ids=1) for i in (0,1)),max_marks=2,max_fee_ids=1)
        small_segments=compose_rewards(segments[:1],max_segments=1,max_fee_ids=1)
        small_ledger=EvidenceLedger(replace(seed,atoms=()),max_factors=1,max_atoms=1)
        for limits in ({'max_marks':True,'max_fee_ids':1},{'max_marks':2.0,'max_fee_ids':1},
                       {'max_marks':2,'max_fee_ids':True},{'max_marks':2,'max_fee_ids':1.0}):
            with self.assertRaises(ContractError):
                IncrementalRewards.from_record(small_marks.record(),**limits)
        for bad in (True,1.0):
            for limits in ({'max_segments':bad,'max_fee_ids':1},{'max_segments':1,'max_fee_ids':bad}):
                with self.assertRaises(ContractError):
                    RewardComposition.from_record(small_segments.record(),**limits)
            for limits in ({'max_factors':bad,'max_atoms':1},{'max_factors':1,'max_atoms':bad}):
                with self.assertRaises(ContractError):
                    restore(small_ledger.record(),**limits)
        for invalid_limit in (0,-1,True,65):
            with self.assertRaises(ContractError): incremental_rewards(many_marks[:2],max_marks=invalid_limit)
        self.assertEqual(initial.seen_factors,()); self.assertEqual(initial.known_at,0)
