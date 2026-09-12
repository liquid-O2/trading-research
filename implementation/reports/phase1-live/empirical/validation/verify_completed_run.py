"""Read-only acceptance checks; emits a separate verification record on success."""
import json
from collections import Counter
from pathlib import Path
from trading_research.research.method_pack.empirical_runner import ROOT, validate_run, file_hash
from trading_research.research.method_pack.empirical_protocol import Opportunity, ReplayResult, population_summary, content_hash, write_json
from trading_research.research.method_pack.empirical_reporting import build_results

root=Path(ROOT)
manifest=validate_run(root)
if isinstance(manifest,tuple): manifest=manifest[0]
manifest=json.loads((root/'RUN_MANIFEST.json').read_text())
report=json.loads((root/'RESULTS.json').read_text())
assert build_results(root)==report
assert report['validation']['valid'] and not report['validation']['errors']
assert report['scope']['remaining']==0 and report['scope']['scanned']==report['scope']['eligible']==165
assert len(list((root/'checkpoints').glob('*.json')))==165
records=[];record_map={};statuses=Counter();holes=Counter();assignments=0;checkpoints={}
for job in manifest['jobs']:
    path=root/'checkpoints'/f"{job['job_id']}.json"
    cp=json.loads(path.read_text());checkpoints[path.name]=file_hash(path)
    expected=root/'artifacts'/manifest['manifest_sha256'][:16]/job['job_id']/'records.json'
    assert Path(cp['artifact_path'])==expected and file_hash(expected)==cp['artifact_sha256']
    assert cp['run_manifest_sha256']==manifest['manifest_sha256']
    assert cp['job_sha256']==content_hash(job)
    assert cp['implementation_sha256']==manifest['implementation']['sha256']
    artifact=json.loads(expected.read_text())
    assert artifact['rules']==cp['rules']
    assert set(job['rule_ids'])=={x['rule_id'] for x in cp['rules']}
    assignments+=len(cp['rules'])
    for rule in cp['rules']:
        matching=[r for r in artifact['records'] if r['opportunity']['rule_id']==rule['rule_id']]
        assert population_summary(matching)==rule['summary']
        statuses[rule['status']]+=1
        holes.update(set(rule['population_holes']))
    for record in artifact['records']:
        op=Opportunity(**record['opportunity']);rp=ReplayResult(**record['replay']);rp.validate(op)
        assert rp.source_method_verdict=='unknown' and rp.faithful_disagreements is None
        assert op.opportunity_id not in record_map
        record_map[op.opportunity_id]=(record,str(expected),cp['artifact_sha256'])
        records.append(record)
assert assignments==2274
summary=population_summary(records)
# Cross-rule totals are bookkeeping only; incompatible populations have no pooled rate.
for key in ("rate","rate_exact","interval","interval_exact"): summary[key]=None
summary["rate_scope"]="additive audit counts only; no pooled rate"
for level in ('groups','rule_reports','family_reports'):
    totals={k:sum((row.get('observed_counts') or {}).get(k) or 0 for row in report[level]) for k in ('p','f','u','n','N')}
    assert totals=={k:summary[k] for k in totals}, (level,totals,summary)
for row in report['groups']:
    if not row['population_complete']:assert row['rate'] is None and row['interval'] is None
for row in report['family_reports']:assert row['rate'] is None
identity=json.loads((root/'validation/TESTED_IDENTITY.json').read_text())
assert identity['implementation']==manifest['implementation']
assert identity['run_manifest_sha256']==manifest['manifest_sha256']
assert file_hash(Path(identity['full_suite']['xml_path']))==identity['full_suite']['xml_sha256']
for group in ('tests','tools'):
    for path,digest in identity[group].items():assert file_hash(Path('/workspace')/path)==digest,path
charts=json.loads((root/'charts/INDEX.json').read_text())
review=json.loads((root/'charts/VISUAL_REVIEW.json').read_text())
assert review['status']=='pass' and review['run_manifest_sha256']==manifest['manifest_sha256']
assert set(review['reviewed_chart_sha256'])=={x['chart_sha256'] for x in charts['charts']}
seen=set();years=set();selection=[]
for job in manifest['jobs']:
    rows=[r for r in records if r['opportunity']['partition_id']==job['partition']['partition_id'] and r['opportunity']['rule_id'] in job['rule_ids']]
    for record in sorted(rows,key=lambda r:(r['opportunity']['available_at'],r['opportunity']['opportunity_id'])):
        op=record['opportunity'];key=(op['rule_id'],record['replay']['verdict']);year=op['session_date'][:4]
        if key not in seen or year not in years:
            seen.add(key);years.add(year);selection.append(op['opportunity_id'])
assert selection[:80]==[x['opportunity_id'] for x in charts['charts']]
for chart in charts['charts']:
    record,path,digest=record_map[chart['opportunity_id']]
    assert content_hash(record)==chart['record_sha256']
    assert path==chart['source_artifact'] and digest==chart['source_sha256']
    assert file_hash(Path(chart['chart_path']))==chart['chart_sha256']
result={'status':'pass','run_manifest_sha256':manifest['manifest_sha256'],'implementation_sha256':manifest['implementation']['sha256'],
    'results_sha256':file_hash(root/'RESULTS.json'),'tested_identity_sha256':file_hash(root/'validation/TESTED_IDENTITY.json'),
    'jobs':165,'rule_partition_assignments':assignments,'summary':summary,'rule_partition_statuses':dict(statuses),
    'population_holes':dict(holes),'chart_count':len(charts['charts']),'chart_index_sha256':file_hash(root/'charts/INDEX.json'),
    'visual_review_sha256':file_hash(root/'charts/VISUAL_REVIEW.json'),'checkpoints':checkpoints,
    'checks':['fresh report exact equality','all frozen jobs scanned','exact canonical artifact hashes and ownership','typed clocks and units','unique opportunity identities','raw/group/rule/family reconciliation','no pooled family rates','incomplete-population rates null','no source-faithful admission or manufactured orders/fills','current tested source/test/tool identity','deterministic chart selection and exact scored-record hashes','visual review covers all selected charts']}
write_json(root/'validation/FINAL_VERIFICATION.json',result)
print(json.dumps({k:result[k] for k in ('status','jobs','rule_partition_assignments','summary','chart_count')},sort_keys=True))
