# Selection headroom of the executed lists

Records: `/workspace/.scratch/a537e734/exits-b03-records/rows.jsonl`

### GB-FAIL, policy E0: 1721 sessions, 29047 trades (16.9 a session)

| list | points a session | median session | sessions positive |
| --- | ---: | ---: | ---: |
| every executed trade | 44.7 | 26.0 | 0.58 |
| hindsight best 1 a session | 82.5 | 67.8 | 0.99 |
| hindsight best 2 | 137.4 | 113.8 | 0.99 |
| hindsight best 3 | 173.3 | 144.8 | 0.98 |
| winners only (a perfect filter) | 237.0 | 195.0 | 0.99 |

By year (points a session, every trade / best 1 / best 3):

| year | sessions | every trade | best 1 | best 3 |
| --- | ---: | ---: | ---: | ---: |
| 2020 | 258 | 49.2 | 66.5 | 144.1 |
| 2021 | 258 | 16.3 | 61.4 | 127.1 |
| 2022 | 258 | 47.4 | 92.3 | 193.2 |
| 2023 | 257 | 25.8 | 60.7 | 129.2 |
| 2024 | 259 | 35.6 | 74.7 | 156.2 |
| 2025 | 257 | 69.4 | 99.6 | 215.6 |
| 2026 | 174 | 81.0 | 141.6 | 283.5 |

By branch (points a trade, count, share of trades positive):

| branch | trades | mean | win share |
| --- | ---: | ---: | ---: |
| nyam_box | 7722 | 7.41 | 0.33 |
| prior_day_level | 3909 | 6.61 | 0.42 |
| cash_open_reclaim_case | 3635 | -1.67 | 0.52 |
| previous_hour | 3312 | -0.81 | 0.23 |
| asia_tdo_case | 3078 | 2.47 | 0.54 |
| golden_pocket | 2715 | -9.05 | 0.22 |
| asia_box | 1632 | 3.79 | 0.41 |
| london_box | 1611 | 4.88 | 0.39 |
| prior_week_level | 1433 | 3.92 | 0.42 |

By fill mode:

| mode | trades | mean | win share |
| --- | ---: | ---: | ---: |
| at_level | 15189 | 6.09 | 0.42 |
| approach_reject | 4399 | 2.21 | 0.24 |
| next_bar_open | 3695 | -3.58 | 0.51 |
| five_minute_close | 1352 | 4.47 | 0.36 |
| pocket_retest_after_failure | 1258 | -10.22 | 0.26 |
| pocket_near_limit | 1248 | -8.94 | 0.19 |
| post_open_retest | 996 | -1.41 | 0.23 |
| tdo_close | 488 | -3.74 | 0.41 |
| stop_at_level | 133 | 71.36 | 0.74 |
| pocket_far_limit | 113 | -1.31 | 0.06 |
| stop_at_next_level | 76 | 5.01 | 0.49 |
| pocket_failure_close | 54 | 3.55 | 0.33 |
| pocket_close | 42 | -14.40 | 0.40 |
| failure_close_1m | 4 | -37.62 | 0.50 |

### GB-FAIL, policy E5: 1721 sessions, 29437 trades (17.1 a session)

| list | points a session | median session | sessions positive |
| --- | ---: | ---: | ---: |
| every executed trade | 44.6 | 2.8 | 0.51 |
| hindsight best 1 a session | 120.6 | 96.5 | 0.98 |
| hindsight best 2 | 196.4 | 154.5 | 0.98 |
| hindsight best 3 | 239.4 | 189.5 | 0.98 |
| winners only (a perfect filter) | 292.6 | 223.5 | 0.98 |

By year (points a session, every trade / best 1 / best 3):

| year | sessions | every trade | best 1 | best 3 |
| --- | ---: | ---: | ---: | ---: |
| 2020 | 258 | 53.6 | 104.6 | 208.6 |
| 2021 | 258 | 13.6 | 88.6 | 174.9 |
| 2022 | 258 | 47.1 | 130.5 | 266.0 |
| 2023 | 257 | 27.5 | 89.5 | 178.4 |
| 2024 | 259 | 45.2 | 111.7 | 224.7 |
| 2025 | 257 | 51.7 | 145.5 | 289.8 |
| 2026 | 174 | 87.6 | 199.3 | 379.1 |

By branch (points a trade, count, share of trades positive):

