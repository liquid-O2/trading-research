from copy import deepcopy
from datetime import date
from decimal import Decimal as D

import pytest

from trading_research.research.method_pack.adapters import normalize_trade_row
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.contracts import validate_output
from trading_research.research.method_pack.evidence import mark_source_admitted
from trading_research.research.method_pack.native_resolution import NativeEvidenceError, NativeInstrumentDefinition, ResolvedMembers
from trading_research.research.method_pack.objects import profile_integration as a
from trading_research.research.method_pack.objects.native_boundary import run_native_object
from trading_research.research.method_pack.objects.context_observations import native_vwap, derived_vwap_band

START=et_ns(date(2026,6,12),9,30)
END=START+60_000_000_000
DATASET='quantpad/cme__nq-continuous-futures__trades'


def resolved(start=START,end=END,offset=0):
    rows=[normalize_trade_row(dict(t=start+1,price='100',size=7,side='B',instrument_id=7),dataset_id=DATASET,source_file='fixture.csv',source_row=offset),
          normalize_trade_row(dict(t=start+2,price='100.25',size=3,side='A',instrument_id=7),dataset_id=DATASET,source_file='fixture.csv',source_row=offset+1)]
    native=NativeInstrumentDefinition('definition-v1',7,D('.25'),START-100,'definition.json','a'*64,0,'NQ','NQM6')
    return ResolvedMembers(tuple(rows),7,start,end,start+2,True,(),instrument_definition=native)


def config(identifier='prior',start=START,end=END,kind='prior_rth'):
    return dict(as_of=end,profile_definition=dict(profile_id=identifier,selection_known_at=start,source_id='explicit-test-configuration',
      window=dict(window_id='window:'+identifier,kind=kind,session_date='2026-06-12',start=start,end=end),
      value_area=dict(config_id='sires-40',fraction='.40',algorithm=None,tie_policy=None)))


def envelope(identifier='prior',start=START,end=END,offset=0):
    result=a._native('O061',config(identifier,start,end),resolved(start,end,offset))
    validate_output(result)
    return dict(object_id=identifier,recipe_id='O061',state=result.state,value=result.value,known_at=result.known_at,
      formation_start=start,formation_end=end,evidence_class='resolved_native',instrument_id=7,
      recipe_base_ok=result.base_ok,recipe_coverage_ok=result.coverage_ok,hole_ids=result.hole_ids)


def parent(identifier, recipe, value, known_at, *, evidence_class='parent_derived'):
    return dict(object_id=identifier, recipe_id=recipe, state='computed', value=value,
                known_at=known_at, evidence_class=evidence_class, instrument_id=7,
                recipe_base_ok=True, recipe_coverage_ok=True, hole_ids=[],
                evidence_ids=[f'evidence:{identifier}'])


def source_parent(identifier, value, known_at):
    result = parent(identifier, 'O022', value, known_at,
                    evidence_class='supplied_source_audit')
    result['state'] = 'supplied'
    for field in value:
        mark_source_admitted(result, field)
    return result


def run_derived(recipe_id, inputs, parents):
    known_at = max(item['known_at'] for item in parents)
    obj = {'recipe_id': recipe_id, 'instrument_id': 7,
           'parent_ids': [item['object_id'] for item in parents],
           'inputs': inputs, 'formation_start': 1, 'formation_end': known_at,
           'as_of': known_at, 'known_at': known_at}
    return run_native_object(obj, None, parents=parents)


def test_serialized_profile_native_tick_rows_and_schema():
    inp=config();inp['levels']=[{'price':999,'size':999}]
    result=a._native('O061',inp,resolved())
    validate_output(result)
    assert result.value['tick_size']==D('.25')
    assert result.value['total_volume']==10
    assert result.value['poc']==100 and result.value['val'] is None
    snapshot=a.snapshot_from_payload(result.value)
    assert snapshot.rows[0].buy_volume==7 and snapshot.rows[1].sell_volume==3
    assert snapshot.known_at==END
    inp['profile_definition']['instrument']={'instrument_id':7,'tick_size':'.5'}
    with pytest.raises(NativeEvidenceError,match='tick'):a._native('O061',inp,resolved())


def test_profile_unknown_coverage_retains_observed_rows_and_clock():
    from dataclasses import replace
    result=a._native('O061',config(),replace(resolved(),coverage_ok=None))
    validate_output(result)
    assert result.coverage_ok is None and result.value['total_volume']==10
    assert a.snapshot_from_payload(result.value).total_volume==10


