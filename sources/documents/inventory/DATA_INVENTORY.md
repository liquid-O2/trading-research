# Acquired market data: complete planning inventory

Prepared 2026-09-06 from the acquisition manifests dated 2026-09-05. This is an inventory of stored data, not a request to fetch data or an instruction to a model.

## Summary

- Main RunPod folder: `/workspace/data`. R2 destination: `r2:data` (bucket `data`).
- 111 dataset folders; 80,198 inventoried files; 322,136,177,617 bytes (322.14 GB decimal). Known Parquet row counts total 37,031,891,942; DBN/other unknown counts are not included.
- Dataset location is `/workspace/data/<dataset ID>`. The previous `/workspace/r2-upload/data` location and source paths in older manifests are historical; obsolete source copies were removed.
- QuantPad is a route for vendor data, not a separate exchange. `databento/` means direct purchases; `quantpad/` means data acquired through QuantPad. `thetadata-opra/` is the separate ThetaData options acquisition.
- Raw acquisition files were not combined, resampled or adjusted during archival. File partition size (daily/monthly/yearly) does not change record granularity. Derived and normalized datasets are explicitly identified.
- Completeness below is the acquisition manifest status, not a fresh market-calendar or semantic-quality audit. During cleanup every inventoried file was checked for existence and exact recorded byte size. Do not infer gap-free coverage from the first and last date alone.

## How to read coverage and timestamps

`Observed` means recorded timestamp extrema where available. `Partitions` means first/last filename partition labels; the final partition label is NOT the exact final trading timestamp. Unrecorded coverage remains unknown, not assumed to run through today. Counts can include vendor metadata and empty markers.

MBP-1 = each top-of-book update, not one-minute bars. Trades = individual executions. Definition = instrument lifecycle/reference events. Statistics = vendor/exchange statistical events, potentially including settlement/OI; not an intraday quote series. `trade_quote` = trades paired with NBBO, not guaranteed precomputed buyer/seller labels.

ThetaData daily boards cover all strikes/expiries where stated. Intraday quotes and trades are scoped by DTE and strike range; ATM +/-10 is the current surface pass. Legacy ATM +/-3 subsets and QuantPad OPRA reference pulls overlap newer data and must not be double-counted. Listed strike counts are not a guaranteed percentage distance from spot.

Timestamp profiles used below:

- **continuous-roll-map-mixed-utc**: stored mixed int64 Unix epochs plus Arrow timestamps; unit milliseconds for bar/segment epoch fields; nanoseconds for definition epoch fields; timezone UTC in explicit Arrow timestamp companion fields; source timezone UTC; effective precision milliseconds for bar-derived fields; nanoseconds for definition-derived fields. Epoch values are retained and paired with explicit Arrow timestamp columns normalized to UTC. DST: not applicable after UTC normalization.
- **databento-dbn-ns-utc**: stored Databento Binary Encoding (DBN), Zstandard compressed; unit nanoseconds for DBN timestamp fields; timezone UTC in native DBN records; source timezone UTC; effective precision nanoseconds. Original Databento .dbn.zst files are byte-identical and unconverted. DST: not applicable after UTC normalization.
- **date-only**: stored Arrow date32 or source text date; unit days; timezone None; source timezone calendar date; effective precision one day. No intraday timestamp is implied by a date-only field. DST: not applicable.
- **mixed-free-source**: stored mixed Parquet, CSV, JSON, and HTML; unit source-specific; timezone UTC for explicit normalized timestamps; otherwise date-only; source timezone source-specific; see schema and dataset notes; effective precision source-specific. Raw source responses and normalized companions are separated by dataset. DST: source-specific.
- **quantpad-bar-ms-utc**: stored int64 Unix epoch; unit milliseconds; timezone UTC (integer epoch field is timezone-naive by type); source timezone UTC; effective precision milliseconds. QuantPad Arrow output retained without timestamp rewriting. DST: not applicable after UTC normalization.
- **quantpad-tick-ns-utc**: stored int64 Unix epoch; unit nanoseconds; timezone UTC (integer epoch fields are timezone-naive by type); source timezone UTC; effective precision nanoseconds. QuantPad Arrow output retained without timestamp rewriting. DST: not applicable after UTC normalization.
- **thetadata-ms-et-to-ns-utc**: stored Arrow timestamp[ns, tz=UTC]; unit nanoseconds; timezone UTC; source timezone America/New_York; effective precision milliseconds (the source terminal supplies milliseconds). ThetaData terminal strings with millisecond precision were converted during ingestion; no additional conversion is performed by this archive builder. DST: Source wall times were localized with the IANA America/New_York zone, ambiguous fall-back times choose the earliest occurrence, nonexistent spring-forward times become null, then values were converted to UTC..

For point-in-time models, use event/receive/availability semantics explicitly. A daily observation date does not prove the value was available at the session open; release calendars and revised macro series require separate look-ahead checks. Nanosecond storage width does not imply nanosecond measurement precision.

## Dataset inventory

### databento (16 datasets)

**`databento/cme__es-options-on-futures__definition`**

- ES.OPT | schema `definition` | instrument-definition events | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2020-01-01 to 2026-09-01. Scope: 2020 onward, full parent option chain. Venue/source: GLBX.MDP3.
- Storage: dbn.zst, json; 84 files; 298.09 MB; rows unknown; partitioning: vendor batch files, generally calendar month. Time: `databento-dbn-ns-utc`.

**`databento/cme__es-options-on-futures__ohlcv-1m`**

- ES.OPT | schema `ohlcv-1m` | one-minute OHLCV bars per option contract | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2020-01-01 to 2026-09-01. Scope: 2020 onward, full parent option chain. Venue/source: GLBX.MDP3.
- Storage: dbn.zst, json; 84 files; 100.86 MB; rows unknown; partitioning: vendor batch files, generally calendar month. Time: `databento-dbn-ns-utc`.

**`databento/cme__es-options-on-futures__statistics`**

- ES.OPT | schema `statistics` | exchange statistics events | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2020-01-01 to 2026-09-01. Scope: 2020 onward, full parent option chain. Venue/source: GLBX.MDP3.
- Storage: dbn.zst, json; 84 files; 5,754.65 MB; rows unknown; partitioning: vendor batch files, generally calendar month. Time: `databento-dbn-ns-utc`.

**`databento/cme__es-options-on-futures__trades`**

- ES.OPT | schema `trades` | individual trade events | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2020-01-01 to 2026-09-01. Scope: 2020 onward, full parent option chain. Venue/source: GLBX.MDP3.
- Storage: dbn.zst, json; 84 files; 317.18 MB; rows unknown; partitioning: vendor batch files, generally calendar month. Time: `databento-dbn-ns-utc`.

