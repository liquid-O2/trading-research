# Author-example replay, source-faithful rebuild (B0.3-2026-09-17)

Entries only: an example is detected when every proper entry on it is reproduced on the
author's play and side, within one five-minute bar of the printed time and within the
stated price tolerance. `tol` is the ticket's own printed risk (|stop - entry|), or 27
points (the median printed stop) where the ticket prints no stop. `strict_10` is the owner's
rule of 2026-09-17: within ten points of the printed price on the right bar AND on the
author's framework -- same play, same branch, same side, and a fill mode the source or
the tickets support. `+/-5` is the previous rule, kept so the change stays visible.

- proper entries inside the tape: 16
- detected (ticket-risk tolerance): 15
- **reproduced (strict_10: +/-10 points, right bar, the author's play, branch, side and a supported fill mode): 14**
- reproduced under the old +/-5 rule: 10
- detected within three five-minute bars of the printed time: 16
- **reproduced by the CANDIDATE list (strict_10): 10** (every opportunity the framework admits, once; mean 17.2 a day)
- reproduced by the EXECUTED list (one position at a time, adds and flips): 9 (mean 20.7 fills / 16.2 round trips a day)
- reproduced by the selected trade list (+/-5): 9
- reproduced by the selected trade list (ticket-risk): 11
- reproduced by the selected trade list (three bars): 13
- the day read named the author's play as PRIMARY on: 3
- selected-list strict if the primary play is set to the author's: 10
- outside the tape: 0

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
| GB | 16 | **10** | 9 | 9 | 13 | 14 | 10 | 15 | 17.2 | 20.7 | 16.2 |
| both | 16 | **10** | 9 | 9 | 13 | 14 | 10 | 15 | 17.2 | 20.7 | 16.2 |

## Every entry

| example | session | play (ours / author) | branch | side | printed | framework fill | d | bars | strict_10 | +/-5 | candidate fill | cand d | cand strict_10 | exec strict_10 | candidates / executed / round trips |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `GB-2025-11-20` | 2025-11-20 | ny_box_fail / ny_box_fail | nyam_box | short | 25301.75 @10:05 | 25291.5 | 10.25 | 0.8 | False | False | 25291.5 | 10.25 | False | False | 18 / 19 / 17 |
| `GB-2025-11-19` | 2025-11-19 | weekly_level / weekly_level | prior_week_level | long | 24625.0 @09:35 | 24626.0 | 1.0 | 0.8 | True | True | 24626.0 | 1.0 | True | True | 18 / 26 / 18 |
| `GB-2026-04-23` | 2026-04-23 | previous_hour_fail / previous_hour_fail | previous_hour | short | 27116.25 @12:35-12:36 | 27110.75 | 5.5 | 0.2 | True | False | None | None | False | False | 18 / 24 / 18 |
| `GB-2026-04-28` | 2026-04-28 | ny_box_fail / cash_open | nyam_box | long | None @09:30 | 27139.5 | None | 1.0 | True | True | 27139.5 | None | True | True | 18 / 23 / 17 |
| `GB-2026-04-28` | 2026-04-28 | ny_box_fail / ny_box_fail | nyam_box | short | None @09:45-09:50 | 27179.75 | None | 1.8 | True | True | 27179.75 | None | True | True | 18 / 23 / 17 |
| `GB-2026-07-13` | 2026-07-14 | overnight_reclaim / overnight_reclaim | prior_day_level | long | 29414.25 @20:40 | 29412.0 | 2.25 | 2.8 | True | True | 29412.0 | 2.25 | True | True | 17 / 18 / 15 |
| `GB-2026-07-29-30` | 2026-07-30 | pocket_continuation / pocket_continuation | golden_pocket | short | 27644.5 @22:20 | None | None | None | False | False | 27640.75 | 3.75 | False | False | 18 / 25 / 16 |
| `GB-2026-07-29-30` | 2026-07-30 | london_reclaim / london_reclaim | london_box | long | 27359.75 @04:00 (07-30) | 27351.25 | 8.5 | 0.2 | True | False | None | None | False | False | 18 / 25 / 16 |
| `GB-2026-08-11-12` | 2026-08-12 | ny_box_fail / ny_box_fail | nyam_box | long | 29635.75 @20:01-20:13 | 29635.25 | 0.5 | 0.0 | True | True | 29635.25 | 0.5 | True | True | 18 / 23 / 18 |
| `GB-2026-08-13` | 2026-08-13 | ny_box_fail / previous_hour_fail | nyam_box | short | 30227.5 @11:20-11:27 | 30225.25 | 2.25 | 0.0 | True | True | 30231.0 | 3.5 | True | False | 18 / 19 / 16 |
| `GB-2026-08-27` | 2026-08-27 | ny_box_fail / ny_box_fail | nyam_box | short | 29613.75 @11:21-11:24 | 29618.5 | 4.75 | 0.0 | True | True | 29618.5 | 4.75 | True | True | 18 / 17 / 17 |
| `GB-2026-08-27` | 2026-08-27 | previous_hour_fail / ny_box_fail | previous_hour | short | 29642.25 @12:50-12:56 | 29643.25 | 1.0 | 0.4 | True | True | 29639.0 | 3.25 | False | False | 18 / 17 / 17 |
| `GB-2026-08-28` | 2026-08-28 | ny_box_fail / ny_box_fail | nyam_box | short | 29674.25 @10:05 | 29668.0 | 6.25 | 0.6 | True | False | 29668.0 | 6.25 | True | True | 18 / 19 / 16 |
| `GB-2026-08-31` | 2026-08-31 | cash_open / cash_open | cash_open_reclaim_case | short | 29510.5 @09:33 | 29506.75 | 3.75 | 0.0 | True | True | 29506.75 | 3.75 | True | True | 18 / 21 / 18 |
| `GB-2026-09-01` | 2026-09-01 | overnight_reclaim / overnight_reclaim | prior_day_level | short | 29253.75 @12:05 | 29260.25 | 6.5 | 1.0 | True | False | None | None | False | False | 18 / 25 / 18 |
| `GB-2026-09-03` | 2026-09-03 | asia_fade / asia_fade | asia_tdo_case | short | 29238.25 @00:32-00:35 | 29236.5 | 1.75 | 0.6 | True | True | 29236.5 | 1.75 | True | True | 6 / 7 / 6 |

## Every remaining miss under strict_10, with its cause

A miss is admissible only if it names the exact input that differs.

| example | printed | ours | d(pts) | bars / allowed | cause | input limit? |
| --- | --- | --- | ---: | --- | --- | --- |
| `GB-2025-11-20` 10:05 | 25301.75 | 25291.5 | 10.25 | 0.8 / 3.0 | his 09:00-10:00 box high is 25,301.75; our tape's high over that hour is 25,292.00 and it does not trade 25,301.75 until 10:37 | yes |
| `GB-2026-07-29-30` 22:20 | 27644.5 | 27640.75 | 3.75 | 2.8 / 1.0 | our near pocket line is 27,650.75; his own printed pocket lines are 27,652 and 27,718, so his fill is 7.5 points from his own nearest line -- a +/-5 match to any level-based rule is arithmetically impossible on this ticket | yes |

## Examples with no proper entry to match


## Other fills on the same charts (neither detections nor misses)

- `GB-2025-11-20`: 11:00 buy_limit 25112.5
- `GB-2026-04-23`: 13:00-14:00 sell 27116.25
- `GB-2026-07-29-30`: 23:30-01:00 sell 27652.25
