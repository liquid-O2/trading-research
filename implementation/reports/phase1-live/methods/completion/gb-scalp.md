# GB-SCALP method pass

formula_version: `method-pack-v1`
implementation_checks: `checks_passed`
historical_discovery: `unavailable`
created_at: `2026-09-12T16:41:26Z`

Implementation checks, source reconstruction and historical discovery are separate results. A passing check verifies the report's implementation evidence; it does not establish every private source setting or a historical sample.

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
GB-SCALP | case_description | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp.md
GB-SCALP | automatic_admission | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp.md

## Summary

- predicate: case_description
- Historical counts: unavailable (search not completed).
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12-completion-v2`; source contracts checked against their recorded hashes.

branch | complete selector | unavailable inputs
--- | --- | ---
bearish_small_scalp | no | direction_recorded_before_entry, small_size_recorded, source_directional_pullback_observed, source_scalp_management_recorded
bullish_discount_pullback | no | direction_recorded_before_entry, small_size_recorded, source_directional_pullback_observed, source_scalp_management_recorded

M04 explicitly returns NULL for automatic_admission. Both branches describe source decisions and management; direction or discount algebra cannot select a scalp.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `bearish_small_scalp` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `bullish_discount_pullback` (historical_discovery): historical discovery unavailable; denominator unestablished.

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
case_description | historical_discovery | raw_derived | None |  | — | — | — | — | — | —
automatic_admission | historical_discovery | raw_derived | None |  | — | — | — | — | — | —

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788393600000000000, 'min_ns': 631238400000000000, 'max_ns': 1788393600000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788393600000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1850256000000000000, 'min_ns': 631238400000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 666; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"assembly_implementation_failures": 0, "detected_causal_violations": 30, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "missing_operand_implementations": 0, "output_schema_failures": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `0836e3cbb77b1f56df0754e6c5b723dba256bcd1`; content hash `e784524fdf589f4724564ff5c958c5829710fade5d45f0fe448f9273c71c17ed`.

## Separate acceptance dimensions

- software_completeness: `{"fixture_checks": 132, "fixture_failures": 0, "missing_operand_implementations": 0, "operand_count": 4, "output_contract_checks": 28, "output_schema_failures": 0, "scope": "Report checks; full stage acceptance is recorded in the completion obligation matrix.", "status": "checks_passed"}`
- source_ambiguity: `{"selector_review": "/workspace/implementation/src/trading_research/research/method_pack/discovery_audit.json", "source_case_catalog": "/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json", "status": "limitations_recorded"}`
- data_coverage: `{"inventory_is_continuity_proof": false, "objects_with_unknown_coverage": 0, "resolved_objects": 0, "status": "per_observation"}`
- source_case_agreement: `{"performance_estimate": false, "source_illustration_episodes": 0, "status": "separate_chart_review"}`
- historical_discovery: `{"candidate_count": null, "reason": "The full branch requires unavailable source definitions or actual case/process records.", "search_completed": false, "status": "unavailable"}`

Historical discovery is unavailable. Its denominator is unestablished; zero ledger rows do not report a completed search with zero candidates.

## Required family tables

Status reports implementation checks first, followed by the separately scoped evidence result. The audit verdict covers implementation checks; unknown historical denominators remain unavailable.

family | variant | n | faithful_disagreements | status | report path
--- | --- | --- | --- | --- | ---
GB-SCALP | case_description / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp.md
GB-SCALP | automatic_admission / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp.md

family | id | verdict | fixture | leakage | proxy-as-faithful | notes
--- | --- | --- | --- | --- | --- | ---
GB-SCALP | M04 | checks_passed | 0 failures | 0 | 0 | implementation checks; historical discovery unavailable; source agreement separate; schema failures=0; missing bindings=0

## Holes

- **Source-complete candidate discovery:** No repeatable source-complete scalp selector is disclosed. Never create a two-box, VWAP or failure-trigger replacement.
- **M04-F3 — source/data hole.** Full trigger, measured-impulse selection, general invalidation and exit algorithm are holes in every automatic scalp-admission result.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/holes.jsonl sha256=549fc384ed6e8966cd4e6e019d9f0fe5810baa47041fd342cb8aad40e98ccd41
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `assembly.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/assembly.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `operand-producers.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/operand-producers.jsonl sha256=677b9bf5f6083c194dd7e8a7bcfec8419e4c7d3bd70c734a2b76e25dad124f82
- `output-contracts.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/output-contracts.jsonl sha256=136547bc5731290f457d53e7fadfe391121dde822a8e558878494636a6ac5692
- `native-window-audits.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/native-window-audits.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/fixtures.json sha256=cdb09d8b77036a35e4537d886dab55efed3753ca4c62e6d887d56b33550c9f54
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/cohort.json sha256=2c391d855a5b93031e062f5cda94984faad41a322c836b066da8e4264d02e5b2
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-scalp/run-d65ww1fy/coverage.json sha256=2e2056726bfbb6137dddeef4cc5f7b5e62aaabdc7c1998e97338d4178fd33533
