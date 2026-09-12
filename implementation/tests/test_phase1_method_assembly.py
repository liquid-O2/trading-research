"""Typed method assembly, source roles and honest implementation limitations."""
from copy import deepcopy
from datetime import date
from decimal import Decimal
import json

import pytest

from trading_research.research.method_pack.assembly import (
    assemble_episode, operand_inventory, producer_coverage_matrix, replay_assembled,
)
from trading_research.research.method_pack.catalog import METHOD_BY_ID
from trading_research.research.method_pack.contracts import fields_for, OUTPUT_SCHEMAS, OutputField
from trading_research.research.method_pack.evidence import SchemaError, fixture_document
from trading_research.research.method_pack.methods import m01_judas_reversal_fixture
from trading_research.research.method_pack.method_slices.m03 import _positive_case
from trading_research.research.method_pack.native_resolution import NativeResolver, file_digest
from trading_research.research.method_pack.objects.native_boundary import NATIVE_PRODUCERS, _interval_coverage
from trading_research.research.method_pack.protocol import RecipeResult
from trading_research.research.method_pack.clocks import et_ns


def _assemble_doc(document, **kwargs):
    candidate = deepcopy(document['candidates'][0])
    candidate['operands'] = {f: {k: v for k, v in b.items() if k != 'value_field'} for f, b in candidate['operands'].items()}
    return assemble_episode(candidate, document['objects'], document['assertions'], document['evidence'], **kwargs)


def _m01():
    row = m01_judas_reversal_fixture()
    for evidence in row['evidence_records']:
        evidence['payload']['observation'] = {'printed_inputs': deepcopy(evidence['payload']), 'source': 'FORMULAS M01-F1'}
    return {'candidates': [row['candidate']], 'objects': row['objects'], 'assertions': row['assertions'], 'evidence': row['evidence_records']}


def test_all_twelve_method_contracts_have_every_operand_and_alternative():
    rows = operand_inventory()
    assert {r.method_id for r in rows} == set(METHOD_BY_ID)
    for method in METHOD_BY_ID:
        actual = {r.field: r for r in rows if r.method_id == method}
        assert actual.keys() == fields_for(method).keys()
        for field, contract in fields_for(method).items():
            assert actual[field].producers == contract.recipes
            assert actual[field].units == contract.type
            assert actual[field].rule == contract.rule
            assert actual[field].branches
    assert len(rows) == sum(len(fields_for(m)) for m in METHOD_BY_ID)
    matrix = producer_coverage_matrix()
    assert len(matrix) == len(rows)
    assert all(r['native_status'] in {'implemented', 'parent_derived', 'source_only', 'supplied_record', 'missing_native_implementation', 'no_native_producer', 'no_declared_producer'} for r in matrix)


def test_complete_source_fixture_assembles_and_replays_without_using_outcome():
    document = _m01()
    first = _assemble_doc(document)
    assert first.result['verdict'] == 'pass'
    assert first.result['observation_unit'] == 'sequence'
    document['candidates'][0]['later_outcome'] = {'result': 'loss', 'reason': 'observed stop after valid entry'}
    second = _assemble_doc(document)
    assert second.result['verdict'] == 'pass'
    replayed = replay_assembled(first.manifest)
    assert replayed.result['verdict'] == 'pass'


def test_copied_boolean_and_arbitrary_alias_rejected():
    document = _m01()
    for row in document['evidence']:
        row['payload'] = {k: v for k, v in row['payload'].items() if isinstance(v, bool)}
    with pytest.raises(SchemaError, match='observation'):
        _assemble_doc(document)
    document = _m01()
    candidate = document['candidates'][0]
    field = next(iter(candidate['operands']))
    candidate['operands'][field]['value_field'] = 'favorable_other_field'
    with pytest.raises(SchemaError, match='alias or literal'):
        assemble_episode(candidate, document['objects'], document['assertions'], document['evidence'])


