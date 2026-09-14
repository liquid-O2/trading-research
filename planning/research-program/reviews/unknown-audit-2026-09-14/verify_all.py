import sys,json,pickle,collections,random
sys.path.insert(0,'/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit')
sys.path.insert(0,'/workspace/implementation/src')
import rawcount as R
from datetime import date,datetime,timedelta
import zoneinfo
NY=zoneinfo.ZoneInfo('America/New_York'); MIN=60_000_000_000
SC='/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit'
random.seed(7)
def et_ns(d,h,m):
    if isinstance(d,str): d=date.fromisoformat(d)
    return int(datetime(d.year,d.month,d.day,h,m,tzinfo=NY).timestamp())*10**9
from trading_research.research.method_pack.event_cache import contract_at
from trading_research.research.method_pack.session_policy import ReconstructionSessionPolicy
pol=ReconstructionSessionPolicy()

cov=pickle.load(open(SC+'/coverage_detail.pkl','rb'))
byday=collections.defaultdict(list)
for d,m in cov['distinct_unknown']: byday[d].append(m)

# ---------- A. full verification of every distinct unknown minute ----------
res=collections.Counter(); per_day={}
detail=[]
for d in sorted(byday):
    ms=sorted(byday[d])
    c=R.counts(ms[0],ms[-1]+MIN)
    inst=str(contract_at('/workspace/data',et_ns(d,9,30))['instrument_id'])
    cnt=collections.Counter()
    for m in ms:
        v=c.get(m)
        if v is None: k='no_raw_rows'
        elif v[1]==0: k='rows_but_no_trades'
        elif inst not in [str(x) for x in v[2]]: k='trades_other_contract_only'
        else: k='trades_for_this_contract'
        cnt[k]+=1; res[k]+=1
        if k=='trades_for_this_contract':
            detail.append({'date':d,'minute_utc':R.ut(m),'minute_et':R.et(m),'rows':v[0],'trades':v[1]})
    per_day[d]=dict(cnt)
json.dump({'totals':dict(res),'per_day':per_day,'minutes_with_trades':detail},open(SC+'/unknown_minute_full.json','w'),indent=1)
print('FULL UNKNOWN-MINUTE VERIFICATION',dict(res))

# ---------- B. reverse check: 30 heaviest, 30 zero ----------
heavy=sorted(per_day.items(),key=lambda x:-sum(x[1].values()))[:30]
rev=[]
for d,cnt in heavy:
    rev.append({'kind':'largest_unknown','date':d,'unknown_minutes':sum(cnt.values()),**cnt})
alldays=sorted({x[0] for x in []} )
# zero-unknown sessions
import json as J
pop=J.load(open('/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/MEASUREMENT_RESULTS.json'))['population']['evaluation_dates']
zero=[d for d in pop if d not in byday]
pick=[zero[i] for i in sorted(random.sample(range(len(zero)),30))]
for d in pick:
    a,b=et_ns(str(date.fromisoformat(d)-timedelta(days=1)),18,0),et_ns(d,16,0)
    inst=str(contract_at('/workspace/data',et_ns(d,9,30))['instrument_id'])
    c=R.counts(a,b)
    total=(b-a)//MIN; withtrades=0; rowsnotrade=0; empty=0; closure=0
    for i in range(total):
        m=a+i*MIN; v=c.get(m)
        sched = pol.state(m,m+MIN)=='scheduled_closure'
        if v and v[1]>0 and inst in [str(x) for x in v[2]]: withtrades+=1
        elif sched: closure+=1
        elif v: rowsnotrade+=1
        else: empty+=1
    rev.append({'kind':'zero_unknown','date':d,'prefix_minutes':total,'minutes_with_trades':withtrades,
                'scheduled_closure_minutes':closure,'silent_minutes_rows_no_trade':rowsnotrade,'silent_minutes_no_rows':empty})
json.dump(rev,open(SC+'/reverse_check.json','w'),indent=1)
print('reverse rows',len(rev))
for r in rev:
    if r['kind']=='zero_unknown': print(r)
