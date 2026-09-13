<!-- full-phase1-measurement-current -->
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
<!-- /full-phase1-measurement-current -->

## Preserved implementation and prior measurement history

# JJumboFX — SDRange / Time-Based Ranges framework

<!-- phase1-strategy-current -->
## Current reconstructed strategy

JJ-TBR: 16 setup, 74 no setup, 0 unavailable input. Personal execution requirements are excluded from qualification.

[Current method report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/JJ-TBR.md) · [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

| Scope and classification | Observations |
| --- | --- |
| entry_setup:no_setup | 74 |
| entry_setup:setup | 16 |

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
| judas_outbound | 5 | 3 | 2 | 1 | observed_subset_with_input_limits |
| judas_reversal | 4 | 0 | 4 | 4 | observed_subset_with_input_limits |
| single_extended | 1 | 0 | 1 | 1 | observed_subset_with_input_limits |
| single_purged | 1 | 0 | 1 | 1 | observed_subset_with_input_limits |
| internal_rotation | 2 | 0 | 2 | 2 | observed_subset_with_input_limits |
| extension_reaction | 6 | 0 | 6 | 2 | observed_subset_with_input_limits |
| other_session | 33 | 5 | 28 | 13 | observed_subset_with_input_limits |
| timed_pzone_reversal | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |
| unit: management | 0 | 0 | 0 | 0 | observed_subset_with_input_limits |

**judas_outbound** — pre-open direction → 09:30 outbound → selected exhaustion → exit by reversal window. Source: TBR pp.8–10. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records); formation_has_no_observed_executions (1 job records).

**judas_reversal** — frozen range/context → edge sweep → 09:40–09:50 block/rejection → opposing draw. Source: TBR pp.8–11,27–29. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records); formation_has_no_observed_executions (1 job records).

**single_extended** — extended overnight → EQ/quadrant → directional confirmation → range-edge target/reduced expectation. Source: TBR pp.12–14,24. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records); formation_has_no_observed_executions (1 job records).

**single_purged** — dated prior-liquidity purge → compressed range → internal contact/confirmation → expansion. Source: TBR pp.12–15. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records); formation_has_no_observed_executions (1 job records).

**internal_rotation** — wide balanced context → named internal → actual reversal signature → nearer named target. Source: JR pp.3,38–43;TBR pp.12,24. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records); formation_has_no_observed_executions (1 job records).

**extension_reaction** — prior expansion → actual parent 1.33–1.66 projection → response → still-unused objective. Source: TBR pp.20–21;JR pp.23–26,57. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records); formation_has_no_observed_executions (1 job records).

**other_session** — one of seven published formations → fixed context/location → selected confirmation/risk/objective. Source: TBR p.7,36;JR pp.46,50–51. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records); formation_has_no_observed_executions (7 job records).

