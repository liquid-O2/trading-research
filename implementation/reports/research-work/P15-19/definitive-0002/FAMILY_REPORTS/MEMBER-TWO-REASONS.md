# P15-19 exit study (E0 baseline) — MEMBER-TWO-REASONS

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001`. Every number below is a cell of `EXIT_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:planned_return_long:P1|E1 | 434 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/MEMBER-TWO-REASONS.md |
| MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:planned_return_long:P1|E2 | 434 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/MEMBER-TWO-REASONS.md |
| MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:planned_return_long:P1|E3 | 434 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/MEMBER-TWO-REASONS.md |
| MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:planned_return_long:P1|E4 | 434 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/MEMBER-TWO-REASONS.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 434 opps / 434 days / 5 blocks; first attribution None; baseline retained |
| MEMBER-TWO-REASONS | P15-17 | retained_baseline | pass | 0 | 0 | support 434 opps / 434 days / 5 blocks; first attribution None; baseline retained |
| MEMBER-TWO-REASONS | P15-17 | retained_baseline | pass | 0 | 0 | support 434 opps / 434 days / 5 blocks; first attribution None; baseline retained |
| MEMBER-TWO-REASONS | P15-17 | retained_baseline | pass | 0 | 0 | support 434 opps / 434 days / 5 blocks; first attribution None; baseline retained |

## Multiplicity

Holm family of this decision stage: 72 candidates, 20000 bootstrap draws, smallest attainable p 0.000050, attainable Holm floor m/(B+1) = 0.003600 (admits a decision at .025).

| candidate_id | p_raw | p_holm | attainable floor | disposition |
| --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS:planned_return_long:P1|E1 | 0.341383 | 1.000000 | 0.003600 | rejected_by_evidence |
| MEMBER-TWO-REASONS:planned_return_long:P1|E2 | 0.916254 | 1.000000 | 0.003600 | retained_baseline |
| MEMBER-TWO-REASONS:planned_return_long:P1|E3 | 0.999900 | 1.000000 | 0.003600 | retained_baseline |
| MEMBER-TWO-REASONS:planned_return_long:P1|E4 | 1.000000 | 1.000000 | 0.003600 | retained_baseline |

## Support on both sides of the pair

| candidate_id | candidate opps | baseline opps | days | blocks | candidate gate | baseline gate | entry ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS:planned_return_long:P1|E1 | 434 | 434 | 434 | 5 | pass | pass | 1.00 |
| MEMBER-TWO-REASONS:planned_return_long:P1|E2 | 434 | 434 | 434 | 5 | pass | pass | 1.00 |
| MEMBER-TWO-REASONS:planned_return_long:P1|E3 | 434 | 434 | 434 | 5 | pass | pass | 1.00 |
| MEMBER-TWO-REASONS:planned_return_long:P1|E4 | 434 | 434 | 434 | 5 | pass | pass | 1.00 |

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
