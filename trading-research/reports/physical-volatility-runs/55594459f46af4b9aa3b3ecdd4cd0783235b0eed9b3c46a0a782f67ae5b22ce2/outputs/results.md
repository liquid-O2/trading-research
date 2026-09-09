# Physical OHLC volatility measurements

Family `Research-Physical-OHLC-Volatility-acquired-v1` version `physical-ohlc-volatility-acquired-v1`. **family_complete is false.**
acquired-minute-ohlc-physical-volatility-measurement; not a Context forecast or Location evaluation.

## Scope and remaining limits

- Mode: `full`. Reused immutable pilot partitions: 1.
- Practical Garman–Klass is original eq. 19a; the full analytic estimator 19 is not computed.
- Yang–Zhang uses hosted-paper sample variance (ddof=1) and k=0.34/(1.34+(n+1)/(n-1)) on contiguous intended sessions; n does not shrink by dropping dates.
- Minute close RV is not tick RV, noise-robust RV, or jump classification.
- Remaining windows store extrema, terminal return and sampled RV. They do not claim first-passage order from OHLC.
- Daily VX/VIX, chain IV, Context fits and Location evaluation remain separate.

## Units

- Prices: raw-contract ticks (1 tick = 0.25 index point).
- Range: ticks, points, fraction of open, and ln(H/L).
- GK / Parkinson / Rogers–Satchell / YZ / RV: log-return squared. Mean-per-interval and accumulated sum are distinct and are not annualized.

## Output tables

- `session-measurements.parquet` (10812 rows, 1431028 bytes, SHA-256 `135723e50b692819c5d04e32291cf9a765dcc59983080d87a4f52aec73a32818`): physical_ohlc_session_measurements_v1.
- `history-windows.parquet` (64872 rows, 4855973 bytes, SHA-256 `8058cd1accb32a77a12b18e6eca66e8862079ae629719738277c0cfa2a2005df`): physical_ohlc_history_windows_v1.
- `scale-aggregates.parquet` (14416 rows, 2383559 bytes, SHA-256 `d80e8f604bd9eae92bff40b010718656f32f6dcf6206331bec9911ec553f0db0`): physical_ohlc_scale_aggregates_v1.
- `seasonal-cells.parquet` (46690 rows, 3267599 bytes, SHA-256 `c87175ae755b2a27009a7b5f0e1de0e2fa5d9c185fbe24e2c0e695228753e122`): physical_ohlc_seasonal_cells_v1.
- `remaining-windows.parquet` (86496 rows, 14484702 bytes, SHA-256 `c271cf5f2bb193c2fa41de983f32a2de335f2fc6d5329fb806eb0af6918b9396`): physical_ohlc_remaining_windows_v1.
- `statistics.json` (n/a rows, 5899348 bytes, SHA-256 `9fea3c72183ec885a97f9ea6049ad7757e0ea7204d02144364ed15f32ed1dba9`): physical_ohlc_volatility_statistics_v1.

## Counts

- session_rows: 10812
- history_rows: 64872
- scale_rows: 14416
- seasonal_rows: 46690
- remaining_rows: 86496
- partitions_computed: 14
- partitions_reused: 1
- intended_date_groups: 15
- expected_primary_cash_dates_per_root: 1676
- expected_original_nq2024_dates: 252
- expected_pilot_dates: 253
- population_cash_dates: 1676
- partitions_in_protocol: 15
- partitions_seen: 15
- pilot_dates: 253
- original_nq2024_dates: 252

## Date-block means (equal intended-date universe)

### root=NQ|year=2020|stage=training|session=cash_rth|variant=primary_corrected
- Parkinson: 0.00020021002 log-return² date-block mean, 95% [0.00014815319, 0.00027138494]; 243 valid dates / 253 intended
- Garman–Klass 19a: 0.00020597513 log-return² date-block mean, 95% [0.00014722377, 0.00028096198]; 243 valid dates / 253 intended
- Rogers–Satchell: 0.0002148032 log-return² date-block mean, 95% [0.00015013464, 0.00029901984]; 243 valid dates / 253 intended

