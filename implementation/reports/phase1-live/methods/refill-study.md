# REFILL-STUDY method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T09:44:46Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
REFILL-STUDY | touch_causality | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/refill-study.md
REFILL-STUDY | selected_order_configuration | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/refill-study.md

## Summary

- predicate: touch_causality
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12`; source contracts checked against their recorded hashes.

branch | complete selector | missing source inputs
--- | --- | ---
supplied_selected_order | no | zone_definition_recorded, instrument_and_threshold_preserved, thesis_recorded, grade_model_frozen_before_touch, fill_assumption_recorded
touch_record | no | zone_definition_recorded, instrument_and_threshold_preserved, thesis_recorded

A source zone is required before touch discovery. Clustering/normalization and the hold label are absent; a supplied selected order additionally needs its frozen grade/model and lifecycle. Generic large prints are not source zones.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `touch_record` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `supplied_selected_order` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
touch_causality | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0
selected_order_configuration | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114378, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 636; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 54, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `43fa8e55f5108ca765dd1a520caea1f74d91faf1`; content hash `abb39481bd9ca8e2da5c2d0cc97749a5c61b92f3ab769d7131ddc0989eab88d8`.

## Holes

- **Required end-to-end behavior:** Frozen source zone → departure → distinct return → strictly causal pre-touch construction/memory/location/flow → later label; if supplied, audit frozen grade/order/bracket/fill/cost records and preserve the later causal correction.
- **Source-complete candidate discovery:** Source cluster/normalization, hold label, grade transformations/model and complete order lifecycle are missing. Do not train a grader, choose later days or turn a useful grade into an entry strategy.
- **M09-F3 — source/data hole.** No supplied frozen grader/grade or exact source zone/side definition → unknown. Headline primary measures touch-record causality, not profitability; later-OFM negative causal rebuild must remain visible.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/refill-study/run-sk5w_azv/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/refill-study/run-sk5w_azv/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/refill-study/run-sk5w_azv/holes.jsonl sha256=bbbaeefb4b8095f007579e579414b4e979c06fb143ad8e6ff0bc0fc70dfc1b31
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/refill-study/run-sk5w_azv/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/refill-study/run-sk5w_azv/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/refill-study/run-sk5w_azv/fixtures.json sha256=4860ec58a6c4e7354747d1f4c89669ba9af71f29abb4c0d79474a334086ee128
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/refill-study/run-sk5w_azv/cohort.json sha256=7c677ae8fba595a9ac45197577a61d927e2d4404af7b3962b18976347f99e5ee
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/refill-study/run-sk5w_azv/coverage.json sha256=4da1247f21783ec9aefe1279c244a7c4a1fdc8a6ea27f95b7e22be20fc64d2ea
