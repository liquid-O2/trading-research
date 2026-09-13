# Phase 1 source review, reconstructions and historical cohorts

<!-- phase1-strategy-current -->
Current strategy reconstruction: **66 setups, 258 no-setup rejections and 0 unavailable market-input candidates** in the declared evaluation sample. Context and research units are separate.

Personal size, account limits and executed-order records do not gate setups. Auction states, QQQ gamma/key levels, P-zones and macro context have explicit source-inspired implementations. A no-setup rejection is not a losing trade or a software failure.

[Completion report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/COMPLETION_REPORT.md) · [Strategy results](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/STRATEGY_RESULTS.md) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md) · [Charts](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/charts/README.md).

Validation: 803 passed, 36 subtests passed in 110.74s (0:01:50); 776 completed jobs across all 58 branch/extra units; 77 primary charts visually checked.

| Family | Current strategy report |
| --- | --- |
| JJ-TBR | [JJ-TBR](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/JJ-TBR.md) |
| GB-FAIL | [GB-FAIL](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-FAIL.md) |
| GB-VWAP | [GB-VWAP](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-VWAP.md) |
| GB-SCALP | [GB-SCALP](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-SCALP.md) |
| SIRES | [SIRES](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/SIRES.md) |
| SAINT-AMT | [SAINT-AMT](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/SAINT-AMT.md) |
| MEMBER-TWO-REASONS | [MEMBER-TWO-REASONS](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/MEMBER-TWO-REASONS.md) |
| KEANI-OPEN-ABOVE-VALUE | [KEANI-OPEN-ABOVE-VALUE](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/KEANI-OPEN-ABOVE-VALUE.md) |
| REFILL-STUDY | [REFILL-STUDY](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/REFILL-STUDY.md) |
| JETBUNDLE-STATES | [JETBUNDLE-STATES](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/JETBUNDLE-STATES.md) |
| STOIC-DATA | [STOIC-DATA](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/STOIC-DATA.md) |
| STOIC-RISK | [STOIC-RISK](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/STOIC-RISK.md) |
<!-- /phase1-strategy-current -->

## Preserved v2 source-audit baseline

The following section records the earlier, broader source-audit scope. Its personal-record requirements and p/f/u counts are historical comparisons; the strategy scope and current classifications above supersede them.

<!-- phase1-native-v2-current -->
Current registry/run v2.0.0 is accepted under identity `1ab8b9d7eb2e8aa36c053033754aac854908a2e90373457fb730671329dc5a60`. All **776 declared jobs** completed across the seven-date pilot and seven-date evaluation sample, with all **50 branches and eight additional units** retained. This is a bounded annual engineering/research sample, not a full-archive census. Pilot/evaluation overlap and prior outcome exposure are explicit; their counts are never pooled.

The implementation uses owned MBP-1 event-time executions, same-contract references and a versioned NQ session policy. Author-exact selections, actual orders/fills and account records remain separate. **Software completion does not establish full historical author-method measurement or profitability.**

