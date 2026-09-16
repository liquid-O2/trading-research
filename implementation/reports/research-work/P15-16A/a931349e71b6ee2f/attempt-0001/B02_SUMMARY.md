# B0.2 full-history summary

- Run id: `1019e6c09ee54609`
- Run root: `/workspace/implementation/reports/research-work/P15-16A/1019e6c09ee54609`
- Dates: 1742 (2020-01-01 .. 2026-09-03)
- Branches: 40
- Distinct job files: 69680
- Runner-declared jobs: 69680
- KEANI B0.2: measured
- Census: `20def36e065c13d7`
- B0 source: run-1.0.1 jobs (via census 20def36e065c13d7; not rescanned)
- Branches over all roots: 41
- Job files over all roots: 76648

The previous B0.2 run root 1e13829f2c88f1e1 is superseded: jobs were named jobs/<date>/<branch>.json.gz so KEANI-OPEN-ABOVE-VALUE:branch:source_long collided with GB-VWAP:branch:source_long. Distinct gzip files on that root: 66196. This run uses coverage_id--json.gz job paths and KEANI is measured. The corrected full-history root carries 40 branches over 1742 dates (69680 job files), and the supplemental root adds 4 branches over the same 1742 dates (6968 job files), so the job files over both roots number 76648 across 41 distinct coverage ids.

## Supplemental run `823273eba4b9ec50`

- Run root: `/workspace/implementation/reports/research-work/P15-16A/823273eba4b9ec50`
- MANIFEST sha256: `823273eba4b9ec5039725ebca1a864259e9279525932c0266c965f200c763746`
- Dates: 1742 | branches: 4 | job files: 6968
- Branches: GB-FAIL:branch:prior_week_level, GB-FAIL:branch:asia_box, GB-FAIL:branch:prior_day_level, JJ-TBR:branch:internal_rotation
- Failed dates: 0
- Reason: prior_week_level was added to B0.2 after the main run (followup-5 GAP 1); asia_box and prior_day_level were re-scanned because the tdo_retest confirmation variant (followup-5 GAP 2) changes their recorded confirmation mode; JJ-TBR internal_rotation was re-scanned because its location stage read the deleted range constant TAPE_LAST (2026-08-19) and now reads the shared frozen-list guard, which moves the boundary to 2026-09-03. Every other branch's job files were produced by scan bytes that are unchanged, and no job file of the main run was changed.

| branch | dates | B0.2 ep | B0.2 pass | B0.2 fail | B0.2 unk | B0 ep | B0 pass | B0.1 ep | B0.1 pass | delta pass vs B0.1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `JJ-TBR:branch:judas_outbound` | 1742 | 818 | 100 | 717 | 1 | 1695 | 1528 | 1695 | 1528 | -1428 |
| `JJ-TBR:branch:judas_reversal` | 1742 | 3112 | 766 | 2326 | 20 | 1397 | 133 | 1714 | 41 | 725 |
| `JJ-TBR:branch:single_extended` | 1742 | 1676 | 342 | 1321 | 13 | 706 | 9 | 568 | 8 | 334 |
| `JJ-TBR:branch:single_purged` | 1742 | 303 | 75 | 228 | 0 | 706 | 25 | 568 | 21 | 54 |
| `JJ-TBR:branch:internal_rotation` | 1742 | 1704 | 339 | 1361 | 4 | 1408 | 4 | 1132 | 3 | 336 |
| `JJ-TBR:branch:extension_reaction` | 1742 | 1012 | 139 | 841 | 32 | 2127 | 178 | 1221 | 149 | -10 |
| `JJ-TBR:branch:other_session` | 1742 | 13081 | 162 | 12918 | 1 | 13116 | 1730 | 13116 | 1730 | -1568 |
| `JJ-TBR:branch:timed_pzone_reversal` | 1742 | 11 | 11 | 0 | 0 | 2633 | 305 | 2633 | 305 | -294 |
| `GB-FAIL:branch:london_box` | 1742 | 1742 | 849 | 872 | 21 | None | None | 0 | 0 | 849 |
| `GB-FAIL:branch:asia_box` | 1742 | 1742 | 946 | 776 | 20 | None | None | 0 | 0 | 946 |
| `GB-FAIL:branch:asia_tdo_case` | 1742 | 1742 | 642 | 1069 | 31 | 2513 | 168 | 2513 | 442 | 200 |
| `GB-FAIL:branch:prior_day_level` | 1742 | 3449 | 971 | 2443 | 35 | 1645 | 532 | 1645 | 1258 | -287 |
| `GB-FAIL:branch:nyam_box` | 1742 | 4623 | 1243 | 3380 | 0 | 2275 | 1063 | 2275 | 2048 | -805 |
| `GB-FAIL:branch:previous_hour` | 1742 | 6558 | 589 | 5969 | 0 | 11705 | 5353 | 11705 | 9035 | -8446 |
| `GB-FAIL:branch:nwog` | 1742 | 2046 | 144 | 1858 | 44 | None | None | 0 | 0 | 144 |
| `GB-FAIL:branch:cash_open_reclaim_case` | 1742 | 1742 | 572 | 1112 | 58 | 1594 | 156 | 1594 | 721 | -149 |
| `GB-FAIL:branch:golden_pocket` | 1742 | 1742 | 718 | 1024 | 0 | None | None | 0 | 0 | 718 |
| `GB-FAIL:branch:ny_session_extreme` | 1742 | 3437 | 438 | 2952 | 47 | None | None | 0 | 0 | 438 |
| `GB-VWAP:branch:source_long` | 1742 | 1742 | 244 | 1477 | 21 | 1127 | 499 | 1127 | 499 | -255 |
| `GB-SCALP:branch:golden_pocket_continuation` | 1742 | 1741 | 466 | 1275 | 0 | None | None | 0 | 0 | 466 |
| `SIRES:branch:dom_rejection` | 1742 | 24055 | 0 | 24055 | 0 | 2523 | 339 | 2523 | 339 | -339 |
| `SIRES:branch:absorption_reward_retest` | 1742 | 24055 | 34 | 24021 | 0 | 2523 | 7 | 2523 | 7 | 27 |
| `SIRES:branch:stop_four_stage` | 1742 | 24055 | 4003 | 20052 | 0 | 2523 | 14 | 2523 | 14 | 3989 |
| `SIRES:branch:footprint_confirmed_reaction` | 1742 | 24055 | 10 | 23373 | 672 | 2523 | 4 | 2523 | 4 | 6 |
| `SIRES:branch:vwap_deviation_fade` | 1742 | 24055 | 298 | 23354 | 403 | 2758 | 153 | 2758 | 153 | 145 |
| `SIRES:branch:ofm_aggressive` | 1742 | 26942 | 0 | 23442 | 3500 | 2523 | 0 | 2523 | 0 | 0 |
| `SIRES:branch:ofm_passive` | 1742 | 24055 | 0 | 24055 | 0 | 1253 | 0 | 1253 | 0 | 0 |
| `SIRES:branch:clean_squeeze` | 1742 | 24055 | 205 | 23850 | 0 | 2523 | 1 | 2523 | 1 | 204 |
| `SIRES:branch:balance_failure_fade` | 1742 | 48110 | 0 | 45634 | 2476 | 2523 | 2 | 2523 | 2 | -2 |
| `SIRES:branch:defended_band_continuation` | 1742 | 24055 | 3993 | 19934 | 128 | 701 | 57 | 701 | 57 | 3936 |
| `SIRES:branch:kg1_retest` | 1742 | 0 | 0 | 0 | 0 | 1758 | 475 | 1758 | 475 | -475 |
| `SIRES:branch:microbalance_break` | 1742 | 1 | 0 | 1 | 0 | 4069 | 1486 | 4069 | 1355 | -1355 |
| `SAINT-AMT:branch:continuation_retest` | 1742 | 3319 | 92 | 3170 | 57 | 2470 | 26 | 2470 | 0 | 92 |
| `SAINT-AMT:branch:trapped_buyers_retest` | 1742 | 3319 | 110 | 3084 | 125 | 1230 | 9 | 1230 | 0 | 110 |
| `SAINT-AMT:branch:failed_auction_return` | 1742 | 761 | 130 | 631 | 0 | 2790 | 471 | 2790 | 0 | 130 |
| `SAINT-AMT:branch:poc_traversal` | 1742 | 1715 | 625 | 1090 | 0 | 2790 | 279 | 2790 | 0 | 625 |
| `MEMBER-TWO-REASONS:branch:resistance_short` | 1742 | 1742 | 451 | 1291 | 0 | 716 | 112 | 716 | 112 | 339 |
| `MEMBER-TWO-REASONS:branch:planned_return_long` | 1742 | 1742 | 473 | 1269 | 0 | 634 | 240 | 634 | 240 | 233 |
| `KEANI-OPEN-ABOVE-VALUE:branch:source_long` | 1742 | 1742 | 0 | 1695 | 47 | 1695 | 6 | 1695 | 39 | -39 |
| `REFILL-STUDY:branch:touch_record` | 1742 | 795369 | 36254 | 759110 | 5 | 1666 | 1666 | 1666 | 1666 | 34588 |
| `GB-FAIL:branch:prior_week_level` | 1742 | 3484 | 400 | 3084 | 0 | 1133 | 219 | 1133 | 561 | -161 |

