"""C01/C02/C03 native provenance and output boundary regression evidence."""
from copy import deepcopy
from datetime import date
from decimal import Decimal
import json

import pytest

from trading_research.research.method_pack.native_resolution import NativeResolver, NativeEvidenceError, file_digest
from trading_research.research.method_pack.objects.native_boundary import run_native_object
from trading_research.research.method_pack.contracts import OutputContractError, validate_output, OUTPUT_SCHEMAS
from trading_research.research.method_pack.protocol import RecipeResult, run_recipe
from trading_research.research.method_pack.clocks import et_ns, time_bar_from_minutes
from trading_research.research.method_pack import objects  # registrations


START = et_ns(date(2026, 1, 15), 10, 0)
MIN = 60_000_000_000


@pytest.fixture
def native(tmp_path):
    dataset = 'quantpad/cme__nq-continuous-futures__ohlcv-1m'
    path = tmp_path / dataset / '2026-01.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps([{'t': (START + i * MIN) // 1_000_000, 'o': 100+i, 'h': 102+i,
                                'l': 99+i, 'c': 101+i, 'v': 10, 'instrument_id': 7}
                               for i in range(2)]))
    loc = {'source_file': str(path), 'dataset_id': dataset, 'sha256': file_digest(path), 'row_start': 0, 'row_end': 2}
    resolver = NativeResolver(tmp_path, owned_spans=[{'path': str(path), 'start_ns': START, 'end_ns': START+2*MIN}])
    obj = {'recipe_id': 'O004', 'instrument_id': 7, 'formation_start': START, 'formation_end': START+2*MIN,
           'as_of': START+2*MIN, 'known_at': START+2*MIN, 'inputs': {'kind': 'time', 'size_minutes': 2, 'use_at': START+2*MIN},
           'raw_member_locators': [loc]}
    return resolver, obj, path


def test_actual_native_result_ignores_supplied_summary_and_retains_members(native):
    resolver, obj, _ = native
    obj['inputs'].update({'O': 999, 'members': [{'O': 999, 'H': 999}], 'known_at': 1})
    result = run_native_object(obj, resolver)
    assert result.value['O'] == Decimal(100)
    assert result.value['C'] == Decimal(102)
    assert result.value['V'] == Decimal(20)
    assert result.value['complete'] is True
    assert len(result.value['member_event_ids']) == 2
    assert result.evidence_class == 'resolved_native'


@pytest.mark.parametrize('mutation', ['nonexistent', 'wrong_digest', 'missing_row', 'wrong_instrument', 'out_of_window', 'unowned', 'string_locator', 'duplicate'])
def test_locator_false_provenance_rejected(native, mutation):
    resolver, obj, path = native
    if mutation == 'nonexistent': obj['raw_member_locators'][0]['source_file'] = str(path)+'missing'
    elif mutation == 'wrong_digest': obj['raw_member_locators'][0]['sha256'] = '0'*64
    elif mutation == 'missing_row': obj['raw_member_locators'][0]['row_end'] = 3
    elif mutation == 'wrong_instrument': obj['instrument_id'] = 8
    elif mutation == 'out_of_window': obj['formation_start'] += MIN
    elif mutation == 'unowned': resolver.owned_spans = []
    elif mutation == 'string_locator': obj['raw_member_locators'] = ['raw://invented/observation']
    elif mutation == 'duplicate': obj['raw_member_locators'] *= 2
    with pytest.raises(NativeEvidenceError): run_native_object(obj, resolver)


def test_P01_exact_interval_coverage_cannot_use_row_count(native):
    resolver, obj, _ = native
    obj['recipe_id'] = 'O001'
    obj['inputs'] = {'required_fields': ['ohlcv']}
    obj['formation_end'] += MIN
    obj['as_of'] += MIN
    obj['known_at'] += MIN
    result = run_native_object(obj, resolver)
    assert result.coverage_ok is None
    assert result.value['missing_intervals'] == [[START+2*MIN, START+3*MIN]]


def test_P02_missing_bar_not_complete(native):
    resolver, obj, _ = native
    obj['raw_member_locators'][0]['row_end'] = 1
    result = run_native_object(obj, resolver)
    assert result.value['complete'] is False
    assert result.coverage_ok is None


def test_P03_absent_clock_verification_is_unknown(native):
    resolver, obj, _ = native
    obj['recipe_id'] = 'O003'
    result = run_native_object(obj, resolver)
    assert result.value['clock_verified'] is None
    assert result.value['clock_check'] is None
    assert result.coverage_ok is None