[Current completion report and reproduction commands](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md) · [Current branch results](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/RESULTS.md) · [Authoritative branch/object/operand manifest](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/registry/coverage.json) · [Diagnostic chart index](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/charts/README.md)

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | v2 bounded native research | 52 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/JJ-TBR.md |
| GB-FAIL | v2 bounded native research | 68 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/GB-FAIL.md |
| GB-VWAP | v2 bounded native research | 2 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/GB-VWAP.md |
| GB-SCALP | v2 bounded native research | 0 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/GB-SCALP.md |
| SIRES | v2 bounded native research | 69 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/SIRES.md |
| SAINT-AMT | v2 bounded native research | 17 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/SAINT-AMT.md |
| MEMBER-TWO-REASONS | v2 bounded native research | 2 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/MEMBER-TWO-REASONS.md |
| KEANI-OPEN-ABOVE-VALUE | v2 bounded native research | 6 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/KEANI-OPEN-ABOVE-VALUE.md |
| REFILL-STUDY | v2 bounded native research | 0 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/REFILL-STUDY.md |
| JETBUNDLE-STATES | v2 bounded native research | 0 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/JETBUNDLE-STATES.md |
| STOIC-DATA | v2 bounded native research | 1 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/STOIC-DATA.md |
| STOIC-RISK | v2 bounded native research | 0 | not established | executed; input limits retained | implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/STOIC-RISK.md |

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | M01 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| GB-FAIL | M02 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| GB-VWAP | M03 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| GB-SCALP | M04 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| SIRES | M05 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| SAINT-AMT | M06 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| MEMBER-TWO-REASONS | M07 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| KEANI-OPEN-ABOVE-VALUE | M08 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| REFILL-STUDY | M09 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| JETBUNDLE-STATES | M10 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| STOIC-DATA | M11 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |
| STOIC-RISK | M12 | controls and native replay pass | pass | 0 | 0 | selected source controls; native jobs retained; author-exact unknown |

<!-- /phase1-native-v2-current -->

## Historical source-method pass reports

> **Historical source-method reports and audits.** “Latest” and “missing implementation” statements below belong to the earlier review stages and were followed by repairs and empirical acceptance. For current status use [PHASE.md](/workspace/planning/phase-1-live/PHASE.md); for readable methods with accepted empirical observations use the [12 live wiki method pages](/workspace/planning/phase-1-live/wiki/index.md). Source-method holes here and later research-comparison results answer different questions.

[Full implementation audit](/workspace/implementation/reports/phase1-live/methods/FULL_AUDIT.md) · [All 166 object reviews](/workspace/implementation/reports/phase1-live/methods/OBJECT_AUDIT.md) · [Proposed implementation plan](/workspace/implementation/reports/phase1-live/methods/IMPLEMENTATION_PLAN.md). The latest audit finds substantial documented behavior missing or incorrect, 27 reproduced object-level gaps, and omitted source settings/process details. The earlier passing fixtures and `source_hole` statuses below are retained run results, not certification of full implementation. No implementation was changed by this audit.

[Latest profile coverage check](/workspace/implementation/reports/phase1-live/methods/PROFILE_COVERAGE_CHECK.md): the wiki and formulas already cover the requested profile types, while full profile rows, dated identities and developing snapshots remain partly implemented. The check also corrects the GB sweep-entry interpretation and records the deferred parameter searches. The tables below retain the previous run's cohort results; this coverage check did not run a new cohort.

The source reread corrected the AAPL-only interpretation, recovered Stoic’s usable process and source-specific GB intent, and added two dated reconstructions. [Source findings](/workspace/implementation/reports/phase1-live/methods/SOURCE_RECHECK.md) · [Source-fit figures and results](/workspace/implementation/reports/phase1-live/methods/reconstructions/README.md). Macro work is deprioritized.

All 12 source-faithful acquired-scope reports were refreshed. Each of the 50 branches still lacks a complete automatic source selector and has an explicit run-specific hole. Sires also retains four separately excluded incomplete cases. **Historical p=f=u=n=N=0, rate=null and interval=null.** The new reconstruction examples are calibration cases; they do not supply actual executions or a historical win rate.

[Direct chart/figure comparisons](/workspace/implementation/reports/phase1-live/methods/CHART_CHECK.md) cover all 12 methods, including dated computable geometry, explicitly limited input comparisons, and unavailable process replays. The primary assistant performed every visual comparison without subagents. FORMULAS changed only for the source-supported NQ eligibility, depth-scope and count-provenance correction; its affected hashes were re-audited. The research reconstructions have separate assumptions. Phase 2 was not started.

All 12 commands exited 0. Cohort arithmetic, 50 branch-hole records, report artifacts and hashes were verified. Fixture entries below are software checks only. With N=0, faithful disagreements are not estimable; zero leakage/proxy emissions describe empty historical output and do not demonstrate method performance.

