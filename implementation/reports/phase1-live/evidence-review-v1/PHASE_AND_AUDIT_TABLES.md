# PHASE and audit tables

Accepted Phase 1 tables reproduced for this follow-on review. No new replay or test-suite run is represented here.

Family n adds observed branch records; it is not a pooled strategy denominator. Audit verdict is the source-method verdict, separate from comparison pass/fail. `fixture=not_run` identifies these empirical observations as native-input records; fixture validation is reported separately in the current736-test suite.

family | variant | n | faithful_disagreements | status | report path
--- | --- | ---: | --- | --- | ---
GB-FAIL | comparison counts; no pooled rate | 1875 | null | data_hole | [RESULTS.md](../empirical/RESULTS.md)
GB-SCALP | comparison counts; no pooled rate | null | null | unavailable_definition | [RESULTS.md](../empirical/RESULTS.md)
GB-VWAP | comparison counts; no pooled rate | 48 | null | data_hole | [RESULTS.md](../empirical/RESULTS.md)
JETBUNDLE-STATES | comparison counts; no pooled rate | null | null | unavailable_definition | [RESULTS.md](../empirical/RESULTS.md)
JJ-TBR | comparison counts; no pooled rate | 291 | null | data_hole | [RESULTS.md](../empirical/RESULTS.md)
KEANI-OPEN-ABOVE-VALUE | comparison counts; no pooled rate | 0 | null | measured | [RESULTS.md](../empirical/RESULTS.md)
MEMBER-TWO-REASONS | comparison counts; no pooled rate | null | null | unavailable_definition | [RESULTS.md](../empirical/RESULTS.md)
REFILL-STUDY | comparison counts; no pooled rate | 0 | null | data_hole | [RESULTS.md](../empirical/RESULTS.md)
SAINT-AMT | comparison counts; no pooled rate | 106 | null | data_hole | [RESULTS.md](../empirical/RESULTS.md)
SIRES | comparison counts; no pooled rate | 92 | null | data_hole | [RESULTS.md](../empirical/RESULTS.md)
STOIC-DATA | comparison counts; no pooled rate | null | null | unavailable_definition | [RESULTS.md](../empirical/RESULTS.md)
STOIC-RISK | comparison counts; no pooled rate | null | null | unavailable_definition | [RESULTS.md](../empirical/RESULTS.md)

