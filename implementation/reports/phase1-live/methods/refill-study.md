# REFILL-STUDY method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T07:55:39Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
REFILL-STUDY | touch_causality | 0 | — | — | 2010:0;2011:0;2012:0;2013:0;2014:0;2015:0;2016:0;2017:0;2018:0;2019:0;2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/refill-study.md
REFILL-STUDY | selected_order_configuration | 0 | — | — | 2010:0;2011:0;2012:0;2013:0;2014:0;2015:0;2016:0;2017:0;2018:0;2019:0;2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/refill-study.md

## Summary

- predicate: touch_causality
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole

## Branches

- `touch_record` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `supplied_selected_order` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
touch_causality | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2010:0;2011:0;2012:0;2013:0;2014:0;2015:0;2016:0;2017:0;2018:0;2019:0;2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0
selected_order_configuration | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2010:0;2011:0;2012:0;2013:0;2014:0;2015:0;2016:0;2017:0;2018:0;2019:0;2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0

## Coverage

Requested span: `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114378, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 636; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 54, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `c08725edbaeab2b9b527e8ae919af861d7fc263f`; content hash `2cab034db2917ee91fe1e35d3256b71efcce07a688cc9c1a0fc51c3073f05f32`.

## Holes

- **Required end-to-end behavior:** Frozen source zone → departure → distinct return → strictly causal pre-touch construction/memory/location/flow → later label; if supplied, audit frozen grade/order/bracket/fill/cost records and preserve the later causal correction.
- **Source-complete candidate discovery:** Source cluster/normalization, hold label, grade transformations/model and complete order lifecycle are missing. Do not train a grader, choose later days or turn a useful grade into an entry strategy.
- **M09-F3 — source/data hole.** No supplied frozen grader/grade or exact source zone/side definition → unknown. Headline primary measures touch-record causality, not profitability; later-OFM negative causal rebuild must remain visible.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/refill-study/run-w616v2h7/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/refill-study/run-w616v2h7/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/refill-study/run-w616v2h7/holes.jsonl sha256=21de877ca01259fda4e5a783af55a1487a111a3f32a13e4c0a2456ac669d50a4
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/refill-study/run-w616v2h7/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/refill-study/run-w616v2h7/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/refill-study/run-w616v2h7/fixtures.json sha256=4860ec58a6c4e7354747d1f4c89669ba9af71f29abb4c0d79474a334086ee128
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/refill-study/run-w616v2h7/cohort.json sha256=fbed6e27d783fb221bc91be52283632e0a8b8adff293ddf815b4f0488c572ba1
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/refill-study/run-w616v2h7/coverage.json sha256=4da1247f21783ec9aefe1279c244a7c4a1fdc8a6ea27f95b7e22be20fc64d2ea
