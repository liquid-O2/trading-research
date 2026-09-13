# SIRES — full acquired Phase 1 measurement

Implementation: accepted reconstructed setup rules, including disclosed inferred models. Historical session search: every frozen date through the owned NQ input endpoint. Setup qualification is distinct from subsequent outcomes and from actual fills.

| Branch | Scope | Searched sessions | Complete eligible sessions | Observed setups | Complete zero-setup sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- | --- |
| dom_rejection | entry_setup | 1742 | 1672 | 339 | 1361 | 58 |
| absorption_reward_retest | entry_setup | 1742 | 1672 | 7 | 1665 | 58 |
| stop_four_stage | entry_setup | 1742 | 1672 | 14 | 1658 | 58 |
| footprint_confirmed_reaction | entry_setup | 1742 | 1672 | 4 | 1668 | 58 |
| vwap_deviation_fade | entry_setup | 1742 | 1671 | 153 | 1525 | 59 |
| ofm_aggressive | entry_setup | 1742 | 1672 | 0 | 1672 | 58 |
| ofm_passive | entry_setup | 1742 | 1672 | 0 | 1672 | 58 |
| clean_squeeze | entry_setup | 1742 | 1672 | 1 | 1671 | 58 |
| balance_failure_fade | entry_setup | 1742 | 1667 | 2 | 1665 | 63 |
| defended_band_continuation | entry_setup | 1742 | 1672 | 57 | 1617 | 58 |
| microbalance_break | entry_setup | 1742 | 1661 | 1486 | 816 | 69 |
| kg1_retest | entry_setup | 1742 | 1588 | 475 | 1131 | 142 |
| case_description | supplemental_observation | 1742 | 0 | 0 | 0 | 1730 |
| management | personal_execution_out_of_scope | 1742 | 0 | 0 | 0 | 0 |
| reentry | supplemental_observation | 1742 | 0 | 0 | 0 | 1730 |

Eligible denominators require complete observed inputs for the branch and no active input limitation. Setups observed in limited sessions remain in the observed population and are excluded from the complete-session frequency numerator. Context, supplemental, personal and collection units do not enter entry-setup denominators.

Outcome tables describe all qualifying observed setups, including those in input-limited sessions. Complete future coverage is a separate requirement for excursion means; the per-setup record retains the input-eligibility flag.

## dom_rejection

Source: DOM6/DOM7 pp.3–7; planned level → arriving effort/no progress → depth-one defense/rejection.

Setups per complete eligible session: 0.197. Observed setups per searched session: 0.195.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 58 | 58 | 2 |
| 2021 | 261 | 249 | 60 | 58 | 11 |
| 2022 | 260 | 249 | 43 | 41 | 10 |
| 2023 | 260 | 249 | 61 | 58 | 9 |
| 2024 | 262 | 250 | 54 | 52 | 10 |
| 2025 | 261 | 250 | 48 | 47 | 8 |
| 2026 | 176 | 167 | 15 | 15 | 8 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 339 | 0 | 0 | 17.956 | 16.868 |
| 15 | 337 | 2 | 0 | 28.756 | 28.106 |
| 30 | 337 | 2 | 0 | 40.458 | 39.421 |
| 60 | 335 | 4 | 0 | 51.645 | 54.020 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 289 |
| objective_observed | 50 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 289 |
| objective_observed | 50 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 289 | 38.223 | 8.118 |
| objective_observed | 50 | 193.528 | 143.821 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 299 | 1672 | 0.173 |
| NY_PM_1200_1600 | 40 | 1672 | 0.023 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 299 | 51.697 | 56.731 | invalidation_observed: 256; objective_observed: 43 |
| NY_PM_1200_1600 | 36 | 51.208 | 31.507 | invalidation_observed: 33; objective_observed: 7 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## absorption_reward_retest

Source: ABS pp.5–13; real extreme → opposing effort/passive defense → own reward near origin → distinct reward-area retest/fresh defense.

