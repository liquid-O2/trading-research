# SIRES method pass

formula_version: `method-pack-v1`
implementation_checks: `checks_passed`
historical_discovery: `unavailable`
created_at: `2026-09-12T16:47:13Z`

Implementation checks, source reconstruction and historical discovery are separate results. A passing check verifies the report's implementation evidence; it does not establish every private source setting or a historical sample.

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
SIRES | sequence | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/sires.md
SIRES | case_description | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/sires.md
SIRES | management | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/sires.md
SIRES | reentry | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/sires.md

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
absorption_reward_retest | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, cvd_filter_ok, reward_near_origin
balance_failure_fade | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, long_gamma, balance_context
clean_squeeze | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, fast_release, opposing_pullback_aggression_absorbed
defended_band_continuation | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, refresh_consistent, prior_band_control
dom_rejection | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, source_dom_confirmation
footprint_confirmed_reaction | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, source_flow_confirmation, intrabar_poc_flip
kg1_retest | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, source_kg1_level_known, aggression_confirms
microbalance_break | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, microbalance_frozen, directional_strength
ofm_aggressive | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, short_gamma, cvd_filter_ok, catalyst_at
ofm_passive | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, tape_died_at_failure, buyers_area_identified
stop_four_stage | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, delta_filter_ok, opponent_thinning, daily_r_before
vwap_deviation_fade | no | thesis_alive, auction_route_ok, location_fixed, objective_fixed, risk_defined, source_vwap_known, cvd_filter_ok, ladder_confirmation

The common M05 sequence gates block every confirmed branch: actual live thesis, selected auction route/band and source risk/objective are required. Numeric STOP distances do not remove those shared prerequisites. The four incomplete cases remain outside confirmed entries.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `dom_rejection` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `absorption_reward_retest` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `stop_four_stage` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `footprint_confirmed_reaction` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `vwap_deviation_fade` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `ofm_aggressive` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `ofm_passive` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `clean_squeeze` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `balance_failure_fade` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `defended_band_continuation` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `microbalance_break` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `kg1_retest` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `late_resistance_fade_case` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `ofm_early_refill_case` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `pre_file_early` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `third_retest_case` (historical_discovery): historical discovery unavailable; denominator unestablished.

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | — | — | — | — | — | —
case_description | historical_discovery | raw_derived | None |  | — | — | — | — | — | —
management | historical_discovery | raw_derived | None |  | — | — | — | — | — | —
reentry | historical_discovery | raw_derived | None |  | — | — | — | — | — | —

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788465600001000000, 'min_ns': 1283644800000000000, 'max_ns': 1788465600001000000, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788465600001000000, 'min_ns': 1283644800000000000, 'max_ns': 1788465600001000000, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788566400000000000, 'min_ns': 631238400000000000, 'max_ns': 1788566400000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788465600001000000, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788566400000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': -655603200000000000, 'max': 1850256000000000000, 'min_ns': -655603200000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': -655603200000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 27564; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"assembly_implementation_failures": 0, "detected_causal_violations": 233, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "missing_operand_implementations": 0, "output_schema_failures": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `0836e3cbb77b1f56df0754e6c5b723dba256bcd1`; content hash `e784524fdf589f4724564ff5c958c5829710fade5d45f0fe448f9273c71c17ed`.

## Separate acceptance dimensions

- software_completeness: `{"fixture_checks": 961, "fixture_failures": 0, "missing_operand_implementations": 0, "operand_count": 135, "output_contract_checks": 230, "output_schema_failures": 0, "scope": "Report checks; full stage acceptance is recorded in the completion obligation matrix.", "status": "checks_passed"}`
- source_ambiguity: `{"selector_review": "/workspace/implementation/src/trading_research/research/method_pack/discovery_audit.json", "source_case_catalog": "/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json", "status": "limitations_recorded"}`
- data_coverage: `{"inventory_is_continuity_proof": false, "objects_with_unknown_coverage": 0, "resolved_objects": 0, "status": "per_observation"}`
- source_case_agreement: `{"performance_estimate": false, "source_illustration_episodes": 0, "status": "separate_chart_review"}`
- historical_discovery: `{"candidate_count": null, "reason": "The full branch requires unavailable source definitions or actual case/process records.", "search_completed": false, "status": "unavailable"}`

Historical discovery is unavailable. Its denominator is unestablished; zero ledger rows do not report a completed search with zero candidates.

## Required family tables

Status reports implementation checks first, followed by the separately scoped evidence result. The audit verdict covers implementation checks; unknown historical denominators remain unavailable.

family | variant | n | faithful_disagreements | status | report path
--- | --- | --- | --- | --- | ---
SIRES | sequence / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/sires.md
SIRES | case_description / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/sires.md
SIRES | management / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/sires.md
SIRES | reentry / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/sires.md

family | id | verdict | fixture | leakage | proxy-as-faithful | notes
--- | --- | --- | --- | --- | --- | ---
SIRES | M05 | checks_passed | 0 failures | 0 | 0 | implementation checks; historical discovery unavailable; source agreement separate; schema failures=0; missing bindings=0

## Holes

- **Source-complete candidate discovery:** Most automatic selectors are source-incomplete: current auction bands, context, local qualitative flow, range bars, CVD reference, proprietary levels and full account journals. Implement their explicit holes, not substitutes.
- **M05-F3 — source/data hole.** Missing exact CVD reference, source state/refresh criterion, full required depth, gamma/KG1 readout or thesis death input → unknown. Incomplete early/third-test/late-fade cases remain case-description rows and do not enter confirmed-branch n.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/holes.jsonl sha256=d7a92a5b659aa331a5477025b38154cf082c7189d58a41268c5be761eccf8bdf
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `assembly.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/assembly.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `operand-producers.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/operand-producers.jsonl sha256=47a94f76aafc80d4811635ee520bc546b94d45dfd28484ee29af09f76ae7e5ff
- `output-contracts.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/output-contracts.jsonl sha256=cc7ef85e5a1d14768a0bfe8d40cd4370493af6a24b147f1833664253d2c08d08
- `native-window-audits.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/native-window-audits.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/fixtures.json sha256=6a534307de3311d2e9d233e6549c4d8eb1b123003a95c3ae9046c556b380bde0
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/cohort.json sha256=e60417fa0e95a410e77cbb010c5260679a6d10430ac34e2d0049f37309796d59
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/completion/sires/run-1rf7mvkj/coverage.json sha256=13c78ad870917093dee6f259530a09e2e082e6c903bf8ffd7d1a184fcd777162
