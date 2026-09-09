from dataclasses import replace
from decimal import Decimal,localcontext
from fractions import Fraction
from pathlib import Path
import tempfile
import unittest

from trading_research.errors import ContractError,IntegrityError
from trading_research.execution.accounting import AccountingLedger,TradingFill,AccountRules,AccountRuleState
from trading_research.execution.costs import load_fee_scenarios
from trading_research.execution.orders import BrokerEvent,OrderLedger,OrderSpec
from trading_research.foundations.units import NQ_REFERENCE


ROOT=Path(__file__).resolve().parents[1]


def spec(id='entry',side=1,role='entry',at=1,parent=None,oco=None):
    return OrderSpec(id,'synthetic','NQH5',side,1,role,'stop_market' if role=='protective_stop' else 'market',90 if role=='protective_stop' else None,at,1000,'risk-approved-fixture',oco,parent)


def event(id,order='entry',kind='working',at=2,execution=None,qty=0,price=None):
    return BrokerEvent(id,order,kind,at,at,'simulated-broker-truth',execution,qty,price)


class OrderFaultTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'orders.sqlite';self.ledger=OrderLedger(self.path,account_id='synthetic')
        self.reconcile('initial',at=0)

    def reconcile(self,id,at=10,positions=None,orders=(),complete=True):
        self.ledger.reconcile(id=id,known_at=at,positions=positions or {},open_order_ids=orders,open_orders_complete=complete,execution_history_complete=complete,evidence_version='broker-snapshot:'+id)

    def fill_entry(self):
        self.ledger.submit(spec());self.ledger.observe(event('fill',kind='fill',at=2,execution='exec1',qty=1,price=100))

    def test_duplicate_execution_late_ack_and_restart_do_not_add_another_unit(self):
        self.fill_entry();self.ledger.observe(event('late-ack',kind='acknowledged',at=3))
        self.ledger.observe(replace(event('redelivery',kind='fill',at=4,execution='exec1',qty=1,price=100),event_at=2))
        state=self.ledger.state();self.assertEqual(state['positions'],{'NQH5':1});self.assertEqual(state['orders']['entry']['state'],'filled');self.assertEqual(len(state['executions']),1)
        restored=OrderLedger(self.path,account_id='synthetic');self.assertEqual(restored.state(),state)
        with self.assertRaises(IntegrityError):self.ledger.observe(replace(event('changed',kind='fill',at=5,execution='exec1',qty=1,price=101),event_at=2))
        with self.assertRaises(ContractError):self.ledger.submit(spec('add',at=5))

    def test_timeout_and_partial_snapshot_never_release_pending_exposure(self):
        self.ledger.submit(spec());self.ledger.observe(event('timeout',kind='timeout',at=2));self.reconcile('partial',at=3,complete=False)
        self.assertFalse(self.ledger.state()['entry_allowed']);self.assertIn('entry',self.ledger.state()['live_orders'])
        with self.assertRaises(ContractError):self.ledger.submit(spec('retry',at=4))
        self.reconcile('complete',at=5);self.assertTrue(self.ledger.state()['entry_allowed']);self.assertEqual(self.ledger.state()['orders']['entry']['state'],'closed_by_reconciliation')

    def test_fill_during_cancel_is_retained_and_cancel_reject_does_not_undo_it(self):
        self.ledger.submit(spec());self.ledger.observe(event('cancel',kind='cancel_requested',at=2));self.ledger.observe(event('fill',kind='fill',at=3,execution='e',qty=1,price=102));self.ledger.observe(event('cancel-reject',kind='cancel_rejected',at=4))
        self.assertEqual(self.ledger.state()['positions'],{'NQH5':1});self.assertEqual(self.ledger.state()['orders']['entry']['state'],'filled')
        self.reconcile('broker',at=5,positions={'NQH5':1});self.assertFalse(self.ledger.state()['entry_allowed'])

    def test_oco_sibling_is_not_atomically_cancelled_and_race_reversal_is_visible(self):
        self.fill_entry();self.ledger.submit(spec('stop',-1,'protective_stop',3,'entry','bracket'));self.ledger.submit(spec('target',-1,'target',3,'entry','bracket'))
        self.ledger.observe(event('stop-ack','stop',at=4));self.ledger.observe(event('target-ack','target',at=4))
        self.ledger.observe(event('take-profit','target','fill',5,'target-fill',1,110))
        self.assertIn('stop',self.ledger.state()['live_orders'])
        self.ledger.observe(event('sibling-race','stop','fill',6,'stop-fill',1,90))
        state=self.ledger.state();self.assertEqual(state['positions'],{'NQH5':-1});self.assertTrue(any(i['kind']=='exit_reversed_position' for i in state['incidents']))
        self.assertFalse(state['entry_allowed'])

    def test_unprotected_interval_and_broker_position_discrepancy_remain_explicit(self):
        self.fill_entry();self.assertEqual(self.ledger.state()['unprotected_since'],2)
        self.ledger.submit(spec('stop',-1,'protective_stop',3,'entry'));self.ledger.observe(event('working','stop',at=5))
        self.assertEqual(self.ledger.state()['observed_unprotected_intervals'],((2,5),))
        self.reconcile('wrong',at=6,positions={'NQH5':2},orders=('stop',));state=self.ledger.state()
        self.assertEqual(state['positions']['NQH5'],1);self.assertFalse(state['reconciled']);self.assertTrue(any(i['kind']=='position_discrepancy' for i in state['incidents']))


class CashAndDayTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.fees=load_fee_scenarios(ROOT/'configs/fee-scenarios.json')[0]
        self.ledger=AccountingLedger(Path(self.temp.name)/'cash.sqlite',account_id='synthetic',eligible_dates=('2025-01-02','2025-01-03'),eligibility_version='frozen-before-outcomes',terms=(('NQH5',NQ_REFERENCE),),fees=self.fees)

    def fill(self,id,side,price,at=1,day='2025-01-02'):
        return TradingFill(id,'NQH5',day,at,side,price,self.fees.fee('NQ'),self.fees.version,'simulated-fill')

    def test_zero_trade_outage_day_stays_in_mean_and_spread_is_not_charged_twice(self):
        entry=self.fill('entry',1,101);self.ledger.fill(entry);self.ledger.fill(self.fill('exit',-1,99,2))
        self.ledger.fill(entry)
        self.ledger.day_status(trading_date='2025-01-02',at=3,status='complete',evidence_version='flat-proof')
        self.ledger.day_status(trading_date='2025-01-03',at=4,status='outage',evidence_version='no-orders-no-position-proof')
        with localcontext() as context:
            context.prec=2;r=self.ledger.report()
        self.assertEqual(r['days']['2025-01-02']['gross'],Decimal('-10.00'));self.assertEqual(r['trading_net'],Decimal('-15.76'));self.assertEqual(r['mean_net_per_eligible_day'],Fraction(-197,25));self.assertEqual(r['eligible_day_count'],2)
        self.assertEqual(r['business_net_cash'],Decimal(0))

    def test_pending_payout_is_not_cash_withdrawal_is_not_trading_loss(self):
        self.ledger.cash(id='purchase',at=1,kind='account_purchase',amount=Decimal(100),evidence_version='paid')
        self.ledger.cash(id='reset',at=2,kind='reset_fee',amount=Decimal(50),evidence_version='failed-attempt-paid')
        self.ledger.cash(id='request',at=3,kind='payout_requested',amount=Decimal(500),payout_id='payout',evidence_version='requested')
        self.assertEqual(self.ledger.report()['business_net_cash'],Decimal(-150));self.assertEqual(self.ledger.report()['received_payouts'],Decimal(0))
        self.ledger.cash(id='receipt',at=4,kind='payout_received',amount=Decimal(450),payout_id='payout',evidence_version='bank-received')
        r=self.ledger.report();self.assertEqual(r['business_net_cash'],Decimal(300));self.assertEqual(r['received_payouts'],Decimal(450));self.assertEqual(r['trading_net'],0);self.assertEqual(r['eligible_or_pending_payouts']['payout']['unpaid_amount'],Decimal(50))
        self.ledger.cash(id='remaining-receipt',at=5,kind='payout_received',amount=Decimal(50),payout_id='payout',evidence_version='second-bank-receipt')
        self.assertEqual(self.ledger.report()['eligible_or_pending_payouts'],{})
        self.assertEqual(self.ledger.report()['business_net_cash'],Decimal(350))

    def test_unreported_and_cross_day_open_positions_block_completed_objective(self):
        self.assertFalse(self.ledger.report()['complete']);self.ledger.fill(self.fill('entry',1,100));self.ledger.fill(self.fill('exit',-1,110,3,'2025-01-03'))
        for i,d in enumerate(self.ledger.dates):self.ledger.day_status(trading_date=d,at=4+i,status='complete',evidence_version='day')
        r=self.ledger.report();self.assertIsNone(r['mean_net_per_eligible_day']);self.assertTrue(any(v['kind']=='crossed_trading_day' for v in r['violations']))
        with self.assertRaises(ContractError):self.ledger.fill(replace(self.fill('new',1,100,6),fee=Decimal(0)))


