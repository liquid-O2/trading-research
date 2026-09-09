"""Production source extraction: file-chain carry, exact artifacts, authenticated reuse.

This controller produces required source-window artifacts for the registered
auction family. It does not run downstream fitting, family statistics, or the
verification wrapper ``measured_unit``. Codex supplies production allocation
and the frozen schedule; this module validates them and fails closed if they
are absent. The named redundant-backward clock policy is passed through only;
it is not implemented here.
"""
from __future__ import annotations

import ast
import hashlib
import inspect
from pathlib import Path

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest, file_digest
from trading_research.research.auction_flow_pipeline import measure_raw_window
from trading_research.research.auction_flow_quote_replay import QuoteReplaySeries
from trading_research.research.auction_flow_schedule import VERSION as SCHEDULE_VERSION
from trading_research.research.auction_flow_storage import (
    BoundedOutputs, ParquetSeries, read_json_artifact,
)


VERSION = 'auction-flow-production-source-controller-v1'
WINDOW_RECEIPT_KIND = 'auction_flow_source_window_receipt_v1'
FILE_RECEIPT_KIND = 'auction_flow_source_file_receipt_v1'
CONTINUATION_KIND = 'auction_flow_production_continuation_v1'
PRODUCER_IDENTITY_KIND = 'auction_flow_source_producer_identity_v1'
LIMITS_KIND = 'auction_flow_production_limits_v1'
EXTRACT_CHECK_LIMITS_KIND = 'auction_flow_extract_check_limits_v1'
PLAN_KIND = 'auction_flow_production_plan_v1'
DEFAULT_LATENCY_NS = 250_000_000
STRICT_SOURCE_CLOCK_POLICY = 'strict'
REDUNDANT_BACKWARD_SNAPSHOT_V1 = 'redundant_backward_snapshot_v1'
COMPLETE_SOURCE_WINDOWS = 3589
COMPLETE_SOURCE_FILES = 167
FAMILY_CPU_BUDGET_SECONDS = 192000
FAMILY_MAXIMUM_ATTEMPTS = 32
FAMILY_STUDY_OUTPUT_BYTES = 256 * 1024 ** 3
FAMILY_HARD_CPU_MARGIN_SECONDS = 10
MAXIMUM_OUTPUT_FILE_BYTES = 512 * 1024 ** 2
CHILD_MEMORY_BYTES = 4 * 1024 ** 3
PRODUCER_IMPLEMENTATION_FILES = (
    'src/trading_research/research/auction_flow_production.py',
    'src/trading_research/research/auction_flow_pipeline.py',
    'src/trading_research/research/auction_flow_storage.py',
    'src/trading_research/research/auction_flow_quote_replay.py',
    'src/trading_research/research/auction_flow_data.py',
    'src/trading_research/research/auction_flow_coordinates.py',
    'src/trading_research/research/auction_flow_quotes.py',
    'src/trading_research/research/auction_flow_windows.py',
    'src/trading_research/research/auction_flow_time_at_price.py',
    'src/trading_research/research/auction_flow_native_bins.py',
    'src/trading_research/research/auction_flow_arrow.py',
    'src/trading_research/research/auction_flow_structural_encoding.py',
    'src/trading_research/data/compact.py',
    'src/trading_research/data/compact_native.py',
    'src/trading_research/data/reconcile.py',
)


def normalize_source_clock_policy(policy):
    if policy in (None, STRICT_SOURCE_CLOCK_POLICY):
        return None
    if policy == REDUNDANT_BACKWARD_SNAPSHOT_V1:
        return policy
    raise ContractError('unknown source_clock_policy')


def clock_kwargs(policy, function):
    """Pass a requested clock policy only when the callee already accepts it."""
    normalized = normalize_source_clock_policy(policy)
    params = inspect.signature(function).parameters
    accepts = ('source_clock_policy' in params
               or any(item.kind is inspect.Parameter.VAR_KEYWORD for item in params.values()))
    if normalized is None:
        if policy == STRICT_SOURCE_CLOCK_POLICY and accepts:
            return {'source_clock_policy': STRICT_SOURCE_CLOCK_POLICY}
        return {}
    if not accepts:
        raise ContractError(
            'requested source_clock_policy is not implemented by the current measurement pipeline')
    return {'source_clock_policy': normalized}


def source_variant(source_path):
    return hashlib.sha256(source_path.encode()).hexdigest()[:12]


def production_window_identity(window):
    return {
        'root': window['root'],
        'source_path': window['source_path'],
        'source_metadata_sha256': window['source_metadata_sha256'],
        'event_start_ns': window['event_start_ns'],
        'event_end_ns': window['event_end_ns'],
        'source_variant': source_variant(window['source_path']),
    }


