# Phase 1 — full acquired historical measurement

The unchanged versioned scanners searched **1,742 declared session dates**, 2020-01-01 through 2026-09-03, across all 50 branches and eight additional observation units. The composed census contains **99,294 daily jobs** and **18,747 qualifying market setups**, plus three actual collection-process jobs. The independent primary run and all 90 calendar-recovery dates completed and were verified.

**The acquired observed-input census is executed. Input-limited populations remain unmeasured beyond the observed subset; the exact affected branch/session denominators are listed below.** Qualification does not establish a winning trade. All reported outcomes are subsequent observed prices; no return simulation or actual fill is claimed. Phase 2 remains the additional context layer that selects which setups to use.

## Population, scope and boundaries

The owned MBP-1 endpoint is **2026-09-03T06:09:59.901114+00:00** (exclusive). September 3 is a partially acquired session label, not a completed RTH day. Branch-specific complete-input endpoints and exclusions below govern the measured denominators.

591,714,592 owned native execution references reconcile from session receipts to daily branch jobs. A session execution is counted once in this native total, even when several branches consume it. Different methods can identify overlapping market events; the setup total is a sum of branch opportunities, not an independent portfolio trade count.

| Manifest scope | Branch / additional units |
| --- | --- |
| context_or_research | 10 |
| entry_setup | 37 |
| personal_execution_out_of_scope | 7 |
| supplemental_observation | 4 |

All weekday session labels were searched, including holidays and unavailable dates. Earlier observations are lookbacks only. Complete eligible denominators require the frozen branch prefix, required context and candidate inputs to be observed. Interior limitations are excluded individually; choosing the last complete endpoint does not discard earlier difficult dates. Native event-time bars and vendor receive-time model inputs retain separate receipts. Canonical ownership prevents counting overlapping recovery files twice and preserves genuine repeated executions.