def test_absent_native_implementation_is_not_relabelled_source_definition():
    document = _m01()
    candidate = document['candidates'][0]
    # Use an actually selected numeric producer, retaining the missing code
    # rather than publishing the caller's high-confidence scalar summary.
    binding = candidate['operands']['range_known_at']
    oid = binding['object_id']
    obj = next(o for o in document['objects'] if o['object_id'] == oid)
    obj['state'] = 'computed'
    obj['inputs'] = {'known_at': obj['known_at'], 'W': 999}
    obj['raw_member_locators'] = [{'fake': 'cannot provide native implementation'}]
    # This checks the missing adapter diagnostic, independently of locator
    # validation (which happens once a producer exists).
    rid = obj['recipe_id']
    original = NATIVE_PRODUCERS.pop(rid, None)
    try:
        result = _assemble_doc(document)
    finally:
        if original is not None:
            NATIVE_PRODUCERS[rid] = original
    assert result.result['verdict'] == 'unknown'
    assert result.result['software_complete'] is False
    assert any(h['field'] == 'range_known_at' and h['kind'] == 'missing_implementation' for h in result.holes)
    assert result.parsed[1][oid]['value'] == {}


def test_documented_source_hole_is_separate_from_absent_record():
    document = _m01()
    candidate = document['candidates'][0]
    candidate['operands'].pop('source_confirmation')
    limitation = {'field': 'source_confirmation', 'kind': 'source_definition',
                  'reason': 'This selected source case does not disclose a confirmation detector',
                  'source_ref': 'FORMULAS O056',
                  'source_setting': {'status': 'unknown', 'value': None, 'source_refs': ['FORMULAS O056'],
                                     'reason': 'Detector definition not disclosed in this synthetic case'}}
    result = _assemble_doc(document, limitations=[limitation])
    assert result.result['verdict'] == 'unknown'
    assert any(h['field'] == 'source_confirmation' and h['kind'] == 'source_definition' for h in result.holes)
    assert all(row['applicability'] == 'not_selected' for row in result.bindings if row['field'] == 'source_zone_known')


def _role(obj, role, candidate):
    return {'object_id': obj['object_id'], 'role': role, 'method_id': candidate['method_id'],
            'instrument_id': candidate['instrument_id'], 'author': obj['author'],
            'source_definition': {'status': 'fact', 'source_refs': ['FORMULAS M03-F1'],
                'reason': 'The synthetic source declares this exact dated formation',
                'value': {'role': role, 'formation_start': obj['formation_start'], 'formation_end': obj['formation_end'],
                          'session_date_et': candidate['session_date_et']}}}


