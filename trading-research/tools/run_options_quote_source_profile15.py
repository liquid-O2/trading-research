"""Registered source-measurement profile of the unchanged quote implementation."""
from pathlib import Path
import cProfile
import hashlib
import importlib.util
import pstats
import signal
import sys
import time

SOURCE = Path(__file__).with_name('run_options_quote_study.py')
BASE_SHA = '5c78e97395686025bdbabfd87216f379ca858502ee064caac27a430bffbf4daf'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError('source diagnostic base changed')
spec = importlib.util.spec_from_file_location('quote_source_diagnostic_base', SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.__file__ = __file__


class DiagnosticStop(Exception):
    pass


def diagnose(packet, protocol, store, outputs):
    from trading_research.research import options_quote_measurements as measurement
    run = measurement.run
    _, admitted = base.predecessor_actual(packet['configuration']['predecessor'], store, protocol, 'admit')
    _, oi = base.accepted_oi(packet['configuration']['oi_execution'], store, full=False)
    profiler = cProfile.Profile(timer=time.process_time)
    source_counts = {"files":0,"rows":0,"bytes":0}
    read_quote = measurement.read_admitted_quote
    def counted_read(*args, **kwargs):
        result = read_quote(*args, **kwargs)
        source_counts["files"] += 1
        source_counts["rows"] += result[1]["rows"]
        source_counts["bytes"] += result[1]["size_bytes"]
        return result
    measurement.read_admitted_quote = counted_read
    original_finalize = measurement.SupportStore.finalize
    measurement_started = None
    def begin_after_bootstrap(self):
        nonlocal measurement_started
        value = original_finalize(self)
        measurement_started = time.process_time()
        signal.setitimer(signal.ITIMER_PROF, 120)
        profiler.enable()
        return value
    measurement.SupportStore.finalize = begin_after_bootstrap
    def stop(signum, frame):
        raise DiagnosticStop('prespecified120CPU post-bootstrap diagnostic endpoint')
    previous = signal.signal(signal.SIGPROF, stop)
    completed = False
    try:
        run(protocol=protocol, admitted=admitted, oi_population=oi, store=store, outputs=outputs,
            selected_dates=base.quote_dates(protocol)[:8], calculate_statistics=False)
        completed = True
    except DiagnosticStop:
        pass
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        profiler.disable()
        signal.signal(signal.SIGPROF, previous)
        measurement.read_admitted_quote = read_quote
        measurement.SupportStore.finalize = original_finalize
    stats = pstats.Stats(profiler)
    rows = [{'file':file, 'line':line, 'name':name, 'calls':calls,
             'own_seconds':own, 'cumulative_seconds':cumulative}
            for (file, line, name), (_, calls, own, cumulative, _) in stats.stats.items()]
    ref = outputs.json('profile.json', {
        'kind':'options_quote_source_profile_v1', 'total_seconds':stats.total_tt,
        'bound_cpu_seconds':120, 'selected_chains':'all7chains',
        'source_counts':source_counts, 'measurement_cpu_seconds':None if measurement_started is None else time.process_time()-measurement_started,
        'base_runner_sha256':BASE_SHA,
        'functions':sorted(rows,key=lambda row:-row['cumulative_seconds']),
        'completed_selected_population':completed,
        'note':'Unchanged implementation, actual source measurements only. Tests already passed48 inpilot14 with complete table and statistics parity to12. CPU timer starts after OI/support initialization. Diagnostic only, never a pilot/full gate.',
    }, kind='options_quote_source_profile_v1')
    return {'kind':'options_quote_source_profile_result_v1', 'passed':True,
            'diagnostic_only':True, 'full_population_complete':False,
            'profile':ref, 'output_bytes':outputs.written}


base.run_measurement = diagnose
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(base.worker(sys.argv[2]))
    if len(sys.argv) != 3:
        raise SystemExit('usage: run_options_quote_source_profile15.py admission-execution oi-execution')
    raise SystemExit(base.parent('pilot',sys.argv[1],oi=sys.argv[2]))