| Branch / unit | Scope | Eligible sessions | Observed setups | Setups in eligible sessions | Complete zero searches | Last complete input session |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR:branch:judas_outbound | entry_setup | 1621 | 1528 | 1453 | 168 | 2026-09-02 |
| JJ-TBR:branch:judas_reversal | entry_setup | 1634 | 133 | 132 | 1502 | 2026-09-02 |
| JJ-TBR:branch:single_extended | entry_setup | 1637 | 9 | 9 | 1628 | 2026-09-02 |
| JJ-TBR:branch:single_purged | entry_setup | 1636 | 25 | 24 | 1612 | 2026-09-02 |
| JJ-TBR:branch:internal_rotation | entry_setup | 1637 | 4 | 4 | 1633 | 2026-09-02 |
| JJ-TBR:branch:extension_reaction | entry_setup | 1634 | 178 | 176 | 1458 | 2026-09-02 |
| JJ-TBR:branch:other_session | entry_setup | 1548 | 1730 | 1586 | 528 | 2026-08-31 |
| JJ-TBR:branch:timed_pzone_reversal | entry_setup | 1613 | 305 | 294 | 1338 | 2026-09-02 |
| JJ-TBR:unit:management | personal_execution_out_of_scope | 0 | 0 | 0 | 0 | none |
| GB-FAIL:branch:nyam_box | entry_setup | 1716 | 1063 | 1061 | 796 | 2026-09-02 |
| GB-FAIL:branch:previous_hour | entry_setup | 1702 | 5353 | 5290 | 81 | 2026-09-02 |
| GB-FAIL:branch:asia_tdo_case | entry_setup | 1662 | 168 | 166 | 1499 | 2026-09-02 |
| GB-FAIL:branch:prior_day_level | entry_setup | 1683 | 532 | 531 | 1184 | 2026-09-02 |
| GB-FAIL:branch:prior_week_level | entry_setup | 1676 | 219 | 219 | 1460 | 2026-09-02 |
| GB-FAIL:branch:prior_month_level | entry_setup | 1497 | 98 | 98 | 1399 | 2026-09-02 |
| GB-FAIL:branch:cash_open_reclaim_case | entry_setup | 1676 | 156 | 156 | 1520 | 2026-09-02 |
| GB-FAIL:branch:mss_fvg_refinement | supplemental_observation | 0 | 0 | 0 | 0 | 2026-09-02 |
| GB-VWAP:branch:source_long | entry_setup | 1666 | 499 | 492 | 1174 | 2026-09-02 |
| GB-SCALP:branch:bearish_small_scalp | entry_setup | 1720 | 1603 | 1602 | 118 | 2026-09-02 |
| GB-SCALP:branch:bullish_discount_pullback | entry_setup | 1720 | 1463 | 1463 | 257 | 2026-09-02 |
| GB-SCALP:unit:automatic_admission | supplemental_observation | 0 | 0 | 0 | 0 | none |
| SIRES:branch:dom_rejection | entry_setup | 1672 | 339 | 329 | 1361 | 2026-09-02 |
| SIRES:branch:absorption_reward_retest | entry_setup | 1672 | 7 | 7 | 1665 | 2026-09-02 |
| SIRES:branch:stop_four_stage | entry_setup | 1672 | 14 | 14 | 1658 | 2026-09-02 |
| SIRES:branch:footprint_confirmed_reaction | entry_setup | 1672 | 4 | 4 | 1668 | 2026-09-02 |
| SIRES:branch:vwap_deviation_fade | entry_setup | 1671 | 153 | 149 | 1525 | 2026-09-02 |
| SIRES:branch:ofm_aggressive | entry_setup | 1672 | 0 | 0 | 1672 | 2026-09-02 |
| SIRES:branch:ofm_passive | entry_setup | 1672 | 0 | 0 | 1672 | 2026-09-02 |
| SIRES:branch:clean_squeeze | entry_setup | 1672 | 1 | 1 | 1671 | 2026-09-02 |
| SIRES:branch:balance_failure_fade | entry_setup | 1667 | 2 | 2 | 1665 | 2026-09-02 |
| SIRES:branch:defended_band_continuation | entry_setup | 1672 | 57 | 56 | 1617 | 2026-09-02 |
| SIRES:branch:microbalance_break | entry_setup | 1661 | 1486 | 1431 | 816 | 2026-08-31 |
| SIRES:branch:kg1_retest | entry_setup | 1588 | 475 | 464 | 1131 | 2026-09-02 |
| SIRES:unit:case_description | supplemental_observation | 0 | 0 | 0 | 0 | none |
| SIRES:unit:management | personal_execution_out_of_scope | 0 | 0 | 0 | 0 | none |
| SIRES:unit:reentry | supplemental_observation | 0 | 0 | 0 | 0 | none |
| SAINT-AMT:branch:continuation_retest | entry_setup | 1659 | 26 | 24 | 1635 | 2026-09-02 |
| SAINT-AMT:branch:trapped_buyers_retest | entry_setup | 1660 | 9 | 9 | 1651 | 2026-09-02 |
| SAINT-AMT:branch:failed_auction_return | entry_setup | 1611 | 471 | 444 | 1209 | 2026-09-02 |
| SAINT-AMT:branch:poc_traversal | entry_setup | 1623 | 279 | 263 | 1378 | 2026-09-02 |
| MEMBER-TWO-REASONS:branch:resistance_short | entry_setup | 1631 | 112 | 106 | 1525 | 2026-09-02 |
| MEMBER-TWO-REASONS:branch:planned_return_long | entry_setup | 1631 | 240 | 230 | 1401 | 2026-09-02 |
| KEANI-OPEN-ABOVE-VALUE:branch:source_long | entry_setup | 1594 | 6 | 6 | 1588 | 2026-09-02 |
| REFILL-STUDY:branch:touch_record | context_or_research | 0 | 0 | 0 | 0 | 2026-09-02 |
| REFILL-STUDY:branch:supplied_selected_order | personal_execution_out_of_scope | 0 | 0 | 0 | 0 | none |
| REFILL-STUDY:unit:selected_order_configuration | personal_execution_out_of_scope | 0 | 0 | 0 | 0 | none |
| JETBUNDLE-STATES:branch:B | context_or_research | 0 | 0 | 0 | 0 | 2026-09-02 |
| JETBUNDLE-STATES:branch:A | context_or_research | 0 | 0 | 0 | 0 | 2026-09-02 |
| JETBUNDLE-STATES:branch:D | context_or_research | 0 | 0 | 0 | 0 | 2026-09-02 |
| JETBUNDLE-STATES:branch:E | context_or_research | 0 | 0 | 0 | 0 | 2026-09-02 |
| JETBUNDLE-STATES:branch:W | context_or_research | 0 | 0 | 0 | 0 | 2026-09-02 |
| JETBUNDLE-STATES:unit:transition_observation | context_or_research | 0 | 0 | 0 | 0 | none |
| STOIC-DATA:branch:macro_application | context_or_research | 0 | 0 | 0 | 0 | none |
| STOIC-DATA:unit:macro_application | context_or_research | 0 | 0 | 0 | 0 | none |
| STOIC-RISK:branch:first | personal_execution_out_of_scope | 0 | 0 | 0 | 0 | none |
| STOIC-RISK:branch:second | personal_execution_out_of_scope | 0 | 0 | 0 | 0 | none |
| STOIC-RISK:branch:reset_after_second_win | personal_execution_out_of_scope | 0 | 0 | 0 | 0 | none |