**`databento/cme__hg-futures__mbp-1`**

- HG | schema `mbp-1` | every top-of-book market-by-price update | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2021-01-01 to 2026-01-01. Scope: 2021 through the available 2026 endpoint. Venue/source: GLBX.MDP3.
- Storage: dbn.zst; 6 files; 13,666.67 MB; rows unknown; partitioning: calendar-year source files. Time: `databento-dbn-ns-utc`.

**`databento/cme__hg-futures__source-metadata`**

- HG | schema `manifest/metadata/conditions` | one acquisition record per source artifact | **complete**.
- Coverage: Observed timestamps not recorded. Scope: provenance for the matching MBP-1/trades archive. Venue/source: GLBX.MDP3.
- Storage: json; 3 files; 0.21 MB; rows unknown; partitioning: small JSON companions. Time: `databento-dbn-ns-utc`.

**`databento/cme__hg-futures__trades`**

- HG | schema `trades` | individual trade events | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2026-06-06 to 2026-06-06. Scope: available companion trade tape. Venue/source: GLBX.MDP3.
- Storage: dbn.zst; 1 files; 5.35 MB; rows unknown; partitioning: as acquired. Time: `databento-dbn-ns-utc`.

**`databento/cme__nkd-futures__mbp-1`**

- NKD | schema `mbp-1` | every top-of-book market-by-price update | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2021-01-01 to 2026-01-01. Scope: 2021 through the available 2026 endpoint. Venue/source: GLBX.MDP3.
- Storage: dbn.zst; 6 files; 8,146.66 MB; rows unknown; partitioning: calendar-year source files. Time: `databento-dbn-ns-utc`.

**`databento/cme__nkd-futures__source-metadata`**

- NKD | schema `manifest/metadata/conditions` | one acquisition record per source artifact | **complete**.
- Coverage: Observed timestamps not recorded. Scope: provenance for the matching MBP-1/trades archive. Venue/source: GLBX.MDP3.
- Storage: json; 3 files; 0.21 MB; rows unknown; partitioning: small JSON companions. Time: `databento-dbn-ns-utc`.

**`databento/cme__nkd-futures__trades`**

- NKD | schema `trades` | individual trade events | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2026-06-01 to 2026-06-01. Scope: available companion trade tape. Venue/source: GLBX.MDP3.
- Storage: dbn.zst; 1 files; 1.35 MB; rows unknown; partitioning: as acquired. Time: `databento-dbn-ns-utc`.

**`databento/cme__nq-options-on-futures__definition`**

- NQ.OPT | schema `definition` | instrument-definition events | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2020-01-01 to 2026-09-01. Scope: 2020 onward, full parent option chain. Venue/source: GLBX.MDP3.
- Storage: dbn.zst, json; 84 files; 43.86 MB; rows unknown; partitioning: vendor batch files, generally calendar month. Time: `databento-dbn-ns-utc`.

**`databento/cme__nq-options-on-futures__ohlcv-1m`**

- NQ.OPT | schema `ohlcv-1m` | one-minute OHLCV bars per option contract | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2020-01-01 to 2026-09-01. Scope: 2020 onward, full parent option chain. Venue/source: GLBX.MDP3.
- Storage: dbn.zst, json; 84 files; 22.87 MB; rows unknown; partitioning: vendor batch files, generally calendar month. Time: `databento-dbn-ns-utc`.

**`databento/cme__nq-options-on-futures__statistics`**

- NQ.OPT | schema `statistics` | exchange statistics events | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2020-01-01 to 2026-09-01. Scope: 2020 onward, full parent option chain. Venue/source: GLBX.MDP3.
- Storage: dbn.zst, json; 84 files; 4,105.19 MB; rows unknown; partitioning: vendor batch files, generally calendar month. Time: `databento-dbn-ns-utc`.

**`databento/cme__nq-options-on-futures__trades`**

- NQ.OPT | schema `trades` | individual trade events | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2020-01-01 to 2026-09-01. Scope: 2020 onward, full parent option chain. Venue/source: GLBX.MDP3.
- Storage: dbn.zst, json; 84 files; 53.23 MB; rows unknown; partitioning: vendor batch files, generally calendar month. Time: `databento-dbn-ns-utc`.

**`databento/cme__si-futures__mbp-1`**

- SI | schema `mbp-1` | every top-of-book market-by-price update | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2021-05-31 to 2026-05-29. Scope: 2021 through the available 2026 endpoint. Venue/source: GLBX.MDP3.
- Storage: dbn.zst; 1,565 files; 28,206.59 MB; rows unknown; partitioning: daily source files. Time: `databento-dbn-ns-utc`.

**`databento/cme__si-futures__source-metadata`**

- SI | schema `manifest/metadata/conditions` | one acquisition record per source artifact | **complete**.
- Coverage: Observed timestamps not recorded. Scope: provenance for the matching MBP-1/trades archive. Venue/source: GLBX.MDP3.
- Storage: json; 3 files; 0.97 MB; rows unknown; partitioning: small JSON companions. Time: `databento-dbn-ns-utc`.

### quantpad (26 datasets)

**`quantpad/cme__es-continuous-futures__definition`**

- ES.c.0 | schema `definition` | instrument-definition events | **complete**.
- Coverage: Observed 2010-09-05T00:00:00+00:00 to 2026-08-30T11:35:24.405359+00:00; partitions 2010 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 17 files; 10.81 MB; rows 4,127; partitioning: calendar year. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__es-continuous-futures__mbp-1`**

- ES.c.0 | schema `mbp-1` | every top-of-book market-by-price update | **partial-paused**.
- Coverage: Observed 2020-01-01T23:00:00+00:00 to 2024-08-30T21:00:00.064048+00:00; partitions 2020-01 to 2024-08. Scope: 2020 onward, continuous front contract. Venue/source: GLBX.MDP3.
- Storage: parquet; 25 files; 19,867.77 MB; rows 2,951,360,512; partitioning: calendar month. Time: `quantpad-tick-ns-utc`.
- Caveats: The six-year ES MBP-1 pull was intentionally paused; see computed missing_months.
- Missing months: 2020-11, 2021-01, 2021-02, 2021-03, 2021-04, 2021-05, 2021-06, 2021-07, 2021-08, 2021-09, 2021-10, 2021-11, 2021-12, 2022-01, 2022-02, 2022-03, 2022-04, 2022-05, 2022-06, 2022-07, 2022-08, 2022-09, 2022-10, 2022-11, 2022-12, 2023-01, 2023-02, 2023-03, 2023-04, 2023-05, 2023-06, 2024-09, 2024-10, 2024-11, 2024-12, 2025-01, 2025-02, 2025-03, 2025-04, 2025-05, 2025-06, 2025-07, 2025-08, 2025-09, 2025-10, 2025-11, 2025-12, 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07, 2026-08, 2026-09.

**`quantpad/cme__es-continuous-futures__ohlcv-1m`**

- ES.c.0 | schema `ohlcv-1m` | one-minute OHLCV bars | **complete**.
- Coverage: Observed 2010-09-06T15:20:00+00:00 to 2026-09-02T15:19:00+00:00; partitions 2010 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 17 files; 63.51 MB; rows 4,843,530; partitioning: calendar year. Time: `quantpad-bar-ms-utc`.

**`quantpad/cme__es-continuous-futures__statistics`**

- ES.c.0 | schema `statistics` | exchange statistics events, including settlement/open interest updates | **complete**.
- Coverage: Observed 2010-09-07T00:02:02.169000+00:00 to 2026-09-01T23:18:58.775715+00:00. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 1 files; 40.74 MB; rows 1,853,081; partitioning: calendar year. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__es-continuous-futures__trades`**

