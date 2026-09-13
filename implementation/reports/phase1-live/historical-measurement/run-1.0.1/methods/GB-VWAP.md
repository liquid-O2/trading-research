# GB-VWAP — full acquired Phase 1 measurement

Implementation: accepted reconstructed setup rules, including disclosed inferred models. Historical session search: every frozen date through the owned NQ input endpoint. Setup qualification is distinct from subsequent outcomes and from actual fills.

| Branch | Scope | Searched sessions | Complete eligible sessions | Observed setups | Complete zero-setup sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- | --- |
| source_long | entry_setup | 1742 | 1666 | 499 | 1174 | 64 |

Eligible denominators require complete observed inputs for the branch and no active input limitation. Setups observed in limited sessions remain in the observed population and are excluded from the complete-session frequency numerator. Context, supplemental, personal and collection units do not enter entry-setup denominators.

Outcome tables describe all qualifying observed setups, including those in input-limited sessions. Complete future coverage is a separate requirement for excursion means; the per-setup record retains the input-eligibility flag.

## source_long

Source: GB p.33 posts 2026329904690712970/2026386393820283204; both finished session highs → close above → later contemporaneous VWAP return → long risk/continuation observation.

Setups per complete eligible session: 0.295. Observed setups per searched session: 0.286.

Searched session labels: 2020-01-01 through 2026-09-03. First/last session with complete branch inputs: 2020-01-02 / 2026-09-02. Interior unavailable sessions are excluded individually; these endpoints do not assert continuous coverage.

| Year | Searched | Eligible | Setups | Setups in eligible sessions | Limited sessions |
| --- | --- | --- | --- | --- | --- |
| 2020 | 262 | 258 | 56 | 56 | 2 |
| 2021 | 261 | 249 | 73 | 71 | 11 |
| 2022 | 260 | 249 | 71 | 70 | 10 |
| 2023 | 260 | 249 | 91 | 90 | 9 |
| 2024 | 262 | 248 | 88 | 86 | 12 |
| 2025 | 261 | 247 | 75 | 74 | 11 |
| 2026 | 176 | 166 | 45 | 45 | 9 |

| Horizon min | Complete futures | Incomplete futures | No price origin | Mean favorable points | Mean adverse points |
| --- | --- | --- | --- | --- | --- |
| 5 | 499 | 0 | 0 | 20.301 | 22.071 |
| 15 | 499 | 0 | 0 | 32.955 | 37.870 |
| 30 | 499 | 0 | 0 | 43.410 | 52.356 |
| 60 | 496 | 3 | 0 | 55.900 | 68.904 |

| Boundary outcome | n |
| --- | --- |
| expired_without_observed_boundary | 49 |
| invalidation_observed | 450 |

| Both objective and invalidation defined: ordering | n |
| --- | --- |

| Only one or neither boundary defined | n |
| --- | --- |
| expired_without_observed_boundary | 49 |
| invalidation_observed | 450 |

| Observed boundary classification | n | Mean seconds from decision | Median seconds |
| --- | --- | --- | --- |
| invalidation_observed | 450 | 206.478 | 25.889 |

A time attached to unresolved prior coverage is time to the observed batch only; it does not establish the population-first resolution time.

| Decision session | Observed setups | Eligible-session denominator | Setups per eligible session |
| --- | --- | --- | --- |
| NY_AM_0930_1200 | 478 | 1666 | 0.283 |
| NY_PM_1200_1600 | 21 | 1666 | 0.013 |

Clock-bin frequencies use the same complete branch-session denominator and count qualifying setups whose decision falls in that bin; they are not returns or independently selected cohorts.

| Decision session | Complete 60-min observations | Mean favorable points | Mean adverse points | Boundary classifications |
| --- | --- | --- | --- | --- |
| NY_AM_0930_1200 | 478 | 55.538 | 69.281 | expired_without_observed_boundary: 46; invalidation_observed: 432 |
| NY_PM_1200_1600 | 18 | 65.514 | 58.889 | expired_without_observed_boundary: 3; invalidation_observed: 18 |

The machine-readable decision-session results retain all four horizons, boundary-definition categories and resolution-time distributions.

| Exact limitation | Affected sessions |
| --- | --- |
| current input prefix has unknown intervals | 70 |
| earlier potential breakout close is unknown | 4 |
| session_reference_missing | 21 |

[Machine-readable results](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/MEASUREMENT_RESULTS.json) · [Coverage and exclusions](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/coverage-exclusions.jsonl.gz) · [Per-setup records](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/records/setup-records.jsonl.gz) · [Charts](/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1/charts/README.md).
