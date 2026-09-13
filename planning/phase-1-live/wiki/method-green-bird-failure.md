<!-- full-phase1-measurement-current -->
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
<!-- /full-phase1-measurement-current -->

## Preserved implementation and prior measurement history

# Green Bird — failed breakout / failed breakdown

<!-- phase1-strategy-current -->
## Current reconstructed strategy

GB-FAIL: 22 setup, 62 no setup, 0 unavailable input. Personal execution requirements are excluded from qualification.

[Current method report](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/strategy-methods/GB-FAIL.md) · [Versioned policy](/workspace/implementation/reports/phase1-live/strategy-reconstruction/run-1.1.0-r1/registry/STRATEGY_POLICY.json) · [Source conformance](/workspace/planning/phase-1-live/STRATEGY_SOURCE_CONFORMANCE.md).

| Scope and classification | Observations |
| --- | --- |
| entry_setup:no_setup | 62 |
| entry_setup:setup | 22 |

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
| nyam_box | 7 | 3 | 4 | 1 | observed_subset_with_input_limits |
| previous_hour | 35 | 12 | 23 | 3 | observed_subset_with_input_limits |
| asia_tdo_case | 9 | 1 | 8 | 1 | observed_subset_with_input_limits |
| prior_day_level | 3 | 0 | 3 | 0 | observed_subset_with_input_limits |
| prior_week_level | 4 | 0 | 4 | 2 | observed_subset_with_input_limits |
| prior_month_level | 2 | 0 | 2 | 2 | observed_subset_with_input_limits |
| cash_open_reclaim_case | 5 | 0 | 5 | 0 | observed_subset_with_input_limits |
| mss_fvg_refinement | 3 | 0 | 3 | 0 | observed_subset_with_input_limits |

**nyam_box** — finished 09–10 box → contextual sweep → five-minute reclaim → opposing box liquidity. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

**previous_hour** — finished prior clock-hour reference → contextual sweep → reclaim → opposing hour liquidity. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

**asia_tdo_case** — completed Asia range + midnight TDO → sweep → reclaim with TDO confirmation. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

**prior_day_level** — same-contract previous actual RTH reference → sweep/reclaim → selected opposing level. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: calendar_unverified (5 job records); same_contract_prior_scope_unknown (4 job records).

**prior_week_level** — same-contract prior-week matching sessions → sweep/reclaim → selected opposing level. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: same_contract_prior_scope_unknown (11 job records); calendar_unverified (9 job records).

**prior_month_level** — same-contract prior-month matching sessions → sweep/reclaim → selected opposing level. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: same_contract_prior_scope_unknown (110 job records); calendar_unverified (11 job records).

**cash_open_reclaim_case** — 09:30 open → below-open manipulation → reclaim → retracement objective with low invalidation. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Recorded scope/record limits: cash_open_order_unknown (2 job records).

**mss_fvg_refinement** — completed parent reclaim → later three 2-minute candles → MSS plus actual wick FVG; annotation unit. Source: GB pp.21,23,25,27,30–35,38–40,43. Scanner: `trading_research.research.method_pack.historical_price_scanners:scan_green_failure`. Operational assumptions are frozen in the policy linked above; exact operands and their derivations are retained in the date-level evidence.

Native market/process research is executed; author-exact verdicts and faithful disagreements remain unknown. No comparison observation is represented as a fill. [Date-level evidence for this method](/workspace/implementation/reports/phase1-live/implementation-v2/run-2.0.0-r9/methods/GB-FAIL.md) · [Software acceptance and remaining external inputs](/workspace/implementation/reports/phase1-live/implementation-v2/COMPLETION_REPORT.md).

<!-- /phase1-native-v2-current -->

## Source definitions and retained historical comparison notes

Operating method / GB-FAIL. [Index](index.md) · [Phase 1 observation contract](source-sequence-fidelity.md) · [Source map](source-catalog.md)


