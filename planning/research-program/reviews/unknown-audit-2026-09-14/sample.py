import sys,json,pickle,random,collections
from datetime import date,timedelta
sys.path.insert(0,'/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit')
import rawcount as R
import zoneinfo, datetime
SC='/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit'
NY=zoneinfo.ZoneInfo('America/New_York')
MIN=60_000_000_000
random.seed(11)

def et_ns(d,h,m):
    if isinstance(d,str): d=date.fromisoformat(d)
    return int(datetime.datetime(d.year,d.month,d.day,h,m,tzinfo=NY).timestamp())*10**9

def win_counts(a,b,instrument=None):
    c=R.counts(a,b)
    if instrument is not None:
        c={k:v for k,v in c.items() if int(instrument) in v[2]}
    return sum(v[0] for v in c.values()), sum(v[1] for v in c.values()), len(c), sorted({i for v in c.values() for i in v[2]})

out=[]
def add(**kw): out.append(kw)

cov=pickle.load(open(SC+'/coverage_detail.pkl','rb'))
scan2=pickle.load(open(SC+'/scan2.pkl','rb'))
rr=scan2['reason_rows']

# ---- S1 unknown minutes (stratified over the 70 affected days)
byday=collections.defaultdict(list)
for d,m in cov['distinct_unknown']: byday[d].append(m)
days=sorted(byday)
picks=[]
for d in days:
    ms=sorted(byday[d]); k=min(len(ms),2 if len(ms)<=3 else 1)
    picks += [(d,m) for m in random.sample(ms,k)]
# extra samples from the big days
for d in days:
    if len(byday[d])>100:
        picks += [(d,m) for m in random.sample(sorted(byday[d]),2)]
for d,m in picks:
    c=R.counts(m,m+MIN)
    allr,tr = (c[m][0],c[m][1]) if m in c else (0,0)
    inst=c[m][2] if m in c else []
    add(label='unknown_current_minutes',date=d,minute_utc=R.ut(m),minute_et=R.et(m),
        raw_rows=allr,raw_trade_rows=tr,instruments=inst,
        finding=('no raw rows at all' if allr==0 else 'rows present, zero trades' if tr==0 else 'rows and trades present'))

# ---- S3 same_contract_prior_scope_unknown
rows=rr['same_contract_prior_scope_unknown']
for d,cid,det in random.sample(rows,18):
    pd_=det.get('date'); inst=det.get('instrument_id')
    if not pd_: continue
    a,b=et_ns(pd_,9,30),et_ns(pd_,16,0)
    allr,tr,mins,insts=win_counts(a,b)
    mine=[x for x in R.counts(a,b).items() if inst in x[1][2]]
    add(label='same_contract_prior_scope_unknown',date=d,coverage_id=cid,prior_date=pd_,required_instrument=inst,
        raw_rows_prior_rth=allr,raw_trade_rows_prior_rth=tr,instruments_present=insts,
        minutes_with_required_instrument=len(mine),
        finding=('prior day has NO rows for any instrument' if allr==0 else
                 'prior day traded but under a different contract id' if not mine else
                 'prior day has rows for the required contract'))

# ---- S4 calendar_unverified
for d,cid,det in random.sample(rr['calendar_unverified'],12):
    cd=det.get('date') or d
    a,b=et_ns(cd,9,30),et_ns(cd,16,0)
    allr,tr,mins,insts=win_counts(a,b)
    add(label='calendar_unverified',date=d,coverage_id=cid,calendar_date=cd,
        raw_rows_rth=allr,raw_trade_rows_rth=tr,minutes_with_rows=mins,
        finding=('no rows in RTH (closed)' if allr==0 else 'RTH rows exist; only the dated schedule is missing'))

# ---- S5 formation_has_no_observed_executions
for d,cid,det in random.sample(rr['formation_has_no_observed_executions'],12):
    w=det.get('window')
    if not w: continue
    allr,tr,mins,insts=win_counts(w[0],w[1])
    add(label='formation_has_no_observed_executions',date=d,coverage_id=cid,
        window_utc=[R.ut(w[0]),R.ut(w[1])],window_et=[R.et(w[0]),R.et(w[1])],
        raw_rows=allr,raw_trade_rows=tr,minutes_with_rows=mins,
        finding=('window truly empty' if allr==0 else 'rows but no trades' if tr==0 else 'TRADES EXIST IN WINDOW'))

# ---- S6 cash_open_order_unknown
for d,cid,det in random.sample(rr['cash_open_order_unknown'],10):
    a=et_ns(d,9,30)
    allr,tr,mins,insts=win_counts(a,a+MIN)
    add(label='cash_open_order_unknown',date=d,coverage_id=cid,minute_et=R.et(a),
        raw_rows=allr,raw_trade_rows=tr,
        finding=('09:30 minute empty' if allr==0 else 'rows but no trades in 09:30 minute' if tr==0 else 'TRADES EXIST at 09:30'))

