"""Standing venue quotes, strategy availability and coupled hypothetical fills."""

from bisect import bisect_left,bisect_right
from dataclasses import dataclass
from fractions import Fraction
from itertools import groupby

from trading_research.errors import ContractError,DependencyUnavailable
from trading_research.foundations.time import timestamp
from trading_research.operations.artifacts import digest


@dataclass(frozen=True)
class VenueQuote:
    id:str
    instrument:str
    event_at:int
    known_at:int
    sequence:int|None
    bid:int
    ask:int
    bid_size:int
    ask_size:int
    book_valid:bool
    market_state:str
    source_version:str

    def __post_init__(self):
        timestamp(self.event_at);timestamp(self.known_at)
        if not self.id or not self.instrument or not self.source_version or self.market_state not in ('continuous','auction','halted','closed','unknown'):
            raise ContractError("quote needs instrument, source and explicit market state")
        if any(type(v) is not int for v in (self.bid,self.ask,self.bid_size,self.ask_size)) or self.bid_size<0 or self.ask_size<0 or (self.sequence is not None and type(self.sequence) is not int):
            raise ContractError("exact tick, depth and source ordering required")

    @property
    def executable(self):return self.book_valid and self.market_state=='continuous' and 0<self.bid<self.ask and min(self.bid_size,self.ask_size)>0


@dataclass(frozen=True)
class VenueTrade:
    id:str
    instrument:str
    event_at:int
    sequence:int|None
    ticks:int
    quantity:int
    aggressor:int|None
    source_version:str

    def __post_init__(self):
        timestamp(self.event_at)
        if not self.id or not self.instrument or not self.source_version or type(self.ticks) is not int or type(self.quantity) is not int or self.quantity<1 or self.aggressor not in (-1,1,None):
            raise ContractError("venue trade needs source identity, exact price and whole quantity")


@dataclass(frozen=True)
class FillScenario:
    id:str
    impact_ticks:int
    same_time_ordering:str
    passive_rule:str
    quote_coverage_version:str
    fee_version:str

    def __post_init__(self):
        if not all((self.id,self.quote_coverage_version,self.fee_version)) or type(self.impact_ticks) is not int or self.impact_ticks<0:
            raise ContractError("fill assumptions and verified fees must be named")
        if self.same_time_ordering not in ('ambiguous','venue_first','order_first') or self.passive_rule not in ('touch_quote_scenario','post_arrival_trade_at_limit','strict_trade_through'):
            raise ContractError("unregistered timing or hypothetical passive priority scenario")

    @property
    def version(self):return digest(self)


@dataclass(frozen=True)
class Fill:
    order_id:str
    status:str
    at:int
    price_ticks:int|None
    quantity:int
    side:int
    source_event_id:str|None
    scenario_version:str
    reason:str


