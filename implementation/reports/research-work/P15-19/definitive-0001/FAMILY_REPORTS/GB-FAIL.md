# P15-19 exit study (E0 baseline) — GB-FAIL

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001`. Every number below is a cell of `EXIT_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| GB-FAIL | GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E1 | 588 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E2 | 588 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E3 | 588 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E4 | 588 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:F3:efficiency=0.5|E1 | 671 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:F3:efficiency=0.5|E2 | 671 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:F3:efficiency=0.5|E3 | 669 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:F3:efficiency=0.5|E4 | 670 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:T4:shift_minutes=-15|E1 | 764 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:T4:shift_minutes=-15|E2 | 762 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:T4:shift_minutes=-15|E3 | 761 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:T4:shift_minutes=-15|E4 | 764 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001/FAMILY_REPORTS/GB-FAIL.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| GB-FAIL | P15-17 | retained_baseline | pass | 0 | 0 | support 667 opps / 588 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 667 opps / 588 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 0 | 0 | support 667 opps / 588 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 0 | 0 | support 667 opps / 588 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 0 | 0 | support 805 opps / 671 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 0 | 0 | support 805 opps / 671 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 2 | 0 | support 801 opps / 669 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 1 | 0 | support 804 opps / 670 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 0 | 0 | support 940 opps / 764 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | rejected_by_evidence | pass | 2 | 0 | support 936 opps / 762 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 3 | 0 | support 935 opps / 761 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 0 | 0 | support 940 opps / 764 days / 5 blocks; first attribution None; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E2 | EXIT | 1.2379 | 993 | 993 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E1 | COMBINED | EXIT | inactive_retained |  | no_improvement |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E2 | COMBINED | EXIT | inactive_retained |  | holm |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E3 | COMBINED | EXIT | inactive_retained |  | no_improvement |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E4 | COMBINED | EXIT | inactive_retained |  | no_improvement |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E1 | previous_hour | EXIT | inactive_retained |  | no_improvement |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E2 | previous_hour | EXIT | inactive_retained |  | no_improvement |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E3 | previous_hour | EXIT | inactive_retained |  | no_improvement |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E4 | previous_hour | EXIT | inactive_retained |  | no_improvement |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E1 | previous_hour | EXIT | inactive_retained |  | no_improvement |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E2 | previous_hour | EXIT | inactive_retained |  | holm |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E3 | previous_hour | EXIT | inactive_retained |  | no_improvement |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E4 | previous_hour | EXIT | inactive_retained |  | no_improvement |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
