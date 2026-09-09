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
        require_output_reservation, require_file_output_reservations,
        artifacts_allowance_after_packet, charge_child_output_bytes,
        actual_source_unit_allocation, require_source_unit_namespace,
        source_file_namespace, require_source_file_namespace,
        require_reference_in_namespace, require_joined_receipt, require_complete_ordinals,
        pool_wall_deadline, wait4_cpu_seconds, apply_remaining_coordinator_cpu_limit,
        terminate_then_kill_group, cleanup_reaped_coordinator_group, conservative_attempt_cpu_seconds,
        REQUIRED_CPU_BUDGET_SECONDS, REQUIRED_HARD_CPU_MARGIN_SECONDS, SourceWorkerInterrupt)
except ImportError:
    from auction_flow_parallel import (
        live_hardware_limits, plan_source_unit_execution, require_parent_identity,
        require_unit_identity, unit_identity, supervise_source_children,
        require_output_reservation, require_file_output_reservations,
        artifacts_allowance_after_packet, charge_child_output_bytes,
        actual_source_unit_allocation, require_source_unit_namespace,
        source_file_namespace, require_source_file_namespace,
        require_reference_in_namespace, require_joined_receipt, require_complete_ordinals,
        pool_wall_deadline, wait4_cpu_seconds, apply_remaining_coordinator_cpu_limit,
        terminate_then_kill_group, cleanup_reaped_coordinator_group, conservative_attempt_cpu_seconds,
        REQUIRED_CPU_BUDGET_SECONDS, REQUIRED_HARD_CPU_MARGIN_SECONDS, SourceWorkerInterrupt)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / 'validation/AUCTION_FLOW_STUDY_V1.json'
CHECK_EXTENSION = ROOT / 'validation/AUCTION_FLOW_SOURCE_CHECK_EXTENSION_V21.json'
HARDWARE_EXECUTION = ROOT / 'validation/AUCTION_FLOW_HARDWARE_EXECUTION_V2.json'
TOOL_FILES = ('tools/run_auction_flow_study.py', 'tools/auction_flow_parallel.py')
RUNS = ROOT / 'reports/auction-flow-runs'
THREADS = {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
           'ARROW_NUM_THREADS': '1', 'NUMEXPR_NUM_THREADS': '1'}
EXTRACT_MODES = ('extract', 'extract-check')
BOOTSTRAP_SOFT_CPU_SECONDS = 1210
FAMILY_HARD_CPU_SECONDS = REQUIRED_CPU_BUDGET_SECONDS + REQUIRED_HARD_CPU_MARGIN_SECONDS
REGISTERED_MODES = ('check', 'profile', 'benchmark', 'compute', 'downstream', 'throughput',
                    'clock-audit', 'source-clock', 'extract', 'extract-check')


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


def limits(protocol, mode='check', *, extension=None):
    resource_spec = protocol['resources']
    cpu = resource_spec['phase_cpu_seconds']['check']
    cap = {'cpu_seconds': cpu, 'hard_cpu_seconds': cpu + resource_spec['hard_cpu_margin_seconds'],
        'memory_bytes': resource_spec['memory_bytes'], 'maximum_output_file_bytes': resource_spec['maximum_output_file_bytes'],
        'maximum_output_bytes': resource_spec['maximum_derived_output_bytes'],
        'supervisor_output_reserve_bytes': resource_spec['supervisor_output_reserve_bytes'],
        'wall_seconds': resource_spec['per_check_wall_seconds']}
    if mode in ('profile', 'compute', 'clock-audit'):
        cap.update(cpu_seconds=180, hard_cpu_seconds=190, wall_seconds=300,
                   maximum_output_bytes=512 * 1024**2, maximum_output_file_bytes=128 * 1024**2)
    elif mode in ('benchmark', 'downstream'):
        cap.update(cpu_seconds=600, hard_cpu_seconds=610, wall_seconds=900,
                   maximum_output_bytes=1024**3, maximum_output_file_bytes=128 * 1024**2)
    elif mode == 'source-clock':
        cap.update(cpu_seconds=600, hard_cpu_seconds=610, wall_seconds=900,
                   maximum_output_bytes=4 * 1024 ** 3)
    elif mode in EXTRACT_MODES:
        return production_mode_limits(protocol, mode, extension)
    elif mode not in ('check', 'throughput'):
        raise ValueError('unknown registered source workload')
    return cap


def production_declarations(extension, mode):
    # Metadata-only before registration: no research module imports here.
    prefix = 'extract_check' if mode == 'extract-check' else 'production'
    declared, plan = extension.get(prefix + '_limits'), extension.get(prefix + '_plan')
    if not isinstance(declared, dict) or not isinstance(plan, dict):
        raise ValueError('production allocation/plan is absent; refuse to invent extract caps')
    return declared, plan


def production_mode_limits(protocol, mode, extension=None):
    if extension is None:
        if not CHECK_EXTENSION.is_file():
            raise ValueError('production allocation is absent; refuse to invent extract caps')
        extension = json.loads(checked(CHECK_EXTENSION)[0])
    declared, _ = production_declarations(extension, mode)
    if {'path', 'sha256', 'size_bytes'} <= declared.keys():
        declared = load_reference(declared)
    expected_kind = 'auction_flow_extract_check_limits_v1' if mode == 'extract-check' else 'auction_flow_production_limits_v1'
    names = ('cpu_seconds', 'hard_cpu_seconds', 'wall_seconds', 'memory_bytes',
             'maximum_output_file_bytes', 'maximum_output_bytes', 'supervisor_output_reserve_bytes')
    if declared.get('kind') != expected_kind or any(type(declared.get(k)) is not int or declared[k] <= 0 for k in names):
        raise ValueError('production_limits are missing or invalid')
    r = protocol['resources']
    if (declared['hard_cpu_seconds'] != declared['cpu_seconds'] + r['hard_cpu_margin_seconds']
            or declared['cpu_seconds'] > r['cpu_budget_seconds']
            or declared['memory_bytes'] != r['memory_bytes']
            or declared['maximum_output_file_bytes'] != r['maximum_output_file_bytes']
            or declared['maximum_output_bytes'] > r['maximum_study_output_bytes']
            or declared['supervisor_output_reserve_bytes'] >= declared['maximum_output_bytes']
            or mode == 'extract-check' and declared['maximum_output_bytes'] > r['maximum_derived_output_bytes']):
        raise ValueError('production limits exceed the original family resources')
    return {k: declared[k] for k in names}


def _finite_rlimit(value, ceiling):
    return ceiling if value in (-1, resource.RLIM_INFINITY) else min(ceiling, value)


def bootstrap_process_limits():
    # Pre-authentication keeps a small SOFT CPU cap. HARD may remain the
    # inherited bound or, when unlimited, the unchanged family total so an
    # authenticated extract can raise SOFT without exceeding that budget.
    # Inherited tighter parent bounds for ordinary tests/benchmarks stay.
    soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
    new_hard = _finite_rlimit(hard, FAMILY_HARD_CPU_SECONDS)
    new_soft = _finite_rlimit(soft, BOOTSTRAP_SOFT_CPU_SECONDS)
    if new_soft > new_hard:
        new_soft = new_hard
    resource.setrlimit(resource.RLIMIT_CPU, (new_soft, new_hard))
    for kind, ceiling in ((resource.RLIMIT_AS, 4 * 1024**3),
                          (resource.RLIMIT_FSIZE, 512 * 1024**2)):
        soft, hard = resource.getrlimit(kind)
        resource.setrlimit(kind, (_finite_rlimit(soft, ceiling), _finite_rlimit(hard, ceiling)))


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


def _apply_authenticated_rlimit(kind, soft, hard, *, name):
    current_soft, current_hard = resource.getrlimit(kind)
    if current_hard not in (-1, resource.RLIM_INFINITY):
        if hard > current_hard:
            raise ValueError(f'authenticated {name} limit would raise an inherited hard rlimit')
        hard = min(hard, current_hard)
    if soft > hard:
        raise ValueError(f'authenticated {name} exceeds inherited or family hard bound')
    resource.setrlimit(kind, (soft, hard))


def apply_registered_limits(cap):
    current_soft, current_hard = resource.getrlimit(resource.RLIMIT_CPU)
    soft, hard = cap['cpu_seconds'], cap['hard_cpu_seconds']
    if type(soft) is not int or type(hard) is not int or hard < soft or soft <= 0:
        raise ValueError('authenticated CPU limits are invalid')
    if hard > FAMILY_HARD_CPU_SECONDS:
        raise ValueError('authenticated CPU hard limit exceeds unchanged family budget')
    if current_hard not in (-1, resource.RLIM_INFINITY) and hard > current_hard:
        raise ValueError('authenticated CPU limit would raise an inherited hard rlimit')
    if current_hard not in (-1, resource.RLIM_INFINITY):
        hard = min(hard, current_hard)
    if soft > hard:
        raise ValueError('authenticated extract CPU exceeds inherited or family hard CPU bound')
    resource.setrlimit(resource.RLIMIT_CPU, (soft, hard))
    _apply_authenticated_rlimit(
        resource.RLIMIT_AS, cap['memory_bytes'], cap['memory_bytes'], name='address-space')
    _apply_authenticated_rlimit(
        resource.RLIMIT_FSIZE, cap['maximum_output_file_bytes'], cap['maximum_output_file_bytes'],
        name='file-size')


def install_source_worker_signal_handlers():
    def handle(signum, frame):
        raise SourceWorkerInterrupt(f'source worker received signal {signum}')
    signal.signal(signal.SIGTERM, handle)
    signal.signal(signal.SIGINT, handle)