@pytest.fixture
def native_m03(tmp_path, monkeypatch):
    op = _positive_case()
    document = fixture_document('GB-VWAP', 'sequence', 'native-assembly', op)
    candidate = document['candidates'][0]
    # A test source declares actual short windows; the native adapter resolves
    # real immutable rows, never the summaries in the object input record.
    start = et_ns(date(2026, 1, 15), 7, 58)
    minute = 60_000_000_000
    dataset = 'quantpad/cme__nq-continuous-futures__ohlcv-1m'
    path = tmp_path / dataset / 'case.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps([{'t': (start+i*minute)//1_000_000, 'o': 99, 'h': 100, 'l': 98, 'c': 99,
                                'v': 10, 'instrument_id': op['instrument_id']} for i in range(2)]))
    loc = {'source_file': str(path), 'dataset_id': dataset, 'sha256': file_digest(path), 'row_start': 0, 'row_end': 2}
    resolver = NativeResolver(tmp_path, owned_spans=[{'path': str(path), 'start_ns': start, 'end_ns': start+2*minute}])
    def range_producer(config, resolved):
        rows = resolved.rows()
        coverage, gaps = _interval_coverage(rows, resolved.start_ns, resolved.end_ns)
        return RecipeResult('O046', 'computed', {'box_high': max(r['H'] for r in rows), 'box_low': min(r['L'] for r in rows)},
                            known_at=resolved.known_at, coverage_ok=coverage)
    monkeypatch.setitem(NATIVE_PRODUCERS, 'O046', range_producer)
    monkeypatch.setitem(OUTPUT_SCHEMAS, 'O046', {'box_high': OutputField((Decimal,)), 'box_low': OutputField((Decimal,))})
    # Merge the Asia high and its availability into the same actual producer.
    asia = next(o for o in document['objects'] if o['object_id'].endswith(':asia_high'))
    asia.update({'state': 'computed', 'inputs': {'H': 999, 'use_at': op['decision_at']}, 'raw_member_locators': [loc],
                 'formation_start': start, 'formation_end': start+2*minute, 'known_at': start+2*minute,
                 'as_of': start+2*minute, 'value': {}})
    candidate['operands']['asia_known_at'] = {'object_id': asia['object_id']}
    # The remaining source observations are genuinely attributed fixture
    # observations, each with its explicit source role and evidence payload.
    roles = [_role(asia, 'asia', candidate)]
    groups = {'london': ['london_high','london_known_at'], 'breakout_candle': ['breakout_close','breakout_at'],
              'vwap_at_retest': ['vwap_at_retest','vwap_known_at']}
    for role, fields in groups.items():
        primary = next(o for o in document['objects'] if o['object_id'].endswith(':'+fields[0]))
        for field in fields:
            origin = next(o for o in document['objects'] if o['object_id'].endswith(':'+field))
            primary['value'].update(origin['value'])
            primary['units'].update(origin['units'])
            primary['evidence_ids'] = list(dict.fromkeys(primary['evidence_ids']+origin['evidence_ids']))
            candidate['operands'][field] = {'object_id': primary['object_id']}
        roles.append(_role(primary, role, candidate))
    return document, resolver, roles, asia


def test_actual_native_reference_uses_dated_role_not_caller_high(native_m03):
    doc, resolver, roles, asia = native_m03
    assembled = _assemble_doc(doc, resolver=resolver, roles=roles)
    assert assembled.result['verdict'] == 'pass'
    output = assembled.parsed[1][asia['object_id']]
    assert output['value']['asia_high'] == Decimal(100)
    assert output['value']['asia_known_at'] == output['known_at']
    assert output['semantic_derivations'][0]['role'] == 'asia'
    assert replay_assembled(assembled.manifest, resolver=resolver).result['verdict'] == 'pass'


def test_equal_prices_do_not_erase_reference_identity(native_m03):
    doc, resolver, roles, asia = native_m03
    same = deepcopy(roles)
    next(r for r in same if r['role'] == 'london')['object_id'] = asia['object_id']
    with pytest.raises(SchemaError, match='reuse one producer identity'):
        _assemble_doc(doc, resolver=resolver, roles=same)


def test_wrong_dated_role_and_foreign_author_rejected(native_m03):
    doc, resolver, roles, _ = native_m03
    wrong = deepcopy(roles)
    wrong[0]['source_definition']['value']['formation_start'] += 1
    with pytest.raises(SchemaError, match='formation window'):
        _assemble_doc(doc, resolver=resolver, roles=wrong)
    wrong = deepcopy(roles)
    wrong[0]['author'] = 'another author'
    with pytest.raises(SchemaError, match="another author's"):
        _assemble_doc(doc, resolver=resolver, roles=wrong)


def _catalog_citation(tmp_path,monkeypatch,key='GB'):
    from trading_research.research.method_pack import semantic_views
    import hashlib
    path=tmp_path/'source-inputs.txt';path.write_text('Synthetic source fixture with its complete attributed observation inputs.')
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setattr(semantic_views,'load_catalog',lambda:{'sources':{key:{'path':str(path),'sha256':digest}}})
    return {'source_key':key,'source_file':str(path),'sha256':digest,'quote':path.read_text()}


