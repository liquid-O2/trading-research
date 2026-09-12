# GB-VWAP method pass

formula_version: `method-pack-v1`
implementation_checks: `checks_passed`
historical_discovery: `unavailable`
created_at: `2026-09-12T16:41:25Z`

Implementation checks, source reconstruction and historical discovery are separate results. A passing check verifies the report's implementation evidence; it does not establish every private source setting or a historical sample.

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
GB-VWAP | sequence | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap.md
GB-VWAP | sequence | 0 | — | [0.000000,1.000000] | 2026:0 | checks_passed; evidence_incomplete | /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap.md

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
source_long | no | london_high, asia_high, continuation_context, breakout_at, vwap_reset_verified, risk_defined

The source does not complete the session bounds, breakout-bar construction, VWAP reset/basis or full risk/continuation admission. The February 24 illustration is not a historical inclusion rule.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `source_long` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `source_long` / sequence / fixed_source_comparisons_v2 / native_control: p=0 f=0 u=1 n=0 N=1

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | — | — | — | — | — | —
sequence | fixed_source_comparisons_v2 | native_control | 42002475 | source-cases-v2.0.0 | 0 | 0 | 1 | 0 | 1 | 2026:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114378, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114378, 'basis': 'observed_event_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114378, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 636; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"assembly_implementation_failures": 0, "detected_causal_violations": 28, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "missing_operand_implementations": 0, "output_schema_failures": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `0836e3cbb77b1f56df0754e6c5b723dba256bcd1`; content hash `e784524fdf589f4724564ff5c958c5829710fade5d45f0fe448f9273c71c17ed`.

## Separate acceptance dimensions

- software_completeness: `{"fixture_checks": 123, "fixture_failures": 0, "missing_operand_implementations": 0, "operand_count": 17, "output_contract_checks": 27, "output_schema_failures": 0, "scope": "Report checks; full stage acceptance is recorded in the completion obligation matrix.", "status": "checks_passed"}`
- source_ambiguity: `{"selector_review": "/workspace/implementation/src/trading_research/research/method_pack/discovery_audit.json", "source_case_catalog": "/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json", "status": "limitations_recorded"}`
- data_coverage: `{"inventory_is_continuity_proof": false, "objects_with_unknown_coverage": 0, "resolved_objects": 5, "status": "per_observation"}`
- source_case_agreement: `{"performance_estimate": false, "source_illustration_episodes": 0, "status": "separate_chart_review"}`
- historical_discovery: `{"candidate_count": null, "reason": "The full branch requires unavailable source definitions or actual case/process records.", "search_completed": false, "status": "unavailable"}`

Historical discovery is unavailable. Its denominator is unestablished; zero ledger rows do not report a completed search with zero candidates.

## Required family tables

Status reports implementation checks first, followed by the separately scoped evidence result. The audit verdict covers implementation checks; unknown historical denominators remain unavailable.

family | variant | n | faithful_disagreements | status | report path
--- | --- | --- | --- | --- | ---
GB-VWAP | sequence / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap.md
GB-VWAP | sequence / fixed_source_comparisons_v2 | 0 | — | checks_passed; evidence_incomplete | /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap.md

family | id | verdict | fixture | leakage | proxy-as-faithful | notes
--- | --- | --- | --- | --- | --- | ---
GB-VWAP | M03 | checks_passed | 0 failures | 0 | 0 | implementation checks; historical discovery unavailable; source agreement separate; schema failures=0; missing bindings=0

## Holes

- **Source-complete candidate discovery:** Unavailable until source session bounds, breakout-bar definition, VWAP reset/basis and risk/admission evidence are supplied.
- **M03-F3 — source/data hole.** Remove verified source VWAP reset: unknown even if a 09:30-reset comparison VWAP exists. General target policy is separately unknown and does not become an added entry gate.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/candidates.jsonl sha256=c2070a8faedea2e51d688ac4f47a73fa6224190135673bc0df4a66d36944c36d
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/objects.jsonl sha256=3631f152e0a13c7c02ed8c684ad278ad7f1a044bb74f20b5bcdc62a1863fa877
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/holes.jsonl sha256=27bbf5d6abf6c8214aa1f11633cedea222b1f2b9c54ab54299db5b40dab863a9
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/reference-outcomes.jsonl sha256=fe5746a3d4bd9b4056d19b42ebe3d21b28ff00ab9e259165d077ccd0dc7a12b0
- `assembly.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/assembly.jsonl sha256=e60102502826045a3362109cced9b075882fe43b63f017836353f82db65df7ec
- `operand-producers.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/operand-producers.jsonl sha256=21d0ae4c4760223add5f4baaf96bec15ab526d0ebd1b4ff0cff6122211580a6d
- `output-contracts.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/output-contracts.jsonl sha256=b43b1889ec67685aeb19210ca5db5f8197deaa5ac7c5bd23263fd3b363dd275e
- `native-window-audits.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/native-window-audits.jsonl sha256=33a61642f108a86f81b017d155c6768b48477a3f4f3bf754f04d7bbabc7ef945
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/fixtures.json sha256=72c2e9eb2c22ca57e0f46b6835ceb34076657e751a83a50ddc926cb0f7e3cabb
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/cohort.json sha256=aa9b70fb47fd2b6ddcc213cf938c38734b97a90b513b0890a9adcbbab8a9a75b
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/coverage.json sha256=a222358da6ce85bbe1fec17038f64660b9a702583c8857005e64d474ee311025
- `episodes.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-vwap/run-k0gubp66/episodes.json sha256=25cd646ea65465281d42283153e1c7e461947767de64b4c3845af296a73a82a8
