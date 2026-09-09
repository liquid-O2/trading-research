"""Register, build and validate the European/American numerical prerequisite."""
from dataclasses import asdict
from datetime import datetime, timezone
import ast
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'validation/OPTIONS_VALUATION_NUMERICS_EXECUTION_V1.json'
RUNS = ROOT / 'reports/options-valuation-numerics-runs'
NATIVE = 'src/trading_research/research/options_valuation_native.cpp'


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def checked(path, sha=None, maximum=32 * 1024**2):
    path = Path(path)
    if not path.is_file() or 'archive' in path.parts or path.stat().st_size > maximum:
        raise ValueError('bounded registered input required')
    raw = path.read_bytes()
    if sha is not None and hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError('registered input changed: ' + str(path))
    return raw


def closure():
    pending = ['src/trading_research/research/options_valuation_numerics.py',
               'tests/test_options_valuation_numerics.py']
    seen = {NATIVE, 'tools/auction_flow_parallel.py', 'tools/run_options_valuation_numerics.py'}
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        for node in ast.walk(ast.parse(checked(ROOT / name))):
            modules = ([node.module] if isinstance(node, ast.ImportFrom) and node.module else
                       [item.name for item in node.names] if isinstance(node, ast.Import) else [])
            for module in modules:
                if module.startswith('trading_research'):
                    relative = 'src/' + module.replace('.', '/') + '.py'
                    if (ROOT / relative).is_file() and relative not in seen:
                        pending.append(relative)
    return {name: hashlib.sha256(checked(ROOT / name)).hexdigest() for name in sorted(seen)}


def load_helper(configuration):
    path = ROOT / 'tools/auction_flow_parallel.py'
    checked(path, configuration['files']['tools/auction_flow_parallel.py'])
    spec = importlib.util.spec_from_file_location('valuation_supervision', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def worker(packet_path):
    packet = json.loads(checked(packet_path))
    protocol = json.loads(checked(PROTOCOL, packet['configuration']['protocol_sha256']))
    cap = protocol['resources']
    resource.setrlimit(resource.RLIMIT_CPU, (cap['cpu_seconds'], cap['hard_cpu_seconds']))
    resource.setrlimit(resource.RLIMIT_AS, (cap['address_space_bytes'], cap['address_space_bytes']))
    resource.setrlimit(resource.RLIMIT_FSIZE, (cap['file_bytes'], cap['file_bytes']))
    def interrupt(signum, frame):
        raise RuntimeError('registered numerical worker interrupted: ' + str(signum))
    for signum in (signal.SIGTERM, signal.SIGINT, signal.SIGXCPU):
        signal.signal(signum, interrupt)
    sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
    from trading_research.operations.artifacts import publish_new
    from trading_research.operations.trials import TrialRegistry
    registry = TrialRegistry(ROOT / 'evidence/trials')
    state = registry.state()
    attempt = state['attempts'][packet['attempt_id']]
    trial = state['trials'][packet['trial_id']]
    cfg = packet['configuration']
    if (attempt['status'] != 'running' or attempt['trial_id'] != packet['trial_id']
            or attempt['family'] != protocol['family'] or trial['configuration'] != cfg
            or trial['code_hash'] != packet['snapshot']['sha256']
            or os.getppid() != packet['supervisor_pid']
            or Path(packet_path).resolve() != RUNS / packet['attempt_id'] / 'packet.json'):
        raise ValueError('worker does not identify its registered attempt')
    for path, sha in cfg['files'].items():
        checked(ROOT / path, sha)
    for name, value in cfg['thread_limits'].items():
        if os.environ.get(name) != value:
            raise ValueError('registered thread limits changed')
    checked(cfg['numerical_contract']['path'], cfg['numerical_contract']['sha256'])
    out = Path(packet_path).parent
    binary = out / 'liboptions_valuation_native.so'
    command = [*protocol['build_flags'], str(ROOT / NATIVE), '-o', str(binary)]
    # Compiler and descendants are reaped before reducing the worker's remaining
    # self CPU limit, so compilation and checks share one charged reservation.
    with (out / 'build.log').open('xb') as log:
        subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                       check=True, timeout=cap['build_wall_seconds'])
    helper = load_helper(cfg)
    helper.apply_remaining_coordinator_cpu_limit(cap['cpu_seconds'], cap['hard_cpu_seconds'])
    binary_raw = checked(binary, maximum=cap['file_bytes'])
    binary_ref = asdict(registry.artifacts.put_bytes(binary_raw, kind='options_valuation_native_binary_v1'))
    os.environ['TR_OPTIONS_VALUATION_NATIVE_PATH'] = str(binary)
    os.environ['TR_OPTIONS_VALUATION_NATIVE_SHA256'] = binary_ref['sha256']
    import unittest
    spec = importlib.util.spec_from_file_location('test_options_valuation_numerics',
                                                ROOT / 'tests/test_options_valuation_numerics.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    began = time.process_time()
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2, failfast=True).run(
        unittest.defaultTestLoader.loadTestsFromModule(module))
    report = {'kind': 'options_valuation_numerics_worker_v1', 'success': result.wasSuccessful(),
              'attempt_id': packet['attempt_id'], 'trial_id': packet['trial_id'],
              'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
              'test_cpu_seconds': time.process_time() - began, 'binary': binary_ref,
              'build_command': command, 'build_cpu_seconds': helper.rusage_children_cpu_seconds(),
              'compiler_version': subprocess.run([protocol['build_flags'][0], '--version'],
                  capture_output=True, text=True, check=True, timeout=5).stdout,
              'snapshot': packet['snapshot'], 'configuration': cfg,
              'full_population_complete': False, 'source_rows_read': 0,
              'cas_output_bytes': binary_ref['size_bytes']}
    publish_new(out / 'worker.json', encoded(report))
    return 0 if result.wasSuccessful() else 1


