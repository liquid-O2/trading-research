"""Lifecycle counterexamples through source admission and actual parent adapters.

All source citations resolve the existing immutable REF artifact. Observations
are synthetic regression records; neither producers nor admission are mocked.
"""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path

import pytest

from trading_research.research.method_pack import objects  # noqa: F401
from trading_research.research.method_pack.assembly import assemble_episode
from trading_research.research.method_pack.contracts import validate_output
from trading_research.research.method_pack.evidence import (
    SchemaError, audit_source_domain_object, source_admitted,
)
from trading_research.research.method_pack.objects.native_boundary import run_native_object
from trading_research.research.method_pack.protocol import run_recipe
from trading_research.research.method_pack.semantic_views import AUTHORS
from trading_research.research.method_pack.source_config import load_catalog

METHOD = 'REFILL-STUDY'
AUTHOR = sorted(AUTHORS[METHOD])[0]
PROBES = Path(__file__).parents[1] / 'validation/phase1-post-implementation-check/lifecycle-probes.json'


def probe(name):
    return deepcopy(next(row['inputs'] for row in json.loads(PROBES.read_text())['results']
                         if row['probe'] == name))


def citation():
    source = load_catalog()['sources']['REF']
    return dict(source_key='REF', source_file=source['path'], sha256=source['sha256'],
                page=7, image_id='REF:7:page')


def supplied(recipe_id, inputs, *, object_id='source', known_at=30, **overrides):
    record = dict(object_id=object_id, recipe_id=recipe_id, method_id=METHOD,
                  author=AUTHOR, instrument_id='NQ', known_at=known_at,
                  value={}, evidence_ids=[object_id + '-evidence'], state='supplied',
                  parent_ids=[], hole_ids=[])
    record.update(overrides)
    # Carry the actual observation, including for recipes whose typed input
    # spelling is not one of the generic source-observation keys.
    payload_inputs = deepcopy(inputs)
    payload_inputs.setdefault('observation', deepcopy(inputs))
    evidence = {record['evidence_ids'][0]: {'payload': dict(recipe_id=recipe_id,
                recipe_inputs=payload_inputs, source_citation=citation())}}
    return record, evidence


def audited_parent(recipe_id, inputs, object_id):
    result = validate_output(run_recipe(recipe_id, deepcopy(inputs)))
    record, evidence = supplied(recipe_id, inputs, object_id=object_id, known_at=result.known_at)
    audit_source_domain_object(record, evidence)
    return record


@pytest.mark.parametrize('name', ['foreign_order_fill', 'future_fill_backdated', 'transition_backdated'])
def test_independent_invalid_inputs_fail_actual_source_admission(name):
    rid = 'O166' if name.startswith('transition') else 'O150'
    record, evidence = supplied(rid, probe(name))
    with pytest.raises(SchemaError, match='invalid supplied'):
        audit_source_domain_object(record, evidence)
    assert not source_admitted(record, 'lifecycle_valid' if rid == 'O150' else 'transition_valid')


@pytest.mark.parametrize('name,rid,field', [('order_control', 'O150', 'lifecycle_valid'),
                                           ('transition_control', 'O166', 'transition_valid')])
def test_independent_valid_controls_pass_full_source_rerun(name, rid, field):
    record, evidence = supplied(rid, probe(name))
    result = audit_source_domain_object(record, evidence)
    assert result.state == 'computed'
    assert result.value[field] is True
    assert source_admitted(record, field)


def test_missing_transition_labels_remain_unknown_in_source_output():
    record, evidence = supplied('O166', probe('transition_missing_labels'))
    result = audit_source_domain_object(record, evidence)
    assert result.state == 'hole'
    assert result.value['transition_valid'] is None
    assert result.base_ok is not True
    assert any('state' in hole for hole in result.hole_ids)


@pytest.mark.parametrize('label', ['', 'Z', 1, ['A']])
def test_invalid_transition_label_cannot_enter_source_audit(label):
    inputs = probe('transition_control')
    inputs['next_observation']['state_label'] = label
    record, evidence = supplied('O166', inputs)
    with pytest.raises(SchemaError):
        audit_source_domain_object(record, evidence)


@pytest.mark.parametrize('kind,extra', [('fill', {'qty': 1}), ('exit_fill', {'qty': 1}),
                                      ('cancel', {}), ('amend', {'new_quantity': 4})])
