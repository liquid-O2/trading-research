# P15-19 exit study (E0 baseline) — KEANI-OPEN-ABOVE-VALUE

Run root `reports/research-work/P15-19/rehearsal-0001`. Every number below is a cell of `EXIT_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E1 | 15 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-19/rehearsal-0001/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E2 | 16 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-19/rehearsal-0001/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3 | 14 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-19/rehearsal-0001/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E4 | 14 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-19/rehearsal-0001/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 1 | 0 | support 15 opps / 15 days / 3 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 16 opps / 16 days / 4 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 2 | 0 | support 14 opps / 14 days / 3 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 2 | 0 | support 14 opps / 14 days / 3 blocks; first attribution support; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3 | EXIT | 18.8214 | 16 | 16 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E1 | source_long | EXIT | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E2 | source_long | EXIT | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3 | source_long | EXIT | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E4 | source_long | EXIT | inactive_retained | support | support |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
