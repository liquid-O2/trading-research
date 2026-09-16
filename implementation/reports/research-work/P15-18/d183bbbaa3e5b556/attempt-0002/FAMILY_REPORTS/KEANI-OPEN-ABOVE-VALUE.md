# P15-18 refinement — KEANI-OPEN-ABOVE-VALUE

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0002`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 13 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | Sequence | -0.2579 | 13 | 0 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | source_long | Sequence | inactive_retained | location_miss | support |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | Sequence:KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | False |
| 2023 | Sequence:KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1 | False |
| 2024 | none |  |
| 2025 | none |  |
| 2026 | none |  |
