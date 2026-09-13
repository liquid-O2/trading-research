"""Versioned empirical method replay using the existing discovery/evaluator.

Run roots are mandatory at the public boundary. A changed implementation,
test, definition, policy or input cannot reuse an accepted checkpoint.
"""
from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import date,datetime,timedelta,timezone
from dataclasses import asdict,is_dataclass
import gzip
import sys
from importlib.metadata import version,PackageNotFoundError
import json
from pathlib import Path
import time

from .branch_coverage import build_manifest, validate_manifest, ASSUMPTIONS, ROOT
from .catalog import METHOD_BY_ID
from .discovery import run_historical
from .empirical_protocol import content_hash
from .historical_features import HistoricalFeatures
from .historical_outcomes import observe_outcome
from .native_discovery import scan_branch
from .native_resolution import file_digest as _full_file_digest, NativeEvidenceError
from .protocol import jsonable

VERSION='2.0.0'
BASE=ROOT/'implementation/reports/phase1-live/implementation-v2'
OLD=ROOT/'implementation/reports/phase1-live/empirical'


_VERIFIED_DIGESTS = {}


def file_digest(path):
    """Full SHA-256, caching only stable large files in this invocation.

    Size, inode, device, mtime and ctime are rechecked at every use. A same-size
    replacement or backdated mtime invalidates a stable-file digest. Small
    or recent files are always rehashed to avoid timestamp-resolution races.
    """
    path=Path(path).resolve()
    def signature():
        st=path.stat()
        return st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns
    before=signature();key=str(path),before
    # Small files and recently changed files must be rehashed even when
    # filesystem timestamp resolution makes two writes share a signature.
    cacheable=before[2]>1_048_576 and before[-1]<time.time_ns()-5_000_000_000
    if not cacheable or key not in _VERIFIED_DIGESTS:
        digest=_full_file_digest(path)
        if signature()!=before:raise NativeEvidenceError('file changed while hashing: '+str(path))
        _VERIFIED_DIGESTS[key]=digest
    return _VERIFIED_DIGESTS[key]


def read(path):return json.loads(Path(path).read_text())


def serializable(value):
    if is_dataclass(value):return serializable(asdict(value))
    if isinstance(value,(date,datetime)):return value.isoformat()
    if isinstance(value,Path):return str(value)
    if isinstance(value,dict):return {k:serializable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serializable(v) for v in value]
    return jsonable(value)


def immutable_json(path, document):
    path=Path(path);payload=json.dumps(serializable(document),sort_keys=True,indent=2,allow_nan=False)+'\n'
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_text()!=payload:raise NativeEvidenceError('immutable artifact differs: '+str(path))
    else:
        with path.open('x') as stream:stream.write(payload)
    return path


def tree_identity(directory, suffixes=('.py','.json')):
    directory=Path(directory)
    return {p.relative_to(ROOT).as_posix():file_digest(p) for p in sorted(directory.rglob('*'))
        if p.is_file() and p.suffix in suffixes and '__pycache__' not in p.parts}


def software_identity():
    files={**tree_identity(ROOT/'implementation/src/trading_research/research/method_pack'),
        **tree_identity(ROOT/'implementation/src/trading_research/research/phase1_live'),
        **tree_identity(ROOT/'implementation/tests'),**tree_identity(ROOT/'implementation/tools')}
    runtime={'python':sys.version.split()[0]}
    for package in ('numpy','pyarrow','pytest','pypdf','matplotlib'):
        try:runtime[package]=version(package)
        except PackageNotFoundError:runtime[package]=None
    return {'sha256':content_hash({'files':files,'runtime':runtime}),'files':files,'runtime':runtime}


def selected_root(path):
    path=Path(path).resolve()
    if path==OLD or path.is_relative_to(OLD):
        raise NativeEvidenceError('v2 replay may not write the historical empirical run')
    return path