def authenticate_registered_packet(packet_path):
    sys.path[:0] = [str(ROOT / 'src'), str(ROOT)]
    packet = json.loads(checked(packet_path, maximum=2 * 1024**2)[0])
    protocol = json.loads(checked(PROTOCOL, packet['protocol_sha256'])[0])
    cap = limits(protocol, packet['configuration']['mode'])
    if packet['limits'] != cap:
        raise ValueError('registered source check resource limits changed')
    apply_registered_limits(cap)
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
    if packet['configuration']['mode'] in EXTRACT_MODES:
        from trading_research.research.auction_flow_production import declared_allocation
        limits_decl, plan_decl = declared_allocation(extension, packet['configuration']['mode'])
        from trading_research.research.auction_flow_production import resolve_declared_document, validate_production_limits
        if validate_production_limits(resolve_declared_document(limits_decl, load_reference=load_reference),
                protocol, mode=packet['configuration']['mode'],
                previous_study_output_bytes=packet['configuration']['previous_study_output_bytes']) != cap:
            raise ValueError('authenticated production limits differ from metadata-only registration')
        if (packet['configuration'].get('production_limits') != limits_decl
                or packet['configuration'].get('production_plan') != plan_decl):
            raise ValueError('production allocation/plan is absent or differs from the frozen extension')
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
                                  cohort_contract=None, compiled_projection=None):
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
                'compiled_projection': compiled_projection,
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
                'compiled_projection': compiled_projection,
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
            allocated_address_space_bytes=allocated, evidence=evidence,
            allowed_failure_exit_codes=(2,) if packet['configuration']['mode'] == 'throughput' else ())
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
                if packet['configuration']['mode'] != 'throughput' or child.get('exit_code') != 2:
                    raise ValueError('source unit failed; partial files retained')
                failure_path = directories[ordinal] / 'source-clock-failure.json'
                raw, sha = checked(failure_path, maximum=1024**2)
                failure = json.loads(raw)
                expected = {key: packet[key] for key in ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'configuration')}
                expected.update(ordinal=ordinal, child_pid=child['pid'], coordinator_pid=os.getpid(), unit=unit,
                    success=False, failure_kind='source_clock_integrity')
                if any(failure.get(key) != value for key, value in expected.items()):
                    raise ValueError('retained source failure does not join its parent and original unit')
                evidence.setdefault('retained_source_failures', []).append({'ordinal': ordinal, 'unit': unit,
                    'reference': {'path': str(failure_path), 'sha256': sha, 'size_bytes': len(raw)}, 'diagnostic': failure['diagnostic']})
                continue
            receipt_path = directories[ordinal] / 'artifacts' / 'source-unit-receipt.json'
            raw, _ = checked(receipt_path, maximum=min(
                cap['maximum_output_file_bytes'], planned['maximum_child_output_bytes']))
            receipt = json.loads(raw)
            require_joined_receipt(
                receipt, packet=packet, wait4_child=child, unit=unit, coordinator_pid=os.getpid())
            if compiled_projection is not None:
                if receipt.get('compiled_library') != compiled_projection['library']:
                    raise ValueError('child compiled source library does not join its coordinator')
                counter_ref = receipt.get('compiled_execution_counts')
                require_reference_in_namespace(counter_ref, directories[ordinal] / 'artifacts')
                counter = load_reference(counter_ref)
                if any(type(counter.get(key)) is not int or counter[key] <= 0 for key in ('fused_rows', 'compiled_quote_slice_calls', 'compiled_native_quote_calls')):
                    raise ValueError('held-out child did not execute all intended compiled source paths')
                evidence.setdefault('compiled_unit_execution', []).append({'ordinal': ordinal, 'library': receipt['compiled_library'], 'reference': counter_ref, 'counts': counter})
            reference = receipt['resource_unit']
            require_reference_in_namespace(reference, directories[ordinal] / 'artifacts')
            result = load_reference(reference, maximum=planned['maximum_child_output_bytes'])
            if result.get('unit') != unit:
                raise ValueError('source unit result identity changed')
            results.append(result)
            refs.append(reference)
        return results, refs
    finally:
        if packet['configuration']['mode'] in ('throughput', 'source-clock') and evidence:
            outputs.json('source-pool-checkpoint.json', evidence, kind='auction_flow_source_pool_checkpoint')
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


def source_clock_diagnostic(unit, *, maximum_rows):
    """Bounded timestamp-only diagnosis; preserves physical order and all rows."""
    import pyarrow.parquet as pq
    import pyarrow.compute as pc
    from trading_research.operations.artifacts import file_digest
    path = ROOT.parent / 'data' / unit['source_path']
    parquet = pq.ParquetFile(path)
    before = file_digest(path) if path.stat().st_size <= 64 * 1024**2 else None
    scanned, selected, previous, previous_address = 0, 0, None, None
    violations = []
    offsets, offset = {}, 0
    for group in range(parquet.num_row_groups):
        offsets[group] = offset
        offset += parquet.metadata.row_group(group).num_rows
    for group in unit['source_groups']:
        within = 0
        for batch in parquet.iter_batches(batch_size=65536, row_groups=[group], columns=['t'], use_threads=False):
            scanned += len(batch)
            if scanned > maximum_rows:
                raise ValueError('timestamp diagnosis exceeds the original source scan ceiling')
            values = batch.column(0).to_pylist()
            for number, value in enumerate(values):
                address = offsets[group] + within + number
                if value is None:
                    if len(violations) < 16:
                        violations.append({'kind': 'null_clock', 'source_row': address})
                    continue
                if not unit['event_start_ns'] <= value < unit['event_end_ns']:
                    continue
                selected += 1
                if previous is not None and value < previous and len(violations) < 16:
                    violations.append({'kind': 'backward_clock', 'previous_t': previous, 't': value,
                        'previous_source_row': previous_address, 'source_row': address,
                        'backward_ns': previous - value})
                previous, previous_address = value, address
            within += len(values)
            if len(violations) == 16:
                break
        if len(violations) == 16:
            break
    return {'unit': unit, 'timestamp_only_diagnostic': True, 'source_values_modified': False,
        'sorted_or_dropped_observations': False, 'physical_rows_scanned': scanned,
        'selected_timestamp_rows_examined': selected, 'first_up_to_16_violations': violations,
        'source_file_size': path.stat().st_size, 'small_file_sha256': before,
        'scope': 'Diagnostic only; no event-time/source-order reconciliation or scientific source exclusion admitted.'}


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
        windows = (source_clock_windows(authenticated, index) if packet['configuration']['mode'] == 'source-clock'
                   else throughput_windows(authenticated, index) if packet['configuration']['mode'] == 'throughput'
                   else resource_windows(protocol, index, calendar))
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
        compiled = child.get('compiled_projection')
        if packet['configuration']['mode'] in ('throughput', 'source-clock'):
            if not compiled:
                raise ValueError('compiled source backend required for throughput')
            reference = compiled['library']
            expected_library = Path(registered_packet_path).parent / 'outputs' / 'compact-projection.so'
            if Path(reference['path']).resolve() != expected_library.resolve():
                raise ValueError('compiled source library escaped its registered coordinator outputs')
            raw, _ = checked(expected_library, reference['sha256'], maximum=cap['maximum_output_file_bytes'])
            if len(raw) != reference['size_bytes']:
                raise ValueError('compiled source library size changed')
            from trading_research.data.compact_native import enable_compiled_projection
            enable_compiled_projection(expected_library, reference['sha256'])
        result, resource_ref = measured_unit(
            unit, protocol=protocol, index=index, coordinates=coordinates, outputs=outputs,
            data_root=ROOT.parent / 'data', storage_encoding='structural',
            anchor_calendar=None if packet['configuration']['mode'] in ('throughput', 'source-clock') else calendar,
            cohort_contract=None if packet['configuration']['mode'] in ('throughput', 'source-clock') else authenticated['extension'].get('cohort_validation'),
            quote_storage=authenticated['extension'].get('quote_storage', 'parquet'),
            source_clock_policy=authenticated['extension']['source_clock_policy'] if packet['configuration']['mode'] == 'source-clock' else None)
        counter_ref = None
        if packet['configuration']['mode'] in ('throughput', 'source-clock'):
            from trading_research.data.compact_native import execution_counts
            counts = execution_counts()
            if counts['fused_rows'] <= 0 or (result['counts']['quote_rows'] and (counts['compiled_quote_slice_calls'] <= 0 or counts['compiled_native_quote_calls'] <= 0)):
                raise ValueError('compiled source projection did not execute on held-out data')
            counter_ref = outputs.json('compiled-execution-counts.json', counts, kind='compiled_source_execution_counts')
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
            'compiled_library': None if compiled is None else compiled['library'],
            'compiled_execution_counts': counter_ref,
        }, kind='auction_flow_source_unit_receipt')
        return 0
    except BaseException as exc:
        if ('authenticated' in locals() and 'unit' in locals()
                and packet['configuration']['mode'] == 'throughput'
                and type(exc).__name__ == 'IntegrityError'
                and str(exc) == 'source event order/null clock requires separate resolution'):
            from trading_research.operations.artifacts import canonical_json, publish_new
            failure = {key: packet[key] for key in ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'configuration')}
            failure.update(ordinal=child['ordinal'], child_pid=os.getpid(), coordinator_pid=os.getppid(), unit=unit,
                success=False, failure_kind='source_clock_integrity',
                diagnostic=source_clock_diagnostic(unit, maximum_rows=protocol['resources']['maximum_source_day_scan_rows']))
            payload = canonical_json(failure) + b'\n'
            if len(payload) > 1024**2:
                raise ValueError('source failure receipt exceeds its bounded output allowance')
            publish_new(expected_dir / 'source-clock-failure.json', payload)
            print('AUCTION_FLOW_SOURCE_CLOCK_FAILURE ' + json.dumps({'ordinal': child['ordinal'], 'unit': unit}), flush=True)
            return 2
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
        if any(name not in protocol['check_modules'] + authenticated['extension']['additional_check_modules'] for name in modules):
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
        from trading_research.data.compact_native import execution_counts
        compiled_before = execution_counts()
        result, reference = measured_unit(unit, protocol=protocol, index=index, coordinates=coordinates[unit['root']],
            outputs=outputs, data_root=ROOT.parent / 'data', storage_encoding='structural',
            diagnostic_profiler=profiler if unit == selected[0] else None,
            quote_storage=authenticated['extension'].get('quote_storage', 'parquet'))
        if compiled_projection is not None and benchmark:
            compiled_after = execution_counts()
            delta = {key: compiled_after[key] - compiled_before[key] for key in compiled_after}
            if result['counts']['quote_rows'] and (delta['compiled_quote_slice_calls'] == 0 or delta['compiled_native_quote_calls'] == 0):
                raise ValueError('compiled quote/native fusion did not execute on this complete source unit')
            compiled_projection.setdefault('per_unit_execution', []).append({'unit': unit, 'counts': delta})
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
                    coordinates=coordinates[result['unit']['root']], outputs=outputs, data_root=ROOT.parent / 'data',
                    quote_storage=authenticated['extension'].get('quote_storage', 'parquet'))
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
        if benchmark and (compiled_projection['compiled_quote_slice_calls'] == 0 or compiled_projection['compiled_native_quote_calls'] == 0):
            raise ValueError('compiled quote and native fusion must execute on the registered population')
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


