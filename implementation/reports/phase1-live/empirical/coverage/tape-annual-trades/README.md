# Empirical native coverage and frozen evaluation split

This report was selected from native Parquet metadata and timestamp/instrument columns. Outcome fields were not examined while choosing dates.

- schema: `phase1-empirical-coverage-v1`
- data root: `/workspace/data`
- canonical manifest: `manifests/files.parquet` sha256=`747bf7582cfca977c013f3686be8f6b518d1948e8e5bd6b5a20d3494525b4acd`
- frozen manifest: `phase1-empirical-coverage-v1:b8fac21d3b5b7735`
- selection frequency: `annual`; required-data policy: `filter`
- validation: `PASS`

## Native dimensions

root | dataset | status | files | rows | years | schema
--- | --- | --- | ---: | ---: | --- | ---
NQ | ohlcv_1m | available | 17 | 4695352 | 2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026 | t,o,h,l,c,v,instrument_id
NQ | ohlcv_1s | available | 17 | 127979940 | 2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023,2024,2025,2026 | t,o,h,l,c,v,instrument_id
NQ | trades | available | 262 | 470160602 | 2021,2022,2023,2024,2025,2026 | t,price,size,side,instrument_id,flags
NQ | mbp1 | available | 142 | 11536223348 | 2020,2021,2022,2023,2024,2025,2026 | t,action,side,price,size,bid_px,ask_px,bid_sz,ask_sz,instrument_id,flags
NQ | definition | available | 1 | 65 | 2010,2026 | root,continuous_symbol,instrument_id,raw_symbol,instrument_class,underlying,expiration,expiration_ts_utc,activation,activation_ts_utc,min_price_increment,min_lot_size,contract_multiplier,currency,first_bar_ms,first_bar_ts_utc,last_bar_ms,last_bar_ts_utc,bar_rows,first_definition_ns,first_definition_ts_utc,last_definition_ns,last_definition_ts_utc,definition_events

## Frozen selection

root | date | instrument | status | required data | lookback
--- | --- | --- | --- | --- | ---
NQ | 2021-09-01 | 828 | eligible | {"definition": "available", "ohlcv_1m": "available", "trades": "available"} | 62 calendar days
NQ | 2022-01-03 | 3541 | eligible | {"definition": "available", "ohlcv_1m": "available", "trades": "available"} | 62 calendar days
NQ | 2023-01-03 | 20631 | eligible | {"definition": "available", "ohlcv_1m": "available", "trades": "available"} | 62 calendar days
NQ | 2026-09-01 | 42004177 | eligible | {"definition": "available", "ohlcv_1m": "available", "trades": "available"} | 62 calendar days

## Exposure and limitations

- selected partitions: `4`
- excluded full-session candidates: `2801`
- input identity hash: `2e295ad02e23527f85fe6f2ae002b7d746ff0bca41083dcb524066bed324e4bf`
- previous exposure remains unknown; no untouched-sample claim is made.
- MBP-1 and standalone trades are represented as prior-weekday-RTH plus evaluation-session windows; they are not loaded during date selection.
- MNQ is absent from the acquired archive and is retained as an explicit missing root.

## Reproduction

```bash
PYTHONPATH=implementation/src python -m trading_research.research.method_pack.empirical_coverage freeze \
  --data-root /workspace/data \
  --output-dir /workspace/implementation/reports/phase1-live/empirical/coverage
```
