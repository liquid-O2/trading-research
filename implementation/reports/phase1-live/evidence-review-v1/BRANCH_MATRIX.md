# Branch evidence matrix

All 50 registered branches are listed below. `null` means unavailable. Observed N counts initial records; n=p+f and N=p+f+u. These additive counts do not authorize pooled branch/family rates.

Complete/partial/missing are **rule/date search jobs**, not opportunity counts. A complete search may contain unknown outcomes. Zero means a complete search found no initial opportunity. Group columns use the frozen rule/cohort/year/instrument/evidence-mode/observation-unit strata.

## Supported comparisons

| Branch | Observed p / f / u | Observed n / N | Complete / partial / missing jobs | Complete zero jobs | Complete / all groups | Frozen status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| JJ-TBR / judas_reversal | 26 / 77 / 9 | 103 / 112 | 124 / 0 / 37 | 18 | 32 / 55 | data_hole |
| JJ-TBR / internal_rotation | 65 / 35 / 0 | 100 / 100 | 124 / 0 / 37 | 24 | 32 / 55 | data_hole |
| JJ-TBR / extension_reaction | 50 / 38 / 1 | 88 / 89 | 124 / 0 / 37 | 41 | 32 / 55 | data_hole |
| GB-FAIL / nyam_box | 99 / 123 / 1 | 222 / 223 | 159 / 0 / 2 | 1 | 53 / 55 | data_hole |
| GB-FAIL / previous_hour | 487 / 631 / 6 | 1118 / 1124 | 158 / 3 / 0 | 0 | 52 / 55 | completed_with_population_holes |
| GB-FAIL / asia_tdo_case | 3 / 114 / 0 | 117 / 117 | 63 / 3 / 95 | 0 | 17 / 55 | data_hole |
| GB-FAIL / prior_day_level | 33 / 75 / 1 | 108 / 109 | 107 / 0 / 54 | 9 | 21 / 55 | data_hole |
| GB-FAIL / prior_week_level | 12 / 46 / 0 | 58 / 58 | 92 / 0 / 69 | 34 | 16 / 55 | data_hole |
| GB-FAIL / prior_month_level | 5 / 6 / 0 | 11 / 11 | 23 / 0 / 138 | 12 | 0 / 55 | data_hole |
| GB-FAIL / cash_open_reclaim_case | 53 / 89 / 0 | 142 / 142 | 161 / 0 / 0 | 19 | 55 / 55 | measured |
| GB-FAIL / mss_fvg_refinement | 52 / 47 / 0 | 99 / 99 | 159 / 0 / 2 | 77 | 53 / 55 | data_hole |
| GB-VWAP / source_long | 36 / 12 / 8 | 48 / 56 | 70 / 0 / 91 | 14 | 19 / 55 | data_hole |
| SIRES / vwap_deviation_fade | 48 / 44 / 10 | 92 / 102 | 59 / 0 / 102 | 0 | 15 / 55 | data_hole |
| SAINT-AMT / continuation_retest | 31 / 75 / 0 | 106 / 106 | 107 / 0 / 54 | 11 | 21 / 55 | data_hole |
| SAINT-AMT / trapped_buyers_retest | 0 / 0 / 0 | 0 / 0 | 0 / 0 / 4 | 0 | 0 / 4 | data_hole |
| SAINT-AMT / failed_auction_return | 0 / 0 / 0 | 0 / 0 | 0 / 0 / 4 | 0 | 0 / 4 | data_hole |
| SAINT-AMT / poc_traversal | 0 / 0 / 0 | 0 / 0 | 0 / 0 / 4 | 0 | 0 / 4 | data_hole |
| KEANI-OPEN-ABOVE-VALUE / source_long | 0 / 0 / 4 | 0 / 4 | 4 / 0 / 0 | 0 | 4 / 4 | measured |
| REFILL-STUDY / touch_record | 0 / 0 / 0 | 0 / 0 | 1 / 0 / 3 | 1 | 1 / 4 | data_hole |

