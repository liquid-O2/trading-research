# Selection fit: /workspace/.scratch/a537e734/zone-pop/rows.jsonl

Rows 337709 (scored out of sample 232030); events a day 286.8; base rate 0.5029; out-of-sample AUC **0.5085**; hold-out from 2026-04-01 untouched.

| test year | train rows | test rows | base rate | AUC |
| --- | ---: | ---: | ---: | ---: |
| 2023 | 105679 | 47212 | 0.5047 | 0.5063 |
| 2024 | 152891 | 62402 | 0.505 | 0.5046 |
| 2025 | 215293 | 92672 | 0.5011 | 0.5107 |
| 2026 | 307965 | 29744 | 0.5014 | 0.5126 |

| score decile | rows | label rate | mean MFE-MAE |
| ---: | ---: | ---: | ---: |
| 1 | 23203 | 0.488 | -4.03 |
| 2 | 23203 | 0.4936 | -2.201 |
| 3 | 23203 | 0.5014 | 0.671 |
| 4 | 23203 | 0.5005 | 1.217 |
| 5 | 23203 | 0.5072 | 0.945 |
| 6 | 23203 | 0.5032 | 1.11 |
| 7 | 23203 | 0.5015 | 1.39 |
| 8 | 23203 | 0.505 | 0.521 |
| 9 | 23203 | 0.509 | 1.231 |
| 10 | 23203 | 0.5201 | 1.779 |

Taking every event: label rate 0.5029, mean MFE-MAE 0.263.

| top-k a day | events | label rate | mean MFE-MAE |
| ---: | ---: | ---: | ---: |
| 3 | 2419 | 0.5308 | -2.696 |
| 5 | 4024 | 0.5293 | -1.086 |
| 10 | 8016 | 0.5349 | 0.825 |

| feature alone | out-of-sample AUC |
| --- | ---: |
| prior_holds | 0.5096 |
| touch_number | 0.5091 |
| prior_breaks | 0.5078 |
| points_from_prior_high | 0.5068 |
| points_from_prior_vah | 0.5059 |
| minutes_since_last_touch | 0.5046 |
| points_from_prior_low | 0.5046 |
| points_from_prior_poc | 0.5044 |
| points_from_prior_val | 0.5041 |
| position_in_day_range | 0.504 |
| points_from_cash_open | 0.5038 |
| points_above_overnight_high | 0.5034 |
| zone_contracts | 0.4969 |
| zone_largest | 0.4971 |
| minutes_from_open | 0.4974 |
| delta_120s_with_fade | 0.4975 |
| zone_orders | 0.4977 |
| delta_30s_with_fade | 0.4981 |
| points_below_overnight_low | 0.5016 |
| points_from_prior_close | 0.5016 |

| feature (joint model) | standardized coefficient, mean over folds |
| --- | ---: |
| minutes_since_last_touch__missing | 0.0856 |
| points_from_prior_poc | -0.0292 |
| points_from_cash_open | 0.0279 |
| points_from_prior_vah | 0.0226 |
| points_from_prior_val | 0.0218 |
| points_below_overnight_low | -0.0203 |
| prior_holds | -0.0195 |
| zone_built_overnight | -0.0177 |
| prior_breaks | 0.0157 |
| points_from_prior_high | 0.0135 |
| zone_age_minutes | 0.0132 |
| points_from_prior_close | -0.0114 |
| delta_120s_with_fade | -0.0104 |
| zone_width | -0.0094 |
| position_in_day_range | -0.009 |
| approach_points_30s | -0.0079 |
| zone_contracts | -0.0078 |
| approach_points_120s | -0.007 |
| zone_orders | 0.006 |
| big_orders_into_level_60s | -0.0049 |