## Per-branch funnel, entry time, and plausibility

### `JJ-TBR:branch:judas_outbound`

- episodes per session: 0.4695752009184845
- pass rate: 0.12224938875305623
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0, 0.7]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 818 | 100 | 717 | 1 | ob_2m=1, ob_3m=1, ob_5m=1, rejection_block=1 |
| context | 818 | 818 | 0 | 0 |  |
| objective | 100 | 100 | 0 | 0 |  |
| reference | 818 | 818 | 0 | 0 |  |
| risk | 100 | 100 | 0 | 0 |  |
| trigger | 818 | 818 | 0 | 0 |  |

30-minute ET entry buckets: 09:30=818

### `JJ-TBR:branch:judas_reversal`

- episodes per session: 1.7864523536165327
- pass rate: 0.2461439588688946
- bound episodes_per_session: [0, 4]
- bound pass_rate: [0, 0.9]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 3112 | 766 | 2326 | 20 | ob_2m=20, ob_3m=20, ob_5m=20, rejection_block=20 |
| context | 3003 | 3003 | 0 | 0 |  |
| location | 3112 | 3112 | 0 | 0 |  |
| objective | 766 | 766 | 0 | 0 |  |
| reference | 3112 | 3112 | 0 | 0 |  |
| risk | 766 | 766 | 0 | 0 |  |
| trigger | 3112 | 3112 | 0 | 0 |  |

30-minute ET entry buckets: 09:00=703, 09:30=2214, 10:00=158, 10:30=36, 11:00=1

### `JJ-TBR:branch:single_extended`

- episodes per session: 0.9621125143513203
- pass rate: 0.20405727923627684
- bound episodes_per_session: [0, 6]
- bound pass_rate: [0, 0.5]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1676 | 342 | 1321 | 13 | ob_2m=13, ob_3m=13, ob_5m=13, rejection_block=13 |
| context | 1676 | 1676 | 0 | 0 |  |
| location | 1676 | 1676 | 0 | 0 |  |
| objective | 342 | 342 | 0 | 0 |  |
| reference | 1676 | 1676 | 0 | 0 |  |
| risk | 342 | 342 | 0 | 0 |  |
| trigger | 1676 | 1676 | 0 | 0 |  |

30-minute ET entry buckets: 09:00=751, 09:30=619, 10:00=119, 10:30=55, 11:00=32, 11:30=17, 12:00=13, 12:30=11, 13:00=12, 13:30=5, 14:00=15, 14:30=7, 15:00=4, 15:30=14, 16:00=2

### `JJ-TBR:branch:single_purged`

- episodes per session: 0.17393800229621126
- pass rate: 0.24752475247524752
- bound episodes_per_session: [0, 6]
- bound pass_rate: [0, 0.5]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 303 | 75 | 228 | 0 |  |
| context | 303 | 303 | 0 | 0 |  |
| location | 303 | 303 | 0 | 0 |  |
| objective | 75 | 75 | 0 | 0 |  |
| reference | 303 | 303 | 0 | 0 |  |
| risk | 75 | 75 | 0 | 0 |  |
| trigger | 303 | 303 | 0 | 0 |  |

30-minute ET entry buckets: 09:30=303

### `JJ-TBR:branch:internal_rotation`

- episodes per session: 0.9781859931113662
- pass rate: 0.198943661971831
- bound episodes_per_session: [0, 8]
- bound pass_rate: [0, 0.4]
- in/out: in
- source run: `823273eba4b9ec50`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1704 | 347 | 1351 | 6 | ob_2m=6, ob_3m=6, ob_5m=6, rejection_block=6 |
| context | 1704 | 1704 | 0 | 0 |  |
| location | 1704 | 1704 | 0 | 0 |  |
| objective | 339 | 339 | 0 | 0 |  |
| reference | 1704 | 1704 | 0 | 0 |  |
| risk | 339 | 339 | 0 | 0 |  |
| trigger | 1704 | 1677 | 27 | 0 |  |

30-minute ET entry buckets: 09:00=824, 09:30=660, 10:00=98, 10:30=32, 11:00=20, 11:30=10, 12:00=12, 12:30=4, 13:00=14, 13:30=10, 14:00=4, 14:30=4, 15:00=8, 15:30=4

### `JJ-TBR:branch:extension_reaction`

- episodes per session: 0.5809414466130884
- pass rate: 0.1373517786561265
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0, 0.5]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1012 | 139 | 841 | 32 | ob_2m=32, ob_3m=32, ob_5m=32, rejection_block=32 |
| context | 1012 | 1012 | 0 | 0 |  |
| location | 1012 | 1012 | 0 | 0 |  |
| objective | 139 | 139 | 0 | 0 |  |
| reference | 1012 | 1012 | 0 | 0 |  |
| risk | 139 | 139 | 0 | 0 |  |
| trigger | 1012 | 1012 | 0 | 0 |  |

30-minute ET entry buckets: 10:00=346, 10:30=145, 11:00=86, 11:30=71, 12:00=58, 12:30=55, 13:00=34, 13:30=36, 14:00=44, 14:30=44, 15:00=38, 15:30=49, 16:00=6

### `JJ-TBR:branch:other_session`

