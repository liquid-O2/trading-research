# Author-example replay, source-faithful rebuild (B0.3-2026-09-17)

Entries only: an example is detected when every proper entry on it is reproduced on the
author's play and side, within one five-minute bar of the printed time and within the
stated price tolerance. `tol` is the ticket's own printed risk (|stop - entry|), or 27
points (the median printed stop) where the ticket prints no stop. `strict_10` is the owner's
rule of 2026-09-17: within ten points of the printed price on the right bar AND on the
author's framework -- same play, same branch, same side, and a fill mode the source or
the tickets support. `+/-5` is the previous rule, kept so the change stays visible.

- proper entries inside the tape: 40
- detected (ticket-risk tolerance): 39
- **reproduced (strict_10: +/-10 points, right bar, the author's play, branch, side and a supported fill mode): 39**
- reproduced under the old +/-5 rule: 33
- detected within three five-minute bars of the printed time: 39
- **reproduced by the CANDIDATE list (strict_10): 30** (every opportunity the framework admits, once; mean 12.2 a day)
- reproduced by the EXECUTED list (one position at a time, adds and flips): 30 (mean 14.9 fills / 11.4 round trips a day)
- reproduced by the selected trade list (+/-5): 27
- reproduced by the selected trade list (ticket-risk): 30
- reproduced by the selected trade list (three bars): 31
- the day read named the author's play as PRIMARY on: 19
- selected-list strict if the primary play is set to the author's: 29
- outside the tape: 9

## By family

`any fill` scores every fill of every passing episode. `candidates` scores the
CANDIDATE list: every opportunity the family's framework admits that session, once
(per segment and play; at most two or three trades on one line; no position
bookkeeping) -- the list the author chooses from. `executed` scores the one-position-
at-a-time list with the family's adds and flips. The acceptance bar is the
CANDIDATE column; the mean list sizes a day are printed beside it so the author's
one to three trades a day can be compared with what the framework admits.

| family | proper entries | candidates strict_10 | executed strict_10 | candidates +/-5 | candidates 3 bars | any-fill strict_10 | any-fill +/-5 | any-fill ticket-risk | mean candidates / day | mean executed fills / day | mean round trips / day |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GB | 16 | **11** | 11 | 9 | 12 | 16 | 11 | 16 | 15.4 | 18.0 | 14.3 |
| JJ-TBR | 24 | **19** | 19 | 18 | 19 | 23 | 22 | 23 | 10.0 | 12.8 | 9.5 |
| both | 40 | **30** | 30 | 27 | 31 | 39 | 33 | 39 | 12.2 | 14.9 | 11.4 |

## Every entry

| example | session | play (ours / author) | branch | side | printed | framework fill | d | bars | strict_10 | +/-5 | candidate fill | cand d | cand strict_10 | exec strict_10 | candidates / executed / round trips |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `JJ-2025-01-28` | 2025-01-28 | double_break / double_break | judas_reversal | long | 21241.75 @09:53:46 | 21242.0 | 0.25 | 0.2 | True | True | 21242.0 | 0.25 | True | True | 8 / 8 / 8 |
| `JJ-2025-05-23-LONDON` | 2025-05-23 | london / london | other_session | long | 21108.5 @02:20 | 21107.25 | 1.25 | 0.8 | True | True | 21107.25 | 1.25 | True | True | 12 / 12 / 10 |
| `JJ-2025-09-09` | 2025-09-09 | double_break / double_break | extension_reaction | long | 23743.5 @10:35 | 23747.245 | 3.745 | 2.2 | True | True | 23790.75 | 47.25 | False | False | 12 / 19 / 12 |
| `JJ-2025-10-01` | 2025-10-01 | double_break / double_break | judas_reversal | short | 24845.0 @09:45 | 24805.5 | 39.5 | 2.6 | True | True | 24805.5 | 39.5 | True | True | 12 / 16 / 11 |
| `JJ-2025-10-03` | 2025-10-03 | double_break / double_break | judas_reversal | long | 25091.45 @10:10 | 25088.5 | 2.95 | 1.8 | True | True | 25088.5 | 2.95 | True | True | 8 / 9 / 8 |
| `JJ-2025-10-06-LONDON` | 2025-10-06 | london / london | other_session | long | 25066.0 @03:40 | 25065.1875 | 0.8125 | 0.8 | True | True | 25079.875 | 13.875 | True | True | 7 / 7 / 6 |
| `JJ-2025-10-07-LONDON` | 2025-10-07 | london / london | other_session | long | 25140.0 @04:30 | 25138.4375 | 1.5625 | 0.6 | True | True | 25154.375 | 14.375 | False | False | 8 / 8 / 7 |
| `JJ-2025-10-08-LONDON` | 2025-10-08 | london / london | other_session | long | 25028.0 @03:00-04:00 | 25043.1875 | 15.1875 | 0.0 | True | True | 25043.1875 | 15.1875 | True | True | 8 / 10 / 8 |
| `JJ-2025-10-13` | 2025-10-13 | double_break / double_break | judas_reversal | short | 24848.5 @09:05 | 24850.0 | 1.5 | 1.4 | True | True | 24850.0 | 1.5 | True | True | 12 / 14 / 12 |
| `JJ-2025-10-13` | 2025-10-13 | double_break / double_break | judas_reversal | long | 24768.5 @09:40 | 24769.1875 | 0.6875 | 0.2 | True | True | 24769.1875 | 0.6875 | True | True | 12 / 14 / 12 |
| `JJ-2025-11-10` | 2025-11-10 | double_break / double_break | extension_reaction | short | 25635.0 @10:15 | 25632.15 | 2.85 | 0.0 | True | True | 25632.15 | 2.85 | True | True | 11 / 12 / 9 |
| `JJ-2025-11-18` | 2025-11-18 | double_break / double_break | extension_reaction | long | 24420.0 @11:00 | 24423.7575 | 3.7575 | 0.6 | True | True | 24423.7575 | 3.7575 | True | True | 8 / 9 / 8 |
| `JJ-2025-12-30` | 2025-12-30 | double_break / double_break | judas_reversal | long | 25690.0 @09:45-09:47 | 25690.75 | 0.75 | 0.2 | True | True | 25691.25 | 1.25 | True | True | 12 / 14 / 12 |
| `JJ-2026-01-02` | 2026-01-02 | double_break / double_break | judas_reversal | long | 25663.0 @09:22 | 25658.295 | 4.705 | 2.6 | True | True | 25658.295 | 4.705 | True | True | 12 / 19 / 12 |
| `JJ-2026-01-09` | 2026-01-09 | double_break / double_break | judas_reversal | long | 25664.25 @09:32 | 25664.25 | 0.0 | 0.2 | True | True | 25664.25 | 0.0 | True | True | 12 / 14 / 11 |
| `JJ-2026-02-24` | 2026-02-24 | double_break / double_break | judas_reversal | long | 24795.0 @09:38 | 24795.25 | 0.25 | 1.4 | True | True | 24795.25 | 0.25 | True | True | 12 / 19 / 12 |
| `JJ-2026-06-05-LONDON` | 2026-06-05 | london / london | other_session | long | 30066.5 @03:20 | 30105.1875 | 38.6875 | 2.6 | False | False | 30106.5 | 40.0 | False | False | 7 / 7 / 7 |
| `JJ-2026-07-06` | 2026-07-06 | double_break / double_break | extension_reaction | short | 30065.0 @10:45 | 30061.3525 | 3.6475 | 2.8 | True | True | 29936.0 | 129.0 | False | False | 11 / 15 / 11 |
| `JJ-2026-07-10` | 2026-07-10 | big_range_eq / big_range_eq | internal_rotation | long | 29809.0 @11:05 | 29808.0 | 1.0 | 0.4 | True | True | None | None | False | False | 12 / 26 / 11 |
| `JJ-2026-07-16` | 2026-07-16 | single_break / single_break | single_extended | short | 29451.5 @09:35 | 29457.0 | 5.5 | 1.6 | True | False | 29457.0 | 5.5 | True | True | 8 / 8 / 8 |
| `JJ-2026-07-27` | 2026-07-27 | single_break / single_break | single_extended | short | 28685.75 @09:02 | 28683.75 | 2.0 | 0.0 | True | True | 28683.75 | 2.0 | True | True | 10 / 10 / 8 |
| `JJ-2026-07-28` | 2026-07-28 | single_break / single_break | single_purged | short | None @09:35 | 27894.375 | None | 0.6 | True | True | 27986.625 | None | True | True | 6 / 7 / 6 |
| `JJ-2026-08-28` | 2026-08-28 | double_break / double_break | judas_reversal | long | 29592.0 @09:31 | 29592.0 | 0.0 | 0.6 | True | True | 29592.0 | 0.0 | True | True | 12 / 22 / 12 |
| `JJ-2026-09-01` | 2026-09-01 | double_break / double_break | judas_reversal | long | 29074.25 @09:40 | 29075.25 | 1.0 | 1.2 | True | True | 29075.25 | 1.0 | True | True | 9 / 9 / 6 |
| `GB-2025-11-20` | 2025-11-20 | ny_box_fail / ny_box_fail | nyam_box | short | 25301.75 @10:05 | 25291.5 | 10.25 | 0.8 | True | False | 25291.5 | 10.25 | True | False | 15 / 15 / 14 |
| `GB-2025-11-19` | 2025-11-19 | weekly_level / weekly_level | prior_week_level | long | 24625.0 @09:35 | 24626.0 | 1.0 | 0.8 | True | True | 24626.0 | 1.0 | True | True | 18 / 23 / 18 |
| `GB-2026-04-23` | 2026-04-23 | previous_hour_fail / previous_hour_fail | previous_hour | short | 27116.25 @12:35-12:36 | 27110.75 | 5.5 | 0.2 | True | False | 27106.25 | 10.0 | False | True | 18 / 21 / 17 |
| `GB-2026-04-28` | 2026-04-28 | ny_box_fail / cash_open | nyam_box | long | None @09:30 | 27139.5 | None | 1.0 | True | True | 27137.5 | None | True | True | 15 / 20 / 15 |
| `GB-2026-04-28` | 2026-04-28 | ny_box_fail / ny_box_fail | nyam_box | short | None @09:45-09:50 | 27179.75 | None | 1.8 | True | True | 27222.75 | None | False | False | 15 / 20 / 15 |
| `GB-2026-07-13` | 2026-07-14 | overnight_reclaim / overnight_reclaim | prior_day_level | long | 29414.25 @20:40 | 29412.0 | 2.25 | 2.8 | True | True | 29412.0 | 2.25 | True | True | 15 / 12 / 10 |
| `GB-2026-07-29-30` | 2026-07-30 | pocket_continuation / pocket_continuation | golden_pocket | short | 27644.5 @22:04-22:25 | 27640.75 | 3.75 | 0.0 | True | True | 27640.75 | 3.75 | True | True | 14 / 21 / 14 |
| `GB-2026-07-29-30` | 2026-07-30 | london_reclaim / london_reclaim | london_box | long | 27359.75 @04:00 (07-30) | 27351.25 | 8.5 | 0.2 | True | False | None | None | False | False | 14 / 21 / 14 |
| `GB-2026-08-11-12` | 2026-08-12 | ny_box_fail / ny_box_fail | nyam_box | long | 29635.75 @20:01-20:13 | 29635.25 | 0.5 | 0.0 | True | True | 29635.25 | 0.5 | True | True | 18 / 23 / 16 |
| `GB-2026-08-13` | 2026-08-13 | ny_box_fail / previous_hour_fail | nyam_box | short | 30227.5 @11:20-11:27 | 30225.25 | 2.25 | 0.0 | True | True | 30231.0 | 3.5 | True | False | 16 / 19 / 16 |
| `GB-2026-08-27` | 2026-08-27 | ny_box_fail / ny_box_fail | nyam_box | short | 29613.75 @11:21-11:24 | 29618.5 | 4.75 | 0.0 | True | True | 29618.5 | 4.75 | True | True | 15 / 16 / 15 |
| `GB-2026-08-27` | 2026-08-27 | previous_hour_fail / ny_box_fail | previous_hour | short | 29642.25 @12:50-12:56 | 29643.25 | 1.0 | 0.4 | True | True | 29639.0 | 3.25 | False | False | 15 / 16 / 15 |
| `GB-2026-08-28` | 2026-08-28 | ny_box_fail / ny_box_fail | nyam_box | short | 29674.25 @10:05 | 29668.0 | 6.25 | 0.6 | True | False | 29668.0 | 6.25 | True | True | 18 / 17 / 13 |
| `GB-2026-08-31` | 2026-08-31 | cash_open / cash_open | cash_open_reclaim_case | short | 29510.5 @09:33 | 29506.75 | 3.75 | 0.0 | True | True | 29506.75 | 3.75 | True | True | 18 / 17 / 16 |
| `GB-2026-09-01` | 2026-09-01 | overnight_reclaim / overnight_reclaim | prior_day_level | short | 29253.75 @12:05 | 29260.25 | 6.5 | 1.0 | True | False | None | None | False | True | 16 / 20 / 16 |
| `GB-2026-09-03` | 2026-09-03 | asia_fade / asia_fade | asia_tdo_case | short | 29238.25 @00:32-00:35 | 29236.5 | 1.75 | 0.6 | True | True | 29236.5 | 1.75 | True | True | 6 / 7 / 5 |
| `GB-2026-09-08` | 2026-09-08 | None / asia_fade | None | short | 29730.5 @00:55 | None | None | None | None | None | None | None | None | None | None / None / None |
| `GB-2026-09-08` | 2026-09-08 | None / ny_box_fail | None | long | 29469.25 @10:00 | None | None | None | None | None | None | None | None | None | None / None / None |
| `GB-2026-09-11` | 2026-09-11 | None / overnight_reclaim | None | long | 29059.5 @00:15 | None | None | None | None | None | None | None | None | None | None / None / None |
| `GB-2026-09-11` | 2026-09-11 | None / pocket_continuation | None | long | 29382.0 @10:00 | None | None | None | None | None | None | None | None | None | None / None / None |
| `GB-2026-09-14` | 2026-09-14 | None / london_reclaim | None | long | 28903.75 @09:40 | None | None | None | None | None | None | None | None | None | None / None / None |
| `GB-2026-09-14` | 2026-09-14 | None / asia_fade | None | short | 29081.5 @10:10 | None | None | None | None | None | None | None | None | None | None / None / None |
| `GB-2026-09-15` | 2026-09-15 | None / ny_box_fail | None | short | 29441.5 @10:05 | None | None | None | None | None | None | None | None | None | None / None / None |
| `GB-2026-09-15` | 2026-09-15 | None / london_reclaim | None | long | 29244.75 @11:05 | None | None | None | None | None | None | None | None | None | None / None / None |
| `GB-2026-09-15` | 2026-09-15 | None / ny_box_fail | None | long | 29215.5 @15:35 | None | None | None | None | None | None | None | None | None | None / None / None |

## Every remaining miss under strict_10, with its cause

A miss is admissible only if it names the exact input that differs.

| example | printed | ours | d(pts) | bars / allowed | cause | input limit? |
| --- | --- | --- | ---: | --- | --- | --- |
| `JJ-2026-06-05-LONDON` 03:20 | 30066.5 | 30105.1875 | 38.6875 | 2.6 / 3.0 | his London box R-Lo 30,162 / R-Hi 30,222 is not a range of our tape; no window of 1-5 hours between 18:00 and 06:00 reproduces both edges within 5 points (best 01:05-02:05 ET: 30,163.00 / 30,228.25) | yes |

## Examples with no proper entry to match

- `JJ-2025-09-12` (JR p.23): the chart narrates levels or shows a P&L card; no fill is marked as the trade
- `JJ-2026-06-09` (JR p.8): the chart narrates levels or shows a P&L card; no fill is marked as the trade
- `JJ-2026-09-02` (JR p.3): the chart narrates levels or shows a P&L card; no fill is marked as the trade

## Other fills on the same charts (neither detections nor misses)

- `JJ-2025-01-28`: 10:27:05 sell 21457.75
- `JJ-2025-05-23-LONDON`: 03:10 buy 21170.5; 03:15 sell 21172.25
- `JJ-2025-09-09`: 11:45 exit 23814
- `JJ-2025-10-03`: 09:55 sell 25119.5; 10:05-10:15 buy 25091.45; 10:05-10:15 buy 25072.75; 10:25 buy 25100; 11:00 buy 25111.5; 11:00 sell 25117; 11:15 sell 25128.75
- `JJ-2026-01-09`: 09:32 stop 25617.25; 09:32 sell_limit 25846.5
- `JJ-2026-06-05-LONDON`: 04:30 sell 30215.25; 05:03 buy 30160.75; 05:14 sell 30215.75
- `JJ-2026-07-10`: later sell_limit 30041.25
- `JJ-2026-07-16`: 09:35 sell 29438; 09:45 buy 29312.25
- `JJ-2026-07-27`: 09:33 add 28578.0; 09:33 add 28550.0; 09:35 buy 28490.75
- `JJ-2026-08-28`: 09:32 sell_limit 29707.25; 09:32 sell_limit 29724.5
- `JJ-2026-09-01`: 09:25 buy 29106.5; 09:35 sell 29112.75; 10:05 sell 29085.5; 10:10 sell 29116.5; 10:32 sell 29196.25; 10:42 sell 29218.5; 11:00 sell 29230.5; 10:40 buy 29204.75
- `GB-2025-11-20`: 11:00 buy_limit 25112.5
- `GB-2026-04-23`: 13:00-14:00 sell 27116.25
- `GB-2026-07-29-30`: 23:30-01:00 sell 27652.25
- `GB-2026-09-08`: NY AM buy 29469.25
