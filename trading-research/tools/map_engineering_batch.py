"""Normalize all frozen case maps without importing or executing candidates."""
import json
import sys

from engineering_batch_contract import (
    ROOT, load_batch_snapshot, local_identity, normalize_coverage, package_path, validate_registrations,
)
from trading_research.operations.artifacts import publish_new
from trading_research.operations.trials import TrialRegistry


def main():
    if len(sys.argv) != 2:
        raise ValueError('supply one canonical relative frozen batch-contract path')
    batch_path = sys.argv[1]
    batch_raw,batch = load_batch_snapshot(batch_path)
    registry = TrialRegistry(ROOT / 'evidence/trials')
    registrations = [json.loads(package_path(s['registration_path']).read_bytes()) for s in batch['families']]
    validate_registrations(registry, registrations, batch)
    staged = []
    for spec, registration in zip(batch['families'], registrations):
        coverage = normalize_coverage(registry.artifacts, registration, spec, batch, batch_path,batch_raw)
        staged.append((spec, coverage, (json.dumps(coverage, indent=2, sort_keys=True) + '\n').encode()))
    # No partial map publication before every family has passed static checks.
    for spec, coverage, raw in staged:
        publish_new(package_path(spec['coverage_path']), raw)
    print(json.dumps([{'family': spec['family'], 'golden_cases': len(coverage['cases']),
                       'source_clauses': len(coverage['source_dispositions']),
                       'artifact': local_identity(spec['coverage_path'])}
                      for spec, coverage, _ in staged], indent=2))


if __name__ == '__main__':
    main()
