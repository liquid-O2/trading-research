"""Check the expanded planning records and bounded evidence; no trading tests."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv
import hashlib
import json
import re
import zipfile

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
errors=[];assertions=0
def require(ok,label):
    global assertions
    assertions+=1
    if not ok:errors.append(label)
def read(p):return json.loads(p.read_text())
registry=read(HERE/'experiment_registry.json');units=registry['units']
require(len(units)==344,'344 distinct experiment units')
ids=[u['id'] for u in units];require(len(ids)==len(set(ids)),'unique unit IDs')
parents=read(ROOT/'review/component_registry.json')
if isinstance(parents,dict):
    parent_ids=set(parents) if all(re.fullmatch(r'[A-Z]\d\d',k) for k in parents) else {r['id'] for r in parents.get('components',[])}
else:parent_ids={r['id'] for r in parents}
require(len(parent_ids)==153,'current component registry has 153 parents')
require({u['id'] for u in units if u['level']=='parent'}==parent_ids,'all parents have phase records')
rows=list(csv.DictReader((HERE/'specialists.tsv').open(),delimiter='|'))
require(len(rows)==191,'191 curated refinements')
require({r['id'] for r in rows}=={u['id'] for u in units if u['level']=='refinement'},'exact refinement registry coverage')
for r in rows:
    require(set(r)=={'id','name','definition','target','comparisons','fixtures','metric','ablations','decision_use'} and all(r.values()),'nine nonempty local fields: '+r['id'])
    require(r['id'].split('.')[0] in parent_ids,'valid parent: '+r['id'])
phase_ids=[]
for u in units:
    require(u['status']=='planned','no fabricated empirical status: '+u['id'])
    require(u['parent'] in parent_ids,'unit parent: '+u['id'])
    require([p[0] for p in u['phases']]==['P'+str(i) for i in range(8)],'eight ordered phases: '+u['id'])
    require(bool(u['target']) and bool(u['local_cases']),'local target and cases: '+u['id'])
    loc=registry['locations'][u['id']];p=Path(loc['path']);text=p.read_text()
    require(f'<a id="{loc["anchor"]}"></a>' in text,'rendered anchor: '+u['id'])
    require(text.splitlines()[loc['line']-1].startswith('## '+u['id']+' —'),'rendered unit line: '+u['id'])
    for phase in u['phases']:
        id='EX-'+u['id']+'-'+phase[0];phase_ids.append(id)
        require(len(phase)==4 and all(phase),'nonempty phase: '+id)
        require(text.count('| '+id+':')==1,'one rendered phase: '+id)
require(len(phase_ids)==2752 and len(set(phase_ids))==2752,'2752 unique phase records')
conv=read(HERE/'conversation_experiment_routes.json')
source=read(ROOT/'review/source_design_routing.json')
expected={r['id'] for r in source if r['id'].startswith(('DTM-','JCV-','CEX-','CRL-','DRF-'))}
require(len(conv)==122 and {r['id'] for r in conv}==expected,'122 exact conversation routes')
for r in conv:
    require(bool(r['units']) and set(r['units'])<=set(ids),'conversation units: '+r['id'])
    require(r['source_fixture']=='T-SRC-'+r['id'],'source fixture retained: '+r['id'])
    line=(ROOT/'SOURCE_FINDINGS_AND_CONFLICTS.md').read_text().splitlines()[r['source_line']-1]
    require(r['id'] in line,'source line: '+r['id'])
primary=read(HERE/'primary_research_registry.json')
require([r['id'] for r in primary]==['R3-TECH-0'+str(i) for i in range(1,6)],'five explicit new primary sources')
for r in primary:
    require(all(k in r and r[k] for k in ['id','url','scope','units']),'primary scope: '+r['id'])
    require(set(r['units'])<=set(ids),'primary unit destinations: '+r['id'])
    require(r['id'] in (ROOT/'THIRD_REVIEW_RESEARCH.md').read_text(),'primary document row: '+r['id'])
examples=read(HERE/'design_examples.json')
require(examples['status']=='PASS' and examples['count']==27 and all(x['passed'] for x in examples['results']),'27 finite worked examples passed')
vix=read(HERE/'vix_feasibility.json')
require(vix['quote_rows_read']==261970 and vix['decision_cuts']==9 and vix['expiry_cuts']==18,'bounded VIX scope')
require(vix['cuts_with_iv']==18,'18 illustrative IV cases, not certified surfaces')
for r in vix['records']:
    require(len(r['rate_scenarios'])==2,'two declared rate scenarios: '+r['cut']+r['expiry'])
    for s in r['rate_scenarios']:
        require(s['max_reprice_error'] is not None and s['max_reprice_error']<1e-10,'numerical inversion bound')
        require(s['otm_iv_count']==s['put_iv_count']+s['call_iv_count'],'IV side counts')
for r in vix['inputs']:
    p=Path(r['quote_path']);require(hashlib.sha256(p.read_bytes()).hexdigest()==r['quote_sha256'],'preserved bounded quote file: '+r['day'])
    p=p.parent.parent/'opra__vix-options__open-interest__dte60-full-chain'/p.name
    require(hashlib.sha256(p.read_bytes()).hexdigest()==r['oi_sha256'],'preserved bounded OI file: '+r['day'])

# Verify all explicit anchors in newly generated experiment links.
new_docs=[ROOT/'CONVERSATION_RECHECK.md',ROOT/'SPECIALIST_EXPERIMENT_PROGRAM.md',ROOT/'MODEL_QUALITY_AND_STOPPING_RULES.md']+list((ROOT/'experiments').glob('*.md'))
for p in new_docs:
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if target.startswith(('http:','https:')) or '#' not in target:continue
        base,anchor=target.split('#',1);q=p.parent/base if base else p
        if q.is_file():require(f'<a id="{anchor}"></a>' in q.read_text(),'explicit anchor '+str(p.relative_to(ROOT))+' -> '+target)

require((HERE/'planning-baseline.zip').is_file() and (HERE/'baseline-manifest.json').is_file(),'preserved prior authored-plan baseline')
with zipfile.ZipFile(HERE/'planning-baseline.zip') as z:
    require(z.testzip() is None,'baseline ZIP CRC integrity')
doc=read(ROOT/'review/document_qa.json')
require(doc.get('status')=='PASS','latest general document/preservation audit passed')
counts=doc.get('counts',{})
require(counts.get('active_clarifications')==17,'general audit includes third-review, MBP, full-handoff and all-component upgrade clarifications')
require(counts.get('checked_markdown_documents',0)>=45,'general audit covers expanded Markdown package')

report={'status':'PASS' if not errors else 'FAIL','created_at':datetime.now(timezone.utc).isoformat(),
        'scope':'Document, registry, local-link, preservation and bounded-example/data checks only; no proposed trading-system phase executed.',
        'assertions':assertions,'parent_contracts':153,'named_refinements':191,'experiment_units':344,'phase_records':2752,
        'conversation_routes':122,'new_primary_findings':5,'total_external_finding_records':119,
        'finite_example_assertions':27,'bounded_vix_quote_rows':261970,'errors':errors}
(HERE/'review_qa.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(0 if not errors else 1)
