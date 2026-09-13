"""Past-only volume/volatility conditioned projection zones; source-inspired v1."""
from collections import defaultdict
from datetime import date,timedelta,datetime,timezone
from decimal import Decimal as D, ROUND_FLOOR, ROUND_CEILING
from functools import lru_cache
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo
import pyarrow.parquet as pq
from .event_time import MINUTE
from .empirical_protocol import content_hash
from .strategy_policy import POLICY


def quantile(values,q):
    values=sorted(values);n=(len(values)-1)*q;i=int(n)
    return values[i]+(values[min(i+1,len(values)-1)]-values[i])*(n-i)


@lru_cache(maxsize=20)
def training(root,day):
    current=date.fromisoformat(day);begin=current-timedelta(days=1100);groups=defaultdict(list);receipts=[]
    from .historical_runner import file_digest
    for year in range(begin.year,current.year+1):
        path=Path(root)/'quantpad/cme__nq-continuous-futures__ohlcv-1m'/f'{year}.parquet'
        if not path.exists():continue
        lo=int(datetime.combine(begin,datetime.min.time(),timezone.utc).timestamp()*1000)
        hi=int(datetime.combine(current,datetime.min.time(),timezone.utc).timestamp()*1000)
        rows=pq.read_table(path,filters=[('t','>=',lo),('t','<',hi)]).to_pylist()
        receipts.append({'path':str(path),'sha256':file_digest(path)})
        for r in rows:
            at=datetime.fromtimestamp(r['t']/1000,timezone.utc).astimezone(ZoneInfo('America/New_York'))
            if at.date()>=current:continue
            r['minute']=at.hour*60+at.minute;groups[str(at.date())].append(r)
    result={anchor:[] for anchor in POLICY['pzone']['anchors']}
    for day,rows in sorted(groups.items()):
        totals=defaultdict(float)
        for r in rows:totals[r['instrument_id']]+=r['v']
        if not totals:continue
        instrument=max(totals,key=totals.get);rows=[r for r in rows if r['instrument_id']==instrument]
        for anchor in result:
            h,m=map(int,anchor.split(':'));minute=60*h+m
            pre=[r for r in rows if minute-60<=r['minute']<minute]
            post=[r for r in rows if minute<=r['minute']<16*60]
            if len({r['minute'] for r in pre})<54 or len({r['minute'] for r in post})<(960-minute)*.9:continue
            scale=max(r['h'] for r in pre)-min(r['l'] for r in pre)
            if scale<=0:continue
            px=max(pre,key=lambda r:r['t'])['c']
            result[anchor].append({'day':day,'instrument_id':instrument,'up':max(0,max(r['h'] for r in post)-px)/scale,
                'down':max(0,px-min(r['l'] for r in post))/scale,'volume':sum(r['v'] for r in post),
                'known_at':max(r['t'] for r in post)*1_000_000+MINUTE})
    return {anchor:rows[-POLICY['pzone']['lookback_sessions']:] for anchor,rows in result.items()},receipts


def inferred_pzones(m):
    if hasattr(m,'_strategy_pzones'):return m._strategy_pzones
    history,receipts=training(str(m.data_root),str(m.day));m.input_receipts.extend(r for r in receipts if r not in m.input_receipts)
    zones=[];diagnostics=[];cfg=POLICY['pzone']
    for anchor,rows in history.items():
        at=m.at(anchor);bars=m.bars(at-60*MINUTE,at)
        if len(rows)<cfg['minimum_sessions'] or len(bars)<54 or not bars or bars[-1]['C'] is None:
            diagnostics.append({'anchor':anchor,'reason':'insufficient historical population or live anchor input','training_n':len(rows)});continue
        scale=max(r['H'] for r in bars)-min(r['L'] for r in bars)
        if scale<=0:continue
        volume_cut=median(r['volume'] for r in rows);selected=[r for r in rows if r['volume']>=volume_cut]
        if len(selected)<cfg['minimum_sessions']:continue
        price=bars[-1]['C'];identity='inferred-pzone:'+content_hash({'anchor':anchor,'day':str(m.day),'training':rows,'price':price,'scale':scale})
        for direction,side in [('up','short'),('down','long')]:
            distances=[D(str(quantile([r[direction] for r in selected],q)))*scale for q in cfg['quantiles']]
            bounds=sorted([price+d if direction=='up' else price-d for d in distances])
            low=(bounds[0]/D('.25')).to_integral_value(rounding=ROUND_FLOOR)*D('.25')
            high=(bounds[1]/D('.25')).to_integral_value(rounding=ROUND_CEILING)*D('.25')
            if high<=low or low<=price<=high:continue
            zones.append({'id':identity+':'+direction,'known_at':at,'formation_start':at-60*MINUTE,'expires_at':m.end,
                'low':low,'high':high,'side':side,'destination_price':price,'destination_id':identity+':anchor',
                'model':'volume-volatility-quantile-pzone-v1','inferred_zone':True,'training_n':len(rows),'conditioned_n':len(selected),
                'training_max_known_at':max(r['known_at'] for r in selected),'training_sha256':content_hash(rows),
                'volume_cut':volume_cut,'live_scale':scale,'quantiles':cfg['quantiles'],'source':cfg['source'],'input_receipts':receipts})
    m._strategy_pzones=zones;m._strategy_pzone_diagnostics=diagnostics
    return zones
