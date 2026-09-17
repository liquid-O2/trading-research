# Selection variants against B0.3 (executed list, points a contract, no costs)

## JJ-TBR

baseline sessions 1719; years 2020-2026; test folds 2022, 2023, 2024, 2025, 2026

| variant | sessions | baseline mean | variant mean | mean diff | 2022 diff (p Holm) | 2023 diff (p Holm) | 2024 diff (p Holm) | 2025 diff (p Holm) | 2026 diff (p Holm) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 | 1719 | 50.628 | 44.204 | -6.424 | -8.125 (1.0) worse | -4.474 (1.0) worse | -7.311 (1.0) worse | -6.223 (1.0) worse | -15.434 (1.0) worse |
| E2 | 1719 | 50.628 | 56.035 | 5.408 | 2.117 (0.8254) not_promoted | 3.045 (0.2216) not_promoted | 2.265 (0.7872) not_promoted | 8.695 (0.0088) promoted | 10.201 (0.0602) not_promoted |
| E3 | 1719 | 50.628 | 51.382 | 0.755 | 4.413 (0.8254) not_promoted | 2.255 (0.6681) not_promoted | -1.503 (1.0) worse | 0.791 (1.0) not_promoted | -18.664 (1.0) worse |
| E4 | 1719 | 50.628 | 43.995 | -6.633 | -10.894 (1.0) worse | -4.929 (1.0) worse | -8.561 (1.0) worse | -1.258 (1.0) worse | -22.761 (1.0) worse |
| E5 | 1719 | 50.628 | 60.313 | 9.686 | 8.024 (0.1702) not_promoted | 5.353 (0.1535) not_promoted | 4.219 (0.612) not_promoted | 14.144 (0.0075) promoted | 11.069 (0.223) not_promoted |

Stratum-conditional policy (fitted on the fit years, scored on the test year):

- 2022: mean diff 8.024 over 258 sessions, p 0.03404829758512074, CI [-0.29097480620155014, 16.67648837209302]; choice {'classification=None|range_bin=None': 'E5'}
- 2023: mean diff 5.353 over 257 sessions, p 0.030698465076746163, CI [0.19136673151751019, 11.0003540856031]; choice {'classification=None|range_bin=None': 'E5'}
- 2024: mean diff 4.219 over 259 sessions, p 0.1223938803059847, CI [-2.5140144787644787, 11.664948841698841]; choice {'classification=None|range_bin=None': 'E5'}
- 2025: mean diff 14.144 over 257 sessions, p 0.0014999250037498126, CI [4.6699776264591435, 23.473101167315164]; choice {'classification=None|range_bin=None': 'E5'}
- 2026: mean diff 11.069 over 173 sessions, p 0.055747212639368035, CI [-1.850471098265896, 24.725692196531774]; choice {'classification=None|range_bin=None': 'E5'}

## GB-FAIL

baseline sessions 1721; years 2020-2026; test folds 2022, 2023, 2024, 2025, 2026

| variant | sessions | baseline mean | variant mean | mean diff | 2022 diff (p Holm) | 2023 diff (p Holm) | 2024 diff (p Holm) | 2025 diff (p Holm) | 2026 diff (p Holm) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 | 1721 | 44.699 | 44.67 | -0.03 | -4.979 (1.0) worse | 7.532 (0.136) not_promoted | -1.971 (1.0) worse | -4.524 (1.0) worse | 7.053 (1.0) not_promoted |
| E2 | 1721 | 44.699 | 45.379 | 0.68 | 5.964 (0.9375) not_promoted | 2.311 (1.0) not_promoted | 4.016 (1.0) not_promoted | -2.059 (1.0) worse | -10.376 (1.0) worse |
| E3 | 1721 | 44.699 | 38.653 | -6.046 | -9.119 (1.0) worse | -4.559 (1.0) worse | 3.196 (1.0) not_promoted | -28.669 (1.0) worse | -0.194 (1.0) worse |
| E4 | 1721 | 44.699 | 27.075 | -17.624 | -12.536 (1.0) worse | -9.084 (1.0) worse | -9.71 (1.0) worse | -43.842 (1.0) worse | -27.577 (1.0) worse |
| E5 | 1721 | 44.699 | 44.621 | -0.078 | -0.375 (1.0) worse | 1.645 (1.0) not_promoted | 9.655 (1.0) not_promoted | -17.699 (1.0) worse | 6.644 (1.0) not_promoted |

Stratum-conditional policy (fitted on the fit years, scored on the test year):

- 2022: mean diff -0.375 over 258 sessions, p 0.5070746462676866, CI [-25.50288081395349, 25.847254844961206]; choice {'day_model=None|bias=None': 'E5'}
- 2023: mean diff 2.311 over 257 sessions, p 0.3105344732763362, CI [-6.975795719844356, 12.264472762645905]; choice {'day_model=None|bias=None': 'E2'}
- 2024: mean diff 4.016 over 259 sessions, p 0.23973801309934503, CI [-6.895210424710426, 15.808751930501929]; choice {'day_model=None|bias=None': 'E2'}
- 2025: mean diff -2.059 over 257 sessions, p 0.5819209039548022, CI [-19.121455252918288, 16.865915369649706]; choice {'day_model=None|bias=None': 'E2'}
- 2026: mean diff -10.376 over 174 sessions, p 0.8432578371081446, CI [-31.098397988505745, 9.31160057471258]; choice {'day_model=None|bias=None': 'E2'}