def file_identity(chain):
    windows = chain['windows']
    return {
        'root': chain['root'],
        'source_path': chain['source_path'],
        'source_metadata_sha256': chain['source_metadata_sha256'],
        'window_count': len(windows),
        'first_event_start_ns': windows[0]['event_start_ns'],
        'last_event_end_ns': windows[-1]['event_end_ns'],
    }


def window_artifact_prefix(window):
    identity = production_window_identity(window)
    return f"{identity['root']}-{identity['event_start_ns']}-{identity['source_variant']}"


def producer_identity(root, *, manifest=None):
    """Relevant source-producer files only; unrelated consumers are excluded."""
    root = Path(root)
    files = {}
    pending = list(PRODUCER_IMPLEMENTATION_FILES)
    while pending:
        name = pending.pop()
        if name in files:
            continue
        path = root / name
        if not path.is_file():
            raise IntegrityError(f'producer implementation file is absent: {name}')
        raw = path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        recorded = None if manifest is None else manifest.get(name)
        if isinstance(recorded, dict):
            recorded = recorded.get('sha256')
        if manifest is not None and recorded != sha:
            raise IntegrityError('producer file differs from its registered manifest')
        files[name] = {'sha256': sha, 'size_bytes': len(raw)}
        if name.endswith('.py'):
            for node in ast.walk(ast.parse(raw)):
                modules = ([node.module] if isinstance(node, ast.ImportFrom) and node.module
                           else [alias.name for alias in node.names] if isinstance(node, ast.Import) else [])
                for module in modules:
                    if module != 'trading_research' and not module.startswith('trading_research.'):
                        continue
                    components = module.split('.')
                    for depth in range(1, len(components) + 1):
                        stem = 'src/' + '/'.join(components[:depth])
                        for local in (stem + '.py', stem + '/__init__.py'):
                            if (root / local).is_file() and local not in files:
                                pending.append(local)
    for name in ('pyproject.toml', 'uv.lock'):
        path = root / name
        if path.is_file():
            raw = path.read_bytes()
            files[name] = {'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': len(raw)}
    identity = {'kind': PRODUCER_IDENTITY_KIND, 'files': files}
    identity['sha256'] = digest({key: value for key, value in identity.items() if key != 'sha256'})
    return identity


def join_window_to_index(window, protocol, index):
    if window['root'] not in protocol['roots']:
        raise IntegrityError('source window root is outside the registered protocol')
    dataset = window.get('dataset') or f"quantpad/cme__{window['root'].lower()}-continuous-futures__mbp-1"
    records = [record for record in index['datasets'][dataset] if record['path'] == window['source_path']]
    if len(records) != 1:
        raise IntegrityError('source window does not join the admitted index')
    if digest(records[0]) != window['source_metadata_sha256']:
        raise IntegrityError('source_metadata hash does not join protocol/index/schedule')
    return records[0]


def file_chains_from_schedule(schedule):
    """Group a frozen complete schedule into per-file chronological chains."""
    if not isinstance(schedule, dict) or schedule.get('version') != SCHEDULE_VERSION:
        raise IntegrityError('production requires the frozen physical source-day schedule')
    windows = schedule.get('windows')
    if not isinstance(windows, list) or not windows:
        raise IntegrityError('production schedule has no source windows')
    if schedule.get('source_windows') != len(windows):
        raise IntegrityError('schedule window count does not match its retained population')
    seen = set()
    groups = {}
    order = []
    for window in windows:
        if (not isinstance(window, dict)
                or window.get('root') not in ('NQ', 'ES')
                or type(window.get('source_path')) is not str or not window['source_path']
                or type(window.get('source_metadata_sha256')) is not str
                or len(window['source_metadata_sha256']) != 64
                or type(window.get('event_start_ns')) is not int
                or type(window.get('event_end_ns')) is not int
                or not 0 <= window['event_start_ns'] < window['event_end_ns']):
            raise IntegrityError('schedule window identity is incomplete')
        key = (window['root'], window['source_path'], window['source_metadata_sha256'],
               window['event_start_ns'], window['event_end_ns'])
        if key in seen:
            raise IntegrityError('duplicate source/day window')
        seen.add(key)
        lineage = (window['root'], window['source_path'], window['source_metadata_sha256'])
        if lineage not in groups:
            groups[lineage] = []
            order.append(lineage)
        groups[lineage].append(window)
    by_path = {}
    chains = []
    for lineage in order:
        items = groups[lineage]
        ordered = sorted(items, key=lambda row: row['event_start_ns'])
        path = lineage[1]
        if path in by_path:
            raise IntegrityError('overlapping file lineages')
        by_path[path] = lineage
        for previous, current in zip(ordered, ordered[1:]):
            if current['event_start_ns'] < previous['event_end_ns']:
                raise IntegrityError('overlapping windows in one physical source lineage')
            if current['event_start_ns'] != previous['event_end_ns']:
                raise IntegrityError('file chain is missing a required source/day window')
        if ordered[0].get('first_window_of_physical_source') is not True:
            raise IntegrityError('file start is not an explicit observed prefix')
        if ordered[-1].get('last_window_of_physical_source') is not True:
            raise IntegrityError('file chain lost its terminal scheduled window')
        if any(row.get('first_window_of_physical_source') for row in ordered[1:]):
            raise IntegrityError('a calendar cut cannot create a new observed prefix')
        chains.append({
            'root': lineage[0], 'source_path': lineage[1],
            'source_metadata_sha256': lineage[2], 'windows': ordered,
        })
    rebuilt = [window for chain in chains for window in chain['windows']]
    expected = sorted(windows, key=lambda row: (row['root'], row['source_path'], row['event_start_ns']))
    actual = sorted(rebuilt, key=lambda row: (row['root'], row['source_path'], row['event_start_ns']))
    if actual != expected or len(rebuilt) != len(windows):
        raise IntegrityError('file grouping lost or duplicated scheduled windows')
    return chains