Setups per complete eligible session: 0.004. Observed setups per searched session: 0.004.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 1 | 1 | 2 |
| 2021 | 261 | 249 | 3 | 3 | 11 |
| 2022 | 260 | 249 | 0 | 0 | 10 |
| 2023 | 260 | 249 | 3 | 3 | 9 |
| 2024 | 262 | 250 | 0 | 0 | 10 |
| 2025 | 261 | 250 | 0 | 0 | 8 |
| 2026 | 176 | 167 | 0 | 0 | 8 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 7 | 0 | 0 | 7.000 | 11.321 |
| 15 | 7 | 0 | 0 | 12.857 | 19.393 |
| 30 | 7 | 0 | 0 | 15.714 | 23.536 |
| 60 | 7 | 0 | 0 | 26.000 | 35.429 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 7 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 7 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 7 | 29.684 | 12.801 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 5 | 1672 | 0.003 |
| NY_PM_1200_1600 | 2 | 1672 | 0.001 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 5 | 28.000 | 33.650 | invalidation_observed: 5 |
| NY_PM_1200_1600 | 2 | 21.000 | 39.875 | invalidation_observed: 2 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## stop_four_stage

Source: STOP pp.10,12,14; real extreme → defense → replenishment → opposing print thinning → absorber aggression and 2–4 tick lift-off; account -4R checked separately.

Setups per complete eligible session: 0.008. Observed setups per searched session: 0.008.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 2 | 2 | 2 |
| 2021 | 261 | 249 | 4 | 4 | 11 |
| 2022 | 260 | 249 | 2 | 2 | 10 |
| 2023 | 260 | 249 | 2 | 2 | 9 |
| 2024 | 262 | 250 | 2 | 2 | 10 |
| 2025 | 261 | 250 | 1 | 1 | 8 |
| 2026 | 176 | 167 | 1 | 1 | 8 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 14 | 0 | 0 | 13.786 | 8.679 |
| 15 | 14 | 0 | 0 | 17.500 | 15.625 |
| 30 | 14 | 0 | 0 | 24.357 | 23.268 |
| 60 | 14 | 0 | 0 | 29.571 | 41.839 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 12 |
| objective_observed | 2 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 12 |
| objective_observed | 2 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 12 | 12.911 | 3.999 |
| objective_observed | 2 | 91.223 | 91.223 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 10 | 1672 | 0.006 |
| NY_PM_1200_1600 | 4 | 1672 | 0.002 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 10 | 26.100 | 53.750 | invalidation_observed: 9; objective_observed: 1 |
| NY_PM_1200_1600 | 4 | 38.250 | 12.062 | invalidation_observed: 3; objective_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## footprint_confirmed_reaction

Source: FP9 pp.4–7; known level → same-candle delta disagreement/absorption → within-candle POC relocation → local flow.

Setups per complete eligible session: 0.002. Observed setups per searched session: 0.002.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 1 | 1 | 2 |
| 2021 | 261 | 249 | 1 | 1 | 11 |
| 2022 | 260 | 249 | 0 | 0 | 10 |
| 2023 | 260 | 249 | 0 | 0 | 9 |
| 2024 | 262 | 250 | 0 | 0 | 10 |
| 2025 | 261 | 250 | 2 | 2 | 8 |
| 2026 | 176 | 167 | 0 | 0 | 8 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 4 | 0 | 0 | 20.688 | 17.062 |
| 15 | 4 | 0 | 0 | 22.312 | 42.938 |
| 30 | 4 | 0 | 0 | 42.438 | 46.250 |
| 60 | 4 | 0 | 0 | 52.125 | 74.938 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 4 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 4 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 4 | 114.529 | 92.773 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 4 | 1672 | 0.002 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 4 | 52.125 | 74.938 | invalidation_observed: 4 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## vwap_deviation_fade

Source: VWAP pp.3–8; auction context → pre-touch executed VWAP/deviation → same-band absorption → local CVD/ladder confirmation.

Setups per complete eligible session: 0.089. Observed setups per searched session: 0.088.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 25 | 25 | 2 |
| 2021 | 261 | 249 | 29 | 28 | 11 |
| 2022 | 260 | 249 | 25 | 24 | 10 |
| 2023 | 260 | 249 | 24 | 23 | 9 |
| 2024 | 262 | 250 | 25 | 24 | 10 |
| 2025 | 261 | 250 | 20 | 20 | 8 |
| 2026 | 176 | 166 | 5 | 5 | 9 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 153 | 0 | 0 | 16.742 | 18.585 |
| 15 | 152 | 1 | 0 | 28.679 | 30.360 |
| 30 | 150 | 3 | 0 | 39.678 | 40.053 |
| 60 | 150 | 3 | 0 | 54.223 | 52.483 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 125 |
| objective_observed | 28 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 125 |
| objective_observed | 28 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 125 | 58.371 | 9.297 |
| objective_observed | 28 | 257.390 | 144.048 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 141 | 1671 | 0.083 |
| NY_PM_1200_1600 | 12 | 1671 | 0.007 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 141 | 55.191 | 54.011 | invalidation_observed: 113; objective_observed: 28 |
| NY_PM_1200_1600 | 9 | 39.056 | 28.556 | invalidation_observed: 12 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## ofm_aggressive

