"""Standard-library hardware and source-unit supervision for auction/flow.

This module does not import scientific measurement code or Jumbo numerical
helpers. Live limits come from the current cgroup, never host CPU or RAM.
"""
from __future__ import annotations

import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import time


KIND = 'auction_flow_user_hardware_execution_v1'
UTILIZATION_KIND = 'auction_flow_user_hardware_execution_v2'
SUPPLIED_VCPUS = 21
SUPPLIED_MEMORY_BYTES = 83_000_000_000
SUPPLIED_GPU = 'NVIDIA RTX A4000'
SUPPLIED_VRAM_BYTES = 16_000_000_000
MAXIMUM_WORKERS_CEILING = 17
AGGREGATE_MEMORY_CEILING = 72 * 1024 ** 3
COORDINATOR_MEMORY_BYTES = 4 * 1024 ** 3
CHILD_MEMORY_BYTES = 4 * 1024 ** 3
MAXIMUM_CHILD_OUTPUT_BYTES = 512 * 1024 ** 2
NATIVE_THREADS_PER_WORKER = 1
GPU_WORKERS = 0
REQUIRED_ATTEMPTS = 32
REQUIRED_CPU_BUDGET_SECONDS = 192000
REQUIRED_CHECK_CPU_SECONDS = 1200
REQUIRED_HARD_CPU_MARGIN_SECONDS = 10
REQUIRED_ATTEMPT_OUTPUT_BYTES = 16 * 1024 ** 3
REQUIRED_STUDY_OUTPUT_BYTES = 256 * 1024 ** 3
REQUIRED_PROTOCOL_MEMORY_BYTES = 4 * 1024 ** 3
V1_UNLIMITED_MEMORY = 2 ** 63 - 4096
POOL_WALL_GUARD_SECONDS = 10
PARENT_TERMINATE_GRACE_SECONDS = 5


class SourceWorkerInterrupt(Exception):
    """Raised from the registered worker signal handler so the pool can reap."""


def parse_cgroup_integer(text):
    raw = text.strip()
    if not raw or raw != raw.strip() or raw in ('True', 'False') or '.' in raw or '+' in raw:
        raise ValueError('invalid effective cgroup resource limits')
    if raw[0] == '-' and raw[1:].isdigit():
        return int(raw)
    if raw.isdigit():
        return int(raw)
    raise ValueError('invalid effective cgroup resource limits')


def require_live_limits(live_limits):
    if (not isinstance(live_limits, dict)
            or not {'cpu_quota_us', 'cpu_period_us', 'memory_limit_bytes'} <= live_limits.keys()):
        raise ValueError('invalid effective cgroup resource limits')
    quota = live_limits.get('cpu_quota_us')
    period = live_limits.get('cpu_period_us')
    memory = live_limits.get('memory_limit_bytes')
    if type(quota) is not int or (quota != -1 and quota <= 0):
        raise ValueError('invalid effective cgroup resource limits')
    if type(period) is not int or period <= 0:
        raise ValueError('invalid effective cgroup resource limits')
    if memory is not None and (type(memory) is not int or memory <= 0):
        raise ValueError('invalid effective cgroup resource limits')
    return {'cpu_quota_us': quota, 'cpu_period_us': period, 'memory_limit_bytes': memory}


def live_hardware_limits(cgroup_root=Path('/sys/fs/cgroup')):
    """Read this allocation's cgroup v1 or v2 limits.

    Host processor counts and system-wide memory totals are not the pod quota.
    Quota is exactly -1 or a positive integer; any other negative is invalid.
    """
    root = Path(cgroup_root)
    if not root.is_dir():
        raise ValueError('invalid effective cgroup resource domain')
    cpu_v1 = root / 'cpu/cpu.cfs_quota_us'
    period_v1 = root / 'cpu/cpu.cfs_period_us'
    cpu_v2 = root / 'cpu.max'
    if cpu_v1.is_file():
        try:
            quota = parse_cgroup_integer(cpu_v1.read_text())
            period = parse_cgroup_integer(period_v1.read_text())
        except (OSError, ValueError) as exc:
            raise ValueError('invalid effective cgroup resource limits') from exc
    elif cpu_v2.is_file():
        try:
            parts = cpu_v2.read_text().split()
            if len(parts) != 2:
                raise ValueError('invalid effective cgroup resource limits')
            quota_text, period_text = parts
            quota = -1 if quota_text == 'max' else parse_cgroup_integer(quota_text)
            period = parse_cgroup_integer(period_text)
        except (OSError, ValueError) as exc:
            raise ValueError('invalid effective cgroup resource limits') from exc
    else:
        raise ValueError('invalid effective cgroup resource domain')
    memory_v1 = root / 'memory/memory.limit_in_bytes'
    memory_v2 = root / 'memory.max'
    try:
        if memory_v1.is_file():
            memory_text = memory_v1.read_text().strip()
        elif memory_v2.is_file():
            memory_text = memory_v2.read_text().strip()
        else:
            raise ValueError('invalid effective cgroup resource domain')
        memory_bytes = None if memory_text == 'max' else parse_cgroup_integer(memory_text)
    except (OSError, ValueError) as exc:
        raise ValueError('invalid effective cgroup resource limits') from exc
    if memory_bytes is not None and memory_bytes >= V1_UNLIMITED_MEMORY:
        memory_bytes = None
    return require_live_limits({
        'cpu_quota_us': quota, 'cpu_period_us': period, 'memory_limit_bytes': memory_bytes,
    })