@pytest.mark.parametrize('key,value', [('order_id', 'order-B'), ('position_id', 'position-B'),
                                      ('instrument_id', 'ES')])
def test_each_foreign_event_link_is_rejected_by_source_rerun(kind, extra, key, value):
    inputs = probe('order_control')
    event = {**inputs['events'][0], 'event_id': 'foreign', 'kind': kind, 'at': 20,
             'known_at': 20, **extra, key: value}
    inputs['events'].append(event)
    record, evidence = supplied('O150', inputs)
    with pytest.raises(SchemaError, match='invalid supplied'):
        audit_source_domain_object(record, evidence)


def test_source_snapshot_keeps_future_tail_pending_and_rejects_conflicting_snapshot():
    inputs = probe('order_control')
    inputs['events'][0].update(at=20, known_at=20)
    inputs.pop('use_at')
    record, evidence = supplied('O150', inputs, as_of=15)
    result = audit_source_domain_object(record, evidence)
    assert result.base_ok is True
    assert result.value['filled_quantity'] == 0
    assert result.value['position_quantity'] == 0
    assert result.known_at <= 15
    inputs['as_of'] = 30
    record, evidence = supplied('O150', inputs, as_of=15)
    with pytest.raises(SchemaError, match='as_of mismatch'):
        audit_source_domain_object(record, evidence)


def test_explicit_unknown_fill_clock_does_not_become_admitted_quantity():
    inputs = probe('order_control')
    inputs['events'][0]['known_at'] = None
    record, evidence = supplied('O150', inputs)
    # Full dependency admission requires known availability; it cannot certify
    # a claimed fill by falling back from the explicit unknown to occurrence.
    with pytest.raises(SchemaError, match='backdates'):
        audit_source_domain_object(record, evidence)


def assembly_order(inputs, *, as_of=30):
    record, evidence = supplied('O150', inputs, as_of=as_of,
        branch_scope=['supplied_selected_order'], source_ref='REF:7', source_version='v1',
        formation_start=10, formation_end=11, units={'stop_ticks': 'decimal_ticks?'},
        value={'stop_ticks': Decimal(32)})
    ev = next(iter(evidence.values()))
    ev['payload']['observation'] = deepcopy(inputs)
    ev.update(evidence_id=record['evidence_ids'][0], method_id=METHOD,
        branch='supplied_selected_order', instrument_id='NQ', band_id=None, side='long',
        source_ref='REF:7', source_version='v1', description='Synthetic cited lifecycle regression',
        observation_start=10, observation_end=11, known_at=30,
        evidence_mode='supplied_contemporaneous')
    candidate = dict(candidate_id='candidate-A', method_id=METHOD,
        branch='supplied_selected_order', predicate='selected_order_configuration', side='long',
        instrument_id='NQ', session_date_et='1970-01-01', decision_at=30, band_ids=[],
        cohort_id='regression', evidence_mode='supplied_contemporaneous',
        operands={'stop_ticks': {'object_id': record['object_id']}})
    return assemble_episode(candidate, [record], evidence=[ev])


def test_full_assembly_cannot_project_valid_policy_from_foreign_order_events():
    control = assembly_order(probe('order_control'))
    record = control.parsed[1]['source']
    assert record['value']['stop_ticks'] == 32
    assert source_admitted(record, 'stop_ticks')
    assert control.result['verdict'] != 'pass'  # Other entry evidence is absent.
    for name in ('foreign_order_fill', 'future_fill_backdated'):
        with pytest.raises(SchemaError, match='invalid'):
            assembly_order(probe(name))


def test_full_assembly_uses_same_outer_snapshot_contract():
    inputs = probe('order_control')
    inputs['as_of'] = 30
    with pytest.raises(SchemaError, match='as_of mismatch'):
        assembly_order(inputs, as_of=15)


