"""Render authored upgrade paths and exact child bindings; no empirical runs."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def read_json(path):return json.loads(path.read_text())
def read_psv(path):return list(csv.DictReader(path.open(),delimiter='|'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def clean(x):return re.sub(r'\s+',' ',x).replace('|','\\|')

parents=read_json(ROOT/'review/component_registry.json')
paths=read_psv(HERE/'upgrade_paths.psv')
bindings=read_psv(HERE/'upgrade_bindings.psv')
specialists=read_psv(ROOT/'review/third-review/specialists.tsv')
source=read_json(ROOT/'review/source_design_routing.json')
conversation=read_json(ROOT/'review/third-review/conversation_experiment_routes.json')
assert len(paths)==153 and {r['id'] for r in paths}==set(parents)
assert len(bindings)==191 and {r['id'] for r in bindings}=={r['id'] for r in specialists}
assert all(set(r)=={'id','kind','starting_point','existing_path','remaining_gap','further_upgrade','comparison','metric','fixtures','decision_use'} and all(r.values()) for r in paths)
assert all(set(r)=={'id','upgrade_scope','comparison','cases'} and all(r.values()) for r in bindings)
byid={r['id']:r for r in paths}
bychild={r['id']:r for r in bindings}
oldchild={r['id']:r for r in specialists}
names={'F':'Foundations','M':'Measurements','C':'Context','O':'Options','X':'Cross-market information',
       'L':'Locations','G':'Mixtures and selection','P':'Policy, execution and risk','R':'Later Response','V':'Research and operations'}
method_references=[
 {'id':'UP-METH-01','title':'Andersen, Bollerslev, Diebold and Labys — Realized Volatility and Correlation (1999 working paper)',
  'url':'https://archive.nyu.edu/bitstream/2451/27128/2/wpa99061.pdf',
  'scope':'Focused text read of section 4, PDF pages 9–10, plus surrounding sampling-noise discussion. Not a fresh full-paper review.',
  'supports':'ARFIMA as a fractional-memory model of log realized volatility; no copied parameter value, Gaussian-return guarantee or NQ/ES performance result.',
  'units':['C12.NOISE','C13.HAR_VARIANTS','G02.MULTITARGET']},
 {'id':'UP-METH-02','title':'Chazal, Guibas, Oudot and Skraba — Persistence-Based Clustering in Riemannian Manifolds (2013)',
  'url':'https://doi.org/10.1145/2535927',
  'scope':'Publisher and author-hosted indexed abstracts read; full-PDF web retrieval exceeded size limit and publisher open failed. Conceptual reference only, not a formula/theorem reproduction.',
  'supports':'Mode prominence/persistence as a clustering idea. Trading-profile dependence, weighted observations and smoothing-scale stability need their own tests; no transferred statistical guarantee.',
  'units':['M04.TOPOLOGY','O11.NODE_GEOMETRY','L05.PROFILE_ROLES']},
 {'id':'UP-METH-03','title':'Bacry and Muzy — Hawkes model for price and trades high-frequency dynamics (2013)',
  'url':'https://arxiv.org/abs/1301.1135',
  'scope':'Author abstract and bibliographic page read; no full-paper implementation reproduction.',
  'supports':'Joint trade-arrival/price-change kernels as a bounded model challenger. Futures event semantics, stability, likelihood and actual predictive value must be verified independently.',
  'units':['M09.RECOVERY','M10.INTENSITY','C18.CONTROL','X07.FLOW_SMT']}
]
records=[]
for r in paths:
    cid=r['id'];parent_sources=[s['id'] for s in source if cid in s['components']]
    records.append({'id':cid,'parent':cid,'level':'parent','upgrade_id':'UP-'+cid,
        'upgrade_scope':r['further_upgrade'],'comparison':r['comparison'],'cases':r['fixtures'],
        'metric':r['metric'],'decision_use':r['decision_use'],'source_ids':parent_sources,
        'conversation_ids':[c['id'] for c in conversation if any(u.split('.')[0]==cid for u in c['units'])],
        'status':'planned','required_phase_ids':['EX-'+cid+'-P'+str(i) for i in range(8)]})
for r in bindings:
    cid=r['id'];parent=cid.split('.')[0];old=oldchild[cid]
    records.append({'id':cid,'parent':parent,'level':'refinement','upgrade_id':'UP-'+parent,
        'upgrade_scope':r['upgrade_scope'],'comparison':r['comparison'],'cases':r['cases'],
        'metric':old['metric'],'target':old['target'],'decision_use':old['decision_use'],
        'source_ids':[s['id'] for s in source if parent in s['components']],
        'conversation_ids':[c['id'] for c in conversation if cid in c['units']],
        'status':'planned','required_phase_ids':['EX-'+cid+'-P'+str(i) for i in range(8)]})
registry={'schema_version':1,'status':'All substantive improvements are planned hypotheses or engineering requirements; no trading-system phase run.',
    'parent_count':len(paths),'refinement_binding_count':len(bindings),'unit_count':len(records),
    'family_parent_counts':dict(Counter(r['id'][0] for r in paths)),
    'family_refinement_counts':dict(Counter(r['id'][0] for r in bindings)),
    'kinds':dict(Counter(r['kind'] for r in paths)),
    'input_hashes':{str(p):digest(p) for p in [HERE/'upgrade_paths.psv',HERE/'upgrade_bindings.psv',ROOT/'review/third-review/specialists.tsv',ROOT/'review/source_design_routing.json',ROOT/'review/third-review/conversation_experiment_routes.json']},
    'parent_paths':paths,'units':records,'method_references':method_references,
    'source_routes':[{'id':s['id'],'source_line':s['source_line'],'fixture':s['fixture'],'parents':s['components'],'upgrades':['UP-'+p for p in s['components']]} for s in source],
    'conversation_routes':[dict(c,upgrades=sorted({'UP-'+u.split('.')[0] for u in c['units']})) for c in conversation]}
(HERE/'upgrade_registry.json').write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n')

doc=['# Upgrade paths across the complete system','',
     '**153 individually authored parent upgrade paths and 191 individually authored child bindings cover every registered F/M/C/O/X/L/G/P/R/V unit.** This is the substantive pass after the [full-system definition refinement](SYSTEM_REFINEMENT.md). It preserves the existing 344 units and 2,752 P0–P7 records, extending their comparisons instead of pretending every improvement needs another standalone model. All empirical comparisons remain unrun.','',
     'The path for each component is: **starting idea → existing conversation/plan improvements → remaining weakness → further construction → fair comparison → evidence and decision use**. Starting points are concise conceptual summaries, not verbatim quotes or claims that every source began at the same level. The exact reviewed source clauses and conversation experiment routes below preserve the historical proposals, user corrections, exceptions and uncertainty. A prior assistant proposal remains a hypothesis; listing it does not make it a user requirement or a proven method.','',
     'Read this with [implementation constructions](UPGRADE_CONSTRUCTIONS.md), the parent ten-part cards, [individual experiment phases](experiments/README.md) and [quality rules](MODEL_QUALITY_AND_STOPPING_RULES.md). The [complete handoff](IMPLEMENTATION_HANDOFF.md) and [versioned scope](IMPLEMENTATION_SCOPE.md) carry all of it through one continuing B00–B10 implementation workflow.','',
     '## Complete family coverage','',
     '| Family | Parent upgrade paths | Specific child bindings |','|---|---:|---:|']
for f,name in names.items():
    doc.append(f'| [{name}](#family-{f.lower()}) | {sum(r["id"].startswith(f) for r in paths)} | {sum(r["id"].startswith(f) for r in bindings)} |')
doc += ['', 'The rows are a worklist, not a completeness proof by counting. Implementers must expand every named source alternative and clause inside each unit, preserve exact target/clock/coverage differences, and attach a comparison or evidence-backed dependency/disposition. Testing one representative child does not satisfy a whole family. Shared kernels can reuse semantic evidence only when definitions are actually identical; every affected child still needs its own integration and target scorecard.','',
        '## What qualifies as an upgrade','',
        '- Measurement upgrades improve supported information, geometry, stability or interpretability while retaining the literal reference. Learned residual transforms belong to the chronological fit graph.','- Forecast upgrades must beat or complement strong same-target baselines on proper scores, calibration and supported cohorts, then justify their role in complete decisions. Information changes and model-capacity changes are tested separately.','- Location upgrades control count, width, distance, age, formation and confirmation delay before comparing selected value. Wider or more numerous regions cannot alone establish better precision.','- Policy upgrades compare full feasible action trajectories, including waiting, occupancy, fills, costs and cumulative one-mini risk. A locally better hit rate is insufficient.','- Engineering/research-service upgrades can earn acceptance through exactness, valid inference, resource savings, recovery or diagnostics. They do not need a fabricated alpha story.','',
        'Complexity is optional. A deterministic representation, corrected definition, robust statistic, fewer duplicated calculations or a simpler policy may be the successful upgrade. The registered challenger can be rejected or inconclusive; no promised improvement factor, profitability, exhaustive global optimum or guarantee of future behavior is asserted.','']
for f,name in names.items():
    doc += [f'<a id="family-{f.lower()}"></a>',f'## {name}','']
    for r in sorted((r for r in paths if r['id'].startswith(f)),key=lambda r:r['id']):
        cid=r['id'];path=str(Path(parents[cid]['path']).relative_to(ROOT))
        sources=[s for s in source if cid in s['components']]
        conv=[c for c in conversation if any(u.split('.')[0]==cid for u in c['units'])]
        doc += [f'<a id="up-{cid.lower()}"></a>',f'### UP-{cid} — {parents[cid]["title"]}','',
                f'Parent: [{cid}]({path}); [local phases](experiments/{f}.md#{cid.lower()}); [definition refinement](SYSTEM_REFINEMENT.md#sr-{cid.lower()}). Upgrade role: `{r["kind"]}`.','',
                '**Starting idea.** '+r['starting_point'],'',
                '**Existing improvement path.** '+r['existing_path'],'',
                '**Remaining weakness.** '+r['remaining_gap'],'',
                '**Further upgrade.** '+r['further_upgrade'],'',
                '**Fair comparison.** '+r['comparison'],'',
                '**Evidence.** '+r['metric'],'',
                '**Additional local cases to implement.** '+r['fixtures'],'',
                '**Decision or system use.** '+r['decision_use'],'']
        if sources:
            doc += ['**Exact reviewed source clauses.** '+', '.join(f'[{s["id"]}](SOURCE_FINDINGS_AND_CONFLICTS.md:{s["source_line"]})' for s in sources)+'.','']
        if conv:
            doc += ['**Conversation upgrade lineage.** '+', '.join(f'[{c["id"]}](SOURCE_FINDINGS_AND_CONFLICTS.md:{c["source_line"]})' for c in conv)+'. Read the full rows and their original conversation references; [the recheck](CONVERSATION_RECHECK.md) preserves the exact unit/exception routes.','']
        children=sorted((x for x in bindings if x['id'].split('.')[0]==cid),key=lambda x:x['id'])
        for child in children:
            uid=child['id'];anchor=uid.lower().replace('.','-')
            doc += [f'<a id="up-{anchor}"></a>',f'#### {uid} — {oldchild[uid]["name"]}','',
                    f'[Existing definition, target and P0–P7](experiments/{f}.md#{anchor}) remain binding.','',
                    '**Specific upgrade scope.** '+child['upgrade_scope'],'',
                    '**Local comparison.** '+child['comparison'],'',
                    '**Additional cases.** '+child['cases'],'']
        if not children:
            doc += ['This parent has no separate named child; its own P0–P7 phases carry the full upgrade and source-clause obligations.','']

doc += ['## Method references and limits of external support','',
        'The designs above are proposed applications and extensions, not claims that a cited paper established their performance on this dataset. These focused references supplement the existing 119 external finding records; they are kept as three method-reference entries, not silently added to the historical review totals. Before reproducing a named source algorithm, verify its full required equations and assumptions in the implementation definition phase.','']
for ref in method_references:
    doc += [f'**{ref["id"]}: [{ref["title"]}]({ref["url"]}).** '+ref['supports']+' Read scope: '+ref['scope']+' Units: '+', '.join(ref['units'])+'.','']
doc += ['## Evidence, preservation and completion','',
        'The authored [parent paths](review/system-refinement/upgrade_paths.psv), [child bindings](review/system-refinement/upgrade_bindings.psv) and [machine upgrade registry](review/system-refinement/upgrade_registry.json) preserve exact IDs. All 712 supplied-source routes and 122 conversation routes are carried into that registry. These links point to the original reviewed findings rather than replacing their detailed clauses with this summary. The [preserved baseline](review/system-refinement/baseline.zip) records the plan before this refinement pass.','',
        'Every parent and child has the upgrade in its local definition, case, comparison, interaction and decision phases. The implementation ledger records actual code, semantic verification, eligible experiments and selected/rejected/inconclusive/blocked disposition separately. New target schemas, fitted transforms and ports must be registered under UPGRADE_CONSTRUCTIONS before dependent code, with the DAG and OOF closure checked. All experiments here remain planned. Coverage, link and hash checks establish document consistency only.','']
(ROOT/'UPGRADE_PATHS.md').write_text('\n'.join(doc))

# Bind comparisons directly into all ten-part parent cards; append no extra field.
for p in (ROOT/'components').glob('*.md'):
    s=p.read_text()
    def bind(m):
        cid=m[1];body=m[0];marker=f'[UP-{cid}](../UPGRADE_PATHS.md#up-{cid.lower()})'
        if marker not in body:
            body=re.sub(r'^(6\. \*\*[^*]+\*\*[^\n]*)',lambda n:n[0]+' Binding further upgrade and child comparisons: '+marker+'.',body,count=1,flags=re.M)
        return body
    s=re.sub(r'^## ([FMCOLXGPRV]\d{2}) — [^\n]+\n.*?(?=^## |\Z)',bind,s,flags=re.M|re.S)
    p.write_text(s)
print(json.dumps({'status':'rendered planned upgrade paths','parents':len(paths),'specific_child_bindings':len(bindings),'source_routes':len(source),'conversation_routes':len(conversation),'method_references':len(method_references)},indent=2))
