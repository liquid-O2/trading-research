"""One-unit marketable bracket reference with explicit cancellation latency.

This conservative route keeps one native protective stop. A local target/time/
boundary exit first requests stop cancellation, waits for simulated complete
broker reconciliation, then sends a marketable full exit if still positioned.
OCO sibling cancellation is never presumed atomic. This route is a separately
versioned execution assumption, not verified Rithmic/Tradovate behavior.
"""

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from trading_research.errors import ContractError
from trading_research.execution.accounting import negative,sum_usd
from trading_research.execution.costs import FeeSchedule
from trading_research.execution.venue import Fill,FillScenario,VenuePath
from trading_research.foundations.time import timestamp
from trading_research.foundations.units import FuturesTerms,Ticks
from trading_research.operations.artifacts import digest
from trading_research.risk.budget import Exposure,risk_verdict


@dataclass(frozen=True)
class BracketPlan:
    id:str
    instrument:str
    side:int
    decision_at:int
    worst_entry_ticks:int
    stop_ticks:int
    target_ticks:int
    horizon_end:int
    flatten_send_at:int
    required_flat_at:int
    gap_reserve_usd:Decimal
    geometry_version:str

    def __post_init__(self):
        for at in (self.decision_at,self.horizon_end,self.flatten_send_at,self.required_flat_at):timestamp(at)
        if not self.id or not self.instrument or not self.geometry_version or self.side not in (-1,1) or any(type(x) is not int for x in (self.worst_entry_ticks,self.stop_ticks,self.target_ticks)):
            raise ContractError("bracket requires a frozen one-unit raw-contract plan")
        if self.side*(self.worst_entry_ticks-self.stop_ticks)<=0 or self.side*(self.target_ticks-self.worst_entry_ticks)<=0:
            raise ContractError("stop and target must lie on opposite sides of the frozen entry bound")
        if min(self.horizon_end,self.flatten_send_at)<=self.decision_at or self.required_flat_at<=self.flatten_send_at or not isinstance(self.gap_reserve_usd,Decimal) or not self.gap_reserve_usd.is_finite() or self.gap_reserve_usd<0:
            raise ContractError("bracket has insufficient original horizon or boundary/reserve margin")

    @property
    def version(self):return digest(self)


@dataclass(frozen=True)
class OrderTiming:
    id:str
    outbound_ns:int
    broker_report_ns:int
    native_stop_delay_ns:int
    cancellation_tie:str
    protection_activation:str='synthetic_prestaged_contingent_stop'

    def __post_init__(self):
        if not self.id or any(type(v) is not int or v<0 for v in (self.outbound_ns,self.broker_report_ns,self.native_stop_delay_ns)) or self.cancellation_tie not in ('ambiguous','cancel_first','trigger_first'):
            raise ContractError("explicit routing, broker-report, stop and race assumptions required")
        if self.protection_activation!='synthetic_prestaged_contingent_stop':raise ContractError("unimplemented protection activation requires a separate route")


@dataclass(frozen=True)
class BracketOutcome:
    plan_version:str
    entry:Fill
    exit:Fill|None
    exit_reason:str
    position_known_flat_at:int|None
    gross_usd:Decimal|None
    fees_usd:Decimal
    net_usd:Decimal|None
    minimum_marked_net_usd:Decimal|None
    daily_loss_breach:bool|None
    boundary_met:bool
    unprotected_interval:tuple[int,int]|None
    events:tuple[dict,...]
    timing_version:str
    observation_complete:bool


