"""Freeze an independently prepared foundation protocol before its implementation."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

from trading_research.operations.artifacts import code_snapshot, file_digest, publish_new
from trading_research.operations.trials import TrialRegistry


ROOT = Path(__file__).resolve().parents[1]


def main():
    request = json.loads(Path(sys.argv[1]).read_text())
    registry = TrialRegistry(ROOT / 'evidence/trials')
    store = registry.artifacts
    retained = {}
    checked = {}

    def retain_path(path, expected, *, temporary=False):
        path = Path(path)
        resolved = path.resolve()
        allowed = (ROOT, ROOT.parent / 'planning/trading-model',
                   ROOT.parent / 'sources/documents', Path('/tmp'))
        reviewed_clock_metadata = ROOT.parent / 'data/manifests/timestamp-conventions.json'
        if resolved != reviewed_clock_metadata and not any(resolved.is_relative_to(p) for p in allowed):
            raise ValueError(f'preparation path outside reviewed document/code roots: {path}')
        if resolved not in checked:
            checked[resolved] = file_digest(resolved)
        if checked[resolved] != expected:
            raise ValueError(f'prepared content changed: {path}')
        if temporary or resolved.is_relative_to('/tmp'):
            ref = store.put_bytes(resolved.read_bytes(), kind='retained_source_preparation_evidence')
            retained[str(path)] = asdict(ref)

    def walk(value):
        if isinstance(value, dict):
            if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
                retain_path(value['path'], value['sha256'])
            for key, path in value.items():
                if key.endswith('_path') and isinstance(path, str):
                    sha = value.get(key[:-5] + '_sha256')
                    if isinstance(sha, str):
                        retain_path(path, sha)
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    source_path = ROOT / request['source_preparation']
    design_path = ROOT / request['design']
    source = json.loads(source_path.read_text())
    design = json.loads(design_path.read_text())
    walk(source)
    walk(design)
    source_ref = store.put_json({
        'preparation': source,
        'preparation_bytes': asdict(store.put_bytes(source_path.read_bytes(), kind='source_preparation_report')),
        'design_bytes': asdict(store.put_bytes(design_path.read_bytes(), kind='implementation_design')),
        'retained_preparation_files': retained,
        'checked_files': {str(p): sha for p, sha in sorted(checked.items())},
        'whole_definition_or_phase_closure': False,
        'market_tape_reads': 0, 'economic_runs': 0,
    }, kind='original_source_case_review')
    protocol_path = ROOT / request['protocol_path']
    golden_path = ROOT / request['golden_path']
    # Exact reviewable bytes are supplied by root; publication never overwrites.
    publish_new(protocol_path, Path(request['protocol_frozen_input']).read_bytes())
    publish_new(golden_path, Path(request['golden_frozen_input']).read_bytes())
    registration = {
        'family': request['family'], 'scope_ids': request['scope_ids'],
        'protocol_path': request['protocol_path'], 'golden_path': request['golden_path'],
        'protocol': asdict(store.put_bytes(protocol_path.read_bytes(), kind='engineering_protocol')),
        'golden': asdict(store.put_bytes(golden_path.read_bytes(), kind='independent_golden_reference')),
        'source_cases': asdict(source_ref),
        'baseline': asdict(code_snapshot(ROOT, store)),
        'maximum_cpu_per_attempt': 180, 'hard_cpu_seconds': 190,
        'address_space_bytes': 4 * 1024 ** 3, 'wall_seconds': 240,
        'shared_verification': 'One combined full-suite worker may be charged conservatively to each participating family; retain one shared execution identity and do not sum duplicated telemetry as physical resource use.',
        'market_tape_reads': 0, 'model_fits': 0, 'economic_runs': 0,
        'registered_at': datetime.now(timezone.utc).isoformat(),
    }
    registry.register_family(request['family'], scope_ids=tuple(request['scope_ids']),
                             protocol=registration, max_attempts=3, cpu_budget_seconds=600)
    publish_new(ROOT / request['registration_report'],
                (json.dumps(registration, indent=2) + '\n').encode())
    print(json.dumps({'registration': registration, 'retained_files': len(retained),
                      'checked_files': len(checked)}, indent=2))


if __name__ == '__main__':
    main()
