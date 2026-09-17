# P15-16A family report

B0.2 source-fidelity baseline over the native calendar. Faithful disagreements against the author are not claimed.

The previous B0.2 run root 1e13829f2c88f1e1 is superseded: jobs were named jobs/<date>/<branch>.json.gz so KEANI-OPEN-ABOVE-VALUE:branch:source_long collided with GB-VWAP:branch:source_long. Distinct gzip files on that root: 66196. This run uses coverage_id--json.gz job paths; KEANI is measured; jobs_declared = 39 x 1742 = 67938.

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| GB-FAIL | B0.2 | 32307 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/7f7929dfcac0d7ae/attempt-0001 |
| GB-SCALP | B0.2 | 1741 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/7f7929dfcac0d7ae/attempt-0001 |
| GB-VWAP | B0.2 | 1742 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/7f7929dfcac0d7ae/attempt-0001 |
| JJ-TBR | B0.2 | 21717 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/7f7929dfcac0d7ae/attempt-0001 |
| KEANI-OPEN-ABOVE-VALUE | B0.2 | 1742 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/7f7929dfcac0d7ae/attempt-0001 |
| MEMBER-TWO-REASONS | B0.2 | 3484 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/7f7929dfcac0d7ae/attempt-0001 |
| REFILL-STUDY | B0.2 | 795369 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/7f7929dfcac0d7ae/attempt-0001 |
| SAINT-AMT | B0.2 | 9114 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/7f7929dfcac0d7ae/attempt-0001 |
| SIRES | B0.2 | 267493 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/7f7929dfcac0d7ae/attempt-0001 |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| GB-FAIL | F01 | implemented | test_p15_16a_greenbird.py::test_f01_old_scalp_branches_are_observations | 0 | 0 | GB p.40 |
| SIRES | F02 | implemented | test_p15_16a_sires.py::test_f02_pullback_then_absorption_is_not_clean_squeeze | 0 | 0 | CONT p.11 |
| SIRES | F03 | implemented | test_p15_16a_sires.py::test_f03_replenishment_three_refills_pass_two_fail | 0 | 0 | STOP pp.10, 14 |
| SAINT-AMT | F04 | implemented | test_p15_16a_saint.py::test_F04_arrival_fast_vs_slow | 0 | 0 | OD:approach_bars=5,fast_ratio=0.08 of balance_width (WIC p.4) |
| SAINT-AMT | F05 | implemented | test_p15_16a_saint.py::test_F05_no_older_auction_gate | 0 | 0 | AMTL p.8 |
| GB-FAIL | F06 | implemented | test_p15_16a_greenbird.py::test_f06_a1_requires_retest_and_post_open_close | 0 | 0 | GB NG 2099513366326730859; GB p.60 |
| GB-FAIL | F07 | implemented | test_p15_16a_greenbird.py::test_f07_bias_reports_unfiltered_and_filtered | 0 | 0 | OD:prior_close_vs_range_midpoint,nyam_box_close_vs_open |
| JJ-TBR | F08 | implemented | test_p15_16a_jumbo.py::test_f08_extension_after_1000_and_1300_admitted | 0 | 0 | TBR p.12 |
| SIRES | F09 | implemented | test_p15_16a_sires.py::test_f09_location_lvn_passes_poc_fails | 0 | 0 | ABS pp.6-7; VP2 p.7; BIG p.10 |
| REFILL-STUDY | F10 | implemented | test_p15_16a_sires.py::test_f10_f20_refill_zone_from_clusters_and_departure_is_actual_time | 0 | 0 | OD:PRINT_THRESHOLD=40,CLUSTER_SECONDS=5,CLUSTER_MIN_SIZE=80 |
| JJ-TBR | F11 | implemented | test_p15_16a_jumbo.py::test_f11_3m_ob_baseline_and_od_variants_labelled | 0 | 0 | F11; RR-06 |
| JJ-TBR | F12 | implemented | no discriminating fixture: RULES membership is asserted in test_f18_f19_clock_fields; no nodeid fails when F12 behavior is removed | 0 | 0 | F12 note only |
| GB-FAIL | F13 | implemented | test_p15_16a_greenbird.py::test_f13_vwap_missing_retest_is_fail_not_unknown | 0 | 0 | OD:retest_horizon_rth_close; 60m_candidate |
| ALL | F14 | deferred | no discriminating fixture: SOURCE_ADDITIONS items 11/19/27 are documentation corrections | 0 | 0 | SOURCE_ADDITIONS items 11/19/27 are documentation corrections; B0.2 adapters implement the underlying F06/F13 rules. |
| MEMBER-TWO-REASONS | F15 | implemented | test_p15_16a_saint.py::test_F15_no_1245_split | 0 | 0 | K10 pp.5-8 |
| KEANI-OPEN-ABOVE-VALUE | F16 | implemented | test_p15_16a_saint.py::test_F16_no_1100_cutoff | 0 | 0 | TPO p.3 |
| JJ-TBR | F17 | implemented | no discriminating fixture: pzone generator unknown is labelled; no nodeid fails when this row is removed | 0 | 0 | OD:proprietary P-zone generator unknown |
| GB-FAIL,GB-SCALP,GB-VWAP,JJ-TBR | F18 | partial | test_p15_16a.py::test_S31_jj_tbr_clock_zone_verified | 0 | 0 | JJ-TBR is dropped from CLOCK_ZONE_UNVERIFIED_FAMILIES (TBR p.4/p.6 New York clock). GB-FAIL, GB-VWAP and GB-SCALP remain in the frozenset so frozen B0/B0.1 dual-scan flags do not move. WORK_LOG: keeping the frozen B0/B0.1 dual-scan flags from moving. |
| JJ-TBR | F19 | implemented | test_p15_16a_jumbo.py::test_f18_f19_clock_fields | 0 | 0 | JR p.71 ticket UTC; 2026 NT charts UK |
| REFILL-STUDY | F20 | implemented | test_p15_16a_sires.py::test_f10_f20_refill_zone_from_clusters_and_departure_is_actual_time | 0 | 0 | REF p.12 |
| JJ-TBR | RR-01 | implemented | test_p15_16a_jumbo.py::test_rr01_extension_band_identity_and_printed_examples | 0 | 0 | JR p.23; o015 |
| JJ-TBR | RR-02 | partial | test_p15_16a.py::test_S02_rr02_eq_contacts_are_two_sided | 0 | 0 | EQ two-sided is implemented in common.changed_reference_scan. Quadrant sides stay the default pair (q1 long / q3 short); they are not bound to the branch context as RR-02 states. WORK_LOG: q1 long / q3 short stay the default pair. |
| JJ-TBR | RR-03 | implemented | test_p15_16a_jumbo.py::test_rr03_sweep_before_0930_is_a_valid_trigger | 0 | 0 | JR p.20 |
| JJ-TBR | RR-04 | implemented | test_p15_16a_jumbo.py::test_rr04_london_box_is_0200_0300_not_0000_0300 | 0 | 0 | JR pp.50, 63-64 |
| JJ-TBR | RR-05 | implemented | test_p15_16a_jumbo.py::test_rr05_printed_pzone_absorption_fixture | 0 | 0 | JR pp.16-18 |
| JJ-TBR | RR-06 | implemented | test_p15_16a_jumbo.py::test_rr06_reclaim_is_the_entry_and_depth_is_recorded_not_required | 0 | 0 | JR p.71 |
| JJ-TBR | RR-07 | implemented | test_p15_16a_jumbo.py::test_rr07_sessionstat_coincidence_and_evrange_after_tape | 0 | 0 | OD:60-session mean/median of selected clock from native tape |
| JJ-TBR | RR-08 | implemented | test_p15_16a_jumbo.py::test_rr08_open_location_uses_prior_rth_at_0930 | 0 | 0 | JR pp.36, 38, 42 |
| JJ-TBR | RR-09 | implemented | test_p15_16a_jumbo.py::test_rr09_one_side_is_high_only_plus_low_only | 0 | 0 | JR pp.23, 37, 70 |
| ALL | RR-10 | deferred | no discriminating fixture: author-example replay set; covered by AUTHOR_EXAMPLE_REPLAY rather than a RULES row | 0 | 0 | Author-example replay set; covered by AUTHOR_EXAMPLE_REPLAY rather than a RULES row. |
| GB-FAIL | RR-11 | implemented | test_p15_16a_greenbird.py::test_rr11_september_uses_asia_0000_and_london_0200_0500 | 0 | 0 | OD:asia_box_windows,london_box_windows,ny_sub_boxes |
| GB-FAIL | RR-12 | implemented | test_p15_16a_greenbird.py::test_rr12_ladder_and_750_not_scored | 0 | 0 | GB pp.52-53, 56, 58, 60 |
| GB-FAIL | RR-13 | implemented | test_p15_16a_greenbird.py::test_rr13_five_minute_required_for_asia_high | 0 | 0 | GB pp.19, 25; RR-13 at-level box edges |
| GB-FAIL | RR-14 | implemented | test_p15_16a_greenbird.py::test_rr14_pocket_uses_impulse_not_910_box | 0 | 0 | GB pp.23, 25, 51; raw capture 2026-09-11 |
| GB-FAIL | RR-15 | implemented | test_p15_16a_greenbird.py::test_rr15_objective_horizon_is_next_open_not_30m | 0 | 0 | GB pp.51-54 |
| ALL | RR-16 | deferred | no discriminating fixture: GB author-example replay set; covered by AUTHOR_EXAMPLE_REPLAY | 0 | 0 | Author-example replay set for GB; covered by AUTHOR_EXAMPLE_REPLAY. |
| ALL | RR-17 | deferred | test_p15_16a_sires.py::test_rr17_replay_sires_author_examples | 0 | 0 | Author-example replay set for SIRES; covered by AUTHOR_EXAMPLE_REPLAY. |
| SIRES | RR-18 | implemented | test_p15_16a_sires.py::test_rr18_resting_stop_is_baseline_ofm_entry | 0 | 0 | K2345 p.9; OFM pp.11-14 |
| SIRES | RR-19 | implemented | test_p15_16a_sires.py::test_rr19_management_partial_trail_daily_stop | 0 | 0 | C2 p.5 |
| SIRES | RR-20 | implemented | test_p15_16a_sires.py::test_rr20_aggression_30_60 | 0 | 0 | OFM p.4; BIG p.3 |
| REFILL-STUDY,SIRES | RR-21 | implemented | test_p15_16a_sires.py::test_rr21_refill_literal_size_family_and_bracket | 0 | 0 | OD:HOLD_BOUNDARY_TICKS=8,HOLD_WINDOW_NS=30m |
| SAINT-AMT | RR-22 | implemented | test_p15_16a_saint.py::test_RR22_asia_session_not_ny_only | 0 | 0 | TRAP pp.3-10 |
| MEMBER-TWO-REASONS | RR-23 | implemented | test_p15_16a_saint.py::test_RR23_es_tape_required | 0 | 0 | OD:instrument transfer NQ from ES-202609 (K10 pp.7-8,12-13) |

