"""Registered 120 CPU-second statistics diagnostic from failed quote pilot6 output."""
from pathlib import Path
import cProfile
import hashlib
import importlib.util
import json
import pstats
import signal
import sys

SOURCE = Path(__file__).with_name('run_options_quote_study.py')
SOURCE_SHA = '16ac887f26b1097f223dacc68a432cab1ab13edd39eb5a1900d4f1cad44dedc4'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError('diagnostic base runner changed')
spec = importlib.util.spec_from_file_location('quote_statistics_diagnostic_base', SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.__file__ = __file__
DIAG = Path('/workspace/coordination/trading-research-cursor/options-quotes6-diagnosis.json')
DIAG_SHA = 'd5afc1284a55a037d91f4fc3f3a997b3fb93d66dd6fc5fd48d3c781aa567a268'

class ProfileComplete(Exception):
    pass


def profiled(packet, protocol, store, outputs):
    from trading_research.operations.artifacts import file_digest, artifact_ref
    from trading_research.research import options_quote_statistics as stats
    diagnostic = json.loads(base.checked(DIAG, DIAG_SHA))
    ref = diagnostic['retained_date_aggregates']
    path = Path(ref['path'])
    if path.stat().st_size != ref['size_bytes'] or file_digest(path) != ref['sha256']:
        raise ValueError('retained quote statistics input changed')
    old = json.loads(base.checked(diagnostic['execution']['path'], diagnostic['execution']['sha256']))
    old_manifest = store.read_json(artifact_ref(old['snapshot']))['manifest']
    new_manifest = store.read_json(artifact_ref(packet['snapshot']))['manifest']
    for name in packet['configuration']['implementation_paths']:
        if old_manifest.get(name) != new_manifest.get(name):
            raise ValueError('unchanged diagnostic implementation differs: ' + name)
    with path.open() as stream:
        rows = json.load(stream)
    selected = sorted({row['request_date'] for row in rows})
    inputs = {'date_aggregate':ref, 'failed_execution':diagnostic['execution'],
              'rows':len(rows), 'histogram_cells':sum(len(row.get('histograms',{})) for row in rows),
              'histogram_bins':sum(len(h.get('v',[])) for row in rows for h in row.get('histograms',{}).values()),
              'selected_dates':selected, 'source_rescans':0}
    outputs.json('diagnostic-input.json', inputs, kind='options_quote_statistics_diagnostic_input_v1')
    profiler = cProfile.Profile()
    def stop(signum, frame):
        raise ProfileComplete('prescribed 120 CPU-second diagnostic bound reached')
    old_handler = signal.signal(signal.SIGPROF, stop)
    stopped = False
    groups = None
    try:
        signal.setitimer(signal.ITIMER_PROF, 120)
        profiler.enable()
        groups, cfg = stats.build_group_statistics(rows, protocol=protocol,
            intended_all=selected, chains=protocol['population']['chains'],
            stages=protocol['population']['stages'], selected_dates=selected)
    except ProfileComplete:
        stopped = True
    finally:
        profiler.disable()
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.signal(signal.SIGPROF, old_handler)
        measured = pstats.Stats(profiler)
        records = [{'file':f,'line':line,'name':name,'primitive_calls':v[0],
                    'calls':v[1],'own_seconds':v[2],'cumulative_seconds':v[3]}
                   for (f,line,name),v in measured.stats.items()]
        outputs.json('profile.json', {'kind':'options_quote_statistics_profile_v1',
            'diagnostic_only':True, 'bound_reached':stopped, 'total_seconds':measured.total_tt,
            'functions':sorted(records,key=lambda x:-x['cumulative_seconds'])},
            kind='options_quote_statistics_profile_v1')
    return {'passed':True, 'diagnostic_only':True, 'full_family_complete':False,
            'complete_scientific_statistics':False, 'source_scans':0,
            'bound_reached':stopped, 'finished_groups':None if groups is None else len(groups),
            'output_bytes':outputs.written}

base.run_measurement = profiled
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(base.worker(sys.argv[2]))
    if len(sys.argv) != 3:
        raise SystemExit('usage: run_options_quote_profile.py accepted-admission accepted-oi')
    raise SystemExit(base.parent('pilot', sys.argv[1], oi=sys.argv[2]))
