# P15-18 refinement — KEANI-OPEN-ABOVE-VALUE

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0001`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 3 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 13 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |

## Multiplicity

Holm family of this decision stage: 18 candidates, 20000 bootstrap draws, smallest attainable p 0.000050, attainable Holm floor m/(B+1) = 0.000900 (admits a decision at .025).

| candidate_id | p_raw | p_holm | attainable floor | disposition |
| --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0 | 0.243588 | 1.000000 | 0.000900 | inconclusive_support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | 0.990500 | 1.000000 | 0.000900 | inconclusive_support |

## Support on both sides of the pair

| candidate_id | candidate opps | baseline opps | days | blocks | candidate gate | baseline gate | entry ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0 | 3 | 0 | 1107 | 5 | fail | fail |  |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | 13 | 0 | 1107 | 5 | fail | fail |  |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0 | Profile | 0.0397 | 3 | 0 |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | Sequence | -0.2579 | 13 | 0 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0 | source_long | Profile | inactive_retained | location_miss | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | source_long | Sequence | inactive_retained | location_miss | support |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | Sequence:KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | False |
| 2023 | Sequence:KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | False |
| 2024 | Profile:KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0 | False |
| 2025 | Profile:KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0 | False |
| 2026 | Profile:KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0 | False |
