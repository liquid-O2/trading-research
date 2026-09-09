"""Build versioned plan coverage only. Never create or update empirical status."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG = Path('/workspace/data/manifests/dataset-catalog.json')

def read(p):
    return json.loads(p.read_text())

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

parents = read(ROOT/'review/component_registry.json')
registry = read(ROOT/'review/third-review/experiment_registry.json')
upgrades = read(HERE/'upgrade_registry.json')
upgrade_units = {u['id']: u for u in upgrades['units']}
sources = read(ROOT/'review/source_design_routing.json')
external = read(ROOT/'review/external_design_routing.json')
primary = read(ROOT/'review/third-review/primary_research_registry.json')
catalog = read(CATALOG)
requirements = []
for n, line in enumerate((ROOT/'REQUIREMENTS_TRACEABILITY.md').read_text().splitlines(), 1):
    m = re.match(r'^\| ((?:U\d{2}|DTM-U\d+|USR-\d+-\d+))\b', line)
    if m:
        requirements.append({'id': m[1], 'source': f'REQUIREMENTS_TRACEABILITY.md:{n}', 'row': line})
tasks = []
for n, line in enumerate((ROOT/'IMPLEMENTATION_BACKLOG.md').read_text().splitlines(), 1):
    m = re.match(r'^\| (B\d{2}\.\d+) \|', line)
    if m:
        cells = re.split(r'(?<!\\)\|', line)[1:-1]
        tasks.append({'id': m[1], 'milestone': m[1].split('.')[0], 'source': f'IMPLEMENTATION_BACKLOG.md:{n}',
                      'deliverable': cells[1].strip(), 'verification_contract': cells[2].strip()})

names = {'F': 'Foundations', 'M': 'Measurements', 'C': 'Context', 'O': 'Options',
         'X': 'Cross-market information', 'L': 'Locations', 'G': 'Mixtures and selection',
         'P': 'Policy, execution and risk', 'R': 'Later Response', 'V': 'Research and operations'}

def milestones(cid):
    family = cid[0]
    out = {'F': ['B00','B01','B02','B08','B10'], 'M': ['B02','B07','B09'],
           'C': ['B04','B07'], 'O': ['B05','B07'], 'X': ['B06','B07'],
           'L': ['B02','B07'], 'G': ['B07','B10'], 'P': ['B03','B08'],
           'R': ['B09'], 'V': ['B00','B03','B07','B08','B10']}[family][:]
    if cid in {'C01','C02','C03','C04','C21','C22','L01','L02','L03','L05','L11','L12','L19'}:
        out += ['B02','B03']
    if cid in {'G01','G03','G04','G05','G06','G07','G08','G09'}:
        out += ['B03']
    if cid in {'O01','O02','O03','O04','O05','O06','O21'}:
        out += ['B01']
    if cid in {'P03','P04'}:
        out += ['B09']
    if cid == 'P12':
        out += ['B06']
    if cid in {'L13','L14','L15'}:
        out = ['B05','B06','B07']
    return sorted(set(out))

units = []
for u in registry['units']:
    loc = registry['locations'][u['id']]
    units.append({'id': u['id'], 'parent': u['parent'], 'level': u['level'], 'name': u['name'],
                  'kind': u['kind'], 'target': u['target'], 'local_cases': u['local_cases'],
                  'system_refinement': u['system_refinement'],
                  'upgrade_id': u['upgrade_id'],
                  'upgrade_contract': upgrade_units[u['id']],
                  'upgrade_document': 'UPGRADE_PATHS.md#up-'+u['id'].lower().replace('.','-'),
                  'contract': str(Path(u['source'].rsplit(':',1)[0]).relative_to(ROOT)) + ':' + u['source'].rsplit(':',1)[1],
                  'experiment': str(Path(loc['path']).relative_to(ROOT)) + '#' + loc['anchor'],
                  'milestones': milestones(u['parent']),
                  'phase_ids': ['EX-'+u['id']+'-'+p[0] for p in u['phases']],
                  'source_ids': [s['id'] for s in sources if u['parent'] in s['components']],
                  'applicability': 'Read exact parent/child dependencies; record an evidence-backed disposition for every applicable comparison. Detailed R work follows C/L. A rejected branch may make later phases inapplicable with reasons; it does not erase its planned phases.'})

datasets = []
for d in catalog['datasets']:
    datasets.append({k: d.get(k) for k in ['dataset_id','archive_path','provider','schema','symbol','asset_class',
                    'description','file_count','formats','known_gaps','missing_months','timestamp_profile']})

binding_docs = sorted(str(p.relative_to(ROOT)) for p in ROOT.glob('*.md') if p.name != 'IMPLEMENTATION_SCOPE.md')
binding_docs += sorted(str(p.relative_to(ROOT)) for folder in ['components','experiments','traceability']
                       for p in (ROOT/folder).glob('*.md'))
input_files = [ROOT/p for p in binding_docs] + [ROOT/'review/component_registry.json',
    ROOT/'review/third-review/experiment_registry.json', ROOT/'review/source_design_routing.json',
    ROOT/'review/external_design_routing.json', ROOT/'review/third-review/primary_research_registry.json', HERE/'upgrade_registry.json', CATALOG]
input_files += sorted(HERE.glob('*.psv'))
manifest = {'schema_version': 1, 'purpose': 'Complete planned scope; no empirical implementation or test status lives here.',
            'workflow': 'One continuing B00–B10 implementation program; E0 is an early checkpoint.',
            'counts': {'parents': len(parents), 'refinements': sum(u['level']=='refinement' for u in units),
                       'units': len(units), 'phases': sum(len(u['phase_ids']) for u in units),
                       'source_findings': len(sources), 'external_findings': len(external)+len(primary),
                       'requirements': len(requirements), 'datasets': len(datasets), 'backlog_tasks': len(tasks)},
            'upgrade_counts': {'parent_paths': upgrades['parent_count'], 'specific_child_bindings': upgrades['refinement_binding_count'], 'units_bound': len(upgrade_units), 'method_references': len(upgrades['method_references'])},
            'upgrade_method_references': upgrades['method_references'],
            'binding_documents': binding_docs, 'units': units, 'requirements': requirements,
            'source_findings': sources, 'external_findings': external + primary,
            'datasets': datasets, 'backlog_tasks': tasks,
            'input_hashes': {str(p): digest(p) for p in input_files},
            'ledger_contract': {'location': 'A separate implementation-owned append-only ledger; never this generated file.',
                'required_keys': ['scope_version','unit_or_source_or_dataset_or_task_id','phase_or_clause','definition_version',
                    'dependency_ids','eligibility_and_cohort','engineering_state','evaluation_state','disposition',
                    'reference_and_code_artifacts','verification_artifacts','experiment_artifacts','source_variant_and_upgrade_stage','applicable_upgrade_comparison','reason','next_action'],
                'engineering_states': ['unstarted','in_progress','implemented','verified'],
                'evaluation_states': ['unrun','running','evaluated'],
                'dispositions': ['undecided','selected','rejected','inconclusive','dependency_blocked','not_applicable'],
                'completion_rule': 'Exact-ID/required-phase coverage plus artifact-backed decisions. Unsupported/future work remains visible; separate engineering, research disposition and economic evidence. No count alone certifies semantic completeness.'}}
payload = json.dumps(manifest, sort_keys=True, ensure_ascii=False, separators=(',',':')).encode()
version = hashlib.sha256(payload).hexdigest()
manifest['scope_version'] = version
serialized = json.dumps(manifest, indent=2, ensure_ascii=False)+'\n'
snapshots = HERE/'scope_snapshots'
snapshots.mkdir(exist_ok=True)
snapshot = snapshots/(version+'.json')
if snapshot.exists():
    assert snapshot.read_text() == serialized, 'Existing immutable scope snapshot differs'
else:
    snapshot.write_text(serialized)
(ROOT/'review/implementation_scope.json').write_text(serialized)

def clean(x):
    return re.sub(r'\s+',' ',x).replace('|','\\|')

counts = manifest['counts']
doc = ['# Full implementation scope','',
       'This is the coverage index for **one continuing B00–B10 implementation workflow**. Read the [handoff](IMPLEMENTATION_HANDOFF.md) for the starting message, sequencing and evidence rules. E0 is an early checkpoint. Detailed Response, later management and prospective evaluation remain in the same scope.', '',
       f"The current version covers **{counts['parents']} parents, {counts['refinements']} named refinements, {counts['units']} units and {counts['phases']:,} P0–P7 phase records**; **{counts['source_findings']} supplied-source findings, {counts['external_findings']} external findings, {counts['requirements']} prompt/DTM/active requirements, {counts['datasets']} datasets and {counts['backlog_tasks']} backlog tasks**. These are planned obligations, not completed implementations or demonstrated improvements.", '',
       'Binding upgrades add **153 authored parent paths and 191 specific child instructions** inside those same units. Their exact constructions, comparisons and cases are included for every unit in the machine scope, alongside three focused method-reference entries. They do not inflate the count of experiments or certify empirical improvement.', '',
       f"The [machine manifest](review/implementation_scope.json) contains every exact ID, target, local case, source route, milestone and phase reference. Its version is `{version}`; the [immutable snapshot](review/system-refinement/scope_snapshots/{version}.json) preserves that definition. Rebuilding this index updates no implementation status.", '',
       '## Binding interpretation', '',
       'Read the full ten-part contract and all linked child/local-phase definitions before implementing a parent. Preserve the original source idea and its conversation upgrade path; every listed variant needs a named implementation/comparison or an explicit dependency/disposition. Shared machinery is encouraged, but shared code does not remove independent semantic tests or target/horizon scorecards. A simpler measurement or deterministic construction can be the right upgrade. A new model is not mandatory.', '',
       'Use the [quality rules](MODEL_QUALITY_AND_STOPPING_RULES.md) to determine what is best supported within tested data, challengers and budgets. Initial screening may close a branch only with its registered rule and evidence; record downstream phases as inapplicable with reasons. An unsupported model is not silently dropped, and every proposal is not forced into production. Keep source-clause, cohort and decision evidence distinct from document-coverage counts.', '',
       'The actual implementation ledger is separate and append-only. It records engineering state, evaluation state and disposition independently, with artifacts, exact dependencies and next actions. At completion reconcile exact IDs/clauses/phases, not only totals. Unavailable data, unelapsed future evaluation and inconclusive research stay visible. The machine manifest contains the ledger fields and allowed states.', '']
for name in ['SYSTEM_REFINEMENT.md','UPGRADE_PATHS.md','UPGRADE_CONSTRUCTIONS.md']:
    if (ROOT/name).exists():
        doc += [f'Binding additional detail: [{name}]({name}).', '']
doc += ['## Every parent and its named refinements', '',
        'Milestones are routing indexes; the ordered backlog and actual dependency graph govern readiness. All families also inherit common contracts and validation. The parent link gives the full definition; each child link gives its individual P0–P7 record.', '']
for family, name in names.items():
    family_units = [u for u in units if u['parent'][0]==family]
    doc += [f'### {name}', '', '| Parent and definition | Named refinements with local phases | Milestones |', '|---|---|---|']
    for u in sorted((x for x in family_units if x['level']=='parent'), key=lambda x:x['id']):
        children = sorted((x for x in family_units if x['parent']==u['id'] and x['level']=='refinement'), key=lambda x:x['id'])
        child_links = ', '.join(f"[{c['id']}]({c['experiment']})" for c in children) or 'Parent-local phases cover this unit; no extra child is required.'
        doc.append(f"| [{u['id']} — {clean(u['name'])}]({u['contract']}); [parent phases]({u['experiment']}); [upgrade path]({u['upgrade_document']}) | {child_links} | {', '.join(u['milestones'])} |")
    doc.append('')
doc += ['## Full-program backlog', '', '| Milestone | Exact tasks |', '|---|---|']
for m in sorted({t['milestone'] for t in tasks}):
    ts = sorted((t for t in tasks if t['milestone']==m), key=lambda t:int(t['id'].split('.')[1]))
    doc.append('| '+m+' | '+', '.join(f"[{t['id']}]({t['source']})" for t in ts)+' |')
doc += ['', '## Source, requirement and data obligations', '',
        '- [Supplied-source routes](traceability/SOURCE_TO_DESIGN.md) and [findings](SOURCE_FINDINGS_AND_CONFLICTS.md): all 712 exact IDs, including every routed correction/exception and source-specific future fixture. The five DTM user requirements are included separately with the current prompt and active clarifications.',
        '- [Conversation upgrade lineage](CONVERSATION_RECHECK.md): all 122 conversation table rows retain their experiment routes; review the substantive sequence of user question, proposed upgrade and corrected definition rather than only the final model name.',
        '- [Requirements](REQUIREMENTS_TRACEABILITY.md), [external findings](EXTERNAL_RESEARCH.md) and [third-review primary checks](THIRD_REVIEW_RESEARCH.md): exact rows are also enumerated in the machine manifest.',
        '- [Data capability audit](DATA_CAPABILITY_AUDIT.md): all 111 catalog dataset IDs appear in the manifest with source/schema/identity metadata. At B01 attach field/cohort eligibility, observed audit depth, critical defects, dependent units and resolution actions. A complete catalog entry does not mean usable or certified data.',
        '- [Ordered backlog](IMPLEMENTATION_BACKLOG.md): every task above has an explicit deliverable and verification interface to build. Future example commands are not existing runnable modules.', '',
        '## Coverage check and resumption', '',
        'Build/check the plan manifest with `python review/system-refinement/build_scope.py`. This is a document utility. The future B00.7 implementation audit must fail on a missing unit, child, source clause, dataset eligibility record, task or required phase; on a stale definition hash; or on a claimed verified/evaluated state without evidence. Include deliberate omission, duplicate-ID, changed-contract and ledger-preservation fixtures. Cross-check actual dependency edges and clause assertions because a correct row count alone cannot establish coverage.', '',
        'At each checkpoint preserve what is built, exact passing/failed results, selected/rejected/inconclusive branches, outstanding dependencies and the next eligible work. Continue from that record in the same implementation thread. Completing a checkpoint is not a reason to abandon the rest of the manifest.', '']
(ROOT/'IMPLEMENTATION_SCOPE.md').write_text('\n'.join(doc))
assert len(units)==len({u['id'] for u in units})==344
assert len(tasks)==len({t['id'] for t in tasks})
assert len(requirements)==len({r['id'] for r in requirements})==68
assert Counter(u['parent'][0] for u in units)==Counter(registry['family_counts'])
print(json.dumps({'scope_version': version, **counts}, indent=2))
