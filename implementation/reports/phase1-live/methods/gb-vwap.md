# GB-VWAP method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T10:46:29Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
GB-VWAP | sequence | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/gb-vwap.md

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
source_long | no | london_high, asia_high, continuation_context, breakout_at, vwap_reset_verified, risk_defined

The source does not complete the session bounds, breakout-bar construction, VWAP reset/basis or full risk/continuation admission. The February 24 illustration is not a historical inclusion rule.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `source_long` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114378, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 636; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 28, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `f7850418c2fffdcbb9b67d52fdea9609e9cbd460`; content hash `30e8f63115b6ecb6d5ab6c62aa8e67675a82cfcfc159f2737d963484f6a9bbf9`.

## Holes

- **Source-complete candidate discovery:** Unavailable until source session bounds, breakout-bar definition, VWAP reset/basis and risk/admission evidence are supplied.
- **M03-F3 — source/data hole.** Remove verified source VWAP reset: unknown even if a 09:30-reset comparison VWAP exists. General target policy is separately unknown and does not become an added entry gate.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-vwap/run-wn0v8sou/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-vwap/run-wn0v8sou/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-vwap/run-wn0v8sou/holes.jsonl sha256=e639fa84d8f744d63945a29e4e144b05c62186c024b0aba5e3b45c45cba2a8e1
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-vwap/run-wn0v8sou/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-vwap/run-wn0v8sou/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/gb-vwap/run-wn0v8sou/fixtures.json sha256=8498fa47bb3353534411fb08db5190fafa1ca2ddbf08801f23cb73a45010aeda
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/gb-vwap/run-wn0v8sou/cohort.json sha256=6481fd3ee64196231eb60acecb6be93c66e4e38934a272cdda6195e48229bddb
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/gb-vwap/run-wn0v8sou/coverage.json sha256=a222358da6ce85bbe1fec17038f64660b9a702583c8857005e64d474ee311025