def test_source_audit_reruns_actual_vwap_observations_and_rejects_copied_result(tmp_path,monkeypatch):
    from trading_research.research.method_pack.assembly import _audit_source_operand
    candidate = {'method_id': 'GB-VWAP', 'instrument_id': 7, 'evidence_mode': 'source_illustration'}
    record = {'recipe_id': 'O030', 'instrument_id': 7, 'author': 'GB',
              'known_at': 20, 'value': {'vwap_at_retest': Decimal(105)}, 'evidence_ids': ['source']}
    inputs = {'reset_at': 10, 'reset_id': 'r', 'reset_verified': True, 'as_of': 20,
              'instrument_id': 7, 'canonical_tape_id': 'test', 'basis': 'trade_price',
              'coverage_complete': True, 'trades': [
                  {'event_id': 'a', 't': 10, 'price': 100, 'size': 1},
                  {'event_id': 'b', 't': 20, 'price': 110, 'size': 1}]}
    evidence = {'source': {'source_ref': 'actual-source', 'source_version': '1',
                          'payload': {'recipe_id': 'O030', 'recipe_inputs': inputs,'source_citation':_catalog_citation(tmp_path,monkeypatch)}}}
    _audit_source_operand('vwap_at_retest', record, evidence, candidate)
    assert record['source_audits']['vwap_at_retest'][0]['known_at'] == 20
    record['value']['vwap_at_retest'] = Decimal(999)
    with pytest.raises(SchemaError, match='differs from cited recipe rerun'):
        _audit_source_operand('vwap_at_retest', record, evidence, candidate)
    evidence['source']['payload'] = {'prices': [100, 110], 'vwap_at_retest': 999, 'source_rule_id': 'O030'}
    with pytest.raises(SchemaError, match='actual cited recipe_inputs'):
        _audit_source_operand('vwap_at_retest', record, evidence, candidate)


def test_source_audit_full_schema_and_availability_are_required(tmp_path,monkeypatch):
    from trading_research.research.method_pack.assembly import _audit_source_operand
    from trading_research.research.method_pack.protocol import RECIPES
    from trading_research.research.method_pack.contracts import OutputContractError
    candidate = {'method_id': 'GB-VWAP', 'instrument_id': 7, 'evidence_mode': 'source_illustration'}
    record = {'recipe_id': 'O030', 'instrument_id': 7, 'known_at': 10,
              'value': {'vwap_at_retest': Decimal(105)}, 'evidence_ids': ['s']}
    evidence = {'s': {'payload': {'recipe_id': 'O030', 'recipe_inputs': {'prices': [100, 110]},'source_citation':_catalog_citation(tmp_path,monkeypatch)}}}
    monkeypatch.setitem(RECIPES, 'O030', lambda _: RecipeResult('O030', 'supplied', {'vwap': Decimal(105)}, known_at=20))
    with pytest.raises(OutputContractError, match='missing required output'):
        _audit_source_operand('vwap_at_retest', record, evidence, candidate)
    monkeypatch.setitem(OUTPUT_SCHEMAS, 'O030', {'vwap': OutputField((Decimal,))})
    with pytest.raises(SchemaError, match='backdates'):
        _audit_source_operand('vwap_at_retest', record, evidence, candidate)


def _source_interpretation(tmp_path, monkeypatch, field='source_confirmation'):
    from trading_research.research.method_pack.semantic_views import ROLES
    import hashlib
    method = 'JJ-TBR'
    text = 'Synthetic test source: the named rejection at the selected band was confirmed before entry.'
    source = tmp_path / 'attributed-source.txt'
    source.write_text(text)
    citation = {'source_key': 'TBR', 'source_file': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'quote': text}
    from trading_research.research.method_pack import semantic_views
    monkeypatch.setattr(semantic_views,'load_catalog',lambda: {'sources':{'TBR':{'path':str(source),'sha256':citation['sha256']}}})
    candidate = {'method_id': method, 'instrument_id': 7, 'session_date_et': '2026-01-15',
                 'branch': 'judas_reversal', 'decision_at': 30, 'evidence_mode': 'source_illustration'}
    rid = fields_for(method)[field].recipes[0]
    row = {'method_id': method, 'recipe_id': rid, 'field': field, 'author': method,
           'instrument_id': 7, 'session_date_et': candidate['session_date_et'],
           'branch': candidate['branch'], 'semantic_role': ROLES[method,field], 'known_at': 20,
           'citation': citation, 'reason': 'Synthetic attributed confirmation at the named location.',
           'criterion': {'status': 'fact', 'value': {'field': field, 'rule': fields_for(method)[field].rule},
                         'source_refs': ['synthetic source'], 'reason': 'The source names this criterion.'},
           'observed_value': {'status': 'fact', 'value': True, 'source_refs': ['synthetic source'],
                              'reason': 'Explicit affirmative source interpretation.'},
           'observations': [{'observation_id': 'rejection-1', 'known_at': 20,
                             'description': 'The source records the named rejection at the selected band.',
                             'citation': citation}]}
    record = {'recipe_id': rid, 'author': method, 'known_at': 20, 'value': {field: True}, 'evidence_ids': ['s']}
    return candidate, record, {'s': {'payload': {'source_interpretation': row}}}, source


