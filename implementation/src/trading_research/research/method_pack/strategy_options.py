"""QQQ quote/OI gamma model with explicit causal availability and inventory sign.

No option trades, author labels or realized strategy outcomes fit this model.
"""
from collections import defaultdict
from datetime import date,datetime,timedelta,timezone
from functools import lru_cache
from math import erf,exp,log,sqrt,pi
from pathlib import Path
from decimal import Decimal as D
import pyarrow as pa
import pyarrow.parquet as pq
from .empirical_protocol import content_hash
from .event_time import MINUTE,SECOND
from .strategy_policy import POLICY


def bs_price(spot,strike,years,vol,call):
    if years<=0:return max(0,spot-strike if call else strike-spot)
    scale=vol*sqrt(years);d1=(log(spot/strike)+scale*scale/2)/scale;d2=d1-scale
    cdf=lambda x:(1+erf(x/sqrt(2)))/2
    return spot*cdf(d1)-strike*cdf(d2) if call else strike*cdf(-d2)-spot*cdf(-d1)


def implied_vol(spot,strike,years,mid,call):
    if min(spot,strike,years,mid)<=0 or mid<=max(0,spot-strike if call else strike-spot):return None
    lo,hi=.005,5.
    if not bs_price(spot,strike,years,lo,call)<=mid<=bs_price(spot,strike,years,hi,call):return None
    for _ in range(48):
        v=(lo+hi)/2
        if bs_price(spot,strike,years,v,call)<mid:lo=v
        else:hi=v
    return (lo+hi)/2


def unit_gamma(spot,strike,years,vol):
    scale=vol*sqrt(years);d1=(log(spot/strike)+scale*scale/2)/scale
    return exp(-d1*d1/2)/(sqrt(2*pi)*spot*scale)


@lru_cache(maxsize=32)
def option_rows(path):
    table=pq.read_table(path)
    table=table.set_column(table.schema.get_field_index('ts_event'),'ts_event',table['ts_event'].cast(pa.int64()))
    return table.to_pylist()


@lru_cache(maxsize=16)
def spot_rows(path,day):
    from .clocks import et_ns
    d=date.fromisoformat(day);lo=et_ns(d,9,30)//1_000_000;hi=et_ns(d,16,0)//1_000_000
    return pq.read_table(path,filters=[('t','>=',lo),('t','<',hi)],columns=['t','c']).to_pylist()


def build_gamma(quotes,oi_rows,spot,at,day):
    """Pure calculation; ignores future quotes and same-day OI by construction."""
    latest={}
    for r in quotes:
        known=r['ts_event']+MINUTE
        if known>at or at-known>POLICY['gamma']['max_quote_age_seconds']*SECOND:continue
        if r['expiration']<day or r['bid']<=0 or r['ask']<r['bid'] or r['bid_size']<=0 or r['ask_size']<=0:continue
        key=r['osi_symbol']
        if key not in latest or latest[key]['ts_event']<r['ts_event']:latest[key]=r
    expiries=sorted({r['expiration'] for r in latest.values()})
    if not expiries:return {'available':False,'reason':'no valid causal option quotes','known_at':at}
    expiry=expiries[0]
    oi={}
    for r in oi_rows:
        if r['request_date']>=day or r['ts_event']>at:continue
        key=r['osi_symbol']
        if key not in oi or oi[key]['ts_event']<r['ts_event']:oi[key]=r
    from .clocks import et_ns
    years=(et_ns(expiry,16,0)-at)/(365.25*86400*SECOND)
    nodes=defaultdict(float);contracts=[];rejected=defaultdict(int)
    for r in latest.values():
        if r['expiration']!=expiry:continue
        interest=oi.get(r['osi_symbol'])
        if not interest or interest['open_interest']<=0:rejected['missing_or_zero_prior_oi']+=1;continue
        call=r['right']=='CALL';mid=(r['bid']+r['ask'])/2
        vol=implied_vol(spot,r['strike'],years,mid,call)
        if vol is None:rejected['invalid_implied_vol']+=1;continue
        gamma=unit_gamma(spot,r['strike'],years,vol)*interest['open_interest']*100*spot*spot*.01*(1 if call else -1)
        nodes[r['strike']]+=gamma
        contracts.append({'osi_symbol':r['osi_symbol'],'strike':r['strike'],'right':r['right'],'iv':vol,'oi':interest['open_interest'],
            'quote_known_at':r['ts_event']+MINUTE,'oi_known_at':interest['ts_event'],'oi_date':str(interest['request_date']),
            'signed_gamma_per_1pct':gamma,'years':years})
    if not contracts:return {'available':False,'reason':'no eligible quote/prior-OI contracts','known_at':at,'rejected':dict(rejected)}
    # Reprice frozen IV/OI on a fixed spot grid; choose nearest sign crossing.
    def net_at(price):
        return sum(unit_gamma(price,r['strike'],r['years'],r['iv'])*r['oi']*100*price*price*.01*(1 if r['right']=='CALL' else -1) for r in contracts)
    grid=[spot*(.9+i*.002) for i in range(101)];flips=[]
    for left,right in zip(grid,grid[1:]):
        gl,gr=net_at(left),net_at(right)
        if gl*gr<0:
            for _ in range(30):
                mid=(left+right)/2;gm=net_at(mid)
                if gl*gm<=0:right=mid
                else:left=mid;gl=gm
            flips.append((left+right)/2)
    # Both rights are needed to decide an aggregate signed inventory regime.
    complete_sides={r['right'] for r in contracts}=={'CALL','PUT'}
    total=sum(nodes.values());key=min(nodes,key=lambda strike:(-abs(nodes[strike]),strike))
    calls=[r for r in contracts if r['right']=='CALL' and r['strike']>=spot]
    puts=[r for r in contracts if r['right']=='PUT' and r['strike']<=spot]
    wall=lambda rows:None if not rows else max(rows,key=lambda r:abs(r['signed_gamma_per_1pct']))['strike']
    return {'available':True,'model':'QQQ-prior-OI-signed-gamma-v1','known_at':at,'spot':spot,'expiry':str(expiry),
        'expiry_kind':'0DTE' if expiry==day else 'front_expiry_approximation','regime':None if not complete_sides else 'long' if total>0 else 'short' if total<0 else 'neutral',
        'gamma_flips':flips,'nearest_gamma_flip':min(flips,key=lambda px:abs(px-spot)) if flips else None,
        'aggregate_signed_gamma_per_1pct':total,'key_strike':key,'call_wall':wall(calls),'put_wall':wall(puts),
        'nodes':[{'strike':k,'gamma':v} for k,v in sorted(nodes.items())],'contracts':contracts,'rejected':dict(rejected),
        'source':POLICY['gamma']['source'],'inventory_assumption':POLICY['gamma']['inventory_assumption'],
        'population':'acquired strike-range42 quotes with valid quotes and prior OI; not the full OPRA chain'}


