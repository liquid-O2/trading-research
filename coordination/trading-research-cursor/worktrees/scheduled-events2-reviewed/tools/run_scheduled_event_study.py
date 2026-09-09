"""Register bounded admission and measurement of the acquired event calendars."""
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
PROTOCOL=ROOT/'validation/SCHEDULED_EVENT_MEASUREMENT_V1.json'
RUNS=ROOT/'reports/scheduled-event-runs'
WINDOW_INPUTS=ROOT/'validation/SCHEDULED_EVENT_WINDOW_INPUTS_V1.json'


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
    import csv,io
    import pyarrow.parquet as pq
    from pyarrow import BufferReader
    records=[]
    for source in protocol['source_files']:
        path=Path('/workspace/data')/source['path']
        if not path.resolve().is_relative_to(Path('/workspace/data')):raise ValueError('raw source outside acquireddata')
        raw=checked(path,maximum=2*1024**2)
        if len(raw)!=source['size_bytes']:raise ValueError('source size changed before admission')
        ref=asdict(store.put_bytes(raw,kind='scheduled_event_original_source'))
        with Path(progress_path).open('ab') as progress:progress.write(json.dumps({'source':source,'raw':ref}).encode()+b'\n')
        record={'source':source,'raw':ref,'format':path.suffix.lower()}
        if path.suffix=='.parquet':
            table=pq.read_table(BufferReader(raw))
            if table.num_rows>100000:raise ValueError('unexpected event population size')
            record.update(rows=table.num_rows,schema=str(table.schema),columns=table.column_names,
                          sample=safe(table.slice(0,5).to_pylist()))
        elif path.suffix in ('.csv','.tsv'):
            text=raw.decode('utf-8-sig');reader=csv.DictReader(io.StringIO(text),delimiter='\t' if path.suffix=='.tsv' else ',')
            rows=list(reader);record.update(rows=len(rows),columns=reader.fieldnames,sample=safe(rows[:5]))
        else:
            record.update(rows=None,note='Original source page retained; normalization/source equality remains a measurement question.')
        records.append(record)
    return {'kind':'scheduled_event_admitted_sources_v1','sources':records,'source_files':len(records),
            'all_declared_sources_admitted':True,'full_population_statistics_complete':False}


def worker(packet_path):
    resource.setrlimit(resource.RLIMIT_CPU,(610,610));resource.setrlimit(resource.RLIMIT_AS,(2147483648,2147483648))
    resource.setrlimit(resource.RLIMIT_FSIZE,(134217728,134217728))
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
        raise ValueError('event worker does not identify its registered supervisor and attempt')
    manifest=store.read_json(artifact_ref(packet['snapshot']))['manifest']
    for name,sha in manifest.items():checked(ROOT/name,sha)
    checked(__file__,packet['runner_sha256'])
    if any(os.environ.get(k)!=v for k,v in packet['configuration']['thread_limits'].items()):raise ValueError('threadlimitschanged')
    if packet['mode']=='admit':
        actual=admit_sources(protocol,store,Path(packet_path).parent/"raw-admissions.jsonl")
        actual_ref=asdict(store.put_json(actual,kind=actual['kind']))
        output_bytes=sum(source['raw']['size_bytes'] for source in actual['sources'])+actual_ref['size_bytes']
    else:
        from trading_research.research.scheduled_event_measurements import run
        actual=run(packet=packet,protocol=protocol,root=ROOT,store=store)
        actual_ref=asdict(store.put_json(actual,kind='scheduled_event_measurement_results_v1'))
        output_bytes=actual['output_bytes']+actual_ref['size_bytes']
    report={'success':True,'attempt_id':packet['attempt_id'],'trial_id':packet['trial_id'],'mode':packet['mode'],
        'protocol_sha256':packet['protocol_sha256'],'snapshot':packet['snapshot'],'actual':actual_ref,
        'source_files':len(protocol['source_files']),'output_bytes':output_bytes,
        'full_family_complete':False,'context_models_complete':False,'model_fits':0}
    if output_bytes+len(encoded(report))*2>cap['per_attempt_output_bytes']:raise ValueError('event attemptoutput exceeded')
    publish_new(Path(packet_path).parent/'worker.json',encoded(report))
    return 0


