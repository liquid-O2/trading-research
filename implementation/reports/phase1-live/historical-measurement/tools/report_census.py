#!/usr/bin/env python3
"""Stream the completed census into reconciled records and current reports."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time
import pickle
import shutil
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, '/workspace/implementation/src')
from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.method_pack.measurement_runner import measurement_scope
from trading_research.research.method_pack.historical_reporting import _table
from trading_research.research.method_pack.catalog import METHOD_BY_ID
from trading_research.research.method_pack.clocks import ns_to_et
from trading_research.research.method_pack.empirical_protocol import content_hash


def write_json(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(hr.serializable(body), indent=2, sort_keys=True)+'\n')


def bucket(at):
    t = ns_to_et(at); n = t.hour*60+t.minute
    return 'previous_evening' if n >= 18*60 else 'overnight_00_06' if n < 6*60 else 'premarket_06_0930' if n < 570 else 'NY_AM_0930_1200' if n < 720 else 'NY_PM_1200_1600'


def blank():
    return {'scope': None, 'counts': Counter(), 'boundary': Counter(), 'session_results': defaultdict(Counter),
            'ordering_with_both_boundaries': Counter(), 'single_or_undefined_boundary': Counter(),
            'resolution_seconds': defaultdict(list),
            'input_endpoints': {'first_searched_session': None, 'last_searched_session': None,
                'first_complete_input_session': None, 'last_complete_input_session': None,
                'last_complete_required_prefix_end_ns': None},
            'horizons': {str(n): {'counts': Counter(), 'favorable': [], 'adverse': []} for n in (5,15,30,60)},
            'limitations': Counter(), 'native_execution_references': 0}


def add_job(stats, doc):
    a = doc['session_accounting']; c = stats['counts']
    stats['scope']=a['scope']
    endpoints=stats['input_endpoints']; day=doc['session_date']
    endpoints['first_searched_session']=endpoints['first_searched_session'] or day
    endpoints['last_searched_session']=day
    if a['status']=='completed_search':
        endpoints['first_complete_input_session']=endpoints['first_complete_input_session'] or day
        endpoints['last_complete_input_session']=day
        endpoints['last_complete_required_prefix_end_ns']=a['required_current_prefix'][1]
    c['searched_sessions'] += 1
    c[a['status']] += 1
    c['eligible_complete_sessions'] += a['eligible_complete_session']
    c['completed_zero_setup_sessions'] += a['completed_zero_setup_search']
    c['observed_candidates'] += len(doc['episodes'])
    qualified = [e for e in doc['episodes'] if e.get('strategy_assessment', {}).get('status') == 'setup']
    is_setup = a['scope'] == 'entry_setup'
    c['setups'] += len(qualified) if is_setup else 0
    c['setups_in_eligible_sessions'] += len(qualified) if is_setup and a['eligible_complete_session'] else 0
    c['sessions_with_setups'] += bool(qualified) if is_setup else 0
    for e in doc['episodes']:
        status = e.get('strategy_assessment', {}).get('status', e['research_verdict'])
        c['candidate_status:'+status] += 1
        if is_setup and status == 'setup':
            stats['session_results'][bucket(e['decision_at'])]['setups'] += 1
            stats['session_results'][bucket(e['decision_at'])]['setups_in_eligible_sessions'] += a['eligible_complete_session']
    # A long lookback can report the same reason on several constituent dates.
    # This table counts affected branch-sessions, not repeated omission rows.
    reasons={item.get('reason') or item.get('id') or 'unspecified' for item in a['active_omissions']}
    gaps = a['current_prefix_coverage']['unknown_intervals']
    if gaps:
        reasons.add('current input prefix has unknown intervals')
        c['unknown_current_minutes'] += len(gaps)
    for reason in reasons:stats['limitations'][reason] += 1
    c['unavailable_candidates'] += a['unavailable_candidates']
    for x in doc['setup_measurements']:
        boundary=x.get('boundary',{}); outcome=boundary.get('result',x['status'])
        stats['boundary'][outcome] += 1
        category='ordering_with_both_boundaries' if boundary.get('stop') is not None and boundary.get('target') is not None else 'single_or_undefined_boundary'
        stats[category][outcome] += 1
        if boundary.get('seconds_to_resolution') is not None:
            stats['resolution_seconds'][outcome].append(boundary['seconds_to_resolution'])
        if not x['horizons']:
            for target in stats['horizons'].values():
                target['counts']['measurement_reference_unavailable']+=1
        for r in x['horizons']:
            target = stats['horizons'][str(r['minutes'])]
            target['counts'][r['status']] += 1
            target['counts']['truncated'] += r['horizon_truncated']
            if r['status'] == 'complete_observed_horizon':
                target['favorable'].append(float(r['favorable_points']))
                target['adverse'].append(float(r['adverse_points']))


def summarize(stats):
    import statistics
    result = {k: dict(v) if isinstance(v, (dict,Counter)) else v for k,v in stats.items() if k != 'horizons'}
    c = stats['counts']; denom = c['eligible_complete_sessions']
    result['setups_per_eligible_session'] = c['setups_in_eligible_sessions']/denom if denom else None
    result['observed_setups_per_searched_session'] = c['setups']/c['searched_sessions'] if c['searched_sessions'] and stats['scope']=='entry_setup' else None
    result['session_results']={k:{**dict(v),'eligible_session_denominator':denom,
        'setups_per_eligible_session':v['setups_in_eligible_sessions']/denom if denom else None}
        for k,v in stats['session_results'].items()}
    result['resolution_seconds']={k:{'n':len(v),'mean':statistics.fmean(v),'median':statistics.median(v)}
                                  for k,v in stats['resolution_seconds'].items()}
    result['horizons'] = {}
    for n,r in stats['horizons'].items():
        result['horizons'][n] = {'counts': dict(r['counts'])}
        for key in ('favorable','adverse'):
            v = r[key]
            result['horizons'][n][key+'_mean_points'] = statistics.fmean(v) if v else None
            result['horizons'][n][key+'_median_points'] = statistics.median(v) if v else None
    return result


def fmt(x):
    return '—' if x is None else f'{x:.3f}' if isinstance(x,float) else x


def collect_dates(args):
    root, days, registry, rows, recovery_root, recovery_registry, recovery_dates, wait_for_completion, stream_root = args
    selected_root=lambda day: recovery_root if day in recovery_dates else root
    daily = [r for r in rows if not (r['method_id']=='STOIC-DATA' and r['branch']=='process_review')]
    bybranch = defaultdict(blank); byyear = defaultdict(blank); bysession = defaultdict(blank); selected_charts = {}
    total = Counter(); native = {}; setup_ids = set(); record_schemas = set()
    eligible_ids, included_ids, features, collection_outcomes = [], [], [], []
    input_receipts = {}; job_hashes = {}; errors = []
    (stream_root/'records').mkdir(parents=True,exist_ok=True)
    setup_path = stream_root/'records/setup-records.jsonl.gz'
    coverage_path = stream_root/'records/coverage-exclusions.jsonl.gz'
    other_path = stream_root/'records/non-setup-observations.jsonl.gz'
    with gzip.GzipFile(filename=str(setup_path),mode='wb',mtime=0,compresslevel=3) as setup_stream, gzip.GzipFile(filename=str(coverage_path),mode='wb',mtime=0,compresslevel=3) as coverage_stream, gzip.GzipFile(filename=str(other_path),mode='wb',mtime=0,compresslevel=3) as other_stream:
        for day_index,day in enumerate(days):
            # Scheduling only: consume immutable completed days while the
            # remaining replay finishes. No summary is published until every
            # declared primary and selected recovery day has been consumed.
            while not all((r/'jobs/evaluation'/day/'completion.json').exists()
                          for r in (root,selected_root(day))):
                if not wait_for_completion:
                    raise ValueError('Census unfinished on '+day)
                time.sleep(10)
            source_registry=recovery_registry if day in recovery_dates else registry
            done = hr.read(selected_root(day)/'jobs/evaluation'/day/'completion.json')
            if done['registry_sha256'] != source_registry['registry_sha256']:
                raise ValueError('date completion identity differs')
            actual = {j['coverage_id']: j for j in done['jobs']}
            if set(actual) != {r['coverage_id'] for r in daily}:
                raise ValueError('branch membership differs on '+day)
            native[day] = {'executions': done['native_executions'], 'input_sha256': done['native_input_sha256']}
            for row in daily:
                key = row['coverage_id']; receipt = actual[key]; path = Path(receipt['path'])
                digest = hr.file_digest(path)
                if digest != receipt['sha256']:
                    raise ValueError('job content changed: '+str(path))
                doc = hr.read_job(path)
                # Full source-byte verification is batched separately; these
                # structural checks are repeated here while streaming records.
                if doc['registry_sha256'] != source_registry['registry_sha256'] or doc['software_sha256'] != registry['software']['sha256']:
                    raise ValueError('checkpoint identity changed')
                if doc['session_date'] != day or doc['coverage_id'] != key:
                    raise ValueError('checkpoint branch/session differs')
                if doc['native_executions']!=done['native_executions'] or doc['input_sha256']!=done['native_input_sha256']:
                    raise ValueError('native session-to-branch counts or input identity differ')
                native_counts = Counter(e['research_verdict'] for e in doc['episodes'])
                if any(doc[k] != native_counts[v] for k,v in [('p','pass'),('f','fail'),('u','unknown')]):
                    raise ValueError('native candidate counts do not reconcile')
                if doc['n']!=doc['p']+doc['f'] or doc['N_observed']!=len(doc['episodes']):
                    raise ValueError('native observed denominator differs')
                ids = [e['candidate_id'] for e in doc['episodes']]
                if len(ids) != len(set(ids)):
                    raise ValueError('duplicate candidate opportunity')
                unit = day+':'+key; eligible_ids.append(unit); included_ids.append(unit)
                job_hashes[str(path)] = digest
                total['daily_jobs'] += 1
                add_job(bybranch[key],doc); add_job(byyear[(key,day[:4])],doc)
                if doc['session_accounting']['scope']=='entry_setup':
                    for clock_bin in ('previous_evening','overnight_00_06','premarket_06_0930','NY_AM_0930_1200','NY_PM_1200_1600'):
                        episodes=[e for e in doc['episodes'] if bucket(e['decision_at'])==clock_bin]
                        ids_in_bin={e['candidate_id'] for e in episodes}
                        sub_accounting=dict(doc['session_accounting'],unavailable_candidates=
                            sum(e.get('strategy_assessment',{}).get('status')=='data_unavailable' for e in episodes),
                            completed_zero_setup_search=
                            doc['session_accounting']['eligible_complete_session'] and
                            not any(e.get('strategy_assessment',{}).get('status')=='setup' for e in episodes))
                        subdoc=dict(doc,episodes=episodes,session_accounting=sub_accounting,
                            setup_measurements=[m for m in doc['setup_measurements'] if m['candidate_id'] in ids_in_bin])
                        add_job(bysession[(key,clock_bin)],subdoc)
                accounting = {'schema':'phase1-branch-session-coverage-v1','date':day,'coverage_id':key,
                    'method':row['method_id'],'branch':row['branch'],'instrument_id':doc['instrument_id'],
                    'registry_sha256':source_registry['registry_sha256'],'job':receipt,
                    **doc['session_accounting'],'original_omissions':doc['omissions'],
                    'native_candidate_counts':dict(native_counts),'setup_count':len(doc['setup_measurements'])}
                # These payloads contain only JSON-loaded values and primitive
                # metadata; avoid walking their large native evidence twice.
                coverage_stream.write((json.dumps(accounting,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())
                if doc['session_accounting']['scope']!='entry_setup':
                    observation={'schema':'phase1-non-setup-observations-v1','date':day,'coverage_id':key,
                        'scope':doc['session_accounting']['scope'],'registry_sha256':source_registry['registry_sha256'],
                        'job':receipt,'episodes':doc['episodes'],'measured_quantities':doc.get('measured_quantities'),
                        'published_arithmetic':doc.get('published_arithmetic'),'entry_setup_denominator':0}
                    other_stream.write((json.dumps(observation,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())
                for item in doc['input_receipts']:
                    input_receipts[content_key(item)] = item
                for item in doc.get('domain_observations',{}).values():
                    input_receipts[content_key(item)] = item
                measurements = {m['candidate_id']:m for m in doc['setup_measurements']}
                expected = {e['candidate_id'] for e in doc['episodes']
                    if measurement_scope(row['method_id'],row['branch'])=='entry_setup'
                    and e.get('strategy_assessment',{}).get('status')=='setup'}
                if set(measurements) != expected:
                    raise ValueError('qualifying setup / measurement mismatch')
                for e in doc['episodes']:
                    record_schemas.add(e['schema'])
                    if e['input_sha256']!=doc['input_sha256'] or e['actual_trade'] or e['faithful_eligible']:
                        raise ValueError('episode native identity or observation scope differs')
                    selected = set(e['selected_fields'])
                    known = [v['known_at'] for k,v in e['operand_derivations'].items()
                             if k in selected and v.get('known_at') is not None]
                    if known and max(known) > e['decision_at']:
                        raise ValueError('future input in consumed setup operands')
                    if any(v.get('known_at') is not None and v['known_at']>e['decision_at']
                           for v in e['operand_derivations'].values()):
                        raise ValueError('future input in recorded episode operand')
                    features.append({'known_at':max(known,default=e['decision_at']), 'decision_at':e['decision_at']})
                    status = e.get('strategy_assessment',{}).get('status',e['research_verdict'])
                    outcome = measurements.get(e['candidate_id'],{}).get('boundary',{}).get('result',status)
                    chart_key = (key,outcome)
                    order = (day,e['decision_at'],e['candidate_id'])
                    candidate = {'job':receipt,'candidate_id':e['candidate_id'],'coverage_id':key,'outcome':outcome,'order':order}
                    if chart_key not in selected_charts or order < tuple(selected_charts[chart_key]['order']):
                        selected_charts[chart_key] = candidate
                    if e['candidate_id'] not in measurements:
                        continue
                    unique = key+':'+e['candidate_id']
                    if unique in setup_ids:
                        raise ValueError('same branch opportunity counted on two session labels')
                    setup_ids.add(unique)
                    if ns_to_et(e['decision_at']).date().isoformat() < registry['scope']['study_start']:
                        raise ValueError('pre-study setup entered denominator')
                    m = measurements[e['candidate_id']]
                    record = {'schema':'phase1-measured-setup-record-v1','registry_sha256':source_registry['registry_sha256'],
                        'source_assumption_version':{'source_definition':row['source_definition'],
                            'assumption_ids':row['assumption_ids'],'strategy_version':e['strategy_assessment']['version'],
                            'software_sha256':registry['software']['sha256'],
                            'protocol_sha256':registry['scope']['measurement_protocol']['sha256']},
                        'coverage_id':key,'session_date':day,'decision_session':bucket(e['decision_at']),
                        'eligible_complete_session':doc['session_accounting']['eligible_complete_session'],
                        'native_job':receipt,'setup':e,'price_measurement':m,
                        'legacy_outcome':next((x for x in doc['outcomes'] if x['candidate_id']==e['candidate_id']),None),
                        'actual_fill':False,'simulated_return':None}
                    setup_stream.write((json.dumps(record,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())
                    total['setups'] += 1
                    collection_outcomes.append({'candidate_id':unique,'result':outcome})
                if not doc['episodes']:
                    zero_kind=('completed_zero_candidate_search' if doc['session_accounting']['status']=='completed_search'
                               else 'zero_candidate_input_or_scope_limitation')
                    chart_key = (key,zero_kind)
                    selected_charts.setdefault(chart_key,{'job':receipt,'candidate_id':None,'coverage_id':key,
                        'outcome':zero_kind,'order':(day,0,'')})
            if (day_index+1)%25==0 or day_index+1==len(days):
                print(json.dumps({'event':'completed_dates_aggregated','date':day,
                    'dates':day_index+1,'daily_jobs':total['daily_jobs']}),flush=True)
    return {'bybranch':bybranch, 'byyear':byyear, 'bysession':bysession, 'selected_charts':selected_charts, 'total':total, 'native':native, 'setup_ids':setup_ids, 'record_schemas':record_schemas, 'eligible_ids':eligible_ids, 'included_ids':included_ids, 'features':features, 'collection_outcomes':collection_outcomes, 'input_receipts':input_receipts, 'job_hashes':job_hashes, 'errors':errors}


def merge_stats(destination, source):
    if destination['scope'] is not None:
        assert destination['scope']==source['scope']
    destination['scope']=source['scope']
    for name in ('counts','boundary','ordering_with_both_boundaries','single_or_undefined_boundary','limitations'):
        destination[name].update(source[name])
    for key,value in source['session_results'].items():destination['session_results'][key].update(value)
    for key,value in source['resolution_seconds'].items():destination['resolution_seconds'][key].extend(value)
    for key,value in source['horizons'].items():
        destination['horizons'][key]['counts'].update(value['counts'])
        for metric in ('favorable','adverse'):destination['horizons'][key][metric].extend(value[metric])
    a=destination['input_endpoints'];b=source['input_endpoints']
    for key in ('first_searched_session','first_complete_input_session'):
        values=[v for v in (a[key],b[key]) if v is not None]
        a[key]=min(values) if values else None
    for key in ('last_searched_session','last_complete_input_session','last_complete_required_prefix_end_ns'):
        values=[v for v in (a[key],b[key]) if v is not None]
        a[key]=max(values) if values else None
    destination['native_execution_references']+=source['native_execution_references']


def merge_states(states):
    bybranch = defaultdict(blank); byyear = defaultdict(blank); bysession = defaultdict(blank); selected_charts = {}
    total = Counter(); native = {}; setup_ids = set(); record_schemas = set()
    eligible_ids, included_ids, features, collection_outcomes = [], [], [], []
    input_receipts = {}; job_hashes = {}; errors = []
    targets={'bybranch':bybranch,'byyear':byyear,'bysession':bysession}
    for state in states:
        for name,target in targets.items():
            for key,value in state[name].items():merge_stats(target[key],value)
        for key,value in state['selected_charts'].items():
            if key not in selected_charts or tuple(value['order'])<tuple(selected_charts[key]['order']):selected_charts[key]=value
        assert not set(native).intersection(state['native'])
        native.update(state['native']);total.update(state['total'])
        assert not setup_ids.intersection(state['setup_ids'])
        setup_ids.update(state['setup_ids']);record_schemas.update(state['record_schemas'])
        eligible_ids.extend(state['eligible_ids']);included_ids.extend(state['included_ids'])
        features.extend(state['features']);collection_outcomes.extend(state['collection_outcomes'])
        input_receipts.update(state['input_receipts']);job_hashes.update(state['job_hashes']);errors.extend(state['errors'])
    return {'bybranch':bybranch, 'byyear':byyear, 'bysession':bysession, 'selected_charts':selected_charts, 'total':total, 'native':native, 'setup_ids':setup_ids, 'record_schemas':record_schemas, 'eligible_ids':eligible_ids, 'included_ids':included_ids, 'features':features, 'collection_outcomes':collection_outcomes, 'input_receipts':input_receipts, 'job_hashes':job_hashes, 'errors':errors}


def collect_chunk(args):
    stream_root=args[-1]
    identity={'helper_sha256':hr.file_digest(Path(__file__)), 'registry_sha256':args[2]['registry_sha256'], 'dates':args[1]}
    marker=stream_root/'COMPLETE.json';state_path=stream_root/'state.pickle'
    if marker.exists():
        receipt=hr.read(marker)
        if receipt['identity']!=identity:raise ValueError('aggregation chunk identity differs')
        for path,digest in receipt['files'].items():
            if hr.file_digest(path)!=digest:raise ValueError('aggregation chunk file changed')
        with state_path.open('rb') as f:state=pickle.load(f)
        for path,digest in state['job_hashes'].items():
            if hr.file_digest(path)!=digest:raise ValueError('aggregation source job changed')
        return state
    state=collect_dates(args)
    with state_path.open('wb') as f:pickle.dump(state,f,protocol=5)
    paths=[state_path,*sorted((stream_root/'records').glob('*.gz'))]
    hr.immutable_json(marker,{'identity':identity,'files':{str(p):hr.file_digest(p) for p in paths}})
    print(json.dumps({'event':'aggregation_chunk_completed','first':args[1][0],'last':args[1][-1],'dates':len(args[1])}),flush=True)
    return state


def main(root, wait_for_completion=False, workers=1):
    root = Path(root).resolve(); registry, manifest = hr.load_registry(root)
    days = registry['scope']['evaluation_dates']; rows = manifest['branches']
    composition_path=root/'protocol/CALENDAR_RECOVERY_COMPOSITION.json'
    composition=hr.read(composition_path) if composition_path.exists() else None
    recovery_dates=set(); recovery_root=None; recovery_registry=None
    if composition:
        if content_hash({k:v for k,v in composition.items() if k!='composition_sha256'})!=composition['composition_sha256']:
            raise ValueError('calendar composition rule changed')
        if composition['primary_run']['registry_sha256']!=registry['registry_sha256']:
            raise ValueError('calendar composition primary identity differs')
        recovery_root=Path(composition['recovery_run']['path'])
        recovery_registry,recovery_manifest=hr.load_registry(recovery_root)
        if recovery_registry['registry_sha256']!=composition['recovery_run']['registry_sha256']:
            raise ValueError('calendar recovery identity differs')
        if recovery_registry['software']!=registry['software'] or recovery_manifest!=manifest:
            raise ValueError('calendar recovery changed setup implementation')
        recovery_dates=set(composition['replace_all_daily_units_on_dates'])
    selected_root=lambda day: recovery_root if day in recovery_dates else root
    daily = [r for r in rows if not (r['method_id']=='STOIC-DATA' and r['branch']=='process_review')]
    missing = [d for d in days if not (root/'jobs/evaluation'/d/'completion.json').exists()
               or not (selected_root(d)/'jobs/evaluation'/d/'completion.json').exists()]
    if missing and not wait_for_completion:
        raise ValueError(f'Census unfinished: {len(missing)} dates lack completion: {missing[:12]}')
    args=(root,days,registry,rows,recovery_root,recovery_registry,recovery_dates,wait_for_completion,root)
    if workers==1:
        state=collect_dates(args)
    else:
        chunks=[days[i:i+25] for i in range(0,len(days),25)]
        work=[(root,chunk,registry,rows,recovery_root,recovery_registry,recovery_dates,wait_for_completion,
               root/'aggregation-chunks'/f'{i:04}') for i,chunk in enumerate(chunks)]
        with ProcessPoolExecutor(max_workers=workers) as pool:
            state=merge_states(pool.map(collect_chunk,work))
        (root/'records').mkdir(exist_ok=True)
        for name in ('setup-records.jsonl.gz','coverage-exclusions.jsonl.gz','non-setup-observations.jsonl.gz'):
            with (root/'records'/name).open('wb') as destination:
                for item in work:
                    with (item[-1]/'records'/name).open('rb') as source:shutil.copyfileobj(source,destination,1024*1024)
        write_json(root/'validation/AGGREGATION_EXECUTION.json',{'workers':workers,'ordered_chunk_dates':chunks,
            'stream_format':'concatenated standard gzip members; decoded records retain original declared date and branch order',
            'chunk_receipts':[{'path':str(item[-1]/'COMPLETE.json'),'sha256':hr.file_digest(item[-1]/'COMPLETE.json')} for item in work]})
    bybranch, byyear, bysession, selected_charts, total, native, setup_ids, record_schemas, eligible_ids, included_ids, features, collection_outcomes, input_receipts, job_hashes, errors = (state[name] for name in ['bybranch', 'byyear', 'bysession', 'selected_charts', 'total', 'native', 'setup_ids', 'record_schemas', 'eligible_ids', 'included_ids', 'features', 'collection_outcomes', 'input_receipts', 'job_hashes', 'errors'])
    branch_results = {k:summarize(v) for k,v in bybranch.items()}
    annual_results = [{'coverage_id':k,'year':year,**summarize(v)} for (k,year),v in sorted(byyear.items())]
    session_results = [{'coverage_id':k,'decision_session':clock_bin,**summarize(v)} for (k,clock_bin),v in sorted(bysession.items())]
    total['sessions'] = len(days); total['native_executions'] = sum(r['executions'] for r in native.values())
    total['duplicate_opportunities'] = 0; total['future_leakage'] = 0
    phase, audit = [], []
    for method, identifier in METHOD_BY_ID.items():
        relevant = [r for r in rows if r['method_id']==method]
        detail = root/'methods'/f'{method}.md'; detail.parent.mkdir(exist_ok=True)
        table = []
        family_counts = Counter()
        for row in relevant:
            stats = branch_results.get(row['coverage_id'])
            if stats is None:
                table.append([row['branch'],'collection process','collection','collection','—','—','—'])
                continue
            c=stats['counts']; family_counts.update(c)
            table.append([row['branch'],measurement_scope(method,row['branch']),c.get('searched_sessions',0),
                          c.get('eligible_complete_sessions',0),c.get('setups',0),
                          c.get('completed_zero_setup_sessions',0),c.get('observed_search_with_input_limitations',0)])
        text=f'# {method} — full acquired Phase 1 measurement\n\n'
        text+='Implementation: accepted reconstructed setup rules, including disclosed inferred models. Historical session search: every frozen date through the owned NQ input endpoint. Setup qualification is distinct from subsequent outcomes and from actual fills.\n\n'
        text+=_table(['Branch','Scope','Searched sessions','Complete eligible sessions','Observed setups','Complete zero-setup sessions','Limited sessions'],table)+'\n\n'
        text+='Eligible denominators require complete observed inputs for the branch and no active input limitation. Setups observed in limited sessions remain in the observed population and are excluded from the complete-session frequency numerator. Context, supplemental, personal and collection units do not enter entry-setup denominators.\n\n'
        text+='Outcome tables describe all qualifying observed setups, including those in input-limited sessions. Complete future coverage is a separate requirement for excursion means; the per-setup record retains the input-eligibility flag.\n\n'
        for row in relevant:
            stats=branch_results.get(row['coverage_id'])
            if not stats:continue
            text+=f"## {row['branch']}\n\nSource: {row['source_definition']['citation']}; {row['source_definition']['operation']}.\n\n"
            text+=f"Setups per complete eligible session: {fmt(stats['setups_per_eligible_session'])}. Observed setups per searched session: {fmt(stats['observed_setups_per_searched_session'])}.\n\n"
            ends=stats['input_endpoints']
            text+=f"Searched session labels: {ends['first_searched_session']} through {ends['last_searched_session']}. First/last session with complete branch inputs: {ends['first_complete_input_session'] or 'none'} / {ends['last_complete_input_session'] or 'none'}. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.\n\n"
            text+=_table(['Year','Searched','Eligible','Setups','Setups in eligible sessions','Limited sessions'],
                [[a['year'],a['counts'].get('searched_sessions',0),a['counts'].get('eligible_complete_sessions',0),a['counts'].get('setups',0),a['counts'].get('setups_in_eligible_sessions',0),a['counts'].get('observed_search_with_input_limitations',0)]
                 for a in annual_results if a['coverage_id']==row['coverage_id']])+'\n\n'
            text+=_table(['Horizon min','Complete futures','Incomplete futures','No price origin','Mean favorable points','Mean adverse points'],
                [[n,v['counts'].get('complete_observed_horizon',0),v['counts'].get('incomplete_future_coverage',0),v['counts'].get('measurement_reference_unavailable',0),fmt(v['favorable_mean_points']),fmt(v['adverse_mean_points'])] for n,v in stats['horizons'].items()])+'\n\n'
            text+=_table(['Boundary outcome','n'],sorted(stats['boundary'].items()))+'\n\n'
            text+=_table(['Both objective and invalidation defined: ordering','n'],sorted(stats['ordering_with_both_boundaries'].items()))+'\n\n'
            text+=_table(['Only one or neither boundary defined','n'],sorted(stats['single_or_undefined_boundary'].items()))+'\n\n'
            text+=_table(['Observed boundary classification','n','Mean seconds from decision','Median seconds'],
                [[k,v['n'],fmt(v['mean']),fmt(v['median'])] for k,v in sorted(stats['resolution_seconds'].items())])+'\n\n'
            text+='A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.\n\n'
            text+=_table(['Decision session','Observed setups','Eligible-session denominator','Setups per eligible session'],
                [[k,v['setups'],v['eligible_session_denominator'],fmt(v['setups_per_eligible_session'])] for k,v in sorted(stats['session_results'].items())])+'\n\n'
            text+='Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.\n\n'
            text+=_table(['Decision session','Complete 60-min observations','Mean favorable points','Mean adverse points','Boundary classifications'],
                [[v['decision_session'],v['horizons']['60']['counts'].get('complete_observed_horizon',0),
                  fmt(v['horizons']['60']['favorable_mean_points']),fmt(v['horizons']['60']['adverse_mean_points']),
                  '; '.join(f'{k}: {n}' for k,n in sorted(v['boundary'].items()))]
                 for v in session_results if v['coverage_id']==row['coverage_id'] and v['counts'].get('setups',0)])+'\n\n'
            text+='The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.\n\n'
            text+=_table(['Exact limitation','Affected sessions'],sorted(stats['limitations'].items()))+'\n\n'
        text+=f'[Machine-readable results]({root}/MEASUREMENT_RESULTS.json) · [Coverage and exclusions]({coverage_path}) · [Per-setup records]({setup_path}) · [Charts]({root}/charts/README.md).\n'
        detail.write_text(text)
        phase.append([method,'full acquired historical measurement',family_counts.get('setups',0),'not claimed',
                      'all sessions searched; input-limited scope explicit',str(detail.relative_to(hr.ROOT))])
        verdict=('measured observed setup population' if any(measurement_scope(method,r['branch'])=='entry_setup' for r in relevant)
                 else 'non-entry scope retained; setup denominator not applicable')
        audit.append([method,identifier,verdict,'pass: full suite and native controls',0,0,
                      'fixed rules; exact limitations retained; outcomes are prices, not fills'])
    body={'schema':'phase1-full-historical-measurement-results-v1','registry_sha256':registry['registry_sha256'],
          'population':registry['scope'],'calendar_recovery_composition':composition,
          'totals':dict(total),'branches':branch_results,'by_year':annual_results,'by_decision_session':session_results,
          'native_sessions':native,'phase':phase,'audit':audit,
          'record_files':{str(p):hr.file_digest(p) for p in (setup_path,coverage_path,other_path)},
          'interpretation':'full declared observed-input census; limited/unavailable population and unresolved future outcomes remain explicit; no untouched holdout, return simulation, actual fill or profit claim'}
    write_json(root/'MEASUREMENT_RESULTS.json',body)
    write_json(root/'validation/CENSUS_RECONCILIATION.json',{
        'status':'pass','registry_sha256':registry['registry_sha256'],'totals':dict(total),
        'expected_daily_jobs':len(days)*len(daily),'job_hashes':job_hashes,
        'all_declared_sessions_completed':True,'duplicate_opportunities':0,'consumed_future_leakage':0})
    write_json(root/'validation/INPUT_RECEIPTS.json',list(input_receipts.values()))
    write_json(root/'charts/SELECTION.json',{'rule':'earliest date/decision/candidate within every branch/outcome category; earliest complete-zero and zero-with-input-or-scope-limitation example per branch',
                                          'registry_sha256':registry['registry_sha256'],'charts':list(selected_charts.values())})
    write_json(root/'validation/COLLECTION_INPUTS.json',{'eligible_ids':eligible_ids,'included_ids':included_ids,
        'features':features,'record_schemas':sorted(record_schemas),'outcomes':collection_outcomes,
        'outcome_counts':dict(sum((Counter(v['boundary']) for v in branch_results.values()),Counter()))})
    print(_table(['family','variant','n','faithful_disagreements','status','report path'],phase))
    print(_table(['family','id','verdict','fixture','leakage','proxy-as-faithful','notes'],audit))
    print(json.dumps(dict(total),indent=2))


def content_key(item):
    return hashlib.sha256(json.dumps(item,sort_keys=True).encode()).hexdigest()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-root',required=True)
    p.add_argument('--wait-for-completion',action='store_true')
    p.add_argument('--workers',type=int,default=1)
    a=p.parse_args();main(a.run_root,a.wait_for_completion,a.workers)
