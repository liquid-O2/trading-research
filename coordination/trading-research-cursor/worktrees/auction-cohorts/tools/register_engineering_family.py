"""Freeze a byte-pinned engineering family after complete preparation review."""

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from trading_research.operations.artifacts import code_snapshot, publish_new
from trading_research.operations.trials import TrialRegistry
from engineering_batch_contract import resource_preset


ROOT = Path(__file__).resolve().parents[1]


def _input_path(value):
    if not isinstance(value, str) or not value:
        raise ValueError('preparation path must be a nonempty string')
    path = Path(value)
    if 'archive' in path.parts:
        raise ValueError('excluded archive path')
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    allowed = (ROOT, ROOT.parent / 'planning/trading-model',
               ROOT.parent / 'sources/documents', Path('/tmp'))
    reviewed_clock_metadata = ROOT.parent / 'data/manifests/timestamp-conventions.json'
    if ('archive' in resolved.parts or resolved != reviewed_clock_metadata
            and not any(resolved.is_relative_to(p) for p in allowed)):
        raise ValueError(f'preparation path outside reviewed document/code roots: {value}')
    return resolved


def _relative_path(value, prefix):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('canonical relative package path required')
    path = Path(value)
    if (path.is_absolute() or path.as_posix() != value
            or any(part in {'.', '..', 'archive'} for part in path.parts)
            or path.parts[:len(prefix)] != prefix or len(path.parts) <= len(prefix)):
        raise ValueError(f'path must be canonical below {"/".join(prefix)}/: {value}')
    joined = ROOT / path
    if joined.resolve() != joined:
        raise ValueError(f'package path traverses a symlink: {value}')
    return joined


def _sha(value):
    if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{64}', value) is None:
        raise ValueError('explicit lowercase SHA-256 required')
    return value


