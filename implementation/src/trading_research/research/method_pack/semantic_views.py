"""Closed method views and audited source interpretations for all M01--M12.

A source interpretation is a separately attributed observation. It is never
turned into a native detector. Arithmetic and event views below consume only
validated domain output, with source roles preserving the selected object.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import hashlib
from functools import lru_cache

from .catalog import METHOD_BY_ID
from .contracts import fields_for, OUTPUT_SCHEMAS
from .logic import kleene_and
from .source_config import SourceSetting, load_catalog


# Every role groups a source-selected reference/observation, rather than merely
# renaming a field. Different roles may have equal prices without equal identity.
ROLE_GROUPS = {
'JJ-TBR': {
 'selected_attempt': 'branch decision_at',
 'source_range': 'range_frozen range_known_at',
 'pre_entry_context': 'context_fixed context_at directional_context reversal_context extended_context purged_compressed_context rotation_context reduced_expectations expansion_policy',
 'location_contact': 'location_touched touch_at edge_swept sweep_at entry_at_eq_or_quadrant entry_at_named_internal_or_ev_band',
 'source_confirmation': 'source_confirmation confirm_at reaction_side_confirmed',
 'structural_risk': 'risk_defined',
 'selected_objective': 'objective_fixed objective_is_selected_exhaustion objective_is_opposing_draw objective_is_range_edge objective_is_named_rotation_target objective_is_remaining_draw',
 'source_clock': 'at_rth_open exit_window_recorded source_time_window source_clock_verified source_case_verified',
 'purged_range': 'purge_known_at', 'source_extension': 'prior_expansion touch_in_source_extension_area',
 'timed_pzone': 'source_zone_known zone_known_at directed_path_recorded'},
'GB-FAIL': {
 'selected_attempt': 'side decision_at', 'failure_reference': 'reference_frozen reference_known_at reference_px',
 'pre_entry_bias': 'bias_recorded context_at', 'source_session': 'source_session_allowed',
 'failure_confirmation': 'sweep_at sweep_high sweep_low confirmation_mode complete_clock_five_minute_bar confirm_at confirm_close source_hold_confirmed box_return_ok',
 'tdo_refinement': 'tdo_required source_tdo_close_confirmed',
 'measured_impulse_pocket': 'pocket_required impulse_known_at touch_at touch_in_measured_pocket',
 'retracement_entry': 'retracement_entry retest_at', 'structural_risk': 'risk_defined', 'selected_objective': 'objective_fixed'},
'GB-VWAP': {
 'session_references': 'reference_frozen', 'london': 'london_high london_known_at', 'asia': 'asia_high asia_known_at',
 'continuation_context': 'continuation_context', 'breakout_candle': 'breakout_at breakout_close',
 'vwap_at_retest': 'vwap_reset_verified vwap_known_at vwap_at_retest',
 'retest_candle': 'retest_at retest_low retest_high', 'structural_risk': 'risk_defined', 'selected_attempt': 'decision_at side'},
'GB-SCALP': {'pre_entry_bias': 'direction_recorded_before_entry', 'source_small_size': 'small_size_recorded',
 'directional_pullback': 'source_directional_pullback_observed', 'scalp_management': 'source_scalp_management_recorded'},
'SIRES': {
 'selected_attempt': 'decision_at side', 'current_thesis': 'thesis_alive thesis_dead thesis_known_at',
 'auction_route': 'auction_route_ok', 'current_regime': 'branch_regime_allowed short_gamma long_gamma',
 'source_location': 'location_fixed location_touched real_extreme at_valid_level location_known_at level_known_at touch_at',
 'selected_objective': 'objective_fixed', 'structural_risk': 'risk_defined', 'confirmed_branch': 'sires_branch_ok confirm_at',
 'dom_rejection': 'arriving_aggression little_progress local_rejection source_dom_confirmation aggression_at rejection_at',
 'absorption_reward_retest': 'passive_wall_confirmed opposing_effort_no_result own_reward_confirmed reward_near_origin fresh_reward_retest_defended absorption_at reward_at cvd_filter_ok delta_filter_ok',
 'stop_four_stage': 'defense replenishment opponent_thinning absorber_aggressive lift_off defense_at replenish_at exhaust_at liftoff_at reward_ticks entry_distance_ticks daily_r_before',
 'footprint_reaction': 'candle_delta_disagreement local_absorption intrabar_poc_flip source_flow_confirmation flip_at',
 'deviation_reaction': 'source_vwap_known selected_deviation_touched absorption_at_that_band ladder_confirmation band_known_at',
 'aggressive_ofm': 'repeated_effort_no_reward first_squeeze squeeze_failed catalyst_reclaimed refill_held initiative_drive intervening_wicks_taken drive_retest_defended own_aggression_rewarded catalyst_at first_release_at failure_at refill_at drive_at',
 'passive_ofm': 'source_squeeze_failed tape_died_at_failure no_aggression_at_failure buyers_area_identified entry_above_buyers stop_below_aggression entry_trigger_at',
 'clean_squeeze': 'catalyst_known fast_release no_prior_squeeze_failure first_pullback opposing_pullback_aggression_absorbed continuation_confirmed release_at pullback_at',
 'balance_failure': 'balance_context failed_aggression_at_extreme left_failed_area retest_same_failed_area aggression_still_unrewarded target_is_prior_opposite_control leave_at',
 'defended_band': 'prior_band_control same_band_retest fresh_same_side_defense executed_aggression refresh_consistent control_side_matches_thesis prior_defense_at',
 'microbalance': 'microbalance_frozen directional_strength breakout_in_thesis_direction stop_behind_microbalance microbalance_known_at breakout_at',
 'kg1': 'source_kg1_level_known kg1_retest aggression_confirms', 'selected_retest': 'retest_at',
 'early_attempt': 'preconfirmation_entry small_risk_declared stop_predefined explicitly_early_entry source_refill_return source_risk_predefined',
 'third_test': 'same_support_band distinct_test_count no_new_buyer_defense',
 'late_resistance': 'resistance_known_before_approach upward_approach_loses_aggression',
 'management_action': 'action_at action_matches_preselected_policy supporting_structure_known_at stop_trailed protected_structure_confirmed risk_added earlier_risk_secured exit_or_new_thesis_recorded',
 'reentry': 'same_band_id price_back_inside_band fresh_confirmation_after_stopout prior_exit_at fresh_confirmation_at daily_limit_allows_entry'},
'SAINT-AMT': {
 'selected_attempt': 'branch side decision_at', 'preselected_balance': 'balance_fixed_before_use balance_known_at profile_allows_trade',
 'local_control': 'arrival_read_recorded arrival_at control_evidence_recorded control_at alignment_ok',
 'structural_risk': 'risk_defined', 'selected_objective': 'objective_fixed',
 'continuation_retest': 'ltf_balance_broken ltf_balance_known_at breakout_at same_boundary_retest_held repeated_aggression_in_trade_direction retest_at confirm_at',
 'trapped_buyers': 'prior_buying_at_upper_extreme two_distinct_prior_failures prior_failures_known_at ltf_break_down repeated_body_selling',
 'failed_auction': 'older_value_tested older_value_rejected older_value_known_at older_value_touch_at rejection_at original_balance_reaccepted reaccept_at local_control_confirms_return',
 'poc_traversal': 'aggressive_poc_passage source_poc_hold_confirmed target_is_far_balance_edge poc_passage_at'},
'MEMBER-TWO-REASONS': {
 'current_thesis': 'thesis_predefined', 'selected_objective': 'objective_fixed', 'structural_risk': 'risk_defined',
 'selected_attempt': 'decision_at side', 'prior_reaction_area': 'prior_reaction_area_known area_known_at',
 'independent_minor_hvn': 'independent_minor_hvn_known hvn_known_at',
 'confluence_band': 'confluence_band_defined actual_band_contact touch_at',
 'short_rejection': 'resistance_rejection reaction_at stop_above_rejection_high',
 'planned_long_return': 'planned_return_to_structure buyers_absorb_and_hold stop_behind_long_invalidation'},
'KEANI-OPEN-ABOVE-VALUE': {
 'prior_session_value': 'prior_value_fixed prior_vah', 'opening_a': 'a_period_complete a_low a_end_at',
 'developing_value_response': 'developing_value_builds_higher source_rejection_observed observation_at',
 'developing_value_before_break': 'dev_vah_known_at dev_vah_at_break', 'breakout_candle': 'breakout_at breakout_close',
 'breakout_imbalance': 'aggressive_buy_imbalance_break imbalance_band_known_at',
 'imbalance_retest': 'retest_at defense_at buyers_defend_same_imbalance_band dom_supports_long',
 'source_clock': 'time_of_day_allowed', 'selected_objective': 'objective_fixed', 'structural_risk': 'risk_defined',
 'selected_attempt': 'decision_at side'},
'REFILL-STUDY': {
 'frozen_zone': 'zone_definition_recorded zone_frozen zone_known_at instrument_and_threshold_preserved',
 'distinct_touch': 'departure_observed departure_at distinct_touch_id touch_at', 'current_thesis': 'thesis_recorded',
 'causal_touch_features': 'feature_max_known_at memory_uses_only_prior_resolved_touches label_uses_only_post_touch_observations',
 'source_grade': 'grade_model_frozen_before_touch grade_available_at touch_selected_without_future_information',
 'selected_order_policy': 'order_at order_inside_ticks stop_ticks target_ticks cancel_minutes one_position_policy',
 'fill_and_cost': 'round_trip_cost_ticks stop_slippage_ticks fill_assumption_recorded'},
'JETBUNDLE-STATES': {
 'participation': 'participation_record_complete participation_known_at',
 'response': 'response_record_complete response_known_at',
 'current_state': 'state state_at two_sided_executions recent_revisits low_aggression_both_sides high_aggression low_response_efficiency opposite_liquidity_holds_and_refills aggression efficient_displacement prior_absorption_or_effort replenishment_stops level_gives_way cancellations_dominate',
 'future_transition': 'next_state_at conditioning_known_at'},
'STOIC-DATA': {
 'frozen_process': 'process_spec_frozen spec_known_at sample_start_at inclusion_rule_fixed uniform_schema',
 'complete_causal_journal': 'all_eligible_observations_retained features_available_before_decisions outcomes_separated_from_inputs',
 'aggregate_review': 'aggregate_winner_loser_comparison_recorded', 'causal_revision': 'revision_uses_only_prior_sample',
 'macro_vintages': 'release_vintages_recorded historical_comparison_defined cycle_and_indicator_rules_recorded'},
'STOIC-RISK': {
 'prior_validation': 'validated_process prior_sample_n win_rate_known average_rr_known mc_loss_streak_known',
 'printed_risk_ladder': 'base_risk_fraction risk_stage risk_units planned_reward_r next_risk_units',
 'first_closed_trade': 'first_trade_closed first_trade_result_units first_trade_close_at',
 'second_closed_trade': 'second_trade_result_units', 'selected_attempt': 'decision_at'},
}
ROLES = {(method, field): role for method, groups in ROLE_GROUPS.items()
         for role, fields in groups.items() for field in fields.split()}
for _method in METHOD_BY_ID:
    if {f for m,f in ROLES if m == _method} != set(fields_for(_method)):
        raise RuntimeError(f'{_method}: semantic role inventory differs from published operands')


@dataclass(frozen=True)
class View:
    path: str
    operation: str = 'exact'
    arguments: tuple = ()


VIEWS: dict[tuple[str, str, str], View] = {}

def views(method, rid, fields):
    for field, descriptor in fields.items():
        if field not in fields_for(method) or rid not in fields_for(method)[field].recipes:
            raise RuntimeError(f'foreign view {method}/{field}/{rid}')
        VIEWS[method, field, rid] = descriptor if isinstance(descriptor, View) else View(descriptor)

# Closed aliases and operations on complete, validated producer payloads.
for method in METHOD_BY_ID:
    for field in fields_for(method):
        for rid in fields_for(method)[field].recipes:
            if field == 'risk_defined' and rid == 'O139':
                views(method, rid, {field: View('stop_side_ok', 'all', ('risk_known_before_entry',))})
            if field == 'objective_fixed' and rid == 'O141':
                views(method, rid, {field: View('objective_preknown', 'all', ('active_at_selection',))})
views('JJ-TBR','O014',{'edge_swept':View('sweep_depth_points','positive')})
views('JJ-TBR','O047',{'edge_swept':View('sweep_at','observed')})
views('JJ-TBR','O056',{'confirm_at':'confirmation_at'})
views('JJ-TBR','O019',{'zone_known_at':'@known_at'})
views('JJ-TBR','O002',{'location_touched':'price_overlap','touch_at':'contact_at'})
views('GB-FAIL','O136',{'context_at':'bias_known_at'})
views('GB-FAIL','O046',{'reference_known_at':'@known_at','reference_frozen':View('formation_end','available')})
views('GB-FAIL','O048',{'reference_known_at':'@known_at','reference_frozen':View('period_end','available')})
views('GB-FAIL','O049',{'reference_px':'tdo_price','reference_known_at':'tdo_known_at','source_tdo_close_confirmed':'close_through_tdo'})
views('GB-FAIL','O050',{'reference_px':'cash_open','reference_known_at':'@known_at'})
views('GB-FAIL','O052',{'impulse_known_at':'@known_at'})
views('GB-VWAP','O046',{'asia_high':'box_high','london_high':'box_high','asia_known_at':'@known_at','london_known_at':'@known_at','reference_frozen':View('formation_end','available')})
views('GB-VWAP','O004',{'breakout_close':'C','breakout_at':'end'})
views('GB-VWAP','O030',{'vwap_at_retest':'vwap','vwap_known_at':'@known_at'})
views('GB-SCALP','O136',{'direction_recorded_before_entry':View('bias_recorded','all_available',('bias_known_at',))})
views('SIRES','O138',{'thesis_alive':'alive_at_decision','thesis_dead':View('alive_at_decision','not'),'thesis_known_at':'@known_at'})
views('SIRES','O033',{'branch_regime_allowed':'branch_regime_ok','short_gamma':View('source_regime','equals',('short_gamma',)),'long_gamma':View('source_regime','equals',('long_gamma',))})
views('SIRES','O071',{'location_fixed':'band_known_before_use','location_known_at':'@known_at','level_known_at':'@known_at'})
views('SIRES','O002',{'location_touched':'price_overlap','touch_at':'contact_at'})
for rid in [f'O{n}' for n in range(121,133)]:
    views('SIRES',rid,{'sires_branch_ok':'branch_ok'})
views('SIRES','O004',{'confirm_at':'end'})
for rid, aliases in {
 'O121': {'aggression_at':'aggression','rejection_at':'rejection'},
 'O122': {'absorption_at':'absorption','reward_at':'reward','retest_at':'reward_return'},
 'O123': {'defense_at':'defense','replenish_at':'replenishment','exhaust_at':'exhaustion','liftoff_at':'liftoff'},
 'O124': {'flip_at':'poc_flip'},
 'O126': {'catalyst_at':'catalyst','first_release_at':'first_release','failure_at':'failure','refill_at':'refill','drive_at':'drive','retest_at':'drive_retest'},
 'O127': {'entry_trigger_at':'entry_trigger'},
 'O128': {'release_at':'release','pullback_at':'pullback'},
 'O129': {'leave_at':'departure','retest_at':'same_area_return'},
 'O131': {'microbalance_known_at':'microbalance_known','breakout_at':'breakout'},
}.items():
    views('SIRES',rid,{field:'stage_ledger.'+stage for field,stage in aliases.items()})
views('SIRES','O128',{'no_prior_squeeze_failure':'no_prior_failure'})
views('SIRES','O131',{'stop_behind_microbalance':'stop_side_ok'})
views('SIRES','O132',{'source_kg1_level_known':'kg1_known'})
views('SIRES','O135',{'resistance_known_before_approach':'resistance_known','upward_approach_loses_aggression':'source_exhaustion'})
views('SIRES','O143',{'supporting_structure_known_at':'protected_known_at','protected_structure_confirmed':View('confirmation_at','observed')})
views('SIRES','O142',{'action_matches_preselected_policy':'action_policy_ok'})
views('SIRES','O144',{'same_band_id':'same_thesis_band','fresh_confirmation_after_stopout':View('fresh_confirmation_at','after',('parent_exit_at',)),'prior_exit_at':'parent_exit_at'})
views('SIRES','O145',{'daily_limit_allows_entry':'entry_permission'})
views('SAINT-AMT','O060',{'balance_fixed_before_use':'balance_active_at_use','balance_known_at':'@known_at'})
views('SAINT-AMT','O091',{'ltf_balance_broken':View('break_at','observed'),'ltf_balance_known_at':'ltf_balance_known_at','breakout_at':'break_at','same_boundary_retest_held':'same_boundary_retest_held'})
views('SAINT-AMT','O094',{'older_value_tested':View('explore_at','observed'),'older_value_rejected':View('failure_at','observed'),'older_value_known_at':'older_value_known_at','older_value_touch_at':'explore_at','rejection_at':'failure_at','original_balance_reaccepted':View('reaccept_at','observed')})
views('SAINT-AMT','O092',{'older_value_known_at':'older_value_known_at','original_balance_reaccepted':'reacceptance_sequence','reaccept_at':'acceptance_at'})
views('SAINT-AMT','O097',{'ltf_balance_known_at':'ltf_balance_known_at','older_value_known_at':'older_value_known_at','local_control_confirms_return':'alignment_ok'})
views('SAINT-AMT','O095',{'aggressive_poc_passage':'source_efficient_passage','source_poc_hold_confirmed':View('held_retest_at','observed'),'poc_passage_at':'passage_at'})
views('MEMBER-TWO-REASONS','O072',{'prior_reaction_area_known':'prior_defense_known','area_known_at':'@known_at','actual_band_contact':'same_band_contact'})
views('MEMBER-TWO-REASONS','O066',{'independent_minor_hvn_known':'source_node_known','hvn_known_at':'@known_at'})
views('MEMBER-TWO-REASONS','O071',{'confluence_band_defined':'band_known_before_use'})
views('MEMBER-TWO-REASONS','O002',{'actual_band_contact':'price_overlap','touch_at':'contact_at'})
views('KEANI-OPEN-ABOVE-VALUE','O062',{'prior_vah':'vah','prior_value_fixed':'construction_known','dev_vah_at_break':'vah','dev_vah_known_at':'@known_at'})
views('KEANI-OPEN-ABOVE-VALUE','O063',{'dev_vah_at_break':'vah','dev_vah_known_at':'@known_at'})
views('KEANI-OPEN-ABOVE-VALUE','O004',{'breakout_close':'C','breakout_at':'end'})
views('KEANI-OPEN-ABOVE-VALUE','O091',{'buyers_defend_same_imbalance_band':'buyers_defend_same_imbalance_band'})
views('REFILL-STUDY','O149',{'feature_max_known_at':'max_feature_known_at','grade_model_frozen_before_touch':'model_known_before_use','grade_available_at':'@known_at','touch_selected_without_future_information':'selected_by_supplied_rule'})
views('REFILL-STUDY','O152',{'round_trip_cost_ticks':'trade_cost_ticks'})
views('JETBUNDLE-STATES','O163',{'participation_record_complete':'source_process_complete','participation_known_at':'@known_at'})
views('JETBUNDLE-STATES','O164',{'response_known_at':'@known_at'})
views('JETBUNDLE-STATES','O165',{'state':'state_label','state_at':'state_at'})
views('JETBUNDLE-STATES','O166',{'conditioning_known_at':View('conditioning_evidence','max_availability')})
views('STOIC-DATA','O137',{'process_spec_frozen':View('frozen_at','observed'),'spec_known_at':'frozen_at'})
views('STOIC-DATA','O146',{'all_eligible_observations_retained':'eligible_ids_accounted_for','features_available_before_decisions':'pre_entry_fields_valid'})
views('STOIC-DATA','O148',{'revision_uses_only_prior_sample':'cohort_causal'})
views('STOIC-DATA','O162',{'release_vintages_recorded':View('vintage_history','observed')})
views('STOIC-RISK','O154',{'validated_process':'overlay_validation','prior_sample_n':'sample_n','win_rate_known':'winrate_known','mc_loss_streak_known':'mc_result_known'})
views('STOIC-RISK','O155',{'risk_stage':'printed_stage','risk_units':'planned_risk_units','planned_reward_r':View('planned_reward_units','ratio',('planned_risk_units',))})

# Literal method measurements from exact geometry, contact and risk outputs.
views('GB-FAIL','O046',{'reference_px':View('box_high','side_reference',('box_low',)),
                      'reference_frozen':View('source_clock_verified','all_available',('known_at',))})
views('GB-FAIL','O048',{'reference_px':View('prior_high','side_reference',('prior_low',)),
                      'reference_known_at':'@known_at'})
views('JJ-TBR','O007',{'entry_at_eq_or_quadrant':'selected_contact','entry_at_named_internal_or_ev_band':'selected_contact'})
views('JJ-TBR','O010',{'prior_expansion':View('high_break_at','any_observed',('low_break_at',))})
views('JJ-TBR','O015',{'touch_in_source_extension_area':'selected_contact'})
views('GB-FAIL','O052',{'touch_at':'selected_contact_at','touch_in_measured_pocket':'selected_contact'})
views('GB-VWAP','O002',{'retest_at':'contact_at','retest_high':'observed_high','retest_low':'observed_low'})
views('MEMBER-TWO-REASONS','O139',{
    'stop_above_rejection_high':View('invalidation_ref','stop_beyond',('short',)),
    'stop_behind_long_invalidation':View('invalidation_ref','stop_beyond',('long',))})
views('KEANI-OPEN-ABOVE-VALUE','O109',{
    'aggressive_buy_imbalance_break':View('buy_runs','buy_imbalance'),
    'imbalance_band_known_at':View('buy_runs','buy_band_known_at')})


def projection(method, field, rid):
    custom = VIEWS.get((method,field,rid))
    if custom is not None:
        return custom
    # This is an exact typed field, not an arbitrary caller-selected alias.
    if field in OUTPUT_SCHEMAS.get(rid, {}):
        return View(field)
    return None


def path_value(value, path, envelope):
    if path == '@known_at':
        return envelope.get('known_at')
    for part in path.split('.'):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def project(view, value, envelope, candidate):
    x = path_value(value,view.path,envelope)
    if view.operation == 'exact': return x
    args = [path_value(value,p,envelope) for p in view.arguments]
    if view.operation == 'side_reference':
        return x if candidate.get('side') == 'short' else args[0] if candidate.get('side') == 'long' else None
    if view.operation == 'any_observed':
        return True if any(v is not None for v in [x,*args]) else False if value.get('window_complete') is True else None
    if view.operation in {'buy_imbalance','buy_band_known_at'}:
        if value.get('ratio_min') is None or value.get('row_count') is None or not isinstance(x,list):return None
        comparisons=value.get('buy_comparisons')
        if not isinstance(comparisons,list) or not comparisons:return None
        qualifies=True if x else None if any(row.get('qualifies') is None for row in comparisons) else False
        if view.operation=='buy_imbalance':return qualifies
        return envelope.get('known_at') if qualifies is True and len(x)==1 else None
    if view.operation=='stop_beyond':
        side=view.arguments[0]
        stop=value.get('planned_stop')
        if not isinstance(x,dict) or not x.get('object_id') or x.get('value') is None or stop is None:return None
        if value.get('planned_stop_side')!=side or candidate.get('side',side)!=side:return False
        relation=Decimal(stop)>Decimal(x['value']) if side=='short' else Decimal(stop)<Decimal(x['value'])
        return kleene_and(relation,value.get('risk_known_before_entry'),value.get('stop_side_ok'))
    if view.operation == 'positive': return None if x is None else x>0
    if view.operation == 'not': return None if x is None else not x
    if view.operation == 'equals': return None if x is None else x == view.arguments[0]
    if view.operation == 'all': return kleene_and(x,*args)
    if view.operation == 'max_availability':
        if not isinstance(x,list) or not x: return None
        times = [row.get('known_at',row.get('available_at')) for row in x]
        return None if any(type(t) is not int for t in times) else max(times)
    if view.operation == 'ratio': return None if x is None or any(a is None or a == 0 for a in args) else Decimal(x)/Decimal(args[0])
    if view.operation == 'observed': return None if x is None else bool(x) if isinstance(x,(list,dict,str)) else True
    if view.operation == 'after': return None if x is None or any(a is None for a in args) else all(x>a for a in args)
    if view.operation == 'available':
        return None if x is None or envelope.get('known_at') is None else x<=envelope['known_at']<=candidate['decision_at']
    if view.operation == 'all_available':
        return kleene_and(x,*(None if t is None else t<=candidate['decision_at'] for t in args))
    if view.operation == 'all_observed': return kleene_and(x,*(None if a is None else True for a in args))
    raise ValueError(f'unsupported closed semantic operation {view.operation}')


# Source attribution is frozen independently of caller-supplied author fields.
SOURCE_KEYS = {
 'JJ-TBR': {'JR','TBR','SS','XF','FIND'},
 'GB-FAIL': {'GB'}, 'GB-VWAP': {'GB'}, 'GB-SCALP': {'GB'},
 'SIRES': {'AMT1','VP2','TPO','VIX4','DOM5','DOM6','DOM7','FP8','FP9','VWAP','C1','C2','C3','EMO','GEX','MAMT','ABS','STOP','RD','BIG','OFM','REF','NYAM','K18','K2345','ANAT','CONT','RTVP'},
 'SAINT-AMT': {'AMTL','WIC','TRAP'}, 'MEMBER-TWO-REASONS': {'K10'},
 'KEANI-OPEN-ABOVE-VALUE': {'AVG'}, 'REFILL-STUDY': {'REF','OFM'},
 'JETBUNDLE-STATES': {'MATH'}, 'STOIC-DATA': {'DATA'}, 'STOIC-RISK': {'DATA'},
}
AUTHORS = {
 'JJ-TBR': {'JJ-TBR','JJumbo','JJumboFX','Jumbo'},
 'GB-FAIL': {'GB-FAIL','GB','Greenbird','Green Bird','greenbirdtrader'},
 'GB-VWAP': {'GB-VWAP','GB','Greenbird','Green Bird','greenbirdtrader'},
 'GB-SCALP': {'GB-SCALP','GB','Greenbird','Green Bird','greenbirdtrader'},
 'SIRES': {'SIRES','Sires'}, 'SAINT-AMT': {'SAINT-AMT','Saint'},
 'MEMBER-TWO-REASONS': {'MEMBER-TWO-REASONS','member'},
 'KEANI-OPEN-ABOVE-VALUE': {'KEANI-OPEN-ABOVE-VALUE','Keani'},
 'REFILL-STUDY': {'REFILL-STUDY','Sires'}, 'JETBUNDLE-STATES': {'JETBUNDLE-STATES','Jetbundle'},
 'STOIC-DATA': {'STOIC-DATA','Stoic'}, 'STOIC-RISK': {'STOIC-RISK','Stoic'},
}

# These are specified measurements/calculations, not unpublished interpretive
# detectors. A source quote may be an observation, but cannot close missing code.
REQUIRES_DOMAIN_VIEW = {
 'JJ-TBR': 'edge_swept entry_at_eq_or_quadrant entry_at_named_internal_or_ev_band prior_expansion touch_in_source_extension_area',
 'GB-FAIL': 'sweep_high sweep_low complete_clock_five_minute_bar confirm_close box_return_ok touch_at touch_in_measured_pocket retest_at',
 'GB-VWAP': 'vwap_reset_verified retest_at retest_low retest_high',
 'SIRES': 'same_support_band reward_ticks entry_distance_ticks daily_r_before',
 'SAINT-AMT': 'two_distinct_prior_failures prior_failures_known_at ltf_balance_known_at older_value_known_at',
 'MEMBER-TWO-REASONS': 'stop_above_rejection_high stop_behind_long_invalidation',
 'KEANI-OPEN-ABOVE-VALUE': 'aggressive_buy_imbalance_break imbalance_band_known_at',
 'REFILL-STUDY': 'zone_definition_recorded zone_frozen instrument_and_threshold_preserved departure_observed distinct_touch_id touch_at memory_uses_only_prior_resolved_touches label_uses_only_post_touch_observations',
 'JETBUNDLE-STATES': 'response_record_complete two_sided_executions',
 'STOIC-DATA': 'inclusion_rule_fixed uniform_schema outcomes_separated_from_inputs aggregate_winner_loser_comparison_recorded',
 'STOIC-RISK': 'base_risk_fraction next_risk_units first_trade_closed first_trade_result_units first_trade_close_at second_trade_result_units',
}
REQUIRES_DOMAIN_VIEW = {(m,f) for m,fields in REQUIRES_DOMAIN_VIEW.items() for f in fields.split()}


def source_interpretation_supported(method,field):
    return (method,field) not in REQUIRES_DOMAIN_VIEW


@lru_cache(maxsize=128)
def _source_bytes(path, stamp):
    source = Path(path)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    pages = None
    if source.suffix.lower() == '.pdf':
        import pypdf
        pages = len(pypdf.PdfReader(source).pages)
    return digest,pages


def source_citation(citation, method):
    """Verify the actual source bytes and locator, without interpreting a chart.

    A chart interpretation retains its page/image crop, while text retains an
    exact excerpt. The result remains supplied evidence even after verification.
    """
    if not isinstance(citation,dict): raise ValueError('source citation must be structured')
    catalog = load_catalog()
    key = citation.get('source_key')
    if key not in SOURCE_KEYS[method] or key not in catalog['sources']:
        raise ValueError('source citation is not an authorized source for this method')
    expected = catalog['sources'][key]
    path = Path(citation.get('source_file',''))
    if path.resolve() != Path(expected['path']).resolve() or citation.get('sha256') != expected['sha256']:
        raise ValueError('source citation differs from frozen catalog source')
    if not path.is_file(): raise ValueError('source citation file is absent')
    stat = path.stat()
    digest,pages = _source_bytes(str(path),(stat.st_dev,stat.st_ino,stat.st_size,stat.st_mtime_ns,stat.st_ctime_ns))
    if digest != citation.get('sha256'):
        raise ValueError('source citation hash differs from actual bytes')
    if path.suffix.lower() == '.pdf':
        if type(citation.get('page')) is not int or citation['page'] < 1 or not citation.get('image_id'):
            raise ValueError('source chart interpretation needs page and image identity')
        if citation['page'] > pages: raise ValueError('source page is outside actual PDF')
        expected_image = f'{key}:{citation["page"]}:page'
        images = [image for case in catalog.get('cases',[]) for image in case.get('source_images',[])
                  if image.get('source_key') == key and image.get('page') == citation['page'] and image.get('sha256') == digest]
        if citation['image_id'] != expected_image and not any(image['image_id']==citation['image_id'] for image in images):
            raise ValueError('source image identity is not a catalog image or exact full page')
    else:
        quote = citation.get('quote')
        if not isinstance(quote,str) or not quote.strip() or quote not in path.read_text():
            raise ValueError('source interpretation quote not present in actual source')
    return citation


def audit_interpretation(method,field,rid,record,candidate,payload):
    """Admit an explicit author observation, never an automatic detector.

    The payload must preserve the dated source criterion, actual source bytes,
    an observed typed value, and separately identified observations supporting
    that interpretation. Source conflicts/unknowns propagate as unknown.
    """
    row = payload.get('source_interpretation')
    if not isinstance(row,dict): return None
    if not source_interpretation_supported(method,field):
        raise ValueError(f'{field}: specified domain view cannot be replaced by a source interpretation')
    if record.get('author',method) not in AUTHORS[method] or row.get('author') not in AUTHORS[method]:
        raise ValueError('source interpretation author is not the frozen method author')
    for key,expected in {'method_id':method,'field':field,'recipe_id':rid,'author':record.get('author',method),
                         'instrument_id':candidate['instrument_id'],'session_date_et':candidate['session_date_et'],
                         'semantic_role':ROLES[method,field]}.items():
        if str(row.get(key)) != str(expected): raise ValueError(f'source interpretation has foreign {key}')
    if row.get('branch') != candidate['branch']: raise ValueError('source interpretation has foreign branch')
    if row.get('known_at') != record.get('known_at'): raise ValueError('source interpretation availability differs from record')
    source_citation(row.get('citation'),method)
    criterion = SourceSetting.parse(row.get('criterion',{}))
    if criterion.status != 'fact': return {'value':None,'status':criterion.status,'role':row['semantic_role']}
    spec = criterion.resolve()
    if not isinstance(spec,dict) or spec.get('field') != field or spec.get('rule') != fields_for(method)[field].rule:
        raise ValueError('source interpretation criterion differs from the published field contract')
    observations = row.get('observations')
    if not isinstance(observations,list) or not observations: raise ValueError('source interpretation lacks actual supporting observations')
    seen = set()
    for observed in observations:
        oid = observed.get('observation_id')
        if not oid or oid in seen: raise ValueError('source interpretation observations need unique identities')
        seen.add(oid)
        if observed.get('known_at') is None or observed['known_at'] > row['known_at']:
            raise ValueError('source interpretation incorporates a later observation')
        if not isinstance(observed.get('description'),str) or not observed['description'].strip():
            raise ValueError('source interpretation needs the actual observed behavior')
        source_citation(observed.get('citation'),method)
    if not isinstance(row.get('reason'),str) or not row['reason'].strip():
        raise ValueError('source interpretation lacks its evidence reasoning')
    # This is deliberately a typed supplied observation, not an inferred event.
    # The value is checked by the assembler against the published operand type.
    value = SourceSetting.parse(row.get('observed_value',{}))
    return {'value':value.resolve(),'status':value.status,'role':row['semantic_role'],
            'source_ref':row['citation'],'observation_ids':sorted(seen),'known_at':row['known_at']}