## Measurement conventions and interpretation

Frequency is qualifying setups in complete sessions divided by complete eligible branch-sessions. Setups in limited sessions remain separately recorded. Decision-clock bins share that denominator; no new session-based selector is introduced. The four fixed excursion horizons are 5, 15, 30 and 60 minutes after qualification. Missing or session-truncated future windows are lower bounds and do not enter complete-horizon means or medians.

Price origin is the existing entry reference when defined, otherwise a causally completed trigger close, otherwise the first strictly subsequent whole-batch VWAP, explicitly a measurement convention. Boundaries are the existing structural invalidation and objective; none are invented. Judas outbound keeps its published 09:40 deadline; other price ordering uses the frozen 60-minute measurement expiry. Original scanner outcome records remain alongside these measurements. Same-batch objective/invalidation touches remain unresolved; an earlier coverage gap prevents establishing population-first ordering. Undefined and single-boundary cases have separate counts. Resolution times attached to gap-ambiguous observations describe the observed batch only.

Source definitions, disclosed inferred rules and model versions are retained per setup. The run is not an untouched holdout: prior engineering evaluations, reconstruction examples and the interrupted first measurement attempt are recorded in the frozen protocol. No thresholds, rules or endpoints were selected from favorable results.

## Current method results

- [JJ-TBR: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/JJ-TBR.md)
- [GB-FAIL: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-FAIL.md)
- [GB-VWAP: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-VWAP.md)
- [GB-SCALP: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-SCALP.md)
- [SIRES: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/SIRES.md)
- [SAINT-AMT: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/SAINT-AMT.md)
- [MEMBER-TWO-REASONS: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/MEMBER-TWO-REASONS.md)
- [KEANI-OPEN-ABOVE-VALUE: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/KEANI-OPEN-ABOVE-VALUE.md)
- [REFILL-STUDY: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/REFILL-STUDY.md)
- [JETBUNDLE-STATES: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/JETBUNDLE-STATES.md)
- [STOIC-DATA: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-DATA.md)
- [STOIC-RISK: branch/year/session frequencies, four-horizon excursions, ordering, resolution times and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-RISK.md)

The existing method pages also contain these generated results above their preserved implementation history. Context, supplemental annotations, personal execution units and collection process records do not enter setup frequency or excursion denominators. Daily macro quantities are retained even where a collection review was pending during a daily job.

| Actual collection unit | Records | Native research verdicts |
| --- | --- | --- |
| STOIC-DATA:branch:process_review | 1 | pass |
| STOIC-DATA:branch:macro_application | 1 | pass |
| STOIC-DATA:unit:macro_application | 1 | pass |

## Exact remaining input limitations

