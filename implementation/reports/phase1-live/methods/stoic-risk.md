# STOIC-RISK method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T09:45:15Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
STOIC-RISK | printed_ladder | 0 | — | — | — | source_hole | /workspace/implementation/reports/phase1-live/methods/stoic-risk.md

## Summary

- predicate: printed_ladder
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12`; source contracts checked against their recorded hashes.

branch | complete selector | missing source inputs
--- | --- | ---
first | no | validated_process, prior_sample_n, win_rate_known, average_rr_known, mc_loss_streak_known
reset_after_second_win | no | validated_process, prior_sample_n, win_rate_known, average_rr_known, mc_loss_streak_known
second | no | validated_process, prior_sample_n, win_rate_known, average_rr_known, mc_loss_streak_known

The unit is a supplied risk-stage decision following prior process validation. Printed 1/4/1 baseline arithmetic does not select underlying trades, supply a prior journal or resolve activation/other-outcome transitions.

Each branch has a candidate-selector record in the `holes.jsonl` artifact, including its producer rules.

## Branches

- `first` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `second` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `reset_after_second_win` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
printed_ladder | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | —

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds', 'event': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': None, 'event_max_ns': None, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds', 'event': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'calendar': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': None, 'event_max_ns': None, 'calendar_min_ns': None, 'calendar_max_ns': None, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`. File endpoints do not prove continuous coverage.
Relevant files: 0; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 22, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `43fa8e55f5108ca765dd1a520caea1f74d91faf1`; content hash `abb39481bd9ca8e2da5c2d0cc97749a5c61b92f3ab769d7131ddc0989eab88d8`.

## Holes

- **Source-complete candidate discovery:** Only printed-stage arithmetic is reconstructable. Activation heading conflicts with ladder; generic rebasing/other-outcome transitions and Monte Carlo construction are unpublished.
- **M12-F3 — source/data hole.** Unknown Monte Carlo result, general activation conflict or undefined after-loss/rebase transitions → corresponding unknown. No new simulation or profitability assertion.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-k1z2_bvb/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-k1z2_bvb/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-k1z2_bvb/holes.jsonl sha256=43e3982bc1cc21afe5057e8c4846d75533a2cd296a592e76c5ff03f015c1c52c
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-k1z2_bvb/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-k1z2_bvb/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-k1z2_bvb/fixtures.json sha256=30a71e4c87645baee95599131c8165532250d2cbd333b45f9d2575e235527d6c
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-k1z2_bvb/cohort.json sha256=0ad0d510c418226480d711c8ba48b8a1042a1f3e4b73a3d6754a9c8c4c4bad8a
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/stoic-risk/run-k1z2_bvb/coverage.json sha256=4c411c652222c975f6c00ad7e550ce8aa706697ca8f676b5bd478100b22fdb97