family | id | verdict | fixture | leakage | proxy-as-faithful | notes
--- | --- | --- | --- | ---: | ---: | ---
JJ-TBR | JJ-TBR:judas_outbound:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
JJ-TBR | JJ-TBR:judas_reversal:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=37; remaining=0
JJ-TBR | JJ-TBR:single_extended:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
JJ-TBR | JJ-TBR:single_purged:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
JJ-TBR | JJ-TBR:internal_rotation:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=37; remaining=0
JJ-TBR | JJ-TBR:extension_reaction:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=37; remaining=0
JJ-TBR | JJ-TBR:other_session:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
JJ-TBR | JJ-TBR:timed_pzone_reversal:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
GB-FAIL | GB-FAIL:nyam_box:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=2; remaining=0
GB-FAIL | GB-FAIL:previous_hour:comparison-v1 | unknown | not_run | 0 | 0 | completed_with_population_holes; disposition=supported_comparison; eligible=161; scanned=161; missing=0; remaining=0
GB-FAIL | GB-FAIL:asia_tdo_case:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=95; remaining=0
GB-FAIL | GB-FAIL:prior_day_level:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=54; remaining=0
GB-FAIL | GB-FAIL:prior_week_level:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=69; remaining=0
GB-FAIL | GB-FAIL:prior_month_level:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=138; remaining=0
GB-FAIL | GB-FAIL:cash_open_reclaim_case:comparison-v1 | unknown | not_run | 0 | 0 | measured; disposition=supported_comparison; eligible=161; scanned=161; missing=0; remaining=0
GB-FAIL | GB-FAIL:mss_fvg_refinement:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=2; remaining=0
GB-VWAP | GB-VWAP:source_long:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=91; remaining=0
GB-SCALP | GB-SCALP:bearish_small_scalp:disposition-v1 | unknown | not_run | 0 | 0 | source_case_only; disposition=source_case_only; eligible=0; scanned=0; missing=0; remaining=0
GB-SCALP | GB-SCALP:bullish_discount_pullback:disposition-v1 | unknown | not_run | 0 | 0 | source_case_only; disposition=source_case_only; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:dom_rejection:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:absorption_reward_retest:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:stop_four_stage:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:footprint_confirmed_reaction:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:vwap_deviation_fade:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=102; remaining=0
SIRES | SIRES:ofm_aggressive:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:ofm_passive:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:clean_squeeze:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:balance_failure_fade:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:defended_band_continuation:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:microbalance_break:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SIRES | SIRES:kg1_retest:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
SAINT-AMT | SAINT-AMT:continuation_retest:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=161; scanned=161; missing=54; remaining=0
SAINT-AMT | SAINT-AMT:trapped_buyers_retest:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=4; scanned=4; missing=4; remaining=0
SAINT-AMT | SAINT-AMT:failed_auction_return:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=4; scanned=4; missing=4; remaining=0
SAINT-AMT | SAINT-AMT:poc_traversal:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=4; scanned=4; missing=4; remaining=0
MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:resistance_short:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:planned_return_long:disposition-v1 | unknown | not_run | 0 | 0 | unavailable_definition; disposition=unavailable_definition; eligible=0; scanned=0; missing=0; remaining=0
KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:comparison-v1 | unknown | not_run | 0 | 0 | measured; disposition=supported_comparison; eligible=4; scanned=4; missing=0; remaining=0
REFILL-STUDY | REFILL-STUDY:touch_record:comparison-v1 | unknown | not_run | 0 | 0 | data_hole; disposition=supported_comparison; eligible=4; scanned=4; missing=3; remaining=0
REFILL-STUDY | REFILL-STUDY:supplied_selected_order:disposition-v1 | unknown | not_run | 0 | 0 | supplied_only; disposition=supplied_only; eligible=0; scanned=0; missing=0; remaining=0
JETBUNDLE-STATES | JETBUNDLE-STATES:B:disposition-v1 | unknown | not_run | 0 | 0 | supplied_only; disposition=supplied_only; eligible=0; scanned=0; missing=0; remaining=0
JETBUNDLE-STATES | JETBUNDLE-STATES:A:disposition-v1 | unknown | not_run | 0 | 0 | supplied_only; disposition=supplied_only; eligible=0; scanned=0; missing=0; remaining=0
JETBUNDLE-STATES | JETBUNDLE-STATES:D:disposition-v1 | unknown | not_run | 0 | 0 | supplied_only; disposition=supplied_only; eligible=0; scanned=0; missing=0; remaining=0
JETBUNDLE-STATES | JETBUNDLE-STATES:E:disposition-v1 | unknown | not_run | 0 | 0 | supplied_only; disposition=supplied_only; eligible=0; scanned=0; missing=0; remaining=0
JETBUNDLE-STATES | JETBUNDLE-STATES:W:disposition-v1 | unknown | not_run | 0 | 0 | supplied_only; disposition=supplied_only; eligible=0; scanned=0; missing=0; remaining=0
STOIC-DATA | STOIC-DATA:process_review:disposition-v1 | unknown | not_run | 0 | 0 | non_entry; disposition=non_entry; eligible=0; scanned=0; missing=0; remaining=0
STOIC-DATA | STOIC-DATA:macro_application:disposition-v1 | unknown | not_run | 0 | 0 | non_entry; disposition=non_entry; eligible=0; scanned=0; missing=0; remaining=0
STOIC-RISK | STOIC-RISK:first:disposition-v1 | unknown | not_run | 0 | 0 | supplied_only; disposition=supplied_only; eligible=0; scanned=0; missing=0; remaining=0
STOIC-RISK | STOIC-RISK:second:disposition-v1 | unknown | not_run | 0 | 0 | supplied_only; disposition=supplied_only; eligible=0; scanned=0; missing=0; remaining=0
STOIC-RISK | STOIC-RISK:reset_after_second_win:disposition-v1 | unknown | not_run | 0 | 0 | supplied_only; disposition=supplied_only; eligible=0; scanned=0; missing=0; remaining=0
JJ-TBR | JJ-TBR:management:observation-v1 | unknown | not_run | 0 | 0 | supplied_only; no market proxy admitted
GB-SCALP | GB-SCALP:automatic_admission:observation-v1 | unknown | not_run | 0 | 0 | supplied_only; no market proxy admitted
SIRES | SIRES:case_description:observation-v1 | unknown | not_run | 0 | 0 | supplied_only; no market proxy admitted
SIRES | SIRES:management:observation-v1 | unknown | not_run | 0 | 0 | supplied_only; no market proxy admitted
SIRES | SIRES:reentry:observation-v1 | unknown | not_run | 0 | 0 | supplied_only; no market proxy admitted
REFILL-STUDY | REFILL-STUDY:selected_order_configuration:observation-v1 | unknown | not_run | 0 | 0 | supplied_only; no market proxy admitted
JETBUNDLE-STATES | JETBUNDLE-STATES:transition_observation:observation-v1 | unknown | not_run | 0 | 0 | supplied_only; no market proxy admitted
STOIC-DATA | STOIC-DATA:macro_application:observation-v1 | unknown | not_run | 0 | 0 | supplied_only; no market proxy admitted
