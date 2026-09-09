from dataclasses import replace
from decimal import Decimal
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import unittest

from trading_research.errors import ContractError
from trading_research.execution.costs import load_fee_scenarios
from trading_research.execution.replay import BracketPlan,InSetAction,OrderTiming,exact_static_day_oracle,reference_bracket
from trading_research.execution.venue import FillScenario,VenuePath
from trading_research.foundations.units import NQ_REFERENCE
from tests.test_venue import quote,trade


class BracketReplayTests(unittest.TestCase):
    def setUp(self):
        self.fees=load_fee_scenarios(Path(__file__).resolve().parents[1]/'configs/fee-scenarios.json')[0]
        self.scenario=FillScenario('named-synthetic',0,'venue_first','strict_trade_through','window-v1',self.fees.version)
        self.timing=OrderTiming('outbound2-report2-native0',2,2,0,'ambiguous')
        self.plan=BracketPlan('plan','NQH5',1,10,102,94,110,50,80,90,Decimal(50),'frozen-band')

    def run_(self,quotes,trades=(),**kwargs):
        path=VenuePath(instrument='NQH5',quotes=quotes,trades=trades,complete_intervals=((0,100),),coverage_version='window-v1')
        return reference_bracket(path,kwargs.pop('plan',self.plan),terms=NQ_REFERENCE,fees=self.fees,fill_scenario=self.scenario,timing=self.timing,**kwargs)

    def test_time_exit_waits_for_cancel_truth_and_keeps_original_horizon(self):
        r=self.run_((quote(),))
        self.assertEqual((r.entry.at,r.entry.price_ticks,r.exit.at,r.exit.price_ticks,r.exit_reason),(12,102,56,100,'deadline'))
        self.assertEqual(r.unprotected_interval,(52,56));self.assertEqual(r.position_known_flat_at,58)
        self.assertEqual((r.gross_usd,r.fees_usd,r.net_usd),(Decimal(-10),Decimal('5.76'),Decimal('-15.76')))
        self.assertTrue(r.boundary_met);self.assertEqual(self.plan.horizon_end,50)

    def test_target_uses_strategy_visibility_and_stop_can_win_during_cancellation(self):
        qs=(quote(),quote('target',at=20,known=30,bid=110,ask=112),quote('drop',at=31,known=40,bid=90,ask=92))
        r=self.run_(qs,(trade('stop-trade',at=31,price=92),))
        self.assertEqual((r.exit_reason,r.exit.at,r.exit.price_ticks),('stop',31,90))
        self.assertFalse(any(e['kind']=='broker_cancel_and_position_reconciled_under_scenario' for e in r.events))
        no_stop=self.run_(qs)
        self.assertEqual((no_stop.exit_reason,no_stop.exit.at,no_stop.exit.price_ticks),('target',36,90))
        self.assertLess(no_stop.net_usd,0)  # Target recognition does not guarantee a profitable eventual fill.

    def test_gap_stop_loss_overshoot_is_observed_not_clamped_to_daily_budget(self):
        r=self.run_((quote(),quote('gap',at=20,known=22,bid=1,ask=3)),(trade('trigger',at=21,price=2),),prior_day_net=Decimal(-600))
        self.assertEqual(r.exit.price_ticks,1);self.assertTrue(r.daily_loss_breach);self.assertLess(r.minimum_marked_net_usd,Decimal(-1000))
        self.assertLess(r.net_usd,Decimal(-500))

    def test_native_trigger_without_executable_book_and_cancel_tie_remain_uncertain(self):
        qs=(quote(),quote('halt',at=20,known=22,bid=90,ask=92,state='halted'))
        r=self.run_(qs,(trade('trigger',at=21,price=92),))
        self.assertIsNone(r.net_usd);self.assertFalse(r.boundary_met);self.assertEqual(r.exit.status,'uncertain')
        tie=self.run_((quote(),),(trade('trigger',at=52,price=92),))
        self.assertEqual(tie.exit_reason,'uncertain_cancel_stop_race');self.assertIsNone(tie.exit)

    def test_budget_and_boundary_are_checked_without_changing_logical_stop(self):
        with self.assertRaises(ContractError):self.run_((quote(),),prior_day_net=Decimal(-950))
        boundary=replace(self.plan,horizon_end=85,flatten_send_at=40,required_flat_at=44)
        r=self.run_((quote(),),plan=boundary)
        self.assertEqual(r.exit_reason,'boundary');self.assertEqual(r.exit.at,46);self.assertFalse(r.boundary_met)
        self.assertEqual(boundary.stop_ticks,94)

    def test_boundary_requires_known_flat_broker_state_after_the_exit_fill(self):
        plan=replace(self.plan,horizon_end=85,flatten_send_at=40,required_flat_at=47)
        r=self.run_((quote(),),plan=plan)
        self.assertEqual((r.exit.at,r.position_known_flat_at),(46,48))
        self.assertFalse(r.boundary_met)


class FiniteOracleTests(unittest.TestCase):
    def test_static_floor_and_occupancy_match_exhaustive_finite_enumeration(self):
        actions=(InSetAction('a',1,5,Fraction(100),Fraction(-20),Fraction(50)),InSetAction('b',2,8,Fraction(170),Fraction(-10),Fraction(20)),
                 InSetAction('c',6,9,Fraction(90),Fraction(-90),Fraction(90)),InSetAction('d',10,12,Fraction(50),Fraction(-30),Fraction(40)))
        budget=Fraction(100);best=Fraction(0)
        for n in range(len(actions)+1):
            for subset in combinations(actions,n):
                ordered=sorted(subset,key=lambda a:a.decision_at);net=Fraction(0);end=-1;valid=True
                for a in ordered:
                    if a.decision_at<end or a.required_reserve>budget+net or net+a.minimum_incremental_mark<=-budget:valid=False;break
                    net+=a.net;end=a.known_flat_at
                if valid:best=max(best,net)
        result=exact_static_day_oracle(actions,daily_budget=budget)
        self.assertEqual(result['best_net'],best);self.assertEqual(result['selected_actions'],('a','c','d'));self.assertFalse(result['live_attainable'])
        self.assertEqual(exact_static_day_oracle((),daily_budget=budget)['best_net'],0)

    def test_oracle_cannot_choose_two_opposing_overlapping_actions_or_an_unfunded_bracket(self):
        actions=(InSetAction('a',1,10,Fraction(30),Fraction(-10),Fraction(20)),InSetAction('b',1,10,Fraction(1000),Fraction(-500),Fraction(500)))
        r=exact_static_day_oracle(actions,daily_budget=Fraction(100));self.assertEqual(r['selected_actions'],('a',));self.assertEqual(r['best_net'],30)