def require_approval_messages(messages):
    if not isinstance(messages, list) or not messages:
        raise ValueError('hardware execution needs the exact explicit same-family instruction')
    for item in messages:
        if (not isinstance(item, dict) or type(item.get('at')) is not str or not item['at']
                or type(item.get('text')) is not str or not item['text']):
            raise ValueError('hardware execution needs the exact explicit same-family instruction')


def require_unchanged_scientific_resources(protocol, declared=None):
    resources = protocol['resources']
    phases = resources.get('phase_cpu_seconds') or {}
    if (resources.get('cpu_budget_seconds') != REQUIRED_CPU_BUDGET_SECONDS
            or resources.get('hard_cpu_margin_seconds') != REQUIRED_HARD_CPU_MARGIN_SECONDS
            or resources.get('maximum_attempts') != REQUIRED_ATTEMPTS
            or resources.get('maximum_derived_output_bytes') != REQUIRED_ATTEMPT_OUTPUT_BYTES
            or resources.get('maximum_study_output_bytes') != REQUIRED_STUDY_OUTPUT_BYTES
            or resources.get('memory_bytes') != REQUIRED_PROTOCOL_MEMORY_BYTES
            or phases.get('check') != REQUIRED_CHECK_CPU_SECONDS):
        raise ValueError('source-unit execution cannot change registered scientific resource fields')
    if declared is not None and declared != resources:
        raise ValueError('hardware document unchanged_scientific_resources differ from the protocol')
    return {
        'cpu_budget_seconds': resources['cpu_budget_seconds'],
        'hard_cpu_margin_seconds': resources['hard_cpu_margin_seconds'],
        'maximum_attempts': resources['maximum_attempts'],
        'maximum_derived_output_bytes': resources['maximum_derived_output_bytes'],
        'maximum_study_output_bytes': resources['maximum_study_output_bytes'],
        'memory_bytes': resources['memory_bytes'],
        'check_cpu_seconds': phases['check'],
        'per_check_wall_seconds': resources['per_check_wall_seconds'],
        'maximum_output_file_bytes': resources['maximum_output_file_bytes'],
        'supervisor_output_reserve_bytes': resources['supervisor_output_reserve_bytes'],
    }


