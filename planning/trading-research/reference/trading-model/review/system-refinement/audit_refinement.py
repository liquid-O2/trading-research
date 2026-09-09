"""Check authored scope/upgrade integration only; no trading-system tests."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import csv
import hashlib
import json
import re
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
errors=[]
assertions=0

def require(ok,label):
    global assertions
    assertions+=1
    if not ok:errors.append(label)
def read(p):return json.loads(p.read_text())
def psv(p):return list(csv.DictReader(p.open(),delimiter='|'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

parents=read(ROOT/'review/component_registry.json')
refinements=psv(HERE/'component_refinements.psv')
paths=psv(HERE/'upgrade_paths.psv')
bindings=psv(HERE/'upgrade_bindings.psv')
specialists=psv(ROOT/'review/third-review/specialists.tsv')
up=read(HERE/'upgrade_registry.json')
ex=read(ROOT/'review/third-review/experiment_registry.json')
scope=read(ROOT/'review/implementation_scope.json')
source=read(ROOT/'review/source_design_routing.json')
conv=read(ROOT/'review/third-review/conversation_experiment_routes.json')
expected={'F':12,'M':13,'C':24,'O':23,'X':10,'L':19,'G':10,'P':12,'R':22,'V':8}
expected_children={'F':12,'M':19,'C':46,'O':28,'X':19,'L':20,'G':11,'P':13,'R':14,'V':9}
require(len(parents)==153,'153 exact parent contracts')
for rows,label in [(refinements,'contract refinements'),(paths,'upgrade paths')]:
    require(len(rows)==153 and len({r['id'] for r in rows})==153,label+' unique rows')
    require({r['id'] for r in rows}==set(parents),label+' exact parent coverage')
    require(dict(Counter(r['id'][0] for r in rows))==expected,label+' family distribution')
    for r in rows:require(None not in r and all(r.values()),label+' nonempty fields '+r['id'])
require(len(bindings)==191 and len({r['id'] for r in bindings})==191,'191 unique authored child bindings')
require({r['id'] for r in bindings}=={r['id'] for r in specialists},'exact child definition coverage')
require(dict(Counter(r['id'][0] for r in bindings))==expected_children,'exact child family distribution')
for r in bindings:require(set(r)=={'id','upgrade_scope','comparison','cases'} and all(r.values()),'complete specific child record '+r['id'])
require(len(up['units'])==344,'344 upgrade-bound units')
uid={u['id']:u for u in up['units']};eid={u['id']:u for u in ex['units']};sid={u['id']:u for u in scope['units']}
require(len(uid)==len(eid)==len(sid)==344,'unique unit IDs in every registry')
require(set(uid)==set(eid)==set(sid),'identical complete unit scope in upgrade/phase/handoff registries')
require(scope['counts']=={'parents':153,'refinements':191,'units':344,'phases':2752,'source_findings':712,'external_findings':119,'requirements':68,'datasets':111,'backlog_tasks':64},'exact complete scope counts')
require(scope['upgrade_counts']=={'parent_paths':153,'specific_child_bindings':191,'units_bound':344,'method_references':3},'exact upgrade counts without unit inflation')

upgrade_doc=(ROOT/'UPGRADE_PATHS.md').read_text()
refine_doc=(ROOT/'SYSTEM_REFINEMENT.md').read_text()
construction_doc=(ROOT/'UPGRADE_CONSTRUCTIONS.md').read_text()
for cid,p in parents.items():
    require(refine_doc.count('#### SR-'+cid+' —')==1,'rendered contract refinement '+cid)
    require(upgrade_doc.count('### UP-'+cid+' —')==1,'rendered parent upgrade '+cid)
    s=Path(p['path']).read_text()
    m=re.search(r'^## '+cid+r' — [^\n]+\n(.*?)(?=^## |\Z)',s,re.M|re.S)
    require(m is not None,'parent card present '+cid)
    if m:
        fields={int(x[1]):x[3] for x in re.finditer(r'^(\d+)\. \*\*([^*]+)\*\*\s*(.*?)(?=^\d+\. \*\*|\Z)',m[1],re.M|re.S)}
        require(set(fields)==set(range(1,11)),'ten fields retained '+cid)
        require('[SR-'+cid+']' in fields.get(3,''),'binding contract in parent field 3 '+cid)
        require('[UP-'+cid+']' in fields.get(6,''),'binding upgrade in parent field 6 '+cid)

phaseids=[]
for id,u in uid.items():
    v=eid[id];s=sid[id];anchor='up-'+id.lower().replace('.','-')
    require(u['status']=='planned' and v['status']=='planned','no invented empirical result '+id)
    require(u['parent'] in parents and u['upgrade_id']=='UP-'+u['parent'],'valid upgrade owner '+id)
    require(upgrade_doc.count('<a id="'+anchor+'"></a>')==1,'exact rendered upgrade anchor '+id)
    require(v['upgrade_id']==u['upgrade_id'] and v['upgrade_contract']==u,'phase registry binds full authored upgrade '+id)
    require(s['upgrade_id']==u['upgrade_id'] and s['upgrade_contract']==u,'handoff scope binds full authored upgrade '+id)
    require(s['upgrade_document']=='UPGRADE_PATHS.md#'+anchor,'scope local upgrade link '+id)
    phases={p[0]:p for p in v['phases']}
    require(list(phases)==['P'+str(i) for i in range(8)],'eight ordered phases '+id)
    require(u['upgrade_scope'] in phases['P0'][2],'specific construction in P0 '+id)
    require(u['cases'] in phases['P1'][2],'specific new cases in P1 '+id)
    require(u['comparison'] in phases['P2'][2],'specific comparison in P2 '+id)
    require('No representative-only substitution' in phases['P4'][2],'all-child/source obligation in P4 '+id)
    require(v['system_refinement']=='SR-'+u['parent'],'system refinement retained '+id)
    require(set(u['source_ids'])=={r['id'] for r in source if u['parent'] in r['components']},'source clauses preserved per unit '+id)
    required=['EX-'+id+'-P'+str(i) for i in range(8)]
    require(u['required_phase_ids']==required and s['phase_ids']==required,'phase IDs unchanged '+id)
    phaseids+=required
    loc=ex['locations'][id];text=Path(loc['path']).read_text()
    require('](../UPGRADE_PATHS.md#'+anchor+')' in text,'local experiment links exact upgrade '+id)
    for pid in required:require(text.count('| '+pid+':')==1,'one rendered planned phase '+pid)
require(len(phaseids)==len(set(phaseids))==2752,'2752 unique planned phases')

require(len(source)==712 and {r['id'] for r in up['source_routes']}=={r['id'] for r in source},'all 712 exact source routes')
require(len(conv)==122 and {r['id'] for r in up['conversation_routes']}=={r['id'] for r in conv},'all 122 exact conversation routes')
for r in up['conversation_routes']:
    require(set(r['units'])<=set(uid),'conversation unit coverage '+r['id'])
    require(r['upgrades']==sorted({'UP-'+u.split('.')[0] for u in r['units']}),'conversation upgrade ownership '+r['id'])
    line=(ROOT/'SOURCE_FINDINGS_AND_CONFLICTS.md').read_text().splitlines()[r['source_line']-1]
    require(r['id'] in line,'conversation exact source line '+r['id'])
require(len(up['method_references'])==3,'three scoped method references')
for r in up['method_references']:
    require(all(r.get(k) for k in ['id','title','url','scope','supports','units']),'scoped method record '+r['id'])
    require(set(r['units'])<=set(uid),'valid method destinations '+r['id'])
    require(r['id'] in upgrade_doc and r['url'] in upgrade_doc,'rendered method scope '+r['id'])
for i in range(1,11):require(f'<a id="upk-{i:02}"></a>' in construction_doc,'shared construction '+str(i))
for term in ['C08.PROFILE_EVOLUTION','C07.STATE','C07.TRANSITION','O12.FIELD_EVOLUTION','C15.SCENARIO','O21.DECISION_SENSITIVITY']:
    require(term in construction_doc,'new/retained port boundary '+term)

for p,h in up['input_hashes'].items():require(sha(Path(p))==h,'upgrade input hash '+p)
require(ex['upgrade_registry_sha256']==sha(HERE/'upgrade_registry.json'),'phase registry current upgrade hash')
require(ex['system_refinement_sha256']==sha(HERE/'component_refinements.psv'),'phase registry current refinement hash')
require(ex['upgrade_constructions_sha256']==sha(ROOT/'UPGRADE_CONSTRUCTIONS.md'),'phase registry current construction hash')
for p,h in scope['input_hashes'].items():require(sha(Path(p))==h,'scope input hash '+p)
manifest=dict(scope);version=manifest.pop('scope_version')
payload=json.dumps(manifest,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
require(hashlib.sha256(payload).hexdigest()==version,'scope content-derived version')
snapshot=HERE/'scope_snapshots'/(version+'.json')
require(snapshot.is_file() and snapshot.read_bytes()==(ROOT/'review/implementation_scope.json').read_bytes(),'immutable scope snapshot matches current definition')
require('separate' in scope['ledger_contract']['location'].lower(),'empirical ledger separate from generated scope')
require('source_variant_and_upgrade_stage' in scope['ledger_contract']['required_keys'],'ledger records original/prior/new stages')
require('applicable_upgrade_comparison' in scope['ledger_contract']['required_keys'],'ledger records exact upgrade comparison')
require(all('engineering_state' not in u and 'evaluation_state' not in u for u in scope['units']),'generated scope does not overwrite empirical states')

req=(ROOT/'REQUIREMENTS_TRACEABILITY.md').read_text()
reqids=re.findall(r'^\| ((?:U\d{2}|DTM-U\d+|USR-\d+-\d+))\b',req,re.M)
require(len(reqids)==68 and len(set(reqids))==68,'68 prompt/DTM/active requirement IDs')
require({r['id'] for r in scope['requirements']}==set(reqids),'all requirements in handoff scope')
tasks=re.findall(r'^\| (B\d{2}\.\d+) \|',(ROOT/'IMPLEMENTATION_BACKLOG.md').read_text(),re.M)
require(len(tasks)==64 and {r['id'] for r in scope['backlog_tasks']}==set(tasks),'all 64 backlog tasks in scope')
catalog=read(Path('/workspace/data/manifests/dataset-catalog.json'))
require(len(scope['datasets'])==111 and {r['dataset_id'] for r in scope['datasets']}=={r['dataset_id'] for r in catalog['datasets']},'all 111 catalog dataset identities retained')
handoff=(ROOT/'IMPLEMENTATION_HANDOFF.md').read_text()
for i in range(11):require(f'| B{i:02} |' in handoff,'full handoff milestone '+str(i))
for doc in ['SYSTEM_REFINEMENT.md','UPGRADE_PATHS.md','UPGRADE_CONSTRUCTIONS.md','IMPLEMENTATION_SCOPE.md']:
    require(doc in handoff and doc in scope['binding_documents'] if doc!='IMPLEMENTATION_SCOPE.md' else doc in handoff,'handoff binds '+doc)
require('one continuing implementation workflow' in handoff.lower(),'single continuing implementation workflow')
require('E0 is an early checkpoint' in handoff,'E0 not full-program stopping boundary')
require('/workspace/archive/' in handoff and 'excluded' in handoff,'excluded prior workspace boundary retained')

baseline=read(HERE/'baseline.json')
with zipfile.ZipFile(HERE/'baseline.zip') as z:
    require(z.testzip() is None,'preserved baseline ZIP CRC')
    for row in baseline:
        require(row['path'] in z.namelist(),'baseline member '+row['path'])
        require(hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256'],'baseline byte preservation '+row['path'])

report={'status':'PASS' if not errors else 'FAIL','created_at':datetime.now(timezone.utc).isoformat(),
    'scope':'Document/registry/phase-binding/source-route/immutable-scope/preservation consistency only. No trading-system implementation, training, backtest or proposed empirical phase executed.',
    'assertions':assertions,'contract_refinements':153,'parent_upgrade_paths':153,'specific_child_upgrade_bindings':191,
    'bound_units':344,'planned_phase_records':2752,'source_findings':712,'conversation_routes':122,
    'prompt_dtm_active_requirements':68,'datasets_in_scope':111,'backlog_tasks':64,
    'existing_external_finding_records':119,'additional_scoped_method_references':3,'scope_version':version,
    'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'SYSTEM_REFINEMENT.md',ROOT/'UPGRADE_PATHS.md',ROOT/'UPGRADE_CONSTRUCTIONS.md',ROOT/'IMPLEMENTATION_HANDOFF.md',ROOT/'IMPLEMENTATION_SCOPE.md',HERE/'upgrade_registry.json',ROOT/'review/third-review/experiment_registry.json']},
    'errors':errors}
(HERE/'refinement_qa.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(report,indent=2,ensure_ascii=False))
raise SystemExit(0 if not errors else 1)
