"""Registered finite F08 fixtures. Synthetic clocks are not market latency data."""
from copy import copy, deepcopy
from dataclasses import FrozenInstanceError, replace
from datetime import date
from decimal import Decimal
from fractions import Fraction as F
import json
from pathlib import Path
import tempfile
import unittest

from references import rolls_literal as literal
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.calendar import Session
from trading_research.foundations.contracts import InstrumentKey
from trading_research.foundations.instruments import InstrumentDefinition, instrument_identity
from trading_research.foundations.rolls import (
    ContractUniverse, SessionVolume, SessionSequence, RawCoordinate, RollPolicy,
    ContractMap, PublicationTiming, select_prior_volume, select_roll, PriceObservation,
    BridgePolicy, build_bridge, CoordinateState, transition_state, RollLedger,
    RollLimits, coordinate_change, tick_distance, require_executable_level,
    require_raw_contract_parity, CorporateAction, apply_action, require_option_underlying,
    require_raw_option_coordinate, RawFill, raw_fill_pnl, RollMapping)
from trading_research.foundations.time import Clocks, AvailabilityBasis
from trading_research.operations.journal import Journal

G = json.loads((Path(__file__).parent / 'golden/f08-transitions.json').read_text())


def clock(at, source='receipt', **kwargs):
    return Clocks(None, at, source, AvailabilityBasis.RECEIVED, received_at=at, **kwargs)


def definition(identity, expiry):
    return InstrumentDefinition(InstrumentKey('test', 'venue', identity, identity.upper(), 'NQ',
        'def-'+identity, expiry), clock(10, 'def-'+identity, valid_from=0, valid_until=2000),
        'future', Decimal(20), Decimal('.25'))


