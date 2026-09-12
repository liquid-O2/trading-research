# JETBUNDLE-STATES method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T10:48:33Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
JETBUNDLE-STATES | state_observation | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/jetbundle-states.md
JETBUNDLE-STATES | transition_observation | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/jetbundle-states.md

## Summary

- predicate: state_observation
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12`; source contracts checked against their recorded hashes.

branch | complete selector | missing source inputs
--- | --- | ---
A | no | participation_record_complete, response_record_complete, state
B | no | participation_record_complete, response_record_complete, state
D | no | participation_record_complete, response_record_complete, state
E | no | participation_record_complete, response_record_complete, state
W | no | participation_record_complete, response_record_complete, state

NQ is eligible; AAPL and ten levels are illustrative. Automatic state windows, qualitative thresholds and priority rules remain unspecified. Native evidence must cover the declared local event/depth scope; missing action/lifecycle data is a separate input limitation.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `B` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `A` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `D` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `E` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `W` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
state_observation | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0
transition_observation | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114378, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 636; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 32, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `f7850418c2fffdcbb9b67d52fdea9609e9cbd460`; content hash `30e8f63115b6ecb6d5ab6c62aa8e67675a82cfcfc159f2737d963484f6a9bbf9`.

## Holes

- **Source-complete candidate discovery:** The framework applies to native NQ or another declared instrument. AAPL's ten-level sample is an illustration, not an instrument or universal depth requirement ([MATH] pp.3, 10, 16; user clarification 2026-09-12). Complete automatic classifier/window/threshold definitions remain absent. Native event and depth coverage must support the selected observation scope; missing cancellations or off-touch depth cannot be invented. No automatic classifier is claimed by this source-faithful contract.
- **M10-F3 — source/data hole.** Missing source depth/cancel data or heuristic thresholds → automatic state unknown. There is no entry-admission predicate beyond this observation method.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/jetbundle-states/run-5w7pmsv2/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/jetbundle-states/run-5w7pmsv2/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/jetbundle-states/run-5w7pmsv2/holes.jsonl sha256=3ee68f1f46c350d1690b6db0fd16eb01fafa7fb190647abde0b5f3e15e25065b
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/jetbundle-states/run-5w7pmsv2/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/jetbundle-states/run-5w7pmsv2/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/jetbundle-states/run-5w7pmsv2/fixtures.json sha256=11b33542de539b8c99a60d9199f1587a248e2c88338517f50ed4ee24b26c5e56
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/jetbundle-states/run-5w7pmsv2/cohort.json sha256=abc2508426950134e106d8b6e62f7c0b713f2bcb5d2b840ea49b37d6384a9beb
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/jetbundle-states/run-5w7pmsv2/coverage.json sha256=019f9611687675abe41ad79356550ff49ec5c433371c890a96fa36a6226a270e