**Source name and unification.** “Sweep → reclaim → opposing liquidity” is his own formulation ([GB] p.31). NYAM, Asia, prior hour, prior day/week/month, TDO confluence, and golden-pocket examples repeat this failure-and-reclaim mechanism. The raw golden-pocket explanation requires a failed breakdown and reclaim, or the PDL sweep followed by a five-minute close back below; the retracement band alone is not another strategy ([GB] pp.25, 31–35).

### Ordered loop and attachments

| Step | Source operation | Current implementation and evidence limits |
|---|---|---|
| 1. Establish the reference and contextual direction | Finish the selected box or use a known prior level. NYAM is 09:00–10:00 and that box cannot be traded as finished before 10:00. Previous-hour examples use the completed hour. Asia's drawn box is approximately 20:00–00:00; exact London bounds are not stated. Prior day, previous weekly candle, previous month, and an already-observed overnight reclaim can supply the context. ([GB] pp.23, 25, 27, 30–35, 38–40.) | [O003](clock-grid-and-bars.md) · [O046](session-fail-boxes.md) · [O048](prior-day-week-month-levels.md) · [O136](directional-bias.md). Completed reference windows, prior day/week/month geometry and attributed directional context are implemented. Same-contract prior coverage and exact source London bounds can remain unavailable. |
| 2. Locate the potential failure | Watch the relevant high/low or reclaimed level. Optional confluence includes PDH/PDL, Asia/London, midnight TDO, and the 50–61.8% retracement of the explicitly measured impulse. TDO is the midnight opening price; NWOG is a destination between the Friday-close and Sunday-open references. ([GB] pp.21, 25, 27, 32–39.) | [O049](true-day-open.md) · [O051](new-week-opening-gap.md) · [O052](golden-pocket.md) · [O053](premium-discount-50.md). TDO, NWOG endpoints and selected-impulse retracement geometry are implemented with parent identity and availability. The source still determines the impulse and endpoint convention. |
| 3. Wait for the sweep and its failure | Sweep above and fail back below → short; sweep below and reclaim → long. The explicit PDL and Asia/TDO examples wait for a completed five-minute close. Those cited close-confirmation variants wait for the reclaim. The November 20, 2025 figure separately shows entry at the high sweep ([GB] pp.31, 43); it must not inherit a later MSS/FVG prerequisite. ([GB] pp.21, 23, 25, 27, 30–35, 38.) | [O003](clock-grid-and-bars.md) · [O047](sweep-reclaim.md). Strict sweep/reclaim ordering and complete clock-aligned confirmations are implemented. The frozen comparison uses its declared endpoint and expiry; those parameters are not universal author rules. |
| 4. Preserve the case-specific entry and structural risk | Enter the reclaim or its retracement; the PDL reply says to wait a few points after the close and use a low-risk retracement. The November 20, 2025 MNQZ2025 two-minute figure displays a short entry at the 9–10 high sweep, at 25301.75. MSS/FVG is annotated later; exact fill time is not established. The September 1 09:30 manipulation/reclaim long is a distinct timing branch, not an early completed 9–10 box. ([GB] pp.25, 31, 40, chart p.43.) | [O054](market-structure-shift.md) · [O055](fvg-body-gaps.md) · [O139](structural-risk.md) · [O150](order-lifecycle.md). MSS/FVG geometry, linked decisions, structural invalidation and lifecycle checks are implemented. The November 2025 sweep-entry observation remains separate from subsequent annotations; exact fill time is unknown. |
| 5. Take opposing liquidity; manage the remaining position | Opposite box edge, intermediate 50%, TDO, prior/session extremes or NWOG as actually named. Take partials, move to breakeven once working, trail/leave the runner when appropriate, then stop the session. Size the quality of the setup; do not average down. ([GB] pp.25, 30–39.) | [O059](quality-grade.md) · [O140](position-sizing.md) · [O141](trade-objective.md) · [O142](position-management.md) · [O145](daily-loss-limit.md) · [O150](order-lifecycle.md). Entry-linked objectives, sizing, partials, stop changes, runners and session constraints are implemented. Historical actions remain unknown without actual source/order records. |

