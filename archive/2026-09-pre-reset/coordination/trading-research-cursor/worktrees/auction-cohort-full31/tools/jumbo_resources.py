"""Resource-only overlay for the explicitly approved unchanged Jumbo family."""
from copy import deepcopy
from pathlib import Path


PHASE_MODES = {"code_check": "check", "admission_pilot": "pilot", "full_admission": "admit",
               "extract": "develop", "fit": "develop", "confirmation": "confirm"}
HARDWARE_MAXIMUM_MEMORY_BYTES = 64 * 1024**3


def live_hardware_limits(cgroup_root=Path('/sys/fs/cgroup')):
    """Read effective pod limits, never the host's CPU count or total RAM."""
    root = Path(cgroup_root)
    cpu = root / 'cpu/cpu.cfs_quota_us'
    if cpu.is_file():
        quota = int(cpu.read_text())
        period = int((root / 'cpu/cpu.cfs_period_us').read_text())
    else:
        quota_text, period_text = (root / 'cpu.max').read_text().split()
        quota = -1 if quota_text == 'max' else int(quota_text)
        period = int(period_text)
    memory = root / 'memory/memory.limit_in_bytes'
    memory_text = (memory if memory.is_file() else root / 'memory.max').read_text().strip()
    memory_bytes = None if memory_text == 'max' else int(memory_text)
    if period <= 0 or quota == 0 or (memory_bytes is not None and memory_bytes <= 0):
        raise ValueError('invalid effective cgroup resource limits')
    return {'cpu_quota_us': quota, 'cpu_period_us': period, 'memory_limit_bytes': memory_bytes}


