"""Count raw MBP-1 rows per minute directly from /workspace/data parquet files."""
import pyarrow as pa, pyarrow.compute as pc, pyarrow.parquet as pq
from pathlib import Path
from datetime import datetime, timezone
import glob, functools
ROOT='/workspace/data/quantpad/cme__nq-continuous-futures__mbp-1'
MIN=60_000_000_000

@functools.lru_cache(maxsize=None)
def _files():
    out=[]
    for p in sorted(glob.glob(ROOT+'/*.parquet')):
        f=pq.ParquetFile(p); i=f.schema_arrow.names.index('t')
        md=f.metadata
        lo=min(md.row_group(g).column(i).statistics.min for g in range(f.num_row_groups))
        hi=max(md.row_group(g).column(i).statistics.max for g in range(f.num_row_groups))
        out.append((p,lo,hi))
    return out

def files_for(start,end):
    return [p for p,lo,hi in _files() if lo<end and hi>=start]

def counts(start_ns,end_ns,per='minute',instrument=None):
    """Return {minute_start: (all_rows, T_rows, distinct_instruments)} over [start,end)."""
    res={}
    for path in files_for(start_ns,end_ns):
        f=pq.ParquetFile(path); i=f.schema_arrow.names.index('t')
        for g in range(f.num_row_groups):
            st=f.metadata.row_group(g).column(i).statistics
            if st is not None and st.has_min_max and (st.max<start_ns or st.min>=end_ns): continue
            for b in f.iter_batches(batch_size=200000,row_groups=[g],columns=['t','action','instrument_id']):
                t=b.column(0)
                m=pc.and_(pc.greater_equal(t,start_ns),pc.less(t,end_ns))
                if pc.sum(pc.cast(m,pa.int64())).as_py()==0: continue
                b=b.filter(m); t=b.column(0)
                mins=pc.multiply(pc.divide(t,MIN),MIN).to_pylist()
                acts=pc.cast(b.column(1),pa.string()).to_pylist()
                inst=b.column(2).to_pylist()
                for mm,aa,ii in zip(mins,acts,inst):
                    r=res.setdefault(mm,[0,0,set()])
                    r[0]+=1; r[1]+= (aa=='T'); r[2].add(ii)
    return {k:(v[0],v[1],sorted(v[2])) for k,v in res.items()}

def et(ns):
    import zoneinfo
    return datetime.fromtimestamp(ns/1e9,zoneinfo.ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M ET')
def ut(ns):
    return datetime.fromtimestamp(ns/1e9,timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
