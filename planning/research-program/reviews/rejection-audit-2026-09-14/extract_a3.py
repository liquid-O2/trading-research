import json,gzip,glob,os
BASE='/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation'
out=[]
for p in sorted(glob.glob(BASE+'/*/*.json.gz')):
    d=json.load(gzip.open(p))
    for ep in d.get('episodes',[]):
        sa=ep.get('strategy_assessment') or {}
        if not(sa.get('scope')=='entry_setup' and sa.get('status')=='no_setup'):continue
        g=ep.get('geometry') or {}; ref=ep.get('reference') or {}; tr=ep.get('trigger') or {}
        out.append(dict(
            date=os.path.basename(os.path.dirname(p)), method=ep.get('method'), branch=ep.get('branch'),
            cid=ep.get('candidate_id'), decision_at=ep.get('decision_at'), occurrence_at=ep.get('occurrence_at'),
            failed=sa.get('failed_conditions'), unavail=sa.get('unavailable_conditions'),
            values=ep.get('values'), side=ep.get('side'),
            stages=[{'s':s['stage'],'o':s['observed'],'at':s['at']} for s in (ep.get('stages') or [])],
            ref={k:ref.get(k) for k in ('id','low','high','known_at','start','end','close','open','complete','width')},
            trig={k:tr.get(k) for k in ('bar_id','id','start','end','known_at','O','H','L','C','delta','at')},
            entry=g.get('entry'), stop=g.get('stop'), target=g.get('target'),
            local_flow=g.get('local_flow'), csw=g.get('control_search_window'),
            nctrl=len(g.get('control_bars') or []),
            older_profile={k:(g.get('older_profile') or {}).get(k) for k in ('val','vah','poc')} if g.get('older_profile') else None,
            htf_poc=(g.get('htf_profile') or {}).get('poc') if g.get('htf_profile') else None,
            mss=g.get('mss_fvg') and {k:g['mss_fvg'].get(k) for k in ('gap','structure')},
            imb_band=g.get('imbalance_band'),
        ))
json.dump(out, open(os.environ['SCRATCH']+'/sampleA.json','w'))
print(len(out))
