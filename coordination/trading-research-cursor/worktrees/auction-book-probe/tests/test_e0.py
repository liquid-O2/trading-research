from dataclasses import replace
from datetime import date,timedelta
from fractions import Fraction as F
import unittest

from trading_research.errors import ContractError,DependencyUnavailable
from trading_research.experiments.e0.candidates import FrozenRange,VisitTracker,numeric_features,objects,stop_distance
from trading_research.experiments.e0.cohort import DayCompleteness,REQUIRED_CHECKS,freeze_cohort,require_runnable
from trading_research.foundations.contracts import Band
from trading_research.research.labels import ObservationWindow
from trading_research.research.object_labels import ExactPoint,ObjectTarget,reference_object_label


def range_(id='range',low=100,high=140,end=10,known=11):
    return FrozenRange(id,'NQH5',0,end,known,F(low),F(high),F(low+10),F(high-10),'exact_trade_ticks','raw-range-version',True)


class E0CandidateTests(unittest.TestCase):
    def test_grid_geometry_retains_source_collisions_and_cannot_use_future_range(self):
        r=range_();prior=range_('prior',end=5,known=6);os=objects(r,prior,cut=11)
        self.assertEqual(len(os),13);self.assertEqual(len({o.id for o in os}),13)
        levels={o.type:o.price for o in os}
        self.assertEqual(levels['06_09:quarter_1'],110);self.assertEqual(levels['06_09:upper_half_extension'],160)
        self.assertEqual(levels['06_09:lower_full_extension'],60)
        self.assertEqual(sum(o.price==100 for o in os),2)
        self.assertEqual(len(objects(r,prior,cut=10)),4)
        flat=replace(r,low=F(100),high=F(100),open=F(100),close=F(100))
        self.assertEqual(len(objects(flat,prior,cut=11)),4)
        with self.assertRaises(DependencyUnavailable):objects(r,replace(prior,instrument='NQM5'),cut=11)

    def test_visits_require_observed_approach_separation_and_survive_restart(self):
        obj=objects(range_(),None,cut=11)[0];tracker=VisitTracker(maximum_gap_ns=10)
        self.assertEqual(tracker.observe(cut=12,price=F(110),candidates=(obj,)),())
        touch=tracker.observe(cut=13,price=F(101),candidates=(obj,))[0]
        self.assertEqual((touch.approach,touch.fade_side,touch.visit),(-1,1,1))
        self.assertFalse(tracker.observe(cut=14,price=F(104),candidates=(obj,)))
        self.assertFalse(tracker.observe(cut=15,price=F(100),candidates=(obj,)))
        tracker.observe(cut=16,price=F(105),candidates=(obj,))
        restored=VisitTracker.restore(tracker.checkpoint())
        a=tracker.observe(cut=17,price=F(100),candidates=(obj,));b=restored.observe(cut=17,price=F(100),candidates=(obj,))
        self.assertEqual(a,b);self.assertEqual(a[0].visit,2)

    def test_missing_observation_and_gap_crossing_do_not_invent_inward_contacts(self):
        obj=objects(range_(),None,cut=11)[0];tracker=VisitTracker(maximum_gap_ns=10)
        tracker.observe(cut=12,price=F(110),candidates=(obj,))
        self.assertFalse(tracker.observe(cut=13,price=F(90),candidates=(obj,)))
        tracker.observe(cut=14,price=None,candidates=(obj,))
        contact=tracker.observe(cut=15,price=F(100),candidates=(obj,))[0]
        self.assertIsNone(contact.approach);self.assertIsNone(contact.fade_side)
        self.assertEqual(stop_distance(F(81)),9)
        with self.assertRaises(DependencyUnavailable):stop_distance(None)

    def test_feature_windows_are_known_before_cut_and_keep_tick_variance_distinct(self):
        r=range_();prior=range_('prior',end=5,known=6);obj=objects(r,prior,cut=11)[0]
        args=dict(obj=obj,side=1,cut=11,price=F(120),range_06_09=r,prior_rth=prior,five_minute_return=F(4),thirty_minute_realized_variation=F(25),history_known_at=11,minute_of_session=30,remaining_minutes=F(300),object_type_code=0)
        f=numeric_features(**args)
        self.assertEqual(f['range_position'],.5);self.assertEqual(f['thirty_minute_realized_variation_ticks2'],25)
        with self.assertRaises(DependencyUnavailable):numeric_features(**{**args,'history_known_at':12})


