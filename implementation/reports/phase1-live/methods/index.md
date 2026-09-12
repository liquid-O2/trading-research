# Phase 1 method cohort and chart audit

All 12 acquired-scope reports were refreshed after reading their FORMULAS candidate selectors. None of the 50 confirmed branches has a complete source-defined selector. Each has an explicit run-specific `holes.jsonl` record naming the missing inputs and producer rules. Sires also retains four separately excluded incomplete cases.

**Every historical cohort has p=f=u=n=N=0, rate=null and interval=null.** No historical method success rate has been measured. Synthetic fixtures, chart diagnostics and archive inventory rows are excluded from the sample.

[Direct chart/figure comparisons](/workspace/implementation/reports/phase1-live/methods/CHART_CHECK.md) cover all 12 methods, including dated computable geometry, explicitly limited input comparisons, and unavailable process replays. The primary assistant performed every visual comparison without subagents. FORMULAS was unchanged and Phase 2 was not started.

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
| JETBUNDLE-STATES | M10 | source_hole | 141 software checks; 0 failures | 0 emitted | 0 emitted | 5 selector holes; native_source_reconstruction_blocked |
| STOIC-DATA | M11 | source_hole | 138 software checks; 0 failures | 0 emitted | 0 emitted | 2 selector holes; process_geometry_unavailable_vintage_supplement |
| STOIC-RISK | M12 | source_hole | 97 software checks; 0 failures | 0 emitted | 0 emitted | 3 selector holes; dated_replay_unavailable_printed_arithmetic_checked |

Implementation content hash: `abb39481bd9ca8e2da5c2d0cc97749a5c61b92f3ab769d7131ddc0989eab88d8`. Source-selector audit hash: `2e41d96c71e0e3a714624b532ed3b4ba499e28e116539803084dd8259d26951c`.

[Machine cohort verification](/workspace/implementation/reports/phase1-live/methods/pass-summary.json) · [Commands and output](/workspace/implementation/reports/phase1-live/methods/command-results.json) · [Chart and report verification](/workspace/implementation/reports/phase1-live/methods/charts/final-verification.json)

[Adapter repairs](/workspace/implementation/reports/phase1-live/adapter-repairs.md) · [Coverage audit](/workspace/implementation/reports/phase1-live/coverage-audit/README.md) · [Runner documentation](/workspace/implementation/src/trading_research/research/method_pack/README.md)
