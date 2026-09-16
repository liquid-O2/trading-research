# P15-18 refinement — SIRES

Run root `/workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0002`. Every number below is a cell of `SELECTED_RULES_BY_FOLD.json and COMBINATION_RESULTS.json` in the same run root; per-day evidence is `daily/<date>.json` and `jobs/<date>/<candidate>.json.gz`.

## PHASE table

| family | variant | n | faithful_disagreements | status | report path |
| --- | --- | --- | --- | --- | --- |
| SIRES | SIRES:absorption_reward_retest:M1:max_prior_contacts=0 | 1094 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:clean_squeeze:M1:max_prior_contacts=0 | 1094 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0002/FAMILY_REPORTS/SIRES.md |
| SIRES | SIRES:defended_band_continuation:R1:dispersion=0.5 | 1094 | not claimed (no source-exact comparison) | retained_baseline | /workspace/.worktrees/p15-17-fast/implementation/reports/research-work/P15-18/d183bbbaa3e5b556/attempt-0002/FAMILY_REPORTS/SIRES.md |

## Audit table

| family | id | verdict | fixture | leakage | proxy-as-faithful | notes |
| --- | --- | --- | --- | --- | --- | --- |
| SIRES | P15-17 | retained_baseline | pass | 13 | 0 | support 1509 opps / 1094 days / 5 blocks; first attribution confirmation_delay; baseline retained |
| SIRES | P15-17 | retained_baseline | pass | 13 | 0 | support 319 opps / 1094 days / 5 blocks; first attribution coverage; baseline retained |
| SIRES | P15-17 | retained_baseline | pass | 13 | 0 | support 219 opps / 1094 days / 5 blocks; first attribution frequency; baseline retained |

## Quality–frequency Pareto set

| candidate_id | bank | mean paired improvement (points/day) | entries | baseline entries |
| --- | --- | --- | --- | --- |
| SIRES:clean_squeeze:M1:max_prior_contacts=0 | Memory | -0.4890 | 319 | 112 |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0 | Memory | -1.6609 | 1509 | 19 |

## Retention set

| candidate_id | branch | bank | status | first attribution | reason |
| --- | --- | --- | --- | --- | --- |
| SIRES:absorption_reward_retest:M1:max_prior_contacts=0 | absorption_reward_retest | Memory | inactive_retained | confirmation_delay | no_improvement |
| SIRES:clean_squeeze:M1:max_prior_contacts=0 | clean_squeeze | Memory | inactive_retained | coverage | no_improvement |
| SIRES:defended_band_continuation:R1:dispersion=0.5 | defended_band_continuation | Reference | inactive_retained | frequency | no_improvement |

## Fold selections (inner tuning only)

| outer fold | selected banks | retained baseline |
| --- | --- | --- |
| 2022 | Memory:SIRES:absorption_reward_retest:M1:max_prior_contacts=0, Reference:SIRES:defended_band_continuation:R1:dispersion=0.5 | False |
| 2023 | Memory:SIRES:absorption_reward_retest:M1:max_prior_contacts=0, Reference:SIRES:defended_band_continuation:R1:dispersion=0.5 | False |
| 2024 | Memory:SIRES:absorption_reward_retest:M1:max_prior_contacts=0, Reference:SIRES:defended_band_continuation:R1:dispersion=0.5 | False |
| 2025 | Memory:SIRES:clean_squeeze:M1:max_prior_contacts=0, Reference:SIRES:defended_band_continuation:R1:dispersion=0.5 | False |
| 2026 | Memory:SIRES:clean_squeeze:M1:max_prior_contacts=0, Reference:SIRES:defended_band_continuation:R1:dispersion=0.5 | False |
