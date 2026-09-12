"""Separate observed management and C06 reference outcomes from entry compliance."""

from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from .logic import kleene_and, verdict
from .outcomes import score_outcome


def management_record(candidate, objects, evidence):
    from .evidence import SchemaError, _observed_value
    obj = objects[candidate['action_object_id']]
    policy = obj['value'].get('action_policy_ok')
    if obj['state'] == 'supplied' and policy is not None:
        observations = [_observed_value(evidence[eid]['payload'], 'action_policy_ok') for eid in obj['evidence_ids']]
        if not any(found and observed == policy for found, observed in observations):
            raise SchemaError('management policy has no supporting observation payload')
    base = obj.get('recipe_base_ok', True)
    if obj['instrument_id'] != candidate['instrument_id'] or obj['method_id'] != candidate['method_id']:
        base = False
    scope = obj['branch_scope'] if isinstance(obj['branch_scope'], list) else [obj['branch_scope']]
    if candidate['branch'] not in scope or obj.get('side') != candidate['side'] or obj.get('band_id') not in candidate['band_ids']:
        base = False
    if any(candidate['entry_identity'][key] != candidate[key] for key in ('method_id', 'side', 'instrument_id', 'band_ids')):
        base = False
    if candidate['decision_at'] <= candidate['entry_decision_at']:
        base = False
    inputs = obj.get('inputs', {})
    linked = inputs.get('entry_id') == candidate['parent_attempt_id'] and inputs.get('entry_at') == candidate['entry_decision_at']
    if inputs.get('entry_at') is not None and inputs['entry_at'] != candidate['entry_decision_at']:
        base = False
    if not linked:
        base = kleene_and(base, None)
        policy = None
    causal = obj['known_at'] is not None and obj['known_at'] > candidate['decision_at']
    if causal:
        base = False
    proxy = 0
    for eid in obj['evidence_ids']:
        ev = evidence[eid]
        if any(ev[key] != candidate[key] for key in ('method_id', 'branch', 'instrument_id', 'side')) or ev['band_id'] not in candidate['band_ids']:
            base = False
        if ev['known_at'] is None or obj['known_at'] is None:
            base = kleene_and(base, None)
        elif ev['known_at'] > obj['known_at'] or ev['known_at'] > candidate['decision_at']:
            base, causal = False, True
        if candidate['evidence_mode'] in {'raw_derived', 'supplied_contemporaneous'} and ev['evidence_mode'] in {'synthetic_fixture', 'source_illustration'}:
            base, proxy = False, proxy + 1
        if candidate['evidence_mode'] == 'raw_derived' and ev['evidence_mode'] == 'supplied_contemporaneous':
            base, proxy = False, proxy + 1
    cov = None if obj['state'] == 'hole' or policy is None else True
    holes = []
    if policy is None or causal:
        holes.append({'hole_id': 'HOLE:O142:action_policy' if not causal else 'HOLE:O142:ordering',
                      'recipe_id': 'O142', 'method_id': candidate['method_id'], 'branch': candidate['branch'],
                      'candidate_id': candidate['candidate_id'], 'kind': 'ordering' if causal else 'supplied_record_missing',
                      'missing_fields': ['action_policy_ok'], 'source_ref': obj['source_ref'],
                      'affected_output': 'management', 'reason': 'Late action evidence' if causal else 'Preselected policy/action evidence unavailable'})
    return {**candidate, 'operands': {'action_policy_ok': {'object_id': obj['object_id'], 'recipe_id': 'O142',
                                                       'type': 'boolean?', 'value': policy}},
            'base_ok': base, 'coverage_ok': cov, 'sequence_ok': policy,
            'verdict': verdict(base, cov, policy), 'failed_prerequisites': [] if base is not False and policy is not False else ['management policy/action'],
            'hole_ids': [h['hole_id'] for h in holes], 'holes': holes,
            'detected_causal_violations': int(causal), 'rejected_proxy_attempts': proxy,
            'used_object_ids': [obj['object_id']], 'used_assertion_ids': [], 'used_evidence_ids': obj['evidence_ids'],
            'source_versions': sorted({obj['source_version'], *(evidence[eid]['source_version'] for eid in obj['evidence_ids'])}),
            'year': datetime.fromtimestamp(candidate['decision_at'] // 1_000_000_000, timezone.utc).astimezone(ZoneInfo('America/New_York')).year}


def reference_outcome(candidate, objects=None, evidence=None):
    spec = candidate.get('outcome_spec')
    common = {'candidate_id': candidate['candidate_id'], 'method_id': candidate['method_id'],
              'branch': candidate['branch'], 'evidence_mode': candidate['evidence_mode'],
              'cohort_id': candidate['cohort_id'], 'decision_at': candidate['decision_at']}
    if spec is None:
        return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:outcome_spec'}
    required = ('source_ref', 'source_version', 'selected_at', 'objective_id', 'invalidation_id',
                'target', 'invalidation', 'window_end', 'coverage_complete', 'instrument_id')
    missing = [field for field in required if spec.get(field) is None]
    if missing:
        return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:' + missing[0]}
    if spec['selected_at'] > candidate['decision_at'] or spec['instrument_id'] != candidate['instrument_id']:
        return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:frozen_reference_identity', 'detected_causal_violation': True}
    from .evidence import _observed_value
    for id_field, price_field, recipe, allowed_fields in (
        ('objective_id', 'target', 'O141', ('target',)),
        ('invalidation_id', 'invalidation', 'O139', ('stop', 'invalidation')),
    ):
        oid = spec[id_field]
        obj = (objects or {}).get(oid)
        if obj is None or oid not in candidate['object_ids'] or obj['recipe_id'] != recipe:
            return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:' + id_field}
        scope = obj['branch_scope'] if isinstance(obj['branch_scope'], list) else [obj['branch_scope']]
        if obj['instrument_id'] != candidate['instrument_id'] or obj['method_id'] != candidate['method_id'] or candidate['branch'] not in scope or obj.get('side') != candidate['side'] or obj.get('band_id') not in candidate['band_ids']:
            return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:frozen_reference_identity'}
        key = next((key for key in allowed_fields if obj['value'].get(key) is not None), None)
        if key is None or Decimal(obj['value'][key]) != Decimal(spec[price_field]) or obj['state'] == 'invalid':
            return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:frozen_reference_value'}
        if obj['known_at'] is None or obj['known_at'] > spec['selected_at']:
            return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:frozen_reference_availability'}
        observations = [(evidence or {}).get(eid) for eid in obj['evidence_ids']]
        if not observations or any(ev is None or ev['known_at'] is None or ev['known_at'] > obj['known_at'] for ev in observations):
            return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:frozen_reference_evidence'}
        if obj['state'] == 'supplied' and not any(_observed_value(ev['payload'], key) == (True, obj['value'][key]) for ev in observations):
            return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:frozen_reference_evidence'}
    for record in [*(spec.get('events') or []), *(spec.get('bars') or [])]:
        if record.get('instrument_id') != candidate['instrument_id']:
            return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:instrument_id'}
    if spec['coverage_complete'] is True and candidate['evidence_mode'] in {'raw_derived', 'supplied_contemporaneous'}:
        coverage_id = spec.get('coverage_object_id')
        coverage = (objects or {}).get(coverage_id)
        if coverage is None or coverage_id not in candidate['object_ids'] or coverage['recipe_id'] != 'O001':
            return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:coverage_evidence'}
        value = coverage['value']
        if coverage['instrument_id'] != candidate['instrument_id'] or value.get('start') is None or value.get('end') is None or value['start'] > candidate['decision_at'] or value['end'] < spec['window_end'] or value.get('gaps') != [] or not coverage.get('raw_member_locators'):
            return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:coverage_evidence'}
        proof = [(evidence or {}).get(eid) for eid in coverage['evidence_ids']]
        if not proof or not any(ev and ev['payload'].get('coverage') == value for ev in proof):
            return {**common, 'outcome': 'unknown', 'hole': 'HOLE:C06:coverage_evidence'}
    result = score_outcome(decision_at=candidate['decision_at'], side=candidate['side'],
                           target=Decimal(spec['target']), invalidation=Decimal(spec['invalidation']),
                           window_end=spec['window_end'], events=spec.get('events'), bars=spec.get('bars'),
                           window_complete=spec['coverage_complete'] is True,
                           observation_stopped_at=spec.get('observation_stopped_at'), gap=spec.get('gap', False))
    return {**common, 'objective_id': spec['objective_id'], 'invalidation_id': spec['invalidation_id'],
            'source_ref': spec['source_ref'], 'source_version': spec['source_version'], **result}
