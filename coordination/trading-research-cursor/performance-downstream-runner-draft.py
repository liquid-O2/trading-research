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

try:
    from .auction_flow_parallel import (
        live_hardware_limits, plan_source_unit_execution, require_parent_identity,
        require_unit_identity, unit_identity, supervise_source_children,
        require_output_reservation, artifacts_allowance_after_packet,
        charge_child_output_bytes, actual_source_unit_allocation,
        require_source_unit_namespace, require_reference_in_namespace,
        require_joined_receipt, require_complete_ordinals, pool_wall_deadline,
        wait4_cpu_seconds, apply_remaining_coordinator_cpu_limit,
        terminate_then_kill_group, cleanup_reaped_coordinator_group, conservative_attempt_cpu_seconds,
        SourceWorkerInterrupt)
except ImportError:
    from auction_flow_parallel import (
        live_hardware_limits, plan_source_unit_execution, require_parent_identity,
        require_unit_identity, unit_identity, supervise_source_children,
        require_output_reservation, artifacts_allowance_after_packet,
        charge_child_output_bytes, actual_source_unit_allocation,
        require_source_unit_namespace, require_reference_in_namespace,
        require_joined_receipt, require_complete_ordinals, pool_wall_deadline,
        wait4_cpu_seconds, apply_remaining_coordinator_cpu_limit,
        terminate_then_kill_group, cleanup_reaped_coordinator_group, conservative_attempt_cpu_seconds,
        SourceWorkerInterrupt)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'validation/AUCTION_FLOW_STUDY_V1.json'
CHECK_EXTENSION = ROOT / 'validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V12.json'
HARDWARE_EXECUTION = ROOT / 'validation/AUCTION_FLOW_HARDWARE_EXECUTION_V1.json'
TOOL_FILES = ('tools/run_auction_flow_study.py', 'tools/auction_flow_parallel.py')
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


def load_reference(reference, *, maximum=16 * 1024**2):
    raw, _ = checked(reference['path'], reference['sha256'], maximum=maximum)
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
    roots.extend(TOOL_FILES)
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
    return {'kind': 'auction_flow_source_component_verification_v4', 'dependencies': dependencies,
            'check_extension': {'path': str(CHECK_EXTENSION), 'sha256': extension_sha, 'size_bytes': len(extension_raw),
                                'kind': extension['kind']},
            'scientific_supplements': supplements, 'additional_check_modules': additional,
            'frozen_test_references': frozen_references,
            'retained_validation_inputs': extension.get('retained_validation_inputs', []),
            'runtime_versions': {**protocol['runtime_versions'], **extension.get('additional_runtime_versions', {})}, 'python_version': protocol['python_version'],
            'inputs_and_science': protocol['frozen_metadata'], 'source_index': protocol['source_index'],
            'raw_variant_policy': protocol['source_overlap_policy'],
            'native_width_ns': protocol['native_width_ns'], 'atomic_width_ns': protocol['atomic_width_ns'],
            'actual_reference_maximum_raw_rows_per_variant': protocol['actual_reference_maximum_raw_rows_per_variant']}


def limits(protocol, mode='check'):
    resource_spec = protocol['resources']
    cpu = resource_spec['phase_cpu_seconds']['check']
    cap = {'cpu_seconds': cpu, 'hard_cpu_seconds': cpu + resource_spec['hard_cpu_margin_seconds'],
        'memory_bytes': resource_spec['memory_bytes'], 'maximum_output_file_bytes': resource_spec['maximum_output_file_bytes'],
        'maximum_output_bytes': resource_spec['maximum_derived_output_bytes'],
        'supervisor_output_reserve_bytes': resource_spec['supervisor_output_reserve_bytes'],
        'wall_seconds': resource_spec['per_check_wall_seconds']}
    if mode in ('profile', 'compute'):
        cap.update(cpu_seconds=180, hard_cpu_seconds=190, wall_seconds=300,
                   maximum_output_bytes=512 * 1024**2, maximum_output_file_bytes=128 * 1024**2)
    elif mode in ('benchmark', 'downstream'):
        cap.update(cpu_seconds=600, hard_cpu_seconds=610, wall_seconds=900,
                   maximum_output_bytes=1024**3, maximum_output_file_bytes=128 * 1024**2)
    elif mode != 'check':
        raise ValueError('unknown registered source workload')
    return cap


def bootstrap_process_limits():
    resource.setrlimit(resource.RLIMIT_CPU, (1210, 1210))
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))
    resource.setrlimit(resource.RLIMIT_FSIZE, (512 * 1024**2, 512 * 1024**2))


def hardware_specification_path(reference):
    path = Path(reference['path'])
    return path if path.is_absolute() else (ROOT / path).resolve()


def join_hardware_execution(protocol, protocol_sha256, reference=None):
    path = HARDWARE_EXECUTION if reference is None else Path(reference['path'])
    if path.resolve() != HARDWARE_EXECUTION.resolve():
        raise ValueError('hardware execution path is not the registered instruction')
    raw, sha = checked(HARDWARE_EXECUTION, None if reference is None else reference['sha256'], maximum=128 * 1024)
    if reference is not None and (sha != reference['sha256'] or len(raw) != reference['size_bytes']):
        raise ValueError('hardware execution instruction changed')
    allocation = json.loads(raw)
    spec = allocation['hardware_specification']
    spec_raw, spec_sha = checked(hardware_specification_path(spec), spec['sha256'], maximum=128 * 1024)
    if len(spec_raw) != spec['size_bytes'] or spec_sha != spec['sha256']:
        raise ValueError('hardware specification bytes changed')
    live = live_hardware_limits()
    planned = plan_source_unit_execution(protocol, allocation, live_limits=live, protocol_sha256=protocol_sha256)
    joined = {'path': str(HARDWARE_EXECUTION.resolve()), 'sha256': sha, 'size_bytes': len(raw),
              'kind': allocation['kind']}
    return raw, spec_raw, spec, joined, live, planned


