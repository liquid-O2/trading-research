"""Supplemental native model causality and accepted-baseline preservation audit."""
from pathlib import Path
import argparse,json
from collections import Counter
from decimal import Decimal as D
from trading_research.research.method_pack.historical_runner import load_registry,read_job,file_digest,immutable_json
from trading_research.research.method_pack.strategy_policy import EXCLUDED
p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);args=p.parse_args();root=Path(args.run_root)
reg,manifest=load_registry(root);counts=Counter();sample=[]
seen_measurements=set()
def measurements(value,opening_projection=False):
 if isinstance(value,list):
  for child in value:measurements(child,opening_projection)
 elif isinstance(value,dict):
  proof=value.get('endpoint_evidence')
  if proof:
   published=proof['published']
   assert published['known_at']<=value['known_at']
   for key,old in proof['native_endpoints'].items():
    if old is not None:assert D(str(old))==D(str(published[key]))
   assert proof['raw_tick_order_recovered'] is False
   for key in ('H','L','V','O','C'):
    if key in value:
     # Judas confirms the opening price; its compact legacy confirmation
     # structure uses C as the generic entry-price slot, not a candle close.
     source_key='O' if opening_projection and 'bar_id' not in value and key=='C' else key
     assert D(str(value[key]))==D(str(published[source_key])),(key,value[key],published[source_key])
   if value.get('bar_id') and value['bar_id'] not in seen_measurements:
    seen_measurements.add(value['bar_id'])
    assert str(value['instrument_id'])==str(published['instrument_id'])
    assert value['start']==published['start'] and value['end']==published['end']
    assert all(key in value for key in ('H','L','V','O','C'))
    counts['reconciled_unique_full_bars']+=1
   elif 'bar_id' not in value:
    counts['reconciled_field_projections']+=1
  for expired in value.get('expired_continuous_chart_windows',[]):
   assert expired['expiration_ns']<=expired['start']<expired['end']
   assert file_digest(Path(expired['path']))==expired['sha256']
   counts['documented_expiration_windows']+=1
  for child in value.values():measurements(child,opening_projection)

job_paths=sorted((root/'jobs').rglob('*.json.gz'));assert len(job_paths)==776,len(job_paths)
for path in job_paths:
 doc=read_job(path)
 measurements(doc,doc['method_id']=='JJ-TBR' and doc['branch']=='judas_outbound')
 for e in doc.get('episodes',[]):
  a=e['strategy_assessment'];assert a is not None
  assert a['status']!='data_unavailable'
  if a['status'] in {'no_setup','condition_absent'}:assert a['failed_conditions']
  if a['status'] in {'setup','condition_present'}:assert not a['failed_conditions'] and not a['unavailable_conditions']
  if a['scope']=='entry_setup':assert not set(e['selected_fields'])&EXCLUDED.get(e['method'],set())
  g=e['geometry'].get('inferred_gamma') or e['reference'].get('model')
  if isinstance(g,dict) and g.get('model')=='QQQ-prior-OI-signed-gamma-v1':
   assert g['known_at']<=e['decision_at']
   for r in g['contracts']:
    assert r['quote_known_at']<=g['known_at'] and r['oi_known_at']<=g['known_at']
    assert r['oi_date']<e['session_date']
   counts['gamma_episodes']+=1;counts['causal_option_contracts']+=len(g['contracts'])
  zone=e['reference']
  if zone.get('inferred_zone'):
   assert 20<=zone['conditioned_n']<=zone['training_n']<=500
   assert zone['training_max_known_at']<zone['formation_start']<zone['known_at']<=e['decision_at']
   counts['pzone_episodes']+=1
  state=e['geometry'].get('inferred_state')
  if state:
   assert state['prior']['end']==state['current']['start']
   assert state['current']['end']<=e['decision_at']
   counts['auction_state_checks']+=1
  if e['method']=='GB-SCALP':
   assert a['excluded_personal_fields']==['small_size_recorded','source_scalp_management_recorded']
   assert e['values']['small_size_recorded'] is None and e['values']['source_scalp_management_recorded'] is None
   counts['scalps_without_personal_records']+=1
  counts['episodes']+=1
for field in ['reconciled_unique_full_bars','gamma_episodes','pzone_episodes','auction_state_checks','scalps_without_personal_records']:assert counts[field]>0,field
preserved=json.loads((root/'validation/PRESERVED_R9.json').read_text())
for path,digest in preserved['files'].items():assert file_digest(Path(path))==digest,path
# Registry explicitly retains the earlier v2 and strategy attempts, including failed/retired outcomes.
for prior,record in reg['evaluation_exposure']['earlier_attempts'].items():
 for rel,digest in record['job_files'].items():assert file_digest(Path(prior)/rel)==digest
out={'status':'pass','registry_sha256':reg['registry_sha256'],'counts':dict(counts),'r9_artifacts_preserved':len(preserved['files']),
 'earlier_attempts_checked':len(reg['evaluation_exposure']['earlier_attempts']),'script_sha256':file_digest(Path(__file__))}
immutable_json(root/'validation/STRATEGY_MODELS_QA.json',out);print(json.dumps(out,indent=2))