def order_parents(*, fill_order='order-A', fill_clock=15, fill_at=15, action_changes=None):
    definition = audited_parent('O137', dict(definition={'rule': 'fixed'},
        model_version='v1', frozen_at=1), 'definition')
    ledger = audited_parent('O148', dict(process_version='v1', frozen_at=1,
        inclusion_rule={'rule_id': 'all'}, candidates=[dict(candidate_id='candidate-A',
        selected=True, known_at=2)]), 'ledger')
    fill = audited_parent('O151', dict(order_id=fill_order, side='buy', limit=100, active_at=10,
        fill_convention='touch_or_through', queue_evidence=True, source_policy={'policy_id': 'fixed'},
        trades=[dict(event_id='trade', price=100, at=fill_at, known_at=fill_clock)],
        fill_report=dict(fill_id='fill-A', order_id=fill_order, position_id='position-A',
        instrument_id='NQ', at=fill_at, known_at=fill_clock, filled_qty=1)), 'fill')
    action_row = dict(event_id='amend', kind='amend', at=20, known_at=20,
        order_id='order-A', position_id='position-A', instrument_id='NQ', new_quantity=3)
    action_row.update(action_changes or {})
    action = audited_parent('O142', dict(entry_id='order-A', entry_at=fill_at, position=1,
        initial_risk=8, source_policy={'allowed_actions': ['amend', 'cancel', 'exit_fill']},
        policy_frozen_at=1, management_actions=[action_row]), 'action')
    return [definition, ledger, fill, action]


def derived_order(parents, *, as_of=30, **order_changes):
    source_order = probe('order_control')
    source_order.pop('events')
    source_order.pop('use_at')
    source_order.update(order_changes)
    obj = dict(object_id='derived-order', recipe_id='O150', instrument_id='NQ',
        method_id=METHOD, parent_ids=[p['object_id'] for p in parents], as_of=as_of,
        inputs=dict(source_order=source_order, source_policy=source_order['source_policy'],
        parent_roles={'definition': 'definition', 'instruction_ledger': 'ledger',
                      'fills': ['fill'], 'position_actions': ['action']}))
    return run_native_object(obj, None, parents=parents)


def test_real_audited_parent_outputs_reach_actual_native_order_adapter():
    result = derived_order(order_parents())
    assert result.state == 'computed', result.reason
    assert result.base_ok is True
    assert result.value['filled_quantity'] == 1
    assert result.value['position_quantity'] == 1
    assert result.evidence_class == 'parent_derived'
    assert result.parent_ids == ['definition', 'ledger', 'fill', 'action']


def test_native_order_adapter_rejects_real_foreign_fill_parent():
    result = derived_order(order_parents(fill_order='order-B'))
    assert result.state == 'invalid'
    assert result.base_ok is False
    assert result.value.get('filled_quantity') in (None, 0)


def test_native_order_adapter_preserves_management_identity():
    result = derived_order(order_parents(action_changes={'order_id': 'order-B'}))
    assert result.state == 'invalid'
    assert result.base_ok is False


def test_native_order_adapter_honors_outer_snapshot_without_counting_future_fill():
    result = derived_order(order_parents(), as_of=14)
    assert result.value['filled_quantity'] == 0
    assert result.value['position_quantity'] == 0
    assert result.state != 'invalid'


def state_parent(object_id, label, at):
    names = {'D': ['aggression', 'efficient_displacement'],
             'A': ['high_aggression', 'low_response_efficiency',
                   'opposite_liquidity_holds_and_refills']}[label]
    return audited_parent('O165', dict(state_label=label, state_at=at,
        instrument_id='NQ', observation_id=object_id, required_depth_levels=1, depth_levels=1,
        criteria=[dict(criterion=name, observed=True, known_at=at) for name in names],
        evidence=[dict(evidence_id=object_id + '-observation', known_at=at)]), object_id)


def transition_parents():
    return [state_parent('current', 'D', 10), state_parent('next', 'A', 20),
            audited_parent('O111', dict(interval_s=1, n_prints=1, contracts=1,
                source_panel_value=1, known_at=9), 'conditioning')]


def derived_transition(parents, *, as_of=30, use_at=None):
    inputs = dict(parent_roles={'current_state': 'current', 'next_state': 'next',
                               'conditioning': ['conditioning']},
                  current_sequence=1, next_sequence=2, cohort_id='cohort', reset_id='session',
                  cadence='adjacent-state-observations')
    if use_at is not None:
        inputs['use_at'] = use_at
    obj = dict(object_id='transition', recipe_id='O166', method_id=METHOD,
        instrument_id='NQ', as_of=as_of, parent_ids=[p['object_id'] for p in parents], inputs=inputs)
    return run_native_object(obj, None, parents=parents)


