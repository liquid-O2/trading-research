# GB-FAIL: current v2 research

The declared annual sample covers 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. Every declared branch/date job is retained. These are ordered market or process observations under frozen research assumptions. They are not reconstructed author trades or fills.

| Branch/unit | Unit | N observed | n | p | f | u | Scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nyam_box | market_sequence | 8 | 8 | 3 | 5 | 0 | bounded_observed_population_measured |
| previous_hour | market_sequence | 38 | 38 | 13 | 25 | 0 | bounded_observed_population_measured |
| asia_tdo_case | market_sequence | 10 | 10 | 1 | 9 | 0 | bounded_observed_population_measured |
| prior_day_level | market_sequence | 9 | 9 | 2 | 7 | 0 | observed_subset_with_input_limits |
| prior_week_level | market_sequence | 7 | 7 | 1 | 6 | 0 | observed_subset_with_input_limits |
| prior_month_level | market_sequence | 3 | 3 | 2 | 1 | 0 | observed_subset_with_input_limits |
| cash_open_reclaim_case | market_sequence | 6 | 6 | 0 | 6 | 0 | observed_subset_with_input_limits |
| mss_fvg_refinement | market_sequence | 3 | 3 | 0 | 3 | 0 | bounded_observed_population_measured |

## nyam_box (catalog branch)

finished 09–10 box → contextual sweep → five-minute reclaim → opposing box liquidity. Source: GB pp.21,23,25,27,30–35,38–40,43.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Native jobs: 7. Observed sequence p/f/u: 3/5/0; n=8.

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 2 | 1 | 1 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/GB-FAIL--branch--nyam_box.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/GB-FAIL--branch--nyam_box.json.gz) |
| 2022-01-03 | 1 | 0 | 1 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/GB-FAIL--branch--nyam_box.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | True | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/GB-FAIL--branch--nyam_box.json.gz) |
| 2024-01-02 | 1 | 1 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/GB-FAIL--branch--nyam_box.json.gz) |
| 2025-01-02 | 2 | 1 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/GB-FAIL--branch--nyam_box.json.gz) |
| 2026-01-02 | 1 | 0 | 1 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/GB-FAIL--branch--nyam_box.json.gz) |

## previous_hour (catalog branch)

finished prior clock-hour reference → contextual sweep → reclaim → opposing hour liquidity. Source: GB pp.21,23,25,27,30–35,38–40,43.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Native jobs: 7. Observed sequence p/f/u: 13/25/0; n=38.

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 6 | 1 | 5 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/GB-FAIL--branch--previous_hour.json.gz) |
| 2021-01-04 | 6 | 0 | 6 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/GB-FAIL--branch--previous_hour.json.gz) |
| 2022-01-03 | 6 | 6 | 0 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/GB-FAIL--branch--previous_hour.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | True | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/GB-FAIL--branch--previous_hour.json.gz) |
| 2024-01-02 | 8 | 3 | 5 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/GB-FAIL--branch--previous_hour.json.gz) |
| 2025-01-02 | 6 | 2 | 4 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/GB-FAIL--branch--previous_hour.json.gz) |
| 2026-01-02 | 6 | 1 | 5 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/GB-FAIL--branch--previous_hour.json.gz) |

## asia_tdo_case (catalog branch)

completed Asia range + midnight TDO → sweep → reclaim with TDO confirmation. Source: GB pp.21,23,25,27,30–35,38–40,43.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Native jobs: 7. Observed sequence p/f/u: 1/9/0; n=10.

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/GB-FAIL--branch--asia_tdo_case.json.gz) |
| 2021-01-04 | 2 | 0 | 2 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/GB-FAIL--branch--asia_tdo_case.json.gz) |
| 2022-01-03 | 2 | 0 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/GB-FAIL--branch--asia_tdo_case.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | True | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/GB-FAIL--branch--asia_tdo_case.json.gz) |
| 2024-01-02 | 1 | 0 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/GB-FAIL--branch--asia_tdo_case.json.gz) |
| 2025-01-02 | 2 | 1 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/GB-FAIL--branch--asia_tdo_case.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/GB-FAIL--branch--asia_tdo_case.json.gz) |

## prior_day_level (catalog branch)

same-contract previous actual RTH reference → sweep/reclaim → selected opposing level. Source: GB pp.21,23,25,27,30–35,38–40,43.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Native jobs: 7. Observed sequence p/f/u: 2/7/0; n=9.