def freeze(run_root, *, scope_path=BASE/'SCOPE_POLICY.json', policy_path=BASE/'RESEARCH_POLICY.json', records_path=None, strategy=False):
    root=selected_root(run_root)
    scope=read(scope_path);policy=read(policy_path)
    if jsonable(ASSUMPTIONS)!=policy['assumptions']:
        raise NativeEvidenceError('implementation assumptions differ from the pre-outcome research policy')
    manifest=build_manifest();software=software_identity()
    records=None if records_path is None else {'path':str(Path(records_path).resolve()),'sha256':file_digest(Path(records_path))}
    body={'schema':'phase1-native-replay-registry-v2','registry_version':VERSION,'run_version':VERSION,
        'scope':scope,'scope_path':str(Path(scope_path).resolve()),'scope_sha256':file_digest(Path(scope_path)),
        'research_policy_path':str(Path(policy_path).resolve()),'research_policy_sha256':file_digest(Path(policy_path)),
        'research_frozen_at':datetime.now(timezone.utc).isoformat() if strategy else policy['frozen_at'],'coverage_sha256':manifest['manifest_sha256'],
        'native_integration':{'path':str(BASE/'NATIVE_INTEGRATION.json'),'sha256':file_digest(BASE/'NATIVE_INTEGRATION.json')},
        'strategy_reconstruction':strategy,'strategy_policy':__import__(__package__+'.strategy_policy',fromlist=['POLICY']).POLICY if strategy else None,
        'software':software,'records':records,'clock_contract':'event-time-observed-v2.0.0',
        'prior_registry':'v1.0.0','prior_run':'v1.0.2',
        'prior_manifest_sha256':'d80935d548abe3cafcd695ec842dc69b1d3391646c2da8fe0db9e935a6c37247',
        'evaluation_exposure':{'outcome_blind':False,'purpose':'engineering verification and descriptive research',
            'initial_policy_exposure':policy['exposure'],
            'development_artifacts':{str(p):file_digest(p) for folder in (BASE/'development',root.parent/'development') for p in sorted(folder.rglob('*.json'))},
            'earlier_attempts':{str(p.parent.parent):{'registry_sha256':read(p)['registry_sha256'],
                'job_files':{str(j.relative_to(p.parent.parent)):file_digest(j) for j in sorted((p.parent.parent/'jobs').rglob('*.json.gz'))}}
                for p in sorted(set(BASE.glob('run-*/registry/registry.json')) | set(root.parent.glob('run-*/registry/registry.json'))) if p.parent.parent!=root},
            'policy_changes_after_outcomes':bool(strategy),'implementation_fixes_after_development':True}}
    body['registry_sha256']=content_hash(body)
    immutable_json(root/'registry/coverage.json',manifest)
    immutable_json(root/'registry/registry.json',body)
    return body


def load_registry(run_root, *, check_software=True):
    root=selected_root(run_root);registry=read(root/'registry/registry.json')
    if content_hash({k:v for k,v in registry.items() if k!='registry_sha256'})!=registry['registry_sha256']:
        raise NativeEvidenceError('selected registry mutated')
    manifest=validate_manifest(read(root/'registry/coverage.json'))
    if manifest['manifest_sha256']!=registry['coverage_sha256']:raise NativeEvidenceError('selected coverage differs')
    for key in ('scope','research_policy'):
        if file_digest(Path(registry[key+'_path']))!=registry[key+'_sha256']:
            raise NativeEvidenceError('frozen '+key+' changed')
    if check_software and software_identity()!=registry['software']:
        raise NativeEvidenceError('code/test identity changed; freeze a new run root')
    admission=registry['native_integration']
    if file_digest(Path(admission['path']))!=admission['sha256']:
        raise NativeEvidenceError('frozen native integration receipt changed')
    if registry['records'] and file_digest(Path(registry['records']['path']))!=registry['records']['sha256']:
        raise NativeEvidenceError('supplied record population changed')
    return registry,manifest


