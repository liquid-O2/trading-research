import json,gzip,os,glob,random,time
R='/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/jobs/evaluation'
S=os.environ['SCRATCH']
dates=sorted(d for d in os.listdir(R) if d[0].isdigit())
# 40 dates evenly spread across the whole 2020-2026 index
idx=[round(i*(len(dates)-1)/39) for i in range(40)]
picked=[dates[i] for i in idx]
json.dump(picked,open(S+'/sampleB_dates.json','w'))
print(len(set(picked)),picked[0],picked[-1])
pool=[];t=time.time()
for dt in picked:
    for p in sorted(glob.glob(os.path.join(R,dt,'*--branch--*.json.gz'))):
        try:d=json.load(gzip.open(p))
        except Exception as e:print('ERR',p,e);continue
        for ep in d.get('episodes',[]):
            sa=ep.get('strategy_assessment') or {}
            if not(sa.get('scope')=='entry_setup' and sa.get('status')=='no_setup'):continue
            g=ep.get('geometry') or {};ref=ep.get('reference') or {};tr=ep.get('trigger') or {}
            pool.append(dict(date=dt,method=ep['method'],branch=ep['branch'],cid=ep['candidate_id'],
                decision_at=ep['decision_at'],occurrence_at=ep.get('occurrence_at'),
                failed=sa.get('failed_conditions'),unavail=sa.get('unavailable_conditions'),
                values=ep.get('values'),side=ep.get('side'),
                stages=[{'s':s['stage'],'o':s['observed'],'at':s['at']} for s in (ep.get('stages') or [])],
                ref={k:ref.get(k) for k in ('id','low','high','known_at','start','end','close','open','complete','width')},
                trig={k:tr.get(k) for k in ('bar_id','id','start','end','known_at','O','H','L','C','delta','at')},
                entry=g.get('entry'),stop=g.get('stop'),target=g.get('target'),
                local_flow=g.get('local_flow'),csw=g.get('control_search_window'),
                nctrl=len(g.get('control_bars') or []),
                older_profile={k:(g.get('older_profile') or {}).get(k) for k in ('val','vah','poc')} if g.get('older_profile') else None,
                mss=g.get('mss_fvg') and {k:g['mss_fvg'].get(k) for k in ('gap','structure')},
                imb_band=g.get('imbalance_band')))
print('pool',len(pool),'in',round(time.time()-t,1),'s')
json.dump(pool,open(S+'/poolB.json','w'))