def snapshot_tool_files():
    payload = {}
    for name in TOOL_FILES:
        script, script_sha = checked(ROOT / name)
        payload[name] = {'sha256': script_sha, 'content_hex': script.hex()}
    return payload


def apply_registered_limits(cap):
    resource.setrlimit(resource.RLIMIT_CPU, (cap['cpu_seconds'], cap['hard_cpu_seconds']))
    resource.setrlimit(resource.RLIMIT_AS, (cap['memory_bytes'], cap['memory_bytes']))
    resource.setrlimit(resource.RLIMIT_FSIZE, (cap['maximum_output_file_bytes'], cap['maximum_output_file_bytes']))


def install_source_worker_signal_handlers():
    def handle(signum, frame):
        raise SourceWorkerInterrupt(f'source worker received signal {signum}')
    signal.signal(signal.SIGTERM, handle)
    signal.signal(signal.SIGINT, handle)


def authenticate_registered_packet(packet_path):
    packet = json.loads(checked(packet_path, maximum=2 * 1024**2)[0])
    protocol = json.loads(checked(PROTOCOL, packet['protocol_sha256'])[0])
    cap = limits(protocol, packet['configuration']['mode'])
    if packet['limits'] != cap:
        raise ValueError('registered source check resource limits changed')
    apply_registered_limits(cap)
    sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
    from trading_research.operations.artifacts import artifact_ref
    from trading_research.operations.trials import TrialRegistry
    registry = TrialRegistry(ROOT / 'evidence/trials')
    state = registry.state()
    attempt, trial = state['attempts'][packet['attempt_id']], state['trials'][packet['trial_id']]
    if (attempt['status'] != 'running' or attempt['trial_id'] != packet['trial_id']
            or attempt['family'] != protocol['family'] or attempt['cpu_reservation_seconds'] != cap['hard_cpu_seconds']
            or trial['code_hash'] != packet['code_snapshot']['sha256']
            or trial['configuration'] != packet['configuration']
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
    if manifest != packet['code_manifest'] or set(TOOL_FILES) - set(script):
        raise ValueError('packet source manifest differs from its reproducible snapshot')
    for name, sha in manifest.items():
        checked(ROOT / name, sha)
    for reference in protocol['frozen_metadata']:
        raw, _ = checked(reference['path'], reference['sha256'])
        if len(raw) != reference['size_bytes']:
            raise ValueError('frozen source/scientific metadata size changed')
    extension = load_reference(packet['configuration']['check_extension'])
    expected_versions = {**protocol['runtime_versions'], **extension.get('additional_runtime_versions', {})}
    versions = {name: importlib.metadata.version(name) for name in expected_versions}
    if (versions != expected_versions or sys.version != protocol['python_version']
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
    for reference, saved in zip(extension.get('retained_validation_inputs', []),
                               packet['configuration']['retained_validation_input_snapshots'], strict=True):
        original, _ = checked(reference['path'], reference['sha256'])
        if len(original) != reference['size_bytes'] or registry.artifacts.read(artifact_ref(saved)) != original:
            raise ValueError('cohort training reference differs from its registered snapshot')
    from trading_research.research.auction_flow_anchors import CONTRACT_SHA256, DETAIL_SHA256
    if [r['sha256'] for r in extension['scientific_supplements']] != [CONTRACT_SHA256, DETAIL_SHA256]:
        raise ValueError('implemented anchor records are not bound to the exact declared mechanisms')
    hardware_raw, spec_raw, spec, joined, live, planned = join_hardware_execution(
        protocol, packet['protocol_sha256'], packet['configuration']['hardware_execution'])
    if (packet['configuration']['hardware_execution'] != joined
            or packet['configuration']['hardware_specification'] != spec
            or registry.artifacts.read(artifact_ref(packet['configuration']['hardware_execution_snapshot'])) != hardware_raw
            or registry.artifacts.read(artifact_ref(packet['configuration']['hardware_specification_snapshot'])) != spec_raw):
        raise ValueError('hardware execution instruction is not fully preserved in its registered snapshot')
    registered_plan = packet['configuration']['source_unit_execution']
    concurrency = min(registered_plan['maximum_concurrency'], planned['maximum_concurrency'])
    if concurrency < 1:
        raise ValueError('live allocation cannot support one source child plus coordinator')
    return {
        'packet': packet, 'protocol': protocol, 'cap': cap, 'extension': extension,
        'versions': versions, 'registry': registry, 'planned': planned,
        'registered_plan': registered_plan, 'concurrency': concurrency, 'live': live,
    }


def execute_source_units_parallel(windows, *, protocol, index, coordinates, outputs, data_root, calendar,
                                  packet_path, packet, planned, concurrency, cap, worker_started, evidence,
                                  cohort_contract=None):
    from trading_research.operations.artifacts import canonical_json

    reserved = require_output_reservation(
        len(windows), planned['maximum_child_output_bytes'], outputs.maximum_total - outputs.written)
    allocation = actual_source_unit_allocation(planned, len(windows), concurrency_limit=concurrency)
    concurrency = allocation['actual_concurrency']
    allocated = allocation['allocated_address_space_bytes']
    runner = str(Path(__file__).resolve())
    registered = str(Path(packet_path).resolve())
    jobs, directories, charged = [], [], False
    try:
        for ordinal, unit in enumerate(windows):
            expected_dir, expected_packet = require_source_unit_namespace(
                attempt_id=packet['attempt_id'], ordinal=ordinal,
                child_packet_path=outputs.directory / f'source-unit-{ordinal:02d}' / 'packet.json',
                output_directory=outputs.directory / f'source-unit-{ordinal:02d}',
                runs_root=RUNS)
            expected_dir.mkdir(parents=False, exist_ok=False)
            directories.append(expected_dir)
            child_packet = {
                'kind': 'auction_flow_source_unit_packet_v1',
                'registered_packet_path': registered, 'ordinal': ordinal, 'unit': unit,
                'unit_identity': unit_identity(unit), 'coordinator_pid': os.getpid(),
                'attempt_id': packet['attempt_id'], 'trial_id': packet['trial_id'],
                'protocol_sha256': packet['protocol_sha256'],
                'code_snapshot': packet['code_snapshot'],
                'configuration': packet['configuration'],
                'output_directory': str(expected_dir),
            }
            payload = canonical_json(child_packet) + b'\n'
            if len(payload) > cap['maximum_output_file_bytes']:
                raise ValueError('source unit packet exceeds the registered file bound')
            artifacts_allowance_after_packet(planned['maximum_child_output_bytes'], len(payload))
            expected_packet.write_bytes(payload)
            jobs.append({
                'ordinal': ordinal,
                'argv': [sys.executable, runner, '--source-unit', registered, str(expected_packet)],
                'cwd': str(ROOT),
                'env': {**os.environ, **THREADS, 'PYTHONHASHSEED': '0'},
                'output_directory': str(expected_dir),
            })
        require_complete_ordinals([job['ordinal'] for job in jobs])
        evidence.update(reserved_output_bytes=reserved, actual_concurrency=concurrency,
                        allocated_address_space_bytes=allocated,
                        aggregate_memory_ceiling_bytes=allocation['aggregate_memory_ceiling_bytes'],
                        maximum_concurrency_ceiling=allocation['maximum_concurrency_ceiling'])
        supervise_source_children(
            jobs, concurrency=concurrency, cpu_soft_seconds=cap['cpu_seconds'],
            cpu_hard_seconds=cap['hard_cpu_seconds'],
            wall_deadline_monotonic=pool_wall_deadline(worker_started, cap['wall_seconds']),
            allocated_address_space_bytes=allocated, evidence=evidence)
        try:
            charge_child_output_bytes(
                outputs, directories, reservation_per_child=planned['maximum_child_output_bytes'],
                evidence=evidence)
        finally:
            charged = True
        apply_remaining_coordinator_cpu_limit(cap['cpu_seconds'], cap['hard_cpu_seconds'])
        results, refs = [], []
        for ordinal, unit in enumerate(windows):
            child = evidence['children'][ordinal]
            if not child.get('success'):
                raise ValueError('source unit failed; partial files retained')
            receipt_path = directories[ordinal] / 'artifacts' / 'source-unit-receipt.json'
            raw, _ = checked(receipt_path, maximum=min(
                cap['maximum_output_file_bytes'], planned['maximum_child_output_bytes']))
            receipt = json.loads(raw)
            require_joined_receipt(
                receipt, packet=packet, wait4_child=child, unit=unit, coordinator_pid=os.getpid())
            reference = receipt['resource_unit']
            require_reference_in_namespace(reference, directories[ordinal] / 'artifacts')
            result = load_reference(reference, maximum=planned['maximum_child_output_bytes'])
            if result.get('unit') != unit:
                raise ValueError('source unit result identity changed')
            results.append(result)
            refs.append(reference)
        return results, refs
    finally:
        if not charged:
            try:
                charge_child_output_bytes(
                    outputs, directories, reservation_per_child=planned['maximum_child_output_bytes'],
                    evidence=evidence)
            except ValueError:
                pass
        try:
            apply_remaining_coordinator_cpu_limit(cap['cpu_seconds'], cap['hard_cpu_seconds'])
        except ValueError:
            pass


def source_unit(registered_packet_path, child_packet_path):
    bootstrap_process_limits()
    try:
        child = json.loads(checked(child_packet_path, maximum=2 * 1024**2)[0])
        registered = json.loads(checked(registered_packet_path, maximum=2 * 1024**2)[0])
        if (child.get('kind') != 'auction_flow_source_unit_packet_v1'
                or Path(child['registered_packet_path']).resolve() != Path(registered_packet_path).resolve()):
            raise ValueError('source unit packet identity changed')
        if os.environ.get('PYTHONHASHSEED') != '0':
            raise ValueError('frozen runtime or one-thread scenario changed')
        require_parent_identity(coordinator_pid=child['coordinator_pid'],
                                supervisor_pid=registered['supervisor_pid'])
        authenticated = authenticate_registered_packet(registered_packet_path)
        packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
        if (child['attempt_id'] != packet['attempt_id'] or child['trial_id'] != packet['trial_id']
                or child.get('protocol_sha256') != packet['protocol_sha256']
                or child.get('code_snapshot') != packet['code_snapshot']
                or child.get('configuration') != packet['configuration']
                or child['coordinator_pid'] != os.getppid()):
            raise ValueError('source unit parent identity mismatch')
        if Path(child['output_directory']).resolve() != Path(child_packet_path).resolve().parent:
            raise ValueError('source unit output directory changed')
        expected_dir, expected_packet = require_source_unit_namespace(
            attempt_id=packet['attempt_id'], ordinal=child['ordinal'],
            child_packet_path=child_packet_path, output_directory=child['output_directory'],
            runs_root=RUNS)
        from trading_research.foundations.cash_calendar import CashCalendar
        from trading_research.research.auction_flow_coordinates import RetainedCoordinateIndex
        from trading_research.research.auction_flow_preflight import resource_windows, measured_unit
        from trading_research.research.auction_flow_storage import BoundedOutputs
        calendar = CashCalendar(Path(protocol['cash_calendar']['path']))
        index = load_reference(protocol['source_index'])
        windows = resource_windows(protocol, index, calendar)
        unit = require_unit_identity(windows, child['ordinal'], child['unit_identity'])
        if child.get('unit') != unit:
            raise ValueError('source unit ordinal/identity changed')
        planned = authenticated['registered_plan']
        packet_bytes = Path(expected_packet).stat().st_size
        allowance = artifacts_allowance_after_packet(planned['maximum_child_output_bytes'], packet_bytes)
        file_limit = min(cap['maximum_output_file_bytes'], allowance)
        outputs = BoundedOutputs(expected_dir / 'artifacts',
            maximum_total_bytes=allowance, maximum_file_bytes=file_limit)
        symbol = unit['root']
        reference = protocol['coordinate_admissions'][symbol]
        coordinates = RetainedCoordinateIndex(
            load_reference(reference), source_version=reference['sha256'],
            snapshot_supplement=load_reference(protocol['nq_snapshot_supplement']) if symbol == 'NQ' else None,
            snapshot_version=protocol['nq_snapshot_supplement']['sha256'] if symbol == 'NQ' else None)
        result, resource_ref = measured_unit(
            unit, protocol=protocol, index=index, coordinates=coordinates, outputs=outputs,
            data_root=ROOT.parent / 'data', storage_encoding='structural', anchor_calendar=calendar,
            cohort_contract=authenticated['extension'].get('cohort_validation'))
        require_reference_in_namespace(resource_ref, expected_dir / 'artifacts')
        outputs.json('source-unit-receipt.json', {
            'kind': 'auction_flow_source_unit_receipt_v1', 'success': True,
            'attempt_id': packet['attempt_id'], 'trial_id': packet['trial_id'],
            'protocol_sha256': packet['protocol_sha256'],
            'code_snapshot': packet['code_snapshot'],
            'configuration': packet['configuration'],
            'coordinator_pid': child['coordinator_pid'],
            'child_pid': os.getpid(),
            'ordinal': child['ordinal'],
            'unit_identity': unit_identity(unit),
            'unit': unit,
            'resource_unit': resource_ref,
        }, kind='auction_flow_source_unit_receipt')
        return 0
    except BaseException:
        traceback.print_exc()
        return 1


def compile_source_projection(packet_path, outputs):
    """Compile inside the same capped worker; wait4 retains compiler CPU."""
    from trading_research.data.compact_native import CPP_SOURCE, enable_compiled_projection
    from trading_research.errors import ContractError
    source_name, library_name = 'compact-projection.cpp', 'compact-projection.so'
    with outputs.create(source_name) as stream:
        stream.write(CPP_SOURCE.encode())
    source_ref = outputs.reference(source_name, kind='compiled_projection_source')
    library_path = outputs.directory / library_name
    if outputs.maximum_total - outputs.written < outputs.maximum_file:
        raise ContractError('compiler requires a full individual-file reservation')
    command = ['/usr/bin/g++', '-O3', '-std=c++17', '-pipe', '-shared', '-fPIC',
               '-fno-fast-math', '-ffp-contract=off', source_ref['path'], '-o', str(library_path)]
    child_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.process_time()
    compiled = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
    child_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = time.process_time()-started + child_after.ru_utime+child_after.ru_stime-child_before.ru_utime-child_before.ru_stime
    if library_path.exists():
        outputs.names.add(library_name)
        outputs.written += library_path.stat().st_size
    if compiled.returncode:
        raise RuntimeError('C++ projection build failed: ' + compiled.stderr.decode(errors='replace')[:8192])
    library_ref = outputs.reference(library_name, kind='compiled_projection_shared_library')
    enable_compiled_projection(library_path, library_ref['sha256'])
    version = subprocess.run(['/usr/bin/g++', '--version'], capture_output=True, text=True, check=True, timeout=5).stdout
    return dict(source=source_ref, library=library_ref, command=command, compiler_version=version,
                compiler_cpu_seconds=cpu, compile_in_registered_worker=True, fast_math=False)


def compute_source_unit(unit, protocol, index, coordinates, outputs, profiler):
    """Isolate unchanged complete calculations from optional derived-file writes."""
    import importlib._bootstrap as import_bootstrap
    from collections import Counter
    from trading_research.research.auction_flow_pipeline import measure_raw_window
    imported, examples = Counter(), {}
    original_import = import_bootstrap._find_and_load
    def traced_import(name, import_):
        imported[name] += 1
        if name not in examples:
            examples[name] = traceback.format_stack(limit=7)
        return original_import(name, import_)
    started = time.process_time()
    if profiler is not None:
        import_bootstrap._find_and_load = traced_import
        profiler.enable()
    try:
        measured = measure_raw_window(data_root=ROOT.parent / 'data', index=index, coordinates=coordinates,
            root=unit['root'], start_ns=unit['event_start_ns'], end_ns=unit['event_end_ns'],
            source_paths=(unit['source_path'],), maximum_scan_rows=protocol['resources']['maximum_source_day_scan_rows'],
            native_width_ns=protocol['native_width_ns'], atomic_width_ns=protocol['atomic_width_ns'],
            maximum_native_array_bytes=protocol['resources']['maximum_native_array_bytes'])
    finally:
        if profiler is not None:
            profiler.disable()
            import_bootstrap._find_and_load = original_import
    cpu = time.process_time() - started
    name = f"{unit['root']}-{unit['event_start_ns']}-{unit['source_variant']}"
    measurement = outputs.json_compressed(name + '-compute-measurements.json.zst', measured,
        kind='auction_flow_compute_diagnostic_measurements', measurement_fast_path=True)
    result = dict(unit=unit, measurement=measurement, cpu_seconds=cpu,
        pipeline_cpu_components=measured['pipeline_cpu_components'],
        scan_cpu_components_disjoint=measured['scan_cpu_components_disjoint'],
        source_cpu_components=measured['source_manifest']['source_cpu_components'],
        workload_counts=measured['workload_counts'],
        counts=measured['source_manifest']['projection']['counts'],
        canonical_selected_raw_stream=measured['source_manifest']['canonical_selected_raw_stream'],
        actual_import_counts=dict(imported), actual_import_stacks=examples,
        scope='Unchanged full calculations, including dense native grid; event/native retention callbacks omitted. Diagnostic only; no extraction representation or family completion accepted.')
    reference = outputs.json(name + '-compute-resource-unit.json', result, kind='auction_flow_compute_diagnostic')
    print('AUCTION_FLOW_COMPUTE_UNIT ' + reference['path'], flush=True)
    return result, reference


def profile_source(authenticated, packet_path, *, benchmark=False, compute=False):
    """One declared complete NQ day; diagnostic only, never a verification claim."""
    import cProfile
    import pstats
    from trading_research.foundations.cash_calendar import CashCalendar
    from trading_research.research.auction_flow_coordinates import RetainedCoordinateIndex
    from trading_research.research.auction_flow_preflight import (
        measured_unit, resource_windows, compare_prior_values, partition_parity)
    from trading_research.research.auction_flow_storage import BoundedOutputs, read_json_artifact
    from trading_research.research.auction_flow_resources import source_cost_projection
    from trading_research.operations.artifacts import canonical_json, publish_new

    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    index = load_reference(protocol['source_index'])
    calendar = CashCalendar(Path(protocol['cash_calendar']['path']))
    all_units = resource_windows(protocol, index, calendar)
    selected = [u for u in all_units if u['root'] == 'NQ' and u['role'] == 'ordinary_pipeline_cost']
    if len(selected) != 1:
        raise ValueError('profile must use the one previously declared complete NQ ordinary window')
    units = all_units if benchmark or compute and authenticated['extension'].get('compute_all_units', True) else selected
    coordinates = {}
    for root, reference in protocol['coordinate_admissions'].items():
        coordinates[root] = RetainedCoordinateIndex(load_reference(reference), source_version=reference['sha256'],
            snapshot_supplement=load_reference(protocol['nq_snapshot_supplement']) if root == 'NQ' else None,
            snapshot_version=protocol['nq_snapshot_supplement']['sha256'] if root == 'NQ' else None)
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs',
        maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'],
        maximum_file_bytes=cap['maximum_output_file_bytes'])
    compiled_projection = compile_source_projection(packet_path, outputs) if authenticated['extension'].get('compiled_projection') else None
    test_report = None
    if benchmark:
        import unittest
        test_start = time.process_time()
        modules = authenticated['extension']['benchmark_check_modules']
        if any(name not in protocol['check_modules'] for name in modules):
            raise ValueError('focused benchmark tests must belong to the original family test set')
        suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
        tested = unittest.TextTestRunner(verbosity=2).run(suite)
        test_report = dict(tests=tested.testsRun, failures=len(tested.failures), errors=len(tested.errors),
                           success=tested.wasSuccessful(), cpu_seconds=time.process_time()-test_start,
                           modules=modules)
        if not tested.wasSuccessful():
            raise ValueError('focused source regression checks failed; do not scan further')
    profiler = cProfile.Profile()
    results, references = [], []
    for unit in units:
        if compute:
            result, reference = compute_source_unit(unit, protocol, index, coordinates[unit['root']], outputs,
                profiler if unit == selected[0] else None)
            results.append(result)
            references.append(reference)
            continue
        result, reference = measured_unit(unit, protocol=protocol, index=index, coordinates=coordinates[unit['root']],
            outputs=outputs, data_root=ROOT.parent / 'data', storage_encoding='structural',
            diagnostic_profiler=profiler if unit == selected[0] else None)
        results.append(result)
        references.append(reference)
    rows = [{'file': key[0], 'line': key[1], 'function': key[2], 'primitive_calls': value[0],
             'calls': value[1], 'self_elapsed_seconds': value[2], 'cumulative_elapsed_seconds': value[3]}
            for key, value in pstats.Stats(profiler).stats.items()]
    rows.sort(key=lambda row: row['self_elapsed_seconds'], reverse=True)
    profile_ref = outputs.json('complete-source-function-profile.json', rows, kind='auction_flow_function_profile')
    compute_diagnostics = []
    if benchmark and authenticated['extension'].get('benchmark_compute_diagnostic'):
        for unit in all_units:
            _, reference = compute_source_unit(unit, protocol, index, coordinates[unit['root']], outputs, None)
            compute_diagnostics.append(reference)
    preflight = None
    if benchmark:
        prior = load_reference(authenticated['extension']['prior_accepted_worker'])
        comparison = compare_prior_values(results, references, prior, outputs=outputs, load_reference=load_reference)
        cuts = [partition_parity(result, protocol=protocol, index=index,
                    coordinates=coordinates[result['unit']['root']], outputs=outputs, data_root=ROOT.parent / 'data')
                for result in results if result['unit']['role'] == 'full_observed_futures_clock_cost'
                or result['unit']['root'] == 'NQ' and result['unit']['role'] == 'ordinary_pipeline_cost']
        schedule_ref = prior['actual_source_preflight']['complete_source_schedule']
        projection = source_cost_projection(results, protocol, read_json_artifact(schedule_ref))
        preflight = dict(passed=True, resource_units=references,
            complete_retained_source_value_comparison=comparison, actual_continuation_parity_units=cuts,
            complete_source_schedule=schedule_ref,
            complete_instrument_inventory=prior['actual_source_preflight']['complete_instrument_inventory'],
            source_cost_projection=projection, resource_probe_only=True, complete_family_statistics=False,
            scope='Affected source tests and complete source/native/measurement/carry equivalence; unchanged inventory and schedule reused; no new anchor/cohort/structure/memory study')
    report = {key: packet[key] for key in
              ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration')}
    if compiled_projection is not None:
        from trading_research.data.compact_native import execution_counts
        compiled_projection.update(execution_counts())
        if compiled_projection['fused_rows'] == 0:
            raise ValueError('registered compiled projection never processed its acquired-schema population')
    report.update(compiled_projection=compiled_projection, family=protocol['family'], mode='compute' if compute else 'benchmark' if benchmark else 'profile', tests=test_report,
        actual_source_preflight=preflight,
        source_unit_parallel_execution=None, source_component_verified=benchmark, success=True,
        runtime_versions=authenticated['versions'], derived_output_bytes=outputs.written,
        resource_units=references, function_profile=profile_ref, compute_diagnostics=compute_diagnostics,
        scope='Focused source equivalence and performance' if benchmark else
            'CPU diagnosis of one previously declared complete source window; no new correctness or family-completion claim')
    publish_new(Path(packet['worker_report']), canonical_json(report) + b'\n')
    return 0


def downstream_measurements(authenticated, packet_path):
    """Recalculate consumers from explicitly authenticated accepted source artifacts."""
    import unittest
    from trading_research.operations.artifacts import canonical_json, publish_new
    from trading_research.research.auction_flow_storage import BoundedOutputs
    from trading_research.research.auction_flow_downstream import run_downstream

    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    modules = authenticated['extension']['downstream_check_modules']
    admitted = protocol['check_modules'] + authenticated['extension']['additional_check_modules']
    if not modules or len(set(modules)) != len(modules) or any(name not in admitted for name in modules):
        raise ValueError('downstream regression checks must belong to the retained family test set')
    began = time.process_time()
    tested = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    tests = dict(tests=tested.testsRun, failures=len(tested.failures), errors=len(tested.errors),
                 success=tested.wasSuccessful(), cpu_seconds=time.process_time()-began, modules=modules)
    if not tested.wasSuccessful():
        raise ValueError('downstream regression checks failed; no consumer execution')
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs',
        maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'],
        maximum_file_bytes=cap['maximum_output_file_bytes'])
    result = run_downstream(protocol=protocol, outputs=outputs, load_reference=load_reference,
                            check_extension=authenticated['extension'])
    report = {key: packet[key] for key in
              ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration')}
    report.update(family=protocol['family'], mode='downstream', tests=tests,
        actual_downstream_check=result, success=bool(result['passed']),
        source_component_verified=False, source_component_reused=True,
        source_unit_parallel_execution=None, runtime_versions=authenticated['versions'],
        derived_output_bytes=outputs.written,
        scope='Complete nine-unit anchor/profile/cohort recalculation from accepted source artifacts; no new raw-source execution or annual family completion')
    publish_new(Path(packet['worker_report']), canonical_json(report) + b'\n')
    return 0 if report['success'] else 1


def worker(packet_path):
    # Set fixed bootstrap ceilings before packet or candidate-dependent work.
    bootstrap_process_limits()
    install_source_worker_signal_handlers()
    worker_started = time.monotonic()
    try:
        authenticated = authenticate_registered_packet(packet_path)
        packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
        extension, versions = authenticated['extension'], authenticated['versions']
        if os.getppid() != packet['supervisor_pid']:
            raise ValueError('worker lacks its actual running same-family attempt, snapshot, limits and supervisor')
        if packet['configuration']['mode'] == 'downstream':
            return downstream_measurements(authenticated, packet_path)
        if packet['configuration']['mode'] in ('profile', 'benchmark', 'compute'):
            return profile_source(authenticated, packet_path,
                benchmark=packet['configuration']['mode'] == 'benchmark', compute=packet['configuration']['mode'] == 'compute')
        from trading_research.operations.artifacts import canonical_json, publish_new
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
        parallel_evidence = None
        from trading_research.research.auction_flow_storage import BoundedOutputs
        outputs = BoundedOutputs(Path(packet_path).parent / 'outputs',
            maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'],
            maximum_file_bytes=cap['maximum_output_file_bytes'])
        if result.wasSuccessful():
            from trading_research.research.auction_flow_preflight import run_preflight, REFERENCE_ROWS, NATIVE_WIDTH_NS
            if (REFERENCE_ROWS != protocol['actual_reference_maximum_raw_rows_per_variant']
                    or NATIVE_WIDTH_NS != protocol['native_width_ns']):
                raise ValueError('declared actual reference/native grid differs from the implementation')
            parallel_evidence = {}
            concurrency = min(authenticated['concurrency'], authenticated['registered_plan']['maximum_concurrency'])
            def unit_executor(windows, **context):
                return execute_source_units_parallel(
                    windows, packet_path=packet_path, packet=packet,
                    planned=authenticated['registered_plan'], concurrency=concurrency,
                    cap=cap, worker_started=worker_started, evidence=parallel_evidence, **context)
            preflight = run_preflight(protocol=protocol, root=ROOT, outputs=outputs, load_reference=load_reference,
                                      check_extension=extension, unit_executor=unit_executor)
        report = {'family': protocol['family'], 'mode': 'check', 'attempt_id': packet['attempt_id'],
            'trial_id': packet['trial_id'], 'protocol_sha256': packet['protocol_sha256'],
            'code_snapshot': packet['code_snapshot'], 'tools_snapshot': packet['tools_snapshot'],
            'configuration': packet['configuration'], 'tests': test_report, 'actual_source_preflight': preflight,
            'source_unit_parallel_execution': parallel_evidence,
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


def parent(mode='check'):
    sys.path.insert(0, str(ROOT / 'src'))
    from trading_research.operations.artifacts import artifact_ref, canonical_json, code_snapshot, publish_new
    from trading_research.operations.trials import TrialRegistry
    protocol_raw, protocol_sha = checked(PROTOCOL)
    protocol = json.loads(protocol_raw)
    cap = limits(protocol, mode)
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
    tools_payload = snapshot_tool_files()
    tools_ref = store.put_json(tools_payload, kind='auction_flow_tools_snapshot')
    manifest.update({name: row['sha256'] for name, row in tools_payload.items()})
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
    retained_validation_input_snapshots = []
    for reference in extension.get('retained_validation_inputs', []):
        raw, _ = checked(reference['path'], reference['sha256'])
        if len(raw) != reference['size_bytes']:
            raise ValueError('cohort training reference changed before registration')
        retained_validation_input_snapshots.append(asdict(store.put_bytes(raw, kind=reference['kind'])))
    hardware_raw, spec_raw, spec, hardware_ref, observed_hardware, planned = join_hardware_execution(
        protocol, protocol_sha)
    hardware_snapshot = store.put_bytes(hardware_raw, kind=hardware_ref['kind'])
    spec_snapshot = store.put_bytes(spec_raw, kind='auction_flow_hardware_specification')
    configuration = {'mode': mode, 'protocol_sha256': protocol_sha, 'tools_snapshot': asdict(tools_ref),
        'verified_component': dependency_contract(manifest, protocol), 'thread_limits': THREADS,
        'check_extension': {'path': str(CHECK_EXTENSION), 'sha256': extension_sha, 'size_bytes': len(extension_raw),
                            'kind': extension['kind']},
        'check_extension_snapshot': asdict(extension_snapshot),
        'scientific_supplement_snapshots': supplement_snapshots,
        'frozen_test_reference_snapshots': frozen_test_reference_snapshots,
        'retained_validation_input_snapshots': retained_validation_input_snapshots,
        'hardware_execution': hardware_ref,
        'hardware_execution_snapshot': asdict(hardware_snapshot),
        'hardware_specification': spec,
        'hardware_specification_snapshot': asdict(spec_snapshot),
        'observed_hardware': observed_hardware,
        'source_unit_execution': planned,
        'python_executable': sys.executable, 'limits': cap, 'previous_study_output_bytes': previous_bytes}
    trial = registry.register(name='Acquired auction/flow: ' + ('complete source performance diagnostic' if mode in ('profile','benchmark','compute')
        else 'accepted-source downstream measurement recalculation' if mode == 'downstream'
        else 'consolidated source and full-window resource check'),
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
    accounting_complete, accounting_uncertainty = True, None
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
                    cleanup = cleanup_reaped_coordinator_group(process.pid)
                    accounting_complete = cleanup['cpu_accounting_complete']
                    accounting_uncertainty = cleanup['cpu_accounting_uncertainty']
                    break
                if time.monotonic() - started > cap['wall_seconds']:
                    timed_out = True
                    stopped = terminate_then_kill_group(process.pid)
                    observed = stopped['usage']
                    process.returncode = 1 if stopped['exit_code'] is None else stopped['exit_code']
                    accounting_complete = stopped['cpu_accounting_complete']
                    accounting_uncertainty = stopped['cpu_accounting_uncertainty']
                    break
                time.sleep(0.2)
        worker_path = destination / 'worker.json'
        value = json.loads(checked(worker_path)[0]) if worker_path.is_file() else None
        joined = value is not None and all(value.get(k) == packet[k] for k in
            ('trial_id', 'attempt_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration'))
        output_bytes = sum(p.stat().st_size for p in destination.rglob('*') if p.is_file())
        elapsed = time.monotonic() - started
        wait4_cpu = None if observed is None else wait4_cpu_seconds(observed)
        peak = 0 if observed is None else observed.ru_maxrss * 1024
        parallel = None if value is None else value.get('source_unit_parallel_execution')
        cpu = conservative_attempt_cpu_seconds(
            wait4_usage=observed, accounting_complete=accounting_complete,
            hard_cpu_seconds=cap['hard_cpu_seconds'])
        within = (wait4_cpu is not None and cpu <= cap['cpu_seconds'] and peak <= cap['memory_bytes']
                  and elapsed <= cap['wall_seconds'] and not timed_out)
        log_ref = store.put_bytes(checked(destination / 'worker.log')[0], kind='auction_flow_worker_log')
        worker_ref = None if value is None else store.put_json(value, kind='auction_flow_worker_report')
        output_bytes += log_ref.size_bytes + (0 if worker_ref is None else worker_ref.size_bytes)
        basis = ('wait4_registered_worker_and_reaped_descendants' if accounting_complete
                 else 'conservative_incomplete_descendant_accounting')
        report = {'family': protocol['family'], 'mode': mode, 'trial_id': trial, 'attempt_id': attempt_id,
            'protocol_sha256': protocol_sha, 'code_snapshot': asdict(snapshot), 'tools_snapshot': asdict(tools_ref),
            'configuration': configuration, 'worker_report': None if worker_ref is None else asdict(worker_ref),
            'worker_report_path': str(worker_path), 'worker_log': asdict(log_ref),
            'exit_code': process.returncode, 'wall_timeout': timed_out, 'worker_identity_joined': joined,
            'cpu_seconds': cpu, 'wait4_worker_cpu_seconds': wait4_cpu,
            'wait4_registered_worker_and_reaped_descendants_seconds': wait4_cpu,
            'wall_seconds': elapsed, 'peak_rss_bytes': peak, 'per_process_wait4_peak_rss_bytes': peak,
            'aggregate_address_space_bytes': None if not parallel else parallel.get('allocated_address_space_bytes'),
            'observed_aggregate_rss_bytes': None if not parallel else parallel.get('observed_aggregate_rss_bytes'),
            'source_unit_parallel_execution': parallel,
            'pool_execution_is_checkpoint_only': True,
            'cpu_accounting_complete': accounting_complete,
            'cpu_accounting_uncertainty': accounting_uncertainty,
            'within_declared_limits': within, 'resource_basis': basis,
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
            reason=('Complete bounded ' + mode + ' workload' if report['success']
                    else 'Bounded source workload failed; log and all partial outputs retained'),
            result_artifacts=(asdict(report_ref),))
        finalized = True
        publish_new(destination / 'execution.json', canonical_json(report) + b'\n')
        print(json.dumps({'report': str(destination / 'execution.json'), 'success': report['success'],
            'cpu_seconds': cpu, 'peak_rss_bytes': peak, 'attempt_output_bytes': report['attempt_output_bytes']}), flush=True)
        return 0 if report['success'] else 1
    except BaseException as exc:
        if process is not None and process.returncode is None:
            stopped = terminate_then_kill_group(process.pid)
            observed = stopped['usage'] if stopped['usage'] is not None else observed
            process.returncode = 1 if stopped['exit_code'] is None else stopped['exit_code']
            accounting_complete = stopped['cpu_accounting_complete']
            accounting_uncertainty = stopped['cpu_accounting_uncertainty']
        if not finalized:
            interrupted_cpu = (0.0 if process is None else conservative_attempt_cpu_seconds(
                wait4_usage=observed, accounting_complete=accounting_complete,
                hard_cpu_seconds=cap['hard_cpu_seconds']))
            registry.finish(attempt_id, status='interrupted',
                cpu_seconds=interrupted_cpu,
                wall_seconds=time.monotonic() - started,
                peak_rss_bytes=0 if process is None or observed is None else observed.ru_maxrss * 1024,
                reason=f'source supervisor exception: {type(exc).__name__}; unknown consumption keeps its reservation')
        raise


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        raise SystemExit(worker(sys.argv[2]))
    if len(sys.argv) == 4 and sys.argv[1] == '--source-unit':
        raise SystemExit(source_unit(sys.argv[2], sys.argv[3]))
    if len(sys.argv) != 2 or sys.argv[1] not in ('check', 'profile', 'benchmark', 'compute', 'downstream'):
        raise SystemExit('usage: run_auction_flow_study.py {check|profile|benchmark|compute|downstream}')
    raise SystemExit(parent(sys.argv[1]))
