# FRED/ALFRED source capability check

**Subsequent work completed:** the [20-series macro backfill](/workspace/implementation/reports/phase1-live/macro-backfill/README.md) now contains 37,003 vintage records and individually verified initial CPI/payroll publication clocks. This page preserves the earlier bounded capability check; use the new bundles for acquired observations.

The supplied FRED credential successfully completed six bounded read-only queries. No credential is retained in the artifacts. Existing acquired data was not changed.

This check uses CPIAUCSL and PAYEMS as examples of provider capabilities, not as an inferred list of a method author's required inputs.

| Series | Initial-release observations for 2020 | Same periods as of 2021-12-31 | Vintage dates in 2020–2021 | Observations whose values differ |
|---|---:|---:|---:|---:|
| CPIAUCSL | 12 | 12 | 26 | 12 |
| PAYEMS | 12 | 12 | 25 | 12 |

For the January 2020 observation period, CPIAUCSL initially reported native value `258.820`, with vintage date February 13, 2020. The value in the December 31, 2021 snapshot is `258.687`. PAYEMS initially reported `152186`, with vintage date February 7, 2020; the December 31, 2021 snapshot contains `152234`. The observation period is the same, but the information available at each historical date differs.

[Query parameters, counts, comparisons and artifact hashes](/workspace/implementation/reports/phase1-live/macro-source-check/fred-x27n_6c9/manifest.json). Every response's declared count equals the retained row count; no pagination was omitted.

## What this closes

FRED/ALFRED can supply original observations and historical snapshots for these series. The API supports initial-release-only, all-vintage and new/revised-observation output modes. These can fill a missing-vintage acquisition gap for a selected macro input. See [FRED observation options](https://fred.stlouisfed.org/docs/api/fred/series_observations.html) and [vintage dates](https://fred.stlouisfed.org/docs/api/fred/series_vintagedates.html).

FRED real-time boundaries and vintage keys are dates. They do not alone distinguish information available before an 08:30 release from information available afterward on the same date. See [FRED real-time periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html).

The corresponding publisher archives demonstrate that clock evidence is obtainable separately:

- The [January 2020 CPI release](https://www.bls.gov/news.release/archives/cpi_02132020.htm) gives February 13, 2020 at 08:30 EST as its embargo endpoint.
- The [January 2020 Employment Situation release](https://www.bls.gov/news.release/archives/empsit_02072020.htm) gives February 7, 2020 at 08:30 EST. That page also notes a later reissue; the check uses the header for its original clock, not the reissued body as an original-value archive.

These are official publication clocks, not observed arrival times at a trading feed. A historical rule using publication time as availability must retain that assumption, as FORMULAS O162 specifies. No blanket 08:30 clock or fixed release lag was assigned to other events.

## Scope

The active study is NQ from 2020 onward. ES trades/OHLCV support selected peer context; ES quote data is required only by an explicit ES liquidity rule. Pre-2020 RTY gaps are outside scope. Macro inputs are required only by branches that consume them. See the [active data scope](/workspace/planning/phase-1-live/DATA_SCOPE.md).

This original check established access and revision handling for two example series. The subsequent linked acquisition backfilled the identifiable 20-series collection. Missing author-specific transforms, C-score definitions or decision thresholds remain procedure gaps that a provider API cannot supply.