## Branch conclusions

| Branch | Definition and evidence implication |
| --- | --- |
| JJ-TBR / judas_reversal | Recover the shared 06:00–09:00 reference only after distinguishing absent trading from missing data. Nine unknowns come from the frozen 09:50 expiry and cannot be repaired by adding later prices. |
| JJ-TBR / internal_rotation | Shares the same 37 missing reference jobs as the other Jumbo comparisons. Direction is frozen from the midpoint-contact close; the outcome is a later range-edge path, not an executed trade. |
| JJ-TBR / extension_reaction | Shares the Jumbo reference gaps. The wide, frozen beyond-edge bands make this a different opportunity population from Judas. One unknown is caused by expiry. |
| GB-FAIL / nyam_box | Two missing reference dates, 2011-04-04 and 2014-05-01, each lack one minute also absent in local one-second bars. These references also feed MSS/FVG. One observed unknown is expiry-related. |
| GB-FAIL / previous_hour | Largest observed count because each completed hour supplies a new reference. Three dates have incomplete reference populations despite no fully missing jobs. Six endpoint unknowns are expiry-related; hourly observations are not independent sessions. |
| GB-FAIL / asia_tdo_case | 95 fully missing jobs plus three partially observed action populations. Recover Asia reference, midnight minute-open TDO and action coverage together. A reclaim of the Asia edge alone does not satisfy the TDO condition. |
| GB-FAIL / prior_day_level | Shares prior RTH inputs with Saint continuation. Audit actual session calendars and same-contract availability before seeking more bars. One observed unknown is expiry-related. |
| GB-FAIL / prior_week_level | Audit every required prior weekday and native contract. Missing references and 34 fully searched zero-opportunity jobs are different populations; do not interpret missing searches as failed reclaims. |
| GB-FAIL / prior_month_level | Only 23 complete jobs and 11 observed opportunities; none of its 55 reporting groups has a complete population. Calendar and contract continuity across the entire reference month dominate the limitation; this branch is too sparse for a ranking claim. |
| GB-FAIL / cash_open_reclaim_case | All 161 declared jobs completed; 19 contain no initial opportunity. Useful as a control for coverage accounting. A comparison pass does not establish private cash-open selection or profitability. |
| GB-FAIL / mss_fvg_refinement | All 99 child opportunities link one-to-one to the 99 passing NYAM parents and start at parent completion. Keep this conditional denominator separate from initial sweeps. The minute overview does not display the three required 2-minute candles or wick gap. |
| GB-VWAP / source_long | 91 missing search jobs and eight observed unknowns from unavailable pre-bar VWAP snapshots are separate gaps. Recover finished Asia/London references and the whole VWAP prefix. A later VWAP touch may occur below the initial breakout price. |
| SIRES / vwap_deviation_fade | 102 missing search jobs depend on the overnight prefix. Ten unknown records arise from six trigger bars touching both deviation bands: four bars contribute both sides and two contribute one remaining side. Finer chronology would require a separately specified rule, not automatic relabeling. |
| SAINT-AMT / continuation_retest | 54 prior RTH reference gaps shared with GB prior-day. The first later retest determines the result even if later price would tell a different story; no failed retest is repaired by selecting another one. |
| SAINT-AMT / trapped_buyers_retest | All four jobs lack required verified inputs; observed zero is not a completed empty population. Prior range plus current executed delta both matter. Investigate 2022 and 2026 reconciliation first. |
| SAINT-AMT / failed_auction_return | All four jobs lack verified prior trade-volume context/current tape. Recover the same-contract prior profile and declared current session before evaluating the excursion/return sequence. |
| SAINT-AMT / poc_traversal | All four jobs lack verified prior trade-volume context/current tape. Recover the prior POC and range; do not substitute a bar-volume or TPO profile. |
| KEANI-OPEN-ABOVE-VALUE / source_long | All four clock-based opening observations exist, but every prior profile is unverified: N=4, n=0, u=4. Status measured describes the opening population, not a resolved classification or a validated long entry. |
| REFILL-STUDY / touch_record | Three tape jobs are missing. The verified 2023-01-03 session has 322181 executed rows and legitimately forms no qualifying zones or returns under the frozen rule. Reconcile 2022/2026 first; do not lower thresholds to manufacture candidates. |