def plan_source_unit_execution(protocol, allocation, *, live_limits, protocol_sha256):
    """Bind concurrency to supplied hardware and the live cgroup.

    Scientific attempt/CPU/output fields stay exactly the registered values.
    """
    live_limits = require_live_limits(live_limits)
    if not isinstance(allocation, dict) or not isinstance(allocation.get('unchanged_scientific_resources'), dict):
        raise ValueError('hardware document must retain the full unchanged scientific resources')
    scientific = require_unchanged_scientific_resources(
        protocol, allocation.get('unchanged_scientific_resources'))
    resources_before = dict(protocol['resources'])
    phases_before = dict(protocol['resources']['phase_cpu_seconds'])
    approval = allocation.get('approval') or {}
    declared = allocation.get('declared_hardware') or {}
    execution = allocation.get('execution') or {}
    specification = allocation.get('hardware_specification') or {}
    require_approval_messages(approval.get('messages'))
    declared_limits = {KIND: (16, 64 * 1024 ** 3),
                       UTILIZATION_KIND: (17, 72 * 1024 ** 3)}.get(allocation.get('kind'))
    if (declared_limits is None or allocation.get('family') != protocol.get('family')
            or allocation.get('parent_protocol_sha256') != protocol_sha256
            or approval.get('source') != 'explicit_user_instruction'
            or type(specification.get('path')) is not str or not specification['path']
            or type(specification.get('sha256')) is not str or len(specification['sha256']) != 64
            or type(specification.get('size_bytes')) is not int or specification['size_bytes'] <= 0):
        raise ValueError('hardware execution needs the exact explicit same-family instruction')
    workers = execution.get('maximum_workers')
    aggregate = execution.get('aggregate_memory_bytes')
    coordinator = execution.get('coordinator_memory_bytes')
    child = execution.get('child_memory_bytes')
    child_output = execution.get('maximum_child_output_bytes')
    if (declared.get('vcpus') != SUPPLIED_VCPUS or declared.get('memory_bytes') != SUPPLIED_MEMORY_BYTES
            or declared.get('gpu') != SUPPLIED_GPU or declared.get('vram_bytes') != SUPPLIED_VRAM_BYTES
            or type(workers) is not int or workers != declared_limits[0]
            or type(aggregate) is not int or aggregate != declared_limits[1]
            or type(coordinator) is not int or coordinator != COORDINATOR_MEMORY_BYTES
            or type(child) is not int or child != CHILD_MEMORY_BYTES
            or type(child_output) is not int or child_output != MAXIMUM_CHILD_OUTPUT_BYTES
            or execution.get('native_threads_per_worker') != NATIVE_THREADS_PER_WORKER
            or execution.get('gpu_workers') != GPU_WORKERS):
        raise ValueError('invalid bounded source-unit execution settings')
    cores = SUPPLIED_VCPUS
    quota, period = live_limits['cpu_quota_us'], live_limits['cpu_period_us']
    if quota > 0:
        quota_cores = quota // period
        if quota_cores <= 0:
            raise ValueError('effective cpu quota is below one period')
        cores = min(cores, quota_cores)
    memory_ceiling = min(SUPPLIED_MEMORY_BYTES, AGGREGATE_MEMORY_CEILING, aggregate)
    live_memory = live_limits.get('memory_limit_bytes')
    if live_memory is not None:
        memory_ceiling = min(memory_ceiling, live_memory)
    if memory_ceiling < coordinator + child:
        raise ValueError('live allocation cannot support one source child plus coordinator')
    memory_workers = (memory_ceiling - coordinator) // child
    concurrency = min(workers, cores, MAXIMUM_WORKERS_CEILING, memory_workers)
    if type(concurrency) is not int or concurrency < 1:
        raise ValueError('live allocation cannot support one source child plus coordinator')
    if (protocol['resources'] != resources_before
            or protocol['resources']['phase_cpu_seconds'] != phases_before):
        raise ValueError('source-unit execution mutated registered scientific resource fields')
    return {
        'kind': 'auction_flow_source_unit_execution_plan_v1',
        'maximum_concurrency': concurrency,
        'effective_cpu_cores': cores,
        'maximum_workers_ceiling': workers,
        'aggregate_memory_bytes': memory_ceiling,
        'aggregate_memory_ceiling_bytes': aggregate,
        'allocated_address_space_bytes': coordinator + concurrency * child,
        'coordinator_memory_bytes': coordinator,
        'child_memory_bytes': child,
        'native_threads_per_worker': NATIVE_THREADS_PER_WORKER,
        'gpu_workers': GPU_WORKERS,
        'maximum_child_output_bytes': child_output,
        'check_cpu_seconds': scientific['check_cpu_seconds'],
        'hard_cpu_margin_seconds': scientific['hard_cpu_margin_seconds'],
        'cpu_budget_seconds': scientific['cpu_budget_seconds'],
        'maximum_attempts': scientific['maximum_attempts'],
        'maximum_derived_output_bytes': scientific['maximum_derived_output_bytes'],
        'maximum_study_output_bytes': scientific['maximum_study_output_bytes'],
        'protocol_memory_bytes': scientific['memory_bytes'],
        'per_check_wall_seconds': scientific['per_check_wall_seconds'],
        'declared_hardware': {
            'vcpus': declared['vcpus'], 'memory_bytes': declared['memory_bytes'],
            'gpu': declared['gpu'], 'vram_bytes': declared['vram_bytes'],
        },
        'live_limits': {
            'cpu_quota_us': live_limits['cpu_quota_us'],
            'cpu_period_us': live_limits['cpu_period_us'],
            'memory_limit_bytes': live_limits['memory_limit_bytes'],
        },
    }


def actual_source_unit_allocation(planned, window_count, *, concurrency_limit=None):
    if type(window_count) is not int or window_count < 1:
        raise ValueError('source unit executor requires the complete reconstructed window population')
    concurrency = min(planned['maximum_concurrency'], window_count)
    if concurrency_limit is not None:
        if type(concurrency_limit) is not int or concurrency_limit < 1:
            raise ValueError('live source concurrency must be a positive integer')
        concurrency = min(concurrency, concurrency_limit)
    if concurrency < 1:
        raise ValueError('live allocation cannot support one source child plus coordinator')
    allocated = planned['coordinator_memory_bytes'] + concurrency * planned['child_memory_bytes']
    return {
        'actual_concurrency': concurrency,
        'allocated_address_space_bytes': allocated,
        'aggregate_memory_ceiling_bytes': planned.get('aggregate_memory_ceiling_bytes', AGGREGATE_MEMORY_CEILING),
        'maximum_concurrency_ceiling': planned['maximum_concurrency'],
    }


