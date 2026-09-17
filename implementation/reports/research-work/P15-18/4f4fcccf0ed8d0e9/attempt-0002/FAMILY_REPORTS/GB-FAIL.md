# P15-18 refinement — GB-FAIL

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0001`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| GB-FAIL | GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5 | 1107 | not claimed (no source-exact comparison) | promoted | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:F3:efficiency=0.5 | 1107 | not claimed (no source-exact comparison) | promoted | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:T4:shift_minutes=-15 | 1107 | not claimed (no source-exact comparison) | promoted | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/GB-FAIL.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| GB-FAIL | P15-17 | promoted | pass | 0 | 0 | support 453 opps / 1107 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | promoted | pass | 0 | 0 | support 570 opps / 1107 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | promoted | pass | 0 | 0 | support 648 opps / 1107 days / 5 blocks; first attribution None; baseline retained |

## Multiplicity

Holm family of this decision stage: 18 candidates, 20000 bootstrap draws, smallest attainable p 0.000050, attainable Holm floor m/(B+1) = 0.000900 (admits a decision at .025).

| candidate_id | p_raw | p_holm | attainable floor | disposition |
| --- | --- | --- | --- | --- |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5 | 0.000150 | 0.002400 | 0.000900 | promoted |
| GB-FAIL:previous_hour:F3:efficiency=0.5 | 0.003350 | 0.046898 | 0.000900 | promoted |
| GB-FAIL:previous_hour:T4:shift_minutes=-15 | 0.000050 | 0.000900 | 0.000900 | promoted |

## Support on both sides of the pair

| candidate_id | candidate opps | baseline opps | days | blocks | candidate gate | baseline gate | entry ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5 | 453 | 374 | 1107 | 5 | pass | pass | 1.21 |
| GB-FAIL:previous_hour:F3:efficiency=0.5 | 570 | 374 | 1107 | 5 | pass | pass | 1.52 |
| GB-FAIL:previous_hour:T4:shift_minutes=-15 | 648 | 374 | 1107 | 5 | pass | pass | 1.73 |

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
