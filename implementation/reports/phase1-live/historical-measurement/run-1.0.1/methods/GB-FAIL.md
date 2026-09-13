# GB-FAIL — full acquired Phase 1 measurement

Implementation: accepted reconstructed setup rules, including disclosed inferred models. Historical session search: every frozen date through the owned NQ input endpoint. Setup qualification is distinct from subsequent outcomes and from actual fills.

| Branch | Scope | Searched sessions | Complete eligible sessions | Observed setups | Complete zero-setup sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- | --- |
| nyam_box | entry_setup | 1742 | 1716 | 1063 | 796 | 14 |
| previous_hour | entry_setup | 1742 | 1702 | 5353 | 81 | 28 |
| asia_tdo_case | entry_setup | 1742 | 1662 | 168 | 1499 | 68 |
| prior_day_level | entry_setup | 1742 | 1683 | 532 | 1184 | 47 |
| prior_week_level | entry_setup | 1742 | 1676 | 219 | 1460 | 54 |
| prior_month_level | entry_setup | 1742 | 1497 | 98 | 1399 | 233 |
| cash_open_reclaim_case | entry_setup | 1742 | 1676 | 156 | 1520 | 54 |
| mss_fvg_refinement | supplemental_observation | 1742 | 0 | 0 | 0 | 10 |

Eligible denominators require complete observed inputs for the branch and no active input limitation. Setups observed in limited sessions remain in the observed population and are excluded from the complete-session frequency numerator. Context, supplemental, personal and collection units do not enter entry-setup denominators.

Outcome tables describe all qualifying observed setups, including those in input-limited sessions. Complete future coverage is a separate requirement for excursion means; the per-setup record retains the input-eligibility flag.

## nyam_box

Source: GB pp.21,23,25,27,30–35,38–40,43; finished 09–10 box → contextual sweep → five-minute reclaim → opposing box liquidity.

Setups per complete eligible session: 0.618. Observed setups per searched session: 0.610.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 259 | 171 | 171 | 1 |
| 2021 | 261 | 258 | 149 | 149 | 2 |
| 2022 | 260 | 258 | 139 | 139 | 1 |
| 2023 | 260 | 254 | 163 | 162 | 4 |
| 2024 | 262 | 258 | 155 | 154 | 2 |
| 2025 | 261 | 257 | 180 | 180 | 1 |
| 2026 | 176 | 172 | 106 | 106 | 3 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 1054 | 9 | 0 | 17.416 | 17.508 |
| 15 | 1045 | 18 | 0 | 28.593 | 30.155 |
| 30 | 1041 | 22 | 0 | 40.037 | 40.990 |
| 60 | 1022 | 41 | 0 | 53.411 | 55.077 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 159 |
| invalidation_observed | 772 |
| missing_future_coverage | 9 |
| objective_observed | 123 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 159 |
| invalidation_observed | 772 |
| missing_future_coverage | 9 |
| objective_observed | 123 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 772 | 584.352 | 289.265 |
| objective_observed | 123 | 1491.585 | 1297.105 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 904 | 1716 | 0.526 |
| NY_PM_1200_1600 | 159 | 1716 | 0.093 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 904 | 54.006 | 56.012 | expired_without_observed_boundary: 125; invalidation_observed: 667; objective_observed: 112 |
| NY_PM_1200_1600 | 118 | 48.852 | 47.913 | expired_without_observed_boundary: 34; invalidation_observed: 105; missing_future_coverage: 9; objective_observed: 11 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 10 |

## previous_hour

Source: GB pp.21,23,25,27,30–35,38–40,43; finished prior clock-hour reference → contextual sweep → reclaim → opposing hour liquidity.

Setups per complete eligible session: 3.108. Observed setups per searched session: 3.073.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 256 | 760 | 748 | 4 |
| 2021 | 261 | 256 | 752 | 747 | 4 |
| 2022 | 260 | 258 | 765 | 765 | 1 |
| 2023 | 260 | 251 | 852 | 832 | 7 |
| 2024 | 262 | 258 | 807 | 804 | 2 |
| 2025 | 261 | 255 | 829 | 823 | 3 |
| 2026 | 176 | 168 | 588 | 571 | 7 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 5307 | 46 | 0 | 14.613 | 14.992 |
| 15 | 5227 | 126 | 0 | 24.538 | 25.521 |
| 30 | 5138 | 215 | 0 | 34.506 | 35.150 |
| 60 | 4562 | 791 | 0 | 48.015 | 48.743 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 645 |
| invalidation_observed | 3794 |
| missing_future_coverage | 45 |
| objective_observed | 869 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 645 |
| invalidation_observed | 3794 |
| missing_future_coverage | 45 |
| objective_observed | 869 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 3794 | 596.834 | 279.649 |
| objective_observed | 869 | 1135.644 | 906.071 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 2283 | 1702 | 1.325 |
| NY_PM_1200_1600 | 3070 | 1702 | 1.783 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 2283 | 57.134 | 57.855 | expired_without_observed_boundary: 237; invalidation_observed: 1553; objective_observed: 493 |
| NY_PM_1200_1600 | 2279 | 38.879 | 39.614 | expired_without_observed_boundary: 408; invalidation_observed: 2241; missing_future_coverage: 45; objective_observed: 376 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 10 |

