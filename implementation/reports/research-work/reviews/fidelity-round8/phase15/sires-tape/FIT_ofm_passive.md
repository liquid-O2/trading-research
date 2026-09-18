# Selection fit: /workspace/.scratch/a537e734/ofm-pop/rows.jsonl

Rows 14163 (scored out of sample 9606); events a day 12.1; base rate 0.509; out-of-sample AUC **0.517**; hold-out from 2026-04-01 untouched.

| test year | train rows | test rows | base rate | AUC |
| --- | ---: | ---: | ---: | ---: |
| 2023 | 4557 | 1444 | 0.5076 | 0.5397 |
| 2024 | 6001 | 2456 | 0.511 | 0.5076 |
| 2025 | 8457 | 4288 | 0.5096 | 0.5164 |
| 2026 | 12745 | 1418 | 0.5049 | 0.5376 |

| score decile | rows | label rate | mean MFE-MAE |
| ---: | ---: | ---: | ---: |
| 1 | 961 | 0.4703 | -6.338 |
| 2 | 961 | 0.514 | 2.615 |
| 3 | 961 | 0.5109 | 3.096 |
| 4 | 961 | 0.4943 | -2.375 |
| 5 | 961 | 0.5016 | 1.456 |
| 6 | 961 | 0.4964 | 1.337 |
| 7 | 960 | 0.526 | 3.61 |
| 8 | 960 | 0.5042 | 2.051 |
| 9 | 960 | 0.5219 | 1.497 |
| 10 | 960 | 0.55 | 2.319 |

Taking every event: label rate 0.509, mean MFE-MAE 0.926.

| top-k a day | events | label rate | mean MFE-MAE |
| ---: | ---: | ---: | ---: |
| 3 | 2265 | 0.5342 | 3.592 |
| 5 | 3512 | 0.5308 | 3.084 |
| 10 | 5700 | 0.5147 | 2.517 |

| feature alone | out-of-sample AUC |
| --- | ---: |
| seconds_failure_to_retest | 0.5219 |
| retest_volume | 0.5189 |
| catalyst_width | 0.5178 |
| stop_points | 0.5178 |
| points_from_cash_open | 0.5136 |
| seconds_catalyst_to_release | 0.4885 |
| catalyst_lots | 0.5099 |
| catalyst_orders | 0.509 |
| prior_sequences_same_area | 0.5083 |
| squeeze_points | 0.5067 |
| points_from_prior_close | 0.4933 |
| points_from_prior_high | 0.4953 |
| position_in_day_range | 0.4963 |
| points_beyond_overnight_low | 0.4967 |
| points_from_prior_low | 0.5029 |
| prior_sequences_same_side_today | 0.5027 |
| points_beyond_overnight_high | 0.4986 |
| retest_buy_share | 0.4992 |
| minutes_from_open | 0.4997 |
| seconds_release_to_failure | 0.5 |

| feature (joint model) | standardized coefficient, mean over folds |
| --- | ---: |
| catalyst_orders | 0.13 |
| points_beyond_overnight_low | -0.1142 |
| catalyst_lots | -0.0776 |
| prior_sequences_same_side_today | -0.0665 |
| points_from_prior_low | -0.0497 |
| retest_volume | 0.0488 |
| catalyst_width | -0.0477 |
| stop_points | -0.0477 |
| minutes_from_open | 0.0458 |
| position_in_day_range | -0.0426 |
| points_from_prior_high | -0.042 |
| seconds_release_to_failure | -0.0418 |
| seconds_failure_to_retest | 0.0274 |
| points_from_prior_high__missing | -0.0203 |
| points_from_prior_low__missing | -0.0203 |
| squeeze_points | -0.0173 |
| points_from_cash_open | 0.0158 |
| points_from_prior_close__missing | 0.0152 |
| points_beyond_overnight_high | 0.0133 |
| prior_sequences_same_area | 0.0117 |
