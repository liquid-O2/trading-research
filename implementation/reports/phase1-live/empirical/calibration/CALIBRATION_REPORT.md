# Phase 1 source calibration report

Calibration date: **2026-09-12**. Matrix SHA-256: `613fc28c6a2e4e5ce7e6ee94a7298dab9e1e69fbac36e1510607e2bd843910e3`. This report covers the existing M01–M12 method pack through Stage 1 source interpretation and native/source-fit controls. The machine-readable ledger is [calibration_matrix.json](calibration_matrix.json).

Every retained source case has an explicit disposition. The source catalog contains 22 cases and 17 configurations; all 22 have `historical_candidate=false`. The 50 catalog branches are accounted for with traceable source-page evidence and, where a deterministic control was necessary, a named assumption. No native control, cross-instrument geometry comparison, schematic, later annotation, process example or arithmetic ladder is counted as a source-faithful historical trade.

Source-case agreement is reported separately from historical discovery. The source-case discovery population is therefore `n=null`, `search_completed=false`, and `faithful_disagreements=null`; this records a calibration exclusion rather than a completed scan with zero candidates.

## Provenance and scope

| artifact | path | SHA-256 | purpose |
| --- | --- | --- | --- |
| source_catalog | `/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json` | `b730c93d4b9e8b8e4cc07d82efaf2298dcf2fe49c146314c386b88a9b6a07602` | retained input/evidence |
| accepted_source_case_review | `/workspace/implementation/validation/phase1-completion/source-case-review.json` | `5c85a2183daaca29819cd129e8c2867c1e04060ad408bf072ea21022cd254652` | retained input/evidence |
| native_clock_coverage | `/workspace/implementation/validation/phase1-completion/native-clock-coverage.json` | `93b817a2f3fb28830c4caf108ecb981252eaced72ccca1890edc31d42df01137` | retained input/evidence |
| accepted_chart_verification | `/workspace/implementation/reports/phase1-live/methods/CHART_VERIFICATION.md` | `6c559c6f415160f537200f3137654ae1d69b4289879820d6af305052f885bba2` | retained input/evidence |
| source_recheck | `/workspace/implementation/reports/phase1-live/methods/SOURCE_RECHECK.md` | `96784d7479d8150f65d37eb8488467f647c44a2af3fb33d3c50060f9b36f77ce` | retained input/evidence |
| reconstruction_readme | `/workspace/implementation/reports/phase1-live/methods/reconstructions/README.md` | `31e384ee5a8a98015ed57f50ec5985242022635ba2ddff23ff4407e03bdeffb1` | retained input/evidence |
| reconstruction_v2_readme | `/workspace/implementation/reports/phase1-live/methods/reconstructions/v2/README.md` | `8aa7e766bb393006c36f373f00ebfb46b8154f793510dd10c06bab84910323e6` | retained input/evidence |

The source catalog itself retains each source PDF path, page count and digest. Case rows in the matrix preserve the original catalog record, source image/page links, source field status, profiles, later annotations and missing fields. Configuration rows preserve every setting value, status (`fact`, `inference`, `unknown`, or `source_conflict`), reason and page reference.

## Calibration dispositions

| method | cases | branches | source-faithful selectors | disposition |
| --- | ---: | ---: | ---: | --- |
| `JJ-TBR` | 4 | 8 | 0 | partial_source_literals; no historical source-faithful entry cohort |
| `GB-FAIL` | 1 | 8 | 0 | source_sequence_partial_comparison_only |
| `GB-VWAP` | 1 | 1 | 0 | comparison_only_source_fidelity_unavailable |
| `GB-SCALP` | 2 | 2 | 0 | description_only_no_automatic_admission |
| `SIRES` | 5 | 12 | 0 | many_literal_observations; source_faithful_entry_unavailable |
| `SAINT-AMT` | 2 | 4 | 0 | source_routes_only_no_dated_native_selector |
| `MEMBER-TWO-REASONS` | 2 | 2 | 0 | source_reasons_only_no_dated_native_selector |
| `KEANI-OPEN-ABOVE-VALUE` | 1 | 1 | 0 | schematic_sequence_only |
| `REFILL-STUDY` | 1 | 2 | 0 | observation_only_no_source_faithful_order_replay |
| `JETBUNDLE-STATES` | 1 | 5 | 0 | process_state_observation_only |
| `STOIC-DATA` | 1 | 2 | 0 | process_only_no_entry_strategy |
| `STOIC-RISK` | 1 | 3 | 0 | arithmetic_only_validation_missing |

A source-faithful selector count of zero is intentional where an indispensable source definition, dated native identity, or execution record is missing. This is a source calibration result; implementation holes are not silently converted to favorable defaults.

## Retained source-case ledger