## asia_tdo_case

Source: GB pp.21,23,25,27,30–35,38–40,43; completed Asia range + midnight TDO → sweep → reclaim with TDO confirmation.

Setups per complete eligible session: 0.100. Observed setups per searched session: 0.096.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 256 | 26 | 26 | 4 |
| 2021 | 261 | 248 | 29 | 29 | 12 |
| 2022 | 260 | 249 | 26 | 26 | 10 |
| 2023 | 260 | 247 | 24 | 23 | 11 |
| 2024 | 262 | 248 | 23 | 23 | 12 |
| 2025 | 261 | 248 | 25 | 24 | 10 |
| 2026 | 176 | 166 | 15 | 15 | 9 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 168 | 0 | 0 | 22.917 | 21.131 |
| 15 | 168 | 0 | 0 | 36.062 | 35.501 |
| 30 | 167 | 1 | 0 | 51.554 | 48.790 |
| 60 | 166 | 2 | 0 | 70.081 | 59.634 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 8 |
| invalidation_observed | 63 |
| objective_observed | 97 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 8 |
| invalidation_observed | 63 |
| objective_observed | 97 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 63 | 468.403 | 385.821 |
| objective_observed | 97 | 499.197 | 173.374 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 155 | 1662 | 0.092 |
| NY_PM_1200_1600 | 13 | 1662 | 0.008 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 155 | 69.966 | 59.600 | expired_without_observed_boundary: 7; invalidation_observed: 56; objective_observed: 92 |
| NY_PM_1200_1600 | 11 | 71.705 | 60.114 | expired_without_observed_boundary: 1; invalidation_observed: 7; objective_observed: 5 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |

## prior_day_level

Source: GB pp.21,23,25,27,30–35,38–40,43; same-contract previous actual RTH reference → sweep/reclaim → selected opposing level.

Setups per complete eligible session: 0.316. Observed setups per searched session: 0.305.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 253 | 74 | 74 | 7 |
| 2021 | 261 | 251 | 81 | 81 | 9 |
| 2022 | 260 | 253 | 82 | 82 | 6 |
| 2023 | 260 | 252 | 86 | 86 | 6 |
| 2024 | 262 | 253 | 65 | 65 | 7 |
| 2025 | 261 | 252 | 85 | 85 | 6 |
| 2026 | 176 | 169 | 59 | 58 | 6 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 527 | 5 | 0 | 22.029 | 19.929 |
| 15 | 524 | 8 | 0 | 35.526 | 33.507 |
| 30 | 517 | 15 | 0 | 49.175 | 46.993 |
| 60 | 509 | 23 | 0 | 63.221 | 61.790 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 138 |
| invalidation_observed | 363 |
| missing_future_coverage | 5 |
| objective_observed | 26 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 138 |
| invalidation_observed | 363 |
| missing_future_coverage | 5 |
| objective_observed | 26 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 363 | 731.104 | 385.821 |
| objective_observed | 26 | 1661.367 | 1632.794 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 441 | 1683 | 0.262 |
| NY_PM_1200_1600 | 91 | 1683 | 0.053 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 441 | 65.235 | 62.203 | expired_without_observed_boundary: 119; invalidation_observed: 299; objective_observed: 23 |
| NY_PM_1200_1600 | 68 | 50.158 | 59.114 | expired_without_observed_boundary: 19; invalidation_observed: 64; missing_future_coverage: 5; objective_observed: 3 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 8 |
| current input prefix has unknown intervals | 10 |
| same_contract_prior_scope_unknown | 34 |

## prior_week_level

Source: GB pp.21,23,25,27,30–35,38–40,43; same-contract prior-week matching sessions → sweep/reclaim → selected opposing level.

Setups per complete eligible session: 0.131. Observed setups per searched session: 0.126.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 254 | 28 | 28 | 6 |
| 2021 | 261 | 247 | 29 | 29 | 13 |
| 2022 | 260 | 253 | 34 | 34 | 6 |
| 2023 | 260 | 252 | 33 | 33 | 6 |
| 2024 | 262 | 251 | 34 | 34 | 9 |
| 2025 | 261 | 252 | 33 | 33 | 6 |
| 2026 | 176 | 167 | 28 | 28 | 8 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 219 | 0 | 0 | 18.588 | 18.979 |
| 15 | 215 | 4 | 0 | 33.448 | 30.860 |
| 30 | 213 | 6 | 0 | 48.933 | 39.386 |
| 60 | 210 | 9 | 0 | 63.606 | 53.256 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 75 |
| invalidation_observed | 144 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 75 |
| invalidation_observed | 144 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 144 | 587.035 | 300.253 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 166 | 1676 | 0.099 |
| NY_PM_1200_1600 | 53 | 1676 | 0.032 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 166 | 68.508 | 55.776 | expired_without_observed_boundary: 55; invalidation_observed: 111 |
| NY_PM_1200_1600 | 44 | 45.114 | 43.750 | expired_without_observed_boundary: 20; invalidation_observed: 33 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 40 |
| current input prefix has unknown intervals | 10 |
| same_contract_prior_scope_unknown | 40 |