class RuleScenarioTests(unittest.TestCase):
    def rules(self,**changes):
        return replace(AccountRules('fixture','synthetic_research_scenario','hand-calculated',Decimal(50000),Decimal(2000),'end_of_day',Decimal(50000),True,Fraction(1,2),2),**changes)

    def test_end_of_day_high_water_does_not_trail_intraday_but_breach_does(self):
        s=AccountRuleState(self.rules());s.observe(at=1,trading_date='2025-01-02',net_liquidation_equity=Decimal(52000));self.assertEqual(s.floor,Decimal(48000))
        s.observe(at=2,trading_date='2025-01-02',net_liquidation_equity=Decimal(48000));self.assertTrue(s.breached)
        s.observe(at=3,trading_date='2025-01-02',net_liquidation_equity=Decimal(51000),end_of_day=True,day_net=Decimal(1000),active=True)
        self.assertTrue(s.breached);self.assertEqual(s.floor,Decimal(49000))
        strict=AccountRuleState(self.rules(breach_at_equality=False));strict.observe(at=1,trading_date='2025-01-02',net_liquidation_equity=Decimal(48000));self.assertFalse(strict.breached)

    def test_floor_lock_loss_day_consistency_and_pending_withdrawal_reserve(self):
        s=AccountRuleState(self.rules())
        for at,d,equity,net in ((1,'2025-01-02',52000,2000),(2,'2025-01-03',54000,2000),(3,'2025-01-06',53000,-1000)):
            s.observe(at=at,trading_date=d,net_liquidation_equity=Decimal(equity),end_of_day=True,day_net=Decimal(net),active=True)
        self.assertEqual(s.floor,Decimal(50000));elig=s.payout_eligibility();self.assertEqual(elig['best_day_over_total_net'],Fraction(2,3));self.assertFalse(elig['eligible_under_declared_rules'])
        s.reserve_payout(Decimal(1000));row=s.observe(at=4,trading_date='2025-01-07',net_liquidation_equity=Decimal(53000));self.assertEqual(row['headroom'],Decimal(2000))
        with self.assertRaises(ContractError):s.reserve_payout(Decimal(2000))

    def test_rule_arithmetic_survives_low_precision_and_failed_update_is_atomic(self):
        with localcontext() as context:
            context.prec=2;s=AccountRuleState(self.rules(initial_equity=Decimal('50000.25')))
            self.assertEqual(s.floor,Decimal('48000.25'))
            s.observe(at=1,trading_date='2025-01-02',net_liquidation_equity=Decimal('50200.37'),end_of_day=True,day_net=Decimal('200.12'))
            self.assertEqual(s.floor,Decimal('48200.37'))
            prior=(s.equity,s.floor,s.high_water,len(s.path))
            with self.assertRaises(ContractError):s.observe(at=2,trading_date='2025-01-03',net_liquidation_equity=Decimal(100000),end_of_day=True)
            self.assertEqual((s.equity,s.floor,s.high_water,len(s.path)),prior)
