# P15-16A family report

B0.2 source-fidelity baseline over the native calendar. Faithful disagreements against the author are not claimed.

Job files are jobs/<date>/<branch>.json.gz. KEANI-OPEN-ABOVE-VALUE:branch:source_long collides with GB-VWAP:branch:source_long; no KEANI job file exists. B0.2 is not measured for KEANI. The runner declared 39*1742=67938 jobs; distinct gzip files on disk are fewer by one branch.

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| GB-FAIL | B0.2 | 26997 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/e76de3546ba24121/attempt-0001 |
| GB-SCALP | B0.2 | 1679 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/e76de3546ba24121/attempt-0001 |
| GB-VWAP | B0.2 | 1742 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/e76de3546ba24121/attempt-0001 |
| JJ-TBR | B0.2 | 25932 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/e76de3546ba24121/attempt-0001 |
| KEANI-OPEN-ABOVE-VALUE | B0.2 | not_measured | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/e76de3546ba24121/attempt-0001 |
| MEMBER-TWO-REASONS | B0.2 | 3484 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/e76de3546ba24121/attempt-0001 |
| REFILL-STUDY | B0.2 | 456448 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/e76de3546ba24121/attempt-0001 |
| SAINT-AMT | B0.2 | 11584 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/e76de3546ba24121/attempt-0001 |
| SIRES | B0.2 | 44720 | not claimed | integration | /workspace/implementation/reports/research-work/P15-16A/e76de3546ba24121/attempt-0001 |

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