### root=NQ|year=2021|stage=training|session=cash_rth|variant=primary_corrected
- Parkinson: 8.5807685e-05 log-return² date-block mean, 95% [6.8160753e-05, 0.00010678736]; 248 valid dates / 252 intended
- Garman–Klass 19a: 8.5395556e-05 log-return² date-block mean, 95% [6.7266451e-05, 0.00010582722]; 248 valid dates / 252 intended
- Rogers–Satchell: 8.609491e-05 log-return² date-block mean, 95% [6.7191309e-05, 0.00010832568]; 248 valid dates / 252 intended

### root=NQ|year=2022|stage=training|session=cash_rth|variant=primary_corrected
- Parkinson: 0.00024802237 log-return² date-block mean, 95% [0.00021695947, 0.00028533582]; 247 valid dates / 251 intended
- Garman–Klass 19a: 0.00023014679 log-return² date-block mean, 95% [0.00020116454, 0.00026507669]; 247 valid dates / 251 intended
- Rogers–Satchell: 0.00022044838 log-return² date-block mean, 95% [0.00019153807, 0.00025703765]; 247 valid dates / 251 intended

### root=NQ|year=2023|stage=development|session=cash_rth|variant=primary_corrected
- Parkinson: 8.8106237e-05 log-return² date-block mean, 95% [7.3019691e-05, 0.00010238907]; 246 valid dates / 250 intended
- Garman–Klass 19a: 8.5219834e-05 log-return² date-block mean, 95% [6.987908e-05, 9.8420398e-05]; 246 valid dates / 250 intended
- Rogers–Satchell: 8.3434343e-05 log-return² date-block mean, 95% [6.7423764e-05, 9.7403067e-05]; 246 valid dates / 250 intended

### root=NQ|year=2024|stage=development|session=cash_rth|variant=primary_corrected
- Parkinson: 7.5240722e-05 log-return² date-block mean, 95% [6.1196612e-05, 9.2306845e-05]; 248 valid dates / 252 intended
- Garman–Klass 19a: 7.3813573e-05 log-return² date-block mean, 95% [5.9755466e-05, 9.0367274e-05]; 248 valid dates / 252 intended
- Rogers–Satchell: 7.4329697e-05 log-return² date-block mean, 95% [6.0107249e-05, 9.0648233e-05]; 248 valid dates / 252 intended

### root=NQ|year=2025|stage=confirmation|session=cash_rth|variant=primary_corrected
- Parkinson: 0.00013537268 log-return² date-block mean, 95% [7.3750614e-05, 0.00024462162]; 245 valid dates / 250 intended
- Garman–Klass 19a: 0.0001253671 log-return² date-block mean, 95% [7.3473747e-05, 0.00021523434]; 245 valid dates / 250 intended
- Rogers–Satchell: 0.0001190375 log-return² date-block mean, 95% [7.3051867e-05, 0.00019697144]; 245 valid dates / 250 intended

### root=NQ|year=2026|stage=confirmation|session=cash_rth|variant=primary_corrected
- Parkinson: 9.7081281e-05 log-return² date-block mean, 95% [7.5800122e-05, 0.00012498579]; 157 valid dates / 168 intended
- Garman–Klass 19a: 0.00010024886 log-return² date-block mean, 95% [7.8174907e-05, 0.00013144752]; 157 valid dates / 168 intended
- Rogers–Satchell: 0.00010216097 log-return² date-block mean, 95% [7.7849801e-05, 0.00013891899]; 157 valid dates / 168 intended

### root=ES|year=2020|stage=training|session=cash_rth|variant=primary_corrected
- Parkinson: 0.00015451836 log-return² date-block mean, 95% [9.7805866e-05, 0.00022782275]; 245 valid dates / 253 intended
- Garman–Klass 19a: 0.0001601288 log-return² date-block mean, 95% [9.8955712e-05, 0.0002393615]; 245 valid dates / 253 intended
- Rogers–Satchell: 0.00016813128 log-return² date-block mean, 95% [0.00010097689, 0.00025426949]; 245 valid dates / 253 intended

