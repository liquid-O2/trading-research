import json,gzip,glob,os,collections
BASE='/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation'
out=[]
for p in sorted(glob.glob(BASE+'/*/*.json.gz')):
    d=json.load(gzip.open(p))
    mend=None
    for ep in d.get('episodes',[]):
        sa=ep.get('strategy_assessment') or {}
        if not(sa.get('scope')=='entry_setup' and sa.get('status')=='no_setup'):continue
        g=ep.get('geometry') or {}
        ref=ep.get('reference') or {}
        rec=dict(
            date=os.path.basename(os.path.dirname(p)),
            method=ep.get('method'), branch=ep.get('branch'),
            cid=ep.get('candidate_id'), decision_at=ep.get('decision_at'),
            occurrence_at=ep.get('occurrence_at'),
            failed=sa.get('failed_conditions'), unavail=sa.get('unavailable_conditions'),
            values=ep.get('values'), side=ep.get('side'),
            stages=[{'s':s['stage'],'o':s['observed'],'at':s['at']} for s in (ep.get('stages') or [])],
            ref={k:ref.get(k) for k in ('id','low','high','known_at','start','end','close','open','complete')},
            local_flow=g.get('local_flow'),
            control_search_window=g.get('control_search_window'),
            control_bars=[{'bar_id':b.get('bar_id'),'O':b.get('O'),'C':b.get('C'),'delta':b.get('delta')} for b in (g.get('control_bars') or [])],
            confirmation_bar={k:(g.get('confirmation_bar') or {}).get(k) for k in ('bar_id','O','H','L','C','observed_complete','start','end')} if g.get('confirmation_bar') else None,
            geom_keys=sorted(g.keys()),
        )
        out.append(rec)
json.dump(out, open(os.environ['SCRATCH']+'/sampleA.json','w'))
print(len(out))