- ES.c.0 | schema `trades` | individual trade events | **complete**.
- Coverage: Observed 2020-01-01T23:00:00+00:00 to 2026-09-03T06:09:59.555968+00:00; partitions 2020 to 2026. Scope: 2020 onward, continuous front contract. Venue/source: GLBX.MDP3.
- Storage: parquet; 7 files; 4,454.48 MB; rows 705,089,126; partitioning: calendar month. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__nq-continuous-futures__definition`**

- NQ.c.0 | schema `definition` | instrument-definition events | **complete**.
- Coverage: Observed 2010-09-05T00:00:00+00:00 to 2026-08-30T11:35:54.177000+00:00; partitions 2010 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 17 files; 10.81 MB; rows 4,129; partitioning: calendar year. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__nq-continuous-futures__mbp-1`**

- NQ.c.0 | schema `mbp-1` | every top-of-book market-by-price update | **complete**.
- Coverage: Observed 2020-01-01T23:00:00+00:00 to 2026-09-03T06:09:59.901114+00:00; partitions 2019-12-30 to 2026-09. Scope: 2020 onward, continuous front contract. Venue/source: GLBX.MDP3.
- Storage: parquet; 142 files; 82,214.54 MB; rows 11,536,223,348; partitioning: calendar month. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__nq-continuous-futures__ohlcv-1m`**

- NQ.c.0 | schema `ohlcv-1m` | one-minute OHLCV bars | **complete**.
- Coverage: Observed 2010-09-06T15:20:00+00:00 to 2026-09-02T15:19:00+00:00; partitions 2010 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 17 files; 67.50 MB; rows 4,695,352; partitioning: calendar year. Time: `quantpad-bar-ms-utc`.

**`quantpad/cme__nq-continuous-futures__ohlcv-1s`**

- NQ.c.0 | schema `ohlcv-1s` | one-second OHLCV bars | **complete**.
- Coverage: Observed 2010-09-06T15:20:56+00:00 to 2026-09-02T15:19:59+00:00; partitions 2010 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 17 files; 1,238.80 MB; rows 127,979,940; partitioning: calendar year/month as acquired. Time: `quantpad-bar-ms-utc`.

**`quantpad/cme__nq-continuous-futures__statistics`**

- NQ.c.0 | schema `statistics` | exchange statistics events, including settlement/open interest updates | **complete**.
- Coverage: Observed 2010-09-06T15:30:23.316000+00:00 to 2026-09-01T23:21:22.580296+00:00. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 1 files; 75.32 MB; rows 3,835,892; partitioning: calendar year. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__nq-continuous-futures__trades`**

- NQ.c.0 | schema `trades` | individual trade events | **complete**.
- Coverage: Observed 2021-09-01T18:00:00.030617+00:00 to 2026-09-02T17:59:59.376719+00:00; partitions 2021-08-30 to 2026-08-31. Scope: 2020 onward, continuous front contract. Venue/source: GLBX.MDP3.
- Storage: parquet; 262 files; 3,571.25 MB; rows 470,160,602; partitioning: calendar month. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__rty-continuous-futures__definition`**

- RTY.c.0 | schema `definition` | instrument-definition events | **partial-skipped**.
- Coverage: Observed 2018-12-30T17:05:05.380000+00:00 to 2026-08-30T11:35:54.277000+00:00; partitions 2019 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 8 files; 5.19 MB; rows 1,981; partitioning: calendar year. Time: `quantpad-tick-ns-utc`.
- Caveats: RTY definition years 2010-2018 were intentionally skipped after repeated vendor read timeouts; 2019-2026 are retained.

**`quantpad/cme__rty-continuous-futures__ohlcv-1m`**

- RTY.c.0 | schema `ohlcv-1m` | one-minute OHLCV bars | **complete**.
- Coverage: Observed 2017-07-09T22:01:00+00:00 to 2026-09-02T15:19:00+00:00; partitions 2010 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 17 files; 39.74 MB; rows 2,941,815; partitioning: calendar year. Time: `quantpad-bar-ms-utc`.

**`quantpad/cme__rty-continuous-futures__statistics`**

- RTY.c.0 | schema `statistics` | exchange statistics events, including settlement/open interest updates | **complete**.
- Coverage: Observed 2017-06-05T23:33:50.523546+00:00 to 2026-09-01T23:21:03.702670+00:00; partitions 2010 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 17 files; 32.75 MB; rows 1,479,501; partitioning: calendar year. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__rty-continuous-futures__trades`**

- RTY.c.0 | schema `trades` | individual trade events | **complete**.
- Coverage: Observed 2020-01-01T23:00:00+00:00 to 2026-09-03T06:09:52.071934+00:00; partitions 2020 to 2026. Scope: 2020 onward, continuous front contract. Venue/source: GLBX.MDP3.
- Storage: parquet; 7 files; 1,418.21 MB; rows 159,978,160; partitioning: calendar month. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__ym-continuous-futures__definition`**

- YM.c.0 | schema `definition` | instrument-definition events | **complete**.
- Coverage: Observed 2010-09-05T00:00:00+00:00 to 2026-08-30T11:35:54.227000+00:00; partitions 2010 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 17 files; 10.81 MB; rows 4,127; partitioning: calendar year. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__ym-continuous-futures__ohlcv-1m`**

- YM.c.0 | schema `ohlcv-1m` | one-minute OHLCV bars | **complete**.
- Coverage: Observed 2010-09-06T15:21:00+00:00 to 2026-09-02T15:19:00+00:00; partitions 2010 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 17 files; 62.84 MB; rows 4,657,444; partitioning: calendar year. Time: `quantpad-bar-ms-utc`.