| # | case | method | mode | source pages | date | instrument | timeframe | decision interval | source-case agreement | disposition | missing evidence |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `JJ-range-control-2026-02-24` | `JJ-TBR` | `native_control` | TBR:4, TBR:21 | 2026-02-24 (inference) | NQH6 (inference) | {"kind":"time","minutes":1} (inference) | {"start_et":"06:00","end_et":"09:00"} (fact) | `native_control_verified` | `native_control_only` | source_trade_decision |
| 2 | `JJ-profiles-2026-06-12` | `JJ-TBR` | `source_illustration` | JR:4 | 2026-06-12 (fact) | NQ (fact) | null (unknown) | null (unknown) | `structure_preserved_settings_unknown` | `source_structure_preserved_native_profiles_settings_unknown` | exact_profile_windows, native_contract, timeframe, decision_timestamp, VA_algorithm |
| 3 | `JJ-orderblock-long` | `JJ-TBR` | `source_illustration` | TBR:27, TBR:28 | None (unknown) | None (unknown) | {"kind":"time","minutes":3} (fact) | null (unknown) | `source_sequence_retained` | `source_sequence_only_dated_native_execution_unavailable` | date, native_contract, event_members |
| 4 | `JJ-orderblock-short-mirror` | `JJ-TBR` | `synthetic_fixture` | TBR:27, TBR:28 | None (unknown) | None (unknown) | {"kind":"time","minutes":3} (inference) | null (unknown) | `synthetic_mirror_only` | `synthetic_mirror_control_only` | dated_short_source_case, date, native_contract, event_members |
| 5 | `GB-FAIL-2025-11-20` | `GB-FAIL` | `source_illustration` | GB:31, GB:43 | 2025-11-20 (fact) | MNQZ2025 (fact) | {"kind":"time","minutes":2} (fact) | {"start_et":"08:00","end_et":"11:02","timezone":"America/New_York"} (fact) | `sequence_correction_preserved` | `source_sequence_preserved_comparison_geometry_only` | actual_fill_time, actual_fill_ledger, native_MNQ_data |
| 6 | `GB-VWAP-2026-02-24` | `GB-VWAP` | `source_illustration` | GB:33, GB:34 | 2026-02-24 (fact) | None (unknown) | {"kind":"time","minutes":1} (inference) | {"start_et":"08:30","end_et":"10:25","timezone":"America/New_York"} (fact) | `frozen_comparison_reproduced` | `comparison_only_source_reset_basis_and_fill_unknown` | display_native_contract, VWAP_reset, VWAP_basis, session_clocks, actual_fill_time |
| 7 | `GB-SCALP-bearish` | `GB-SCALP` | `source_illustration` | GB:40 | None (unknown) | None (unknown) | null (unknown) | null (unknown) | `source_description_retained` | `source_description_only_no_repeatable_selector` | native_contract, exact_trading_date, entry_time, fill_ledger, size_quantity, repeatable_entry_and_exit_rules |
| 8 | `GB-SCALP-bullish` | `GB-SCALP` | `source_illustration` | GB:40 | None (unknown) | None (unknown) | null (unknown) | null (unknown) | `source_description_retained` | `source_description_only_no_repeatable_selector` | native_contract, exact_trading_date, entry_time, fill_ledger, size_quantity, repeatable_entry_and_exit_rules |
| 9 | `SIRES-overnight-profile` | `SIRES` | `source_illustration` | MAMT:14, MAMT:15, MAMT:16 | None (unknown) | None (unknown) | null (unknown) | {"start_et_previous_day":"18:00","end_et":"09:30","timezone":"America/New_York"} (fact) | `source_window_bound_native_control` | `source_sequence_and_native_clock_control_settings_unknown` | date, native_contract, VA_algorithm, exact_LVN_selection |
| 10 | `SIRES-same-candle-POC` | `SIRES` | `source_illustration` | FP9:5, FP9:7, FP8:6 | None (unknown) | None (unknown) | null (unknown) | null (unknown) | `schematic_and_native_control_separated` | `source_schematic_native_controls_separated` | date, native_contract, exact_snapshot_times, source_POC_tie_rule |
| 11 | `STOP-confirmed` | `SIRES` | `source_illustration` | STOP:11, STOP:12 | None (unknown) | EPZ25 (fact) | {"kind":"time","minutes":1} (fact) | null (unknown) | `source_stages_retained` | `source_stages_only_non_native_execution_record` | exact_dated_event_interval, ES_full_depth, actual_execution_record |
| 12 | `STOP-early` | `SIRES` | `source_illustration` | STOP:13 | None (unknown) | EPZ25 (fact) | {"kind":"time","minutes":1} (fact) | null (unknown) | `early_attempt_retained` | `early_loss_attempt_preserved_no_fill` | exact_date_year, event_interval, actual_execution_record |
| 13 | `SIRES-losses-2026-07-23` | `SIRES` | `source_illustration` | ANAT:1, ANAT:6, ANAT:8, ANAT:9 | 2026-07-23 (fact) | NQ (fact) | null (unknown) | {"start_display_clock":"10:14","end_display_clock":"10:32","timezone":null} (fact) | `losses_and_source_conflict_retained` | `source_attempt_outcomes_only_conflict_retained` | exact_order_fill_times, price_levels, chart_timezone, bar_size |
| 14 | `SAINT-break-retest` | `SAINT-AMT` | `source_illustration` | TRAP:7, TRAP:3, TRAP:4, TRAP:5, TRAP:9 | None (unknown) | None (unknown) | null (unknown) | null (unknown) | `source_route_retained` | `source_route_only_date_band_and_native_flow_unknown` | date, native_contract, exact_band, source_footprint_configuration |
| 15 | `SAINT-failed-auction` | `SAINT-AMT` | `source_illustration` | AMTL:10, AMTL:8, AMTL:9 | None (unknown) | None (unknown) | null (unknown) | null (unknown) | `source_route_retained` | `source_route_only_schematic_no_dated_control` | date, native_contract, exact_interval, source_control_interpretation |
| 16 | `MEMBER-resistance` | `MEMBER-TWO-REASONS` | `source_illustration` | K10:7 | None (unknown) | ES (fact) | {"execution_minutes":2,"context_minutes":5} (fact) | null (unknown) | `independent_reasons_retained` | `source_reasons_only_date_band_and_fill_unknown` | date, native_contract, band_coordinates, fill_times |
| 17 | `MEMBER-return` | `MEMBER-TWO-REASONS` | `source_illustration` | K10:8 | None (unknown) | ES (fact) | null (unknown) | null (unknown) | `source_return_plan_retained` | `source_return_plan_only_date_band_and_fill_unknown` | date, native_contract, band_coordinates, fill_times |
| 18 | `KEANI-open-above` | `KEANI-OPEN-ABOVE-VALUE` | `source_illustration` | AVG:22 | None (unknown) | None (unknown) | null (unknown) | null (unknown) | `schematic_sequence_retained` | `schematic_sequence_only_value_and_imbalance_unknown` | date, native_contract, VA_configuration, imbalance_configuration, exact_decision_time |
| 19 | `REFILL-selected-order` | `REFILL-STUDY` | `source_illustration` | REF:7, REF:12, OFM:18 | None (unknown) | NQ (fact) | null (unknown) | null (unknown) | `selected_order_record_retained` | `touch_and_order_observation_only_queue_and_ledger_unknown` | source_model_and_zone_selector, individual_selected_order_ledger, date, native_contract |
| 20 | `JETBUNDLE-state-process` | `JETBUNDLE-STATES` | `source_illustration` | MATH:3, MATH:10, MATH:11 | None (unknown) | AAPL (fact) | null (unknown) | null (unknown) | `process_observation_retained` | `process_state_observation_only_classifier_unknown` | exact_native_state_observations, unpublished_classifier, full_participation_events |
| 21 | `STOIC-process` | `STOIC-DATA` | `source_illustration` | DATA:3, DATA:4 | None (unknown) | None (unknown) | null (unknown) | null (unknown) | `research_process_retained` | `research_process_only_no_entry_strategy` | private_contemporaneous_research_records |
| 22 | `STOIC-risk` | `STOIC-RISK` | `source_illustration` | DATA:7, DATA:8 | None (unknown) | None (unknown) | null (unknown) | null (unknown) | `risk_illustration_retained` | `printed_arithmetic_only_validation_and_mc_unknown` | validation_trade_journal, source_Monte_Carlo_records |

