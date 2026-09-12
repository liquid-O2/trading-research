"""Printed method cases exercise the same boundary as supplied manifests."""

from copy import deepcopy

from .evidence import fixture_document, parse_manifest, score_episode
from .protocol import jsonable


def method_case(method_id, predicate, fid, inputs, expected, *, kind='method'):
    document = deepcopy(inputs) if 'candidates' in inputs else fixture_document(method_id, predicate, fid, inputs)
    candidates, objects, assertions, evidence = parse_manifest(document, method_id)
    candidate = next(c for c in candidates.values() if c['candidate_id'] == fid) if fid in candidates else next(iter(candidates.values()))
    actual = score_episode(candidate, objects, assertions, evidence)
    expected_values = {'verdict': expected} if isinstance(expected, str) else expected
    failures = [f'{key}: {actual.get(key)!r} != {value!r}' for key, value in expected_values.items() if actual.get(key) != value]
    return {'id': fid, 'recipe': method_id, 'predicate': predicate, 'kind': kind,
            'status': 'fail' if failures else 'pass', 'failures': failures,
            'inputs': jsonable(document), 'expected': jsonable(expected_values),
            'actual_value': jsonable(actual), 'evidence_mode': 'synthetic_fixture',
            'hole_ids': actual['hole_ids'],
            'detected_causal_violation': actual['detected_causal_violations'] > 0,
            'unbound_fields': []}