**`quantpad/cme__ym-continuous-futures__statistics`**

- YM.c.0 | schema `statistics` | exchange statistics events, including settlement/open interest updates | **complete**.
- Coverage: Observed 2010-09-07T01:21:21.543000+00:00 to 2026-09-01T23:21:13.023358+00:00; partitions 2010 to 2026. Scope: full available continuous-contract history. Venue/source: GLBX.MDP3.
- Storage: parquet; 17 files; 47.43 MB; rows 2,262,532; partitioning: calendar year. Time: `quantpad-tick-ns-utc`.

**`quantpad/cme__ym-continuous-futures__trades`**

- YM.c.0 | schema `trades` | individual trade events | **complete**.
- Coverage: Observed 2020-01-01T23:00:00+00:00 to 2026-09-03T06:09:44.925944+00:00; partitions 2020 to 2026. Scope: 2020 onward, continuous front contract. Venue/source: GLBX.MDP3.
- Storage: parquet; 7 files; 1,435.32 MB; rows 159,991,516; partitioning: calendar month. Time: `quantpad-tick-ns-utc`.

**`quantpad/nasdaq__qqq-etf__ohlcv-1m`**

- QQQ | schema `ohlcv-1m` | one-minute OHLCV bars | **complete**.
- Coverage: Observed 2018-09-05T13:30:00+00:00 to 2026-09-02T19:59:00+00:00; partitions 2018 to 2026. Scope: full available history from September 2018 onward. Venue/source: XNAS.ITCH.
- Storage: parquet; 9 files; 14.36 MB; rows 778,822; partitioning: calendar year. Time: `quantpad-bar-ms-utc`.

**`quantpad/nyse-arca__spy-etf__ohlcv-1m`**

- SPY | schema `ohlcv-1m` | one-minute OHLCV bars | **complete**.
- Coverage: Observed 2018-09-05T13:30:00+00:00 to 2026-09-01T19:59:00+00:00; partitions 2018 to 2026. Scope: full available history from September 2018 onward. Venue/source: ARCX.PILLAR.
- Storage: parquet; 9 files; 14.56 MB; rows 779,709; partitioning: calendar year. Time: `quantpad-bar-ms-utc`.

**`quantpad/opra__ndx-options__ohlcv-1d__reference`**

- NDX.OPT | schema `ohlcv-1d` | one-day OHLCV per contract | **reference-partial-superseded**.
- Coverage: Observed 2013-09-05T00:00:00+00:00 to 2026-09-01T00:00:00+00:00; partitions 2013 to 2026. Scope: partial reference pull; superseded by the ThetaData OPRA archive. Venue/source: OPRA.PILLAR.
- Storage: parquet; 14 files; 36.15 MB; rows 2,502,765; partitioning: calendar month. Time: `quantpad-bar-ms-utc`.

**`quantpad/opra__ndxp-options__ohlcv-1d__reference`**

- NDXP.OPT | schema `ohlcv-1d` | one-day OHLCV per contract | **reference-partial-superseded**.
- Coverage: Observed 2018-01-04T00:00:00+00:00 to 2026-09-01T00:00:00+00:00; partitions 2018 to 2026. Scope: partial reference pull; superseded by the ThetaData OPRA archive. Venue/source: OPRA.PILLAR.
- Storage: parquet; 9 files; 54.14 MB; rows 3,542,879; partitioning: calendar month. Time: `quantpad-bar-ms-utc`.

**`quantpad/opra__ndxp-options__statistics__reference`**

- NDXP.OPT | schema `statistics` | OPRA statistics events | **reference-partial-superseded**.
- Coverage: Observed 2020-01-02T14:31:00+00:00 to 2021-02-26T14:31:00+00:00; partitions 2020-01 to 2021-02. Scope: partial reference pull; superseded by the ThetaData OPRA archive. Venue/source: OPRA.PILLAR.
- Storage: parquet; 13 files; 8.42 MB; rows 1,557,732; partitioning: calendar month. Time: `quantpad-tick-ns-utc`.

**`quantpad/opra__qqq-options__ohlcv-1d__reference`**

- QQQ.OPT | schema `ohlcv-1d` | one-day OHLCV per contract | **reference-partial-superseded**.
- Coverage: Observed 2013-09-05T00:00:00+00:00 to 2026-09-01T00:00:00+00:00; partitions 2013 to 2026. Scope: partial reference pull; superseded by the ThetaData OPRA archive. Venue/source: OPRA.PILLAR.
- Storage: parquet; 14 files; 394.25 MB; rows 38,410,697; partitioning: calendar month. Time: `quantpad-bar-ms-utc`.

**`quantpad/opra__qqq-options__statistics__reference`**

- QQQ.OPT | schema `statistics` | OPRA statistics events | **reference-partial-superseded**.
- Coverage: Observed 2020-01-02T14:31:00+00:00 to 2026-09-02T21:45:11.555722+00:00; partitions 2020-01 to 2026-09. Scope: partial reference pull; superseded by the ThetaData OPRA archive. Venue/source: OPRA.PILLAR.
- Storage: parquet; 81 files; 1,907.90 MB; rows 553,136,200; partitioning: calendar month. Time: `quantpad-tick-ns-utc`.

### thetadata-opra (41 datasets)

**`thetadata-opra/opra__ndx-options__contracts`**

- NDX | schema `contracts` | one contract-list snapshot per exchange date | **complete**.
- Coverage: Observed 2016-01-04 to 2026-09-02; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 67.92 MB; rows 13,249,752; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__ndx-options__eod`**

- NDX | schema `eod` | daily OHLC, volume, and closing NBBO per contract | **complete**.
- Coverage: Observed 2016-01-04 to 2026-09-02; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 249.31 MB; rows 13,249,752; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__ndx-options__open-interest`**

- NDX | schema `open_interest` | one open-interest observation per contract per exchange date | **complete**.
- Coverage: Observed 2016-01-04T10:22:12+00:00 to 2026-09-02T10:30:40.902000+00:00; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 95.79 MB; rows 12,003,953; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__ndx-options__quote-1m__dte14__strike-range70`**

- NDX | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-03T14:30:00+00:00 to 2026-08-20T20:00:00+00:00; partitions 2020-01-03 to 2026-09-03. Scope: DTE <= 14; strike_range=70 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: empty-marker.json, parquet; 778 files; 1,354.84 MB; rows 299,455,170; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.
- Empty markers: 1 (not data rows).

**`thetadata-opra/opra__ndx-options__quote-1m__dte60__atm10`**

- NDX | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: ATM +/- 10 listed strikes for every expiry with DTE <= 60. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 4,815.74 MB; rows 995,403,890; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__ndx-options__trade-quote__dte7__strike-range70`**