## Plausibility

Density and pass rate per branch beside the source's stated frequency and page. Out-of-bound and zero-pass branches keep their diagnosis. Author-example reached-location is reported from the location stage.

| family | branch | eps | pass_rate | source frequency | page | in/out | diagnosis |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| JJ-TBR | judas_outbound | 0.4695752009184845 | 0.12224938875305623 | Once-per-session opening drive toward a selected 6-9 edge; two sides at most. | TBR pp.8-10 | in |  |
| JJ-TBR | judas_reversal | 1.7864523536165327 | 0.2461439588688946 | Once-per-session reversal structure (first sweep plus optional 09:40-09:50 cycle, two sides). 86.46% is the author's reversal-share histogram over 4,537 days, a plausibility reference not a scanner target. Capture 0.66-0.92 is the 1.33/1.66 table, not a pass-rate target. | JR p.70; JR p.23 | in |  |
| JJ-TBR | single_extended | 0.9621125143513203 | 0.20405727923627684 | EQ/quadrant contacts in the allowed continuation direction after an extended overnight. Bounded by qualifying contacts, not by every session. | TBR pp.12-14, 24 | in |  |
| JJ-TBR | single_purged | 0.17393800229621126 | 0.24752475247524752 | 09:40-09:50 add/continuation after overnight liquidity is purged. Bounded by qualifying contacts in that window. | TBR pp.12-15; E3 | in |  |
| JJ-TBR | internal_rotation | 0.9781859931113662 | 0.198943661971831 | In-value rotations at EQ/quadrants with confirmation. Touch EQ is not a trade (JR p.3). Bounded by qualifying contacts. | TBR p.24; JR p.3 | in |  |
| JJ-TBR | extension_reaction | 0.5809414466130884 | 0.1373517786561265 | First touch of the 1.33-1.66 band after 10:00, one side per band. Bounded by qualifying band contacts. | TBR p.21; JR pp.23-26; RR-01 | in |  |
| JJ-TBR | other_session | 7.50918484500574 | 0.012384374283311673 | London box 02:00-03:00 ET traded 03:00-06:00. At most one pass per side per session. Episodes bounded by distinct quadrant/box/band contacts. A session with no sweep has no pass. | JR pp.50, 63-64; RR-04 | in |  |
| JJ-TBR | timed_pzone_reversal | 0.006314580941446613 | 1.0 | Fixture-limited, no population bound. Proprietary P-zone generator unknown (F17, RR-05). Report printed-zone fixture count. Do not invent a generator. | JR pp.16-18; F17; RR-05 | in |  |
| GB-FAIL | london_box | 1.0 | 0.4873708381171068 | London-low A1 is a named sequence, not a daily default. | GB NG 2099513366326730859; RR-11; F06 A1 | in |  |
| GB-FAIL | asia_box | 1.0 | 0.5430539609644087 | Asia-high failure short, no TDO required. Histogram must show Asia entries. | GB pp.16, 19, 27; F06 A2 | in |  |
| GB-FAIL | asia_tdo_case | 1.0 | 0.3685419058553387 | Literal 5-minute close below TDO after Asia-high sweep. | GB pp.19, 27 | in |  |
| GB-FAIL | prior_day_level | 1.9799081515499426 | 0.28153087851551173 | PDL/PDH sweep and 5-minute close. Both sides. Overnight eligible. | GB pp.25, 48, 52-54; F06 A3 | in |  |
| GB-FAIL | nyam_box | 2.6538461538461537 | 0.2688730261734804 | At-level failure of the 9-10 box and sub-boxes. A+ is one or two per session across boxes, not several nyam passes. | GB pp.22, 38, 43, 58; RR-13 | in |  |
| GB-FAIL | previous_hour | 3.764638346727899 | 0.08981396767307105 | Completed-hour fail-back. Repeats allowed. Not several A+ per hour. | GB pp.37-38 | in |  |
| GB-FAIL | nwog | 1.17451205510907 | 0.07038123167155426 | NWOG Mondays. Destination after a midnight or NY-open failure, not a daily box. | GB pp.13, 14, 36, 37 | in |  |
| GB-FAIL | cash_open_reclaim_case | 1.0 | 0.3283582089552239 | 09:30 manipulation below, reclaim, retracement objective, stops at lows. Confirmation duration unpublished (OD 5-minute reclaim). | GB p.3 / p.40 | in |  |
| GB-FAIL | golden_pocket | 1.0 | 0.4121699196326062 | Down-leg pocket plus a real failure. Band touch alone is not the setup. | GB pp.23, 25, 51; RR-14 | out | Down-leg pocket plus a real failure. Band touch alone is not the setup. |
| GB-FAIL | ny_session_extreme | 1.9730195177956371 | 0.12743671806808263 | One dated afternoon sweep-and-fail of the running NY session low after 11:00, plus the text that session highs and lows are the table edges. | SOURCE_ADDITIONS_2026-09-15 trade 3; GB p.3 session highs and lows | in |  |
| GB-VWAP | source_long | 1.0 | 0.14006888633754305 | unstated. One dated continuation: close above London and Asia highs, retrace into VWAP, long, 30-point stop, 150-point caption result. VWAP is not drawn on later charts. Bound is the measured sequence rate, not a published frequency. | GB pp.33-34; SD04 keeps 150 and 100; 30-point stop is the example risk | in |  |
| GB-SCALP | golden_pocket_continuation | 0.9994259471871412 | 0.26766226306720275 | unstated as a daily rate. A4 is a NY pullback into the impulse pocket, long in bullish context. A scalp setup does not occur on 80% of sessions. | GB p.40 unpublished trigger; F06 A4 / RR-14 continuation long; 2026-09-11 ticket | in |  |
| SIRES | dom_rejection | 13.808840413318025 | 0.0 | A contact at a source-literal location (extreme, shelf, ledge, LVN, minor node), not an A+ trade. Author takes at most one or two A+ trades per session. | ABS p.6; DOM6-7 pp.3-7 | in |  |
| SIRES | absorption_reward_retest | 13.808840413318025 | 0.0014134275618374558 | A contact at a real extreme. 27% of absorptions fail without the three-tick reward. Passes are the setups among those contacts. | ABS pp.3-7 | in |  |
| SIRES | stop_four_stage | 13.808840413318025 | 0.16641030970692164 | Three-tick replenishment is a minimum filter at a defended level. One or two ticks is the fake-out zone. Passes are the setups among source-literal contacts. | STOP pp.10, 14 | in |  |
| SIRES | footprint_confirmed_reaction | 13.808840413318025 | 0.0004157139887757223 | Footprint flag 3-4x at a valid level. Contacts are source-literal locations, not A+ trades. | FP8 p.5; FP9 pp.4-7 | in |  |
| SIRES | vwap_deviation_fade | 13.808840413318025 | 0.012388276865516525 | Trades beyond the 1 band, ideally at 2, only with absorption. Contacts are VWAP-band touches, not A+ trades. | VWAP p.4 | in |  |
| SIRES | ofm_aggressive | 15.466130884041332 | 0.0 | an A++ a handful of times a month. Short-gamma permission is not observable in Phase 1.5. Combined verdict stays unknown when gamma is missing; location and later stages are still evaluated when their operands exist. The source gives no contact-per-session density. | OFM p.4; BIG p.14 | out | OFM p.4: OFM p.4 states an A++ a handful of times a month. That is an A++-trade frequency, not a contact-per-session density. The B0.2 scan enumerates contacts at source-literal locations. No source page states a contact density, so the registry keeps the source-grounded one-decision-per-session bound [1, 1] and episode_kind session_unknown. After ruling (a) the scan no longer stops at the unknown gamma context, so it enumerates every source-literal contact and the observed density lands above [1, 1]. That is reported as an out-of-bound finding with this justification; the bound is not widened to make the gate pass. |
| SIRES | ofm_passive | 13.808840413318025 | 0.0 | Squeeze fails with no aggression at the failure. Rarer than the aggressive OFM. Contacts at source-literal locations. | OFM p.14 | in |  |
| SIRES | clean_squeeze | 13.808840413318025 | 0.008522136769902306 | A squeeze with no failure: fast, real aggression, no retest, no false start. At most one or two A+ trades per session among source-literal contacts. | CONT p.11 | in |  |
| SIRES | balance_failure_fade | 27.61768082663605 | 0.0 | Balance fade in long gamma about 80% of the time is a regime share, not a pass rate or a contact density. Long-gamma permission is not observable in Phase 1.5. Combined verdict stays unknown when gamma is missing; location and later stages are still evaluated when their operands exist. The source gives no contact-per-session density. | BIG p.14 | out | BIG p.14: BIG p.14 states the balance fade in long gamma about 80% of the time. That is a regime-share frequency, not a contact-per-session density. The B0.2 scan enumerates contacts at source-literal locations. No source page states a contact density, so the registry keeps the source-grounded one-decision-per-session bound [1, 1] and episode_kind session_unknown. After ruling (a) the scan no longer stops at the unknown gamma context, so it enumerates every source-literal contact and the observed density lands above [1, 1]. That is reported as an out-of-bound finding with this justification; the bound is not widened to make the gate pass. |
| SIRES | defended_band_continuation | 13.808840413318025 | 0.16599459571814593 | A retest of an already-defended band. Contacts at source-literal locations, not A+ trades. | NYAM pp.4-5; CONT pp.4-10 | in |  |
| SIRES | kg1_retest | 0.0 | 0.0 | KG1 engine unpublished. Phase 1.5 has no supplied KG1 record, so the branch is empty. | NYAM pp.8-9 | in |  |
| SIRES | microbalance_break | 0.000574052812858783 | 0.0 | P15-05 F3 microbalances. Qualifying breakouts, not every 1-minute bar. | K2345 pp.4-7 | in |  |
| SAINT-AMT | continuation_retest | 1.9052812858783008 | 0.02771919252786984 | unstated |  | in |  |
| SAINT-AMT | trapped_buyers_retest | 1.9052812858783008 | 0.033142512805061766 | unstated |  | in |  |
| SAINT-AMT | failed_auction_return | 0.4368541905855339 | 0.17082785808147175 | unstated |  | in |  |
| SAINT-AMT | poc_traversal | 0.9845005740528129 | 0.36443148688046645 | 80 percent that price runs all the way to the far extreme, 20 percent that it simply ranges inside instead |  | in |  |
| MEMBER-TWO-REASONS | resistance_short | 1.0 | 0.25889781859931116 | unstated |  | in |  |
| MEMBER-TWO-REASONS | planned_return_long | 1.0 | 0.27152698048220436 | unstated |  | in |  |
| KEANI-OPEN-ABOVE-VALUE | source_long | 1.0 | 0.0 | unstated; B0.1 reference density 39 of 1695 A-period observations |  | in |  |
| REFILL-STUDY | touch_record | 456.58381171067737 | 0.0455813590924464 | about 175 touches per session; 42% of touches hold | REF p.5 (sixty, eighty, a hundred contracts in seconds); REF p.8 (41152 touches / 235 sessions = 175; 42% hold) | out | REF pp.5-8: REF p.8 prints 42% hold on 41152 NQ and MNQ touches over 235 RTH sessions Dec 24-Nov 25. The hold tick cutoff is not printed. Phase 1.5 labels hold with OD HOLD_BOUNDARY_TICKS=8 inside 30 minutes on NQ only, on 15 calendar sessions that are not that 235-session window. The bound stays at 175 and 42%. The observed hold rate is the OD label on this slice, not a rewrite of the paper. |
| GB-FAIL | prior_week_level | 2.0 | 0.1148105625717566 | Previous weekly candle's extremes (PWH/PWL) as sweep-and-reclaim references, both sides, one reference lifecycle per level per week. The page names the level set and dates three uses; it states no frequency, so the bound is the structural one: at most one episode per side per session. | GB p.31 (SD03 addendum); 2025-11-19, 2026-04-23, 2026-09-15; frequency unstated | in |  |

Author-example reached-location and detected counts are in AUTHOR_EXAMPLE_REPLAY.json. Management stays unmeasured where the author's size and amendment tape is unpublished.

## Author examples: reached location and detected, per family

| family | examples | reached_location | detected | data_unavailable |
| --- | ---: | ---: | ---: | ---: |
| GB-FAIL | 16 | 13 | 0 | 3 |
| GB-FAIL / GB-SCALP | 1 | 0 | 0 | 1 |
| JJ-TBR | 26 | 15 | 2 | 0 |
| MEMBER-TWO-REASONS | 1 | 0 | 0 | 1 |
| SAINT-AMT | 2 | 2 | 0 | 0 |
| SIRES | 10 | 1 | 0 | 0 |