| branch | trades | mean | win share |
| --- | ---: | ---: | ---: |
| nyam_box | 7813 | 8.45 | 0.19 |
| prior_day_level | 3944 | 6.37 | 0.26 |
| cash_open_reclaim_case | 3612 | -1.81 | 0.53 |
| previous_hour | 3299 | -1.34 | 0.19 |
| asia_tdo_case | 3181 | 2.31 | 0.48 |
| golden_pocket | 2806 | -10.17 | 0.18 |
| asia_box | 1700 | 2.34 | 0.15 |
| london_box | 1638 | 4.72 | 0.23 |
| prior_week_level | 1444 | 4.24 | 0.32 |

By fill mode:

| mode | trades | mean | win share |
| --- | ---: | ---: | ---: |
| at_level | 15540 | 5.71 | 0.26 |
| approach_reject | 4376 | 2.84 | 0.20 |
| next_bar_open | 3668 | -3.82 | 0.52 |
| pocket_retest_after_failure | 1336 | -12.09 | 0.22 |
| five_minute_close | 1335 | 5.71 | 0.28 |
| pocket_near_limit | 1259 | -9.09 | 0.14 |
| post_open_retest | 993 | -1.30 | 0.19 |
| tdo_close | 510 | -6.03 | 0.23 |
| stop_at_level | 130 | 103.42 | 0.70 |
| pocket_far_limit | 113 | -2.03 | 0.04 |
| stop_at_next_level | 75 | 21.66 | 0.53 |
| pocket_failure_close | 56 | -2.29 | 0.30 |
| pocket_close | 42 | -13.69 | 0.40 |
| failure_close_1m | 4 | -37.62 | 0.50 |

### GB-SCALP, policy E0: 1165 sessions, 2156 trades (1.9 a session)

| list | points a session | median session | sessions positive |
| --- | ---: | ---: | ---: |
| every executed trade | -7.6 | -17.1 | 0.38 |
| hindsight best 1 a session | 10.3 | -3.6 | 0.46 |
| hindsight best 2 | 2.0 | -12.6 | 0.42 |
| hindsight best 3 | -4.0 | -14.9 | 0.39 |
| winners only (a perfect filter) | 25.6 | 0.0 | 0.46 |

By year (points a session, every trade / best 1 / best 3):

| year | sessions | every trade | best 1 | best 3 |
| --- | ---: | ---: | ---: | ---: |
| 2020 | 175 | 0.4 | 12.5 | 3.6 |
| 2021 | 169 | -4.7 | 9.3 | -2.9 |
| 2022 | 171 | -10.5 | 10.5 | -5.7 |
| 2023 | 183 | -10.2 | 8.8 | -5.4 |
| 2024 | 187 | -11.0 | 6.7 | -8.1 |
| 2025 | 180 | -9.0 | 14.2 | -4.6 |
| 2026 | 100 | -7.7 | 10.8 | -4.7 |

By branch (points a trade, count, share of trades positive):

| branch | trades | mean | win share |
| --- | ---: | ---: | ---: |
| golden_pocket_continuation | 2156 | -4.09 | 0.30 |

By fill mode:

| mode | trades | mean | win share |
| --- | ---: | ---: | ---: |
| pocket_near_limit | 1133 | -4.01 | 0.25 |
| pocket_retest_after_failure | 887 | -4.73 | 0.37 |
| pocket_far_limit | 69 | -2.66 | 0.06 |
| pocket_close | 41 | -15.28 | 0.39 |
| pocket_failure_close | 26 | 28.04 | 0.77 |

### GB-SCALP, policy E5: 1165 sessions, 2144 trades (1.8 a session)

| list | points a session | median session | sessions positive |
| --- | ---: | ---: | ---: |
| every executed trade | -6.0 | -20.7 | 0.35 |
| hindsight best 1 a session | 13.0 | -10.4 | 0.41 |
| hindsight best 2 | 4.1 | -17.8 | 0.38 |
| hindsight best 3 | -2.1 | -18.9 | 0.36 |
| winners only (a perfect filter) | 31.2 | 0.0 | 0.41 |

By year (points a session, every trade / best 1 / best 3):

