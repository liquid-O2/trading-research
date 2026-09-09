# Daily VX/VIX complex measurement

This is the acquired daily branch only. It does not complete C16, does not replicate official VIX or VVIX,
does not interpolate variance, and does not fit Context or join NQ/ES.

## Definitions and units

- VX levels are futures prices in index points on the chosen price basis (`settlement` or `close`).
- DTE is calendar days `contract_expiration - trade_date`. Expiry-day DTE 0 is retained and excluded from the positive-time curve.
- Front/second rank distinct positive DTE within one duration-curve key. Spread is F2-F1. Ratio is F2/F1-1.
- A maturity-price conflict does not silently promote a remaining contract to front unless the curve is marked `partial_curve`.
- Constant 30/60/90 DTE values are linear **price** interpolation between nearest same-duration brackets, or the exact observed tenor.
- Same-contract changes require a unique finite positive level on both the current and previous intended cash date. Conflicts/nonpositive/nonfinite block the change.
- Index units are published index points and require finite positive levels. Combined FRED is a comparison copy.

## Clocks

- Every row is date-only: `known_at_ns` is null and `causal_feature_eligible` is false.
- FRED `realtime_start` / `realtime_end` vintages are retained in lineage; they are not pre-event availability.
- Expected next publication is unknown.

## Source identities

- Individual `VIX.parquet`, `VIX3M.parquet`, and `VXN.parquet` are FRED series, not independent Cboe histories.
- Those individual FRED files share the admitted 2026-09-03 `realtime_start` / `realtime_end` vintage with `fred-volatility.parquet`.
- `VVIX.parquet` is Cboe. Combined FRED is a comparison copy and does not add independent date support.

## Coverage

- Primary population: 2020-01-01 through 2026-09-03. Older acquired rows are counted and excluded from primary support.
- Intended cash dates: 1677.
- Acquired rows: 70755 (primary 35513, older 35242, after 0, outside intended cash 35646).
- Duration labels retained as observed: {'W': 8397, 'M': 14994}. Unexpected originals stay on separate curve keys: [].

## Individual vs combined FRED comparison

- Exact same-symbol/date comparison only. No merge or winner. Aliases do not add independent dates.

| symbol | individual_publisher | matched_valid | equal | different | primary_dates | not_independent |
|---|---|---|---|---|---|---|
| VIX | FRED | 9265 | 9265 | 0 | 9265 | True |
| VIX3M | FRED | 4716 | 4716 | 0 | 4716 | True |
| VXN | FRED | 6434 | 6434 | 0 | 6434 | True |
| VVIX | Cboe | 0 | 0 | 0 | 5096 | False |

## Date-mean and 95% block CI (all-period intended universe)

| metric | mean | ci_low | ci_high | valid_dates | missing_dates | support_dates | sparse |
|---|---|---|---|---|---|---|---|
| front | 21.29 | 20.62 | 21.93 | 1677 | 0 | 1677 | False |
| spread F2-F1 | 0.9791 | 0.812 | 1.142 | 1677 | 0 | 1677 | False |
| ratio F2/F1-1 | 0.0569 | 0.05085 | 0.06285 | 1677 | 0 | 1677 | False |
| F30 price | 21.76 | 21.1 | 22.37 | 1597 | 80 | 1597 | False |
| F60 price | 22.51 | 21.92 | 23.05 | 1677 | 0 | 1677 | False |
| F90 price | 22.87 | 22.33 | 23.36 | 1677 | 0 | 1677 | False |

## Chronological stages (training / development / confirmation)

Each stage uses only that stage's intended cash dates as the denominator.

| stage | metric | mean | ci_low | ci_high | valid_dates | missing_dates | support_dates | sparse |
|---|---|---|---|---|---|---|---|---|
| training | front | 25.34 | 24.33 | 26.45 | 756 | 0 | 756 | False |
| development | front | 16.82 | 16.25 | 17.33 | 502 | 0 | 502 | False |
| confirmation | front | 19.36 | 18.76 | 20.08 | 419 | 0 | 419 | False |
| training | spread F2-F1 | 1.079 | 0.7621 | 1.384 | 756 | 0 | 756 | False |
| development | spread F2-F1 | 0.9297 | 0.786 | 1.072 | 502 | 0 | 502 | False |
| confirmation | spread F2-F1 | 0.858 | 0.5638 | 1.109 | 419 | 0 | 419 | False |
| training | ratio F2/F1-1 | 0.05702 | 0.04649 | 0.06653 | 756 | 0 | 756 | False |
| development | ratio F2/F1-1 | 0.05996 | 0.05107 | 0.06881 | 502 | 0 | 502 | False |
| confirmation | ratio F2/F1-1 | 0.05301 | 0.03954 | 0.06502 | 419 | 0 | 419 | False |
| training | F30 price | 25.87 | 24.95 | 26.92 | 719 | 37 | 719 | False |
| development | F30 price | 17.25 | 16.7 | 17.75 | 475 | 27 | 475 | False |
| confirmation | F30 price | 19.74 | 19.27 | 20.32 | 403 | 16 | 403 | False |
| training | F60 price | 26.57 | 25.81 | 27.4 | 756 | 0 | 756 | False |
| development | F60 price | 18.08 | 17.56 | 18.54 | 502 | 0 | 502 | False |
| confirmation | F60 price | 20.48 | 20.14 | 20.92 | 419 | 0 | 419 | False |
| training | F90 price | 26.74 | 26.09 | 27.42 | 756 | 0 | 756 | False |
| development | F90 price | 18.65 | 18.16 | 19.1 | 502 | 0 | 502 | False |
| confirmation | F90 price | 20.93 | 20.65 | 21.28 | 419 | 0 | 419 | False |

