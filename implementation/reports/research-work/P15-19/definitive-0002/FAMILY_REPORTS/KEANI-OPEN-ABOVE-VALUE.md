# P15-19 exit study (E0 baseline) — KEANI-OPEN-ABOVE-VALUE

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-19/definitive-0001`. Every number below is a cell of `EXIT_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E1 | 6 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E2 | 6 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E3 | 5 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E4 | 5 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E1 | 15 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E2 | 16 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3 | 14 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |
| KEANI-OPEN-ABOVE-VALUE | KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E4 | 14 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-19/definitive-0002/FAMILY_REPORTS/KEANI-OPEN-ABOVE-VALUE.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 6 opps / 6 days / 2 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 6 opps / 6 days / 2 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 1 | 0 | support 5 opps / 5 days / 2 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 1 | 0 | support 5 opps / 5 days / 2 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 1 | 0 | support 15 opps / 15 days / 3 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 0 | 0 | support 16 opps / 16 days / 4 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 2 | 0 | support 14 opps / 14 days / 3 blocks; first attribution support; baseline retained |
| KEANI-OPEN-ABOVE-VALUE | P15-17 | inconclusive_support | pass | 2 | 0 | support 14 opps / 14 days / 3 blocks; first attribution support; baseline retained |

## Multiplicity

Holm family of this decision stage: 72 candidates, 20000 bootstrap draws, smallest attainable p 0.000050, attainable Holm floor m/(B+1) = 0.003600 (admits a decision at .025).

| candidate_id | p_raw | p_holm | attainable floor | disposition |
| --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E1 | 1.000000 | 1.000000 | 0.003600 | inconclusive_support |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E2 | 1.000000 | 1.000000 | 0.003600 | inconclusive_support |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E3 | 1.000000 | 1.000000 | 0.003600 | inconclusive_support |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E4 | 1.000000 | 1.000000 | 0.003600 | inconclusive_support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E1 | 0.204990 | 1.000000 | 0.003600 | inconclusive_support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E2 | 0.000050 | 0.003600 | 0.003600 | inconclusive_support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3 | 0.000050 | 0.003600 | 0.003600 | inconclusive_support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E4 | 0.000050 | 0.003600 | 0.003600 | inconclusive_support |

## Support on both sides of the pair

| candidate_id | candidate opps | baseline opps | days | blocks | candidate gate | baseline gate | entry ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E1 | 6 | 6 | 6 | 2 | fail | fail | 1.00 |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E2 | 6 | 6 | 6 | 2 | fail | fail | 1.00 |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E3 | 5 | 5 | 5 | 2 | fail | fail | 1.00 |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E4 | 5 | 5 | 5 | 2 | fail | fail | 1.00 |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E1 | 15 | 15 | 15 | 3 | fail | fail | 1.00 |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E2 | 16 | 16 | 16 | 4 | fail | fail | 1.00 |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3 | 14 | 14 | 14 | 3 | fail | fail | 1.00 |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E4 | 14 | 14 | 14 | 3 | fail | fail | 1.00 |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3 | EXIT | 18.8214 | 16 | 16 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E1 | source_long | EXIT | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E2 | source_long | EXIT | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E3 | source_long | EXIT | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:P4:bandwidth=0|E4 | source_long | EXIT | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E1 | source_long | EXIT | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E2 | source_long | EXIT | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E3 | source_long | EXIT | inactive_retained | support | support |
| KEANI-OPEN-ABOVE-VALUE:source_long:S4:favorable_ticks=1|E4 | source_long | EXIT | inactive_retained | support | support |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
