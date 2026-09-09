"""Register bounded admission and measurement of the acquired options OI sources."""
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
PROTOCOL=ROOT/'validation/OPTIONS_OI_REPORT_LIFECYCLE_V1.json'
RUNS=ROOT/'reports/options-oi-runs'


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


def admit_sources(protocol,store,progress_path):
    import pyarrow.parquet as pq
    from pyarrow import BufferReader
    reference=protocol['source_file_manifest']
    manifest=json.loads(checked(reference['path'],reference['sha256']))
    if manifest['file_count']!=len(manifest['files']):raise ValueError('source file membership differs')
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
    return {'kind':'options_oi_admitted_sources_v1','sources':records,'source_files':len(records),'source_bytes':source_bytes,
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
    pending=['src/trading_research/research/options_oi_measurements.py','tests/test_options_oi_measurements.py']
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


def verify_pilot2_logical(actual, store, protocol, outputs):
    import math
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    from trading_research.operations.artifacts import artifact_ref
    baseline_path=RUNS/'7afd70dbe582775095dc3367834abdd4ba4a71ff2263dff0948587ba3d7b0816/execution.json'
    baseline_raw=checked(baseline_path)
    _,expected=predecessor_actual({'path':str(baseline_path),'sha256':hashlib.sha256(baseline_raw).hexdigest()},store,protocol,'pilot')
    def table(refs):
        refs=[refs] if isinstance(refs,dict) else refs
        return pa.concat_tables([pq.read_table(pa.BufferReader(checked(r['path'],r['sha256'],maximum=128*1024**2))) for r in refs])
    def jsonref(ref):return json.loads(checked(ref['path'],ref['sha256'],maximum=128*1024**2))
    def rec(a,b,path='value'):
        if type(a) is dict:
            if type(b) is not dict or a.keys()!=b.keys():raise ValueError('logical keys mismatch: '+path)
            for k in a:rec(a[k],b[k],path+'.'+str(k))
        elif type(a) is list:
            if type(b) is not list or len(a)!=len(b):raise ValueError('logical list mismatch: '+path)
            for i,(x,y) in enumerate(zip(a,b)):rec(x,y,path+'['+str(i)+']')
        elif type(a) is float and type(b) in (float,int):
            if not math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12):raise ValueError('logical number mismatch: '+path+' '+repr((a,b)))
        elif a!=b:raise ValueError('logical value mismatch: '+path+' '+repr((a,b)))
    rec(expected['counts'],actual['counts'],'counts')
    report=table(actual['refs']['reports'])
    for suffix in ['oi','ts_event_ns','file_id','row_index']:
        name='last_'+suffix
        report=report.set_column(report.schema.get_field_index(name),name,pc.if_else(report['last_eq_first'],report['first_'+suffix],report[name]))
    reports_by_id=report.sort_by([('report_id','ascending')])
    checks={}
    order_keys={
      'reports':['contract_id','request_date'], 'lifecycle':['contract_id','prior_date','next_date'],
      'asof_intervals':['contract_id','valid_from_ns','ts_event_ns','valid_to_ns'],
      'identity_map':['contract_id'], 'exceptions':['file_id','row_index'], 'membership':['file_id'],
      'coverage':['chain','request_date'],'asof_aggregates':['chain','cut_date','cut_label'],
    }
    for key,keys in order_keys.items():
        left=table(expected['refs'][key])
        right=report if key=='reports' else table(actual['refs'][key])
        if key=='lifecycle':
            for name in left.column_names:
                if name in right.column_names:continue
                parts=name.split('_')
                if len(parts)>=3 and parts[0] in ('first','last') and parts[1] in ('prior','next'):
                    field=parts[0]+'_'+'_'.join(parts[2:])
                    ids=right[parts[1]+'_report_id']
                    values=pc.take(reports_by_id[field],ids)
                    right=right.append_column(name,values)
                else:raise ValueError('unreconstructable lifecycle field: '+name)
        right=right.select(left.column_names).cast(left.schema.remove_metadata())
        left=left.replace_schema_metadata(None)
        if left.num_rows!=right.num_rows:raise ValueError('logical row count mismatch: '+key)
        left=left.sort_by([(k,'ascending') for k in keys]);right=right.sort_by([(k,'ascending') for k in keys])
        if not left.equals(right,check_metadata=False):
            bad=[name for name in left.column_names if not left[name].equals(right[name])]
            raise ValueError('logical table mismatch: '+key+' fields='+repr(bad))
        checks[key]={'rows':left.num_rows,'columns':len(left.column_names),'equal':True}
        del left,right
    for key in ['date_aggregates','distributions']:
        rec(jsonref(expected['refs'][key]),jsonref(actual['refs'][key]),key)
        checks[key]={'equal':True,'float_tolerance':1e-12}
    rec(jsonref(expected['refs']['statistics'])['groups'],jsonref(actual['refs']['statistics'])['groups'],'statistics.groups')
    checks['statistics.groups']={'equal':True,'float_tolerance':1e-12}
    return outputs.json('pilot2-logical-parity.json',{'passed':True,'baseline_execution':str(baseline_path),'checks':checks},kind='options_oi_complete_pilot_logical_parity_v1')


