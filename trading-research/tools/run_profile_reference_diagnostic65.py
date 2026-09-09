"""Registered 120-CPU profile of unchanged actual profile/reference reduction."""
from pathlib import Path
import cProfile
import hashlib
import importlib.util
import json
import pstats
import signal
import sys
import time
import traceback
SOURCE = Path(__file__).with_name('run_auction_flow_study.py')
BASE_SHA = '4b1e23c9b1a0373a225be391930eb869ba9e7e874c87dd0a55bb60278ffb14a7'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError('diagnostic base runner changed')
spec = importlib.util.spec_from_file_location('auction_profile_diagnostic_base', SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.__file__ = __file__
base.CHECK_EXTENSION = base.ROOT / 'validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V57.json'

class DiagnosticStop(Exception):
    pass

def diagnose(authenticated,packet_path):
    from trading_research.operations.artifacts import canonical_json,publish_new
    from trading_research.research.auction_flow_profile_statistics import run_profile_statistics
    from trading_research.research.auction_flow_storage import BoundedOutputs
    packet,protocol,cap=authenticated['packet'],authenticated['protocol'],authenticated['cap']
    operational,contract,population,windows,population_ref=base.profile_statistics_inputs(authenticated)
    outputs=BoundedOutputs(Path(packet_path).parent/'outputs',maximum_total_bytes=cap['maximum_output_bytes']-cap['supervisor_output_reserve_bytes'],maximum_file_bytes=cap['maximum_output_file_bytes'])
    profiler=cProfile.Profile()
    stop_stack=[]
    def stop(signum,frame):
        stop_stack.extend(traceback.format_stack(frame))
        raise DiagnosticStop('prespecified120CPU unchanged actual-reduction diagnostic')
    previous=signal.signal(signal.SIGPROF,stop)
    began=time.process_time(); completed=False
    try:
        signal.setitimer(signal.ITIMER_PROF,120)
        profiler.enable()
        run_profile_statistics(population=population,window_population=windows,contract=contract,
            outputs=outputs,load_reference=base.load_reference,
            selected_partition_keys=operational['selected_partition_keys'])
        completed=True
    except DiagnosticStop:
        pass
    finally:
        signal.setitimer(signal.ITIMER_PROF,0);profiler.disable();signal.signal(signal.SIGPROF,previous)
    stats=pstats.Stats(profiler)
    rows=[{'file':file,'line':line,'name':name,'calls':calls,'own_seconds':own,'cumulative_seconds':cumulative}
        for (file,line,name),(_,calls,own,cumulative,_) in stats.stats.items()]
    ref=outputs.json('profile.json',{'kind':'auction_flow_profile_reduction_diagnostic_v1',
        'measured_cpu_seconds':time.process_time()-began,'cprofile_elapsed_seconds':stats.total_tt,
        'profile_timer':'cProfile default elapsed; 120 CPU seconds via ITIMER_PROF',
        'base_runner_sha256':BASE_SHA,'implementation':operational['accepted_consumer_files'],
        'selected_partition_keys':operational['selected_partition_keys'],'completed':completed,
        'stop_stack':stop_stack,'functions':sorted(rows,key=lambda x:-x['cumulative_seconds']),
        'test_evidence':{'execution':'dfdb11a0c5c50b7f0599b505f1ece50f450f0f8ff8b3193bcccc49ba31cd8cd2','passed':56,
            'reuse_scope':'unchanged consumer/test hashes, diagnostic skips tests; failed64 actual population not accepted'}},
        kind='auction_flow_profile_reduction_diagnostic_v1')
    report={k:packet[k] for k in ('attempt_id','trial_id','protocol_sha256','code_snapshot','tools_snapshot','configuration')}
    report.update(family=protocol['family'],mode='profile-statistics',success=True,
        diagnostic_only=True,profile=ref,derived_output_bytes=outputs.written,
        scope='Unchanged actual profile reduction diagnosis only; no population, pilot, or full gate acceptance.')
    publish_new(Path(packet['worker_report']),canonical_json(report)+b'\n')
    return 0
base.profile_statistics=diagnose
if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':
        raise SystemExit(base.worker(sys.argv[2]))
    if len(sys.argv)!=1:raise SystemExit('no arguments, or registered --worker packet')
    raise SystemExit(base.parent('profile-statistics'))