def gamma_at(m,at):
    cutoff=at//MINUTE*MINUTE
    if not hasattr(m,'_strategy_gamma'):m._strategy_gamma={}
    if cutoff in m._strategy_gamma:return m._strategy_gamma[cutoff]
    root=Path(m.data_root);base=root/'thetadata-opra'
    qpath=base/'opra__qqq-options__quote-1m__dte14__strike-range42'/f'{m.day}.parquet'
    opath=base/'opra__qqq-options__open-interest';prior=sorted(p for p in opath.glob('*.parquet') if p.stem<str(m.day))
    spath=root/'quantpad/nasdaq__qqq-etf__ohlcv-1m'/f'{m.day.year}.parquet'
    result={'available':False,'known_at':cutoff,'reason':'quote/prior OI/spot data unavailable'}
    if qpath.exists() and prior and spath.exists():
        # Limit stale carry across closures; no older unrelated inventory selection.
        oi_path=prior[-1]
        spots=[r for r in spot_rows(str(spath),str(m.day)) if r['t']*1_000_000+MINUTE<=cutoff]
        selected=max(spots,key=lambda r:r['t']) if spots else None
        if selected and cutoff-(selected['t']*1_000_000+MINUTE)<=3*MINUTE and (m.day-date.fromisoformat(oi_path.stem)).days<=7:
            result=build_gamma(option_rows(str(qpath)),option_rows(str(oi_path)),selected['c'],cutoff,m.day)
            from .historical_runner import file_digest
            receipts=[{'path':str(p),'sha256':file_digest(p)} for p in (qpath,oi_path,spath)]
            m.input_receipts.extend(r for r in receipts if r not in m.input_receipts)
            result['input_receipts']=receipts;result['spot_known_at']=selected['t']*1_000_000+MINUTE
    result['id']='inferred-gamma:'+content_hash(result)
    m._strategy_gamma[cutoff]=result
    return result


def key_gamma_reference(m):
    # Open's first completed option/spot minute; level then frozen for the day.
    at=m.at('09:32');g=gamma_at(m,at)
    bars=m.bars(at-MINUTE,at)
    if not g['available'] or not bars or bars[-1]['C'] is None:return []
    ratio=bars[-1]['C']/D(str(g['spot']));px=(D(str(g['key_strike']))*ratio/D('.25')).quantize(D('1'))*D('.25')
    prior=m.range(m.start,m.at('09:30'),'KG-context')
    if prior is None:return []
    return [{'id':g['id']+':mapped-key','known_at':at,'low':px-D('.25'),'high':px+D('.25'),
        'inferred_level':True,'model':g,'mapping_ratio':ratio,'complete':True,
        'long_target':max(prior['high'],px+(prior['high']-prior['low'])),
        'short_target':min(prior['low'],px-(prior['high']-prior['low']))}]
