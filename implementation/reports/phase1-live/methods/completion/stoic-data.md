# STOIC-DATA method pass

formula_version: `method-pack-v1`
implementation_checks: `checks_passed`
historical_discovery: `unavailable`
created_at: `2026-09-12T16:45:40Z`

Implementation checks, source reconstruction and historical discovery are separate results. A passing check verifies the report's implementation evidence; it does not establish every private source setting or a historical sample.

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
STOIC-DATA | process | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/stoic-data.md
STOIC-DATA | macro_application | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/stoic-data.md

## Summary

- predicate: process
- Historical counts: unavailable (search not completed).
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12-completion-v2`; source contracts checked against their recorded hashes.

branch | complete selector | unavailable inputs
--- | --- | ---
macro_application | no | process_spec_frozen, inclusion_rule_fixed, all_eligible_observations_retained, aggregate_winner_loser_comparison_recorded, revision_uses_only_prior_sample, cycle_and_indicator_rules_recorded, historical_comparison_defined
process_review | no | process_spec_frozen, inclusion_rule_fixed, all_eligible_observations_retained, aggregate_winner_loser_comparison_recorded, revision_uses_only_prior_sample

The unit is a supplied process-review block. Acquired market/macro rows are not review blocks, complete trading recipes or journals. The macro branch also lacks the custom cycle/C-score/trend rules.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `process_review` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `macro_application` (historical_discovery): historical discovery unavailable; denominator unestablished.

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
process | historical_discovery | raw_derived | None |  | — | — | — | — | — | —
macro_application | historical_discovery | raw_derived | None |  | — | — | — | — | — | —

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 631238400000000000, 'max': 1788566400000000000, 'min_ns': 631238400000000000, 'max_ns': 1788566400000000000, 'basis': 'calendar_date_bounds', 'event': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788566400000000000, 'min_ns': 631238400000000000, 'max_ns': 1788566400000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': None, 'event_max_ns': None, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788566400000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': -655603200000000000, 'max': 1850256000000000000, 'min_ns': -655603200000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': -655603200000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`. File endpoints do not prove continuous coverage.
Relevant files: 553; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"assembly_implementation_failures": 0, "detected_causal_violations": 34, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "missing_operand_implementations": 0, "output_schema_failures": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `0836e3cbb77b1f56df0754e6c5b723dba256bcd1`; content hash `e784524fdf589f4724564ff5c958c5829710fade5d45f0fe448f9273c71c17ed`.

## Separate acceptance dimensions

- software_completeness: `{"fixture_checks": 138, "fixture_failures": 0, "missing_operand_implementations": 0, "operand_count": 13, "output_contract_checks": 30, "output_schema_failures": 0, "scope": "Report checks; full stage acceptance is recorded in the completion obligation matrix.", "status": "checks_passed"}`
- source_ambiguity: `{"selector_review": "/workspace/implementation/src/trading_research/research/method_pack/discovery_audit.json", "source_case_catalog": "/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json", "status": "limitations_recorded"}`
- data_coverage: `{"inventory_is_continuity_proof": false, "objects_with_unknown_coverage": 0, "resolved_objects": 0, "status": "per_observation"}`
- source_case_agreement: `{"performance_estimate": false, "source_illustration_episodes": 0, "status": "separate_chart_review"}`
- historical_discovery: `{"candidate_count": null, "reason": "The full branch requires unavailable source definitions or actual case/process records.", "search_completed": false, "status": "unavailable"}`

Historical discovery is unavailable. Its denominator is unestablished; zero ledger rows do not report a completed search with zero candidates.

## Required family tables

Status reports implementation checks first, followed by the separately scoped evidence result. The audit verdict covers implementation checks; unknown historical denominators remain unavailable.

family | variant | n | faithful_disagreements | status | report path
--- | --- | --- | --- | --- | ---
STOIC-DATA | process / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/stoic-data.md
STOIC-DATA | macro_application / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/stoic-data.md

family | id | verdict | fixture | leakage | proxy-as-faithful | notes
--- | --- | --- | --- | --- | --- | ---
STOIC-DATA | M11 | checks_passed | 0 failures | 0 | 0 | implementation checks; historical discovery unavailable; source agreement separate; schema failures=0; missing bindings=0

## Holes

- **Source-complete candidate discovery:** The full trading recipe, macro series/transforms/C-score/cycle/trend-strength classifiers and decision thresholds are unpublished. Audit supplied process records; do not invent a trading or current macro model.
- **M11-F3 — source/data hole.** Missing series/vintages or custom metric/cycle rules leaves macro application unknown while separately complete process-record checks may be reported.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/holes.jsonl sha256=63f458df0419f6f6b454eace193a3e959b0dec8cde911fe36686402ff1f5731e
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `assembly.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/assembly.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `operand-producers.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/operand-producers.jsonl sha256=9f0d744f1a88aa40481c551f234fabda9c77dcff73883d8ca0d53163ca319408
- `output-contracts.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/output-contracts.jsonl sha256=25e3950bc15e6642dfbd4519ea1b6073a013e6f26964a55ee508d22c400dad4d
- `native-window-audits.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/native-window-audits.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/fixtures.json sha256=35f9eac53d0c53009a7232d037dfc1c3531d9422531214542e0eb26c45a048a7
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/cohort.json sha256=3dbe172ceeb8e8f3b69b959e3587a36c72c7d861993e140ea1cef0f34f7b1d10
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/completion/stoic-data/run-mzbep8n5/coverage.json sha256=f62aac397e6bd8917b3fb904261ebd02b02bddbdc0be8c0fc06376caad765d77
