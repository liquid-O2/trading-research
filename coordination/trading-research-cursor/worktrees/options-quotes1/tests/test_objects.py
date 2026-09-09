from dataclasses import replace
from fractions import Fraction
from pathlib import Path
import tempfile
import unittest

from trading_research.errors import ContractError,DependencyUnavailable,IntegrityError
from trading_research.foundations.bars import CausalBar
from trading_research.foundations.contracts import Band,Geometry,InstrumentKey,MarketObject
from trading_research.foundations.objects import Lifecycle,ObjectRegistry
from trading_research.measurements.footprint import footprint,imbalance_rows,stacked_imbalances
from trading_research.measurements.structure import DirectionalChanges,DivergenceAnchor,PricePoint,divergence,pivot_reference,retracement
from tests.test_foundations import clocks
from tests.test_measurements import trade


def object_(id='poc',at=10,price=100):
    band=Band(Fraction(price),Fraction(price));geometry=Geometry(band,band,Fraction(0),Fraction(0),Fraction(1),'g','NQH5','NQH5')
    return MarketObject(id,0,'profile','fixed',InstrumentKey('q','CME','NQH5','NQH5','NQ','terms'),geometry,clocks(at),('bar',),(id+':source',),0,5,5,'eligible','unvisited','observed',('support','resistance'))


def lifecycle():
    return Lifecycle('profile','fixed',(('active','contacted'),('contacted','reclaimed'),('active','invalidated'),('invalidated','active'),('active','expired')),
                     frozenset({'active'}),frozenset({'active','contacted','reclaimed'}),False,False)


def bar(i,high,low,*,published=None,final=True,complete=True):
    start=i*10;end=start+10;at=end if published is None else published
    return CausalBar('NQH5',start,end,'bar10',0,end,end,final,low,high,low,high,2,2,0,True,complete,10,('a'+str(i),'b'+str(i)),'coverage',(),at)


class ObjectHistoryTests(unittest.TestCase):
    def test_overlap_is_relationship_and_contact_does_not_remove_usable_object(self):
        with tempfile.TemporaryDirectory() as root:
            registry=ObjectRegistry(Path(root)/'o.sqlite',lifecycles=(lifecycle(),));registry.anchor(id='bar',known_at=5,evidence_version='barbytes')
            a,b=object_(),object_('vwap')
            registry.append(a,state='active',event_id='a',reason='formed');registry.append(b,state='active',event_id='b',reason='formed')
            registry.relationship(id='overlap',at=10,left_version=a.version_id,right_version=b.version_id,kind='geometric_overlap')
            self.assertEqual(registry.freeze_candidates(id='cut10',at=10,instrument=a.instrument)['candidate_count'],2)
            contacted=replace(a,revision=1,supersedes=a.version_id,clocks=clocks(20),visit_state='contacted')
            registry.append(contacted,state='contacted',event_id='touch',reason='contact now observed')
            self.assertEqual(len(registry.asof(20,active_only=True)),2)
            self.assertEqual(registry.asof(15,active_only=True),((a,'active'),(b,'active')))
            restart=ObjectRegistry(Path(root)/'o.sqlite',lifecycles=(lifecycle(),))
            self.assertEqual(restart.asof(20),registry.asof(20));self.assertEqual(restart.asof(15),registry.asof(15))

    def test_late_invalidation_reactivation_and_expiry_keep_all_original_versions(self):
        with tempfile.TemporaryDirectory() as root:
            registry=ObjectRegistry(Path(root)/'o.sqlite',lifecycles=(lifecycle(),));registry.anchor(id='bar',known_at=5,evidence_version='bar')
            a=object_();registry.append(a,state='active',event_id='born',reason='formed')
            invalid=replace(a,revision=1,supersedes=a.version_id,clocks=clocks(20),eligibility='ineligible')
            registry.append(invalid,state='invalidated',event_id='invalid',reason='observed invalidation')
            self.assertEqual(len(registry.asof(15,active_only=True)),1);self.assertEqual(registry.asof(20,active_only=True),())
            reactivated=replace(invalid,revision=2,supersedes=invalid.version_id,clocks=clocks(30),eligibility='eligible')
            registry.append(reactivated,state='active',event_id='reactivated',reason='new version allowed by this generator')
            self.assertEqual(registry.asof(25,active_only=True),());self.assertEqual(registry.asof(30,active_only=True)[0][0],reactivated)
            registry.append(reactivated,state='active',event_id='reactivated',reason='new version allowed by this generator')
            with self.assertRaises(IntegrityError):registry.append(reactivated,state='active',event_id='reactivated',reason='changed')

    def test_orphan_future_parent_changed_geometry_and_backdated_birth_fail(self):
        with tempfile.TemporaryDirectory() as root:
            registry=ObjectRegistry(Path(root)/'o.sqlite',lifecycles=(lifecycle(),));a=object_()
            with self.assertRaises(ContractError):registry.append(a,state='active',event_id='no-parent',reason='bad')
            registry.anchor(id='bar',known_at=15,evidence_version='future')
            with self.assertRaises(ContractError):registry.append(a,state='active',event_id='future-parent',reason='bad')
            a=replace(a,clocks=clocks(20));registry.append(a,state='active',event_id='born',reason='now available')
            changed=replace(a,revision=1,supersedes=a.version_id,clocks=clocks(30),geometry=object_(price=110).geometry)
            with self.assertRaises(ContractError):registry.append(changed,state='contacted',event_id='changed',reason='frozen geometry')
            with self.assertRaises(ContractError):registry.append(replace(a,id='new',clocks=clocks(19)),state='active',event_id='backdate',reason='bad')


