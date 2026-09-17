# Plausibility GB-FAIL

slice n=15 baseline=B0.3-2026-09-17

| branch | sessions | episodes | pass | fail | unknown | pass_rate | eps/session | bound | in/out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| london_box | 15 | 973 | 665 | 308 | 0 | 0.683 | 64.87 | eps [0, 2] pr [0.0, 0.55] | out |
| asia_box | 15 | 1050 | 756 | 294 | 0 | 0.720 | 70.00 | eps [0, 2] pr [0.0, 0.7] | out |
| asia_tdo_case | 15 | 840 | 493 | 347 | 0 | 0.587 | 56.00 | eps [0, 2] pr [0.0, 0.65] | out |
| prior_day_level | 15 | 731 | 506 | 225 | 0 | 0.692 | 48.73 | eps [0, 4] pr [0.0, 0.6] | out |
| prior_week_level | 15 | 667 | 434 | 233 | 0 | 0.651 | 44.47 | eps [0, 2] pr [0.0, 0.6] | out |
| nyam_box | 15 | 1742 | 1404 | 338 | 0 | 0.806 | 116.13 | eps [0, 12] pr [0.0, 0.4] | out |
| previous_hour | 15 | 1992 | 1357 | 635 | 0 | 0.681 | 132.80 | eps [0, 16] pr [0.0, 0.35] | out |
| nwog | 15 | 0 | 0 | 0 | 0 | 0.000 | 0.00 | eps [0, 4] pr [0.0, 0.25] | in |
| cash_open_reclaim_case | 15 | 618 | 381 | 237 | 0 | 0.617 | 41.20 | eps [0, 2] pr [0.0, 0.5] | out |
| golden_pocket | 15 | 68 | 47 | 21 | 0 | 0.691 | 4.53 | eps [0, 2] pr [0.0, 0.3] | out |
| ny_session_extreme | 15 | 0 | 0 | 0 | 0 | 0.000 | 0.00 | eps [0, 2] pr [0.0, 0.2] | in |

Diagnosis `prior_week_level`. GB p.31 (SD03 addendum): The source gives no weekly-level frequency. The episodes-per-session bound [0, 2] is structural (one reference per side per session) and the pass-rate bound reuses the prior_day_level sweep-and-reclaim template on the same confirmation mode. An observed rate outside it is reported, not tuned.

Across GB-FAIL boxes (london/asia/nyam/previous_hour) passes/session=278.800 bound=[0,2] out.
Asia histogram passes={'00:00': 6, '00:30': 22, '01:00': 25, '01:30': 47, '02:00': 61, '02:30': 13, '03:00': 15, '03:30': 17, '04:00': 13, '04:30': 20, '05:00': 17, '05:30': 20, '06:00': 5, '06:30': 8, '07:00': 11, '08:30': 16, '09:00': 5, '09:30': 53, '10:00': 45, '10:30': 25, '11:00': 21, '11:30': 4, '12:00': 1, '12:30': 4, '13:00': 5, '13:30': 23, '14:00': 10, '14:30': 17, '15:00': 4, '15:30': 10, '16:00': 1, '21:00': 18, '21:30': 52, '22:00': 54, '22:30': 32, '23:00': 43, '23:30': 13}. London passes=665 histogram={'03:00': 41, '03:30': 46, '04:00': 72, '04:30': 36, '05:00': 56, '05:30': 29, '06:00': 17, '06:30': 26, '07:00': 7, '07:30': 8, '08:00': 26, '08:30': 25, '09:00': 43, '09:30': 74, '10:00': 46, '10:30': 10, '11:00': 6, '11:30': 5, '12:00': 19, '12:30': 14, '13:00': 4, '13:30': 4, '14:00': 8, '14:30': 13, '15:00': 13, '15:30': 16, '16:00': 1}.
NWOG monday_passes=0 of 0 passes (GB pp.13,14,36,37).
