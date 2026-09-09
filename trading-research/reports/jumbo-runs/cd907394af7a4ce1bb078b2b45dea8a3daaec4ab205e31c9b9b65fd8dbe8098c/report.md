# Jumbo range, path and timing study: development

This report answers descriptive questions across every declared formation clock and source-specific mechanism. The complete year tables preserve each candidate, failed formation, unresolved outcome and exact source identity. The separate model and Location reports assess predictive and candidate quality; a frequency difference alone does not choose a clock.

## What population and clocks were measured?

| Instrument | Year | Intended actual cash dates |
|---|---:|---:|
| ES | 2020 | 253 |
| ES | 2021 | 252 |
| ES | 2022 | 251 |
| ES | 2023 | 250 |
| ES | 2024 | 252 |
| NQ | 2020 | 253 |
| NQ | 2021 | 252 |
| NQ | 2022 | 251 |
| NQ | 2023 | 250 |
| NQ | 2024 | 252 |

The acquired NQ/ES contract sequence is used with raw contract boundaries. Individual admitted minutes do not certify a whole window. The declared scenario publishes each minute bar one minute after its end; this is a latency assumption, not measured historical receipt. A 06:00–09:00 New York formation therefore ordinarily permits a 09:01 causal forecast and a 12:01 end for the following 180 minutes. Literal source forecasts and availability-delayed special-mechanism forecasts are separately identified.

OR15 is the disclosed 09:30–09:45 source benchmark. Its prior-volume activity variants and old generic opening-reference features are explicitly legacy benchmark constructions. It has no privileged interpretation as the user framework. Exact anchor supplements identify OR5, OR15, the 06:00–09:00 JTR range, the futures 08:00 range and New York 08:00 range separately.

## How often are ranges available, and how wide are they?

Every declared clock appears below. Widths are integer quarter-point ticks. The median column is the range of separately computed annual medians, not a pooled median. Missing dates and zero-width formations are retained. Exclusion counts can overlap when a date has several reasons.

| Instrument / clock | Available / intended | Zero width | Annual median width, min–max | Exclusion reasons |
|---|---:|---:|---|---|
| ES / AM | 1235 / 1258 | 0 | 102.00–184.00 | invalid_source_minutes: 1; missing_all_minutes: 19; missing_interior_minutes: 3; missing_last_minute: 1 |
| ES / Asia19 | 963 / 1258 | 0 | 47.00–92.00 | invalid_source_minutes: 18; missing_first_minute: 6; missing_interior_minutes: 279; missing_last_minute: 5; raw_contract_transition: 18 |
| ES / Asia20 | 1001 / 1258 | 0 | 41.00–84.00 | invalid_source_minutes: 13; missing_interior_minutes: 245; missing_last_minute: 5; raw_contract_transition: 13 |
| ES / JTR_fixed_01 | 1220 / 1258 | 0 | 16.00–30.50 | invalid_source_minutes: 13; missing_interior_minutes: 25; missing_last_minute: 4; raw_contract_transition: 13 |
| ES / JTR_fixed_02 | 1145 / 1258 | 0 | 9.00–18.00 | missing_first_minute: 8; missing_interior_minutes: 112; missing_last_minute: 12 |
| ES / JTR_fixed_03 | 1244 / 1258 | 0 | 24.00–52.00 | missing_first_minute: 2; missing_interior_minutes: 14; missing_last_minute: 4 |
| ES / JTR_fixed_04 | 1228 / 1258 | 0 | 51.00–99.00 | missing_first_minute: 3; missing_interior_minutes: 30; missing_last_minute: 1 |
| ES / JTR_fixed_04__shift_+10m | 1230 / 1258 | 0 | 52.00–98.00 | missing_first_minute: 6; missing_interior_minutes: 27; missing_last_minute: 2 |
| ES / JTR_fixed_04__shift_-10m | 1228 / 1258 | 0 | 50.00–98.00 | missing_first_minute: 3; missing_interior_minutes: 30; missing_last_minute: 2 |
| ES / JTR_fixed_05 | 1235 / 1258 | 0 | 56.50–109.00 | invalid_source_minutes: 1; missing_all_minutes: 19; missing_interior_minutes: 3; missing_last_minute: 1 |
| ES / JTR_fixed_06 | 1238 / 1258 | 0 | 47.50–89.00 | missing_all_minutes: 20 |
| ES / JTR_fixed_07 | 1238 / 1258 | 0 | 28.00–59.00 | missing_all_minutes: 20 |
| ES / JTR_fixed_08 | 1229 / 1258 | 0 | 30.00–68.00 | missing_all_minutes: 29 |
| ES / JTR_fixed_EST_sensitivity_01 | 1232 / 1258 | 0 | 13.50–28.00 | missing_first_minute: 3; missing_interior_minutes: 25; missing_last_minute: 5 |
| ES / JTR_fixed_EST_sensitivity_02 | 1190 / 1258 | 0 | 11.00–22.00 | missing_first_minute: 3; missing_interior_minutes: 67; missing_last_minute: 8 |
| ES / JTR_fixed_EST_sensitivity_03 | 1244 / 1258 | 0 | 24.00–44.00 | missing_interior_minutes: 14; missing_last_minute: 2 |
| ES / JTR_fixed_EST_sensitivity_04 | 1230 / 1258 | 0 | 67.00–134.00 | invalid_source_minutes: 1; missing_first_minute: 3; missing_interior_minutes: 24; missing_last_minute: 15; raw_contract_transition: 1 |
| ES / JTR_fixed_EST_sensitivity_05 | 1238 / 1258 | 0 | 45.50–88.00 | missing_all_minutes: 20 |
| ES / JTR_fixed_EST_sensitivity_06 | 1238 / 1258 | 0 | 37.00–75.00 | missing_all_minutes: 20 |
| ES / JTR_fixed_EST_sensitivity_07 | 1235 / 1258 | 0 | 27.00–55.00 | missing_all_minutes: 20; missing_first_minute: 1; missing_last_minute: 2 |
| ES / JTR_fixed_EST_sensitivity_08 | 992 / 1258 | 0 | 25.00–42.00 | missing_all_minutes: 29; missing_interior_minutes: 7; missing_last_minute: 230 |
| ES / London02 | 1206 / 1258 | 0 | 69.00–127.00 | missing_interior_minutes: 52; missing_last_minute: 1 |
| ES / NY08 | 1223 / 1258 | 0 | 147.00–291.00 | invalid_source_minutes: 1; missing_first_minute: 3; missing_interior_minutes: 11; missing_last_minute: 29; raw_contract_transition: 1 |
| ES / ONS03 | 1220 / 1258 | 0 | 57.00–105.00 | missing_first_minute: 2; missing_interior_minutes: 38; missing_last_minute: 4 |
| ES / ONS20 | 1102 / 1258 | 0 | 36.00–68.00 | invalid_source_minutes: 13; missing_interior_minutes: 141; missing_last_minute: 10; raw_contract_transition: 13 |
| ES / OR15 | 1235 / 1258 | 0 | 42.00–83.00 | invalid_source_minutes: 1; missing_all_minutes: 19; missing_last_minute: 4 |
| ES / OR15__shift_+10m | 1235 / 1258 | 0 | 39.00–72.00 | missing_all_minutes: 20; missing_first_minute: 3 |
| ES / OR15__shift_-10m | 1232 / 1258 | 0 | 31.00–58.00 | invalid_source_minutes: 1; missing_first_minute: 2; missing_interior_minutes: 7; missing_last_minute: 21; raw_contract_transition: 1 |
| ES / OR5 | 1237 / 1258 | 0 | 29.00–52.00 | invalid_source_minutes: 1; missing_all_minutes: 19; missing_last_minute: 2 |
| ES / OR5__shift_+10m | 1235 / 1258 | 0 | 20.00–42.00 | missing_all_minutes: 23 |
| ES / OR5__shift_-10m | 1252 / 1258 | 1 | 8.00–16.00 | missing_first_minute: 2; missing_interior_minutes: 4; missing_last_minute: 3 |
| ES / OR_activity_1_1 | 1151 / 1258 | 0 | 43.00–81.50 | activity_threshold_not_completed_before_cap: 87; insufficient_prior_activity_history: 20; invalid_source_minutes: 1; missing_all_minutes: 19; missing_interior_minutes: 3; missing_last_minute: 1 |
| ES / OR_activity_1_2 | 1183 / 1258 | 0 | 33.00–59.00 | activity_threshold_not_completed_before_cap: 55; insufficient_prior_activity_history: 20; invalid_source_minutes: 1; missing_all_minutes: 19; missing_interior_minutes: 2; missing_last_minute: 1 |
| ES / OR_activity_3_2 | 1137 / 1258 | 0 | 52.00–104.00 | activity_threshold_not_completed_before_cap: 101; insufficient_prior_activity_history: 20; invalid_source_minutes: 1; missing_all_minutes: 19; missing_interior_minutes: 3; missing_last_minute: 1 |
| ES / PIN015_Asia_UTC | 995 / 1258 | 0 | 48.00–93.50 | invalid_source_minutes: 18; missing_first_minute: 1; missing_interior_minutes: 247; missing_last_minute: 4; raw_contract_transition: 18 |
| ES / PIN015_London_UTC | 1213 / 1258 | 0 | 71.00–130.00 | missing_first_minute: 2; missing_interior_minutes: 45; missing_last_minute: 3 |
| ES / PIN015_NY_UTC | 284 / 1258 | 0 | 172.50–289.00 | invalid_source_minutes: 1; missing_first_minute: 2; missing_interior_minutes: 378; missing_last_minute: 835; raw_contract_transition: 1 |
| ES / PIN073_1 | 1232 / 1258 | 0 | 17.00–31.50 | missing_interior_minutes: 25; missing_last_minute: 5 |
| ES / PIN073_2 | 1251 / 1258 | 0 | 23.00–41.00 | missing_first_minute: 2; missing_interior_minutes: 6; missing_last_minute: 6 |
| ES / PIN073_3 | 1145 / 1258 | 0 | 9.00–18.00 | missing_first_minute: 8; missing_interior_minutes: 112; missing_last_minute: 12 |
| ES / PIN073_4 | 1238 / 1258 | 0 | 34.00–66.00 | missing_all_minutes: 20 |
| ES / PIN073_5 | 1229 / 1258 | 0 | 28.00–57.50 | missing_all_minutes: 29 |
| ES / PIN074_ref_00 | 1250 / 1258 | 33 | 2.00–4.00 | missing_all_minutes: 8 |
| ES / PIN074_ref_01 | 1256 / 1258 | 25 | 2.00–5.00 | missing_all_minutes: 2 |
| ES / PIN074_ref_03 | 1256 / 1258 | 3 | 6.00–12.00 | missing_all_minutes: 2 |
| ES / PIN074_ref_04 | 1258 / 1258 | 5 | 5.00–9.00 | none |
| ES / PIN074_ref_07 | 1255 / 1258 | 2 | 5.00–8.00 | missing_all_minutes: 3 |
| ES / PIN075_01 | 1142 / 1258 | 0 | 22.00–41.00 | invalid_source_minutes: 18; missing_all_minutes: 1; missing_interior_minutes: 99; missing_last_minute: 5 |
| ES / PIN075_02 | 1099 / 1258 | 0 | 37.00–73.00 | invalid_source_minutes: 13; missing_first_minute: 5; missing_interior_minutes: 144; missing_last_minute: 6; raw_contract_transition: 13 |
| ES / PIN075_03 | 1031 / 1258 | 0 | 37.00–66.00 | missing_first_minute: 4; missing_interior_minutes: 227; missing_last_minute: 4 |
| ES / PIN075_04 | 1241 / 1258 | 0 | 27.00–60.50 | missing_first_minute: 2; missing_interior_minutes: 17; missing_last_minute: 5 |
| ES / PIN075_05 | 1232 / 1258 | 0 | 34.00–70.00 | missing_first_minute: 2; missing_interior_minutes: 25; missing_last_minute: 3 |
| ES / PIN075_06 | 1229 / 1258 | 0 | 29.00–51.00 | missing_first_minute: 2; missing_interior_minutes: 29; missing_last_minute: 3 |
| ES / PIN075_07 | 1233 / 1258 | 0 | 53.00–98.00 | missing_first_minute: 2; missing_interior_minutes: 25; missing_last_minute: 6 |
| ES / PIN075_08 | 1238 / 1258 | 0 | 43.00–89.00 | missing_all_minutes: 20 |
| ES / PIN075_09 | 1238 / 1258 | 0 | 49.00–99.00 | missing_all_minutes: 20 |
| ES / PIN075_10 | 1238 / 1258 | 0 | 35.50–74.00 | missing_all_minutes: 20 |
| ES / PIN075_11 | 1228 / 1258 | 0 | 46.00–104.00 | missing_all_minutes: 20; missing_interior_minutes: 1; missing_last_minute: 9 |
| ES / PIN075_12 | 1229 / 1258 | 0 | 63.00–131.00 | missing_all_minutes: 29 |
| ES / PIN076_00_08 | 1250 / 1258 | 33 | 2.00–4.00 | missing_all_minutes: 8 |
| ES / PIN076_08_0930 | 1255 / 1258 | 1 | 4.00–8.00 | missing_all_minutes: 3 |
| ES / PIN078_daily_not_combined | 160 / 493 | 0 | 172.00–323.50 | invalid_source_minutes: 18; missing_first_minute: 168; missing_interior_minutes: 195; missing_last_minute: 2; raw_contract_transition: 18 |
| ES / PM | 1228 / 1258 | 0 | 76.00–159.50 | missing_all_minutes: 27; missing_first_minute: 1; missing_last_minute: 2 |
| ES / RTH0930 | 1225 / 1258 | 0 | 143.00–277.50 | invalid_source_minutes: 1; missing_all_minutes: 19; missing_interior_minutes: 4; missing_last_minute: 10 |
| ES / RTH_actual | 1234 / 1258 | 0 | 143.00–277.00 | invalid_source_minutes: 1; missing_all_minutes: 19; missing_interior_minutes: 4; missing_last_minute: 1 |
| ES / custom09 | 1232 / 1258 | 0 | 103.00–190.00 | invalid_source_minutes: 1; missing_first_minute: 2; missing_interior_minutes: 7; missing_last_minute: 20; raw_contract_transition: 1 |
| ES / day00 | 729 / 1258 | 0 | 170.00–323.50 | invalid_source_minutes: 1; missing_first_minute: 8; missing_interior_minutes: 525; missing_last_minute: 29; raw_contract_transition: 1 |
| ES / futures08 | 853 / 1258 | 0 | 145.00–297.00 | invalid_source_minutes: 1; missing_first_minute: 3; missing_interior_minutes: 381; missing_last_minute: 29; raw_contract_transition: 1 |
| ES / lunch | 1237 / 1258 | 0 | 38.50–81.00 | missing_all_minutes: 20; missing_last_minute: 1 |
| ES / magic_00 | 1096 / 1258 | 0 | 14.00–25.00 | missing_first_minute: 8; missing_interior_minutes: 160; missing_last_minute: 11 |
| ES / magic_01 | 1187 / 1258 | 0 | 17.00–35.00 | missing_first_minute: 2; missing_interior_minutes: 70; missing_last_minute: 5 |
| ES / magic_02 | 1222 / 1258 | 0 | 23.00–43.00 | missing_interior_minutes: 36; missing_last_minute: 4 |
| ES / magic_06 | 1230 / 1258 | 0 | 25.00–43.00 | missing_first_minute: 3; missing_interior_minutes: 28; missing_last_minute: 4 |
| ES / magic_07 | 1240 / 1258 | 0 | 27.00–49.00 | missing_first_minute: 3; missing_interior_minutes: 18; missing_last_minute: 1 |
| ES / magic_08 | 1249 / 1258 | 0 | 33.00–65.50 | missing_first_minute: 3; missing_interior_minutes: 9; missing_last_minute: 1 |
| ES / magic_23 | 1144 / 1258 | 0 | 13.00–27.00 | missing_first_minute: 1; missing_interior_minutes: 112; missing_last_minute: 10 |
| ES / prior_RTH_open_observed | 1233 / 1258 | 0 | 143.00–277.00 | invalid_source_minutes: 1; missing_all_minutes: 19; missing_interior_minutes: 4; missing_last_minute: 1; prior_actual_cash_session_outside_primary_admitted_history: 1 |
| ES / prior_RTH_preopen | 1233 / 1258 | 0 | 143.00–277.00 | invalid_source_minutes: 1; missing_all_minutes: 19; missing_interior_minutes: 4; missing_last_minute: 1; prior_actual_cash_session_outside_primary_admitted_history: 1 |
| ES / turn_earlier | 1235 / 1258 | 0 | 37.00–69.00 | invalid_source_minutes: 1; missing_all_minutes: 19; missing_last_minute: 4 |
| ES / turn_later | 1238 / 1258 | 0 | 27.00–53.00 | missing_all_minutes: 20 |
| ES / turn_source | 1235 / 1258 | 0 | 30.00–60.00 | missing_all_minutes: 21; missing_first_minute: 2 |
| NQ / AM | 1212 / 1258 | 0 | 512.00–854.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 3 |
| NQ / Asia19 | 1067 / 1258 | 0 | 190.00–354.00 | invalid_source_minutes: 42; missing_first_minute: 6; missing_interior_minutes: 154; missing_last_minute: 15; raw_contract_transition: 19 |
| NQ / Asia20 | 1097 / 1258 | 0 | 174.50–334.50 | invalid_source_minutes: 37; missing_first_minute: 2; missing_interior_minutes: 129; missing_last_minute: 15; raw_contract_transition: 13 |
| NQ / JTR_fixed_01 | 1193 / 1258 | 0 | 67.00–123.00 | invalid_source_minutes: 37; missing_first_minute: 2; missing_interior_minutes: 29; missing_last_minute: 9; raw_contract_transition: 13 |
| NQ / JTR_fixed_02 | 1167 / 1258 | 0 | 37.00–67.00 | invalid_source_minutes: 24; missing_all_minutes: 1; missing_first_minute: 6; missing_interior_minutes: 65; missing_last_minute: 13 |
| NQ / JTR_fixed_03 | 1217 / 1258 | 0 | 110.00–198.00 | invalid_source_minutes: 24; missing_first_minute: 2; missing_interior_minutes: 17; missing_last_minute: 7 |
| NQ / JTR_fixed_04 | 1193 / 1258 | 0 | 238.00–398.50 | invalid_source_minutes: 24; missing_first_minute: 8; missing_interior_minutes: 42; missing_last_minute: 8 |
| NQ / JTR_fixed_04__shift_+10m | 1194 / 1258 | 0 | 237.00–408.50 | invalid_source_minutes: 24; missing_first_minute: 9; missing_interior_minutes: 41; missing_last_minute: 4 |
| NQ / JTR_fixed_04__shift_-10m | 1193 / 1258 | 0 | 229.50–392.50 | invalid_source_minutes: 24; missing_first_minute: 4; missing_interior_minutes: 42; missing_last_minute: 6 |
| NQ / JTR_fixed_05 | 1212 / 1258 | 0 | 313.50–500.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 3 |
| NQ / JTR_fixed_06 | 1215 / 1258 | 0 | 234.00–398.00 | invalid_source_minutes: 23; missing_all_minutes: 20 |
| NQ / JTR_fixed_07 | 1215 / 1258 | 0 | 148.50–243.00 | invalid_source_minutes: 23; missing_all_minutes: 20 |
| NQ / JTR_fixed_08 | 1207 / 1258 | 0 | 131.00–264.00 | invalid_source_minutes: 22; missing_all_minutes: 29 |
| NQ / JTR_fixed_EST_sensitivity_01 | 1207 / 1258 | 0 | 61.00–104.00 | invalid_source_minutes: 24; missing_first_minute: 5; missing_interior_minutes: 28; missing_last_minute: 11 |
| NQ / JTR_fixed_EST_sensitivity_02 | 1190 / 1258 | 0 | 50.00–89.00 | invalid_source_minutes: 24; missing_first_minute: 12; missing_interior_minutes: 45; missing_last_minute: 13 |
| NQ / JTR_fixed_EST_sensitivity_03 | 1214 / 1258 | 0 | 102.50–161.50 | invalid_source_minutes: 24; missing_first_minute: 1; missing_interior_minutes: 20; missing_last_minute: 8 |
| NQ / JTR_fixed_EST_sensitivity_04 | 1201 / 1258 | 0 | 342.00–571.00 | invalid_source_minutes: 24; missing_first_minute: 3; missing_interior_minutes: 34; missing_last_minute: 16 |
| NQ / JTR_fixed_EST_sensitivity_05 | 1215 / 1258 | 0 | 238.00–374.00 | invalid_source_minutes: 23; missing_all_minutes: 20 |
| NQ / JTR_fixed_EST_sensitivity_06 | 1215 / 1258 | 0 | 203.00–319.00 | invalid_source_minutes: 23; missing_all_minutes: 20 |
| NQ / JTR_fixed_EST_sensitivity_07 | 1212 / 1258 | 0 | 138.50–228.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_first_minute: 1; missing_last_minute: 2 |
| NQ / JTR_fixed_EST_sensitivity_08 | 964 / 1258 | 0 | 105.00–168.00 | invalid_source_minutes: 22; missing_all_minutes: 29; missing_interior_minutes: 13; missing_last_minute: 230 |
| NQ / London02 | 1189 / 1258 | 0 | 300.00–496.00 | invalid_source_minutes: 24; missing_first_minute: 4; missing_interior_minutes: 47; missing_last_minute: 8 |
| NQ / NY08 | 1197 / 1258 | 0 | 759.00–1213.00 | invalid_source_minutes: 24; missing_first_minute: 5; missing_interior_minutes: 29; missing_last_minute: 29 |
| NQ / ONS03 | 1195 / 1258 | 0 | 246.00–411.00 | invalid_source_minutes: 24; missing_first_minute: 2; missing_interior_minutes: 41; missing_last_minute: 8 |
| NQ / ONS20 | 1138 / 1258 | 0 | 150.50–271.00 | invalid_source_minutes: 37; missing_first_minute: 2; missing_interior_minutes: 87; missing_last_minute: 12; raw_contract_transition: 13 |
| NQ / OR15 | 1212 / 1258 | 0 | 235.00–393.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 1; missing_last_minute: 3 |
| NQ / OR15__shift_+10m | 1212 / 1258 | 0 | 198.50–331.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_first_minute: 3 |
| NQ / OR15__shift_-10m | 1210 / 1258 | 0 | 168.00–276.00 | invalid_source_minutes: 24; missing_first_minute: 2; missing_interior_minutes: 7; missing_last_minute: 21 |
| NQ / OR5 | 1213 / 1258 | 0 | 157.00–256.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 1; missing_last_minute: 1 |
| NQ / OR5__shift_+10m | 1212 / 1258 | 0 | 112.00–192.00 | invalid_source_minutes: 23; missing_all_minutes: 23 |
| NQ / OR5__shift_-10m | 1226 / 1258 | 0 | 34.50–61.00 | invalid_source_minutes: 24; missing_all_minutes: 1; missing_first_minute: 1; missing_interior_minutes: 4; missing_last_minute: 4 |
| NQ / OR_activity_1_1 | 1141 / 1258 | 0 | 248.00–404.00 | activity_threshold_not_completed_before_cap: 97; insufficient_prior_activity_history: 20; invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 3 |
| NQ / OR_activity_1_2 | 1169 / 1258 | 0 | 188.50–299.00 | activity_threshold_not_completed_before_cap: 69; insufficient_prior_activity_history: 20; invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 3 |
| NQ / OR_activity_3_2 | 1113 / 1258 | 0 | 296.00–483.00 | activity_threshold_not_completed_before_cap: 125; insufficient_prior_activity_history: 20; invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 3 |
| NQ / PIN015_Asia_UTC | 1092 / 1258 | 0 | 206.00–370.00 | invalid_source_minutes: 42; missing_first_minute: 3; missing_interior_minutes: 129; missing_last_minute: 14; raw_contract_transition: 19 |
| NQ / PIN015_London_UTC | 1190 / 1258 | 0 | 320.00–516.00 | invalid_source_minutes: 24; missing_first_minute: 3; missing_interior_minutes: 46; missing_last_minute: 7 |
| NQ / PIN015_NY_UTC | 260 / 1258 | 0 | 820.00–1285.50 | invalid_source_minutes: 24; missing_first_minute: 5; missing_interior_minutes: 398; missing_last_minute: 837 |
| NQ / PIN073_1 | 1203 / 1258 | 0 | 75.00–126.00 | invalid_source_minutes: 24; missing_all_minutes: 1; missing_first_minute: 3; missing_interior_minutes: 31; missing_last_minute: 8 |
| NQ / PIN073_2 | 1219 / 1258 | 0 | 97.00–177.00 | invalid_source_minutes: 24; missing_first_minute: 4; missing_interior_minutes: 14; missing_last_minute: 5 |
| NQ / PIN073_3 | 1167 / 1258 | 0 | 37.00–67.00 | invalid_source_minutes: 24; missing_all_minutes: 1; missing_first_minute: 6; missing_interior_minutes: 65; missing_last_minute: 13 |
| NQ / PIN073_4 | 1215 / 1258 | 0 | 183.00–287.00 | invalid_source_minutes: 23; missing_all_minutes: 20 |
| NQ / PIN073_5 | 1207 / 1258 | 0 | 130.00–239.00 | invalid_source_minutes: 22; missing_all_minutes: 29 |
| NQ / PIN074_ref_00 | 1227 / 1258 | 6 | 7.00–13.00 | invalid_source_minutes: 24; missing_all_minutes: 7 |
| NQ / PIN074_ref_01 | 1223 / 1258 | 6 | 10.00–19.00 | invalid_source_minutes: 24; missing_all_minutes: 11 |
| NQ / PIN074_ref_03 | 1232 / 1258 | 3 | 28.00–49.00 | invalid_source_minutes: 24; missing_all_minutes: 2 |
| NQ / PIN074_ref_04 | 1233 / 1258 | 11 | 20.00–35.00 | invalid_source_minutes: 24; missing_all_minutes: 1 |
| NQ / PIN074_ref_07 | 1230 / 1258 | 5 | 20.00–31.00 | invalid_source_minutes: 24; missing_all_minutes: 4 |
| NQ / PIN075_01 | 1145 / 1258 | 0 | 83.50–146.00 | invalid_source_minutes: 41; missing_all_minutes: 1; missing_interior_minutes: 73; missing_last_minute: 5 |
| NQ / PIN075_02 | 1132 / 1258 | 0 | 158.00–277.00 | invalid_source_minutes: 37; missing_first_minute: 7; missing_interior_minutes: 92; missing_last_minute: 14; raw_contract_transition: 13 |
| NQ / PIN075_03 | 1115 / 1258 | 0 | 148.00–269.50 | invalid_source_minutes: 24; missing_first_minute: 9; missing_interior_minutes: 124; missing_last_minute: 10 |
| NQ / PIN075_04 | 1214 / 1258 | 0 | 133.00–228.00 | invalid_source_minutes: 24; missing_first_minute: 2; missing_interior_minutes: 21; missing_last_minute: 6 |
| NQ / PIN075_05 | 1203 / 1258 | 0 | 153.00–265.00 | invalid_source_minutes: 24; missing_first_minute: 7; missing_interior_minutes: 33; missing_last_minute: 8 |
| NQ / PIN075_06 | 1200 / 1258 | 0 | 120.00–203.50 | invalid_source_minutes: 24; missing_first_minute: 9; missing_interior_minutes: 35; missing_last_minute: 8 |
| NQ / PIN075_07 | 1198 / 1258 | 0 | 230.00–408.00 | invalid_source_minutes: 24; missing_first_minute: 13; missing_interior_minutes: 37; missing_last_minute: 5 |
| NQ / PIN075_08 | 1215 / 1258 | 0 | 221.00–394.00 | invalid_source_minutes: 23; missing_all_minutes: 20 |
| NQ / PIN075_09 | 1215 / 1258 | 0 | 258.50–433.00 | invalid_source_minutes: 23; missing_all_minutes: 20 |
| NQ / PIN075_10 | 1215 / 1258 | 0 | 192.00–308.00 | invalid_source_minutes: 23; missing_all_minutes: 20 |
| NQ / PIN075_11 | 1206 / 1258 | 0 | 226.00–428.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 1; missing_last_minute: 9 |
| NQ / PIN075_12 | 1205 / 1258 | 0 | 276.00–509.00 | invalid_source_minutes: 22; missing_all_minutes: 29; missing_interior_minutes: 2 |
| NQ / PIN076_00_08 | 1227 / 1258 | 6 | 7.00–13.00 | invalid_source_minutes: 24; missing_all_minutes: 7 |
| NQ / PIN076_08_0930 | 1229 / 1258 | 5 | 19.00–32.00 | invalid_source_minutes: 24; missing_all_minutes: 5 |
| NQ / PIN078_daily_not_combined | 188 / 493 | 0 | 796.00–1319.50 | invalid_source_minutes: 28; missing_first_minute: 168; missing_interior_minutes: 146; missing_last_minute: 2; raw_contract_transition: 19 |
| NQ / PM | 1204 / 1258 | 0 | 338.00–625.50 | invalid_source_minutes: 22; missing_all_minutes: 27; missing_first_minute: 1; missing_interior_minutes: 2; missing_last_minute: 2 |
| NQ / RTH0930 | 1201 / 1258 | 0 | 702.00–1160.50 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 6; missing_last_minute: 9 |
| NQ / RTH_actual | 1209 / 1258 | 0 | 702.00–1160.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 6 |
| NQ / custom09 | 1210 / 1258 | 0 | 516.00–863.00 | invalid_source_minutes: 24; missing_first_minute: 4; missing_interior_minutes: 15; missing_last_minute: 20 |
| NQ / day00 | 781 / 1258 | 0 | 792.00–1329.00 | invalid_source_minutes: 24; missing_first_minute: 7; missing_interior_minutes: 448; missing_last_minute: 29 |
| NQ / futures08 | 822 / 1258 | 0 | 727.00–1234.00 | invalid_source_minutes: 24; missing_first_minute: 5; missing_interior_minutes: 406; missing_last_minute: 29 |
| NQ / lunch | 1214 / 1258 | 0 | 188.00–333.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_last_minute: 1 |
| NQ / magic_00 | 1147 / 1258 | 0 | 56.00–106.00 | invalid_source_minutes: 24; missing_first_minute: 7; missing_interior_minutes: 89; missing_last_minute: 16 |
| NQ / magic_01 | 1187 / 1258 | 0 | 76.00–136.00 | invalid_source_minutes: 24; missing_first_minute: 11; missing_interior_minutes: 46; missing_last_minute: 15 |
| NQ / magic_02 | 1201 / 1258 | 0 | 99.00–168.00 | invalid_source_minutes: 24; missing_first_minute: 4; missing_interior_minutes: 34; missing_last_minute: 10 |
| NQ / magic_06 | 1199 / 1258 | 0 | 106.00–170.50 | invalid_source_minutes: 24; missing_first_minute: 8; missing_interior_minutes: 36; missing_last_minute: 8 |
| NQ / magic_07 | 1204 / 1258 | 0 | 124.00–191.50 | invalid_source_minutes: 24; missing_first_minute: 4; missing_interior_minutes: 31; missing_last_minute: 8 |
| NQ / magic_08 | 1207 / 1258 | 0 | 142.50–255.50 | invalid_source_minutes: 24; missing_all_minutes: 1; missing_first_minute: 4; missing_interior_minutes: 26; missing_last_minute: 7 |
| NQ / magic_23 | 1165 / 1258 | 0 | 54.00–103.00 | invalid_source_minutes: 24; missing_first_minute: 6; missing_interior_minutes: 72; missing_last_minute: 12 |
| NQ / prior_RTH_open_observed | 1208 / 1258 | 0 | 702.00–1160.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 6; prior_actual_cash_session_outside_primary_admitted_history: 1 |
| NQ / prior_RTH_preopen | 1208 / 1258 | 0 | 702.00–1160.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 6; prior_actual_cash_session_outside_primary_admitted_history: 1 |
| NQ / turn_earlier | 1212 / 1258 | 0 | 207.50–331.00 | invalid_source_minutes: 23; missing_all_minutes: 20; missing_interior_minutes: 1; missing_last_minute: 3 |
| NQ / turn_later | 1215 / 1258 | 0 | 148.00–249.00 | invalid_source_minutes: 23; missing_all_minutes: 20 |
| NQ / turn_source | 1212 / 1258 | 0 | 162.00–284.00 | invalid_source_minutes: 23; missing_all_minutes: 21; missing_first_minute: 2 |

## Which boundary paths occur after formation?

The following 180-minute table pools actual class counts across the displayed years for each instrument and clock. Its denominator is complete observed positive-width targets. Ordered high-then-low and low-then-high paths are displayed separately. Ambiguous first-side order remains a distinct observed OHLC class. These descriptive rates have different widths and forecast origins.

| Instrument / clock | Complete / intended | No break | High only | Low only | High then low | Low then high | Both edges | Ambiguous order |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ES / AM | 1225 / 1258 | 20.6% | 40.8% | 32.5% | 3.3% | 2.8% | 6.1% | 0.0% |
| ES / Asia19 | 962 / 1258 | 14.4% | 41.8% | 34.4% | 5.1% | 4.3% | 9.4% | 0.0% |
| ES / Asia20 | 1000 / 1258 | 11.7% | 41.1% | 34.5% | 6.7% | 6.0% | 12.7% | 0.0% |
| ES / JTR_fixed_01 | 1131 / 1258 | 1.8% | 34.6% | 30.9% | 16.0% | 16.8% | 32.8% | 0.0% |
| ES / JTR_fixed_02 | 1080 / 1258 | 0.0% | 19.4% | 14.7% | 33.2% | 32.6% | 65.9% | 0.1% |
| ES / JTR_fixed_03 | 1225 / 1258 | 1.8% | 34.2% | 31.3% | 15.5% | 17.2% | 32.7% | 0.0% |
| ES / JTR_fixed_04 | 1224 / 1258 | 1.6% | 32.4% | 30.1% | 19.0% | 17.0% | 35.9% | 0.0% |
| ES / JTR_fixed_04__shift_+10m | 1224 / 1258 | 1.6% | 32.8% | 30.0% | 18.6% | 16.9% | 35.5% | 0.0% |
| ES / JTR_fixed_04__shift_-10m | 1224 / 1258 | 1.7% | 32.0% | 30.1% | 18.5% | 17.6% | 36.2% | 0.0% |
| ES / JTR_fixed_05 | 1227 / 1258 | 1.1% | 36.8% | 31.5% | 15.9% | 14.8% | 30.6% | 0.0% |
| ES / JTR_fixed_06 | 1228 / 1258 | 1.1% | 35.3% | 32.2% | 15.6% | 15.8% | 31.4% | 0.0% |
| ES / JTR_fixed_07 | 1228 / 1258 | 0.3% | 29.5% | 21.6% | 24.0% | 24.5% | 48.6% | 0.1% |
| ES / JTR_fixed_08 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / JTR_fixed_EST_sensitivity_01 | 1090 / 1258 | 1.4% | 36.1% | 30.4% | 16.7% | 15.5% | 32.2% | 0.0% |
| ES / JTR_fixed_EST_sensitivity_02 | 1158 / 1258 | 0.0% | 18.8% | 16.3% | 31.0% | 33.8% | 64.9% | 0.1% |
| ES / JTR_fixed_EST_sensitivity_03 | 1221 / 1258 | 1.2% | 36.4% | 28.6% | 15.2% | 18.7% | 33.8% | 0.0% |
| ES / JTR_fixed_EST_sensitivity_04 | 1228 / 1258 | 3.9% | 38.3% | 35.7% | 11.6% | 10.5% | 22.1% | 0.0% |
| ES / JTR_fixed_EST_sensitivity_05 | 1228 / 1258 | 0.8% | 34.4% | 29.1% | 17.0% | 18.6% | 35.7% | 0.1% |
| ES / JTR_fixed_EST_sensitivity_06 | 1228 / 1258 | 0.7% | 33.7% | 27.6% | 19.7% | 18.3% | 38.0% | 0.0% |
| ES / JTR_fixed_EST_sensitivity_07 | 992 / 1258 | 0.2% | 30.5% | 21.2% | 24.1% | 24.0% | 48.1% | 0.0% |
| ES / JTR_fixed_EST_sensitivity_08 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / London02 | 1204 / 1258 | 5.3% | 39.6% | 33.0% | 12.4% | 9.1% | 22.1% | 0.6% |
| ES / NY08 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / ONS03 | 1216 / 1258 | 5.6% | 43.1% | 31.5% | 11.4% | 8.1% | 19.8% | 0.3% |
| ES / ONS20 | 1001 / 1258 | 22.2% | 39.9% | 33.5% | 3.1% | 1.4% | 4.5% | 0.0% |
| ES / OR15 | 1235 / 1258 | 0.2% | 29.1% | 25.2% | 21.8% | 23.6% | 45.4% | 0.0% |
| ES / OR15__shift_+10m | 1235 / 1258 | 0.2% | 28.5% | 22.9% | 25.5% | 22.7% | 48.4% | 0.2% |
| ES / OR15__shift_-10m | 1232 / 1258 | 0.1% | 21.8% | 19.6% | 28.7% | 29.7% | 58.5% | 0.2% |
| ES / OR5 | 1235 / 1258 | 0.0% | 20.0% | 17.6% | 30.1% | 32.1% | 62.4% | 0.2% |
| ES / OR5__shift_+10m | 1235 / 1258 | 0.0% | 18.2% | 13.3% | 36.4% | 31.8% | 68.5% | 0.3% |
| ES / OR5__shift_-10m | 1232 / 1258 | 0.0% | 7.4% | 6.6% | 42.7% | 42.1% | 86.0% | 1.2% |
| ES / OR_activity_1_1 | 1147 / 1258 | 0.4% | 29.2% | 25.2% | 22.1% | 23.0% | 45.2% | 0.0% |
| ES / OR_activity_1_2 | 1181 / 1258 | 0.2% | 22.2% | 19.5% | 28.5% | 29.7% | 58.2% | 0.0% |
| ES / OR_activity_3_2 | 1134 / 1258 | 1.1% | 34.5% | 30.2% | 15.9% | 18.3% | 34.1% | 0.0% |
| ES / PIN015_Asia_UTC | 993 / 1258 | 17.7% | 39.4% | 34.0% | 4.8% | 4.0% | 8.9% | 0.0% |
| ES / PIN015_London_UTC | 1212 / 1258 | 5.6% | 40.1% | 33.0% | 11.5% | 9.7% | 21.3% | 0.2% |
| ES / PIN015_NY_UTC | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / PIN073_1 | 1217 / 1258 | 0.1% | 27.3% | 20.9% | 26.3% | 25.5% | 51.8% | 0.0% |
| ES / PIN073_2 | 1232 / 1258 | 0.0% | 18.3% | 14.9% | 35.8% | 30.3% | 66.8% | 0.7% |
| ES / PIN073_3 | 1080 / 1258 | 0.0% | 19.4% | 14.7% | 33.2% | 32.6% | 65.9% | 0.1% |
| ES / PIN073_4 | 1228 / 1258 | 0.6% | 32.2% | 25.0% | 22.1% | 20.1% | 42.2% | 0.0% |
| ES / PIN073_5 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / PIN074_ref_00 | 1064 / 1258 | 0.0% | 6.8% | 6.2% | 43.0% | 43.3% | 87.0% | 0.8% |
| ES / PIN074_ref_01 | 1168 / 1258 | 0.0% | 5.4% | 5.5% | 45.5% | 42.6% | 89.1% | 1.0% |
| ES / PIN074_ref_03 | 1228 / 1258 | 0.0% | 11.2% | 9.4% | 38.7% | 40.1% | 79.5% | 0.7% |
| ES / PIN074_ref_04 | 1220 / 1258 | 0.0% | 11.3% | 10.0% | 40.2% | 37.0% | 78.7% | 1.5% |
| ES / PIN074_ref_07 | 1231 / 1258 | 0.0% | 5.7% | 5.6% | 45.0% | 43.3% | 88.7% | 0.4% |
| ES / PIN075_01 | 1084 / 1258 | 5.1% | 33.8% | 32.7% | 13.4% | 15.0% | 28.4% | 0.0% |
| ES / PIN075_02 | 967 / 1258 | 33.4% | 36.7% | 28.5% | 0.8% | 0.5% | 1.3% | 0.0% |
| ES / PIN075_03 | 1029 / 1258 | 5.4% | 39.3% | 35.9% | 10.8% | 8.6% | 19.4% | 0.0% |
| ES / PIN075_04 | 1222 / 1258 | 4.4% | 38.6% | 33.5% | 12.1% | 11.4% | 23.5% | 0.0% |
| ES / PIN075_05 | 1219 / 1258 | 8.2% | 42.9% | 34.1% | 7.5% | 7.2% | 14.8% | 0.0% |
| ES / PIN075_06 | 1221 / 1258 | 0.7% | 29.5% | 23.2% | 27.6% | 18.9% | 46.6% | 0.1% |
| ES / PIN075_07 | 1227 / 1258 | 1.5% | 33.4% | 30.3% | 17.8% | 16.9% | 34.7% | 0.1% |
| ES / PIN075_08 | 1228 / 1258 | 0.4% | 33.8% | 28.8% | 19.2% | 17.8% | 37.0% | 0.0% |
| ES / PIN075_09 | 1228 / 1258 | 3.1% | 38.8% | 32.8% | 12.7% | 12.5% | 25.2% | 0.0% |
| ES / PIN075_10 | 1228 / 1258 | 1.0% | 34.6% | 26.1% | 19.1% | 19.2% | 38.3% | 0.0% |
| ES / PIN075_11 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / PIN075_12 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / PIN076_00_08 | 1064 / 1258 | 0.0% | 6.8% | 6.2% | 43.0% | 43.3% | 87.0% | 0.8% |
| ES / PIN076_08_0930 | 1232 / 1258 | 0.0% | 4.4% | 5.2% | 47.1% | 41.8% | 90.4% | 1.5% |
| ES / PIN078_daily_not_combined | 0 / 493 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / PM | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / RTH0930 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / RTH_actual | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / custom09 | 1223 / 1258 | 22.0% | 40.1% | 32.2% | 3.0% | 2.6% | 5.6% | 0.0% |
| ES / day00 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / futures08 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| ES / lunch | 1228 / 1258 | 1.3% | 35.1% | 24.2% | 20.0% | 19.3% | 39.4% | 0.1% |
| ES / magic_00 | 1079 / 1258 | 0.2% | 23.9% | 18.7% | 29.9% | 27.2% | 57.2% | 0.0% |
| ES / magic_01 | 1182 / 1258 | 0.2% | 25.4% | 22.7% | 24.6% | 27.2% | 51.8% | 0.0% |
| ES / magic_02 | 1214 / 1258 | 1.2% | 32.5% | 27.9% | 20.1% | 18.3% | 38.4% | 0.0% |
| ES / magic_06 | 1224 / 1258 | 0.1% | 22.9% | 18.7% | 33.7% | 24.3% | 58.3% | 0.2% |
| ES / magic_07 | 1231 / 1258 | 0.2% | 18.0% | 19.6% | 32.1% | 29.7% | 62.3% | 0.6% |
| ES / magic_08 | 1232 / 1258 | 0.7% | 25.3% | 22.3% | 26.7% | 24.8% | 51.6% | 0.1% |
| ES / magic_23 | 1030 / 1258 | 1.6% | 30.0% | 27.3% | 21.8% | 19.3% | 41.2% | 0.0% |
| ES / prior_RTH_open_observed | 1210 / 1258 | 19.1% | 44.9% | 32.1% | 2.9% | 1.1% | 4.0% | 0.0% |
| ES / prior_RTH_preopen | 1210 / 1258 | 18.7% | 45.2% | 32.2% | 3.0% | 0.9% | 3.9% | 0.0% |
| ES / turn_earlier | 1235 / 1258 | 0.2% | 25.4% | 21.9% | 26.2% | 26.3% | 52.5% | 0.0% |
| ES / turn_later | 1230 / 1258 | 0.1% | 23.8% | 18.1% | 30.2% | 27.6% | 58.0% | 0.2% |
| ES / turn_source | 1235 / 1258 | 0.0% | 24.0% | 20.5% | 27.4% | 28.0% | 55.5% | 0.1% |
| NQ / AM | 1201 / 1258 | 25.9% | 39.8% | 30.6% | 2.2% | 1.4% | 3.7% | 0.0% |
| NQ / Asia19 | 1066 / 1258 | 16.1% | 41.1% | 32.6% | 4.8% | 5.3% | 10.1% | 0.0% |
| NQ / Asia20 | 1096 / 1258 | 12.8% | 42.0% | 32.9% | 6.3% | 6.0% | 12.3% | 0.0% |
| NQ / JTR_fixed_01 | 1151 / 1258 | 1.6% | 34.5% | 30.4% | 16.1% | 17.5% | 33.5% | 0.0% |
| NQ / JTR_fixed_02 | 1139 / 1258 | 0.1% | 19.8% | 16.1% | 32.6% | 31.3% | 64.0% | 0.1% |
| NQ / JTR_fixed_03 | 1197 / 1258 | 2.0% | 33.0% | 31.2% | 17.4% | 16.5% | 33.8% | 0.0% |
| NQ / JTR_fixed_04 | 1193 / 1258 | 1.2% | 28.8% | 27.0% | 22.0% | 21.0% | 43.0% | 0.0% |
| NQ / JTR_fixed_04__shift_+10m | 1194 / 1258 | 1.3% | 28.9% | 26.5% | 22.4% | 20.9% | 43.4% | 0.1% |
| NQ / JTR_fixed_04__shift_-10m | 1193 / 1258 | 0.9% | 28.4% | 27.7% | 22.0% | 21.0% | 43.0% | 0.0% |
| NQ / JTR_fixed_05 | 1205 / 1258 | 2.1% | 39.6% | 33.9% | 13.1% | 11.3% | 24.4% | 0.0% |
| NQ / JTR_fixed_06 | 1206 / 1258 | 1.6% | 36.7% | 33.2% | 14.4% | 14.1% | 28.5% | 0.0% |
| NQ / JTR_fixed_07 | 1204 / 1258 | 0.2% | 29.4% | 22.8% | 25.2% | 22.3% | 47.6% | 0.0% |
| NQ / JTR_fixed_08 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / JTR_fixed_EST_sensitivity_01 | 1143 / 1258 | 1.6% | 34.2% | 31.1% | 16.7% | 16.4% | 33.1% | 0.0% |
| NQ / JTR_fixed_EST_sensitivity_02 | 1173 / 1258 | 0.1% | 20.1% | 17.1% | 30.3% | 32.2% | 62.7% | 0.1% |
| NQ / JTR_fixed_EST_sensitivity_03 | 1195 / 1258 | 1.7% | 36.0% | 30.8% | 15.0% | 16.6% | 31.5% | 0.0% |
| NQ / JTR_fixed_EST_sensitivity_04 | 1201 / 1258 | 4.9% | 36.7% | 33.5% | 12.9% | 12.0% | 24.9% | 0.0% |
| NQ / JTR_fixed_EST_sensitivity_05 | 1206 / 1258 | 1.2% | 35.7% | 31.5% | 15.1% | 16.6% | 31.7% | 0.0% |
| NQ / JTR_fixed_EST_sensitivity_06 | 1206 / 1258 | 0.9% | 32.8% | 27.9% | 20.6% | 17.7% | 38.4% | 0.0% |
| NQ / JTR_fixed_EST_sensitivity_07 | 964 / 1258 | 0.4% | 30.9% | 21.9% | 25.0% | 21.7% | 46.8% | 0.1% |
| NQ / JTR_fixed_EST_sensitivity_08 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / London02 | 1186 / 1258 | 2.9% | 36.0% | 31.2% | 16.6% | 12.4% | 29.9% | 0.9% |
| NQ / NY08 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / ONS03 | 1189 / 1258 | 3.7% | 39.1% | 30.2% | 15.1% | 11.4% | 27.0% | 0.4% |
| NQ / ONS20 | 1096 / 1258 | 22.2% | 39.9% | 33.1% | 2.8% | 2.0% | 4.8% | 0.0% |
| NQ / OR15 | 1212 / 1258 | 0.2% | 32.3% | 28.0% | 20.4% | 19.1% | 39.5% | 0.1% |
| NQ / OR15__shift_+10m | 1212 / 1258 | 0.3% | 31.5% | 23.9% | 23.4% | 20.6% | 44.2% | 0.2% |
| NQ / OR15__shift_-10m | 1210 / 1258 | 0.1% | 23.1% | 19.6% | 28.1% | 29.1% | 57.2% | 0.0% |
| NQ / OR5 | 1212 / 1258 | 0.1% | 21.6% | 18.5% | 29.1% | 30.7% | 59.8% | 0.0% |
| NQ / OR5__shift_+10m | 1212 / 1258 | 0.0% | 19.6% | 15.9% | 32.9% | 31.4% | 64.4% | 0.1% |
| NQ / OR5__shift_-10m | 1210 / 1258 | 0.0% | 4.9% | 5.5% | 38.0% | 49.4% | 89.6% | 2.1% |
| NQ / OR_activity_1_1 | 1138 / 1258 | 0.4% | 32.2% | 28.7% | 19.0% | 19.6% | 38.7% | 0.1% |
| NQ / OR_activity_1_2 | 1169 / 1258 | 0.2% | 24.6% | 20.8% | 27.8% | 26.7% | 54.5% | 0.0% |
| NQ / OR_activity_3_2 | 1108 / 1258 | 1.4% | 37.9% | 32.7% | 14.7% | 13.4% | 28.1% | 0.0% |
| NQ / PIN015_Asia_UTC | 1090 / 1258 | 18.5% | 40.3% | 32.5% | 4.7% | 4.0% | 8.7% | 0.0% |
| NQ / PIN015_London_UTC | 1188 / 1258 | 3.5% | 37.0% | 32.3% | 15.2% | 11.7% | 27.2% | 0.3% |
| NQ / PIN015_NY_UTC | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / PIN073_1 | 1197 / 1258 | 0.1% | 27.5% | 21.1% | 26.2% | 25.1% | 51.3% | 0.0% |
| NQ / PIN073_2 | 1210 / 1258 | 0.0% | 16.7% | 13.6% | 33.7% | 34.0% | 69.8% | 2.1% |
| NQ / PIN073_3 | 1139 / 1258 | 0.1% | 19.8% | 16.1% | 32.6% | 31.3% | 64.0% | 0.1% |
| NQ / PIN073_4 | 1206 / 1258 | 0.7% | 32.8% | 24.5% | 22.9% | 19.1% | 42.0% | 0.0% |
| NQ / PIN073_5 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / PIN074_ref_00 | 1139 / 1258 | 0.0% | 5.3% | 5.4% | 42.6% | 45.3% | 89.3% | 1.4% |
| NQ / PIN074_ref_01 | 1182 / 1258 | 0.0% | 5.9% | 5.4% | 44.7% | 42.1% | 88.7% | 1.9% |
| NQ / PIN074_ref_03 | 1200 / 1258 | 0.0% | 10.2% | 9.9% | 37.2% | 40.9% | 79.8% | 1.7% |
| NQ / PIN074_ref_04 | 1196 / 1258 | 0.0% | 12.9% | 9.7% | 40.2% | 34.8% | 77.4% | 2.4% |
| NQ / PIN074_ref_07 | 1200 / 1258 | 0.0% | 5.8% | 5.3% | 44.8% | 42.6% | 88.8% | 1.4% |
| NQ / PIN075_01 | 1114 / 1258 | 5.3% | 34.6% | 32.7% | 14.0% | 13.5% | 27.5% | 0.0% |
| NQ / PIN075_02 | 1072 / 1258 | 32.3% | 36.1% | 29.5% | 1.3% | 0.8% | 2.1% | 0.0% |
| NQ / PIN075_03 | 1114 / 1258 | 5.7% | 41.4% | 35.2% | 9.6% | 8.2% | 17.8% | 0.0% |
| NQ / PIN075_04 | 1197 / 1258 | 4.3% | 37.8% | 33.2% | 13.6% | 11.2% | 24.8% | 0.0% |
| NQ / PIN075_05 | 1191 / 1258 | 8.2% | 41.6% | 32.6% | 8.9% | 8.6% | 17.5% | 0.0% |
| NQ / PIN075_06 | 1192 / 1258 | 0.4% | 25.5% | 22.6% | 29.2% | 22.2% | 51.5% | 0.1% |
| NQ / PIN075_07 | 1198 / 1258 | 1.5% | 30.3% | 26.9% | 21.5% | 19.8% | 41.3% | 0.0% |
| NQ / PIN075_08 | 1206 / 1258 | 1.0% | 34.7% | 30.8% | 17.8% | 15.8% | 33.6% | 0.0% |
| NQ / PIN075_09 | 1206 / 1258 | 4.4% | 39.0% | 34.2% | 12.3% | 10.1% | 22.4% | 0.0% |
| NQ / PIN075_10 | 1205 / 1258 | 0.7% | 36.2% | 26.2% | 19.4% | 17.4% | 36.8% | 0.0% |
| NQ / PIN075_11 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / PIN075_12 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / PIN076_00_08 | 1139 / 1258 | 0.0% | 5.3% | 5.4% | 42.6% | 45.3% | 89.3% | 1.4% |
| NQ / PIN076_08_0930 | 1207 / 1258 | 0.0% | 3.4% | 3.5% | 45.4% | 45.7% | 93.1% | 2.0% |
| NQ / PIN078_daily_not_combined | 0 / 493 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / PM | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / RTH0930 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / RTH_actual | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / custom09 | 1200 / 1258 | 26.8% | 39.4% | 30.2% | 2.2% | 1.3% | 3.6% | 0.0% |
| NQ / day00 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / futures08 | 0 / 1258 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| NQ / lunch | 1204 / 1258 | 1.5% | 36.7% | 25.6% | 18.5% | 17.7% | 36.2% | 0.0% |
| NQ / magic_00 | 1139 / 1258 | 0.3% | 24.2% | 20.5% | 27.2% | 27.7% | 55.0% | 0.0% |
| NQ / magic_01 | 1181 / 1258 | 0.2% | 27.2% | 22.5% | 23.4% | 26.8% | 50.1% | 0.0% |
| NQ / magic_02 | 1195 / 1258 | 1.1% | 33.2% | 28.8% | 17.8% | 19.1% | 36.9% | 0.0% |
| NQ / magic_06 | 1193 / 1258 | 0.0% | 20.0% | 16.7% | 35.1% | 27.9% | 63.3% | 0.3% |
| NQ / magic_07 | 1201 / 1258 | 0.0% | 16.2% | 17.1% | 32.7% | 33.0% | 66.7% | 1.0% |
| NQ / magic_08 | 1207 / 1258 | 0.7% | 22.8% | 19.7% | 28.1% | 28.7% | 56.8% | 0.0% |
| NQ / magic_23 | 1115 / 1258 | 1.3% | 29.2% | 26.1% | 23.0% | 20.4% | 43.3% | 0.0% |
| NQ / prior_RTH_open_observed | 1187 / 1258 | 17.4% | 44.3% | 33.5% | 3.5% | 1.2% | 4.7% | 0.0% |
| NQ / prior_RTH_preopen | 1187 / 1258 | 17.4% | 44.2% | 33.4% | 3.6% | 1.4% | 5.1% | 0.0% |
| NQ / turn_earlier | 1212 / 1258 | 0.2% | 27.7% | 24.6% | 24.5% | 22.9% | 47.5% | 0.1% |
| NQ / turn_later | 1208 / 1258 | 0.1% | 23.9% | 20.0% | 29.7% | 26.1% | 56.0% | 0.2% |
| NQ / turn_source | 1212 / 1258 | 0.1% | 26.1% | 21.2% | 25.9% | 26.6% | 52.6% | 0.2% |

## Are event rates stable across years, and how much can censoring change them?

Each annual both-edge estimate below includes its original 95% interval from 1,000 nonwrapping five-date block resamples, seed 20260907. The separate identified population bounds include every available positive-width formation: a breach observed before censoring stays positive, while an unresolved outcome can be either zero or one. The bounds are not confidence intervals. Sparse dates/events remain flagged in the full report; these intervals are descriptive and do not correct a search across all clocks.

| Instrument / clock | Year | Complete / intended | Both-edge rate [95% interval] | Formed-population lower–upper |
|---|---:|---:|---|---|
| ES / AM | 2020 | 243 / 253 | 3.7% [1.6%, 6.3%] | 4.1%–4.9% |
| ES / AM | 2021 | 247 / 252 | 4.0% [2.0%, 6.5%] | 4.0%–4.4% |
| ES / AM | 2022 | 246 / 251 | 6.5% [3.6%, 9.8%] | 6.5%–6.9% |
| ES / AM | 2023 | 244 / 250 | 9.0% [5.7%, 12.0%] | 8.9%–9.8% |
| ES / AM | 2024 | 245 / 252 | 7.3% [4.0%, 10.4%] | 7.3%–8.5% |
| ES / Asia19 | 2020 | 219 / 253 | 5.0% [2.4%, 8.1%] | 5.0%–5.0% |
| ES / Asia19 | 2021 | 193 / 252 | 5.2% [2.1%, 8.7%] | 5.2%–5.7% |
| ES / Asia19 | 2022 | 231 / 251 | 11.7% [7.6%, 16.5%] | 11.7%–11.7% |
| ES / Asia19 | 2023 | 158 / 250 | 15.2% [9.9%, 21.0%] | 15.2%–15.2% |
| ES / Asia19 | 2024 | 161 / 252 | 11.2% [6.4%, 16.0%] | 11.2%–11.2% |
| ES / Asia20 | 2020 | 222 / 253 | 7.2% [4.0%, 10.6%] | 7.2%–7.2% |
| ES / Asia20 | 2021 | 199 / 252 | 7.0% [3.9%, 10.5%] | 7.0%–7.5% |
| ES / Asia20 | 2022 | 237 / 251 | 15.6% [11.4%, 20.6%] | 15.6%–15.6% |
| ES / Asia20 | 2023 | 173 / 250 | 19.1% [13.7%, 25.0%] | 19.1%–19.1% |
| ES / Asia20 | 2024 | 169 / 252 | 16.0% [10.1%, 21.4%] | 16.0%–16.0% |
| ES / JTR_fixed_01 | 2020 | 236 / 253 | 34.7% [29.3%, 40.8%] | 34.3%–37.9% |
| ES / JTR_fixed_01 | 2021 | 230 / 252 | 29.1% [23.6%, 35.0%] | 29.9%–33.2% |
| ES / JTR_fixed_01 | 2022 | 240 / 251 | 33.8% [28.3%, 39.6%] | 34.6%–35.4% |
| ES / JTR_fixed_01 | 2023 | 217 / 250 | 32.7% [26.7%, 38.6%] | 32.6%–39.7% |
| ES / JTR_fixed_01 | 2024 | 208 / 252 | 33.7% [27.1%, 41.3%] | 32.1%–42.5% |
| ES / JTR_fixed_02 | 2020 | 231 / 253 | 61.9% [55.7%, 69.5%] | 59.8%–63.5% |
| ES / JTR_fixed_02 | 2021 | 217 / 252 | 64.5% [58.0%, 70.5%] | 61.6%–66.4% |
| ES / JTR_fixed_02 | 2022 | 243 / 251 | 72.0% [66.0%, 78.0%] | 71.4%–72.2% |
| ES / JTR_fixed_02 | 2023 | 192 / 250 | 69.3% [61.9%, 76.5%] | 64.1%–71.8% |
| ES / JTR_fixed_02 | 2024 | 197 / 252 | 61.4% [54.8%, 67.9%] | 55.2%–65.6% |
| ES / JTR_fixed_03 | 2020 | 242 / 253 | 27.7% [21.6%, 32.9%] | 27.5%–29.1% |
| ES / JTR_fixed_03 | 2021 | 244 / 252 | 27.0% [21.9%, 32.2%] | 26.5%–28.5% |
| ES / JTR_fixed_03 | 2022 | 248 / 251 | 35.5% [28.5%, 40.8%] | 35.1%–36.3% |
| ES / JTR_fixed_03 | 2023 | 244 / 250 | 35.2% [29.9%, 42.0%] | 35.1%–36.3% |
| ES / JTR_fixed_03 | 2024 | 247 / 252 | 38.1% [32.1%, 44.2%] | 38.2%–38.6% |
| ES / JTR_fixed_04 | 2020 | 241 / 253 | 32.8% [27.3%, 38.2%] | 32.6%–33.1% |
| ES / JTR_fixed_04 | 2021 | 247 / 252 | 35.2% [28.8%, 41.9%] | 35.2%–35.2% |
| ES / JTR_fixed_04 | 2022 | 247 / 251 | 35.2% [29.6%, 40.7%] | 34.9%–35.7% |
| ES / JTR_fixed_04 | 2023 | 243 / 250 | 35.8% [29.9%, 41.1%] | 35.8%–35.8% |
| ES / JTR_fixed_04 | 2024 | 246 / 252 | 40.7% [34.8%, 47.8%] | 40.5%–40.9% |
| ES / JTR_fixed_04__shift_+10m | 2020 | 241 / 253 | 33.2% [27.7%, 38.7%] | 33.1%–33.5% |
| ES / JTR_fixed_04__shift_+10m | 2021 | 247 / 252 | 36.4% [30.6%, 42.6%] | 36.4%–36.4% |
| ES / JTR_fixed_04__shift_+10m | 2022 | 247 / 251 | 34.4% [29.0%, 39.6%] | 34.5%–34.9% |
| ES / JTR_fixed_04__shift_+10m | 2023 | 243 / 250 | 34.6% [28.9%, 40.6%] | 34.3%–35.1% |
| ES / JTR_fixed_04__shift_+10m | 2024 | 246 / 252 | 39.0% [33.5%, 45.9%] | 38.9%–39.3% |
| ES / JTR_fixed_04__shift_-10m | 2020 | 241 / 253 | 34.4% [28.7%, 40.0%] | 34.3%–34.7% |
| ES / JTR_fixed_04__shift_-10m | 2021 | 247 / 252 | 34.0% [27.1%, 39.7%] | 34.0%–34.0% |
| ES / JTR_fixed_04__shift_-10m | 2022 | 247 / 251 | 35.6% [29.8%, 41.4%] | 35.3%–36.1% |
| ES / JTR_fixed_04__shift_-10m | 2023 | 243 / 250 | 36.6% [30.3%, 42.5%] | 36.6%–36.6% |
| ES / JTR_fixed_04__shift_-10m | 2024 | 246 / 252 | 40.2% [34.0%, 47.3%] | 40.1%–40.5% |
| ES / JTR_fixed_05 | 2020 | 243 / 253 | 30.0% [24.8%, 36.6%] | 30.9%–30.9% |
| ES / JTR_fixed_05 | 2021 | 247 / 252 | 24.7% [19.4%, 31.0%] | 24.6%–25.0% |
| ES / JTR_fixed_05 | 2022 | 246 / 251 | 32.9% [27.9%, 39.2%] | 32.8%–33.2% |
| ES / JTR_fixed_05 | 2023 | 245 / 250 | 32.7% [25.9%, 38.1%] | 32.9%–32.9% |
| ES / JTR_fixed_05 | 2024 | 246 / 252 | 32.9% [26.7%, 37.9%] | 32.7%–33.5% |
| ES / JTR_fixed_06 | 2020 | 246 / 253 | 35.0% [30.1%, 41.9%] | 34.9%–35.7% |
| ES / JTR_fixed_06 | 2021 | 247 / 252 | 31.6% [26.1%, 38.0%] | 31.5%–31.9% |
| ES / JTR_fixed_06 | 2022 | 246 / 251 | 28.0% [22.1%, 33.9%] | 28.3%–28.3% |
| ES / JTR_fixed_06 | 2023 | 244 / 250 | 33.2% [26.8%, 39.3%] | 33.3%–33.7% |
| ES / JTR_fixed_06 | 2024 | 245 / 252 | 29.0% [23.6%, 34.4%] | 28.6%–29.8% |
| ES / JTR_fixed_07 | 2020 | 246 / 253 | 46.7% [40.8%, 53.5%] | 46.2%–47.4% |
| ES / JTR_fixed_07 | 2021 | 247 / 252 | 43.7% [38.2%, 50.0%] | 44.0%–44.0% |
| ES / JTR_fixed_07 | 2022 | 246 / 251 | 52.4% [46.5%, 57.6%] | 52.2%–52.6% |
| ES / JTR_fixed_07 | 2023 | 244 / 250 | 52.0% [45.4%, 58.0%] | 51.6%–52.4% |
| ES / JTR_fixed_07 | 2024 | 245 / 252 | 48.2% [42.2%, 53.8%] | 48.0%–48.8% |
| ES / JTR_fixed_08 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 21.1%–100.0% |
| ES / JTR_fixed_08 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 29.6%–100.0% |
| ES / JTR_fixed_08 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 20.3%–100.0% |
| ES / JTR_fixed_08 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 20.9%–100.0% |
| ES / JTR_fixed_08 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 26.9%–100.0% |
| ES / JTR_fixed_EST_sensitivity_01 | 2020 | 235 / 253 | 27.2% [21.2%, 33.8%] | 27.3%–31.3% |
| ES / JTR_fixed_EST_sensitivity_01 | 2021 | 221 / 252 | 32.1% [26.1%, 39.9%] | 31.9%–39.5% |
| ES / JTR_fixed_EST_sensitivity_01 | 2022 | 241 / 251 | 34.4% [29.4%, 40.3%] | 34.4%–36.0% |
| ES / JTR_fixed_EST_sensitivity_01 | 2023 | 197 / 250 | 32.0% [26.0%, 39.3%] | 31.1%–45.1% |
| ES / JTR_fixed_EST_sensitivity_01 | 2024 | 196 / 252 | 35.7% [28.0%, 42.9%] | 33.2%–48.4% |
| ES / JTR_fixed_EST_sensitivity_02 | 2020 | 236 / 253 | 63.1% [58.0%, 69.8%] | 62.0%–64.0% |
| ES / JTR_fixed_EST_sensitivity_02 | 2021 | 235 / 252 | 58.3% [51.9%, 64.0%] | 57.5%–59.2% |
| ES / JTR_fixed_EST_sensitivity_02 | 2022 | 244 / 251 | 70.1% [64.0%, 76.1%] | 69.8%–70.2% |
| ES / JTR_fixed_EST_sensitivity_02 | 2023 | 226 / 250 | 66.8% [59.6%, 73.9%] | 65.8%–67.5% |
| ES / JTR_fixed_EST_sensitivity_02 | 2024 | 217 / 252 | 65.9% [59.7%, 72.2%] | 61.6%–68.1% |
| ES / JTR_fixed_EST_sensitivity_03 | 2020 | 242 / 253 | 29.3% [21.9%, 35.5%] | 29.6%–30.8% |
| ES / JTR_fixed_EST_sensitivity_03 | 2021 | 244 / 252 | 35.2% [29.1%, 42.1%] | 34.4%–36.8% |
| ES / JTR_fixed_EST_sensitivity_03 | 2022 | 248 / 251 | 35.5% [28.7%, 40.6%] | 35.3%–35.7% |
| ES / JTR_fixed_EST_sensitivity_03 | 2023 | 242 / 250 | 36.0% [30.2%, 42.9%] | 35.3%–37.8% |
| ES / JTR_fixed_EST_sensitivity_03 | 2024 | 245 / 252 | 33.1% [27.6%, 38.8%] | 32.9%–34.1% |
| ES / JTR_fixed_EST_sensitivity_04 | 2020 | 241 / 253 | 19.5% [14.2%, 25.3%] | 19.5%–19.5% |
| ES / JTR_fixed_EST_sensitivity_04 | 2021 | 247 / 252 | 21.9% [15.7%, 28.2%] | 21.9%–21.9% |
| ES / JTR_fixed_EST_sensitivity_04 | 2022 | 247 / 251 | 23.9% [19.2%, 28.2%] | 23.8%–24.2% |
| ES / JTR_fixed_EST_sensitivity_04 | 2023 | 245 / 250 | 20.8% [15.1%, 25.7%] | 20.8%–20.8% |
| ES / JTR_fixed_EST_sensitivity_04 | 2024 | 248 / 252 | 24.2% [19.1%, 29.7%] | 24.1%–24.5% |
| ES / JTR_fixed_EST_sensitivity_05 | 2020 | 246 / 253 | 35.0% [29.1%, 41.7%] | 35.3%–35.7% |
| ES / JTR_fixed_EST_sensitivity_05 | 2021 | 247 / 252 | 27.5% [22.1%, 34.0%] | 27.4%–27.8% |
| ES / JTR_fixed_EST_sensitivity_05 | 2022 | 246 / 251 | 34.1% [28.0%, 40.0%] | 34.0%–34.4% |
| ES / JTR_fixed_EST_sensitivity_05 | 2023 | 244 / 250 | 41.0% [34.3%, 47.1%] | 41.1%–41.5% |
| ES / JTR_fixed_EST_sensitivity_05 | 2024 | 245 / 252 | 41.2% [34.3%, 46.8%] | 40.7%–41.9% |
| ES / JTR_fixed_EST_sensitivity_06 | 2020 | 246 / 253 | 33.3% [27.4%, 40.2%] | 33.7%–34.1% |
| ES / JTR_fixed_EST_sensitivity_06 | 2021 | 247 / 252 | 35.6% [30.0%, 42.5%] | 35.5%–35.9% |
| ES / JTR_fixed_EST_sensitivity_06 | 2022 | 246 / 251 | 40.7% [35.0%, 47.2%] | 40.9%–40.9% |
| ES / JTR_fixed_EST_sensitivity_06 | 2023 | 244 / 250 | 42.6% [36.4%, 49.8%] | 42.3%–43.1% |
| ES / JTR_fixed_EST_sensitivity_06 | 2024 | 245 / 252 | 38.0% [32.0%, 44.1%] | 37.5%–38.7% |
| ES / JTR_fixed_EST_sensitivity_07 | 2020 | 84 / 253 | 47.6% [38.9%, 59.4%] | 56.9%–82.3% |
| ES / JTR_fixed_EST_sensitivity_07 | 2021 | 175 / 252 | 42.3% [36.3%, 49.0%] | 44.8%–59.3% |
| ES / JTR_fixed_EST_sensitivity_07 | 2022 | 246 / 251 | 47.2% [40.9%, 53.3%] | 47.0%–47.4% |
| ES / JTR_fixed_EST_sensitivity_07 | 2023 | 243 / 250 | 54.3% [46.7%, 60.3%] | 54.3%–54.7% |
| ES / JTR_fixed_EST_sensitivity_07 | 2024 | 244 / 252 | 47.1% [41.5%, 52.7%] | 47.4%–47.8% |
| ES / JTR_fixed_EST_sensitivity_08 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 19.0%–100.0% |
| ES / JTR_fixed_EST_sensitivity_08 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 16.6%–100.0% |
| ES / JTR_fixed_EST_sensitivity_08 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 6.5%–100.0% |
| ES / JTR_fixed_EST_sensitivity_08 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 6.6%–100.0% |
| ES / JTR_fixed_EST_sensitivity_08 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 8.6%–100.0% |
| ES / London02 | 2020 | 237 / 253 | 13.5% [8.9%, 17.4%] | 13.4%–14.2% |
| ES / London02 | 2021 | 240 / 252 | 15.0% [10.6%, 19.2%] | 15.0%–15.0% |
| ES / London02 | 2022 | 247 / 251 | 22.3% [16.9%, 27.7%] | 22.3%–22.3% |
| ES / London02 | 2023 | 239 / 250 | 28.5% [23.1%, 34.0%] | 28.5%–28.5% |
| ES / London02 | 2024 | 241 / 252 | 31.1% [25.3%, 37.2%] | 31.1%–31.1% |
| ES / NY08 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / NY08 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / NY08 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / NY08 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / NY08 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / ONS03 | 2020 | 239 / 253 | 12.6% [8.5%, 17.1%] | 12.4%–13.6% |
| ES / ONS03 | 2021 | 243 / 252 | 15.6% [11.1%, 19.8%] | 15.6%–15.6% |
| ES / ONS03 | 2022 | 247 / 251 | 19.0% [14.6%, 23.7%] | 19.0%–19.4% |
| ES / ONS03 | 2023 | 242 / 250 | 24.0% [18.3%, 29.7%] | 24.0%–24.0% |
| ES / ONS03 | 2024 | 245 / 252 | 27.8% [21.9%, 33.7%] | 27.8%–27.8% |
| ES / ONS20 | 2020 | 222 / 253 | 2.3% [0.5%, 4.2%] | 2.2%–6.1% |
| ES / ONS20 | 2021 | 200 / 252 | 1.5% [0.0%, 3.4%] | 1.3%–12.1% |
| ES / ONS20 | 2022 | 237 / 251 | 4.6% [2.1%, 7.5%] | 4.6%–5.0% |
| ES / ONS20 | 2023 | 173 / 250 | 6.9% [3.4%, 11.6%] | 5.8%–21.8% |
| ES / ONS20 | 2024 | 169 / 252 | 8.3% [4.5%, 12.8%] | 6.9%–23.6% |
| ES / OR15 | 2020 | 246 / 253 | 45.9% [39.6%, 52.2%] | 45.9%–45.9% |
| ES / OR15 | 2021 | 248 / 252 | 35.5% [29.3%, 42.6%] | 35.5%–35.5% |
| ES / OR15 | 2022 | 247 / 251 | 43.3% [37.5%, 50.0%] | 43.3%–43.3% |
| ES / OR15 | 2023 | 246 / 250 | 50.8% [43.7%, 56.7%] | 50.8%–50.8% |
| ES / OR15 | 2024 | 248 / 252 | 51.6% [44.9%, 57.5%] | 51.6%–51.6% |
| ES / OR15__shift_+10m | 2020 | 246 / 253 | 49.2% [43.2%, 56.0%] | 49.2%–49.2% |
| ES / OR15__shift_+10m | 2021 | 248 / 252 | 42.3% [35.5%, 49.2%] | 42.3%–42.3% |
| ES / OR15__shift_+10m | 2022 | 247 / 251 | 49.8% [44.5%, 56.2%] | 49.8%–49.8% |
| ES / OR15__shift_+10m | 2023 | 246 / 250 | 52.0% [45.9%, 57.3%] | 52.0%–52.0% |
| ES / OR15__shift_+10m | 2024 | 248 / 252 | 48.8% [41.5%, 54.9%] | 48.8%–48.8% |
| ES / OR15__shift_-10m | 2020 | 243 / 253 | 60.5% [54.4%, 66.4%] | 60.5%–60.5% |
| ES / OR15__shift_-10m | 2021 | 248 / 252 | 50.0% [44.4%, 55.8%] | 50.0%–50.0% |
| ES / OR15__shift_-10m | 2022 | 247 / 251 | 57.5% [51.8%, 63.2%] | 57.5%–57.5% |
| ES / OR15__shift_-10m | 2023 | 246 / 250 | 63.0% [55.3%, 68.8%] | 63.0%–63.0% |
| ES / OR15__shift_-10m | 2024 | 248 / 252 | 61.7% [55.4%, 67.8%] | 61.7%–61.7% |
| ES / OR5 | 2020 | 246 / 253 | 64.6% [58.7%, 70.3%] | 64.1%–64.9% |
| ES / OR5 | 2021 | 248 / 252 | 53.6% [47.8%, 59.6%] | 53.6%–53.6% |
| ES / OR5 | 2022 | 247 / 251 | 60.7% [55.1%, 66.3%] | 60.7%–60.7% |
| ES / OR5 | 2023 | 246 / 250 | 67.1% [59.5%, 72.8%] | 67.1%–67.1% |
| ES / OR5 | 2024 | 248 / 252 | 66.1% [59.9%, 72.0%] | 66.1%–66.1% |
| ES / OR5__shift_+10m | 2020 | 246 / 253 | 69.9% [64.5%, 75.7%] | 69.9%–69.9% |
| ES / OR5__shift_+10m | 2021 | 248 / 252 | 63.7% [57.7%, 70.3%] | 63.7%–63.7% |
| ES / OR5__shift_+10m | 2022 | 247 / 251 | 68.4% [63.3%, 74.7%] | 68.4%–68.4% |
| ES / OR5__shift_+10m | 2023 | 246 / 250 | 69.9% [64.2%, 74.9%] | 69.9%–69.9% |
| ES / OR5__shift_+10m | 2024 | 248 / 252 | 70.6% [64.4%, 76.1%] | 70.6%–70.6% |
| ES / OR5__shift_-10m | 2020 | 243 / 253 | 85.6% [81.5%, 89.8%] | 84.6%–85.8% |
| ES / OR5__shift_-10m | 2021 | 248 / 252 | 81.9% [77.2%, 87.2%] | 81.3%–82.1% |
| ES / OR5__shift_-10m | 2022 | 247 / 251 | 87.4% [83.5%, 91.1%] | 87.3%–87.6% |
| ES / OR5__shift_-10m | 2023 | 246 / 250 | 87.8% [83.5%, 91.5%] | 86.4%–88.0% |
| ES / OR5__shift_-10m | 2024 | 248 / 252 | 87.5% [83.7%, 91.5%] | 86.5%–87.7% |
| ES / OR_activity_1_1 | 2020 | 211 / 253 | 42.7% [35.9%, 50.2%] | 43.2%–43.2% |
| ES / OR_activity_1_1 | 2021 | 233 / 252 | 36.9% [31.1%, 43.7%] | 36.9%–36.9% |
| ES / OR_activity_1_1 | 2022 | 233 / 251 | 45.1% [39.4%, 52.1%] | 44.9%–45.3% |
| ES / OR_activity_1_1 | 2023 | 233 / 250 | 51.1% [44.1%, 58.0%] | 50.9%–51.3% |
| ES / OR_activity_1_1 | 2024 | 237 / 252 | 49.8% [42.6%, 56.8%] | 49.8%–49.8% |
| ES / OR_activity_1_2 | 2020 | 217 / 253 | 62.2% [56.3%, 68.3%] | 61.6%–62.6% |
| ES / OR_activity_1_2 | 2021 | 241 / 252 | 48.1% [41.7%, 55.2%] | 48.1%–48.1% |
| ES / OR_activity_1_2 | 2022 | 241 / 251 | 55.2% [49.8%, 61.3%] | 55.2%–55.2% |
| ES / OR_activity_1_2 | 2023 | 240 / 250 | 63.3% [55.6%, 69.0%] | 63.3%–63.3% |
| ES / OR_activity_1_2 | 2024 | 242 / 252 | 62.4% [56.2%, 68.4%] | 62.4%–62.4% |
| ES / OR_activity_3_2 | 2020 | 210 / 253 | 33.8% [27.3%, 41.3%] | 33.6%–34.1% |
| ES / OR_activity_3_2 | 2021 | 233 / 252 | 27.5% [22.2%, 34.0%] | 27.5%–27.5% |
| ES / OR_activity_3_2 | 2022 | 231 / 251 | 35.1% [29.5%, 41.0%] | 35.1%–35.1% |
| ES / OR_activity_3_2 | 2023 | 228 / 250 | 36.8% [29.9%, 43.0%] | 36.8%–36.8% |
| ES / OR_activity_3_2 | 2024 | 232 / 252 | 37.5% [30.7%, 43.4%] | 37.2%–38.0% |
| ES / PIN015_Asia_UTC | 2020 | 220 / 253 | 3.6% [1.4%, 6.4%] | 3.6%–4.1% |
| ES / PIN015_Asia_UTC | 2021 | 198 / 252 | 4.5% [2.0%, 7.4%] | 4.5%–5.0% |
| ES / PIN015_Asia_UTC | 2022 | 236 / 251 | 13.1% [9.0%, 18.1%] | 13.1%–13.1% |
| ES / PIN015_Asia_UTC | 2023 | 173 / 250 | 12.1% [7.5%, 17.4%] | 12.1%–12.1% |
| ES / PIN015_Asia_UTC | 2024 | 166 / 252 | 11.4% [6.9%, 16.1%] | 11.4%–11.4% |
| ES / PIN015_London_UTC | 2020 | 237 / 253 | 16.0% [11.2%, 20.5%] | 16.0%–16.4% |
| ES / PIN015_London_UTC | 2021 | 243 / 252 | 16.0% [11.8%, 20.1%] | 16.0%–16.0% |
| ES / PIN015_London_UTC | 2022 | 247 / 251 | 25.1% [19.3%, 30.6%] | 25.1%–25.1% |
| ES / PIN015_London_UTC | 2023 | 241 / 250 | 22.8% [17.7%, 28.2%] | 22.8%–22.8% |
| ES / PIN015_London_UTC | 2024 | 244 / 252 | 26.2% [21.5%, 31.5%] | 26.2%–26.2% |
| ES / PIN015_NY_UTC | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | unavailable–unavailable |
| ES / PIN015_NY_UTC | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PIN015_NY_UTC | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PIN015_NY_UTC | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PIN015_NY_UTC | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PIN073_1 | 2020 | 243 / 253 | 48.1% [41.9%, 54.9%] | 47.8%–48.6% |
| ES / PIN073_1 | 2021 | 241 / 252 | 45.6% [39.3%, 52.1%] | 45.2%–47.2% |
| ES / PIN073_1 | 2022 | 247 / 251 | 55.9% [49.8%, 62.3%] | 55.6%–56.0% |
| ES / PIN073_1 | 2023 | 242 / 250 | 55.8% [50.4%, 61.7%] | 55.3%–56.5% |
| ES / PIN073_1 | 2024 | 244 / 252 | 53.3% [46.2%, 58.8%] | 53.1%–53.5% |
| ES / PIN073_2 | 2020 | 243 / 253 | 67.9% [62.2%, 74.3%] | 66.8%–68.4% |
| ES / PIN073_2 | 2021 | 248 / 252 | 63.3% [57.7%, 69.3%] | 62.5%–63.7% |
| ES / PIN073_2 | 2022 | 247 / 251 | 67.2% [61.5%, 71.4%] | 66.1%–67.7% |
| ES / PIN073_2 | 2023 | 246 / 250 | 65.0% [58.3%, 70.6%] | 64.0%–65.6% |
| ES / PIN073_2 | 2024 | 248 / 252 | 70.6% [64.4%, 76.9%] | 69.4%–71.0% |
| ES / PIN073_3 | 2020 | 231 / 253 | 61.9% [55.7%, 69.5%] | 59.8%–63.5% |
| ES / PIN073_3 | 2021 | 217 / 252 | 64.5% [58.0%, 70.5%] | 61.6%–66.4% |
| ES / PIN073_3 | 2022 | 243 / 251 | 72.0% [66.0%, 78.0%] | 71.4%–72.2% |
| ES / PIN073_3 | 2023 | 192 / 250 | 69.3% [61.9%, 76.5%] | 64.1%–71.8% |
| ES / PIN073_3 | 2024 | 197 / 252 | 61.4% [54.8%, 67.9%] | 55.2%–65.6% |
| ES / PIN073_4 | 2020 | 246 / 253 | 35.0% [28.1%, 41.2%] | 35.3%–35.7% |
| ES / PIN073_4 | 2021 | 247 / 252 | 35.6% [29.7%, 42.1%] | 35.9%–35.9% |
| ES / PIN073_4 | 2022 | 246 / 251 | 48.0% [41.6%, 53.6%] | 47.8%–48.2% |
| ES / PIN073_4 | 2023 | 244 / 250 | 47.5% [41.0%, 53.9%] | 47.6%–48.0% |
| ES / PIN073_4 | 2024 | 245 / 252 | 44.9% [39.2%, 51.2%] | 44.4%–45.6% |
| ES / PIN073_5 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 42.5%–100.0% |
| ES / PIN073_5 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 49.4%–100.0% |
| ES / PIN073_5 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 42.3%–100.0% |
| ES / PIN073_5 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 38.9%–100.0% |
| ES / PIN073_5 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 44.5%–100.0% |
| ES / PIN074_ref_00 | 2020 | 230 / 253 | 85.7% [81.7%, 90.3%] | 82.9%–86.6% |
| ES / PIN074_ref_00 | 2021 | 215 / 252 | 87.4% [82.1%, 91.7%] | 81.1%–88.9% |
| ES / PIN074_ref_00 | 2022 | 243 / 251 | 86.8% [83.4%, 90.7%] | 86.0%–87.2% |
| ES / PIN074_ref_00 | 2023 | 184 / 250 | 89.7% [85.1%, 94.2%] | 79.7%–91.9% |
| ES / PIN074_ref_00 | 2024 | 192 / 252 | 85.9% [81.7%, 90.1%] | 76.9%–88.8% |
| ES / PIN074_ref_01 | 2020 | 239 / 253 | 88.3% [83.9%, 92.5%] | 86.5%–88.8% |
| ES / PIN074_ref_01 | 2021 | 238 / 252 | 87.8% [83.5%, 91.5%] | 85.5%–88.4% |
| ES / PIN074_ref_01 | 2022 | 245 / 251 | 91.8% [88.1%, 95.5%] | 91.2%–92.0% |
| ES / PIN074_ref_01 | 2023 | 227 / 250 | 90.3% [85.9%, 94.2%] | 87.6%–90.9% |
| ES / PIN074_ref_01 | 2024 | 219 / 252 | 87.2% [82.0%, 91.7%] | 84.9%–88.3% |
| ES / PIN074_ref_03 | 2020 | 244 / 253 | 75.4% [69.9%, 80.7%] | 75.5%–75.9% |
| ES / PIN074_ref_03 | 2021 | 244 / 252 | 80.3% [75.9%, 84.7%] | 79.8%–81.0% |
| ES / PIN074_ref_03 | 2022 | 248 / 251 | 79.8% [74.9%, 84.0%] | 80.1%–80.1% |
| ES / PIN074_ref_03 | 2023 | 245 / 250 | 82.4% [78.5%, 86.4%] | 81.6%–82.8% |
| ES / PIN074_ref_03 | 2024 | 247 / 252 | 79.4% [73.9%, 84.8%] | 78.9%–79.7% |
| ES / PIN074_ref_04 | 2020 | 242 / 253 | 78.1% [72.7%, 83.6%] | 77.0%–78.6% |
| ES / PIN074_ref_04 | 2021 | 243 / 252 | 82.3% [77.0%, 87.1%] | 80.6%–82.9% |
| ES / PIN074_ref_04 | 2022 | 248 / 251 | 75.8% [70.0%, 81.4%] | 75.3%–76.1% |
| ES / PIN074_ref_04 | 2023 | 242 / 250 | 79.3% [74.4%, 84.0%] | 79.2%–80.0% |
| ES / PIN074_ref_04 | 2024 | 245 / 252 | 78.0% [73.6%, 82.9%] | 77.0%–78.6% |
| ES / PIN074_ref_07 | 2020 | 242 / 253 | 87.6% [84.0%, 90.8%] | 86.3%–87.9% |
| ES / PIN074_ref_07 | 2021 | 248 / 252 | 85.5% [80.2%, 90.7%] | 84.9%–85.7% |
| ES / PIN074_ref_07 | 2022 | 247 / 251 | 89.1% [85.4%, 93.1%] | 88.4%–89.2% |
| ES / PIN074_ref_07 | 2023 | 246 / 250 | 92.7% [89.3%, 95.9%] | 92.0%–92.8% |
| ES / PIN074_ref_07 | 2024 | 248 / 252 | 88.7% [85.4%, 92.8%] | 87.7%–88.9% |
| ES / PIN075_01 | 2020 | 235 / 253 | 28.9% [23.0%, 35.3%] | 28.9%–30.1% |
| ES / PIN075_01 | 2021 | 221 / 252 | 36.7% [30.7%, 43.1%] | 34.9%–39.7% |
| ES / PIN075_01 | 2022 | 235 / 251 | 34.9% [29.3%, 41.4%] | 34.6%–36.2% |
| ES / PIN075_01 | 2023 | 190 / 250 | 25.3% [19.2%, 32.4%] | 23.0%–32.1% |
| ES / PIN075_01 | 2024 | 203 / 252 | 14.3% [9.9%, 19.4%] | 13.1%–21.6% |
| ES / PIN075_02 | 2020 | 220 / 253 | 0.9% [0.0%, 2.3%] | 0.9%–7.2% |
| ES / PIN075_02 | 2021 | 195 / 252 | 1.5% [0.0%, 3.5%] | 1.4%–13.5% |
| ES / PIN075_02 | 2022 | 232 / 251 | 1.7% [0.4%, 3.8%] | 1.7%–4.6% |
| ES / PIN075_02 | 2023 | 158 / 250 | 1.9% [0.0%, 4.1%] | 1.5%–23.3% |
| ES / PIN075_02 | 2024 | 162 / 252 | 0.6% [0.0%, 2.1%] | 0.5%–19.9% |
| ES / PIN075_03 | 2020 | 225 / 253 | 12.0% [8.1%, 16.5%] | 11.9%–12.4% |
| ES / PIN075_03 | 2021 | 204 / 252 | 13.7% [9.1%, 18.3%] | 13.7%–14.1% |
| ES / PIN075_03 | 2022 | 239 / 251 | 23.8% [18.6%, 29.9%] | 23.8%–23.8% |
| ES / PIN075_03 | 2023 | 179 / 250 | 27.4% [20.9%, 33.5%] | 27.4%–27.4% |
| ES / PIN075_03 | 2024 | 182 / 252 | 21.4% [15.0%, 28.0%] | 21.4%–21.4% |
| ES / PIN075_04 | 2020 | 242 / 253 | 20.2% [14.9%, 25.1%] | 20.2%–21.9% |
| ES / PIN075_04 | 2021 | 243 / 252 | 18.9% [14.3%, 23.6%] | 19.0%–20.6% |
| ES / PIN075_04 | 2022 | 248 / 251 | 23.4% [17.7%, 27.1%] | 23.2%–24.0% |
| ES / PIN075_04 | 2023 | 243 / 250 | 26.7% [21.2%, 33.2%] | 26.3%–27.9% |
| ES / PIN075_04 | 2024 | 246 / 252 | 28.0% [23.0%, 33.9%] | 28.1%–28.9% |
| ES / PIN075_05 | 2020 | 241 / 253 | 13.3% [9.2%, 17.5%] | 13.0%–15.0% |
| ES / PIN075_05 | 2021 | 243 / 252 | 13.6% [9.1%, 18.8%] | 13.5%–13.9% |
| ES / PIN075_05 | 2022 | 248 / 251 | 12.5% [8.1%, 17.1%] | 12.5%–12.5% |
| ES / PIN075_05 | 2023 | 242 / 250 | 19.8% [14.8%, 25.0%] | 19.5%–21.1% |
| ES / PIN075_05 | 2024 | 245 / 252 | 14.7% [10.4%, 19.1%] | 14.5%–15.7% |
| ES / PIN075_06 | 2020 | 240 / 253 | 37.1% [31.0%, 43.0%] | 36.6%–37.9% |
| ES / PIN075_06 | 2021 | 247 / 252 | 44.1% [37.9%, 50.2%] | 44.0%–44.4% |
| ES / PIN075_06 | 2022 | 247 / 251 | 49.0% [43.1%, 55.4%] | 48.8%–49.2% |
| ES / PIN075_06 | 2023 | 242 / 250 | 52.1% [45.6%, 57.6%] | 51.9%–52.3% |
| ES / PIN075_06 | 2024 | 245 / 252 | 50.6% [44.9%, 56.7%] | 50.2%–51.0% |
| ES / PIN075_07 | 2020 | 242 / 253 | 31.8% [26.4%, 37.9%] | 31.7%–32.1% |
| ES / PIN075_07 | 2021 | 247 / 252 | 36.0% [30.1%, 42.7%] | 36.0%–36.0% |
| ES / PIN075_07 | 2022 | 247 / 251 | 36.4% [31.3%, 41.3%] | 36.1%–36.9% |
| ES / PIN075_07 | 2023 | 245 / 250 | 32.7% [26.9%, 38.1%] | 32.4%–33.2% |
| ES / PIN075_07 | 2024 | 246 / 252 | 36.6% [30.3%, 43.9%] | 36.4%–36.8% |
| ES / PIN075_08 | 2020 | 246 / 253 | 39.0% [34.1%, 45.8%] | 39.4%–39.8% |
| ES / PIN075_08 | 2021 | 247 / 252 | 36.8% [31.0%, 42.9%] | 36.7%–37.1% |
| ES / PIN075_08 | 2022 | 246 / 251 | 35.4% [29.4%, 40.7%] | 35.6%–35.6% |
| ES / PIN075_08 | 2023 | 244 / 250 | 37.7% [32.9%, 43.2%] | 37.8%–38.2% |
| ES / PIN075_08 | 2024 | 245 / 252 | 35.9% [30.2%, 41.1%] | 35.5%–36.7% |
| ES / PIN075_09 | 2020 | 246 / 253 | 24.0% [18.7%, 28.7%] | 24.1%–24.9% |
| ES / PIN075_09 | 2021 | 247 / 252 | 22.7% [17.3%, 27.6%] | 23.0%–23.0% |
| ES / PIN075_09 | 2022 | 246 / 251 | 27.2% [21.3%, 33.9%] | 27.1%–27.5% |
| ES / PIN075_09 | 2023 | 244 / 250 | 28.3% [22.3%, 34.0%] | 28.0%–28.9% |
| ES / PIN075_09 | 2024 | 245 / 252 | 24.1% [19.3%, 29.2%] | 23.8%–25.0% |
| ES / PIN075_10 | 2020 | 246 / 253 | 36.2% [30.5%, 41.9%] | 36.5%–36.9% |
| ES / PIN075_10 | 2021 | 247 / 252 | 36.0% [30.9%, 41.0%] | 36.3%–36.3% |
| ES / PIN075_10 | 2022 | 246 / 251 | 39.8% [34.1%, 45.5%] | 39.7%–40.1% |
| ES / PIN075_10 | 2023 | 244 / 250 | 38.9% [33.3%, 44.5%] | 39.0%–39.4% |
| ES / PIN075_10 | 2024 | 245 / 252 | 40.4% [35.2%, 45.3%] | 39.9%–41.1% |
| ES / PIN075_11 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 30.1%–100.0% |
| ES / PIN075_11 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 24.3%–100.0% |
| ES / PIN075_11 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 18.3%–100.0% |
| ES / PIN075_11 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 18.0%–100.0% |
| ES / PIN075_11 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 15.9%–100.0% |
| ES / PIN075_12 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PIN075_12 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.8%–100.0% |
| ES / PIN075_12 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PIN075_12 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.4%–100.0% |
| ES / PIN075_12 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PIN076_00_08 | 2020 | 230 / 253 | 85.7% [81.7%, 90.3%] | 82.9%–86.6% |
| ES / PIN076_00_08 | 2021 | 215 / 252 | 87.4% [82.1%, 91.7%] | 81.1%–88.9% |
| ES / PIN076_00_08 | 2022 | 243 / 251 | 86.8% [83.4%, 90.7%] | 86.0%–87.2% |
| ES / PIN076_00_08 | 2023 | 184 / 250 | 89.7% [85.1%, 94.2%] | 79.7%–91.9% |
| ES / PIN076_00_08 | 2024 | 192 / 252 | 85.9% [81.7%, 90.1%] | 76.9%–88.8% |
| ES / PIN076_08_0930 | 2020 | 243 / 253 | 90.9% [87.4%, 93.9%] | 90.4%–91.2% |
| ES / PIN076_08_0930 | 2021 | 248 / 252 | 89.5% [85.4%, 93.1%] | 88.9%–89.7% |
| ES / PIN076_08_0930 | 2022 | 247 / 251 | 89.1% [84.9%, 92.4%] | 88.8%–89.2% |
| ES / PIN076_08_0930 | 2023 | 246 / 250 | 89.4% [85.4%, 93.0%] | 89.6%–89.6% |
| ES / PIN076_08_0930 | 2024 | 248 / 252 | 93.1% [89.9%, 96.4%] | 92.5%–93.3% |
| ES / PIN078_daily_not_combined | 2020 | 0 / 100 | unavailable [unavailable, unavailable] | unavailable–unavailable |
| ES / PIN078_daily_not_combined | 2021 | 0 / 99 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PIN078_daily_not_combined | 2022 | 0 / 97 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PIN078_daily_not_combined | 2023 | 0 / 96 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PIN078_daily_not_combined | 2024 | 0 / 101 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PM | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PM | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.4%–100.0% |
| ES / PM | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PM | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / PM | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / RTH0930 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / RTH0930 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / RTH0930 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / RTH0930 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / RTH0930 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / RTH_actual | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / RTH_actual | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / RTH_actual | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / RTH_actual | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / RTH_actual | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / custom09 | 2020 | 241 / 253 | 3.7% [1.7%, 6.4%] | 4.1%–4.5% |
| ES / custom09 | 2021 | 247 / 252 | 3.2% [1.2%, 5.7%] | 3.2%–3.6% |
| ES / custom09 | 2022 | 246 / 251 | 5.7% [2.9%, 8.9%] | 5.7%–6.1% |
| ES / custom09 | 2023 | 244 / 250 | 8.6% [5.3%, 11.6%] | 8.5%–9.3% |
| ES / custom09 | 2024 | 245 / 252 | 6.9% [3.7%, 9.9%] | 6.9%–8.1% |
| ES / day00 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | unavailable–unavailable |
| ES / day00 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / day00 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / day00 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / day00 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / futures08 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | unavailable–unavailable |
| ES / futures08 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / futures08 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / futures08 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / futures08 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| ES / lunch | 2020 | 246 / 253 | 45.1% [40.2%, 50.6%] | 44.8%–45.6% |
| ES / lunch | 2021 | 247 / 252 | 41.3% [35.5%, 47.6%] | 41.1%–41.5% |
| ES / lunch | 2022 | 246 / 251 | 36.2% [29.8%, 42.6%] | 36.0%–36.4% |
| ES / lunch | 2023 | 244 / 250 | 37.3% [31.7%, 42.6%] | 37.0%–37.8% |
| ES / lunch | 2024 | 245 / 252 | 37.1% [31.7%, 42.9%] | 36.7%–37.9% |
| ES / magic_00 | 2020 | 231 / 253 | 52.4% [46.3%, 59.9%] | 51.5%–53.2% |
| ES / magic_00 | 2021 | 217 / 252 | 55.3% [49.3%, 61.7%] | 54.8%–55.7% |
| ES / magic_00 | 2022 | 243 / 251 | 63.4% [57.4%, 69.7%] | 63.4%–63.4% |
| ES / magic_00 | 2023 | 192 / 250 | 58.9% [50.8%, 66.5%] | 57.7%–59.7% |
| ES / magic_00 | 2024 | 196 / 252 | 55.6% [48.9%, 61.0%] | 53.7%–57.1% |
| ES / magic_01 | 2020 | 239 / 253 | 48.5% [41.4%, 55.9%] | 48.3%–48.8% |
| ES / magic_01 | 2021 | 239 / 252 | 47.7% [41.4%, 53.7%] | 47.5%–48.3% |
| ES / magic_01 | 2022 | 245 / 251 | 59.2% [53.4%, 66.1%] | 59.2%–59.2% |
| ES / magic_01 | 2023 | 233 / 250 | 54.9% [47.8%, 61.5%] | 54.7%–55.1% |
| ES / magic_01 | 2024 | 226 / 252 | 48.2% [41.7%, 55.0%] | 48.2%–48.2% |
| ES / magic_02 | 2020 | 241 / 253 | 32.0% [26.1%, 38.7%] | 31.7%–32.5% |
| ES / magic_02 | 2021 | 241 / 252 | 34.9% [29.5%, 40.7%] | 34.8%–35.7% |
| ES / magic_02 | 2022 | 247 / 251 | 41.7% [35.5%, 48.0%] | 41.5%–41.9% |
| ES / magic_02 | 2023 | 242 / 250 | 45.0% [39.4%, 51.0%] | 45.3%–45.3% |
| ES / magic_02 | 2024 | 243 / 252 | 38.3% [31.2%, 44.1%] | 38.1%–38.5% |
| ES / magic_06 | 2020 | 241 / 253 | 48.1% [42.4%, 54.1%] | 47.5%–48.8% |
| ES / magic_06 | 2021 | 247 / 252 | 56.3% [49.0%, 63.3%] | 56.3%–56.3% |
| ES / magic_06 | 2022 | 247 / 251 | 61.5% [55.5%, 68.4%] | 61.4%–61.8% |
| ES / magic_06 | 2023 | 243 / 250 | 64.2% [58.3%, 69.5%] | 64.2%–64.2% |
| ES / magic_06 | 2024 | 246 / 252 | 61.4% [55.5%, 69.1%] | 61.5%–61.5% |
| ES / magic_07 | 2020 | 242 / 253 | 55.0% [49.2%, 61.0%] | 54.1%–55.7% |
| ES / magic_07 | 2021 | 248 / 252 | 55.6% [49.0%, 62.3%] | 55.6%–55.6% |
| ES / magic_07 | 2022 | 247 / 251 | 62.3% [56.3%, 68.4%] | 62.2%–62.7% |
| ES / magic_07 | 2023 | 246 / 250 | 68.7% [62.6%, 74.0%] | 68.5%–69.0% |
| ES / magic_07 | 2024 | 248 / 252 | 69.8% [63.9%, 76.8%] | 69.5%–69.9% |
| ES / magic_08 | 2020 | 243 / 253 | 54.3% [48.5%, 59.7%] | 53.4%–55.1% |
| ES / magic_08 | 2021 | 248 / 252 | 53.6% [47.2%, 60.1%] | 53.0%–54.2% |
| ES / magic_08 | 2022 | 247 / 251 | 49.8% [43.7%, 54.7%] | 49.6%–50.4% |
| ES / magic_08 | 2023 | 246 / 250 | 48.8% [42.1%, 54.9%] | 48.0%–49.6% |
| ES / magic_08 | 2024 | 248 / 252 | 51.6% [45.6%, 57.7%] | 51.0%–52.2% |
| ES / magic_23 | 2020 | 226 / 253 | 40.7% [34.5%, 47.7%] | 39.2%–43.5% |
| ES / magic_23 | 2021 | 205 / 252 | 43.4% [36.8%, 49.5%] | 39.1%–49.6% |
| ES / magic_23 | 2022 | 239 / 251 | 42.7% [36.6%, 48.3%] | 42.3%–43.2% |
| ES / magic_23 | 2023 | 179 / 250 | 45.3% [39.0%, 51.5%] | 37.3%–54.8% |
| ES / magic_23 | 2024 | 181 / 252 | 33.1% [25.4%, 40.4%] | 28.3%–44.7% |
| ES / prior_RTH_open_observed | 2020 | 237 / 253 | 3.0% [1.2%, 5.1%] | 2.9%–5.7% |
| ES / prior_RTH_open_observed | 2021 | 244 / 252 | 4.9% [2.4%, 7.1%] | 4.8%–6.5% |
| ES / prior_RTH_open_observed | 2022 | 243 / 251 | 3.3% [0.8%, 5.0%] | 3.2%–4.9% |
| ES / prior_RTH_open_observed | 2023 | 242 / 250 | 4.5% [2.1%, 6.7%] | 4.5%–6.1% |
| ES / prior_RTH_open_observed | 2024 | 244 / 252 | 4.1% [2.0%, 6.9%] | 4.0%–5.6% |
| ES / prior_RTH_preopen | 2020 | 237 / 253 | 3.0% [1.2%, 5.1%] | 2.9%–5.7% |
| ES / prior_RTH_preopen | 2021 | 244 / 252 | 4.9% [2.4%, 7.1%] | 4.8%–6.5% |
| ES / prior_RTH_preopen | 2022 | 243 / 251 | 3.3% [0.8%, 5.0%] | 3.2%–4.9% |
| ES / prior_RTH_preopen | 2023 | 242 / 250 | 4.5% [2.1%, 6.7%] | 4.5%–6.1% |
| ES / prior_RTH_preopen | 2024 | 244 / 252 | 3.7% [1.6%, 6.3%] | 3.6%–5.2% |
| ES / turn_earlier | 2020 | 246 / 253 | 53.7% [47.8%, 60.3%] | 53.7%–53.7% |
| ES / turn_earlier | 2021 | 248 / 252 | 40.3% [34.5%, 47.2%] | 40.3%–40.3% |
| ES / turn_earlier | 2022 | 247 / 251 | 49.0% [43.7%, 55.1%] | 49.0%–49.0% |
| ES / turn_earlier | 2023 | 246 / 250 | 59.8% [52.7%, 65.5%] | 59.8%–59.8% |
| ES / turn_earlier | 2024 | 248 / 252 | 59.7% [53.2%, 65.7%] | 59.7%–59.7% |
| ES / turn_later | 2020 | 246 / 253 | 58.9% [53.2%, 65.3%] | 59.4%–59.4% |
| ES / turn_later | 2021 | 247 / 252 | 55.5% [49.6%, 61.8%] | 55.2%–55.6% |
| ES / turn_later | 2022 | 246 / 251 | 60.6% [54.9%, 67.3%] | 60.3%–60.7% |
| ES / turn_later | 2023 | 245 / 250 | 58.8% [52.4%, 64.5%] | 58.9%–58.9% |
| ES / turn_later | 2024 | 246 / 252 | 56.1% [49.8%, 61.3%] | 55.6%–56.5% |
| ES / turn_source | 2020 | 246 / 253 | 56.1% [49.6%, 63.1%] | 56.1%–56.1% |
| ES / turn_source | 2021 | 248 / 252 | 48.8% [42.3%, 56.0%] | 48.8%–48.8% |
| ES / turn_source | 2022 | 247 / 251 | 56.3% [50.2%, 62.9%] | 56.3%–56.3% |
| ES / turn_source | 2023 | 246 / 250 | 60.2% [53.9%, 66.0%] | 60.2%–60.2% |
| ES / turn_source | 2024 | 248 / 252 | 56.5% [49.2%, 62.9%] | 56.5%–56.5% |
| NQ / AM | 2020 | 241 / 253 | 2.9% [0.8%, 5.0%] | 2.8%–4.9% |
| NQ / AM | 2021 | 247 / 252 | 2.0% [0.4%, 4.0%] | 2.0%–2.4% |
| NQ / AM | 2022 | 246 / 251 | 4.1% [1.6%, 6.9%] | 4.0%–4.5% |
| NQ / AM | 2023 | 244 / 250 | 4.1% [2.1%, 6.5%] | 4.1%–4.9% |
| NQ / AM | 2024 | 223 / 252 | 5.4% [2.7%, 8.4%] | 5.3%–6.2% |
| NQ / Asia19 | 2020 | 225 / 253 | 5.8% [3.4%, 8.6%] | 5.8%–5.8% |
| NQ / Asia19 | 2021 | 211 / 252 | 8.1% [4.9%, 11.8%] | 8.1%–8.1% |
| NQ / Asia19 | 2022 | 230 / 251 | 9.1% [5.8%, 12.9%] | 9.1%–9.1% |
| NQ / Asia19 | 2023 | 211 / 250 | 16.1% [11.1%, 21.5%] | 16.1%–16.1% |
| NQ / Asia19 | 2024 | 189 / 252 | 12.2% [7.0%, 16.4%] | 12.1%–12.6% |
| NQ / Asia20 | 2020 | 230 / 253 | 7.8% [4.9%, 10.8%] | 7.8%–7.8% |
| NQ / Asia20 | 2021 | 218 / 252 | 9.6% [6.0%, 13.8%] | 9.6%–9.6% |
| NQ / Asia20 | 2022 | 234 / 251 | 12.4% [8.7%, 16.0%] | 12.4%–12.4% |
| NQ / Asia20 | 2023 | 222 / 250 | 18.0% [12.8%, 23.6%] | 18.0%–18.0% |
| NQ / Asia20 | 2024 | 192 / 252 | 14.1% [8.9%, 18.5%] | 14.0%–14.5% |
| NQ / JTR_fixed_01 | 2020 | 239 / 253 | 35.1% [29.4%, 40.7%] | 34.1%–37.0% |
| NQ / JTR_fixed_01 | 2021 | 230 / 252 | 32.2% [26.8%, 37.7%] | 32.1%–35.8% |
| NQ / JTR_fixed_01 | 2022 | 241 / 251 | 32.8% [27.2%, 38.9%] | 32.2%–33.9% |
| NQ / JTR_fixed_01 | 2023 | 232 / 250 | 34.5% [28.7%, 41.0%] | 33.6%–36.9% |
| NQ / JTR_fixed_01 | 2024 | 209 / 252 | 33.0% [27.0%, 39.8%] | 31.7%–35.8% |
| NQ / JTR_fixed_02 | 2020 | 237 / 253 | 63.7% [57.2%, 69.9%] | 62.7%–64.3% |
| NQ / JTR_fixed_02 | 2021 | 228 / 252 | 64.9% [58.4%, 70.8%] | 63.2%–65.8% |
| NQ / JTR_fixed_02 | 2022 | 243 / 251 | 67.5% [60.9%, 74.1%] | 66.9%–67.8% |
| NQ / JTR_fixed_02 | 2023 | 229 / 250 | 66.4% [60.3%, 73.3%] | 64.7%–67.2% |
| NQ / JTR_fixed_02 | 2024 | 202 / 252 | 56.4% [49.5%, 63.7%] | 54.7%–58.5% |
| NQ / JTR_fixed_03 | 2020 | 241 / 253 | 27.4% [21.8%, 32.4%] | 27.2%–28.9% |
| NQ / JTR_fixed_03 | 2021 | 245 / 252 | 31.4% [25.8%, 36.3%] | 30.9%–32.5% |
| NQ / JTR_fixed_03 | 2022 | 246 / 251 | 33.7% [27.9%, 38.3%] | 33.6%–34.8% |
| NQ / JTR_fixed_03 | 2023 | 243 / 250 | 37.0% [31.4%, 42.4%] | 37.2%–38.1% |
| NQ / JTR_fixed_03 | 2024 | 222 / 252 | 40.1% [33.2%, 47.6%] | 39.6%–40.9% |
| NQ / JTR_fixed_04 | 2020 | 239 / 253 | 42.3% [35.2%, 49.0%] | 42.3%–42.3% |
| NQ / JTR_fixed_04 | 2021 | 244 / 252 | 44.3% [38.3%, 49.8%] | 44.3%–44.3% |
| NQ / JTR_fixed_04 | 2022 | 244 / 251 | 39.3% [33.6%, 45.9%] | 39.3%–39.3% |
| NQ / JTR_fixed_04 | 2023 | 243 / 250 | 43.2% [36.9%, 49.6%] | 43.2%–43.2% |
| NQ / JTR_fixed_04 | 2024 | 223 / 252 | 46.2% [41.2%, 52.7%] | 46.2%–46.2% |
| NQ / JTR_fixed_04__shift_+10m | 2020 | 239 / 253 | 41.8% [35.1%, 48.5%] | 41.8%–41.8% |
| NQ / JTR_fixed_04__shift_+10m | 2021 | 245 / 252 | 45.3% [39.0%, 50.8%] | 45.3%–45.3% |
| NQ / JTR_fixed_04__shift_+10m | 2022 | 244 / 251 | 41.0% [35.5%, 46.9%] | 41.0%–41.0% |
| NQ / JTR_fixed_04__shift_+10m | 2023 | 243 / 250 | 43.6% [37.2%, 49.6%] | 43.6%–43.6% |
| NQ / JTR_fixed_04__shift_+10m | 2024 | 223 / 252 | 45.3% [40.1%, 52.2%] | 45.3%–45.3% |
| NQ / JTR_fixed_04__shift_-10m | 2020 | 239 / 253 | 42.7% [35.4%, 49.1%] | 42.7%–42.7% |
| NQ / JTR_fixed_04__shift_-10m | 2021 | 244 / 252 | 44.3% [37.5%, 49.8%] | 44.3%–44.3% |
| NQ / JTR_fixed_04__shift_-10m | 2022 | 244 / 251 | 39.3% [33.5%, 45.7%] | 39.3%–39.3% |
| NQ / JTR_fixed_04__shift_-10m | 2023 | 243 / 250 | 43.6% [37.3%, 49.2%] | 43.6%–43.6% |
| NQ / JTR_fixed_04__shift_-10m | 2024 | 223 / 252 | 45.3% [40.7%, 51.5%] | 45.3%–45.3% |
| NQ / JTR_fixed_05 | 2020 | 243 / 253 | 25.1% [20.5%, 30.5%] | 24.8%–26.0% |
| NQ / JTR_fixed_05 | 2021 | 247 / 252 | 21.5% [17.1%, 26.4%] | 21.4%–21.8% |
| NQ / JTR_fixed_05 | 2022 | 246 / 251 | 25.6% [21.2%, 30.8%] | 25.5%–25.9% |
| NQ / JTR_fixed_05 | 2023 | 245 / 250 | 26.1% [20.5%, 31.8%] | 26.0%–26.4% |
| NQ / JTR_fixed_05 | 2024 | 224 / 252 | 23.7% [18.4%, 29.3%] | 23.6%–24.0% |
| NQ / JTR_fixed_06 | 2020 | 246 / 253 | 30.1% [24.9%, 36.6%] | 30.5%–30.9% |
| NQ / JTR_fixed_06 | 2021 | 247 / 252 | 30.0% [24.7%, 36.6%] | 29.8%–30.2% |
| NQ / JTR_fixed_06 | 2022 | 246 / 251 | 28.9% [23.6%, 34.7%] | 28.7%–29.1% |
| NQ / JTR_fixed_06 | 2023 | 244 / 250 | 24.6% [19.6%, 29.7%] | 24.4%–25.2% |
| NQ / JTR_fixed_06 | 2024 | 223 / 252 | 29.1% [23.4%, 35.5%] | 28.9%–29.8% |
| NQ / JTR_fixed_07 | 2020 | 244 / 253 | 43.0% [36.4%, 49.6%] | 42.2%–44.2% |
| NQ / JTR_fixed_07 | 2021 | 247 / 252 | 44.1% [38.8%, 50.2%] | 44.4%–44.4% |
| NQ / JTR_fixed_07 | 2022 | 246 / 251 | 52.8% [47.4%, 58.1%] | 53.0%–53.0% |
| NQ / JTR_fixed_07 | 2023 | 244 / 250 | 52.0% [45.7%, 57.9%] | 51.6%–52.4% |
| NQ / JTR_fixed_07 | 2024 | 223 / 252 | 45.7% [39.8%, 52.3%] | 46.2%–46.2% |
| NQ / JTR_fixed_08 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 24.3%–100.0% |
| NQ / JTR_fixed_08 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 30.0%–100.0% |
| NQ / JTR_fixed_08 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 23.6%–100.0% |
| NQ / JTR_fixed_08 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 22.5%–100.0% |
| NQ / JTR_fixed_08 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 32.3%–100.0% |
| NQ / JTR_fixed_EST_sensitivity_01 | 2020 | 238 / 253 | 30.7% [24.0%, 36.8%] | 30.1%–32.9% |
| NQ / JTR_fixed_EST_sensitivity_01 | 2021 | 228 / 252 | 36.4% [29.9%, 43.7%] | 35.6%–41.3% |
| NQ / JTR_fixed_EST_sensitivity_01 | 2022 | 241 / 251 | 36.1% [30.3%, 42.6%] | 35.2%–37.7% |
| NQ / JTR_fixed_EST_sensitivity_01 | 2023 | 230 / 250 | 28.3% [23.7%, 33.6%] | 28.2%–32.7% |
| NQ / JTR_fixed_EST_sensitivity_01 | 2024 | 206 / 252 | 34.0% [29.0%, 39.9%] | 33.3%–38.7% |
| NQ / JTR_fixed_EST_sensitivity_02 | 2020 | 240 / 253 | 61.7% [55.9%, 68.1%] | 60.9%–62.1% |
| NQ / JTR_fixed_EST_sensitivity_02 | 2021 | 237 / 252 | 60.3% [55.1%, 65.1%] | 59.3%–61.0% |
| NQ / JTR_fixed_EST_sensitivity_02 | 2022 | 245 / 251 | 64.9% [59.0%, 71.5%] | 64.6%–65.0% |
| NQ / JTR_fixed_EST_sensitivity_02 | 2023 | 235 / 250 | 63.0% [57.7%, 69.2%] | 61.8%–63.9% |
| NQ / JTR_fixed_EST_sensitivity_02 | 2024 | 216 / 252 | 63.4% [57.8%, 70.1%] | 63.0%–63.9% |
| NQ / JTR_fixed_EST_sensitivity_03 | 2020 | 241 / 253 | 32.0% [25.5%, 37.3%] | 31.8%–33.1% |
| NQ / JTR_fixed_EST_sensitivity_03 | 2021 | 243 / 252 | 34.2% [28.1%, 39.9%] | 33.5%–35.5% |
| NQ / JTR_fixed_EST_sensitivity_03 | 2022 | 245 / 251 | 34.3% [28.6%, 39.0%] | 33.6%–35.6% |
| NQ / JTR_fixed_EST_sensitivity_03 | 2023 | 243 / 250 | 31.3% [25.7%, 36.8%] | 31.0%–31.8% |
| NQ / JTR_fixed_EST_sensitivity_03 | 2024 | 223 / 252 | 25.6% [19.9%, 31.7%] | 25.2%–26.5% |
| NQ / JTR_fixed_EST_sensitivity_04 | 2020 | 242 / 253 | 31.0% [24.1%, 37.4%] | 31.0%–31.0% |
| NQ / JTR_fixed_EST_sensitivity_04 | 2021 | 247 / 252 | 26.3% [19.5%, 32.7%] | 26.3%–26.3% |
| NQ / JTR_fixed_EST_sensitivity_04 | 2022 | 245 / 251 | 23.3% [17.6%, 28.9%] | 23.3%–23.3% |
| NQ / JTR_fixed_EST_sensitivity_04 | 2023 | 243 / 250 | 23.5% [17.2%, 28.6%] | 23.5%–23.5% |
| NQ / JTR_fixed_EST_sensitivity_04 | 2024 | 224 / 252 | 20.1% [14.1%, 26.5%] | 20.1%–20.1% |
| NQ / JTR_fixed_EST_sensitivity_05 | 2020 | 246 / 253 | 32.1% [27.0%, 37.9%] | 31.7%–32.9% |
| NQ / JTR_fixed_EST_sensitivity_05 | 2021 | 247 / 252 | 30.0% [24.7%, 35.8%] | 29.8%–30.2% |
| NQ / JTR_fixed_EST_sensitivity_05 | 2022 | 246 / 251 | 32.5% [27.9%, 37.6%] | 32.4%–32.8% |
| NQ / JTR_fixed_EST_sensitivity_05 | 2023 | 244 / 250 | 30.3% [25.0%, 36.0%] | 30.5%–30.9% |
| NQ / JTR_fixed_EST_sensitivity_05 | 2024 | 223 / 252 | 33.6% [27.9%, 39.2%] | 33.3%–34.2% |
| NQ / JTR_fixed_EST_sensitivity_06 | 2020 | 246 / 253 | 37.0% [30.6%, 43.5%] | 37.3%–37.8% |
| NQ / JTR_fixed_EST_sensitivity_06 | 2021 | 247 / 252 | 36.8% [30.9%, 44.5%] | 36.7%–37.1% |
| NQ / JTR_fixed_EST_sensitivity_06 | 2022 | 246 / 251 | 37.8% [32.7%, 43.5%] | 37.7%–38.1% |
| NQ / JTR_fixed_EST_sensitivity_06 | 2023 | 244 / 250 | 40.6% [34.7%, 46.9%] | 40.7%–41.1% |
| NQ / JTR_fixed_EST_sensitivity_06 | 2024 | 223 / 252 | 39.9% [34.3%, 46.6%] | 39.6%–40.4% |
| NQ / JTR_fixed_EST_sensitivity_07 | 2020 | 84 / 253 | 45.2% [37.0%, 54.7%] | 52.0%–81.5% |
| NQ / JTR_fixed_EST_sensitivity_07 | 2021 | 175 / 252 | 45.7% [39.2%, 54.2%] | 47.2%–61.7% |
| NQ / JTR_fixed_EST_sensitivity_07 | 2022 | 244 / 251 | 47.5% [41.2%, 54.4%] | 47.4%–48.2% |
| NQ / JTR_fixed_EST_sensitivity_07 | 2023 | 241 / 250 | 51.0% [43.5%, 57.9%] | 51.4%–51.8% |
| NQ / JTR_fixed_EST_sensitivity_07 | 2024 | 220 / 252 | 42.7% [37.0%, 49.3%] | 43.3%–43.8% |
| NQ / JTR_fixed_EST_sensitivity_08 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 21.4%–100.0% |
| NQ / JTR_fixed_EST_sensitivity_08 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 15.4%–100.0% |
| NQ / JTR_fixed_EST_sensitivity_08 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 7.4%–100.0% |
| NQ / JTR_fixed_EST_sensitivity_08 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 6.2%–100.0% |
| NQ / JTR_fixed_EST_sensitivity_08 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 8.6%–100.0% |
| NQ / London02 | 2020 | 238 / 253 | 24.8% [19.3%, 30.2%] | 24.7%–25.1% |
| NQ / London02 | 2021 | 243 / 252 | 29.2% [23.2%, 34.9%] | 29.2%–29.2% |
| NQ / London02 | 2022 | 244 / 251 | 28.3% [22.4%, 34.1%] | 28.2%–28.6% |
| NQ / London02 | 2023 | 240 / 250 | 32.1% [26.1%, 37.7%] | 32.0%–32.4% |
| NQ / London02 | 2024 | 221 / 252 | 35.7% [30.0%, 42.7%] | 35.7%–35.7% |
| NQ / NY08 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / NY08 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.4%–100.0% |
| NQ / NY08 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / NY08 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / NY08 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / ONS03 | 2020 | 238 / 253 | 23.5% [18.4%, 28.8%] | 23.2%–24.5% |
| NQ / ONS03 | 2021 | 243 / 252 | 26.7% [20.7%, 32.3%] | 26.7%–26.7% |
| NQ / ONS03 | 2022 | 244 / 251 | 25.8% [20.4%, 32.0%] | 25.6%–26.4% |
| NQ / ONS03 | 2023 | 242 / 250 | 29.3% [23.3%, 35.5%] | 29.2%–29.6% |
| NQ / ONS03 | 2024 | 222 / 252 | 29.7% [23.4%, 36.4%] | 29.7%–29.7% |
| NQ / ONS20 | 2020 | 230 / 253 | 4.3% [2.1%, 7.1%] | 4.3%–6.4% |
| NQ / ONS20 | 2021 | 218 / 252 | 3.7% [1.4%, 6.0%] | 3.5%–8.3% |
| NQ / ONS20 | 2022 | 234 / 251 | 6.0% [3.3%, 8.9%] | 5.9%–7.2% |
| NQ / ONS20 | 2023 | 222 / 250 | 3.6% [1.7%, 6.0%] | 3.5%–7.0% |
| NQ / ONS20 | 2024 | 192 / 252 | 6.8% [3.3%, 10.7%] | 6.3%–13.5% |
| NQ / OR15 | 2020 | 246 / 253 | 38.6% [32.8%, 45.6%] | 38.6%–38.6% |
| NQ / OR15 | 2021 | 248 / 252 | 34.7% [29.4%, 40.7%] | 34.7%–34.7% |
| NQ / OR15 | 2022 | 247 / 251 | 38.9% [32.8%, 45.5%] | 38.9%–38.9% |
| NQ / OR15 | 2023 | 246 / 250 | 43.5% [37.5%, 48.4%] | 43.5%–43.5% |
| NQ / OR15 | 2024 | 225 / 252 | 42.2% [36.6%, 48.2%] | 42.2%–42.2% |
| NQ / OR15__shift_+10m | 2020 | 246 / 253 | 44.3% [38.2%, 51.0%] | 44.3%–44.3% |
| NQ / OR15__shift_+10m | 2021 | 248 / 252 | 39.5% [33.9%, 45.3%] | 39.5%–39.5% |
| NQ / OR15__shift_+10m | 2022 | 247 / 251 | 44.9% [39.6%, 51.2%] | 44.9%–44.9% |
| NQ / OR15__shift_+10m | 2023 | 246 / 250 | 49.2% [42.7%, 55.0%] | 49.2%–49.2% |
| NQ / OR15__shift_+10m | 2024 | 225 / 252 | 43.1% [35.3%, 49.8%] | 43.1%–43.1% |
| NQ / OR15__shift_-10m | 2020 | 244 / 253 | 58.6% [53.4%, 63.5%] | 58.6%–58.6% |
| NQ / OR15__shift_-10m | 2021 | 248 / 252 | 53.6% [47.4%, 59.6%] | 53.6%–53.6% |
| NQ / OR15__shift_-10m | 2022 | 247 / 251 | 55.5% [49.6%, 61.1%] | 55.5%–55.5% |
| NQ / OR15__shift_-10m | 2023 | 246 / 250 | 62.2% [56.7%, 66.9%] | 62.2%–62.2% |
| NQ / OR15__shift_-10m | 2024 | 225 / 252 | 56.0% [50.2%, 62.3%] | 56.0%–56.0% |
| NQ / OR5 | 2020 | 246 / 253 | 61.0% [55.9%, 65.7%] | 60.7%–61.1% |
| NQ / OR5 | 2021 | 248 / 252 | 56.0% [50.0%, 62.3%] | 56.0%–56.0% |
| NQ / OR5 | 2022 | 247 / 251 | 58.7% [52.8%, 64.4%] | 58.7%–58.7% |
| NQ / OR5 | 2023 | 246 / 250 | 63.8% [58.0%, 68.7%] | 63.8%–63.8% |
| NQ / OR5 | 2024 | 225 / 252 | 59.6% [54.1%, 66.0%] | 59.6%–59.6% |
| NQ / OR5__shift_+10m | 2020 | 246 / 253 | 61.0% [55.5%, 67.6%] | 61.0%–61.0% |
| NQ / OR5__shift_+10m | 2021 | 248 / 252 | 61.3% [55.6%, 67.3%] | 61.3%–61.3% |
| NQ / OR5__shift_+10m | 2022 | 247 / 251 | 64.0% [58.4%, 70.4%] | 64.0%–64.0% |
| NQ / OR5__shift_+10m | 2023 | 246 / 250 | 68.3% [62.5%, 73.3%] | 68.3%–68.3% |
| NQ / OR5__shift_+10m | 2024 | 225 / 252 | 68.0% [61.7%, 73.7%] | 68.0%–68.0% |
| NQ / OR5__shift_-10m | 2020 | 244 / 253 | 91.0% [86.6%, 94.6%] | 89.9%–91.1% |
| NQ / OR5__shift_-10m | 2021 | 248 / 252 | 92.3% [89.2%, 95.5%] | 91.6%–92.4% |
| NQ / OR5__shift_-10m | 2022 | 247 / 251 | 89.1% [85.7%, 92.6%] | 89.2%–89.2% |
| NQ / OR5__shift_-10m | 2023 | 246 / 250 | 89.8% [86.6%, 93.1%] | 88.8%–90.0% |
| NQ / OR5__shift_-10m | 2024 | 225 / 252 | 85.3% [81.5%, 90.0%] | 84.6%–85.5% |
| NQ / OR_activity_1_1 | 2020 | 214 / 253 | 40.2% [34.5%, 47.0%] | 40.0%–40.5% |
| NQ / OR_activity_1_1 | 2021 | 234 / 252 | 34.2% [28.9%, 40.4%] | 34.2%–34.2% |
| NQ / OR_activity_1_1 | 2022 | 238 / 251 | 39.1% [32.8%, 45.6%] | 38.9%–39.3% |
| NQ / OR_activity_1_1 | 2023 | 235 / 250 | 42.1% [36.4%, 48.1%] | 41.9%–42.4% |
| NQ / OR_activity_1_1 | 2024 | 217 / 252 | 37.8% [31.9%, 44.0%] | 37.8%–37.8% |
| NQ / OR_activity_1_2 | 2020 | 219 / 253 | 55.7% [50.5%, 60.4%] | 55.7%–55.7% |
| NQ / OR_activity_1_2 | 2021 | 243 / 252 | 49.8% [44.1%, 56.3%] | 49.8%–49.8% |
| NQ / OR_activity_1_2 | 2022 | 245 / 251 | 53.5% [47.7%, 59.1%] | 53.5%–53.5% |
| NQ / OR_activity_1_2 | 2023 | 242 / 250 | 59.5% [53.1%, 64.8%] | 59.5%–59.5% |
| NQ / OR_activity_1_2 | 2024 | 220 / 252 | 54.1% [48.4%, 60.9%] | 54.1%–54.1% |
| NQ / OR_activity_3_2 | 2020 | 202 / 253 | 31.7% [25.5%, 38.5%] | 31.4%–32.4% |
| NQ / OR_activity_3_2 | 2021 | 232 / 252 | 25.9% [20.5%, 32.1%] | 25.9%–25.9% |
| NQ / OR_activity_3_2 | 2022 | 232 / 251 | 28.4% [23.4%, 34.3%] | 28.4%–28.4% |
| NQ / OR_activity_3_2 | 2023 | 228 / 250 | 29.8% [24.0%, 35.7%] | 29.6%–30.4% |
| NQ / OR_activity_3_2 | 2024 | 214 / 252 | 24.8% [18.5%, 31.2%] | 24.7%–25.1% |
| NQ / PIN015_Asia_UTC | 2020 | 229 / 253 | 4.4% [2.2%, 7.0%] | 4.4%–4.4% |
| NQ / PIN015_Asia_UTC | 2021 | 216 / 252 | 6.9% [4.0%, 10.1%] | 6.9%–7.4% |
| NQ / PIN015_Asia_UTC | 2022 | 233 / 251 | 6.4% [3.4%, 9.7%] | 6.4%–6.4% |
| NQ / PIN015_Asia_UTC | 2023 | 221 / 250 | 14.0% [9.7%, 18.9%] | 14.0%–14.0% |
| NQ / PIN015_Asia_UTC | 2024 | 191 / 252 | 12.6% [7.3%, 17.0%] | 12.5%–13.0% |
| NQ / PIN015_London_UTC | 2020 | 238 / 253 | 23.1% [18.1%, 28.0%] | 23.1%–23.1% |
| NQ / PIN015_London_UTC | 2021 | 243 / 252 | 28.8% [22.8%, 34.8%] | 28.8%–28.8% |
| NQ / PIN015_London_UTC | 2022 | 244 / 251 | 24.6% [19.4%, 29.9%] | 24.5%–24.9% |
| NQ / PIN015_London_UTC | 2023 | 242 / 250 | 29.3% [23.6%, 34.3%] | 29.2%–29.6% |
| NQ / PIN015_London_UTC | 2024 | 221 / 252 | 30.3% [25.2%, 36.3%] | 30.3%–30.3% |
| NQ / PIN015_NY_UTC | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | unavailable–unavailable |
| NQ / PIN015_NY_UTC | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / PIN015_NY_UTC | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / PIN015_NY_UTC | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / PIN015_NY_UTC | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / PIN073_1 | 2020 | 244 / 253 | 46.3% [41.2%, 52.3%] | 46.3%–46.3% |
| NQ / PIN073_1 | 2021 | 245 / 252 | 46.9% [40.2%, 53.7%] | 47.0%–47.4% |
| NQ / PIN073_1 | 2022 | 246 / 251 | 54.5% [48.6%, 60.4%] | 54.3%–54.7% |
| NQ / PIN073_1 | 2023 | 241 / 250 | 55.2% [49.0%, 61.2%] | 55.4%–55.4% |
| NQ / PIN073_1 | 2024 | 221 / 252 | 53.8% [47.2%, 59.2%] | 53.8%–54.3% |
| NQ / PIN073_2 | 2020 | 244 / 253 | 73.0% [66.9%, 78.8%] | 72.7%–73.1% |
| NQ / PIN073_2 | 2021 | 248 / 252 | 69.4% [64.0%, 75.0%] | 69.1%–69.5% |
| NQ / PIN073_2 | 2022 | 247 / 251 | 69.2% [63.6%, 74.2%] | 68.7%–69.5% |
| NQ / PIN073_2 | 2023 | 246 / 250 | 69.5% [63.7%, 74.9%] | 68.7%–69.9% |
| NQ / PIN073_2 | 2024 | 225 / 252 | 67.6% [61.7%, 73.7%] | 67.0%–67.8% |
| NQ / PIN073_3 | 2020 | 237 / 253 | 63.7% [57.2%, 69.9%] | 62.7%–64.3% |
| NQ / PIN073_3 | 2021 | 228 / 252 | 64.9% [58.4%, 70.8%] | 63.2%–65.8% |
| NQ / PIN073_3 | 2022 | 243 / 251 | 67.5% [60.9%, 74.1%] | 66.9%–67.8% |
| NQ / PIN073_3 | 2023 | 229 / 250 | 66.4% [60.3%, 73.3%] | 64.7%–67.2% |
| NQ / PIN073_3 | 2024 | 202 / 252 | 56.4% [49.5%, 63.7%] | 54.7%–58.5% |
| NQ / PIN073_4 | 2020 | 246 / 253 | 35.4% [30.0%, 41.2%] | 35.3%–36.1% |
| NQ / PIN073_4 | 2021 | 247 / 252 | 38.9% [32.9%, 45.3%] | 39.1%–39.1% |
| NQ / PIN073_4 | 2022 | 246 / 251 | 44.3% [38.4%, 49.0%] | 44.1%–44.5% |
| NQ / PIN073_4 | 2023 | 244 / 250 | 47.5% [40.5%, 53.5%] | 47.6%–48.0% |
| NQ / PIN073_4 | 2024 | 223 / 252 | 43.9% [37.6%, 50.5%] | 44.0%–44.4% |
| NQ / PIN073_5 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 40.5%–100.0% |
| NQ / PIN073_5 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 43.7%–100.0% |
| NQ / PIN073_5 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 43.1%–100.0% |
| NQ / PIN073_5 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 38.1%–100.0% |
| NQ / PIN073_5 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 46.6%–100.0% |
| NQ / PIN074_ref_00 | 2020 | 237 / 253 | 87.3% [83.5%, 91.4%] | 86.3%–88.0% |
| NQ / PIN074_ref_00 | 2021 | 228 / 252 | 92.1% [88.4%, 95.2%] | 88.4%–92.8% |
| NQ / PIN074_ref_00 | 2022 | 243 / 251 | 88.9% [84.7%, 92.5%] | 87.9%–89.1% |
| NQ / PIN074_ref_00 | 2023 | 229 / 250 | 91.7% [88.5%, 95.5%] | 87.1%–92.4% |
| NQ / PIN074_ref_00 | 2024 | 202 / 252 | 86.1% [82.2%, 90.6%] | 81.7%–87.5% |
| NQ / PIN074_ref_01 | 2020 | 240 / 253 | 87.5% [82.9%, 91.9%] | 87.4%–87.8% |
| NQ / PIN074_ref_01 | 2021 | 241 / 252 | 86.3% [82.6%, 90.4%] | 85.5%–86.7% |
| NQ / PIN074_ref_01 | 2022 | 246 / 251 | 91.9% [88.8%, 95.2%] | 91.6%–92.0% |
| NQ / PIN074_ref_01 | 2023 | 237 / 250 | 90.3% [86.9%, 93.8%] | 89.5%–90.7% |
| NQ / PIN074_ref_01 | 2024 | 218 / 252 | 87.2% [82.4%, 91.7%] | 85.8%–87.6% |
| NQ / PIN074_ref_03 | 2020 | 243 / 253 | 77.0% [71.3%, 82.2%] | 76.3%–77.5% |
| NQ / PIN074_ref_03 | 2021 | 245 / 252 | 78.8% [73.5%, 83.9%] | 77.8%–79.4% |
| NQ / PIN074_ref_03 | 2022 | 247 / 251 | 81.8% [76.5%, 86.5%] | 82.1%–82.1% |
| NQ / PIN074_ref_03 | 2023 | 243 / 250 | 79.0% [73.4%, 83.8%] | 78.8%–79.6% |
| NQ / PIN074_ref_03 | 2024 | 222 / 252 | 82.9% [76.9%, 88.4%] | 81.9%–83.3% |
| NQ / PIN074_ref_04 | 2020 | 241 / 253 | 82.2% [77.7%, 86.3%] | 81.4%–82.6% |
| NQ / PIN074_ref_04 | 2021 | 243 / 252 | 78.2% [72.6%, 83.5%] | 77.6%–78.8% |
| NQ / PIN074_ref_04 | 2022 | 246 / 251 | 74.8% [70.1%, 80.7%] | 74.5%–75.3% |
| NQ / PIN074_ref_04 | 2023 | 243 / 250 | 76.1% [70.7%, 81.3%] | 75.4%–76.6% |
| NQ / PIN074_ref_04 | 2024 | 223 / 252 | 75.8% [70.3%, 81.3%] | 75.2%–76.1% |
| NQ / PIN074_ref_07 | 2020 | 241 / 253 | 87.6% [83.8%, 91.7%] | 85.4%–87.9% |
| NQ / PIN074_ref_07 | 2021 | 247 / 252 | 87.0% [82.3%, 91.2%] | 86.3%–87.1% |
| NQ / PIN074_ref_07 | 2022 | 245 / 251 | 90.2% [86.6%, 93.9%] | 88.8%–90.4% |
| NQ / PIN074_ref_07 | 2023 | 243 / 250 | 90.1% [86.4%, 93.8%] | 88.4%–90.4% |
| NQ / PIN074_ref_07 | 2024 | 224 / 252 | 89.3% [85.2%, 93.5%] | 88.6%–89.5% |
| NQ / PIN075_01 | 2020 | 229 / 253 | 23.6% [17.8%, 29.8%] | 23.3%–24.6% |
| NQ / PIN075_01 | 2021 | 226 / 252 | 34.5% [28.7%, 40.6%] | 33.3%–36.8% |
| NQ / PIN075_01 | 2022 | 236 / 251 | 32.2% [26.2%, 38.2%] | 31.8%–33.1% |
| NQ / PIN075_01 | 2023 | 218 / 250 | 25.7% [20.6%, 31.9%] | 24.6%–28.9% |
| NQ / PIN075_01 | 2024 | 205 / 252 | 20.5% [14.4%, 25.5%] | 19.8%–23.1% |
| NQ / PIN075_02 | 2020 | 226 / 253 | 1.8% [0.4%, 3.6%] | 1.7%–5.5% |
| NQ / PIN075_02 | 2021 | 212 / 252 | 0.9% [0.0%, 2.4%] | 0.9%–7.1% |
| NQ / PIN075_02 | 2022 | 231 / 251 | 1.3% [0.0%, 3.0%] | 1.2%–5.4% |
| NQ / PIN075_02 | 2023 | 212 / 250 | 3.3% [0.9%, 5.4%] | 3.1%–8.1% |
| NQ / PIN075_02 | 2024 | 191 / 252 | 3.7% [1.2%, 6.8%] | 3.4%–11.1% |
| NQ / PIN075_03 | 2020 | 234 / 253 | 10.3% [7.1%, 14.2%] | 10.3%–10.3% |
| NQ / PIN075_03 | 2021 | 222 / 252 | 16.7% [11.2%, 21.7%] | 16.6%–17.0% |
| NQ / PIN075_03 | 2022 | 236 / 251 | 19.5% [14.5%, 24.9%] | 19.5%–19.5% |
| NQ / PIN075_03 | 2023 | 224 / 250 | 22.3% [16.2%, 28.3%] | 22.3%–22.3% |
| NQ / PIN075_03 | 2024 | 198 / 252 | 20.7% [13.9%, 25.9%] | 20.7%–20.7% |
| NQ / PIN075_04 | 2020 | 241 / 253 | 17.8% [13.1%, 22.4%] | 17.5%–19.5% |
| NQ / PIN075_04 | 2021 | 245 / 252 | 22.0% [17.2%, 26.8%] | 21.7%–23.3% |
| NQ / PIN075_04 | 2022 | 246 / 251 | 21.5% [15.9%, 25.8%] | 21.7%–22.5% |
| NQ / PIN075_04 | 2023 | 243 / 250 | 26.7% [22.0%, 33.2%] | 26.5%–27.3% |
| NQ / PIN075_04 | 2024 | 222 / 252 | 36.9% [30.6%, 44.0%] | 36.4%–37.8% |
| NQ / PIN075_05 | 2020 | 238 / 253 | 21.8% [17.2%, 27.1%] | 21.7%–23.8% |
| NQ / PIN075_05 | 2021 | 243 / 252 | 15.2% [10.6%, 19.8%] | 15.0%–16.3% |
| NQ / PIN075_05 | 2022 | 245 / 251 | 16.3% [11.7%, 20.6%] | 16.2%–17.0% |
| NQ / PIN075_05 | 2023 | 243 / 250 | 19.8% [15.4%, 24.4%] | 19.8%–19.8% |
| NQ / PIN075_05 | 2024 | 222 / 252 | 14.4% [10.5%, 18.6%] | 14.3%–14.8% |
| NQ / PIN075_06 | 2020 | 239 / 253 | 42.3% [35.6%, 48.5%] | 42.1%–43.0% |
| NQ / PIN075_06 | 2021 | 243 / 252 | 51.9% [43.7%, 59.8%] | 51.4%–52.2% |
| NQ / PIN075_06 | 2022 | 244 / 251 | 52.9% [46.7%, 60.2%] | 52.4%–53.3% |
| NQ / PIN075_06 | 2023 | 243 / 250 | 55.1% [48.8%, 60.9%] | 54.9%–55.3% |
| NQ / PIN075_06 | 2024 | 223 / 252 | 55.6% [49.8%, 61.7%] | 55.6%–55.6% |
| NQ / PIN075_07 | 2020 | 241 / 253 | 41.9% [35.3%, 48.1%] | 41.9%–41.9% |
| NQ / PIN075_07 | 2021 | 245 / 252 | 40.8% [34.6%, 46.6%] | 40.8%–40.8% |
| NQ / PIN075_07 | 2022 | 245 / 251 | 43.3% [37.4%, 49.2%] | 43.3%–43.3% |
| NQ / PIN075_07 | 2023 | 243 / 250 | 39.5% [33.3%, 44.8%] | 39.5%–39.5% |
| NQ / PIN075_07 | 2024 | 224 / 252 | 41.1% [36.2%, 47.0%] | 41.1%–41.1% |
| NQ / PIN075_08 | 2020 | 246 / 253 | 35.4% [30.4%, 41.9%] | 35.7%–36.1% |
| NQ / PIN075_08 | 2021 | 247 / 252 | 32.4% [27.5%, 38.2%] | 32.3%–32.7% |
| NQ / PIN075_08 | 2022 | 246 / 251 | 32.5% [27.2%, 39.1%] | 32.4%–32.8% |
| NQ / PIN075_08 | 2023 | 244 / 250 | 36.1% [31.4%, 41.8%] | 35.8%–36.6% |
| NQ / PIN075_08 | 2024 | 223 / 252 | 31.4% [25.1%, 38.1%] | 31.1%–32.0% |
| NQ / PIN075_09 | 2020 | 246 / 253 | 22.8% [17.7%, 27.4%] | 22.5%–23.7% |
| NQ / PIN075_09 | 2021 | 247 / 252 | 17.8% [12.6%, 23.4%] | 17.7%–18.1% |
| NQ / PIN075_09 | 2022 | 246 / 251 | 23.2% [17.6%, 29.5%] | 23.1%–23.5% |
| NQ / PIN075_09 | 2023 | 244 / 250 | 23.4% [18.4%, 28.8%] | 23.2%–24.0% |
| NQ / PIN075_09 | 2024 | 223 / 252 | 25.1% [19.5%, 30.0%] | 24.9%–25.8% |
| NQ / PIN075_10 | 2020 | 245 / 253 | 30.6% [24.8%, 35.6%] | 30.9%–31.7% |
| NQ / PIN075_10 | 2021 | 247 / 252 | 31.6% [25.9%, 37.2%] | 31.9%–31.9% |
| NQ / PIN075_10 | 2022 | 246 / 251 | 40.2% [33.5%, 46.2%] | 40.1%–40.5% |
| NQ / PIN075_10 | 2023 | 244 / 250 | 40.6% [34.7%, 45.7%] | 40.2%–41.1% |
| NQ / PIN075_10 | 2024 | 223 / 252 | 41.7% [34.9%, 47.4%] | 41.8%–42.2% |
| NQ / PIN075_11 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 23.6%–100.0% |
| NQ / PIN075_11 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 17.4%–100.0% |
| NQ / PIN075_11 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 18.3%–100.0% |
| NQ / PIN075_11 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 18.4%–100.0% |
| NQ / PIN075_11 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 16.6%–100.0% |
| NQ / PIN075_12 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / PIN075_12 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 1.6%–100.0% |
| NQ / PIN075_12 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.8%–100.0% |
| NQ / PIN075_12 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 2.0%–100.0% |
| NQ / PIN075_12 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.4%–100.0% |
| NQ / PIN076_00_08 | 2020 | 237 / 253 | 87.3% [83.5%, 91.4%] | 86.3%–88.0% |
| NQ / PIN076_00_08 | 2021 | 228 / 252 | 92.1% [88.4%, 95.2%] | 88.4%–92.8% |
| NQ / PIN076_00_08 | 2022 | 243 / 251 | 88.9% [84.7%, 92.5%] | 87.9%–89.1% |
| NQ / PIN076_00_08 | 2023 | 229 / 250 | 91.7% [88.5%, 95.5%] | 87.1%–92.4% |
| NQ / PIN076_00_08 | 2024 | 202 / 252 | 86.1% [82.2%, 90.6%] | 81.7%–87.5% |
| NQ / PIN076_08_0930 | 2020 | 244 / 253 | 93.9% [91.0%, 96.7%] | 93.1%–93.9% |
| NQ / PIN076_08_0930 | 2021 | 248 / 252 | 92.3% [89.1%, 95.6%] | 91.6%–92.4% |
| NQ / PIN076_08_0930 | 2022 | 246 / 251 | 93.1% [89.6%, 96.0%] | 92.0%–93.2% |
| NQ / PIN076_08_0930 | 2023 | 244 / 250 | 91.4% [88.1%, 94.3%] | 90.4%–91.6% |
| NQ / PIN076_08_0930 | 2024 | 225 / 252 | 95.1% [92.1%, 98.0%] | 93.9%–95.2% |
| NQ / PIN078_daily_not_combined | 2020 | 0 / 100 | unavailable [unavailable, unavailable] | unavailable–unavailable |
| NQ / PIN078_daily_not_combined | 2021 | 0 / 99 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / PIN078_daily_not_combined | 2022 | 0 / 97 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / PIN078_daily_not_combined | 2023 | 0 / 96 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / PIN078_daily_not_combined | 2024 | 0 / 101 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / PM | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / PM | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 1.2%–100.0% |
| NQ / PM | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.8%–100.0% |
| NQ / PM | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 1.2%–100.0% |
| NQ / PM | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.4%–100.0% |
| NQ / RTH0930 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / RTH0930 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.4%–100.0% |
| NQ / RTH0930 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / RTH0930 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.8%–100.0% |
| NQ / RTH0930 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / RTH_actual | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / RTH_actual | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.4%–100.0% |
| NQ / RTH_actual | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / RTH_actual | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.8%–100.0% |
| NQ / RTH_actual | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / custom09 | 2020 | 240 / 253 | 2.9% [0.8%, 5.0%] | 2.9%–4.5% |
| NQ / custom09 | 2021 | 247 / 252 | 2.0% [0.4%, 4.0%] | 2.0%–2.4% |
| NQ / custom09 | 2022 | 246 / 251 | 4.1% [1.6%, 6.9%] | 4.0%–4.5% |
| NQ / custom09 | 2023 | 244 / 250 | 4.1% [2.1%, 6.5%] | 4.1%–4.9% |
| NQ / custom09 | 2024 | 223 / 252 | 4.9% [2.3%, 8.0%] | 4.9%–5.8% |
| NQ / day00 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | unavailable–unavailable |
| NQ / day00 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / day00 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / day00 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / day00 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / futures08 | 2020 | 0 / 253 | unavailable [unavailable, unavailable] | unavailable–unavailable |
| NQ / futures08 | 2021 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / futures08 | 2022 | 0 / 251 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / futures08 | 2023 | 0 / 250 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / futures08 | 2024 | 0 / 252 | unavailable [unavailable, unavailable] | 0.0%–100.0% |
| NQ / lunch | 2020 | 244 / 253 | 38.9% [33.6%, 44.6%] | 38.3%–39.9% |
| NQ / lunch | 2021 | 247 / 252 | 37.2% [32.4%, 43.3%] | 37.1%–37.5% |
| NQ / lunch | 2022 | 246 / 251 | 35.0% [28.2%, 41.0%] | 34.8%–35.2% |
| NQ / lunch | 2023 | 244 / 250 | 38.5% [32.1%, 45.1%] | 38.2%–39.0% |
| NQ / lunch | 2024 | 223 / 252 | 30.9% [24.3%, 36.9%] | 30.7%–31.6% |
| NQ / magic_00 | 2020 | 237 / 253 | 50.6% [44.2%, 57.7%] | 50.0%–51.2% |
| NQ / magic_00 | 2021 | 228 / 252 | 54.8% [48.9%, 61.1%] | 54.3%–55.2% |
| NQ / magic_00 | 2022 | 243 / 251 | 59.7% [53.1%, 67.6%] | 59.7%–59.7% |
| NQ / magic_00 | 2023 | 229 / 250 | 56.3% [50.2%, 63.1%] | 56.1%–56.5% |
| NQ / magic_00 | 2024 | 202 / 252 | 53.0% [45.6%, 60.4%] | 52.9%–53.4% |
| NQ / magic_01 | 2020 | 240 / 253 | 44.6% [38.1%, 51.4%] | 44.6%–44.6% |
| NQ / magic_01 | 2021 | 240 / 252 | 47.1% [40.3%, 53.7%] | 47.3%–47.3% |
| NQ / magic_01 | 2022 | 246 / 251 | 57.7% [51.6%, 64.9%] | 57.5%–57.9% |
| NQ / magic_01 | 2023 | 237 / 250 | 53.6% [47.7%, 59.7%] | 53.1%–54.0% |
| NQ / magic_01 | 2024 | 218 / 252 | 47.2% [40.4%, 53.9%] | 46.8%–47.7% |
| NQ / magic_02 | 2020 | 243 / 253 | 32.1% [26.7%, 38.6%] | 32.0%–32.4% |
| NQ / magic_02 | 2021 | 244 / 252 | 34.0% [28.5%, 39.6%] | 34.4%–34.8% |
| NQ / magic_02 | 2022 | 246 / 251 | 37.8% [32.0%, 43.4%] | 37.8%–37.8% |
| NQ / magic_02 | 2023 | 241 / 250 | 39.4% [32.9%, 45.4%] | 39.3%–39.7% |
| NQ / magic_02 | 2024 | 221 / 252 | 41.6% [33.9%, 48.2%] | 41.4%–41.9% |
| NQ / magic_06 | 2020 | 239 / 253 | 56.5% [50.2%, 62.5%] | 55.8%–57.0% |
| NQ / magic_06 | 2021 | 244 / 252 | 63.5% [56.6%, 69.9%] | 63.5%–63.5% |
| NQ / magic_06 | 2022 | 244 / 251 | 63.5% [57.3%, 70.2%] | 63.4%–63.8% |
| NQ / magic_06 | 2023 | 243 / 250 | 66.7% [60.0%, 72.7%] | 66.4%–66.8% |
| NQ / magic_06 | 2024 | 223 / 252 | 66.4% [60.6%, 73.0%] | 66.4%–66.4% |
| NQ / magic_07 | 2020 | 242 / 253 | 60.3% [53.9%, 66.1%] | 60.1%–60.5% |
| NQ / magic_07 | 2021 | 247 / 252 | 65.6% [60.2%, 70.5%] | 65.6%–65.6% |
| NQ / magic_07 | 2022 | 245 / 251 | 68.2% [63.0%, 73.9%] | 67.9%–68.3% |
| NQ / magic_07 | 2023 | 243 / 250 | 69.1% [63.3%, 74.4%] | 68.9%–69.3% |
| NQ / magic_07 | 2024 | 224 / 252 | 70.5% [64.9%, 77.2%] | 70.5%–70.5% |
| NQ / magic_08 | 2020 | 244 / 253 | 63.9% [57.0%, 70.1%] | 63.9%–63.9% |
| NQ / magic_08 | 2021 | 248 / 252 | 57.7% [51.8%, 63.2%] | 57.7%–57.7% |
| NQ / magic_08 | 2022 | 246 / 251 | 52.8% [47.3%, 58.2%] | 52.8%–52.8% |
| NQ / magic_08 | 2023 | 244 / 250 | 53.7% [46.9%, 60.2%] | 53.7%–53.7% |
| NQ / magic_08 | 2024 | 225 / 252 | 55.6% [49.6%, 62.2%] | 55.6%–55.6% |
| NQ / magic_23 | 2020 | 234 / 253 | 41.0% [35.9%, 47.3%] | 40.4%–42.5% |
| NQ / magic_23 | 2021 | 223 / 252 | 42.2% [35.4%, 47.8%] | 39.8%–45.3% |
| NQ / magic_23 | 2022 | 236 / 251 | 44.9% [38.1%, 50.9%] | 44.4%–45.6% |
| NQ / magic_23 | 2023 | 224 / 250 | 49.6% [44.1%, 56.4%] | 47.4%–51.7% |
| NQ / magic_23 | 2024 | 198 / 252 | 38.4% [29.8%, 45.1%] | 35.2%–43.5% |
| NQ / prior_RTH_open_observed | 2020 | 237 / 253 | 3.4% [1.3%, 5.9%] | 3.3%–5.4% |
| NQ / prior_RTH_open_observed | 2021 | 244 / 252 | 4.9% [2.1%, 7.3%] | 4.8%–6.5% |
| NQ / prior_RTH_open_observed | 2022 | 243 / 251 | 4.5% [1.7%, 6.8%] | 4.5%–6.1% |
| NQ / prior_RTH_open_observed | 2023 | 242 / 250 | 5.4% [2.6%, 7.5%] | 5.3%–6.9% |
| NQ / prior_RTH_open_observed | 2024 | 221 / 252 | 5.4% [3.1%, 8.4%] | 5.3%–7.1% |
| NQ / prior_RTH_preopen | 2020 | 237 / 253 | 3.8% [1.7%, 6.5%] | 3.7%–5.8% |
| NQ / prior_RTH_preopen | 2021 | 244 / 252 | 5.3% [2.5%, 7.7%] | 5.2%–6.9% |
| NQ / prior_RTH_preopen | 2022 | 243 / 251 | 4.9% [2.0%, 7.5%] | 4.9%–6.5% |
| NQ / prior_RTH_preopen | 2023 | 242 / 250 | 5.8% [2.9%, 8.1%] | 5.7%–7.3% |
| NQ / prior_RTH_preopen | 2024 | 221 / 252 | 5.4% [3.1%, 8.4%] | 5.3%–7.1% |
| NQ / turn_earlier | 2020 | 246 / 253 | 49.6% [43.7%, 55.3%] | 49.6%–49.6% |
| NQ / turn_earlier | 2021 | 248 / 252 | 41.5% [35.2%, 48.2%] | 41.5%–41.5% |
| NQ / turn_earlier | 2022 | 247 / 251 | 46.2% [40.7%, 52.2%] | 46.2%–46.2% |
| NQ / turn_earlier | 2023 | 246 / 250 | 52.0% [46.4%, 56.7%] | 52.0%–52.0% |
| NQ / turn_earlier | 2024 | 225 / 252 | 48.4% [43.1%, 54.7%] | 48.4%–48.4% |
| NQ / turn_later | 2020 | 246 / 253 | 55.3% [49.8%, 60.9%] | 55.4%–55.8% |
| NQ / turn_later | 2021 | 247 / 252 | 52.2% [46.8%, 58.5%] | 52.0%–52.4% |
| NQ / turn_later | 2022 | 246 / 251 | 57.3% [52.2%, 63.4%] | 57.5%–57.5% |
| NQ / turn_later | 2023 | 245 / 250 | 58.8% [52.0%, 65.4%] | 58.5%–58.9% |
| NQ / turn_later | 2024 | 224 / 252 | 56.7% [49.8%, 62.1%] | 56.4%–56.9% |
| NQ / turn_source | 2020 | 246 / 253 | 51.2% [45.4%, 57.7%] | 51.2%–51.2% |
| NQ / turn_source | 2021 | 248 / 252 | 50.0% [44.2%, 56.5%] | 50.0%–50.0% |
| NQ / turn_source | 2022 | 247 / 251 | 53.0% [47.6%, 59.3%] | 53.0%–53.0% |
| NQ / turn_source | 2023 | 246 / 250 | 57.7% [51.4%, 63.3%] | 57.7%–57.7% |
| NQ / turn_source | 2024 | 225 / 252 | 51.1% [43.5%, 58.0%] | 51.1%–51.1% |

## Does waiting reveal more information or merely change the target?

The retained tables separately cover 15/30/60/180-minute horizons, actual cash-close endpoints, prefix updates and the common 10:01 prediction cut. First-breach curves at 1/5/15/30/60/180 minutes use observed prefixes and preserve no-event and censored dates. A later formation supplies later information and usually a shorter remaining fixed-end horizon. Timing superiority requires the independently scored common-cut, common-endpoint targets with prior-scale and available-geometry controls. The adjacent clock and OR15-volume activity constructions are named experiments, not selected defaults. Auction-completed windows require their separately admitted auction observations; minute volume is not an auction-state substitute.

Every retained clock/horizon appears below, including prefix and common-cut updates. Each timing cell gives the observed-prefix rate and its actual event/known-outcome denominator. A requested time beyond the planned horizon has no eligible observations; censored truth is not a non-event. First-event medians are conditional on an observed event and display the range of annual medians of its lower/upper observation-time bounds. Pooling observed-prefix counts is descriptive and does not estimate a censoring-adjusted survival distribution.

| Instrument / clock | Horizon | Complete / intended | First by 15m (events/known) | First by 60m (events/known) | First by 180m (events/known) | Annual median first-event lower / upper bounds, minutes |
|---|---|---:|---|---|---|---|
| ES / AM | after_15m | 1235 / 1258 | 27.1% (335/1235) | unavailable (0/0) | unavailable (0/0) | 1.50–3.00 / 2.50–4.00 |
| ES / AM | after_180m | 1225 / 1258 | 27.1% (335/1235) | 50.9% (627/1233) | 79.6% (981/1233) | 30.00–44.50 / 31.00–45.50 |
| ES / AM | after_30m | 1235 / 1258 | 27.1% (335/1235) | unavailable (0/0) | unavailable (0/0) | 4.00–8.00 / 5.00–9.00 |
| ES / AM | after_60m | 1227 / 1258 | 27.1% (335/1235) | 50.9% (627/1233) | unavailable (0/0) | 8.00–15.50 / 9.00–16.50 |
| ES / AM | to_actual_cash_close | 1234 / 1258 | 27.1% (335/1235) | 50.6% (620/1226) | 79.4% (974/1226) | 34.00–63.00 / 35.00–64.00 |
| ES / Asia19 | after_15m | 963 / 1258 | 27.2% (262/963) | unavailable (0/0) | unavailable (0/0) | 0.00–4.00 / 1.00–5.00 |
| ES / Asia19 | after_180m | 962 / 1258 | 27.2% (262/963) | 49.8% (480/963) | 85.6% (824/963) | 38.50–53.50 / 39.50–54.50 |
| ES / Asia19 | after_30m | 963 / 1258 | 27.2% (262/963) | unavailable (0/0) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| ES / Asia19 | after_60m | 963 / 1258 | 27.2% (262/963) | 49.8% (480/963) | unavailable (0/0) | 10.00–14.00 / 11.00–15.00 |
| ES / Asia19 | to_actual_cash_close | 954 / 1258 | 27.2% (262/963) | 49.8% (480/963) | 85.6% (824/963) | 43.00–69.00 / 44.00–70.00 |
| ES / Asia20 | after_15m | 1001 / 1258 | 30.7% (307/1001) | unavailable (0/0) | unavailable (0/0) | 0.00–4.00 / 1.00–5.00 |
| ES / Asia20 | after_180m | 1000 / 1258 | 30.7% (307/1001) | 54.4% (545/1001) | 88.3% (884/1001) | 29.00–48.00 / 30.00–49.00 |
| ES / Asia20 | after_30m | 1001 / 1258 | 30.7% (307/1001) | unavailable (0/0) | unavailable (0/0) | 4.00–7.00 / 5.00–8.00 |
| ES / Asia20 | after_60m | 1001 / 1258 | 30.7% (307/1001) | 54.4% (545/1001) | unavailable (0/0) | 9.00–15.00 / 10.00–16.00 |
| ES / Asia20 | prefix_15m_to_actual_cash_close | 992 / 1258 | 33.4% (334/1001) | 64.0% (641/1001) | 88.1% (882/1001) | 40.50–54.00 / 41.50–55.00 |
| ES / Asia20 | prefix_30m_to_actual_cash_close | 992 / 1258 | 35.8% (358/1001) | 69.6% (697/1001) | 88.6% (887/1001) | 29.00–42.00 / 30.00–43.00 |
| ES / Asia20 | prefix_60m_to_actual_cash_close | 992 / 1258 | 54.3% (544/1001) | 75.0% (751/1001) | 88.5% (886/1001) | 2.00–21.00 / 3.00–22.00 |
| ES / Asia20 | to_actual_cash_close | 992 / 1258 | 30.7% (307/1001) | 54.4% (545/1001) | 88.3% (884/1001) | 36.00–61.00 / 37.00–62.00 |
| ES / JTR_fixed_01 | after_15m | 1212 / 1258 | 61.8% (751/1216) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| ES / JTR_fixed_01 | after_180m | 1131 / 1258 | 61.8% (751/1216) | 90.7% (1099/1212) | 98.3% (1187/1207) | 7.00–8.00 / 8.00–9.00 |
| ES / JTR_fixed_01 | after_30m | 1207 / 1258 | 61.8% (751/1216) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / JTR_fixed_01 | after_60m | 1203 / 1258 | 61.8% (751/1216) | 90.7% (1099/1212) | unavailable (0/0) | 6.00–7.00 / 7.00–8.00 |
| ES / JTR_fixed_01 | to_actual_cash_close | 992 / 1258 | 61.8% (751/1216) | 90.7% (1099/1212) | 98.3% (1187/1207) | 7.00–9.00 / 8.00–10.00 |
| ES / JTR_fixed_02 | after_15m | 1124 / 1258 | 63.5% (719/1132) | unavailable (0/0) | unavailable (0/0) | 2.00–2.00 / 3.00–3.00 |
| ES / JTR_fixed_02 | after_180m | 1080 / 1258 | 63.5% (719/1132) | 95.8% (1075/1122) | 100.0% (1122/1122) | 7.00–9.00 / 8.00–10.00 |
| ES / JTR_fixed_02 | after_30m | 1097 / 1258 | 63.5% (719/1132) | unavailable (0/0) | unavailable (0/0) | 4.00–5.00 / 5.00–6.00 |
| ES / JTR_fixed_02 | after_60m | 1086 / 1258 | 63.5% (719/1132) | 95.8% (1075/1122) | unavailable (0/0) | 6.00–8.00 / 7.00–9.00 |
| ES / JTR_fixed_02 | to_actual_cash_close | 1070 / 1258 | 63.5% (719/1132) | 95.8% (1075/1122) | 100.0% (1122/1122) | 7.00–9.00 / 8.00–10.00 |
| ES / JTR_fixed_03 | after_15m | 1241 / 1258 | 61.8% (767/1241) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| ES / JTR_fixed_03 | after_180m | 1225 / 1258 | 61.8% (767/1241) | 91.2% (1132/1241) | 98.2% (1218/1240) | 4.00–9.00 / 5.00–10.00 |
| ES / JTR_fixed_03 | after_30m | 1239 / 1258 | 61.8% (767/1241) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / JTR_fixed_03 | after_60m | 1237 / 1258 | 61.8% (767/1241) | 91.2% (1132/1241) | unavailable (0/0) | 4.00–7.00 / 5.00–8.00 |
| ES / JTR_fixed_03 | to_actual_cash_close | 1216 / 1258 | 61.8% (767/1241) | 91.2% (1132/1241) | 98.2% (1218/1240) | 4.00–10.00 / 5.00–11.00 |
| ES / JTR_fixed_04 | after_15m | 1228 / 1258 | 33.9% (416/1228) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / JTR_fixed_04 | after_180m | 1224 / 1258 | 33.9% (416/1228) | 90.4% (1110/1228) | 98.5% (1209/1228) | 27.00–29.00 / 28.00–30.00 |
| ES / JTR_fixed_04 | after_30m | 1224 / 1258 | 33.9% (416/1228) | unavailable (0/0) | unavailable (0/0) | 8.00–10.50 / 9.00–11.50 |
| ES / JTR_fixed_04 | after_60m | 1224 / 1258 | 33.9% (416/1228) | 90.4% (1110/1228) | unavailable (0/0) | 20.50–29.00 / 21.50–30.00 |
| ES / JTR_fixed_04 | common_1001_to_actual_cash_close | 1224 / 1258 | 78.8% (965/1224) | 91.9% (1125/1224) | 97.9% (1189/1215) | 0.00–0.00 / 1.00–1.00 |
| ES / JTR_fixed_04 | prefix_15m_to_actual_cash_close | 1224 / 1258 | 50.0% (614/1228) | 92.3% (1133/1228) | 98.4% (1208/1228) | 14.00–16.00 / 15.00–17.00 |
| ES / JTR_fixed_04 | prefix_30m_to_actual_cash_close | 1224 / 1258 | 76.7% (939/1224) | 93.7% (1147/1224) | 98.8% (1209/1224) | 1.00–3.00 / 2.00–4.00 |
| ES / JTR_fixed_04 | prefix_60m_to_actual_cash_close | 1224 / 1258 | 78.8% (965/1224) | 91.9% (1125/1224) | 97.9% (1189/1215) | 0.00–0.00 / 1.00–1.00 |
| ES / JTR_fixed_04 | to_actual_cash_close | 1224 / 1258 | 33.9% (416/1228) | 90.4% (1110/1228) | 98.5% (1209/1228) | 28.00–30.00 / 29.00–31.00 |
| ES / JTR_fixed_04__shift_+10m | after_15m | 1230 / 1258 | 30.2% (371/1230) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| ES / JTR_fixed_04__shift_+10m | after_180m | 1224 / 1258 | 30.2% (371/1230) | 91.4% (1123/1229) | 98.4% (1209/1229) | 19.00–21.00 / 20.00–22.00 |
| ES / JTR_fixed_04__shift_+10m | after_30m | 1224 / 1258 | 30.2% (371/1230) | unavailable (0/0) | unavailable (0/0) | 16.00–19.00 / 17.00–20.00 |
| ES / JTR_fixed_04__shift_+10m | after_60m | 1224 / 1258 | 30.2% (371/1230) | 91.4% (1123/1229) | unavailable (0/0) | 19.00–20.00 / 20.00–21.00 |
| ES / JTR_fixed_04__shift_+10m | common_1001_to_actual_cash_close | 1224 / 1258 | 77.9% (954/1224) | 91.5% (1120/1224) | 97.7% (1187/1215) | 0.00–0.00 / 1.00–1.00 |
| ES / JTR_fixed_04__shift_+10m | to_actual_cash_close | 1224 / 1258 | 30.2% (371/1230) | 91.4% (1123/1229) | 98.4% (1209/1229) | 19.00–21.00 / 20.00–22.00 |
| ES / JTR_fixed_04__shift_-10m | after_15m | 1228 / 1258 | 35.9% (441/1228) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / JTR_fixed_04__shift_-10m | after_180m | 1224 / 1258 | 35.9% (441/1228) | 88.0% (1081/1228) | 98.3% (1207/1228) | 24.00–39.00 / 25.00–40.00 |
| ES / JTR_fixed_04__shift_-10m | after_30m | 1228 / 1258 | 35.9% (441/1228) | unavailable (0/0) | unavailable (0/0) | 5.00–9.00 / 6.00–10.00 |
| ES / JTR_fixed_04__shift_-10m | after_60m | 1224 / 1258 | 35.9% (441/1228) | 88.0% (1081/1228) | unavailable (0/0) | 19.00–38.00 / 20.00–39.00 |
| ES / JTR_fixed_04__shift_-10m | common_1001_to_actual_cash_close | 1224 / 1258 | 79.9% (978/1224) | 92.2% (1129/1224) | 97.7% (1187/1215) | 0.00–0.00 / 1.00–1.00 |
| ES / JTR_fixed_04__shift_-10m | to_actual_cash_close | 1224 / 1258 | 35.9% (441/1228) | 88.0% (1081/1228) | 98.3% (1207/1228) | 24.00–39.00 / 25.00–40.00 |
| ES / JTR_fixed_05 | after_15m | 1235 / 1258 | 73.4% (906/1235) | unavailable (0/0) | unavailable (0/0) | 0.00–3.00 / 1.00–4.00 |
| ES / JTR_fixed_05 | after_180m | 1227 / 1258 | 73.4% (906/1235) | 94.9% (1172/1235) | 98.9% (1221/1235) | 3.00–6.00 / 4.00–7.00 |
| ES / JTR_fixed_05 | after_30m | 1235 / 1258 | 73.4% (906/1235) | unavailable (0/0) | unavailable (0/0) | 1.00–5.00 / 2.00–6.00 |
| ES / JTR_fixed_05 | after_60m | 1235 / 1258 | 73.4% (906/1235) | 94.9% (1172/1235) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| ES / JTR_fixed_05 | to_actual_cash_close | 1234 / 1258 | 73.4% (906/1235) | 94.9% (1172/1235) | 98.9% (1212/1226) | 3.00–7.00 / 4.00–8.00 |
| ES / JTR_fixed_06 | after_15m | 1238 / 1258 | 67.3% (833/1238) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / JTR_fixed_06 | after_180m | 1228 / 1258 | 67.3% (833/1238) | 92.0% (1139/1238) | 98.9% (1225/1238) | 5.00–7.00 / 6.00–8.00 |
| ES / JTR_fixed_06 | after_30m | 1238 / 1258 | 67.3% (833/1238) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| ES / JTR_fixed_06 | after_60m | 1238 / 1258 | 67.3% (833/1238) | 92.0% (1139/1238) | unavailable (0/0) | 4.00–5.50 / 5.00–6.50 |
| ES / JTR_fixed_06 | to_actual_cash_close | 1237 / 1258 | 67.3% (833/1238) | 92.0% (1139/1238) | 98.9% (1216/1229) | 5.00–7.00 / 6.00–8.00 |
| ES / JTR_fixed_07 | after_15m | 1238 / 1258 | 69.3% (858/1238) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / JTR_fixed_07 | after_180m | 1228 / 1258 | 69.3% (858/1238) | 95.7% (1185/1238) | 99.7% (1234/1238) | 5.00–8.00 / 6.00–9.00 |
| ES / JTR_fixed_07 | after_30m | 1230 / 1258 | 69.3% (858/1238) | unavailable (0/0) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| ES / JTR_fixed_07 | after_60m | 1228 / 1258 | 69.3% (858/1238) | 95.7% (1185/1238) | unavailable (0/0) | 4.50–7.00 / 5.50–8.00 |
| ES / JTR_fixed_07 | to_actual_cash_close | 1237 / 1258 | 69.3% (858/1238) | 95.7% (1176/1229) | 99.7% (1225/1229) | 5.00–8.00 / 6.00–9.00 |
| ES / JTR_fixed_08 | after_15m | 1229 / 1258 | 76.2% (936/1229) | unavailable (0/0) | unavailable (0/0) | 1.00–4.00 / 2.00–5.00 |
| ES / JTR_fixed_08 | after_180m | 0 / 1258 | 76.2% (936/1229) | 97.7% (1184/1212) | 100.0% (1187/1187) | unavailable / unavailable |
| ES / JTR_fixed_08 | after_30m | 1229 / 1258 | 76.2% (936/1229) | unavailable (0/0) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| ES / JTR_fixed_08 | after_60m | 860 / 1258 | 76.2% (936/1229) | 97.7% (1184/1212) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| ES / JTR_fixed_08 | to_actual_cash_close | 1229 / 1258 | 76.2% (936/1229) | unavailable (0/0) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| ES / JTR_fixed_EST_sensitivity_01 | after_15m | 1229 / 1258 | 72.2% (888/1230) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| ES / JTR_fixed_EST_sensitivity_01 | after_180m | 1090 / 1258 | 72.2% (888/1230) | 92.5% (1136/1228) | 98.8% (1212/1227) | 4.00–7.00 / 5.00–8.00 |
| ES / JTR_fixed_EST_sensitivity_01 | after_30m | 1227 / 1258 | 72.2% (888/1230) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| ES / JTR_fixed_EST_sensitivity_01 | after_60m | 1218 / 1258 | 72.2% (888/1230) | 92.5% (1136/1228) | unavailable (0/0) | 3.00–6.00 / 4.00–7.00 |
| ES / JTR_fixed_EST_sensitivity_01 | to_actual_cash_close | 1008 / 1258 | 72.2% (888/1230) | 92.5% (1136/1228) | 98.8% (1212/1227) | 4.00–7.00 / 5.00–8.00 |
| ES / JTR_fixed_EST_sensitivity_02 | after_15m | 1183 / 1258 | 65.4% (776/1186) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| ES / JTR_fixed_EST_sensitivity_02 | after_180m | 1158 / 1258 | 65.4% (776/1186) | 96.8% (1145/1183) | 100.0% (1183/1183) | 6.00–10.00 / 7.00–11.00 |
| ES / JTR_fixed_EST_sensitivity_02 | after_30m | 1170 / 1258 | 65.4% (776/1186) | unavailable (0/0) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| ES / JTR_fixed_EST_sensitivity_02 | after_60m | 1165 / 1258 | 65.4% (776/1186) | 96.8% (1145/1183) | unavailable (0/0) | 5.00–9.00 / 6.00–10.00 |
| ES / JTR_fixed_EST_sensitivity_02 | to_actual_cash_close | 1147 / 1258 | 65.4% (776/1186) | 96.8% (1145/1183) | 100.0% (1183/1183) | 6.00–10.00 / 7.00–11.00 |
| ES / JTR_fixed_EST_sensitivity_03 | after_15m | 1241 / 1258 | 62.3% (774/1242) | unavailable (0/0) | unavailable (0/0) | 2.00–2.00 / 3.00–3.00 |
| ES / JTR_fixed_EST_sensitivity_03 | after_180m | 1221 / 1258 | 62.3% (774/1242) | 91.3% (1132/1240) | 98.8% (1225/1240) | 6.00–10.00 / 7.00–11.00 |
| ES / JTR_fixed_EST_sensitivity_03 | after_30m | 1236 / 1258 | 62.3% (774/1242) | unavailable (0/0) | unavailable (0/0) | 3.50–5.00 / 4.50–6.00 |
| ES / JTR_fixed_EST_sensitivity_03 | after_60m | 1233 / 1258 | 62.3% (774/1242) | 91.3% (1132/1240) | unavailable (0/0) | 5.00–7.00 / 6.00–8.00 |
| ES / JTR_fixed_EST_sensitivity_03 | to_actual_cash_close | 1216 / 1258 | 62.3% (774/1242) | 91.3% (1132/1240) | 98.8% (1225/1240) | 7.00–10.00 / 8.00–11.00 |
| ES / JTR_fixed_EST_sensitivity_04 | after_15m | 1230 / 1258 | 50.4% (620/1230) | unavailable (0/0) | unavailable (0/0) | 0.00–3.00 / 1.00–4.00 |
| ES / JTR_fixed_EST_sensitivity_04 | after_180m | 1228 / 1258 | 50.4% (620/1230) | 86.0% (1058/1230) | 96.1% (1182/1230) | 8.00–16.50 / 9.00–17.50 |
| ES / JTR_fixed_EST_sensitivity_04 | after_30m | 1228 / 1258 | 50.4% (620/1230) | unavailable (0/0) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| ES / JTR_fixed_EST_sensitivity_04 | after_60m | 1228 / 1258 | 50.4% (620/1230) | 86.0% (1058/1230) | unavailable (0/0) | 5.00–13.00 / 6.00–14.00 |
| ES / JTR_fixed_EST_sensitivity_04 | to_actual_cash_close | 1228 / 1258 | 50.4% (620/1230) | 86.0% (1058/1230) | 96.1% (1180/1228) | 9.00–18.00 / 10.00–19.00 |
| ES / JTR_fixed_EST_sensitivity_05 | after_15m | 1238 / 1258 | 69.5% (860/1238) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / JTR_fixed_EST_sensitivity_05 | after_180m | 1228 / 1258 | 69.5% (860/1238) | 93.6% (1159/1238) | 99.2% (1228/1238) | 4.00–7.00 / 5.00–8.00 |
| ES / JTR_fixed_EST_sensitivity_05 | after_30m | 1238 / 1258 | 69.5% (860/1238) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / JTR_fixed_EST_sensitivity_05 | after_60m | 1238 / 1258 | 69.5% (860/1238) | 93.6% (1159/1238) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / JTR_fixed_EST_sensitivity_05 | to_actual_cash_close | 1237 / 1258 | 69.5% (860/1238) | 93.6% (1159/1238) | 99.2% (1219/1229) | 4.00–7.00 / 5.00–8.00 |
| ES / JTR_fixed_EST_sensitivity_06 | after_15m | 1238 / 1258 | 69.7% (863/1238) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| ES / JTR_fixed_EST_sensitivity_06 | after_180m | 1228 / 1258 | 69.7% (863/1238) | 93.7% (1160/1238) | 99.4% (1230/1238) | 4.00–8.00 / 5.00–9.00 |
| ES / JTR_fixed_EST_sensitivity_06 | after_30m | 1238 / 1258 | 69.7% (863/1238) | unavailable (0/0) | unavailable (0/0) | 2.00–4.50 / 3.00–5.50 |
| ES / JTR_fixed_EST_sensitivity_06 | after_60m | 1238 / 1258 | 69.7% (863/1238) | 93.7% (1160/1238) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| ES / JTR_fixed_EST_sensitivity_06 | to_actual_cash_close | 1237 / 1258 | 69.7% (863/1238) | 93.7% (1160/1238) | 99.3% (1221/1229) | 4.00–8.00 / 5.00–9.00 |
| ES / JTR_fixed_EST_sensitivity_07 | after_15m | 1235 / 1258 | 71.8% (887/1235) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / JTR_fixed_EST_sensitivity_07 | after_180m | 992 / 1258 | 71.8% (887/1235) | 96.5% (1192/1235) | 99.8% (1233/1235) | 4.00–8.00 / 5.00–9.00 |
| ES / JTR_fixed_EST_sensitivity_07 | after_30m | 1228 / 1258 | 71.8% (887/1235) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / JTR_fixed_EST_sensitivity_07 | after_60m | 1228 / 1258 | 71.8% (887/1235) | 96.5% (1192/1235) | unavailable (0/0) | 4.00–5.00 / 5.00–6.00 |
| ES / JTR_fixed_EST_sensitivity_07 | to_actual_cash_close | 1235 / 1258 | 71.8% (887/1235) | 96.5% (1185/1228) | 99.8% (418/419) | 4.00–6.00 / 5.00–7.00 |
| ES / JTR_fixed_EST_sensitivity_08 | after_15m | 988 / 1258 | 52.6% (520/989) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / JTR_fixed_EST_sensitivity_08 | after_180m | 0 / 1258 | 52.6% (520/989) | 98.7% (686/695) | 100.0% (686/686) | unavailable / unavailable |
| ES / JTR_fixed_EST_sensitivity_08 | after_30m | 420 / 1258 | 52.6% (520/989) | unavailable (0/0) | unavailable (0/0) | 2.00–5.00 / 3.00–6.00 |
| ES / JTR_fixed_EST_sensitivity_08 | after_60m | 287 / 1258 | 52.6% (520/989) | 98.7% (686/695) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / JTR_fixed_EST_sensitivity_08 | to_actual_cash_close | 419 / 1258 | 75.2% (315/419) | unavailable (0/0) | unavailable (0/0) | 2.00–5.00 / 3.00–6.00 |
| ES / London02 | after_15m | 1206 / 1258 | 22.7% (274/1206) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / London02 | after_180m | 1204 / 1258 | 22.7% (274/1206) | 58.1% (700/1205) | 94.7% (1141/1205) | 29.00–65.00 / 30.00–66.00 |
| ES / London02 | after_30m | 1204 / 1258 | 22.7% (274/1206) | unavailable (0/0) | unavailable (0/0) | 10.00–15.00 / 11.00–16.00 |
| ES / London02 | after_60m | 1204 / 1258 | 22.7% (274/1206) | 58.1% (700/1205) | unavailable (0/0) | 20.00–29.00 / 21.00–30.00 |
| ES / London02 | to_actual_cash_close | 1204 / 1258 | 22.7% (274/1206) | 58.1% (700/1205) | 94.7% (1141/1205) | 29.00–88.00 / 30.00–89.00 |
| ES / NY08 | after_15m | 863 / 1258 | 20.0% (185/926) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / NY08 | after_180m | 0 / 1258 | 20.0% (185/926) | 99.6% (244/245) | 100.0% (244/244) | unavailable / unavailable |
| ES / NY08 | after_30m | 860 / 1258 | 20.0% (185/926) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / NY08 | after_60m | 1 / 1258 | 20.0% (185/926) | 99.6% (244/245) | unavailable (0/0) | unavailable / unavailable |
| ES / NY08 | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / ONS03 | after_15m | 1220 / 1258 | 22.0% (269/1220) | unavailable (0/0) | unavailable (0/0) | 4.00–5.00 / 5.00–6.00 |
| ES / ONS03 | after_180m | 1216 / 1258 | 22.0% (269/1220) | 48.0% (585/1220) | 94.4% (1151/1219) | 44.00–74.00 / 45.00–75.00 |
| ES / ONS03 | after_30m | 1220 / 1258 | 22.0% (269/1220) | unavailable (0/0) | unavailable (0/0) | 6.00–12.00 / 7.00–13.00 |
| ES / ONS03 | after_60m | 1220 / 1258 | 22.0% (269/1220) | 48.0% (585/1220) | unavailable (0/0) | 12.50–27.00 / 13.50–28.00 |
| ES / ONS03 | to_actual_cash_close | 1216 / 1258 | 22.0% (269/1220) | 48.0% (585/1220) | 94.4% (1151/1219) | 45.00–81.50 / 46.00–82.50 |
| ES / ONS20 | after_15m | 1078 / 1258 | 16.1% (174/1078) | unavailable (0/0) | unavailable (0/0) | 4.50–5.00 / 5.50–6.00 |
| ES / ONS20 | after_180m | 1001 / 1258 | 16.1% (174/1078) | 36.4% (371/1020) | 78.1% (792/1014) | 56.00–75.00 / 57.00–76.00 |
| ES / ONS20 | after_30m | 1043 / 1258 | 16.1% (174/1078) | unavailable (0/0) | unavailable (0/0) | 7.00–9.00 / 8.00–10.00 |
| ES / ONS20 | after_60m | 1012 / 1258 | 16.1% (174/1078) | 36.4% (371/1020) | unavailable (0/0) | 15.00–24.00 / 16.00–25.00 |
| ES / ONS20 | to_actual_cash_close | 992 / 1258 | 16.1% (174/1078) | 36.4% (371/1020) | 78.1% (792/1014) | 77.00–112.00 / 78.00–113.00 |
| ES / OR15 | after_15m | 1235 / 1258 | 82.8% (1023/1235) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| ES / OR15 | after_180m | 1235 / 1258 | 82.8% (1023/1235) | 98.8% (1220/1235) | 99.8% (1232/1235) | 2.00–4.00 / 3.00–5.00 |
| ES / OR15 | after_30m | 1235 / 1258 | 82.8% (1023/1235) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / OR15 | after_60m | 1235 / 1258 | 82.8% (1023/1235) | 98.8% (1220/1235) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / OR15 | common_1001_to_actual_cash_close | 1234 / 1258 | 87.6% (1082/1235) | 98.2% (1213/1235) | 99.6% (1221/1226) | 0.00–0.00 / 1.00–1.00 |
| ES / OR15 | prefix_15m_to_actual_cash_close | 1234 / 1258 | 87.6% (1082/1235) | 98.2% (1213/1235) | 99.6% (1221/1226) | 0.00–0.00 / 1.00–1.00 |
| ES / OR15 | prefix_30m_to_actual_cash_close | 1234 / 1258 | 88.3% (1091/1235) | 98.3% (1214/1235) | 99.6% (1221/1226) | 0.00–0.00 / 1.00–1.00 |
| ES / OR15 | prefix_60m_to_actual_cash_close | 1234 / 1258 | 87.3% (1078/1235) | 96.8% (1195/1235) | 99.6% (1221/1226) | 0.00–0.00 / 1.00–1.00 |
| ES / OR15 | to_actual_cash_close | 1234 / 1258 | 82.8% (1023/1235) | 98.8% (1220/1235) | 99.8% (1232/1235) | 2.00–4.00 / 3.00–5.00 |
| ES / OR15__shift_+10m | after_15m | 1235 / 1258 | 88.9% (1098/1235) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / OR15__shift_+10m | after_180m | 1235 / 1258 | 88.9% (1098/1235) | 99.2% (1225/1235) | 99.8% (1233/1235) | 2.00–4.00 / 3.00–5.00 |
| ES / OR15__shift_+10m | after_30m | 1235 / 1258 | 88.9% (1098/1235) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / OR15__shift_+10m | after_60m | 1235 / 1258 | 88.9% (1098/1235) | 99.2% (1225/1235) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / OR15__shift_+10m | common_1001_to_actual_cash_close | 1234 / 1258 | 89.6% (1107/1235) | 99.2% (1225/1235) | 99.8% (1224/1226) | 0.00–0.00 / 1.00–1.00 |
| ES / OR15__shift_+10m | to_actual_cash_close | 1234 / 1258 | 88.9% (1098/1235) | 99.2% (1225/1235) | 99.8% (1233/1235) | 2.00–4.00 / 3.00–5.00 |
| ES / OR15__shift_-10m | after_15m | 1232 / 1258 | 94.7% (1167/1232) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / OR15__shift_-10m | after_180m | 1232 / 1258 | 94.7% (1167/1232) | 99.8% (1229/1232) | 99.9% (1231/1232) | 0.00–2.00 / 1.00–3.00 |
| ES / OR15__shift_-10m | after_30m | 1232 / 1258 | 94.7% (1167/1232) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / OR15__shift_-10m | after_60m | 1232 / 1258 | 94.7% (1167/1232) | 99.8% (1229/1232) | unavailable (0/0) | 0.00–2.00 / 1.00–3.00 |
| ES / OR15__shift_-10m | common_1001_to_actual_cash_close | 1232 / 1258 | 94.8% (1168/1232) | 99.4% (1224/1232) | 99.9% (1222/1223) | 0.00–0.00 / 1.00–1.00 |
| ES / OR15__shift_-10m | to_actual_cash_close | 1232 / 1258 | 94.7% (1167/1232) | 99.8% (1229/1232) | 99.9% (1231/1232) | 0.00–2.00 / 1.00–3.00 |
| ES / OR5 | after_15m | 1235 / 1258 | 96.4% (1191/1236) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / OR5 | after_180m | 1235 / 1258 | 96.4% (1191/1236) | 99.8% (1234/1236) | 100.0% (1236/1236) | 0.00–1.00 / 1.00–2.00 |
| ES / OR5 | after_30m | 1235 / 1258 | 96.4% (1191/1236) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / OR5 | after_60m | 1235 / 1258 | 96.4% (1191/1236) | 99.8% (1234/1236) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / OR5 | common_1001_to_actual_cash_close | 1236 / 1258 | 96.8% (1197/1237) | 99.8% (1234/1237) | 100.0% (1228/1228) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5 | to_actual_cash_close | 1234 / 1258 | 96.4% (1191/1236) | 99.8% (1234/1236) | 100.0% (1236/1236) | 0.00–1.00 / 1.00–2.00 |
| ES / OR5__shift_+10m | after_15m | 1235 / 1258 | 98.1% (1212/1235) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_+10m | after_180m | 1235 / 1258 | 98.1% (1212/1235) | 100.0% (1235/1235) | 100.0% (1235/1235) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_+10m | after_30m | 1235 / 1258 | 98.1% (1212/1235) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_+10m | after_60m | 1235 / 1258 | 98.1% (1212/1235) | 100.0% (1235/1235) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_+10m | common_1001_to_actual_cash_close | 1234 / 1258 | 98.7% (1219/1235) | 100.0% (1235/1235) | 100.0% (1226/1226) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_+10m | to_actual_cash_close | 1234 / 1258 | 98.1% (1212/1235) | 100.0% (1235/1235) | 100.0% (1235/1235) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_-10m | after_15m | 1232 / 1258 | 99.9% (1250/1251) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_-10m | after_180m | 1232 / 1258 | 99.9% (1250/1251) | 100.0% (1251/1251) | 100.0% (1251/1251) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_-10m | after_30m | 1232 / 1258 | 99.9% (1250/1251) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_-10m | after_60m | 1232 / 1258 | 99.9% (1250/1251) | 100.0% (1251/1251) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_-10m | common_1001_to_actual_cash_close | 1232 / 1258 | 99.9% (1231/1232) | 99.9% (1231/1232) | 99.9% (1222/1223) | 0.00–0.00 / 1.00–1.00 |
| ES / OR5__shift_-10m | to_actual_cash_close | 1232 / 1258 | 99.9% (1250/1251) | 100.0% (1251/1251) | 100.0% (1251/1251) | 0.00–0.00 / 1.00–1.00 |
| ES / OR_activity_1_1 | after_15m | 1151 / 1258 | 82.5% (950/1151) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| ES / OR_activity_1_1 | after_180m | 1147 / 1258 | 82.5% (950/1151) | 98.3% (1131/1151) | 99.6% (1146/1151) | 2.00–4.00 / 3.00–5.00 |
| ES / OR_activity_1_1 | after_30m | 1151 / 1258 | 82.5% (950/1151) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| ES / OR_activity_1_1 | after_60m | 1151 / 1258 | 82.5% (950/1151) | 98.3% (1131/1151) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / OR_activity_1_1 | common_1001_to_actual_cash_close | 1120 / 1258 | 87.4% (979/1120) | 98.2% (1100/1120) | 99.5% (1109/1115) | 0.00–0.00 / 1.00–1.00 |
| ES / OR_activity_1_1 | to_actual_cash_close | 1151 / 1258 | 82.5% (950/1151) | 98.3% (1131/1151) | 99.6% (1142/1147) | 2.00–4.00 / 3.00–5.00 |
| ES / OR_activity_1_2 | after_15m | 1182 / 1258 | 92.9% (1099/1183) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / OR_activity_1_2 | after_180m | 1181 / 1258 | 92.9% (1099/1183) | 99.4% (1176/1183) | 99.8% (1181/1183) | 1.00–1.00 / 2.00–2.00 |
| ES / OR_activity_1_2 | after_30m | 1182 / 1258 | 92.9% (1099/1183) | unavailable (0/0) | unavailable (0/0) | 1.00–1.00 / 2.00–2.00 |
| ES / OR_activity_1_2 | after_60m | 1182 / 1258 | 92.9% (1099/1183) | 99.4% (1176/1183) | unavailable (0/0) | 1.00–1.00 / 2.00–2.00 |
| ES / OR_activity_1_2 | common_1001_to_actual_cash_close | 1161 / 1258 | 94.8% (1101/1161) | 99.7% (1157/1161) | 100.0% (1152/1152) | 0.00–0.00 / 1.00–1.00 |
| ES / OR_activity_1_2 | to_actual_cash_close | 1181 / 1258 | 92.9% (1099/1183) | 99.4% (1176/1183) | 99.8% (1181/1183) | 1.00–1.00 / 2.00–2.00 |
| ES / OR_activity_3_2 | after_15m | 1137 / 1258 | 76.0% (864/1137) | unavailable (0/0) | unavailable (0/0) | 1.50–2.00 / 2.50–3.00 |
| ES / OR_activity_3_2 | after_180m | 1134 / 1258 | 76.0% (864/1137) | 95.4% (1085/1137) | 98.9% (1124/1137) | 3.00–5.00 / 4.00–6.00 |
| ES / OR_activity_3_2 | after_30m | 1137 / 1258 | 76.0% (864/1137) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| ES / OR_activity_3_2 | after_60m | 1137 / 1258 | 76.0% (864/1137) | 95.4% (1085/1137) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / OR_activity_3_2 | common_1001_to_actual_cash_close | 805 / 1258 | 81.4% (655/805) | 95.8% (771/805) | 99.3% (798/804) | 0.00–2.00 / 1.00–3.00 |
| ES / OR_activity_3_2 | to_actual_cash_close | 1137 / 1258 | 76.0% (864/1137) | 95.4% (1085/1137) | 98.9% (1119/1132) | 3.50–6.00 / 4.50–7.00 |
| ES / PIN015_Asia_UTC | after_15m | 995 / 1258 | 34.3% (341/995) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| ES / PIN015_Asia_UTC | after_180m | 993 / 1258 | 34.3% (341/995) | 57.9% (576/995) | 82.3% (819/995) | 17.00–27.00 / 18.00–28.00 |
| ES / PIN015_Asia_UTC | after_30m | 995 / 1258 | 34.3% (341/995) | unavailable (0/0) | unavailable (0/0) | 5.00–9.00 / 6.00–10.00 |
| ES / PIN015_Asia_UTC | after_60m | 995 / 1258 | 34.3% (341/995) | 57.9% (576/995) | unavailable (0/0) | 8.00–12.50 / 9.00–13.50 |
| ES / PIN015_Asia_UTC | to_actual_cash_close | 986 / 1258 | 34.3% (341/995) | 57.9% (576/995) | 82.3% (819/995) | 24.00–59.50 / 25.00–60.50 |
| ES / PIN015_London_UTC | after_15m | 1213 / 1258 | 24.5% (297/1213) | unavailable (0/0) | unavailable (0/0) | 3.00–6.00 / 4.00–7.00 |
| ES / PIN015_London_UTC | after_180m | 1212 / 1258 | 24.5% (297/1213) | 66.2% (803/1213) | 94.4% (1145/1213) | 39.00–53.00 / 40.00–54.00 |
| ES / PIN015_London_UTC | after_30m | 1213 / 1258 | 24.5% (297/1213) | unavailable (0/0) | unavailable (0/0) | 7.00–11.00 / 8.00–12.00 |
| ES / PIN015_London_UTC | after_60m | 1212 / 1258 | 24.5% (297/1213) | 66.2% (803/1213) | unavailable (0/0) | 20.50–37.00 / 21.50–38.00 |
| ES / PIN015_London_UTC | to_actual_cash_close | 1212 / 1258 | 24.5% (297/1213) | 66.2% (803/1213) | 94.4% (1145/1213) | 42.00–57.00 / 43.00–58.00 |
| ES / PIN015_NY_UTC | after_15m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN015_NY_UTC | after_180m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN015_NY_UTC | after_30m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN015_NY_UTC | after_60m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN015_NY_UTC | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN073_1 | after_15m | 1225 / 1258 | 58.2% (713/1226) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| ES / PIN073_1 | after_180m | 1217 / 1258 | 58.2% (713/1226) | 98.1% (1200/1223) | 99.9% (1222/1223) | 7.00–12.50 / 8.00–13.50 |
| ES / PIN073_1 | after_30m | 1222 / 1258 | 58.2% (713/1226) | unavailable (0/0) | unavailable (0/0) | 6.00–7.00 / 7.00–8.00 |
| ES / PIN073_1 | after_60m | 1222 / 1258 | 58.2% (713/1226) | 98.1% (1200/1223) | unavailable (0/0) | 7.00–12.00 / 8.00–13.00 |
| ES / PIN073_1 | to_actual_cash_close | 1204 / 1258 | 58.2% (713/1226) | 98.1% (1200/1223) | 99.9% (1222/1223) | 7.00–13.00 / 8.00–14.00 |
| ES / PIN073_2 | after_15m | 1232 / 1258 | 98.6% (1215/1232) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN073_2 | after_180m | 1232 / 1258 | 98.6% (1215/1232) | 100.0% (1232/1232) | 100.0% (1232/1232) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN073_2 | after_30m | 1232 / 1258 | 98.6% (1215/1232) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN073_2 | after_60m | 1232 / 1258 | 98.6% (1215/1232) | 100.0% (1232/1232) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN073_2 | to_actual_cash_close | 1232 / 1258 | 98.6% (1215/1232) | 100.0% (1232/1232) | 100.0% (1232/1232) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN073_3 | after_15m | 1124 / 1258 | 63.5% (719/1132) | unavailable (0/0) | unavailable (0/0) | 2.00–2.00 / 3.00–3.00 |
| ES / PIN073_3 | after_180m | 1080 / 1258 | 63.5% (719/1132) | 95.8% (1075/1122) | 100.0% (1122/1122) | 7.00–9.00 / 8.00–10.00 |
| ES / PIN073_3 | after_30m | 1097 / 1258 | 63.5% (719/1132) | unavailable (0/0) | unavailable (0/0) | 4.00–5.00 / 5.00–6.00 |
| ES / PIN073_3 | after_60m | 1086 / 1258 | 63.5% (719/1132) | 95.8% (1075/1122) | unavailable (0/0) | 6.00–8.00 / 7.00–9.00 |
| ES / PIN073_3 | to_actual_cash_close | 1070 / 1258 | 63.5% (719/1132) | 95.8% (1075/1122) | 100.0% (1122/1122) | 7.00–9.00 / 8.00–10.00 |
| ES / PIN073_4 | after_15m | 1238 / 1258 | 71.2% (882/1238) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| ES / PIN073_4 | after_180m | 1228 / 1258 | 71.2% (882/1238) | 95.2% (1179/1238) | 99.4% (1231/1238) | 4.00–6.00 / 5.00–7.00 |
| ES / PIN073_4 | after_30m | 1238 / 1258 | 71.2% (882/1238) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / PIN073_4 | after_60m | 1238 / 1258 | 71.2% (882/1238) | 95.2% (1179/1238) | unavailable (0/0) | 3.00–5.50 / 4.00–6.50 |
| ES / PIN073_4 | to_actual_cash_close | 1237 / 1258 | 71.2% (882/1238) | 95.2% (1179/1238) | 99.4% (1222/1229) | 4.00–6.00 / 5.00–7.00 |
| ES / PIN073_5 | after_15m | 1229 / 1258 | 73.6% (905/1229) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / PIN073_5 | after_180m | 0 / 1258 | 73.6% (905/1229) | 96.4% (1185/1229) | 100.0% (1219/1219) | unavailable / unavailable |
| ES / PIN073_5 | after_30m | 1229 / 1258 | 73.6% (905/1229) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / PIN073_5 | after_60m | 1229 / 1258 | 73.6% (905/1229) | 96.4% (1185/1229) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| ES / PIN073_5 | to_actual_cash_close | 1229 / 1258 | 73.6% (905/1229) | 96.4% (1185/1229) | unavailable (0/0) | 3.00–6.50 / 4.00–7.50 |
| ES / PIN074_ref_00 | after_15m | 1172 / 1258 | 99.3% (1200/1208) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_00 | after_180m | 1064 / 1258 | 99.3% (1200/1208) | 99.9% (1207/1208) | 100.0% (1208/1208) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_00 | after_30m | 1125 / 1258 | 99.3% (1200/1208) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_00 | after_60m | 1080 / 1258 | 99.3% (1200/1208) | 99.9% (1207/1208) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_00 | to_actual_cash_close | 1054 / 1258 | 99.3% (1200/1208) | 99.9% (1207/1208) | 100.0% (1208/1208) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_01 | after_15m | 1211 / 1258 | 99.8% (1224/1226) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_01 | after_180m | 1168 / 1258 | 99.8% (1224/1226) | 100.0% (1226/1226) | 100.0% (1226/1226) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_01 | after_30m | 1186 / 1258 | 99.8% (1224/1226) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_01 | after_60m | 1172 / 1258 | 99.8% (1224/1226) | 100.0% (1226/1226) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_01 | to_actual_cash_close | 1157 / 1258 | 99.8% (1224/1226) | 100.0% (1226/1226) | 100.0% (1226/1226) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_03 | after_15m | 1246 / 1258 | 99.9% (1252/1253) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_03 | after_180m | 1228 / 1258 | 99.9% (1252/1253) | 100.0% (1253/1253) | 100.0% (1253/1253) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_03 | after_30m | 1243 / 1258 | 99.9% (1252/1253) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_03 | after_60m | 1239 / 1258 | 99.9% (1252/1253) | 100.0% (1253/1253) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_03 | to_actual_cash_close | 1216 / 1258 | 99.9% (1252/1253) | 100.0% (1253/1253) | 100.0% (1253/1253) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_04 | after_15m | 1246 / 1258 | 99.9% (1249/1250) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_04 | after_180m | 1220 / 1258 | 99.9% (1249/1250) | 100.0% (1250/1250) | 100.0% (1250/1250) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_04 | after_30m | 1245 / 1258 | 99.9% (1249/1250) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_04 | after_60m | 1238 / 1258 | 99.9% (1249/1250) | 100.0% (1250/1250) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_04 | to_actual_cash_close | 1216 / 1258 | 99.9% (1249/1250) | 100.0% (1250/1250) | 100.0% (1250/1250) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_07 | after_15m | 1245 / 1258 | 99.6% (1247/1252) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_07 | after_180m | 1231 / 1258 | 99.6% (1247/1252) | 100.0% (1252/1252) | 100.0% (1252/1252) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_07 | after_30m | 1242 / 1258 | 99.6% (1247/1252) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_07 | after_60m | 1239 / 1258 | 99.6% (1247/1252) | 100.0% (1252/1252) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN074_ref_07 | to_actual_cash_close | 1231 / 1258 | 99.6% (1247/1252) | 100.0% (1252/1252) | 100.0% (1252/1252) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN075_01 | after_15m | 1129 / 1258 | 41.1% (464/1129) | unavailable (0/0) | unavailable (0/0) | 2.00–5.00 / 3.00–6.00 |
| ES / PIN075_01 | after_180m | 1084 / 1258 | 41.1% (464/1129) | 77.5% (858/1107) | 95.0% (1050/1105) | 16.50–22.00 / 17.50–23.00 |
| ES / PIN075_01 | after_30m | 1111 / 1258 | 41.1% (464/1129) | unavailable (0/0) | unavailable (0/0) | 5.00–7.00 / 6.00–8.00 |
| ES / PIN075_01 | after_60m | 1098 / 1258 | 41.1% (464/1129) | 77.5% (858/1107) | unavailable (0/0) | 9.00–15.00 / 10.00–16.00 |
| ES / PIN075_01 | to_actual_cash_close | 937 / 1258 | 41.1% (464/1129) | 77.5% (858/1107) | 95.0% (1050/1105) | 19.00–28.00 / 20.00–29.00 |
| ES / PIN075_02 | after_15m | 1089 / 1258 | 16.1% (175/1089) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / PIN075_02 | after_180m | 967 / 1258 | 16.1% (175/1089) | 33.5% (353/1055) | 67.6% (673/996) | 43.50–66.00 / 44.50–67.00 |
| ES / PIN075_02 | after_30m | 1075 / 1258 | 16.1% (175/1089) | unavailable (0/0) | unavailable (0/0) | 7.00–11.00 / 8.00–12.00 |
| ES / PIN075_02 | after_60m | 1049 / 1258 | 16.1% (175/1089) | 33.5% (353/1055) | unavailable (0/0) | 14.00–16.00 / 15.00–17.00 |
| ES / PIN075_02 | to_actual_cash_close | 958 / 1258 | 16.1% (175/1089) | 33.5% (353/1055) | 67.6% (673/996) | 109.50–146.00 / 110.50–147.00 |
| ES / PIN075_03 | after_15m | 1031 / 1258 | 55.0% (567/1031) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / PIN075_03 | after_180m | 1029 / 1258 | 55.0% (567/1031) | 81.6% (841/1031) | 94.6% (975/1031) | 8.00–13.50 / 9.00–14.50 |
| ES / PIN075_03 | after_30m | 1031 / 1258 | 55.0% (567/1031) | unavailable (0/0) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| ES / PIN075_03 | after_60m | 1031 / 1258 | 55.0% (567/1031) | 81.6% (841/1031) | unavailable (0/0) | 5.00–9.00 / 6.00–10.00 |
| ES / PIN075_03 | to_actual_cash_close | 1022 / 1258 | 55.0% (567/1031) | 81.6% (841/1031) | 94.6% (975/1031) | 8.00–16.00 / 9.00–17.00 |
| ES / PIN075_04 | after_15m | 1239 / 1258 | 46.9% (581/1240) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| ES / PIN075_04 | after_180m | 1222 / 1258 | 46.9% (581/1240) | 84.7% (1049/1239) | 95.6% (1184/1238) | 12.50–17.00 / 13.50–18.00 |
| ES / PIN075_04 | after_30m | 1237 / 1258 | 46.9% (581/1240) | unavailable (0/0) | unavailable (0/0) | 6.00–10.00 / 7.00–11.00 |
| ES / PIN075_04 | after_60m | 1235 / 1258 | 46.9% (581/1240) | 84.7% (1049/1239) | unavailable (0/0) | 10.00–13.00 / 11.00–14.00 |
| ES / PIN075_04 | to_actual_cash_close | 1216 / 1258 | 46.9% (581/1240) | 84.7% (1049/1239) | 95.6% (1184/1238) | 14.00–18.00 / 15.00–19.00 |
| ES / PIN075_05 | after_15m | 1231 / 1258 | 32.0% (394/1231) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| ES / PIN075_05 | after_180m | 1219 / 1258 | 32.0% (394/1231) | 64.7% (795/1228) | 91.8% (1125/1225) | 25.50–39.00 / 26.50–40.00 |
| ES / PIN075_05 | after_30m | 1229 / 1258 | 32.0% (394/1231) | unavailable (0/0) | unavailable (0/0) | 5.50–9.00 / 6.50–10.00 |
| ES / PIN075_05 | after_60m | 1226 / 1258 | 32.0% (394/1231) | 64.7% (795/1228) | unavailable (0/0) | 12.00–18.50 / 13.00–19.50 |
| ES / PIN075_05 | to_actual_cash_close | 1216 / 1258 | 32.0% (394/1231) | 64.7% (795/1228) | 91.8% (1125/1225) | 33.00–40.00 / 34.00–41.00 |
| ES / PIN075_06 | after_15m | 1225 / 1258 | 41.6% (509/1225) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / PIN075_06 | after_180m | 1221 / 1258 | 41.6% (509/1225) | 82.2% (1007/1225) | 99.3% (1216/1225) | 18.00–21.00 / 19.00–22.00 |
| ES / PIN075_06 | after_30m | 1225 / 1258 | 41.6% (509/1225) | unavailable (0/0) | unavailable (0/0) | 7.00–10.00 / 8.00–11.00 |
| ES / PIN075_06 | after_60m | 1225 / 1258 | 41.6% (509/1225) | 82.2% (1007/1225) | unavailable (0/0) | 12.00–16.00 / 13.00–17.00 |
| ES / PIN075_06 | to_actual_cash_close | 1221 / 1258 | 41.6% (509/1225) | 82.2% (1007/1225) | 99.3% (1216/1225) | 18.00–22.00 / 19.00–23.00 |
| ES / PIN075_07 | after_15m | 1227 / 1258 | 74.2% (911/1227) | unavailable (0/0) | unavailable (0/0) | 0.00–2.00 / 1.00–3.00 |
| ES / PIN075_07 | after_180m | 1227 / 1258 | 74.2% (911/1227) | 93.1% (1142/1227) | 98.5% (1208/1227) | 2.00–4.50 / 3.00–5.50 |
| ES / PIN075_07 | after_30m | 1227 / 1258 | 74.2% (911/1227) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| ES / PIN075_07 | after_60m | 1227 / 1258 | 74.2% (911/1227) | 93.1% (1142/1227) | unavailable (0/0) | 1.00–4.00 / 2.00–5.00 |
| ES / PIN075_07 | to_actual_cash_close | 1227 / 1258 | 74.2% (911/1227) | 93.1% (1142/1227) | 98.5% (1208/1227) | 2.00–5.00 / 3.00–6.00 |
| ES / PIN075_08 | after_15m | 1238 / 1258 | 74.5% (922/1238) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| ES / PIN075_08 | after_180m | 1228 / 1258 | 74.5% (922/1238) | 95.2% (1178/1238) | 99.6% (1233/1238) | 4.00–6.00 / 5.00–7.00 |
| ES / PIN075_08 | after_30m | 1238 / 1258 | 74.5% (922/1238) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / PIN075_08 | after_60m | 1238 / 1258 | 74.5% (922/1238) | 95.2% (1178/1238) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| ES / PIN075_08 | to_actual_cash_close | 1237 / 1258 | 74.5% (922/1238) | 95.2% (1178/1238) | 99.6% (1224/1229) | 4.00–6.50 / 5.00–7.50 |
| ES / PIN075_09 | after_15m | 1238 / 1258 | 53.4% (661/1238) | unavailable (0/0) | unavailable (0/0) | 2.50–4.00 / 3.50–5.00 |
| ES / PIN075_09 | after_180m | 1228 / 1258 | 53.4% (661/1238) | 83.8% (1037/1238) | 96.9% (1200/1238) | 10.00–16.00 / 11.00–17.00 |
| ES / PIN075_09 | after_30m | 1238 / 1258 | 53.4% (661/1238) | unavailable (0/0) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| ES / PIN075_09 | after_60m | 1238 / 1258 | 53.4% (661/1238) | 83.8% (1037/1238) | unavailable (0/0) | 6.00–11.00 / 7.00–12.00 |
| ES / PIN075_09 | to_actual_cash_close | 1237 / 1258 | 53.4% (661/1238) | 83.8% (1037/1238) | 96.9% (1191/1229) | 10.00–17.50 / 11.00–18.50 |
| ES / PIN075_10 | after_15m | 1238 / 1258 | 62.5% (774/1238) | unavailable (0/0) | unavailable (0/0) | 3.00–3.50 / 4.00–4.50 |
| ES / PIN075_10 | after_180m | 1228 / 1258 | 62.5% (774/1238) | 92.0% (1139/1238) | 99.0% (1226/1238) | 8.00–10.50 / 9.00–11.50 |
| ES / PIN075_10 | after_30m | 1238 / 1258 | 62.5% (774/1238) | unavailable (0/0) | unavailable (0/0) | 5.00–7.00 / 6.00–8.00 |
| ES / PIN075_10 | after_60m | 1238 / 1258 | 62.5% (774/1238) | 92.0% (1139/1238) | unavailable (0/0) | 7.00–8.00 / 8.00–9.00 |
| ES / PIN075_10 | to_actual_cash_close | 1237 / 1258 | 62.5% (774/1238) | 92.0% (1139/1238) | 99.0% (1217/1229) | 8.50–11.00 / 9.50–12.00 |
| ES / PIN075_11 | after_15m | 1228 / 1258 | 45.8% (563/1228) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / PIN075_11 | after_180m | 0 / 1258 | 45.8% (563/1228) | 80.8% (992/1228) | 100.0% (1165/1165) | unavailable / unavailable |
| ES / PIN075_11 | after_30m | 1228 / 1258 | 45.8% (563/1228) | unavailable (0/0) | unavailable (0/0) | 5.00–8.00 / 6.00–9.00 |
| ES / PIN075_11 | after_60m | 1228 / 1258 | 45.8% (563/1228) | 80.8% (992/1228) | unavailable (0/0) | 8.00–14.00 / 9.00–15.00 |
| ES / PIN075_11 | to_actual_cash_close | 1228 / 1258 | 45.8% (563/1228) | 80.8% (992/1228) | unavailable (0/0) | 11.50–17.00 / 12.50–18.00 |
| ES / PIN075_12 | after_15m | 863 / 1258 | 38.0% (375/988) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / PIN075_12 | after_180m | 0 / 1258 | 38.0% (375/988) | 99.8% (453/454) | 100.0% (453/453) | unavailable / unavailable |
| ES / PIN075_12 | after_30m | 860 / 1258 | 38.0% (375/988) | unavailable (0/0) | unavailable (0/0) | 0.00–3.00 / 1.00–4.00 |
| ES / PIN075_12 | after_60m | 1 / 1258 | 38.0% (375/988) | 99.8% (453/454) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN075_12 | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN076_00_08 | after_15m | 1172 / 1258 | 99.3% (1200/1208) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN076_00_08 | after_180m | 1064 / 1258 | 99.3% (1200/1208) | 99.9% (1207/1208) | 100.0% (1208/1208) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN076_00_08 | after_30m | 1125 / 1258 | 99.3% (1200/1208) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN076_00_08 | after_60m | 1080 / 1258 | 99.3% (1200/1208) | 99.9% (1207/1208) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN076_00_08 | to_actual_cash_close | 1054 / 1258 | 99.3% (1200/1208) | 99.9% (1207/1208) | 100.0% (1208/1208) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN076_08_0930 | after_15m | 1250 / 1258 | 99.8% (1252/1254) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN076_08_0930 | after_180m | 1232 / 1258 | 99.8% (1252/1254) | 100.0% (1254/1254) | 100.0% (1254/1254) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN076_08_0930 | after_30m | 1249 / 1258 | 99.8% (1252/1254) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN076_08_0930 | after_60m | 1249 / 1258 | 99.8% (1252/1254) | 100.0% (1254/1254) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN076_08_0930 | to_actual_cash_close | 1232 / 1258 | 99.8% (1252/1254) | 100.0% (1254/1254) | 100.0% (1254/1254) | 0.00–0.00 / 1.00–1.00 |
| ES / PIN078_daily_not_combined | after_15m | 0 / 493 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN078_daily_not_combined | after_180m | 0 / 493 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN078_daily_not_combined | after_30m | 0 / 493 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN078_daily_not_combined | after_60m | 0 / 493 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PIN078_daily_not_combined | to_actual_cash_close | 0 / 493 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / PM | after_15m | 863 / 1258 | 32.1% (312/973) | unavailable (0/0) | unavailable (0/0) | 0.00–3.00 / 1.00–4.00 |
| ES / PM | after_180m | 0 / 1258 | 32.1% (312/973) | 99.7% (381/382) | 100.0% (381/381) | unavailable / unavailable |
| ES / PM | after_30m | 860 / 1258 | 32.1% (312/973) | unavailable (0/0) | unavailable (0/0) | 0.00–3.00 / 1.00–4.00 |
| ES / PM | after_60m | 1 / 1258 | 32.1% (312/973) | 99.7% (381/382) | unavailable (0/0) | unavailable / unavailable |
| ES / PM | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / RTH0930 | after_15m | 863 / 1258 | 20.8% (193/930) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / RTH0930 | after_180m | 0 / 1258 | 20.8% (193/930) | 99.6% (253/254) | 100.0% (253/253) | unavailable / unavailable |
| ES / RTH0930 | after_30m | 860 / 1258 | 20.8% (193/930) | unavailable (0/0) | unavailable (0/0) | 1.00–3.50 / 2.00–4.50 |
| ES / RTH0930 | after_60m | 1 / 1258 | 20.8% (193/930) | 99.6% (253/254) | unavailable (0/0) | unavailable / unavailable |
| ES / RTH0930 | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / RTH_actual | after_15m | 863 / 1258 | 20.8% (193/930) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / RTH_actual | after_180m | 0 / 1258 | 20.8% (193/930) | 99.6% (253/254) | 100.0% (253/253) | unavailable / unavailable |
| ES / RTH_actual | after_30m | 860 / 1258 | 20.8% (193/930) | unavailable (0/0) | unavailable (0/0) | 1.00–3.50 / 2.00–4.50 |
| ES / RTH_actual | after_60m | 1 / 1258 | 20.8% (193/930) | 99.6% (253/254) | unavailable (0/0) | unavailable / unavailable |
| ES / RTH_actual | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / custom09 | after_15m | 1232 / 1258 | 26.7% (329/1232) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / custom09 | after_180m | 1223 / 1258 | 26.7% (329/1232) | 49.6% (610/1230) | 78.1% (961/1230) | 30.00–46.00 / 31.00–47.00 |
| ES / custom09 | after_30m | 1232 / 1258 | 26.7% (329/1232) | unavailable (0/0) | unavailable (0/0) | 4.00–8.00 / 5.00–9.00 |
| ES / custom09 | after_60m | 1225 / 1258 | 26.7% (329/1232) | 49.6% (610/1230) | unavailable (0/0) | 8.00–15.00 / 9.00–16.00 |
| ES / custom09 | to_actual_cash_close | 1232 / 1258 | 26.7% (329/1232) | 49.3% (603/1223) | 78.0% (954/1223) | 34.00–66.00 / 35.00–67.00 |
| ES / day00 | after_15m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / day00 | after_180m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / day00 | after_30m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / day00 | after_60m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / day00 | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / futures08 | after_15m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / futures08 | after_180m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / futures08 | after_30m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / futures08 | after_60m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / futures08 | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| ES / lunch | after_15m | 1228 / 1258 | 57.6% (707/1228) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| ES / lunch | after_180m | 1228 / 1258 | 57.6% (707/1228) | 87.0% (1068/1228) | 98.7% (1212/1228) | 6.00–12.00 / 7.00–13.00 |
| ES / lunch | after_30m | 1228 / 1258 | 57.6% (707/1228) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / lunch | after_60m | 1228 / 1258 | 57.6% (707/1228) | 87.0% (1068/1228) | unavailable (0/0) | 5.00–8.00 / 6.00–9.00 |
| ES / lunch | to_actual_cash_close | 1228 / 1258 | 57.6% (707/1228) | 87.0% (1068/1228) | unavailable (0/0) | 6.00–12.00 / 7.00–13.00 |
| ES / magic_00 | after_15m | 1095 / 1258 | 59.9% (656/1096) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| ES / magic_00 | after_180m | 1079 / 1258 | 59.9% (656/1096) | 91.8% (1003/1092) | 99.8% (1090/1092) | 7.00–13.50 / 8.00–14.50 |
| ES / magic_00 | after_30m | 1085 / 1258 | 59.9% (656/1096) | unavailable (0/0) | unavailable (0/0) | 4.00–5.00 / 5.00–6.00 |
| ES / magic_00 | after_60m | 1080 / 1258 | 59.9% (656/1096) | 91.8% (1003/1092) | unavailable (0/0) | 6.00–11.00 / 7.00–12.00 |
| ES / magic_00 | to_actual_cash_close | 1069 / 1258 | 59.9% (656/1096) | 91.8% (1003/1092) | 99.8% (1090/1092) | 7.00–14.00 / 8.00–15.00 |
| ES / magic_01 | after_15m | 1186 / 1258 | 70.9% (841/1187) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| ES / magic_01 | after_180m | 1182 / 1258 | 70.9% (841/1187) | 94.2% (1118/1187) | 99.8% (1185/1187) | 4.00–5.00 / 5.00–6.00 |
| ES / magic_01 | after_30m | 1186 / 1258 | 70.9% (841/1187) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| ES / magic_01 | after_60m | 1183 / 1258 | 70.9% (841/1187) | 94.2% (1118/1187) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| ES / magic_01 | to_actual_cash_close | 1171 / 1258 | 70.9% (841/1187) | 94.2% (1118/1187) | 99.8% (1185/1187) | 4.00–5.00 / 5.00–6.00 |
| ES / magic_02 | after_15m | 1222 / 1258 | 75.7% (925/1222) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / magic_02 | after_180m | 1214 / 1258 | 75.7% (925/1222) | 95.0% (1160/1221) | 98.9% (1207/1221) | 3.00–6.00 / 4.00–7.00 |
| ES / magic_02 | after_30m | 1222 / 1258 | 75.7% (925/1222) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / magic_02 | after_60m | 1221 / 1258 | 75.7% (925/1222) | 95.0% (1160/1221) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / magic_02 | to_actual_cash_close | 1204 / 1258 | 75.7% (925/1222) | 95.0% (1160/1221) | 98.9% (1207/1221) | 3.00–6.00 / 4.00–7.00 |
| ES / magic_06 | after_15m | 1230 / 1258 | 57.7% (710/1230) | unavailable (0/0) | unavailable (0/0) | 1.00–5.00 / 2.00–6.00 |
| ES / magic_06 | after_180m | 1224 / 1258 | 57.7% (710/1230) | 88.0% (1082/1230) | 99.9% (1229/1230) | 8.00–13.00 / 9.00–14.00 |
| ES / magic_06 | after_30m | 1230 / 1258 | 57.7% (710/1230) | unavailable (0/0) | unavailable (0/0) | 3.00–7.00 / 4.00–8.00 |
| ES / magic_06 | after_60m | 1230 / 1258 | 57.7% (710/1230) | 88.0% (1082/1230) | unavailable (0/0) | 5.00–10.00 / 6.00–11.00 |
| ES / magic_06 | to_actual_cash_close | 1224 / 1258 | 57.7% (710/1230) | 88.0% (1082/1230) | 99.9% (1229/1230) | 8.00–13.00 / 9.00–14.00 |
| ES / magic_07 | after_15m | 1240 / 1258 | 54.9% (681/1240) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| ES / magic_07 | after_180m | 1231 / 1258 | 54.9% (681/1240) | 91.5% (1134/1239) | 99.8% (1237/1239) | 8.00–16.00 / 9.00–17.00 |
| ES / magic_07 | after_30m | 1238 / 1258 | 54.9% (681/1240) | unavailable (0/0) | unavailable (0/0) | 5.00–8.00 / 6.00–9.00 |
| ES / magic_07 | after_60m | 1238 / 1258 | 54.9% (681/1240) | 91.5% (1134/1239) | unavailable (0/0) | 8.00–13.00 / 9.00–14.00 |
| ES / magic_07 | to_actual_cash_close | 1231 / 1258 | 54.9% (681/1240) | 91.5% (1134/1239) | 99.8% (1237/1239) | 8.00–16.00 / 9.00–17.00 |
| ES / magic_08 | after_15m | 1249 / 1258 | 47.6% (594/1249) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| ES / magic_08 | after_180m | 1232 / 1258 | 47.6% (594/1249) | 95.6% (1192/1247) | 99.3% (1238/1247) | 14.00–19.00 / 15.00–20.00 |
| ES / magic_08 | after_30m | 1232 / 1258 | 47.6% (594/1249) | unavailable (0/0) | unavailable (0/0) | 6.00–9.00 / 7.00–10.00 |
| ES / magic_08 | after_60m | 1232 / 1258 | 47.6% (594/1249) | 95.6% (1192/1247) | unavailable (0/0) | 13.00–19.00 / 14.00–20.00 |
| ES / magic_08 | to_actual_cash_close | 1232 / 1258 | 47.6% (594/1249) | 95.6% (1192/1247) | 99.3% (1238/1247) | 14.00–19.00 / 15.00–20.00 |
| ES / magic_23 | after_15m | 1117 / 1258 | 45.0% (504/1120) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| ES / magic_23 | after_180m | 1030 / 1258 | 45.0% (504/1120) | 79.6% (864/1085) | 98.5% (1069/1085) | 13.00–24.00 / 14.00–25.00 |
| ES / magic_23 | after_30m | 1078 / 1258 | 45.0% (504/1120) | unavailable (0/0) | unavailable (0/0) | 5.00–7.00 / 6.00–8.00 |
| ES / magic_23 | after_60m | 1044 / 1258 | 45.0% (504/1120) | 79.6% (864/1085) | unavailable (0/0) | 9.00–12.00 / 10.00–13.00 |
| ES / magic_23 | to_actual_cash_close | 1021 / 1258 | 45.0% (504/1120) | 79.6% (864/1085) | 98.5% (1069/1085) | 14.00–26.00 / 15.00–27.00 |
| ES / prior_RTH_open_observed | after_15m | 1210 / 1258 | 55.9% (678/1212) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / prior_RTH_open_observed | after_180m | 1210 / 1258 | 55.9% (678/1212) | 69.1% (838/1212) | 80.9% (981/1212) | 0.00–1.00 / 1.00–2.00 |
| ES / prior_RTH_open_observed | after_30m | 1210 / 1258 | 55.9% (678/1212) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / prior_RTH_open_observed | after_60m | 1210 / 1258 | 55.9% (678/1212) | 69.1% (838/1212) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / prior_RTH_open_observed | to_actual_cash_close | 1209 / 1258 | 55.9% (678/1212) | 69.1% (838/1212) | 80.9% (981/1212) | 0.00–3.00 / 1.00–4.00 |
| ES / prior_RTH_preopen | after_15m | 1210 / 1258 | 57.2% (693/1212) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / prior_RTH_preopen | after_180m | 1210 / 1258 | 57.2% (693/1212) | 69.6% (844/1212) | 81.4% (986/1212) | 0.00–0.00 / 1.00–1.00 |
| ES / prior_RTH_preopen | after_30m | 1210 / 1258 | 57.2% (693/1212) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / prior_RTH_preopen | after_60m | 1210 / 1258 | 57.2% (693/1212) | 69.6% (844/1212) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| ES / prior_RTH_preopen | common_1001_to_actual_cash_close | 1212 / 1258 | 57.5% (697/1213) | 68.9% (836/1213) | 79.3% (955/1204) | 0.00–0.00 / 1.00–1.00 |
| ES / prior_RTH_preopen | prefix_15m_to_actual_cash_close | 1210 / 1258 | 55.1% (667/1211) | 68.6% (831/1211) | 80.6% (976/1211) | 0.00–2.50 / 1.00–3.50 |
| ES / prior_RTH_preopen | prefix_30m_to_actual_cash_close | 1212 / 1258 | 57.5% (698/1213) | 69.1% (838/1213) | 79.3% (962/1213) | 0.00–0.00 / 1.00–1.00 |
| ES / prior_RTH_preopen | prefix_60m_to_actual_cash_close | 1212 / 1258 | 57.2% (694/1213) | 68.0% (825/1213) | 78.4% (944/1204) | 0.00–0.00 / 1.00–1.00 |
| ES / prior_RTH_preopen | to_actual_cash_close | 1209 / 1258 | 57.2% (693/1212) | 69.6% (844/1212) | 81.4% (986/1212) | 0.00–4.00 / 1.00–5.00 |
| ES / turn_earlier | after_15m | 1235 / 1258 | 87.2% (1077/1235) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| ES / turn_earlier | after_180m | 1235 / 1258 | 87.2% (1077/1235) | 99.3% (1226/1235) | 99.8% (1232/1235) | 1.00–3.00 / 2.00–4.00 |
| ES / turn_earlier | after_30m | 1235 / 1258 | 87.2% (1077/1235) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / turn_earlier | after_60m | 1235 / 1258 | 87.2% (1077/1235) | 99.3% (1226/1235) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| ES / turn_earlier | common_1001_to_actual_cash_close | 1234 / 1258 | 92.0% (1136/1235) | 99.1% (1224/1235) | 99.8% (1223/1226) | 0.00–0.00 / 1.00–1.00 |
| ES / turn_earlier | to_actual_cash_close | 1234 / 1258 | 87.2% (1077/1235) | 99.3% (1226/1235) | 99.8% (1232/1235) | 1.00–3.00 / 2.00–4.00 |
| ES / turn_later | after_15m | 1238 / 1258 | 94.6% (1171/1238) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / turn_later | after_180m | 1230 / 1258 | 94.6% (1171/1238) | 99.6% (1233/1238) | 99.9% (1237/1238) | 0.00–1.00 / 1.00–2.00 |
| ES / turn_later | after_30m | 1238 / 1258 | 94.6% (1171/1238) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / turn_later | after_60m | 1238 / 1258 | 94.6% (1171/1238) | 99.6% (1233/1238) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| ES / turn_later | common_1001_to_actual_cash_close | 1237 / 1258 | 94.6% (1171/1238) | 99.6% (1233/1238) | 99.9% (1228/1229) | 0.00–1.00 / 1.00–2.00 |
| ES / turn_later | to_actual_cash_close | 1237 / 1258 | 94.6% (1171/1238) | 99.6% (1233/1238) | 99.9% (1228/1229) | 0.00–1.00 / 1.00–2.00 |
| ES / turn_source | after_15m | 1235 / 1258 | 93.0% (1148/1235) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| ES / turn_source | after_180m | 1235 / 1258 | 93.0% (1148/1235) | 99.8% (1232/1235) | 100.0% (1235/1235) | 1.50–2.00 / 2.50–3.00 |
| ES / turn_source | after_30m | 1235 / 1258 | 93.0% (1148/1235) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| ES / turn_source | after_60m | 1235 / 1258 | 93.0% (1148/1235) | 99.8% (1232/1235) | unavailable (0/0) | 1.50–2.00 / 2.50–3.00 |
| ES / turn_source | common_1001_to_actual_cash_close | 1234 / 1258 | 94.7% (1169/1235) | 99.8% (1232/1235) | 100.0% (1226/1226) | 0.00–0.00 / 1.00–1.00 |
| ES / turn_source | to_actual_cash_close | 1234 / 1258 | 93.0% (1148/1235) | 99.8% (1232/1235) | 100.0% (1235/1235) | 2.00–2.00 / 3.00–3.00 |
| NQ / AM | after_15m | 1212 / 1258 | 27.6% (335/1212) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| NQ / AM | after_180m | 1201 / 1258 | 27.6% (335/1212) | 48.1% (581/1207) | 74.2% (894/1205) | 21.00–33.00 / 22.00–34.00 |
| NQ / AM | after_30m | 1212 / 1258 | 27.6% (335/1212) | unavailable (0/0) | unavailable (0/0) | 3.00–7.00 / 4.00–8.00 |
| NQ / AM | after_60m | 1205 / 1258 | 27.6% (335/1212) | 48.1% (581/1207) | unavailable (0/0) | 5.00–11.00 / 6.00–12.00 |
| NQ / AM | to_actual_cash_close | 1209 / 1258 | 27.6% (335/1212) | 48.0% (578/1203) | 74.1% (891/1202) | 31.00–41.00 / 32.00–42.00 |
| NQ / Asia19 | after_15m | 1067 / 1258 | 28.9% (308/1067) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / Asia19 | after_180m | 1066 / 1258 | 28.9% (308/1067) | 52.3% (558/1066) | 83.9% (894/1066) | 29.00–44.00 / 30.00–45.00 |
| NQ / Asia19 | after_30m | 1067 / 1258 | 28.9% (308/1067) | unavailable (0/0) | unavailable (0/0) | 4.00–7.00 / 5.00–8.00 |
| NQ / Asia19 | after_60m | 1066 / 1258 | 28.9% (308/1067) | 52.3% (558/1066) | unavailable (0/0) | 9.00–16.00 / 10.00–17.00 |
| NQ / Asia19 | to_actual_cash_close | 1060 / 1258 | 28.9% (308/1067) | 52.3% (558/1066) | 83.9% (894/1066) | 39.00–66.50 / 40.00–67.50 |
| NQ / Asia20 | after_15m | 1097 / 1258 | 31.0% (340/1097) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / Asia20 | after_180m | 1096 / 1258 | 31.0% (340/1097) | 55.5% (608/1096) | 87.2% (956/1096) | 27.50–44.00 / 28.50–45.00 |
| NQ / Asia20 | after_30m | 1097 / 1258 | 31.0% (340/1097) | unavailable (0/0) | unavailable (0/0) | 4.00–8.00 / 5.00–9.00 |
| NQ / Asia20 | after_60m | 1096 / 1258 | 31.0% (340/1097) | 55.5% (608/1096) | unavailable (0/0) | 9.00–15.00 / 10.00–16.00 |
| NQ / Asia20 | prefix_15m_to_actual_cash_close | 1089 / 1258 | 33.3% (365/1097) | 64.8% (710/1096) | 86.5% (948/1096) | 29.00–52.00 / 30.00–53.00 |
| NQ / Asia20 | prefix_30m_to_actual_cash_close | 1089 / 1258 | 37.2% (408/1096) | 70.2% (769/1096) | 87.1% (955/1096) | 25.50–44.00 / 26.50–45.00 |
| NQ / Asia20 | prefix_60m_to_actual_cash_close | 1090 / 1258 | 57.3% (629/1097) | 76.0% (834/1097) | 88.4% (970/1097) | 1.00–20.00 / 2.00–21.00 |
| NQ / Asia20 | to_actual_cash_close | 1089 / 1258 | 31.0% (340/1097) | 55.5% (608/1096) | 87.2% (956/1096) | 32.50–62.00 / 33.50–63.00 |
| NQ / JTR_fixed_01 | after_15m | 1191 / 1258 | 64.7% (770/1191) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / JTR_fixed_01 | after_180m | 1151 / 1258 | 64.7% (770/1191) | 91.3% (1085/1189) | 98.5% (1171/1189) | 6.00–8.00 / 7.00–9.00 |
| NQ / JTR_fixed_01 | after_30m | 1188 / 1258 | 64.7% (770/1191) | unavailable (0/0) | unavailable (0/0) | 4.00–4.00 / 5.00–5.00 |
| NQ / JTR_fixed_01 | after_60m | 1181 / 1258 | 64.7% (770/1191) | 91.3% (1085/1189) | unavailable (0/0) | 5.00–7.00 / 6.00–8.00 |
| NQ / JTR_fixed_01 | to_actual_cash_close | 1089 / 1258 | 64.7% (770/1191) | 91.3% (1085/1189) | 98.5% (1171/1189) | 6.00–9.00 / 7.00–10.00 |
| NQ / JTR_fixed_02 | after_15m | 1156 / 1258 | 68.1% (791/1162) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / JTR_fixed_02 | after_180m | 1139 / 1258 | 68.1% (791/1162) | 97.2% (1128/1161) | 99.9% (1160/1161) | 5.00–6.00 / 6.00–7.00 |
| NQ / JTR_fixed_02 | after_30m | 1147 / 1258 | 68.1% (791/1162) | unavailable (0/0) | unavailable (0/0) | 2.50–4.50 / 3.50–5.50 |
| NQ / JTR_fixed_02 | after_60m | 1143 / 1258 | 68.1% (791/1162) | 97.2% (1128/1161) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| NQ / JTR_fixed_02 | to_actual_cash_close | 1132 / 1258 | 68.1% (791/1162) | 97.2% (1128/1161) | 99.9% (1160/1161) | 5.00–6.00 / 6.00–7.00 |
| NQ / JTR_fixed_03 | after_15m | 1214 / 1258 | 64.2% (780/1215) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / JTR_fixed_03 | after_180m | 1197 / 1258 | 64.2% (780/1215) | 91.0% (1105/1214) | 98.0% (1190/1214) | 5.00–8.00 / 6.00–9.00 |
| NQ / JTR_fixed_03 | after_30m | 1211 / 1258 | 64.2% (780/1215) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| NQ / JTR_fixed_03 | after_60m | 1206 / 1258 | 64.2% (780/1215) | 91.0% (1105/1214) | unavailable (0/0) | 4.00–7.00 / 5.00–8.00 |
| NQ / JTR_fixed_03 | to_actual_cash_close | 1188 / 1258 | 64.2% (780/1215) | 91.0% (1105/1214) | 98.0% (1190/1214) | 5.00–9.00 / 6.00–10.00 |
| NQ / JTR_fixed_04 | after_15m | 1193 / 1258 | 32.4% (387/1193) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / JTR_fixed_04 | after_180m | 1193 / 1258 | 32.4% (387/1193) | 94.8% (1131/1193) | 98.8% (1179/1193) | 28.00–29.00 / 29.00–30.00 |
| NQ / JTR_fixed_04 | after_30m | 1193 / 1258 | 32.4% (387/1193) | unavailable (0/0) | unavailable (0/0) | 9.00–13.00 / 10.00–14.00 |
| NQ / JTR_fixed_04 | after_60m | 1193 / 1258 | 32.4% (387/1193) | 94.8% (1131/1193) | unavailable (0/0) | 25.50–29.00 / 26.50–30.00 |
| NQ / JTR_fixed_04 | common_1001_to_actual_cash_close | 1192 / 1258 | 86.1% (1027/1193) | 95.5% (1139/1193) | 98.2% (1164/1185) | 0.00–0.00 / 1.00–1.00 |
| NQ / JTR_fixed_04 | prefix_15m_to_actual_cash_close | 1192 / 1258 | 54.3% (648/1193) | 96.3% (1149/1193) | 98.7% (1177/1193) | 14.00–15.00 / 15.00–16.00 |
| NQ / JTR_fixed_04 | prefix_30m_to_actual_cash_close | 1192 / 1258 | 87.4% (1043/1193) | 96.4% (1150/1193) | 98.7% (1178/1193) | 0.00–1.00 / 1.00–2.00 |
| NQ / JTR_fixed_04 | prefix_60m_to_actual_cash_close | 1192 / 1258 | 86.1% (1027/1193) | 95.5% (1139/1193) | 98.2% (1164/1185) | 0.00–0.00 / 1.00–1.00 |
| NQ / JTR_fixed_04 | to_actual_cash_close | 1192 / 1258 | 32.4% (387/1193) | 94.8% (1131/1193) | 98.8% (1179/1193) | 28.00–29.00 / 29.00–30.00 |
| NQ / JTR_fixed_04__shift_+10m | after_15m | 1194 / 1258 | 30.0% (358/1194) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| NQ / JTR_fixed_04__shift_+10m | after_180m | 1194 / 1258 | 30.0% (358/1194) | 95.4% (1139/1194) | 98.7% (1179/1194) | 19.00–20.00 / 20.00–21.00 |
| NQ / JTR_fixed_04__shift_+10m | after_30m | 1194 / 1258 | 30.0% (358/1194) | unavailable (0/0) | unavailable (0/0) | 18.00–19.00 / 19.00–20.00 |
| NQ / JTR_fixed_04__shift_+10m | after_60m | 1194 / 1258 | 30.0% (358/1194) | 95.4% (1139/1194) | unavailable (0/0) | 19.00–20.00 / 20.00–21.00 |
| NQ / JTR_fixed_04__shift_+10m | common_1001_to_actual_cash_close | 1193 / 1258 | 85.8% (1025/1194) | 95.3% (1138/1194) | 98.2% (1165/1186) | 0.00–0.00 / 1.00–1.00 |
| NQ / JTR_fixed_04__shift_+10m | to_actual_cash_close | 1193 / 1258 | 30.0% (358/1194) | 95.4% (1139/1194) | 98.7% (1179/1194) | 19.00–20.00 / 20.00–21.00 |
| NQ / JTR_fixed_04__shift_-10m | after_15m | 1193 / 1258 | 35.1% (419/1193) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| NQ / JTR_fixed_04__shift_-10m | after_180m | 1193 / 1258 | 35.1% (419/1193) | 93.7% (1118/1193) | 99.1% (1182/1193) | 27.00–37.00 / 28.00–38.00 |
| NQ / JTR_fixed_04__shift_-10m | after_30m | 1193 / 1258 | 35.1% (419/1193) | unavailable (0/0) | unavailable (0/0) | 3.00–9.00 / 4.00–10.00 |
| NQ / JTR_fixed_04__shift_-10m | after_60m | 1193 / 1258 | 35.1% (419/1193) | 93.7% (1118/1193) | unavailable (0/0) | 23.50–36.00 / 24.50–37.00 |
| NQ / JTR_fixed_04__shift_-10m | common_1001_to_actual_cash_close | 1192 / 1258 | 86.8% (1036/1193) | 95.6% (1141/1193) | 98.6% (1168/1185) | 0.00–0.00 / 1.00–1.00 |
| NQ / JTR_fixed_04__shift_-10m | to_actual_cash_close | 1192 / 1258 | 35.1% (419/1193) | 93.7% (1118/1193) | 99.1% (1182/1193) | 28.00–37.00 / 29.00–38.00 |
| NQ / JTR_fixed_05 | after_15m | 1212 / 1258 | 69.7% (845/1212) | unavailable (0/0) | unavailable (0/0) | 0.00–2.00 / 1.00–3.00 |
| NQ / JTR_fixed_05 | after_180m | 1205 / 1258 | 69.7% (845/1212) | 92.7% (1123/1212) | 97.9% (1187/1212) | 3.50–7.00 / 4.50–8.00 |
| NQ / JTR_fixed_05 | after_30m | 1212 / 1258 | 69.7% (845/1212) | unavailable (0/0) | unavailable (0/0) | 1.00–4.00 / 2.00–5.00 |
| NQ / JTR_fixed_05 | after_60m | 1212 / 1258 | 69.7% (845/1212) | 92.7% (1123/1212) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| NQ / JTR_fixed_05 | to_actual_cash_close | 1209 / 1258 | 69.7% (845/1212) | 92.7% (1123/1212) | 97.9% (1179/1204) | 4.00–8.00 / 5.00–9.00 |
| NQ / JTR_fixed_06 | after_15m | 1215 / 1258 | 69.1% (839/1215) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / JTR_fixed_06 | after_180m | 1206 / 1258 | 69.1% (839/1215) | 92.2% (1120/1215) | 98.4% (1196/1215) | 4.00–6.00 / 5.00–7.00 |
| NQ / JTR_fixed_06 | after_30m | 1215 / 1258 | 69.1% (839/1215) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / JTR_fixed_06 | after_60m | 1215 / 1258 | 69.1% (839/1215) | 92.2% (1120/1215) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| NQ / JTR_fixed_06 | to_actual_cash_close | 1212 / 1258 | 69.1% (839/1215) | 92.2% (1120/1215) | 98.4% (1188/1207) | 5.00–6.00 / 6.00–7.00 |
| NQ / JTR_fixed_07 | after_15m | 1215 / 1258 | 70.0% (851/1215) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| NQ / JTR_fixed_07 | after_180m | 1204 / 1258 | 70.0% (851/1215) | 96.4% (1170/1214) | 99.8% (1211/1214) | 5.00–8.00 / 6.00–9.00 |
| NQ / JTR_fixed_07 | after_30m | 1208 / 1258 | 70.0% (851/1215) | unavailable (0/0) | unavailable (0/0) | 3.00–4.50 / 4.00–5.50 |
| NQ / JTR_fixed_07 | after_60m | 1206 / 1258 | 70.0% (851/1215) | 96.4% (1170/1214) | unavailable (0/0) | 4.00–7.00 / 5.00–8.00 |
| NQ / JTR_fixed_07 | to_actual_cash_close | 1212 / 1258 | 70.0% (851/1215) | 96.4% (1163/1207) | 99.8% (1204/1207) | 5.00–8.00 / 6.00–9.00 |
| NQ / JTR_fixed_08 | after_15m | 1207 / 1258 | 73.6% (888/1207) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| NQ / JTR_fixed_08 | after_180m | 0 / 1258 | 73.6% (888/1207) | 97.3% (1155/1187) | 100.0% (1155/1155) | unavailable / unavailable |
| NQ / JTR_fixed_08 | after_30m | 1207 / 1258 | 73.6% (888/1207) | unavailable (0/0) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| NQ / JTR_fixed_08 | after_60m | 830 / 1258 | 73.6% (888/1207) | 97.3% (1155/1187) | unavailable (0/0) | 2.00–7.00 / 3.00–8.00 |
| NQ / JTR_fixed_08 | to_actual_cash_close | 1207 / 1258 | 73.6% (888/1207) | unavailable (0/0) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| NQ / JTR_fixed_EST_sensitivity_01 | after_15m | 1205 / 1258 | 72.0% (869/1207) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / JTR_fixed_EST_sensitivity_01 | after_180m | 1143 / 1258 | 72.0% (869/1207) | 92.2% (1110/1204) | 98.5% (1184/1202) | 4.00–5.00 / 5.00–6.00 |
| NQ / JTR_fixed_EST_sensitivity_01 | after_30m | 1201 / 1258 | 72.0% (869/1207) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / JTR_fixed_EST_sensitivity_01 | after_60m | 1199 / 1258 | 72.0% (869/1207) | 92.2% (1110/1204) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| NQ / JTR_fixed_EST_sensitivity_01 | to_actual_cash_close | 1102 / 1258 | 72.0% (869/1207) | 92.2% (1110/1204) | 98.5% (1184/1202) | 4.00–5.00 / 5.00–6.00 |
| NQ / JTR_fixed_EST_sensitivity_02 | after_15m | 1185 / 1258 | 68.4% (813/1189) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| NQ / JTR_fixed_EST_sensitivity_02 | after_180m | 1173 / 1258 | 68.4% (813/1189) | 97.2% (1153/1186) | 99.9% (1185/1186) | 3.00–8.00 / 4.00–9.00 |
| NQ / JTR_fixed_EST_sensitivity_02 | after_30m | 1182 / 1258 | 68.4% (813/1189) | unavailable (0/0) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| NQ / JTR_fixed_EST_sensitivity_02 | after_60m | 1177 / 1258 | 68.4% (813/1189) | 97.2% (1153/1186) | unavailable (0/0) | 3.00–7.00 / 4.00–8.00 |
| NQ / JTR_fixed_EST_sensitivity_02 | to_actual_cash_close | 1164 / 1258 | 68.4% (813/1189) | 97.2% (1153/1186) | 99.9% (1185/1186) | 3.00–8.00 / 4.00–9.00 |
| NQ / JTR_fixed_EST_sensitivity_03 | after_15m | 1211 / 1258 | 62.5% (758/1212) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / JTR_fixed_EST_sensitivity_03 | after_180m | 1195 / 1258 | 62.5% (758/1212) | 89.8% (1088/1211) | 98.3% (1191/1211) | 6.00–11.00 / 7.00–12.00 |
| NQ / JTR_fixed_EST_sensitivity_03 | after_30m | 1207 / 1258 | 62.5% (758/1212) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| NQ / JTR_fixed_EST_sensitivity_03 | after_60m | 1204 / 1258 | 62.5% (758/1212) | 89.8% (1088/1211) | unavailable (0/0) | 5.00–7.00 / 6.00–8.00 |
| NQ / JTR_fixed_EST_sensitivity_03 | to_actual_cash_close | 1189 / 1258 | 62.5% (758/1212) | 89.8% (1088/1211) | 98.3% (1191/1211) | 7.00–11.00 / 8.00–12.00 |
| NQ / JTR_fixed_EST_sensitivity_04 | after_15m | 1201 / 1258 | 51.3% (616/1201) | unavailable (0/0) | unavailable (0/0) | 0.00–3.00 / 1.00–4.00 |
| NQ / JTR_fixed_EST_sensitivity_04 | after_180m | 1201 / 1258 | 51.3% (616/1201) | 88.3% (1060/1201) | 95.1% (1142/1201) | 9.00–15.00 / 10.00–16.00 |
| NQ / JTR_fixed_EST_sensitivity_04 | after_30m | 1201 / 1258 | 51.3% (616/1201) | unavailable (0/0) | unavailable (0/0) | 2.50–7.00 / 3.50–8.00 |
| NQ / JTR_fixed_EST_sensitivity_04 | after_60m | 1201 / 1258 | 51.3% (616/1201) | 88.3% (1060/1201) | unavailable (0/0) | 8.00–12.00 / 9.00–13.00 |
| NQ / JTR_fixed_EST_sensitivity_04 | to_actual_cash_close | 1199 / 1258 | 51.3% (616/1201) | 88.3% (1060/1201) | 95.1% (1140/1199) | 11.00–16.00 / 12.00–17.00 |
| NQ / JTR_fixed_EST_sensitivity_05 | after_15m | 1215 / 1258 | 71.6% (870/1215) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| NQ / JTR_fixed_EST_sensitivity_05 | after_180m | 1206 / 1258 | 71.6% (870/1215) | 93.8% (1140/1215) | 98.8% (1201/1215) | 4.00–6.00 / 5.00–7.00 |
| NQ / JTR_fixed_EST_sensitivity_05 | after_30m | 1215 / 1258 | 71.6% (870/1215) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / JTR_fixed_EST_sensitivity_05 | after_60m | 1215 / 1258 | 71.6% (870/1215) | 93.8% (1140/1215) | unavailable (0/0) | 4.00–5.00 / 5.00–6.00 |
| NQ / JTR_fixed_EST_sensitivity_05 | to_actual_cash_close | 1212 / 1258 | 71.6% (870/1215) | 93.8% (1140/1215) | 98.8% (1193/1207) | 4.00–7.00 / 5.00–8.00 |
| NQ / JTR_fixed_EST_sensitivity_06 | after_15m | 1215 / 1258 | 71.4% (868/1215) | unavailable (0/0) | unavailable (0/0) | 0.00–3.00 / 1.00–4.00 |
| NQ / JTR_fixed_EST_sensitivity_06 | after_180m | 1206 / 1258 | 71.4% (868/1215) | 94.4% (1147/1215) | 99.1% (1204/1215) | 5.00–7.00 / 6.00–8.00 |
| NQ / JTR_fixed_EST_sensitivity_06 | after_30m | 1215 / 1258 | 71.4% (868/1215) | unavailable (0/0) | unavailable (0/0) | 2.00–5.00 / 3.00–6.00 |
| NQ / JTR_fixed_EST_sensitivity_06 | after_60m | 1215 / 1258 | 71.4% (868/1215) | 94.4% (1147/1215) | unavailable (0/0) | 4.00–7.00 / 5.00–8.00 |
| NQ / JTR_fixed_EST_sensitivity_06 | to_actual_cash_close | 1212 / 1258 | 71.4% (868/1215) | 94.4% (1147/1215) | 99.1% (1196/1207) | 5.00–7.00 / 6.00–8.00 |
| NQ / JTR_fixed_EST_sensitivity_07 | after_15m | 1212 / 1258 | 72.4% (878/1212) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / JTR_fixed_EST_sensitivity_07 | after_180m | 964 / 1258 | 72.4% (878/1212) | 96.7% (1171/1211) | 99.7% (1207/1211) | 3.00–8.50 / 4.00–9.50 |
| NQ / JTR_fixed_EST_sensitivity_07 | after_30m | 1206 / 1258 | 72.4% (878/1212) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / JTR_fixed_EST_sensitivity_07 | after_60m | 1206 / 1258 | 72.4% (878/1212) | 96.7% (1171/1211) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| NQ / JTR_fixed_EST_sensitivity_07 | to_actual_cash_close | 1210 / 1258 | 72.4% (878/1212) | 96.7% (1166/1206) | 100.0% (397/397) | 3.00–6.00 / 4.00–7.00 |
| NQ / JTR_fixed_EST_sensitivity_08 | after_15m | 960 / 1258 | 52.4% (504/961) | unavailable (0/0) | unavailable (0/0) | 0.50–4.00 / 1.50–5.00 |
| NQ / JTR_fixed_EST_sensitivity_08 | after_180m | 0 / 1258 | 52.4% (504/961) | 98.1% (655/668) | 100.0% (655/655) | unavailable / unavailable |
| NQ / JTR_fixed_EST_sensitivity_08 | after_30m | 397 / 1258 | 52.4% (504/961) | unavailable (0/0) | unavailable (0/0) | 1.00–7.00 / 2.00–8.00 |
| NQ / JTR_fixed_EST_sensitivity_08 | after_60m | 263 / 1258 | 52.4% (504/961) | 98.1% (655/668) | unavailable (0/0) | 2.00–8.00 / 3.00–9.00 |
| NQ / JTR_fixed_EST_sensitivity_08 | to_actual_cash_close | 397 / 1258 | 74.1% (294/397) | unavailable (0/0) | unavailable (0/0) | 1.00–7.00 / 2.00–8.00 |
| NQ / London02 | after_15m | 1188 / 1258 | 23.7% (281/1188) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| NQ / London02 | after_180m | 1186 / 1258 | 23.7% (281/1188) | 58.3% (692/1187) | 97.1% (1153/1187) | 29.00–59.00 / 30.00–60.00 |
| NQ / London02 | after_30m | 1187 / 1258 | 23.7% (281/1188) | unavailable (0/0) | unavailable (0/0) | 8.00–15.50 / 9.00–16.50 |
| NQ / London02 | after_60m | 1186 / 1258 | 23.7% (281/1188) | 58.3% (692/1187) | unavailable (0/0) | 16.00–28.00 / 17.00–29.00 |
| NQ / London02 | to_actual_cash_close | 1185 / 1258 | 23.7% (281/1188) | 58.3% (692/1187) | 97.1% (1153/1187) | 29.00–63.50 / 30.00–64.50 |
| NQ / NY08 | after_15m | 837 / 1258 | 24.5% (225/919) | unavailable (0/0) | unavailable (0/0) | 0.00–1.50 / 1.00–2.50 |
| NQ / NY08 | after_180m | 0 / 1258 | 24.5% (225/919) | 100.0% (269/269) | 100.0% (269/269) | unavailable / unavailable |
| NQ / NY08 | after_30m | 827 / 1258 | 24.5% (225/919) | unavailable (0/0) | unavailable (0/0) | 2.00–2.00 / 3.00–3.00 |
| NQ / NY08 | after_60m | 0 / 1258 | 24.5% (225/919) | 100.0% (269/269) | unavailable (0/0) | unavailable / unavailable |
| NQ / NY08 | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / ONS03 | after_15m | 1194 / 1258 | 24.0% (287/1194) | unavailable (0/0) | unavailable (0/0) | 2.00–5.00 / 3.00–6.00 |
| NQ / ONS03 | after_180m | 1189 / 1258 | 24.0% (287/1194) | 49.9% (596/1194) | 96.3% (1148/1192) | 44.00–63.00 / 45.00–64.00 |
| NQ / ONS03 | after_30m | 1194 / 1258 | 24.0% (287/1194) | unavailable (0/0) | unavailable (0/0) | 5.00–10.50 / 6.00–11.50 |
| NQ / ONS03 | after_60m | 1192 / 1258 | 24.0% (287/1194) | 49.9% (596/1194) | unavailable (0/0) | 12.00–22.00 / 13.00–23.00 |
| NQ / ONS03 | to_actual_cash_close | 1188 / 1258 | 24.0% (287/1194) | 49.9% (596/1194) | 96.3% (1148/1192) | 44.00–66.50 / 45.00–67.50 |
| NQ / ONS20 | after_15m | 1127 / 1258 | 14.7% (166/1127) | unavailable (0/0) | unavailable (0/0) | 3.00–4.50 / 4.00–5.50 |
| NQ / ONS20 | after_180m | 1096 / 1258 | 14.7% (166/1127) | 35.5% (393/1106) | 77.9% (858/1101) | 50.00–82.00 / 51.00–83.00 |
| NQ / ONS20 | after_30m | 1117 / 1258 | 14.7% (166/1127) | unavailable (0/0) | unavailable (0/0) | 6.50–11.00 / 7.50–12.00 |
| NQ / ONS20 | after_60m | 1103 / 1258 | 14.7% (166/1127) | 35.5% (393/1106) | unavailable (0/0) | 14.00–25.00 / 15.00–26.00 |
| NQ / ONS20 | to_actual_cash_close | 1089 / 1258 | 14.7% (166/1127) | 35.5% (393/1106) | 77.9% (858/1101) | 71.50–104.00 / 72.50–105.00 |
| NQ / OR15 | after_15m | 1212 / 1258 | 82.9% (1005/1212) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / OR15 | after_180m | 1212 / 1258 | 82.9% (1005/1212) | 98.6% (1195/1212) | 99.8% (1209/1212) | 2.00–4.00 / 3.00–5.00 |
| NQ / OR15 | after_30m | 1212 / 1258 | 82.9% (1005/1212) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / OR15 | after_60m | 1212 / 1258 | 82.9% (1005/1212) | 98.6% (1195/1212) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / OR15 | common_1001_to_actual_cash_close | 1209 / 1258 | 86.3% (1046/1212) | 97.4% (1181/1212) | 99.7% (1200/1204) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR15 | prefix_15m_to_actual_cash_close | 1209 / 1258 | 86.3% (1046/1212) | 97.4% (1181/1212) | 99.7% (1200/1204) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR15 | prefix_30m_to_actual_cash_close | 1209 / 1258 | 87.0% (1055/1212) | 96.5% (1170/1212) | 99.3% (1196/1204) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR15 | prefix_60m_to_actual_cash_close | 1209 / 1258 | 84.5% (1024/1212) | 95.9% (1162/1212) | 98.9% (1191/1204) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR15 | to_actual_cash_close | 1209 / 1258 | 82.9% (1005/1212) | 98.6% (1195/1212) | 99.8% (1209/1212) | 2.00–4.00 / 3.00–5.00 |
| NQ / OR15__shift_+10m | after_15m | 1212 / 1258 | 87.0% (1054/1212) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / OR15__shift_+10m | after_180m | 1212 / 1258 | 87.0% (1054/1212) | 98.9% (1199/1212) | 99.7% (1208/1212) | 3.00–4.00 / 4.00–5.00 |
| NQ / OR15__shift_+10m | after_30m | 1212 / 1258 | 87.0% (1054/1212) | unavailable (0/0) | unavailable (0/0) | 2.00–3.50 / 3.00–4.50 |
| NQ / OR15__shift_+10m | after_60m | 1212 / 1258 | 87.0% (1054/1212) | 98.9% (1199/1212) | unavailable (0/0) | 2.50–4.00 / 3.50–5.00 |
| NQ / OR15__shift_+10m | common_1001_to_actual_cash_close | 1209 / 1258 | 87.7% (1063/1212) | 98.8% (1198/1212) | 99.7% (1200/1204) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR15__shift_+10m | to_actual_cash_close | 1209 / 1258 | 87.0% (1054/1212) | 98.9% (1199/1212) | 99.7% (1208/1212) | 3.00–4.00 / 4.00–5.00 |
| NQ / OR15__shift_-10m | after_15m | 1210 / 1258 | 96.5% (1168/1210) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR15__shift_-10m | after_180m | 1210 / 1258 | 96.5% (1168/1210) | 99.9% (1209/1210) | 99.9% (1209/1210) | 0.00–1.00 / 1.00–2.00 |
| NQ / OR15__shift_-10m | after_30m | 1210 / 1258 | 96.5% (1168/1210) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / OR15__shift_-10m | after_60m | 1210 / 1258 | 96.5% (1168/1210) | 99.9% (1209/1210) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / OR15__shift_-10m | common_1001_to_actual_cash_close | 1208 / 1258 | 96.4% (1166/1210) | 99.6% (1205/1210) | 100.0% (1202/1202) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR15__shift_-10m | to_actual_cash_close | 1208 / 1258 | 96.5% (1168/1210) | 99.9% (1209/1210) | 99.9% (1209/1210) | 0.00–1.00 / 1.00–2.00 |
| NQ / OR5 | after_15m | 1212 / 1258 | 97.2% (1179/1213) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5 | after_180m | 1212 / 1258 | 97.2% (1179/1213) | 99.9% (1212/1213) | 99.9% (1212/1213) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5 | after_30m | 1212 / 1258 | 97.2% (1179/1213) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5 | after_60m | 1212 / 1258 | 97.2% (1179/1213) | 99.9% (1212/1213) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5 | common_1001_to_actual_cash_close | 1210 / 1258 | 97.2% (1179/1213) | 99.8% (1210/1213) | 100.0% (1205/1205) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5 | to_actual_cash_close | 1209 / 1258 | 97.2% (1179/1213) | 99.9% (1212/1213) | 99.9% (1212/1213) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_+10m | after_15m | 1212 / 1258 | 98.8% (1197/1212) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_+10m | after_180m | 1212 / 1258 | 98.8% (1197/1212) | 99.9% (1211/1212) | 100.0% (1212/1212) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_+10m | after_30m | 1212 / 1258 | 98.8% (1197/1212) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_+10m | after_60m | 1212 / 1258 | 98.8% (1197/1212) | 99.9% (1211/1212) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_+10m | common_1001_to_actual_cash_close | 1209 / 1258 | 98.8% (1197/1212) | 99.9% (1211/1212) | 100.0% (1204/1204) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_+10m | to_actual_cash_close | 1209 / 1258 | 98.8% (1197/1212) | 99.9% (1211/1212) | 100.0% (1212/1212) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_-10m | after_15m | 1210 / 1258 | 100.0% (1226/1226) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_-10m | after_180m | 1210 / 1258 | 100.0% (1226/1226) | 100.0% (1226/1226) | 100.0% (1226/1226) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_-10m | after_30m | 1210 / 1258 | 100.0% (1226/1226) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_-10m | after_60m | 1210 / 1258 | 100.0% (1226/1226) | 100.0% (1226/1226) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_-10m | common_1001_to_actual_cash_close | 1208 / 1258 | 100.0% (1210/1210) | 100.0% (1210/1210) | 100.0% (1202/1202) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR5__shift_-10m | to_actual_cash_close | 1208 / 1258 | 100.0% (1226/1226) | 100.0% (1226/1226) | 100.0% (1226/1226) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR_activity_1_1 | after_15m | 1141 / 1258 | 83.5% (953/1141) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / OR_activity_1_1 | after_180m | 1138 / 1258 | 83.5% (953/1141) | 98.9% (1128/1141) | 99.6% (1137/1141) | 2.00–3.00 / 3.00–4.00 |
| NQ / OR_activity_1_1 | after_30m | 1141 / 1258 | 83.5% (953/1141) | unavailable (0/0) | unavailable (0/0) | 2.00–2.00 / 3.00–3.00 |
| NQ / OR_activity_1_1 | after_60m | 1141 / 1258 | 83.5% (953/1141) | 98.9% (1128/1141) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / OR_activity_1_1 | common_1001_to_actual_cash_close | 1097 / 1258 | 86.0% (943/1097) | 97.4% (1068/1097) | 99.6% (1088/1092) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR_activity_1_1 | to_actual_cash_close | 1141 / 1258 | 83.5% (953/1141) | 98.9% (1128/1141) | 99.6% (1134/1138) | 2.00–3.00 / 3.00–4.00 |
| NQ / OR_activity_1_2 | after_15m | 1169 / 1258 | 92.7% (1084/1169) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / OR_activity_1_2 | after_180m | 1169 / 1258 | 92.7% (1084/1169) | 99.5% (1163/1169) | 99.8% (1167/1169) | 0.00–1.00 / 1.00–2.00 |
| NQ / OR_activity_1_2 | after_30m | 1169 / 1258 | 92.7% (1084/1169) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / OR_activity_1_2 | after_60m | 1169 / 1258 | 92.7% (1084/1169) | 99.5% (1163/1169) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / OR_activity_1_2 | common_1001_to_actual_cash_close | 1146 / 1258 | 95.2% (1091/1146) | 99.4% (1139/1146) | 100.0% (1138/1138) | 0.00–0.00 / 1.00–1.00 |
| NQ / OR_activity_1_2 | to_actual_cash_close | 1169 / 1258 | 92.7% (1084/1169) | 99.5% (1163/1169) | 99.8% (1167/1169) | 0.00–1.00 / 1.00–2.00 |
| NQ / OR_activity_3_2 | after_15m | 1113 / 1258 | 73.1% (814/1113) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / OR_activity_3_2 | after_180m | 1108 / 1258 | 73.1% (814/1113) | 94.5% (1052/1113) | 98.7% (1098/1113) | 4.00–5.00 / 5.00–6.00 |
| NQ / OR_activity_3_2 | after_30m | 1113 / 1258 | 73.1% (814/1113) | unavailable (0/0) | unavailable (0/0) | 2.50–4.00 / 3.50–5.00 |
| NQ / OR_activity_3_2 | after_60m | 1113 / 1258 | 73.1% (814/1113) | 94.5% (1052/1113) | unavailable (0/0) | 4.00–4.00 / 5.00–5.00 |
| NQ / OR_activity_3_2 | common_1001_to_actual_cash_close | 870 / 1258 | 76.0% (661/870) | 94.0% (818/870) | 98.5% (855/868) | 1.00–3.00 / 2.00–4.00 |
| NQ / OR_activity_3_2 | to_actual_cash_close | 1113 / 1258 | 73.1% (814/1113) | 94.5% (1052/1113) | 98.6% (1092/1107) | 4.00–5.00 / 5.00–6.00 |
| NQ / PIN015_Asia_UTC | after_15m | 1092 / 1258 | 34.9% (381/1092) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / PIN015_Asia_UTC | after_180m | 1090 / 1258 | 34.9% (381/1092) | 58.8% (641/1091) | 81.5% (889/1091) | 20.00–30.00 / 21.00–31.00 |
| NQ / PIN015_Asia_UTC | after_30m | 1092 / 1258 | 34.9% (381/1092) | unavailable (0/0) | unavailable (0/0) | 5.00–6.00 / 6.00–7.00 |
| NQ / PIN015_Asia_UTC | after_60m | 1091 / 1258 | 34.9% (381/1092) | 58.8% (641/1091) | unavailable (0/0) | 9.00–12.00 / 10.00–13.00 |
| NQ / PIN015_Asia_UTC | to_actual_cash_close | 1084 / 1258 | 34.9% (381/1092) | 58.8% (641/1091) | 81.5% (889/1091) | 25.00–64.50 / 26.00–65.50 |
| NQ / PIN015_London_UTC | after_15m | 1190 / 1258 | 23.9% (285/1190) | unavailable (0/0) | unavailable (0/0) | 2.00–5.00 / 3.00–6.00 |
| NQ / PIN015_London_UTC | after_180m | 1188 / 1258 | 23.9% (285/1190) | 71.5% (850/1189) | 96.6% (1148/1189) | 43.00–47.00 / 44.00–48.00 |
| NQ / PIN015_London_UTC | after_30m | 1190 / 1258 | 23.9% (285/1190) | unavailable (0/0) | unavailable (0/0) | 7.00–9.00 / 8.00–10.00 |
| NQ / PIN015_London_UTC | after_60m | 1188 / 1258 | 23.9% (285/1190) | 71.5% (850/1189) | unavailable (0/0) | 23.50–42.00 / 24.50–43.00 |
| NQ / PIN015_London_UTC | to_actual_cash_close | 1187 / 1258 | 23.9% (285/1190) | 71.5% (850/1189) | 96.6% (1148/1189) | 43.50–48.00 / 44.50–49.00 |
| NQ / PIN015_NY_UTC | after_15m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN015_NY_UTC | after_180m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN015_NY_UTC | after_30m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN015_NY_UTC | after_60m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN015_NY_UTC | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN073_1 | after_15m | 1201 / 1258 | 60.8% (731/1202) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / PIN073_1 | after_180m | 1197 / 1258 | 60.8% (731/1202) | 97.8% (1176/1202) | 99.9% (1201/1202) | 7.00–12.00 / 8.00–13.00 |
| NQ / PIN073_1 | after_30m | 1201 / 1258 | 60.8% (731/1202) | unavailable (0/0) | unavailable (0/0) | 4.00–6.50 / 5.00–7.50 |
| NQ / PIN073_1 | after_60m | 1201 / 1258 | 60.8% (731/1202) | 97.8% (1176/1202) | unavailable (0/0) | 7.00–11.00 / 8.00–12.00 |
| NQ / PIN073_1 | to_actual_cash_close | 1185 / 1258 | 60.8% (731/1202) | 97.8% (1176/1202) | 99.9% (1201/1202) | 7.00–12.00 / 8.00–13.00 |
| NQ / PIN073_2 | after_15m | 1210 / 1258 | 99.7% (1206/1210) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN073_2 | after_180m | 1210 / 1258 | 99.7% (1206/1210) | 100.0% (1210/1210) | 100.0% (1210/1210) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN073_2 | after_30m | 1210 / 1258 | 99.7% (1206/1210) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN073_2 | after_60m | 1210 / 1258 | 99.7% (1206/1210) | 100.0% (1210/1210) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN073_2 | to_actual_cash_close | 1208 / 1258 | 99.7% (1206/1210) | 100.0% (1210/1210) | 100.0% (1210/1210) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN073_3 | after_15m | 1156 / 1258 | 68.1% (791/1162) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / PIN073_3 | after_180m | 1139 / 1258 | 68.1% (791/1162) | 97.2% (1128/1161) | 99.9% (1160/1161) | 5.00–6.00 / 6.00–7.00 |
| NQ / PIN073_3 | after_30m | 1147 / 1258 | 68.1% (791/1162) | unavailable (0/0) | unavailable (0/0) | 2.50–4.50 / 3.50–5.50 |
| NQ / PIN073_3 | after_60m | 1143 / 1258 | 68.1% (791/1162) | 97.2% (1128/1161) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| NQ / PIN073_3 | to_actual_cash_close | 1132 / 1258 | 68.1% (791/1162) | 97.2% (1128/1161) | 99.9% (1160/1161) | 5.00–6.00 / 6.00–7.00 |
| NQ / PIN073_4 | after_15m | 1215 / 1258 | 74.0% (899/1215) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| NQ / PIN073_4 | after_180m | 1206 / 1258 | 74.0% (899/1215) | 95.3% (1158/1215) | 99.3% (1207/1215) | 4.00–6.00 / 5.00–7.00 |
| NQ / PIN073_4 | after_30m | 1215 / 1258 | 74.0% (899/1215) | unavailable (0/0) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| NQ / PIN073_4 | after_60m | 1215 / 1258 | 74.0% (899/1215) | 95.3% (1158/1215) | unavailable (0/0) | 4.00–5.00 / 5.00–6.00 |
| NQ / PIN073_4 | to_actual_cash_close | 1212 / 1258 | 74.0% (899/1215) | 95.3% (1158/1215) | 99.3% (1199/1207) | 4.00–6.00 / 5.00–7.00 |
| NQ / PIN073_5 | after_15m | 1206 / 1258 | 72.7% (878/1207) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / PIN073_5 | after_180m | 0 / 1258 | 72.7% (878/1207) | 96.0% (1158/1206) | 100.0% (1187/1187) | unavailable / unavailable |
| NQ / PIN073_5 | after_30m | 1205 / 1258 | 72.7% (878/1207) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / PIN073_5 | after_60m | 1205 / 1258 | 72.7% (878/1207) | 96.0% (1158/1206) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| NQ / PIN073_5 | to_actual_cash_close | 1205 / 1258 | 72.7% (878/1207) | 96.0% (1158/1206) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| NQ / PIN074_ref_00 | after_15m | 1188 / 1258 | 99.5% (1209/1215) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_00 | after_180m | 1139 / 1258 | 99.5% (1209/1215) | 100.0% (1215/1215) | 100.0% (1215/1215) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_00 | after_30m | 1166 / 1258 | 99.5% (1209/1215) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_00 | after_60m | 1147 / 1258 | 99.5% (1209/1215) | 100.0% (1215/1215) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_00 | to_actual_cash_close | 1132 / 1258 | 99.5% (1209/1215) | 100.0% (1215/1215) | 100.0% (1215/1215) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_01 | after_15m | 1205 / 1258 | 99.7% (1210/1214) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_01 | after_180m | 1182 / 1258 | 99.7% (1210/1214) | 99.9% (1213/1214) | 100.0% (1214/1214) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_01 | after_30m | 1197 / 1258 | 99.7% (1210/1214) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_01 | after_60m | 1186 / 1258 | 99.7% (1210/1214) | 99.9% (1213/1214) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_01 | to_actual_cash_close | 1172 / 1258 | 99.7% (1210/1214) | 99.9% (1213/1214) | 100.0% (1214/1214) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_03 | after_15m | 1219 / 1258 | 99.8% (1223/1225) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_03 | after_180m | 1200 / 1258 | 99.8% (1223/1225) | 100.0% (1225/1225) | 100.0% (1225/1225) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_03 | after_30m | 1217 / 1258 | 99.8% (1223/1225) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_03 | after_60m | 1211 / 1258 | 99.8% (1223/1225) | 100.0% (1225/1225) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_03 | to_actual_cash_close | 1188 / 1258 | 99.8% (1223/1225) | 100.0% (1225/1225) | 100.0% (1225/1225) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_04 | after_15m | 1214 / 1258 | 99.9% (1220/1221) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_04 | after_180m | 1196 / 1258 | 99.9% (1220/1221) | 100.0% (1221/1221) | 100.0% (1221/1221) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_04 | after_30m | 1213 / 1258 | 99.9% (1220/1221) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_04 | after_60m | 1207 / 1258 | 99.9% (1220/1221) | 100.0% (1221/1221) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_04 | to_actual_cash_close | 1189 / 1258 | 99.9% (1220/1221) | 100.0% (1221/1221) | 100.0% (1221/1221) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_07 | after_15m | 1209 / 1258 | 99.8% (1217/1220) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_07 | after_180m | 1200 / 1258 | 99.8% (1217/1220) | 100.0% (1220/1220) | 100.0% (1220/1220) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_07 | after_30m | 1206 / 1258 | 99.8% (1217/1220) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_07 | after_60m | 1203 / 1258 | 99.8% (1217/1220) | 100.0% (1220/1220) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN074_ref_07 | to_actual_cash_close | 1198 / 1258 | 99.8% (1217/1220) | 100.0% (1220/1220) | 100.0% (1220/1220) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN075_01 | after_15m | 1136 / 1258 | 42.0% (477/1137) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / PIN075_01 | after_180m | 1114 / 1258 | 42.0% (477/1137) | 77.4% (873/1128) | 94.8% (1067/1126) | 16.00–21.00 / 17.00–22.00 |
| NQ / PIN075_01 | after_30m | 1128 / 1258 | 42.0% (477/1137) | unavailable (0/0) | unavailable (0/0) | 6.00–7.00 / 7.00–8.00 |
| NQ / PIN075_01 | after_60m | 1120 / 1258 | 42.0% (477/1137) | 77.4% (873/1128) | unavailable (0/0) | 10.00–14.00 / 11.00–15.00 |
| NQ / PIN075_01 | to_actual_cash_close | 1043 / 1258 | 42.0% (477/1137) | 77.4% (873/1128) | 94.8% (1067/1126) | 18.00–23.00 / 19.00–24.00 |
| NQ / PIN075_02 | after_15m | 1125 / 1258 | 14.7% (165/1125) | unavailable (0/0) | unavailable (0/0) | 2.00–5.00 / 3.00–6.00 |
| NQ / PIN075_02 | after_180m | 1072 / 1258 | 14.7% (165/1125) | 32.1% (357/1112) | 68.2% (741/1087) | 35.50–76.50 / 36.50–77.50 |
| NQ / PIN075_02 | after_30m | 1121 / 1258 | 14.7% (165/1125) | unavailable (0/0) | unavailable (0/0) | 6.00–13.00 / 7.00–14.00 |
| NQ / PIN075_02 | after_60m | 1110 / 1258 | 14.7% (165/1125) | 32.1% (357/1112) | unavailable (0/0) | 13.00–19.00 / 14.00–20.00 |
| NQ / PIN075_02 | to_actual_cash_close | 1065 / 1258 | 14.7% (165/1125) | 32.1% (357/1112) | 68.2% (741/1087) | 105.50–131.50 / 106.50–132.50 |
| NQ / PIN075_03 | after_15m | 1115 / 1258 | 52.7% (588/1115) | unavailable (0/0) | unavailable (0/0) | 1.00–4.00 / 2.00–5.00 |
| NQ / PIN075_03 | after_180m | 1114 / 1258 | 52.7% (588/1115) | 79.9% (891/1115) | 94.3% (1052/1115) | 9.00–18.00 / 10.00–19.00 |
| NQ / PIN075_03 | after_30m | 1115 / 1258 | 52.7% (588/1115) | unavailable (0/0) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| NQ / PIN075_03 | after_60m | 1115 / 1258 | 52.7% (588/1115) | 79.9% (891/1115) | unavailable (0/0) | 5.00–10.00 / 6.00–11.00 |
| NQ / PIN075_03 | to_actual_cash_close | 1108 / 1258 | 52.7% (588/1115) | 79.9% (891/1115) | 94.3% (1052/1115) | 9.00–22.00 / 10.00–23.00 |
| NQ / PIN075_04 | after_15m | 1211 / 1258 | 49.1% (595/1212) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / PIN075_04 | after_180m | 1197 / 1258 | 49.1% (595/1212) | 84.1% (1019/1211) | 95.8% (1160/1211) | 9.00–15.00 / 10.00–16.00 |
| NQ / PIN075_04 | after_30m | 1206 / 1258 | 49.1% (595/1212) | unavailable (0/0) | unavailable (0/0) | 6.00–8.00 / 7.00–9.00 |
| NQ / PIN075_04 | after_60m | 1205 / 1258 | 49.1% (595/1212) | 84.1% (1019/1211) | unavailable (0/0) | 8.00–11.00 / 9.00–12.00 |
| NQ / PIN075_04 | to_actual_cash_close | 1188 / 1258 | 49.1% (595/1212) | 84.1% (1019/1211) | 95.8% (1160/1211) | 11.00–16.00 / 12.00–17.00 |
| NQ / PIN075_05 | after_15m | 1202 / 1258 | 34.7% (417/1203) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| NQ / PIN075_05 | after_180m | 1191 / 1258 | 34.7% (417/1203) | 65.8% (790/1200) | 91.8% (1101/1199) | 23.50–33.00 / 24.50–34.00 |
| NQ / PIN075_05 | after_30m | 1200 / 1258 | 34.7% (417/1203) | unavailable (0/0) | unavailable (0/0) | 4.00–9.00 / 5.00–10.00 |
| NQ / PIN075_05 | after_60m | 1198 / 1258 | 34.7% (417/1203) | 65.8% (790/1200) | unavailable (0/0) | 9.00–16.00 / 10.00–17.00 |
| NQ / PIN075_05 | to_actual_cash_close | 1188 / 1258 | 34.7% (417/1203) | 65.8% (790/1200) | 91.8% (1101/1199) | 29.00–38.50 / 30.00–39.50 |
| NQ / PIN075_06 | after_15m | 1199 / 1258 | 43.6% (523/1199) | unavailable (0/0) | unavailable (0/0) | 2.00–5.00 / 3.00–6.00 |
| NQ / PIN075_06 | after_180m | 1192 / 1258 | 43.6% (523/1199) | 85.6% (1025/1198) | 99.6% (1192/1197) | 16.00–20.00 / 17.00–21.00 |
| NQ / PIN075_06 | after_30m | 1198 / 1258 | 43.6% (523/1199) | unavailable (0/0) | unavailable (0/0) | 7.00–10.00 / 8.00–11.00 |
| NQ / PIN075_06 | after_60m | 1195 / 1258 | 43.6% (523/1199) | 85.6% (1025/1198) | unavailable (0/0) | 13.00–15.00 / 14.00–16.00 |
| NQ / PIN075_06 | to_actual_cash_close | 1191 / 1258 | 43.6% (523/1199) | 85.6% (1025/1198) | 99.6% (1192/1197) | 16.00–20.50 / 17.00–21.50 |
| NQ / PIN075_07 | after_15m | 1198 / 1258 | 85.8% (1028/1198) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / PIN075_07 | after_180m | 1198 / 1258 | 85.8% (1028/1198) | 95.9% (1149/1198) | 98.5% (1180/1198) | 1.00–1.00 / 2.00–2.00 |
| NQ / PIN075_07 | after_30m | 1198 / 1258 | 85.8% (1028/1198) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / PIN075_07 | after_60m | 1198 / 1258 | 85.8% (1028/1198) | 95.9% (1149/1198) | unavailable (0/0) | 1.00–1.00 / 2.00–2.00 |
| NQ / PIN075_07 | to_actual_cash_close | 1196 / 1258 | 85.8% (1028/1198) | 95.9% (1149/1198) | 98.5% (1180/1198) | 1.00–1.00 / 2.00–2.00 |
| NQ / PIN075_08 | after_15m | 1215 / 1258 | 73.7% (896/1215) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / PIN075_08 | after_180m | 1206 / 1258 | 73.7% (896/1215) | 94.7% (1150/1215) | 99.0% (1203/1215) | 3.50–7.00 / 4.50–8.00 |
| NQ / PIN075_08 | after_30m | 1215 / 1258 | 73.7% (896/1215) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| NQ / PIN075_08 | after_60m | 1215 / 1258 | 73.7% (896/1215) | 94.7% (1150/1215) | unavailable (0/0) | 3.00–6.50 / 4.00–7.50 |
| NQ / PIN075_08 | to_actual_cash_close | 1212 / 1258 | 73.7% (896/1215) | 94.7% (1150/1215) | 99.0% (1195/1207) | 3.50–7.00 / 4.50–8.00 |
| NQ / PIN075_09 | after_15m | 1215 / 1258 | 53.3% (647/1215) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / PIN075_09 | after_180m | 1206 / 1258 | 53.3% (647/1215) | 83.5% (1015/1215) | 95.6% (1162/1215) | 8.00–15.00 / 9.00–16.00 |
| NQ / PIN075_09 | after_30m | 1215 / 1258 | 53.3% (647/1215) | unavailable (0/0) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| NQ / PIN075_09 | after_60m | 1215 / 1258 | 53.3% (647/1215) | 83.5% (1015/1215) | unavailable (0/0) | 5.50–11.00 / 6.50–12.00 |
| NQ / PIN075_09 | to_actual_cash_close | 1212 / 1258 | 53.3% (647/1215) | 83.5% (1015/1215) | 95.6% (1154/1207) | 8.00–17.00 / 9.00–18.00 |
| NQ / PIN075_10 | after_15m | 1215 / 1258 | 65.3% (794/1215) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / PIN075_10 | after_180m | 1205 / 1258 | 65.3% (794/1215) | 91.4% (1111/1215) | 99.3% (1205/1214) | 7.00–9.00 / 8.00–10.00 |
| NQ / PIN075_10 | after_30m | 1215 / 1258 | 65.3% (794/1215) | unavailable (0/0) | unavailable (0/0) | 5.00–5.00 / 6.00–6.00 |
| NQ / PIN075_10 | after_60m | 1215 / 1258 | 65.3% (794/1215) | 91.4% (1111/1215) | unavailable (0/0) | 5.50–7.00 / 6.50–8.00 |
| NQ / PIN075_10 | to_actual_cash_close | 1212 / 1258 | 65.3% (794/1215) | 91.4% (1111/1215) | 99.3% (1198/1207) | 6.50–9.00 / 7.50–10.00 |
| NQ / PIN075_11 | after_15m | 1206 / 1258 | 46.3% (558/1206) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / PIN075_11 | after_180m | 0 / 1258 | 46.3% (558/1206) | 79.8% (961/1205) | 100.0% (1123/1123) | unavailable / unavailable |
| NQ / PIN075_11 | after_30m | 1205 / 1258 | 46.3% (558/1206) | unavailable (0/0) | unavailable (0/0) | 3.00–8.00 / 4.00–9.00 |
| NQ / PIN075_11 | after_60m | 1204 / 1258 | 46.3% (558/1206) | 79.8% (961/1205) | unavailable (0/0) | 7.50–12.00 / 8.50–13.00 |
| NQ / PIN075_11 | to_actual_cash_close | 1204 / 1258 | 46.3% (558/1206) | 79.8% (961/1205) | unavailable (0/0) | 12.00–17.00 / 13.00–18.00 |
| NQ / PIN075_12 | after_15m | 840 / 1258 | 43.8% (432/987) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / PIN075_12 | after_180m | 0 / 1258 | 43.8% (432/987) | 100.0% (498/498) | 100.0% (498/498) | unavailable / unavailable |
| NQ / PIN075_12 | after_30m | 830 / 1258 | 43.8% (432/987) | unavailable (0/0) | unavailable (0/0) | 1.00–1.50 / 2.00–2.50 |
| NQ / PIN075_12 | after_60m | 0 / 1258 | 43.8% (432/987) | 100.0% (498/498) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN075_12 | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN076_00_08 | after_15m | 1188 / 1258 | 99.5% (1209/1215) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN076_00_08 | after_180m | 1139 / 1258 | 99.5% (1209/1215) | 100.0% (1215/1215) | 100.0% (1215/1215) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN076_00_08 | after_30m | 1166 / 1258 | 99.5% (1209/1215) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN076_00_08 | after_60m | 1147 / 1258 | 99.5% (1209/1215) | 100.0% (1215/1215) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN076_00_08 | to_actual_cash_close | 1132 / 1258 | 99.5% (1209/1215) | 100.0% (1215/1215) | 100.0% (1215/1215) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN076_08_0930 | after_15m | 1212 / 1258 | 100.0% (1223/1223) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN076_08_0930 | after_180m | 1207 / 1258 | 100.0% (1223/1223) | 100.0% (1223/1223) | 100.0% (1223/1223) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN076_08_0930 | after_30m | 1208 / 1258 | 100.0% (1223/1223) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN076_08_0930 | after_60m | 1208 / 1258 | 100.0% (1223/1223) | 100.0% (1223/1223) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN076_08_0930 | to_actual_cash_close | 1205 / 1258 | 100.0% (1223/1223) | 100.0% (1223/1223) | 100.0% (1223/1223) | 0.00–0.00 / 1.00–1.00 |
| NQ / PIN078_daily_not_combined | after_15m | 0 / 493 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN078_daily_not_combined | after_180m | 0 / 493 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN078_daily_not_combined | after_30m | 0 / 493 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN078_daily_not_combined | after_60m | 0 / 493 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PIN078_daily_not_combined | to_actual_cash_close | 0 / 493 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / PM | after_15m | 840 / 1258 | 37.6% (363/965) | unavailable (0/0) | unavailable (0/0) | 0.00–1.50 / 1.00–2.50 |
| NQ / PM | after_180m | 0 / 1258 | 37.6% (363/965) | 100.0% (417/417) | 100.0% (417/417) | unavailable / unavailable |
| NQ / PM | after_30m | 830 / 1258 | 37.6% (363/965) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / PM | after_60m | 0 / 1258 | 37.6% (363/965) | 100.0% (417/417) | unavailable (0/0) | unavailable / unavailable |
| NQ / PM | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / RTH0930 | after_15m | 840 / 1258 | 24.8% (229/924) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / RTH0930 | after_180m | 0 / 1258 | 24.8% (229/924) | 100.0% (273/273) | 100.0% (273/273) | unavailable / unavailable |
| NQ / RTH0930 | after_30m | 830 / 1258 | 24.8% (229/924) | unavailable (0/0) | unavailable (0/0) | 2.00–2.00 / 3.00–3.00 |
| NQ / RTH0930 | after_60m | 0 / 1258 | 24.8% (229/924) | 100.0% (273/273) | unavailable (0/0) | unavailable / unavailable |
| NQ / RTH0930 | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / RTH_actual | after_15m | 840 / 1258 | 24.9% (230/925) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / RTH_actual | after_180m | 0 / 1258 | 24.9% (230/925) | 100.0% (274/274) | 100.0% (274/274) | unavailable / unavailable |
| NQ / RTH_actual | after_30m | 830 / 1258 | 24.9% (230/925) | unavailable (0/0) | unavailable (0/0) | 2.00–2.00 / 3.00–3.00 |
| NQ / RTH_actual | after_60m | 0 / 1258 | 24.9% (230/925) | 100.0% (274/274) | unavailable (0/0) | unavailable / unavailable |
| NQ / RTH_actual | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / custom09 | after_15m | 1210 / 1258 | 27.5% (333/1210) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| NQ / custom09 | after_180m | 1200 / 1258 | 27.5% (333/1210) | 47.3% (571/1206) | 73.3% (882/1204) | 21.00–33.00 / 22.00–34.00 |
| NQ / custom09 | after_30m | 1210 / 1258 | 27.5% (333/1210) | unavailable (0/0) | unavailable (0/0) | 3.00–7.50 / 4.00–8.50 |
| NQ / custom09 | after_60m | 1204 / 1258 | 27.5% (333/1210) | 47.3% (571/1206) | unavailable (0/0) | 6.00–13.00 / 7.00–14.00 |
| NQ / custom09 | to_actual_cash_close | 1208 / 1258 | 27.5% (333/1210) | 47.3% (568/1202) | 73.2% (879/1201) | 31.00–40.00 / 32.00–41.00 |
| NQ / day00 | after_15m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / day00 | after_180m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / day00 | after_30m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / day00 | after_60m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / day00 | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / futures08 | after_15m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / futures08 | after_180m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / futures08 | after_30m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / futures08 | after_60m | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / futures08 | to_actual_cash_close | 0 / 1258 | unavailable (0/0) | unavailable (0/0) | unavailable (0/0) | unavailable / unavailable |
| NQ / lunch | after_15m | 1206 / 1258 | 57.6% (695/1207) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / lunch | after_180m | 1204 / 1258 | 57.6% (695/1207) | 87.4% (1055/1207) | 98.5% (1189/1207) | 5.00–12.00 / 6.00–13.00 |
| NQ / lunch | after_30m | 1206 / 1258 | 57.6% (695/1207) | unavailable (0/0) | unavailable (0/0) | 2.00–6.00 / 3.00–7.00 |
| NQ / lunch | after_60m | 1206 / 1258 | 57.6% (695/1207) | 87.4% (1055/1207) | unavailable (0/0) | 3.00–9.00 / 4.00–10.00 |
| NQ / lunch | to_actual_cash_close | 1204 / 1258 | 57.5% (694/1206) | 87.4% (1054/1206) | unavailable (0/0) | 5.00–12.00 / 6.00–13.00 |
| NQ / magic_00 | after_15m | 1147 / 1258 | 63.7% (731/1147) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / magic_00 | after_180m | 1139 / 1258 | 63.7% (731/1147) | 92.4% (1057/1144) | 99.7% (1141/1144) | 6.00–8.50 / 7.00–9.50 |
| NQ / magic_00 | after_30m | 1143 / 1258 | 63.7% (731/1147) | unavailable (0/0) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| NQ / magic_00 | after_60m | 1140 / 1258 | 63.7% (731/1147) | 92.4% (1057/1144) | unavailable (0/0) | 5.00–7.00 / 6.00–8.00 |
| NQ / magic_00 | to_actual_cash_close | 1132 / 1258 | 63.7% (731/1147) | 92.4% (1057/1144) | 99.7% (1141/1144) | 6.00–9.00 / 7.00–10.00 |
| NQ / magic_01 | after_15m | 1185 / 1258 | 71.4% (846/1185) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / magic_01 | after_180m | 1181 / 1258 | 71.4% (846/1185) | 93.8% (1111/1184) | 99.8% (1182/1184) | 3.00–6.00 / 4.00–7.00 |
| NQ / magic_01 | after_30m | 1184 / 1258 | 71.4% (846/1185) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / magic_01 | after_60m | 1182 / 1258 | 71.4% (846/1185) | 93.8% (1111/1184) | unavailable (0/0) | 3.00–4.00 / 4.00–5.00 |
| NQ / magic_01 | to_actual_cash_close | 1172 / 1258 | 71.4% (846/1185) | 93.8% (1111/1184) | 99.8% (1182/1184) | 3.00–6.00 / 4.00–7.00 |
| NQ / magic_02 | after_15m | 1201 / 1258 | 73.9% (887/1201) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| NQ / magic_02 | after_180m | 1195 / 1258 | 73.9% (887/1201) | 93.4% (1122/1201) | 98.9% (1188/1201) | 3.00–5.50 / 4.00–6.50 |
| NQ / magic_02 | after_30m | 1201 / 1258 | 73.9% (887/1201) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / magic_02 | after_60m | 1201 / 1258 | 73.9% (887/1201) | 93.4% (1122/1201) | unavailable (0/0) | 3.00–5.00 / 4.00–6.00 |
| NQ / magic_02 | to_actual_cash_close | 1185 / 1258 | 73.9% (887/1201) | 93.4% (1122/1201) | 98.9% (1188/1201) | 3.00–5.00 / 4.00–6.00 |
| NQ / magic_06 | after_15m | 1198 / 1258 | 63.1% (756/1199) | unavailable (0/0) | unavailable (0/0) | 1.00–3.50 / 2.00–4.50 |
| NQ / magic_06 | after_180m | 1193 / 1258 | 63.1% (756/1199) | 88.5% (1061/1199) | 100.0% (1198/1198) | 6.00–10.00 / 7.00–11.00 |
| NQ / magic_06 | after_30m | 1198 / 1258 | 63.1% (756/1199) | unavailable (0/0) | unavailable (0/0) | 2.50–5.00 / 3.50–6.00 |
| NQ / magic_06 | after_60m | 1196 / 1258 | 63.1% (756/1199) | 88.5% (1061/1199) | unavailable (0/0) | 4.00–7.00 / 5.00–8.00 |
| NQ / magic_06 | to_actual_cash_close | 1192 / 1258 | 63.1% (756/1199) | 88.5% (1061/1199) | 100.0% (1198/1198) | 6.00–10.00 / 7.00–11.00 |
| NQ / magic_07 | after_15m | 1203 / 1258 | 57.3% (689/1203) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / magic_07 | after_180m | 1201 / 1258 | 57.3% (689/1203) | 91.5% (1100/1202) | 100.0% (1202/1202) | 9.00–12.00 / 10.00–13.00 |
| NQ / magic_07 | after_30m | 1202 / 1258 | 57.3% (689/1203) | unavailable (0/0) | unavailable (0/0) | 4.00–6.00 / 5.00–7.00 |
| NQ / magic_07 | after_60m | 1201 / 1258 | 57.3% (689/1203) | 91.5% (1100/1202) | unavailable (0/0) | 7.00–9.00 / 8.00–10.00 |
| NQ / magic_07 | to_actual_cash_close | 1199 / 1258 | 57.3% (689/1203) | 91.5% (1100/1202) | 100.0% (1202/1202) | 9.00–12.00 / 10.00–13.00 |
| NQ / magic_08 | after_15m | 1207 / 1258 | 47.0% (567/1207) | unavailable (0/0) | unavailable (0/0) | 2.00–3.00 / 3.00–4.00 |
| NQ / magic_08 | after_180m | 1207 / 1258 | 47.0% (567/1207) | 97.3% (1174/1207) | 99.3% (1198/1207) | 14.00–20.00 / 15.00–21.00 |
| NQ / magic_08 | after_30m | 1207 / 1258 | 47.0% (567/1207) | unavailable (0/0) | unavailable (0/0) | 8.00–10.00 / 9.00–11.00 |
| NQ / magic_08 | after_60m | 1207 / 1258 | 47.0% (567/1207) | 97.3% (1174/1207) | unavailable (0/0) | 14.00–19.00 / 15.00–20.00 |
| NQ / magic_08 | to_actual_cash_close | 1205 / 1258 | 47.0% (567/1207) | 97.3% (1174/1207) | 99.3% (1198/1207) | 14.50–20.00 / 15.50–21.00 |
| NQ / magic_23 | after_15m | 1153 / 1258 | 47.5% (548/1153) | unavailable (0/0) | unavailable (0/0) | 2.00–4.00 / 3.00–5.00 |
| NQ / magic_23 | after_180m | 1115 / 1258 | 47.5% (548/1153) | 81.0% (923/1140) | 98.7% (1123/1138) | 12.50–19.50 / 13.50–20.50 |
| NQ / magic_23 | after_30m | 1139 / 1258 | 47.5% (548/1153) | unavailable (0/0) | unavailable (0/0) | 5.00–7.00 / 6.00–8.00 |
| NQ / magic_23 | after_60m | 1123 / 1258 | 47.5% (548/1153) | 81.0% (923/1140) | unavailable (0/0) | 8.00–13.00 / 9.00–14.00 |
| NQ / magic_23 | to_actual_cash_close | 1108 / 1258 | 47.5% (548/1153) | 81.0% (923/1140) | 98.7% (1123/1138) | 12.50–21.00 / 13.50–22.00 |
| NQ / prior_RTH_open_observed | after_15m | 1187 / 1258 | 59.0% (701/1189) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / prior_RTH_open_observed | after_180m | 1187 / 1258 | 59.0% (701/1189) | 72.8% (866/1189) | 82.6% (982/1189) | 0.00–3.00 / 1.00–4.00 |
| NQ / prior_RTH_open_observed | after_30m | 1187 / 1258 | 59.0% (701/1189) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / prior_RTH_open_observed | after_60m | 1187 / 1258 | 59.0% (701/1189) | 72.8% (866/1189) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / prior_RTH_open_observed | to_actual_cash_close | 1185 / 1258 | 59.0% (701/1189) | 72.8% (866/1189) | 82.6% (982/1189) | 0.00–4.00 / 1.00–5.00 |
| NQ / prior_RTH_preopen | after_15m | 1187 / 1258 | 59.3% (705/1189) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / prior_RTH_preopen | after_180m | 1187 / 1258 | 59.3% (705/1189) | 73.1% (869/1189) | 82.7% (983/1189) | 0.00–0.00 / 1.00–1.00 |
| NQ / prior_RTH_preopen | after_30m | 1187 / 1258 | 59.3% (705/1189) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / prior_RTH_preopen | after_60m | 1187 / 1258 | 59.3% (705/1189) | 73.1% (869/1189) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / prior_RTH_preopen | common_1001_to_actual_cash_close | 1188 / 1258 | 57.8% (688/1190) | 70.0% (833/1190) | 79.8% (943/1181) | 0.00–0.00 / 1.00–1.00 |
| NQ / prior_RTH_preopen | prefix_15m_to_actual_cash_close | 1186 / 1258 | 57.4% (682/1188) | 70.6% (839/1188) | 81.1% (963/1188) | 0.00–1.00 / 1.00–2.00 |
| NQ / prior_RTH_preopen | prefix_30m_to_actual_cash_close | 1188 / 1258 | 58.4% (695/1190) | 70.1% (834/1190) | 80.0% (951/1189) | 0.00–0.00 / 1.00–1.00 |
| NQ / prior_RTH_preopen | prefix_60m_to_actual_cash_close | 1188 / 1258 | 57.9% (689/1190) | 68.5% (815/1190) | 77.9% (920/1181) | 0.00–0.00 / 1.00–1.00 |
| NQ / prior_RTH_preopen | to_actual_cash_close | 1185 / 1258 | 59.3% (705/1189) | 73.1% (869/1189) | 82.7% (983/1189) | 0.00–3.00 / 1.00–4.00 |
| NQ / turn_earlier | after_15m | 1212 / 1258 | 88.0% (1067/1212) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / turn_earlier | after_180m | 1212 / 1258 | 88.0% (1067/1212) | 99.3% (1204/1212) | 99.8% (1210/1212) | 1.00–4.00 / 2.00–5.00 |
| NQ / turn_earlier | after_30m | 1212 / 1258 | 88.0% (1067/1212) | unavailable (0/0) | unavailable (0/0) | 1.00–3.00 / 2.00–4.00 |
| NQ / turn_earlier | after_60m | 1212 / 1258 | 88.0% (1067/1212) | 99.3% (1204/1212) | unavailable (0/0) | 1.00–4.00 / 2.00–5.00 |
| NQ / turn_earlier | common_1001_to_actual_cash_close | 1209 / 1258 | 91.8% (1113/1212) | 98.8% (1198/1212) | 99.9% (1203/1204) | 0.00–0.00 / 1.00–1.00 |
| NQ / turn_earlier | to_actual_cash_close | 1209 / 1258 | 88.0% (1067/1212) | 99.3% (1204/1212) | 99.8% (1210/1212) | 1.00–4.00 / 2.00–5.00 |
| NQ / turn_later | after_15m | 1215 / 1258 | 94.7% (1151/1215) | unavailable (0/0) | unavailable (0/0) | 0.00–0.00 / 1.00–1.00 |
| NQ / turn_later | after_180m | 1208 / 1258 | 94.7% (1151/1215) | 99.8% (1212/1215) | 99.9% (1214/1215) | 0.00–1.00 / 1.00–2.00 |
| NQ / turn_later | after_30m | 1215 / 1258 | 94.7% (1151/1215) | unavailable (0/0) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / turn_later | after_60m | 1215 / 1258 | 94.7% (1151/1215) | 99.8% (1212/1215) | unavailable (0/0) | 0.00–1.00 / 1.00–2.00 |
| NQ / turn_later | common_1001_to_actual_cash_close | 1212 / 1258 | 94.7% (1151/1215) | 99.8% (1212/1215) | 99.9% (1206/1207) | 0.00–1.00 / 1.00–2.00 |
| NQ / turn_later | to_actual_cash_close | 1212 / 1258 | 94.7% (1151/1215) | 99.8% (1212/1215) | 99.9% (1206/1207) | 0.00–1.00 / 1.00–2.00 |
| NQ / turn_source | after_15m | 1212 / 1258 | 93.0% (1127/1212) | unavailable (0/0) | unavailable (0/0) | 1.00–1.00 / 2.00–2.00 |
| NQ / turn_source | after_180m | 1212 / 1258 | 93.0% (1127/1212) | 99.8% (1209/1212) | 99.9% (1211/1212) | 1.00–2.00 / 2.00–3.00 |
| NQ / turn_source | after_30m | 1212 / 1258 | 93.0% (1127/1212) | unavailable (0/0) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / turn_source | after_60m | 1212 / 1258 | 93.0% (1127/1212) | 99.8% (1209/1212) | unavailable (0/0) | 1.00–2.00 / 2.00–3.00 |
| NQ / turn_source | common_1001_to_actual_cash_close | 1209 / 1258 | 93.6% (1134/1212) | 99.3% (1204/1212) | 99.8% (1201/1204) | 0.00–0.00 / 1.00–1.00 |
| NQ / turn_source | to_actual_cash_close | 1209 / 1258 | 93.0% (1127/1212) | 99.8% (1209/1212) | 99.9% (1211/1212) | 1.00–2.00 / 2.00–3.00 |

## How large are the subsequent excursions and terminal moves?

Excursions and terminal displacement are in units of the specific formation width W. Each cell is the minimum–maximum across separately computed annual quantiles, not a pooled quantile or confidence interval. The terminal columns preserve negative as well as positive moves. Observed complete-horizon distributions condition on available truth; the preceding population counts expose the excluded and unresolved dates. Changing W or the forecast origin changes the quantity, so these marginal distributions cannot select the best timing.

| Instrument / clock | Horizon | Annual median up / down excursion, W | Annual 95th-percentile up / down excursion, W | Annual terminal 5th / median / 95th percentiles, W |
|---|---|---|---|---|
| ES / AM | after_15m | 0.09–0.10 / 0.08–0.11 | 0.27–0.31 / 0.30–0.37 | -0.32–-0.25 / -0.03–0.03 / 0.24–0.26 |
| ES / AM | after_180m | 0.30–0.39 / 0.26–0.37 | 0.92–1.32 / 1.15–1.50 | -1.11–-0.86 / -0.01–0.15 / 0.75–1.05 |
| ES / AM | after_30m | 0.11–0.15 / 0.11–0.15 | 0.36–0.43 / 0.47–0.56 | -0.44–-0.30 / -0.03–0.04 / 0.30–0.35 |
| ES / AM | after_60m | 0.16–0.21 / 0.16–0.21 | 0.52–0.67 / 0.64–0.81 | -0.64–-0.47 / -0.02–0.05 / 0.42–0.53 |
| ES / AM | to_actual_cash_close | 0.40–0.46 / 0.30–0.46 | 1.15–1.66 / 1.58–1.89 | -1.40–-1.10 / -0.03–0.13 / 0.96–1.25 |
| ES / Asia19 | after_15m | 0.10–0.11 / 0.10–0.12 | 0.30–0.40 / 0.33–0.43 | -0.39–-0.28 / -0.02–0.01 / 0.23–0.35 |
| ES / Asia19 | after_180m | 0.36–0.53 / 0.35–0.50 | 1.19–1.58 / 1.36–1.82 | -1.33–-1.10 / 0.04–0.13 / 0.92–1.28 |
| ES / Asia19 | after_30m | 0.13–0.17 / 0.13–0.15 | 0.43–0.62 / 0.46–0.56 | -0.42–-0.33 / -0.01–0.02 / 0.29–0.51 |
| ES / Asia19 | after_60m | 0.18–0.24 / 0.17–0.21 | 0.56–0.89 / 0.60–0.87 | -0.68–-0.38 / -0.01–0.04 / 0.46–0.71 |
| ES / Asia19 | to_actual_cash_close | 0.96–1.74 / 0.88–1.73 | 3.02–6.51 / 4.04–6.34 | -5.32–-3.02 / -0.17–0.52 / 2.37–5.80 |
| ES / Asia20 | after_15m | 0.10–0.12 / 0.11–0.13 | 0.32–0.47 / 0.36–0.50 | -0.46–-0.29 / -0.03–0.01 / 0.26–0.37 |
| ES / Asia20 | after_180m | 0.39–0.59 / 0.38–0.51 | 1.22–1.79 / 1.61–1.94 | -1.43–-1.19 / 0.04–0.14 / 0.98–1.45 |
| ES / Asia20 | after_30m | 0.14–0.18 / 0.15–0.16 | 0.44–0.70 / 0.55–0.66 | -0.52–-0.36 / -0.01–0.02 / 0.35–0.54 |
| ES / Asia20 | after_60m | 0.20–0.25 / 0.19–0.23 | 0.66–0.94 / 0.66–0.95 | -0.81–-0.45 / -0.01–0.04 / 0.53–0.79 |
| ES / Asia20 | prefix_15m_to_actual_cash_close | 1.06–1.98 / 0.99–1.87 | 3.31–7.25 / 4.72–7.67 | -6.09–-3.58 / -0.16–0.55 / 2.61–6.04 |
| ES / Asia20 | prefix_30m_to_actual_cash_close | 1.07–1.91 / 1.02–1.92 | 3.33–7.03 / 4.71–7.77 | -5.91–-3.45 / -0.22–0.45 / 2.73–5.78 |
| ES / Asia20 | prefix_60m_to_actual_cash_close | 1.02–1.89 / 1.03–1.94 | 3.17–7.06 / 4.70–7.83 | -6.07–-3.58 / -0.02–0.43 / 2.68–5.84 |
| ES / Asia20 | to_actual_cash_close | 1.05–1.93 / 0.98–1.86 | 3.28–7.27 / 4.96–7.65 | -5.96–-3.58 / -0.21–0.46 / 2.51–6.27 |
| ES / JTR_fixed_01 | after_15m | 0.22–0.25 / 0.25–0.29 | 0.78–1.07 / 0.90–1.27 | -1.00–-0.69 / -0.05–0.00 / 0.62–0.83 |
| ES / JTR_fixed_01 | after_180m | 0.66–0.93 / 0.64–0.85 | 2.63–3.09 / 2.64–3.60 | -2.86–-1.89 / -0.10–0.21 / 2.00–2.40 |
| ES / JTR_fixed_01 | after_30m | 0.30–0.35 / 0.30–0.40 | 1.16–1.39 / 1.19–1.68 | -1.20–-0.93 / -0.09–0.06 / 0.81–1.12 |
| ES / JTR_fixed_01 | after_60m | 0.44–0.57 / 0.46–0.59 | 1.53–1.91 / 1.93–2.23 | -1.81–-1.19 / -0.05–0.09 / 1.22–1.40 |
| ES / JTR_fixed_01 | to_actual_cash_close | 3.31–4.96 / 2.82–5.35 | 10.29–19.09 / 13.58–20.94 | -16.06–-10.41 / -0.33–1.42 / 9.10–15.58 |
| ES / JTR_fixed_02 | after_15m | 0.28–0.33 / 0.26–0.33 | 1.00–1.33 / 1.00–1.33 | -1.00–-0.66 / 0.00–0.07 / 0.66–1.00 |
| ES / JTR_fixed_02 | after_180m | 1.67–1.93 / 1.50–2.00 | 5.46–6.60 / 5.47–7.60 | -6.16–-4.69 / 0.06–0.26 / 4.00–4.98 |
| ES / JTR_fixed_02 | after_30m | 0.40–0.48 / 0.38–0.50 | 1.44–2.12 / 1.55–1.98 | -1.33–-1.15 / 0.00–0.00 / 0.84–1.55 |
| ES / JTR_fixed_02 | after_60m | 0.60–0.75 / 0.65–0.75 | 1.89–2.85 / 2.41–3.00 | -2.44–-1.60 / -0.09–0.11 / 1.50–1.99 |
| ES / JTR_fixed_02 | to_actual_cash_close | 5.07–8.78 / 4.70–8.00 | 17.19–29.36 / 19.02–39.94 | -32.29–-14.52 / -0.71–2.41 / 13.69–24.91 |
| ES / JTR_fixed_03 | after_15m | 0.24–0.27 / 0.23–0.29 | 0.77–0.96 / 0.82–1.12 | -0.80–-0.59 / -0.02–0.00 / 0.60–0.80 |
| ES / JTR_fixed_03 | after_180m | 0.69–0.80 / 0.66–0.83 | 2.43–2.86 / 2.52–3.28 | -2.54–-1.96 / 0.06–0.19 / 1.99–2.27 |
| ES / JTR_fixed_03 | after_30m | 0.36–0.40 / 0.31–0.40 | 1.12–1.34 / 1.07–1.35 | -1.00–-0.67 / -0.01–0.05 / 0.92–1.02 |
| ES / JTR_fixed_03 | after_60m | 0.47–0.56 / 0.44–0.59 | 1.64–1.97 / 1.66–1.94 | -1.52–-1.22 / 0.00–0.09 / 1.27–1.61 |
| ES / JTR_fixed_03 | to_actual_cash_close | 2.14–3.48 / 2.06–3.23 | 6.92–13.18 / 7.93–15.04 | -9.97–-6.04 / -0.13–0.73 / 5.50–9.80 |
| ES / JTR_fixed_04 | after_15m | 0.12–0.15 / 0.11–0.15 | 0.36–0.45 / 0.40–0.47 | -0.35–-0.30 / -0.01–0.02 / 0.32–0.37 |
| ES / JTR_fixed_04 | after_180m | 0.70–0.85 / 0.71–0.84 | 2.14–3.37 / 2.53–3.46 | -2.71–-2.16 / -0.10–0.25 / 1.74–2.93 |
| ES / JTR_fixed_04 | after_30m | 0.19–0.26 / 0.19–0.24 | 0.58–0.78 / 0.61–0.73 | -0.62–-0.43 / -0.02–0.07 / 0.44–0.65 |
| ES / JTR_fixed_04 | after_60m | 0.44–0.65 / 0.40–0.52 | 1.26–1.71 / 1.39–1.87 | -1.32–-1.00 / -0.04–0.17 / 1.05–1.41 |
| ES / JTR_fixed_04 | common_1001_to_actual_cash_close | 0.91–1.03 / 0.89–1.04 | 2.76–4.06 / 4.04–4.74 | -3.98–-2.84 / 0.09–0.27 / 2.49–3.41 |
| ES / JTR_fixed_04 | prefix_15m_to_actual_cash_close | 1.08–1.18 / 0.97–1.20 | 3.17–4.40 / 4.38–5.51 | -4.65–-3.28 / -0.06–0.33 / 2.47–3.59 |
| ES / JTR_fixed_04 | prefix_30m_to_actual_cash_close | 1.04–1.13 / 0.93–1.21 | 3.09–4.36 / 4.31–5.18 | -4.67–-3.46 / -0.09–0.33 / 2.46–3.51 |
| ES / JTR_fixed_04 | prefix_60m_to_actual_cash_close | 0.91–1.03 / 0.89–1.04 | 2.76–4.06 / 4.04–4.74 | -3.98–-2.84 / 0.09–0.27 / 2.49–3.41 |
| ES / JTR_fixed_04 | to_actual_cash_close | 0.97–1.24 / 0.96–1.24 | 3.10–4.24 / 4.68–5.65 | -4.66–-3.12 / -0.05–0.34 / 2.45–3.56 |
| ES / JTR_fixed_04__shift_+10m | after_15m | 0.11–0.14 / 0.10–0.13 | 0.36–0.44 / 0.37–0.41 | -0.30–-0.20 / -0.02–0.06 / 0.26–0.36 |
| ES / JTR_fixed_04__shift_+10m | after_180m | 0.71–0.84 / 0.72–0.89 | 2.07–3.31 / 2.92–3.56 | -2.81–-1.99 / -0.08–0.18 / 1.69–2.90 |
| ES / JTR_fixed_04__shift_+10m | after_30m | 0.30–0.42 / 0.27–0.34 | 0.88–1.29 / 1.03–1.29 | -1.00–-0.77 / -0.05–0.06 / 0.73–1.03 |
| ES / JTR_fixed_04__shift_+10m | after_60m | 0.45–0.70 / 0.45–0.58 | 1.34–1.82 / 1.55–2.05 | -1.53–-1.16 / -0.08–0.17 / 1.16–1.59 |
| ES / JTR_fixed_04__shift_+10m | common_1001_to_actual_cash_close | 0.88–1.01 / 0.86–1.02 | 2.80–3.62 / 3.85–4.59 | -3.92–-2.96 / 0.09–0.27 / 2.39–3.18 |
| ES / JTR_fixed_04__shift_+10m | to_actual_cash_close | 1.08–1.24 / 0.96–1.17 | 3.19–4.24 / 4.47–5.14 | -4.47–-3.27 / -0.01–0.33 / 2.56–3.42 |
| ES / JTR_fixed_04__shift_-10m | after_15m | 0.12–0.16 / 0.12–0.14 | 0.41–0.45 / 0.47–0.51 | -0.42–-0.33 / -0.01–0.01 / 0.30–0.36 |
| ES / JTR_fixed_04__shift_-10m | after_180m | 0.69–0.88 / 0.70–0.89 | 2.17–3.23 / 2.44–3.48 | -2.64–-2.17 / -0.08–0.19 / 1.89–2.79 |
| ES / JTR_fixed_04__shift_-10m | after_30m | 0.18–0.20 / 0.16–0.18 | 0.57–0.63 / 0.61–0.74 | -0.56–-0.47 / -0.02–0.04 / 0.43–0.50 |
| ES / JTR_fixed_04__shift_-10m | after_60m | 0.40–0.55 / 0.36–0.45 | 1.12–1.56 / 1.26–1.78 | -1.31–-0.96 / -0.06–0.12 / 0.93–1.21 |
| ES / JTR_fixed_04__shift_-10m | common_1001_to_actual_cash_close | 0.93–1.04 / 0.93–1.09 | 2.76–4.01 / 4.04–4.74 | -3.98–-2.84 / 0.09–0.29 / 2.45–3.53 |
| ES / JTR_fixed_04__shift_-10m | to_actual_cash_close | 1.05–1.31 / 1.01–1.23 | 3.29–4.30 / 4.71–5.49 | -4.82–-3.00 / -0.02–0.46 / 2.49–3.69 |
| ES / JTR_fixed_05 | after_15m | 0.22–0.31 / 0.26–0.34 | 0.74–1.06 / 0.86–1.25 | -0.94–-0.65 / -0.02–0.02 / 0.61–0.81 |
| ES / JTR_fixed_05 | after_180m | 0.62–0.81 / 0.69–0.86 | 1.90–2.67 / 2.52–3.77 | -2.75–-1.66 / -0.04–0.19 / 1.63–2.18 |
| ES / JTR_fixed_05 | after_30m | 0.32–0.40 / 0.35–0.47 | 1.06–1.44 / 1.27–1.52 | -1.29–-0.92 / 0.02–0.11 / 0.89–1.08 |
| ES / JTR_fixed_05 | after_60m | 0.44–0.58 / 0.46–0.60 | 1.28–1.79 / 1.65–2.35 | -1.74–-1.29 / 0.01–0.06 / 1.05–1.43 |
| ES / JTR_fixed_05 | to_actual_cash_close | 0.89–1.16 / 0.87–1.11 | 2.80–3.96 / 3.76–4.94 | -3.65–-2.85 / 0.12–0.28 / 2.50–3.30 |
| ES / JTR_fixed_06 | after_15m | 0.24–0.28 / 0.26–0.29 | 0.73–0.87 / 0.77–1.06 | -0.90–-0.67 / 0.00–0.06 / 0.56–0.73 |
| ES / JTR_fixed_06 | after_180m | 0.61–0.77 / 0.68–0.82 | 2.07–2.69 / 2.43–3.14 | -2.25–-1.74 / -0.01–0.24 / 1.73–2.06 |
| ES / JTR_fixed_06 | after_30m | 0.33–0.38 / 0.35–0.39 | 0.99–1.23 / 1.16–1.48 | -1.36–-0.87 / -0.04–0.07 / 0.81–0.99 |
| ES / JTR_fixed_06 | after_60m | 0.44–0.50 / 0.47–0.53 | 1.38–1.58 / 1.60–2.23 | -1.56–-1.24 / -0.01–0.09 / 1.16–1.39 |
| ES / JTR_fixed_06 | to_actual_cash_close | 1.02–1.09 / 0.87–1.22 | 3.65–4.00 / 3.76–4.54 | -3.63–-2.91 / 0.00–0.23 / 2.76–3.07 |
| ES / JTR_fixed_07 | after_15m | 0.26–0.32 / 0.26–0.31 | 0.81–1.03 / 0.85–1.08 | -0.74–-0.63 / 0.03–0.06 / 0.69–0.83 |
| ES / JTR_fixed_07 | after_180m | 1.10–1.22 / 0.89–1.17 | 3.08–4.55 / 4.17–5.09 | -3.99–-3.08 / 0.10–0.29 / 2.59–3.55 |
| ES / JTR_fixed_07 | after_30m | 0.37–0.45 / 0.36–0.45 | 1.18–1.40 / 1.24–1.50 | -1.18–-1.00 / 0.05–0.10 / 0.94–1.21 |
| ES / JTR_fixed_07 | after_60m | 0.53–0.67 / 0.53–0.65 | 1.62–2.05 / 1.90–2.51 | -1.83–-1.47 / 0.07–0.19 / 1.30–1.82 |
| ES / JTR_fixed_07 | to_actual_cash_close | 1.32–1.41 / 1.04–1.32 | 3.98–4.54 / 4.75–5.45 | -4.42–-3.61 / 0.10–0.29 / 3.24–3.70 |
| ES / JTR_fixed_08 | after_15m | 0.30–0.37 / 0.32–0.35 | 0.97–1.22 / 1.06–1.45 | -0.96–-0.81 / -0.02–0.05 / 0.77–0.92 |
| ES / JTR_fixed_08 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / JTR_fixed_08 | after_30m | 0.50–0.62 / 0.50–0.72 | 1.72–2.29 / 1.74–2.37 | -1.80–-1.17 / -0.12–0.04 / 1.37–1.80 |
| ES / JTR_fixed_08 | after_60m | 0.55–0.75 / 0.59–0.85 | 1.84–2.62 / 1.88–2.66 | -1.95–-1.38 / -0.12–0.14 / 1.50–2.03 |
| ES / JTR_fixed_08 | to_actual_cash_close | 0.48–0.60 / 0.48–0.68 | 1.64–2.27 / 1.68–2.19 | -1.74–-1.13 / -0.12–0.12 / 1.38–1.80 |
| ES / JTR_fixed_EST_sensitivity_01 | after_15m | 0.30–0.33 / 0.30–0.33 | 1.05–1.22 / 1.20–1.37 | -1.09–-0.70 / 0.00–0.05 / 0.68–0.91 |
| ES / JTR_fixed_EST_sensitivity_01 | after_180m | 0.72–0.93 / 0.67–0.89 | 2.87–3.14 / 3.21–3.48 | -2.55–-2.12 / -0.08–0.25 / 2.17–2.36 |
| ES / JTR_fixed_EST_sensitivity_01 | after_30m | 0.37–0.46 / 0.38–0.44 | 1.36–1.57 / 1.44–1.61 | -1.40–-0.94 / -0.03–0.12 / 1.00–1.22 |
| ES / JTR_fixed_EST_sensitivity_01 | after_60m | 0.48–0.64 / 0.46–0.62 | 1.75–2.02 / 2.00–2.49 | -1.99–-1.21 / -0.06–0.18 / 1.38–1.68 |
| ES / JTR_fixed_EST_sensitivity_01 | to_actual_cash_close | 3.26–5.42 / 2.85–5.77 | 11.17–22.07 / 15.43–24.20 | -17.62–-10.28 / -0.30–1.45 / 8.93–17.44 |
| ES / JTR_fixed_EST_sensitivity_02 | after_15m | 0.28–0.33 / 0.29–0.31 | 1.12–1.29 / 0.95–1.36 | -1.00–-0.67 / 0.00–0.05 / 0.88–1.12 |
| ES / JTR_fixed_EST_sensitivity_02 | after_180m | 1.43–1.88 / 1.33–1.88 | 5.13–6.09 / 5.36–7.87 | -5.60–-4.16 / 0.00–0.22 / 3.64–5.23 |
| ES / JTR_fixed_EST_sensitivity_02 | after_30m | 0.46–0.50 / 0.40–0.47 | 1.70–2.07 / 1.51–2.00 | -1.54–-1.05 / -0.08–0.11 / 1.20–1.41 |
| ES / JTR_fixed_EST_sensitivity_02 | after_60m | 0.65–0.79 / 0.60–0.78 | 2.38–3.23 / 2.56–4.03 | -2.69–-1.73 / 0.00–0.11 / 1.48–2.38 |
| ES / JTR_fixed_EST_sensitivity_02 | to_actual_cash_close | 4.60–8.30 / 3.81–7.20 | 14.14–26.62 / 17.41–28.93 | -22.74–-11.35 / -0.69–1.84 / 11.52–22.74 |
| ES / JTR_fixed_EST_sensitivity_03 | after_15m | 0.23–0.29 / 0.21–0.26 | 0.83–1.00 / 0.87–1.06 | -0.84–-0.61 / 0.00–0.05 / 0.65–0.78 |
| ES / JTR_fixed_EST_sensitivity_03 | after_180m | 0.78–0.92 / 0.66–0.81 | 2.50–2.93 / 2.89–3.30 | -2.49–-1.92 / 0.04–0.20 / 1.98–2.34 |
| ES / JTR_fixed_EST_sensitivity_03 | after_30m | 0.33–0.40 / 0.28–0.36 | 1.08–1.37 / 1.17–1.51 | -1.23–-0.89 / -0.07–0.11 / 0.86–1.06 |
| ES / JTR_fixed_EST_sensitivity_03 | after_60m | 0.46–0.60 / 0.40–0.52 | 1.62–1.73 / 1.57–2.29 | -1.80–-1.26 / 0.00–0.07 / 1.23–1.51 |
| ES / JTR_fixed_EST_sensitivity_03 | to_actual_cash_close | 2.35–3.62 / 2.32–3.38 | 7.45–13.38 / 9.32–15.26 | -10.98–-7.32 / -0.24–0.96 / 5.86–10.78 |
| ES / JTR_fixed_EST_sensitivity_04 | after_15m | 0.14–0.17 / 0.16–0.20 | 0.50–0.62 / 0.58–0.77 | -0.57–-0.43 / -0.04–0.02 / 0.42–0.47 |
| ES / JTR_fixed_EST_sensitivity_04 | after_180m | 0.53–0.60 / 0.57–0.60 | 1.82–2.24 / 2.19–2.91 | -1.97–-1.64 / -0.02–0.12 / 1.43–2.07 |
| ES / JTR_fixed_EST_sensitivity_04 | after_30m | 0.20–0.27 / 0.23–0.27 | 0.69–0.84 / 0.88–1.01 | -0.85–-0.60 / -0.01–0.04 / 0.55–0.70 |
| ES / JTR_fixed_EST_sensitivity_04 | after_60m | 0.34–0.39 / 0.37–0.46 | 1.16–1.40 / 1.37–1.73 | -1.19–-1.02 / 0.00–0.06 / 0.88–1.18 |
| ES / JTR_fixed_EST_sensitivity_04 | to_actual_cash_close | 0.79–0.88 / 0.74–0.90 | 2.61–3.52 / 3.48–4.09 | -3.27–-2.50 / 0.08–0.29 / 1.92–2.76 |
| ES / JTR_fixed_EST_sensitivity_05 | after_15m | 0.24–0.33 / 0.27–0.31 | 0.79–0.92 / 0.93–1.20 | -0.82–-0.63 / 0.00–0.10 / 0.65–0.80 |
| ES / JTR_fixed_EST_sensitivity_05 | after_180m | 0.74–0.87 / 0.69–0.95 | 2.21–2.88 / 2.65–3.52 | -2.77–-1.95 / -0.10–0.30 / 1.86–2.40 |
| ES / JTR_fixed_EST_sensitivity_05 | after_30m | 0.34–0.44 / 0.35–0.43 | 0.99–1.32 / 1.21–1.60 | -1.26–-0.95 / 0.04–0.14 / 0.85–1.10 |
| ES / JTR_fixed_EST_sensitivity_05 | after_60m | 0.49–0.58 / 0.47–0.56 | 1.45–1.75 / 1.55–2.37 | -1.69–-1.21 / 0.01–0.10 / 1.12–1.46 |
| ES / JTR_fixed_EST_sensitivity_05 | to_actual_cash_close | 0.98–1.17 / 0.93–1.16 | 3.39–4.52 / 4.12–4.74 | -3.88–-3.02 / 0.04–0.39 / 2.70–3.53 |
| ES / JTR_fixed_EST_sensitivity_06 | after_15m | 0.27–0.29 / 0.26–0.28 | 0.78–0.93 / 0.93–1.03 | -0.76–-0.70 / 0.00–0.04 / 0.61–0.78 |
| ES / JTR_fixed_EST_sensitivity_06 | after_180m | 0.77–0.93 / 0.65–0.90 | 2.51–3.06 / 2.99–3.67 | -2.71–-2.27 / -0.02–0.34 / 1.97–2.49 |
| ES / JTR_fixed_EST_sensitivity_06 | after_30m | 0.35–0.40 / 0.33–0.41 | 0.99–1.29 / 1.23–1.55 | -1.11–-0.94 / 0.00–0.13 / 0.89–1.14 |
| ES / JTR_fixed_EST_sensitivity_06 | after_60m | 0.46–0.58 / 0.41–0.55 | 1.43–1.76 / 1.70–2.05 | -1.51–-1.21 / -0.13–0.18 / 1.04–1.46 |
| ES / JTR_fixed_EST_sensitivity_06 | to_actual_cash_close | 1.08–1.22 / 0.85–1.27 | 3.71–4.44 / 4.37–5.09 | -4.18–-3.03 / -0.05–0.36 / 2.88–3.62 |
| ES / JTR_fixed_EST_sensitivity_07 | after_15m | 0.27–0.31 / 0.26–0.29 | 0.84–1.09 / 0.88–1.26 | -0.80–-0.68 / 0.00–0.06 / 0.71–0.91 |
| ES / JTR_fixed_EST_sensitivity_07 | after_180m | 1.01–1.23 / 0.86–1.27 | 3.07–4.52 / 3.93–5.64 | -4.52–-2.95 / -0.15–0.38 / 2.32–3.54 |
| ES / JTR_fixed_EST_sensitivity_07 | after_30m | 0.39–0.45 / 0.36–0.45 | 1.32–1.71 / 1.32–2.14 | -1.47–-1.00 / 0.00–0.08 / 1.02–1.24 |
| ES / JTR_fixed_EST_sensitivity_07 | after_60m | 0.57–0.67 / 0.54–0.63 | 1.94–2.22 / 2.16–2.77 | -1.83–-1.54 / 0.04–0.22 / 1.50–1.66 |
| ES / JTR_fixed_EST_sensitivity_07 | to_actual_cash_close | 1.16–1.31 / 0.97–1.32 | 3.87–4.51 / 4.21–5.40 | -4.23–-2.90 / 0.12–0.30 / 2.85–3.56 |
| ES / JTR_fixed_EST_sensitivity_08 | after_15m | 0.15–0.31 / 0.16–0.36 | 0.75–1.07 / 0.82–1.15 | -0.90–-0.58 / -0.03–0.06 / 0.50–0.78 |
| ES / JTR_fixed_EST_sensitivity_08 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / JTR_fixed_EST_sensitivity_08 | after_30m | 0.50–0.62 / 0.50–0.77 | 1.60–2.60 / 1.68–2.38 | -2.01–-1.08 / -0.36–0.14 / 1.33–1.83 |
| ES / JTR_fixed_EST_sensitivity_08 | after_60m | 0.56–0.72 / 0.59–0.89 | 1.65–2.67 / 1.78–2.76 | -2.01–-1.53 / -0.07–0.13 / 1.34–2.39 |
| ES / JTR_fixed_EST_sensitivity_08 | to_actual_cash_close | 0.47–0.61 / 0.49–0.73 | 1.60–2.57 / 1.60–2.29 | -2.07–-1.17 / -0.34–0.18 / 1.36–1.78 |
| ES / London02 | after_15m | 0.08–0.12 / 0.08–0.10 | 0.28–0.37 / 0.29–0.38 | -0.30–-0.19 / -0.00–0.03 / 0.20–0.29 |
| ES / London02 | after_180m | 0.50–0.71 / 0.45–0.77 | 1.58–2.67 / 1.82–2.98 | -2.33–-1.36 / -0.12–0.15 / 1.20–2.05 |
| ES / London02 | after_30m | 0.11–0.20 / 0.11–0.18 | 0.42–1.13 / 0.47–1.11 | -0.74–-0.29 / -0.01–0.03 / 0.35–0.84 |
| ES / London02 | after_60m | 0.17–0.29 / 0.16–0.27 | 0.77–1.44 / 0.74–1.41 | -0.90–-0.49 / -0.04–0.04 / 0.56–1.08 |
| ES / London02 | to_actual_cash_close | 0.77–1.12 / 0.75–1.12 | 2.53–4.02 / 3.35–4.38 | -3.39–-2.40 / -0.07–0.37 / 1.97–3.12 |
| ES / NY08 | after_15m | 0.04–0.05 / 0.04–0.05 | 0.14–0.19 / 0.13–0.21 | -0.15–-0.08 / -0.01–0.00 / 0.10–0.13 |
| ES / NY08 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / NY08 | after_30m | 0.04–0.05 / 0.04–0.06 | 0.19–0.23 / 0.15–0.28 | -0.16–-0.10 / 0.00–0.01 / 0.13–0.15 |
| ES / NY08 | after_60m | 0.01–0.01 / 0.12–0.12 | 0.01–0.01 / 0.12–0.12 | -0.04–-0.04 / -0.04–-0.04 / -0.04–-0.04 |
| ES / NY08 | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / ONS03 | after_15m | 0.09–0.12 / 0.08–0.12 | 0.29–0.39 / 0.32–0.42 | -0.38–-0.22 / 0.00–0.02 / 0.22–0.31 |
| ES / ONS03 | after_180m | 0.43–0.68 / 0.47–0.64 | 1.60–2.46 / 1.50–2.68 | -2.03–-1.07 / -0.02–0.14 / 1.28–1.87 |
| ES / ONS03 | after_30m | 0.13–0.16 / 0.12–0.15 | 0.42–0.57 / 0.46–0.59 | -0.42–-0.34 / -0.01–0.04 / 0.32–0.43 |
| ES / ONS03 | after_60m | 0.19–0.24 / 0.18–0.21 | 0.56–0.75 / 0.65–0.83 | -0.65–-0.43 / -0.03–0.02 / 0.39–0.54 |
| ES / ONS03 | to_actual_cash_close | 0.91–1.39 / 0.88–1.33 | 3.03–4.53 / 3.65–6.27 | -4.40–-2.88 / -0.10–0.31 / 2.50–4.17 |
| ES / ONS20 | after_15m | 0.06–0.09 / 0.07–0.08 | 0.24–0.32 / 0.23–0.32 | -0.20–-0.18 / 0.00–0.02 / 0.16–0.22 |
| ES / ONS20 | after_180m | 0.31–0.37 / 0.28–0.45 | 1.12–1.46 / 1.12–1.55 | -1.19–-0.86 / 0.00–0.04 / 0.90–1.08 |
| ES / ONS20 | after_30m | 0.10–0.11 / 0.09–0.12 | 0.30–0.52 / 0.38–0.49 | -0.37–-0.27 / -0.01–0.01 / 0.23–0.40 |
| ES / ONS20 | after_60m | 0.12–0.17 / 0.14–0.16 | 0.48–0.70 / 0.53–0.61 | -0.48–-0.40 / 0.00–0.04 / 0.35–0.50 |
| ES / ONS20 | to_actual_cash_close | 1.33–2.21 / 1.13–2.09 | 4.18–7.80 / 5.50–10.12 | -7.60–-4.26 / -0.29–0.44 / 3.33–6.73 |
| ES / OR15 | after_15m | 0.37–0.41 / 0.37–0.45 | 1.14–1.32 / 1.24–1.42 | -1.05–-0.93 / -0.07–0.12 / 0.92–1.14 |
| ES / OR15 | after_180m | 0.81–1.10 / 0.92–1.11 | 2.74–3.55 / 3.51–4.63 | -3.78–-2.48 / -0.09–0.28 / 2.12–3.13 |
| ES / OR15 | after_30m | 0.48–0.61 / 0.49–0.60 | 1.55–1.79 / 1.74–2.46 | -1.82–-1.31 / -0.08–0.05 / 1.27–1.49 |
| ES / OR15 | after_60m | 0.62–0.77 / 0.63–0.82 | 2.02–2.43 / 2.05–3.12 | -2.47–-1.78 / -0.01–0.20 / 1.51–1.97 |
| ES / OR15 | common_1001_to_actual_cash_close | 1.13–1.48 / 1.18–1.36 | 3.86–5.02 / 4.71–6.25 | -4.80–-3.69 / 0.15–0.38 / 3.11–4.07 |
| ES / OR15 | prefix_15m_to_actual_cash_close | 1.13–1.48 / 1.18–1.36 | 3.86–5.02 / 4.71–6.25 | -4.80–-3.69 / 0.15–0.38 / 3.11–4.07 |
| ES / OR15 | prefix_30m_to_actual_cash_close | 1.19–1.43 / 1.05–1.42 | 3.60–4.89 / 4.40–5.97 | -4.61–-3.61 / 0.07–0.46 / 3.07–4.11 |
| ES / OR15 | prefix_60m_to_actual_cash_close | 1.03–1.41 / 0.95–1.36 | 3.56–4.46 / 4.14–5.60 | -4.14–-3.18 / -0.03–0.41 / 2.91–3.85 |
| ES / OR15 | to_actual_cash_close | 1.21–1.58 / 1.22–1.54 | 3.85–5.28 / 4.79–6.44 | -5.41–-3.49 / 0.18–0.50 / 3.12–4.24 |
| ES / OR15__shift_+10m | after_15m | 0.35–0.50 / 0.31–0.45 | 1.16–1.65 / 1.23–1.99 | -1.57–-0.86 / -0.09–0.15 / 0.88–1.17 |
| ES / OR15__shift_+10m | after_180m | 0.99–1.22 / 1.00–1.24 | 3.05–4.40 / 3.66–5.25 | -4.06–-2.82 / -0.03–0.34 / 2.48–3.47 |
| ES / OR15__shift_+10m | after_30m | 0.49–0.66 / 0.45–0.59 | 1.50–1.99 / 1.87–2.57 | -2.03–-1.34 / -0.04–0.13 / 1.25–1.59 |
| ES / OR15__shift_+10m | after_60m | 0.67–0.93 / 0.65–0.84 | 2.07–2.75 / 2.52–3.33 | -2.66–-2.09 / -0.09–0.17 / 1.70–2.20 |
| ES / OR15__shift_+10m | common_1001_to_actual_cash_close | 1.31–1.75 / 1.30–1.68 | 4.53–6.17 / 5.83–7.65 | -5.28–-4.42 / 0.14–0.44 / 3.76–5.49 |
| ES / OR15__shift_+10m | to_actual_cash_close | 1.38–1.83 / 1.32–1.79 | 4.59–6.46 / 5.82–7.16 | -5.54–-4.50 / 0.17–0.47 / 3.97–5.38 |
| ES / OR15__shift_-10m | after_15m | 0.49–0.62 / 0.48–0.53 | 1.35–1.79 / 1.68–1.96 | -1.66–-1.20 / -0.07–0.07 / 1.08–1.44 |
| ES / OR15__shift_-10m | after_180m | 1.33–1.43 / 1.26–1.64 | 3.85–5.08 / 4.99–5.88 | -4.55–-3.38 / -0.12–0.33 / 2.96–4.09 |
| ES / OR15__shift_-10m | after_30m | 0.67–0.78 / 0.65–0.81 | 1.99–2.45 / 2.14–2.63 | -2.10–-1.56 / -0.12–0.12 / 1.64–2.14 |
| ES / OR15__shift_-10m | after_60m | 0.92–1.03 / 0.89–1.06 | 2.73–3.22 / 3.20–3.64 | -2.91–-2.59 / -0.01–0.32 / 2.15–2.73 |
| ES / OR15__shift_-10m | common_1001_to_actual_cash_close | 1.62–1.97 / 1.58–1.88 | 5.14–6.98 / 6.24–9.05 | -6.60–-4.82 / 0.22–0.50 / 3.89–5.94 |
| ES / OR15__shift_-10m | to_actual_cash_close | 1.80–2.05 / 1.71–2.05 | 5.33–7.89 / 6.97–9.05 | -7.03–-4.90 / 0.00–0.61 / 4.07–6.77 |
| ES / OR5 | after_15m | 0.55–0.66 / 0.54–0.60 | 1.66–2.02 / 1.81–2.16 | -1.80–-1.29 / -0.07–0.09 / 1.16–1.64 |
| ES / OR5 | after_180m | 1.43–1.69 / 1.35–1.80 | 4.37–5.80 / 5.74–7.31 | -5.14–-4.17 / -0.12–0.37 / 3.40–4.45 |
| ES / OR5 | after_30m | 0.81–0.87 / 0.78–0.94 | 2.32–2.73 / 2.38–3.23 | -2.54–-1.91 / -0.12–0.15 / 1.83–2.35 |
| ES / OR5 | after_60m | 1.06–1.18 / 0.96–1.27 | 3.07–3.45 / 3.63–4.35 | -3.26–-2.91 / -0.01–0.37 / 2.22–2.97 |
| ES / OR5 | common_1001_to_actual_cash_close | 1.83–2.25 / 1.84–2.15 | 5.74–7.12 / 7.72–9.98 | -8.01–-5.36 / 0.24–0.57 / 4.31–6.71 |
| ES / OR5 | to_actual_cash_close | 1.99–2.38 / 1.91–2.20 | 5.59–7.95 / 7.66–9.79 | -8.02–-5.55 / 0.00–0.65 / 4.53–7.15 |
| ES / OR5__shift_+10m | after_15m | 0.71–0.78 / 0.69–0.81 | 2.07–2.58 / 2.33–3.36 | -2.60–-1.66 / -0.13–0.24 / 1.69–2.10 |
| ES / OR5__shift_+10m | after_180m | 1.72–2.10 / 1.83–2.08 | 5.48–6.57 / 7.18–9.60 | -7.49–-4.90 / -0.18–0.48 / 4.32–5.62 |
| ES / OR5__shift_+10m | after_30m | 0.97–1.13 / 0.94–1.23 | 2.99–3.73 / 3.49–5.15 | -4.13–-2.79 / -0.12–0.10 / 2.35–2.83 |
| ES / OR5__shift_+10m | after_60m | 1.24–1.45 / 1.34–1.53 | 4.10–4.63 / 4.53–7.10 | -5.87–-3.34 / -0.02–0.32 / 3.14–3.74 |
| ES / OR5__shift_+10m | common_1001_to_actual_cash_close | 2.19–2.92 / 2.31–2.82 | 8.22–10.69 / 9.96–13.26 | -10.51–-7.55 / 0.29–0.72 / 6.54–8.82 |
| ES / OR5__shift_+10m | to_actual_cash_close | 2.37–3.16 / 2.42–2.98 | 8.88–10.44 / 10.42–13.77 | -10.59–-7.81 / 0.30–0.94 / 7.16–8.33 |
| ES / OR5__shift_-10m | after_15m | 1.90–2.18 / 1.44–2.40 | 6.06–8.00 / 5.59–8.31 | -6.52–-4.15 / -0.24–0.78 / 4.58–6.50 |
| ES / OR5__shift_-10m | after_180m | 5.06–5.61 / 4.66–5.83 | 16.81–20.01 / 18.50–24.41 | -18.09–-13.62 / -0.55–1.32 / 12.69–16.38 |
| ES / OR5__shift_-10m | after_30m | 2.39–3.07 / 1.91–3.25 | 8.78–10.00 / 7.00–12.49 | -8.93–-5.64 / -0.37–0.78 / 6.27–8.22 |
| ES / OR5__shift_-10m | after_60m | 3.25–4.00 / 3.16–4.20 | 11.98–14.64 / 10.99–16.30 | -11.94–-8.40 / -0.11–0.53 / 9.58–12.48 |
| ES / OR5__shift_-10m | common_1001_to_actual_cash_close | 6.21–6.62 / 5.74–6.85 | 21.36–24.07 / 26.94–35.39 | -26.30–-19.59 / 0.77–2.10 / 18.06–19.79 |
| ES / OR5__shift_-10m | to_actual_cash_close | 6.97–7.85 / 6.07–8.46 | 24.37–28.33 / 28.17–37.73 | -28.66–-21.14 / -0.55–2.58 / 19.45–22.64 |
| ES / OR_activity_1_1 | after_15m | 0.35–0.39 / 0.31–0.40 | 1.16–1.29 / 1.23–1.56 | -1.17–-0.91 / -0.02–0.13 / 0.93–1.13 |
| ES / OR_activity_1_1 | after_180m | 0.93–1.05 / 0.81–1.08 | 2.64–3.46 / 3.40–4.65 | -3.67–-2.61 / 0.02–0.30 / 2.05–3.00 |
| ES / OR_activity_1_1 | after_30m | 0.45–0.59 / 0.41–0.59 | 1.52–1.78 / 1.81–2.16 | -1.75–-1.37 / -0.05–0.23 / 1.18–1.55 |
| ES / OR_activity_1_1 | after_60m | 0.63–0.80 / 0.58–0.77 | 1.97–2.37 / 2.15–3.18 | -2.67–-1.78 / -0.13–0.17 / 1.56–2.10 |
| ES / OR_activity_1_1 | common_1001_to_actual_cash_close | 1.17–1.46 / 1.08–1.33 | 3.90–4.99 / 4.68–6.55 | -5.48–-3.51 / 0.21–0.34 / 3.09–4.19 |
| ES / OR_activity_1_1 | to_actual_cash_close | 1.26–1.59 / 1.17–1.43 | 3.77–5.44 / 4.85–6.68 | -5.66–-3.60 / 0.10–0.44 / 2.80–4.60 |
| ES / OR_activity_1_2 | after_15m | 0.46–0.57 / 0.49–0.52 | 1.57–1.78 / 1.56–1.98 | -1.65–-1.09 / -0.09–0.08 / 1.07–1.57 |
| ES / OR_activity_1_2 | after_180m | 1.25–1.58 / 1.14–1.62 | 3.75–4.66 / 5.17–7.24 | -5.18–-3.89 / -0.11–0.37 / 2.89–4.00 |
| ES / OR_activity_1_2 | after_30m | 0.67–0.81 / 0.68–0.83 | 2.08–2.64 / 2.34–2.92 | -2.44–-1.84 / -0.15–0.20 / 1.62–2.36 |
| ES / OR_activity_1_2 | after_60m | 0.87–1.07 / 0.82–1.15 | 2.82–3.22 / 3.51–3.81 | -3.22–-2.68 / -0.07–0.29 / 1.88–2.73 |
| ES / OR_activity_1_2 | common_1001_to_actual_cash_close | 1.55–2.01 / 1.69–1.97 | 5.02–6.27 / 6.09–9.49 | -6.90–-4.46 / 0.21–0.50 / 3.78–5.39 |
| ES / OR_activity_1_2 | to_actual_cash_close | 1.71–2.23 / 1.61–2.12 | 5.06–6.55 / 6.95–9.77 | -7.69–-4.42 / 0.12–0.57 / 4.05–5.58 |
| ES / OR_activity_3_2 | after_15m | 0.27–0.35 / 0.24–0.29 | 0.85–1.08 / 0.95–1.20 | -0.93–-0.67 / -0.03–0.12 / 0.67–0.89 |
| ES / OR_activity_3_2 | after_180m | 0.72–0.83 / 0.69–0.91 | 2.22–2.86 / 2.59–3.91 | -3.19–-1.89 / 0.01–0.17 / 1.66–2.30 |
| ES / OR_activity_3_2 | after_30m | 0.36–0.47 / 0.33–0.43 | 1.13–1.45 / 1.31–1.98 | -1.42–-0.98 / 0.03–0.10 / 0.96–1.07 |
| ES / OR_activity_3_2 | after_60m | 0.50–0.64 / 0.45–0.60 | 1.46–2.02 / 1.71–2.43 | -2.21–-1.33 / -0.07–0.11 / 1.18–1.61 |
| ES / OR_activity_3_2 | common_1001_to_actual_cash_close | 0.99–1.23 / 0.94–1.16 | 3.08–3.82 / 4.12–5.84 | -4.49–-3.05 / 0.15–0.24 / 2.56–3.42 |
| ES / OR_activity_3_2 | to_actual_cash_close | 1.04–1.25 / 0.91–1.23 | 2.93–4.10 / 3.89–5.24 | -3.96–-2.75 / 0.16–0.32 / 2.35–3.40 |
| ES / PIN015_Asia_UTC | after_15m | 0.11–0.14 / 0.11–0.15 | 0.38–0.58 / 0.43–0.54 | -0.42–-0.39 / -0.02–0.02 / 0.33–0.41 |
| ES / PIN015_Asia_UTC | after_180m | 0.35–0.52 / 0.33–0.47 | 1.09–1.58 / 1.37–1.80 | -1.26–-1.01 / 0.04–0.08 / 0.81–1.28 |
| ES / PIN015_Asia_UTC | after_30m | 0.16–0.20 / 0.14–0.23 | 0.56–0.70 / 0.61–0.73 | -0.57–-0.42 / -0.03–0.02 / 0.40–0.54 |
| ES / PIN015_Asia_UTC | after_60m | 0.19–0.27 / 0.18–0.30 | 0.60–0.92 / 0.84–0.99 | -0.75–-0.60 / 0.00–0.04 / 0.49–0.76 |
| ES / PIN015_Asia_UTC | to_actual_cash_close | 0.90–1.64 / 0.86–1.68 | 2.88–6.26 / 3.66–6.50 | -5.52–-3.08 / -0.09–0.45 / 2.08–5.17 |
| ES / PIN015_London_UTC | after_15m | 0.08–0.11 / 0.08–0.10 | 0.27–0.35 / 0.30–0.38 | -0.27–-0.19 / 0.00–0.01 / 0.21–0.28 |
| ES / PIN015_London_UTC | after_180m | 0.49–0.67 / 0.48–0.65 | 1.47–2.36 / 1.83–2.78 | -1.99–-1.40 / -0.08–0.12 / 1.12–1.94 |
| ES / PIN015_London_UTC | after_30m | 0.11–0.15 / 0.11–0.14 | 0.38–0.52 / 0.46–0.58 | -0.38–-0.30 / 0.00–0.02 / 0.35–0.39 |
| ES / PIN015_London_UTC | after_60m | 0.22–0.34 / 0.23–0.28 | 0.75–1.21 / 0.87–1.12 | -0.83–-0.57 / -0.04–0.08 / 0.56–0.96 |
| ES / PIN015_London_UTC | to_actual_cash_close | 0.72–0.98 / 0.71–0.99 | 2.13–3.34 / 3.19–3.97 | -3.23–-2.35 / 0.02–0.32 / 1.81–2.85 |
| ES / PIN015_NY_UTC | after_15m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN015_NY_UTC | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN015_NY_UTC | after_30m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN015_NY_UTC | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN015_NY_UTC | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN073_1 | after_15m | 0.23–0.26 / 0.23–0.26 | 0.78–1.07 / 0.80–1.06 | -0.82–-0.65 / 0.00–0.05 / 0.57–0.83 |
| ES / PIN073_1 | after_180m | 1.08–1.37 / 1.00–1.31 | 3.95–4.33 / 3.99–5.24 | -3.88–-3.37 / -0.02–0.33 / 2.95–3.30 |
| ES / PIN073_1 | after_30m | 0.38–0.40 / 0.35–0.42 | 1.19–1.53 / 1.33–1.42 | -1.06–-0.93 / -0.01–0.04 / 0.90–1.23 |
| ES / PIN073_1 | after_60m | 0.69–0.75 / 0.65–0.75 | 2.31–2.71 / 2.55–2.99 | -2.21–-1.99 / -0.13–0.11 / 1.93–2.18 |
| ES / PIN073_1 | to_actual_cash_close | 2.88–5.06 / 2.76–4.38 | 9.15–17.11 / 12.32–22.00 | -13.50–-8.40 / -0.56–1.34 / 7.19–14.00 |
| ES / PIN073_2 | after_15m | 0.61–0.81 / 0.54–0.96 | 2.14–2.45 / 2.06–2.94 | -2.39–-1.60 / -0.08–0.27 / 1.72–1.90 |
| ES / PIN073_2 | after_180m | 1.64–1.85 / 1.55–2.14 | 5.47–6.72 / 6.33–8.16 | -6.84–-5.12 / -0.28–0.36 / 4.39–5.53 |
| ES / PIN073_2 | after_30m | 0.87–1.09 / 0.75–1.20 | 2.94–3.33 / 2.94–3.99 | -2.99–-2.35 / -0.16–0.20 / 2.34–2.90 |
| ES / PIN073_2 | after_60m | 1.15–1.39 / 1.09–1.73 | 4.05–4.84 / 4.21–5.43 | -4.38–-3.40 / -0.05–0.33 / 3.22–4.25 |
| ES / PIN073_2 | to_actual_cash_close | 2.44–2.60 / 2.26–3.17 | 8.35–9.29 / 10.00–14.50 | -10.28–-7.01 / -0.14–0.89 / 6.77–8.11 |
| ES / PIN073_3 | after_15m | 0.28–0.33 / 0.26–0.33 | 1.00–1.33 / 1.00–1.33 | -1.00–-0.66 / 0.00–0.07 / 0.66–1.00 |
| ES / PIN073_3 | after_180m | 1.67–1.93 / 1.50–2.00 | 5.46–6.60 / 5.47–7.60 | -6.16–-4.69 / 0.06–0.26 / 4.00–4.98 |
| ES / PIN073_3 | after_30m | 0.40–0.48 / 0.38–0.50 | 1.44–2.12 / 1.55–1.98 | -1.33–-1.15 / 0.00–0.00 / 0.84–1.55 |
| ES / PIN073_3 | after_60m | 0.60–0.75 / 0.65–0.75 | 1.89–2.85 / 2.41–3.00 | -2.44–-1.60 / -0.09–0.11 / 1.50–1.99 |
| ES / PIN073_3 | to_actual_cash_close | 5.07–8.78 / 4.70–8.00 | 17.19–29.36 / 19.02–39.94 | -32.29–-14.52 / -0.71–2.41 / 13.69–24.91 |
| ES / PIN073_4 | after_15m | 0.26–0.30 / 0.27–0.33 | 0.72–0.96 / 0.95–1.15 | -0.92–-0.68 / -0.03–0.06 / 0.58–0.86 |
| ES / PIN073_4 | after_180m | 0.84–1.03 / 0.70–1.13 | 2.46–3.11 / 3.34–3.78 | -2.84–-2.50 / 0.02–0.33 / 2.02–2.64 |
| ES / PIN073_4 | after_30m | 0.34–0.43 / 0.35–0.46 | 0.97–1.27 / 1.30–1.53 | -1.14–-0.98 / -0.02–0.10 / 0.78–1.06 |
| ES / PIN073_4 | after_60m | 0.47–0.58 / 0.45–0.62 | 1.30–1.78 / 1.65–2.28 | -1.62–-1.15 / -0.07–0.17 / 1.04–1.41 |
| ES / PIN073_4 | to_actual_cash_close | 1.17–1.32 / 0.88–1.30 | 3.64–4.92 / 4.27–5.51 | -4.50–-3.20 / 0.02–0.40 / 2.88–3.88 |
| ES / PIN073_5 | after_15m | 0.28–0.32 / 0.29–0.31 | 0.88–1.15 / 0.92–1.19 | -0.95–-0.74 / -0.03–0.05 / 0.67–0.94 |
| ES / PIN073_5 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN073_5 | after_30m | 0.41–0.48 / 0.38–0.42 | 1.32–1.71 / 1.34–1.58 | -1.10–-0.98 / 0.03–0.13 / 1.00–1.18 |
| ES / PIN073_5 | after_60m | 0.56–0.73 / 0.58–0.70 | 1.88–2.25 / 2.20–2.39 | -1.77–-1.58 / 0.00–0.11 / 1.41–1.97 |
| ES / PIN073_5 | to_actual_cash_close | 0.86–0.93 / 0.77–0.95 | 2.73–3.23 / 2.77–3.64 | -3.00–-1.89 / -0.04–0.14 / 2.22–2.85 |
| ES / PIN074_ref_00 | after_15m | 1.00–2.00 / 1.25–1.71 | 5.00–7.80 / 5.00–7.00 | -4.85–-3.00 / 0.00–0.00 / 3.00–5.50 |
| ES / PIN074_ref_00 | after_180m | 6.20–8.00 / 5.66–9.42 | 24.00–35.89 / 23.03–37.85 | -27.90–-14.18 / 0.00–1.00 / 18.00–25.83 |
| ES / PIN074_ref_00 | after_30m | 1.67–2.38 / 2.00–2.25 | 7.00–10.50 / 7.37–10.90 | -7.93–-5.00 / 0.00–0.31 / 4.88–7.80 |
| ES / PIN074_ref_00 | after_60m | 2.50–3.50 / 2.63–3.50 | 11.00–15.45 / 11.00–16.00 | -11.90–-8.00 / -0.12–1.00 / 8.00–11.22 |
| ES / PIN074_ref_00 | to_actual_cash_close | 24.10–48.00 / 20.17–49.00 | 91.75–191.00 / 124.00–251.60 | -184.43–-68.88 / -6.33–10.50 / 72.70–144.00 |
| ES / PIN074_ref_01 | after_15m | 1.00–1.50 / 1.33–1.57 | 5.57–6.35 / 5.33–7.00 | -4.65–-3.50 / -0.33–0.00 / 3.50–4.62 |
| ES / PIN074_ref_01 | after_180m | 5.75–9.00 / 5.82–9.67 | 26.87–34.45 / 26.43–46.10 | -24.85–-15.94 / -0.67–0.67 / 17.38–25.93 |
| ES / PIN074_ref_01 | after_30m | 1.67–2.11 / 1.80–2.06 | 6.97–8.00 / 7.49–10.00 | -7.00–-5.00 / -0.33–0.00 / 4.97–6.20 |
| ES / PIN074_ref_01 | after_60m | 2.50–3.50 / 2.59–3.83 | 10.01–13.55 / 10.57–14.07 | -10.55–-7.26 / 0.00–0.33 / 7.00–10.27 |
| ES / PIN074_ref_01 | to_actual_cash_close | 19.47–38.00 / 18.12–32.75 | 75.65–165.60 / 87.70–161.17 | -111.15–-64.75 / -4.40–7.60 / 59.53–133.45 |
| ES / PIN074_ref_03 | after_15m | 1.00–1.21 / 1.00–1.25 | 3.83–5.00 / 3.88–4.86 | -3.57–-2.78 / 0.00–0.18 / 2.79–4.35 |
| ES / PIN074_ref_03 | after_180m | 2.62–3.73 / 2.77–3.75 | 8.75–13.00 / 9.59–14.28 | -10.40–-7.84 / 0.36–0.73 / 6.42–9.50 |
| ES / PIN074_ref_03 | after_30m | 1.35–1.67 / 1.40–2.00 | 4.75–7.00 / 5.20–6.56 | -5.38–-3.74 / -0.38–0.33 / 3.19–5.12 |
| ES / PIN074_ref_03 | after_60m | 1.71–2.33 / 1.88–2.38 | 5.77–8.95 / 6.00–9.50 | -6.25–-4.89 / 0.11–0.45 / 4.37–6.21 |
| ES / PIN074_ref_03 | to_actual_cash_close | 8.50–13.00 / 7.27–13.00 | 27.40–60.40 / 32.11–65.48 | -44.36–-22.92 / -1.50–2.65 / 21.68–49.50 |
| ES / PIN074_ref_04 | after_15m | 1.33–1.58 / 1.33–1.44 | 4.71–5.25 / 5.10–6.27 | -4.55–-3.96 / 0.00–0.22 / 3.69–4.40 |
| ES / PIN074_ref_04 | after_180m | 3.50–4.18 / 3.33–4.10 | 13.12–16.37 / 15.30–21.15 | -15.20–-10.28 / 0.40–0.67 / 9.75–12.72 |
| ES / PIN074_ref_04 | after_30m | 1.71–2.00 / 1.75–2.00 | 6.39–7.70 / 7.08–8.12 | -5.74–-5.25 / 0.00–0.20 / 4.18–5.48 |
| ES / PIN074_ref_04 | after_60m | 2.44–2.69 / 2.33–2.67 | 8.00–10.44 / 9.78–12.44 | -9.27–-6.00 / 0.00–0.33 / 5.36–7.59 |
| ES / PIN074_ref_04 | to_actual_cash_close | 12.00–16.83 / 10.00–15.56 | 45.49–64.80 / 44.32–78.93 | -64.93–-34.01 / -1.43–3.53 / 34.01–51.72 |
| ES / PIN074_ref_07 | after_15m | 1.08–1.30 / 1.00–1.43 | 4.89–5.50 / 4.40–6.00 | -4.33–-2.67 / 0.00–0.17 / 3.11–4.00 |
| ES / PIN074_ref_07 | after_180m | 5.59–8.00 / 6.33–7.57 | 22.50–38.54 / 28.00–38.24 | -33.50–-19.79 / -0.50–1.38 / 17.99–28.80 |
| ES / PIN074_ref_07 | after_30m | 1.67–2.00 / 1.57–1.88 | 6.25–7.47 / 6.00–8.97 | -6.07–-4.50 / -0.07–0.40 / 4.50–6.40 |
| ES / PIN074_ref_07 | after_60m | 2.17–2.67 / 2.20–2.75 | 8.82–10.73 / 7.70–12.30 | -9.05–-5.30 / -0.33–0.37 / 6.43–7.54 |
| ES / PIN074_ref_07 | to_actual_cash_close | 12.00–15.58 / 11.75–16.17 | 47.34–68.73 / 56.82–74.99 | -63.26–-39.81 / -1.12–4.12 / 32.95–57.74 |
| ES / PIN075_01 | after_15m | 0.15–0.19 / 0.16–0.21 | 0.57–0.69 / 0.65–0.81 | -0.65–-0.40 / -0.01–0.00 / 0.40–0.52 |
| ES / PIN075_01 | after_180m | 0.57–0.83 / 0.55–0.89 | 1.99–2.53 / 2.34–3.67 | -2.58–-1.45 / -0.02–0.17 / 1.49–1.92 |
| ES / PIN075_01 | after_30m | 0.22–0.27 / 0.20–0.28 | 0.86–1.09 / 0.80–1.14 | -0.93–-0.55 / -0.04–0.04 / 0.61–0.85 |
| ES / PIN075_01 | after_60m | 0.31–0.41 / 0.29–0.46 | 1.03–1.66 / 1.26–1.58 | -1.24–-0.88 / -0.06–0.08 / 0.76–1.22 |
| ES / PIN075_01 | to_actual_cash_close | 2.27–4.00 / 2.50–3.95 | 7.77–14.03 / 9.79–16.56 | -13.48–-6.31 / -0.23–1.08 / 6.39–11.92 |
| ES / PIN075_02 | after_15m | 0.07–0.09 / 0.06–0.08 | 0.26–0.29 / 0.22–0.29 | -0.23–-0.16 / 0.00–0.02 / 0.21–0.24 |
| ES / PIN075_02 | after_180m | 0.26–0.34 / 0.21–0.35 | 0.80–1.24 / 0.91–1.13 | -0.80–-0.67 / -0.04–0.08 / 0.63–0.88 |
| ES / PIN075_02 | after_30m | 0.10–0.12 / 0.08–0.11 | 0.37–0.44 / 0.34–0.40 | -0.35–-0.25 / 0.00–0.03 / 0.25–0.37 |
| ES / PIN075_02 | after_60m | 0.14–0.16 / 0.11–0.16 | 0.49–0.55 / 0.47–0.56 | -0.48–-0.38 / -0.03–0.03 / 0.33–0.42 |
| ES / PIN075_02 | to_actual_cash_close | 1.16–2.10 / 1.12–1.96 | 3.73–7.33 / 5.08–9.22 | -6.81–-3.70 / -0.24–0.56 / 3.27–6.03 |
| ES / PIN075_03 | after_15m | 0.18–0.24 / 0.18–0.26 | 0.60–0.81 / 0.72–0.87 | -0.66–-0.58 / 0.00–0.02 / 0.51–0.65 |
| ES / PIN075_03 | after_180m | 0.50–0.72 / 0.52–0.62 | 1.55–2.17 / 2.24–2.56 | -1.87–-1.56 / 0.04–0.18 / 1.09–1.79 |
| ES / PIN075_03 | after_30m | 0.25–0.32 / 0.25–0.36 | 0.86–1.09 / 1.00–1.21 | -1.03–-0.78 / -0.08–0.04 / 0.68–0.88 |
| ES / PIN075_03 | after_60m | 0.34–0.44 / 0.31–0.48 | 1.10–1.38 / 1.23–1.59 | -1.11–-0.93 / 0.00–0.07 / 0.88–1.15 |
| ES / PIN075_03 | to_actual_cash_close | 1.38–2.44 / 1.35–2.10 | 4.27–7.85 / 4.76–9.45 | -7.18–-4.08 / -0.03–0.66 / 3.39–6.63 |
| ES / PIN075_04 | after_15m | 0.21–0.22 / 0.17–0.22 | 0.65–0.79 / 0.61–0.81 | -0.63–-0.45 / 0.00–0.04 / 0.50–0.58 |
| ES / PIN075_04 | after_180m | 0.64–0.74 / 0.49–0.79 | 2.05–2.48 / 2.07–2.82 | -2.06–-1.76 / 0.03–0.15 / 1.61–1.93 |
| ES / PIN075_04 | after_30m | 0.30–0.36 / 0.26–0.35 | 0.93–1.21 / 0.97–1.19 | -0.92–-0.70 / -0.02–0.07 / 0.74–0.97 |
| ES / PIN075_04 | after_60m | 0.43–0.47 / 0.34–0.45 | 1.27–1.72 / 1.43–1.70 | -1.33–-1.06 / 0.00–0.14 / 1.00–1.43 |
| ES / PIN075_04 | to_actual_cash_close | 1.80–2.96 / 1.72–2.78 | 5.62–11.57 / 6.65–12.13 | -9.24–-5.54 / -0.13–0.68 / 4.31–9.18 |
| ES / PIN075_05 | after_15m | 0.13–0.15 / 0.14–0.16 | 0.43–0.50 / 0.46–0.58 | -0.48–-0.30 / -0.04–0.00 / 0.28–0.42 |
| ES / PIN075_05 | after_180m | 0.49–0.62 / 0.46–0.52 | 1.71–1.90 / 1.82–2.08 | -1.56–-1.33 / 0.00–0.24 / 1.14–1.47 |
| ES / PIN075_05 | after_30m | 0.18–0.22 / 0.18–0.22 | 0.56–0.70 / 0.63–0.79 | -0.62–-0.47 / -0.01–0.04 / 0.45–0.52 |
| ES / PIN075_05 | after_60m | 0.26–0.30 / 0.28–0.30 | 0.88–0.96 / 0.96–1.28 | -0.89–-0.69 / -0.04–0.04 / 0.65–0.75 |
| ES / PIN075_05 | to_actual_cash_close | 1.48–2.28 / 1.48–2.02 | 4.98–7.34 / 6.54–8.44 | -6.67–-5.20 / -0.24–0.69 / 4.09–6.15 |
| ES / PIN075_06 | after_15m | 0.18–0.20 / 0.15–0.19 | 0.59–0.73 / 0.59–0.80 | -0.55–-0.46 / 0.00–0.03 / 0.44–0.57 |
| ES / PIN075_06 | after_180m | 0.75–1.31 / 0.86–1.10 | 2.88–4.67 / 2.85–5.31 | -3.80–-2.16 / -0.13–0.22 / 2.12–3.59 |
| ES / PIN075_06 | after_30m | 0.27–0.33 / 0.25–0.29 | 0.89–1.13 / 0.86–1.22 | -0.84–-0.65 / 0.00–0.08 / 0.69–0.89 |
| ES / PIN075_06 | after_60m | 0.40–0.53 / 0.34–0.43 | 1.32–1.46 / 1.28–1.70 | -1.31–-0.79 / 0.00–0.14 / 1.00–1.16 |
| ES / PIN075_06 | to_actual_cash_close | 1.94–2.87 / 1.83–2.62 | 5.98–10.41 / 8.04–13.07 | -9.35–-6.36 / -0.21–0.66 / 4.88–8.39 |
| ES / PIN075_07 | after_15m | 0.27–0.35 / 0.23–0.36 | 0.94–1.12 / 0.81–1.39 | -0.97–-0.69 / -0.03–0.10 / 0.77–0.87 |
| ES / PIN075_07 | after_180m | 0.70–0.83 / 0.71–0.89 | 2.00–3.20 / 2.89–3.70 | -3.09–-2.41 / -0.10–0.16 / 1.64–2.64 |
| ES / PIN075_07 | after_30m | 0.34–0.47 / 0.32–0.51 | 1.30–1.49 / 1.24–1.79 | -1.35–-0.85 / -0.05–0.09 / 1.06–1.27 |
| ES / PIN075_07 | after_60m | 0.50–0.58 / 0.49–0.66 | 1.54–1.98 / 1.79–2.49 | -1.65–-1.51 / -0.02–0.14 / 1.17–1.76 |
| ES / PIN075_07 | to_actual_cash_close | 1.01–1.13 / 0.93–1.23 | 3.24–3.78 / 4.26–5.23 | -4.19–-2.99 / -0.07–0.39 / 2.41–3.28 |
| ES / PIN075_08 | after_15m | 0.26–0.32 / 0.28–0.32 | 0.87–1.02 / 1.03–1.25 | -1.02–-0.83 / 0.00–0.05 / 0.69–0.84 |
| ES / PIN075_08 | after_180m | 0.74–0.83 / 0.79–0.85 | 2.24–2.60 / 2.69–3.71 | -2.29–-1.89 / 0.04–0.19 / 1.84–2.28 |
| ES / PIN075_08 | after_30m | 0.36–0.42 / 0.38–0.47 | 1.21–1.50 / 1.36–1.76 | -1.55–-1.07 / -0.03–0.06 / 0.99–1.23 |
| ES / PIN075_08 | after_60m | 0.49–0.58 / 0.52–0.60 | 1.63–1.80 / 1.86–2.80 | -2.11–-1.36 / -0.02–0.09 / 1.30–1.50 |
| ES / PIN075_08 | to_actual_cash_close | 1.02–1.21 / 1.02–1.23 | 3.62–4.70 / 4.22–4.85 | -3.64–-2.82 / 0.13–0.32 / 3.01–3.31 |
| ES / PIN075_09 | after_15m | 0.19–0.24 / 0.19–0.22 | 0.56–0.76 / 0.65–0.75 | -0.63–-0.48 / 0.00–0.05 / 0.43–0.53 |
| ES / PIN075_09 | after_180m | 0.61–0.71 / 0.55–0.66 | 1.78–2.27 / 2.33–2.92 | -2.33–-1.64 / -0.03–0.17 / 1.43–1.83 |
| ES / PIN075_09 | after_30m | 0.29–0.32 / 0.27–0.30 | 0.83–1.01 / 0.83–1.14 | -0.82–-0.63 / 0.00–0.04 / 0.64–0.80 |
| ES / PIN075_09 | after_60m | 0.36–0.42 / 0.35–0.39 | 1.16–1.37 / 1.05–1.69 | -1.43–-0.85 / -0.05–0.11 / 0.85–1.10 |
| ES / PIN075_09 | to_actual_cash_close | 0.82–0.98 / 0.70–0.85 | 2.54–3.31 / 3.21–3.66 | -3.04–-2.19 / 0.10–0.25 / 2.11–2.93 |
| ES / PIN075_10 | after_15m | 0.25–0.29 / 0.20–0.24 | 0.70–0.84 / 0.85–0.92 | -0.77–-0.59 / 0.00–0.07 / 0.53–0.71 |
| ES / PIN075_10 | after_180m | 0.78–0.93 / 0.70–1.00 | 2.40–3.15 / 3.00–3.65 | -2.80–-2.06 / -0.06–0.32 / 1.92–2.53 |
| ES / PIN075_10 | after_30m | 0.34–0.39 / 0.28–0.35 | 0.97–1.07 / 1.15–1.31 | -1.06–-0.88 / -0.05–0.10 / 0.75–0.93 |
| ES / PIN075_10 | after_60m | 0.42–0.55 / 0.38–0.53 | 1.30–1.56 / 1.56–1.88 | -1.45–-1.18 / -0.07–0.12 / 0.95–1.21 |
| ES / PIN075_10 | to_actual_cash_close | 1.02–1.19 / 0.86–1.16 | 3.32–3.96 / 3.70–5.23 | -4.02–-2.97 / 0.00–0.36 / 2.60–3.24 |
| ES / PIN075_11 | after_15m | 0.13–0.19 / 0.15–0.19 | 0.49–0.63 / 0.61–0.69 | -0.55–-0.46 / -0.03–0.07 / 0.39–0.52 |
| ES / PIN075_11 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN075_11 | after_30m | 0.18–0.29 / 0.22–0.25 | 0.76–0.94 / 0.91–1.06 | -0.80–-0.62 / -0.01–0.07 / 0.55–0.70 |
| ES / PIN075_11 | after_60m | 0.29–0.40 / 0.28–0.37 | 1.03–1.32 / 1.19–1.51 | -1.17–-0.87 / 0.00–0.10 / 0.74–1.11 |
| ES / PIN075_11 | to_actual_cash_close | 0.47–0.63 / 0.39–0.61 | 1.69–2.23 / 1.84–2.69 | -2.05–-1.36 / 0.02–0.16 / 1.35–1.88 |
| ES / PIN075_12 | after_15m | 0.08–0.10 / 0.08–0.12 | 0.28–0.42 / 0.30–0.42 | -0.31–-0.20 / -0.02–0.01 / 0.22–0.28 |
| ES / PIN075_12 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN075_12 | after_30m | 0.10–0.12 / 0.09–0.13 | 0.38–0.52 / 0.32–0.52 | -0.40–-0.24 / 0.00–0.02 / 0.30–0.34 |
| ES / PIN075_12 | after_60m | 0.03–0.03 / 0.31–0.31 | 0.03–0.03 / 0.31–0.31 | -0.10–-0.10 / -0.10–-0.10 / -0.10–-0.10 |
| ES / PIN075_12 | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN076_00_08 | after_15m | 1.00–2.00 / 1.25–1.71 | 5.00–7.80 / 5.00–7.00 | -4.85–-3.00 / 0.00–0.00 / 3.00–5.50 |
| ES / PIN076_00_08 | after_180m | 6.20–8.00 / 5.66–9.42 | 24.00–35.89 / 23.03–37.85 | -27.90–-14.18 / 0.00–1.00 / 18.00–25.83 |
| ES / PIN076_00_08 | after_30m | 1.67–2.38 / 2.00–2.25 | 7.00–10.50 / 7.37–10.90 | -7.93–-5.00 / 0.00–0.31 / 4.88–7.80 |
| ES / PIN076_00_08 | after_60m | 2.50–3.50 / 2.63–3.50 | 11.00–15.45 / 11.00–16.00 | -11.90–-8.00 / -0.12–1.00 / 8.00–11.22 |
| ES / PIN076_00_08 | to_actual_cash_close | 24.10–48.00 / 20.17–49.00 | 91.75–191.00 / 124.00–251.60 | -184.43–-68.88 / -6.33–10.50 / 72.70–144.00 |
| ES / PIN076_08_0930 | after_15m | 1.24–1.69 / 1.30–1.67 | 4.20–6.40 / 4.94–6.61 | -5.00–-3.80 / -0.14–0.40 / 3.17–4.85 |
| ES / PIN076_08_0930 | after_180m | 7.54–10.93 / 6.33–11.31 | 27.90–42.67 / 32.06–48.70 | -32.81–-23.68 / -1.47–1.08 / 22.09–32.15 |
| ES / PIN076_08_0930 | after_30m | 2.00–3.42 / 1.67–2.79 | 8.00–18.00 / 8.18–19.37 | -14.85–-4.67 / -0.20–0.50 / 5.00–14.40 |
| ES / PIN076_08_0930 | after_60m | 2.60–4.67 / 2.70–4.71 | 12.23–24.75 / 11.35–26.61 | -17.70–-7.80 / -0.67–0.47 / 9.25–21.57 |
| ES / PIN076_08_0930 | to_actual_cash_close | 11.45–19.00 / 11.00–17.73 | 42.73–65.88 / 54.95–79.31 | -61.77–-39.92 / -2.00–4.71 / 31.32–48.38 |
| ES / PIN078_daily_not_combined | after_15m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN078_daily_not_combined | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN078_daily_not_combined | after_30m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN078_daily_not_combined | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PIN078_daily_not_combined | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PM | after_15m | 0.07–0.09 / 0.06–0.11 | 0.25–0.37 / 0.24–0.37 | -0.24–-0.16 / -0.02–0.01 / 0.19–0.24 |
| ES / PM | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / PM | after_30m | 0.08–0.10 / 0.07–0.11 | 0.34–0.40 / 0.26–0.43 | -0.31–-0.20 / 0.00–0.02 / 0.25–0.33 |
| ES / PM | after_60m | 0.01–0.01 / 0.14–0.14 | 0.01–0.01 / 0.14–0.14 | -0.05–-0.05 / -0.05–-0.05 / -0.05–-0.05 |
| ES / PM | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / RTH0930 | after_15m | 0.04–0.05 / 0.04–0.06 | 0.14–0.21 / 0.14–0.22 | -0.15–-0.10 / -0.01–0.00 / 0.10–0.14 |
| ES / RTH0930 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / RTH0930 | after_30m | 0.05–0.06 / 0.04–0.06 | 0.19–0.24 / 0.15–0.28 | -0.17–-0.11 / 0.00–0.01 / 0.14–0.16 |
| ES / RTH0930 | after_60m | 0.01–0.01 / 0.12–0.12 | 0.01–0.01 / 0.12–0.12 | -0.04–-0.04 / -0.04–-0.04 / -0.04–-0.04 |
| ES / RTH0930 | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / RTH_actual | after_15m | 0.04–0.05 / 0.04–0.06 | 0.14–0.21 / 0.14–0.22 | -0.15–-0.10 / -0.01–0.00 / 0.10–0.14 |
| ES / RTH_actual | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / RTH_actual | after_30m | 0.05–0.06 / 0.04–0.06 | 0.19–0.24 / 0.15–0.28 | -0.17–-0.11 / 0.00–0.01 / 0.14–0.16 |
| ES / RTH_actual | after_60m | 0.01–0.01 / 0.12–0.12 | 0.01–0.01 / 0.12–0.12 | -0.04–-0.04 / -0.04–-0.04 / -0.04–-0.04 |
| ES / RTH_actual | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / custom09 | after_15m | 0.08–0.10 / 0.08–0.11 | 0.27–0.31 / 0.29–0.37 | -0.32–-0.24 / -0.02–0.03 / 0.23–0.26 |
| ES / custom09 | after_180m | 0.29–0.37 / 0.25–0.36 | 0.86–1.32 / 1.15–1.49 | -1.11–-0.75 / -0.01–0.14 / 0.75–1.03 |
| ES / custom09 | after_30m | 0.11–0.15 / 0.10–0.15 | 0.36–0.41 / 0.44–0.56 | -0.41–-0.29 / -0.03–0.04 / 0.29–0.34 |
| ES / custom09 | after_60m | 0.16–0.21 / 0.15–0.19 | 0.51–0.62 / 0.63–0.78 | -0.62–-0.45 / -0.02–0.05 / 0.42–0.51 |
| ES / custom09 | to_actual_cash_close | 0.38–0.45 / 0.29–0.46 | 1.09–1.59 / 1.53–1.89 | -1.38–-1.09 / -0.03–0.12 / 0.92–1.23 |
| ES / day00 | after_15m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / day00 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / day00 | after_30m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / day00 | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / day00 | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / futures08 | after_15m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / futures08 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / futures08 | after_30m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / futures08 | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / futures08 | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| ES / lunch | after_15m | 0.20–0.25 / 0.19–0.26 | 0.59–0.84 / 0.70–0.96 | -0.69–-0.55 / 0.00–0.05 / 0.50–0.65 |
| ES / lunch | after_180m | 0.80–0.91 / 0.69–0.90 | 2.98–3.31 / 3.38–4.11 | -3.37–-2.22 / 0.02–0.27 / 2.24–2.52 |
| ES / lunch | after_30m | 0.27–0.34 / 0.27–0.34 | 0.80–1.08 / 0.96–1.29 | -1.05–-0.81 / -0.01–0.09 / 0.60–0.82 |
| ES / lunch | after_60m | 0.41–0.48 / 0.41–0.44 | 1.19–1.73 / 1.59–1.98 | -1.34–-1.26 / 0.00–0.09 / 0.88–1.42 |
| ES / lunch | to_actual_cash_close | 0.80–0.90 / 0.69–0.90 | 2.95–3.29 / 3.29–3.96 | -3.35–-2.26 / 0.03–0.26 / 2.19–2.72 |
| ES / magic_00 | after_15m | 0.24–0.29 / 0.25–0.32 | 0.76–1.24 / 0.77–1.25 | -0.81–-0.54 / 0.00–0.00 / 0.47–0.77 |
| ES / magic_00 | after_180m | 1.27–1.53 / 1.14–1.48 | 4.22–4.70 / 4.80–6.00 | -4.25–-3.26 / -0.08–0.08 / 3.26–3.69 |
| ES / magic_00 | after_30m | 0.30–0.40 / 0.35–0.42 | 1.09–1.32 / 1.24–1.57 | -1.14–-0.90 / -0.03–0.03 / 0.83–1.00 |
| ES / magic_00 | after_60m | 0.47–0.62 / 0.53–0.58 | 1.79–2.37 / 1.84–2.18 | -1.59–-1.21 / -0.03–0.07 / 1.21–1.89 |
| ES / magic_00 | to_actual_cash_close | 3.63–5.77 / 3.12–6.00 | 10.72–20.38 / 13.38–24.70 | -20.55–-11.16 / -0.88–1.75 / 9.90–17.17 |
| ES / magic_01 | after_15m | 0.25–0.30 / 0.29–0.33 | 0.93–1.15 / 1.09–1.30 | -1.03–-0.84 / -0.08–0.03 / 0.70–0.89 |
| ES / magic_01 | after_180m | 1.06–1.31 / 1.03–1.33 | 3.66–4.07 / 3.76–5.03 | -3.46–-2.92 / 0.00–0.22 / 2.59–3.24 |
| ES / magic_01 | after_30m | 0.36–0.42 / 0.37–0.43 | 1.31–1.49 / 1.41–1.62 | -1.33–-0.99 / -0.01–0.08 / 1.02–1.14 |
| ES / magic_01 | after_60m | 0.52–0.60 / 0.50–0.57 | 1.67–2.00 / 1.88–2.22 | -1.88–-1.44 / -0.03–0.09 / 1.25–1.64 |
| ES / magic_01 | to_actual_cash_close | 3.10–4.78 / 2.60–4.31 | 9.07–18.50 / 12.64–17.87 | -14.17–-9.04 / -0.67–1.12 / 7.46–14.03 |
| ES / magic_02 | after_15m | 0.29–0.39 / 0.31–0.39 | 1.06–1.29 / 1.07–1.27 | -0.95–-0.80 / 0.00–0.04 / 0.86–1.07 |
| ES / magic_02 | after_180m | 0.80–1.13 / 0.78–0.98 | 2.77–3.41 / 3.41–3.99 | -3.05–-2.41 / 0.09–0.33 / 2.07–2.76 |
| ES / magic_02 | after_30m | 0.40–0.50 / 0.39–0.54 | 1.43–1.71 / 1.53–2.00 | -1.56–-1.20 / -0.12–0.08 / 1.18–1.37 |
| ES / magic_02 | after_60m | 0.54–0.72 / 0.50–0.68 | 1.88–2.35 / 1.93–2.22 | -1.72–-1.46 / 0.00–0.13 / 1.40–1.83 |
| ES / magic_02 | to_actual_cash_close | 2.22–3.84 / 2.00–3.33 | 6.99–13.08 / 9.52–15.47 | -11.10–-6.39 / -0.05–0.95 / 5.70–10.54 |
| ES / magic_06 | after_15m | 0.21–0.27 / 0.19–0.26 | 0.64–1.00 / 0.74–0.94 | -0.77–-0.53 / 0.00–0.04 / 0.57–0.75 |
| ES / magic_06 | after_180m | 1.02–1.61 / 1.22–1.50 | 3.60–5.91 / 3.84–7.44 | -5.23–-2.70 / -0.05–0.30 / 2.48–4.36 |
| ES / magic_06 | after_30m | 0.31–0.38 / 0.30–0.33 | 0.93–1.32 / 1.07–1.26 | -0.99–-0.83 / -0.03–0.10 / 0.81–0.97 |
| ES / magic_06 | after_60m | 0.44–0.52 / 0.41–0.50 | 1.25–1.77 / 1.53–1.81 | -1.38–-1.04 / -0.06–0.04 / 0.83–1.33 |
| ES / magic_06 | to_actual_cash_close | 2.15–3.05 / 2.12–3.11 | 6.69–11.53 / 9.10–15.29 | -11.03–-5.77 / -0.18–0.66 / 5.72–9.87 |
| ES / magic_07 | after_15m | 0.21–0.29 / 0.20–0.24 | 0.79–0.89 / 0.69–0.93 | -0.64–-0.56 / -0.01–0.05 / 0.58–0.76 |
| ES / magic_07 | after_180m | 1.26–1.65 / 1.32–1.77 | 4.65–6.42 / 4.91–7.47 | -5.53–-3.31 / -0.29–0.28 / 3.07–5.10 |
| ES / magic_07 | after_30m | 0.32–0.50 / 0.32–0.43 | 1.39–2.95 / 1.33–2.41 | -1.75–-0.85 / -0.05–0.08 / 1.02–1.91 |
| ES / magic_07 | after_60m | 0.48–0.74 / 0.47–0.69 | 2.05–3.69 / 1.81–3.55 | -2.34–-1.18 / -0.08–0.09 / 1.42–2.50 |
| ES / magic_07 | to_actual_cash_close | 2.10–2.81 / 1.89–2.82 | 6.30–9.87 / 8.04–12.91 | -9.54–-6.36 / -0.16–0.83 / 4.70–7.97 |
| ES / magic_08 | after_15m | 0.16–0.22 / 0.16–0.21 | 0.59–0.68 / 0.59–0.76 | -0.61–-0.44 / -0.01–0.03 / 0.45–0.54 |
| ES / magic_08 | after_180m | 1.01–1.26 / 0.99–1.25 | 3.68–4.92 / 3.88–5.84 | -4.30–-3.47 / -0.14–0.38 / 2.98–4.34 |
| ES / magic_08 | after_30m | 0.25–0.37 / 0.27–0.33 | 1.00–1.21 / 0.96–1.08 | -0.88–-0.64 / -0.04–0.11 / 0.74–1.08 |
| ES / magic_08 | after_60m | 0.61–0.91 / 0.55–0.81 | 2.14–2.63 / 1.91–2.84 | -1.99–-1.38 / -0.05–0.25 / 1.63–2.27 |
| ES / magic_08 | to_actual_cash_close | 1.51–1.73 / 1.38–1.68 | 5.28–6.46 / 7.07–7.94 | -6.35–-5.04 / -0.10–0.54 / 4.21–5.29 |
| ES / magic_23 | after_15m | 0.18–0.22 / 0.18–0.21 | 0.73–0.92 / 0.71–0.85 | -0.62–-0.44 / 0.00–0.04 / 0.45–0.63 |
| ES / magic_23 | after_180m | 0.88–1.14 / 0.84–1.19 | 3.11–3.88 / 3.56–3.96 | -3.04–-2.28 / 0.00–0.09 / 2.27–3.11 |
| ES / magic_23 | after_30m | 0.25–0.32 / 0.27–0.29 | 0.88–1.29 / 0.91–1.32 | -0.87–-0.62 / -0.02–0.03 / 0.65–0.90 |
| ES / magic_23 | after_60m | 0.38–0.45 / 0.36–0.41 | 1.35–1.94 / 1.46–1.63 | -1.25–-1.10 / 0.00–0.11 / 1.05–1.44 |
| ES / magic_23 | to_actual_cash_close | 3.62–6.00 / 3.48–5.75 | 11.95–21.10 / 14.66–24.41 | -19.62–-11.22 / -0.80–1.34 / 9.56–17.96 |
| ES / prior_RTH_open_observed | after_15m | 0.10–0.14 / 0.09–0.14 | 0.35–0.41 / 0.34–0.50 | -0.37–-0.28 / -0.02–0.04 / 0.26–0.33 |
| ES / prior_RTH_open_observed | after_180m | 0.27–0.32 / 0.25–0.33 | 0.86–1.10 / 1.30–1.51 | -1.19–-0.92 / -0.01–0.07 / 0.66–0.83 |
| ES / prior_RTH_open_observed | after_30m | 0.13–0.18 / 0.12–0.18 | 0.50–0.56 / 0.54–0.65 | -0.56–-0.41 / -0.02–0.04 / 0.37–0.46 |
| ES / prior_RTH_open_observed | after_60m | 0.19–0.23 / 0.18–0.24 | 0.61–0.70 / 0.73–1.07 | -0.77–-0.54 / -0.02–0.10 / 0.48–0.56 |
| ES / prior_RTH_open_observed | to_actual_cash_close | 0.41–0.46 / 0.35–0.44 | 1.32–1.56 / 1.75–1.87 | -1.45–-1.21 / -0.02–0.12 / 0.96–1.34 |
| ES / prior_RTH_preopen | after_15m | 0.11–0.14 / 0.09–0.14 | 0.33–0.44 / 0.40–0.52 | -0.37–-0.31 / -0.02–0.03 / 0.28–0.35 |
| ES / prior_RTH_preopen | after_180m | 0.28–0.33 / 0.27–0.34 | 0.91–1.12 / 1.28–1.72 | -1.12–-0.89 / -0.01–0.06 / 0.68–0.89 |
| ES / prior_RTH_preopen | after_30m | 0.14–0.19 / 0.12–0.18 | 0.47–0.61 / 0.52–0.71 | -0.51–-0.40 / 0.00–0.04 / 0.34–0.44 |
| ES / prior_RTH_preopen | after_60m | 0.19–0.25 / 0.18–0.23 | 0.68–0.77 / 0.76–1.02 | -0.77–-0.53 / 0.00–0.06 / 0.52–0.57 |
| ES / prior_RTH_preopen | common_1001_to_actual_cash_close | 0.36–0.40 / 0.35–0.40 | 1.16–1.47 / 1.57–1.80 | -1.56–-1.17 / 0.04–0.10 / 0.91–1.18 |
| ES / prior_RTH_preopen | prefix_15m_to_actual_cash_close | 0.39–0.45 / 0.35–0.42 | 1.21–1.49 / 1.54–1.87 | -1.62–-1.20 / 0.02–0.12 / 0.91–1.25 |
| ES / prior_RTH_preopen | prefix_30m_to_actual_cash_close | 0.36–0.41 / 0.35–0.41 | 1.16–1.49 / 1.53–1.79 | -1.51–-1.15 / 0.05–0.11 / 0.92–1.19 |
| ES / prior_RTH_preopen | prefix_60m_to_actual_cash_close | 0.31–0.40 / 0.29–0.38 | 1.09–1.41 / 1.39–1.62 | -1.29–-1.02 / 0.01–0.08 / 0.86–1.13 |
| ES / prior_RTH_preopen | to_actual_cash_close | 0.40–0.45 / 0.36–0.45 | 1.29–1.51 / 1.80–1.87 | -1.57–-1.24 / -0.01–0.13 / 1.02–1.26 |
| ES / turn_earlier | after_15m | 0.42–0.45 / 0.37–0.47 | 1.22–1.54 / 1.35–1.63 | -1.45–-1.03 / -0.00–0.10 / 1.03–1.31 |
| ES / turn_earlier | after_180m | 1.09–1.38 / 0.97–1.34 | 2.95–4.42 / 4.19–5.51 | -3.94–-2.73 / -0.16–0.39 / 2.56–3.50 |
| ES / turn_earlier | after_30m | 0.57–0.67 / 0.52–0.71 | 1.86–2.08 / 1.82–2.41 | -1.87–-1.31 / -0.11–0.18 / 1.42–1.79 |
| ES / turn_earlier | after_60m | 0.79–0.95 / 0.68–0.94 | 2.23–2.87 / 2.64–3.37 | -2.72–-2.07 / -0.06–0.33 / 1.76–2.44 |
| ES / turn_earlier | common_1001_to_actual_cash_close | 1.28–1.77 / 1.41–1.67 | 4.06–5.77 / 5.33–8.10 | -6.06–-3.90 / 0.20–0.42 / 3.41–5.17 |
| ES / turn_earlier | to_actual_cash_close | 1.45–1.85 / 1.36–1.74 | 4.43–6.06 / 5.29–8.67 | -6.04–-4.04 / 0.19–0.56 / 3.46–5.24 |
| ES / turn_later | after_15m | 0.48–0.63 / 0.51–0.65 | 1.52–1.99 / 1.82–2.32 | -2.00–-1.41 / -0.03–0.03 / 1.24–1.62 |
| ES / turn_later | after_180m | 1.29–1.53 / 1.34–1.55 | 3.94–5.20 / 5.43–7.65 | -5.05–-3.87 / -0.09–0.37 / 3.00–4.26 |
| ES / turn_later | after_30m | 0.66–0.79 / 0.64–0.83 | 2.15–2.63 / 2.73–3.36 | -2.55–-2.04 / 0.03–0.22 / 1.75–2.07 |
| ES / turn_later | after_60m | 0.78–1.00 / 0.91–1.17 | 2.82–3.58 / 3.72–4.60 | -3.54–-2.79 / 0.01–0.11 / 2.23–2.74 |
| ES / turn_later | common_1001_to_actual_cash_close | 1.78–2.17 / 1.79–2.23 | 5.72–7.87 / 7.90–10.74 | -6.88–-4.95 / 0.23–0.52 / 4.83–6.73 |
| ES / turn_later | to_actual_cash_close | 1.78–2.17 / 1.79–2.23 | 5.72–7.87 / 7.90–10.74 | -6.88–-4.95 / 0.23–0.52 / 4.83–6.73 |
| ES / turn_source | after_15m | 0.48–0.60 / 0.39–0.53 | 1.45–1.83 / 1.54–2.01 | -1.69–-1.31 / -0.05–0.15 / 1.19–1.46 |
| ES / turn_source | after_180m | 1.20–1.50 / 1.11–1.49 | 3.71–4.80 / 4.95–5.80 | -4.90–-3.59 / 0.01–0.41 / 3.17–3.95 |
| ES / turn_source | after_30m | 0.69–0.80 / 0.60–0.73 | 1.99–2.30 / 2.15–2.93 | -2.38–-1.63 / -0.03–0.21 / 1.58–1.99 |
| ES / turn_source | after_60m | 0.86–1.09 / 0.78–1.07 | 2.73–3.32 / 3.02–4.20 | -3.28–-2.58 / -0.06–0.33 / 2.07–2.73 |
| ES / turn_source | common_1001_to_actual_cash_close | 1.54–2.01 / 1.60–2.06 | 5.46–7.27 / 6.81–8.67 | -6.93–-5.17 / 0.17–0.52 / 4.35–6.11 |
| ES / turn_source | to_actual_cash_close | 1.69–2.19 / 1.52–2.10 | 5.79–7.47 / 6.68–8.78 | -7.30–-4.85 / 0.33–0.45 / 4.75–6.36 |
| NQ / AM | after_15m | 0.08–0.10 / 0.08–0.10 | 0.26–0.29 / 0.30–0.40 | -0.30–-0.24 / -0.03–0.02 / 0.20–0.25 |
| NQ / AM | after_180m | 0.27–0.35 / 0.22–0.32 | 0.84–1.13 / 1.07–1.41 | -1.10–-0.66 / -0.02–0.12 / 0.69–0.96 |
| NQ / AM | after_30m | 0.09–0.14 / 0.11–0.15 | 0.37–0.40 / 0.42–0.59 | -0.42–-0.27 / -0.02–0.03 / 0.29–0.33 |
| NQ / AM | after_60m | 0.14–0.19 / 0.15–0.19 | 0.49–0.63 / 0.58–0.74 | -0.66–-0.38 / -0.04–0.05 / 0.39–0.53 |
| NQ / AM | to_actual_cash_close | 0.33–0.41 / 0.25–0.38 | 1.08–1.37 / 1.30–1.44 | -1.20–-0.95 / -0.02–0.11 / 0.95–1.12 |
| NQ / Asia19 | after_15m | 0.09–0.12 / 0.11–0.12 | 0.34–0.45 / 0.37–0.46 | -0.35–-0.27 / -0.02–0.00 / 0.26–0.36 |
| NQ / Asia19 | after_180m | 0.37–0.59 / 0.33–0.48 | 1.21–1.59 / 1.42–1.77 | -1.30–-1.01 / 0.02–0.12 / 0.83–1.25 |
| NQ / Asia19 | after_30m | 0.14–0.16 / 0.13–0.16 | 0.41–0.59 / 0.45–0.62 | -0.47–-0.30 / -0.01–0.04 / 0.32–0.44 |
| NQ / Asia19 | after_60m | 0.18–0.22 / 0.17–0.20 | 0.67–0.82 / 0.61–0.84 | -0.62–-0.41 / 0.00–0.04 / 0.51–0.61 |
| NQ / Asia19 | to_actual_cash_close | 1.17–1.98 / 0.97–1.77 | 3.51–7.69 / 4.56–6.74 | -5.74–-3.52 / -0.32–0.49 / 2.77–6.72 |
| NQ / Asia20 | after_15m | 0.10–0.12 / 0.12–0.14 | 0.39–0.47 / 0.40–0.49 | -0.40–-0.31 / -0.02–0.00 / 0.27–0.39 |
| NQ / Asia20 | after_180m | 0.38–0.61 / 0.37–0.52 | 1.26–1.72 / 1.59–1.94 | -1.40–-1.16 / 0.03–0.13 / 0.94–1.39 |
| NQ / Asia20 | after_30m | 0.15–0.17 / 0.14–0.18 | 0.45–0.67 / 0.54–0.72 | -0.57–-0.35 / -0.01–0.05 / 0.37–0.51 |
| NQ / Asia20 | after_60m | 0.20–0.25 / 0.20–0.22 | 0.68–0.85 / 0.70–0.92 | -0.74–-0.46 / 0.00–0.04 / 0.51–0.70 |
| NQ / Asia20 | prefix_15m_to_actual_cash_close | 1.30–2.13 / 1.10–1.94 | 3.56–7.67 / 5.14–7.25 | -5.90–-3.60 / -0.23–0.57 / 2.97–6.72 |
| NQ / Asia20 | prefix_30m_to_actual_cash_close | 1.26–2.11 / 1.11–1.91 | 3.62–7.74 / 5.08–7.48 | -6.07–-3.72 / -0.24–0.41 / 2.87–6.83 |
| NQ / Asia20 | prefix_60m_to_actual_cash_close | 1.21–2.05 / 1.11–1.92 | 3.51–7.71 / 5.25–7.18 | -6.17–-3.68 / -0.29–0.48 / 2.93–6.72 |
| NQ / Asia20 | to_actual_cash_close | 1.28–2.11 / 1.09–1.92 | 3.74–7.80 / 5.22–7.54 | -5.97–-3.64 / -0.32–0.52 / 3.02–6.83 |
| NQ / JTR_fixed_01 | after_15m | 0.21–0.26 / 0.25–0.29 | 0.82–1.05 / 0.88–1.33 | -1.03–-0.67 / -0.03–0.03 / 0.58–0.81 |
| NQ / JTR_fixed_01 | after_180m | 0.73–0.94 / 0.69–0.87 | 2.45–3.24 / 2.65–4.11 | -2.66–-1.72 / -0.10–0.25 / 1.79–2.61 |
| NQ / JTR_fixed_01 | after_30m | 0.29–0.35 / 0.32–0.38 | 1.11–1.48 / 1.24–1.72 | -1.30–-0.92 / -0.03–0.07 / 0.90–1.10 |
| NQ / JTR_fixed_01 | after_60m | 0.48–0.51 / 0.48–0.56 | 1.67–2.01 / 1.79–2.29 | -1.87–-1.21 / -0.02–0.13 / 1.19–1.58 |
| NQ / JTR_fixed_01 | to_actual_cash_close | 3.74–5.24 / 3.37–4.94 | 11.42–20.94 / 13.92–21.58 | -19.74–-10.05 / -0.71–1.19 / 10.26–17.11 |
| NQ / JTR_fixed_02 | after_15m | 0.27–0.33 / 0.28–0.34 | 0.88–1.24 / 1.07–1.41 | -0.98–-0.69 / -0.05–0.04 / 0.60–0.91 |
| NQ / JTR_fixed_02 | after_180m | 1.65–1.91 / 1.40–2.05 | 5.18–7.17 / 5.33–9.12 | -6.36–-4.01 / -0.03–0.45 / 3.86–5.93 |
| NQ / JTR_fixed_02 | after_30m | 0.39–0.47 / 0.37–0.48 | 1.38–2.02 / 1.51–2.01 | -1.39–-1.12 / -0.11–0.05 / 0.83–1.67 |
| NQ / JTR_fixed_02 | after_60m | 0.64–0.79 / 0.64–0.75 | 2.14–2.99 / 2.55–3.47 | -2.77–-1.62 / -0.09–0.16 / 1.67–2.13 |
| NQ / JTR_fixed_02 | to_actual_cash_close | 6.00–9.00 / 5.33–8.84 | 19.93–41.30 / 21.22–42.22 | -32.97–-14.70 / -1.39–2.47 / 16.22–32.48 |
| NQ / JTR_fixed_03 | after_15m | 0.23–0.27 / 0.24–0.27 | 0.77–1.08 / 0.81–1.03 | -0.79–-0.60 / 0.00–0.03 / 0.63–0.88 |
| NQ / JTR_fixed_03 | after_180m | 0.71–0.81 / 0.68–0.87 | 2.43–3.02 / 2.80–3.33 | -2.52–-1.85 / 0.03–0.09 / 2.06–2.51 |
| NQ / JTR_fixed_03 | after_30m | 0.33–0.37 / 0.31–0.38 | 1.10–1.38 / 1.07–1.24 | -0.98–-0.72 / -0.01–0.08 / 0.91–0.97 |
| NQ / JTR_fixed_03 | after_60m | 0.51–0.56 / 0.45–0.57 | 1.78–2.13 / 1.73–2.02 | -1.57–-1.33 / 0.01–0.09 / 1.44–1.84 |
| NQ / JTR_fixed_03 | to_actual_cash_close | 2.64–3.56 / 2.61–3.26 | 8.32–12.80 / 9.06–13.92 | -11.42–-7.13 / -0.36–0.92 / 6.81–10.66 |
| NQ / JTR_fixed_04 | after_15m | 0.12–0.14 / 0.12–0.14 | 0.35–0.43 / 0.39–0.45 | -0.33–-0.26 / -0.01–0.02 / 0.24–0.32 |
| NQ / JTR_fixed_04 | after_180m | 0.76–0.97 / 0.81–1.02 | 2.64–3.69 / 3.13–4.71 | -3.42–-2.63 / -0.11–0.25 / 2.22–2.97 |
| NQ / JTR_fixed_04 | after_30m | 0.19–0.26 / 0.22–0.23 | 0.69–0.79 / 0.71–0.79 | -0.62–-0.51 / -0.00–0.05 / 0.54–0.66 |
| NQ / JTR_fixed_04 | after_60m | 0.48–0.68 / 0.49–0.62 | 1.67–2.01 / 1.67–2.24 | -1.71–-1.32 / -0.06–0.11 / 1.44–1.80 |
| NQ / JTR_fixed_04 | common_1001_to_actual_cash_close | 0.93–1.12 / 0.89–1.17 | 2.83–3.97 / 4.03–4.98 | -3.81–-3.15 / 0.06–0.28 / 2.60–3.20 |
| NQ / JTR_fixed_04 | prefix_15m_to_actual_cash_close | 1.10–1.25 / 1.02–1.25 | 3.87–4.69 / 5.00–5.91 | -4.39–-3.63 / -0.12–0.37 / 3.24–4.03 |
| NQ / JTR_fixed_04 | prefix_30m_to_actual_cash_close | 1.03–1.31 / 1.06–1.23 | 3.86–4.51 / 4.71–5.66 | -4.57–-3.46 / -0.19–0.48 / 3.10–3.87 |
| NQ / JTR_fixed_04 | prefix_60m_to_actual_cash_close | 0.93–1.12 / 0.89–1.17 | 2.83–3.97 / 4.03–4.98 | -3.81–-3.15 / 0.06–0.28 / 2.60–3.20 |
| NQ / JTR_fixed_04 | to_actual_cash_close | 1.07–1.28 / 1.10–1.27 | 3.84–4.57 / 5.06–5.93 | -4.53–-3.63 / -0.14–0.33 / 3.39–3.93 |
| NQ / JTR_fixed_04__shift_+10m | after_15m | 0.11–0.13 / 0.10–0.14 | 0.34–0.40 / 0.38–0.45 | -0.32–-0.25 / -0.02–0.04 / 0.24–0.32 |
| NQ / JTR_fixed_04__shift_+10m | after_180m | 0.77–0.98 / 0.82–1.02 | 2.75–3.58 / 3.23–4.45 | -3.23–-2.63 / -0.08–0.21 / 2.32–3.13 |
| NQ / JTR_fixed_04__shift_+10m | after_30m | 0.33–0.47 / 0.32–0.43 | 1.10–1.60 / 1.21–1.67 | -1.34–-0.91 / -0.12–0.13 / 0.80–1.27 |
| NQ / JTR_fixed_04__shift_+10m | after_60m | 0.51–0.69 / 0.50–0.66 | 1.97–2.28 / 1.97–2.35 | -1.99–-1.54 / -0.10–0.11 / 1.38–2.01 |
| NQ / JTR_fixed_04__shift_+10m | common_1001_to_actual_cash_close | 0.93–1.07 / 0.88–1.12 | 2.85–4.43 / 4.05–4.88 | -3.40–-3.07 / 0.06–0.28 / 2.63–3.78 |
| NQ / JTR_fixed_04__shift_+10m | to_actual_cash_close | 1.07–1.24 / 1.07–1.24 | 3.96–4.38 / 4.82–5.85 | -4.19–-3.53 / -0.11–0.37 / 3.40–3.83 |
| NQ / JTR_fixed_04__shift_-10m | after_15m | 0.12–0.15 / 0.12–0.14 | 0.40–0.44 / 0.41–0.50 | -0.40–-0.33 / -0.00–0.01 / 0.31–0.34 |
| NQ / JTR_fixed_04__shift_-10m | after_180m | 0.76–1.00 / 0.83–1.05 | 2.76–3.52 / 3.03–4.79 | -3.47–-2.42 / -0.13–0.20 / 2.35–2.86 |
| NQ / JTR_fixed_04__shift_-10m | after_30m | 0.17–0.19 / 0.15–0.19 | 0.55–0.60 / 0.58–0.74 | -0.58–-0.43 / -0.00–0.03 / 0.41–0.51 |
| NQ / JTR_fixed_04__shift_-10m | after_60m | 0.44–0.62 / 0.42–0.55 | 1.42–1.80 / 1.54–2.09 | -1.53–-1.28 / -0.10–0.11 / 1.04–1.47 |
| NQ / JTR_fixed_04__shift_-10m | common_1001_to_actual_cash_close | 0.96–1.13 / 0.92–1.17 | 2.80–4.19 / 4.20–5.02 | -3.81–-3.15 / 0.06–0.30 / 2.60–3.15 |
| NQ / JTR_fixed_04__shift_-10m | to_actual_cash_close | 1.02–1.35 / 1.02–1.34 | 3.90–4.90 / 5.06–6.02 | -4.67–-3.58 / -0.18–0.39 / 3.42–4.16 |
| NQ / JTR_fixed_05 | after_15m | 0.21–0.27 / 0.23–0.29 | 0.65–0.88 / 0.83–1.09 | -0.85–-0.66 / -0.02–0.04 / 0.55–0.75 |
| NQ / JTR_fixed_05 | after_180m | 0.59–0.72 / 0.59–0.70 | 1.75–2.38 / 2.20–3.00 | -2.57–-1.68 / -0.03–0.17 / 1.42–1.90 |
| NQ / JTR_fixed_05 | after_30m | 0.31–0.38 / 0.33–0.39 | 0.90–1.22 / 1.08–1.33 | -1.11–-0.86 / 0.00–0.06 / 0.73–1.06 |
| NQ / JTR_fixed_05 | after_60m | 0.40–0.50 / 0.44–0.50 | 1.14–1.44 / 1.54–2.00 | -1.64–-1.21 / 0.02–0.07 / 0.90–1.19 |
| NQ / JTR_fixed_05 | to_actual_cash_close | 0.80–0.96 / 0.77–0.93 | 2.21–3.10 / 3.38–3.85 | -3.10–-2.21 / 0.03–0.24 / 1.85–2.57 |
| NQ / JTR_fixed_06 | after_15m | 0.24–0.29 / 0.24–0.29 | 0.75–0.95 / 0.79–1.12 | -0.98–-0.67 / -0.00–0.05 / 0.55–0.82 |
| NQ / JTR_fixed_06 | after_180m | 0.63–0.77 / 0.69–0.77 | 2.03–2.56 / 2.18–3.20 | -2.07–-1.78 / -0.08–0.21 / 1.76–2.08 |
| NQ / JTR_fixed_06 | after_30m | 0.32–0.36 / 0.35–0.38 | 0.95–1.42 / 1.13–1.45 | -1.14–-0.88 / -0.05–0.03 / 0.76–1.00 |
| NQ / JTR_fixed_06 | after_60m | 0.42–0.47 / 0.45–0.54 | 1.37–1.62 / 1.48–2.33 | -1.63–-1.15 / -0.01–0.07 / 1.14–1.34 |
| NQ / JTR_fixed_06 | to_actual_cash_close | 0.79–1.07 / 0.83–1.07 | 3.24–3.57 / 3.15–3.95 | -2.98–-2.36 / -0.06–0.39 / 2.65–2.76 |
| NQ / JTR_fixed_07 | after_15m | 0.27–0.31 / 0.26–0.31 | 0.82–1.01 / 0.85–1.07 | -0.76–-0.69 / 0.01–0.07 / 0.61–0.77 |
| NQ / JTR_fixed_07 | after_180m | 0.98–1.19 / 0.89–1.08 | 2.86–4.31 / 3.74–4.70 | -3.60–-2.69 / 0.10–0.25 / 2.46–3.66 |
| NQ / JTR_fixed_07 | after_30m | 0.37–0.42 / 0.34–0.42 | 1.05–1.38 / 1.32–1.59 | -1.18–-0.99 / -0.03–0.12 / 0.85–1.23 |
| NQ / JTR_fixed_07 | after_60m | 0.54–0.62 / 0.51–0.63 | 1.51–2.11 / 1.89–2.28 | -1.76–-1.32 / 0.07–0.14 / 1.33–1.70 |
| NQ / JTR_fixed_07 | to_actual_cash_close | 1.06–1.30 / 0.93–1.19 | 3.38–4.31 / 4.13–5.09 | -3.94–-3.20 / 0.13–0.33 / 2.74–3.41 |
| NQ / JTR_fixed_08 | after_15m | 0.29–0.37 / 0.31–0.33 | 0.92–1.04 / 0.96–1.27 | -0.94–-0.70 / -0.01–0.07 / 0.68–0.92 |
| NQ / JTR_fixed_08 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / JTR_fixed_08 | after_30m | 0.46–0.57 / 0.50–0.63 | 1.45–1.99 / 1.47–2.17 | -1.57–-1.00 / -0.10–0.04 / 1.20–1.66 |
| NQ / JTR_fixed_08 | after_60m | 0.53–0.69 / 0.56–0.70 | 2.01–2.43 / 1.77–2.75 | -2.34–-1.43 / -0.07–0.09 / 1.62–2.00 |
| NQ / JTR_fixed_08 | to_actual_cash_close | 0.45–0.54 / 0.50–0.61 | 1.42–1.98 / 1.46–2.09 | -1.66–-1.09 / -0.08–0.10 / 1.23–1.73 |
| NQ / JTR_fixed_EST_sensitivity_01 | after_15m | 0.27–0.34 / 0.29–0.35 | 1.02–1.32 / 1.12–1.36 | -0.95–-0.83 / -0.03–0.07 / 0.71–0.88 |
| NQ / JTR_fixed_EST_sensitivity_01 | after_180m | 0.70–0.89 / 0.66–0.87 | 2.99–3.19 / 3.14–3.42 | -2.38–-2.02 / -0.05–0.28 / 2.09–2.49 |
| NQ / JTR_fixed_EST_sensitivity_01 | after_30m | 0.38–0.46 / 0.38–0.48 | 1.42–2.10 / 1.48–1.70 | -1.47–-1.10 / 0.01–0.08 / 1.10–1.77 |
| NQ / JTR_fixed_EST_sensitivity_01 | after_60m | 0.50–0.61 / 0.46–0.63 | 1.81–2.32 / 2.05–2.38 | -1.90–-1.55 / -0.02–0.16 / 1.31–1.98 |
| NQ / JTR_fixed_EST_sensitivity_01 | to_actual_cash_close | 3.86–6.06 / 3.33–5.87 | 10.42–23.74 / 15.80–22.80 | -19.89–-10.59 / -0.40–1.33 / 9.18–20.02 |
| NQ / JTR_fixed_EST_sensitivity_02 | after_15m | 0.27–0.32 / 0.28–0.31 | 1.04–1.27 / 1.08–1.35 | -0.97–-0.75 / 0.00–0.04 / 0.74–0.96 |
| NQ / JTR_fixed_EST_sensitivity_02 | after_180m | 1.50–1.85 / 1.30–1.77 | 4.53–5.84 / 4.94–6.57 | -4.87–-3.78 / 0.11–0.42 / 3.40–4.53 |
| NQ / JTR_fixed_EST_sensitivity_02 | after_30m | 0.41–0.47 / 0.41–0.48 | 1.55–1.82 / 1.38–2.06 | -1.49–-1.00 / -0.09–0.07 / 1.04–1.47 |
| NQ / JTR_fixed_EST_sensitivity_02 | after_60m | 0.62–0.72 / 0.58–0.79 | 2.59–2.89 / 2.40–3.55 | -2.62–-1.81 / -0.09–0.20 / 1.82–2.48 |
| NQ / JTR_fixed_EST_sensitivity_02 | to_actual_cash_close | 5.04–7.65 / 3.72–6.95 | 15.65–29.57 / 21.49–28.88 | -24.59–-16.52 / -1.15–1.95 / 12.08–25.87 |
| NQ / JTR_fixed_EST_sensitivity_03 | after_15m | 0.22–0.27 / 0.22–0.25 | 0.78–1.02 / 0.86–0.94 | -0.76–-0.62 / -0.01–0.02 / 0.64–0.76 |
| NQ / JTR_fixed_EST_sensitivity_03 | after_180m | 0.73–0.85 / 0.72–0.82 | 2.40–2.99 / 2.85–3.65 | -2.53–-2.03 / 0.06–0.14 / 1.98–2.27 |
| NQ / JTR_fixed_EST_sensitivity_03 | after_30m | 0.32–0.39 / 0.28–0.37 | 1.02–1.36 / 1.12–1.52 | -1.18–-0.74 / -0.01–0.10 / 0.81–1.04 |
| NQ / JTR_fixed_EST_sensitivity_03 | after_60m | 0.44–0.54 / 0.40–0.53 | 1.68–1.80 / 1.58–2.23 | -1.74–-1.04 / -0.01–0.09 / 1.27–1.40 |
| NQ / JTR_fixed_EST_sensitivity_03 | to_actual_cash_close | 2.70–3.57 / 2.61–3.32 | 9.49–12.23 / 10.26–14.10 | -11.85–-7.36 / -0.60–0.92 / 7.77–10.79 |
| NQ / JTR_fixed_EST_sensitivity_04 | after_15m | 0.15–0.18 / 0.16–0.19 | 0.48–0.58 / 0.59–0.76 | -0.54–-0.41 / -0.03–0.02 / 0.37–0.51 |
| NQ / JTR_fixed_EST_sensitivity_04 | after_180m | 0.52–0.63 / 0.58–0.71 | 1.81–2.41 / 2.28–2.89 | -2.13–-1.76 / -0.04–0.15 / 1.39–2.02 |
| NQ / JTR_fixed_EST_sensitivity_04 | after_30m | 0.22–0.28 / 0.24–0.27 | 0.65–0.78 / 0.80–0.97 | -0.83–-0.62 / -0.01–0.05 / 0.54–0.70 |
| NQ / JTR_fixed_EST_sensitivity_04 | after_60m | 0.39–0.42 / 0.40–0.47 | 1.22–1.50 / 1.51–1.74 | -1.38–-1.13 / -0.02–0.07 / 0.90–1.04 |
| NQ / JTR_fixed_EST_sensitivity_04 | to_actual_cash_close | 0.70–0.86 / 0.71–0.88 | 2.47–3.25 / 3.15–4.00 | -3.19–-2.30 / 0.02–0.22 / 2.03–2.67 |
| NQ / JTR_fixed_EST_sensitivity_05 | after_15m | 0.24–0.30 / 0.22–0.30 | 0.73–0.97 / 0.91–1.08 | -0.81–-0.62 / -0.01–0.08 / 0.57–0.75 |
| NQ / JTR_fixed_EST_sensitivity_05 | after_180m | 0.68–0.82 / 0.64–0.77 | 1.97–2.43 / 2.50–3.12 | -2.47–-1.79 / -0.10–0.29 / 1.68–2.23 |
| NQ / JTR_fixed_EST_sensitivity_05 | after_30m | 0.34–0.44 / 0.31–0.42 | 0.96–1.23 / 1.22–1.40 | -1.11–-0.83 / -0.01–0.11 / 0.79–0.99 |
| NQ / JTR_fixed_EST_sensitivity_05 | after_60m | 0.45–0.57 / 0.41–0.57 | 1.38–1.70 / 1.68–1.92 | -1.63–-1.15 / 0.03–0.15 / 1.13–1.31 |
| NQ / JTR_fixed_EST_sensitivity_05 | to_actual_cash_close | 0.87–1.07 / 0.84–1.07 | 3.05–3.69 / 3.41–3.98 | -3.28–-2.61 / -0.02–0.39 / 2.58–2.93 |
| NQ / JTR_fixed_EST_sensitivity_06 | after_15m | 0.24–0.30 / 0.25–0.30 | 0.80–0.96 / 0.93–1.01 | -0.85–-0.68 / 0.00–0.05 / 0.62–0.87 |
| NQ / JTR_fixed_EST_sensitivity_06 | after_180m | 0.76–0.86 / 0.70–0.88 | 2.45–2.84 / 2.63–3.64 | -2.47–-2.24 / -0.11–0.26 / 1.82–2.32 |
| NQ / JTR_fixed_EST_sensitivity_06 | after_30m | 0.35–0.40 / 0.33–0.39 | 0.96–1.23 / 1.20–1.43 | -1.17–-0.85 / -0.01–0.15 / 0.76–1.02 |
| NQ / JTR_fixed_EST_sensitivity_06 | after_60m | 0.48–0.54 / 0.43–0.58 | 1.37–1.74 / 1.63–2.07 | -1.66–-1.19 / -0.11–0.18 / 1.11–1.49 |
| NQ / JTR_fixed_EST_sensitivity_06 | to_actual_cash_close | 0.95–1.16 / 0.82–1.13 | 3.25–3.83 / 3.60–4.43 | -3.54–-2.64 / -0.11–0.38 / 2.61–3.28 |
| NQ / JTR_fixed_EST_sensitivity_07 | after_15m | 0.26–0.31 / 0.25–0.29 | 0.77–1.08 / 0.89–1.23 | -0.83–-0.65 / 0.01–0.07 / 0.60–0.95 |
| NQ / JTR_fixed_EST_sensitivity_07 | after_180m | 0.90–1.20 / 0.84–1.11 | 2.67–4.41 / 3.57–5.21 | -3.93–-2.55 / -0.04–0.29 / 2.33–3.61 |
| NQ / JTR_fixed_EST_sensitivity_07 | after_30m | 0.37–0.44 / 0.36–0.46 | 1.16–1.71 / 1.34–1.94 | -1.57–-1.05 / 0.00–0.04 / 0.94–1.18 |
| NQ / JTR_fixed_EST_sensitivity_07 | after_60m | 0.56–0.64 / 0.56–0.67 | 1.82–2.24 / 2.03–2.68 | -1.83–-1.47 / 0.04–0.18 / 1.35–1.63 |
| NQ / JTR_fixed_EST_sensitivity_07 | to_actual_cash_close | 1.04–1.23 / 0.89–1.12 | 3.41–4.25 / 4.31–4.90 | -4.08–-3.02 / 0.08–0.35 / 2.66–3.31 |
| NQ / JTR_fixed_EST_sensitivity_08 | after_15m | 0.13–0.31 / 0.16–0.32 | 0.65–0.90 / 0.75–1.09 | -0.71–-0.53 / -0.05–0.05 / 0.47–0.80 |
| NQ / JTR_fixed_EST_sensitivity_08 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / JTR_fixed_EST_sensitivity_08 | after_30m | 0.44–0.54 / 0.42–0.63 | 1.47–2.05 / 1.48–2.07 | -1.62–-0.92 / -0.26–0.16 / 1.25–1.94 |
| NQ / JTR_fixed_EST_sensitivity_08 | after_60m | 0.53–0.64 / 0.51–0.70 | 1.82–2.64 / 1.75–2.50 | -1.88–-1.51 / -0.02–0.16 / 1.57–2.43 |
| NQ / JTR_fixed_EST_sensitivity_08 | to_actual_cash_close | 0.43–0.54 / 0.42–0.59 | 1.47–2.02 / 1.47–2.07 | -1.73–-1.10 / -0.21–0.18 / 1.30–1.80 |
| NQ / London02 | after_15m | 0.08–0.12 / 0.08–0.10 | 0.28–0.36 / 0.28–0.36 | -0.26–-0.21 / 0.00–0.03 / 0.22–0.28 |
| NQ / London02 | after_180m | 0.58–0.78 / 0.64–0.82 | 1.99–2.83 / 2.20–3.00 | -2.60–-1.61 / -0.12–0.12 / 1.58–2.36 |
| NQ / London02 | after_30m | 0.14–0.20 / 0.13–0.17 | 0.44–0.94 / 0.47–1.28 | -0.74–-0.33 / -0.02–0.03 / 0.37–0.76 |
| NQ / London02 | after_60m | 0.19–0.27 / 0.18–0.28 | 0.72–1.38 / 0.75–1.80 | -0.92–-0.55 / -0.03–0.05 / 0.58–1.10 |
| NQ / London02 | to_actual_cash_close | 0.85–1.20 / 0.80–1.15 | 3.08–4.34 / 3.45–4.70 | -3.61–-2.40 / -0.17–0.35 / 2.47–3.97 |
| NQ / NY08 | after_15m | 0.04–0.04 / 0.03–0.05 | 0.13–0.21 / 0.14–0.23 | -0.15–-0.10 / -0.01–0.00 / 0.08–0.13 |
| NQ / NY08 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / NY08 | after_30m | 0.04–0.05 / 0.04–0.06 | 0.14–0.30 / 0.17–0.30 | -0.20–-0.10 / -0.00–0.01 / 0.13–0.17 |
| NQ / NY08 | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / NY08 | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / ONS03 | after_15m | 0.09–0.13 / 0.08–0.11 | 0.34–0.41 / 0.36–0.51 | -0.40–-0.24 / 0.00–0.03 / 0.27–0.33 |
| NQ / ONS03 | after_180m | 0.60–0.79 / 0.61–0.77 | 2.05–2.70 / 2.35–2.85 | -2.35–-1.31 / -0.11–0.14 / 1.61–2.21 |
| NQ / ONS03 | after_30m | 0.14–0.18 / 0.12–0.14 | 0.48–0.55 / 0.50–0.69 | -0.55–-0.35 / 0.01–0.03 / 0.34–0.43 |
| NQ / ONS03 | after_60m | 0.20–0.24 / 0.19–0.20 | 0.70–0.78 / 0.71–0.85 | -0.69–-0.47 / 0.00–0.04 / 0.50–0.58 |
| NQ / ONS03 | to_actual_cash_close | 1.14–1.41 / 1.03–1.41 | 3.55–5.11 / 4.51–6.18 | -4.64–-3.26 / -0.20–0.38 / 2.84–4.40 |
| NQ / ONS20 | after_15m | 0.07–0.09 / 0.07–0.08 | 0.24–0.32 / 0.23–0.27 | -0.19–-0.17 / -0.01–0.01 / 0.18–0.23 |
| NQ / ONS20 | after_180m | 0.35–0.40 / 0.31–0.45 | 1.22–1.53 / 1.23–1.72 | -1.44–-0.75 / -0.02–0.08 / 0.93–1.25 |
| NQ / ONS20 | after_30m | 0.09–0.12 / 0.10–0.12 | 0.34–0.50 / 0.37–0.48 | -0.34–-0.27 / -0.01–0.02 / 0.25–0.38 |
| NQ / ONS20 | after_60m | 0.15–0.17 / 0.14–0.17 | 0.50–0.66 / 0.50–0.70 | -0.52–-0.36 / -0.02–0.02 / 0.32–0.50 |
| NQ / ONS20 | to_actual_cash_close | 1.56–2.50 / 1.35–2.32 | 4.09–9.13 / 6.16–10.13 | -7.29–-4.17 / -0.42–0.58 / 3.47–7.53 |
| NQ / OR15 | after_15m | 0.35–0.36 / 0.31–0.42 | 0.95–1.12 / 1.13–1.41 | -1.13–-0.87 / -0.04–0.12 / 0.82–0.92 |
| NQ / OR15 | after_180m | 0.82–0.96 / 0.81–1.04 | 2.31–3.04 / 3.05–3.91 | -2.89–-2.33 / -0.05–0.20 / 1.84–2.60 |
| NQ / OR15 | after_30m | 0.44–0.54 / 0.41–0.61 | 1.29–1.62 / 1.53–2.14 | -1.63–-1.22 / -0.03–0.09 / 1.03–1.33 |
| NQ / OR15 | after_60m | 0.60–0.66 / 0.53–0.74 | 1.69–2.28 / 2.05–2.63 | -2.10–-1.70 / -0.06–0.15 / 1.35–1.92 |
| NQ / OR15 | common_1001_to_actual_cash_close | 1.05–1.28 / 1.03–1.18 | 2.77–4.09 / 4.05–5.21 | -3.95–-2.78 / 0.05–0.30 / 2.30–3.48 |
| NQ / OR15 | prefix_15m_to_actual_cash_close | 1.05–1.28 / 1.03–1.18 | 2.77–4.09 / 4.05–5.21 | -3.95–-2.78 / 0.05–0.30 / 2.30–3.48 |
| NQ / OR15 | prefix_30m_to_actual_cash_close | 0.93–1.17 / 0.96–1.09 | 2.65–3.75 / 3.68–5.13 | -3.70–-2.72 / 0.10–0.34 / 2.26–3.13 |
| NQ / OR15 | prefix_60m_to_actual_cash_close | 0.86–1.09 / 0.84–1.01 | 2.71–3.62 / 3.31–4.35 | -3.10–-2.31 / -0.00–0.40 / 2.24–3.03 |
| NQ / OR15 | to_actual_cash_close | 1.11–1.27 / 1.08–1.25 | 3.08–4.53 / 4.35–5.55 | -4.31–-3.13 / 0.04–0.45 / 2.58–3.58 |
| NQ / OR15__shift_+10m | after_15m | 0.37–0.46 / 0.26–0.43 | 1.14–1.25 / 1.32–1.66 | -1.31–-0.94 / -0.06–0.16 / 0.88–1.02 |
| NQ / OR15__shift_+10m | after_180m | 0.93–1.12 / 0.88–1.00 | 2.69–3.36 / 3.55–4.93 | -4.00–-2.77 / -0.06–0.31 / 2.35–2.88 |
| NQ / OR15__shift_+10m | after_30m | 0.51–0.63 / 0.41–0.53 | 1.49–1.67 / 1.76–2.53 | -1.86–-1.22 / -0.05–0.17 / 1.24–1.41 |
| NQ / OR15__shift_+10m | after_60m | 0.70–0.81 / 0.61–0.75 | 1.87–2.35 / 2.61–3.16 | -2.83–-1.92 / -0.00–0.18 / 1.44–1.95 |
| NQ / OR15__shift_+10m | common_1001_to_actual_cash_close | 1.18–1.45 / 1.15–1.36 | 3.56–4.78 / 5.01–6.33 | -4.93–-3.50 / 0.05–0.34 / 2.96–3.98 |
| NQ / OR15__shift_+10m | to_actual_cash_close | 1.24–1.49 / 1.19–1.39 | 4.00–5.10 / 5.05–6.47 | -5.28–-3.57 / 0.01–0.44 / 3.00–3.95 |
| NQ / OR15__shift_-10m | after_15m | 0.46–0.60 / 0.50–0.58 | 1.38–1.70 / 1.66–1.91 | -1.53–-1.33 / -0.11–0.07 / 1.01–1.46 |
| NQ / OR15__shift_-10m | after_180m | 1.23–1.37 / 1.18–1.47 | 3.41–4.38 / 4.10–5.45 | -4.07–-3.20 / -0.14–0.33 / 2.90–3.79 |
| NQ / OR15__shift_-10m | after_30m | 0.66–0.79 / 0.66–0.82 | 2.00–2.28 / 2.30–2.54 | -2.17–-1.59 / -0.03–0.18 / 1.60–1.94 |
| NQ / OR15__shift_-10m | after_60m | 0.89–1.04 / 0.86–1.01 | 2.53–3.14 / 2.80–3.57 | -2.96–-2.33 / 0.02–0.25 / 2.11–2.73 |
| NQ / OR15__shift_-10m | common_1001_to_actual_cash_close | 1.41–1.64 / 1.37–1.77 | 4.44–5.33 / 4.70–6.34 | -5.06–-3.56 / 0.06–0.41 / 3.70–4.53 |
| NQ / OR15__shift_-10m | to_actual_cash_close | 1.61–1.81 / 1.56–1.94 | 4.75–6.18 / 5.69–6.99 | -5.27–-4.04 / -0.30–0.66 / 4.10–5.11 |
| NQ / OR5 | after_15m | 0.49–0.65 / 0.54–0.66 | 1.50–1.82 / 1.76–2.10 | -1.64–-1.41 / -0.11–0.08 / 1.05–1.56 |
| NQ / OR5 | after_180m | 1.29–1.55 / 1.25–1.51 | 3.93–4.90 / 4.72–6.12 | -5.23–-3.54 / -0.14–0.35 / 2.94–4.13 |
| NQ / OR5 | after_30m | 0.73–0.90 / 0.71–0.93 | 2.07–2.41 / 2.45–2.93 | -2.29–-1.73 / -0.04–0.19 / 1.66–2.00 |
| NQ / OR5 | after_60m | 0.96–1.10 / 0.95–1.17 | 2.64–3.31 / 3.00–3.83 | -3.28–-2.46 / 0.02–0.28 / 2.14–2.81 |
| NQ / OR5 | common_1001_to_actual_cash_close | 1.52–1.86 / 1.52–1.83 | 4.61–6.19 / 5.47–7.23 | -6.14–-3.73 / 0.06–0.43 / 4.03–5.38 |
| NQ / OR5 | to_actual_cash_close | 1.76–2.03 / 1.63–2.02 | 5.15–7.04 / 6.22–8.14 | -5.91–-4.31 / -0.33–0.70 / 4.40–5.78 |
| NQ / OR5__shift_+10m | after_15m | 0.66–0.79 / 0.65–0.78 | 2.11–2.42 / 2.40–2.96 | -2.33–-1.92 / -0.12–0.23 / 1.82–1.99 |
| NQ / OR5__shift_+10m | after_180m | 1.62–1.92 / 1.67–1.90 | 4.94–6.18 / 6.86–7.97 | -5.98–-5.11 / -0.08–0.52 / 3.78–5.05 |
| NQ / OR5__shift_+10m | after_30m | 0.85–1.03 / 0.82–1.17 | 2.92–3.18 / 3.47–4.18 | -3.05–-2.86 / -0.04–0.17 / 2.34–2.51 |
| NQ / OR5__shift_+10m | after_60m | 1.17–1.33 / 1.07–1.49 | 3.61–4.38 / 4.44–5.45 | -4.19–-3.27 / -0.10–0.24 / 3.11–3.55 |
| NQ / OR5__shift_+10m | common_1001_to_actual_cash_close | 2.02–2.50 / 1.94–2.20 | 6.32–8.27 / 8.25–9.31 | -7.08–-5.79 / 0.07–0.60 / 5.79–6.89 |
| NQ / OR5__shift_+10m | to_actual_cash_close | 2.10–2.50 / 2.02–2.43 | 7.19–8.43 / 8.69–10.33 | -7.47–-5.96 / 0.05–1.05 / 5.85–7.21 |
| NQ / OR5__shift_-10m | after_15m | 2.06–2.80 / 1.82–3.09 | 7.13–10.61 / 6.95–11.24 | -8.36–-5.53 / -0.66–1.03 / 5.11–9.68 |
| NQ / OR5__shift_-10m | after_180m | 5.20–6.70 / 4.76–6.99 | 18.58–25.97 / 19.28–27.86 | -20.02–-15.69 / -0.26–1.88 / 14.93–21.14 |
| NQ / OR5__shift_-10m | after_30m | 2.58–3.64 / 2.44–3.81 | 10.72–12.72 / 9.00–13.78 | -10.24–-7.46 / -0.19–0.90 / 8.75–11.37 |
| NQ / OR5__shift_-10m | after_60m | 3.67–4.68 / 3.53–4.63 | 13.75–17.14 / 13.21–19.41 | -13.33–-9.45 / -0.43–1.18 / 11.05–16.02 |
| NQ / OR5__shift_-10m | common_1001_to_actual_cash_close | 6.47–7.34 / 6.22–7.67 | 21.92–25.95 / 23.56–33.67 | -23.54–-17.44 / 0.39–2.14 / 17.65–21.16 |
| NQ / OR5__shift_-10m | to_actual_cash_close | 7.41–8.30 / 6.63–8.40 | 25.19–32.85 / 26.42–34.95 | -27.71–-18.71 / -1.25–2.62 / 19.64–26.88 |
| NQ / OR_activity_1_1 | after_15m | 0.32–0.37 / 0.30–0.38 | 0.93–1.08 / 1.13–1.29 | -1.18–-0.86 / -0.04–0.08 / 0.76–0.85 |
| NQ / OR_activity_1_1 | after_180m | 0.84–0.98 / 0.76–0.93 | 2.30–2.89 / 3.08–3.77 | -3.02–-2.30 / 0.03–0.27 / 1.93–2.46 |
| NQ / OR_activity_1_1 | after_30m | 0.46–0.51 / 0.37–0.55 | 1.32–1.50 / 1.70–1.84 | -1.49–-1.31 / -0.01–0.12 / 1.12–1.27 |
| NQ / OR_activity_1_1 | after_60m | 0.61–0.71 / 0.54–0.69 | 1.59–2.06 / 2.06–2.51 | -1.95–-1.52 / -0.12–0.16 / 1.30–1.58 |
| NQ / OR_activity_1_1 | common_1001_to_actual_cash_close | 1.01–1.22 / 1.01–1.16 | 2.61–3.86 / 3.87–5.11 | -3.84–-2.49 / 0.11–0.30 / 2.30–3.24 |
| NQ / OR_activity_1_1 | to_actual_cash_close | 1.10–1.26 / 0.97–1.26 | 3.06–4.19 / 4.09–5.36 | -4.46–-2.72 / -0.07–0.45 / 2.52–3.23 |
| NQ / OR_activity_1_2 | after_15m | 0.43–0.57 / 0.41–0.51 | 1.28–1.60 / 1.55–1.70 | -1.42–-1.34 / -0.05–0.10 / 0.98–1.33 |
| NQ / OR_activity_1_2 | after_180m | 1.07–1.35 / 1.05–1.28 | 3.14–4.40 / 4.22–5.07 | -3.93–-3.15 / -0.16–0.29 / 2.59–3.84 |
| NQ / OR_activity_1_2 | after_30m | 0.65–0.70 / 0.55–0.76 | 1.92–2.16 / 2.14–2.64 | -2.02–-1.59 / -0.04–0.19 / 1.55–1.86 |
| NQ / OR_activity_1_2 | after_60m | 0.81–0.96 / 0.73–1.00 | 2.44–2.93 / 2.80–3.75 | -2.53–-2.26 / -0.01–0.33 / 1.92–2.55 |
| NQ / OR_activity_1_2 | common_1001_to_actual_cash_close | 1.32–1.66 / 1.34–1.53 | 3.91–5.90 / 4.26–6.98 | -5.69–-3.34 / 0.06–0.40 / 3.34–4.91 |
| NQ / OR_activity_1_2 | to_actual_cash_close | 1.44–1.75 / 1.27–1.71 | 4.39–6.58 / 5.47–6.83 | -5.21–-3.90 / -0.23–0.69 / 3.43–5.49 |
| NQ / OR_activity_3_2 | after_15m | 0.26–0.30 / 0.23–0.30 | 0.74–0.94 / 0.79–1.13 | -0.94–-0.66 / -0.06–0.07 / 0.58–0.74 |
| NQ / OR_activity_3_2 | after_180m | 0.67–0.79 / 0.60–0.72 | 1.93–2.33 / 2.34–3.00 | -2.64–-1.73 / -0.06–0.21 / 1.58–1.92 |
| NQ / OR_activity_3_2 | after_30m | 0.36–0.41 / 0.33–0.40 | 1.00–1.23 / 1.07–1.52 | -1.14–-0.84 / -0.00–0.10 / 0.79–0.95 |
| NQ / OR_activity_3_2 | after_60m | 0.45–0.54 / 0.47–0.58 | 1.23–1.59 / 1.48–1.97 | -1.65–-1.22 / -0.01–0.12 / 1.01–1.32 |
| NQ / OR_activity_3_2 | common_1001_to_actual_cash_close | 0.82–0.96 / 0.83–1.05 | 2.27–3.16 / 3.45–4.15 | -3.24–-2.34 / 0.11–0.26 / 1.88–2.60 |
| NQ / OR_activity_3_2 | to_actual_cash_close | 0.90–0.98 / 0.78–0.97 | 2.38–3.37 / 3.21–4.00 | -3.16–-2.39 / 0.00–0.27 / 1.90–2.73 |
| NQ / PIN015_Asia_UTC | after_15m | 0.11–0.14 / 0.10–0.16 | 0.41–0.51 / 0.44–0.56 | -0.44–-0.34 / -0.02–0.01 / 0.34–0.38 |
| NQ / PIN015_Asia_UTC | after_180m | 0.33–0.52 / 0.30–0.46 | 1.25–1.55 / 1.35–1.67 | -1.20–-0.90 / 0.00–0.06 / 0.99–1.18 |
| NQ / PIN015_Asia_UTC | after_30m | 0.15–0.20 / 0.13–0.24 | 0.50–0.72 / 0.55–0.75 | -0.58–-0.41 / -0.02–0.04 / 0.40–0.56 |
| NQ / PIN015_Asia_UTC | after_60m | 0.20–0.28 / 0.18–0.27 | 0.66–0.95 / 0.74–1.07 | -0.65–-0.50 / 0.01–0.06 / 0.45–0.76 |
| NQ / PIN015_Asia_UTC | to_actual_cash_close | 1.15–1.92 / 0.96–1.65 | 3.27–7.30 / 4.42–6.23 | -5.48–-2.63 / -0.25–0.38 / 2.69–6.05 |
| NQ / PIN015_London_UTC | after_15m | 0.07–0.10 / 0.08–0.10 | 0.29–0.33 / 0.31–0.38 | -0.26–-0.22 / -0.01–0.01 / 0.18–0.26 |
| NQ / PIN015_London_UTC | after_180m | 0.59–0.81 / 0.58–0.77 | 1.95–2.70 / 2.28–3.02 | -2.63–-1.70 / -0.10–0.11 / 1.69–2.29 |
| NQ / PIN015_London_UTC | after_30m | 0.11–0.15 / 0.11–0.14 | 0.38–0.50 / 0.45–0.52 | -0.37–-0.33 / -0.01–0.02 / 0.33–0.38 |
| NQ / PIN015_London_UTC | after_60m | 0.29–0.38 / 0.25–0.34 | 1.00–1.35 / 1.04–1.24 | -1.03–-0.64 / -0.03–0.08 / 0.75–1.06 |
| NQ / PIN015_London_UTC | to_actual_cash_close | 0.85–1.08 / 0.79–1.03 | 2.79–3.91 / 3.47–4.27 | -3.56–-2.55 / -0.16–0.30 / 2.32–3.49 |
| NQ / PIN015_NY_UTC | after_15m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN015_NY_UTC | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN015_NY_UTC | after_30m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN015_NY_UTC | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN015_NY_UTC | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN073_1 | after_15m | 0.23–0.28 / 0.23–0.28 | 0.89–1.03 / 0.86–1.12 | -0.77–-0.66 / -0.01–0.06 / 0.69–0.82 |
| NQ / PIN073_1 | after_180m | 1.11–1.41 / 0.96–1.28 | 3.74–4.91 / 4.16–5.01 | -3.71–-2.96 / 0.06–0.35 / 2.87–3.67 |
| NQ / PIN073_1 | after_30m | 0.39–0.43 / 0.33–0.41 | 1.15–1.60 / 1.21–1.75 | -1.21–-0.98 / -0.04–0.08 / 0.88–1.21 |
| NQ / PIN073_1 | after_60m | 0.65–0.77 / 0.61–0.81 | 2.25–2.72 / 2.67–2.95 | -2.57–-1.86 / -0.08–0.19 / 1.94–2.19 |
| NQ / PIN073_1 | to_actual_cash_close | 3.62–5.29 / 3.23–4.80 | 10.63–18.22 / 14.22–19.84 | -16.17–-10.37 / -0.60–1.02 / 8.86–14.37 |
| NQ / PIN073_2 | after_15m | 0.76–1.05 / 0.78–1.19 | 2.97–3.24 / 2.87–3.81 | -3.07–-2.16 / -0.21–0.24 / 2.02–2.72 |
| NQ / PIN073_2 | after_180m | 1.91–2.29 / 2.06–2.40 | 6.57–7.44 / 7.52–9.49 | -7.28–-5.93 / -0.18–0.75 / 4.79–6.73 |
| NQ / PIN073_2 | after_30m | 1.01–1.32 / 1.02–1.43 | 3.88–4.19 / 3.46–4.65 | -3.74–-3.00 / -0.15–0.25 / 2.80–3.38 |
| NQ / PIN073_2 | after_60m | 1.44–1.69 / 1.55–1.93 | 4.84–5.09 / 5.07–6.08 | -4.97–-3.78 / -0.04–0.41 / 3.47–4.40 |
| NQ / PIN073_2 | to_actual_cash_close | 2.65–3.01 / 2.47–3.06 | 8.27–10.50 / 9.64–12.93 | -9.76–-7.64 / -0.50–0.93 / 6.95–8.74 |
| NQ / PIN073_3 | after_15m | 0.27–0.33 / 0.28–0.34 | 0.88–1.24 / 1.07–1.41 | -0.98–-0.69 / -0.05–0.04 / 0.60–0.91 |
| NQ / PIN073_3 | after_180m | 1.65–1.91 / 1.40–2.05 | 5.18–7.17 / 5.33–9.12 | -6.36–-4.01 / -0.03–0.45 / 3.86–5.93 |
| NQ / PIN073_3 | after_30m | 0.39–0.47 / 0.37–0.48 | 1.38–2.02 / 1.51–2.01 | -1.39–-1.12 / -0.11–0.05 / 0.83–1.67 |
| NQ / PIN073_3 | after_60m | 0.64–0.79 / 0.64–0.75 | 2.14–2.99 / 2.55–3.47 | -2.77–-1.62 / -0.09–0.16 / 1.67–2.13 |
| NQ / PIN073_3 | to_actual_cash_close | 6.00–9.00 / 5.33–8.84 | 19.93–41.30 / 21.22–42.22 | -32.97–-14.70 / -1.39–2.47 / 16.22–32.48 |
| NQ / PIN073_4 | after_15m | 0.26–0.29 / 0.26–0.31 | 0.75–0.96 / 0.88–1.09 | -0.85–-0.68 / -0.00–0.09 / 0.58–0.85 |
| NQ / PIN073_4 | after_180m | 0.79–0.96 / 0.74–1.03 | 2.45–3.09 / 3.06–3.71 | -2.61–-2.42 / -0.08–0.24 / 2.02–2.46 |
| NQ / PIN073_4 | after_30m | 0.36–0.41 / 0.33–0.42 | 1.00–1.28 / 1.20–1.42 | -1.09–-0.96 / 0.01–0.11 / 0.78–1.02 |
| NQ / PIN073_4 | after_60m | 0.48–0.60 / 0.46–0.59 | 1.39–1.90 / 1.66–2.09 | -1.68–-1.19 / -0.07–0.16 / 1.18–1.47 |
| NQ / PIN073_4 | to_actual_cash_close | 1.04–1.25 / 0.89–1.20 | 3.11–3.83 / 4.00–4.20 | -3.59–-2.69 / 0.03–0.35 / 2.61–3.35 |
| NQ / PIN073_5 | after_15m | 0.27–0.34 / 0.27–0.33 | 0.87–1.11 / 0.90–1.23 | -0.86–-0.67 / -0.01–0.06 / 0.75–0.93 |
| NQ / PIN073_5 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN073_5 | after_30m | 0.40–0.49 / 0.39–0.43 | 1.30–1.71 / 1.31–1.56 | -1.17–-0.92 / 0.00–0.17 / 1.03–1.31 |
| NQ / PIN073_5 | after_60m | 0.55–0.70 / 0.55–0.65 | 1.75–2.15 / 2.04–2.23 | -1.70–-1.43 / 0.00–0.10 / 1.24–1.85 |
| NQ / PIN073_5 | to_actual_cash_close | 0.75–0.92 / 0.72–0.84 | 2.36–3.18 / 2.56–3.65 | -2.89–-1.65 / -0.01–0.19 / 1.94–2.82 |
| NQ / PIN074_ref_00 | after_15m | 1.40–1.53 / 1.33–1.71 | 5.17–7.28 / 5.40–7.08 | -4.12–-3.61 / -0.13–0.22 / 3.38–5.35 |
| NQ / PIN074_ref_00 | after_180m | 6.90–7.77 / 5.79–9.00 | 26.29–33.19 / 23.77–34.87 | -26.80–-14.93 / -0.30–1.06 / 18.41–24.20 |
| NQ / PIN074_ref_00 | after_30m | 1.94–2.40 / 1.86–2.40 | 6.93–11.29 / 7.67–9.10 | -6.50–-5.53 / -0.16–0.33 / 5.23–8.86 |
| NQ / PIN074_ref_00 | after_60m | 2.80–3.44 / 2.68–3.37 | 10.11–17.19 / 10.89–12.51 | -10.31–-7.54 / -0.27–0.60 / 7.00–11.24 |
| NQ / PIN074_ref_00 | to_actual_cash_close | 27.18–45.00 / 22.88–44.68 | 121.79–197.98 / 117.27–210.48 | -156.77–-74.04 / -7.85–10.67 / 97.35–172.30 |
| NQ / PIN074_ref_01 | after_15m | 1.12–1.56 / 1.27–1.69 | 5.13–5.86 / 5.13–6.50 | -4.50–-3.54 / -0.12–0.17 / 3.65–4.24 |
| NQ / PIN074_ref_01 | after_180m | 6.18–8.95 / 5.63–8.31 | 24.61–33.17 / 22.14–31.38 | -23.62–-16.63 / 0.20–1.38 / 17.56–25.48 |
| NQ / PIN074_ref_01 | after_30m | 1.64–2.60 / 1.71–2.17 | 6.20–7.77 / 6.82–10.00 | -6.94–-4.62 / -0.12–0.32 / 4.66–6.40 |
| NQ / PIN074_ref_01 | after_60m | 2.71–3.85 / 2.60–3.35 | 11.22–12.45 / 8.80–14.23 | -9.60–-6.27 / -0.25–0.07 / 8.26–10.66 |
| NQ / PIN074_ref_01 | to_actual_cash_close | 21.91–37.26 / 18.40–33.26 | 73.12–147.33 / 95.06–165.40 | -119.60–-58.68 / -5.33–8.73 / 57.60–125.25 |
| NQ / PIN074_ref_03 | after_15m | 1.03–1.40 / 1.17–1.23 | 4.14–4.54 / 4.15–5.57 | -3.83–-3.10 / -0.12–0.14 / 2.90–3.92 |
| NQ / PIN074_ref_03 | after_180m | 2.84–4.41 / 2.86–4.16 | 10.53–12.92 / 11.49–15.24 | -12.09–-8.32 / -0.10–0.63 / 8.38–9.47 |
| NQ / PIN074_ref_03 | after_30m | 1.32–2.00 / 1.38–1.98 | 5.58–6.59 / 5.67–7.30 | -5.04–-4.36 / -0.38–0.41 / 4.05–5.68 |
| NQ / PIN074_ref_03 | after_60m | 2.05–2.93 / 1.80–2.39 | 7.34–8.31 / 7.50–8.58 | -6.04–-5.17 / 0.01–0.70 / 5.23–6.61 |
| NQ / PIN074_ref_03 | to_actual_cash_close | 10.26–14.89 / 9.41–15.00 | 31.48–55.00 / 38.64–67.72 | -56.67–-30.43 / -2.01–3.43 / 28.01–45.80 |
| NQ / PIN074_ref_04 | after_15m | 1.26–1.54 / 1.29–1.44 | 4.49–6.53 / 4.66–6.67 | -4.57–-3.54 / -0.07–0.19 / 3.36–5.06 |
| NQ / PIN074_ref_04 | after_180m | 3.41–3.90 / 3.50–4.35 | 12.04–14.14 / 13.75–20.35 | -12.93–-9.00 / -0.16–0.81 / 7.86–10.49 |
| NQ / PIN074_ref_04 | after_30m | 1.64–2.07 / 1.74–2.00 | 6.54–8.14 / 6.91–8.11 | -5.77–-5.15 / -0.17–0.23 / 4.43–5.54 |
| NQ / PIN074_ref_04 | after_60m | 2.19–2.72 / 2.24–2.73 | 8.16–10.40 / 9.22–10.21 | -8.00–-6.58 / -0.38–0.22 / 6.11–7.03 |
| NQ / PIN074_ref_04 | to_actual_cash_close | 13.34–16.78 / 13.00–18.00 | 44.79–65.41 / 54.48–70.99 | -55.27–-39.65 / -3.20–4.95 / 35.33–48.52 |
| NQ / PIN074_ref_07 | after_15m | 1.15–1.37 / 0.89–1.29 | 4.16–5.23 / 4.05–5.76 | -4.59–-2.91 / 0.07–0.34 / 3.10–4.11 |
| NQ / PIN074_ref_07 | after_180m | 7.00–9.91 / 7.19–9.64 | 28.17–38.59 / 32.00–43.54 | -33.33–-20.76 / -1.82–1.12 / 21.41–29.82 |
| NQ / PIN074_ref_07 | after_30m | 1.56–2.06 / 1.36–1.73 | 5.20–7.52 / 5.67–8.05 | -6.08–-4.27 / -0.07–0.68 / 4.47–5.49 |
| NQ / PIN074_ref_07 | after_60m | 2.29–2.76 / 1.88–2.55 | 7.98–11.23 / 8.01–12.75 | -9.82–-5.44 / -0.20–0.37 / 5.91–7.77 |
| NQ / PIN074_ref_07 | to_actual_cash_close | 13.86–18.38 / 12.06–17.00 | 46.74–68.39 / 61.64–89.73 | -69.53–-38.74 / -2.23–5.56 / 41.75–58.05 |
| NQ / PIN075_01 | after_15m | 0.13–0.17 / 0.16–0.20 | 0.56–0.68 / 0.64–0.75 | -0.56–-0.42 / -0.02–0.02 / 0.38–0.55 |
| NQ / PIN075_01 | after_180m | 0.54–0.83 / 0.60–0.86 | 2.35–2.96 / 2.60–3.13 | -2.33–-1.78 / -0.08–0.13 / 1.73–2.14 |
| NQ / PIN075_01 | after_30m | 0.20–0.25 / 0.21–0.24 | 0.84–1.07 / 0.91–0.99 | -0.83–-0.66 / -0.03–0.03 / 0.59–0.90 |
| NQ / PIN075_01 | after_60m | 0.31–0.34 / 0.29–0.41 | 1.28–1.58 / 1.40–1.53 | -1.32–-0.94 / -0.04–0.05 / 1.00–1.19 |
| NQ / PIN075_01 | to_actual_cash_close | 2.76–4.13 / 2.54–4.23 | 8.17–16.71 / 9.65–18.47 | -13.95–-6.92 / -0.88–0.94 / 6.53–12.95 |
| NQ / PIN075_02 | after_15m | 0.07–0.09 / 0.06–0.08 | 0.24–0.29 / 0.24–0.31 | -0.23–-0.16 / 0.00–0.01 / 0.19–0.22 |
| NQ / PIN075_02 | after_180m | 0.28–0.32 / 0.22–0.36 | 0.95–1.15 / 0.95–1.19 | -0.89–-0.65 / -0.05–0.10 / 0.76–0.91 |
| NQ / PIN075_02 | after_30m | 0.11–0.12 / 0.08–0.11 | 0.36–0.40 / 0.37–0.43 | -0.33–-0.25 / -0.01–0.02 / 0.25–0.31 |
| NQ / PIN075_02 | after_60m | 0.14–0.17 / 0.12–0.15 | 0.44–0.53 / 0.48–0.60 | -0.40–-0.37 / -0.03–0.04 / 0.32–0.40 |
| NQ / PIN075_02 | to_actual_cash_close | 1.37–2.49 / 1.24–2.17 | 4.02–9.04 / 5.58–8.90 | -6.93–-3.90 / -0.47–0.53 / 3.48–7.59 |
| NQ / PIN075_03 | after_15m | 0.17–0.23 / 0.17–0.26 | 0.60–0.73 / 0.70–0.86 | -0.63–-0.57 / -0.03–0.01 / 0.49–0.57 |
| NQ / PIN075_03 | after_180m | 0.48–0.76 / 0.47–0.63 | 1.62–2.17 / 1.96–2.47 | -1.95–-1.34 / -0.05–0.11 / 1.22–1.70 |
| NQ / PIN075_03 | after_30m | 0.23–0.32 / 0.22–0.35 | 0.81–1.06 / 0.99–1.24 | -0.98–-0.72 / -0.05–0.06 / 0.65–0.83 |
| NQ / PIN075_03 | after_60m | 0.32–0.43 / 0.30–0.43 | 1.13–1.33 / 1.35–1.67 | -1.02–-0.80 / 0.00–0.08 / 0.78–1.05 |
| NQ / PIN075_03 | to_actual_cash_close | 1.66–2.35 / 1.50–2.29 | 4.85–9.41 / 6.06–9.27 | -7.55–-4.53 / -0.37–0.56 / 4.03–8.17 |
| NQ / PIN075_04 | after_15m | 0.19–0.23 / 0.17–0.24 | 0.65–0.75 / 0.57–0.71 | -0.56–-0.43 / -0.02–0.04 / 0.51–0.58 |
| NQ / PIN075_04 | after_180m | 0.62–0.68 / 0.53–0.79 | 2.21–2.56 / 2.19–2.83 | -2.01–-1.67 / -0.04–0.10 / 1.73–1.99 |
| NQ / PIN075_04 | after_30m | 0.32–0.36 / 0.25–0.40 | 1.06–1.28 / 0.96–1.16 | -1.01–-0.72 / -0.05–0.07 / 0.80–1.00 |
| NQ / PIN075_04 | after_60m | 0.37–0.47 / 0.34–0.51 | 1.37–1.69 / 1.43–1.57 | -1.22–-0.87 / -0.03–0.10 / 1.02–1.41 |
| NQ / PIN075_04 | to_actual_cash_close | 2.22–2.87 / 2.14–2.81 | 6.92–10.88 / 7.53–11.03 | -9.13–-5.70 / -0.34–0.69 / 5.64–9.75 |
| NQ / PIN075_05 | after_15m | 0.12–0.16 / 0.13–0.16 | 0.43–0.47 / 0.46–0.55 | -0.41–-0.32 / -0.02–0.02 / 0.31–0.40 |
| NQ / PIN075_05 | after_180m | 0.49–0.60 / 0.42–0.59 | 1.61–1.75 / 1.75–2.45 | -1.70–-1.36 / 0.03–0.20 / 1.17–1.32 |
| NQ / PIN075_05 | after_30m | 0.18–0.22 / 0.17–0.22 | 0.51–0.66 / 0.63–0.82 | -0.70–-0.46 / -0.01–0.04 / 0.44–0.53 |
| NQ / PIN075_05 | after_60m | 0.27–0.32 / 0.26–0.31 | 0.82–0.93 / 0.97–1.35 | -0.93–-0.67 / -0.06–0.05 / 0.57–0.70 |
| NQ / PIN075_05 | to_actual_cash_close | 1.81–2.23 / 1.70–2.06 | 5.68–7.91 / 6.59–9.12 | -7.39–-5.51 / -0.45–0.73 / 4.61–7.17 |
| NQ / PIN075_06 | after_15m | 0.18–0.20 / 0.17–0.19 | 0.57–0.71 / 0.60–0.76 | -0.56–-0.43 / 0.01–0.03 / 0.41–0.54 |
| NQ / PIN075_06 | after_180m | 1.00–1.38 / 1.00–1.32 | 3.18–4.81 / 3.75–5.53 | -3.72–-2.56 / -0.32–0.24 / 2.55–3.99 |
| NQ / PIN075_06 | after_30m | 0.29–0.32 / 0.26–0.31 | 0.84–1.18 / 0.86–1.18 | -0.90–-0.64 / -0.01–0.07 / 0.71–0.85 |
| NQ / PIN075_06 | after_60m | 0.42–0.48 / 0.36–0.42 | 1.25–1.54 / 1.41–1.74 | -1.26–-1.02 / -0.01–0.12 / 1.02–1.14 |
| NQ / PIN075_06 | to_actual_cash_close | 2.38–2.97 / 2.05–2.89 | 7.29–11.02 / 9.40–12.64 | -9.65–-7.30 / -0.40–1.02 / 6.46–9.00 |
| NQ / PIN075_07 | after_15m | 0.31–0.42 / 0.32–0.46 | 1.20–1.42 / 1.13–1.62 | -1.16–-0.89 / -0.09–0.12 / 0.88–1.16 |
| NQ / PIN075_07 | after_180m | 0.80–0.94 / 0.87–0.96 | 2.79–3.72 / 2.88–4.54 | -3.30–-2.46 / -0.06–0.30 / 2.14–3.17 |
| NQ / PIN075_07 | after_30m | 0.41–0.55 / 0.43–0.58 | 1.52–1.81 / 1.45–2.01 | -1.56–-1.09 / -0.07–0.11 / 1.30–1.56 |
| NQ / PIN075_07 | after_60m | 0.57–0.72 / 0.61–0.79 | 1.97–2.65 / 1.95–3.05 | -2.39–-1.54 / -0.03–0.19 / 1.58–2.33 |
| NQ / PIN075_07 | to_actual_cash_close | 1.03–1.26 / 1.04–1.26 | 3.82–4.38 / 4.36–5.96 | -4.20–-3.43 / -0.18–0.50 / 3.05–3.81 |
| NQ / PIN075_08 | after_15m | 0.24–0.33 / 0.26–0.35 | 0.87–1.06 / 1.00–1.23 | -0.92–-0.72 / -0.03–0.06 / 0.70–0.82 |
| NQ / PIN075_08 | after_180m | 0.69–0.83 / 0.72–0.82 | 2.38–2.87 / 2.57–3.15 | -2.22–-1.93 / -0.14–0.31 / 1.67–2.47 |
| NQ / PIN075_08 | after_30m | 0.36–0.43 / 0.38–0.49 | 1.19–1.48 / 1.24–1.64 | -1.29–-0.96 / -0.03–0.10 / 0.88–1.17 |
| NQ / PIN075_08 | after_60m | 0.49–0.54 / 0.50–0.57 | 1.59–1.71 / 1.73–2.63 | -1.82–-1.42 / -0.01–0.10 / 1.26–1.53 |
| NQ / PIN075_08 | to_actual_cash_close | 0.95–1.21 / 0.95–1.17 | 3.21–3.99 / 3.72–4.10 | -3.33–-2.60 / 0.00–0.37 / 2.69–3.30 |
| NQ / PIN075_09 | after_15m | 0.19–0.22 / 0.17–0.20 | 0.48–0.65 / 0.60–0.70 | -0.60–-0.49 / 0.00–0.05 / 0.39–0.55 |
| NQ / PIN075_09 | after_180m | 0.54–0.64 / 0.53–0.61 | 1.87–2.12 / 2.05–2.74 | -2.13–-1.57 / -0.02–0.22 / 1.36–1.95 |
| NQ / PIN075_09 | after_30m | 0.27–0.30 / 0.24–0.29 | 0.74–0.95 / 0.85–1.08 | -0.81–-0.64 / 0.04–0.06 / 0.57–0.79 |
| NQ / PIN075_09 | after_60m | 0.37–0.41 / 0.34–0.41 | 1.02–1.20 / 1.12–1.59 | -1.31–-0.83 / 0.01–0.12 / 0.90–1.01 |
| NQ / PIN075_09 | to_actual_cash_close | 0.74–0.93 / 0.62–0.82 | 2.50–2.84 / 2.49–3.52 | -2.90–-1.93 / 0.05–0.25 / 1.81–2.58 |
| NQ / PIN075_10 | after_15m | 0.24–0.29 / 0.23–0.24 | 0.69–0.86 / 0.81–0.93 | -0.69–-0.62 / -0.01–0.07 / 0.53–0.74 |
| NQ / PIN075_10 | after_180m | 0.70–0.85 / 0.59–0.92 | 2.14–3.17 / 2.79–3.32 | -2.46–-1.82 / -0.18–0.25 / 1.80–2.50 |
| NQ / PIN075_10 | after_30m | 0.32–0.38 / 0.29–0.35 | 0.98–1.18 / 1.11–1.37 | -0.96–-0.91 / -0.06–0.14 / 0.82–0.94 |
| NQ / PIN075_10 | after_60m | 0.40–0.50 / 0.37–0.52 | 1.24–1.51 / 1.35–1.84 | -1.49–-1.02 / -0.10–0.12 / 1.05–1.21 |
| NQ / PIN075_10 | to_actual_cash_close | 0.94–1.06 / 0.70–1.11 | 2.83–4.01 / 3.60–4.28 | -3.57–-2.57 / -0.05–0.35 / 2.35–2.98 |
| NQ / PIN075_11 | after_15m | 0.14–0.19 / 0.15–0.18 | 0.47–0.60 / 0.55–0.62 | -0.52–-0.39 / -0.01–0.06 / 0.36–0.47 |
| NQ / PIN075_11 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN075_11 | after_30m | 0.19–0.27 / 0.20–0.24 | 0.66–0.87 / 0.81–0.97 | -0.76–-0.51 / 0.00–0.09 / 0.49–0.71 |
| NQ / PIN075_11 | after_60m | 0.27–0.39 / 0.28–0.34 | 0.92–1.31 / 1.14–1.34 | -1.09–-0.83 / -0.02–0.10 / 0.71–1.13 |
| NQ / PIN075_11 | to_actual_cash_close | 0.41–0.58 / 0.40–0.53 | 1.46–2.03 / 1.69–2.30 | -2.07–-1.26 / 0.02–0.11 / 1.17–1.77 |
| NQ / PIN075_12 | after_15m | 0.09–0.11 / 0.08–0.12 | 0.35–0.56 / 0.40–0.60 | -0.38–-0.24 / -0.01–0.01 / 0.21–0.34 |
| NQ / PIN075_12 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN075_12 | after_30m | 0.10–0.13 / 0.09–0.13 | 0.43–0.65 / 0.42–0.65 | -0.43–-0.25 / -0.00–0.02 / 0.31–0.47 |
| NQ / PIN075_12 | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN075_12 | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN076_00_08 | after_15m | 1.40–1.53 / 1.33–1.71 | 5.17–7.28 / 5.40–7.08 | -4.12–-3.61 / -0.13–0.22 / 3.38–5.35 |
| NQ / PIN076_00_08 | after_180m | 6.90–7.77 / 5.79–9.00 | 26.29–33.19 / 23.77–34.87 | -26.80–-14.93 / -0.30–1.06 / 18.41–24.20 |
| NQ / PIN076_00_08 | after_30m | 1.94–2.40 / 1.86–2.40 | 6.93–11.29 / 7.67–9.10 | -6.50–-5.53 / -0.16–0.33 / 5.23–8.86 |
| NQ / PIN076_00_08 | after_60m | 2.80–3.44 / 2.68–3.37 | 10.11–17.19 / 10.89–12.51 | -10.31–-7.54 / -0.27–0.60 / 7.00–11.24 |
| NQ / PIN076_00_08 | to_actual_cash_close | 27.18–45.00 / 22.88–44.68 | 121.79–197.98 / 117.27–210.48 | -156.77–-74.04 / -7.85–10.67 / 97.35–172.30 |
| NQ / PIN076_08_0930 | after_15m | 1.22–1.70 / 1.17–1.41 | 4.12–5.67 / 4.58–6.45 | -5.13–-3.18 / -0.09–0.43 / 2.80–4.74 |
| NQ / PIN076_08_0930 | after_180m | 8.66–11.57 / 7.89–13.11 | 29.31–40.69 / 33.66–51.14 | -39.62–-25.40 / -1.97–1.44 / 23.67–32.05 |
| NQ / PIN076_08_0930 | after_30m | 1.95–3.03 / 1.86–2.74 | 7.36–15.68 / 7.28–17.90 | -12.46–-4.50 / -0.24–0.47 / 5.08–10.44 |
| NQ / PIN076_08_0930 | after_60m | 2.93–4.30 / 2.50–4.04 | 10.26–22.36 / 10.31–22.48 | -15.67–-7.27 / -0.62–0.63 / 7.65–15.77 |
| NQ / PIN076_08_0930 | to_actual_cash_close | 13.12–19.02 / 12.05–18.57 | 46.00–64.45 / 55.39–84.26 | -66.57–-33.89 / -3.33–5.46 / 36.53–47.97 |
| NQ / PIN078_daily_not_combined | after_15m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN078_daily_not_combined | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN078_daily_not_combined | after_30m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN078_daily_not_combined | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PIN078_daily_not_combined | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PM | after_15m | 0.07–0.08 / 0.06–0.10 | 0.29–0.44 / 0.29–0.47 | -0.26–-0.16 / -0.01–0.01 / 0.20–0.30 |
| NQ / PM | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PM | after_30m | 0.08–0.09 / 0.07–0.11 | 0.37–0.55 / 0.37–0.52 | -0.33–-0.18 / -0.00–0.02 / 0.26–0.37 |
| NQ / PM | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / PM | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / RTH0930 | after_15m | 0.04–0.05 / 0.04–0.05 | 0.13–0.23 / 0.15–0.23 | -0.15–-0.10 / -0.01–0.00 / 0.08–0.14 |
| NQ / RTH0930 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / RTH0930 | after_30m | 0.04–0.05 / 0.04–0.06 | 0.15–0.36 / 0.17–0.30 | -0.20–-0.11 / -0.00–0.01 / 0.13–0.19 |
| NQ / RTH0930 | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / RTH0930 | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / RTH_actual | after_15m | 0.04–0.05 / 0.04–0.05 | 0.13–0.23 / 0.15–0.23 | -0.15–-0.10 / -0.01–0.00 / 0.08–0.14 |
| NQ / RTH_actual | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / RTH_actual | after_30m | 0.04–0.05 / 0.04–0.06 | 0.15–0.36 / 0.17–0.30 | -0.20–-0.11 / -0.00–0.01 / 0.13–0.19 |
| NQ / RTH_actual | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / RTH_actual | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / custom09 | after_15m | 0.08–0.10 / 0.08–0.10 | 0.26–0.28 / 0.29–0.40 | -0.30–-0.24 / -0.03–0.02 / 0.20–0.25 |
| NQ / custom09 | after_180m | 0.26–0.35 / 0.21–0.31 | 0.81–1.13 / 1.07–1.41 | -1.10–-0.63 / -0.02–0.12 / 0.69–0.96 |
| NQ / custom09 | after_30m | 0.09–0.13 / 0.11–0.14 | 0.37–0.40 / 0.42–0.58 | -0.42–-0.27 / -0.02–0.04 / 0.29–0.33 |
| NQ / custom09 | after_60m | 0.14–0.19 / 0.15–0.19 | 0.46–0.62 / 0.57–0.74 | -0.64–-0.38 / -0.04–0.05 / 0.38–0.46 |
| NQ / custom09 | to_actual_cash_close | 0.32–0.39 / 0.24–0.37 | 1.05–1.33 / 1.30–1.43 | -1.16–-0.95 / -0.02–0.11 / 0.93–1.12 |
| NQ / day00 | after_15m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / day00 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / day00 | after_30m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / day00 | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / day00 | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / futures08 | after_15m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / futures08 | after_180m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / futures08 | after_30m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / futures08 | after_60m | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / futures08 | to_actual_cash_close | unavailable / unavailable | unavailable / unavailable | unavailable / unavailable / unavailable |
| NQ / lunch | after_15m | 0.21–0.23 / 0.20–0.22 | 0.64–0.80 / 0.70–0.85 | -0.61–-0.54 / 0.02–0.05 / 0.49–0.66 |
| NQ / lunch | after_180m | 0.73–0.87 / 0.61–0.83 | 2.35–3.17 / 3.16–3.45 | -2.70–-2.24 / -0.02–0.24 / 1.92–2.34 |
| NQ / lunch | after_30m | 0.28–0.32 / 0.27–0.33 | 0.88–1.04 / 1.00–1.25 | -0.99–-0.69 / -0.02–0.08 / 0.73–0.87 |
| NQ / lunch | after_60m | 0.41–0.48 / 0.39–0.42 | 1.19–1.68 / 1.37–1.81 | -1.38–-1.17 / -0.00–0.09 / 0.99–1.28 |
| NQ / lunch | to_actual_cash_close | 0.72–0.87 / 0.61–0.83 | 2.27–3.17 / 3.15–3.40 | -2.74–-2.22 / 0.05–0.23 / 1.79–2.37 |
| NQ / magic_00 | after_15m | 0.23–0.30 / 0.25–0.32 | 0.81–1.25 / 0.93–1.22 | -0.85–-0.64 / -0.06–0.02 / 0.54–0.81 |
| NQ / magic_00 | after_180m | 1.22–1.56 / 1.05–1.41 | 4.12–5.57 / 4.27–5.96 | -4.69–-3.08 / 0.09–0.21 / 3.07–4.63 |
| NQ / magic_00 | after_30m | 0.31–0.41 / 0.33–0.42 | 1.23–1.44 / 1.19–1.61 | -1.19–-0.89 / -0.05–0.07 / 0.88–1.10 |
| NQ / magic_00 | after_60m | 0.45–0.59 / 0.51–0.58 | 1.80–2.42 / 1.69–2.49 | -1.95–-1.20 / -0.04–0.01 / 1.45–1.88 |
| NQ / magic_00 | to_actual_cash_close | 3.99–6.91 / 3.47–5.86 | 13.68–25.83 / 15.37–26.60 | -20.96–-10.33 / -1.04–1.66 / 10.56–22.67 |
| NQ / magic_01 | after_15m | 0.24–0.29 / 0.27–0.33 | 0.92–1.24 / 0.92–1.26 | -0.96–-0.73 / -0.04–0.01 / 0.67–0.86 |
| NQ / magic_01 | after_180m | 1.06–1.39 / 0.98–1.17 | 3.46–4.52 / 3.82–5.13 | -3.86–-2.70 / 0.09–0.28 / 2.52–3.37 |
| NQ / magic_01 | after_30m | 0.35–0.42 / 0.37–0.41 | 1.25–1.55 / 1.36–1.74 | -1.48–-1.00 / -0.01–0.08 / 0.94–1.28 |
| NQ / magic_01 | after_60m | 0.49–0.59 / 0.48–0.53 | 1.75–2.04 / 1.72–2.26 | -1.73–-1.42 / 0.00–0.08 / 1.25–1.72 |
| NQ / magic_01 | to_actual_cash_close | 3.36–5.01 / 2.77–4.58 | 9.60–19.70 / 14.23–19.08 | -14.99–-11.18 / -0.89–1.44 / 7.82–16.79 |
| NQ / magic_02 | after_15m | 0.27–0.35 / 0.29–0.39 | 1.03–1.30 / 1.12–1.25 | -0.98–-0.79 / -0.03–0.03 / 0.79–0.97 |
| NQ / magic_02 | after_180m | 0.78–1.09 / 0.77–0.96 | 2.72–3.35 / 3.10–3.58 | -2.81–-2.51 / -0.05–0.18 / 1.93–2.53 |
| NQ / magic_02 | after_30m | 0.37–0.50 / 0.37–0.54 | 1.46–1.72 / 1.59–2.00 | -1.61–-1.07 / -0.09–0.12 / 1.16–1.45 |
| NQ / magic_02 | after_60m | 0.46–0.66 / 0.47–0.68 | 1.87–2.34 / 2.04–2.38 | -1.54–-1.30 / 0.00–0.14 / 1.32–1.73 |
| NQ / magic_02 | to_actual_cash_close | 2.63–3.95 / 2.30–3.66 | 8.15–12.90 / 10.11–14.46 | -11.83–-8.12 / -0.56–0.85 / 6.82–11.35 |
| NQ / magic_06 | after_15m | 0.20–0.30 / 0.18–0.26 | 0.77–1.04 / 0.87–1.03 | -0.88–-0.61 / 0.01–0.08 / 0.66–0.92 |
| NQ / magic_06 | after_180m | 1.30–1.88 / 1.33–1.79 | 4.99–6.47 / 4.82–7.19 | -5.26–-3.12 / -0.38–0.29 / 3.71–5.51 |
| NQ / magic_06 | after_30m | 0.32–0.40 / 0.27–0.34 | 1.17–1.35 / 1.16–1.43 | -1.12–-0.90 / 0.02–0.09 / 0.78–1.05 |
| NQ / magic_06 | after_60m | 0.46–0.52 / 0.40–0.47 | 1.45–1.92 / 1.61–2.03 | -1.46–-1.16 / 0.01–0.07 / 1.14–1.50 |
| NQ / magic_06 | to_actual_cash_close | 2.53–3.39 / 2.33–3.60 | 8.30–11.54 / 10.60–13.53 | -10.40–-7.61 / -0.49–0.87 / 6.66–10.29 |
| NQ / magic_07 | after_15m | 0.21–0.28 / 0.20–0.25 | 0.72–0.81 / 0.76–0.98 | -0.71–-0.57 / 0.00–0.06 / 0.50–0.65 |
| NQ / magic_07 | after_180m | 1.51–2.02 / 1.51–1.97 | 4.85–7.04 / 6.11–8.60 | -6.03–-4.60 / -0.39–0.32 / 3.93–6.01 |
| NQ / magic_07 | after_30m | 0.32–0.48 / 0.32–0.43 | 1.18–2.37 / 1.14–2.58 | -1.96–-0.74 / -0.06–0.07 / 0.92–1.74 |
| NQ / magic_07 | after_60m | 0.48–0.67 / 0.47–0.68 | 1.87–3.34 / 1.73–3.74 | -2.44–-1.23 / -0.07–0.10 / 1.37–2.43 |
| NQ / magic_07 | to_actual_cash_close | 2.18–2.93 / 2.01–3.21 | 7.49–10.29 / 9.16–13.03 | -10.40–-6.54 / -0.41–0.91 / 6.04–8.24 |
| NQ / magic_08 | after_15m | 0.17–0.19 / 0.16–0.21 | 0.58–0.66 / 0.55–0.84 | -0.58–-0.42 / -0.02–0.02 / 0.41–0.52 |
| NQ / magic_08 | after_180m | 1.03–1.52 / 1.03–1.51 | 4.11–5.70 / 4.26–7.15 | -5.09–-3.76 / -0.15–0.37 / 3.28–5.35 |
| NQ / magic_08 | after_30m | 0.27–0.41 / 0.29–0.33 | 1.07–1.27 / 0.96–1.45 | -1.01–-0.68 / -0.01–0.05 / 0.73–1.02 |
| NQ / magic_08 | after_60m | 0.66–1.01 / 0.66–0.94 | 2.71–3.02 / 2.26–3.69 | -2.82–-1.73 / -0.10–0.17 / 1.78–2.78 |
| NQ / magic_08 | to_actual_cash_close | 1.57–2.05 / 1.39–1.83 | 5.94–7.37 / 6.24–8.71 | -7.11–-5.18 / -0.22–0.62 / 4.72–5.90 |
| NQ / magic_23 | after_15m | 0.18–0.23 / 0.19–0.22 | 0.68–0.93 / 0.64–0.81 | -0.58–-0.45 / -0.02–0.03 / 0.47–0.67 |
| NQ / magic_23 | after_180m | 0.95–1.14 / 0.86–1.21 | 2.92–4.07 / 3.53–3.97 | -2.94–-2.21 / -0.04–0.18 / 2.22–3.28 |
| NQ / magic_23 | after_30m | 0.27–0.32 / 0.25–0.31 | 0.96–1.34 / 0.91–1.25 | -0.87–-0.62 / -0.02–0.06 / 0.75–0.98 |
| NQ / magic_23 | after_60m | 0.41–0.45 / 0.37–0.46 | 1.48–1.85 / 1.52–1.94 | -1.33–-1.07 / -0.07–0.08 / 0.99–1.40 |
| NQ / magic_23 | to_actual_cash_close | 4.12–7.16 / 3.93–5.76 | 11.56–26.11 / 14.79–24.08 | -18.57–-9.61 / -1.13–1.47 / 9.77–22.26 |
| NQ / prior_RTH_open_observed | after_15m | 0.12–0.16 / 0.12–0.17 | 0.41–0.49 / 0.42–0.49 | -0.43–-0.32 / -0.02–0.02 / 0.32–0.38 |
| NQ / prior_RTH_open_observed | after_180m | 0.29–0.35 / 0.30–0.33 | 0.96–1.09 / 1.16–1.65 | -1.31–-0.93 / -0.01–0.07 / 0.73–1.01 |
| NQ / prior_RTH_open_observed | after_30m | 0.15–0.19 / 0.17–0.20 | 0.55–0.59 / 0.57–0.83 | -0.61–-0.43 / -0.00–0.04 / 0.45–0.53 |
| NQ / prior_RTH_open_observed | after_60m | 0.19–0.25 / 0.21–0.25 | 0.70–0.82 / 0.82–1.06 | -0.92–-0.56 / -0.00–0.08 / 0.57–0.65 |
| NQ / prior_RTH_open_observed | to_actual_cash_close | 0.39–0.45 / 0.36–0.46 | 1.31–1.54 / 1.53–2.04 | -1.67–-1.21 / -0.05–0.14 / 1.09–1.37 |
| NQ / prior_RTH_preopen | after_15m | 0.12–0.16 / 0.12–0.16 | 0.43–0.51 / 0.45–0.59 | -0.49–-0.33 / -0.02–0.04 / 0.36–0.44 |
| NQ / prior_RTH_preopen | after_180m | 0.29–0.36 / 0.30–0.34 | 1.03–1.15 / 1.08–1.66 | -1.42–-0.94 / -0.03–0.08 / 0.74–0.96 |
| NQ / prior_RTH_preopen | after_30m | 0.13–0.21 / 0.16–0.20 | 0.62–0.72 / 0.58–0.83 | -0.66–-0.37 / -0.02–0.06 / 0.47–0.60 |
| NQ / prior_RTH_preopen | after_60m | 0.19–0.27 / 0.21–0.26 | 0.76–0.90 / 0.78–1.11 | -0.86–-0.55 / -0.00–0.05 / 0.59–0.72 |
| NQ / prior_RTH_preopen | common_1001_to_actual_cash_close | 0.36–0.39 / 0.34–0.38 | 1.17–1.27 / 1.52–1.70 | -1.40–-1.12 / 0.01–0.09 / 0.84–1.20 |
| NQ / prior_RTH_preopen | prefix_15m_to_actual_cash_close | 0.38–0.42 / 0.34–0.40 | 1.20–1.44 / 1.49–1.93 | -1.44–-1.14 / -0.01–0.13 / 0.98–1.25 |
| NQ / prior_RTH_preopen | prefix_30m_to_actual_cash_close | 0.35–0.39 / 0.33–0.39 | 1.14–1.37 / 1.54–1.77 | -1.35–-1.11 / 0.02–0.09 / 0.89–1.16 |
| NQ / prior_RTH_preopen | prefix_60m_to_actual_cash_close | 0.30–0.36 / 0.32–0.36 | 1.06–1.26 / 1.26–1.66 | -1.25–-0.89 / 0.01–0.13 / 0.85–1.07 |
| NQ / prior_RTH_preopen | to_actual_cash_close | 0.38–0.46 / 0.36–0.44 | 1.38–1.54 / 1.65–2.16 | -1.78–-1.22 / -0.06–0.15 / 1.10–1.42 |
| NQ / turn_earlier | after_15m | 0.39–0.48 / 0.34–0.46 | 1.18–1.37 / 1.35–1.68 | -1.23–-1.01 / 0.01–0.06 / 0.98–1.15 |
| NQ / turn_earlier | after_180m | 0.95–1.19 / 0.90–1.15 | 2.91–3.58 / 3.74–4.08 | -3.42–-2.61 / -0.07–0.30 / 2.33–3.25 |
| NQ / turn_earlier | after_30m | 0.56–0.62 / 0.47–0.67 | 1.53–2.01 / 1.70–2.30 | -1.88–-1.35 / 0.00–0.20 / 1.22–1.62 |
| NQ / turn_earlier | after_60m | 0.72–0.76 / 0.60–0.93 | 2.03–2.73 / 2.57–2.83 | -2.31–-2.03 / -0.04–0.21 / 1.74–2.36 |
| NQ / turn_earlier | common_1001_to_actual_cash_close | 1.14–1.50 / 1.20–1.43 | 3.31–5.19 / 4.37–5.85 | -4.36–-3.30 / 0.06–0.36 / 2.72–4.37 |
| NQ / turn_earlier | to_actual_cash_close | 1.23–1.52 / 1.14–1.46 | 3.66–5.77 / 4.76–6.06 | -4.93–-3.36 / -0.12–0.52 / 3.03–4.77 |
| NQ / turn_later | after_15m | 0.44–0.60 / 0.48–0.62 | 1.30–1.88 / 1.68–2.12 | -1.72–-1.32 / -0.03–0.07 / 1.07–1.63 |
| NQ / turn_later | after_180m | 1.25–1.46 / 1.21–1.36 | 3.79–4.45 / 4.90–6.36 | -5.26–-3.63 / -0.09–0.32 / 3.01–3.79 |
| NQ / turn_later | after_30m | 0.67–0.73 / 0.67–0.81 | 1.89–2.53 / 2.37–2.85 | -2.41–-1.70 / 0.00–0.10 / 1.62–2.20 |
| NQ / turn_later | after_60m | 0.84–1.04 / 0.86–1.07 | 2.51–3.00 / 3.26–4.19 | -3.52–-2.40 / 0.04–0.14 / 1.88–2.25 |
| NQ / turn_later | common_1001_to_actual_cash_close | 1.68–2.11 / 1.61–1.85 | 4.94–6.02 / 7.09–8.01 | -5.89–-5.03 / 0.06–0.48 / 4.29–5.28 |
| NQ / turn_later | to_actual_cash_close | 1.68–2.11 / 1.61–1.85 | 4.94–6.02 / 7.09–8.01 | -5.89–-5.03 / 0.06–0.48 / 4.29–5.28 |
| NQ / turn_source | after_15m | 0.47–0.54 / 0.38–0.51 | 1.46–1.68 / 1.68–1.85 | -1.43–-1.29 / -0.01–0.21 / 1.05–1.44 |
| NQ / turn_source | after_180m | 1.18–1.40 / 1.12–1.20 | 3.59–4.00 / 4.71–5.33 | -4.36–-3.36 / -0.01–0.41 / 2.66–3.48 |
| NQ / turn_source | after_30m | 0.65–0.77 / 0.51–0.68 | 1.81–2.22 / 2.08–2.68 | -2.18–-1.65 / -0.01–0.24 / 1.43–1.98 |
| NQ / turn_source | after_60m | 0.85–1.03 / 0.76–0.95 | 2.58–2.83 / 2.91–3.44 | -2.88–-2.27 / -0.07–0.25 / 2.04–2.30 |
| NQ / turn_source | common_1001_to_actual_cash_close | 1.40–1.73 / 1.39–1.64 | 4.17–6.37 / 6.18–6.95 | -5.70–-3.71 / 0.05–0.38 / 3.41–5.37 |
| NQ / turn_source | to_actual_cash_close | 1.56–1.93 / 1.51–1.59 | 4.34–6.36 / 6.08–7.52 | -5.61–-4.08 / 0.09–0.76 / 3.85–5.45 |

## Do the source-specific mechanisms support their stated claims?

Generic double-break statistics do not answer these source questions. The table below reports the actual payload state populations for each source clock and branch. Magic midpoint return versus extension invalidation retains compatible terminal states when OHLC cannot order events. PIN073 midpoint return is conditional on its own conditioning stage, with neither/high-only/low-only/both strata; an earlier edge touch is not an invented prerequisite. PIN074/PIN076 open-to-open targets are created only once their observed opens are available. PIN078 measures separate Monday/Tuesday daily ranges and distinguishes repeated hit shares from unique-day hit rates. ONS retains the overnight range midpoint; no undisclosed classical-pivot formula is manufactured.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| ES / ONS03 | 2020 | 242 / 253 | availability_delayed | candidate_available: 242; formation_unavailable: 11 |
| ES / ONS03 | 2020 | 242 / 253 | nominal | candidate_available: 242; formation_unavailable: 11 |
| ES / ONS03 | 2021 | 243 / 252 | availability_delayed | candidate_available: 243; formation_unavailable: 9 |
| ES / ONS03 | 2021 | 243 / 252 | nominal | candidate_available: 243; formation_unavailable: 9 |
| ES / ONS03 | 2022 | 248 / 251 | availability_delayed | candidate_available: 248; formation_unavailable: 3 |
| ES / ONS03 | 2022 | 248 / 251 | nominal | candidate_available: 248; formation_unavailable: 3 |
| ES / ONS03 | 2023 | 242 / 250 | availability_delayed | candidate_available: 242; formation_unavailable: 8 |
| ES / ONS03 | 2023 | 242 / 250 | nominal | candidate_available: 242; formation_unavailable: 8 |
| ES / ONS03 | 2024 | 245 / 252 | availability_delayed | candidate_available: 245; formation_unavailable: 7 |
| ES / ONS03 | 2024 | 245 / 252 | nominal | candidate_available: 245; formation_unavailable: 7 |
| ES / ONS20 | 2020 | 231 / 253 | availability_delayed | candidate_available: 231; formation_unavailable: 22 |
| ES / ONS20 | 2020 | 231 / 253 | nominal | candidate_available: 231; formation_unavailable: 22 |
| ES / ONS20 | 2021 | 224 / 252 | availability_delayed | candidate_available: 224; formation_unavailable: 28 |
| ES / ONS20 | 2021 | 224 / 252 | nominal | candidate_available: 224; formation_unavailable: 28 |
| ES / ONS20 | 2022 | 238 / 251 | availability_delayed | candidate_available: 238; formation_unavailable: 13 |
| ES / ONS20 | 2022 | 238 / 251 | nominal | candidate_available: 238; formation_unavailable: 13 |
| ES / ONS20 | 2023 | 206 / 250 | availability_delayed | candidate_available: 206; formation_unavailable: 44 |
| ES / ONS20 | 2023 | 206 / 250 | nominal | candidate_available: 206; formation_unavailable: 44 |
| ES / ONS20 | 2024 | 203 / 252 | availability_delayed | candidate_available: 203; formation_unavailable: 49 |
| ES / ONS20 | 2024 | 203 / 252 | nominal | candidate_available: 203; formation_unavailable: 49 |
| ES / PIN073_1 | 2020 | 245 / 253 | availability_delayed | candidate_available: 239; conditioning_censored: 6; formation_unavailable: 8 |
| ES / PIN073_1 | 2020 | 245 / 253 | nominal | candidate_available: 239; conditioning_censored: 6; formation_unavailable: 8 |
| ES / PIN073_1 | 2020 | 236 observed dates | availability_delayed|compatible_reach | 69.9% [63.9%, 74.8%] |
| ES / PIN073_1 | 2020 | 236 observed dates | availability_delayed|definite_print | 33.9% [27.8%, 40.3%] |
| ES / PIN073_1 | 2020 | 148 observed dates | availability_delayed|stratum=both|compatible_reach | 77.7% [70.5%, 83.9%] |
| ES / PIN073_1 | 2020 | 148 observed dates | availability_delayed|stratum=both|definite_print | 36.5% [28.9%, 44.7%] |
| ES / PIN073_1 | 2020 | 52 observed dates | availability_delayed|stratum=high_only|compatible_reach | 55.8% [42.4%, 68.0%] |
| ES / PIN073_1 | 2020 | 52 observed dates | availability_delayed|stratum=high_only|definite_print | 28.8% [17.6%, 42.1%] |
| ES / PIN073_1 | 2020 | 35 observed dates | availability_delayed|stratum=low_only|compatible_reach | 60.0% [42.1%, 75.6%] |
| ES / PIN073_1 | 2020 | 35 observed dates | availability_delayed|stratum=low_only|definite_print | 31.4% [18.0%, 46.3%] |
| ES / PIN073_1 | 2020 | 1 observed dates | availability_delayed|stratum=neither|compatible_reach | 0.0% [0.0%, 0.0%] |
| ES / PIN073_1 | 2020 | 1 observed dates | availability_delayed|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| ES / PIN073_1 | 2020 | 239 observed dates | nominal|compatible_reach | 69.9% [64.0%, 74.6%] |
| ES / PIN073_1 | 2020 | 239 observed dates | nominal|definite_print | 34.3% [28.2%, 40.7%] |
| ES / PIN073_1 | 2020 | 148 observed dates | nominal|stratum=both|compatible_reach | 77.7% [70.5%, 83.9%] |
| ES / PIN073_1 | 2020 | 148 observed dates | nominal|stratum=both|definite_print | 36.5% [28.9%, 44.7%] |
| ES / PIN073_1 | 2020 | 52 observed dates | nominal|stratum=high_only|compatible_reach | 55.8% [42.4%, 68.0%] |
| ES / PIN073_1 | 2020 | 52 observed dates | nominal|stratum=high_only|definite_print | 28.8% [17.6%, 42.1%] |
| ES / PIN073_1 | 2020 | 35 observed dates | nominal|stratum=low_only|compatible_reach | 60.0% [42.1%, 75.6%] |
| ES / PIN073_1 | 2020 | 35 observed dates | nominal|stratum=low_only|definite_print | 31.4% [18.0%, 46.3%] |
| ES / PIN073_1 | 2020 | 1 observed dates | nominal|stratum=neither|compatible_reach | 0.0% [0.0%, 0.0%] |
| ES / PIN073_1 | 2020 | 1 observed dates | nominal|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| ES / PIN073_1 | 2021 | 248 / 252 | availability_delayed | candidate_available: 240; conditioning_censored: 8; formation_unavailable: 4 |
| ES / PIN073_1 | 2021 | 248 / 252 | nominal | candidate_available: 240; conditioning_censored: 8; formation_unavailable: 4 |
| ES / PIN073_1 | 2021 | 239 observed dates | availability_delayed|compatible_reach | 64.9% [59.2%, 70.0%] |
| ES / PIN073_1 | 2021 | 239 observed dates | availability_delayed|definite_print | 29.3% [24.0%, 34.4%] |
| ES / PIN073_1 | 2021 | 141 observed dates | availability_delayed|stratum=both|compatible_reach | 72.3% [65.1%, 78.8%] |
| ES / PIN073_1 | 2021 | 141 observed dates | availability_delayed|stratum=both|definite_print | 30.5% [22.3%, 37.9%] |
| ES / PIN073_1 | 2021 | 57 observed dates | availability_delayed|stratum=high_only|compatible_reach | 47.4% [35.3%, 60.0%] |
| ES / PIN073_1 | 2021 | 57 observed dates | availability_delayed|stratum=high_only|definite_print | 22.8% [12.0%, 36.2%] |
| ES / PIN073_1 | 2021 | 41 observed dates | availability_delayed|stratum=low_only|compatible_reach | 63.4% [48.0%, 77.8%] |
| ES / PIN073_1 | 2021 | 41 observed dates | availability_delayed|stratum=low_only|definite_print | 34.1% [20.0%, 50.0%] |
| ES / PIN073_1 | 2021 | 246 observed dates | nominal|compatible_reach | 65.9% [60.4%, 71.0%] |
| ES / PIN073_1 | 2021 | 246 observed dates | nominal|definite_print | 29.7% [24.3%, 34.7%] |
| ES / PIN073_1 | 2021 | 141 observed dates | nominal|stratum=both|compatible_reach | 72.3% [65.1%, 78.8%] |
| ES / PIN073_1 | 2021 | 141 observed dates | nominal|stratum=both|definite_print | 30.5% [22.3%, 37.9%] |
| ES / PIN073_1 | 2021 | 57 observed dates | nominal|stratum=high_only|compatible_reach | 47.4% [35.3%, 60.0%] |
| ES / PIN073_1 | 2021 | 57 observed dates | nominal|stratum=high_only|definite_print | 22.8% [12.0%, 36.2%] |
| ES / PIN073_1 | 2021 | 41 observed dates | nominal|stratum=low_only|compatible_reach | 63.4% [48.0%, 77.8%] |
| ES / PIN073_1 | 2021 | 41 observed dates | nominal|stratum=low_only|definite_print | 34.1% [20.0%, 50.0%] |
| ES / PIN073_1 | 2022 | 248 / 251 | availability_delayed | candidate_available: 247; conditioning_censored: 1; formation_unavailable: 3 |
| ES / PIN073_1 | 2022 | 248 / 251 | nominal | candidate_available: 247; conditioning_censored: 1; formation_unavailable: 3 |
| ES / PIN073_1 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 72.0% [66.7%, 77.2%] |
| ES / PIN073_1 | 2022 | 246 observed dates | availability_delayed|definite_print | 27.6% [22.0%, 33.2%] |
| ES / PIN073_1 | 2022 | 163 observed dates | availability_delayed|stratum=both|compatible_reach | 74.2% [67.6%, 81.3%] |
| ES / PIN073_1 | 2022 | 163 observed dates | availability_delayed|stratum=both|definite_print | 30.7% [24.2%, 38.0%] |
| ES / PIN073_1 | 2022 | 43 observed dates | availability_delayed|stratum=high_only|compatible_reach | 76.7% [62.8%, 88.9%] |
| ES / PIN073_1 | 2022 | 43 observed dates | availability_delayed|stratum=high_only|definite_print | 27.9% [13.9%, 45.5%] |
| ES / PIN073_1 | 2022 | 40 observed dates | availability_delayed|stratum=low_only|compatible_reach | 57.5% [42.1%, 73.0%] |
| ES / PIN073_1 | 2022 | 40 observed dates | availability_delayed|stratum=low_only|definite_print | 15.0% [5.6%, 26.2%] |
| ES / PIN073_1 | 2022 | 246 observed dates | nominal|compatible_reach | 72.0% [66.7%, 77.2%] |
| ES / PIN073_1 | 2022 | 246 observed dates | nominal|definite_print | 27.6% [22.0%, 33.2%] |
| ES / PIN073_1 | 2022 | 163 observed dates | nominal|stratum=both|compatible_reach | 74.2% [67.6%, 81.3%] |
| ES / PIN073_1 | 2022 | 163 observed dates | nominal|stratum=both|definite_print | 30.7% [24.2%, 38.0%] |
| ES / PIN073_1 | 2022 | 43 observed dates | nominal|stratum=high_only|compatible_reach | 76.7% [62.8%, 88.9%] |
| ES / PIN073_1 | 2022 | 43 observed dates | nominal|stratum=high_only|definite_print | 27.9% [13.9%, 45.5%] |
| ES / PIN073_1 | 2022 | 40 observed dates | nominal|stratum=low_only|compatible_reach | 57.5% [42.1%, 73.0%] |
| ES / PIN073_1 | 2022 | 40 observed dates | nominal|stratum=low_only|definite_print | 15.0% [5.6%, 26.2%] |
| ES / PIN073_1 | 2023 | 246 / 250 | availability_delayed | candidate_available: 239; conditioning_censored: 7; formation_unavailable: 4 |
| ES / PIN073_1 | 2023 | 246 / 250 | nominal | candidate_available: 239; conditioning_censored: 7; formation_unavailable: 4 |
| ES / PIN073_1 | 2023 | 237 observed dates | availability_delayed|compatible_reach | 76.4% [71.3%, 81.9%] |
| ES / PIN073_1 | 2023 | 237 observed dates | availability_delayed|definite_print | 31.6% [26.2%, 37.2%] |
| ES / PIN073_1 | 2023 | 165 observed dates | availability_delayed|stratum=both|compatible_reach | 81.2% [76.1%, 87.2%] |
| ES / PIN073_1 | 2023 | 165 observed dates | availability_delayed|stratum=both|definite_print | 33.9% [27.6%, 40.5%] |
| ES / PIN073_1 | 2023 | 43 observed dates | availability_delayed|stratum=high_only|compatible_reach | 72.1% [57.9%, 83.7%] |
| ES / PIN073_1 | 2023 | 43 observed dates | availability_delayed|stratum=high_only|definite_print | 27.9% [17.1%, 41.5%] |
| ES / PIN073_1 | 2023 | 29 observed dates | availability_delayed|stratum=low_only|compatible_reach | 55.2% [36.0%, 74.1%] |
| ES / PIN073_1 | 2023 | 29 observed dates | availability_delayed|stratum=low_only|definite_print | 24.1% [10.0%, 39.4%] |
| ES / PIN073_1 | 2023 | 244 observed dates | nominal|compatible_reach | 76.6% [71.7%, 82.2%] |
| ES / PIN073_1 | 2023 | 244 observed dates | nominal|definite_print | 32.0% [26.6%, 37.6%] |
| ES / PIN073_1 | 2023 | 165 observed dates | nominal|stratum=both|compatible_reach | 81.2% [76.1%, 87.2%] |
| ES / PIN073_1 | 2023 | 165 observed dates | nominal|stratum=both|definite_print | 33.9% [27.6%, 40.5%] |
| ES / PIN073_1 | 2023 | 43 observed dates | nominal|stratum=high_only|compatible_reach | 72.1% [57.9%, 83.7%] |
| ES / PIN073_1 | 2023 | 43 observed dates | nominal|stratum=high_only|definite_print | 27.9% [17.1%, 41.5%] |
| ES / PIN073_1 | 2023 | 29 observed dates | nominal|stratum=low_only|compatible_reach | 55.2% [36.0%, 74.1%] |
| ES / PIN073_1 | 2023 | 29 observed dates | nominal|stratum=low_only|definite_print | 24.1% [10.0%, 39.4%] |
| ES / PIN073_1 | 2024 | 245 / 252 | availability_delayed | candidate_available: 241; conditioning_censored: 4; formation_unavailable: 7 |
| ES / PIN073_1 | 2024 | 245 / 252 | nominal | candidate_available: 241; conditioning_censored: 4; formation_unavailable: 7 |
| ES / PIN073_1 | 2024 | 238 observed dates | availability_delayed|compatible_reach | 73.9% [69.0%, 80.2%] |
| ES / PIN073_1 | 2024 | 238 observed dates | availability_delayed|definite_print | 31.5% [26.3%, 38.4%] |
| ES / PIN073_1 | 2024 | 156 observed dates | availability_delayed|stratum=both|compatible_reach | 76.3% [70.9%, 83.3%] |
| ES / PIN073_1 | 2024 | 156 observed dates | availability_delayed|stratum=both|definite_print | 31.4% [24.8%, 39.3%] |
| ES / PIN073_1 | 2024 | 46 observed dates | availability_delayed|stratum=high_only|compatible_reach | 67.4% [54.0%, 80.3%] |
| ES / PIN073_1 | 2024 | 46 observed dates | availability_delayed|stratum=high_only|definite_print | 34.8% [20.8%, 50.9%] |
| ES / PIN073_1 | 2024 | 36 observed dates | availability_delayed|stratum=low_only|compatible_reach | 72.2% [57.9%, 87.8%] |
| ES / PIN073_1 | 2024 | 36 observed dates | availability_delayed|stratum=low_only|definite_print | 27.8% [13.2%, 45.2%] |
| ES / PIN073_1 | 2024 | 242 observed dates | nominal|compatible_reach | 74.4% [69.4%, 80.5%] |
| ES / PIN073_1 | 2024 | 242 observed dates | nominal|definite_print | 31.8% [26.5%, 38.8%] |
| ES / PIN073_1 | 2024 | 156 observed dates | nominal|stratum=both|compatible_reach | 76.3% [70.9%, 83.3%] |
| ES / PIN073_1 | 2024 | 156 observed dates | nominal|stratum=both|definite_print | 31.4% [24.8%, 39.3%] |
| ES / PIN073_1 | 2024 | 46 observed dates | nominal|stratum=high_only|compatible_reach | 67.4% [54.0%, 80.3%] |
| ES / PIN073_1 | 2024 | 46 observed dates | nominal|stratum=high_only|definite_print | 34.8% [20.8%, 50.9%] |
| ES / PIN073_1 | 2024 | 36 observed dates | nominal|stratum=low_only|compatible_reach | 72.2% [57.9%, 87.8%] |
| ES / PIN073_1 | 2024 | 36 observed dates | nominal|stratum=low_only|definite_print | 27.8% [13.2%, 45.2%] |
| ES / PIN073_2 | 2020 | 247 / 253 | availability_delayed | candidate_available: 243; conditioning_censored: 4; formation_unavailable: 6 |
| ES / PIN073_2 | 2020 | 247 / 253 | nominal | candidate_available: 243; conditioning_censored: 4; formation_unavailable: 6 |
| ES / PIN073_2 | 2020 | 241 observed dates | availability_delayed|compatible_reach | 32.0% [26.4%, 36.6%] |
| ES / PIN073_2 | 2020 | 241 observed dates | availability_delayed|definite_print | 13.3% [8.8%, 17.1%] |
| ES / PIN073_2 | 2020 | 180 observed dates | availability_delayed|stratum=both|compatible_reach | 33.3% [26.8%, 39.7%] |
| ES / PIN073_2 | 2020 | 180 observed dates | availability_delayed|stratum=both|definite_print | 15.6% [10.2%, 21.1%] |
| ES / PIN073_2 | 2020 | 32 observed dates | availability_delayed|stratum=high_only|compatible_reach | 18.8% [6.2%, 30.0%] |
| ES / PIN073_2 | 2020 | 32 observed dates | availability_delayed|stratum=high_only|definite_print | 0.0% [0.0%, 0.0%] |
| ES / PIN073_2 | 2020 | 29 observed dates | availability_delayed|stratum=low_only|compatible_reach | 37.9% [21.9%, 50.0%] |
| ES / PIN073_2 | 2020 | 29 observed dates | availability_delayed|stratum=low_only|definite_print | 13.8% [0.0%, 23.3%] |
| ES / PIN073_2 | 2020 | 241 observed dates | nominal|compatible_reach | 32.0% [26.4%, 36.6%] |
| ES / PIN073_2 | 2020 | 241 observed dates | nominal|definite_print | 13.3% [8.8%, 17.1%] |
| ES / PIN073_2 | 2020 | 180 observed dates | nominal|stratum=both|compatible_reach | 33.3% [26.8%, 39.7%] |
| ES / PIN073_2 | 2020 | 180 observed dates | nominal|stratum=both|definite_print | 15.6% [10.2%, 21.1%] |
| ES / PIN073_2 | 2020 | 32 observed dates | nominal|stratum=high_only|compatible_reach | 18.8% [6.2%, 30.0%] |
| ES / PIN073_2 | 2020 | 32 observed dates | nominal|stratum=high_only|definite_print | 0.0% [0.0%, 0.0%] |
| ES / PIN073_2 | 2020 | 29 observed dates | nominal|stratum=low_only|compatible_reach | 37.9% [21.9%, 50.0%] |
| ES / PIN073_2 | 2020 | 29 observed dates | nominal|stratum=low_only|definite_print | 13.8% [0.0%, 23.3%] |
| ES / PIN073_2 | 2021 | 251 / 252 | availability_delayed | candidate_available: 248; conditioning_censored: 3; formation_unavailable: 1 |
| ES / PIN073_2 | 2021 | 251 / 252 | nominal | candidate_available: 248; conditioning_censored: 3; formation_unavailable: 1 |
| ES / PIN073_2 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 32.4% [26.1%, 38.8%] |
| ES / PIN073_2 | 2021 | 247 observed dates | availability_delayed|definite_print | 11.7% [8.1%, 16.8%] |
| ES / PIN073_2 | 2021 | 169 observed dates | availability_delayed|stratum=both|compatible_reach | 39.6% [31.7%, 47.5%] |
| ES / PIN073_2 | 2021 | 169 observed dates | availability_delayed|stratum=both|definite_print | 14.2% [9.5%, 20.1%] |
| ES / PIN073_2 | 2021 | 54 observed dates | availability_delayed|stratum=high_only|compatible_reach | 16.7% [7.1%, 27.5%] |
| ES / PIN073_2 | 2021 | 54 observed dates | availability_delayed|stratum=high_only|definite_print | 7.4% [1.7%, 14.8%] |
| ES / PIN073_2 | 2021 | 24 observed dates | availability_delayed|stratum=low_only|compatible_reach | 16.7% [0.0%, 36.0%] |
| ES / PIN073_2 | 2021 | 24 observed dates | availability_delayed|stratum=low_only|definite_print | 4.2% [0.0%, 14.3%] |
| ES / PIN073_2 | 2021 | 247 observed dates | nominal|compatible_reach | 32.4% [26.1%, 38.8%] |
| ES / PIN073_2 | 2021 | 247 observed dates | nominal|definite_print | 11.7% [8.1%, 16.8%] |
| ES / PIN073_2 | 2021 | 169 observed dates | nominal|stratum=both|compatible_reach | 39.6% [31.7%, 47.5%] |
| ES / PIN073_2 | 2021 | 169 observed dates | nominal|stratum=both|definite_print | 14.2% [9.5%, 20.1%] |
| ES / PIN073_2 | 2021 | 54 observed dates | nominal|stratum=high_only|compatible_reach | 16.7% [7.1%, 27.5%] |
| ES / PIN073_2 | 2021 | 54 observed dates | nominal|stratum=high_only|definite_print | 7.4% [1.7%, 14.8%] |
| ES / PIN073_2 | 2021 | 24 observed dates | nominal|stratum=low_only|compatible_reach | 16.7% [0.0%, 36.0%] |
| ES / PIN073_2 | 2021 | 24 observed dates | nominal|stratum=low_only|definite_print | 4.2% [0.0%, 14.3%] |
| ES / PIN073_2 | 2022 | 251 / 251 | availability_delayed | candidate_available: 247; conditioning_censored: 4 |
| ES / PIN073_2 | 2022 | 251 / 251 | nominal | candidate_available: 247; conditioning_censored: 4 |
| ES / PIN073_2 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 32.1% [26.4%, 37.0%] |
| ES / PIN073_2 | 2022 | 246 observed dates | availability_delayed|definite_print | 12.6% [8.9%, 16.9%] |
| ES / PIN073_2 | 2022 | 176 observed dates | availability_delayed|stratum=both|compatible_reach | 38.6% [31.7%, 44.9%] |
| ES / PIN073_2 | 2022 | 176 observed dates | availability_delayed|stratum=both|definite_print | 14.8% [9.8%, 20.7%] |
| ES / PIN073_2 | 2022 | 30 observed dates | availability_delayed|stratum=high_only|compatible_reach | 20.0% [6.7%, 34.8%] |
| ES / PIN073_2 | 2022 | 30 observed dates | availability_delayed|stratum=high_only|definite_print | 10.0% [0.0%, 21.9%] |
| ES / PIN073_2 | 2022 | 40 observed dates | availability_delayed|stratum=low_only|compatible_reach | 12.5% [4.2%, 22.2%] |
| ES / PIN073_2 | 2022 | 40 observed dates | availability_delayed|stratum=low_only|definite_print | 5.0% [0.0%, 12.2%] |
| ES / PIN073_2 | 2022 | 246 observed dates | nominal|compatible_reach | 32.5% [26.8%, 37.8%] |
| ES / PIN073_2 | 2022 | 246 observed dates | nominal|definite_print | 12.6% [8.9%, 16.9%] |
| ES / PIN073_2 | 2022 | 176 observed dates | nominal|stratum=both|compatible_reach | 39.2% [32.3%, 45.6%] |
| ES / PIN073_2 | 2022 | 176 observed dates | nominal|stratum=both|definite_print | 14.8% [9.8%, 20.7%] |
| ES / PIN073_2 | 2022 | 30 observed dates | nominal|stratum=high_only|compatible_reach | 20.0% [6.7%, 34.8%] |
| ES / PIN073_2 | 2022 | 30 observed dates | nominal|stratum=high_only|definite_print | 10.0% [0.0%, 21.9%] |
| ES / PIN073_2 | 2022 | 40 observed dates | nominal|stratum=low_only|compatible_reach | 12.5% [4.2%, 22.2%] |
| ES / PIN073_2 | 2022 | 40 observed dates | nominal|stratum=low_only|definite_print | 5.0% [0.0%, 12.2%] |
| ES / PIN073_2 | 2023 | 250 / 250 | availability_delayed | candidate_available: 246; conditioning_censored: 4 |
| ES / PIN073_2 | 2023 | 250 / 250 | nominal | candidate_available: 246; conditioning_censored: 4 |
| ES / PIN073_2 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 36.9% [31.0%, 42.4%] |
| ES / PIN073_2 | 2023 | 244 observed dates | availability_delayed|definite_print | 17.6% [13.1%, 22.8%] |
| ES / PIN073_2 | 2023 | 173 observed dates | availability_delayed|stratum=both|compatible_reach | 41.6% [35.0%, 48.5%] |
| ES / PIN073_2 | 2023 | 173 observed dates | availability_delayed|stratum=both|definite_print | 20.2% [14.8%, 26.7%] |
| ES / PIN073_2 | 2023 | 38 observed dates | availability_delayed|stratum=high_only|compatible_reach | 18.4% [6.4%, 29.5%] |
| ES / PIN073_2 | 2023 | 38 observed dates | availability_delayed|stratum=high_only|definite_print | 7.9% [0.0%, 17.6%] |
| ES / PIN073_2 | 2023 | 33 observed dates | availability_delayed|stratum=low_only|compatible_reach | 33.3% [17.5%, 50.0%] |
| ES / PIN073_2 | 2023 | 33 observed dates | availability_delayed|stratum=low_only|definite_print | 15.2% [3.4%, 27.8%] |
| ES / PIN073_2 | 2023 | 244 observed dates | nominal|compatible_reach | 36.9% [31.0%, 42.4%] |
| ES / PIN073_2 | 2023 | 244 observed dates | nominal|definite_print | 17.6% [13.1%, 22.8%] |
| ES / PIN073_2 | 2023 | 173 observed dates | nominal|stratum=both|compatible_reach | 41.6% [35.0%, 48.5%] |
| ES / PIN073_2 | 2023 | 173 observed dates | nominal|stratum=both|definite_print | 20.2% [14.8%, 26.7%] |
| ES / PIN073_2 | 2023 | 38 observed dates | nominal|stratum=high_only|compatible_reach | 18.4% [6.4%, 29.5%] |
| ES / PIN073_2 | 2023 | 38 observed dates | nominal|stratum=high_only|definite_print | 7.9% [0.0%, 17.6%] |
| ES / PIN073_2 | 2023 | 33 observed dates | nominal|stratum=low_only|compatible_reach | 33.3% [17.5%, 50.0%] |
| ES / PIN073_2 | 2023 | 33 observed dates | nominal|stratum=low_only|definite_print | 15.2% [3.4%, 27.8%] |
| ES / PIN073_2 | 2024 | 252 / 252 | availability_delayed | candidate_available: 248; conditioning_censored: 4 |
| ES / PIN073_2 | 2024 | 252 / 252 | nominal | candidate_available: 248; conditioning_censored: 4 |
| ES / PIN073_2 | 2024 | 245 observed dates | availability_delayed|compatible_reach | 40.4% [34.7%, 46.5%] |
| ES / PIN073_2 | 2024 | 245 observed dates | availability_delayed|definite_print | 16.7% [12.4%, 21.6%] |
| ES / PIN073_2 | 2024 | 185 observed dates | availability_delayed|stratum=both|compatible_reach | 45.4% [38.3%, 52.2%] |
| ES / PIN073_2 | 2024 | 185 observed dates | availability_delayed|stratum=both|definite_print | 18.4% [13.6%, 24.6%] |
| ES / PIN073_2 | 2024 | 32 observed dates | availability_delayed|stratum=high_only|compatible_reach | 21.9% [6.4%, 36.1%] |
| ES / PIN073_2 | 2024 | 32 observed dates | availability_delayed|stratum=high_only|definite_print | 12.5% [0.0%, 24.1%] |
| ES / PIN073_2 | 2024 | 28 observed dates | availability_delayed|stratum=low_only|compatible_reach | 28.6% [13.0%, 46.2%] |
| ES / PIN073_2 | 2024 | 28 observed dates | availability_delayed|stratum=low_only|definite_print | 10.7% [0.0%, 25.0%] |
| ES / PIN073_2 | 2024 | 245 observed dates | nominal|compatible_reach | 40.4% [34.7%, 46.5%] |
| ES / PIN073_2 | 2024 | 245 observed dates | nominal|definite_print | 16.7% [12.4%, 21.6%] |
| ES / PIN073_2 | 2024 | 185 observed dates | nominal|stratum=both|compatible_reach | 45.4% [38.3%, 52.2%] |
| ES / PIN073_2 | 2024 | 185 observed dates | nominal|stratum=both|definite_print | 18.4% [13.6%, 24.6%] |
| ES / PIN073_2 | 2024 | 32 observed dates | nominal|stratum=high_only|compatible_reach | 21.9% [6.4%, 36.1%] |
| ES / PIN073_2 | 2024 | 32 observed dates | nominal|stratum=high_only|definite_print | 12.5% [0.0%, 24.1%] |
| ES / PIN073_2 | 2024 | 28 observed dates | nominal|stratum=low_only|compatible_reach | 28.6% [13.0%, 46.2%] |
| ES / PIN073_2 | 2024 | 28 observed dates | nominal|stratum=low_only|definite_print | 10.7% [0.0%, 25.0%] |
| ES / PIN073_3 | 2020 | 241 / 253 | availability_delayed | candidate_available: 231; conditioning_censored: 10; formation_unavailable: 12 |
| ES / PIN073_3 | 2020 | 241 / 253 | nominal | candidate_available: 231; conditioning_censored: 10; formation_unavailable: 12 |
| ES / PIN073_3 | 2020 | 229 observed dates | availability_delayed|compatible_reach | 79.9% [74.5%, 85.2%] |
| ES / PIN073_3 | 2020 | 229 observed dates | availability_delayed|definite_print | 34.5% [28.3%, 40.8%] |
| ES / PIN073_3 | 2020 | 99 observed dates | availability_delayed|stratum=both|compatible_reach | 81.8% [75.0%, 89.1%] |
| ES / PIN073_3 | 2020 | 99 observed dates | availability_delayed|stratum=both|definite_print | 34.3% [25.3%, 44.7%] |
| ES / PIN073_3 | 2020 | 75 observed dates | availability_delayed|stratum=high_only|compatible_reach | 74.7% [64.4%, 84.0%] |
| ES / PIN073_3 | 2020 | 75 observed dates | availability_delayed|stratum=high_only|definite_print | 30.7% [20.6%, 41.8%] |
| ES / PIN073_3 | 2020 | 54 observed dates | availability_delayed|stratum=low_only|compatible_reach | 83.3% [73.3%, 91.8%] |
| ES / PIN073_3 | 2020 | 54 observed dates | availability_delayed|stratum=low_only|definite_print | 40.7% [26.4%, 55.6%] |
| ES / PIN073_3 | 2020 | 1 observed dates | availability_delayed|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2020 | 1 observed dates | availability_delayed|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| ES / PIN073_3 | 2020 | 235 observed dates | nominal|compatible_reach | 81.7% [77.0%, 86.3%] |
| ES / PIN073_3 | 2020 | 235 observed dates | nominal|definite_print | 35.3% [29.2%, 41.5%] |
| ES / PIN073_3 | 2020 | 99 observed dates | nominal|stratum=both|compatible_reach | 82.8% [76.2%, 90.2%] |
| ES / PIN073_3 | 2020 | 99 observed dates | nominal|stratum=both|definite_print | 34.3% [25.3%, 44.7%] |
| ES / PIN073_3 | 2020 | 75 observed dates | nominal|stratum=high_only|compatible_reach | 77.3% [67.6%, 86.5%] |
| ES / PIN073_3 | 2020 | 75 observed dates | nominal|stratum=high_only|definite_print | 30.7% [20.6%, 41.8%] |
| ES / PIN073_3 | 2020 | 54 observed dates | nominal|stratum=low_only|compatible_reach | 85.2% [75.5%, 93.0%] |
| ES / PIN073_3 | 2020 | 54 observed dates | nominal|stratum=low_only|definite_print | 40.7% [26.4%, 55.6%] |
| ES / PIN073_3 | 2020 | 1 observed dates | nominal|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2020 | 1 observed dates | nominal|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| ES / PIN073_3 | 2021 | 229 / 252 | availability_delayed | candidate_available: 218; conditioning_censored: 11; formation_unavailable: 23 |
| ES / PIN073_3 | 2021 | 229 / 252 | nominal | candidate_available: 218; conditioning_censored: 11; formation_unavailable: 23 |
| ES / PIN073_3 | 2021 | 215 observed dates | availability_delayed|compatible_reach | 79.5% [75.2%, 84.3%] |
| ES / PIN073_3 | 2021 | 215 observed dates | availability_delayed|definite_print | 42.8% [36.2%, 49.3%] |
| ES / PIN073_3 | 2021 | 96 observed dates | availability_delayed|stratum=both|compatible_reach | 86.5% [80.6%, 92.9%] |
| ES / PIN073_3 | 2021 | 96 observed dates | availability_delayed|stratum=both|definite_print | 44.8% [36.4%, 54.7%] |
| ES / PIN073_3 | 2021 | 64 observed dates | availability_delayed|stratum=high_only|compatible_reach | 68.8% [57.1%, 78.6%] |
| ES / PIN073_3 | 2021 | 64 observed dates | availability_delayed|stratum=high_only|definite_print | 34.4% [22.1%, 46.1%] |
| ES / PIN073_3 | 2021 | 54 observed dates | availability_delayed|stratum=low_only|compatible_reach | 79.6% [68.3%, 88.9%] |
| ES / PIN073_3 | 2021 | 54 observed dates | availability_delayed|stratum=low_only|definite_print | 48.1% [35.2%, 60.3%] |
| ES / PIN073_3 | 2021 | 1 observed dates | availability_delayed|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2021 | 1 observed dates | availability_delayed|stratum=neither|definite_print | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2021 | 225 observed dates | nominal|compatible_reach | 80.0% [75.7%, 84.8%] |
| ES / PIN073_3 | 2021 | 225 observed dates | nominal|definite_print | 42.7% [36.6%, 49.3%] |
| ES / PIN073_3 | 2021 | 96 observed dates | nominal|stratum=both|compatible_reach | 86.5% [80.6%, 92.9%] |
| ES / PIN073_3 | 2021 | 96 observed dates | nominal|stratum=both|definite_print | 44.8% [36.4%, 54.7%] |
| ES / PIN073_3 | 2021 | 64 observed dates | nominal|stratum=high_only|compatible_reach | 68.8% [57.1%, 78.6%] |
| ES / PIN073_3 | 2021 | 64 observed dates | nominal|stratum=high_only|definite_print | 34.4% [22.1%, 46.1%] |
| ES / PIN073_3 | 2021 | 54 observed dates | nominal|stratum=low_only|compatible_reach | 79.6% [68.3%, 88.9%] |
| ES / PIN073_3 | 2021 | 54 observed dates | nominal|stratum=low_only|definite_print | 48.1% [35.2%, 60.3%] |
| ES / PIN073_3 | 2021 | 1 observed dates | nominal|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2021 | 1 observed dates | nominal|stratum=neither|definite_print | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2022 | 245 / 251 | availability_delayed | candidate_available: 243; conditioning_censored: 2; formation_unavailable: 6 |
| ES / PIN073_3 | 2022 | 245 / 251 | nominal | candidate_available: 243; conditioning_censored: 2; formation_unavailable: 6 |
| ES / PIN073_3 | 2022 | 243 observed dates | availability_delayed|compatible_reach | 79.4% [75.1%, 84.5%] |
| ES / PIN073_3 | 2022 | 243 observed dates | availability_delayed|definite_print | 42.4% [37.5%, 48.3%] |
| ES / PIN073_3 | 2022 | 111 observed dates | availability_delayed|stratum=both|compatible_reach | 82.9% [75.0%, 89.8%] |
| ES / PIN073_3 | 2022 | 111 observed dates | availability_delayed|stratum=both|definite_print | 44.1% [35.5%, 54.1%] |
| ES / PIN073_3 | 2022 | 77 observed dates | availability_delayed|stratum=high_only|compatible_reach | 74.0% [66.1%, 82.4%] |
| ES / PIN073_3 | 2022 | 77 observed dates | availability_delayed|stratum=high_only|definite_print | 33.8% [24.4%, 42.6%] |
| ES / PIN073_3 | 2022 | 53 observed dates | availability_delayed|stratum=low_only|compatible_reach | 79.2% [69.2%, 89.8%] |
| ES / PIN073_3 | 2022 | 53 observed dates | availability_delayed|stratum=low_only|definite_print | 49.1% [37.0%, 61.4%] |
| ES / PIN073_3 | 2022 | 2 observed dates | availability_delayed|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2022 | 2 observed dates | availability_delayed|stratum=neither|definite_print | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2022 | 245 observed dates | nominal|compatible_reach | 79.6% [74.9%, 84.8%] |
| ES / PIN073_3 | 2022 | 245 observed dates | nominal|definite_print | 42.0% [37.0%, 48.0%] |
| ES / PIN073_3 | 2022 | 111 observed dates | nominal|stratum=both|compatible_reach | 83.8% [75.9%, 90.7%] |
| ES / PIN073_3 | 2022 | 111 observed dates | nominal|stratum=both|definite_print | 44.1% [35.5%, 54.1%] |
| ES / PIN073_3 | 2022 | 77 observed dates | nominal|stratum=high_only|compatible_reach | 74.0% [66.1%, 82.4%] |
| ES / PIN073_3 | 2022 | 77 observed dates | nominal|stratum=high_only|definite_print | 33.8% [24.4%, 42.6%] |
| ES / PIN073_3 | 2022 | 53 observed dates | nominal|stratum=low_only|compatible_reach | 79.2% [69.2%, 89.8%] |
| ES / PIN073_3 | 2022 | 53 observed dates | nominal|stratum=low_only|definite_print | 49.1% [37.0%, 61.4%] |
| ES / PIN073_3 | 2022 | 2 observed dates | nominal|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2022 | 2 observed dates | nominal|stratum=neither|definite_print | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2023 | 209 / 250 | availability_delayed | candidate_available: 192; conditioning_censored: 17; formation_unavailable: 41 |
| ES / PIN073_3 | 2023 | 209 / 250 | nominal | candidate_available: 192; conditioning_censored: 17; formation_unavailable: 41 |
| ES / PIN073_3 | 2023 | 189 observed dates | availability_delayed|compatible_reach | 80.4% [74.8%, 85.3%] |
| ES / PIN073_3 | 2023 | 189 observed dates | availability_delayed|definite_print | 39.2% [31.7%, 45.4%] |
| ES / PIN073_3 | 2023 | 96 observed dates | availability_delayed|stratum=both|compatible_reach | 83.3% [75.3%, 90.0%] |
| ES / PIN073_3 | 2023 | 96 observed dates | availability_delayed|stratum=both|definite_print | 41.7% [32.6%, 50.6%] |
| ES / PIN073_3 | 2023 | 42 observed dates | availability_delayed|stratum=high_only|compatible_reach | 66.7% [51.4%, 78.9%] |
| ES / PIN073_3 | 2023 | 42 observed dates | availability_delayed|stratum=high_only|definite_print | 40.5% [24.2%, 53.8%] |
| ES / PIN073_3 | 2023 | 49 observed dates | availability_delayed|stratum=low_only|compatible_reach | 85.7% [75.0%, 94.5%] |
| ES / PIN073_3 | 2023 | 49 observed dates | availability_delayed|stratum=low_only|definite_print | 34.7% [20.0%, 45.9%] |
| ES / PIN073_3 | 2023 | 2 observed dates | availability_delayed|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2023 | 2 observed dates | availability_delayed|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| ES / PIN073_3 | 2023 | 204 observed dates | nominal|compatible_reach | 82.4% [77.2%, 86.9%] |
| ES / PIN073_3 | 2023 | 204 observed dates | nominal|definite_print | 40.2% [33.8%, 45.9%] |
| ES / PIN073_3 | 2023 | 96 observed dates | nominal|stratum=both|compatible_reach | 85.4% [78.3%, 91.8%] |
| ES / PIN073_3 | 2023 | 96 observed dates | nominal|stratum=both|definite_print | 41.7% [32.6%, 50.6%] |
| ES / PIN073_3 | 2023 | 42 observed dates | nominal|stratum=high_only|compatible_reach | 71.4% [56.8%, 84.2%] |
| ES / PIN073_3 | 2023 | 42 observed dates | nominal|stratum=high_only|definite_print | 40.5% [24.2%, 53.8%] |
| ES / PIN073_3 | 2023 | 49 observed dates | nominal|stratum=low_only|compatible_reach | 85.7% [75.0%, 94.5%] |
| ES / PIN073_3 | 2023 | 49 observed dates | nominal|stratum=low_only|definite_print | 34.7% [20.0%, 45.9%] |
| ES / PIN073_3 | 2023 | 2 observed dates | nominal|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2023 | 2 observed dates | nominal|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| ES / PIN073_3 | 2024 | 221 / 252 | availability_delayed | candidate_available: 196; conditioning_censored: 25; formation_unavailable: 31 |
| ES / PIN073_3 | 2024 | 221 / 252 | nominal | candidate_available: 196; conditioning_censored: 25; formation_unavailable: 31 |
| ES / PIN073_3 | 2024 | 195 observed dates | availability_delayed|compatible_reach | 75.4% [68.8%, 81.4%] |
| ES / PIN073_3 | 2024 | 195 observed dates | availability_delayed|definite_print | 34.4% [28.3%, 40.8%] |
| ES / PIN073_3 | 2024 | 79 observed dates | availability_delayed|stratum=both|compatible_reach | 84.8% [78.3%, 92.0%] |
| ES / PIN073_3 | 2024 | 79 observed dates | availability_delayed|stratum=both|definite_print | 40.5% [30.3%, 50.0%] |
| ES / PIN073_3 | 2024 | 62 observed dates | availability_delayed|stratum=high_only|compatible_reach | 64.5% [52.5%, 76.7%] |
| ES / PIN073_3 | 2024 | 62 observed dates | availability_delayed|stratum=high_only|definite_print | 30.6% [18.3%, 42.4%] |
| ES / PIN073_3 | 2024 | 53 observed dates | availability_delayed|stratum=low_only|compatible_reach | 73.6% [61.7%, 83.7%] |
| ES / PIN073_3 | 2024 | 53 observed dates | availability_delayed|stratum=low_only|definite_print | 30.2% [20.0%, 43.8%] |
| ES / PIN073_3 | 2024 | 1 observed dates | availability_delayed|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2024 | 1 observed dates | availability_delayed|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| ES / PIN073_3 | 2024 | 218 observed dates | nominal|compatible_reach | 75.7% [69.8%, 81.6%] |
| ES / PIN073_3 | 2024 | 218 observed dates | nominal|definite_print | 33.9% [28.3%, 40.1%] |
| ES / PIN073_3 | 2024 | 79 observed dates | nominal|stratum=both|compatible_reach | 86.1% [80.0%, 93.3%] |
| ES / PIN073_3 | 2024 | 79 observed dates | nominal|stratum=both|definite_print | 41.8% [31.6%, 51.9%] |
| ES / PIN073_3 | 2024 | 62 observed dates | nominal|stratum=high_only|compatible_reach | 64.5% [52.5%, 76.7%] |
| ES / PIN073_3 | 2024 | 62 observed dates | nominal|stratum=high_only|definite_print | 30.6% [18.3%, 42.4%] |
| ES / PIN073_3 | 2024 | 53 observed dates | nominal|stratum=low_only|compatible_reach | 73.6% [61.7%, 83.7%] |
| ES / PIN073_3 | 2024 | 53 observed dates | nominal|stratum=low_only|definite_print | 30.2% [20.0%, 43.8%] |
| ES / PIN073_3 | 2024 | 1 observed dates | nominal|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| ES / PIN073_3 | 2024 | 1 observed dates | nominal|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| ES / PIN073_4 | 2020 | 249 / 253 | availability_delayed | candidate_available: 249; formation_unavailable: 4 |
| ES / PIN073_4 | 2020 | 249 / 253 | nominal | candidate_available: 249; formation_unavailable: 4 |
| ES / PIN073_4 | 2020 | 246 observed dates | availability_delayed|compatible_reach | 67.5% [61.0%, 72.7%] |
| ES / PIN073_4 | 2020 | 246 observed dates | availability_delayed|definite_print | 33.3% [27.2%, 39.0%] |
| ES / PIN073_4 | 2020 | 14 observed dates | availability_delayed|stratum=both|compatible_reach | 85.7% [63.6%, 100.0%] |
| ES / PIN073_4 | 2020 | 14 observed dates | availability_delayed|stratum=both|definite_print | 35.7% [10.5%, 60.0%] |
| ES / PIN073_4 | 2020 | 108 observed dates | availability_delayed|stratum=high_only|compatible_reach | 65.7% [55.9%, 74.1%] |
| ES / PIN073_4 | 2020 | 108 observed dates | availability_delayed|stratum=high_only|definite_print | 36.1% [27.0%, 45.4%] |
| ES / PIN073_4 | 2020 | 86 observed dates | availability_delayed|stratum=low_only|compatible_reach | 64.0% [52.8%, 72.7%] |
| ES / PIN073_4 | 2020 | 86 observed dates | availability_delayed|stratum=low_only|definite_print | 27.9% [17.1%, 37.6%] |
| ES / PIN073_4 | 2020 | 38 observed dates | availability_delayed|stratum=neither|compatible_reach | 73.7% [59.4%, 87.2%] |
| ES / PIN073_4 | 2020 | 38 observed dates | availability_delayed|stratum=neither|definite_print | 36.8% [21.3%, 53.5%] |
| ES / PIN073_4 | 2020 | 246 observed dates | nominal|compatible_reach | 69.5% [63.2%, 74.6%] |
| ES / PIN073_4 | 2020 | 246 observed dates | nominal|definite_print | 33.7% [27.5%, 39.4%] |
| ES / PIN073_4 | 2020 | 14 observed dates | nominal|stratum=both|compatible_reach | 85.7% [63.6%, 100.0%] |
| ES / PIN073_4 | 2020 | 14 observed dates | nominal|stratum=both|definite_print | 35.7% [10.5%, 60.0%] |
| ES / PIN073_4 | 2020 | 108 observed dates | nominal|stratum=high_only|compatible_reach | 67.6% [58.0%, 75.9%] |
| ES / PIN073_4 | 2020 | 108 observed dates | nominal|stratum=high_only|definite_print | 37.0% [28.1%, 46.2%] |
| ES / PIN073_4 | 2020 | 86 observed dates | nominal|stratum=low_only|compatible_reach | 65.1% [53.9%, 74.2%] |
| ES / PIN073_4 | 2020 | 86 observed dates | nominal|stratum=low_only|definite_print | 27.9% [17.1%, 37.6%] |
| ES / PIN073_4 | 2020 | 38 observed dates | nominal|stratum=neither|compatible_reach | 78.9% [67.4%, 90.6%] |
| ES / PIN073_4 | 2020 | 38 observed dates | nominal|stratum=neither|definite_print | 36.8% [21.3%, 53.5%] |
| ES / PIN073_4 | 2021 | 248 / 252 | availability_delayed | candidate_available: 248; formation_unavailable: 4 |
| ES / PIN073_4 | 2021 | 248 / 252 | nominal | candidate_available: 248; formation_unavailable: 4 |
| ES / PIN073_4 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 64.8% [59.8%, 70.3%] |
| ES / PIN073_4 | 2021 | 247 observed dates | availability_delayed|definite_print | 27.1% [22.5%, 32.5%] |
| ES / PIN073_4 | 2021 | 26 observed dates | availability_delayed|stratum=both|compatible_reach | 69.2% [52.2%, 84.6%] |
| ES / PIN073_4 | 2021 | 26 observed dates | availability_delayed|stratum=both|definite_print | 26.9% [12.9%, 44.0%] |
| ES / PIN073_4 | 2021 | 103 observed dates | availability_delayed|stratum=high_only|compatible_reach | 53.4% [44.4%, 62.9%] |
| ES / PIN073_4 | 2021 | 103 observed dates | availability_delayed|stratum=high_only|definite_print | 25.2% [17.5%, 33.0%] |
| ES / PIN073_4 | 2021 | 87 observed dates | availability_delayed|stratum=low_only|compatible_reach | 74.7% [66.7%, 83.2%] |
| ES / PIN073_4 | 2021 | 87 observed dates | availability_delayed|stratum=low_only|definite_print | 31.0% [23.0%, 40.2%] |
| ES / PIN073_4 | 2021 | 31 observed dates | availability_delayed|stratum=neither|compatible_reach | 71.0% [54.5%, 84.9%] |
| ES / PIN073_4 | 2021 | 31 observed dates | availability_delayed|stratum=neither|definite_print | 22.6% [9.7%, 37.9%] |
| ES / PIN073_4 | 2021 | 247 observed dates | nominal|compatible_reach | 66.0% [60.6%, 71.7%] |
| ES / PIN073_4 | 2021 | 247 observed dates | nominal|definite_print | 27.5% [22.8%, 32.9%] |
| ES / PIN073_4 | 2021 | 26 observed dates | nominal|stratum=both|compatible_reach | 73.1% [57.1%, 88.5%] |
| ES / PIN073_4 | 2021 | 26 observed dates | nominal|stratum=both|definite_print | 30.8% [14.8%, 48.3%] |
| ES / PIN073_4 | 2021 | 103 observed dates | nominal|stratum=high_only|compatible_reach | 53.4% [44.4%, 62.9%] |
| ES / PIN073_4 | 2021 | 103 observed dates | nominal|stratum=high_only|definite_print | 25.2% [17.5%, 33.0%] |
| ES / PIN073_4 | 2021 | 87 observed dates | nominal|stratum=low_only|compatible_reach | 74.7% [66.7%, 83.2%] |
| ES / PIN073_4 | 2021 | 87 observed dates | nominal|stratum=low_only|definite_print | 31.0% [23.0%, 40.2%] |
| ES / PIN073_4 | 2021 | 31 observed dates | nominal|stratum=neither|compatible_reach | 77.4% [61.8%, 90.0%] |
| ES / PIN073_4 | 2021 | 31 observed dates | nominal|stratum=neither|definite_print | 22.6% [9.7%, 37.9%] |
| ES / PIN073_4 | 2022 | 247 / 251 | availability_delayed | candidate_available: 247; formation_unavailable: 4 |
| ES / PIN073_4 | 2022 | 247 / 251 | nominal | candidate_available: 247; formation_unavailable: 4 |
| ES / PIN073_4 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 71.5% [65.2%, 77.0%] |
| ES / PIN073_4 | 2022 | 246 observed dates | availability_delayed|definite_print | 28.0% [22.0%, 33.9%] |
| ES / PIN073_4 | 2022 | 22 observed dates | availability_delayed|stratum=both|compatible_reach | 90.9% [77.3%, 100.0%] |
| ES / PIN073_4 | 2022 | 22 observed dates | availability_delayed|stratum=both|definite_print | 27.3% [5.9%, 44.4%] |
| ES / PIN073_4 | 2022 | 109 observed dates | availability_delayed|stratum=high_only|compatible_reach | 69.7% [60.7%, 78.2%] |
| ES / PIN073_4 | 2022 | 109 observed dates | availability_delayed|stratum=high_only|definite_print | 24.8% [15.8%, 34.5%] |
| ES / PIN073_4 | 2022 | 82 observed dates | availability_delayed|stratum=low_only|compatible_reach | 65.9% [54.5%, 75.3%] |
| ES / PIN073_4 | 2022 | 82 observed dates | availability_delayed|stratum=low_only|definite_print | 30.5% [20.7%, 41.4%] |
| ES / PIN073_4 | 2022 | 33 observed dates | availability_delayed|stratum=neither|compatible_reach | 78.8% [64.3%, 92.3%] |
| ES / PIN073_4 | 2022 | 33 observed dates | availability_delayed|stratum=neither|definite_print | 33.3% [18.2%, 48.4%] |
| ES / PIN073_4 | 2022 | 246 observed dates | nominal|compatible_reach | 72.0% [65.6%, 77.4%] |
| ES / PIN073_4 | 2022 | 246 observed dates | nominal|definite_print | 28.0% [22.0%, 33.9%] |
| ES / PIN073_4 | 2022 | 22 observed dates | nominal|stratum=both|compatible_reach | 90.9% [77.3%, 100.0%] |
| ES / PIN073_4 | 2022 | 22 observed dates | nominal|stratum=both|definite_print | 27.3% [5.9%, 44.4%] |
| ES / PIN073_4 | 2022 | 109 observed dates | nominal|stratum=high_only|compatible_reach | 70.6% [61.2%, 79.2%] |
| ES / PIN073_4 | 2022 | 109 observed dates | nominal|stratum=high_only|definite_print | 24.8% [15.8%, 34.5%] |
| ES / PIN073_4 | 2022 | 82 observed dates | nominal|stratum=low_only|compatible_reach | 65.9% [54.5%, 75.3%] |
| ES / PIN073_4 | 2022 | 82 observed dates | nominal|stratum=low_only|definite_print | 30.5% [20.7%, 41.4%] |
| ES / PIN073_4 | 2022 | 33 observed dates | nominal|stratum=neither|compatible_reach | 78.8% [64.3%, 92.3%] |
| ES / PIN073_4 | 2022 | 33 observed dates | nominal|stratum=neither|definite_print | 33.3% [18.2%, 48.4%] |
| ES / PIN073_4 | 2023 | 246 / 250 | availability_delayed | candidate_available: 246; formation_unavailable: 4 |
| ES / PIN073_4 | 2023 | 246 / 250 | nominal | candidate_available: 246; formation_unavailable: 4 |
| ES / PIN073_4 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 71.7% [66.2%, 77.4%] |
| ES / PIN073_4 | 2023 | 244 observed dates | availability_delayed|definite_print | 35.7% [28.4%, 41.4%] |
| ES / PIN073_4 | 2023 | 34 observed dates | availability_delayed|stratum=both|compatible_reach | 76.5% [62.9%, 89.3%] |
| ES / PIN073_4 | 2023 | 34 observed dates | availability_delayed|stratum=both|definite_print | 44.1% [29.0%, 60.0%] |
| ES / PIN073_4 | 2023 | 99 observed dates | availability_delayed|stratum=high_only|compatible_reach | 63.6% [53.3%, 72.4%] |
| ES / PIN073_4 | 2023 | 99 observed dates | availability_delayed|stratum=high_only|definite_print | 32.3% [22.8%, 40.7%] |
| ES / PIN073_4 | 2023 | 80 observed dates | availability_delayed|stratum=low_only|compatible_reach | 76.2% [67.7%, 85.2%] |
| ES / PIN073_4 | 2023 | 80 observed dates | availability_delayed|stratum=low_only|definite_print | 33.8% [22.5%, 45.0%] |
| ES / PIN073_4 | 2023 | 31 observed dates | availability_delayed|stratum=neither|compatible_reach | 80.6% [65.6%, 93.1%] |
| ES / PIN073_4 | 2023 | 31 observed dates | availability_delayed|stratum=neither|definite_print | 41.9% [21.9%, 61.1%] |
| ES / PIN073_4 | 2023 | 244 observed dates | nominal|compatible_reach | 72.5% [67.1%, 78.1%] |
| ES / PIN073_4 | 2023 | 244 observed dates | nominal|definite_print | 35.7% [28.4%, 41.4%] |
| ES / PIN073_4 | 2023 | 34 observed dates | nominal|stratum=both|compatible_reach | 76.5% [62.9%, 89.3%] |
| ES / PIN073_4 | 2023 | 34 observed dates | nominal|stratum=both|definite_print | 44.1% [29.0%, 60.0%] |
| ES / PIN073_4 | 2023 | 99 observed dates | nominal|stratum=high_only|compatible_reach | 63.6% [53.3%, 72.4%] |
| ES / PIN073_4 | 2023 | 99 observed dates | nominal|stratum=high_only|definite_print | 32.3% [22.8%, 40.7%] |
| ES / PIN073_4 | 2023 | 80 observed dates | nominal|stratum=low_only|compatible_reach | 76.2% [67.7%, 85.2%] |
| ES / PIN073_4 | 2023 | 80 observed dates | nominal|stratum=low_only|definite_print | 33.8% [22.5%, 45.0%] |
| ES / PIN073_4 | 2023 | 31 observed dates | nominal|stratum=neither|compatible_reach | 87.1% [72.4%, 97.1%] |
| ES / PIN073_4 | 2023 | 31 observed dates | nominal|stratum=neither|definite_print | 41.9% [21.9%, 61.1%] |
| ES / PIN073_4 | 2024 | 248 / 252 | availability_delayed | candidate_available: 248; formation_unavailable: 4 |
| ES / PIN073_4 | 2024 | 248 / 252 | nominal | candidate_available: 248; formation_unavailable: 4 |
| ES / PIN073_4 | 2024 | 245 observed dates | availability_delayed|compatible_reach | 71.0% [66.2%, 77.0%] |
| ES / PIN073_4 | 2024 | 245 observed dates | availability_delayed|definite_print | 31.0% [25.6%, 36.4%] |
| ES / PIN073_4 | 2024 | 27 observed dates | availability_delayed|stratum=both|compatible_reach | 88.9% [73.1%, 100.0%] |
| ES / PIN073_4 | 2024 | 27 observed dates | availability_delayed|stratum=both|definite_print | 37.0% [20.0%, 57.7%] |
| ES / PIN073_4 | 2024 | 102 observed dates | availability_delayed|stratum=high_only|compatible_reach | 63.7% [55.4%, 71.6%] |
| ES / PIN073_4 | 2024 | 102 observed dates | availability_delayed|stratum=high_only|definite_print | 24.5% [17.5%, 31.2%] |
| ES / PIN073_4 | 2024 | 85 observed dates | availability_delayed|stratum=low_only|compatible_reach | 68.2% [58.8%, 79.1%] |
| ES / PIN073_4 | 2024 | 85 observed dates | availability_delayed|stratum=low_only|definite_print | 31.8% [22.2%, 41.5%] |
| ES / PIN073_4 | 2024 | 31 observed dates | availability_delayed|stratum=neither|compatible_reach | 87.1% [73.3%, 97.1%] |
| ES / PIN073_4 | 2024 | 31 observed dates | availability_delayed|stratum=neither|definite_print | 45.2% [29.2%, 62.1%] |
| ES / PIN073_4 | 2024 | 245 observed dates | nominal|compatible_reach | 71.8% [66.8%, 77.8%] |
| ES / PIN073_4 | 2024 | 245 observed dates | nominal|definite_print | 31.0% [25.6%, 36.4%] |
| ES / PIN073_4 | 2024 | 27 observed dates | nominal|stratum=both|compatible_reach | 88.9% [73.1%, 100.0%] |
| ES / PIN073_4 | 2024 | 27 observed dates | nominal|stratum=both|definite_print | 37.0% [20.0%, 57.7%] |
| ES / PIN073_4 | 2024 | 102 observed dates | nominal|stratum=high_only|compatible_reach | 64.7% [56.4%, 72.6%] |
| ES / PIN073_4 | 2024 | 102 observed dates | nominal|stratum=high_only|definite_print | 24.5% [17.5%, 31.2%] |
| ES / PIN073_4 | 2024 | 85 observed dates | nominal|stratum=low_only|compatible_reach | 69.4% [60.0%, 80.3%] |
| ES / PIN073_4 | 2024 | 85 observed dates | nominal|stratum=low_only|definite_print | 31.8% [22.2%, 41.5%] |
| ES / PIN073_4 | 2024 | 31 observed dates | nominal|stratum=neither|compatible_reach | 87.1% [73.3%, 97.1%] |
| ES / PIN073_4 | 2024 | 31 observed dates | nominal|stratum=neither|definite_print | 45.2% [29.2%, 62.1%] |
| ES / PIN073_5 | 2020 | 247 / 253 | availability_delayed | candidate_available: 247; formation_unavailable: 6 |
| ES / PIN073_5 | 2020 | 247 / 253 | nominal | candidate_available: 247; formation_unavailable: 6 |
| ES / PIN073_5 | 2020 | 247 observed dates | availability_delayed|compatible_reach | 66.4% [61.1%, 71.8%] |
| ES / PIN073_5 | 2020 | 247 observed dates | availability_delayed|definite_print | 25.9% [20.2%, 31.1%] |
| ES / PIN073_5 | 2020 | 23 observed dates | availability_delayed|stratum=both|compatible_reach | 78.3% [61.9%, 94.1%] |
| ES / PIN073_5 | 2020 | 23 observed dates | availability_delayed|stratum=both|definite_print | 39.1% [18.7%, 60.6%] |
| ES / PIN073_5 | 2020 | 117 observed dates | availability_delayed|stratum=high_only|compatible_reach | 61.5% [54.2%, 70.3%] |
| ES / PIN073_5 | 2020 | 117 observed dates | availability_delayed|stratum=high_only|definite_print | 17.9% [11.3%, 25.0%] |
| ES / PIN073_5 | 2020 | 79 observed dates | availability_delayed|stratum=low_only|compatible_reach | 60.8% [49.4%, 70.9%] |
| ES / PIN073_5 | 2020 | 79 observed dates | availability_delayed|stratum=low_only|definite_print | 26.6% [16.4%, 35.1%] |
| ES / PIN073_5 | 2020 | 28 observed dates | availability_delayed|stratum=neither|compatible_reach | 92.9% [81.5%, 100.0%] |
| ES / PIN073_5 | 2020 | 28 observed dates | availability_delayed|stratum=neither|definite_print | 46.4% [25.0%, 64.9%] |
| ES / PIN073_5 | 2020 | 247 observed dates | nominal|compatible_reach | 68.4% [63.0%, 74.2%] |
| ES / PIN073_5 | 2020 | 247 observed dates | nominal|definite_print | 27.1% [21.3%, 32.4%] |
| ES / PIN073_5 | 2020 | 23 observed dates | nominal|stratum=both|compatible_reach | 82.6% [66.7%, 95.8%] |
| ES / PIN073_5 | 2020 | 23 observed dates | nominal|stratum=both|definite_print | 43.5% [22.7%, 65.0%] |
| ES / PIN073_5 | 2020 | 117 observed dates | nominal|stratum=high_only|compatible_reach | 62.4% [55.4%, 70.7%] |
| ES / PIN073_5 | 2020 | 117 observed dates | nominal|stratum=high_only|definite_print | 18.8% [11.9%, 26.0%] |
| ES / PIN073_5 | 2020 | 79 observed dates | nominal|stratum=low_only|compatible_reach | 63.3% [52.2%, 73.3%] |
| ES / PIN073_5 | 2020 | 79 observed dates | nominal|stratum=low_only|definite_print | 27.8% [17.4%, 36.1%] |
| ES / PIN073_5 | 2020 | 28 observed dates | nominal|stratum=neither|compatible_reach | 96.4% [87.5%, 100.0%] |
| ES / PIN073_5 | 2020 | 28 observed dates | nominal|stratum=neither|definite_print | 46.4% [25.0%, 64.9%] |
| ES / PIN073_5 | 2021 | 247 / 252 | availability_delayed | candidate_available: 247; formation_unavailable: 5 |
| ES / PIN073_5 | 2021 | 247 / 252 | nominal | candidate_available: 247; formation_unavailable: 5 |
| ES / PIN073_5 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 64.4% [58.7%, 69.8%] |
| ES / PIN073_5 | 2021 | 247 observed dates | availability_delayed|definite_print | 29.1% [23.6%, 34.4%] |
| ES / PIN073_5 | 2021 | 29 observed dates | availability_delayed|stratum=both|compatible_reach | 55.2% [36.4%, 73.1%] |
| ES / PIN073_5 | 2021 | 29 observed dates | availability_delayed|stratum=both|definite_print | 17.2% [3.8%, 32.0%] |
| ES / PIN073_5 | 2021 | 119 observed dates | availability_delayed|stratum=high_only|compatible_reach | 63.0% [52.7%, 72.7%] |
| ES / PIN073_5 | 2021 | 119 observed dates | availability_delayed|stratum=high_only|definite_print | 31.1% [24.4%, 39.3%] |
| ES / PIN073_5 | 2021 | 72 observed dates | availability_delayed|stratum=low_only|compatible_reach | 63.9% [54.1%, 73.6%] |
| ES / PIN073_5 | 2021 | 72 observed dates | availability_delayed|stratum=low_only|definite_print | 30.6% [21.1%, 40.3%] |
| ES / PIN073_5 | 2021 | 27 observed dates | availability_delayed|stratum=neither|compatible_reach | 81.5% [66.7%, 93.5%] |
| ES / PIN073_5 | 2021 | 27 observed dates | availability_delayed|stratum=neither|definite_print | 29.6% [10.5%, 48.4%] |
| ES / PIN073_5 | 2021 | 247 observed dates | nominal|compatible_reach | 64.8% [58.9%, 70.3%] |
| ES / PIN073_5 | 2021 | 247 observed dates | nominal|definite_print | 29.1% [23.6%, 34.4%] |
| ES / PIN073_5 | 2021 | 29 observed dates | nominal|stratum=both|compatible_reach | 58.6% [38.5%, 76.9%] |
| ES / PIN073_5 | 2021 | 29 observed dates | nominal|stratum=both|definite_print | 17.2% [3.8%, 32.0%] |
| ES / PIN073_5 | 2021 | 119 observed dates | nominal|stratum=high_only|compatible_reach | 63.0% [52.7%, 72.7%] |
| ES / PIN073_5 | 2021 | 119 observed dates | nominal|stratum=high_only|definite_print | 31.1% [24.4%, 39.3%] |
| ES / PIN073_5 | 2021 | 72 observed dates | nominal|stratum=low_only|compatible_reach | 63.9% [54.1%, 73.6%] |
| ES / PIN073_5 | 2021 | 72 observed dates | nominal|stratum=low_only|definite_print | 30.6% [21.1%, 40.3%] |
| ES / PIN073_5 | 2021 | 27 observed dates | nominal|stratum=neither|compatible_reach | 81.5% [66.7%, 93.5%] |
| ES / PIN073_5 | 2021 | 27 observed dates | nominal|stratum=neither|definite_print | 29.6% [10.5%, 48.4%] |
| ES / PIN073_5 | 2022 | 246 / 251 | availability_delayed | candidate_available: 246; formation_unavailable: 5 |
| ES / PIN073_5 | 2022 | 246 / 251 | nominal | candidate_available: 246; formation_unavailable: 5 |
| ES / PIN073_5 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 54.1% [49.0%, 60.0%] |
| ES / PIN073_5 | 2022 | 246 observed dates | availability_delayed|definite_print | 19.5% [14.6%, 25.3%] |
| ES / PIN073_5 | 2022 | 24 observed dates | availability_delayed|stratum=both|compatible_reach | 62.5% [43.5%, 80.0%] |
| ES / PIN073_5 | 2022 | 24 observed dates | availability_delayed|stratum=both|definite_print | 29.2% [11.8%, 47.5%] |
| ES / PIN073_5 | 2022 | 109 observed dates | availability_delayed|stratum=high_only|compatible_reach | 49.5% [40.5%, 58.3%] |
| ES / PIN073_5 | 2022 | 109 observed dates | availability_delayed|stratum=high_only|definite_print | 15.6% [8.6%, 23.9%] |
| ES / PIN073_5 | 2022 | 97 observed dates | availability_delayed|stratum=low_only|compatible_reach | 55.7% [46.2%, 65.6%] |
| ES / PIN073_5 | 2022 | 97 observed dates | availability_delayed|stratum=low_only|definite_print | 21.6% [13.3%, 31.6%] |
| ES / PIN073_5 | 2022 | 16 observed dates | availability_delayed|stratum=neither|compatible_reach | 62.5% [42.8%, 89.5%] |
| ES / PIN073_5 | 2022 | 16 observed dates | availability_delayed|stratum=neither|definite_print | 18.8% [0.0%, 42.9%] |
| ES / PIN073_5 | 2022 | 246 observed dates | nominal|compatible_reach | 54.5% [49.0%, 60.0%] |
| ES / PIN073_5 | 2022 | 246 observed dates | nominal|definite_print | 19.5% [14.6%, 25.3%] |
| ES / PIN073_5 | 2022 | 24 observed dates | nominal|stratum=both|compatible_reach | 62.5% [43.5%, 80.0%] |
| ES / PIN073_5 | 2022 | 24 observed dates | nominal|stratum=both|definite_print | 29.2% [11.8%, 47.5%] |
| ES / PIN073_5 | 2022 | 109 observed dates | nominal|stratum=high_only|compatible_reach | 49.5% [40.5%, 58.3%] |
| ES / PIN073_5 | 2022 | 109 observed dates | nominal|stratum=high_only|definite_print | 15.6% [8.6%, 23.9%] |
| ES / PIN073_5 | 2022 | 97 observed dates | nominal|stratum=low_only|compatible_reach | 55.7% [46.2%, 65.6%] |
| ES / PIN073_5 | 2022 | 97 observed dates | nominal|stratum=low_only|definite_print | 21.6% [13.3%, 31.6%] |
| ES / PIN073_5 | 2022 | 16 observed dates | nominal|stratum=neither|compatible_reach | 68.8% [43.7%, 90.5%] |
| ES / PIN073_5 | 2022 | 16 observed dates | nominal|stratum=neither|definite_print | 18.8% [0.0%, 42.9%] |
| ES / PIN073_5 | 2023 | 244 / 250 | availability_delayed | candidate_available: 244; formation_unavailable: 6 |
| ES / PIN073_5 | 2023 | 244 / 250 | nominal | candidate_available: 244; formation_unavailable: 6 |
| ES / PIN073_5 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 53.7% [47.8%, 59.3%] |
| ES / PIN073_5 | 2023 | 244 observed dates | availability_delayed|definite_print | 24.2% [19.4%, 28.7%] |
| ES / PIN073_5 | 2023 | 33 observed dates | availability_delayed|stratum=both|compatible_reach | 75.8% [64.5%, 90.9%] |
| ES / PIN073_5 | 2023 | 33 observed dates | availability_delayed|stratum=both|definite_print | 39.4% [23.3%, 56.4%] |
| ES / PIN073_5 | 2023 | 117 observed dates | availability_delayed|stratum=high_only|compatible_reach | 50.4% [40.0%, 60.0%] |
| ES / PIN073_5 | 2023 | 117 observed dates | availability_delayed|stratum=high_only|definite_print | 21.4% [14.5%, 28.9%] |
| ES / PIN073_5 | 2023 | 81 observed dates | availability_delayed|stratum=low_only|compatible_reach | 45.7% [35.5%, 55.6%] |
| ES / PIN073_5 | 2023 | 81 observed dates | availability_delayed|stratum=low_only|definite_print | 19.8% [10.4%, 29.6%] |
| ES / PIN073_5 | 2023 | 13 observed dates | availability_delayed|stratum=neither|compatible_reach | 76.9% [53.3%, 100.0%] |
| ES / PIN073_5 | 2023 | 13 observed dates | availability_delayed|stratum=neither|definite_print | 38.5% [10.0%, 62.5%] |
| ES / PIN073_5 | 2023 | 244 observed dates | nominal|compatible_reach | 54.5% [48.8%, 60.0%] |
| ES / PIN073_5 | 2023 | 244 observed dates | nominal|definite_print | 24.6% [19.8%, 29.3%] |
| ES / PIN073_5 | 2023 | 33 observed dates | nominal|stratum=both|compatible_reach | 75.8% [64.5%, 90.9%] |
| ES / PIN073_5 | 2023 | 33 observed dates | nominal|stratum=both|definite_print | 39.4% [23.3%, 56.4%] |
| ES / PIN073_5 | 2023 | 117 observed dates | nominal|stratum=high_only|compatible_reach | 52.1% [42.5%, 60.8%] |
| ES / PIN073_5 | 2023 | 117 observed dates | nominal|stratum=high_only|definite_print | 22.2% [15.6%, 29.4%] |
| ES / PIN073_5 | 2023 | 81 observed dates | nominal|stratum=low_only|compatible_reach | 45.7% [35.5%, 55.6%] |
| ES / PIN073_5 | 2023 | 81 observed dates | nominal|stratum=low_only|definite_print | 19.8% [10.4%, 29.6%] |
| ES / PIN073_5 | 2023 | 13 observed dates | nominal|stratum=neither|compatible_reach | 76.9% [53.3%, 100.0%] |
| ES / PIN073_5 | 2023 | 13 observed dates | nominal|stratum=neither|definite_print | 38.5% [10.0%, 62.5%] |
| ES / PIN073_5 | 2024 | 245 / 252 | availability_delayed | candidate_available: 245; formation_unavailable: 7 |
| ES / PIN073_5 | 2024 | 245 / 252 | nominal | candidate_available: 245; formation_unavailable: 7 |
| ES / PIN073_5 | 2024 | 245 observed dates | availability_delayed|compatible_reach | 68.6% [62.6%, 73.6%] |
| ES / PIN073_5 | 2024 | 245 observed dates | availability_delayed|definite_print | 28.2% [22.9%, 34.2%] |
| ES / PIN073_5 | 2024 | 27 observed dates | availability_delayed|stratum=both|compatible_reach | 66.7% [44.0%, 85.3%] |
| ES / PIN073_5 | 2024 | 27 observed dates | availability_delayed|stratum=both|definite_print | 40.7% [23.5%, 59.1%] |
| ES / PIN073_5 | 2024 | 101 observed dates | availability_delayed|stratum=high_only|compatible_reach | 58.4% [48.6%, 67.1%] |
| ES / PIN073_5 | 2024 | 101 observed dates | availability_delayed|stratum=high_only|definite_print | 27.7% [19.0%, 37.0%] |
| ES / PIN073_5 | 2024 | 83 observed dates | availability_delayed|stratum=low_only|compatible_reach | 74.7% [65.8%, 82.4%] |
| ES / PIN073_5 | 2024 | 83 observed dates | availability_delayed|stratum=low_only|definite_print | 20.5% [12.5%, 30.0%] |
| ES / PIN073_5 | 2024 | 34 observed dates | availability_delayed|stratum=neither|compatible_reach | 85.3% [71.4%, 96.8%] |
| ES / PIN073_5 | 2024 | 34 observed dates | availability_delayed|stratum=neither|definite_print | 38.2% [25.8%, 55.9%] |
| ES / PIN073_5 | 2024 | 245 observed dates | nominal|compatible_reach | 69.8% [63.9%, 74.7%] |
| ES / PIN073_5 | 2024 | 245 observed dates | nominal|definite_print | 29.4% [24.3%, 35.4%] |
| ES / PIN073_5 | 2024 | 27 observed dates | nominal|stratum=both|compatible_reach | 70.4% [51.7%, 86.7%] |
| ES / PIN073_5 | 2024 | 27 observed dates | nominal|stratum=both|definite_print | 44.4% [28.0%, 61.9%] |
| ES / PIN073_5 | 2024 | 101 observed dates | nominal|stratum=high_only|compatible_reach | 59.4% [49.5%, 68.6%] |
| ES / PIN073_5 | 2024 | 101 observed dates | nominal|stratum=high_only|definite_print | 28.7% [20.0%, 38.1%] |
| ES / PIN073_5 | 2024 | 83 observed dates | nominal|stratum=low_only|compatible_reach | 74.7% [65.8%, 82.4%] |
| ES / PIN073_5 | 2024 | 83 observed dates | nominal|stratum=low_only|definite_print | 20.5% [12.5%, 30.0%] |
| ES / PIN073_5 | 2024 | 34 observed dates | nominal|stratum=neither|compatible_reach | 88.2% [75.7%, 100.0%] |
| ES / PIN073_5 | 2024 | 34 observed dates | nominal|stratum=neither|definite_print | 41.2% [28.6%, 57.9%] |
| ES / PIN074_ref_00 | 2020 | 248 / 253 | availability_delayed | candidate_available: 248; forecast_open_unavailable: 2; reference_open_unavailable: 3 |
| ES / PIN074_ref_00 | 2020 | 248 / 253 | nominal | candidate_available: 248; forecast_open_unavailable: 2; reference_open_unavailable: 3 |
| ES / PIN074_ref_00 | 2020 | 241 observed dates | availability_delayed|compatible_reach | 81.3% [76.0%, 85.5%] |
| ES / PIN074_ref_00 | 2020 | 241 observed dates | availability_delayed|definite_print | 38.2% [32.4%, 44.1%] |
| ES / PIN074_ref_00 | 2020 | 241 observed dates | nominal|compatible_reach | 81.3% [76.0%, 85.5%] |
| ES / PIN074_ref_00 | 2020 | 241 observed dates | nominal|definite_print | 38.2% [32.4%, 44.1%] |
| ES / PIN074_ref_00 | 2021 | 251 / 252 | availability_delayed | candidate_available: 251; reference_open_unavailable: 1 |
| ES / PIN074_ref_00 | 2021 | 251 / 252 | nominal | candidate_available: 251; reference_open_unavailable: 1 |
| ES / PIN074_ref_00 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 85.4% [81.0%, 89.4%] |
| ES / PIN074_ref_00 | 2021 | 247 observed dates | availability_delayed|definite_print | 40.9% [34.4%, 46.8%] |
| ES / PIN074_ref_00 | 2021 | 247 observed dates | nominal|compatible_reach | 85.4% [81.0%, 89.4%] |
| ES / PIN074_ref_00 | 2021 | 247 observed dates | nominal|definite_print | 40.9% [34.4%, 46.8%] |
| ES / PIN074_ref_00 | 2022 | 250 / 251 | availability_delayed | candidate_available: 250; reference_open_unavailable: 1 |
| ES / PIN074_ref_00 | 2022 | 250 / 251 | nominal | candidate_available: 250; reference_open_unavailable: 1 |
| ES / PIN074_ref_00 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 82.9% [77.9%, 87.4%] |
| ES / PIN074_ref_00 | 2022 | 246 observed dates | availability_delayed|definite_print | 42.3% [35.8%, 48.6%] |
| ES / PIN074_ref_00 | 2022 | 246 observed dates | nominal|compatible_reach | 84.1% [78.9%, 88.7%] |
| ES / PIN074_ref_00 | 2022 | 246 observed dates | nominal|definite_print | 43.9% [37.4%, 50.6%] |
| ES / PIN074_ref_00 | 2023 | 249 / 250 | availability_delayed | candidate_available: 249; reference_open_unavailable: 1 |
| ES / PIN074_ref_00 | 2023 | 249 / 250 | nominal | candidate_available: 249; reference_open_unavailable: 1 |
| ES / PIN074_ref_00 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 88.1% [83.7%, 91.8%] |
| ES / PIN074_ref_00 | 2023 | 244 observed dates | availability_delayed|definite_print | 50.0% [43.1%, 56.7%] |
| ES / PIN074_ref_00 | 2023 | 244 observed dates | nominal|compatible_reach | 88.1% [83.7%, 91.8%] |
| ES / PIN074_ref_00 | 2023 | 244 observed dates | nominal|definite_print | 50.0% [43.1%, 56.7%] |
| ES / PIN074_ref_00 | 2024 | 250 / 252 | availability_delayed | candidate_available: 250; reference_open_unavailable: 2 |
| ES / PIN074_ref_00 | 2024 | 250 / 252 | nominal | candidate_available: 250; reference_open_unavailable: 2 |
| ES / PIN074_ref_00 | 2024 | 245 observed dates | availability_delayed|compatible_reach | 87.8% [85.2%, 92.0%] |
| ES / PIN074_ref_00 | 2024 | 245 observed dates | availability_delayed|definite_print | 38.4% [33.1%, 44.2%] |
| ES / PIN074_ref_00 | 2024 | 245 observed dates | nominal|compatible_reach | 87.8% [85.2%, 92.0%] |
| ES / PIN074_ref_00 | 2024 | 245 observed dates | nominal|definite_print | 38.4% [33.1%, 44.2%] |
| ES / PIN074_ref_01 | 2020 | 250 / 253 | availability_delayed | candidate_available: 250; forecast_open_unavailable: 3 |
| ES / PIN074_ref_01 | 2020 | 250 / 253 | nominal | candidate_available: 250; forecast_open_unavailable: 3 |
| ES / PIN074_ref_01 | 2020 | 241 observed dates | availability_delayed|compatible_reach | 82.6% [77.0%, 86.6%] |
| ES / PIN074_ref_01 | 2020 | 241 observed dates | availability_delayed|definite_print | 43.2% [37.5%, 49.8%] |
| ES / PIN074_ref_01 | 2020 | 241 observed dates | nominal|compatible_reach | 82.6% [77.0%, 86.6%] |
| ES / PIN074_ref_01 | 2020 | 241 observed dates | nominal|definite_print | 43.2% [37.5%, 49.8%] |
| ES / PIN074_ref_01 | 2021 | 251 / 252 | availability_delayed | candidate_available: 251; reference_open_unavailable: 1 |
| ES / PIN074_ref_01 | 2021 | 251 / 252 | nominal | candidate_available: 251; reference_open_unavailable: 1 |
| ES / PIN074_ref_01 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 85.4% [81.3%, 89.0%] |
| ES / PIN074_ref_01 | 2021 | 247 observed dates | availability_delayed|definite_print | 38.9% [33.3%, 44.2%] |
| ES / PIN074_ref_01 | 2021 | 247 observed dates | nominal|compatible_reach | 85.4% [81.3%, 89.0%] |
| ES / PIN074_ref_01 | 2021 | 247 observed dates | nominal|definite_print | 38.9% [33.3%, 44.2%] |
| ES / PIN074_ref_01 | 2022 | 251 / 251 | availability_delayed | candidate_available: 251 |
| ES / PIN074_ref_01 | 2022 | 251 / 251 | nominal | candidate_available: 251 |
| ES / PIN074_ref_01 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 84.6% [79.6%, 88.8%] |
| ES / PIN074_ref_01 | 2022 | 246 observed dates | availability_delayed|definite_print | 38.6% [32.5%, 44.0%] |
| ES / PIN074_ref_01 | 2022 | 246 observed dates | nominal|compatible_reach | 85.4% [80.6%, 89.4%] |
| ES / PIN074_ref_01 | 2022 | 246 observed dates | nominal|definite_print | 38.6% [32.5%, 44.0%] |
| ES / PIN074_ref_01 | 2023 | 250 / 250 | availability_delayed | candidate_available: 250 |
| ES / PIN074_ref_01 | 2023 | 250 / 250 | nominal | candidate_available: 250 |
| ES / PIN074_ref_01 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 88.1% [83.8%, 91.8%] |
| ES / PIN074_ref_01 | 2023 | 244 observed dates | availability_delayed|definite_print | 39.3% [33.3%, 45.9%] |
| ES / PIN074_ref_01 | 2023 | 244 observed dates | nominal|compatible_reach | 88.1% [83.8%, 91.8%] |
| ES / PIN074_ref_01 | 2023 | 244 observed dates | nominal|definite_print | 39.3% [33.3%, 45.9%] |
| ES / PIN074_ref_01 | 2024 | 251 / 252 | availability_delayed | candidate_available: 251; reference_open_unavailable: 1 |
| ES / PIN074_ref_01 | 2024 | 251 / 252 | nominal | candidate_available: 251; reference_open_unavailable: 1 |
| ES / PIN074_ref_01 | 2024 | 245 observed dates | availability_delayed|compatible_reach | 88.2% [85.2%, 92.2%] |
| ES / PIN074_ref_01 | 2024 | 245 observed dates | availability_delayed|definite_print | 41.2% [35.5%, 47.6%] |
| ES / PIN074_ref_01 | 2024 | 245 observed dates | nominal|compatible_reach | 88.2% [85.2%, 92.2%] |
| ES / PIN074_ref_01 | 2024 | 245 observed dates | nominal|definite_print | 41.2% [35.5%, 47.6%] |
| ES / PIN074_ref_03 | 2020 | 250 / 253 | availability_delayed | candidate_available: 250; forecast_open_unavailable: 1; reference_open_unavailable: 2 |
| ES / PIN074_ref_03 | 2020 | 250 / 253 | nominal | candidate_available: 250; forecast_open_unavailable: 1; reference_open_unavailable: 2 |
| ES / PIN074_ref_03 | 2020 | 241 observed dates | availability_delayed|compatible_reach | 86.3% [81.7%, 90.2%] |
| ES / PIN074_ref_03 | 2020 | 241 observed dates | availability_delayed|definite_print | 42.7% [35.6%, 49.2%] |
| ES / PIN074_ref_03 | 2020 | 241 observed dates | nominal|compatible_reach | 86.7% [81.9%, 90.5%] |
| ES / PIN074_ref_03 | 2020 | 241 observed dates | nominal|definite_print | 42.7% [35.6%, 49.2%] |
| ES / PIN074_ref_03 | 2021 | 252 / 252 | availability_delayed | candidate_available: 252 |
| ES / PIN074_ref_03 | 2021 | 252 / 252 | nominal | candidate_available: 252 |
| ES / PIN074_ref_03 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 84.2% [80.1%, 87.9%] |
| ES / PIN074_ref_03 | 2021 | 247 observed dates | availability_delayed|definite_print | 36.4% [29.9%, 42.3%] |
| ES / PIN074_ref_03 | 2021 | 247 observed dates | nominal|compatible_reach | 84.6% [80.5%, 88.2%] |
| ES / PIN074_ref_03 | 2021 | 247 observed dates | nominal|definite_print | 36.8% [30.2%, 42.7%] |
| ES / PIN074_ref_03 | 2022 | 251 / 251 | availability_delayed | candidate_available: 251 |
| ES / PIN074_ref_03 | 2022 | 251 / 251 | nominal | candidate_available: 251 |
| ES / PIN074_ref_03 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 85.8% [81.6%, 89.5%] |
| ES / PIN074_ref_03 | 2022 | 246 observed dates | availability_delayed|definite_print | 37.4% [31.9%, 43.3%] |
| ES / PIN074_ref_03 | 2022 | 246 observed dates | nominal|compatible_reach | 87.0% [82.8%, 90.7%] |
| ES / PIN074_ref_03 | 2022 | 246 observed dates | nominal|definite_print | 37.8% [32.3%, 43.5%] |
| ES / PIN074_ref_03 | 2023 | 250 / 250 | availability_delayed | candidate_available: 250 |
| ES / PIN074_ref_03 | 2023 | 250 / 250 | nominal | candidate_available: 250 |
| ES / PIN074_ref_03 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 88.9% [84.4%, 92.5%] |
| ES / PIN074_ref_03 | 2023 | 244 observed dates | availability_delayed|definite_print | 41.0% [35.7%, 46.9%] |
| ES / PIN074_ref_03 | 2023 | 244 observed dates | nominal|compatible_reach | 89.3% [85.1%, 92.7%] |
| ES / PIN074_ref_03 | 2023 | 244 observed dates | nominal|definite_print | 41.0% [35.7%, 46.9%] |
| ES / PIN074_ref_03 | 2024 | 252 / 252 | availability_delayed | candidate_available: 252 |
| ES / PIN074_ref_03 | 2024 | 252 / 252 | nominal | candidate_available: 252 |
| ES / PIN074_ref_03 | 2024 | 245 observed dates | availability_delayed|compatible_reach | 88.2% [84.8%, 92.3%] |
| ES / PIN074_ref_03 | 2024 | 245 observed dates | availability_delayed|definite_print | 42.9% [38.3%, 49.4%] |
| ES / PIN074_ref_03 | 2024 | 245 observed dates | nominal|compatible_reach | 88.2% [84.8%, 92.3%] |
| ES / PIN074_ref_03 | 2024 | 245 observed dates | nominal|definite_print | 42.9% [38.3%, 49.4%] |
| ES / PIN074_ref_04 | 2020 | 250 / 253 | availability_delayed | candidate_available: 250; forecast_open_unavailable: 3 |
| ES / PIN074_ref_04 | 2020 | 250 / 253 | nominal | candidate_available: 250; forecast_open_unavailable: 3 |
| ES / PIN074_ref_04 | 2020 | 241 observed dates | availability_delayed|compatible_reach | 91.3% [87.2%, 94.8%] |
| ES / PIN074_ref_04 | 2020 | 241 observed dates | availability_delayed|definite_print | 46.5% [40.0%, 53.1%] |
| ES / PIN074_ref_04 | 2020 | 241 observed dates | nominal|compatible_reach | 91.3% [87.2%, 94.8%] |
| ES / PIN074_ref_04 | 2020 | 241 observed dates | nominal|definite_print | 46.5% [40.0%, 53.1%] |
| ES / PIN074_ref_04 | 2021 | 252 / 252 | availability_delayed | candidate_available: 252 |
| ES / PIN074_ref_04 | 2021 | 252 / 252 | nominal | candidate_available: 252 |
| ES / PIN074_ref_04 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 86.2% [81.9%, 89.5%] |
| ES / PIN074_ref_04 | 2021 | 247 observed dates | availability_delayed|definite_print | 42.1% [35.9%, 48.8%] |
| ES / PIN074_ref_04 | 2021 | 247 observed dates | nominal|compatible_reach | 86.6% [82.4%, 89.9%] |
| ES / PIN074_ref_04 | 2021 | 247 observed dates | nominal|definite_print | 42.5% [36.2%, 49.2%] |
| ES / PIN074_ref_04 | 2022 | 251 / 251 | availability_delayed | candidate_available: 251 |
| ES / PIN074_ref_04 | 2022 | 251 / 251 | nominal | candidate_available: 251 |
| ES / PIN074_ref_04 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 90.2% [86.7%, 93.9%] |
| ES / PIN074_ref_04 | 2022 | 246 observed dates | availability_delayed|definite_print | 37.8% [32.3%, 43.9%] |
| ES / PIN074_ref_04 | 2022 | 246 observed dates | nominal|compatible_reach | 90.7% [87.2%, 94.3%] |
| ES / PIN074_ref_04 | 2022 | 246 observed dates | nominal|definite_print | 37.8% [32.3%, 43.9%] |
| ES / PIN074_ref_04 | 2023 | 250 / 250 | availability_delayed | candidate_available: 250 |
| ES / PIN074_ref_04 | 2023 | 250 / 250 | nominal | candidate_available: 250 |
| ES / PIN074_ref_04 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 91.4% [87.6%, 94.4%] |
| ES / PIN074_ref_04 | 2023 | 244 observed dates | availability_delayed|definite_print | 44.7% [37.6%, 50.6%] |
| ES / PIN074_ref_04 | 2023 | 244 observed dates | nominal|compatible_reach | 91.8% [88.4%, 94.7%] |
| ES / PIN074_ref_04 | 2023 | 244 observed dates | nominal|definite_print | 44.7% [37.6%, 50.6%] |
| ES / PIN074_ref_04 | 2024 | 252 / 252 | availability_delayed | candidate_available: 252 |
| ES / PIN074_ref_04 | 2024 | 252 / 252 | nominal | candidate_available: 252 |
| ES / PIN074_ref_04 | 2024 | 245 observed dates | availability_delayed|compatible_reach | 91.0% [87.8%, 94.7%] |
| ES / PIN074_ref_04 | 2024 | 245 observed dates | availability_delayed|definite_print | 45.3% [39.3%, 51.4%] |
| ES / PIN074_ref_04 | 2024 | 245 observed dates | nominal|compatible_reach | 91.0% [87.8%, 94.7%] |
| ES / PIN074_ref_04 | 2024 | 245 observed dates | nominal|definite_print | 45.3% [39.3%, 51.4%] |
| ES / PIN074_ref_07 | 2020 | 250 / 253 | availability_delayed | candidate_available: 250; reference_open_unavailable: 3 |
| ES / PIN074_ref_07 | 2020 | 250 / 253 | nominal | candidate_available: 250; reference_open_unavailable: 3 |
| ES / PIN074_ref_07 | 2020 | 241 observed dates | availability_delayed|compatible_reach | 94.2% [91.7%, 96.7%] |
| ES / PIN074_ref_07 | 2020 | 241 observed dates | availability_delayed|definite_print | 45.2% [38.8%, 52.2%] |
| ES / PIN074_ref_07 | 2020 | 241 observed dates | nominal|compatible_reach | 94.6% [92.1%, 97.1%] |
| ES / PIN074_ref_07 | 2020 | 241 observed dates | nominal|definite_print | 45.2% [38.8%, 52.2%] |
| ES / PIN074_ref_07 | 2021 | 252 / 252 | availability_delayed | candidate_available: 252 |
| ES / PIN074_ref_07 | 2021 | 252 / 252 | nominal | candidate_available: 252 |
| ES / PIN074_ref_07 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 91.5% [88.3%, 94.3%] |
| ES / PIN074_ref_07 | 2021 | 247 observed dates | availability_delayed|definite_print | 41.7% [36.0%, 47.8%] |
| ES / PIN074_ref_07 | 2021 | 247 observed dates | nominal|compatible_reach | 91.9% [88.6%, 94.7%] |
| ES / PIN074_ref_07 | 2021 | 247 observed dates | nominal|definite_print | 42.1% [36.2%, 47.8%] |
| ES / PIN074_ref_07 | 2022 | 251 / 251 | availability_delayed | candidate_available: 251 |
| ES / PIN074_ref_07 | 2022 | 251 / 251 | nominal | candidate_available: 251 |
| ES / PIN074_ref_07 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 94.7% [92.4%, 97.2%] |
| ES / PIN074_ref_07 | 2022 | 246 observed dates | availability_delayed|definite_print | 41.5% [36.1%, 48.4%] |
| ES / PIN074_ref_07 | 2022 | 246 observed dates | nominal|compatible_reach | 95.9% [93.9%, 98.3%] |
| ES / PIN074_ref_07 | 2022 | 246 observed dates | nominal|definite_print | 41.5% [36.1%, 48.4%] |
| ES / PIN074_ref_07 | 2023 | 250 / 250 | availability_delayed | candidate_available: 250 |
| ES / PIN074_ref_07 | 2023 | 250 / 250 | nominal | candidate_available: 250 |
| ES / PIN074_ref_07 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 93.4% [89.8%, 96.3%] |
| ES / PIN074_ref_07 | 2023 | 244 observed dates | availability_delayed|definite_print | 43.0% [37.3%, 48.3%] |
| ES / PIN074_ref_07 | 2023 | 244 observed dates | nominal|compatible_reach | 94.3% [90.8%, 96.7%] |
| ES / PIN074_ref_07 | 2023 | 244 observed dates | nominal|definite_print | 43.0% [37.3%, 48.3%] |
| ES / PIN074_ref_07 | 2024 | 252 / 252 | availability_delayed | candidate_available: 252 |
| ES / PIN074_ref_07 | 2024 | 252 / 252 | nominal | candidate_available: 252 |
| ES / PIN074_ref_07 | 2024 | 245 observed dates | availability_delayed|compatible_reach | 96.7% [93.9%, 99.2%] |
| ES / PIN074_ref_07 | 2024 | 245 observed dates | availability_delayed|definite_print | 44.9% [39.2%, 51.2%] |
| ES / PIN074_ref_07 | 2024 | 245 observed dates | nominal|compatible_reach | 97.6% [95.0%, 99.6%] |
| ES / PIN074_ref_07 | 2024 | 245 observed dates | nominal|definite_print | 44.9% [39.2%, 51.2%] |
| ES / PIN076_00_08 | 2020 | 248 / 253 | availability_delayed | candidate_available: 248; forecast_open_unavailable: 2; reference_open_unavailable: 3 |
| ES / PIN076_00_08 | 2020 | 248 / 253 | nominal | candidate_available: 248; forecast_open_unavailable: 2; reference_open_unavailable: 3 |
| ES / PIN076_00_08 | 2020 | 241 observed dates | availability_delayed|compatible_reach | 81.3% [76.0%, 85.5%] |
| ES / PIN076_00_08 | 2020 | 241 observed dates | availability_delayed|definite_print | 38.2% [32.4%, 44.1%] |
| ES / PIN076_00_08 | 2020 | 241 observed dates | nominal|compatible_reach | 81.3% [76.0%, 85.5%] |
| ES / PIN076_00_08 | 2020 | 241 observed dates | nominal|definite_print | 38.2% [32.4%, 44.1%] |
| ES / PIN076_00_08 | 2021 | 251 / 252 | availability_delayed | candidate_available: 251; reference_open_unavailable: 1 |
| ES / PIN076_00_08 | 2021 | 251 / 252 | nominal | candidate_available: 251; reference_open_unavailable: 1 |
| ES / PIN076_00_08 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 85.4% [81.0%, 89.4%] |
| ES / PIN076_00_08 | 2021 | 247 observed dates | availability_delayed|definite_print | 40.9% [34.4%, 46.8%] |
| ES / PIN076_00_08 | 2021 | 247 observed dates | nominal|compatible_reach | 85.4% [81.0%, 89.4%] |
| ES / PIN076_00_08 | 2021 | 247 observed dates | nominal|definite_print | 40.9% [34.4%, 46.8%] |
| ES / PIN076_00_08 | 2022 | 250 / 251 | availability_delayed | candidate_available: 250; reference_open_unavailable: 1 |
| ES / PIN076_00_08 | 2022 | 250 / 251 | nominal | candidate_available: 250; reference_open_unavailable: 1 |
| ES / PIN076_00_08 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 82.9% [77.9%, 87.4%] |
| ES / PIN076_00_08 | 2022 | 246 observed dates | availability_delayed|definite_print | 42.3% [35.8%, 48.6%] |
| ES / PIN076_00_08 | 2022 | 246 observed dates | nominal|compatible_reach | 84.1% [78.9%, 88.7%] |
| ES / PIN076_00_08 | 2022 | 246 observed dates | nominal|definite_print | 43.9% [37.4%, 50.6%] |
| ES / PIN076_00_08 | 2023 | 249 / 250 | availability_delayed | candidate_available: 249; reference_open_unavailable: 1 |
| ES / PIN076_00_08 | 2023 | 249 / 250 | nominal | candidate_available: 249; reference_open_unavailable: 1 |
| ES / PIN076_00_08 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 88.1% [83.7%, 91.8%] |
| ES / PIN076_00_08 | 2023 | 244 observed dates | availability_delayed|definite_print | 50.0% [43.1%, 56.7%] |
| ES / PIN076_00_08 | 2023 | 244 observed dates | nominal|compatible_reach | 88.1% [83.7%, 91.8%] |
| ES / PIN076_00_08 | 2023 | 244 observed dates | nominal|definite_print | 50.0% [43.1%, 56.7%] |
| ES / PIN076_00_08 | 2024 | 250 / 252 | availability_delayed | candidate_available: 250; reference_open_unavailable: 2 |
| ES / PIN076_00_08 | 2024 | 250 / 252 | nominal | candidate_available: 250; reference_open_unavailable: 2 |
| ES / PIN076_00_08 | 2024 | 245 observed dates | availability_delayed|compatible_reach | 87.8% [85.2%, 92.0%] |
| ES / PIN076_00_08 | 2024 | 245 observed dates | availability_delayed|definite_print | 38.4% [33.1%, 44.2%] |
| ES / PIN076_00_08 | 2024 | 245 observed dates | nominal|compatible_reach | 87.8% [85.2%, 92.0%] |
| ES / PIN076_00_08 | 2024 | 245 observed dates | nominal|definite_print | 38.4% [33.1%, 44.2%] |
| ES / PIN076_08_0930 | 2020 | 246 / 253 | availability_delayed | candidate_available: 246; forecast_open_unavailable: 4; reference_open_unavailable: 3 |
| ES / PIN076_08_0930 | 2020 | 246 / 253 | nominal | candidate_available: 246; forecast_open_unavailable: 4; reference_open_unavailable: 3 |
| ES / PIN076_08_0930 | 2020 | 243 observed dates | availability_delayed|compatible_reach | 87.2% [82.8%, 91.5%] |
| ES / PIN076_08_0930 | 2020 | 243 observed dates | availability_delayed|definite_print | 38.3% [33.2%, 44.2%] |
| ES / PIN076_08_0930 | 2020 | 243 observed dates | nominal|compatible_reach | 92.2% [88.6%, 95.1%] |
| ES / PIN076_08_0930 | 2020 | 243 observed dates | nominal|definite_print | 39.5% [34.2%, 45.4%] |
| ES / PIN076_08_0930 | 2021 | 248 / 252 | availability_delayed | candidate_available: 248; forecast_open_unavailable: 4 |
| ES / PIN076_08_0930 | 2021 | 248 / 252 | nominal | candidate_available: 248; forecast_open_unavailable: 4 |
| ES / PIN076_08_0930 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 85.0% [80.9%, 89.3%] |
| ES / PIN076_08_0930 | 2021 | 247 observed dates | availability_delayed|definite_print | 39.7% [33.6%, 46.0%] |
| ES / PIN076_08_0930 | 2021 | 247 observed dates | nominal|compatible_reach | 88.3% [84.6%, 92.2%] |
| ES / PIN076_08_0930 | 2021 | 247 observed dates | nominal|definite_print | 41.7% [35.5%, 48.6%] |
| ES / PIN076_08_0930 | 2022 | 247 / 251 | availability_delayed | candidate_available: 247; forecast_open_unavailable: 4 |
| ES / PIN076_08_0930 | 2022 | 247 / 251 | nominal | candidate_available: 247; forecast_open_unavailable: 4 |
| ES / PIN076_08_0930 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 85.4% [80.9%, 89.3%] |
| ES / PIN076_08_0930 | 2022 | 246 observed dates | availability_delayed|definite_print | 39.0% [34.0%, 43.3%] |
| ES / PIN076_08_0930 | 2022 | 246 observed dates | nominal|compatible_reach | 88.2% [84.4%, 91.5%] |
| ES / PIN076_08_0930 | 2022 | 246 observed dates | nominal|definite_print | 40.2% [35.1%, 44.5%] |
| ES / PIN076_08_0930 | 2023 | 246 / 250 | availability_delayed | candidate_available: 246; forecast_open_unavailable: 4 |
| ES / PIN076_08_0930 | 2023 | 246 / 250 | nominal | candidate_available: 246; forecast_open_unavailable: 4 |
| ES / PIN076_08_0930 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 88.1% [83.6%, 92.2%] |
| ES / PIN076_08_0930 | 2023 | 244 observed dates | availability_delayed|definite_print | 36.9% [31.6%, 43.0%] |
| ES / PIN076_08_0930 | 2023 | 244 observed dates | nominal|compatible_reach | 90.2% [85.8%, 93.9%] |
| ES / PIN076_08_0930 | 2023 | 244 observed dates | nominal|definite_print | 38.1% [33.1%, 44.3%] |
| ES / PIN076_08_0930 | 2024 | 248 / 252 | availability_delayed | candidate_available: 248; forecast_open_unavailable: 4 |
| ES / PIN076_08_0930 | 2024 | 248 / 252 | nominal | candidate_available: 248; forecast_open_unavailable: 4 |
| ES / PIN076_08_0930 | 2024 | 245 observed dates | availability_delayed|compatible_reach | 86.9% [82.2%, 91.0%] |
| ES / PIN076_08_0930 | 2024 | 245 observed dates | availability_delayed|definite_print | 44.1% [37.7%, 50.0%] |
| ES / PIN076_08_0930 | 2024 | 245 observed dates | nominal|compatible_reach | 89.4% [85.3%, 93.0%] |
| ES / PIN076_08_0930 | 2024 | 245 observed dates | nominal|definite_print | 44.1% [37.7%, 50.0%] |
| ES / PIN078_daily_not_combined | 2020 | 0 / 100 | availability_delayed | formation_unavailable: 100 |
| ES / PIN078_daily_not_combined | 2020 | 0 / 100 | nominal | formation_unavailable: 100 |

ES 2020: Monday and Tuesday source ranges remain separate daily candidates. Repeated compatible bars and unique contact dates answer different questions.

| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |
|---|---:|---|---|---:|

Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| ES / PIN078_daily_not_combined | 2021 | 26 / 99 | availability_delayed | candidate_available: 26; formation_unavailable: 73 |
| ES / PIN078_daily_not_combined | 2021 | 26 / 99 | nominal | candidate_available: 26; formation_unavailable: 73 |

ES 2021: Monday and Tuesday source ranges remain separate daily candidates. Repeated compatible bars and unique contact dates answer different questions.

| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |
|---|---:|---|---|---:|
| fib1_actual_30pct | 0 / 99 | 0 / unavailable | 0 / unavailable | 0 |
| fib2_actual_70pct | 0 / 99 | 0 / unavailable | 0 / unavailable | 0 |
| high | 0 / 99 | 0 / unavailable | 0 / unavailable | 0 |
| low | 0 / 99 | 0 / unavailable | 0 / unavailable | 0 |
| midpoint | 0 / 99 | 0 / unavailable | 0 / unavailable | 0 |

Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| ES / PIN078_daily_not_combined | 2022 | 58 / 97 | availability_delayed | candidate_available: 58; formation_unavailable: 39 |
| ES / PIN078_daily_not_combined | 2022 | 58 / 97 | nominal | candidate_available: 58; formation_unavailable: 39 |

ES 2022: Monday and Tuesday source ranges remain separate daily candidates. Repeated compatible bars and unique contact dates answer different questions.

| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |
|---|---:|---|---|---:|
| fib1_actual_30pct | 0 / 97 | 0 / unavailable | 0 / unavailable | 0 |
| fib2_actual_70pct | 0 / 97 | 0 / unavailable | 0 / unavailable | 0 |
| high | 0 / 97 | 0 / unavailable | 0 / unavailable | 0 |
| low | 0 / 97 | 0 / unavailable | 0 / unavailable | 0 |
| midpoint | 0 / 97 | 0 / unavailable | 0 / unavailable | 0 |

Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| ES / PIN078_daily_not_combined | 2023 | 37 / 96 | availability_delayed | candidate_available: 37; formation_unavailable: 59 |
| ES / PIN078_daily_not_combined | 2023 | 37 / 96 | nominal | candidate_available: 37; formation_unavailable: 59 |

ES 2023: Monday and Tuesday source ranges remain separate daily candidates. Repeated compatible bars and unique contact dates answer different questions.

| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |
|---|---:|---|---|---:|
| fib1_actual_30pct | 0 / 96 | 0 / unavailable | 0 / unavailable | 0 |
| fib2_actual_70pct | 0 / 96 | 0 / unavailable | 0 / unavailable | 0 |
| high | 0 / 96 | 0 / unavailable | 0 / unavailable | 0 |
| low | 0 / 96 | 0 / unavailable | 0 / unavailable | 0 |
| midpoint | 0 / 96 | 0 / unavailable | 0 / unavailable | 0 |

Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| ES / PIN078_daily_not_combined | 2024 | 39 / 101 | availability_delayed | candidate_available: 39; formation_unavailable: 62 |
| ES / PIN078_daily_not_combined | 2024 | 39 / 101 | nominal | candidate_available: 39; formation_unavailable: 62 |

ES 2024: Monday and Tuesday source ranges remain separate daily candidates. Repeated compatible bars and unique contact dates answer different questions.

| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |
|---|---:|---|---|---:|
| fib1_actual_30pct | 0 / 101 | 0 / unavailable | 0 / unavailable | 0 |
| fib2_actual_70pct | 0 / 101 | 0 / unavailable | 0 / unavailable | 0 |
| high | 0 / 101 | 0 / unavailable | 0 / unavailable | 0 |
| low | 0 / 101 | 0 / unavailable | 0 / unavailable | 0 |
| midpoint | 0 / 101 | 0 / unavailable | 0 / unavailable | 0 |

Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| ES / magic_00 | 2020 | 235 / 253 | availability_delayed | break_then_neither_by_horizon: 8; competing_order_ambiguous: 1; future_censored: 4; invalidation_before_midpoint: 90; midpoint_before_invalidation: 132 |
| ES / magic_00 | 2020 | 235 / 253 | nominal | break_then_neither_by_horizon: 8; competing_order_ambiguous: 1; future_censored: 4; invalidation_before_midpoint: 89; midpoint_before_invalidation: 133 |
| ES / magic_00 | 2020 | 231 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.5% [1.2%, 6.1%] |
| ES / magic_00 | 2020 | 231 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.5% [1.2%, 6.1%] |
| ES / magic_00 | 2020 | 231 observed dates | availability_delayed|invalidation_before_midpoint_lower | 39.0% [33.3%, 45.2%] |
| ES / magic_00 | 2020 | 231 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.4% [33.8%, 45.6%] |
| ES / magic_00 | 2020 | 231 observed dates | availability_delayed|midpoint_before_invalidation_lower | 57.1% [50.7%, 63.2%] |
| ES / magic_00 | 2020 | 231 observed dates | availability_delayed|midpoint_before_invalidation_upper | 57.6% [51.3%, 63.4%] |
| ES / magic_00 | 2020 | 231 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2020 | 231 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2020 | 231 observed dates | nominal|break_then_neither_by_horizon_lower | 3.5% [1.2%, 6.1%] |
| ES / magic_00 | 2020 | 231 observed dates | nominal|break_then_neither_by_horizon_upper | 3.5% [1.2%, 6.1%] |
| ES / magic_00 | 2020 | 231 observed dates | nominal|invalidation_before_midpoint_lower | 38.5% [32.9%, 44.6%] |
| ES / magic_00 | 2020 | 231 observed dates | nominal|invalidation_before_midpoint_upper | 39.0% [33.3%, 45.0%] |
| ES / magic_00 | 2020 | 231 observed dates | nominal|midpoint_before_invalidation_lower | 57.6% [51.4%, 63.5%] |
| ES / magic_00 | 2020 | 231 observed dates | nominal|midpoint_before_invalidation_upper | 58.0% [51.7%, 63.8%] |
| ES / magic_00 | 2020 | 231 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2020 | 231 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2021 | 219 / 252 | availability_delayed | break_then_neither_by_horizon: 7; competing_order_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 77; midpoint_before_invalidation: 132 |
| ES / magic_00 | 2021 | 219 / 252 | nominal | break_then_neither_by_horizon: 6; competing_order_ambiguous: 4; future_censored: 2; invalidation_before_midpoint: 72; midpoint_before_invalidation: 135 |
| ES / magic_00 | 2021 | 217 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.2% [0.9%, 5.4%] |
| ES / magic_00 | 2021 | 217 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.2% [0.9%, 5.4%] |
| ES / magic_00 | 2021 | 217 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.5% [29.3%, 41.1%] |
| ES / magic_00 | 2021 | 217 observed dates | availability_delayed|invalidation_before_midpoint_upper | 35.9% [29.7%, 41.7%] |
| ES / magic_00 | 2021 | 217 observed dates | availability_delayed|midpoint_before_invalidation_lower | 60.8% [55.5%, 67.0%] |
| ES / magic_00 | 2021 | 217 observed dates | availability_delayed|midpoint_before_invalidation_upper | 61.3% [56.1%, 67.4%] |
| ES / magic_00 | 2021 | 217 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2021 | 217 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2021 | 217 observed dates | nominal|break_then_neither_by_horizon_lower | 2.8% [0.9%, 4.8%] |
| ES / magic_00 | 2021 | 217 observed dates | nominal|break_then_neither_by_horizon_upper | 2.8% [0.9%, 4.8%] |
| ES / magic_00 | 2021 | 217 observed dates | nominal|invalidation_before_midpoint_lower | 33.2% [26.8%, 38.8%] |
| ES / magic_00 | 2021 | 217 observed dates | nominal|invalidation_before_midpoint_upper | 35.0% [28.8%, 40.8%] |
| ES / magic_00 | 2021 | 217 observed dates | nominal|midpoint_before_invalidation_lower | 62.2% [56.5%, 68.5%] |
| ES / magic_00 | 2021 | 217 observed dates | nominal|midpoint_before_invalidation_upper | 64.1% [58.7%, 70.5%] |
| ES / magic_00 | 2021 | 217 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2021 | 217 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2022 | 243 / 251 | availability_delayed | break_then_neither_by_horizon: 3; invalidation_before_midpoint: 74; midpoint_before_invalidation: 165; no_break_by_horizon: 1 |
| ES / magic_00 | 2022 | 243 / 251 | nominal | break_then_neither_by_horizon: 3; competing_order_ambiguous: 1; invalidation_before_midpoint: 72; midpoint_before_invalidation: 166; no_break_by_horizon: 1 |
| ES / magic_00 | 2022 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 1.2% [0.0%, 2.9%] |
| ES / magic_00 | 2022 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 1.2% [0.0%, 2.9%] |
| ES / magic_00 | 2022 | 243 observed dates | availability_delayed|invalidation_before_midpoint_lower | 30.5% [23.9%, 36.8%] |
| ES / magic_00 | 2022 | 243 observed dates | availability_delayed|invalidation_before_midpoint_upper | 30.5% [23.9%, 36.8%] |
| ES / magic_00 | 2022 | 243 observed dates | availability_delayed|midpoint_before_invalidation_lower | 67.9% [61.6%, 74.5%] |
| ES / magic_00 | 2022 | 243 observed dates | availability_delayed|midpoint_before_invalidation_upper | 67.9% [61.6%, 74.5%] |
| ES / magic_00 | 2022 | 243 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| ES / magic_00 | 2022 | 243 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| ES / magic_00 | 2022 | 243 observed dates | nominal|break_then_neither_by_horizon_lower | 1.2% [0.0%, 2.9%] |
| ES / magic_00 | 2022 | 243 observed dates | nominal|break_then_neither_by_horizon_upper | 1.2% [0.0%, 2.9%] |
| ES / magic_00 | 2022 | 243 observed dates | nominal|invalidation_before_midpoint_lower | 29.6% [23.1%, 35.8%] |
| ES / magic_00 | 2022 | 243 observed dates | nominal|invalidation_before_midpoint_upper | 30.0% [23.7%, 36.4%] |
| ES / magic_00 | 2022 | 243 observed dates | nominal|midpoint_before_invalidation_lower | 68.3% [61.8%, 74.7%] |
| ES / magic_00 | 2022 | 243 observed dates | nominal|midpoint_before_invalidation_upper | 68.7% [62.5%, 75.0%] |
| ES / magic_00 | 2022 | 243 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| ES / magic_00 | 2022 | 243 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| ES / magic_00 | 2023 | 196 / 250 | availability_delayed | break_then_neither_by_horizon: 4; competing_order_ambiguous: 1; future_censored: 4; invalidation_before_midpoint: 74; midpoint_before_invalidation: 113 |
| ES / magic_00 | 2023 | 196 / 250 | nominal | break_then_neither_by_horizon: 4; competing_order_ambiguous: 1; future_censored: 4; invalidation_before_midpoint: 74; midpoint_before_invalidation: 113 |
| ES / magic_00 | 2023 | 192 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.1% [0.5%, 4.2%] |
| ES / magic_00 | 2023 | 192 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.1% [0.5%, 4.2%] |
| ES / magic_00 | 2023 | 192 observed dates | availability_delayed|invalidation_before_midpoint_lower | 38.5% [31.7%, 46.4%] |
| ES / magic_00 | 2023 | 192 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.1% [32.6%, 46.8%] |
| ES / magic_00 | 2023 | 192 observed dates | availability_delayed|midpoint_before_invalidation_lower | 58.9% [51.2%, 65.4%] |
| ES / magic_00 | 2023 | 192 observed dates | availability_delayed|midpoint_before_invalidation_upper | 59.4% [51.7%, 65.9%] |
| ES / magic_00 | 2023 | 192 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2023 | 192 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2023 | 192 observed dates | nominal|break_then_neither_by_horizon_lower | 2.1% [0.5%, 4.2%] |
| ES / magic_00 | 2023 | 192 observed dates | nominal|break_then_neither_by_horizon_upper | 2.1% [0.5%, 4.2%] |
| ES / magic_00 | 2023 | 192 observed dates | nominal|invalidation_before_midpoint_lower | 38.5% [31.7%, 46.4%] |
| ES / magic_00 | 2023 | 192 observed dates | nominal|invalidation_before_midpoint_upper | 39.1% [32.6%, 46.8%] |
| ES / magic_00 | 2023 | 192 observed dates | nominal|midpoint_before_invalidation_lower | 58.9% [51.2%, 65.4%] |
| ES / magic_00 | 2023 | 192 observed dates | nominal|midpoint_before_invalidation_upper | 59.4% [51.7%, 65.9%] |
| ES / magic_00 | 2023 | 192 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2023 | 192 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_00 | 2024 | 203 / 252 | availability_delayed | break_then_neither_by_horizon: 4; future_censored: 7; invalidation_before_midpoint: 74; midpoint_before_invalidation: 117; no_break_by_horizon: 1 |
| ES / magic_00 | 2024 | 203 / 252 | nominal | break_then_neither_by_horizon: 4; competing_order_ambiguous: 1; future_censored: 7; invalidation_before_midpoint: 72; midpoint_before_invalidation: 118; no_break_by_horizon: 1 |
| ES / magic_00 | 2024 | 196 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.0% [0.5%, 4.3%] |
| ES / magic_00 | 2024 | 196 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.0% [0.5%, 4.3%] |
| ES / magic_00 | 2024 | 196 observed dates | availability_delayed|invalidation_before_midpoint_lower | 37.8% [31.9%, 43.3%] |
| ES / magic_00 | 2024 | 196 observed dates | availability_delayed|invalidation_before_midpoint_upper | 37.8% [31.9%, 43.3%] |
| ES / magic_00 | 2024 | 196 observed dates | availability_delayed|midpoint_before_invalidation_lower | 59.7% [54.2%, 65.3%] |
| ES / magic_00 | 2024 | 196 observed dates | availability_delayed|midpoint_before_invalidation_upper | 59.7% [54.2%, 65.3%] |
| ES / magic_00 | 2024 | 196 observed dates | availability_delayed|no_break_by_horizon_lower | 0.5% [0.0%, 1.6%] |
| ES / magic_00 | 2024 | 196 observed dates | availability_delayed|no_break_by_horizon_upper | 0.5% [0.0%, 1.6%] |
| ES / magic_00 | 2024 | 196 observed dates | nominal|break_then_neither_by_horizon_lower | 2.0% [0.5%, 4.3%] |
| ES / magic_00 | 2024 | 196 observed dates | nominal|break_then_neither_by_horizon_upper | 2.0% [0.5%, 4.3%] |
| ES / magic_00 | 2024 | 196 observed dates | nominal|invalidation_before_midpoint_lower | 36.7% [31.0%, 42.1%] |
| ES / magic_00 | 2024 | 196 observed dates | nominal|invalidation_before_midpoint_upper | 37.2% [31.5%, 42.7%] |
| ES / magic_00 | 2024 | 196 observed dates | nominal|midpoint_before_invalidation_lower | 60.2% [54.7%, 65.8%] |
| ES / magic_00 | 2024 | 196 observed dates | nominal|midpoint_before_invalidation_upper | 60.7% [55.1%, 66.4%] |
| ES / magic_00 | 2024 | 196 observed dates | nominal|no_break_by_horizon_lower | 0.5% [0.0%, 1.6%] |
| ES / magic_00 | 2024 | 196 observed dates | nominal|no_break_by_horizon_upper | 0.5% [0.0%, 1.6%] |
| ES / magic_01 | 2020 | 240 / 253 | availability_delayed | break_then_neither_by_horizon: 18; competing_order_ambiguous: 1; future_censored: 1; invalidation_before_midpoint: 83; midpoint_before_invalidation: 136; no_break_by_horizon: 1 |
| ES / magic_01 | 2020 | 240 / 253 | nominal | break_then_neither_by_horizon: 18; competing_order_ambiguous: 3; future_censored: 1; invalidation_before_midpoint: 78; midpoint_before_invalidation: 139; no_break_by_horizon: 1 |
| ES / magic_01 | 2020 | 239 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 7.5% [4.5%, 11.3%] |
| ES / magic_01 | 2020 | 239 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 7.5% [4.5%, 11.3%] |
| ES / magic_01 | 2020 | 239 observed dates | availability_delayed|invalidation_before_midpoint_lower | 34.7% [29.6%, 40.8%] |
| ES / magic_01 | 2020 | 239 observed dates | availability_delayed|invalidation_before_midpoint_upper | 35.1% [30.2%, 41.3%] |
| ES / magic_01 | 2020 | 239 observed dates | availability_delayed|midpoint_before_invalidation_lower | 56.9% [50.0%, 62.1%] |
| ES / magic_01 | 2020 | 239 observed dates | availability_delayed|midpoint_before_invalidation_upper | 57.3% [50.4%, 62.5%] |
| ES / magic_01 | 2020 | 239 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| ES / magic_01 | 2020 | 239 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| ES / magic_01 | 2020 | 239 observed dates | nominal|break_then_neither_by_horizon_lower | 7.5% [4.5%, 11.3%] |
| ES / magic_01 | 2020 | 239 observed dates | nominal|break_then_neither_by_horizon_upper | 7.5% [4.5%, 11.3%] |
| ES / magic_01 | 2020 | 239 observed dates | nominal|invalidation_before_midpoint_lower | 32.6% [27.5%, 39.0%] |
| ES / magic_01 | 2020 | 239 observed dates | nominal|invalidation_before_midpoint_upper | 33.9% [28.7%, 39.9%] |
| ES / magic_01 | 2020 | 239 observed dates | nominal|midpoint_before_invalidation_lower | 58.2% [51.4%, 63.4%] |
| ES / magic_01 | 2020 | 239 observed dates | nominal|midpoint_before_invalidation_upper | 59.4% [52.7%, 64.9%] |
| ES / magic_01 | 2020 | 239 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| ES / magic_01 | 2020 | 239 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| ES / magic_01 | 2021 | 242 / 252 | availability_delayed | break_then_neither_by_horizon: 8; future_censored: 3; invalidation_before_midpoint: 92; midpoint_before_invalidation: 138; no_break_by_horizon: 1 |
| ES / magic_01 | 2021 | 242 / 252 | nominal | break_then_neither_by_horizon: 8; competing_order_ambiguous: 1; future_censored: 3; invalidation_before_midpoint: 89; midpoint_before_invalidation: 140; no_break_by_horizon: 1 |
| ES / magic_01 | 2021 | 239 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.3% [1.2%, 5.4%] |
| ES / magic_01 | 2021 | 239 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.3% [1.2%, 5.4%] |
| ES / magic_01 | 2021 | 239 observed dates | availability_delayed|invalidation_before_midpoint_lower | 38.5% [31.8%, 44.1%] |
| ES / magic_01 | 2021 | 239 observed dates | availability_delayed|invalidation_before_midpoint_upper | 38.5% [31.8%, 44.1%] |
| ES / magic_01 | 2021 | 239 observed dates | availability_delayed|midpoint_before_invalidation_lower | 57.7% [51.7%, 64.7%] |
| ES / magic_01 | 2021 | 239 observed dates | availability_delayed|midpoint_before_invalidation_upper | 57.7% [51.7%, 64.7%] |
| ES / magic_01 | 2021 | 239 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| ES / magic_01 | 2021 | 239 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| ES / magic_01 | 2021 | 239 observed dates | nominal|break_then_neither_by_horizon_lower | 3.3% [1.2%, 5.4%] |
| ES / magic_01 | 2021 | 239 observed dates | nominal|break_then_neither_by_horizon_upper | 3.3% [1.2%, 5.4%] |
| ES / magic_01 | 2021 | 239 observed dates | nominal|invalidation_before_midpoint_lower | 37.2% [30.7%, 42.7%] |
| ES / magic_01 | 2021 | 239 observed dates | nominal|invalidation_before_midpoint_upper | 37.7% [31.1%, 43.1%] |
| ES / magic_01 | 2021 | 239 observed dates | nominal|midpoint_before_invalidation_lower | 58.6% [52.7%, 65.3%] |
| ES / magic_01 | 2021 | 239 observed dates | nominal|midpoint_before_invalidation_upper | 59.0% [53.1%, 65.6%] |
| ES / magic_01 | 2021 | 239 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| ES / magic_01 | 2021 | 239 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| ES / magic_01 | 2022 | 245 / 251 | availability_delayed | break_then_neither_by_horizon: 7; invalidation_before_midpoint: 88; midpoint_before_invalidation: 150 |
| ES / magic_01 | 2022 | 245 / 251 | nominal | break_then_neither_by_horizon: 6; invalidation_before_midpoint: 86; midpoint_before_invalidation: 153 |
| ES / magic_01 | 2022 | 245 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.9% [0.8%, 4.5%] |
| ES / magic_01 | 2022 | 245 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.9% [0.8%, 4.5%] |
| ES / magic_01 | 2022 | 245 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.9% [29.8%, 41.8%] |
| ES / magic_01 | 2022 | 245 observed dates | availability_delayed|invalidation_before_midpoint_upper | 35.9% [29.8%, 41.8%] |
| ES / magic_01 | 2022 | 245 observed dates | availability_delayed|midpoint_before_invalidation_lower | 61.2% [55.9%, 67.9%] |
| ES / magic_01 | 2022 | 245 observed dates | availability_delayed|midpoint_before_invalidation_upper | 61.2% [55.9%, 67.9%] |
| ES / magic_01 | 2022 | 245 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2022 | 245 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2022 | 245 observed dates | nominal|break_then_neither_by_horizon_lower | 2.4% [0.8%, 4.1%] |
| ES / magic_01 | 2022 | 245 observed dates | nominal|break_then_neither_by_horizon_upper | 2.4% [0.8%, 4.1%] |
| ES / magic_01 | 2022 | 245 observed dates | nominal|invalidation_before_midpoint_lower | 35.1% [29.0%, 41.0%] |
| ES / magic_01 | 2022 | 245 observed dates | nominal|invalidation_before_midpoint_upper | 35.1% [29.0%, 41.0%] |
| ES / magic_01 | 2022 | 245 observed dates | nominal|midpoint_before_invalidation_lower | 62.4% [57.0%, 68.9%] |
| ES / magic_01 | 2022 | 245 observed dates | nominal|midpoint_before_invalidation_upper | 62.4% [57.0%, 68.9%] |
| ES / magic_01 | 2022 | 245 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2022 | 245 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2023 | 234 / 250 | availability_delayed | break_then_neither_by_horizon: 4; competing_order_ambiguous: 1; future_censored: 1; invalidation_before_midpoint: 90; midpoint_before_invalidation: 138 |
| ES / magic_01 | 2023 | 234 / 250 | nominal | break_then_neither_by_horizon: 4; competing_order_ambiguous: 3; future_censored: 1; invalidation_before_midpoint: 84; midpoint_before_invalidation: 142 |
| ES / magic_01 | 2023 | 233 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 1.7% [0.0%, 4.2%] |
| ES / magic_01 | 2023 | 233 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 1.7% [0.0%, 4.2%] |
| ES / magic_01 | 2023 | 233 observed dates | availability_delayed|invalidation_before_midpoint_lower | 38.6% [33.0%, 45.0%] |
| ES / magic_01 | 2023 | 233 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.1% [33.6%, 45.3%] |
| ES / magic_01 | 2023 | 233 observed dates | availability_delayed|midpoint_before_invalidation_lower | 59.2% [52.4%, 65.4%] |
| ES / magic_01 | 2023 | 233 observed dates | availability_delayed|midpoint_before_invalidation_upper | 59.7% [52.9%, 65.5%] |
| ES / magic_01 | 2023 | 233 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2023 | 233 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2023 | 233 observed dates | nominal|break_then_neither_by_horizon_lower | 1.7% [0.0%, 4.2%] |
| ES / magic_01 | 2023 | 233 observed dates | nominal|break_then_neither_by_horizon_upper | 1.7% [0.0%, 4.2%] |
| ES / magic_01 | 2023 | 233 observed dates | nominal|invalidation_before_midpoint_lower | 36.1% [30.4%, 42.6%] |
| ES / magic_01 | 2023 | 233 observed dates | nominal|invalidation_before_midpoint_upper | 37.3% [31.9%, 43.9%] |
| ES / magic_01 | 2023 | 233 observed dates | nominal|midpoint_before_invalidation_lower | 60.9% [53.7%, 67.1%] |
| ES / magic_01 | 2023 | 233 observed dates | nominal|midpoint_before_invalidation_upper | 62.2% [55.0%, 68.3%] |
| ES / magic_01 | 2023 | 233 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2023 | 233 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2024 | 226 / 252 | availability_delayed | break_then_neither_by_horizon: 9; invalidation_before_midpoint: 81; midpoint_before_invalidation: 136 |
| ES / magic_01 | 2024 | 226 / 252 | nominal | break_then_neither_by_horizon: 9; invalidation_before_midpoint: 79; midpoint_before_invalidation: 138 |
| ES / magic_01 | 2024 | 226 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 4.0% [1.8%, 6.6%] |
| ES / magic_01 | 2024 | 226 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 4.0% [1.8%, 6.6%] |
| ES / magic_01 | 2024 | 226 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.8% [29.7%, 42.1%] |
| ES / magic_01 | 2024 | 226 observed dates | availability_delayed|invalidation_before_midpoint_upper | 35.8% [29.7%, 42.1%] |
| ES / magic_01 | 2024 | 226 observed dates | availability_delayed|midpoint_before_invalidation_lower | 60.2% [53.2%, 66.7%] |
| ES / magic_01 | 2024 | 226 observed dates | availability_delayed|midpoint_before_invalidation_upper | 60.2% [53.2%, 66.7%] |
| ES / magic_01 | 2024 | 226 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2024 | 226 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2024 | 226 observed dates | nominal|break_then_neither_by_horizon_lower | 4.0% [1.8%, 6.6%] |
| ES / magic_01 | 2024 | 226 observed dates | nominal|break_then_neither_by_horizon_upper | 4.0% [1.8%, 6.6%] |
| ES / magic_01 | 2024 | 226 observed dates | nominal|invalidation_before_midpoint_lower | 35.0% [28.9%, 41.2%] |
| ES / magic_01 | 2024 | 226 observed dates | nominal|invalidation_before_midpoint_upper | 35.0% [28.9%, 41.2%] |
| ES / magic_01 | 2024 | 226 observed dates | nominal|midpoint_before_invalidation_lower | 61.1% [53.8%, 67.7%] |
| ES / magic_01 | 2024 | 226 observed dates | nominal|midpoint_before_invalidation_upper | 61.1% [53.8%, 67.7%] |
| ES / magic_01 | 2024 | 226 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_01 | 2024 | 226 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_02 | 2020 | 243 / 253 | availability_delayed | break_then_neither_by_horizon: 17; competing_order_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 99; midpoint_before_invalidation: 118; no_break_by_horizon: 6 |
| ES / magic_02 | 2020 | 243 / 253 | nominal | break_then_neither_by_horizon: 17; competing_order_ambiguous: 2; future_censored: 2; invalidation_before_midpoint: 97; midpoint_before_invalidation: 119; no_break_by_horizon: 6 |
| ES / magic_02 | 2020 | 241 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 7.1% [4.3%, 10.2%] |
| ES / magic_02 | 2020 | 241 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 7.1% [4.3%, 10.2%] |
| ES / magic_02 | 2020 | 241 observed dates | availability_delayed|invalidation_before_midpoint_lower | 41.1% [34.4%, 47.1%] |
| ES / magic_02 | 2020 | 241 observed dates | availability_delayed|invalidation_before_midpoint_upper | 41.5% [34.8%, 47.9%] |
| ES / magic_02 | 2020 | 241 observed dates | availability_delayed|midpoint_before_invalidation_lower | 49.0% [42.7%, 55.6%] |
| ES / magic_02 | 2020 | 241 observed dates | availability_delayed|midpoint_before_invalidation_upper | 49.4% [43.2%, 56.0%] |
| ES / magic_02 | 2020 | 241 observed dates | availability_delayed|no_break_by_horizon_lower | 2.5% [0.4%, 4.9%] |
| ES / magic_02 | 2020 | 241 observed dates | availability_delayed|no_break_by_horizon_upper | 2.5% [0.4%, 4.9%] |
| ES / magic_02 | 2020 | 241 observed dates | nominal|break_then_neither_by_horizon_lower | 7.1% [4.3%, 10.2%] |
| ES / magic_02 | 2020 | 241 observed dates | nominal|break_then_neither_by_horizon_upper | 7.1% [4.3%, 10.2%] |
| ES / magic_02 | 2020 | 241 observed dates | nominal|invalidation_before_midpoint_lower | 40.2% [33.5%, 46.3%] |
| ES / magic_02 | 2020 | 241 observed dates | nominal|invalidation_before_midpoint_upper | 41.1% [34.3%, 47.5%] |
| ES / magic_02 | 2020 | 241 observed dates | nominal|midpoint_before_invalidation_lower | 49.4% [43.2%, 56.2%] |
| ES / magic_02 | 2020 | 241 observed dates | nominal|midpoint_before_invalidation_upper | 50.2% [44.1%, 56.9%] |
| ES / magic_02 | 2020 | 241 observed dates | nominal|no_break_by_horizon_lower | 2.5% [0.4%, 4.9%] |
| ES / magic_02 | 2020 | 241 observed dates | nominal|no_break_by_horizon_upper | 2.5% [0.4%, 4.9%] |
| ES / magic_02 | 2021 | 244 / 252 | availability_delayed | break_then_neither_by_horizon: 22; future_censored: 3; invalidation_before_midpoint: 99; midpoint_before_invalidation: 117; no_break_by_horizon: 3 |
| ES / magic_02 | 2021 | 244 / 252 | nominal | break_then_neither_by_horizon: 22; competing_order_ambiguous: 2; future_censored: 3; invalidation_before_midpoint: 94; midpoint_before_invalidation: 120; no_break_by_horizon: 3 |
| ES / magic_02 | 2021 | 241 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 9.1% [5.5%, 12.3%] |
| ES / magic_02 | 2021 | 241 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 9.1% [5.5%, 12.3%] |
| ES / magic_02 | 2021 | 241 observed dates | availability_delayed|invalidation_before_midpoint_lower | 41.1% [34.7%, 47.1%] |
| ES / magic_02 | 2021 | 241 observed dates | availability_delayed|invalidation_before_midpoint_upper | 41.1% [34.7%, 47.1%] |
| ES / magic_02 | 2021 | 241 observed dates | availability_delayed|midpoint_before_invalidation_lower | 48.5% [42.9%, 54.9%] |
| ES / magic_02 | 2021 | 241 observed dates | availability_delayed|midpoint_before_invalidation_upper | 48.5% [42.9%, 54.9%] |
| ES / magic_02 | 2021 | 241 observed dates | availability_delayed|no_break_by_horizon_lower | 1.2% [0.0%, 2.9%] |
| ES / magic_02 | 2021 | 241 observed dates | availability_delayed|no_break_by_horizon_upper | 1.2% [0.0%, 2.9%] |
| ES / magic_02 | 2021 | 241 observed dates | nominal|break_then_neither_by_horizon_lower | 9.1% [5.5%, 12.3%] |
| ES / magic_02 | 2021 | 241 observed dates | nominal|break_then_neither_by_horizon_upper | 9.1% [5.5%, 12.3%] |
| ES / magic_02 | 2021 | 241 observed dates | nominal|invalidation_before_midpoint_lower | 39.0% [32.8%, 44.8%] |
| ES / magic_02 | 2021 | 241 observed dates | nominal|invalidation_before_midpoint_upper | 39.8% [33.5%, 45.5%] |
| ES / magic_02 | 2021 | 241 observed dates | nominal|midpoint_before_invalidation_lower | 49.8% [44.2%, 56.0%] |
| ES / magic_02 | 2021 | 241 observed dates | nominal|midpoint_before_invalidation_upper | 50.6% [45.0%, 57.0%] |
| ES / magic_02 | 2021 | 241 observed dates | nominal|no_break_by_horizon_lower | 1.2% [0.0%, 2.9%] |
| ES / magic_02 | 2021 | 241 observed dates | nominal|no_break_by_horizon_upper | 1.2% [0.0%, 2.9%] |
| ES / magic_02 | 2022 | 248 / 251 | availability_delayed | break_then_neither_by_horizon: 9; competing_order_ambiguous: 2; future_censored: 1; invalidation_before_midpoint: 90; midpoint_before_invalidation: 143; no_break_by_horizon: 3 |
| ES / magic_02 | 2022 | 248 / 251 | nominal | break_then_neither_by_horizon: 7; competing_order_ambiguous: 6; future_censored: 1; invalidation_before_midpoint: 83; midpoint_before_invalidation: 148; no_break_by_horizon: 3 |
| ES / magic_02 | 2022 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.6% [1.6%, 6.0%] |
| ES / magic_02 | 2022 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.6% [1.6%, 6.0%] |
| ES / magic_02 | 2022 | 247 observed dates | availability_delayed|invalidation_before_midpoint_lower | 36.4% [30.5%, 43.7%] |
| ES / magic_02 | 2022 | 247 observed dates | availability_delayed|invalidation_before_midpoint_upper | 37.2% [31.1%, 44.5%] |
| ES / magic_02 | 2022 | 247 observed dates | availability_delayed|midpoint_before_invalidation_lower | 57.9% [50.8%, 63.6%] |
| ES / magic_02 | 2022 | 247 observed dates | availability_delayed|midpoint_before_invalidation_upper | 58.7% [51.4%, 64.1%] |
| ES / magic_02 | 2022 | 247 observed dates | availability_delayed|no_break_by_horizon_lower | 1.2% [0.0%, 2.8%] |
| ES / magic_02 | 2022 | 247 observed dates | availability_delayed|no_break_by_horizon_upper | 1.2% [0.0%, 2.8%] |
| ES / magic_02 | 2022 | 247 observed dates | nominal|break_then_neither_by_horizon_lower | 2.8% [1.2%, 4.9%] |
| ES / magic_02 | 2022 | 247 observed dates | nominal|break_then_neither_by_horizon_upper | 2.8% [1.2%, 4.9%] |
| ES / magic_02 | 2022 | 247 observed dates | nominal|invalidation_before_midpoint_lower | 33.6% [27.7%, 41.1%] |
| ES / magic_02 | 2022 | 247 observed dates | nominal|invalidation_before_midpoint_upper | 36.0% [29.9%, 43.5%] |
| ES / magic_02 | 2022 | 247 observed dates | nominal|midpoint_before_invalidation_lower | 59.9% [52.6%, 65.6%] |
| ES / magic_02 | 2022 | 247 observed dates | nominal|midpoint_before_invalidation_upper | 62.3% [55.1%, 68.0%] |
| ES / magic_02 | 2022 | 247 observed dates | nominal|no_break_by_horizon_lower | 1.2% [0.0%, 2.8%] |
| ES / magic_02 | 2022 | 247 observed dates | nominal|no_break_by_horizon_upper | 1.2% [0.0%, 2.8%] |
| ES / magic_02 | 2023 | 243 / 250 | availability_delayed | break_then_neither_by_horizon: 8; competing_order_ambiguous: 2; future_censored: 1; invalidation_before_midpoint: 97; midpoint_before_invalidation: 133; no_break_by_horizon: 2 |
| ES / magic_02 | 2023 | 243 / 250 | nominal | break_then_neither_by_horizon: 7; competing_order_ambiguous: 5; future_censored: 1; invalidation_before_midpoint: 91; midpoint_before_invalidation: 137; no_break_by_horizon: 2 |
| ES / magic_02 | 2023 | 242 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.3% [1.2%, 5.7%] |
| ES / magic_02 | 2023 | 242 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.3% [1.2%, 5.7%] |
| ES / magic_02 | 2023 | 242 observed dates | availability_delayed|invalidation_before_midpoint_lower | 40.1% [34.3%, 46.5%] |
| ES / magic_02 | 2023 | 242 observed dates | availability_delayed|invalidation_before_midpoint_upper | 40.9% [34.6%, 47.0%] |
| ES / magic_02 | 2023 | 242 observed dates | availability_delayed|midpoint_before_invalidation_lower | 55.0% [49.2%, 61.2%] |
| ES / magic_02 | 2023 | 242 observed dates | availability_delayed|midpoint_before_invalidation_upper | 55.8% [50.0%, 61.7%] |
| ES / magic_02 | 2023 | 242 observed dates | availability_delayed|no_break_by_horizon_lower | 0.8% [0.0%, 2.1%] |
| ES / magic_02 | 2023 | 242 observed dates | availability_delayed|no_break_by_horizon_upper | 0.8% [0.0%, 2.1%] |
| ES / magic_02 | 2023 | 242 observed dates | nominal|break_then_neither_by_horizon_lower | 2.9% [1.2%, 5.0%] |
| ES / magic_02 | 2023 | 242 observed dates | nominal|break_then_neither_by_horizon_upper | 2.9% [1.2%, 5.0%] |
| ES / magic_02 | 2023 | 242 observed dates | nominal|invalidation_before_midpoint_lower | 37.6% [31.5%, 43.8%] |
| ES / magic_02 | 2023 | 242 observed dates | nominal|invalidation_before_midpoint_upper | 39.7% [33.5%, 45.5%] |
| ES / magic_02 | 2023 | 242 observed dates | nominal|midpoint_before_invalidation_lower | 56.6% [51.0%, 63.1%] |
| ES / magic_02 | 2023 | 242 observed dates | nominal|midpoint_before_invalidation_upper | 58.7% [52.9%, 64.7%] |
| ES / magic_02 | 2023 | 242 observed dates | nominal|no_break_by_horizon_lower | 0.8% [0.0%, 2.1%] |
| ES / magic_02 | 2023 | 242 observed dates | nominal|no_break_by_horizon_upper | 0.8% [0.0%, 2.1%] |
| ES / magic_02 | 2024 | 244 / 252 | availability_delayed | break_then_neither_by_horizon: 8; competing_order_ambiguous: 2; future_censored: 1; invalidation_before_midpoint: 95; midpoint_before_invalidation: 138 |
| ES / magic_02 | 2024 | 244 / 252 | nominal | break_then_neither_by_horizon: 8; competing_order_ambiguous: 2; future_censored: 1; invalidation_before_midpoint: 92; midpoint_before_invalidation: 141 |
| ES / magic_02 | 2024 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.3% [1.2%, 6.1%] |
| ES / magic_02 | 2024 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.3% [1.2%, 6.1%] |
| ES / magic_02 | 2024 | 243 observed dates | availability_delayed|invalidation_before_midpoint_lower | 39.1% [33.7%, 45.1%] |
| ES / magic_02 | 2024 | 243 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.9% [34.3%, 45.5%] |
| ES / magic_02 | 2024 | 243 observed dates | availability_delayed|midpoint_before_invalidation_lower | 56.8% [51.0%, 62.3%] |
| ES / magic_02 | 2024 | 243 observed dates | availability_delayed|midpoint_before_invalidation_upper | 57.6% [51.4%, 62.7%] |
| ES / magic_02 | 2024 | 243 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_02 | 2024 | 243 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_02 | 2024 | 243 observed dates | nominal|break_then_neither_by_horizon_lower | 3.3% [1.2%, 6.1%] |
| ES / magic_02 | 2024 | 243 observed dates | nominal|break_then_neither_by_horizon_upper | 3.3% [1.2%, 6.1%] |
| ES / magic_02 | 2024 | 243 observed dates | nominal|invalidation_before_midpoint_lower | 37.9% [32.5%, 43.9%] |
| ES / magic_02 | 2024 | 243 observed dates | nominal|invalidation_before_midpoint_upper | 38.7% [33.2%, 44.2%] |
| ES / magic_02 | 2024 | 243 observed dates | nominal|midpoint_before_invalidation_lower | 58.0% [52.2%, 63.5%] |
| ES / magic_02 | 2024 | 243 observed dates | nominal|midpoint_before_invalidation_upper | 58.8% [52.9%, 64.2%] |
| ES / magic_02 | 2024 | 243 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_02 | 2024 | 243 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2020 | 244 / 253 | availability_delayed | break_then_neither_by_horizon: 17; competing_order_ambiguous: 3; future_censored: 3; invalidation_before_midpoint: 73; midpoint_before_invalidation: 148 |
| ES / magic_06 | 2020 | 244 / 253 | nominal | break_then_neither_by_horizon: 17; competing_order_ambiguous: 2; future_censored: 3; invalidation_before_midpoint: 72; midpoint_before_invalidation: 150 |
| ES / magic_06 | 2020 | 241 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 7.1% [4.1%, 10.1%] |
| ES / magic_06 | 2020 | 241 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 7.1% [4.1%, 10.1%] |
| ES / magic_06 | 2020 | 241 observed dates | availability_delayed|invalidation_before_midpoint_lower | 30.3% [24.9%, 35.2%] |
| ES / magic_06 | 2020 | 241 observed dates | availability_delayed|invalidation_before_midpoint_upper | 31.5% [26.6%, 36.4%] |
| ES / magic_06 | 2020 | 241 observed dates | availability_delayed|midpoint_before_invalidation_lower | 61.4% [56.4%, 66.9%] |
| ES / magic_06 | 2020 | 241 observed dates | availability_delayed|midpoint_before_invalidation_upper | 62.7% [57.5%, 68.3%] |
| ES / magic_06 | 2020 | 241 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2020 | 241 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2020 | 241 observed dates | nominal|break_then_neither_by_horizon_lower | 7.1% [4.1%, 10.1%] |
| ES / magic_06 | 2020 | 241 observed dates | nominal|break_then_neither_by_horizon_upper | 7.1% [4.1%, 10.1%] |
| ES / magic_06 | 2020 | 241 observed dates | nominal|invalidation_before_midpoint_lower | 29.9% [24.7%, 34.8%] |
| ES / magic_06 | 2020 | 241 observed dates | nominal|invalidation_before_midpoint_upper | 30.7% [25.3%, 35.7%] |
| ES / magic_06 | 2020 | 241 observed dates | nominal|midpoint_before_invalidation_lower | 62.2% [57.2%, 67.8%] |
| ES / magic_06 | 2020 | 241 observed dates | nominal|midpoint_before_invalidation_upper | 63.1% [57.9%, 68.9%] |
| ES / magic_06 | 2020 | 241 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2020 | 241 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2021 | 247 / 252 | availability_delayed | break_then_neither_by_horizon: 9; competing_order_ambiguous: 2; invalidation_before_midpoint: 77; midpoint_before_invalidation: 158; no_break_by_horizon: 1 |
| ES / magic_06 | 2021 | 247 / 252 | nominal | break_then_neither_by_horizon: 9; competing_order_ambiguous: 2; invalidation_before_midpoint: 77; midpoint_before_invalidation: 158; no_break_by_horizon: 1 |
| ES / magic_06 | 2021 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.6% [1.6%, 6.1%] |
| ES / magic_06 | 2021 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.6% [1.6%, 6.1%] |
| ES / magic_06 | 2021 | 247 observed dates | availability_delayed|invalidation_before_midpoint_lower | 31.2% [25.3%, 37.1%] |
| ES / magic_06 | 2021 | 247 observed dates | availability_delayed|invalidation_before_midpoint_upper | 32.0% [25.9%, 37.9%] |
| ES / magic_06 | 2021 | 247 observed dates | availability_delayed|midpoint_before_invalidation_lower | 64.0% [58.2%, 70.5%] |
| ES / magic_06 | 2021 | 247 observed dates | availability_delayed|midpoint_before_invalidation_upper | 64.8% [59.0%, 71.2%] |
| ES / magic_06 | 2021 | 247 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.6%] |
| ES / magic_06 | 2021 | 247 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.6%] |
| ES / magic_06 | 2021 | 247 observed dates | nominal|break_then_neither_by_horizon_lower | 3.6% [1.6%, 6.1%] |
| ES / magic_06 | 2021 | 247 observed dates | nominal|break_then_neither_by_horizon_upper | 3.6% [1.6%, 6.1%] |
| ES / magic_06 | 2021 | 247 observed dates | nominal|invalidation_before_midpoint_lower | 31.2% [25.3%, 37.1%] |
| ES / magic_06 | 2021 | 247 observed dates | nominal|invalidation_before_midpoint_upper | 32.0% [25.9%, 37.9%] |
| ES / magic_06 | 2021 | 247 observed dates | nominal|midpoint_before_invalidation_lower | 64.0% [58.2%, 70.5%] |
| ES / magic_06 | 2021 | 247 observed dates | nominal|midpoint_before_invalidation_upper | 64.8% [59.0%, 71.2%] |
| ES / magic_06 | 2021 | 247 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.6%] |
| ES / magic_06 | 2021 | 247 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.6%] |
| ES / magic_06 | 2022 | 249 / 251 | availability_delayed | break_then_neither_by_horizon: 3; competing_order_ambiguous: 4; first_side_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 94; midpoint_before_invalidation: 145 |
| ES / magic_06 | 2022 | 249 / 251 | nominal | break_then_neither_by_horizon: 3; competing_order_ambiguous: 4; first_side_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 93; midpoint_before_invalidation: 146 |
| ES / magic_06 | 2022 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 1.2% [0.0%, 2.8%] |
| ES / magic_06 | 2022 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 1.2% [0.0%, 2.8%] |
| ES / magic_06 | 2022 | 247 observed dates | availability_delayed|invalidation_before_midpoint_lower | 38.1% [32.4%, 43.4%] |
| ES / magic_06 | 2022 | 247 observed dates | availability_delayed|invalidation_before_midpoint_upper | 40.1% [34.3%, 45.3%] |
| ES / magic_06 | 2022 | 247 observed dates | availability_delayed|midpoint_before_invalidation_lower | 58.7% [53.3%, 64.5%] |
| ES / magic_06 | 2022 | 247 observed dates | availability_delayed|midpoint_before_invalidation_upper | 60.7% [55.1%, 66.5%] |
| ES / magic_06 | 2022 | 247 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2022 | 247 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2022 | 247 observed dates | nominal|break_then_neither_by_horizon_lower | 1.2% [0.0%, 2.8%] |
| ES / magic_06 | 2022 | 247 observed dates | nominal|break_then_neither_by_horizon_upper | 1.2% [0.0%, 2.8%] |
| ES / magic_06 | 2022 | 247 observed dates | nominal|invalidation_before_midpoint_lower | 37.7% [31.6%, 43.1%] |
| ES / magic_06 | 2022 | 247 observed dates | nominal|invalidation_before_midpoint_upper | 39.7% [33.9%, 44.6%] |
| ES / magic_06 | 2022 | 247 observed dates | nominal|midpoint_before_invalidation_lower | 59.1% [53.5%, 65.0%] |
| ES / magic_06 | 2022 | 247 observed dates | nominal|midpoint_before_invalidation_upper | 61.1% [55.4%, 67.1%] |
| ES / magic_06 | 2022 | 247 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2022 | 247 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2023 | 243 / 250 | availability_delayed | break_then_neither_by_horizon: 2; competing_order_ambiguous: 3; first_side_ambiguous: 1; invalidation_before_midpoint: 81; midpoint_before_invalidation: 156 |
| ES / magic_06 | 2023 | 243 / 250 | nominal | break_then_neither_by_horizon: 2; competing_order_ambiguous: 3; first_side_ambiguous: 1; invalidation_before_midpoint: 81; midpoint_before_invalidation: 156 |
| ES / magic_06 | 2023 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 0.8% [0.0%, 2.1%] |
| ES / magic_06 | 2023 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 0.8% [0.0%, 2.1%] |
| ES / magic_06 | 2023 | 243 observed dates | availability_delayed|invalidation_before_midpoint_lower | 33.3% [27.4%, 39.8%] |
| ES / magic_06 | 2023 | 243 observed dates | availability_delayed|invalidation_before_midpoint_upper | 34.6% [28.9%, 40.8%] |
| ES / magic_06 | 2023 | 243 observed dates | availability_delayed|midpoint_before_invalidation_lower | 64.6% [58.3%, 70.4%] |
| ES / magic_06 | 2023 | 243 observed dates | availability_delayed|midpoint_before_invalidation_upper | 65.8% [59.4%, 71.9%] |
| ES / magic_06 | 2023 | 243 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2023 | 243 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2023 | 243 observed dates | nominal|break_then_neither_by_horizon_lower | 0.8% [0.0%, 2.1%] |
| ES / magic_06 | 2023 | 243 observed dates | nominal|break_then_neither_by_horizon_upper | 0.8% [0.0%, 2.1%] |
| ES / magic_06 | 2023 | 243 observed dates | nominal|invalidation_before_midpoint_lower | 33.3% [27.4%, 39.8%] |
| ES / magic_06 | 2023 | 243 observed dates | nominal|invalidation_before_midpoint_upper | 34.6% [28.9%, 40.8%] |
| ES / magic_06 | 2023 | 243 observed dates | nominal|midpoint_before_invalidation_lower | 64.6% [58.3%, 70.4%] |
| ES / magic_06 | 2023 | 243 observed dates | nominal|midpoint_before_invalidation_upper | 65.8% [59.4%, 71.9%] |
| ES / magic_06 | 2023 | 243 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2023 | 243 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2024 | 247 / 252 | availability_delayed | break_then_neither_by_horizon: 8; competing_order_ambiguous: 4; first_side_ambiguous: 1; future_censored: 1; invalidation_before_midpoint: 84; midpoint_before_invalidation: 149 |
| ES / magic_06 | 2024 | 247 / 252 | nominal | break_then_neither_by_horizon: 8; competing_order_ambiguous: 4; first_side_ambiguous: 1; future_censored: 1; invalidation_before_midpoint: 81; midpoint_before_invalidation: 152 |
| ES / magic_06 | 2024 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.3% [1.2%, 4.9%] |
| ES / magic_06 | 2024 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.3% [1.2%, 4.9%] |
| ES / magic_06 | 2024 | 246 observed dates | availability_delayed|invalidation_before_midpoint_lower | 34.1% [28.1%, 40.2%] |
| ES / magic_06 | 2024 | 246 observed dates | availability_delayed|invalidation_before_midpoint_upper | 36.2% [30.4%, 42.0%] |
| ES / magic_06 | 2024 | 246 observed dates | availability_delayed|midpoint_before_invalidation_lower | 60.6% [55.0%, 66.4%] |
| ES / magic_06 | 2024 | 246 observed dates | availability_delayed|midpoint_before_invalidation_upper | 62.6% [56.9%, 68.6%] |
| ES / magic_06 | 2024 | 246 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2024 | 246 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2024 | 246 observed dates | nominal|break_then_neither_by_horizon_lower | 3.3% [1.2%, 4.9%] |
| ES / magic_06 | 2024 | 246 observed dates | nominal|break_then_neither_by_horizon_upper | 3.3% [1.2%, 4.9%] |
| ES / magic_06 | 2024 | 246 observed dates | nominal|invalidation_before_midpoint_lower | 32.9% [27.0%, 38.7%] |
| ES / magic_06 | 2024 | 246 observed dates | nominal|invalidation_before_midpoint_upper | 35.0% [29.1%, 40.7%] |
| ES / magic_06 | 2024 | 246 observed dates | nominal|midpoint_before_invalidation_lower | 61.8% [56.4%, 67.8%] |
| ES / magic_06 | 2024 | 246 observed dates | nominal|midpoint_before_invalidation_upper | 63.8% [58.4%, 69.9%] |
| ES / magic_06 | 2024 | 246 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_06 | 2024 | 246 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2020 | 246 / 253 | availability_delayed | break_then_neither_by_horizon: 1; competing_order_ambiguous: 2; future_censored: 4; invalidation_before_midpoint: 85; midpoint_before_invalidation: 154 |
| ES / magic_07 | 2020 | 246 / 253 | nominal | break_then_neither_by_horizon: 1; competing_order_ambiguous: 2; future_censored: 4; invalidation_before_midpoint: 85; midpoint_before_invalidation: 154 |
| ES / magic_07 | 2020 | 242 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| ES / magic_07 | 2020 | 242 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| ES / magic_07 | 2020 | 242 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.1% [29.5%, 41.2%] |
| ES / magic_07 | 2020 | 242 observed dates | availability_delayed|invalidation_before_midpoint_upper | 36.0% [30.5%, 42.2%] |
| ES / magic_07 | 2020 | 242 observed dates | availability_delayed|midpoint_before_invalidation_lower | 63.6% [57.4%, 69.1%] |
| ES / magic_07 | 2020 | 242 observed dates | availability_delayed|midpoint_before_invalidation_upper | 64.5% [58.3%, 70.0%] |
| ES / magic_07 | 2020 | 242 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2020 | 242 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2020 | 242 observed dates | nominal|break_then_neither_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| ES / magic_07 | 2020 | 242 observed dates | nominal|break_then_neither_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| ES / magic_07 | 2020 | 242 observed dates | nominal|invalidation_before_midpoint_lower | 35.1% [29.5%, 41.2%] |
| ES / magic_07 | 2020 | 242 observed dates | nominal|invalidation_before_midpoint_upper | 36.0% [30.5%, 42.2%] |
| ES / magic_07 | 2020 | 242 observed dates | nominal|midpoint_before_invalidation_lower | 63.6% [57.4%, 69.1%] |
| ES / magic_07 | 2020 | 242 observed dates | nominal|midpoint_before_invalidation_upper | 64.5% [58.3%, 70.0%] |
| ES / magic_07 | 2020 | 242 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2020 | 242 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2021 | 248 / 252 | availability_delayed | break_then_neither_by_horizon: 7; competing_order_ambiguous: 4; invalidation_before_midpoint: 95; midpoint_before_invalidation: 142 |
| ES / magic_07 | 2021 | 248 / 252 | nominal | break_then_neither_by_horizon: 7; competing_order_ambiguous: 6; invalidation_before_midpoint: 93; midpoint_before_invalidation: 142 |
| ES / magic_07 | 2021 | 248 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.8% [1.2%, 4.8%] |
| ES / magic_07 | 2021 | 248 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.8% [1.2%, 4.8%] |
| ES / magic_07 | 2021 | 248 observed dates | availability_delayed|invalidation_before_midpoint_lower | 38.3% [32.8%, 44.0%] |
| ES / magic_07 | 2021 | 248 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.9% [34.4%, 46.0%] |
| ES / magic_07 | 2021 | 248 observed dates | availability_delayed|midpoint_before_invalidation_lower | 57.3% [51.2%, 62.6%] |
| ES / magic_07 | 2021 | 248 observed dates | availability_delayed|midpoint_before_invalidation_upper | 58.9% [53.0%, 64.0%] |
| ES / magic_07 | 2021 | 248 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2021 | 248 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2021 | 248 observed dates | nominal|break_then_neither_by_horizon_lower | 2.8% [1.2%, 4.8%] |
| ES / magic_07 | 2021 | 248 observed dates | nominal|break_then_neither_by_horizon_upper | 2.8% [1.2%, 4.8%] |
| ES / magic_07 | 2021 | 248 observed dates | nominal|invalidation_before_midpoint_lower | 37.5% [31.9%, 43.4%] |
| ES / magic_07 | 2021 | 248 observed dates | nominal|invalidation_before_midpoint_upper | 39.9% [34.4%, 46.0%] |
| ES / magic_07 | 2021 | 248 observed dates | nominal|midpoint_before_invalidation_lower | 57.3% [51.2%, 62.6%] |
| ES / magic_07 | 2021 | 248 observed dates | nominal|midpoint_before_invalidation_upper | 59.7% [53.6%, 65.0%] |
| ES / magic_07 | 2021 | 248 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2021 | 248 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2022 | 249 / 251 | availability_delayed | break_then_neither_by_horizon: 3; competing_order_ambiguous: 5; first_side_ambiguous: 2; future_censored: 2; invalidation_before_midpoint: 93; midpoint_before_invalidation: 143; no_break_by_horizon: 1 |
| ES / magic_07 | 2022 | 249 / 251 | nominal | break_then_neither_by_horizon: 3; competing_order_ambiguous: 5; first_side_ambiguous: 2; future_censored: 2; invalidation_before_midpoint: 91; midpoint_before_invalidation: 145; no_break_by_horizon: 1 |
| ES / magic_07 | 2022 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 1.2% [0.0%, 2.8%] |
| ES / magic_07 | 2022 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 1.2% [0.0%, 2.8%] |
| ES / magic_07 | 2022 | 247 observed dates | availability_delayed|invalidation_before_midpoint_lower | 37.7% [31.1%, 44.3%] |
| ES / magic_07 | 2022 | 247 observed dates | availability_delayed|invalidation_before_midpoint_upper | 40.1% [33.5%, 47.0%] |
| ES / magic_07 | 2022 | 247 observed dates | availability_delayed|midpoint_before_invalidation_lower | 58.3% [51.4%, 64.8%] |
| ES / magic_07 | 2022 | 247 observed dates | availability_delayed|midpoint_before_invalidation_upper | 60.7% [54.3%, 67.4%] |
| ES / magic_07 | 2022 | 247 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| ES / magic_07 | 2022 | 247 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| ES / magic_07 | 2022 | 247 observed dates | nominal|break_then_neither_by_horizon_lower | 1.2% [0.0%, 2.8%] |
| ES / magic_07 | 2022 | 247 observed dates | nominal|break_then_neither_by_horizon_upper | 1.2% [0.0%, 2.8%] |
| ES / magic_07 | 2022 | 247 observed dates | nominal|invalidation_before_midpoint_lower | 36.8% [30.7%, 43.5%] |
| ES / magic_07 | 2022 | 247 observed dates | nominal|invalidation_before_midpoint_upper | 39.3% [32.8%, 46.3%] |
| ES / magic_07 | 2022 | 247 observed dates | nominal|midpoint_before_invalidation_lower | 59.1% [51.8%, 65.7%] |
| ES / magic_07 | 2022 | 247 observed dates | nominal|midpoint_before_invalidation_upper | 61.5% [54.8%, 68.1%] |
| ES / magic_07 | 2022 | 247 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| ES / magic_07 | 2022 | 247 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| ES / magic_07 | 2023 | 248 / 250 | availability_delayed | break_then_neither_by_horizon: 3; competing_order_ambiguous: 8; first_side_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 67; midpoint_before_invalidation: 166; no_break_by_horizon: 1 |
| ES / magic_07 | 2023 | 248 / 250 | nominal | break_then_neither_by_horizon: 3; competing_order_ambiguous: 8; first_side_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 66; midpoint_before_invalidation: 167; no_break_by_horizon: 1 |
| ES / magic_07 | 2023 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 1.2% [0.0%, 2.8%] |
| ES / magic_07 | 2023 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 1.2% [0.0%, 2.8%] |
| ES / magic_07 | 2023 | 246 observed dates | availability_delayed|invalidation_before_midpoint_lower | 27.2% [22.5%, 32.9%] |
| ES / magic_07 | 2023 | 246 observed dates | availability_delayed|invalidation_before_midpoint_upper | 30.5% [25.7%, 36.2%] |
| ES / magic_07 | 2023 | 246 observed dates | availability_delayed|midpoint_before_invalidation_lower | 67.9% [61.8%, 72.8%] |
| ES / magic_07 | 2023 | 246 observed dates | availability_delayed|midpoint_before_invalidation_upper | 71.1% [64.9%, 76.0%] |
| ES / magic_07 | 2023 | 246 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| ES / magic_07 | 2023 | 246 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| ES / magic_07 | 2023 | 246 observed dates | nominal|break_then_neither_by_horizon_lower | 1.2% [0.0%, 2.8%] |
| ES / magic_07 | 2023 | 246 observed dates | nominal|break_then_neither_by_horizon_upper | 1.2% [0.0%, 2.8%] |
| ES / magic_07 | 2023 | 246 observed dates | nominal|invalidation_before_midpoint_lower | 26.8% [22.1%, 32.5%] |
| ES / magic_07 | 2023 | 246 observed dates | nominal|invalidation_before_midpoint_upper | 30.1% [25.4%, 35.9%] |
| ES / magic_07 | 2023 | 246 observed dates | nominal|midpoint_before_invalidation_lower | 68.3% [62.1%, 73.3%] |
| ES / magic_07 | 2023 | 246 observed dates | nominal|midpoint_before_invalidation_upper | 71.5% [65.4%, 76.3%] |
| ES / magic_07 | 2023 | 246 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| ES / magic_07 | 2023 | 246 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| ES / magic_07 | 2024 | 249 / 252 | availability_delayed | break_then_neither_by_horizon: 3; competing_order_ambiguous: 10; first_side_ambiguous: 4; future_censored: 1; invalidation_before_midpoint: 78; midpoint_before_invalidation: 153 |
| ES / magic_07 | 2024 | 249 / 252 | nominal | break_then_neither_by_horizon: 3; competing_order_ambiguous: 10; first_side_ambiguous: 4; future_censored: 1; invalidation_before_midpoint: 77; midpoint_before_invalidation: 154 |
| ES / magic_07 | 2024 | 248 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 1.2% [0.0%, 2.0%] |
| ES / magic_07 | 2024 | 248 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 1.2% [0.0%, 2.0%] |
| ES / magic_07 | 2024 | 248 observed dates | availability_delayed|invalidation_before_midpoint_lower | 31.5% [26.6%, 36.8%] |
| ES / magic_07 | 2024 | 248 observed dates | availability_delayed|invalidation_before_midpoint_upper | 35.5% [30.4%, 41.1%] |
| ES / magic_07 | 2024 | 248 observed dates | availability_delayed|midpoint_before_invalidation_lower | 63.3% [57.8%, 68.7%] |
| ES / magic_07 | 2024 | 248 observed dates | availability_delayed|midpoint_before_invalidation_upper | 67.3% [61.7%, 72.5%] |
| ES / magic_07 | 2024 | 248 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2024 | 248 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2024 | 248 observed dates | nominal|break_then_neither_by_horizon_lower | 1.2% [0.0%, 2.0%] |
| ES / magic_07 | 2024 | 248 observed dates | nominal|break_then_neither_by_horizon_upper | 1.2% [0.0%, 2.0%] |
| ES / magic_07 | 2024 | 248 observed dates | nominal|invalidation_before_midpoint_lower | 31.0% [26.1%, 36.5%] |
| ES / magic_07 | 2024 | 248 observed dates | nominal|invalidation_before_midpoint_upper | 35.1% [30.1%, 40.7%] |
| ES / magic_07 | 2024 | 248 observed dates | nominal|midpoint_before_invalidation_lower | 63.7% [58.3%, 69.1%] |
| ES / magic_07 | 2024 | 248 observed dates | nominal|midpoint_before_invalidation_upper | 67.7% [62.3%, 72.8%] |
| ES / magic_07 | 2024 | 248 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_07 | 2024 | 248 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_08 | 2020 | 247 / 253 | availability_delayed | break_then_neither_by_horizon: 8; competing_order_ambiguous: 1; future_censored: 4; invalidation_before_midpoint: 89; midpoint_before_invalidation: 145 |
| ES / magic_08 | 2020 | 247 / 253 | nominal | break_then_neither_by_horizon: 7; competing_order_ambiguous: 1; future_censored: 4; invalidation_before_midpoint: 88; midpoint_before_invalidation: 147 |
| ES / magic_08 | 2020 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.3% [1.2%, 5.7%] |
| ES / magic_08 | 2020 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.3% [1.2%, 5.7%] |
| ES / magic_08 | 2020 | 243 observed dates | availability_delayed|invalidation_before_midpoint_lower | 36.6% [31.0%, 43.0%] |
| ES / magic_08 | 2020 | 243 observed dates | availability_delayed|invalidation_before_midpoint_upper | 37.0% [31.4%, 43.3%] |
| ES / magic_08 | 2020 | 243 observed dates | availability_delayed|midpoint_before_invalidation_lower | 59.7% [52.5%, 65.8%] |
| ES / magic_08 | 2020 | 243 observed dates | availability_delayed|midpoint_before_invalidation_upper | 60.1% [53.1%, 66.1%] |
| ES / magic_08 | 2020 | 243 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_08 | 2020 | 243 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_08 | 2020 | 243 observed dates | nominal|break_then_neither_by_horizon_lower | 2.9% [1.2%, 5.3%] |
| ES / magic_08 | 2020 | 243 observed dates | nominal|break_then_neither_by_horizon_upper | 2.9% [1.2%, 5.3%] |
| ES / magic_08 | 2020 | 243 observed dates | nominal|invalidation_before_midpoint_lower | 36.2% [30.5%, 42.6%] |
| ES / magic_08 | 2020 | 243 observed dates | nominal|invalidation_before_midpoint_upper | 36.6% [31.0%, 42.8%] |
| ES / magic_08 | 2020 | 243 observed dates | nominal|midpoint_before_invalidation_lower | 60.5% [53.5%, 66.7%] |
| ES / magic_08 | 2020 | 243 observed dates | nominal|midpoint_before_invalidation_upper | 60.9% [53.9%, 66.8%] |
| ES / magic_08 | 2020 | 243 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| ES / magic_08 | 2020 | 243 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| ES / magic_08 | 2021 | 251 / 252 | availability_delayed | break_then_neither_by_horizon: 9; competing_order_ambiguous: 4; first_side_ambiguous: 1; future_censored: 3; invalidation_before_midpoint: 104; midpoint_before_invalidation: 129; no_break_by_horizon: 1 |
| ES / magic_08 | 2021 | 251 / 252 | nominal | break_then_neither_by_horizon: 9; competing_order_ambiguous: 3; first_side_ambiguous: 1; future_censored: 3; invalidation_before_midpoint: 102; midpoint_before_invalidation: 132; no_break_by_horizon: 1 |
| ES / magic_08 | 2021 | 248 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.6% [1.6%, 6.0%] |
| ES / magic_08 | 2021 | 248 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.6% [1.6%, 6.0%] |
| ES / magic_08 | 2021 | 248 observed dates | availability_delayed|invalidation_before_midpoint_lower | 41.9% [35.5%, 47.2%] |
| ES / magic_08 | 2021 | 248 observed dates | availability_delayed|invalidation_before_midpoint_upper | 43.5% [37.2%, 49.0%] |
| ES / magic_08 | 2021 | 248 observed dates | availability_delayed|midpoint_before_invalidation_lower | 52.4% [46.7%, 59.0%] |
| ES / magic_08 | 2021 | 248 observed dates | availability_delayed|midpoint_before_invalidation_upper | 54.0% [48.4%, 60.7%] |
| ES / magic_08 | 2021 | 248 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| ES / magic_08 | 2021 | 248 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| ES / magic_08 | 2021 | 248 observed dates | nominal|break_then_neither_by_horizon_lower | 3.6% [1.6%, 6.0%] |
| ES / magic_08 | 2021 | 248 observed dates | nominal|break_then_neither_by_horizon_upper | 3.6% [1.6%, 6.0%] |
| ES / magic_08 | 2021 | 248 observed dates | nominal|invalidation_before_midpoint_lower | 41.1% [35.0%, 46.6%] |
| ES / magic_08 | 2021 | 248 observed dates | nominal|invalidation_before_midpoint_upper | 42.3% [36.0%, 48.2%] |
| ES / magic_08 | 2021 | 248 observed dates | nominal|midpoint_before_invalidation_lower | 53.6% [47.6%, 59.9%] |
| ES / magic_08 | 2021 | 248 observed dates | nominal|midpoint_before_invalidation_upper | 54.8% [49.0%, 61.1%] |
| ES / magic_08 | 2021 | 248 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| ES / magic_08 | 2021 | 248 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| ES / magic_08 | 2022 | 250 / 251 | availability_delayed | break_then_neither_by_horizon: 9; competing_order_ambiguous: 2; future_censored: 3; invalidation_before_midpoint: 90; midpoint_before_invalidation: 139; no_break_by_horizon: 7 |
| ES / magic_08 | 2022 | 250 / 251 | nominal | break_then_neither_by_horizon: 8; competing_order_ambiguous: 2; future_censored: 3; invalidation_before_midpoint: 89; midpoint_before_invalidation: 141; no_break_by_horizon: 7 |
| ES / magic_08 | 2022 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.6% [1.6%, 6.1%] |
| ES / magic_08 | 2022 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.6% [1.6%, 6.1%] |
| ES / magic_08 | 2022 | 247 observed dates | availability_delayed|invalidation_before_midpoint_lower | 36.4% [31.7%, 42.1%] |
| ES / magic_08 | 2022 | 247 observed dates | availability_delayed|invalidation_before_midpoint_upper | 37.2% [32.4%, 42.9%] |
| ES / magic_08 | 2022 | 247 observed dates | availability_delayed|midpoint_before_invalidation_lower | 56.3% [50.4%, 61.0%] |
| ES / magic_08 | 2022 | 247 observed dates | availability_delayed|midpoint_before_invalidation_upper | 57.1% [51.2%, 61.7%] |
| ES / magic_08 | 2022 | 247 observed dates | availability_delayed|no_break_by_horizon_lower | 2.8% [0.8%, 5.3%] |
| ES / magic_08 | 2022 | 247 observed dates | availability_delayed|no_break_by_horizon_upper | 2.8% [0.8%, 5.3%] |
| ES / magic_08 | 2022 | 247 observed dates | nominal|break_then_neither_by_horizon_lower | 3.2% [1.2%, 5.3%] |
| ES / magic_08 | 2022 | 247 observed dates | nominal|break_then_neither_by_horizon_upper | 3.2% [1.2%, 5.3%] |
| ES / magic_08 | 2022 | 247 observed dates | nominal|invalidation_before_midpoint_lower | 36.0% [31.4%, 41.5%] |
| ES / magic_08 | 2022 | 247 observed dates | nominal|invalidation_before_midpoint_upper | 36.8% [31.9%, 42.4%] |
| ES / magic_08 | 2022 | 247 observed dates | nominal|midpoint_before_invalidation_lower | 57.1% [51.0%, 61.9%] |
| ES / magic_08 | 2022 | 247 observed dates | nominal|midpoint_before_invalidation_upper | 57.9% [51.8%, 62.8%] |
| ES / magic_08 | 2022 | 247 observed dates | nominal|no_break_by_horizon_lower | 2.8% [0.8%, 5.3%] |
| ES / magic_08 | 2022 | 247 observed dates | nominal|no_break_by_horizon_upper | 2.8% [0.8%, 5.3%] |
| ES / magic_08 | 2023 | 250 / 250 | availability_delayed | break_then_neither_by_horizon: 11; future_censored: 4; invalidation_before_midpoint: 83; midpoint_before_invalidation: 151; no_break_by_horizon: 1 |
| ES / magic_08 | 2023 | 250 / 250 | nominal | break_then_neither_by_horizon: 11; future_censored: 4; invalidation_before_midpoint: 83; midpoint_before_invalidation: 151; no_break_by_horizon: 1 |
| ES / magic_08 | 2023 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 4.5% [2.0%, 7.7%] |
| ES / magic_08 | 2023 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 4.5% [2.0%, 7.7%] |
| ES / magic_08 | 2023 | 246 observed dates | availability_delayed|invalidation_before_midpoint_lower | 33.7% [27.6%, 40.2%] |
| ES / magic_08 | 2023 | 246 observed dates | availability_delayed|invalidation_before_midpoint_upper | 33.7% [27.6%, 40.2%] |
| ES / magic_08 | 2023 | 246 observed dates | availability_delayed|midpoint_before_invalidation_lower | 61.4% [54.9%, 67.6%] |
| ES / magic_08 | 2023 | 246 observed dates | availability_delayed|midpoint_before_invalidation_upper | 61.4% [54.9%, 67.6%] |
| ES / magic_08 | 2023 | 246 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.6%] |
| ES / magic_08 | 2023 | 246 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.6%] |
| ES / magic_08 | 2023 | 246 observed dates | nominal|break_then_neither_by_horizon_lower | 4.5% [2.0%, 7.7%] |
| ES / magic_08 | 2023 | 246 observed dates | nominal|break_then_neither_by_horizon_upper | 4.5% [2.0%, 7.7%] |
| ES / magic_08 | 2023 | 246 observed dates | nominal|invalidation_before_midpoint_lower | 33.7% [27.6%, 40.2%] |
| ES / magic_08 | 2023 | 246 observed dates | nominal|invalidation_before_midpoint_upper | 33.7% [27.6%, 40.2%] |
| ES / magic_08 | 2023 | 246 observed dates | nominal|midpoint_before_invalidation_lower | 61.4% [54.9%, 67.6%] |
| ES / magic_08 | 2023 | 246 observed dates | nominal|midpoint_before_invalidation_upper | 61.4% [54.9%, 67.6%] |
| ES / magic_08 | 2023 | 246 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.6%] |
| ES / magic_08 | 2023 | 246 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.6%] |
| ES / magic_08 | 2024 | 251 / 252 | availability_delayed | break_then_neither_by_horizon: 16; competing_order_ambiguous: 3; future_censored: 3; invalidation_before_midpoint: 93; midpoint_before_invalidation: 135; no_break_by_horizon: 1 |
| ES / magic_08 | 2024 | 251 / 252 | nominal | break_then_neither_by_horizon: 16; competing_order_ambiguous: 3; future_censored: 3; invalidation_before_midpoint: 93; midpoint_before_invalidation: 135; no_break_by_horizon: 1 |
| ES / magic_08 | 2024 | 248 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 6.5% [3.6%, 10.0%] |
| ES / magic_08 | 2024 | 248 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 6.5% [3.6%, 10.0%] |
| ES / magic_08 | 2024 | 248 observed dates | availability_delayed|invalidation_before_midpoint_lower | 37.5% [31.7%, 41.9%] |
| ES / magic_08 | 2024 | 248 observed dates | availability_delayed|invalidation_before_midpoint_upper | 38.7% [32.8%, 43.7%] |
| ES / magic_08 | 2024 | 248 observed dates | availability_delayed|midpoint_before_invalidation_lower | 54.4% [49.2%, 60.3%] |
| ES / magic_08 | 2024 | 248 observed dates | availability_delayed|midpoint_before_invalidation_upper | 55.6% [50.8%, 61.7%] |
| ES / magic_08 | 2024 | 248 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| ES / magic_08 | 2024 | 248 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| ES / magic_08 | 2024 | 248 observed dates | nominal|break_then_neither_by_horizon_lower | 6.5% [3.6%, 10.0%] |
| ES / magic_08 | 2024 | 248 observed dates | nominal|break_then_neither_by_horizon_upper | 6.5% [3.6%, 10.0%] |
| ES / magic_08 | 2024 | 248 observed dates | nominal|invalidation_before_midpoint_lower | 37.5% [31.7%, 41.9%] |
| ES / magic_08 | 2024 | 248 observed dates | nominal|invalidation_before_midpoint_upper | 38.7% [32.8%, 43.7%] |
| ES / magic_08 | 2024 | 248 observed dates | nominal|midpoint_before_invalidation_lower | 54.4% [49.2%, 60.3%] |
| ES / magic_08 | 2024 | 248 observed dates | nominal|midpoint_before_invalidation_upper | 55.6% [50.8%, 61.7%] |
| ES / magic_08 | 2024 | 248 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| ES / magic_08 | 2024 | 248 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| ES / magic_23 | 2020 | 237 / 253 | availability_delayed | break_then_neither_by_horizon: 7; future_censored: 11; invalidation_before_midpoint: 103; midpoint_before_invalidation: 113; no_break_by_horizon: 3 |
| ES / magic_23 | 2020 | 237 / 253 | nominal | break_then_neither_by_horizon: 7; future_censored: 11; invalidation_before_midpoint: 102; midpoint_before_invalidation: 114; no_break_by_horizon: 3 |
| ES / magic_23 | 2020 | 226 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.1% [1.3%, 5.5%] |
| ES / magic_23 | 2020 | 226 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.1% [1.3%, 5.5%] |
| ES / magic_23 | 2020 | 226 observed dates | availability_delayed|invalidation_before_midpoint_lower | 45.6% [39.9%, 51.6%] |
| ES / magic_23 | 2020 | 226 observed dates | availability_delayed|invalidation_before_midpoint_upper | 45.6% [39.9%, 51.6%] |
| ES / magic_23 | 2020 | 226 observed dates | availability_delayed|midpoint_before_invalidation_lower | 50.0% [44.1%, 55.7%] |
| ES / magic_23 | 2020 | 226 observed dates | availability_delayed|midpoint_before_invalidation_upper | 50.0% [44.1%, 55.7%] |
| ES / magic_23 | 2020 | 226 observed dates | availability_delayed|no_break_by_horizon_lower | 1.3% [0.0%, 2.9%] |
| ES / magic_23 | 2020 | 226 observed dates | availability_delayed|no_break_by_horizon_upper | 1.3% [0.0%, 2.9%] |
| ES / magic_23 | 2020 | 226 observed dates | nominal|break_then_neither_by_horizon_lower | 3.1% [1.3%, 5.5%] |
| ES / magic_23 | 2020 | 226 observed dates | nominal|break_then_neither_by_horizon_upper | 3.1% [1.3%, 5.5%] |
| ES / magic_23 | 2020 | 226 observed dates | nominal|invalidation_before_midpoint_lower | 45.1% [39.6%, 51.3%] |
| ES / magic_23 | 2020 | 226 observed dates | nominal|invalidation_before_midpoint_upper | 45.1% [39.6%, 51.3%] |
| ES / magic_23 | 2020 | 226 observed dates | nominal|midpoint_before_invalidation_lower | 50.4% [44.6%, 56.0%] |
| ES / magic_23 | 2020 | 226 observed dates | nominal|midpoint_before_invalidation_upper | 50.4% [44.6%, 56.0%] |
| ES / magic_23 | 2020 | 226 observed dates | nominal|no_break_by_horizon_lower | 1.3% [0.0%, 2.9%] |
| ES / magic_23 | 2020 | 226 observed dates | nominal|no_break_by_horizon_upper | 1.3% [0.0%, 2.9%] |
| ES / magic_23 | 2021 | 230 / 252 | availability_delayed | break_then_neither_by_horizon: 12; future_censored: 25; invalidation_before_midpoint: 64; midpoint_before_invalidation: 125; no_break_by_horizon: 4 |
| ES / magic_23 | 2021 | 230 / 252 | nominal | break_then_neither_by_horizon: 12; future_censored: 25; invalidation_before_midpoint: 62; midpoint_before_invalidation: 127; no_break_by_horizon: 4 |
| ES / magic_23 | 2021 | 205 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 5.9% [3.1%, 9.0%] |
| ES / magic_23 | 2021 | 205 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 5.9% [3.1%, 9.0%] |
| ES / magic_23 | 2021 | 205 observed dates | availability_delayed|invalidation_before_midpoint_lower | 31.2% [26.0%, 37.1%] |
| ES / magic_23 | 2021 | 205 observed dates | availability_delayed|invalidation_before_midpoint_upper | 31.2% [26.0%, 37.1%] |
| ES / magic_23 | 2021 | 205 observed dates | availability_delayed|midpoint_before_invalidation_lower | 61.0% [54.4%, 66.7%] |
| ES / magic_23 | 2021 | 205 observed dates | availability_delayed|midpoint_before_invalidation_upper | 61.0% [54.4%, 66.7%] |
| ES / magic_23 | 2021 | 205 observed dates | availability_delayed|no_break_by_horizon_lower | 2.0% [0.0%, 4.1%] |
| ES / magic_23 | 2021 | 205 observed dates | availability_delayed|no_break_by_horizon_upper | 2.0% [0.0%, 4.1%] |
| ES / magic_23 | 2021 | 205 observed dates | nominal|break_then_neither_by_horizon_lower | 5.9% [3.1%, 9.0%] |
| ES / magic_23 | 2021 | 205 observed dates | nominal|break_then_neither_by_horizon_upper | 5.9% [3.1%, 9.0%] |
| ES / magic_23 | 2021 | 205 observed dates | nominal|invalidation_before_midpoint_lower | 30.2% [25.0%, 36.0%] |
| ES / magic_23 | 2021 | 205 observed dates | nominal|invalidation_before_midpoint_upper | 30.2% [25.0%, 36.0%] |
| ES / magic_23 | 2021 | 205 observed dates | nominal|midpoint_before_invalidation_lower | 62.0% [55.7%, 67.3%] |
| ES / magic_23 | 2021 | 205 observed dates | nominal|midpoint_before_invalidation_upper | 62.0% [55.7%, 67.3%] |
| ES / magic_23 | 2021 | 205 observed dates | nominal|no_break_by_horizon_lower | 2.0% [0.0%, 4.1%] |
| ES / magic_23 | 2021 | 205 observed dates | nominal|no_break_by_horizon_upper | 2.0% [0.0%, 4.1%] |
| ES / magic_23 | 2022 | 241 / 251 | availability_delayed | break_then_neither_by_horizon: 12; competing_order_ambiguous: 4; future_censored: 2; invalidation_before_midpoint: 85; midpoint_before_invalidation: 133; no_break_by_horizon: 5 |
| ES / magic_23 | 2022 | 241 / 251 | nominal | break_then_neither_by_horizon: 12; competing_order_ambiguous: 3; future_censored: 2; invalidation_before_midpoint: 85; midpoint_before_invalidation: 134; no_break_by_horizon: 5 |
| ES / magic_23 | 2022 | 239 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 5.0% [2.5%, 7.4%] |
| ES / magic_23 | 2022 | 239 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 5.0% [2.5%, 7.4%] |
| ES / magic_23 | 2022 | 239 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.6% [29.8%, 42.1%] |
| ES / magic_23 | 2022 | 239 observed dates | availability_delayed|invalidation_before_midpoint_upper | 37.2% [31.9%, 43.6%] |
| ES / magic_23 | 2022 | 239 observed dates | availability_delayed|midpoint_before_invalidation_lower | 55.6% [49.4%, 61.2%] |
| ES / magic_23 | 2022 | 239 observed dates | availability_delayed|midpoint_before_invalidation_upper | 57.3% [50.9%, 63.0%] |
| ES / magic_23 | 2022 | 239 observed dates | availability_delayed|no_break_by_horizon_lower | 2.1% [0.8%, 4.2%] |
| ES / magic_23 | 2022 | 239 observed dates | availability_delayed|no_break_by_horizon_upper | 2.1% [0.8%, 4.2%] |
| ES / magic_23 | 2022 | 239 observed dates | nominal|break_then_neither_by_horizon_lower | 5.0% [2.5%, 7.4%] |
| ES / magic_23 | 2022 | 239 observed dates | nominal|break_then_neither_by_horizon_upper | 5.0% [2.5%, 7.4%] |
| ES / magic_23 | 2022 | 239 observed dates | nominal|invalidation_before_midpoint_lower | 35.6% [29.8%, 42.1%] |
| ES / magic_23 | 2022 | 239 observed dates | nominal|invalidation_before_midpoint_upper | 36.8% [31.4%, 42.9%] |
| ES / magic_23 | 2022 | 239 observed dates | nominal|midpoint_before_invalidation_lower | 56.1% [49.8%, 61.5%] |
| ES / magic_23 | 2022 | 239 observed dates | nominal|midpoint_before_invalidation_upper | 57.3% [50.9%, 63.0%] |
| ES / magic_23 | 2022 | 239 observed dates | nominal|no_break_by_horizon_lower | 2.1% [0.8%, 4.2%] |
| ES / magic_23 | 2022 | 239 observed dates | nominal|no_break_by_horizon_upper | 2.1% [0.8%, 4.2%] |
| ES / magic_23 | 2023 | 217 / 250 | availability_delayed | break_then_neither_by_horizon: 6; competing_order_ambiguous: 2; future_censored: 38; invalidation_before_midpoint: 70; midpoint_before_invalidation: 100; no_break_by_horizon: 1 |
| ES / magic_23 | 2023 | 217 / 250 | nominal | break_then_neither_by_horizon: 6; competing_order_ambiguous: 2; future_censored: 38; invalidation_before_midpoint: 69; midpoint_before_invalidation: 101; no_break_by_horizon: 1 |
| ES / magic_23 | 2023 | 179 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.4% [1.1%, 6.3%] |
| ES / magic_23 | 2023 | 179 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.9% [1.6%, 7.0%] |
| ES / magic_23 | 2023 | 179 observed dates | availability_delayed|invalidation_before_midpoint_lower | 39.1% [32.4%, 47.0%] |
| ES / magic_23 | 2023 | 179 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.7% [33.0%, 47.3%] |
| ES / magic_23 | 2023 | 179 observed dates | availability_delayed|midpoint_before_invalidation_lower | 55.9% [48.5%, 61.6%] |
| ES / magic_23 | 2023 | 179 observed dates | availability_delayed|midpoint_before_invalidation_upper | 57.0% [49.5%, 63.0%] |
| ES / magic_23 | 2023 | 179 observed dates | availability_delayed|no_break_by_horizon_lower | 0.6% [0.0%, 1.8%] |
| ES / magic_23 | 2023 | 179 observed dates | availability_delayed|no_break_by_horizon_upper | 0.6% [0.0%, 1.8%] |
| ES / magic_23 | 2023 | 179 observed dates | nominal|break_then_neither_by_horizon_lower | 3.4% [1.1%, 6.3%] |
| ES / magic_23 | 2023 | 179 observed dates | nominal|break_then_neither_by_horizon_upper | 3.9% [1.6%, 7.0%] |
| ES / magic_23 | 2023 | 179 observed dates | nominal|invalidation_before_midpoint_lower | 38.5% [31.6%, 46.2%] |
| ES / magic_23 | 2023 | 179 observed dates | nominal|invalidation_before_midpoint_upper | 39.1% [32.2%, 46.8%] |
| ES / magic_23 | 2023 | 179 observed dates | nominal|midpoint_before_invalidation_lower | 56.4% [49.0%, 61.9%] |
| ES / magic_23 | 2023 | 179 observed dates | nominal|midpoint_before_invalidation_upper | 57.5% [50.0%, 63.6%] |
| ES / magic_23 | 2023 | 179 observed dates | nominal|no_break_by_horizon_lower | 0.6% [0.0%, 1.8%] |
| ES / magic_23 | 2023 | 179 observed dates | nominal|no_break_by_horizon_upper | 0.6% [0.0%, 1.8%] |
| ES / magic_23 | 2024 | 219 / 252 | availability_delayed | break_then_neither_by_horizon: 12; future_censored: 38; invalidation_before_midpoint: 84; midpoint_before_invalidation: 81; no_break_by_horizon: 4 |
| ES / magic_23 | 2024 | 219 / 252 | nominal | break_then_neither_by_horizon: 11; future_censored: 38; invalidation_before_midpoint: 83; midpoint_before_invalidation: 83; no_break_by_horizon: 4 |
| ES / magic_23 | 2024 | 181 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 6.6% [3.2%, 10.6%] |
| ES / magic_23 | 2024 | 181 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 6.6% [3.2%, 10.6%] |
| ES / magic_23 | 2024 | 181 observed dates | availability_delayed|invalidation_before_midpoint_lower | 46.4% [39.2%, 53.1%] |
| ES / magic_23 | 2024 | 181 observed dates | availability_delayed|invalidation_before_midpoint_upper | 46.4% [39.2%, 53.1%] |
| ES / magic_23 | 2024 | 181 observed dates | availability_delayed|midpoint_before_invalidation_lower | 44.8% [37.6%, 52.0%] |
| ES / magic_23 | 2024 | 181 observed dates | availability_delayed|midpoint_before_invalidation_upper | 44.8% [37.6%, 52.0%] |
| ES / magic_23 | 2024 | 181 observed dates | availability_delayed|no_break_by_horizon_lower | 2.2% [0.5%, 4.4%] |
| ES / magic_23 | 2024 | 181 observed dates | availability_delayed|no_break_by_horizon_upper | 2.2% [0.5%, 4.4%] |
| ES / magic_23 | 2024 | 181 observed dates | nominal|break_then_neither_by_horizon_lower | 6.1% [2.7%, 10.1%] |
| ES / magic_23 | 2024 | 181 observed dates | nominal|break_then_neither_by_horizon_upper | 6.1% [2.7%, 10.1%] |
| ES / magic_23 | 2024 | 181 observed dates | nominal|invalidation_before_midpoint_lower | 45.9% [38.7%, 52.5%] |
| ES / magic_23 | 2024 | 181 observed dates | nominal|invalidation_before_midpoint_upper | 45.9% [38.7%, 52.5%] |
| ES / magic_23 | 2024 | 181 observed dates | nominal|midpoint_before_invalidation_lower | 45.9% [38.8%, 53.3%] |
| ES / magic_23 | 2024 | 181 observed dates | nominal|midpoint_before_invalidation_upper | 45.9% [38.8%, 53.3%] |
| ES / magic_23 | 2024 | 181 observed dates | nominal|no_break_by_horizon_lower | 2.2% [0.5%, 4.4%] |
| ES / magic_23 | 2024 | 181 observed dates | nominal|no_break_by_horizon_upper | 2.2% [0.5%, 4.4%] |
| NQ / ONS03 | 2020 | 241 / 253 | availability_delayed | candidate_available: 241; formation_unavailable: 12 |
| NQ / ONS03 | 2020 | 241 / 253 | nominal | candidate_available: 241; formation_unavailable: 12 |
| NQ / ONS03 | 2021 | 243 / 252 | availability_delayed | candidate_available: 243; formation_unavailable: 9 |
| NQ / ONS03 | 2021 | 243 / 252 | nominal | candidate_available: 243; formation_unavailable: 9 |
| NQ / ONS03 | 2022 | 246 / 251 | availability_delayed | candidate_available: 246; formation_unavailable: 5 |
| NQ / ONS03 | 2022 | 246 / 251 | nominal | candidate_available: 246; formation_unavailable: 5 |
| NQ / ONS03 | 2023 | 243 / 250 | availability_delayed | candidate_available: 243; formation_unavailable: 7 |
| NQ / ONS03 | 2023 | 243 / 250 | nominal | candidate_available: 243; formation_unavailable: 7 |
| NQ / ONS03 | 2024 | 222 / 252 | availability_delayed | candidate_available: 222; formation_unavailable: 30 |
| NQ / ONS03 | 2024 | 222 / 252 | nominal | candidate_available: 222; formation_unavailable: 30 |
| NQ / ONS20 | 2020 | 235 / 253 | availability_delayed | candidate_available: 235; formation_unavailable: 18 |
| NQ / ONS20 | 2020 | 235 / 253 | nominal | candidate_available: 235; formation_unavailable: 18 |
| NQ / ONS20 | 2021 | 229 / 252 | availability_delayed | candidate_available: 229; formation_unavailable: 23 |
| NQ / ONS20 | 2021 | 229 / 252 | nominal | candidate_available: 229; formation_unavailable: 23 |
| NQ / ONS20 | 2022 | 237 / 251 | availability_delayed | candidate_available: 237; formation_unavailable: 14 |
| NQ / ONS20 | 2022 | 237 / 251 | nominal | candidate_available: 237; formation_unavailable: 14 |
| NQ / ONS20 | 2023 | 230 / 250 | availability_delayed | candidate_available: 230; formation_unavailable: 20 |
| NQ / ONS20 | 2023 | 230 / 250 | nominal | candidate_available: 230; formation_unavailable: 20 |
| NQ / ONS20 | 2024 | 207 / 252 | availability_delayed | candidate_available: 207; formation_unavailable: 45 |
| NQ / ONS20 | 2024 | 207 / 252 | nominal | candidate_available: 207; formation_unavailable: 45 |
| NQ / PIN073_1 | 2020 | 244 / 253 | availability_delayed | candidate_available: 239; conditioning_censored: 5; formation_unavailable: 9 |
| NQ / PIN073_1 | 2020 | 244 / 253 | nominal | candidate_available: 239; conditioning_censored: 5; formation_unavailable: 9 |
| NQ / PIN073_1 | 2020 | 235 observed dates | availability_delayed|compatible_reach | 72.8% [66.5%, 78.7%] |
| NQ / PIN073_1 | 2020 | 235 observed dates | availability_delayed|definite_print | 24.3% [18.8%, 29.5%] |
| NQ / PIN073_1 | 2020 | 145 observed dates | availability_delayed|stratum=both|compatible_reach | 80.0% [72.6%, 86.5%] |
| NQ / PIN073_1 | 2020 | 145 observed dates | availability_delayed|stratum=both|definite_print | 26.9% [20.4%, 33.8%] |
| NQ / PIN073_1 | 2020 | 50 observed dates | availability_delayed|stratum=high_only|compatible_reach | 62.0% [50.0%, 76.7%] |
| NQ / PIN073_1 | 2020 | 50 observed dates | availability_delayed|stratum=high_only|definite_print | 18.0% [8.7%, 28.6%] |
| NQ / PIN073_1 | 2020 | 40 observed dates | availability_delayed|stratum=low_only|compatible_reach | 60.0% [44.7%, 75.5%] |
| NQ / PIN073_1 | 2020 | 40 observed dates | availability_delayed|stratum=low_only|definite_print | 22.5% [10.9%, 35.9%] |
| NQ / PIN073_1 | 2020 | 238 observed dates | nominal|compatible_reach | 72.7% [66.4%, 78.5%] |
| NQ / PIN073_1 | 2020 | 238 observed dates | nominal|definite_print | 23.9% [18.4%, 29.2%] |
| NQ / PIN073_1 | 2020 | 145 observed dates | nominal|stratum=both|compatible_reach | 80.0% [72.6%, 86.5%] |
| NQ / PIN073_1 | 2020 | 145 observed dates | nominal|stratum=both|definite_print | 26.9% [20.4%, 33.8%] |
| NQ / PIN073_1 | 2020 | 50 observed dates | nominal|stratum=high_only|compatible_reach | 62.0% [50.0%, 76.7%] |
| NQ / PIN073_1 | 2020 | 50 observed dates | nominal|stratum=high_only|definite_print | 18.0% [8.7%, 28.6%] |
| NQ / PIN073_1 | 2020 | 40 observed dates | nominal|stratum=low_only|compatible_reach | 60.0% [44.7%, 75.5%] |
| NQ / PIN073_1 | 2020 | 40 observed dates | nominal|stratum=low_only|definite_print | 22.5% [10.9%, 35.9%] |
| NQ / PIN073_1 | 2021 | 247 / 252 | availability_delayed | candidate_available: 243; conditioning_censored: 4; formation_unavailable: 5 |
| NQ / PIN073_1 | 2021 | 247 / 252 | nominal | candidate_available: 243; conditioning_censored: 4; formation_unavailable: 5 |
| NQ / PIN073_1 | 2021 | 242 observed dates | availability_delayed|compatible_reach | 74.0% [68.7%, 78.6%] |
| NQ / PIN073_1 | 2021 | 242 observed dates | availability_delayed|definite_print | 26.0% [21.1%, 31.0%] |
| NQ / PIN073_1 | 2021 | 148 observed dates | availability_delayed|stratum=both|compatible_reach | 81.8% [75.2%, 87.1%] |
| NQ / PIN073_1 | 2021 | 148 observed dates | availability_delayed|stratum=both|definite_print | 28.4% [22.3%, 35.0%] |
| NQ / PIN073_1 | 2021 | 53 observed dates | availability_delayed|stratum=high_only|compatible_reach | 60.4% [46.2%, 71.7%] |
| NQ / PIN073_1 | 2021 | 53 observed dates | availability_delayed|stratum=high_only|definite_print | 20.8% [11.7%, 30.4%] |
| NQ / PIN073_1 | 2021 | 41 observed dates | availability_delayed|stratum=low_only|compatible_reach | 63.4% [48.9%, 76.5%] |
| NQ / PIN073_1 | 2021 | 41 observed dates | availability_delayed|stratum=low_only|definite_print | 24.4% [11.4%, 37.5%] |
| NQ / PIN073_1 | 2021 | 246 observed dates | nominal|compatible_reach | 74.0% [68.9%, 78.6%] |
| NQ / PIN073_1 | 2021 | 246 observed dates | nominal|definite_print | 26.0% [21.1%, 31.1%] |
| NQ / PIN073_1 | 2021 | 148 observed dates | nominal|stratum=both|compatible_reach | 81.8% [75.2%, 87.1%] |
| NQ / PIN073_1 | 2021 | 148 observed dates | nominal|stratum=both|definite_print | 28.4% [22.3%, 35.0%] |
| NQ / PIN073_1 | 2021 | 53 observed dates | nominal|stratum=high_only|compatible_reach | 60.4% [46.2%, 71.7%] |
| NQ / PIN073_1 | 2021 | 53 observed dates | nominal|stratum=high_only|definite_print | 20.8% [11.7%, 30.4%] |
| NQ / PIN073_1 | 2021 | 41 observed dates | nominal|stratum=low_only|compatible_reach | 63.4% [48.9%, 76.5%] |
| NQ / PIN073_1 | 2021 | 41 observed dates | nominal|stratum=low_only|definite_print | 24.4% [11.4%, 37.5%] |
| NQ / PIN073_1 | 2022 | 247 / 251 | availability_delayed | candidate_available: 245; conditioning_censored: 2; formation_unavailable: 4 |
| NQ / PIN073_1 | 2022 | 247 / 251 | nominal | candidate_available: 245; conditioning_censored: 2; formation_unavailable: 4 |
| NQ / PIN073_1 | 2022 | 243 observed dates | availability_delayed|compatible_reach | 73.7% [68.9%, 78.7%] |
| NQ / PIN073_1 | 2022 | 243 observed dates | availability_delayed|definite_print | 18.5% [13.9%, 22.5%] |
| NQ / PIN073_1 | 2022 | 155 observed dates | availability_delayed|stratum=both|compatible_reach | 78.7% [73.5%, 85.4%] |
| NQ / PIN073_1 | 2022 | 155 observed dates | availability_delayed|stratum=both|definite_print | 21.9% [16.0%, 27.6%] |
| NQ / PIN073_1 | 2022 | 45 observed dates | availability_delayed|stratum=high_only|compatible_reach | 75.6% [62.2%, 88.2%] |
| NQ / PIN073_1 | 2022 | 45 observed dates | availability_delayed|stratum=high_only|definite_print | 11.1% [2.6%, 21.4%] |
| NQ / PIN073_1 | 2022 | 43 observed dates | availability_delayed|stratum=low_only|compatible_reach | 53.5% [39.5%, 67.4%] |
| NQ / PIN073_1 | 2022 | 43 observed dates | availability_delayed|stratum=low_only|definite_print | 14.0% [4.3%, 25.0%] |
| NQ / PIN073_1 | 2022 | 245 observed dates | nominal|compatible_reach | 74.3% [69.7%, 79.5%] |
| NQ / PIN073_1 | 2022 | 245 observed dates | nominal|definite_print | 18.8% [14.2%, 22.8%] |
| NQ / PIN073_1 | 2022 | 155 observed dates | nominal|stratum=both|compatible_reach | 79.4% [74.1%, 85.6%] |
| NQ / PIN073_1 | 2022 | 155 observed dates | nominal|stratum=both|definite_print | 21.9% [16.0%, 27.6%] |
| NQ / PIN073_1 | 2022 | 45 observed dates | nominal|stratum=high_only|compatible_reach | 75.6% [62.2%, 88.2%] |
| NQ / PIN073_1 | 2022 | 45 observed dates | nominal|stratum=high_only|definite_print | 11.1% [2.6%, 21.4%] |
| NQ / PIN073_1 | 2022 | 43 observed dates | nominal|stratum=low_only|compatible_reach | 53.5% [39.5%, 67.4%] |
| NQ / PIN073_1 | 2022 | 43 observed dates | nominal|stratum=low_only|definite_print | 14.0% [4.3%, 25.0%] |
| NQ / PIN073_1 | 2023 | 242 / 250 | availability_delayed | candidate_available: 241; conditioning_censored: 1; formation_unavailable: 8 |
| NQ / PIN073_1 | 2023 | 242 / 250 | nominal | candidate_available: 241; conditioning_censored: 1; formation_unavailable: 8 |
| NQ / PIN073_1 | 2023 | 238 observed dates | availability_delayed|compatible_reach | 77.7% [72.4%, 82.8%] |
| NQ / PIN073_1 | 2023 | 238 observed dates | availability_delayed|definite_print | 26.5% [21.5%, 31.7%] |
| NQ / PIN073_1 | 2023 | 157 observed dates | availability_delayed|stratum=both|compatible_reach | 82.2% [76.8%, 87.5%] |
| NQ / PIN073_1 | 2023 | 157 observed dates | availability_delayed|stratum=both|definite_print | 27.4% [21.2%, 33.8%] |
| NQ / PIN073_1 | 2023 | 49 observed dates | availability_delayed|stratum=high_only|compatible_reach | 69.4% [56.9%, 80.5%] |
| NQ / PIN073_1 | 2023 | 49 observed dates | availability_delayed|stratum=high_only|definite_print | 26.5% [16.0%, 38.3%] |
| NQ / PIN073_1 | 2023 | 32 observed dates | availability_delayed|stratum=low_only|compatible_reach | 68.8% [48.6%, 84.0%] |
| NQ / PIN073_1 | 2023 | 32 observed dates | availability_delayed|stratum=low_only|definite_print | 21.9% [7.7%, 37.0%] |
| NQ / PIN073_1 | 2023 | 239 observed dates | nominal|compatible_reach | 77.8% [72.7%, 83.0%] |
| NQ / PIN073_1 | 2023 | 239 observed dates | nominal|definite_print | 26.4% [21.4%, 31.6%] |
| NQ / PIN073_1 | 2023 | 157 observed dates | nominal|stratum=both|compatible_reach | 82.2% [76.8%, 87.5%] |
| NQ / PIN073_1 | 2023 | 157 observed dates | nominal|stratum=both|definite_print | 27.4% [21.2%, 33.8%] |
| NQ / PIN073_1 | 2023 | 49 observed dates | nominal|stratum=high_only|compatible_reach | 69.4% [56.9%, 80.5%] |
| NQ / PIN073_1 | 2023 | 49 observed dates | nominal|stratum=high_only|definite_print | 26.5% [16.0%, 38.3%] |
| NQ / PIN073_1 | 2023 | 32 observed dates | nominal|stratum=low_only|compatible_reach | 68.8% [48.6%, 84.0%] |
| NQ / PIN073_1 | 2023 | 32 observed dates | nominal|stratum=low_only|definite_print | 21.9% [7.7%, 37.0%] |
| NQ / PIN073_1 | 2024 | 223 / 252 | availability_delayed | candidate_available: 221; conditioning_censored: 2; formation_unavailable: 29 |
| NQ / PIN073_1 | 2024 | 223 / 252 | nominal | candidate_available: 221; conditioning_censored: 2; formation_unavailable: 29 |
| NQ / PIN073_1 | 2024 | 219 observed dates | availability_delayed|compatible_reach | 78.1% [73.9%, 83.6%] |
| NQ / PIN073_1 | 2024 | 219 observed dates | availability_delayed|definite_print | 30.6% [24.7%, 37.7%] |
| NQ / PIN073_1 | 2024 | 143 observed dates | availability_delayed|stratum=both|compatible_reach | 76.9% [71.7%, 84.2%] |
| NQ / PIN073_1 | 2024 | 143 observed dates | availability_delayed|stratum=both|definite_print | 30.1% [22.8%, 39.1%] |
| NQ / PIN073_1 | 2024 | 44 observed dates | availability_delayed|stratum=high_only|compatible_reach | 77.3% [64.5%, 88.1%] |
| NQ / PIN073_1 | 2024 | 44 observed dates | availability_delayed|stratum=high_only|definite_print | 25.0% [12.5%, 37.8%] |
| NQ / PIN073_1 | 2024 | 32 observed dates | availability_delayed|stratum=low_only|compatible_reach | 84.4% [72.0%, 96.2%] |
| NQ / PIN073_1 | 2024 | 32 observed dates | availability_delayed|stratum=low_only|definite_print | 40.6% [25.0%, 56.7%] |
| NQ / PIN073_1 | 2024 | 221 observed dates | nominal|compatible_reach | 77.8% [73.4%, 83.3%] |
| NQ / PIN073_1 | 2024 | 221 observed dates | nominal|definite_print | 30.3% [24.5%, 37.1%] |
| NQ / PIN073_1 | 2024 | 143 observed dates | nominal|stratum=both|compatible_reach | 76.9% [71.7%, 84.2%] |
| NQ / PIN073_1 | 2024 | 143 observed dates | nominal|stratum=both|definite_print | 30.1% [22.8%, 39.1%] |
| NQ / PIN073_1 | 2024 | 44 observed dates | nominal|stratum=high_only|compatible_reach | 77.3% [64.5%, 88.1%] |
| NQ / PIN073_1 | 2024 | 44 observed dates | nominal|stratum=high_only|definite_print | 25.0% [12.5%, 37.8%] |
| NQ / PIN073_1 | 2024 | 32 observed dates | nominal|stratum=low_only|compatible_reach | 84.4% [72.0%, 96.2%] |
| NQ / PIN073_1 | 2024 | 32 observed dates | nominal|stratum=low_only|definite_print | 40.6% [25.0%, 56.7%] |
| NQ / PIN073_2 | 2020 | 245 / 253 | availability_delayed | candidate_available: 244; conditioning_censored: 1; formation_unavailable: 8 |
| NQ / PIN073_2 | 2020 | 245 / 253 | nominal | candidate_available: 244; conditioning_censored: 1; formation_unavailable: 8 |
| NQ / PIN073_2 | 2020 | 240 observed dates | availability_delayed|compatible_reach | 31.7% [26.1%, 37.9%] |
| NQ / PIN073_2 | 2020 | 240 observed dates | availability_delayed|definite_print | 9.6% [6.2%, 13.4%] |
| NQ / PIN073_2 | 2020 | 188 observed dates | availability_delayed|stratum=both|compatible_reach | 33.0% [27.2%, 39.8%] |
| NQ / PIN073_2 | 2020 | 188 observed dates | availability_delayed|stratum=both|definite_print | 9.6% [5.9%, 13.6%] |
| NQ / PIN073_2 | 2020 | 28 observed dates | availability_delayed|stratum=high_only|compatible_reach | 17.9% [3.7%, 34.8%] |
| NQ / PIN073_2 | 2020 | 28 observed dates | availability_delayed|stratum=high_only|definite_print | 7.1% [0.0%, 18.2%] |
| NQ / PIN073_2 | 2020 | 24 observed dates | availability_delayed|stratum=low_only|compatible_reach | 37.5% [17.9%, 57.1%] |
| NQ / PIN073_2 | 2020 | 24 observed dates | availability_delayed|stratum=low_only|definite_print | 12.5% [0.0%, 26.3%] |
| NQ / PIN073_2 | 2020 | 240 observed dates | nominal|compatible_reach | 31.7% [26.1%, 37.9%] |
| NQ / PIN073_2 | 2020 | 240 observed dates | nominal|definite_print | 9.6% [6.2%, 13.4%] |
| NQ / PIN073_2 | 2020 | 188 observed dates | nominal|stratum=both|compatible_reach | 33.0% [27.2%, 39.8%] |
| NQ / PIN073_2 | 2020 | 188 observed dates | nominal|stratum=both|definite_print | 9.6% [5.9%, 13.6%] |
| NQ / PIN073_2 | 2020 | 28 observed dates | nominal|stratum=high_only|compatible_reach | 17.9% [3.7%, 34.8%] |
| NQ / PIN073_2 | 2020 | 28 observed dates | nominal|stratum=high_only|definite_print | 7.1% [0.0%, 18.2%] |
| NQ / PIN073_2 | 2020 | 24 observed dates | nominal|stratum=low_only|compatible_reach | 37.5% [17.9%, 57.1%] |
| NQ / PIN073_2 | 2020 | 24 observed dates | nominal|stratum=low_only|definite_print | 12.5% [0.0%, 26.3%] |
| NQ / PIN073_2 | 2021 | 249 / 252 | availability_delayed | candidate_available: 248; conditioning_censored: 1; formation_unavailable: 3 |
| NQ / PIN073_2 | 2021 | 249 / 252 | nominal | candidate_available: 248; conditioning_censored: 1; formation_unavailable: 3 |
| NQ / PIN073_2 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 27.9% [22.5%, 33.1%] |
| NQ / PIN073_2 | 2021 | 247 observed dates | availability_delayed|definite_print | 7.7% [4.0%, 11.8%] |
| NQ / PIN073_2 | 2021 | 186 observed dates | availability_delayed|stratum=both|compatible_reach | 33.9% [27.3%, 40.3%] |
| NQ / PIN073_2 | 2021 | 186 observed dates | availability_delayed|stratum=both|definite_print | 9.1% [4.5%, 13.9%] |
| NQ / PIN073_2 | 2021 | 41 observed dates | availability_delayed|stratum=high_only|compatible_reach | 9.8% [2.3%, 19.5%] |
| NQ / PIN073_2 | 2021 | 41 observed dates | availability_delayed|stratum=high_only|definite_print | 2.4% [0.0%, 8.6%] |
| NQ / PIN073_2 | 2021 | 20 observed dates | availability_delayed|stratum=low_only|compatible_reach | 10.0% [0.0%, 26.7%] |
| NQ / PIN073_2 | 2021 | 20 observed dates | availability_delayed|stratum=low_only|definite_print | 5.0% [0.0%, 16.7%] |
| NQ / PIN073_2 | 2021 | 247 observed dates | nominal|compatible_reach | 27.9% [22.5%, 33.1%] |
| NQ / PIN073_2 | 2021 | 247 observed dates | nominal|definite_print | 7.7% [4.0%, 11.8%] |
| NQ / PIN073_2 | 2021 | 186 observed dates | nominal|stratum=both|compatible_reach | 33.9% [27.3%, 40.3%] |
| NQ / PIN073_2 | 2021 | 186 observed dates | nominal|stratum=both|definite_print | 9.1% [4.5%, 13.9%] |
| NQ / PIN073_2 | 2021 | 41 observed dates | nominal|stratum=high_only|compatible_reach | 9.8% [2.3%, 19.5%] |
| NQ / PIN073_2 | 2021 | 41 observed dates | nominal|stratum=high_only|definite_print | 2.4% [0.0%, 8.6%] |
| NQ / PIN073_2 | 2021 | 20 observed dates | nominal|stratum=low_only|compatible_reach | 10.0% [0.0%, 26.7%] |
| NQ / PIN073_2 | 2021 | 20 observed dates | nominal|stratum=low_only|definite_print | 5.0% [0.0%, 16.7%] |
| NQ / PIN073_2 | 2022 | 249 / 251 | availability_delayed | candidate_available: 247; conditioning_censored: 2; formation_unavailable: 2 |
| NQ / PIN073_2 | 2022 | 249 / 251 | nominal | candidate_available: 247; conditioning_censored: 2; formation_unavailable: 2 |
| NQ / PIN073_2 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 29.3% [24.0%, 35.0%] |
| NQ / PIN073_2 | 2022 | 246 observed dates | availability_delayed|definite_print | 4.5% [2.0%, 7.3%] |
| NQ / PIN073_2 | 2022 | 179 observed dates | availability_delayed|stratum=both|compatible_reach | 35.2% [28.9%, 42.4%] |
| NQ / PIN073_2 | 2022 | 179 observed dates | availability_delayed|stratum=both|definite_print | 5.6% [2.7%, 9.3%] |
| NQ / PIN073_2 | 2022 | 28 observed dates | availability_delayed|stratum=high_only|compatible_reach | 21.4% [5.0%, 39.3%] |
| NQ / PIN073_2 | 2022 | 28 observed dates | availability_delayed|stratum=high_only|definite_print | 0.0% [0.0%, 0.0%] |
| NQ / PIN073_2 | 2022 | 39 observed dates | availability_delayed|stratum=low_only|compatible_reach | 7.7% [0.0%, 16.3%] |
| NQ / PIN073_2 | 2022 | 39 observed dates | availability_delayed|stratum=low_only|definite_print | 2.6% [0.0%, 8.8%] |
| NQ / PIN073_2 | 2022 | 246 observed dates | nominal|compatible_reach | 29.3% [24.0%, 35.0%] |
| NQ / PIN073_2 | 2022 | 246 observed dates | nominal|definite_print | 4.5% [2.0%, 7.3%] |
| NQ / PIN073_2 | 2022 | 179 observed dates | nominal|stratum=both|compatible_reach | 35.2% [28.9%, 42.4%] |
| NQ / PIN073_2 | 2022 | 179 observed dates | nominal|stratum=both|definite_print | 5.6% [2.7%, 9.3%] |
| NQ / PIN073_2 | 2022 | 28 observed dates | nominal|stratum=high_only|compatible_reach | 21.4% [5.0%, 39.3%] |
| NQ / PIN073_2 | 2022 | 28 observed dates | nominal|stratum=high_only|definite_print | 0.0% [0.0%, 0.0%] |
| NQ / PIN073_2 | 2022 | 39 observed dates | nominal|stratum=low_only|compatible_reach | 7.7% [0.0%, 16.3%] |
| NQ / PIN073_2 | 2022 | 39 observed dates | nominal|stratum=low_only|definite_print | 2.6% [0.0%, 8.8%] |
| NQ / PIN073_2 | 2023 | 249 / 250 | availability_delayed | candidate_available: 246; conditioning_censored: 3; formation_unavailable: 1 |
| NQ / PIN073_2 | 2023 | 249 / 250 | nominal | candidate_available: 246; conditioning_censored: 3; formation_unavailable: 1 |
| NQ / PIN073_2 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 30.7% [25.8%, 35.9%] |
| NQ / PIN073_2 | 2023 | 244 observed dates | availability_delayed|definite_print | 11.1% [6.9%, 15.4%] |
| NQ / PIN073_2 | 2023 | 181 observed dates | availability_delayed|stratum=both|compatible_reach | 37.0% [30.9%, 44.1%] |
| NQ / PIN073_2 | 2023 | 181 observed dates | availability_delayed|stratum=both|definite_print | 13.3% [8.2%, 18.8%] |
| NQ / PIN073_2 | 2023 | 41 observed dates | availability_delayed|stratum=high_only|compatible_reach | 12.2% [2.9%, 21.1%] |
| NQ / PIN073_2 | 2023 | 41 observed dates | availability_delayed|stratum=high_only|definite_print | 4.9% [0.0%, 11.3%] |
| NQ / PIN073_2 | 2023 | 22 observed dates | availability_delayed|stratum=low_only|compatible_reach | 13.6% [0.0%, 29.4%] |
| NQ / PIN073_2 | 2023 | 22 observed dates | availability_delayed|stratum=low_only|definite_print | 4.5% [0.0%, 15.0%] |
| NQ / PIN073_2 | 2023 | 244 observed dates | nominal|compatible_reach | 30.7% [25.8%, 35.9%] |
| NQ / PIN073_2 | 2023 | 244 observed dates | nominal|definite_print | 11.1% [6.9%, 15.4%] |
| NQ / PIN073_2 | 2023 | 181 observed dates | nominal|stratum=both|compatible_reach | 37.0% [30.9%, 44.1%] |
| NQ / PIN073_2 | 2023 | 181 observed dates | nominal|stratum=both|definite_print | 13.3% [8.2%, 18.8%] |
| NQ / PIN073_2 | 2023 | 41 observed dates | nominal|stratum=high_only|compatible_reach | 12.2% [2.9%, 21.1%] |
| NQ / PIN073_2 | 2023 | 41 observed dates | nominal|stratum=high_only|definite_print | 4.9% [0.0%, 11.3%] |
| NQ / PIN073_2 | 2023 | 22 observed dates | nominal|stratum=low_only|compatible_reach | 13.6% [0.0%, 29.4%] |
| NQ / PIN073_2 | 2023 | 22 observed dates | nominal|stratum=low_only|definite_print | 4.5% [0.0%, 15.0%] |
| NQ / PIN073_2 | 2024 | 227 / 252 | availability_delayed | candidate_available: 225; conditioning_censored: 2; formation_unavailable: 25 |
| NQ / PIN073_2 | 2024 | 227 / 252 | nominal | candidate_available: 225; conditioning_censored: 2; formation_unavailable: 25 |
| NQ / PIN073_2 | 2024 | 223 observed dates | availability_delayed|compatible_reach | 31.8% [26.2%, 38.2%] |
| NQ / PIN073_2 | 2024 | 223 observed dates | availability_delayed|definite_print | 10.8% [7.4%, 14.6%] |
| NQ / PIN073_2 | 2024 | 164 observed dates | availability_delayed|stratum=both|compatible_reach | 36.6% [29.6%, 44.1%] |
| NQ / PIN073_2 | 2024 | 164 observed dates | availability_delayed|stratum=both|definite_print | 12.8% [8.3%, 17.6%] |
| NQ / PIN073_2 | 2024 | 24 observed dates | availability_delayed|stratum=high_only|compatible_reach | 16.7% [3.6%, 33.3%] |
| NQ / PIN073_2 | 2024 | 24 observed dates | availability_delayed|stratum=high_only|definite_print | 0.0% [0.0%, 0.0%] |
| NQ / PIN073_2 | 2024 | 35 observed dates | availability_delayed|stratum=low_only|compatible_reach | 20.0% [7.9%, 35.5%] |
| NQ / PIN073_2 | 2024 | 35 observed dates | availability_delayed|stratum=low_only|definite_print | 8.6% [0.0%, 20.0%] |
| NQ / PIN073_2 | 2024 | 223 observed dates | nominal|compatible_reach | 31.8% [26.2%, 38.2%] |
| NQ / PIN073_2 | 2024 | 223 observed dates | nominal|definite_print | 10.8% [7.4%, 14.6%] |
| NQ / PIN073_2 | 2024 | 164 observed dates | nominal|stratum=both|compatible_reach | 36.6% [29.6%, 44.1%] |
| NQ / PIN073_2 | 2024 | 164 observed dates | nominal|stratum=both|definite_print | 12.8% [8.3%, 17.6%] |
| NQ / PIN073_2 | 2024 | 24 observed dates | nominal|stratum=high_only|compatible_reach | 16.7% [3.6%, 33.3%] |
| NQ / PIN073_2 | 2024 | 24 observed dates | nominal|stratum=high_only|definite_print | 0.0% [0.0%, 0.0%] |
| NQ / PIN073_2 | 2024 | 35 observed dates | nominal|stratum=low_only|compatible_reach | 20.0% [7.9%, 35.5%] |
| NQ / PIN073_2 | 2024 | 35 observed dates | nominal|stratum=low_only|definite_print | 8.6% [0.0%, 20.0%] |
| NQ / PIN073_3 | 2020 | 241 / 253 | availability_delayed | candidate_available: 237; conditioning_censored: 4; formation_unavailable: 12 |
| NQ / PIN073_3 | 2020 | 241 / 253 | nominal | candidate_available: 237; conditioning_censored: 4; formation_unavailable: 12 |
| NQ / PIN073_3 | 2020 | 234 observed dates | availability_delayed|compatible_reach | 75.6% [69.7%, 81.2%] |
| NQ / PIN073_3 | 2020 | 234 observed dates | availability_delayed|definite_print | 33.8% [26.9%, 40.8%] |
| NQ / PIN073_3 | 2020 | 91 observed dates | availability_delayed|stratum=both|compatible_reach | 72.5% [63.9%, 81.8%] |
| NQ / PIN073_3 | 2020 | 91 observed dates | availability_delayed|stratum=both|definite_print | 30.8% [22.2%, 41.1%] |
| NQ / PIN073_3 | 2020 | 78 observed dates | availability_delayed|stratum=high_only|compatible_reach | 74.4% [63.7%, 84.5%] |
| NQ / PIN073_3 | 2020 | 78 observed dates | availability_delayed|stratum=high_only|definite_print | 29.5% [18.8%, 40.5%] |
| NQ / PIN073_3 | 2020 | 61 observed dates | availability_delayed|stratum=low_only|compatible_reach | 80.3% [70.4%, 88.7%] |
| NQ / PIN073_3 | 2020 | 61 observed dates | availability_delayed|stratum=low_only|definite_print | 42.6% [28.8%, 54.2%] |
| NQ / PIN073_3 | 2020 | 4 observed dates | availability_delayed|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| NQ / PIN073_3 | 2020 | 4 observed dates | availability_delayed|stratum=neither|definite_print | 50.0% [0.0%, 100.0%] |
| NQ / PIN073_3 | 2020 | 237 observed dates | nominal|compatible_reach | 76.4% [70.5%, 81.8%] |
| NQ / PIN073_3 | 2020 | 237 observed dates | nominal|definite_print | 33.3% [26.4%, 40.0%] |
| NQ / PIN073_3 | 2020 | 91 observed dates | nominal|stratum=both|compatible_reach | 73.6% [64.9%, 83.2%] |
| NQ / PIN073_3 | 2020 | 91 observed dates | nominal|stratum=both|definite_print | 30.8% [22.2%, 41.1%] |
| NQ / PIN073_3 | 2020 | 78 observed dates | nominal|stratum=high_only|compatible_reach | 74.4% [63.7%, 84.5%] |
| NQ / PIN073_3 | 2020 | 78 observed dates | nominal|stratum=high_only|definite_print | 29.5% [18.8%, 40.5%] |
| NQ / PIN073_3 | 2020 | 61 observed dates | nominal|stratum=low_only|compatible_reach | 82.0% [72.5%, 90.5%] |
| NQ / PIN073_3 | 2020 | 61 observed dates | nominal|stratum=low_only|definite_print | 42.6% [28.8%, 54.2%] |
| NQ / PIN073_3 | 2020 | 4 observed dates | nominal|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| NQ / PIN073_3 | 2020 | 4 observed dates | nominal|stratum=neither|definite_print | 50.0% [0.0%, 100.0%] |
| NQ / PIN073_3 | 2021 | 234 / 252 | availability_delayed | candidate_available: 228; conditioning_censored: 6; formation_unavailable: 18 |
| NQ / PIN073_3 | 2021 | 234 / 252 | nominal | candidate_available: 228; conditioning_censored: 6; formation_unavailable: 18 |
| NQ / PIN073_3 | 2021 | 227 observed dates | availability_delayed|compatible_reach | 79.7% [74.1%, 84.8%] |
| NQ / PIN073_3 | 2021 | 227 observed dates | availability_delayed|definite_print | 37.4% [31.2%, 43.7%] |
| NQ / PIN073_3 | 2021 | 84 observed dates | availability_delayed|stratum=both|compatible_reach | 78.6% [70.0%, 86.6%] |
| NQ / PIN073_3 | 2021 | 84 observed dates | availability_delayed|stratum=both|definite_print | 40.5% [29.5%, 51.8%] |
| NQ / PIN073_3 | 2021 | 82 observed dates | availability_delayed|stratum=high_only|compatible_reach | 82.9% [74.7%, 90.4%] |
| NQ / PIN073_3 | 2021 | 82 observed dates | availability_delayed|stratum=high_only|definite_print | 35.4% [25.3%, 44.9%] |
| NQ / PIN073_3 | 2021 | 59 observed dates | availability_delayed|stratum=low_only|compatible_reach | 76.3% [63.2%, 87.0%] |
| NQ / PIN073_3 | 2021 | 59 observed dates | availability_delayed|stratum=low_only|definite_print | 37.3% [23.1%, 51.0%] |
| NQ / PIN073_3 | 2021 | 2 observed dates | availability_delayed|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| NQ / PIN073_3 | 2021 | 2 observed dates | availability_delayed|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| NQ / PIN073_3 | 2021 | 232 observed dates | nominal|compatible_reach | 80.2% [75.1%, 85.2%] |
| NQ / PIN073_3 | 2021 | 232 observed dates | nominal|definite_print | 37.9% [31.9%, 44.1%] |
| NQ / PIN073_3 | 2021 | 84 observed dates | nominal|stratum=both|compatible_reach | 79.8% [71.4%, 87.8%] |
| NQ / PIN073_3 | 2021 | 84 observed dates | nominal|stratum=both|definite_print | 40.5% [29.5%, 51.8%] |
| NQ / PIN073_3 | 2021 | 82 observed dates | nominal|stratum=high_only|compatible_reach | 82.9% [74.7%, 90.4%] |
| NQ / PIN073_3 | 2021 | 82 observed dates | nominal|stratum=high_only|definite_print | 35.4% [25.3%, 44.9%] |
| NQ / PIN073_3 | 2021 | 59 observed dates | nominal|stratum=low_only|compatible_reach | 76.3% [63.2%, 87.0%] |
| NQ / PIN073_3 | 2021 | 59 observed dates | nominal|stratum=low_only|definite_print | 37.3% [23.1%, 51.0%] |
| NQ / PIN073_3 | 2021 | 2 observed dates | nominal|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| NQ / PIN073_3 | 2021 | 2 observed dates | nominal|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| NQ / PIN073_3 | 2022 | 245 / 251 | availability_delayed | candidate_available: 243; conditioning_censored: 2; formation_unavailable: 6 |
| NQ / PIN073_3 | 2022 | 245 / 251 | nominal | candidate_available: 243; conditioning_censored: 2; formation_unavailable: 6 |
| NQ / PIN073_3 | 2022 | 242 observed dates | availability_delayed|compatible_reach | 76.9% [72.3%, 82.3%] |
| NQ / PIN073_3 | 2022 | 242 observed dates | availability_delayed|definite_print | 33.9% [28.2%, 39.3%] |
| NQ / PIN073_3 | 2022 | 100 observed dates | availability_delayed|stratum=both|compatible_reach | 80.0% [72.3%, 86.7%] |
| NQ / PIN073_3 | 2022 | 100 observed dates | availability_delayed|stratum=both|definite_print | 34.0% [24.7%, 42.2%] |
| NQ / PIN073_3 | 2022 | 77 observed dates | availability_delayed|stratum=high_only|compatible_reach | 74.0% [65.7%, 83.1%] |
| NQ / PIN073_3 | 2022 | 77 observed dates | availability_delayed|stratum=high_only|definite_print | 27.3% [18.1%, 37.6%] |
| NQ / PIN073_3 | 2022 | 62 observed dates | availability_delayed|stratum=low_only|compatible_reach | 74.2% [65.0%, 85.2%] |
| NQ / PIN073_3 | 2022 | 62 observed dates | availability_delayed|stratum=low_only|definite_print | 41.9% [30.4%, 54.7%] |
| NQ / PIN073_3 | 2022 | 3 observed dates | availability_delayed|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| NQ / PIN073_3 | 2022 | 3 observed dates | availability_delayed|stratum=neither|definite_print | 33.3% [0.0%, 100.0%] |
| NQ / PIN073_3 | 2022 | 244 observed dates | nominal|compatible_reach | 77.0% [72.5%, 82.5%] |
| NQ / PIN073_3 | 2022 | 244 observed dates | nominal|definite_print | 34.4% [28.9%, 40.0%] |
| NQ / PIN073_3 | 2022 | 100 observed dates | nominal|stratum=both|compatible_reach | 80.0% [72.3%, 86.7%] |
| NQ / PIN073_3 | 2022 | 100 observed dates | nominal|stratum=both|definite_print | 34.0% [24.7%, 42.2%] |
| NQ / PIN073_3 | 2022 | 77 observed dates | nominal|stratum=high_only|compatible_reach | 74.0% [65.7%, 83.1%] |
| NQ / PIN073_3 | 2022 | 77 observed dates | nominal|stratum=high_only|definite_print | 27.3% [18.1%, 37.6%] |
| NQ / PIN073_3 | 2022 | 62 observed dates | nominal|stratum=low_only|compatible_reach | 74.2% [65.0%, 85.2%] |
| NQ / PIN073_3 | 2022 | 62 observed dates | nominal|stratum=low_only|definite_print | 41.9% [30.4%, 54.7%] |
| NQ / PIN073_3 | 2022 | 3 observed dates | nominal|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| NQ / PIN073_3 | 2022 | 3 observed dates | nominal|stratum=neither|definite_print | 33.3% [0.0%, 100.0%] |
| NQ / PIN073_3 | 2023 | 235 / 250 | availability_delayed | candidate_available: 229; conditioning_censored: 6; formation_unavailable: 15 |
| NQ / PIN073_3 | 2023 | 235 / 250 | nominal | candidate_available: 229; conditioning_censored: 6; formation_unavailable: 15 |
| NQ / PIN073_3 | 2023 | 229 observed dates | availability_delayed|compatible_reach | 78.6% [72.7%, 83.8%] |
| NQ / PIN073_3 | 2023 | 229 observed dates | availability_delayed|definite_print | 35.4% [29.3%, 41.8%] |
| NQ / PIN073_3 | 2023 | 101 observed dates | availability_delayed|stratum=both|compatible_reach | 85.1% [77.9%, 91.5%] |
| NQ / PIN073_3 | 2023 | 101 observed dates | availability_delayed|stratum=both|definite_print | 40.6% [31.1%, 50.5%] |
| NQ / PIN073_3 | 2023 | 58 observed dates | availability_delayed|stratum=high_only|compatible_reach | 63.8% [50.8%, 75.5%] |
| NQ / PIN073_3 | 2023 | 58 observed dates | availability_delayed|stratum=high_only|definite_print | 24.1% [14.8%, 33.9%] |
| NQ / PIN073_3 | 2023 | 68 observed dates | availability_delayed|stratum=low_only|compatible_reach | 80.9% [72.5%, 89.2%] |
| NQ / PIN073_3 | 2023 | 68 observed dates | availability_delayed|stratum=low_only|definite_print | 38.2% [25.4%, 49.2%] |
| NQ / PIN073_3 | 2023 | 2 observed dates | availability_delayed|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| NQ / PIN073_3 | 2023 | 2 observed dates | availability_delayed|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| NQ / PIN073_3 | 2023 | 234 observed dates | nominal|compatible_reach | 80.8% [75.1%, 86.1%] |
| NQ / PIN073_3 | 2023 | 234 observed dates | nominal|definite_print | 35.9% [30.1%, 42.2%] |
| NQ / PIN073_3 | 2023 | 101 observed dates | nominal|stratum=both|compatible_reach | 87.1% [80.0%, 93.3%] |
| NQ / PIN073_3 | 2023 | 101 observed dates | nominal|stratum=both|definite_print | 40.6% [31.1%, 50.5%] |
| NQ / PIN073_3 | 2023 | 58 observed dates | nominal|stratum=high_only|compatible_reach | 65.5% [52.8%, 76.9%] |
| NQ / PIN073_3 | 2023 | 58 observed dates | nominal|stratum=high_only|definite_print | 24.1% [14.8%, 33.9%] |
| NQ / PIN073_3 | 2023 | 68 observed dates | nominal|stratum=low_only|compatible_reach | 83.8% [75.4%, 91.5%] |
| NQ / PIN073_3 | 2023 | 68 observed dates | nominal|stratum=low_only|definite_print | 41.2% [29.4%, 51.5%] |
| NQ / PIN073_3 | 2023 | 2 observed dates | nominal|stratum=neither|compatible_reach | 100.0% [100.0%, 100.0%] |
| NQ / PIN073_3 | 2023 | 2 observed dates | nominal|stratum=neither|definite_print | 0.0% [0.0%, 0.0%] |
| NQ / PIN073_3 | 2024 | 212 / 252 | availability_delayed | candidate_available: 203; conditioning_censored: 9; formation_unavailable: 40 |
| NQ / PIN073_3 | 2024 | 212 / 252 | nominal | candidate_available: 203; conditioning_censored: 9; formation_unavailable: 40 |
| NQ / PIN073_3 | 2024 | 202 observed dates | availability_delayed|compatible_reach | 72.8% [66.3%, 79.3%] |
| NQ / PIN073_3 | 2024 | 202 observed dates | availability_delayed|definite_print | 30.7% [25.2%, 38.1%] |
| NQ / PIN073_3 | 2024 | 77 observed dates | availability_delayed|stratum=both|compatible_reach | 83.1% [73.8%, 91.2%] |
| NQ / PIN073_3 | 2024 | 77 observed dates | availability_delayed|stratum=both|definite_print | 41.6% [30.8%, 53.9%] |
| NQ / PIN073_3 | 2024 | 65 observed dates | availability_delayed|stratum=high_only|compatible_reach | 67.7% [57.7%, 78.7%] |
| NQ / PIN073_3 | 2024 | 65 observed dates | availability_delayed|stratum=high_only|definite_print | 27.7% [17.6%, 40.0%] |
| NQ / PIN073_3 | 2024 | 60 observed dates | availability_delayed|stratum=low_only|compatible_reach | 65.0% [52.5%, 77.6%] |
| NQ / PIN073_3 | 2024 | 60 observed dates | availability_delayed|stratum=low_only|definite_print | 20.0% [10.5%, 31.7%] |
| NQ / PIN073_3 | 2024 | 210 observed dates | nominal|compatible_reach | 74.3% [68.3%, 80.6%] |
| NQ / PIN073_3 | 2024 | 210 observed dates | nominal|definite_print | 31.0% [25.5%, 38.5%] |
| NQ / PIN073_3 | 2024 | 77 observed dates | nominal|stratum=both|compatible_reach | 84.4% [75.6%, 91.7%] |
| NQ / PIN073_3 | 2024 | 77 observed dates | nominal|stratum=both|definite_print | 41.6% [30.8%, 53.9%] |
| NQ / PIN073_3 | 2024 | 65 observed dates | nominal|stratum=high_only|compatible_reach | 67.7% [57.7%, 78.7%] |
| NQ / PIN073_3 | 2024 | 65 observed dates | nominal|stratum=high_only|definite_print | 27.7% [17.6%, 40.0%] |
| NQ / PIN073_3 | 2024 | 60 observed dates | nominal|stratum=low_only|compatible_reach | 65.0% [52.5%, 77.6%] |
| NQ / PIN073_3 | 2024 | 60 observed dates | nominal|stratum=low_only|definite_print | 20.0% [10.5%, 31.7%] |
| NQ / PIN073_4 | 2020 | 249 / 253 | availability_delayed | candidate_available: 249; formation_unavailable: 4 |
| NQ / PIN073_4 | 2020 | 249 / 253 | nominal | candidate_available: 249; formation_unavailable: 4 |
| NQ / PIN073_4 | 2020 | 244 observed dates | availability_delayed|compatible_reach | 63.1% [57.5%, 67.5%] |
| NQ / PIN073_4 | 2020 | 244 observed dates | availability_delayed|definite_print | 19.7% [14.6%, 25.0%] |
| NQ / PIN073_4 | 2020 | 10 observed dates | availability_delayed|stratum=both|compatible_reach | 50.0% [14.3%, 83.3%] |
| NQ / PIN073_4 | 2020 | 10 observed dates | availability_delayed|stratum=both|definite_print | 20.0% [0.0%, 50.1%] |
| NQ / PIN073_4 | 2020 | 114 observed dates | availability_delayed|stratum=high_only|compatible_reach | 62.3% [53.6%, 69.5%] |
| NQ / PIN073_4 | 2020 | 114 observed dates | availability_delayed|stratum=high_only|definite_print | 18.4% [11.4%, 25.7%] |
| NQ / PIN073_4 | 2020 | 78 observed dates | availability_delayed|stratum=low_only|compatible_reach | 62.8% [50.0%, 72.8%] |
| NQ / PIN073_4 | 2020 | 78 observed dates | availability_delayed|stratum=low_only|definite_print | 23.1% [13.3%, 34.1%] |
| NQ / PIN073_4 | 2020 | 42 observed dates | availability_delayed|stratum=neither|compatible_reach | 69.0% [56.8%, 81.8%] |
| NQ / PIN073_4 | 2020 | 42 observed dates | availability_delayed|stratum=neither|definite_print | 16.7% [7.1%, 27.9%] |
| NQ / PIN073_4 | 2020 | 244 observed dates | nominal|compatible_reach | 64.3% [58.5%, 69.0%] |
| NQ / PIN073_4 | 2020 | 244 observed dates | nominal|definite_print | 19.7% [14.6%, 25.0%] |
| NQ / PIN073_4 | 2020 | 10 observed dates | nominal|stratum=both|compatible_reach | 60.0% [25.0%, 92.3%] |
| NQ / PIN073_4 | 2020 | 10 observed dates | nominal|stratum=both|definite_print | 20.0% [0.0%, 50.1%] |
| NQ / PIN073_4 | 2020 | 114 observed dates | nominal|stratum=high_only|compatible_reach | 62.3% [53.6%, 69.5%] |
| NQ / PIN073_4 | 2020 | 114 observed dates | nominal|stratum=high_only|definite_print | 18.4% [11.4%, 25.7%] |
| NQ / PIN073_4 | 2020 | 78 observed dates | nominal|stratum=low_only|compatible_reach | 64.1% [51.3%, 74.3%] |
| NQ / PIN073_4 | 2020 | 78 observed dates | nominal|stratum=low_only|definite_print | 23.1% [13.3%, 34.1%] |
| NQ / PIN073_4 | 2020 | 42 observed dates | nominal|stratum=neither|compatible_reach | 71.4% [59.1%, 83.9%] |
| NQ / PIN073_4 | 2020 | 42 observed dates | nominal|stratum=neither|definite_print | 16.7% [7.1%, 27.9%] |
| NQ / PIN073_4 | 2021 | 248 / 252 | availability_delayed | candidate_available: 248; formation_unavailable: 4 |
| NQ / PIN073_4 | 2021 | 248 / 252 | nominal | candidate_available: 248; formation_unavailable: 4 |
| NQ / PIN073_4 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 64.4% [57.9%, 70.2%] |
| NQ / PIN073_4 | 2021 | 247 observed dates | availability_delayed|definite_print | 27.9% [22.4%, 33.2%] |
| NQ / PIN073_4 | 2021 | 17 observed dates | availability_delayed|stratum=both|compatible_reach | 64.7% [37.5%, 89.5%] |
| NQ / PIN073_4 | 2021 | 17 observed dates | availability_delayed|stratum=both|definite_print | 29.4% [6.7%, 53.9%] |
| NQ / PIN073_4 | 2021 | 111 observed dates | availability_delayed|stratum=high_only|compatible_reach | 52.3% [42.5%, 61.5%] |
| NQ / PIN073_4 | 2021 | 111 observed dates | availability_delayed|stratum=high_only|definite_print | 23.4% [15.8%, 32.0%] |
| NQ / PIN073_4 | 2021 | 87 observed dates | availability_delayed|stratum=low_only|compatible_reach | 75.9% [66.7%, 84.7%] |
| NQ / PIN073_4 | 2021 | 87 observed dates | availability_delayed|stratum=low_only|definite_print | 29.9% [20.0%, 40.4%] |
| NQ / PIN073_4 | 2021 | 32 observed dates | availability_delayed|stratum=neither|compatible_reach | 75.0% [56.0%, 88.5%] |
| NQ / PIN073_4 | 2021 | 32 observed dates | availability_delayed|stratum=neither|definite_print | 37.5% [19.4%, 52.6%] |
| NQ / PIN073_4 | 2021 | 247 observed dates | nominal|compatible_reach | 64.4% [57.9%, 70.2%] |
| NQ / PIN073_4 | 2021 | 247 observed dates | nominal|definite_print | 27.9% [22.4%, 33.2%] |
| NQ / PIN073_4 | 2021 | 17 observed dates | nominal|stratum=both|compatible_reach | 64.7% [37.5%, 89.5%] |
| NQ / PIN073_4 | 2021 | 17 observed dates | nominal|stratum=both|definite_print | 29.4% [6.7%, 53.9%] |
| NQ / PIN073_4 | 2021 | 111 observed dates | nominal|stratum=high_only|compatible_reach | 52.3% [42.5%, 61.5%] |
| NQ / PIN073_4 | 2021 | 111 observed dates | nominal|stratum=high_only|definite_print | 23.4% [15.8%, 32.0%] |
| NQ / PIN073_4 | 2021 | 87 observed dates | nominal|stratum=low_only|compatible_reach | 75.9% [66.7%, 84.7%] |
| NQ / PIN073_4 | 2021 | 87 observed dates | nominal|stratum=low_only|definite_print | 29.9% [20.0%, 40.4%] |
| NQ / PIN073_4 | 2021 | 32 observed dates | nominal|stratum=neither|compatible_reach | 75.0% [56.0%, 88.5%] |
| NQ / PIN073_4 | 2021 | 32 observed dates | nominal|stratum=neither|definite_print | 37.5% [19.4%, 52.6%] |
| NQ / PIN073_4 | 2022 | 247 / 251 | availability_delayed | candidate_available: 247; formation_unavailable: 4 |
| NQ / PIN073_4 | 2022 | 247 / 251 | nominal | candidate_available: 247; formation_unavailable: 4 |
| NQ / PIN073_4 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 69.1% [63.2%, 74.2%] |
| NQ / PIN073_4 | 2022 | 246 observed dates | availability_delayed|definite_print | 21.1% [16.5%, 25.2%] |
| NQ / PIN073_4 | 2022 | 19 observed dates | availability_delayed|stratum=both|compatible_reach | 84.2% [68.0%, 100.0%] |
| NQ / PIN073_4 | 2022 | 19 observed dates | availability_delayed|stratum=both|definite_print | 31.6% [13.6%, 52.4%] |
| NQ / PIN073_4 | 2022 | 108 observed dates | availability_delayed|stratum=high_only|compatible_reach | 72.2% [62.9%, 80.0%] |
| NQ / PIN073_4 | 2022 | 108 observed dates | availability_delayed|stratum=high_only|definite_print | 15.7% [9.0%, 22.7%] |
| NQ / PIN073_4 | 2022 | 81 observed dates | availability_delayed|stratum=low_only|compatible_reach | 54.3% [43.8%, 64.0%] |
| NQ / PIN073_4 | 2022 | 81 observed dates | availability_delayed|stratum=low_only|definite_print | 19.8% [11.5%, 26.6%] |
| NQ / PIN073_4 | 2022 | 38 observed dates | availability_delayed|stratum=neither|compatible_reach | 84.2% [71.9%, 94.9%] |
| NQ / PIN073_4 | 2022 | 38 observed dates | availability_delayed|stratum=neither|definite_print | 34.2% [19.4%, 51.4%] |
| NQ / PIN073_4 | 2022 | 246 observed dates | nominal|compatible_reach | 70.3% [65.2%, 74.9%] |
| NQ / PIN073_4 | 2022 | 246 observed dates | nominal|definite_print | 21.1% [16.5%, 25.2%] |
| NQ / PIN073_4 | 2022 | 19 observed dates | nominal|stratum=both|compatible_reach | 84.2% [68.0%, 100.0%] |
| NQ / PIN073_4 | 2022 | 19 observed dates | nominal|stratum=both|definite_print | 31.6% [13.6%, 52.4%] |
| NQ / PIN073_4 | 2022 | 108 observed dates | nominal|stratum=high_only|compatible_reach | 74.1% [65.1%, 81.7%] |
| NQ / PIN073_4 | 2022 | 108 observed dates | nominal|stratum=high_only|definite_print | 15.7% [9.0%, 22.7%] |
| NQ / PIN073_4 | 2022 | 81 observed dates | nominal|stratum=low_only|compatible_reach | 55.6% [44.7%, 65.0%] |
| NQ / PIN073_4 | 2022 | 81 observed dates | nominal|stratum=low_only|definite_print | 19.8% [11.5%, 26.6%] |
| NQ / PIN073_4 | 2022 | 38 observed dates | nominal|stratum=neither|compatible_reach | 84.2% [71.9%, 94.9%] |
| NQ / PIN073_4 | 2022 | 38 observed dates | nominal|stratum=neither|definite_print | 34.2% [19.4%, 51.4%] |
| NQ / PIN073_4 | 2023 | 246 / 250 | availability_delayed | candidate_available: 246; formation_unavailable: 4 |
| NQ / PIN073_4 | 2023 | 246 / 250 | nominal | candidate_available: 246; formation_unavailable: 4 |
| NQ / PIN073_4 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 72.1% [65.8%, 77.6%] |
| NQ / PIN073_4 | 2023 | 244 observed dates | availability_delayed|definite_print | 25.0% [19.9%, 30.0%] |
| NQ / PIN073_4 | 2023 | 27 observed dates | availability_delayed|stratum=both|compatible_reach | 81.5% [66.7%, 94.4%] |
| NQ / PIN073_4 | 2023 | 27 observed dates | availability_delayed|stratum=both|definite_print | 25.9% [11.1%, 40.6%] |
| NQ / PIN073_4 | 2023 | 113 observed dates | availability_delayed|stratum=high_only|compatible_reach | 61.9% [52.7%, 70.8%] |
| NQ / PIN073_4 | 2023 | 113 observed dates | availability_delayed|stratum=high_only|definite_print | 16.8% [10.1%, 23.5%] |
| NQ / PIN073_4 | 2023 | 85 observed dates | availability_delayed|stratum=low_only|compatible_reach | 78.8% [69.6%, 87.0%] |
| NQ / PIN073_4 | 2023 | 85 observed dates | availability_delayed|stratum=low_only|definite_print | 34.1% [25.3%, 45.6%] |
| NQ / PIN073_4 | 2023 | 19 observed dates | availability_delayed|stratum=neither|compatible_reach | 89.5% [71.4%, 100.0%] |
| NQ / PIN073_4 | 2023 | 19 observed dates | availability_delayed|stratum=neither|definite_print | 31.6% [11.1%, 52.9%] |
| NQ / PIN073_4 | 2023 | 244 observed dates | nominal|compatible_reach | 72.5% [66.1%, 78.1%] |
| NQ / PIN073_4 | 2023 | 244 observed dates | nominal|definite_print | 25.0% [19.9%, 30.0%] |
| NQ / PIN073_4 | 2023 | 27 observed dates | nominal|stratum=both|compatible_reach | 81.5% [66.7%, 94.4%] |
| NQ / PIN073_4 | 2023 | 27 observed dates | nominal|stratum=both|definite_print | 25.9% [11.1%, 40.6%] |
| NQ / PIN073_4 | 2023 | 113 observed dates | nominal|stratum=high_only|compatible_reach | 62.8% [53.5%, 71.6%] |
| NQ / PIN073_4 | 2023 | 113 observed dates | nominal|stratum=high_only|definite_print | 16.8% [10.1%, 23.5%] |
| NQ / PIN073_4 | 2023 | 85 observed dates | nominal|stratum=low_only|compatible_reach | 78.8% [69.6%, 87.0%] |
| NQ / PIN073_4 | 2023 | 85 observed dates | nominal|stratum=low_only|definite_print | 34.1% [25.3%, 45.6%] |
| NQ / PIN073_4 | 2023 | 19 observed dates | nominal|stratum=neither|compatible_reach | 89.5% [71.4%, 100.0%] |
| NQ / PIN073_4 | 2023 | 19 observed dates | nominal|stratum=neither|definite_print | 31.6% [11.1%, 52.9%] |
| NQ / PIN073_4 | 2024 | 225 / 252 | availability_delayed | candidate_available: 225; formation_unavailable: 27 |
| NQ / PIN073_4 | 2024 | 225 / 252 | nominal | candidate_available: 225; formation_unavailable: 27 |
| NQ / PIN073_4 | 2024 | 223 observed dates | availability_delayed|compatible_reach | 69.1% [62.7%, 75.6%] |
| NQ / PIN073_4 | 2024 | 223 observed dates | availability_delayed|definite_print | 26.5% [20.0%, 31.3%] |
| NQ / PIN073_4 | 2024 | 18 observed dates | availability_delayed|stratum=both|compatible_reach | 88.9% [71.4%, 100.0%] |
| NQ / PIN073_4 | 2024 | 18 observed dates | availability_delayed|stratum=both|definite_print | 38.9% [17.6%, 60.0%] |
| NQ / PIN073_4 | 2024 | 96 observed dates | availability_delayed|stratum=high_only|compatible_reach | 60.4% [49.5%, 70.5%] |
| NQ / PIN073_4 | 2024 | 96 observed dates | availability_delayed|stratum=high_only|definite_print | 27.1% [17.8%, 35.4%] |
| NQ / PIN073_4 | 2024 | 82 observed dates | availability_delayed|stratum=low_only|compatible_reach | 68.3% [58.3%, 77.9%] |
| NQ / PIN073_4 | 2024 | 82 observed dates | availability_delayed|stratum=low_only|definite_print | 18.3% [8.6%, 26.6%] |
| NQ / PIN073_4 | 2024 | 27 observed dates | availability_delayed|stratum=neither|compatible_reach | 88.9% [76.0%, 100.0%] |
| NQ / PIN073_4 | 2024 | 27 observed dates | availability_delayed|stratum=neither|definite_print | 40.7% [24.0%, 58.6%] |
| NQ / PIN073_4 | 2024 | 223 observed dates | nominal|compatible_reach | 69.5% [63.2%, 76.1%] |
| NQ / PIN073_4 | 2024 | 223 observed dates | nominal|definite_print | 26.9% [20.5%, 31.8%] |
| NQ / PIN073_4 | 2024 | 18 observed dates | nominal|stratum=both|compatible_reach | 88.9% [71.4%, 100.0%] |
| NQ / PIN073_4 | 2024 | 18 observed dates | nominal|stratum=both|definite_print | 38.9% [17.6%, 60.0%] |
| NQ / PIN073_4 | 2024 | 96 observed dates | nominal|stratum=high_only|compatible_reach | 61.5% [51.0%, 71.4%] |
| NQ / PIN073_4 | 2024 | 96 observed dates | nominal|stratum=high_only|definite_print | 28.1% [18.6%, 36.6%] |
| NQ / PIN073_4 | 2024 | 82 observed dates | nominal|stratum=low_only|compatible_reach | 68.3% [58.3%, 77.9%] |
| NQ / PIN073_4 | 2024 | 82 observed dates | nominal|stratum=low_only|definite_print | 18.3% [8.6%, 26.6%] |
| NQ / PIN073_4 | 2024 | 27 observed dates | nominal|stratum=neither|compatible_reach | 88.9% [76.0%, 100.0%] |
| NQ / PIN073_4 | 2024 | 27 observed dates | nominal|stratum=neither|definite_print | 40.7% [24.0%, 58.6%] |
| NQ / PIN073_5 | 2020 | 247 / 253 | availability_delayed | candidate_available: 245; conditioning_censored: 2; formation_unavailable: 6 |
| NQ / PIN073_5 | 2020 | 247 / 253 | nominal | candidate_available: 245; conditioning_censored: 2; formation_unavailable: 6 |
| NQ / PIN073_5 | 2020 | 245 observed dates | availability_delayed|compatible_reach | 66.1% [60.8%, 71.8%] |
| NQ / PIN073_5 | 2020 | 245 observed dates | availability_delayed|definite_print | 18.0% [13.1%, 22.2%] |
| NQ / PIN073_5 | 2020 | 21 observed dates | availability_delayed|stratum=both|compatible_reach | 66.7% [44.4%, 86.7%] |
| NQ / PIN073_5 | 2020 | 21 observed dates | availability_delayed|stratum=both|definite_print | 9.5% [0.0%, 23.1%] |
| NQ / PIN073_5 | 2020 | 114 observed dates | availability_delayed|stratum=high_only|compatible_reach | 60.5% [53.0%, 68.8%] |
| NQ / PIN073_5 | 2020 | 114 observed dates | availability_delayed|stratum=high_only|definite_print | 20.2% [12.9%, 27.6%] |
| NQ / PIN073_5 | 2020 | 80 observed dates | availability_delayed|stratum=low_only|compatible_reach | 66.2% [56.0%, 75.0%] |
| NQ / PIN073_5 | 2020 | 80 observed dates | availability_delayed|stratum=low_only|definite_print | 15.0% [7.3%, 22.6%] |
| NQ / PIN073_5 | 2020 | 30 observed dates | availability_delayed|stratum=neither|compatible_reach | 86.7% [73.1%, 96.8%] |
| NQ / PIN073_5 | 2020 | 30 observed dates | availability_delayed|stratum=neither|definite_print | 23.3% [8.0%, 38.5%] |
| NQ / PIN073_5 | 2020 | 247 observed dates | nominal|compatible_reach | 68.0% [63.0%, 73.2%] |
| NQ / PIN073_5 | 2020 | 247 observed dates | nominal|definite_print | 18.6% [13.7%, 23.2%] |
| NQ / PIN073_5 | 2020 | 21 observed dates | nominal|stratum=both|compatible_reach | 71.4% [52.9%, 88.9%] |
| NQ / PIN073_5 | 2020 | 21 observed dates | nominal|stratum=both|definite_print | 14.3% [0.0%, 29.4%] |
| NQ / PIN073_5 | 2020 | 114 observed dates | nominal|stratum=high_only|compatible_reach | 62.3% [55.2%, 70.8%] |
| NQ / PIN073_5 | 2020 | 114 observed dates | nominal|stratum=high_only|definite_print | 20.2% [12.9%, 27.6%] |
| NQ / PIN073_5 | 2020 | 80 observed dates | nominal|stratum=low_only|compatible_reach | 67.5% [57.5%, 75.6%] |
| NQ / PIN073_5 | 2020 | 80 observed dates | nominal|stratum=low_only|definite_print | 15.0% [7.3%, 22.6%] |
| NQ / PIN073_5 | 2020 | 30 observed dates | nominal|stratum=neither|compatible_reach | 86.7% [73.1%, 96.8%] |
| NQ / PIN073_5 | 2020 | 30 observed dates | nominal|stratum=neither|definite_print | 23.3% [8.0%, 38.5%] |
| NQ / PIN073_5 | 2021 | 247 / 252 | availability_delayed | candidate_available: 247; formation_unavailable: 5 |
| NQ / PIN073_5 | 2021 | 247 / 252 | nominal | candidate_available: 247; formation_unavailable: 5 |
| NQ / PIN073_5 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 62.3% [56.6%, 67.6%] |
| NQ / PIN073_5 | 2021 | 247 observed dates | availability_delayed|definite_print | 19.4% [14.5%, 24.9%] |
| NQ / PIN073_5 | 2021 | 18 observed dates | availability_delayed|stratum=both|compatible_reach | 55.6% [30.8%, 80.0%] |
| NQ / PIN073_5 | 2021 | 18 observed dates | availability_delayed|stratum=both|definite_print | 22.2% [5.6%, 43.8%] |
| NQ / PIN073_5 | 2021 | 124 observed dates | availability_delayed|stratum=high_only|compatible_reach | 58.9% [50.0%, 67.5%] |
| NQ / PIN073_5 | 2021 | 124 observed dates | availability_delayed|stratum=high_only|definite_print | 18.5% [11.9%, 25.6%] |
| NQ / PIN073_5 | 2021 | 73 observed dates | availability_delayed|stratum=low_only|compatible_reach | 63.0% [52.6%, 72.9%] |
| NQ / PIN073_5 | 2021 | 73 observed dates | availability_delayed|stratum=low_only|definite_print | 17.8% [9.0%, 28.2%] |
| NQ / PIN073_5 | 2021 | 32 observed dates | availability_delayed|stratum=neither|compatible_reach | 78.1% [62.5%, 90.3%] |
| NQ / PIN073_5 | 2021 | 32 observed dates | availability_delayed|stratum=neither|definite_print | 25.0% [11.4%, 42.4%] |
| NQ / PIN073_5 | 2021 | 247 observed dates | nominal|compatible_reach | 62.3% [56.6%, 67.6%] |
| NQ / PIN073_5 | 2021 | 247 observed dates | nominal|definite_print | 20.2% [15.3%, 25.8%] |
| NQ / PIN073_5 | 2021 | 18 observed dates | nominal|stratum=both|compatible_reach | 55.6% [30.8%, 80.0%] |
| NQ / PIN073_5 | 2021 | 18 observed dates | nominal|stratum=both|definite_print | 22.2% [5.6%, 43.8%] |
| NQ / PIN073_5 | 2021 | 124 observed dates | nominal|stratum=high_only|compatible_reach | 58.9% [50.0%, 67.5%] |
| NQ / PIN073_5 | 2021 | 124 observed dates | nominal|stratum=high_only|definite_print | 18.5% [11.9%, 25.6%] |
| NQ / PIN073_5 | 2021 | 73 observed dates | nominal|stratum=low_only|compatible_reach | 63.0% [52.6%, 72.9%] |
| NQ / PIN073_5 | 2021 | 73 observed dates | nominal|stratum=low_only|definite_print | 19.2% [9.6%, 29.8%] |
| NQ / PIN073_5 | 2021 | 32 observed dates | nominal|stratum=neither|compatible_reach | 78.1% [62.5%, 90.3%] |
| NQ / PIN073_5 | 2021 | 32 observed dates | nominal|stratum=neither|definite_print | 28.1% [14.3%, 46.4%] |
| NQ / PIN073_5 | 2022 | 246 / 251 | availability_delayed | candidate_available: 246; formation_unavailable: 5 |
| NQ / PIN073_5 | 2022 | 246 / 251 | nominal | candidate_available: 246; formation_unavailable: 5 |
| NQ / PIN073_5 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 56.9% [52.2%, 62.2%] |
| NQ / PIN073_5 | 2022 | 246 observed dates | availability_delayed|definite_print | 13.8% [9.3%, 18.4%] |
| NQ / PIN073_5 | 2022 | 17 observed dates | availability_delayed|stratum=both|compatible_reach | 70.6% [52.6%, 88.3%] |
| NQ / PIN073_5 | 2022 | 17 observed dates | availability_delayed|stratum=both|definite_print | 11.8% [0.0%, 26.3%] |
| NQ / PIN073_5 | 2022 | 107 observed dates | availability_delayed|stratum=high_only|compatible_reach | 52.3% [44.2%, 61.4%] |
| NQ / PIN073_5 | 2022 | 107 observed dates | availability_delayed|stratum=high_only|definite_print | 10.3% [5.0%, 16.7%] |
| NQ / PIN073_5 | 2022 | 96 observed dates | availability_delayed|stratum=low_only|compatible_reach | 55.2% [45.3%, 64.9%] |
| NQ / PIN073_5 | 2022 | 96 observed dates | availability_delayed|stratum=low_only|definite_print | 13.5% [6.7%, 20.6%] |
| NQ / PIN073_5 | 2022 | 26 observed dates | availability_delayed|stratum=neither|compatible_reach | 73.1% [55.9%, 90.0%] |
| NQ / PIN073_5 | 2022 | 26 observed dates | availability_delayed|stratum=neither|definite_print | 30.8% [11.1%, 48.3%] |
| NQ / PIN073_5 | 2022 | 246 observed dates | nominal|compatible_reach | 58.1% [53.4%, 63.7%] |
| NQ / PIN073_5 | 2022 | 246 observed dates | nominal|definite_print | 14.6% [9.8%, 19.4%] |
| NQ / PIN073_5 | 2022 | 17 observed dates | nominal|stratum=both|compatible_reach | 70.6% [52.6%, 88.3%] |
| NQ / PIN073_5 | 2022 | 17 observed dates | nominal|stratum=both|definite_print | 11.8% [0.0%, 26.3%] |
| NQ / PIN073_5 | 2022 | 107 observed dates | nominal|stratum=high_only|compatible_reach | 54.2% [45.9%, 63.4%] |
| NQ / PIN073_5 | 2022 | 107 observed dates | nominal|stratum=high_only|definite_print | 10.3% [5.0%, 16.7%] |
| NQ / PIN073_5 | 2022 | 96 observed dates | nominal|stratum=low_only|compatible_reach | 55.2% [45.3%, 64.9%] |
| NQ / PIN073_5 | 2022 | 96 observed dates | nominal|stratum=low_only|definite_print | 13.5% [6.7%, 20.6%] |
| NQ / PIN073_5 | 2022 | 26 observed dates | nominal|stratum=neither|compatible_reach | 76.9% [60.0%, 94.5%] |
| NQ / PIN073_5 | 2022 | 26 observed dates | nominal|stratum=neither|definite_print | 38.5% [19.0%, 58.6%] |
| NQ / PIN073_5 | 2023 | 244 / 250 | availability_delayed | candidate_available: 244; formation_unavailable: 6 |
| NQ / PIN073_5 | 2023 | 244 / 250 | nominal | candidate_available: 244; formation_unavailable: 6 |
| NQ / PIN073_5 | 2023 | 244 observed dates | availability_delayed|compatible_reach | 52.9% [46.6%, 58.6%] |
| NQ / PIN073_5 | 2023 | 244 observed dates | availability_delayed|definite_print | 18.9% [14.7%, 23.8%] |
| NQ / PIN073_5 | 2023 | 32 observed dates | availability_delayed|stratum=both|compatible_reach | 78.1% [66.7%, 93.3%] |
| NQ / PIN073_5 | 2023 | 32 observed dates | availability_delayed|stratum=both|definite_print | 15.6% [5.7%, 32.1%] |
| NQ / PIN073_5 | 2023 | 112 observed dates | availability_delayed|stratum=high_only|compatible_reach | 50.0% [39.1%, 59.0%] |
| NQ / PIN073_5 | 2023 | 112 observed dates | availability_delayed|stratum=high_only|definite_print | 17.9% [11.2%, 25.2%] |
| NQ / PIN073_5 | 2023 | 79 observed dates | availability_delayed|stratum=low_only|compatible_reach | 43.0% [32.3%, 53.8%] |
| NQ / PIN073_5 | 2023 | 79 observed dates | availability_delayed|stratum=low_only|definite_print | 16.5% [8.1%, 25.5%] |
| NQ / PIN073_5 | 2023 | 21 observed dates | availability_delayed|stratum=neither|compatible_reach | 66.7% [45.8%, 87.5%] |
| NQ / PIN073_5 | 2023 | 21 observed dates | availability_delayed|stratum=neither|definite_print | 38.1% [17.6%, 61.1%] |
| NQ / PIN073_5 | 2023 | 244 observed dates | nominal|compatible_reach | 53.7% [47.1%, 59.4%] |
| NQ / PIN073_5 | 2023 | 244 observed dates | nominal|definite_print | 18.9% [14.7%, 23.8%] |
| NQ / PIN073_5 | 2023 | 32 observed dates | nominal|stratum=both|compatible_reach | 78.1% [66.7%, 93.3%] |
| NQ / PIN073_5 | 2023 | 32 observed dates | nominal|stratum=both|definite_print | 15.6% [5.7%, 32.1%] |
| NQ / PIN073_5 | 2023 | 112 observed dates | nominal|stratum=high_only|compatible_reach | 50.9% [39.8%, 60.0%] |
| NQ / PIN073_5 | 2023 | 112 observed dates | nominal|stratum=high_only|definite_print | 17.9% [11.2%, 25.2%] |
| NQ / PIN073_5 | 2023 | 79 observed dates | nominal|stratum=low_only|compatible_reach | 43.0% [32.3%, 53.8%] |
| NQ / PIN073_5 | 2023 | 79 observed dates | nominal|stratum=low_only|definite_print | 16.5% [8.1%, 25.5%] |
| NQ / PIN073_5 | 2023 | 21 observed dates | nominal|stratum=neither|compatible_reach | 71.4% [52.2%, 90.9%] |
| NQ / PIN073_5 | 2023 | 21 observed dates | nominal|stratum=neither|definite_print | 38.1% [17.6%, 61.1%] |
| NQ / PIN073_5 | 2024 | 223 / 252 | availability_delayed | candidate_available: 223; formation_unavailable: 29 |
| NQ / PIN073_5 | 2024 | 223 / 252 | nominal | candidate_available: 223; formation_unavailable: 29 |
| NQ / PIN073_5 | 2024 | 223 observed dates | availability_delayed|compatible_reach | 68.2% [61.4%, 73.8%] |
| NQ / PIN073_5 | 2024 | 223 observed dates | availability_delayed|definite_print | 15.7% [11.2%, 21.1%] |
| NQ / PIN073_5 | 2024 | 27 observed dates | availability_delayed|stratum=both|compatible_reach | 77.8% [58.8%, 92.9%] |
| NQ / PIN073_5 | 2024 | 27 observed dates | availability_delayed|stratum=both|definite_print | 14.8% [3.7%, 31.8%] |
| NQ / PIN073_5 | 2024 | 85 observed dates | availability_delayed|stratum=high_only|compatible_reach | 52.9% [43.2%, 60.9%] |
| NQ / PIN073_5 | 2024 | 85 observed dates | availability_delayed|stratum=high_only|definite_print | 9.4% [3.6%, 16.3%] |
| NQ / PIN073_5 | 2024 | 74 observed dates | availability_delayed|stratum=low_only|compatible_reach | 68.9% [58.2%, 78.2%] |
| NQ / PIN073_5 | 2024 | 74 observed dates | availability_delayed|stratum=low_only|definite_print | 17.6% [9.4%, 25.0%] |
| NQ / PIN073_5 | 2024 | 37 observed dates | availability_delayed|stratum=neither|compatible_reach | 94.6% [85.3%, 100.0%] |
| NQ / PIN073_5 | 2024 | 37 observed dates | availability_delayed|stratum=neither|definite_print | 27.0% [11.8%, 44.2%] |
| NQ / PIN073_5 | 2024 | 223 observed dates | nominal|compatible_reach | 69.1% [62.4%, 74.5%] |
| NQ / PIN073_5 | 2024 | 223 observed dates | nominal|definite_print | 15.7% [11.2%, 21.1%] |
| NQ / PIN073_5 | 2024 | 27 observed dates | nominal|stratum=both|compatible_reach | 77.8% [58.8%, 92.9%] |
| NQ / PIN073_5 | 2024 | 27 observed dates | nominal|stratum=both|definite_print | 14.8% [3.7%, 31.8%] |
| NQ / PIN073_5 | 2024 | 85 observed dates | nominal|stratum=high_only|compatible_reach | 54.1% [44.3%, 62.1%] |
| NQ / PIN073_5 | 2024 | 85 observed dates | nominal|stratum=high_only|definite_print | 9.4% [3.6%, 16.3%] |
| NQ / PIN073_5 | 2024 | 74 observed dates | nominal|stratum=low_only|compatible_reach | 70.3% [59.8%, 79.3%] |
| NQ / PIN073_5 | 2024 | 74 observed dates | nominal|stratum=low_only|definite_print | 17.6% [9.4%, 25.0%] |
| NQ / PIN073_5 | 2024 | 37 observed dates | nominal|stratum=neither|compatible_reach | 94.6% [85.3%, 100.0%] |
| NQ / PIN073_5 | 2024 | 37 observed dates | nominal|stratum=neither|definite_print | 27.0% [11.8%, 44.2%] |
| NQ / PIN074_ref_00 | 2020 | 248 / 253 | availability_delayed | candidate_available: 248; forecast_open_unavailable: 2; reference_open_unavailable: 3 |
| NQ / PIN074_ref_00 | 2020 | 248 / 253 | nominal | candidate_available: 248; forecast_open_unavailable: 2; reference_open_unavailable: 3 |
| NQ / PIN074_ref_00 | 2020 | 239 observed dates | availability_delayed|compatible_reach | 86.2% [81.4%, 90.3%] |
| NQ / PIN074_ref_00 | 2020 | 239 observed dates | availability_delayed|definite_print | 34.3% [28.1%, 40.4%] |
| NQ / PIN074_ref_00 | 2020 | 239 observed dates | nominal|compatible_reach | 87.0% [82.6%, 91.1%] |
| NQ / PIN074_ref_00 | 2020 | 239 observed dates | nominal|definite_print | 34.3% [28.1%, 40.4%] |
| NQ / PIN074_ref_00 | 2021 | 250 / 252 | availability_delayed | candidate_available: 250; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN074_ref_00 | 2021 | 250 / 252 | nominal | candidate_available: 250; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN074_ref_00 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 86.6% [82.6%, 90.3%] |
| NQ / PIN074_ref_00 | 2021 | 247 observed dates | availability_delayed|definite_print | 29.1% [23.5%, 35.2%] |
| NQ / PIN074_ref_00 | 2021 | 247 observed dates | nominal|compatible_reach | 87.0% [83.0%, 90.7%] |
| NQ / PIN074_ref_00 | 2021 | 247 observed dates | nominal|definite_print | 29.6% [24.1%, 35.6%] |
| NQ / PIN074_ref_00 | 2022 | 251 / 251 | availability_delayed | candidate_available: 251 |
| NQ / PIN074_ref_00 | 2022 | 251 / 251 | nominal | candidate_available: 251 |
| NQ / PIN074_ref_00 | 2022 | 245 observed dates | availability_delayed|compatible_reach | 86.5% [82.6%, 90.7%] |
| NQ / PIN074_ref_00 | 2022 | 245 observed dates | availability_delayed|definite_print | 28.2% [21.9%, 34.7%] |
| NQ / PIN074_ref_00 | 2022 | 245 observed dates | nominal|compatible_reach | 86.5% [82.6%, 90.7%] |
| NQ / PIN074_ref_00 | 2022 | 245 observed dates | nominal|definite_print | 28.6% [22.2%, 35.2%] |
| NQ / PIN074_ref_00 | 2023 | 248 / 250 | availability_delayed | candidate_available: 248; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN074_ref_00 | 2023 | 248 / 250 | nominal | candidate_available: 248; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN074_ref_00 | 2023 | 242 observed dates | availability_delayed|compatible_reach | 85.5% [80.7%, 89.6%] |
| NQ / PIN074_ref_00 | 2023 | 242 observed dates | availability_delayed|definite_print | 34.7% [27.9%, 41.7%] |
| NQ / PIN074_ref_00 | 2023 | 242 observed dates | nominal|compatible_reach | 85.5% [80.7%, 89.6%] |
| NQ / PIN074_ref_00 | 2023 | 242 observed dates | nominal|definite_print | 35.1% [28.3%, 41.9%] |
| NQ / PIN074_ref_00 | 2024 | 226 / 252 | availability_delayed | candidate_available: 226; reference_open_unavailable: 26 |
| NQ / PIN074_ref_00 | 2024 | 226 / 252 | nominal | candidate_available: 226; reference_open_unavailable: 26 |
| NQ / PIN074_ref_00 | 2024 | 223 observed dates | availability_delayed|compatible_reach | 85.2% [81.7%, 89.9%] |
| NQ / PIN074_ref_00 | 2024 | 223 observed dates | availability_delayed|definite_print | 29.6% [24.4%, 36.1%] |
| NQ / PIN074_ref_00 | 2024 | 223 observed dates | nominal|compatible_reach | 85.2% [81.7%, 89.9%] |
| NQ / PIN074_ref_00 | 2024 | 223 observed dates | nominal|definite_print | 29.6% [24.4%, 36.1%] |
| NQ / PIN074_ref_01 | 2020 | 247 / 253 | availability_delayed | candidate_available: 247; forecast_open_unavailable: 2; reference_open_unavailable: 4 |
| NQ / PIN074_ref_01 | 2020 | 247 / 253 | nominal | candidate_available: 247; forecast_open_unavailable: 2; reference_open_unavailable: 4 |
| NQ / PIN074_ref_01 | 2020 | 240 observed dates | availability_delayed|compatible_reach | 89.2% [84.5%, 93.0%] |
| NQ / PIN074_ref_01 | 2020 | 240 observed dates | availability_delayed|definite_print | 35.4% [29.1%, 41.4%] |
| NQ / PIN074_ref_01 | 2020 | 240 observed dates | nominal|compatible_reach | 89.2% [84.5%, 93.0%] |
| NQ / PIN074_ref_01 | 2020 | 240 observed dates | nominal|definite_print | 35.4% [29.1%, 41.4%] |
| NQ / PIN074_ref_01 | 2021 | 249 / 252 | availability_delayed | candidate_available: 249; forecast_open_unavailable: 1; reference_open_unavailable: 2 |
| NQ / PIN074_ref_01 | 2021 | 249 / 252 | nominal | candidate_available: 249; forecast_open_unavailable: 1; reference_open_unavailable: 2 |
| NQ / PIN074_ref_01 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 87.0% [82.9%, 90.7%] |
| NQ / PIN074_ref_01 | 2021 | 247 observed dates | availability_delayed|definite_print | 27.9% [22.0%, 33.9%] |
| NQ / PIN074_ref_01 | 2021 | 247 observed dates | nominal|compatible_reach | 87.0% [82.9%, 90.7%] |
| NQ / PIN074_ref_01 | 2021 | 247 observed dates | nominal|definite_print | 28.7% [22.7%, 34.8%] |
| NQ / PIN074_ref_01 | 2022 | 249 / 251 | availability_delayed | candidate_available: 249; reference_open_unavailable: 2 |
| NQ / PIN074_ref_01 | 2022 | 249 / 251 | nominal | candidate_available: 249; reference_open_unavailable: 2 |
| NQ / PIN074_ref_01 | 2022 | 245 observed dates | availability_delayed|compatible_reach | 86.5% [82.3%, 90.6%] |
| NQ / PIN074_ref_01 | 2022 | 245 observed dates | availability_delayed|definite_print | 26.5% [22.4%, 31.3%] |
| NQ / PIN074_ref_01 | 2022 | 245 observed dates | nominal|compatible_reach | 86.9% [82.9%, 91.0%] |
| NQ / PIN074_ref_01 | 2022 | 245 observed dates | nominal|definite_print | 26.9% [22.6%, 32.0%] |
| NQ / PIN074_ref_01 | 2023 | 249 / 250 | availability_delayed | candidate_available: 249; forecast_open_unavailable: 1 |
| NQ / PIN074_ref_01 | 2023 | 249 / 250 | nominal | candidate_available: 249; forecast_open_unavailable: 1 |
| NQ / PIN074_ref_01 | 2023 | 242 observed dates | availability_delayed|compatible_reach | 87.2% [82.2%, 91.2%] |
| NQ / PIN074_ref_01 | 2023 | 242 observed dates | availability_delayed|definite_print | 32.2% [25.4%, 38.8%] |
| NQ / PIN074_ref_01 | 2023 | 242 observed dates | nominal|compatible_reach | 87.2% [82.2%, 91.2%] |
| NQ / PIN074_ref_01 | 2023 | 242 observed dates | nominal|definite_print | 32.2% [25.4%, 38.8%] |
| NQ / PIN074_ref_01 | 2024 | 225 / 252 | availability_delayed | candidate_available: 225; reference_open_unavailable: 27 |
| NQ / PIN074_ref_01 | 2024 | 225 / 252 | nominal | candidate_available: 225; reference_open_unavailable: 27 |
| NQ / PIN074_ref_01 | 2024 | 222 observed dates | availability_delayed|compatible_reach | 86.0% [82.5%, 90.7%] |
| NQ / PIN074_ref_01 | 2024 | 222 observed dates | availability_delayed|definite_print | 34.2% [28.3%, 40.8%] |
| NQ / PIN074_ref_01 | 2024 | 222 observed dates | nominal|compatible_reach | 86.0% [82.5%, 90.7%] |
| NQ / PIN074_ref_01 | 2024 | 222 observed dates | nominal|definite_print | 34.7% [28.8%, 41.3%] |
| NQ / PIN074_ref_03 | 2020 | 249 / 253 | availability_delayed | candidate_available: 249; forecast_open_unavailable: 2; reference_open_unavailable: 2 |
| NQ / PIN074_ref_03 | 2020 | 249 / 253 | nominal | candidate_available: 249; forecast_open_unavailable: 2; reference_open_unavailable: 2 |
| NQ / PIN074_ref_03 | 2020 | 239 observed dates | availability_delayed|compatible_reach | 87.9% [82.5%, 92.1%] |
| NQ / PIN074_ref_03 | 2020 | 239 observed dates | availability_delayed|definite_print | 39.3% [32.9%, 45.8%] |
| NQ / PIN074_ref_03 | 2020 | 239 observed dates | nominal|compatible_reach | 88.3% [82.6%, 92.4%] |
| NQ / PIN074_ref_03 | 2020 | 239 observed dates | nominal|definite_print | 39.7% [33.3%, 46.1%] |
| NQ / PIN074_ref_03 | 2021 | 251 / 252 | availability_delayed | candidate_available: 251; forecast_open_unavailable: 1 |
| NQ / PIN074_ref_03 | 2021 | 251 / 252 | nominal | candidate_available: 251; forecast_open_unavailable: 1 |
| NQ / PIN074_ref_03 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 87.4% [83.5%, 90.7%] |
| NQ / PIN074_ref_03 | 2021 | 247 observed dates | availability_delayed|definite_print | 25.9% [20.7%, 30.9%] |
| NQ / PIN074_ref_03 | 2021 | 247 observed dates | nominal|compatible_reach | 87.4% [83.5%, 90.7%] |
| NQ / PIN074_ref_03 | 2021 | 247 observed dates | nominal|definite_print | 26.3% [21.1%, 31.6%] |
| NQ / PIN074_ref_03 | 2022 | 251 / 251 | availability_delayed | candidate_available: 251 |
| NQ / PIN074_ref_03 | 2022 | 251 / 251 | nominal | candidate_available: 251 |
| NQ / PIN074_ref_03 | 2022 | 245 observed dates | availability_delayed|compatible_reach | 88.2% [84.3%, 92.3%] |
| NQ / PIN074_ref_03 | 2022 | 245 observed dates | availability_delayed|definite_print | 31.4% [26.2%, 36.9%] |
| NQ / PIN074_ref_03 | 2022 | 245 observed dates | nominal|compatible_reach | 88.6% [84.8%, 92.6%] |
| NQ / PIN074_ref_03 | 2022 | 245 observed dates | nominal|definite_print | 31.8% [26.7%, 37.6%] |
| NQ / PIN074_ref_03 | 2023 | 249 / 250 | availability_delayed | candidate_available: 249; forecast_open_unavailable: 1 |
| NQ / PIN074_ref_03 | 2023 | 249 / 250 | nominal | candidate_available: 249; forecast_open_unavailable: 1 |
| NQ / PIN074_ref_03 | 2023 | 242 observed dates | availability_delayed|compatible_reach | 88.8% [83.8%, 92.7%] |
| NQ / PIN074_ref_03 | 2023 | 242 observed dates | availability_delayed|definite_print | 31.4% [24.6%, 38.2%] |
| NQ / PIN074_ref_03 | 2023 | 242 observed dates | nominal|compatible_reach | 89.7% [85.1%, 93.5%] |
| NQ / PIN074_ref_03 | 2023 | 242 observed dates | nominal|definite_print | 31.4% [24.6%, 38.2%] |
| NQ / PIN074_ref_03 | 2024 | 228 / 252 | availability_delayed | candidate_available: 228; reference_open_unavailable: 24 |
| NQ / PIN074_ref_03 | 2024 | 228 / 252 | nominal | candidate_available: 228; reference_open_unavailable: 24 |
| NQ / PIN074_ref_03 | 2024 | 223 observed dates | availability_delayed|compatible_reach | 87.4% [84.2%, 91.7%] |
| NQ / PIN074_ref_03 | 2024 | 223 observed dates | availability_delayed|definite_print | 29.1% [23.5%, 35.0%] |
| NQ / PIN074_ref_03 | 2024 | 223 observed dates | nominal|compatible_reach | 87.9% [84.4%, 91.9%] |
| NQ / PIN074_ref_03 | 2024 | 223 observed dates | nominal|definite_print | 30.0% [24.9%, 35.7%] |
| NQ / PIN074_ref_04 | 2020 | 250 / 253 | availability_delayed | candidate_available: 250; forecast_open_unavailable: 3 |
| NQ / PIN074_ref_04 | 2020 | 250 / 253 | nominal | candidate_available: 250; forecast_open_unavailable: 3 |
| NQ / PIN074_ref_04 | 2020 | 240 observed dates | availability_delayed|compatible_reach | 91.7% [87.8%, 95.0%] |
| NQ / PIN074_ref_04 | 2020 | 240 observed dates | availability_delayed|definite_print | 40.4% [34.8%, 46.5%] |
| NQ / PIN074_ref_04 | 2020 | 240 observed dates | nominal|compatible_reach | 92.1% [88.2%, 95.3%] |
| NQ / PIN074_ref_04 | 2020 | 240 observed dates | nominal|definite_print | 40.8% [35.3%, 46.8%] |
| NQ / PIN074_ref_04 | 2021 | 250 / 252 | availability_delayed | candidate_available: 250; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN074_ref_04 | 2021 | 250 / 252 | nominal | candidate_available: 250; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN074_ref_04 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 91.1% [87.4%, 94.2%] |
| NQ / PIN074_ref_04 | 2021 | 247 observed dates | availability_delayed|definite_print | 42.1% [35.6%, 48.6%] |
| NQ / PIN074_ref_04 | 2021 | 247 observed dates | nominal|compatible_reach | 91.1% [87.4%, 94.2%] |
| NQ / PIN074_ref_04 | 2021 | 247 observed dates | nominal|definite_print | 42.1% [35.6%, 48.6%] |
| NQ / PIN074_ref_04 | 2022 | 251 / 251 | availability_delayed | candidate_available: 251 |
| NQ / PIN074_ref_04 | 2022 | 251 / 251 | nominal | candidate_available: 251 |
| NQ / PIN074_ref_04 | 2022 | 245 observed dates | availability_delayed|compatible_reach | 91.4% [87.7%, 95.2%] |
| NQ / PIN074_ref_04 | 2022 | 245 observed dates | availability_delayed|definite_print | 29.0% [23.6%, 34.3%] |
| NQ / PIN074_ref_04 | 2022 | 245 observed dates | nominal|compatible_reach | 91.8% [88.1%, 95.5%] |
| NQ / PIN074_ref_04 | 2022 | 245 observed dates | nominal|definite_print | 29.0% [23.6%, 34.3%] |
| NQ / PIN074_ref_04 | 2023 | 249 / 250 | availability_delayed | candidate_available: 249; forecast_open_unavailable: 1 |
| NQ / PIN074_ref_04 | 2023 | 249 / 250 | nominal | candidate_available: 249; forecast_open_unavailable: 1 |
| NQ / PIN074_ref_04 | 2023 | 242 observed dates | availability_delayed|compatible_reach | 91.3% [87.6%, 94.4%] |
| NQ / PIN074_ref_04 | 2023 | 242 observed dates | availability_delayed|definite_print | 38.0% [33.3%, 44.2%] |
| NQ / PIN074_ref_04 | 2023 | 242 observed dates | nominal|compatible_reach | 92.1% [88.7%, 95.0%] |
| NQ / PIN074_ref_04 | 2023 | 242 observed dates | nominal|definite_print | 39.3% [34.2%, 45.5%] |
| NQ / PIN074_ref_04 | 2024 | 228 / 252 | availability_delayed | candidate_available: 228; reference_open_unavailable: 24 |
| NQ / PIN074_ref_04 | 2024 | 228 / 252 | nominal | candidate_available: 228; reference_open_unavailable: 24 |
| NQ / PIN074_ref_04 | 2024 | 223 observed dates | availability_delayed|compatible_reach | 87.9% [84.3%, 91.6%] |
| NQ / PIN074_ref_04 | 2024 | 223 observed dates | availability_delayed|definite_print | 29.6% [23.9%, 36.0%] |
| NQ / PIN074_ref_04 | 2024 | 223 observed dates | nominal|compatible_reach | 87.9% [84.3%, 91.6%] |
| NQ / PIN074_ref_04 | 2024 | 223 observed dates | nominal|definite_print | 29.6% [23.9%, 36.0%] |
| NQ / PIN074_ref_07 | 2020 | 249 / 253 | availability_delayed | candidate_available: 249; forecast_open_unavailable: 1; reference_open_unavailable: 3 |
| NQ / PIN074_ref_07 | 2020 | 249 / 253 | nominal | candidate_available: 249; forecast_open_unavailable: 1; reference_open_unavailable: 3 |
| NQ / PIN074_ref_07 | 2020 | 240 observed dates | availability_delayed|compatible_reach | 94.6% [92.0%, 97.2%] |
| NQ / PIN074_ref_07 | 2020 | 240 observed dates | availability_delayed|definite_print | 40.8% [35.1%, 46.5%] |
| NQ / PIN074_ref_07 | 2020 | 240 observed dates | nominal|compatible_reach | 94.6% [92.0%, 97.2%] |
| NQ / PIN074_ref_07 | 2020 | 240 observed dates | nominal|definite_print | 40.8% [35.1%, 46.5%] |
| NQ / PIN074_ref_07 | 2021 | 250 / 252 | availability_delayed | candidate_available: 250; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN074_ref_07 | 2021 | 250 / 252 | nominal | candidate_available: 250; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN074_ref_07 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 92.3% [89.1%, 95.1%] |
| NQ / PIN074_ref_07 | 2021 | 247 observed dates | availability_delayed|definite_print | 32.8% [26.9%, 39.4%] |
| NQ / PIN074_ref_07 | 2021 | 247 observed dates | nominal|compatible_reach | 92.7% [89.6%, 95.5%] |
| NQ / PIN074_ref_07 | 2021 | 247 observed dates | nominal|definite_print | 33.2% [27.1%, 39.5%] |
| NQ / PIN074_ref_07 | 2022 | 251 / 251 | availability_delayed | candidate_available: 251 |
| NQ / PIN074_ref_07 | 2022 | 251 / 251 | nominal | candidate_available: 251 |
| NQ / PIN074_ref_07 | 2022 | 245 observed dates | availability_delayed|compatible_reach | 95.9% [93.0%, 98.4%] |
| NQ / PIN074_ref_07 | 2022 | 245 observed dates | availability_delayed|definite_print | 42.4% [36.2%, 48.0%] |
| NQ / PIN074_ref_07 | 2022 | 245 observed dates | nominal|compatible_reach | 96.7% [94.2%, 98.8%] |
| NQ / PIN074_ref_07 | 2022 | 245 observed dates | nominal|definite_print | 43.7% [37.0%, 48.8%] |
| NQ / PIN074_ref_07 | 2023 | 249 / 250 | availability_delayed | candidate_available: 249; forecast_open_unavailable: 1 |
| NQ / PIN074_ref_07 | 2023 | 249 / 250 | nominal | candidate_available: 249; forecast_open_unavailable: 1 |
| NQ / PIN074_ref_07 | 2023 | 242 observed dates | availability_delayed|compatible_reach | 95.0% [92.1%, 97.5%] |
| NQ / PIN074_ref_07 | 2023 | 242 observed dates | availability_delayed|definite_print | 35.1% [28.9%, 40.1%] |
| NQ / PIN074_ref_07 | 2023 | 242 observed dates | nominal|compatible_reach | 95.9% [93.1%, 98.0%] |
| NQ / PIN074_ref_07 | 2023 | 242 observed dates | nominal|definite_print | 35.5% [29.4%, 40.5%] |
| NQ / PIN074_ref_07 | 2024 | 228 / 252 | availability_delayed | candidate_available: 228; reference_open_unavailable: 24 |
| NQ / PIN074_ref_07 | 2024 | 228 / 252 | nominal | candidate_available: 228; reference_open_unavailable: 24 |
| NQ / PIN074_ref_07 | 2024 | 223 observed dates | availability_delayed|compatible_reach | 94.2% [91.5%, 96.9%] |
| NQ / PIN074_ref_07 | 2024 | 223 observed dates | availability_delayed|definite_print | 38.1% [32.4%, 43.4%] |
| NQ / PIN074_ref_07 | 2024 | 223 observed dates | nominal|compatible_reach | 95.1% [92.6%, 97.3%] |
| NQ / PIN074_ref_07 | 2024 | 223 observed dates | nominal|definite_print | 39.0% [33.2%, 44.6%] |
| NQ / PIN076_00_08 | 2020 | 248 / 253 | availability_delayed | candidate_available: 248; forecast_open_unavailable: 2; reference_open_unavailable: 3 |
| NQ / PIN076_00_08 | 2020 | 248 / 253 | nominal | candidate_available: 248; forecast_open_unavailable: 2; reference_open_unavailable: 3 |
| NQ / PIN076_00_08 | 2020 | 239 observed dates | availability_delayed|compatible_reach | 86.2% [81.4%, 90.3%] |
| NQ / PIN076_00_08 | 2020 | 239 observed dates | availability_delayed|definite_print | 34.3% [28.1%, 40.4%] |
| NQ / PIN076_00_08 | 2020 | 239 observed dates | nominal|compatible_reach | 87.0% [82.6%, 91.1%] |
| NQ / PIN076_00_08 | 2020 | 239 observed dates | nominal|definite_print | 34.3% [28.1%, 40.4%] |
| NQ / PIN076_00_08 | 2021 | 250 / 252 | availability_delayed | candidate_available: 250; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN076_00_08 | 2021 | 250 / 252 | nominal | candidate_available: 250; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN076_00_08 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 86.6% [82.6%, 90.3%] |
| NQ / PIN076_00_08 | 2021 | 247 observed dates | availability_delayed|definite_print | 29.1% [23.5%, 35.2%] |
| NQ / PIN076_00_08 | 2021 | 247 observed dates | nominal|compatible_reach | 87.0% [83.0%, 90.7%] |
| NQ / PIN076_00_08 | 2021 | 247 observed dates | nominal|definite_print | 29.6% [24.1%, 35.6%] |
| NQ / PIN076_00_08 | 2022 | 251 / 251 | availability_delayed | candidate_available: 251 |
| NQ / PIN076_00_08 | 2022 | 251 / 251 | nominal | candidate_available: 251 |
| NQ / PIN076_00_08 | 2022 | 245 observed dates | availability_delayed|compatible_reach | 86.5% [82.6%, 90.7%] |
| NQ / PIN076_00_08 | 2022 | 245 observed dates | availability_delayed|definite_print | 28.2% [21.9%, 34.7%] |
| NQ / PIN076_00_08 | 2022 | 245 observed dates | nominal|compatible_reach | 86.5% [82.6%, 90.7%] |
| NQ / PIN076_00_08 | 2022 | 245 observed dates | nominal|definite_print | 28.6% [22.2%, 35.2%] |
| NQ / PIN076_00_08 | 2023 | 248 / 250 | availability_delayed | candidate_available: 248; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN076_00_08 | 2023 | 248 / 250 | nominal | candidate_available: 248; forecast_open_unavailable: 1; reference_open_unavailable: 1 |
| NQ / PIN076_00_08 | 2023 | 242 observed dates | availability_delayed|compatible_reach | 85.5% [80.7%, 89.6%] |
| NQ / PIN076_00_08 | 2023 | 242 observed dates | availability_delayed|definite_print | 34.7% [27.9%, 41.7%] |
| NQ / PIN076_00_08 | 2023 | 242 observed dates | nominal|compatible_reach | 85.5% [80.7%, 89.6%] |
| NQ / PIN076_00_08 | 2023 | 242 observed dates | nominal|definite_print | 35.1% [28.3%, 41.9%] |
| NQ / PIN076_00_08 | 2024 | 226 / 252 | availability_delayed | candidate_available: 226; reference_open_unavailable: 26 |
| NQ / PIN076_00_08 | 2024 | 226 / 252 | nominal | candidate_available: 226; reference_open_unavailable: 26 |
| NQ / PIN076_00_08 | 2024 | 223 observed dates | availability_delayed|compatible_reach | 85.2% [81.7%, 89.9%] |
| NQ / PIN076_00_08 | 2024 | 223 observed dates | availability_delayed|definite_print | 29.6% [24.4%, 36.1%] |
| NQ / PIN076_00_08 | 2024 | 223 observed dates | nominal|compatible_reach | 85.2% [81.7%, 89.9%] |
| NQ / PIN076_00_08 | 2024 | 223 observed dates | nominal|definite_print | 29.6% [24.4%, 36.1%] |
| NQ / PIN076_08_0930 | 2020 | 246 / 253 | availability_delayed | candidate_available: 246; forecast_open_unavailable: 4; reference_open_unavailable: 3 |
| NQ / PIN076_08_0930 | 2020 | 246 / 253 | nominal | candidate_available: 246; forecast_open_unavailable: 4; reference_open_unavailable: 3 |
| NQ / PIN076_08_0930 | 2020 | 240 observed dates | availability_delayed|compatible_reach | 86.7% [82.5%, 90.9%] |
| NQ / PIN076_08_0930 | 2020 | 240 observed dates | availability_delayed|definite_print | 25.8% [20.3%, 31.4%] |
| NQ / PIN076_08_0930 | 2020 | 240 observed dates | nominal|compatible_reach | 93.8% [90.8%, 96.3%] |
| NQ / PIN076_08_0930 | 2020 | 240 observed dates | nominal|definite_print | 26.2% [20.7%, 31.5%] |
| NQ / PIN076_08_0930 | 2021 | 248 / 252 | availability_delayed | candidate_available: 248; forecast_open_unavailable: 3; reference_open_unavailable: 1 |
| NQ / PIN076_08_0930 | 2021 | 248 / 252 | nominal | candidate_available: 248; forecast_open_unavailable: 3; reference_open_unavailable: 1 |
| NQ / PIN076_08_0930 | 2021 | 247 observed dates | availability_delayed|compatible_reach | 81.4% [77.0%, 86.2%] |
| NQ / PIN076_08_0930 | 2021 | 247 observed dates | availability_delayed|definite_print | 27.5% [22.9%, 32.9%] |
| NQ / PIN076_08_0930 | 2021 | 247 observed dates | nominal|compatible_reach | 87.4% [83.8%, 91.8%] |
| NQ / PIN076_08_0930 | 2021 | 247 observed dates | nominal|definite_print | 29.6% [24.6%, 35.3%] |
| NQ / PIN076_08_0930 | 2022 | 247 / 251 | availability_delayed | candidate_available: 247; forecast_open_unavailable: 4 |
| NQ / PIN076_08_0930 | 2022 | 247 / 251 | nominal | candidate_available: 247; forecast_open_unavailable: 4 |
| NQ / PIN076_08_0930 | 2022 | 246 observed dates | availability_delayed|compatible_reach | 81.3% [76.9%, 85.8%] |
| NQ / PIN076_08_0930 | 2022 | 246 observed dates | availability_delayed|definite_print | 22.4% [17.2%, 27.2%] |
| NQ / PIN076_08_0930 | 2022 | 246 observed dates | nominal|compatible_reach | 85.4% [81.6%, 89.4%] |
| NQ / PIN076_08_0930 | 2022 | 246 observed dates | nominal|definite_print | 22.4% [17.2%, 27.2%] |
| NQ / PIN076_08_0930 | 2023 | 245 / 250 | availability_delayed | candidate_available: 245; forecast_open_unavailable: 4; reference_open_unavailable: 1 |
| NQ / PIN076_08_0930 | 2023 | 245 / 250 | nominal | candidate_available: 245; forecast_open_unavailable: 4; reference_open_unavailable: 1 |
| NQ / PIN076_08_0930 | 2023 | 243 observed dates | availability_delayed|compatible_reach | 83.5% [78.6%, 87.6%] |
| NQ / PIN076_08_0930 | 2023 | 243 observed dates | availability_delayed|definite_print | 24.7% [19.5%, 29.8%] |
| NQ / PIN076_08_0930 | 2023 | 243 observed dates | nominal|compatible_reach | 87.7% [83.1%, 91.8%] |
| NQ / PIN076_08_0930 | 2023 | 243 observed dates | nominal|definite_print | 25.5% [20.1%, 30.7%] |
| NQ / PIN076_08_0930 | 2024 | 225 / 252 | availability_delayed | candidate_available: 225; forecast_open_unavailable: 3; reference_open_unavailable: 24 |
| NQ / PIN076_08_0930 | 2024 | 225 / 252 | nominal | candidate_available: 225; forecast_open_unavailable: 3; reference_open_unavailable: 24 |
| NQ / PIN076_08_0930 | 2024 | 223 observed dates | availability_delayed|compatible_reach | 87.9% [83.6%, 91.8%] |
| NQ / PIN076_08_0930 | 2024 | 223 observed dates | availability_delayed|definite_print | 20.6% [15.9%, 25.9%] |
| NQ / PIN076_08_0930 | 2024 | 223 observed dates | nominal|compatible_reach | 90.6% [87.1%, 94.0%] |
| NQ / PIN076_08_0930 | 2024 | 223 observed dates | nominal|definite_print | 20.6% [15.9%, 25.9%] |
| NQ / PIN078_daily_not_combined | 2020 | 0 / 100 | availability_delayed | formation_unavailable: 100 |
| NQ / PIN078_daily_not_combined | 2020 | 0 / 100 | nominal | formation_unavailable: 100 |

NQ 2020: Monday and Tuesday source ranges remain separate daily candidates. Repeated compatible bars and unique contact dates answer different questions.

| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |
|---|---:|---|---|---:|

Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| NQ / PIN078_daily_not_combined | 2021 | 30 / 99 | availability_delayed | candidate_available: 30; formation_unavailable: 69 |
| NQ / PIN078_daily_not_combined | 2021 | 30 / 99 | nominal | candidate_available: 30; formation_unavailable: 69 |

NQ 2021: Monday and Tuesday source ranges remain separate daily candidates. Repeated compatible bars and unique contact dates answer different questions.

| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |
|---|---:|---|---|---:|
| fib1_actual_30pct | 0 / 99 | 0 / unavailable | 0 / unavailable | 0 |
| fib2_actual_70pct | 0 / 99 | 0 / unavailable | 0 / unavailable | 0 |
| high | 0 / 99 | 0 / unavailable | 0 / unavailable | 0 |
| low | 0 / 99 | 0 / unavailable | 0 / unavailable | 0 |
| midpoint | 0 / 99 | 0 / unavailable | 0 / unavailable | 0 |

Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| NQ / PIN078_daily_not_combined | 2022 | 60 / 97 | availability_delayed | candidate_available: 60; formation_unavailable: 37 |
| NQ / PIN078_daily_not_combined | 2022 | 60 / 97 | nominal | candidate_available: 60; formation_unavailable: 37 |

NQ 2022: Monday and Tuesday source ranges remain separate daily candidates. Repeated compatible bars and unique contact dates answer different questions.

| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |
|---|---:|---|---|---:|
| fib1_actual_30pct | 0 / 97 | 0 / unavailable | 0 / unavailable | 0 |
| fib2_actual_70pct | 0 / 97 | 0 / unavailable | 0 / unavailable | 0 |
| high | 0 / 97 | 0 / unavailable | 0 / unavailable | 0 |
| low | 0 / 97 | 0 / unavailable | 0 / unavailable | 0 |
| midpoint | 0 / 97 | 0 / unavailable | 0 / unavailable | 0 |

Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| NQ / PIN078_daily_not_combined | 2023 | 50 / 96 | availability_delayed | candidate_available: 50; formation_unavailable: 46 |
| NQ / PIN078_daily_not_combined | 2023 | 50 / 96 | nominal | candidate_available: 50; formation_unavailable: 46 |

NQ 2023: Monday and Tuesday source ranges remain separate daily candidates. Repeated compatible bars and unique contact dates answer different questions.

| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |
|---|---:|---|---|---:|
| fib1_actual_30pct | 0 / 96 | 0 / unavailable | 0 / unavailable | 0 |
| fib2_actual_70pct | 0 / 96 | 0 / unavailable | 0 / unavailable | 0 |
| high | 0 / 96 | 0 / unavailable | 0 / unavailable | 0 |
| low | 0 / 96 | 0 / unavailable | 0 / unavailable | 0 |
| midpoint | 0 / 96 | 0 / unavailable | 0 / unavailable | 0 |

Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| NQ / PIN078_daily_not_combined | 2024 | 48 / 101 | availability_delayed | candidate_available: 48; formation_unavailable: 53 |
| NQ / PIN078_daily_not_combined | 2024 | 48 / 101 | nominal | candidate_available: 48; formation_unavailable: 53 |

NQ 2024: Monday and Tuesday source ranges remain separate daily candidates. Repeated compatible bars and unique contact dates answer different questions.

| Source level | Eligible / excluded dates | Unique compatible dates / rate | Unique definite-print dates / rate | Repeated compatible bars |
|---|---:|---|---|---:|
| fib1_actual_30pct | 0 / 101 | 0 / unavailable | 0 / unavailable | 0 |
| fib2_actual_70pct | 0 / 101 | 0 / unavailable | 0 / unavailable | 0 |
| high | 0 / 101 | 0 / unavailable | 0 / unavailable | 0 |
| low | 0 / 101 | 0 / unavailable | 0 / unavailable | 0 |
| midpoint | 0 / 101 | 0 / unavailable | 0 / unavailable | 0 |

Formation-date share of repeated straddling bars, not source exchange-weekday mapping and not daily probability.

| Instrument / source clock | Year | Candidate / intended | Branch | Observed states |
|---|---:|---:|---|---|
| NQ / magic_00 | 2020 | 240 / 253 | availability_delayed | break_then_neither_by_horizon: 7; future_censored: 3; invalidation_before_midpoint: 86; midpoint_before_invalidation: 143; no_break_by_horizon: 1 |
| NQ / magic_00 | 2020 | 240 / 253 | nominal | break_then_neither_by_horizon: 7; future_censored: 3; invalidation_before_midpoint: 85; midpoint_before_invalidation: 144; no_break_by_horizon: 1 |
| NQ / magic_00 | 2020 | 237 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.0% [0.8%, 4.8%] |
| NQ / magic_00 | 2020 | 237 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.0% [0.8%, 4.8%] |
| NQ / magic_00 | 2020 | 237 observed dates | availability_delayed|invalidation_before_midpoint_lower | 36.3% [31.0%, 42.3%] |
| NQ / magic_00 | 2020 | 237 observed dates | availability_delayed|invalidation_before_midpoint_upper | 36.3% [31.0%, 42.3%] |
| NQ / magic_00 | 2020 | 237 observed dates | availability_delayed|midpoint_before_invalidation_lower | 60.3% [54.3%, 66.2%] |
| NQ / magic_00 | 2020 | 237 observed dates | availability_delayed|midpoint_before_invalidation_upper | 60.3% [54.3%, 66.2%] |
| NQ / magic_00 | 2020 | 237 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2020 | 237 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2020 | 237 observed dates | nominal|break_then_neither_by_horizon_lower | 3.0% [0.8%, 4.8%] |
| NQ / magic_00 | 2020 | 237 observed dates | nominal|break_then_neither_by_horizon_upper | 3.0% [0.8%, 4.8%] |
| NQ / magic_00 | 2020 | 237 observed dates | nominal|invalidation_before_midpoint_lower | 35.9% [30.4%, 42.1%] |
| NQ / magic_00 | 2020 | 237 observed dates | nominal|invalidation_before_midpoint_upper | 35.9% [30.4%, 42.1%] |
| NQ / magic_00 | 2020 | 237 observed dates | nominal|midpoint_before_invalidation_lower | 60.8% [54.6%, 66.7%] |
| NQ / magic_00 | 2020 | 237 observed dates | nominal|midpoint_before_invalidation_upper | 60.8% [54.6%, 66.7%] |
| NQ / magic_00 | 2020 | 237 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2020 | 237 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2021 | 230 / 252 | availability_delayed | break_then_neither_by_horizon: 8; competing_order_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 77; midpoint_before_invalidation: 142 |
| NQ / magic_00 | 2021 | 230 / 252 | nominal | break_then_neither_by_horizon: 8; competing_order_ambiguous: 3; future_censored: 2; invalidation_before_midpoint: 70; midpoint_before_invalidation: 147 |
| NQ / magic_00 | 2021 | 228 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.5% [0.9%, 5.7%] |
| NQ / magic_00 | 2021 | 228 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.5% [0.9%, 5.7%] |
| NQ / magic_00 | 2021 | 228 observed dates | availability_delayed|invalidation_before_midpoint_lower | 33.8% [26.9%, 40.4%] |
| NQ / magic_00 | 2021 | 228 observed dates | availability_delayed|invalidation_before_midpoint_upper | 34.2% [27.4%, 40.8%] |
| NQ / magic_00 | 2021 | 228 observed dates | availability_delayed|midpoint_before_invalidation_lower | 62.3% [56.1%, 69.0%] |
| NQ / magic_00 | 2021 | 228 observed dates | availability_delayed|midpoint_before_invalidation_upper | 62.7% [56.5%, 69.2%] |
| NQ / magic_00 | 2021 | 228 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_00 | 2021 | 228 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_00 | 2021 | 228 observed dates | nominal|break_then_neither_by_horizon_lower | 3.5% [0.9%, 5.7%] |
| NQ / magic_00 | 2021 | 228 observed dates | nominal|break_then_neither_by_horizon_upper | 3.5% [0.9%, 5.7%] |
| NQ / magic_00 | 2021 | 228 observed dates | nominal|invalidation_before_midpoint_lower | 30.7% [24.0%, 37.2%] |
| NQ / magic_00 | 2021 | 228 observed dates | nominal|invalidation_before_midpoint_upper | 32.0% [25.2%, 38.6%] |
| NQ / magic_00 | 2021 | 228 observed dates | nominal|midpoint_before_invalidation_lower | 64.5% [58.4%, 71.1%] |
| NQ / magic_00 | 2021 | 228 observed dates | nominal|midpoint_before_invalidation_upper | 65.8% [59.6%, 72.3%] |
| NQ / magic_00 | 2021 | 228 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_00 | 2021 | 228 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_00 | 2022 | 243 / 251 | availability_delayed | break_then_neither_by_horizon: 4; competing_order_ambiguous: 2; invalidation_before_midpoint: 71; midpoint_before_invalidation: 165; no_break_by_horizon: 1 |
| NQ / magic_00 | 2022 | 243 / 251 | nominal | break_then_neither_by_horizon: 4; competing_order_ambiguous: 3; invalidation_before_midpoint: 69; midpoint_before_invalidation: 166; no_break_by_horizon: 1 |
| NQ / magic_00 | 2022 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 1.6% [0.4%, 3.7%] |
| NQ / magic_00 | 2022 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 1.6% [0.4%, 3.7%] |
| NQ / magic_00 | 2022 | 243 observed dates | availability_delayed|invalidation_before_midpoint_lower | 29.2% [23.3%, 34.7%] |
| NQ / magic_00 | 2022 | 243 observed dates | availability_delayed|invalidation_before_midpoint_upper | 30.0% [24.3%, 35.7%] |
| NQ / magic_00 | 2022 | 243 observed dates | availability_delayed|midpoint_before_invalidation_lower | 67.9% [62.3%, 73.7%] |
| NQ / magic_00 | 2022 | 243 observed dates | availability_delayed|midpoint_before_invalidation_upper | 68.7% [63.1%, 74.7%] |
| NQ / magic_00 | 2022 | 243 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2022 | 243 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2022 | 243 observed dates | nominal|break_then_neither_by_horizon_lower | 1.6% [0.4%, 3.7%] |
| NQ / magic_00 | 2022 | 243 observed dates | nominal|break_then_neither_by_horizon_upper | 1.6% [0.4%, 3.7%] |
| NQ / magic_00 | 2022 | 243 observed dates | nominal|invalidation_before_midpoint_lower | 28.4% [22.6%, 33.6%] |
| NQ / magic_00 | 2022 | 243 observed dates | nominal|invalidation_before_midpoint_upper | 29.6% [23.9%, 35.1%] |
| NQ / magic_00 | 2022 | 243 observed dates | nominal|midpoint_before_invalidation_lower | 68.3% [63.0%, 74.1%] |
| NQ / magic_00 | 2022 | 243 observed dates | nominal|midpoint_before_invalidation_upper | 69.5% [63.9%, 75.5%] |
| NQ / magic_00 | 2022 | 243 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2022 | 243 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2023 | 230 / 250 | availability_delayed | break_then_neither_by_horizon: 1; future_censored: 1; invalidation_before_midpoint: 89; midpoint_before_invalidation: 139 |
| NQ / magic_00 | 2023 | 230 / 250 | nominal | break_then_neither_by_horizon: 1; future_censored: 1; invalidation_before_midpoint: 87; midpoint_before_invalidation: 141 |
| NQ / magic_00 | 2023 | 229 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2023 | 229 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2023 | 229 observed dates | availability_delayed|invalidation_before_midpoint_lower | 38.9% [31.7%, 45.6%] |
| NQ / magic_00 | 2023 | 229 observed dates | availability_delayed|invalidation_before_midpoint_upper | 38.9% [31.7%, 45.6%] |
| NQ / magic_00 | 2023 | 229 observed dates | availability_delayed|midpoint_before_invalidation_lower | 60.7% [54.1%, 67.6%] |
| NQ / magic_00 | 2023 | 229 observed dates | availability_delayed|midpoint_before_invalidation_upper | 60.7% [54.1%, 67.6%] |
| NQ / magic_00 | 2023 | 229 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_00 | 2023 | 229 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_00 | 2023 | 229 observed dates | nominal|break_then_neither_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2023 | 229 observed dates | nominal|break_then_neither_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_00 | 2023 | 229 observed dates | nominal|invalidation_before_midpoint_lower | 38.0% [30.9%, 44.4%] |
| NQ / magic_00 | 2023 | 229 observed dates | nominal|invalidation_before_midpoint_upper | 38.0% [30.9%, 44.4%] |
| NQ / magic_00 | 2023 | 229 observed dates | nominal|midpoint_before_invalidation_lower | 61.6% [55.2%, 68.4%] |
| NQ / magic_00 | 2023 | 229 observed dates | nominal|midpoint_before_invalidation_upper | 61.6% [55.2%, 68.4%] |
| NQ / magic_00 | 2023 | 229 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_00 | 2023 | 229 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_00 | 2024 | 204 / 252 | availability_delayed | break_then_neither_by_horizon: 5; future_censored: 2; invalidation_before_midpoint: 84; midpoint_before_invalidation: 112; no_break_by_horizon: 1 |
| NQ / magic_00 | 2024 | 204 / 252 | nominal | break_then_neither_by_horizon: 5; competing_order_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 82; midpoint_before_invalidation: 113; no_break_by_horizon: 1 |
| NQ / magic_00 | 2024 | 202 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.5% [0.5%, 4.8%] |
| NQ / magic_00 | 2024 | 202 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.5% [0.5%, 4.8%] |
| NQ / magic_00 | 2024 | 202 observed dates | availability_delayed|invalidation_before_midpoint_lower | 41.6% [35.4%, 47.5%] |
| NQ / magic_00 | 2024 | 202 observed dates | availability_delayed|invalidation_before_midpoint_upper | 41.6% [35.4%, 47.5%] |
| NQ / magic_00 | 2024 | 202 observed dates | availability_delayed|midpoint_before_invalidation_lower | 55.4% [49.5%, 61.3%] |
| NQ / magic_00 | 2024 | 202 observed dates | availability_delayed|midpoint_before_invalidation_upper | 55.4% [49.5%, 61.3%] |
| NQ / magic_00 | 2024 | 202 observed dates | availability_delayed|no_break_by_horizon_lower | 0.5% [0.0%, 1.6%] |
| NQ / magic_00 | 2024 | 202 observed dates | availability_delayed|no_break_by_horizon_upper | 0.5% [0.0%, 1.6%] |
| NQ / magic_00 | 2024 | 202 observed dates | nominal|break_then_neither_by_horizon_lower | 2.5% [0.5%, 4.8%] |
| NQ / magic_00 | 2024 | 202 observed dates | nominal|break_then_neither_by_horizon_upper | 2.5% [0.5%, 4.8%] |
| NQ / magic_00 | 2024 | 202 observed dates | nominal|invalidation_before_midpoint_lower | 40.6% [35.0%, 46.5%] |
| NQ / magic_00 | 2024 | 202 observed dates | nominal|invalidation_before_midpoint_upper | 41.1% [35.1%, 46.9%] |
| NQ / magic_00 | 2024 | 202 observed dates | nominal|midpoint_before_invalidation_lower | 55.9% [50.0%, 61.6%] |
| NQ / magic_00 | 2024 | 202 observed dates | nominal|midpoint_before_invalidation_upper | 56.4% [50.7%, 61.9%] |
| NQ / magic_00 | 2024 | 202 observed dates | nominal|no_break_by_horizon_lower | 0.5% [0.0%, 1.6%] |
| NQ / magic_00 | 2024 | 202 observed dates | nominal|no_break_by_horizon_upper | 0.5% [0.0%, 1.6%] |
| NQ / magic_01 | 2020 | 240 / 253 | availability_delayed | break_then_neither_by_horizon: 20; competing_order_ambiguous: 1; invalidation_before_midpoint: 81; midpoint_before_invalidation: 137; no_break_by_horizon: 1 |
| NQ / magic_01 | 2020 | 240 / 253 | nominal | break_then_neither_by_horizon: 20; competing_order_ambiguous: 2; invalidation_before_midpoint: 79; midpoint_before_invalidation: 138; no_break_by_horizon: 1 |
| NQ / magic_01 | 2020 | 240 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 8.3% [5.5%, 12.1%] |
| NQ / magic_01 | 2020 | 240 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 8.3% [5.5%, 12.1%] |
| NQ / magic_01 | 2020 | 240 observed dates | availability_delayed|invalidation_before_midpoint_lower | 33.8% [28.2%, 39.3%] |
| NQ / magic_01 | 2020 | 240 observed dates | availability_delayed|invalidation_before_midpoint_upper | 34.2% [28.8%, 39.8%] |
| NQ / magic_01 | 2020 | 240 observed dates | availability_delayed|midpoint_before_invalidation_lower | 57.1% [51.1%, 62.6%] |
| NQ / magic_01 | 2020 | 240 observed dates | availability_delayed|midpoint_before_invalidation_upper | 57.5% [51.4%, 63.2%] |
| NQ / magic_01 | 2020 | 240 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_01 | 2020 | 240 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_01 | 2020 | 240 observed dates | nominal|break_then_neither_by_horizon_lower | 8.3% [5.5%, 12.1%] |
| NQ / magic_01 | 2020 | 240 observed dates | nominal|break_then_neither_by_horizon_upper | 8.3% [5.5%, 12.1%] |
| NQ / magic_01 | 2020 | 240 observed dates | nominal|invalidation_before_midpoint_lower | 32.9% [27.8%, 38.2%] |
| NQ / magic_01 | 2020 | 240 observed dates | nominal|invalidation_before_midpoint_upper | 33.8% [28.4%, 39.5%] |
| NQ / magic_01 | 2020 | 240 observed dates | nominal|midpoint_before_invalidation_lower | 57.5% [51.5%, 62.8%] |
| NQ / magic_01 | 2020 | 240 observed dates | nominal|midpoint_before_invalidation_upper | 58.3% [52.2%, 63.9%] |
| NQ / magic_01 | 2020 | 240 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_01 | 2020 | 240 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_01 | 2021 | 241 / 252 | availability_delayed | break_then_neither_by_horizon: 14; competing_order_ambiguous: 3; future_censored: 1; invalidation_before_midpoint: 80; midpoint_before_invalidation: 142; no_break_by_horizon: 1 |
| NQ / magic_01 | 2021 | 241 / 252 | nominal | break_then_neither_by_horizon: 14; competing_order_ambiguous: 2; future_censored: 1; invalidation_before_midpoint: 78; midpoint_before_invalidation: 145; no_break_by_horizon: 1 |
| NQ / magic_01 | 2021 | 240 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 5.8% [3.0%, 8.9%] |
| NQ / magic_01 | 2021 | 240 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 5.8% [3.0%, 8.9%] |
| NQ / magic_01 | 2021 | 240 observed dates | availability_delayed|invalidation_before_midpoint_lower | 33.3% [27.1%, 39.1%] |
| NQ / magic_01 | 2021 | 240 observed dates | availability_delayed|invalidation_before_midpoint_upper | 34.6% [28.2%, 40.6%] |
| NQ / magic_01 | 2021 | 240 observed dates | availability_delayed|midpoint_before_invalidation_lower | 59.2% [52.5%, 65.6%] |
| NQ / magic_01 | 2021 | 240 observed dates | availability_delayed|midpoint_before_invalidation_upper | 60.4% [53.8%, 66.7%] |
| NQ / magic_01 | 2021 | 240 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_01 | 2021 | 240 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_01 | 2021 | 240 observed dates | nominal|break_then_neither_by_horizon_lower | 5.8% [3.0%, 8.9%] |
| NQ / magic_01 | 2021 | 240 observed dates | nominal|break_then_neither_by_horizon_upper | 5.8% [3.0%, 8.9%] |
| NQ / magic_01 | 2021 | 240 observed dates | nominal|invalidation_before_midpoint_lower | 32.5% [26.4%, 38.6%] |
| NQ / magic_01 | 2021 | 240 observed dates | nominal|invalidation_before_midpoint_upper | 33.3% [27.0%, 39.8%] |
| NQ / magic_01 | 2021 | 240 observed dates | nominal|midpoint_before_invalidation_lower | 60.4% [53.3%, 66.8%] |
| NQ / magic_01 | 2021 | 240 observed dates | nominal|midpoint_before_invalidation_upper | 61.3% [54.7%, 67.2%] |
| NQ / magic_01 | 2021 | 240 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_01 | 2021 | 240 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_01 | 2022 | 247 / 251 | availability_delayed | break_then_neither_by_horizon: 8; competing_order_ambiguous: 1; future_censored: 1; invalidation_before_midpoint: 82; midpoint_before_invalidation: 155 |
| NQ / magic_01 | 2022 | 247 / 251 | nominal | break_then_neither_by_horizon: 8; competing_order_ambiguous: 1; future_censored: 1; invalidation_before_midpoint: 79; midpoint_before_invalidation: 158 |
| NQ / magic_01 | 2022 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.3% [1.2%, 5.7%] |
| NQ / magic_01 | 2022 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.3% [1.2%, 5.7%] |
| NQ / magic_01 | 2022 | 246 observed dates | availability_delayed|invalidation_before_midpoint_lower | 33.3% [27.3%, 39.4%] |
| NQ / magic_01 | 2022 | 246 observed dates | availability_delayed|invalidation_before_midpoint_upper | 33.7% [28.1%, 39.7%] |
| NQ / magic_01 | 2022 | 246 observed dates | availability_delayed|midpoint_before_invalidation_lower | 63.0% [57.2%, 69.1%] |
| NQ / magic_01 | 2022 | 246 observed dates | availability_delayed|midpoint_before_invalidation_upper | 63.4% [57.6%, 69.5%] |
| NQ / magic_01 | 2022 | 246 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2022 | 246 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2022 | 246 observed dates | nominal|break_then_neither_by_horizon_lower | 3.3% [1.2%, 5.7%] |
| NQ / magic_01 | 2022 | 246 observed dates | nominal|break_then_neither_by_horizon_upper | 3.3% [1.2%, 5.7%] |
| NQ / magic_01 | 2022 | 246 observed dates | nominal|invalidation_before_midpoint_lower | 32.1% [26.5%, 38.5%] |
| NQ / magic_01 | 2022 | 246 observed dates | nominal|invalidation_before_midpoint_upper | 32.5% [27.0%, 38.7%] |
| NQ / magic_01 | 2022 | 246 observed dates | nominal|midpoint_before_invalidation_lower | 64.2% [58.4%, 70.0%] |
| NQ / magic_01 | 2022 | 246 observed dates | nominal|midpoint_before_invalidation_upper | 64.6% [58.5%, 70.6%] |
| NQ / magic_01 | 2022 | 246 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2022 | 246 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2023 | 239 / 250 | availability_delayed | break_then_neither_by_horizon: 5; competing_order_ambiguous: 2; future_censored: 2; invalidation_before_midpoint: 93; midpoint_before_invalidation: 137 |
| NQ / magic_01 | 2023 | 239 / 250 | nominal | break_then_neither_by_horizon: 5; competing_order_ambiguous: 3; first_side_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 89; midpoint_before_invalidation: 139 |
| NQ / magic_01 | 2023 | 237 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.1% [0.4%, 4.1%] |
| NQ / magic_01 | 2023 | 237 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.1% [0.4%, 4.1%] |
| NQ / magic_01 | 2023 | 237 observed dates | availability_delayed|invalidation_before_midpoint_lower | 39.2% [33.9%, 45.0%] |
| NQ / magic_01 | 2023 | 237 observed dates | availability_delayed|invalidation_before_midpoint_upper | 40.1% [35.2%, 45.6%] |
| NQ / magic_01 | 2023 | 237 observed dates | availability_delayed|midpoint_before_invalidation_lower | 57.8% [52.3%, 62.9%] |
| NQ / magic_01 | 2023 | 237 observed dates | availability_delayed|midpoint_before_invalidation_upper | 58.6% [52.9%, 64.1%] |
| NQ / magic_01 | 2023 | 237 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2023 | 237 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2023 | 237 observed dates | nominal|break_then_neither_by_horizon_lower | 2.1% [0.4%, 4.1%] |
| NQ / magic_01 | 2023 | 237 observed dates | nominal|break_then_neither_by_horizon_upper | 2.1% [0.4%, 4.1%] |
| NQ / magic_01 | 2023 | 237 observed dates | nominal|invalidation_before_midpoint_lower | 37.6% [32.5%, 43.1%] |
| NQ / magic_01 | 2023 | 237 observed dates | nominal|invalidation_before_midpoint_upper | 38.8% [34.0%, 44.1%] |
| NQ / magic_01 | 2023 | 237 observed dates | nominal|midpoint_before_invalidation_lower | 59.1% [54.0%, 64.1%] |
| NQ / magic_01 | 2023 | 237 observed dates | nominal|midpoint_before_invalidation_upper | 60.3% [55.0%, 65.7%] |
| NQ / magic_01 | 2023 | 237 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2023 | 237 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2024 | 220 / 252 | availability_delayed | break_then_neither_by_horizon: 9; future_censored: 2; invalidation_before_midpoint: 71; midpoint_before_invalidation: 138 |
| NQ / magic_01 | 2024 | 220 / 252 | nominal | break_then_neither_by_horizon: 9; future_censored: 2; invalidation_before_midpoint: 67; midpoint_before_invalidation: 142 |
| NQ / magic_01 | 2024 | 218 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 4.1% [1.8%, 7.1%] |
| NQ / magic_01 | 2024 | 218 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 4.1% [1.8%, 7.1%] |
| NQ / magic_01 | 2024 | 218 observed dates | availability_delayed|invalidation_before_midpoint_lower | 32.6% [26.8%, 38.5%] |
| NQ / magic_01 | 2024 | 218 observed dates | availability_delayed|invalidation_before_midpoint_upper | 32.6% [26.8%, 38.5%] |
| NQ / magic_01 | 2024 | 218 observed dates | availability_delayed|midpoint_before_invalidation_lower | 63.3% [56.9%, 69.1%] |
| NQ / magic_01 | 2024 | 218 observed dates | availability_delayed|midpoint_before_invalidation_upper | 63.3% [56.9%, 69.1%] |
| NQ / magic_01 | 2024 | 218 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2024 | 218 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2024 | 218 observed dates | nominal|break_then_neither_by_horizon_lower | 4.1% [1.8%, 7.1%] |
| NQ / magic_01 | 2024 | 218 observed dates | nominal|break_then_neither_by_horizon_upper | 4.1% [1.8%, 7.1%] |
| NQ / magic_01 | 2024 | 218 observed dates | nominal|invalidation_before_midpoint_lower | 30.7% [25.2%, 37.0%] |
| NQ / magic_01 | 2024 | 218 observed dates | nominal|invalidation_before_midpoint_upper | 30.7% [25.2%, 37.0%] |
| NQ / magic_01 | 2024 | 218 observed dates | nominal|midpoint_before_invalidation_lower | 65.1% [58.6%, 71.3%] |
| NQ / magic_01 | 2024 | 218 observed dates | nominal|midpoint_before_invalidation_upper | 65.1% [58.6%, 71.3%] |
| NQ / magic_01 | 2024 | 218 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_01 | 2024 | 218 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_02 | 2020 | 244 / 253 | availability_delayed | break_then_neither_by_horizon: 25; competing_order_ambiguous: 1; future_censored: 1; invalidation_before_midpoint: 93; midpoint_before_invalidation: 119; no_break_by_horizon: 5 |
| NQ / magic_02 | 2020 | 244 / 253 | nominal | break_then_neither_by_horizon: 24; competing_order_ambiguous: 3; future_censored: 1; invalidation_before_midpoint: 89; midpoint_before_invalidation: 122; no_break_by_horizon: 5 |
| NQ / magic_02 | 2020 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 10.3% [6.6%, 14.2%] |
| NQ / magic_02 | 2020 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 10.3% [6.6%, 14.2%] |
| NQ / magic_02 | 2020 | 243 observed dates | availability_delayed|invalidation_before_midpoint_lower | 38.3% [32.3%, 44.4%] |
| NQ / magic_02 | 2020 | 243 observed dates | availability_delayed|invalidation_before_midpoint_upper | 38.7% [32.6%, 45.1%] |
| NQ / magic_02 | 2020 | 243 observed dates | availability_delayed|midpoint_before_invalidation_lower | 49.0% [41.9%, 55.2%] |
| NQ / magic_02 | 2020 | 243 observed dates | availability_delayed|midpoint_before_invalidation_upper | 49.4% [42.6%, 55.6%] |
| NQ / magic_02 | 2020 | 243 observed dates | availability_delayed|no_break_by_horizon_lower | 2.1% [0.4%, 3.8%] |
| NQ / magic_02 | 2020 | 243 observed dates | availability_delayed|no_break_by_horizon_upper | 2.1% [0.4%, 3.8%] |
| NQ / magic_02 | 2020 | 243 observed dates | nominal|break_then_neither_by_horizon_lower | 9.9% [6.4%, 13.8%] |
| NQ / magic_02 | 2020 | 243 observed dates | nominal|break_then_neither_by_horizon_upper | 9.9% [6.4%, 13.8%] |
| NQ / magic_02 | 2020 | 243 observed dates | nominal|invalidation_before_midpoint_lower | 36.6% [30.2%, 43.0%] |
| NQ / magic_02 | 2020 | 243 observed dates | nominal|invalidation_before_midpoint_upper | 37.9% [31.5%, 44.4%] |
| NQ / magic_02 | 2020 | 243 observed dates | nominal|midpoint_before_invalidation_lower | 50.2% [43.0%, 56.6%] |
| NQ / magic_02 | 2020 | 243 observed dates | nominal|midpoint_before_invalidation_upper | 51.4% [44.5%, 57.9%] |
| NQ / magic_02 | 2020 | 243 observed dates | nominal|no_break_by_horizon_lower | 2.1% [0.4%, 3.8%] |
| NQ / magic_02 | 2020 | 243 observed dates | nominal|no_break_by_horizon_upper | 2.1% [0.4%, 3.8%] |
| NQ / magic_02 | 2021 | 247 / 252 | availability_delayed | break_then_neither_by_horizon: 21; future_censored: 3; invalidation_before_midpoint: 89; midpoint_before_invalidation: 130; no_break_by_horizon: 4 |
| NQ / magic_02 | 2021 | 247 / 252 | nominal | break_then_neither_by_horizon: 21; competing_order_ambiguous: 1; future_censored: 3; invalidation_before_midpoint: 85; midpoint_before_invalidation: 134; no_break_by_horizon: 3 |
| NQ / magic_02 | 2021 | 244 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 8.6% [4.5%, 11.7%] |
| NQ / magic_02 | 2021 | 244 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 8.6% [4.5%, 11.7%] |
| NQ / magic_02 | 2021 | 244 observed dates | availability_delayed|invalidation_before_midpoint_lower | 36.5% [30.9%, 41.9%] |
| NQ / magic_02 | 2021 | 244 observed dates | availability_delayed|invalidation_before_midpoint_upper | 36.5% [30.9%, 41.9%] |
| NQ / magic_02 | 2021 | 244 observed dates | availability_delayed|midpoint_before_invalidation_lower | 53.3% [48.4%, 59.6%] |
| NQ / magic_02 | 2021 | 244 observed dates | availability_delayed|midpoint_before_invalidation_upper | 53.3% [48.4%, 59.6%] |
| NQ / magic_02 | 2021 | 244 observed dates | availability_delayed|no_break_by_horizon_lower | 1.6% [0.0%, 3.7%] |
| NQ / magic_02 | 2021 | 244 observed dates | availability_delayed|no_break_by_horizon_upper | 1.6% [0.0%, 3.7%] |
| NQ / magic_02 | 2021 | 244 observed dates | nominal|break_then_neither_by_horizon_lower | 8.6% [4.5%, 11.7%] |
| NQ / magic_02 | 2021 | 244 observed dates | nominal|break_then_neither_by_horizon_upper | 8.6% [4.5%, 11.7%] |
| NQ / magic_02 | 2021 | 244 observed dates | nominal|invalidation_before_midpoint_lower | 34.8% [28.9%, 40.3%] |
| NQ / magic_02 | 2021 | 244 observed dates | nominal|invalidation_before_midpoint_upper | 35.2% [29.6%, 40.7%] |
| NQ / magic_02 | 2021 | 244 observed dates | nominal|midpoint_before_invalidation_lower | 54.9% [50.0%, 61.4%] |
| NQ / magic_02 | 2021 | 244 observed dates | nominal|midpoint_before_invalidation_upper | 55.3% [50.2%, 61.8%] |
| NQ / magic_02 | 2021 | 244 observed dates | nominal|no_break_by_horizon_lower | 1.2% [0.0%, 3.3%] |
| NQ / magic_02 | 2021 | 244 observed dates | nominal|no_break_by_horizon_upper | 1.2% [0.0%, 3.3%] |
| NQ / magic_02 | 2022 | 246 / 251 | availability_delayed | break_then_neither_by_horizon: 11; competing_order_ambiguous: 3; invalidation_before_midpoint: 95; midpoint_before_invalidation: 133; no_break_by_horizon: 4 |
| NQ / magic_02 | 2022 | 246 / 251 | nominal | break_then_neither_by_horizon: 10; competing_order_ambiguous: 5; invalidation_before_midpoint: 89; midpoint_before_invalidation: 138; no_break_by_horizon: 4 |
| NQ / magic_02 | 2022 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 4.5% [2.0%, 7.3%] |
| NQ / magic_02 | 2022 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 4.5% [2.0%, 7.3%] |
| NQ / magic_02 | 2022 | 246 observed dates | availability_delayed|invalidation_before_midpoint_lower | 38.6% [32.5%, 45.1%] |
| NQ / magic_02 | 2022 | 246 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.8% [33.6%, 46.3%] |
| NQ / magic_02 | 2022 | 246 observed dates | availability_delayed|midpoint_before_invalidation_lower | 54.1% [46.9%, 60.6%] |
| NQ / magic_02 | 2022 | 246 observed dates | availability_delayed|midpoint_before_invalidation_upper | 55.3% [48.2%, 61.8%] |
| NQ / magic_02 | 2022 | 246 observed dates | availability_delayed|no_break_by_horizon_lower | 1.6% [0.4%, 3.3%] |
| NQ / magic_02 | 2022 | 246 observed dates | availability_delayed|no_break_by_horizon_upper | 1.6% [0.4%, 3.3%] |
| NQ / magic_02 | 2022 | 246 observed dates | nominal|break_then_neither_by_horizon_lower | 4.1% [1.6%, 6.6%] |
| NQ / magic_02 | 2022 | 246 observed dates | nominal|break_then_neither_by_horizon_upper | 4.1% [1.6%, 6.6%] |
| NQ / magic_02 | 2022 | 246 observed dates | nominal|invalidation_before_midpoint_lower | 36.2% [30.1%, 42.5%] |
| NQ / magic_02 | 2022 | 246 observed dates | nominal|invalidation_before_midpoint_upper | 38.2% [32.0%, 44.7%] |
| NQ / magic_02 | 2022 | 246 observed dates | nominal|midpoint_before_invalidation_lower | 56.1% [49.2%, 62.7%] |
| NQ / magic_02 | 2022 | 246 observed dates | nominal|midpoint_before_invalidation_upper | 58.1% [51.6%, 64.4%] |
| NQ / magic_02 | 2022 | 246 observed dates | nominal|no_break_by_horizon_lower | 1.6% [0.4%, 3.3%] |
| NQ / magic_02 | 2022 | 246 observed dates | nominal|no_break_by_horizon_upper | 1.6% [0.4%, 3.3%] |
| NQ / magic_02 | 2023 | 242 / 250 | availability_delayed | break_then_neither_by_horizon: 9; competing_order_ambiguous: 1; future_censored: 1; invalidation_before_midpoint: 106; midpoint_before_invalidation: 125 |
| NQ / magic_02 | 2023 | 242 / 250 | nominal | break_then_neither_by_horizon: 8; competing_order_ambiguous: 2; future_censored: 1; invalidation_before_midpoint: 103; midpoint_before_invalidation: 128 |
| NQ / magic_02 | 2023 | 241 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.7% [1.6%, 6.4%] |
| NQ / magic_02 | 2023 | 241 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.7% [1.6%, 6.4%] |
| NQ / magic_02 | 2023 | 241 observed dates | availability_delayed|invalidation_before_midpoint_lower | 44.0% [37.0%, 49.8%] |
| NQ / magic_02 | 2023 | 241 observed dates | availability_delayed|invalidation_before_midpoint_upper | 44.4% [37.7%, 50.0%] |
| NQ / magic_02 | 2023 | 241 observed dates | availability_delayed|midpoint_before_invalidation_lower | 51.9% [46.0%, 58.7%] |
| NQ / magic_02 | 2023 | 241 observed dates | availability_delayed|midpoint_before_invalidation_upper | 52.3% [46.2%, 59.2%] |
| NQ / magic_02 | 2023 | 241 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_02 | 2023 | 241 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_02 | 2023 | 241 observed dates | nominal|break_then_neither_by_horizon_lower | 3.3% [1.3%, 5.6%] |
| NQ / magic_02 | 2023 | 241 observed dates | nominal|break_then_neither_by_horizon_upper | 3.3% [1.3%, 5.6%] |
| NQ / magic_02 | 2023 | 241 observed dates | nominal|invalidation_before_midpoint_lower | 42.7% [35.7%, 48.4%] |
| NQ / magic_02 | 2023 | 241 observed dates | nominal|invalidation_before_midpoint_upper | 43.6% [36.6%, 49.2%] |
| NQ / magic_02 | 2023 | 241 observed dates | nominal|midpoint_before_invalidation_lower | 53.1% [47.3%, 60.1%] |
| NQ / magic_02 | 2023 | 241 observed dates | nominal|midpoint_before_invalidation_upper | 53.9% [48.1%, 60.8%] |
| NQ / magic_02 | 2023 | 241 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_02 | 2023 | 241 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_02 | 2024 | 222 / 252 | availability_delayed | break_then_neither_by_horizon: 10; future_censored: 1; invalidation_before_midpoint: 79; midpoint_before_invalidation: 132 |
| NQ / magic_02 | 2024 | 222 / 252 | nominal | break_then_neither_by_horizon: 10; future_censored: 1; invalidation_before_midpoint: 75; midpoint_before_invalidation: 136 |
| NQ / magic_02 | 2024 | 221 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 4.5% [2.2%, 7.3%] |
| NQ / magic_02 | 2024 | 221 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 4.5% [2.2%, 7.3%] |
| NQ / magic_02 | 2024 | 221 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.7% [29.9%, 42.8%] |
| NQ / magic_02 | 2024 | 221 observed dates | availability_delayed|invalidation_before_midpoint_upper | 35.7% [29.9%, 42.8%] |
| NQ / magic_02 | 2024 | 221 observed dates | availability_delayed|midpoint_before_invalidation_lower | 59.7% [52.6%, 65.7%] |
| NQ / magic_02 | 2024 | 221 observed dates | availability_delayed|midpoint_before_invalidation_upper | 59.7% [52.6%, 65.7%] |
| NQ / magic_02 | 2024 | 221 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_02 | 2024 | 221 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_02 | 2024 | 221 observed dates | nominal|break_then_neither_by_horizon_lower | 4.5% [2.2%, 7.3%] |
| NQ / magic_02 | 2024 | 221 observed dates | nominal|break_then_neither_by_horizon_upper | 4.5% [2.2%, 7.3%] |
| NQ / magic_02 | 2024 | 221 observed dates | nominal|invalidation_before_midpoint_lower | 33.9% [28.4%, 40.7%] |
| NQ / magic_02 | 2024 | 221 observed dates | nominal|invalidation_before_midpoint_upper | 33.9% [28.4%, 40.7%] |
| NQ / magic_02 | 2024 | 221 observed dates | nominal|midpoint_before_invalidation_lower | 61.5% [54.3%, 67.3%] |
| NQ / magic_02 | 2024 | 221 observed dates | nominal|midpoint_before_invalidation_upper | 61.5% [54.3%, 67.3%] |
| NQ / magic_02 | 2024 | 221 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_02 | 2024 | 221 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2020 | 242 / 253 | availability_delayed | break_then_neither_by_horizon: 7; competing_order_ambiguous: 1; future_censored: 3; invalidation_before_midpoint: 87; midpoint_before_invalidation: 144 |
| NQ / magic_06 | 2020 | 242 / 253 | nominal | break_then_neither_by_horizon: 7; competing_order_ambiguous: 1; future_censored: 3; invalidation_before_midpoint: 87; midpoint_before_invalidation: 144 |
| NQ / magic_06 | 2020 | 239 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.9% [1.2%, 5.0%] |
| NQ / magic_06 | 2020 | 239 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.9% [1.2%, 5.0%] |
| NQ / magic_06 | 2020 | 239 observed dates | availability_delayed|invalidation_before_midpoint_lower | 36.4% [30.3%, 42.3%] |
| NQ / magic_06 | 2020 | 239 observed dates | availability_delayed|invalidation_before_midpoint_upper | 36.8% [30.9%, 42.7%] |
| NQ / magic_06 | 2020 | 239 observed dates | availability_delayed|midpoint_before_invalidation_lower | 60.3% [54.5%, 66.2%] |
| NQ / magic_06 | 2020 | 239 observed dates | availability_delayed|midpoint_before_invalidation_upper | 60.7% [54.8%, 66.7%] |
| NQ / magic_06 | 2020 | 239 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2020 | 239 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2020 | 239 observed dates | nominal|break_then_neither_by_horizon_lower | 2.9% [1.2%, 5.0%] |
| NQ / magic_06 | 2020 | 239 observed dates | nominal|break_then_neither_by_horizon_upper | 2.9% [1.2%, 5.0%] |
| NQ / magic_06 | 2020 | 239 observed dates | nominal|invalidation_before_midpoint_lower | 36.4% [30.3%, 42.3%] |
| NQ / magic_06 | 2020 | 239 observed dates | nominal|invalidation_before_midpoint_upper | 36.8% [30.9%, 42.7%] |
| NQ / magic_06 | 2020 | 239 observed dates | nominal|midpoint_before_invalidation_lower | 60.3% [54.5%, 66.2%] |
| NQ / magic_06 | 2020 | 239 observed dates | nominal|midpoint_before_invalidation_upper | 60.7% [54.8%, 66.7%] |
| NQ / magic_06 | 2020 | 239 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2020 | 239 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2021 | 244 / 252 | availability_delayed | break_then_neither_by_horizon: 2; competing_order_ambiguous: 2; invalidation_before_midpoint: 91; midpoint_before_invalidation: 149 |
| NQ / magic_06 | 2021 | 244 / 252 | nominal | break_then_neither_by_horizon: 2; competing_order_ambiguous: 4; invalidation_before_midpoint: 85; midpoint_before_invalidation: 153 |
| NQ / magic_06 | 2021 | 244 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 0.8% [0.0%, 2.1%] |
| NQ / magic_06 | 2021 | 244 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 0.8% [0.0%, 2.1%] |
| NQ / magic_06 | 2021 | 244 observed dates | availability_delayed|invalidation_before_midpoint_lower | 37.3% [30.4%, 44.2%] |
| NQ / magic_06 | 2021 | 244 observed dates | availability_delayed|invalidation_before_midpoint_upper | 38.1% [31.2%, 45.3%] |
| NQ / magic_06 | 2021 | 244 observed dates | availability_delayed|midpoint_before_invalidation_lower | 61.1% [53.7%, 68.3%] |
| NQ / magic_06 | 2021 | 244 observed dates | availability_delayed|midpoint_before_invalidation_upper | 61.9% [54.6%, 68.9%] |
| NQ / magic_06 | 2021 | 244 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2021 | 244 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2021 | 244 observed dates | nominal|break_then_neither_by_horizon_lower | 0.8% [0.0%, 2.1%] |
| NQ / magic_06 | 2021 | 244 observed dates | nominal|break_then_neither_by_horizon_upper | 0.8% [0.0%, 2.1%] |
| NQ / magic_06 | 2021 | 244 observed dates | nominal|invalidation_before_midpoint_lower | 34.8% [28.0%, 42.0%] |
| NQ / magic_06 | 2021 | 244 observed dates | nominal|invalidation_before_midpoint_upper | 36.5% [29.3%, 43.9%] |
| NQ / magic_06 | 2021 | 244 observed dates | nominal|midpoint_before_invalidation_lower | 62.7% [55.3%, 69.9%] |
| NQ / magic_06 | 2021 | 244 observed dates | nominal|midpoint_before_invalidation_upper | 64.3% [57.0%, 71.3%] |
| NQ / magic_06 | 2021 | 244 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2021 | 244 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2022 | 246 / 251 | availability_delayed | break_then_neither_by_horizon: 4; competing_order_ambiguous: 5; first_side_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 86; midpoint_before_invalidation: 148 |
| NQ / magic_06 | 2022 | 246 / 251 | nominal | break_then_neither_by_horizon: 4; competing_order_ambiguous: 5; first_side_ambiguous: 1; future_censored: 2; invalidation_before_midpoint: 86; midpoint_before_invalidation: 148 |
| NQ / magic_06 | 2022 | 244 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 1.6% [0.4%, 3.3%] |
| NQ / magic_06 | 2022 | 244 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 1.6% [0.4%, 3.3%] |
| NQ / magic_06 | 2022 | 244 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.2% [30.0%, 39.7%] |
| NQ / magic_06 | 2022 | 244 observed dates | availability_delayed|invalidation_before_midpoint_upper | 37.7% [31.8%, 42.4%] |
| NQ / magic_06 | 2022 | 244 observed dates | availability_delayed|midpoint_before_invalidation_lower | 60.7% [55.7%, 66.4%] |
| NQ / magic_06 | 2022 | 244 observed dates | availability_delayed|midpoint_before_invalidation_upper | 63.1% [58.7%, 68.6%] |
| NQ / magic_06 | 2022 | 244 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2022 | 244 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2022 | 244 observed dates | nominal|break_then_neither_by_horizon_lower | 1.6% [0.4%, 3.3%] |
| NQ / magic_06 | 2022 | 244 observed dates | nominal|break_then_neither_by_horizon_upper | 1.6% [0.4%, 3.3%] |
| NQ / magic_06 | 2022 | 244 observed dates | nominal|invalidation_before_midpoint_lower | 35.2% [30.0%, 39.7%] |
| NQ / magic_06 | 2022 | 244 observed dates | nominal|invalidation_before_midpoint_upper | 37.7% [31.8%, 42.4%] |
| NQ / magic_06 | 2022 | 244 observed dates | nominal|midpoint_before_invalidation_lower | 60.7% [55.7%, 66.4%] |
| NQ / magic_06 | 2022 | 244 observed dates | nominal|midpoint_before_invalidation_upper | 63.1% [58.7%, 68.6%] |
| NQ / magic_06 | 2022 | 244 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2022 | 244 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2023 | 244 / 250 | availability_delayed | break_then_neither_by_horizon: 1; competing_order_ambiguous: 2; first_side_ambiguous: 1; future_censored: 1; invalidation_before_midpoint: 92; midpoint_before_invalidation: 147 |
| NQ / magic_06 | 2023 | 244 / 250 | nominal | break_then_neither_by_horizon: 1; competing_order_ambiguous: 2; first_side_ambiguous: 1; future_censored: 1; invalidation_before_midpoint: 92; midpoint_before_invalidation: 147 |
| NQ / magic_06 | 2023 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_06 | 2023 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_06 | 2023 | 243 observed dates | availability_delayed|invalidation_before_midpoint_lower | 37.9% [32.2%, 43.4%] |
| NQ / magic_06 | 2023 | 243 observed dates | availability_delayed|invalidation_before_midpoint_upper | 38.7% [32.8%, 44.5%] |
| NQ / magic_06 | 2023 | 243 observed dates | availability_delayed|midpoint_before_invalidation_lower | 60.9% [54.9%, 66.4%] |
| NQ / magic_06 | 2023 | 243 observed dates | availability_delayed|midpoint_before_invalidation_upper | 61.7% [56.1%, 67.4%] |
| NQ / magic_06 | 2023 | 243 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2023 | 243 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2023 | 243 observed dates | nominal|break_then_neither_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_06 | 2023 | 243 observed dates | nominal|break_then_neither_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_06 | 2023 | 243 observed dates | nominal|invalidation_before_midpoint_lower | 37.9% [32.2%, 43.4%] |
| NQ / magic_06 | 2023 | 243 observed dates | nominal|invalidation_before_midpoint_upper | 38.7% [32.8%, 44.5%] |
| NQ / magic_06 | 2023 | 243 observed dates | nominal|midpoint_before_invalidation_lower | 60.9% [54.9%, 66.4%] |
| NQ / magic_06 | 2023 | 243 observed dates | nominal|midpoint_before_invalidation_upper | 61.7% [56.1%, 67.4%] |
| NQ / magic_06 | 2023 | 243 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2023 | 243 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2024 | 223 / 252 | availability_delayed | break_then_neither_by_horizon: 3; competing_order_ambiguous: 2; first_side_ambiguous: 1; invalidation_before_midpoint: 79; midpoint_before_invalidation: 138 |
| NQ / magic_06 | 2024 | 223 / 252 | nominal | break_then_neither_by_horizon: 3; competing_order_ambiguous: 2; first_side_ambiguous: 1; invalidation_before_midpoint: 78; midpoint_before_invalidation: 139 |
| NQ / magic_06 | 2024 | 223 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 1.3% [0.0%, 2.5%] |
| NQ / magic_06 | 2024 | 223 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 1.3% [0.0%, 2.5%] |
| NQ / magic_06 | 2024 | 223 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.4% [29.2%, 41.2%] |
| NQ / magic_06 | 2024 | 223 observed dates | availability_delayed|invalidation_before_midpoint_upper | 36.3% [30.2%, 42.3%] |
| NQ / magic_06 | 2024 | 223 observed dates | availability_delayed|midpoint_before_invalidation_lower | 62.3% [56.4%, 69.1%] |
| NQ / magic_06 | 2024 | 223 observed dates | availability_delayed|midpoint_before_invalidation_upper | 63.2% [57.7%, 70.0%] |
| NQ / magic_06 | 2024 | 223 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2024 | 223 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2024 | 223 observed dates | nominal|break_then_neither_by_horizon_lower | 1.3% [0.0%, 2.5%] |
| NQ / magic_06 | 2024 | 223 observed dates | nominal|break_then_neither_by_horizon_upper | 1.3% [0.0%, 2.5%] |
| NQ / magic_06 | 2024 | 223 observed dates | nominal|invalidation_before_midpoint_lower | 35.0% [28.7%, 40.7%] |
| NQ / magic_06 | 2024 | 223 observed dates | nominal|invalidation_before_midpoint_upper | 35.9% [29.4%, 41.7%] |
| NQ / magic_06 | 2024 | 223 observed dates | nominal|midpoint_before_invalidation_lower | 62.8% [56.9%, 69.7%] |
| NQ / magic_06 | 2024 | 223 observed dates | nominal|midpoint_before_invalidation_upper | 63.7% [58.1%, 70.5%] |
| NQ / magic_06 | 2024 | 223 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_06 | 2024 | 223 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2020 | 243 / 253 | availability_delayed | break_then_neither_by_horizon: 4; future_censored: 1; invalidation_before_midpoint: 78; midpoint_before_invalidation: 160 |
| NQ / magic_07 | 2020 | 243 / 253 | nominal | break_then_neither_by_horizon: 4; future_censored: 1; invalidation_before_midpoint: 77; midpoint_before_invalidation: 161 |
| NQ / magic_07 | 2020 | 242 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 1.7% [0.4%, 3.3%] |
| NQ / magic_07 | 2020 | 242 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 1.7% [0.4%, 3.3%] |
| NQ / magic_07 | 2020 | 242 observed dates | availability_delayed|invalidation_before_midpoint_lower | 32.2% [25.9%, 37.6%] |
| NQ / magic_07 | 2020 | 242 observed dates | availability_delayed|invalidation_before_midpoint_upper | 32.2% [25.9%, 37.6%] |
| NQ / magic_07 | 2020 | 242 observed dates | availability_delayed|midpoint_before_invalidation_lower | 66.1% [61.1%, 72.2%] |
| NQ / magic_07 | 2020 | 242 observed dates | availability_delayed|midpoint_before_invalidation_upper | 66.1% [61.1%, 72.2%] |
| NQ / magic_07 | 2020 | 242 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2020 | 242 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2020 | 242 observed dates | nominal|break_then_neither_by_horizon_lower | 1.7% [0.4%, 3.3%] |
| NQ / magic_07 | 2020 | 242 observed dates | nominal|break_then_neither_by_horizon_upper | 1.7% [0.4%, 3.3%] |
| NQ / magic_07 | 2020 | 242 observed dates | nominal|invalidation_before_midpoint_lower | 31.8% [25.6%, 37.1%] |
| NQ / magic_07 | 2020 | 242 observed dates | nominal|invalidation_before_midpoint_upper | 31.8% [25.6%, 37.1%] |
| NQ / magic_07 | 2020 | 242 observed dates | nominal|midpoint_before_invalidation_lower | 66.5% [61.5%, 72.5%] |
| NQ / magic_07 | 2020 | 242 observed dates | nominal|midpoint_before_invalidation_upper | 66.5% [61.5%, 72.5%] |
| NQ / magic_07 | 2020 | 242 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2020 | 242 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2021 | 247 / 252 | availability_delayed | break_then_neither_by_horizon: 2; competing_order_ambiguous: 4; first_side_ambiguous: 1; invalidation_before_midpoint: 87; midpoint_before_invalidation: 153 |
| NQ / magic_07 | 2021 | 247 / 252 | nominal | break_then_neither_by_horizon: 2; competing_order_ambiguous: 4; first_side_ambiguous: 1; invalidation_before_midpoint: 85; midpoint_before_invalidation: 155 |
| NQ / magic_07 | 2021 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 0.8% [0.0%, 2.0%] |
| NQ / magic_07 | 2021 | 247 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 0.8% [0.0%, 2.0%] |
| NQ / magic_07 | 2021 | 247 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.2% [29.9%, 40.5%] |
| NQ / magic_07 | 2021 | 247 observed dates | availability_delayed|invalidation_before_midpoint_upper | 36.8% [31.3%, 42.2%] |
| NQ / magic_07 | 2021 | 247 observed dates | availability_delayed|midpoint_before_invalidation_lower | 62.3% [56.9%, 68.0%] |
| NQ / magic_07 | 2021 | 247 observed dates | availability_delayed|midpoint_before_invalidation_upper | 64.0% [58.6%, 69.4%] |
| NQ / magic_07 | 2021 | 247 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2021 | 247 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2021 | 247 observed dates | nominal|break_then_neither_by_horizon_lower | 0.8% [0.0%, 2.0%] |
| NQ / magic_07 | 2021 | 247 observed dates | nominal|break_then_neither_by_horizon_upper | 0.8% [0.0%, 2.0%] |
| NQ / magic_07 | 2021 | 247 observed dates | nominal|invalidation_before_midpoint_lower | 34.4% [29.4%, 40.2%] |
| NQ / magic_07 | 2021 | 247 observed dates | nominal|invalidation_before_midpoint_upper | 36.0% [30.9%, 41.8%] |
| NQ / magic_07 | 2021 | 247 observed dates | nominal|midpoint_before_invalidation_lower | 63.2% [57.3%, 68.4%] |
| NQ / magic_07 | 2021 | 247 observed dates | nominal|midpoint_before_invalidation_upper | 64.8% [59.0%, 69.8%] |
| NQ / magic_07 | 2021 | 247 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2021 | 247 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2022 | 246 / 251 | availability_delayed | break_then_neither_by_horizon: 1; competing_order_ambiguous: 7; first_side_ambiguous: 3; future_censored: 1; invalidation_before_midpoint: 88; midpoint_before_invalidation: 146 |
| NQ / magic_07 | 2022 | 246 / 251 | nominal | break_then_neither_by_horizon: 1; competing_order_ambiguous: 7; first_side_ambiguous: 3; future_censored: 1; invalidation_before_midpoint: 85; midpoint_before_invalidation: 149 |
| NQ / magic_07 | 2022 | 245 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| NQ / magic_07 | 2022 | 245 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| NQ / magic_07 | 2022 | 245 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.9% [29.4%, 40.9%] |
| NQ / magic_07 | 2022 | 245 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.6% [33.1%, 44.8%] |
| NQ / magic_07 | 2022 | 245 observed dates | availability_delayed|midpoint_before_invalidation_lower | 60.0% [54.6%, 66.3%] |
| NQ / magic_07 | 2022 | 245 observed dates | availability_delayed|midpoint_before_invalidation_upper | 63.7% [58.6%, 70.0%] |
| NQ / magic_07 | 2022 | 245 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2022 | 245 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2022 | 245 observed dates | nominal|break_then_neither_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| NQ / magic_07 | 2022 | 245 observed dates | nominal|break_then_neither_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| NQ / magic_07 | 2022 | 245 observed dates | nominal|invalidation_before_midpoint_lower | 34.7% [28.3%, 39.9%] |
| NQ / magic_07 | 2022 | 245 observed dates | nominal|invalidation_before_midpoint_upper | 38.4% [31.8%, 43.9%] |
| NQ / magic_07 | 2022 | 245 observed dates | nominal|midpoint_before_invalidation_lower | 61.2% [55.7%, 67.8%] |
| NQ / magic_07 | 2022 | 245 observed dates | nominal|midpoint_before_invalidation_upper | 64.9% [59.8%, 71.3%] |
| NQ / magic_07 | 2022 | 245 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2022 | 245 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2023 | 244 / 250 | availability_delayed | competing_order_ambiguous: 7; first_side_ambiguous: 4; future_censored: 1; invalidation_before_midpoint: 72; midpoint_before_invalidation: 160 |
| NQ / magic_07 | 2023 | 244 / 250 | nominal | competing_order_ambiguous: 7; first_side_ambiguous: 4; future_censored: 1; invalidation_before_midpoint: 70; midpoint_before_invalidation: 162 |
| NQ / magic_07 | 2023 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2023 | 243 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2023 | 243 observed dates | availability_delayed|invalidation_before_midpoint_lower | 29.6% [24.6%, 35.1%] |
| NQ / magic_07 | 2023 | 243 observed dates | availability_delayed|invalidation_before_midpoint_upper | 32.9% [27.8%, 38.5%] |
| NQ / magic_07 | 2023 | 243 observed dates | availability_delayed|midpoint_before_invalidation_lower | 67.1% [61.5%, 72.2%] |
| NQ / magic_07 | 2023 | 243 observed dates | availability_delayed|midpoint_before_invalidation_upper | 70.4% [64.9%, 75.4%] |
| NQ / magic_07 | 2023 | 243 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2023 | 243 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2023 | 243 observed dates | nominal|break_then_neither_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2023 | 243 observed dates | nominal|break_then_neither_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2023 | 243 observed dates | nominal|invalidation_before_midpoint_lower | 28.8% [23.8%, 34.3%] |
| NQ / magic_07 | 2023 | 243 observed dates | nominal|invalidation_before_midpoint_upper | 32.1% [27.3%, 37.6%] |
| NQ / magic_07 | 2023 | 243 observed dates | nominal|midpoint_before_invalidation_lower | 67.9% [62.4%, 72.7%] |
| NQ / magic_07 | 2023 | 243 observed dates | nominal|midpoint_before_invalidation_upper | 71.2% [65.7%, 76.2%] |
| NQ / magic_07 | 2023 | 243 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2023 | 243 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2024 | 224 / 252 | availability_delayed | break_then_neither_by_horizon: 1; competing_order_ambiguous: 14; first_side_ambiguous: 4; invalidation_before_midpoint: 71; midpoint_before_invalidation: 134 |
| NQ / magic_07 | 2024 | 224 / 252 | nominal | break_then_neither_by_horizon: 1; competing_order_ambiguous: 13; first_side_ambiguous: 4; invalidation_before_midpoint: 71; midpoint_before_invalidation: 135 |
| NQ / magic_07 | 2024 | 224 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 0.4% [0.0%, 0.9%] |
| NQ / magic_07 | 2024 | 224 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 0.4% [0.0%, 0.9%] |
| NQ / magic_07 | 2024 | 224 observed dates | availability_delayed|invalidation_before_midpoint_lower | 31.7% [25.9%, 37.1%] |
| NQ / magic_07 | 2024 | 224 observed dates | availability_delayed|invalidation_before_midpoint_upper | 38.8% [32.4%, 45.3%] |
| NQ / magic_07 | 2024 | 224 observed dates | availability_delayed|midpoint_before_invalidation_lower | 60.7% [54.4%, 67.4%] |
| NQ / magic_07 | 2024 | 224 observed dates | availability_delayed|midpoint_before_invalidation_upper | 67.9% [62.8%, 73.8%] |
| NQ / magic_07 | 2024 | 224 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2024 | 224 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2024 | 224 observed dates | nominal|break_then_neither_by_horizon_lower | 0.4% [0.0%, 0.9%] |
| NQ / magic_07 | 2024 | 224 observed dates | nominal|break_then_neither_by_horizon_upper | 0.4% [0.0%, 0.9%] |
| NQ / magic_07 | 2024 | 224 observed dates | nominal|invalidation_before_midpoint_lower | 31.7% [25.9%, 37.1%] |
| NQ / magic_07 | 2024 | 224 observed dates | nominal|invalidation_before_midpoint_upper | 38.4% [32.0%, 44.7%] |
| NQ / magic_07 | 2024 | 224 observed dates | nominal|midpoint_before_invalidation_lower | 61.2% [55.2%, 68.0%] |
| NQ / magic_07 | 2024 | 224 observed dates | nominal|midpoint_before_invalidation_upper | 67.9% [62.8%, 73.8%] |
| NQ / magic_07 | 2024 | 224 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_07 | 2024 | 224 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_08 | 2020 | 244 / 253 | availability_delayed | break_then_neither_by_horizon: 2; competing_order_ambiguous: 4; invalidation_before_midpoint: 93; midpoint_before_invalidation: 145 |
| NQ / magic_08 | 2020 | 244 / 253 | nominal | break_then_neither_by_horizon: 2; competing_order_ambiguous: 4; invalidation_before_midpoint: 93; midpoint_before_invalidation: 145 |
| NQ / magic_08 | 2020 | 244 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 0.8% [0.0%, 2.1%] |
| NQ / magic_08 | 2020 | 244 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 0.8% [0.0%, 2.1%] |
| NQ / magic_08 | 2020 | 244 observed dates | availability_delayed|invalidation_before_midpoint_lower | 38.1% [32.5%, 44.9%] |
| NQ / magic_08 | 2020 | 244 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.8% [34.3%, 46.5%] |
| NQ / magic_08 | 2020 | 244 observed dates | availability_delayed|midpoint_before_invalidation_lower | 59.4% [52.4%, 65.0%] |
| NQ / magic_08 | 2020 | 244 observed dates | availability_delayed|midpoint_before_invalidation_upper | 61.1% [54.3%, 66.7%] |
| NQ / magic_08 | 2020 | 244 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_08 | 2020 | 244 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_08 | 2020 | 244 observed dates | nominal|break_then_neither_by_horizon_lower | 0.8% [0.0%, 2.1%] |
| NQ / magic_08 | 2020 | 244 observed dates | nominal|break_then_neither_by_horizon_upper | 0.8% [0.0%, 2.1%] |
| NQ / magic_08 | 2020 | 244 observed dates | nominal|invalidation_before_midpoint_lower | 38.1% [32.5%, 44.9%] |
| NQ / magic_08 | 2020 | 244 observed dates | nominal|invalidation_before_midpoint_upper | 39.8% [34.3%, 46.5%] |
| NQ / magic_08 | 2020 | 244 observed dates | nominal|midpoint_before_invalidation_lower | 59.4% [52.4%, 65.0%] |
| NQ / magic_08 | 2020 | 244 observed dates | nominal|midpoint_before_invalidation_upper | 61.1% [54.3%, 66.7%] |
| NQ / magic_08 | 2020 | 244 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_08 | 2020 | 244 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_08 | 2021 | 248 / 252 | availability_delayed | break_then_neither_by_horizon: 8; competing_order_ambiguous: 7; invalidation_before_midpoint: 95; midpoint_before_invalidation: 137; no_break_by_horizon: 1 |
| NQ / magic_08 | 2021 | 248 / 252 | nominal | break_then_neither_by_horizon: 8; competing_order_ambiguous: 7; invalidation_before_midpoint: 93; midpoint_before_invalidation: 139; no_break_by_horizon: 1 |
| NQ / magic_08 | 2021 | 248 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.2% [1.2%, 6.0%] |
| NQ / magic_08 | 2021 | 248 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.2% [1.2%, 6.0%] |
| NQ / magic_08 | 2021 | 248 observed dates | availability_delayed|invalidation_before_midpoint_lower | 38.3% [31.4%, 43.4%] |
| NQ / magic_08 | 2021 | 248 observed dates | availability_delayed|invalidation_before_midpoint_upper | 41.1% [34.5%, 46.3%] |
| NQ / magic_08 | 2021 | 248 observed dates | availability_delayed|midpoint_before_invalidation_lower | 55.2% [50.0%, 61.8%] |
| NQ / magic_08 | 2021 | 248 observed dates | availability_delayed|midpoint_before_invalidation_upper | 58.1% [53.0%, 64.7%] |
| NQ / magic_08 | 2021 | 248 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| NQ / magic_08 | 2021 | 248 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| NQ / magic_08 | 2021 | 248 observed dates | nominal|break_then_neither_by_horizon_lower | 3.2% [1.2%, 6.0%] |
| NQ / magic_08 | 2021 | 248 observed dates | nominal|break_then_neither_by_horizon_upper | 3.2% [1.2%, 6.0%] |
| NQ / magic_08 | 2021 | 248 observed dates | nominal|invalidation_before_midpoint_lower | 37.5% [31.3%, 43.1%] |
| NQ / magic_08 | 2021 | 248 observed dates | nominal|invalidation_before_midpoint_upper | 40.3% [34.1%, 46.2%] |
| NQ / magic_08 | 2021 | 248 observed dates | nominal|midpoint_before_invalidation_lower | 56.0% [50.4%, 62.5%] |
| NQ / magic_08 | 2021 | 248 observed dates | nominal|midpoint_before_invalidation_upper | 58.9% [53.2%, 64.9%] |
| NQ / magic_08 | 2021 | 248 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.2%] |
| NQ / magic_08 | 2021 | 248 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.2%] |
| NQ / magic_08 | 2022 | 246 / 251 | availability_delayed | break_then_neither_by_horizon: 7; competing_order_ambiguous: 7; invalidation_before_midpoint: 92; midpoint_before_invalidation: 134; no_break_by_horizon: 6 |
| NQ / magic_08 | 2022 | 246 / 251 | nominal | break_then_neither_by_horizon: 7; competing_order_ambiguous: 7; invalidation_before_midpoint: 91; midpoint_before_invalidation: 135; no_break_by_horizon: 6 |
| NQ / magic_08 | 2022 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.8% [1.2%, 4.9%] |
| NQ / magic_08 | 2022 | 246 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.8% [1.2%, 4.9%] |
| NQ / magic_08 | 2022 | 246 observed dates | availability_delayed|invalidation_before_midpoint_lower | 37.4% [31.0%, 43.4%] |
| NQ / magic_08 | 2022 | 246 observed dates | availability_delayed|invalidation_before_midpoint_upper | 40.2% [34.3%, 46.2%] |
| NQ / magic_08 | 2022 | 246 observed dates | availability_delayed|midpoint_before_invalidation_lower | 54.5% [48.2%, 60.6%] |
| NQ / magic_08 | 2022 | 246 observed dates | availability_delayed|midpoint_before_invalidation_upper | 57.3% [51.0%, 63.4%] |
| NQ / magic_08 | 2022 | 246 observed dates | availability_delayed|no_break_by_horizon_lower | 2.4% [0.8%, 4.5%] |
| NQ / magic_08 | 2022 | 246 observed dates | availability_delayed|no_break_by_horizon_upper | 2.4% [0.8%, 4.5%] |
| NQ / magic_08 | 2022 | 246 observed dates | nominal|break_then_neither_by_horizon_lower | 2.8% [1.2%, 4.9%] |
| NQ / magic_08 | 2022 | 246 observed dates | nominal|break_then_neither_by_horizon_upper | 2.8% [1.2%, 4.9%] |
| NQ / magic_08 | 2022 | 246 observed dates | nominal|invalidation_before_midpoint_lower | 37.0% [30.6%, 42.9%] |
| NQ / magic_08 | 2022 | 246 observed dates | nominal|invalidation_before_midpoint_upper | 39.8% [34.2%, 45.7%] |
| NQ / magic_08 | 2022 | 246 observed dates | nominal|midpoint_before_invalidation_lower | 54.9% [48.6%, 60.7%] |
| NQ / magic_08 | 2022 | 246 observed dates | nominal|midpoint_before_invalidation_upper | 57.7% [51.4%, 63.8%] |
| NQ / magic_08 | 2022 | 246 observed dates | nominal|no_break_by_horizon_lower | 2.4% [0.8%, 4.5%] |
| NQ / magic_08 | 2022 | 246 observed dates | nominal|no_break_by_horizon_upper | 2.4% [0.8%, 4.5%] |
| NQ / magic_08 | 2023 | 244 / 250 | availability_delayed | break_then_neither_by_horizon: 7; competing_order_ambiguous: 7; invalidation_before_midpoint: 86; midpoint_before_invalidation: 144 |
| NQ / magic_08 | 2023 | 244 / 250 | nominal | break_then_neither_by_horizon: 7; competing_order_ambiguous: 7; invalidation_before_midpoint: 85; midpoint_before_invalidation: 145 |
| NQ / magic_08 | 2023 | 244 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.9% [0.8%, 5.3%] |
| NQ / magic_08 | 2023 | 244 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.9% [0.8%, 5.3%] |
| NQ / magic_08 | 2023 | 244 observed dates | availability_delayed|invalidation_before_midpoint_lower | 35.2% [29.9%, 41.3%] |
| NQ / magic_08 | 2023 | 244 observed dates | availability_delayed|invalidation_before_midpoint_upper | 38.1% [32.5%, 44.3%] |
| NQ / magic_08 | 2023 | 244 observed dates | availability_delayed|midpoint_before_invalidation_lower | 59.0% [52.8%, 65.0%] |
| NQ / magic_08 | 2023 | 244 observed dates | availability_delayed|midpoint_before_invalidation_upper | 61.9% [55.5%, 67.6%] |
| NQ / magic_08 | 2023 | 244 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_08 | 2023 | 244 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_08 | 2023 | 244 observed dates | nominal|break_then_neither_by_horizon_lower | 2.9% [0.8%, 5.3%] |
| NQ / magic_08 | 2023 | 244 observed dates | nominal|break_then_neither_by_horizon_upper | 2.9% [0.8%, 5.3%] |
| NQ / magic_08 | 2023 | 244 observed dates | nominal|invalidation_before_midpoint_lower | 34.8% [29.5%, 41.0%] |
| NQ / magic_08 | 2023 | 244 observed dates | nominal|invalidation_before_midpoint_upper | 37.7% [32.1%, 43.8%] |
| NQ / magic_08 | 2023 | 244 observed dates | nominal|midpoint_before_invalidation_lower | 59.4% [53.1%, 65.4%] |
| NQ / magic_08 | 2023 | 244 observed dates | nominal|midpoint_before_invalidation_upper | 62.3% [56.0%, 68.3%] |
| NQ / magic_08 | 2023 | 244 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_08 | 2023 | 244 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_08 | 2024 | 225 / 252 | availability_delayed | break_then_neither_by_horizon: 6; competing_order_ambiguous: 1; invalidation_before_midpoint: 90; midpoint_before_invalidation: 126; no_break_by_horizon: 2 |
| NQ / magic_08 | 2024 | 225 / 252 | nominal | break_then_neither_by_horizon: 6; competing_order_ambiguous: 2; invalidation_before_midpoint: 87; midpoint_before_invalidation: 128; no_break_by_horizon: 2 |
| NQ / magic_08 | 2024 | 225 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.7% [0.8%, 5.4%] |
| NQ / magic_08 | 2024 | 225 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.7% [0.8%, 5.4%] |
| NQ / magic_08 | 2024 | 225 observed dates | availability_delayed|invalidation_before_midpoint_lower | 40.0% [34.1%, 45.9%] |
| NQ / magic_08 | 2024 | 225 observed dates | availability_delayed|invalidation_before_midpoint_upper | 40.4% [34.6%, 46.3%] |
| NQ / magic_08 | 2024 | 225 observed dates | availability_delayed|midpoint_before_invalidation_lower | 56.0% [49.5%, 62.3%] |
| NQ / magic_08 | 2024 | 225 observed dates | availability_delayed|midpoint_before_invalidation_upper | 56.4% [50.0%, 62.8%] |
| NQ / magic_08 | 2024 | 225 observed dates | availability_delayed|no_break_by_horizon_lower | 0.9% [0.0%, 2.2%] |
| NQ / magic_08 | 2024 | 225 observed dates | availability_delayed|no_break_by_horizon_upper | 0.9% [0.0%, 2.2%] |
| NQ / magic_08 | 2024 | 225 observed dates | nominal|break_then_neither_by_horizon_lower | 2.7% [0.8%, 5.4%] |
| NQ / magic_08 | 2024 | 225 observed dates | nominal|break_then_neither_by_horizon_upper | 2.7% [0.8%, 5.4%] |
| NQ / magic_08 | 2024 | 225 observed dates | nominal|invalidation_before_midpoint_lower | 38.7% [32.7%, 44.6%] |
| NQ / magic_08 | 2024 | 225 observed dates | nominal|invalidation_before_midpoint_upper | 39.6% [33.3%, 45.6%] |
| NQ / magic_08 | 2024 | 225 observed dates | nominal|midpoint_before_invalidation_lower | 56.9% [50.5%, 63.3%] |
| NQ / magic_08 | 2024 | 225 observed dates | nominal|midpoint_before_invalidation_upper | 57.8% [51.6%, 64.1%] |
| NQ / magic_08 | 2024 | 225 observed dates | nominal|no_break_by_horizon_lower | 0.9% [0.0%, 2.2%] |
| NQ / magic_08 | 2024 | 225 observed dates | nominal|no_break_by_horizon_upper | 0.9% [0.0%, 2.2%] |
| NQ / magic_23 | 2020 | 240 / 253 | availability_delayed | break_then_neither_by_horizon: 8; future_censored: 6; invalidation_before_midpoint: 100; midpoint_before_invalidation: 125; no_break_by_horizon: 1 |
| NQ / magic_23 | 2020 | 240 / 253 | nominal | break_then_neither_by_horizon: 8; future_censored: 6; invalidation_before_midpoint: 99; midpoint_before_invalidation: 126; no_break_by_horizon: 1 |
| NQ / magic_23 | 2020 | 234 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.4% [1.2%, 6.2%] |
| NQ / magic_23 | 2020 | 234 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.4% [1.2%, 6.2%] |
| NQ / magic_23 | 2020 | 234 observed dates | availability_delayed|invalidation_before_midpoint_lower | 42.7% [37.4%, 48.9%] |
| NQ / magic_23 | 2020 | 234 observed dates | availability_delayed|invalidation_before_midpoint_upper | 42.7% [37.4%, 48.9%] |
| NQ / magic_23 | 2020 | 234 observed dates | availability_delayed|midpoint_before_invalidation_lower | 53.4% [47.7%, 58.7%] |
| NQ / magic_23 | 2020 | 234 observed dates | availability_delayed|midpoint_before_invalidation_upper | 53.4% [47.7%, 58.7%] |
| NQ / magic_23 | 2020 | 234 observed dates | availability_delayed|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_23 | 2020 | 234 observed dates | availability_delayed|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_23 | 2020 | 234 observed dates | nominal|break_then_neither_by_horizon_lower | 3.4% [1.2%, 6.2%] |
| NQ / magic_23 | 2020 | 234 observed dates | nominal|break_then_neither_by_horizon_upper | 3.4% [1.2%, 6.2%] |
| NQ / magic_23 | 2020 | 234 observed dates | nominal|invalidation_before_midpoint_lower | 42.3% [37.1%, 48.3%] |
| NQ / magic_23 | 2020 | 234 observed dates | nominal|invalidation_before_midpoint_upper | 42.3% [37.1%, 48.3%] |
| NQ / magic_23 | 2020 | 234 observed dates | nominal|midpoint_before_invalidation_lower | 53.8% [48.1%, 59.0%] |
| NQ / magic_23 | 2020 | 234 observed dates | nominal|midpoint_before_invalidation_upper | 53.8% [48.1%, 59.0%] |
| NQ / magic_23 | 2020 | 234 observed dates | nominal|no_break_by_horizon_lower | 0.4% [0.0%, 1.3%] |
| NQ / magic_23 | 2020 | 234 observed dates | nominal|no_break_by_horizon_upper | 0.4% [0.0%, 1.3%] |
| NQ / magic_23 | 2021 | 236 / 252 | availability_delayed | break_then_neither_by_horizon: 9; future_censored: 13; invalidation_before_midpoint: 89; midpoint_before_invalidation: 122; no_break_by_horizon: 3 |
| NQ / magic_23 | 2021 | 236 / 252 | nominal | break_then_neither_by_horizon: 9; future_censored: 13; invalidation_before_midpoint: 88; midpoint_before_invalidation: 123; no_break_by_horizon: 3 |
| NQ / magic_23 | 2021 | 223 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 4.0% [1.4%, 6.5%] |
| NQ / magic_23 | 2021 | 223 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 4.0% [1.4%, 6.5%] |
| NQ / magic_23 | 2021 | 223 observed dates | availability_delayed|invalidation_before_midpoint_lower | 39.9% [34.1%, 46.7%] |
| NQ / magic_23 | 2021 | 223 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.9% [34.1%, 46.7%] |
| NQ / magic_23 | 2021 | 223 observed dates | availability_delayed|midpoint_before_invalidation_lower | 54.7% [48.1%, 61.3%] |
| NQ / magic_23 | 2021 | 223 observed dates | availability_delayed|midpoint_before_invalidation_upper | 54.7% [48.1%, 61.3%] |
| NQ / magic_23 | 2021 | 223 observed dates | availability_delayed|no_break_by_horizon_lower | 1.3% [0.0%, 2.8%] |
| NQ / magic_23 | 2021 | 223 observed dates | availability_delayed|no_break_by_horizon_upper | 1.3% [0.0%, 2.8%] |
| NQ / magic_23 | 2021 | 223 observed dates | nominal|break_then_neither_by_horizon_lower | 4.0% [1.4%, 6.5%] |
| NQ / magic_23 | 2021 | 223 observed dates | nominal|break_then_neither_by_horizon_upper | 4.0% [1.4%, 6.5%] |
| NQ / magic_23 | 2021 | 223 observed dates | nominal|invalidation_before_midpoint_lower | 39.5% [33.6%, 46.1%] |
| NQ / magic_23 | 2021 | 223 observed dates | nominal|invalidation_before_midpoint_upper | 39.5% [33.6%, 46.1%] |
| NQ / magic_23 | 2021 | 223 observed dates | nominal|midpoint_before_invalidation_lower | 55.2% [48.6%, 61.6%] |
| NQ / magic_23 | 2021 | 223 observed dates | nominal|midpoint_before_invalidation_upper | 55.2% [48.6%, 61.6%] |
| NQ / magic_23 | 2021 | 223 observed dates | nominal|no_break_by_horizon_lower | 1.3% [0.0%, 2.8%] |
| NQ / magic_23 | 2021 | 223 observed dates | nominal|no_break_by_horizon_upper | 1.3% [0.0%, 2.8%] |
| NQ / magic_23 | 2022 | 239 / 251 | availability_delayed | break_then_neither_by_horizon: 14; competing_order_ambiguous: 4; future_censored: 3; invalidation_before_midpoint: 82; midpoint_before_invalidation: 129; no_break_by_horizon: 7 |
| NQ / magic_23 | 2022 | 239 / 251 | nominal | break_then_neither_by_horizon: 14; competing_order_ambiguous: 4; future_censored: 3; invalidation_before_midpoint: 82; midpoint_before_invalidation: 129; no_break_by_horizon: 7 |
| NQ / magic_23 | 2022 | 236 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 5.9% [3.4%, 8.9%] |
| NQ / magic_23 | 2022 | 236 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 5.9% [3.4%, 8.9%] |
| NQ / magic_23 | 2022 | 236 observed dates | availability_delayed|invalidation_before_midpoint_lower | 34.7% [29.4%, 40.8%] |
| NQ / magic_23 | 2022 | 236 observed dates | availability_delayed|invalidation_before_midpoint_upper | 36.4% [30.7%, 42.7%] |
| NQ / magic_23 | 2022 | 236 observed dates | availability_delayed|midpoint_before_invalidation_lower | 54.7% [47.9%, 61.1%] |
| NQ / magic_23 | 2022 | 236 observed dates | availability_delayed|midpoint_before_invalidation_upper | 56.4% [49.4%, 62.7%] |
| NQ / magic_23 | 2022 | 236 observed dates | availability_delayed|no_break_by_horizon_lower | 3.0% [0.9%, 5.4%] |
| NQ / magic_23 | 2022 | 236 observed dates | availability_delayed|no_break_by_horizon_upper | 3.0% [0.9%, 5.4%] |
| NQ / magic_23 | 2022 | 236 observed dates | nominal|break_then_neither_by_horizon_lower | 5.9% [3.4%, 8.9%] |
| NQ / magic_23 | 2022 | 236 observed dates | nominal|break_then_neither_by_horizon_upper | 5.9% [3.4%, 8.9%] |
| NQ / magic_23 | 2022 | 236 observed dates | nominal|invalidation_before_midpoint_lower | 34.7% [29.4%, 40.8%] |
| NQ / magic_23 | 2022 | 236 observed dates | nominal|invalidation_before_midpoint_upper | 36.4% [30.7%, 42.7%] |
| NQ / magic_23 | 2022 | 236 observed dates | nominal|midpoint_before_invalidation_lower | 54.7% [47.9%, 61.1%] |
| NQ / magic_23 | 2022 | 236 observed dates | nominal|midpoint_before_invalidation_upper | 56.4% [49.4%, 62.7%] |
| NQ / magic_23 | 2022 | 236 observed dates | nominal|no_break_by_horizon_lower | 3.0% [0.9%, 5.4%] |
| NQ / magic_23 | 2022 | 236 observed dates | nominal|no_break_by_horizon_upper | 3.0% [0.9%, 5.4%] |
| NQ / magic_23 | 2023 | 234 / 250 | availability_delayed | break_then_neither_by_horizon: 8; competing_order_ambiguous: 1; future_censored: 10; invalidation_before_midpoint: 88; midpoint_before_invalidation: 127 |
| NQ / magic_23 | 2023 | 234 / 250 | nominal | break_then_neither_by_horizon: 8; competing_order_ambiguous: 1; future_censored: 10; invalidation_before_midpoint: 87; midpoint_before_invalidation: 128 |
| NQ / magic_23 | 2023 | 224 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 3.6% [1.7%, 6.1%] |
| NQ / magic_23 | 2023 | 224 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 3.6% [1.7%, 6.1%] |
| NQ / magic_23 | 2023 | 224 observed dates | availability_delayed|invalidation_before_midpoint_lower | 39.3% [33.0%, 45.8%] |
| NQ / magic_23 | 2023 | 224 observed dates | availability_delayed|invalidation_before_midpoint_upper | 39.7% [33.8%, 46.2%] |
| NQ / magic_23 | 2023 | 224 observed dates | availability_delayed|midpoint_before_invalidation_lower | 56.7% [50.7%, 62.4%] |
| NQ / magic_23 | 2023 | 224 observed dates | availability_delayed|midpoint_before_invalidation_upper | 57.1% [51.1%, 63.2%] |
| NQ / magic_23 | 2023 | 224 observed dates | availability_delayed|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_23 | 2023 | 224 observed dates | availability_delayed|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_23 | 2023 | 224 observed dates | nominal|break_then_neither_by_horizon_lower | 3.6% [1.7%, 6.1%] |
| NQ / magic_23 | 2023 | 224 observed dates | nominal|break_then_neither_by_horizon_upper | 3.6% [1.7%, 6.1%] |
| NQ / magic_23 | 2023 | 224 observed dates | nominal|invalidation_before_midpoint_lower | 38.8% [32.6%, 45.5%] |
| NQ / magic_23 | 2023 | 224 observed dates | nominal|invalidation_before_midpoint_upper | 39.3% [33.2%, 45.8%] |
| NQ / magic_23 | 2023 | 224 observed dates | nominal|midpoint_before_invalidation_lower | 57.1% [51.0%, 62.9%] |
| NQ / magic_23 | 2023 | 224 observed dates | nominal|midpoint_before_invalidation_upper | 57.6% [51.4%, 63.8%] |
| NQ / magic_23 | 2023 | 224 observed dates | nominal|no_break_by_horizon_lower | 0.0% [0.0%, 0.0%] |
| NQ / magic_23 | 2023 | 224 observed dates | nominal|no_break_by_horizon_upper | 0.0% [0.0%, 0.0%] |
| NQ / magic_23 | 2024 | 216 / 252 | availability_delayed | break_then_neither_by_horizon: 4; future_censored: 18; invalidation_before_midpoint: 93; midpoint_before_invalidation: 97; no_break_by_horizon: 4 |
| NQ / magic_23 | 2024 | 216 / 252 | nominal | break_then_neither_by_horizon: 4; future_censored: 18; invalidation_before_midpoint: 91; midpoint_before_invalidation: 99; no_break_by_horizon: 4 |
| NQ / magic_23 | 2024 | 198 observed dates | availability_delayed|break_then_neither_by_horizon_lower | 2.0% [0.5%, 4.0%] |
| NQ / magic_23 | 2024 | 198 observed dates | availability_delayed|break_then_neither_by_horizon_upper | 2.0% [0.5%, 4.0%] |
| NQ / magic_23 | 2024 | 198 observed dates | availability_delayed|invalidation_before_midpoint_lower | 47.0% [39.3%, 55.6%] |
| NQ / magic_23 | 2024 | 198 observed dates | availability_delayed|invalidation_before_midpoint_upper | 47.0% [39.3%, 55.6%] |
| NQ / magic_23 | 2024 | 198 observed dates | availability_delayed|midpoint_before_invalidation_lower | 49.0% [40.5%, 57.1%] |
| NQ / magic_23 | 2024 | 198 observed dates | availability_delayed|midpoint_before_invalidation_upper | 49.0% [40.5%, 57.1%] |
| NQ / magic_23 | 2024 | 198 observed dates | availability_delayed|no_break_by_horizon_lower | 2.0% [0.5%, 4.1%] |
| NQ / magic_23 | 2024 | 198 observed dates | availability_delayed|no_break_by_horizon_upper | 2.0% [0.5%, 4.1%] |
| NQ / magic_23 | 2024 | 198 observed dates | nominal|break_then_neither_by_horizon_lower | 2.0% [0.5%, 4.0%] |
| NQ / magic_23 | 2024 | 198 observed dates | nominal|break_then_neither_by_horizon_upper | 2.0% [0.5%, 4.0%] |
| NQ / magic_23 | 2024 | 198 observed dates | nominal|invalidation_before_midpoint_lower | 46.0% [38.4%, 54.3%] |
| NQ / magic_23 | 2024 | 198 observed dates | nominal|invalidation_before_midpoint_upper | 46.0% [38.4%, 54.3%] |
| NQ / magic_23 | 2024 | 198 observed dates | nominal|midpoint_before_invalidation_lower | 50.0% [41.4%, 58.2%] |
| NQ / magic_23 | 2024 | 198 observed dates | nominal|midpoint_before_invalidation_upper | 50.0% [41.4%, 58.2%] |
| NQ / magic_23 | 2024 | 198 observed dates | nominal|no_break_by_horizon_lower | 2.0% [0.5%, 4.1%] |
| NQ / magic_23 | 2024 | 198 observed dates | nominal|no_break_by_horizon_upper | 2.0% [0.5%, 4.1%] |

## What remains unresolved?

OHLC resolves neither arbitrary intraminute event order nor every exact trade contact. Compatible range intersection, a definite observed print, no contact and incomplete future observation remain distinct. Fixed raw-contract coordinates never span an unhandled roll. The original NQ2024 definition-conflict exclusions remain auditable; a source-supported supersession supplement, when available, reports its incremental population separately. Unpublished statistical-zone formulas, source chart-clock assumptions and trade-order or auction dependencies retain their exact unresolved status. The matched timing, independent Context and full Location results have their own linked outputs and acceptance decisions. No descriptive table establishes trading profitability.

## Reproducible evidence

- [ES 2020 tables and complete annual statistics](ES-2020-shard.json): statistics SHA256 `95e5969a305e6759e42baa3e5e98f67b1754ace6ac178ef018c437cf54cb5c2d`.
- [ES 2021 tables and complete annual statistics](ES-2021-shard.json): statistics SHA256 `f9d4dface8f5d246b10b228c51d86c525b4bdfb3766d9191a6d659ddf8630c88`.
- [ES 2022 tables and complete annual statistics](ES-2022-shard.json): statistics SHA256 `5ab541ff00f6c27eed3c6bfcc702d63debac2b601517f203da17240865170770`.
- [ES 2023 tables and complete annual statistics](ES-2023-shard.json): statistics SHA256 `e1f90ce9eec127ae29cf0047ed704d504068934dc5b0794f3af465b261e9831c`.
- [ES 2024 tables and complete annual statistics](ES-2024-shard.json): statistics SHA256 `a6171946f6caffd880a9816a0d42bb3e3407bca13f106e039e7117bc1e735ee7`.
- [NQ 2020 tables and complete annual statistics](NQ-2020-shard.json): statistics SHA256 `325083c6307df84f2b07835949a4fbfc5a495ddfb2111a99919381e5e5af72ae`.
- [NQ 2021 tables and complete annual statistics](NQ-2021-shard.json): statistics SHA256 `395c489cdc31ad3c9c7b48acd25b604dc43d1760a6d76a42429d61b322b75158`.
- [NQ 2022 tables and complete annual statistics](NQ-2022-shard.json): statistics SHA256 `93aa7e9f818f0d4b1e8d290a80c88a7fd52e6fc5e199c3536a90d134a393d538`.
- [NQ 2023 tables and complete annual statistics](NQ-2023-shard.json): statistics SHA256 `35d1b213dd1f3bc40d6aa27ffd730f240f663cf5cbc3defc0d5cda8c812f072a`.
- [NQ 2024 tables and complete annual statistics](NQ-2024-shard.json): statistics SHA256 `8451e55429054c118b61ef7add0eddc35e95b78fddd2a9e9738457a42b478435`.
- Explicit supplement: `exact per-row anchor and named range relationships`.

Reporter: `jumbo-question-report-v3`. Every published number above is derived from the linked actual annual reports.