def test_real_state_records_pass_actual_parent_transition_adapter():
    result = derived_transition(transition_parents())
    assert result.state == 'computed', result.reason
    assert result.value['transition_valid'] is True
    assert result.value['from_state'] == 'D'
    assert result.value['to_state'] == 'A'
    assert result.known_at == 20


def test_real_future_state_parent_cannot_certify_transition_at_earlier_snapshot():
    result = derived_transition(transition_parents(), as_of=15)
    assert result.state == 'hole'
    assert result.value['transition_valid'] is None


def test_real_state_parent_available_after_use_is_rejected_by_native_boundary():
    result = derived_transition(transition_parents(), use_at=15)
    assert result.state == 'invalid'
    assert result.base_ok is False
    assert 'HOLE:O166:dependency_after_use' in result.hole_ids


def test_source_snapshot_after_use_is_rejected_without_rewriting_inputs():
    inputs = probe('order_control')
    inputs['use_at'] = 15
    inputs['events'][0].update(at=20, known_at=20)
    record, evidence = supplied('O150', inputs, as_of=30)
    with pytest.raises(SchemaError, match='invalid supplied'):
        audit_source_domain_object(record, evidence)
    assert evidence['source-evidence']['payload']['recipe_inputs']['use_at'] == 15
    assert evidence['source-evidence']['payload']['recipe_inputs']['events'][0]['at'] == 20


def test_source_transition_cannot_transfer_two_matching_foreign_states():
    inputs = probe('transition_control')
    for key in ('current_observation', 'next_observation'):
        inputs[key]['instrument_id'] = 'ES'
    record, evidence = supplied('O166', inputs)
    with pytest.raises(SchemaError, match='invalid supplied'):
        audit_source_domain_object(record, evidence)


def test_source_snapshot_remains_earliest_when_use_deadline_is_later():
    inputs = probe('order_control')
    inputs['events'][0].update(at=20, known_at=20)
    record, evidence = supplied('O150', inputs, as_of=15)
    result = audit_source_domain_object(record, evidence)
    assert result.value['filled_quantity'] == 0
    pending = result.value['pending_events']
    fill = next(row for row in pending if row.get('event_id') == 'fill-A')
    assert fill['at'] == 20
    assert fill['known_at'] == 20


def test_source_explicit_unknown_snapshot_is_not_rewritten_to_outer_claim():
    inputs = probe('order_control')
    inputs['as_of'] = None
    record, evidence = supplied('O150', inputs, as_of=15)
    with pytest.raises(SchemaError, match='as_of mismatch'):
        audit_source_domain_object(record, evidence)
    assert evidence['source-evidence']['payload']['recipe_inputs']['as_of'] is None


def test_explicit_linked_reopen_is_admitted_and_preserves_new_order_generation():
    inputs = probe('order_control')
    identity = dict(order_id='order-A', position_id='position-A', instrument_id='NQ')
    inputs['events'] = [dict(event_id='cancel', kind='cancel', at=12, known_at=12, **identity),
        dict(event_id='reopen', kind='reopen', at=13, known_at=13, **identity,
             prior_order_id='order-A', new_order_id='order-B', new_quantity=2),
        dict(event_id='new-fill', kind='fill', at=15, known_at=15, qty=1,
             order_id='order-B', position_id='position-A', instrument_id='NQ')]
    record, evidence = supplied('O150', inputs)
    result = audit_source_domain_object(record, evidence)
    assert result.state == 'computed'
    assert result.value['filled_quantity'] == 1
    assert result.value['position_quantity'] == 1
    assert result.value['remaining_quantity'] == 1


@pytest.mark.parametrize('snapshot', [None, 30])
def test_native_order_adapter_rejects_contradictory_source_order_snapshot(snapshot):
    parents = order_parents()
    source_order = probe('order_control')
    source_order.pop('events')
    source_order.pop('use_at')
    source_order['as_of'] = snapshot
    obj = dict(object_id='derived-order', recipe_id='O150', instrument_id='NQ',
        method_id=METHOD, parent_ids=[p['object_id'] for p in parents], as_of=15,
        inputs=dict(source_order=source_order, source_policy=source_order['source_policy'],
        parent_roles={'definition': 'definition', 'instruction_ledger': 'ledger',
                      'fills': ['fill'], 'position_actions': ['action']}))
    result = run_native_object(obj, None, parents=parents)
    assert result.state == 'invalid'
    assert result.base_ok is False
    assert source_order['as_of'] == snapshot