- episodes per session: 7.50918484500574
- pass rate: 0.012384374283311673
- bound episodes_per_session: [0, 12]
- bound pass_rate: [0, 0.5]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 13081 | 252 | 12807 | 22 | ob_2m=22, ob_3m=22, ob_5m=22, rejection_block=22 |
| context | 13081 | 13081 | 0 | 0 |  |
| location | 13081 | 13081 | 0 | 0 |  |
| objective | 162 | 162 | 0 | 0 |  |
| reference | 13081 | 13081 | 0 | 0 |  |
| risk | 162 | 162 | 0 | 0 |  |
| trigger | 13081 | 9840 | 3241 | 0 |  |

30-minute ET entry buckets: 03:00=9177, 03:30=1489, 04:00=1168, 04:30=574, 05:00=394, 05:30=276, 06:00=3

### `JJ-TBR:branch:timed_pzone_reversal`

- episodes per session: 0.006314580941446613
- pass rate: 1.0
- bound episodes_per_session: [0, 6]
- bound pass_rate: None
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 11 | 11 | 0 | 0 |  |
| location | 11 | 11 | 0 | 0 |  |
| objective | 1 | 1 | 0 | 0 |  |
| reference | 11 | 11 | 0 | 0 |  |
| risk | 11 | 11 | 0 | 0 |  |
| trigger | 11 | 11 | 0 | 0 |  |

30-minute ET entry buckets: 09:00=1, 09:30=6, 10:00=4

### `GB-FAIL:branch:london_box`

- episodes per session: 1.0
- pass rate: 0.4873708381171068
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.55]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1264 | 849 | 415 | 0 |  |
| context | 1742 | 1742 | 0 | 0 |  |
| location | 1721 | 1264 | 457 | 0 |  |
| management | 849 | 849 | 0 | 0 |  |
| objective | 849 | 849 | 0 | 0 |  |
| reference | 1742 | 1721 | 0 | 21 |  |
| risk | 849 | 849 | 0 | 0 |  |
| trigger | 1264 | 1264 | 0 | 0 |  |

30-minute ET entry buckets: 04:30=43, 05:00=458, 05:30=14, 06:00=12, 06:30=8, 07:00=20, 07:30=8, 08:00=23, 08:30=36, 09:00=21, 09:30=773, 10:00=156, 10:30=87, 11:00=75, 11:30=8

### `GB-FAIL:branch:asia_box`

- episodes per session: 1.0
- pass rate: 0.5430539609644087
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.7]
- in/out: in
- source run: `823273eba4b9ec50`
- confirmation modes: mode:five_minute_close=1265, mode:tdo_retest=457, tdo_retest_reason:no_retest_in_window=454, tdo_retest_reason:retest_broke_through=507, tdo_retest_reason:tdo_unavailable=9

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1497 | 952 | 545 | 0 |  |
| context | 1742 | 1267 | 475 | 0 |  |
| location | 1722 | 1022 | 700 | 0 |  |
| management | 1427 | 946 | 481 | 0 |  |
| objective | 1427 | 946 | 481 | 0 |  |
| reference | 1742 | 1247 | 475 | 20 |  |
| risk | 1427 | 952 | 475 | 0 |  |
| trigger | 1497 | 1022 | 475 | 0 |  |

30-minute ET entry buckets: 00:00=246, 00:30=101, 01:00=111, 01:30=88, 02:00=99, 02:30=48, 03:00=108, 03:30=72, 04:00=67, 04:30=47, 05:00=34, 05:30=16, 06:00=14, 06:30=29, 07:00=22, 07:30=35, 08:00=21, 08:30=52, 09:00=21, 09:30=113, 10:00=45, 10:30=34, 11:00=14, 11:30=13, 12:00=13, 12:30=8, 13:00=9, 13:30=9, 14:00=5, 14:30=6, 15:00=5, 15:30=7, 23:00=184, 23:30=46

### `GB-FAIL:branch:asia_tdo_case`

- episodes per session: 1.0
- pass rate: 0.3685419058553387
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.65]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1486 | 737 | 749 | 0 |  |
| context | 1742 | 1292 | 450 | 0 |  |
| location | 1711 | 1036 | 675 | 0 |  |
| management | 1187 | 642 | 545 | 0 |  |
| objective | 1187 | 642 | 545 | 0 |  |
| reference | 1742 | 1261 | 450 | 31 |  |
| risk | 1187 | 737 | 450 | 0 |  |
| trigger | 1711 | 1036 | 675 | 0 |  |

30-minute ET entry buckets: 00:00=215, 00:30=68, 01:00=65, 01:30=50, 02:00=77, 02:30=48, 03:00=75, 03:30=69, 04:00=68, 04:30=43, 05:00=37, 05:30=17, 06:00=23, 06:30=19, 07:00=32, 07:30=24, 08:00=26, 08:30=68, 09:00=31, 09:30=160, 10:00=67, 10:30=68, 11:00=41, 11:30=16, 12:00=18, 12:30=10, 13:00=15, 13:30=12, 14:00=15, 14:30=7, 15:00=11, 15:30=11, 16:00=2, 23:00=165, 23:30=69

### `GB-FAIL:branch:prior_day_level`

- episodes per session: 1.9799081515499426
- pass rate: 0.28153087851551173
- bound episodes_per_session: [0, 4]
- bound pass_rate: [0.0, 0.6]
- in/out: in
- source run: `823273eba4b9ec50`
- confirmation modes: mode:five_minute_close=3044, mode:tdo_retest=370, tdo_retest_reason:no_retest_in_window=967, tdo_retest_reason:retest_broke_through=367, tdo_retest_reason:tdo_unavailable=6

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1884 | 972 | 912 | 0 |  |
| context | 3449 | 2711 | 738 | 0 |  |
| location | 3414 | 1146 | 2268 | 0 |  |
| management | 1710 | 971 | 739 | 0 |  |
| objective | 1710 | 971 | 739 | 0 |  |
| reference | 3449 | 2676 | 738 | 35 |  |
| risk | 1710 | 972 | 738 | 0 |  |
| trigger | 3414 | 1146 | 2268 | 0 |  |

30-minute ET entry buckets: 00:00=21, 00:30=11, 01:00=22, 01:30=17, 02:00=26, 02:30=21, 03:00=43, 03:30=43, 04:00=46, 04:30=32, 05:00=28, 05:30=9, 06:00=13, 06:30=19, 07:00=27, 07:30=22, 08:00=23, 08:30=70, 09:00=35, 09:30=188, 10:00=101, 10:30=75, 11:00=65, 11:30=40, 12:00=29, 12:30=27, 13:00=20, 13:30=26, 14:00=36, 14:30=22, 15:00=22, 15:30=32, 16:00=5, 18:00=1782, 18:30=69, 19:00=60, 19:30=42, 20:00=70, 20:30=56, 21:00=45, 21:30=33, 22:00=27, 22:30=21, 23:00=15, 23:30=13

### `GB-FAIL:branch:nyam_box`

- episodes per session: 2.6538461538461537
- pass rate: 0.2688730261734804
- bound episodes_per_session: [0, 12]
- bound pass_rate: [0.0, 0.4]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 3556 | 1244 | 2312 | 0 |  |
| context | 4623 | 4620 | 3 | 0 |  |
| location | 4623 | 3553 | 1070 | 0 |  |
| management | 1247 | 1243 | 4 | 0 |  |
| objective | 1247 | 1243 | 4 | 0 |  |
| reference | 4623 | 4620 | 3 | 0 |  |
| risk | 1247 | 1244 | 3 | 0 |  |
| trigger | 4623 | 3553 | 1070 | 0 |  |

