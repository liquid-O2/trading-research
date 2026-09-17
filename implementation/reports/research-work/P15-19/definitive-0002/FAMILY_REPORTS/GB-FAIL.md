# P15-19 exit study (E0 baseline) — GB-FAIL

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001`. Every number below is a cell of `EXIT_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| GB-FAIL | GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E1 | 588 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E2 | 588 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E3 | 588 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E4 | 588 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:F3:efficiency=0.5|E1 | 671 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:F3:efficiency=0.5|E2 | 671 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:F3:efficiency=0.5|E3 | 669 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:F3:efficiency=0.5|E4 | 670 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:T4:shift_minutes=-15|E1 | 764 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:T4:shift_minutes=-15|E2 | 762 | not claimed (no source-exact comparison) | inconclusive_multiplicity | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:T4:shift_minutes=-15|E3 | 761 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |
| GB-FAIL | GB-FAIL:previous_hour:T4:shift_minutes=-15|E4 | 764 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/GB-FAIL.md |

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
| GB-FAIL | P15-17 | inconclusive_multiplicity | pass | 2 | 0 | support 936 opps / 762 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 3 | 0 | support 935 opps / 761 days / 5 blocks; first attribution None; baseline retained |
| GB-FAIL | P15-17 | retained_baseline | pass | 0 | 0 | support 940 opps / 764 days / 5 blocks; first attribution None; baseline retained |

## Multiplicity

Holm family of this decision stage: 72 candidates, 20000 bootstrap draws, smallest attainable p 0.000050, attainable Holm floor m/(B+1) = 0.003600 (admits a decision at .025).

| candidate_id | p_raw | p_holm | attainable floor | disposition |
| --- | --- | --- | --- | --- |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E1 | 0.586771 | 1.000000 | 0.003600 | retained_baseline |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E2 | 0.134343 | 1.000000 | 0.003600 | rejected_by_evidence |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E3 | 0.951452 | 1.000000 | 0.003600 | retained_baseline |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E4 | 0.862557 | 1.000000 | 0.003600 | retained_baseline |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E1 | 0.664817 | 1.000000 | 0.003600 | retained_baseline |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E2 | 0.697415 | 1.000000 | 0.003600 | retained_baseline |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E3 | 0.766112 | 1.000000 | 0.003600 | retained_baseline |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E4 | 0.653517 | 1.000000 | 0.003600 | retained_baseline |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E1 | 0.967752 | 1.000000 | 0.003600 | retained_baseline |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E2 | 0.004800 | 0.331183 | 0.003600 | inconclusive_multiplicity |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E3 | 0.977301 | 1.000000 | 0.003600 | retained_baseline |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E4 | 0.955302 | 1.000000 | 0.003600 | retained_baseline |

## Support on both sides of the pair

| candidate_id | candidate opps | baseline opps | days | blocks | candidate gate | baseline gate | entry ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E1 | 667 | 667 | 588 | 5 | pass | pass | 1.00 |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E2 | 667 | 667 | 588 | 5 | pass | pass | 1.00 |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E3 | 667 | 667 | 588 | 5 | pass | pass | 1.00 |
| GB-FAIL:COMBINED:GB-FAIL:previous_hour:T4:shift_minutes=-15+GB-FAIL:previous_hour:F3:efficiency=0.5|E4 | 667 | 667 | 588 | 5 | pass | pass | 1.00 |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E1 | 805 | 805 | 671 | 5 | pass | pass | 1.00 |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E2 | 805 | 805 | 671 | 5 | pass | pass | 1.00 |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E3 | 801 | 801 | 669 | 5 | pass | pass | 1.00 |
| GB-FAIL:previous_hour:F3:efficiency=0.5|E4 | 804 | 804 | 670 | 5 | pass | pass | 1.00 |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E1 | 940 | 940 | 764 | 5 | pass | pass | 1.00 |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E2 | 936 | 936 | 762 | 5 | pass | pass | 1.00 |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E3 | 935 | 935 | 761 | 5 | pass | pass | 1.00 |
| GB-FAIL:previous_hour:T4:shift_minutes=-15|E4 | 940 | 940 | 764 | 5 | pass | pass | 1.00 |

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