def test_late_member_and_backdated_object_rejected(native):
    resolver, obj, _ = native
    obj['known_at'] = START+MIN
    result = run_native_object(obj, resolver)
    assert result.base_ok is False
    assert result.known_at == START+2*MIN
    obj['inputs']['use_at'] = START+MIN
    with pytest.raises(NativeEvidenceError, match='after use'): run_native_object(obj, resolver)


def test_exact_bar_alignment_and_identity(native):
    resolver, obj, _ = native
    obj['inputs']['size_minutes'] = 3
    with pytest.raises(NativeEvidenceError, match='clock-aligned'): run_native_object(obj, resolver)


def test_missing_schema_and_domain_state_are_implementation_errors(monkeypatch):
    monkeypatch.delitem(OUTPUT_SCHEMAS, 'O009')
    with pytest.raises(OutputContractError, match='schema not implemented'):
        validate_output(RecipeResult('O009', 'computed', {}))
    with pytest.raises(OutputContractError, match='domain state'):
        validate_output(RecipeResult('O150', 'filled', {}))
    with pytest.raises(OutputContractError, match='missing required output'):
        validate_output(RecipeResult('O004', 'computed', {'O': Decimal(1)}))


def test_clock_builder_uses_latest_availability_and_checks_member_identity():
    row = {'O': 100, 'H': 102, 'L': 99, 'C': 101, 'V': 10, 'start': START, 'end': START+MIN,
           'instrument_id': 7, 'known_at': START+MIN+99}
    result = time_bar_from_minutes(START, START+MIN, {START: row}, instrument_id=7, bar_id='a', size='1m')
    assert result.known_at == START+MIN+99
    with pytest.raises(ValueError, match='instrument'):
        time_bar_from_minutes(START, START+MIN, {START: row}, instrument_id=8, bar_id='a', size='1m')
    row['known_at'] = None
    assert time_bar_from_minutes(START, START+MIN, {START: row}, instrument_id=7, bar_id='a', size='1m').known_at is None


def test_P05_consumed_future_observation_cannot_certify():
    result = run_recipe('O031', {
        'trades': [{'event_id': 'a', 'price': 100, 'size': 1, 't': 10},
                   {'event_id': 'b', 'price': 110, 'size': 1, 't': 20}],
        'anchor_id': 'anchor', 'anchor_price_at': 10, 'anchor_known_at': 10,
        'anchor_selected_at': 10, 'anchor_reason': 'cited low',
        'instrument_id': 7, 'canonical_tape_id': 'test', 'basis': 'trade_price',
        'coverage_complete': True, 'as_of': 20, 'known_at': 10, 'use_at': 15})
    assert result.base_ok is False
    assert result.known_at == 20
    assert result.value['comparison_vwap'] == Decimal(105)


def test_P07_unused_future_open_crossings_do_not_enter_snapshot():
    inp = {'open_px': 100, 'open_at': 10, 'events': [], 'known_at': 10, 'use_at': 15}
    baseline = run_recipe('O050', inp)
    inp['events'] = [{'t': 20, 'price': 99}, {'t': 30, 'price': 101}]
    result = run_recipe('O050', inp)
    assert result.value == baseline.value
    assert result.known_at == baseline.known_at == 10
    assert result.value['cross_below_at'] is None
    assert result.value['cross_above_at'] is None
    assert result.value['source_open_reclaim'] is None


def test_missing_coverage_survives_method_boundary():
    from trading_research.research.method_pack.methods import m01_judas_reversal_fixture
    from trading_research.research.method_pack.evidence import parse_manifest, score_episode
    fixture = m01_judas_reversal_fixture()
    document = {'formula_version': 'method-pack-v1', 'candidates': [fixture['candidate']],
                'objects': fixture['objects'], 'assertions': fixture['assertions'], 'evidence': fixture['evidence_records']}
    parsed = parse_manifest(document, 'JJ-TBR')
    candidate = parsed[0][fixture['candidate_id']]
    baseline = score_episode(candidate, *parsed[1:])
    assert baseline['verdict'] == 'pass'
    for obj in parsed[1].values():
        obj['recipe_coverage_ok'] = None
    result = score_episode(candidate, *parsed[1:])
    assert result['coverage_ok'] is None
    assert result['verdict'] == 'unknown'


def test_O030_earlier_snapshot_invariant_when_unused_future_events_are_appended():
    from trading_research.research.method_pack.objects.m03_recipes import _BASE
    inp = deepcopy(_BASE)
    first = run_recipe('O030', inp)
    inp['trades'].append({'event_id': 'future', 'price': 999, 'size': 10000, 't': 10000})
    second = run_recipe('O030', inp)
    assert second.value == first.value
    assert second.known_at == first.known_at
    assert second.state == first.state
    assert second.base_ok is first.base_ok