**timed_pzone_reversal** — dated supplied P-zone → contact → reversal → directed named destination. Source: JR pp.16–18,53–55,58–62. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_jumbo`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `source_zone_known`, `zone_known_at`: dated source P-zone band ID, bounds, active state, generator version and named destination. Source catalog contains case readouts/settings, not a historical 2020+ P-zone series or generator. Usage scanner accepts dated supplied bands; no approximate substitute. Source: JR pp.16–18,53–55,58–62;O019.

Inspected local evidence: ['planning/phase-1-live/wiki/p-zones-benchmark.md', 'implementation/src/trading_research/research/method_pack/source_cases_v2.json'].

Recorded scope/record limits: no dated P-zone bands/destinations (7 job records); calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records); dated source P-zone band ID, bounds, active state, generator version and named destination (7 job records).

**management** — management process/management unit. Source: FORMULAS:M01. Scanner: `trading_research.research.method_pack.native_discovery:extra_jumbo`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Remaining operand(s) `daily_r_before`, `daily_limit_allows_entry`: actual account/session closed R and active quantity/order ledger. Public market events and illustrated tickets are not a historical account ledger. The connected process interface audits supplied real records; market-stage measurement does not wait for them. Source: STOP pp.12,14;O140,O145,O150.

Inspected local evidence: ['implementation/src/trading_research/research/method_pack/objects/lifecycles.py', 'implementation/src/trading_research/research/method_pack/source_cases_v2.json'].

Recorded scope/record limits: actual dated process/source records absent (7 job records); actual account/session closed R and active quantity/order ledger (7 job records).

Native market/process research is executed; author-exact verdicts and faithful disagreements remain unknown. No comparison observation is represented as a fill. [Date-level evidence for this method](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/JJ-TBR.md) · [Software acceptance and remaining external inputs](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md).

<!-- /phase1-native-v2-current -->

## Source definitions and retained historical comparison notes

Operating method / JJ-TBR. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


**Why one method.** The manual calls false breakout/Judas and range breakout applications of the same time-based framework ([TBR] pp.6–12). The raw record says “same ranges, different layers” on 15 May 2026 and “same 6-9 framework, more refinement” when adding order flow on 23 February ([JR] pp.11, 14, posts 2055344660986364371 / 2026059018750378427). The later summary is the author's own ordered phrase: context, location, confirmation ([JR] p.33, post 2093335135789719861).

### Ordered loop and attachments

| Step | Source operation, in order | Current implementation and evidence limits |
|---|---|---|
| 1. Choose the session and freeze its geometry | Select the range being traded. Main NY formation is 06:00–09:00 ET; draw H/L, width, EQ, quadrants, range open/close and projections. The manual also lists Asia 20:00–20:30, midnight 00:00–00:30, London 03:00–03:30, 09:30–10:00, 10:00–10:30, lunch 12:00–12:30 and 15:00–15:30. These are applications of the framework, not eight entry products. ([TBR] pp.4–7.) | [O003](clock-grid-and-bars.md) · [O005](tbr-6-9-range.md) · [O006](tbr-remaining-clocks.md) · [O007](range-internals.md) · [O008](range-open-close.md) · [O016](nested-range-geometry.md). Frozen clocks, exact parent identities and nested geometry are implemented. Automatic selection of the author's preferred session remains source-dependent. |
| 2. Set expectations before the entry | Read overnight size and balance, liquidity already purged, open versus previous RTH value/range and today's box, news, and current behavior. Wide/extended overnight and range-bound news conditions reduce targets and risk; compressed/purged conditions can favor single-direction expansion. The raw July examples include continuation from outside value while still inside the prior price range: “outside both AND high RVOL” is a particular case, not the only permission to continue. ([TBR] pp.12, 16–24; [JR] pp.33–39, 48–49.) | [O009](range-width-context.md) · [O010](range-path-class.md) · [O011](overnight-range.md) · [O012](overnight-purge.md) · [O013](open-location-switch.md) · [O027](relative-volume.md) · [O029](news-event-context.md). Chronological purges, opening observations, completed-window relative volume and causal news admission are implemented. Final path labels remain outcomes; later opening volume cannot inform the cash-open decision. |
| 3. Choose a location and a destination within that case | Exhaustion beyond a swept edge, EQ/quadrants on internal entries, 1.33–1.66 after expansion, or a source-drawn P-zone/expected-range boundary. Preserve separate identities for 6–9 EQ, EV midpoint, SessionStat bands, P-zones, and RTH/profile references. Mark the remaining directional objective before acting. ([TBR] pp.8–24, 31–35; [JR] pp.3, 23–26, 48, 53–57.) | [O014](range-exhaustion-area.md) · [O015](extensions-1-33-1-66.md) · [O017](sessionstat-9-12-envelope.md) · [O018](ev-range-expected-move.md) · [O019](p-zones-benchmark.md) · [O020](pd-rth-range-plus.md) · [O087](unfinished-business.md). Range projections and the remaining-object ledger are implemented. EVRange, P-zone and Stat+ proprietary construction remains unavailable; supplied source readouts retain their settings and times. |
| 4. Let the selected location produce the selected entry signature | The manual's favorite reversal entries use 2/3/5-minute orderblocks or rejection blocks; they are expressly personal entry choices, not fixed to the model. Later charts add absorption candles, BigTrades, footprint/profile behavior, and refinements at the same range levels. Use the confirmation actually present in that source episode. ([TBR] pp.27–31, 35; [JR] pp.14, 48, 50, 52, 67–69.) | [O004](execution-bars.md) · [O055](fvg-body-gaps.md) · [O056](sweep-cisd-blocks.md) · [O057](rejection-block.md) · [O058](absorption-candle-jumbo.md) · [O063](developing-profile.md) · [O077](weekly-delta-profile.md) · [O099](big-trades.md) · [O120](footprint.md). Selected-parent geometry, mirrored blocks, native profiles and local execution observations are implemented. Source confirmation choice and unavailable platform settings remain explicit inputs. |
| 5. Enter with the case's risk and target policy | Choose immediate, retracement, or stop-triggered execution and structural invalidation. The OB example distinguishes a midpoint stop/entry from a conservative boundary stop. Size and target ambition depend on the case. Do not turn a ticket's points or R:R into a universal preset. ([TBR] pp.24–29; [JR] pp.3, 54–57.) | [O139](structural-risk.md) · [O140](position-sizing.md) · [O141](trade-objective.md) · [O150](order-lifecycle.md). Entry-side invalidation, exposure, fixed objective and order lifecycle are implemented. A historical source entry or fill still requires its actual linked record. |
| 6. Manage, recognize failure, and reassess | Take the appropriate internal/opposite/external objective, protect or compound justified winners, and reduce ambition in grind. Three failed reversal attempts at the same level, strong bodies/volume continuing through it, or absent rejection defeat a reversal idea. Exit and observe; if continuing after failure the manual says reduce allocation at least 50%. Reassess another case/session rather than relabel the failed fade as a successful breakout. ([TBR] pp.24, 36–37.) | [O024](jumbo-failure-attempts.md) · [O026](confirmed-swing-midpoint.md) · [O142](position-management.md) · [O145](daily-loss-limit.md) · [O150](order-lifecycle.md). Distinct attempts, protected geometry, amendments, partials and session constraints are implemented. Supplied source policies and actual management records remain necessary. |

### Branches inside this loop

| Branch | Source sequence and objective | Boundary on interpretation |
|---|---|---|
| `judas_outbound` — Judas Trade #1 | At the 09:30 open, take the contextual move toward the selected exhaustion projection; close as the 09:40–09:50 reversal window arrives. ([TBR] pp.8–10.) | The direction and exact entry selection are not supplied by the later double-break label. This is an outbound leg, not the reversal entry. |
| `judas_reversal` — Judas Trade #2 | A completed range edge is swept; the exhaustion area produces a reversal signature, normally in the manual's 09:40–09:50 window; trade back through internal levels toward the opposite liquidity/projections. ([TBR] pp.8–11, 27–29.) | A mandatory exact ±0.5 touch is too narrow. Raw charts include shallow edge sweeps. Record depth; do not choose the deepest eventual excursion retrospectively. |
| `single_extended` | Extended overnight: wait for an EQ/quadrant entry in the allowed direction, usually take the range edge, moderate risk and expansion expectations. ([TBR] pp.12–14, 24.) | The eventual “single break” cannot be an entry-time input. “Extended” has no author-exact universal width ratio. |
| `single_purged` | Overnight stop hunts have already removed the relevant liquidity; the contracted range supports expansion from EQ/quadrants. 09:40–09:50 can be a continuation/add window, not a compulsory reversal. ([TBR] pp.12–15.) | Preserve the actual overnight references and when they were taken. Containment of two completed boxes is not a purge-time ledger. |
| `internal_rotation` | In the appropriate wide/in-value context, take confirmed rotations at EQ/expected-range locations, with nearer objectives. The 2 September raw example explicitly trades EQ both ways on a big 6–9 range and includes two losing attempts. ([JR] p.3, post 2095172969035096454; pp.38–43.) | EQ is a location; the author does not publish “touch EQ = reverse.” EV and EQ are different targets. |
| `extension_reaction` | After range expansion reaches the 1.33–1.66 area, examine rejection/continuation and the still-owed objective. The September 9 example combines session-average lows, that extension area, and equal highs as the long's destination. ([TBR] pp.20–21; [JR] pp.23–26, 57, 71.) | Extension touch, HOD/LOD in the band, and a confirmed reversal are different observations. Each projection uses its actual parent range width. |
| `other_session` | Apply the selected geometry and signatures to the observed London or later-session case. AM consolidation can precede PM expansion; AM expansion can precede PM consolidation. ([TBR] pp.7, 36; [JR] pp.46, 50–51, 63–66.) | Modern London charts freeze a box before the marked action; the retained 00:00–03:00 assumption is not a verified universal author clock. A source-known clock is required. “London is cleaner this cycle” does not publish a rolling-ten-day selector. |
| `timed_pzone_reversal` | Use the actual time-anchored P-zone and observed reversal sequence. The January 2 post's “low > range open” describes a path from the low to the range-open line; the December 17 post's “10 am p-zone > london low” names another path. ([JR] pp.53–55.) | The arrow is not an inequality. A 09:00 zone anchor is not proof of a 09:00 fill. Later time-specific examples must not be forced into the manual's 09:40 window. |

**PD RTH Range+ is a context/destination application.** It uses prior 09:30–16:00 highs/lows and M15/H1 imbalances, waits for current RTH direction, then trades toward those objectives with the range framework. In this expressly RTH-only view, an ETH sweep does not consume the RTH objective ([TBR] pp.32–35). This exception does not erase overnight purge information in `single_purged`. [O020](pd-rth-range-plus.md), [O055](fvg-body-gaps.md) and [O087](unfinished-business.md) implement the selected references, availability and remaining-object scope; historical source direction still requires evidence known before the decision.

**SessionStat, EV, P-zones, and flow are not standalone trades.** SessionStat's average/median high-low areas, minimum-average levels, projection extensions, selected session, and lookback frame likely reach/exhaustion ([SS] pp.3–12); its choppy/low-volatility limitations remain part of the read. The source settings do not publish the exact minimum-average engine. P-zone settings show learning-window/percentile controls, not a recoverable formula ([JR] pp.16–18, 58–62). Newer nested profile/range spans must not be mistaken for outer 6–9 width or automatically named EV.

Jumbo explicitly distinguishes BigTrades from absorption bubbles and gives **NQ 100 during NY, 75 during London** ([JR] p.50). An MNQ chart is not evidence for an NQ print-size threshold. The Absorption Zone+ settings actually display body threshold **0.6**, volume multiplier **1.5**, and a **14-period** volume average ([TBR] p.35); the old “unprinted” claim is wrong. Those settings still do not prove passive replenishment. The OB is the second candle's full range; a rejection block is its rejection wick. The two “midpoint” stop captions on p.29 conflict with the differently drawn stops; retain the fixture's geometry and mark the generic conservative rule unresolved.

### Phase 1 predicate — `JJ-TBR`

The branch fields below are observations made by the decision time: `extended_context`, `purged_compressed_context`, `rotation_context`, and `directional_context` are source-context labels, not final-session path classes. `source_confirmation` identifies the chosen OB/rejection/flow signature and its location/side. `source_time_window` is the documented timing for that particular branch/fixture.

```sql
range_frozen AND context_fixed AND location_touched
AND source_confirmation AND risk_defined AND objective_fixed
AND range_known_at <= touch_at
AND context_at <= touch_at AND touch_at <= confirm_at
AND confirm_at <= decision_at
AND CASE branch
  WHEN 'judas_outbound' THEN
    directional_context AND at_rth_open
    AND objective_is_selected_exhaustion AND exit_window_recorded
  WHEN 'judas_reversal' THEN
    reversal_context AND edge_swept AND sweep_at <= confirm_at
    AND source_time_window AND objective_is_opposing_draw
  WHEN 'single_extended' THEN
    extended_context AND entry_at_eq_or_quadrant
    AND objective_is_range_edge AND reduced_expectations
  WHEN 'single_purged' THEN
    purged_compressed_context AND purge_known_at < decision_at
    AND entry_at_eq_or_quadrant AND expansion_policy
  WHEN 'internal_rotation' THEN
    rotation_context AND entry_at_named_internal_or_ev_band
    AND objective_is_named_rotation_target
  WHEN 'extension_reaction' THEN
    prior_expansion AND touch_in_source_extension_area
    AND reaction_side_confirmed AND objective_is_remaining_draw
  WHEN 'other_session' THEN
    source_clock_verified AND source_case_verified
  WHEN 'timed_pzone_reversal' THEN
    source_zone_known AND source_time_window
    AND zone_known_at <= touch_at AND directed_path_recorded
  ELSE NULL
