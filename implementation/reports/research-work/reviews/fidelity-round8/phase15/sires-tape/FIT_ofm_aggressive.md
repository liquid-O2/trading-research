# Selection fit: /workspace/.scratch/a537e734/ofm-pop/rows.jsonl

Rows 12856 (scored out of sample 8701); events a day 10.9; base rate 0.5036; out-of-sample AUC **0.4987**; hold-out from 2026-04-01 untouched.

| test year | train rows | test rows | base rate | AUC |
| --- | ---: | ---: | ---: | ---: |
| 2023 | 4155 | 1305 | 0.5119 | 0.5026 |
| 2024 | 5460 | 2268 | 0.4969 | 0.4941 |
| 2025 | 7728 | 3831 | 0.5035 | 0.4934 |
| 2026 | 11559 | 1297 | 0.5073 | 0.5235 |

| score decile | rows | label rate | mean MFE-MAE |
| ---: | ---: | ---: | ---: |
| 1 | 871 | 0.5155 | 0.943 |
| 2 | 870 | 0.5264 | 1.464 |
| 3 | 870 | 0.4862 | -2.816 |
| 4 | 870 | 0.5092 | -0.093 |
| 5 | 870 | 0.4908 | -0.359 |
| 6 | 870 | 0.4839 | 0.948 |
| 7 | 870 | 0.4977 | -0.089 |
| 8 | 870 | 0.4977 | -0.07 |
| 9 | 870 | 0.5276 | 1.048 |
| 10 | 870 | 0.5011 | 3.307 |

Taking every event: label rate 0.5036, mean MFE-MAE 0.428.

| top-k a day | events | label rate | mean MFE-MAE |
| ---: | ---: | ---: | ---: |
| 3 | 2237 | 0.5123 | 0.481 |
| 5 | 3438 | 0.5061 | -0.345 |
| 10 | 5467 | 0.503 | -0.188 |

| feature alone | out-of-sample AUC |
| --- | ---: |
| points_from_cash_open | 0.5134 |
| prior_sequences_same_area | 0.4897 |
| retest_buy_share | 0.5077 |
| seconds_catalyst_to_release | 0.4923 |
| position_in_day_range | 0.4948 |
| prior_sequences_same_side_today | 0.4948 |
| stop_points | 0.4949 |
| retest_volume | 0.4951 |
| catalyst_lots | 0.5047 |
| seconds_release_to_failure | 0.4964 |
| squeeze_points | 0.4969 |
| points_from_prior_low | 0.5025 |
| points_beyond_overnight_high | 0.4976 |
| points_beyond_overnight_low | 0.4976 |
| minutes_from_open | 0.5024 |
| catalyst_orders | 0.5011 |
| points_from_prior_high | 0.4991 |
| seconds_failure_to_retest | 0.4992 |
| points_from_prior_close | 0.5002 |
| catalyst_width | 0.4999 |

| feature (joint model) | standardized coefficient, mean over folds |
| --- | ---: |
| points_beyond_overnight_high | 0.0879 |
| catalyst_lots | -0.0841 |
| catalyst_orders | 0.0825 |
| points_from_prior_high__missing | 0.0781 |
| points_from_prior_low__missing | 0.0781 |
| seconds_catalyst_to_release | 0.0696 |
| squeeze_points | -0.0598 |
| points_from_prior_low | -0.0591 |
| stop_points | -0.0453 |
| prior_sequences_same_side_today | 0.0414 |
| points_from_cash_open | 0.0397 |
| minutes_from_open | -0.0283 |
| catalyst_width | -0.0225 |
| prior_sequences_same_area | 0.0172 |
| retest_volume | -0.0162 |
| points_from_prior_close | -0.0127 |
| seconds_release_to_failure | -0.0116 |
| retest_buy_share | 0.0076 |
| points_from_prior_high | 0.0053 |
| points_from_prior_close__missing | 0.0017 |