def _records(registry):
    records={} if registry['records'] is None else read(registry['records']['path'])
    return dict(records,registry_sha256=registry['registry_sha256'],strategy_reconstruction=registry.get('strategy_reconstruction',False))


def _job_path(root,cohort,day,coverage_id):
    return root/'jobs'/cohort/day/(coverage_id.replace(':','--')+'.json.gz')


def write_job(path, document):
    data=gzip.compress(json.dumps(serializable(document),sort_keys=True,separators=(',',':'),allow_nan=False).encode(),mtime=0)
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=data:raise NativeEvidenceError('completed job differs; never overwrite')
    else:
        with path.open('xb') as stream:stream.write(data)
    return {'path':str(path),'sha256':file_digest(path)}


def read_job(path):return json.loads(gzip.decompress(Path(path).read_bytes()))


def verify_input_receipts(receipts):
    for receipt in receipts:
        if 'cache_identity' in receipt:
            if file_digest(Path(receipt['path']))!=receipt['artifact_sha256']:
                raise NativeEvidenceError('checkpoint event artifact changed')
            for source in receipt['cache_identity']['sources']:
                if file_digest(ROOT/'data'/source['path'])!=source['sha256']:
                    raise NativeEvidenceError('checkpoint native source changed')
        elif receipt.get('path') and receipt.get('sha256'):
            if file_digest(Path(receipt['path']))!=receipt['sha256']:
                raise NativeEvidenceError('checkpoint external/derived input changed')


def verify_job(document, registry, row, market=None):
    if document['registry_sha256']!=registry['registry_sha256']:
        raise NativeEvidenceError('checkpoint belongs to another registry')
    if document['coverage_id']!=row['coverage_id'] or document['scanner']!=row['scanner']:
        raise NativeEvidenceError('checkpoint branch/scanner identity differs')
    if market and document['input_sha256']!=market.window.document['input_sha256']:
        raise NativeEvidenceError('checkpoint current native membership differs')
    if any(document[k]!=row[k] for k in ('method_id','branch','extra_unit')):
        raise NativeEvidenceError('checkpoint method/branch/unit identity differs')
    if document['software_sha256']!=registry['software']['sha256']:
        raise NativeEvidenceError('checkpoint software identity differs')
    verify_input_receipts(document['input_receipts'])
    for item in document.get('domain_observations',{}).values():
        if file_digest(Path(item['path']))!=item['sha256']:
            raise NativeEvidenceError('checkpoint domain derivation changed')
    episodes=document['episodes']
    counts={v:sum(e['research_verdict']==v for e in episodes) for v in ('pass','fail','unknown')}
    if any(document[k]!=v for k,v in {'p':counts['pass'],'f':counts['fail'],'u':counts['unknown'],
            'n':counts['pass']+counts['fail'],'N_observed':len(episodes)}.items()):
        raise NativeEvidenceError('checkpoint denominator does not reconcile')
    for e in episodes:
        if e['method']!=row['method_id'] or e['branch']!=row['branch']:
            raise NativeEvidenceError('episode belongs to a different selected branch')
        if not row['extra_unit'] and 'branch' in e['values'] and e['values']['branch']!=row['branch']:
            raise NativeEvidenceError('predicate operands belong to a different selected branch')
        if e['faithful_eligible'] or e['actual_trade']:raise NativeEvidenceError('research episode promoted to faithful/trade')
        if any(d.get('known_at') is not None and d['known_at']>e['decision_at'] for d in e['operand_derivations'].values()):
            raise NativeEvidenceError('checkpoint has future input')
    return document


def domain_receipts(root,market):
    if not hasattr(market,'_published_domain_receipts'):market._published_domain_receipts={}
    records=market._published_domain_receipts
    for key,record in market.domain_observations.items():
        if key not in records:
            receipt=write_job(root/'domain'/(key+'.json.gz'),record)
            records[key]={**receipt,'recipe_id':record['recipe_id'],'result':record['result']}
        elif file_digest(Path(records[key]['path']))!=records[key]['sha256']:
            raise NativeEvidenceError('published domain observation changed')
    return records.copy()