30-minute ET entry buckets: 09:30=3410, 10:00=934, 10:30=111, 11:00=49, 11:30=3, 12:30=96, 13:00=20

### `GB-FAIL:branch:previous_hour`

- episodes per session: 3.764638346727899
- pass rate: 0.08981396767307105
- bound episodes_per_session: [0, 16]
- bound pass_rate: [0.0, 0.35]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1998 | 589 | 1409 | 0 |  |
| context | 6558 | 6558 | 0 | 0 |  |
| location | 6558 | 1998 | 4560 | 0 |  |
| management | 589 | 589 | 0 | 0 |  |
| objective | 589 | 589 | 0 | 0 |  |
| reference | 6558 | 6558 | 0 | 0 |  |
| risk | 589 | 589 | 0 | 0 |  |
| trigger | 6558 | 1998 | 4560 | 0 |  |

30-minute ET entry buckets: 14:00=3282, 15:00=3276

### `GB-FAIL:branch:nwog`

- episodes per session: 1.17451205510907
- pass rate: 0.07038123167155426
- bound episodes_per_session: [0, 4]
- bound pass_rate: [0.0, 0.25]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 565 | 145 | 420 | 0 |  |
| context | 2046 | 652 | 1394 | 0 |  |
| location | 608 | 565 | 43 | 0 |  |
| management | 145 | 144 | 1 | 0 |  |
| objective | 145 | 144 | 1 | 0 |  |
| reference | 2046 | 608 | 1394 | 44 |  |
| risk | 145 | 145 | 0 | 0 |  |
| trigger | 608 | 565 | 43 | 0 |  |

30-minute ET entry buckets: 00:00=2, 00:30=2, 01:00=1, 01:30=1, 02:00=1, 02:30=1, 03:00=4, 03:30=3, 04:00=1, 04:30=1, 05:30=2, 06:00=1, 07:00=5, 07:30=2, 08:00=1, 08:30=2, 09:00=2, 09:30=1458, 10:00=5, 10:30=4, 11:00=1, 11:30=4, 12:00=3, 12:30=1, 13:00=2, 13:30=2, 14:30=1, 15:30=2, 18:00=472, 18:30=14, 19:00=6, 19:30=8, 20:00=8, 20:30=7, 21:00=6, 21:30=2, 22:00=2, 22:30=3, 23:00=1, 23:30=2

### `GB-FAIL:branch:cash_open_reclaim_case`

- episodes per session: 1.0
- pass rate: 0.3283582089552239
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.5]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1681 | 1404 | 277 | 0 |  |
| context | 1742 | 1742 | 0 | 0 |  |
| location | 1684 | 1681 | 3 | 0 |  |
| management | 1404 | 572 | 832 | 0 |  |
| objective | 1404 | 572 | 832 | 0 |  |
| reference | 1742 | 1684 | 0 | 58 |  |
| risk | 1404 | 1404 | 0 | 0 |  |
| trigger | 1684 | 1681 | 3 | 0 |  |

30-minute ET entry buckets: 09:30=1554, 10:00=122, 10:30=37, 11:00=25, 11:30=4

### `GB-FAIL:branch:golden_pocket`

- episodes per session: 1.0
- pass rate: 0.4121699196326062
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.3]
- in/out: out
- diagnosis: Down-leg pocket plus a real failure. Band touch alone is not the setup.
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 763 | 720 | 43 | 0 |  |
| context | 1742 | 1742 | 0 | 0 |  |
| location | 1742 | 763 | 979 | 0 |  |
| management | 743 | 718 | 25 | 0 |  |
| objective | 743 | 718 | 25 | 0 |  |
| reference | 1742 | 824 | 918 | 0 |  |
| risk | 743 | 720 | 23 | 0 |  |
| trigger | 824 | 740 | 84 | 0 |  |

30-minute ET entry buckets: 00:00=43, 00:30=41, 01:00=39, 01:30=28, 02:00=31, 02:30=23, 03:00=34, 03:30=22, 04:00=22, 04:30=15, 05:00=7, 05:30=7, 06:00=7, 06:30=10, 07:00=10, 07:30=7, 08:00=10, 08:30=8, 09:00=1, 09:30=944, 10:00=9, 10:30=4, 11:00=1, 11:30=3, 12:00=2, 12:30=3, 13:00=3, 14:00=1, 14:30=1, 15:00=1, 15:30=5, 18:00=4, 18:30=7, 19:00=7, 19:30=14, 20:00=15, 20:30=39, 21:00=50, 21:30=72, 22:00=38, 22:30=52, 23:00=49, 23:30=53

### `GB-FAIL:branch:ny_session_extreme`

- episodes per session: 1.9730195177956371
- pass rate: 0.12743671806808263
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.2]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1789 | 438 | 1351 | 0 |  |
| context | 3437 | 3437 | 0 | 0 |  |
| location | 3390 | 1789 | 1601 | 0 |  |
| management | 438 | 438 | 0 | 0 |  |
| objective | 438 | 438 | 0 | 0 |  |
| reference | 3437 | 3390 | 0 | 47 |  |
| risk | 438 | 438 | 0 | 0 |  |
| trigger | 3390 | 1789 | 1601 | 0 |  |

30-minute ET entry buckets: 09:30=47, 11:00=2441, 11:30=249, 12:00=142, 12:30=87, 13:00=115, 13:30=64, 14:00=85, 14:30=64, 15:00=62, 15:30=70, 16:00=11

### `GB-VWAP:branch:source_long`

- episodes per session: 1.0
- pass rate: 0.14006888633754305
- bound episodes_per_session: [0, 1]
- bound pass_rate: [0.0, 0.5]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1129 | 244 | 885 | 0 |  |
| context | 1742 | 1742 | 0 | 0 |  |
| location | 1721 | 1129 | 592 | 0 |  |
| management | 244 | 244 | 0 | 0 |  |
| objective | 244 | 244 | 0 | 0 |  |
| reference | 1742 | 1721 | 0 | 21 |  |
| risk | 244 | 244 | 0 | 0 |  |
| trigger | 1721 | 1129 | 592 | 0 |  |

30-minute ET entry buckets: 09:30=857, 10:00=146, 10:30=103, 11:00=45, 11:30=44, 12:00=29, 12:30=24, 13:00=35, 13:30=19, 14:00=33, 14:30=15, 15:00=16, 15:30=18, 16:00=358

### `GB-SCALP:branch:golden_pocket_continuation`

- episodes per session: 0.9994259471871412
- pass rate: 0.26766226306720275
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.35]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 713 | 529 | 184 | 0 |  |
| context | 1741 | 1741 | 0 | 0 |  |
| location | 1741 | 713 | 1028 | 0 |  |
| management | 531 | 466 | 65 | 0 |  |
| objective | 531 | 466 | 65 | 0 |  |
| reference | 1741 | 860 | 881 | 0 |  |
| risk | 531 | 529 | 2 | 0 |  |
| trigger | 860 | 711 | 149 | 0 |  |

30-minute ET entry buckets: 09:30=1520, 10:00=88, 10:30=39, 11:00=23, 11:30=16, 12:00=8, 12:30=9, 13:00=6, 13:30=7, 14:00=10, 14:30=5, 15:00=3, 15:30=4, 16:00=3

### `SIRES:branch:dom_rejection`