def reference_bracket(path:VenuePath,plan:BracketPlan,*,terms:FuturesTerms,fees:FeeSchedule,
                      fill_scenario:FillScenario,timing:OrderTiming,prior_day_net:Decimal=Decimal(0),daily_budget:Decimal=Decimal(1000)):
    if plan.instrument!=path.instrument or fill_scenario.fee_version!=fees.version or terms.root not in ('NQ','ES'):
        raise ContractError("bracket, raw venue contract, mini terms and verified fees disagree")
    exposure=Exposure(plan.instrument,terms,plan.side,Ticks(plan.worst_entry_ticks),Ticks(plan.stop_ticks),fees.fee(terms.root,sides=2),plan.gap_reserve_usd)
    verdict=risk_verdict(daily_budget=daily_budget,trading_net_liquidation_pnl=prior_day_net,firm_headroom=None,mutually_possible_exposures=(exposure,),rule_version='synthetic-static-day-start-budget',state_known=True)
    if not verdict.allowed:raise ContractError('bracket refused before entry: '+verdict.reason)
    quote,why=path.quote_at(plan.decision_at,clock='strategy')
    if quote is None:raise ContractError('entry decision lacks an eligible strategy quote: '+why)
    executable=quote.ask if plan.side==1 else quote.bid
    if plan.side*(executable-plan.worst_entry_ticks)>0:raise ContractError("decision quote exceeds frozen entry bound")
    entry_at=plan.decision_at+timing.outbound_ns
    if entry_at>=min(plan.horizon_end,plan.flatten_send_at):raise ContractError("intent expires before modeled venue arrival")
    entry=path.marketable(order_id=plan.id+':entry',side=plan.side,arrival_at=entry_at,scenario=fill_scenario)
    events=[{'kind':'entry_sent','at':plan.decision_at,'plan':plan.version},{'kind':entry.status,'at':entry.at,'price':entry.price_ticks}]
    def finish(exit=None,reason='uncertain_entry',unprotected=None):
        paid=fees.fee(terms.root,sides=2 if exit and exit.quantity else 1) if entry.quantity else Decimal(0)
        if not exit or not exit.quantity:
            return BracketOutcome(plan.version,entry,exit,reason,None,None,paid,None,None,None,False,unprotected,tuple(events),digest(timing),False)
        gross=terms.pnl(Ticks(entry.price_ticks),Ticks(exit.price_ticks),side=plan.side).value;net=sum_usd(gross,negative(paid))
        marks=[sum_usd(prior_day_net,negative(fees.fee(terms.root))),sum_usd(prior_day_net,net)]
        observed=path.covered(entry.at,exit.at)
        standing,standing_reason=path.quote_at(entry.at,clock='venue',same_time_ordering=fill_scenario.same_time_ordering)
        if standing is None:
            observed=False
        else:
            liquidation=standing.bid if plan.side==1 else standing.ask
            marks.append(sum_usd(prior_day_net,terms.pnl(Ticks(entry.price_ticks),Ticks(liquidation),side=plan.side).value,
                                 negative(fees.fee(terms.root))))
        for q in path.quote_range(entry.at,exit.at):
            if entry.at<=q.event_at<=exit.at:
                if not q.executable:observed=False;continue
                liquidation=q.bid if plan.side==1 else q.ask
                marks.append(sum_usd(prior_day_net,terms.pnl(Ticks(entry.price_ticks),Ticks(liquidation),side=plan.side).value,negative(fees.fee(terms.root))))
        minimum=min(marks)
        return BracketOutcome(plan.version,entry,exit,reason,exit.at+timing.broker_report_ns,gross,paid,net,minimum,minimum<=negative(daily_budget) if observed else None,
                              exit.at+timing.broker_report_ns<=plan.required_flat_at,unprotected,tuple(events),digest(timing),observed)
    if not entry.quantity:return finish()
    entry_known=entry.at+timing.broker_report_ns
    local_exit=min(plan.horizon_end,plan.flatten_send_at);reason='deadline' if plan.horizon_end<=plan.flatten_send_at else 'boundary'
    # Check the currently visible standing quote on entry confirmation, then each
    # later publication. A stale older revision does not replace a newer quote.
    cuts=sorted({entry_known,*(q.known_at for q in path.quote_range(entry_known,local_exit,clock='strategy') if q.known_at<local_exit)})
    for cut in cuts:
        if cut>=local_exit:break
        q,_=path.quote_at(cut,clock='strategy')
        if q and plan.side*((q.bid if plan.side==1 else q.ask)-plan.target_ticks)>=0:
            local_exit=cut;reason='target';break
    cancel_at=local_exit+timing.outbound_ns
    stop=None
    for t in path.trade_range(entry.at,cancel_at):
        if plan.side*(t.ticks-plan.stop_ticks)>0:continue
        if t.event_at==entry.at and fill_scenario.same_time_ordering=='ambiguous':
            events.append({'kind':'entry_stop_ordering_ambiguous','at':t.event_at});return finish(reason='uncertain_entry_stop_order')
        if t.event_at==entry.at and fill_scenario.same_time_ordering=='venue_first':continue
        if t.event_at==cancel_at:
            if timing.cancellation_tie=='ambiguous':
                events.append({'kind':'cancel_trigger_race_ambiguous','at':t.event_at});return finish(reason='uncertain_cancel_stop_race')
            if timing.cancellation_tie=='cancel_first':continue
        stop=t;break
    if stop is not None:
        events.append({'kind':'native_stop_triggered','at':stop.event_at,'source':stop.id})
        closing=path.marketable(order_id=plan.id+':stop',side=-plan.side,arrival_at=stop.event_at+timing.native_stop_delay_ns,scenario=fill_scenario)
        events.append({'kind':closing.status,'at':closing.at,'price':closing.price_ticks})
        return finish(closing,'stop')
    events.extend(({'kind':'stop_cancel_sent','at':local_exit,'cause':reason},{'kind':'stop_cancel_effective_under_scenario','at':cancel_at}))
    if not path.covered(entry.at,cancel_at):return finish(reason='uncertain_stop_during_unobserved_interval')
    reconciled_at=cancel_at+timing.broker_report_ns
    exit_at=reconciled_at+timing.outbound_ns
    events.append({'kind':'broker_cancel_and_position_reconciled_under_scenario','at':reconciled_at})
    closing=path.marketable(order_id=plan.id+':full-exit',side=-plan.side,arrival_at=exit_at,scenario=fill_scenario)
    events.append({'kind':closing.status,'at':closing.at,'price':closing.price_ticks})
    return finish(closing,reason,(cancel_at,exit_at))


