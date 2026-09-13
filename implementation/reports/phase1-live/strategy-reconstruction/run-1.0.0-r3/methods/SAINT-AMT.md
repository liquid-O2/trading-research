# SAINT-AMT: current v2 research

The declared annual sample covers 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. Every declared branch/date job is retained. These are ordered market or process observations under frozen research assumptions. They are not reconstructed author trades or fills.

| Branch/unit | Unit | N observed | n | p | f | u | Scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| continuation_retest | market_sequence | 5 | 5 | 0 | 5 | 0 | observed_subset_with_input_limits |
| trapped_buyers_retest | market_sequence | 3 | 3 | 0 | 3 | 0 | observed_subset_with_input_limits |
| failed_auction_return | market_sequence | 9 | 5 | 0 | 5 | 4 | observed_subset_with_input_limits |
| poc_traversal | market_sequence | 9 | 5 | 0 | 5 | 4 | observed_subset_with_input_limits |

## continuation_retest (catalog branch)

fitted HTF accepted balance → actual LTF balance break → same-boundary retest → repeated directional aggression. Source: RTVP pp.3–11;WIC pp.7–10.

Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_saint`. Native jobs: 7. Observed sequence p/f/u: 0/5/0; n=5.

Observed scope/record limits: no distinct confirmed LTF price balance (3 job records); no confirmed HTF price balance in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 2 | 0 | 2 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SAINT-AMT--branch--continuation_retest.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SAINT-AMT--branch--continuation_retest.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | False | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SAINT-AMT--branch--continuation_retest.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SAINT-AMT--branch--continuation_retest.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | False | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SAINT-AMT--branch--continuation_retest.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 0 | False | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SAINT-AMT--branch--continuation_retest.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SAINT-AMT--branch--continuation_retest.json.gz) |

## trapped_buyers_retest (catalog branch)

two distinct earlier upper buying failures → current LTF down break → same-boundary retest → repeated body selling. Source: TRAP pp.3–10;WIC pp.7–10.

Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_saint`. Native jobs: 7. Observed sequence p/f/u: 0/3/0; n=3.

Observed scope/record limits: no distinct confirmed LTF price balance (3 job records); no confirmed HTF price balance in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SAINT-AMT--branch--trapped_buyers_retest.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SAINT-AMT--branch--trapped_buyers_retest.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | False | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SAINT-AMT--branch--trapped_buyers_retest.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SAINT-AMT--branch--trapped_buyers_retest.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | False | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SAINT-AMT--branch--trapped_buyers_retest.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 0 | False | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SAINT-AMT--branch--trapped_buyers_retest.json.gz) |
| 2026-01-02 | 1 | 0 | 1 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SAINT-AMT--branch--trapped_buyers_retest.json.gz) |

## failed_auction_return (catalog branch)

original balance → distinct older value tested/rejected → original balance reacceptance → local control. Source: AMTL pp.8–10.

Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_saint`. Native jobs: 7. Observed sequence p/f/u: 0/5/4; n=5.

Observed scope/record limits: no confirmed HTF price balance in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 2 | 0 | 2 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SAINT-AMT--branch--failed_auction_return.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SAINT-AMT--branch--failed_auction_return.json.gz) |
| 2022-01-03 | 1 | 0 | 1 | 1 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SAINT-AMT--branch--failed_auction_return.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SAINT-AMT--branch--failed_auction_return.json.gz) |
| 2024-01-02 | 1 | 0 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SAINT-AMT--branch--failed_auction_return.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 1 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SAINT-AMT--branch--failed_auction_return.json.gz) |
| 2026-01-02 | 0 | 0 | 0 | 2 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SAINT-AMT--branch--failed_auction_return.json.gz) |

## poc_traversal (catalog branch)

original balance reacceptance → aggressive POC passage → source hold → far-edge objective. Source: RTVP pp.5–8;AMTL pp.8–11.

Scanner: `trading_research.research.method_pack.historical_auction_scanners:scan_saint`. Native jobs: 7. Observed sequence p/f/u: 0/5/4; n=5.

Observed scope/record limits: no confirmed HTF price balance in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 2 | 0 | 2 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SAINT-AMT--branch--poc_traversal.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 1 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SAINT-AMT--branch--poc_traversal.json.gz) |
| 2022-01-03 | 2 | 0 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SAINT-AMT--branch--poc_traversal.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SAINT-AMT--branch--poc_traversal.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 1 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SAINT-AMT--branch--poc_traversal.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 1 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SAINT-AMT--branch--poc_traversal.json.gz) |
| 2026-01-02 | 1 | 0 | 1 | 1 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SAINT-AMT--branch--poc_traversal.json.gz) |

Counts from dependent branches are not a pooled family win rate. The pilot is separate. Full-feed completeness and author-exact measurement remain unestablished.
