"""Exact one-account trading and business-cash ledgers with fixed day coverage."""

from dataclasses import asdict,dataclass
from datetime import date
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from trading_research.errors import ContractError,IntegrityError
from trading_research.execution.costs import FeeSchedule
from trading_research.foundations.units import FuturesTerms,Ticks,decimal_product,decimal_sum
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest
from trading_research.operations.journal import Journal


def usd(value):
    if not isinstance(value,Decimal) or not value.is_finite():raise ContractError("exact finite USD required")
    return value


def negative(value):return decimal_product(value,-1)


def sum_usd(*values):
    total=Decimal(0)
    for value in values:total=decimal_sum(total,value)
    return total


@dataclass(frozen=True)
class TradingFill:
    execution_id:str
    instrument:str
    trading_date:str
    at:int
    side:int
    price_ticks:int
    fee:Decimal
    fee_version:str
    source_version:str

    def __post_init__(self):
        date.fromisoformat(self.trading_date);usd(self.fee);timestamp(self.at)
        if not all((self.execution_id,self.instrument,self.fee_version,self.source_version)) or type(self.side) is not int or self.side not in (-1,1) or type(self.price_ticks) is not int or self.fee<=0:
            raise ContractError("one-mini fill requires actual price, positive verified per-side fees and immutable evidence")