The decision interval column is the visible or declared observation interval. It is never an exact exchange fill interval unless the source supplies one; in these cases no such fill ledger is present. The GB-November source position is at the high sweep before later MSS/FVG annotations. The SIRES nine-attempt case retains the plotted sequence `L,L,W,L,W,W,L,L,W` and the conflicting “first four hurt” caption.

## Versioned source configurations

| configuration | author | version | scoped methods | settings by evidence status | source refs |
| --- | --- | --- | --- | --- | --- |
| `jumbo-published-geometry` | Jumbo | `2.0.0` | JJ-TBR | facts: range_clock, orderblock_bar_minutes, absorption_body_max, absorption_volume_min, absorption_history; unknown: profile_va_policy | JR:4, JR:41, TBR:27, TBR:35, TBR:4 |
| `jumbo-sessionstat` | Jumbo | `2.0.0` | JJ-TBR | facts: platform, timeframe_dependence; unknown: engine | SS:7 |
| `gb-nov20-sweep` | Green Bird | `2.0.0` | GB-FAIL | facts: bar_minutes, display_symbol, entry_sequence, observed_position_price, mss_fvg_role; unknown: fill_time | GB:43 |
| `gb-vwap-continuation` | Green Bird | `2.0.0` | GB-VWAP | facts: entry_sequence, stop_points; inference: prior_comparison; unknown: reset, price_basis, asia_london_windows | GB:33 |
| `gb-discretionary-scalp` | Green Bird | `2.0.0` | GB-SCALP | facts: bearish_case, bullish_case; unknown: automatic_entry | GB:40 |
| `sires-overnight` | Sires | `2.0.0` | SIRES | facts: window, reference_roles, MPOC | MAMT:14, MAMT:15, MAMT:16 |
| `sires-vwap-illustration` | Sires | `2.0.0` | SIRES | facts: anchor, offset, timeframe, wait_for_timeframe_close, source_price_label, enabled_multipliers; unknown: price_basis, reset_clock; conflict: discussed_multiplier | VWAP:8 |
| `sires-va40` | Sires | `2.0.0` | SIRES | facts: fraction; unknown: algorithm | C3:7 |
| `saint-va68` | Saint | `2.0.0` | SAINT-AMT | facts: fraction; unknown: algorithm | RTVP:4 |
| `vp-lesson-va70` | Sires | `2.0.0` | SIRES | facts: fraction; unknown: algorithm | AMT1:5, MAMT:5 |
| `sires-process` | Sires | `2.0.0` | SIRES | facts: confidence_scale, confidence_observation, review_example_sessions, excursion_collection_trades; inference: retained_categories | C1:6, C2:4 |
| `sires-stop-sequence` | Sires | `2.0.0` | SIRES | facts: stages, bars_nq_walkthrough; unknown: range_construction | STOP:10, STOP:12, STOP:8 |
| `member-two-reasons` | Member | `2.0.0` | MEMBER-TWO-REASONS | facts: reasons, target_R | K10:7, K10:8 |
| `stoic-process-risk` | Stoic | `2.0.0` | STOIC-DATA, STOIC-RISK | facts: observation_unit, macro_status; unknown: execution_journal | DATA:3, DATA:5, DATA:7, DATA:8 |
| `keani-open-above-blueprint` | Keani | `2.0.0` | KEANI-OPEN-ABOVE-VALUE | facts: sequence; unknown: value_engine, imbalance_configuration | AVG:22 |
| `refill-observation-study` | Refill | `2.0.0` | REFILL-STUDY | facts: observation_unit, illustrated_sequence; unknown: zone_selector, execution_records | REF:12, REF:7 |
| `jetbundle-participation-process` | Jetbundle | `2.0.0` | JETBUNDLE-STATES | facts: participation_actions, observation_unit; unknown: classifier | MATH:10, MATH:11, MATH:3 |