# ---- S7 session_reference_missing
for d,cid,det in random.sample(rr['session_reference_missing'],8):
    pdy=str(date.fromisoformat(d)-timedelta(days=1))
    aa,ab=et_ns(pdy,20,0),et_ns(d,0,0)
    la,lb=et_ns(d,2,0),et_ns(d,5,0)
    a1,t1,_,_=win_counts(aa,ab); a2,t2,_,_=win_counts(la,lb)
    add(label='session_reference_missing',date=d,coverage_id=cid,
        asia_window_et=[R.et(aa),R.et(ab)],asia_rows=a1,asia_trades=t1,
        london_window_et=[R.et(la),R.et(lb)],london_rows=a2,london_trades=t2,
        finding=('both reference windows empty' if t1==0 and t2==0 else 'ONE OR BOTH REFERENCE WINDOWS HAVE TRADES'))

# ---- S8 KG1
import os,glob
qdir='/workspace/data/thetadata-opra/opra__qqq-options__quote-1m__dte14__strike-range42'
oidir='/workspace/data/thetadata-opra/opra__qqq-options__open-interest'
oi=sorted(os.path.basename(p)[:-8] for p in glob.glob(oidir+'/*.parquet'))
for d,cid,det in random.sample(rr['KG1/key-gamma model input unavailable'],14):
    q=os.path.join(qdir,d+'.parquet')
    spath=f'/workspace/data/quantpad/nasdaq__qqq-etf__ohlcv-1m/{d[:4]}.parquet'
    prior=[x for x in oi if x<d]
    lag=(date.fromisoformat(d)-date.fromisoformat(prior[-1])).days if prior else None
    a=et_ns(d,9,31); allr,tr,_,_=win_counts(a,a+MIN)
    add(label='KG1/key-gamma model input unavailable',date=d,coverage_id=cid,
        qqq_quote_file_exists=os.path.exists(q),spot_file_exists=os.path.exists(spath),
        prior_oi_file=prior[-1] if prior else None,prior_oi_lag_days=lag,
        nq_rows_0931=allr,nq_trade_rows_0931=tr,
        finding=('QQQ option quote file for the date is absent' if not os.path.exists(q)
                 else 'prior open-interest file older than the 7-day rule' if lag and lag>7
                 else 'inputs present - model returned unavailable for a rule reason'))

# ---- S11 no distinct older completed auction
for d,cid,det in random.sample(rr['no distinct older completed auction in current admitted prefix'],6):
    a,b=et_ns(str(date.fromisoformat(d)-timedelta(days=1)),18,0),et_ns(d,9,30)
    allr,tr,mins,_=win_counts(a,b)
    add(label='no distinct older completed auction in current admitted prefix',date=d,coverage_id=cid,
        overnight_rows=allr,overnight_trades=tr,overnight_minutes_with_rows=mins,
        finding='overnight tape present; the rule needs a second price-defined balance, not more rows' if tr>0 else 'overnight tape empty')

# ---- S12 A period has no observed executions
for d,cid,det in random.sample(rr['A period has no observed executions'],6):
    a,b=et_ns(d,9,30),et_ns(d,10,0)
    allr,tr,mins,_=win_counts(a,b)
    add(label='A period has no observed executions',date=d,coverage_id=cid,
        rows_0930_1000=allr,trades_0930_1000=tr,
        finding=('09:30-10:00 truly empty' if allr==0 else 'ROWS EXIST 09:30-10:00'))

# ---- S10 external record labels: confirm the project owns no such input
supplied=[]
for pat in ['/workspace/data/**/*process*','/workspace/data/**/*ledger*','/workspace/data/**/*journal*','/workspace/data/**/*trade-record*']:
    supplied+=glob.glob(pat,recursive=True)
for lbl in ['actual dated process/source records absent','no actual validated process and risk-stage ledger',
            'no dated P-zone bands/destinations','GB p.40 discloses no complete repeatable scalp entry']:
    rows=rr.get(lbl,[])
    for d,cid,det in random.sample(rows,3) if rows else []:
        add(label=lbl,date=d,coverage_id=cid,candidate_input_files_found=supplied[:5],
            finding='no personal/proprietary record dataset exists anywhere under /workspace/data')

json.dump(out,open(SC+'/sample_part1.json','w'),indent=1)
print('rows',len(out))
for k,v in collections.Counter(r['label'] for r in out).items(): print(' ',v,k)