def test_backdated_fill_report_is_rejected_before_becoming_a_derived_parent():
    with pytest.raises(SchemaError, match='invalid supplied'):
        order_parents(fill_at=20, fill_clock=12)


def test_unknown_fill_report_availability_cannot_become_a_known_parent():
    with pytest.raises(SchemaError):
        order_parents(fill_clock=None)


def test_real_parent_post_cancellation_exit_closes_only_filled_position():
    parents = order_parents(action_changes={'kind': 'cancel', 'at': 20, 'known_at': 20})
    # Replace the actual management parent by another full audited output whose
    # own policy authorizes both actions and whose quantities reconcile.
    parents[-1] = audited_parent('O142', dict(entry_id='order-A', entry_at=15, position=1,
        initial_risk=8, source_policy={'allowed_actions': ['cancel', 'exit_fill']},
        policy_frozen_at=1, management_actions=[
            dict(event_id='cancel', kind='cancel', at=20, known_at=20,
                 order_id='order-A', position_id='position-A', instrument_id='NQ'),
            dict(event_id='exit', kind='exit_fill', at=25, known_at=25, filled_qty=1,
                 order_id='order-A', position_id='position-A', instrument_id='NQ')]), 'action')
    result = derived_order(parents)
    assert result.state == 'computed', result.reason
    assert result.value['filled_quantity'] == 1
    assert result.value['remaining_quantity'] == 0
    assert result.value['position_quantity'] == 0
    assert result.value['position_open'] is False


def test_future_transition_source_record_remains_pending_without_certification():
    inputs = probe('transition_control')
    record, evidence = supplied('O166', inputs, as_of=15)
    result = audit_source_domain_object(record, evidence)
    assert result.state == 'hole'
    assert result.value['transition_valid'] is None
    assert result.value['next_observation']['state_at'] == 20
    assert result.value['next_observation']['known_at'] == 20


def test_explicit_unknown_state_availability_cannot_become_source_certification():
    inputs = probe('transition_control')
    inputs['next_observation']['known_at'] = None
    result = validate_output(run_recipe('O166', deepcopy(inputs)))
    assert result.known_at is None
    assert result.value['transition_valid'] is None
    record, evidence = supplied('O166', inputs)
    with pytest.raises(SchemaError, match='backdates'):
        audit_source_domain_object(record, evidence)


def test_native_order_keeps_each_real_partial_fill_clock_with_a_future_report_tail():
    parents = order_parents()
    parents[2] = audited_parent('O151', dict(order_id='order-A', side='buy', limit=100,
        active_at=10, fill_convention='touch_or_through', queue_evidence=True,
        source_policy={'policy_id': 'fixed'},
        trades=[dict(event_id='trade', price=100, at=15, known_at=15)],
        fill_reports=[dict(fill_id='early-fill', order_id='order-A', position_id='position-A',
                           instrument_id='NQ', at=15, known_at=15, filled_qty=1),
                      dict(fill_id='future-fill', order_id='order-A', position_id='position-A',
                           instrument_id='NQ', at=25, known_at=25, filled_qty=1)]), 'fill')
    result = derived_order(parents, as_of=20)
    assert result.state == 'computed', result.reason
    assert result.value['filled_quantity'] == 1
    assert result.value['position_quantity'] == 1
    assert result.value['remaining_quantity'] == 2
    future = next(row for row in result.value['pending_events'] if row.get('fill_id') == 'future-fill')
    assert future['at'] == 25
    assert future['known_at'] == 25


def test_source_event_cannot_claim_internal_policy_status_to_bypass_identity():
    inputs = probe('order_control')
    inputs['events'] = [dict(kind='fill', qty=1, at=15, known_at=15, synthetic_from_policy=True)]
    result = validate_output(run_recipe('O150', deepcopy(inputs)))
    assert result.base_ok is not True
    assert result.value['filled_quantity'] in (None, 0)
    record, evidence = supplied('O150', inputs)
    try:
        audited = audit_source_domain_object(record, evidence)
    except SchemaError:
        return
    assert audited.base_ok is not True
    assert audited.value['lifecycle_valid'] is not True
    assert audited.value['filled_quantity'] in (None, 0)