## PHASE

| family | variant | n | faithful_disagreements | status | report path |
|---|---|---:|---|---|---|
| JJ-TBR | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/jj-tbr.md) |
| GB-FAIL | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/gb-fail.md) |
| GB-VWAP | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/gb-vwap.md) |
| GB-SCALP | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/gb-scalp.md) |
| SIRES | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/sires.md) |
| SAINT-AMT | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/saint-amt.md) |
| MEMBER-TWO-REASONS | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/member-two-reasons.md) |
| KEANI-OPEN-ABOVE-VALUE | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/keani-open-above-value.md) |
| REFILL-STUDY | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/refill-study.md) |
| JETBUNDLE-STATES | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/jetbundle-states.md) |
| STOIC-DATA | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/stoic-data.md) |
| STOIC-RISK | method-pack-v1 | 0 | N/A (N=0) | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/stoic-risk.md) |

## Audit

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
|---|---|---|---|---|---|---|
| JJ-TBR | M01 | source_hole | 430 software checks; 0 failures | 0 emitted | 0 emitted | 8 selector holes; geometry_checked |
| GB-FAIL | M02 | source_hole | 210 software checks; 0 failures | 0 emitted | 0 emitted | 8 selector holes; partial_geometry_only |
| GB-VWAP | M03 | source_hole | 123 software checks; 0 failures | 0 emitted | 0 emitted | 1 selector holes; source_geometry_blocked_comparisons_only |
| GB-SCALP | M04 | source_hole | 132 software checks; 0 failures | 0 emitted | 0 emitted | 2 selector holes; comparison_parent_only |
| SIRES | M05 | source_hole | 961 software checks; 0 failures | 0 emitted | 0 emitted | 12 selector holes; period_geometry_checked |
| SAINT-AMT | M06 | source_hole | 295 software checks; 0 failures | 0 emitted | 0 emitted | 4 selector holes; native_profile_only |
| MEMBER-TWO-REASONS | M07 | source_hole | 233 software checks; 0 failures | 0 emitted | 0 emitted | 2 selector holes; native_profile_only |
| KEANI-OPEN-ABOVE-VALUE | M08 | source_hole | 205 software checks; 0 failures | 0 emitted | 0 emitted | 1 selector holes; A_period_geometry_checked |
| REFILL-STUDY | M09 | source_hole | 220 software checks; 0 failures | 0 emitted | 0 emitted | 2 selector holes; native_print_geometry_only |
| JETBUNDLE-STATES | M10 | source_hole | 141 software checks; 0 failures | 0 emitted | 0 emitted | 5 selector holes; NQ_eligible_state_classifier_undefined |
| STOIC-DATA | M11 | source_hole | 138 software checks; 0 failures | 0 emitted | 0 emitted | 2 selector holes; process_geometry_unavailable_vintage_supplement |
| STOIC-RISK | M12 | source_hole | 97 software checks; 0 failures | 0 emitted | 0 emitted | 3 selector holes; dated_replay_unavailable_printed_arithmetic_checked |

Implementation content hash: `30e8f63115b6ecb6d5ab6c62aa8e67675a82cfcfc159f2737d963484f6a9bbf9`. Source-selector audit hash: `6119ab2fab40d794ad4fc39d360236d1978b8f4744f58f77b2293f77a55a9006`.

[Machine cohort verification](/workspace/implementation/reports/phase1-live/methods/pass-summary.json) · [Commands and output](/workspace/implementation/reports/phase1-live/methods/command-results.json) · [Chart and report verification](/workspace/implementation/reports/phase1-live/methods/charts/final-verification.json)

[Adapter repairs](/workspace/implementation/reports/phase1-live/adapter-repairs.md) · [Coverage audit](/workspace/implementation/reports/phase1-live/coverage-audit/README.md) · [Runner documentation](/workspace/implementation/src/trading_research/research/method_pack/README.md)