- NDX | schema `trade_quote` | every selected trade paired with the prevailing NBBO | **complete**.
- Coverage: Observed 2020-01-10T14:30:15.422000+00:00 to 2026-08-20T19:59:52.423000+00:00; partitions 2020-01-10 to 2026-09-03. Scope: DTE <= 7; strike_range=70 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: empty-marker.json, parquet; 392 files; 21.27 MB; rows 670,928; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.
- Empty markers: 2 (not data rows).

**`thetadata-opra/opra__ndxp-options__contracts`**

- NDXP | schema `contracts` | one contract-list snapshot per exchange date | **complete**.
- Coverage: Observed 2018-01-04 to 2026-09-02; partitions 2018-01-02 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: empty-marker.json, parquet; 2,179 files; 84.95 MB; rows 18,947,982; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.
- Empty markers: 2 (not data rows).

**`thetadata-opra/opra__ndxp-options__eod`**

- NDXP | schema `eod` | daily OHLC, volume, and closing NBBO per contract | **complete**.
- Coverage: Observed 2018-01-04 to 2026-09-02; partitions 2018-01-02 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: empty-marker.json, parquet; 2,179 files; 318.60 MB; rows 18,947,984; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.
- Empty markers: 2 (not data rows).

**`thetadata-opra/opra__ndxp-options__open-interest`**

- NDXP | schema `open_interest` | one open-interest observation per contract per exchange date | **complete**.
- Coverage: Observed 2018-01-05T10:30:00+00:00 to 2026-09-02T10:30:41+00:00; partitions 2018-01-02 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: empty-marker.json, parquet; 2,179 files; 106.00 MB; rows 18,776,114; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.
- Empty markers: 3 (not data rows).

**`thetadata-opra/opra__ndxp-options__quote-1m__dte14__strike-range70`**

- NDXP | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: DTE <= 14; strike_range=70 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 16,151.18 MB; rows 3,477,034,361; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__ndxp-options__quote-1m__dte60__atm10`**

- NDXP | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: ATM +/- 10 listed strikes for every expiry with DTE <= 60. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 30,104.93 MB; rows 6,297,946,089; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__ndxp-options__quote-1m__dte60__atm3-legacy`**

- NDXP | schema `quote` | one-minute NBBO snapshots per selected contract | **superseded-subset**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2020-11-10T21:00:00+00:00; partitions 2020-01-02 to 2020-11-10. Scope: legacy first pass: ATM +/- 3 listed strikes for DTE <= 60. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 218 files; 2,248.26 MB; rows 442,764,490; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__ndxp-options__trade-quote__dte7__strike-range70`**

- NDXP | schema `trade_quote` | every selected trade paired with the prevailing NBBO | **complete**.
- Coverage: Observed 2020-01-02T14:30:15.478000+00:00 to 2026-09-03T19:59:59.616000+00:00; partitions 2020-01-02 to 2026-09-03. Scope: DTE <= 7; strike_range=70 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 665.98 MB; rows 25,937,738; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__qqq-options__contracts`**

- QQQ | schema `contracts` | one contract-list snapshot per exchange date | **complete**.
- Coverage: Observed 2016-01-04 to 2026-09-02; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 76.38 MB; rows 15,255,488; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__qqq-options__eod`**

- QQQ | schema `eod` | daily OHLC, volume, and closing NBBO per contract | **complete**.
- Coverage: Observed 2016-01-04 to 2026-09-02; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 431.07 MB; rows 15,255,488; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__qqq-options__open-interest`**

- QQQ | schema `open_interest` | one open-interest observation per contract per exchange date | **complete**.
- Coverage: Observed 2016-01-04T10:22:13+00:00 to 2026-09-02T10:30:39.778000+00:00; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 122.88 MB; rows 14,805,808; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__qqq-options__quote-1m__dte14__strike-range42`**

- QQQ | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: DTE <= 14; strike_range=42 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 5,204.23 MB; rows 803,791,603; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__qqq-options__quote-1m__dte60__atm10`**

- QQQ | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: ATM +/- 10 listed strikes for every expiry with DTE <= 60. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 2,825.08 MB; rows 397,613,374; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__qqq-options__quote-1m__dte60__atm3-legacy`**

- QQQ | schema `quote` | one-minute NBBO snapshots per selected contract | **superseded-subset**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2020-11-13T21:00:00+00:00; partitions 2020-01-02 to 2020-11-13. Scope: legacy first pass: ATM +/- 3 listed strikes for DTE <= 60. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 221 files; 56.79 MB; rows 8,280,598; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__qqq-options__trade-quote__dte7__strike-range42`**

- QQQ | schema `trade_quote` | every selected trade paired with the prevailing NBBO | **complete**.
- Coverage: Observed 2020-01-02T14:30:00.338000+00:00 to 2026-09-03T19:59:59.917000+00:00; partitions 2020-01-02 to 2026-09-03. Scope: DTE <= 7; strike_range=42 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 10,683.23 MB; rows 496,412,394; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spx-options__contracts`**

- SPX | schema `contracts` | one contract-list snapshot per exchange date | **complete**.
- Coverage: Observed 2016-01-04 to 2026-09-02; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 81.18 MB; rows 15,081,222; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spx-options__eod`**

- SPX | schema `eod` | daily OHLC, volume, and closing NBBO per contract | **complete**.
- Coverage: Observed 2016-01-04 to 2026-09-02; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 357.47 MB; rows 15,083,224; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spx-options__open-interest`**

- SPX | schema `open_interest` | one open-interest observation per contract per exchange date | **complete**.
- Coverage: Observed 2016-01-04T10:22:14+00:00 to 2026-09-02T10:30:37.631000+00:00; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 156.26 MB; rows 14,544,923; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spx-options__quote-1m__dte14__strike-range90`**

- SPX | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-03T14:30:00+00:00 to 2026-08-20T20:00:00+00:00; partitions 2020-01-03 to 2026-09-03. Scope: DTE <= 14; strike_range=90 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: empty-marker.json, parquet; 779 files; 669.12 MB; rows 130,711,300; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.
- Empty markers: 1 (not data rows).

**`thetadata-opra/opra__spx-options__quote-1m__dte60__atm10`**

