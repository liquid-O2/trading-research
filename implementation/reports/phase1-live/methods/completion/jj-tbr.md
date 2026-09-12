# JJ-TBR method pass

formula_version: `method-pack-v1`
implementation_checks: `checks_passed`
historical_discovery: `unavailable`
created_at: `2026-09-12T16:40:52Z`

Implementation checks, source reconstruction and historical discovery are separate results. A passing check verifies the report's implementation evidence; it does not establish every private source setting or a historical sample.

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
JJ-TBR | sequence | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr.md
JJ-TBR | management | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr.md
JJ-TBR | sequence | 0 | — | [0.000000,1.000000] | 2026:0 | checks_passed; evidence_incomplete | /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr.md

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
extension_reaction | no | context_fixed, source_confirmation, risk_defined, objective_fixed
internal_rotation | no | context_fixed, source_confirmation, risk_defined, objective_fixed
judas_outbound | no | context_fixed, source_confirmation, risk_defined, objective_fixed
judas_reversal | no | context_fixed, source_confirmation, risk_defined, objective_fixed
other_session | no | context_fixed, source_confirmation, risk_defined, objective_fixed, source_clock_verified, source_case_verified
single_extended | no | context_fixed, source_confirmation, risk_defined, objective_fixed
single_purged | no | context_fixed, source_confirmation, risk_defined, objective_fixed
timed_pzone_reversal | no | context_fixed, source_confirmation, risk_defined, objective_fixed, source_zone_known, source_time_window

All eight routes require source context, confirmation and a preselected risk/objective. Fixed range clocks and projections select measurements, not complete attempts.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `judas_outbound` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `judas_reversal` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `single_extended` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `single_purged` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `internal_rotation` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `internal_rotation` / sequence / fixed_source_comparisons_v2 / native_control: p=0 f=0 u=1 n=0 N=1
- `extension_reaction` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `other_session` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `timed_pzone_reversal` (historical_discovery): historical discovery unavailable; denominator unestablished.

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | — | — | — | — | — | —
management | historical_discovery | raw_derived | None |  | — | — | — | — | — | —
sequence | fixed_source_comparisons_v2 | native_control | 42002475 | source-cases-v2.0.0 | 0 | 0 | 1 | 0 | 1 | 2026:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788393600000000000, 'min_ns': 631238400000000000, 'max_ns': 1788393600000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788393600000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1850256000000000000, 'min_ns': 631238400000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 666; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"assembly_implementation_failures": 0, "detected_causal_violations": 107, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "missing_operand_implementations": 0, "output_schema_failures": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `0836e3cbb77b1f56df0754e6c5b723dba256bcd1`; content hash `e784524fdf589f4724564ff5c958c5829710fade5d45f0fe448f9273c71c17ed`.

## Separate acceptance dimensions

- software_completeness: `{"fixture_checks": 430, "fixture_failures": 0, "missing_operand_implementations": 0, "operand_count": 40, "output_contract_checks": 103, "output_schema_failures": 0, "scope": "Report checks; full stage acceptance is recorded in the completion obligation matrix.", "status": "checks_passed"}`
- source_ambiguity: `{"selector_review": "/workspace/implementation/src/trading_research/research/method_pack/discovery_audit.json", "source_case_catalog": "/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json", "status": "limitations_recorded"}`
- data_coverage: `{"inventory_is_continuity_proof": false, "objects_with_unknown_coverage": 0, "resolved_objects": 1, "status": "per_observation"}`
- source_case_agreement: `{"performance_estimate": false, "source_illustration_episodes": 0, "status": "separate_chart_review"}`
- historical_discovery: `{"candidate_count": null, "reason": "The full branch requires unavailable source definitions or actual case/process records.", "search_completed": false, "status": "unavailable"}`

Historical discovery is unavailable. Its denominator is unestablished; zero ledger rows do not report a completed search with zero candidates.

## Required family tables

Status reports implementation checks first, followed by the separately scoped evidence result. The audit verdict covers implementation checks; unknown historical denominators remain unavailable.

family | variant | n | faithful_disagreements | status | report path
--- | --- | --- | --- | --- | ---
JJ-TBR | sequence / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr.md
JJ-TBR | management / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr.md
JJ-TBR | sequence / fixed_source_comparisons_v2 | 0 | — | checks_passed; evidence_incomplete | /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr.md

family | id | verdict | fixture | leakage | proxy-as-faithful | notes
--- | --- | --- | --- | --- | --- | ---
JJ-TBR | M01 | checks_passed | 0 failures | 0 | 0 | implementation checks; historical discovery unavailable; source agreement separate; schema failures=0; missing bindings=0

## Holes

- **Source-complete candidate discovery:** Unavailable without the source context/location/confirmation selectors. Literal ranges and projections can still be computed for covered windows.
- **M01-F3 — source/data hole.** Remove source confirmation or a required P-zone/EV/Session Stat source value: unknown for that branch. Do not generate the missing engine.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/candidates.jsonl sha256=c8c4a31ff440737076ddbaa4bb2eec57d6c57c1ca510ed5e18d2e852c240b6ed
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/objects.jsonl sha256=5dfe46c0691ce08d95dc45378f8029bf951a0fdeb301627b5ad2fb053247e971
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/holes.jsonl sha256=4a7c7568b1841f2a163c1c14ec83cba61a4ef2b0a6597bd34d1ef187a78b1693
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/reference-outcomes.jsonl sha256=01bd76746564fcf7b5d275d23b91a7d7873f417885b9d0f9211824f39df7ad0e
- `assembly.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/assembly.jsonl sha256=f11266fbdee9421b75dade879587729ac2351e05391a122cbcd5d647bcc67297
- `operand-producers.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/operand-producers.jsonl sha256=32ed6f03aa14bd28cdfe93e4d96f4f7cc0d3785157fed9b29873e4b8804957c1
- `output-contracts.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/output-contracts.jsonl sha256=bb91f86a930827aa9a97f797fe059ac74a31e995a5ffeee79a89f69db14e26fc
- `native-window-audits.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/native-window-audits.jsonl sha256=3ea37e89717c2a909baa0e6a0f6706ec76dfba97645b06e882818f26b4b3aa60
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/fixtures.json sha256=38d92cd4116204ec3a4bd04f5c6a4dde4ca7e529d7bd81fda61673ff2931c2b4
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/cohort.json sha256=331b5c55b06478a5c3a0b0db5421e5925f8b4a4ecdd69367cbd443465f3dc5b9
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/coverage.json sha256=7a26a28b9f662d8234efacf2216c96ab1190e44a3b20c987e2fd9855aeea90b8
- `episodes.json` /workspace/implementation/reports/phase1-live/methods/completion/jj-tbr/run-8ps6c5q_/episodes.json sha256=67f7f5b84007ed18f0d0d2adc07b275109ea434ea47166c60acd5ff59299c9eb