def declared_allocation(extension, mode):
    """Return Codex-supplied limits/plan for the extract mode; never invent them."""
    if not isinstance(extension, dict):
        raise ValueError('production allocation/plan is absent; refuse to invent extract caps')
    if mode == 'extract-check':
        limits = extension.get('extract_check_limits')
        plan = extension.get('extract_check_plan')
        production_limits = extension.get('production_limits')
        production_plan = extension.get('production_plan')
        if limits is None and isinstance(production_limits, dict) and production_limits.get('kind') == EXTRACT_CHECK_LIMITS_KIND:
            limits = production_limits
        if plan is None and isinstance(production_plan, dict) and production_plan.get('mode') == 'extract-check':
            plan = production_plan
    elif mode == 'extract':
        limits = extension.get('production_limits')
        plan = extension.get('production_plan')
    else:
        raise ValueError('unknown registered source workload')
    if limits is None or plan is None:
        raise ValueError('production allocation/plan is absent; refuse to invent extract caps')
    return limits, plan


def resolve_declared_document(value, *, load_reference=None):
    if not isinstance(value, dict):
        raise ValueError('production allocation/plan is absent; refuse to invent extract caps')
    if {'path', 'sha256', 'size_bytes'} <= value.keys() and 'windows' not in value and 'cpu_seconds' not in value:
        if load_reference is None:
            raise ValueError('production allocation/plan is absent; refuse to invent extract caps')
        return load_reference(value)
    return value


def resolve_production_schedule(plan, *, load_reference=None):
    schedule = plan.get('schedule') if isinstance(plan, dict) else None
    if schedule is None:
        raise ValueError('frozen production plan is absent; refuse to invent a schedule')
    if isinstance(schedule, dict) and isinstance(schedule.get('windows'), list):
        return schedule
    return resolve_declared_document(schedule, load_reference=load_reference)


