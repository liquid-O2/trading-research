"""Register and supervise the auction/flow source check before candidate imports.

This distinct scientific family retains its initial resource limits and every
attempt. The full package is snapshotted; reusable verification records the
exact source/measurement/test dependency closure separately.
"""
from dataclasses import asdict
from datetime import datetime, timezone
import ast
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'validation/AUCTION_FLOW_STUDY_V1.json'
CHECK_EXTENSION = ROOT / 'validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V3.json'
RUNS = ROOT / 'reports/auction-flow-runs'
THREADS = {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
           'ARROW_NUM_THREADS': '1', 'NUMEXPR_NUM_THREADS': '1'}


def checked(path, expected=None, *, maximum=16 * 1024**2):
    path = Path(path).resolve()
    if 'archive' in path.parts or not path.is_file() or path.stat().st_size > maximum:
        raise ValueError('bounded retained input required')
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if expected is not None and expected != sha:
        raise ValueError(f'frozen input changed: {path}')
    return raw, sha


def load_reference(reference):
    raw, _ = checked(reference['path'], reference['sha256'])
    if len(raw) != reference['size_bytes']:
        raise ValueError('retained reference size changed')
    return json.loads(raw)


def dependency_contract(manifest, protocol):
    """Exact local static-import closure; unrelated package files stay snapshotted."""
    modules, by_path = {}, {}
    for name in manifest:
        if not name.endswith('.py'):
            continue
        module = (name[4:] if name.startswith('src/') else name)[:-3].replace('/', '.')
        if module.endswith('.__init__'):
            module = module[:-9]
        modules[module], by_path[name] = name, module
    extension_raw, extension_sha = checked(CHECK_EXTENSION)
    extension = json.loads(extension_raw)
    additional = extension['additional_check_modules']
    if (not isinstance(additional, list) or not additional or len(set(additional)) != len(additional)
            or any(not name.startswith('tests.test_auction_flow_') or name in protocol['check_modules'] for name in additional)):
        raise ValueError('explicit additive within-family check modules required')
    supplements = extension['scientific_supplements']
    for reference in supplements:
        raw, _ = checked(reference['path'], reference['sha256'])
        if len(raw) != reference['size_bytes']:
            raise ValueError('frozen anchor science supplement size changed')
    roots = ['src/trading_research/research/auction_flow_pipeline.py',
             'src/trading_research/research/auction_flow_storage.py',
             'src/trading_research/research/auction_flow_preflight.py']
    roots.extend('tests/' + name.rsplit('.', 1)[1] + '.py' for name in protocol['check_modules'] + additional)
    frozen_references = extension.get('frozen_test_references', [])
    for reference in frozen_references:
        path = Path(reference['path']).resolve()
        raw, _ = checked(path, reference['sha256'])
        if len(raw) != reference['size_bytes'] or not path.is_relative_to(ROOT / 'references'):
            raise ValueError('frozen independent comparison reference changed')
        if path.suffix == '.py':
            roots.append(str(path.relative_to(ROOT)))
    pending, found = list(roots), set()
    while pending:
        name = pending.pop()
        if name in found:
            continue
        if name not in manifest:
            raise ValueError(f'verification dependency is absent: {name}')
        found.add(name)
        tree = ast.parse(checked(ROOT / name, manifest[name])[0], filename=name)
        current = by_path[name]
        package = current if name.endswith('/__init__.py') else current.rsplit('.', 1)[0]
        for node in ast.walk(tree):
            imports = []
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ''
                if node.level:
                    parent = package.split('.')[:len(package.split('.')) - node.level + 1]
                    base = '.'.join([*parent, *([base] if base else [])])
                imports.extend([base, *(base + '.' + alias.name for alias in node.names if alias.name != '*')])
            for module in imports:
                for depth in range(1, len(module.split('.')) + 1):
                    local = modules.get('.'.join(module.split('.')[:depth]))
                    if local is not None and local not in found:
                        pending.append(local)
    dependencies = {name: manifest[name] for name in sorted(found)}
    dependencies.update({name: manifest[name] for name in ('pyproject.toml', 'uv.lock')})
    return {'kind': 'auction_flow_source_component_verification_v3', 'dependencies': dependencies,
            'check_extension': {'path': str(CHECK_EXTENSION), 'sha256': extension_sha, 'size_bytes': len(extension_raw),
                                'kind': extension['kind']},
            'scientific_supplements': supplements, 'additional_check_modules': additional,
            'frozen_test_references': frozen_references,
            'runtime_versions': protocol['runtime_versions'], 'python_version': protocol['python_version'],
            'inputs_and_science': protocol['frozen_metadata'], 'source_index': protocol['source_index'],
            'raw_variant_policy': protocol['source_overlap_policy'],
            'native_width_ns': protocol['native_width_ns'], 'atomic_width_ns': protocol['atomic_width_ns'],
            'actual_reference_maximum_raw_rows_per_variant': protocol['actual_reference_maximum_raw_rows_per_variant']}


