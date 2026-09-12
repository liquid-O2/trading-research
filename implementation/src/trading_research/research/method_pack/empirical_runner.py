"""Frozen, bounded empirical jobs with atomic, hash-checked resume points."""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import date, datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from .empirical_protocol import content_hash, implementation_identity, population_summary, write_json
from .empirical_registry import load_registry, canonical_hash, validate_registry, validated_registry_batch
from .empirical_market import BarMarket, clock, previous_weekday
from .empirical_bar_engine import run_bar_rule
from .empirical_selectors import MINUTE, compact_bar

ROOT=Path('/workspace/implementation/reports/phase1-live/empirical')
COHORTS=('bar-monthly','tape-annual-trades')


def file_hash(path):
    h=sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()


def manifest_hash(doc):
    return content_hash({k:v for k,v in doc.items() if k!='manifest_sha256'})


def calibrate(root=ROOT,data_root='/workspace/data'):
    """Operational native pipeline check on an already excluded source date."""
    root=Path(root);registry=load_registry(root/'registry/CANDIDATE_REGISTRY.json')
    registry['freeze_status']='frozen';registry['registry_sha256']=canonical_hash(registry)
    partition={'partition_id':'calibration-NQ-2026-02-24','instrument_id':42002475,
               'session_date':'2026-02-24'}
    code_identity=implementation_identity()
    summaries=[];records=[]
    with validated_registry_batch(registry):
        market=BarMarket(partition,data_root)
        # The same already-excluded calibration date also exercises native
        # tape orchestration before the annual evaluation jobs reach it.
        trade_dataset='quantpad/cme__nq-continuous-futures__trades'
        identities=[]
        native_files=[(market.dataset_id,path) for path in market.resolver.identities]
        definition=market.window.instrument_definition
        native_files.append(('derived/continuous-futures__instrument-and-roll-maps',definition.source_file))
        native_files.append((trade_dataset,str(Path(data_root)/trade_dataset/'2026-02-23.parquet')))
        for dataset,path in native_files:
            relative=Path(path).resolve().relative_to(Path(data_root).resolve()).as_posix()
            identities.append({'dataset_id':dataset,'path':relative,'sha256':file_hash(path),'hash_basis':'full_file_sha256'})
        partition.update(input_identities=identities,dataset_windows={'trades':{'dataset_id':trade_dataset}})
        tape,profile=tape_context(market,partition,data_root)
        for rule in registry['rules']:
            if not rule['supported']:continue
            if rule['method_id']=='REFILL-STUDY':
                found=execute_m09(rule,market,registry,partition,tape,data_root);batch=found['records']
            else:
                found=run_bar_rule(rule,market,registry,tape=tape,prior_profile=profile)
                batch=execute_bar_records(rule,market,registry,found)
            records.extend(batch)
            summaries.append({'rule_id':rule['rule_id'],'population_holes':found['population_holes'],
                              'summary':population_summary(batch)})
        bars=[compact_bar(b) for b in market.bars(clock(market.day,'00:00'),market.end)]
    if implementation_identity()['sha256']!=code_identity['sha256']:
        raise ValueError('implementation changed during calibration; discard unpublished batch')
    if not records:raise ValueError('native calibration pipeline did not produce any auditable record')
    path=root/'artifacts/calibration-native-pipeline'/code_identity['sha256'][:16]/'records.json'
    digest=write_json(path,{'records':records,'bars':bars,'tape':tape,'prior_profile':profile})
    result={'schema':'phase1-empirical-calibration-pipeline-v1','historical_candidate':False,
            'evaluation_inclusion':False,'source_case':'GB-VWAP-2026-02-24 / JJ native control date',
            'source_agreement':'Not scored by this operational check; see calibration_matrix.json.',
            'implementation_sha256':code_identity['sha256'],'registry_sha256':registry['registry_sha256'],
            'partition':partition,'rules':summaries,'artifact_path':str(path),'artifact_sha256':digest}
    write_json(root/'calibration/NATIVE_PIPELINE.json',result)
    return {'calibration_only':True,'rules':len(summaries),'opportunities':len(records),'artifact_sha256':digest}


