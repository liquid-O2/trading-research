# SIRES: strategy reconstruction

Observed entry candidates: 11 setup, 67 no setup, 15 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

No setup is a rejection of a candidate by the strategy rules. It is not a losing trade or a software failure. Zero-candidate windows are retained separately and are not counted as confirmed absent setups.

| Branch | Scope | Source logic |
| --- | --- | --- |
| dom_rejection | entry_setup | DOM6/DOM7 pp.3–7: planned level → arriving effort/no progress → depth-one defense/rejection |
| absorption_reward_retest | entry_setup | ABS pp.5–13: real extreme → opposing effort/passive defense → own reward near origin → distinct reward-area retest/fresh defense |
| stop_four_stage | entry_setup | STOP pp.10,12,14: real extreme → defense → replenishment → opposing print thinning → absorber aggression and 2–4 tick lift-off; account -4R checked separately |
| footprint_confirmed_reaction | entry_setup | FP9 pp.4–7: known level → same-candle delta disagreement/absorption → within-candle POC relocation → local flow |
| vwap_deviation_fade | entry_setup | VWAP pp.3–8: auction context → pre-touch executed VWAP/deviation → same-band absorption → local CVD/ladder confirmation |
| ofm_aggressive | entry_setup | OFM pp.3–13;BIG pp.7–14,18;CONT p.10: catalyst → release → failed squeeze → catalyst reclaim/refill → initiative/wicks → defended drive retest; source gamma retained separately |
| ofm_passive | entry_setup | OFM p.14: failed squeeze → dying tape/no aggressive failure → actual buyer area → trigger above buyers and stop below aggression |
| clean_squeeze | entry_setup | CONT p.11;OFM p.5: catalyst → fast release with no earlier failure → first pullback → opposing absorption → continuation |
| balance_failure_fade | entry_setup | BIG pp.14–15,18: balance extreme → unpaid aggression → leave → same-area retest still unpaid → prior opposite-control target; dated gamma input separate |
| defended_band_continuation | entry_setup | NYAM pp.4–5;K18 pp.7,11,14;CONT pp.4–10;ANAT p.7: prior band control → distinct current return → fresh same-side defense/refresh and executed aggression |
| microbalance_break | entry_setup | K2345 pp.4–7: larger direction → price-defined alternating-pivot microbalance → strength/break → stop behind that structure |
| kg1_retest | entry_setup | NYAM pp.8–9: dated source KG1 → actual same-band retest → aggressive confirmation → supplied management policy |
| case_description | supplemental_observation | FORMULAS:M05: case_description process/management unit |
| management | personal_execution_out_of_scope | FORMULAS:M05: management process/management unit |
| reentry | supplemental_observation | FORMULAS:M05: reentry process/management unit |

Operational model (gamma): `{'source': 'gex-framework.pdf pp.4–20; ny-am-session.pdf pp.8–9', 'inventory_assumption': 'call OI positive, put OI negative; model sign convention, not observed dealer inventory', 'option_model': 'European Black-Scholes, r=q=0, midquote implied volatility, 100 shares/contract', 'expiry': '0DTE if quoted; otherwise nearest listed expiry explicitly identified as a front-expiry approximation', 'oi': 'latest prior-date snapshot only', 'max_quote_age_seconds': 180, 'quote_availability': 'minute label plus 60 seconds; completed QQQ and NQ minute prices only', 'KG1': 'largest absolute signed gamma strike; same-time NQ/QQQ mapping; inferred key-gamma node, not proprietary KG1'}`

Operational model (auction): `{'source': 'the-math-behind-auction-market-theory.pdf pp.4–11', 'window_seconds': 120, 'high_effort_multiple': 1.5, 'low_efficiency': 0.2, 'high_efficiency': 0.6, 'replenishment_stop_fraction': 0.25, 'response': 'difference of first/last quarter-window execution VWAP; efficiency divided by window range', 'inventory': 'displayed depth-one additions/removals; removal less executions is an estimate, not identified cancels'}`

