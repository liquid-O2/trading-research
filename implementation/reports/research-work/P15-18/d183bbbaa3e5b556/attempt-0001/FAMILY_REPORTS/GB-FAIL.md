# P15-18 refinement — GB-FAIL

Run root `reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| GB-FAIL | GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5 | 1107 | not claimed (no source-exact comparison) | promoted | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:F3:efficiency=0.5 | 1107 | not claimed (no source-exact comparison) | promoted | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:T4:shift_minutes=-15 | 1107 | not claimed (no source-exact comparison) | promoted | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/GB-FAIL.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| GB-FAIL | P15-17 | promoted | pass | 0 | 0 | support 453 opps / 1107 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | promoted | pass | 0 | 0 | support 570 opps / 1107 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | promoted | pass | 0 | 0 | support 648 opps / 1107 days / 5 blocks; first attribution None; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| GB-FAIL:previous_hour:T4:shift_minutes=-15 | Timing | 5.5885 | 648 | 374 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5 | previous_hour | Timing | active_selected |  |  |
| GB-FAIL:previous_hour:F3:efficiency=0.5 | previous_hour | Formation | active_selected |  |  |
| GB-FAIL:previous_hour:T4:shift_minutes=-15 | previous_hour | Timing | active_selected |  |  |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | Formation:GB-FAIL:previous_hour:F3:efficiency=0.5, Timing:GB-FAIL:previous_hour:T4:shift_minutes=-15 | False |
| 2023 | Formation:GB-FAIL:previous_hour:F3:efficiency=0.5, Timing:GB-FAIL:previous_hour:T4:shift_minutes=-15 | False |
| 2024 | Formation:GB-FAIL:previous_hour:F3:efficiency=0.5, Timing:GB-FAIL:previous_hour:T4:shift_minutes=-15 | False |
| 2025 | Formation:GB-FAIL:previous_hour:F3:efficiency=0.5, Timing:GB-FAIL:previous_hour:T4:shift_minutes=-15 | False |
| 2026 | Formation:GB-FAIL:previous_hour:F3:efficiency=0.5, Timing:GB-FAIL:previous_hour:T4:shift_minutes=-15 | False |