Unknown settings stay unknown. Examples that remain unresolved include profile value-area expansion/tie construction, Green Bird VWAP reset and basis, source session bounds, source-specific LVN selection, exact state thresholds, and private order/validation records. The Sires VWAP input conflict (visible multipliers 1 and 2 versus prose/caption 2.5) is retained as `source_conflict`.

## Branch rule inventory

| method | branch | calibration disposition | source case(s) | evidence | explicit assumption(s) | missing/limitation |
| --- | --- | --- | --- | --- | --- | --- |
| `JJ-TBR` | `judas_outbound` | `source_faithful_unavailable` | `JJ-range-control-2026-02-24`, `JJ-profiles-2026-06-12`, `JJ-orderblock-long`, `JJ-orderblock-short-mirror` | TBR:8, TBR:9 | none | source direction and selected outbound entry/exit are not published. |
| `JJ-TBR` | `judas_reversal` | `source_faithful_unavailable` | `JJ-range-control-2026-02-24`, `JJ-profiles-2026-06-12`, `JJ-orderblock-long`, `JJ-orderblock-short-mirror` | TBR:8, TBR:9, TBR:27 | `A-JJ-RANGE-CONTROL-FEB24` | source exact edge depth, context, confirmation and dated decision/fill are absent. |
| `JJ-TBR` | `single_extended` | `source_faithful_unavailable` | `JJ-range-control-2026-02-24`, `JJ-profiles-2026-06-12`, `JJ-orderblock-long`, `JJ-orderblock-short-mirror` | TBR:12, TBR:13, TBR:24 | none | author-exact extended threshold, purge chronology and source-selected entry are absent. |
| `JJ-TBR` | `single_purged` | `source_faithful_unavailable` | `JJ-range-control-2026-02-24`, `JJ-profiles-2026-06-12`, `JJ-orderblock-long`, `JJ-orderblock-short-mirror` | TBR:12, TBR:15, TBR:24 | none | purge ledger and dated source selection are absent. |
| `JJ-TBR` | `internal_rotation` | `source_faithful_unavailable` | `JJ-range-control-2026-02-24`, `JJ-profiles-2026-06-12`, `JJ-orderblock-long`, `JJ-orderblock-short-mirror` | JR:3, JR:38, JR:43 | none | location selection, context, confirmation and source target are not reproducibly recorded. |
| `JJ-TBR` | `extension_reaction` | `source_faithful_unavailable` | `JJ-range-control-2026-02-24`, `JJ-profiles-2026-06-12`, `JJ-orderblock-long`, `JJ-orderblock-short-mirror` | TBR:20, TBR:21, JR:23 | none | parent selection, reaction confirmation and decision record are absent. |
| `JJ-TBR` | `other_session` | `source_faithful_unavailable` | `JJ-range-control-2026-02-24`, `JJ-profiles-2026-06-12`, `JJ-orderblock-long`, `JJ-orderblock-short-mirror` | TBR:7, JR:46, JR:50 | none | source clock, case identity and selection are not established. |
| `JJ-TBR` | `timed_pzone_reversal` | `source_faithful_unavailable` | `JJ-range-control-2026-02-24`, `JJ-profiles-2026-06-12`, `JJ-orderblock-long`, `JJ-orderblock-short-mirror` | JR:53, JR:54, JR:55 | none | P-zone formula, selected zone, event clock and exact entry are unpublished. |
| `GB-FAIL` | `nyam_box` | `source_faithful_unavailable` | `GB-FAIL-2025-11-20` | GB:23, GB:40 | none | no dated source case supplies the full NYAM selector and fill. |
| `GB-FAIL` | `previous_hour` | `source_faithful_unavailable` | `GB-FAIL-2025-11-20` | GB:27, GB:31 | none | source hour selection, confirmation and fill are not recoverable. |
| `GB-FAIL` | `asia_tdo_case` | `source_faithful_unavailable` | `GB-FAIL-2025-11-20` | GB:30, GB:31 | none | Asia/TDO clocks and source admission remain incomplete. |
| `GB-FAIL` | `prior_day_level` | `source_faithful_unavailable` | `GB-FAIL-2025-11-20` | GB:25, GB:32 | none | source level/fill and exact five-minute admission are unavailable. |
| `GB-FAIL` | `prior_week_level` | `source_faithful_unavailable` | `GB-FAIL-2025-11-20` | GB:34, GB:35 | none | prior-week identity, date, execution and confirmation are absent. |
| `GB-FAIL` | `prior_month_level` | `source_faithful_unavailable` | `GB-FAIL-2025-11-20` | GB:34, GB:35 | none | prior-month identity, date, execution and confirmation are absent. |
| `GB-FAIL` | `cash_open_reclaim_case` | `source_faithful_unavailable` | `GB-FAIL-2025-11-20` | GB:38, GB:40 | none | source confirmation duration and exact fill are unspecified. |
| `GB-FAIL` | `mss_fvg_refinement` | `source_sequence_only` | `GB-FAIL-2025-11-20` | GB:31, GB:43 | none | the source figure does not establish MSS/FVG as a prerequisite; exact mechanics/fill remain unknown. |
| `GB-VWAP` | `source_long` | `comparison_only` | `GB-VWAP-2026-02-24` | GB:33, GB:34 | `A-GB-VWAP-PREV18-HLC3` | source reset, basis, clocks, contract and fill are unknown; use A-GB-VWAP-PREV18-HLC3 only as the frozen comparison. |
| `GB-SCALP` | `bearish_small_scalp` | `source_description_only` | `GB-SCALP-bearish`, `GB-SCALP-bullish` | GB:40 | none | publication is not entry time and no general trigger, size, fill or exit algorithm is given. |
| `GB-SCALP` | `bullish_discount_pullback` | `source_description_only` | `GB-SCALP-bearish`, `GB-SCALP-bullish` | GB:40 | none | publication is not entry time and no general trigger, size, fill or exit algorithm is given. |
| `SIRES` | `dom_rejection` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | DOM6:3, DOM7:3 | none | source DOM scope, side-specific sequence, dated level and execution record are absent. |
| `SIRES` | `absorption_reward_retest` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | ABS:5, ABS:6, ABS:13 | none | reward window, source CVD reference and dated fill are unresolved. |
| `SIRES` | `stop_four_stage` | `source_sequence_only` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | STOP:6, STOP:10, STOP:12 | none | the source stages are retained, but exact dated native execution/depth and NQ transfer are unavailable. |
| `SIRES` | `footprint_confirmed_reaction` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | FP9:4, FP9:5, FP9:7 | `A-SIRES-FLOW-CONTROLS` | FP9 is a schematic; exact snapshot times, tie rule, source level and fill are absent. |
| `SIRES` | `vwap_deviation_fade` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | VWAP:3, VWAP:8 | none | source reset/basis and entry records are not established; settings illustration is not a trade. |
| `SIRES` | `ofm_aggressive` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | OFM:3, OFM:13, BIG:7 | none | full catalyst/release/failure/refill identity and source execution are missing. |
| `SIRES` | `ofm_passive` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | OFM:14, OFM:15 | none | passive branch is described but no reproducible source zone/order/fill ledger exists. |
| `SIRES` | `clean_squeeze` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | CONT:10, CONT:11, OFM:5 | none | source catalyst, timing, confirmation and fill are not recoverable. |
| `SIRES` | `balance_failure_fade` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | BIG:14, BIG:15, BIG:18 | none | source balance/failed area and decision record are absent. |
| `SIRES` | `defended_band_continuation` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | NYAM:4, K18:7, CONT:4, ANAT:7 | `A-SIRES-OVERNIGHT-JUN12` | band identity, side-specific refresh sequence and flip branch are unpublished. |
| `SIRES` | `microbalance_break` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | K2345:4, K2345:7 | none | source-selected box and exact decision/fill are unavailable. |
| `SIRES` | `kg1_retest` | `source_faithful_unavailable` | `SIRES-overnight-profile`, `SIRES-same-candle-POC`, `STOP-confirmed`, `STOP-early`, `SIRES-losses-2026-07-23` | NYAM:8, NYAM:9, K10:9 | none | KG1 level engine and trailing algorithm are expressly not fully published. |
| `SAINT-AMT` | `continuation_retest` | `source_faithful_unavailable` | `SAINT-break-retest`, `SAINT-failed-auction` | WIC:7, WIC:10, TRAP:5 | none | dated source balance, band, clock and flow join are missing. |
| `SAINT-AMT` | `trapped_buyers_retest` | `source_faithful_unavailable` | `SAINT-break-retest`, `SAINT-failed-auction` | TRAP:3, TRAP:5, TRAP:7, TRAP:9 | none | source date, native band, exact retest and fill are absent. |
| `SAINT-AMT` | `failed_auction_return` | `source_faithful_unavailable` | `SAINT-break-retest`, `SAINT-failed-auction` | AMTL:8, AMTL:9, AMTL:10 | none | schematic pages do not provide a dated native interval or exact control observation. |
| `SAINT-AMT` | `poc_traversal` | `source_faithful_unavailable` | `SAINT-break-retest`, `SAINT-failed-auction` | RTVP:5, RTVP:8, AMTL:10 | none | source POC passage/timing/target and fill are not recoverable. |
| `MEMBER-TWO-REASONS` | `resistance_short` | `source_faithful_unavailable` | `MEMBER-resistance`, `MEMBER-return` | K10:5, K10:7 | none | date, native contract, band coordinates, complete contact and fill are absent. |
| `MEMBER-TWO-REASONS` | `planned_return_long` | `source_faithful_unavailable` | `MEMBER-resistance`, `MEMBER-return` | K10:6, K10:8 | none | date, band coordinates, full prior-defense record and fill are absent. |
| `KEANI-OPEN-ABOVE-VALUE` | `source_long` | `source_faithful_unavailable` | `KEANI-open-above` | AVG:21, AVG:22 | none | schematic has no date/contract/VA or imbalance settings and no exact decision/fill. |
| `REFILL-STUDY` | `touch_record` | `observation_only` | `REFILL-selected-order` | REF:5, REF:7, REF:9 | none | source zone selector and complete touch/feature ledger are unavailable; no entry or return result is inferred. |
| `REFILL-STUDY` | `supplied_selected_order` | `observation_only` | `REFILL-selected-order` | REF:12, REF:16, OFM:18 | none | selected order, queue, fill, lifecycle and source cohort records are unavailable; this is not a trade replay. |
| `JETBUNDLE-STATES` | `B` | `process_observation_only` | `JETBUNDLE-state-process` | MATH:3, MATH:9, MATH:10 | `A-JETBUNDLE-NQ-SCOPE` | state thresholds and complete native participation records are unpublished. |
| `JETBUNDLE-STATES` | `A` | `process_observation_only` | `JETBUNDLE-state-process` | MATH:3, MATH:7, MATH:10 | `A-JETBUNDLE-NQ-SCOPE` | state thresholds, hidden depth/lifecycle and native source records are unavailable. |
| `JETBUNDLE-STATES` | `D` | `process_observation_only` | `JETBUNDLE-state-process` | MATH:3, MATH:6, MATH:10 | `A-JETBUNDLE-NQ-SCOPE` | state thresholds and native transition cohort are unavailable. |
| `JETBUNDLE-STATES` | `E` | `process_observation_only` | `JETBUNDLE-state-process` | MATH:3, MATH:8, MATH:10 | `A-JETBUNDLE-NQ-SCOPE` | state thresholds and native transition cohort are unavailable. |
| `JETBUNDLE-STATES` | `W` | `process_observation_only` | `JETBUNDLE-state-process` | MATH:3, MATH:5, MATH:10 | `A-JETBUNDLE-NQ-SCOPE` | complete cancellations/order identities are unavailable. |
| `STOIC-DATA` | `process_review` | `process_observation_only` | `STOIC-process` | DATA:3, DATA:4 | none | private contemporaneous journal and process-specific inclusion rules are absent; no entry strategy. |
| `STOIC-DATA` | `macro_application` | `process_observation_only` | `STOIC-process` | DATA:5, DATA:6 | none | custom series, lookbacks, weights, vintages, cycle classifier and thresholds are unpublished. |
| `STOIC-RISK` | `first` | `arithmetic_only` | `STOIC-risk` | DATA:7 | `A-STOIC-RISK-PRINTED-LADDER` | requires an already validated process; no entry or result is created. |
| `STOIC-RISK` | `second` | `arithmetic_only` | `STOIC-risk` | DATA:7 | `A-STOIC-RISK-PRINTED-LADDER` | heading says two-win activation while ladder raises risk after first; validation sample is missing. |
| `STOIC-RISK` | `reset_after_second_win` | `arithmetic_only` | `STOIC-risk` | DATA:7, DATA:8 | `A-STOIC-RISK-PRINTED-LADDER` | Monte Carlo and 100+ trade validation records are missing; no new simulation. |