### root=ES|year=2021|stage=training|session=cash_rth|variant=primary_corrected
- Parkinson: 4.2939382e-05 log-return² date-block mean, 95% [3.2554732e-05, 5.3311277e-05]; 248 valid dates / 252 intended
- Garman–Klass 19a: 4.3732372e-05 log-return² date-block mean, 95% [3.2827423e-05, 5.547135e-05]; 248 valid dates / 252 intended
- Rogers–Satchell: 4.4968024e-05 log-return² date-block mean, 95% [3.3439283e-05, 5.7272211e-05]; 248 valid dates / 252 intended

### root=ES|year=2022|stage=training|session=cash_rth|variant=primary_corrected
- Parkinson: 0.00014200365 log-return² date-block mean, 95% [0.00012144586, 0.00016560604]; 247 valid dates / 251 intended
- Garman–Klass 19a: 0.00013481874 log-return² date-block mean, 95% [0.00011601236, 0.00015706069]; 247 valid dates / 251 intended
- Rogers–Satchell: 0.00013095599 log-return² date-block mean, 95% [0.00011123098, 0.0001561529]; 247 valid dates / 251 intended

### root=ES|year=2023|stage=development|session=cash_rth|variant=primary_corrected
- Parkinson: 4.8130901e-05 log-return² date-block mean, 95% [3.837046e-05, 5.7253598e-05]; 246 valid dates / 250 intended
- Garman–Klass 19a: 4.7079331e-05 log-return² date-block mean, 95% [3.7446195e-05, 5.5938428e-05]; 246 valid dates / 250 intended
- Rogers–Satchell: 4.6021706e-05 log-return² date-block mean, 95% [3.6475373e-05, 5.4850399e-05]; 246 valid dates / 250 intended

### root=ES|year=2024|stage=development|session=cash_rth|variant=primary_corrected
- Parkinson: 3.8292816e-05 log-return² date-block mean, 95% [3.0804258e-05, 4.7043742e-05]; 248 valid dates / 252 intended
- Garman–Klass 19a: 3.8841205e-05 log-return² date-block mean, 95% [3.0860548e-05, 4.7497171e-05]; 248 valid dates / 252 intended
- Rogers–Satchell: 4.0309587e-05 log-return² date-block mean, 95% [3.1509018e-05, 4.9827582e-05]; 248 valid dates / 252 intended

### root=ES|year=2025|stage=confirmation|session=cash_rth|variant=primary_corrected
- Parkinson: 9.0897044e-05 log-return² date-block mean, 95% [4.417347e-05, 0.00017464639]; 245 valid dates / 250 intended
- Garman–Klass 19a: 8.3968523e-05 log-return² date-block mean, 95% [4.5054859e-05, 0.00015161893]; 245 valid dates / 250 intended
- Rogers–Satchell: 7.9002459e-05 log-return² date-block mean, 95% [4.4858523e-05, 0.00013773432]; 245 valid dates / 250 intended

### root=ES|year=2026|stage=confirmation|session=cash_rth|variant=primary_corrected
- Parkinson: 4.4413153e-05 log-return² date-block mean, 95% [3.5416911e-05, 5.6061001e-05]; 162 valid dates / 168 intended
- Garman–Klass 19a: 4.6106537e-05 log-return² date-block mean, 95% [3.6753976e-05, 5.7999601e-05]; 162 valid dates / 168 intended
- Rogers–Satchell: 4.6471225e-05 log-return² date-block mean, 95% [3.6246273e-05, 6.0371504e-05]; 162 valid dates / 168 intended

## Original versus primary NQ 2024

The original acquisition is a same-calendar sensitivity, not an independent sample.
- Both present: 252; primary only: 0; original only: 0.
- GK original minus primary: 0 log-return² date-block mean, 95% [0, 0]; 225 valid dates / 252 intended

## Internal suite

- tests=34 passed=True failures=0 errors=0

## Dispositions retained

Missing input, invalid OHLC, negative unclipped GK, warmup, roll (previous close NULL), short sessions, unknown missing bars, not-applicable remaining cuts, and stage-purged labels remain as rows.

