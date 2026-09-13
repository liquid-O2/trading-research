# SIRES: current v2 research

The declared annual sample covers 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. Every declared branch/date job is retained. These are ordered market or process observations under frozen research assumptions. They are not reconstructed author trades or fills.

| Branch/unit | Unit | N observed | n | p | f | u | Scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dom_rejection | market_sequence | 8 | 5 | 1 | 4 | 3 | observed_subset_with_input_limits |
| absorption_reward_retest | market_sequence | 8 | 7 | 0 | 7 | 1 | observed_subset_with_input_limits |
| stop_four_stage | market_sequence | 8 | 7 | 0 | 7 | 1 | observed_subset_with_input_limits |
| footprint_confirmed_reaction | market_sequence | 8 | 8 | 0 | 8 | 0 | observed_subset_with_input_limits |
| vwap_deviation_fade | market_sequence | 9 | 7 | 0 | 7 | 2 | observed_subset_with_input_limits |
| ofm_aggressive | market_sequence | 8 | 8 | 0 | 8 | 0 | observed_subset_with_input_limits |
| ofm_passive | market_sequence | 5 | 3 | 0 | 3 | 2 | observed_subset_with_input_limits |
| clean_squeeze | market_sequence | 8 | 5 | 0 | 5 | 3 | observed_subset_with_input_limits |
| balance_failure_fade | market_sequence | 8 | 5 | 0 | 5 | 3 | observed_subset_with_input_limits |
| defended_band_continuation | market_sequence | 2 | 2 | 0 | 2 | 0 | observed_subset_with_input_limits |
| microbalance_break | market_sequence | 13 | 13 | 6 | 7 | 0 | observed_subset_with_input_limits |
| kg1_retest | market_sequence | 8 | 8 | 4 | 4 | 0 | observed_subset_with_input_limits |
| unit: case_description | case_description | 0 | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |
| unit: management | management | 0 | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |
| unit: reentry | reentry | 0 | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |

## dom_rejection (catalog branch)

planned level → arriving effort/no progress → depth-one defense/rejection. Source: DOM6/DOM7 pp.3–7.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 1/4/3; n=5.

Observed scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 2 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--dom_rejection.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--dom_rejection.json.gz) |
| 2022-01-03 | 1 | 1 | 0 | 1 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--dom_rejection.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--dom_rejection.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--dom_rejection.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--dom_rejection.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--dom_rejection.json.gz) |

## absorption_reward_retest (catalog branch)

real extreme → opposing effort/passive defense → own reward near origin → distinct reward-area retest/fresh defense. Source: ABS pp.5–13.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 0/7/1; n=7.

Observed scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 1 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--absorption_reward_retest.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--absorption_reward_retest.json.gz) |
| 2022-01-03 | 2 | 0 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--absorption_reward_retest.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--absorption_reward_retest.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--absorption_reward_retest.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--absorption_reward_retest.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--absorption_reward_retest.json.gz) |

## stop_four_stage (catalog branch)

real extreme → defense → replenishment → opposing print thinning → absorber aggression and 2–4 tick lift-off; account -4R checked separately. Source: STOP pp.10,12,14.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 0/7/1; n=7.

Original source-audit requirement (see reconstruction report for implemented models) (daily_r_before, daily_limit_allows_entry): actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Citation: STOP pp.12,14;O140,O145,O150.

Observed scope/record limits: actual account/session closed R and active quantity/order ledger (7 job records); no confirmed alternating-pivot auction in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 1 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--stop_four_stage.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--stop_four_stage.json.gz) |
| 2022-01-03 | 2 | 0 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--stop_four_stage.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--stop_four_stage.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--stop_four_stage.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--stop_four_stage.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--stop_four_stage.json.gz) |

## footprint_confirmed_reaction (catalog branch)

known level → same-candle delta disagreement/absorption → within-candle POC relocation → local flow. Source: FP9 pp.4–7.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 0/8/0; n=8.

Observed scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 2 | 0 | 2 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--footprint_confirmed_reaction.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--footprint_confirmed_reaction.json.gz) |
| 2022-01-03 | 2 | 0 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--footprint_confirmed_reaction.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--footprint_confirmed_reaction.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--footprint_confirmed_reaction.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--footprint_confirmed_reaction.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--footprint_confirmed_reaction.json.gz) |

## vwap_deviation_fade (catalog branch)

auction context → pre-touch executed VWAP/deviation → same-band absorption → local CVD/ladder confirmation. Source: VWAP pp.3–8.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 0/7/2; n=7.

