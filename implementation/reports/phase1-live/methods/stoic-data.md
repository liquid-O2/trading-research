# STOIC-DATA method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T10:49:00Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
STOIC-DATA | process | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/stoic-data.md
STOIC-DATA | macro_application | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/stoic-data.md

## Summary

- predicate: process
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12`; source contracts checked against their recorded hashes.

branch | complete selector | missing source inputs
--- | --- | ---
macro_application | no | process_spec_frozen, inclusion_rule_fixed, all_eligible_observations_retained, aggregate_winner_loser_comparison_recorded, revision_uses_only_prior_sample, cycle_and_indicator_rules_recorded, historical_comparison_defined
process_review | no | process_spec_frozen, inclusion_rule_fixed, all_eligible_observations_retained, aggregate_winner_loser_comparison_recorded, revision_uses_only_prior_sample

The unit is a supplied process-review block. Acquired market/macro rows are not review blocks, complete trading recipes or journals. The macro branch also lacks the custom cycle/C-score/trend rules.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `process_review` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `macro_application` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
process | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0
macro_application | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 631238400000000000, 'max': 1788566400000000000, 'min_ns': 631238400000000000, 'max_ns': 1788566400000000000, 'basis': 'calendar_date_bounds', 'event': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788566400000000000, 'min_ns': 631238400000000000, 'max_ns': 1788566400000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': None, 'event_max_ns': None, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788566400000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': -655603200000000000, 'max': 1850256000000000000, 'min_ns': -655603200000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': -655603200000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`. File endpoints do not prove continuous coverage.
Relevant files: 553; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 34, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `f7850418c2fffdcbb9b67d52fdea9609e9cbd460`; content hash `30e8f63115b6ecb6d5ab6c62aa8e67675a82cfcfc159f2737d963484f6a9bbf9`.

## Holes

- **Source-complete candidate discovery:** The full trading recipe, macro series/transforms/C-score/cycle/trend-strength classifiers and decision thresholds are unpublished. Audit supplied process records; do not invent a trading or current macro model.
- **M11-F3 — source/data hole.** Missing series/vintages or custom metric/cycle rules leaves macro application unknown while separately complete process-record checks may be reported.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-data/run-o3s4x3e1/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-data/run-o3s4x3e1/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-data/run-o3s4x3e1/holes.jsonl sha256=dee2a952129dca7b2f2ad71ede86561bed94d1caef8fef48b429d83cb6ed7412
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-data/run-o3s4x3e1/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-data/run-o3s4x3e1/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/stoic-data/run-o3s4x3e1/fixtures.json sha256=bd58309899f47d0314cb5df456d5678ae4c65fadb2712b1454c5297a70e03176
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/stoic-data/run-o3s4x3e1/cohort.json sha256=47e2a398bab815c58c86a7d8c4511299cb64e062287cbbd74c63e5ffb3cabe1f
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/stoic-data/run-o3s4x3e1/coverage.json sha256=f62aac397e6bd8917b3fb904261ebd02b02bddbdc0be8c0fc06376caad765d77