def main():
    request = json.loads(_input_path(sys.argv[1]).read_bytes())
    cpu, hard_cpu, memory, wall = resource_preset(request.get('resource_contract_version', 'legacy'))
    # Validate all requested package paths before reading or publishing content.
    source_path = _relative_path(request['source_preparation'], ('reports',))
    design_path = _relative_path(request['design'], ('reports',))
    protocol_path = _relative_path(request['protocol_path'], ('validation',))
    golden_path = _relative_path(request['golden_path'], ('tests', 'golden'))
    report_path = _relative_path(request['registration_report'], ('reports',))
    destinations = (protocol_path, golden_path, report_path)
    if len(set(destinations)) != 3 or report_path in (source_path, design_path):
        raise ValueError('registration outputs must not alias input reports or each other')
    pins = {key: _sha(request[key]) for key in (
        'source_preparation_sha256', 'design_sha256',
        'protocol_frozen_sha256', 'golden_frozen_sha256')}
    checked = {}
    staged = {}
    retain = {}
    cas_refs = {}

    def stage_path(path, expected, *, temporary=False):
        expected = _sha(expected)
        resolved = _input_path(str(path))
        if resolved in checked and checked[resolved] != expected:
            raise ValueError(f'conflicting hash declarations: {path}')
        if resolved not in staged:
            payload = resolved.read_bytes()
            if hashlib.sha256(payload).hexdigest() != expected:
                raise ValueError(f'prepared content changed: {path}')
            staged[resolved] = payload
            checked[resolved] = expected
        if temporary or resolved.is_relative_to('/tmp'):
            retain[str(path)] = resolved
        return staged[resolved]

    def walk(value):
        # Inspect only the existing JSON trees, never follow JSON file contents.
        if isinstance(value, dict):
            if set(value) == {'sha256', 'size_bytes', 'kind'}:
                sha = _sha(value['sha256'])
                if (type(value['size_bytes']) is not int or value['size_bytes'] < 0
                        or not isinstance(value['kind'], str) or not value['kind']):
                    raise ValueError('invalid exact content-addressed evidence reference')
                candidates = tuple(_input_path(str(ROOT / base / sha[:2] / sha)) for base in
                                   ('evidence/artifacts', 'evidence/trials/artifacts'))
                found = next((p for p in candidates if p.is_file()), None)
                if found is None:
                    raise ValueError(f'missing content-addressed evidence: {sha}')
                payload = stage_path(found, sha)
                if len(payload) != value['size_bytes']:
                    raise ValueError(f'content-addressed size mismatch: {sha}')
                cas_refs[(sha, value['kind'])] = (_input_path(str(found)), value['size_bytes'])
            if isinstance(value.get('path'), str) and 'sha256' in value:
                stage_path(value['path'], value['sha256'])
            for key, path in value.items():
                if key.endswith('_path') and isinstance(path, str):
                    names = (key[:-5] + '_sha256', key + '_sha256')
                    hashes = [_sha(value[name]) for name in names if name in value]
                    if len(set(hashes)) > 1:
                        raise ValueError(f'conflicting hash declarations for {key}')
                    if hashes:
                        stage_path(path, hashes[0])
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    source_bytes = stage_path(source_path, pins['source_preparation_sha256'])
    design_bytes = stage_path(design_path, pins['design_sha256'])
    protocol_bytes = stage_path(request['protocol_frozen_input'], pins['protocol_frozen_sha256'])
    golden_bytes = stage_path(request['golden_frozen_input'], pins['golden_frozen_sha256'])
    source = json.loads(source_bytes)
    design = json.loads(design_bytes)
    json.loads(golden_bytes)
    walk(source)
    walk(design)
    # Recheck the exact retained bytes, not a second filesystem read after hashing.
    for path, payload in staged.items():
        if hashlib.sha256(payload).hexdigest() != checked[path]:
            raise ValueError(f'staged preparation bytes changed: {path}')

    # Only after every declared record is checked may any artifact be published.
    registry = TrialRegistry(ROOT / 'evidence/trials')
    store = registry.artifacts
    retained = {name: asdict(store.put_bytes(staged[path], kind='retained_source_preparation_evidence'))
                for name, path in retain.items()}
    retained_cas = [asdict(store.put_bytes(staged[path], kind=kind))
                    for (sha, kind), (path, size) in sorted(cas_refs.items())]
    source_ref = store.put_json({
        'preparation': source,
        'preparation_bytes': asdict(store.put_bytes(source_bytes, kind='source_preparation_report')),
        'design_bytes': asdict(store.put_bytes(design_bytes, kind='implementation_design')),
        'retained_preparation_files': retained,
        'retained_content_addressed_evidence': retained_cas,
        'checked_files': {str(p): sha for p, sha in sorted(checked.items())},
        'whole_definition_or_phase_closure': False,
        'market_tape_reads': 0, 'economic_runs': 0,
    }, kind='original_source_case_review')
    publish_new(protocol_path, protocol_bytes)
    publish_new(golden_path, golden_bytes)
    registration = {
        'family': request['family'], 'scope_ids': request['scope_ids'],
        'protocol_path': request['protocol_path'], 'golden_path': request['golden_path'],
        'protocol': asdict(store.put_bytes(protocol_bytes, kind='engineering_protocol')),
        'golden': asdict(store.put_bytes(golden_bytes, kind='independent_golden_reference')),
        'source_cases': asdict(source_ref),
        'baseline': asdict(code_snapshot(ROOT, store)),
        'maximum_cpu_per_attempt': cpu, 'hard_cpu_seconds': hard_cpu,
        'address_space_bytes': memory, 'wall_seconds': wall,
        'shared_verification': 'One combined full-suite worker may be charged conservatively to each participating family; retain one shared execution identity and do not sum duplicated telemetry as physical resource use.',
        'market_tape_reads': 0, 'model_fits': 0, 'economic_runs': 0,
        'registered_at': datetime.now(timezone.utc).isoformat(),
    }
    registry.register_family(request['family'], scope_ids=tuple(request['scope_ids']),
                             protocol=registration, max_attempts=3, cpu_budget_seconds=600)
    publish_new(report_path, (json.dumps(registration, indent=2) + '\n').encode())
    print(json.dumps({'registration': registration, 'retained_files': len(retained),
                      'checked_files': len(checked)}, indent=2))


if __name__ == '__main__':
    main()
