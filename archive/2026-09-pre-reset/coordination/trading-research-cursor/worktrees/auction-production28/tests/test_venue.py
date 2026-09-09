from dataclasses import replace
from fractions import Fraction
import unittest

from trading_research.errors import ContractError
from trading_research.execution.venue import CoupledPassiveFills,FillScenario,VenuePath,VenueQuote,VenueTrade,shortfall


def quote(id='q1',at=1,known=2,bid=100,ask=102,seq=0,**kwargs):
    return VenueQuote(id,'NQH5',at,known,seq,bid,ask,kwargs.get('bid_size',5),kwargs.get('ask_size',5),kwargs.get('valid',True),kwargs.get('state','continuous'),'raw:'+id)


def trade(id='t1',at=5,price=99,size=1,side=-1):
    return VenueTrade(id,'NQH5',at,0,price,size,side,'raw:'+id)


def path(quotes=None,trades=(),intervals=((0,100),)):
    return VenuePath(instrument='NQH5',quotes=(quote(),) if quotes is None else quotes,trades=trades,complete_intervals=intervals,coverage_version='window-v1')


def scenario(**kwargs):return FillScenario('scenario',kwargs.get('impact',1),kwargs.get('ordering','ambiguous'),kwargs.get('passive','strict_trade_through'),'window-v1','verified-fees')


class VenueClockTests(unittest.TestCase):
    def test_unchanged_standing_quote_fills_at_arrival_without_waiting_for_another_update(self):
        tape=path();fill=tape.marketable(order_id='buy',side=1,arrival_at=50,scenario=scenario())
        self.assertEqual((fill.at,fill.price_ticks,fill.source_event_id),(50,103,'q1'))
        self.assertEqual(tape.marketable(order_id='sell',side=-1,arrival_at=50,scenario=scenario()).price_ticks,99)
        self.assertEqual(tape.marketable(order_id='late',side=1,arrival_at=100,scenario=scenario()).status,'uncertain')

    def test_unseen_venue_update_affects_fill_but_cannot_change_strategy_information(self):
        old=quote();new=quote('q2',at=10,known=30,bid=110,ask=112)
        tape=path((old,new))
        self.assertEqual(tape.quote_at(20,clock='strategy')[0],old)
        fill=tape.marketable(order_id='buy',side=1,arrival_at=20,scenario=scenario(impact=0))
        self.assertEqual(fill.price_ticks,112);self.assertEqual(fill.source_event_id,'q2')
        prefix=path((old,));self.assertEqual(prefix.quote_at(20,clock='strategy'),tape.quote_at(20,clock='strategy'))

    def test_same_time_arrival_uncertainty_missing_depth_gap_and_auction_are_not_clean_fills(self):
        new=quote('q2',at=10,known=10,bid=105,ask=107)
        tape=path((quote(),new))
        self.assertEqual(tape.marketable(order_id='tie',side=1,arrival_at=10,scenario=scenario()).status,'uncertain')
        self.assertEqual(tape.marketable(order_id='early',side=1,arrival_at=10,scenario=scenario(ordering='order_first')).price_ticks,103)
        self.assertEqual(tape.marketable(order_id='late',side=1,arrival_at=10,scenario=scenario(ordering='venue_first')).price_ticks,108)
        for bad in (replace(new,ask_size=0),replace(new,book_valid=False),replace(new,market_state='auction'),replace(new,bid=108)):
            self.assertEqual(path((quote(),bad)).marketable(order_id='bad',side=1,arrival_at=20,scenario=scenario()).status,'uncertain')
        unordered=path((quote('a',at=10,known=10,seq=None),quote('b',at=10,known=10,ask=104,seq=None)))
        self.assertIsNone(unordered.quote_at(20,clock='strategy')[0])

    def test_missing_interval_cannot_be_filled_by_old_standing_quote(self):
        tape=path(intervals=((0,10),(20,30)))
        self.assertFalse(tape.covered(5,25));self.assertFalse(tape.covered(15))
        self.assertEqual(tape.marketable(order_id='gap',side=1,arrival_at=15,scenario=scenario()).status,'uncertain')
        self.assertEqual(tape.marketable(order_id='no-recovery',side=1,arrival_at=25,scenario=scenario()).status,'uncertain')


class CoupledFillTests(unittest.TestCase):
    def evaluate(self,engine,id='buy',**kwargs):
        return engine.evaluate(order_id=id,side=1,limit_ticks=100,arrival_at=3,cancel_effective_at=20,priority=kwargs.get('priority',1))

    def test_touch_without_print_is_only_the_explicit_optimistic_scenario(self):
        tape=path((quote(),quote('touch',at=5,known=6,bid=98,ask=100)))
        strict=self.evaluate(CoupledPassiveFills(tape,scenario()))
        optimistic=self.evaluate(CoupledPassiveFills(tape,scenario(passive='touch_quote_scenario')))
        self.assertEqual(strict.status,'no_fill_under_scenario');self.assertEqual(optimistic.status,'filled_under_scenario')

    def test_two_competing_orders_cannot_both_consume_one_print(self):
        tape=path(trades=(trade(),));engine=CoupledPassiveFills(tape,scenario())
        first=self.evaluate(engine);second=self.evaluate(engine,'second',priority=2)
        self.assertEqual(first.status,'filled_under_scenario');self.assertEqual(second.status,'no_fill_under_scenario');self.assertEqual(engine.used,{'t1':1})
        self.assertEqual(self.evaluate(engine),first)
        more=CoupledPassiveFills(path(trades=(trade(size=2),)),scenario())
        self.assertEqual(self.evaluate(more).quantity,1);self.assertEqual(self.evaluate(more,'second',priority=2).quantity,1)

    def test_trade_through_vs_at_limit_and_same_time_cancel_race(self):
        at_limit=path(trades=(trade(price=100),))
        self.assertEqual(self.evaluate(CoupledPassiveFills(at_limit,scenario())).status,'no_fill_under_scenario')
        self.assertEqual(self.evaluate(CoupledPassiveFills(at_limit,scenario(passive='post_arrival_trade_at_limit'))).status,'filled_under_scenario')
        cancel_tie=path(trades=(trade(at=20),))
        self.assertEqual(self.evaluate(CoupledPassiveFills(cancel_tie,scenario())).status,'uncertain')
        self.assertEqual(self.evaluate(CoupledPassiveFills(cancel_tie,scenario(ordering='order_first'))).status,'no_fill_under_scenario')
        self.assertEqual(self.evaluate(CoupledPassiveFills(cancel_tie,scenario(ordering='venue_first'))).status,'filled_under_scenario')

    def test_shortfall_components_are_attribution_and_allow_price_improvement(self):
        r=shortfall(side=1,decision_mid=Fraction(101),decision_executable=102,arrival_executable=104,fill_ticks=105)
        self.assertEqual((r['decision_spread_ticks'],r['latency_drift_ticks'],r['impact_ticks'],r['total_ticks']),(1,2,1,4))
        improvement=shortfall(side=-1,decision_mid=Fraction(101),decision_executable=100,arrival_executable=103,fill_ticks=103)
        self.assertEqual(improvement['total_ticks'],-2)
        self.assertEqual(sum(improvement[k] for k in ('decision_spread_ticks','latency_drift_ticks','impact_ticks')),improvement['total_ticks'])
