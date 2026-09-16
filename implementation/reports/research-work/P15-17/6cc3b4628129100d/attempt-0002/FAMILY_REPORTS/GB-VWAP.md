# P15-17 breadth — GB-VWAP

Run root `reports/research-work/P15-17/6cc3b4628129100d/attempt-0002`. Every number below is a cell of `BREADTH_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| GB-VWAP | GB-VWAP:source_long:R1 | 1107 | not claimed (no source-exact comparison) | retained_baseline | reports/research-work/P15-17/6cc3b4628129100d/attempt-0002/FAMILY_REPORTS/GB-VWAP.md |
| GB-VWAP | GB-VWAP:source_long:R2 | 1107 | not claimed (no source-exact comparison) | retained_baseline | reports/research-work/P15-17/6cc3b4628129100d/attempt-0002/FAMILY_REPORTS/GB-VWAP.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| GB-VWAP | P15-17 | retained_baseline | pass | 0 | 0 | support 302 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| GB-VWAP | P15-17 | retained_baseline | pass | 0 | 0 | support 319 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| GB-VWAP:source_long:R2 | Reference | -0.6187 | 319 | 179 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| GB-VWAP:source_long:R1 | source_long | Reference | inactive_retained | location_miss | no_improvement |
| GB-VWAP:source_long:R2 | source_long | Reference | inactive_retained | location_miss | no_improvement |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | none | True |
| 2023 | none | True |
| 2024 | none | True |
| 2025 | none | True |
| 2026 | none | True |
