# JJ-TBR method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T10:45:49Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
JJ-TBR | sequence | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/jj-tbr.md
JJ-TBR | management | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/jj-tbr.md

## Summary

- predicate: sequence
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12`; source contracts checked against their recorded hashes.

branch | complete selector | missing source inputs
--- | --- | ---
extension_reaction | no | context_fixed, source_confirmation, risk_defined, objective_fixed
internal_rotation | no | context_fixed, source_confirmation, risk_defined, objective_fixed
judas_outbound | no | context_fixed, source_confirmation, risk_defined, objective_fixed
judas_reversal | no | context_fixed, source_confirmation, risk_defined, objective_fixed
other_session | no | context_fixed, source_confirmation, risk_defined, objective_fixed, source_clock_verified, source_case_verified
single_extended | no | context_fixed, source_confirmation, risk_defined, objective_fixed
single_purged | no | context_fixed, source_confirmation, risk_defined, objective_fixed
timed_pzone_reversal | no | context_fixed, source_confirmation, risk_defined, objective_fixed, source_zone_known, source_time_window

All eight routes require source context, confirmation and a preselected risk/objective. Fixed range clocks and projections select measurements, not complete attempts.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `judas_outbound` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `judas_reversal` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `single_extended` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `single_purged` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `internal_rotation` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `extension_reaction` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `other_session` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `timed_pzone_reversal` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0
management | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788393600000000000, 'min_ns': 631238400000000000, 'max_ns': 1788393600000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788393600000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1850256000000000000, 'min_ns': 631238400000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 666; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 107, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `f7850418c2fffdcbb9b67d52fdea9609e9cbd460`; content hash `30e8f63115b6ecb6d5ab6c62aa8e67675a82cfcfc159f2737d963484f6a9bbf9`.

## Holes

- **Source-complete candidate discovery:** Unavailable without the source context/location/confirmation selectors. Literal ranges and projections can still be computed for covered windows.
- **M01-F3 — source/data hole.** Remove source confirmation or a required P-zone/EV/Session Stat source value: unknown for that branch. Do not generate the missing engine.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/jj-tbr/run-d4o3s_93/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/jj-tbr/run-d4o3s_93/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/jj-tbr/run-d4o3s_93/holes.jsonl sha256=239c2bbbe9dad42c0c8ea4418f608a0cac3dd61d6ccb6fa831d5b5eb2bba40b0
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/jj-tbr/run-d4o3s_93/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/jj-tbr/run-d4o3s_93/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/jj-tbr/run-d4o3s_93/fixtures.json sha256=531214d7b2c6f09747abc3b22d2ab0daba44a5f9a28f3c11f4411982b87b78e2
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/jj-tbr/run-d4o3s_93/cohort.json sha256=0daba508e0e7e8aeab82966eecc6c5d45682fc986baf4362b7e155284c8530a6
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/jj-tbr/run-d4o3s_93/coverage.json sha256=7a26a28b9f662d8234efacf2216c96ab1190e44a3b20c987e2fd9855aeea90b8
