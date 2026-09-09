# Physical OHLC volatility measurements

Family `Research-Physical-OHLC-Volatility-acquired-v1` version `physical-ohlc-volatility-acquired-v1`. **family_complete is false.**
acquired-minute-ohlc-physical-volatility-measurement; not a Context forecast or Location evaluation.

## Scope and remaining limits

- Mode: `pilot`. Reused immutable pilot partitions: 0.
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

- `session-measurements.parquet` (759 rows, 120038 bytes, SHA-256 `1325d31de8a1e12f1747916f379612404f5cea15fb00b1572156de4722fc31a1`): physical_ohlc_session_measurements_v1.
- `history-windows.parquet` (4554 rows, 311399 bytes, SHA-256 `ef8e3537b8d375bf1855e8e20684d4ef4087b79db9bebd4f6118c863d3c2558e`): physical_ohlc_history_windows_v1.
- `scale-aggregates.parquet` (1012 rows, 195938 bytes, SHA-256 `a8b36d2c12a3705e5d73bf78478f4042ae5631e6d7883f8d68d15f542393395c`): physical_ohlc_scale_aggregates_v1.
- `seasonal-cells.parquet` (3277 rows, 280403 bytes, SHA-256 `1450c18b0d449889ae29d03532f6b66b1aa58217bce607a5e4f80ff962a2bb49`): physical_ohlc_seasonal_cells_v1.
- `remaining-windows.parquet` (6072 rows, 1087025 bytes, SHA-256 `e95d7797d382d3e60d59b62f57c4a935bd4fae47e6390fdb7676cfe3c45a55ad`): physical_ohlc_remaining_windows_v1.
- `statistics.json` (n/a rows, 430879 bytes, SHA-256 `2cbd48b152faf1eb30e58be9daffad10a2df5fdd129bd2869c11dbefd2c41125`): physical_ohlc_volatility_statistics_v1.

## Counts

- session_rows: 759
- history_rows: 4554
- scale_rows: 1012
- seasonal_rows: 3277
- remaining_rows: 6072
- partitions_computed: 1
- partitions_reused: 0
- intended_date_groups: 1
- expected_primary_cash_dates_per_root: 1676
- expected_original_nq2024_dates: 252
- expected_pilot_dates: 253
- population_cash_dates: 1676
- partitions_in_protocol: 15
- partitions_seen: 1
- pilot_dates: 253
- original_nq2024_dates: 0

## Date-block means (equal intended-date universe)

### root=NQ|year=2020|stage=training|session=cash_rth|variant=primary_corrected
- Parkinson: 0.00020021002 log-return² date-block mean, 95% [0.00014815319, 0.00027138494]; 243 valid dates / 253 intended
- Garman–Klass 19a: 0.00020597513 log-return² date-block mean, 95% [0.00014722377, 0.00028096198]; 243 valid dates / 253 intended
- Rogers–Satchell: 0.0002148032 log-return² date-block mean, 95% [0.00015013464, 0.00029901984]; 243 valid dates / 253 intended

## Internal suite

- tests=34 passed=True failures=0 errors=0

## Dispositions retained

Missing input, invalid OHLC, negative unclipped GK, warmup, roll (previous close NULL), short sessions, unknown missing bars, not-applicable remaining cuts, and stage-purged labels remain as rows.

