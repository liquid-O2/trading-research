# Plausibility GB-FAIL

slice n=15 baseline=B0.3-2026-09-17

| branch | sessions | episodes | pass | fail | unknown | pass_rate | eps/session | bound | in/out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| london_box | 15 | 358 | 316 | 42 | 0 | 0.883 | 23.87 | eps [0, 2] pr [0.0, 0.55] | out |
| asia_box | 15 | 390 | 363 | 27 | 0 | 0.931 | 26.00 | eps [0, 2] pr [0.0, 0.7] | out |
| asia_tdo_case | 15 | 583 | 361 | 222 | 0 | 0.619 | 38.87 | eps [0, 2] pr [0.0, 0.65] | out |
| prior_day_level | 15 | 462 | 284 | 178 | 0 | 0.615 | 30.80 | eps [0, 4] pr [0.0, 0.6] | out |
| prior_week_level | 15 | 405 | 236 | 169 | 0 | 0.583 | 27.00 | eps [0, 2] pr [0.0, 0.6] | out |
| nyam_box | 15 | 339 | 307 | 32 | 0 | 0.906 | 22.60 | eps [0, 12] pr [0.0, 0.4] | out |
| previous_hour | 15 | 654 | 588 | 66 | 0 | 0.899 | 43.60 | eps [0, 16] pr [0.0, 0.35] | out |
| nwog | 15 | 0 | 0 | 0 | 0 | 0.000 | 0.00 | eps [0, 4] pr [0.0, 0.25] | in |
| cash_open_reclaim_case | 15 | 83 | 46 | 37 | 0 | 0.554 | 5.53 | eps [0, 2] pr [0.0, 0.5] | out |
| golden_pocket | 15 | 30 | 17 | 13 | 0 | 0.567 | 2.00 | eps [0, 2] pr [0.0, 0.3] | out |
| ny_session_extreme | 15 | 0 | 0 | 0 | 0 | 0.000 | 0.00 | eps [0, 2] pr [0.0, 0.2] | in |

Diagnosis `prior_week_level`. GB p.31 (SD03 addendum): The source gives no weekly-level frequency. The episodes-per-session bound [0, 2] is structural (one reference per side per session) and the pass-rate bound reuses the prior_day_level sweep-and-reclaim template on the same confirmation mode. An observed rate outside it is reported, not tuned.

Across GB-FAIL boxes (london/asia/nyam/previous_hour) passes/session=104.933 bound=[0,2] out.
Asia histogram passes={'00:00': 7, '00:30': 17, '01:00': 16, '01:30': 38, '02:00': 44, '02:30': 10, '03:00': 14, '03:30': 13, '04:00': 11, '04:30': 13, '05:00': 13, '05:30': 15, '06:00': 6, '06:30': 6, '07:00': 8, '08:30': 11, '09:00': 3, '09:30': 12, '10:00': 19, '10:30': 22, '11:00': 7, '11:30': 2, '12:00': 1, '12:30': 3, '13:00': 3, '13:30': 19, '14:00': 7, '14:30': 13, '15:00': 3, '15:30': 6, '16:00': 1}. London passes=316 histogram={'05:00': 41, '05:30': 21, '06:00': 15, '06:30': 21, '07:00': 2, '07:30': 8, '08:00': 19, '08:30': 22, '09:00': 29, '09:30': 26, '10:00': 26, '10:30': 7, '11:00': 4, '11:30': 4, '12:00': 14, '12:30': 12, '13:00': 4, '13:30': 3, '14:00': 7, '14:30': 9, '15:00': 10, '15:30': 11, '16:00': 1}.
NWOG monday_passes=0 of 0 passes (GB pp.13,14,36,37).