- SPX | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: ATM +/- 10 listed strikes for every expiry with DTE <= 60. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 1,105.57 MB; rows 206,537,539; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spx-options__trade-quote__dte7__strike-range90`**

- SPX | schema `trade_quote` | every selected trade paired with the prevailing NBBO | **complete**.
- Coverage: Observed 2020-01-10T14:30:04.327000+00:00 to 2026-08-20T19:59:59.740000+00:00; partitions 2020-01-10 to 2026-09-03. Scope: DTE <= 7; strike_range=90 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: empty-marker.json, parquet; 393 files; 136.28 MB; rows 5,758,099; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.
- Empty markers: 3 (not data rows).

**`thetadata-opra/opra__spxw-options__contracts`**

- SPXW | schema `contracts` | one contract-list snapshot per exchange date | **complete**.
- Coverage: Observed 2016-01-04 to 2026-09-02; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 165.10 MB; rows 32,216,089; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spxw-options__eod`**

- SPXW | schema `eod` | daily OHLC, volume, and closing NBBO per contract | **complete**.
- Coverage: Observed 2016-01-04 to 2026-09-02; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 745.31 MB; rows 32,218,143; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spxw-options__open-interest`**

- SPXW | schema `open_interest` | one open-interest observation per contract per exchange date | **complete**.
- Coverage: Observed 2016-01-04T10:22:12+00:00 to 2026-09-02T10:30:37.792000+00:00; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 263.18 MB; rows 30,262,601; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spxw-options__quote-1m__dte14__strike-range90`**

- SPXW | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: DTE <= 14; strike_range=90 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 9,145.02 MB; rows 1,880,165,337; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spxw-options__quote-1m__dte60__atm10`**

- SPXW | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: ATM +/- 10 listed strikes for every expiry with DTE <= 60. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 3,670.53 MB; rows 668,357,023; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spxw-options__quote-1m__dte60__atm3-legacy`**

- SPXW | schema `quote` | one-minute NBBO snapshots per selected contract | **superseded-subset**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2020-11-12T21:00:00+00:00; partitions 2020-01-02 to 2020-11-12. Scope: legacy first pass: ATM +/- 3 listed strikes for DTE <= 60. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 220 files; 107.27 MB; rows 19,288,812; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spxw-options__trade-quote__dte7__strike-range90`**

- SPXW | schema `trade_quote` | every selected trade paired with the prevailing NBBO | **complete**.
- Coverage: Observed 2020-01-02T14:30:04.474000+00:00 to 2026-09-03T19:59:59.994000+00:00; partitions 2020-01-02 to 2026-09-03. Scope: DTE <= 7; strike_range=90 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 16,838.90 MB; rows 795,921,509; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spy-options__contracts`**

- SPY | schema `contracts` | one contract-list snapshot per exchange date | **complete**.
- Coverage: Observed 2016-01-04 to 2026-09-02; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 113.28 MB; rows 21,601,651; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spy-options__eod`**

- SPY | schema `eod` | daily OHLC, volume, and closing NBBO per contract | **complete**.
- Coverage: Observed 2016-01-04 to 2026-09-02; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 630.26 MB; rows 21,601,650; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spy-options__open-interest`**

- SPY | schema `open_interest` | one open-interest observation per contract per exchange date | **complete**.
- Coverage: Observed 2016-01-04T10:22:12+00:00 to 2026-09-02T10:30:37.631000+00:00; partitions 2016-01-04 to 2026-09-02. Scope: full option chain: all listed expiries and strikes. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 2,682 files; 180.69 MB; rows 20,855,185; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spy-options__quote-1m__dte14__strike-range45`**

- SPY | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: DTE <= 14; strike_range=45 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 6,011.98 MB; rows 1,023,040,552; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spy-options__quote-1m__dte60__atm10`**

- SPY | schema `quote` | one-minute NBBO snapshots per selected contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: ATM +/- 10 listed strikes for every expiry with DTE <= 60. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 4,758.87 MB; rows 741,569,036; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__spy-options__trade-quote__dte7__strike-range45`**

- SPY | schema `trade_quote` | every selected trade paired with the prevailing NBBO | **complete**.
- Coverage: Observed 2020-01-02T14:30:00.420000+00:00 to 2026-09-03T19:59:59.962000+00:00; partitions 2020-01-02 to 2026-09-03. Scope: DTE <= 7; strike_range=45 around spot. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 22,502.90 MB; rows 1,085,536,449; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__vix-options__open-interest__dte60-full-chain`**

- VIX | schema `open_interest` | one open-interest observation per contract per exchange date | **complete**.
- Coverage: Observed 2020-01-02T12:01:01+00:00 to 2026-09-03T10:31:06.324000+00:00; partitions 2020-01-02 to 2026-09-03. Scope: full chain, DTE <= 60. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 21.30 MB; rows 1,503,420; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

**`thetadata-opra/opra__vix-options__quote-1m__dte60-full-chain`**

- VIX | schema `quote` | one-minute NBBO snapshots per contract | **complete**.
- Coverage: Observed 2020-01-02T14:30:00+00:00 to 2026-09-03T20:00:00+00:00; partitions 2020-01-02 to 2026-09-03. Scope: full chain, DTE <= 60, no strike filter. Venue/source: ThetaData Options / OPRA.
- Storage: parquet; 1,677 files; 689.38 MB; rows 146,035,763; partitioning: one file or explicit empty marker per exchange date. Time: `thetadata-ms-et-to-ns-utc`.

### free-sources (27 datasets)

**`free-sources/bls__release-calendars`**

- CPI,employment releases | schema `release calendar and source snapshots` | one row/page per release calendar artifact | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2021 to 2026-07-01. Scope: available historical release calendars. Venue/source: US Bureau of Labor Statistics/Wayback.
- Storage: csv, htm, tsv; 17 files; 0.80 MB; rows unknown; partitioning: CSV/HTML and provenance. Time: `mixed-free-source`.
- Description: BLS CPI and employment-release calendars with archived source pages.

**`free-sources/cboe__vvix__raw`**

- VVIX | schema `daily_history` | daily observations | **complete**.
- Coverage: Observed timestamps not recorded. Scope: available official history. Venue/source: Cboe.
- Storage: csv; 1 files; 0.11 MB; rows unknown; partitioning: single CSV. Time: `date-only`.
- Description: Raw official Cboe VVIX history.

**`free-sources/cboe__vx-futures__normalized`**

- VX | schema `daily_futures` | daily OHLC, settlement, volume, and open interest per contract | **complete**.
- Coverage: Observed 2020-01-02 to 2026-09-03. Scope: official Cboe archive from 2020 onward. Venue/source: Cboe.
- Storage: parquet; 1 files; 0.49 MB; rows 23,391; partitioning: single combined Parquet. Time: `date-only`.
- Description: Normalized VX term-structure table retaining monthly/weekly identifiers.

