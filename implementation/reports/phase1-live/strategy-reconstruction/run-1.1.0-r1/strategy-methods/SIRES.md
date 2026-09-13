# SIRES: strategy reconstruction

Observed entry candidates: 12 setup, 84 no setup, 0 unavailable market input. Separately retained context/process observations: 0. No personal quantity, account limit or executed-order history gates these setup results.

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
| vwap_deviation_fade | no_setup | ladder_confirmation | 9 |
| stop_four_stage | no_setup | absorber_aggressive | 8 |
| stop_four_stage | no_setup | lift_off | 8 |
| footprint_confirmed_reaction | no_setup | candle_delta_disagreement | 8 |
| vwap_deviation_fade | no_setup | absorption_at_that_band | 8 |
| ofm_aggressive | no_setup | repeated_effort_no_reward | 8 |
| ofm_aggressive | no_setup | initiative_drive | 8 |
| ofm_aggressive | no_setup | drive_retest_defended | 8 |
| ofm_aggressive | no_setup | own_aggression_rewarded | 8 |
| absorption_reward_retest | no_setup | fresh_reward_retest_defended | 7 |
| ofm_aggressive | no_setup | catalyst_reclaimed | 7 |
| ofm_aggressive | no_setup | refill_held | 7 |
| clean_squeeze | no_setup | continuation_confirmed | 7 |
| dom_rejection | no_setup | local_rejection | 6 |
| absorption_reward_retest | no_setup | own_reward_confirmed | 6 |
| absorption_reward_retest | no_setup | cvd_filter_ok | 6 |
| stop_four_stage | no_setup | replenishment | 6 |
| stop_four_stage | no_setup | opponent_thinning | 6 |
| footprint_confirmed_reaction | no_setup | source_flow_confirmation | 6 |
| ofm_aggressive | no_setup | first_squeeze | 6 |
| ofm_aggressive | no_setup | squeeze_failed | 6 |
| clean_squeeze | no_setup | first_pullback | 6 |
| balance_failure_fade | no_setup | left_failed_area | 6 |
| balance_failure_fade | no_setup | retest_same_failed_area | 6 |
| stop_four_stage | no_setup | delta_filter_ok | 5 |
| footprint_confirmed_reaction | no_setup | intrabar_poc_flip | 5 |
| vwap_deviation_fade | no_setup | cvd_filter_ok | 5 |
| ofm_aggressive | no_setup | cvd_filter_ok | 5 |
| microbalance_break | no_setup | objective_fixed | 5 |
| kg1_retest | no_setup | thesis_alive | 5 |
| kg1_retest | no_setup | risk_defined | 5 |
| kg1_retest | no_setup | aggression_confirms | 5 |
| dom_rejection | no_setup | arriving_aggression | 4 |
| dom_rejection | no_setup | little_progress | 4 |
| dom_rejection | no_setup | source_dom_confirmation | 4 |
| absorption_reward_retest | no_setup | passive_wall_confirmed | 4 |
| absorption_reward_retest | no_setup | opposing_effort_no_result | 4 |
| stop_four_stage | no_setup | defense | 4 |
| stop_four_stage | no_setup | thesis_alive | 4 |
| stop_four_stage | no_setup | risk_defined | 4 |
| footprint_confirmed_reaction | no_setup | local_absorption | 4 |
| ofm_aggressive | no_setup | thesis_alive | 4 |
| ofm_aggressive | no_setup | risk_defined | 4 |
| ofm_passive | no_setup | source_squeeze_failed | 4 |
| ofm_passive | no_setup | buyers_area_identified | 4 |
| clean_squeeze | no_setup | catalyst_known | 4 |
| balance_failure_fade | no_setup | failed_aggression_at_extreme | 4 |
| balance_failure_fade | no_setup | thesis_alive | 4 |
| balance_failure_fade | no_setup | risk_defined | 4 |
| dom_rejection | no_setup | thesis_alive | 3 |
| dom_rejection | no_setup | risk_defined | 3 |
| absorption_reward_retest | no_setup | thesis_alive | 3 |
| absorption_reward_retest | no_setup | risk_defined | 3 |
| footprint_confirmed_reaction | no_setup | thesis_alive | 3 |
| footprint_confirmed_reaction | no_setup | risk_defined | 3 |
| vwap_deviation_fade | no_setup | thesis_alive | 3 |
| vwap_deviation_fade | no_setup | risk_defined | 3 |
| ofm_aggressive | no_setup | branch_regime_allowed | 3 |
| ofm_aggressive | no_setup | short_gamma | 3 |
| clean_squeeze | no_setup | thesis_alive | 3 |
| clean_squeeze | no_setup | risk_defined | 3 |
| microbalance_break | no_setup | directional_strength | 3 |
| absorption_reward_retest | no_setup | reward_near_origin | 2 |
| ofm_passive | no_setup | thesis_alive | 2 |
| ofm_passive | no_setup | risk_defined | 2 |
| ofm_passive | no_setup | entry_above_buyers | 2 |
| clean_squeeze | no_setup | fast_release | 2 |
| clean_squeeze | no_setup | no_prior_squeeze_failure | 2 |
| clean_squeeze | no_setup | opposing_pullback_aggression_absorbed | 2 |
| balance_failure_fade | no_setup | aggression_still_unrewarded | 2 |
| defended_band_continuation | no_setup | executed_aggression | 2 |
| defended_band_continuation | no_setup | control_side_matches_thesis | 2 |
| defended_band_continuation | no_setup | objective_fixed | 2 |
| defended_band_continuation | no_setup | fresh_same_side_defense | 2 |
| defended_band_continuation | no_setup | refresh_consistent | 2 |
| vwap_deviation_fade | no_setup | objective_fixed | 1 |
| ofm_passive | no_setup | tape_died_at_failure | 1 |
| ofm_passive | no_setup | no_aggression_at_failure | 1 |
| balance_failure_fade | no_setup | branch_regime_allowed | 1 |
| balance_failure_fade | no_setup | long_gamma | 1 |

Full episode values, inferred-model receipts and legacy source-audit comparisons: [native report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/methods/SIRES.md). [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json).
