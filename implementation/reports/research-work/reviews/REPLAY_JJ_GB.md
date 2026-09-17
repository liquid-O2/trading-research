# Author-example replay, source-faithful rebuild (B0.3-2026-09-17)

Entries only: an example is detected when every proper entry on it is reproduced on the
author's play and side, within one five-minute bar of the printed time and within the
stated price tolerance. `tol` is the ticket's own printed risk (|stop - entry|), or 27
points (the median printed stop) where the ticket prints no stop. `strict_10` is the owner's
rule of 2026-09-17: within ten points of the printed price on the right bar AND on the
author's framework -- same play, same branch, same side, and a fill mode the source or
the tickets support. `+/-5` is the previous rule, kept so the change stays visible.

- proper entries inside the tape: 40
- detected (ticket-risk tolerance): 32
- **reproduced (strict_10: +/-10 points, right bar, the author's play, branch, side and a supported fill mode): 28**
- reproduced under the old +/-5 rule: 24
- detected within three five-minute bars of the printed time: 33
- **reproduced by the SELECTED trade list (strict_10): 3**
- reproduced by the selected trade list (+/-5): 3
- reproduced by the selected trade list (ticket-risk): 4
- reproduced by the selected trade list (three bars): 4
- the day read named the author's play as PRIMARY on: 15
- selected-list strict if the primary play is set to the author's: 7
- outside the tape: 9

## By family

`any fill` scores every fill of every passing episode; `selected` scores only the
trade list the family would actually have taken that session (the day's primary play,
the first qualifying setup, one position at a time, at most three entries). The
acceptance bar is the SELECTED column.

| family | proper entries | selected strict_10 | selected +/-5 | selected 3 bars | any-fill strict_10 | any-fill +/-5 | any-fill ticket-risk |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GB | 16 | **0** | 0 | 0 | 5 | 3 | 9 |
| JJ-TBR | 24 | **3** | 3 | 4 | 23 | 21 | 23 |
| both | 40 | **3** | 3 | 4 | 28 | 24 | 32 |

## Every entry

| example | session | play (ours / author) | branch | side | printed | framework fill | d | bars | strict_10 | +/-5 | sel fill | sel d | sel strict_10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `JJ-2025-01-28` | 2025-01-28 | double_break / double_break | judas_reversal | long | 21241.75 @09:53:46 | 21242.0 | 0.25 | 0.2 | True | True | 21295.875 | 54.125 | False |
| `JJ-2025-05-23-LONDON` | 2025-05-23 | london / london | other_session | long | 21108.5 @02:20 | 21107.25 | 1.25 | 0.8 | True | True | None | None | False |
| `JJ-2025-09-09` | 2025-09-09 | double_break / double_break | extension_reaction | long | 23743.5 @10:35 | 23747.245 | 3.745 | 2.2 | True | True | 23747.245 | 3.745 | True |
| `JJ-2025-10-01` | 2025-10-01 | double_break / double_break | judas_reversal | short | 24845.0 @09:45 | 24837.0 | 8.0 | 1.4 | True | True | 24782.25 | 62.75 | False |
| `JJ-2025-10-03` | 2025-10-03 | double_break / double_break | judas_reversal | long | 25091.45 @10:10 | 25088.5 | 2.95 | 1.8 | True | True | None | None | False |
| `JJ-2025-10-06-LONDON` | 2025-10-06 | london / london | other_session | long | 25066.0 @03:40 | 25068.25 | 2.25 | 3.0 | True | True | None | None | False |
| `JJ-2025-10-07-LONDON` | 2025-10-07 | london / london | other_session | long | 25140.0 @04:30 | 25138.0 | 2.0 | 1.8 | True | True | None | None | False |
| `JJ-2025-10-08-LONDON` | 2025-10-08 | london / london | other_session | long | 25028.0 @03:00-04:00 | 25045.5 | 17.5 | 0.0 | True | True | None | None | False |
| `JJ-2025-10-13` | 2025-10-13 | double_break / double_break | judas_reversal | short | 24848.5 @09:05 | 24850.0 | 1.5 | 1.4 | True | True | 24853.25 | 4.75 | True |
| `JJ-2025-10-13` | 2025-10-13 | double_break / double_break | judas_reversal | long | 24768.5 @09:40 | 24773.75 | 5.25 | 0.8 | True | False | 24841.5625 | 73.0625 | False |
| `JJ-2025-11-10` | 2025-11-10 | double_break / double_break | extension_reaction | short | 25635.0 @10:15 | 25632.15 | 2.85 | 0.0 | True | True | None | None | False |
| `JJ-2025-11-18` | 2025-11-18 | double_break / double_break | extension_reaction | long | 24420.0 @11:00 | 24423.7575 | 3.7575 | 0.6 | True | True | None | None | False |
| `JJ-2025-12-30` | 2025-12-30 | double_break / double_break | judas_reversal | long | 25690.0 @09:45-09:47 | 25691.25 | 1.25 | 2.8 | True | True | 25691.25 | 1.25 | True |
| `JJ-2026-01-02` | 2026-01-02 | pzone / pzone | timed_pzone_reversal | long | 25663.0 @09:22 | 25663.0 | 0.0 | 2.8 | True | True | None | None | False |
| `JJ-2026-01-09` | 2026-01-09 | pzone / pzone | timed_pzone_reversal | long | 25664.25 @09:32 | 25660.0 | 4.25 | 0.8 | True | True | None | None | False |
| `JJ-2026-02-24` | 2026-02-24 | double_break / double_break | judas_reversal | long | 24795.0 @09:38 | 24795.0 | 0.0 | 1.2 | True | True | None | None | False |
| `JJ-2026-06-05-LONDON` | 2026-06-05 | london / london | other_session | long | 30066.5 @03:20 | 30098.5 | 32.0 | 1.0 | False | False | None | None | False |
| `JJ-2026-07-06` | 2026-07-06 | double_break / double_break | extension_reaction | short | 30065.0 @10:45 | 30061.3525 | 3.6475 | 2.8 | True | True | 29858.25 | 206.75 | False |
| `JJ-2026-07-10` | 2026-07-10 | big_range_eq / big_range_eq | internal_rotation | long | 29809.0 @11:05 | 29808.0 | 1.0 | 0.4 | True | True | None | None | False |
| `JJ-2026-07-16` | 2026-07-16 | single_break / single_break | single_extended | short | 29451.5 @09:35 | 29457.0 | 5.5 | 1.6 | True | False | 29384.75 | 66.75 | False |
| `JJ-2026-07-27` | 2026-07-27 | single_break / single_break | single_extended | short | 28685.75 @09:02 | 28683.0 | 2.75 | 0.2 | True | True | None | None | False |
| `JJ-2026-07-28` | 2026-07-28 | single_break / single_break | single_purged | short | None @09:35 | 27940.5 | None | 0.4 | True | True | 27986.625 | None | False |
| `JJ-2026-08-28` | 2026-08-28 | double_break / double_break | judas_reversal | long | 29592.0 @09:31 | 29593.25 | 1.25 | 1.0 | True | True | None | None | False |
| `JJ-2026-09-01` | 2026-09-01 | double_break / double_break | judas_reversal | long | 29074.25 @09:40 | 29077.535 | 3.285 | 1.2 | True | True | None | None | False |
| `GB-2025-11-20` | 2025-11-20 | ny_box_fail / ny_box_fail | nyam_box | short | 25301.75 @10:05 | 25291.5 | 10.25 | 0.6 | False | False | None | None | False |
| `GB-2025-11-19` | 2025-11-19 | weekly_level / weekly_level | prior_week_level | long | 24625.0 @09:35 | 24626.0 | 1.0 | 0.8 | True | True | None | None | False |
| `GB-2026-04-23` | 2026-04-23 | previous_hour_fail / previous_hour_fail | previous_hour | short | None @13:00 | None | None | None | False | False | None | None | False |
| `GB-2026-04-28` | 2026-04-28 | ny_box_fail / ny_box_fail | nyam_box | long | None @09:30 | None | None | None | False | False | None | None | False |
| `GB-2026-04-28` | 2026-04-28 | ny_box_fail / ny_box_fail | nyam_box | short | None @09:45-09:50 | 27166.75 | None | 1.0 | True | True | None | None | False |
| `GB-2026-07-13` | 2026-07-14 | overnight_reclaim / overnight_reclaim | prior_day_level | long | 29414.25 @20:40 | 29420.75 | 6.5 | 2.0 | True | False | 29401.0 | 13.25 | False |
| `GB-2026-07-29-30` | 2026-07-30 | pocket_continuation / pocket_continuation | golden_pocket | short | 27644.5 @22:20 | None | None | None | False | False | None | None | False |
| `GB-2026-07-29-30` | 2026-07-30 | london_reclaim / london_reclaim | london_box | long | 27359.75 @04:00 (07-30) | 27351.25 | 8.5 | 0.8 | True | False | None | None | False |
| `GB-2026-08-11-12` | 2026-08-12 | ny_box_fail / ny_box_fail | nyam_box | long | 29635.75 @20:40 | None | None | None | False | False | None | None | False |
| `GB-2026-08-13` | 2026-08-13 | previous_hour_fail / previous_hour_fail | previous_hour | short | 30227.5 @11:30 | None | None | None | False | False | None | None | False |
| `GB-2026-08-27` | 2026-08-27 | ny_box_fail / ny_box_fail | nyam_box | short | 29613.75 @11:30 | 29597.5 | 16.25 | 1.0 | False | False | None | None | False |
| `GB-2026-08-27` | 2026-08-27 | ny_box_fail / ny_box_fail | nyam_box | short | 29642.25 @13:00 | None | None | None | False | False | None | None | False |
| `GB-2026-08-28` | 2026-08-28 | ny_box_fail / ny_box_fail | nyam_box | short | 29674.25 @10:05 | 29629.0 | 45.25 | 0.0 | False | False | None | None | False |
| `GB-2026-08-31` | 2026-08-31 | cash_open / cash_open | cash_open_reclaim_case | short | 29510.5 @09:33 | 29506.75 | 3.75 | 0.0 | True | True | None | None | False |
| `GB-2026-09-01` | 2026-09-01 | overnight_reclaim / overnight_reclaim | prior_day_level | short | 29253.75 @11:45 | 29273.5 | 19.75 | 0.6 | False | False | 29545.75 | 292.0 | False |
| `GB-2026-09-03` | 2026-09-03 | asia_fade / asia_fade | asia_tdo_case | short | 29238.25 @00:45 | None | None | None | False | False | None | None | False |
| `GB-2026-09-08` | 2026-09-08 | None / asia_fade | None | short | 29730.5 @00:55 | None | None | None | None | None | None | None | None |
| `GB-2026-09-08` | 2026-09-08 | None / ny_box_fail | None | long | 29469.25 @10:00 | None | None | None | None | None | None | None | None |
| `GB-2026-09-11` | 2026-09-11 | None / overnight_reclaim | None | long | 29059.5 @00:15 | None | None | None | None | None | None | None | None |
| `GB-2026-09-11` | 2026-09-11 | None / pocket_continuation | None | long | 29382.0 @10:00 | None | None | None | None | None | None | None | None |
| `GB-2026-09-14` | 2026-09-14 | None / london_reclaim | None | long | 28903.75 @09:40 | None | None | None | None | None | None | None | None |
| `GB-2026-09-14` | 2026-09-14 | None / asia_fade | None | short | 29081.5 @10:10 | None | None | None | None | None | None | None | None |
| `GB-2026-09-15` | 2026-09-15 | None / ny_box_fail | None | short | 29441.5 @10:05 | None | None | None | None | None | None | None | None |
| `GB-2026-09-15` | 2026-09-15 | None / london_reclaim | None | long | 29244.75 @11:05 | None | None | None | None | None | None | None | None |
| `GB-2026-09-15` | 2026-09-15 | None / ny_box_fail | None | long | 29215.5 @15:35 | None | None | None | None | None | None | None | None |

## Every remaining miss under strict_10, with its cause

A miss is admissible only if it names the exact input that differs.

| example | printed | ours | d(pts) | bars / allowed | cause | input limit? |
| --- | --- | --- | ---: | --- | --- | --- |
| `JJ-2026-06-05-LONDON` 03:20 | 30066.5 | 30098.5 | 32.0 | 1.0 / 3.0 | his London box R-Lo 30,162 / R-Hi 30,222 is not a range of our tape; no window of 1-5 hours between 18:00 and 06:00 reproduces both edges within 5 points (best 01:05-02:05 ET: 30,163.00 / 30,228.25) | yes |
| `GB-2025-11-20` 10:05 | 25301.75 | 25291.5 | 10.25 | 0.6 / 3.0 | his 09:00-10:00 box high is 25,301.75; our tape's high over that hour is 25,292.00 and it does not trade 25,301.75 until 10:37 | yes |
| `GB-2026-04-23` 13:00 | None | 27145.75 | None | 17.0 / 1.0 | the proper-entry action carries no price (his 27,116.25 sits on the following action of the same ticket), so the test is play + side + time; no previous_hour fill of ours falls in the one-bar window and the nearest is 17 bars away | no -- the record omits the price on the proper-entry action |
| `GB-2026-04-28` 09:30 | None | 27112.5 | None | 13.4 / 3.0 | the developing box low is a reference now, but our tape has no sweep of it at 09:30 | no |
| `GB-2026-07-29-30` 22:20 | 27644.5 | 27650.75 | 6.25 | 14.2 / 1.0 | our near pocket line is 27,650.75; his own printed pocket lines are 27,652 and 27,718, so his fill is 7.5 points from his own nearest line -- a +/-5 match to any level-based rule is arithmetically impossible on this ticket | yes |
| `GB-2026-08-11-12` 20:40 | 29635.75 | 29650.5 | 14.75 | 5.0 / 1.0 | our previous-session 09:00-10:00 box low is 29,631.75 against his 29,635 -- inside strict -- but our tape last trades that level at 20:14, 26 minutes before his stamp | yes |
| `GB-2026-08-13` 11:30 | 30227.5 | 30192.75 | 34.75 | 12.4 / 1.0 | CORRECTED 2026-09-17: this is NOT a tape limit. His 30,238 poke IS on our tape -- the 11:24 bar prints H 30,238.75 -- and our 10:00-11:00 box high is 30,267.50 (his tops[0] 30,258). His 30,227.50 is a lower-high rejection about 29 points UNDER the previous-hour high, not a sweep of it, so the miss is our mechanism, not the data | no -- a mechanism miss (discretion) |
| `GB-2026-08-27` 11:30 | 29613.75 | 29597.5 | 16.25 | 1.0 / 1.0 | our 10:00-11:00 box high 29,623.50 matches his 29,620 and the one-minute failure close 29,618.50 is 4.75 from his fill, but it prints at 11:21, 1.8 bars early | no |
| `GB-2026-08-27` 13:00 | 29642.25 | 29639.0 | 3.25 | 3.8 / 1.0 | price is now within 3.25 points on the author's branch; the fill prints 3.8 bars early against the one-bar allowance for a ticket time | no -- a timing miss only |
| `GB-2026-08-28` 10:05 | 29674.25 | 29687.25 | 13.0 | 0.8 / 1.0 | after the running-reference fix our 09:00-10:00 box high is 29,703.25 (his 29,708.75) and the nyam_box fill is 29,687.25, 13.00 points out; the nearest fill of all is the True Day Open at 29,668.00 (6.25) on asia_tdo_case, which the framework rule cannot count against a nyam_box entry. Our 00:00 bar opens 29,668.00 against his drawn 29,674 | yes, and a record question: his reference line names the box high but his fill is at the TDO |
| `GB-2026-09-01` 11:45 | 29253.75 | 29273.5 | 19.75 | 0.6 / 1.0 | CORRECTED 2026-09-17: his 29,253.75 DOES print on our tape, at 11:38 (low 29,253.50) -- seven minutes before his printed 11:45, where our tape is 29,286-29,295. Our PDL 29,273.50 matches his 29,270. The miss stands but the reason is a clock or feed inconsistency in the ticket, not an absent price | yes -- but as a ticket clock inconsistency, not a missing price |
| `GB-2026-09-03` 00:45 | 29238.25 | 29227.75 | 10.5 | 3.0 / 1.0 | CORRECTED 2026-09-17: the loader reads data/quantpad/cme__nq-continuous-futures__mbp-1/2026-09.parquet (the MBP-1 tick file), not the 1-minute file that ends 2026-09-02 11:19, so the session is fully covered. Re-verified: the high over 00:38-00:52 is 29,229.00, 9.25 points under his 29,238.25 -- INSIDE the ten-point rule -- so this is a mechanism miss, not an input limit: no episode of ours is on the right branch and mode in that window | no -- a mechanism miss |

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