def limits(protocol):
    resource_spec = protocol['resources']
    cpu = resource_spec['phase_cpu_seconds']['check']
    return {'cpu_seconds': cpu, 'hard_cpu_seconds': cpu + resource_spec['hard_cpu_margin_seconds'],
        'memory_bytes': resource_spec['memory_bytes'], 'maximum_output_file_bytes': resource_spec['maximum_output_file_bytes'],
        'maximum_output_bytes': resource_spec['maximum_derived_output_bytes'],
        'supervisor_output_reserve_bytes': resource_spec['supervisor_output_reserve_bytes'],
        'wall_seconds': resource_spec['per_check_wall_seconds']}


def worker(packet_path):
    # Set fixed bootstrap ceilings before packet or candidate-dependent work.
    resource.setrlimit(resource.RLIMIT_CPU, (1210, 1210))
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (512 * 1024**2, 512 * 1024**2))
    packet = json.loads(checked(packet_path, maximum=2 * 1024**2)[0])
    protocol = json.loads(checked(PROTOCOL, packet['protocol_sha256'])[0])
    cap = limits(protocol)
    if packet['limits'] != cap:
        raise ValueError('registered source check resource limits changed')
    resource.setrlimit(resource.RLIMIT_CPU, (cap['cpu_seconds'], cap['hard_cpu_seconds']))
    resource.setrlimit(resource.RLIMIT_AS, (cap['memory_bytes'], cap['memory_bytes']))
    resource.setrlimit(resource.RLIMIT_FSIZE, (cap['maximum_output_file_bytes'], cap['maximum_output_file_bytes']))
    sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
    try:
        from trading_research.operations.artifacts import artifact_ref, canonical_json, publish_new
        from trading_research.operations.trials import TrialRegistry
        registry = TrialRegistry(ROOT / 'evidence/trials')
        state = registry.state()
        attempt, trial = state['attempts'][packet['attempt_id']], state['trials'][packet['trial_id']]
        if (attempt['status'] != 'running' or attempt['trial_id'] != packet['trial_id']
                or attempt['family'] != protocol['family'] or attempt['cpu_reservation_seconds'] != cap['hard_cpu_seconds']
                or trial['code_hash'] != packet['code_snapshot']['sha256']
                or trial['configuration'] != packet['configuration'] or os.getppid() != packet['supervisor_pid']
                or Path(packet_path).resolve() != RUNS / packet['attempt_id'] / 'packet.json'
                or Path(packet['worker_report']) != Path(packet_path).parent / 'worker.json'
                or state['effective_budgets'][protocol['family']] != {'max_attempts': protocol['resources']['maximum_attempts'],
                    'cpu_budget_seconds': protocol['resources']['cpu_budget_seconds']}):
            raise ValueError('worker lacks its actual running same-family attempt, snapshot, limits and supervisor')
        snapshot = registry.artifacts.read_json(artifact_ref(packet['code_snapshot']))
        manifest = snapshot['manifest']
        del snapshot
        script = registry.artifacts.read_json(artifact_ref(packet['tools_snapshot']))
        manifest.update({name: row['sha256'] for name, row in script.items()})
        if manifest != packet['code_manifest']:
            raise ValueError('packet source manifest differs from its reproducible snapshot')
        for name, sha in manifest.items():
            checked(ROOT / name, sha)
        for reference in protocol['frozen_metadata']:
            raw, _ = checked(reference['path'], reference['sha256'])
            if len(raw) != reference['size_bytes']:
                raise ValueError('frozen source/scientific metadata size changed')
        versions = {name: importlib.metadata.version(name) for name in protocol['runtime_versions']}
        if (versions != protocol['runtime_versions'] or sys.version != protocol['python_version']
                or any(os.environ.get(name) != value for name, value in THREADS.items())):
            raise ValueError('frozen runtime or one-thread scenario changed')
        contract = dependency_contract(manifest, protocol)
        if contract != packet['configuration']['verified_component']:
            raise ValueError('source component no longer has its exact relevant dependency closure')
        extension = load_reference(packet['configuration']['check_extension'])
        if (extension['parent_protocol_sha256'] != packet['protocol_sha256']
                or extension['registered_family'] != protocol['family']
                or extension['registered_resources_changed'] is not False):
            raise ValueError('source continuation check changed the registered family or its resources')
        saved_extension = registry.artifacts.read(artifact_ref(packet['configuration']['check_extension_snapshot']))
        if saved_extension != checked(CHECK_EXTENSION, packet['configuration']['check_extension']['sha256'])[0]:
            raise ValueError('source continuation check is not fully preserved in its registered snapshot')
        for reference, saved in zip(extension['scientific_supplements'], packet['configuration']['scientific_supplement_snapshots'], strict=True):
            original, _ = checked(reference['path'], reference['sha256'])
            if len(original) != reference['size_bytes'] or registry.artifacts.read(artifact_ref(saved)) != original:
                raise ValueError('anchor scientific supplement differs from its preserved registered snapshot')
        for reference, saved in zip(extension.get('frozen_test_references', []),
                                    packet['configuration']['frozen_test_reference_snapshots'], strict=True):
            original, _ = checked(reference['path'], reference['sha256'])
            if len(original) != reference['size_bytes'] or registry.artifacts.read(artifact_ref(saved)) != original:
                raise ValueError('independent comparison reference differs from its preserved registered snapshot')
        from trading_research.research.auction_flow_anchors import CONTRACT_SHA256, DETAIL_SHA256
        if [r['sha256'] for r in extension['scientific_supplements']] != [CONTRACT_SHA256, DETAIL_SHA256]:
            raise ValueError('implemented anchor records are not bound to the exact declared mechanisms')
        import unittest
        suite = unittest.TestSuite()
        for name in protocol['check_modules'] + extension['additional_check_modules']:
            module = importlib.import_module(name)
            for value in vars(module).values():
                if isinstance(value, type) and issubclass(value, unittest.TestCase) and value.__module__ == name:
                    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(value))
        test_start = time.process_time()
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        test_report = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
                       'success': result.wasSuccessful(), 'cpu_seconds': time.process_time() - test_start}
        preflight = None
        from trading_research.research.auction_flow_storage import BoundedOutputs
        outputs = BoundedOutputs(Path(packet_path).parent / 'outputs',
            maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'],
            maximum_file_bytes=cap['maximum_output_file_bytes'])
        if result.wasSuccessful():
            from trading_research.research.auction_flow_preflight import run_preflight, REFERENCE_ROWS, NATIVE_WIDTH_NS
            if (REFERENCE_ROWS != protocol['actual_reference_maximum_raw_rows_per_variant']
                    or NATIVE_WIDTH_NS != protocol['native_width_ns']):
                raise ValueError('declared actual reference/native grid differs from the implementation')
            preflight = run_preflight(protocol=protocol, root=ROOT, outputs=outputs, load_reference=load_reference,
                                      check_extension=extension)
        report = {'family': protocol['family'], 'mode': 'check', 'attempt_id': packet['attempt_id'],
            'trial_id': packet['trial_id'], 'protocol_sha256': packet['protocol_sha256'],
            'code_snapshot': packet['code_snapshot'], 'tools_snapshot': packet['tools_snapshot'],
            'configuration': packet['configuration'], 'tests': test_report, 'actual_source_preflight': preflight,
            'derived_output_bytes': outputs.written, 'source_component_verified': bool(preflight and preflight['passed']),
            'runtime_versions': versions,
            'success': bool(result.wasSuccessful() and preflight and preflight['passed'])}
        payload = canonical_json(report) + b'\n'
        if len(payload) > cap['supervisor_output_reserve_bytes'] // 4:
            raise ValueError('worker summary exceeds its explicitly reserved publication bytes')
        publish_new(Path(packet['worker_report']), payload)
        return 0 if report['success'] else 1
    except BaseException:
        traceback.print_exc()
        return 1