**Branches, not new products.**

- NYAM / completed hour / Asia failures use their own finished reference. A sweep during construction is part of the box.
- A prior-day/week/month reclaim can establish a bias for subsequent aligned pullbacks. Do not demand a fresh NYAM sweep for a separately cited prior-level trade.
- The golden pocket is `[L + 0.50(H-L), L + 0.618(H-L)]` for the illustrated retracement of a down impulse; direction and measured impulse matter. The September 1 source combines it with an actual PDL sweep and five-minute failure ([GB] p.25). The July example combines a fib pullback and hourly-low reclaim ([GB] p.35).
- The 09:30 manipulation branch is the source's below-open/reclaim long with a retracement objective and stop at the lows ([GB] p.40). Its confirmation duration is not fully specified by that reply; do not silently impose all parameters from the PDL example.
- A+ requires a relevant sweep; “no sweep = not A+” is a necessary quality condition, not proof that every sweep is A+ or that no other trade is allowed ([GB] pp.21–23, 37–40). R-G11 attaches to grading this candidate, not an OR across unrelated boxes somewhere during the day.

**November 20, 2025 source correction.** The retained [case registry](/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json), case `GB-FAIL-2025-11-20`, separates the displayed MNQ sweep entry from the subsequent MSS/FVG annotation ([GB] pp.31, 43). The predicate below describes confirmed-reclaim variants; it must not be applied retrospectively as this case's entry prerequisite. The frozen `mss_fvg_refinement` research comparison remains separately named. An NQ comparison does not establish the displayed MNQ execution or its exact fill clock.

### Phase 1 predicate — `GB-FAIL`

`reference_px` is the swept boundary; `opposite_bound` is the other edge when the reference is a box. `box_return_ok` means the confirmation is back inside that finished box, or true for a single-level reclaim. `source_hold_confirmed` records the actual reclaim/hold observation when a five-minute rule was not stated. `tdo_required` is true only in the selected source variant.

```sql
reference_frozen AND bias_recorded AND risk_defined AND objective_fixed
AND reference_known_at <= sweep_at
AND context_at <= sweep_at AND sweep_at < confirm_at
AND confirm_at <= decision_at AND source_session_allowed
AND (
  (side = 'short' AND sweep_high > reference_px
                  AND confirm_close < reference_px)
  OR
  (side = 'long' AND sweep_low < reference_px
                 AND confirm_close > reference_px)
)
AND box_return_ok
AND CASE confirmation_mode
  WHEN 'five_minute_close' THEN complete_clock_five_minute_bar
  WHEN 'reclaim_and_hold' THEN source_hold_confirmed
  ELSE NULL
END
AND (NOT tdo_required OR source_tdo_close_confirmed)
AND (NOT pocket_required OR impulse_known_at <= touch_at
                            AND touch_in_measured_pocket)
AND (NOT retracement_entry OR confirm_at <= retest_at
                              AND retest_at <= decision_at)
```

Sequence citations: [GB] pp.21, 23, 25, 27, 30–35, 38–40. Outcome: the preselected opposing-liquidity objective after this entry, with source stop/management recorded separately. Examples that sweep and remain accepted outside fail this predicate. A 09:45 candidate using a final 09:00–10:00 box fails availability. A pocket touch without failure fails. Missing London bounds, prior-week/month data, or an unspecified reclaim detector leave the corresponding automatic check unknown.

## Implementation and empirical status — 2026-09-12