## Index levels and ratios (all-period, not pooled across publishers)

| metric | mean | ci_low | ci_high | valid_dates | missing_dates | support_dates | sparse |
|---|---|---|---|---|---|---|---|
| VIX | 20.76 | 19.96 | 21.52 | 1676 | 1 | 1676 | False |
| VIX3M/VIX-1 | 0.1231 | 0.1147 | 0.1318 | 1676 | 1 | 1676 | False |
| VXN/VIX-1 | 0.2402 | 0.228 | 0.2524 | 1676 | 1 | 1676 | False |
| VVIX | 103 | 101.2 | 104.9 | 1676 | 1 | 1676 | False |

## Equal-date distributions (all-period groups, not pooled aliases)

| group | weighting | intended | observed | missing | median | q05 | q95 |
|---|---|---|---|---|---|---|---|
| index|fred_comparison|FRED|all|all|vix3m_over_vix_minus_one | equal_date | 1677 | 1676 | 1 | 0.1309 | -0.01482 | 0.2481 |
| index|primary_individual|Cboe|all|all|vvix | equal_date | 1677 | 1676 | 1 | 100.7 | 79.95 | 133.1 |
| index|primary_individual|Cboe|all|all|vvix_change | equal_date | 1677 | 1675 | 2 | -0.31 | -8.507 | 9.402 |
| index|primary_individual|FRED|all|all|vix3m_over_vix_minus_one | equal_date | 1677 | 1676 | 1 | 0.1309 | -0.01482 | 0.2481 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|monthly|close|all|all|front_level | equal_date | 1677 | 1677 | 0 | 19.75 | 13.96 | 31.96 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|monthly|close|all|all|spread | equal_date | 1677 | 1677 | 0 | 1.12 | -1.162 | 2.6 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|monthly|close|all|all|tenor_30|interp | equal_date | 1677 | 1597 | 80 | 20.24 | 14.56 | 31.71 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|monthly|close|all|all|tenor_60|interp | equal_date | 1677 | 1677 | 0 | 21.33 | 15.54 | 31.75 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|monthly|close|all|all|tenor_90|interp | equal_date | 1677 | 1677 | 0 | 22.02 | 16.33 | 31.38 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|monthly|settlement|all|all|front_level | equal_date | 1677 | 1677 | 0 | 19.71 | 13.98 | 32.08 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|monthly|settlement|all|all|spread | equal_date | 1677 | 1677 | 0 | 1.148 | -1.16 | 2.627 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|monthly|settlement|all|all|tenor_30|interp | equal_date | 1677 | 1597 | 80 | 20.23 | 14.54 | 31.76 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|monthly|settlement|all|all|tenor_60|interp | equal_date | 1677 | 1677 | 0 | 21.33 | 15.53 | 31.73 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|monthly|settlement|all|all|tenor_90|interp | equal_date | 1677 | 1677 | 0 | 22 | 16.35 | 31.4 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|weekly|close|all|all|front_level | equal_date | 1677 | 971 | 706 | 21.45 | 14 | 33.42 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|weekly|close|all|all|spread | equal_date | 1677 | 559 | 1118 | 0.55 | -2.415 | 2.15 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|weekly|close|all|all|tenor_30|interp | equal_date | 1677 | 130 | 1547 | 25.01 | 15.8 | 35.24 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|weekly|settlement|all|all|front_level | equal_date | 1677 | 1677 | 0 | 19.38 | 13.65 | 32.39 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|weekly|settlement|all|all|spread | equal_date | 1677 | 1677 | 0 | 0.15 | -0.98 | 1.625 |
| vx|Cboe|free-sources/cboe__vx-futures__normalized/all-contracts.parquet|weekly|settlement|all|all|tenor_30|interp | equal_date | 1677 | 1677 | 0 | 20.32 | 14.73 | 31.92 |

## Counts and retained raw dispositions