Observed scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 1 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--vwap_deviation_fade.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--vwap_deviation_fade.json.gz) |
| 2022-01-03 | 2 | 0 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--vwap_deviation_fade.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--vwap_deviation_fade.json.gz) |
| 2024-01-02 | 1 | 0 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--vwap_deviation_fade.json.gz) |
| 2025-01-02 | 2 | 0 | 2 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--vwap_deviation_fade.json.gz) |
| 2026-01-02 | 1 | 0 | 1 | 1 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--vwap_deviation_fade.json.gz) |

## ofm_aggressive (catalog branch)

catalyst → release → failed squeeze → catalyst reclaim/refill → initiative/wicks → defended drive retest; source gamma retained separately. Source: OFM pp.3–13;BIG pp.7–14,18;CONT p.10.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 0/8/0; n=8.

Original source-audit requirement (see reconstruction report for implemented models) (short_gamma, long_gamma, branch_regime_allowed): dated source dealer-map regime and selected native product/transform. Local option contract/quote/OI data exist; they do not disclose author dealer positions or gamma-map formula. Observable OFM/fade stages run independently. Citation: BIG pp.14–18;GEX pp.4–20;O033–O040.

Observed scope/record limits: dated source dealer-map regime and selected native product/transform (7 job records); no confirmed alternating-pivot auction in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 2 | 0 | 2 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--ofm_aggressive.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--ofm_aggressive.json.gz) |
| 2022-01-03 | 2 | 0 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--ofm_aggressive.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--ofm_aggressive.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--ofm_aggressive.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--ofm_aggressive.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--ofm_aggressive.json.gz) |

## ofm_passive (catalog branch)

failed squeeze → dying tape/no aggressive failure → actual buyer area → trigger above buyers and stop below aggression. Source: OFM p.14.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 0/3/2; n=3.

Observed scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 1 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--ofm_passive.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--ofm_passive.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 1 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--ofm_passive.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--ofm_passive.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--ofm_passive.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--ofm_passive.json.gz) |
| 2026-01-02 | 1 | 0 | 1 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--ofm_passive.json.gz) |

## clean_squeeze (catalog branch)

catalyst → fast release with no earlier failure → first pullback → opposing absorption → continuation. Source: CONT p.11;OFM p.5.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 0/5/3; n=5.

Observed scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 2 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--clean_squeeze.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--clean_squeeze.json.gz) |
| 2022-01-03 | 1 | 0 | 1 | 1 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--clean_squeeze.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--clean_squeeze.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--clean_squeeze.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--clean_squeeze.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--clean_squeeze.json.gz) |

## balance_failure_fade (catalog branch)

balance extreme → unpaid aggression → leave → same-area retest still unpaid → prior opposite-control target; dated gamma input separate. Source: BIG pp.14–15,18.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 0/5/3; n=5.

Original source-audit requirement (see reconstruction report for implemented models) (short_gamma, long_gamma, branch_regime_allowed): dated source dealer-map regime and selected native product/transform. Local option contract/quote/OI data exist; they do not disclose author dealer positions or gamma-map formula. Observable OFM/fade stages run independently. Citation: BIG pp.14–18;GEX pp.4–20;O033–O040.

Observed scope/record limits: dated source dealer-map regime and selected native product/transform (7 job records); no confirmed alternating-pivot auction in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 2 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--balance_failure_fade.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--balance_failure_fade.json.gz) |
| 2022-01-03 | 1 | 0 | 1 | 1 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--balance_failure_fade.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--balance_failure_fade.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--balance_failure_fade.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--balance_failure_fade.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--balance_failure_fade.json.gz) |

## defended_band_continuation (catalog branch)

prior band control → distinct current return → fresh same-side defense/refresh and executed aggression. Source: NYAM pp.4–5;K18 pp.7,11,14;CONT pp.4–10;ANAT p.7.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 0/2/0; n=2.

Observed scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--defended_band_continuation.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--defended_band_continuation.json.gz) |
| 2022-01-03 | 1 | 0 | 1 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--defended_band_continuation.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--defended_band_continuation.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--defended_band_continuation.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--defended_band_continuation.json.gz) |
| 2026-01-02 | 0 | 0 | 0 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--defended_band_continuation.json.gz) |

## microbalance_break (catalog branch)

larger direction → price-defined alternating-pivot microbalance → strength/break → stop behind that structure. Source: K2345 pp.4–7.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 6/7/0; n=13.

