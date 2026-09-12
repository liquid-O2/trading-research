"""C01 episode manifests and causal, typed operand bindings at the input boundary."""

from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from . import FORMULA_VERSION
from .catalog import BRANCHES, METHOD_BY_ID, PRIMARY, EXTRA_PREDICATES, objects_for
from .contracts import fields_for, sections
from .expressions import evaluate
from .logic import kleene_and, kleene_cmp, verdict
from .protocol import RECIPES, jsonable, run_recipe
from .stages import stage_at, audit_candidate

MODES = {'raw_derived', 'supplied_contemporaneous', 'source_illustration', 'synthetic_fixture', 'native_control'}
CASE_BRANCHES = {'pre_file_early', 'third_retest_case', 'late_resistance_fade_case', 'ofm_early_refill_case'}
IDENTITY = ('method_id', 'instrument_id', 'side')


class SchemaError(ValueError):
    pass


def _required(record, fields, label):
    if not isinstance(record, dict):
        raise SchemaError(f'{label} must be a record')
    missing = [key for key in fields if key not in record]
    if missing:
        raise SchemaError(f'{label} missing {", ".join(missing)}')


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(f'{label} must be a nonempty string')


def _ns(value, label, nullable=True):
    if value is None and nullable:
        return None
    if type(value) is not int or not -(2**63) <= value < 2**63:
        raise SchemaError(f'{label} must be int64 UTC nanoseconds')
    return value


def _index(records, key):
    if not isinstance(records, list):
        raise SchemaError(f'{key} records must be an array')
    result = {}
    for record in records:
        _required(record, [key], key)
        _text(record[key], key)
        if record[key] in result:
            raise SchemaError(f'duplicate {key}: {record[key]}')
        result[record[key]] = record
    return result


def _ids(value, label):
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise SchemaError(f'{label} must be an array of nonempty IDs')
    if len(value) != len(set(value)):
        raise SchemaError(f'{label} contains duplicate IDs')


# In-process admission identity cannot be forged by a JSON manifest. Parsing
# removes claimed audit markers; only verified source audit may set this token.
class _AdmissionToken:
    def __deepcopy__(self, memo):
        return self


_SOURCE_ADMISSION = _AdmissionToken()


def mark_source_admitted(record, field):
    record.setdefault('_source_admission', {})[field] = _SOURCE_ADMISSION


def source_admitted(record, field):
    return record.get('_source_admission', {}).get(field) is _SOURCE_ADMISSION


def audit_source_domain_object(record, evidence):
    """Recompute a supplied dependency/action from its complete cited inputs.

    No caller-written output dictionary is admitted as a native dependency.
    Actual source-record inputs and the full domain schema are both required.
    """
    from .contracts import validate_output
    from .protocol import run_recipe, jsonable
    from .semantic_views import source_citation, AUTHORS
    if record.get('author',record['method_id']) not in AUTHORS[record['method_id']]:
        raise SchemaError('supplied dependency/action has foreign source author')
    matches=[]
    for eid in record.get('evidence_ids',[]):
        ev=evidence[eid];payload=ev.get('payload',{});inputs=payload.get('recipe_inputs')
        if payload.get('recipe_id')!=record['recipe_id'] or not isinstance(inputs,dict) or not _has_observation(inputs):continue
        for key in ('instrument_id','method_id','author'):
            if key in inputs and str(inputs[key])!=str(record.get(key,inputs[key])):
                raise SchemaError('supplied dependency/action input identity differs from record')
        try:source_citation(payload.get('source_citation'),record['method_id'])
        except ValueError as exc:raise SchemaError(str(exc)) from exc
        result=validate_output(run_recipe(record['recipe_id'],deepcopy(inputs)))
        if result.state=='invalid' or result.base_ok is False:raise SchemaError('invalid supplied dependency/action source record')
        if result.known_at is None or record.get('known_at') is None or result.known_at>record['known_at']:
            raise SchemaError('supplied dependency/action backdates actual source inputs')
        if any(key not in result.value or jsonable(value)!=jsonable(result.value[key]) for key,value in record['value'].items()):
            raise SchemaError('supplied dependency/action differs from full source recipe rerun')
        matches.append((eid,result))
    if not matches:raise SchemaError('supplied dependency/action requires actual cited recipe_inputs and full output schema')
    eid,result=matches[0]
    record['value']=result.value
    record['recipe_base_ok']=result.base_ok
    record['recipe_coverage_ok']=result.coverage_ok
    record['evidence_class']='supplied_source_audit'
    for field,value in result.value.items():
        mark_source_admitted(record,field)
        evidence[eid]['payload'][field]=value
    return result