def validate_production_limits(declared, protocol, *, mode, previous_study_output_bytes=0):
    """Bind Codex-supplied extract caps to the unchanged family totals."""
    if not isinstance(declared, dict):
        raise ValueError('production allocation is absent; refuse to invent extract caps')
    expected_kind = EXTRACT_CHECK_LIMITS_KIND if mode == 'extract-check' else LIMITS_KIND
    if declared.get('kind') != expected_kind:
        raise ValueError('production_limits kind is missing or does not match the extract mode')
    resources = protocol['resources']
    if (resources.get('cpu_budget_seconds') != FAMILY_CPU_BUDGET_SECONDS
            or resources.get('maximum_attempts') != FAMILY_MAXIMUM_ATTEMPTS
            or resources.get('maximum_study_output_bytes') != FAMILY_STUDY_OUTPUT_BYTES
            or resources.get('hard_cpu_margin_seconds') != FAMILY_HARD_CPU_MARGIN_SECONDS):
        raise ValueError('production cannot change registered family resource totals')
    required = ('cpu_seconds', 'hard_cpu_seconds', 'wall_seconds', 'memory_bytes',
                'maximum_output_file_bytes', 'maximum_output_bytes',
                'supervisor_output_reserve_bytes')
    for name in required:
        if type(declared.get(name)) is not int or declared[name] <= 0:
            raise ValueError(f'production_limits field {name} is absent or invalid')
    cpu, hard = declared['cpu_seconds'], declared['hard_cpu_seconds']
    if hard - cpu != FAMILY_HARD_CPU_MARGIN_SECONDS:
        raise ValueError('hard CPU margin must remain the registered 10-second bound')
    if cpu > FAMILY_CPU_BUDGET_SECONDS or hard > FAMILY_CPU_BUDGET_SECONDS + FAMILY_HARD_CPU_MARGIN_SECONDS:
        raise ValueError('extract CPU exceeds the unchanged family total')
    if declared['memory_bytes'] != resources['memory_bytes']:
        raise ValueError('per-process memory must remain the registered 4GiB bound')
    if declared['maximum_output_file_bytes'] != resources['maximum_output_file_bytes']:
        raise ValueError('individual file bound must remain 512MiB')
    if type(previous_study_output_bytes) is not int or previous_study_output_bytes < 0:
        raise ValueError('retained study output is invalid')
    if previous_study_output_bytes + declared['maximum_output_bytes'] > FAMILY_STUDY_OUTPUT_BYTES:
        raise ValueError('remaining study output allowance cannot reserve this extract attempt')
    if mode == 'extract-check' and declared['maximum_output_bytes'] > resources['maximum_derived_output_bytes']:
        raise ValueError('extract-check cannot exceed the ordinary check output allowance')
    return {
        'cpu_seconds': cpu, 'hard_cpu_seconds': hard, 'wall_seconds': declared['wall_seconds'],
        'memory_bytes': declared['memory_bytes'],
        'maximum_output_file_bytes': declared['maximum_output_file_bytes'],
        'maximum_output_bytes': declared['maximum_output_bytes'],
        'supervisor_output_reserve_bytes': declared['supervisor_output_reserve_bytes'],
    }


def validate_production_plan(plan, chains, protocol, *, mode, available_output_bytes):
    if not isinstance(plan, dict) or plan.get('kind') != PLAN_KIND:
        raise ValueError('frozen production plan is absent; refuse to invent a schedule')
    files = plan.get('files')
    if not isinstance(files, list) or not files:
        raise ValueError('production plan has no per-file output reservations')
    if type(plan.get('coordinator_reserve_bytes')) is not int or plan['coordinator_reserve_bytes'] < 0:
        raise ValueError('production plan coordinator reserve is invalid')
    normalize_source_clock_policy(plan.get('source_clock_policy'))
    required_windows = plan.get('required_window_count')
    required_files = plan.get('required_file_count')
    if mode == 'extract':
        if required_windows not in (None, COMPLETE_SOURCE_WINDOWS):
            raise ValueError('extract requires the complete declared schedule')
        if required_files not in (None, COMPLETE_SOURCE_FILES):
            raise ValueError('extract requires the complete declared schedule')
        required_windows = COMPLETE_SOURCE_WINDOWS
        required_files = COMPLETE_SOURCE_FILES
    if type(required_windows) is not int or type(required_files) is not int:
        raise ValueError('production plan required window/file counts are absent')
    actual_windows = sum(len(chain['windows']) for chain in chains)
    if actual_windows != required_windows or len(chains) != required_files:
        if mode == 'extract':
            raise ValueError('extract requires the complete declared schedule')
        raise ValueError('extract-check schedule does not match its frozen plan')
    by_path = {(chain['root'], chain['source_path'], chain['source_metadata_sha256']): chain
               for chain in chains}
    seen = set()
    maximums = []
    for row in files:
        if (not isinstance(row, dict) or row.get('root') not in protocol['roots']
                or type(row.get('source_path')) is not str
                or type(row.get('source_metadata_sha256')) is not str
                or type(row.get('maximum_output_bytes')) is not int
                or row['maximum_output_bytes'] <= 0
                or type(row.get('window_count')) is not int or row['window_count'] <= 0):
            raise ValueError('production plan file reservation is invalid')
        key = (row['root'], row['source_path'], row['source_metadata_sha256'])
        if key in seen or key not in by_path:
            raise ValueError('production plan file does not join the reconstructed schedule')
        if len(by_path[key]['windows']) != row['window_count']:
            raise ValueError('production plan window count does not join its file chain')
        seen.add(key)
        maximums.append(row['maximum_output_bytes'])
    if len(seen) != len(chains):
        raise ValueError('production plan is missing a reconstructed source file')
    reserved = sum(maximums) + plan['coordinator_reserve_bytes']
    if type(available_output_bytes) is not int or available_output_bytes < 0:
        raise ValueError('available derived output is invalid')
    if reserved > available_output_bytes:
        raise ValueError('file reservations plus coordinator reserve exceed the attempt allowance')
    return {
        'file_maximums': maximums,
        'reserved_output_bytes': reserved,
        'coordinator_reserve_bytes': plan['coordinator_reserve_bytes'],
        'source_clock_policy': normalize_source_clock_policy(plan.get('source_clock_policy')),
        'required_window_count': required_windows,
        'required_file_count': required_files,
    }


