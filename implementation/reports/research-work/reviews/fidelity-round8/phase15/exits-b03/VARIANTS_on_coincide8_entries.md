# Selection variants against B0.3 (executed list, points a contract, no costs)

## JJ-TBR

baseline sessions 1719; years 2020-2026; test folds 2022, 2023, 2024, 2025, 2026

| variant | sessions | baseline mean | variant mean | mean diff | 2022 diff (p Holm) | 2023 diff (p Holm) | 2024 diff (p Holm) | 2025 diff (p Holm) | 2026 diff (p Holm) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 | 1719 | 57.296 | 49.248 | -8.048 | -9.444 (1.0) worse | -6.096 (1.0) worse | -9.197 (1.0) worse | -8.046 (1.0) worse | -17.505 (1.0) worse |
| E2 | 1719 | 57.296 | 62.853 | 5.557 | 2.933 (0.6414) not_promoted | 3.706 (0.1466) not_promoted | 2.964 (0.589) not_promoted | 7.199 (0.0352) promoted | 9.846 (0.1247) not_promoted |
| E3 | 1719 | 57.296 | 57.696 | 0.4 | 2.424 (0.9786) not_promoted | 2.527 (0.6897) not_promoted | -3.015 (1.0) worse | -0.685 (1.0) worse | -14.901 (1.0) worse |
| E4 | 1719 | 57.296 | 50.643 | -6.653 | -12.656 (1.0) worse | -2.402 (1.0) worse | -10.759 (1.0) worse | -2.679 (1.0) worse | -20.005 (1.0) worse |
| E5 | 1719 | 57.296 | 68.535 | 11.239 | 8.556 (0.1525) not_promoted | 6.345 (0.0975) not_promoted | 7.574 (0.1592) not_promoted | 16.319 (0.0045) promoted | 10.875 (0.3308) not_promoted |

Stratum-conditional policy (fitted on the fit years, scored on the test year):

- 2022: mean diff 8.556 over 258 sessions, p 0.030498475076246187, CI [-0.12412596899224798, 17.496323643410843]; choice {'classification=None|range_bin=None': 'E5'}
- 2023: mean diff 6.345 over 257 sessions, p 0.01949902504874756, CI [0.7123404669260698, 12.337836575875482]; choice {'classification=None|range_bin=None': 'E5'}
- 2024: mean diff 7.574 over 259 sessions, p 0.03184840757962102, CI [0.005535714285714095, 15.691686293436264]; choice {'classification=None|range_bin=None': 'E5'}
- 2025: mean diff 16.319 over 257 sessions, p 0.0008999550022498875, CI [6.156529182879378, 26.327666342412428]; choice {'classification=None|range_bin=None': 'E5'}
- 2026: mean diff 10.875 over 173 sessions, p 0.08269586520673966, CI [-3.6113265895953757, 26.419092485549132]; choice {'classification=None|range_bin=None': 'E5'}