| Branch / unit | Input-limited session jobs | Reason: affected sessions (reasons may overlap) |
| --- | --- | --- |
| JJ-TBR:branch:judas_outbound | 109 | calendar_unverified: 8; current input prefix has unknown intervals: 70; formation_has_no_observed_executions: 21; nonpositive_formation_width: 3; same_contract_prior_scope_unknown: 34 |
| JJ-TBR:branch:judas_reversal | 96 | calendar_unverified: 8; current input prefix has unknown intervals: 70; formation_has_no_observed_executions: 21; nonpositive_formation_width: 3; same_contract_prior_scope_unknown: 34 |
| JJ-TBR:branch:single_extended | 93 | calendar_unverified: 8; current input prefix has unknown intervals: 70; formation_has_no_observed_executions: 21; nonpositive_formation_width: 3; same_contract_prior_scope_unknown: 34 |
| JJ-TBR:branch:single_purged | 94 | calendar_unverified: 8; current input prefix has unknown intervals: 70; formation_has_no_observed_executions: 21; nonpositive_formation_width: 3; same_contract_prior_scope_unknown: 34 |
| JJ-TBR:branch:internal_rotation | 93 | calendar_unverified: 8; current input prefix has unknown intervals: 70; formation_has_no_observed_executions: 21; nonpositive_formation_width: 3; same_contract_prior_scope_unknown: 34 |
| JJ-TBR:branch:extension_reaction | 96 | calendar_unverified: 8; current input prefix has unknown intervals: 70; formation_has_no_observed_executions: 21; nonpositive_formation_width: 3; same_contract_prior_scope_unknown: 34 |
| JJ-TBR:branch:other_session | 182 | calendar_unverified: 8; current input prefix has unknown intervals: 70; formation_has_no_observed_executions: 105; nonpositive_formation_width: 4; same_contract_prior_scope_unknown: 34 |
| JJ-TBR:branch:timed_pzone_reversal | 117 | calendar_unverified: 8; current input prefix has unknown intervals: 70; no dated P-zone bands/destinations: 35; same_contract_prior_scope_unknown: 34 |
| JJ-TBR:unit:management | 0 | actual dated process/source records absent: 1742; current input prefix has unknown intervals: 70 |
| GB-FAIL:branch:nyam_box | 14 | current input prefix has unknown intervals: 10 |
| GB-FAIL:branch:previous_hour | 28 | current input prefix has unknown intervals: 10 |
| GB-FAIL:branch:asia_tdo_case | 68 | current input prefix has unknown intervals: 70 |
| GB-FAIL:branch:prior_day_level | 47 | calendar_unverified: 8; current input prefix has unknown intervals: 10; same_contract_prior_scope_unknown: 34 |
| GB-FAIL:branch:prior_week_level | 54 | calendar_unverified: 40; current input prefix has unknown intervals: 10; same_contract_prior_scope_unknown: 40 |
| GB-FAIL:branch:prior_month_level | 233 | calendar_unverified: 219; current input prefix has unknown intervals: 10; same_contract_prior_scope_unknown: 219 |
| GB-FAIL:branch:cash_open_reclaim_case | 54 | cash_open_order_unknown: 58; current input prefix has unknown intervals: 10 |
| GB-FAIL:branch:mss_fvg_refinement | 10 | current input prefix has unknown intervals: 10 |
| GB-VWAP:branch:source_long | 64 | current input prefix has unknown intervals: 70; earlier potential breakout close is unknown: 4; session_reference_missing: 21 |
| GB-SCALP:branch:bearish_small_scalp | 10 | current input prefix has unknown intervals: 11 |
| GB-SCALP:branch:bullish_discount_pullback | 10 | current input prefix has unknown intervals: 11 |
| GB-SCALP:unit:automatic_admission | 1730 | GB p.40 discloses no complete repeatable scalp entry: 1742; current input prefix has unknown intervals: 11 |
| SIRES:branch:dom_rejection | 58 | current input prefix has unknown intervals: 70 |
| SIRES:branch:absorption_reward_retest | 58 | current input prefix has unknown intervals: 70 |
| SIRES:branch:stop_four_stage | 58 | current input prefix has unknown intervals: 70 |
| SIRES:branch:footprint_confirmed_reaction | 58 | current input prefix has unknown intervals: 70 |
| SIRES:branch:vwap_deviation_fade | 59 | current input prefix has unknown intervals: 70 |
| SIRES:branch:ofm_aggressive | 58 | current input prefix has unknown intervals: 70 |
| SIRES:branch:ofm_passive | 58 | current input prefix has unknown intervals: 70 |
| SIRES:branch:clean_squeeze | 58 | current input prefix has unknown intervals: 70 |
| SIRES:branch:balance_failure_fade | 63 | current input prefix has unknown intervals: 70 |
| SIRES:branch:defended_band_continuation | 58 | current input prefix has unknown intervals: 70 |
| SIRES:branch:microbalance_break | 69 | current input prefix has unknown intervals: 70; earlier potential directional breakout close is unknown: 11 |
| SIRES:branch:kg1_retest | 142 | KG1/key-gamma model input unavailable: 107; current input prefix has unknown intervals: 70 |
| SIRES:unit:case_description | 1730 | actual dated process/source records absent: 1742; current input prefix has unknown intervals: 70 |
| SIRES:unit:management | 0 | actual dated process/source records absent: 1742; current input prefix has unknown intervals: 70 |
| SIRES:unit:reentry | 1730 | actual dated process/source records absent: 1742; current input prefix has unknown intervals: 70 |
| SAINT-AMT:branch:continuation_retest | 71 | current input prefix has unknown intervals: 70; earlier potential directional breakout close is unknown: 13 |
| SAINT-AMT:branch:trapped_buyers_retest | 70 | current input prefix has unknown intervals: 70; earlier potential directional breakout close is unknown: 10 |
| SAINT-AMT:branch:failed_auction_return | 119 | calendar_unverified: 9; current input prefix has unknown intervals: 70; no distinct older completed auction in current admitted prefix: 45 |
| SAINT-AMT:branch:poc_traversal | 107 | calendar_unverified: 9; current input prefix has unknown intervals: 70; no distinct older completed auction in current admitted prefix: 45 |
| MEMBER-TWO-REASONS:branch:resistance_short | 99 | calendar_unverified: 65; current input prefix has unknown intervals: 10; same_contract_prior_scope_unknown: 37 |
| MEMBER-TWO-REASONS:branch:planned_return_long | 99 | bar contact has no exact band execution: 1; calendar_unverified: 65; current input prefix has unknown intervals: 10; same_contract_prior_scope_unknown: 37 |
| KEANI-OPEN-ABOVE-VALUE:branch:source_long | 136 | A period has no observed executions: 47; calendar_unverified: 65; current input prefix has unknown intervals: 10; same_contract_prior_scope_unknown: 37 |
| REFILL-STUDY:branch:touch_record | 10 | current input prefix has unknown intervals: 10 |
| REFILL-STUDY:branch:supplied_selected_order | 0 | actual dated process/source records absent: 1742; current input prefix has unknown intervals: 10 |
| REFILL-STUDY:unit:selected_order_configuration | 0 | actual dated process/source records absent: 1742; current input prefix has unknown intervals: 10 |
| JETBUNDLE-STATES:branch:B | 43 | current input prefix has unknown intervals: 10; scheduled RTH closure; no market-state observation: 12 |
| JETBUNDLE-STATES:branch:A | 43 | current input prefix has unknown intervals: 10; scheduled RTH closure; no market-state observation: 12 |
| JETBUNDLE-STATES:branch:D | 42 | current input prefix has unknown intervals: 10; scheduled RTH closure; no market-state observation: 12 |
| JETBUNDLE-STATES:branch:E | 42 | current input prefix has unknown intervals: 10; scheduled RTH closure; no market-state observation: 12 |
| JETBUNDLE-STATES:branch:W | 45 | current input prefix has unknown intervals: 10; scheduled RTH closure; no market-state observation: 12 |
| JETBUNDLE-STATES:unit:transition_observation | 1730 | actual dated process/source records absent: 1742; current input prefix has unknown intervals: 10 |
| STOIC-DATA:branch:macro_application | 1730 | collection review is emitted after this date job finishes: 1742; current input prefix has unknown intervals: 10 |
| STOIC-DATA:unit:macro_application | 1730 | collection review is emitted after this date job finishes: 1742; current input prefix has unknown intervals: 10 |
| STOIC-RISK:branch:first | 0 | current input prefix has unknown intervals: 10; no actual validated process and risk-stage ledger: 1742 |
| STOIC-RISK:branch:second | 0 | current input prefix has unknown intervals: 10; no actual validated process and risk-stage ledger: 1742 |
| STOIC-RISK:branch:reset_after_second_win | 0 | current input prefix has unknown intervals: 10; no actual validated process and risk-stage ledger: 1742 |