## Source dispositions

Each of these 31 branches has unavailable p/f/u/n/N, no declared empirical search, and source-method verdict unknown. More historical price data alone does not supply the missing definition, selection, process or state record.

| Branch | Disposition | Required evidence or limitation |
| --- | --- | --- |
| JJ-TBR / judas_outbound | unavailable_definition | Actual source directional context and cash-open selection are absent; later path cannot select opening side or infer an entry. |
| JJ-TBR / single_extended | unavailable_definition | Unpublished extended-context classification and reduced-expectation source policy absent; midpoint path comparison is represented separately under internal_rotation. |
| JJ-TBR / single_purged | unavailable_definition | Required independently known purges, compressed-context selection and expansion policy absent; containment cannot substitute. |
| JJ-TBR / other_session | unavailable_definition | Actual source other-session formation/action clocks and source cleanliness selection absent. |
| JJ-TBR / timed_pzone_reversal | unavailable_definition | Source P-zone bounds/version/active policy and ordered source-to-destination path absent; engine is proprietary. |
| GB-SCALP / bearish_small_scalp | source_case_only | Case descriptions lack repeatable source-complete trigger, impulse, admission and invalidation; do not replace them with failure/VWAP trades. |
| GB-SCALP / bullish_discount_pullback | source_case_only | Case descriptions lack repeatable source-complete trigger, impulse, admission and invalidation; do not replace them with failure/VWAP trades. |
| SIRES / dom_rejection | unavailable_definition | Selected planned level and actual source DOM queue/rejection observations absent; trades alone do not recover standing depth. |
| SIRES / absorption_reward_retest | unavailable_definition | Source real-extreme selection, local absorption, own price reward and reward-retest qualification are absent; generic band touch is insufficient. |
| SIRES / stop_four_stage | unavailable_definition | Actual linked four-stage defense/replenishment/exhaustion/lift-off observations and source risk stage are absent. |
| SIRES / footprint_confirmed_reaction | unavailable_definition | Selected source candle/POC snapshot, local reaction and exact source footprint confirmation conventions are absent. |
| SIRES / ofm_aggressive | unavailable_definition | Source selected origin, catalyst/release, failure/refill and drive/retest episodes are absent; no generic impulse substitute. |
| SIRES / ofm_passive | unavailable_definition | Source selected origin and passive pullback/refill confirmation are absent; executed-only tape cannot reconstruct private passive order selection. |
| SIRES / clean_squeeze | unavailable_definition | Source clean-state and squeeze qualification, thesis and current flow criteria are unpublished. |
| SIRES / balance_failure_fade | unavailable_definition | Source gamma regime, selected balance and source aggression-failure confirmation are absent. |
| SIRES / defended_band_continuation | unavailable_definition | Actual selected continuation band and fresh same-band defense/current source confirmation are absent. |
| SIRES / microbalance_break | unavailable_definition | Actual selected small balance and larger thesis/strength are absent; source explicitly disallows universal fixed-clock box/run-detector substitution. |
| SIRES / kg1_retest | unavailable_definition | Proprietary source KG1/version and aggressive retest confirmation are absent; scenario gamma wall is not KG1. |
| MEMBER-TWO-REASONS / resistance_short | unavailable_definition | Missing independent prior-reaction and minor-HVN selection, profile window, confluence tolerance and current confirmation; arbitrary first HVN/prior extreme is not the source model. |
| MEMBER-TWO-REASONS / planned_return_long | unavailable_definition | Missing independent prior-reaction and minor-HVN selection, profile window, confluence tolerance and current confirmation; arbitrary first HVN/prior extreme is not the source model. |
| REFILL-STUDY / supplied_selected_order | supplied_only | Missing actual private model/grade, selected-order identity and order/fill ledger; public executions do not manufacture selection. |
| JETBUNDLE-STATES / B | supplied_only | Actual supplied state labels, classifier cadence/thresholds/priority and transition adjacency absent; no classifier training authorized. |
| JETBUNDLE-STATES / A | supplied_only | Actual supplied state labels, classifier cadence/thresholds/priority and transition adjacency absent; no classifier training authorized. |
| JETBUNDLE-STATES / D | supplied_only | Actual supplied state labels, classifier cadence/thresholds/priority and transition adjacency absent; no classifier training authorized. |
| JETBUNDLE-STATES / E | supplied_only | Actual supplied state labels, classifier cadence/thresholds/priority and transition adjacency absent; no classifier training authorized. |
| JETBUNDLE-STATES / W | supplied_only | Actual supplied state labels, classifier cadence/thresholds/priority and transition adjacency absent; no classifier training authorized. |
| STOIC-DATA / process_review | non_entry | Process journal and declared process versions required; macro application additionally lacks custom series/vintages/C-score/cycle rules. |
| STOIC-DATA / macro_application | non_entry | Process journal and declared process versions required; macro application additionally lacks custom series/vintages/C-score/cycle rules. |
| STOIC-RISK / first | supplied_only | Actual validated process, Monte Carlo inputs and risk-stage/position ledger absent; printed arithmetic is separately auditable. |
| STOIC-RISK / second | supplied_only | Actual validated process, Monte Carlo inputs and risk-stage/position ledger absent; printed arithmetic is separately auditable. |
| STOIC-RISK / reset_after_second_win | supplied_only | Actual validated process, Monte Carlo inputs and risk-stage/position ledger absent; printed arithmetic is separately auditable. |