- episodes per session: 13.808840413318025
- pass rate: 0.0
- bound episodes_per_session: [0, 16]
- bound pass_rate: [0.0, 0.2]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 622 | 602 | 20 | 0 |  |
| context | 24055 | 23994 | 61 | 0 |  |
| location | 23994 | 18984 | 5010 | 0 |  |
| management | 602 | 0 | 602 | 0 |  |
| objective | 602 | 0 | 0 | 602 | control_zone_far_ticks=595, target=602, target_price_ticks=602 |
| reference | 23994 | 23994 | 0 | 0 |  |
| risk | 602 | 602 | 0 | 0 |  |
| trigger | 18984 | 622 | 18362 | 0 |  |

30-minute ET entry buckets: 00:00=40, 00:30=41, 01:00=48, 01:30=71, 02:00=104, 02:30=67, 03:00=170, 03:30=130, 04:00=133, 04:30=80, 05:00=94, 05:30=87, 06:00=80, 06:30=81, 07:00=100, 07:30=100, 08:00=151, 08:30=368, 09:00=505, 09:30=3662, 10:00=891, 10:30=526, 11:00=3660, 11:30=2384, 12:00=484, 12:30=313, 13:00=240, 13:30=229, 14:00=237, 14:30=197, 15:00=230, 15:30=400, 16:00=252, 16:30=198, 18:00=5587, 18:30=567, 19:00=364, 19:30=229, 20:00=303, 20:30=175, 21:00=124, 21:30=125, 22:00=77, 22:30=61, 23:00=43, 23:30=47

### `SIRES:branch:absorption_reward_retest`

- episodes per session: 13.808840413318025
- pass rate: 0.0014134275618374558
- bound episodes_per_session: [0, 16]
- bound pass_rate: [0.0, 0.2]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 736 | 34 | 702 | 0 |  |
| context | 24055 | 23994 | 61 | 0 |  |
| location | 23994 | 18984 | 5010 | 0 |  |
| management | 34 | 34 | 0 | 0 |  |
| objective | 34 | 34 | 0 | 0 |  |
| reference | 23994 | 23994 | 0 | 0 |  |
| risk | 34 | 34 | 0 | 0 |  |
| trigger | 18984 | 736 | 18248 | 0 |  |

30-minute ET entry buckets: 00:00=41, 00:30=39, 01:00=45, 01:30=69, 02:00=103, 02:30=67, 03:00=170, 03:30=128, 04:00=128, 04:30=78, 05:00=93, 05:30=84, 06:00=79, 06:30=75, 07:00=98, 07:30=96, 08:00=144, 08:30=351, 09:00=520, 09:30=3695, 10:00=913, 10:30=548, 11:00=3678, 11:30=2385, 12:00=489, 12:30=314, 13:00=248, 13:30=231, 14:00=246, 14:30=202, 15:00=234, 15:30=403, 16:00=248, 16:30=199, 18:00=5503, 18:30=566, 19:00=371, 19:30=229, 20:00=299, 20:30=176, 21:00=121, 21:30=126, 22:00=73, 22:30=62, 23:00=42, 23:30=46

### `SIRES:branch:stop_four_stage`

- episodes per session: 13.808840413318025
- pass rate: 0.16641030970692164
- bound episodes_per_session: [0, 16]
- bound pass_rate: [0.0, 0.2]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 15726 | 14685 | 1041 | 0 |  |
| context | 24055 | 23994 | 61 | 0 |  |
| location | 23994 | 18984 | 5010 | 0 |  |
| management | 14529 | 4003 | 10526 | 0 |  |
| objective | 14529 | 14529 | 0 | 0 |  |
| reference | 23994 | 23994 | 0 | 0 |  |
| risk | 14685 | 14529 | 156 | 0 |  |
| trigger | 18984 | 15726 | 3258 | 0 |  |

30-minute ET entry buckets: 00:00=41, 00:30=39, 01:00=45, 01:30=69, 02:00=103, 02:30=67, 03:00=170, 03:30=128, 04:00=128, 04:30=78, 05:00=93, 05:30=84, 06:00=79, 06:30=75, 07:00=98, 07:30=96, 08:00=144, 08:30=351, 09:00=520, 09:30=3695, 10:00=913, 10:30=548, 11:00=3678, 11:30=2385, 12:00=489, 12:30=314, 13:00=248, 13:30=231, 14:00=246, 14:30=202, 15:00=234, 15:30=403, 16:00=248, 16:30=199, 18:00=5503, 18:30=566, 19:00=371, 19:30=229, 20:00=299, 20:30=176, 21:00=121, 21:30=126, 22:00=73, 22:30=62, 23:00=42, 23:30=46

### `SIRES:branch:footprint_confirmed_reaction`

- episodes per session: 13.808840413318025
- pass rate: 0.0004157139887757223
- bound episodes_per_session: [0, 16]
- bound pass_rate: [0.0, 0.2]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 14335 | 682 | 13653 | 0 |  |
| context | 24055 | 23994 | 61 | 0 |  |
| location | 23994 | 18984 | 5010 | 0 |  |
| management | 682 | 682 | 0 | 0 |  |
| objective | 682 | 682 | 0 | 0 |  |
| reference | 23994 | 23994 | 0 | 0 |  |
| risk | 682 | 682 | 0 | 0 |  |
| trigger | 18984 | 890 | 4649 | 13445 | footprint_ratio=13445, imbalance_ratio=6809 |

30-minute ET entry buckets: 00:00=40, 00:30=41, 01:00=48, 01:30=71, 02:00=104, 02:30=67, 03:00=170, 03:30=130, 04:00=133, 04:30=80, 05:00=94, 05:30=87, 06:00=80, 06:30=81, 07:00=100, 07:30=100, 08:00=151, 08:30=368, 09:00=505, 09:30=3662, 10:00=891, 10:30=526, 11:00=3660, 11:30=2384, 12:00=484, 12:30=313, 13:00=240, 13:30=229, 14:00=237, 14:30=197, 15:00=230, 15:30=400, 16:00=252, 16:30=198, 18:00=5587, 18:30=567, 19:00=364, 19:30=229, 20:00=303, 20:30=175, 21:00=124, 21:30=125, 22:00=77, 22:30=61, 23:00=43, 23:30=47

### `SIRES:branch:vwap_deviation_fade`

- episodes per session: 13.808840413318025
- pass rate: 0.012388276865516525
- bound episodes_per_session: [0, 16]
- bound pass_rate: [0.0, 0.2]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 7109 | 701 | 6408 | 0 |  |
| context | 24055 | 23994 | 61 | 0 |  |
| location | 23994 | 18984 | 5010 | 0 |  |
| management | 701 | 701 | 0 | 0 |  |
| objective | 701 | 701 | 0 | 0 |  |
| reference | 23994 | 23994 | 0 | 0 |  |
| risk | 701 | 701 | 0 | 0 |  |
| trigger | 18984 | 298 | 11875 | 6811 | beyond_1_band=6811, vwap_sd_ticks=6782, vwap_ticks=6782 |

