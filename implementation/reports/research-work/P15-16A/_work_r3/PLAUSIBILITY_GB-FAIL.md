# Plausibility GB-FAIL

slice n=15 baseline=B0.2-2026-09-15

| branch | sessions | episodes | pass | fail | unknown | pass_rate | eps/session | bound | in/out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| london_box | 15 | 15 | 2 | 13 | 0 | 0.133 | 1.00 | eps [0, 2] pr [0.0, 0.55] | in |
| asia_box | 15 | 15 | 8 | 7 | 0 | 0.533 | 1.00 | eps [0, 2] pr [0.0, 0.7] | in |
| asia_tdo_case | 15 | 15 | 4 | 11 | 0 | 0.267 | 1.00 | eps [0, 2] pr [0.0, 0.65] | in |
| prior_day_level | 15 | 30 | 12 | 18 | 0 | 0.400 | 2.00 | eps [0, 4] pr [0.0, 0.6] | in |
| prior_week_level | 15 | 30 | 9 | 21 | 0 | 0.300 | 2.00 | eps [0, 2] pr [0.0, 0.6] | in |
| nyam_box | 15 | 39 | 10 | 29 | 0 | 0.256 | 2.60 | eps [0, 12] pr [0.0, 0.4] | in |
| previous_hour | 15 | 60 | 8 | 52 | 0 | 0.133 | 4.00 | eps [0, 16] pr [0.0, 0.35] | in |
| nwog | 15 | 21 | 4 | 16 | 1 | 0.191 | 1.40 | eps [0, 4] pr [0.0, 0.25] | in |
| cash_open_reclaim_case | 15 | 15 | 3 | 12 | 0 | 0.200 | 1.00 | eps [0, 2] pr [0.0, 0.5] | in |
| golden_pocket | 15 | 15 | 4 | 11 | 0 | 0.267 | 1.00 | eps [0, 2] pr [0.0, 0.3] | in |
| ny_session_extreme | 15 | 30 | 5 | 25 | 0 | 0.167 | 2.00 | eps [0, 2] pr [0.0, 0.2] | in |

Across GB-FAIL boxes (london/asia/nyam/previous_hour) passes/session=1.867 bound=[0,2] in.
Asia histogram passes={'00:00': 1, '01:00': 1, '01:30': 2, '03:30': 1, '05:00': 2, '10:00': 1}. London passes=2 histogram={'09:30': 1, '11:00': 1}.
NWOG monday_passes=4 of 4 passes (GB pp.13,14,36,37).
