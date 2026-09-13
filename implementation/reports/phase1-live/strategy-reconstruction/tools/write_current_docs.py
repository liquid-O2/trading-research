"""Publish accepted strategy results into live docs while preserving old bodies."""
from pathlib import Path
import argparse,json,gzip,re,hashlib
from trading_research.research.method_pack.historical_runner import load_registry,immutable_json,file_digest
from trading_research.research.method_pack.historical_reporting import _table
from trading_research.research.method_pack.branch_coverage import METHOD_PAGES
p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);args=p.parse_args();root=Path(args.run_root)
registry,manifest=load_registry(root);read=lambda p:json.loads(p.read_text())
accept=read(root/'ACCEPTANCE.json');models=read(root/'validation/STRATEGY_MODELS_QA.json');results=read(root/'STRATEGY_RESULTS.json')
resolved=read(root/'validation/RESOLVED_51_CASES.json')
assert accept['software_acceptance']=='pass' and models['status']=='pass' and resolved['status']=='pass'
assert resolved['remaining_open_all_cohorts']==0
R=Path('/workspace');base=root.parent;snapshot=json.loads(gzip.decompress((root/'validation/BEFORE_DOCS.json.gz').read_bytes()))
entry=results['evaluation']['scopes'].get('entry_setup',{});context=results['evaluation']['scopes'].get('context_or_research',{})
phase=_table(['family','variant','n','faithful_disagreements','status','report path'],results['phase'])
audit=_table(['family','id','verdict','fixture','leakage','proxy-as-faithful','notes'],results['audit'])
summary=f"Current strategy reconstruction: **{entry.get('setup',0)} setups, {entry.get('no_setup',0)} no-setup rejections and {entry.get('data_unavailable',0)} unavailable market-input candidates** in the declared evaluation sample. Context and research units are separate."
common=summary+f"\n\nPersonal size, account limits and executed-order records do not gate setups. Auction states, QQQ gamma/key levels, P-zones and macro context have explicit source-inspired implementations. A no-setup rejection is not a losing trade or a software failure.\n\n[Completion report]({base}/COMPLETION_REPORT.md) · [Strategy results]({root}/STRATEGY_RESULTS.md) · [Source conformance]({R}/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Charts]({root}/charts/README.md).\n\nValidation: {accept['full_suite']}; {accept['completed_jobs']} completed jobs across all {accept['exact_coverage_units']} branch/extra units; {accept['charts']} primary charts visually checked."
updated=[]
def publish(rel,body):
 old=snapshot[rel];first,tail=old.split('\n',1)
 fresh=first+'\n\n<!-- phase1-strategy-current -->\n'+body.strip()+'\n<!-- /phase1-strategy-current -->\n\n## Preserved v2 source-audit baseline\n\nThe following section records the earlier, broader source-audit scope. Its personal-record requirements and p/f/u counts are historical comparisons; the strategy scope and current classifications above supersede them.\n\n'+tail.lstrip()
 path=R/rel;path.write_text(fresh);updated.append({'path':str(path),'before_sha256':hashlib.sha256(old.encode()).hexdigest(),'after_sha256':file_digest(path)})
for method,name in METHOD_PAGES.items():
 rel=f'planning/phase-1-live/wiki/method-{name}.md';counts=results['evaluation']['families'].get(method,{})
 body=f"## Current reconstructed strategy\n\n{method}: {counts.get('entry_setup:setup',0)} setup, {counts.get('entry_setup:no_setup',0)} no setup, {counts.get('entry_setup:data_unavailable',0)} unavailable input. Personal execution requirements are excluded from qualification.\n\n[Current method report]({root}/strategy-methods/{method}.md) · [Versioned policy]({root}/registry/STRATEGY_POLICY.json) · [Source conformance]({R}/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).\n\n"
 body+=_table(['Scope and classification','Observations'],sorted(counts.items()))+'\n\n'
 body+='The preserved source audit below describes its original scope. An inferred level/state is identified as our model; it is not a recovered author label or evidence of an actual trade.'
 publish(rel,body)