def test_derived_poc_requires_selected_profile_identity():
    first=envelope();second=envelope('second')
    with pytest.raises(NativeEvidenceError,match='exactly one'):a.derived_profile('O064',{},[first,second])
    result=a.derived_profile('O064',{'profile_parent_id':'prior'},[first,second])
    validate_output(result)
    assert result.value['poc']==100 and result.value['profile_id']=='prior'
    changed=deepcopy(first);changed['value']['rows'][0]['total_volume']=D(8)
    with pytest.raises(NativeEvidenceError,match='reconcile'):a.derived_profile('O064',{},[changed])


def test_composite_uses_actual_disjoint_constituents_and_preserves_child_identity():
    first=envelope();second=envelope('second',END,END+60_000_000_000,2)
    result=a.derived_profile('O070',dict(constituent_ids=['prior','second'],composite_id='both',selection_known_at=END+60_000_000_001,rationale='explicit adjacent constituents'),[first,second])
    validate_output(result)
    assert result.value['total_volume']==20
    assert result.parent_ids==['prior','second']
    child={**first,'object_id':'both','recipe_id':'O070','value':result.value,'evidence_class':'parent_derived','known_at':result.known_at}
    assert a.derived_profile('O064',dict(profile_parent_id='both'),[child]).value['poc']==100


def test_reference_visits_use_trusted_parent_and_actual_postformation_members():
    parent=envelope();later=resolved(END,END+60_000_000_000,2)
    result=a.native_reference_visits(dict(parents={'prior':parent},reference_parent_id='prior',as_of=later.end_ns),later)
    validate_output(result)
    assert result.value['untested_at_decision'] is False
    assert result.value['first_qualifying_visit']['event_id']==later.members[0]['event_id']


def test_derived_ledge_joins_actual_lineage_and_not_equal_price():
    ledge = parent('ledge-object', 'O068', {
        'edge_id': 'ledge:A', 'ledge_band': [D('102'), D('102')],
        'shelf_volume': D('40'), 'transition_volume': D('5')}, 10)
    retest = parent('retest-object', 'O002', {
        'reference_lineage_id': 'ledge:A', 'contact_at': 20,
        'contact_price': D('102'), 'price_overlap': True}, 20,
        evidence_class='resolved_native')
    result = a.derived_profile('O069', {
        'ledge_parent_id': 'ledge-object', 'retest_parent_id': 'retest-object',
        'use_at': 21, 'ledge_px': 999, 'retest_px': 999}, [ledge, retest])
    validate_output(result)
    assert result.value['same_ledge_retest'] is True
    assert result.value['ledge_id'] == result.value['retest_ledge_id'] == 'ledge:A'
    assert result.value['neighbor_volumes'] == {'shelf': D('40'), 'transition': D('5')}
    assert result.parent_ids == ['ledge-object', 'retest-object']

    other = deepcopy(retest)
    other['object_id'] = 'same-price-other-lineage'
    other['value']['reference_lineage_id'] = 'ledge:B'
    mismatch = a.derived_profile('O069', {
        'ledge_parent_id': 'ledge-object',
        'retest_parent_id': 'same-price-other-lineage', 'use_at': 21}, [ledge, other])
    assert mismatch.value['same_price'] is True
    assert mismatch.value['same_id'] is False
    assert mismatch.value['same_ledge_retest'] is False


def test_derived_ledge_rejects_a_future_retest_parent():
    ledge = parent('ledge', 'O068', {'edge_id': 'ledge:A', 'ledge_band': [102, 102]}, 10)
    future = parent('future', 'O002', {'reference_lineage_id': 'ledge:A',
        'contact_at': 22, 'contact_price': 102, 'price_overlap': True}, 22,
        evidence_class='resolved_native')
    with pytest.raises(NativeEvidenceError, match='after use'):
        a.derived_profile('O069', {'ledge_parent_id': 'ledge',
            'retest_parent_id': 'future', 'use_at': 21}, [ledge, future])


