# Selection variants against B0.3 (executed list, points a contract, no costs)

## JJ-TBR

baseline sessions 1719; years 2020-2026; test folds 2022, 2023, 2024, 2025, 2026

| variant | sessions | baseline mean | variant mean | mean diff | 2022 diff (p Holm) | 2023 diff (p Holm) | 2024 diff (p Holm) | 2025 diff (p Holm) | 2026 diff (p Holm) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 | 1719 | 50.628 | 44.204 | -6.424 | -8.125 (1.0) worse | -4.474 (1.0) worse | -7.311 (1.0) worse | -6.223 (1.0) worse | -15.434 (1.0) worse |
| E2 | 1719 | 50.628 | 56.035 | 5.408 | 2.117 (0.8254) not_promoted | 3.045 (0.2216) not_promoted | 2.265 (0.7872) not_promoted | 8.695 (0.0088) promoted | 10.201 (0.0482) promoted |
| E3 | 1719 | 50.628 | 51.382 | 0.755 | 4.413 (0.8254) not_promoted | 2.255 (0.6681) not_promoted | -1.503 (1.0) worse | 0.791 (1.0) not_promoted | -18.664 (1.0) worse |
| E4 | 1719 | 50.628 | 43.995 | -6.633 | -10.894 (1.0) worse | -4.929 (1.0) worse | -8.561 (1.0) worse | -1.258 (1.0) worse | -22.761 (1.0) worse |

Stratum-conditional policy (fitted on the fit years, scored on the test year):

- 2022: mean diff 2.117 over 258 sessions, p 0.22453877306134692, CI [-3.4216104651162795, 7.700766472868211]; choice {'classification=None|range_bin=None': 'E2'}
- 2023: mean diff 2.255 over 257 sessions, p 0.22268886555672215, CI [-3.480101167315174, 8.044386186770419]; choice {'classification=None|range_bin=None': 'E3'}
- 2024: mean diff -1.503 over 259 sessions, p 0.6351182440877956, CI [-9.468317567567569, 7.0812750965250935]; choice {'classification=None|range_bin=None': 'E3'}
- 2025: mean diff 8.695 over 257 sessions, p 0.002199890005499725, CI [3.1445787937743193, 14.456882295719838]; choice {'classification=None|range_bin=None': 'E2'}
- 2026: mean diff 10.201 over 173 sessions, p 0.012049397530123494, CI [1.7729017341040465, 19.19754190751445]; choice {'classification=None|range_bin=None': 'E2'}

## GB-FAIL

baseline sessions 1721; years 2020-2026; test folds 2022, 2023, 2024, 2025, 2026

| variant | sessions | baseline mean | variant mean | mean diff | 2022 diff (p Holm) | 2023 diff (p Holm) | 2024 diff (p Holm) | 2025 diff (p Holm) | 2026 diff (p Holm) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 | 1721 | 44.699 | 44.67 | -0.03 | -4.979 (1.0) worse | 7.532 (0.1088) not_promoted | -1.971 (1.0) worse | -4.524 (1.0) worse | 7.053 (1.0) not_promoted |
| E2 | 1721 | 44.699 | 45.379 | 0.68 | 5.964 (0.75) not_promoted | 2.311 (0.9316) not_promoted | 4.016 (0.959) not_promoted | -2.059 (1.0) worse | -10.376 (1.0) worse |
| E3 | 1721 | 44.699 | 38.653 | -6.046 | -9.119 (1.0) worse | -4.559 (1.0) worse | 3.196 (1.0) not_promoted | -28.669 (1.0) worse | -0.194 (1.0) worse |
| E4 | 1721 | 44.699 | 27.075 | -17.624 | -12.536 (1.0) worse | -9.084 (1.0) worse | -9.71 (1.0) worse | -43.842 (1.0) worse | -27.577 (1.0) worse |

Stratum-conditional policy (fitted on the fit years, scored on the test year):

- 2022: mean diff 5.964 over 258 sessions, p 0.18749062546872655, CI [-6.745091085271318, 19.36740116279068]; choice {'day_model=None|bias=None': 'E2'}
- 2023: mean diff 2.311 over 257 sessions, p 0.3105344732763362, CI [-6.975795719844356, 12.264472762645905]; choice {'day_model=None|bias=None': 'E2'}
- 2024: mean diff 4.016 over 259 sessions, p 0.23973801309934503, CI [-6.895210424710426, 15.808751930501929]; choice {'day_model=None|bias=None': 'E2'}
- 2025: mean diff -2.059 over 257 sessions, p 0.5819209039548022, CI [-19.121455252918288, 16.865915369649706]; choice {'day_model=None|bias=None': 'E2'}
- 2026: mean diff -10.376 over 174 sessions, p 0.8432578371081446, CI [-31.098397988505745, 9.31160057471258]; choice {'day_model=None|bias=None': 'E2'}

