# JETBUNDLE-STATES method pass

formula_version: `method-pack-v1`
implementation_checks: `checks_passed`
historical_discovery: `unavailable`
created_at: `2026-09-12T18:02:57Z`

Implementation checks, source reconstruction and historical discovery are separate results. A passing check verifies the report's implementation evidence; it does not establish every private source setting or a historical sample.

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
JETBUNDLE-STATES | state_observation | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states.md
JETBUNDLE-STATES | transition_observation | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states.md

## Summary

- predicate: state_observation
- Historical counts: unavailable (search not completed).
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12-completion-v2`; source contracts checked against their recorded hashes.

branch | complete selector | unavailable inputs
--- | --- | ---
A | no | participation_record_complete, response_record_complete, state
B | no | participation_record_complete, response_record_complete, state
D | no | participation_record_complete, response_record_complete, state
E | no | participation_record_complete, response_record_complete, state
W | no | participation_record_complete, response_record_complete, state

NQ is eligible; AAPL and ten levels are illustrative. Automatic state windows, qualitative thresholds and priority rules remain unspecified. Native evidence must cover the declared local event/depth scope; missing action/lifecycle data is a separate input limitation.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `B` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `A` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `D` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `E` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `W` (historical_discovery): historical discovery unavailable; denominator unestablished.

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
state_observation | historical_discovery | raw_derived | None |  | — | — | — | — | — | —
transition_observation | historical_discovery | raw_derived | None |  | — | — | — | — | — | —

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114378, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 636; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"assembly_implementation_failures": 0, "detected_causal_violations": 32, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "missing_operand_implementations": 0, "output_schema_failures": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `662463b545394e663937be2d83e0677f50492dc3`; content hash `4962839b1ad3f3216b1541abad364b7a069b1ef94acc88b679df16c614141c97`.

## Separate acceptance dimensions

- software_completeness: `{"fixture_checks": 141, "fixture_failures": 0, "missing_operand_implementations": 0, "operand_count": 20, "output_contract_checks": 30, "output_schema_failures": 0, "scope": "Report checks; full stage acceptance is recorded in the completion obligation matrix.", "status": "checks_passed"}`
- source_ambiguity: `{"selector_review": "/workspace/implementation/src/trading_research/research/method_pack/discovery_audit.json", "source_case_catalog": "/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json", "status": "limitations_recorded"}`
- data_coverage: `{"inventory_is_continuity_proof": false, "objects_with_unknown_coverage": 0, "resolved_objects": 0, "status": "per_observation"}`
- source_case_agreement: `{"performance_estimate": false, "source_illustration_episodes": 0, "status": "separate_chart_review"}`
- historical_discovery: `{"candidate_count": null, "reason": "The full branch requires unavailable source definitions or actual case/process records.", "search_completed": false, "status": "unavailable"}`

Historical discovery is unavailable. Its denominator is unestablished; zero ledger rows do not report a completed search with zero candidates.

## Required family tables

Status reports implementation checks first, followed by the separately scoped evidence result. The audit verdict covers implementation checks; unknown historical denominators remain unavailable.

family | variant | n | faithful_disagreements | status | report path
--- | --- | --- | --- | --- | ---
JETBUNDLE-STATES | state_observation / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states.md
JETBUNDLE-STATES | transition_observation / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states.md

family | id | verdict | fixture | leakage | proxy-as-faithful | notes
--- | --- | --- | --- | --- | --- | ---
JETBUNDLE-STATES | M10 | checks_passed | 0 failures | 0 | 0 | implementation checks; historical discovery unavailable; source agreement separate; schema failures=0; missing bindings=0

## Holes

- **Source-complete candidate discovery:** The framework applies to native NQ or another declared instrument. AAPL's ten-level sample is an illustration, not an instrument or universal depth requirement ([MATH] pp.3, 10, 16; user clarification 2026-09-12). Complete automatic classifier/window/threshold definitions remain absent. Native event and depth coverage must support the selected observation scope; missing cancellations or off-touch depth cannot be invented. No automatic classifier is claimed by this source-faithful contract.
- **M10-F3 — source/data hole.** Missing source depth/cancel data or heuristic thresholds → automatic state unknown. There is no entry-admission predicate beyond this observation method.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/holes.jsonl sha256=596f4ec5cca0f83efc3f51db1c53d17a41cbfcc8c9d03241475048a718fa71b5
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `assembly.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/assembly.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `operand-producers.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/operand-producers.jsonl sha256=4506c300162944759fc06a3f7d32a0e4795751811991feaa3999751d83c76333
- `output-contracts.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/output-contracts.jsonl sha256=45da19dbc8f047467f9cd0ae4cded679cecdd7697af4686421c7ba9dfa80a7ab
- `native-window-audits.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/native-window-audits.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/fixtures.json sha256=4b7e34e111950cb60d431cfa77c17b8f800234a1b2a3616d140bd98d3d819ca0
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/cohort.json sha256=12587d8f5a094eee5b145909e815964f286000a37a49499492f95f56d06fb4ea
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/completion/jetbundle-states/run-a_8j1qwn/coverage.json sha256=019f9611687675abe41ad79356550ff49ec5c433371c890a96fa36a6226a270e
