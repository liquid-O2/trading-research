"""Register complete acquired-OHLC physical-volatility measurement partitions."""
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
PROTOCOL=ROOT/'validation/PHYSICAL_OHLC_VOLATILITY_MEASUREMENT_V1.json'
RUNS=ROOT/'reports/physical-volatility-runs'


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()


def checked(path, sha=None, maximum=16*1024**2):
    path=Path(path)
    if 'archive' in path.parts or not path.is_file() or path.stat().st_size>maximum:
        raise ValueError('bounded retained input required')
    raw=path.read_bytes()
    if sha and hashlib.sha256(raw).hexdigest()!=sha:raise ValueError(f'input changed: {path}')
    return raw


def worker(packet_path):
    resource.setrlimit(resource.RLIMIT_CPU,(1610,1610));resource.setrlimit(resource.RLIMIT_AS,(4294967296,4294967296))
    resource.setrlimit(resource.RLIMIT_FSIZE,(536870912,536870912))
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
        raise ValueError('physical-volatility worker does not identify its registered supervisor and attempt')
    manifest=store.read_json(artifact_ref(packet['snapshot']))['manifest']
    for name,sha in manifest.items():checked(ROOT/name,sha)
    checked(__file__,packet['runner_sha256'])
    if any(os.environ.get(k)!=v for k,v in packet['configuration']['thread_limits'].items()):raise ValueError('threadlimitschanged')
    from trading_research.research.physical_ohlc_volatility import run
    actual=run(packet=packet,protocol=protocol,root=ROOT,store=store)
    actual_ref=asdict(store.put_json(actual,kind='physical_volatility_measurement_results_v1'))
    output_bytes=actual['output_bytes']+actual_ref['size_bytes']
    report={'success':True,'attempt_id':packet['attempt_id'],'trial_id':packet['trial_id'],'mode':packet['mode'],
        'protocol_sha256':packet['protocol_sha256'],'snapshot':packet['snapshot'],'actual':actual_ref,
        'source_partitions':len(protocol['canonical_partitions']),'output_bytes':output_bytes,
        'full_family_complete':False,'context_models_complete':False,'model_fits':0}
    if output_bytes+len(encoded(report))*2>cap['per_attempt_output_bytes']:raise ValueError('physical-volatility attemptoutput exceeded')
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
            if ref['kind']=='physical_volatility_execution_v1':used+=store.read_json(artifact_ref(ref))['output_bytes']
    if used+cap['per_attempt_output_bytes']>cap['maximum_study_output_bytes']:raise ValueError('physical-volatility totaloutput allowance exhausted')
    prior=None;pilot_execution=None;pilot_actual=None
    if predecessor:
        path=Path(predecessor).resolve()
        if not path.is_relative_to(RUNS):raise ValueError('physical-volatility predecessor must be ownretainedexecution')
        prior_raw=checked(path);d=json.loads(prior_raw);attempt=state['attempts'].get(d.get('attempt_id'))
        if (d.get('success') is not True or d.get('mode')!='pilot' or attempt is None or attempt['status']!='succeeded'
                or not any(r['sha256']==digest(d) for r in attempt['result_artifacts'])):raise ValueError('physical-volatility full measurement needs exactaccepted admission')
        prior={'path':str(path),'sha256':hashlib.sha256(prior_raw).hexdigest(),'size_bytes':len(prior_raw)}
        pilot_execution=d
        pilot_worker=store.read_json(artifact_ref(d['worker']))
        if pilot_worker.get('success') is not True or pilot_worker['attempt_id']!=d['attempt_id']:raise ValueError('pilot worker identity mismatch')
        pilot_actual=store.read_json(artifact_ref(pilot_worker['actual']))
    if mode=='full' and prior is None:raise ValueError('physical-volatility full measurement needsadmission')
    snapshot=code_snapshot(ROOT,store);runner_sha=hashlib.sha256(checked(__file__)).hexdigest()
    projection=None
    if mode=='full':
        if pilot_execution['snapshot']!=asdict(snapshot) or pilot_execution['runner_sha256']!=runner_sha:raise ValueError('full phase requires exact successful pilot implementation')
        selection=protocol['pilot_selection']
        pilot_rows=sum(x['canonical_table']['rows'] for x in protocol['canonical_partitions'] if all(x[k]==v for k,v in selection.items()))
        all_rows=sum(x['canonical_table']['rows'] for x in protocol['canonical_partitions'])
        ratio=(all_rows-pilot_rows)/pilot_rows
        projection={'cpu_seconds':1.5*pilot_execution['cpu_seconds']*ratio+60,'output_bytes':1.5*pilot_worker['output_bytes']*(ratio+1)+32*1024**2,'remaining_input_rows':all_rows-pilot_rows}
        if projection['cpu_seconds']>cap['mode_cpu_seconds']['full'] or projection['output_bytes']>cap['per_attempt_output_bytes']:raise ValueError(f'full physical-volatility projection exceeds frozen resources: {projection}')
    config={'mode':mode,'accepted_pilot':pilot_actual,'pilot_actual_reference':None if prior is None else pilot_worker['actual'],'resource_projection':projection,'protocol_sha256':sha,'predecessor':prior,'runner_sha256':runner_sha,
        'thread_limits':{'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','ARROW_NUM_THREADS':'1'}}
    trial=registry.register(name='physical-volatility:'+mode,family=protocol['family'],stage='representation',
        configuration=config,code_hash=snapshot.sha256,data_hashes={'protocol':sha},fold_version='2020plus-physical-volatility-v1',target_version='observed-ohlc-log-variance-v1')
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
        worker_ref=None if worker_value is None else asdict(store.put_json(worker_value,kind='physical_volatility_worker_v1'))
        raw_progress = 0
        output_bytes=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())+(raw_progress if worker_value is None else worker_value['output_bytes']+worker_ref['size_bytes'])
        report={'kind':'physical_volatility_execution_v1','family':protocol['family'],'mode':mode,'attempt_id':attempt,'trial_id':trial,
            'protocol':protocol_ref,'snapshot':asdict(snapshot),'runner_sha256':runner_sha,'success':success,'worker':worker_ref,
            'cpu_seconds':cpu,'wall_seconds':wall,'peak_rss_bytes':usage.ru_maxrss*1024,'output_bytes':output_bytes,
            'exit_code':process.returncode,'finished_at':datetime.now(timezone.utc).isoformat()}
        ref=store.put_json(report,kind=report['kind']);registry.finish(attempt,status='succeeded' if success else 'failed',cpu_seconds=cpu,
            wall_seconds=wall,peak_rss_bytes=usage.ru_maxrss*1024,reason='bounded physical-volatility study result; all failures retained',result_artifacts=(asdict(ref),))
        finished=True;publish_new(out/'execution.json',encoded(report));print(json.dumps({'report':str(out/'execution.json'),'success':success,'cpu_seconds':cpu}),flush=True)
        return 0 if success else 1
    finally:
        if not finished:
            if process is not None and process.returncode is None:
                os.killpg(process.pid,signal.SIGKILL);_,_,usage=os.wait4(process.pid,0)
            registry.finish(attempt,status='interrupted',cpu_seconds=0 if process is None else None if usage is None else usage.ru_utime+usage.ru_stime,
                wall_seconds=time.monotonic()-started,peak_rss_bytes=0 if usage is None else usage.ru_maxrss*1024,reason='physical-volatility supervisor failure; reservation retained if usageunknown')


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':raise SystemExit(worker(sys.argv[2]))
    if len(sys.argv) not in (2,3) or sys.argv[1] not in ('pilot','full'):raise SystemExit('usage: run_physical_volatility_study.py pilot|full [pilotexecution]')
    raise SystemExit(parent(sys.argv[1],sys.argv[2] if len(sys.argv)==3 else None))
