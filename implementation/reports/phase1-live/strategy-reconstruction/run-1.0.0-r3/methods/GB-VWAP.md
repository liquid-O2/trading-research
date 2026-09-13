# GB-VWAP: current v2 research

The declared annual sample covers 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. Every declared branch/date job is retained. These are ordered market or process observations under frozen research assumptions. They are not reconstructed author trades or fills.

| Branch/unit | Unit | N observed | n | p | f | u | Scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| source_long | market_sequence | 3 | 2 | 2 | 0 | 1 | observed_subset_with_input_limits |

## source_long (catalog branch)

both finished session highs → close above → later contemporaneous VWAP return → long risk/continuation observation. Source: GB p.33 posts 2026329904690712970/2026386393820283204.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_vwap`. Native jobs: 7. Observed sequence p/f/u: 2/0/1; n=2.

Observed scope/record limits: session_reference_missing (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 1 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/GB-VWAP--branch--source_long.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/GB-VWAP--branch--source_long.json.gz) |
| 2022-01-03 | 1 | 1 | 0 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/GB-VWAP--branch--source_long.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/GB-VWAP--branch--source_long.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/GB-VWAP--branch--source_long.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/GB-VWAP--branch--source_long.json.gz) |
| 2026-01-02 | 1 | 1 | 0 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/GB-VWAP--branch--source_long.json.gz) |

Counts from dependent branches are not a pooled family win rate. The pilot is separate. Full-feed completeness and author-exact measurement remain unestablished.