def parent():
    sys.path.insert(0, str(ROOT / 'src'))
    from trading_research.operations.artifacts import artifact_ref, canonical_json, code_snapshot, publish_new
    from trading_research.operations.trials import TrialRegistry
    protocol_raw, protocol_sha = checked(PROTOCOL)
    protocol = json.loads(protocol_raw)
    cap = limits(protocol)
    registry = TrialRegistry(ROOT / 'evidence/trials')
    store = registry.artifacts
    protocol_ref = store.put_bytes(protocol_raw, kind='auction_flow_scientific_protocol_v1')
    supporting = []
    for reference in protocol['frozen_metadata']:
        raw, _ = checked(reference['path'], reference['sha256'])
        if len(raw) != reference['size_bytes']:
            raise ValueError('source/scientific reference bytes changed before registration')
        supporting.append(asdict(store.put_bytes(raw, kind=reference['kind'])))
    registry.register_family(protocol['family'], scope_ids=tuple(protocol['independent_scope_ids']),
        protocol={'protocol': asdict(protocol_ref), 'frozen_metadata': supporting,
                  'active_scope': protocol['active_scope'], 'question': protocol['question']},
        max_attempts=protocol['resources']['maximum_attempts'], cpu_budget_seconds=protocol['resources']['cpu_budget_seconds'])
    state = registry.state()
    previous_bytes = 0
    for attempt in state['attempts'].values():
        if attempt['family'] != protocol['family']:
            continue
        if attempt['status'] == 'running':
            raise ValueError('a source-family attempt is already running')
        reports = [r for r in attempt.get('result_artifacts', ()) if r['kind'] == 'auction_flow_execution']
        if reports:
            previous_bytes += store.read_json(artifact_ref(reports[-1]))['attempt_output_bytes']
        else:
            # A prior interrupted parent may leave files without a result;
            # retaining and charging them is required before another attempt.
            previous_bytes += sum(p.stat().st_size for p in (RUNS / attempt['id']).rglob('*') if p.is_file())
    if previous_bytes + cap['maximum_output_bytes'] > protocol['resources']['maximum_study_output_bytes']:
        raise ValueError('remaining study output allowance cannot reserve this complete bounded attempt')
    snapshot = code_snapshot(ROOT, store)
    manifest = store.read_json(snapshot)['manifest']
    tool_name = 'tools/run_auction_flow_study.py'
    script, script_sha = checked(ROOT / tool_name)
    tools_ref = store.put_json({tool_name: {'sha256': script_sha, 'content_hex': script.hex()}}, kind='auction_flow_tools_snapshot')
    manifest[tool_name] = script_sha
    extension_raw, extension_sha = checked(CHECK_EXTENSION)
    extension = json.loads(extension_raw)
    extension_snapshot = store.put_bytes(extension_raw, kind=extension['kind'])
    supplement_snapshots = []
    for reference in extension['scientific_supplements']:
        raw, _ = checked(reference['path'], reference['sha256'])
        if len(raw) != reference['size_bytes']:
            raise ValueError('anchor supplement changed before registration')
        supplement_snapshots.append(asdict(store.put_bytes(raw, kind=reference['kind'])))
    frozen_test_reference_snapshots = []
    for reference in extension.get('frozen_test_references', []):
        raw, _ = checked(reference['path'], reference['sha256'])
        if len(raw) != reference['size_bytes']:
            raise ValueError('independent comparison reference changed before registration')
        frozen_test_reference_snapshots.append(asdict(store.put_bytes(raw, kind=reference['kind'])))
    configuration = {'mode': 'check', 'protocol_sha256': protocol_sha, 'tools_snapshot': asdict(tools_ref),
        'verified_component': dependency_contract(manifest, protocol), 'thread_limits': THREADS,
        'check_extension': {'path': str(CHECK_EXTENSION), 'sha256': extension_sha, 'size_bytes': len(extension_raw),
                            'kind': extension['kind']},
        'check_extension_snapshot': asdict(extension_snapshot),
        'scientific_supplement_snapshots': supplement_snapshots,
        'frozen_test_reference_snapshots': frozen_test_reference_snapshots,
        'python_executable': sys.executable, 'limits': cap, 'previous_study_output_bytes': previous_bytes}
    trial = registry.register(name='Acquired auction/flow: consolidated source and full-window resource check',
        family=protocol['family'], stage='engineering', configuration=configuration, code_hash=snapshot.sha256,
        data_hashes={'protocol': protocol_sha, 'source_index': protocol['source_index']['sha256']},
        fold_version='NQ-2020-2022-train-2023-dev-2024-calibration-2025plus-confirm_ES-discontinuous-v1',
        target_version='reported-side-auction-quote-and-participation-source-path-v1')
    attempt_id = registry.start(trial, cpu_reservation_seconds=cap['hard_cpu_seconds'])
    destination = RUNS / attempt_id
    packet = {'attempt_id': attempt_id, 'trial_id': trial, 'protocol_sha256': protocol_sha,
        'code_snapshot': asdict(snapshot), 'tools_snapshot': asdict(tools_ref), 'code_manifest': manifest,
        'configuration': configuration, 'limits': cap, 'supervisor_pid': os.getpid(),
        'worker_report': str(destination / 'worker.json')}
    started, process, observed, finalized, timed_out = time.monotonic(), None, None, False, False
    try:
        destination.mkdir(parents=True, exist_ok=False)
        publish_new(destination / 'packet.json', canonical_json(packet) + b'\n')
        with (destination / 'worker.log').open('xb') as log:
            process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker', str(destination / 'packet.json')],
                cwd=ROOT, env={**os.environ, **THREADS, 'PYTHONHASHSEED': '0'}, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            while True:
                pid, status, usage = os.wait4(process.pid, os.WNOHANG)
                if pid:
                    observed, process.returncode = usage, os.waitstatus_to_exitcode(status)
                    break
                if time.monotonic() - started > cap['wall_seconds']:
                    timed_out = True
                    os.killpg(process.pid, signal.SIGKILL)
                    _, status, observed = os.wait4(process.pid, 0)
                    process.returncode = os.waitstatus_to_exitcode(status)
                    break
                time.sleep(0.2)
        worker_path = destination / 'worker.json'
        value = json.loads(checked(worker_path)[0]) if worker_path.is_file() else None
        joined = value is not None and all(value.get(k) == packet[k] for k in
            ('trial_id', 'attempt_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration'))
        output_bytes = sum(p.stat().st_size for p in destination.rglob('*') if p.is_file())
        elapsed = time.monotonic() - started
        cpu, peak = observed.ru_utime + observed.ru_stime, observed.ru_maxrss * 1024
        within = cpu <= cap['cpu_seconds'] and peak <= cap['memory_bytes'] and elapsed <= cap['wall_seconds'] and not timed_out
        log_ref = store.put_bytes(checked(destination / 'worker.log')[0], kind='auction_flow_worker_log')
        worker_ref = None if value is None else store.put_json(value, kind='auction_flow_worker_report')
        output_bytes += log_ref.size_bytes + (0 if worker_ref is None else worker_ref.size_bytes)
        report = {'family': protocol['family'], 'mode': 'check', 'trial_id': trial, 'attempt_id': attempt_id,
            'protocol_sha256': protocol_sha, 'code_snapshot': asdict(snapshot), 'tools_snapshot': asdict(tools_ref),
            'configuration': configuration, 'worker_report': None if worker_ref is None else asdict(worker_ref),
            'worker_report_path': str(worker_path), 'worker_log': asdict(log_ref),
            'exit_code': process.returncode, 'wall_timeout': timed_out, 'worker_identity_joined': joined,
            'cpu_seconds': cpu, 'wall_seconds': elapsed, 'peak_rss_bytes': peak,
            'within_declared_limits': within, 'resource_basis': 'wait4_specific_worker_and_descendants',
            'success': bool(process.returncode == 0 and joined and within and value.get('success') is True),
            'attempt_output_bytes': output_bytes, 'finished_at': datetime.now(timezone.utc).isoformat()}
        # Count both the disk execution receipt and its canonical CAS copy.
        base = output_bytes
        for _ in range(16):
            total = base + 2 * len(canonical_json(report)) + 1
            if report['attempt_output_bytes'] == total:
                break
            report['attempt_output_bytes'] = total
        else:
            raise ValueError('execution-output byte accounting did not converge')
        if report['attempt_output_bytes'] > cap['maximum_output_bytes']:
            report['success'] = report['within_declared_limits'] = False
        report_ref = store.put_json(report, kind='auction_flow_execution')
        registry.finish(attempt_id, status='succeeded' if report['success'] else 'failed',
            cpu_seconds=cpu, wall_seconds=elapsed, peak_rss_bytes=peak,
            reason='Complete bounded source check and full-window measurements' if report['success'] else 'Bounded source check failed; log and all partial outputs retained',
            result_artifacts=(asdict(report_ref),))
        finalized = True
        publish_new(destination / 'execution.json', canonical_json(report) + b'\n')
        print(json.dumps({'report': str(destination / 'execution.json'), 'success': report['success'],
            'cpu_seconds': cpu, 'peak_rss_bytes': peak, 'attempt_output_bytes': report['attempt_output_bytes']}), flush=True)
        return 0 if report['success'] else 1
    except BaseException as exc:
        if process is not None and process.returncode is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
                _, status, observed = os.wait4(process.pid, 0)
                process.returncode = os.waitstatus_to_exitcode(status)
            except (ProcessLookupError, ChildProcessError):
                pass
        if not finalized:
            registry.finish(attempt_id, status='interrupted',
                cpu_seconds=0.0 if process is None else None if observed is None else observed.ru_utime + observed.ru_stime,
                wall_seconds=time.monotonic() - started,
                peak_rss_bytes=0 if process is None else None if observed is None else observed.ru_maxrss * 1024,
                reason=f'source supervisor exception: {type(exc).__name__}; unknown consumption keeps its reservation')
        raise


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(worker(sys.argv[2]))
    if sys.argv[1:] != ['check']:
        raise SystemExit('usage: run_auction_flow_study.py check')
    raise SystemExit(parent())
