"""Causal, explicitly inferred auction-state and macro context implementations."""
from decimal import Decimal as D
from .event_time import BookObservations, SECOND
from .logic import kleene_and
from .strategy_policy import POLICY


def conjunction(*values):
    result=True
    for value in values:result=kleene_and(result,value)
    return result


def auction_metrics(events,start,end):
    rows=[r for r in events if start<=r['event_ns']<end and r['known_at']<=end]
    trades=[r for r in rows if r['action']=='T' and r['executed_size']>0]
    if not trades:return {'available':False,'start':start,'end':end}
    acc=BookObservations();book=[]
    for row in rows:book.extend(acc.add(row))
    book.extend(acc.finish());book=[r for r in book if not r['bad_book'] and not r['reset'] and r['known_at']<=end]
    def vwap(rs):
        total=sum(r['executed_size'] for r in rs)
        return sum(r['price']*r['executed_size'] for r in rs)/total if total else None
    first=vwap([r for r in trades if r['event_ns']<start+(end-start)//4])
    last=vwap([r for r in trades if r['event_ns']>=end-(end-start)//4])
    lo=min(r['price'] for r in trades);hi=max(r['price'] for r in trades)
    response=None if first is None or last is None else last-first
    buys=sum(r['executed_size'] for r in trades if r['side']=='B');sells=sum(r['executed_size'] for r in trades if r['side']=='A')
    unknown=sum(r['executed_size'] for r in trades if r['side']=='N')
    changes={k:sum(r.get(k) or 0 for r in book) for k in ('bid_added','ask_added','bid_removed','ask_removed')}
    # A lower bound of nonexecution visible removals, not an MBO cancel count.
    removals=changes['bid_removed']+changes['ask_removed']
    withdrawal=max(0,removals-buys-sells-unknown)
    bins=[]
    for i in range(4):
        sample=[r for r in trades if start+i*(end-start)//4<=r['event_ns']<start+(i+1)*(end-start)//4]
        bins.append({r['price'] for r in sample})
    revisit=bool(bins[0]&bins[2] or bins[1]&bins[3])
    return {'available':True,'start':start,'end':end,'buy':buys,'sell':sells,'unknown':unknown,'volume':buys+sells+unknown,
        'first_vwap':first,'last_vwap':last,'response':response,'low':lo,'high':hi,
        'efficiency':None if response is None else abs(response)/max(D('.25'),hi-lo),
        'book_available':bool(book),'withdrawal_estimate':withdrawal,'revisit':revisit,**changes,
        'event_ids':[r['event_id'] for r in rows]}


def auction_criteria(current,previous):
    names={'B':['two_sided_executions','recent_revisits','low_aggression_both_sides'],
      'A':['high_aggression','low_response_efficiency','opposite_liquidity_holds_and_refills'],
      'D':['aggression','efficient_displacement'],
      'E':['prior_absorption_or_effort','replenishment_stops','level_gives_way'],
      'W':['cancellations_dominate']}
    if not current['available'] or not previous['available']:
        return {state:{name:None for name in fields} for state,fields in names.items()}
    c,p=current,previous;cfg=POLICY['auction'];direction_known=c['unknown']==0 and p['unknown']==0
    high=None if not direction_known else max(c['buy'],c['sell'])>=D(str(cfg['high_effort_multiple']))*max(1,p['buy'],p['sell'])
    low=None if not direction_known else c['buy']<=p['buy'] and c['sell']<=p['sell']
    efficiency=c['efficiency'];absorb=None if efficiency is None else efficiency<=D(str(cfg['low_efficiency']))
    drive=None if efficiency is None else efficiency>=D(str(cfg['high_efficiency'])) and abs(c['response'])>=D('.5')
    passive='ask' if c['buy']>=c['sell'] else 'bid'
    held=None if c['response'] is None else (c['response']<=D('.5') if passive=='ask' else c['response']>=D('-.5'))
    refill=None if not c['book_available'] or not direction_known else conjunction(held,c[passive+'_added']>0)
    p_effort=None if p['unknown'] else max(p['buy'],p['sell'])>min(p['buy'],p['sell']) and p['volume']>0
    adds=c['bid_added']+c['ask_added'];oldadds=p['bid_added']+p['ask_added']
    stopped=None if not c['book_available'] or not p['book_available'] else oldadds>0 and adds<=D(str(cfg['replenishment_stop_fraction']))*oldadds
    gives=None if c['last_vwap'] is None else c['last_vwap']>p['high'] or c['last_vwap']<p['low']
    withdrawal=None if not c['book_available'] else c['withdrawal_estimate']>adds+c['volume']
    return {'B':dict(zip(names['B'],[True if c['buy']>0 and c['sell']>0 else None if c['unknown'] else False,c['revisit'],low])),
        'A':dict(zip(names['A'],[high,absorb,refill])), 'D':dict(zip(names['D'],[high,drive])),
        'E':dict(zip(names['E'],[p_effort,stopped,gives])), 'W':{'cancellations_dominate':withdrawal}}


def inferred_auction(m,start,end):
    if not hasattr(m,'_inferred_auction_cache'):m._inferred_auction_cache={}
    key=start,end
    if key in m._inferred_auction_cache:return m._inferred_auction_cache[key]
    duration=end-start
    events=m.local(start-duration,end,book=True)
    prior=auction_metrics(events,start-duration,start);current=auction_metrics(events,start,end)
    criteria=auction_criteria(current,prior)
    result={'known_at':end,'model':'source-reconstruction-auction-v1','criteria':criteria,
        'states':{key:conjunction(*values.values()) for key,values in criteria.items()},
        'current':current,'prior':prior,'source':POLICY['auction']['source'],
        'interpretation':'independent heuristic state tests; no forced label; depth-one withdrawal estimate'}
    m._inferred_auction_cache[key]=result
    return result


def inferred_macro(observations):
    from statistics import mean,stdev
    scores=[]
    for row in observations:
        values=[float(r['value']) for r in row['baseline']]
        current=row['current']
        if current is None or len(values)!=12 or stdev(values)==0:continue
        z=(float(current['value'])-mean(values))/stdev(values)
        scores.append({'series':row['series_id'],'z':z,'signed_z':-z if row['series_id']=='CPIAUCSL' else z,
            'known_at':current['available_at']})
    composite=mean(r['signed_z'] for r in scores) if len(scores)==2 else None
    return {'model':'initial-release-growth-minus-inflation-z-v1','components':scores,'composite':composite,
        'state':None if composite is None else 'growth_supportive' if composite>0 else 'growth_adverse' if composite<0 else 'neutral',
        'source':POLICY['macro']['source'],'is_source_C_score':False}
