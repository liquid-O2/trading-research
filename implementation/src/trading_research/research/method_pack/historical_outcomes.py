"""Separate post-sequence observations; these are never actual trades or fills."""
from decimal import Decimal
from .historical_features import SECOND, MINUTE
from .historical_flow import batches
from .branch_coverage import setting


def observe_outcome(market, episode):
    geometry=episode.get('geometry',{})
    entry,stop,target=(geometry.get(k) for k in ('entry','stop','target'))
    result={'schema':'phase1-post-sequence-observation-v2','candidate_id':episode['candidate_id'],
        'actual_trade':False,'cost_or_fill_model':False,'sequence_verdict':episode['research_verdict'],
        'result':'not_applicable','resolved_at':None,'event_ids':[]}
    if episode['research_verdict']!='pass' or any(v is None for v in (entry,stop,target)):
        return result
    entry,stop,target=map(lambda v:Decimal(str(v)),(entry,stop,target))
    side=episode['side'];sg=1 if side=='long' else -1
    if sg*(entry-stop)<=0 or sg*(target-entry)<=0:
        raise ValueError('accepted sequence has invalid preselected outcome geometry')
    start=episode['decision_at'];end=min(market.end,start+setting('outcomes')['horizon_minutes']*MINUTE)
    if episode['method']=='JJ-TBR' and episode['branch']=='judas_outbound':
        end=min(end,market.at(setting('tbr_sessions')['outbound_end']))
    result.update(start_ns=start,end_ns=end,entry=entry,stop=stop,target=target,result='unknown')
    if end<=start:return dict(result,reason='no acquired post-sequence window')
    # Use order-independent one-second extrema only to find possible crossing
    # seconds. Resolve the first crossing from the actual whole native batch.
    scan_start=(start//SECOND+1)*SECOND
    spans=[(start,min(scan_start,end))]
    for bar in market.bars(scan_start,end,1):
        if bar['H']>=max(stop,target) or bar['L']<=min(stop,target):
            spans.append((bar['start'],bar['end']))
    for a,b in spans:
        if b<=a:continue
        for at,rows in batches(market.local(a,b)):
            if at<=start:continue
            targets=[r for r in rows if sg*(r['price']-target)>=0]
            stops=[r for r in rows if sg*(r['price']-stop)<=0]
            if not targets and not stops:continue
            result.update(resolved_at=max(r['known_at'] for r in rows),
                event_ids=[r['event_id'] for r in targets+stops],
                result='unknown' if targets and stops else 'target_observed' if targets else 'invalidation_observed',
                reason='same timestamp batch contains both boundaries' if targets and stops else 'first observed native boundary batch')
            # An earlier unknown interval prevents calling this the first
            # boundary in the entire market population, even if observed.
            result['coverage']=market.coverage(start//MINUTE*MINUTE,min(market.end,(at//MINUTE+1)*MINUTE))
            result['population_first_boundary_known']=result['coverage']['observed_scope_complete']
            return result
    result['coverage']=market.coverage(start//MINUTE*MINUTE,min(market.end,((end+MINUTE-1)//MINUTE)*MINUTE))
    result['result']='no_boundary_in_observed_horizon' if result['coverage']['observed_scope_complete'] else 'unknown'
    result['reason']='bounded observed event horizon; no fill or return claim'
    return result