def parent(mode,predecessor=None):
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
            if ref['kind']=='scheduled_event_execution_v1':used+=store.read_json(artifact_ref(ref))['output_bytes']
    if used+cap['per_attempt_output_bytes']>cap['maximum_study_output_bytes']:raise ValueError('event totaloutput allowance exhausted')
    prior=None
    if predecessor:
        path=Path(predecessor).resolve()
        if not path.is_relative_to(RUNS):raise ValueError('event predecessor must be ownretainedexecution')
        prior_raw=checked(path);d=json.loads(prior_raw);attempt=state['attempts'].get(d.get('attempt_id'))
        if (d.get('success') is not True or d.get('mode')!='admit' or attempt is None or attempt['status']!='succeeded'
                or not any(r['sha256']==digest(d) for r in attempt['result_artifacts'])):raise ValueError('eventmeasurement needs exactaccepted admission')
        prior={'path':str(path),'sha256':hashlib.sha256(prior_raw).hexdigest(),'size_bytes':len(prior_raw)}
    if mode=='measure' and prior is None:raise ValueError('eventmeasurement needsadmission')
    window_inputs=None
    if mode=='measure':
        supplement=checked(WINDOW_INPUTS)
        value=json.loads(supplement)
        if value['family']!=protocol['family']:raise ValueError('eventwindowfamily mismatch')
        window_inputs={'path':str(WINDOW_INPUTS),'sha256':hashlib.sha256(supplement).hexdigest(),'size_bytes':len(supplement),'kind':value['kind']}
        store.put_bytes(supplement,kind=value['kind'])
    snapshot=code_snapshot(ROOT,store);runner_sha=hashlib.sha256(checked(__file__)).hexdigest()
    config={'mode':mode,'protocol_sha256':sha,'predecessor':prior,'runner_sha256':runner_sha,'window_inputs':window_inputs,
        'thread_limits':{'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','ARROW_NUM_THREADS':'1'}}
    trial=registry.register(name='scheduled-events:'+mode,family=protocol['family'],stage='original' if mode=='admit' else 'representation',
        configuration=config,code_hash=snapshot.sha256,data_hashes={'protocol':sha},fold_version='2020plus-scheduled-calendar-v1',target_version='event-schedule-observation-v1')
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
        worker_ref=None if worker_value is None else asdict(store.put_json(worker_value,kind='scheduled_event_worker_v1'))
        raw_progress = sum(json.loads(line)['raw']['size_bytes'] for line in (out/'raw-admissions.jsonl').read_text().splitlines()) if (out/'raw-admissions.jsonl').exists() else 0
        output_bytes=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())+(raw_progress if worker_value is None else worker_value['output_bytes']+worker_ref['size_bytes'])
        report={'kind':'scheduled_event_execution_v1','family':protocol['family'],'mode':mode,'attempt_id':attempt,'trial_id':trial,
            'protocol':protocol_ref,'snapshot':asdict(snapshot),'runner_sha256':runner_sha,'success':success,'worker':worker_ref,
            'cpu_seconds':cpu,'wall_seconds':wall,'peak_rss_bytes':usage.ru_maxrss*1024,'output_bytes':output_bytes,
            'exit_code':process.returncode,'finished_at':datetime.now(timezone.utc).isoformat()}
        ref=store.put_json(report,kind=report['kind']);registry.finish(attempt,status='succeeded' if success else 'failed',cpu_seconds=cpu,
            wall_seconds=wall,peak_rss_bytes=usage.ru_maxrss*1024,reason='bounded event study result; all failures retained',result_artifacts=(asdict(ref),))
        finished=True;publish_new(out/'execution.json',encoded(report));print(json.dumps({'report':str(out/'execution.json'),'success':success,'cpu_seconds':cpu}),flush=True)
        return 0 if success else 1
    finally:
        if not finished:
            if process is not None and process.returncode is None:
                os.killpg(process.pid,signal.SIGKILL);_,_,usage=os.wait4(process.pid,0)
            registry.finish(attempt,status='interrupted',cpu_seconds=0 if process is None else None if usage is None else usage.ru_utime+usage.ru_stime,
                wall_seconds=time.monotonic()-started,peak_rss_bytes=0 if usage is None else usage.ru_maxrss*1024,reason='event supervisor failure; reservation retained if usageunknown')


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':raise SystemExit(worker(sys.argv[2]))
    if len(sys.argv) not in (2,3) or sys.argv[1] not in ('admit','measure'):raise SystemExit('usage: run_scheduled_event_study.py admit|measure [admissionexecution]')
    raise SystemExit(parent(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else None))
