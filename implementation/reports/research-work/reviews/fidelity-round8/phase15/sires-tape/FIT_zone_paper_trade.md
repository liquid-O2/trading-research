# Selection fit: /workspace/.scratch/a537e734/zone-pop/rows_paper_trade.jsonl

Rows 316324 (scored out of sample 216992); events a day 268.9; base rate 0.2502; out-of-sample AUC **0.507**; hold-out from 2026-04-01 untouched.

| test year | train rows | test rows | base rate | AUC |
| --- | ---: | ---: | ---: | ---: |
| 2023 | 99332 | 42943 | 0.2454 | 0.5015 |
| 2024 | 142275 | 57757 | 0.2514 | 0.5132 |
| 2025 | 200032 | 87891 | 0.2522 | 0.5062 |
| 2026 | 287923 | 28401 | 0.2487 | 0.508 |

| score decile | rows | label rate | mean MFE-MAE |
| ---: | ---: | ---: | ---: |
| 1 | 21700 | 0.2385 | -5.755 |
| 2 | 21700 | 0.2488 | -5.425 |
| 3 | 21699 | 0.2481 | -5.068 |
| 4 | 21699 | 0.2451 | -5.17 |
| 5 | 21699 | 0.2502 | -3.714 |
| 6 | 21699 | 0.2543 | -4.147 |
| 7 | 21699 | 0.2516 | -3.46 |
| 8 | 21699 | 0.2562 | -3.33 |
| 9 | 21699 | 0.251 | -2.75 |
| 10 | 21699 | 0.2583 | -0.257 |

Taking every event: label rate 0.2502, mean MFE-MAE -3.908.

| top-k a day | events | label rate | mean MFE-MAE |
| ---: | ---: | ---: | ---: |
| 3 | 2412 | 0.2662 | -6.897 |
| 5 | 4015 | 0.2555 | -5.53 |
| 10 | 8002 | 0.2574 | -4.717 |

| feature alone | out-of-sample AUC |
| --- | ---: |
| minutes_from_open | 0.5094 |
| prior_holds | 0.5091 |
| touch_number | 0.5091 |
| prior_breaks | 0.5065 |
| zone_age_minutes | 0.4954 |
| minutes_since_last_touch | 0.5033 |
| delta_120s_with_fade | 0.4971 |
| points_from_cash_open | 0.5029 |
| zone_width | 0.4971 |
| zone_contracts | 0.4975 |
| big_orders_with_fade_60s | 0.4976 |
| zone_aggressor_absorbed | 0.4976 |
| zone_orders | 0.4976 |
| points_above_overnight_high | 0.4977 |
| delta_30s_with_fade | 0.4982 |
| points_below_overnight_low | 0.5016 |
| zone_largest | 0.4985 |
| position_in_day_range | 0.4986 |
| points_from_prior_close | 0.4987 |
| approach_points_120s | 0.5013 |

| feature (joint model) | standardized coefficient, mean over folds |
| --- | ---: |
| prior_holds | -0.049 |
| minutes_since_last_touch__missing | 0.0409 |
| points_from_prior_vah | 0.0377 |
| points_below_overnight_low | -0.0362 |
| prior_breaks | 0.0358 |
| points_from_cash_open | 0.0352 |
| minutes_from_open | -0.0287 |
| delta_120s_with_fade | -0.0259 |
| points_above_overnight_high | -0.0232 |
| approach_points_120s | -0.0232 |
| zone_age_minutes | 0.0223 |
| points_from_prior_high | -0.0204 |
| points_from_prior_low | -0.0187 |
| zone_orders | 0.0152 |
| points_from_prior_poc | 0.0117 |
| zone_built_overnight | -0.0111 |
| points_from_prior_high__missing | -0.0107 |
| points_from_prior_low__missing | -0.0107 |
| position_in_day_range | -0.0102 |
| big_orders_into_level_60s | -0.0101 |
