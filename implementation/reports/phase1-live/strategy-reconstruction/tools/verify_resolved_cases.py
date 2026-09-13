"""Retain exact lineage for all 51 previously open evaluation entry candidates."""
from pathlib import Path
import argparse,json,gzip
from collections import Counter
from decimal import Decimal as D
from trading_research.research.method_pack.historical_runner import load_registry,read_job,file_digest,immutable_json
from trading_research.research.method_pack.historical_reporting import _table
p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);root=Path(p.parse_args().run_root)
registry,manifest=load_registry(root);base=root.parent
oldpath=base/'development/open-case-forensics-r3.json';old=json.loads(oldpath.read_text())
cases=[r for r in old if r['cohort']=='evaluation' and r['scope']=='entry_setup'];assert len(cases)==51
jobs={};records=[];totals=Counter();open_now=[]
job_paths=sorted((root/'jobs').rglob('*.json.gz'));assert len(job_paths)==776,len(job_paths)
for path in job_paths:
 d=read_job(path)
 jobs[(d['cohort'],d['session_date'],d['method_id'],d['branch'])]=(d,path)
 for e in d['episodes']:
  a=e['strategy_assessment']
  if a['status']=='data_unavailable':open_now.append((str(path),e['candidate_id'],a['scope']))
assert not open_now,open_now
for old in cases:
 d,path=jobs[('evaluation',old['date'],old['method'],old['branch'])]
 found=[e for e in d['episodes'] if e['candidate_id']==old['candidate_id']]
 detail={};reason='same candidate; consumed inputs resolved and strategy predicate evaluated'
 if not found:
  assert old['method']=='GB-FAIL' and old['branch']=='prior_month_level'
  refs=d['reference_selections'];detail['corrected_references']=refs
  if old['date']=='2021-01-04':
   found=[e for e in d['episodes'] if e['side']==old['side']]
   assert len(found)==1 and found[0]['strategy_assessment']['status']=='setup'
   reason='partial December reference replaced by complete acquired continuous-chart range; same short sweep now qualifies'
  else:
   assert old['date']=='2026-01-02' and not d['episodes'] and len(refs)==1
   assert D(str(old['trigger']['L']))>=D(str(refs[0]['low']))
   assert D(str(old['trigger']['H']))<=D(str(refs[0]['high']))
   detail['old_trigger_inside_corrected_range']=True
   detail['old_trigger']={k:old['trigger'][k] for k in ('start','end','H','L')}
   status='no_candidate_after_reference_correction';reason='old partial December low was not the prior-month boundary; no strict sweep of corrected full-chart range'
 if found:
  assert len(found)==1;e=found[0];a=e['strategy_assessment'];status=a['status'];assert status in {'setup','no_setup'}
  detail.update(candidate_id=e['candidate_id'],strategy_assessment=a,values=e['values'],stages=e['stages'],reference=e['reference'],geometry=e['geometry'])
 totals[status]+=1
 records.append({'old_candidate_id':old['candidate_id'],'old_job':old['job'],'old_job_sha256':file_digest(Path(old['job'])),
  'date':old['date'],'method':old['method'],'branch':old['branch'],'old_unknown_fields':old['unknown'],
  'status':status,'reason':reason,'new_job':str(path),'new_job_sha256':file_digest(path),'evidence':detail})
assert sum(totals.values())==51
out={'status':'pass','registry_sha256':registry['registry_sha256'],'source_cases':str(oldpath),'source_cases_sha256':file_digest(oldpath),
 'original_open_entry_cases':51,'dispositions':dict(totals),'remaining_open_all_cohorts':len(open_now),'cases':records}
immutable_json(root/'validation/RESOLVED_51_CASES.json',out)
rows=[[r['date'],r['method'],r['branch'],r['old_candidate_id'],r['status'],r['reason']] for r in records]
(root/'validation/RESOLVED_51_CASES.md').write_text('# Resolution of all 51 previously open entry candidates\n\n'+str(dict(totals))+'; zero open decisions in either cohort.\n\n'+_table(['Date','Family','Branch','Original candidate','Disposition','Evidence summary'],rows)+'\n\nFull values, stages, changed references, geometry and immutable job identities are retained in [the full JSON evidence]('+str(root/'validation/RESOLVED_51_CASES.json')+').\n')
print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
