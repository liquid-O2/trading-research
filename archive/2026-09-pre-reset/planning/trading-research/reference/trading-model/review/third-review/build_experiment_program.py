"""Render proposed experiment contracts, not executable trading tests."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import re

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'experiments';OUT.mkdir(exist_ok=True)
rows=list(csv.DictReader((Path(__file__).parent/'specialists.tsv').open(),delimiter='|'))
system_path=ROOT/'review/system-refinement/component_refinements.psv'
system_rows=list(csv.DictReader(system_path.open(),delimiter='|'))
system_refinements={r['id']:r for r in system_rows}
upgrade_path=ROOT/'review/system-refinement/upgrade_registry.json'
upgrade_registry=json.loads(upgrade_path.read_text())
upgrades={r['id']:r for r in upgrade_registry['units']}
assert len(upgrades)==344
assert len(system_rows)==len(system_refinements)==153
assert len(rows)==191
assert len({r['id'] for r in rows})==len(rows)
assert all(None not in r and all(r.values()) for r in rows)
cards={}
for p in sorted((ROOT/'components').glob('*.md')):
    s=p.read_text()
    for m in re.finditer(r'^## ([FMCOLXGPRV]\d{2}) — ([^\n]+)\n(.*?)(?=^## |\Z)',s,re.M|re.S):
        fields={int(x[1]):x[3].strip() for x in re.finditer(r'^(\d+)\. \*\*([^*]+)\*\*\s*(.*?)(?=^\d+\. \*\*|\Z)',m[3],re.M|re.S)}
        assert set(fields)==set(range(1,11)),m[1]
        cards[m[1]]={'id':m[1],'name':m[2],'path':str(p),'line':s[:m.start()].count('\n')+1,'fields':fields}
assert len(cards)==153
assert all(r['id'].split('.')[0] in cards for r in rows)

names={'F':'Data, clocks and state','M':'Flow, profile and market measurements','C':'Context and volatility',
       'O':'Options, surfaces, flow and nodes','X':'Cross-market information','L':'Location and opportunity generation',
       'G':'Mixtures, calibration and selection','P':'Policy, execution and account risk','R':'Deferred Response mechanisms',
       'V':'Research evidence and operations'}
deterministic=set('F01 F02 F03 F04 F05 F06 F07 F08 F09 F10 F11 F12 M01 M02 M03 M04 M05 M06 M07 M08 M09 M10 M11 M12 M13 C01 C02 O01 O02 O04 O05 O06 O09 O10 O11 O15 O16 O17 O20 O21 O23 X01 X02 P01 P07 P08 P09 P10 P11 V01 V02 V03 V04 V05 V06 V07 V08'.split())
latent={'O03','O08'}
policies={'G06','G07','G08','G09','G10','P02','P03','P04','P05','P06','P12','R19'}
family_effect={
 'F':'Re-run the affected downstream chain with the reference versus changed data/state service; reconcile changed/missing candidates and latency before attributing forecast or economic gain.',
 'M':'Hold the downstream learner and candidate set fixed to compare measurement information; then hold inputs fixed to compare model capacity. Test the proposed measurement in its stated C/L/G/R consumer.',
 'C':'Replace only this Context input/head before refitting its OOF consumers. Measure changed P-zone/role/room forecasts and resulting stops, destinations and waiting decisions.',
 'O':'Compare raw/static prior-OI, mechanical repricing, flow/IV and latent-update paths on common coverage. Propagate uncertainty into node identity, reach/runner forecasts and feasible action value.',
 'X':'Compare receiver-only versus added source at first-actionable time. Preserve same-date and no-local-node cohorts, source lag, mapping error and common-shock controls.',
 'L':'Hold the scorer fixed to test generation; hold candidates fixed to test role/ranking. Match candidate count, width, distance, age and coverage, then allow full sequential policy competition.',
 'G':'Compare the same complete candidate/action sets first; then replay each sequential policy with occupancy, changing risk state and the same terminal boundary. Refit downstream using OOF predictions.',
 'P':'Compare whole full-unit action trajectories from common initial opportunities and dates, including fills/non-fills, pending state, costs, occupied time and independent account rules.',
 'R':'Retain the original C/L opportunity and each observed prefix. Measure delay, lost winners, rescued losses, non-fill, price deterioration and exit effects separately; initial C/L does not require Response.',
 'V':'Compare the explicit reference/negative/positive controls and intended evidence decisions. A governance service earns acceptance through valid inference, reconciliation or bounded operational behavior, not invented alpha.'}

def kind(parent):
    if parent in latent:return 'latent-inference'
    if parent in deterministic:return 'measurement-or-integrity'
    if parent in policies:return 'policy-or-value'
    if parent.startswith('L'):return 'generator-and-role-forecast'
    return 'predictive-specialist'

def p3(parent):
    k=kind(parent)
    if k=='measurement-or-integrity':
        return 'Exact facts get fidelity/coverage/numerical-error reports, not learned confidence. Any downstream learned head, fitted transform or uncertainty model requires chronological OOF/calibration; report year/session/age/coverage sensitivity and effective observations.'
    if k=='latent-inference':
        return 'Evaluate only identified observations/endpoint labels and sensitivity across admissible latent scenarios. Do not calibrate against invented dealer/queue/intraday-inventory truth. All learned dependencies are OOF and grouped by date/report maturity.'
    return 'Fit calibrators on separate chronological predictions of this complete upstream chain; score the stated target/horizon and natural deployment prevalence. Report effective date/episode/report counts, conditional coverage and year/session/regime/age/missingness uncertainty.'

def phases(id,parent,definition,fixture,models,metric,ablation,use,target,source):
    refinement=system_refinements[parent]
    upgrade=upgrades[id]
    definition += f" Binding local contract SR-{parent}: {refinement['definition']}"
    definition += f" Binding substantive upgrade UP-{parent}: {upgrade['upgrade_scope']} Register exact added targets/ports and applicable UPGRADE_CONSTRUCTIONS before dependent code; retain every source variant and the earlier improvement path."
    if id==parent:
        fixture += ' Full-system local cases: '+refinement['fixtures']
        models += ' Full-system comparison: '+refinement['comparison']
    else:
        fixture += f' Verify this child against the applicable SR-{parent} contract cases; reference shared parent evidence and add child integration assertions rather than repeating unrelated cases.'
    fixture += ' Specific upgrade cases: '+upgrade['cases']
    models += ' Specific further-upgrade comparison: '+upgrade['comparison']
    if id==parent:
        metric += ' Further-upgrade evidence: '+upgrade['metric']
        use += ' Further-upgrade use: '+upgrade['decision_use']
    ablation += ' Preserve source-faithful computable, corrected/earlier-upgraded and further-candidate stages. Separate added information, representation and learner capacity; apply the local geometry, latency, uncertainty and resource controls. No representative-only substitution for the other child/source variants.'
    return [
      ('P0','Definition, data and target',f'{definition} Target: {target} Confirm the exact inputs, observation clock, units, coverage and model capabilities in the linked parent contract and this local definition. Freeze definition/variant/horizon and baseline before outcomes.', 'Complete numeric/data/target manifest; unsupported inputs remain gated. This is a planned implementation check.'),
      ('P1','Reference, causality and faults',f'Local mandatory cases: {fixture} Add suffix-deletion, delayed/corrected-input and restart equivalence through this unit and its consumers.', 'Named assertions with expected outcomes for every listed case; zero unexplained semantic/causal failures, bounded declared ambiguity and numerical tolerance.'),
      ('P2','Isolated quality and challengers',f'Compare: {models} Primary local evidence: {metric}', 'Exact services require reference/invariance consistency; any learned comparison uses the same target/horizon/cohort, separates information from model class, fits/tunes only inside the chronology, and reports effect intervals/learning curves.'),
      ('P3','Calibration, support and generalization',p3(parent),'No in-sample substitution at learned edges; report unsupported/rare cohorts rather than unconditional confidence. Deterministic correctness is not an alpha claim.'),
      ('P4','Increment and interactions',f'Ablations/controls: {ablation} Also register no-component/simple-component and selected 2x2 interactions where applicable. Hard position/account/integrity constraints stay in every eligible policy comparison; relaxations are separate diagnostics.', 'Held-out increment under a frozen useful-effect/non-inferiority rule, or a prespecified joint interaction/invariant role; trial/search accounting complete.'),
      ('P5','Decision consequences',f'Use: {use} {family_effect[parent[0]]}', 'Attribution reconciles with a full rerun; include rejected, untraded, no-touch and non-fill opportunities. Local score alone is insufficient for policy promotion.'),
      ('P6','Integrated economic confirmation','Run the appropriate E0–E5 complete one-account/one-mini policy with independently reserved daily/account risk, actual required cutoff, all-in fees, latency/fill stress and all eligible days. Select before frozen outer/future confirmation.', 'Report paired daily net/risk/occupancy, account survival, uncertainty and objective gap. A useful component need not meet $2,000/day alone; the complete policy must be evaluated against that target.'),
      ('P7','Future parity, monitoring and fallback',f'Freeze parameter policy, future endpoint/inference, input/definition/model versions and monitored local metrics ({metric}). Test fallback, stale state, restart and rollback. Detailed R work waits for E5; unavailable data dependencies stay disabled.', 'Actual captured-receipt/replay and operational evidence when authorized; no future-test tuning. Mark supported/not met/inconclusive with scope. All trading-system phases remain planned here.')
    ]

units=[]
for id,c in cards.items():
    f=c['fields'];source=f"{c['path']}:{c['line']}"
    metric=('Reference algebra/state/coverage, numerical uncertainty and the independently scored downstream forecast role; '+f[9]) if id in deterministic else f[9]
    units.append({'id':id,'parent':id,'level':'parent','name':c['name'],'kind':kind(id),'status':'planned','source':source,
        'target':f[4],'local_cases':f[8]+' Full-system local cases: '+system_refinements[id]['fixtures']+' Upgrade cases: '+upgrades[id]['cases'],'system_refinement':'SR-'+id,'upgrade_id':'UP-'+id,'upgrade_contract':upgrades[id],
        'phases':phases(id,id,'Implement the ten-part parent contract with its own declared inputs/definition.',f[8],f[6],metric,f[10],f[5],f[4],source)})
for r in rows:
    id=r['id'];parent=id.split('.')[0];c=cards[parent];source=f"{c['path']}:{c['line']}"
    units.append({'id':id,'parent':parent,'level':'refinement','name':r['name'],'kind':kind(parent),'status':'planned',
       'source':source,'target':r['target'],'local_cases':r['fixtures']+' Upgrade cases: '+upgrades[id]['cases'],'system_refinement':'SR-'+parent,'upgrade_id':'UP-'+parent,'upgrade_contract':upgrades[id],'data_gate':'deferred detailed Response' if parent.startswith('R') else ('explicit data dependency' if 'DEFERRED' in r['definition'] else 'parent data and publication certification'),
       'local_definition':r,'phases':phases(id,parent,r['definition'],r['fixtures'],r['comparisons'],r['metric'],r['ablations'],r['decision_use'],r['target'],source)})

def clean(x):return re.sub(r'\s+',' ',x).replace('|','\\|')

locs={}
for family in names:
    path=OUT/(family+'.md');subset=sorted([u for u in units if u['parent'][0]==family],key=lambda u:(u['parent'],u['level']!='parent',u['id']))
    lines=[f'# {names[family]}: individual experiment phases','',
        'All phase records below are **planned trading-system checks**, not completed test results. Each parent retains its ten-part specification; named refinements isolate particular information, definitions or model/policy alternatives. They do not imply one process or model per row.',
        '', '[Phase rules and model quality](../SPECIALIST_EXPERIMENT_PROGRAM.md) govern chronology, metrics, interactions, useful effects, failure decisions and future testing. The [complete upgrade paths and specific child bindings](../UPGRADE_PATHS.md) and [implementation constructions](../UPGRADE_CONSTRUCTIONS.md) bind every unit below. Every listed local case needs separate named assertions at implementation; a test bearing the component name alone is insufficient.',
        '', '| Unit | Kind | Individual target |','|---|---|---|']
    # Stable in-file anchors avoid absolute line-number churn inside these large files.
    for u in subset:
        anchor=u['id'].lower().replace('.','-')
        lines.append(f"| [{u['id']}](#{anchor}) — {u['name']} | {u['kind']} | {clean(u['target'])} |")
    for u in subset:
        anchor=u['id'].lower().replace('.','-');lines += ['',f'<a id="{anchor}"></a>',f"## {u['id']} — {u['name']}",'']
        locs[u['id']]={'path':str(path),'line':len(lines)-1,'anchor':anchor}
        lines += [f"Parent contract: [{u['parent']}]({u['source']}). Further upgrade: [{u['upgrade_id']}](../UPGRADE_PATHS.md#up-{u['id'].lower().replace('.','-')}). Status: **planned**. Data/sequence gate: {u.get('data_gate','parent data and implementation certification')}.",
                  '', '| Phase ID | Concrete work | Acceptance / evidence |','|---|---|---|']
        for pid,title,work,acceptance in u['phases']:
            lines.append(f"| EX-{u['id']}-{pid}: {title} | {clean(work)} | {clean(acceptance)} |")
    path.write_text('\n'.join(lines)+'\n')

registry={'status':'All empirical trading-system phases planned; document/finite-example/data audits are separate.',
          'parent_count':len(cards),'refinement_count':len(rows),'unit_count':len(units),'phase_count':sum(len(u['phases']) for u in units),
          'family_counts':dict(Counter(u['parent'][0] for u in units)),
          'port_owners':{'C15.SCENARIO':'C15.LEVERAGE'},
          'input_sha256':hashlib.sha256((Path(__file__).parent/'specialists.tsv').read_bytes()).hexdigest(),
          'system_refinement_sha256':hashlib.sha256(system_path.read_bytes()).hexdigest(),
          'upgrade_registry_sha256':hashlib.sha256(upgrade_path.read_bytes()).hexdigest(),
          'upgrade_constructions_sha256':hashlib.sha256((ROOT/'UPGRADE_CONSTRUCTIONS.md').read_bytes()).hexdigest(),
          'units':units,'locations':locs}
(Path(__file__).parent/'experiment_registry.json').write_text(json.dumps(registry,indent=2,ensure_ascii=False)+'\n')
index=['# Every component and named refinement has an experiment record','',
       f"There are **{len(cards)} parent contracts**, **{len(rows)} named refinement experiments**, and **{registry['phase_count']:,} explicit phase records** across {len(units)} units. This counts test plans, not trained models, independent discoveries, passing tests or mandatory production components.",'',
       '| Family | Parent contracts | Named refinements | Individual phases |','|---|---|---|---|']
for family,name in names.items():
    nc=sum(c.startswith(family) for c in cards);nr=sum(r['id'].startswith(family) for r in rows)
    index.append(f'| [{name}]({family}.md) | {nc} | {nr} | {(nc+nr)*8} |')
index += ['', 'Machine-readable [experiment registry](../review/third-review/experiment_registry.json) and manually curated [refinement definitions](../review/third-review/specialists.tsv) preserve the same IDs, targets, fixtures, challengers and gates. The generator reads current parent cards so their local cases remain attached to each parent; substantive refinement definitions are authored separately, not inferred from keywords. The [full-system contract refinements](../SYSTEM_REFINEMENT.md), [153 upgrade paths with 191 specific child bindings](../UPGRADE_PATHS.md) and [implementation constructions](../UPGRADE_CONSTRUCTIONS.md) bind every unit and are carried into local definition/reference/comparison/interaction phases.',
          '', 'The [conversation recheck](../CONVERSATION_RECHECK.md) maps all 122 conversation findings to specific experiment units or explicit provenance/dependency cases. The original 712-source and 114-external matrices remain authoritative for exact source clauses.']
(OUT/'README.md').write_text('\n'.join(index)+'\n')
print(json.dumps({k:registry[k] for k in ['parent_count','refinement_count','unit_count','phase_count','family_counts']}))