def freeze(root=ROOT):
    root=Path(root)
    if (root/'RUN_MANIFEST.json').exists():raise ValueError('run already frozen; do not overwrite evaluation identity')
    registry=load_registry(root/'registry/CANDIDATE_REGISTRY.json')
    from .empirical_coverage import assert_valid_frozen_split
    jobs=[];splits={}
    for cohort in COHORTS:
        path=root/'coverage'/cohort/'evaluation-split.json'
        split=json.loads(path.read_text())
        assert_valid_frozen_split(split, data_root=Path(split['data_root']))
        if split['lookback_calendar_days']<62:raise ValueError('full prior-month reference requires62daymanifest')
        rules=[r['rule_id'] for r in registry['rules'] if r['supported'] and
               ('native_executed_trades_with_aggressor' in r['required_data'])==(cohort=='tape-annual-trades')]
        splits[cohort]={'path':str(path),'sha256':file_hash(path),'manifest_sha256':split['manifest_sha256']}
        for partition in split['partitions']:
            jobs.append({'job_id':cohort+'--'+partition['partition_id'],'cohort':cohort,
                         'partition':partition,'rule_ids':rules})
    registry['freeze_status']='frozen';registry['registry_sha256']=canonical_hash(registry)
    validate_registry(registry)
    pilot=json.loads((root/'calibration/NATIVE_PIPELINE.json').read_text())
    if pilot['implementation_sha256']!=implementation_identity()['sha256'] or pilot['registry_sha256']!=registry['registry_sha256']:
        raise ValueError('rerun native calibration pipeline against current code and rules before freeze')
    if file_hash(pilot['artifact_path'])!=pilot['artifact_sha256']:
        raise ValueError('calibration pipeline artifact changed')
    write_json(root/'registry/CANDIDATE_REGISTRY.json',registry)
    doc={'schema':'phase1-empirical-run-v1','frozen_at_utc':datetime.now(timezone.utc).isoformat(),
         'registry_sha256':registry['registry_sha256'],'implementation':implementation_identity(),
         'calibration_sha256':file_hash(root/'calibration/calibration_matrix.json'),
         'native_pipeline_sha256':file_hash(root/'calibration/NATIVE_PIPELINE.json'),
         'splits':splits,'jobs':jobs,'outcome_blind':True,
         'interpretation':'Retrospective research freeze, not historical foreknowledge. No untouched claim.',
         'selection':'Coverage-only chronological monthly bar and annual standalone-trade samples; no outcome filtering.',
         'chart_selection':'First chronological record per rule/verdict, plus first record per observed year; deduplicate, cap80.',
         'populations':'Initial market opportunities; passing endpoints are nested comparison signals. Actual selections/attempts/orders/fills unavailable.'}
    doc['manifest_sha256']=manifest_hash(doc)
    write_json(root/'RUN_MANIFEST.json',doc)
    return {'jobs':len(jobs),'rule_jobs':sum(len(j['rule_ids']) for j in jobs),'manifest_sha256':doc['manifest_sha256']}


