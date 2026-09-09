"""Resource-only overlay for the explicitly approved unchanged Jumbo family."""
from copy import deepcopy


PHASE_MODES = {"code_check": "check", "admission_pilot": "pilot", "full_admission": "admit",
               "extract": "develop", "fit": "develop", "confirmation": "confirm"}


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
            "maximum_output_bytes": resources["maximum_derived_output_bytes"], "wall_seconds": wall}
