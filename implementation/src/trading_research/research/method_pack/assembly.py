"""Explicit M01--M12 method operands from identified native/source producers.

This module is an assembler, not a strategy detector. The application chooses
source branches and object identities before seeing outcomes. Output aliases are
closed semantic derivations with dated roles; arbitrary value_field is forbidden.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from decimal import Decimal
from functools import lru_cache
from typing import Any

from . import FORMULA_VERSION
from .catalog import BRANCHES, EXTRA_PREDICATES, METHOD_BY_ID, PRIMARY
from .contracts import OUTPUT_SCHEMAS, fields_for, validate_output
from .evidence import SchemaError, _has_observation, parse_manifest, score_episode, typed, mark_source_admitted, audit_source_domain_object
from .expressions import evaluate
from .native_resolution import ns
from .logic import kleene_and
from .objects.native_boundary import NATIVE_PRODUCERS, DERIVED_PRODUCERS
from .protocol import jsonable, run_recipe, RECIPES
from .source_config import SourceSetting
from .semantic_views import ROLES, projection, project, audit_interpretation, source_interpretation_supported, source_citation, AUTHORS

HOLE_KINDS = {'missing_implementation', 'source_definition', 'data_coverage', 'supplied_record_missing'}


@dataclass(frozen=True)
class OperandBinding:
    method_id: str
    field: str
    type: str
    units: str
    producers: tuple[str, ...]
    semantic_role: str
    branches: tuple[str, ...]
    rule: str
    identity_keys: tuple[str, ...] = ('method_id', 'branch', 'instrument_id', 'band_id', 'side')
    availability_rule: str = 'all incorporated observations and parents known by the actual stage of use'


# These are specific source-role derivations, not user-configurable field aliases.
# Each entry: recipe alternatives, required dated role, exact native quantity.
SEMANTIC_FIELDS = {
    ('GB-VWAP', 'asia_high'): (('O046',), 'asia', 'box_high'),
    ('GB-VWAP', 'asia_known_at'): (('O046',), 'asia', '@known_at'),
    ('GB-VWAP', 'london_high'): (('O046',), 'london', 'box_high'),
    ('GB-VWAP', 'london_known_at'): (('O046',), 'london', '@known_at'),
    ('GB-VWAP', 'breakout_close'): (('O004',), 'breakout_candle', 'C'),
    ('GB-VWAP', 'breakout_at'): (('O004',), 'breakout_candle', '@known_at'),
    ('GB-VWAP', 'vwap_at_retest'): (('O030',), 'vwap_at_retest', 'vwap'),
    ('GB-VWAP', 'vwap_known_at'): (('O030',), 'vwap_at_retest', '@known_at'),
    ('GB-VWAP', 'vwap_reset_verified'): (('O030',), 'vwap_at_retest', 'vwap_reset_verified'),
    ('KEANI-OPEN-ABOVE-VALUE', 'prior_vah'): (('O062', 'O086'), 'prior_session_value', 'vah'),
    ('KEANI-OPEN-ABOVE-VALUE', 'a_low'): (('O078',), 'opening_a', 'a_low'),
    ('KEANI-OPEN-ABOVE-VALUE', 'a_period_complete'): (('O078',), 'opening_a', 'a_period_complete'),
    ('KEANI-OPEN-ABOVE-VALUE', 'a_end_at'): (('O078',), 'opening_a', 'a_end_at'),
    ('KEANI-OPEN-ABOVE-VALUE', 'dev_vah_at_break'): (('O063', 'O062'), 'developing_value_before_break', 'vah'),
    ('KEANI-OPEN-ABOVE-VALUE', 'dev_vah_known_at'): (('O063', 'O062'), 'developing_value_before_break', '@known_at'),
    ('KEANI-OPEN-ABOVE-VALUE', 'breakout_close'): (('O004',), 'breakout_candle', 'C'),
    ('KEANI-OPEN-ABOVE-VALUE', 'breakout_at'): (('O004',), 'breakout_candle', '@known_at'),
    ('MEMBER-TWO-REASONS', 'area_known_at'): (('O072',), 'prior_reaction_area', '@known_at'),
    ('MEMBER-TWO-REASONS', 'hvn_known_at'): (('O066',), 'independent_minor_hvn', '@known_at'),
}


@lru_cache(maxsize=1024)
def _applicable_branches(method_id, field):
    branches = list(BRANCHES[method_id])
    if method_id == 'SIRES':
        branches += ['pre_file_early', 'third_retest_case', 'late_resistance_fade_case', 'ofm_early_refill_case']
    predicates = [PRIMARY[method_id]] + EXTRA_PREDICATES.get(method_id, [])
    selected = []
    if method_id == 'SIRES' and field == 'sires_branch_ok':
        return tuple(BRANCHES[method_id])
    for branch in branches:
        for predicate in predicates:
            for side in ('long', 'short', 'not_applicable'):
                for mode in (None, 'five_minute_close', 'reclaim_and_hold') if method_id == 'GB-FAIL' else (None,):
                    try:
                        fields = evaluate(method_id, predicate, {'branch': branch, 'side': side,
                                          'state': branch, 'risk_stage': branch, 'confirmation_mode': mode}).fields
                    except ValueError:
                        continue
                    if field in fields:
                        selected.append(branch)
    return tuple(dict.fromkeys(selected))


@lru_cache(maxsize=13)
def operand_inventory(method_id=None):
    """Every published operand, including alternatives and secondary predicates.

    Inventory completeness is separate from availability of producer code/data.
    No missing output is reclassified as an unpublished source definition here.
    """
    methods = [method_id] if method_id is not None else list(METHOD_BY_ID)
    out = []
    for method in methods:
        for name, contract in fields_for(method).items():
            role = ROLES[method,name]
            out.append(OperandBinding(method, name, contract.type, contract.type,
                                      contract.recipes, role, _applicable_branches(method, name), contract.rule))
    return out


def producer_coverage_matrix(method_id=None):
    """Separate actual binding code, native adapters, and source audit paths.

    A registered recipe is not an implemented method projection. In particular,
    a source-only audit does not acquire a native detector merely by registration.
    """
    rows = []
    for spec in operand_inventory(method_id):
        semantic = SEMANTIC_FIELDS.get((spec.method_id, spec.field))
        producers = []
        for rid in spec.producers:
            schema = OUTPUT_SCHEMAS.get(rid)
            view = projection(spec.method_id, spec.field, rid)
            output = view.path if view else None
            has_projection = view is not None and schema is not None and (output == '@known_at' or output.split('.')[0] in schema)
            routes = ['supplied_source_interpretation'] if source_interpretation_supported(spec.method_id,spec.field) else []
            if has_projection and rid in NATIVE_PRODUCERS:
                routes.append('resolved_native')
            if has_projection and rid in DERIVED_PRODUCERS:
                routes.append('parent_derived')
            if has_projection and rid in RECIPES:
                routes.append('supplied_source_audit')
            producers.append({'recipe_id': rid, 'native_producer': rid in NATIVE_PRODUCERS,
                'derived_producer': rid in DERIVED_PRODUCERS, 'complete_schema': schema is not None,
                'required_output': output, 'projection': view.operation if view else 'attributed_source_interpretation',
                'projection_arguments': list(view.arguments) if view else [],
                'binding_implemented': bool(routes), 'routes': routes,
                'source_audit_rule': 'exact cited author observation with immutable source bytes, field-specific criterion, dated role, typed value and supporting observations; domain rerun/full schema for quantitative producer route'})
        implemented = any(p['binding_implemented'] for p in producers)
        if any('resolved_native' in p['routes'] for p in producers):
            native_status = 'implemented'
        elif any('parent_derived' in p['routes'] for p in producers):
            native_status = 'parent_derived'
        elif any('supplied_source_interpretation' in p['routes'] for p in producers):
            # The field is a source interpretation, even when one of its
            # alternative objects also computes unrelated native quantities.
            native_status = 'source_only'
        elif any(p['native_producer'] for p in producers):
            # A declared native alternative whose projection is not available
            # is a genuine implementation gap.  Keep this distinct from a
            # source-only operand, for which no native detector is promised.
            native_status = 'missing_native_implementation'
        elif any('supplied_source_audit' in p['routes'] for p in producers):
            # Account/journal statistics require actual external process
            # records. Their implemented domain audit is a distinct route
            # from market-member computation or qualitative interpretation.
            native_status = 'supplied_record'
        elif producers:
            native_status = 'no_native_producer'
        else:
            native_status = 'no_declared_producer'
        rows.append({**asdict(spec), 'producer_status': producers,
            'binding_status': 'implemented' if implemented else 'missing_implementation',
            'native_status': native_status,
            'supplied_source_alternative': ('audited structured source/process records; full recipe rerun and typed projection'
                if native_status == 'supplied_record' else
                'audited source interpretation; remains supplied, never a native detector')})
    return rows


def _role_definition(role, obj, candidate):
    if not isinstance(role, dict) or role.get('object_id') != obj['object_id']:
        raise SchemaError('semantic role must identify its actual producer object')
    for key in ('method_id', 'instrument_id'):
        if str(role.get(key)) != str(candidate[key]) or str(obj[key]) != str(candidate[key]):
            raise SchemaError('semantic role identity differs from object/candidate')
    if role.get('author') != obj['author']:
        raise SchemaError("semantic role cannot transfer another author's reference")
    definition = SourceSetting.parse(role.get('source_definition', {}))
    control=candidate.get('evidence_mode')=='native_control' and candidate.get('variant')=='comparison'
    if definition.status != 'fact' and not (control and definition.status=='inference'):
        return None
    value = definition.resolve(comparison=control)
    if not isinstance(value, dict):
        raise SchemaError('dated semantic role requires actual source window definition')
    if candidate.get('evidence_mode') != 'synthetic_fixture':
        from .source_config import load_catalog
        from .catalog import METHOD_BY_ID
        catalog=load_catalog()
        cid=role.get('source_configuration_id');key=role.get('source_setting_key')
        config=catalog['configurations'].get(cid)
        if config is None or config.get('version')!=role.get('source_configuration_version'):
            raise SchemaError('semantic role requires its frozen catalog configuration/version')
        if config.get('author') not in AUTHORS[candidate['method_id']] or METHOD_BY_ID[candidate['method_id']] not in config.get('scope',[]):
            raise SchemaError('semantic role configuration has foreign author/method scope')
        control_artifact=role.get('control_artifact') if control else None
        if control_artifact is not None:
            import json,gzip,hashlib
            from pathlib import Path
            path=Path(control_artifact.get('path',''))
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=control_artifact.get('sha256'):
                raise SchemaError('comparison role needs its actual immutable selection artifact')
            data=json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
            pointer=control_artifact.get('json_pointer','')
            for component in pointer.strip('/').split('/') if pointer else []:
                component=component.replace('~1','/').replace('~0','~')
                try:data=data[int(component)] if isinstance(data,list) else data[component]
                except (KeyError,IndexError,ValueError,TypeError) as exc:raise SchemaError('comparison role artifact pointer is absent') from exc
            if not isinstance(data,dict) or data.get('source_case_id')!=candidate.get('source_case_id') or data.get('role')!=role.get('role'):
                raise SchemaError('comparison role artifact has foreign case/role identity')
            if data.get('object_id')!=obj['object_id'] or str(data.get('instrument_id'))!=str(obj['instrument_id']):
                raise SchemaError('comparison role artifact has foreign producer identity')
            for key_name in ('formation_start','formation_end'):
                if ns(data.get(key_name),key_name)!=obj[key_name] or ns(value.get(key_name),key_name)!=obj[key_name]:
                    raise SchemaError('comparison role differs from actual frozen selection window')
            if value.get('role') != role.get('role') or value.get('session_date_et') != candidate.get('session_date_et'):
                raise SchemaError('comparison role lacks matching source date/role identity')
            if obj.get('known_at') is not None and obj['formation_end'] > obj['known_at']:
                raise SchemaError('semantic reference backdates its formation')
            obj['source_role_comparison']=True
            return value
        control_window_id=role.get('control_window_id') if control else None
        if control_window_id:
            from datetime import datetime
            from zoneinfo import ZoneInfo
            case=next((row for row in catalog['cases'] if row['case_id']==candidate.get('source_case_id')),None)
            if case is None or case.get('method_id')!=candidate['method_id'] or cid not in case.get('configuration_ids',[]):
                raise SchemaError('semantic control has foreign source case/configuration')
            windows=[] if case is None else [row for row in case.get('native_control_windows',[]) if row.get('control_window_id')==control_window_id]
            if len(windows)!=1 or windows[0].get('version')!=role.get('control_window_version') or windows[0].get('role')!=role.get('role'):
                raise SchemaError('semantic control needs its exact frozen catalog case/window/version/role')
            window=windows[0]
            if window.get('timezone')!='America/New_York':raise SchemaError('control window must use documented ET clock')
            frozen_window={name:int(datetime.fromisoformat(window[clock]).replace(tzinfo=ZoneInfo('America/New_York')).timestamp())*1_000_000_000
                           for name,clock in [('formation_start','start_et'),('formation_end','end_et')]}
            setting=SourceSetting.parse({'status':window['status'],'value':frozen_window,'source_refs':window['source_refs'],'reason':window['reason']})
        else:
            if key not in config.get('settings',{}):raise SchemaError('semantic role has unknown catalog setting key')
            setting=SourceSetting.parse(config['settings'][key])
        if setting.status!='fact' and not (control and setting.status=='inference'):
            obj.setdefault('_role_status',{})[role['role']]=setting.status
            return None
        for ref in setting.source_refs:
            pieces=ref.split(':')
            if len(pieces)!=2 or not pieces[1].isdigit() or pieces[0] not in catalog['sources']:
                raise SchemaError('semantic role catalog fact lacks exact source page')
            source=catalog['sources'][pieces[0]];page=int(pieces[1])
            try:source_citation({'source_key':pieces[0],'source_file':source['path'],'sha256':source['sha256'],
                                 'page':page,'image_id':f'{pieces[0]}:{page}:page'},candidate['method_id'])
            except ValueError as exc:raise SchemaError(str(exc)) from exc
        frozen=setting.resolve(comparison=control)
        if control and isinstance(frozen,dict) and role.get('role') in {'asia','london'} and not control_window_id:
            frozen=frozen.get(role['role'])
        if control:obj['source_role_comparison']=True
        if isinstance(frozen,dict) and all(k in frozen for k in ('formation_start','formation_end')):
            source_window={k:ns(frozen[k],k) for k in ('formation_start','formation_end')}
        else:
            from datetime import date,timedelta
            from .clocks import et_ns
            if isinstance(frozen,list) and len(frozen) in {2,3}:
                start_clock,end_clock=frozen[:2];start_day=0;end_day=0
                if len(frozen)==3 and frozen[2]!='America/New_York':
                    raise SchemaError('source role clock timezone is not the documented ET clock')
                if end_clock<=start_clock:start_day=-1
            elif isinstance(frozen,dict) and 'start_et' in frozen and 'end_et' in frozen:
                start_clock,end_clock=frozen['start_et'],frozen['end_et']
                if frozen.get('timezone','America/New_York')!='America/New_York':
                    raise SchemaError('source role clock timezone is not the documented ET clock')
                start_day=frozen.get('start_day_offset',-1 if end_clock<=start_clock else 0);end_day=frozen.get('end_day_offset',0)
            else:raise SchemaError('catalog source setting does not define a complete role window')
            try:
                day=date.fromisoformat(value['session_date_et'])
                sh,sm=map(int,start_clock.split(':'));eh,em=map(int,end_clock.split(':'))
                source_window={'formation_start':et_ns(day+timedelta(days=start_day),sh,sm),
                               'formation_end':et_ns(day+timedelta(days=end_day),eh,em)}
            except (ValueError,TypeError,KeyError) as exc:raise SchemaError('invalid catalog role clock') from exc
        if any(ns(value.get(k),k)!=t for k,t in source_window.items()):
            raise SchemaError('semantic role window differs from its actual catalog source definition')
    expected = {'formation_start': obj['formation_start'], 'formation_end': obj['formation_end']}
    for key, want in expected.items():
        if ns(value.get(key), f'semantic {key}') != want:
            raise SchemaError('semantic role does not match its exact native formation window')
    if value.get('role') != role.get('role') or not value.get('session_date_et'):
        raise SchemaError('semantic role lacks its source date/role identity')
    if obj.get('known_at') is not None and obj['formation_end'] > obj['known_at']:
        raise SchemaError('semantic reference backdates its formation')
    return value


def _semantic_projection(field, obj, candidate, roles):
    spec = SEMANTIC_FIELDS.get((candidate['method_id'], field))
    if spec is None:
        return False
    recipes, required_role, quantity = spec
    if obj['state']=='supplied' and field in obj['value']:
        # Exact named source observations use source audit below; only a
        # native numeric rename requires this separate source-window role.
        return False
    if obj['recipe_id'] not in recipes:
        raise SchemaError(f'{field}: wrong semantic producer')
    matching = [r for r in roles if r.get('role') == required_role and r.get('object_id') == obj['object_id']]
    if len(matching) != 1:
        raise SchemaError(f'{field}: needs one explicitly selected {required_role} source role')
    definition = _role_definition(matching[0], obj, candidate)
    if definition is None:
        obj.setdefault('_semantic_holes',{})[field]='source_definition'
        obj['value'].pop(field,None)
        return False
    if required_role == 'prior_session_value':
        if definition['session_date_et'] >= candidate['session_date_et']:
            raise SchemaError('prior value role must have its actual earlier session date')
    elif required_role in {'asia', 'london', 'opening_a', 'breakout_candle', 'developing_value_before_break'}:
        if definition['session_date_et'] != candidate['session_date_et']:
            raise SchemaError('current source role belongs to another session')
    if obj.get('evidence_class') not in {'resolved_native', 'parent_derived'}:
        # Direct source observations remain an attributed alternative. A drawn
        # H label cannot be silently renamed into a native Asia/London high.
        if obj['state'] == 'supplied' and field in obj['value']:
            return False
        raise SchemaError(f'{field}: semantic numeric derivation needs resolved native observations')
    if quantity == '@known_at':
        value = obj['known_at']
    elif quantity in obj['value']:
        value = obj['value'][quantity]
    else:
        return False
    obj['value'][field] = typed(value, fields_for(candidate['method_id'])[field].type, field)
    obj['units'][field] = fields_for(candidate['method_id'])[field].type
    if required_role in {'asia', 'london'}:
        obj['value']['source_session_id'] = obj['object_id']
    if required_role == 'breakout_candle':
        obj['value']['breakout_bar_id'] = obj['value'].get('bar_id')
        obj['value']['breakout_bar_complete'] = obj['value'].get('complete')
    obj.setdefault('semantic_derivations', []).append({'field': field, 'source_quantity': quantity,
        'role': required_role, 'object_id': obj['object_id'], 'parent_ids': list(obj['parent_ids']),
        'source_definition': deepcopy(matching[0]['source_definition'])})
    return True


def _check_distinct_roles(candidate, roles):
    role_ids = {}
    for role in roles:
        role_ids.setdefault(role.get('role'), set()).add(role.get('object_id'))
    if any(len(ids) != 1 for ids in role_ids.values()):
        raise SchemaError('a selected semantic role must retain one actual producer identity')
    pairs = [('asia', 'london'), ('prior_session_value', 'developing_value_before_break'),
             ('prior_reaction_area', 'independent_minor_hvn')]
    for first, second in pairs:
        a = {r.get('object_id') for r in roles if r.get('role') == first}
        b = {r.get('object_id') for r in roles if r.get('role') == second}
        if a & b:
            raise SchemaError(f'{first} and {second} cannot reuse one producer identity')


def _actual_source_observation(record, evidence):
    observations = [evidence[eid] for eid in record.get('evidence_ids', []) if eid in evidence]
    return any(_has_observation(ev.get('payload', {})) and ev.get('source_ref') and ev.get('source_version')
               for ev in observations)


def _audit_source_operand(field, record, evidence, candidate):
    """Recompute a historical source operand from its cited domain inputs.

    Synthetic printed algebra has its own explicitly synthetic admission path.
    Historical source observations cannot pass by attaching unrelated prices to
    a copied result, or by merely naming a rule identifier.
    """
    if candidate.get('evidence_mode') == 'synthetic_fixture':
        return
    rid = record['recipe_id']
    for eid in record.get('evidence_ids', []):
        try:
            interpreted = audit_interpretation(candidate['method_id'],field,rid,record,candidate,evidence[eid].get('payload', {}))
        except ValueError as exc:
            raise SchemaError(str(exc)) from exc
        if interpreted is not None:
            value = typed(interpreted['value'],fields_for(candidate['method_id'])[field].type,field)
            original = record['value'].get(field) if isinstance(record['value'],dict) else record['value']
            if value is not None and value != typed(original,fields_for(candidate['method_id'])[field].type,field):
                raise SchemaError(f'{field}: supplied value differs from actual source interpretation')
            if isinstance(record['value'],dict): record['value'][field] = value
            else: record['value'] = value
            record.setdefault('source_audits', {})[field] = interpreted
            evidence[eid]['payload'][field] = value
            evidence[eid]['payload'].setdefault('audited_fields',[]).append(field)
            record['evidence_class'] = 'supplied_source_interpretation'
            record['recipe_coverage_ok'] = True if interpreted['status'] == 'fact' else None
            mark_source_admitted(record,field)
            return
    semantic = SEMANTIC_FIELDS.get((candidate['method_id'], field))
    view = projection(candidate['method_id'],field,rid)
    output = view.path if view else field
    if rid not in RECIPES or rid not in OUTPUT_SCHEMAS:
        raise SchemaError(f'{field}: source audit implementation/schema missing')
    matches = []
    for eid in record.get('evidence_ids', []):
        ev = evidence[eid]
        payload = ev.get('payload', {})
        inputs = payload.get('recipe_inputs')
        if not isinstance(inputs, dict) or not inputs or payload.get('recipe_id') != rid:
            continue
        if not _has_observation(inputs):
            continue
        for key in ('instrument_id', 'method_id', 'author'):
            expected = record.get(key, candidate.get(key))
            if key in inputs and str(inputs[key]) != str(expected):
                raise SchemaError(f'{field}: cited recipe input has foreign {key}')
        try:source_citation(payload.get('source_citation'),candidate['method_id'])
        except ValueError as exc:raise SchemaError(str(exc)) from exc
        audited = validate_output(run_recipe(rid, deepcopy(inputs)))
        if audited.base_ok is False or audited.state == 'invalid':
            raise SchemaError(f'{field}: cited recipe observation is invalid')
        value = project(view,audited.value,{'known_at':audited.known_at},candidate) if view else audited.value.get(output)
        actual = record['value'].get(field) if isinstance(record['value'], dict) else record['value']
        if typed(value, fields_for(candidate['method_id'])[field].type, field) != typed(actual, fields_for(candidate['method_id'])[field].type, field):
            raise SchemaError(f'{field}: supplied result differs from cited recipe rerun')
        if value is not None and (audited.known_at is None or record['known_at'] is None or audited.known_at > record['known_at']):
            raise SchemaError(f'{field}: supplied result backdates cited recipe availability')
        evidence[eid]['payload'][field] = value
        evidence[eid]['payload'].setdefault('audited_fields',[]).append(field)
        matches.append({'recipe_id': rid, 'evidence_id': eid, 'output': output,
                        'known_at': audited.known_at, 'coverage_ok': audited.coverage_ok, 'base_ok': audited.base_ok})
    if not matches:
        raise SchemaError(f'{field}: actual cited recipe_inputs required for source audit')
    record.setdefault('source_audits', {})[field] = matches
    for match in matches:
        record['recipe_coverage_ok'] = kleene_and(record.get('recipe_coverage_ok', True), match['coverage_ok'])
        record['recipe_base_ok'] = kleene_and(record.get('recipe_base_ok', True), match['base_ok'])
    record['evidence_class'] = 'supplied_source_audit'
    mark_source_admitted(record,field)


def _limitation_index(limitations, candidate):
    out = {}
    for row in limitations:
        if row.get('field') not in fields_for(candidate['method_id']) or row.get('kind') not in HOLE_KINDS:
            raise SchemaError('unrecognized operand limitation')
        if not row.get('reason') or not row.get('source_ref'):
            raise SchemaError('operand limitation needs an evidence reason and reference')
        if row['field'] in out:
            raise SchemaError('duplicate operand limitation')
        if row['kind'] == 'source_definition':
            setting = SourceSetting.parse(row.get('source_setting', {}))
            if setting.status not in {'unknown', 'source_conflict'}:
                raise SchemaError('source definition hole requires documented unknown/conflict')
        out[row['field']] = deepcopy(row)
    return out


@dataclass
class AssembledEpisode:
    manifest: dict
    parsed: tuple
    result: dict
    bindings: list[dict]
    holes: list[dict]


def assemble_episode(candidate, objects, assertions=(), evidence=(), *, bindings=None,
                     roles=(), limitations=(), resolver=None, _parsed_context=None, _implementation_objects=()):
    """Resolve/validate objects, bind actual operands, and call score_episode.

    ``bindings`` maps an operand to {object_id: ID} or {assertion_id: ID}; it
    never contains a value or value_field. Source role records identify dated
    references. Missing implementations return explicit assembly holes, while
    nonexistent locators and witnessed identity errors raise SchemaError.
    """
    candidate = deepcopy(candidate)
    method = candidate['method_id']
    candidate.setdefault('predicate', PRIMARY[method])
    bound = deepcopy(bindings if bindings is not None else candidate.get('operands', {}))
    for field, binding in bound.items():
        if field not in fields_for(method):
            raise SchemaError(f'unknown method operand {field}')
        if not isinstance(binding, dict) or set(binding) not in ({'object_id'}, {'assertion_id'}):
            raise SchemaError(f'{field}: binding identifies exactly one producer, never an alias or literal')
    object_rows = deepcopy(list(objects))
    assertion_rows = deepcopy(list(assertions))
    evidence_rows = deepcopy(list(evidence))
    candidate['operands'] = deepcopy(bound)
    candidate.setdefault('object_ids', [o['object_id'] for o in object_rows])
    candidate.setdefault('assertion_ids', [a['assertion_id'] for a in assertion_rows])
    limits = _limitation_index(limitations, candidate)
    _check_distinct_roles(candidate, roles)
    implementation_objects = set(_implementation_objects)
    for obj in object_rows:
        if obj['state'] == 'computed' and (obj['recipe_id'] not in NATIVE_PRODUCERS and obj['recipe_id'] not in DERIVED_PRODUCERS or obj['recipe_id'] not in OUTPUT_SCHEMAS):
            # Preserve the unavailable producer in scope without publishing its
            # supplied summary as a computed observation or padding null keys.
            implementation_objects.add(obj['object_id'])
            obj['state'], obj['value'], obj['known_at'] = 'hole', {}, None
            obj['hole_ids'] = list(dict.fromkeys(obj['hole_ids'] + [f"HOLE:{obj['recipe_id']}:missing_implementation"]))
            obj['recipe_base_ok'], obj['recipe_coverage_ok'] = None, None
    manifest = {'formula_version': FORMULA_VERSION, 'candidates': [candidate], 'objects': object_rows,
                'assertions': assertion_rows, 'evidence': evidence_rows}
    # Retain replayable inputs: parse_manifest replaces computed values with
    # resolved outputs, while assembly additionally applies closed role maps.
    replay = deepcopy(manifest)
    parsed = _parsed_context if _parsed_context is not None else parse_manifest(manifest, method, resolver=resolver)
    candidate = parsed[0][candidate['candidate_id']]
    candidate['operands'] = deepcopy(bound)
    object_index, assertion_index, evidence_index = parsed[1:]
    if method=='JJ-TBR' and candidate['predicate']=='management':
        action=object_index[candidate['action_object_id']]
        if candidate.get('evidence_mode')!='synthetic_fixture' and action.get('state')=='supplied':
            audit_source_domain_object(action,evidence_index)
        result=score_episode(candidate,object_index,assertion_index,evidence_index)
        issues=[]
        if action['object_id'] in implementation_objects:
            issues.append({'field':'action_policy_ok','kind':'missing_implementation','recipe_id':'O142',
                           'reason':'management producer unavailable','source_ref':action['source_ref']})
        result.update(assembly_holes=issues,software_complete=not issues,observation_unit='management')
        if candidate.get('evidence_mode')=='native_control':
            result.update(variant='comparison',faithful_eligible=False,historical_eligible=False)
        replay['assembly']={'schema':'phase1-method-assembly-v1','roles':deepcopy(list(roles)),
                            'limitations':deepcopy(list(limitations))}
        return AssembledEpisode(replay,parsed,result,[],issues)
    issues = []
    actual_values = {'branch': candidate['branch'], 'side': candidate['side'], 'decision_at': candidate['decision_at']}
    for field, binding in bound.items():
        record = object_index.get(binding.get('object_id')) if 'object_id' in binding else assertion_index.get(binding.get('assertion_id'))
        if record is None:
            raise SchemaError(f'{field}: nonexistent operand producer')
        if record['recipe_id'] not in fields_for(method)[field].recipes:
            raise SchemaError(f'{field}: foreign semantic producer')
        if 'object_id' in binding:
            semantic = (method, field) in SEMANTIC_FIELDS
            if semantic and record['object_id'] not in implementation_objects and record['state'] != 'invalid':
                _semantic_projection(field, record, candidate, roles)
            if not semantic and record.get('evidence_class') in {'resolved_native','parent_derived'}:
                view = projection(method,field,record['recipe_id'])
                if view is not None:
                    role_rows = [r for r in roles if r.get('role') == ROLES[method,field] and r.get('object_id') == record['object_id']]
                    if len(role_rows) != 1:
                        raise SchemaError(f'{field}: requires its selected {ROLES[method,field]} source role')
                    if _role_definition(role_rows[0],record,candidate) is None:
                        record.setdefault('_semantic_holes',{})[field]='source_definition'
                        record['value'].pop(field,None)
                    else:
                        record['value'][field] = typed(project(view,record['value'],record,candidate),fields_for(method)[field].type,field)
                        record['units'][field] = fields_for(method)[field].type
                        record.setdefault('semantic_derivations',[]).append({'field':field,'source_quantity':view.path,'operation':view.operation,'role':ROLES[method,field],'object_id':record['object_id']})
            value = record['value'].get(field)
            if record['state'] == 'supplied' and value is not None and not _actual_source_observation(record, evidence_index):
                raise SchemaError(f'{field}: supplied value lacks its actual cited observation')
            if record['state'] == 'supplied' and value is not None:
                _audit_source_operand(field, record, evidence_index, candidate)
                value = record['value'].get(field)
            if field not in record['value']:
                kind = record.get('_semantic_holes',{}).get(field) or ('missing_implementation' if record['state'] != 'supplied' else 'supplied_record_missing')
                candidate['operands'].pop(field, None)
                issues.append({'field': field, 'kind': kind, 'recipe_id': record['recipe_id'],
                               'reason': 'producer does not emit its required semantic output', 'source_ref': fields_for(method)[field].rule})
        else:
            value = record['value']
            if candidate.get('evidence_mode')!='synthetic_fixture' and record['evidence_mode']=='raw_derived' and value is not None:
                raise SchemaError(f'{field}: raw-derived operand must bind its actual resolved producer object')
            if value is not None and record['evidence_mode'] != 'raw_derived' and not _actual_source_observation(record, evidence_index):
                raise SchemaError(f'{field}: attributed interpretation lacks its actual cited observation')
            if value is not None and record['evidence_mode'] != 'raw_derived':
                _audit_source_operand(field, record, evidence_index, candidate)
                value = record['value']
        actual_values[field] = typed(value, fields_for(method)[field].type, field)
    selected = evaluate(method, candidate['predicate'], actual_values).fields
    # Only the source-selected branch is scored. Missing operands of unrelated
    # alternatives remain in the inventory, not artificial candidate holes.
    issues = [issue for issue in issues if issue['field'] in selected]
    existing = {issue['field'] for issue in issues}
    coverage_rows = {r['field']: r for r in producer_coverage_matrix(method)}
    for field in sorted(selected & fields_for(method).keys()):
        if (field in bound and actual_values.get(field) is not None) or field in existing:
            continue
        if field in limits:
            issue = limits[field]
        elif field in bound:
            binding = bound[field]
            record = object_index.get(binding.get('object_id')) if 'object_id' in binding else assertion_index[binding['assertion_id']]
            kind = 'data_coverage' if 'recipe_coverage_ok' in record and record['recipe_coverage_ok'] is not True else 'supplied_record_missing'
            issue = {'field': field, 'kind': kind, 'reason': 'bound source operand is unknown', 'source_ref': fields_for(method)[field].rule}
        else:
            row = coverage_rows[field]
            kind = 'missing_implementation' if row['binding_status'] == 'missing_implementation' else 'supplied_record_missing'
            issue = {'field': field, 'kind': kind, 'reason': 'required operand has no selected actual producer', 'source_ref': fields_for(method)[field].rule}
        issues.append(issue)
    result = score_episode(candidate, object_index, assertion_index, evidence_index)
    result['assembly_holes'] = deepcopy(issues)
    if candidate.get('evidence_mode')=='native_control':
        result.update(variant='comparison',faithful_eligible=False,historical_eligible=False,source_role_comparison=True)
    result['software_complete'] = not any(i['kind'] == 'missing_implementation' for i in issues)
    result['observation_unit'] = candidate['predicate']
    inventory = []
    for spec in operand_inventory(method):
        binding = bound.get(spec.field)
        inventory.append({**asdict(spec), 'binding': binding,
                          'applicability': 'selected' if spec.field in selected else 'not_selected',
                          'value': jsonable(actual_values.get(spec.field)) if spec.field in selected else None})
    replay['assembly'] = {'schema': 'phase1-method-assembly-v1', 'roles': deepcopy(list(roles)),
                          'limitations': deepcopy(list(limitations))}
    return AssembledEpisode(replay, parsed, result, inventory, issues)


def replay_assembled(manifest, *, resolver=None):
    metadata = manifest.get('assembly', {})
    if metadata.get('schema') != 'phase1-method-assembly-v1' or len(manifest.get('candidates', [])) != 1:
        raise SchemaError('expected one replayable assembled episode')
    return assemble_episode(manifest['candidates'][0], manifest['objects'], manifest['assertions'], manifest['evidence'],
                            roles=metadata.get('roles', []), limitations=metadata.get('limitations', []), resolver=resolver)


def read_assembled_manifest(path, method_id, *, resolver=None):
    """Read all candidate episodes through the same semantic admission boundary.

    Returns ``(document, assembled_episodes, sha256)``. Each episode carries its
    parsed tuple and scored result. The caller must use ``episode.result`` so
    implementation/source/coverage diagnostics are retained in the report.
    """
    import hashlib
    import json
    from pathlib import Path
    try:
        raw = Path(path).read_bytes()
        document = json.loads(raw, parse_float=Decimal)
    except (OSError,json.JSONDecodeError) as exc:
        raise SchemaError(str(exc)) from exc
    if document.get('formula_version') != FORMULA_VERSION:
        raise SchemaError('episode formula_version mismatch')
    index = {o['object_id']:o for o in document.get('objects',[])}
    assertions = {a['assertion_id']:a for a in document.get('assertions',[])}
    evidence = {e['evidence_id']:e for e in document.get('evidence',[])}
    if len(index) != len(document.get('objects',[])) or len(assertions) != len(document.get('assertions',[])) or len(evidence) != len(document.get('evidence',[])):
        raise SchemaError('duplicate manifest observation identity')
    working=deepcopy(document)
    missing_implementations=set()
    for obj in working.get('objects',[]):
        if obj.get('state')=='computed' and (obj['recipe_id'] not in NATIVE_PRODUCERS and obj['recipe_id'] not in DERIVED_PRODUCERS or obj['recipe_id'] not in OUTPUT_SCHEMAS):
            missing_implementations.add(obj['object_id'])
            obj.update(state='hole',value={},known_at=None,recipe_base_ok=None,recipe_coverage_ok=None)
            obj['hole_ids']=list(dict.fromkeys(obj.get('hole_ids',[])+[f"HOLE:{obj['recipe_id']}:missing_implementation"]))
    for candidate in working.get('candidates',[]):
        for field,binding in candidate.get('operands',{}).items():
            if 'value_field' in binding:
                if binding['value_field']!=field: raise SchemaError('arbitrary operand alias')
                del binding['value_field']
    parsed=parse_manifest(working,method_id,resolver=resolver)
    seen,episodes,visiting=set(),{},set()
    sources={c['candidate_id']:c for c in working.get('candidates',[])}
    def admit(cid):
        if cid in seen:return
        if cid in visiting:raise SchemaError('cyclic candidate source dependency')
        visiting.add(cid)
        source=sources[cid]
        for key in ('parent_attempt_id','parent_entry_id','current_state_candidate_id','next_state_candidate_id'):
            dep=source.get(key)
            if dep in sources:admit(dep)
        candidate=deepcopy(source)
        metadata=document.get('assembly',{})
        roles=candidate.get('semantic_roles',document.get('semantic_roles',metadata.get('roles',[])))
        roles=[r for r in roles if r.get('candidate_id',cid)==cid]
        limitations=candidate.get('limitations',document.get('limitations',metadata.get('limitations',[])))
        limitations=[r for r in limitations if r.get('candidate_id',cid)==cid]
        bindings=candidate.pop('bindings',None)
        episode=assemble_episode(candidate,working['objects'],working['assertions'],working['evidence'],
            bindings=bindings,roles=roles,limitations=limitations,resolver=resolver,
            _parsed_context=parsed,_implementation_objects=missing_implementations)
        # Replay uses the full document so entry/state counterpart identities
        # remain available. The public reader is the full-manifest replay API.
        episode.manifest=deepcopy(document)
        episodes[cid]=episode
        seen.add(cid);visiting.remove(cid)
    for cid in sources:admit(cid)
    episodes=[episodes[cid] for cid in sources]
    return document,episodes,hashlib.sha256(raw).hexdigest()