def revise_reporting_run(root=ROOT):
    """Record the reviewed reporting/orchestration v1.0.1 repair after exposure.

    Rules and selector functions remain unchanged. Every original input and
    job is retained and recomputed; old outputs stay in the revision archive.
    """
    root=Path(root);old=json.loads((root/'RUN_MANIFEST.json').read_text())
    if old['manifest_sha256']!=manifest_hash(old):raise ValueError('original run identity changed')
    if old.get('run_version') not in {None,'1.0.1'}:raise ValueError('recorded reporting repairs already applied')
    next_version='1.0.1' if old.get('run_version') is None else '1.0.2'
    archive=root/'revisions'/('run-v1' if old.get('run_version') is None else 'run-v1.0.1')
    saved=json.loads((archive/'RUN_MANIFEST.json').read_text())
    if saved!=old:raise ValueError('original freeze must be preserved before revision')
    if (root/'checkpoints').exists() and list((root/'checkpoints').glob('*.json')):
        raise ValueError('archive original checkpoints before recomputation')
    registry=load_registry(root/'registry/CANDIDATE_REGISTRY.json')
    if registry['registry_sha256']!=old['registry_sha256']:raise ValueError('reporting repair cannot alter rules')
    for split in old['splits'].values():
        if file_hash(split['path'])!=split['sha256']:raise ValueError('reporting repair cannot change cohort')
    current=implementation_identity();before=old['implementation']['files'];after=current['files']
    changed={path for path in before.keys()|after.keys() if before.get(path)!=after.get(path)}
    allowed={'implementation/src/trading_research/research/method_pack/'+name
             for name in ('empirical_reporting.py','empirical_runner.py')}
    tape_path='implementation/src/trading_research/research/method_pack/empirical_tape.py'
    if tape_path in changed:
        # Only the reviewed per-file metadata cache in the aggregation helper
        # may change; the M09 selector and stream normalization must be exact.
        import ast
        original=archive/'source/empirical_tape.py'
        if file_hash(original)!=before[tape_path]:raise ValueError('original tape implementation not preserved')
        def other_functions(path):
            tree=ast.parse(Path(path).read_text())
            tree.body=[node for node in tree.body if not isinstance(node,ast.FunctionDef) or node.name!='load_tape_session']
            return ast.dump(tree,include_attributes=False)
        if other_functions(original)!=other_functions(Path('/workspace')/tape_path):
            raise ValueError('revision changes a frozen tape selector or native stream')
        allowed.add(tape_path)
    if not changed or not changed<=allowed:raise ValueError('revision is not the reviewed reporting-only repair')
    pilot=json.loads((root/'calibration/NATIVE_PIPELINE.json').read_text())
    if pilot['implementation_sha256']!=current['sha256'] or pilot['registry_sha256']!=registry['registry_sha256']:
        raise ValueError('rerun native calibration against repaired implementation')
    if file_hash(pilot['artifact_path'])!=pilot['artifact_sha256']:raise ValueError('revised calibration artifact changed')
    exposure=json.loads((root/'EVALUATION_EXPOSURE.json').read_text())
    if not exposure['revisions'] or exposure['revisions'][-1]['previous_run_manifest_sha256']!=old['manifest_sha256']:
        raise ValueError('explicit exposure record is required')
    if exposure['revisions'][-1]['revision']!=next_version:raise ValueError('revision version lacks exact exposure record')
    new=dict(old,run_version=next_version,previous_run_manifest_sha256=old['manifest_sha256'],
             implementation=current,native_pipeline_sha256=file_hash(root/'calibration/NATIVE_PIPELINE.json'),
             frozen_at_utc=datetime.now(timezone.utc).isoformat(),outcome_blind=False,
             rule_and_split_freeze_unchanged=True,
             revision={'reason':exposure['revisions'][-1]['reason'],'changed_files':sorted(changed),
                       'source_rule_or_selector_changes':False,'rerun':'all original declared jobs',
                       'exposure_record_sha256':file_hash(root/'EVALUATION_EXPOSURE.json')})
    new['manifest_sha256']=manifest_hash(new)
    write_json(root/'RUN_MANIFEST.json',new)
    return {'run_version':next_version,'jobs':len(new['jobs']),'manifest_sha256':new['manifest_sha256'],'unchanged_registry_sha256':registry['registry_sha256']}


def validate_run(root=ROOT):
    root=Path(root);doc=json.loads((root/'RUN_MANIFEST.json').read_text())
    if doc['manifest_sha256']!=manifest_hash(doc):raise ValueError('run manifest mutated')
    registry=load_registry(root/'registry/CANDIDATE_REGISTRY.json')
    if registry['freeze_status']!='frozen' or registry['registry_sha256']!=doc['registry_sha256']:
        raise ValueError('registry differs from frozen run')
    if implementation_identity()['sha256']!=doc['implementation']['sha256']:
        raise ValueError('implementation differs from frozen run; record exposure revision before replay')
    if file_hash(root/'calibration/calibration_matrix.json')!=doc['calibration_sha256']:
        raise ValueError('calibration differs from freeze')
    if file_hash(root/'calibration/NATIVE_PIPELINE.json')!=doc['native_pipeline_sha256']:
        raise ValueError('native pipeline gate differs from freeze')
    if doc.get('revision') and file_hash(root/'EVALUATION_EXPOSURE.json')!=doc['revision']['exposure_record_sha256']:
        raise ValueError('recorded evaluation exposure changed after revision')
    if set(doc['splits'])!=set(COHORTS):raise ValueError('frozen cohort missing or added')
    expected_jobs=[]
    for cohort,split in doc['splits'].items():
        if file_hash(split['path'])!=split['sha256']:raise ValueError('coverage split differs from freeze')
        scope=json.loads(Path(split['path']).read_text())
        rule_ids=[r['rule_id'] for r in registry['rules'] if r['supported'] and
                  ('native_executed_trades_with_aggressor' in r['required_data'])==(cohort=='tape-annual-trades')]
        expected_jobs.extend({'job_id':cohort+'--'+p['partition_id'],'cohort':cohort,
                              'partition':p,'rule_ids':rule_ids} for p in scope['partitions'])
    if content_hash(expected_jobs)!=content_hash(doc['jobs']):raise ValueError('jobs do not equal frozen split membership')
    ids=[j['job_id'] for j in doc['jobs']]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate frozen jobs')
    return doc,registry