| year | sessions | every trade | best 1 | best 3 |
| --- | ---: | ---: | ---: | ---: |
| 2020 | 175 | 6.2 | 20.6 | 10.2 |
| 2021 | 169 | -1.4 | 12.9 | 0.1 |
| 2022 | 171 | -12.4 | 9.2 | -7.3 |
| 2023 | 183 | -8.9 | 10.9 | -3.8 |
| 2024 | 187 | -11.9 | 8.4 | -8.6 |
| 2025 | 180 | -5.2 | 17.7 | -0.5 |
| 2026 | 100 | -9.2 | 10.0 | -6.2 |

By branch (points a trade, count, share of trades positive):

| branch | trades | mean | win share |
| --- | ---: | ---: | ---: |
| golden_pocket_continuation | 2144 | -3.24 | 0.27 |

By fill mode:

| mode | trades | mean | win share |
| --- | ---: | ---: | ---: |
| pocket_near_limit | 1131 | -3.51 | 0.23 |
| pocket_retest_after_failure | 878 | -3.86 | 0.31 |
| pocket_far_limit | 69 | -2.08 | 0.06 |
| pocket_close | 41 | -13.97 | 0.39 |
| pocket_failure_close | 25 | 44.69 | 0.76 |

### JJ-TBR, policy E0: 1719 sessions, 19691 trades (11.5 a session)

| list | points a session | median session | sessions positive |
| --- | ---: | ---: | ---: |
| every executed trade | 50.6 | 23.3 | 0.61 |
| hindsight best 1 a session | 48.6 | 40.0 | 0.96 |
| hindsight best 2 | 82.6 | 67.0 | 0.95 |
| hindsight best 3 | 103.9 | 85.8 | 0.94 |
| winners only (a perfect filter) | 155.2 | 113.5 | 0.96 |

By year (points a session, every trade / best 1 / best 3):

| year | sessions | every trade | best 1 | best 3 |
| --- | ---: | ---: | ---: | ---: |
| 2020 | 257 | 38.3 | 37.1 | 82.3 |
| 2021 | 258 | 30.9 | 35.3 | 76.4 |
| 2022 | 258 | 51.6 | 56.8 | 124.4 |
| 2023 | 257 | 41.5 | 36.4 | 78.6 |
| 2024 | 259 | 45.7 | 45.0 | 95.2 |
| 2025 | 257 | 62.2 | 57.4 | 120.7 |
| 2026 | 173 | 100.7 | 83.3 | 172.1 |

By branch (points a trade, count, share of trades positive):

| branch | trades | mean | win share |
| --- | ---: | ---: | ---: |
| other_session | 7684 | 3.54 | 0.46 |
| internal_rotation | 5121 | 1.92 | 0.55 |
| judas_reversal | 4925 | 8.08 | 0.38 |
| single_extended | 892 | 8.90 | 0.36 |
| extension_reaction | 526 | -2.92 | 0.24 |
| single_purged | 308 | 12.63 | 0.46 |
| judas_outbound | 235 | -0.36 | 0.14 |

By fill mode:

| mode | trades | mean | win share |
| --- | ---: | ---: | ---: |
| stop_at_line | 14277 | 5.45 | 0.43 |
| two_minute_close | 3808 | 3.50 | 0.54 |
| signature_close | 592 | 3.16 | 0.58 |
| rejection_block | 299 | -3.81 | 0.30 |
| next_bar_open | 290 | -12.29 | 0.04 |
| failure_close | 163 | -8.11 | 0.57 |
| absorption | 145 | -0.41 | 0.11 |
| orderblock | 82 | -4.13 | 0.26 |
| rejection_close | 35 | 13.68 | 0.97 |

### JJ-TBR, policy E5: 1719 sessions, 19749 trades (11.5 a session)

| list | points a session | median session | sessions positive |
| --- | ---: | ---: | ---: |
| every executed trade | 60.3 | 28.5 | 0.62 |
| hindsight best 1 a session | 53.4 | 43.2 | 0.95 |
| hindsight best 2 | 90.4 | 74.5 | 0.94 |
| hindsight best 3 | 113.4 | 92.1 | 0.93 |
| winners only (a perfect filter) | 169.2 | 120.4 | 0.95 |

By year (points a session, every trade / best 1 / best 3):

