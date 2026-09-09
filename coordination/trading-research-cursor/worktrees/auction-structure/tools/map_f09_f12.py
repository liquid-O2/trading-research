"""Normalize static assertion metadata; does not import or execute candidate code."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = (
    ('f09', 'f09-shared-bar-registration.json', 'expected_cases', 'id', 'id', 'self', 'tests.test_shared_bars'),
    ('f10', 'f10-object-lineage-registration.json', 'case_proposals', 'id', 'case_id', 'source_case_id', 'tests.test_object_graph'),
    ('f11', 'f11-artifact-closure-registration.json', 'proposed_cases', 'case_id', 'id', 'source_preparation_cases', 'tests.test_artifact_graph'),
    ('f12', 'f12-arrival-trace-registration.json', 'case_proposals', 'case_id', 'case_id', 'source_case', 'tests.test_arrival'),
)
REMAINING = ['Finite registered engineering assertions only. Native/private data, source-specific generators, all consumer integration, calibration, economic evaluation and future captured receipts remain open.']


def identity(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': len(raw)}


def registered_bytes(ref):
    if (type(ref) is not dict or set(ref) != {'sha256', 'size_bytes', 'kind'}
            or type(ref['sha256']) is not str or len(ref['sha256']) != 64
            or any(c not in '0123456789abcdef' for c in ref['sha256'])
            or type(ref['size_bytes']) is not int or ref['size_bytes'] < 0):
        raise ValueError('registered artifact identity invalid')
    raw = (ROOT / 'evidence/trials/artifacts' / ref['sha256'][:2] / ref['sha256']).read_bytes()
    if len(raw) != ref['size_bytes'] or hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise ValueError('registered source artifact bytes changed')
    return raw


def main():
    summaries = []
    for prefix, filename, case_key, source_key, golden_key, binding_key, module in SPECS:
        registration_path = ROOT / 'reports' / filename
        registration = json.loads(registration_path.read_bytes())
        golden_path = ROOT / registration['golden_path']
        protocol_path = ROOT / registration['protocol_path']
        if (golden_path.read_bytes() != registered_bytes(registration['golden'])
                or protocol_path.read_bytes() != registered_bytes(registration['protocol'])):
            raise ValueError('frozen protocol or golden differs from retained registration')
        if identity(golden_path)['sha256'] != registration['golden']['sha256']:
            raise ValueError('frozen golden changed')
        golden = json.loads(golden_path.read_bytes())['cases']
        prepared_path = ROOT / f'reports/{prefix}-source-preparation.json'
        frozen_source = json.loads(registered_bytes(registration['source_cases']))
        preparation_raw = registered_bytes(frozen_source['preparation_bytes'])
        if prepared_path.read_bytes() != preparation_raw or json.loads(preparation_raw) != frozen_source['preparation']:
            raise ValueError('local preparation does not match exact registered source bytes')
        prepared = frozen_source['preparation'][case_key]
        sources = {case[source_key]: case for case in prepared}
        if len(sources) != len(prepared):
            raise ValueError('duplicate source cases')
        path = ROOT / (module.replace('.', '/') + '.py')
        tree = ast.parse(path.read_text())
        methods = sorted(f'{module}.{cls.name}.{method.name}' for cls in tree.body if isinstance(cls, ast.ClassDef)
                         for method in cls.body if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                         and method.name.startswith('test_'))
        if len(methods) != len(set(methods)):
            raise ValueError('duplicate assertion identities')
        map_path = ROOT / f'reports/{prefix}-case-test-map.json'
        raw_map = json.loads(map_path.read_bytes())
        proposed = {case['case_id']: case for case in raw_map['cases']}
        ids = [case[golden_key] for case in golden]
        if len(proposed) != len(raw_map['cases']) or len(ids) != len(set(ids)) or set(proposed) != set(ids):
            raise ValueError('exact golden assertion mapping differs')
        cases, used = [], set()
        source_map = {source: [] for source in sorted(sources)}
        for literal in golden:
            case_id = literal[golden_key]
            row = proposed[case_id]
            requests = [row['method_id']] if 'method_id' in row else row['test_methods']
            selected = []
            for requested in requests:
                matches = [method for method in methods if method == requested or method.rsplit('.', 1)[-1] == requested]
                if len(matches) != 1:
                    raise ValueError(f'missing or ambiguous assertion: {requested}')
                selected.append(matches[0])
            if not selected or len(selected) != len(set(selected)):
                raise ValueError('every frozen case requires distinct concrete assertions')
            value = case_id if binding_key == 'self' else literal[binding_key]
            bound = value if type(value) is list else ([] if value is None else [value])
            if len(bound) != len(set(bound)) or not set(bound) <= set(sources):
                raise ValueError('unknown or duplicate frozen source binding')
            for source in bound:
                source_map[source].append(case_id)
            for key in ('source_case_id', 'source_preparation_cases', 'source_case'):
                if key in row and key != binding_key and prefix != 'f09':
                    continue
                if key in row:
                    claimed = row[key] if type(row[key]) is list else ([] if row[key] is None else [row[key]])
                    if sorted(claimed) != sorted(bound):
                        raise ValueError('raw assertion source mapping differs from frozen binding')
            cases.append({'case_id': case_id, 'source_case_ids': sorted(bound),
                          'assertion_ids': sorted(selected), 'remaining': REMAINING})
            used.update(selected)
        if any(not cases for cases in source_map.values()):
            raise ValueError('prepared source case missing a frozen assertion')
        payload = {'kind': 'static_implementation_case_mapping', 'family': registration['family'],
                   'test_modules': [module], 'cases': cases,
                   'source_case_mapping': {source: sorted(cases) for source, cases in source_map.items()},
                   'additional_assertion_ids': sorted(set(methods) - used),
                   'remaining': REMAINING, 'inputs': [identity(p) for p in (registration_path, golden_path, protocol_path, prepared_path, map_path, path)],
                   'mapping_script': identity(Path(__file__).resolve()),
                   'registered_source_cases': registration['source_cases'],
                   'registered_preparation_bytes': frozen_source['preparation_bytes'],
                   'executed_by_mapping': False, 'whole_unit_definition_closure': False}
        output = ROOT / f'reports/{prefix}-implementation-coverage.json'
        output.write_text(json.dumps(payload, sort_keys=True, indent=2) + '\n')
        summaries.append({'prefix': prefix, 'golden_cases': len(cases), 'prepared_cases': len(sources),
                          'assertion_methods': len(methods), 'artifact': identity(output)})
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
