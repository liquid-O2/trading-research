# GB-FAIL method pass

formula_version: `method-pack-v1`
status: `source_hole`
created_at: `2026-09-12T07:53:45Z`

## Headline

method | predicate | n | rate | interval | year split | status | report path
--- | --- | --- | --- | --- | --- | --- | ---
GB-FAIL | sequence | 0 | — | — | 1990:0;1991:0;1992:0;1993:0;1994:0;1995:0;1996:0;1997:0;1998:0;1999:0;2000:0;2001:0;2002:0;2003:0;2004:0;2005:0;2006:0;2007:0;2008:0;2009:0;2010:0;2011:0;2012:0;2013:0;2014:0;2015:0;2016:0;2017:0;2018:0;2019:0;2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0;2027:0;2028:0 | source_hole | /workspace/implementation/reports/phase1-live/methods/gb-fail.md

## Summary

- predicate: sequence
- p=0 f=0 u=0 n=0 N=0
- rate: —
- interval: —
- candidate_discovery: hole

## Branches

- `nyam_box` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `previous_hour` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `asia_tdo_case` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `prior_day_level` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `prior_week_level` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `prior_month_level` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `cash_open_reclaim_case` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole
- `mss_fvg_refinement` (historical_discovery) p=0 f=0 u=0 n=0 N=0 status=source_hole

## Cohorts and years

predicate | cohort | mode | instrument | source versions | p | f | u | n | N | ET years
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
sequence | historical_discovery | raw_derived | None |  | 0 | 0 | 0 | 0 | 0 | 1990:0;1991:0;1992:0;1993:0;1994:0;1995:0;1996:0;1997:0;1998:0;1999:0;2000:0;2001:0;2002:0;2003:0;2004:0;2005:0;2006:0;2007:0;2008:0;2009:0;2010:0;2011:0;2012:0;2013:0;2014:0;2015:0;2016:0;2017:0;2018:0;2019:0;2020:0;2021:0;2022:0;2023:0;2024:0;2025:0;2026:0;2027:0;2028:0

## Coverage

Requested span: `{'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds', 'event': {'min': 1283644800000000000, 'max': 1788415799901114001, 'min_ns': 1283644800000000000, 'max_ns': 1788415799901114001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1788393600000000000, 'min_ns': 631238400000000000, 'max_ns': 1788393600000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'availability': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'definition': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'event_min_ns': 1283644800000000000, 'event_max_ns': 1788415799901114001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1788393600000000000, 'scheduled_min_ns': None, 'scheduled_max_ns': None, 'available_min_ns': None, 'available_max_ns': None, 'definition_min_ns': None, 'definition_max_ns': None, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': None, 'metadata_max_ns': None}`.
Observed file span: `{'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds', 'event': {'min': 1263553200000000000, 'max': 1796932800000000001, 'min_ns': 1263553200000000000, 'max_ns': 1796932800000000001, 'basis': 'observed_event_bounds'}, 'calendar': {'min': 631238400000000000, 'max': 1850256000000000000, 'min_ns': 631238400000000000, 'max_ns': 1850256000000000000, 'basis': 'calendar_date_bounds'}, 'scheduled': {'min': 1262957400000000000, 'max': 1846256400000000001, 'min_ns': 1262957400000000000, 'max_ns': 1846256400000000001, 'basis': 'scheduled_calendar_bounds'}, 'availability': {'min': 1283787023316000000, 'max': 1788480000000000001, 'min_ns': 1283787023316000000, 'max_ns': 1788480000000000001, 'basis': 'available_at_bounds'}, 'definition': {'min': 1283644800000000000, 'max': 1788089754277000001, 'min_ns': 1283644800000000000, 'max_ns': 1788089754277000001, 'basis': 'contract_definition_bounds'}, 'roll': {'min': None, 'max': None, 'min_ns': None, 'max_ns': None, 'basis': 'no_verified_bounds'}, 'metadata': {'min': 1283644800000000000, 'max': 1788362340000000001, 'min_ns': 1283644800000000000, 'max_ns': 1788362340000000001, 'basis': 'metadata_bounds'}, 'event_min_ns': 1263553200000000000, 'event_max_ns': 1796932800000000001, 'calendar_min_ns': 631238400000000000, 'calendar_max_ns': 1850256000000000000, 'scheduled_min_ns': 1262957400000000000, 'scheduled_max_ns': 1846256400000000001, 'available_min_ns': 1283787023316000000, 'available_max_ns': 1788480000000000001, 'definition_min_ns': 1283644800000000000, 'definition_max_ns': 1788089754277000001, 'roll_min_ns': None, 'roll_max_ns': None, 'metadata_min_ns': 1283644800000000000, 'metadata_max_ns': 1788362340000000001}`. File endpoints do not prove continuous coverage.
Relevant files: 666; disjoint owned tape intervals: 92.
Partial years: none.

## Validation

Quality: `{"detected_causal_violations": 50, "duplicate_candidates": 0, "fixture_failures": 0, "leakage_count": 0, "proxy_as_faithful_count": 0, "rejected_proxy_attempts": 0, "unbound_fields": 0, "year_reconciliation_errors": 0}`.
Implementation: `c08725edbaeab2b9b527e8ae919af861d7fc263f`; content hash `2cab034db2917ee91fe1e35d3256b71efcce07a688cc9c1a0fc51c3073f05f32`.

## Holes

- **Source-complete candidate discovery:** Complete five-minute comparisons are calculable for verified references; the full source session/bias/admission selector and several reference clocks remain holes.
- **M02-F3 — source/data hole.** Unspecified London/session clock, source hold detector, prior-period scope or stop policy → corresponding unknown. TDO is not universally mandatory.

## Artifacts

- `candidates.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-jt39vtnj/candidates.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `objects.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-jt39vtnj/objects.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `holes.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-jt39vtnj/holes.jsonl sha256=38c57fabf047f3c9881c6140df8a5c47b5022a5705625a8ba7d984542a4775e4
- `management.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-jt39vtnj/management.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `reference-outcomes.jsonl` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-jt39vtnj/reference-outcomes.jsonl sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
- `fixtures.json` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-jt39vtnj/fixtures.json sha256=bdb1f3ead66c7152eecffe32839c45476eddc837a1766acbcdd7521b27b2931a
- `cohort.json` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-jt39vtnj/cohort.json sha256=19d6ff9889d194cd6662de5e9db86a8cbfb0a1abc06c17f27f7532bf471caffb
- `coverage.json` /workspace/implementation/reports/phase1-live/methods/gb-fail/run-jt39vtnj/coverage.json sha256=81cf564cc0f92fed5181b6566869e03674a41cb448a8136a2bbf028a1642c7c1