Observed scope/record limits: earlier potential directional breakout close is unknown (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 2 | 1 | 1 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--microbalance_break.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--microbalance_break.json.gz) |
| 2022-01-03 | 4 | 2 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--microbalance_break.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | True | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--microbalance_break.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--microbalance_break.json.gz) |
| 2025-01-02 | 1 | 1 | 0 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--microbalance_break.json.gz) |
| 2026-01-02 | 6 | 2 | 4 | 0 | False | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--microbalance_break.json.gz) |

## kg1_retest (catalog branch)

dated source KG1 → actual same-band retest → aggressive confirmation → supplied management policy. Source: NYAM pp.8–9.

Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Native jobs: 7. Observed sequence p/f/u: 4/4/0; n=8.

Original source-audit requirement (see reconstruction report for implemented models) (source_kg1_level_known, level_known_at): dated source KG1 level/band, identity and version. Retained source cases provide limited readouts; no historical generator/series. Existing options snapshots cannot establish proprietary KG1. Citation: NYAM pp.8–9;K10 pp.4–6;O041.

Observed scope/record limits: dated source KG1 level/band, identity and version (7 job records); KG1/key-gamma model input unavailable (2 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 2 | 1 | 1 | 0 | True | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--branch--kg1_retest.json.gz) |
| 2021-01-04 | 2 | 1 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--branch--kg1_retest.json.gz) |
| 2022-01-03 | 2 | 1 | 1 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--branch--kg1_retest.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--branch--kg1_retest.json.gz) |
| 2024-01-02 | 2 | 1 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--branch--kg1_retest.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--branch--kg1_retest.json.gz) |
| 2026-01-02 | 0 | 0 | 0 | 0 | False | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--branch--kg1_retest.json.gz) |

## case_description (additional unit)

case_description process/management unit. Source: FORMULAS:M05.

Scanner: `trading_research.research.method_pack.native_discovery:extra_sires`. Native jobs: 7. Observed sequence p/f/u: 0/0/0; n=0.

Observed scope/record limits: actual dated process/source records absent (7 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--unit--case_description.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | False | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--unit--case_description.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | False | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--unit--case_description.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--unit--case_description.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | False | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--unit--case_description.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 0 | False | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--unit--case_description.json.gz) |
| 2026-01-02 | 0 | 0 | 0 | 0 | False | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--unit--case_description.json.gz) |

## management (additional unit)

management process/management unit. Source: FORMULAS:M05.

Scanner: `trading_research.research.method_pack.native_discovery:extra_sires`. Native jobs: 7. Observed sequence p/f/u: 0/0/0; n=0.

Original source-audit requirement (see reconstruction report for implemented models) (daily_r_before, daily_limit_allows_entry): actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Citation: STOP pp.12,14;O140,O145,O150.

Observed scope/record limits: actual dated process/source records absent (7 job records); actual account/session closed R and active quantity/order ledger (7 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--unit--management.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | False | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--unit--management.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | False | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--unit--management.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--unit--management.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | False | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--unit--management.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 0 | False | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--unit--management.json.gz) |
| 2026-01-02 | 0 | 0 | 0 | 0 | False | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--unit--management.json.gz) |

## reentry (additional unit)

reentry process/management unit. Source: FORMULAS:M05.

Scanner: `trading_research.research.method_pack.native_discovery:extra_sires`. Native jobs: 7. Observed sequence p/f/u: 0/0/0; n=0.

Original source-audit requirement (see reconstruction report for implemented models) (daily_r_before, daily_limit_allows_entry): actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Citation: STOP pp.12,14;O140,O145,O150.

Observed scope/record limits: actual dated process/source records absent (7 job records); actual account/session closed R and active quantity/order ledger (7 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2020-01-02/SIRES--unit--reentry.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | False | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2021-01-04/SIRES--unit--reentry.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | False | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2022-01-03/SIRES--unit--reentry.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2023-01-02/SIRES--unit--reentry.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | False | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2024-01-02/SIRES--unit--reentry.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 0 | False | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2025-01-02/SIRES--unit--reentry.json.gz) |
| 2026-01-02 | 0 | 0 | 0 | 0 | False | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.0.0-r3/jobs/evaluation/2026-01-02/SIRES--unit--reentry.json.gz) |

Counts from dependent branches are not a pooled family win rate. The pilot is separate. Full-feed completeness and author-exact measurement remain unestablished.