def parse_proc_stat(text):
    close = text.rfind(')')
    open_paren = text.find('(')
    if open_paren < 0 or close < 0 or close < open_paren:
        raise ValueError('invalid process stat')
    fields = text[close + 2:].split()
    if len(fields) < 22:
        raise ValueError('invalid process stat')
    return {
        'pid': int(text[:open_paren].strip()),
        'state': fields[0],
        'ppid': int(fields[1]),
        'pgrp': int(fields[2]),
        'session': int(fields[3]),
        'utime_ticks': int(fields[11]),
        'stime_ticks': int(fields[12]),
        'rss_pages': int(fields[21]),
    }


def process_usage(pid, *, proc_root=Path('/proc'), clock_ticks=None, page_size=None):
    if clock_ticks is None:
        clock_ticks = os.sysconf('SC_CLK_TCK')
    if page_size is None:
        page_size = os.sysconf('SC_PAGESIZE')
    if type(clock_ticks) is not int or clock_ticks <= 0 or type(page_size) is not int or page_size <= 0:
        raise ValueError('invalid process accounting clock or page size')
    path = Path(proc_root) / str(pid) / 'stat'
    try:
        parsed = parse_proc_stat(path.read_text())
    except FileNotFoundError:
        return {'cpu_seconds': 0.0, 'rss_bytes': 0}
    return {
        'cpu_seconds': (parsed['utime_ticks'] + parsed['stime_ticks']) / clock_ticks,
        'rss_bytes': parsed['rss_pages'] * page_size,
    }


def process_cpu_seconds(pid, *, proc_root=Path('/proc'), clock_ticks=None):
    return process_usage(pid, proc_root=proc_root, clock_ticks=clock_ticks)['cpu_seconds']


def process_rss_bytes(pid, *, proc_root=Path('/proc'), page_size=None):
    return process_usage(pid, proc_root=proc_root, page_size=page_size)['rss_bytes']


def wait4_cpu_seconds(usage):
    return usage.ru_utime + usage.ru_stime


def rusage_children_cpu_seconds():
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return usage.ru_utime + usage.ru_stime


def aggregate_cpu_seconds(*, coordinator_cpu_seconds, reaped_child_cpu_seconds, live_pids,
                          proc_root=Path('/proc'), clock_ticks=None):
    """Self + all reaped children (RUSAGE_CHILDREN) + live unreaped pool children."""
    if type(coordinator_cpu_seconds) is bool or type(reaped_child_cpu_seconds) is bool:
        raise ValueError('aggregate CPU components cannot be negative')
    if any(not math.isfinite(value) or value < 0
           for value in (coordinator_cpu_seconds, reaped_child_cpu_seconds)):
        raise ValueError('aggregate CPU components cannot be negative')
    live = 0.0
    for pid in live_pids:
        live += process_cpu_seconds(pid, proc_root=proc_root, clock_ticks=clock_ticks)
    return coordinator_cpu_seconds + reaped_child_cpu_seconds + live


def aggregate_rss_bytes(*, coordinator_pid, live_pids, proc_root=Path('/proc'), page_size=None):
    total = process_rss_bytes(coordinator_pid, proc_root=proc_root, page_size=page_size)
    for pid in live_pids:
        total += process_rss_bytes(pid, proc_root=proc_root, page_size=page_size)
    return total


def remaining_self_cpu_rlimits(soft_seconds, hard_seconds, children_cpu_seconds):
    if type(soft_seconds) is not int or type(hard_seconds) is not int:
        raise ValueError('aggregate CPU thresholds must be the registered integer limits')
    if type(children_cpu_seconds) is bool or type(children_cpu_seconds) not in (int, float):
        raise ValueError('reaped child CPU is invalid')
    if not math.isfinite(children_cpu_seconds) or children_cpu_seconds < 0:
        raise ValueError('reaped child CPU is invalid')
    remaining_soft = math.floor(soft_seconds - children_cpu_seconds)
    remaining_hard = math.floor(hard_seconds - children_cpu_seconds)
    if remaining_soft <= 0 or remaining_hard <= 0:
        raise ValueError('remaining coordinator CPU allowance is exhausted')
    if remaining_soft > remaining_hard:
        remaining_soft = remaining_hard
    return remaining_soft, remaining_hard