class RollTransitionTests(unittest.TestCase):
    def setUp(self):
        self.definitions = (definition('old', 1000), definition('new', 1200))
        self.old, self.new = tuple(RawCoordinate.from_definition(d, currency='USD', currency_evidence_id='fixture-currency') for d in self.definitions)
        self.universe = ContractUniverse('universe', 'NQ', 111, ('old', 'new'),
            'synthetic_complete_parent_fixture', 'universe-v1', 'test', 'venue',
            tuple((d.key.instrument_id, instrument_identity(d)) for d in self.definitions))
        previous = Session('previous', date(2025, 1, 1), 'NQ', 120, 150, (), 0, 80,
                           'previous-row', 'tz-v1', True, 'synthetic fixture')
        current = Session('current', date(2025, 1, 2), 'NQ', 180, 300, (), 0, 80,
                          'current-row', 'tz-v1', True, 'synthetic fixture')
        self.calendar = SessionSequence('calendar', 'NQ', (previous, current), 160, 'calendar-v1', True)
        self.volumes = tuple(SessionVolume(d.key.instrument_id, 'previous', 120, 150, 160,
            count, True, d.key.instrument_id+'-v1', instrument_identity(d))
            for d, count in zip(self.definitions, (10, 20)))
        self.policy = RollPolicy('previous-volume-v1', 'preceding_volume')
        self.old_quote = PriceObservation('old-quote', self.old, 100, clock(105, 'old-q'), F(100), True, 'synthetic')
        self.new_quote = PriceObservation('new-quote', self.new, 101, clock(105, 'new-q'), F(110), True, 'synthetic')
        self.bridge_policy = BridgePolicy('bounded-pair', 2, 10)
        self.bridge = self.make_bridge()
        self.source = CoordinateState('source', self.old, 'level', (F(101),), (), clock(104, 'level'),
            ('parent-row',), 110, exposure_lineage=('exposure',), cost_lineage=('cost',))
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def ledger(self, name='ledger', **kwargs):
        return RollLedger(Journal(Path(self.tmp.name) / (name+'.sqlite')), **kwargs)

    def select(self, **kwargs):
        args = dict(id='decision', policy=self.policy, universe=self.universe, definitions=self.definitions,
            currency='USD', currency_evidence_id='fixture-currency', cut=200, completed_at=202, horizon_end=250, volumes=self.volumes, session_sequence=self.calendar)
        args.update(kwargs)
        return select_roll(**args)

    def make_bridge(self, **kwargs):
        args = dict(id='bridge', old=self.old_quote, new=self.new_quote, policy=self.bridge_policy,
                    uncertainty_points=F(1, 8), cut=105, completed_at=105, horizon_end=500)
        args.update(kwargs)
        return build_bridge(**args)

    def transition(self, **kwargs):
        args = dict(id='transition', source=self.source, destination=self.new, mode='translate',
                    cut=105, completed_at=107, horizon_end=110, reason='declared roll', bridge=self.bridge)
        args.update(kwargs)
        return transition_state(**args)

    def test_missing_competitor_blocks_declared_fixture_without_certifying_parent(self):
        self.assertEqual(self.select().universe.coverage_scope, G['selection']['universe']['scope'])
        self.assertFalse(G['scope']['exact_e0_parent_evidence_satisfied'])
        for volumes in (self.volumes[:1], (self.volumes[0], replace(self.volumes[1], complete=False))):
            with self.subTest(volumes=volumes), self.assertRaises(DependencyUnavailable):
                self.select(volumes=volumes)

    def test_prior_volume_ties_future_suffix_and_literal_oracle(self):
        decision = self.select()
        self.assertEqual(decision.coordinate.instrument_id, G['selection']['selected'])
        tie = (self.volumes[0], replace(self.volumes[1], contracts=10))
        self.assertEqual(self.select(volumes=tie).coordinate.instrument_id, G['selection']['equal_volume_selected'])
        future = replace(self.volumes[0], contracts=100000, known_at=201, source_version='future')
        self.assertEqual(self.select(volumes=(*self.volumes, future)).coordinate, decision.coordinate)
        oracle = literal.select_volume(('old', 'new'),
            ({'id':'old','known_at':10,'expiry':1000}, {'id':'new','known_at':10,'expiry':1200}),
            tuple({'id':r.instrument_id,'known_at':r.known_at,'contracts':r.contracts,
                   'complete':r.complete,'interval':(120,150),'receipt_id':r.source_version,'source_version':r.source_version} for r in self.volumes),
            cut=200, previous_interval=(120,150))
        self.assertEqual(oracle['selected'], decision.coordinate.instrument_id)
        self.assertEqual(decision.operations, 2+oracle['volume_rows_examined'])

    def test_selection_publication_preserves_input_cut_completion(self):
        result = self.select()
        self.assertEqual((result.timing.input_known_at, result.timing.decision_cut, result.known_at), (160,200,202))
        self.assertFalse(result.available(201)); self.assertTrue(result.available(202))
        scalar = select_prior_volume(universe=self.universe, definitions=self.definitions, volumes=self.volumes,
            previous_session_id='previous', cut=200, session_sequence=self.calendar)
        self.assertFalse(scalar['published']); self.assertEqual(scalar['input_known_at'],160)
        self.assertNotIn('known_at', scalar)
        with self.assertRaises(ContractError): self.select(completed_at=199)
        with self.assertRaises(DependencyUnavailable): self.select(horizon_end=202)

    def test_calendar_predecessor_and_interval_are_required(self):
        with self.assertRaises(ContractError): self.select(volumes=(self.volumes[0],replace(self.volumes[1],session_start=121)))
        with self.assertRaises(DependencyUnavailable): self.select(session_sequence=replace(self.calendar, complete=False))
        with self.assertRaises(DependencyUnavailable): self.select(volumes=tuple(replace(v,session_id='current') for v in self.volumes))
        with self.assertRaises(ContractError):
            select_prior_volume(universe=self.universe, definitions=self.definitions, volumes=self.volumes,
                previous_session_id='week-old', cut=200, session_sequence=self.calendar)

    def test_namespace_lifetime_collisions_do_not_share_volume(self):
        collision = replace(self.definitions[0], key=replace(self.definitions[0].key, provider='other'))
        with self.assertRaises(ContractError): self.select(definitions=(*self.definitions,collision))
        with self.assertRaises(ContractError): self.select(definitions=(collision,self.definitions[1]))
        with self.assertRaises(ContractError): self.select(volumes=(replace(self.volumes[0],instrument_lifetime='wrong'),self.volumes[1]))
        with self.assertRaises(ContractError): self.bridge.translate(F(101),coordinate=replace(self.old,lifetime='other'),at=105)

    def test_immutable_exact_inputs_and_same_value_new_lineage(self):
        with self.assertRaises(ContractError): replace(self.universe,contract_ids=['old','new'])
        with self.assertRaises(ContractError): replace(self.universe,known_at=True)
        with self.assertRaises(ContractError): replace(self.volumes[0],complete='false')
        with self.assertRaises(ContractError): replace(self.old_quote,price=100.0)
        with self.assertRaises(FrozenInstanceError): self.universe.id='mutated'
        revised = self.select(volumes=(self.volumes[0],replace(self.volumes[1],source_version='same-value-new-source')))
        original = self.select()
        self.assertEqual(revised.coordinate,original.coordinate)
        self.assertNotEqual(revised.version,original.version)
        self.assertEqual(original.volume_evidence,self.volumes)

    def test_book_trade_bar_parity_requires_published_exact_contract(self):
        chosen = self.select()
        self.assertEqual(require_raw_contract_parity(chosen,book=self.new,trades=self.new,bars=self.new,at=202),chosen.version)
        with self.assertRaises(ContractError): require_raw_contract_parity(chosen,book=self.old,trades=self.new,bars=self.new,at=202)
        with self.assertRaises(DependencyUnavailable): require_raw_contract_parity(chosen,book=self.new,trades=self.new,bars=self.new,at=201)

    def test_expired_competitor_does_not_require_later_volume(self):
        expired = replace(self.definitions[0],key=replace(self.definitions[0].key,expiry_at=150))
        definitions = (expired,self.definitions[1])
        universe = replace(self.universe,lifetimes=tuple((d.key.instrument_id,instrument_identity(d)) for d in definitions))
        chosen = self.select(definitions=definitions,universe=universe,volumes=self.volumes[1:])
        self.assertEqual(chosen.coordinate.instrument_id,'new')
        self.assertFalse(chosen.definition_evidence[0][4])

    def test_fixed_provider_and_volume_rules_are_distinct_and_causal(self):
        results = [self.select()]
        for name in ('fixed_calendar','provider_map'):
            policy = RollPolicy(name+'-v1',name)
            mapping = ContractMap(name+'-map',policy,self.universe.version,self.old,180,300,clock(170,name))
            future = replace(mapping,id=name+'-revision',coordinate=self.new,clocks=clock(201,name+'-later'))
            result = self.select(policy=policy,maps=(mapping,future))
            self.assertEqual(result.coordinate.instrument_id,'old')
            self.assertEqual(result.source_map,mapping)
            results.append(result)
        self.assertEqual(len({r.version for r in results}),3)

    def test_bridge_missing_ineligible_async_future_and_clock_domain(self):
        self.assertEqual(self.bridge.observation_interval,(100,101))
        for kwargs in ({'new':None}, {'new':replace(self.new_quote,eligible=False)},
                       {'new':replace(self.new_quote,observed_at=103)},
                       {'new':replace(self.new_quote,clock_domain='unreconciled')},
                       {'new':replace(self.new_quote,clocks=clock(106,'future'))}):
            with self.subTest(kwargs=kwargs), self.assertRaises((DependencyUnavailable,ContractError)):
                self.make_bridge(**kwargs)

    def test_bridge_age_boundary_and_legacy_no_indefinite_reuse(self):
        for at,expected in ((104,False),(105,True),(110,True),(111,False)):
            self.assertEqual(self.bridge.available(at),expected)
        with self.assertRaises(DependencyUnavailable): self.bridge.translate(F(101),coordinate=self.old,at=111)
        legacy = RollMapping('legacy','old','new',100,101,105,F(100),F(110),2,F(1,2),'pair')
        self.assertEqual(legacy.translate(F(101),cut=105,source_instrument='old')['raw_destination_price'],111)
        with self.assertRaises(DependencyUnavailable): legacy.translate(F(101),cut=106,source_instrument='old')

    def test_genuine_gap_and_independent_bridge_arithmetic(self):
        moved = self.bridge.translate(F(101),coordinate=self.old,at=105)
        reference = literal.bridge(F(101),F(113),F(100),F(110))
        self.assertEqual(moved,F(*G['bridge']['translated_level']))
        self.assertEqual(coordinate_change(moved,F(113)),F(*G['bridge']['point_change']))
        self.assertEqual(reference['translated'],moved)
        self.assertEqual(reference['point_change'],F(2))

    def test_bridge_revision_restart_and_prefix_suffix_invariance(self):
        prefix = self.ledger('prefix'); prefix.append(self.bridge)
        full = self.ledger('full'); full.append(self.bridge)
        revised = self.make_bridge(id='revision',new=replace(self.new_quote,id='revised-quote',price=F(112),clocks=clock(108,'revision')),cut=108,completed_at=108)
        full.append(revised)
        self.assertEqual(full.bridge_at(self.old,self.new,at=107).version,prefix.bridge_at(self.old,self.new,at=107).version)
        self.assertEqual(full.bridge_at(self.old,self.new,at=107).translate(F(101),coordinate=self.old,at=107),111)
        self.assertEqual(full.bridge_at(self.old,self.new,at=108).translate(F(101),coordinate=self.old,at=108),113)
        self.assertEqual(self.ledger('full').bridge_at(self.old,self.new,at=107).version,self.bridge.version)

    def test_explicit_reset_has_parent_lineage_and_no_usable_values(self):
        reset = self.transition(mode='reset',bridge=None,reason='missing overlap')
        self.assertFalse(reset.destination.active); self.assertEqual(reset.destination.values,())
        self.assertIn(self.source.version,reset.destination.lineage)
        self.assertFalse(reset.destination.available(107))
        with self.assertRaises(DependencyUnavailable): self.transition(bridge=None)

    def test_translation_preserves_lineage_uncertainty_and_original_horizon(self):
        result = self.transition()
        self.assertEqual(result.destination.values,(F(111),))
        self.assertEqual(result.destination.uncertainty_points,F(1,8))
        self.assertEqual(result.destination.exposure_lineage,('exposure',))
        self.assertEqual(result.destination.cost_lineage,('cost',))
        self.assertIn(self.source.version,result.destination.lineage)
        self.assertIn(self.bridge.version,result.destination.lineage)
        self.assertEqual((result.timing.input_known_at,result.timing.decision_cut,result.known_at,result.destination.horizon_end),(105,105,107,110))
        self.assertFalse(result.destination.available(106)); self.assertTrue(result.destination.available(107)); self.assertFalse(result.destination.available(110))
        with self.assertRaises(DependencyUnavailable): self.transition(completed_at=110)

    def test_committed_transition_retry_conflict_and_double_translation(self):
        ledger = self.ledger(); ledger.append(self.source); ledger.append(self.bridge)
        result = self.transition(); self.assertTrue(ledger.append(result)); self.assertFalse(ledger.append(result))
        with self.assertRaises(IntegrityError): ledger.append(replace(result,reason='conflict'))
        with self.assertRaises(ContractError): ledger.append(self.transition(id='second'))
        with self.assertRaises(ContractError): self.transition(source=result.destination,cut=107,completed_at=108)
        relabelled = replace(result.destination,coordinate=self.old,id='relabelled')
        with self.assertRaises(ContractError): ledger.append(relabelled)
        self.assertIsNotNone(ledger.state(self.source.version,at=106))
        self.assertIsNone(ledger.state(self.source.version,at=107))
        self.assertEqual(ledger.state(result.destination.version,at=107),result.destination)

    def test_profile_mass_translation_and_mixed_coordinate_guard(self):
        source = replace(self.source,kind='profile',values=(F(99),F(101)),masses=(2,3))
        result = self.transition(source=source)
        reference = literal.profile(((F(99),2),(F(101),3)),spread=F(10))
        self.assertEqual(tuple(zip(result.destination.values,result.destination.masses)),reference['nodes'])
        self.assertEqual(sum(result.destination.masses),G['profile']['destination_mass'])
        self.assertEqual(result.operations,reference['additions'])
        with self.assertRaises(ContractError): self.transition(source=replace(source,coordinate=self.new))

    def test_different_tick_grids_remain_exact_and_offgrid_cannot_execute(self):
        new = replace(self.new,tick_size=F(1,2))
        bridge = self.make_bridge(new=replace(self.new_quote,coordinate=new))
        result = self.transition(source=replace(self.source,values=(F(397,4),)),destination=new,bridge=bridge)
        self.assertEqual(tick_distance(F(2),self.old,new),F(1))
        self.assertEqual(result.destination.values,(F(437,4),))
        self.assertFalse(result.destination.on_grid)
        with self.assertRaises(ContractError): require_executable_level(result.destination,at=107)

    def test_negative_zero_prices_and_explicit_return_domains(self):
        for old,new,previous,current,expected in ((-5,-2,-4,1,2),(0,3,0,4,1)):
            bridge = self.make_bridge(old=replace(self.old_quote,price=F(old)),new=replace(self.new_quote,price=F(new)))
            translated = bridge.translate(F(previous),coordinate=self.old,at=105)
            self.assertEqual(coordinate_change(translated,F(current)),F(expected))
            self.assertEqual(literal.bridge(F(previous),F(current),F(old),F(new))['point_change'],F(expected))
        with self.assertRaises(ContractError): coordinate_change(F(0),F(1),kind='simple')
        with self.assertRaises(ContractError): coordinate_change(F(-1),F(1),kind='log')
        self.assertEqual(coordinate_change(F(2),F(3),kind='simple'),F(1,2))

    def split_fixture(self):
        action = CorporateAction('split-v1','split',self.old,'split',100,clock(90,'announcement'),F(1,4))
        observation = PriceObservation('pre-split',self.old,80,clock(90,'raw-equity'),F(400),True,'synthetic')
        return action,observation

    def test_split_effect_receipt_result_publication_and_raw_quantity(self):
        action,observation = self.split_fixture()
        args = dict(id='adjusted',action=action,observations=(observation,),cut=100,completed_at=102,horizon_end=200,quantity=F(4))
        result = apply_action(**args)
        self.assertEqual(dict(result.values),literal.split(F(400),F(4),F(1,4)))
        self.assertEqual((result.value('price'),result.value('quantity'),result.value('notional')),(100,16,1600))
        self.assertFalse(result.available(101)); self.assertTrue(result.available(102))
        self.assertEqual((result.timing.input_known_at,result.known_at),(90,102))
        self.assertEqual(observation.price,400)
        for changed in ({'cut':99},{'action':replace(action,clocks=clock(110,'late'))}):
            with self.assertRaises(DependencyUnavailable): apply_action(**{**args,**changed})
        with self.assertRaises(ContractError): apply_action(**{**args,'observations':(result,)})
        with self.assertRaises(ContractError): replace(action,factor=0.25)

    def test_dividend_cash_and_raw_option_coordinate_remain_distinct(self):
        action = CorporateAction('dividend','dividend',self.old,'dividend',100,clock(90,'dividend'),cash_per_share=F(2))
        previous = PriceObservation('pre',self.old,90,clock(90,'pre'),F(100),True,'synthetic')
        ex = PriceObservation('ex',self.old,100,clock(100,'ex'),F(98),True,'synthetic')
        result = apply_action(id='cash-change',action=action,observations=(previous,ex),cut=100,completed_at=102,horizon_end=200)
        self.assertEqual(dict(result.values),literal.dividend(F(100),F(98),F(2)))
        self.assertEqual((result.value('raw_point_change'),result.value('total_return_cash_change')),(-2,0))
        self.assertEqual(result.coordinate,'total_return_cash_change')
        self.assertEqual(require_option_underlying(ex,expected=self.old,at=100),ex.version)
        with self.assertRaises(ContractError): require_option_underlying(result,expected=self.old,at=102)
        with self.assertRaises(DependencyUnavailable): require_option_underlying(ex,expected=self.new,at=102)
        with self.assertRaises(ContractError): require_raw_option_coordinate(result.coordinate,'raw')

    def test_action_revision_preserves_prior_result_after_restart(self):
        action,observation = self.split_fixture()
        revised = replace(action,id='split-v2',factor=F(1,2),clocks=clock(110,'correction'),supersedes=action.version)
        ledger = self.ledger(); ledger.append(action); ledger.append(revised)
        self.assertEqual(ledger.action_at('split',at=100),action)
        self.assertEqual(self.ledger().action_at('split',at=110),revised)
        with self.assertRaises(ContractError): self.ledger('orphan').append(revised)

    def test_declared_scale_carries_and_absolute_state_translates_or_resets(self):
        scale = replace(self.source,kind='point_scale',values=(F(2),))
        self.assertEqual(self.transition(source=scale,mode='carry').destination.values,(F(2),))
        self.assertEqual(self.transition(source=replace(self.source,values=(F(100),))).destination.values,(F(110),))
        with self.assertRaises(ContractError): self.transition(mode='carry')
        with self.assertRaises(ContractError): replace(scale,kind='arbitrary-indicator')
        with self.assertRaises(ContractError): self.transition(source=scale)

    def test_actual_raw_legs_determine_cash_after_display_change(self):
        legs = ((RawFill('old-entry',self.old,F(100),1,1,100,F(2)),RawFill('old-exit',self.old,F(101),-1,1,101,F(2))),
                (RawFill('new-entry',self.new,F(111),1,1,102,F(2)),RawFill('new-exit',self.new,F(113),-1,1,103,F(2))))
        result = raw_fill_pnl(legs)
        reference = literal.fills(((F(100),F(101),1,1),(F(111),F(113),1,1)),F(20),F(2),currency='USD')
        self.assertEqual({k:result[k] for k in ('gross','fees','net','currency')},reference)
        self.assertEqual((result['gross'],result['fees'],result['net']),(60,8,52))
        self.bridge.translate(F(101),coordinate=self.old,at=105)
        self.assertEqual(raw_fill_pnl(legs),result)
        with self.assertRaises(ContractError): raw_fill_pnl(((legs[0][0],legs[1][1]),))

    def test_restart_uncommitted_result_configuration_and_content_corruption(self):
        ledger = self.ledger(); ledger.append(self.source); ledger.append(self.bridge)
        result = self.transition()
        self.assertIsNone(self.ledger().state(result.destination.version,at=107))
        ledger.append(result)
        restored = self.ledger()
        self.assertEqual(restored.state(result.destination.version,at=107).version,result.destination.version)
        self.assertIsNone(restored.record(result.id,at=106))
        self.assertEqual(restored.record(result.id,at=107).version,result.version)
        with self.assertRaises(IntegrityError): self.ledger(limits=RollLimits(max_records=100))
        payload = dict(ledger.journal.read()[-1]['payload']); payload['version']='tampered'
        ledger.journal.append(key='tampered-record',kind='f08_record',payload=payload)
        with self.assertRaises(IntegrityError): self.ledger()

    def test_retained_record_bytes_profile_and_chain_bounds_are_atomic(self):
        ledger = self.ledger(limits=RollLimits(max_records=1)); ledger.append(self.source)
        before = ledger.metrics()
        with self.assertRaises(ContractError): ledger.append(self.bridge)
        self.assertEqual(ledger.metrics(),before)
        tiny = self.ledger('tiny',limits=RollLimits(max_bytes=1))
        with self.assertRaises(ContractError): tiny.append(self.source)
        self.assertEqual(tiny.metrics()['retained_records'],0)
        profile = replace(self.source,kind='profile',values=(F(99),F(101)),masses=(2,3))
        with self.assertRaises(ContractError): self.transition(source=profile,limits=RollLimits(max_profile_nodes=1))
        with self.assertRaises(ContractError): self.transition(source=replace(self.source,chain=('previous-transition',)),limits=RollLimits(max_chain=1))
        action,observation = self.split_fixture()
        short = self.ledger('short',limits=RollLimits(max_chain=1)); short.append(action)
        with self.assertRaises(ContractError): short.append(replace(action,id='revision',clocks=clock(110),supersedes=action.version))


    def test_input_validity_cannot_restart_at_derived_completion(self):
        expired = replace(self.source, clocks=clock(104, 'finite-state', valid_until=106))
        with self.assertRaises(DependencyUnavailable): self.transition(source=expired)
        valid = replace(self.source, clocks=clock(104, 'finite-state', valid_until=109))
        result = self.transition(source=valid)
        self.assertEqual(result.destination.clocks.valid_until, 109)
        self.assertTrue(result.destination.available(108)); self.assertFalse(result.destination.available(109))
        policy = RollPolicy('fixed-validity', 'fixed_calendar')
        mapping = ContractMap('finite-map', policy, self.universe.version, self.old, 180, 300,
                              clock(170, 'map', valid_until=201))
        with self.assertRaises(DependencyUnavailable): self.select(policy=policy, maps=(mapping,))
        action, observation = self.split_fixture()
        for changed_action, changed_observation in (
            (replace(action, clocks=clock(90, 'finite-action', valid_until=101)), observation),
            (action, replace(observation, clocks=clock(90, 'finite-price', valid_until=101)))):
            with self.assertRaises(DependencyUnavailable):
                apply_action(id='expired', action=changed_action, observations=(changed_observation,),
                             cut=100, completed_at=102, horizon_end=200)
        historical = replace(observation, clocks=clock(90, 'historical', valid_from=0, valid_until=95))
        self.assertTrue(historical.historical_available(100)); self.assertFalse(historical.available(100))

    def test_selection_reconstructs_winner_timing_and_roundtrips(self):
        result = self.select()
        with self.assertRaises(IntegrityError): replace(result, coordinate=self.old)
        with self.assertRaises(ContractError): replace(result, timing=PublicationTiming(0,1,1,250))
        ledger = self.ledger(); ledger.append(result)
        self.assertEqual(self.ledger().record(result.id, at=202), result)
        self.assertIsNone(self.ledger().record(result.id, at=201))
        forged = copy(result); object.__setattr__(forged, 'coordinate', self.old)
        with self.assertRaises(IntegrityError): self.ledger('forged-selection').append(forged)
        payload = deepcopy(ledger.journal.read()[-1]['payload'])
        payload['record']['fields']['coordinate']['fields']['instrument_id'] = 'old'
        corrupt = self.ledger('corrupt-selection')
        corrupt.journal.append(key='forged-selection', kind='f08_record', payload=payload)
        with self.assertRaises(IntegrityError): self.ledger('corrupt-selection')

    def test_adjustment_reconstructs_arithmetic_inputs_and_roundtrips(self):
        action, observation = self.split_fixture()
        result = apply_action(id='split-result', action=action, observations=(observation,),
                              cut=100, completed_at=102, horizon_end=200, quantity=F(4))
        for changes in ({'values': (('price',F(999)),)}, {'quantity': F(8)},
                        {'coordinate': 'raw'}, {'timing': PublicationTiming(0,1,1,200)}):
            with self.subTest(changes=changes), self.assertRaises(ContractError): replace(result, **changes)
        ledger = self.ledger(); ledger.append(action); ledger.append(result)
        self.assertEqual(self.ledger().record(result.id, at=102), result)
        self.assertIsNone(self.ledger().record(result.id, at=101))
        forged = copy(result); object.__setattr__(forged, 'quantity', F(8))
        rejected = self.ledger('forged-adjustment'); rejected.append(action)
        with self.assertRaises(IntegrityError): rejected.append(forged)
        payload = deepcopy(ledger.journal.read()[-1]['payload'])
        payload['record']['fields']['quantity'] = {'fraction': [8, 1]}
        corrupt = self.ledger('corrupt-adjustment'); corrupt.append(action)
        corrupt.journal.append(key='forged-adjustment', kind='f08_record', payload=payload)
        with self.assertRaises(IntegrityError): self.ledger('corrupt-adjustment')

    def test_nested_destination_identity_resists_cleared_chain_and_preexisting_collision(self):
        result = self.transition()
        ledger = self.ledger(); ledger.append(self.source); ledger.append(self.bridge); ledger.append(result)
        forged = replace(result.destination, chain=(), coordinate=self.old)
        with self.assertRaises(IntegrityError): ledger.append(forged)
        with self.assertRaises(IntegrityError): self.ledger().append(forged)
        other = self.ledger('preexisting'); other.append(self.source); other.append(self.bridge)
        other.append(replace(self.source, id=result.destination.id))
        with self.assertRaises(IntegrityError): other.append(result)

    def test_live_availability_obeys_coordinate_and_action_validity(self):
        finite = replace(self.old, valid_until=108)
        state = replace(self.source, coordinate=finite)
        self.assertTrue(state.available(107)); self.assertFalse(state.available(108))
        quote = replace(self.old_quote, coordinate=finite)
        with self.assertRaises(DependencyUnavailable): require_option_underlying(quote, expected=finite, at=108)
        future = replace(self.old, valid_from=106)
        self.assertFalse(replace(self.source, coordinate=future).available(105))
        action, observation = self.split_fixture()
        action = replace(action, clocks=clock(90, 'finite-action', valid_until=110))
        ledger = self.ledger(); ledger.append(action)
        self.assertEqual(ledger.action_at('split', at=109), action)
        self.assertIsNone(ledger.action_at('split', at=110))

    def test_coordinate_expiry_limits_selection_and_actual_fills(self):
        self.assertEqual(self.old.valid_until, 1000)
        with self.assertRaises(ContractError): RawFill('expired', self.old, F(100), 1, 1, 1000, F(2))
        policy = RollPolicy('long-map', 'fixed_calendar')
        mapping = ContractMap('long-map', policy, self.universe.version, self.old, 180, 1500, clock(170))
        selection = self.select(policy=policy, maps=(mapping,), horizon_end=1500)
        self.assertEqual(selection.timing.horizon_end, 1000)
        self.assertFalse(selection.available(1000))
        with self.assertRaises(DependencyUnavailable): self.select(policy=policy, maps=(mapping,), horizon_end=1500, completed_at=1000)

    def test_cash_currency_is_explicit_and_cannot_mix(self):
        with self.assertRaises(TypeError): RawCoordinate.from_definition(self.definitions[0])
        eur = RawCoordinate.from_definition(self.definitions[1], currency='EUR', currency_evidence_id='euro-terms')
        def leg(prefix, coordinate):
            return (RawFill(prefix+'-in',coordinate,F(100),1,1,100,F(2)),
                    RawFill(prefix+'-out',coordinate,F(101),-1,1,101,F(2)))
        self.assertEqual(raw_fill_pnl((leg('usd',self.old),))['currency'], 'USD')
        with self.assertRaises(ContractError): raw_fill_pnl((leg('usd',self.old),leg('eur',eur)))

    def test_literal_and_selector_agree_on_receipt_redelivery_and_conflict(self):
        definitions = ({'id':'old','known_at':10,'expiry':1000}, {'id':'new','known_at':10,'expiry':1200})
        def oracle(rows):
            primitive = tuple({'id':r.instrument_id,'known_at':r.known_at,'contracts':r.contracts,
                'complete':r.complete,'interval':(r.session_start,r.session_end),
                'receipt_id':r.source_version,'source_version':r.source_version} for r in rows)
            return literal.select_volume(('old','new'), definitions, primitive, cut=200, previous_interval=(120,150))
        duplicate = (*self.volumes, self.volumes[1])
        self.assertEqual(self.select(volumes=duplicate).coordinate.instrument_id, oracle(duplicate)['selected'])
        conflict = (*self.volumes, replace(self.volumes[1], contracts=21))
        with self.assertRaises(DependencyUnavailable): oracle(conflict)
        with self.assertRaises(DependencyUnavailable): self.select(volumes=conflict)

    def test_logical_actions_reject_disconnected_roots_assets_and_forks(self):
        action, observation = self.split_fixture()
        ledger = self.ledger(); ledger.append(action)
        for invalid in (replace(action,id='other-root',clocks=clock(110)),
                        replace(action,id='other-asset',asset=self.new,clocks=clock(110),supersedes=action.version)):
            with self.assertRaises(ContractError): ledger.append(invalid)
        revision = replace(action,id='revision',clocks=clock(110),supersedes=action.version)
        ledger.append(revision)
        fork = replace(action,id='fork',clocks=clock(120),supersedes=action.version)
        with self.assertRaises(ContractError): self.ledger().append(fork)
        self.assertEqual(self.ledger().action_at('split',at=120),revision)


if __name__ == '__main__':
    unittest.main()
