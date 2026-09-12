# GB-FAIL method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T09:42:54Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
GB-FAIL | sequence | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/gb-fail.md

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
asia_tdo_case | no | bias_recorded, source_session_allowed, risk_defined, objective_fixed, source_tdo_close_confirmed
cash_open_reclaim_case | no | bias_recorded, source_session_allowed, risk_defined, objective_fixed
mss_fvg_refinement | no | bias_recorded, source_session_allowed, risk_defined, objective_fixed, source_hold_confirmed
nyam_box | no | bias_recorded, source_session_allowed, risk_defined, objective_fixed
previous_hour | no | bias_recorded, source_session_allowed, risk_defined, objective_fixed
prior_day_level | no | bias_recorded, source_session_allowed, risk_defined, objective_fixed
prior_month_level | no | bias_recorded, source_session_allowed, risk_defined, objective_fixed
prior_week_level | no | bias_recorded, source_session_allowed, risk_defined, objective_fixed

All eight routes retain source bias/session admission and risk/objective prerequisites. Enumerating five-minute failures alone would change the unit and inclusion rule.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `nyam_box` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `previous_hour` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `asia_tdo_case` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `prior_day_level` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `prior_week_level` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `prior_month_level` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `cash_open_reclaim_case` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `mss_fvg_refinement` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788393600000000000, 'min_ns': 631238400000000000, 'max_ns': 1788393600000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788393600000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1850256000000000000, 'min_ns': 631238400000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 666; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 50, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `43fa8e55f5108ca765dd1a520caea1f74d91faf1`; content hash `abb39481bd9ca8e2da5c2d0cc97749a5c61b92f3ab769d7131ddc0989eab88d8`.

## Holes

- **Source-complete candidate discovery:** Complete five-minute comparisons are calculable for verified references; the full source session/bias/admission selector and several reference clocks remain holes.
- **M02-F3 — source/data hole.** Unspecified London/session clock, source hold detector, prior-period scope or stop policy → corresponding unknown. TDO is not universally mandatory.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-ye4ih4xz/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-ye4ih4xz/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-ye4ih4xz/holes.jsonl sha256=383bc14aa7965f94350406ea26094a1d13d86a7635d7358de9efb5fc7dc0c534
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-ye4ih4xz/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-ye4ih4xz/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-ye4ih4xz/fixtures.json sha256=4c47a5854f5c0ba0434dfa797c7652294da5e78caa747425f6fbfbecbb40b4b2
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-ye4ih4xz/cohort.json sha256=28f1caca6e74392c693d22f52d34e1c5e0fb38dccb643eaf768cd5c76a2381fb
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-ye4ih4xz/coverage.json sha256=81cf564cc0f92fed5181b6566869e03674a41cb448a8136a2bbf028a1642c7c1