def test_actual_cited_interpretation_is_supplied_and_has_immutable_observation(tmp_path,monkeypatch):
    from trading_research.research.method_pack.assembly import _audit_source_operand
    candidate,record,evidence,source = _source_interpretation(tmp_path,monkeypatch)
    _audit_source_operand('source_confirmation', record, evidence, candidate)
    assert record['evidence_class'] == 'supplied_source_interpretation'
    assert record['source_audits']['source_confirmation']['observation_ids'] == ['rejection-1']
    source.write_text('changed after attribution')
    with pytest.raises(SchemaError,match='hash differs'):
        _audit_source_operand('source_confirmation',record,evidence,candidate)


def test_source_interpretation_cannot_transfer_field_role_author_or_future(tmp_path,monkeypatch):
    from trading_research.research.method_pack.assembly import _audit_source_operand
    candidate,record,evidence,_ = _source_interpretation(tmp_path,monkeypatch)
    for key, bad in [('field','risk_defined'),('author','another'),('semantic_role','structural_risk')]:
        changed = deepcopy(evidence)
        changed['s']['payload']['source_interpretation'][key] = bad
        with pytest.raises(SchemaError,match='foreign|frozen method author'):
            _audit_source_operand('source_confirmation',record,changed,candidate)
    changed = deepcopy(evidence)
    changed['s']['payload']['source_interpretation']['observations'][0]['known_at'] = 21
    with pytest.raises(SchemaError,match='later observation'):
        _audit_source_operand('source_confirmation',record,changed,candidate)
    changed = deepcopy(evidence)
    changed['s']['payload']['source_interpretation']['observations'] = []
    with pytest.raises(SchemaError,match='supporting observations'):
        _audit_source_operand('source_confirmation',record,changed,candidate)


def test_unknown_source_definition_stays_unknown(tmp_path,monkeypatch):
    from trading_research.research.method_pack.assembly import _audit_source_operand
    candidate,record,evidence,_ = _source_interpretation(tmp_path,monkeypatch)
    evidence['s']['payload']['source_interpretation']['criterion'].update(status='unknown', value=None)
    _audit_source_operand('source_confirmation',record,evidence,candidate)
    assert record['value']['source_confirmation'] is None
    assert record['recipe_coverage_ok'] is None


def test_closed_domain_views_preserve_unknowns_and_risk_units():
    from trading_research.research.method_pack.semantic_views import project, projection
    candidate = {'decision_at': 30}
    risk = projection('SIRES','risk_defined','O139')
    assert project(risk, {'stop_side_ok': True, 'risk_known_before_entry': None}, {}, candidate) is None
    assert project(risk, {'stop_side_ok': False, 'risk_known_before_entry': True}, {}, candidate) is False
    reward = projection('STOIC-RISK','planned_reward_r','O155')
    assert project(reward, {'planned_risk_units': Decimal(4), 'planned_reward_units': Decimal(12)}, {}, candidate) == Decimal(3)
    clock = projection('SIRES','replenish_at','O123')
    assert project(clock, {'stage_ledger': {'replenishment': 12}}, {}, candidate) == 12
    assert project(clock, {'stage_ledger': {}}, {}, candidate) is None