def test_instrument_tick_and_availability_come_from_actual_definition_file(native):
    resolver, obj, _ = native
    path = resolver.root / 'derived' / 'continuous-futures__instrument-and-roll-maps' / 'nq-instruments.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps([{'instrument_id': 7, 'root': 'NQ', 'raw_symbol': 'NQH6',
                                 'min_price_increment': '0.25', 'first_definition_ns': START-100}]))
    resolved = resolver.resolve(obj['raw_member_locators'], instrument_id=7, start_ns=START,
                                end_ns=START+2*MIN, use_at=START+2*MIN)
    definition = resolved.instrument_definition
    assert definition.tick_size == Decimal('0.25')
    assert definition.known_at == START-100
    assert definition.available_at == START-100
    assert definition.source_file == str(path)
    assert definition.sha256 == file_digest(path)
    assert definition.raw_symbol == 'NQH6'
    assert definition.definition_id.endswith('@'+definition.sha256)


def test_missing_definition_never_gets_global_tick_default(native):
    resolver, obj, _ = native
    resolved = resolver.resolve(obj['raw_member_locators'], instrument_id=7, start_ns=START, end_ns=START+2*MIN)
    assert resolved.instrument_definition is None


def test_grouped_locators_hash_each_immutable_source_once(native, monkeypatch):
    from trading_research.research.method_pack import native_resolution
    resolver, obj, path = native
    loc = obj['raw_member_locators'][0]
    obj['raw_member_locators'] = [{**loc, 'row_start': 0, 'row_end': 1}, {**loc, 'row_start': 1, 'row_end': 2}]
    calls = []
    original = native_resolution.file_digest
    def counted(path):
        calls.append(path)
        return original(path)
    monkeypatch.setattr(native_resolution, 'file_digest', counted)
    run_native_object(obj, resolver)
    run_native_object(obj, resolver)
    assert calls == [path]
    # A changed file invalidates both cached digest and existing locators.
    path.write_text(path.read_text()+' ')
    with pytest.raises(NativeEvidenceError, match='digest mismatch'):
        run_native_object(obj, resolver)
    assert calls == [path, path]


def test_supplied_parent_cannot_launder_unrelated_prices_as_native_selection(native,monkeypatch):
    from trading_research.research.method_pack.objects.native_boundary import DERIVED_PRODUCERS
    from trading_research.research.method_pack.contracts import OutputField
    resolver,_,_=native
    invoked=[]
    monkeypatch.setitem(DERIVED_PRODUCERS,'O066',lambda config,parents: invoked.append(True))
    monkeypatch.setitem(OUTPUT_SCHEMAS,'O066',{'source_node_known':OutputField((bool,),True)})
    parent={'object_id':'source-node','recipe_id':'O066','state':'supplied','instrument_id':7,
            'known_at':START,'value':{'source_node_known':True},'evidence_ids':['unrelated-price'],
            'evidence_class':'supplied_source_audit','recipe_base_ok':True,'recipe_coverage_ok':True}
    child={'object_id':'child','recipe_id':'O066','state':'computed','instrument_id':7,
           'formation_start':START,'formation_end':START+MIN,'as_of':START+MIN,'known_at':START+MIN,
           'raw_member_locators':[],'parent_ids':['source-node'],'inputs':{'use_at':START+MIN}}
    with pytest.raises(NativeEvidenceError,match='full source audit'):
        run_native_object(child,resolver,parents=[parent])
    assert not invoked


def test_equal_price_boundary_batch_has_exact_ohlcv_without_sequence():
    from trading_research.research.method_pack.native_resolution import ResolvedMembers
    from trading_research.research.method_pack.objects.native_boundary import o004
    from types import MappingProxyType
    rows=[{'event_ns':START+1,'event_id':str(i),'price':Decimal(100),'size':1,
           'action':'T','known_at':START+1} for i in range(2)]
    rows.append({'event_ns':START+MIN-1,'event_id':'close','price':Decimal(101),'size':2,
                 'action':'T','known_at':START+MIN-1})
    resolved=ResolvedMembers(tuple(MappingProxyType(row) for row in rows),7,START,START+MIN,START+MIN-1,True,())
    result=o004({'kind':'time','size_minutes':1},resolved)
    assert result.value['O']==100 and result.value['C']==101
    assert result.value['V']==4 and result.value['complete'] is True
    rows[1]['price']=Decimal(99)
    with pytest.raises(NativeEvidenceError,match='unknown_order'):
        o004({'kind':'time','size_minutes':1},resolved)