The branch inventory is deliberately conservative:

- `comparison_only` is used only for the frozen Green Bird previous-18:00/HLC3 VWAP curve. The NQZ5/NQH6 controls and dated profile/flow controls are recorded as native geometry/observation controls, never source fills.
- `source_sequence_only` retains a sequence such as the GB high-sweep position or Sires four-stage sequence while withholding automatic entry admission when the exact selector/fill is absent.
- `source_description_only`, `observation_only`, `process_observation_only`, and `arithmetic_only` preserve the distinct non-entry units in the catalog. They cannot be turned into trade candidates by later market outcomes.
- Every branch has page-level source evidence. Comparison assumptions are resolved against the top-level assumption table and include explicit excluded claims. `proxy_as_faithful_allowed=false` for all 50 branches.

## Native and source-fit controls

| chart/control | chart SHA-256 | evidence | source-case agreement | rows/snapshot | interpretation boundary |
| --- | --- | --- | --- | --- | --- |
| `JJ-range-control-2026-02-24.png` | `bc5e120ca7296547e44c3b544f6a1ed0160b4d86238dee188ab5436f4a6c112b` | `/workspace/implementation/validation/phase1-completion/native-geometry.json` (`a84388870eb9ef96cc399153be3c52dd781e3b3ff99977958a82b137b15c63ac`) | native control only; no source fill or author detector inferred | native/comparison artifact | `historical_candidate=false`; no source fill inferred |
| `native-TPO-IB-2026-06-12.png` | `fea8413609ad7af084fb6356c9af020d54dbe1bf9192a7c3b130dd2bed04cc73` | `/workspace/implementation/validation/phase1-completion/native-geometry.json` (`a84388870eb9ef96cc399153be3c52dd781e3b3ff99977958a82b137b15c63ac`) | native control only; no source fill or author detector inferred | native/comparison artifact | `historical_candidate=false`; no source fill inferred |
| `native-composite-2026-06-12.png` | `efe74acd2156216833a2c1bbcd86bcd526c8200f74666ce330f330456bca5036` | `/workspace/implementation/validation/phase1-completion/native-geometry.json` (`a84388870eb9ef96cc399153be3c52dd781e3b3ff99977958a82b137b15c63ac`) | native control only; no source fill or author detector inferred | disjoint composite total 603210 | `historical_candidate=false`; no source fill inferred |
| `native-SIRES-overnight-2026-06-12.png` | `bcc4a63b1d3df622078252fa4910b71acc0a3ceff43ec5a131ce996a4f24729f` | `/workspace/implementation/validation/phase1-completion/native-geometry.json` (`a84388870eb9ef96cc399153be3c52dd781e3b3ff99977958a82b137b15c63ac`) | native control only; no source fill or author detector inferred | source unknowns retained | `historical_candidate=false`; no source fill inferred |
| `native-flow-2026-02-24.png` | `6da5c25d1a693245c36ff5159901019d6ee4da42132d6d13ef5f7cb02e66f7b3` | `/workspace/implementation/validation/phase1-completion/native-flow.json` (`2f114ff04f0f300b2cbc3921cbfe6564a9256a1eb3a62ff8a69ccd352ac2f829`) | native control only; no source fill or author detector inferred | 470 native footprint rows, same-candle POC change 0.00 | `historical_candidate=false`; no source fill inferred |
| `native-flow-2026-06-12.png` | `25956a307d19dcb5bf7038394f3fefd9ca33ad08ca271bc14fa67b044fa9cf4c` | `/workspace/implementation/validation/phase1-completion/native-flow.json` (`2f114ff04f0f300b2cbc3921cbfe6564a9256a1eb3a62ff8a69ccd352ac2f829`) | native control only; no source fill or author detector inferred | 793 native footprint rows, same-candle POC change 0.00 | `historical_candidate=false`; no source fill inferred |
| `native-flow-2026-07-23.png` | `43a96c5cd859fb2c5ad86d3ef5df99c5365c235d8dbe8997c22f63e5a9272b89` | `/workspace/implementation/validation/phase1-completion/native-flow.json` (`2f114ff04f0f300b2cbc3921cbfe6564a9256a1eb3a62ff8a69ccd352ac2f829`) | native control only; no source fill or author detector inferred | 431 native footprint rows, same-candle POC change 15.00 | `historical_candidate=false`; no source fill inferred |

