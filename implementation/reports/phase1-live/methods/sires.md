# SIRES method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T09:48:25Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
SIRES | sequence | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/sires.md
SIRES | case_description | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/sires.md
SIRES | management | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/sires.md
SIRES | reentry | 0 | — | — | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/sires.md

## Summary

- predicate: sequence
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole
- Synthetic fixtures, chart geometry checks and archive rows are excluded from p/f/u/n/N.

## Candidate selector review

Audit: `source-selector-review-2026-09-12`; source contracts checked against their recorded hashes.

branch | complete selector | missing source inputs
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

- `dom_rejection` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `absorption_reward_retest` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `stop_four_stage` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `footprint_confirmed_reaction` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `vwap_deviation_fade` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `ofm_aggressive` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `ofm_passive` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `clean_squeeze` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `balance_failure_fade` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `defended_band_continuation` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `microbalance_break` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `kg1_retest` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `late_resistance_fade_case` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `ofm_early_refill_case` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `pre_file_early` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `third_retest_case` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0
case_description | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0
management | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0
reentry | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0

## Coverage

Historical study scope: `{'primary_instrument': 'NQ', 'start_date': '2020-01-01', 'end': 'actual acquired endpoint for each selected dependency', 'source_ref': '/workspace/planning/phase-1-live/DATA_SCOPE.md', 'note': 'Archive coverage is inventory only. Source-native non-NQ/process requirements are not replaced with NQ observations.'}`.
Archive requested span (inventory, not the method sample): `{'min': 1283644800000000000, 'max': 1788465600001000000, 'min_ns': 1283644800000000000, 'max_ns': 1788465600001000000, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788465600001000000, 'min_ns': 1283644800000000000, 'max_ns': 1788465600001000000, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788566400000000000, 'min_ns': 631238400000000000, 'max_ns': 1788566400000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788465600001000000, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788566400000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': -655603200000000000, 'max': 1850256000000000000, 'min_ns': -655603200000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': -655603200000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 27564; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 233, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `43fa8e55f5108ca765dd1a520caea1f74d91faf1`; content hash `abb39481bd9ca8e2da5c2d0cc97749a5c61b92f3ab769d7131ddc0989eab88d8`.

## Holes

- **Source-complete candidate discovery:** Most automatic selectors are source-incomplete: current auction bands, context, local qualitative flow, range bars, CVD reference, proprietary levels and full account journals. Implement their explicit holes, not substitutes.
- **M05-F3 — source/data hole.** Missing exact CVD reference, source state/refresh criterion, full required depth, gamma/KG1 readout or thesis death input → unknown. Incomplete early/third-test/late-fade cases remain case-description rows and do not enter confirmed-branch n.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/sires/run-xbklzdqi/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/sires/run-xbklzdqi/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/sires/run-xbklzdqi/holes.jsonl sha256=eaef6b10a36d56d020f478f1967277dced3827856b5c4a3071874ba6a4684b02
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/sires/run-xbklzdqi/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/sires/run-xbklzdqi/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/sires/run-xbklzdqi/fixtures.json sha256=651a0f9d94bc4777ec1b4859ed471f88c4291db60c1d25166250b990a6d9571c
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/sires/run-xbklzdqi/cohort.json sha256=c8b72f45165bd70d3b961b810f3e876b14470162bc06bbfe7093f174f671bbfc
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/sires/run-xbklzdqi/coverage.json sha256=13c78ad870917093dee6f259530a09e2e082e6c903bf8ffd7d1a184fcd777162
