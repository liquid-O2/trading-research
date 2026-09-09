"""Register bounded admission and measurement of the acquired cross-market sources."""
from dataclasses import asdict
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'validation/CROSS_MARKET_ALIGNMENT_DESCRIPTIVE_V1.json'
RUNS=ROOT/'reports/cross-market-runs'
OPERATIONAL_LIMITS=ROOT/'validation/CROSS_MARKET_OPERATIONAL_LIMITS_V3.json'


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()


def checked(path, sha=None, maximum=16*1024**2):
    path=Path(path)
    if 'archive' in path.parts or not path.is_file() or path.stat().st_size>maximum:
        raise ValueError('bounded retained input required')
    raw=path.read_bytes()
    if sha and hashlib.sha256(raw).hexdigest()!=sha:raise ValueError(f'input changed: {path}')
    return raw


def safe(value):
    if isinstance(value,(date,datetime)):return value.isoformat()
    if isinstance(value,dict):return {str(k):safe(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [safe(v) for v in value]
    if isinstance(value,float) and not __import__('math').isfinite(value):return {'nonfinite':str(value)}
    return value


def effective_resources(protocol, reference):
    document=json.loads(checked(reference['path'],reference['sha256']))
    if (document.get('kind')!='cross_market_operational_limits_v1'
            or document.get('family')!=protocol['family']
            or document.get('protocol_sha256')!=hashlib.sha256(checked(PROTOCOL)).hexdigest()):
        raise ValueError('cross-market operational limits do not bind the frozen family')
    resources={**protocol['resources'],**document['overrides']}
    if (resources['memory_bytes'] not in (protocol['resources']['memory_bytes'],8589934592)
            or resources['cpu_budget_seconds']!=protocol['resources']['cpu_budget_seconds']
            or resources['maximum_study_output_bytes']!=protocol['resources']['maximum_study_output_bytes']):
        raise ValueError('operational amendment changed retained total CPU/memory/output contracts')
    return resources


def admit_sources(protocol,store,progress_path):
    import pyarrow.parquet as pq
    from pyarrow import BufferReader
    manifest={'files':protocol['source_files']}
    records=[];schemas={};rows_by_role={};source_bytes=0;samples={}
    for file_id,source in enumerate(manifest['files']):
        path=Path('/workspace/data')/source['path']
        if not path.resolve().is_relative_to(Path('/workspace/data')):raise ValueError('source outside original acquired data')
        raw=checked(path,maximum=protocol['resources']['maximum_source_file_bytes'])
        if len(raw)!=source['size_bytes']:raise ValueError('source changed since metadata freeze')
        sha=hashlib.sha256(raw).hexdigest();record={'file_id':file_id,'source':source,'sha256':sha,'format':path.suffix}
        if path.suffix=='.parquet':
            pf=pq.ParquetFile(BufferReader(raw));schema=str(pf.schema_arrow);schema_id=hashlib.sha256(schema.encode()).hexdigest()
            schemas[schema_id]=schema;record.update(rows=pf.metadata.num_rows,schema_id=schema_id)
            rows_by_role[source['role']]=rows_by_role.get(source['role'],0)+pf.metadata.num_rows
            if source['dataset_id'] not in samples:
                batches=pf.iter_batches(batch_size=2);batch=next(batches,None)
                samples[source['dataset_id']]={'file_id':file_id,'rows':[] if batch is None else safe(batch.to_pylist())}
        else:
            marker=json.loads(raw);record.update(rows=0,schema_id='empty_marker',marker=marker)
        records.append(record);source_bytes+=len(raw)
        with Path(progress_path).open('ab') as progress:progress.write(json.dumps({'file_id':file_id,'sha256':sha,'rows':record['rows']}).encode()+b'\n')
    return {'kind':'cross_market_admitted_sources_v1','sources':records,'source_files':len(records),'source_bytes':source_bytes,
            'schemas':schemas,'rows_by_role':rows_by_role,'samples':samples,'all_declared_sources_admitted':True,'full_population_statistics_complete':False}


def predecessor_actual(reference,store,protocol,mode):
    from trading_research.operations.artifacts import artifact_ref
    execution=json.loads(checked(reference['path'],reference['sha256']))
    if execution.get('success') is not True or execution.get('mode')!=mode or execution.get('family')!=protocol['family']:
        raise ValueError('successful own-family predecessor required')
    worker=store.read_json(artifact_ref(execution['worker']))
    if worker.get('success') is not True or worker.get('attempt_id')!=execution['attempt_id']:
        raise ValueError('predecessor worker identity differs')
    actual=store.read_json(artifact_ref(worker['actual']))
    return execution,actual


def implementation_paths():
    import ast
    pending=['src/trading_research/research/cross_market_descriptive.py','tests/test_cross_market_descriptive.py']
    seen=set()
    while pending:
        name=pending.pop()
        if name in seen:continue
        seen.add(name)
        tree=ast.parse((ROOT/name).read_text())
        for node in ast.walk(tree):
            mods=[]
            if isinstance(node,ast.ImportFrom) and node.module:mods=[node.module]
            elif isinstance(node,ast.Import):mods=[a.name for a in node.names]
            for mod in mods:
                if not mod.startswith('trading_research'):continue
                rel='src/'+mod.replace('.','/')+'.py'
                if (ROOT/rel).is_file() and rel not in seen:pending.append(rel)
    return sorted(seen)


def run_measurement(packet,protocol,store,outputs):
    import importlib.util,io,unittest
    from trading_research.research.cross_market_descriptive import run
    spec=importlib.util.spec_from_file_location('test_cross_market_descriptive',ROOT/'tests/test_cross_market_descriptive.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    stream=io.StringIO();test_result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    tests={'passed':test_result.wasSuccessful(),'tests':test_result.testsRun,'failures':len(test_result.failures),'errors':len(test_result.errors),'output':stream.getvalue()}
    outputs.json('unit-tests.json',tests,kind='cross_market_unit_tests_v1')
    if not tests['passed']:raise ValueError('cross-market literal checks failed; no actual source execution:\n'+stream.getvalue())
    admission,admitted=predecessor_actual(packet['configuration']['predecessor'],store,protocol,'admit')
    if admitted.get('kind')!='cross_market_admitted_sources_v1':raise ValueError('admission actual kind differs')
    selected=[2020] if packet['mode']=='pilot' else None
    cap=effective_resources(protocol,packet['configuration']['operational_limits'])
    pilot_gate=None
    if packet['mode']=='full':
        pilot,actual=predecessor_actual(packet['configuration']['pilot'],store,protocol,'pilot')
        if actual.get('diagnostic_profile'):raise ValueError('diagnostic profile is not an accepted throughput pilot')
        from trading_research.operations.artifacts import artifact_ref
        previous_manifest=store.read_json(artifact_ref(pilot['snapshot']))['manifest']
        current_manifest=store.read_json(artifact_ref(packet['snapshot']))['manifest']
        paths=packet['configuration']['implementation_paths']
        operational=json.loads(checked(packet['configuration']['operational_limits']['path'],packet['configuration']['operational_limits']['sha256']))
        allowed_runner=(pilot['runner_sha256']==packet['runner_sha256'] or pilot['runner_sha256']==operational.get('accepted_pilot_runner_sha256'))
        changed_paths = {name for name in paths if previous_manifest.get(name) != current_manifest.get(name)}
        alias_validation = None
        if changed_paths and operational.get('accepted_alias_validation_execution'):
            validation_execution, alias_validation = predecessor_actual(
                operational['accepted_alias_validation_execution'], store, protocol, 'pilot')
            validation_manifest = store.read_json(artifact_ref(validation_execution['snapshot']))['manifest']
            allowed_changes = {'src/trading_research/research/cross_market_alignment.py',
                'src/trading_research/research/cross_market_descriptive.py', 'tests/test_cross_market_descriptive.py'}
            if (not changed_paths <= allowed_changes
                    or alias_validation.get('kind') != 'cross_market_alias_validation_v1'
                    or alias_validation.get('all_2026_raw_sources_validated') is not True
                    or alias_validation.get('base_runner_sha256') != packet['runner_sha256']
                    or alias_validation.get('tests', {}).get('passed') is not True
                    or any(validation_manifest.get(name) != current_manifest.get(name) for name in paths)):
                raise ValueError('exact current alias correction and all source/regression checks required')
        if (not allowed_runner or pilot['configuration_implementation_paths']!=paths
                or (changed_paths and alias_validation is None)):
            raise ValueError('full cross-market requires tested implementation and exact scoped correction validation')
        pilot_sources=[s for s in admitted['sources'] if s['source'].get('year')==2020 or 'year' not in s['source']]
        canonical=protocol['canonical_partitions']; pilot_canonical=[p for p in canonical if p['year']==2020]
        all_rows=sum(s['rows'] for s in admitted['sources'])+sum(p['canonical_table']['rows'] for p in canonical)
        pilot_rows=sum(s['rows'] for s in pilot_sources)+sum(p['canonical_table']['rows'] for p in pilot_canonical)
        all_bytes=admitted['source_bytes']+sum(p['canonical_table']['size_bytes'] for p in canonical)
        pilot_bytes=sum(s['source']['size_bytes'] for s in pilot_sources)+sum(p['canonical_table']['size_bytes'] for p in pilot_canonical)
        scale=max(all_rows/max(1,pilot_rows),all_bytes/max(1,pilot_bytes),(len(admitted['sources'])+len(canonical))/max(1,len(pilot_sources)+len(pilot_canonical)),7)
        projected_cpu=pilot['cpu_seconds']*scale*1.5+60
        projected_output=actual['output_bytes']*scale*1.5+32*1024**2
        pilot_gate={'scale':scale,'margin':1.5,'projected_cpu_seconds':projected_cpu,'projected_output_bytes':projected_output,'pilot_attempt':pilot['attempt_id']}
        if operational.get('six_year_cost_execution'):
            cost_ref = operational['six_year_cost_execution']
            cost = json.loads(checked(cost_ref['path'], cost_ref['sha256']))
            cost_manifest = store.read_json(artifact_ref(cost['snapshot']))['manifest']
            if (alias_validation is None or cost.get('mode') != 'full' or cost.get('success') is not False
                    or operational.get('cost_completed_years') != list(range(2020, 2026))
                    or any(cost_manifest.get(name) != previous_manifest.get(name) for name in paths)):
                raise ValueError('six completed unchanged years and current alias validation required for cost evidence')
            # Six complete years were written before the 2026 input failure.
            # Charge a seventh full year (2026 is partial) and 25% margin.
            projected_cpu = cost['cpu_seconds'] * (7 / 6) * 1.25
            projected_output = cost['output_bytes'] * (7 / 6) * 1.25 + 32 * 1024**2
            pilot_gate.update(projected_cpu_seconds=projected_cpu, projected_output_bytes=projected_output,
                cost_execution=cost_ref, completed_years=operational['cost_completed_years'],
                margin=1.25, method='Six completed full years plus one full-year allowance; current alias handling verified separately')
        if projected_cpu>cap['mode_cpu_seconds']['full'] or projected_output>cap['per_attempt_output_bytes']-32*1024**2:
            raise ValueError('measured cross-market full resource projection exceeds frozen bound: '+str(pilot_gate))
    cpu0=time.process_time();wall0=time.monotonic()
    actual=run(protocol=protocol,admitted=admitted,store=store,outputs=outputs,selected_years=selected)
    if actual.get('passed') is not True:raise ValueError('cross-market measurement did not pass')
    actual.update(tests=tests,output_bytes=outputs.written,execution_resources={'cpu_seconds':time.process_time()-cpu0,'wall_seconds':time.monotonic()-wall0},pilot_gate=pilot_gate,selected_years=selected)
    return actual


def worker(packet_path):
    resource.setrlimit(resource.RLIMIT_CPU,(9010,9010));resource.setrlimit(resource.RLIMIT_AS,(8589934592,8589934592))
    resource.setrlimit(resource.RLIMIT_FSIZE,(8589934592,8589934592))
    packet=json.loads(checked(packet_path));protocol=json.loads(checked(PROTOCOL,packet['protocol_sha256']))
    cap=effective_resources(protocol,packet['configuration']['operational_limits']);soft=cap['mode_cpu_seconds'][packet['mode']];hard=soft+cap['hard_cpu_margin']
    resource.setrlimit(resource.RLIMIT_CPU,(soft,hard))
    resource.setrlimit(resource.RLIMIT_AS,(cap['memory_bytes'],cap['memory_bytes']))
    sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
    from trading_research.operations.artifacts import artifact_ref,publish_new
    from trading_research.operations.trials import TrialRegistry
    registry=TrialRegistry(ROOT/'evidence/trials');store=registry.artifacts;state=registry.state()
    attempt=state['attempts'][packet['attempt_id']];trial=state['trials'][packet['trial_id']]
    if (attempt['status']!='running' or attempt['trial_id']!=packet['trial_id'] or attempt['family']!=protocol['family']
            or trial['configuration']!=packet['configuration'] or trial['code_hash']!=packet['snapshot']['sha256']
            or os.getppid()!=packet['supervisor_pid'] or Path(packet_path).resolve()!=RUNS/packet['attempt_id']/'packet.json'):
        raise ValueError('cross-market worker does not identify its registered supervisor and attempt')
    manifest=store.read_json(artifact_ref(packet['snapshot']))['manifest']
    for name,sha in manifest.items():checked(ROOT/name,sha)
    checked(__file__,packet['runner_sha256'])
    if any(os.environ.get(k)!=v for k,v in packet['configuration']['thread_limits'].items()):raise ValueError('threadlimitschanged')
    if packet['mode']=='admit':
        actual=admit_sources(protocol,store,Path(packet_path).parent/"raw-admissions.jsonl")
        actual_ref=asdict(store.put_json(actual,kind=actual['kind']))
        output_bytes=actual_ref['size_bytes']
    else:
        from trading_research.research.auction_flow_storage import BoundedOutputs
        outputs=BoundedOutputs(Path(packet_path).parent/'outputs',maximum_total_bytes=cap['per_attempt_output_bytes']-32*1024**2,maximum_file_bytes=cap['per_attempt_output_bytes']-32*1024**2)
        actual=run_measurement(packet,protocol,store,outputs)
        actual_ref=asdict(store.put_json(actual,kind='cross_market_measurement_results_v1'))
        output_bytes=actual['output_bytes']+actual_ref['size_bytes']
    report={'success':True,'attempt_id':packet['attempt_id'],'trial_id':packet['trial_id'],'mode':packet['mode'],
        'protocol_sha256':packet['protocol_sha256'],'snapshot':packet['snapshot'],'actual':actual_ref,
        'source_files':len(protocol['source_files']),'output_bytes':output_bytes,
        'full_family_complete':False,'context_models_complete':False,'model_fits':0}
    if output_bytes+len(encoded(report))*2>cap['per_attempt_output_bytes']:raise ValueError('event attemptoutput exceeded')
    publish_new(Path(packet_path).parent/'worker.json',encoded(report))
    return 0


def parent(mode,predecessor=None,pilot=None):
    sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
    from trading_research.operations.artifacts import artifact_ref,code_snapshot,digest,publish_new
    from trading_research.operations.trials import TrialRegistry
    raw=checked(PROTOCOL);protocol=json.loads(raw);sha=hashlib.sha256(raw).hexdigest()
    limits_raw=checked(OPERATIONAL_LIMITS)
    limits_reference={'path':str(OPERATIONAL_LIMITS),'sha256':hashlib.sha256(limits_raw).hexdigest(),'size_bytes':len(limits_raw)}
    cap=effective_resources(protocol,limits_reference)
    registry=TrialRegistry(ROOT/'evidence/trials');store=registry.artifacts
    protocol_ref=asdict(store.put_bytes(raw,kind=protocol['kind']))
    registry.register_family(protocol['family'],scope_ids=tuple(protocol['scope_ids']),protocol=protocol_ref,
        max_attempts=protocol['resources']['max_attempts'],cpu_budget_seconds=protocol['resources']['cpu_budget_seconds'])
    state=registry.state();used=0
    for attempt in state['attempts'].values():
        if attempt['family']!=protocol['family']:continue
        for ref in attempt.get('result_artifacts',[]):
            if ref['kind']=='cross_market_execution_v1':used+=store.read_json(artifact_ref(ref))['output_bytes']
    if used+cap['per_attempt_output_bytes']>cap['maximum_study_output_bytes']:raise ValueError('event totaloutput allowance exhausted')
    prior=None
    if predecessor:
        path=Path(predecessor).resolve()
        if not path.is_relative_to(RUNS):raise ValueError('event predecessor must be ownretainedexecution')
        prior_raw=checked(path);d=json.loads(prior_raw);attempt=state['attempts'].get(d.get('attempt_id'))
        if (d.get('success') is not True or d.get('mode')!='admit' or attempt is None or attempt['status']!='succeeded'
                or not any(r['sha256']==digest(d) for r in attempt['result_artifacts'])):raise ValueError('cross-market measurement needs exactaccepted admission')
        prior={'path':str(path),'sha256':hashlib.sha256(prior_raw).hexdigest(),'size_bytes':len(prior_raw)}
    if mode in ('pilot','full') and prior is None:raise ValueError('cross-market measurement needsadmission')
    pilot_reference=None
    if mode=='full':
        if not pilot:raise ValueError('full requires accepted pilot execution')
        path=Path(pilot).resolve();raw=checked(path);d=json.loads(raw);a=state['attempts'].get(d.get('attempt_id'))
        if (not path.is_relative_to(RUNS) or d.get('success') is not True or d.get('mode')!='pilot' or a is None or a['status']!='succeeded'
                or not any(ref['sha256']==digest(d) for ref in a['result_artifacts'])):raise ValueError('registered accepted pilot required')
        pilot_reference={'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}
    snapshot=code_snapshot(ROOT,store);runner_sha=hashlib.sha256(checked(__file__)).hexdigest()
    config={'implementation_paths':implementation_paths(),'mode':mode,'protocol_sha256':sha,'predecessor':prior,'pilot':pilot_reference,'runner_sha256':runner_sha,'operational_limits':limits_reference,
        'thread_limits':{'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','ARROW_NUM_THREADS':'1'}}
    trial=registry.register(name='cross-market:'+mode,family=protocol['family'],stage='original' if mode=='admit' else 'representation',
        configuration=config,code_hash=snapshot.sha256,data_hashes={'protocol':sha},fold_version='2020plus-cross-market-v1',target_version='cross-market-curve-observation-v1')
    soft=cap['mode_cpu_seconds'][mode];hard=soft+cap['hard_cpu_margin'];attempt=registry.start(trial,cpu_reservation_seconds=hard)
    out=RUNS/attempt;out.mkdir(parents=True,exist_ok=False)
    packet={'mode':mode,'attempt_id':attempt,'trial_id':trial,'snapshot':asdict(snapshot),'runner_sha256':runner_sha,
            'protocol_sha256':sha,'configuration':config,'supervisor_pid':os.getpid()}
    publish_new(out/'packet.json',encoded(packet));started=time.monotonic();process=None;usage=None;finished=False
    try:
        with (out/'worker.log').open('xb') as log:
            process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(out/'packet.json')],cwd=ROOT,
                env={**os.environ,**config['thread_limits'],'PYTHONHASHSEED':'0'},stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            while True:
                pid,status,usage_now=os.wait4(process.pid,os.WNOHANG)
                if pid:usage=usage_now;process.returncode=os.waitstatus_to_exitcode(status);break
                if time.monotonic()-started>cap['wall_seconds']:
                    os.killpg(process.pid,signal.SIGKILL);_,status,usage=os.wait4(process.pid,0);process.returncode=os.waitstatus_to_exitcode(status);break
                time.sleep(.2)
        worker_value=json.loads(checked(out/'worker.json')) if (out/'worker.json').exists() else None
        cpu=usage.ru_utime+usage.ru_stime;wall=time.monotonic()-started
        success=bool(process.returncode==0 and worker_value and worker_value['success'] and worker_value['attempt_id']==attempt
                     and worker_value['trial_id']==trial and worker_value['snapshot']==asdict(snapshot)
                     and cpu<=soft and usage.ru_maxrss*1024<=cap['memory_bytes'] and wall<=cap['wall_seconds'])
        worker_ref=None if worker_value is None else asdict(store.put_json(worker_value,kind='cross_market_worker_v1'))
        output_bytes=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
        if worker_value is not None:
            output_bytes+=worker_ref['size_bytes']+worker_value['actual']['size_bytes']
        success=success and output_bytes<=cap['per_attempt_output_bytes']
        report={'kind':'cross_market_execution_v1','family':protocol['family'],'mode':mode,'attempt_id':attempt,'trial_id':trial,
            'configuration_implementation_paths':config['implementation_paths'],'protocol':protocol_ref,'snapshot':asdict(snapshot),'runner_sha256':runner_sha,'success':success,'worker':worker_ref,
            'cpu_seconds':cpu,'wall_seconds':wall,'peak_rss_bytes':usage.ru_maxrss*1024,'output_bytes':output_bytes,
            'exit_code':process.returncode,'finished_at':datetime.now(timezone.utc).isoformat()}
        ref=store.put_json(report,kind=report['kind']);registry.finish(attempt,status='succeeded' if success else 'failed',cpu_seconds=cpu,
            wall_seconds=wall,peak_rss_bytes=usage.ru_maxrss*1024,reason='bounded cross-market study result; all failures retained',result_artifacts=(asdict(ref),))
        finished=True;publish_new(out/'execution.json',encoded(report));print(json.dumps({'report':str(out/'execution.json'),'success':success,'cpu_seconds':cpu}),flush=True)
        return 0 if success else 1
    finally:
        if not finished:
            if process is not None and process.returncode is None:
                os.killpg(process.pid,signal.SIGKILL);_,_,usage=os.wait4(process.pid,0)
            registry.finish(attempt,status='interrupted',cpu_seconds=0 if process is None else None if usage is None else usage.ru_utime+usage.ru_stime,
                wall_seconds=time.monotonic()-started,peak_rss_bytes=0 if usage is None else usage.ru_maxrss*1024,reason='cross-market supervisor failure; reservation retained if usageunknown')


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':raise SystemExit(worker(sys.argv[2]))
    if len(sys.argv) not in (2,3,4) or sys.argv[1] not in ('admit','pilot','full'):raise SystemExit('usage: run_cross_market_study.py admit|pilot|full [admissionexecution] [pilotexecution]')
    raise SystemExit(parent(sys.argv[1],sys.argv[2] if len(sys.argv)>=3 else None,sys.argv[3] if len(sys.argv)==4 else None))
