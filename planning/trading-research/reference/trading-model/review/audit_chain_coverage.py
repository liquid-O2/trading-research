"""Bounded capability audit: three dates, six chain families, one quote instant per day. No model/backtest."""
from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd,json,time
p=Path('/workspace/data/thetadata-opra');out=Path('/workspace/planning/trading-model/review/data-audit');res=[];start=time.time()
for day in ['2020-01-02','2023-05-02','2026-09-02']:
 at=pd.Timestamp(day+'T15:00:00Z')
 for sym in ['ndx','ndxp','qqq','spx','spxw','spy']:
  rec={'symbol':sym,'date':day,'quote_at':str(at),'scope':'All contract/OI rows for selected date, quote rows exactly at15:00UTC; not historical listed-universe certification.'}
  cp=p/f'opra__{sym}-options__contracts/{day}.parquet';op=p/f'opra__{sym}-options__open-interest/{day}.parquet'
  if not cp.exists():rec['missing_contracts']=True;res.append(rec);continue
  c=pq.read_table(cp,columns=['osi_symbol','expiration']).to_pandas().drop_duplicates('osi_symbol');c['dte']=(pd.to_datetime(c.expiration)-pd.Timestamp(day)).dt.days
  o=pq.read_table(op,columns=['osi_symbol','open_interest','ts_event']).to_pandas() if op.exists() else pd.DataFrame(columns=['osi_symbol','open_interest','ts_event'])
  rec['oi_rows']=len(o);rec['oi_future_rows']=int((o.ts_event>at).sum());o=o[o.ts_event<=at].sort_values('ts_event').drop_duplicates('osi_symbol',keep='last')
  qlist=[];rec['quote_files']=[];rec['missing_quote_files']=[]
  paths=[d/f'{day}.parquet' for d in p.glob(f'opra__{sym}-options__quote-1m*') if 'legacy' not in d.name]
  for qp in paths:
   if not qp.exists():rec['missing_quote_files'].append(str(qp.relative_to(p)));continue
   q=pq.read_table(qp,columns=['osi_symbol','ts_event','bid','ask','bid_size','ask_size'],filters=[('ts_event','=',at.to_pydatetime())]).to_pandas();rec['quote_files'].append({'file':str(qp.relative_to(p)),'snapshot_rows':len(q)})
   qlist.append(q)
  q=pd.concat(qlist,ignore_index=True) if qlist else pd.DataFrame(columns=['osi_symbol','bid','ask','bid_size','ask_size'])
  rec['quote_duplicate_contract_rows']=int(q.osi_symbol.duplicated().sum());seen=set(q.osi_symbol);valid=set(q.loc[(q.bid>0)&(q.ask>=q.bid)&(q.bid_size>0)&(q.ask_size>0),'osi_symbol'])
  j=c.merge(o[['osi_symbol','open_interest']],how='left',on='osi_symbol');j['quoted']=j.osi_symbol.isin(seen);j['valid_quote']=j.osi_symbol.isin(valid)
  rec['bands']=[]
  for label,lo,hi in [('0dte',0,0),('1-7',1,7),('8-14',8,14),('15-30',15,30),('31-60',31,60),('61+',61,10000)]:
   x=j[(j.dte>=lo)&(j.dte<=hi)];den=x.open_interest.sum();rec['bands'].append({'dte':label,'contracts':len(x),'oi_known_contracts':int(x.open_interest.notna().sum()),'oi_sum':int(den),'quoted_contracts':int(x.quoted.sum()),'valid_quote_contracts':int(x.valid_quote.sum()),'valid_quote_oi_fraction':float(x.loc[x.valid_quote,'open_interest'].sum()/den) if den else None})
  res.append(rec);print(day,sym,'contracts',len(c),'quote',len(seen),flush=True)
(out/'chain-snapshot-coverage.json').write_text(json.dumps(res,indent=2));print('DONE',time.time()-start,flush=True)