Specific retained controls include:

- JJ 06:00–09:00 NQH6 range geometry (107-point width, complete one-minute membership) and five separate June 12 NQM6 profile windows. Selected range coverage is true; four cross-source profile windows retain coverage uncertainty. The 40% VA setting is sourced to Sires, not assigned to Jumbo.
- Green Bird November 20 MNQZ2025 two-minute source figure versus NQZ5 comparison geometry. The source line at 25301.75 is a displayed position in the high-sweep area; no NQ fill or return is used.
- Green Bird February 24 VWAP: one prior-18:00/HLC3 comparison at the retained 13 points. It reproduces the frozen curve; reset, basis, source clocks and fill remain unknown, and no new grid search is admitted.
- Sires June 12 overnight binding and dated NQ footprint controls. Native flow rows retain B/A/D/N side semantics and distinct developing/close snapshots. A same-candle POC relocation in a native control is not the FP9 source observation.
- Sires July 23 context for the nine displayed attempts. The native NQU6 one-minute window has complete coverage for its declared control; source timezone, bar size and fill clocks remain unknown.

## Visual reinspection and provenance

The existing accepted parent source-case review is reused through `source-case-review.json`; it records the 22-case visual review and its chart hashes. The calibration pass re-inspected source page renders and derived charts for the 20 cases indexed below, for identity, legibility, sequence labels and layout; the remaining accepted dispositions are reused. The lead additionally inspected the GB November20, GB February24 and Sires July23 source/native composite charts during integration. The sweep-entry/later-MSS distinction, unresolved VWAP settings, MNQ/NQ separation, and all nine July23 outcomes remain explicit. These visual checks make no method-performance claim.