def parent():
    sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
    from trading_research.operations.artifacts import code_snapshot, publish_new
    from trading_research.operations.trials import TrialRegistry
    raw = checked(PROTOCOL)
    protocol = json.loads(raw)
    cap = protocol['resources']
    registry = TrialRegistry(ROOT / 'evidence/trials')
    store = registry.artifacts
    protocol_ref = asdict(store.put_bytes(raw, kind=protocol['kind']))
    registry.register_family(protocol['family'], scope_ids=tuple(protocol['scope_ids']),
        protocol=protocol_ref, max_attempts=cap['max_attempts'], cpu_budget_seconds=cap['cpu_budget_seconds'])
    previous = [a for a in registry.state()['attempts'].values() if a['family'] == protocol['family']]
    physical_used = sum(p.stat().st_size for p in RUNS.rglob('*') if p.is_file()) if RUNS.exists() else 0
    if physical_used + (len(previous) + 1) * cap['file_bytes'] + cap['output_bytes'] > cap['study_output_bytes']:
        raise ValueError('numerical study output allowance exhausted')
    numerical_path = ROOT / 'validation/OPTIONS_VALUATION_NUMERICS_V1.json'
    numerical_raw = checked(numerical_path)
    cfg = {'files': closure(), 'protocol_sha256': hashlib.sha256(raw).hexdigest(),
           'numerical_contract': {'path': str(numerical_path),
               'sha256': hashlib.sha256(numerical_raw).hexdigest(), 'size_bytes': len(numerical_raw)},
           'numerical_contract_snapshot': asdict(store.put_bytes(numerical_raw, kind='options_valuation_numerics_contract_v1')),
           'runner_source': asdict(store.put_bytes(checked(__file__), kind='options_valuation_numerics_runner_source_v1')),
           'thread_limits': {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
                             'ARROW_NUM_THREADS': '1', 'PYTHONHASHSEED': '0'}}
    snapshot = code_snapshot(ROOT, store)
    trial = registry.register(name='options-valuation-numerics', family=protocol['family'], stage='engineering',
        configuration=cfg, code_hash=snapshot.sha256, data_hashes={'protocol': cfg['protocol_sha256']},
        fold_version='deterministic-independent-numerical-fixtures-v1', target_version='options-valuation-numerics-v1')
    attempt = registry.start(trial, cpu_reservation_seconds=cap['hard_cpu_seconds'])
    out = RUNS / attempt
    out.mkdir(parents=True, exist_ok=False)
    packet = {'attempt_id': attempt, 'trial_id': trial, 'snapshot': asdict(snapshot),
              'configuration': cfg, 'supervisor_pid': os.getpid()}
    publish_new(out / 'packet.json', encoded(packet))
    helper = load_helper(cfg)
    started = time.monotonic()
    process = usage = None
    finished = False
    cleanup = {'cpu_accounting_complete': True}
    try:
        with (out / 'worker.log').open('xb') as log:
            process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker', str(out / 'packet.json')],
                cwd=ROOT, env={**os.environ, **cfg['thread_limits']}, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=True)
            while True:
                pid, status, received = os.wait4(process.pid, os.WNOHANG)
                if pid:
                    usage = received
                    process.returncode = os.waitstatus_to_exitcode(status)
                    cleanup = helper.cleanup_reaped_coordinator_group(process.pid)
                    break
                if time.monotonic() - started > cap['wall_seconds']:
                    cleanup = helper.terminate_then_kill_group(process.pid)
                    usage, process.returncode = cleanup['usage'], cleanup['exit_code']
                    break
                time.sleep(0.2)
        cpu = helper.conservative_attempt_cpu_seconds(wait4_usage=usage,
            accounting_complete=cleanup['cpu_accounting_complete'], hard_cpu_seconds=cap['hard_cpu_seconds'])
        peak = None if usage is None else usage.ru_maxrss * 1024
        elapsed = time.monotonic() - started
        w = json.loads(checked(out / 'worker.json')) if (out / 'worker.json').exists() else None
        wr = asdict(store.put_json(w, kind=w['kind'])) if w else None
        physical = sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
        physical += (w['cas_output_bytes'] + wr['size_bytes']) if w else cap['file_bytes']
        success = bool(process.returncode == 0 and w and w['success']
            and w['attempt_id'] == attempt and w['trial_id'] == trial and w['snapshot'] == asdict(snapshot)
            and cleanup['cpu_accounting_complete'] and cpu <= cap['cpu_seconds']
            and peak is not None and peak <= cap['address_space_bytes']
            and elapsed <= cap['wall_seconds'] and physical <= cap['output_bytes'])
        report = {'kind': 'options_valuation_numerics_execution_v1', 'family': protocol['family'],
            'success': success, 'attempt_id': attempt, 'trial_id': trial, 'worker': wr,
            'protocol': protocol_ref, 'snapshot': asdict(snapshot), 'configuration': cfg,
            'cpu_seconds': cpu, 'peak_rss_bytes': peak, 'wall_seconds': elapsed, 'output_bytes': physical,
            'exit_code': process.returncode, 'cleanup': {k: v for k, v in cleanup.items() if k != 'usage'},
            'finished_at': datetime.now(timezone.utc).isoformat(), 'full_population_complete': False}
        ref = asdict(store.put_json(report, kind=report['kind']))
        registry.finish(attempt, status='succeeded' if success else 'failed', cpu_seconds=cpu,
            wall_seconds=elapsed, peak_rss_bytes=peak, reason='numerical prerequisite; every failure retained',
            result_artifacts=(ref,))
        finished = True
        publish_new(out / 'execution.json', encoded(report))
        print(json.dumps({'report': str(out / 'execution.json'), 'success': success, 'cpu_seconds': cpu}), flush=True)
        return 0 if success else 1
    finally:
        if not finished:
            if process is not None and process.returncode is None:
                cleanup = helper.terminate_then_kill_group(process.pid)
                usage, process.returncode = cleanup['usage'], cleanup['exit_code']
            cpu = 0 if process is None else helper.conservative_attempt_cpu_seconds(
                wait4_usage=usage, accounting_complete=cleanup['cpu_accounting_complete'],
                hard_cpu_seconds=cap['hard_cpu_seconds'])
            registry.finish(attempt, status='interrupted', cpu_seconds=cpu,
                wall_seconds=time.monotonic() - started, peak_rss_bytes=None,
                reason='numerical supervisor failure; bounded reservation charged if accounting uncertain')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(worker(sys.argv[2]))
    if len(sys.argv) != 1:
        raise SystemExit('usage: run_options_valuation_numerics.py')
    raise SystemExit(parent())