The coverage ledger identifies every affected date, required prefix, missing interval, original omission and disposition. A scheduled closure, completed zero search, unavailable population and unresolved future outcome are distinct states. Personal-record exclusions describe out-of-scope execution audits, not missing market-setup evidence.

Two factual matching-calendar inputs were recovered from dated official CME schedules: the [2023 Presidents Day schedule](https://www.cmegroup.com/files/presidents-day.pdf) and the [January 9, 2025 mourning-day table](https://www.cmegroup.com/content/dam/cmegroup/trading-hours/files/day-of-mourning-january-9-2024.pdf), whose URL filename has a different year. The evidence artifact records normalized table facts and time-zone conversion, not a claimed hash of PDF bytes that were not retrieved. A separately frozen dependency run replaces all units on the affected dates and following 62 calendar days. Other missing calendar evidence remains explicit.

## Verification and reproducibility

Tests: **816 passed, 36 subtests passed in 323.28s (0:05:23)**. Native integration, future-perturbation and regression controls passed. Every primary and recovery completion hash was checked; 323,676 distinct input files were verified. Resume reproduced all 57 jobs and the selected date completion byte-for-byte. Counts reconcile with zero duplicate within-branch opportunities and zero recorded future leakage. All 341 final charts were visually inspected. The accepted implementation's 245 files are unchanged.

Registry: `63e572556212f5c02f524af1cb8b70ef4e35eaa07649c24b78bb604d79f9cbf6`. Calendar composition: `8508a2bfadc1af381bf1b35345d9c6519a7d07999d18955cfddc7bd500b4ecb2`. [Frozen protocol](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/protocol/MEASUREMENT_PROTOCOL_1_1.json), [full reconciliation](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/validation/CENSUS_RECONCILIATION.json), [input verification and resolved failure history](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/validation/FULL_INPUT_VERIFICATION.json), [chart inspection](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/VISUAL_QA.json). Earlier runs, raw/source files and pre-existing documentation corrections are preserved.

Run from `/workspace`; these commands resume the frozen identities:

```bash
export PYTHONPATH=/workspace/implementation/src
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python -m trading_research.research.method_pack.measurement_runner run --run-root /workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1 --workers 16
python /workspace/implementation/reports/phase1-live/historical-measurement/tools/recover_calendars.py run --workers 2
python /workspace/implementation/reports/phase1-live/historical-measurement/tools/finish_aggregation.py --run-root /workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1 --collect --workers 16
python /workspace/implementation/reports/phase1-live/historical-measurement/tools/finish_collection.py --run-root /workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1
python /workspace/implementation/reports/phase1-live/historical-measurement/tools/verify_census.py --run-root /workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1
python /workspace/implementation/reports/phase1-live/historical-measurement/tools/render_census.py --run-root /workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1
```

Rendering regenerates image files; visual inspection must be repeated if their content changes. `publish_local_report.py` requires a completed visual-inspection receipt before updating current documentation. All helper identities are recorded in the final artifact manifest.

[Per-setup records](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/setup-records.jsonl.gz) · [Coverage/exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz) · [Context and other observations](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/non-setup-observations.jsonl.gz) · [Machine-readable results](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/MEASUREMENT_RESULTS.json) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md).

