import sys,json,random,collections
sys.path.insert(0,'/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit')
sys.path.insert(0,'/workspace/implementation/src')
import pyarrow.parquet as pq, pyarrow.compute as pc, pyarrow as pa
import rawcount as R
from datetime import date, datetime, timedelta
import zoneinfo, glob
NY=zoneinfo.ZoneInfo('America/New_York'); MIN=60_000_000_000
SC='/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit'
random.seed(3)
def et_ns(d,h,m):
    if isinstance(d,str): d=date.fromisoformat(d)
    return int(datetime(d.year,d.month,d.day,h,m,tzinfo=NY).timestamp())*10**9
from trading_research.research.method_pack.event_cache import contract_at

def trade_detail(a,b,inst):
    """rows, trades, side histogram for one instrument."""
    n=t=0; sides=collections.Counter()
    for path in R.files_for(a,b):
        f=pq.ParquetFile(path); i=f.schema_arrow.names.index('t')
        for g in range(f.num_row_groups):
            st=f.metadata.row_group(g).column(i).statistics
            if st.max<a or st.min>=b: continue
            for bt in f.iter_batches(batch_size=200000,row_groups=[g],columns=['t','action','side','instrument_id']):
                tt=bt.column(0)
                m=pc.and_(pc.greater_equal(tt,a),pc.less(tt,b))
                m=pc.and_(m,pc.equal(bt.column(3),int(inst)))
                if pc.sum(pc.cast(m,pa.int64())).as_py()==0: continue
                sub=bt.filter(m)
                acts=pc.cast(sub.column(1),pa.string()).to_pylist(); sds=pc.cast(sub.column(2),pa.string()).to_pylist()
                n+=len(acts)
                for aa,ss in zip(acts,sds):
                    if aa=='T': t+=1; sides[ss]+=1
    return n,t,dict(sides)

det=json.load(open(SC+'/unavailable_detail.json'))
byfam=collections.defaultdict(list)
for r in det: byfam[r['coverage_id'].split(':')[0]].append(r)
out=[]
quota={'JETBUNDLE-STATES':10,'GB-FAIL':8,'JJ-TBR':8,'SAINT-AMT':5,'KEANI-OPEN-ABOVE-VALUE':4,'GB-VWAP':3,'SIRES':3,'MEMBER-TWO-REASONS':1}
for fam,k in quota.items():
    rows=byfam[fam]
    for r in random.sample(rows,min(k,len(rows))):
        d=r['date']; inst=contract_at('/workspace/data',et_ns(d,9,30))['instrument_id']
        dec=r['decision_at']
        rec={'label':'candidate_status:data_unavailable','method':fam,'date':d,'coverage_id':r['coverage_id'],
             'decision_at_et':R.et(dec),'instrument_id':inst,
             'unavailable_conditions':r['unavailable_conditions'][:6],
             'active_omissions':r['active_omissions']}
        if fam=='JETBUNDLE-STATES':
            a,b=et_ns(d,9,30),et_ns(d,9,32); p=a-2*MIN
            n1,t1,s1=trade_detail(p,a,inst); n2,t2,s2=trade_detail(a,b,inst)
            rec.update(prior_window_rows=n1,prior_window_trades=t1,prior_sides=s1,
                       current_window_rows=n2,current_window_trades=t2,current_sides=s2)
            rec['finding']=('prior 09:28-09:30 window has no executions' if t1==0 else
                            'current 09:30-09:32 window has no executions' if t2==0 else
                            'both windows have executions with unknown-side prints' if s1.get('N') or s2.get('N') else
                            'both windows populated - criterion None for a model rule, not missing rows')
        else:
            a,b=dec-15*MIN,dec+15*MIN
            n,t,s=trade_detail(a,b,inst)
            rec.update(rows_pm15min=n,trades_pm15min=t,sides=s)
            rec['finding']=('no rows around the decision' if n==0 else
                            'rows present, no executions' if t==0 else
                            'raw executions exist around the decision; the None operand comes from a rule')
        out.append(rec)
json.dump(out,open(SC+'/unavail_rawcheck.json','w'),indent=1)
for k,v in collections.Counter((r['method'],r['finding']) for r in out).items(): print(v,k)