for rel in snapshot:
 if rel.startswith('planning/phase-1-live/wiki/method-'):continue
 if rel=='planning/phase-1-live/SOURCE_CALIBRATION_DISCOVERY_HANDOFF.md':continue
 body=common
 if rel=='planning/phase-1-live/PHASE.md':body+='\n\n### PHASE lines\n\n'+phase+'\n\n### Audit lines\n\n'+audit
 if rel=='implementation/reports/phase1-live/methods/index.md':
  body+='\n\n'+_table(['Family','Current strategy report'],[[m,f'[{m}]({root}/strategy-methods/{m}.md)'] for m in METHOD_PAGES])
 publish(rel,body)
commands=f"""```bash
python implementation/tools/run_phase1_objects.py historical-replay freeze --strategy \\
  --run-root <new-run-root> \\
  --scope /workspace/implementation/reports/phase1-live/strategy-reconstruction/SCOPE_POLICY_1_1.json
python implementation/tools/run_phase1_objects.py historical-replay run --run-root <new-run-root> --cohort pilot --workers 4
python implementation/tools/run_phase1_objects.py historical-replay run --run-root <new-run-root> --cohort evaluation --workers 4
python implementation/tools/validate_phase1_native_replay.py --run-root <new-run-root> --part all
python implementation/tools/run_phase1_objects.py historical-replay report --run-root <new-run-root>
python implementation/tools/chart_phase1_native_replay.py --run-root <new-run-root>
cp {root}/validation/PRESERVED_R9.json <new-run-root>/validation/PRESERVED_R9.json
PYTHONPATH=implementation/src python implementation/reports/phase1-live/strategy-reconstruction/tools/verify_resolved_cases.py --run-root <new-run-root>
PYTHONPATH=implementation/src python implementation/reports/phase1-live/strategy-reconstruction/tools/verify_strategy_models.py --run-root <new-run-root>
PYTHONPATH=implementation/src python implementation/reports/phase1-live/strategy-reconstruction/tools/render_model_diagnostics.py --run-root <new-run-root>
python implementation/reports/phase1-live/strategy-reconstruction/tools/prepare_chart_review.py --run-root <new-run-root>
# Review every newly rendered chart; record VISUAL_QA.json for that exact manifest.
python implementation/tools/run_phase1_objects.py historical-replay verify --run-root <new-run-root>
```
"""
text='# Strategy reconstruction completion report\n\n'+common+'\n\n'
text+='## Implemented changes\n\n'
text+='- Removed personal size/management and daily account-limit clauses from market setup qualification; retained source contracts as a separate audit comparison.\n- Added source-inspired auction-state criteria, causal QQQ gamma/flip/wall and mapped key-level models, volume/volatility-conditioned P-zones and initial-release macro context.\n- Repaired incomplete prior-value and unobserved-objective false failures; restricted O056 to fields its mathematical signature consumes.\n- Used a separately identified inferred holiday calendar, retained real Friday-before-Saturday-New-Year trading, and fixed early-zone clocks and full-band contacts.\n- Corrected file-hash caching at filesystem timestamp boundaries and preserved distinct context units when matching shared candidate IDs.\n\n'
text+='- Reconciled ambiguous candle endpoints with published same-contract OHLCV; evaluated local flow with order-independent batch prices and condition-specific absence proofs.\n- Rebuilt prior-month chart context across explicit contract changes and documented empty expiration windows.\n- Bound Saint control searches to the actual selected episode and exposed corrected reference selections even in zero-candidate windows.\n\n'
text+=_table(['Family','Setup','No setup','Market input unavailable','Separate context/process'],results['family_rows'])+'\n\n'
text+=f"## Resolution of the 51 open cases\n\nAll 51 original open entry candidates have an explicit disposition: {resolved['dispositions']}. There are zero unavailable decisions across both fresh replay cohorts. [Case-by-case resolution]({root}/validation/RESOLVED_51_CASES.md) and its linked JSON retain every original candidate ID, old and new job hashes, resolved values, stages and changed references.\n\nThe 2021 prior-month reference now includes the full acquired December chart and qualifies the short setup. The 2026 partial-range candidate never sweeps the corrected full-month boundary, so it is recorded as invalidated by reference correction rather than silently omitted. No additional private account, order, size or author-label records are required.\n\n"
text+='Models are explicit interpretations of the sources. Gamma uses a call-positive/put-negative OI assumption on the acquired chain; nearest-expiry fallback is identified when 0DTE is unavailable. The key level, P-zone quantiles, state thresholds and macro composite are our definitions, not recovered proprietary formulas. This is the same bounded annual engineering sample, not an untouched holdout, full-history census, fill simulation or profitability result.\n\n'
text+=f"## Validation and preserved evidence\n\nRegistry: `{registry['registry_sha256']}`. Software: `{registry['software']['sha256']}`.\n\n"
text+=f"[Acceptance]({root}/ACCEPTANCE.json); [native model causality and preservation]({root}/validation/STRATEGY_MODELS_QA.json); [model diagnostics]({root}/diagnostics/models/README.md); [all chart examples]({root}/charts/README.md). The {accept['historical_artifacts_preserved']} protected older artifacts and {models['r9_artifacts_preserved']} accepted-r9 report/chart/validation artifacts remain unchanged; earlier attempt job hashes are checked. Earlier source-audit bodies and user edits in live documents are preserved below the new current sections.\n\n"
text+=f"The [resume check]({root}/validation/resume-verification.json) reran a completed date and preserved all 55 jobs plus its completion receipt. The primary charts use the corrected session endpoint; their consumed-input ledgers identify the strategy conditions used at the decision.\n\n"
text+='## Reproduction\n\nUse the runtime versions frozen in the selected registry. Run from `/workspace`; keep `/workspace/data` on disk and out of Git. Choose a fresh root under `/workspace/implementation/reports/phase1-live/strategy-reconstruction/` after any implementation change. Resume an unchanged run by repeating its run command.\n\n'+commands+'\n'
text+='## PHASE lines\n\n'+phase+'\n\n## Audit lines\n\n'+audit+'\n'
(base/'COMPLETION_REPORT.md').write_text(text)
plan=R/'planning/phase-1-live/STRATEGY_RECONSTRUCTION.md'
oldplan=plan.read_text().replace('## Deliverables in progress','## Delivered').replace('No unsupported holiday exception has been inserted.','The reconstructed strategy uses a separately identified inferred calendar with recorded-market checks; the earlier source-evidence calendar is preserved.')
plan.write_text(oldplan+'\n\n## Accepted reconstruction release\n\n'+summary+f'\n\n[Completion report]({base}/COMPLETION_REPORT.md). All 58 branch/extra units were replayed; personal execution units and context outputs are separate from setup qualification.\n')
conformance=R/'planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md'
conformance.write_text(conformance.read_text().replace('the source-evidence calendar remains unchanged','Friday before Saturday New Year remains regular based on recorded NQ trading; the source-evidence calendar remains unchanged'))

# Verify every preserved body and new local link before declaring docs complete.
for rel,old in snapshot.items():
 current=(R/rel).read_text()
 if rel=='planning/phase-1-live/SOURCE_CALIBRATION_DISCOVERY_HANDOFF.md':assert current==old
 else:assert old.split('\n',1)[1].lstrip() in current,rel
links=[]
for path in [Path(r['path']) for r in updated]+[base/'COMPLETION_REPORT.md']:
 content=path.read_text().split('<!-- /phase1-strategy-current -->')[0]
 for target in re.findall(r'\]\((/workspace/[^)]+)\)',content):
  assert Path(target).exists(),(path,target)
  links.append(target)
immutable_json(root/'validation/STRATEGY_DOCUMENTATION_QA.json',{'status':'pass','registry_sha256':registry['registry_sha256'],
 'files':updated,'old_bodies_preserved':len(snapshot),'existing_links_checked':len(links),'source_handoff_unchanged':True,
 'completion_report':str(base/'COMPLETION_REPORT.md'),'completion_sha256':file_digest(base/'COMPLETION_REPORT.md')})
print(base/'COMPLETION_REPORT.md')