def _observed_value(payload, field):
    if field in payload:
        return True, payload[field]
    if payload.get('field') == field and 'value' in payload:
        return True, payload['value']
    if isinstance(payload.get('value'), dict):
        return _observed_value(payload['value'], field)
    return False, None


def _has_observation(payload):
    interpreted = payload.get('source_interpretation')
    if isinstance(interpreted, dict) and isinstance(interpreted.get('citation'), dict) and interpreted.get('observations'):
        # Full file/hash/role/type verification happens in method assembly.
        return True
    # A source interpretation must also carry the cited observation. Identity,
    # a Boolean flag, or its timestamp alone is not an observation payload.
    for key in ('observation', 'source_observation', 'events', 'bars', 'trades', 'prices', 'levels'):
        value = payload.get(key)
        if isinstance(value, (dict, list, str)) and len(value) > 0:
            return True
    return any(key in payload and payload[key] is not None for key in
               ('price', 'high', 'low', 'close', 'volume', 'bid', 'ask', 'executed_size'))


def typed(value, kind, field):
    if value is None:
        return None
    if kind.startswith('boolean'):
        if type(value) is not bool:
            raise SchemaError(f'{field} must be true, false or null')
        return value
    if kind.startswith('event_key'):
        return _ns(value, field)
    if kind.startswith('integer'):
        if type(value) is not int:
            raise SchemaError(f'{field} must be an integer')
        return value
    if kind.startswith('decimal'):
        if isinstance(value, bool) or isinstance(value, float):
            raise SchemaError(f'{field} must be an exact decimal string or integer')
        try:
            result = Decimal(value)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise SchemaError(f'{field} invalid decimal') from exc
        if not result.is_finite():
            raise SchemaError(f'{field} must be finite')
        return result
    _text(value, field)
    return value


