# Adapter-population full-history summary

- Run id: `1019e6c09ee54609`
- Dates: 1742 (2020-01-01 .. 2026-09-03)
- Branches: 40
- Jobs: 69680
- Workers requested: 12; cgroup default 17; achieved concurrency 12
- Orchestrator wall seconds: 7413.0086
- Census run: `20def36e065c13d7`

| branch | dates | episodes | pass | fail | unknown | census B0.1 ep | census B0.1 pass | census B0.1 fail | census B0.1 unknown | delta pass | delta fail | delta unknown | wall s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `JJ-TBR:branch:judas_outbound` | 1742 | 818 | 100 | 717 | 1 | 1695 | 1528 | 148 | 19 | -1428 | 569 | -18 | 863.0 |
| `JJ-TBR:branch:judas_reversal` | 1742 | 3112 | 766 | 2326 | 20 | 1714 | 41 | 1671 | 2 | 725 | 655 | 18 | 2507.0 |
| `JJ-TBR:branch:single_extended` | 1742 | 1676 | 342 | 1321 | 13 | 568 | 8 | 560 | 0 | 334 | 761 | 13 | 409.6 |
| `JJ-TBR:branch:single_purged` | 1742 | 303 | 75 | 228 | 0 | 568 | 21 | 546 | 1 | 54 | -318 | -1 | 104.0 |
| `JJ-TBR:branch:internal_rotation` | 1742 | 1694 | 336 | 1354 | 4 | 1132 | 3 | 1128 | 1 | 333 | 226 | 3 | 389.1 |
| `JJ-TBR:branch:extension_reaction` | 1742 | 1012 | 139 | 841 | 32 | 1221 | 149 | 1069 | 3 | -10 | -228 | 29 | 169.1 |
| `JJ-TBR:branch:other_session` | 1742 | 13081 | 162 | 12918 | 1 | 13116 | 1730 | 11371 | 15 | -1568 | 1547 | -14 | 195.0 |
| `JJ-TBR:branch:timed_pzone_reversal` | 1742 | 11 | 11 | 0 | 0 | 2633 | 305 | 2310 | 18 | -294 | -2310 | -18 | 58.0 |
| `GB-FAIL:branch:london_box` | 1742 | 1742 | 849 | 872 | 21 | 0 | 0 | 0 | 0 | 849 | 872 | 21 | 664.1 |
| `GB-FAIL:branch:asia_box` | 1742 | 1742 | 946 | 776 | 20 | 0 | 0 | 0 | 0 | 946 | 776 | 20 | 603.2 |
| `GB-FAIL:branch:asia_tdo_case` | 1742 | 1742 | 642 | 1069 | 31 | 2513 | 442 | 2062 | 9 | 200 | -993 | 22 | 342.3 |
| `GB-FAIL:branch:prior_day_level` | 1742 | 3449 | 971 | 2443 | 35 | 1645 | 1258 | 387 | 0 | -287 | 2056 | 35 | 552.7 |
| `GB-FAIL:branch:nyam_box` | 1742 | 4623 | 1243 | 3380 | 0 | 2275 | 2048 | 227 | 0 | -805 | 3153 | 0 | 636.2 |
| `GB-FAIL:branch:previous_hour` | 1742 | 6558 | 589 | 5969 | 0 | 11705 | 9035 | 2668 | 2 | -8446 | 3301 | -2 | 330.5 |
| `GB-FAIL:branch:nwog` | 1742 | 2046 | 144 | 1858 | 44 | 0 | 0 | 0 | 0 | 144 | 1858 | 44 | 101.7 |
| `GB-FAIL:branch:cash_open_reclaim_case` | 1742 | 1742 | 572 | 1112 | 58 | 1594 | 721 | 872 | 1 | -149 | 240 | 57 | 253.8 |
| `GB-FAIL:branch:golden_pocket` | 1742 | 1742 | 718 | 1024 | 0 | 0 | 0 | 0 | 0 | 718 | 1024 | 0 | 369.1 |
| `GB-FAIL:branch:ny_session_extreme` | 1742 | 3437 | 438 | 2952 | 47 | 0 | 0 | 0 | 0 | 438 | 2952 | 47 | 247.9 |
| `GB-VWAP:branch:source_long` | 1742 | 1742 | 244 | 1477 | 21 | 1127 | 499 | 0 | 628 | -255 | 1477 | -607 | 3144.3 |
| `GB-SCALP:branch:golden_pocket_continuation` | 1742 | 1741 | 466 | 1275 | 0 | 0 | 0 | 0 | 0 | 466 | 1275 | 0 | 210.5 |
| `SIRES:branch:dom_rejection` | 1742 | 24055 | 0 | 24055 | 0 | 2523 | 339 | 2175 | 9 | -339 | 21880 | -9 | 1754.6 |
| `SIRES:branch:absorption_reward_retest` | 1742 | 24055 | 34 | 24021 | 0 | 2523 | 7 | 2514 | 2 | 27 | 21507 | -2 | 1681.0 |
| `SIRES:branch:stop_four_stage` | 1742 | 24055 | 4003 | 20052 | 0 | 2523 | 14 | 2507 | 2 | 3989 | 17545 | -2 | 2092.0 |
| `SIRES:branch:footprint_confirmed_reaction` | 1742 | 24055 | 10 | 23373 | 672 | 2523 | 4 | 2519 | 0 | 6 | 20854 | 672 | 1626.4 |
| `SIRES:branch:vwap_deviation_fade` | 1742 | 24055 | 298 | 23354 | 403 | 2758 | 153 | 2604 | 1 | 145 | 20750 | 402 | 1648.6 |
| `SIRES:branch:ofm_aggressive` | 1742 | 26942 | 0 | 23442 | 3500 | 2523 | 0 | 2520 | 3 | 0 | 20922 | 3497 | 1714.0 |
| `SIRES:branch:ofm_passive` | 1742 | 24055 | 0 | 24055 | 0 | 1253 | 0 | 1249 | 4 | 0 | 22806 | -4 | 1626.3 |
| `SIRES:branch:clean_squeeze` | 1742 | 24055 | 205 | 23850 | 0 | 2523 | 1 | 2512 | 10 | 204 | 21338 | -10 | 1647.0 |
| `SIRES:branch:balance_failure_fade` | 1742 | 48110 | 0 | 45634 | 2476 | 2523 | 2 | 2507 | 14 | -2 | 43127 | 2462 | 2347.4 |
| `SIRES:branch:defended_band_continuation` | 1742 | 24055 | 3993 | 19934 | 128 | 701 | 57 | 641 | 3 | 3936 | 19293 | 125 | 1962.5 |
| `SIRES:branch:kg1_retest` | 1742 | 0 | 0 | 0 | 0 | 1758 | 475 | 1283 | 0 | -475 | -1283 | 0 | 110.6 |
| `SIRES:branch:microbalance_break` | 1742 | 1 | 0 | 1 | 0 | 4069 | 1355 | 2713 | 1 | -1355 | -2712 | -1 | 160.0 |
| `SAINT-AMT:branch:continuation_retest` | 1742 | 3319 | 92 | 3170 | 57 | 2470 | 0 | 2431 | 39 | 92 | 739 | 18 | 144.3 |
| `SAINT-AMT:branch:trapped_buyers_retest` | 1742 | 3319 | 110 | 3084 | 125 | 1230 | 0 | 1215 | 15 | 110 | 1869 | 110 | 107.8 |
| `SAINT-AMT:branch:failed_auction_return` | 1742 | 761 | 130 | 631 | 0 | 2790 | 0 | 2251 | 539 | 130 | -1620 | -539 | 244.5 |
| `SAINT-AMT:branch:poc_traversal` | 1742 | 1715 | 625 | 1090 | 0 | 2790 | 0 | 2411 | 379 | 625 | -1321 | -379 | 224.3 |
| `MEMBER-TWO-REASONS:branch:resistance_short` | 1742 | 1742 | 451 | 1291 | 0 | 716 | 112 | 603 | 1 | 339 | 688 | -1 | 4310.9 |
| `MEMBER-TWO-REASONS:branch:planned_return_long` | 1742 | 1742 | 473 | 1269 | 0 | 634 | 240 | 394 | 0 | 233 | 875 | 0 | 292.5 |
| `KEANI-OPEN-ABOVE-VALUE:branch:source_long` | 1742 | 1742 | 0 | 1695 | 47 | 1695 | 39 | 1630 | 26 | -39 | 65 | 21 | 25328.4 |
| `REFILL-STUDY:branch:touch_record` | 1742 | 795369 | 36254 | 759110 | 5 | 1666 | 1666 | 0 | 0 | 34588 | 759110 | 5 | 18743.1 |

## SAINT stages

| branch | arrival false | arrival none | alignment false | alignment none | profile false | profile none |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `SAINT-AMT:branch:continuation_retest` | 0 | 3319 | 0 | 0 | 48 | 0 |
| `SAINT-AMT:branch:trapped_buyers_retest` | 0 | 3319 | 0 | 0 | 48 | 0 |
| `SAINT-AMT:branch:failed_auction_return` | 0 | 761 | 0 | 761 | 0 | 761 |
| `SAINT-AMT:branch:poc_traversal` | 0 | 1715 | 0 | 1715 | 0 | 1715 |

## GB-VWAP unknowns resolved

GB-VWAP source_long resolved 0 census unknowns to pass and 0 to fail (census B0.1 unknown total 628).