**`free-sources/cboe__vx-futures__raw`**

- VX | schema `daily_futures` | daily OHLC, settlement, volume, and open interest per contract | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2020-01-08 to 2027-05-18. Scope: official Cboe archive from 2020 onward. Venue/source: Cboe.
- Storage: csv, json; 364 files; 2.87 MB; rows unknown; partitioning: one CSV per contract expiration. Time: `date-only`.
- Description: Raw official Cboe VX futures contract files.

**`free-sources/central-banks__fomc-and-boj-calendars`**

- FOMC,BOJ | schema `event calendar` | one row per scheduled event | **complete**.
- Coverage: Observed timestamps not recorded. Scope: available event history. Venue/source: Federal Reserve/Bank of Japan.
- Storage: csv; 2 files; 0.00 MB; rows unknown; partitioning: two CSV files. Time: `mixed-free-source`.
- Description: Legacy FOMC and BOJ event calendars.

**`free-sources/cftc__commitments-of-traders`**

- futures positioning | schema `legacy/disaggregated/TFF reports` | weekly reports | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2021 to 2026. Scope: 2021-2026. Venue/source: CFTC.
- Storage: tsv, txt, zip; 38 files; 255.83 MB; rows unknown; partitioning: annual TXT/ZIP files plus manifests. Time: `mixed-free-source`.
- Description: CFTC Commitments of Traders source reports.

**`free-sources/context__earnings__normalized`**

- mega-cap equities | schema `earnings` | one row per earnings event | **complete**.
- Coverage: Observed timestamps not recorded. Scope: tracked mega-cap constituents. Venue/source: free calendar sources.
- Storage: parquet; 20 files; 0.09 MB; rows 1,346; partitioning: one Parquet per symbol. Time: `mixed-free-source`.
- Description: Normalized earnings dates used as event context.

**`free-sources/context__event-calendar__normalized`**

- market events | schema `event_calendar` | one row per event/session | **complete**.
- Coverage: Observed timestamps not recorded. Scope: FOMC, economic releases, earnings, and market sessions. Venue/source: Federal Reserve/FRED/market calendars.
- Storage: parquet; 5 files; 0.10 MB; rows 4,506; partitioning: small topical Parquet files. Time: `mixed-free-source`.
- Description: Normalized event calendar tables.

**`free-sources/context__volatility__normalized`**

- VIX,VXN,VIX3M,VVIX | schema `daily_history` | daily observations | **complete**.
- Coverage: Observed 1990-01-02 to 2026-09-02. Scope: normalized free-source volatility context. Venue/source: Cboe/FRED.
- Storage: parquet; 5 files; 0.25 MB; rows 47,364; partitioning: one Parquet per index/source. Time: `date-only`.
- Description: Normalized cash volatility indices.

**`free-sources/cross-asset__acquisition-metadata`**

- cross-asset context | schema `provenance` | one record per acquisition run | **complete**.
- Coverage: Observed timestamps not recorded. Scope: metadata for the Nikkei/copper/rates context pull. Venue/source: legacy ingestion scripts/logs.
- Storage: json, py, txt; 5 files; 0.01 MB; rows unknown; partitioning: root-level files only. Time: `mixed-free-source`.
- Description: Legacy fetch logs, notes, and acquisition script.

**`free-sources/cross-asset__copper`**

- HG,SHFE copper,USDCNY | schema `mixed daily and 1/5/15/30/60-minute history` | source-native interval stated in each filename | **complete**.
- Coverage: Observed timestamps not recorded. Scope: cross-asset copper context. Venue/source: FRED/Sina/SHFE comparison.
- Storage: csv, tsv; 11 files; 1.03 MB; rows unknown; partitioning: one CSV per instrument/interval plus manifest. Time: `mixed-free-source`.
- Description: COMEX/SHFE copper, FX, and verification context.

**`free-sources/cross-asset__nikkei-and-fx`**

- Nikkei,NKD,USDJPY | schema `mixed daily/intraday history` | source-native daily or intraday observations | **complete**.
- Coverage: Observed timestamps not recorded. Scope: cross-asset Nikkei context. Venue/source: FRED/Sina.
- Storage: csv, tsv; 6 files; 0.83 MB; rows unknown; partitioning: one CSV per instrument plus manifest. Time: `mixed-free-source`.
- Description: Nikkei index/futures/FX context and provenance.

**`free-sources/cross-asset__rates`**

- USD rates | schema `daily history` | daily observations | **complete**.
- Coverage: Observed timestamps not recorded. Scope: cross-asset model inputs. Venue/source: FRED.
- Storage: csv, tsv; 6 files; 0.86 MB; rows unknown; partitioning: one CSV per series plus manifest. Time: `mixed-free-source`.
- Description: Rate series from the legacy cross-asset context pull.

**`free-sources/federal-reserve__fomc-pages__raw`**

- FOMC | schema `HTML pages` | meeting schedule page | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2010 to 2020. Scope: historical/current meeting calendars. Venue/source: Federal Reserve.
- Storage: html; 12 files; 1.23 MB; rows unknown; partitioning: one file per source page/year. Time: `date-only`.
- Description: Raw Federal Reserve FOMC calendar pages.

**`free-sources/fred__macro-context__legacy-refresh`**

- USDJPY,GVZ,DGS10,T10YIE,dollar index | schema `daily macro history` | daily/source-native observations | **complete**.
- Coverage: Observed timestamps not recorded. Scope: legacy macro refresh. Venue/source: FRED.
- Storage: csv, tsv; 6 files; 0.81 MB; rows unknown; partitioning: one CSV per series plus manifest. Time: `mixed-free-source`.
- Description: Additional FRED macro and cross-asset context.

**`free-sources/fred__rates__legacy-raw`**

- USD rates | schema `JSON responses and provenance` | source observation cadence | **complete**.
- Coverage: Observed timestamps not recorded. Scope: previously acquired rate inputs. Venue/source: FRED.
- Storage: json, sha256; 8 files; 0.64 MB; rows unknown; partitioning: one response per FRED series. Time: `mixed-free-source`.
- Description: Legacy raw FRED rate responses with receipt and SHA-256 manifest.

**`free-sources/fred__usd-rates__normalized`**

- USD rates | schema `observations` | daily/series-native observations | **complete**.
- Coverage: Observed 2010-01-01 to 2026-09-03. Scope: normalized USD rate table. Venue/source: FRED.
- Storage: parquet; 1 files; 0.08 MB; rows 30,032; partitioning: single combined Parquet. Time: `date-only`.
- Description: Normalized rate observations for option valuation.

**`free-sources/fred__usd-rates__raw`**

