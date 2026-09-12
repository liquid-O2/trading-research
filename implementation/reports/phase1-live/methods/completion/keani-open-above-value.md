# KEANI-OPEN-ABOVE-VALUE method pass

formula_version: `method-pack-v1`
implementation_checks: `checks_passed`
historical_discovery: `unavailable`
created_at: `2026-09-12T18:02:34Z`

Implementation checks, source reconstruction and historical discovery are separate results. A passing check verifies the report's implementation evidence; it does not establish every private source setting or a historical sample.

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
KEANI-OPEN-ABOVE-VALUE | sequence | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value.md

## Summary

- predicate: sequence
- Historical counts: unavailable (search not completed).
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12-completion-v2`; source contracts checked against their recorded hashes.

branch | complete selector | unavailable inputs
--- | --- | ---
source_long | no | prior_value_fixed, developing_value_builds_higher, source_rejection_observed, aggressive_buy_imbalance_break, time_of_day_allowed, risk_defined, objective_fixed

Whole-A low is computable, but source value construction, higher-building value/control, imbalance settings and near-10:00 tolerance do not define a complete selector.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `source_long` (historical_discovery): historical discovery unavailable; denominator unestablished.

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | — | — | — | — | — | —

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114378, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 636; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"assembly_implementation_failures": 0, "detected_causal_violations": 49, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "missing_operand_implementations": 0, "output_schema_failures": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `662463b545394e663937be2d83e0677f50492dc3`; content hash `4962839b1ad3f3216b1541abad364b7a069b1ef94acc88b679df16c614141c97`.

## Separate acceptance dimensions

- software_completeness: `{"fixture_checks": 205, "fixture_failures": 0, "missing_operand_implementations": 0, "operand_count": 23, "output_contract_checks": 47, "output_schema_failures": 0, "scope": "Report checks; full stage acceptance is recorded in the completion obligation matrix.", "status": "checks_passed"}`
- source_ambiguity: `{"selector_review": "/workspace/implementation/src/trading_research/research/method_pack/discovery_audit.json", "source_case_catalog": "/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json", "status": "limitations_recorded"}`
- data_coverage: `{"inventory_is_continuity_proof": false, "objects_with_unknown_coverage": 0, "resolved_objects": 0, "status": "per_observation"}`
- source_case_agreement: `{"performance_estimate": false, "source_illustration_episodes": 0, "status": "separate_chart_review"}`
- historical_discovery: `{"candidate_count": null, "reason": "The full branch requires unavailable source definitions or actual case/process records.", "search_completed": false, "status": "unavailable"}`

Historical discovery is unavailable. Its denominator is unestablished; zero ledger rows do not report a completed search with zero candidates.

## Required family tables

Status reports implementation checks first, followed by the separately scoped evidence result. The audit verdict covers implementation checks; unknown historical denominators remain unavailable.

family | variant | n | faithful_disagreements | status | report path
--- | --- | --- | --- | --- | ---
KEANI-OPEN-ABOVE-VALUE | sequence / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value.md

family | id | verdict | fixture | leakage | proxy-as-faithful | notes
--- | --- | --- | --- | --- | --- | ---
KEANI-OPEN-ABOVE-VALUE | M08 | checks_passed | 0 failures | 0 | 0 | implementation checks; historical discovery unavailable; source agreement separate; schema failures=0; missing bindings=0

## Holes

- **Source-complete candidate discovery:** Exact source value/imbalance settings, near 10:00 timing tolerance, automatic developing-value/control selectors and source risk/target records are incomplete.
- **M08-F3 — source/data hole.** Unknown exact source near 10:00 timing convention or diagonal settings stays unknown; do not select a minute tolerance or a developing VAL short mirror.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/holes.jsonl sha256=6e47982f192bb58c3ba44eed8b4f3ece7b380cf5ec71458f8574cb4158772d59
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `assembly.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/assembly.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `operand-producers.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/operand-producers.jsonl sha256=59a7e093809b8c2093911d7cb0200211962d98c5adf73ab3a367bbe8eac1b63d
- `output-contracts.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/output-contracts.jsonl sha256=bec2fa850a2a62ab05b31e0dfcc8ae92a78524e384f1e9ba60726a7c7fc70a93
- `native-window-audits.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/native-window-audits.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/fixtures.json sha256=b019e95c63739785d24f00909db09f1138c97531917d02187dd4372939bb0234
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/cohort.json sha256=f79a09a9efbd40300a7ea2d39721ba517097c3b7e2ad1ce2b773ada2edf2111b
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/completion/keani-open-above-value/run-gq9c7q82/coverage.json sha256=42c3a3eadb0501d9b5d2d11f986f14375630a8991983ffb5faf73af43df21870