class ObjectLabelTests(unittest.TestCase):
    def setUp(self):
        self.target=ObjectTarget('target','frozen-object',10,100,Band(F(99),F(101)),1,F(5),F(5),'native_bbo_midpoint')
        self.coverage=ObservationWindow(10,100,110,version='certified-fixture')
    def run_(self,points,**kwargs):
        return reference_object_label(kwargs.pop('target',self.target),initial=kwargs.pop('initial',F(110)),points=tuple(ExactPoint(t,s,F(p),t+1) for s,(t,p) in enumerate(points)),coverage=kwargs.pop('coverage',self.coverage),**kwargs)

    def test_gap_cross_has_no_touch_and_full_no_contact_is_not_censored(self):
        r=self.run_(((20,90),(50,95)))
        self.assertEqual((r['reach_status'],r['departure']),('no_contact','no_contact'));self.assertEqual(r['gap_crossings'],(20,))
        censored=self.run_(((20,90),),coverage=replace(self.coverage,end=50))
        self.assertEqual(censored['reach_status'],'censored')

    def test_late_contact_does_not_restart_fifteen_minute_equivalent_horizon(self):
        r=self.run_(((90,100),(99,103)))
        self.assertEqual((r['contact_at'],r['departure'],r['fixed_end']),(90,'unresolved',100))
        with self.assertRaises(ContractError):self.run_(((90,100),(101,110)))

    def test_exact_order_and_unknown_same_timestamp_have_different_departures(self):
        points=((20,100),(30,106),(30,94))
        exact=self.run_(points);unknown=self.run_(points,coverage=replace(self.coverage,source_order_known=False))
        self.assertEqual(exact['departure'],'favorable_first');self.assertEqual(unknown['departure'],'ambiguous')
        one_sided=self.run_(((20,100),(30,106),(30,107)),coverage=replace(self.coverage,source_order_known=False))
        self.assertEqual(one_sided['departure'],'favorable_first')

    def test_current_contact_target_and_later_frozen_revision_stay_distinct(self):
        current=replace(self.target,contact_mode='contact_at_cut')
        r=self.run_(((20,106),),target=current,initial=F(100))
        self.assertEqual((r['contact_at'],r['departure']),(10,'favorable_first'))
        changed=replace(self.target,object_version='later-object',band=Band(F(119),F(121)))
        self.assertNotEqual(self.target.version,changed.version)
        original=self.run_(((20,100),(30,106)))
        revised=self.run_(((20,100),(30,106)),target=changed)
        self.assertEqual(original['reach_status'],'contact');self.assertEqual(revised['reach_status'],'no_contact')


class CohortTests(unittest.TestCase):
    def row(self,day,**changes):
        checks=tuple((n,'satisfied','fixture-evidence') for n in sorted(REQUIRED_CHECKS))
        return DayCompleteness(day,changes.get('checks',checks),('fixture-data-hash',),changes.get('fields',('t','flags','instrument_id','schema','coverage')))

    def test_first_last_selection_is_based_on_completeness_and_logs_exclusions(self):
        days=tuple(date(2022,1,3)+timedelta(days=i) for i in range(15))
        rows=tuple(self.row(day) for day in days)
        rows=(replace(rows[0],checks=tuple((n,'missing' if n=='mbp_full_schema' else s,e) for n,s,e in rows[0].checks)),*rows[1:])
        m=freeze_cohort(rows,years=(2022,),per_end=5)
        self.assertEqual(m['dates'],tuple(d.isoformat() for d in (*days[1:6],*days[-5:])))
        self.assertEqual(m['exclusions'][0]['day'],days[0].isoformat())
        with self.assertRaises(DependencyUnavailable):require_runnable(m)
        with self.assertRaises(ContractError):self.row(days[0],fields=('realized_pnl',))

    def test_exact_reference_cannot_adopt_acquired_universe_as_complete_parent(self):
        day=self.row(date(2022,1,3));less=REQUIRED_CHECKS-{'complete_outright_universe'}
        with self.assertRaises(ContractError):freeze_cohort((day,),required_checks=less)
        diagnostic=freeze_cohort((day,),required_checks=less,scope='registered_acquired_cohort_diagnostic')
        with self.assertRaises(DependencyUnavailable):require_runnable(diagnostic)