- USD rates | schema `observations` | source observation cadence | **complete**.
- Coverage: Observed timestamps not recorded. Scope: DFF, SOFR, Treasury bill and constant-maturity series. Venue/source: FRED.
- Storage: json; 7 files; 4.49 MB; rows unknown; partitioning: one JSON response per series. Time: `date-only`.
- Description: Raw FRED API responses for option-rate inputs.

**`free-sources/fred__volatility-and-releases__raw`**

- VIX,VXN,VIX3M,economic releases | schema `JSON responses` | source observation cadence | **complete**.
- Coverage: Observed timestamps not recorded. Scope: free external context. Venue/source: FRED.
- Storage: json; 5 files; 3.29 MB; rows unknown; partitioning: one JSON response per series/release. Time: `date-only`.
- Description: Raw FRED volatility-index and release responses.

**`free-sources/fred__volatility-indices__legacy`**

- VIX,VXD,RVX | schema `daily history` | daily observations | **complete**.
- Coverage: Observed timestamps not recorded. Scope: available source history. Venue/source: FRED.
- Storage: csv; 3 files; 0.39 MB; rows unknown; partitioning: one CSV per index. Time: `mixed-free-source`.
- Description: Legacy FRED cash volatility-index histories.

**`free-sources/ishares__slv-fund-flows`**

- SLV | schema `fund NAV/shares/ounces` | daily observations | **complete**.
- Coverage: Observed timestamps not recorded. Scope: available fund history. Venue/source: iShares.
- Storage: csv, tsv, xml; 4 files; 2.22 MB; rows unknown; partitioning: CSV plus raw workbook and manifest. Time: `mixed-free-source`.
- Description: SLV NAV, shares, and implied ounces-flow context.

**`free-sources/nasdaq__trading-calendars__reference`**

- US market calendars | schema `PDF/HTML reference` | annual trading-calendar documents | **complete**.
- Coverage: Observed timestamps not recorded; partitions 2020 to 2025. Scope: 2020-2025 reference calendars. Venue/source: Nasdaq/reference sources.
- Storage: html, pdf; 7 files; 0.86 MB; rows unknown; partitioning: one file per calendar year/source. Time: `mixed-free-source`.
- Description: Original market-calendar reference documents.

**`free-sources/shfe__metal-inventories`**

- silver,copper | schema `inventory history` | daily or weekly observations by file | **complete**.
- Coverage: Observed timestamps not recorded. Scope: available source history. Venue/source: SHFE/secondary mirrors.
- Storage: csv, tsv; 5 files; 0.06 MB; rows unknown; partitioning: one CSV per metal/frequency plus manifest. Time: `mixed-free-source`.
- Description: SHFE silver and copper inventory context.

**`free-sources/yahoo__cash-daily__normalized`**

- QQQ,SPY,NDX,SPX | schema `daily_ohlcv` | daily OHLCV observations | **complete**.
- Coverage: Observed 2010-01-04 to 2026-09-04. Scope: normalized companion to the raw Yahoo files. Venue/source: Yahoo Finance.
- Storage: parquet; 4 files; 0.40 MB; rows 16,776; partitioning: one file per symbol. Time: `date-only`.
- Description: Normalized cash daily history.

**`free-sources/yahoo__cash-daily__raw`**

- QQQ,SPY,NDX,SPX | schema `daily_ohlcv` | daily source records | **complete**.
- Coverage: Observed timestamps not recorded. Scope: raw vendor responses. Venue/source: Yahoo Finance.
- Storage: csv; 4 files; 1.79 MB; rows unknown; partitioning: one file per symbol. Time: `date-only`.
- Description: Unmodified Yahoo daily-history CSV responses.

**`free-sources/yahoo__commodity-futures-daily__legacy`**

- SI,HG,NKD,GC | schema `daily futures history` | daily OHLCV observations | **complete**.
- Coverage: Observed timestamps not recorded. Scope: legacy cross-asset daily context. Venue/source: Yahoo Finance.
- Storage: csv; 4 files; 0.76 MB; rows unknown; partitioning: one CSV per continuous Yahoo symbol. Time: `mixed-free-source`.
- Description: Yahoo daily futures histories retained from the earlier archive.

**`free-sources/yahoo__corporate-actions__normalized`**

- QQQ,SPY | schema `corporate_actions` | dividend/split event | **complete**.
- Coverage: Observed timestamps not recorded. Scope: all available actions. Venue/source: Yahoo Finance.
- Storage: parquet; 2 files; 0.01 MB; rows 135; partitioning: one file per symbol. Time: `mixed-free-source`.
- Description: Normalized QQQ and SPY dividend/split history.

### derived (1 datasets)

**`derived/continuous-futures__instrument-and-roll-maps`**

- NQ.c.0,ES.c.0,YM.c.0 | schema `instrument_map and roll_segments` | one row per instrument or continuous-contract segment | **complete**.
- Coverage: Observed 2010-09-06T15:20:00+00:00 to 2026-06-19T00:00:00+00:00. Scope: full bar/definition coverage for NQ, ES, and YM. Venue/source: derived from QuantPad GLBX.MDP3.
- Storage: parquet; 6 files; 0.07 MB; rows 390; partitioning: one pair of files per futures root. Time: `continuous-roll-map-mixed-utc`.
- Caveats: RTY roll maps intentionally omitted because RTY definitions are incomplete.

## Not available / intentionally excluded

- NQ MBP-10 was declared unnecessary and is intentionally excluded.
- Superseded/benchmark yearly NQ MBP-1 copies are excluded to avoid duplicating the complete monthly raw archive.
- Five incomplete atomic download files were excluded. A `.part` file is not usable completed coverage.
- Empty planned datasets omitted from the archive:
  - `quantpad/opra__ndx-options__statistics__reference`
  - `databento/cme__si-futures__trades`
  - `thetadata-opra/opra__ndx-options__quote-1m__dte60__atm3-legacy`
  - `thetadata-opra/opra__spx-options__quote-1m__dte60__atm3-legacy`
  - `thetadata-opra/opra__spy-options__quote-1m__dte60__atm3-legacy`

## Source manifests and limits

Authoritative detailed inventory is in `/workspace/data/manifests/`: `dataset-catalog.json`, `files.csv` / `files.parquet` (individual file inventory), `schema-catalog.json` (actual Arrow fields/types), `timestamp-conventions.json`, `exclusions-and-gaps.json`, and `data-location.json`.
This document enumerates every dataset, not all 80,198 filenames or every schema column. Unknown row counts and missing time bounds are intentionally preserved. Do not treat complete acquisition status as proof of suitability for live trading or bias-free historical modeling.
