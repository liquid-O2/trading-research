# Adapter-population full-history summary

- Run id: `dd386316321ee58d`
- Dates: 1742 (2020-01-01 .. 2026-09-03)
- Branches: 9
- Jobs: 15678
- Workers requested: 12; cgroup default 17; achieved concurrency 12
- Orchestrator wall seconds: 4629.5089
- Census run: `20def36e065c13d7`

| branch | dates | episodes | pass | fail | unknown | census B0.1 ep | census B0.1 pass | census B0.1 fail | census B0.1 unknown | delta pass | delta fail | delta unknown | wall s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `GB-FAIL:branch:london_box` | 1742 | 2495 | 1995 | 500 | 0 | 0 | 0 | 0 | 0 | 1995 | 500 | 0 | 3687.5 |
| `GB-FAIL:branch:asia_box` | 1742 | 2513 | 1866 | 615 | 32 | 0 | 0 | 0 | 0 | 1866 | 615 | 32 | 1014.9 |
| `GB-FAIL:branch:overnight_scan` | 1742 | 12656 | 0 | 12656 | 0 | 0 | 0 | 0 | 0 | 0 | 12656 | 0 | 37168.9 |
| `GB-SCALP:branch:golden_pocket_continuation` | 1742 | 1722 | 1168 | 0 | 554 | 0 | 0 | 0 | 0 | 1168 | 0 | 554 | 594.2 |
| `SAINT-AMT:branch:continuation_retest` | 1742 | 2470 | 26 | 2432 | 12 | 2470 | 0 | 2431 | 39 | 26 | 1 | -27 | 1136.6 |
| `SAINT-AMT:branch:trapped_buyers_retest` | 1742 | 1230 | 9 | 1215 | 6 | 1230 | 0 | 1215 | 15 | 9 | 0 | -9 | 822.9 |
| `SAINT-AMT:branch:failed_auction_return` | 1742 | 2790 | 0 | 2255 | 535 | 2790 | 0 | 2251 | 539 | 0 | 4 | -4 | 818.8 |
| `SAINT-AMT:branch:poc_traversal` | 1742 | 2790 | 0 | 2417 | 373 | 2790 | 0 | 2411 | 379 | 0 | 6 | -6 | 784.9 |
| `GB-VWAP:branch:source_long` | 1742 | 1127 | 499 | 0 | 628 | 1127 | 499 | 0 | 628 | 0 | 0 | 0 | 4145.4 |

## SAINT stages

| branch | arrival false | arrival none | alignment false | alignment none | profile false | profile none |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `SAINT-AMT:branch:continuation_retest` | 0 | 500 | 1 | 0 | 23 | 0 |
| `SAINT-AMT:branch:trapped_buyers_retest` | 0 | 246 | 1 | 0 | 13 | 0 |
| `SAINT-AMT:branch:failed_auction_return` | 0 | 2790 | 0 | 2790 | 35 | 0 |
| `SAINT-AMT:branch:poc_traversal` | 0 | 2790 | 0 | 2790 | 35 | 0 |

## GB-VWAP unknowns resolved

GB-VWAP source_long resolved 0 census unknowns to pass and 0 to fail (census B0.1 unknown total 628).