## prior_month_level

Source: GB pp.21,23,25,27,30–35,38–40,43; same-contract prior-month matching sessions → sweep/reclaim → selected opposing level.

Setups per complete eligible session: 0.065. Observed setups per searched session: 0.056.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 238 | 9 | 9 | 22 |
| 2021 | 261 | 236 | 19 | 19 | 24 |
| 2022 | 260 | 214 | 13 | 13 | 45 |
| 2023 | 260 | 234 | 12 | 12 | 24 |
| 2024 | 262 | 235 | 14 | 14 | 25 |
| 2025 | 261 | 212 | 17 | 17 | 46 |
| 2026 | 176 | 128 | 14 | 14 | 47 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 98 | 0 | 0 | 24.429 | 19.227 |
| 15 | 98 | 0 | 0 | 39.401 | 32.365 |
| 30 | 97 | 1 | 0 | 51.361 | 43.369 |
| 60 | 94 | 4 | 0 | 72.043 | 54.963 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 30 |
| invalidation_observed | 68 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 30 |
| invalidation_observed | 68 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 68 | 737.181 | 442.984 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 81 | 1497 | 0.054 |
| NY_PM_1200_1600 | 17 | 1497 | 0.011 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 81 | 76.451 | 56.096 | expired_without_observed_boundary: 28; invalidation_observed: 53 |
| NY_PM_1200_1600 | 13 | 44.577 | 47.904 | expired_without_observed_boundary: 2; invalidation_observed: 15 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 219 |
| current input prefix has unknown intervals | 10 |
| same_contract_prior_scope_unknown | 219 |

## cash_open_reclaim_case

Source: GB pp.21,23,25,27,30–35,38–40,43; 09:30 open → below-open manipulation → reclaim → retracement objective with low invalidation.

Setups per complete eligible session: 0.093. Observed setups per searched session: 0.090.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 253 | 25 | 25 | 7 |
| 2021 | 261 | 252 | 20 | 20 | 8 |
| 2022 | 260 | 252 | 29 | 29 | 7 |
| 2023 | 260 | 251 | 21 | 21 | 7 |
| 2024 | 262 | 251 | 27 | 27 | 9 |
| 2025 | 261 | 252 | 24 | 24 | 6 |
| 2026 | 176 | 165 | 10 | 10 | 10 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 156 | 0 | 0 | 21.921 | 25.981 |
| 15 | 156 | 0 | 0 | 35.391 | 42.232 |
| 30 | 156 | 0 | 0 | 48.420 | 60.252 |
| 60 | 155 | 1 | 0 | 62.513 | 78.663 |

| Boundary outcome | n |
| --- | --- |
| invalidation_observed | 22 |
| objective_observed | 134 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| invalidation_observed | 22 |
| objective_observed | 134 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 22 | 126.388 | 69.172 |
| objective_observed | 134 | 30.463 | 2.399 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 155 | 1676 | 0.092 |
| NY_PM_1200_1600 | 1 | 1676 | 0.001 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 155 | 62.513 | 78.663 | invalidation_observed: 22; objective_observed: 133 |
| NY_PM_1200_1600 | 0 | — | — | objective_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| cash_open_order_unknown | 58 |
| current input prefix has unknown intervals | 10 |

## mss_fvg_refinement

Source: GB pp.21,23,25,27,30–35,38–40,43; completed parent reclaim → later three 2-minute candles → MSS plus actual wick FVG; annotation unit.

Setups per complete eligible session: —. Observed setups per searched session: —.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 0 | 0 | 0 | 1 |
| 2021 | 261 | 0 | 0 | 0 | 2 |
| 2022 | 260 | 0 | 0 | 0 | 1 |
| 2023 | 260 | 0 | 0 | 0 | 1 |
| 2024 | 262 | 0 | 0 | 0 | 2 |
| 2025 | 261 | 0 | 0 | 0 | 1 |
| 2026 | 176 | 0 | 0 | 0 | 2 |

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
| current input prefix has unknown intervals | 10 |

[Machine-readable results](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/MEASUREMENT_RESULTS.json) · [Coverage and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz) · [Per-setup records](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/setup-records.jsonl.gz) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md).