def apply_remaining_coordinator_cpu_limit(soft_seconds, hard_seconds, *, children_cpu_seconds=None,
                                          set_limit=True):
    if children_cpu_seconds is None:
        children_cpu_seconds = rusage_children_cpu_seconds()
    remaining_soft, remaining_hard = remaining_self_cpu_rlimits(
        soft_seconds, hard_seconds, children_cpu_seconds)
    current_soft, current_hard = resource.getrlimit(resource.RLIMIT_CPU)
    if current_hard not in (-1, resource.RLIM_INFINITY):
        remaining_hard = min(remaining_hard, current_hard)
    if current_soft not in (-1, resource.RLIM_INFINITY):
        remaining_soft = min(remaining_soft, current_soft)
    if remaining_soft > remaining_hard:
        remaining_soft = remaining_hard
    if remaining_soft <= 0 or remaining_hard <= 0:
        raise ValueError('remaining coordinator CPU allowance is exhausted')
    if set_limit:
        resource.setrlimit(resource.RLIMIT_CPU, (remaining_soft, remaining_hard))
    return remaining_soft, remaining_hard


def reserved_child_output_bytes(unit_count, maximum_child_output_bytes):
    if type(unit_count) is not int or unit_count < 0:
        raise ValueError('source unit count is invalid')
    if type(maximum_child_output_bytes) is not int or maximum_child_output_bytes <= 0:
        raise ValueError('source child output bound is invalid')
    return unit_count * maximum_child_output_bytes


def require_output_reservation(unit_count, maximum_child_output_bytes, available_bytes):
    reserved = reserved_child_output_bytes(unit_count, maximum_child_output_bytes)
    if type(available_bytes) is not int or available_bytes < 0:
        raise ValueError('available derived output is invalid')
    if reserved > available_bytes:
        raise ValueError('source-unit output reservation exceeds remaining derived-output allowance')
    if reserved > REQUIRED_ATTEMPT_OUTPUT_BYTES:
        raise ValueError('source-unit output reservation exceeds the unchanged check output allowance')
    return reserved


def directory_file_bytes(directory):
    root = Path(directory)
    if not root.is_dir():
        return 0
    total = 0
    for path in root.rglob('*'):
        if path.is_file():
            total += path.stat().st_size
    return total


def join_directory_bytes(directories):
    return sum(directory_file_bytes(directory) for directory in directories)


def artifacts_allowance_after_packet(maximum_child_output_bytes, packet_bytes):
    if type(packet_bytes) is not int or packet_bytes < 0:
        raise ValueError('source unit packet size is invalid')
    if type(maximum_child_output_bytes) is not int or maximum_child_output_bytes <= 0:
        raise ValueError('source child output bound is invalid')
    if packet_bytes >= maximum_child_output_bytes:
        raise ValueError('source unit packet consumes the child output reservation')
    return maximum_child_output_bytes - packet_bytes


def charge_child_output_bytes(outputs, directories, *, reservation_per_child, evidence):
    """Join every retained child byte once, then fail if a reservation was exceeded."""
    child_bytes = join_directory_bytes(directories)
    overruns = []
    for directory in directories:
        size = directory_file_bytes(directory)
        if size > reservation_per_child:
            overruns.append({'directory': str(directory), 'size_bytes': size})
    outputs.written += child_bytes
    evidence['joined_output_bytes'] = child_bytes
    evidence['child_directory_overruns'] = overruns
    if overruns or outputs.written > outputs.maximum_total:
        outputs.failed = True
        raise ValueError('joined source-unit output exceeds a declared reservation; retained bytes charged')
    return child_bytes


def unit_identity(unit):
    return {
        'root': unit['root'],
        'role': unit['role'],
        'source_path': unit['source_path'],
        'event_start_ns': unit['event_start_ns'],
        'event_end_ns': unit['event_end_ns'],
        'source_variant': unit['source_variant'],
        'cash_date': unit.get('cash_date'),
    }


def require_unit_identity(windows, ordinal, declared):
    if type(ordinal) is not int or not 0 <= ordinal < len(windows):
        raise ValueError('source unit ordinal is outside the reconstructed schedule')
    unit = windows[ordinal]
    expected = unit_identity(unit)
    if declared != expected:
        raise ValueError('source unit ordinal/identity changed')
    return unit


def require_complete_ordinals(ordinals):
    if not isinstance(ordinals, (list, tuple)) or not ordinals:
        raise ValueError('source unit jobs must be a complete unique ordinal sequence')
    if any(type(item) is not int or item < 0 for item in ordinals):
        raise ValueError('source unit ordinal is invalid')
    if len(set(ordinals)) != len(ordinals) or sorted(ordinals) != list(range(len(ordinals))):
        raise ValueError('source unit jobs must be a complete unique ordinal sequence')
    return list(ordinals)


