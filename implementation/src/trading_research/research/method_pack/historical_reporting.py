"""Reports and acceptance from exact selected v2 branch/job membership."""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import json

from .catalog import METHOD_BY_ID
from .empirical_protocol import content_hash
from .historical_runner import BASE,ROOT,load_registry,selected_root,read,read_job,verify_job,immutable_json,_job_path
from .native_resolution import NativeEvidenceError
from .historical_runner import file_digest
from .protocol import jsonable


def completed_jobs(root,registry,manifest,cohort):
    jobs=[]
    for row in manifest['branches']:
        days=['collection'] if row['method_id']=='STOIC-DATA' else registry['scope'][cohort+'_dates']
        for day in days:
            path=_job_path(root,cohort,day,row['coverage_id'])
            if not path.is_file():raise NativeEvidenceError('declared branch/date job missing: '+str(path))
            doc=verify_job(read_job(path),registry,row)
            if doc['job_state']!='completed':raise NativeEvidenceError('declared job is not completed')
            jobs.append((row,doc,{'path':str(path),'sha256':file_digest(path)}))
    return jobs


def summarize(root,registry,manifest,cohort):
    jobs=completed_jobs(root,registry,manifest,cohort);summaries=[]
    for row in manifest['branches']:
        selected=[(d,r) for b,d,r in jobs if b['coverage_id']==row['coverage_id']]
        counts={k:sum(d[k] for d,r in selected) for k in ('N_observed','n','p','f','u')}
        omissions=[]
        for d,r in selected:
            for omission in d['omissions']:omissions.append({'date':d['session_date'],**omission})
        scope=all(d['population_complete'] for d,r in selected)
        external=bool(row['input_limits']) or any(o.get('kind') in {'external_record','external_definition','external_operand'} for o in omissions)
        status='observed_subset_with_input_limits' if omissions or external or not scope else 'bounded_observed_population_measured'
        summary={**{k:row[k] for k in ('coverage_id','method_id','branch','extra_unit','observation_unit','source_definition','scanner','assumption_ids','input_limits')},
            **counts,'cohort':cohort,'jobs':len(selected),'population_complete':scope,'exchange_feed_completeness':None,
            'status':status,'omissions':omissions,'software_state':'executed',
            'author_exact_measurement':'unknown','faithful_disagreements':None,
            'per_date':[{'date':d['session_date'],**{k:d[k] for k in ('N_observed','n','p','f','u','population_complete')},
                'native_executions':d['native_executions'],'artifact':r,'omissions':d['omissions']} for d,r in selected],
            'postsequence_observations':dict(Counter(o['result'] for d,r in selected for o in d['outcomes'])),
            'denominator_note':'n=p+f; N_observed=n+u. Counts are selected branch/unit observations, not author trades, fills or a full-archive census.'}
        summaries.append(summary)
    return summaries,jobs