def production_parameters(protocol, *, latency_ns=DEFAULT_LATENCY_NS, source_clock_policy=None):
    if type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000:
        raise ContractError('production latency scenario is invalid')
    return {
        'latency_ns': latency_ns,
        'native_width_ns': protocol['native_width_ns'],
        'atomic_width_ns': protocol['atomic_width_ns'],
        'source_clock_policy': normalize_source_clock_policy(source_clock_policy),
    }


def authenticate_artifact_reference(reference):
    if not isinstance(reference, dict) or type(reference.get('path')) is not str:
        raise IntegrityError('production artifact reference is invalid')
    path = Path(reference['path'])
    if not path.is_file():
        raise IntegrityError('retained production artifact is absent')
    size = path.stat().st_size
    if type(reference.get('size_bytes')) is not int or size != reference['size_bytes']:
        raise IntegrityError('retained production artifact length changed')
    if file_digest(path) != reference.get('sha256'):
        raise IntegrityError('retained production artifact content changed')
    return reference


def authenticate_retained_payload(value):
    if not isinstance(value, dict):
        raise IntegrityError('production artifact reference is invalid')
    files = value.get('files')
    descriptor = value.get('replay_descriptor')
    if isinstance(files, list):
        for reference in files:
            authenticate_artifact_reference(reference)
        if isinstance(descriptor, dict):
            authenticate_artifact_reference(descriptor)
            return value
        if value.get('encoding') == 'raw-source-quote-replay-v1':
            raise IntegrityError('quote replay lost its descriptor')
        return value
    if isinstance(descriptor, dict):
        authenticate_artifact_reference(descriptor)
        return value
    return authenticate_artifact_reference(value)


def require_registered_attempt(receipt, registered_attempts):
    if not isinstance(registered_attempts, dict):
        raise IntegrityError('reuse requires registered attempt evidence')
    attempt_id = receipt.get('attempt_id')
    attempt = registered_attempts.get(attempt_id)
    if not isinstance(attempt, dict):
        raise IntegrityError('window receipt has no registered prior attempt')
    family = receipt.get('family') or receipt.get('registered_attempt', {}).get('family')
    trial_id = receipt.get('trial_id')
    if (attempt.get('id', attempt_id) != attempt_id
            or (family is not None and attempt.get('family') != family)
            or (trial_id is not None and attempt.get('trial_id') != trial_id)):
        raise IntegrityError('window receipt does not join its registered attempt')
    if attempt.get('status') not in ('running', 'succeeded', 'failed', 'interrupted'):
        raise IntegrityError('registered prior attempt has no retained status')
    return attempt


def authenticate_reused_receipt(receipt, *, window, chain, protocol, producer_identity_value,
                                runtime_versions, source_clock_policy, parameters,
                                registered_attempts, prior_carry_identity, compatible_producer_identities=()):
    if not isinstance(receipt, dict) or receipt.get('kind') != WINDOW_RECEIPT_KIND:
        raise IntegrityError('production window receipt kind is invalid')
    if receipt.get('success') is not True:
        raise IntegrityError('incomplete window receipt cannot be reused')
    require_registered_attempt(receipt, registered_attempts)
    if receipt.get('unit_identity') != production_window_identity(window):
        raise IntegrityError('reused receipt source coordinates do not join the schedule')
    if receipt.get('unit') != window:
        raise IntegrityError('reused receipt is not a member of the reconstructed file chain')
    if window not in chain['windows']:
        raise IntegrityError('reused receipt is outside its physical source lineage')
    if (receipt.get('producer_identity') != producer_identity_value
            and receipt.get('producer_identity') not in compatible_producer_identities):
        raise IntegrityError('reused receipt producer identity changed')
    if receipt.get('runtime_versions') != runtime_versions:
        raise IntegrityError('reused receipt runtime identity changed')
    if receipt.get('parameters') != parameters:
        raise IntegrityError('reused receipt grid/delay/clock definition changed')
    if normalize_source_clock_policy(receipt.get('source_clock_policy')) != normalize_source_clock_policy(source_clock_policy):
        raise IntegrityError('reused receipt source_clock_policy changed')
    if 'protocol_sha256' in protocol and receipt.get('protocol_sha256') != protocol['protocol_sha256']:
        raise IntegrityError('reused receipt protocol identity changed')
    artifacts = receipt.get('artifacts')
    if not isinstance(artifacts, dict):
        raise IntegrityError('reused receipt lost its artifact set')
    for name in ('trades', 'excluded', 'quotes', 'measurement', 'continuation'):
        if name not in artifacts:
            raise IntegrityError('reused receipt is missing a required source artifact')
        authenticate_retained_payload(artifacts[name])
    natives = artifacts.get('native')
    if not isinstance(natives, list):
        raise IntegrityError('reused receipt native artifacts are invalid')
    for reference in natives:
        authenticate_retained_payload(reference)
    continuation = load_production_continuation(artifacts['continuation'])
    if continuation['identity'] != receipt.get('final_continuation_identity'):
        raise IntegrityError('reused continuation identity does not join its receipt')
    if continuation['source_clock_policy'] != normalize_source_clock_policy(receipt.get('source_clock_policy')):
        raise IntegrityError('reused continuation source_clock_policy does not join its receipt')
    if prior_carry_identity is None:
        if receipt.get('initial_continuation_identity') is not None:
            raise IntegrityError('file-start reuse is not an observed prefix')
    elif receipt.get('initial_continuation_identity') != prior_carry_identity:
        raise IntegrityError('reused carry chain is nonadjacent or tampered')
    return {
        'status': 'reused',
        'receipt': receipt,
        'continuation': continuation['measurement_continuation'],
        'continuation_identity': continuation['identity'],
        'source_clock_policy': continuation['source_clock_policy'],
    }