def source_unit_namespace(attempt_id, ordinal, *, runs_root):
    if type(attempt_id) is not str or not attempt_id or '/' in attempt_id or attempt_id in ('.', '..'):
        raise ValueError('source unit attempt identity is invalid')
    if type(ordinal) is not int or ordinal < 0:
        raise ValueError('source unit ordinal is invalid')
    directory = Path(runs_root) / attempt_id / 'outputs' / f'source-unit-{ordinal:02d}'
    return directory.resolve(), (directory / 'packet.json').resolve()


def require_source_unit_namespace(*, attempt_id, ordinal, child_packet_path, output_directory, runs_root):
    expected_dir, expected_packet = source_unit_namespace(attempt_id, ordinal, runs_root=runs_root)
    if Path(child_packet_path).resolve() != expected_packet:
        raise ValueError('source unit packet is outside the registered attempt namespace')
    if Path(output_directory).resolve() != expected_dir:
        raise ValueError('source unit output directory is outside the registered attempt namespace')
    return expected_dir, expected_packet


def require_reference_in_namespace(reference, artifacts_directory):
    if not isinstance(reference, dict) or type(reference.get('path')) is not str:
        raise ValueError('source unit result reference is invalid')
    artifacts = Path(artifacts_directory).resolve()
    path = Path(reference['path']).resolve()
    if path != artifacts and artifacts not in path.parents:
        raise ValueError('source unit result escaped its artifacts namespace')
    return path


def require_joined_receipt(receipt, *, packet, wait4_child, unit, coordinator_pid):
    if not isinstance(receipt, dict) or receipt.get('success') is not True:
        raise ValueError('source unit receipt is not successful')
    if (receipt.get('attempt_id') != packet['attempt_id']
            or receipt.get('trial_id') != packet['trial_id']
            or receipt.get('protocol_sha256') != packet['protocol_sha256']
            or receipt.get('code_snapshot') != packet['code_snapshot']
            or receipt.get('configuration') != packet['configuration']
            or receipt.get('coordinator_pid') != coordinator_pid
            or receipt.get('child_pid') != wait4_child['pid']
            or receipt.get('ordinal') != wait4_child['ordinal']
            or receipt.get('unit_identity') != unit_identity(unit)
            or receipt.get('unit') != unit):
        raise ValueError('source unit receipt identity does not join its coordinator packet')
    return receipt


def require_parent_identity(*, coordinator_pid, supervisor_pid, proc_root=Path('/proc')):
    if type(coordinator_pid) is not int or coordinator_pid <= 1:
        raise ValueError('source unit coordinator pid is invalid')
    if type(supervisor_pid) is not int or supervisor_pid <= 0:
        raise ValueError('source unit supervisor pid is invalid')
    if os.getppid() != coordinator_pid:
        raise ValueError('source unit parent identity mismatch')
    if os.getpgid(0) != os.getpgid(coordinator_pid) or os.getpgrp() != os.getpgid(coordinator_pid):
        raise ValueError('source unit is not in the registered worker process group')
    parsed = parse_proc_stat((Path(proc_root) / str(coordinator_pid) / 'stat').read_text())
    if parsed['ppid'] != supervisor_pid:
        raise ValueError('source unit coordinator is not the registered supervisor child')
    if parsed['pgrp'] != os.getpgid(0) or parsed['session'] != os.getsid(0):
        raise ValueError('source unit process-group chain changed')
    return parsed


def pool_wall_deadline(worker_started, wall_seconds, *, guard_seconds=POOL_WALL_GUARD_SECONDS):
    if type(wall_seconds) is not int or wall_seconds <= 0 or type(guard_seconds) is not int or guard_seconds <= 0:
        raise ValueError('pool wall watchdog is invalid')
    deadline = worker_started + wall_seconds - guard_seconds
    if deadline <= worker_started:
        raise ValueError('pool wall guard leaves no finite watchdog')
    return deadline


def conservative_attempt_cpu_seconds(*, wait4_usage, accounting_complete, hard_cpu_seconds):
    if wait4_usage is not None:
        charged = wait4_cpu_seconds(wait4_usage)
        if accounting_complete:
            return charged
        return max(charged, hard_cpu_seconds)
    return hard_cpu_seconds


