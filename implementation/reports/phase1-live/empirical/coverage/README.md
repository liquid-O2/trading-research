# Empirical coverage artifacts

These manifests are frozen from native Parquet metadata and the `t` / `instrument_id`
columns used to identify complete RTH sessions. Prices, sizes, sides, labels and
historical outcomes are not read while choosing partitions. Full file SHA-256
identities are retained for inputs used by each cohort.

| cohort | partitions | scope | validation |
|---|---:|---|---|
| [`bar-monthly`](bar-monthly/README.md) | 161 | NQ, first complete 09:30–16:00 ET weekday session per month, 2010–2026 | PASS |
| [`tape-annual-trades`](tape-annual-trades/README.md) | 4 | NQ, first complete session per year where native standalone trades overlap the prior-weekday RTH plus evaluation session | PASS |

[`native-inventory-all.json`](native-inventory-all.json) inventories NQ, MNQ and ES.
It records 489 native Parquet files: NQ and ES are available, while the acquired
MNQ root is absent. NQ MBP-1 ownership is resolved through the existing canonical
monthly/weekly adapter; unowned partitions are retained as explicit holes.

Reproduce the metadata inventory and the default bar cohort with:

```bash
PYTHONPATH=implementation/src python -m trading_research.research.method_pack.empirical_coverage \
  inventory --data-root /workspace/data --output-dir /workspace/implementation/reports/phase1-live/empirical/coverage/inventory-all --no-hashes

PYTHONPATH=implementation/src python -m trading_research.research.method_pack.empirical_coverage \
  freeze --data-root /workspace/data --output-dir /workspace/implementation/reports/phase1-live/empirical/coverage/bar-monthly \
  --root NQ --frequency monthly --required-dataset ohlcv_1m --required-dataset definition
```

The annual trade cohort uses the same command with `--frequency annual`,
`--required-data-policy filter`, and `--required-dataset trades`; its exact
manifest identity is retained in `tape-annual-trades/evaluation-split.json`.
Prior exposure is only partially detectable from retained selected outputs, so
every included partition keeps `prior_exposure_status=unknown` and no untouched
sample claim is made.
