#!/usr/bin/env python3
"""Replay the 27 original counterexamples without changing their inputs.

Each negative check is paired with an identified regression exercising the
complete observations. Rejecting incomplete legacy records alone is not the
evidence for implementation completeness.
"""
from __future__ import annotations

from dataclasses import asdict
from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from typing import Any

from trading_research.research.method_pack import objects  # register domains
from trading_research.research.method_pack.contracts import validate_output
from trading_research.research.method_pack.protocol import jsonable, run_recipe

ROOT=Path(__file__).resolve().parents[2]
ORIGINAL=ROOT/'implementation/reports/phase1-live/methods/charts/full-audit-probes.json'
OUTPUT=ROOT/'implementation/validation/phase1-completion/audit-regressions.json'

PAIRED_O150_IDS = ('P21', 'P22', 'P23', 'P24', 'P25')
O150_IDENTITY_HOLES = {
    'HOLE:O150:order_id',
    'HOLE:O150:candidate_id',
    'HOLE:O150:position_id',
    'HOLE:O150:instrument_id',
    'HOLE:O150:event_identity',
}
IMPLEMENTATION_SOURCES = (
    'implementation/src/trading_research/research/method_pack/objects/lifecycles.py',
    'implementation/src/trading_research/research/method_pack/objects/native_boundary.py',
    'implementation/src/trading_research/research/method_pack/objects/range_geometry.py',
    'implementation/src/trading_research/research/method_pack/protocol.py',
    'implementation/src/trading_research/research/method_pack/contracts.py',
    'implementation/src/trading_research/research/method_pack/objects/__init__.py',
    'implementation/src/trading_research/research/method_pack/evidence.py',
    'implementation/src/trading_research/research/method_pack/assembly.py',
)

CONTROL_EXPECTATIONS = {
    'P21': {
        'state': 'computed', 'base_ok': True, 'coverage_ok': True,
        'remaining_quantity': '0', 'position_quantity': '1',
        'lifecycle_valid': True,
    },
    'P22': {
        'state': 'computed', 'base_ok': True, 'coverage_ok': True,
        'position_quantity': '0', 'lifecycle_valid': True,
    },
    'P23': {
        'state': 'invalid', 'base_ok': False,
        'filled_quantity': '0', 'lifecycle_valid': False,
    },
    'P24': {
        'state': 'computed', 'base_ok': True, 'coverage_ok': True,
        'authorized_quantity': '5', 'filled_quantity': '1',
        'remaining_quantity': '4',
    },
    'P25': {
        'state': 'computed', 'base_ok': True, 'coverage_ok': True,
        'filled_quantity': '0', 'known_at': 10, 'pending_fill': True,
    },
}


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':')).encode('utf-8')