def date_job(run_root,cohort,day, *, data_root='/workspace/data'):
    root=selected_root(run_root);registry,manifest=load_registry(root)
    market=HistoricalFeatures(day,data_root=data_root,records=_records(registry))
    for record in market.supplied('object_observation',market.end):
        if record['recipe_id'] not in {r['object_id'] for r in manifest['objects']}:
            raise NativeEvidenceError('object observation is outside the selected manifest')
        market.domain(record['recipe_id'],record['inputs'])
        market.input_receipts.append({'path':record['evidence_path'],'sha256':record['evidence_sha256']})
    jobs=[]
    for row in manifest['branches']:
        if row['method_id']=='STOIC-DATA':continue  # one actual collection review after market jobs
        path=_job_path(root,cohort,day,row['coverage_id'])
        if path.exists():
            document=verify_job(read_job(path),registry,row,market)
        else:
            t=time.monotonic()
            document=run_historical(row['method_id'],market=market,manifest=manifest,coverage_id=row['coverage_id'])[0]
            document['outcomes']=[observe_outcome(market,e) for e in document['episodes']]
            document.update(registry_sha256=registry['registry_sha256'],software_sha256=registry['software']['sha256'],
                cohort=cohort,input_receipts=market.input_receipts.copy(),
                domain_observations=domain_receipts(root,market),job_state='completed',
                native_executions=market.window.document['row_count'])
            write_job(path,document)
            print(json.dumps({'date':day,'cohort':cohort,'branch':row['coverage_id'],
                'n':document['n'],'p':document['p'],'f':document['f'],'u':document['u'],
                'elapsed_s':round(time.monotonic()-t,3)}),flush=True)
        jobs.append({'coverage_id':row['coverage_id'],'path':str(path),'sha256':file_digest(path)})
    result={'schema':'phase1-date-completion-v2','registry_sha256':registry['registry_sha256'],
        'date':day,'cohort':cohort,'jobs':jobs,'input_receipts':market.input_receipts}
    # Membership is stable even if a resumed process did not rebuild memoized
    # ancestors. The branch receipts are the actual complete dependencies.
    result['input_receipts']=list({content_hash(r):r for j in jobs for r in read_job(j['path'])['input_receipts']}.values())
    immutable_json(root/'jobs'/cohort/day/'completion.json',result)
    return {'date':day,'branches':len(jobs),'executions':market.window.document['row_count']}


