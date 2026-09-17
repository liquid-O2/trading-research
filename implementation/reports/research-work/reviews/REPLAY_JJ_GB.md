# Author-example replay, source-faithful rebuild (B0.3-2026-09-17)

Entries only: an example is detected when every proper entry on it is reproduced on the
author's play and side, within one five-minute bar of the printed time and within the
stated price tolerance. `tol` is the ticket's own printed risk (|stop - entry|), or 27
points (the median printed stop) where the ticket prints no stop; `strict` is +/-5 points.

- proper entries inside the tape: 40
- detected (ticket-risk tolerance): 18
- detected (strict +/-5 points): 7
- detected within three five-minute bars of the printed time: 22
- outside the tape: 9

| example | src | session | play (ours / author) | branch | side | printed | ours | d(pts) | bars | tol | det | strict | 3bar | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `JJ-2025-01-28` | JR p.71 (post 2025-01-30, chart 2025-01-28) | 2025-01-28 | double_break / double_break | judas_reversal | long | 21241.75 @09:53:46 | 21242.0 @09:54 | 0.25 | 0.2 | 27.0 | True | True | True |  |
| `JJ-2025-05-23-LONDON` | JR p.69 | 2025-05-23 | london / london | other_session | long | 21108.5 @02:20 | 21107.25 @02:16 | 1.25 | 0.8 | 27.0 | True | True | True |  |
| `JJ-2025-09-09` | JR pp.25-26 | 2025-09-09 | double_break / double_break | extension_reaction | long | 23743.5 @10:35 | 23747.245 @10:46 | 3.745 | 2.2 | 27.0 | False | False | True | entry 2.2 five-minute bars from the printed time |
| `JJ-2025-10-01` | JR p.21 | 2025-10-01 | double_break / double_break | judas_reversal | short | 24845.0 @09:45 | 24837.0 @09:50 | 8.0 | 1.0 | 27.0 | True | False | True |  |
| `JJ-2025-10-03` | JR pp.65-66 | 2025-10-03 | double_break / double_break | judas_reversal | long | 25091.45 @10:10 | 25079.25 @10:14 | 12.2 | 0.8 | 27.0 | True | False | True |  |
| `JJ-2025-10-06-LONDON` | JR p.64 | 2025-10-06 | london / london | other_session | long | 25066.0 @03:40 | 25069.375 @03:54 | 3.375 | 2.8 | 27.0 | False | False | True | entry 2.8 five-minute bars from the printed time |
| `JJ-2025-10-07-LONDON` | JR p.64 | 2025-10-07 | london / london | other_session | long | 25140.0 @04:30 | 25138.0 @04:39 | 2.0 | 1.8 | 27.0 | False | False | True | entry 1.8 five-minute bars from the printed time |
| `JJ-2025-10-08-LONDON` | JR p.63 | 2025-10-08 | london / london | other_session | long | 25028.0 @03:00-04:00 | 25045.5 @03:06 | 17.5 | 0.0 | 27.0 | True | False | True |  |
| `JJ-2025-10-13` | JR p.20 | 2025-10-13 | double_break / double_break | judas_reversal | short | 24848.5 @09:05 | 24877.75 @09:12 | 29.25 | 1.4 | 27.0 | False | False | False | entry 1.4 five-minute bars from the printed time |
| `JJ-2025-10-13` | JR p.20 | 2025-10-13 | double_break / double_break | judas_reversal | long | 24768.5 @09:40 | 24773.75 @09:44 | 5.25 | 0.8 | 27.0 | True | False | True |  |
| `JJ-2025-11-10` | JR p.59 | 2025-11-10 | double_break / double_break | extension_reaction | short | 25635.0 @10:15 | 25632.15 @10:15 | 2.85 | 0.0 | 27.0 | True | True | True |  |
| `JJ-2025-11-18` | JR p.57 | 2025-11-18 | double_break / double_break | extension_reaction | long | 24420.0 @11:00 | 24423.7575 @11:03 | 3.7575 | 0.6 | 27.0 | True | True | True |  |
| `JJ-2025-12-30` | JR p.55 | 2025-12-30 | double_break / double_break | judas_reversal | long | 25690.0 @09:45-09:47 | 25691.25 @09:50 | 1.25 | 0.6 | 27.0 | True | True | True |  |
| `JJ-2026-01-02` | JR pp.53-54 | 2026-01-02 | pzone / pzone | timed_pzone_reversal | long | 25663.0 @09:22 | 25663.0 @09:38 | 0.0 | 3.2 | 27.0 | False | False | False | entry 3.2 five-minute bars from the printed time |
| `JJ-2026-01-09` | JR pp.51-52 | 2026-01-09 | pzone / pzone | timed_pzone_reversal | long | 25664.25 @09:32 | 25660.0 @09:36 | 4.25 | 0.8 | 47.0 | True | True | True |  |
| `JJ-2026-02-24` | JR p.13 | 2026-02-24 | double_break / double_break | judas_reversal | long | 24795.0 @09:38 | 24795.0 @09:42 | 0.0 | 0.8 | 27.0 | True | True | True |  |
| `JJ-2026-06-05-LONDON` | JR p.50 | 2026-06-05 | london / london | other_session | long | 30066.5 @03:20 | 30105.0 @03:02 | 38.5 | 3.6 | 27.0 | False | False | False | entry 3.6 five-minute bars from the printed time |
| `JJ-2026-07-06` | JR p.44 | 2026-07-06 | double_break / double_break | judas_reversal | short | 30065.0 @10:45 | 30011.25 @10:42 | 53.75 | 0.6 | 27.0 | False | False | False | entry 53.75 points from the printed fill (tolerance 27.0) |
| `JJ-2026-07-10` | JR p.42 | 2026-07-10 | big_range_eq / big_range_eq | internal_rotation | long | 29809.0 @11:05 | 29819.25 @09:20 | 10.25 | 21.0 | 27.0 | False | False | False | entry 21.0 five-minute bars from the printed time |
| `JJ-2026-07-16` | JR p.41 | 2026-07-16 | None / double_break | None | short | 29451.5 @09:35 | None @ | None | None | 27.0 | False | False | False | no passing episode on the author's play and side |
| `JJ-2026-07-27` | JR p.38 | 2026-07-27 | None / single_break | None | short | None @09:35 | None @ | None | None | 27.0 | False | False | False | no passing episode on the author's play and side |
| `JJ-2026-07-28` | JR p.36 | 2026-07-28 | single_break / single_break | single_purged | short | None @09:35 | 27894.375 @09:40 | None | 1.0 | 27.0 | True | False | True |  |
| `JJ-2026-08-28` | JR pp.32-33 | 2026-08-28 | double_break / double_break | judas_reversal | long | 29592.0 @09:31 | 29600.0 @09:36 | 8.0 | 1.0 | 27.0 | True | False | True |  |
| `JJ-2026-09-01` | JR pp.30-31 | 2026-09-01 | double_break / double_break | judas_reversal | long | 29074.25 @09:40 | 29122.25 @09:31 | 48.0 | 1.8 | 27.0 | False | False | False | entry 1.8 five-minute bars from the printed time |
| `GB-2025-11-20` | GB p.43 | 2025-11-20 | ny_box_fail / ny_box_fail | nyam_box | short | 25301.75 @10:05 | 25291.5 @10:02 | 10.25 | 0.6 | 27.0 | True | False | True |  |
| `GB-2025-11-19` | GB p.31 | 2025-11-19 | weekly_level / weekly_level | prior_week_level | long | 24625.0 @10:00 | 24626.0 @09:31 | 1.0 | 5.8 | 27.0 | False | False | False | entry 5.8 five-minute bars from the printed time |
| `GB-2026-04-23` | GB p.45 | 2026-04-23 | previous_hour_fail / previous_hour_fail | previous_hour | short | None @13:00 | 27094.5 @12:55 | None | 1.0 | 27.0 | True | False | True |  |
| `GB-2026-04-28` | GB p.45 | 2026-04-28 | ny_box_fail / ny_box_fail | nyam_box | long | None @09:30 | 27073.5 @10:40 | None | 14.0 | 27.0 | False | False | False | entry 14.0 five-minute bars from the printed time |
| `GB-2026-04-28` | GB p.45 | 2026-04-28 | None / ny_box_fail | None | short | None @09:45-09:50 | None @ | None | None | 27.0 | False | False | False | no passing episode on the author's play and side |
| `GB-2026-07-13` | GB p.48 | 2026-07-14 | overnight_reclaim / overnight_reclaim | prior_day_level | long | 29414.25 @20:40 | 29393.25 @19:25 | 21.0 | 273.0 | 27.0 | False | False | False | entry 273.0 five-minute bars from the printed time |
| `GB-2026-07-29-30` | GB pp.51-52 | 2026-07-30 | None / pocket_continuation | None | short | 27644.5 @23:20 | None @ | None | None | 73.0 | False | False | False | no passing episode on the author's play and side |
| `GB-2026-07-29-30` | GB pp.51-52 | 2026-07-30 | None / london_reclaim | None | long | 27359.75 @04:00 (07-30) | None @ | None | None | 27.0 | False | False | False | no passing episode on the author's play and side |
| `GB-2026-08-11-12` | GB pp.52-54 | 2026-08-12 | ny_box_fail / ny_box_fail | nyam_box | long | 29635.75 @20:40 | 29887.25 @10:06 | 251.5 | 449.2 | 48.25 | False | False | False | entry 449.2 five-minute bars from the printed time |
| `GB-2026-08-13` | GB p.54 | 2026-08-13 | previous_hour_fail / previous_hour_fail | previous_hour | short | 30227.5 @11:45 | 30192.75 @12:32 | 34.75 | 9.4 | 11.25 | False | False | False | entry 9.4 five-minute bars from the printed time |
| `GB-2026-08-27` | GB pp.38, 56 | 2026-08-27 | ny_box_fail / ny_box_fail | nyam_box | short | 29613.75 @11:30 | 29597.5 @11:25 | 16.25 | 1.0 | 19.25 | True | False | True |  |
| `GB-2026-08-27` | GB pp.38, 56 | 2026-08-27 | ny_box_fail / ny_box_fail | nyam_box | short | 29642.25 @13:00 | 29623.5 @12:38 | 18.75 | 4.4 | 21.75 | False | False | False | entry 4.4 five-minute bars from the printed time |
| `GB-2026-08-28` | GB pp.39, 55 | 2026-08-28 | ny_box_fail / ny_box_fail | nyam_box | short | 29674.25 @10:05 | 29687.25 @10:01 | 13.0 | 0.8 | 34.5 | True | False | True |  |
| `GB-2026-08-31` | GB p.58 | 2026-08-31 | cash_open / cash_open | cash_open_reclaim_case | short | 29510.5 @09:33 | 29465.25 @09:35 | 45.25 | 0.4 | 28.25 | False | False | False | entry 45.25 points from the printed fill (tolerance 28.25) |
| `GB-2026-09-01` | GB p.23 | 2026-09-01 | overnight_reclaim / overnight_reclaim | prior_day_level | short | 29253.75 @11:45 | 29273.5 @11:42 | 19.75 | 0.6 | 49.75 | True | False | True |  |
| `GB-2026-09-03` | GB pp.27, 59 | 2026-09-03 | asia_fade / asia_fade | asia_tdo_case | short | 29238.25 @00:45 | 29227.75 @00:30 | 10.5 | 3.0 | 16.75 | False | False | True | entry 3.0 five-minute bars from the printed time |
| `GB-2026-09-08` | GB pp.16, 19, 60 | 2026-09-08 | None / asia_fade | None | short | 29730.5 @00:55 | None @ | None | None | None | None | None | None | date outside the tape |
| `GB-2026-09-08` | GB pp.16, 19, 60 | 2026-09-08 | None / ny_box_fail | None | long | 29469.25 @10:00 | None @ | None | None | None | None | None | None | date outside the tape |
| `GB-2026-09-11` | raw capture 2026-09-14, post 2099503614372741234 | 2026-09-11 | None / overnight_reclaim | None | long | 29059.5 @00:15 | None @ | None | None | None | None | None | None | date outside the tape |
| `GB-2026-09-11` | raw capture 2026-09-14, post 2099503614372741234 | 2026-09-11 | None / pocket_continuation | None | long | 29382.0 @10:00 | None @ | None | None | None | None | None | None | date outside the tape |
| `GB-2026-09-14` | raw capture 2026-09-14, post 2099513366326730859 | 2026-09-14 | None / london_reclaim | None | long | 28903.75 @09:40 | None @ | None | None | None | None | None | None | date outside the tape |
| `GB-2026-09-14` | raw capture 2026-09-14, post 2099513366326730859 | 2026-09-14 | None / asia_fade | None | short | 29081.5 @10:10 | None @ | None | None | None | None | None | None | date outside the tape |
| `GB-2026-09-15` | raw capture 2026-09-15, post 2099958990486798753 | 2026-09-15 | None / ny_box_fail | None | short | 29441.5 @10:05 | None @ | None | None | None | None | None | None | date outside the tape |
| `GB-2026-09-15` | raw capture 2026-09-15, post 2099958990486798753 | 2026-09-15 | None / london_reclaim | None | long | 29244.75 @11:05 | None @ | None | None | None | None | None | None | date outside the tape |
| `GB-2026-09-15` | raw capture 2026-09-15, post 2099958990486798753 | 2026-09-15 | None / ny_box_fail | None | long | 29215.5 @15:35 | None @ | None | None | None | None | None | None | date outside the tape |

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
- `JJ-2026-08-28`: 09:32 sell_limit 29707.25; 09:32 sell_limit 29724.5
- `JJ-2026-09-01`: 09:25 buy 29106.5; 09:35 sell 29112.75; 10:05 sell 29085.5; 10:10 sell 29116.5; 10:32 sell 29196.25; 10:42 sell 29218.5; 11:00 sell 29230.5; 10:40 buy 29204.75
- `GB-2025-11-20`: 11:00 buy_limit 25112.5
- `GB-2026-04-23`: 13:00-14:00 sell 27116.25
- `GB-2026-07-29-30`: 23:30-01:00 sell 27652.25
- `GB-2026-09-08`: NY AM buy 29469.25