END
```

Citations for the sequence: [TBR] pp.6–12, 20–29, 37; [JR] pp.3, 14, 25, 33, 50–57. A source-drawn proprietary band can support a fixture check; an automatically generated approximation cannot set `source_zone_known` true. Report branch eligibility, confirmation, and directional target outcomes separately. Negative controls include momentum through an exhaustion level without rejection, a presumed purge occurring after entry, and a location/target picked from the final morning range. No current R-J predicate establishes this whole loop.

## Definition and scanner correction — 2026-09-13

The five legacy `unavailable_definition` rows below **have source definitions and implemented M01 predicates**. No comparison scanner was registered for them in empirical v1. Their source sequences above remain the definitions; this table identifies the work still needed for historical discovery.

| Branch | Existing definition and implementation | Actual unresolved scope |
|---|---|---|
| `judas_outbound` | TBR pp.8–10 defines the cash-open outbound leg, exhaustion destination and exit approaching 09:40–09:50; M01 checks its ordered context and objective. | Build discovery using an explicit pre-open directional/context rule and selected confirmation. The later day's path cannot supply direction retrospectively. The cash-open clock itself is known. |
| `single_extended` | TBR pp.12–14, 24 defines extended overnight context, EQ/quadrant entry, range-edge target and reduced expectations; M01 and [range-width geometry](range-width-context.md) exist. | Operationalize context classification and entry confirmation. The printed 106.50 range on p.13 is an example, not a universal extended threshold. The target/reduced-expectation policy is published, contrary to the blanket registry reason. |
| `single_purged` | TBR pp.12–15 defines prior overnight stop hunts followed by expansion from internals; [purge lifecycle](overnight-purge.md) and M01 ordering exist. | Connect named prior-liquidity references, their causal sweeps and compressed context to discovery. Some reference/confirmation selection remains to be specified; the purge sequence is defined. |
| `other_session` | TBR p.7 prints seven additional formation windows: 20:00–20:30, 00:00–00:30, 03:00–03:30, 09:30–10:00, 10:00–10:30, 12:00–12:30, 15:00–15:30; [O006](tbr-remaining-clocks.md) builds explicitly clocked ranges. | The registry's blanket claim that formation clocks are absent is incorrect. Implement manual variants with their applicable confirmation/action rules. Verify later-platform London configuration separately; its uncertainty does not invalidate the printed manual clocks. |
| `timed_pzone_reversal` | JR pp.53–55 defines the illustrated directed reversals; [O019](p-zones-benchmark.md) and M01 check supplied zone identity, state and path. | Historical automatic P-zone generation or a historical series of actual source zones is missing. JR pp.16–18, 58–62 shows controls rather than the formula. This is a zone-generation/input limitation, not absence of the reversal usage definition. |

These are unscanned historical populations, not zero-opportunity searches. See the [source/evaluator/scanner distinction](current-status.md#correction-definitions-exist-18-branches-were-not-scanned). No scanner or empirical result changed in this correction.

## Implementation and empirical status — 2026-09-12

The [M01 contract](../FORMULAS.md#m01) and its 40 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following historical dispositions. **`unavailable_definition` is the original registry label, not the current assessment of source availability; those rows were not scanned.** Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `judas_outbound` | `unavailable_definition` | unavailable | — | — |
| `judas_reversal` | `data_hole` | 26 / 77 / 9 | 161 / 161 | 37 |
| `single_extended` | `unavailable_definition` | unavailable | — | — |
| `single_purged` | `unavailable_definition` | unavailable | — | — |
| `internal_rotation` | `data_hole` | 65 / 35 / 0 | 161 / 161 | 37 |
| `extension_reaction` | `data_hole` | 50 / 38 / 1 | 161 / 161 | 37 |
| `other_session` | `unavailable_definition` | unavailable | — | — |
| `timed_pzone_reversal` | `unavailable_definition` | unavailable | — | — |

All scheduled comparison jobs are accounted for. The unsupported branches had no historical searches scheduled; they were recorded as dispositions only. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. Separate `management` units remain supplied-only and outside the market-opportunity denominator. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Session and range geometry.** [Jumbo's 06:00–09:00 range](tbr-6-9-range.md) · [Other time-based range formations](tbr-remaining-clocks.md) · [Range EQ and quadrants](range-internals.md) · [Source range-open and range-close references](range-open-close.md) · [Range width and expectations](range-width-context.md) · [Retrospective range path](range-path-class.md) · [Overnight high, low and width](overnight-range.md) · [Chronological liquidity purges](overnight-purge.md) · [Opening location and participation](open-location-switch.md) · [Range exhaustion and mean-reversal area](range-exhaustion-area.md) · [The 1.33–1.66 extension area](extensions-1-33-1-66.md) · [Nested source range geometry](nested-range-geometry.md) · [SessionStat+ envelopes](sessionstat-9-12-envelope.md) · [Jumbo EVRange](ev-range-expected-move.md) · [Time-anchored P-zones](p-zones-benchmark.md) · [PD RTH Range+ destinations](pd-rth-range-plus.md) · [Jumbo reversal and action windows](reversal-time-window.md) · [Source session-cleanliness assessment](clean-session-label.md) · [Accumulation, manipulation and distribution phases](amd-phase-labels.md) · [Jumbo failure signatures and three attempts](jumbo-failure-attempts.md) · [Opening-range midpoint reference](opening-range-midpoint.md) · [Confirmed swing midpoint retrace](confirmed-swing-midpoint.md) · [Relative-volume context at the open](relative-volume.md) · [Equal-high or equal-low liquidity objective](equal-high-low-objectives.md).

**Regime and thesis context.** [Scheduled news and changing information](news-event-context.md).

**Price references and price-action confirmation.** [Sweep, failure and reclaim](sweep-reclaim.md) · [Prior day, week and month extremes](prior-day-week-month-levels.md) · [09:30 cash-open price](cash-open-reference.md) · [Fair-value gaps and higher-timeframe imbalances](fvg-body-gaps.md) · [Jumbo orderblocks](sweep-cisd-blocks.md) · [Jumbo rejection blocks](rejection-block.md) · [Jumbo Absorption Zone+ candle](absorption-candle-jumbo.md).

**Auction and profile structure.** [Volume profile](value-and-profiles.md) · [Profile value area](value-area.md) · [Developing profile snapshot](developing-profile.md) · [Profile point of control](profile-poc.md) · [High-volume node](hvn.md) · [Low-volume node](lvn.md) · [Profile shelf](profile-shelf.md) · [Profile ledge](profile-ledge.md) · [Overnight volume structure](overnight-profile.md) · [ETH profile identity](prior-eth-profile.md) · [Signed volume-by-price profile](weekly-delta-profile.md) · [Prior-session auction landmarks](prior-session-reference-levels.md) · [Remaining auction objectives](unfinished-business.md) · [Source-conditioned reference statistics](reference-statistics.md).

**Order-flow evidence.** [Executed aggressor-side trades](aggressor-trades.md) · [BigTrades aggression markers](big-trades.md) · [Absorption: effort without price reward](absorption-and-big-trades.md) · [Local delta concentration at an extreme](delta-spike.md) · [Native candle footprint](footprint.md).

**Risk, objectives and process.** [Entry-side structural invalidation](structural-risk.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md) · [Source account and session stop](daily-loss-limit.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md) · [Economic observation and release vintage](economic-release-vintage.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[JR]: </workspace/sources/x-raw-2026-09-11/JJumboFX_Raw_X_Archive_v2.pdf>
[TBR]: </workspace/sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf>
[SS]: </workspace/sources/documents/jumbo/SessionStat+.pdf>
[FORMULAS]: </workspace/planning/phase-1-live/FORMULAS.md>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
