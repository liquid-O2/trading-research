# P15-17 breadth — KEANI-OPEN-ABOVE-VALUE

Run root `reports/research-work/P15-17/6cc3b4628129100d/attempt-0003`. Every number below is a cell of `BREADTH_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:P1 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0003/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:P2 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0003/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:P3 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0003/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:P4 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0003/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S1 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0003/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S2 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0003/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S3 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0003/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-17/6cc3b4628129100d/attempt-0003/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 1 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 1 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 1 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 3 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 7 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 5 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 0 opps / 1107 days / 5 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 13 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4 | Profile | 0.0397 | 3 | 0 |
| KEANI-OPEN-ABOVE-VALUE:source_long:S2 | Sequence | -0.1066 | 5 | 0 |
| KEANI-OPEN-ABOVE-VALUE:source_long:S1 | Sequence | -0.1786 | 7 | 0 |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4 | Sequence | -0.2579 | 13 | 0 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:P1 | source_long | Profile | inactive_retained | location_miss | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:P2 | source_long | Profile | inactive_retained | location_miss | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:P3 | source_long | Profile | inactive_retained | location_miss | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4 | source_long | Profile | active_selected | location_miss | selected for refinement by inner tuning |
| KEANI-OPEN-ABOVE-VALUE:source_long:S1 | source_long | Sequence | inactive_retained | location_miss | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S2 | source_long | Sequence | inactive_retained | location_miss | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S3 | source_long | Sequence | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4 | source_long | Sequence | active_selected | location_miss | selected for refinement by inner tuning |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | Sequence:KEANI-OPEN-ABOVE-VALUE:source_long:S4 | False |
| 2023 | Sequence:KEANI-OPEN-ABOVE-VALUE:source_long:S4 | False |
| 2024 | Profile:KEANI-OPEN-ABOVE-VALUE:source_long:P4 | False |
| 2025 | Profile:KEANI-OPEN-ABOVE-VALUE:source_long:P4 | False |
| 2026 | Profile:KEANI-OPEN-ABOVE-VALUE:source_long:P4 | False |
