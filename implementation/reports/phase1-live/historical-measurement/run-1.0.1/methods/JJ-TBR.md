# JJ-TBR — full acquired Phase 1 measurement

Implementation: accepted reconstructed setup rules, including disclosed inferred models. Historical session search: every frozen date through the owned NQ input endpoint. Setup qualification is distinct from subsequent outcomes and from actual fills.

| Branch | Scope | Searched sessions | Complete eligible sessions | Observed setups | Complete zero-setup sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- | --- |
| judas_outbound | entry_setup | 1742 | 1621 | 1528 | 168 | 109 |
| judas_reversal | entry_setup | 1742 | 1634 | 133 | 1502 | 96 |
| single_extended | entry_setup | 1742 | 1637 | 9 | 1628 | 93 |
| single_purged | entry_setup | 1742 | 1636 | 25 | 1612 | 94 |
| internal_rotation | entry_setup | 1742 | 1637 | 4 | 1633 | 93 |
| extension_reaction | entry_setup | 1742 | 1634 | 178 | 1458 | 96 |
| other_session | entry_setup | 1742 | 1548 | 1730 | 528 | 182 |
| timed_pzone_reversal | entry_setup | 1742 | 1613 | 305 | 1338 | 117 |
| management | personal_execution_out_of_scope | 1742 | 0 | 0 | 0 | 0 |

Eligible denominators require complete observed inputs for the branch and no active input limitation. Setups observed in limited sessions remain in the observed population and are excluded from the complete-session frequency numerator. Context, supplemental, personal and collection units do not enter entry-setup denominators.

Outcome tables describe all qualifying observed setups, including those in input-limited sessions. Complete future coverage is a separate requirement for excursion means; the per-setup record retains the input-eligibility flag.

## judas_outbound

Source: TBR pp.8–10; pre-open direction → 09:30 outbound → selected exhaustion → exit by reversal window.

Setups per complete eligible session: 0.896. Observed setups per searched session: 0.877.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 246 | 225 | 219 | 14 |
| 2021 | 261 | 241 | 230 | 215 | 19 |
| 2022 | 260 | 243 | 232 | 218 | 16 |
| 2023 | 260 | 242 | 234 | 221 | 16 |
| 2024 | 262 | 245 | 232 | 222 | 15 |
| 2025 | 261 | 244 | 225 | 214 | 14 |
| 2026 | 176 | 160 | 150 | 144 | 15 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 1528 | 0 | 0 | 28.324 | 29.235 |
| 15 | 1528 | 0 | 0 | 42.002 | 44.470 |
| 30 | 1528 | 0 | 0 | 55.128 | 57.260 |
| 60 | 1528 | 0 | 0 | 71.736 | 74.753 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 801 |
| invalidation_observed | 459 |
| objective_observed | 268 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 801 |
| invalidation_observed | 459 |
| objective_observed | 268 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 459 | 169.358 | 107.357 |
| objective_observed | 268 | 223.736 | 196.168 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 1528 | 1621 | 0.896 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 1528 | 71.736 | 74.753 | expired_without_observed_boundary: 801; invalidation_observed: 459; objective_observed: 268 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 8 |
| current input prefix has unknown intervals | 70 |
| formation_has_no_observed_executions | 21 |
| nonpositive_formation_width | 3 |
| same_contract_prior_scope_unknown | 34 |

## judas_reversal

Source: TBR pp.8–11,27–29; frozen range/context → edge sweep → 09:40–09:50 block/rejection → opposing draw.