Source: OFM pp.3–13;BIG pp.7–14,18;CONT p.10; catalyst → release → failed squeeze → catalyst reclaim/refill → initiative/wicks → defended drive retest; source gamma retained separately.

Setups per complete eligible session: 0.000. Observed setups per searched session: 0.000.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 0 | 0 | 2 |
| 2021 | 261 | 249 | 0 | 0 | 11 |
| 2022 | 260 | 249 | 0 | 0 | 10 |
| 2023 | 260 | 249 | 0 | 0 | 9 |
| 2024 | 262 | 250 | 0 | 0 | 10 |
| 2025 | 261 | 250 | 0 | 0 | 8 |
| 2026 | 176 | 167 | 0 | 0 | 8 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 0 | 0 | 0 | — | — |
| 15 | 0 | 0 | 0 | — | — |
| 30 | 0 | 0 | 0 | — | — |
| 60 | 0 | 0 | 0 | — | — |

| Boundary outcome | n |
| --- | --- |

| Both objective and invalidation defined: ordering | n |
| --- | --- |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## ofm_passive

Source: OFM p.14; failed squeeze → dying tape/no aggressive failure → actual buyer area → trigger above buyers and stop below aggression.

Setups per complete eligible session: 0.000. Observed setups per searched session: 0.000.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 0 | 0 | 2 |
| 2021 | 261 | 249 | 0 | 0 | 11 |
| 2022 | 260 | 249 | 0 | 0 | 10 |
| 2023 | 260 | 249 | 0 | 0 | 9 |
| 2024 | 262 | 250 | 0 | 0 | 10 |
| 2025 | 261 | 250 | 0 | 0 | 8 |
| 2026 | 176 | 167 | 0 | 0 | 8 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 0 | 0 | 0 | — | — |
| 15 | 0 | 0 | 0 | — | — |
| 30 | 0 | 0 | 0 | — | — |
| 60 | 0 | 0 | 0 | — | — |

| Boundary outcome | n |
| --- | --- |

| Both objective and invalidation defined: ordering | n |
| --- | --- |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## clean_squeeze

Source: CONT p.11;OFM p.5; catalyst → fast release with no earlier failure → first pullback → opposing absorption → continuation.

Setups per complete eligible session: 0.001. Observed setups per searched session: 0.001.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 0 | 0 | 2 |
| 2021 | 261 | 249 | 0 | 0 | 11 |
| 2022 | 260 | 249 | 0 | 0 | 10 |
| 2023 | 260 | 249 | 1 | 1 | 9 |
| 2024 | 262 | 250 | 0 | 0 | 10 |
| 2025 | 261 | 250 | 0 | 0 | 8 |
| 2026 | 176 | 167 | 0 | 0 | 8 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 1 | 0 | 0 | 3.250 | 13.250 |
| 15 | 1 | 0 | 0 | 6.250 | 29.750 |
| 30 | 1 | 0 | 0 | 19.250 | 29.750 |
| 60 | 1 | 0 | 0 | 21.250 | 29.750 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 1 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 1 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 1 | 64.495 | 64.495 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 1 | 1672 | 0.001 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 1 | 21.250 | 29.750 | invalidation_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## balance_failure_fade

Source: BIG pp.14–15,18; balance extreme → unpaid aggression → leave → same-area retest still unpaid → prior opposite-control target; dated gamma input separate.

Setups per complete eligible session: 0.001. Observed setups per searched session: 0.001.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 0 | 0 | 2 |
| 2021 | 261 | 249 | 0 | 0 | 11 |
| 2022 | 260 | 247 | 0 | 0 | 12 |
| 2023 | 260 | 247 | 1 | 1 | 11 |
| 2024 | 262 | 249 | 0 | 0 | 11 |
| 2025 | 261 | 250 | 0 | 0 | 8 |
| 2026 | 176 | 167 | 1 | 1 | 8 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 2 | 0 | 0 | 36.250 | 2.250 |
| 15 | 2 | 0 | 0 | 43.500 | 2.250 |
| 30 | 2 | 0 | 0 | 53.000 | 2.750 |
| 60 | 2 | 0 | 0 | 62.375 | 2.750 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 2 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 2 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 2 | 1.576 | 1.576 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 1 | 1667 | 0.001 |
| NY_PM_1200_1600 | 1 | 1667 | 0.001 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 1 | 105.500 | 1.250 | invalidation_observed: 1 |
| NY_PM_1200_1600 | 1 | 19.250 | 4.250 | invalidation_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## defended_band_continuation

