# Acquired futures coverage audit

This report separates observed timestamps, declared partition scope, and continuity checks. A file min/max and a row-group min/max are envelopes; they do not prove that every timestamp or market event inside the envelope exists.

Reproduce from the repository root:

```bash
python implementation/tools/audit_acquired_windows.py \
  --data-root /workspace/data \
  --output-dir /workspace/implementation/reports/phase1-live/coverage-audit \
  --comparison-dir /workspace/implementation/reports/phase1-live/derived-views/mbp1-o741r2ic \
  --minute-recovery-manifest /workspace/implementation/reports/phase1-live/derived-views/nq-minutes-37uhc_wa/manifest.json \
  --tail-recovery-manifest /workspace/implementation/reports/phase1-live/derived-views/mbp1-9_5xkllu/manifest.json
```

## NQ observed bounds

| format | files | rows | row groups | empty files | missing `t` stats | first observed `t` UTC | last observed `t` UTC |
|---|---:|---:|---:|---:|---:|---|---|
| MBP-1 | 142 | 11,536,223,348 | 47,269 | 0 | 0 | 2020-01-01T23:00:00.000000000Z | 2026-09-03T06:09:59.901114377Z |
| trades | 262 | 470,160,602 | 3,344 | 0 | 0 | 2021-09-01T18:00:00.030617317Z | 2026-09-02T17:59:59.376719279Z |
| OHLCV-1s | 17 | 127,979,940 | 2,568 | 0 | 0 | 2010-09-06T15:20:56.000000000Z | 2026-09-02T15:19:59.000000000Z |
| OHLCV-1m | 17 | 4,695,352 | 100 | 0 | 0 | 2010-09-06T15:20:00.000000000Z | 2026-09-02T15:19:00.000000000Z |

All four bounds are the exact extrema of every row-group `t` statistic. The bar timestamps are bar starts. OHLCV-1m's exclusive observed endpoint is 2026-09-02T15:20:00.000000000Z; OHLCV-1s's is 2026-09-02T15:20:00.000000000Z. MBP-1's last observed event is 2026-09-03T06:09:59.901114377Z.

The companion row-group artifact contains 53,281 exact footer interval records and its SHA-256 is `1fcd74e6a1f0f69b0a63de7aec5b03d7229ac379997633de75763c8635b3e7e2`.

## Nominal partitions and MBP-1 ownership

The monthly physical track has 81 files (2020-01 through 2026-09); no label is missing between those endpoints; no file is empty. The weekly physical track has 61 files (2019-12-30 through 2021-02-22); no label is missing between those endpoints; no file is empty. Every MBP-1 row group has `t` statistics.

Monthly files have precedence. Subtracting the monthly observed envelopes from the weekly envelopes produces 11 candidate spans. Targeted `t` scans read the intersecting boundary groups and find **0 rows** across those spans. The scans found no weekly rows outside the monthly envelopes. Equality of every overlapping weekly/monthly row was not scanned.

Trades has 262 weekly labels from 2021-08-30 through 2026-08-31; no label is missing between those endpoints; 0 empty file(s); 0 row group(s) missing `t` statistics. OHLCV-1s has 17 annual labels from 2010 through 2026; no label is missing between those endpoints; 0 empty file(s); 0 row group(s) missing `t` statistics. OHLCV-1m has 17 annual labels from 2010 through 2026; no label is missing between those endpoints; 0 empty file(s); 0 row group(s) missing `t` statistics. The first standalone trade event is `2021-09-01T18:00:00.030617317Z`.

## Actually incomplete NQ standalone windows

An exact streamed comparison finds 12,452 minute buckets present in OHLCV-1s but absent from OHLCV-1m. 9 are complete 18:00–17:00 ET Globex sessions:

- 2025-06-10: `2025-06-09T22:00:00.000000000Z` to `2025-06-10T21:00:00.000000000Z` (exclusive), 1,380 1s-occupied minutes; MBP-1 endpoint evidence=true, standalone-trade endpoint evidence=true.
- 2026-06-02: `2026-06-01T22:00:00.000000000Z` to `2026-06-02T21:00:00.000000000Z` (exclusive), 1,380 1s-occupied minutes; MBP-1 endpoint evidence=true, standalone-trade endpoint evidence=true.
- 2026-06-03: `2026-06-02T22:00:00.000000000Z` to `2026-06-03T21:00:00.000000000Z` (exclusive), 1,380 1s-occupied minutes; MBP-1 endpoint evidence=true, standalone-trade endpoint evidence=true.
- 2026-06-04: `2026-06-03T22:00:00.000000000Z` to `2026-06-04T21:00:00.000000000Z` (exclusive), 1,380 1s-occupied minutes; MBP-1 endpoint evidence=true, standalone-trade endpoint evidence=true.
- 2026-07-06: `2026-07-05T22:00:00.000000000Z` to `2026-07-06T21:00:00.000000000Z` (exclusive), 1,380 1s-occupied minutes; MBP-1 endpoint evidence=true, standalone-trade endpoint evidence=true.
- 2026-07-07: `2026-07-06T22:00:00.000000000Z` to `2026-07-07T21:00:00.000000000Z` (exclusive), 1,380 1s-occupied minutes; MBP-1 endpoint evidence=true, standalone-trade endpoint evidence=true.
- 2026-07-08: `2026-07-07T22:00:00.000000000Z` to `2026-07-08T21:00:00.000000000Z` (exclusive), 1,380 1s-occupied minutes; MBP-1 endpoint evidence=true, standalone-trade endpoint evidence=true.
- 2026-08-03: `2026-08-02T22:00:00.000000000Z` to `2026-08-03T21:00:00.000000000Z` (exclusive), 1,380 1s-occupied minutes; MBP-1 endpoint evidence=true, standalone-trade endpoint evidence=true.
- 2026-08-04: `2026-08-03T22:00:00.000000000Z` to `2026-08-04T21:00:00.000000000Z` (exclusive), 1,380 1s-occupied minutes; MBP-1 endpoint evidence=true, standalone-trade endpoint evidence=true.