30-minute ET entry buckets: 00:00=40, 00:30=41, 01:00=48, 01:30=71, 02:00=104, 02:30=67, 03:00=170, 03:30=130, 04:00=133, 04:30=80, 05:00=94, 05:30=87, 06:00=80, 06:30=81, 07:00=100, 07:30=100, 08:00=151, 08:30=368, 09:00=505, 09:30=3662, 10:00=891, 10:30=526, 11:00=3660, 11:30=2384, 12:00=484, 12:30=313, 13:00=240, 13:30=229, 14:00=237, 14:30=197, 15:00=230, 15:30=400, 16:00=252, 16:30=198, 18:00=5587, 18:30=567, 19:00=364, 19:30=229, 20:00=303, 20:30=175, 21:00=124, 21:30=125, 22:00=77, 22:30=61, 23:00=43, 23:30=47

### `SIRES:branch:ofm_aggressive`

- episodes per session: 15.466130884041332
- pass rate: 0.0
- bound episodes_per_session: [1, 1]
- bound pass_rate: [0.0, 0.0]
- in/out: out
- diagnosis: OFM p.4: OFM p.4 states an A++ a handful of times a month. That is an A++-trade frequency, not a contact-per-session density. The B0.2 scan enumerates contacts at source-literal locations. No source page states a contact density, so the registry keeps the source-grounded one-decision-per-session bound [1, 1] and episode_kind session_unknown. After ruling (a) the scan no longer stops at the unknown gamma context, so it enumerates every source-literal contact and the observed density lands above [1, 1]. That is reported as an out-of-bound finding with this justification; the bound is not widened to make the gate pass.
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 4728 | 4728 | 0 | 0 |  |
| context | 26942 | 0 | 0 | 26942 | gamma_regime=26942, new_information=26942 |
| location | 26942 | 21388 | 5554 | 0 |  |
| management | 3500 | 3500 | 0 | 0 |  |
| objective | 3500 | 3500 | 0 | 0 |  |
| reference | 26942 | 26942 | 0 | 0 |  |
| risk | 4728 | 3500 | 1228 | 0 |  |
| trigger | 21388 | 4728 | 16660 | 0 |  |

30-minute ET entry buckets: 00:00=47, 00:30=44, 01:00=58, 01:30=81, 02:00=118, 02:30=74, 03:00=194, 03:30=142, 04:00=148, 04:30=93, 05:00=108, 05:30=92, 06:00=87, 06:30=94, 07:00=119, 07:30=111, 08:00=176, 08:30=460, 09:00=597, 09:30=4044, 10:00=991, 10:30=586, 11:00=4100, 11:30=2751, 12:00=552, 12:30=362, 13:00=277, 13:30=262, 14:00=274, 14:30=233, 15:00=258, 15:30=463, 16:00=312, 16:30=231, 18:00=6056, 18:30=616, 19:00=392, 19:30=255, 20:00=335, 20:30=199, 21:00=145, 21:30=139, 22:00=84, 22:30=76, 23:00=52, 23:30=54

### `SIRES:branch:ofm_passive`

- episodes per session: 13.808840413318025
- pass rate: 0.0
- bound episodes_per_session: [0, 16]
- bound pass_rate: [0.0, 0.15]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| context | 24055 | 23994 | 61 | 0 |  |
| location | 23994 | 18984 | 5010 | 0 |  |
| reference | 23994 | 23994 | 0 | 0 |  |
| trigger | 18984 | 0 | 18984 | 0 |  |

30-minute ET entry buckets: 00:00=40, 00:30=41, 01:00=48, 01:30=71, 02:00=104, 02:30=67, 03:00=170, 03:30=130, 04:00=133, 04:30=80, 05:00=94, 05:30=87, 06:00=80, 06:30=81, 07:00=100, 07:30=100, 08:00=151, 08:30=368, 09:00=505, 09:30=3662, 10:00=891, 10:30=526, 11:00=3660, 11:30=2384, 12:00=484, 12:30=313, 13:00=240, 13:30=229, 14:00=237, 14:30=197, 15:00=230, 15:30=400, 16:00=252, 16:30=198, 18:00=5587, 18:30=567, 19:00=364, 19:30=229, 20:00=303, 20:30=175, 21:00=124, 21:30=125, 22:00=77, 22:30=61, 23:00=43, 23:30=47

### `SIRES:branch:clean_squeeze`

- episodes per session: 13.808840413318025
- pass rate: 0.008522136769902306
- bound episodes_per_session: [0, 16]
- bound pass_rate: [0.0, 0.15]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 205 | 205 | 0 | 0 |  |
| context | 24055 | 23994 | 61 | 0 |  |
| location | 23994 | 18984 | 5010 | 0 |  |
| management | 205 | 205 | 0 | 0 |  |
| objective | 205 | 205 | 0 | 0 |  |
| reference | 23994 | 23994 | 0 | 0 |  |
| risk | 205 | 205 | 0 | 0 |  |
| trigger | 18984 | 205 | 18779 | 0 |  |

30-minute ET entry buckets: 00:00=40, 00:30=41, 01:00=48, 01:30=71, 02:00=104, 02:30=67, 03:00=170, 03:30=130, 04:00=133, 04:30=80, 05:00=94, 05:30=87, 06:00=80, 06:30=81, 07:00=100, 07:30=100, 08:00=151, 08:30=368, 09:00=505, 09:30=3662, 10:00=891, 10:30=526, 11:00=3660, 11:30=2384, 12:00=484, 12:30=313, 13:00=240, 13:30=229, 14:00=237, 14:30=197, 15:00=230, 15:30=400, 16:00=252, 16:30=198, 18:00=5587, 18:30=567, 19:00=364, 19:30=229, 20:00=303, 20:30=175, 21:00=124, 21:30=125, 22:00=77, 22:30=61, 23:00=43, 23:30=47

### `SIRES:branch:balance_failure_fade`

- episodes per session: 27.61768082663605
- pass rate: 0.0
- bound episodes_per_session: [1, 1]
- bound pass_rate: [0.0, 0.0]
- in/out: out
- diagnosis: BIG p.14: BIG p.14 states the balance fade in long gamma about 80% of the time. That is a regime-share frequency, not a contact-per-session density. The B0.2 scan enumerates contacts at source-literal locations. No source page states a contact density, so the registry keeps the source-grounded one-decision-per-session bound [1, 1] and episode_kind session_unknown. After ruling (a) the scan no longer stops at the unknown gamma context, so it enumerates every source-literal contact and the observed density lands above [1, 1]. That is reported as an out-of-bound finding with this justification; the bound is not widened to make the gate pass.
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 4728 | 2476 | 2252 | 0 |  |
| context | 48110 | 0 | 0 | 48110 | gamma_regime=48110, new_information=48110 |
| location | 48110 | 38048 | 10062 | 0 |  |
| management | 2476 | 2476 | 0 | 0 |  |
| objective | 2476 | 2476 | 0 | 0 |  |
| reference | 48110 | 48110 | 0 | 0 |  |
| risk | 2476 | 2476 | 0 | 0 |  |
| trigger | 38048 | 4728 | 33320 | 0 |  |

30-minute ET entry buckets: 00:00=80, 00:30=82, 01:00=96, 01:30=142, 02:00=208, 02:30=134, 03:00=340, 03:30=260, 04:00=266, 04:30=160, 05:00=188, 05:30=174, 06:00=160, 06:30=162, 07:00=200, 07:30=200, 08:00=302, 08:30=736, 09:00=1010, 09:30=7324, 10:00=1782, 10:30=1052, 11:00=7320, 11:30=4768, 12:00=968, 12:30=626, 13:00=480, 13:30=458, 14:00=474, 14:30=394, 15:00=460, 15:30=800, 16:00=504, 16:30=396, 18:00=11174, 18:30=1134, 19:00=728, 19:30=458, 20:00=606, 20:30=350, 21:00=248, 21:30=250, 22:00=154, 22:30=122, 23:00=86, 23:30=94