Source: NYAM pp.4–5;K18 pp.7,11,14;CONT pp.4–10;ANAT p.7; prior band control → distinct current return → fresh same-side defense/refresh and executed aggression.

Setups per complete eligible session: 0.033. Observed setups per searched session: 0.033.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 13 | 13 | 2 |
| 2021 | 261 | 249 | 10 | 10 | 11 |
| 2022 | 260 | 249 | 4 | 4 | 10 |
| 2023 | 260 | 249 | 11 | 10 | 9 |
| 2024 | 262 | 250 | 9 | 9 | 10 |
| 2025 | 261 | 250 | 8 | 8 | 8 |
| 2026 | 176 | 167 | 2 | 2 | 8 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 56 | 1 | 0 | 12.871 | 11.942 |
| 15 | 55 | 2 | 0 | 23.000 | 19.195 |
| 30 | 55 | 2 | 0 | 30.073 | 25.568 |
| 60 | 54 | 3 | 0 | 40.185 | 34.745 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 53 |
| objective_observed | 4 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 53 |
| objective_observed | 4 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 53 | 41.255 | 7.315 |
| objective_observed | 4 | 1249.967 | 1132.768 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 40 | 1672 | 0.023 |
| NY_PM_1200_1600 | 17 | 1672 | 0.010 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 40 | 46.562 | 39.237 | invalidation_observed: 36; objective_observed: 4 |
| NY_PM_1200_1600 | 14 | 21.964 | 21.911 | invalidation_observed: 17 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## microbalance_break

Source: K2345 pp.4–7; larger direction → price-defined alternating-pivot microbalance → strength/break → stop behind that structure.

Setups per complete eligible session: 0.862. Observed setups per searched session: 0.853.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-08-31. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 256 | 257 | 253 | 4 |
| 2021 | 261 | 248 | 223 | 209 | 12 |
| 2022 | 260 | 248 | 185 | 175 | 11 |
| 2023 | 260 | 248 | 182 | 176 | 10 |
| 2024 | 262 | 250 | 218 | 218 | 10 |
| 2025 | 261 | 249 | 244 | 234 | 9 |
| 2026 | 176 | 162 | 177 | 166 | 13 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 1443 | 43 | 0 | 16.713 | 17.354 |
| 15 | 1395 | 91 | 0 | 28.388 | 28.710 |
| 30 | 1330 | 156 | 0 | 39.411 | 39.321 |
| 60 | 1231 | 255 | 0 | 53.521 | 54.388 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 407 |
| invalidation_observed | 428 |
| missing_future_coverage | 11 |
| objective_observed | 640 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 407 |
| invalidation_observed | 428 |
| missing_future_coverage | 11 |
| objective_observed | 640 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 428 | 990.274 | 551.600 |
| objective_observed | 640 | 559.318 | 199.944 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 741 | 1661 | 0.427 |
| NY_PM_1200_1600 | 745 | 1661 | 0.434 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 741 | 62.290 | 65.378 | expired_without_observed_boundary: 56; invalidation_observed: 274; objective_observed: 411 |
| NY_PM_1200_1600 | 490 | 40.259 | 37.768 | expired_without_observed_boundary: 351; invalidation_observed: 154; missing_future_coverage: 11; objective_observed: 229 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |
| earlier potential directional breakout close is unknown | 11 |

## kg1_retest

Source: NYAM pp.8–9; dated source KG1 → actual same-band retest → aggressive confirmation → supplied management policy.

