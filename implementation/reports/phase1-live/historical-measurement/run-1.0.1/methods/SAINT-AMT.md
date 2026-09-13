# SAINT-AMT — full acquired Phase 1 measurement

Implementation: accepted reconstructed setup rules, including disclosed inferred models. Historical session search: every frozen date through the owned NQ input endpoint. Setup qualification is distinct from subsequent outcomes and from actual fills.

| Branch | Scope | Searched sessions | Complete eligible sessions | Observed setups | Complete zero-setup sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- | --- |
| continuation_retest | entry_setup | 1742 | 1659 | 26 | 1635 | 71 |
| trapped_buyers_retest | entry_setup | 1742 | 1660 | 9 | 1651 | 70 |
| failed_auction_return | entry_setup | 1742 | 1611 | 471 | 1209 | 119 |
| poc_traversal | entry_setup | 1742 | 1623 | 279 | 1378 | 107 |

Eligible denominators require complete observed inputs for the branch and no active input limitation. Setups observed in limited sessions remain in the observed population and are excluded from the complete-session frequency numerator. Context, supplemental, personal and collection units do not enter entry-setup denominators.

Outcome tables describe all qualifying observed setups, including those in input-limited sessions. Complete future coverage is a separate requirement for excursion means; the per-setup record retains the input-eligibility flag.

## continuation_retest

Source: RTVP pp.3–11;WIC pp.7–10; fitted HTF accepted balance → actual LTF balance break → same-boundary retest → repeated directional aggression.

Setups per complete eligible session: 0.014. Observed setups per searched session: 0.015.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 255 | 8 | 7 | 5 |
| 2021 | 261 | 246 | 4 | 4 | 14 |
| 2022 | 260 | 249 | 4 | 3 | 10 |
| 2023 | 260 | 249 | 4 | 4 | 9 |
| 2024 | 262 | 247 | 2 | 2 | 13 |
| 2025 | 261 | 248 | 3 | 3 | 10 |
| 2026 | 176 | 165 | 1 | 1 | 10 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 26 | 0 | 0 | 15.933 | 11.394 |
| 15 | 26 | 0 | 0 | 25.846 | 21.029 |
| 30 | 26 | 0 | 0 | 34.760 | 25.212 |
| 60 | 26 | 0 | 0 | 44.144 | 36.519 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 8 |
| invalidation_observed | 5 |
| objective_observed | 13 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 8 |
| invalidation_observed | 5 |
| objective_observed | 13 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 5 | 1081.867 | 1194.315 |
| objective_observed | 13 | 302.387 | 95.640 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 18 | 1659 | 0.010 |
| NY_PM_1200_1600 | 8 | 1659 | 0.005 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 18 | 48.681 | 41.347 | expired_without_observed_boundary: 6; invalidation_observed: 3; objective_observed: 9 |
| NY_PM_1200_1600 | 8 | 33.938 | 25.656 | expired_without_observed_boundary: 2; invalidation_observed: 2; objective_observed: 4 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |
| earlier potential directional breakout close is unknown | 13 |

## trapped_buyers_retest

Source: TRAP pp.3–10;WIC pp.7–10; two distinct earlier upper buying failures → current LTF down break → same-boundary retest → repeated body selling.

Setups per complete eligible session: 0.005. Observed setups per searched session: 0.005.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 254 | 1 | 1 | 6 |
| 2021 | 261 | 247 | 2 | 2 | 13 |
| 2022 | 260 | 249 | 2 | 2 | 10 |
| 2023 | 260 | 249 | 2 | 2 | 9 |
| 2024 | 262 | 247 | 0 | 0 | 13 |
| 2025 | 261 | 248 | 1 | 1 | 10 |
| 2026 | 176 | 166 | 1 | 1 | 9 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 9 | 0 | 0 | 21.028 | 10.667 |
| 15 | 9 | 0 | 0 | 28.583 | 19.861 |
| 30 | 9 | 0 | 0 | 35.056 | 28.556 |
| 60 | 9 | 0 | 0 | 45.250 | 48.056 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 4 |
| invalidation_observed | 2 |
| objective_observed | 3 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 4 |
| invalidation_observed | 2 |
| objective_observed | 3 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 2 | 1443.085 | 1443.085 |
| objective_observed | 3 | 81.511 | 20.520 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 6 | 1660 | 0.004 |
| NY_PM_1200_1600 | 3 | 1660 | 0.002 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 6 | 55.042 | 52.958 | expired_without_observed_boundary: 2; invalidation_observed: 1; objective_observed: 3 |
| NY_PM_1200_1600 | 3 | 25.667 | 38.250 | expired_without_observed_boundary: 2; invalidation_observed: 1 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |
| earlier potential directional breakout close is unknown | 10 |

