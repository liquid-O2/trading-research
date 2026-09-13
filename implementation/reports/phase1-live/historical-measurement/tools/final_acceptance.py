"""Record final artifact identities after completed execution and manual chart QA."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,'/workspace/implementation/src')
from trading_research.research.method_pack import historical_runner as hr

p=argparse.ArgumentParser();p.add_argument('--run-root',required=True)
root=Path(p.parse_args().run_root).resolve();base=root.parent
registry,coverage=hr.load_registry(root)
reconciliation=hr.read(root/'validation/CENSUS_RECONCILIATION.json')
verification=hr.read(root/'validation/FULL_INPUT_VERIFICATION.json')
qa=hr.read(root/'charts/VISUAL_QA.json');charts=hr.read(root/'charts/manifest.json')
assert reconciliation['all_declared_sessions_completed']
assert verification['status']=='pass' and qa['status']=='pass'
verification_proof=hr.read(root/'validation/PARALLEL_INPUT_VERIFICATION_CHECK.json')
assert verification_proof['status']=='pass'
assert verification_proof['helper_sha256']==hr.file_digest(base/'tools/verify_census.py')
assert qa['reviewed_charts']==len(charts['charts'])
assert len(verification['collection_jobs_verified'])==3
assert hr.read(root/'validation/full-suite.json')['exit_code']==0
assert not hr.read(root/'validation/controls.json')['failures']
parallel=hr.read(root/'validation/PARALLEL_AGGREGATION_EQUIVALENCE.json')
assert parallel['status']=='pass'
assert parallel['helper_sha256']==hr.file_digest(base/'tools/report_census.py')
for item in hr.read(root/'validation/AGGREGATION_EXECUTION.json')['chunk_receipts']:
    assert hr.file_digest(item['path'])==item['sha256']
    assert hr.read(item['path'])['identity']['helper_sha256']==parallel['helper_sha256']
finalization=hr.read(root/'validation/AGGREGATION_FINALIZATION_EQUIVALENCE.json')
assert finalization['status']=='pass'
assert finalization['helper_sha256']==hr.file_digest(base/'tools/finish_aggregation.py')
assert finalization['collector_sha256']==parallel['helper_sha256']
for item in charts['charts']:
    assert hr.file_digest(item['path'])==item['sha256']
paths=set()
for directory in ('registry','protocol','methods','records','validation','charts'):
    paths.update(p for p in (root/directory).rglob('*') if p.is_file() and p.suffix!='.pyc'
                 and p.name not in {'FINAL_ARTIFACT_MANIFEST.json','ACCEPTANCE.json'})
paths.add(root/'MEASUREMENT_RESULTS.json');paths.add(base/'MEASUREMENT_REPORT.md')
paths.update((base/'tools').glob('*.py'))
paths.update(p for p in (base/'calendar-evidence').rglob('*') if p.is_file())
paths.update(p for p in (base/'entry-review-2020-01-02').glob('*') if p.is_file())
paths.update(base/'performance-diagnostic-2024-04-15'/name for name in
    ('DIAGNOSTIC_ONLY.json','FINDINGS.md','SEMANTIC_EQUALITY.json','PROFILE.txt','profile.pstats'))
paths.update((base/'performance-diagnostic-report-serialization').glob('*.json'))
paths.update(hr.ROOT/p for p in ('.gitignore','README.md','planning/phase-1-live/PHASE.md',
    'planning/phase-1-live/wiki/current-status.md','planning/phase-1-live/wiki/index.md','planning/phase-1-live/wiki/log.md'))
from publish_local_report import PAGES
paths.update(hr.ROOT/'planning/phase-1-live/wiki'/f'{page}.md' for page in PAGES.values())
artifact={'registry_sha256':registry['registry_sha256'],
    'files':{str(path):hr.file_digest(path) for path in sorted(paths)},
    'daily_jobs':'Individual retained daily job hashes are in CENSUS_RECONCILIATION and FULL_INPUT_VERIFICATION.'}
hr.immutable_json(root/'validation/FINAL_ARTIFACT_MANIFEST.json',artifact)
result={'status':'completed_with_explicit_input_limitations','full_declared_population_executed':True,
    'registry_sha256':registry['registry_sha256'],'coverage_sha256':coverage['manifest_sha256'],
    'final_artifact_manifest_sha256':hr.file_digest(root/'validation/FINAL_ARTIFACT_MANIFEST.json'),
    'reviewed_charts':len(charts['charts']),
    'inputs_and_all_primary_recovery_checkpoints_verified':True,
    'private_execution_population_claimed':False,'actual_fills_or_returns_claimed':False,
    'phase2_selection_performed':False,'published_locally':True,
    'git_publication':'User authorized commit and push to main after local acceptance; Git history records that subsequent action.'}
hr.immutable_json(root/'validation/ACCEPTANCE.json',result)
print(result)