Setups per complete eligible session: 0.292. Observed setups per searched session: 0.273.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 245 | 61 | 61 | 15 |
| 2021 | 261 | 238 | 57 | 54 | 22 |
| 2022 | 260 | 235 | 68 | 65 | 24 |
| 2023 | 260 | 234 | 80 | 78 | 24 |
| 2024 | 262 | 239 | 87 | 86 | 21 |
| 2025 | 261 | 240 | 79 | 77 | 18 |
| 2026 | 176 | 157 | 43 | 43 | 18 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 470 | 5 | 0 | 21.577 | 20.005 |
| 15 | 469 | 6 | 0 | 34.367 | 35.419 |
| 30 | 467 | 8 | 0 | 47.722 | 50.489 |
| 60 | 457 | 18 | 0 | 63.647 | 67.450 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 45 |
| invalidation_observed | 406 |
| missing_future_coverage | 2 |
| objective_observed | 22 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 45 |
| invalidation_observed | 406 |
| missing_future_coverage | 2 |
| objective_observed | 22 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 406 | 314.427 | 59.960 |
| objective_observed | 22 | 1723.407 | 1933.356 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 395 | 1588 | 0.244 |
| NY_PM_1200_1600 | 80 | 1588 | 0.048 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 395 | 65.776 | 68.416 | expired_without_observed_boundary: 33; invalidation_observed: 341; objective_observed: 21 |
| NY_PM_1200_1600 | 62 | 50.081 | 61.294 | expired_without_observed_boundary: 12; invalidation_observed: 65; missing_future_coverage: 2; objective_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| KG1/key-gamma model input unavailable | 107 |
| current input prefix has unknown intervals | 70 |

## case_description

Source: FORMULAS:M05; case_description process/management unit.

Setups per complete eligible session: —. Observed setups per searched session: —.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: none / none. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 0 | 0 | 0 | 260 |
| 2021 | 261 | 0 | 0 | 0 | 260 |
| 2022 | 260 | 0 | 0 | 0 | 259 |
| 2023 | 260 | 0 | 0 | 0 | 258 |
| 2024 | 262 | 0 | 0 | 0 | 260 |
| 2025 | 261 | 0 | 0 | 0 | 258 |
| 2026 | 176 | 0 | 0 | 0 | 175 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 0 | 0 | 0 | — | — |
| 15 | 0 | 0 | 0 | — | — |
| 30 | 0 | 0 | 0 | — | — |
| 60 | 0 | 0 | 0 | — | — |

| Boundary outcome | n |
| --- | --- |

| Both objective and invalidation defined: ordering | n |
| --- | --- |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| actual dated process/source records absent | 1742 |
| current input prefix has unknown intervals | 70 |

## management

Source: FORMULAS:M05; management process/management unit.

Setups per complete eligible session: —. Observed setups per searched session: —.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: none / none. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 0 | 0 | 0 | 0 |
| 2021 | 261 | 0 | 0 | 0 | 0 |
| 2022 | 260 | 0 | 0 | 0 | 0 |
| 2023 | 260 | 0 | 0 | 0 | 0 |
| 2024 | 262 | 0 | 0 | 0 | 0 |
| 2025 | 261 | 0 | 0 | 0 | 0 |
| 2026 | 176 | 0 | 0 | 0 | 0 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 0 | 0 | 0 | — | — |
| 15 | 0 | 0 | 0 | — | — |
| 30 | 0 | 0 | 0 | — | — |
| 60 | 0 | 0 | 0 | — | — |

| Boundary outcome | n |
| --- | --- |

| Both objective and invalidation defined: ordering | n |
| --- | --- |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| actual dated process/source records absent | 1742 |
| current input prefix has unknown intervals | 70 |

## reentry

Source: FORMULAS:M05; reentry process/management unit.

Setups per complete eligible session: —. Observed setups per searched session: —.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: none / none. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 0 | 0 | 0 | 260 |
| 2021 | 261 | 0 | 0 | 0 | 260 |
| 2022 | 260 | 0 | 0 | 0 | 259 |
| 2023 | 260 | 0 | 0 | 0 | 258 |
| 2024 | 262 | 0 | 0 | 0 | 260 |
| 2025 | 261 | 0 | 0 | 0 | 258 |
| 2026 | 176 | 0 | 0 | 0 | 175 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 0 | 0 | 0 | — | — |
| 15 | 0 | 0 | 0 | — | — |
| 30 | 0 | 0 | 0 | — | — |
| 60 | 0 | 0 | 0 | — | — |

| Boundary outcome | n |
| --- | --- |

| Both objective and invalidation defined: ordering | n |
| --- | --- |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| actual dated process/source records absent | 1742 |
| current input prefix has unknown intervals | 70 |

[Machine-readable results](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/MEASUREMENT_RESULTS.json) · [Coverage and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz) · [Per-setup records](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/setup-records.jsonl.gz) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md).
