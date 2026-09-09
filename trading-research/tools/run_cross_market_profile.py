"""Bounded registered diagnosis of the unchanged 2020 cross-market pilot."""
from pathlib import Path
import cProfile
import hashlib
import importlib.util
import json
import marshal
import pstats
import signal
import sys

SOURCE = Path(__file__).with_name('run_cross_market_study.py')
BASE_SHA = '920bab04d9cff6dc1aa5cdd4821c5dbe484ddb755eb0007c60dc7907c7540f4f'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError('registered diagnostic base changed')
spec = importlib.util.spec_from_file_location('cross_registered_diagnostic_base', SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.__file__ = __file__
original = base.run_measurement


class DiagnosticStop(Exception):
    pass


def profiled(packet, protocol, store, outputs):
    profiler = cProfile.Profile()
    def stop(signum, frame):
        raise DiagnosticStop('prespecified 120 CPU-second diagnostic endpoint')
    previous = signal.signal(signal.SIGPROF, stop)
    complete = False
    actual = None
    try:
        signal.setitimer(signal.ITIMER_PROF, 120)
        profiler.enable()
        actual = original(packet, protocol, store, outputs)
        complete = True
    except DiagnosticStop:
        pass
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        profiler.disable()
        signal.signal(signal.SIGPROF, previous)
        stats = pstats.Stats(profiler)
        records = []
        for (filename, line, name), (primitive, calls, own, cumulative, callers) in stats.stats.items():
            records.append({'file':filename,'line':line,'name':name,'primitive_calls':primitive,
                'calls':calls,'own_seconds':own,'cumulative_seconds':cumulative})
        outputs.json('profile.json', {'kind':'cross_market_profile_v1','total_seconds':stats.total_tt,
            'completed_selected_population':complete,'base_sha256':BASE_SHA,
            'note':'Unchanged 2020 calculation, stopped at120CPU for diagnosis. Profiler overhead included; not a scientific/throughput pilot.',
            'functions':sorted(records,key=lambda row:-row['cumulative_seconds'])},kind='cross_market_profile_v1')
        with outputs.create('profile.pstats') as stream:
            marshal.dump(stats.stats,stream)
    return {'kind':'cross_market_profile_diagnostic_v1','passed':True,'diagnostic_profile':True,
        'complete_population_statistics':False,'output_bytes':outputs.written,
        'underlying_completed':complete,'underlying_actual':actual}


base.run_measurement = profiled
if __name__ == '__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--worker':
        raise SystemExit(base.worker(sys.argv[2]))
    if len(sys.argv)!=2:
        raise SystemExit('usage: run_cross_market_profile.py accepted-admission-execution')
    raise SystemExit(base.parent('pilot',sys.argv[1]))