def test_every_operand_has_explicit_role_and_audited_source_route():
    from trading_research.research.method_pack.semantic_views import ROLES
    matrix = producer_coverage_matrix()
    assert len(ROLES) == len(matrix) == 373
    for row in matrix:
        assert row['semantic_role'] == ROLES[row['method_id'],row['field']]
        from trading_research.research.method_pack.semantic_views import source_interpretation_supported
        if source_interpretation_supported(row['method_id'],row['field']):
            assert row['binding_status'] == 'implemented'
            assert all('supplied_source_interpretation' in p['routes'] for p in row['producer_status'])
    # A source audit route never claims that its quantitative native adapter exists.
    source_only = next(row for row in matrix if row['field'] == 'source_confirmation')
    assert source_only['native_status'] == 'source_only'


def test_manifest_reader_uses_assembly_and_retains_diagnostics(tmp_path):
    from trading_research.research.method_pack.assembly import read_assembled_manifest
    from trading_research.research.method_pack import FORMULA_VERSION
    from trading_research.research.method_pack.protocol import jsonable
    doc = _m01()
    doc['formula_version'] = FORMULA_VERSION
    path = tmp_path / 'episodes.json'
    path.write_text(json.dumps(jsonable(doc)))
    original,episodes,digest = read_assembled_manifest(path,'JJ-TBR')
    assert len(episodes) == 1 and len(digest) == 64
    assert episodes[0].result['verdict'] == 'pass'
    assert 'assembly_holes' in episodes[0].result
    original['candidates'][0]['operands']['range_known_at']['value_field'] = 'different_field'
    path.write_text(json.dumps(original))
    with pytest.raises(SchemaError,match='alias'):
        read_assembled_manifest(path,'JJ-TBR')


def test_state_and_conditioning_views_do_not_use_later_availability():
    from trading_research.research.method_pack.semantic_views import projection,project
    candidate={'decision_at':100}
    assert project(projection('JETBUNDLE-STATES','state_at','O165'),{'state_at':10},{'known_at':12},candidate)==10
    conditioning=projection('JETBUNDLE-STATES','conditioning_known_at','O166')
    assert project(conditioning,{'conditioning_evidence':[{'known_at':8},{'known_at':9}]},{'known_at':50},candidate)==9
    assert project(conditioning,{'conditioning_evidence':[{'known_at':None}]},{'known_at':50},candidate) is None
    # An event timestamp does not supply the source's aggression interpretation.
    assert projection('SIRES','aggression_confirms','O132') is None


def test_dated_role_cannot_self_certify_unpublished_asia_clock(native_m03):
    from trading_research.research.method_pack.assembly import _role_definition
    doc,resolver,roles,asia=native_m03
    candidate=deepcopy(doc['candidates'][0]);candidate['evidence_mode']='source_illustration'
    with pytest.raises(SchemaError,match='frozen catalog configuration'):
        _role_definition(roles[0],asia,candidate)
    role=deepcopy(roles[0])
    role.update(source_configuration_id='gb-vwap-continuation',source_configuration_version='2.0.0',
                source_setting_key='asia_london_windows')
    assert _role_definition(role,asia,candidate) is None
    assert asia['_role_status']['asia']=='unknown'


def test_direct_scoring_cannot_trust_serialized_source_audit_marker():
    from trading_research.research.method_pack.evidence import parse_manifest,score_episode
    from trading_research.research.method_pack import FORMULA_VERSION
    doc=_m01();doc['formula_version']=FORMULA_VERSION
    for rows in ('candidates','assertions','evidence'):
        for row in doc[rows]:row['evidence_mode']='supplied_contemporaneous'
    for row in doc['objects']+doc['assertions']:
        row['_source_admission']={'source_confirmation':True}
        row['evidence_class']='supplied_source_audit'
    parsed=parse_manifest(doc,'JJ-TBR')
    with pytest.raises(SchemaError,match='actual source assembly audit'):
        score_episode(next(iter(parsed[0].values())),*parsed[1:])


