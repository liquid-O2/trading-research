# STOIC-RISK method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T07:56:07Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
STOIC-RISK | printed_ladder | 0 | — | — | — | source_hole | /workspace/implementation/reports/phase1-live/methods/stoic-risk.md

## Summary

- predicate: printed_ladder
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole

## Branches

- `first` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `second` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `reset_after_second_win` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
printed_ladder | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | —

## Coverage

Requested span: `{'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds', 'event': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': None, 'event_max_ns': None, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds', 'event': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': None, 'event_max_ns': None, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`. File endpoints do not prove continuous coverage.
Relevant files: 0; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 22, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `c08725edbaeab2b9b527e8ae919af861d7fc263f`; content hash `2cab034db2917ee91fe1e35d3256b71efcce07a688cc9c1a0fc51c3073f05f32`.

## Holes

- **Source-complete candidate discovery:** Only printed-stage arithmetic is reconstructable. Activation heading conflicts with ladder; generic rebasing/other-outcome transitions and Monte Carlo construction are unpublished.
- **M12-F3 — source/data hole.** Unknown Monte Carlo result, general activation conflict or undefined after-loss/rebase transitions → corresponding unknown. No new simulation or profitability assertion.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-sq58156x/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-sq58156x/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-sq58156x/holes.jsonl sha256=a5ac45845608eeb8a6e01d027a942de556ba862e25efaeba4a78ed6e31e579ea
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-sq58156x/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-sq58156x/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-sq58156x/fixtures.json sha256=db665b7f58de213861a8fd67e0f9f028f8fff11dcf7cefb9368f4b7960c7fed4
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-sq58156x/cohort.json sha256=5544474aff33ec65a11f45d585ef8fe65d5111c950b4a1e02fe03584f24982e2
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-sq58156x/coverage.json sha256=4c411c652222c975f6c00ad7e550ce8aa706697ca8f676b5bd478100b22fdb97
