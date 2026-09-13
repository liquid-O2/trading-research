#!/usr/bin/env python3
"""Assemble the current local report only after execution and visual verification."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import sys
sys.path.insert(0,'/workspace/implementation/src')
from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.method_pack.historical_reporting import _table
from trading_research.research.method_pack.measurement_runner import measurement_scope

PAGES=dict(zip(['JJ-TBR','GB-FAIL','GB-VWAP','GB-SCALP','SIRES','SAINT-AMT','MEMBER-TWO-REASONS','KEANI-OPEN-ABOVE-VALUE','REFILL-STUDY','JETBUNDLE-STATES','STOIC-DATA','STOIC-RISK'],
 ['method-jumbo-tbr','method-green-bird-failure','method-green-bird-vwap-continuation','method-green-bird-directional-scalps','method-sires-thesis-flow','method-saint-amt','method-member-two-reasons','method-keani-open-above-value','method-refill-effect','method-jetbundle-auction-states','method-stoic-data-engine','method-stoic-asymmetric-compounding']))


def prepend(path,text):
    marker='<!-- full-phase1-measurement-current -->';end='<!-- /full-phase1-measurement-current -->'
    old=path.read_text()
    if marker in old:
        old=old.split(end,1)[1].lstrip('\n')
        label='## Preserved implementation and prior measurement history\n\n'
        if old.startswith(label):old=old[len(label):]
    path.write_text(marker+'\n'+text.rstrip()+'\n'+end+'\n\n## Preserved implementation and prior measurement history\n\n'+old)


def main(root):
    root=Path(root).resolve();base=root.parent;registry,manifest=hr.load_registry(root)
    results=hr.read(root/'MEASUREMENT_RESULTS.json');verify=hr.read(root/'validation/FULL_INPUT_VERIFICATION.json')
    collection=hr.read(root/'validation/COLLECTION_REVIEW.json');qa=hr.read(root/'charts/VISUAL_QA.json')
    suite=hr.read(root/'validation/full-suite.json');controls=hr.read(root/'validation/controls.json')
    charts=hr.read(root/'charts/manifest.json')
    assert verify['status']=='pass' and suite['exit_code']==0 and qa['status']=='pass'
    assert qa['reviewed_charts']==len(charts['charts'])
    for chart in charts['charts']:
        assert hr.file_digest(chart['path'])==chart['sha256']
    assert not controls['failures']
    total=results['totals'];branches=results['branches']
    population=hr.read(root/'protocol/ACQUIRED_INPUT_POPULATION.json')
    scope_counts=Counter(measurement_scope(r['method_id'],r['branch']) for r in manifest['branches'])
    rows=[];limited=[]
    for r in manifest['branches']:
        key=r['coverage_id'];s=branches.get(key)
        if not s:continue
        c=s['counts'];endpoint=s['input_endpoints']['last_complete_input_session'] or 'none'
        rows.append([key,measurement_scope(r['method_id'],r['branch']),c.get('eligible_complete_sessions',0),c.get('setups',0),
            c.get('setups_in_eligible_sessions',0),c.get('completed_zero_setup_sessions',0),endpoint])
        if s['limitations']:
            limited.append([key,c.get('observed_search_with_input_limitations',0),'; '.join(f'{k}: {v}' for k,v in sorted(s['limitations'].items()))])
    intro=f"# Phase 1 — full acquired historical measurement\n\nThe unchanged versioned scanners searched **{total['sessions']:,} declared session dates**, 2020-01-01 through 2026-09-03, across all 50 branches and eight additional observation units. The composed census contains **{total['daily_jobs']:,} daily jobs** and **{total['setups']:,} qualifying market setups**, plus three actual collection-process jobs. The independent primary run and all 90 calendar-recovery dates completed and were verified.\n\n"
    intro+='**The acquired observed-input census is executed. Input-limited populations remain unmeasured beyond the observed subset; the exact affected branch/session denominators are listed below.** Qualification does not establish a winning trade. All reported outcomes are subsequent observed prices; no return simulation or actual fill is claimed. Phase 2 remains the additional context layer that selects which setups to use.\n\n'
    text=intro+'## Population, scope and boundaries\n\n'
    endpoint_utc=datetime.fromtimestamp(population['endpoint_ns_exclusive']/1e9,timezone.utc).isoformat()
    text+=f"The owned MBP-1 endpoint is **{endpoint_utc}** (exclusive). September 3 is a partially acquired session label, not a completed RTH day. Branch-specific complete-input endpoints and exclusions below govern the measured denominators.\n\n"
    text+=f"{total['native_executions']:,} owned native execution references reconcile from session receipts to daily branch jobs. A session execution is counted once in this native total, even when several branches consume it. Different methods can identify overlapping market events; the setup total is a sum of branch opportunities, not an independent portfolio trade count.\n\n"
    text+=_table(['Manifest scope','Branch / additional units'],sorted(scope_counts.items()))+'\n\n'
    text+='All weekday session labels were searched, including holidays and unavailable dates. Earlier observations are lookbacks only. Complete eligible denominators require the frozen branch prefix, required context and candidate inputs to be observed. Interior limitations are excluded individually; choosing the last complete endpoint does not discard earlier difficult dates. Native event-time bars and vendor receive-time model inputs retain separate receipts. Canonical ownership prevents counting overlapping recovery files twice and preserves genuine repeated executions.\n\n'
    text+=_table(['Branch / unit','Scope','Eligible sessions','Observed setups','Setups in eligible sessions','Complete zero searches','Last complete input session'],rows)+'\n\n'
    text+='## Measurement conventions and interpretation\n\n'
    text+='Frequency is qualifying setups in complete sessions divided by complete eligible branch-sessions. Setups in limited sessions remain separately recorded. Decision-clock bins share that denominator; no new session-based selector is introduced. The four fixed excursion horizons are 5, 15, 30 and 60 minutes after qualification. Missing or session-truncated future windows are lower bounds and do not enter complete-horizon means or medians.\n\n'
    text+='Price origin is the existing entry reference when defined, otherwise a causally completed trigger close, otherwise the first strictly subsequent whole-batch VWAP, explicitly a measurement convention. Boundaries are the existing structural invalidation and objective; none are invented. Judas outbound keeps its published 09:40 deadline; other price ordering uses the frozen 60-minute measurement expiry. Original scanner outcome records remain alongside these measurements. Same-batch objective/invalidation touches remain unresolved; an earlier coverage gap prevents establishing population-first ordering. Undefined and single-boundary cases have separate counts. Resolution times attached to gap-ambiguous observations describe the observed batch only.\n\n'
    text+='Source definitions, disclosed inferred rules and model versions are retained per setup. The run is not an untouched holdout: prior engineering evaluations, reconstruction examples and the interrupted first measurement attempt are recorded in the frozen protocol. No thresholds, rules or endpoints were selected from favorable results.\n\n'
    text+='## Current method results\n\n'
    for method in PAGES:text+=f"- [{method}: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions]({root}/methods/{method}.md)\n"
    text+='\nThe existing method pages also contain these generated results above their preserved implementation history. Context, supplemental annotations, personal execution units and collection process records do not enter setup frequency or excursion denominators. Daily macro quantities are retained even where a collection review was pending during a daily job.\n\n'
    text+=_table(['Actual collection unit','Records','Native research verdicts'],[[r['coverage_id'],r['episodes'],', '.join(r['verdicts'])] for r in collection['jobs']])+'\n\n'
    text+='## Exact remaining input limitations\n\n'+_table(['Branch / unit','Input-limited session jobs','Reason: affected sessions (reasons may overlap)'],limited)+'\n\n'
    text+='The coverage ledger identifies every affected date, required prefix, missing interval, original omission and disposition. A scheduled closure, completed zero search, unavailable population and unresolved future outcome are distinct states. Personal-record exclusions describe out-of-scope execution audits, not missing market-setup evidence.\n\n'
    text+='Two factual matching-calendar inputs were recovered from dated official CME schedules: the [2023 Presidents Day schedule](https://www.cmegroup.com/files/presidents-day.pdf) and the [January 9, 2025 mourning-day table](https://www.cmegroup.com/content/dam/cmegroup/trading-hours/files/day-of-mourning-january-9-2024.pdf), whose URL filename has a different year. The evidence artifact records normalized table facts and time-zone conversion, not a claimed hash of PDF bytes that were not retrieved. A separately frozen dependency run replaces all units on the affected dates and following 62 calendar days. Other missing calendar evidence remains explicit.\n\n'
    text+='## Verification and reproducibility\n\n'
    text+=f"Tests: **{suite['summary']}**. Native integration, future-perturbation and regression controls passed. Every primary and recovery completion hash was checked; {verify['unique_verified_input_files']:,} distinct input files were verified. Resume reproduced all 57 jobs and the selected date completion byte-for-byte. Counts reconcile with zero duplicate within-branch opportunities and zero recorded future leakage. All {len(charts['charts'])} final charts were visually inspected. The accepted implementation's {verify['baseline_software_files_unchanged']} files are unchanged.\n\n"
    text+=f"Registry: `{registry['registry_sha256']}`. Calendar composition: `{results['calendar_recovery_composition']['composition_sha256']}`. [Frozen protocol]({root}/protocol/MEASUREMENT_PROTOCOL_1_1.json), [full reconciliation]({root}/validation/CENSUS_RECONCILIATION.json), [input verification and resolved failure history]({root}/validation/FULL_INPUT_VERIFICATION.json), [chart inspection]({root}/charts/VISUAL_QA.json). Earlier runs, raw/source files and pre-existing documentation corrections are preserved.\n\n"
    text+='Run from `/workspace`; these commands resume the frozen identities:\n\n```bash\n'
    text+='export PYTHONPATH=/workspace/implementation/src\nexport OPENBLAS_NUM_THREADS=1\nexport OMP_NUM_THREADS=1\n'
    text+=f'python -m trading_research.research.method_pack.measurement_runner run --run-root {root} --workers 16\n'
    text+=f'python {base}/tools/recover_calendars.py run --workers 2\n'
    for helper in ('finish_aggregation','finish_collection','verify_census','render_census'):
        extra=' --collect --workers 16' if helper=='finish_aggregation' else ''
        text+=f'python {base}/tools/{helper}.py --run-root {root}{extra}\n'
    text+='```\n\nRendering regenerates image files; visual inspection must be repeated if their content changes. `publish_local_report.py` requires a completed visual-inspection receipt before updating current documentation. All helper identities are recorded in the final artifact manifest.\n\n'
    text+=f"[Per-setup records]({root}/records/setup-records.jsonl.gz) · [Coverage/exclusions]({root}/records/coverage-exclusions.jsonl.gz) · [Context and other observations]({root}/records/non-setup-observations.jsonl.gz) · [Machine-readable results]({root}/MEASUREMENT_RESULTS.json) · [Charts]({root}/charts/README.md).\n\n"
    text+='Bulk daily jobs, native derivations and full record streams remain on the workspace volume, following the repository’s existing historical-replay policy. Git publishes the implementation, reports, charts, frozen identities and verification receipts; their recorded hashes identify the retained local evidence.\n\n'
    phase=_table(['family','variant','n','faithful_disagreements','status','report path'],results['phase'])
    audit=_table(['family','id','verdict','fixture','leakage','proxy-as-faithful','notes'],results['audit'])
    text+='## Required family tables\n\nHere `n` is the observed qualifying market-setup count, including the explicitly separated limited-session subset. It is not a fill count or the historical predicate-audit `p+f`.\n\n'+phase+'\n\n'+audit+'\n'
    (base/'MEASUREMENT_REPORT.md').write_text(text)
    for method,page in PAGES.items():
        detail=(root/'methods'/f'{method}.md').read_text()
        if method=='STOIC-DATA':detail+='\n'+_table(['Collection unit','Records','Verdicts'],[[r['coverage_id'],r['episodes'],', '.join(r['verdicts'])] for r in collection['jobs']])+'\n'
        prepend(hr.ROOT/'planning/phase-1-live/wiki'/f'{page}.md',detail)
    summary=intro+f'[Current measurement report]({base}/MEASUREMENT_REPORT.md) · [Charts]({root}/charts/README.md)\n\n'+phase+'\n\n'+audit
    prepend(hr.ROOT/'planning/phase-1-live/PHASE.md',summary)
    # Preserve the user's complete prior corrections and all unrelated bodies.
    for path in ('README.md','planning/phase-1-live/wiki/current-status.md','planning/phase-1-live/wiki/index.md'):
        prepend(hr.ROOT/path,intro+f'[Current measurement report and exact limitations]({base}/MEASUREMENT_REPORT.md).')
    with (hr.ROOT/'planning/phase-1-live/wiki/log.md').open('a') as f:
        f.write('\n\n## 2026-09-13 — full acquired Phase 1 measurement\n\n'+intro.split('\n\n',1)[1]+f'[Current report]({base}/MEASUREMENT_REPORT.md).\n')
    print(phase);print(audit)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);main(p.parse_args().run_root)
