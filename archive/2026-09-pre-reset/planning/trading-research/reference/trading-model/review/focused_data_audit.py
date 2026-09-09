"""Bounded read-only data capability checks, not a trading backtest or production code."""
from pathlib import Path
import json,collections,datetime,time
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np
root=Path('/workspace/data'); out=Path('/workspace/planning/trading-model/review/data-audit');start=time.time()
samples=json.load(open(out/'parquet-samples.json'));results=[]
for r in samples:
 p=pq.ParquetFile(root/r['file']);groups=sorted(set([0,max(0,p.metadata.num_row_groups-1)]));rec={'file':r['file'],'scope':'first up to4096 rows of first and last row group; not random or full file','chunks':[]}
 for g in groups:
  if p.metadata.num_row_groups==0:continue
  b=next(p.iter_batches(batch_size=4096,row_groups=[g],use_threads=False),None)
  if b is None:continue
  d=b.to_pandas();q={'row_group':g,'rows':len(d),'null_counts':{c:int(n) for c,n in d.isna().sum().items() if n}}
  for tc in ['t','ts_event','ts_recv','ts_quote']:
   if tc in d:
    s=d[tc].dropna();q[tc]={'min':str(s.min()),'max':str(s.max()),'adjacent_decreases':int((s.diff().dropna()< (np.timedelta64(0,'ns') if str(s.dtype).startswith('datetime') else 0)).sum()),'ties':int(s.duplicated().sum())}
  for c in ['side','action','stat_type','condition','valid_for_volume','flags']:
   if c in d:q[c]={str(k):int(v) for k,v in d[c].value_counts(dropna=False).items()}
  bp='bid_px' if 'bid_px' in d else 'bid' if 'bid'in d else None;ap='ask_px' if 'ask_px'in d else 'ask' if 'ask'in d else None
  if bp and ap:
   bid=d[bp];ask=d[ap];q['quote_quality']={'crossed':int((bid>ask).sum()),'locked':int((bid==ask).sum()),'zero_side':int(((bid<=0)|(ask<=0)).sum()),'nonfinite':int((~np.isfinite(bid)|~np.isfinite(ask)).sum())}
  if 'ts_event'in d and 'ts_quote'in d:
   lag=(d.ts_event-d.ts_quote).dt.total_seconds();q['quote_lag_seconds']={str(k):float(v) for k,v in lag.quantile([0,.5,.9,.99,1]).items()};q['quote_after_trade']=int((lag<0).sum())
  if 't'in d and 'ts_recv'in d:
   q['receive_before_event']=int((d.ts_recv<d.t).sum())
  if all(c in d for c in ['o','h','l','c']):q['ohlc_invalid']=int(((d.h<d[['o','c','l']].max(axis=1))|(d.l>d[['o','c','h']].min(axis=1))).sum())
  sent={}
  for c in d.select_dtypes(include='number'):
   n=int(((d[c]>=9e18)|(d[c]<=-9e18)).sum())
   if n:sent[c]=n
  q['numeric_extreme_sentinels']=sent
  rec['chunks'].append(q)
 results.append(rec)
(out/'focused-parquet-quality.json').write_text(json.dumps(results,indent=2,default=str));print('Representative quality:',len(results),'files',flush=True)
# Exact one-hour trade-stream reconciliation; row-group bounds restrict disk reads.
def window(rel,lo,hi):
 p=pq.ParquetFile(root/rel);groups=[]
 for g in range(p.metadata.num_row_groups):
  st=p.metadata.row_group(g).column(0).statistics
  if st and st.has_min_max and st.max>=lo and st.min<hi:groups.append(g)
 t=p.read_row_groups(groups,use_threads=False);df=t.to_pandas();return df[(df.t>=lo)&(df.t<hi)].copy(),groups
checks=[]
for sym,mb,td,ts in [('NQ','quantpad/cme__nq-continuous-futures__mbp-1/2021-09.parquet','quantpad/cme__nq-continuous-futures__trades/2021-08-30.parquet','2021-09-01T18:00:00+00:00'),('ES','quantpad/cme__es-continuous-futures__mbp-1/2020-01.parquet','quantpad/cme__es-continuous-futures__trades/2020.parquet','2020-01-01T23:00:00+00:00')]:
 lo=int(datetime.datetime.fromisoformat(ts).timestamp()*1e9);hi=lo+3600*10**9
 m,mg=window(mb,lo,hi);t,tg=window(td,lo,hi);mt=m[m.action=='T'];key=['t','instrument_id','price','size','side','flags'];a=collections.Counter(mt[key].itertuples(index=False,name=None));b=collections.Counter(t[key].itertuples(index=False,name=None))
 checks.append({'symbol':sym,'start':ts,'hours':1,'mbp_file':mb,'trades_file':td,'row_groups_read':[mg,tg],'mbp_rows':len(m),'mbp_trade_rows':len(mt),'trades_rows':len(t),'extra_mbp_trade_records':sum((a-b).values()),'extra_standalone_records':sum((b-a).values()),'mbp_volume':int(mt['size'].sum()),'standalone_volume':int(t['size'].sum()),'mbp_signed_volume':int((mt['size']*mt.side.map({'B':1,'A':-1,'N':0}).astype(float)).sum()),'unknown_side_volume':int(mt.loc[mt.side=='N','size'].sum()),'crossed_book_rows':int((m.bid_px>m.ask_px).sum()),'zero_book_rows':int(((m.bid_px<=0)|(m.ask_px<=0)).sum()),'adjacent_event_time_decreases':int((m.t.diff()<0).sum())})
 print('Reconciled',sym,checks[-1]['mbp_rows'],'rows',flush=True)
(out/'trade-stream-reconciliation.json').write_text(json.dumps(checks,indent=2,default=str));print('DONE seconds',round(time.time()-start,2),flush=True)
