#!/usr/bin/env python3
"""Replay the 27 original counterexamples without changing their inputs.

Each negative check is paired with an identified regression exercising the
complete observations. Rejecting incomplete legacy records alone is not the
evidence for implementation completeness.
"""
from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path

from trading_research.research.method_pack import objects  # register domains
from trading_research.research.method_pack.protocol import jsonable, run_recipe

ROOT=Path(__file__).resolve().parents[2]
ORIGINAL=ROOT/'implementation/reports/phase1-live/methods/charts/full-audit-probes.json'
OUTPUT=ROOT/'implementation/validation/phase1-completion/audit-regressions.json'


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
        'P21': lambda: v.get('remaining_quantity')==0 and v.get('position_quantity')==1 and v.get('lifecycle_valid') is None,
        'P22': lambda: v.get('position_quantity')==0 and v.get('lifecycle_valid') is None,
        'P23': lambda: result.base_ok is False and v.get('filled_quantity')==0 and v.get('lifecycle_valid') is False,
        'P24': lambda: v.get('authorized_quantity')==5 and v.get('filled_quantity')==1 and v.get('remaining_quantity')==4,
        'P25': lambda: v.get('filled_quantity')==0 and result.known_at==10 and any(x.get('kind')=='fill' for x in v.get('pending_events',[])),
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
    probes=json.loads(ORIGINAL.read_text())['probes'];rows=[]
    assert len(probes)==27 and {x['id'] for x in probes}==set(TESTS)
    for probe in probes:
        result=run_recipe(probe['object_id'],probe['input'])
        filename,test_name=TESTS[probe['id']];test=ROOT/'implementation/tests'/filename
        assert 'def '+test_name+'(' in test.read_text(),test_name
        passed=checks(probe['id'],result)
        rows.append(dict(id=probe['id'],object_id=probe['object_id'],status='pass' if passed else 'fail',
            original_finding=probe['finding'],contract_expectation=probe['contract_expectation'],
            original_input=probe['input'],actual=asdict(result),gap_observed=not passed,
            full_observation_regression=dict(path=str(test),test=test_name,sha256=hashlib.sha256(test.read_bytes()).hexdigest()),
            scope='Unchanged original helper probe plus linked complete-observation regression; neither is a historical source candidate.'))
    doc=dict(schema='phase1-audit-regressions-v2',original=dict(path=str(ORIGINAL),sha256=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()),
        status='pass' if all(x['status']=='pass' for x in rows) else 'fail',probes=rows,
        full_observation_tests_execution='See final test-run.json; file linkage alone is not a test execution claim.')
    OUTPUT.write_text(json.dumps(jsonable(doc),indent=2)+'\n')
    print(json.dumps(dict(status=doc['status'],passed=sum(x['status']=='pass' for x in rows),total=len(rows),path=str(OUTPUT))))
    return 0 if doc['status']=='pass' else 1


if __name__=='__main__':raise SystemExit(main())
