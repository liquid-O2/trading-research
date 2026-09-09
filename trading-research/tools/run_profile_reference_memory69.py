"""Registered diagnosis of failed profile68 retained component allocations."""
from pathlib import Path
import gc
import hashlib
import importlib.util
import signal
import sys
import time
import traceback

SOURCE = Path(__file__).with_name('run_auction_flow_study.py')
BASE_SHA = 'fadade3bbe0e6674a78c83787ebaa5ba78c2141709205e78767887f35fc7c951'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError('diagnostic base runner changed')
spec = importlib.util.spec_from_file_location('profile_memory_diagnostic_base', SOURCE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.__file__ = __file__
base.TOOL_FILES = (*base.TOOL_FILES, 'tools/run_profile_reference_memory69.py')
base.CHECK_EXTENSION = base.ROOT / 'validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V60.json'


class DiagnosticStop(Exception):
    pass


def diagnose(authenticated, packet_path):
    import pyarrow.parquet as pq
    from trading_research.operations.artifacts import canonical_json, publish_new
    from trading_research.research import auction_flow_profile_reference as profile
    from trading_research.research import auction_flow_profile_statistics as stats
    from trading_research.research.auction_flow_storage import BoundedOutputs
    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    operational, contract, population, windows, population_ref = base.profile_statistics_inputs(authenticated)
    diagnosis = operational['memory_diagnostic']
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs',
        maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'],
        maximum_file_bytes=32 * 1024**2)
    events = []
    began = time.process_time()
    def memory(phase, **extra):
        proc = {}
        for line in Path('/proc/self/status').read_text().splitlines():
            if line.startswith(('VmRSS:', 'VmSize:', 'VmData:', 'VmPeak:')):
                fields = line.split()
                proc[fields[0][:-1] + '_bytes'] = int(fields[1]) * 1024
        event = dict(phase=phase, cpu_seconds=time.process_time() - began, **proc, **extra)
        events.append(event)
        print(canonical_json(event).decode(), flush=True)
    def stop(signum, frame):
        raise DiagnosticStop('prespecified300CPU diagnostic endpoint')
    previous = signal.signal(signal.SIGPROF, stop)
    complete = False
    failure = None
    acc = stats.new_partition_accumulators()
    cache = profile.WindowUnitCache(windows['units'])
    def accumulator_size():
        stores = [v for branch in ('groups', 'paired') for group in acc[branch].values() for v in group.values()]
        return {'metric_stores': len(stores),
                'raw_value_bytes': sum(v.raw.itemsize * len(v.raw) for v in stores),
                'raw_values': sum(len(v.raw) for v in stores),
                'date_entries': sum(len(v.date_count) for v in stores),
                'index_entries': {k: len(v) for k, v in acc.items()}}
    try:
        signal.setitimer(signal.ITIMER_PROF, diagnosis['prespecified_stop_cpu_seconds'])
        memory('authenticated_populations')
        selected = [u for u in population['units'] if u.get('root') == 'NQ'
            and u.get('source_path') == diagnosis['input_path']
            and u.get('source_window_start_ns') == diagnosis['input_start_ns']]
        if len(selected) != 1:
            raise ValueError('diagnostic input identity is not unique')
        unit = selected[0]
        measurement_ref = profile.measurement_reference(unit)
        memory('before_measurement_decode', input=measurement_ref)
        extracted = profile.load_measurement_cells(unit)
        memory('after_measurement_extract', atoms=len(extracted['atoms']))
        del extracted
        gc.collect()
        memory('after_measurement_release')
        choices = [u for u in windows['units'] if (u.get('source_identity') or {}).get('source_path') == diagnosis['input_path']
            and (u.get('source_identity') or {}).get('acquired_event_start_ns') == diagnosis['input_start_ns']]
        if len(choices) != 1:
            raise ValueError('diagnostic window identity is not unique')
        cache._load(choices[0])
        memory('window_cache_loaded', buckets=len(cache.index), **cache.stats)
        for ref in diagnosis['retained_outputs']:
            name = Path(ref['path']).name
            if '-cells-' in name:
                continue
            raw, _ = base.checked(ref['path'], ref['sha256'], maximum=512 * 1024**2)
            if len(raw) != ref['size_bytes']:
                raise ValueError('retained diagnostic output size changed')
            del raw
            consumer = stats.accumulate_geometry_row if '-geometry-' in name else stats.accumulate_join_row
            rows = 0
            for batch in pq.ParquetFile(ref['path']).iter_batches(batch_size=2048):
                values = batch.to_pylist()
                for row in values:
                    consumer(acc, row, collection='weekly_acquisitions', year=2021)
                rows += len(values)
                del values
            memory('retained_rows_accumulated', file=name, rows=rows, **accumulator_size())
        complete = True
    except (DiagnosticStop, MemoryError) as exc:
        failure = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
    finally:
        signal.setitimer(signal.ITIMER_PROF, 0)
        signal.signal(signal.SIGPROF, previous)
    summary = accumulator_size()
    del acc, cache
    gc.collect()
    memory('released_diagnostic_state')
    ref = outputs.json('memory-diagnostic.json', {
        'kind': 'profile_failed68_component_memory_diagnostic_v1', 'completed': complete,
        'failure': failure, 'events': events, 'accumulator_summary': summary,
        'original_failure': diagnosis['failed_execution'], 'diagnostic_inputs': diagnosis,
        'scope': 'Component allocation diagnosis only; no scientific population acceptance.',
        'tests_reused': 57, 'unchanged_consumer_files': operational['accepted_consumer_files'],
    }, kind='profile_failed68_component_memory_diagnostic_v1')
    report = {k: packet[k] for k in ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration')}
    report.update(family=protocol['family'], mode='profile-statistics', success=True,
        diagnostic_only=True, memory_diagnostic=ref, derived_output_bytes=outputs.written,
        scope='Unchanged component allocation diagnosis; no population or full gate acceptance.')
    publish_new(Path(packet['worker_report']), canonical_json(report) + b'\n')
    return 0


base.profile_statistics = diagnose
if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(base.worker(sys.argv[2]))
    if len(sys.argv) != 1:
        raise SystemExit('no arguments, or registered --worker packet')
    raise SystemExit(base.parent('profile-statistics'))