class StructureTests(unittest.TestCase):
    def test_pivot_is_available_after_right_bar_and_not_backplotted(self):
        bars=(bar(0,101,99),bar(1,105,100),bar(2,103,100,published=35))
        self.assertEqual(pivot_reference(bars,left=1,right=1,cut=34),())
        high=[s for s in pivot_reference(bars,left=1,right=1,cut=35) if s.side=='high'][0]
        self.assertEqual((high.extreme_start,high.extreme_end,high.confirmed_at),(10,20,35))
        self.assertEqual(pivot_reference(bars+(bar(3,120,119,published=45),),left=1,right=1,cut=35),(high,))
        self.assertEqual(pivot_reference(bars[:-1]+(replace(bars[-1],final=False),),left=1,right=1,cut=40),())

    def test_plateau_ties_gap_and_roll_are_explicit(self):
        bars=(bar(0,100,90),bar(1,105,91),bar(2,105,92),bar(3,100,93))
        self.assertFalse(any(s.side=='high' for s in pivot_reference(bars,left=1,right=1,cut=50)))
        early=[s for s in pivot_reference(bars,left=1,right=1,cut=50,ties='earliest') if s.side=='high']
        late=[s for s in pivot_reference(bars,left=1,right=1,cut=50,ties='latest') if s.side=='high']
        self.assertEqual((early[0].extreme_start,late[0].extreme_start),(10,20))
        self.assertEqual(pivot_reference((bars[0],bars[1],replace(bars[2],coverage_complete=False)),left=1,right=1,cut=50),())
        with self.assertRaises(ContractError):pivot_reference(bars+(replace(bar(4,102,100),instrument='NQM5'),),left=1,right=1,cut=60)

    def test_threshold_confirmation_prefix_restart_gap_and_same_timestamp_order(self):
        engine=DirectionalChanges(instrument='NQH5',threshold_ticks=4,definition_version='fixed4')
        points=tuple(PricePoint(str(i),'NQH5',i+1,i+1,p,i) for i,p in enumerate((100,106,110,109,106)))
        for p in points[:3]:engine.add(p)
        saved=engine.checkpoint();restored=DirectionalChanges.restore(saved)
        for obj in (engine,restored):
            self.assertEqual(obj.add(points[3]),());high=obj.add(points[4])[0]
            self.assertEqual((high.side,high.price_ticks,high.extreme_start,high.confirmed_at),('high',110,3,5))
            self.assertEqual(obj.add(points[4]),())
            obj.add(PricePoint('gap','NQH5',6,6,50,6,False));self.assertEqual(obj.add(PricePoint('after','NQH5',7,7,49,7)),())
            with self.assertRaises(DependencyUnavailable):obj.add(PricePoint('tie','NQH5',7,7,100,None))
        self.assertEqual(engine.checkpoint(),restored.checkpoint())

    def test_anchor_divergence_is_not_reversal_and_body_quarter_differs(self):
        a=DivergenceAnchor('a','NQ','d',1,5,Fraction(100),Fraction(50),'high','confirmed_close_cvd')
        b=replace(a,id='b',extreme_at=10,known_at=15,price=Fraction(105),flow=Fraction(40))
        with self.assertRaises(DependencyUnavailable):divergence(a,b,cut=14,price_scale=Fraction(5),flow_scale=Fraction(10))
        r=divergence(a,b,cut=15,price_scale=Fraction(5),flow_scale=Fraction(10))
        self.assertEqual((r['regular'],r['hidden'],r['price_change'],r['flow_change']),(True,False,1,-1))
        self.assertTrue(divergence(a,replace(b,price=Fraction(95),flow=Fraction(60)),cut=15,price_scale=Fraction(5),flow_scale=Fraction(10))['hidden'])
        with self.assertRaises(ContractError):divergence(a,replace(b,trading_date='tomorrow'),cut=15,price_scale=Fraction(5),flow_scale=Fraction(10))
        self.assertEqual(retracement(90,110,Fraction(1,4)),95)
        self.assertNotEqual(retracement(90,110,Fraction(1,4)),Fraction(3,4)*105+Fraction(1,4)*100)