| year | sessions | every trade | best 1 | best 3 |
| --- | ---: | ---: | ---: | ---: |
| 2020 | 257 | 55.0 | 43.3 | 95.7 |
| 2021 | 258 | 39.7 | 40.1 | 84.9 |
| 2022 | 258 | 59.6 | 59.8 | 131.5 |
| 2023 | 257 | 46.9 | 38.9 | 83.1 |
| 2024 | 259 | 49.9 | 48.3 | 100.9 |
| 2025 | 257 | 76.3 | 63.9 | 135.0 |
| 2026 | 173 | 111.8 | 92.2 | 187.2 |

By branch (points a trade, count, share of trades positive):

| branch | trades | mean | win share |
| --- | ---: | ---: | ---: |
| other_session | 7773 | 4.26 | 0.44 |
| internal_rotation | 5108 | 3.59 | 0.56 |
| judas_reversal | 4910 | 8.30 | 0.36 |
| single_extended | 892 | 9.13 | 0.36 |
| extension_reaction | 524 | -2.52 | 0.19 |
| single_purged | 307 | 15.14 | 0.46 |
| judas_outbound | 235 | 0.00 | 0.14 |

By fill mode:

| mode | trades | mean | win share |
| --- | ---: | ---: | ---: |
| stop_at_line | 14350 | 6.55 | 0.42 |
| two_minute_close | 3797 | 3.74 | 0.54 |
| signature_close | 592 | 3.36 | 0.58 |
| rejection_block | 297 | -3.08 | 0.24 |
| next_bar_open | 290 | -12.53 | 0.04 |
| failure_close | 161 | -12.44 | 0.63 |
| absorption | 145 | 0.88 | 0.09 |
| orderblock | 82 | -6.49 | 0.20 |
| rejection_close | 35 | 13.68 | 0.97 |

### The authors' reproduced tickets under our fills

