# Empirical native coverage and frozen evaluation split

This report was selected from native Parquet metadata and timestamp/instrument columns. Outcome fields were not examined while choosing dates.

- schema: `phase1-empirical-coverage-v1`
- data root: `/workspace/data`
- canonical manifest: `manifests/files.parquet` sha256=`747bf7582cfca977c013f3686be8f6b518d1948e8e5bd6b5a20d3494525b4acd`
- frozen manifest: `phase1-empirical-coverage-v1:7301d07a0d6759d8`
- selection frequency: `monthly`; required-data policy: `annotate`
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
NQ | 2010-09-07 | 26715 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2010-10-04 | 3088 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2010-11-01 | 3088 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2010-12-06 | 3088 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-01-03 | 93735 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-02-07 | 93735 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-03-07 | 93735 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-04-04 | 30668 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-05-02 | 30668 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-06-02 | 30668 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-07-05 | 56972 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-08-01 | 56972 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-09-06 | 56972 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-10-03 | 12038 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-11-07 | 12038 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2011-12-05 | 12038 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-01-03 | 8870 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-02-06 | 8870 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-03-05 | 8870 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-04-02 | 20924 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-05-07 | 20924 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-06-04 | 20924 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-07-02 | 57494 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-08-06 | 57494 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-09-04 | 57494 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-10-01 | 10016 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-11-01 | 10016 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2012-12-03 | 10016 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-01-02 | 36931 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-02-01 | 36931 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-03-01 | 36931 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-04-01 | 11518 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-05-01 | 11518 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-06-03 | 11518 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-07-01 | 17591 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-08-01 | 17591 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-09-03 | 17591 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-10-01 | 28499 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-11-01 | 28499 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2013-12-02 | 28499 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-01-02 | 382251 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-02-03 | 382251 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-03-03 | 382251 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-04-01 | 8223 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-05-01 | 8223 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-06-02 | 8223 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-07-01 | 83745 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-08-01 | 83745 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-09-02 | 83745 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-10-01 | 28097 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-11-03 | 28097 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2014-12-01 | 28097 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-01-02 | 50207 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-02-02 | 50207 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-03-02 | 50207 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-04-06 | 58385 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-05-01 | 58385 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-06-01 | 58385 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-07-02 | 2913 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-08-03 | 2913 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-09-01 | 2913 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-10-01 | 12809 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-11-02 | 12809 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2015-12-01 | 12809 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-01-04 | 49734 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-02-01 | 49734 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-03-01 | 49734 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-04-01 | 765 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-05-02 | 765 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-06-01 | 765 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-07-01 | 2563 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-08-01 | 2563 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-09-01 | 2563 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-10-03 | 2887 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-11-01 | 2887 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2016-12-01 | 2887 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-01-03 | 35888 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-02-01 | 35888 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-03-01 | 35888 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-04-03 | 6398 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-05-01 | 6398 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-06-01 | 6398 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-07-05 | 26054 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-08-01 | 26054 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-09-01 | 26054 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-10-02 | 15466 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-11-01 | 15466 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2017-12-01 | 15466 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-01-02 | 16210 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-02-01 | 16210 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-03-01 | 16210 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-04-02 | 23520 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-05-01 | 23520 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-06-01 | 23520 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-07-02 | 47511 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-08-01 | 47511 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-09-04 | 47511 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-10-01 | 16041 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-11-01 | 16041 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2018-12-03 | 16041 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-01-02 | 15657 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-02-01 | 15657 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-03-01 | 15657 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-04-01 | 9166 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-05-01 | 9166 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-06-03 | 9166 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-07-01 | 36742 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-08-01 | 36742 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-09-03 | 36742 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-10-01 | 15907 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-11-01 | 15907 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2019-12-02 | 15907 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-01-02 | 10204 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-02-03 | 10204 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-03-02 | 10204 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-04-01 | 16908 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-05-01 | 16908 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-06-01 | 16908 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-07-01 | 14028 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-08-03 | 14028 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-09-01 | 14028 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-10-01 | 16337 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-11-02 | 16337 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2020-12-01 | 16337 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-01-04 | 4378 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-02-01 | 4378 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-03-01 | 4378 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-04-01 | 2786 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-05-03 | 2786 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-06-01 | 2786 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-07-01 | 828 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-08-02 | 828 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-09-01 | 828 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-10-01 | 2770 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-11-01 | 2770 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2021-12-01 | 2770 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-01-03 | 3541 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-02-01 | 3541 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-03-01 | 3541 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-04-01 | 2895 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-05-02 | 2895 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-06-01 | 2895 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-07-01 | 10391 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-08-01 | 10391 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-09-01 | 10391 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-10-03 | 13613 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-11-01 | 13613 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2022-12-01 | 13613 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-01-03 | 20631 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-02-01 | 20631 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-03-01 | 20631 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-04-03 | 3522 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-05-01 | 3522 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-06-01 | 3522 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-07-05 | 2130 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-08-01 | 2130 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-09-01 | 2130 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-10-02 | 260937 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-11-01 | 260937 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2023-12-01 | 260937 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days
NQ | 2026-09-01 | 42004177 | eligible | {"definition": "available", "ohlcv_1m": "available"} | 62 calendar days

## Exposure and limitations

- selected partitions: `161`
- excluded full-session candidates: `643`
- input identity hash: `22d0478759881e54bb0aefa1827de3b77d4783039f532f6deb137d70363f029a`
- previous exposure remains unknown; no untouched-sample claim is made.
- MBP-1 and standalone trades are represented as prior-weekday-RTH plus evaluation-session windows; they are not loaded during date selection.
- MNQ is absent from the acquired archive and is retained as an explicit missing root.

## Reproduction

```bash
PYTHONPATH=implementation/src python -m trading_research.research.method_pack.empirical_coverage freeze \
  --data-root /workspace/data \
  --output-dir /workspace/implementation/reports/phase1-live/empirical/coverage
```