The other 32 discrepancies are isolated minute starts (2010-09-24 through 2015-08-07). Many may reflect closure context; the JSON lists every timestamp so they remain visible rather than being silently called market gaps.

Standalone trades have no rows from the observed MBP-1 trade-action edge `2020-01-01T23:00:00.000000000Z` to `2021-09-01T18:00:00.030617317Z` (exclusive). MBP-1 T actions and row-group session endpoints exist in this range; continuity was not scanned.
A later MBP-1 trade action is observed from after the standalone trade endpoint through `2026-09-03T06:09:57.452247829Z` (inclusive). A later MBP-1 T action is directly observed.

The supplied bounded comparison covers `2020-01-02T14:30:00.000000000Z` through `2020-01-02T14:35:00.000000000Z` (exclusive). It produced 9,537 trades, 107,067 top-of-book observations, 300 one-second bars, and 5 one-minute bars. 25 of 25 minute OHLCV fields equal the native minute bars.
For native 1s, the supplied comparison records 1,474 equal fields, 19 unresolved equal-timestamp O/C fields, and 7 mismatches (1 O, 6 V). The acquired MBP-1 schema lacks ts_recv and sequence. Event-time 1s bars are valid derived views, but native vendor 1s bins cannot be promised bit-identical; the supplied comparison retains mismatches and unresolved equal-timestamp O/C order explicitly.

The supplied minute-recovery manifest records 12,452 of 12,452 requested keys recovered, 0 unresolved, and 0 existing keys encountered. The recovered JSONL SHA-256 is `ae869033ec6489b57104237cddb3a8d4f290d53faec0b8d562f705bfa96ed349`; raw source signatures unchanged=true.
The supplied MBP-1 event-time tail manifest covers `2026-09-02T15:20:00.000000000Z` through `2026-09-03T06:09:00.000000000Z` (exclusive), with 829 non-empty minute bars and SHA-256 `69153a50fd0a2bc0829a60bf7d7ce3fce28048f76db286da65dc9eb9a758f6cd`; raw source signatures unchanged=true.

## What the evidence supports about MBP-1 gaps

The exact 1m session set contains 4,107 Globex trade dates. All 1,712 1m-observed sessions within MBP-1's endpoint bounds have at least one actual MBP-1 row-group endpoint in the session. After merging monthly-primary row-group envelopes, 0 gaps contain a complete standalone 1m bar.

No nominal NQ MBP-1 month label is missing between the physical endpoints. No empty MBP-1 file was found. No MBP-1 row group with missing `t` statistics was found. All 1712 1m-observed session(s) within the MBP-1 endpoint bounds have MBP-1 row-group endpoint evidence. No gap between monthly-primary row-group envelopes containing a complete existing 1m bar was found. Event-level internal continuity was not checked, so this is not proof of a gap-free tape.

The last physical MBP-1 monthly label is `2026-09` and the last observed event is `2026-09-03T06:09:59.901114377Z`. The audit does not invent a missing interval after that observed bound. Market closures and contract rolls are not inferred from elapsed UTC time alone.

## Other major acquired gaps

- `quantpad/cme__rty-continuous-futures__ohlcv-1m`: zero-row partitions `2010.parquet`, `2011.parquet`, `2012.parquet`, `2013.parquet`, `2014.parquet`, `2015.parquet`, `2016.parquet`.
- `quantpad/cme__rty-continuous-futures__statistics`: zero-row partitions `2010.parquet`, `2011.parquet`, `2012.parquet`, `2013.parquet`, `2014.parquet`, `2015.parquet`, `2016.parquet`.
- `quantpad/cme__es-continuous-futures__mbp-1` (partial-paused): missing month ranges through 2026-09: 2020-11, 2021-01 through 2023-06, 2024-09 through 2026-09.
- `quantpad/cme__rty-continuous-futures__definition` (partial-skipped): physical year labels 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026; RTY definition years 2010-2018 were intentionally skipped after repeated vendor read timeouts; 2019-2026 are retained.

CME's [launch announcement](https://www.cmegroup.com/media-room/press-releases/2017/7/11/cme_group_announcesfirsttradesafterthereturnoftherussell2000inde.html) places the RTY launch at the July 10, 2017 trade date. Empty 2010-2016 RTY files therefore precede this listing; they are not lost RTY sessions. Any missing RTY definition files from 2017 onward are a separate acquisition limitation.

Reference/superseded option datasets are outside this compact futures-window overview. MBP-1 supports depth-one state and trade actions; this audit does not claim that deeper book or order-level formats can be reconstructed.