def apply_hardware_execution(protocol, allocation, *, budget_reference, live_limits):
    """Apply the later explicit hardware instruction without changing spending.

    The separate retained instruction supersedes the old 4 GiB job ceiling.
    Its exact document, hardware specification and budget join are verified by
    the supervisor and worker. Native kernels keep their single-thread policy;
    independent families share one process and its aggregate CPU/RAM limits.
    """
    if (allocation.get('kind') != 'jumbo_user_hardware_execution_v1'
            or allocation.get('family') != protocol['family']
            or allocation.get('budget_authorization') != budget_reference
            or allocation.get('approval', {}).get('source') != 'explicit_user_instruction'
            or not allocation.get('approval', {}).get('messages')):
        raise ValueError('hardware execution needs the exact explicit same-family instruction and budget')
    declared, execution = allocation['declared_hardware'], allocation['execution']
    workers, memory = execution['family_workers'], execution['memory_bytes']
    if (type(workers) is not int or workers <= 0 or type(memory) is not int or memory <= 0
            or type(declared['vcpus']) is not int or declared['vcpus'] <= 0
            or type(declared['memory_bytes']) is not int or declared['memory_bytes'] <= 0
            or execution.get('native_threads_per_worker') != 1 or execution.get('gpu_workers') != 0):
        raise ValueError('invalid bounded independent-family execution settings')
    cores = declared['vcpus']
    if live_limits['cpu_quota_us'] > 0:
        cores = min(cores, live_limits['cpu_quota_us'] // live_limits['cpu_period_us'])
    memory_ceiling = min(declared['memory_bytes'], HARDWARE_MAXIMUM_MEMORY_BYTES)
    if live_limits['memory_limit_bytes'] is not None:
        memory_ceiling = min(memory_ceiling, live_limits['memory_limit_bytes'])
    if workers > cores or memory > memory_ceiling:
        raise ValueError('execution exceeds the supplied hardware or the effective pod allocation')
    result = deepcopy(protocol)
    result['resources'].update(memory_bytes=memory, family_workers=workers)
    return result


def require_same_verification_resources(baseline, current):
    """Attempt-count-only approvals do not change a measured phase workload.

    The registry still validates and appends the exact current user approval,
    previous balance and unchanged scientific-family identity. This narrowly
    rejects CPU/memory/output changes; they need their own verification plan.
    """
    if (baseline.get("kind") != "family_budget_authorization_v1"
            or current.get("kind") != "family_budget_authorization_v1"
            or current.get("family") != baseline.get("family")
            or current.get("base_family_sha256") != baseline.get("base_family_sha256")
            or current.get("base_protocol") != baseline.get("base_protocol")
            or current.get("approval", {}).get("source") != "explicit_user_approval"):
        raise ValueError("attempt-count override differs from its authorized scientific family")
    fields = ("cpu_seconds_per_phase", "hard_cpu_margin_seconds", "memory_bytes", "maximum_derived_output_bytes")
    old, new = baseline["resource_limits"], current["resource_limits"]
    if (any(new.get(k) != old.get(k) for k in fields)
            or current["authorized_limits"]["cpu_budget_seconds"] != baseline["authorized_limits"]["cpu_budget_seconds"]
            or new.get("maximum_attempts_total") != current["authorized_limits"]["max_attempts"]
            or new.get("cumulative_cpu_seconds_total") != current["authorized_limits"]["cpu_budget_seconds"]):
        raise ValueError("only an explicitly approved attempt-count change can reuse this resource verification")


def require_approved_execution_resources(baseline, current, execution_plan):
    """A new bounded resource plan still needs the exact appended user approval.

    The measured scientific workload is unchanged. A changed execution-plan
    identity requires its new registered check before fitting/confirmation.
    An envelope is only a ceiling for an approval; it is not an authorization.
    """
    envelope = execution_plan.get('resource_verification_envelope')
    if envelope is None:
        return require_same_verification_resources(baseline, current)
    if (envelope.get('kind') != 'jumbo_measured_resource_envelope_v1'
            or current.get('kind') != 'family_budget_authorization_v1'
            or baseline.get('kind') != 'family_budget_authorization_v1'
            or any(current.get(k) != baseline.get(k) for k in ('family', 'base_family_sha256', 'base_protocol'))
            or current.get('approval', {}).get('source') != 'explicit_user_approval'
            or not execution_plan.get('complete_resource_review')):
        raise ValueError('resource envelope requires explicit same-family approval and complete measured evidence')
    old, new = baseline['resource_limits'], current['resource_limits']
    ceilings = envelope['resource_limits']
    for key in ('memory_bytes', 'hard_cpu_margin_seconds'):
        if new.get(key) != old.get(key) or ceilings.get(key) != old.get(key):
            raise ValueError('memory and hard margin are outside this resource amendment')
    if set(new['cpu_seconds_per_phase']) != set(old['cpu_seconds_per_phase']):
        raise ValueError('resource amendment changed the scientific phase catalogue')
    for phase, amount in new['cpu_seconds_per_phase'].items():
        if type(amount) is not int or not old['cpu_seconds_per_phase'][phase] <= amount <= ceilings['cpu_seconds_per_phase'][phase]:
            raise ValueError('phase CPU is outside the explicitly bounded execution plan')
    for key in ('maximum_derived_output_bytes', 'maximum_attempts_total', 'cumulative_cpu_seconds_total'):
        value = new.get(key)
        if type(value) is not int or not old[key] <= value <= ceilings[key]:
            raise ValueError('resource approval is outside the declared envelope')
    if (new['maximum_attempts_total'] != current['authorized_limits']['max_attempts']
            or new['cumulative_cpu_seconds_total'] != current['authorized_limits']['cpu_budget_seconds']):
        raise ValueError('authorization counts disagree with its resource limits')


def cpu_limit(protocol, phase):
    limits = protocol["resources"]
    return limits.get("phase_cpu_seconds", {}).get(phase, limits["mode_cpu_seconds"][PHASE_MODES[phase]])


def amended_protocol(protocol, protocol_sha256, authorization):
    """Keep original protocol bytes/identity; validate a separate resource overlay."""
    if (authorization.get("kind") != "family_budget_authorization_v1"
            or authorization.get("family") != protocol["family"]
            or authorization.get("base_protocol", {}).get("sha256") != protocol_sha256
            or authorization.get("approval", {}).get("source") != "explicit_user_approval"):
        raise ValueError("resource amendment is not authorized for the frozen protocol")
    resource = authorization["resource_limits"]
    cpu = resource["cpu_seconds_per_phase"]
    if (set(cpu) != {"code_check", "extract", "fit", "confirmation"}
            or any(type(v) is not int or v <= 0 for v in cpu.values())
            or resource["memory_bytes"] != protocol["resources"]["memory_bytes"]
            or type(resource['maximum_derived_output_bytes']) is not int
            or not protocol['resources']['maximum_derived_output_bytes'] <= resource['maximum_derived_output_bytes'] <= 1024**3
            or resource["hard_cpu_margin_seconds"] != protocol["resources"]["hard_cpu_margin_seconds"]):
        raise ValueError("invalid resource-only phase overlay")
    result = deepcopy(protocol)
    result["resources"].update(phase_cpu_seconds=cpu,
        maximum_derived_output_bytes=resource['maximum_derived_output_bytes'],
        maximum_attempts=authorization["authorized_limits"]["max_attempts"],
        cpu_budget_seconds=authorization["authorized_limits"]["cpu_budget_seconds"])
    return result


def worker_limits(protocol, phase):
    resources = protocol["resources"]
    cpu = cpu_limit(protocol, phase)
    hard = cpu + resources["hard_cpu_margin_seconds"]
    # The finite watchdog must permit use of the explicitly approved CPU.
    # It consumes no extra CPU allowance; the process CPU limit is binding.
    wall = max(resources["wall_seconds"], 2 * hard)
    return {"cpu_seconds": cpu, "hard_cpu_seconds": hard,
            "memory_bytes": resources["memory_bytes"],
            "maximum_output_bytes": resources["maximum_derived_output_bytes"], "wall_seconds": wall,
            "family_workers": resources.get('family_workers', 1)}