def load_production_continuation(reference):
    payload = read_json_artifact(authenticate_artifact_reference(reference))
    if payload.get('kind') != CONTINUATION_KIND:
        raise IntegrityError('production continuation kind is invalid')
    carry = payload.get('measurement_continuation')
    if not isinstance(carry, dict) or carry.get('completed') is not True or 'sha256' not in carry:
        raise IntegrityError('production continuation lost its measurement carry')
    policy = normalize_source_clock_policy(payload.get('source_clock_policy'))
    if carry['sha256'] != digest({k: v for k, v in carry.items() if k != 'sha256'}):
        raise IntegrityError('production continuation digest changed')
    source = carry.get('source')
    if not isinstance(source, dict) or source.get('sha256') != digest({k: v for k, v in source.items() if k != 'sha256'}):
        raise IntegrityError('production source continuation digest changed')
    identity = {'sha256': carry['sha256'], 'next_start_ns': carry.get('next_start_ns')}
    return {'measurement_continuation': carry, 'source_clock_policy': policy, 'identity': identity}


def continuation_identity(carry):
    if carry is None:
        return None
    return {'sha256': carry['sha256'], 'next_start_ns': carry['next_start_ns']}


def produce_source_window(window, *, protocol, index, coordinates, outputs, data_root,
                          continuation=None, source_clock_policy=None,
                          producer_identity_value, runtime_versions, attempt,
                          latency_ns=DEFAULT_LATENCY_NS, storage_encoding='structural'):
    """Write exact trades/excluded/native, quote replay, and compressed measurements."""
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError('production window requires bounded registered outputs')
    join_window_to_index(window, protocol, index)
    parameters = production_parameters(protocol, latency_ns=latency_ns,
                                       source_clock_policy=source_clock_policy)
    policy = parameters['source_clock_policy']
    identity = production_window_identity(window)
    name = window_artifact_prefix(window)
    source_carry = None if continuation is None else continuation.get('source')
    initial_identity = continuation_identity(continuation)
    events = {
        'trades': ParquetSeries(outputs, f'{name}-trades', encoding=storage_encoding),
        'excluded': ParquetSeries(outputs, f'{name}-excluded', encoding=storage_encoding),
    }
    quotes = QuoteReplaySeries(
        outputs, f'{name}-quotes', data_root=data_root,
        source_index_reference=protocol['source_index'], root=window['root'],
        start_ns=window['event_start_ns'], end_ns=window['event_end_ns'],
        source_paths=(window['source_path'],),
        maximum_scan_rows=protocol['resources']['maximum_source_day_scan_rows'],
        latency_ns=latency_ns, continuation=source_carry,
        **clock_kwargs(source_clock_policy, QuoteReplaySeries.__init__))
    native_storage = []

    def retain_native(table, metadata):
        series = ParquetSeries(outputs, f"{name}-native-{metadata['instrument_id']}",
                               encoding=storage_encoding)
        series.append(table)
        result = series.finish()
        native_storage.append(result)
        return result

    try:
        measured = measure_raw_window(
            data_root=data_root, index=index, coordinates=coordinates, root=window['root'],
            start_ns=window['event_start_ns'], end_ns=window['event_end_ns'],
            source_paths=(window['source_path'],), continuation=continuation,
            maximum_scan_rows=protocol['resources']['maximum_source_day_scan_rows'],
            native_width_ns=protocol['native_width_ns'], atomic_width_ns=protocol['atomic_width_ns'],
            maximum_native_array_bytes=protocol['resources']['maximum_native_array_bytes'],
            latency_ns=latency_ns, retain_trade_batch=events['trades'].append,
            retain_quote_batch=quotes.append, retain_excluded_batch=events['excluded'].append,
            retain_native_table=retain_native,
            **clock_kwargs(source_clock_policy, measure_raw_window))
        storage = {
            'trades': events['trades'].finish(),
            'excluded': events['excluded'].finish(),
            'quotes': quotes.finish(measured['source_manifest']),
        }
    except BaseException:
        for series in (*events.values(), quotes):
            if not series.closed:
                series.abort()
        raise
    counts = measured['source_manifest']['projection']['counts']
    excluded_rows = measured['source_manifest']['trade_exclusions'].get('unique_excluded_trade_rows', 0)
    if (storage['trades']['rows'] != counts['trades']
            or storage['quotes']['rows'] != counts['quote_rows']
            or storage['excluded']['rows'] != excluded_rows):
        raise IntegrityError('complete source scan and retained production caches differ')
    measurement_ref = outputs.json_compressed(
        f'{name}-measurements.json.zst', measured,
        kind='auction_flow_full_window_measurements', measurement_fast_path=True)
    carry = measured['measurement_continuation']
    continuation_ref = outputs.json_compressed(
        f'{name}-continuation.json.zst',
        {'kind': CONTINUATION_KIND, 'source_clock_policy': policy,
         'measurement_continuation': carry},
        kind=CONTINUATION_KIND)
    final_identity = continuation_identity(carry)
    manifest = measured['source_manifest']
    receipt = {
        'kind': WINDOW_RECEIPT_KIND, 'success': True, 'version': VERSION,
        'attempt_id': attempt['attempt_id'], 'trial_id': attempt['trial_id'],
        'family': attempt['family'], 'protocol_sha256': attempt.get('protocol_sha256'),
        'registered_attempt': {'attempt_id': attempt['attempt_id'],
                               'trial_id': attempt['trial_id'], 'family': attempt['family']},
        'producer_identity': producer_identity_value,
        'runtime_versions': runtime_versions,
        'source_clock_policy': policy,
        'parameters': parameters,
        'unit': window,
        'unit_identity': identity,
        'source_metadata_sha256': window['source_metadata_sha256'],
        'coordinate_version': measured['coordinate_manifest_version'],
        'coordinate_snapshot_version': measured['coordinate_snapshot_supplement_version'],
        'initial_continuation_identity': initial_identity,
        'final_continuation_identity': final_identity,
        'counts': counts,
        'source_manifest_identity': {
            'canonical_selected_raw_stream': manifest['canonical_selected_raw_stream'],
            'physical_scan_rows': manifest['physical_scan_rows'],
            'source_all_field_arrow_stream_sha256': manifest.get('source_all_field_arrow_stream_sha256'),
        },
        'status': measured['status'],
        'artifacts': {
            'trades': storage['trades'],
            'excluded': storage['excluded'],
            'quotes': storage['quotes'],
            'native': native_storage,
            'measurement': measurement_ref,
            'continuation': continuation_ref,
        },
        'event_storage': {kind: storage[kind] for kind in ('trades', 'excluded', 'quotes')},
        'native_storage': native_storage,
        'family_statistics_or_model_complete': False,
    }
    receipt_ref = outputs.json(f'{name}-window-receipt.json', receipt, kind=WINDOW_RECEIPT_KIND)
    return {
        'status': 'completed',
        'receipt': receipt,
        'receipt_reference': receipt_ref,
        'continuation': carry,
        'continuation_identity': final_identity,
        'source_clock_policy': policy,
        'counts': counts,
        'event_storage': storage,
        'native_storage': native_storage,
        'measurement': measurement_ref,
    }