def test_derived_dealing_range_uses_measured_band_control_and_audited_selection():
    band = parent('band', 'O060', {'band_id': 'range:A', 'balance_band': [100, 105]}, 10)
    control = parent('control', 'O064', {'price': 100}, 11)
    selection = source_parent('selection', {'rationale': 'selected source auction',
        'thesis_side': 'long', 'scale': 'session', 'band_parent_id': 'band',
        'control_parent_id': 'control', 'band_id': 'range:A'}, 12)
    result = a.derived_profile('O071', {'band_parent_id': 'band',
        'control_parent_id': 'control', 'selection_parent_id': 'selection',
        'use_at': 20, 'lo': 900, 'hi': 999, 'controlling_reference': 999},
        [band, control, selection])
    validate_output(result)
    assert result.value['dealing_band'] == [D('100'), D('105')]
    assert result.value['width'] == 5 and result.value['controlling_reference'] == 100
    assert result.value['rationale'] == 'selected source auction'
    assert result.value['thesis_side'] == 'long'
    assert result.value['parent_ids'] == ['band', 'control', 'selection']
    assert result.known_at == 12

    comparison = a.derived_profile('O071', {'band_parent_id': 'band',
        'control_parent_id': 'control', 'variant': 'comparison', 'use_at': 20},
        [band, control])
    assert comparison.value['dealing_band'] == [D('100'), D('105')]
    assert comparison.value['rationale'] is None
    assert comparison.value['thesis_side'] is None
    assert comparison.value['band_known_before_use'] is None
    assert 'HOLE:O071:source_selection' in comparison.hole_ids


def test_derived_dealing_range_rejects_unadmitted_or_wrong_parent_selection():
    band = parent('band', 'O060', {'band_id': 'range:A', 'balance_band': [100, 105]}, 10)
    control = parent('control', 'O064', {'price': 100}, 11)
    unadmitted = parent('selection', 'O022', {'rationale': 'later chosen',
        'thesis_side': 'long', 'band_parent_id': 'band',
        'control_parent_id': 'control'}, 12, evidence_class='supplied_source_audit')
    unadmitted['state'] = 'supplied'
    with pytest.raises(NativeEvidenceError, match='not admitted'):
        a.derived_profile('O071', {'band_parent_id': 'band',
            'control_parent_id': 'control', 'selection_parent_id': 'selection',
            'use_at': 20}, [band, control, unadmitted])

    wrong = source_parent('wrong', {'rationale': 'wrong graph', 'thesis_side': 'long',
        'band_parent_id': 'another-band', 'control_parent_id': 'control'}, 12)
    with pytest.raises(NativeEvidenceError, match='different band/control'):
        a.derived_profile('O071', {'band_parent_id': 'band',
            'control_parent_id': 'control', 'selection_parent_id': 'wrong',
            'use_at': 20}, [band, control, wrong])


def test_prior_defense_requires_actual_same_band_history_contact_and_fresh_control():
    band = parent('band', 'O071', {'band_id': 'range:A', 'band': [100, 101]}, 5)
    prior = source_parent('prior-defense', {'band_id': 'range:A',
        'defended': True, 'defended_at': 6}, 8)
    contact = parent('contact', 'O002', {'reference_lineage_id': 'range:A',
        'contact_at': 20, 'contact_price': 100, 'price_overlap': True}, 20,
        evidence_class='resolved_native')
    control = parent('fresh-control', 'O057', {'reference_lineage_id': 'range:A',
        'confirmation_at': 22, 'confirmed': True}, 22)
    result = a.derived_profile('O072', {'band_parent_id': 'band',
        'prior_defense_parent_id': 'prior-defense', 'contact_parent_id': 'contact',
        'control_parent_id': 'fresh-control', 'use_at': 23,
        'lo': 900, 'hi': 999, 'history_ids': ['invented']},
        [band, prior, contact, control])
    validate_output(result)
    assert result.value['band'] == [D('100'), D('101')]
    assert result.value['prior_defense_known'] is True
    assert result.value['same_band_contact'] is True
    assert result.value['current_defense'] is True
    assert result.value['history_ids'] == ['prior-defense']
    assert result.parent_ids == ['band', 'prior-defense', 'contact', 'fresh-control']

    other = deepcopy(contact)
    other['object_id'] = 'equal-price-other-band'
    other['value']['reference_lineage_id'] = 'range:B'
    mismatch = a.derived_profile('O072', {'band_parent_id': 'band',
        'prior_defense_parent_id': 'prior-defense',
        'contact_parent_id': 'equal-price-other-band',
        'control_parent_id': 'fresh-control', 'use_at': 23},
        [band, prior, other, control])
    assert mismatch.value['same_band_contact'] is False
    assert mismatch.value['current_defense'] is False