class AccountingLedger:
    def __init__(self,path:Path,*,account_id:str,eligible_dates:tuple[str,...],eligibility_version:str,
                 terms:tuple[tuple[str,FuturesTerms],...],fees:FeeSchedule):
        if not account_id or not eligibility_version or not eligible_dates or len(set(eligible_dates))!=len(eligible_dates):raise ContractError("freeze all eligible dates before outcomes, including later flat/outage days")
        for d in eligible_dates:date.fromisoformat(d)
        self.account_id=account_id;self.dates=eligible_dates;self.terms=dict(terms);self.fees=fees;self.journal=Journal(path)
        if len(self.terms)!=len(terms) or any(t.root not in ('NQ','ES') for t in self.terms.values()):raise ContractError("raw NQ/ES mini terms required")
        self.journal.append(key='accounting-contract',kind='accounting_contract',payload={'account_id':account_id,'eligible_dates':eligible_dates,'eligibility_version':eligibility_version,
                           'terms':tuple((id,digest(t)) for id,t in terms),'fee_version':fees.version})

    def fill(self,fill:TradingFill):
        if fill.instrument not in self.terms or fill.trading_date not in self.dates:raise ContractError("fill lies outside the declared raw contract/date universe")
        if fill.fee_version!=self.fees.version or fill.fee!=self.fees.fee(self.terms[fill.instrument].root):raise ContractError("fee differs from the frozen scenario; register changed fees explicitly")
        payload={**asdict(fill),'fee':str(fill.fee)}
        self.journal.append(key='fill:'+fill.execution_id,kind='trading_fill',payload=payload)

    def day_status(self,*,trading_date:str,at:int,status:str,evidence_version:str):
        if trading_date not in self.dates or status not in ('complete','flat','outage','halted','incomplete','boundary_failure') or not evidence_version:
            raise ContractError("day status cannot remove a predeclared eligible date")
        timestamp(at)
        payload = {'date': trading_date, 'at': at, 'status': status,
                   'evidence_version': evidence_version}
        # A date has one immutable final status in this ledger version.  Exact
        # replays are idempotent, including journals created by the old
        # date:at key; a changed clock/status/evidence requires a new ledger
        # identity rather than silently rewriting the report.
        existing = tuple(event for event in self.journal.read()
                         if event['kind'] == 'day_status'
                         and event['payload'].get('date') == trading_date)
        if existing:
            if any(event['payload'] != payload for event in existing):
                raise IntegrityError("conflicting day status requires an explicit new ledger version")
            return
        self.journal.append(key='day:'+trading_date+':final', kind='day_status', payload=payload)

    def cash(self,*,id:str,at:int,kind:str,amount:Decimal,evidence_version:str,payout_id:str|None=None):
        usd(amount)
        if not id or not evidence_version or amount<=0 or kind not in ('account_purchase','reset_fee','data_fee','platform_fee','payout_received','refund_received','payout_eligible','payout_requested','payout_approved'):
            raise ContractError("cash/receivable event requires a positive amount and explicit paid/pending category")
        if kind.startswith('payout_') and not payout_id:raise ContractError("payout events require lifecycle identity")
        actual_in=kind in ('payout_received','refund_received');actual_out=kind in ('account_purchase','reset_fee','data_fee','platform_fee')
        cash_change=amount if actual_in else decimal_product(amount,-1) if actual_out else Decimal(0)
        self.journal.append(key='cash:'+id,kind='business_event',payload={'id':id,'at':at,'kind':kind,'amount':str(amount),'payout_id':payout_id,'evidence_version':evidence_version,
                           'entries':{'cash_usd':str(cash_change),'offset_usd':str(decimal_product(cash_change,-1))}})

    def report(self):
        events=self.journal.read();days={d:{'gross':Decimal(0),'fees':Decimal(0),'net':Decimal(0),'fills':0,'status':'unreported'} for d in self.dates}
        position=None;last_at=None;violations=[];cash=Decimal(0);paid=Decimal(0);payouts={};cash_costs=Decimal(0)
        for event in events:
            p=event['payload']
            if event['kind']=='trading_fill':
                if last_at is not None and p['at']<last_at:raise IntegrityError("trading fill sequence regressed; late corrections need a separate explicit ledger version")
                last_at=p['at'];day=days[p['trading_date']];fee=Decimal(p['fee']);day['fees']=decimal_sum(day['fees'],fee);day['fills']+=1
                if position is None:position=p
                elif position['instrument']!=p['instrument'] or position['side']==p['side']:
                    violations.append({'kind':'illegal_add_or_cross_instrument','execution':p['execution_id']});raise IntegrityError("fill ledger reveals unauthorized multiple exposure; preserve broker incident separately")
                else:
                    gross=self.terms[p['instrument']].pnl(Ticks(position['price_ticks']),Ticks(p['price_ticks']),side=position['side']).value
                    day['gross']=decimal_sum(day['gross'],gross)
                    if position['trading_date']!=p['trading_date']:violations.append({'kind':'crossed_trading_day','entry':position['execution_id'],'exit':p['execution_id']})
                    position=None
            elif event['kind']=='day_status':days[p['date']]['status']=p['status']
            elif event['kind']=='business_event':
                amount=Decimal(p['amount']);change=Decimal(p['entries']['cash_usd'])
                if decimal_sum(change,Decimal(p['entries']['offset_usd']))!=0:raise IntegrityError("cash double-entry ledger does not balance")
                cash=decimal_sum(cash,change)
                if change<0:cash_costs=decimal_sum(cash_costs,decimal_product(change,-1))
                if p['kind'].startswith('payout_'):
                    state=payouts.setdefault(p['payout_id'],{'stage':'unreported','recognized_amount':Decimal(0),'received':Decimal(0)})
                    if p['kind']=='payout_received':
                        if state['stage']=='unreported':state['recognized_amount']=amount
                        state['received']=decimal_sum(state['received'],amount);paid=decimal_sum(paid,amount)
                    else:
                        state['stage']=p['kind'];state['recognized_amount']=amount
        total=Decimal(0)
        for d,row in days.items():row['net']=decimal_sum(row['gross'],decimal_product(row['fees'],-1));total=decimal_sum(total,row['net'])
        if position:violations.append({'kind':'unclosed_position','execution':position['execution_id']})
        complete=not violations and all(d['status'] not in ('unreported','incomplete','boundary_failure') for d in days.values())
        mean=Fraction(total)/len(days) if complete else None
        return {'account':self.account_id,'days':days,'eligible_day_count':len(days),'trading_net':total,'mean_net_per_eligible_day':mean,
                'objective_gap':None if mean is None else Fraction(2000)-mean,'complete':complete,'violations':violations,
                'business_net_cash':cash,'paid_business_costs':cash_costs,'received_payouts':paid,
                'eligible_or_pending_payouts':{id:{**p,'unpaid_amount':sum_usd(p['recognized_amount'],negative(p['received']))} for id,p in payouts.items() if p['recognized_amount']>p['received']},
                'payout_receipt_discrepancies':{id:p for id,p in payouts.items() if p['received']>p['recognized_amount']},
                'interpretation':'Spread/latency/impact already represented in actual fill prices; withdrawals and business expenses are separate from trading P&L.'}