def verify_inputs(partition,data_root):
    signatures={}
    for identity in partition['input_identities']:
        path=(Path(data_root)/identity['path']).resolve()
        if not path.is_relative_to(Path(data_root).resolve()):raise ValueError('foreign input path')
        if file_hash(path)!=identity['sha256']:raise ValueError('input changed since coverage freeze: '+str(path))
        stat=path.stat();signatures[path]=(stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns)
    return signatures


def assert_inputs_unchanged(signatures):
    for path,old in signatures.items():
        stat=path.stat()
        if old!=(stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns):raise ValueError('input changed during bounded job')


def check_market_members(market,partition,data_root):
    frozen={str((Path(data_root)/i['path']).resolve()):i['sha256'] for i in partition['input_identities']}
    for path,(_,digest,_) in market.resolver.identities.items():
        if frozen.get(path)!=digest:raise ValueError('bar member outside frozen inputs')
    definition=market.window.instrument_definition
    if definition is not None and frozen.get(str(Path(definition.source_file).resolve()))!=definition.sha256:
        raise ValueError('native definition outside frozen inputs')


def endpoint_object(market,rule,opportunity,replay):
    """Recompute every bar endpoint through accepted O004, not just the kernel."""
    endpoint=replay.endpoint
    if endpoint is None or 'start' not in endpoint:return None
    start,end=endpoint['start'],endpoint['end']
    obj,result=market.object(rule['method_id'],rule['branch'],'O004',start,end,
        {'kind':'time','size_minutes':(end-start)//MINUTE},label='replay-endpoint')
    if result is None or result.coverage_ok is not True:raise ValueError('endpoint lacks native producer coverage')
    for key in ('O','H','L','C','V','known_at','instrument_id'):
        if str(result.value[key])!=str(endpoint[key]):raise ValueError('kernel endpoint differs from native producer: '+key)
    if result.known_at!=replay.completed_at:raise ValueError('native endpoint available after result')
    return obj


def execute_bar_records(rule,market,registry,found):
    records=[]
    for opportunity,replay in found['records']:
        assembled=market.source_assembly(rule,opportunity,registry)
        endpoint=endpoint_object(market,rule,opportunity,replay)
        replay=replace(replay,source_method_verdict=assembled.result['verdict'])
        records.append({'opportunity':opportunity.to_dict(),'replay':replay.to_dict(opportunity),
                        'source_assembly':{'manifest':assembled.manifest,'result':assembled.result},
                        'native_endpoint_object':endpoint})
    return records


def tape_context(market,partition,data_root):
    from .empirical_tape import load_tape_session
    from .native_resolution import NativeEvidenceError
    kwargs={'frozen_inputs':partition['input_identities'],'ohlcv_dataset':market.dataset_id,
            'value_area_fraction':'.70','value_area_tie_policy':'both','poc_tie_policy':'lowest'}
    dataset=partition['dataset_windows']['trades']['dataset_id']
    prior=previous_weekday(market.day)
    def load_window(day,kind):
        start,end=clock(day,'09:30'),clock(day,'16:00')
        try:
            return load_tape_session(data_root,dataset,start,end,market.instrument_id,
                profile_kind=kind,session_date=str(day),**kwargs)
        except NativeEvidenceError as exc:
            # Coverage-only selection admits partitions whose file metadata
            # intersects the combined prior/current window. One constituent
            # may have no tape at all; independent branches must still run.
            # Hash, ownership, schema and identity failures are never swallowed.
            if str(exc)!='no canonical native tape file overlaps requested interval':raise
            return {'schema':'phase1-empirical-empty-tape-window-v1','dataset_id':dataset,
                    'instrument_id':market.instrument_id,'formation_start':start,'formation_end':end,
                    'row_count':0,'profile':{},'minutes':[],'source_files':[],
                    'coverage':{'coverage_ok':None,'coverage_reason':'no_native_tape_window',
                                'reconciliation':[],'missing_intervals':[[start,end]]}}
    profile=load_window(prior,'prior_rth')
    tape=load_window(market.day,'developing_rth')
    return tape,profile


def execute_m09(rule,market,registry,partition,tape,data_root):
    from .empirical_tape import stream_native_trades,m09_research_comparison
    from .empirical_protocol import Opportunity,ReplayResult
    from .empirical_tape_binding import assemble_m09
    if tape['row_count']==0:
        return {'records':[],'population_holes':['no_native_tape_members_for_session'],
                'search_executed':True,'coverage_ok':None,'zones':[]}
    stream=stream_native_trades(data_root,partition['dataset_windows']['trades']['dataset_id'],
        clock(market.day,'09:30'),market.end,market.instrument_id,frozen_inputs=partition['input_identities'])
    definition=market.window.instrument_definition
    found=m09_research_comparison(stream,rule=rule,partition=market.partition,
        registry_sha256=registry['registry_sha256'],tick_size=definition.tick_size,
        coverage_ok=tape['coverage']['coverage_ok'],session_end=market.end)
    for record in found['records']:
        op=Opportunity(**record['opportunity']);replay=ReplayResult(**record['replay'])
        assembled=assemble_m09(rule,record['opportunity'],registry,market,tape)
        if assembled.result['faithful_eligible'] or assembled.result['detected_causal_violations']:
            raise ValueError('M09 source assembly crosses source boundary')
        record['replay']=replace(replay,source_method_verdict=assembled.result['verdict']).to_dict(op)
        record['source_assembly']={'manifest':assembled.manifest,'result':assembled.result}
        record['native_tape_evidence_sha256']=tape['evidence_sha256']
    found['population_holes']=[] if tape['coverage']['coverage_ok'] is True else ['native_tape_coverage_unverified']
    found['search_executed']=True
    return found


def run_job(job,manifest,registry,root=ROOT,data_root='/workspace/data'):
    root=Path(root);job_id=job['job_id'];checkpoint_path=root/'checkpoints'/f'{job_id}.json'
    if checkpoint_path.exists():
        previous=json.loads(checkpoint_path.read_text())
        if (previous.get('job_sha256')!=content_hash(job) or previous['job_id']!=job_id or
            previous['partition_id']!=job['partition']['partition_id'] or
            previous['session_date']!=job['partition']['date'] or
            str(previous['instrument_id'])!=str(job['partition']['instrument_id']) or
            previous['registry_sha256']!=registry['registry_sha256'] or
            previous['search_completed'] is not True or
            [r['rule_id'] for r in previous['rules']]!=job['rule_ids'] or
            previous['run_manifest_sha256']!=manifest['manifest_sha256'] or
            previous['implementation_sha256']!=manifest['implementation']['sha256'] or
            previous['artifact_sha256']!=file_hash(previous['artifact_path'])):
            raise ValueError('stale or damaged checkpoint; never silently skip')
        artifact=json.loads(Path(previous['artifact_path']).read_text())
        if artifact['job_id']!=job_id:raise ValueError('artifact belongs to another job')
        if content_hash(artifact['rules'])!=content_hash(previous['rules']):
            raise ValueError('checkpoint rule scope differs from hashed artifact')
        for summary in previous['rules']:
            rows=[r for r in artifact['records'] if r['opportunity']['rule_id']==summary['rule_id']]
            if content_hash(population_summary(rows))!=content_hash(summary['summary']):
                raise ValueError('checkpoint summary differs from actual records')
        return {'job_id':job_id,'resumed':True}
    partition=job['partition'];signatures=verify_inputs(partition,data_root)
    normalized=dict(partition,session_date=partition['date'],dataset_id=partition['dataset_windows']['ohlcv_1m']['dataset_id'])
    records=[];summaries=[];tape=profile=None;m09_diagnostics=None
    with validated_registry_batch(registry):
        market=BarMarket(normalized,data_root);check_market_members(market,partition,data_root)
        if job['cohort']=='tape-annual-trades':tape,profile=tape_context(market,partition,data_root)
        for rule_id in job['rule_ids']:
            rule=next(r for r in registry['rules'] if r['rule_id']==rule_id)
            if rule['method_id']=='REFILL-STUDY':
                found=execute_m09(rule,market,registry,partition,tape,data_root)
                batch=found['records'];m09_diagnostics={k:v for k,v in found.items() if k!='records'}
            else:
                found=run_bar_rule(rule,market,registry,tape=tape,prior_profile=profile)
                batch=execute_bar_records(rule,market,registry,found)
            holes=found['population_holes'];summary=population_summary(batch)
            summaries.append({'rule_id':rule_id,'method_id':rule['method_id'],'branch':rule['branch'],
                'observation_unit':rule['observation_unit'],'search_executed':True,
                'status':('completed_with_population_holes' if batch else 'missing_data') if holes else 'completed',
                'population_holes':holes,'summary':summary,'references':found.get('references',[])})
            records.extend(batch)
        # Export actual prefix-produced bars used in the deterministic charts.
        bars=[compact_bar(b) for b in market.bars(clock(market.day,'00:00'),market.end)]
        assert_inputs_unchanged(signatures)
    if implementation_identity()['sha256']!=manifest['implementation']['sha256']:
        raise ValueError('implementation changed during job; discard unpublished batch')
    if len({r['opportunity']['opportunity_id'] for r in records})!=len(records):raise ValueError('duplicate job opportunities')
    artifact=root/'artifacts'/manifest['manifest_sha256'][:16]/job_id/'records.json'
    digest=write_json(artifact,{'schema':'phase1-empirical-artifact-v1','job_id':job_id,
        'registry_sha256':registry['registry_sha256'],'implementation_sha256':manifest['implementation']['sha256'],
        'records':records,'rules':summaries,'bars':bars,'tape':tape,'prior_profile':profile,'m09_diagnostics':m09_diagnostics})
    checkpoint={'schema':'phase1-empirical-checkpoint-v1','job_id':job_id,'job_sha256':content_hash(job),'cohort':job['cohort'],
        'partition_id':partition['partition_id'],'session_date':partition['date'],'instrument_id':partition['instrument_id'],
        'registry_sha256':registry['registry_sha256'],'implementation_sha256':manifest['implementation']['sha256'],
        'run_manifest_sha256':manifest['manifest_sha256'],'search_completed':True,
        'artifact_path':str(artifact),'artifact_sha256':digest,'rules':summaries}
    write_json(checkpoint_path,checkpoint)
    return {'job_id':job_id,'resumed':False,'opportunities':len(records),'rules':len(summaries),
            'missing_rules':sum(bool(r['population_holes']) for r in summaries)}


_WORKER_CONTEXT=None


def _worker_init(root,data_root):
    global _WORKER_CONTEXT
    manifest,registry=validate_run(root)
    _WORKER_CONTEXT=(manifest,registry,root,data_root)


def _worker_job(job):
    manifest,registry,root,data_root=_WORKER_CONTEXT
    return run_job(job,manifest,registry,root,data_root)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['calibrate','freeze','revise-reporting','validate','run','report'])
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--data-root',default='/workspace/data')
    parser.add_argument('--cohort',choices=COHORTS)
    parser.add_argument('--job-id');parser.add_argument('--max-partitions',type=int)
    parser.add_argument('--workers',type=int,choices=range(1,5),default=1,
                        help='Independent bounded date processes; all frozen jobs still required.')
    args=parser.parse_args(argv)
    if args.stage=='calibrate':print(json.dumps(calibrate(args.root,args.data_root)));return
    if args.stage=='revise-reporting':print(json.dumps(revise_reporting_run(args.root)));return
    if args.stage=='freeze':print(json.dumps(freeze(args.root)));return
    if args.stage=='report':
        from .empirical_reporting import report
        doc=report(args.root)
        print(json.dumps({'status':doc['status'],'valid':doc['validation']['valid'],'scope':doc['scope']}))
        print('family | variant | n | faithful_disagreements | status | report path')
        for row in doc['family_reports']:
            print(f"{row['family']} | comparison counts; no pooled rate | {row['n']} | null | {row['status']} | {args.root/'RESULTS.md'}")
        print('family | id | verdict | fixture | leakage | proxy-as-faithful | notes')
        for row in doc['audit']:
            print(' | '.join(str(row.get(key)) for key in ('family','id','verdict','fixture','leakage','proxy_as_faithful','notes')))
        if not doc['validation']['valid']:raise ValueError('empirical report validation failed')
        return
    manifest,registry=validate_run(args.root)
    if args.stage=='validate':print(json.dumps({'valid':True,'jobs':len(manifest['jobs'])}));return
    jobs=[j for j in manifest['jobs'] if (args.cohort is None or j['cohort']==args.cohort) and
          (args.job_id is None or j['job_id']==args.job_id)]
    if args.job_id and not jobs:raise ValueError('job outside frozen manifest')
    if args.max_partitions is not None:jobs=jobs[:args.max_partitions]
    if args.workers==1:
        for job in jobs:print(json.dumps(run_job(job,manifest,registry,args.root,args.data_root)),flush=True)
    else:
        from concurrent.futures import ProcessPoolExecutor,as_completed
        import multiprocessing
        with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context('spawn'),
                initializer=_worker_init,initargs=(args.root,args.data_root)) as pool:
            futures=[pool.submit(_worker_job,job) for job in jobs]
            for future in as_completed(futures):print(json.dumps(future.result()),flush=True)


if __name__=='__main__':main()