def test_prior_defense_rejects_reused_or_future_control():
    band = parent('band', 'O071', {'band_id': 'range:A', 'band': [100, 101]}, 5)
    prior = source_parent('prior', {'band_id': 'range:A', 'defended': True,
                                    'defended_at': 6}, 8)
    contact = parent('contact', 'O002', {'reference_lineage_id': 'range:A',
        'contact_at': 20, 'contact_price': 100, 'price_overlap': True}, 20,
        evidence_class='resolved_native')
    reused = parent('reused', 'O057', {'reference_lineage_id': 'range:A',
        'confirmation_at': 19, 'confirmed': True}, 19)
    with pytest.raises(NativeEvidenceError, match='precedes'):
        a.derived_profile('O072', {'band_parent_id': 'band',
            'prior_defense_parent_id': 'prior', 'contact_parent_id': 'contact',
            'control_parent_id': 'reused', 'use_at': 25}, [band, prior, contact, reused])
    future = deepcopy(reused)
    future['object_id'] = 'future'
    future['known_at'] = 30
    future['value']['confirmation_at'] = 30
    with pytest.raises(NativeEvidenceError, match='after use'):
        a.derived_profile('O072', {'band_parent_id': 'band',
            'prior_defense_parent_id': 'prior', 'contact_parent_id': 'contact',
            'control_parent_id': 'future', 'use_at': 25}, [band, prior, contact, future])


def test_new_profile_routes_execute_through_parent_derived_boundary():
    ledge = parent('ledge', 'O068', {'edge_id': 'ledge:A', 'ledge_band': [102, 102]}, 10)
    retest = parent('retest', 'O002', {'reference_lineage_id': 'ledge:A',
        'contact_at': 20, 'contact_price': 102, 'price_overlap': True}, 20,
        evidence_class='resolved_native')
    ledge_result = run_derived('O069', {'ledge_parent_id': 'ledge',
        'retest_parent_id': 'retest', 'use_at': 20}, [ledge, retest])
    assert ledge_result.evidence_class == 'parent_derived'
    assert ledge_result.value['same_ledge_retest'] is True

    band = parent('band', 'O060', {'band_id': 'range:A', 'balance_band': [100, 105]}, 10)
    control = parent('control', 'O064', {'price': 100}, 11)
    selection = source_parent('selection', {'rationale': 'source range',
        'thesis_side': 'long', 'band_parent_id': 'band',
        'control_parent_id': 'control', 'band_id': 'range:A'}, 12)
    range_result = run_derived('O071', {'band_parent_id': 'band',
        'control_parent_id': 'control', 'selection_parent_id': 'selection',
        'use_at': 20}, [band, control, selection])
    assert range_result.value['width'] == 5
    assert range_result.known_at == 12

    defense_band = parent('defense-band', 'O071',
                          {'band_id': 'range:A', 'band': [100, 101]}, 5)
    prior = source_parent('prior', {'band_id': 'range:A', 'defended': True,
                                    'defended_at': 6}, 8)
    contact = parent('contact', 'O002', {'reference_lineage_id': 'range:A',
        'contact_at': 20, 'contact_price': 100, 'price_overlap': True}, 20,
        evidence_class='resolved_native')
    fresh = parent('fresh', 'O057', {'reference_lineage_id': 'range:A',
        'confirmation_at': 22, 'confirmed': True}, 22)
    defense_result = run_derived('O072', {'band_parent_id': 'defense-band',
        'prior_defense_parent_id': 'prior', 'contact_parent_id': 'contact',
        'control_parent_id': 'fresh', 'use_at': 22}, [defense_band, prior, contact, fresh])
    assert defense_result.value['prior_defense_known'] is True
    assert defense_result.value['current_defense'] is True
    assert defense_result.parent_ids == ['defense-band', 'prior', 'contact', 'fresh']


def test_vwap_dispersion_uses_identical_parent_weights_and_ignores_supplied_sigma():
    result=native_vwap(dict(reset_id='session',reset_at=START,reset_verified=True,basis='trade_price',as_of=END),resolved())
    parent=dict(object_id='vwap',recipe_id='O030',value=result.value,known_at=result.known_at,recipe_coverage_ok=True,evidence_class='resolved_native')
    derived=derived_vwap_band(dict(vwap_parent_id='vwap',band_id='band',k=2,variance_convention='volume_weighted_population',variant='comparison',sigma=999),[parent])
    validate_output(derived)
    mu=D('100.075');sigma=(D('.013125')).sqrt()
    assert derived.value['upper']==mu+2*sigma
    assert derived.known_at==END
    hole=derived_vwap_band(dict(vwap_parent_id='vwap',band_id='source-band',k=2,variance_convention='volume_weighted_population'),[parent])
    assert hole.value['upper'] is None and hole.state=='hole'