- Curves: 6712 dispositions {'observed': 6005, 'no_chain': 707}
- Interpolations: 20136 reasons {'observed': 11716, 'missing_right': 6130, 'no_positive_curve': 2121, 'missing_left': 169}
- Contract changes: 46778 dispositions {'unique': 40038, 'alias': 4, 'nonpositive': 6736} gaps 8022
- Index observations: 47364 dispositions {'unique': 45926, 'missing': 1438} unused/conflict 1438
- Index relations: 23632
- Unit tests: 30 passed=True

Full grouped date-mean/CI tables and per-group distributions are in `date-statistics.json` and `distributions.json`.

## Exact result paths

- acquired_rows: `/workspace/trading-research/reports/daily-volatility-runs/703380e44e03117d4fe2a29bf09f0b8be5191ecc9612d84908ef2e111c5feaef/outputs/acquired-rows.parquet` sha256=9a9ec0b8f74a1a753abed1377bf7178dfc7498a80b3f02e21c3847024be04c54 bytes=824322
- vx_curves: `/workspace/trading-research/reports/daily-volatility-runs/703380e44e03117d4fe2a29bf09f0b8be5191ecc9612d84908ef2e111c5feaef/outputs/vx-curves.parquet` sha256=38bc0ddde9b17fdca0035d5d170a6a1c14d5bde63d07c15d0400400b3bbf7516 bytes=162085
- vx_interpolations: `/workspace/trading-research/reports/daily-volatility-runs/703380e44e03117d4fe2a29bf09f0b8be5191ecc9612d84908ef2e111c5feaef/outputs/vx-interpolations.parquet` sha256=f2828cd967548bd52346014bef0225106606ba8ecd664e15373b0e145627ba30 bytes=239597
- vx_changes: `/workspace/trading-research/reports/daily-volatility-runs/703380e44e03117d4fe2a29bf09f0b8be5191ecc9612d84908ef2e111c5feaef/outputs/vx-changes.parquet` sha256=ed6307b318ec343b914378a11e39357276de6b506fc630f89a2294083010c93c bytes=458469
- index_observations: `/workspace/trading-research/reports/daily-volatility-runs/703380e44e03117d4fe2a29bf09f0b8be5191ecc9612d84908ef2e111c5feaef/outputs/index-observations.parquet` sha256=d52b3e015ef15fe4f8a2c5718dae6015e13080f450d24bec929977af230ba3f9 bytes=188167
- index_relations: `/workspace/trading-research/reports/daily-volatility-runs/703380e44e03117d4fe2a29bf09f0b8be5191ecc9612d84908ef2e111c5feaef/outputs/index-relations.parquet` sha256=bd6d6b8687a86101db63e6d991d31bc117077a92b52108723bd4cbb83a5add50 bytes=392530
- population_counts: `/workspace/trading-research/reports/daily-volatility-runs/703380e44e03117d4fe2a29bf09f0b8be5191ecc9612d84908ef2e111c5feaef/outputs/population-counts.json` sha256=ee1274b743514cdaa5b7b0aeeb1e48b3a2c57a95dcdb47dda219ca5598a16947 bytes=2854
- source_comparison: `/workspace/trading-research/reports/daily-volatility-runs/703380e44e03117d4fe2a29bf09f0b8be5191ecc9612d84908ef2e111c5feaef/outputs/source-comparison.json` sha256=1895b4d4aeb455ccd2f03c4dbdac8c2ea7e48e973f222339799d0d8002efda73 bytes=1495
- distributions: `/workspace/trading-research/reports/daily-volatility-runs/703380e44e03117d4fe2a29bf09f0b8be5191ecc9612d84908ef2e111c5feaef/outputs/distributions.json` sha256=d2f64690db72a5956397fa55782155a9ba0ec976c2f523a329a0609226de63d9 bytes=235914
- date_statistics: `/workspace/trading-research/reports/daily-volatility-runs/703380e44e03117d4fe2a29bf09f0b8be5191ecc9612d84908ef2e111c5feaef/outputs/date-statistics.json` sha256=65351063b07059d665085f434181bcfc37b227551c9f77b6def8c25dc526192b bytes=415043

- Admission execution: `/workspace/trading-research/reports/daily-volatility-runs/bf2387e52d112c076b777a3e8a1c7382e0228c079ee87948725b47e2e48d955c/execution.json` sha256=a482118b979c828dc55d53a2ce95f766c7c3882815a578b97fde55dc185db3bb
- Cash calendar: `/workspace/trading-research/configs/cash-rth-calendar-research-v1.json` sha256=f069df0ccbb8318f1c675a05d9deed64ad681ebe1e47dd8573a6b18266665818

## Family status

- `family_complete` is false. This file reports the acquired daily measurement branch after actual data, not the full C16 parent.

