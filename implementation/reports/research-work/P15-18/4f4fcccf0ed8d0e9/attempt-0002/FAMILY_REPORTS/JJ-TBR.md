# P15-18 refinement — JJ-TBR

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0001`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | JJ-TBR:internal_rotation:F1:minutes=90 | 1107 | not claimed (no source-exact comparison) | inconclusive_multiplicity | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/JJ-TBR.md |
| JJ-TBR | JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75 | 1107 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/JJ-TBR.md |
| JJ-TBR | JJ-TBR:judas_reversal:S4:deadline_minutes=10 | 1107 | not claimed (no source-exact comparison) | promoted | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/JJ-TBR.md |
| JJ-TBR | JJ-TBR:single_extended:F2:volume_threshold_multiplier=0.75 | 1107 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/JJ-TBR.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | P15-17 | inconclusive_multiplicity | pass | 0 | 0 | support 236 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| JJ-TBR | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 224 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| JJ-TBR | P15-17 | promoted | pass | 0 | 0 | support 203 opps / 1107 days / 5 blocks; first attribution None; baseline retained |
| JJ-TBR | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 225 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |

## Multiplicity

Holm family of this decision stage: 18 candidates, 20000 bootstrap draws, smallest attainable p 0.000050, attainable Holm floor m/(B+1) = 0.000900 (admits a decision at .025).

| candidate_id | p_raw | p_holm | attainable floor | disposition |
| --- | --- | --- | --- | --- |
| JJ-TBR:internal_rotation:F1:minutes=90 | 0.011049 | 0.143643 | 0.000900 | inconclusive_multiplicity |
| JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75 | 0.206040 | 1.000000 | 0.000900 | rejected_by_evidence |
| JJ-TBR:judas_reversal:S4:deadline_minutes=10 | 0.000050 | 0.000900 | 0.000900 | promoted |
| JJ-TBR:single_extended:F2:volume_threshold_multiplier=0.75 | 0.219239 | 1.000000 | 0.000900 | rejected_by_evidence |

## Support on both sides of the pair

| candidate_id | candidate opps | baseline opps | days | blocks | candidate gate | baseline gate | entry ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR:internal_rotation:F1:minutes=90 | 236 | 220 | 1107 | 5 | pass | pass | 1.07 |
| JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75 | 224 | 220 | 1107 | 5 | pass | pass | 1.02 |
| JJ-TBR:judas_reversal:S4:deadline_minutes=10 | 203 | 388 | 1107 | 5 | pass | pass | 0.52 |
| JJ-TBR:single_extended:F2:volume_threshold_multiplier=0.75 | 225 | 199 | 1107 | 5 | pass | pass | 1.13 |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| JJ-TBR:judas_reversal:S4:deadline_minutes=10 | Sequence | 4.8988 | 203 | 388 |
| JJ-TBR:internal_rotation:F1:minutes=90 | Formation | 0.6678 | 236 | 220 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR:internal_rotation:F1:minutes=90 | internal_rotation | Formation | inactive_retained | location_miss | holm |
| JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75 | internal_rotation | Formation | inactive_retained | location_miss | holm |
| JJ-TBR:judas_reversal:S4:deadline_minutes=10 | judas_reversal | Sequence | active_selected |  |  |
| JJ-TBR:single_extended:F2:volume_threshold_multiplier=0.75 | single_extended | Formation | inactive_retained | location_miss | holm |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | Formation:JJ-TBR:single_extended:F2:volume_threshold_multiplier=0.75, Sequence:JJ-TBR:judas_reversal:S4:deadline_minutes=10 | False |
| 2023 | Formation:JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75, Sequence:JJ-TBR:judas_reversal:S4:deadline_minutes=10 | False |
| 2024 | Formation:JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75, Sequence:JJ-TBR:judas_reversal:S4:deadline_minutes=10 | False |
| 2025 | Formation:JJ-TBR:internal_rotation:F1:minutes=90, Sequence:JJ-TBR:judas_reversal:S4:deadline_minutes=10 | False |
| 2026 | Formation:JJ-TBR:internal_rotation:F1:minutes=90, Sequence:JJ-TBR:judas_reversal:S4:deadline_minutes=10 | False |
