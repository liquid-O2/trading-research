# Selection variants against B0.3 (executed list, points a contract, no costs)

## GB-FAIL

baseline sessions 1742; years 2020-2026; test folds 2022, 2023, 2024, 2025, 2026

| variant | sessions | baseline mean | variant mean | mean diff | 2022 diff (p Holm) | 2023 diff (p Holm) | 2024 diff (p Holm) | 2025 diff (p Holm) | 2026 diff (p Holm) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GB-S-inside12-clean | 1742 | 3.484 | 3.115 | -0.37 | -6.288 (1.0) worse | 0.936 (1.0) not_promoted | -0.303 (1.0) worse | 0.759 (1.0) not_promoted | 6.331 (1.0) not_promoted |
| GB-anyadds | 1742 | 3.484 | 0.687 | -2.797 | -3.846 (1.0) worse | -4.813 (1.0) worse | -5.337 (1.0) worse | 10.71 (1.0) not_promoted | -17.048 (1.0) worse |
| GB-line1 | 1742 | 3.484 | -3.518 | -7.002 | -13.114 (1.0) worse | -7.232 (1.0) worse | -3.777 (1.0) worse | -23.276 (1.0) worse | 1.361 (1.0) not_promoted |
| GB-noadds | 1742 | 3.484 | -2.619 | -6.103 | -7.363 (1.0) worse | -6.236 (1.0) worse | -2.307 (1.0) worse | -11.018 (1.0) worse | -2.157 (1.0) worse |
| GB-noflips | 1742 | 3.484 | 1.07 | -2.414 | -4.556 (1.0) worse | -5.059 (1.0) worse | -5.588 (1.0) worse | -6.215 (1.0) worse | 7.231 (1.0) not_promoted |
| GB-noreenter | 1742 | 3.484 | 27.172 | 23.688 | 33.071 (0.0008) promoted | 16.521 (0.0017) promoted | 20.241 (0.0697) not_promoted | 5.219 (1.0) not_promoted | 38.36 (0.0178) promoted |
| GB-rt1 | 1742 | 3.484 | -4.388 | -7.872 | -11.796 (1.0) worse | -7.337 (1.0) worse | -9.972 (1.0) worse | -12.223 (1.0) worse | 7.196 (1.0) not_promoted |
| GB-rt2 | 1742 | 3.484 | 1.198 | -2.286 | -6.494 (1.0) worse | -0.196 (1.0) worse | -1.766 (1.0) worse | -3.248 (1.0) worse | 7.251 (1.0) not_promoted |
| GB-rt3 | 1742 | 3.484 | -0.157 | -3.642 | -5.336 (1.0) worse | -4.642 (1.0) worse | -2.438 (1.0) worse | 1.917 (1.0) not_promoted | -4.519 (1.0) worse |
| JJ-line1 | 1742 | 3.484 | 3.484 | 0.0 | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted |
| JJ-noadds | 1742 | 3.484 | 3.484 | 0.0 | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted |
| JJ-noflips | 1742 | 3.484 | 3.484 | 0.0 | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted |
| JJ-rt1 | 1742 | 3.484 | 3.484 | 0.0 | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted |
| JJ-rt2 | 1742 | 3.484 | 3.484 | 0.0 | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted |
| JJ-rt3 | 1742 | 3.484 | 3.484 | 0.0 | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted |
| JJ-rt4 | 1742 | 3.484 | 3.484 | 0.0 | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted |
| JJ-timeorder | 1742 | 3.484 | 3.484 | 0.0 | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted | 0.0 (1.0) not_promoted |

Stratum-conditional policy (fitted on the fit years, scored on the test year):

- 2022: mean diff 24.563 over 260 sessions, p 0.000599970001499925, CI [9.172666346153846, 39.24611730769229]; choice {'day_model=sweep_and_fail|bias=None': 'GB-noreenter', 'day_model=pullback_continuation|bias=None': 'GB-noreenter', 'day_model=sweep_and_fail|bias=long': 'GB-noreenter', 'day_model=sweep_and_fail|bias=short': 'GB-noreenter', 'day_model=pullback_continuation|bias=short': 'GB-rt1', 'day_model=pullback_continuation|bias=long': 'GB-noreenter'}
- 2023: mean diff 16.521 over 260 sessions, p 9.99950002499875e-05, CI [9.054542307692309, 23.726890384615384]; choice {'day_model=sweep_and_fail|bias=None': 'GB-noreenter', 'day_model=pullback_continuation|bias=None': 'GB-noreenter', 'day_model=sweep_and_fail|bias=long': 'GB-noreenter', 'day_model=sweep_and_fail|bias=short': 'GB-noreenter', 'day_model=pullback_continuation|bias=short': 'GB-noreenter', 'day_model=pullback_continuation|bias=long': 'GB-noreenter'}
- 2024: mean diff 20.241 over 262 sessions, p 0.004099795010249488, CI [3.6385314885496203, 35.420042938931275]; choice {'day_model=sweep_and_fail|bias=None': 'GB-noreenter', 'day_model=pullback_continuation|bias=None': 'GB-noreenter', 'day_model=sweep_and_fail|bias=long': 'GB-noreenter', 'day_model=sweep_and_fail|bias=short': 'GB-noreenter', 'day_model=pullback_continuation|bias=short': 'GB-noreenter', 'day_model=pullback_continuation|bias=long': 'GB-noreenter'}
- 2025: mean diff 5.219 over 261 sessions, p 0.23808809559522023, CI [-9.278150383141762, 19.062508620689652]; choice {'day_model=sweep_and_fail|bias=None': 'GB-noreenter', 'day_model=pullback_continuation|bias=None': 'GB-noreenter', 'day_model=sweep_and_fail|bias=long': 'GB-noreenter', 'day_model=sweep_and_fail|bias=short': 'GB-noreenter', 'day_model=pullback_continuation|bias=short': 'GB-noreenter', 'day_model=pullback_continuation|bias=long': 'GB-noreenter'}
- 2026: mean diff 38.36 over 176 sessions, p 0.0010499475026248687, CI [14.576485795454545, 63.02450142045453]; choice {'day_model=sweep_and_fail|bias=None': 'GB-noreenter', 'day_model=pullback_continuation|bias=None': 'GB-noreenter', 'day_model=sweep_and_fail|bias=long': 'GB-noreenter', 'day_model=sweep_and_fail|bias=short': 'GB-noreenter', 'day_model=pullback_continuation|bias=short': 'GB-noreenter', 'day_model=pullback_continuation|bias=long': 'GB-noreenter'}

