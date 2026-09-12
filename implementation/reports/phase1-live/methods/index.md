# Phase 1 source review, reconstructions and historical cohorts

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