The [M02 contract](../FORMULAS.md#m02) and its 27 operand bindings are implemented and reviewed. [Method evaluation](/workspace/implementation/src/trading_research/research/method_pack/methods.py) and [causal assembly](/workspace/implementation/src/trading_research/research/method_pack/assembly.py) consume the selected object evidence. [Implementation acceptance](/workspace/implementation/reports/phase1-live/methods/COMPLETION_REPORT.md) and [repairs](/workspace/implementation/reports/phase1-live/methods/POST_IMPLEMENTATION_REPAIR.md) establish software completion; the source and data limits described below remain.

The frozen empirical v1 run has the following branch dispositions. Counts are **recorded comparison opportunities**, with separate branch denominators; jobs processed can still contain missing inputs. See [exact definitions](/workspace/implementation/reports/phase1-live/empirical/registry/CANDIDATE_RULES.md), [group results](/workspace/implementation/reports/phase1-live/empirical/RESULTS.md) and [calibration](/workspace/implementation/reports/phase1-live/empirical/calibration/CALIBRATION_REPORT.md).

| Branch | Frozen disposition | Recorded p / f / u | Jobs processed / eligible | Missing-input jobs |
|---|---|---:|---:|---:|
| `nyam_box` | `data_hole` | 99 / 123 / 1 | 161 / 161 | 2 |
| `previous_hour` | `completed_with_population_holes` | 487 / 631 / 6 | 161 / 161 | 0 |
| `asia_tdo_case` | `data_hole` | 3 / 114 / 0 | 161 / 161 | 95 |
| `prior_day_level` | `data_hole` | 33 / 75 / 1 | 161 / 161 | 54 |
| `prior_week_level` | `data_hole` | 12 / 46 / 0 | 161 / 161 | 69 |
| `prior_month_level` | `data_hole` | 5 / 6 / 0 | 161 / 161 | 138 |
| `cash_open_reclaim_case` | `measured` | 53 / 89 / 0 | 161 / 161 | 0 |
| `mss_fvg_refinement` | `data_hole` | 52 / 47 / 0 | 161 / 161 | 2 |

All declared jobs for these branches are accounted for; none remain pending. Zero recorded rows under missing scope do not mean a completed zero-opportunity population. The complete **source-method verdict remains unknown**; these counts establish neither author-selected trades nor fills, P&L or a pooled success rate. The [current status page](current-status.md) explains the sampled dates, evidence boundary and frozen-run reproduction.

## Objects used by this method

These pages define the observations, locations, execution branches and process records in the loop. A shared object does not transfer another author’s entry rule.

**Observation foundations.** [Evidence and data coverage](data-coverage.md) · [Touch, reject, hold and break measurements](touch-reject-hold-break-grid.md) · [Source clocks and availability](clock-grid-and-bars.md) · [Source execution bars](execution-bars.md).

**Regime and thesis context.** [Scheduled news and changing information](news-event-context.md).

**Price references and price-action confirmation.** [Green Bird's finished session references](session-fail-boxes.md) · [Sweep, failure and reclaim](sweep-reclaim.md) · [Prior day, week and month extremes](prior-day-week-month-levels.md) · [Green Bird's midnight true-day open](true-day-open.md) · [09:30 cash-open price](cash-open-reference.md) · [New-week opening gap](new-week-opening-gap.md) · [Measured 50–61.8% retracement](golden-pocket.md) · [Premium / discount within a selected range](premium-discount-50.md) · [Market-structure shift after failure](market-structure-shift.md) · [Fair-value gaps and higher-timeframe imbalances](fvg-body-gaps.md) · [Source setup quality and exposure](quality-grade.md).

**Auction and profile structure.** [Prior-session auction landmarks](prior-session-reference-levels.md) · [Remaining auction objectives](unfinished-business.md).

**Risk, objectives and process.** [Green Bird's directional read](directional-bias.md) · [Entry-side structural invalidation](structural-risk.md) · [Exposure fitted to source risk constraints](position-sizing.md) · [Objective selected before entry](trade-objective.md) · [Source-selected position management](position-management.md) · [Source account and session stop](daily-loss-limit.md).

**Research, execution-study and risk records.** [Observed order lifecycle](order-lifecycle.md).


Compiled from the cited raw evidence and [OPERATORS]. Existing formula IDs identify component attachments; their historical scores do not certify this whole method.

[GB]: </workspace/sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf>
[OPERATORS]: </workspace/planning/phase-1-live/OPERATORS.md>