### `SIRES:branch:defended_band_continuation`

- episodes per session: 13.808840413318025
- pass rate: 0.16599459571814593
- bound episodes_per_session: [0, 16]
- bound pass_rate: [0.0, 0.2]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 15726 | 14685 | 1041 | 0 |  |
| context | 24055 | 23994 | 61 | 0 |  |
| location | 23994 | 18984 | 5010 | 0 |  |
| management | 14685 | 3993 | 10564 | 128 |  |
| objective | 14685 | 3993 | 0 | 10692 | control_zone_far_ticks=10621, target=10692, target_price_ticks=10692 |
| reference | 23994 | 23994 | 0 | 0 |  |
| risk | 14685 | 14685 | 0 | 0 |  |
| trigger | 18984 | 15726 | 3258 | 0 |  |

30-minute ET entry buckets: 00:00=40, 00:30=41, 01:00=48, 01:30=71, 02:00=104, 02:30=67, 03:00=170, 03:30=130, 04:00=133, 04:30=80, 05:00=94, 05:30=87, 06:00=80, 06:30=81, 07:00=100, 07:30=100, 08:00=151, 08:30=368, 09:00=505, 09:30=3662, 10:00=891, 10:30=526, 11:00=3660, 11:30=2384, 12:00=484, 12:30=313, 13:00=240, 13:30=229, 14:00=237, 14:30=197, 15:00=230, 15:30=400, 16:00=252, 16:30=198, 18:00=5587, 18:30=567, 19:00=364, 19:30=229, 20:00=303, 20:30=175, 21:00=124, 21:30=125, 22:00=77, 22:30=61, 23:00=43, 23:30=47

### `SIRES:branch:kg1_retest`

- episodes per session: 0.0
- pass rate: 0.0
- bound episodes_per_session: [0, 1]
- bound pass_rate: [0.0, 0.2]
- in/out: in
- source run: `1019e6c09ee54609`

### `SIRES:branch:microbalance_break`

- episodes per session: 0.000574052812858783
- pass rate: 0.0
- bound episodes_per_session: [0, 16]
- bound pass_rate: [0.0, 0.2]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1 | 0 | 1 | 0 |  |
| context | 1 | 1 | 0 | 0 |  |
| location | 1 | 1 | 0 | 0 |  |
| reference | 1 | 1 | 0 | 0 |  |
| trigger | 1 | 1 | 0 | 0 |  |

30-minute ET entry buckets: 18:00=1

### `SAINT-AMT:branch:continuation_retest`

- episodes per session: 1.9052812858783008
- pass rate: 0.02771919252786984
- bound episodes_per_session: [0, 3]
- bound pass_rate: [0.0, 0.35]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 3271 | 92 | 3091 | 88 | arrival=57, arrival_ok=57, arrival_ratio=57, confirm_at=31, held_retest=31, retest_aggression=31 |
| context | 3319 | 3271 | 48 | 0 |  |
| location | 3271 | 3271 | 0 | 0 |  |
| objective | 149 | 149 | 0 | 0 |  |
| reference | 3271 | 3271 | 0 | 0 |  |
| risk | 180 | 149 | 31 | 0 |  |
| trigger | 3271 | 3271 | 0 | 0 |  |

30-minute ET entry buckets: 00:00=57, 00:30=46, 01:00=68, 01:30=65, 02:00=108, 02:30=81, 03:00=164, 03:30=133, 04:00=150, 04:30=114, 05:00=98, 05:30=78, 06:00=80, 06:30=68, 07:00=74, 07:30=61, 08:00=60, 08:30=61, 09:00=46, 09:30=144, 10:00=36, 10:30=19, 11:00=11, 11:30=4, 12:00=10, 12:30=4, 13:00=4, 13:30=6, 14:00=4, 14:30=6, 15:00=2, 15:30=3, 18:00=332, 18:30=132, 19:00=121, 19:30=101, 20:00=166, 20:30=130, 21:00=110, 21:30=107, 22:00=94, 22:30=74, 23:00=52, 23:30=35

### `SAINT-AMT:branch:trapped_buyers_retest`

- episodes per session: 1.9052812858783008
- pass rate: 0.033142512805061766
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.25]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 3271 | 110 | 3005 | 156 | arrival=125, arrival_ok=125, arrival_ratio=125, confirm_at=31, held_retest=31, retest_aggression=31, trap_delta_at_extreme=125 |
| context | 3319 | 3271 | 48 | 0 |  |
| location | 3271 | 3271 | 0 | 0 |  |
| objective | 235 | 235 | 0 | 0 |  |
| reference | 3271 | 3271 | 0 | 0 |  |
| risk | 266 | 235 | 31 | 0 |  |
| trigger | 3271 | 3271 | 0 | 0 |  |

30-minute ET entry buckets: 00:00=57, 00:30=46, 01:00=68, 01:30=65, 02:00=108, 02:30=81, 03:00=164, 03:30=133, 04:00=150, 04:30=114, 05:00=98, 05:30=78, 06:00=80, 06:30=68, 07:00=74, 07:30=61, 08:00=60, 08:30=61, 09:00=46, 09:30=144, 10:00=36, 10:30=19, 11:00=11, 11:30=4, 12:00=10, 12:30=4, 13:00=4, 13:30=6, 14:00=4, 14:30=6, 15:00=2, 15:30=3, 18:00=332, 18:30=132, 19:00=121, 19:30=101, 20:00=166, 20:30=130, 21:00=110, 21:30=107, 22:00=94, 22:30=74, 23:00=52, 23:30=35

### `SAINT-AMT:branch:failed_auction_return`

- episodes per session: 0.4368541905855339
- pass rate: 0.17082785808147175
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.35]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 683 | 130 | 553 | 0 |  |
| context | 761 | 751 | 10 | 0 |  |
| location | 751 | 683 | 68 | 0 |  |
| reference | 751 | 751 | 0 | 0 |  |
| trigger | 683 | 683 | 0 | 0 |  |

30-minute ET entry buckets: 00:00=6, 00:30=10, 01:00=14, 01:30=18, 02:00=20, 02:30=9, 03:00=21, 03:30=16, 04:00=30, 04:30=20, 05:00=20, 05:30=14, 06:00=13, 06:30=10, 07:00=16, 07:30=10, 08:00=13, 08:30=35, 09:00=8, 09:30=40, 10:00=22, 10:30=11, 11:00=18, 11:30=7, 12:00=4, 12:30=7, 13:00=8, 13:30=3, 14:00=9, 14:30=7, 15:00=3, 15:30=5, 18:00=92, 18:30=30, 19:00=32, 19:30=20, 20:00=40, 20:30=19, 21:00=23, 21:30=23, 22:00=9, 22:30=10, 23:00=7, 23:30=9

### `SAINT-AMT:branch:poc_traversal`

- episodes per session: 0.9845005740528129
- pass rate: 0.36443148688046645
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.4]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1136 | 625 | 511 | 0 |  |
| context | 1715 | 1690 | 25 | 0 |  |
| location | 1690 | 1690 | 0 | 0 |  |
| objective | 625 | 625 | 0 | 0 |  |
| reference | 1690 | 1690 | 0 | 0 |  |
| trigger | 1690 | 1136 | 554 | 0 |  |