## failed_auction_return

Source: AMTL pp.8–10; original balance → distinct older value tested/rejected → original balance reacceptance → local control.

Setups per complete eligible session: 0.276. Observed setups per searched session: 0.270.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 247 | 67 | 66 | 13 |
| 2021 | 261 | 237 | 72 | 67 | 23 |
| 2022 | 260 | 238 | 68 | 66 | 21 |
| 2023 | 260 | 243 | 75 | 69 | 15 |
| 2024 | 262 | 240 | 76 | 69 | 20 |
| 2025 | 261 | 243 | 78 | 72 | 15 |
| 2026 | 176 | 163 | 35 | 35 | 12 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 470 | 1 | 0 | 18.172 | 19.388 |
| 15 | 469 | 2 | 0 | 32.022 | 31.975 |
| 30 | 469 | 2 | 0 | 47.205 | 42.558 |
| 60 | 464 | 7 | 0 | 61.345 | 56.357 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 22 |
| invalidation_observed | 155 |
| objective_observed | 294 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 22 |
| invalidation_observed | 155 |
| objective_observed | 294 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 155 | 606.801 | 373.001 |
| objective_observed | 294 | 432.811 | 176.409 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 433 | 1611 | 0.254 |
| NY_PM_1200_1600 | 38 | 1611 | 0.022 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 433 | 62.407 | 57.785 | expired_without_observed_boundary: 16; invalidation_observed: 147; objective_observed: 270 |
| NY_PM_1200_1600 | 31 | 46.508 | 36.411 | expired_without_observed_boundary: 6; invalidation_observed: 8; objective_observed: 24 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 9 |
| current input prefix has unknown intervals | 70 |
| no distinct older completed auction in current admitted prefix | 45 |

## poc_traversal

Source: RTVP pp.5–8;AMTL pp.8–11; original balance reacceptance → aggressive POC passage → source hold → far-edge objective.

Setups per complete eligible session: 0.162. Observed setups per searched session: 0.160.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 248 | 48 | 47 | 12 |
| 2021 | 261 | 238 | 29 | 27 | 22 |
| 2022 | 260 | 240 | 35 | 35 | 19 |
| 2023 | 260 | 244 | 49 | 45 | 14 |
| 2024 | 262 | 245 | 41 | 37 | 15 |
| 2025 | 261 | 245 | 42 | 39 | 13 |
| 2026 | 176 | 163 | 35 | 33 | 12 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 278 | 1 | 0 | 17.720 | 18.519 |
| 15 | 277 | 2 | 0 | 31.116 | 30.959 |
| 30 | 275 | 4 | 0 | 47.668 | 42.078 |
| 60 | 272 | 7 | 0 | 60.561 | 57.786 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 16 |
| invalidation_observed | 42 |
| objective_observed | 221 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |
| expired_without_observed_boundary | 16 |
| invalidation_observed | 42 |
| objective_observed | 221 |

| Only one or neither boundary defined | n |
| --- | --- |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 42 | 926.113 | 567.832 |
| objective_observed | 221 | 309.329 | 58.215 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 242 | 1623 | 0.142 |
| NY_PM_1200_1600 | 37 | 1623 | 0.020 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 242 | 64.595 | 60.180 | expired_without_observed_boundary: 8; invalidation_observed: 40; objective_observed: 194 |
| NY_PM_1200_1600 | 30 | 28.017 | 38.475 | expired_without_observed_boundary: 8; invalidation_observed: 2; objective_observed: 27 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| calendar_unverified | 9 |
| current input prefix has unknown intervals | 70 |
| no distinct older completed auction in current admitted prefix | 45 |

[Machine-readable results](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/MEASUREMENT_RESULTS.json) · [Coverage and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz) · [Per-setup records](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/setup-records.jsonl.gz) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md).