@dataclass(frozen=True)
class InSetAction:
    id:str
    decision_at:int
    known_flat_at:int
    net:Fraction
    minimum_incremental_mark:Fraction
    required_reserve:Fraction


def exact_static_day_oracle(actions:tuple[InSetAction,...],*,daily_budget:Fraction,maximum_actions:int=10000):
    """Exact foresight upper result ONLY for these fixed outcomes/static rules.

    Higher completed cash dominates at each decision cut for a static day-start
    floor. Trailing-firm floors, business rules and shared scarce-fill changes are
    excluded; they require a larger state and a separately proven algorithm.
    """
    if len(actions)>maximum_actions or len({a.id for a in actions})!=len(actions) or daily_budget<=0:raise ContractError("oracle requires bounded unique finite action set and a static loss budget")
    if any(a.known_flat_at<=a.decision_at or a.required_reserve<0 for a in actions):raise ContractError("invalid occupancy/risk action interval")
    states=[(None,Fraction(0),())]
    for action in sorted(actions,key=lambda a:(a.decision_at,a.id)):
        predecessors=[s for s in states if s[0] is None or s[0]<=action.decision_at]
        best=max(predecessors,key=lambda s:s[1])
        if action.required_reserve>daily_budget+best[1] or best[1]+action.minimum_incremental_mark<=-daily_budget:continue
        states.append((action.known_flat_at,best[1]+action.net,(*best[2],action.id)))
    best=max(states,key=lambda s:s[1])
    return {'best_net':best[1],'selected_actions':best[2],'set_hash':digest(actions),'exact_for_declared_set':True,
            'live_attainable':False,'interpretation':'Foresight optimum for this fixed finite action set, static daily floor, fixed full paths and one-position occupancy only.'}