def cleanup_reaped_coordinator_group(pid, *, proc_root=Path('/proc')):
    """Stop survivors after the registered, dedicated-session leader was reaped.

    Unreaped descendants are absent from its wait4 receipt, so any surviving
    group member makes the final CPU accounting incomplete.
    """
    if type(pid) is not int or pid <= 0 or pid == os.getpgrp():
        raise ValueError('only a registered dedicated coordinator group may be cleaned')
    survivors = []
    for entry in Path(proc_root).iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            member = parse_proc_stat((entry / 'stat').read_text())
        except FileNotFoundError:
            continue
        if member['pgrp'] == pid and member['session'] == pid:
            survivors.append(member['pid'])
    if survivors:
        try:
            os.killpg(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    return {
        'group_killed': bool(survivors), 'surviving_group_pids': sorted(survivors),
        'cpu_accounting_complete': not survivors,
        'cpu_accounting_uncertainty': (
            'coordinator exited with descendants outside its wait4 receipt' if survivors else None),
    }


def terminate_then_kill_group(pid, *, grace_seconds=PARENT_TERMINATE_GRACE_SECONDS, poll_seconds=0.05):
    """SIGTERM the coordinator, wait a finite grace, then kill the group if needed."""
    if type(pid) is not int or pid <= 0:
        raise ValueError('coordinator pid is invalid')
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    deadline = time.monotonic() + grace_seconds
    while time.monotonic() < deadline:
        try:
            waited, status, usage = os.wait4(pid, os.WNOHANG)
        except ChildProcessError:
            cleanup = cleanup_reaped_coordinator_group(pid)
            return {'usage': None, 'exit_code': None, **cleanup,
                    'cpu_accounting_complete': False,
                    'cpu_accounting_uncertainty': 'coordinator vanished before wait4'}
        if waited:
            try:
                exit_code = os.waitstatus_to_exitcode(status)
            except ValueError:
                exit_code = 1
            return {'usage': usage, 'exit_code': exit_code,
                    **cleanup_reaped_coordinator_group(pid)}
        time.sleep(poll_seconds)
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        waited, status, usage = os.wait4(pid, 0)
        try:
            exit_code = os.waitstatus_to_exitcode(status)
        except ValueError:
            exit_code = 1
        return {'usage': usage, 'exit_code': exit_code, 'group_killed': True,
                'cpu_accounting_complete': False,
                'cpu_accounting_uncertainty': 'process-group kill may have prevented descendant wait4'}
    except (ProcessLookupError, ChildProcessError):
        return {'usage': None, 'exit_code': None, 'group_killed': True,
                'cpu_accounting_complete': False,
                'cpu_accounting_uncertainty': 'process-group kill may have prevented descendant wait4'}


def supervise_source_children(jobs, *, concurrency, cpu_soft_seconds, cpu_hard_seconds,
                              wall_deadline_monotonic, allocated_address_space_bytes,
                              coordinator_cpu=time.process_time,
                              reaped_children_cpu=rusage_children_cpu_seconds,
                              coordinator_pid=None, proc_root=Path('/proc'),
                              clock_ticks=None, page_size=None, poll_seconds=0.2,
                              evidence=None):
    """Run independent source-unit argv vectors and reap every launched child.

    Aggregate CPU is coordinator self-time plus the coordinator's entire
    RUSAGE_CHILDREN plus live unreaped pool-child ``/proc/<pid>/stat`` ticks.
    """
    require_complete_ordinals([job['ordinal'] for job in jobs])
    if type(concurrency) is not int or concurrency < 1:
        raise ValueError('source unit concurrency must be a positive integer')
    if type(cpu_soft_seconds) is not int or type(cpu_hard_seconds) is not int:
        raise ValueError('aggregate CPU thresholds must be the registered integer limits')
    if cpu_soft_seconds <= 0 or cpu_hard_seconds < cpu_soft_seconds:
        raise ValueError('aggregate CPU thresholds are invalid')
    if cpu_hard_seconds - cpu_soft_seconds != REQUIRED_HARD_CPU_MARGIN_SECONDS:
        raise ValueError('hard CPU margin must remain the registered 10-second bound')
    if type(allocated_address_space_bytes) is not int or allocated_address_space_bytes <= 0:
        raise ValueError('allocated coordinator+child address space is invalid')
    if clock_ticks is None:
        clock_ticks = os.sysconf('SC_CLK_TCK')
    if page_size is None:
        page_size = os.sysconf('SC_PAGESIZE')
    if coordinator_pid is None:
        coordinator_pid = os.getpid()
    report = evidence if evidence is not None else {}
    pending = list(jobs)
    live = {}
    completed = {}
    pool_wait4_cpu = 0.0
    observed_rss_max = 0
    started = time.monotonic()

    def sample():
        live_cpu = 0.0
        rss = process_rss_bytes(coordinator_pid, proc_root=proc_root, page_size=page_size)
        for pid in live:
            usage = process_usage(pid, proc_root=proc_root, clock_ticks=clock_ticks, page_size=page_size)
            live_cpu += usage['cpu_seconds']
            rss += usage['rss_bytes']
        self_cpu = coordinator_cpu()
        children_cpu = reaped_children_cpu()
        return self_cpu + children_cpu + live_cpu, rss, self_cpu, children_cpu, live_cpu

    def record(pid, status, usage):
        nonlocal pool_wait4_cpu
        state = live.pop(pid)
        cpu = wait4_cpu_seconds(usage)
        pool_wait4_cpu += cpu
        try:
            exit_code = os.waitstatus_to_exitcode(status)
        except ValueError:
            exit_code = 1
        state['process'].returncode = exit_code
        row = {
            'ordinal': state['ordinal'],
            'pid': pid,
            'exit_code': exit_code,
            'cpu_seconds': cpu,
            'wall_seconds': time.monotonic() - state['started'],
            'wait4_peak_rss_bytes': usage.ru_maxrss * 1024,
            'success': exit_code == 0,
        }
        completed[state['ordinal']] = row
        return row

    def stop_live():
        for pid in list(live):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def reap_live():
        for pid in list(live):
            try:
                waited, status, usage = os.wait4(pid, 0)
            except ChildProcessError:
                live.pop(pid, None)
                continue
            if waited:
                record(pid, status, usage)

    def publish():
        snapshot = sample()
        self_cpu, children_cpu, live_cpu = snapshot[2], snapshot[3], snapshot[4]
        children = [completed[index] for index in sorted(completed)]
        peaks = [row['wait4_peak_rss_bytes'] for row in children]
        report.update({
            'kind': 'auction_flow_source_unit_parallel_execution_v1',
            'concurrency': concurrency,
            'allocated_address_space_bytes': allocated_address_space_bytes,
            'observed_aggregate_rss_bytes': observed_rss_max,
            'per_process_wait4_peak_rss_bytes': max(peaks) if peaks else 0,
            'coordinator_cpu_seconds': self_cpu,
            'all_reaped_child_cpu_seconds': children_cpu,
            'pool_child_wait4_cpu_seconds': pool_wait4_cpu,
            'live_unreaped_cpu_seconds': live_cpu,
            'aggregate_cpu_seconds': self_cpu + children_cpu + live_cpu,
            'children': children,
            'launched_units': len(completed),
            'pending_units': len(pending),
            'wall_seconds': time.monotonic() - started,
        })
        return report

    try:
        while pending or live:
            if time.monotonic() > wall_deadline_monotonic:
                stop_live()
                reap_live()
                publish()
                raise ValueError('source unit wall watchdog expired')
            total_cpu, rss, _, _, _ = sample()
            observed_rss_max = max(observed_rss_max, rss)
            if total_cpu >= cpu_soft_seconds:
                stop_live()
                reap_live()
                publish()
                raise ValueError('aggregate source-check CPU reached the soft threshold')
            if rss > allocated_address_space_bytes:
                stop_live()
                reap_live()
                publish()
                raise ValueError('observed aggregate RSS exceeds allocated coordinator+child address space')
            while pending and len(live) < concurrency:
                job = pending.pop(0)
                argv = job.get('argv')
                if (not isinstance(argv, (list, tuple)) or isinstance(argv, (str, bytes))
                        or not argv or any(type(part) is not str for part in argv)):
                    raise ValueError('source unit command must be an explicit argument vector')
                process = subprocess.Popen(
                    list(argv), cwd=job.get('cwd'), env=job.get('env'),
                    start_new_session=False, close_fds=True)
                live[process.pid] = {
                    'ordinal': job['ordinal'], 'process': process,
                    'started': time.monotonic(), 'job': job,
                }
            finished = []
            for pid in list(live):
                waited, status, usage = os.wait4(pid, os.WNOHANG)
                if waited:
                    finished.append(record(pid, status, usage))
            if any(not row['success'] for row in finished):
                stop_live()
                reap_live()
                publish()
                raise ValueError('source unit failed; remaining children stopped and reaped')
            if pending or live:
                time.sleep(poll_seconds)
    except BaseException:
        stop_live()
        reap_live()
        publish()
        raise
    if live:
        stop_live()
        reap_live()
        publish()
        raise ValueError('source unit supervisor exited with unreaped children')
    if len(completed) != len(jobs) or any(index not in completed for index in range(len(jobs))):
        publish()
        raise ValueError('source units incomplete; skipped units are not results')
    if any(not completed[index]['success'] for index in range(len(jobs))):
        publish()
        raise ValueError('source unit failed; skipped units are not results')
    return publish()