def _table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |',
        *['| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in rows]])


def _write_text(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text.rstrip()+'\n')


def report(run_root):
    root=selected_root(run_root);registry,manifest=load_registry(root)
    evaluation,jobs=summarize(root,registry,manifest,'evaluation')
    pilot,pilot_jobs=summarize(root,registry,manifest,'pilot')
    body={'schema':'phase1-native-results-v2','registry_sha256':registry['registry_sha256'],
        'coverage_sha256':manifest['manifest_sha256'],'software_sha256':registry['software']['sha256'],
        'scope':registry['scope'],'evaluation':evaluation,'pilot':pilot,
        'cohort_overlap':'pilot and evaluation share some dates; never pool their populations',
        'pooled_family_win_rate':None,'jobs':{'evaluation':len(jobs),'pilot':len(pilot_jobs)},
        'evidence_mode':'operational research assumptions; author-exact verdict remains unknown',
        'preserved_historical_manifest_sha256':registry['prior_manifest_sha256']}
    body['results_sha256']=content_hash(body)
    immutable_json(root/'RESULTS.json',body)
    controls=read(root/'validation/controls.json');suite=read(root/'validation/full-suite.json')
    if controls['failures'] or suite['exit_code'] or any(r['software_sha256']!=registry['software']['sha256'] for r in (controls,suite)):
        raise NativeEvidenceError('reports require passing validation for the selected software')
    phase=[];audit=[]
    for method in METHOD_BY_ID:
        rows=[r for r in evaluation if r['method_id']==method]
        n=sum(r['n'] for r in rows if not r['extra_unit'])
        path=root/'methods'/(method+'.md')
        text=f'# {method}: current v2 research\n\n'
        text+='The declared annual sample covers '+', '.join(registry['scope']['evaluation_dates'])+'. Every declared branch/date job is retained. '
        text+='These are ordered market or process observations under frozen research assumptions. They are not reconstructed author trades or fills.\n\n'
        text+=_table(['Branch/unit','Unit','N observed','n','p','f','u','Scope'],[[('unit: ' if r['extra_unit'] else '')+r['branch'],r['observation_unit'],r['N_observed'],r['n'],r['p'],r['f'],r['u'],r['status']] for r in rows])+'\n\n'
        for r in rows:
            text+=f"## {r['branch']} ({'additional unit' if r['extra_unit'] else 'catalog branch'})\n\n"
            text+=r['source_definition']['operation']+'. Source: '+r['source_definition']['citation']+'.\n\n'
            text+=f"Scanner: `{r['scanner']}`. Native jobs: {r['jobs']}. Observed sequence p/f/u: {r['p']}/{r['f']}/{r['u']}; n={r['n']}.\n\n"
            if r['input_limits']:
                for limit in r['input_limits']:
                    text+=f"{'Original source-audit requirement (see reconstruction report for implemented models)' if registry.get('strategy_reconstruction') else 'Required input'} ({', '.join(limit['operands'])}): {limit['required']}. {limit['recovery']} Citation: {limit['citation']}.\n\n"
            reasons=Counter(o.get('reason',o.get('required','unspecified')) for o in r['omissions'])
            if reasons:text+='Observed scope/record limits: '+'; '.join(f'{k} ({v} job records)' for k,v in reasons.items())+'.\n\n'
            text+=_table(['Date','n','p','f','u','Observed scope complete','Executions','Evidence'],
                [[d['date'],d['n'],d['p'],d['f'],d['u'],d['population_complete'],d['native_executions'],f"[job]({d['artifact']['path']})"] for d in r['per_date']])+'\n\n'
        text+='Counts from dependent branches are not a pooled family win rate. The pilot is separate. Full-feed completeness and author-exact measurement remain unestablished.\n'
        _write_text(path,text)
        phase.append([method,'v2 bounded native research',n,'not established','executed; input limits retained',str(path.relative_to(ROOT))])
        audit.append([method,METHOD_BY_ID[method],'controls and native replay pass','pass',0,0,'selected source controls; native jobs retained; author-exact unknown'])
    text='# Phase 1 v2 native replay\n\n'+registry['scope']['sample_kind']+'.\n\n'
    text+='Registry/run 2.0.0; registry hash `'+registry['registry_sha256']+'`. NQ native contracts, event-time executions, explicit same-contract prior scope and product-session policy. The accepted v1.0.0/v1.0.2 comparison is preserved.\n\n'
    text+=_table(['Family','Branch/unit','n','p','f','u','Status'],[[r['method_id'],('unit:' if r['extra_unit'] else '')+r['branch'],r['n'],r['p'],r['f'],r['u'],r['status']] for r in evaluation])+'\n\n'
    text+='## PHASE lines\n\n'+_table(['family','variant','n','faithful_disagreements','status','report path'],phase)+'\n\n'
    text+='## Audit lines\n\n'+_table(['family','id','verdict','fixture','leakage','proxy-as-faithful','notes'],audit)+'\n'
    _write_text(root/'RESULTS.md',text)
    immutable_json(root/'FAMILY_TABLES.json',{'phase':phase,'audit':audit})
    print(_table(['family','variant','n','faithful_disagreements','status','report path'],phase))
    print(_table(['family','id','verdict','fixture','leakage','proxy-as-faithful','notes'],audit))
    if registry.get('strategy_reconstruction'):
        from .strategy_reporting import report_strategy
        report_strategy(root,registry,manifest,jobs,pilot_jobs)
    return {'results_sha256':body['results_sha256'],'evaluation_jobs':len(jobs),'pilot_jobs':len(pilot_jobs),
        'coverage_units':len(evaluation),'report':str(root/'RESULTS.md')}


def verify(run_root):
    root=selected_root(run_root);registry,manifest=load_registry(root)
    errors=[];unit_ids=set();job_count=0;native_count=0;fixtures=read(root/'validation/controls.json')
    suite=read(root/'validation/full-suite.json')
    for record in (fixtures,suite):
        if record['software_sha256']!=registry['software']['sha256']:errors.append('verification code/test identity stale')
    if suite['exit_code']!=0:errors.append('full suite failed')
    if file_digest(Path(suite['log_path']))!=suite['log_sha256']:errors.append('full-suite log changed')
    if fixtures['failures']:errors.append('source/native controls failed')
    if file_digest(Path(fixtures['details']['path']))!=fixtures['details']['sha256']:errors.append('control details changed')
    for regression in fixtures['regressions']:
        if regression['exit_code'] or file_digest(Path(regression['path']))!=regression['sha256']:errors.append('regression validation failed or changed')
    if set(fixtures['coverage_ids'])!={r['coverage_id'] for r in manifest['branches']}:errors.append('controls omit branch/unit')
    for cohort in ('pilot','evaluation'):
        summaries,jobs=summarize(root,registry,manifest,cohort)
        for row,doc,receipt in jobs:
            unit_ids.add(row['coverage_id']);job_count+=1;native_count+=doc['native_executions']
            if any(e['research_verdict']=='pass' and set(e['selected_fields'])-set(e['values']) for e in doc['episodes']):
                errors.append('accepted episode has unbound operands')
        if len(summaries)!=58:errors.append('wrong exact branch/unit membership')
    historical=read(BASE/'PRESERVATION.json')
    changed=[name for name,digest in historical['historical_files'].items() if file_digest(ROOT/name)!=digest]
    if changed:errors.append('historical artifacts changed: '+str(changed))
    integration=read(BASE/'NATIVE_INTEGRATION.json')
    if len(integration['old_tape_windows'])!=8 or any(w['shared_observed_multiset_equal'] is False for w in integration['old_tape_windows']):
        errors.append('native eight-window membership integration failed')
    if not native_count:errors.append('no actual native market evidence')
    if integration['tail']['fresh_rows']!=829 or integration['tail']['mismatches']:errors.append('tail integration differs')
    recovery=integration['derived_recovery']
    if (recovery['recovered_study_keys'],recovery['august_equal_overlaps'],recovery['admitted_unique_keys'])!=(12420,780,12420):errors.append('recovery admission differs')
    charts=read(root/'charts/manifest.json');qa=read(root/'charts/VISUAL_QA.json')
    if {r['coverage_id'] for r in charts['examples']}!=unit_ids:errors.append('diagnostic charts omit a unit')
    for example in charts['examples']:
        if file_digest(Path(example['path']))!=example['sha256']:errors.append('chart artifact changed')
    if set(qa['inspected_paths'])!={e['path'] for e in charts['examples']} or qa['unresolved_layout_issues']:
        errors.append('visual verification incomplete')
    result=read(root/'RESULTS.json')
    if result['registry_sha256']!=registry['registry_sha256']:errors.append('report used a different registry')
    report_again={c:summarize(root,registry,manifest,c)[0] for c in ('pilot','evaluation')}
    if any(result[c]!=jsonable(report_again[c]) for c in report_again):errors.append('report counts differ from completed jobs')
    out={'schema':'phase1-native-acceptance-v2','registry_sha256':registry['registry_sha256'],
        'software_sha256':registry['software']['sha256'],'software_acceptance':'pass' if not errors else 'fail',
        'errors':errors,'exact_coverage_units':len(unit_ids),'completed_jobs':job_count,
        'historical_artifacts_preserved':len(historical['historical_files'])-len(changed),
        'native_integration_sha256':integration['report_sha256'],'full_historical_author_method_measurement':'not complete',
        'remaining_limits':'exact external operands and population-scope gaps are retained per branch; no private fills/account reconstruction',
        'fixtures':fixtures['counts'],'full_suite':suite['summary'],'charts':len(charts['examples'])}
    immutable_json(root/'ACCEPTANCE.json',out)
    if errors:raise NativeEvidenceError('acceptance failed: '+'; '.join(errors))
    return out
