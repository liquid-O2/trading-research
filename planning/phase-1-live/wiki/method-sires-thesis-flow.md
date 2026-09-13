<!-- full-phase1-measurement-current -->
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
<!-- /full-phase1-measurement-current -->

## Preserved implementation and prior measurement history

# Sires — thesis, risk, and order flow

<!-- phase1-strategy-current -->
## Current reconstructed strategy

SIRES: 12 setup, 84 no setup, 0 unavailable input. Personal execution requirements are excluded from qualification.

[Current method report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/SIRES.md) · [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

| Scope and classification | Observations |
| --- | --- |
| entry_setup:no_setup | 84 |
| entry_setup:setup | 12 |

The preserved source audit below describes its original scope. An inferred level/state is identified as our model; it is not a recovered author label or evidence of an actual trade.
<!-- /phase1-strategy-current -->

## Preserved v2 source-audit baseline

The following section records the earlier, broader source-audit scope. Its personal-record requirements and p/f/u counts are historical comparisons; the strategy scope and current classifications above supersede them.

<!-- phase1-native-v2-current -->
## Current native research implementation — 2026-09-13

Every listed scanner/interface ran for its declared dates or actual collection unit. Source definitions below remain the owner of the method; frozen operational choices are in [the research policy](/workspace/implementation/reports/phase1-live/implementation-v2/RESEARCH_POLICY.json).

Evaluation dates: 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-02, 2024-01-02, 2025-01-02, 2026-01-02. No date was replaced because of missing coverage. `n=p+f`; `N observed=n+u`. A missing population scope is recorded separately from an observed zero.

| Branch/unit | n | p | f | u | Observed scope |
| --- | --- | --- | --- | --- | --- |
| dom_rejection | 5 | 1 | 4 | 3 | observed_subset_with_input_limits |
| absorption_reward_retest | 7 | 0 | 7 | 1 | observed_subset_with_input_limits |
| stop_four_stage | 7 | 0 | 7 | 1 | observed_subset_with_input_limits |
| footprint_confirmed_reaction | 8 | 0 | 8 | 0 | observed_subset_with_input_limits |
| vwap_deviation_fade | 7 | 0 | 7 | 2 | observed_subset_with_input_limits |
| ofm_aggressive | 7 | 0 | 7 | 1 | observed_subset_with_input_limits |
| ofm_passive | 3 | 0 | 3 | 2 | observed_subset_with_input_limits |
| clean_squeeze | 5 | 0 | 5 | 3 | observed_subset_with_input_limits |
| balance_failure_fade | 5 | 0 | 5 | 3 | observed_subset_with_input_limits |
| defended_band_continuation | 2 | 0 | 2 | 0 | observed_subset_with_input_limits |
| microbalance_break | 13 | 6 | 7 | 0 | observed_subset_with_input_limits |
| kg1_retest | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |
| unit: case_description | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |
| unit: management | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |
| unit: reentry | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |

**dom_rejection** — planned level → arriving effort/no progress → depth-one defense/rejection. Source: DOM6/DOM7 pp.3–7. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

**absorption_reward_retest** — real extreme → opposing effort/passive defense → own reward near origin → distinct reward-area retest/fresh defense. Source: ABS pp.5–13. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

**stop_four_stage** — real extreme → defense → replenishment → opposing print thinning → absorber aggression and 2–4 tick lift-off; account -4R checked separately. Source: STOP pp.10,12,14. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `daily_r_before`, `daily_limit_allows_entry`: actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Source: STOP pp.12,14;O140,O145,O150.

Inspected local evidence: ['implementation/src/trading_research/research/method_pack/objects/lifecycles.py', 'implementation/src/trading_research/research/method_pack/source_cases_v2.json'].

Recorded scope/record limits: actual account/session closed R and active quantity/order ledger (7 job records); no confirmed alternating-pivot auction in observed prefix (1 job records).

**footprint_confirmed_reaction** — known level → same-candle delta disagreement/absorption → within-candle POC relocation → local flow. Source: FP9 pp.4–7. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

**vwap_deviation_fade** — auction context → pre-touch executed VWAP/deviation → same-band absorption → local CVD/ladder confirmation. Source: VWAP pp.3–8. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

**ofm_aggressive** — catalyst → release → failed squeeze → catalyst reclaim/refill → initiative/wicks → defended drive retest; source gamma retained separately. Source: OFM pp.3–13;BIG pp.7–14,18;CONT p.10. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `short_gamma`, `long_gamma`, `branch_regime_allowed`: dated source dealer-map regime and selected native product/transform. Local option contract/quote/OI data exist; they do not disclose author dealer positions or gamma-map formula. Observable OFM/fade stages run independently. Source: BIG pp.14–18;GEX pp.4–20;O033–O040.

Inspected local evidence: ['planning/phase-1-live/wiki/gex-regime.md', 'data/thetadata-opra', 'data/manifests'].

Recorded scope/record limits: dated source dealer-map regime and selected native product/transform (7 job records); no confirmed alternating-pivot auction in observed prefix (1 job records).

**ofm_passive** — failed squeeze → dying tape/no aggressive failure → actual buyer area → trigger above buyers and stop below aggression. Source: OFM p.14. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

**clean_squeeze** — catalyst → fast release with no earlier failure → first pullback → opposing absorption → continuation. Source: CONT p.11;OFM p.5. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

**balance_failure_fade** — balance extreme → unpaid aggression → leave → same-area retest still unpaid → prior opposite-control target; dated gamma input separate. Source: BIG pp.14–15,18. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `short_gamma`, `long_gamma`, `branch_regime_allowed`: dated source dealer-map regime and selected native product/transform. Local option contract/quote/OI data exist; they do not disclose author dealer positions or gamma-map formula. Observable OFM/fade stages run independently. Source: BIG pp.14–18;GEX pp.4–20;O033–O040.

Inspected local evidence: ['planning/phase-1-live/wiki/gex-regime.md', 'data/thetadata-opra', 'data/manifests'].

Recorded scope/record limits: dated source dealer-map regime and selected native product/transform (7 job records); no confirmed alternating-pivot auction in observed prefix (1 job records).

**defended_band_continuation** — prior band control → distinct current return → fresh same-side defense/refresh and executed aggression. Source: NYAM pp.4–5;K18 pp.7,11,14;CONT pp.4–10;ANAT p.7. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: no confirmed alternating-pivot auction in observed prefix (1 job records).

**microbalance_break** — larger direction → price-defined alternating-pivot microbalance → strength/break → stop behind that structure. Source: K2345 pp.4–7. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: earlier potential directional breakout close is unknown (1 job records).

**kg1_retest** — dated source KG1 → actual same-band retest → aggressive confirmation → supplied management policy. Source: NYAM pp.8–9. Scanner: `trading_research.research.method_pack.historical_flow:scan_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `source_kg1_level_known`, `level_known_at`: dated source KG1 level/band, identity and version. Retained source cases provide limited readouts; no historical generator/series. Existing options snapshots cannot establish proprietary KG1. Source: NYAM pp.8–9;K10 pp.4–6;O041.

Inspected local evidence: ['planning/phase-1-live/wiki/kg1-level.md', 'implementation/src/trading_research/research/method_pack/source_cases_v2.json'].

Recorded scope/record limits: dated KG1 band and identity absent (7 job records); dated source KG1 level/band, identity and version (7 job records).

**case_description** — case_description process/management unit. Source: FORMULAS:M05. Scanner: `trading_research.research.method_pack.native_discovery:extra_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: actual dated process/source records absent (7 job records).

**management** — management process/management unit. Source: FORMULAS:M05. Scanner: `trading_research.research.method_pack.native_discovery:extra_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `daily_r_before`, `daily_limit_allows_entry`: actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Source: STOP pp.12,14;O140,O145,O150.

Inspected local evidence: ['implementation/src/trading_research/research/method_pack/objects/lifecycles.py', 'implementation/src/trading_research/research/method_pack/source_cases_v2.json'].

Recorded scope/record limits: actual dated process/source records absent (7 job records); actual account/session closed R and active quantity/order ledger (7 job records).

**reentry** — reentry process/management unit. Source: FORMULAS:M05. Scanner: `trading_research.research.method_pack.native_discovery:extra_sires`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `daily_r_before`, `daily_limit_allows_entry`: actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Source: STOP pp.12,14;O140,O145,O150.

Inspected local evidence: ['implementation/src/trading_research/research/method_pack/objects/lifecycles.py', 'implementation/src/trading_research/research/method_pack/source_cases_v2.json'].

Recorded scope/record limits: actual dated process/source records absent (7 job records); actual account/session closed R and active quantity/order ledger (7 job records).

Native market/process research is executed; author-exact verdicts and faithful disagreements remain unknown. No comparison observation is represented as a fill. [Date-level evidence for this method](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/SIRES.md) · [Software acceptance and remaining external inputs](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md).

<!-- /phase1-native-v2-current -->

## Source definitions and retained historical comparison notes

Operating method / SIRES. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


**Source identity.** [C1] p.3 states the loop: form the thesis, define where it dies, trade while it lives, and recreate it when invalidated. [BIG] pp.14–18 explicitly places aggressive continuation and balance fades inside one framework. [CONT] p.12 says its three lower-timeframe confirmations expressed the **same higher-timeframe short thesis**. The payout/session titles therefore identify examples, not new operating systems. [C3] is by Sires and explicitly credits a recording with **orderxfilled**; that collaboration is retained without inventing another disclosed entry system.

### The operating loop

| Step | Source operation, in order | Current implementation and evidence limits |
|---|---|---|
| 1. Define the model and account constraints | Define the features, regimes and products being traded; set the loss/risk constraints and news plan. The coaching blueprint then tests one change over a block of trades, rather than switching tools after individual losses. ([AVG] pp.17–20, 27–30; [C3] pp.3–7; [EMO] pp.3–8.) | [O137](model-definition.md) · [O140](position-sizing.md) · [O145](daily-loss-limit.md) · [O146](process-journal.md). Versioned models, account constraints, exit policy and revision/breach journals are implemented as supplied process records. Actual source/account history remains indispensable. |
| 2. Read the current auction and relevant larger structure | Map actual balances and imbalances, prior value, shelves/ledges, minor nodes, naked POCs, overnight inventory, current and composite structure, and the weekly/daily signed-delta evidence relevant to the idea. Use the current auction, not an arbitrary stale profile. Locate untouched objectives and recognize when a correlated market has already used its own objective. ([AMT1] pp.3–13; [VP2] pp.3–8; [TPO] pp.3–9; [MAMT] pp.4–17; [MATH] pp.12–14; [C1] pp.5–6; [K18] p.4; [K2345] pp.4–6.) | [O060](auction-balance.md) · [O061](value-and-profiles.md) · [O063](developing-profile.md) · [O070](composite-profiles.md) · [O071](dealing-range.md) · [O077](weekly-delta-profile.md) · [O087](unfinished-business.md) · [O147](correlated-object-first-use.md). Native profiles, immutable developing snapshots, selected parent bands, triad first-use and remaining-object lifecycles are implemented. Missing source band selection or native coverage remains explicit. |
| 3. Read the relevant regime, then write the thesis and death condition | When using the gamma framework, read the native 0DTE complex, flip/walls, location and current regime before setup selection; re-read after a large impulse. VIX/range completion, event expansion/crush and curve context modify ambition and risk. Write direction or a conditional reaction, objective and validity band. Structure break, value migration or new information can kill the thesis. ([GEX] pp.4–20; [VIX4] pp.3–9; [C1] pp.3–6; [ANAT] pp.4, 10.) | [O029](news-event-context.md) · [O033](gex-regime.md) · [O034](options-nodes.md) · [O035](gex-flip.md) · [O036](gex-walls-and-max-pain.md) · [O041](kg1-level.md) · [O138](thesis-lifecycle.md). Native options identity, supplied source gamma/KG maps and the causal thesis/death ledger are implemented. Proprietary dealer-map/level engines remain unavailable; scenarios cannot become the author's map. |
| 4. Wait at a location allowed by that thesis | A real auction extreme, previously defended reaction/refill band, appropriate broken balance boundary, or the relevant VWAP deviation/anchored confluence. Mark the band before the trade. VA calculations may move; a fixed previous-day value reference is different from today's developing value. A first naked touch is not proof of defense. ([ABS] pp.5–8; [VP2] pp.4–8; [VWAP] pp.3–8; [ANAT] pp.7–10; [CONT] pp.4–8.) | [O030](vwap-session.md) · [O031](vwap-anchored.md) · [O032](vwap-deviations.md) · [O068](profile-shelf.md) · [O069](profile-ledge.md) · [O116](refill-zone.md). Clocked VWAP and selected anchors, profile locations and same-band event association are implemented. Source location selection and later-only chart annotations cannot become pre-entry gates. |
| 5. Read participation and result; choose one permitted execution branch | Reset/read the DOM at the level, distinguish aggressive effort from price reward, and observe actual replenishment, thinning, pace, delta/CVD and the relevant footprint structure. Run the branch below; do not combine the easiest Boolean from several unrelated times. ([DOM5], [DOM6], [DOM7] pp.3–7; [FP8], [FP9] pp.3–7; [ABS] pp.8–13; [STOP] pp.6–14; [BIG] pp.5–18; [OFM] pp.3–14.) | [O004](execution-bars.md) · [O098](aggressor-trades.md) · [O100](dom.md) · [O101](absorption-and-big-trades.md) · [O103](iceberg-evidence.md) · [O105](cvd-variants.md) · [O108](candle-poc-flip.md) · [O120](footprint.md). Local side-specific flow stages, native execution bars and selected branch admission are implemented. Unpublished detectors, platform CVD/settings and unavailable depth remain separate source/data limits. |
| 6. Fit structural risk to the account and execute | The controlling structure determines invalidation; size follows the stop distance and account constraint; an actual HTF objective determines available reward. Do not pick an attractive R:R and invent the structure to fit it. A modest initial R:R can be acceptable when the defense and management are sound. ([ANAT] pp.8–10; [C2] pp.3–7; [K18] pp.7–9, 14; [K2345] p.7.) | [O139](structural-risk.md) · [O140](position-sizing.md) · [O141](trade-objective.md) · [O150](order-lifecycle.md). Entry-linked invalidation, exposure, objective and execution lifecycle are implemented. Case-specific distances retain their source scope; historical fills require actual records. |
| 7. Manage the position as control develops | Take the chosen static/partial or dynamic policy. Move to breakeven at a logical change in risk; trail behind newly confirmed protected highs/lows, not an unconfirmed wick. For the K18 short, a prior low must break and close with real aggression before the intervening high becomes protected. Add risk only after earlier risk is secured. ([RD] pp.4–5; [C2] p.5; [C3] p.4; [NYAM] pp.8–9; [K18] pp.8–14; [ANAT] p.10.) | [O142](position-management.md) · [O143](protected-high-low.md) · [O150](order-lifecycle.md). Mirrored protected structure, confirmation times, amendments, partials and aggregate position quantities are implemented. Each management action remains tied to the actual policy and position. |
| 8. Re-enter only on a fresh qualifying episode, or rebuild the thesis | A stop-out can leave the larger reaction band valid. Price must return inside that same band and produce fresh branch-specific confirmation; rerun location, reward/result and delta checks from zero. A thesis death requires a new thesis. A daily stop is not reset by calling the next attempt a re-entry. ([ANAT] pp.7, 10; [STOP] pp.6, 14–15; [CONT] pp.8–10; [C1] pp.3–4.) | [O138](thesis-lifecycle.md) · [O144](reentry.md) · [O145](daily-loss-limit.md) · [O150](order-lifecycle.md). Thesis/band lineage, fresh attempts, re-entry and account constraints are implemented. Early source attempts remain separate from confirmed-branch qualification. |
| 9. Review process and distributions, then change one thing | Record thesis, confidence, regime, every attempted trade and breach; pause replay before the entry to state its reason; examine aggregate outcomes, MFE/MAE and account costs; revise a single model variable over a defined sample. ([C1] pp.6–7; [C2] pp.4, 6–7; [AVG] pp.27–30; [EMO] pp.6–8.) | [O137](model-definition.md) · [O146](process-journal.md) · [O148](research-cohort.md) · [O153](outcome-metrics.md). The process/cohort review and distribution contracts are implemented. Empirical v1 now measures its frozen comparison subset; it still does not reconstruct private decisions or certify a source trading edge. |

### Auction routes that decide which execution is allowed

These are context-to-objective routes within Sires's loop. They are not a license to enter on a profile label.

| Route | Ordered read and destination | Current attachment and source boundary |
|---|---|---|
| Balance rotation | Establish balance; wait at a real outer edge; require the chosen fade confirmation; target POC/fair value and reassess before expecting the far side. ([AMT1] pp.7–10; [VP2] pp.3–8.) | [O060](auction-balance.md) · [O062](value-area.md) · [O064](profile-poc.md) · [O066](hvn.md). Selected balance/value parents and the source confirmation remain prerequisites. |
| Accepted breakout / boundary retest | Balance or ledge breaks with participation and acceptance outside; return to the broken boundary; its defense permits continuation toward the next value area/objective. ([AMT1] pp.8–9; [MAMT] p.12.) | [O091](break-retest.md). The break must precede the later retest of the same boundary. |
| Re-acceptance / rotation | Price leaves or opens outside value, returns inside and establishes acceptance; the directional read changes toward the opposite side. Two-period-inside and generic re-entry claims keep separate denominators. ([AMT1] p.7; [MAMT] pp.12, 18.) | [O092](value-reacceptance.md). The accepted-inside record uses the stated source rule; a research duration remains a declared assumption. |
| The **Failed Auction setup** | Established balance → break → actually tag an **older, separate balance's POC** → instant rejection → trade back toward the established balance's specified boundary. The source names VAH after rejection from above a prior POC and VAL after rejection from below; the schematic/fixture fixes which balance and side. ([MAMT] pp.9–11.) | [O065](naked-poc.md) · [O093](failed-auction-sires.md). The actual failed-auction parent and source objective are retained. A naked POC by itself is insufficient. |
| Full traversal with one side in control | Price traverses the whole balance without holding; subsequent retests trade with that side until contradicted. ([MAMT] p.12.) | [O096](balance-traversal.md). Traversal and one-sided control retain their event clocks; a comparison timeout is not an author rule. |
| Overnight/open/day structure | Read overnight inventory and its LVN/shelf at the open, then the developing open/day type. A shelf's hold or aggressive break changes expectations. IB, single prints, excess, poor extremes, prior-session landmarks and MPOC inform targets and timing. ([TPO] pp.3–9; [AMT1] pp.10–13; [MAMT] pp.14–26.) | [O073](overnight-profile.md) · [O074](overnight-inventory.md) · [O075](prior-eth-profile.md) · [O076](mpoc.md) · [O082](initial-balance.md) · [O083](open-type.md) · [O084](day-type.md). Final day labels remain outcomes. The conditional overnight-edge and MPOC claims remain separate from entry probabilities. |

The P/b sketches are not a universal directional switch: [MAMT] p.7's caption and diagrams do not consistently prescribe the same break direction, and Saint's P/b continuation explanations are his own. An LVN requires the appropriate profile structure on both sides; an outer taper alone is not the second transition back into balance ([MATH] pp.12–14; R-A17).

### Execution branches and their full predicates

All qualified Sires branches use:

```sql
thesis_alive AND auction_route_ok AND branch_regime_allowed
AND location_fixed AND location_touched AND objective_fixed AND risk_defined
AND thesis_known_at <= touch_at AND location_known_at <= touch_at
AND touch_at <= confirm_at AND confirm_at <= decision_at
AND sires_branch_ok
```

`thesis_alive` means no **observed** structure/value/news death before the decision, using the recorded death conditions. `branch_regime_allowed` has the scope the source gives it: [BIG]'s aggressive OFM is short-gamma-only; its balance fade is long gamma. Other examples retain their own regime evidence, including the disagreement near the flip in [K18] p.4. Do not invent a unanimously signed gamma gate for every historical Sires example.

Each row below defines `sires_branch_ok` for that named branch. Stage times refer to the same level, side and attempt.

| Branch / source name | Required ordered observation and SQL Boolean body | Current attachment and source boundary |
|---|---|---|
| `dom_rejection` — at-level DOM absorption | At a premarked level, arriving aggression makes little progress; observe actual rejection and additional opposing participation where the selected lesson requires it; enter behind the defended structure. `arriving_aggression AND little_progress AND local_rejection AND source_dom_confirmation AND aggression_at <= rejection_at AND rejection_at <= decision_at`. The iceberg refinement adds executed depletion → persistent replenishment → added participation within the illustrated two-tick area. ([DOM6] pp.3–7; [DOM7] pp.3–7.) | [O100](dom.md) · [O101](absorption-and-big-trades.md) · [O103](iceberg-evidence.md) · [O121](dom-rejection-branch.md). The local same-band sequence is implemented; hidden reserve or off-touch depth remains unavailable from BBO alone. |
| `absorption_reward_retest` — the four-check absorption reversal | A **fixed real extreme**, opposing aggression absorbed at a passive wall, actual reward by the new controlling side within the source's three-tick neighborhood, then a retest of that rewarded area with renewed defense/aggression; CVD must support the read. `real_extreme AND passive_wall_confirmed AND opposing_effort_no_result AND own_reward_confirmed AND reward_near_origin AND cvd_filter_ok AND fresh_reward_retest_defended AND absorption_at < reward_at AND reward_at < retest_at AND retest_at <= decision_at`. ([ABS] pp.5–13.) | [O101](absorption-and-big-trades.md) · [O104](reward-system-3tick.md) · [O105](cvd-variants.md) · [O122](absorption-reward-retest.md). Ordered failure/reward/retest and exact parents are implemented. Unpublished reward settings and the platform CVD reference remain source inputs. |
| `stop_four_stage` — defense, replenishment, exhaustion, lift-off | Location → initial defense → replenishment → the opposing aggressor's prints shrink → absorber turns aggressive and price lifts off; reward is illustrated as 2–4 ticks, entry within 1–2 ticks of confirmation; re-entry repeats every check and respects the stated −4R daily stop. `real_extreme AND defense AND replenishment AND opponent_thinning AND absorber_aggressive AND delta_filter_ok AND lift_off AND reward_ticks BETWEEN 2 AND 4 AND entry_distance_ticks BETWEEN 0 AND 2 AND daily_r_before > -4 AND defense_at < replenish_at AND replenish_at <= exhaust_at AND exhaust_at < liftoff_at AND liftoff_at <= decision_at`. ([STOP] pp.6–15.) | [O101](absorption-and-big-trades.md) · [O102](passive-replenishment.md) · [O103](iceberg-evidence.md) · [O114](digit-thinning.md) · [O115](lift-off.md) · [O123](stop-four-stage.md). The four ordered local stages are implemented. The cited three-tick replenishment measure does not become an arbitrary event count; ES examples are not universal NQ thresholds. |
| `footprint_confirmed_reaction` — level, absorption, intrabar POC flip | A valid level first, candle direction versus executed delta disagreement there, absorption, then POC relocation **within the candle**, supported by the selected DOM/delta read. `at_valid_level AND candle_delta_disagreement AND local_absorption AND intrabar_poc_flip AND source_flow_confirmation AND level_known_at <= absorption_at AND absorption_at <= flip_at AND flip_at <= decision_at`. ([FP9] pp.4–7.) | [O108](candle-poc-flip.md) · [O120](footprint.md) · [O124](footprint-confirmed-reaction.md). The actual intrabar POC sequence and same-level reaction are implemented with execution-bar identity. Later candle summaries cannot replace the intrabar path. |
| `vwap_deviation_fade` — VWAP premium/discount reaction | An appropriate auction context and source session/anchor, price at a selected deviation, absorption/rejection plus CVD/ladder confirmation, then rotation toward VWAP or the named objective. `source_vwap_known AND selected_deviation_touched AND absorption_at_that_band AND cvd_filter_ok AND ladder_confirmation AND band_known_at <= touch_at AND touch_at <= confirm_at`. ([VWAP] pp.3–8.) | [O030](vwap-session.md) · [O032](vwap-deviations.md) · [O125](vwap-deviation-fade.md). Native VWAP/deviation geometry and selected local response are implemented. The empirical comparison uses explicitly declared bar assumptions and does not supply the full source flow confirmation. |
| `ofm_aggressive` — Origin of the Move, aggressive drive | Repeated absorbed effort creates the catalyst; an attempted squeeze fails; price returns through the catalyst/refill area; renewed initiative takes the intervening wicks, the refill holds, and the entry is on the drive's retest with own-side aggression and CVD not against it. `short_gamma AND repeated_effort_no_reward AND first_squeeze AND squeeze_failed AND catalyst_reclaimed AND refill_held AND initiative_drive AND intervening_wicks_taken AND drive_retest_defended AND own_aggression_rewarded AND cvd_filter_ok AND catalyst_at < first_release_at AND first_release_at < failure_at AND failure_at <= refill_at AND refill_at < drive_at AND drive_at < retest_at AND retest_at <= decision_at`. ([OFM] pp.3–13; [BIG] pp.7–14, 18; [CONT] p.10.) | [O109](footprint-imbalance-zones.md) · [O110](same-price-imbalance.md) · [O116](refill-zone.md) · [O118](ofm-catalyst.md) · [O126](ofm-aggressive-branch.md). The release, failure, refill and later confirmation are linked and checked. Source triggers and thresholds that were never published remain unavailable for automatic discovery. |
| `ofm_passive` — the passive variant | The squeeze fails **without aggressive orders at the failure** as tape speed dies; the demonstrated long enters above the buyers, stop below the aggression, with a 1R–3R scalp objective. `source_squeeze_failed AND tape_died_at_failure AND no_aggression_at_failure AND buyers_area_identified AND entry_above_buyers AND stop_below_aggression AND failure_at < entry_trigger_at AND entry_trigger_at <= decision_at`. ([OFM] p.14.) | [O127](ofm-passive-branch.md). The distinct passive branch is implemented and does not require the aggressive variant's failure print. Missing source/private selection remains explicit. |
| `clean_squeeze` — squeeze without the failed first attempt | Fast release from the catalyst without the prior OFM failure; on the first pullback, opposing aggression is absorbed and continuation is confirmed in the thesis direction. `catalyst_known AND fast_release AND no_prior_squeeze_failure AND first_pullback AND opposing_pullback_aggression_absorbed AND continuation_confirmed AND catalyst_at < release_at AND release_at < pullback_at AND pullback_at <= confirm_at`. ([CONT] p.11; [OFM] p.5.) | [O111](tape-speed.md) · [O118](ofm-catalyst.md) · [O128](clean-squeeze.md). Catalyst, release, speed and decision-time no-failure evidence are checked in order. A future survival window cannot select the earlier decision. |
| `balance_failure_fade` — failure of aggression in balance | Long gamma/balance, aggression at an extreme repeatedly goes unpaid, price leaves and retests the failed area, aggression there is still unpaid; fade toward where the opposite side **previously had control**. `long_gamma AND balance_context AND failed_aggression_at_extreme AND left_failed_area AND retest_same_failed_area AND aggression_still_unrewarded AND target_is_prior_opposite_control AND failure_at < leave_at AND leave_at < retest_at AND retest_at <= decision_at`. ([BIG] pp.14–15, 18.) | [O129](balance-failure-fade.md). The selected long-gamma balance, opposing aggression and failed response are checked. Own-side reward and a squeeze are not prerequisites; the source selects the objective. |
| `defended_band_continuation` — refill / minor-node continuation or re-entry | Established HTF direction and band; prior defense/control is visible; the return finds the same side defending/refilling with real participation; enter the confirmed continuation. A break above the short thesis's extreme with strong buying instead calls for a retest long toward VWAP. `prior_band_control AND same_band_retest AND fresh_same_side_defense AND executed_aggression AND refresh_consistent AND control_side_matches_thesis AND prior_defense_at < retest_at AND retest_at <= confirm_at`. ([NYAM] pp.4–5; [K18] pp.7, 11, 14; [CONT] pp.4–10; [ANAT] p.7.) | [O102](passive-replenishment.md) · [O116](refill-zone.md) · [O130](defended-band-continuation.md). Distinct returns and local fresh defense use the same band and executed flow identity. Price changes cannot stand in for signed executed volume. |
| `microbalance_break` — price-defined microbalance continuation | Within the established directional auction, a small price balance forms; price shows strength and breaks it; use the opposite side of that structure for risk and the pre-existing HTF objective, then trail confirmed structure. `microbalance_frozen AND directional_strength AND breakout_in_thesis_direction AND stop_behind_microbalance AND microbalance_known_at < breakout_at AND breakout_at <= decision_at`. ([K2345] pp.4–7.) | [O131](microbalance.md). The price-defined balance is frozen before breakout; the final or most favorable later box cannot select the earlier reference. |
| `kg1_retest` — KG1 retest with trailing convexity | Source KG1 level known → retest with aggressive confirmation → entry → trail as the trade develops. ([NYAM] pp.8–9.) `source_kg1_level_known AND kg1_retest AND aggression_confirms AND level_known_at <= retest_at AND retest_at <= confirm_at`. | [O041](kg1-level.md) · [O132](kg1-retest.md). Supplied KG1 retests and trailing-policy records are admitted. The proprietary level engine and general trailing-convexity selector remain unpublished. |

These predicates preserve branch differences. They do not require every indicator in every source. Diagonal footprint stacks, same-price 350% displays, a candle POC, a big trade, delta divergence, tape speed and an iceberg hypothesis are **evidence at a location**, not independent entry products. When the chosen confirmation uses a stack, record the candle, side, actual row band, departure and later defended revisit ([FP8] pp.4–7; R-F04). For the 350% display, preserve its ratio convention and instrument: “350% more” and “3.5 times” are not automatically interchangeable ([BIG] pp.3–5). Never compare a CVD value with a price-unit median.

### Attempts and exceptions the source actually shows

The source record includes more than textbook confirmed trades. Preserve these observations without manufacturing complete automatic entry rules:

| Source case | Known loop and Phase 1 case predicate | Current attachment and source boundary |
|---|---|---|
| “Pre-file” / early buffer entries | Thesis → deliberately small pre-confirmation attempt → defined small stop → loss → unchanged thesis pending the actual test. `thesis_alive AND preconfirmation_entry AND small_risk_declared AND stop_predefined`. ([K18] pp.5–6, 14.) | [O133](early-attempts.md). The source-case admission is implemented; the repeatable early-entry selector remains unpublished. These B+ attempts do not pass a confirmed-refill predicate. |
| Third retest with no new buyer defense | Prior tests of a support band → no fresh buyer defense on the third test → small short with stop just above → stop-out. `same_support_band AND distinct_test_count = 3 AND no_new_buyer_defense AND side = 'short' AND risk_defined`. ([NYAM] pp.6–7.) | [O134](third-retest-attempt.md). Distinct retests and actual local buyer-defense evidence are implemented. The source supplies no universal third-touch guarantee or complete automatic selector. |
| Late small resistance fade | Premarked resistance → an upward approach loses aggression candle by candle → small short near the session objective → session ends. `resistance_known_before_approach AND upward_approach_loses_aggression AND side = 'short' AND small_risk_declared`. ([NYAM] pp.10–11.) | [O135](late-resistance-fade.md). The supplied source case is retained; precise entry selection and the quantitative exhaustion threshold remain unpublished. |
| Earlier refill entry in OFM schematic | Catalyst/failure → return to the refill → optional earlier entry with more risk, instead of waiting for the later confirmed drive/retest. ([OFM] p.6.) `source_refill_return AND explicitly_early_entry AND source_risk_predefined`. | [O116](refill-zone.md) · [O126](ofm-aggressive-branch.md) · [O127](ofm-passive-branch.md). The earlier source choice stays distinct from later confirmation. It does not waive the aggressive branch's required retest. |

### Management and re-entry checks

Management is attached to the original entry and its chosen account policy. [C2] p.5 offers breakeven-then-trail, a trailing-distance example, and partial exits; [C3] p.4 distinguishes static/funded and dynamic/personal-account choices. The example numbers are not one mandatory rule for every session. [NYAM] pp.8–9 shows both target expansion and a trail; the pictured original risk box remains unchanged while the displayed target changes. Do not attribute the entire displayed 0.69→1.83 change to a shrinking initial stop.

A management scorer checks each action, after entry:

```sql
action_at > decision_at
AND action_matches_preselected_policy
AND supporting_structure_known_at <= action_at
AND (NOT stop_trailed OR protected_structure_confirmed)
AND (NOT risk_added OR earlier_risk_secured)
AND (NOT thesis_dead OR exit_or_new_thesis_recorded)
```

A re-entry candidate additionally requires:

```sql
same_band_id AND thesis_alive AND price_back_inside_band
AND fresh_confirmation_after_stopout
AND prior_exit_at < fresh_confirmation_at
AND fresh_confirmation_at <= decision_at
AND daily_limit_allows_entry
```

Citations: [RD] pp.4–5; [K18] pp.8–14; [ANAT] pp.7–10; [STOP] pp.6, 14–15; [CONT] pp.8–10. The new candidate must also pass its selected execution branch. A stop-out does not automatically kill the wider thesis, and prior confirmation does not automatically authorize another entry.

**Key fidelity limits.** The strict absorption reversal's “real extreme, not POC” restriction does not prohibit every other Sires setup from using POC as a destination or a different continuation context. [ABS] p.11 repeats contradictory directional annotations at its two extremes; its lower-side example cannot settle an exact signed-delta rule. [FP8] p.5's highlighted cells conflict with the stated diagonal ratio. The plotted CVD reference and “Speed of Tape (10)” reset/unit are unpublished. These remain unknown fields for author-exact automatic scoring. The current morning-level R-F/R-S booleans do not measure the complete operating loop.

## Definition and scanner correction — 2026-09-13

All eleven legacy `unavailable_definition` branches below **have documented source sequences, O121–O132 branch objects (excluding the separately scanned O125 comparison), and M05 predicates**. The branch producers evaluate selected observations; empirical v1 does not connect these eleven branches to automatic historical discovery. The table identifies what is defined and what still needs implementation or a specific input.

| Branch | Existing definition | Actual unresolved scope |
|---|---|---|
| `dom_rejection` | DOM6/DOM7 pp.3–7: premarked location, aggression without progress, rejection and selected additional participation; [O121](dom-rejection-branch.md). | Connect level selection and native at-level flow observations to discovery. MBP-1 can supply best-level updates and executions; deeper queues/individual hidden-order identity require different evidence. Neither limit erases the sequence. |
| `absorption_reward_retest` | ABS pp.5–13: real extreme → absorption → own-side reward near origin → freshly defended reward retest, with CVD; [O122](absorption-reward-retest.md). | Build linked extreme, effort/reward and retest discovery; identify the exact source CVD reference and remaining quantitative choices. The reward/retest definition is present. |
| `stop_four_stage` | STOP p.10 explicitly lists defense, replenishment, exhaustion and lift-off; pp.12, 14 give reward/entry-distance, print-thinning and daily-risk checks; [O123](stop-four-stage.md). | Derive and link these stages from native events at an identified location. Clarify the spatial replenishment convention and source CVD reference; retain instrument-specific scope. A historical account ledger affects account-risk evaluation, not availability of the market sequence. |
| `footprint_confirmed_reaction` | FP9 pp.4–7: valid level → candle/delta disagreement and absorption → intrabar POC relocation → selected flow confirmation; [O124](footprint-confirmed-reaction.md). | Connect native execution-bar construction, evolving POC snapshots and location selection. Identify remaining platform conventions individually; do not substitute final-candle summaries for the intrabar path. |
| `ofm_aggressive` | OFM pp.3–13; BIG pp.7–14, 18: catalyst → release → failure → refill → drive → defended retest; [O126](ofm-aggressive-branch.md). | Build causal episode discovery and explicit event/pace qualification. The source short-gamma context needs a dated map or separately named research treatment; the ordered OFM definition is published. |
| `ofm_passive` | OFM p.14 expressly describes failed squeeze with dying tape and no aggression at failure, entry above buyers, stop below aggression, 1R–3R objective; [O127](ofm-passive-branch.md). | Operationalize squeeze/buyer-area selection and dying-tape measurement. The registry's private-passive-order explanation does not justify suppressing this published market sequence. This example does not require inferring an individual's passive order identity. |
| `clean_squeeze` | CONT p.11 describes fast aggressive release without the failed first attempt, then opposing buyers absorbed and an available short entry; [O128](clean-squeeze.md). | Implement release/pullback/absorption discovery with explicit pace criteria and decision-time history. The registry statement that the clean-state and squeeze qualification are unpublished is too broad and incorrect for this documented sequence. |
| `balance_failure_fade` | BIG pp.14–15, 18: long-gamma balance extreme, unpaid aggression, leave, same-area retest still unpaid, prior opposite-control target; [O129](balance-failure-fade.md). | Derive balance/extreme and failure/retest stages; identify dated gamma context separately. Do not replace the branch with a generic touch or add another branch's own-reward condition. |
| `defended_band_continuation` | NYAM pp.4–5; K18 pp.7, 11, 14; CONT pp.4–10; ANAT p.7: prior band control, return and fresh same-side defense; [O130](defended-band-continuation.md). | Connect causal band history and fresh event observations to discovery, including thesis invalidation. Prior defense alone cannot stand for current defense. |
| `microbalance_break` | K2345 pp.4–7: price-defined small balance within larger direction, strength/break, structural stop and prior objective; [O131](microbalance.md). | Implement causal price-balance selection and strength measurement; identify algorithmic choices as research assumptions where the source gives no exact thresholds. The setup is defined even though a universal detector is not. |
| `kg1_retest` | NYAM pp.8–9: known KG1, aggressive retest, entry and later management; [O132](kg1-retest.md). | The KG1 level generator or dated historical level series is a distinct external input gap; the usage sequence is defined. A generic gamma wall cannot silently replace KG1. |

Missing stages in a particular replay do not prove that their definitions are unpublished. Extract observable stages from native executions/book events where supported, and name the precise remaining setting, selection rule, depth requirement or external level. This correction does not certify a complete automatic scanner for any of these eleven branches.

These are unscanned historical populations, not zero-opportunity searches. See the [source/evaluator/scanner distinction](current-status.md#correction-definitions-exist-18-branches-were-not-scanned). No scanner or empirical result changed in this correction.

## Implementation and empirical status — 2026-09-12

The [M05 contract](../FORMULAS.md#m05) and its 135 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following historical dispositions. **`unavailable_definition` is the original registry label, not the current assessment of source availability; those rows were not scanned.** Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `dom_rejection` | `unavailable_definition` | unavailable | — | — |
| `absorption_reward_retest` | `unavailable_definition` | unavailable | — | — |
| `stop_four_stage` | `unavailable_definition` | unavailable | — | — |
| `footprint_confirmed_reaction` | `unavailable_definition` | unavailable | — | — |
| `vwap_deviation_fade` | `data_hole` | 48 / 44 / 10 | 161 / 161 | 102 |
| `ofm_aggressive` | `unavailable_definition` | unavailable | — | — |
| `ofm_passive` | `unavailable_definition` | unavailable | — | — |
| `clean_squeeze` | `unavailable_definition` | unavailable | — | — |
| `balance_failure_fade` | `unavailable_definition` | unavailable | — | — |
| `defended_band_continuation` | `unavailable_definition` | unavailable | — | — |
| `microbalance_break` | `unavailable_definition` | unavailable | — | — |
| `kg1_retest` | `unavailable_definition` | unavailable | — | — |

All scheduled comparison jobs are accounted for. The unsupported branches had no historical searches scheduled; they were recorded as dispositions only. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. Separate `case_description`, `management`, `reentry` units remain supplied-only and outside the market-opportunity denominator. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Session and range geometry.** [Overnight high, low and width](overnight-range.md) · [Opening location and participation](open-location-switch.md).

**Regime and thesis context.** [Scheduled news and changing information](news-event-context.md) · [Session VWAP](vwap-session.md) · [Anchored VWAP](vwap-anchored.md) · [VWAP deviation bands](vwap-deviations.md) · [Source gamma regime](gex-regime.md) · [Native options-chain identity](options-nodes.md) · [Gamma-flip reference](gex-flip.md) · [Gamma call and put walls](gex-walls-and-max-pain.md) · [Source max-pain reference](max-pain.md) · [Source Vol Trigger readout](volatility-trigger.md) · [Source VOL-GEX readout](vol-gex.md) · [Source hedging-pressure gauge](hedging-pressure.md) · [Source KG1 level](kg1-level.md) · [VIX and volatility context](vix-context.md) · [Volatility-implied daily-move estimate](expected-daily-move.md) · [Volatility term structure and event change](volatility-curve.md) · [VVIX context](vvix-context.md).

**Price references and price-action confirmation.** [09:30 cash-open price](cash-open-reference.md) · [Premium / discount within a selected range](premium-discount-50.md) · [Source setup quality and exposure](quality-grade.md).

**Auction and profile structure.** [Auction balance](auction-balance.md) · [Volume profile](value-and-profiles.md) · [Profile value area](value-area.md) · [Developing profile snapshot](developing-profile.md) · [Profile point of control](profile-poc.md) · [Untested prior POC](naked-poc.md) · [High-volume node](hvn.md) · [Low-volume node](lvn.md) · [Profile shelf](profile-shelf.md) · [Profile ledge](profile-ledge.md) · [Composite auction profiles](composite-profiles.md) · [Source-selected dealing range](dealing-range.md) · [Prior defended reaction area](prior-reaction-area.md) · [Overnight volume structure](overnight-profile.md) · [Overnight directional inventory](overnight-inventory.md) · [ETH profile identity](prior-eth-profile.md) · [MPOC: the profile midpoint](mpoc.md) · [Signed volume-by-price profile](weekly-delta-profile.md) · [Time-price-opportunity profile](tpo-ib-auction.md) · [TPO single-print structure](single-prints.md) · [TPO excess at auction extremes](excess.md) · [TPO poor high and poor low](poor-extremes.md) · [Initial balance](initial-balance.md) · [Developing auction open type](open-type.md) · [Developing auction day structure](day-type.md) · [Profile shape and trade permission](profile-shape.md) · [Prior-session auction landmarks](prior-session-reference-levels.md) · [Remaining auction objectives](unfinished-business.md) · [Source-conditioned reference statistics](reference-statistics.md).

**Auction routes inside a method.** [Rotation within accepted balance](balance-rotation.md) · [Accepted break and defended boundary retest](break-retest.md) · [Re-acceptance into value](value-reacceptance.md) · [Sires's narrower Failed Auction setup](failed-auction-sires.md) · [POC failure versus efficient passage](poc-traversal.md) · [Whole-balance traversal with one side in control](balance-traversal.md) · [Higher- and lower-timeframe control alignment](htf-ltf-alignment.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [BigTrades aggression markers](big-trades.md) · [DOM at a planned location](dom.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Executed passive replenishment](passive-replenishment.md) · [Iceberg evidence and added participation](iceberg-evidence.md) · [Price reward near the absorption origin](reward-system-3tick.md) · [Cumulative volume delta and its source reference](cvd-variants.md) · [Candle direction versus executed delta](candle-delta-disagreement.md) · [Local delta concentration at an extreme](delta-spike.md) · [POC relocation within a candle](candle-poc-flip.md) · [Diagonal footprint imbalance stacks](footprint-imbalance-zones.md) · [Same-price 350% imbalance display](same-price-imbalance.md) · [Speed of tape](tape-speed.md) · [Bid-ask spread](spread-width.md) · [How price arrives at the area](approach-speed.md) · [Aggressor print-size thinning](digit-thinning.md) · [Absorber becomes aggressive and price lifts off](lift-off.md) · [Zone formed by aggressive prints](refill-zone.md) · [Memory of earlier zone tests](zone-touch-memory.md) · [Origin-of-the-Move catalyst](ofm-catalyst.md) · [Trapped aggression at an auction extreme](trapped-buyers.md) · [Native candle footprint](footprint.md).

**Execution branches within Sires's loop.** [At-level DOM rejection](dom-rejection-branch.md) · [Four-check absorption reversal](absorption-reward-retest.md) · [Defense, replenishment, exhaustion and lift-off](stop-four-stage.md) · [Footprint-confirmed reaction](footprint-confirmed-reaction.md) · [Confirmed VWAP deviation fade](vwap-deviation-fade.md) · [Aggressive Origin of the Move](ofm-aggressive-branch.md) · [Passive Origin-of-the-Move variant](ofm-passive-branch.md) · [Clean squeeze continuation](clean-squeeze.md) · [Failure of aggression in long-gamma balance](balance-failure-fade.md) · [Fresh defense of a continuation band](defended-band-continuation.md) · [Price-defined microbalance continuation](microbalance.md) · [KG1 retest and subsequent trailing](kg1-retest.md) · [Deliberate pre-confirmation attempts](early-attempts.md) · [Third support test without new buyer defense](third-retest-attempt.md) · [Late small resistance-fade case](late-resistance-fade.md).

**Risk, objectives and process.** [Declared model and review version](model-definition.md) · [Thesis, validity band and death condition](thesis-lifecycle.md) · [Entry-side structural invalidation](structural-risk.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md) · [Confirmed protected high or low](protected-high-low.md) · [Freshly qualified re-entry](reentry.md) · [Source account and session stop](daily-loss-limit.md) · [Thesis and execution journal](process-journal.md) · [Triad AMT-object first use: IØD and RFZ](correlated-object-first-use.md).

**Research, execution-study and risk records.** [Frozen observation cohort](research-cohort.md) · [Observed order lifecycle](order-lifecycle.md) · [Trading and account costs](cost-model.md) · [Outcome distribution of a declared process](outcome-metrics.md) · [Economic observation and release vintage](economic-release-vintage.md).

**Auction-state observation.** [Aggressive effort versus price-response efficiency](response-efficiency.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[AMT1]: </workspace/sources/documents/discretionary/amt-lesson-1.pdf>
[VP2]: </workspace/sources/documents/discretionary/vp-lesson-2.pdf>
[TPO]: </workspace/sources/documents/discretionary/tpo-lesson-3.pdf>
[VIX4]: </workspace/sources/documents/discretionary/vix-lesson-4.pdf>
[DOM5]: </workspace/sources/documents/discretionary/dom-lesson-5.pdf>
[DOM6]: </workspace/sources/documents/discretionary/dom-lesson-6.pdf>
[DOM7]: </workspace/sources/documents/discretionary/dom-lesson-7.pdf>
[FP8]: </workspace/sources/documents/discretionary/fp-lesson-8.pdf>
[FP9]: </workspace/sources/documents/discretionary/fp-lesson-9.pdf>
[VWAP]: </workspace/sources/documents/discretionary/vwap-lesson-10.pdf>
[C1]: </workspace/sources/documents/discretionary/code-1-thesis.pdf>
[C2]: </workspace/sources/documents/discretionary/code-2-risk.pdf>
[C3]: </workspace/sources/documents/discretionary/code-3-orderflow.pdf>
[EMO]: </workspace/sources/documents/discretionary/emotion.pdf>
[GEX]: </workspace/sources/documents/discretionary/gex-framework.pdf>
[MAMT]: </workspace/sources/documents/discretionary/mastering-amt-vp.pdf>
[ABS]: </workspace/sources/documents/discretionary/your-mistakes-with-absorption.pdf>
[STOP]: </workspace/sources/documents/discretionary/stop-re-entering.pdf>
[RD]: </workspace/sources/documents/discretionary/reading-delta.pdf>
[BIG]: </workspace/sources/documents/discretionary/only-trade-big-trades.pdf>
[OFM]: </workspace/sources/documents/discretionary/origin-of-the-move.pdf>
[NYAM]: </workspace/sources/documents/discretionary/ny-am-session.pdf>
[K18]: </workspace/sources/documents/discretionary/18k-payout-session.pdf>
[K2345]: </workspace/sources/documents/discretionary/2345-funded-session.pdf>
[ANAT]: </workspace/sources/documents/discretionary/anatomy-of-a-losing-start.pdf>
[CONT]: </workspace/sources/documents/discretionary/a-clean-continuation-short.pdf>
[K10]: </workspace/sources/documents/discretionary/10k-first-month.pdf>
[AVG]: </workspace/sources/documents/discretionary/average-unprofitable-trader.pdf>
[MATH]: </workspace/sources/documents/discretionary/the-math-behind-auction-market-theory.pdf>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