def run_measurement(packet,protocol,store,outputs):
    import importlib.util,io,unittest
    from trading_research.research.options_oi_measurements import run
    spec=importlib.util.spec_from_file_location('test_options_oi_measurements',ROOT/'tests/test_options_oi_measurements.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    check_cpu0=time.process_time()
    stream=io.StringIO();test_result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    tests={'passed':test_result.wasSuccessful(),'tests':test_result.testsRun,'failures':len(test_result.failures),'errors':len(test_result.errors),'output':stream.getvalue()}
    tests['cpu_seconds']=time.process_time()-check_cpu0
    outputs.json('unit-tests.json',tests,kind='options_oi_unit_tests_v1')
    if not tests['passed']:raise ValueError('options OI literal checks failed; no actual source execution:\n'+stream.getvalue())
    admission,admitted=predecessor_actual(packet['configuration']['predecessor'],store,protocol,'admit')
    if admitted.get('kind')!='options_oi_admitted_sources_v1':raise ValueError('admission actual kind differs')
    from trading_research.foundations.cash_calendar import CashCalendar
    from trading_research.foundations.calendar import local_timestamp
    from datetime import time as clock_time,timedelta
    calendar_ref=protocol['cash_calendar'];checked(calendar_ref['path'],calendar_ref['sha256']);calendar=CashCalendar(calendar_ref['path'])
    day=date.fromisoformat(protocol['population']['first_date']);end=date.fromisoformat(protocol['population']['last_date']);intended=[]
    cut=local_timestamp(date(2026,9,4),clock_time(0),calendar.zone)
    while day<=end:
        if calendar.resolve(day,cut=cut).state!='closed':intended.append(day.isoformat())
        day+=timedelta(days=1)
    selected=intended[:16] if packet['mode']=='pilot' else None
    pilot_gate=None
    if packet['mode']=='full':
        pilot,actual=predecessor_actual(packet['configuration']['pilot'],store,protocol,'pilot')
        from trading_research.operations.artifacts import artifact_ref
        previous_manifest=store.read_json(artifact_ref(pilot['snapshot']))['manifest']
        current_manifest=store.read_json(artifact_ref(packet['snapshot']))['manifest']
        paths=packet['configuration']['implementation_paths']
        if (pilot['runner_sha256']!=packet['runner_sha256'] or pilot['configuration_implementation_paths']!=paths
                or any(previous_manifest.get(name)!=current_manifest.get(name) for name in paths)):
            raise ValueError('full OI requires unchanged tested runner and transitive implementation')
        if not actual.get('logical_parity'):raise ValueError('accepted pilot2 logical population parity required')
        selected_set=set(intended[:16]);pilot_sources=[s for s in admitted['sources'] if s['source']['request_date'] in selected_set]
        scale=max(len(admitted['sources'])/max(1,len(pilot_sources)),sum(s['rows'] for s in admitted['sources'])/max(1,sum(s['rows'] for s in pilot_sources)),len(intended)/16)
        resources=actual['resources'];group_scale=7*1.5
        projected_cpu=(resources['production_cpu_seconds']*scale*1.5 + resources['statistics_cpu_seconds']*group_scale + actual['tests']['cpu_seconds'] + 60)
        projected_output=(resources['production_output_bytes']*scale*1.5 + resources['statistics_output_bytes']*group_scale + 32*1024**2)
        pilot_gate={'scale':scale,'margin':1.5,'projected_cpu_seconds':projected_cpu,'projected_output_bytes':projected_output,'pilot_attempt':pilot['attempt_id']}
        if projected_cpu>protocol['resources']['mode_cpu_seconds']['full'] or projected_output>protocol['resources']['per_attempt_output_bytes']-32*1024**2:
            raise ValueError('measured OI full resource projection exceeds frozen bound: '+str(pilot_gate))
    cpu0=time.process_time();wall0=time.monotonic()
    actual=run(protocol=protocol,admitted=admitted,outputs=outputs,selected_dates=selected)
    if actual.get('passed') is not True:raise ValueError('options OI measurement did not pass')
    actual.update(tests=tests,output_bytes=outputs.written,execution_resources={'cpu_seconds':time.process_time()-cpu0,'wall_seconds':time.monotonic()-wall0},pilot_gate=pilot_gate,selected_dates=selected)
    if packet['mode']=='pilot':
        parity_cpu=time.process_time();actual['logical_parity']=verify_pilot2_logical(actual,store,protocol,outputs)
        actual['logical_parity_cpu_seconds']=time.process_time()-parity_cpu
        actual['output_bytes']=outputs.written
    return actual


def worker(packet_path):
    resource.setrlimit(resource.RLIMIT_CPU,(5010,5010));resource.setrlimit(resource.RLIMIT_AS,(4294967296,4294967296))
    resource.setrlimit(resource.RLIMIT_FSIZE,(4294967296,4294967296))
    packet=json.loads(checked(packet_path));protocol=json.loads(checked(PROTOCOL,packet['protocol_sha256']))
    cap=protocol['resources'];soft=cap['mode_cpu_seconds'][packet['mode']];hard=soft+cap['hard_cpu_margin']
    resource.setrlimit(resource.RLIMIT_CPU,(soft,hard))
    sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
    from trading_research.operations.artifacts import artifact_ref,publish_new
    from trading_research.operations.trials import TrialRegistry
    registry=TrialRegistry(ROOT/'evidence/trials');store=registry.artifacts;state=registry.state()
    attempt=state['attempts'][packet['attempt_id']];trial=state['trials'][packet['trial_id']]
    if (attempt['status']!='running' or attempt['trial_id']!=packet['trial_id'] or attempt['family']!=protocol['family']
            or trial['configuration']!=packet['configuration'] or trial['code_hash']!=packet['snapshot']['sha256']
            or os.getppid()!=packet['supervisor_pid'] or Path(packet_path).resolve()!=RUNS/packet['attempt_id']/'packet.json'):
        raise ValueError('options OI worker does not identify its registered supervisor and attempt')
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
        actual_ref=asdict(store.put_json(actual,kind='options_oi_measurement_results_v1'))
        output_bytes=actual['output_bytes']+actual_ref['size_bytes']
    report={'success':True,'attempt_id':packet['attempt_id'],'trial_id':packet['trial_id'],'mode':packet['mode'],
        'protocol_sha256':packet['protocol_sha256'],'snapshot':packet['snapshot'],'actual':actual_ref,
        'source_files':sum(d['source_file_count'] for d in protocol['source_datasets']),'output_bytes':output_bytes,
        'full_family_complete':False,'context_models_complete':False,'model_fits':0}
    if output_bytes+len(encoded(report))*2>cap['per_attempt_output_bytes']:raise ValueError('event attemptoutput exceeded')
    publish_new(Path(packet_path).parent/'worker.json',encoded(report))
    return 0


def parent(mode,predecessor=None,pilot=None):
    sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
    from trading_research.operations.artifacts import artifact_ref,code_snapshot,digest,publish_new
    from trading_research.operations.trials import TrialRegistry
    raw=checked(PROTOCOL);protocol=json.loads(raw);sha=hashlib.sha256(raw).hexdigest();cap=protocol['resources']
    registry=TrialRegistry(ROOT/'evidence/trials');store=registry.artifacts
    protocol_ref=asdict(store.put_bytes(raw,kind=protocol['kind']))
    registry.register_family(protocol['family'],scope_ids=tuple(protocol['scope_ids']),protocol=protocol_ref,
        max_attempts=cap['max_attempts'],cpu_budget_seconds=cap['cpu_budget_seconds'])
    state=registry.state();used=0
    for attempt in state['attempts'].values():
        if attempt['family']!=protocol['family']:continue
        for ref in attempt.get('result_artifacts',[]):
            if ref['kind']=='options_oi_execution_v1':used+=store.read_json(artifact_ref(ref))['output_bytes']
    if used+cap['per_attempt_output_bytes']>cap['maximum_study_output_bytes']:raise ValueError('event totaloutput allowance exhausted')
    prior=None
    if predecessor:
        path=Path(predecessor).resolve()
        if not path.is_relative_to(RUNS):raise ValueError('event predecessor must be ownretainedexecution')
        prior_raw=checked(path);d=json.loads(prior_raw);attempt=state['attempts'].get(d.get('attempt_id'))
        if (d.get('success') is not True or d.get('mode')!='admit' or attempt is None or attempt['status']!='succeeded'
                or not any(r['sha256']==digest(d) for r in attempt['result_artifacts'])):raise ValueError('options-oi measurement needs exactaccepted admission')
        prior={'path':str(path),'sha256':hashlib.sha256(prior_raw).hexdigest(),'size_bytes':len(prior_raw)}
    if mode in ('pilot','full') and prior is None:raise ValueError('options-oi measurement needsadmission')
    pilot_reference=None
    if mode=='full':
        if not pilot:raise ValueError('full requires accepted pilot execution')
        path=Path(pilot).resolve();raw=checked(path);d=json.loads(raw);a=state['attempts'].get(d.get('attempt_id'))
        if (not path.is_relative_to(RUNS) or d.get('success') is not True or d.get('mode')!='pilot' or a is None or a['status']!='succeeded'
                or not any(ref['sha256']==digest(d) for ref in a['result_artifacts'])):raise ValueError('registered accepted pilot required')
        pilot_reference={'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw)}
    snapshot=code_snapshot(ROOT,store);runner_sha=hashlib.sha256(checked(__file__)).hexdigest()
    config={'implementation_paths':implementation_paths(),'mode':mode,'protocol_sha256':sha,'predecessor':prior,'pilot':pilot_reference,'runner_sha256':runner_sha,
        'thread_limits':{'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','ARROW_NUM_THREADS':'1'}}
    trial=registry.register(name='options-oi:'+mode,family=protocol['family'],stage='original' if mode=='admit' else 'representation',
        configuration=config,code_hash=snapshot.sha256,data_hashes={'protocol':sha},fold_version='2020plus-options-oi-v1',target_version='options-oi-curve-observation-v1')
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
        worker_ref=None if worker_value is None else asdict(store.put_json(worker_value,kind='options_oi_worker_v1'))
        raw_progress = 0
        output_bytes=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())+(raw_progress if worker_value is None else worker_value['output_bytes']+worker_ref['size_bytes'])
        report={'kind':'options_oi_execution_v1','family':protocol['family'],'mode':mode,'attempt_id':attempt,'trial_id':trial,
            'configuration_implementation_paths':config['implementation_paths'],'protocol':protocol_ref,'snapshot':asdict(snapshot),'runner_sha256':runner_sha,'success':success,'worker':worker_ref,
            'cpu_seconds':cpu,'wall_seconds':wall,'peak_rss_bytes':usage.ru_maxrss*1024,'output_bytes':output_bytes,
            'exit_code':process.returncode,'finished_at':datetime.now(timezone.utc).isoformat()}
        ref=store.put_json(report,kind=report['kind']);registry.finish(attempt,status='succeeded' if success else 'failed',cpu_seconds=cpu,
            wall_seconds=wall,peak_rss_bytes=usage.ru_maxrss*1024,reason='bounded options OI study result; all failures retained',result_artifacts=(asdict(ref),))
        finished=True;publish_new(out/'execution.json',encoded(report));print(json.dumps({'report':str(out/'execution.json'),'success':success,'cpu_seconds':cpu}),flush=True)
        return 0 if success else 1
    finally:
        if not finished:
            if process is not None and process.returncode is None:
                os.killpg(process.pid,signal.SIGKILL);_,_,usage=os.wait4(process.pid,0)
            registry.finish(attempt,status='interrupted',cpu_seconds=0 if process is None else None if usage is None else usage.ru_utime+usage.ru_stime,
                wall_seconds=time.monotonic()-started,peak_rss_bytes=0 if usage is None else usage.ru_maxrss*1024,reason='options OI supervisor failure; reservation retained if usageunknown')


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':raise SystemExit(worker(sys.argv[2]))
    if len(sys.argv) not in (2,3,4) or sys.argv[1] not in ('admit','pilot','full'):raise SystemExit('usage: run_options_oi_study.py admit|pilot|full [admissionexecution] [pilotexecution]')
    raise SystemExit(parent(sys.argv[1],sys.argv[2] if len(sys.argv)>=3 else None,sys.argv[3] if len(sys.argv)==4 else None))
