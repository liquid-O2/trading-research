from dataclasses import replace
from decimal import Decimal
from fractions import Fraction
import unittest

from trading_research.data.definitions import ProductTermsEvidence,futures_definition
from trading_research.errors import ContractError,DependencyUnavailable,IntegrityError
from trading_research.foundations.rolls import ContractUniverse,EquityAdjustment,RollMapping,SessionVolume,require_raw_option_coordinate,roll_adjusted_change,select_prior_volume
from trading_research.foundations.units import Ticks


def raw_definition(id=1,expiry=1000):
    return {'instrument_class':'F','raw_symbol':'NQH5','instrument_id':id,'security_update_action':'A',
            'activation':1,'expiration':expiry,'ts_recv':100,'t':90,'min_price_increment':.25,'contract_multiplier':None,'unused_field':b'preserved'}


def definition(id=1,expiry=1000):
    terms=ProductTermsEvidence('NQ',Decimal(20),Decimal('.25'),50,'synthetic-known-terms',('https://example.test/product',),'verified_historical_terms')
    return futures_definition(raw_definition(id,expiry),root='NQ',source_id=f'row-{id}',source_version='raw-hash',latency_ns=10,latency_scenario='synthetic-10ns',external_terms=terms)


class DefinitionTests(unittest.TestCase):
    def test_missing_multiplier_preserves_raw_flow_but_blocks_execution(self):
        d=futures_definition(raw_definition(),root='NQ',source_id='row-1',source_version='h',latency_ns=10,latency_scenario='synthetic')
        self.assertIsNone(d.multiplier);self.assertTrue(d.eligibility('raw_flow')[0]);self.assertFalse(d.eligibility('execution')[0])
        self.assertEqual((d.clocks.event_at,d.clocks.provider_received_at,d.clocks.known_at),(90,100,110))
        self.assertEqual(definition().futures_terms().pnl(Ticks(0),Ticks(1),side=1).value,Decimal(5))

    def test_external_terms_must_be_available_match_raw_terms_and_preserve_unused_field_identity(self):
        terms=ProductTermsEvidence('NQ',Decimal(20),Decimal('.25'),111,'known-terms',('https://example.test',),'published_product_reference')
        kwargs=dict(root='NQ',source_id='row',source_version='hash',latency_ns=10,latency_scenario='synthetic')
        with self.assertRaises(DependencyUnavailable):futures_definition(raw_definition(),external_terms=terms,**kwargs)
        with self.assertRaises(IntegrityError):futures_definition({**raw_definition(),'contract_multiplier':50},external_terms=replace(terms,known_at=50),**kwargs)
        a=futures_definition(raw_definition(),**kwargs);b=futures_definition({**raw_definition(),'unused_field':b'different'},**kwargs)
        self.assertNotEqual(a.key.definition_version,b.key.definition_version)

    def test_spreads_deletions_sentinels_and_bad_clocks_are_explicitly_unavailable(self):
        kwargs=dict(root='NQ',source_id='row',source_version='hash',latency_ns=10,latency_scenario='synthetic')
        for change in ({'raw_symbol':'NQH5-NQM5'},{'security_update_action':'D'},{'expiration':2**64-1},{'ts_recv':None},{'instrument_class':'S'}):
            with self.subTest(change=change),self.assertRaises(DependencyUnavailable):futures_definition({**raw_definition(),**change},**kwargs)


class RollTests(unittest.TestCase):
    def setUp(self):
        self.universe=ContractUniverse('u','NQ',111,('1','2'),'acquired_outright_cohort','universe-source')
        self.definitions=(definition(1,1000),definition(2,1200))
        self.volumes=(SessionVolume('1','previous',120,150,160,10,True,'v1'),SessionVolume('2','previous',120,150,160,20,True,'v2'))

    def select(self,**kwargs):
        return select_prior_volume(universe=kwargs.pop('universe',self.universe),definitions=kwargs.pop('definitions',self.definitions),volumes=kwargs.pop('volumes',self.volumes),previous_session_id='previous',cut=200,**kwargs)

    def test_previous_volume_ties_and_universe_scope_are_frozen_at_cut(self):
        self.assertEqual(self.select()['instrument_id'],'2')
        self.assertEqual(self.select()['universe_scope'],'acquired_outright_cohort')
        tie=(self.volumes[0],replace(self.volumes[1],contracts=10))
        self.assertEqual(self.select(volumes=tie)['instrument_id'],'1')
        future=replace(self.volumes[0],contracts=100000,known_at=201)
        self.assertEqual(self.select(volumes=(*self.volumes,future))['instrument_id'],'2')

    def test_missing_competitor_duplicate_definitions_and_mismatched_sessions_cannot_select(self):
        with self.assertRaises(DependencyUnavailable):self.select(volumes=self.volumes[:1])
        with self.assertRaises(ContractError):self.select(definitions=(*self.definitions,self.definitions[0]))
        with self.assertRaises(ContractError):self.select(volumes=(self.volumes[0],replace(self.volumes[1],session_start=121)))
        with self.assertRaises(DependencyUnavailable):self.select(universe=replace(self.universe,known_at=201))
        with self.assertRaises(DependencyUnavailable):self.select(volumes=(self.volumes[0],replace(self.volumes[1],complete=False)))

    def test_expired_outright_is_excluded_without_requiring_nonexistent_later_volume(self):
        result=self.select(definitions=(definition(1,150),self.definitions[1]),volumes=self.volumes[1:])
        self.assertEqual(result['instrument_id'],'2');self.assertIn('1',result['excluded'])

    def test_roll_gap_is_removed_only_with_known_raw_contract_spread_mapping(self):
        m=RollMapping('roll','old','new',100,101,105,Fraction(100),Fraction(110),2,Fraction(1,2),'pair-evidence')
        self.assertEqual(roll_adjusted_change(previous_old_price=Fraction(101),current_new_price=Fraction(113),mapping=m,cut=105),2)
        with self.assertRaises(DependencyUnavailable):m.translate(Fraction(101),cut=104,source_instrument='old')
        with self.assertRaises(DependencyUnavailable):replace(m,new_quote_at=103)
        self.assertEqual(m.translate(Fraction(101),cut=105,source_instrument='old')['mapping_uncertainty'],Fraction(1,2))

    def test_future_split_does_not_rewrite_features_or_option_strike_coordinates(self):
        split=EquityAdjustment('split','asset',100,90,Fraction(1,4),'announcement')
        with self.assertRaises(DependencyUnavailable):split.apply(Fraction(400),cut=99)
        self.assertEqual(split.apply(Fraction(400),cut=100)['price'],100)
        require_raw_option_coordinate('raw','raw')
        with self.assertRaises(ContractError):require_raw_option_coordinate('causally_adjusted_display','raw')
