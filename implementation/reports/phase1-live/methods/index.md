# Phase 1 method-pack-v1 verification

All 12 acquired-scope method-pass commands exited 0 after the adapter repairs. Every JSON/Markdown report, declared artifact hash, fixture inventory, cohort total and year total passed verification.

Validation: 201 tests passed; 166 unique recipes passed 1,316 object fixture/mutation checks; all 373 typed method fields have declared producers.

Historical N=0 for every method. The pack names incomplete source selectors, and no episode manifest was supplied. These source holes remain explicit; synthetic fixtures are excluded from historical cohorts. This is distinct from the repaired data adapters and recovered format gaps.

[Adapter repairs and recovered windows](/workspace/implementation/reports/phase1-live/adapter-repairs.md) · [Acquired coverage audit](/workspace/implementation/reports/phase1-live/coverage-audit/README.md)

Implementation content hash: `2cab034db2917ee91fe1e35d3256b71efcce07a688cc9c1a0fc51c3073f05f32`.

Method | Objects | Fixture checks | Exit | Status | Report
--- | ---: | ---: | ---: | --- | ---
JJ-TBR | 62 | 430 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/jj-tbr.md)
GB-FAIL | 25 | 210 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/gb-fail.md)
GB-VWAP | 11 | 123 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/gb-vwap.md)
GB-SCALP | 15 | 132 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/gb-scalp.md)
SIRES | 117 | 961 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/sires.md)
SAINT-AMT | 36 | 295 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/saint-amt.md)
MEMBER-TWO-REASONS | 28 | 233 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/member-two-reasons.md)
KEANI-OPEN-ABOVE-VALUE | 24 | 205 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/keani-open-above-value.md)
REFILL-STUDY | 27 | 220 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/refill-study.md)
JETBUNDLE-STATES | 15 | 141 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/jetbundle-states.md)
STOIC-DATA | 14 | 138 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/stoic-data.md)
STOIC-RISK | 8 | 97 | 0 | source_hole | [Report](/workspace/implementation/reports/phase1-live/methods/stoic-risk.md)

[Machine verification summary](/workspace/implementation/reports/phase1-live/methods/pass-summary.json) · [Exact commands and output](/workspace/implementation/reports/phase1-live/methods/command-results.json)

[Runner documentation](/workspace/implementation/src/trading_research/research/method_pack/README.md)