def test_control_selection_artifact_binds_exact_case_role_and_window(native_m03, tmp_path):
    from trading_research.research.method_pack.assembly import _role_definition
    doc, _, roles, asia = native_m03
    candidate = deepcopy(doc['candidates'][0])
    candidate.update(evidence_mode='native_control', variant='comparison', source_case_id='control-case')
    role = deepcopy(roles[0])
    role.update(source_configuration_id='gb-vwap-continuation', source_configuration_version='2.0.0')
    selected = {key: asia[key] for key in ('object_id','instrument_id','formation_start','formation_end')}
    selected.update(source_case_id=candidate['source_case_id'],role='asia')
    path = tmp_path/'selection.json'
    path.write_text(json.dumps(selected))
    role['control_artifact'] = {'path':str(path),'sha256':file_digest(path)}
    assert _role_definition(role,asia,candidate)['formation_start']==asia['formation_start']
    assert asia['source_role_comparison'] is True
    role['source_definition']['value']['role']='london'
    with pytest.raises(SchemaError,match='date/role identity'):
        _role_definition(role,asia,candidate)
    role['source_definition']['value']['role']='asia'
    path.write_text('{}')
    with pytest.raises(SchemaError,match='immutable selection artifact'):
        _role_definition(role,asia,candidate)


@pytest.mark.parametrize('session_day',['2026-03-08','2026-11-01'])
def test_control_asia_midnight_clock_uses_prior_et_date(native_m03, monkeypatch, session_day):
    from datetime import timedelta
    from trading_research.research.method_pack.assembly import _role_definition
    from trading_research.research.method_pack import source_config
    doc, _, roles, asia = native_m03
    candidate = deepcopy(doc['candidates'][0])
    candidate.update(evidence_mode='native_control',variant='comparison',session_date_et=session_day)
    day=date.fromisoformat(session_day)
    asia.update(formation_start=et_ns(day-timedelta(days=1),20,0),formation_end=et_ns(day,0,0),known_at=et_ns(day,0,0))
    role=deepcopy(roles[0])
    role.update(source_configuration_id='gb-vwap-continuation',source_configuration_version='2.0.0',source_setting_key='asia_london_windows')
    role['source_definition']['value'].update(session_date_et=session_day,formation_start=asia['formation_start'],formation_end=asia['formation_end'])
    catalog=deepcopy(source_config.load_catalog())
    setting=catalog['configurations']['gb-vwap-continuation']['settings']['asia_london_windows']
    setting.update(status='inference',value={'asia':['20:00','00:00','America/New_York']})
    monkeypatch.setattr(source_config,'load_catalog',lambda:catalog)
    assert _role_definition(role,asia,candidate)['formation_start']==asia['formation_start']


def test_control_role_consumes_actual_frozen_catalog_window(native_m03):
    from trading_research.research.method_pack.assembly import _role_definition
    doc, _, roles, asia=native_m03
    candidate=deepcopy(doc['candidates'][0])
    candidate.update(evidence_mode='native_control',variant='comparison',source_case_id='GB-VWAP-2026-02-24',session_date_et='2026-02-24')
    asia.update(formation_start=et_ns(date(2026,2,23),20,0),formation_end=et_ns(date(2026,2,24),0,0),known_at=et_ns(date(2026,2,24),0,0))
    role=deepcopy(roles[0])
    role.update(source_configuration_id='gb-vwap-continuation',source_configuration_version='2.0.0',control_window_id='GB-VWAP-2026-02-24:asia',control_window_version='2.0.0')
    role['source_definition']['value'].update(session_date_et='2026-02-24',formation_start=asia['formation_start'],formation_end=asia['formation_end'])
    assert _role_definition(role,asia,candidate)['formation_end']==asia['formation_end']
    role['control_window_version']='invented'
    with pytest.raises(SchemaError,match='frozen catalog'):
        _role_definition(role,asia,candidate)


