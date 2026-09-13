# STOIC-DATA: current v2 research

The declared annual sample covers 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. Every declared branch/date job is retained. These are ordered market or process observations under frozen research assumptions. They are not reconstructed author trades or fills.

| Branch/unit | Unit | N observed | n | p | f | u | Scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| process_review | process_record | 1 | 1 | 1 | 0 | 0 | bounded_observed_population_measured |
| macro_application | process_record | 1 | 1 | 1 | 0 | 0 | observed_subset_with_input_limits |
| unit: macro_application | macro_application | 1 | 1 | 1 | 0 | 0 | observed_subset_with_input_limits |

## process_review (catalog branch)

frozen declared process → uniform inclusion → all observations → winner/loser comparison → prior-sample revision. Source: DATA pp.3–4.

Scanner: `trading_research.research.method_pack.historical_process_scanners:scan_stoic_data`. Native jobs: 1. Observed sequence p/f/u: 1/0/0; n=1.

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-01-02 | 1 | 1 | 0 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/collection/STOIC-DATA--branch--process_review.json.gz) |

## macro_application (catalog branch)

actual vintage admission → selected indicator historical comparison → supplied custom cycle/C-score/trend interpretation. Source: DATA pp.5–6.

Scanner: `trading_research.research.method_pack.historical_process_scanners:scan_stoic_data`. Native jobs: 1. Observed sequence p/f/u: 1/0/0; n=1.

Original source-audit requirement (see reconstruction report for implemented models) (cycle_and_indicator_rules_recorded): source custom indicator set/transforms, C-score/cycle/trend formula and historical interpretation. Existing 20-series/37003-vintage bundles are used directly; initial BLS clocks and specified standardized comparisons are available. Source proprietary transforms and non-initial intraday clocks are not supplied by that recovery. Citation: DATA pp.5–6;O157–O161.

Observed scope/record limits: source custom indicator set/transforms, C-score/cycle/trend formula and historical interpretation (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-01-02 | 1 | 1 | 0 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/collection/STOIC-DATA--branch--macro_application.json.gz) |

## macro_application (additional unit)

actual vintage admission → selected indicator historical comparison → supplied custom cycle/C-score/trend interpretation. Source: DATA pp.5–6.

Scanner: `trading_research.research.method_pack.native_discovery:extra_stoic`. Native jobs: 1. Observed sequence p/f/u: 1/0/0; n=1.

Original source-audit requirement (see reconstruction report for implemented models) (cycle_and_indicator_rules_recorded): source custom indicator set/transforms, C-score/cycle/trend formula and historical interpretation. Existing 20-series/37003-vintage bundles are used directly; initial BLS clocks and specified standardized comparisons are available. Source proprietary transforms and non-initial intraday clocks are not supplied by that recovery. Citation: DATA pp.5–6;O157–O161.

Observed scope/record limits: source custom indicator set/transforms, C-score/cycle/trend formula and historical interpretation (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-01-02 | 1 | 1 | 0 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/collection/STOIC-DATA--unit--macro_application.json.gz) |

Counts from dependent branches are not a pooled family win rate. The pilot is separate. Full-feed completeness and author-exact measurement remain unestablished.
