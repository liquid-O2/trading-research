# P15-18 refinement — SAINT-AMT

Run root `reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| SAINT-AMT | SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=15+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 1219 | not claimed (no source-exact comparison) | rejected_by_evidence | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/SAINT-AMT.md |
| SAINT-AMT | SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=5+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 1219 | not claimed (no source-exact comparison) | rejected_by_evidence | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/SAINT-AMT.md |
| SAINT-AMT | SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 1219 | not claimed (no source-exact comparison) | inconclusive_support | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/SAINT-AMT.md |
| SAINT-AMT | SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | 1219 | not claimed (no source-exact comparison) | rejected_by_evidence | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/SAINT-AMT.md |
| SAINT-AMT | SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | 1219 | not claimed (no source-exact comparison) | rejected_by_evidence | reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0001/FAMILY_REPORTS/SAINT-AMT.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| SAINT-AMT | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 407 opps / 1219 days / 5 blocks; first attribution location_miss; baseline retained |
| SAINT-AMT | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 327 opps / 1219 days / 5 blocks; first attribution location_miss; baseline retained |
| SAINT-AMT | P15-17 | inconclusive_support | pass | 0 | 0 | support 3 opps / 1219 days / 5 blocks; first attribution support; baseline retained |
| SAINT-AMT | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 386 opps / 1219 days / 5 blocks; first attribution location_miss; baseline retained |
| SAINT-AMT | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 296 opps / 1219 days / 5 blocks; first attribution location_miss; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | Sequence | 18.8361 | 296 | 3 |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | Sequence | 18.7758 | 386 | 3 |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=15+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | Sequence | 0.1429 | 407 | 3 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=15+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | continuation_retest | Sequence | inactive_retained | location_miss | holm |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=5+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | continuation_retest | Sequence | inactive_retained | location_miss | holm |
| SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | continuation_retest | Formation | inactive_retained | support | support |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | continuation_retest | Sequence | inactive_retained | location_miss | holm |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | continuation_retest | Sequence | inactive_retained | location_miss | holm |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | False |
| 2023 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | False |
| 2024 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | False |
| 2025 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | False |
| 2026 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | False |