@dataclass(frozen=True)
class AccountRules:
    id:str
    basis:str
    evidence_version:str
    initial_equity:Decimal
    drawdown_amount:Decimal
    trailing_mode:str
    floor_cap:Decimal|None
    breach_at_equality:bool
    consistency_fraction:Fraction|None
    minimum_active_days:int

    def __post_init__(self):
        if not self.id or not self.evidence_version or self.basis not in ('synthetic_research_scenario','verified_product_version'):raise ContractError("rules need an explicit synthetic or verified product basis")
        if usd(self.initial_equity)<=0 or usd(self.drawdown_amount)<=0 or self.trailing_mode not in ('static','end_of_day','intraday') or (self.floor_cap is not None and usd(self.floor_cap)<sum_usd(self.initial_equity,negative(self.drawdown_amount))):raise ContractError("invalid explicit drawdown floor rule")
        if self.consistency_fraction is not None and not 0<self.consistency_fraction<=1:raise ContractError("consistency limit must be explicit")
        if type(self.minimum_active_days) is not int or self.minimum_active_days<0:raise ContractError("invalid activity rule")

    @property
    def version(self):return digest(self)


class AccountRuleState:
    def __init__(self,rules:AccountRules):
        self.rules=rules;self.equity=rules.initial_equity;self.high_water=rules.initial_equity;self.floor=sum_usd(rules.initial_equity,negative(rules.drawdown_amount))
        self.pending_withdrawal=Decimal(0);self.breached=False;self.days={};self.path=[]

    def observe(self,*,at:int,trading_date:str,net_liquidation_equity:Decimal,end_of_day:bool=False,day_net:Decimal|None=None,active:bool=False):
        usd(net_liquidation_equity);timestamp(at);date.fromisoformat(trading_date)
        if self.path and at<self.path[-1]['at']:raise ContractError("account rule observation moved backward")
        if end_of_day:
            if day_net is None:raise ContractError("end-of-day consistency requires actual daily net")
            usd(day_net)
            if trading_date in self.days:raise ContractError("day already finalized; append a separately versioned rule correction")
        self.equity=net_liquidation_equity
        # Breach is checked against the previously binding floor before any EOD update.
        available=sum_usd(self.equity,negative(self.pending_withdrawal))
        breach=available<=self.floor if self.rules.breach_at_equality else available<self.floor
        self.breached|=breach
        if self.rules.trailing_mode=='intraday' or self.rules.trailing_mode=='end_of_day' and end_of_day:
            self.high_water=max(self.high_water,self.equity);new=sum_usd(self.high_water,negative(self.rules.drawdown_amount))
            if self.rules.floor_cap is not None:new=min(new,self.rules.floor_cap)
            self.floor=max(self.floor,new)
        if end_of_day:
            self.days[trading_date]={'net':day_net,'active':active}
        row={'at':at,'date':trading_date,'equity':self.equity,'floor':self.floor,'headroom':sum_usd(available,negative(self.floor)),'breached':self.breached,'rule_version':self.rules.version}
        self.path.append(row);return row

    def payout_eligibility(self):
        total=sum((Fraction(d['net']) for d in self.days.values()),Fraction(0));best=max((Fraction(d['net']) for d in self.days.values()),default=Fraction(0))
        consistency=None if total<=0 else max(Fraction(0),best)/total
        active=sum(d['active'] for d in self.days.values())
        allowed=not self.breached and active>=self.rules.minimum_active_days and total>0 and (self.rules.consistency_fraction is None or consistency<=self.rules.consistency_fraction)
        return {'eligible_under_declared_rules':allowed,'active_days':active,'total_net':total,'best_day_over_total_net':consistency,'basis':self.rules.basis,'received_cash':False}

    def reserve_payout(self,amount:Decimal):
        usd(amount)
        if amount<=0 or self.breached or sum_usd(self.equity,negative(self.pending_withdrawal),negative(amount))<=self.floor:raise ContractError("payout reservation would consume binding floor headroom")
        self.pending_withdrawal=decimal_sum(self.pending_withdrawal,amount)
