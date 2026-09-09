# Report preview

The complete report is preserved in [results.md.gz](results.md.gz). Use the root restoration script to restore it byte for byte. The excerpt below is for navigation; it is not the complete report.

---

# Options quote quality / support

Family: `Research-Options-Quote-Quality-Support-acquired-v1`
Statistics version: `options-quote-quality-support-statistics-v2`
Scope: acquired quote-minute quality, coverage, ages and underlier/rate/action support.
IV, Greeks and surfaces are not computed.
causal_feature_eligible is FALSE. received_at, published_at, known_at and last_actual_update are NULL.
actual update age is unknown. Missing, invalid and conflicting quotes are never treated as prices.
The scientific family is not complete from this execution alone.

Full metric tables for every constructed group are written below and in the streamed `groups-*.json` artifacts. This report is not a 10-metric subset.

## Accounting

- source files read: 102
- raw quotation rows: 34209372
- unique timestamps / events: 26948502
- cut-board rows: 4222390
- listed contracts (observed): 278864
- quoted contracts: 68922
- OI-matched contracts: 276348
- support files read: 25
- support rows: 1605474
- independent intended dates in this selection: 8
- intended chain-date units: 56

Classes are complete, censored or missing as labeled. Absence is not zero.
Moving-block bootstrap: 1000 replicates, block length 5, seed 20260908, 0.95 interval. Sparse if fewer than 100 independent dates or 20 events.

## Streamed references

- `admission`: `[{'path': '/workspace/trading-research/reports/options-quote-runs/a930254c41bdac723592f14b04831f7caa96efe8624fefcef61cdccb99273830/outputs/admission-0000.parquet', 'sha256': 'b1f20bdee8d3ab4091fa76562be5b12cf771f8b05067e6b7f00a31a4c015ca2a', 'size_bytes': 12284, 'kind': 'options_quote_file_admission_v1', 'rows': 127}]`
- `exceptions`: `[{'path': '/workspace/trading-research/reports/options-quote-runs/a930254c41bdac723592f14b04831f7caa96efe8624fefcef61cdccb99273830/outputs/exceptions-0000.parquet', 'sha256': '1864948a5d16a8372b91aad69ca52cdf6a3a3175d5542365b3da8412c0d1a6d2', 'size_bytes': 2309, 'kind': 'options_quote_exceptions_v1', 'rows': 0}]`
- `alias_conflict`: `[{'path': '/workspace/trading-research/reports/options-quote-runs/a930254c41bdac723592f14b04831f7caa96efe8624fefcef61cdccb99273830/outputs/alias-conflict-0000.parquet', 'sha256': 'c62d1acaeecaed0ea44232f7875f335597abaf398d42dc4abe5c5ecd5a49d13b', 'size_bytes': 7695, 'kind': 'options_quote_alias_conflict_v1', 'rows': 158}]`

[Download the complete report](results.md.gz).
