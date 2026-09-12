# STOIC-RISK method pass

formula_version: `method-pack-v1`
implementation_checks: `checks_passed`
historical_discovery: `unavailable`
created_at: `2026-09-12T16:42:47Z`

Implementation checks, source reconstruction and historical discovery are separate results. A passing check verifies the report's implementation evidence; it does not establish every private source setting or a historical sample.

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
STOIC-RISK | printed_ladder | — | — | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk.md

## Summary

- predicate: printed_ladder
- Historical counts: unavailable (search not completed).
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12-completion-v2`; source contracts checked against their recorded hashes.

branch | complete selector | unavailable inputs
--- | --- | ---
first | no | validated_process, prior_sample_n, win_rate_known, average_rr_known, mc_loss_streak_known
reset_after_second_win | no | validated_process, prior_sample_n, win_rate_known, average_rr_known, mc_loss_streak_known
second | no | validated_process, prior_sample_n, win_rate_known, average_rr_known, mc_loss_streak_known

The unit is a supplied risk-stage decision following prior process validation. Printed 1/4/1 baseline arithmetic does not select underlying trades, supply a prior journal or resolve activation/other-outcome transitions.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `first` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `second` (historical_discovery): historical discovery unavailable; denominator unestablished.
- `reset_after_second_win` (historical_discovery): historical discovery unavailable; denominator unestablished.

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
printed_ladder | historical_discovery | raw_derived | None |  | — | — | — | — | — | —

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds', 'event': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': None, 'event_max_ns': None, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds', 'event': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': None, 'event_max_ns': None, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`. File endpoints do not prove continuous coverage.
Relevant files: 0; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"assembly_implementation_failures": 0, "detected_causal_violations": 22, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "missing_operand_implementations": 0, "output_schema_failures": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `0836e3cbb77b1f56df0754e6c5b723dba256bcd1`; content hash `e784524fdf589f4724564ff5c958c5829710fade5d45f0fe448f9273c71c17ed`.

## Separate acceptance dimensions

- software_completeness: `{"fixture_checks": 97, "fixture_failures": 0, "missing_operand_implementations": 0, "operand_count": 15, "output_contract_checks": 19, "output_schema_failures": 0, "scope": "Report checks; full stage acceptance is recorded in the completion obligation matrix.", "status": "checks_passed"}`
- source_ambiguity: `{"selector_review": "/workspace/implementation/src/trading_research/research/method_pack/discovery_audit.json", "source_case_catalog": "/workspace/implementation/src/trading_research/research/method_pack/source_cases_v2.json", "status": "limitations_recorded"}`
- data_coverage: `{"inventory_is_continuity_proof": false, "objects_with_unknown_coverage": 0, "resolved_objects": 0, "status": "per_observation"}`
- source_case_agreement: `{"performance_estimate": false, "source_illustration_episodes": 0, "status": "separate_chart_review"}`
- historical_discovery: `{"candidate_count": null, "reason": "The full branch requires unavailable source definitions or actual case/process records.", "search_completed": false, "status": "unavailable"}`

Historical discovery is unavailable. Its denominator is unestablished; zero ledger rows do not report a completed search with zero candidates.

## Required family tables

Status reports implementation checks first, followed by the separately scoped evidence result. The audit verdict covers implementation checks; unknown historical denominators remain unavailable.

family | variant | n | faithful_disagreements | status | report path
--- | --- | --- | --- | --- | ---
STOIC-RISK | printed_ladder / historical_discovery | — | — | checks_passed; historical_unavailable | /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk.md

family | id | verdict | fixture | leakage | proxy-as-faithful | notes
--- | --- | --- | --- | --- | --- | ---
STOIC-RISK | M12 | checks_passed | 0 failures | 0 | 0 | implementation checks; historical discovery unavailable; source agreement separate; schema failures=0; missing bindings=0

## Holes

- **Source-complete candidate discovery:** Only printed-stage arithmetic is reconstructable. Activation heading conflicts with ladder; generic rebasing/other-outcome transitions and Monte Carlo construction are unpublished.
- **M12-F3 — source/data hole.** Unknown Monte Carlo result, general activation conflict or undefined after-loss/rebase transitions → corresponding unknown. No new simulation or profitability assertion.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/holes.jsonl sha256=19c3a8fed3c4632075262caa79082f452c625f8e4e70f51cf8a51930d46cd849
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `assembly.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/assembly.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `operand-producers.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/operand-producers.jsonl sha256=9b890a2d3cff378b2d64d7840ac0090d579879f3a7b13252d9d7583d042c3263
- `output-contracts.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/output-contracts.jsonl sha256=28d135f517b4edde65545a191f7d8681901b9473b9954621f33ea8f3ca013ee7
- `native-window-audits.jsonl` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/native-window-audits.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/fixtures.json sha256=08197c2a16826f686a7653b97a89f191a4bd6985c9d259546f48b2de2a81f0a8
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/cohort.json sha256=d0ea6652d6ead4f9ed124a4828c6b94b3a4420985fbfa651bcead51fca327849
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/completion/stoic-risk/run-2w3ldzc3/coverage.json sha256=4c411c652222c975f6c00ad7e550ce8aa706697ca8f676b5bd478100b22fdb97