Observed scope/record limits: same_contract_prior_scope_unknown (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/GB-FAIL--branch--prior_day_level.json.gz) |
| 2021-01-04 | 2 | 0 | 2 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/GB-FAIL--branch--prior_day_level.json.gz) |
| 2022-01-03 | 2 | 0 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/GB-FAIL--branch--prior_day_level.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | True | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/GB-FAIL--branch--prior_day_level.json.gz) |
| 2024-01-02 | 1 | 0 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/GB-FAIL--branch--prior_day_level.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/GB-FAIL--branch--prior_day_level.json.gz) |
| 2026-01-02 | 2 | 2 | 0 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/GB-FAIL--branch--prior_day_level.json.gz) |

## prior_week_level (catalog branch)

same-contract prior-week matching sessions → sweep/reclaim → selected opposing level. Source: GB pp.21,23,25,27,30–35,38–40,43.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Native jobs: 7. Observed sequence p/f/u: 1/6/0; n=7.

Observed scope/record limits: same_contract_prior_scope_unknown (4 job records); calendar_unverified (3 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/GB-FAIL--branch--prior_week_level.json.gz) |
| 2021-01-04 | 2 | 1 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/GB-FAIL--branch--prior_week_level.json.gz) |
| 2022-01-03 | 1 | 0 | 1 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/GB-FAIL--branch--prior_week_level.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | True | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/GB-FAIL--branch--prior_week_level.json.gz) |
| 2024-01-02 | 1 | 0 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/GB-FAIL--branch--prior_week_level.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | False | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/GB-FAIL--branch--prior_week_level.json.gz) |
| 2026-01-02 | 1 | 0 | 1 | 0 | False | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/GB-FAIL--branch--prior_week_level.json.gz) |

## prior_month_level (catalog branch)

same-contract prior-month matching sessions → sweep/reclaim → selected opposing level. Source: GB pp.21,23,25,27,30–35,38–40,43.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Native jobs: 7. Observed sequence p/f/u: 2/1/0; n=3.

Observed scope/record limits: same_contract_prior_scope_unknown (102 job records); calendar_unverified (5 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/GB-FAIL--branch--prior_month_level.json.gz) |
| 2021-01-04 | 1 | 1 | 0 | 0 | False | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/GB-FAIL--branch--prior_month_level.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | False | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/GB-FAIL--branch--prior_month_level.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/GB-FAIL--branch--prior_month_level.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | False | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/GB-FAIL--branch--prior_month_level.json.gz) |
| 2025-01-02 | 1 | 1 | 0 | 0 | False | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/GB-FAIL--branch--prior_month_level.json.gz) |
| 2026-01-02 | 0 | 0 | 0 | 0 | False | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/GB-FAIL--branch--prior_month_level.json.gz) |

## cash_open_reclaim_case (catalog branch)

09:30 open → below-open manipulation → reclaim → retracement objective with low invalidation. Source: GB pp.21,23,25,27,30–35,38–40,43.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Native jobs: 7. Observed sequence p/f/u: 0/6/0; n=6.

Observed scope/record limits: cash_open_order_unknown (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/GB-FAIL--branch--cash_open_reclaim_case.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/GB-FAIL--branch--cash_open_reclaim_case.json.gz) |
| 2022-01-03 | 1 | 0 | 1 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/GB-FAIL--branch--cash_open_reclaim_case.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/GB-FAIL--branch--cash_open_reclaim_case.json.gz) |
| 2024-01-02 | 1 | 0 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/GB-FAIL--branch--cash_open_reclaim_case.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/GB-FAIL--branch--cash_open_reclaim_case.json.gz) |
| 2026-01-02 | 1 | 0 | 1 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/GB-FAIL--branch--cash_open_reclaim_case.json.gz) |

## mss_fvg_refinement (catalog branch)

completed parent reclaim → later three 2-minute candles → MSS plus actual wick FVG; annotation unit. Source: GB pp.21,23,25,27,30–35,38–40,43.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Native jobs: 7. Observed sequence p/f/u: 0/3/0; n=3.

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/GB-FAIL--branch--mss_fvg_refinement.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/GB-FAIL--branch--mss_fvg_refinement.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/GB-FAIL--branch--mss_fvg_refinement.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | True | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/GB-FAIL--branch--mss_fvg_refinement.json.gz) |
| 2024-01-02 | 1 | 0 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/GB-FAIL--branch--mss_fvg_refinement.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/GB-FAIL--branch--mss_fvg_refinement.json.gz) |
| 2026-01-02 | 0 | 0 | 0 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/GB-FAIL--branch--mss_fvg_refinement.json.gz) |

Counts from dependent branches are not a pooled family win rate. The pilot is separate. Full-feed completeness and author-exact measurement remain unestablished.