def throughput_windows(authenticated, index):
    """Reconstruct each frozen held-out window from the admitted source index."""
    from trading_research.data.reconcile import select_groups
    from trading_research.operations.artifacts import digest
    protocol = authenticated['protocol']
    declared = authenticated['extension']['throughput_windows']
    if len(declared) != 17 or len({w['source_path'] for w in declared}) != 17:
        raise ValueError('throughput requires all 17 distinct declared physical sources')
    result = []
    for value in declared:
        if value['event_end_ns'] - value['event_start_ns'] != 86_400_000_000_000 or not value['whole_window_inside_acquired_file']:
            raise ValueError('complete held-out UTC day required')
        records = [record for record in index['datasets'][value['dataset']] if record['path'] == value['source_path']]
        if len(records) != 1:
            raise ValueError('held-out explicit source is missing or duplicated')
        restricted = {**index, 'datasets': {**index['datasets'], value['dataset']: records}}
        if (value['event_start_ns'] % 86_400_000_000_000
                or min(group['minimum'] for group in records[0]['groups']) > value['event_start_ns']
                or max(group['maximum'] for group in records[0]['groups']) < value['event_end_ns']):
            raise ValueError('held-out complete UTC window lacks authenticated file containment')
        selected, _ = select_groups(restricted, dataset=value['dataset'], start=value['event_start_ns'],
            end=value['event_end_ns'], max_scan_rows=protocol['resources']['maximum_source_day_scan_rows'])
        matched = [(record, groups) for record, groups in selected if record['path'] == value['source_path']]
        if len(matched) != 1:
            raise ValueError('held-out source is absent or ambiguous')
        record, groups = matched[0]
        if digest(record) != value['source_metadata_sha256'] or list(groups) != value['source_groups']:
            raise ValueError('held-out source metadata or row groups changed')
        result.append({'root': value['root'], 'role': 'independent_full_day_throughput_cost',
            'cash_date': None, 'event_start_ns': value['event_start_ns'], 'event_end_ns': value['event_end_ns'],
            'source_path': record['path'], 'source_metadata_version': digest(record), 'source_groups': groups,
            'calendar_version': None, 'source_variant': hashlib.sha256(record['path'].encode()).hexdigest()[:12],
            'coverage_basis': 'Explicitly initialized observed prefix of one retained physical source; no inferred pre-window book coverage. Full UTC day cost holdout, not complete annual family validation.'})
    return result


def source_clock_windows(authenticated, index):
    extension = authenticated['extension']
    records = load_reference(extension['source_clock_neighbor_records'])
    if len(records) != 5:
        raise ValueError('source-clock check requires the original five audited failures')
    all_windows = throughput_windows(authenticated, index)
    keys = {(r['unit']['source_path'], r['unit']['event_start_ns'], r['unit']['event_end_ns']) for r in records}
    windows = [u for u in all_windows if (u['source_path'], u['event_start_ns'], u['event_end_ns']) in keys]
    if len(keys) != 5 or len(windows) != 5:
        raise ValueError('source-clock failure identities no longer join the frozen holdout')
    return windows