| Branch | Status | Condition | Observations |
| --- | --- | --- | --- |
| footprint_confirmed_reaction | no_setup | candle_delta_disagreement | 7 |
| absorption_reward_retest | no_setup | cvd_filter_ok | 5 |
| stop_four_stage | no_setup | delta_filter_ok | 5 |
| footprint_confirmed_reaction | no_setup | intrabar_poc_flip | 5 |
| footprint_confirmed_reaction | no_setup | source_flow_confirmation | 5 |
| vwap_deviation_fade | no_setup | cvd_filter_ok | 5 |
| ofm_aggressive | no_setup | cvd_filter_ok | 5 |
| microbalance_break | no_setup | objective_fixed | 5 |
| dom_rejection | no_setup | thesis_alive | 4 |
| dom_rejection | no_setup | risk_defined | 4 |
| absorption_reward_retest | no_setup | thesis_alive | 4 |
| absorption_reward_retest | no_setup | risk_defined | 4 |
| stop_four_stage | no_setup | thesis_alive | 4 |
| stop_four_stage | no_setup | risk_defined | 4 |
| footprint_confirmed_reaction | no_setup | thesis_alive | 4 |
| footprint_confirmed_reaction | no_setup | risk_defined | 4 |
| ofm_aggressive | no_setup | thesis_alive | 4 |
| ofm_aggressive | no_setup | risk_defined | 4 |
| clean_squeeze | no_setup | thesis_alive | 4 |
| clean_squeeze | no_setup | risk_defined | 4 |
| balance_failure_fade | no_setup | thesis_alive | 4 |
| balance_failure_fade | no_setup | risk_defined | 4 |
| kg1_retest | no_setup | thesis_alive | 4 |
| kg1_retest | no_setup | risk_defined | 4 |
| kg1_retest | no_setup | aggression_confirms | 4 |
| dom_rejection | data_unavailable | local_rejection | 3 |
| dom_rejection | data_unavailable | rejection_at | 3 |
| dom_rejection | data_unavailable | aggression_at rejection_at | 3 |
| dom_rejection | data_unavailable | decision_at rejection_at | 3 |
| vwap_deviation_fade | no_setup | thesis_alive | 3 |
| vwap_deviation_fade | no_setup | risk_defined | 3 |
| ofm_aggressive | no_setup | branch_regime_allowed | 3 |
| ofm_aggressive | no_setup | short_gamma | 3 |
| ofm_passive | no_setup | thesis_alive | 3 |
| ofm_passive | no_setup | risk_defined | 3 |
| ofm_passive | no_setup | entry_above_buyers | 3 |
| clean_squeeze | data_unavailable | fast_release | 3 |
| clean_squeeze | data_unavailable | no_prior_squeeze_failure | 3 |
| clean_squeeze | data_unavailable | first_pullback | 3 |
| clean_squeeze | data_unavailable | opposing_pullback_aggression_absorbed | 3 |
| clean_squeeze | data_unavailable | continuation_confirmed | 3 |
| clean_squeeze | data_unavailable | release_at | 3 |
| clean_squeeze | data_unavailable | catalyst_at release_at | 3 |
| clean_squeeze | data_unavailable | pullback_at | 3 |
| clean_squeeze | data_unavailable | pullback_at release_at | 3 |
| clean_squeeze | data_unavailable | confirm_at pullback_at | 3 |
| balance_failure_fade | data_unavailable | left_failed_area | 3 |
| balance_failure_fade | data_unavailable | retest_same_failed_area | 3 |
| balance_failure_fade | data_unavailable | aggression_still_unrewarded | 3 |
| balance_failure_fade | data_unavailable | leave_at | 3 |
| balance_failure_fade | data_unavailable | failure_at leave_at | 3 |
| balance_failure_fade | data_unavailable | retest_at | 3 |
| balance_failure_fade | data_unavailable | leave_at retest_at | 3 |
| balance_failure_fade | data_unavailable | decision_at retest_at | 3 |
| dom_rejection | data_unavailable | arriving_aggression | 2 |
| dom_rejection | data_unavailable | little_progress | 2 |
| dom_rejection | data_unavailable | source_dom_confirmation | 2 |
| dom_rejection | data_unavailable | aggression_at | 2 |
| vwap_deviation_fade | data_unavailable | absorption_at_that_band | 2 |
| vwap_deviation_fade | data_unavailable | ladder_confirmation | 2 |
| ofm_passive | data_unavailable | source_squeeze_failed | 2 |
| ofm_passive | data_unavailable | tape_died_at_failure | 2 |
| ofm_passive | data_unavailable | no_aggression_at_failure | 2 |
| ofm_passive | data_unavailable | buyers_area_identified | 2 |
| ofm_passive | data_unavailable | failure_at | 2 |
| ofm_passive | data_unavailable | entry_trigger_at | 2 |
| ofm_passive | data_unavailable | entry_trigger_at failure_at | 2 |
| ofm_passive | data_unavailable | decision_at entry_trigger_at | 2 |
| clean_squeeze | data_unavailable | catalyst_known | 2 |
| clean_squeeze | data_unavailable | catalyst_at | 2 |
| balance_failure_fade | data_unavailable | branch_regime_allowed | 2 |
| balance_failure_fade | data_unavailable | long_gamma | 2 |
| balance_failure_fade | data_unavailable | failed_aggression_at_extreme | 2 |
| balance_failure_fade | data_unavailable | failure_at | 2 |
| microbalance_break | no_setup | directional_strength | 2 |
| absorption_reward_retest | data_unavailable | own_reward_confirmed | 1 |
| absorption_reward_retest | data_unavailable | reward_near_origin | 1 |
| absorption_reward_retest | data_unavailable | fresh_reward_retest_defended | 1 |
| absorption_reward_retest | data_unavailable | reward_at | 1 |
| absorption_reward_retest | data_unavailable | absorption_at reward_at | 1 |
| absorption_reward_retest | data_unavailable | retest_at | 1 |
| absorption_reward_retest | data_unavailable | retest_at reward_at | 1 |
| absorption_reward_retest | data_unavailable | decision_at retest_at | 1 |
| absorption_reward_retest | no_setup | reward_near_origin | 1 |
| stop_four_stage | data_unavailable | replenishment | 1 |
| stop_four_stage | data_unavailable | opponent_thinning | 1 |
| stop_four_stage | data_unavailable | absorber_aggressive | 1 |
| stop_four_stage | data_unavailable | lift_off | 1 |
| stop_four_stage | data_unavailable | reward_ticks | 1 |
| stop_four_stage | data_unavailable | entry_distance_ticks | 1 |
| stop_four_stage | data_unavailable | replenish_at | 1 |
| stop_four_stage | data_unavailable | defense_at replenish_at | 1 |
| stop_four_stage | data_unavailable | exhaust_at | 1 |
| stop_four_stage | data_unavailable | exhaust_at replenish_at | 1 |
| stop_four_stage | data_unavailable | liftoff_at | 1 |
| stop_four_stage | data_unavailable | exhaust_at liftoff_at | 1 |
| stop_four_stage | data_unavailable | decision_at liftoff_at | 1 |
| vwap_deviation_fade | no_setup | objective_fixed | 1 |
| vwap_deviation_fade | no_setup | ladder_confirmation | 1 |
| clean_squeeze | no_setup | fast_release | 1 |
| clean_squeeze | no_setup | no_prior_squeeze_failure | 1 |
| clean_squeeze | no_setup | opposing_pullback_aggression_absorbed | 1 |
| balance_failure_fade | no_setup | aggression_still_unrewarded | 1 |
| balance_failure_fade | no_setup | branch_regime_allowed | 1 |
| balance_failure_fade | no_setup | long_gamma | 1 |
| defended_band_continuation | no_setup | executed_aggression | 1 |
| defended_band_continuation | no_setup | control_side_matches_thesis | 1 |
| defended_band_continuation | no_setup | objective_fixed | 1 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/methods/SIRES.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/registry/STRATEGY_POLICY.json).