class FootprintTests(unittest.TestCase):
    def test_diagonal_same_price_unknown_and_zero_opponent_rules(self):
        values=(trade(0,99,10,-1),trade(1,100,50,1),trade(2,100,30,-1),trade(3,101,1,1))
        view=footprint(values,row_ticks=1)
        same=imbalance_rows(view,ratio=Fraction(3),minimum_volume=5,comparison='same_price',zero_opponent='require_observed_opponent')
        diagonal=imbalance_rows(view,ratio=Fraction(3),minimum_volume=5,comparison='diagonal',zero_opponent='require_observed_opponent')
        self.assertFalse(same[1]['buy']['qualifying']);self.assertTrue(diagonal[1]['buy']['qualifying']);self.assertFalse(diagonal[2]['buy']['qualifying'])
        uncertain=footprint(values+(trade(4,99,100,None),),row_ticks=1)
        self.assertFalse(imbalance_rows(uncertain,ratio=Fraction(3),minimum_volume=5,comparison='diagonal',zero_opponent='require_observed_opponent')[1]['buy']['qualifying'])
        only=footprint((trade(9,100,1,1),),row_ticks=1)
        self.assertFalse(imbalance_rows(only,ratio=Fraction(3),minimum_volume=2,comparison='same_price',zero_opponent='infinite_if_minimum')[0]['buy']['qualifying'])

    def test_price_gaps_do_not_become_stacks_and_mass_survives_row_aggregation(self):
        values=tuple(trade(i,p,10,1) for i,p in enumerate((100,101,103,104)))+(trade(5,None,7,None),)
        view=footprint(values,row_ticks=1)
        rows=imbalance_rows(view,ratio=Fraction(3),minimum_volume=5,comparison='same_price',zero_opponent='infinite_if_minimum')
        self.assertEqual(stacked_imbalances(rows,side='buy',row_ticks=1,minimum_rows=3),())
        self.assertEqual(stacked_imbalances(rows,side='buy',row_ticks=1,minimum_rows=2),((100,101),(103,104)))
        coarse=footprint(values,row_ticks=2)
        self.assertEqual(view['total_volume'],47);self.assertEqual(coarse['total_volume'],47);self.assertEqual(coarse['unpriced_volume'],7)
        self.assertNotEqual(view['rows'],coarse['rows'])
