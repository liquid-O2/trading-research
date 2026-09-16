# P15-18 refinement — SAINT-AMT

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0002`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| SAINT-AMT | SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0002/FAMILY_REPORTS/SAINT-AMT.md |
| SAINT-AMT | SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | 1107 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0002/FAMILY_REPORTS/SAINT-AMT.md |
| SAINT-AMT | SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | 1107 | not claimed (no source-exact comparison) | rejected_by_evidence | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0002/FAMILY_REPORTS/SAINT-AMT.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| SAINT-AMT | P15-17 | inconclusive_support | pass | 0 | 0 | support 3 opps / 1107 days / 5 blocks; first attribution support; baseline retained |
| SAINT-AMT | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 362 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| SAINT-AMT | P15-17 | rejected_by_evidence | pass | 0 | 0 | support 277 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | Sequence | 0.1021 | 277 | 3 |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | Sequence | 0.0490 | 362 | 3 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | continuation_retest | Formation | inactive_retained | support | support |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | continuation_retest | Sequence | inactive_retained | location_miss | cost_stress |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | continuation_retest | Sequence | inactive_retained | location_miss | holm |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | False |
| 2023 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | False |
| 2024 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | False |
| 2025 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | False |
| 2026 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | False |