Bulk daily jobs, native derivations and full record streams remain on the workspace volume, following the repository’s existing historical-replay policy. Git publishes the implementation, reports, charts, frozen identities and verification receipts; their recorded hashes identify the retained local evidence.

## Required family tables

Here `n` is the observed qualifying market-setup count, including the explicitly separated limited-session subset. It is not a fill count or the historical predicate-audit `p+f`.

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | full acquired historical measurement | 3912 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/JJ-TBR.md |
| GB-FAIL | full acquired historical measurement | 7589 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-FAIL.md |
| GB-VWAP | full acquired historical measurement | 499 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-VWAP.md |
| GB-SCALP | full acquired historical measurement | 3066 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/GB-SCALP.md |
| SIRES | full acquired historical measurement | 2538 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/SIRES.md |
| SAINT-AMT | full acquired historical measurement | 785 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/SAINT-AMT.md |
| MEMBER-TWO-REASONS | full acquired historical measurement | 352 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/MEMBER-TWO-REASONS.md |
| KEANI-OPEN-ABOVE-VALUE | full acquired historical measurement | 6 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/KEANI-OPEN-ABOVE-VALUE.md |
| REFILL-STUDY | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/REFILL-STUDY.md |
| JETBUNDLE-STATES | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/JETBUNDLE-STATES.md |
| STOIC-DATA | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-DATA.md |
| STOIC-RISK | full acquired historical measurement | 0 | not claimed | all sessions searched; input-limited scope explicit | implementation/reports/phase1-live/historical-measurement/run-1.0.1/methods/STOIC-RISK.md |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | M01 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| GB-FAIL | M02 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| GB-VWAP | M03 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| GB-SCALP | M04 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| SIRES | M05 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| SAINT-AMT | M06 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| MEMBER-TWO-REASONS | M07 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| KEANI-OPEN-ABOVE-VALUE | M08 | measured observed setup population | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| REFILL-STUDY | M09 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| JETBUNDLE-STATES | M10 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| STOIC-DATA | M11 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
| STOIC-RISK | M12 | non-entry scope retained; setup denominator not applicable | pass: full suite and native controls | 0 | 0 | fixed rules; exact limitations retained; outcomes are prices, not fills |
