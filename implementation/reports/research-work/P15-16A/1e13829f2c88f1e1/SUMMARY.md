# Adapter-population full-history summary

- Run id: `1e13829f2c88f1e1`
- Dates: 1742 (2020-01-01 .. 2026-09-03)
- Branches: 39
- Jobs: 67938
- Workers requested: 12; cgroup default 17; achieved concurrency 1
- Orchestrator wall seconds: 66.0996
- Census run: `20def36e065c13d7`

| branch | dates | episodes | pass | fail | unknown | census B0.1 ep | census B0.1 pass | census B0.1 fail | census B0.1 unknown | delta pass | delta fail | delta unknown | wall s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `JJ-TBR:branch:judas_outbound` | 1742 | 818 | 818 | 0 | 0 | 1695 | 1528 | 148 | 19 | -710 | -148 | -19 | 1575.4 |
| `JJ-TBR:branch:judas_reversal` | 1742 | 3758 | 3512 | 246 | 0 | 1714 | 41 | 1671 | 2 | 3471 | -1425 | -2 | 3992.8 |
| `JJ-TBR:branch:single_extended` | 1742 | 5802 | 2244 | 3363 | 195 | 568 | 8 | 560 | 0 | 2236 | 2803 | 195 | 917.8 |
| `JJ-TBR:branch:single_purged` | 1742 | 2372 | 373 | 1944 | 55 | 568 | 21 | 546 | 1 | 352 | 1398 | 54 | 163.3 |
| `JJ-TBR:branch:internal_rotation` | 1742 | 5802 | 3363 | 2244 | 195 | 1132 | 3 | 1128 | 1 | 3360 | 1116 | 194 | 1299.0 |
| `JJ-TBR:branch:extension_reaction` | 1742 | 1012 | 1012 | 0 | 0 | 1221 | 149 | 1069 | 3 | 863 | -1069 | -3 | 553.9 |
| `JJ-TBR:branch:other_session` | 1742 | 6357 | 6357 | 0 | 0 | 13116 | 1730 | 11371 | 15 | 4627 | -11371 | -15 | 2423.3 |
| `JJ-TBR:branch:timed_pzone_reversal` | 1742 | 11 | 11 | 0 | 0 | 2633 | 305 | 2310 | 18 | -294 | -2310 | -18 | 68.9 |
| `GB-FAIL:branch:london_box` | 1742 | 1742 | 750 | 971 | 21 | 0 | 0 | 0 | 0 | 750 | 971 | 21 | 411.6 |
| `GB-FAIL:branch:asia_box` | 1742 | 1742 | 1415 | 307 | 20 | 0 | 0 | 0 | 0 | 1415 | 307 | 20 | 718.9 |
| `GB-FAIL:branch:asia_tdo_case` | 1742 | 1517 | 1040 | 446 | 31 | 2513 | 442 | 2062 | 9 | 598 | -1616 | 22 | 477.1 |
| `GB-FAIL:branch:prior_day_level` | 1742 | 1919 | 1707 | 177 | 35 | 1645 | 1258 | 387 | 0 | 449 | -210 | 35 | 855.1 |
| `GB-FAIL:branch:nyam_box` | 1742 | 7053 | 6308 | 745 | 0 | 2275 | 2048 | 227 | 0 | 4260 | 518 | 0 | 2535.0 |
| `GB-FAIL:branch:previous_hour` | 1742 | 7295 | 6522 | 773 | 0 | 11705 | 9035 | 2668 | 2 | -2513 | -1895 | -2 | 1762.7 |
| `GB-FAIL:branch:nwog` | 1742 | 3166 | 2603 | 460 | 103 | 0 | 0 | 0 | 0 | 2603 | 460 | 103 | 1227.1 |
| `GB-FAIL:branch:cash_open_reclaim_case` | 1742 | 1739 | 0 | 1681 | 58 | 1594 | 721 | 872 | 1 | -721 | 809 | 57 | 52.7 |
| `GB-FAIL:branch:golden_pocket` | 1742 | 824 | 746 | 78 | 0 | 0 | 0 | 0 | 0 | 746 | 78 | 0 | 389.9 |
| `GB-VWAP:branch:source_long` | 1742 | 1742 | 772 | 949 | 21 | 1127 | 499 | 0 | 628 | 273 | 949 | -607 | 3351.0 |
| `GB-SCALP:branch:golden_pocket_continuation` | 1742 | 1679 | 1388 | 291 | 0 | 0 | 0 | 0 | 0 | 1388 | 291 | 0 | 334.6 |
| `SIRES:branch:dom_rejection` | 1742 | 3440 | 0 | 0 | 3440 | 2523 | 339 | 2175 | 9 | -339 | -2175 | 3431 | 1490.7 |
| `SIRES:branch:absorption_reward_retest` | 1742 | 3440 | 0 | 0 | 3440 | 2523 | 7 | 2514 | 2 | -7 | -2514 | 3438 | 1492.2 |
| `SIRES:branch:stop_four_stage` | 1742 | 3440 | 0 | 0 | 3440 | 2523 | 14 | 2507 | 2 | -14 | -2507 | 3438 | 1491.1 |
| `SIRES:branch:footprint_confirmed_reaction` | 1742 | 3440 | 0 | 0 | 3440 | 2523 | 4 | 2519 | 0 | -4 | -2519 | 3440 | 1486.7 |
| `SIRES:branch:vwap_deviation_fade` | 1742 | 3440 | 0 | 0 | 3440 | 2758 | 153 | 2604 | 1 | -153 | -2604 | 3439 | 1489.2 |
| `SIRES:branch:ofm_aggressive` | 1742 | 3440 | 0 | 0 | 3440 | 2523 | 0 | 2520 | 3 | 0 | -2520 | 3437 | 1486.4 |
| `SIRES:branch:ofm_passive` | 1742 | 3440 | 0 | 0 | 3440 | 1253 | 0 | 1249 | 4 | 0 | -1249 | 3436 | 1486.8 |
| `SIRES:branch:clean_squeeze` | 1742 | 3440 | 0 | 3440 | 0 | 2523 | 1 | 2512 | 10 | -1 | 928 | -10 | 1486.5 |
| `SIRES:branch:balance_failure_fade` | 1742 | 6880 | 0 | 0 | 6880 | 2523 | 2 | 2507 | 14 | -2 | -2507 | 6866 | 1586.1 |
| `SIRES:branch:defended_band_continuation` | 1742 | 3440 | 0 | 0 | 3440 | 701 | 57 | 641 | 3 | -57 | -641 | 3437 | 1491.0 |
| `SIRES:branch:kg1_retest` | 1742 | 3440 | 0 | 0 | 3440 | 1758 | 475 | 1283 | 0 | -475 | -1283 | 3440 | 1486.8 |
| `SIRES:branch:microbalance_break` | 1742 | 3440 | 0 | 0 | 3440 | 4069 | 1355 | 2713 | 1 | -1355 | -2713 | 3439 | 1485.3 |
| `SAINT-AMT:branch:continuation_retest` | 1742 | 3336 | 211 | 855 | 2270 | 2470 | 0 | 2431 | 39 | 211 | -1576 | 2231 | 153.3 |
| `SAINT-AMT:branch:trapped_buyers_retest` | 1742 | 3336 | 365 | 666 | 2305 | 1230 | 0 | 1215 | 15 | 365 | -549 | 2290 | 120.1 |
| `SAINT-AMT:branch:failed_auction_return` | 1742 | 3197 | 1547 | 1650 | 0 | 2790 | 0 | 2251 | 539 | 1547 | -601 | -539 | 240.5 |
| `SAINT-AMT:branch:poc_traversal` | 1742 | 1715 | 1020 | 695 | 0 | 2790 | 0 | 2411 | 379 | 1020 | -1716 | -379 | 98.8 |
| `MEMBER-TWO-REASONS:branch:resistance_short` | 1742 | 1742 | 1377 | 365 | 0 | 716 | 112 | 603 | 1 | 1265 | -238 | -1 | 4471.2 |
| `MEMBER-TWO-REASONS:branch:planned_return_long` | 1742 | 1742 | 1366 | 376 | 0 | 634 | 240 | 394 | 0 | 1126 | -18 | 0 | 393.9 |
| `KEANI-OPEN-ABOVE-VALUE:branch:source_long` | 1742 | 1742 | 772 | 949 | 21 | 1695 | 39 | 1630 | 26 | 733 | -681 | -5 | 3351.0 |
| `REFILL-STUDY:branch:touch_record` | 1742 | 456448 | 425183 | 29204 | 2061 | 1666 | 1666 | 0 | 0 | 423517 | 29204 | 2061 | 11413.1 |

## SAINT stages

| branch | arrival false | arrival none | alignment false | alignment none | profile false | profile none |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `SAINT-AMT:branch:continuation_retest` | 0 | 3336 | 0 | 2757 | 49 | 0 |
| `SAINT-AMT:branch:trapped_buyers_retest` | 0 | 3336 | 0 | 2757 | 49 | 0 |
| `SAINT-AMT:branch:failed_auction_return` | 0 | 3197 | 0 | 3197 | 0 | 3197 |
| `SAINT-AMT:branch:poc_traversal` | 0 | 1715 | 0 | 1715 | 0 | 1715 |

## GB-VWAP unknowns resolved

GB-VWAP source_long resolved 0 census unknowns to pass and 0 to fail (census B0.1 unknown total 628).