class VenuePath:
    def __init__(self,*,instrument:str,quotes:tuple[VenueQuote,...],trades:tuple[VenueTrade,...],
                 complete_intervals:tuple[tuple[int,int],...],coverage_version:str,max_events:int=2_000_000):
        if not instrument or not coverage_version or len(quotes)+len(trades)>max_events:raise ContractError("bounded source-certified venue path required")
        if any(e.instrument!=instrument for e in (*quotes,*trades)) or len({e.id for e in (*quotes,*trades)})!=len(quotes)+len(trades):raise ContractError("duplicate evidence or mixed raw contracts in venue path")
        if any(a>=b for a,b in complete_intervals) or any(a[1]>b[0] for a,b in zip(complete_intervals,complete_intervals[1:])):raise ContractError("venue coverage intervals overlap or reverse")
        self.instrument=instrument;self.quotes=tuple(sorted(quotes,key=lambda q:(q.event_at,q.sequence if q.sequence is not None else -1,q.id)))
        self.trades=tuple(sorted(trades,key=lambda t:(t.event_at,t.sequence if t.sequence is not None else -1,t.id)))
        self.times=tuple(q.event_at for q in self.quotes);self.trade_times=tuple(t.event_at for t in self.trades)
        self.complete_intervals=complete_intervals;self.coverage_version=coverage_version
        self.information_times=[];self.information_states=[];latest_event=None;current={}
        for known,batch in groupby(sorted(self.quotes,key=lambda q:q.known_at),key=lambda q:q.known_at):
            for q in batch:
                if latest_event is None or q.event_at>latest_event:latest_event=q.event_at;current={q.id:q}
                elif q.event_at==latest_event:current[q.id]=q
            group=tuple(current.values())
            if len(group)>1 and (any(q.sequence is None for q in group) or len({q.sequence for q in group})!=len(group)):
                state=(None,'same-time source quote ordering is unproved')
            else:
                latest=max(group,key=lambda q:q.sequence if q.sequence is not None else -1)
                state=(latest,None) if latest.executable else (None,'invalid/crossed/empty/stale-book or noncontinuous venue quote')
            self.information_times.append(known);self.information_states.append(state)
        self.version=digest({'instrument':instrument,'quotes':quotes,'trades':trades,'coverage':complete_intervals,'version':coverage_version})

    def covered(self,start,end=None):
        timestamp(start);end=start if end is None else timestamp(end)
        if end<start:raise ContractError("coverage interval reversed")
        cursor=start
        for left,right in self.complete_intervals:
            if left<=cursor<right:
                if end<right:return True
                cursor=right
        return False

    def quote_range(self,start,end,*,clock='venue'):
        if clock=='venue':return iter(self.quotes[bisect_left(self.times,start):bisect_right(self.times,end)])
        if clock=='strategy':return (q for q in self.quotes if start<=q.known_at<=end)
        raise ContractError("unknown quote range clock")

    def trade_range(self,start,end):return iter(self.trades[bisect_left(self.trade_times,start):bisect_right(self.trade_times,end)])

    def quote_at(self,at:int,*,clock:str,same_time_ordering:str='ambiguous'):
        timestamp(at)
        if clock not in ('venue','strategy'):raise ContractError("choose venue outcome or actual strategy-information clock")
        if clock=='strategy':
            index=bisect_right(self.information_times,at)-1
            if index<0:return None,'missing strategy quote'
            q,reason=self.information_states[index]
            if q is not None and q.event_at>at:return None,'source event clock ahead of strategy cut; unresolved clock skew'
            return q,reason
        else:
            if not self.covered(at):return None,'venue observation interval not certified'
            end=bisect_left(self.times,at) if same_time_ordering=='order_first' else bisect_right(self.times,at)
            if end==0:return None,'no standing venue quote'
            if same_time_ordering=='ambiguous' and self.quotes[end-1].event_at==at:return None,'order arrival versus same-time venue update is ambiguous'
            last=self.quotes[end-1];start=bisect_left(self.times,last.event_at);tied=list(self.quotes[start:end])
        if len(tied)>1 and (any(q.sequence is None for q in tied) or len({q.sequence for q in tied})!=len(tied)):
            return None,'same-time source quote ordering is unproved'
        quote=max(tied,key=lambda q:q.sequence if q.sequence is not None else -1)
        if clock=='venue':
            segment_start=None;previous_end=None
            for left,right in self.complete_intervals:
                if previous_end!=left:segment_start=left
                if left<=at<right:break
                previous_end=right
            if segment_start is not None and quote.event_at<segment_start:
                return None,'standing quote predates an unobserved interval; explicit book recovery is required'
        return (quote,None) if quote.executable else (None,'invalid/crossed/empty/stale-book or noncontinuous venue quote')

    def marketable(self,*,order_id:str,side:int,arrival_at:int,scenario:FillScenario):
        if not order_id or type(side) is not int or side not in (-1,1) or scenario.quote_coverage_version!=self.coverage_version:raise ContractError("marketable order needs matching coverage and one-unit direction")
        q,reason=self.quote_at(arrival_at,clock='venue',same_time_ordering=scenario.same_time_ordering)
        if q is None:return Fill(order_id,'uncertain',arrival_at,None,0,side,None,scenario.version,reason)
        price=(q.ask if side==1 else q.bid)+side*scenario.impact_ticks
        return Fill(order_id,'filled_under_scenario',arrival_at,price,1,side,q.id,scenario.version,'standing side-correct BBO plus declared adverse impact; historical receipt/queue exactness is not implied')