| case | source render(s) available | derived chart SHA-256 | reinspection scope |
| --- | --- | --- | --- |
| `GB-FAIL-2025-11-20` | `GB:31` PDF page, `GB-43-figure.png` (`d62b380b61624a659988d42f545a4e96a811d7e4ee11c0b7f874d3d9621523e3`) | `5d75479ab54cada16015d2e0d9e54837e9b35ea6f475bb77d4e452ed13177c1b` | source identity, sequence and layout only |
| `GB-VWAP-2026-02-24` | `GB-33-figure.png` (`e11eea3d30c4d80f64a090f68f5e6eedc74d8d6b2379815b11fd6b7328d2bfa1`), `GB:34` PDF page | `bb99fcfca213e9eeef5afcb1c55a076664076cb985450c17049306fb14483be3` | source identity, sequence and layout only |
| `JJ-profiles-2026-06-12` | `JR-4-figure.png` (`3522da7d77508d15e96b5e1f739066523eb93e640204d508fceb7fd735a446d2`) | `f81c317b65bee8e4f49bfb93bc613e29c01148b9c7508b6d9b016d9f0de70f0b` | source identity, sequence and layout only |
| `SIRES-overnight-profile` | `MAMT-14-page.png` (`0984f29a9d71dbede6de35147775c69c54a630a5bae17d0015d48bb958967634`), `MAMT:15` PDF page, `MAMT:16` PDF page | `bcc4a63b1d3df622078252fa4910b71acc0a3ceff43ec5a131ce996a4f24729f` | source identity, sequence and layout only |
| `SIRES-same-candle-POC` | `FP9-5-page.png` (`e100ee63d8504090ce61b25bc96efc498c078b481f98aae819c6b0cbf5ed3c98`), `FP9:7` PDF page, `FP8:6` PDF page | `e100ee63d8504090ce61b25bc96efc498c078b481f98aae819c6b0cbf5ed3c98` | source identity, sequence and layout only |
| `SIRES-losses-2026-07-23` | `ANAT:1` PDF page, `ANAT-6-figure.png` (`38d0b5ff541f6941b7e76fb2fdf1f74c63c41e87a8559c78e0de393a4cbd5ea8`), `ANAT:8` PDF page, `ANAT:9` PDF page | `83d603ec4e030443dd610c7405b30ff30ca315ffb18f1064835f397f8453504f` | source identity, sequence and layout only |
| `JJ-orderblock-long` | `TBR-27-page.png` (`8f4d0b4f621fc40b8b678c699ce8a9df17a99d964a53313072dc20a0bccf9906`), `TBR:28` PDF page | `8f4d0b4f621fc40b8b678c699ce8a9df17a99d964a53313072dc20a0bccf9906` | source identity, sequence and layout only |
| `STOP-confirmed` | `STOP-11-page.png` (`a6f3ce24a7aa18a5c19cc9023a478eda19966a106364d69f19ed1a11b5fa3655`), `STOP:12` PDF page | `a6f3ce24a7aa18a5c19cc9023a478eda19966a106364d69f19ed1a11b5fa3655` | source identity, sequence and layout only |
| `STOP-early` | `STOP-13-page.png` (`09031933a95911a979625b1a9f370cd1eba1cd50ad09b7b4d9cffed10e56823b`) | `09031933a95911a979625b1a9f370cd1eba1cd50ad09b7b4d9cffed10e56823b` | source identity, sequence and layout only |
| `SAINT-break-retest` | `TRAP-7-page.png` (`75301a4a7ff71b4ba0f52eeeeea5477a92c474a8748bd09ade770a56d601b235`), `TRAP:3` PDF page, `TRAP:4` PDF page, `TRAP:5` PDF page, `TRAP:9` PDF page | `75301a4a7ff71b4ba0f52eeeeea5477a92c474a8748bd09ade770a56d601b235` | source identity, sequence and layout only |
| `SAINT-failed-auction` | `AMTL-10-page.png` (`d3b7266963b900af7f04919f6fe06047b8c613a4fc087c980c55d6c2f304f81d`), `AMTL:8` PDF page, `AMTL:9` PDF page | `d3b7266963b900af7f04919f6fe06047b8c613a4fc087c980c55d6c2f304f81d` | source identity, sequence and layout only |
| `MEMBER-resistance` | `K10-7-page.png` (`322533902e1d80a6b1d602ed9050d4fbae47c3128701be00e6db022f92730979`) | `322533902e1d80a6b1d602ed9050d4fbae47c3128701be00e6db022f92730979` | source identity, sequence and layout only |
| `MEMBER-return` | `K10-8-page.png` (`f9fad6649195ad4334b15f71debff12490e6e0b0ab0758d52916689a5a9b8b4e`) | `f9fad6649195ad4334b15f71debff12490e6e0b0ab0758d52916689a5a9b8b4e` | source identity, sequence and layout only |
| `KEANI-open-above` | `AVG-22-page.png` (`532ec8a79512a811112f6e788df4e92d9161642b03b6522f57a716774bec3bbd`) | `532ec8a79512a811112f6e788df4e92d9161642b03b6522f57a716774bec3bbd` | source identity, sequence and layout only |
| `REFILL-selected-order` | `REF-7-page.png` (`316eba231a41e8b073f4638301b21ca5748b8fe154f0e402de68cd0c63433bac`), `REF:12` PDF page, `OFM:18` PDF page | `316eba231a41e8b073f4638301b21ca5748b8fe154f0e402de68cd0c63433bac` | source identity, sequence and layout only |
| `JETBUNDLE-state-process` | `MATH-3-page.png` (`67a0a9866467987325336a33aaca887734244aac0a38506fdb60ce2de92b46ea`), `MATH:10` PDF page, `MATH:11` PDF page | `67a0a9866467987325336a33aaca887734244aac0a38506fdb60ce2de92b46ea` | source identity, sequence and layout only |
| `STOIC-process` | `DATA-3-page.png` (`3b62aaa227581a3c8923ce38211c701b981dcf821c89ac72057be3a661ccfce9`), `DATA:4` PDF page | `3b62aaa227581a3c8923ce38211c701b981dcf821c89ac72057be3a661ccfce9` | source identity, sequence and layout only |
| `STOIC-risk` | `DATA-7-page.png` (`aac04ccec2b68ff64d6379d27e6f8daf59383a3412678bb05d2839ba657cdb17`), `DATA:8` PDF page | `aac04ccec2b68ff64d6379d27e6f8daf59383a3412678bb05d2839ba657cdb17` | source identity, sequence and layout only |
| `GB-SCALP-bearish` | `GB-40-page.png` (`e856bc8117350bcfdc244a94a3dbfb8c5621b29c8b873fe76aaecfcfc87a89f1`) | `e856bc8117350bcfdc244a94a3dbfb8c5621b29c8b873fe76aaecfcfc87a89f1` | source identity, sequence and layout only |
| `GB-SCALP-bullish` | `GB-40-page.png` (`e856bc8117350bcfdc244a94a3dbfb8c5621b29c8b873fe76aaecfcfc87a89f1`) | `e856bc8117350bcfdc244a94a3dbfb8c5621b29c8b873fe76aaecfcfc87a89f1` | source identity, sequence and layout only |