def run_file_chain(chain, *, protocol, index, coordinates, outputs, data_root,
                   prior_receipts=(), registered_attempts=None, source_clock_policy=None,
                   producer_identity_value, runtime_versions, attempt,
                   latency_ns=DEFAULT_LATENCY_NS, compatible_producer_identities=()):
    """Process one physical file's scheduled days in order with actual carry.

    Complete contiguous leading windows are reused in place. The first pending
    window and every later day are computed in this attempt. A failure leaves
    later carry-dependent days pending without overwriting prior artifacts.
    """
    if registered_attempts is None:
        raise IntegrityError('reuse requires registered attempt evidence')
    parameters = production_parameters(protocol, latency_ns=latency_ns,
                                       source_clock_policy=source_clock_policy)
    policy = parameters['source_clock_policy']
    by_key = {}
    for receipt in prior_receipts:
        if not isinstance(receipt, dict):
            raise IntegrityError('prior production receipt is invalid')
        unit = receipt.get('unit') if isinstance(receipt.get('unit'), dict) else {}
        key = (unit.get('root'), unit.get('source_path'), unit.get('source_metadata_sha256'),
               unit.get('event_start_ns'), unit.get('event_end_ns'))
        if key in by_key:
            raise IntegrityError('duplicate prior production receipt for one window')
        by_key[key] = receipt
    missing = False
    for window in chain['windows']:
        key = (window['root'], window['source_path'], window['source_metadata_sha256'],
               window['event_start_ns'], window['event_end_ns'])
        if key in by_key:
            if missing:
                raise IntegrityError('noncontiguous reuse is not an observed prefix')
        else:
            missing = True
    results = []
    carry = None
    carry_identity = None
    reuse_prefix = True
    failed = None
    for window in chain['windows']:
        identity = production_window_identity(window)
        key = (window['root'], window['source_path'], window['source_metadata_sha256'],
               window['event_start_ns'], window['event_end_ns'])
        if failed is not None:
            results.append({'status': 'pending', 'unit': window, 'unit_identity': identity,
                            'reason': 'blocked_by_earlier_file_failure'})
            continue
        try:
            join_window_to_index(window, protocol, index)
            candidate = by_key.get(key) if reuse_prefix else None
            if candidate is not None:
                reused = authenticate_reused_receipt(
                    candidate, window=window, chain=chain, protocol=protocol,
                    producer_identity_value=producer_identity_value,
                    runtime_versions=runtime_versions, source_clock_policy=policy,
                    parameters=parameters, registered_attempts=registered_attempts,
                    prior_carry_identity=carry_identity,
                    compatible_producer_identities=compatible_producer_identities)
                results.append({**reused, 'unit': window, 'unit_identity': identity,
                                'receipt_reference': None})
                carry = reused['continuation']
                carry_identity = reused['continuation_identity']
                continue
            reuse_prefix = False
            produced = produce_source_window(
                window, protocol=protocol, index=index, coordinates=coordinates,
                outputs=outputs, data_root=data_root, continuation=carry,
                source_clock_policy=source_clock_policy,
                producer_identity_value=producer_identity_value,
                runtime_versions=runtime_versions, attempt=attempt,
                latency_ns=latency_ns)
        except BaseException as exc:
            failed = {'unit': window, 'unit_identity': identity,
                      'error': f'{type(exc).__name__}: {exc}'}
            results.append({'status': 'failed', 'unit': window, 'unit_identity': identity,
                            'error': failed['error']})
            continue
        results.append({**produced, 'unit': window, 'unit_identity': identity})
        carry = produced['continuation']
        carry_identity = produced['continuation_identity']
    complete = all(row['status'] in ('reused', 'completed') for row in results)
    return {
        'kind': FILE_RECEIPT_KIND,
        'success': complete,
        'file_identity': file_identity(chain),
        'source_clock_policy': policy,
        'windows': results,
        'completed_windows': sum(row['status'] in ('reused', 'completed') for row in results),
        'reused_windows': sum(row['status'] == 'reused' for row in results),
        'pending_units': [row['unit_identity'] for row in results if row['status'] == 'pending'],
        'failures': [row for row in results if row['status'] == 'failed'],
        'family_statistics_or_model_complete': False,
    }


def file_chain_complete(report):
    return bool(report.get('success') is True and not report.get('pending_units')
                and not report.get('failures'))


def summarize_file_reports(reports, *, required_window_count):
    completed, reused, pending, failures = [], [], [], []
    for report in reports:
        failures.extend(report.get('failures', ()))
        for row in report.get('windows', ()):
            if row.get('status') in ('reused', 'completed'):
                completed.append(row['unit_identity'])
            if row.get('status') == 'reused':
                reused.append(row['unit_identity'])
            if row.get('status') == 'pending':
                pending.append(row['unit_identity'])
            if row.get('status') == 'failed':
                failures.append(row)
    complete = (len(completed) == required_window_count and not pending and not failures
                and all(file_chain_complete(report) for report in reports))
    return {
        'required_windows': required_window_count,
        'completed_windows': len(completed),
        'reused_windows': len(reused),
        'pending_units': pending,
        'failures': failures,
        'complete_source_extraction': complete,
        'complete_family_statistics': False,
        'full_project_under_three_hours_verified': False,
        'success': complete,
    }
