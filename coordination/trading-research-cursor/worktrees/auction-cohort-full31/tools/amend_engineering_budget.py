"""Retain one explicit engineering extension without altering its predecessor."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
import hashlib
import sys

from trading_research.operations.artifacts import ArtifactRef, publish_new
from trading_research.operations.trials import TrialRegistry
from engineering_batch_contract import ROOT, bounded_metadata_bytes, package_path, registration_budget


def main():
    amendment_path, destination = (package_path(value) for value in sys.argv[1:])
    if (not amendment_path.is_relative_to(ROOT / 'reports')
            or not destination.is_relative_to(ROOT / 'reports') or destination == amendment_path):
        raise ValueError('distinct retained report paths required')
    if not destination.parent.is_dir() or destination.exists() and not destination.is_file():
        raise ValueError('registration report requires an existing regular parent directory and file destination')
    raw = bounded_metadata_bytes(amendment_path)
    amendment = json.loads(raw)
    registry = TrialRegistry(ROOT / 'evidence/trials')
    state = registry.state()
    parent = state['families'][amendment['parent_family']]['protocol']
    if destination == package_path(amendment['parent_registration']['path']):
        raise ValueError('original registration is immutable')
    ref = ArtifactRef(hashlib.sha256(raw).hexdigest(), len(raw), 'engineering_budget_amendment')
    family_name = amendment['additional_family']
    existing = state['families'].get(family_name)
    registration = ({**parent, 'family': family_name, 'budget_amendment': asdict(ref),
                     'registered_at': datetime.now(timezone.utc).isoformat()}
                    if existing is None else existing['protocol'])
    if registration.get('budget_amendment') != asdict(ref):
        raise ValueError('existing extension names another immutable amendment')
    attempts, cpu = registration_budget(registry, registration, amendment_bytes=raw)
    encoded = (json.dumps(registration, indent=2, sort_keys=True) + '\n').encode()
    if destination.exists() and bounded_metadata_bytes(destination) != encoded:
        raise ValueError('extension report already contains different bytes')
    # All semantic/path checks precede publication. A process loss after the
    # immutable family append can be recovered by this exact idempotent call.
    retained = registry.artifacts.put_bytes(raw, kind='engineering_budget_amendment')
    if retained != ref:
        raise ValueError('retained amendment identity differs from preflight')
    registry.register_family(family_name, scope_ids=tuple(parent['scope_ids']),
                             protocol=registration, max_attempts=attempts, cpu_budget_seconds=cpu)
    publish_new(destination, encoded)
    print(json.dumps({'family': family_name, 'additional_attempts': attempts,
                      'additional_cpu_budget_seconds': cpu, 'parent_unchanged': True}))


if __name__ == '__main__':
    main()