def parse_manifest(document, method_id, *, resolver=None):
    _required(document, ['formula_version', 'candidates', 'objects', 'assertions', 'evidence'], 'manifest')
    if document['formula_version'] != FORMULA_VERSION:
        raise SchemaError('episode formula_version mismatch')
    candidates = _index(document['candidates'], 'candidate_id')
    objects = _index(document['objects'], 'object_id')
    assertions = _index(document['assertions'], 'assertion_id')
    evidence = _index(document['evidence'], 'evidence_id')
    allowed = set(objects_for(method_id))
    for obj in objects.values():
        obj.pop('_source_admission', None)
        obj.pop('source_audits', None)
        if obj.get('state') != 'computed': obj.pop('evidence_class', None)
        _required(obj, ['recipe_id', 'method_id', 'branch_scope', 'author', 'instrument_id',
                        'parent_ids', 'source_ref', 'source_version', 'value', 'units',
                        'formation_start', 'formation_end', 'as_of', 'known_at', 'state',
                        'hole_ids', 'evidence_ids'], 'object')
        if obj['recipe_id'] not in allowed or obj['method_id'] != method_id:
            raise SchemaError(f'foreign method/object recipe: {obj["recipe_id"]}')
        if obj['state'] not in {'computed', 'supplied', 'hole', 'invalid'}:
            raise SchemaError('unknown object state')
        for key in ('parent_ids', 'hole_ids', 'evidence_ids'):
            _ids(obj[key], f'object.{key}')
        for key in ('source_ref', 'source_version', 'author'):
            _text(obj[key], f'object.{key}')
        for key in ('formation_start', 'formation_end', 'as_of', 'known_at'):
            _ns(obj[key], f'object.{key}')
        if not isinstance(obj['value'], dict) or not isinstance(obj['units'], dict):
            raise SchemaError('object value and units must be typed mappings')
        for parent in obj['parent_ids']:
            if parent not in objects:
                raise SchemaError(f'unknown parent object {parent}')
        for eid in obj['evidence_ids']:
            if eid not in evidence:
                raise SchemaError(f'unknown evidence {eid}')
        if obj['state'] == 'computed':
            _required(obj, ['inputs'], 'computed object')
            if not obj.get('raw_member_locators') and not obj['parent_ids']:
                raise SchemaError('computed object needs immutable raw members or actual parent provenance')
    for ev in evidence.values():
        _required(ev, ['method_id', 'branch', 'instrument_id', 'band_id', 'side',
                       'source_ref', 'source_version', 'description', 'payload',
                       'observation_start', 'observation_end', 'known_at', 'evidence_mode'], 'evidence')
        for key in ('source_ref', 'source_version', 'description'):
            _text(ev[key], f'evidence.{key}')
        if ev['method_id'] != method_id:
            raise SchemaError('foreign evidence method')
        if not isinstance(ev['payload'], dict) or not ev['payload']:
            raise SchemaError('evidence needs the actual observation payload')
        if ev['evidence_mode'] not in MODES:
            raise SchemaError('unknown evidence mode')
        for key in ('observation_start', 'observation_end', 'known_at'):
            _ns(ev[key], f'evidence.{key}')
    # Resolve actual parent objects first; JSON list order is not availability.
    # The manifest cannot replace a parent with a same-price scalar dependency.
    resolving, resolved_objects = set(), set()
    def resolve_object(oid):
        if oid in resolving:
            raise SchemaError('cyclic object parent identity')
        if oid in resolved_objects:
            return
        resolving.add(oid)
        obj = objects[oid]
        for parent in obj['parent_ids']:
            resolve_object(parent)
        if obj['state'] == 'computed':
            from .native_resolution import NativeResolver, NativeEvidenceError
            from .objects.native_boundary import run_native_object
            parents = [objects[parent] for parent in obj['parent_ids']]
            for parent in parents:
                if parent['state'] == 'supplied':
                    audit_source_domain_object(parent,evidence)
            try:
                result = run_native_object(obj, native_resolver, parents=parents)
            except NativeEvidenceError as exc:
                raise SchemaError(str(exc)) from exc
            obj['value'] = result.value
            obj['state'] = result.state
            obj['hole_ids'] = result.hole_ids
            obj['known_at'] = result.known_at
            obj['recipe_base_ok'] = result.base_ok
            obj['recipe_coverage_ok'] = result.coverage_ok
            obj['evidence_class'] = result.evidence_class
            obj['units'] = result.units or obj['units']
        resolving.remove(oid)
        resolved_objects.add(oid)
    from .native_resolution import NativeResolver
    native_resolver = resolver or NativeResolver()
    for oid in objects:
        resolve_object(oid)
    for assertion in assertions.values():
        assertion.pop('_source_admission', None)
        assertion.pop('source_audits', None)
        assertion.pop('evidence_class', None)
        _required(assertion, ['field', 'value', 'recipe_id', 'method_id', 'branch', 'candidate_id',
                              'instrument_id', 'band_id', 'side', 'evidence_ids',
                              'observation_start', 'observation_end', 'known_at',
                              'evidence_mode', 'source_ref', 'source_version', 'reason'], 'assertion')
        if assertion['recipe_id'] not in allowed or assertion['method_id'] != method_id:
            raise SchemaError('foreign assertion producer')
        if assertion['evidence_mode'] not in MODES:
            raise SchemaError('unknown assertion evidence mode')
        _ids(assertion['evidence_ids'], 'assertion.evidence_ids')
        if type(assertion['value']) is not bool and assertion['value'] is not None:
            raise SchemaError('assertion is not a nullable Boolean')
        if not assertion['evidence_ids'] and assertion['value'] is not None:
            raise SchemaError('naked Boolean without observation evidence')
        for eid in assertion['evidence_ids']:
            if eid not in evidence:
                raise SchemaError(f'unknown assertion evidence {eid}')
        if assertion['evidence_mode'] != 'raw_derived' and assertion['value'] is not None:
            observations = [_observed_value(evidence[eid]['payload'], assertion['field']) for eid in assertion['evidence_ids']]
            if not any(found and value == assertion['value'] for found, value in observations):
                raise SchemaError(f'{assertion["field"]}: source observation does not support the asserted value')
            if assertion['evidence_mode'] == 'supplied_contemporaneous' and not any(_has_observation(evidence[eid]['payload']) for eid in assertion['evidence_ids']):
                raise SchemaError(f'{assertion["field"]}: supplied interpretation lacks an actual cited observation')
        for key in ('source_ref', 'source_version', 'reason'):
            _text(assertion[key], f'assertion.{key}')
        for key in ('observation_start', 'observation_end', 'known_at'):
            _ns(assertion[key], f'assertion.{key}')
        if 'object_id' in assertion:
            linked = objects.get(assertion['object_id'])
            if linked is None or linked['recipe_id'] != assertion['recipe_id']:
                raise SchemaError('assertion object link must identify its actual recipe producer')
        if assertion['evidence_mode'] == 'raw_derived':
            _required(assertion, ['object_id', 'comparison'], 'computed assertion')
            producer = objects.get(assertion['object_id'])
            if producer is None or 'inputs' not in producer or producer['recipe_id'] != assertion['recipe_id']:
                raise SchemaError('computed assertion needs its actual computed object')
            comparison = assertion['comparison']
            _required(comparison, ['left_field', 'operator'], 'comparison')
            if comparison['left_field'] != assertion['field'] or comparison['operator'] != '==' or comparison.get('right_value') is not True or 'right_field' in comparison:
                raise SchemaError('computed assertion must compare its recipe-produced Boolean field to true')
            left = producer['value'].get(comparison['left_field'])
            if left is not None and type(left) is not bool:
                raise SchemaError('computed assertion field is not a nullable Boolean')
            right = producer['value'].get(comparison['right_field']) if 'right_field' in comparison else comparison.get('right_value')
            if comparison['operator'] not in {'==', '!=', '<', '<=', '>', '>='}:
                raise SchemaError('unsupported computed comparison')
            assertion['value'] = kleene_cmp(comparison['operator'], left, right)
            assertion['known_at'] = producer['known_at']
    visiting, visited = set(), set()
    def check_parent_graph(oid):
        if oid in visiting:
            raise SchemaError('cyclic object parent identity')
        if oid in visited:
            return
        visiting.add(oid)
        for parent in objects[oid]['parent_ids']:
            check_parent_graph(parent)
        visiting.remove(oid)
        visited.add(oid)
    for oid in objects:
        check_parent_graph(oid)
    for candidate in candidates.values():
        seen = {candidate['candidate_id']}
        parent_id = candidate.get('parent_attempt_id')
        while parent_id in candidates:
            if parent_id in seen:
                raise SchemaError('cyclic candidate parent identity')
            seen.add(parent_id)
            parent_id = candidates[parent_id].get('parent_attempt_id')
    predicates = {PRIMARY[method_id], *EXTRA_PREDICATES.get(method_id, [])}
    if method_id == 'SIRES':
        predicates.add('case_description')
    for candidate in candidates.values():
        _required(candidate, ['method_id', 'branch', 'side', 'instrument_id', 'session_date_et',
                              'decision_at', 'band_ids', 'object_ids', 'assertion_ids',
                              'cohort_id', 'evidence_mode', 'operands'], 'candidate')
        if candidate['method_id'] != method_id:
            raise SchemaError('foreign candidate method')
        branches = set(BRANCHES[method_id]) | (CASE_BRANCHES if method_id == 'SIRES' else set())
        if candidate['branch'] not in branches:
            raise SchemaError('unknown source branch')
        predicate = candidate.setdefault('predicate', PRIMARY[method_id])
        if predicate not in predicates:
            raise SchemaError('unknown method predicate')
        if method_id == 'SIRES' and candidate['branch'] in CASE_BRANCHES and predicate != 'case_description':
            raise SchemaError('incomplete source case cannot enter a confirmed-entry cohort')
        if candidate['side'] not in {'long', 'short', 'not_applicable'}:
            raise SchemaError('invalid candidate side')
        if candidate['evidence_mode'] not in MODES:
            raise SchemaError('unknown candidate evidence_mode')
        if candidate['evidence_mode']=='native_control':
            from .source_config import load_catalog
            catalog=load_catalog()
            case=next((r for r in catalog['cases'] if r['case_id']==candidate.get('source_case_id')),None)
            if candidate.get('variant')!='comparison' or case is None or case['method_id']!=method_id:
                raise SchemaError('native control requires comparison variant and exact catalog source case')

        for key in ('band_ids', 'object_ids', 'assertion_ids'):
            _ids(candidate[key], f'candidate.{key}')
        _ns(candidate['decision_at'], 'candidate.decision_at', nullable=False)
        for oid in candidate['object_ids']:
            if oid not in objects:
                raise SchemaError(f'unknown candidate object {oid}')
        for aid in candidate['assertion_ids']:
            if aid not in assertions:
                raise SchemaError(f'unknown candidate assertion {aid}')
        if not isinstance(candidate['operands'], dict):
            raise SchemaError('candidate operands must reference producers')
        if method_id == 'JJ-TBR' and predicate == 'management':
            _required(candidate, ['action_object_id', 'parent_attempt_id'], 'management candidate')
            obj = objects.get(candidate['action_object_id'])
            parent = candidates.get(candidate['parent_attempt_id'])
            if obj is None or obj['recipe_id'] != 'O142' or parent is None:
                raise SchemaError('management needs its O142 object and parent entry')
            if candidate['action_object_id'] not in candidate['object_ids']:
                raise SchemaError('management object is not owned by action')
            candidate['entry_decision_at'] = parent['decision_at']
            candidate['entry_identity'] = {key: parent[key] for key in ('method_id', 'side', 'instrument_id', 'band_ids')}
        if method_id == 'SIRES' and predicate in {'management', 'reentry'}:
            parent = candidates.get(candidate.get('parent_attempt_id'))
            candidate['parent_record'] = deepcopy(parent) if parent else None
        for field, binding in candidate['operands'].items():
            if field not in fields_for(method_id):
                raise SchemaError(f'unknown operand {field}')
            if not isinstance(binding, dict) or len(set(binding) & {'assertion_id', 'object_id'}) != 1:
                raise SchemaError(f'{field} needs one object or assertion binding, not a naked value')
    if method_id == 'JETBUNDLE-STATES':
        for candidate in candidates.values():
            if candidate['predicate'] != 'transition_observation':
                continue
            links = {}
            for role in ('current', 'next'):
                key = f'{role}_state_candidate_id'
                identifier = candidate.get(key)
                if identifier is not None:
                    _text(identifier, f'candidate.{key}')
                links[role] = deepcopy(candidates.get(identifier))
            candidate['state_records'] = links
    return candidates, objects, assertions, evidence