def input_sha256(value: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def source_hashes() -> dict[str, str | None]:
    result = {}
    for relative in IMPLEMENTATION_SOURCES:
        path = ROOT / relative
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return result


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        converted = value if isinstance(value, Decimal) else Decimal(str(value))
    except Exception:
        return None
    return converted if converted.is_finite() else None


def _equals_decimal(value: Any, expected: str | int) -> bool:
    converted = _decimal(value)
    return converted is not None and converted == Decimal(str(expected))


def _thin_o150_expectation(result) -> bool:
    """Thin legacy P21-P25 records stay holes and certify no quantities."""
    value = result.value if isinstance(result.value, dict) else {}
    holes = set(result.hole_ids or [])
    timeline = value.get('order_state_timeline')
    no_applied_timeline = timeline in (None, [])
    if isinstance(timeline, list):
        for row in timeline:
            if not isinstance(row, dict):
                no_applied_timeline = False
                break
            kind = str(row.get('kind', '')).strip().lower().replace('-', '_')
            if kind in {'fill', 'partial_fill'} and (
                row.get('state_after') in {'filled', 'partially_filled'}
                or not _equals_decimal(row.get('position_quantity_after'), 0)
            ):
                no_applied_timeline = False
                break
    return (
        result.state == 'hole'
        and result.base_ok is None
        and result.coverage_ok is None
        and value.get('remaining_quantity') is None
        and value.get('filled_quantity') is None
        and value.get('position_quantity') is None
        and value.get('remaining') is None
        and value.get('filled') is None
        and value.get('authorized_quantity') is None
        and value.get('position_open') is None
        and value.get('lifecycle_valid') is None
        and O150_IDENTITY_HOLES <= holes
        and no_applied_timeline
    )


def identified_o150_control(probe: dict[str, Any]) -> dict[str, Any]:
    """Add identity and event availability to a copy of P21-P25 only."""
    probe_id = probe['id'].lower()
    order_id = f'{probe_id}-order'
    candidate_id = f'{probe_id}-candidate'
    position_id = f'{probe_id}-position'
    instrument_id = 'NQ'
    control = deepcopy(probe['input'])
    control.update({
        'order_id': order_id,
        'candidate_id': candidate_id,
        'position_id': position_id,
        'instrument_id': instrument_id,
        'method_id': 'M09',
        'side': 'long',
        'order_type': 'limit',
        'source_policy': {
            'policy_id': 'audit-supplied',
            'source_id': 'audit-supplied',
            'method_id': 'M09',
        },
    })
    events = []
    for index, source_event in enumerate(control.get('events', []) or []):
        event = deepcopy(source_event)
        event.update({
            'event_id': f'{probe_id}-event-{index}',
            'order_id': order_id,
            'candidate_id': candidate_id,
            'position_id': position_id,
            'instrument_id': instrument_id,
        })
        if 'at' in event:
            event['known_at'] = event['at']
        events.append(event)
    # The legacy record expresses cancellation as a scalar.  Make the
    # control's corresponding event explicit so its identity and known_at are
    # audited without changing any original numeric/timing field.
    cancel_at = control.get('cancel_at')
    if cancel_at is not None and not any(
        str(event.get('kind', '')).strip().lower() in {'cancel', 'canceled'}
        for event in events
    ):
        events.append({
            'event_id': f'{probe_id}-cancel',
            'kind': 'cancel',
            'at': cancel_at,
            'known_at': cancel_at,
            'order_id': order_id,
            'candidate_id': candidate_id,
            'position_id': position_id,
            'instrument_id': instrument_id,
        })
    control['events'] = events
    return control


def control_checks(probe_id: str, result) -> bool:
    value = result.value if isinstance(result.value, dict) else {}
    if probe_id in {'P21', 'P22', 'P24', 'P25'}:
        if result.state != 'computed' or result.base_ok is not True or result.coverage_ok is not True:
            return False
    if probe_id == 'P21':
        return (_equals_decimal(value.get('remaining_quantity'), 0)
                and _equals_decimal(value.get('position_quantity'), 1)
                and value.get('lifecycle_valid') is True)
    if probe_id == 'P22':
        return (_equals_decimal(value.get('position_quantity'), 0)
                and value.get('lifecycle_valid') is True)
    if probe_id == 'P23':
        return (result.state == 'invalid' and result.base_ok is False
                and _equals_decimal(value.get('filled_quantity'), 0)
                and value.get('lifecycle_valid') is False)
    if probe_id == 'P24':
        return (_equals_decimal(value.get('authorized_quantity'), 5)
                and _equals_decimal(value.get('filled_quantity'), 1)
                and _equals_decimal(value.get('remaining_quantity'), 4))
    if probe_id == 'P25':
        pending = value.get('pending_events') or []
        return (
            _equals_decimal(value.get('filled_quantity'), 0)
            and result.known_at == 10
            and any(str(row.get('kind', '')).lower() == 'fill' for row in pending if isinstance(row, dict))
        )
    return False


def replay(recipe_id: str, inputs: dict[str, Any]):
    """Run one registered recipe and independently validate its output schema."""
    try:
        result = run_recipe(recipe_id, deepcopy(inputs))
    except Exception as exc:
        return None, f'{type(exc).__name__}: {exc}'
    try:
        validate_output(result)
    except Exception as exc:
        return result, f'{type(exc).__name__}: {exc}'
    return result, None


def result_record(result, error: str | None = None):
    if result is None:
        return {'execution_error': error}
    return {
        'execution_error': error,
        'schema_validated': error is None,
        'actual': asdict(result),
    }


def checks(probe_id, result):
    v=result.value
    return {
        'P01': lambda: result.coverage_ok is not True and v.get('coverage_ok') is not True,
        'P02': lambda: v.get('complete') is False,
        'P03': lambda: v.get('source_clock_verified') is None and result.state=='hole',
        'P04': lambda: v.get('upper_band') != [Decimal('173.20'),Decimal('186.40')] and result.state=='hole',
        'P05': lambda: result.base_ok is False and v.get('usable') is not True,
        'P06': lambda: result.base_ok is False and v.get('failure_confirmed') is not True,
        'P07': lambda: v.get('cross_below_at') is None and v.get('cross_above_at') is None and result.known_at==10,
        'P08': lambda: result.state=='hole' and v.get('confirmed') is not False,
        'P09': lambda: v.get('volume_average') is None and v.get('source_zone_flag') is not True,
        'P10': lambda: v.get('untested') is None,
        'P11': lambda: result.base_ok is False and v.get('poor_low') is not False,
        'P12': lambda: result.base_ok is False and v.get('break_retest_complete') is not True and v.get('entry_pass') is not True,
        'P13': lambda: v.get('route_ok') is not True and result.state in {'hole','invalid'},
        'P14': lambda: v.get('consumption')==0 and v.get('refresh')==0 and v.get('verified_replenishment') is not True,
        'P15': lambda: v.get('total')==200 and v.get('unknown_volume')==100 and v.get('fraction_interval')==[Decimal('-.2'),Decimal('.8')],
        'P16': lambda: v.get('order_ok') is None,
        'P17': lambda: v.get('reward_gate_ok') is False and v.get('geometry_ok') is False and v.get('stage_evidence_ok') is None,
        'P18': lambda: v.get('qualification') is False and v.get('tape_died_at_failure') is False,
        'P19': lambda: v.get('no_prior_failure') is None and v.get('failure_history_complete') is None and v.get('branch_ok') is None,
        'P20': lambda: v.get('objective_preexists') is None and v.get('preexisting_target') is None,
        'P21': lambda: _thin_o150_expectation(result),
        'P22': lambda: _thin_o150_expectation(result),
        'P23': lambda: _thin_o150_expectation(result),
        'P24': lambda: _thin_o150_expectation(result),
        'P25': lambda: _thin_o150_expectation(result),
        'P26': lambda: v.get('overlay_validation') is None and v.get('validation_before_risk') is None and not v.get('sample_ids'),
        'P27': lambda: v.get('conditioning_causal') is None and v.get('transition_valid') is None and v.get('p_dd')==Decimal('.84'),
    }[probe_id]()


# These are executable full-observation and causal regression tests, not
# assertions that absent input has become a valid positive example.
TESTS={
 'P01':('test_phase1_native_contracts.py','test_P01_exact_interval_coverage_cannot_use_row_count'),
 'P02':('test_phase1_native_contracts.py','test_exact_bar_alignment_and_identity'),
 'P03':('test_phase1_native_contracts.py','test_P03_absent_clock_verification_is_unknown'),
 'P04':('test_phase1_range_geometry.py','test_extensions_bind_the_selected_parent_and_do_not_substitute_outer_width'),
 'P05':('test_phase1_native_contracts.py','test_P05_consumed_future_observation_cannot_certify'),
 'P06':('test_phase1_range_geometry.py','test_sweep_failure_requires_strict_side_and_strict_event_order_in_both_directions'),
 'P07':('test_phase1_range_geometry.py','test_cash_open_path_is_clipped_to_as_of_and_never_backdates_reclaim'),
 'P08':('test_phase1_range_geometry.py','test_orderblock_pattern_is_complete_c2_range_and_has_bearish_mirror'),
 'P09':('test_phase1_range_geometry.py','test_absorption_uses_exactly_fourteen_prior_complete_causal_bars'),
 'P10':('test_phase1_complete_profiles.py','test_missing_coverage_is_unknown_and_cannot_certify_an_untested_reference'),
 'P11':('test_phase1_auction_geometry.py','test_excess_and_poor_extremes_are_side_specific_and_grid_adjacent'),
 'P12':('test_phase1_auction_geometry.py','test_shape_break_retest_requires_causal_order_and_decision_clock'),
 'P13':('test_phase1_auction_geometry.py','test_failed_auction_routes_keep_sires_and_saint_sequences_distinct'),
 'P14':('test_phase1_local_flow.py','test_dom_bbo_change_does_not_invent_execution_depth_or_hidden_reserve'),
 'P15':('test_phase1_local_flow.py','test_unknown_volume_makes_delta_concentration_an_interval_p15'),
 'P16':('test_phase1_local_flow.py','test_liftoff_requires_all_ordered_stages_and_directional_reward_p16'),
 'P17':('test_phase1_flow_sequences.py','test_stop_branch_enforces_two_to_four_reward_zero_to_two_entry_and_daily_gate_p17'),
 'P18':('test_phase1_flow_sequences.py','test_passive_ofm_is_long_only_and_false_dying_tape_cannot_qualify_p18'),
 'P19':('test_phase1_flow_sequences.py','test_clean_squeeze_reads_only_complete_prior_failure_history_p19'),
 'P20':('test_phase1_flow_sequences.py','test_microbalance_target_must_be_preexisting_and_dated_p20'),
 'P21':('test_phase1_complete_lifecycles.py','test_cancel_ends_working_quantity_but_preserves_filled_position_p21'),
 'P22':('test_phase1_complete_lifecycles.py','test_exit_after_entry_order_cancel_closes_only_filled_position_p22'),
 'P23':('test_phase1_complete_lifecycles.py','test_expiry_prohibits_fill_until_explicit_reopen_p23'),
 'P24':('test_phase1_complete_lifecycles.py','test_amended_quantity_and_price_reconcile_and_reject_below_fills_p24'),
 'P25':('test_phase1_complete_lifecycles.py','test_future_fill_is_not_backdated_into_snapshot_p25'),
 'P26':('test_phase1_process_observations.py','test_validation_requires_actual_prior_sample_and_compatible_supplied_result'),
 'P27':('test_phase1_complete_lifecycles.py','test_transition_requires_actual_adjacent_state_records_declared_cadence_and_current_conditioning'),
}


def main():
    original_document = json.loads(ORIGINAL.read_text())
    probes = original_document['probes']
    assert len(probes) == 27 and {x['id'] for x in probes} == set(TESTS)
    rows = []
    original_input_hashes = {}
    control_input_hashes = {}
    for probe in probes:
        probe_id = probe['id']
        filename, test_name = TESTS[probe_id]
        test = ROOT / 'implementation/tests' / filename
        assert 'def ' + test_name + '(' in test.read_text(), test_name

        original_input = deepcopy(probe['input'])
        original_input_hash = input_sha256(original_input)
        original_input_hashes[probe_id] = original_input_hash
        original_result, original_error = replay(probe['object_id'], original_input)
        original_passed = original_result is not None and original_error is None and checks(probe_id, original_result)
        original_evidence = {
            'input': original_input,
            'input_sha256': original_input_hash,
            'input_hash_algorithm': 'sha256(canonical-json; UTF-8; sorted keys; compact separators)',
            'actual': result_record(original_result, original_error),
            'status': 'pass' if original_passed else 'fail',
            'expectation': ('Strict O150 thin-record hole: explicit identity holes, unknown quantities, '
                            'and no applied timeline.') if probe_id in PAIRED_O150_IDS else probe['contract_expectation'],
        }

        control_evidence = None
        control_passed = True
        if probe_id in PAIRED_O150_IDS:
            control_input = identified_o150_control(probe)
            control_input_hash = input_sha256(control_input)
            control_input_hashes[probe_id] = control_input_hash
            control_result, control_error = replay(probe['object_id'], control_input)
            control_passed = control_result is not None and control_error is None and control_checks(probe_id, control_result)
            control_evidence = {
                'input': control_input,
                'input_sha256': control_input_hash,
                'input_hash_algorithm': 'sha256(canonical-json; UTF-8; sorted keys; compact separators)',
                'actual': result_record(control_result, control_error),
                'status': 'pass' if control_passed else 'fail',
                'expected_invariants': CONTROL_EXPECTATIONS[probe_id],
                'construction': (
                    'Copy of the exact original input with explicit '
                    'order/candidate/position/instrument/side/order_type, '
                    'a dict source_policy, and identified event records '
                    'with known_at=at.'
                ),
            }

        passed = original_passed and control_passed
        rows.append(dict(
            id=probe_id,
            object_id=probe['object_id'],
            status='pass' if passed else 'fail',
            original_finding=probe['finding'],
            contract_expectation=probe['contract_expectation'],
            original_input=original_input,
            actual=(asdict(original_result) if original_result is not None else None),
            gap_observed=not original_passed,
            original=original_evidence,
            control=control_evidence,
            paired_probe=probe_id in PAIRED_O150_IDS,
            both_original_and_control_required=probe_id in PAIRED_O150_IDS,
            full_observation_regression=dict(
                path=str(test),
                test=test_name,
                sha256=hashlib.sha256(test.read_bytes()).hexdigest(),
            ),
            scope='Unchanged original helper probe plus linked complete-observation regression; neither is a historical source candidate.',
        ))
    doc = dict(
        # Keep the established top-level schema for existing matrix readers;
        # the paired evidence extension is versioned separately.
        schema='phase1-audit-regressions-v2',
        evidence_schema='phase1-audit-regressions-v3',
        original=dict(
            path=str(ORIGINAL),
            sha256=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
            declared_schema=original_document.get('schema'),
            declared_source_code_hashes=original_document.get('source_code_hashes'),
            exact_input_count=len(probes),
            exact_input_hashes=original_input_hashes,
        ),
        tested_implementation_source_hashes=source_hashes(),
        paired_probe_ids=list(PAIRED_O150_IDS),
        control_input_hashes=control_input_hashes,
        scope={
            'synthetic_inputs_only': True,
            'candidate_claims': False,
            'historical_claims': False,
        },
        status='pass' if all(x['status'] == 'pass' for x in rows) else 'fail',
        probes=rows,
        full_observation_tests_execution='See final test-run.json; file linkage alone is not a test execution claim.',
    )
    OUTPUT.write_text(json.dumps(jsonable(doc),indent=2)+'\n')
    print(json.dumps(dict(status=doc['status'], passed=sum(x['status'] == 'pass' for x in rows),
                          total=len(rows), paired=len(PAIRED_O150_IDS), path=str(OUTPUT))))
    return 0 if doc['status']=='pass' else 1


if __name__=='__main__':raise SystemExit(main())