class CoupledPassiveFills:
    """One shared tape capacity per scenario; process orders in declared priority."""
    def __init__(self,path:VenuePath,scenario:FillScenario):
        if scenario.quote_coverage_version!=path.coverage_version:raise ContractError("scenario coverage mismatch")
        self.path=path;self.scenario=scenario;self.used={};self.orders={};self.last_priority=None

    def evaluate(self,*,order_id:str,side:int,limit_ticks:int,arrival_at:int,cancel_effective_at:int,priority:int):
        args=(side,limit_ticks,arrival_at,cancel_effective_at,priority)
        if order_id in self.orders:
            old,result=self.orders[order_id]
            if old!=args:raise ContractError("hypothetical order ID changed")
            return result
        if side not in (-1,1) or any(type(v) is not int for v in (limit_ticks,arrival_at,cancel_effective_at,priority)) or cancel_effective_at<=arrival_at or self.last_priority is not None and priority<=self.last_priority:
            raise ContractError("passive orders require original expiry and strictly declared shared priority")
        self.last_priority=priority;scenario=self.scenario;path=self.path
        def result(status,at,price=None,event=None,reason=''):
            fill=Fill(order_id,status,at,price,1 if price is not None else 0,side,event,scenario.version,reason);self.orders[order_id]=(args,fill);return fill
        if not path.covered(arrival_at,cancel_effective_at):return result('uncertain',arrival_at,reason='incomplete order-life observation interval')
        standing,reason=path.quote_at(arrival_at,clock='venue',same_time_ordering=scenario.same_time_ordering)
        if standing is None:return result('uncertain',arrival_at,reason=reason)
        if standing and side*((standing.ask if side==1 else standing.bid)-limit_ticks)<=0:
            return result('uncertain',arrival_at,reason='order is marketable at arrival; use registered marketable-limit routing assumptions')
        if scenario.passive_rule=='touch_quote_scenario':
            for q in path.quotes:
                if arrival_at<q.event_at<cancel_effective_at and q.executable and side*((q.ask if side==1 else q.bid)-limit_ticks)<=0:
                    return result('filled_under_scenario',q.event_at,limit_ticks,q.id,'optimistic quote-touch scenario, with no queue-rank evidence')
        else:
            for t in path.trades[bisect_left(path.trade_times,arrival_at):]:
                if t.event_at>cancel_effective_at:break
                if t.aggressor!=-side:continue
                through=side*(t.ticks-limit_ticks)
                if through>0 or scenario.passive_rule=='strict_trade_through' and through==0:continue
                if t.event_at in (arrival_at,cancel_effective_at):
                    if scenario.same_time_ordering=='ambiguous':return result('uncertain',t.event_at,event=t.id,reason='execution versus arrival/cancellation ordering ambiguous')
                    if t.event_at==arrival_at and scenario.same_time_ordering=='venue_first' or t.event_at==cancel_effective_at and scenario.same_time_ordering=='order_first':continue
                if self.used.get(t.id,0)>=t.quantity:continue
                executable_quote,reason=path.quote_at(t.event_at,clock='venue',same_time_ordering='venue_first')
                if executable_quote is None:return result('uncertain',t.event_at,event=t.id,reason=reason)
                self.used[t.id]=self.used.get(t.id,0)+1
                return result('filled_under_scenario',t.event_at,limit_ticks,t.id,'post-arrival execution allocated under declared coupled priority; no exact MBP queue claim')
        return result('no_fill_under_scenario',cancel_effective_at,reason='no eligible execution under this complete-window priority scenario')


def shortfall(*,side:int,decision_mid:Fraction,decision_executable:int,arrival_executable:int,fill_ticks:int):
    if side not in (-1,1) or not isinstance(decision_mid,Fraction):raise ContractError("signed exact decision benchmark required")
    spread=side*(Fraction(decision_executable)-decision_mid);latency=Fraction(side*(arrival_executable-decision_executable));impact=Fraction(side*(fill_ticks-arrival_executable))
    total=side*(Fraction(fill_ticks)-decision_mid)
    if spread+latency+impact!=total:raise ContractError("shortfall attribution does not reconcile")
    return {'total_ticks':total,'decision_spread_ticks':spread,'latency_drift_ticks':latency,'impact_ticks':impact,
            'accounting':'attribution within side-correct fill prices, not three additional cash charges'}
