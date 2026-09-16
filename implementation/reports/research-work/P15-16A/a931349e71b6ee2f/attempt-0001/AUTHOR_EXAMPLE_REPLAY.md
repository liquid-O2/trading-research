# Author example replay

- Examples: 56
- Detected: 2
- Miss: 49
- data_unavailable: 5

| id | source | date | family | branch | detected | our_level | our_side | author_level | author_side | entry_time | divergence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `JJ-2025-01-28` | JR p.71 (post 2025-01-30, chart 2025-01-28) | 2025-01-28 | JJ-TBR | judas_reversal | True | 21257.75 | long | 21258.0 | long | 1738075980000000000 | match |
| `JJ-2025-05-23-LONDON` | JR p.69 | 2025-05-23 | JJ-TBR | other_session | False | 21139.125 | long | 21115.0 | long | 1747983660000000000 | miss: verdict=fail; failed=['box_edge_swept', 'source_confirmation'] |
| `JJ-2025-09-09` | JR pp.25-26 | 2025-09-09 | JJ-TBR | extension_reaction | False | 23739.2425 | long | 23727.0 | long | 1757428560000000000 | miss: level 23739.2425 vs 23727.0; level-selection: our_level 23739.2425 is inside the RR-01 lower band [23727.00, 23743.50]; author_level 23727.0 is the band far edge. Finding, not a rule change. |
| `JJ-2025-09-12` | JR p.23 | 2025-09-12 | JJ-TBR | extension_reaction | True | 24113.40875 | short | 24111.5 | short | 1757688900000000000 | match |
| `JJ-2025-10-01` | JR p.21 | 2025-10-01 | JJ-TBR | judas_reversal | False | 24805.5 | short | 24805.0 | short | 1759325580000000000 | miss: entry_outside_window |
| `JJ-2025-10-03` | JR pp.65-66 | 2025-10-03 | JJ-TBR | judas_reversal | False | 25103.0 | long | 25104.0 | long | 1759500000000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2025-10-06-LONDON` | JR p.64 | 2025-10-06 | JJ-TBR | other_session | False | 25088.3125 | long | 25052.0 | long | 1759735500000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2025-10-07-LONDON` | JR p.64 | 2025-10-07 | JJ-TBR | other_session | False | 25148.0625 | long | 25122.0 | long | 1759820700000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2025-10-08-LONDON` | JR p.63 | 2025-10-08 | JJ-TBR | other_session | False | 25045.5 | long | 25028.0 | long | 1759906860000000000 | miss: verdict=fail; failed=['box_edge_swept', 'source_confirmation'] |
| `JJ-2025-10-13` | JR p.20 | 2025-10-13 | JJ-TBR | judas_reversal | False | 24733.0 | long | 24731.0 | long | 1760362620000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2025-11-10` | JR p.59 | 2025-11-10 | JJ-TBR | extension_reaction | False | 25641.225 | short | 25642.5 | short | 1762786860000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2025-11-18` | JR p.57 | 2025-11-18 | JJ-TBR | extension_reaction | False | 24394.51125 | long | 24660.0 | long | 1763481720000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2025-12-30` | JR p.55 | 2025-12-30 | JJ-TBR | judas_reversal | False | 25691.25 | long | 25690.0 | long | 1767105060000000000 | miss: entry_outside_window |
| `JJ-2026-01-02` | JR pp.53-54 | 2026-01-02 | JJ-TBR | timed_pzone_reversal | False | 25761.0 | long | 25681.0 | long | 1767365340000000000 | miss: level 25761.0 vs 25681.0 |
| `JJ-2026-01-09` | JR pp.51-52 | 2026-01-09 | JJ-TBR | timed_pzone_reversal | False | 25660.0 | long | 25710.0 | long | 1767969060000000000 | miss: level 25660.0 vs 25710.0 |
| `JJ-2026-02-24` | JR p.13 | 2026-02-24 | JJ-TBR | judas_reversal | False | 24795.25 | long | 24795.0 | long | 1771943520000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2026-06-05-LONDON` | JR p.50 | 2026-06-05 | JJ-TBR | other_session | False | 30138.1875 | long | 30058.0 | long | 1780644960000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2026-06-09` | JR p.8 | 2026-06-09 | JJ-TBR | judas_reversal | False | 29739.5 | short | 219.0 | short | 1781010420000000000 | miss: level 29739.5 vs 219.0 |
| `JJ-2026-07-06` | JR p.44 | 2026-07-06 | JJ-TBR | extension_reaction | False | 30076.90375 | short | 30095.0 | short | 1783349460000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2026-07-10` | JR p.42 | 2026-07-10 | JJ-TBR | internal_rotation | False | 29829.5 | long | 29770.0 | long | 1783689720000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2026-07-16` | JR p.41 | 2026-07-16 | JJ-TBR | judas_outbound | False | None | None | 29555.0 | short | None | miss |
| `JJ-2026-07-27` | JR p.38 | 2026-07-27 | JJ-TBR | single_extended | False | None | None | None | short | None | miss |
| `JJ-2026-07-28` | JR p.36 | 2026-07-28 | JJ-TBR | single_purged | False | None | None | None | short | None | miss |
| `JJ-2026-08-28` | JR pp.32-33 | 2026-08-28 | JJ-TBR | judas_reversal | False | 29593.25 | long | 29592.0 | long | 1787924100000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `JJ-2026-09-01` | JR pp.30-31 | 2026-09-01 | JJ-TBR | judas_reversal | False | 29122.25 | long | 29120.0 | long | 1788269400000000000 | miss: level 29122.25 vs 29120.0 |
| `JJ-2026-09-02` | JR p.3 | 2026-09-02 | JJ-TBR | internal_rotation | False | 29038.375 | long | None | both | 1788354060000000000 | miss: verdict=fail; failed=['source_confirmation'] |
| `GB-2025-11-20` | GB p.43 | 2025-11-20 | GB-FAIL | nyam_box | False | None | short | 25301.75 | short | 1763650080000000000 | miss_after_location:confirmation:no_close_back_inside_fail_window |
| `GB-2025-11-19` | GB p.31 | 2025-11-19 | GB-FAIL | prior_week_level | False | 24626.0 | long | 24625.0 | long | 1763519700000000000 | miss_after_location:detection:window_or_branch_mismatch |
| `GB-2026-04-23` | GB p.45 | 2026-04-23 | GB-FAIL | nyam_box | False | None | short | 27116.25 | short | 1776951420000000000 | miss_after_location:confirmation:no_close_back_inside_fail_window |
| `GB-2026-04-28` | GB p.45 | 2026-04-28 | GB-FAIL | nyam_box | False | None | short | None | both | 1777383480000000000 | miss_after_location:confirmation:no_close_back_inside_fail_window |
| `GB-2026-07-13` | GB p.48 | 2026-07-13 | GB-FAIL | nwog | False | None | long | 29414.25 | long | 1783893660000000000 | miss_after_location:confirmation:no_close_back_inside_fail_window |
| `GB-2026-07-29-30` | GB pp.51-52 | 2026-07-29 | GB-FAIL | ny_session_extreme | False | None | short | 27644.5 | short | 1785350820000000000 | miss_after_location:confirmation:no_close_back_inside_fail_window |
| `GB-2026-08-11-12` | GB pp.52-54 | 2026-08-11 | GB-FAIL | cash_open_reclaim_case | False | None | long | 29635.75 | long | 1786455000000000000 | miss_after_location:confirmation:no_reclaim_close_above_open |
| `GB-2026-08-13` | GB p.54 | 2026-08-13 | GB-FAIL | previous_hour | False | None | short | 30227.5 | short | 1786647660000000000 | miss_after_location:confirmation:no_close_back_inside_fail_window |
| `GB-2026-08-27` | GB pp.38, 56 | 2026-08-27 | GB-FAIL | nyam_box | False | None | short | 29613.75 | short | 1787837460000000000 | miss_after_location:confirmation:no_close_back_inside_fail_window |
| `GB-2026-08-28` | GB pp.39, 55 | 2026-08-28 | GB-FAIL | nyam_box | False | None | short | 29674.25 | short | 1787924460000000000 | miss_after_location:confirmation:no_close_back_inside_fail_window |
| `GB-2026-08-31` | GB p.58 | 2026-08-31 | GB-FAIL | nyam_box | False | None | short | 29510.5 | short | 1788183060000000000 | miss_after_location:confirmation:no_close_back_inside_fail_window |
| `GB-2026-09-01` | GB p.23 | 2026-09-01 | GB-FAIL | prior_day_level | False | None | long | 29253.75 | short | 1788250020000000000 | miss_after_location:confirmation:no_five_minute_close |
| `GB-2026-09-03` | GB pp.27, 59 | 2026-09-03 | GB-FAIL | asia_tdo_case | False | 29236.5 | short | 29238.25 | short | 1788409800000000000 | miss_after_location:detection:window_or_branch_mismatch |
| `GB-2026-09-08` | GB pp.16, 19, 60 | 2026-09-08 | GB-FAIL | asia_tdo_case then nyam_box | None | None | None | None | short then long | None | data_unavailable |
| `GB-2026-09-11` | raw capture 2026-09-14, post 2099503614372741234 | 2026-09-11 | GB-FAIL / GB-SCALP | overnight prior_day_level long; golden_pocket_continuation | None | None | None | None | long | None | data_unavailable |
| `GB-2026-09-14` | raw capture 2026-09-14, post 2099513366326730859 | 2026-09-14 | GB-FAIL | london_box then asia_box | None | None | None | None | long then short | None | data_unavailable |
| `SI-2026-07-08` | OFM p.7 | 2026-07-08 | SIRES | ofm_aggressive | False | 29371.5 | short | 29246.5 | short | 1783462128774287125 | miss:level |
| `SI-2026-07-09` | OFM pp.9, 14 | 2026-07-09 | SIRES | ofm_aggressive | False | 29446.0 | short | 29812.25 | long | 1783548401140445017 | miss:side |
| `SI-2026-07-10` | OFM pp.8, 11-13 | 2026-07-10 | SIRES | ofm_aggressive | False | 29927.0 | long | 29901.75 | short | 1783634676855298985 | miss:level |
| `SI-2026-07-14` | NYAM pp.4-11 | 2026-07-14 | SIRES | defended_band_continuation | False | 29443.75 | long | 29757.25 | long | 1783981462815683901 | miss:side |
| `SI-2026-07-15-OVERNIGHT` | STOP pp.8-9 | 2026-07-15 | SIRES | absorption_reward_retest | False | 29779.25 | long | 30045.0 | short | 1784066881196444569 | miss:level |
| `SI-2026-07-23` | ANAT pp.5-9 | 2026-07-23 | SIRES | defended_band_continuation | False | 28700.75 | short | 28700.0 | as attempted | 1784813408100296877 | reached_location;fail:trigger |
| `SI-2026-07-31` | K18 pp.4-10; MAMT p.12 | 2026-07-31 | SIRES | ofm_aggressive | False | 28300.0 | long | 28693.5 | short | 1785448800037593259 | miss:level |
| `SI-2026-08-04` | K2345 pp.3-9 | 2026-08-04 | SIRES | ofm_aggressive | False | 28942.5 | short | 29304.25 | long | 1785794878512244815 | miss:level |
| `SI-2026-08-06` | BIG pp.3-16 | 2026-08-06 | SIRES | ofm_aggressive | False | 29596.5 | short | 29258.0 | long | 1785968333548032261 | miss:side |
| `SI-2026-08-19` | CONT pp.4-10 | 2026-08-19 | SIRES | ofm_aggressive | False | 29549.0 | long | 29665.0 | short | 1787092161649705425 | miss:level |
| `SA-2026-08-10-ASIA` | TRAP pp.3-11 | 2026-08-10 | SAINT-AMT | trapped_buyers_retest | False | 29599.25 | short | 29729.25 | short | 1786468740000000000 | level |
| `SA-2026-08-04-12-WIC` | WIC pp.6-8 | 2026-08-10 | SAINT-AMT | continuation_retest | False | 29782.25 | short | 29730.0 | short | 1786368960000000000 | no printed fill |
| `MB-2026-07-K10` | K10 pp.7-8, 12-13 | 2026-07 (undated day; presentation 2026-07-01) | MEMBER-TWO-REASONS | member two reasons | None | None | None | None | short then long | None | data_unavailable |
| `GB-2026-09-15` | raw capture 2026-09-15, post 2099958990486798753 | 2026-09-15 | GB-FAIL | nyam_box then london_box then ny_session_extreme | None | None | None | None | short then long then long | None | data_unavailable |
