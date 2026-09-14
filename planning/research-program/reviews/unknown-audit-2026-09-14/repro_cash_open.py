"""Why GB-FAIL:cash_open_reclaim_case reports cash_open_order_unknown on a day that traded."""
import pyarrow.parquet as pq, pyarrow.compute as pc, pyarrow as pa
from datetime import date, datetime
import zoneinfo, collections, sys
NY=zoneinfo.ZoneInfo('America/New_York')
def et_ns(d,h,m):
    d=date.fromisoformat(d); return int(datetime(d.year,d.month,d.day,h,m,tzinfo=NY).timestamp())*10**9
for day,inst,mon in [('2024-06-03',13743,'2024-06'),('2026-06-02',42004058,'2026-06')]:
    a=et_ns(day,9,30); b=a+60_000_000_000
    p=f'/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1/{mon}.parquet'
    f=pq.ParquetFile(p); i=f.schema_arrow.names.index('t')
    print('columns:',f.schema_arrow.names)
    first_ts=None; first_batch=[]; last_ts=None; last_batch=[]
    for g in range(f.num_row_groups):
        st=f.metadata.row_group(g).column(i).statistics
        if st.max<a or st.min>=b: continue
        for bt in f.iter_batches(batch_size=200000,row_groups=[g],columns=['t','action','price','size','instrument_id']):
            t=bt.column(0)
            m=pc.and_(pc.and_(pc.greater_equal(t,a),pc.less(t,b)),pc.equal(pc.cast(bt.column(1),pa.string()),'T'))
            m=pc.and_(m,pc.equal(bt.column(4),inst))
            if pc.sum(pc.cast(m,pa.int64())).as_py()==0: continue
            for r in bt.filter(m).to_pylist():
                if first_ts is None or r['t']<first_ts: first_ts=r['t']; first_batch=[]
                if r['t']==first_ts: first_batch.append(r)
                if last_ts is None or r['t']>last_ts: last_ts=r['t']; last_batch=[]
                if r['t']==last_ts: last_batch.append(r)
    print(day,'instrument',inst)
    print('  first trade timestamp',first_ts,'rows in that batch',len(first_batch),
          'distinct prices',sorted({r['price'] for r in first_batch}))
    print('  last  trade timestamp',last_ts,'rows in that batch',len(last_batch),
          'distinct prices',sorted({r["price"] for r in last_batch}))
    print('  -> _endpoint() returns None because the batch has >1 price and the acquired')
    print('     MBP-1 schema has no exchange_sequence column to order them:',
          'exchange_sequence' in f.schema_arrow.names)
