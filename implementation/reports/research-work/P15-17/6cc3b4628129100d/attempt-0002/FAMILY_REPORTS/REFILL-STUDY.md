# P15-17 breadth — REFILL-STUDY

Run root `reports/research-work/P15-17/6cc3b4628129100d/attempt-0002`. Every number below is a cell of `BREADTH_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| REFILL-STUDY | REFILL-STUDY:supplied_selected_order:M1 | 1094 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0002/FAMILY_REPORTS/REFILL-STUDY.md |
| REFILL-STUDY | REFILL-STUDY:supplied_selected_order:M2 | 1094 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0002/FAMILY_REPORTS/REFILL-STUDY.md |
| REFILL-STUDY | REFILL-STUDY:touch_record:M1 | 1094 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0002/FAMILY_REPORTS/REFILL-STUDY.md |
| REFILL-STUDY | REFILL-STUDY:touch_record:M2 | 1094 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0002/FAMILY_REPORTS/REFILL-STUDY.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| REFILL-STUDY | P15-17 | inconclusive_support | pass | 13 | 0 | support 0 opps / 1094 days / 5 blocks; first attribution frequency; baseline retained |
| REFILL-STUDY | P15-17 | inconclusive_support | pass | 13 | 0 | support 0 opps / 1094 days / 5 blocks; first attribution frequency; baseline retained |
| REFILL-STUDY | P15-17 | inconclusive_support | pass | 13 | 0 | support 0 opps / 1094 days / 5 blocks; first attribution frequency; baseline retained |
| REFILL-STUDY | P15-17 | inconclusive_support | pass | 13 | 0 | support 0 opps / 1094 days / 5 blocks; first attribution frequency; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| REFILL-STUDY:supplied_selected_order:M1 | Memory | -53.1362 | 0 | 21395 |
| REFILL-STUDY:supplied_selected_order:M2 | Memory | -53.1362 | 0 | 21395 |
| REFILL-STUDY:touch_record:M1 | Memory | -53.1362 | 0 | 21395 |
| REFILL-STUDY:touch_record:M2 | Memory | -53.1362 | 0 | 21395 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| REFILL-STUDY:supplied_selected_order:M1 | supplied_selected_order | Memory | inactive_retained | frequency | support |
| REFILL-STUDY:supplied_selected_order:M2 | supplied_selected_order | Memory | inactive_retained | frequency | support |
| REFILL-STUDY:touch_record:M1 | touch_record | Memory | inactive_retained | frequency | support |
| REFILL-STUDY:touch_record:M2 | touch_record | Memory | inactive_retained | frequency | support |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | none | True |
| 2023 | none | True |
| 2024 | none | True |
| 2025 | none | True |
| 2026 | none | True |