| ticket | family | printed | our entry | executed? | E0 | E5 |
| --- | --- | --- | --- | --- | ---: | ---: |
| JJ-2025-01-28 09:53:46 | JJ-TBR | long 21241.75 | 21242.0 | no (not on the executed list) |  |  |
| JJ-2025-05-23-LONDON 02:20 | JJ-TBR | long 21108.5 | 21107.25 | no (not on the executed list) |  |  |
| JJ-2025-09-09 10:35 | JJ-TBR | long None | 23747.245 | no (not on the executed list) |  |  |
| JJ-2025-10-01 09:45 | JJ-TBR | short None | 24805.5 (stop_at_line) | yes | -15.50 | -15.50 |
| JJ-2025-10-03 10:10 | JJ-TBR | long 25091.45 | 25103.0 (stop_at_line) | yes | -10.50 | -10.50 |
| JJ-2025-10-06-LONDON 03:40 | JJ-TBR | long None | 25065.1875 | no (not on the executed list) |  |  |
| JJ-2025-10-07-LONDON 04:30 | JJ-TBR | long None | 25138.4375 (stop_at_line) | yes | -32.31 | -32.31 |
| JJ-2025-10-08-LONDON 03:00-04:00 | JJ-TBR | long None | 25043.1875 (stop_at_line) | yes | 16.06 | 16.06 |
| JJ-2025-10-13 09:05 | JJ-TBR | short 24848.5 | 24850.0 | no (not on the executed list) |  |  |
| JJ-2025-10-13 09:40 | JJ-TBR | long 24768.5 | 24733.0 (stop_at_line) | yes | 69.25 | 69.25 |
| JJ-2025-11-10 10:15 | JJ-TBR | short None | 25624.5 (rejection_block) | yes | -27.25 | -27.25 |
| JJ-2025-11-18 11:00 | JJ-TBR | long None | 24395.25 (absorption) | yes | -15.25 | -15.25 |
| JJ-2025-12-30 09:45-09:47 | JJ-TBR | long 25690.0 | 25684.75 (stop_at_line) | yes | -4.00 | -4.00 |
| JJ-2026-01-02 09:22 | JJ-TBR | long None | 25658.295 (stop_at_line) | yes | -6.54 | -6.54 |
| JJ-2026-01-09 09:32 | JJ-TBR | long 25664.25 | 25680.485 (stop_at_line) | yes | -23.48 | -23.48 |
| JJ-2026-02-24 09:38 | JJ-TBR | long None | 24795.25 (stop_at_line) | yes | -32.00 | -32.00 |
| JJ-2026-07-06 10:45 | JJ-TBR | short None | 30061.3525 | no (not on the executed list) |  |  |
| JJ-2026-07-10 11:05 | JJ-TBR | long 29809.0 | 29816.25 (signature_close) | yes | -17.25 | -17.25 |
| JJ-2026-07-16 09:35 | JJ-TBR | short 29451.5 | 29461.125 (stop_at_line) | yes | -6.12 | -6.12 |
| JJ-2026-07-27 09:02 | JJ-TBR | short 28685.75 | 28693.625 (stop_at_line) | yes | 64.12 | 64.12 |
| JJ-2026-07-28 09:35 | JJ-TBR | short None | 27894.375 | no (not on the executed list) |  |  |
| JJ-2026-08-28 09:31 | JJ-TBR | long 29592.0 | 29578.25 (stop_at_line) | yes | 50.00 | 50.00 |
| JJ-2026-09-01 09:40 | JJ-TBR | long 29074.25 | 29077.535 (stop_at_line) | yes | -17.79 | -17.79 |
| GB-2025-11-20 10:05 | GB-FAIL | short 25301.75 | 25291.5 (at_level) | yes | -11.00 | -11.00 |
| GB-2025-11-19 09:35 | GB-FAIL | long 24625.0 | 24626.0 (post_open_retest) | yes | -25.50 | -25.50 |
| GB-2026-04-23 12:35-12:36 | GB-FAIL | short 27116.25 | 27110.75 | no (not on the executed list) |  |  |
| GB-2026-04-28 09:30 | GB-FAIL | long None | 27085.0 (next_bar_open) | yes | 82.75 | -23.50 |
| GB-2026-04-28 09:45-09:50 | GB-FAIL | short None | 27179.75 | no (not on the executed list) |  |  |
| GB-2026-07-13 20:40 | GB-FAIL | long 29414.25 | 29393.25 (at_level) | yes | 131.50 | -14.00 |
| GB-2026-07-29-30 22:04-22:25 | GB-FAIL | short 27644.5 | 27640.75 (pocket_retest_after_failure) | yes | 78.75 | -118.00 |
| GB-2026-07-29-30 04:00 (07-30) | GB-FAIL | long 27359.75 | 27351.25 | no (not on the executed list) |  |  |
| GB-2026-08-11-12 20:01-20:13 | GB-FAIL | long 29635.75 | 29631.75 (at_level) | yes | 36.00 | 248.50 |
| GB-2026-08-13 11:20-11:27 | GB-FAIL | short 30227.5 | 30225.25 | no (not on the executed list) |  |  |
| GB-2026-08-27 11:21-11:24 | GB-FAIL | short 29613.75 | 29618.5 | no (not on the executed list) |  |  |
| GB-2026-08-27 12:50-12:56 | GB-FAIL | short 29642.25 | 29643.25 | no (not on the executed list) |  |  |
| GB-2026-08-28 10:05 | GB-FAIL | short 29674.25 | 29704.5 (post_open_retest) | yes | -8.00 | -8.00 |
| GB-2026-08-31 09:33 | GB-FAIL | short 29510.5 | 29506.75 (next_bar_open) | yes | 128.00 | 128.00 |
| GB-2026-09-01 12:05 | GB-FAIL | short 29253.75 | 29273.5 (at_level) | yes | 6.50 | 6.50 |
| GB-2026-09-03 00:32-00:35 | GB-FAIL | short 29238.25 | 29243.0 (at_level) | yes | 123.75 | 123.75 |
| GB-2026-04-16 10:00-10:20 | GB-FAIL | long 26336.75 | 26339.5 (approach_reject) | yes | -26.25 | -26.25 |
| JJ-2026-05-20 09:39 | JJ-TBR | long 29028.0 | 29028.6025 (stop_at_line) | yes | 86.15 | 86.15 |
| JJ-2026-05-20 09:46 | JJ-TBR | short 29170.0 | 29169.25 (stop_at_line) | yes | 49.25 | 49.25 |
| JJ-2025-10-14 09:45-09:55 | JJ-TBR | long 24420.0 | 24421.25 | no (not on the executed list) |  |  |
| GB-2026-05-01 10:40-11:16 | GB-FAIL | short 27901.5 | 27875.75 (at_level) | yes | 4.75 | -36.00 |
| GB-2026-05-04 10:55-11:12 | GB-FAIL | short 27900.75 | 27917.0 (post_open_retest) | yes | -4.25 | -4.25 |

Detected tickets 45; on the executed list 31. Mean points a ticket: E0 20.8 over 31, E5 11.8 over 31.

