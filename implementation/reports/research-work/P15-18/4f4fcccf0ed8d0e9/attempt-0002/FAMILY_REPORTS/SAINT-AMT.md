# P15-18 refinement — SAINT-AMT

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0001`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| SAINT-AMT | SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=15+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/SAINT-AMT.md |
| SAINT-AMT | SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=5+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/SAINT-AMT.md |
| SAINT-AMT | SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/SAINT-AMT.md |
| SAINT-AMT | SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/SAINT-AMT.md |
| SAINT-AMT | SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | 1107 | not claimed (no source-exact comparison) | inconclusive_support | /workspace/implementation/reports/research-work/P15-18/4f4fcccf0ed8d0e9/attempt-0002/FAMILY_REPORTS/SAINT-AMT.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| SAINT-AMT | P15-17 | inconclusive_support | pass | 0 | 0 | support 393 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| SAINT-AMT | P15-17 | inconclusive_support | pass | 0 | 0 | support 316 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| SAINT-AMT | P15-17 | inconclusive_support | pass | 0 | 0 | support 3 opps / 1107 days / 5 blocks; first attribution support; baseline retained |
| SAINT-AMT | P15-17 | inconclusive_support | pass | 0 | 0 | support 362 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |
| SAINT-AMT | P15-17 | inconclusive_support | pass | 0 | 0 | support 277 opps / 1107 days / 5 blocks; first attribution location_miss; baseline retained |

## Multiplicity

Holm family of this decision stage: 18 candidates, 20000 bootstrap draws, smallest attainable p 0.000050, attainable Holm floor m/(B+1) = 0.000900 (admits a decision at .025).

| candidate_id | p_raw | p_holm | attainable floor | disposition |
| --- | --- | --- | --- | --- |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=15+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 0.098895 | 1.000000 | 0.000900 | inconclusive_support |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=5+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 0.001150 | 0.017249 | 0.000900 | inconclusive_support |
| SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 1.000000 | 1.000000 | 0.000900 | inconclusive_support |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | 0.357682 | 1.000000 | 0.000900 | inconclusive_support |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | 0.170441 | 1.000000 | 0.000900 | inconclusive_support |

## Support on both sides of the pair

| candidate_id | candidate opps | baseline opps | days | blocks | candidate gate | baseline gate | entry ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=15+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 393 | 3 | 1107 | 5 | pass | fail | 131.00 |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=5+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 316 | 3 | 1107 | 5 | pass | fail | 105.33 |
| SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | 3 | 3 | 1107 | 5 | fail | fail | 1.00 |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | 362 | 3 | 1107 | 5 | pass | fail | 120.67 |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | 277 | 3 | 1107 | 5 | pass | fail | 92.33 |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=5+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | Sequence | 0.2642 | 316 | 3 |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=15+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | Sequence | 0.1680 | 393 | 3 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=15+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | continuation_retest | Sequence | inactive_retained | location_miss | baseline_support |
| SAINT-AMT:COMBINED:SAINT-AMT:continuation_retest:S1:deadline_minutes=5+SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | continuation_retest | Sequence | inactive_retained | location_miss | baseline_support |
| SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75 | continuation_retest | Formation | inactive_retained | support | support |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | continuation_retest | Sequence | inactive_retained | location_miss | baseline_support |
| SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | continuation_retest | Sequence | inactive_retained | location_miss | baseline_support |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | False |
| 2023 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | False |
| 2024 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=15 | False |
| 2025 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | False |
| 2026 | Formation:SAINT-AMT:continuation_retest:F2:volume_threshold_multiplier=0.75, Sequence:SAINT-AMT:continuation_retest:S1:deadline_minutes=5 | False |
