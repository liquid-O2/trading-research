# MEMBER-TWO-REASONS method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T07:55:00Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
MEMBER-TWO-REASONS | sequence | 0 | — | — | 2010:0;2011:0;2012:0;2013:0;2014:0;2015:0;2016:0;2017:0;2018:0;2019:0;2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/member-two-reasons.md

## Summary

- predicate: sequence
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole

## Branches

- `resistance_short` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `planned_return_long` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2010:0;2011:0;2012:0;2013:0;2014:0;2015:0;2016:0;2017:0;2018:0;2019:0;2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0

## Coverage

Requested span: `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114378, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 636; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 56, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `c08725edbaeab2b9b527e8ae919af861d7fc263f`; content hash `2cab034db2917ee91fe1e35d3256b71efcce07a688cc9c1a0fc51c3073f05f32`.

## Holes

- **Source-complete candidate discovery:** Automatic source reaction/node selection and exact local confirmation/risk policies are incomplete. KG1 is optional additional context, not a replacement for either reason.
- **M07-F3 — source/data hole.** Source target prose/ticket conflict is kept as a separate target-policy hole. The long case needs buyers absorbing/holding; do not import Sires's four-check lift-off gate.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/member-two-reasons/run-2jhnq7if/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/member-two-reasons/run-2jhnq7if/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/member-two-reasons/run-2jhnq7if/holes.jsonl sha256=6d69fdff8e9bfdda948a1db1a10b14ead4c446c58fb9a04de444c278dcdf9ebd
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/member-two-reasons/run-2jhnq7if/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/member-two-reasons/run-2jhnq7if/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/member-two-reasons/run-2jhnq7if/fixtures.json sha256=4c28c70a1ec4442ed2930dbe649abeede3a3ebdd2bc229b5e0f564f90cc491c3
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/member-two-reasons/run-2jhnq7if/cohort.json sha256=c3b0962c150bdedf9324fdf0cb33ba97805e866f535fe8057e2e53f31d9c58e0
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/member-two-reasons/run-2jhnq7if/coverage.json sha256=f56d7dc9a2fa094f047f5f00b9bc0641512270b3cc0bf8011437b13ac05aa955
