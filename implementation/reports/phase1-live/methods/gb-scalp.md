# GB-SCALP method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T10:46:50Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
GB-SCALP | case_description | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/gb-scalp.md
GB-SCALP | automatic_admission | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/gb-scalp.md

## Summary

- predicate: case_description
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12`; source contracts checked against their recorded hashes.

branch | complete selector | missing source inputs
--- | --- | ---
bearish_small_scalp | no | direction_recorded_before_entry, small_size_recorded, source_directional_pullback_observed, source_scalp_management_recorded
bullish_discount_pullback | no | direction_recorded_before_entry, small_size_recorded, source_directional_pullback_observed, source_scalp_management_recorded

M04 explicitly returns NULL for automatic_admission. Both branches describe source decisions and management; direction or discount algebra cannot select a scalp.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `bearish_small_scalp` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `bullish_discount_pullback` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
case_description | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0
automatic_admission | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788393600000000000, 'min_ns': 631238400000000000, 'max_ns': 1788393600000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788393600000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1850256000000000000, 'min_ns': 631238400000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 666; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 30, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `f7850418c2fffdcbb9b67d52fdea9609e9cbd460`; content hash `30e8f63115b6ecb6d5ab6c62aa8e67675a82cfcfc159f2737d963484f6a9bbf9`.

## Holes

- **Source-complete candidate discovery:** No repeatable source-complete scalp selector is disclosed. Never create a two-box, VWAP or failure-trigger replacement.
- **M04-F3 — source/data hole.** Full trigger, measured-impulse selection, general invalidation and exit algorithm are holes in every automatic scalp-admission result.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-scalp/run-8urznj6v/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-scalp/run-8urznj6v/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-scalp/run-8urznj6v/holes.jsonl sha256=bee09610f006d9fe7e54483939f1006a3c73f8d9c4cff92e89452de60a797e59
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-scalp/run-8urznj6v/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-scalp/run-8urznj6v/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/gb-scalp/run-8urznj6v/fixtures.json sha256=09ad4f415c85a5cc3ea1b0457ae48e1ee57d788e263139bd467873503c86a2c0
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/gb-scalp/run-8urznj6v/cohort.json sha256=ee41aebb10ac133b2538edf601e3c37e6fe2ba23c278cc58a5fa5171d221f5a5
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/gb-scalp/run-8urznj6v/coverage.json sha256=2e2056726bfbb6137dddeef4cc5f7b5e62aaabdc7c1998e97338d4178fd33533
