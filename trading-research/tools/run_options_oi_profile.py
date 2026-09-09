"""One registered diagnostic replay of the unchanged first-16-date OI pilot.

Uses the existing family, limits, supervisor and worker checks. Profiled timings
include profiler overhead and cannot be accepted as full-run throughput evidence.
"""
from pathlib import Path
import cProfile
import importlib.util
import json
import marshal
import pstats
import sys

SOURCE = Path(__file__).with_name('run_options_oi_study.py')
spec = importlib.util.spec_from_file_location('oi_registered_diagnostic_base', SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
# The registered supervisor must launch and hash this diagnostic entry point.
base.__file__ = __file__
original = base.run_measurement


def profiled(packet, protocol, store, outputs):
    profile = cProfile.Profile()
    try:
        profile.enable()
        actual = original(packet, protocol, store, outputs)
    finally:
        profile.disable()
        stats = pstats.Stats(profile)
        records = []
        for (filename, line, name), (primitive, calls, own, cumulative, callers) in stats.stats.items():
            records.append({'file': filename, 'line': line, 'name': name,
                'primitive_calls': primitive, 'calls': calls,
                'own_seconds': own, 'cumulative_seconds': cumulative})
        outputs.json('profile.json', {'kind': 'options_oi_profile_v1',
            'note': 'Diagnostic only; cProfile overhead included. No changed scientific computation.',
            'total_seconds': stats.total_tt,
            'functions': sorted(records, key=lambda x: -x['cumulative_seconds'])}, kind='options_oi_profile_v1')
        with outputs.create('profile.pstats') as stream:
            marshal.dump(stats.stats, stream)
    actual['diagnostic_profile'] = True
    actual['output_bytes'] = outputs.written
    return actual


base.run_measurement = profiled
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(base.worker(sys.argv[2]))
    if len(sys.argv) != 2:
        raise SystemExit('usage: run_options_oi_profile.py accepted-admission-execution')
    raise SystemExit(base.parent('pilot', sys.argv[1]))
