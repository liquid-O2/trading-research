import json,gzip,glob,os,collections
BASE='/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation'
out=[]
for p in sorted(glob.glob(BASE+'/*/*.json.gz')):
    d=json.load(gzip.open(p))
    for ep in d.get('episodes',[]):
        sa=ep.get('strategy_assessment') or {}
        if sa.get('scope')=='entry_setup' and sa.get('status')=='no_setup':
            out.append(dict(
                path=p, date=os.path.basename(os.path.dirname(p)),
                method=ep.get('method'), branch=ep.get('branch'),
                candidate_id=ep.get('candidate_id'),
                decision_at=ep.get('decision_at'),
                failed=sa.get('failed_conditions'),
                unavailable=sa.get('unavailable_conditions'),
                unknown=ep.get('unknown'),
                values=ep.get('values'),
                stages=[{'stage':s.get('stage'),'observed':s.get('observed'),'at':s.get('at'),'details':s.get('details')} for s in (ep.get('stages') or [])],
                predicate=ep.get('predicate'),
                side=ep.get('side'),
            ))
print(len(out))
json.dump(out, open(os.environ['SCRATCH']+'/sampleA.json','w'))
c=collections.Counter((o['method'],o['branch']) for o in out)
for k,v in sorted(c.items()): print(k,v)
print('---failed conjunct counts---')
cf=collections.Counter()
for o in out:
    for f in (o['failed'] or []): cf[(o['method'],f)]+=1
for k,v in cf.most_common(): print(v,k)
