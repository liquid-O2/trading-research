# Author example replay

- Examples: 55
- Detected: 8
- Miss: 35
- data_unavailable: 12

| id | source | date | family | branch | detected | our_level | our_side | author_level | author_side | entry_time | divergence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `JJ-2025-01-28` | JR p.71 (post 2025-01-30, chart 2025-01-28) | 2025-01-28 | JJ-TBR | judas_reversal | True | 21257.75 | long | 21258.0 | long | 1738075980000000000 | match |
| `JJ-2025-05-23-LONDON` | JR p.69 | 2025-05-23 | JJ-TBR | other_session | False | 21123.5 | long | 21115.0 | long | 1747992600000000000 | miss: level 21123.5 vs 21115.0 |
| `JJ-2025-09-09` | JR pp.25-26 | 2025-09-09 | JJ-TBR | extension_reaction | False | 23739.2425 | long | 23727.0 | long | 1757428560000000000 | miss: level 23739.2425 vs 23727.0; level-selection: our_level 23739.2425 is inside the RR-01 lower band [23727.00, 23743.50]; author_level 23727.0 is the band far edge. Finding, not a rule change. |
| `JJ-2025-09-12` | JR p.23 | 2025-09-12 | JJ-TBR | extension_reaction | True | 24113.40875 | short | 24111.5 | short | 1757688900000000000 | match |
| `JJ-2025-10-01` | JR p.21 | 2025-10-01 | JJ-TBR | judas_reversal | True | 24805.5 | short | 24805.0 | short | 1759326240000000000 | match |
| `JJ-2025-10-03` | JR pp.65-66 | 2025-10-03 | JJ-TBR | judas_reversal | True | 25103.0 | long | 25104.0 | long | 1759500000000000000 | match |
| `JJ-2025-10-06-LONDON` | JR p.64 | 2025-10-06 | JJ-TBR | other_session | False | 25088.3125 | long | 25052.0 | long | 1759735500000000000 | miss: level 25088.3125 vs 25052.0 |
| `JJ-2025-10-07-LONDON` | JR p.64 | 2025-10-07 | JJ-TBR | other_session | False | 25148.0625 | long | 25122.0 | long | 1759820700000000000 | miss: level 25148.0625 vs 25122.0 |
| `JJ-2025-10-08-LONDON` | JR p.63 | 2025-10-08 | JJ-TBR | other_session | False | 25045.5 | long | 25028.0 | long | 1759906860000000000 | miss: level 25045.5 vs 25028.0 |
| `JJ-2025-10-13` | JR p.20 | 2025-10-13 | JJ-TBR | judas_reversal | True | 24733.0 | long | 24731.0 | long | 1760362620000000000 | match |
| `JJ-2025-11-10` | JR p.59 | 2025-11-10 | JJ-TBR | extension_reaction | True | 25641.225 | short | 25642.5 | short | 1762786860000000000 | match |
| `JJ-2025-11-18` | JR p.57 | 2025-11-18 | JJ-TBR | extension_reaction | False | 24394.51125 | long | 24660.0 | long | 1763481720000000000 | miss: level 24394.51125 vs 24660.0 |
| `JJ-2025-12-30` | JR p.55 | 2025-12-30 | JJ-TBR | judas_reversal | True | 25691.25 | long | 25690.0 | long | 1767105720000000000 | match |
| `JJ-2026-01-02` | JR pp.53-54 | 2026-01-02 | JJ-TBR | timed_pzone_reversal | False | 25761.0 | long | 25681.0 | long | 1767365340000000000 | miss: level 25761.0 vs 25681.0 |
| `JJ-2026-01-09` | JR pp.51-52 | 2026-01-09 | JJ-TBR | timed_pzone_reversal | False | 25660.0 | long | 25710.0 | long | 1767969060000000000 | miss: level 25660.0 vs 25710.0 |
| `JJ-2026-02-24` | JR p.13 | 2026-02-24 | JJ-TBR | judas_reversal | False | 24795.25 | long | 24795.0 | long | 1771943520000000000 | miss: entry_outside_window |
| `JJ-2026-06-05-LONDON` | JR p.50 | 2026-06-05 | JJ-TBR | other_session | False | 30138.1875 | long | 30058.0 | long | 1780644960000000000 | miss: level 30138.1875 vs 30058.0 |
| `JJ-2026-06-09` | JR p.8 | 2026-06-09 | JJ-TBR | judas_reversal | False | 29739.5 | short | 219.0 | short | 1781010420000000000 | miss: level 29739.5 vs 219.0 |
| `JJ-2026-07-06` | JR p.44 | 2026-07-06 | JJ-TBR | extension_reaction | False | 30076.90375 | short | 30095.0 | short | 1783349460000000000 | miss: level 30076.90375 vs 30095.0 |
| `JJ-2026-07-10` | JR p.42 | 2026-07-10 | JJ-TBR | internal_rotation | False | 29829.5 | long | 29770.0 | long | 1783689720000000000 | miss: level 29829.5 vs 29770.0 |
| `JJ-2026-07-16` | JR p.41 | 2026-07-16 | JJ-TBR | judas_outbound | False | None | None | 29555.0 | short | None | miss |
| `JJ-2026-07-27` | JR p.38 | 2026-07-27 | JJ-TBR | single_extended | False | 28693.625 | short | None | short | 1785157260000000000 | miss: verdict=fail |
| `JJ-2026-07-28` | JR p.36 | 2026-07-28 | JJ-TBR | single_purged | False | None | None | None | short | None | miss |
| `JJ-2026-08-28` | JR pp.32-33 | 2026-08-28 | JJ-TBR | judas_reversal | None | None | None | None | long | None | data_unavailable |
| `JJ-2026-09-01` | JR pp.30-31 | 2026-09-01 | JJ-TBR | judas_reversal / internal_rotation | None | None | None | None | long | None | data_unavailable |
| `JJ-2026-09-02` | JR p.3 | 2026-09-02 | JJ-TBR | internal_rotation | None | None | None | None | both | None | data_unavailable |
| `GB-2025-11-20` | GB p.43 | 2025-11-20 | GB-FAIL | nyam_box | False | None | None | 25301.75 | short | None | no_matching_episode |
| `GB-2025-11-19` | GB p.31 | 2025-11-19 | GB-FAIL | prior_week_level | False | None | None | 24625.0 | long | None | no_matching_episode |
| `GB-2026-04-23` | GB p.45 | 2026-04-23 | GB-FAIL | previous_hour / nyam_box (PM sweep of the AM high) | False | None | None | 27116.25 | short | None | no_matching_episode |
| `GB-2026-04-28` | GB p.45 | 2026-04-28 | GB-FAIL | nyam_box | True | 27179.75 | short | 27250.0 | short | 1777383480000000000 | drawn-not-live |
| `GB-2026-07-13` | GB p.48 | 2026-07-13 | GB-FAIL | prior_day_level / asia_box | False | None | None | 29414.25 | long | None | no_matching_episode |
| `GB-2026-07-29-30` | GB pp.51-52 | 2026-07-29 | GB-FAIL | golden_pocket (down-leg short) then london_box long | False | None | None | 27644.5 | short | None | no_matching_episode |
| `GB-2026-08-11-12` | GB pp.52-54 | 2026-08-11 | GB-FAIL | asia_box | False | None | None | 29635.75 | long | None | no_matching_episode |
| `GB-2026-08-13` | GB p.54 | 2026-08-13 | GB-FAIL | previous_hour | False | None | None | 30227.5 | short | None | no_matching_episode |
| `GB-2026-08-27` | GB pp.38, 56 | 2026-08-27 | GB-FAIL | nyam_box (PM sweep) | None | None | None | None | short | None | data_unavailable |
| `GB-2026-08-28` | GB pp.39, 55 | 2026-08-28 | GB-FAIL | nyam_box | None | None | None | None | short | None | data_unavailable |
| `GB-2026-08-31` | GB p.58 | 2026-08-31 | GB-FAIL | nyam_box (at-level failure before 10:00) | None | None | None | None | short | None | data_unavailable |
| `GB-2026-09-01` | GB p.23 | 2026-09-01 | GB-FAIL | prior_day_level with golden pocket | None | None | None | None | short | None | data_unavailable |
| `GB-2026-09-03` | GB pp.27, 59 | 2026-09-03 | GB-FAIL | asia_tdo_case | None | None | None | None | short | None | data_unavailable |
| `GB-2026-09-08` | GB pp.16, 19, 60 | 2026-09-08 | GB-FAIL | asia_tdo_case then nyam_box | None | None | None | None | short then long | None | data_unavailable |
| `GB-2026-09-11` | raw capture 2026-09-14, post 2099503614372741234 | 2026-09-11 | GB-FAIL / GB-SCALP | overnight prior_day_level long; golden_pocket_continuation | None | None | None | None | long | None | data_unavailable |
| `GB-2026-09-14` | raw capture 2026-09-14, post 2099513366326730859 | 2026-09-14 | GB-FAIL | london_box then asia_box | None | None | None | None | long then short | None | data_unavailable |
| `SI-2026-07-08` | OFM p.7 | 2026-07-08 | SIRES | ofm_aggressive | False | 29374.5 | long | 29246.5 | short | 1783461600012544871 | match_branch_only;miss:side our=long author=short |
| `SI-2026-07-09` | OFM pp.9, 14 | 2026-07-09 | SIRES | ofm_aggressive | False | 29415.25 | long | 29812.25 | long | 1783548010946125021 | match_branch_only |
| `SI-2026-07-10` | OFM pp.8, 11-13 | 2026-07-10 | SIRES | ofm_aggressive | False | 29937.75 | long | 29901.75 | short | 1783634400000000000 | match_branch_only |
| `SI-2026-07-14` | NYAM pp.4-11 | 2026-07-14 | SIRES | defended_band_continuation | False | 29446.0 | long | 29757.25 | long | 1783980000000000000 | match_branch_only |
| `SI-2026-07-15-OVERNIGHT` | STOP pp.8-9 | 2026-07-15 | SIRES | absorption_reward_retest | False | 29805.0 | long | 30045.0 | short | 1784066400000000000 | match_branch_only |
| `SI-2026-07-23` | ANAT pp.5-9 | 2026-07-23 | SIRES | defended_band_continuation | False | 29130.25 | long | 28700.0 | as attempted | 1784763997629815135 | match_branch_only |
| `SI-2026-07-31` | K18 pp.4-10; MAMT p.12 | 2026-07-31 | SIRES | ofm_aggressive | False | 28317.0 | long | 28693.5 | short | 1785448800000000000 | match_branch_only |
| `SI-2026-08-04` | K2345 pp.3-9 | 2026-08-04 | SIRES | ofm_aggressive | False | 28930.25 | long | 29304.25 | long | 1785794400020158969 | match_branch_only |
| `SI-2026-08-06` | BIG pp.3-16 | 2026-08-06 | SIRES | ofm_aggressive | False | 29572.0 | long | 29258.0 | long | 1785967205340052875 | match_branch_only |
| `SI-2026-08-19` | CONT pp.4-10 | 2026-08-19 | SIRES | ofm_aggressive | False | 29569.5 | long | 29665.0 | short | 1787090400585636367 | match_branch_only |
| `SA-2026-08-10-ASIA` | TRAP pp.3-11 | 2026-08-10 | SAINT-AMT | continuation_retest | False | 29857.0 | short | 29729.25 | short | 1786313460000000000 | level |
| `SA-2026-08-04-12-WIC` | WIC pp.6-8 | 2026-08-10 | SAINT-AMT | continuation_retest | False | 29782.25 | short | None | short | 1786368960000000000 | no printed fill |
| `MB-2026-07-K10` | K10 pp.7-8, 12-13 | 2026-07 (undated day; presentation 2026-07-01) | MEMBER-TWO-REASONS | member two reasons | None | None | None | None | short then long | None | data_unavailable |