def test_method_contacts_require_exact_geometry_lineage_and_availability():
    from trading_research.research.method_pack.objects.range_geometry import o007,o015,o052
    contact={'reference_lineage_id':'range-1','reference_band':[Decimal('105'),Decimal('105')],
             'price_overlap':True,'contact_at':20,'known_at':21}
    inputs={'L':100,'H':110,'parent_id':'range-1','known_at':10,'contact_observation':contact}
    result=o007(inputs)
    assert result.value['selected_contact'] is True and result.known_at==21
    assert o007({k:v for k,v in inputs.items() if k!='contact_observation'}).value['selected_contact'] is None
    for changed in ({'reference_lineage_id':'foreign'},{'reference_band':[104,104]},{'contact_at':9}):
        assert o007({**inputs,'contact_observation':{**contact,**changed}}).state=='invalid'
    extension={**contact,'reference_band':[Decimal('123.30'),Decimal('126.60')]}
    assert o015({**inputs,'coordinate_convention_verified':True,'contact_observation':extension}).value['selected_contact'] is True
    pocket={**contact,'reference_band':[Decimal('105'),Decimal('106.18')]}
    assert o052({**inputs,'impulse_id':'range-1','impulse_side':'down','contact_observation':pocket}).value['selected_contact_at']==20


def test_failure_view_retains_complete_clock_close_and_postconfirmation_retest():
    from trading_research.research.method_pack.objects.range_geometry import o047
    minute=60_000_000_000
    inputs={'reference_px':100,'reference_known_at':0,'side':'high','confirmation_type':'five_minute_close',
            'confirmation_bar':{'start':0,'end':5*minute,'known_at':5*minute,'complete':True,'C':99},
            'events':[{'t':minute,'price':102},{'t':6*minute,'price':100},{'t':7*minute,'price':105}],
            'box_other_edge':95,'return_inside_box':True,'decision_at':8*minute,'coverage_ok':True}
    result=o047(inputs)
    assert result.value['sweep_high']==102  # Later excursion cannot redefine the failed sweep.
    assert result.value['sweep_low'] is None
    assert result.value['confirm_close']==99 and result.value['complete_clock_five_minute_bar'] is True
    assert result.value['box_return_ok'] is True and result.value['retest_at']==6*minute
    result=o047({**inputs,'confirmation_bar':{**inputs['confirmation_bar'],'start':minute}})
    assert result.value['complete_clock_five_minute_bar'] is False


def test_method_risk_and_buy_imbalance_views_preserve_direction_and_unknowns():
    from trading_research.research.method_pack.semantic_views import projection,project
    stop=projection('MEMBER-TWO-REASONS','stop_above_rejection_high','O139')
    value={'planned_stop':103,'planned_stop_side':'short','stop_side_ok':True,'risk_known_before_entry':True,
           'invalidation_ref':{'object_id':'rejection-1','field':'H','value':102}}
    assert project(stop,value,{}, {'side':'short'}) is True
    assert project(stop,{**value,'planned_stop':102},{},{'side':'short'}) is False
    assert project(stop,{**value,'invalidation_ref':None},{},{'side':'short'}) is None
    buy=projection('KEANI-OPEN-ABOVE-VALUE','aggressive_buy_imbalance_break','O109')
    known=projection('KEANI-OPEN-ABOVE-VALUE','imbalance_band_known_at','O109')
    footprint={'ratio_min':3,'row_count':2,'buy_comparisons':[{'qualifies':False}],
               'buy_runs':[],'sell_runs':[{'band':[100,101]}]}
    assert project(buy,footprint,{'known_at':20},{}) is False
    assert project(known,footprint,{'known_at':20},{}) is None
    assert project(buy,{**footprint,'ratio_min':None},{},{}) is None
    footprint.update(buy_comparisons=[{'qualifies':True}],buy_runs=[{'band':[100,101]}])
    assert project(buy,footprint,{'known_at':20},{}) is True
    assert project(known,footprint,{'known_at':20},{})==20
