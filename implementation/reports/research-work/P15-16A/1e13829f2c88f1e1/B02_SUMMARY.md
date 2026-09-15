# B0.2 full-history summary

- Run id: `1e13829f2c88f1e1`
- Run root: `/workspace/implementation/reports/research-work/P15-16A/1e13829f2c88f1e1`
- Dates: 1742 (2020-01-01 .. 2026-09-03)
- Branches: 39
- Distinct job files: 66196
- Runner-declared jobs (39*1742): 67938
- KEANI B0.2: not_measured
- Census: `20def36e065c13d7`
- B0 source: run-1.0.1 jobs (via census 20def36e065c13d7; not rescanned)

Job files are jobs/<date>/<branch>.json.gz. KEANI-OPEN-ABOVE-VALUE:branch:source_long collides with GB-VWAP:branch:source_long; no KEANI job file exists. B0.2 is not measured for KEANI. The runner declared 39*1742=67938 jobs; distinct gzip files on disk are fewer by one branch.

| branch | dates | B0.2 ep | B0.2 pass | B0.2 fail | B0.2 unk | B0 ep | B0 pass | B0.1 ep | B0.1 pass | delta pass vs B0.1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `JJ-TBR:branch:judas_outbound` | 1742 | 818 | 818 | 0 | 0 | 1695 | 1528 | 1695 | 1528 | -710 |
| `JJ-TBR:branch:judas_reversal` | 1742 | 3758 | 3512 | 246 | 0 | 1397 | 133 | 1714 | 41 | 3471 |
| `JJ-TBR:branch:single_extended` | 1742 | 5802 | 2244 | 3363 | 195 | 706 | 9 | 568 | 8 | 2236 |
| `JJ-TBR:branch:single_purged` | 1742 | 2372 | 373 | 1944 | 55 | 706 | 25 | 568 | 21 | 352 |
| `JJ-TBR:branch:internal_rotation` | 1742 | 5802 | 3363 | 2244 | 195 | 1408 | 4 | 1132 | 3 | 3360 |
| `JJ-TBR:branch:extension_reaction` | 1742 | 1012 | 1012 | 0 | 0 | 2127 | 178 | 1221 | 149 | 863 |
| `JJ-TBR:branch:other_session` | 1742 | 6357 | 6357 | 0 | 0 | 13116 | 1730 | 13116 | 1730 | 4627 |
| `JJ-TBR:branch:timed_pzone_reversal` | 1742 | 11 | 11 | 0 | 0 | 2633 | 305 | 2633 | 305 | -294 |
| `GB-FAIL:branch:london_box` | 1742 | 1742 | 750 | 971 | 21 | None | None | 0 | 0 | 750 |
| `GB-FAIL:branch:asia_box` | 1742 | 1742 | 1415 | 307 | 20 | None | None | 0 | 0 | 1415 |
| `GB-FAIL:branch:asia_tdo_case` | 1742 | 1517 | 1040 | 446 | 31 | 2513 | 168 | 2513 | 442 | 598 |
| `GB-FAIL:branch:prior_day_level` | 1742 | 1919 | 1707 | 177 | 35 | 1645 | 532 | 1645 | 1258 | 449 |
| `GB-FAIL:branch:nyam_box` | 1742 | 7053 | 6308 | 745 | 0 | 2275 | 1063 | 2275 | 2048 | 4260 |
| `GB-FAIL:branch:previous_hour` | 1742 | 7295 | 6522 | 773 | 0 | 11705 | 5353 | 11705 | 9035 | -2513 |
| `GB-FAIL:branch:nwog` | 1742 | 3166 | 2603 | 460 | 103 | None | None | 0 | 0 | 2603 |
| `GB-FAIL:branch:cash_open_reclaim_case` | 1742 | 1739 | 0 | 1681 | 58 | 1594 | 156 | 1594 | 721 | -721 |
| `GB-FAIL:branch:golden_pocket` | 1742 | 824 | 746 | 78 | 0 | None | None | 0 | 0 | 746 |
| `GB-VWAP:branch:source_long` | 1742 | 1742 | 772 | 949 | 21 | 1127 | 499 | 1127 | 499 | 273 |
| `GB-SCALP:branch:golden_pocket_continuation` | 1742 | 1679 | 1388 | 291 | 0 | None | None | 0 | 0 | 1388 |
| `SIRES:branch:dom_rejection` | 1742 | 3440 | 0 | 0 | 3440 | 2523 | 339 | 2523 | 339 | -339 |
| `SIRES:branch:absorption_reward_retest` | 1742 | 3440 | 0 | 0 | 3440 | 2523 | 7 | 2523 | 7 | -7 |
| `SIRES:branch:stop_four_stage` | 1742 | 3440 | 0 | 0 | 3440 | 2523 | 14 | 2523 | 14 | -14 |
| `SIRES:branch:footprint_confirmed_reaction` | 1742 | 3440 | 0 | 0 | 3440 | 2523 | 4 | 2523 | 4 | -4 |
| `SIRES:branch:vwap_deviation_fade` | 1742 | 3440 | 0 | 0 | 3440 | 2758 | 153 | 2758 | 153 | -153 |
| `SIRES:branch:ofm_aggressive` | 1742 | 3440 | 0 | 0 | 3440 | 2523 | 0 | 2523 | 0 | 0 |
| `SIRES:branch:ofm_passive` | 1742 | 3440 | 0 | 0 | 3440 | 1253 | 0 | 1253 | 0 | 0 |
| `SIRES:branch:clean_squeeze` | 1742 | 3440 | 0 | 3440 | 0 | 2523 | 1 | 2523 | 1 | -1 |
| `SIRES:branch:balance_failure_fade` | 1742 | 6880 | 0 | 0 | 6880 | 2523 | 2 | 2523 | 2 | -2 |
| `SIRES:branch:defended_band_continuation` | 1742 | 3440 | 0 | 0 | 3440 | 701 | 57 | 701 | 57 | -57 |
| `SIRES:branch:kg1_retest` | 1742 | 3440 | 0 | 0 | 3440 | 1758 | 475 | 1758 | 475 | -475 |
| `SIRES:branch:microbalance_break` | 1742 | 3440 | 0 | 0 | 3440 | 4069 | 1486 | 4069 | 1355 | -1355 |
| `SAINT-AMT:branch:continuation_retest` | 1742 | 3336 | 211 | 855 | 2270 | 2470 | 26 | 2470 | 0 | 211 |
| `SAINT-AMT:branch:trapped_buyers_retest` | 1742 | 3336 | 365 | 666 | 2305 | 1230 | 9 | 1230 | 0 | 365 |
| `SAINT-AMT:branch:failed_auction_return` | 1742 | 3197 | 1547 | 1650 | 0 | 2790 | 471 | 2790 | 0 | 1547 |
| `SAINT-AMT:branch:poc_traversal` | 1742 | 1715 | 1020 | 695 | 0 | 2790 | 279 | 2790 | 0 | 1020 |
| `MEMBER-TWO-REASONS:branch:resistance_short` | 1742 | 1742 | 1377 | 365 | 0 | 716 | 112 | 716 | 112 | 1265 |
| `MEMBER-TWO-REASONS:branch:planned_return_long` | 1742 | 1742 | 1366 | 376 | 0 | 634 | 240 | 634 | 240 | 1126 |
| `KEANI-OPEN-ABOVE-VALUE:branch:source_long` | not_measured | — | — | — | — | 1695 | 6 | 1695 | 39 | — |
| `REFILL-STUDY:branch:touch_record` | 1742 | 456448 | 425183 | 29204 | 2061 | 1666 | 1666 | 1666 | 1666 | 423517 |