Setups per complete eligible session: 0.081. Observed setups per searched session: 0.076.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 249 | 26 | 26 | 11 |
| 2021 | 261 | 243 | 18 | 18 | 17 |
| 2022 | 260 | 244 | 16 | 16 | 15 |
| 2023 | 260 | 244 | 16 | 16 | 14 |
| 2024 | 262 | 246 | 20 | 20 | 14 |
| 2025 | 261 | 244 | 18 | 17 | 14 |
| 2026 | 176 | 164 | 19 | 19 | 11 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 133 | 0 | 0 | 23.055 | 21.419 |
| 15 | 133 | 0 | 0 | 39.487 | 36.355 |
| 30 | 133 | 0 | 0 | 56.500 | 47.833 |
| 60 | 133 | 0 | 0 | 75.530 | 64.806 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 17 |
| invalidation_observed | 57 |
| objective_observed | 59 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 17 |
| invalidation_observed | 57 |
| objective_observed | 59 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 57 | 958.248 | 568.811 |
| objective_observed | 59 | 929.299 | 751.489 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 133 | 1634 | 0.081 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 133 | 75.530 | 64.806 | expired_without_observed_boundary: 17; invalidation_observed: 57; objective_observed: 59 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 8 |
| current input prefix has unknown intervals | 70 |
| formation_has_no_observed_executions | 21 |
| nonpositive_formation_width | 3 |
| same_contract_prior_scope_unknown | 34 |

## single_extended

Source: TBR pp.12–14,24; extended overnight → EQ/quadrant → directional confirmation → range-edge target/reduced expectation.

Setups per complete eligible session: 0.005. Observed setups per searched session: 0.005.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 250 | 3 | 3 | 10 |
| 2021 | 261 | 243 | 1 | 1 | 17 |
| 2022 | 260 | 244 | 0 | 0 | 15 |
| 2023 | 260 | 244 | 2 | 2 | 14 |
| 2024 | 262 | 246 | 0 | 0 | 14 |
| 2025 | 261 | 245 | 2 | 2 | 13 |
| 2026 | 176 | 165 | 1 | 1 | 10 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 9 | 0 | 0 | 17.472 | 36.806 |
| 15 | 9 | 0 | 0 | 20.194 | 62.611 |
| 30 | 9 | 0 | 0 | 26.111 | 73.028 |
| 60 | 9 | 0 | 0 | 28.944 | 90.528 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 7 |
| objective_observed | 2 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 7 |
| objective_observed | 2 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 7 | 494.376 | 369.586 |
| objective_observed | 2 | 97.092 | 97.092 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 9 | 1637 | 0.005 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 9 | 28.944 | 90.528 | invalidation_observed: 7; objective_observed: 2 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 8 |
| current input prefix has unknown intervals | 70 |
| formation_has_no_observed_executions | 21 |
| nonpositive_formation_width | 3 |
| same_contract_prior_scope_unknown | 34 |

## single_purged

Source: TBR pp.12–15; dated prior-liquidity purge → compressed range → internal contact/confirmation → expansion.

Setups per complete eligible session: 0.015. Observed setups per searched session: 0.014.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 250 | 5 | 5 | 10 |
| 2021 | 261 | 243 | 4 | 4 | 17 |
| 2022 | 260 | 244 | 4 | 4 | 15 |
| 2023 | 260 | 244 | 2 | 2 | 14 |
| 2024 | 262 | 245 | 2 | 2 | 15 |
| 2025 | 261 | 245 | 5 | 4 | 13 |
| 2026 | 176 | 165 | 3 | 3 | 10 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 25 | 0 | 0 | 20.220 | 29.470 |
| 15 | 25 | 0 | 0 | 41.290 | 47.700 |
| 30 | 25 | 0 | 0 | 49.150 | 61.410 |
| 60 | 25 | 0 | 0 | 60.400 | 97.260 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 8 |
| objective_observed | 17 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 8 |
| objective_observed | 17 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 8 | 1032.081 | 836.655 |
| objective_observed | 17 | 708.216 | 215.980 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 24 | 1636 | 0.014 |
| NY_PM_1200_1600 | 1 | 1636 | 0.001 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 24 | 61.240 | 100.948 | invalidation_observed: 8; objective_observed: 16 |
| NY_PM_1200_1600 | 1 | 40.250 | 8.750 | objective_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 8 |
| current input prefix has unknown intervals | 70 |
| formation_has_no_observed_executions | 21 |
| nonpositive_formation_width | 3 |
| same_contract_prior_scope_unknown | 34 |

## internal_rotation

Source: JR pp.3,38–43;TBR pp.12,24; wide balanced context → named internal → actual reversal signature → nearer named target.