## Separate observation units

All eight remain supplied-only with unavailable denominators. They are not added to initial market opportunities.

| Unit ID | Observation unit | Status | Required evidence |
| --- | --- | --- | --- |
| JJ-TBR:management:observation-v1 | management | supplied_only | Actual linked source process/position/decision/state records are indispensable; preserve separately from market opportunities and never infer from later prices. |
| GB-SCALP:automatic_admission:observation-v1 | automatic_admission | supplied_only | Actual linked source process/position/decision/state records are indispensable; preserve separately from market opportunities and never infer from later prices. |
| SIRES:case_description:observation-v1 | case_description | supplied_only | Actual linked source process/position/decision/state records are indispensable; preserve separately from market opportunities and never infer from later prices. |
| SIRES:management:observation-v1 | management | supplied_only | Actual linked source process/position/decision/state records are indispensable; preserve separately from market opportunities and never infer from later prices. |
| SIRES:reentry:observation-v1 | reentry | supplied_only | Actual linked source process/position/decision/state records are indispensable; preserve separately from market opportunities and never infer from later prices. |
| REFILL-STUDY:selected_order_configuration:observation-v1 | selected_order_configuration | supplied_only | Actual linked source process/position/decision/state records are indispensable; preserve separately from market opportunities and never infer from later prices. |
| JETBUNDLE-STATES:transition_observation:observation-v1 | transition_observation | supplied_only | Actual linked source process/position/decision/state records are indispensable; preserve separately from market opportunities and never infer from later prices. |
| STOIC-DATA:macro_application:observation-v1 | macro_application | supplied_only | Actual linked source process/position/decision/state records are indispensable; preserve separately from market opportunities and never infer from later prices. |

The exact definitions, counts by year, population holes, missing reference objects and per-date checkpoint links are in [DENOMINATOR_AUDIT.json](DENOMINATOR_AUDIT.json). Source definitions remain in the [frozen registry](../empirical/registry/CANDIDATE_REGISTRY.json).
