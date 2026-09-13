# JJ-TBR: current v2 research

The declared annual sample covers 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. Every declared branch/date job is retained. These are ordered market or process observations under frozen research assumptions. They are not reconstructed author trades or fills.

| Branch/unit | Unit | N observed | n | p | f | u | Scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| judas_outbound | market_sequence | 6 | 6 | 3 | 3 | 0 | observed_subset_with_input_limits |
| judas_reversal | market_sequence | 8 | 8 | 4 | 4 | 0 | observed_subset_with_input_limits |
| single_extended | market_sequence | 2 | 2 | 0 | 2 | 0 | observed_subset_with_input_limits |
| single_purged | market_sequence | 2 | 2 | 0 | 2 | 0 | observed_subset_with_input_limits |
| internal_rotation | market_sequence | 4 | 4 | 0 | 4 | 0 | observed_subset_with_input_limits |
| extension_reaction | market_sequence | 8 | 8 | 0 | 8 | 0 | observed_subset_with_input_limits |
| other_session | market_sequence | 46 | 46 | 6 | 40 | 0 | observed_subset_with_input_limits |
| timed_pzone_reversal | market_sequence | 14 | 14 | 3 | 11 | 0 | observed_subset_with_input_limits |
| unit: management | management | 0 | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |

## judas_outbound (catalog branch)

pre-open direction → 09:30 outbound → selected exhaustion → exit by reversal window. Source: TBR pp.8–10.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Native jobs: 7. Observed sequence p/f/u: 3/3/0; n=6.

Observed scope/record limits: same_contract_prior_scope_unknown (1 job records); formation_has_no_observed_executions (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 1 | 0 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/JJ-TBR--branch--judas_outbound.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/JJ-TBR--branch--judas_outbound.json.gz) |
| 2022-01-03 | 1 | 0 | 1 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/JJ-TBR--branch--judas_outbound.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/JJ-TBR--branch--judas_outbound.json.gz) |
| 2024-01-02 | 1 | 1 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/JJ-TBR--branch--judas_outbound.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/JJ-TBR--branch--judas_outbound.json.gz) |
| 2026-01-02 | 1 | 1 | 0 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/JJ-TBR--branch--judas_outbound.json.gz) |

## judas_reversal (catalog branch)

frozen range/context → edge sweep → 09:40–09:50 block/rejection → opposing draw. Source: TBR pp.8–11,27–29.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Native jobs: 7. Observed sequence p/f/u: 4/4/0; n=8.

Observed scope/record limits: same_contract_prior_scope_unknown (1 job records); formation_has_no_observed_executions (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 1 | 0 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/JJ-TBR--branch--judas_reversal.json.gz) |
| 2021-01-04 | 1 | 1 | 0 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/JJ-TBR--branch--judas_reversal.json.gz) |
| 2022-01-03 | 2 | 0 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/JJ-TBR--branch--judas_reversal.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/JJ-TBR--branch--judas_reversal.json.gz) |
| 2024-01-02 | 1 | 0 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/JJ-TBR--branch--judas_reversal.json.gz) |
| 2025-01-02 | 1 | 1 | 0 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/JJ-TBR--branch--judas_reversal.json.gz) |
| 2026-01-02 | 2 | 1 | 1 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/JJ-TBR--branch--judas_reversal.json.gz) |

## single_extended (catalog branch)

extended overnight → EQ/quadrant → directional confirmation → range-edge target/reduced expectation. Source: TBR pp.12–14,24.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Native jobs: 7. Observed sequence p/f/u: 0/2/0; n=2.

Observed scope/record limits: same_contract_prior_scope_unknown (1 job records); formation_has_no_observed_executions (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/JJ-TBR--branch--single_extended.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/JJ-TBR--branch--single_extended.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/JJ-TBR--branch--single_extended.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/JJ-TBR--branch--single_extended.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/JJ-TBR--branch--single_extended.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/JJ-TBR--branch--single_extended.json.gz) |
| 2026-01-02 | 1 | 0 | 1 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/JJ-TBR--branch--single_extended.json.gz) |

## single_purged (catalog branch)

dated prior-liquidity purge → compressed range → internal contact/confirmation → expansion. Source: TBR pp.12–15.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Native jobs: 7. Observed sequence p/f/u: 0/2/0; n=2.

Observed scope/record limits: same_contract_prior_scope_unknown (1 job records); formation_has_no_observed_executions (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/JJ-TBR--branch--single_purged.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/JJ-TBR--branch--single_purged.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/JJ-TBR--branch--single_purged.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/JJ-TBR--branch--single_purged.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/JJ-TBR--branch--single_purged.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/JJ-TBR--branch--single_purged.json.gz) |
| 2026-01-02 | 1 | 0 | 1 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/JJ-TBR--branch--single_purged.json.gz) |

## internal_rotation (catalog branch)

wide balanced context → named internal → actual reversal signature → nearer named target. Source: JR pp.3,38–43;TBR pp.12,24.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Native jobs: 7. Observed sequence p/f/u: 0/4/0; n=4.

Observed scope/record limits: same_contract_prior_scope_unknown (1 job records); formation_has_no_observed_executions (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/JJ-TBR--branch--internal_rotation.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/JJ-TBR--branch--internal_rotation.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/JJ-TBR--branch--internal_rotation.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/JJ-TBR--branch--internal_rotation.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/JJ-TBR--branch--internal_rotation.json.gz) |
| 2025-01-02 | 2 | 0 | 2 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/JJ-TBR--branch--internal_rotation.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/JJ-TBR--branch--internal_rotation.json.gz) |