Setups per complete eligible session: 0.002. Observed setups per searched session: 0.002.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 250 | 0 | 0 | 10 |
| 2021 | 261 | 243 | 0 | 0 | 17 |
| 2022 | 260 | 244 | 0 | 0 | 15 |
| 2023 | 260 | 244 | 1 | 1 | 14 |
| 2024 | 262 | 246 | 0 | 0 | 14 |
| 2025 | 261 | 245 | 2 | 2 | 13 |
| 2026 | 176 | 165 | 1 | 1 | 10 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 4 | 0 | 0 | 26.125 | 74.062 |
| 15 | 4 | 0 | 0 | 26.125 | 105.812 |
| 30 | 4 | 0 | 0 | 26.125 | 126.250 |
| 60 | 4 | 0 | 0 | 71.188 | 142.062 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 3 |
| objective_observed | 1 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 3 |
| objective_observed | 1 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 3 | 478.880 | 250.949 |
| objective_observed | 1 | 34.777 | 34.777 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 4 | 1637 | 0.002 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 4 | 71.188 | 142.062 | invalidation_observed: 3; objective_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 8 |
| current input prefix has unknown intervals | 70 |
| formation_has_no_observed_executions | 21 |
| nonpositive_formation_width | 3 |
| same_contract_prior_scope_unknown | 34 |

## extension_reaction

Source: TBR pp.20–21;JR pp.23–26,57; prior expansion → actual parent 1.33–1.66 projection → response → still-unused objective.

Setups per complete eligible session: 0.108. Observed setups per searched session: 0.102.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 250 | 24 | 24 | 10 |
| 2021 | 261 | 242 | 25 | 25 | 18 |
| 2022 | 260 | 244 | 27 | 27 | 15 |
| 2023 | 260 | 244 | 33 | 32 | 14 |
| 2024 | 262 | 246 | 22 | 21 | 14 |
| 2025 | 261 | 244 | 24 | 24 | 14 |
| 2026 | 176 | 164 | 23 | 23 | 11 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 178 | 0 | 0 | 23.066 | 23.635 |
| 15 | 178 | 0 | 0 | 41.105 | 38.240 |
| 30 | 178 | 0 | 0 | 64.423 | 51.615 |
| 60 | 177 | 1 | 0 | 82.977 | 65.274 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 31 |
| invalidation_observed | 79 |
| objective_observed | 68 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 31 |
| invalidation_observed | 79 |
| objective_observed | 68 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 79 | 974.951 | 850.466 |
| objective_observed | 68 | 942.907 | 571.395 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 174 | 1634 | 0.105 |
| NY_PM_1200_1600 | 4 | 1634 | 0.002 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 174 | 82.076 | 65.534 | expired_without_observed_boundary: 27; invalidation_observed: 79; objective_observed: 68 |
| NY_PM_1200_1600 | 3 | 135.250 | 50.167 | expired_without_observed_boundary: 4 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 8 |
| current input prefix has unknown intervals | 70 |
| formation_has_no_observed_executions | 21 |
| nonpositive_formation_width | 3 |
| same_contract_prior_scope_unknown | 34 |

## other_session

Source: TBR p.7,36;JR pp.46,50–51; one of seven published formations → fixed context/location → selected confirmation/risk/objective.

