# Baseline repair B0.1 full-history summary

- B0: `B0` read from run-1.0.1 job files
- B0.1: `B0.1-2026-09-14` via `scan_branch_repaired`
- Run id: `20def36e065c13d7`
- Dates: 1742 (2020-01-01 .. 2026-09-03)
- Branches: 39
- Jobs: 67938
- Workers requested: 10; cgroup default 17; achieved concurrency 10
- Orchestrator wall seconds: 14390.4575

| branch | dates | ep B0 | ep B0.1 | pass B0 | pass B0.1 | fail B0 | fail B0.1 | unknown B0 | unknown B0.1 | no-setup B0 | no-setup B0.1 | data_unavailable B0 | data_unavailable B0.1 | verdict changed | directions | wall s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| `GB-VWAP:branch:source_long` | 1742 | 1127 | 1127 | 499 | 499 | 619 | 0 | 9 | 628 | 619 | 0 | 9 | 628 | 619 | fail->unknown:619 | 4701.8 |
| `GB-FAIL:branch:nyam_box` | 1742 | 2275 | 2275 | 1063 | 2048 | 1208 | 227 | 4 | 0 | 1208 | 227 | 4 | 0 | 985 | fail->pass:981, unknown->pass:4 | 2425.1 |
| `GB-FAIL:branch:previous_hour` | 1742 | 11705 | 11705 | 5353 | 9035 | 6333 | 2668 | 19 | 2 | 6333 | 2668 | 19 | 2 | 3688 | fail->pass:3671, unknown->fail:6, unknown->pass:11 | 4817.4 |
| `GB-FAIL:branch:asia_tdo_case` | 1742 | 2513 | 2513 | 168 | 442 | 2333 | 2062 | 12 | 9 | 2333 | 2062 | 12 | 9 | 286 | fail->pass:273, fail->unknown:5, unknown->fail:7, unknown->pass:1 | 446.2 |
| `GB-FAIL:branch:prior_day_level` | 1742 | 1645 | 1645 | 532 | 1258 | 1110 | 387 | 3 | 0 | 1110 | 387 | 3 | 0 | 726 | fail->pass:723, unknown->pass:3 | 1913.1 |
| `GB-FAIL:branch:prior_week_level` | 1742 | 1133 | 1133 | 219 | 561 | 903 | 557 | 11 | 15 | 903 | 557 | 11 | 15 | 353 | fail->pass:339, fail->unknown:9, unknown->fail:2, unknown->pass:3 | 6850.3 |
| `GB-FAIL:branch:prior_month_level` | 1742 | 972 | 972 | 96 | 258 | 854 | 674 | 22 | 40 | 854 | 674 | 22 | 40 | 185 | fail->pass:159, fail->unknown:22, unknown->fail:1, unknown->pass:3 | 26593.7 |
| `GB-FAIL:branch:cash_open_reclaim_case` | 1742 | 1594 | 1594 | 156 | 721 | 1431 | 872 | 7 | 1 | 1431 | 872 | 7 | 1 | 570 | fail->pass:562, fail->unknown:1, unknown->fail:4, unknown->pass:3 | 467.7 |
| `GB-FAIL:branch:mss_fvg_refinement` | 1742 | 1050 | 2023 | 49 | 89 | 1001 | 1933 | 0 | 1 | 1001 | 1933 | 0 | 1 | 0 | — | 123.6 |
| `SIRES:branch:dom_rejection` | 1742 | 2523 | 2523 | 339 | 339 | 2184 | 2175 | 0 | 9 | 2184 | 2175 | 0 | 9 | 9 | fail->unknown:9 | 5666.0 |
| `SIRES:branch:absorption_reward_retest` | 1742 | 2523 | 2523 | 7 | 7 | 2516 | 2514 | 0 | 2 | 2516 | 2514 | 0 | 2 | 2 | fail->unknown:2 | 4609.3 |
| `SIRES:branch:stop_four_stage` | 1742 | 2523 | 2523 | 14 | 14 | 2509 | 2507 | 0 | 2 | 2509 | 2507 | 0 | 2 | 2 | fail->unknown:2 | 4606.7 |
| `SIRES:branch:footprint_confirmed_reaction` | 1742 | 2523 | 2523 | 4 | 4 | 2519 | 2519 | 0 | 0 | 2519 | 2519 | 0 | 0 | 0 | — | 4638.1 |
| `SIRES:branch:vwap_deviation_fade` | 1742 | 2758 | 2758 | 153 | 153 | 2604 | 2604 | 1 | 1 | 2604 | 2604 | 1 | 1 | 0 | — | 15960.2 |
| `SIRES:branch:ofm_aggressive` | 1742 | 2523 | 2523 | 0 | 0 | 2523 | 2520 | 0 | 3 | 2523 | 2520 | 0 | 3 | 3 | fail->unknown:3 | 7775.2 |
| `SIRES:branch:ofm_passive` | 1742 | 1253 | 1253 | 0 | 0 | 1253 | 1249 | 0 | 4 | 1253 | 1249 | 0 | 4 | 4 | fail->unknown:4 | 2379.3 |
| `SIRES:branch:clean_squeeze` | 1742 | 2523 | 2523 | 1 | 1 | 2522 | 2512 | 0 | 10 | 2522 | 2512 | 0 | 10 | 10 | fail->unknown:10 | 4566.2 |
| `SIRES:branch:balance_failure_fade` | 1742 | 2523 | 2523 | 2 | 2 | 2516 | 2507 | 5 | 14 | 2516 | 2507 | 5 | 14 | 9 | fail->unknown:9 | 4585.5 |
| `SIRES:branch:defended_band_continuation` | 1742 | 701 | 701 | 57 | 57 | 644 | 641 | 0 | 3 | 644 | 641 | 0 | 3 | 3 | fail->unknown:3 | 5038.9 |
| `SIRES:branch:kg1_retest` | 1742 | 1758 | 1758 | 475 | 475 | 1283 | 1283 | 0 | 0 | 1283 | 1283 | 0 | 0 | 0 | — | 4601.5 |
| `MEMBER-TWO-REASONS:branch:resistance_short` | 1742 | 716 | 716 | 112 | 112 | 603 | 603 | 1 | 1 | 603 | 603 | 1 | 1 | 0 | — | 1690.3 |
| `MEMBER-TWO-REASONS:branch:planned_return_long` | 1742 | 634 | 634 | 240 | 240 | 394 | 394 | 0 | 0 | 394 | 394 | 0 | 0 | 0 | — | 1533.0 |
| `KEANI-OPEN-ABOVE-VALUE:branch:source_long` | 1742 | 1695 | 1695 | 6 | 39 | 1669 | 1630 | 20 | 26 | 1669 | 1630 | 20 | 26 | 50 | fail->pass:35, fail->unknown:9, pass->fail:3, unknown->fail:2, unknown->pass:1 | 2108.4 |
| `SAINT-AMT:branch:continuation_retest` | 1742 | 2470 | 2470 | 26 | 0 | 2444 | 2431 | 0 | 39 | 2444 | 2431 | 0 | 39 | 39 | fail->unknown:13, pass->unknown:26 | 355.3 |
| `SAINT-AMT:branch:trapped_buyers_retest` | 1742 | 1230 | 1230 | 9 | 0 | 1218 | 1215 | 3 | 15 | 1218 | 1215 | 3 | 15 | 12 | fail->unknown:3, pass->unknown:9 | 127.8 |
| `SAINT-AMT:branch:failed_auction_return` | 1742 | 2790 | 2790 | 471 | 0 | 2286 | 2251 | 33 | 539 | 2286 | 2251 | 33 | 539 | 506 | fail->unknown:35, pass->unknown:471 | 133.0 |
| `SAINT-AMT:branch:poc_traversal` | 1742 | 2790 | 2790 | 279 | 0 | 2511 | 2411 | 0 | 379 | 2511 | 2411 | 0 | 379 | 379 | fail->unknown:100, pass->unknown:279 | 115.2 |
| `JJ-TBR:branch:judas_reversal` | 1742 | 1397 | 1714 | 133 | 41 | 1258 | 1671 | 6 | 2 | 1258 | 1671 | 6 | 2 | 0 | — | 307.6 |
| `JJ-TBR:branch:single_extended` | 1742 | 706 | 568 | 9 | 8 | 697 | 560 | 0 | 0 | 697 | 560 | 0 | 0 | 0 | — | 189.4 |
| `JJ-TBR:branch:single_purged` | 1742 | 706 | 568 | 25 | 21 | 680 | 546 | 1 | 1 | 680 | 546 | 1 | 1 | 0 | — | 120.2 |
| `JJ-TBR:branch:internal_rotation` | 1742 | 1408 | 1132 | 4 | 3 | 1403 | 1128 | 1 | 1 | 1403 | 1128 | 1 | 1 | 0 | — | 118.6 |
| `JJ-TBR:branch:extension_reaction` | 1742 | 2127 | 1221 | 178 | 149 | 1946 | 1069 | 3 | 3 | 1946 | 1069 | 3 | 3 | 2 | pass->fail:2 | 300.9 |
| `JJ-TBR:branch:other_session` | 1742 | 13116 | 13116 | 1730 | 1730 | 11371 | 11371 | 15 | 15 | 11371 | 11371 | 15 | 15 | 0 | — | 2088.9 |
| `JJ-TBR:branch:timed_pzone_reversal` | 1742 | 2633 | 2633 | 305 | 305 | 2310 | 2310 | 18 | 18 | 2310 | 2310 | 18 | 18 | 0 | — | 7731.2 |
| `JJ-TBR:branch:judas_reversal_deferred` | 1742 | 0 | 1714 | 0 | 213 | 0 | 1496 | 0 | 5 | 0 | 1496 | 0 | 5 | 0 | — | 224.1 |
| `SIRES:branch:microbalance_break` | 1742 | 4069 | 4069 | 1486 | 1355 | 2583 | 2713 | 0 | 1 | 2583 | 2713 | 0 | 1 | 131 | pass->fail:130, pass->unknown:1 | 696.8 |
| `JJ-TBR:branch:judas_outbound` | 1742 | 1695 | 1695 | 1528 | 1528 | 148 | 148 | 19 | 19 | 148 | 148 | 19 | 19 | 0 | — | 990.8 |
| `REFILL-STUDY:branch:touch_record` | 1742 | 1666 | 1666 | 1666 | 1666 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 10692.0 |
| `STOIC-DATA:branch:macro_application` | 1742 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — | 1860.8 |
