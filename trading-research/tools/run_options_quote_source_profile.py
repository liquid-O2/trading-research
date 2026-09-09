"""Registered source-measurement profile of the unchanged quote implementation."""
from pathlib import Path
import cProfile
import hashlib
import importlib.util
import pstats
import signal
import sys

SOURCE = Path(__file__).with_name('run_options_quote_study.py')
BASE_SHA = '16ac887f26b1097f223dacc68a432cab1ab13edd39eb5a1900d4f1cad44dedc4'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError('source diagnostic base changed')
spec = importlib.util.spec_from_file_location('quote_source_diagnostic_base', SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.__file__ = __file__


class DiagnosticStop(Exception):
    pass


def diagnose(packet, protocol, store, outputs):
    from trading_research.research.options_quote_measurements import run
    _, admitted = base.predecessor_actual(packet['configuration']['predecessor'], store, protocol, 'admit')
    _, oi = base.accepted_oi(packet['configuration']['oi_execution'], store, full=False)
    profiler = cProfile.Profile()
    def stop(signum, frame):
        raise DiagnosticStop('prespecified60CPU source-only diagnostic endpoint')
    previous = signal.signal(signal.SIGPROF, stop)
    completed = False
    try:
        signal.setitimer(signal.ITIMER_PROF, 60)
        profiler.enable()
        run(protocol=protocol, admitted=admitted, oi_population=oi, store=store, outputs=outputs,
            selected_dates=base.quote_dates(protocol)[:8], selected_chains=['NDXP'])
        completed = True
    except DiagnosticStop:
        pass
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        profiler.disable()
        signal.signal(signal.SIGPROF, previous)
    stats = pstats.Stats(profiler)
    rows = [{'file':file, 'line':line, 'name':name, 'calls':calls,
             'own_seconds':own, 'cumulative_seconds':cumulative}
            for (file, line, name), (_, calls, own, cumulative, _) in stats.stats.items()]
    ref = outputs.json('profile.json', {
        'kind':'options_quote_source_profile_v1', 'total_seconds':stats.total_tt,
        'bound_cpu_seconds':60, 'selected_chains':['NDXP'], 'base_runner_sha256':BASE_SHA,
        'functions':sorted(rows,key=lambda row:-row['cumulative_seconds']),
        'completed_selected_population':completed,
        'note':'Unchanged implementation, actual source measurements only. Tests already passed42 inpilot10; this skips tests and is diagnostic only, never a pilot/full gate.',
    }, kind='options_quote_source_profile_v1')
    return {'kind':'options_quote_source_profile_result_v1', 'passed':True,
            'diagnostic_only':True, 'full_population_complete':False,
            'profile':ref, 'output_bytes':outputs.written}


base.run_measurement = diagnose
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(base.worker(sys.argv[2]))
    if len(sys.argv) != 3:
        raise SystemExit('usage: run_options_quote_source_profile.py admission-execution oi-execution')
    raise SystemExit(base.parent('pilot',sys.argv[1],oi=sys.argv[2]))
