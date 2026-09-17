# P15-18 refinement — MEMBER-TWO-REASONS

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0001`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS | MEMBER-TWO-REASONS:planned_return_long:P1:bandwidth=0 | 1107 | not claimed (no source-exact comparison) | retained_baseline | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/MEMBER-TWO-REASONS.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS | P15-17 | retained_baseline | pass | 0 | 0 | support 294 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |

## Multiplicity

Holm family of this decision stage: 18 candidates, 20000 bootstrap draws, smallest attainable p 0.000050, attainable Holm floor m/(B+1) = 0.000900 (admits a decision at .025).

| candidate_id | p_raw | p_holm | attainable floor | disposition |
| --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS:planned_return_long:P1:bandwidth=0 | 0.921404 | 1.000000 | 0.000900 | retained_baseline |

## Support on both sides of the pair

| candidate_id | candidate opps | baseline opps | days | blocks | candidate gate | baseline gate | entry ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS:planned_return_long:P1:bandwidth=0 | 294 | 295 | 1107 | 5 | pass | pass | 1.00 |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS:planned_return_long:P1:bandwidth=0 | Profile | -0.0619 | 294 | 295 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| MEMBER-TWO-REASONS:planned_return_long:P1:bandwidth=0 | planned_return_long | Profile | inactive_retained | location_miss | no_improvement |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | none | True |
| 2023 | none | True |
| 2024 | none | True |
| 2025 | none |  |
| 2026 | none |  |
