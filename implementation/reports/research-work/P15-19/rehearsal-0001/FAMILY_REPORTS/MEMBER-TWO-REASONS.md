# P15-19 exit study (E0 baseline) — MEMBER-TWO-REASONS

Run root `reports/research-work/P15-19/rehearsal-0001`. Every number below is a cell of `EXIT_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:planned_return_long:P1|E1 | 434 | not claimed (no source-exact comparison) | rejected_by_evidence | reports/research-work/P15-19/rehearsal-0001/FAMILY_REPORTS/MEMBER-TWO-REASONS.md |
| MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:planned_return_long:P1|E2 | 434 | not claimed (no source-exact comparison) | retained_baseline | reports/research-work/P15-19/rehearsal-0001/FAMILY_REPORTS/MEMBER-TWO-REASONS.md |
| MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:planned_return_long:P1|E3 | 434 | not claimed (no source-exact comparison) | retained_baseline | reports/research-work/P15-19/rehearsal-0001/FAMILY_REPORTS/MEMBER-TWO-REASONS.md |
| MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:planned_return_long:P1|E4 | 434 | not claimed (no source-exact comparison) | retained_baseline | reports/research-work/P15-19/rehearsal-0001/FAMILY_REPORTS/MEMBER-TWO-REASONS.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 434 opps / 434 days / 5 blocks; first attribution None; baseline retained |
| MEMBER-TWO-REASONS | P15-17 | retained_baseline | pass | 0 | 0 | support 434 opps / 434 days / 5 blocks; first attribution None; baseline retained |
| MEMBER-TWO-REASONS | P15-17 | retained_baseline | pass | 0 | 0 | support 434 opps / 434 days / 5 blocks; first attribution None; baseline retained |
| MEMBER-TWO-REASONS | P15-17 | retained_baseline | pass | 0 | 0 | support 434 opps / 434 days / 5 blocks; first attribution None; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS:planned_return_long:P1|E1 | EXIT | 0.0968 | 455 | 455 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS:planned_return_long:P1|E1 | planned_return_long | EXIT | inactive_retained |  | holm |
| MEMBER-TWO-REASONS:planned_return_long:P1|E2 | planned_return_long | EXIT | inactive_retained |  | no_improvement |
| MEMBER-TWO-REASONS:planned_return_long:P1|E3 | planned_return_long | EXIT | inactive_retained |  | no_improvement |
| MEMBER-TWO-REASONS:planned_return_long:P1|E4 | planned_return_long | EXIT | inactive_retained |  | no_improvement |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