## extension_reaction (catalog branch)

prior expansion → actual parent 1.33–1.66 projection → response → still-unused objective. Source: TBR pp.20–21;JR pp.23–26,57.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Native jobs: 7. Observed sequence p/f/u: 0/8/0; n=8.

Observed scope/record limits: same_contract_prior_scope_unknown (1 job records); formation_has_no_observed_executions (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 1 | 0 | 1 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/JJ-TBR--branch--extension_reaction.json.gz) |
| 2021-01-04 | 1 | 0 | 1 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/JJ-TBR--branch--extension_reaction.json.gz) |
| 2022-01-03 | 2 | 0 | 2 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/JJ-TBR--branch--extension_reaction.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/JJ-TBR--branch--extension_reaction.json.gz) |
| 2024-01-02 | 1 | 0 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/JJ-TBR--branch--extension_reaction.json.gz) |
| 2025-01-02 | 1 | 0 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/JJ-TBR--branch--extension_reaction.json.gz) |
| 2026-01-02 | 2 | 0 | 2 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/JJ-TBR--branch--extension_reaction.json.gz) |

## other_session (catalog branch)

one of seven published formations → fixed context/location → selected confirmation/risk/objective. Source: TBR p.7,36;JR pp.46,50–51.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Native jobs: 7. Observed sequence p/f/u: 6/40/0; n=46.

Observed scope/record limits: same_contract_prior_scope_unknown (1 job records); formation_has_no_observed_executions (7 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 7 | 0 | 7 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/JJ-TBR--branch--other_session.json.gz) |
| 2021-01-04 | 10 | 1 | 9 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/JJ-TBR--branch--other_session.json.gz) |
| 2022-01-03 | 7 | 1 | 6 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/JJ-TBR--branch--other_session.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/JJ-TBR--branch--other_session.json.gz) |
| 2024-01-02 | 8 | 2 | 6 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/JJ-TBR--branch--other_session.json.gz) |
| 2025-01-02 | 7 | 1 | 6 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/JJ-TBR--branch--other_session.json.gz) |
| 2026-01-02 | 7 | 1 | 6 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/JJ-TBR--branch--other_session.json.gz) |

## timed_pzone_reversal (catalog branch)

dated supplied P-zone → contact → reversal → directed named destination. Source: JR pp.16–18,53–55,58–62.

Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Native jobs: 7. Observed sequence p/f/u: 3/11/0; n=14.

Original source-audit requirement (see reconstruction report for implemented models) (source_zone_known, zone_known_at): dated source P-zone band ID, bounds, active state, generator version and named destination. Source catalog contains case readouts/settings, not a historical 2020+ P-zone series or generator. Usage scanner accepts dated supplied bands; no approximate substitute. Citation: JR pp.16–18,53–55,58–62;O019.

Observed scope/record limits: same_contract_prior_scope_unknown (1 job records); dated source P-zone band ID, bounds, active state, generator version and named destination (7 job records); no dated P-zone bands/destinations (1 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 2 | 0 | 2 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/JJ-TBR--branch--timed_pzone_reversal.json.gz) |
| 2021-01-04 | 3 | 0 | 3 | 0 | True | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/JJ-TBR--branch--timed_pzone_reversal.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | True | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/JJ-TBR--branch--timed_pzone_reversal.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/JJ-TBR--branch--timed_pzone_reversal.json.gz) |
| 2024-01-02 | 2 | 1 | 1 | 0 | True | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/JJ-TBR--branch--timed_pzone_reversal.json.gz) |
| 2025-01-02 | 2 | 1 | 1 | 0 | True | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/JJ-TBR--branch--timed_pzone_reversal.json.gz) |
| 2026-01-02 | 5 | 1 | 4 | 0 | True | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/JJ-TBR--branch--timed_pzone_reversal.json.gz) |

## management (additional unit)

management process/management unit. Source: FORMULAS:M01.

Scanner: `trading_research.research.method_pack.native_discovery:extra_jumbo`. Native jobs: 7. Observed sequence p/f/u: 0/0/0; n=0.

Original source-audit requirement (see reconstruction report for implemented models) (daily_r_before, daily_limit_allows_entry): actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Citation: STOP pp.12,14;O140,O145,O150.

Observed scope/record limits: actual dated process/source records absent (7 job records); actual account/session closed R and active quantity/order ledger (7 job records).

| Date | n | p | f | u | Observed scope complete | Executions | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2020-01-02 | 0 | 0 | 0 | 0 | False | 198050 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2020-01-02/JJ-TBR--unit--management.json.gz) |
| 2021-01-04 | 0 | 0 | 0 | 0 | False | 431378 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2021-01-04/JJ-TBR--unit--management.json.gz) |
| 2022-01-03 | 0 | 0 | 0 | 0 | False | 324395 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2022-01-03/JJ-TBR--unit--management.json.gz) |
| 2023-01-02 | 0 | 0 | 0 | 0 | False | 0 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2023-01-02/JJ-TBR--unit--management.json.gz) |
| 2024-01-02 | 0 | 0 | 0 | 0 | False | 370432 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2024-01-02/JJ-TBR--unit--management.json.gz) |
| 2025-01-02 | 0 | 0 | 0 | 0 | False | 470052 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2025-01-02/JJ-TBR--unit--management.json.gz) |
| 2026-01-02 | 0 | 0 | 0 | 0 | False | 352408 | [job](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/jobs/evaluation/2026-01-02/JJ-TBR--unit--management.json.gz) |

Counts from dependent branches are not a pooled family win rate. The pilot is separate. Full-feed completeness and author-exact measurement remain unestablished.
