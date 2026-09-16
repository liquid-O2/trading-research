# P15-18 refinement — JJ-TBR

Run root `reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR | JJ-TBR:internal_rotation:F1:minutes=90 | 1219 | not claimed (no source-exact comparison) | rejected_by_evidence | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/JJ-TBR.md |
| JJ-TBR | JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75 | 1219 | not claimed (no source-exact comparison) | rejected_by_evidence | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/JJ-TBR.md |
| JJ-TBR | JJ-TBR:judas_reversal:S4:deadline_minutes=10 | 1219 | not claimed (no source-exact comparison) | promoted | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/JJ-TBR.md |
| JJ-TBR | JJ-TBR:single_extended:F2:volume_threshold_multiplier=0.75 | 1219 | not claimed (no source-exact comparison) | retained_baseline | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/JJ-TBR.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| JJ-TBR | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 249 opps / 1219 days / 5 blocks; first attribution location_miss; baseline retained |
| JJ-TBR | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 238 opps / 1219 days / 5 blocks; first attribution location_miss; baseline retained |
| JJ-TBR | P15-17 | promoted | pass | 0 | 0 | support 209 opps / 1219 days / 5 blocks; first attribution None; baseline retained |
| JJ-TBR | P15-17 | retained_baseline | pass | 0 | 0 | support 246 opps / 1219 days / 5 blocks; first attribution location_miss; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| JJ-TBR:judas_reversal:S4:deadline_minutes=10 | Sequence | 4.6758 | 209 | 417 |
| JJ-TBR:internal_rotation:F1:minutes=90 | Formation | 0.6220 | 249 | 229 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| JJ-TBR:internal_rotation:F1:minutes=90 | internal_rotation | Formation | inactive_retained | location_miss | holm |
| JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75 | internal_rotation | Formation | inactive_retained | location_miss | holm |
| JJ-TBR:judas_reversal:S4:deadline_minutes=10 | judas_reversal | Sequence | active_selected |  |  |
| JJ-TBR:single_extended:F2:volume_threshold_multiplier=0.75 | single_extended | Formation | inactive_retained | location_miss | no_improvement |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | Formation:JJ-TBR:single_extended:F2:volume_threshold_multiplier=0.75, Sequence:JJ-TBR:judas_reversal:S4:deadline_minutes=10 | False |
| 2023 | Formation:JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75, Sequence:JJ-TBR:judas_reversal:S4:deadline_minutes=10 | False |
| 2024 | Formation:JJ-TBR:internal_rotation:F2:volume_threshold_multiplier=0.75, Sequence:JJ-TBR:judas_reversal:S4:deadline_minutes=10 | False |
| 2025 | Formation:JJ-TBR:internal_rotation:F1:minutes=90, Sequence:JJ-TBR:judas_reversal:S4:deadline_minutes=10 | False |
| 2026 | Formation:JJ-TBR:internal_rotation:F1:minutes=90, Sequence:JJ-TBR:judas_reversal:S4:deadline_minutes=10 | False |
