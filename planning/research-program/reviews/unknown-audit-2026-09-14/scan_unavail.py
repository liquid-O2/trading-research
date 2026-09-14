import json,gzip,collections,sys
SC='/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/unknown-audit'
s=json.load(open(SC+'/coverage_summary.json'))
rows=s['unavail_rows']
out=[]; cond=collections.Counter(); bybranch=collections.Counter(); byyear=collections.Counter()
for i,(d,cid,n,path) in enumerate(rows):
    doc=json.load(gzip.open('/workspace/'+path if not path.startswith('/') else path))
    for e in doc['episodes']:
        sa=e.get('strategy_assessment') or {}
        if sa.get('status')!='data_unavailable': continue
        uc=sa.get('unavailable_conditions') or []
        lims=[l.get('reason') for l in (e.get('limitations') or [])]
        vals={k:v for k,v in (e.get('values') or {}).items() if v is None}
        out.append({'date':d,'coverage_id':cid,'candidate_id':e['candidate_id'],'decision_at':e['decision_at'],
                    'unavailable_conditions':uc,'limitation_reasons':lims,'none_valued_fields':sorted(vals),
                    'active_omissions':[o.get('reason') for o in doc['session_accounting']['active_omissions']],
                    'unknown_minutes':len(doc['session_accounting']['current_prefix_coverage']['unknown_intervals'])})
        for c in uc: cond[c]+=1
        bybranch[cid]+=1; byyear[d[:4]]+=1
    if i%50==0: print(i,file=sys.stderr,flush=True)
json.dump({'instances':out,'conditions':dict(cond),'by_branch':dict(bybranch),'by_year':dict(byyear)},open(SC+'/unavailable_candidates.json','w'),indent=1)
print('instances',len(out))
print('by branch',bybranch.most_common())
print('by year',sorted(byyear.items()))
print('conditions',cond.most_common(40))