def read_manifest(path, method_id, *, resolver=None):
    try:
        raw = Path(path).read_bytes()
        doc = json.loads(raw, parse_float=Decimal)
        parsed = parse_manifest(doc, method_id, resolver=resolver)
    except (OSError, json.JSONDecodeError) as exc:
        raise SchemaError(str(exc)) from exc
    return doc, parsed, hashlib.sha256(raw).hexdigest()


def score_episode(candidate, objects, assertions, evidence):
    method_id = candidate['method_id']
    if method_id == 'JJ-TBR' and candidate['predicate'] == 'management':
        from .secondary import management_record
        action=objects[candidate['action_object_id']]
        if candidate.get('evidence_mode')!='synthetic_fixture' and action.get('state')=='supplied' and not source_admitted(action,'action_policy_ok'):
            raise SchemaError('management action has not passed actual source assembly audit')
        return management_record(candidate, objects, evidence)
    contracts = fields_for(method_id)
    operands, bindings, issues = {}, {}, []
    used_objects, used_assertions, used_evidence = set(), set(), set()

    def issue(field, kind, reason, recipe=None):
        issues.append({'hole_id': f'HOLE:{recipe or METHOD_BY_ID[method_id]}:{field}',
                       'recipe_id': recipe or METHOD_BY_ID[method_id], 'method_id': method_id,
                       'candidate_id': candidate['candidate_id'], 'branch': candidate['branch'],
                       'kind': kind, 'missing_fields': [field], 'source_ref': contracts[field].rule if field in contracts else 'C01/C04',
                       'affected_output': candidate['predicate'], 'reason': reason})

    for field, binding in candidate['operands'].items():
        contract = contracts[field]
        if 'assertion_id' in binding:
            aid = binding['assertion_id']
            if aid not in candidate['assertion_ids'] or aid not in assertions:
                raise SchemaError(f'{field}: assertion not owned by candidate')
            record = assertions[aid]
            if record['field'] != field or record['recipe_id'] not in contract.recipes:
                raise SchemaError(f'{field}: wrong producer binding')
            value = record['value']
            used_assertions.add(aid)
        else:
            oid = binding['object_id']
            if oid not in candidate['object_ids'] or oid not in objects:
                raise SchemaError(f'{field}: object not owned by candidate')
            record = objects[oid]
            if record['recipe_id'] not in contract.recipes:
                raise SchemaError(f'{field}: wrong recipe producer')
            key = binding.get('value_field', field)
            if key != field:
                raise SchemaError(f'{field}: arbitrary object-field substitution is not a producer binding')
            value = record['value'].get(key)
            if record['state'] == 'supplied' and value is not None:
                observations = [_observed_value(evidence[eid]['payload'], key) for eid in record['evidence_ids']]
                if not any(found and typed(observed, contract.type, field) == typed(value, contract.type, field)
                           for found, observed in observations):
                    raise SchemaError(f'{field}: supplied object has no supporting observation payload')
            used_objects.add(oid)
            if record['state'] == 'invalid':
                value = None
        source_record = ('assertion_id' in binding) or ('object_id' in binding and record.get('state') == 'supplied')
        if candidate.get('evidence_mode') != 'synthetic_fixture' and source_record and value is not None and not source_admitted(record, field):
            raise SchemaError(f'{field}: source operand has not passed actual source assembly audit')
        operands[field] = typed(value, contract.type, field)
        if 'object_id' in binding and record['units'].get(key) != contract.type:
            raise SchemaError(f'{field}: object units do not match {contract.type}')
        bindings[field] = {**binding, 'recipe_id': record['recipe_id'], 'type': contract.type,
                           'value': jsonable(operands[field]), 'known_at': record['known_at'],
                           'evidence_ids': record['evidence_ids'], 'applicability': 'required'}
    operands.setdefault('branch', candidate['branch'])
    operands.setdefault('side', candidate['side'])
    operands.setdefault('decision_at', candidate['decision_at'])
    selected = evaluate(method_id, candidate['predicate'], operands)
    base, coverage = True, True
    causal_count = proxy_count = 0
    for field in selected.fields:
        if field not in contracts:
            continue
        if field not in bindings:
            issue(field, 'supplied_record_missing', 'required operand has no supplied record', contracts[field].recipes[0])
            coverage = kleene_and(coverage, None)
            bindings[field] = {'value': None, 'type': contracts[field].type,
                               'recipe_id': contracts[field].recipes[0], 'applicability': 'required'}
            continue
        binding = bindings[field]
        record = assertions[binding['assertion_id']] if 'assertion_id' in binding else objects[binding['object_id']]
        records = [record]
        for eid in record['evidence_ids']:
            records.append(evidence[eid])
            used_evidence.add(eid)
        producer_id = binding.get('object_id') or record.get('object_id')
        if producer_id:
            pending = [producer_id]
            visited_parents = set()
            while pending:
                parent = objects[pending.pop()]
                if parent['object_id'] in visited_parents:
                    continue
                visited_parents.add(parent['object_id'])
                used_objects.add(parent['object_id'])
                records.append(parent)
                pending.extend(parent['parent_ids'])
                for eid in parent['evidence_ids']:
                    records.append(evidence[eid])
                    used_evidence.add(eid)
        if operands.get(field) is None:
            coverage = kleene_and(coverage, None)
            issue(field, 'supplied_record_missing', 'source definition or supplied value unavailable', record['recipe_id'])
        if field.endswith('known_at') and operands.get(field) is not None and record['known_at'] is not None and operands[field] < record['known_at']:
            base = False
            causal_count += 1
            issue(field, 'ordering', 'availability operand predates its actual producer', record['recipe_id'])
        for rec in records:
            if 'recipe_coverage_ok' in rec:
                coverage = kleene_and(coverage, rec['recipe_coverage_ok'])
                if rec['recipe_coverage_ok'] is not True:
                    issue(field, 'data_coverage', 'producer coverage is incomplete or unknown', record['recipe_id'])
            if 'recipe_base_ok' in rec:
                base = kleene_and(base, rec['recipe_base_ok'])
            if rec.get('recipe_base_ok') is False or rec.get('state') == 'invalid':
                base = False
                issue(field, 'identity', 'producer object is invalid', record['recipe_id'])
            mismatch = any(key in rec and rec[key] != candidate[key] for key in IDENTITY)
            if 'candidate_id' in rec and rec['candidate_id'] != candidate['candidate_id']:
                mismatch = True
            if 'branch' in rec and rec['branch'] != candidate['branch']:
                mismatch = True
            if 'branch_scope' in rec and candidate['branch'] not in ([rec['branch_scope']] if isinstance(rec['branch_scope'], str) else rec['branch_scope']):
                mismatch = True
            if rec.get('band_id') is not None and rec['band_id'] not in candidate['band_ids']:
                mismatch = True
            if mismatch:
                base = False
                issue(field, 'identity', 'source candidate/branch/instrument/band/side identity mismatch', record['recipe_id'])
            limit = candidate['decision_at']
            if candidate['predicate'] == 'management':
                limit = operands.get('action_at') or limit
            if candidate['predicate'] == 'transition_observation' and field == 'next_state_at':
                limit = operands.get('next_state_at') or limit
            stage = stage_at(method_id, field, operands)
            if stage is not None:
                limit = min(limit, stage)
            known = rec.get('known_at')
            if known is None:
                base = kleene_and(base, None)
                issue(field, 'ordering', 'availability is unknown', record['recipe_id'])
            elif known > limit:
                base = False
                causal_count += 1
                issue(field, 'ordering', 'prerequisite available after use', record['recipe_id'])
            end = rec.get('observation_end', rec.get('formation_end'))
            start = rec.get('observation_start', rec.get('formation_start'))
            if known is not None and end is not None and end > known:
                base = False
                causal_count += 1
                issue(field, 'ordering', 'observation finishes after claimed availability', record['recipe_id'])
            if known is not None and rec.get('as_of') is not None and rec['as_of'] > known:
                base = False
                causal_count += 1
                issue(field, 'ordering', 'snapshot as_of follows its claimed availability', record['recipe_id'])
            if start is not None and end is not None and start > end:
                base = False
                issue(field, 'ordering', 'reversed observation interval', record['recipe_id'])
            if known is not None and record['known_at'] is not None and known > record['known_at']:
                base = False
                causal_count += 1
                issue(field, 'ordering', 'dependency later than dependent assertion/snapshot', record['recipe_id'])
            mode = rec.get('evidence_mode', candidate['evidence_mode'])
            if candidate['evidence_mode'] == 'raw_derived' and mode == 'supplied_contemporaneous':
                base = False
                proxy_count += 1
                issue(field, 'supplied_record_missing', 'supplied interpretation cannot be counted as raw-derived evidence', record['recipe_id'])
            if candidate['evidence_mode'] in {'raw_derived', 'supplied_contemporaneous'} and mode in {'source_illustration', 'synthetic_fixture', 'native_control'}:
                base = False
                proxy_count += 1
                issue(field, 'supplied_record_missing', 'retrospective or synthetic evidence cannot establish historical admission', record['recipe_id'])
        if record.get('recipe_base_ok') is False:
            base = False
    for name in ('branch', 'side', 'decision_at'):
        if operands.get(name) != candidate[name]:
            base = False
            issue(name, 'identity', 'bound decision identity differs from candidate')
    for unknown in selected.unknown:
        if unknown.startswith('unknown_order:'):
            base = kleene_and(base, None)
            issue(unknown, 'ordering', 'Strict stage order is unresolved at equal timestamps', 'C02')
    if method_id == 'SIRES' and candidate['predicate'] in {'management', 'reentry'}:
        parent = candidate.get('parent_record')
        if parent is None:
            coverage = kleene_and(coverage, None)
            issue('parent_attempt_id', 'supplied_record_missing', 'Action/reentry has no observed parent entry', 'O142' if candidate['predicate'] == 'management' else 'O144')
        else:
            if parent.get('predicate', PRIMARY[method_id]) != 'sequence':
                base = False
                issue('parent_attempt_id', 'identity', 'Action/reentry parent is not an observed entry unit')
            if any(parent[key] != candidate[key] for key in ('method_id', 'branch', 'instrument_id', 'side', 'band_ids')):
                base = False
                issue('parent_attempt_id', 'identity', 'Action/reentry differs from its parent entry identity')
            parent_binding = parent['operands'].get('decision_at', {})
            parent_object = objects.get(parent_binding.get('object_id'))
            if parent_object is None or parent_object['object_id'] not in parent['object_ids'] or parent_object['recipe_id'] != 'O150' or parent_object['value'].get('decision_at') != parent['decision_at']:
                coverage = kleene_and(coverage, None)
                issue('parent_attempt_id', 'supplied_record_missing', 'Parent entry lacks its actual O150 decision record')
            else:
                used_objects.add(parent_object['object_id'])
                used_evidence.update(parent_object['evidence_ids'])
            if candidate['predicate'] == 'management' and operands.get('decision_at') != parent['decision_at']:
                base = False
                issue('decision_at', 'identity', 'Management expression must use its actual parent entry time')
            if candidate['predicate'] == 'reentry' and operands.get('prior_exit_at') is not None and operands['prior_exit_at'] <= parent['decision_at']:
                base = False
                causal_count += 1
                issue('prior_exit_at', 'ordering', 'Prior exit must follow the actual parent entry')
    for finding in audit_candidate(candidate, operands, objects, assertions, evidence):
        for key, registry, used in (
            ('supporting_object_ids', objects, used_objects),
            ('supporting_assertion_ids', assertions, used_assertions),
            ('supporting_evidence_ids', evidence, used_evidence),
        ):
            identifiers = finding.get(key, [])
            if any(identifier not in registry for identifier in identifiers):
                raise SchemaError('method audit references an unknown supporting record')
            used.update(identifiers)
        if finding['kind'] == 'supporting_records':
            continue
        issue(finding['field'], finding['kind'], finding['reason'], finding.get('recipe_id'))
        if finding.get('affected_output'):
            issues[-1]['affected_output'] = finding['affected_output']
        if finding.get('affects_admission') is False:
            issues[-1]['affects_admission'] = False
            continue
        if finding.get('unknown'):
            coverage = kleene_and(coverage, None)
        else:
            base = False
            causal_count += finding['kind'] == 'ordering'
    for field, contract in contracts.items():
        if field not in selected.fields:
            bindings.setdefault(field, {'value': None, 'type': contract.type,
                                        'recipe_id': contract.recipes[0]})
            bindings[field]['applicability'] = 'not_required'
    result = {**candidate, 'operands': bindings, 'base_ok': base, 'coverage_ok': coverage,
              'sequence_ok': selected.value, 'verdict': verdict(base, coverage, selected.value),
              'failed_prerequisites': selected.failed + [h['reason'] for h in issues if h['kind'] in {'identity', 'ordering'}],
              'hole_ids': sorted({h['hole_id'] for h in issues}), 'holes': issues,
              'detected_causal_violations': causal_count, 'rejected_proxy_attempts': proxy_count,
              'used_object_ids': sorted(used_objects), 'used_assertion_ids': sorted(used_assertions),
              'used_evidence_ids': sorted(used_evidence),
              'source_versions': sorted({rec['source_version'] for rec in
                                          [*(objects[oid] for oid in used_objects), *(assertions[aid] for aid in used_assertions), *(evidence[eid] for eid in used_evidence)]}),
              'year': datetime.fromtimestamp(candidate['decision_at'] // 1_000_000_000, timezone.utc).astimezone(ZoneInfo('America/New_York')).year}
    if candidate.get('evidence_mode')=='native_control':
        result.update(variant='comparison',faithful_eligible=False,historical_eligible=False)
    return result


def fixture_document(method_id, predicate, fid, op):
    """Only this fixture constructor may turn printed algebra values into supplied observations."""
    contracts = fields_for(method_id)
    branch = op.get('branch', BRANCHES[method_id][0])
    if method_id == 'JETBUNDLE-STATES':
        branch = op.get('state', branch)
    if method_id == 'STOIC-RISK':
        branch = op.get('risk_stage', branch)
    decision = op.get('decision_at', op.get('state_at', op.get('order_at', op.get('sample_start_at', 1_000_000_000))))
    side = op.get('side', 'not_applicable')
    band = op.get('band_id', 'fixture-band')
    common = {'method_id': method_id, 'branch': branch, 'side': side,
              'instrument_id': op.get('instrument_id', 'fixture-instrument'), 'band_id': band}
    source = f'FORMULAS {METHOD_BY_ID[method_id]} {fid}'
    candidate = {**common, 'candidate_id': fid, 'predicate': predicate,
                 'session_date_et': datetime.fromtimestamp(decision // 1_000_000_000, timezone.utc).astimezone(ZoneInfo('America/New_York')).date().isoformat(),
                 'decision_at': decision, 'band_ids': [band], 'object_ids': [], 'assertion_ids': [],
                 'cohort_id': 'synthetic-fixtures', 'evidence_mode': 'synthetic_fixture', 'operands': {}}
    doc = {'formula_version': FORMULA_VERSION, 'candidates': [candidate], 'objects': [], 'assertions': [], 'evidence': []}
    payload = jsonable({key: value for key, value in op.items() if not key.startswith('_')})
    payload['observation'] = {'printed_inputs': deepcopy(payload), 'source': source}
    for field, value in op.items():
        if field not in contracts:
            continue
        contract = contracts[field]
        recipe = contract.recipes[0]
        known = value if contract.type.startswith('event_key') and value is not None else min(decision, op.get('confirm_at') or decision)
        stage = stage_at(method_id, field, op)
        if stage is not None and not contract.type.startswith('event_key'):
            known = stage
        evidence_id, object_id = f'{fid}:e:{field}', f'{fid}:o:{field}'
        ev = {**common, 'evidence_id': evidence_id, 'source_ref': source, 'source_version': FORMULA_VERSION,
              'description': f'Synthetic printed observation for {field}. {contract.rule}', 'payload': payload,
              'observation_start': known, 'observation_end': known, 'known_at': known,
              'evidence_mode': 'synthetic_fixture'}
        doc['evidence'].append(ev)
        obj = {**common, 'object_id': object_id, 'recipe_id': recipe, 'branch_scope': [branch],
               'author': method_id, 'parent_ids': [], 'source_ref': source, 'source_version': FORMULA_VERSION,
               'value': {field: value}, 'units': {field: contract.type}, 'formation_start': known,
               'formation_end': known, 'as_of': known, 'known_at': known,
               'state': 'supplied' if value is not None else 'hole',
               'hole_ids': [] if value is not None else [f'HOLE:{recipe}:{field}'],
               'evidence_ids': [evidence_id], 'raw_member_locators': [{'fixture_id': fid, 'field': field}]}
        doc['objects'].append(obj)
        candidate['object_ids'].append(object_id)
        if contract.type.startswith('boolean'):
            assertion_id = f'{fid}:a:{field}'
            assertion = {**common, 'assertion_id': assertion_id, 'field': field, 'value': value,
                         'recipe_id': recipe, 'candidate_id': fid, 'evidence_ids': [evidence_id],
                         'observation_start': known, 'observation_end': known, 'known_at': known,
                         'evidence_mode': 'synthetic_fixture', 'source_ref': source,
                         'source_version': FORMULA_VERSION, 'reason': ev['description']}
            doc['assertions'].append(assertion)
            candidate['assertion_ids'].append(assertion_id)
            candidate['operands'][field] = {'assertion_id': assertion_id}
        else:
            candidate['operands'][field] = {'object_id': object_id, 'value_field': field}
    return doc


def bind_fixture(method_id, predicate, fid, op):
    document = fixture_document(method_id, predicate, fid, op)
    candidates, objects, assertions, evidence = parse_manifest(document, method_id)
    result = score_episode(candidates[fid], objects, assertions, evidence)
    result['fixture_records'] = jsonable(document)
    return result
