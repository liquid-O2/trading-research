# GB-FAIL method pass

formula_version: `method-pack-v1`
implementation_checks: `checks_passed`
historical_discovery: `unavailable`
created_at: `2026-09-12T16:41:01Z`

Implementation checks, source reconstruction and historical discovery are separate results. A passing check verifies the report's implementation evidence; it does not establish every private source setting or a historical sample.

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
GB-FAIL | sequence | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/gb-fail.md
GB-FAIL | sequence | 0 | — | [0.000000,1.000000] | 2025:0 | checks_passed; evidence_incomplete | /workspace/implementation/reports/phase1-live/methods/completion/gb-fail.md

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

- `nyam_box` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `nyam_box` / sequence / fixed_source_comparisons_v2 / native_control: p=0 f=0 u=1 n=0 N=1
- `previous_hour` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `asia_tdo_case` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `prior_day_level` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `prior_week_level` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `prior_month_level` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `cash_open_reclaim_case` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `mss_fvg_refinement` (historical_discovery): historical discovery unavailable; denominator unestablished.

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | — | — | — | — | — | —
sequence | fixed_source_comparisons_v2 | native_control | 158704 | source-cases-v2.0.0 | 0 | 0 | 1 | 0 | 1 | 2025:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788393600000000000, 'min_ns': 631238400000000000, 'max_ns': 1788393600000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788393600000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1850256000000000000, 'min_ns': 631238400000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 666; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"assembly_implementation_failures": 0, "detected_causal_violations": 50, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "missing_operand_implementations": 0, "output_schema_failures": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `0836e3cbb77b1f56df0754e6c5b723dba256bcd1`; content hash `e784524fdf589f4724564ff5c958c5829710fade5d45f0fe448f9273c71c17ed`.

## Separate acceptance dimensions

- software_completeness: `{"fixture_checks": 210, "fixture_failures": 0, "missing_operand_implementations": 0, "operand_count": 27, "output_contract_checks": 48, "output_schema_failures": 0, "scope": "Report checks; full stage acceptance is recorded in the completion obligation matrix.", "status": "checks_passed"}`
- source_ambiguity: `{"selector_review": "/workspace/implementation/src/trading_research/research/method_pack/discovery_audit.json", "source_case_catalog": "/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json", "status": "limitations_recorded"}`
- data_coverage: `{"inventory_is_continuity_proof": false, "objects_with_unknown_coverage": 0, "resolved_objects": 1, "status": "per_observation"}`
- source_case_agreement: `{"performance_estimate": false, "source_illustration_episodes": 0, "status": "separate_chart_review"}`
- historical_discovery: `{"candidate_count": null, "reason": "The full branch requires unavailable source definitions or actual case/process records.", "search_completed": false, "status": "unavailable"}`

Historical discovery is unavailable. Its denominator is unestablished; zero ledger rows do not report a completed search with zero candidates.

## Required family tables

Status reports implementation checks first, followed by the separately scoped evidence result. The audit verdict covers implementation checks; unknown historical denominators remain unavailable.

family | variant | n | faithful_disagreements | status | report path
--- | --- | --- | --- | --- | ---
GB-FAIL | sequence / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/gb-fail.md
GB-FAIL | sequence / fixed_source_comparisons_v2 | 0 | — | checks_passed; evidence_incomplete | /workspace/implementation/reports/phase1-live/methods/completion/gb-fail.md

family | id | verdict | fixture | leakage | proxy-as-faithful | notes
--- | --- | --- | --- | --- | --- | ---
GB-FAIL | M02 | checks_passed | 0 failures | 0 | 0 | implementation checks; historical discovery unavailable; source agreement separate; schema failures=0; missing bindings=0

## Holes

- **Source-complete candidate discovery:** Complete five-minute comparisons are calculable for verified references; the full source session/bias/admission selector and several reference clocks remain holes.
- **M02-F3 — source/data hole.** Unspecified London/session clock, source hold detector, prior-period scope or stop policy → corresponding unknown. TDO is not universally mandatory.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/candidates.jsonl sha256=00439f1e60616e0e58133f2be4293859411cf7bce16d51af7c19b06f33975182
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/objects.jsonl sha256=a6f4965937f3c65c6d0d6b73ac8f664b6d37596ab07ba8a759f8f0c66f82b7f7
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/holes.jsonl sha256=a54e4ddbcb08213c61d3f89e644ba0fd0f4d5128816b0e7ca2d9a46f80dc94b1
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/reference-outcomes.jsonl sha256=cd3a772993558ed34f16f35e6dd788c6612678e39f4e5660ee2504521d0b2dd8
- `assembly.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/assembly.jsonl sha256=ca080ffee705d8a55f8d799451d27d522b75ce6ade6ce562b11de09394f1c8f8
- `operand-producers.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/operand-producers.jsonl sha256=7c9c03aa822365285dc1852d7da94aca5498c71d30f750266a03d0b79f1dc86a
- `output-contracts.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/output-contracts.jsonl sha256=5f7c8da8a83d0636dc980721be78f54f2d7888b352e015df4bbe4e07b906b9bc
- `native-window-audits.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/native-window-audits.jsonl sha256=ceebc94d8a69ae9a1aa7c0cd0af3f9337cd7211625e8de921bfb11ace9e1fb4d
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/fixtures.json sha256=6c95450ec0e44e8f2fc02e1d723611a4aeec8cd1ba290ab44567b45a875c0db4
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/cohort.json sha256=e96b2a01310e4a88577e3ce0478af6cf0d8422a6ff96675f414e18594eaebd06
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/coverage.json sha256=81cf564cc0f92fed5181b6566869e03674a41cb448a8136a2bbf028a1642c7c1
- `episodes.json` /workspace/implementation/reports/phase1-live/methods/completion/gb-fail/run-w4m8mzqi/episodes.json sha256=21a5d9c170ca8e11d56014bbc4fa8a636af385c7d58f535ff4ca030a8743257f