def check_source_clock(authenticated, packet_path, worker_started):
    import unittest
    from trading_research.research.auction_flow_storage import BoundedOutputs
    from trading_research.operations.artifacts import canonical_json, digest, publish_new
    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    extension = authenticated['extension']
    audit = load_reference(extension['source_clock_audit_worker'])
    audit_execution = load_reference(extension['source_clock_audit_execution'])
    if (audit.get('success') is not True or audit_execution.get('success') is not True
            or audit_execution.get('within_declared_limits') is not True
            or audit_execution.get('worker_identity_joined') is not True
            or audit_execution['attempt_id'] != audit['attempt_id']
            or audit_execution['worker_report']['sha256'] != digest(audit)
            or any(audit['clock_neighbor_records'].get(k) != extension['source_clock_neighbor_records'].get(k) for k in ('path', 'sha256', 'size_bytes'))
            or audit['source_clock_failure_count'] != 5 or len(audit['completed_source_units']) != 12):
        raise ValueError('source-clock check lost its successful retained original-record audit')
    for row in audit['completed_source_units']:
        for key in ('receipt', 'resource_unit', 'compiled_execution_counts'):
            load_reference(row[key])
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs',
        maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'],
        maximum_file_bytes=cap['maximum_output_file_bytes'])
    compiled = compile_source_projection(packet_path, outputs)
    modules = extension['benchmark_check_modules']
    if any(name not in protocol['check_modules'] + extension['additional_check_modules'] for name in modules):
        raise ValueError('focused clock tests must belong to the registered family')
    started = time.process_time()
    tested = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    test_report = dict(tests=tested.testsRun, failures=len(tested.failures), errors=len(tested.errors),
        success=tested.wasSuccessful(), cpu_seconds=time.process_time() - started, modules=modules)
    if not tested.wasSuccessful():
        raise ValueError('source-clock regression checks failed; do not scan further')
    index = load_reference(protocol['source_index'])
    windows = source_clock_windows(authenticated, index)
    evidence = {}
    results, references = execute_source_units_parallel(windows, protocol=protocol, index=index,
        coordinates=None, outputs=outputs, data_root=ROOT.parent / 'data', calendar=None,
        packet_path=packet_path, packet=packet, planned=authenticated['registered_plan'],
        concurrency=authenticated['concurrency'], cap=cap, worker_started=worker_started,
        evidence=evidence, compiled_projection=compiled)
    if len(results) != 5 or any(r['actual_reference']['passed'] is not True for r in results):
        raise ValueError('source-clock check requires all five complete current-policy source results')
    from trading_research.research.auction_flow_storage import read_series_tables
    audited = {row['timestamp_diagnostic']['unit']['source_path']: row
               for row in load_reference(extension['source_clock_neighbor_records'])}
    for result in results:
        expected = audited[result['unit']['source_path']]
        violation = expected['timestamp_diagnostic']['first_up_to_16_violations'][0]
        original = next(row for row in expected['unchanged_all_field_neighbor_records']
                        if row['source_row'] == violation['source_row'])
        replayed = [row for table in read_series_tables(result['event_storage']['replayed_snapshots'])
                    for row in table.to_pylist()]
        if (len(replayed) != 1 or result['counts']['disposed_snapshot_rows'] != 1
                or result['source_manifest']['source_clock_policy'] != extension['source_clock_policy']
                or replayed[0]['source_row'] != original['source_row']
                or replayed[0]['predecessor_source_row'] != violation['previous_source_row']
                or any(replayed[0][name] != value for name, value in original['record'].items())):
            raise ValueError('clock disposition must reproduce exactly the audited original snapshot')
    report = {key: packet[key] for key in ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration')}
    report.update(family=protocol['family'], mode='source-clock', success=True,
        source_component_verified=True, complete_family_statistics=False,
        tests=test_report, compiled_projection=compiled, runtime_versions=authenticated['versions'],
        resource_units=references, source_unit_parallel_execution=evidence,
        source_clock_policy=extension['source_clock_policy'], source_clock_contract=extension['source_clock_contract'],
        retained_source_audit=extension['source_clock_audit_worker'],
        reused_strict_source_units=audit['completed_source_units'], completed_changed_source_units=len(results),
        derived_output_bytes=outputs.written,
        scope=extension['source_clock_check_scope'])
    publish_new(Path(packet['worker_report']), canonical_json(report) + b'\n')
    return 0


def throughput_source(authenticated, packet_path, worker_started):
    from trading_research.foundations.cash_calendar import CashCalendar
    from trading_research.research.auction_flow_storage import BoundedOutputs
    from trading_research.operations.artifacts import canonical_json, publish_new
    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    extension = authenticated['extension']
    index = load_reference(protocol['source_index'])
    windows = throughput_windows(authenticated, index)
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs',
        maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'],
        maximum_file_bytes=cap['maximum_output_file_bytes'])
    from trading_research.research.auction_flow_downstream import join_prior_identity
    prior = load_reference(extension['throughput_calibration_worker'])
    prior_execution = load_reference(extension['throughput_calibration_execution'])
    joined = join_prior_identity(prior, prior_execution, {
        'downstream_prior_worker': extension['throughput_calibration_worker'],
        'downstream_prior_execution': extension['throughput_calibration_execution'],
        'parent_protocol_sha256': packet['protocol_sha256']})
    if joined['runtime_versions'] != authenticated['versions']:
        raise ValueError('held-out calibration runtime changed')
    dependencies = prior['configuration']['verified_component']['dependencies']
    if any(packet['code_manifest'].get(name) != sha for name, sha in dependencies.items() if name.startswith('src/')):
        raise ValueError('held-out calibration source implementation changed')
    calibration_units = [load_reference(ref) for ref in joined['resource_units']]
    if any(u['event_storage']['quotes'].get('encoding') != 'raw-source-quote-replay-v1' for u in calibration_units):
        raise ValueError('calibration uses a different quote representation')
    compiled = compile_source_projection(packet_path, outputs)
    evidence = {}
    results, references = execute_source_units_parallel(windows, protocol=protocol, index=index,
        coordinates=None, outputs=outputs, data_root=ROOT.parent / 'data', calendar=None,
        packet_path=packet_path, packet=packet, planned=authenticated['registered_plan'],
        concurrency=authenticated['concurrency'], cap=cap, worker_started=worker_started,
        evidence=evidence, compiled_projection=compiled)
    frozen = prior['actual_source_preflight']['source_cost_projection']
    rates = frozen['cpu_coefficients']
    comparisons = []
    for result in results:
        counts = next(row for row in extension['throughput_windows'] if row['source_path'] == result['unit']['source_path'])
        instruments = counts['raw_instruments_per_window_upper']
        prospective = {**counts, 'source_windows': 1,
            'instrument_window_allocations_upper': instruments,
            'instrument_atomic_cells_upper': instruments * counts['atomic_cells_per_instrument'],
            'instrument_native_cells_upper': counts['native_instrument_cells_upper'],
            'atomic_parts_per_consumer_upper': instruments * (counts['atomic_cells_per_instrument'] + counts['reader_batches_upper'])}
        allowance = 1.5 * sum(rate['cpu_seconds_per_work_unit'] * prospective[rate['prospective_count_field']] for rate in rates.values())
        pipeline = result['pipeline_cpu_components']
        actual = (sum(pipeline[key] for key in ('initialization', 'instrument_allocation', 'scan_and_consumers', 'finalization_and_native_storage'))
            - result['scan_cpu_components_disjoint']['reference_sample_collection']
            - result['native_reference_sample_collection_cpu_seconds']
            + result['event_storage_finalization_cpu_seconds'] + result.get('quote_replay_validation_cpu_seconds', 0)
            + result['measurement_json_serialization_cpu_seconds'])
        bounds = (result['raw_physical_rows'] <= counts['physical_scan_rows']
            and result['source_manifest']['physical_reader_batches'] <= counts['reader_batches_upper']
            and result['native_cells'] <= counts['native_instrument_cells_upper'])
        if not bounds:
            raise ValueError('held-out source exceeds frozen metadata allocation bounds')
        comparisons.append({'unit': result['unit'], 'source_stage_cpu_seconds': actual,
            'frozen_allowance_cpu_seconds': allowance, 'within_frozen_allowance': actual <= allowance,
            'allocation_bounds_passed': bounds,
            'quote_descriptor_bytes': result['event_storage']['quotes']['serialized_bytes']})
        source, scan, pipe = result['source_manifest']['source_cpu_components'], result['scan_cpu_components_disjoint'], result['pipeline_cpu_components']
        quotes = result['event_storage']['quotes']
        actual_components = {name: source[name] for name in ('source_metadata_and_open', 'physical_batch_decode', 'physical_address_and_selection', 'selected_projection')}
        actual_components.update({name: scan[name] for name in ('native_source_ownership', 'time_at_price_consumers', 'whole_trade_and_native_consumers', 'event_storage', 'raw_atomic_batch_reduction', 'raw_atomic_counter_updates', 'trade_atomic_consumers', 'quote_atomic_consumers')})
        replay = result['quote_replay_validation_cpu_seconds']
        fixed_replay = quotes['quote_replay_metadata_cpu_seconds'] if result['source_manifest']['physical_reader_batches'] else replay
        actual_components.update(scan_dispatch_and_manifest=max(0.0, scan['source_decode_and_projection'] - sum(source.values())) + scan['unassigned_scan_routing'],
            initialization_and_carry=pipe['initialization'], native_array_allocation=pipe['instrument_allocation'],
            finalization_and_native_storage=pipe['finalization_and_native_storage'] - result['native_reference_sample_collection_cpu_seconds'],
            tail_event_storage=result['event_storage_finalization_cpu_seconds'], exact_measurement_serialization=result['measurement_json_serialization_cpu_seconds'],
            quote_replay_validation=max(0.0, replay - fixed_replay), quote_replay_metadata_and_dispatch=fixed_replay)
        component_allowances = {name: 1.5 * rate['cpu_seconds_per_work_unit'] * prospective[rate['prospective_count_field']] for name, rate in rates.items()}
        component_checks = {name: {'actual_cpu_seconds': value, 'allowance_cpu_seconds': component_allowances[name], 'passed': value <= component_allowances[name]}
            for name, value in actual_components.items()}
        # This separately frozen empirical envelope models both slice overhead
        # and quote-row work; it does not alter calculation or coverage scope.
        envelope = extension['quote_cost_envelope']
        quote_allowance = 1.5 * (envelope['cpu_seconds_per_slice'] * prospective['atomic_parts_per_consumer_upper']
            + envelope['cpu_seconds_per_quote_row'] * prospective['selected_raw_rows_upper'])
        component_checks['quote_atomic_dual_count_envelope'] = {'actual_cpu_seconds': scan['quote_atomic_consumers'],
            'allowance_cpu_seconds': quote_allowance, 'passed': scan['quote_atomic_consumers'] <= quote_allowance}
        quote_adjusted_allowance = allowance - component_allowances['quote_atomic_consumers'] + quote_allowance
        workload = result['workload_counts']
        observed_ids = {row['instrument_id'] for row in result['instrument_quality']}
        additional_bounds = (result['counts']['raw_rows'] <= prospective['selected_raw_rows_upper']
            and workload['raw_instrument_batches'] <= prospective['instrument_batches_upper']
            and workload['instrument_atomic_cells'] <= prospective['instrument_atomic_cells_upper']
            and observed_ids <= set(counts['raw_instrument_allocation_ids_upper'])
            and all(workload[key] <= prospective['atomic_parts_per_consumer_upper'] for key in ('raw_atomic_parts', 'quote_atomic_parts', 'trade_atomic_parts')))
        if not additional_bounds:
            raise ValueError('held-out source consumer population exceeds its frozen count bounds')
        output_pairs = {
            'native': (sum(x['serialized_bytes'] for x in result['native_storage']), 1.5 * frozen['native_bytes_per_cell_max'] * prospective['instrument_native_cells_upper']),
            'measurement': (result['measurement']['size_bytes'], 1.5 * frozen['compressed_json_bytes_per_atomic_cell_max'] * prospective['instrument_atomic_cells_upper']),
            'quote_descriptor': (quotes['serialized_bytes'], 1.5 * frozen['quote_replay_descriptor_bytes_per_source_window_max'])}
        for kind in ('trades', 'excluded'):
            rate = frozen['event_output_rates'][kind]
            output_pairs[kind] = (result['event_storage'][kind]['serialized_bytes'], None if rate['bytes_per_actual_event_max'] is None else
                1.5 * prospective['selected_raw_rows_upper'] * rate['actual_rows_per_selected_raw_max'] * rate['bytes_per_actual_event_max'])
        output_checks = {name: {'actual_bytes': pair[0], 'allowance_bytes': pair[1], 'passed': None if pair[1] is None else pair[0] <= pair[1]}
            for name, pair in output_pairs.items()}
        comparisons[-1].update(component_checks=component_checks, output_checks=output_checks,
            quote_adjusted_source_allowance_cpu_seconds=quote_adjusted_allowance,
            within_quote_adjusted_source_allowance=actual <= quote_adjusted_allowance,
            all_measured_output_bounds_passed=all(row['passed'] is not False for row in output_checks.values()),
            all_component_allowances_passed=all(row['passed'] for row in component_checks.values()))
    average_cores = evidence['pool_child_wait4_cpu_seconds'] / evidence['wall_seconds']
    report = {key: packet[key] for key in ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration')}
    report.update(family=protocol['family'], mode='throughput', success=not evidence.get('retained_source_failures'),
        source_component_verified=False, complete_family_statistics=False,
        completed_source_units=len(results), declared_source_units=len(windows),
        source_clock_failures=evidence.get('retained_source_failures', []),
        compiled_projection=compiled, runtime_versions=authenticated['versions'],
        resource_units=references, source_unit_parallel_execution=evidence,
        held_out_calibration=comparisons,
        all_held_out_source_costs_within_frozen_allowance=all(r['within_frozen_allowance'] for r in comparisons),
        all_held_out_component_allowances_passed=all(r['all_component_allowances_passed'] for r in comparisons),
        all_held_out_measured_output_bounds_passed=all(r['all_measured_output_bounds_passed'] for r in comparisons),
        actual_average_busy_cpu_cores=average_cores,
        effective_cpu_utilization=average_cores / min(21.0, authenticated['live']['cpu_quota_us'] / authenticated['live']['cpu_period_us']) ,
        derived_output_bytes=outputs.written,
        scope='17 independent complete UTC source windows with source/native/measurement calculations and exact verified quote replay. Actual source throughput holdout; no all-family, Context or Location completion.')
    publish_new(Path(packet['worker_report']), canonical_json(report) + b'\n')
    return 0 if report['success'] else 1


def audit_nan_failures(authenticated, packet_path):
    """Read original failed terminal rows and reproduce one complete window per root."""
    import math
    import struct
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    from trading_research.operations.artifacts import canonical_json, publish_new
    from trading_research.research.auction_flow_storage import BoundedOutputs, read_json_artifact
    from trading_research.research.auction_flow_pipeline import measure_raw_window
    from trading_research.research.auction_flow_coordinates import RetainedCoordinateIndex
    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    extension = authenticated['extension']
    previous = load_reference(extension['nan_failure_worker'])
    execution = load_reference(extension['nan_failure_execution'])
    if previous['attempt_id'] != execution['attempt_id'] or execution['protocol_sha256'] != packet['protocol_sha256']:
        raise ValueError('NaN evidence identity changed')
    failures = {}
    for failure in previous['failures']:
        if failure.get('error') == 'ValueError: Out of range float values are not JSON compliant: nan':
            unit = failure['unit']
            failures[(unit['source_path'], unit['event_start_ns'])] = failure
    if len(failures) != 33:
        raise ValueError('original 33 distinct NaN failures required')
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs', maximum_total_bytes=cap['maximum_output_bytes']-cap['supervisor_output_reserve_bytes'], maximum_file_bytes=cap['maximum_output_file_bytes'])
    compiled = compile_source_projection(packet_path, outputs)
    def exact(value):
        if isinstance(value, dict):
            return {k: exact(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [exact(v) for v in value]
        if type(value) is float and not math.isfinite(value):
            return {'$float64_bits_le': struct.pack('<d', value).hex()}
        return value
    records = []
    for failure in failures.values():
        unit = failure['unit']; path = ROOT.parent / 'data' / unit['source_path']
        stamp = (path.stat().st_size, path.stat().st_mtime_ns)
        parquet = pq.ParquetFile(path); offsets = []; total = 0
        for group in range(parquet.num_row_groups):
            offsets.append(total); total += parquet.metadata.row_group(group).num_rows
        scanned = 0; terminal = None
        for group in reversed(unit['source_groups']):
            table = parquet.read_row_group(group, use_threads=False); scanned += len(table)
            if scanned > unit['physical_scan_rows']:
                raise ValueError('terminal audit exceeded original scan bound')
            selected = pc.indices_nonzero(pc.and_(pc.greater_equal(table['t'], unit['event_start_ns']), pc.less(table['t'], unit['event_end_ns'])))
            if len(selected):
                row = selected[-1].as_py(); terminal = table.slice(row, 1).to_pylist()[0]
                address = offsets[group] + row; break
        if terminal is None or stamp != (path.stat().st_size, path.stat().st_mtime_ns):
            raise ValueError('original terminal row absent or source changed')
        nonfinite = [k for k, v in terminal.items() if type(v) is float and not math.isfinite(v)]
        records.append({'unit_identity': failure['unit_identity'], 'source_row': address, 'row_group': group, 'terminal_original_fields': exact(terminal), 'nonfinite_fields': nonfinite, 'physical_rows_scanned': scanned, 'source_stamp': list(stamp)})
    terminal_ref = outputs.json('original-nan-terminal-records.json', records, kind='auction_flow_original_nan_terminal_audit')
    index = load_reference(protocol['source_index'])
    catalog = load_reference(extension['prior_production_receipt_catalog'])['receipts']
    reproductions = []; roots = set()
    for failure in failures.values():
        unit = failure['unit']; symbol = unit['root']
        if symbol in roots:
            continue
        roots.add(symbol)
        suffix = f"{symbol}-{unit['event_start_ns']-86400000000000}-{failure['unit_identity']['source_variant']}-window-receipt.json"
        references = [r for r in catalog if r['path'].endswith(suffix)]
        if len(references) != 1:
            raise ValueError('unique authenticated preceding window required')
        receipt = load_reference(references[0])
        if receipt['unit']['event_end_ns'] != unit['event_start_ns'] or receipt['unit']['source_path'] != unit['source_path']:
            raise ValueError('preceding carry does not join original failed window')
        carry = read_json_artifact(receipt['artifacts']['continuation'])['measurement_continuation']
        coordinate_ref = protocol['coordinate_admissions'][symbol]
        coordinates = RetainedCoordinateIndex(load_reference(coordinate_ref), source_version=coordinate_ref['sha256'], snapshot_supplement=load_reference(protocol['nq_snapshot_supplement']) if symbol == 'NQ' else None, snapshot_version=protocol['nq_snapshot_supplement']['sha256'] if symbol == 'NQ' else None)
        began = time.process_time()
        try:
            measure_raw_window(data_root=ROOT.parent/'data', index=index, coordinates=coordinates, root=symbol, start_ns=unit['event_start_ns'], end_ns=unit['event_end_ns'], source_paths=(unit['source_path'],), continuation=carry, maximum_scan_rows=protocol['resources']['maximum_source_day_scan_rows'], native_width_ns=protocol['native_width_ns'], atomic_width_ns=protocol['atomic_width_ns'], maximum_native_array_bytes=protocol['resources']['maximum_native_array_bytes'], source_clock_policy=extension['source_clock_policy'])
        except ValueError as error:
            trace = error.__traceback__; captured = None
            while trace is not None:
                if trace.tb_frame.f_code.co_name == 'carry' and trace.tb_frame.f_code.co_filename.endswith('/auction_flow_data.py'):
                    captured = exact(trace.tb_frame.f_locals['result'])
                trace = trace.tb_next
            if captured is None or str(error) != 'Out of range float values are not JSON compliant: nan':
                raise
            reproductions.append({'unit_identity': failure['unit_identity'], 'prior_receipt': references[0], 'cpu_seconds': time.process_time()-began, 'error': f'{type(error).__name__}: {error}', 'traceback': traceback.format_exc(), 'source_carry_at_failure': captured})
        else:
            raise ValueError('original NaN failure did not reproduce')
    reproduction_ref = outputs.json('original-nan-full-window-reproductions.json', reproductions, kind='auction_flow_original_nan_reproduction')
    report = {key: packet[key] for key in ('attempt_id','trial_id','protocol_sha256','code_snapshot','tools_snapshot','configuration')}
    report.update(family=protocol['family'], mode='clock-audit', success=all(r['nonfinite_fields'] for r in records) and len(reproductions)==2, runtime_versions=authenticated['versions'], terminal_records=terminal_ref, reproduced_failures=reproduction_ref, audited_nan_windows=len(records), reproduced_complete_windows=len(reproductions), compiled_projection=compiled, derived_output_bytes=outputs.written, source_component_verified=False, full_project_under_three_hours_verified=False, scope='Original failure diagnosis only; no repair or performance success claim.')
    publish_new(Path(packet['worker_report']), canonical_json(report)+b'\n')
    return 0 if report['success'] else 1


def audit_clock_records(authenticated, packet_path):
    import pyarrow.parquet as pq
    from trading_research.research.auction_flow_storage import BoundedOutputs
    from trading_research.operations.artifacts import canonical_json, publish_new
    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    prior_ref = authenticated['extension']['throughput_observed_execution']
    observed = load_reference(prior_ref)
    if (observed['protocol_sha256'] != packet['protocol_sha256'] or observed['success'] is not False
            or observed['mode'] != 'throughput' or observed['cpu_accounting_complete'] is not True
            or observed['within_declared_limits'] is not True):
        raise ValueError('clock audit requires its retained bounded partial throughput attempt')
    prior_dir = Path(prior_ref['path']).parent
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs', maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'], maximum_file_bytes=cap['maximum_output_file_bytes'])
    records, completed = [], []
    for folder in sorted((prior_dir / 'outputs').glob('source-unit-*')):
        child = json.loads(checked(folder / 'packet.json', maximum=1024**2)[0])
        if child['attempt_id'] != observed['attempt_id'] or child['configuration'] != observed['configuration'] or child['code_snapshot'] != observed['code_snapshot']:
            raise ValueError('retained child packet differs from its bounded partial execution')
        failure_path, receipt_path = folder / 'source-clock-failure.json', folder / 'artifacts/source-unit-receipt.json'
        if failure_path.exists():
            raw, sha = checked(failure_path, maximum=1024**2)
            failure = json.loads(raw)
            if failure['unit'] != child['unit'] or failure['attempt_id'] != child['attempt_id'] or failure['ordinal'] != child['ordinal'] or failure['success'] is not False:
                raise ValueError('retained source failure identity differs')
            unit = failure['unit']
            parquet = pq.ParquetFile(ROOT.parent / 'data' / unit['source_path'])
            offsets, at = [], 0
            for group in range(parquet.num_row_groups):
                offsets.append(at)
                at += parquet.metadata.row_group(group).num_rows
            wanted = {row for issue in failure['diagnostic']['first_up_to_16_violations']
                for anchor in (issue.get('previous_source_row', issue['source_row']), issue['source_row'])
                for row in range(max(0, anchor - 2), min(at, anchor + 3))}
            rows, read_groups = [], []
            for group, start in enumerate(offsets):
                stop = start + parquet.metadata.row_group(group).num_rows
                selected = sorted(row for row in wanted if start <= row < stop)
                if not selected:
                    continue
                table = parquet.read_row_group(group, use_threads=False)
                read_groups.append(group)
                for row in selected:
                    rows.append({'source_row': row, 'row_group': group, 'record': table.slice(row - start, 1).to_pylist()[0]})
            records.append({'unit': unit, 'original_failure_reference': {'path': str(failure_path), 'sha256': sha, 'size_bytes': len(raw)},
                'timestamp_diagnostic': failure['diagnostic'], 'read_groups': read_groups, 'unchanged_all_field_neighbor_records': rows})
        elif receipt_path.exists():
            raw, sha = checked(receipt_path, maximum=1024**2)
            receipt = json.loads(raw)
            if receipt['success'] is not True or receipt['unit'] != child['unit'] or receipt['attempt_id'] != child['attempt_id']:
                raise ValueError('completed child source receipt identity differs')
            require_reference_in_namespace(receipt['resource_unit'], folder / 'artifacts')
            resource_unit = load_reference(receipt['resource_unit'])
            require_reference_in_namespace(receipt['compiled_execution_counts'], folder / 'artifacts')
            counters = load_reference(receipt['compiled_execution_counts'])
            if any(counters[key] <= 0 for key in ('fused_rows', 'compiled_quote_slice_calls', 'compiled_native_quote_calls')):
                raise ValueError('completed child did not execute its compiled source paths')
            completed.append({'ordinal': child['ordinal'], 'unit': child['unit'],
                'receipt': {'path': str(receipt_path), 'sha256': sha, 'size_bytes': len(raw)},
                'resource_unit': receipt['resource_unit'], 'compiled_execution_counts': receipt['compiled_execution_counts'],
                'source_result_passed_before_coordinator_summary_failure': True})
        else:
            raise ValueError('partial throughput child has no completed result or explicit source failure')
    if len(records) + len(completed) != 17:
        raise ValueError('clock audit must account for all original17held-out windows')
    detail = outputs.json('clock-neighbor-records.json', records, kind='auction_flow_clock_neighbor_record_audit')
    report = {key: packet[key] for key in ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration')}
    report.update(family=protocol['family'], mode='clock-audit', success=True, source_component_verified=False,
        runtime_versions=authenticated['versions'], derived_output_bytes=outputs.written,
        audited_execution=prior_ref, completed_source_units=completed, source_clock_failure_count=len(records),
        clock_neighbor_records=detail, retained_original_window_count=17,
        observed_attempt_cpu_seconds=observed['cpu_seconds'], observed_attempt_wall_seconds=observed['wall_seconds'],
        observed_average_busy_cores=observed['cpu_seconds'] / observed['wall_seconds'],
        observed_allocation_utilization=observed['cpu_seconds'] / observed['wall_seconds'] / 17.85,
        scope='All-field read-only diagnosis of five retained source-clock failures and identity audit of twelve completed children. Partial throughput scope retained; missing per-child wait4/pool checkpoint not reconstructed. No sorting, dropping, source exclusion, clock repair, full source acceptance or end-to-end ETA admitted.')
    publish_new(Path(packet['worker_report']), canonical_json(report) + b'\n')
    return 0


def extract_check_modules(protocol, extension):
    declared = extension.get('extract_check_modules')
    default = ['tests.test_auction_flow_production']
    if not declared:
        return default
    if (not isinstance(declared, list) or not declared or len(set(declared)) != len(declared)):
        raise ValueError('extract-check modules must be an explicit unique list')
    admitted = set(protocol['check_modules'] + extension.get('additional_check_modules', []) + default)
    if any(name not in admitted for name in declared):
        raise ValueError('extract-check tests must belong to the retained family or production tests')
    return declared


def load_production_schedule(plan):
    from trading_research.research.auction_flow_production import resolve_production_schedule
    return resolve_production_schedule(plan, load_reference=load_reference)



def order_source_file_jobs(jobs, chains, plan):
    """Dispatch independent files by declared work; original identities stay fixed."""
    import math
    require_complete_ordinals([job['ordinal'] for job in jobs])
    if len(jobs) != len(chains):
        raise ValueError('dispatch jobs and complete file chains differ')
    strategy = plan.get('dispatch_strategy', 'file_ordinal')
    if strategy == 'file_ordinal':
        return sorted(jobs, key=lambda job: job['ordinal'])
    if strategy != 'largest_declared_file_first_v1':
        raise ValueError('unknown declared file dispatch strategy')
    records = {(row['root'], row['source_path'], row['source_metadata_sha256']): row
               for row in plan['files']}
    if len(records) != len(plan['files']):
        raise ValueError('duplicate file dispatch weights')
    weights = {}
    for ordinal, chain in enumerate(chains):
        row = records.get((chain['root'], chain['source_path'], chain['source_metadata_sha256']))
        weight = None if row is None else row.get('dispatch_work_weight')
        if type(weight) not in (int, float) or not math.isfinite(weight) or weight < 0:
            raise ValueError('each file requires a finite nonnegative declared dispatch weight')
        weights[ordinal] = weight
    return sorted(jobs, key=lambda job: (-weights[job['ordinal']], job['ordinal']))


def execute_source_files_parallel(chains, *, plan, packet_path, packet, planned, concurrency, cap,
                                  worker_started, evidence, outputs, compiled_projection,
                                  prior_receipts_by_file=None):
    from trading_research.operations.artifacts import canonical_json
    from trading_research.research.auction_flow_production import (
        file_identity, production_window_identity)

    reservations = []
    lookup = {(row['root'], row['source_path'], row['source_metadata_sha256']): row['maximum_output_bytes']
              for row in plan['files']}
    for chain in chains:
        key = (chain['root'], chain['source_path'], chain['source_metadata_sha256'])
        if key not in lookup:
            raise ValueError('reconstructed file chain has no frozen per-file reservation')
        reservations.append(lookup[key])
    reserved = require_file_output_reservations(
        reservations, outputs.maximum_total - outputs.written,
        coordinator_reserve_bytes=0)
    allocation = actual_source_unit_allocation(planned, len(chains), concurrency_limit=concurrency)
    concurrency = allocation['actual_concurrency']
    allocated = allocation['allocated_address_space_bytes']
    runner = str(Path(__file__).resolve())
    registered = str(Path(packet_path).resolve())
    jobs, directories, charged = [], [], False
    prior_receipts_by_file = prior_receipts_by_file or {}
    try:
        for ordinal, chain in enumerate(chains):
            expected_dir, expected_packet = require_source_file_namespace(
                attempt_id=packet['attempt_id'], ordinal=ordinal,
                child_packet_path=outputs.directory / f'source-file-{ordinal:03d}' / 'packet.json',
                output_directory=outputs.directory / f'source-file-{ordinal:03d}',
                runs_root=RUNS)
            expected_dir.mkdir(parents=False, exist_ok=False)
            directories.append(expected_dir)
            child_packet = {
                'kind': 'auction_flow_source_file_packet_v1',
                'registered_packet_path': registered, 'ordinal': ordinal,
                'file_identity': file_identity(chain),
                'window_identities': [production_window_identity(window) for window in chain['windows']],
                'source_path': chain['source_path'], 'root': chain['root'],
                'source_metadata_sha256': chain['source_metadata_sha256'],
                'window_count': len(chain['windows']),
                'maximum_output_bytes': reservations[ordinal],
                'prior_receipts': prior_receipts_by_file.get(
                    (chain['root'], chain['source_path'], chain['source_metadata_sha256']), ()),
                'coordinator_pid': os.getpid(),
                'attempt_id': packet['attempt_id'], 'trial_id': packet['trial_id'],
                'protocol_sha256': packet['protocol_sha256'],
                'code_snapshot': packet['code_snapshot'],
                'configuration': packet['configuration'],
                'output_directory': str(expected_dir),
                'compiled_projection': compiled_projection,
            }
            payload = canonical_json(child_packet) + b'\n'
            if len(payload) > cap['maximum_output_file_bytes']:
                raise ValueError('source file packet exceeds the registered file bound')
            artifacts_allowance_after_packet(reservations[ordinal], len(payload))
            expected_packet.write_bytes(payload)
            jobs.append({
                'ordinal': ordinal,
                'argv': [sys.executable, runner, '--source-file', registered, str(expected_packet)],
                'cwd': str(ROOT),
                'env': {**os.environ, **THREADS, 'PYTHONHASHSEED': '0'},
                'output_directory': str(expected_dir),
                'compiled_projection': compiled_projection,
            })
        jobs = order_source_file_jobs(jobs, chains, plan)
        evidence.update(dispatch_strategy=plan.get('dispatch_strategy', 'file_ordinal'),
                        dispatch_ordinals=[job['ordinal'] for job in jobs])
        evidence.update(reserved_output_bytes=reserved, actual_concurrency=concurrency,
                        allocated_address_space_bytes=allocated,
                        aggregate_memory_ceiling_bytes=allocation['aggregate_memory_ceiling_bytes'],
                        maximum_concurrency_ceiling=allocation['maximum_concurrency_ceiling'],
                        file_output_reservations=reservations)
        try:
            supervise_source_children(
                jobs, concurrency=concurrency, cpu_soft_seconds=cap['cpu_seconds'],
                cpu_hard_seconds=cap['hard_cpu_seconds'],
                wall_deadline_monotonic=pool_wall_deadline(worker_started, cap['wall_seconds']),
                allocated_address_space_bytes=allocated, evidence=evidence,
                allowed_failure_exit_codes=(1, 2))
        except ValueError:
            evidence.setdefault('pool_failed', True)
        try:
            charge_child_output_bytes(
                outputs, directories, reservation_per_child=reservations, evidence=evidence)
        finally:
            charged = True
        apply_remaining_coordinator_cpu_limit(cap['cpu_seconds'], cap['hard_cpu_seconds'])
        reports = []
        for ordinal, chain in enumerate(chains):
            receipt_path = directories[ordinal] / 'artifacts' / 'source-file-receipt.json'
            if not receipt_path.is_file():
                receipt_path = directories[ordinal] / 'failure' / 'source-file-receipt.json'
            if not receipt_path.is_file():
                reports.append({
                    'success': False, 'ordinal': ordinal, 'file_identity': file_identity(chain),
                    'windows': [{'status': 'pending', 'unit': window,
                                 'unit_identity': production_window_identity(window)}
                                for window in chain['windows']],
                    'pending_units': [production_window_identity(window) for window in chain['windows']],
                    'failures': [{'error': 'source file child produced no receipt'}],
                })
                continue
            raw, _ = checked(receipt_path, maximum=min(
                cap['maximum_output_file_bytes'], reservations[ordinal]))
            report = json.loads(raw)
            reaped = next((r for r in evidence.get('children', ()) if r['ordinal'] == ordinal), None)
            if (report.get('attempt_id') != packet['attempt_id']
                    or report.get('trial_id') != packet['trial_id']
                    or report.get('ordinal') != ordinal
                    or report.get('file_identity') != file_identity(chain)
                    or report.get('protocol_sha256') != packet['protocol_sha256']
                    or report.get('coordinator_pid') != os.getpid()
                    or reaped is None or report.get('child_pid') != reaped['pid']
                    or report.get('success') is True and reaped['exit_code'] != 0):
                raise ValueError('source file receipt does not join its coordinator packet')
            reports.append(report)
        return reports
    finally:
        if evidence is not None:
            try:
                outputs.json('source-pool-checkpoint.json', evidence, kind='auction_flow_source_pool_checkpoint')
            except Exception:
                pass
        if not charged:
            try:
                charge_child_output_bytes(
                    outputs, directories, reservation_per_child=reservations, evidence=evidence)
            except ValueError:
                pass
        try:
            apply_remaining_coordinator_cpu_limit(cap['cpu_seconds'], cap['hard_cpu_seconds'])
        except ValueError:
            pass



def diagnose_unresolved_source_clock(unit, *, data_root):
    """Original fields for the first clock violation NOT admitted by the frozen policy.

    Runs only after a real clock failure, within that registered file worker.
    No sorting, replacement clock, source exclusion, or successful artifact is produced.
    """
    import numpy as np
    import pyarrow.parquet as pq
    import math
    import struct
    from trading_research.data.compact import authenticate_redundant_backward_snapshot, _CLOCK_FIELDS
    def retained_record(value):
        if value is None:
            return None
        return {key: ({'$float64_bits_le': struct.pack('<d', item).hex()}
                      if type(item) is float and not math.isfinite(item) else item)
                for key, item in value.items()}
    path = Path(data_root) / unit['source_path']
    stamp = (path.stat().st_size, path.stat().st_mtime_ns)
    parquet = pq.ParquetFile(path)
    offsets, total = [], 0
    for group in range(parquet.num_row_groups):
        offsets.append(total)
        total += parquet.metadata.row_group(group).num_rows
    limit = unit['physical_scan_rows']
    scanned = admitted = 0
    highwater = previous = previous_address = None
    issue = None
    for group in unit['source_groups']:
        within = 0
        for batch in parquet.iter_batches(batch_size=65536, row_groups=[group], columns=list(_CLOCK_FIELDS), use_threads=False):
            scanned += len(batch)
            if scanned > limit:
                raise ValueError('failure diagnosis exceeded original selected physical scan bound')
            times = batch.column(batch.schema.get_field_index('t'))
            if times.null_count:
                i = int(np.flatnonzero(times.is_null().to_numpy(zero_copy_only=False))[0])
                address = offsets[group] + within + i
                issue = {'kind': 'null_clock', 'source_row': address,
                    'record': retained_record(batch.slice(i, 1).to_pylist()[0]),
                    'previous_source_row': address - 1 if i else previous_address,
                    'physical_predecessor': retained_record(batch.slice(i - 1, 1).to_pylist()[0] if i else previous)}
                break
            t = times.to_numpy(zero_copy_only=False)
            selected = np.flatnonzero((t >= unit['event_start_ns']) & (t < unit['event_end_ns']))
            if len(selected):
                values = t[selected]
                prefix = np.maximum.accumulate(values)
                prior = np.concatenate((values[:1] if highwater is None else np.array([highwater], dtype=values.dtype), prefix[:-1]))
                if highwater is not None:
                    prior = np.maximum(prior, highwater)
                for i in selected[values < prior]:
                    i = int(i)
                    address = offsets[group] + within + i
                    event = batch.slice(i, 1).to_pylist()[0]
                    predecessor = batch.slice(i - 1, 1).to_pylist()[0] if i else previous
                    predecessor_address = address - 1 if i else previous_address
                    adjacent = predecessor_address == address - 1
                    # The production projection's predecessor must also have survived the event-window filter.
                    in_window = (predecessor is not None and predecessor.get('t') is not None
                        and unit['event_start_ns'] <= predecessor['t'] < unit['event_end_ns'])
                    reason = authenticate_redundant_backward_snapshot(event=event, predecessor=predecessor,
                        same_physical_source=adjacent and in_window, physically_adjacent=adjacent and in_window)
                    if reason is None:
                        issue = {'kind': 'unresolved_backward_clock', 'source_row': address,
                            'previous_source_row': predecessor_address, 'record': retained_record(event),
                            'physical_predecessor': retained_record(predecessor), 'physically_adjacent': adjacent,
                            'predecessor_inside_selected_window': in_window}
                        break
                    admitted += 1
                highwater = max(int(values.max()), highwater if highwater is not None else int(values[0]))
            if issue:
                break
            previous = batch.slice(len(batch)-1, 1).to_pylist()[0]
            previous_address = offsets[group] + within + len(batch) - 1
            within += len(batch)
        if issue:
            break
    if stamp != (path.stat().st_size, path.stat().st_mtime_ns):
        raise ValueError('raw source changed during failure diagnosis')
    return {'unit': unit, 'physical_rows_scanned': scanned, 'original_scan_row_bound': limit,
        'earlier_admitted_redundant_snapshots': admitted, 'first_unresolved_issue': issue,
        'source_values_modified': False, 'source_policy_changed': False,
        'scope': 'Failure diagnosis only; original all-field rows and physical addresses, no measurement acceptance.'}


def publish_source_file_result(*, outputs, packet, child, result):
    """Retain the actual file result even when a failed window poisoned its writer.

    The fallback has a fresh namespace and consumes the remaining ORIGINAL
    per-file reservation. It cannot revive partial measurement artifacts.
    """
    from trading_research.operations.artifacts import canonical_json
    if not outputs.failed:
        return outputs.json('source-file-receipt.json', result, kind='auction_flow_source_file_receipt')
    failure_summary = {'kind': 'auction_flow_source_file_failure_notice',
        'attempt_id': packet['attempt_id'], 'ordinal': child['ordinal'],
        'source_path': child['source_path'],
        'errors': [str(row.get('error', 'unspecified file failure'))[:2048]
                   for row in result.get('failures', ())[:32]],
        'completed_windows': result.get('completed_windows', 0),
        'pending_windows': len(result.get('pending_units', ()))}
    print(json.dumps(failure_summary, sort_keys=True), file=sys.stderr, flush=True)
    expected = Path(child['output_directory']).resolve()
    used = sum(path.stat().st_size for path in expected.rglob('*') if path.is_file())
    available = child['maximum_output_bytes'] - used
    payload = canonical_json(result) + b'\n'
    if len(payload) > available or len(payload) > packet['limits']['maximum_output_file_bytes']:
        raise ValueError('failure result does not fit the remaining original file reservation')
    target = expected / 'failure'
    target.mkdir(parents=False, exist_ok=False)
    path = target / 'source-file-receipt.json'
    with path.open('xb') as stream:
        stream.write(payload)
    return {'path': str(path), 'sha256': hashlib.sha256(payload).hexdigest(),
            'size_bytes': len(payload), 'kind': 'auction_flow_source_file_receipt'}


def _source_file_failure_receipt(*, outputs, packet, child, compiled, error):
    if outputs is None or packet is None or child is None:
        return
    try:
        result = {
            'kind': 'auction_flow_source_file_receipt_v1', 'success': False,
            'attempt_id': packet['attempt_id'], 'trial_id': packet['trial_id'],
            'protocol_sha256': packet['protocol_sha256'], 'ordinal': child.get('ordinal'),
            'file_identity': child.get('file_identity'),
            'windows': [{'status': 'pending', 'unit_identity': identity}
                        for identity in child.get('window_identities') or ()],
            'pending_units': list(child.get('window_identities') or ()),
            'failures': [{'error': error}],
            'coordinator_pid': child.get('coordinator_pid'), 'child_pid': os.getpid(),
            'compiled_library': None if compiled is None else compiled.get('library'),
            'family_statistics_or_model_complete': False,
        }
        publish_source_file_result(outputs=outputs, packet=packet, child=child, result=result)
    except Exception:
        pass


def source_file(registered_packet_path, child_packet_path):
    bootstrap_process_limits()
    outputs = packet = child = compiled = None
    receipt_written = False
    try:
        child = json.loads(checked(child_packet_path, maximum=2 * 1024**2)[0])
        registered = json.loads(checked(registered_packet_path, maximum=2 * 1024**2)[0])
        if (child.get('kind') != 'auction_flow_source_file_packet_v1'
                or Path(child['registered_packet_path']).resolve() != Path(registered_packet_path).resolve()):
            raise ValueError('source file packet identity changed')
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
            raise ValueError('source file parent identity mismatch')
        if Path(child['output_directory']).resolve() != Path(child_packet_path).resolve().parent:
            raise ValueError('source file output directory changed')
        expected_dir, expected_packet = require_source_file_namespace(
            attempt_id=packet['attempt_id'], ordinal=child['ordinal'],
            child_packet_path=child_packet_path, output_directory=child['output_directory'],
            runs_root=RUNS)
        from trading_research.research.auction_flow_coordinates import RetainedCoordinateIndex
        from trading_research.research.auction_flow_production import (
            declared_allocation, file_chains_from_schedule, file_identity,
            producer_identity, production_window_identity, resolve_declared_document,
            resolve_production_schedule, run_file_chain, validate_production_plan)
        from trading_research.research.auction_flow_storage import BoundedOutputs
        limits_decl, plan_decl = declared_allocation(authenticated['extension'], packet['configuration']['mode'])
        plan = resolve_declared_document(plan_decl, load_reference=load_reference)
        schedule = resolve_production_schedule(plan, load_reference=load_reference)
        chains = file_chains_from_schedule(schedule)
        if type(child['ordinal']) is not int or not 0 <= child['ordinal'] < len(chains):
            raise ValueError('source file ordinal is outside the reconstructed parent plan')
        chain = chains[child['ordinal']]
        if (child.get('file_identity') != file_identity(chain)
                or child.get('window_identities') != [production_window_identity(w) for w in chain['windows']]
                or child.get('source_path') != chain['source_path']
                or child.get('source_metadata_sha256') != chain['source_metadata_sha256']):
            raise ValueError('file child job does not match the reconstructed parent plan')
        validate_production_plan(plan, chains, protocol, mode=packet['configuration']['mode'],
                                 available_output_bytes=packet['limits']['maximum_output_bytes'])
        reserved_file = next(row for row in plan['files'] if row['root'] == chain['root']
                             and row['source_path'] == chain['source_path']
                             and row['source_metadata_sha256'] == chain['source_metadata_sha256'])
        if child.get('maximum_output_bytes') != reserved_file['maximum_output_bytes']:
            raise ValueError('source file output reservation differs from frozen plan')
        packet_bytes = Path(expected_packet).stat().st_size
        allowance = artifacts_allowance_after_packet(child['maximum_output_bytes'], packet_bytes)
        file_limit = min(cap['maximum_output_file_bytes'], allowance)
        outputs = BoundedOutputs(expected_dir / 'artifacts',
            maximum_total_bytes=allowance, maximum_file_bytes=file_limit)
        compiled = child.get('compiled_projection')
        if not compiled:
            raise ValueError('compiled source backend required for production extract')
        reference = compiled['library']
        expected_library = Path(registered_packet_path).parent / 'outputs' / 'compact-projection.so'
        if Path(reference['path']).resolve() != expected_library.resolve():
            raise ValueError('compiled source library escaped its registered coordinator outputs')
        raw, _ = checked(expected_library, reference['sha256'], maximum=cap['maximum_output_file_bytes'])
        if len(raw) != reference['size_bytes']:
            raise ValueError('compiled source library size changed')
        from trading_research.data.compact_native import enable_compiled_projection
        enable_compiled_projection(expected_library, reference['sha256'])
        symbol = chain['root']
        coord_ref = protocol['coordinate_admissions'][symbol]
        coordinates = RetainedCoordinateIndex(
            load_reference(coord_ref), source_version=coord_ref['sha256'],
            snapshot_supplement=load_reference(protocol['nq_snapshot_supplement']) if symbol == 'NQ' else None,
            snapshot_version=protocol['nq_snapshot_supplement']['sha256'] if symbol == 'NQ' else None)
        index = load_reference(protocol['source_index'])
        prior = []
        for reference in child.get('prior_receipts') or ():
            prior.append(load_reference(reference, maximum=cap['maximum_output_file_bytes']))
        identity = producer_identity(ROOT, manifest=packet['code_manifest'])
        attempt = {'attempt_id': packet['attempt_id'], 'trial_id': packet['trial_id'],
                   'family': protocol['family'], 'protocol_sha256': packet['protocol_sha256']}
        registered_attempts = authenticated['registry'].state()['attempts']
        result = run_file_chain(
            chain, protocol={**protocol, 'protocol_sha256': packet['protocol_sha256']},
            index=index, coordinates=coordinates, outputs=outputs, data_root=ROOT.parent / 'data',
            prior_receipts=prior, registered_attempts=registered_attempts,
            source_clock_policy=plan.get('source_clock_policy'),
            producer_identity_value=identity, runtime_versions=authenticated['versions'],
            attempt=attempt, latency_ns=plan.get('latency_ns', 250_000_000))
        if authenticated['extension'].get('diagnose_first_unresolved_clock_after_file_failure') is True:
            for failure in result.get('failures', ()):
                if 'source event order/null clock requires separate resolution' in failure.get('error', ''):
                    try:
                        failure['clock_diagnostic'] = diagnose_unresolved_source_clock(
                            failure['unit'], data_root=ROOT.parent / 'data')
                    except Exception as diagnostic_error:
                        failure['clock_diagnostic_error'] = f'{type(diagnostic_error).__name__}: {diagnostic_error}'
        from trading_research.data.compact_native import execution_counts
        result['compiled_execution_counts'] = execution_counts()
        result.update({
            'attempt_id': packet['attempt_id'], 'trial_id': packet['trial_id'],
            'protocol_sha256': packet['protocol_sha256'], 'ordinal': child['ordinal'],
            'coordinator_pid': child['coordinator_pid'], 'child_pid': os.getpid(),
            'compiled_library': compiled['library'],
        })
        publish_source_file_result(outputs=outputs, packet=packet, child=child, result=result)
        receipt_written = True
        return 0 if result['success'] else 2
    except BaseException as exc:
        traceback.print_exc()
        if not receipt_written:
            _source_file_failure_receipt(
                outputs=outputs, packet=packet, child=child, compiled=compiled,
                error=f'{type(exc).__name__}: {exc}')
        return 1


def extract_check_source(authenticated, packet_path, worker_started):
    import unittest
    from trading_research.operations.artifacts import canonical_json, publish_new
    from trading_research.research.auction_flow_production import (
        declared_allocation, file_chains_from_schedule, resolve_declared_document,
        resolve_production_schedule, validate_production_plan)
    from trading_research.research.auction_flow_storage import BoundedOutputs

    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    extension = authenticated['extension']
    limits_decl, plan_decl = declared_allocation(extension, 'extract-check')
    plan = resolve_declared_document(plan_decl, load_reference=load_reference)
    modules = extract_check_modules(protocol, extension)
    started = time.process_time()
    tested = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    tests = dict(tests=tested.testsRun, failures=len(tested.failures), errors=len(tested.errors),
                 success=tested.wasSuccessful(), cpu_seconds=time.process_time() - started, modules=modules)
    if not tested.wasSuccessful():
        raise ValueError('extract-check regression checks failed; no production execution')
    schedule = resolve_production_schedule(plan, load_reference=load_reference)
    chains = file_chains_from_schedule(schedule)
    planned = validate_production_plan(
        plan, chains, protocol, mode='extract-check',
        available_output_bytes=cap['maximum_output_bytes'])
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs',
        maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'],
        maximum_file_bytes=cap['maximum_output_file_bytes'])
    from trading_research.research.auction_flow_production import summarize_file_reports
    compiled = compile_source_projection(packet_path, outputs)
    evidence = {}
    reports = execute_source_files_parallel(chains, plan=plan, packet_path=packet_path, packet=packet,
        planned=authenticated['registered_plan'], concurrency=authenticated['concurrency'], cap=cap,
        worker_started=worker_started, evidence=evidence, outputs=outputs, compiled_projection=compiled)
    summary = summarize_file_reports(reports, required_window_count=sum(len(c['windows']) for c in chains))
    if not summary['success']:
        raise ValueError('bounded production file chains failed; retained pool and window receipts remain')
    receipts = [row['receipt_reference'] for report in reports for row in report['windows']]
    report = {key: packet[key] for key in
              ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration')}
    report.update(family=protocol['family'], mode='extract-check', success=True,
        tests=tests, production_plan_validated=True, compiled_projection=compiled,
        source_unit_parallel_execution=evidence, production_window_receipts=receipts,
        reconstructed_files=len(chains), reconstructed_windows=sum(len(c['windows']) for c in chains),
        reserved_output_bytes=planned['reserved_output_bytes'],
        complete_source_extraction=False, complete_family_statistics=False,
        full_project_under_three_hours_verified=False,
        runtime_versions=authenticated['versions'], derived_output_bytes=outputs.written,
        scope='Production controller checks plus eight retained eligible windows in two complete physical files; outputs reusable by exact receipt. No complete source population or family statistics.')
    publish_new(Path(packet['worker_report']), canonical_json(report) + b'\n')
    return 0


def extract_source(authenticated, packet_path, worker_started):
    from trading_research.operations.artifacts import canonical_json, publish_new
    from trading_research.research.auction_flow_production import (
        COMPLETE_SOURCE_FILES, COMPLETE_SOURCE_WINDOWS, declared_allocation,
        file_chains_from_schedule, resolve_declared_document, resolve_production_schedule,
        summarize_file_reports, validate_production_plan)
    from trading_research.research.auction_flow_storage import BoundedOutputs

    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    extension = authenticated['extension']
    limits_decl, plan_decl = declared_allocation(extension, 'extract')
    plan = resolve_declared_document(plan_decl, load_reference=load_reference)
    schedule = resolve_production_schedule(plan, load_reference=load_reference)
    chains = file_chains_from_schedule(schedule)
    required_windows = COMPLETE_SOURCE_WINDOWS
    required_files = COMPLETE_SOURCE_FILES
    if (plan.get('required_window_count') not in (None, COMPLETE_SOURCE_WINDOWS)
            or plan.get('required_file_count') not in (None, COMPLETE_SOURCE_FILES)
            or schedule['source_windows'] != required_windows or len(chains) != required_files):
        raise ValueError('extract requires the complete declared schedule')
    planned = validate_production_plan(
        plan, chains, protocol, mode='extract',
        available_output_bytes=cap['maximum_output_bytes'])
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs',
        maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'],
        maximum_file_bytes=cap['maximum_output_file_bytes'])
    tests = None
    if extension.get('production_continuation_check_modules'):
        import unittest
        declared = extension['production_continuation_check_modules']
        admitted = set(protocol['check_modules'] + extension.get('additional_check_modules', []))
        if not isinstance(declared, list) or len(set(declared)) != len(declared) or any(m not in admitted for m in declared):
            raise ValueError('continuation checks must use unique admitted family modules')
        began = time.process_time()
        tested = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(declared))
        tests = {'tests': tested.testsRun, 'failures': len(tested.failures), 'errors': len(tested.errors),
            'success': tested.wasSuccessful(), 'cpu_seconds': time.process_time() - began, 'modules': declared}
        outputs.json('continuation-checks.json', tests, kind='auction_flow_changed_behavior_checks')
        if not tests['success']:
            raise ValueError('failure-capture checks failed before source continuation; preserve and reassess diagnosis')
    compiled = compile_source_projection(packet_path, outputs)
    prior_refs = {}
    catalog = extension.get('prior_production_window_receipts') or plan.get('prior_production_window_receipts') or ()
    catalog_ref = extension.get('prior_production_receipt_catalog')
    if catalog_ref is not None:
        if catalog:
            raise ValueError('declare one retained production receipt catalog')
        catalog_payload = load_reference(catalog_ref)
        if catalog_payload.get('kind') != 'auction_flow_retained_production_receipt_catalog_v1':
            raise ValueError('retained source receipt catalog kind changed')
        catalog = catalog_payload['receipts']
        if not isinstance(catalog, list):
            raise ValueError('retained source receipt catalog must contain explicit references')
    for reference in catalog:
        receipt = load_reference(reference)
        unit = receipt['unit']
        key = (unit['root'], unit['source_path'], unit['source_metadata_sha256'])
        prior_refs.setdefault(key, []).append(reference)
    evidence = {}
    reports = execute_source_files_parallel(
        chains, plan=plan, packet_path=packet_path, packet=packet,
        planned=authenticated['registered_plan'], concurrency=authenticated['concurrency'],
        cap=cap, worker_started=worker_started, evidence=evidence, outputs=outputs,
        compiled_projection=compiled, prior_receipts_by_file=prior_refs)
    summary = summarize_file_reports(reports, required_window_count=required_windows)
    report = {key: packet[key] for key in
              ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration')}
    report.update(family=protocol['family'], mode='extract',
        success=summary['success'] and (tests is None or tests['success']), tests=tests,
        complete_source_extraction=summary['complete_source_extraction'],
        complete_family_statistics=False, full_project_under_three_hours_verified=False,
        completed_windows=summary['completed_windows'], required_windows=required_windows,
        reused_windows=summary['reused_windows'], pending_units=summary['pending_units'],
        failures=summary['failures'], compiled_projection=compiled,
        runtime_versions=authenticated['versions'], source_unit_parallel_execution=evidence,
        derived_output_bytes=outputs.written, reserved_output_bytes=planned['reserved_output_bytes'],
        file_reports=[{'ordinal': index, 'success': row.get('success'),
                       'file_identity': row.get('file_identity'),
                       'completed_windows': row.get('completed_windows'),
                       'pending_units': row.get('pending_units')}
                      for index, row in enumerate(reports)],
        scope='Complete acquired-source extraction with exact trades/exclusions/native/quote-replay/measurements and authenticated reuse. No family statistics or end-to-end runtime claim.')
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
        if packet['configuration']['mode'] == 'extract-check':
            return extract_check_source(authenticated, packet_path, worker_started)
        if packet['configuration']['mode'] == 'extract':
            return extract_source(authenticated, packet_path, worker_started)
        if packet['configuration']['mode'] == 'source-clock':
            return check_source_clock(authenticated, packet_path, worker_started)
        if packet['configuration']['mode'] == 'clock-audit':
            return audit_nan_failures(authenticated, packet_path) if extension.get('nan_failure_audit') else audit_clock_records(authenticated, packet_path)
        if packet['configuration']['mode'] == 'throughput':
            return throughput_source(authenticated, packet_path, worker_started)
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
    if mode in EXTRACT_MODES:
        limits_decl, plan_decl = production_declarations(extension, mode)
        configuration['production_limits'] = limits_decl
        configuration['production_plan'] = plan_decl
    trial = registry.register(name='Acquired auction/flow: ' + (
        'production source extraction' if mode == 'extract'
        else 'production source extract-check' if mode == 'extract-check'
        else 'complete source performance diagnostic' if mode in ('profile','benchmark','compute')
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
    if len(sys.argv) == 4 and sys.argv[1] == '--source-file':
        raise SystemExit(source_file(sys.argv[2], sys.argv[3]))
    if len(sys.argv) != 2 or sys.argv[1] not in REGISTERED_MODES:
        raise SystemExit('usage: run_auction_flow_study.py {check|profile|benchmark|compute|downstream|throughput|clock-audit|source-clock|extract|extract-check}')
    raise SystemExit(parent(sys.argv[1]))