30-minute ET entry buckets: 00:00=18, 00:30=15, 01:00=27, 01:30=26, 02:00=53, 02:30=33, 03:00=66, 03:30=43, 04:00=69, 04:30=41, 05:00=40, 05:30=35, 06:00=36, 06:30=23, 07:00=32, 07:30=24, 08:00=25, 08:30=43, 09:00=28, 09:30=95, 10:00=46, 10:30=29, 11:00=30, 11:30=19, 12:00=18, 12:30=26, 13:00=15, 13:30=22, 14:00=19, 14:30=14, 15:00=24, 15:30=73, 16:00=36, 18:00=134, 18:30=64, 19:00=48, 19:30=43, 20:00=76, 20:30=48, 21:00=33, 21:30=44, 22:00=29, 22:30=14, 23:00=20, 23:30=19

### `MEMBER-TWO-REASONS:branch:resistance_short`

- episodes per session: 1.0
- pass rate: 0.25889781859931116
- bound episodes_per_session: [0, 3]
- bound pass_rate: [0.0, 0.35]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1107 | 451 | 656 | 0 |  |
| context | 1742 | 1711 | 31 | 0 |  |
| location | 1711 | 1711 | 0 | 0 |  |
| objective | 451 | 451 | 0 | 0 |  |
| reference | 1711 | 1711 | 0 | 0 |  |
| risk | 451 | 451 | 0 | 0 |  |
| trigger | 1711 | 1107 | 604 | 0 |  |

30-minute ET entry buckets: 09:30=694, 10:00=160, 10:30=112, 11:00=77, 11:30=59, 12:00=37, 12:30=33, 13:00=37, 13:30=27, 14:00=35, 14:30=28, 15:00=40, 15:30=38, 16:00=365

### `MEMBER-TWO-REASONS:branch:planned_return_long`

- episodes per session: 1.0
- pass rate: 0.27152698048220436
- bound episodes_per_session: [0, 3]
- bound pass_rate: [0.0, 0.35]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1136 | 473 | 663 | 0 |  |
| context | 1742 | 1709 | 33 | 0 |  |
| location | 1709 | 1709 | 0 | 0 |  |
| objective | 473 | 473 | 0 | 0 |  |
| reference | 1709 | 1709 | 0 | 0 |  |
| risk | 473 | 473 | 0 | 0 |  |
| trigger | 1709 | 1136 | 573 | 0 |  |

30-minute ET entry buckets: 09:30=673, 10:00=155, 10:30=110, 11:00=80, 11:30=59, 12:00=37, 12:30=37, 13:00=34, 13:30=38, 14:00=40, 14:30=40, 15:00=38, 15:30=25, 16:00=376

### `KEANI-OPEN-ABOVE-VALUE:branch:source_long`

- episodes per session: 1.0
- pass rate: 0.0
- bound episodes_per_session: [0, 1]
- bound pass_rate: [0.0, 0.08]
- in/out: in
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| context | 1742 | 406 | 1253 | 83 | a_low=47, prior_vah=37 |
| location | 442 | 440 | 2 | 0 |  |
| reference | 489 | 452 | 0 | 37 | prior_vah=37 |
| trigger | 440 | 0 | 440 | 0 |  |

30-minute ET entry buckets: 10:00=1742

### `REFILL-STUDY:branch:touch_record`

- episodes per session: 456.58381171067737
- pass rate: 0.0455813590924464
- bound episodes_per_session: [80, 350]
- bound pass_rate: [0.25, 0.6]
- in/out: out
- diagnosis: REF pp.5-8: REF p.8 prints 42% hold on 41152 NQ and MNQ touches over 235 RTH sessions Dec 24-Nov 25. The hold tick cutoff is not printed. Phase 1.5 labels hold with OD HOLD_BOUNDARY_TICKS=8 inside 30 minutes on NQ only, on 15 calendar sessions that are not that 235-session window. The bound stays at 175 and 42%. The observed hold rate is the OD label on this slice, not a rewrite of the paper.
- source run: `1019e6c09ee54609`

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 795369 | 36254 | 759110 | 5 | held=5 |
| location | 795369 | 795369 | 0 | 0 |  |
| objective | 795369 | 739976 | 51982 | 3411 |  |
| reference | 795369 | 795369 | 0 | 0 |  |
| risk | 795369 | 795369 | 0 | 0 |  |
| trigger | 795369 | 795369 | 0 | 0 |  |

30-minute ET entry buckets: 00:00=821, 00:30=832, 01:00=1139, 01:30=1067, 02:00=1462, 02:30=1468, 03:00=2757, 03:30=2498, 04:00=3104, 04:30=2367, 05:00=2202, 05:30=2381, 06:00=2594, 06:30=2474, 07:00=3447, 07:30=3669, 08:00=5567, 08:30=12209, 09:00=12730, 09:30=85951, 10:00=69297, 10:30=56561, 11:00=50286, 11:30=43993, 12:00=39229, 12:30=36794, 13:00=39587, 13:30=38412, 14:00=43867, 14:30=44893, 15:00=49931, 15:30=74234, 16:00=34075, 16:30=11564, 18:00=853, 18:30=570, 19:00=637, 19:30=817, 20:00=1367, 20:30=1131, 21:00=1213, 21:30=1127, 22:00=1155, 22:30=1024, 23:00=1035, 23:30=978

### `GB-FAIL:branch:prior_week_level`

- episodes per session: 2.0
- pass rate: 0.1148105625717566
- bound episodes_per_session: [0, 2]
- bound pass_rate: [0.0, 0.6]
- in/out: in
- source run: `823273eba4b9ec50`
- confirmation modes: mode:five_minute_close=3360, mode:tdo_retest=124, tdo_retest_reason:no_retest_in_window=484, tdo_retest_reason:retest_broke_through=127, tdo_retest_reason:retest_close_unknown=1, tdo_retest_reason:tdo_unavailable=5

| stage | entering | pass | fail | unknown | unknown operands |
| --- | ---: | ---: | ---: | ---: | --- |
| confirmation | 1218 | 400 | 818 | 0 |  |
| context | 3484 | 3143 | 341 | 0 |  |
| location | 3484 | 877 | 2607 | 0 |  |
| management | 741 | 400 | 341 | 0 |  |
| objective | 741 | 400 | 341 | 0 |  |
| reference | 3484 | 3143 | 341 | 0 |  |
| risk | 741 | 400 | 341 | 0 |  |
| trigger | 3484 | 877 | 2607 | 0 |  |

30-minute ET entry buckets: 00:00=3, 00:30=2, 01:00=5, 01:30=5, 02:00=9, 02:30=10, 03:00=13, 03:30=19, 04:00=12, 04:30=11, 05:00=12, 05:30=7, 06:00=5, 06:30=8, 07:00=11, 07:30=9, 08:00=14, 08:30=23, 09:00=14, 09:30=74, 10:00=47, 10:30=41, 11:00=26, 11:30=26, 12:00=22, 12:30=13, 13:00=12, 13:30=20, 14:00=11, 14:30=20, 15:00=15, 15:30=24, 16:00=1, 18:00=2764, 18:30=33, 19:00=20, 19:30=14, 20:00=22, 20:30=21, 21:00=17, 21:30=17, 22:00=11, 22:30=6, 23:00=8, 23:30=7