## Gate result and limits

| check | result | evidence |
| --- | --- | --- |
| every retained case has a disposition | **PASS** (22/22) | `calibration_matrix.json` case rows |
| every catalog branch has a disposition | **PASS** (50/50) | `calibration_matrix.json` branch rows |
| every branch rule has source-page evidence or named assumption | **PASS** | source refs resolve to catalog PDFs/pages; comparison assumptions resolve |
| source PDF identity | **PASS** | source catalog SHA-256 links and generation-time file verification |
| historical discovery for source cases | **EXCLUDED** | `n=null`, `search_completed=false`; source cases are not historical candidates |
| proxy-as-faithful admission | **0** | all branches carry `false`; cross-contract controls and later annotations stay separate |
| source-faithful disagreement count | **null** | no exact source fill/selector comparison is decidable for this calibration cohort |

The remaining limits are evidence limits: exact source fills and order ledgers, source contract/timeframe for undated figures, unpublished profile/VA and VWAP settings, proprietary P-zone/EV/SessionStat calculations, flow/depth/order lifecycle, classifier thresholds, and private process/Monte Carlo records. The matrix keeps each limitation attached to its case or branch, so later historical discovery can only admit a branch after its declared observable inputs and clocks are available.

## Reproduction and review commands

Run from `/workspace`:

```bash
PYTHONPATH=implementation/src python -m json.tool implementation/reports/phase1-live/empirical/calibration/calibration_matrix.json >/dev/null
PYTHONPATH=implementation/src python - <<'PY'
import json
from pathlib import Path
p = Path("implementation/reports/phase1-live/empirical/calibration/calibration_matrix.json")
d = json.loads(p.read_text())
assert (len(d["configurations"]), len(d["cases"]), len(d["branches"])) == (17, 22, 50)
assert not any(c["historical_candidate"] for c in d["cases"])
assert all(not b["proxy_as_faithful_allowed"] for b in d["branches"])
print("calibration matrix checks passed")
PY
```

The full native reconstruction commands and test identities remain in [CHART_VERIFICATION.md](../../methods/CHART_VERIFICATION.md), [SOURCE_RECHECK.md](../../methods/SOURCE_RECHECK.md), and the reconstruction READMEs. Changes to source interpretations or controls require a new calibration matrix version and refreshed hashes.