def _collection_review(root,cohort,days,registry,manifest,started):
    members=[];documents=[]
    for day in days:
        completion=read(root/'jobs'/cohort/day/'completion.json')
        for j in completion['jobs']:
            if file_digest(Path(j['path']))!=j['sha256']:raise NativeEvidenceError('collection job changed')
            members.append(j);documents.append(read_job(j['path']))
    episodes=[e for d in documents for e in d['episodes']]
    outcomes=[e for d in documents for e in d['outcomes']]
    completed=time.time_ns()
    # The published process is audited against this actual collection. Its
    # start is collection time, never a fabricated freeze before market 2020.
    inclusion=content_hash({'days':days,'branches':[r['coverage_id'] for r in manifest['branches'] if r['method_id']!='STOIC-DATA']})
    ids=[d['cohort']+':'+d['session_date']+':'+d['coverage_id'] for d in documents]
    expected=[cohort+':'+day+':'+r['coverage_id'] for day in days for r in manifest['branches'] if r['method_id']!='STOIC-DATA']
    record={'id':'collection:'+cohort+':'+registry['registry_sha256'],'spec_sha256':registry['registry_sha256'],
        'spec_frozen_at':int(datetime.fromisoformat(registry['research_frozen_at']).timestamp()*1_000_000_000),
        'collection_started_at':started,'collection_completed_at':completed,'eligible_ids':expected,'included_ids':ids,
        'inclusion_sha256':inclusion,'frozen_inclusion_sha256':inclusion,
        'features':[{'candidate_id':e['candidate_id'],'known_at':d['known_at'],'decision_at':e['decision_at']}
            for e in episodes for d in e['operand_derivations'].values() if d.get('known_at') is not None],
        'outcomes':[{'candidate_id':e['candidate_id'],'result':e['result']} for e in outcomes],
        'record_schemas':sorted({e['schema'] for e in episodes}),
        'feature_fields':['predecision_values','operand_derivations'],
        'outcome_fields':['postsequence_result'],
        'comparison_counts':{key:sum(o['result']==key for o in outcomes) for key in sorted({o['result'] for o in outcomes})},
        'revisions':[],'members':members}
    review_path=root/'jobs'/cohort/'process-review.json'
    if review_path.exists():record=read(review_path)
    else:immutable_json(review_path,record)
    for row in manifest['branches']:
        if row['method_id']!='STOIC-DATA':continue
        path=_job_path(root,cohort,'collection',row['coverage_id'])
        if path.exists():verify_job(read_job(path),registry,row);continue
        market=HistoricalFeatures(days[-1],records={**_records(registry),'process_review':[record]})
        result=scan_branch(market,row)
        result.update(registry_sha256=registry['registry_sha256'],software_sha256=registry['software']['sha256'],
            cohort=cohort,collection_dates=days,input_receipts=[*market.input_receipts,{'path':str(review_path),'sha256':file_digest(review_path)}],
            domain_observations=domain_receipts(root,market),job_state='completed',outcomes=[],
            native_executions=market.window.document['row_count'])
        write_job(path,result)


def run(run_root, *, cohort='evaluation',workers=1):
    root=selected_root(run_root);registry,manifest=load_registry(root)
    days=registry['scope'][cohort+'_dates']
    started_path=root/'jobs'/cohort/'started.json'
    if not started_path.exists():immutable_json(started_path,{'started_at':time.time_ns(),'days':days,'registry_sha256':registry['registry_sha256']})
    started=read(started_path)['started_at']
    if workers==1:
        result=[date_job(root,cohort,day) for day in days]
    else:
        result=[]
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures={pool.submit(date_job,root,cohort,day):day for day in days}
            for future in as_completed(futures):result.append(future.result())
    _collection_review(root,cohort,days,registry,manifest,started)
    return sorted(result,key=lambda r:r['date'])


def scope_for_range(start,end):
    start,end=date.fromisoformat(start),date.fromisoformat(end)
    if start<date(2020,1,1) or end<start or end>date(2026,9,3):
        raise ValueError('date range outside acquired 2020+ study bounds')
    return [str(start+timedelta(days=n)) for n in range((end-start).days+1)]


def main(args):
    if args.action=='freeze':
        scope_path=args.scope
        if args.date_from or args.date_to:
            if not (args.date_from and args.date_to):raise ValueError('both date bounds are required')
            scope=read(scope_path)
            scope.update(evaluation_dates=scope_for_range(args.date_from,args.date_to),
                sample_kind='Explicit inclusive calendar-date range; all dates and all branches retained',
                range_policy={'from':args.date_from,'through':args.date_to,'coverage_replacement':False})
            scope_path=immutable_json(selected_root(args.run_root)/'registry/range-scope.json',scope)
        out=freeze(args.run_root,scope_path=scope_path,records_path=args.records,strategy=args.strategy)
    elif args.action=='run':out=run(args.run_root,cohort=args.cohort,workers=args.workers)
    elif args.action in {'report','verify'}:
        from .historical_reporting import report,verify
        out=report(args.run_root) if args.action=='report' else verify(args.run_root)
    else:raise ValueError('unknown historical replay action')
    print(json.dumps(jsonable(out),sort_keys=True,indent=2))
    return 0