Setups per complete eligible session: 1.025. Observed setups per searched session: 0.993.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-08-31. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 235 | 206 | 193 | 25 |
| 2021 | 261 | 232 | 245 | 222 | 28 |
| 2022 | 260 | 233 | 248 | 225 | 26 |
| 2023 | 260 | 230 | 303 | 278 | 28 |
| 2024 | 262 | 233 | 260 | 238 | 27 |
| 2025 | 261 | 231 | 273 | 254 | 27 |
| 2026 | 176 | 154 | 195 | 176 | 21 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 1704 | 26 | 0 | 10.543 | 10.704 |
| 15 | 1643 | 87 | 0 | 18.434 | 18.225 |
| 30 | 1475 | 255 | 0 | 25.323 | 25.077 |
| 60 | 1475 | 255 | 0 | 35.782 | 35.020 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 256 |
| invalidation_observed | 867 |
| missing_future_coverage | 16 |
| objective_observed | 591 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 256 |
| invalidation_observed | 867 |
| missing_future_coverage | 16 |
| objective_observed | 591 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 867 | 994.815 | 723.784 |
| objective_observed | 591 | 971.154 | 781.054 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 464 | 1548 | 0.275 |
| NY_PM_1200_1600 | 536 | 1548 | 0.321 |
| overnight_00_06 | 509 | 1548 | 0.295 |
| previous_evening | 221 | 1548 | 0.133 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 464 | 55.589 | 53.968 | expired_without_observed_boundary: 81; invalidation_observed: 247; objective_observed: 136 |
| NY_PM_1200_1600 | 281 | 42.654 | 36.698 | expired_without_observed_boundary: 87; invalidation_observed: 239; missing_future_coverage: 16; objective_observed: 194 |
| overnight_00_06 | 509 | 21.617 | 22.534 | expired_without_observed_boundary: 54; invalidation_observed: 270; objective_observed: 185 |
| previous_evening | 221 | 18.081 | 21.862 | expired_without_observed_boundary: 34; invalidation_observed: 111; objective_observed: 76 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 8 |
| current input prefix has unknown intervals | 70 |
| formation_has_no_observed_executions | 105 |
| nonpositive_formation_width | 4 |
| same_contract_prior_scope_unknown | 34 |

## timed_pzone_reversal

Source: JR pp.16–18,53–55,58–62; dated supplied P-zone → contact → reversal → directed named destination.

Setups per complete eligible session: 0.182. Observed setups per searched session: 0.175.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 245 | 36 | 36 | 15 |
| 2021 | 261 | 239 | 45 | 44 | 21 |
| 2022 | 260 | 241 | 48 | 45 | 18 |
| 2023 | 260 | 243 | 46 | 44 | 15 |
| 2024 | 262 | 242 | 51 | 48 | 18 |
| 2025 | 261 | 240 | 55 | 54 | 18 |
| 2026 | 176 | 163 | 24 | 23 | 12 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 300 | 5 | 0 | 17.127 | 16.791 |
| 15 | 294 | 11 | 0 | 27.787 | 30.859 |
| 30 | 285 | 20 | 0 | 40.025 | 42.836 |
| 60 | 266 | 39 | 0 | 56.736 | 56.852 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 101 |
| invalidation_observed | 168 |
| missing_future_coverage | 2 |
| objective_observed | 34 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 101 |
| invalidation_observed | 168 |
| missing_future_coverage | 2 |
| objective_observed | 34 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 168 | 1017.962 | 723.696 |
| objective_observed | 34 | 1383.247 | 1176.313 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 163 | 1613 | 0.095 |
| NY_PM_1200_1600 | 129 | 1613 | 0.079 |
| overnight_00_06 | 3 | 1613 | 0.002 |
| premarket_06_0930 | 10 | 1613 | 0.006 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 163 | 59.531 | 62.169 | expired_without_observed_boundary: 40; invalidation_observed: 99; objective_observed: 24 |
| NY_PM_1200_1600 | 90 | 54.550 | 48.308 | expired_without_observed_boundary: 56; invalidation_observed: 62; missing_future_coverage: 2; objective_observed: 9 |
| overnight_00_06 | 3 | 40.250 | 33.667 | expired_without_observed_boundary: 1; invalidation_observed: 2 |
| premarket_06_0930 | 10 | 35.800 | 54.025 | expired_without_observed_boundary: 4; invalidation_observed: 5; objective_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 8 |
| current input prefix has unknown intervals | 70 |
| no dated P-zone bands/destinations | 35 |
| same_contract_prior_scope_unknown | 34 |

## management

Source: FORMULAS:M01; management process/management unit.

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

[Machine-readable results](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/MEASUREMENT_RESULTS.json) · [Coverage and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz) · [Per-setup records](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/setup-records.jsonl.gz) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md).
