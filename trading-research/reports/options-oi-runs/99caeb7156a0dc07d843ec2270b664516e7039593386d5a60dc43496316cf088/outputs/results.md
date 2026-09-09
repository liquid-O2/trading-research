# Options OI report/lifecycle results

Source-derived candidate estimates from admitted OI/listing files. No first/last, cut, or position-date assumption is selected as the winner. The family is not complete.
Verified known_at_ns, received_at_ns, published_at_ns and position_date are NULL. causal_feature_eligible is FALSE.
Source-clock as-of rows are retrospective scenarios (ts_event_ns <= cut). They are not actual predictive evaluation.
Dates with no OI rows are unknown, not zero. VIX listing denominators are unknown. Absence is never filled.
Typed OIReport/oi_endpoint/OIReportChanges helpers were not used; certified clocks and supersedes are unavailable.

## Population and clocks

- Family: Research-Options-OI-report-lifecycle-v1
- Chains: NDX, NDXP, QQQ, SPX, SPXW, SPY, VIX
- Inclusive dates: 2020-01-01 through 2026-09-03
- Stages (half-open): {'confirmation': ['2025-01-01', '2026-09-04'], 'development': ['2023-01-01', '2025-01-01'], 'training': ['2020-01-01', '2023-01-01']}
- As-of cuts (Eastern): 09:30, 10:00, 15:00
- Position assumptions: position_date_by_request=previous intended cash date of request_date; position_date_by_event=previous intended cash date of event Eastern date; separate diagnostics and mapping_agrees. source_clock_known_at_assumed_ns=ts_event_ns. Never elevate assumptions to verified clocks.
- Primary clock note: Theta describes daily OPRA OI reports around 06:30 Eastern, reporting the preceding trading-day end. Missing new messages can occur. Its timestamp field description does not establish receipt or vintage.
- Operational selection: pilot 2020-01-02,2020-01-03,2020-01-06,2020-01-07,2020-01-08,2020-01-09,2020-01-10,2020-01-13,2020-01-14,2020-01-15,2020-01-16,2020-01-17,2020-01-21,2020-01-22,2020-01-23,2020-01-24
- Bootstrap: seed 20260908, block 5, replicates 1000, confidence 0.95, min dates 100, min events 20
- Source files/rows/bytes read: 208/1150347/7024108
- Intended chain-date units: 112

## Output artifacts

- identity_map: [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/identity-0000.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/identity-0000.parquet)
- exceptions: [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/exceptions-0000.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/exceptions-0000.parquet)
- membership: [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/membership-0000.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/membership-0000.parquet)
- reports: [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/reports-0000.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/reports-0000.parquet), [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/reports-0001.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/reports-0001.parquet), [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/reports-0002.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/reports-0002.parquet), [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/reports-0003.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/reports-0003.parquet)
- lifecycle: [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/lifecycle-0000.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/lifecycle-0000.parquet), [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/lifecycle-0001.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/lifecycle-0001.parquet), [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/lifecycle-0002.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/lifecycle-0002.parquet), [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/lifecycle-0003.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/lifecycle-0003.parquet)
- asof_intervals: [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/asof-intervals-0000.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/asof-intervals-0000.parquet), [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/asof-intervals-0001.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/asof-intervals-0001.parquet), [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/asof-intervals-0002.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/asof-intervals-0002.parquet), [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/asof-intervals-0003.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/asof-intervals-0003.parquet)
- asof_aggregates: [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/asof-aggregates-0000.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/asof-aggregates-0000.parquet)
- coverage: [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/coverage.parquet](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/coverage.parquet)
- reconstruction: [/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/reconstruction.json](/workspace/trading-research/reports/options-oi-runs/99caeb7156a0dc07d843ec2270b664516e7039593386d5a60dc43496316cf088/outputs/reconstruction.json)

## Numeric findings

Equal-date means (one weight per date). CI is the moving-block date bootstrap. Raw support is contract/observation counts, not the number of date cells.

- `NDXP\|all_period\|first\|CALL\|all` `oi_level_date_mean`: 5.79529 contracts (equal-date mean of daily mean OI); CI [5.48244, 6.22498] at 0.95; support 16 dates / 26974 raw observations; sparse=True
- `NDXP\|all_period\|first\|PUT\|all` `oi_level_date_mean`: 8.17214 contracts (equal-date mean of daily mean OI); CI [7.56818, 8.62901] at 0.95; support 16 dates / 26974 raw observations; sparse=True
- `NDXP\|all_period\|first\|all\|0` `oi_level_date_mean`: 21.0869 contracts (equal-date mean of daily mean OI); CI [18.7717, 24.2552] at 0.95; support 6 dates / 2314 raw observations; sparse=True
- `NDXP\|all_period\|first\|all\|1` `oi_level_date_mean`: 18.0143 contracts (equal-date mean of daily mean OI); CI [16.1615, 20.5511] at 0.95; support 6 dates / 2314 raw observations; sparse=True
- `NDXP\|all_period\|first\|all\|2-7` `oi_level_date_mean`: 10.3938 contracts (equal-date mean of daily mean OI); CI [9.89539, 12.1521] at 0.95; support 15 dates / 7948 raw observations; sparse=True
- `NDXP\|all_period\|first\|all\|31-60` `oi_level_date_mean`: 0.990981 contracts (equal-date mean of daily mean OI); CI [0.702223, 1.33373] at 0.95; support 16 dates / 6798 raw observations; sparse=True
- `NDXP\|all_period\|first\|all\|8-30` `oi_level_date_mean`: 4.68672 contracts (equal-date mean of daily mean OI); CI [4.36352, 5.11625] at 0.95; support 16 dates / 32370 raw observations; sparse=True
- `NDXP\|all_period\|first\|all\|all` `oi_level_date_mean`: 6.98371 contracts (equal-date mean of daily mean OI); CI [6.56325, 7.42659] at 0.95; support 16 dates / 53948 raw observations; sparse=True
- `NDXP\|all_period\|first\|all\|all` `next_delta`: 0.91222 contracts (equal-date mean of adjacent first/last delta); CI [0.803872, 1.02238] at 0.95; support 15 dates / 47944 raw observations; sparse=True
- `NDXP\|all_period\|first\|all\|all` `asof_0930_available_fraction`: 0.939895 fraction of unique-contract universe; CI [0.923223, 0.970859] at 0.95; support 16 dates / 51744 raw observations; sparse=True
- `NDXP\|all_period\|first\|all\|all` `coverage_fraction`: 1 listed contracts with OI / listed contracts; CI [1, 1] at 0.95; support 16 dates / 51744 raw observations; sparse=True
- `NDXP\|all_period\|first\|all\|expired` `oi_level_date_mean`: 18.7621 contracts (equal-date mean of daily mean OI); CI [17.5216, 21.0746] at 0.95; support 6 dates / 2204 raw observations; sparse=True

## Remaining dependencies

- Quotes, IV, flow, Greek exposures and futures-options sources stay on separate branches.
- No dealer ownership, settlement timestamp or multiplier is applied to counts.
- Daily listings are observed snapshots, not a certified as-known universe.
- No Context fit. Full-family completion is not claimed.

## Group estimates

| group | metric | estimate | ci_low | ci_high | valid_dates | missing_dates | support_dates | support_events | sparse | event_weighted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NDXP\|all_period\|first\|CALL\|all | oi_level_date_mean | 5.79529 | 5.48244 | 6.22498 | 16 | 0 | 16 | 26974 | True | 5.75658 |
| NDXP\|all_period\|first\|CALL\|all | ratio:oi_level_event_weighted | 5.75658 | 5.46095 | 6.21652 | 16 | None | 16 | 26974 | True | undefined |
| NDXP\|all_period\|first\|PUT\|all | oi_level_date_mean | 8.17214 | 7.56818 | 8.62901 | 16 | 0 | 16 | 26974 | True | 8.16675 |
| NDXP\|all_period\|first\|PUT\|all | ratio:oi_level_event_weighted | 8.16675 | 7.54733 | 8.60927 | 16 | None | 16 | 26974 | True | undefined |
| NDXP\|all_period\|first\|all\|0 | oi_level_date_mean | 21.0869 | 18.7717 | 24.2552 | 6 | 10 | 6 | 2314 | True | 21.1707 |
| NDXP\|all_period\|first\|all\|0 | ratio:oi_level_event_weighted | 21.1707 | 18.8564 | 24.2254 | 6 | None | 6 | 2314 | True | undefined |
| NDXP\|all_period\|first\|all\|1 | oi_level_date_mean | 18.0143 | 16.1615 | 20.5511 | 6 | 10 | 6 | 2314 | True | 18.1054 |
| NDXP\|all_period\|first\|all\|1 | ratio:oi_level_event_weighted | 18.1054 | 16.2582 | 20.5676 | 6 | None | 6 | 2314 | True | undefined |
| NDXP\|all_period\|first\|all\|2-7 | oi_level_date_mean | 10.3938 | 9.89539 | 12.1521 | 15 | 1 | 15 | 7948 | True | 10.6685 |
| NDXP\|all_period\|first\|all\|2-7 | ratio:oi_level_event_weighted | 10.6685 | 10.3006 | 12.0985 | 15 | None | 15 | 7948 | True | undefined |
| NDXP\|all_period\|first\|all\|31-60 | oi_level_date_mean | 0.990981 | 0.702223 | 1.33373 | 16 | 0 | 16 | 6798 | True | 0.966755 |
| NDXP\|all_period\|first\|all\|31-60 | ratio:oi_level_event_weighted | 0.966755 | 0.709237 | 1.24464 | 16 | None | 16 | 6798 | True | undefined |
| NDXP\|all_period\|first\|all\|8-30 | oi_level_date_mean | 4.68672 | 4.36352 | 5.11625 | 16 | 0 | 16 | 32370 | True | 4.69858 |
| NDXP\|all_period\|first\|all\|8-30 | ratio:oi_level_event_weighted | 4.69858 | 4.39157 | 5.14135 | 16 | None | 16 | 32370 | True | undefined |
| NDXP\|all_period\|first\|all\|all | oi_level_date_mean | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | 6.96167 |
| NDXP\|all_period\|first\|all\|all | oi_zero_fraction | 0.584256 | 0.571157 | 0.593616 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | report_seconds_after_eastern_midnight | 27958.3 | 26606.3 | 28748.8 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDXP\|all_period\|first\|all\|all | common_support_first | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | common_support_last | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | next_delta | 0.91222 | 0.803872 | 1.02238 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|all_period\|first\|all\|all | next_abs_delta | 1.55747 | 1.33339 | 1.82455 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|all_period\|first\|all\|all | next_positive_fraction | 0.128628 | 0.12401 | 0.134861 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|all_period\|first\|all\|all | next_zero_fraction | 0.837276 | 0.824789 | 0.847784 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|all_period\|first\|all\|all | next_negative_fraction | 0.0340964 | 0.0272771 | 0.0408385 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|all_period\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|all_period\|first\|all\|all | censor_expired_fraction | 0.0401745 | 0.0248384 | 0.0485743 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|all_period\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7226 | True | undefined |
| NDXP\|all_period\|first\|all\|all | first_observed_fraction | 0.0465444 | 0.025205 | 0.0682921 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|all_period\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | late_clock_flag_fraction | 0.0566177 | 0.0282397 | 0.0732119 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | asof_0930_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | asof_0930_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | asof_1000_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | asof_1000_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | asof_1500_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | asof_1500_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|first\|all\|all | ratio:oi_level_event_weighted | 6.96167 | 6.5585 | 7.41716 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|all_period\|first\|all\|expired | oi_level_date_mean | 18.7621 | 17.5216 | 21.0746 | 6 | 10 | 6 | 2204 | True | 18.7046 |
| NDXP\|all_period\|first\|all\|expired | ratio:oi_level_event_weighted | 18.7046 | 17.5249 | 21.008 | 6 | None | 6 | 2204 | True | undefined |
| NDXP\|all_period\|last\|CALL\|all | oi_level_date_mean | 5.79529 | 5.48244 | 6.22498 | 16 | 0 | 16 | 26974 | True | 5.75658 |
| NDXP\|all_period\|last\|CALL\|all | ratio:oi_level_event_weighted | 5.75658 | 5.46095 | 6.21652 | 16 | None | 16 | 26974 | True | undefined |
| NDXP\|all_period\|last\|PUT\|all | oi_level_date_mean | 8.17214 | 7.56818 | 8.62901 | 16 | 0 | 16 | 26974 | True | 8.16675 |
| NDXP\|all_period\|last\|PUT\|all | ratio:oi_level_event_weighted | 8.16675 | 7.54733 | 8.60927 | 16 | None | 16 | 26974 | True | undefined |
| NDXP\|all_period\|last\|all\|0 | oi_level_date_mean | 21.0869 | 18.7717 | 24.2552 | 6 | 10 | 6 | 2314 | True | 21.1707 |
| NDXP\|all_period\|last\|all\|0 | ratio:oi_level_event_weighted | 21.1707 | 18.8564 | 24.2254 | 6 | None | 6 | 2314 | True | undefined |
| NDXP\|all_period\|last\|all\|1 | oi_level_date_mean | 18.0143 | 16.1615 | 20.5511 | 6 | 10 | 6 | 2314 | True | 18.1054 |
| NDXP\|all_period\|last\|all\|1 | ratio:oi_level_event_weighted | 18.1054 | 16.2582 | 20.5676 | 6 | None | 6 | 2314 | True | undefined |
| NDXP\|all_period\|last\|all\|2-7 | oi_level_date_mean | 10.3938 | 9.89539 | 12.1521 | 15 | 1 | 15 | 7948 | True | 10.6685 |
| NDXP\|all_period\|last\|all\|2-7 | ratio:oi_level_event_weighted | 10.6685 | 10.3006 | 12.0985 | 15 | None | 15 | 7948 | True | undefined |
| NDXP\|all_period\|last\|all\|31-60 | oi_level_date_mean | 0.990981 | 0.702223 | 1.33373 | 16 | 0 | 16 | 6798 | True | 0.966755 |
| NDXP\|all_period\|last\|all\|31-60 | ratio:oi_level_event_weighted | 0.966755 | 0.709237 | 1.24464 | 16 | None | 16 | 6798 | True | undefined |
| NDXP\|all_period\|last\|all\|8-30 | oi_level_date_mean | 4.68672 | 4.36352 | 5.11625 | 16 | 0 | 16 | 32370 | True | 4.69858 |
| NDXP\|all_period\|last\|all\|8-30 | ratio:oi_level_event_weighted | 4.69858 | 4.39157 | 5.14135 | 16 | None | 16 | 32370 | True | undefined |
| NDXP\|all_period\|last\|all\|all | oi_level_date_mean | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | 6.96167 |
| NDXP\|all_period\|last\|all\|all | oi_zero_fraction | 0.584256 | 0.571157 | 0.593616 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | report_seconds_after_eastern_midnight | 27958.3 | 26606.3 | 28748.8 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDXP\|all_period\|last\|all\|all | common_support_first | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | common_support_last | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | next_delta | 0.91222 | 0.803872 | 1.02238 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|all_period\|last\|all\|all | next_abs_delta | 1.55747 | 1.33339 | 1.82455 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|all_period\|last\|all\|all | next_positive_fraction | 0.128628 | 0.12401 | 0.134861 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|all_period\|last\|all\|all | next_zero_fraction | 0.837276 | 0.824789 | 0.847784 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|all_period\|last\|all\|all | next_negative_fraction | 0.0340964 | 0.0272771 | 0.0408385 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|all_period\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|all_period\|last\|all\|all | censor_expired_fraction | 0.0401745 | 0.0248384 | 0.0485743 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|all_period\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7226 | True | undefined |
| NDXP\|all_period\|last\|all\|all | first_observed_fraction | 0.0465444 | 0.025205 | 0.0682921 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|all_period\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | late_clock_flag_fraction | 0.0566177 | 0.0282397 | 0.0732119 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | asof_0930_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | asof_0930_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | asof_1000_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | asof_1000_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | asof_1500_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | asof_1500_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|all_period\|last\|all\|all | ratio:oi_level_event_weighted | 6.96167 | 6.5585 | 7.41716 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|all_period\|last\|all\|expired | oi_level_date_mean | 18.7621 | 17.5216 | 21.0746 | 6 | 10 | 6 | 2204 | True | 18.7046 |
| NDXP\|all_period\|last\|all\|expired | ratio:oi_level_event_weighted | 18.7046 | 17.5249 | 21.008 | 6 | None | 6 | 2204 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_confirmation\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_development\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | oi_level_date_mean | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | 6.96167 |
| NDXP\|stage_training\|first\|all\|all | oi_zero_fraction | 0.584256 | 0.571157 | 0.593616 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | report_seconds_after_eastern_midnight | 27958.3 | 26606.3 | 28748.8 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | common_support_first | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | common_support_last | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | next_delta | 0.91222 | 0.803872 | 1.02238 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | next_abs_delta | 1.55747 | 1.33339 | 1.82455 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | next_positive_fraction | 0.128628 | 0.12401 | 0.134861 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | next_zero_fraction | 0.837276 | 0.824789 | 0.847784 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | next_negative_fraction | 0.0340964 | 0.0272771 | 0.0408385 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | censor_expired_fraction | 0.0401745 | 0.0248384 | 0.0485743 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7226 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | first_observed_fraction | 0.0465444 | 0.025205 | 0.0682921 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | late_clock_flag_fraction | 0.0566177 | 0.0282397 | 0.0732119 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | asof_0930_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | asof_0930_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | asof_1000_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | asof_1000_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | asof_1500_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | asof_1500_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | ratio:oi_level_event_weighted | 6.96167 | 6.5585 | 7.41716 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | oi_level_date_mean | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | 6.96167 |
| NDXP\|stage_training\|last\|all\|all | oi_zero_fraction | 0.584256 | 0.571157 | 0.593616 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | report_seconds_after_eastern_midnight | 27958.3 | 26606.3 | 28748.8 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | common_support_first | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | common_support_last | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | next_delta | 0.91222 | 0.803872 | 1.02238 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | next_abs_delta | 1.55747 | 1.33339 | 1.82455 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | next_positive_fraction | 0.128628 | 0.12401 | 0.134861 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | next_zero_fraction | 0.837276 | 0.824789 | 0.847784 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | next_negative_fraction | 0.0340964 | 0.0272771 | 0.0408385 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | censor_expired_fraction | 0.0401745 | 0.0248384 | 0.0485743 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7226 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | first_observed_fraction | 0.0465444 | 0.025205 | 0.0682921 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | late_clock_flag_fraction | 0.0566177 | 0.0282397 | 0.0732119 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | asof_0930_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | asof_0930_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | asof_1000_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | asof_1000_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | asof_1500_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | asof_1500_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | ratio:oi_level_event_weighted | 6.96167 | 6.5585 | 7.41716 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|stage_training\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | oi_level_date_mean | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | 6.96167 |
| NDXP\|year_2020\|first\|all\|all | oi_zero_fraction | 0.584256 | 0.571157 | 0.593616 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | report_seconds_after_eastern_midnight | 27958.3 | 26606.3 | 28748.8 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | common_support_first | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | common_support_last | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | next_delta | 0.91222 | 0.803872 | 1.02238 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | next_abs_delta | 1.55747 | 1.33339 | 1.82455 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | next_positive_fraction | 0.128628 | 0.12401 | 0.134861 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | next_zero_fraction | 0.837276 | 0.824789 | 0.847784 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | next_negative_fraction | 0.0340964 | 0.0272771 | 0.0408385 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | censor_expired_fraction | 0.0401745 | 0.0248384 | 0.0485743 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7226 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | first_observed_fraction | 0.0465444 | 0.025205 | 0.0682921 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | late_clock_flag_fraction | 0.0566177 | 0.0282397 | 0.0732119 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | asof_0930_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | asof_0930_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | asof_1000_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | asof_1000_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | asof_1500_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | asof_1500_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | ratio:oi_level_event_weighted | 6.96167 | 6.5585 | 7.41716 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | oi_level_date_mean | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | 6.96167 |
| NDXP\|year_2020\|last\|all\|all | oi_zero_fraction | 0.584256 | 0.571157 | 0.593616 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | report_seconds_after_eastern_midnight | 27958.3 | 26606.3 | 28748.8 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | common_support_first | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | common_support_last | 6.98371 | 6.56325 | 7.42659 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | next_delta | 0.91222 | 0.803872 | 1.02238 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | next_abs_delta | 1.55747 | 1.33339 | 1.82455 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | next_positive_fraction | 0.128628 | 0.12401 | 0.134861 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | next_zero_fraction | 0.837276 | 0.824789 | 0.847784 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | next_negative_fraction | 0.0340964 | 0.0272771 | 0.0408385 | 15 | 1 | 15 | 47944 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | censor_expired_fraction | 0.0401745 | 0.0248384 | 0.0485743 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7226 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | first_observed_fraction | 0.0465444 | 0.025205 | 0.0682921 | 15 | 1 | 15 | 52726 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | late_clock_flag_fraction | 0.0566177 | 0.0282397 | 0.0732119 | 16 | 0 | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | asof_0930_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | asof_0930_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | asof_1000_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | asof_1000_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | asof_1500_available_fraction | 0.939895 | 0.923223 | 0.970859 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | asof_1500_future_today_fraction | 0.060105 | 0.0291409 | 0.0767771 | 16 | 0 | 16 | 51744 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | ratio:oi_level_event_weighted | 6.96167 | 6.5585 | 7.41716 | 16 | None | 16 | 53948 | True | undefined |
| NDXP\|year_2020\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 53948 | True | undefined |
| NDX\|all_period\|first\|CALL\|all | oi_level_date_mean | 13.5774 | 13.1299 | 14.2802 | 16 | 0 | 16 | 30109 | True | 13.5857 |
| NDX\|all_period\|first\|CALL\|all | ratio:oi_level_event_weighted | 13.5857 | 13.135 | 14.2739 | 16 | None | 16 | 30109 | True | undefined |
| NDX\|all_period\|first\|PUT\|all | oi_level_date_mean | 21.3918 | 20.0564 | 23.3696 | 16 | 0 | 16 | 30109 | True | 21.4799 |
| NDX\|all_period\|first\|PUT\|all | ratio:oi_level_event_weighted | 21.4799 | 20.0848 | 23.4264 | 16 | None | 16 | 30109 | True | undefined |
| NDX\|all_period\|first\|all\|0 | oi_level_date_mean | 46.9498 | 46.9498 | 46.9498 | 1 | 15 | 1 | 558 | True | 46.9498 |
| NDX\|all_period\|first\|all\|0 | ratio:oi_level_event_weighted | 46.9498 | 46.9498 | 46.9498 | 1 | None | 1 | 558 | True | undefined |
| NDX\|all_period\|first\|all\|1 | oi_level_date_mean | 45.6075 | 45.6075 | 45.6075 | 1 | 15 | 1 | 558 | True | 45.6075 |
| NDX\|all_period\|first\|all\|1 | ratio:oi_level_event_weighted | 45.6075 | 45.6075 | 45.6075 | 1 | None | 1 | 558 | True | undefined |
| NDX\|all_period\|first\|all\|2-7 | oi_level_date_mean | 41.3353 | 40.5515 | 42.4767 | 4 | 12 | 4 | 2166 | True | 41.3426 |
| NDX\|all_period\|first\|all\|2-7 | ratio:oi_level_event_weighted | 41.3426 | 40.5515 | 42.4767 | 4 | None | 4 | 2166 | True | undefined |
| NDX\|all_period\|first\|all\|31-60 | oi_level_date_mean | 36.6621 | 25.159 | 46.2476 | 16 | 0 | 16 | 6428 | True | 37.6879 |
| NDX\|all_period\|first\|all\|31-60 | ratio:oi_level_event_weighted | 37.6879 | 25.159 | 45.9008 | 16 | None | 16 | 6428 | True | undefined |
| NDX\|all_period\|first\|all\|61+ | oi_level_date_mean | 10.5327 | 9.71378 | 12.236 | 16 | 0 | 16 | 45440 | True | 10.5744 |
| NDX\|all_period\|first\|all\|61+ | ratio:oi_level_event_weighted | 10.5744 | 9.77446 | 12.2458 | 16 | None | 16 | 45440 | True | undefined |
| NDX\|all_period\|first\|all\|8-30 | oi_level_date_mean | 38.7385 | 37.2284 | 40.6469 | 9 | 7 | 9 | 4510 | True | 38.7732 |
| NDX\|all_period\|first\|all\|8-30 | ratio:oi_level_event_weighted | 38.7732 | 37.2284 | 40.6469 | 9 | None | 9 | 4510 | True | undefined |
| NDX\|all_period\|first\|all\|all | oi_level_date_mean | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | 17.5328 |
| NDX\|all_period\|first\|all\|all | oi_zero_fraction | 0.533577 | 0.513086 | 0.543419 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | report_seconds_after_eastern_midnight | 25936.7 | 25552.3 | 26284.8 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|all_period\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|all_period\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDX\|all_period\|first\|all\|all | common_support_first | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | common_support_last | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | next_delta | 0.506492 | 0.352042 | 0.746045 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|all_period\|first\|all\|all | next_abs_delta | 1.06973 | 0.73262 | 1.58351 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|all_period\|first\|all\|all | next_positive_fraction | 0.0618919 | 0.0582603 | 0.0679215 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|all_period\|first\|all\|all | next_zero_fraction | 0.917446 | 0.910854 | 0.922507 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|all_period\|first\|all\|all | next_negative_fraction | 0.0206623 | 0.0176385 | 0.0255561 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|all_period\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|all_period\|first\|all\|all | censor_expired_fraction | 0.00899855 | 0 | 0.0179971 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|all_period\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7146 | True | undefined |
| NDX\|all_period\|first\|all\|all | first_observed_fraction | 0.0145028 | 0.00610954 | 0.0215513 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|all_period\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | late_clock_flag_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | asof_0930_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|first\|all\|all | asof_0930_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|first\|all\|all | asof_1000_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|first\|all\|all | asof_1000_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|first\|all\|all | asof_1500_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|first\|all\|all | asof_1500_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|first\|all\|all | ratio:oi_level_event_weighted | 17.5328 | 16.6501 | 18.756 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|all_period\|first\|all\|expired | oi_level_date_mean | 30.4068 | 30.4068 | 30.4068 | 1 | 15 | 1 | 558 | True | 30.4068 |
| NDX\|all_period\|first\|all\|expired | ratio:oi_level_event_weighted | 30.4068 | 30.4068 | 30.4068 | 1 | None | 1 | 558 | True | undefined |
| NDX\|all_period\|last\|CALL\|all | oi_level_date_mean | 13.5774 | 13.1299 | 14.2802 | 16 | 0 | 16 | 30109 | True | 13.5857 |
| NDX\|all_period\|last\|CALL\|all | ratio:oi_level_event_weighted | 13.5857 | 13.135 | 14.2739 | 16 | None | 16 | 30109 | True | undefined |
| NDX\|all_period\|last\|PUT\|all | oi_level_date_mean | 21.3918 | 20.0564 | 23.3696 | 16 | 0 | 16 | 30109 | True | 21.4799 |
| NDX\|all_period\|last\|PUT\|all | ratio:oi_level_event_weighted | 21.4799 | 20.0848 | 23.4264 | 16 | None | 16 | 30109 | True | undefined |
| NDX\|all_period\|last\|all\|0 | oi_level_date_mean | 46.9498 | 46.9498 | 46.9498 | 1 | 15 | 1 | 558 | True | 46.9498 |
| NDX\|all_period\|last\|all\|0 | ratio:oi_level_event_weighted | 46.9498 | 46.9498 | 46.9498 | 1 | None | 1 | 558 | True | undefined |
| NDX\|all_period\|last\|all\|1 | oi_level_date_mean | 45.6075 | 45.6075 | 45.6075 | 1 | 15 | 1 | 558 | True | 45.6075 |
| NDX\|all_period\|last\|all\|1 | ratio:oi_level_event_weighted | 45.6075 | 45.6075 | 45.6075 | 1 | None | 1 | 558 | True | undefined |
| NDX\|all_period\|last\|all\|2-7 | oi_level_date_mean | 41.3353 | 40.5515 | 42.4767 | 4 | 12 | 4 | 2166 | True | 41.3426 |
| NDX\|all_period\|last\|all\|2-7 | ratio:oi_level_event_weighted | 41.3426 | 40.5515 | 42.4767 | 4 | None | 4 | 2166 | True | undefined |
| NDX\|all_period\|last\|all\|31-60 | oi_level_date_mean | 36.6621 | 25.159 | 46.2476 | 16 | 0 | 16 | 6428 | True | 37.6879 |
| NDX\|all_period\|last\|all\|31-60 | ratio:oi_level_event_weighted | 37.6879 | 25.159 | 45.9008 | 16 | None | 16 | 6428 | True | undefined |
| NDX\|all_period\|last\|all\|61+ | oi_level_date_mean | 10.5327 | 9.71378 | 12.236 | 16 | 0 | 16 | 45440 | True | 10.5744 |
| NDX\|all_period\|last\|all\|61+ | ratio:oi_level_event_weighted | 10.5744 | 9.77446 | 12.2458 | 16 | None | 16 | 45440 | True | undefined |
| NDX\|all_period\|last\|all\|8-30 | oi_level_date_mean | 38.7385 | 37.2284 | 40.6469 | 9 | 7 | 9 | 4510 | True | 38.7732 |
| NDX\|all_period\|last\|all\|8-30 | ratio:oi_level_event_weighted | 38.7732 | 37.2284 | 40.6469 | 9 | None | 9 | 4510 | True | undefined |
| NDX\|all_period\|last\|all\|all | oi_level_date_mean | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | 17.5328 |
| NDX\|all_period\|last\|all\|all | oi_zero_fraction | 0.533577 | 0.513086 | 0.543419 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | report_seconds_after_eastern_midnight | 25936.7 | 25552.3 | 26284.8 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|all_period\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|all_period\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDX\|all_period\|last\|all\|all | common_support_first | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | common_support_last | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | next_delta | 0.506492 | 0.352042 | 0.746045 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|all_period\|last\|all\|all | next_abs_delta | 1.06973 | 0.73262 | 1.58351 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|all_period\|last\|all\|all | next_positive_fraction | 0.0618919 | 0.0582603 | 0.0679215 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|all_period\|last\|all\|all | next_zero_fraction | 0.917446 | 0.910854 | 0.922507 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|all_period\|last\|all\|all | next_negative_fraction | 0.0206623 | 0.0176385 | 0.0255561 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|all_period\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|all_period\|last\|all\|all | censor_expired_fraction | 0.00899855 | 0 | 0.0179971 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|all_period\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7146 | True | undefined |
| NDX\|all_period\|last\|all\|all | first_observed_fraction | 0.0145028 | 0.00610954 | 0.0215513 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|all_period\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | late_clock_flag_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | asof_0930_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|last\|all\|all | asof_0930_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|last\|all\|all | asof_1000_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|last\|all\|all | asof_1000_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|last\|all\|all | asof_1500_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|last\|all\|all | asof_1500_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|all_period\|last\|all\|all | ratio:oi_level_event_weighted | 17.5328 | 16.6501 | 18.756 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|all_period\|last\|all\|expired | oi_level_date_mean | 30.4068 | 30.4068 | 30.4068 | 1 | 15 | 1 | 558 | True | 30.4068 |
| NDX\|all_period\|last\|all\|expired | ratio:oi_level_event_weighted | 30.4068 | 30.4068 | 30.4068 | 1 | None | 1 | 558 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_confirmation\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_development\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| NDX\|stage_training\|first\|all\|all | oi_level_date_mean | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | 17.5328 |
| NDX\|stage_training\|first\|all\|all | oi_zero_fraction | 0.533577 | 0.513086 | 0.543419 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | report_seconds_after_eastern_midnight | 25936.7 | 25552.3 | 26284.8 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|stage_training\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|stage_training\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDX\|stage_training\|first\|all\|all | common_support_first | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | common_support_last | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | next_delta | 0.506492 | 0.352042 | 0.746045 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|stage_training\|first\|all\|all | next_abs_delta | 1.06973 | 0.73262 | 1.58351 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|stage_training\|first\|all\|all | next_positive_fraction | 0.0618919 | 0.0582603 | 0.0679215 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|stage_training\|first\|all\|all | next_zero_fraction | 0.917446 | 0.910854 | 0.922507 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|stage_training\|first\|all\|all | next_negative_fraction | 0.0206623 | 0.0176385 | 0.0255561 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|stage_training\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|stage_training\|first\|all\|all | censor_expired_fraction | 0.00899855 | 0 | 0.0179971 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|stage_training\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7146 | True | undefined |
| NDX\|stage_training\|first\|all\|all | first_observed_fraction | 0.0145028 | 0.00610954 | 0.0215513 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|stage_training\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | late_clock_flag_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | asof_0930_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|first\|all\|all | asof_0930_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|first\|all\|all | asof_1000_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|first\|all\|all | asof_1000_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|first\|all\|all | asof_1500_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|first\|all\|all | asof_1500_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|first\|all\|all | ratio:oi_level_event_weighted | 17.5328 | 16.6501 | 18.756 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|stage_training\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | oi_level_date_mean | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | 17.5328 |
| NDX\|stage_training\|last\|all\|all | oi_zero_fraction | 0.533577 | 0.513086 | 0.543419 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | report_seconds_after_eastern_midnight | 25936.7 | 25552.3 | 26284.8 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|stage_training\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|stage_training\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDX\|stage_training\|last\|all\|all | common_support_first | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | common_support_last | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | next_delta | 0.506492 | 0.352042 | 0.746045 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|stage_training\|last\|all\|all | next_abs_delta | 1.06973 | 0.73262 | 1.58351 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|stage_training\|last\|all\|all | next_positive_fraction | 0.0618919 | 0.0582603 | 0.0679215 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|stage_training\|last\|all\|all | next_zero_fraction | 0.917446 | 0.910854 | 0.922507 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|stage_training\|last\|all\|all | next_negative_fraction | 0.0206623 | 0.0176385 | 0.0255561 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|stage_training\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|stage_training\|last\|all\|all | censor_expired_fraction | 0.00899855 | 0 | 0.0179971 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|stage_training\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7146 | True | undefined |
| NDX\|stage_training\|last\|all\|all | first_observed_fraction | 0.0145028 | 0.00610954 | 0.0215513 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|stage_training\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | late_clock_flag_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | asof_0930_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|last\|all\|all | asof_0930_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|last\|all\|all | asof_1000_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|last\|all\|all | asof_1000_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|last\|all\|all | asof_1500_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|last\|all\|all | asof_1500_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|stage_training\|last\|all\|all | ratio:oi_level_event_weighted | 17.5328 | 16.6501 | 18.756 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|stage_training\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | oi_level_date_mean | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | 17.5328 |
| NDX\|year_2020\|first\|all\|all | oi_zero_fraction | 0.533577 | 0.513086 | 0.543419 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | report_seconds_after_eastern_midnight | 25936.7 | 25552.3 | 26284.8 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|year_2020\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|year_2020\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDX\|year_2020\|first\|all\|all | common_support_first | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | common_support_last | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | next_delta | 0.506492 | 0.352042 | 0.746045 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|year_2020\|first\|all\|all | next_abs_delta | 1.06973 | 0.73262 | 1.58351 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|year_2020\|first\|all\|all | next_positive_fraction | 0.0618919 | 0.0582603 | 0.0679215 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|year_2020\|first\|all\|all | next_zero_fraction | 0.917446 | 0.910854 | 0.922507 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|year_2020\|first\|all\|all | next_negative_fraction | 0.0206623 | 0.0176385 | 0.0255561 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|year_2020\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|year_2020\|first\|all\|all | censor_expired_fraction | 0.00899855 | 0 | 0.0179971 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|year_2020\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7146 | True | undefined |
| NDX\|year_2020\|first\|all\|all | first_observed_fraction | 0.0145028 | 0.00610954 | 0.0215513 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|year_2020\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | late_clock_flag_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | asof_0930_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|first\|all\|all | asof_0930_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|first\|all\|all | asof_1000_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|first\|all\|all | asof_1000_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|first\|all\|all | asof_1500_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|first\|all\|all | asof_1500_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|first\|all\|all | ratio:oi_level_event_weighted | 17.5328 | 16.6501 | 18.756 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|year_2020\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | oi_level_date_mean | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | 17.5328 |
| NDX\|year_2020\|last\|all\|all | oi_zero_fraction | 0.533577 | 0.513086 | 0.543419 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | report_seconds_after_eastern_midnight | 25936.7 | 25552.3 | 26284.8 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|year_2020\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59102 | True | undefined |
| NDX\|year_2020\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| NDX\|year_2020\|last\|all\|all | common_support_first | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | common_support_last | 17.4846 | 16.6089 | 18.745 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | next_delta | 0.506492 | 0.352042 | 0.746045 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|year_2020\|last\|all\|all | next_abs_delta | 1.06973 | 0.73262 | 1.58351 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|year_2020\|last\|all\|all | next_positive_fraction | 0.0618919 | 0.0582603 | 0.0679215 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|year_2020\|last\|all\|all | next_zero_fraction | 0.917446 | 0.910854 | 0.922507 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|year_2020\|last\|all\|all | next_negative_fraction | 0.0206623 | 0.0176385 | 0.0255561 | 15 | 1 | 15 | 55946 | True | undefined |
| NDX\|year_2020\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|year_2020\|last\|all\|all | censor_expired_fraction | 0.00899855 | 0 | 0.0179971 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|year_2020\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 7146 | True | undefined |
| NDX\|year_2020\|last\|all\|all | first_observed_fraction | 0.0145028 | 0.00610954 | 0.0215513 | 15 | 1 | 15 | 57344 | True | undefined |
| NDX\|year_2020\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | late_clock_flag_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | asof_0930_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|last\|all\|all | asof_0930_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|last\|all\|all | asof_1000_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|last\|all\|all | asof_1000_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|last\|all\|all | asof_1500_available_fraction | 0.985816 | 0.978511 | 0.993886 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|last\|all\|all | asof_1500_future_today_fraction | 0.0141839 | 0.00611426 | 0.0214893 | 16 | 0 | 16 | 59660 | True | undefined |
| NDX\|year_2020\|last\|all\|all | ratio:oi_level_event_weighted | 17.5328 | 16.6501 | 18.756 | 16 | None | 16 | 60218 | True | undefined |
| NDX\|year_2020\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 60218 | True | undefined |
| QQQ\|all_period\|first\|CALL\|all | oi_level_date_mean | 768.534 | 741.658 | 826.341 | 16 | 0 | 16 | 37067 | True | 767.531 |
| QQQ\|all_period\|first\|CALL\|all | ratio:oi_level_event_weighted | 767.531 | 740.188 | 826.534 | 16 | None | 16 | 37067 | True | undefined |
| QQQ\|all_period\|first\|PUT\|all | oi_level_date_mean | 1781.92 | 1745.91 | 1916.79 | 16 | 0 | 16 | 37067 | True | 1783.29 |
| QQQ\|all_period\|first\|PUT\|all | ratio:oi_level_event_weighted | 1783.29 | 1746.24 | 1918.78 | 16 | None | 16 | 37067 | True | undefined |
| QQQ\|all_period\|first\|all\|0 | oi_level_date_mean | 3598.36 | 1745.87 | 8636.45 | 4 | 12 | 4 | 912 | True | 4070.32 |
| QQQ\|all_period\|first\|all\|0 | ratio:oi_level_event_weighted | 4070.32 | 1630.82 | 8636.45 | 4 | None | 4 | 912 | True | undefined |
| QQQ\|all_period\|first\|all\|1 | oi_level_date_mean | 3501.35 | 1799.98 | 8605.44 | 4 | 12 | 4 | 912 | True | 3979.61 |
| QQQ\|all_period\|first\|all\|1 | ratio:oi_level_event_weighted | 3979.61 | 1689.45 | 8605.44 | 4 | None | 4 | 912 | True | undefined |
| QQQ\|all_period\|first\|all\|2-7 | oi_level_date_mean | 3887.4 | 1746.46 | 7282.58 | 12 | 4 | 12 | 2658 | True | 4694.36 |
| QQQ\|all_period\|first\|all\|2-7 | ratio:oi_level_event_weighted | 4694.36 | 1752.57 | 7645.92 | 12 | None | 12 | 2658 | True | undefined |
| QQQ\|all_period\|first\|all\|31-60 | oi_level_date_mean | 2065.77 | 1401.21 | 2879.38 | 16 | 0 | 16 | 7702 | True | 2047.16 |
| QQQ\|all_period\|first\|all\|31-60 | ratio:oi_level_event_weighted | 2047.16 | 1380.97 | 2902.75 | 16 | None | 16 | 7702 | True | undefined |
| QQQ\|all_period\|first\|all\|61+ | oi_level_date_mean | 588.047 | 545.342 | 651.15 | 16 | 0 | 16 | 50896 | True | 586.815 |
| QQQ\|all_period\|first\|all\|61+ | ratio:oi_level_event_weighted | 586.815 | 545.77 | 652.042 | 16 | None | 16 | 50896 | True | undefined |
| QQQ\|all_period\|first\|all\|8-30 | oi_level_date_mean | 2484.48 | 1231.42 | 3494 | 16 | 0 | 16 | 10114 | True | 2587.93 |
| QQQ\|all_period\|first\|all\|8-30 | ratio:oi_level_event_weighted | 2587.93 | 1273.57 | 3506 | 16 | None | 16 | 10114 | True | undefined |
| QQQ\|all_period\|first\|all\|all | oi_level_date_mean | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | 1275.41 |
| QQQ\|all_period\|first\|all\|all | oi_zero_fraction | 0.418606 | 0.406091 | 0.427795 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | report_seconds_after_eastern_midnight | 26177.9 | 25882.3 | 26463.1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| QQQ\|all_period\|first\|all\|all | common_support_first | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | common_support_last | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | next_delta | 39.6754 | 24.8265 | 55.5813 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|all_period\|first\|all\|all | next_abs_delta | 84.4134 | 73.416 | 96.6464 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|all_period\|first\|all\|all | next_positive_fraction | 0.177041 | 0.174817 | 0.180986 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|all_period\|first\|all\|all | next_zero_fraction | 0.753672 | 0.74606 | 0.759048 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|all_period\|first\|all\|all | next_negative_fraction | 0.0692867 | 0.065824 | 0.0733703 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|all_period\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|all_period\|first\|all\|all | censor_expired_fraction | 0.0132076 | 0.00708419 | 0.0185271 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|all_period\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9420 | True | undefined |
| QQQ\|all_period\|first\|all\|all | first_observed_fraction | 0.0164908 | 0.0106759 | 0.0248981 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|all_period\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | late_clock_flag_fraction | 0.0192455 | 0.0130409 | 0.0252337 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | asof_0930_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | asof_0930_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | asof_1000_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | asof_1000_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | asof_1500_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | asof_1500_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|first\|all\|all | ratio:oi_level_event_weighted | 1275.41 | 1249.4 | 1369.93 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|all_period\|first\|all\|expired | oi_level_date_mean | 2818.64 | 1214 | 6430.16 | 4 | 12 | 4 | 940 | True | 3110.79 |
| QQQ\|all_period\|first\|all\|expired | ratio:oi_level_event_weighted | 3110.79 | 1136.88 | 6430.16 | 4 | None | 4 | 940 | True | undefined |
| QQQ\|all_period\|last\|CALL\|all | oi_level_date_mean | 768.534 | 741.658 | 826.341 | 16 | 0 | 16 | 37067 | True | 767.531 |
| QQQ\|all_period\|last\|CALL\|all | ratio:oi_level_event_weighted | 767.531 | 740.188 | 826.534 | 16 | None | 16 | 37067 | True | undefined |
| QQQ\|all_period\|last\|PUT\|all | oi_level_date_mean | 1781.92 | 1745.91 | 1916.79 | 16 | 0 | 16 | 37067 | True | 1783.29 |
| QQQ\|all_period\|last\|PUT\|all | ratio:oi_level_event_weighted | 1783.29 | 1746.24 | 1918.78 | 16 | None | 16 | 37067 | True | undefined |
| QQQ\|all_period\|last\|all\|0 | oi_level_date_mean | 3598.36 | 1745.87 | 8636.45 | 4 | 12 | 4 | 912 | True | 4070.32 |
| QQQ\|all_period\|last\|all\|0 | ratio:oi_level_event_weighted | 4070.32 | 1630.82 | 8636.45 | 4 | None | 4 | 912 | True | undefined |
| QQQ\|all_period\|last\|all\|1 | oi_level_date_mean | 3501.35 | 1799.98 | 8605.44 | 4 | 12 | 4 | 912 | True | 3979.61 |
| QQQ\|all_period\|last\|all\|1 | ratio:oi_level_event_weighted | 3979.61 | 1689.45 | 8605.44 | 4 | None | 4 | 912 | True | undefined |
| QQQ\|all_period\|last\|all\|2-7 | oi_level_date_mean | 3887.4 | 1746.46 | 7282.58 | 12 | 4 | 12 | 2658 | True | 4694.36 |
| QQQ\|all_period\|last\|all\|2-7 | ratio:oi_level_event_weighted | 4694.36 | 1752.57 | 7645.92 | 12 | None | 12 | 2658 | True | undefined |
| QQQ\|all_period\|last\|all\|31-60 | oi_level_date_mean | 2065.77 | 1401.21 | 2879.38 | 16 | 0 | 16 | 7702 | True | 2047.16 |
| QQQ\|all_period\|last\|all\|31-60 | ratio:oi_level_event_weighted | 2047.16 | 1380.97 | 2902.75 | 16 | None | 16 | 7702 | True | undefined |
| QQQ\|all_period\|last\|all\|61+ | oi_level_date_mean | 588.047 | 545.342 | 651.15 | 16 | 0 | 16 | 50896 | True | 586.815 |
| QQQ\|all_period\|last\|all\|61+ | ratio:oi_level_event_weighted | 586.815 | 545.77 | 652.042 | 16 | None | 16 | 50896 | True | undefined |
| QQQ\|all_period\|last\|all\|8-30 | oi_level_date_mean | 2484.48 | 1231.42 | 3494 | 16 | 0 | 16 | 10114 | True | 2587.93 |
| QQQ\|all_period\|last\|all\|8-30 | ratio:oi_level_event_weighted | 2587.93 | 1273.57 | 3506 | 16 | None | 16 | 10114 | True | undefined |
| QQQ\|all_period\|last\|all\|all | oi_level_date_mean | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | 1275.41 |
| QQQ\|all_period\|last\|all\|all | oi_zero_fraction | 0.418606 | 0.406091 | 0.427795 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | report_seconds_after_eastern_midnight | 26177.9 | 25882.3 | 26463.1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| QQQ\|all_period\|last\|all\|all | common_support_first | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | common_support_last | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | next_delta | 39.6754 | 24.8265 | 55.5813 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|all_period\|last\|all\|all | next_abs_delta | 84.4134 | 73.416 | 96.6464 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|all_period\|last\|all\|all | next_positive_fraction | 0.177041 | 0.174817 | 0.180986 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|all_period\|last\|all\|all | next_zero_fraction | 0.753672 | 0.74606 | 0.759048 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|all_period\|last\|all\|all | next_negative_fraction | 0.0692867 | 0.065824 | 0.0733703 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|all_period\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|all_period\|last\|all\|all | censor_expired_fraction | 0.0132076 | 0.00708419 | 0.0185271 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|all_period\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9420 | True | undefined |
| QQQ\|all_period\|last\|all\|all | first_observed_fraction | 0.0164908 | 0.0106759 | 0.0248981 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|all_period\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | late_clock_flag_fraction | 0.0192455 | 0.0130409 | 0.0252337 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | asof_0930_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | asof_0930_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | asof_1000_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | asof_1000_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | asof_1500_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | asof_1500_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|all_period\|last\|all\|all | ratio:oi_level_event_weighted | 1275.41 | 1249.4 | 1369.93 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|all_period\|last\|all\|expired | oi_level_date_mean | 2818.64 | 1214 | 6430.16 | 4 | 12 | 4 | 940 | True | 3110.79 |
| QQQ\|all_period\|last\|all\|expired | ratio:oi_level_event_weighted | 3110.79 | 1136.88 | 6430.16 | 4 | None | 4 | 940 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_confirmation\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_development\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | oi_level_date_mean | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | 1275.41 |
| QQQ\|stage_training\|first\|all\|all | oi_zero_fraction | 0.418606 | 0.406091 | 0.427795 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | report_seconds_after_eastern_midnight | 26177.9 | 25882.3 | 26463.1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | common_support_first | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | common_support_last | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | next_delta | 39.6754 | 24.8265 | 55.5813 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | next_abs_delta | 84.4134 | 73.416 | 96.6464 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | next_positive_fraction | 0.177041 | 0.174817 | 0.180986 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | next_zero_fraction | 0.753672 | 0.74606 | 0.759048 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | next_negative_fraction | 0.0692867 | 0.065824 | 0.0733703 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | censor_expired_fraction | 0.0132076 | 0.00708419 | 0.0185271 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9420 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | first_observed_fraction | 0.0164908 | 0.0106759 | 0.0248981 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | late_clock_flag_fraction | 0.0192455 | 0.0130409 | 0.0252337 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | asof_0930_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | asof_0930_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | asof_1000_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | asof_1000_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | asof_1500_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | asof_1500_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | ratio:oi_level_event_weighted | 1275.41 | 1249.4 | 1369.93 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | oi_level_date_mean | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | 1275.41 |
| QQQ\|stage_training\|last\|all\|all | oi_zero_fraction | 0.418606 | 0.406091 | 0.427795 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | report_seconds_after_eastern_midnight | 26177.9 | 25882.3 | 26463.1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | common_support_first | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | common_support_last | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | next_delta | 39.6754 | 24.8265 | 55.5813 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | next_abs_delta | 84.4134 | 73.416 | 96.6464 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | next_positive_fraction | 0.177041 | 0.174817 | 0.180986 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | next_zero_fraction | 0.753672 | 0.74606 | 0.759048 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | next_negative_fraction | 0.0692867 | 0.065824 | 0.0733703 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | censor_expired_fraction | 0.0132076 | 0.00708419 | 0.0185271 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9420 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | first_observed_fraction | 0.0164908 | 0.0106759 | 0.0248981 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | late_clock_flag_fraction | 0.0192455 | 0.0130409 | 0.0252337 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | asof_0930_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | asof_0930_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | asof_1000_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | asof_1000_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | asof_1500_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | asof_1500_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | ratio:oi_level_event_weighted | 1275.41 | 1249.4 | 1369.93 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|stage_training\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | oi_level_date_mean | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | 1275.41 |
| QQQ\|year_2020\|first\|all\|all | oi_zero_fraction | 0.418606 | 0.406091 | 0.427795 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | report_seconds_after_eastern_midnight | 26177.9 | 25882.3 | 26463.1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | common_support_first | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | common_support_last | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | next_delta | 39.6754 | 24.8265 | 55.5813 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | next_abs_delta | 84.4134 | 73.416 | 96.6464 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | next_positive_fraction | 0.177041 | 0.174817 | 0.180986 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | next_zero_fraction | 0.753672 | 0.74606 | 0.759048 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | next_negative_fraction | 0.0692867 | 0.065824 | 0.0733703 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | censor_expired_fraction | 0.0132076 | 0.00708419 | 0.0185271 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9420 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | first_observed_fraction | 0.0164908 | 0.0106759 | 0.0248981 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | late_clock_flag_fraction | 0.0192455 | 0.0130409 | 0.0252337 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | asof_0930_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | asof_0930_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | asof_1000_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | asof_1000_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | asof_1500_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | asof_1500_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | ratio:oi_level_event_weighted | 1275.41 | 1249.4 | 1369.93 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | oi_level_date_mean | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | 1275.41 |
| QQQ\|year_2020\|last\|all\|all | oi_zero_fraction | 0.418606 | 0.406091 | 0.427795 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | report_seconds_after_eastern_midnight | 26177.9 | 25882.3 | 26463.1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | common_support_first | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | common_support_last | 1275.23 | 1250.65 | 1369.45 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | next_delta | 39.6754 | 24.8265 | 55.5813 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | next_abs_delta | 84.4134 | 73.416 | 96.6464 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | next_positive_fraction | 0.177041 | 0.174817 | 0.180986 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | next_zero_fraction | 0.753672 | 0.74606 | 0.759048 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | next_negative_fraction | 0.0692867 | 0.065824 | 0.0733703 | 15 | 1 | 15 | 68370 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | censor_expired_fraction | 0.0132076 | 0.00708419 | 0.0185271 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9420 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | first_observed_fraction | 0.0164908 | 0.0106759 | 0.0248981 | 15 | 1 | 15 | 70478 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | late_clock_flag_fraction | 0.0192455 | 0.0130409 | 0.0252337 | 16 | 0 | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | asof_0930_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | asof_0930_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | asof_1000_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | asof_1000_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | asof_1500_available_fraction | 0.980492 | 0.974741 | 0.986701 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | asof_1500_future_today_fraction | 0.0195076 | 0.0132991 | 0.0252591 | 16 | 0 | 16 | 73194 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | ratio:oi_level_event_weighted | 1275.41 | 1249.4 | 1369.93 | 16 | None | 16 | 74134 | True | undefined |
| QQQ\|year_2020\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 74134 | True | undefined |
| SPXW\|all_period\|first\|CALL\|all | oi_level_date_mean | 225.31 | 214.297 | 235.634 | 16 | 0 | 16 | 90800 | True | 225.364 |
| SPXW\|all_period\|first\|CALL\|all | ratio:oi_level_event_weighted | 225.364 | 214.306 | 235.646 | 16 | None | 16 | 90800 | True | undefined |
| SPXW\|all_period\|first\|PUT\|all | oi_level_date_mean | 625.539 | 587.948 | 656.484 | 16 | 0 | 16 | 90828 | True | 625.808 |
| SPXW\|all_period\|first\|PUT\|all | ratio:oi_level_event_weighted | 625.808 | 588.05 | 656.559 | 16 | None | 16 | 90828 | True | undefined |
| SPXW\|all_period\|first\|all\|0 | oi_level_date_mean | 943.077 | 712.35 | 1046.64 | 10 | 6 | 10 | 3976 | True | 981.465 |
| SPXW\|all_period\|first\|all\|0 | ratio:oi_level_event_weighted | 981.465 | 726.549 | 1107.63 | 10 | None | 10 | 3976 | True | undefined |
| SPXW\|all_period\|first\|all\|1 | oi_level_date_mean | 969.009 | 660.638 | 1098.16 | 7 | 9 | 7 | 2980 | True | 987.856 |
| SPXW\|all_period\|first\|all\|1 | ratio:oi_level_event_weighted | 987.856 | 665.842 | 1148.49 | 7 | None | 7 | 2980 | True | undefined |
| SPXW\|all_period\|first\|all\|2-7 | oi_level_date_mean | 603.735 | 500.189 | 666.585 | 16 | 0 | 16 | 15214 | True | 620.521 |
| SPXW\|all_period\|first\|all\|2-7 | ratio:oi_level_event_weighted | 620.521 | 503.431 | 683.839 | 16 | None | 16 | 15214 | True | undefined |
| SPXW\|all_period\|first\|all\|31-60 | oi_level_date_mean | 303.01 | 282.713 | 325.302 | 16 | 0 | 16 | 37873 | True | 303.815 |
| SPXW\|all_period\|first\|all\|31-60 | ratio:oi_level_event_weighted | 303.815 | 283.447 | 325.659 | 16 | None | 16 | 37873 | True | undefined |
| SPXW\|all_period\|first\|all\|61+ | oi_level_date_mean | 228.608 | 207.298 | 252.463 | 16 | 0 | 16 | 62648 | True | 228.112 |
| SPXW\|all_period\|first\|all\|61+ | ratio:oi_level_event_weighted | 228.112 | 207.22 | 251.835 | 16 | None | 16 | 62648 | True | undefined |
| SPXW\|all_period\|first\|all\|8-30 | oi_level_date_mean | 559.04 | 520.489 | 628.82 | 16 | 0 | 16 | 54871 | True | 558.508 |
| SPXW\|all_period\|first\|all\|8-30 | ratio:oi_level_event_weighted | 558.508 | 520.207 | 627.832 | 16 | None | 16 | 54871 | True | undefined |
| SPXW\|all_period\|first\|all\|all | oi_level_date_mean | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | 425.617 |
| SPXW\|all_period\|first\|all\|all | oi_zero_fraction | 0.401236 | 0.392624 | 0.406344 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | report_seconds_after_eastern_midnight | 25392.1 | 25349.4 | 25433.9 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | coverage_fraction | 0.977728 | 0.973105 | 0.984956 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | missing_oi_fraction | 0.0222719 | 0.0150436 | 0.0268946 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPXW\|all_period\|first\|all\|all | common_support_first | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | common_support_last | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | next_delta | 28.7753 | 27.5295 | 30.6182 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|all_period\|first\|all\|all | next_abs_delta | 40.6241 | 39.6129 | 42.5407 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|all_period\|first\|all\|all | next_positive_fraction | 0.18301 | 0.176713 | 0.187446 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|all_period\|first\|all\|all | next_zero_fraction | 0.757243 | 0.75517 | 0.76134 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|all_period\|first\|all\|all | next_negative_fraction | 0.0597475 | 0.0546147 | 0.0651264 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|all_period\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|all_period\|first\|all\|all | censor_expired_fraction | 0.0230133 | 0.0177582 | 0.0256024 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|all_period\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 22690 | True | undefined |
| SPXW\|all_period\|first\|all\|all | first_observed_fraction | 0.0239673 | 0.0166015 | 0.0268275 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|all_period\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | late_clock_flag_fraction | 0.00275263 | 0.00185661 | 0.00363014 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | asof_0930_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | asof_0930_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | asof_1000_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | asof_1000_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | asof_1500_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | asof_1500_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|first\|all\|all | ratio:oi_level_event_weighted | 425.617 | 401.204 | 446.363 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|all_period\|first\|all\|expired | oi_level_date_mean | 1071.21 | 757.672 | 1234.52 | 10 | 6 | 10 | 4066 | True | 1124.99 |
| SPXW\|all_period\|first\|all\|expired | ratio:oi_level_event_weighted | 1124.99 | 742.887 | 1321.29 | 10 | None | 10 | 4066 | True | undefined |
| SPXW\|all_period\|last\|CALL\|all | oi_level_date_mean | 225.31 | 214.297 | 235.634 | 16 | 0 | 16 | 90800 | True | 225.364 |
| SPXW\|all_period\|last\|CALL\|all | ratio:oi_level_event_weighted | 225.364 | 214.306 | 235.646 | 16 | None | 16 | 90800 | True | undefined |
| SPXW\|all_period\|last\|PUT\|all | oi_level_date_mean | 625.539 | 587.948 | 656.484 | 16 | 0 | 16 | 90828 | True | 625.808 |
| SPXW\|all_period\|last\|PUT\|all | ratio:oi_level_event_weighted | 625.808 | 588.05 | 656.559 | 16 | None | 16 | 90828 | True | undefined |
| SPXW\|all_period\|last\|all\|0 | oi_level_date_mean | 943.077 | 712.35 | 1046.64 | 10 | 6 | 10 | 3976 | True | 981.465 |
| SPXW\|all_period\|last\|all\|0 | ratio:oi_level_event_weighted | 981.465 | 726.549 | 1107.63 | 10 | None | 10 | 3976 | True | undefined |
| SPXW\|all_period\|last\|all\|1 | oi_level_date_mean | 969.009 | 660.638 | 1098.16 | 7 | 9 | 7 | 2980 | True | 987.856 |
| SPXW\|all_period\|last\|all\|1 | ratio:oi_level_event_weighted | 987.856 | 665.842 | 1148.49 | 7 | None | 7 | 2980 | True | undefined |
| SPXW\|all_period\|last\|all\|2-7 | oi_level_date_mean | 603.735 | 500.189 | 666.585 | 16 | 0 | 16 | 15214 | True | 620.521 |
| SPXW\|all_period\|last\|all\|2-7 | ratio:oi_level_event_weighted | 620.521 | 503.431 | 683.839 | 16 | None | 16 | 15214 | True | undefined |
| SPXW\|all_period\|last\|all\|31-60 | oi_level_date_mean | 303.01 | 282.713 | 325.302 | 16 | 0 | 16 | 37873 | True | 303.815 |
| SPXW\|all_period\|last\|all\|31-60 | ratio:oi_level_event_weighted | 303.815 | 283.447 | 325.659 | 16 | None | 16 | 37873 | True | undefined |
| SPXW\|all_period\|last\|all\|61+ | oi_level_date_mean | 228.608 | 207.298 | 252.463 | 16 | 0 | 16 | 62648 | True | 228.112 |
| SPXW\|all_period\|last\|all\|61+ | ratio:oi_level_event_weighted | 228.112 | 207.22 | 251.835 | 16 | None | 16 | 62648 | True | undefined |
| SPXW\|all_period\|last\|all\|8-30 | oi_level_date_mean | 559.04 | 520.489 | 628.82 | 16 | 0 | 16 | 54871 | True | 558.508 |
| SPXW\|all_period\|last\|all\|8-30 | ratio:oi_level_event_weighted | 558.508 | 520.207 | 627.832 | 16 | None | 16 | 54871 | True | undefined |
| SPXW\|all_period\|last\|all\|all | oi_level_date_mean | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | 425.617 |
| SPXW\|all_period\|last\|all\|all | oi_zero_fraction | 0.401236 | 0.392624 | 0.406344 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | report_seconds_after_eastern_midnight | 25392.1 | 25349.4 | 25433.9 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | coverage_fraction | 0.977728 | 0.973105 | 0.984956 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | missing_oi_fraction | 0.0222719 | 0.0150436 | 0.0268946 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPXW\|all_period\|last\|all\|all | common_support_first | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | common_support_last | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | next_delta | 28.7753 | 27.5295 | 30.6182 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|all_period\|last\|all\|all | next_abs_delta | 40.6241 | 39.6129 | 42.5407 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|all_period\|last\|all\|all | next_positive_fraction | 0.18301 | 0.176713 | 0.187446 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|all_period\|last\|all\|all | next_zero_fraction | 0.757243 | 0.75517 | 0.76134 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|all_period\|last\|all\|all | next_negative_fraction | 0.0597475 | 0.0546147 | 0.0651264 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|all_period\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|all_period\|last\|all\|all | censor_expired_fraction | 0.0230133 | 0.0177582 | 0.0256024 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|all_period\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 22690 | True | undefined |
| SPXW\|all_period\|last\|all\|all | first_observed_fraction | 0.0239673 | 0.0166015 | 0.0268275 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|all_period\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | late_clock_flag_fraction | 0.00275263 | 0.00185661 | 0.00363014 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | asof_0930_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | asof_0930_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | asof_1000_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | asof_1000_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | asof_1500_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | asof_1500_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|all_period\|last\|all\|all | ratio:oi_level_event_weighted | 425.617 | 401.204 | 446.363 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|all_period\|last\|all\|expired | oi_level_date_mean | 1071.21 | 757.672 | 1234.52 | 10 | 6 | 10 | 4066 | True | 1124.99 |
| SPXW\|all_period\|last\|all\|expired | ratio:oi_level_event_weighted | 1124.99 | 742.887 | 1321.29 | 10 | None | 10 | 4066 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_confirmation\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_development\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | oi_level_date_mean | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | 425.617 |
| SPXW\|stage_training\|first\|all\|all | oi_zero_fraction | 0.401236 | 0.392624 | 0.406344 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | report_seconds_after_eastern_midnight | 25392.1 | 25349.4 | 25433.9 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | coverage_fraction | 0.977728 | 0.973105 | 0.984956 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | missing_oi_fraction | 0.0222719 | 0.0150436 | 0.0268946 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | common_support_first | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | common_support_last | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | next_delta | 28.7753 | 27.5295 | 30.6182 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | next_abs_delta | 40.6241 | 39.6129 | 42.5407 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | next_positive_fraction | 0.18301 | 0.176713 | 0.187446 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | next_zero_fraction | 0.757243 | 0.75517 | 0.76134 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | next_negative_fraction | 0.0597475 | 0.0546147 | 0.0651264 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | censor_expired_fraction | 0.0230133 | 0.0177582 | 0.0256024 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 22690 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | first_observed_fraction | 0.0239673 | 0.0166015 | 0.0268275 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | late_clock_flag_fraction | 0.00275263 | 0.00185661 | 0.00363014 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | asof_0930_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | asof_0930_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | asof_1000_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | asof_1000_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | asof_1500_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | asof_1500_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | ratio:oi_level_event_weighted | 425.617 | 401.204 | 446.363 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | oi_level_date_mean | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | 425.617 |
| SPXW\|stage_training\|last\|all\|all | oi_zero_fraction | 0.401236 | 0.392624 | 0.406344 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | report_seconds_after_eastern_midnight | 25392.1 | 25349.4 | 25433.9 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | coverage_fraction | 0.977728 | 0.973105 | 0.984956 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | missing_oi_fraction | 0.0222719 | 0.0150436 | 0.0268946 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | common_support_first | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | common_support_last | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | next_delta | 28.7753 | 27.5295 | 30.6182 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | next_abs_delta | 40.6241 | 39.6129 | 42.5407 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | next_positive_fraction | 0.18301 | 0.176713 | 0.187446 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | next_zero_fraction | 0.757243 | 0.75517 | 0.76134 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | next_negative_fraction | 0.0597475 | 0.0546147 | 0.0651264 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | censor_expired_fraction | 0.0230133 | 0.0177582 | 0.0256024 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 22690 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | first_observed_fraction | 0.0239673 | 0.0166015 | 0.0268275 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | late_clock_flag_fraction | 0.00275263 | 0.00185661 | 0.00363014 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | asof_0930_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | asof_0930_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | asof_1000_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | asof_1000_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | asof_1500_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | asof_1500_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | ratio:oi_level_event_weighted | 425.617 | 401.204 | 446.363 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|stage_training\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | oi_level_date_mean | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | 425.617 |
| SPXW\|year_2020\|first\|all\|all | oi_zero_fraction | 0.401236 | 0.392624 | 0.406344 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | report_seconds_after_eastern_midnight | 25392.1 | 25349.4 | 25433.9 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | coverage_fraction | 0.977728 | 0.973105 | 0.984956 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | missing_oi_fraction | 0.0222719 | 0.0150436 | 0.0268946 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | common_support_first | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | common_support_last | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | next_delta | 28.7753 | 27.5295 | 30.6182 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | next_abs_delta | 40.6241 | 39.6129 | 42.5407 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | next_positive_fraction | 0.18301 | 0.176713 | 0.187446 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | next_zero_fraction | 0.757243 | 0.75517 | 0.76134 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | next_negative_fraction | 0.0597475 | 0.0546147 | 0.0651264 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | censor_expired_fraction | 0.0230133 | 0.0177582 | 0.0256024 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 22690 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | first_observed_fraction | 0.0239673 | 0.0166015 | 0.0268275 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | late_clock_flag_fraction | 0.00275263 | 0.00185661 | 0.00363014 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | asof_0930_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | asof_0930_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | asof_1000_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | asof_1000_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | asof_1500_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | asof_1500_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | ratio:oi_level_event_weighted | 425.617 | 401.204 | 446.363 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | oi_level_date_mean | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | 425.617 |
| SPXW\|year_2020\|last\|all\|all | oi_zero_fraction | 0.401236 | 0.392624 | 0.406344 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | report_seconds_after_eastern_midnight | 25392.1 | 25349.4 | 25433.9 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | coverage_fraction | 0.977728 | 0.973105 | 0.984956 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | missing_oi_fraction | 0.0222719 | 0.0150436 | 0.0268946 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | common_support_first | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | common_support_last | 425.46 | 401.159 | 446.32 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | next_delta | 28.7753 | 27.5295 | 30.6182 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | next_abs_delta | 40.6241 | 39.6129 | 42.5407 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | next_positive_fraction | 0.18301 | 0.176713 | 0.187446 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | next_zero_fraction | 0.757243 | 0.75517 | 0.76134 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | next_negative_fraction | 0.0597475 | 0.0546147 | 0.0651264 | 15 | 1 | 15 | 166128 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | censor_expired_fraction | 0.0230133 | 0.0177582 | 0.0256024 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 22690 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | first_observed_fraction | 0.0239673 | 0.0166015 | 0.0268275 | 15 | 1 | 15 | 174438 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | late_clock_flag_fraction | 0.00275263 | 0.00185661 | 0.00363014 | 16 | 0 | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | asof_0930_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | asof_0930_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | asof_1000_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | asof_1000_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | asof_1500_available_fraction | 0.975013 | 0.970727 | 0.98204 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | asof_1500_future_today_fraction | 0.00271501 | 0.00184182 | 0.00355498 | 16 | 0 | 16 | 181644 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | ratio:oi_level_event_weighted | 425.617 | 401.204 | 446.363 | 16 | None | 16 | 181628 | True | undefined |
| SPXW\|year_2020\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 181628 | True | undefined |
| SPX\|all_period\|first\|CALL\|all | oi_level_date_mean | 1360.79 | 1331.13 | 1437.27 | 16 | 0 | 16 | 40522 | True | 1361.87 |
| SPX\|all_period\|first\|CALL\|all | ratio:oi_level_event_weighted | 1361.87 | 1331.77 | 1437.49 | 16 | None | 16 | 40522 | True | undefined |
| SPX\|all_period\|first\|PUT\|all | oi_level_date_mean | 2987.1 | 2925.14 | 3150.17 | 16 | 0 | 16 | 40519 | True | 2990.42 |
| SPX\|all_period\|first\|PUT\|all | ratio:oi_level_event_weighted | 2990.42 | 2927.54 | 3151.97 | 16 | None | 16 | 40519 | True | undefined |
| SPX\|all_period\|first\|all\|0 | oi_level_date_mean | 5141.12 | 5141.12 | 5141.12 | 1 | 15 | 1 | 642 | True | 5141.12 |
| SPX\|all_period\|first\|all\|0 | ratio:oi_level_event_weighted | 5141.12 | 5141.12 | 5141.12 | 1 | None | 1 | 642 | True | undefined |
| SPX\|all_period\|first\|all\|1 | oi_level_date_mean | 4992.92 | 4992.92 | 4992.92 | 1 | 15 | 1 | 642 | True | 4992.92 |
| SPX\|all_period\|first\|all\|1 | ratio:oi_level_event_weighted | 4992.92 | 4992.92 | 4992.92 | 1 | None | 1 | 642 | True | undefined |
| SPX\|all_period\|first\|all\|2-7 | oi_level_date_mean | 4856.75 | 4816.58 | 4919.71 | 4 | 12 | 4 | 2554 | True | 4856.95 |
| SPX\|all_period\|first\|all\|2-7 | ratio:oi_level_event_weighted | 4856.95 | 4816.54 | 4919.71 | 4 | None | 4 | 2554 | True | undefined |
| SPX\|all_period\|first\|all\|31-60 | oi_level_date_mean | 2614.92 | 1784.52 | 3374.26 | 16 | 0 | 16 | 10460 | True | 2700.47 |
| SPX\|all_period\|first\|all\|31-60 | ratio:oi_level_event_weighted | 2700.47 | 1784.87 | 3438.94 | 16 | None | 16 | 10460 | True | undefined |
| SPX\|all_period\|first\|all\|61+ | oi_level_date_mean | 1725.05 | 1660.1 | 1878.58 | 16 | 0 | 16 | 60413 | True | 1732.58 |
| SPX\|all_period\|first\|all\|61+ | ratio:oi_level_event_weighted | 1732.58 | 1672.36 | 1880.29 | 16 | None | 16 | 60413 | True | undefined |
| SPX\|all_period\|first\|all\|8-30 | oi_level_date_mean | 3906.4 | 2287.72 | 4742.92 | 9 | 7 | 9 | 5688 | True | 3894.26 |
| SPX\|all_period\|first\|all\|8-30 | ratio:oi_level_event_weighted | 3894.26 | 2287.72 | 4742.92 | 9 | None | 9 | 5688 | True | undefined |
| SPX\|all_period\|first\|all\|all | oi_level_date_mean | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | 2176.11 |
| SPX\|all_period\|first\|all\|all | oi_zero_fraction | 0.328089 | 0.315263 | 0.335979 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | report_seconds_after_eastern_midnight | 25263.9 | 25262.2 | 25268 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | coverage_fraction | 0.994346 | 0.98697 | 0.998361 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|all_period\|first\|all\|all | missing_oi_fraction | 0.00565374 | 0.00163904 | 0.0130299 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|all_period\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPX\|all_period\|first\|all\|all | common_support_first | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | common_support_last | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | next_delta | 28.3542 | 14.8031 | 41.4216 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|all_period\|first\|all\|all | next_abs_delta | 70.9253 | 52.7925 | 100.148 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|all_period\|first\|all\|all | next_positive_fraction | 0.13423 | 0.127192 | 0.138882 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|all_period\|first\|all\|all | next_zero_fraction | 0.813019 | 0.804078 | 0.8232 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|all_period\|first\|all\|all | next_negative_fraction | 0.052751 | 0.0494821 | 0.0584198 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|all_period\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|all_period\|first\|all\|all | censor_expired_fraction | 0.00777334 | 0 | 0.0155467 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|all_period\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9918 | True | undefined |
| SPX\|all_period\|first\|all\|all | first_observed_fraction | 0.00558708 | 0.00107306 | 0.00988217 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|all_period\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | late_clock_flag_fraction | 6.09506e-05 | 2.46063e-05 | 0.000146507 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | asof_0930_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|first\|all\|all | asof_0930_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|first\|all\|all | asof_1000_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|first\|all\|all | asof_1000_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|first\|all\|all | asof_1500_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|first\|all\|all | asof_1500_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|first\|all\|all | ratio:oi_level_event_weighted | 2176.11 | 2131.66 | 2288.45 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|all_period\|first\|all\|expired | oi_level_date_mean | 3700.26 | 3700.26 | 3700.26 | 1 | 15 | 1 | 642 | True | 3700.26 |
| SPX\|all_period\|first\|all\|expired | ratio:oi_level_event_weighted | 3700.26 | 3700.26 | 3700.26 | 1 | None | 1 | 642 | True | undefined |
| SPX\|all_period\|last\|CALL\|all | oi_level_date_mean | 1360.79 | 1331.13 | 1437.27 | 16 | 0 | 16 | 40522 | True | 1361.87 |
| SPX\|all_period\|last\|CALL\|all | ratio:oi_level_event_weighted | 1361.87 | 1331.77 | 1437.49 | 16 | None | 16 | 40522 | True | undefined |
| SPX\|all_period\|last\|PUT\|all | oi_level_date_mean | 2987.1 | 2925.14 | 3150.17 | 16 | 0 | 16 | 40519 | True | 2990.42 |
| SPX\|all_period\|last\|PUT\|all | ratio:oi_level_event_weighted | 2990.42 | 2927.54 | 3151.97 | 16 | None | 16 | 40519 | True | undefined |
| SPX\|all_period\|last\|all\|0 | oi_level_date_mean | 5141.12 | 5141.12 | 5141.12 | 1 | 15 | 1 | 642 | True | 5141.12 |
| SPX\|all_period\|last\|all\|0 | ratio:oi_level_event_weighted | 5141.12 | 5141.12 | 5141.12 | 1 | None | 1 | 642 | True | undefined |
| SPX\|all_period\|last\|all\|1 | oi_level_date_mean | 4992.92 | 4992.92 | 4992.92 | 1 | 15 | 1 | 642 | True | 4992.92 |
| SPX\|all_period\|last\|all\|1 | ratio:oi_level_event_weighted | 4992.92 | 4992.92 | 4992.92 | 1 | None | 1 | 642 | True | undefined |
| SPX\|all_period\|last\|all\|2-7 | oi_level_date_mean | 4856.75 | 4816.58 | 4919.71 | 4 | 12 | 4 | 2554 | True | 4856.95 |
| SPX\|all_period\|last\|all\|2-7 | ratio:oi_level_event_weighted | 4856.95 | 4816.54 | 4919.71 | 4 | None | 4 | 2554 | True | undefined |
| SPX\|all_period\|last\|all\|31-60 | oi_level_date_mean | 2614.92 | 1784.52 | 3374.26 | 16 | 0 | 16 | 10460 | True | 2700.47 |
| SPX\|all_period\|last\|all\|31-60 | ratio:oi_level_event_weighted | 2700.47 | 1784.87 | 3438.94 | 16 | None | 16 | 10460 | True | undefined |
| SPX\|all_period\|last\|all\|61+ | oi_level_date_mean | 1725.05 | 1660.1 | 1878.58 | 16 | 0 | 16 | 60413 | True | 1732.58 |
| SPX\|all_period\|last\|all\|61+ | ratio:oi_level_event_weighted | 1732.58 | 1672.36 | 1880.29 | 16 | None | 16 | 60413 | True | undefined |
| SPX\|all_period\|last\|all\|8-30 | oi_level_date_mean | 3906.4 | 2287.72 | 4742.92 | 9 | 7 | 9 | 5688 | True | 3894.26 |
| SPX\|all_period\|last\|all\|8-30 | ratio:oi_level_event_weighted | 3894.26 | 2287.72 | 4742.92 | 9 | None | 9 | 5688 | True | undefined |
| SPX\|all_period\|last\|all\|all | oi_level_date_mean | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | 2176.11 |
| SPX\|all_period\|last\|all\|all | oi_zero_fraction | 0.328089 | 0.315263 | 0.335979 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | report_seconds_after_eastern_midnight | 25263.9 | 25262.2 | 25268 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | coverage_fraction | 0.994346 | 0.98697 | 0.998361 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|all_period\|last\|all\|all | missing_oi_fraction | 0.00565374 | 0.00163904 | 0.0130299 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|all_period\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPX\|all_period\|last\|all\|all | common_support_first | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | common_support_last | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | next_delta | 28.3542 | 14.8031 | 41.4216 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|all_period\|last\|all\|all | next_abs_delta | 70.9253 | 52.7925 | 100.148 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|all_period\|last\|all\|all | next_positive_fraction | 0.13423 | 0.127192 | 0.138882 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|all_period\|last\|all\|all | next_zero_fraction | 0.813019 | 0.804078 | 0.8232 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|all_period\|last\|all\|all | next_negative_fraction | 0.052751 | 0.0494821 | 0.0584198 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|all_period\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|all_period\|last\|all\|all | censor_expired_fraction | 0.00777334 | 0 | 0.0155467 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|all_period\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9918 | True | undefined |
| SPX\|all_period\|last\|all\|all | first_observed_fraction | 0.00558708 | 0.00107306 | 0.00988217 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|all_period\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | late_clock_flag_fraction | 6.09506e-05 | 2.46063e-05 | 0.000146507 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | asof_0930_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|last\|all\|all | asof_0930_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|last\|all\|all | asof_1000_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|last\|all\|all | asof_1000_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|last\|all\|all | asof_1500_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|last\|all\|all | asof_1500_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|all_period\|last\|all\|all | ratio:oi_level_event_weighted | 2176.11 | 2131.66 | 2288.45 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|all_period\|last\|all\|expired | oi_level_date_mean | 3700.26 | 3700.26 | 3700.26 | 1 | 15 | 1 | 642 | True | 3700.26 |
| SPX\|all_period\|last\|all\|expired | ratio:oi_level_event_weighted | 3700.26 | 3700.26 | 3700.26 | 1 | None | 1 | 642 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_confirmation\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_development\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPX\|stage_training\|first\|all\|all | oi_level_date_mean | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | 2176.11 |
| SPX\|stage_training\|first\|all\|all | oi_zero_fraction | 0.328089 | 0.315263 | 0.335979 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | report_seconds_after_eastern_midnight | 25263.9 | 25262.2 | 25268 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | coverage_fraction | 0.994346 | 0.98697 | 0.998361 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|stage_training\|first\|all\|all | missing_oi_fraction | 0.00565374 | 0.00163904 | 0.0130299 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|stage_training\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPX\|stage_training\|first\|all\|all | common_support_first | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | common_support_last | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | next_delta | 28.3542 | 14.8031 | 41.4216 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|stage_training\|first\|all\|all | next_abs_delta | 70.9253 | 52.7925 | 100.148 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|stage_training\|first\|all\|all | next_positive_fraction | 0.13423 | 0.127192 | 0.138882 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|stage_training\|first\|all\|all | next_zero_fraction | 0.813019 | 0.804078 | 0.8232 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|stage_training\|first\|all\|all | next_negative_fraction | 0.052751 | 0.0494821 | 0.0584198 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|stage_training\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|stage_training\|first\|all\|all | censor_expired_fraction | 0.00777334 | 0 | 0.0155467 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|stage_training\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9918 | True | undefined |
| SPX\|stage_training\|first\|all\|all | first_observed_fraction | 0.00558708 | 0.00107306 | 0.00988217 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|stage_training\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | late_clock_flag_fraction | 6.09506e-05 | 2.46063e-05 | 0.000146507 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | asof_0930_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|first\|all\|all | asof_0930_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|first\|all\|all | asof_1000_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|first\|all\|all | asof_1000_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|first\|all\|all | asof_1500_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|first\|all\|all | asof_1500_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|first\|all\|all | ratio:oi_level_event_weighted | 2176.11 | 2131.66 | 2288.45 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|stage_training\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | oi_level_date_mean | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | 2176.11 |
| SPX\|stage_training\|last\|all\|all | oi_zero_fraction | 0.328089 | 0.315263 | 0.335979 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | report_seconds_after_eastern_midnight | 25263.9 | 25262.2 | 25268 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | coverage_fraction | 0.994346 | 0.98697 | 0.998361 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|stage_training\|last\|all\|all | missing_oi_fraction | 0.00565374 | 0.00163904 | 0.0130299 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|stage_training\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPX\|stage_training\|last\|all\|all | common_support_first | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | common_support_last | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | next_delta | 28.3542 | 14.8031 | 41.4216 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|stage_training\|last\|all\|all | next_abs_delta | 70.9253 | 52.7925 | 100.148 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|stage_training\|last\|all\|all | next_positive_fraction | 0.13423 | 0.127192 | 0.138882 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|stage_training\|last\|all\|all | next_zero_fraction | 0.813019 | 0.804078 | 0.8232 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|stage_training\|last\|all\|all | next_negative_fraction | 0.052751 | 0.0494821 | 0.0584198 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|stage_training\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|stage_training\|last\|all\|all | censor_expired_fraction | 0.00777334 | 0 | 0.0155467 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|stage_training\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9918 | True | undefined |
| SPX\|stage_training\|last\|all\|all | first_observed_fraction | 0.00558708 | 0.00107306 | 0.00988217 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|stage_training\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | late_clock_flag_fraction | 6.09506e-05 | 2.46063e-05 | 0.000146507 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | asof_0930_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|last\|all\|all | asof_0930_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|last\|all\|all | asof_1000_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|last\|all\|all | asof_1000_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|last\|all\|all | asof_1500_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|last\|all\|all | asof_1500_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|stage_training\|last\|all\|all | ratio:oi_level_event_weighted | 2176.11 | 2131.66 | 2288.45 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|stage_training\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | oi_level_date_mean | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | 2176.11 |
| SPX\|year_2020\|first\|all\|all | oi_zero_fraction | 0.328089 | 0.315263 | 0.335979 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | report_seconds_after_eastern_midnight | 25263.9 | 25262.2 | 25268 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | coverage_fraction | 0.994346 | 0.98697 | 0.998361 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|year_2020\|first\|all\|all | missing_oi_fraction | 0.00565374 | 0.00163904 | 0.0130299 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|year_2020\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPX\|year_2020\|first\|all\|all | common_support_first | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | common_support_last | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | next_delta | 28.3542 | 14.8031 | 41.4216 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|year_2020\|first\|all\|all | next_abs_delta | 70.9253 | 52.7925 | 100.148 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|year_2020\|first\|all\|all | next_positive_fraction | 0.13423 | 0.127192 | 0.138882 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|year_2020\|first\|all\|all | next_zero_fraction | 0.813019 | 0.804078 | 0.8232 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|year_2020\|first\|all\|all | next_negative_fraction | 0.052751 | 0.0494821 | 0.0584198 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|year_2020\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|year_2020\|first\|all\|all | censor_expired_fraction | 0.00777334 | 0 | 0.0155467 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|year_2020\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9918 | True | undefined |
| SPX\|year_2020\|first\|all\|all | first_observed_fraction | 0.00558708 | 0.00107306 | 0.00988217 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|year_2020\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | late_clock_flag_fraction | 6.09506e-05 | 2.46063e-05 | 0.000146507 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | asof_0930_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|first\|all\|all | asof_0930_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|first\|all\|all | asof_1000_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|first\|all\|all | asof_1000_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|first\|all\|all | asof_1500_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|first\|all\|all | asof_1500_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|first\|all\|all | ratio:oi_level_event_weighted | 2176.11 | 2131.66 | 2288.45 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|year_2020\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | oi_level_date_mean | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | 2176.11 |
| SPX\|year_2020\|last\|all\|all | oi_zero_fraction | 0.328089 | 0.315263 | 0.335979 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | report_seconds_after_eastern_midnight | 25263.9 | 25262.2 | 25268 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | coverage_fraction | 0.994346 | 0.98697 | 0.998361 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|year_2020\|last\|all\|all | missing_oi_fraction | 0.00565374 | 0.00163904 | 0.0130299 | 16 | 0 | 16 | 80202 | True | undefined |
| SPX\|year_2020\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPX\|year_2020\|last\|all\|all | common_support_first | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | common_support_last | 2173.91 | 2130.17 | 2287.98 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | next_delta | 28.3542 | 14.8031 | 41.4216 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|year_2020\|last\|all\|all | next_abs_delta | 70.9253 | 52.7925 | 100.148 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|year_2020\|last\|all\|all | next_positive_fraction | 0.13423 | 0.127192 | 0.138882 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|year_2020\|last\|all\|all | next_zero_fraction | 0.813019 | 0.804078 | 0.8232 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|year_2020\|last\|all\|all | next_negative_fraction | 0.052751 | 0.0494821 | 0.0584198 | 15 | 1 | 15 | 75535 | True | undefined |
| SPX\|year_2020\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|year_2020\|last\|all\|all | censor_expired_fraction | 0.00777334 | 0 | 0.0155467 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|year_2020\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 9918 | True | undefined |
| SPX\|year_2020\|last\|all\|all | first_observed_fraction | 0.00558708 | 0.00107306 | 0.00988217 | 15 | 1 | 15 | 76629 | True | undefined |
| SPX\|year_2020\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | late_clock_flag_fraction | 6.09506e-05 | 2.46063e-05 | 0.000146507 | 16 | 0 | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | asof_0930_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|last\|all\|all | asof_0930_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|last\|all\|all | asof_1000_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|last\|all\|all | asof_1000_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|last\|all\|all | asof_1500_available_fraction | 0.994286 | 0.986898 | 0.998315 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|last\|all\|all | asof_1500_future_today_fraction | 6.04129e-05 | 2.42718e-05 | 0.000145098 | 16 | 0 | 16 | 80846 | True | undefined |
| SPX\|year_2020\|last\|all\|all | ratio:oi_level_event_weighted | 2176.11 | 2131.66 | 2288.45 | 16 | None | 16 | 81041 | True | undefined |
| SPX\|year_2020\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 81041 | True | undefined |
| SPY\|all_period\|first\|CALL\|all | oi_level_date_mean | 1677.11 | 1655.18 | 1732.55 | 16 | 0 | 16 | 61572 | True | 1677.23 |
| SPY\|all_period\|first\|CALL\|all | ratio:oi_level_event_weighted | 1677.23 | 1655.2 | 1731.8 | 16 | None | 16 | 61572 | True | undefined |
| SPY\|all_period\|first\|PUT\|all | oi_level_date_mean | 3227.93 | 3189.53 | 3403.95 | 16 | 0 | 16 | 61572 | True | 3228.35 |
| SPY\|all_period\|first\|PUT\|all | ratio:oi_level_event_weighted | 3228.35 | 3189.2 | 3405.4 | 16 | None | 16 | 61572 | True | undefined |
| SPY\|all_period\|first\|all\|0 | oi_level_date_mean | 4056.98 | 3030.27 | 5900.99 | 10 | 6 | 10 | 1984 | True | 5482.22 |
| SPY\|all_period\|first\|all\|0 | ratio:oi_level_event_weighted | 5482.22 | 3150.5 | 8873.54 | 10 | None | 10 | 1984 | True | undefined |
| SPY\|all_period\|first\|all\|1 | oi_level_date_mean | 4535.24 | 3036.32 | 7310.71 | 7 | 9 | 7 | 1540 | True | 6172.4 |
| SPY\|all_period\|first\|all\|1 | ratio:oi_level_event_weighted | 6172.4 | 3200.68 | 10261 | 7 | None | 7 | 1540 | True | undefined |
| SPY\|all_period\|first\|all\|2-7 | oi_level_date_mean | 3912.34 | 2211.51 | 7012.02 | 16 | 0 | 16 | 7202 | True | 4736.4 |
| SPY\|all_period\|first\|all\|2-7 | ratio:oi_level_event_weighted | 4736.4 | 2259.29 | 7848.97 | 16 | None | 16 | 7202 | True | undefined |
| SPY\|all_period\|first\|all\|31-60 | oi_level_date_mean | 3719.71 | 3033.17 | 4649.48 | 16 | 0 | 16 | 11980 | True | 3747.13 |
| SPY\|all_period\|first\|all\|31-60 | ratio:oi_level_event_weighted | 3747.13 | 2999.08 | 4733.67 | 16 | None | 16 | 11980 | True | undefined |
| SPY\|all_period\|first\|all\|61+ | oi_level_date_mean | 1741.77 | 1681.44 | 1879.32 | 16 | 0 | 16 | 72438 | True | 1741.88 |
| SPY\|all_period\|first\|all\|61+ | ratio:oi_level_event_weighted | 1741.88 | 1681.4 | 1879.94 | 16 | None | 16 | 72438 | True | undefined |
| SPY\|all_period\|first\|all\|8-30 | oi_level_date_mean | 2459.28 | 1290.9 | 3280.13 | 16 | 0 | 16 | 26040 | True | 2533.15 |
| SPY\|all_period\|first\|all\|8-30 | ratio:oi_level_event_weighted | 2533.15 | 1308.07 | 3350.42 | 16 | None | 16 | 26040 | True | undefined |
| SPY\|all_period\|first\|all\|all | oi_level_date_mean | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | 2452.79 |
| SPY\|all_period\|first\|all\|all | oi_zero_fraction | 0.227115 | 0.222558 | 0.228311 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | report_seconds_after_eastern_midnight | 26258.2 | 25951.1 | 26413.7 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPY\|all_period\|first\|all\|all | common_support_first | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | common_support_last | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | next_delta | 76.9223 | 67.7174 | 87.7499 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|all_period\|first\|all\|all | next_abs_delta | 150.229 | 132.933 | 176.409 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|all_period\|first\|all\|all | next_positive_fraction | 0.268681 | 0.264269 | 0.272713 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|all_period\|first\|all\|all | next_zero_fraction | 0.638613 | 0.633284 | 0.643295 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|all_period\|first\|all\|all | next_negative_fraction | 0.0927051 | 0.0887641 | 0.0981445 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|all_period\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|all_period\|first\|all\|all | censor_expired_fraction | 0.0165413 | 0.0115535 | 0.0194671 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|all_period\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 15450 | True | undefined |
| SPY\|all_period\|first\|all\|all | first_observed_fraction | 0.0186809 | 0.013608 | 0.0232492 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|all_period\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | late_clock_flag_fraction | 0.0209281 | 0.0144786 | 0.0241915 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | asof_0930_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | asof_0930_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | asof_1000_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | asof_1000_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | asof_1500_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | asof_1500_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|first\|all\|all | ratio:oi_level_event_weighted | 2452.79 | 2424.42 | 2567.78 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|all_period\|first\|all\|expired | oi_level_date_mean | 4069.95 | 2811.03 | 4930.45 | 10 | 6 | 10 | 1960 | True | 5367.51 |
| SPY\|all_period\|first\|all\|expired | ratio:oi_level_event_weighted | 5367.51 | 2870.82 | 7145.68 | 10 | None | 10 | 1960 | True | undefined |
| SPY\|all_period\|last\|CALL\|all | oi_level_date_mean | 1677.11 | 1655.18 | 1732.55 | 16 | 0 | 16 | 61572 | True | 1677.23 |
| SPY\|all_period\|last\|CALL\|all | ratio:oi_level_event_weighted | 1677.23 | 1655.2 | 1731.8 | 16 | None | 16 | 61572 | True | undefined |
| SPY\|all_period\|last\|PUT\|all | oi_level_date_mean | 3227.93 | 3189.53 | 3403.95 | 16 | 0 | 16 | 61572 | True | 3228.35 |
| SPY\|all_period\|last\|PUT\|all | ratio:oi_level_event_weighted | 3228.35 | 3189.2 | 3405.4 | 16 | None | 16 | 61572 | True | undefined |
| SPY\|all_period\|last\|all\|0 | oi_level_date_mean | 4056.98 | 3030.27 | 5900.99 | 10 | 6 | 10 | 1984 | True | 5482.22 |
| SPY\|all_period\|last\|all\|0 | ratio:oi_level_event_weighted | 5482.22 | 3150.5 | 8873.54 | 10 | None | 10 | 1984 | True | undefined |
| SPY\|all_period\|last\|all\|1 | oi_level_date_mean | 4535.24 | 3036.32 | 7310.71 | 7 | 9 | 7 | 1540 | True | 6172.4 |
| SPY\|all_period\|last\|all\|1 | ratio:oi_level_event_weighted | 6172.4 | 3200.68 | 10261 | 7 | None | 7 | 1540 | True | undefined |
| SPY\|all_period\|last\|all\|2-7 | oi_level_date_mean | 3912.34 | 2211.51 | 7012.02 | 16 | 0 | 16 | 7202 | True | 4736.4 |
| SPY\|all_period\|last\|all\|2-7 | ratio:oi_level_event_weighted | 4736.4 | 2259.29 | 7848.97 | 16 | None | 16 | 7202 | True | undefined |
| SPY\|all_period\|last\|all\|31-60 | oi_level_date_mean | 3719.71 | 3033.17 | 4649.48 | 16 | 0 | 16 | 11980 | True | 3747.13 |
| SPY\|all_period\|last\|all\|31-60 | ratio:oi_level_event_weighted | 3747.13 | 2999.08 | 4733.67 | 16 | None | 16 | 11980 | True | undefined |
| SPY\|all_period\|last\|all\|61+ | oi_level_date_mean | 1741.77 | 1681.44 | 1879.32 | 16 | 0 | 16 | 72438 | True | 1741.88 |
| SPY\|all_period\|last\|all\|61+ | ratio:oi_level_event_weighted | 1741.88 | 1681.4 | 1879.94 | 16 | None | 16 | 72438 | True | undefined |
| SPY\|all_period\|last\|all\|8-30 | oi_level_date_mean | 2459.28 | 1290.9 | 3280.13 | 16 | 0 | 16 | 26040 | True | 2533.15 |
| SPY\|all_period\|last\|all\|8-30 | ratio:oi_level_event_weighted | 2533.15 | 1308.07 | 3350.42 | 16 | None | 16 | 26040 | True | undefined |
| SPY\|all_period\|last\|all\|all | oi_level_date_mean | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | 2452.79 |
| SPY\|all_period\|last\|all\|all | oi_zero_fraction | 0.227115 | 0.222558 | 0.228311 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | report_seconds_after_eastern_midnight | 26258.2 | 25951.1 | 26413.7 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPY\|all_period\|last\|all\|all | common_support_first | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | common_support_last | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | next_delta | 76.9223 | 67.7174 | 87.7499 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|all_period\|last\|all\|all | next_abs_delta | 150.229 | 132.933 | 176.409 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|all_period\|last\|all\|all | next_positive_fraction | 0.268681 | 0.264269 | 0.272713 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|all_period\|last\|all\|all | next_zero_fraction | 0.638613 | 0.633284 | 0.643295 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|all_period\|last\|all\|all | next_negative_fraction | 0.0927051 | 0.0887641 | 0.0981445 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|all_period\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|all_period\|last\|all\|all | censor_expired_fraction | 0.0165413 | 0.0115535 | 0.0194671 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|all_period\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 15450 | True | undefined |
| SPY\|all_period\|last\|all\|all | first_observed_fraction | 0.0186809 | 0.013608 | 0.0232492 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|all_period\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | late_clock_flag_fraction | 0.0209281 | 0.0144786 | 0.0241915 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | asof_0930_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | asof_0930_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | asof_1000_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | asof_1000_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | asof_1500_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | asof_1500_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|all_period\|last\|all\|all | ratio:oi_level_event_weighted | 2452.79 | 2424.42 | 2567.78 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|all_period\|last\|all\|expired | oi_level_date_mean | 4069.95 | 2811.03 | 4930.45 | 10 | 6 | 10 | 1960 | True | 5367.51 |
| SPY\|all_period\|last\|all\|expired | ratio:oi_level_event_weighted | 5367.51 | 2870.82 | 7145.68 | 10 | None | 10 | 1960 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_confirmation\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_development\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| SPY\|stage_training\|first\|all\|all | oi_level_date_mean | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | 2452.79 |
| SPY\|stage_training\|first\|all\|all | oi_zero_fraction | 0.227115 | 0.222558 | 0.228311 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | report_seconds_after_eastern_midnight | 26258.2 | 25951.1 | 26413.7 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPY\|stage_training\|first\|all\|all | common_support_first | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | common_support_last | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | next_delta | 76.9223 | 67.7174 | 87.7499 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|stage_training\|first\|all\|all | next_abs_delta | 150.229 | 132.933 | 176.409 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|stage_training\|first\|all\|all | next_positive_fraction | 0.268681 | 0.264269 | 0.272713 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|stage_training\|first\|all\|all | next_zero_fraction | 0.638613 | 0.633284 | 0.643295 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|stage_training\|first\|all\|all | next_negative_fraction | 0.0927051 | 0.0887641 | 0.0981445 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|stage_training\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|stage_training\|first\|all\|all | censor_expired_fraction | 0.0165413 | 0.0115535 | 0.0194671 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|stage_training\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 15450 | True | undefined |
| SPY\|stage_training\|first\|all\|all | first_observed_fraction | 0.0186809 | 0.013608 | 0.0232492 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|stage_training\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | late_clock_flag_fraction | 0.0209281 | 0.0144786 | 0.0241915 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | asof_0930_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | asof_0930_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | asof_1000_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | asof_1000_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | asof_1500_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | asof_1500_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|first\|all\|all | ratio:oi_level_event_weighted | 2452.79 | 2424.42 | 2567.78 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|stage_training\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | oi_level_date_mean | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | 2452.79 |
| SPY\|stage_training\|last\|all\|all | oi_zero_fraction | 0.227115 | 0.222558 | 0.228311 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | report_seconds_after_eastern_midnight | 26258.2 | 25951.1 | 26413.7 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPY\|stage_training\|last\|all\|all | common_support_first | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | common_support_last | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | next_delta | 76.9223 | 67.7174 | 87.7499 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|stage_training\|last\|all\|all | next_abs_delta | 150.229 | 132.933 | 176.409 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|stage_training\|last\|all\|all | next_positive_fraction | 0.268681 | 0.264269 | 0.272713 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|stage_training\|last\|all\|all | next_zero_fraction | 0.638613 | 0.633284 | 0.643295 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|stage_training\|last\|all\|all | next_negative_fraction | 0.0927051 | 0.0887641 | 0.0981445 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|stage_training\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|stage_training\|last\|all\|all | censor_expired_fraction | 0.0165413 | 0.0115535 | 0.0194671 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|stage_training\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 15450 | True | undefined |
| SPY\|stage_training\|last\|all\|all | first_observed_fraction | 0.0186809 | 0.013608 | 0.0232492 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|stage_training\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | late_clock_flag_fraction | 0.0209281 | 0.0144786 | 0.0241915 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | asof_0930_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | asof_0930_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | asof_1000_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | asof_1000_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | asof_1500_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | asof_1500_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|stage_training\|last\|all\|all | ratio:oi_level_event_weighted | 2452.79 | 2424.42 | 2567.78 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|stage_training\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | oi_level_date_mean | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | 2452.79 |
| SPY\|year_2020\|first\|all\|all | oi_zero_fraction | 0.227115 | 0.222558 | 0.228311 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | report_seconds_after_eastern_midnight | 26258.2 | 25951.1 | 26413.7 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPY\|year_2020\|first\|all\|all | common_support_first | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | common_support_last | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | next_delta | 76.9223 | 67.7174 | 87.7499 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|year_2020\|first\|all\|all | next_abs_delta | 150.229 | 132.933 | 176.409 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|year_2020\|first\|all\|all | next_positive_fraction | 0.268681 | 0.264269 | 0.272713 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|year_2020\|first\|all\|all | next_zero_fraction | 0.638613 | 0.633284 | 0.643295 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|year_2020\|first\|all\|all | next_negative_fraction | 0.0927051 | 0.0887641 | 0.0981445 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|year_2020\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|year_2020\|first\|all\|all | censor_expired_fraction | 0.0165413 | 0.0115535 | 0.0194671 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|year_2020\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 15450 | True | undefined |
| SPY\|year_2020\|first\|all\|all | first_observed_fraction | 0.0186809 | 0.013608 | 0.0232492 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|year_2020\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | late_clock_flag_fraction | 0.0209281 | 0.0144786 | 0.0241915 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | asof_0930_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | asof_0930_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | asof_1000_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | asof_1000_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | asof_1500_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | asof_1500_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|first\|all\|all | ratio:oi_level_event_weighted | 2452.79 | 2424.42 | 2567.78 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|year_2020\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | oi_level_date_mean | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | 2452.79 |
| SPY\|year_2020\|last\|all\|all | oi_zero_fraction | 0.227115 | 0.222558 | 0.228311 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | report_seconds_after_eastern_midnight | 26258.2 | 25951.1 | 26413.7 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | coverage_fraction | 1 | 1 | 1 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | missing_oi_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| SPY\|year_2020\|last\|all\|all | common_support_first | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | common_support_last | 2452.52 | 2424.44 | 2567.91 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | next_delta | 76.9223 | 67.7174 | 87.7499 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|year_2020\|last\|all\|all | next_abs_delta | 150.229 | 132.933 | 176.409 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|year_2020\|last\|all\|all | next_positive_fraction | 0.268681 | 0.264269 | 0.272713 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|year_2020\|last\|all\|all | next_zero_fraction | 0.638613 | 0.633284 | 0.643295 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|year_2020\|last\|all\|all | next_negative_fraction | 0.0927051 | 0.0887641 | 0.0981445 | 15 | 1 | 15 | 113336 | True | undefined |
| SPY\|year_2020\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|year_2020\|last\|all\|all | censor_expired_fraction | 0.0165413 | 0.0115535 | 0.0194671 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|year_2020\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 15450 | True | undefined |
| SPY\|year_2020\|last\|all\|all | first_observed_fraction | 0.0186809 | 0.013608 | 0.0232492 | 15 | 1 | 15 | 117502 | True | undefined |
| SPY\|year_2020\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | late_clock_flag_fraction | 0.0209281 | 0.0144786 | 0.0241915 | 16 | 0 | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | asof_0930_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | asof_0930_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | asof_1000_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | asof_1000_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | asof_1500_available_fraction | 0.978709 | 0.975524 | 0.985332 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | asof_1500_future_today_fraction | 0.0212908 | 0.0146679 | 0.0244763 | 16 | 0 | 16 | 121184 | True | undefined |
| SPY\|year_2020\|last\|all\|all | ratio:oi_level_event_weighted | 2452.79 | 2424.42 | 2567.78 | 16 | None | 16 | 123144 | True | undefined |
| SPY\|year_2020\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 123144 | True | undefined |
| VIX\|all_period\|first\|CALL\|all | oi_level_date_mean | 15521.6 | 14428.8 | 16409.8 | 16 | 0 | 16 | 4586 | True | 15377.1 |
| VIX\|all_period\|first\|CALL\|all | ratio:oi_level_event_weighted | 15377.1 | 14274.6 | 16348.1 | 16 | None | 16 | 4586 | True | undefined |
| VIX\|all_period\|first\|PUT\|all | oi_level_date_mean | 6636.97 | 6057.92 | 7498.8 | 16 | 0 | 16 | 4578 | True | 6474.68 |
| VIX\|all_period\|first\|PUT\|all | ratio:oi_level_event_weighted | 6474.68 | 6042.64 | 7335.19 | 16 | None | 16 | 4578 | True | undefined |
| VIX\|all_period\|first\|all\|0 | oi_level_date_mean | 35463.3 | 35463.3 | 35463.3 | 1 | 15 | 1 | 80 | True | 35463.3 |
| VIX\|all_period\|first\|all\|0 | ratio:oi_level_event_weighted | 35463.3 | 35463.3 | 35463.3 | 1 | None | 1 | 80 | True | undefined |
| VIX\|all_period\|first\|all\|1 | oi_level_date_mean | 35437.6 | 35437.6 | 35437.6 | 1 | 15 | 1 | 80 | True | 35437.6 |
| VIX\|all_period\|first\|all\|1 | ratio:oi_level_event_weighted | 35437.6 | 35437.6 | 35437.6 | 1 | None | 1 | 80 | True | undefined |
| VIX\|all_period\|first\|all\|2-7 | oi_level_date_mean | 34888.1 | 34420.4 | 35184.5 | 3 | 13 | 3 | 240 | True | 34888.1 |
| VIX\|all_period\|first\|all\|2-7 | ratio:oi_level_event_weighted | 34888.1 | 34420.4 | 35184.5 | 3 | None | 3 | 240 | True | undefined |
| VIX\|all_period\|first\|all\|31-60 | oi_level_date_mean | 18038.5 | 16035.3 | 21157.7 | 16 | 0 | 16 | 1250 | True | 18036.5 |
| VIX\|all_period\|first\|all\|31-60 | ratio:oi_level_event_weighted | 18036.5 | 16012.3 | 21227.4 | 16 | None | 16 | 1250 | True | undefined |
| VIX\|all_period\|first\|all\|61+ | oi_level_date_mean | 4382.84 | 3725.73 | 5282.15 | 16 | 0 | 16 | 6394 | True | 4209.21 |
| VIX\|all_period\|first\|all\|61+ | ratio:oi_level_event_weighted | 4209.21 | 3750.52 | 5066.59 | 16 | None | 16 | 6394 | True | undefined |
| VIX\|all_period\|first\|all\|8-30 | oi_level_date_mean | 33092.6 | 31239 | 34387.7 | 13 | 3 | 13 | 1040 | True | 33092.6 |
| VIX\|all_period\|first\|all\|8-30 | ratio:oi_level_event_weighted | 33092.6 | 31239 | 34387.7 | 13 | None | 13 | 1040 | True | undefined |
| VIX\|all_period\|first\|all\|all | oi_level_date_mean | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | 10929.8 |
| VIX\|all_period\|first\|all\|all | oi_zero_fraction | 0.254732 | 0.19684 | 0.310606 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | report_seconds_after_eastern_midnight | 25415.4 | 25261.4 | 25723.5 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|all_period\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|all_period\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|all_period\|first\|all\|all | common_support_first | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | common_support_last | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | next_delta | 321.817 | 285.241 | 405.277 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|all_period\|first\|all\|all | next_abs_delta | 573.035 | 464.727 | 665.547 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|all_period\|first\|all\|all | next_positive_fraction | 0.335579 | 0.307498 | 0.368007 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|all_period\|first\|all\|all | next_zero_fraction | 0.579287 | 0.533436 | 0.619519 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|all_period\|first\|all\|all | next_negative_fraction | 0.0851346 | 0.0718645 | 0.098835 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|all_period\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|all_period\|first\|all\|all | censor_expired_fraction | 0.00730594 | 0 | 0.00782779 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|all_period\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 1090 | True | undefined |
| VIX\|all_period\|first\|all\|all | first_observed_fraction | 0.0298311 | 0 | 0.0633521 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|all_period\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | late_clock_flag_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | asof_0930_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|first\|all\|all | asof_0930_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|first\|all\|all | asof_1000_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|first\|all\|all | asof_1000_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|first\|all\|all | asof_1500_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|first\|all\|all | asof_1500_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|first\|all\|all | ratio:oi_level_event_weighted | 10929.8 | 10327.1 | 11768.7 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|all_period\|first\|all\|expired | oi_level_date_mean | 27994.1 | 27994.1 | 27994.1 | 1 | 15 | 1 | 80 | True | 27994.1 |
| VIX\|all_period\|first\|all\|expired | ratio:oi_level_event_weighted | 27994.1 | 27994.1 | 27994.1 | 1 | None | 1 | 80 | True | undefined |
| VIX\|all_period\|last\|CALL\|all | oi_level_date_mean | 15521.6 | 14428.8 | 16409.8 | 16 | 0 | 16 | 4586 | True | 15377.1 |
| VIX\|all_period\|last\|CALL\|all | ratio:oi_level_event_weighted | 15377.1 | 14274.6 | 16348.1 | 16 | None | 16 | 4586 | True | undefined |
| VIX\|all_period\|last\|PUT\|all | oi_level_date_mean | 6636.97 | 6057.92 | 7498.8 | 16 | 0 | 16 | 4578 | True | 6474.68 |
| VIX\|all_period\|last\|PUT\|all | ratio:oi_level_event_weighted | 6474.68 | 6042.64 | 7335.19 | 16 | None | 16 | 4578 | True | undefined |
| VIX\|all_period\|last\|all\|0 | oi_level_date_mean | 35463.3 | 35463.3 | 35463.3 | 1 | 15 | 1 | 80 | True | 35463.3 |
| VIX\|all_period\|last\|all\|0 | ratio:oi_level_event_weighted | 35463.3 | 35463.3 | 35463.3 | 1 | None | 1 | 80 | True | undefined |
| VIX\|all_period\|last\|all\|1 | oi_level_date_mean | 35437.6 | 35437.6 | 35437.6 | 1 | 15 | 1 | 80 | True | 35437.6 |
| VIX\|all_period\|last\|all\|1 | ratio:oi_level_event_weighted | 35437.6 | 35437.6 | 35437.6 | 1 | None | 1 | 80 | True | undefined |
| VIX\|all_period\|last\|all\|2-7 | oi_level_date_mean | 34888.1 | 34420.4 | 35184.5 | 3 | 13 | 3 | 240 | True | 34888.1 |
| VIX\|all_period\|last\|all\|2-7 | ratio:oi_level_event_weighted | 34888.1 | 34420.4 | 35184.5 | 3 | None | 3 | 240 | True | undefined |
| VIX\|all_period\|last\|all\|31-60 | oi_level_date_mean | 18038.5 | 16035.3 | 21157.7 | 16 | 0 | 16 | 1250 | True | 18036.5 |
| VIX\|all_period\|last\|all\|31-60 | ratio:oi_level_event_weighted | 18036.5 | 16012.3 | 21227.4 | 16 | None | 16 | 1250 | True | undefined |
| VIX\|all_period\|last\|all\|61+ | oi_level_date_mean | 4382.84 | 3725.73 | 5282.15 | 16 | 0 | 16 | 6394 | True | 4209.21 |
| VIX\|all_period\|last\|all\|61+ | ratio:oi_level_event_weighted | 4209.21 | 3750.52 | 5066.59 | 16 | None | 16 | 6394 | True | undefined |
| VIX\|all_period\|last\|all\|8-30 | oi_level_date_mean | 33092.6 | 31239 | 34387.7 | 13 | 3 | 13 | 1040 | True | 33092.6 |
| VIX\|all_period\|last\|all\|8-30 | ratio:oi_level_event_weighted | 33092.6 | 31239 | 34387.7 | 13 | None | 13 | 1040 | True | undefined |
| VIX\|all_period\|last\|all\|all | oi_level_date_mean | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | 10929.8 |
| VIX\|all_period\|last\|all\|all | oi_zero_fraction | 0.254732 | 0.19684 | 0.310606 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | report_seconds_after_eastern_midnight | 25415.4 | 25261.4 | 25723.5 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|all_period\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|all_period\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|all_period\|last\|all\|all | common_support_first | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | common_support_last | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | next_delta | 321.817 | 285.241 | 405.277 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|all_period\|last\|all\|all | next_abs_delta | 573.035 | 464.727 | 665.547 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|all_period\|last\|all\|all | next_positive_fraction | 0.335579 | 0.307498 | 0.368007 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|all_period\|last\|all\|all | next_zero_fraction | 0.579287 | 0.533436 | 0.619519 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|all_period\|last\|all\|all | next_negative_fraction | 0.0851346 | 0.0718645 | 0.098835 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|all_period\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|all_period\|last\|all\|all | censor_expired_fraction | 0.00730594 | 0 | 0.00782779 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|all_period\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 1090 | True | undefined |
| VIX\|all_period\|last\|all\|all | first_observed_fraction | 0.0298311 | 0 | 0.0633521 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|all_period\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | late_clock_flag_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | asof_0930_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|last\|all\|all | asof_0930_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|last\|all\|all | asof_1000_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|last\|all\|all | asof_1000_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|last\|all\|all | asof_1500_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|last\|all\|all | asof_1500_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|all_period\|last\|all\|all | ratio:oi_level_event_weighted | 10929.8 | 10327.1 | 11768.7 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|all_period\|last\|all\|expired | oi_level_date_mean | 27994.1 | 27994.1 | 27994.1 | 1 | 15 | 1 | 80 | True | 27994.1 |
| VIX\|all_period\|last\|all\|expired | ratio:oi_level_event_weighted | 27994.1 | 27994.1 | 27994.1 | 1 | None | 1 | 80 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_confirmation\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|first\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | oi_level_date_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | oi_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | report_seconds_after_eastern_midnight | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | update_candidate_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | common_support_first | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | common_support_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | common_support_first_minus_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | next_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | next_abs_delta | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | next_positive_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | next_zero_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | next_negative_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | censor_missing_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | censor_expired_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | censor_boundary_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | first_observed_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | position_mapping_agree_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | event_local_mismatch_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | future_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | late_clock_flag_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | asof_0930_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | asof_0930_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | asof_0930_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | asof_1000_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | asof_1000_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | asof_1000_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | asof_1500_available_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | asof_1500_stale_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | asof_1500_future_today_fraction | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | ratio:oi_level_event_weighted | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_development\|last\|all\|all | ratio:common_first_over_last | undefined | undefined | undefined | 0 | 0 | 0 | 0 | True | undefined |
| VIX\|stage_training\|first\|all\|all | oi_level_date_mean | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | 10929.8 |
| VIX\|stage_training\|first\|all\|all | oi_zero_fraction | 0.254732 | 0.19684 | 0.310606 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | report_seconds_after_eastern_midnight | 25415.4 | 25261.4 | 25723.5 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|stage_training\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|stage_training\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|stage_training\|first\|all\|all | common_support_first | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | common_support_last | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | next_delta | 321.817 | 285.241 | 405.277 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|stage_training\|first\|all\|all | next_abs_delta | 573.035 | 464.727 | 665.547 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|stage_training\|first\|all\|all | next_positive_fraction | 0.335579 | 0.307498 | 0.368007 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|stage_training\|first\|all\|all | next_zero_fraction | 0.579287 | 0.533436 | 0.619519 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|stage_training\|first\|all\|all | next_negative_fraction | 0.0851346 | 0.0718645 | 0.098835 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|stage_training\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|stage_training\|first\|all\|all | censor_expired_fraction | 0.00730594 | 0 | 0.00782779 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|stage_training\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 1090 | True | undefined |
| VIX\|stage_training\|first\|all\|all | first_observed_fraction | 0.0298311 | 0 | 0.0633521 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|stage_training\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | late_clock_flag_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | asof_0930_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|first\|all\|all | asof_0930_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|first\|all\|all | asof_1000_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|first\|all\|all | asof_1000_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|first\|all\|all | asof_1500_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|first\|all\|all | asof_1500_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|first\|all\|all | ratio:oi_level_event_weighted | 10929.8 | 10327.1 | 11768.7 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|stage_training\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | oi_level_date_mean | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | 10929.8 |
| VIX\|stage_training\|last\|all\|all | oi_zero_fraction | 0.254732 | 0.19684 | 0.310606 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | report_seconds_after_eastern_midnight | 25415.4 | 25261.4 | 25723.5 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|stage_training\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|stage_training\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|stage_training\|last\|all\|all | common_support_first | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | common_support_last | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | next_delta | 321.817 | 285.241 | 405.277 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|stage_training\|last\|all\|all | next_abs_delta | 573.035 | 464.727 | 665.547 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|stage_training\|last\|all\|all | next_positive_fraction | 0.335579 | 0.307498 | 0.368007 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|stage_training\|last\|all\|all | next_zero_fraction | 0.579287 | 0.533436 | 0.619519 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|stage_training\|last\|all\|all | next_negative_fraction | 0.0851346 | 0.0718645 | 0.098835 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|stage_training\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|stage_training\|last\|all\|all | censor_expired_fraction | 0.00730594 | 0 | 0.00782779 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|stage_training\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 1090 | True | undefined |
| VIX\|stage_training\|last\|all\|all | first_observed_fraction | 0.0298311 | 0 | 0.0633521 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|stage_training\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | late_clock_flag_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | asof_0930_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|last\|all\|all | asof_0930_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|last\|all\|all | asof_1000_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|last\|all\|all | asof_1000_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|last\|all\|all | asof_1500_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|last\|all\|all | asof_1500_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|stage_training\|last\|all\|all | ratio:oi_level_event_weighted | 10929.8 | 10327.1 | 11768.7 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|stage_training\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | oi_level_date_mean | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | 10929.8 |
| VIX\|year_2020\|first\|all\|all | oi_zero_fraction | 0.254732 | 0.19684 | 0.310606 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | report_seconds_after_eastern_midnight | 25415.4 | 25261.4 | 25723.5 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|year_2020\|first\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|year_2020\|first\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|year_2020\|first\|all\|all | common_support_first | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | common_support_last | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | next_delta | 321.817 | 285.241 | 405.277 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|year_2020\|first\|all\|all | next_abs_delta | 573.035 | 464.727 | 665.547 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|year_2020\|first\|all\|all | next_positive_fraction | 0.335579 | 0.307498 | 0.368007 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|year_2020\|first\|all\|all | next_zero_fraction | 0.579287 | 0.533436 | 0.619519 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|year_2020\|first\|all\|all | next_negative_fraction | 0.0851346 | 0.0718645 | 0.098835 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|year_2020\|first\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|year_2020\|first\|all\|all | censor_expired_fraction | 0.00730594 | 0 | 0.00782779 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|year_2020\|first\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 1090 | True | undefined |
| VIX\|year_2020\|first\|all\|all | first_observed_fraction | 0.0298311 | 0 | 0.0633521 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|year_2020\|first\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | late_clock_flag_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | asof_0930_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|first\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|first\|all\|all | asof_0930_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|first\|all\|all | asof_1000_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|first\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|first\|all\|all | asof_1000_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|first\|all\|all | asof_1500_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|first\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|first\|all\|all | asof_1500_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|first\|all\|all | ratio:oi_level_event_weighted | 10929.8 | 10327.1 | 11768.7 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|year_2020\|first\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | oi_level_date_mean | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | 10929.8 |
| VIX\|year_2020\|last\|all\|all | oi_zero_fraction | 0.254732 | 0.19684 | 0.310606 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | report_seconds_after_eastern_midnight | 25415.4 | 25261.4 | 25723.5 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | coverage_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|year_2020\|last\|all\|all | missing_oi_fraction | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|year_2020\|last\|all\|all | update_candidate_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | update_difference_mean | undefined | undefined | undefined | 0 | 16 | 0 | 0 | True | undefined |
| VIX\|year_2020\|last\|all\|all | common_support_first | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | common_support_last | 11084.1 | 10411.5 | 11916.7 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | common_support_first_minus_last | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | next_delta | 321.817 | 285.241 | 405.277 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|year_2020\|last\|all\|all | next_abs_delta | 573.035 | 464.727 | 665.547 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|year_2020\|last\|all\|all | next_positive_fraction | 0.335579 | 0.307498 | 0.368007 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|year_2020\|last\|all\|all | next_zero_fraction | 0.579287 | 0.533436 | 0.619519 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|year_2020\|last\|all\|all | next_negative_fraction | 0.0851346 | 0.0718645 | 0.098835 | 15 | 1 | 15 | 8434 | True | undefined |
| VIX\|year_2020\|last\|all\|all | censor_missing_fraction | 0 | 0 | 0 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|year_2020\|last\|all\|all | censor_expired_fraction | 0.00730594 | 0 | 0.00782779 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|year_2020\|last\|all\|all | censor_boundary_fraction | 1 | 1 | 1 | 2 | 14 | 2 | 1090 | True | undefined |
| VIX\|year_2020\|last\|all\|all | first_observed_fraction | 0.0298311 | 0 | 0.0633521 | 15 | 1 | 15 | 8804 | True | undefined |
| VIX\|year_2020\|last\|all\|all | position_mapping_agree_fraction | 0.9375 | 0.875 | 1 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | event_local_mismatch_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | future_clock_flag_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | late_clock_flag_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | asof_0930_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|last\|all\|all | asof_0930_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|last\|all\|all | asof_0930_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|last\|all\|all | asof_1000_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|last\|all\|all | asof_1000_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|last\|all\|all | asof_1000_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|last\|all\|all | asof_1500_available_fraction | 0.996767 | 0.990302 | 1 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|last\|all\|all | asof_1500_stale_fraction | 0 | 0 | 0 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|last\|all\|all | asof_1500_future_today_fraction | 0.00323276 | 0 | 0.00969828 | 16 | 0 | 16 | 9084 | True | undefined |
| VIX\|year_2020\|last\|all\|all | ratio:oi_level_event_weighted | 10929.8 | 10327.1 | 11768.7 | 16 | None | 16 | 9164 | True | undefined |
| VIX\|year_2020\|last\|all\|all | ratio:common_first_over_last | 1 | 1 | 1 | 16 | None | 16 | 9164 | True | undefined |

## Equal-date empirical quantiles of the date-level series

Each date has one weight. These are not event-weighted quantiles. Event-weighted points use the mass/count ratio separately. Contract observations are not additional independent dates. censor_boundary_fraction uses only the separately retained source-boundary endpoint population; its event support reports that boundary count.

- `NDXP\|all_period\|first\|CALL\|all` `oi_level_date_mean`: q0.01=4.88171, q0.05=5.09004, q0.25=5.48607, q0.5=5.77474, q0.75=6.08632, q0.95=6.55826, q0.99=6.70434
- `NDXP\|all_period\|first\|CALL\|all` `oi_mass`: q0.01=8910.1, q0.05=8918.5, q0.25=9350, q0.5=9736.5, q0.75=10011.5, q0.95=10472.8, q0.99=10647.4
- `NDXP\|all_period\|first\|CALL\|all` `oi_width`: q0.01=1479.5, q0.05=1497.5, q0.25=1528.5, q0.5=1664, q0.75=1765.25, q0.95=1951, q0.99=1984.6
- `NDXP\|all_period\|first\|PUT\|all` `oi_level_date_mean`: q0.01=6.06958, q0.05=6.43916, q0.25=7.22572, q0.5=8.29178, q0.75=8.90288, q0.95=9.84344, q0.99=10.0904
- `NDXP\|all_period\|first\|PUT\|all` `oi_mass`: q0.01=10540.4, q0.05=10790, q0.25=11756.8, q0.5=13656.5, q0.75=15128, q0.95=17407.2, q0.99=18535.8
- `NDXP\|all_period\|first\|PUT\|all` `oi_width`: q0.01=1479.5, q0.05=1497.5, q0.25=1528.5, q0.5=1664, q0.75=1765.25, q0.95=1951, q0.99=1984.6
- `NDXP\|all_period\|first\|all\|0` `oi_level_date_mean`: q0.01=16.9921, q0.05=17.177, q0.25=18.0151, q0.5=21.192, q0.75=24.0614, q0.95=24.9389, q0.99=25.1616
- `NDXP\|all_period\|first\|all\|0` `oi_mass`: q0.01=6568.35, q0.05=6569.75, q0.25=6584.25, q0.5=7542.5, q0.75=8975.5, q0.95=10999.2, q0.99=11494.2
- `NDXP\|all_period\|first\|all\|0` `oi_width`: q0.01=337, q0.05=341, q0.25=359.5, q0.5=376, q0.75=386.5, q0.95=458.5, q0.99=477.3
- `NDXP\|all_period\|first\|all\|1` `oi_level_date_mean`: q0.01=13.8225, q0.05=14.0747, q0.25=15.2802, q0.5=18.3749, q0.75=20.9785, q0.95=21.3799, q0.99=21.4613
- `NDXP\|all_period\|first\|all\|1` `oi_mass`: q0.01=5122.3, q0.05=5247.5, q0.25=5744.75, q0.5=6454.5, q0.75=7924.75, q0.95=9531.25, q0.99=9884.65
- `NDXP\|all_period\|first\|all\|1` `oi_width`: q0.01=337, q0.05=341, q0.25=359.5, q0.5=376, q0.75=386.5, q0.95=458.5, q0.99=477.3
- `NDXP\|all_period\|first\|all\|2-7` `oi_level_date_mean`: q0.01=4.51429, q0.05=4.8093, q0.25=7.58045, q0.5=11.3974, q0.75=12.4279, q0.95=15.2641, q0.99=17.4688
- `NDXP\|all_period\|first\|all\|2-7` `oi_mass`: q0.01=1689.76, q0.05=1876.8, q0.25=2981, q0.5=5191, q0.75=8115, q0.95=10457.6, q0.99=10621.1
- `NDXP\|all_period\|first\|all\|2-7` `oi_width`: q0.01=336.56, q0.05=338.8, q0.25=353, q0.5=398, q0.75=692, q0.95=855.6, q0.99=862.32
- `NDXP\|all_period\|first\|all\|31-60` `oi_level_date_mean`: q0.01=0.444169, q0.05=0.517873, q0.25=0.597143, q0.5=0.847666, q0.75=1.10329, q0.95=1.90901, q0.99=2.20493
- `NDXP\|all_period\|first\|all\|31-60` `oi_mass`: q0.01=148.2, q0.05=165, q0.25=286, q0.5=364.5, q0.75=468.25, q0.95=784.5, q0.99=869.7
- `NDXP\|all_period\|first\|all\|31-60` `oi_width`: q0.01=250.3, q0.05=251.5, q0.25=304.5, q0.5=429, q0.75=501, q0.95=587.5, q0.99=677.5
- `NDXP\|all_period\|first\|all\|8-30` `oi_level_date_mean`: q0.01=2.85124, q0.05=3.58207, q0.25=4.48051, q0.5=4.82121, q0.75=5.11023, q0.95=5.49117, q0.99=5.54677
- `NDXP\|all_period\|first\|all\|8-30` `oi_mass`: q0.01=5234.85, q0.05=7046.25, q0.25=8437.75, q0.5=9259, q0.75=10062, q0.95=12892.2, q0.99=13327.2
- `NDXP\|all_period\|first\|all\|8-30` `oi_width`: q0.01=1702.5, q0.05=1720.5, q0.25=1788, q0.5=1914, q0.75=2225, q0.95=2472, q0.99=2606.4
- `NDXP\|all_period\|first\|all\|all` `oi_level_date_mean`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|all_period\|first\|all\|all` `oi_zero_fraction`: q0.01=0.54528, q0.05=0.548971, q0.25=0.564513, q0.5=0.582719, q0.75=0.603608, q0.95=0.622805, q0.99=0.624716
- `NDXP\|all_period\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25525.9, q0.5=26397.9, q0.75=29216.7, q0.95=33834.1, q0.99=34117.5
- `NDXP\|all_period\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|all_period\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|first\|all\|all` `oi_mass`: q0.01=19653.7, q0.05=19768.2, q0.25=21634.5, q0.5=23715.5, q0.75=24534, q0.95=27462.2, q0.99=29099.6
- `NDXP\|all_period\|first\|all\|all` `oi_width`: q0.01=2959, q0.05=2995, q0.25=3057, q0.5=3328, q0.75=3530.5, q0.95=3902, q0.99=3969.2
- `NDXP\|all_period\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|first\|all\|all` `common_support_first`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|all_period\|first\|all\|all` `common_support_last`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|all_period\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|first\|all\|all` `next_delta`: q0.01=0.283879, q0.05=0.475354, q0.25=0.685583, q0.5=0.853093, q0.75=1.05547, q0.95=1.53982, q0.99=1.73029
- `NDXP\|all_period\|first\|all\|all` `next_abs_delta`: q0.01=0.766088, q0.05=0.866377, q0.25=1.15431, q0.5=1.56457, q0.75=1.91176, q0.95=2.39909, q0.99=2.45731
- `NDXP\|all_period\|first\|all\|all` `next_positive_fraction`: q0.01=0.115488, q0.05=0.115812, q0.25=0.120149, q0.5=0.129702, q0.75=0.13381, q0.95=0.144833, q0.99=0.149911
- `NDXP\|all_period\|first\|all\|all` `next_zero_fraction`: q0.01=0.804288, q0.05=0.80815, q0.25=0.821363, q0.5=0.836608, q0.75=0.856637, q0.95=0.864307, q0.99=0.869769
- `NDXP\|all_period\|first\|all\|all` `next_negative_fraction`: q0.01=0.013627, q0.05=0.0142978, q0.25=0.0207551, q0.5=0.0256696, q0.75=0.0482082, q0.95=0.0620882, q0.99=0.0658396
- `NDXP\|all_period\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0957404, q0.95=0.109634, q0.99=0.113275
- `NDXP\|all_period\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|all_period\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00503, q0.5=0.0206004, q0.75=0.0730222, q0.95=0.154165, q0.99=0.159579
- `NDXP\|all_period\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|all_period\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0238634, q0.75=0.0830338, q0.95=0.179957, q0.99=0.185904
- `NDXP\|all_period\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|all_period\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|all_period\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|all_period\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|all_period\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|all_period\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|all_period\|first\|all\|expired` `oi_level_date_mean`: q0.01=15.7557, q0.05=16.1117, q0.25=17.4851, q0.5=18.1759, q0.75=19.9293, q0.95=22.1698, q0.99=22.6625
- `NDXP\|all_period\|first\|all\|expired` `oi_mass`: q0.01=5847.15, q0.05=5923.75, q0.25=6365.5, q0.5=6883.5, q0.75=7476.5, q0.95=7736.25, q0.99=7757.65
- `NDXP\|all_period\|first\|all\|expired` `oi_width`: q0.01=337, q0.05=341, q0.25=359.5, q0.5=371, q0.75=379.5, q0.95=386.5, q0.99=387.7
- `NDXP\|all_period\|last\|CALL\|all` `oi_level_date_mean`: q0.01=4.88171, q0.05=5.09004, q0.25=5.48607, q0.5=5.77474, q0.75=6.08632, q0.95=6.55826, q0.99=6.70434
- `NDXP\|all_period\|last\|CALL\|all` `oi_mass`: q0.01=8910.1, q0.05=8918.5, q0.25=9350, q0.5=9736.5, q0.75=10011.5, q0.95=10472.8, q0.99=10647.4
- `NDXP\|all_period\|last\|CALL\|all` `oi_width`: q0.01=1479.5, q0.05=1497.5, q0.25=1528.5, q0.5=1664, q0.75=1765.25, q0.95=1951, q0.99=1984.6
- `NDXP\|all_period\|last\|PUT\|all` `oi_level_date_mean`: q0.01=6.06958, q0.05=6.43916, q0.25=7.22572, q0.5=8.29178, q0.75=8.90288, q0.95=9.84344, q0.99=10.0904
- `NDXP\|all_period\|last\|PUT\|all` `oi_mass`: q0.01=10540.4, q0.05=10790, q0.25=11756.8, q0.5=13656.5, q0.75=15128, q0.95=17407.2, q0.99=18535.8
- `NDXP\|all_period\|last\|PUT\|all` `oi_width`: q0.01=1479.5, q0.05=1497.5, q0.25=1528.5, q0.5=1664, q0.75=1765.25, q0.95=1951, q0.99=1984.6
- `NDXP\|all_period\|last\|all\|0` `oi_level_date_mean`: q0.01=16.9921, q0.05=17.177, q0.25=18.0151, q0.5=21.192, q0.75=24.0614, q0.95=24.9389, q0.99=25.1616
- `NDXP\|all_period\|last\|all\|0` `oi_mass`: q0.01=6568.35, q0.05=6569.75, q0.25=6584.25, q0.5=7542.5, q0.75=8975.5, q0.95=10999.2, q0.99=11494.2
- `NDXP\|all_period\|last\|all\|0` `oi_width`: q0.01=337, q0.05=341, q0.25=359.5, q0.5=376, q0.75=386.5, q0.95=458.5, q0.99=477.3
- `NDXP\|all_period\|last\|all\|1` `oi_level_date_mean`: q0.01=13.8225, q0.05=14.0747, q0.25=15.2802, q0.5=18.3749, q0.75=20.9785, q0.95=21.3799, q0.99=21.4613
- `NDXP\|all_period\|last\|all\|1` `oi_mass`: q0.01=5122.3, q0.05=5247.5, q0.25=5744.75, q0.5=6454.5, q0.75=7924.75, q0.95=9531.25, q0.99=9884.65
- `NDXP\|all_period\|last\|all\|1` `oi_width`: q0.01=337, q0.05=341, q0.25=359.5, q0.5=376, q0.75=386.5, q0.95=458.5, q0.99=477.3
- `NDXP\|all_period\|last\|all\|2-7` `oi_level_date_mean`: q0.01=4.51429, q0.05=4.8093, q0.25=7.58045, q0.5=11.3974, q0.75=12.4279, q0.95=15.2641, q0.99=17.4688
- `NDXP\|all_period\|last\|all\|2-7` `oi_mass`: q0.01=1689.76, q0.05=1876.8, q0.25=2981, q0.5=5191, q0.75=8115, q0.95=10457.6, q0.99=10621.1
- `NDXP\|all_period\|last\|all\|2-7` `oi_width`: q0.01=336.56, q0.05=338.8, q0.25=353, q0.5=398, q0.75=692, q0.95=855.6, q0.99=862.32
- `NDXP\|all_period\|last\|all\|31-60` `oi_level_date_mean`: q0.01=0.444169, q0.05=0.517873, q0.25=0.597143, q0.5=0.847666, q0.75=1.10329, q0.95=1.90901, q0.99=2.20493
- `NDXP\|all_period\|last\|all\|31-60` `oi_mass`: q0.01=148.2, q0.05=165, q0.25=286, q0.5=364.5, q0.75=468.25, q0.95=784.5, q0.99=869.7
- `NDXP\|all_period\|last\|all\|31-60` `oi_width`: q0.01=250.3, q0.05=251.5, q0.25=304.5, q0.5=429, q0.75=501, q0.95=587.5, q0.99=677.5
- `NDXP\|all_period\|last\|all\|8-30` `oi_level_date_mean`: q0.01=2.85124, q0.05=3.58207, q0.25=4.48051, q0.5=4.82121, q0.75=5.11023, q0.95=5.49117, q0.99=5.54677
- `NDXP\|all_period\|last\|all\|8-30` `oi_mass`: q0.01=5234.85, q0.05=7046.25, q0.25=8437.75, q0.5=9259, q0.75=10062, q0.95=12892.2, q0.99=13327.2
- `NDXP\|all_period\|last\|all\|8-30` `oi_width`: q0.01=1702.5, q0.05=1720.5, q0.25=1788, q0.5=1914, q0.75=2225, q0.95=2472, q0.99=2606.4
- `NDXP\|all_period\|last\|all\|all` `oi_level_date_mean`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|all_period\|last\|all\|all` `oi_zero_fraction`: q0.01=0.54528, q0.05=0.548971, q0.25=0.564513, q0.5=0.582719, q0.75=0.603608, q0.95=0.622805, q0.99=0.624716
- `NDXP\|all_period\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25525.9, q0.5=26397.9, q0.75=29216.7, q0.95=33834.1, q0.99=34117.5
- `NDXP\|all_period\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|all_period\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|last\|all\|all` `oi_mass`: q0.01=19653.7, q0.05=19768.2, q0.25=21634.5, q0.5=23715.5, q0.75=24534, q0.95=27462.2, q0.99=29099.6
- `NDXP\|all_period\|last\|all\|all` `oi_width`: q0.01=2959, q0.05=2995, q0.25=3057, q0.5=3328, q0.75=3530.5, q0.95=3902, q0.99=3969.2
- `NDXP\|all_period\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|last\|all\|all` `common_support_first`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|all_period\|last\|all\|all` `common_support_last`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|all_period\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|last\|all\|all` `next_delta`: q0.01=0.283879, q0.05=0.475354, q0.25=0.685583, q0.5=0.853093, q0.75=1.05547, q0.95=1.53982, q0.99=1.73029
- `NDXP\|all_period\|last\|all\|all` `next_abs_delta`: q0.01=0.766088, q0.05=0.866377, q0.25=1.15431, q0.5=1.56457, q0.75=1.91176, q0.95=2.39909, q0.99=2.45731
- `NDXP\|all_period\|last\|all\|all` `next_positive_fraction`: q0.01=0.115488, q0.05=0.115812, q0.25=0.120149, q0.5=0.129702, q0.75=0.13381, q0.95=0.144833, q0.99=0.149911
- `NDXP\|all_period\|last\|all\|all` `next_zero_fraction`: q0.01=0.804288, q0.05=0.80815, q0.25=0.821363, q0.5=0.836608, q0.75=0.856637, q0.95=0.864307, q0.99=0.869769
- `NDXP\|all_period\|last\|all\|all` `next_negative_fraction`: q0.01=0.013627, q0.05=0.0142978, q0.25=0.0207551, q0.5=0.0256696, q0.75=0.0482082, q0.95=0.0620882, q0.99=0.0658396
- `NDXP\|all_period\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0957404, q0.95=0.109634, q0.99=0.113275
- `NDXP\|all_period\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|all_period\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00503, q0.5=0.0206004, q0.75=0.0730222, q0.95=0.154165, q0.99=0.159579
- `NDXP\|all_period\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|all_period\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0238634, q0.75=0.0830338, q0.95=0.179957, q0.99=0.185904
- `NDXP\|all_period\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|all_period\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|all_period\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|all_period\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|all_period\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|all_period\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|all_period\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|all_period\|last\|all\|expired` `oi_level_date_mean`: q0.01=15.7557, q0.05=16.1117, q0.25=17.4851, q0.5=18.1759, q0.75=19.9293, q0.95=22.1698, q0.99=22.6625
- `NDXP\|all_period\|last\|all\|expired` `oi_mass`: q0.01=5847.15, q0.05=5923.75, q0.25=6365.5, q0.5=6883.5, q0.75=7476.5, q0.95=7736.25, q0.99=7757.65
- `NDXP\|all_period\|last\|all\|expired` `oi_width`: q0.01=337, q0.05=341, q0.25=359.5, q0.5=371, q0.75=379.5, q0.95=386.5, q0.99=387.7
- `NDXP\|stage_confirmation\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `NDXP\|stage_confirmation\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `NDXP\|stage_development\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `NDXP\|stage_development\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `NDXP\|stage_training\|first\|all\|all` `oi_level_date_mean`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|stage_training\|first\|all\|all` `oi_zero_fraction`: q0.01=0.54528, q0.05=0.548971, q0.25=0.564513, q0.5=0.582719, q0.75=0.603608, q0.95=0.622805, q0.99=0.624716
- `NDXP\|stage_training\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25525.9, q0.5=26397.9, q0.75=29216.7, q0.95=33834.1, q0.99=34117.5
- `NDXP\|stage_training\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|stage_training\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|first\|all\|all` `oi_mass`: q0.01=19653.7, q0.05=19768.2, q0.25=21634.5, q0.5=23715.5, q0.75=24534, q0.95=27462.2, q0.99=29099.6
- `NDXP\|stage_training\|first\|all\|all` `oi_width`: q0.01=2959, q0.05=2995, q0.25=3057, q0.5=3328, q0.75=3530.5, q0.95=3902, q0.99=3969.2
- `NDXP\|stage_training\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|first\|all\|all` `common_support_first`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|stage_training\|first\|all\|all` `common_support_last`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|stage_training\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|first\|all\|all` `next_delta`: q0.01=0.283879, q0.05=0.475354, q0.25=0.685583, q0.5=0.853093, q0.75=1.05547, q0.95=1.53982, q0.99=1.73029
- `NDXP\|stage_training\|first\|all\|all` `next_abs_delta`: q0.01=0.766088, q0.05=0.866377, q0.25=1.15431, q0.5=1.56457, q0.75=1.91176, q0.95=2.39909, q0.99=2.45731
- `NDXP\|stage_training\|first\|all\|all` `next_positive_fraction`: q0.01=0.115488, q0.05=0.115812, q0.25=0.120149, q0.5=0.129702, q0.75=0.13381, q0.95=0.144833, q0.99=0.149911
- `NDXP\|stage_training\|first\|all\|all` `next_zero_fraction`: q0.01=0.804288, q0.05=0.80815, q0.25=0.821363, q0.5=0.836608, q0.75=0.856637, q0.95=0.864307, q0.99=0.869769
- `NDXP\|stage_training\|first\|all\|all` `next_negative_fraction`: q0.01=0.013627, q0.05=0.0142978, q0.25=0.0207551, q0.5=0.0256696, q0.75=0.0482082, q0.95=0.0620882, q0.99=0.0658396
- `NDXP\|stage_training\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0957404, q0.95=0.109634, q0.99=0.113275
- `NDXP\|stage_training\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|stage_training\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00503, q0.5=0.0206004, q0.75=0.0730222, q0.95=0.154165, q0.99=0.159579
- `NDXP\|stage_training\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|stage_training\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0238634, q0.75=0.0830338, q0.95=0.179957, q0.99=0.185904
- `NDXP\|stage_training\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|stage_training\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|stage_training\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|stage_training\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|stage_training\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|stage_training\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|stage_training\|last\|all\|all` `oi_level_date_mean`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|stage_training\|last\|all\|all` `oi_zero_fraction`: q0.01=0.54528, q0.05=0.548971, q0.25=0.564513, q0.5=0.582719, q0.75=0.603608, q0.95=0.622805, q0.99=0.624716
- `NDXP\|stage_training\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25525.9, q0.5=26397.9, q0.75=29216.7, q0.95=33834.1, q0.99=34117.5
- `NDXP\|stage_training\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|stage_training\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|last\|all\|all` `oi_mass`: q0.01=19653.7, q0.05=19768.2, q0.25=21634.5, q0.5=23715.5, q0.75=24534, q0.95=27462.2, q0.99=29099.6
- `NDXP\|stage_training\|last\|all\|all` `oi_width`: q0.01=2959, q0.05=2995, q0.25=3057, q0.5=3328, q0.75=3530.5, q0.95=3902, q0.99=3969.2
- `NDXP\|stage_training\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|last\|all\|all` `common_support_first`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|stage_training\|last\|all\|all` `common_support_last`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|stage_training\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|last\|all\|all` `next_delta`: q0.01=0.283879, q0.05=0.475354, q0.25=0.685583, q0.5=0.853093, q0.75=1.05547, q0.95=1.53982, q0.99=1.73029
- `NDXP\|stage_training\|last\|all\|all` `next_abs_delta`: q0.01=0.766088, q0.05=0.866377, q0.25=1.15431, q0.5=1.56457, q0.75=1.91176, q0.95=2.39909, q0.99=2.45731
- `NDXP\|stage_training\|last\|all\|all` `next_positive_fraction`: q0.01=0.115488, q0.05=0.115812, q0.25=0.120149, q0.5=0.129702, q0.75=0.13381, q0.95=0.144833, q0.99=0.149911
- `NDXP\|stage_training\|last\|all\|all` `next_zero_fraction`: q0.01=0.804288, q0.05=0.80815, q0.25=0.821363, q0.5=0.836608, q0.75=0.856637, q0.95=0.864307, q0.99=0.869769
- `NDXP\|stage_training\|last\|all\|all` `next_negative_fraction`: q0.01=0.013627, q0.05=0.0142978, q0.25=0.0207551, q0.5=0.0256696, q0.75=0.0482082, q0.95=0.0620882, q0.99=0.0658396
- `NDXP\|stage_training\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0957404, q0.95=0.109634, q0.99=0.113275
- `NDXP\|stage_training\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|stage_training\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00503, q0.5=0.0206004, q0.75=0.0730222, q0.95=0.154165, q0.99=0.159579
- `NDXP\|stage_training\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|stage_training\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0238634, q0.75=0.0830338, q0.95=0.179957, q0.99=0.185904
- `NDXP\|stage_training\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|stage_training\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|stage_training\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|stage_training\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|stage_training\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|stage_training\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|stage_training\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|year_2020\|first\|all\|all` `oi_level_date_mean`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|year_2020\|first\|all\|all` `oi_zero_fraction`: q0.01=0.54528, q0.05=0.548971, q0.25=0.564513, q0.5=0.582719, q0.75=0.603608, q0.95=0.622805, q0.99=0.624716
- `NDXP\|year_2020\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25525.9, q0.5=26397.9, q0.75=29216.7, q0.95=33834.1, q0.99=34117.5
- `NDXP\|year_2020\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|year_2020\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|first\|all\|all` `oi_mass`: q0.01=19653.7, q0.05=19768.2, q0.25=21634.5, q0.5=23715.5, q0.75=24534, q0.95=27462.2, q0.99=29099.6
- `NDXP\|year_2020\|first\|all\|all` `oi_width`: q0.01=2959, q0.05=2995, q0.25=3057, q0.5=3328, q0.75=3530.5, q0.95=3902, q0.99=3969.2
- `NDXP\|year_2020\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|first\|all\|all` `common_support_first`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|year_2020\|first\|all\|all` `common_support_last`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|year_2020\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|first\|all\|all` `next_delta`: q0.01=0.283879, q0.05=0.475354, q0.25=0.685583, q0.5=0.853093, q0.75=1.05547, q0.95=1.53982, q0.99=1.73029
- `NDXP\|year_2020\|first\|all\|all` `next_abs_delta`: q0.01=0.766088, q0.05=0.866377, q0.25=1.15431, q0.5=1.56457, q0.75=1.91176, q0.95=2.39909, q0.99=2.45731
- `NDXP\|year_2020\|first\|all\|all` `next_positive_fraction`: q0.01=0.115488, q0.05=0.115812, q0.25=0.120149, q0.5=0.129702, q0.75=0.13381, q0.95=0.144833, q0.99=0.149911
- `NDXP\|year_2020\|first\|all\|all` `next_zero_fraction`: q0.01=0.804288, q0.05=0.80815, q0.25=0.821363, q0.5=0.836608, q0.75=0.856637, q0.95=0.864307, q0.99=0.869769
- `NDXP\|year_2020\|first\|all\|all` `next_negative_fraction`: q0.01=0.013627, q0.05=0.0142978, q0.25=0.0207551, q0.5=0.0256696, q0.75=0.0482082, q0.95=0.0620882, q0.99=0.0658396
- `NDXP\|year_2020\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0957404, q0.95=0.109634, q0.99=0.113275
- `NDXP\|year_2020\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|year_2020\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00503, q0.5=0.0206004, q0.75=0.0730222, q0.95=0.154165, q0.99=0.159579
- `NDXP\|year_2020\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|year_2020\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0238634, q0.75=0.0830338, q0.95=0.179957, q0.99=0.185904
- `NDXP\|year_2020\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|year_2020\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|year_2020\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|year_2020\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|year_2020\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|year_2020\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|year_2020\|last\|all\|all` `oi_level_date_mean`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|year_2020\|last\|all\|all` `oi_zero_fraction`: q0.01=0.54528, q0.05=0.548971, q0.25=0.564513, q0.5=0.582719, q0.75=0.603608, q0.95=0.622805, q0.99=0.624716
- `NDXP\|year_2020\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25525.9, q0.5=26397.9, q0.75=29216.7, q0.95=33834.1, q0.99=34117.5
- `NDXP\|year_2020\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|year_2020\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|last\|all\|all` `oi_mass`: q0.01=19653.7, q0.05=19768.2, q0.25=21634.5, q0.5=23715.5, q0.75=24534, q0.95=27462.2, q0.99=29099.6
- `NDXP\|year_2020\|last\|all\|all` `oi_width`: q0.01=2959, q0.05=2995, q0.25=3057, q0.5=3328, q0.75=3530.5, q0.95=3902, q0.99=3969.2
- `NDXP\|year_2020\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|last\|all\|all` `common_support_first`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|year_2020\|last\|all\|all` `common_support_last`: q0.01=5.67315, q0.05=5.97556, q0.25=6.48208, q0.5=7.1319, q0.75=7.43193, q0.95=8.04611, q0.99=8.1044
- `NDXP\|year_2020\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|last\|all\|all` `next_delta`: q0.01=0.283879, q0.05=0.475354, q0.25=0.685583, q0.5=0.853093, q0.75=1.05547, q0.95=1.53982, q0.99=1.73029
- `NDXP\|year_2020\|last\|all\|all` `next_abs_delta`: q0.01=0.766088, q0.05=0.866377, q0.25=1.15431, q0.5=1.56457, q0.75=1.91176, q0.95=2.39909, q0.99=2.45731
- `NDXP\|year_2020\|last\|all\|all` `next_positive_fraction`: q0.01=0.115488, q0.05=0.115812, q0.25=0.120149, q0.5=0.129702, q0.75=0.13381, q0.95=0.144833, q0.99=0.149911
- `NDXP\|year_2020\|last\|all\|all` `next_zero_fraction`: q0.01=0.804288, q0.05=0.80815, q0.25=0.821363, q0.5=0.836608, q0.75=0.856637, q0.95=0.864307, q0.99=0.869769
- `NDXP\|year_2020\|last\|all\|all` `next_negative_fraction`: q0.01=0.013627, q0.05=0.0142978, q0.25=0.0207551, q0.5=0.0256696, q0.75=0.0482082, q0.95=0.0620882, q0.99=0.0658396
- `NDXP\|year_2020\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0957404, q0.95=0.109634, q0.99=0.113275
- `NDXP\|year_2020\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|year_2020\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00503, q0.5=0.0206004, q0.75=0.0730222, q0.95=0.154165, q0.99=0.159579
- `NDXP\|year_2020\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDXP\|year_2020\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0238634, q0.75=0.0830338, q0.95=0.179957, q0.99=0.185904
- `NDXP\|year_2020\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|year_2020\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|year_2020\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|year_2020\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDXP\|year_2020\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.794695, q0.05=0.814337, q0.25=0.914245, q0.5=0.974607, q0.75=0.99444, q0.95=1, q0.99=1
- `NDXP\|year_2020\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDXP\|year_2020\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00556033, q0.5=0.0253928, q0.75=0.0857548, q0.95=0.185663, q0.99=0.205305
- `NDX\|all_period\|first\|CALL\|all` `oi_level_date_mean`: q0.01=11.6465, q0.05=12.1356, q0.25=12.8559, q0.5=13.7484, q0.75=14.3678, q0.95=14.6376, q0.99=14.8504
- `NDX\|all_period\|first\|CALL\|all` `oi_mass`: q0.01=22122.8, q0.05=22446.2, q0.25=23740, q0.5=25192, q0.75=27109.8, q0.95=29863, q0.99=30019
- `NDX\|all_period\|first\|CALL\|all` `oi_width`: q0.01=1726.8, q0.05=1770, q0.25=1830, q0.5=1856, q0.75=1896.5, q0.95=2066, q0.99=2066
- `NDX\|all_period\|first\|PUT\|all` `oi_level_date_mean`: q0.01=18.2218, q0.05=18.4444, q0.25=19.8077, q0.5=21.1591, q0.75=22.9205, q0.95=24.6318, q0.99=24.7842
- `NDX\|all_period\|first\|PUT\|all` `oi_mass`: q0.01=32905.7, q0.05=33144.5, q0.25=36248, q0.5=39271.5, q0.75=43781.2, q0.95=50889.2, q0.99=51204.2
- `NDX\|all_period\|first\|PUT\|all` `oi_width`: q0.01=1726.8, q0.05=1770, q0.25=1830, q0.5=1856, q0.75=1896.5, q0.95=2066, q0.99=2066
- `NDX\|all_period\|first\|all\|0` `oi_level_date_mean`: q0.01=46.9498, q0.05=46.9498, q0.25=46.9498, q0.5=46.9498, q0.75=46.9498, q0.95=46.9498, q0.99=46.9498
- `NDX\|all_period\|first\|all\|0` `oi_mass`: q0.01=26198, q0.05=26198, q0.25=26198, q0.5=26198, q0.75=26198, q0.95=26198, q0.99=26198
- `NDX\|all_period\|first\|all\|0` `oi_width`: q0.01=558, q0.05=558, q0.25=558, q0.5=558, q0.75=558, q0.95=558, q0.99=558
- `NDX\|all_period\|first\|all\|1` `oi_level_date_mean`: q0.01=45.6075, q0.05=45.6075, q0.25=45.6075, q0.5=45.6075, q0.75=45.6075, q0.95=45.6075, q0.99=45.6075
- `NDX\|all_period\|first\|all\|1` `oi_mass`: q0.01=25449, q0.05=25449, q0.25=25449, q0.5=25449, q0.75=25449, q0.95=25449, q0.99=25449
- `NDX\|all_period\|first\|all\|1` `oi_width`: q0.01=558, q0.05=558, q0.25=558, q0.5=558, q0.75=558, q0.95=558, q0.99=558
- `NDX\|all_period\|first\|all\|2-7` `oi_level_date_mean`: q0.01=40.5541, q0.05=40.5642, q0.25=40.615, q0.5=41.1565, q0.75=41.8768, q0.95=42.3567, q0.99=42.4527
- `NDX\|all_period\|first\|all\|2-7` `oi_mass`: q0.01=21269.2, q0.05=21350, q0.25=21753.8, q0.5=22298.5, q0.75=22931.8, q0.95=23548, q0.99=23671.2
- `NDX\|all_period\|first\|all\|2-7` `oi_width`: q0.01=524.06, q0.05=524.3, q0.25=525.5, q0.5=542, q0.75=558, q0.95=558, q0.99=558
- `NDX\|all_period\|first\|all\|31-60` `oi_level_date_mean`: q0.01=21.5522, q0.05=21.903, q0.25=24.7459, q0.5=31.4348, q0.75=39.4748, q0.95=64.682, q0.99=73.4308
- `NDX\|all_period\|first\|all\|31-60` `oi_mass`: q0.01=7439.5, q0.05=7733.5, q0.25=8621.75, q0.5=11570.5, q0.75=17176, q0.95=29699.8, q0.99=37110.3
- `NDX\|all_period\|first\|all\|31-60` `oi_width`: q0.01=242.1, q0.05=298.5, q0.25=366, q0.5=366, q0.75=434.5, q0.95=544.5, q0.99=737.7
- `NDX\|all_period\|first\|all\|61+` `oi_level_date_mean`: q0.01=6.92078, q0.05=7.11181, q0.25=9.48765, q0.5=11.0887, q0.75=12.4234, q0.95=12.8437, q0.99=12.9292
- `NDX\|all_period\|first\|all\|61+` `oi_mass`: q0.01=19297.3, q0.05=19838.5, q0.25=26114.2, q0.5=30826.5, q0.75=35852, q0.95=38867, q0.99=39639.8
- `NDX\|all_period\|first\|all\|61+` `oi_width`: q0.01=2703.5, q0.05=2757.5, q0.25=2780, q0.5=2793, q0.75=2868, q0.95=3107, q0.99=3109.4
- `NDX\|all_period\|first\|all\|8-30` `oi_level_date_mean`: q0.01=37.2234, q0.05=37.2251, q0.25=37.8237, q0.5=38.2451, q0.75=39.6304, q0.95=40.6518, q0.99=40.6704
- `NDX\|all_period\|first\|all\|8-30` `oi_mass`: q0.01=17321.4, q0.05=17511.2, q0.25=18231, q0.5=19658, q0.75=20370, q0.95=20895, q0.99=20904.6
- `NDX\|all_period\|first\|all\|8-30` `oi_width`: q0.01=465.28, q0.05=470.4, q0.25=482, q0.5=514, q0.75=514, q0.95=514, q0.99=514
- `NDX\|all_period\|first\|all\|all` `oi_level_date_mean`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|all_period\|first\|all\|all` `oi_zero_fraction`: q0.01=0.493678, q0.05=0.500002, q0.25=0.519749, q0.5=0.537536, q0.75=0.55123, q0.95=0.559768, q0.99=0.565505
- `NDX\|all_period\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25311.8, q0.75=25867.6, q0.95=28444.7, q0.99=28962.9
- `NDX\|all_period\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|first\|all\|all` `oi_mass`: q0.01=55028.6, q0.05=55590.8, q0.25=60500.2, q0.5=64966, q0.75=71504.2, q0.95=78908.8, q0.99=80434.6
- `NDX\|all_period\|first\|all\|all` `oi_width`: q0.01=3453.6, q0.05=3540, q0.25=3660, q0.5=3712, q0.75=3793, q0.95=4132, q0.99=4132
- `NDX\|all_period\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|first\|all\|all` `common_support_first`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|all_period\|first\|all\|all` `common_support_last`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|all_period\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|first\|all\|all` `next_delta`: q0.01=-1.15382, q0.05=-0.227963, q0.25=0.291635, q0.5=0.596448, q0.75=0.837939, q0.95=1.15296, q0.99=1.25901
- `NDX\|all_period\|first\|all\|all` `next_abs_delta`: q0.01=0.414767, q0.05=0.437176, q0.25=0.582767, q0.5=0.832088, q0.75=1.35942, q0.95=2.06376, q0.99=3.0083
- `NDX\|all_period\|first\|all\|all` `next_positive_fraction`: q0.01=0.0513152, q0.05=0.0513483, q0.25=0.0581372, q0.5=0.0608974, q0.75=0.0655266, q0.95=0.0765274, q0.99=0.0778587
- `NDX\|all_period\|first\|all\|all` `next_zero_fraction`: q0.01=0.888557, q0.05=0.895835, q0.25=0.911575, q0.5=0.919463, q0.75=0.925531, q0.95=0.936431, q0.99=0.937013
- `NDX\|all_period\|first\|all\|all` `next_negative_fraction`: q0.01=0.0115292, q0.05=0.0117445, q0.25=0.0142313, q0.5=0.0190157, q0.75=0.0218173, q0.95=0.036756, q0.99=0.0569156
- `NDX\|all_period\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0404935, q0.99=0.116081
- `NDX\|all_period\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00105374, q0.75=0.0156983, q0.95=0.0677345, q0.99=0.077888
- `NDX\|all_period\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|all_period\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|all_period\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|all_period\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|all_period\|first\|all\|expired` `oi_level_date_mean`: q0.01=30.4068, q0.05=30.4068, q0.25=30.4068, q0.5=30.4068, q0.75=30.4068, q0.95=30.4068, q0.99=30.4068
- `NDX\|all_period\|first\|all\|expired` `oi_mass`: q0.01=16967, q0.05=16967, q0.25=16967, q0.5=16967, q0.75=16967, q0.95=16967, q0.99=16967
- `NDX\|all_period\|first\|all\|expired` `oi_width`: q0.01=558, q0.05=558, q0.25=558, q0.5=558, q0.75=558, q0.95=558, q0.99=558
- `NDX\|all_period\|last\|CALL\|all` `oi_level_date_mean`: q0.01=11.6465, q0.05=12.1356, q0.25=12.8559, q0.5=13.7484, q0.75=14.3678, q0.95=14.6376, q0.99=14.8504
- `NDX\|all_period\|last\|CALL\|all` `oi_mass`: q0.01=22122.8, q0.05=22446.2, q0.25=23740, q0.5=25192, q0.75=27109.8, q0.95=29863, q0.99=30019
- `NDX\|all_period\|last\|CALL\|all` `oi_width`: q0.01=1726.8, q0.05=1770, q0.25=1830, q0.5=1856, q0.75=1896.5, q0.95=2066, q0.99=2066
- `NDX\|all_period\|last\|PUT\|all` `oi_level_date_mean`: q0.01=18.2218, q0.05=18.4444, q0.25=19.8077, q0.5=21.1591, q0.75=22.9205, q0.95=24.6318, q0.99=24.7842
- `NDX\|all_period\|last\|PUT\|all` `oi_mass`: q0.01=32905.7, q0.05=33144.5, q0.25=36248, q0.5=39271.5, q0.75=43781.2, q0.95=50889.2, q0.99=51204.2
- `NDX\|all_period\|last\|PUT\|all` `oi_width`: q0.01=1726.8, q0.05=1770, q0.25=1830, q0.5=1856, q0.75=1896.5, q0.95=2066, q0.99=2066
- `NDX\|all_period\|last\|all\|0` `oi_level_date_mean`: q0.01=46.9498, q0.05=46.9498, q0.25=46.9498, q0.5=46.9498, q0.75=46.9498, q0.95=46.9498, q0.99=46.9498
- `NDX\|all_period\|last\|all\|0` `oi_mass`: q0.01=26198, q0.05=26198, q0.25=26198, q0.5=26198, q0.75=26198, q0.95=26198, q0.99=26198
- `NDX\|all_period\|last\|all\|0` `oi_width`: q0.01=558, q0.05=558, q0.25=558, q0.5=558, q0.75=558, q0.95=558, q0.99=558
- `NDX\|all_period\|last\|all\|1` `oi_level_date_mean`: q0.01=45.6075, q0.05=45.6075, q0.25=45.6075, q0.5=45.6075, q0.75=45.6075, q0.95=45.6075, q0.99=45.6075
- `NDX\|all_period\|last\|all\|1` `oi_mass`: q0.01=25449, q0.05=25449, q0.25=25449, q0.5=25449, q0.75=25449, q0.95=25449, q0.99=25449
- `NDX\|all_period\|last\|all\|1` `oi_width`: q0.01=558, q0.05=558, q0.25=558, q0.5=558, q0.75=558, q0.95=558, q0.99=558
- `NDX\|all_period\|last\|all\|2-7` `oi_level_date_mean`: q0.01=40.5541, q0.05=40.5642, q0.25=40.615, q0.5=41.1565, q0.75=41.8768, q0.95=42.3567, q0.99=42.4527
- `NDX\|all_period\|last\|all\|2-7` `oi_mass`: q0.01=21269.2, q0.05=21350, q0.25=21753.8, q0.5=22298.5, q0.75=22931.8, q0.95=23548, q0.99=23671.2
- `NDX\|all_period\|last\|all\|2-7` `oi_width`: q0.01=524.06, q0.05=524.3, q0.25=525.5, q0.5=542, q0.75=558, q0.95=558, q0.99=558
- `NDX\|all_period\|last\|all\|31-60` `oi_level_date_mean`: q0.01=21.5522, q0.05=21.903, q0.25=24.7459, q0.5=31.4348, q0.75=39.4748, q0.95=64.682, q0.99=73.4308
- `NDX\|all_period\|last\|all\|31-60` `oi_mass`: q0.01=7439.5, q0.05=7733.5, q0.25=8621.75, q0.5=11570.5, q0.75=17176, q0.95=29699.8, q0.99=37110.3
- `NDX\|all_period\|last\|all\|31-60` `oi_width`: q0.01=242.1, q0.05=298.5, q0.25=366, q0.5=366, q0.75=434.5, q0.95=544.5, q0.99=737.7
- `NDX\|all_period\|last\|all\|61+` `oi_level_date_mean`: q0.01=6.92078, q0.05=7.11181, q0.25=9.48765, q0.5=11.0887, q0.75=12.4234, q0.95=12.8437, q0.99=12.9292
- `NDX\|all_period\|last\|all\|61+` `oi_mass`: q0.01=19297.3, q0.05=19838.5, q0.25=26114.2, q0.5=30826.5, q0.75=35852, q0.95=38867, q0.99=39639.8
- `NDX\|all_period\|last\|all\|61+` `oi_width`: q0.01=2703.5, q0.05=2757.5, q0.25=2780, q0.5=2793, q0.75=2868, q0.95=3107, q0.99=3109.4
- `NDX\|all_period\|last\|all\|8-30` `oi_level_date_mean`: q0.01=37.2234, q0.05=37.2251, q0.25=37.8237, q0.5=38.2451, q0.75=39.6304, q0.95=40.6518, q0.99=40.6704
- `NDX\|all_period\|last\|all\|8-30` `oi_mass`: q0.01=17321.4, q0.05=17511.2, q0.25=18231, q0.5=19658, q0.75=20370, q0.95=20895, q0.99=20904.6
- `NDX\|all_period\|last\|all\|8-30` `oi_width`: q0.01=465.28, q0.05=470.4, q0.25=482, q0.5=514, q0.75=514, q0.95=514, q0.99=514
- `NDX\|all_period\|last\|all\|all` `oi_level_date_mean`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|all_period\|last\|all\|all` `oi_zero_fraction`: q0.01=0.493678, q0.05=0.500002, q0.25=0.519749, q0.5=0.537536, q0.75=0.55123, q0.95=0.559768, q0.99=0.565505
- `NDX\|all_period\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25311.8, q0.75=25867.6, q0.95=28444.7, q0.99=28962.9
- `NDX\|all_period\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|last\|all\|all` `oi_mass`: q0.01=55028.6, q0.05=55590.8, q0.25=60500.2, q0.5=64966, q0.75=71504.2, q0.95=78908.8, q0.99=80434.6
- `NDX\|all_period\|last\|all\|all` `oi_width`: q0.01=3453.6, q0.05=3540, q0.25=3660, q0.5=3712, q0.75=3793, q0.95=4132, q0.99=4132
- `NDX\|all_period\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|last\|all\|all` `common_support_first`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|all_period\|last\|all\|all` `common_support_last`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|all_period\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|last\|all\|all` `next_delta`: q0.01=-1.15382, q0.05=-0.227963, q0.25=0.291635, q0.5=0.596448, q0.75=0.837939, q0.95=1.15296, q0.99=1.25901
- `NDX\|all_period\|last\|all\|all` `next_abs_delta`: q0.01=0.414767, q0.05=0.437176, q0.25=0.582767, q0.5=0.832088, q0.75=1.35942, q0.95=2.06376, q0.99=3.0083
- `NDX\|all_period\|last\|all\|all` `next_positive_fraction`: q0.01=0.0513152, q0.05=0.0513483, q0.25=0.0581372, q0.5=0.0608974, q0.75=0.0655266, q0.95=0.0765274, q0.99=0.0778587
- `NDX\|all_period\|last\|all\|all` `next_zero_fraction`: q0.01=0.888557, q0.05=0.895835, q0.25=0.911575, q0.5=0.919463, q0.75=0.925531, q0.95=0.936431, q0.99=0.937013
- `NDX\|all_period\|last\|all\|all` `next_negative_fraction`: q0.01=0.0115292, q0.05=0.0117445, q0.25=0.0142313, q0.5=0.0190157, q0.75=0.0218173, q0.95=0.036756, q0.99=0.0569156
- `NDX\|all_period\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0404935, q0.99=0.116081
- `NDX\|all_period\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00105374, q0.75=0.0156983, q0.95=0.0677345, q0.99=0.077888
- `NDX\|all_period\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|all_period\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|all_period\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|all_period\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|all_period\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|all_period\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|all_period\|last\|all\|expired` `oi_level_date_mean`: q0.01=30.4068, q0.05=30.4068, q0.25=30.4068, q0.5=30.4068, q0.75=30.4068, q0.95=30.4068, q0.99=30.4068
- `NDX\|all_period\|last\|all\|expired` `oi_mass`: q0.01=16967, q0.05=16967, q0.25=16967, q0.5=16967, q0.75=16967, q0.95=16967, q0.99=16967
- `NDX\|all_period\|last\|all\|expired` `oi_width`: q0.01=558, q0.05=558, q0.25=558, q0.5=558, q0.75=558, q0.95=558, q0.99=558
- `NDX\|stage_confirmation\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `NDX\|stage_confirmation\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `NDX\|stage_development\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `NDX\|stage_development\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `NDX\|stage_training\|first\|all\|all` `oi_level_date_mean`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|stage_training\|first\|all\|all` `oi_zero_fraction`: q0.01=0.493678, q0.05=0.500002, q0.25=0.519749, q0.5=0.537536, q0.75=0.55123, q0.95=0.559768, q0.99=0.565505
- `NDX\|stage_training\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25311.8, q0.75=25867.6, q0.95=28444.7, q0.99=28962.9
- `NDX\|stage_training\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|first\|all\|all` `oi_mass`: q0.01=55028.6, q0.05=55590.8, q0.25=60500.2, q0.5=64966, q0.75=71504.2, q0.95=78908.8, q0.99=80434.6
- `NDX\|stage_training\|first\|all\|all` `oi_width`: q0.01=3453.6, q0.05=3540, q0.25=3660, q0.5=3712, q0.75=3793, q0.95=4132, q0.99=4132
- `NDX\|stage_training\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|first\|all\|all` `common_support_first`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|stage_training\|first\|all\|all` `common_support_last`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|stage_training\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|first\|all\|all` `next_delta`: q0.01=-1.15382, q0.05=-0.227963, q0.25=0.291635, q0.5=0.596448, q0.75=0.837939, q0.95=1.15296, q0.99=1.25901
- `NDX\|stage_training\|first\|all\|all` `next_abs_delta`: q0.01=0.414767, q0.05=0.437176, q0.25=0.582767, q0.5=0.832088, q0.75=1.35942, q0.95=2.06376, q0.99=3.0083
- `NDX\|stage_training\|first\|all\|all` `next_positive_fraction`: q0.01=0.0513152, q0.05=0.0513483, q0.25=0.0581372, q0.5=0.0608974, q0.75=0.0655266, q0.95=0.0765274, q0.99=0.0778587
- `NDX\|stage_training\|first\|all\|all` `next_zero_fraction`: q0.01=0.888557, q0.05=0.895835, q0.25=0.911575, q0.5=0.919463, q0.75=0.925531, q0.95=0.936431, q0.99=0.937013
- `NDX\|stage_training\|first\|all\|all` `next_negative_fraction`: q0.01=0.0115292, q0.05=0.0117445, q0.25=0.0142313, q0.5=0.0190157, q0.75=0.0218173, q0.95=0.036756, q0.99=0.0569156
- `NDX\|stage_training\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0404935, q0.99=0.116081
- `NDX\|stage_training\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00105374, q0.75=0.0156983, q0.95=0.0677345, q0.99=0.077888
- `NDX\|stage_training\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|stage_training\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|stage_training\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|stage_training\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|stage_training\|last\|all\|all` `oi_level_date_mean`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|stage_training\|last\|all\|all` `oi_zero_fraction`: q0.01=0.493678, q0.05=0.500002, q0.25=0.519749, q0.5=0.537536, q0.75=0.55123, q0.95=0.559768, q0.99=0.565505
- `NDX\|stage_training\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25311.8, q0.75=25867.6, q0.95=28444.7, q0.99=28962.9
- `NDX\|stage_training\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|last\|all\|all` `oi_mass`: q0.01=55028.6, q0.05=55590.8, q0.25=60500.2, q0.5=64966, q0.75=71504.2, q0.95=78908.8, q0.99=80434.6
- `NDX\|stage_training\|last\|all\|all` `oi_width`: q0.01=3453.6, q0.05=3540, q0.25=3660, q0.5=3712, q0.75=3793, q0.95=4132, q0.99=4132
- `NDX\|stage_training\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|last\|all\|all` `common_support_first`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|stage_training\|last\|all\|all` `common_support_last`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|stage_training\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|last\|all\|all` `next_delta`: q0.01=-1.15382, q0.05=-0.227963, q0.25=0.291635, q0.5=0.596448, q0.75=0.837939, q0.95=1.15296, q0.99=1.25901
- `NDX\|stage_training\|last\|all\|all` `next_abs_delta`: q0.01=0.414767, q0.05=0.437176, q0.25=0.582767, q0.5=0.832088, q0.75=1.35942, q0.95=2.06376, q0.99=3.0083
- `NDX\|stage_training\|last\|all\|all` `next_positive_fraction`: q0.01=0.0513152, q0.05=0.0513483, q0.25=0.0581372, q0.5=0.0608974, q0.75=0.0655266, q0.95=0.0765274, q0.99=0.0778587
- `NDX\|stage_training\|last\|all\|all` `next_zero_fraction`: q0.01=0.888557, q0.05=0.895835, q0.25=0.911575, q0.5=0.919463, q0.75=0.925531, q0.95=0.936431, q0.99=0.937013
- `NDX\|stage_training\|last\|all\|all` `next_negative_fraction`: q0.01=0.0115292, q0.05=0.0117445, q0.25=0.0142313, q0.5=0.0190157, q0.75=0.0218173, q0.95=0.036756, q0.99=0.0569156
- `NDX\|stage_training\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0404935, q0.99=0.116081
- `NDX\|stage_training\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00105374, q0.75=0.0156983, q0.95=0.0677345, q0.99=0.077888
- `NDX\|stage_training\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|stage_training\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|stage_training\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|stage_training\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|stage_training\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|stage_training\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|year_2020\|first\|all\|all` `oi_level_date_mean`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|year_2020\|first\|all\|all` `oi_zero_fraction`: q0.01=0.493678, q0.05=0.500002, q0.25=0.519749, q0.5=0.537536, q0.75=0.55123, q0.95=0.559768, q0.99=0.565505
- `NDX\|year_2020\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25311.8, q0.75=25867.6, q0.95=28444.7, q0.99=28962.9
- `NDX\|year_2020\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|first\|all\|all` `oi_mass`: q0.01=55028.6, q0.05=55590.8, q0.25=60500.2, q0.5=64966, q0.75=71504.2, q0.95=78908.8, q0.99=80434.6
- `NDX\|year_2020\|first\|all\|all` `oi_width`: q0.01=3453.6, q0.05=3540, q0.25=3660, q0.5=3712, q0.75=3793, q0.95=4132, q0.99=4132
- `NDX\|year_2020\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|first\|all\|all` `common_support_first`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|year_2020\|first\|all\|all` `common_support_last`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|year_2020\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|first\|all\|all` `next_delta`: q0.01=-1.15382, q0.05=-0.227963, q0.25=0.291635, q0.5=0.596448, q0.75=0.837939, q0.95=1.15296, q0.99=1.25901
- `NDX\|year_2020\|first\|all\|all` `next_abs_delta`: q0.01=0.414767, q0.05=0.437176, q0.25=0.582767, q0.5=0.832088, q0.75=1.35942, q0.95=2.06376, q0.99=3.0083
- `NDX\|year_2020\|first\|all\|all` `next_positive_fraction`: q0.01=0.0513152, q0.05=0.0513483, q0.25=0.0581372, q0.5=0.0608974, q0.75=0.0655266, q0.95=0.0765274, q0.99=0.0778587
- `NDX\|year_2020\|first\|all\|all` `next_zero_fraction`: q0.01=0.888557, q0.05=0.895835, q0.25=0.911575, q0.5=0.919463, q0.75=0.925531, q0.95=0.936431, q0.99=0.937013
- `NDX\|year_2020\|first\|all\|all` `next_negative_fraction`: q0.01=0.0115292, q0.05=0.0117445, q0.25=0.0142313, q0.5=0.0190157, q0.75=0.0218173, q0.95=0.036756, q0.99=0.0569156
- `NDX\|year_2020\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0404935, q0.99=0.116081
- `NDX\|year_2020\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00105374, q0.75=0.0156983, q0.95=0.0677345, q0.99=0.077888
- `NDX\|year_2020\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|year_2020\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|year_2020\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|year_2020\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|year_2020\|last\|all\|all` `oi_level_date_mean`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|year_2020\|last\|all\|all` `oi_zero_fraction`: q0.01=0.493678, q0.05=0.500002, q0.25=0.519749, q0.5=0.537536, q0.75=0.55123, q0.95=0.559768, q0.99=0.565505
- `NDX\|year_2020\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25311.8, q0.75=25867.6, q0.95=28444.7, q0.99=28962.9
- `NDX\|year_2020\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|last\|all\|all` `oi_mass`: q0.01=55028.6, q0.05=55590.8, q0.25=60500.2, q0.5=64966, q0.75=71504.2, q0.95=78908.8, q0.99=80434.6
- `NDX\|year_2020\|last\|all\|all` `oi_width`: q0.01=3453.6, q0.05=3540, q0.25=3660, q0.5=3712, q0.75=3793, q0.95=4132, q0.99=4132
- `NDX\|year_2020\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|last\|all\|all` `common_support_first`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|year_2020\|last\|all\|all` `common_support_last`: q0.01=15.2945, q0.05=15.4617, q0.25=16.5301, q0.5=17.5015, q0.75=18.4235, q0.95=19.5324, q0.99=19.5533
- `NDX\|year_2020\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|last\|all\|all` `next_delta`: q0.01=-1.15382, q0.05=-0.227963, q0.25=0.291635, q0.5=0.596448, q0.75=0.837939, q0.95=1.15296, q0.99=1.25901
- `NDX\|year_2020\|last\|all\|all` `next_abs_delta`: q0.01=0.414767, q0.05=0.437176, q0.25=0.582767, q0.5=0.832088, q0.75=1.35942, q0.95=2.06376, q0.99=3.0083
- `NDX\|year_2020\|last\|all\|all` `next_positive_fraction`: q0.01=0.0513152, q0.05=0.0513483, q0.25=0.0581372, q0.5=0.0608974, q0.75=0.0655266, q0.95=0.0765274, q0.99=0.0778587
- `NDX\|year_2020\|last\|all\|all` `next_zero_fraction`: q0.01=0.888557, q0.05=0.895835, q0.25=0.911575, q0.5=0.919463, q0.75=0.925531, q0.95=0.936431, q0.99=0.937013
- `NDX\|year_2020\|last\|all\|all` `next_negative_fraction`: q0.01=0.0115292, q0.05=0.0117445, q0.25=0.0142313, q0.5=0.0190157, q0.75=0.0218173, q0.95=0.036756, q0.99=0.0569156
- `NDX\|year_2020\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0404935, q0.99=0.116081
- `NDX\|year_2020\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00105374, q0.75=0.0156983, q0.95=0.0677345, q0.99=0.077888
- `NDX\|year_2020\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|year_2020\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|year_2020\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `NDX\|year_2020\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.922293, q0.05=0.933172, q0.25=0.987268, q0.5=0.998935, q0.75=1, q0.95=1, q0.99=1
- `NDX\|year_2020\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `NDX\|year_2020\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00106537, q0.75=0.0127325, q0.95=0.0668279, q0.99=0.0777067
- `QQQ\|all_period\|first\|CALL\|all` `oi_level_date_mean`: q0.01=617.705, q0.05=633.941, q0.25=728.255, q0.5=795.151, q0.75=825.113, q0.95=866.932, q0.99=870.994
- `QQQ\|all_period\|first\|CALL\|all` `oi_mass`: q0.01=1.49672e+06, q0.05=1.50709e+06, q0.25=1.65899e+06, q0.5=1.72498e+06, q0.75=1.90882e+06, q0.95=2.07654e+06, q0.99=2.08349e+06
- `QQQ\|all_period\|first\|CALL\|all` `oi_width`: q0.01=2111, q0.05=2111, q0.25=2246.25, q0.5=2349.5, q0.75=2380, q0.95=2424.75, q0.99=2455.35
- `QQQ\|all_period\|first\|PUT\|all` `oi_level_date_mean`: q0.01=1509.16, q0.05=1514.41, q0.25=1672.5, q0.5=1802.33, q0.75=1905.55, q0.95=2015.25, q0.99=2025.62
- `QQQ\|all_period\|first\|PUT\|all` `oi_mass`: q0.01=3.53164e+06, q0.05=3.59304e+06, q0.25=3.75909e+06, q0.5=3.966e+06, q0.75=4.51649e+06, q0.95=4.88363e+06, q0.99=4.97313e+06
- `QQQ\|all_period\|first\|PUT\|all` `oi_width`: q0.01=2111, q0.05=2111, q0.25=2246.25, q0.5=2349.5, q0.75=2380, q0.95=2424.75, q0.99=2455.35
- `QQQ\|all_period\|first\|all\|0` `oi_level_date_mean`: q0.01=1063.12, q0.05=1211.84, q0.25=1955.43, q0.5=2365.53, q0.75=4008.47, q0.95=7710.85, q0.99=8451.33
- `QQQ\|all_period\|first\|all\|0` `oi_mass`: q0.01=264461, q0.05=279945, q0.25=357366, q0.5=421666, q0.75=992333, q0.95=2.28503e+06, q0.99=2.54357e+06
- `QQQ\|all_period\|first\|all\|0` `oi_width`: q0.01=172.36, q0.05=173.8, q0.25=181, q0.5=219, q0.75=266, q0.95=294.8, q0.99=300.56
- `QQQ\|all_period\|first\|all\|1` `oi_level_date_mean`: q0.01=948.755, q0.05=1106.44, q0.25=1894.85, q0.5=2245.3, q0.75=3851.8, q0.95=7654.71, q0.99=8415.29
- `QQQ\|all_period\|first\|all\|1` `oi_mass`: q0.01=235514, q0.05=253688, q0.25=344555, q0.5=399796, q0.75=962592, q0.95=2.27159e+06, q0.99=2.53339e+06
- `QQQ\|all_period\|first\|all\|1` `oi_width`: q0.01=172.36, q0.05=173.8, q0.25=181, q0.5=219, q0.75=266, q0.95=294.8, q0.99=300.56
- `QQQ\|all_period\|first\|all\|2-7` `oi_level_date_mean`: q0.01=1068.62, q0.05=1237.68, q0.25=1655.22, q0.5=1955.56, q0.75=8088.79, q0.95=8486.05, q0.99=8541.56
- `QQQ\|all_period\|first\|all\|2-7` `oi_mass`: q0.01=194764, q0.05=218423, q0.25=289074, q0.5=352378, q0.75=2.44281e+06, q0.95=2.56279e+06, q0.99=2.57955e+06
- `QQQ\|all_period\|first\|all\|2-7` `oi_width`: q0.01=172, q0.05=172, q0.25=181, q0.5=184, q0.75=302, q0.95=302, q0.99=302
- `QQQ\|all_period\|first\|all\|31-60` `oi_level_date_mean`: q0.01=937.785, q0.05=971.514, q0.25=1351.16, q0.5=1903.96, q0.75=2784.58, q0.95=3176.81, q0.99=3417
- `QQQ\|all_period\|first\|all\|31-60` `oi_mass`: q0.01=468200, q0.05=489727, q0.25=609720, q0.5=1.01471e+06, q0.75=1.1751e+06, q0.95=1.56819e+06, q0.99=2.17734e+06
- `QQQ\|all_period\|first\|all\|31-60` `oi_width`: q0.01=372.4, q0.05=382, q0.25=397.5, q0.5=499, q0.75=513, q0.95=577, q0.99=651.4
- `QQQ\|all_period\|first\|all\|61+` `oi_level_date_mean`: q0.01=409.766, q0.05=414.13, q0.25=565.405, q0.5=630.951, q0.75=649.738, q0.95=681.948, q0.99=683.467
- `QQQ\|all_period\|first\|all\|61+` `oi_mass`: q0.01=1.34079e+06, q0.05=1.36503e+06, q0.25=1.68285e+06, q0.5=1.88846e+06, q0.75=2.10387e+06, q0.95=2.31729e+06, q0.99=2.3454e+06
- `QQQ\|all_period\|first\|all\|61+` `oi_width`: q0.01=2900.3, q0.05=2925.5, q0.25=2936, q0.5=3258, q0.75=3328, q0.95=3398, q0.99=3431.6
- `QQQ\|all_period\|first\|all\|8-30` `oi_level_date_mean`: q0.01=959.277, q0.05=995.584, q0.25=1090.57, q0.5=2605.78, q0.75=3694.21, q0.95=4411.81, q0.99=4471.85
- `QQQ\|all_period\|first\|all\|8-30` `oi_mass`: q0.01=460453, q0.05=477880, q0.25=596460, q0.5=1.9311e+06, q0.75=2.62944e+06, q0.95=2.74391e+06, q0.99=2.77979e+06
- `QQQ\|all_period\|first\|all\|8-30` `oi_width`: q0.01=480, q0.05=480, q0.25=516, q0.5=614, q0.75=736.5, q0.95=791, q0.99=803
- `QQQ\|all_period\|first\|all\|all` `oi_level_date_mean`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|all_period\|first\|all\|all` `oi_zero_fraction`: q0.01=0.39608, q0.05=0.39665, q0.25=0.402946, q0.5=0.418051, q0.75=0.434339, q0.95=0.443168, q0.99=0.45208
- `QQQ\|all_period\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25498.3, q0.5=25834, q0.75=26374.6, q0.95=28075.3, q0.99=28162.4
- `QQQ\|all_period\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|all_period\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|first\|all\|all` `oi_mass`: q0.01=5.03484e+06, q0.05=5.13252e+06, q0.25=5.42166e+06, q0.5=5.72682e+06, q0.75=6.41719e+06, q0.95=6.81849e+06, q0.99=6.90895e+06
- `QQQ\|all_period\|first\|all\|all` `oi_width`: q0.01=4222, q0.05=4222, q0.25=4492.5, q0.5=4699, q0.75=4760, q0.95=4849.5, q0.99=4910.7
- `QQQ\|all_period\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|first\|all\|all` `common_support_first`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|all_period\|first\|all\|all` `common_support_last`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|all_period\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|first\|all\|all` `next_delta`: q0.01=-73.0456, q0.05=-12.8155, q0.25=33.3046, q0.5=40.9238, q0.75=62.3642, q0.95=81.4643, q0.99=93.3543
- `QQQ\|all_period\|first\|all\|all` `next_abs_delta`: q0.01=40.7402, q0.05=47.1855, q0.25=59.0732, q0.5=71.7331, q0.75=92.6814, q0.95=146.055, q0.99=205.72
- `QQQ\|all_period\|first\|all\|all` `next_positive_fraction`: q0.01=0.161134, q0.05=0.162371, q0.25=0.172024, q0.5=0.173282, q0.75=0.184455, q0.95=0.18932, q0.99=0.194556
- `QQQ\|all_period\|first\|all\|all` `next_zero_fraction`: q0.01=0.72398, q0.05=0.726953, q0.25=0.736867, q0.5=0.755575, q0.75=0.765836, q0.95=0.780341, q0.99=0.787238
- `QQQ\|all_period\|first\|all\|all` `next_negative_fraction`: q0.01=0.0502795, q0.05=0.0505448, q0.25=0.0627431, q0.5=0.0713979, q0.75=0.0753287, q0.95=0.0866649, q0.99=0.0895321
- `QQQ\|all_period\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0188912, q0.95=0.057967, q0.99=0.0602442
- `QQQ\|all_period\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|all_period\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00444312, q0.5=0.0107794, q0.75=0.0220752, q0.95=0.0533047, q0.99=0.0597494
- `QQQ\|all_period\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|all_period\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00498048, q0.5=0.0120287, q0.75=0.0233761, q0.95=0.0590738, q0.99=0.0609033
- `QQQ\|all_period\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|all_period\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|all_period\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|all_period\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|all_period\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|all_period\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|all_period\|first\|all\|expired` `oi_level_date_mean`: q0.01=867.093, q0.05=1004.33, q0.25=1690.53, q0.5=2005.81, q0.75=3133.93, q0.95=5770.92, q0.99=6298.31
- `QQQ\|all_period\|first\|all\|expired` `oi_mass`: q0.01=216091, q0.05=234348, q0.25=325630, q0.5=385351, q0.75=790755, q0.95=1.71168e+06, q0.99=1.89586e+06
- `QQQ\|all_period\|first\|all\|expired` `oi_width`: q0.01=184.48, q0.05=186.4, q0.25=196, q0.5=227, q0.75=266, q0.95=294.8, q0.99=300.56
- `QQQ\|all_period\|last\|CALL\|all` `oi_level_date_mean`: q0.01=617.705, q0.05=633.941, q0.25=728.255, q0.5=795.151, q0.75=825.113, q0.95=866.932, q0.99=870.994
- `QQQ\|all_period\|last\|CALL\|all` `oi_mass`: q0.01=1.49672e+06, q0.05=1.50709e+06, q0.25=1.65899e+06, q0.5=1.72498e+06, q0.75=1.90882e+06, q0.95=2.07654e+06, q0.99=2.08349e+06
- `QQQ\|all_period\|last\|CALL\|all` `oi_width`: q0.01=2111, q0.05=2111, q0.25=2246.25, q0.5=2349.5, q0.75=2380, q0.95=2424.75, q0.99=2455.35
- `QQQ\|all_period\|last\|PUT\|all` `oi_level_date_mean`: q0.01=1509.16, q0.05=1514.41, q0.25=1672.5, q0.5=1802.33, q0.75=1905.55, q0.95=2015.25, q0.99=2025.62
- `QQQ\|all_period\|last\|PUT\|all` `oi_mass`: q0.01=3.53164e+06, q0.05=3.59304e+06, q0.25=3.75909e+06, q0.5=3.966e+06, q0.75=4.51649e+06, q0.95=4.88363e+06, q0.99=4.97313e+06
- `QQQ\|all_period\|last\|PUT\|all` `oi_width`: q0.01=2111, q0.05=2111, q0.25=2246.25, q0.5=2349.5, q0.75=2380, q0.95=2424.75, q0.99=2455.35
- `QQQ\|all_period\|last\|all\|0` `oi_level_date_mean`: q0.01=1063.12, q0.05=1211.84, q0.25=1955.43, q0.5=2365.53, q0.75=4008.47, q0.95=7710.85, q0.99=8451.33
- `QQQ\|all_period\|last\|all\|0` `oi_mass`: q0.01=264461, q0.05=279945, q0.25=357366, q0.5=421666, q0.75=992333, q0.95=2.28503e+06, q0.99=2.54357e+06
- `QQQ\|all_period\|last\|all\|0` `oi_width`: q0.01=172.36, q0.05=173.8, q0.25=181, q0.5=219, q0.75=266, q0.95=294.8, q0.99=300.56
- `QQQ\|all_period\|last\|all\|1` `oi_level_date_mean`: q0.01=948.755, q0.05=1106.44, q0.25=1894.85, q0.5=2245.3, q0.75=3851.8, q0.95=7654.71, q0.99=8415.29
- `QQQ\|all_period\|last\|all\|1` `oi_mass`: q0.01=235514, q0.05=253688, q0.25=344555, q0.5=399796, q0.75=962592, q0.95=2.27159e+06, q0.99=2.53339e+06
- `QQQ\|all_period\|last\|all\|1` `oi_width`: q0.01=172.36, q0.05=173.8, q0.25=181, q0.5=219, q0.75=266, q0.95=294.8, q0.99=300.56
- `QQQ\|all_period\|last\|all\|2-7` `oi_level_date_mean`: q0.01=1068.62, q0.05=1237.68, q0.25=1655.22, q0.5=1955.56, q0.75=8088.79, q0.95=8486.05, q0.99=8541.56
- `QQQ\|all_period\|last\|all\|2-7` `oi_mass`: q0.01=194764, q0.05=218423, q0.25=289074, q0.5=352378, q0.75=2.44281e+06, q0.95=2.56279e+06, q0.99=2.57955e+06
- `QQQ\|all_period\|last\|all\|2-7` `oi_width`: q0.01=172, q0.05=172, q0.25=181, q0.5=184, q0.75=302, q0.95=302, q0.99=302
- `QQQ\|all_period\|last\|all\|31-60` `oi_level_date_mean`: q0.01=937.785, q0.05=971.514, q0.25=1351.16, q0.5=1903.96, q0.75=2784.58, q0.95=3176.81, q0.99=3417
- `QQQ\|all_period\|last\|all\|31-60` `oi_mass`: q0.01=468200, q0.05=489727, q0.25=609720, q0.5=1.01471e+06, q0.75=1.1751e+06, q0.95=1.56819e+06, q0.99=2.17734e+06
- `QQQ\|all_period\|last\|all\|31-60` `oi_width`: q0.01=372.4, q0.05=382, q0.25=397.5, q0.5=499, q0.75=513, q0.95=577, q0.99=651.4
- `QQQ\|all_period\|last\|all\|61+` `oi_level_date_mean`: q0.01=409.766, q0.05=414.13, q0.25=565.405, q0.5=630.951, q0.75=649.738, q0.95=681.948, q0.99=683.467
- `QQQ\|all_period\|last\|all\|61+` `oi_mass`: q0.01=1.34079e+06, q0.05=1.36503e+06, q0.25=1.68285e+06, q0.5=1.88846e+06, q0.75=2.10387e+06, q0.95=2.31729e+06, q0.99=2.3454e+06
- `QQQ\|all_period\|last\|all\|61+` `oi_width`: q0.01=2900.3, q0.05=2925.5, q0.25=2936, q0.5=3258, q0.75=3328, q0.95=3398, q0.99=3431.6
- `QQQ\|all_period\|last\|all\|8-30` `oi_level_date_mean`: q0.01=959.277, q0.05=995.584, q0.25=1090.57, q0.5=2605.78, q0.75=3694.21, q0.95=4411.81, q0.99=4471.85
- `QQQ\|all_period\|last\|all\|8-30` `oi_mass`: q0.01=460453, q0.05=477880, q0.25=596460, q0.5=1.9311e+06, q0.75=2.62944e+06, q0.95=2.74391e+06, q0.99=2.77979e+06
- `QQQ\|all_period\|last\|all\|8-30` `oi_width`: q0.01=480, q0.05=480, q0.25=516, q0.5=614, q0.75=736.5, q0.95=791, q0.99=803
- `QQQ\|all_period\|last\|all\|all` `oi_level_date_mean`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|all_period\|last\|all\|all` `oi_zero_fraction`: q0.01=0.39608, q0.05=0.39665, q0.25=0.402946, q0.5=0.418051, q0.75=0.434339, q0.95=0.443168, q0.99=0.45208
- `QQQ\|all_period\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25498.3, q0.5=25834, q0.75=26374.6, q0.95=28075.3, q0.99=28162.4
- `QQQ\|all_period\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|all_period\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|last\|all\|all` `oi_mass`: q0.01=5.03484e+06, q0.05=5.13252e+06, q0.25=5.42166e+06, q0.5=5.72682e+06, q0.75=6.41719e+06, q0.95=6.81849e+06, q0.99=6.90895e+06
- `QQQ\|all_period\|last\|all\|all` `oi_width`: q0.01=4222, q0.05=4222, q0.25=4492.5, q0.5=4699, q0.75=4760, q0.95=4849.5, q0.99=4910.7
- `QQQ\|all_period\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|last\|all\|all` `common_support_first`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|all_period\|last\|all\|all` `common_support_last`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|all_period\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|last\|all\|all` `next_delta`: q0.01=-73.0456, q0.05=-12.8155, q0.25=33.3046, q0.5=40.9238, q0.75=62.3642, q0.95=81.4643, q0.99=93.3543
- `QQQ\|all_period\|last\|all\|all` `next_abs_delta`: q0.01=40.7402, q0.05=47.1855, q0.25=59.0732, q0.5=71.7331, q0.75=92.6814, q0.95=146.055, q0.99=205.72
- `QQQ\|all_period\|last\|all\|all` `next_positive_fraction`: q0.01=0.161134, q0.05=0.162371, q0.25=0.172024, q0.5=0.173282, q0.75=0.184455, q0.95=0.18932, q0.99=0.194556
- `QQQ\|all_period\|last\|all\|all` `next_zero_fraction`: q0.01=0.72398, q0.05=0.726953, q0.25=0.736867, q0.5=0.755575, q0.75=0.765836, q0.95=0.780341, q0.99=0.787238
- `QQQ\|all_period\|last\|all\|all` `next_negative_fraction`: q0.01=0.0502795, q0.05=0.0505448, q0.25=0.0627431, q0.5=0.0713979, q0.75=0.0753287, q0.95=0.0866649, q0.99=0.0895321
- `QQQ\|all_period\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0188912, q0.95=0.057967, q0.99=0.0602442
- `QQQ\|all_period\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|all_period\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00444312, q0.5=0.0107794, q0.75=0.0220752, q0.95=0.0533047, q0.99=0.0597494
- `QQQ\|all_period\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|all_period\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00498048, q0.5=0.0120287, q0.75=0.0233761, q0.95=0.0590738, q0.99=0.0609033
- `QQQ\|all_period\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|all_period\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|all_period\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|all_period\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|all_period\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|all_period\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|all_period\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|all_period\|last\|all\|expired` `oi_level_date_mean`: q0.01=867.093, q0.05=1004.33, q0.25=1690.53, q0.5=2005.81, q0.75=3133.93, q0.95=5770.92, q0.99=6298.31
- `QQQ\|all_period\|last\|all\|expired` `oi_mass`: q0.01=216091, q0.05=234348, q0.25=325630, q0.5=385351, q0.75=790755, q0.95=1.71168e+06, q0.99=1.89586e+06
- `QQQ\|all_period\|last\|all\|expired` `oi_width`: q0.01=184.48, q0.05=186.4, q0.25=196, q0.5=227, q0.75=266, q0.95=294.8, q0.99=300.56
- `QQQ\|stage_confirmation\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `QQQ\|stage_confirmation\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `QQQ\|stage_development\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `QQQ\|stage_development\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `QQQ\|stage_training\|first\|all\|all` `oi_level_date_mean`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|stage_training\|first\|all\|all` `oi_zero_fraction`: q0.01=0.39608, q0.05=0.39665, q0.25=0.402946, q0.5=0.418051, q0.75=0.434339, q0.95=0.443168, q0.99=0.45208
- `QQQ\|stage_training\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25498.3, q0.5=25834, q0.75=26374.6, q0.95=28075.3, q0.99=28162.4
- `QQQ\|stage_training\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|stage_training\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|first\|all\|all` `oi_mass`: q0.01=5.03484e+06, q0.05=5.13252e+06, q0.25=5.42166e+06, q0.5=5.72682e+06, q0.75=6.41719e+06, q0.95=6.81849e+06, q0.99=6.90895e+06
- `QQQ\|stage_training\|first\|all\|all` `oi_width`: q0.01=4222, q0.05=4222, q0.25=4492.5, q0.5=4699, q0.75=4760, q0.95=4849.5, q0.99=4910.7
- `QQQ\|stage_training\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|first\|all\|all` `common_support_first`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|stage_training\|first\|all\|all` `common_support_last`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|stage_training\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|first\|all\|all` `next_delta`: q0.01=-73.0456, q0.05=-12.8155, q0.25=33.3046, q0.5=40.9238, q0.75=62.3642, q0.95=81.4643, q0.99=93.3543
- `QQQ\|stage_training\|first\|all\|all` `next_abs_delta`: q0.01=40.7402, q0.05=47.1855, q0.25=59.0732, q0.5=71.7331, q0.75=92.6814, q0.95=146.055, q0.99=205.72
- `QQQ\|stage_training\|first\|all\|all` `next_positive_fraction`: q0.01=0.161134, q0.05=0.162371, q0.25=0.172024, q0.5=0.173282, q0.75=0.184455, q0.95=0.18932, q0.99=0.194556
- `QQQ\|stage_training\|first\|all\|all` `next_zero_fraction`: q0.01=0.72398, q0.05=0.726953, q0.25=0.736867, q0.5=0.755575, q0.75=0.765836, q0.95=0.780341, q0.99=0.787238
- `QQQ\|stage_training\|first\|all\|all` `next_negative_fraction`: q0.01=0.0502795, q0.05=0.0505448, q0.25=0.0627431, q0.5=0.0713979, q0.75=0.0753287, q0.95=0.0866649, q0.99=0.0895321
- `QQQ\|stage_training\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0188912, q0.95=0.057967, q0.99=0.0602442
- `QQQ\|stage_training\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|stage_training\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00444312, q0.5=0.0107794, q0.75=0.0220752, q0.95=0.0533047, q0.99=0.0597494
- `QQQ\|stage_training\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|stage_training\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00498048, q0.5=0.0120287, q0.75=0.0233761, q0.95=0.0590738, q0.99=0.0609033
- `QQQ\|stage_training\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|stage_training\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|stage_training\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|stage_training\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|stage_training\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|stage_training\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|stage_training\|last\|all\|all` `oi_level_date_mean`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|stage_training\|last\|all\|all` `oi_zero_fraction`: q0.01=0.39608, q0.05=0.39665, q0.25=0.402946, q0.5=0.418051, q0.75=0.434339, q0.95=0.443168, q0.99=0.45208
- `QQQ\|stage_training\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25498.3, q0.5=25834, q0.75=26374.6, q0.95=28075.3, q0.99=28162.4
- `QQQ\|stage_training\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|stage_training\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|last\|all\|all` `oi_mass`: q0.01=5.03484e+06, q0.05=5.13252e+06, q0.25=5.42166e+06, q0.5=5.72682e+06, q0.75=6.41719e+06, q0.95=6.81849e+06, q0.99=6.90895e+06
- `QQQ\|stage_training\|last\|all\|all` `oi_width`: q0.01=4222, q0.05=4222, q0.25=4492.5, q0.5=4699, q0.75=4760, q0.95=4849.5, q0.99=4910.7
- `QQQ\|stage_training\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|last\|all\|all` `common_support_first`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|stage_training\|last\|all\|all` `common_support_last`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|stage_training\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|last\|all\|all` `next_delta`: q0.01=-73.0456, q0.05=-12.8155, q0.25=33.3046, q0.5=40.9238, q0.75=62.3642, q0.95=81.4643, q0.99=93.3543
- `QQQ\|stage_training\|last\|all\|all` `next_abs_delta`: q0.01=40.7402, q0.05=47.1855, q0.25=59.0732, q0.5=71.7331, q0.75=92.6814, q0.95=146.055, q0.99=205.72
- `QQQ\|stage_training\|last\|all\|all` `next_positive_fraction`: q0.01=0.161134, q0.05=0.162371, q0.25=0.172024, q0.5=0.173282, q0.75=0.184455, q0.95=0.18932, q0.99=0.194556
- `QQQ\|stage_training\|last\|all\|all` `next_zero_fraction`: q0.01=0.72398, q0.05=0.726953, q0.25=0.736867, q0.5=0.755575, q0.75=0.765836, q0.95=0.780341, q0.99=0.787238
- `QQQ\|stage_training\|last\|all\|all` `next_negative_fraction`: q0.01=0.0502795, q0.05=0.0505448, q0.25=0.0627431, q0.5=0.0713979, q0.75=0.0753287, q0.95=0.0866649, q0.99=0.0895321
- `QQQ\|stage_training\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0188912, q0.95=0.057967, q0.99=0.0602442
- `QQQ\|stage_training\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|stage_training\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00444312, q0.5=0.0107794, q0.75=0.0220752, q0.95=0.0533047, q0.99=0.0597494
- `QQQ\|stage_training\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|stage_training\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00498048, q0.5=0.0120287, q0.75=0.0233761, q0.95=0.0590738, q0.99=0.0609033
- `QQQ\|stage_training\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|stage_training\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|stage_training\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|stage_training\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|stage_training\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|stage_training\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|stage_training\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|year_2020\|first\|all\|all` `oi_level_date_mean`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|year_2020\|first\|all\|all` `oi_zero_fraction`: q0.01=0.39608, q0.05=0.39665, q0.25=0.402946, q0.5=0.418051, q0.75=0.434339, q0.95=0.443168, q0.99=0.45208
- `QQQ\|year_2020\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25498.3, q0.5=25834, q0.75=26374.6, q0.95=28075.3, q0.99=28162.4
- `QQQ\|year_2020\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|year_2020\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|first\|all\|all` `oi_mass`: q0.01=5.03484e+06, q0.05=5.13252e+06, q0.25=5.42166e+06, q0.5=5.72682e+06, q0.75=6.41719e+06, q0.95=6.81849e+06, q0.99=6.90895e+06
- `QQQ\|year_2020\|first\|all\|all` `oi_width`: q0.01=4222, q0.05=4222, q0.25=4492.5, q0.5=4699, q0.75=4760, q0.95=4849.5, q0.99=4910.7
- `QQQ\|year_2020\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|first\|all\|all` `common_support_first`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|year_2020\|first\|all\|all` `common_support_last`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|year_2020\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|first\|all\|all` `next_delta`: q0.01=-73.0456, q0.05=-12.8155, q0.25=33.3046, q0.5=40.9238, q0.75=62.3642, q0.95=81.4643, q0.99=93.3543
- `QQQ\|year_2020\|first\|all\|all` `next_abs_delta`: q0.01=40.7402, q0.05=47.1855, q0.25=59.0732, q0.5=71.7331, q0.75=92.6814, q0.95=146.055, q0.99=205.72
- `QQQ\|year_2020\|first\|all\|all` `next_positive_fraction`: q0.01=0.161134, q0.05=0.162371, q0.25=0.172024, q0.5=0.173282, q0.75=0.184455, q0.95=0.18932, q0.99=0.194556
- `QQQ\|year_2020\|first\|all\|all` `next_zero_fraction`: q0.01=0.72398, q0.05=0.726953, q0.25=0.736867, q0.5=0.755575, q0.75=0.765836, q0.95=0.780341, q0.99=0.787238
- `QQQ\|year_2020\|first\|all\|all` `next_negative_fraction`: q0.01=0.0502795, q0.05=0.0505448, q0.25=0.0627431, q0.5=0.0713979, q0.75=0.0753287, q0.95=0.0866649, q0.99=0.0895321
- `QQQ\|year_2020\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0188912, q0.95=0.057967, q0.99=0.0602442
- `QQQ\|year_2020\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|year_2020\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00444312, q0.5=0.0107794, q0.75=0.0220752, q0.95=0.0533047, q0.99=0.0597494
- `QQQ\|year_2020\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|year_2020\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00498048, q0.5=0.0120287, q0.75=0.0233761, q0.95=0.0590738, q0.99=0.0609033
- `QQQ\|year_2020\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|year_2020\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|year_2020\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|year_2020\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|year_2020\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|year_2020\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|year_2020\|last\|all\|all` `oi_level_date_mean`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|year_2020\|last\|all\|all` `oi_zero_fraction`: q0.01=0.39608, q0.05=0.39665, q0.25=0.402946, q0.5=0.418051, q0.75=0.434339, q0.95=0.443168, q0.99=0.45208
- `QQQ\|year_2020\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25498.3, q0.5=25834, q0.75=26374.6, q0.95=28075.3, q0.99=28162.4
- `QQQ\|year_2020\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|year_2020\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|last\|all\|all` `oi_mass`: q0.01=5.03484e+06, q0.05=5.13252e+06, q0.25=5.42166e+06, q0.5=5.72682e+06, q0.75=6.41719e+06, q0.95=6.81849e+06, q0.99=6.90895e+06
- `QQQ\|year_2020\|last\|all\|all` `oi_width`: q0.01=4222, q0.05=4222, q0.25=4492.5, q0.5=4699, q0.75=4760, q0.95=4849.5, q0.99=4910.7
- `QQQ\|year_2020\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|last\|all\|all` `common_support_first`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|year_2020\|last\|all\|all` `common_support_last`: q0.01=1075.74, q0.05=1081.63, q0.25=1211.27, q0.5=1301.12, q0.75=1348.17, q0.95=1428.82, q0.99=1436.23
- `QQQ\|year_2020\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|last\|all\|all` `next_delta`: q0.01=-73.0456, q0.05=-12.8155, q0.25=33.3046, q0.5=40.9238, q0.75=62.3642, q0.95=81.4643, q0.99=93.3543
- `QQQ\|year_2020\|last\|all\|all` `next_abs_delta`: q0.01=40.7402, q0.05=47.1855, q0.25=59.0732, q0.5=71.7331, q0.75=92.6814, q0.95=146.055, q0.99=205.72
- `QQQ\|year_2020\|last\|all\|all` `next_positive_fraction`: q0.01=0.161134, q0.05=0.162371, q0.25=0.172024, q0.5=0.173282, q0.75=0.184455, q0.95=0.18932, q0.99=0.194556
- `QQQ\|year_2020\|last\|all\|all` `next_zero_fraction`: q0.01=0.72398, q0.05=0.726953, q0.25=0.736867, q0.5=0.755575, q0.75=0.765836, q0.95=0.780341, q0.99=0.787238
- `QQQ\|year_2020\|last\|all\|all` `next_negative_fraction`: q0.01=0.0502795, q0.05=0.0505448, q0.25=0.0627431, q0.5=0.0713979, q0.75=0.0753287, q0.95=0.0866649, q0.99=0.0895321
- `QQQ\|year_2020\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0188912, q0.95=0.057967, q0.99=0.0602442
- `QQQ\|year_2020\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|year_2020\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0.00444312, q0.5=0.0107794, q0.75=0.0220752, q0.95=0.0533047, q0.99=0.0597494
- `QQQ\|year_2020\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `QQQ\|year_2020\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0.00498048, q0.5=0.0120287, q0.75=0.0233761, q0.95=0.0590738, q0.99=0.0609033
- `QQQ\|year_2020\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|year_2020\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|year_2020\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|year_2020\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `QQQ\|year_2020\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.938699, q0.05=0.938936, q0.25=0.976405, q0.5=0.987971, q0.75=0.994986, q0.95=1, q0.99=1
- `QQQ\|year_2020\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `QQQ\|year_2020\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0.00501441, q0.5=0.0120287, q0.75=0.023595, q0.95=0.0610635, q0.99=0.0613012
- `SPXW\|all_period\|first\|CALL\|all` `oi_level_date_mean`: q0.01=204.925, q0.05=207.826, q0.25=214.06, q0.5=223.862, q0.75=236.97, q0.95=245.833, q0.99=249.529
- `SPXW\|all_period\|first\|CALL\|all` `oi_mass`: q0.01=1.14044e+06, q0.05=1.15346e+06, q0.25=1.22615e+06, q0.5=1.26583e+06, q0.75=1.34769e+06, q0.95=1.40436e+06, q0.99=1.42294e+06
- `SPXW\|all_period\|first\|CALL\|all` `oi_width`: q0.01=5544.9, q0.05=5548.5, q0.25=5613.75, q0.5=5665, q0.75=5709.5, q0.95=5865.75, q0.99=5891.55
- `SPXW\|all_period\|first\|PUT\|all` `oi_level_date_mean`: q0.01=528.232, q0.05=553.442, q0.25=594.805, q0.5=624.721, q0.75=660.022, q0.95=689.55, q0.99=696.074
- `SPXW\|all_period\|first\|PUT\|all` `oi_mass`: q0.01=2.97641e+06, q0.05=3.09272e+06, q0.25=3.40466e+06, q0.5=3.56773e+06, q0.75=3.82281e+06, q0.95=3.93096e+06, q0.99=3.9694e+06
- `SPXW\|all_period\|first\|PUT\|all` `oi_width`: q0.01=5546.85, q0.05=5558.25, q0.25=5618.75, q0.5=5659.5, q0.75=5718.75, q0.95=5866.25, q0.99=5893.25
- `SPXW\|all_period\|first\|all\|0` `oi_level_date_mean`: q0.01=532.695, q0.05=548.189, q0.25=657.628, q0.5=754.962, q0.75=1277.24, q0.95=1625.49, q0.99=1707.56
- `SPXW\|all_period\|first\|all\|0` `oi_mass`: q0.01=175686, q0.05=180388, q0.25=215546, q0.5=260404, q0.75=617190, q0.95=711743, q0.99=731277
- `SPXW\|all_period\|first\|all\|0` `oi_width`: q0.01=324.36, q0.05=325.8, q0.25=331, q0.5=339, q0.75=435, q0.95=567.3, q0.99=627.06
- `SPXW\|all_period\|first\|all\|1` `oi_level_date_mean`: q0.01=590.97, q0.05=599.215, q0.25=636.563, q0.5=675.477, q0.75=1344.22, q0.95=1501.76, q0.99=1546.04
- `SPXW\|all_period\|first\|all\|1` `oi_mass`: q0.01=199299, q0.05=200291, q0.25=210119, q0.5=433656, q0.75=613768, q0.95=652233, q0.99=661111
- `SPXW\|all_period\|first\|all\|1` `oi_width`: q0.01=326.48, q0.05=328.4, q0.25=336, q0.5=426, q0.75=457, q0.95=592.2, q0.99=632.04
- `SPXW\|all_period\|first\|all\|2-7` `oi_level_date_mean`: q0.01=325.789, q0.05=359.402, q0.25=465.719, q0.5=572.161, q0.75=702.071, q0.95=929.129, q0.99=1156.76
- `SPXW\|all_period\|first\|all\|2-7` `oi_mass`: q0.01=213025, q0.05=229765, q0.25=422776, q0.5=612768, q0.75=694262, q0.95=940368, q0.99=1.28911e+06
- `SPXW\|all_period\|first\|all\|2-7` `oi_width`: q0.01=636.1, q0.05=644.5, q0.25=720.5, q0.5=1018, q0.75=1119, q0.95=1269, q0.99=1285.8
- `SPXW\|all_period\|first\|all\|31-60` `oi_level_date_mean`: q0.01=228.82, q0.05=230.671, q0.25=288.003, q0.5=302.414, q0.75=329.64, q0.95=356.746, q0.99=367.149
- `SPXW\|all_period\|first\|all\|31-60` `oi_mass`: q0.01=518253, q0.05=534226, q0.25=667583, q0.5=717052, q0.75=799899, q0.95=880158, q0.99=887625
- `SPXW\|all_period\|first\|all\|31-60` `oi_width`: q0.01=2232, q0.05=2232, q0.25=2285, q0.5=2368, q0.75=2407.25, q0.95=2544.25, q0.99=2652.85
- `SPXW\|all_period\|first\|all\|61+` `oi_level_date_mean`: q0.01=186.969, q0.05=192.495, q0.25=207.463, q0.5=230.126, q0.75=249.054, q0.95=262.514, q0.99=269.774
- `SPXW\|all_period\|first\|all\|61+` `oi_mass`: q0.01=754170, q0.05=760060, q0.25=802249, q0.5=906376, q0.75=970501, q0.95=1.02256e+06, q0.99=1.02302e+06
- `SPXW\|all_period\|first\|all\|61+` `oi_width`: q0.01=3442.1, q0.05=3642.5, q0.25=3842, q0.5=3937.5, q0.75=3987, q0.95=4211.75, q0.99=4215.95
- `SPXW\|all_period\|first\|all\|8-30` `oi_level_date_mean`: q0.01=411.16, q0.05=446.408, q0.25=491.249, q0.5=576.337, q0.75=619.347, q0.95=657.802, q0.99=671.735
- `SPXW\|all_period\|first\|all\|8-30` `oi_mass`: q0.01=1.36334e+06, q0.05=1.45098e+06, q0.25=1.74412e+06, q0.5=1.98332e+06, q0.75=2.09228e+06, q0.95=2.32042e+06, q0.99=2.32282e+06
- `SPXW\|all_period\|first\|all\|8-30` `oi_width`: q0.01=2983.7, q0.05=3054.5, q0.25=3311.5, q0.5=3429.5, q0.75=3597, q0.95=3748.5, q0.99=3768.9
- `SPXW\|all_period\|first\|all\|all` `oi_level_date_mean`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|all_period\|first\|all\|all` `oi_zero_fraction`: q0.01=0.382444, q0.05=0.3825, q0.25=0.395061, q0.5=0.40156, q0.75=0.411777, q0.95=0.41702, q0.99=0.417022
- `SPXW\|all_period\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25315.4, q0.75=25457.9, q0.95=25683.8, q0.99=25763.9
- `SPXW\|all_period\|first\|all\|all` `coverage_fraction`: q0.01=0.923865, q0.05=0.942469, q0.25=0.971046, q0.5=0.983111, q0.75=0.99231, q0.95=1, q0.99=1
- `SPXW\|all_period\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0.00768955, q0.5=0.0168893, q0.75=0.0289543, q0.95=0.057531, q0.99=0.0761347
- `SPXW\|all_period\|first\|all\|all` `oi_mass`: q0.01=4.15502e+06, q0.05=4.24209e+06, q0.25=4.63081e+06, q0.5=4.85395e+06, q0.75=5.11862e+06, q0.95=5.34331e+06, q0.99=5.34521e+06
- `SPXW\|all_period\|first\|all\|all` `oi_width`: q0.01=11091.8, q0.05=11106.8, q0.25=11238, q0.5=11324.5, q0.75=11431.8, q0.95=11732, q0.99=11784.8
- `SPXW\|all_period\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|first\|all\|all` `common_support_first`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|all_period\|first\|all\|all` `common_support_last`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|all_period\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|first\|all\|all` `next_delta`: q0.01=22.4355, q0.05=24.0902, q0.25=26.2029, q0.5=28.968, q0.75=31.6667, q0.95=33.8979, q0.99=34.6239
- `SPXW\|all_period\|first\|all\|all` `next_abs_delta`: q0.01=27.254, q0.05=29.0474, q0.25=33.801, q0.5=40.7456, q0.75=44.0669, q0.95=58.5021, q0.99=58.6113
- `SPXW\|all_period\|first\|all\|all` `next_positive_fraction`: q0.01=0.164462, q0.05=0.166008, q0.25=0.175159, q0.5=0.181666, q0.75=0.190208, q0.95=0.200752, q0.99=0.203478
- `SPXW\|all_period\|first\|all\|all` `next_zero_fraction`: q0.01=0.734606, q0.05=0.736948, q0.25=0.746464, q0.5=0.759722, q0.75=0.763798, q0.95=0.778857, q0.99=0.789009
- `SPXW\|all_period\|first\|all\|all` `next_negative_fraction`: q0.01=0.0424605, q0.05=0.0458365, q0.25=0.0578347, q0.5=0.0605104, q0.75=0.062725, q0.95=0.071128, q0.99=0.0735375
- `SPXW\|all_period\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0288354, q0.75=0.0332594, q0.95=0.0471983, q0.99=0.05102
- `SPXW\|all_period\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|all_period\|first\|all\|all` `first_observed_fraction`: q0.01=0.00130162, q0.05=0.00191892, q0.25=0.00834112, q0.5=0.0184613, q0.75=0.0345085, q0.95=0.05816, q0.99=0.0729014
- `SPXW\|all_period\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|all_period\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00114099, q0.75=0.00413381, q0.95=0.00887437, q0.99=0.0105567
- `SPXW\|all_period\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|all_period\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|all_period\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|all_period\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|all_period\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|all_period\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|all_period\|first\|all\|expired` `oi_level_date_mean`: q0.01=647.863, q0.05=664.758, q0.25=721.796, q0.5=845.827, q0.75=1272.41, q0.95=1984.2, q0.99=2251.56
- `SPXW\|all_period\|first\|all\|expired` `oi_mass`: q0.01=221941, q0.05=224057, q0.25=268699, q0.5=293468, q0.75=570546, q0.95=994326, q0.99=1.18928e+06
- `SPXW\|all_period\|first\|all\|expired` `oi_width`: q0.01=326.18, q0.05=326.9, q0.25=335, q0.5=342, q0.75=441, q0.95=593.4, q0.99=632.28
- `SPXW\|all_period\|last\|CALL\|all` `oi_level_date_mean`: q0.01=204.925, q0.05=207.826, q0.25=214.06, q0.5=223.862, q0.75=236.97, q0.95=245.833, q0.99=249.529
- `SPXW\|all_period\|last\|CALL\|all` `oi_mass`: q0.01=1.14044e+06, q0.05=1.15346e+06, q0.25=1.22615e+06, q0.5=1.26583e+06, q0.75=1.34769e+06, q0.95=1.40436e+06, q0.99=1.42294e+06
- `SPXW\|all_period\|last\|CALL\|all` `oi_width`: q0.01=5544.9, q0.05=5548.5, q0.25=5613.75, q0.5=5665, q0.75=5709.5, q0.95=5865.75, q0.99=5891.55
- `SPXW\|all_period\|last\|PUT\|all` `oi_level_date_mean`: q0.01=528.232, q0.05=553.442, q0.25=594.805, q0.5=624.721, q0.75=660.022, q0.95=689.55, q0.99=696.074
- `SPXW\|all_period\|last\|PUT\|all` `oi_mass`: q0.01=2.97641e+06, q0.05=3.09272e+06, q0.25=3.40466e+06, q0.5=3.56773e+06, q0.75=3.82281e+06, q0.95=3.93096e+06, q0.99=3.9694e+06
- `SPXW\|all_period\|last\|PUT\|all` `oi_width`: q0.01=5546.85, q0.05=5558.25, q0.25=5618.75, q0.5=5659.5, q0.75=5718.75, q0.95=5866.25, q0.99=5893.25
- `SPXW\|all_period\|last\|all\|0` `oi_level_date_mean`: q0.01=532.695, q0.05=548.189, q0.25=657.628, q0.5=754.962, q0.75=1277.24, q0.95=1625.49, q0.99=1707.56
- `SPXW\|all_period\|last\|all\|0` `oi_mass`: q0.01=175686, q0.05=180388, q0.25=215546, q0.5=260404, q0.75=617190, q0.95=711743, q0.99=731277
- `SPXW\|all_period\|last\|all\|0` `oi_width`: q0.01=324.36, q0.05=325.8, q0.25=331, q0.5=339, q0.75=435, q0.95=567.3, q0.99=627.06
- `SPXW\|all_period\|last\|all\|1` `oi_level_date_mean`: q0.01=590.97, q0.05=599.215, q0.25=636.563, q0.5=675.477, q0.75=1344.22, q0.95=1501.76, q0.99=1546.04
- `SPXW\|all_period\|last\|all\|1` `oi_mass`: q0.01=199299, q0.05=200291, q0.25=210119, q0.5=433656, q0.75=613768, q0.95=652233, q0.99=661111
- `SPXW\|all_period\|last\|all\|1` `oi_width`: q0.01=326.48, q0.05=328.4, q0.25=336, q0.5=426, q0.75=457, q0.95=592.2, q0.99=632.04
- `SPXW\|all_period\|last\|all\|2-7` `oi_level_date_mean`: q0.01=325.789, q0.05=359.402, q0.25=465.719, q0.5=572.161, q0.75=702.071, q0.95=929.129, q0.99=1156.76
- `SPXW\|all_period\|last\|all\|2-7` `oi_mass`: q0.01=213025, q0.05=229765, q0.25=422776, q0.5=612768, q0.75=694262, q0.95=940368, q0.99=1.28911e+06
- `SPXW\|all_period\|last\|all\|2-7` `oi_width`: q0.01=636.1, q0.05=644.5, q0.25=720.5, q0.5=1018, q0.75=1119, q0.95=1269, q0.99=1285.8
- `SPXW\|all_period\|last\|all\|31-60` `oi_level_date_mean`: q0.01=228.82, q0.05=230.671, q0.25=288.003, q0.5=302.414, q0.75=329.64, q0.95=356.746, q0.99=367.149
- `SPXW\|all_period\|last\|all\|31-60` `oi_mass`: q0.01=518253, q0.05=534226, q0.25=667583, q0.5=717052, q0.75=799899, q0.95=880158, q0.99=887625
- `SPXW\|all_period\|last\|all\|31-60` `oi_width`: q0.01=2232, q0.05=2232, q0.25=2285, q0.5=2368, q0.75=2407.25, q0.95=2544.25, q0.99=2652.85
- `SPXW\|all_period\|last\|all\|61+` `oi_level_date_mean`: q0.01=186.969, q0.05=192.495, q0.25=207.463, q0.5=230.126, q0.75=249.054, q0.95=262.514, q0.99=269.774
- `SPXW\|all_period\|last\|all\|61+` `oi_mass`: q0.01=754170, q0.05=760060, q0.25=802249, q0.5=906376, q0.75=970501, q0.95=1.02256e+06, q0.99=1.02302e+06
- `SPXW\|all_period\|last\|all\|61+` `oi_width`: q0.01=3442.1, q0.05=3642.5, q0.25=3842, q0.5=3937.5, q0.75=3987, q0.95=4211.75, q0.99=4215.95
- `SPXW\|all_period\|last\|all\|8-30` `oi_level_date_mean`: q0.01=411.16, q0.05=446.408, q0.25=491.249, q0.5=576.337, q0.75=619.347, q0.95=657.802, q0.99=671.735
- `SPXW\|all_period\|last\|all\|8-30` `oi_mass`: q0.01=1.36334e+06, q0.05=1.45098e+06, q0.25=1.74412e+06, q0.5=1.98332e+06, q0.75=2.09228e+06, q0.95=2.32042e+06, q0.99=2.32282e+06
- `SPXW\|all_period\|last\|all\|8-30` `oi_width`: q0.01=2983.7, q0.05=3054.5, q0.25=3311.5, q0.5=3429.5, q0.75=3597, q0.95=3748.5, q0.99=3768.9
- `SPXW\|all_period\|last\|all\|all` `oi_level_date_mean`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|all_period\|last\|all\|all` `oi_zero_fraction`: q0.01=0.382444, q0.05=0.3825, q0.25=0.395061, q0.5=0.40156, q0.75=0.411777, q0.95=0.41702, q0.99=0.417022
- `SPXW\|all_period\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25315.4, q0.75=25457.9, q0.95=25683.8, q0.99=25763.9
- `SPXW\|all_period\|last\|all\|all` `coverage_fraction`: q0.01=0.923865, q0.05=0.942469, q0.25=0.971046, q0.5=0.983111, q0.75=0.99231, q0.95=1, q0.99=1
- `SPXW\|all_period\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0.00768955, q0.5=0.0168893, q0.75=0.0289543, q0.95=0.057531, q0.99=0.0761347
- `SPXW\|all_period\|last\|all\|all` `oi_mass`: q0.01=4.15502e+06, q0.05=4.24209e+06, q0.25=4.63081e+06, q0.5=4.85395e+06, q0.75=5.11862e+06, q0.95=5.34331e+06, q0.99=5.34521e+06
- `SPXW\|all_period\|last\|all\|all` `oi_width`: q0.01=11091.8, q0.05=11106.8, q0.25=11238, q0.5=11324.5, q0.75=11431.8, q0.95=11732, q0.99=11784.8
- `SPXW\|all_period\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|last\|all\|all` `common_support_first`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|all_period\|last\|all\|all` `common_support_last`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|all_period\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|last\|all\|all` `next_delta`: q0.01=22.4355, q0.05=24.0902, q0.25=26.2029, q0.5=28.968, q0.75=31.6667, q0.95=33.8979, q0.99=34.6239
- `SPXW\|all_period\|last\|all\|all` `next_abs_delta`: q0.01=27.254, q0.05=29.0474, q0.25=33.801, q0.5=40.7456, q0.75=44.0669, q0.95=58.5021, q0.99=58.6113
- `SPXW\|all_period\|last\|all\|all` `next_positive_fraction`: q0.01=0.164462, q0.05=0.166008, q0.25=0.175159, q0.5=0.181666, q0.75=0.190208, q0.95=0.200752, q0.99=0.203478
- `SPXW\|all_period\|last\|all\|all` `next_zero_fraction`: q0.01=0.734606, q0.05=0.736948, q0.25=0.746464, q0.5=0.759722, q0.75=0.763798, q0.95=0.778857, q0.99=0.789009
- `SPXW\|all_period\|last\|all\|all` `next_negative_fraction`: q0.01=0.0424605, q0.05=0.0458365, q0.25=0.0578347, q0.5=0.0605104, q0.75=0.062725, q0.95=0.071128, q0.99=0.0735375
- `SPXW\|all_period\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0288354, q0.75=0.0332594, q0.95=0.0471983, q0.99=0.05102
- `SPXW\|all_period\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|all_period\|last\|all\|all` `first_observed_fraction`: q0.01=0.00130162, q0.05=0.00191892, q0.25=0.00834112, q0.5=0.0184613, q0.75=0.0345085, q0.95=0.05816, q0.99=0.0729014
- `SPXW\|all_period\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|all_period\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00114099, q0.75=0.00413381, q0.95=0.00887437, q0.99=0.0105567
- `SPXW\|all_period\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|all_period\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|all_period\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|all_period\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|all_period\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|all_period\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|all_period\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|all_period\|last\|all\|expired` `oi_level_date_mean`: q0.01=647.863, q0.05=664.758, q0.25=721.796, q0.5=845.827, q0.75=1272.41, q0.95=1984.2, q0.99=2251.56
- `SPXW\|all_period\|last\|all\|expired` `oi_mass`: q0.01=221941, q0.05=224057, q0.25=268699, q0.5=293468, q0.75=570546, q0.95=994326, q0.99=1.18928e+06
- `SPXW\|all_period\|last\|all\|expired` `oi_width`: q0.01=326.18, q0.05=326.9, q0.25=335, q0.5=342, q0.75=441, q0.95=593.4, q0.99=632.28
- `SPXW\|stage_confirmation\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `SPXW\|stage_confirmation\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `SPXW\|stage_development\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `SPXW\|stage_development\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `SPXW\|stage_training\|first\|all\|all` `oi_level_date_mean`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|stage_training\|first\|all\|all` `oi_zero_fraction`: q0.01=0.382444, q0.05=0.3825, q0.25=0.395061, q0.5=0.40156, q0.75=0.411777, q0.95=0.41702, q0.99=0.417022
- `SPXW\|stage_training\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25315.4, q0.75=25457.9, q0.95=25683.8, q0.99=25763.9
- `SPXW\|stage_training\|first\|all\|all` `coverage_fraction`: q0.01=0.923865, q0.05=0.942469, q0.25=0.971046, q0.5=0.983111, q0.75=0.99231, q0.95=1, q0.99=1
- `SPXW\|stage_training\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0.00768955, q0.5=0.0168893, q0.75=0.0289543, q0.95=0.057531, q0.99=0.0761347
- `SPXW\|stage_training\|first\|all\|all` `oi_mass`: q0.01=4.15502e+06, q0.05=4.24209e+06, q0.25=4.63081e+06, q0.5=4.85395e+06, q0.75=5.11862e+06, q0.95=5.34331e+06, q0.99=5.34521e+06
- `SPXW\|stage_training\|first\|all\|all` `oi_width`: q0.01=11091.8, q0.05=11106.8, q0.25=11238, q0.5=11324.5, q0.75=11431.8, q0.95=11732, q0.99=11784.8
- `SPXW\|stage_training\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|first\|all\|all` `common_support_first`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|stage_training\|first\|all\|all` `common_support_last`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|stage_training\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|first\|all\|all` `next_delta`: q0.01=22.4355, q0.05=24.0902, q0.25=26.2029, q0.5=28.968, q0.75=31.6667, q0.95=33.8979, q0.99=34.6239
- `SPXW\|stage_training\|first\|all\|all` `next_abs_delta`: q0.01=27.254, q0.05=29.0474, q0.25=33.801, q0.5=40.7456, q0.75=44.0669, q0.95=58.5021, q0.99=58.6113
- `SPXW\|stage_training\|first\|all\|all` `next_positive_fraction`: q0.01=0.164462, q0.05=0.166008, q0.25=0.175159, q0.5=0.181666, q0.75=0.190208, q0.95=0.200752, q0.99=0.203478
- `SPXW\|stage_training\|first\|all\|all` `next_zero_fraction`: q0.01=0.734606, q0.05=0.736948, q0.25=0.746464, q0.5=0.759722, q0.75=0.763798, q0.95=0.778857, q0.99=0.789009
- `SPXW\|stage_training\|first\|all\|all` `next_negative_fraction`: q0.01=0.0424605, q0.05=0.0458365, q0.25=0.0578347, q0.5=0.0605104, q0.75=0.062725, q0.95=0.071128, q0.99=0.0735375
- `SPXW\|stage_training\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0288354, q0.75=0.0332594, q0.95=0.0471983, q0.99=0.05102
- `SPXW\|stage_training\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|stage_training\|first\|all\|all` `first_observed_fraction`: q0.01=0.00130162, q0.05=0.00191892, q0.25=0.00834112, q0.5=0.0184613, q0.75=0.0345085, q0.95=0.05816, q0.99=0.0729014
- `SPXW\|stage_training\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|stage_training\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00114099, q0.75=0.00413381, q0.95=0.00887437, q0.99=0.0105567
- `SPXW\|stage_training\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|stage_training\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|stage_training\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|stage_training\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|stage_training\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|stage_training\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|stage_training\|last\|all\|all` `oi_level_date_mean`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|stage_training\|last\|all\|all` `oi_zero_fraction`: q0.01=0.382444, q0.05=0.3825, q0.25=0.395061, q0.5=0.40156, q0.75=0.411777, q0.95=0.41702, q0.99=0.417022
- `SPXW\|stage_training\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25315.4, q0.75=25457.9, q0.95=25683.8, q0.99=25763.9
- `SPXW\|stage_training\|last\|all\|all` `coverage_fraction`: q0.01=0.923865, q0.05=0.942469, q0.25=0.971046, q0.5=0.983111, q0.75=0.99231, q0.95=1, q0.99=1
- `SPXW\|stage_training\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0.00768955, q0.5=0.0168893, q0.75=0.0289543, q0.95=0.057531, q0.99=0.0761347
- `SPXW\|stage_training\|last\|all\|all` `oi_mass`: q0.01=4.15502e+06, q0.05=4.24209e+06, q0.25=4.63081e+06, q0.5=4.85395e+06, q0.75=5.11862e+06, q0.95=5.34331e+06, q0.99=5.34521e+06
- `SPXW\|stage_training\|last\|all\|all` `oi_width`: q0.01=11091.8, q0.05=11106.8, q0.25=11238, q0.5=11324.5, q0.75=11431.8, q0.95=11732, q0.99=11784.8
- `SPXW\|stage_training\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|last\|all\|all` `common_support_first`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|stage_training\|last\|all\|all` `common_support_last`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|stage_training\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|last\|all\|all` `next_delta`: q0.01=22.4355, q0.05=24.0902, q0.25=26.2029, q0.5=28.968, q0.75=31.6667, q0.95=33.8979, q0.99=34.6239
- `SPXW\|stage_training\|last\|all\|all` `next_abs_delta`: q0.01=27.254, q0.05=29.0474, q0.25=33.801, q0.5=40.7456, q0.75=44.0669, q0.95=58.5021, q0.99=58.6113
- `SPXW\|stage_training\|last\|all\|all` `next_positive_fraction`: q0.01=0.164462, q0.05=0.166008, q0.25=0.175159, q0.5=0.181666, q0.75=0.190208, q0.95=0.200752, q0.99=0.203478
- `SPXW\|stage_training\|last\|all\|all` `next_zero_fraction`: q0.01=0.734606, q0.05=0.736948, q0.25=0.746464, q0.5=0.759722, q0.75=0.763798, q0.95=0.778857, q0.99=0.789009
- `SPXW\|stage_training\|last\|all\|all` `next_negative_fraction`: q0.01=0.0424605, q0.05=0.0458365, q0.25=0.0578347, q0.5=0.0605104, q0.75=0.062725, q0.95=0.071128, q0.99=0.0735375
- `SPXW\|stage_training\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0288354, q0.75=0.0332594, q0.95=0.0471983, q0.99=0.05102
- `SPXW\|stage_training\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|stage_training\|last\|all\|all` `first_observed_fraction`: q0.01=0.00130162, q0.05=0.00191892, q0.25=0.00834112, q0.5=0.0184613, q0.75=0.0345085, q0.95=0.05816, q0.99=0.0729014
- `SPXW\|stage_training\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|stage_training\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00114099, q0.75=0.00413381, q0.95=0.00887437, q0.99=0.0105567
- `SPXW\|stage_training\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|stage_training\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|stage_training\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|stage_training\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|stage_training\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|stage_training\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|stage_training\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|year_2020\|first\|all\|all` `oi_level_date_mean`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|year_2020\|first\|all\|all` `oi_zero_fraction`: q0.01=0.382444, q0.05=0.3825, q0.25=0.395061, q0.5=0.40156, q0.75=0.411777, q0.95=0.41702, q0.99=0.417022
- `SPXW\|year_2020\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25315.4, q0.75=25457.9, q0.95=25683.8, q0.99=25763.9
- `SPXW\|year_2020\|first\|all\|all` `coverage_fraction`: q0.01=0.923865, q0.05=0.942469, q0.25=0.971046, q0.5=0.983111, q0.75=0.99231, q0.95=1, q0.99=1
- `SPXW\|year_2020\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0.00768955, q0.5=0.0168893, q0.75=0.0289543, q0.95=0.057531, q0.99=0.0761347
- `SPXW\|year_2020\|first\|all\|all` `oi_mass`: q0.01=4.15502e+06, q0.05=4.24209e+06, q0.25=4.63081e+06, q0.5=4.85395e+06, q0.75=5.11862e+06, q0.95=5.34331e+06, q0.99=5.34521e+06
- `SPXW\|year_2020\|first\|all\|all` `oi_width`: q0.01=11091.8, q0.05=11106.8, q0.25=11238, q0.5=11324.5, q0.75=11431.8, q0.95=11732, q0.99=11784.8
- `SPXW\|year_2020\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|first\|all\|all` `common_support_first`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|year_2020\|first\|all\|all` `common_support_last`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|year_2020\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|first\|all\|all` `next_delta`: q0.01=22.4355, q0.05=24.0902, q0.25=26.2029, q0.5=28.968, q0.75=31.6667, q0.95=33.8979, q0.99=34.6239
- `SPXW\|year_2020\|first\|all\|all` `next_abs_delta`: q0.01=27.254, q0.05=29.0474, q0.25=33.801, q0.5=40.7456, q0.75=44.0669, q0.95=58.5021, q0.99=58.6113
- `SPXW\|year_2020\|first\|all\|all` `next_positive_fraction`: q0.01=0.164462, q0.05=0.166008, q0.25=0.175159, q0.5=0.181666, q0.75=0.190208, q0.95=0.200752, q0.99=0.203478
- `SPXW\|year_2020\|first\|all\|all` `next_zero_fraction`: q0.01=0.734606, q0.05=0.736948, q0.25=0.746464, q0.5=0.759722, q0.75=0.763798, q0.95=0.778857, q0.99=0.789009
- `SPXW\|year_2020\|first\|all\|all` `next_negative_fraction`: q0.01=0.0424605, q0.05=0.0458365, q0.25=0.0578347, q0.5=0.0605104, q0.75=0.062725, q0.95=0.071128, q0.99=0.0735375
- `SPXW\|year_2020\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0288354, q0.75=0.0332594, q0.95=0.0471983, q0.99=0.05102
- `SPXW\|year_2020\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|year_2020\|first\|all\|all` `first_observed_fraction`: q0.01=0.00130162, q0.05=0.00191892, q0.25=0.00834112, q0.5=0.0184613, q0.75=0.0345085, q0.95=0.05816, q0.99=0.0729014
- `SPXW\|year_2020\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|year_2020\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00114099, q0.75=0.00413381, q0.95=0.00887437, q0.99=0.0105567
- `SPXW\|year_2020\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|year_2020\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|year_2020\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|year_2020\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|year_2020\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|year_2020\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|year_2020\|last\|all\|all` `oi_level_date_mean`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|year_2020\|last\|all\|all` `oi_zero_fraction`: q0.01=0.382444, q0.05=0.3825, q0.25=0.395061, q0.5=0.40156, q0.75=0.411777, q0.95=0.41702, q0.99=0.417022
- `SPXW\|year_2020\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25315.4, q0.75=25457.9, q0.95=25683.8, q0.99=25763.9
- `SPXW\|year_2020\|last\|all\|all` `coverage_fraction`: q0.01=0.923865, q0.05=0.942469, q0.25=0.971046, q0.5=0.983111, q0.75=0.99231, q0.95=1, q0.99=1
- `SPXW\|year_2020\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0.00768955, q0.5=0.0168893, q0.75=0.0289543, q0.95=0.057531, q0.99=0.0761347
- `SPXW\|year_2020\|last\|all\|all` `oi_mass`: q0.01=4.15502e+06, q0.05=4.24209e+06, q0.25=4.63081e+06, q0.5=4.85395e+06, q0.75=5.11862e+06, q0.95=5.34331e+06, q0.99=5.34521e+06
- `SPXW\|year_2020\|last\|all\|all` `oi_width`: q0.01=11091.8, q0.05=11106.8, q0.25=11238, q0.5=11324.5, q0.75=11431.8, q0.95=11732, q0.99=11784.8
- `SPXW\|year_2020\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|last\|all\|all` `common_support_first`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|year_2020\|last\|all\|all` `common_support_last`: q0.01=368.715, q0.05=379.567, q0.25=404.885, q0.5=421.794, q0.75=447.018, q0.95=468.65, q0.99=468.669
- `SPXW\|year_2020\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|last\|all\|all` `next_delta`: q0.01=22.4355, q0.05=24.0902, q0.25=26.2029, q0.5=28.968, q0.75=31.6667, q0.95=33.8979, q0.99=34.6239
- `SPXW\|year_2020\|last\|all\|all` `next_abs_delta`: q0.01=27.254, q0.05=29.0474, q0.25=33.801, q0.5=40.7456, q0.75=44.0669, q0.95=58.5021, q0.99=58.6113
- `SPXW\|year_2020\|last\|all\|all` `next_positive_fraction`: q0.01=0.164462, q0.05=0.166008, q0.25=0.175159, q0.5=0.181666, q0.75=0.190208, q0.95=0.200752, q0.99=0.203478
- `SPXW\|year_2020\|last\|all\|all` `next_zero_fraction`: q0.01=0.734606, q0.05=0.736948, q0.25=0.746464, q0.5=0.759722, q0.75=0.763798, q0.95=0.778857, q0.99=0.789009
- `SPXW\|year_2020\|last\|all\|all` `next_negative_fraction`: q0.01=0.0424605, q0.05=0.0458365, q0.25=0.0578347, q0.5=0.0605104, q0.75=0.062725, q0.95=0.071128, q0.99=0.0735375
- `SPXW\|year_2020\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0288354, q0.75=0.0332594, q0.95=0.0471983, q0.99=0.05102
- `SPXW\|year_2020\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|year_2020\|last\|all\|all` `first_observed_fraction`: q0.01=0.00130162, q0.05=0.00191892, q0.25=0.00834112, q0.5=0.0184613, q0.75=0.0345085, q0.95=0.05816, q0.99=0.0729014
- `SPXW\|year_2020\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPXW\|year_2020\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00114099, q0.75=0.00413381, q0.95=0.00887437, q0.99=0.0105567
- `SPXW\|year_2020\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|year_2020\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|year_2020\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|year_2020\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPXW\|year_2020\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.922301, q0.05=0.934646, q0.25=0.969354, q0.5=0.978941, q0.75=0.991302, q0.95=1, q0.99=1
- `SPXW\|year_2020\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPXW\|year_2020\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.00116687, q0.75=0.00413249, q0.95=0.00876292, q0.99=0.0100972
- `SPX\|all_period\|first\|CALL\|all` `oi_level_date_mean`: q0.01=1216.92, q0.05=1243.81, q0.25=1295.18, q0.5=1347.05, q0.75=1431.32, q0.95=1491.9, q0.99=1513.26
- `SPX\|all_period\|first\|CALL\|all` `oi_mass`: q0.01=3.06134e+06, q0.05=3.09791e+06, q0.25=3.2237e+06, q0.5=3.41612e+06, q0.75=3.68565e+06, q0.95=3.85553e+06, q0.99=3.92251e+06
- `SPX\|all_period\|first\|CALL\|all` `oi_width`: q0.01=2432, q0.05=2432, q0.25=2527, q0.5=2536, q0.75=2575.75, q0.95=2594, q0.99=2594
- `SPX\|all_period\|first\|PUT\|all` `oi_level_date_mean`: q0.01=2711.33, q0.05=2760.36, q0.25=2832.59, q0.5=2953.79, q0.75=3112.3, q0.95=3306.04, q0.99=3347.86
- `SPX\|all_period\|first\|PUT\|all` `oi_mass`: q0.01=6.59396e+06, q0.05=6.71319e+06, q0.25=7.12267e+06, q0.5=7.49081e+06, q0.75=8.01654e+06, q0.95=8.57587e+06, q0.99=8.68435e+06
- `SPX\|all_period\|first\|PUT\|all` `oi_width`: q0.01=2432, q0.05=2432, q0.25=2527, q0.5=2536, q0.75=2575.75, q0.95=2594, q0.99=2594
- `SPX\|all_period\|first\|all\|0` `oi_level_date_mean`: q0.01=5141.12, q0.05=5141.12, q0.25=5141.12, q0.5=5141.12, q0.75=5141.12, q0.95=5141.12, q0.99=5141.12
- `SPX\|all_period\|first\|all\|0` `oi_mass`: q0.01=3.3006e+06, q0.05=3.3006e+06, q0.25=3.3006e+06, q0.5=3.3006e+06, q0.75=3.3006e+06, q0.95=3.3006e+06, q0.99=3.3006e+06
- `SPX\|all_period\|first\|all\|0` `oi_width`: q0.01=642, q0.05=642, q0.25=642, q0.5=642, q0.75=642, q0.95=642, q0.99=642
- `SPX\|all_period\|first\|all\|1` `oi_level_date_mean`: q0.01=4992.92, q0.05=4992.92, q0.25=4992.92, q0.5=4992.92, q0.75=4992.92, q0.95=4992.92, q0.99=4992.92
- `SPX\|all_period\|first\|all\|1` `oi_mass`: q0.01=3.20545e+06, q0.05=3.20545e+06, q0.25=3.20545e+06, q0.5=3.20545e+06, q0.75=3.20545e+06, q0.95=3.20545e+06, q0.99=3.20545e+06
- `SPX\|all_period\|first\|all\|1` `oi_width`: q0.01=642, q0.05=642, q0.25=642, q0.5=642, q0.75=642, q0.95=642, q0.99=642
- `SPX\|all_period\|first\|all\|2-7` `oi_level_date_mean`: q0.01=4813.42, q0.05=4814.22, q0.25=4818.26, q0.5=4847.04, q0.75=4885.54, q0.95=4912.88, q0.99=4918.34
- `SPX\|all_period\|first\|all\|2-7` `oi_mass`: q0.01=3.02882e+06, q0.05=3.0364e+06, q0.25=3.07429e+06, q0.5=3.10964e+06, q0.75=3.13651e+06, q0.95=3.15407e+06, q0.99=3.15758e+06
- `SPX\|all_period\|first\|all\|2-7` `oi_width`: q0.01=628.42, q0.05=630.1, q0.25=638.5, q0.5=642, q0.75=642, q0.95=642, q0.99=642
- `SPX\|all_period\|first\|all\|31-60` `oi_level_date_mean`: q0.01=1591.08, q0.05=1627.07, q0.25=1774.22, q0.5=1921.88, q0.75=2528.41, q0.95=5312.85, q0.99=5377.86
- `SPX\|all_period\|first\|all\|31-60` `oi_mass`: q0.01=957833, q0.05=979494, q0.25=1.07163e+06, q0.5=1.18583e+06, q0.75=1.81937e+06, q0.95=3.71507e+06, q0.99=4.44943e+06
- `SPX\|all_period\|first\|all\|31-60` `oi_width`: q0.01=602, q0.05=602, q0.25=604, q0.5=618, q0.75=627.5, q0.95=784.5, q0.99=1150.5
- `SPX\|all_period\|first\|all\|61+` `oi_level_date_mean`: q0.01=1369.44, q0.05=1384.67, q0.25=1635.37, q0.5=1771.84, q0.75=1870.71, q0.95=1973.15, q0.99=1994.09
- `SPX\|all_period\|first\|all\|61+` `oi_mass`: q0.01=4.85119e+06, q0.05=4.8875e+06, q0.25=6.1211e+06, q0.5=6.80385e+06, q0.75=7.27706e+06, q0.95=7.70234e+06, q0.99=7.81034e+06
- `SPX\|all_period\|first\|all\|61+` `oi_width`: q0.01=3346.9, q0.05=3518.5, q0.25=3767, q0.5=3840, q0.75=3890, q0.95=3903.5, q0.99=3916.7
- `SPX\|all_period\|first\|all\|8-30` `oi_level_date_mean`: q0.01=2244.52, q0.05=2299.09, q0.25=2464.22, q0.5=4632.24, q0.75=4702.18, q0.95=4743.56, q0.99=4762.45
- `SPX\|all_period\|first\|all\|8-30` `oi_mass`: q0.01=1.44098e+06, q0.05=1.47602e+06, q0.25=1.58203e+06, q0.5=2.89978e+06, q0.75=2.95297e+06, q0.95=2.97896e+06, q0.99=2.99082e+06
- `SPX\|all_period\|first\|all\|8-30` `oi_width`: q0.01=626, q0.05=626, q0.25=626, q0.5=628, q0.75=642, q0.95=642, q0.99=642
- `SPX\|all_period\|first\|all\|all` `oi_level_date_mean`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|all_period\|first\|all\|all` `oi_zero_fraction`: q0.01=0.302512, q0.05=0.305158, q0.25=0.319284, q0.5=0.327472, q0.75=0.338064, q0.95=0.352592, q0.99=0.356391
- `SPX\|all_period\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261, q0.75=25261, q0.95=25282, q0.99=25287.4
- `SPX\|all_period\|first\|all\|all` `coverage_fraction`: q0.01=0.942389, q0.05=0.973457, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0017734, q0.95=0.0265427, q0.99=0.0576112
- `SPX\|all_period\|first\|all\|all` `oi_mass`: q0.01=9.6553e+06, q0.05=9.8111e+06, q0.25=1.03956e+07, q0.5=1.09779e+07, q0.75=1.17472e+07, q0.95=1.22332e+07, q0.99=1.24226e+07
- `SPX\|all_period\|first\|all\|all` `oi_width`: q0.01=4864, q0.05=4864, q0.25=5054, q0.5=5072, q0.75=5151.5, q0.95=5188, q0.99=5188
- `SPX\|all_period\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|first\|all\|all` `common_support_first`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|all_period\|first\|all\|all` `common_support_last`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|all_period\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|first\|all\|all` `next_delta`: q0.01=-99.8162, q0.05=-21.6484, q0.25=27.9296, q0.5=36.3878, q0.75=46.8591, q0.95=55.7232, q0.99=60.0858
- `SPX\|all_period\|first\|all\|all` `next_abs_delta`: q0.01=44.4685, q0.05=44.6346, q0.25=49.6237, q0.5=59.8539, q0.75=64.8746, q0.95=131.72, q0.99=228.144
- `SPX\|all_period\|first\|all\|all` `next_positive_fraction`: q0.01=0.116913, q0.05=0.118475, q0.25=0.127499, q0.5=0.134951, q0.75=0.138991, q0.95=0.150444, q0.99=0.160517
- `SPX\|all_period\|first\|all\|all` `next_zero_fraction`: q0.01=0.781624, q0.05=0.790157, q0.25=0.804634, q0.5=0.813217, q0.75=0.819568, q0.95=0.841097, q0.99=0.841112
- `SPX\|all_period\|first\|all\|all` `next_negative_fraction`: q0.01=0.0378963, q0.05=0.0389878, q0.25=0.0467259, q0.5=0.0499029, q0.75=0.0569795, q0.95=0.0742367, q0.99=0.0803832
- `SPX\|all_period\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.03498, q0.99=0.100276
- `SPX\|all_period\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.00256185, q0.95=0.0268411, q0.99=0.0515724
- `SPX\|all_period\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000440653, q0.99=0.000553337
- `SPX\|all_period\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|all_period\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|all_period\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|all_period\|first\|all\|expired` `oi_level_date_mean`: q0.01=3700.26, q0.05=3700.26, q0.25=3700.26, q0.5=3700.26, q0.75=3700.26, q0.95=3700.26, q0.99=3700.26
- `SPX\|all_period\|first\|all\|expired` `oi_mass`: q0.01=2.37557e+06, q0.05=2.37557e+06, q0.25=2.37557e+06, q0.5=2.37557e+06, q0.75=2.37557e+06, q0.95=2.37557e+06, q0.99=2.37557e+06
- `SPX\|all_period\|first\|all\|expired` `oi_width`: q0.01=642, q0.05=642, q0.25=642, q0.5=642, q0.75=642, q0.95=642, q0.99=642
- `SPX\|all_period\|last\|CALL\|all` `oi_level_date_mean`: q0.01=1216.92, q0.05=1243.81, q0.25=1295.18, q0.5=1347.05, q0.75=1431.32, q0.95=1491.9, q0.99=1513.26
- `SPX\|all_period\|last\|CALL\|all` `oi_mass`: q0.01=3.06134e+06, q0.05=3.09791e+06, q0.25=3.2237e+06, q0.5=3.41612e+06, q0.75=3.68565e+06, q0.95=3.85553e+06, q0.99=3.92251e+06
- `SPX\|all_period\|last\|CALL\|all` `oi_width`: q0.01=2432, q0.05=2432, q0.25=2527, q0.5=2536, q0.75=2575.75, q0.95=2594, q0.99=2594
- `SPX\|all_period\|last\|PUT\|all` `oi_level_date_mean`: q0.01=2711.33, q0.05=2760.36, q0.25=2832.59, q0.5=2953.79, q0.75=3112.3, q0.95=3306.04, q0.99=3347.86
- `SPX\|all_period\|last\|PUT\|all` `oi_mass`: q0.01=6.59396e+06, q0.05=6.71319e+06, q0.25=7.12267e+06, q0.5=7.49081e+06, q0.75=8.01654e+06, q0.95=8.57587e+06, q0.99=8.68435e+06
- `SPX\|all_period\|last\|PUT\|all` `oi_width`: q0.01=2432, q0.05=2432, q0.25=2527, q0.5=2536, q0.75=2575.75, q0.95=2594, q0.99=2594
- `SPX\|all_period\|last\|all\|0` `oi_level_date_mean`: q0.01=5141.12, q0.05=5141.12, q0.25=5141.12, q0.5=5141.12, q0.75=5141.12, q0.95=5141.12, q0.99=5141.12
- `SPX\|all_period\|last\|all\|0` `oi_mass`: q0.01=3.3006e+06, q0.05=3.3006e+06, q0.25=3.3006e+06, q0.5=3.3006e+06, q0.75=3.3006e+06, q0.95=3.3006e+06, q0.99=3.3006e+06
- `SPX\|all_period\|last\|all\|0` `oi_width`: q0.01=642, q0.05=642, q0.25=642, q0.5=642, q0.75=642, q0.95=642, q0.99=642
- `SPX\|all_period\|last\|all\|1` `oi_level_date_mean`: q0.01=4992.92, q0.05=4992.92, q0.25=4992.92, q0.5=4992.92, q0.75=4992.92, q0.95=4992.92, q0.99=4992.92
- `SPX\|all_period\|last\|all\|1` `oi_mass`: q0.01=3.20545e+06, q0.05=3.20545e+06, q0.25=3.20545e+06, q0.5=3.20545e+06, q0.75=3.20545e+06, q0.95=3.20545e+06, q0.99=3.20545e+06
- `SPX\|all_period\|last\|all\|1` `oi_width`: q0.01=642, q0.05=642, q0.25=642, q0.5=642, q0.75=642, q0.95=642, q0.99=642
- `SPX\|all_period\|last\|all\|2-7` `oi_level_date_mean`: q0.01=4813.42, q0.05=4814.22, q0.25=4818.26, q0.5=4847.04, q0.75=4885.54, q0.95=4912.88, q0.99=4918.34
- `SPX\|all_period\|last\|all\|2-7` `oi_mass`: q0.01=3.02882e+06, q0.05=3.0364e+06, q0.25=3.07429e+06, q0.5=3.10964e+06, q0.75=3.13651e+06, q0.95=3.15407e+06, q0.99=3.15758e+06
- `SPX\|all_period\|last\|all\|2-7` `oi_width`: q0.01=628.42, q0.05=630.1, q0.25=638.5, q0.5=642, q0.75=642, q0.95=642, q0.99=642
- `SPX\|all_period\|last\|all\|31-60` `oi_level_date_mean`: q0.01=1591.08, q0.05=1627.07, q0.25=1774.22, q0.5=1921.88, q0.75=2528.41, q0.95=5312.85, q0.99=5377.86
- `SPX\|all_period\|last\|all\|31-60` `oi_mass`: q0.01=957833, q0.05=979494, q0.25=1.07163e+06, q0.5=1.18583e+06, q0.75=1.81937e+06, q0.95=3.71507e+06, q0.99=4.44943e+06
- `SPX\|all_period\|last\|all\|31-60` `oi_width`: q0.01=602, q0.05=602, q0.25=604, q0.5=618, q0.75=627.5, q0.95=784.5, q0.99=1150.5
- `SPX\|all_period\|last\|all\|61+` `oi_level_date_mean`: q0.01=1369.44, q0.05=1384.67, q0.25=1635.37, q0.5=1771.84, q0.75=1870.71, q0.95=1973.15, q0.99=1994.09
- `SPX\|all_period\|last\|all\|61+` `oi_mass`: q0.01=4.85119e+06, q0.05=4.8875e+06, q0.25=6.1211e+06, q0.5=6.80385e+06, q0.75=7.27706e+06, q0.95=7.70234e+06, q0.99=7.81034e+06
- `SPX\|all_period\|last\|all\|61+` `oi_width`: q0.01=3346.9, q0.05=3518.5, q0.25=3767, q0.5=3840, q0.75=3890, q0.95=3903.5, q0.99=3916.7
- `SPX\|all_period\|last\|all\|8-30` `oi_level_date_mean`: q0.01=2244.52, q0.05=2299.09, q0.25=2464.22, q0.5=4632.24, q0.75=4702.18, q0.95=4743.56, q0.99=4762.45
- `SPX\|all_period\|last\|all\|8-30` `oi_mass`: q0.01=1.44098e+06, q0.05=1.47602e+06, q0.25=1.58203e+06, q0.5=2.89978e+06, q0.75=2.95297e+06, q0.95=2.97896e+06, q0.99=2.99082e+06
- `SPX\|all_period\|last\|all\|8-30` `oi_width`: q0.01=626, q0.05=626, q0.25=626, q0.5=628, q0.75=642, q0.95=642, q0.99=642
- `SPX\|all_period\|last\|all\|all` `oi_level_date_mean`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|all_period\|last\|all\|all` `oi_zero_fraction`: q0.01=0.302512, q0.05=0.305158, q0.25=0.319284, q0.5=0.327472, q0.75=0.338064, q0.95=0.352592, q0.99=0.356391
- `SPX\|all_period\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261, q0.75=25261, q0.95=25282, q0.99=25287.4
- `SPX\|all_period\|last\|all\|all` `coverage_fraction`: q0.01=0.942389, q0.05=0.973457, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0017734, q0.95=0.0265427, q0.99=0.0576112
- `SPX\|all_period\|last\|all\|all` `oi_mass`: q0.01=9.6553e+06, q0.05=9.8111e+06, q0.25=1.03956e+07, q0.5=1.09779e+07, q0.75=1.17472e+07, q0.95=1.22332e+07, q0.99=1.24226e+07
- `SPX\|all_period\|last\|all\|all` `oi_width`: q0.01=4864, q0.05=4864, q0.25=5054, q0.5=5072, q0.75=5151.5, q0.95=5188, q0.99=5188
- `SPX\|all_period\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|last\|all\|all` `common_support_first`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|all_period\|last\|all\|all` `common_support_last`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|all_period\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|last\|all\|all` `next_delta`: q0.01=-99.8162, q0.05=-21.6484, q0.25=27.9296, q0.5=36.3878, q0.75=46.8591, q0.95=55.7232, q0.99=60.0858
- `SPX\|all_period\|last\|all\|all` `next_abs_delta`: q0.01=44.4685, q0.05=44.6346, q0.25=49.6237, q0.5=59.8539, q0.75=64.8746, q0.95=131.72, q0.99=228.144
- `SPX\|all_period\|last\|all\|all` `next_positive_fraction`: q0.01=0.116913, q0.05=0.118475, q0.25=0.127499, q0.5=0.134951, q0.75=0.138991, q0.95=0.150444, q0.99=0.160517
- `SPX\|all_period\|last\|all\|all` `next_zero_fraction`: q0.01=0.781624, q0.05=0.790157, q0.25=0.804634, q0.5=0.813217, q0.75=0.819568, q0.95=0.841097, q0.99=0.841112
- `SPX\|all_period\|last\|all\|all` `next_negative_fraction`: q0.01=0.0378963, q0.05=0.0389878, q0.25=0.0467259, q0.5=0.0499029, q0.75=0.0569795, q0.95=0.0742367, q0.99=0.0803832
- `SPX\|all_period\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.03498, q0.99=0.100276
- `SPX\|all_period\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.00256185, q0.95=0.0268411, q0.99=0.0515724
- `SPX\|all_period\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000440653, q0.99=0.000553337
- `SPX\|all_period\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|all_period\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|all_period\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|all_period\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|all_period\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|all_period\|last\|all\|expired` `oi_level_date_mean`: q0.01=3700.26, q0.05=3700.26, q0.25=3700.26, q0.5=3700.26, q0.75=3700.26, q0.95=3700.26, q0.99=3700.26
- `SPX\|all_period\|last\|all\|expired` `oi_mass`: q0.01=2.37557e+06, q0.05=2.37557e+06, q0.25=2.37557e+06, q0.5=2.37557e+06, q0.75=2.37557e+06, q0.95=2.37557e+06, q0.99=2.37557e+06
- `SPX\|all_period\|last\|all\|expired` `oi_width`: q0.01=642, q0.05=642, q0.25=642, q0.5=642, q0.75=642, q0.95=642, q0.99=642
- `SPX\|stage_confirmation\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `SPX\|stage_confirmation\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `SPX\|stage_development\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `SPX\|stage_development\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `SPX\|stage_training\|first\|all\|all` `oi_level_date_mean`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|stage_training\|first\|all\|all` `oi_zero_fraction`: q0.01=0.302512, q0.05=0.305158, q0.25=0.319284, q0.5=0.327472, q0.75=0.338064, q0.95=0.352592, q0.99=0.356391
- `SPX\|stage_training\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261, q0.75=25261, q0.95=25282, q0.99=25287.4
- `SPX\|stage_training\|first\|all\|all` `coverage_fraction`: q0.01=0.942389, q0.05=0.973457, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0017734, q0.95=0.0265427, q0.99=0.0576112
- `SPX\|stage_training\|first\|all\|all` `oi_mass`: q0.01=9.6553e+06, q0.05=9.8111e+06, q0.25=1.03956e+07, q0.5=1.09779e+07, q0.75=1.17472e+07, q0.95=1.22332e+07, q0.99=1.24226e+07
- `SPX\|stage_training\|first\|all\|all` `oi_width`: q0.01=4864, q0.05=4864, q0.25=5054, q0.5=5072, q0.75=5151.5, q0.95=5188, q0.99=5188
- `SPX\|stage_training\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|first\|all\|all` `common_support_first`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|stage_training\|first\|all\|all` `common_support_last`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|stage_training\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|first\|all\|all` `next_delta`: q0.01=-99.8162, q0.05=-21.6484, q0.25=27.9296, q0.5=36.3878, q0.75=46.8591, q0.95=55.7232, q0.99=60.0858
- `SPX\|stage_training\|first\|all\|all` `next_abs_delta`: q0.01=44.4685, q0.05=44.6346, q0.25=49.6237, q0.5=59.8539, q0.75=64.8746, q0.95=131.72, q0.99=228.144
- `SPX\|stage_training\|first\|all\|all` `next_positive_fraction`: q0.01=0.116913, q0.05=0.118475, q0.25=0.127499, q0.5=0.134951, q0.75=0.138991, q0.95=0.150444, q0.99=0.160517
- `SPX\|stage_training\|first\|all\|all` `next_zero_fraction`: q0.01=0.781624, q0.05=0.790157, q0.25=0.804634, q0.5=0.813217, q0.75=0.819568, q0.95=0.841097, q0.99=0.841112
- `SPX\|stage_training\|first\|all\|all` `next_negative_fraction`: q0.01=0.0378963, q0.05=0.0389878, q0.25=0.0467259, q0.5=0.0499029, q0.75=0.0569795, q0.95=0.0742367, q0.99=0.0803832
- `SPX\|stage_training\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.03498, q0.99=0.100276
- `SPX\|stage_training\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.00256185, q0.95=0.0268411, q0.99=0.0515724
- `SPX\|stage_training\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000440653, q0.99=0.000553337
- `SPX\|stage_training\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|stage_training\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|stage_training\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|stage_training\|last\|all\|all` `oi_level_date_mean`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|stage_training\|last\|all\|all` `oi_zero_fraction`: q0.01=0.302512, q0.05=0.305158, q0.25=0.319284, q0.5=0.327472, q0.75=0.338064, q0.95=0.352592, q0.99=0.356391
- `SPX\|stage_training\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261, q0.75=25261, q0.95=25282, q0.99=25287.4
- `SPX\|stage_training\|last\|all\|all` `coverage_fraction`: q0.01=0.942389, q0.05=0.973457, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0017734, q0.95=0.0265427, q0.99=0.0576112
- `SPX\|stage_training\|last\|all\|all` `oi_mass`: q0.01=9.6553e+06, q0.05=9.8111e+06, q0.25=1.03956e+07, q0.5=1.09779e+07, q0.75=1.17472e+07, q0.95=1.22332e+07, q0.99=1.24226e+07
- `SPX\|stage_training\|last\|all\|all` `oi_width`: q0.01=4864, q0.05=4864, q0.25=5054, q0.5=5072, q0.75=5151.5, q0.95=5188, q0.99=5188
- `SPX\|stage_training\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|last\|all\|all` `common_support_first`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|stage_training\|last\|all\|all` `common_support_last`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|stage_training\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|last\|all\|all` `next_delta`: q0.01=-99.8162, q0.05=-21.6484, q0.25=27.9296, q0.5=36.3878, q0.75=46.8591, q0.95=55.7232, q0.99=60.0858
- `SPX\|stage_training\|last\|all\|all` `next_abs_delta`: q0.01=44.4685, q0.05=44.6346, q0.25=49.6237, q0.5=59.8539, q0.75=64.8746, q0.95=131.72, q0.99=228.144
- `SPX\|stage_training\|last\|all\|all` `next_positive_fraction`: q0.01=0.116913, q0.05=0.118475, q0.25=0.127499, q0.5=0.134951, q0.75=0.138991, q0.95=0.150444, q0.99=0.160517
- `SPX\|stage_training\|last\|all\|all` `next_zero_fraction`: q0.01=0.781624, q0.05=0.790157, q0.25=0.804634, q0.5=0.813217, q0.75=0.819568, q0.95=0.841097, q0.99=0.841112
- `SPX\|stage_training\|last\|all\|all` `next_negative_fraction`: q0.01=0.0378963, q0.05=0.0389878, q0.25=0.0467259, q0.5=0.0499029, q0.75=0.0569795, q0.95=0.0742367, q0.99=0.0803832
- `SPX\|stage_training\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.03498, q0.99=0.100276
- `SPX\|stage_training\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.00256185, q0.95=0.0268411, q0.99=0.0515724
- `SPX\|stage_training\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000440653, q0.99=0.000553337
- `SPX\|stage_training\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|stage_training\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|stage_training\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|stage_training\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|stage_training\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|year_2020\|first\|all\|all` `oi_level_date_mean`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|year_2020\|first\|all\|all` `oi_zero_fraction`: q0.01=0.302512, q0.05=0.305158, q0.25=0.319284, q0.5=0.327472, q0.75=0.338064, q0.95=0.352592, q0.99=0.356391
- `SPX\|year_2020\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261, q0.75=25261, q0.95=25282, q0.99=25287.4
- `SPX\|year_2020\|first\|all\|all` `coverage_fraction`: q0.01=0.942389, q0.05=0.973457, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0017734, q0.95=0.0265427, q0.99=0.0576112
- `SPX\|year_2020\|first\|all\|all` `oi_mass`: q0.01=9.6553e+06, q0.05=9.8111e+06, q0.25=1.03956e+07, q0.5=1.09779e+07, q0.75=1.17472e+07, q0.95=1.22332e+07, q0.99=1.24226e+07
- `SPX\|year_2020\|first\|all\|all` `oi_width`: q0.01=4864, q0.05=4864, q0.25=5054, q0.5=5072, q0.75=5151.5, q0.95=5188, q0.99=5188
- `SPX\|year_2020\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|first\|all\|all` `common_support_first`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|year_2020\|first\|all\|all` `common_support_last`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|year_2020\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|first\|all\|all` `next_delta`: q0.01=-99.8162, q0.05=-21.6484, q0.25=27.9296, q0.5=36.3878, q0.75=46.8591, q0.95=55.7232, q0.99=60.0858
- `SPX\|year_2020\|first\|all\|all` `next_abs_delta`: q0.01=44.4685, q0.05=44.6346, q0.25=49.6237, q0.5=59.8539, q0.75=64.8746, q0.95=131.72, q0.99=228.144
- `SPX\|year_2020\|first\|all\|all` `next_positive_fraction`: q0.01=0.116913, q0.05=0.118475, q0.25=0.127499, q0.5=0.134951, q0.75=0.138991, q0.95=0.150444, q0.99=0.160517
- `SPX\|year_2020\|first\|all\|all` `next_zero_fraction`: q0.01=0.781624, q0.05=0.790157, q0.25=0.804634, q0.5=0.813217, q0.75=0.819568, q0.95=0.841097, q0.99=0.841112
- `SPX\|year_2020\|first\|all\|all` `next_negative_fraction`: q0.01=0.0378963, q0.05=0.0389878, q0.25=0.0467259, q0.5=0.0499029, q0.75=0.0569795, q0.95=0.0742367, q0.99=0.0803832
- `SPX\|year_2020\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.03498, q0.99=0.100276
- `SPX\|year_2020\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.00256185, q0.95=0.0268411, q0.99=0.0515724
- `SPX\|year_2020\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000440653, q0.99=0.000553337
- `SPX\|year_2020\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|year_2020\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|year_2020\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|year_2020\|last\|all\|all` `oi_level_date_mean`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|year_2020\|last\|all\|all` `oi_zero_fraction`: q0.01=0.302512, q0.05=0.305158, q0.25=0.319284, q0.5=0.327472, q0.75=0.338064, q0.95=0.352592, q0.99=0.356391
- `SPX\|year_2020\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261, q0.75=25261, q0.95=25282, q0.99=25287.4
- `SPX\|year_2020\|last\|all\|all` `coverage_fraction`: q0.01=0.942389, q0.05=0.973457, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.0017734, q0.95=0.0265427, q0.99=0.0576112
- `SPX\|year_2020\|last\|all\|all` `oi_mass`: q0.01=9.6553e+06, q0.05=9.8111e+06, q0.25=1.03956e+07, q0.5=1.09779e+07, q0.75=1.17472e+07, q0.95=1.22332e+07, q0.99=1.24226e+07
- `SPX\|year_2020\|last\|all\|all` `oi_width`: q0.01=4864, q0.05=4864, q0.25=5054, q0.5=5072, q0.75=5151.5, q0.95=5188, q0.99=5188
- `SPX\|year_2020\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|last\|all\|all` `common_support_first`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|year_2020\|last\|all\|all` `common_support_last`: q0.01=1985.05, q0.05=2017.09, q0.25=2066.16, q0.5=2164.4, q0.75=2276.8, q0.95=2367.86, q0.99=2396.46
- `SPX\|year_2020\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|last\|all\|all` `next_delta`: q0.01=-99.8162, q0.05=-21.6484, q0.25=27.9296, q0.5=36.3878, q0.75=46.8591, q0.95=55.7232, q0.99=60.0858
- `SPX\|year_2020\|last\|all\|all` `next_abs_delta`: q0.01=44.4685, q0.05=44.6346, q0.25=49.6237, q0.5=59.8539, q0.75=64.8746, q0.95=131.72, q0.99=228.144
- `SPX\|year_2020\|last\|all\|all` `next_positive_fraction`: q0.01=0.116913, q0.05=0.118475, q0.25=0.127499, q0.5=0.134951, q0.75=0.138991, q0.95=0.150444, q0.99=0.160517
- `SPX\|year_2020\|last\|all\|all` `next_zero_fraction`: q0.01=0.781624, q0.05=0.790157, q0.25=0.804634, q0.5=0.813217, q0.75=0.819568, q0.95=0.841097, q0.99=0.841112
- `SPX\|year_2020\|last\|all\|all` `next_negative_fraction`: q0.01=0.0378963, q0.05=0.0389878, q0.25=0.0467259, q0.5=0.0499029, q0.75=0.0569795, q0.95=0.0742367, q0.99=0.0803832
- `SPX\|year_2020\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.03498, q0.99=0.100276
- `SPX\|year_2020\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0.00256185, q0.95=0.0268411, q0.99=0.0515724
- `SPX\|year_2020\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000440653, q0.99=0.000553337
- `SPX\|year_2020\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|year_2020\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPX\|year_2020\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.942331, q0.05=0.97317, q0.25=0.998227, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPX\|year_2020\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPX\|year_2020\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.000435827, q0.99=0.000549771
- `SPY\|all_period\|first\|CALL\|all` `oi_level_date_mean`: q0.01=1578.74, q0.05=1597.79, q0.25=1625.27, q0.5=1668.23, q0.75=1676.45, q0.95=1842.44, q0.99=1842.47
- `SPY\|all_period\|first\|CALL\|all` `oi_mass`: q0.01=6.00957e+06, q0.05=6.07746e+06, q0.25=6.22097e+06, q0.5=6.32161e+06, q0.75=6.58313e+06, q0.95=7.14453e+06, q0.99=7.1745e+06
- `SPY\|all_period\|first\|CALL\|all` `oi_width`: q0.01=3676.35, q0.05=3681.75, q0.25=3780.75, q0.5=3872, q0.75=3906, q0.95=3986.5, q0.99=3997.3
- `SPY\|all_period\|first\|PUT\|all` `oi_level_date_mean`: q0.01=2723.52, q0.05=2737.7, q0.25=3174.08, q0.5=3258.48, q0.75=3393.59, q0.95=3590.48, q0.99=3633.8
- `SPY\|all_period\|first\|PUT\|all` `oi_mass`: q0.01=1.05593e+07, q0.05=1.06587e+07, q0.25=1.18421e+07, q0.5=1.25149e+07, q0.75=1.30523e+07, q0.95=1.40886e+07, q0.99=1.44806e+07
- `SPY\|all_period\|first\|PUT\|all` `oi_width`: q0.01=3676.35, q0.05=3681.75, q0.25=3780.75, q0.5=3872, q0.75=3906, q0.95=3986.5, q0.99=3997.3
- `SPY\|all_period\|first\|all\|0` `oi_level_date_mean`: q0.01=1810.48, q0.05=1917.52, q0.25=2434.33, q0.5=3069.84, q0.75=3473.79, q0.95=9831.79, q0.99=12852.4
- `SPY\|all_period\|first\|all\|0` `oi_mass`: q0.01=270448, q0.05=282009, q0.25=312381, q0.5=413808, q0.75=947098, q0.95=3.77841e+06, q0.99=5.58909e+06
- `SPY\|all_period\|first\|all\|0` `oi_width`: q0.01=120, q0.05=120, q0.25=144, q0.5=149, q0.75=225.5, q0.95=372, q0.99=429.6
- `SPY\|all_period\|first\|all\|1` `oi_level_date_mean`: q0.01=1735.43, q0.05=1990.35, q0.25=2756.31, q0.5=3049.38, q0.75=3992.1, q0.95=10843.4, q0.99=12991.7
- `SPY\|all_period\|first\|all\|1` `oi_mass`: q0.01=207267, q0.05=233921, q0.25=361458, q0.5=719654, q0.75=927772, q0.95=4.49501e+06, q0.99=5.70443e+06
- `SPY\|all_period\|first\|all\|1` `oi_width`: q0.01=114.36, q0.05=115.8, q0.25=134, q0.5=194, q0.75=260, q0.95=396, q0.99=434.4
- `SPY\|all_period\|first\|all\|2-7` `oi_level_date_mean`: q0.01=1155.89, q0.05=1343.22, q0.25=1866.22, q0.5=2232.23, q0.75=4430.49, q0.95=10263.8, q0.99=10554.9
- `SPY\|all_period\|first\|all\|2-7` `oi_mass`: q0.01=331057, q0.05=342163, q0.25=700814, q0.5=1.0025e+06, q0.75=2.79275e+06, q0.95=6.04864e+06, q0.99=6.15486e+06
- `SPY\|all_period\|first\|all\|2-7` `oi_width`: q0.01=232.3, q0.05=233.5, q0.25=305, q0.5=456, q0.75=546.5, q0.95=692.5, q0.99=732.1
- `SPY\|all_period\|first\|all\|31-60` `oi_level_date_mean`: q0.01=2542.31, q0.05=2615.69, q0.25=3005.31, q0.5=3383.28, q0.75=4213.1, q0.95=5602.14, q0.99=6432
- `SPY\|all_period\|first\|all\|31-60` `oi_mass`: q0.01=1.94134e+06, q0.05=1.9749e+06, q0.25=2.07965e+06, q0.5=2.54384e+06, q0.75=3.13036e+06, q0.95=4.22519e+06, q0.99=5.86979e+06
- `SPY\|all_period\|first\|all\|31-60` `oi_width`: q0.01=588.6, q0.05=615, q0.25=693.5, q0.5=744, q0.75=809, q0.95=884.5, q0.99=933.7
- `SPY\|all_period\|first\|all\|61+` `oi_level_date_mean`: q0.01=1447.78, q0.05=1456.08, q0.25=1624.45, q0.5=1804.18, q0.75=1869.11, q0.95=1964.01, q0.99=1985.75
- `SPY\|all_period\|first\|all\|61+` `oi_mass`: q0.01=6.53802e+06, q0.05=6.60295e+06, q0.25=7.21375e+06, q0.5=7.91313e+06, q0.75=8.57834e+06, q0.95=9.19804e+06, q0.99=9.27155e+06
- `SPY\|all_period\|first\|all\|61+` `oi_width`: q0.01=4370.7, q0.05=4381.5, q0.25=4386, q0.5=4585, q0.75=4601, q0.95=4713, q0.99=4744.2
- `SPY\|all_period\|first\|all\|8-30` `oi_level_date_mean`: q0.01=967.042, q0.05=996.447, q0.25=1179.87, q0.5=2895.84, q0.75=3762.61, q0.95=3825.84, q0.99=3833.15
- `SPY\|all_period\|first\|all\|8-30` `oi_mass`: q0.01=1.45596e+06, q0.05=1.52901e+06, q0.25=1.74481e+06, q0.5=4.67187e+06, q0.75=6.48782e+06, q0.95=6.7278e+06, q0.99=6.82498e+06
- `SPY\|all_period\|first\|all\|8-30` `oi_width`: q0.01=1340.3, q0.05=1389.5, q0.25=1531, q0.5=1637, q0.75=1743.5, q0.95=1786, q0.99=1786
- `SPY\|all_period\|first\|all\|all` `oi_level_date_mean`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|all_period\|first\|all\|all` `oi_zero_fraction`: q0.01=0.213309, q0.05=0.213543, q0.25=0.220173, q0.5=0.226255, q0.75=0.232224, q0.95=0.241828, q0.99=0.248734
- `SPY\|all_period\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25358.8, q0.05=25403.2, q0.25=25754.4, q0.5=26279.6, q0.75=26480.8, q0.95=27503.9, q0.99=27604.7
- `SPY\|all_period\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|all_period\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|first\|all\|all` `oi_mass`: q0.01=1.68104e+07, q0.05=1.69687e+07, q0.25=1.7948e+07, q0.5=1.89169e+07, q0.75=1.97475e+07, q0.95=2.09327e+07, q0.99=2.10724e+07
- `SPY\|all_period\|first\|all\|all` `oi_width`: q0.01=7352.7, q0.05=7363.5, q0.25=7561.5, q0.5=7744, q0.75=7812, q0.95=7973, q0.99=7994.6
- `SPY\|all_period\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|first\|all\|all` `common_support_first`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|all_period\|first\|all\|all` `common_support_last`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|all_period\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|first\|all\|all` `next_delta`: q0.01=-17.7783, q0.05=30.5802, q0.25=76.1307, q0.5=83.2864, q0.75=93.7372, q0.95=102.644, q0.99=110.18
- `SPY\|all_period\|first\|all\|all` `next_abs_delta`: q0.01=93.1484, q0.05=98.885, q0.25=123.217, q0.5=147.824, q0.75=156.22, q0.95=219.537, q0.99=306.412
- `SPY\|all_period\|first\|all\|all` `next_positive_fraction`: q0.01=0.239033, q0.05=0.247446, q0.25=0.258937, q0.5=0.27011, q0.75=0.279803, q0.95=0.288891, q0.99=0.293245
- `SPY\|all_period\|first\|all\|all` `next_zero_fraction`: q0.01=0.60122, q0.05=0.607946, q0.25=0.62453, q0.5=0.636387, q0.75=0.653043, q0.95=0.673378, q0.99=0.682504
- `SPY\|all_period\|first\|all\|all` `next_negative_fraction`: q0.01=0.0770319, q0.05=0.0778478, q0.25=0.0845643, q0.5=0.0895753, q0.75=0.0983763, q0.95=0.11523, q0.99=0.118685
- `SPY\|all_period\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0181269, q0.75=0.0215759, q0.95=0.0398267, q0.99=0.0513353
- `SPY\|all_period\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|all_period\|first\|all\|all` `first_observed_fraction`: q0.01=0.0020172, q0.05=0.00285273, q0.25=0.00997311, q0.5=0.0210843, q0.75=0.0251762, q0.95=0.0330037, q0.99=0.0428819
- `SPY\|all_period\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|all_period\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0.00204173, q0.05=0.00297537, q0.25=0.0103494, q0.5=0.0213764, q0.75=0.0256027, q0.95=0.047073, q0.99=0.0491936
- `SPY\|all_period\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|all_period\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|all_period\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|all_period\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|all_period\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|all_period\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|all_period\|first\|all\|expired` `oi_level_date_mean`: q0.01=1572.62, q0.05=1654.68, q0.25=2328.37, q0.5=2794.8, q0.75=3930.54, q0.95=9973.35, q0.99=10721
- `SPY\|all_period\|first\|all\|expired` `oi_mass`: q0.01=234932, q0.05=243396, q0.25=287966, q0.5=404002, q0.75=779979, q0.95=3.69695e+06, q0.99=4.61386e+06
- `SPY\|all_period\|first\|all\|expired` `oi_width`: q0.01=120, q0.05=120, q0.25=144, q0.5=149, q0.75=225.5, q0.95=361.2, q0.99=427.44
- `SPY\|all_period\|last\|CALL\|all` `oi_level_date_mean`: q0.01=1578.74, q0.05=1597.79, q0.25=1625.27, q0.5=1668.23, q0.75=1676.45, q0.95=1842.44, q0.99=1842.47
- `SPY\|all_period\|last\|CALL\|all` `oi_mass`: q0.01=6.00957e+06, q0.05=6.07746e+06, q0.25=6.22097e+06, q0.5=6.32161e+06, q0.75=6.58313e+06, q0.95=7.14453e+06, q0.99=7.1745e+06
- `SPY\|all_period\|last\|CALL\|all` `oi_width`: q0.01=3676.35, q0.05=3681.75, q0.25=3780.75, q0.5=3872, q0.75=3906, q0.95=3986.5, q0.99=3997.3
- `SPY\|all_period\|last\|PUT\|all` `oi_level_date_mean`: q0.01=2723.52, q0.05=2737.7, q0.25=3174.08, q0.5=3258.48, q0.75=3393.59, q0.95=3590.48, q0.99=3633.8
- `SPY\|all_period\|last\|PUT\|all` `oi_mass`: q0.01=1.05593e+07, q0.05=1.06587e+07, q0.25=1.18421e+07, q0.5=1.25149e+07, q0.75=1.30523e+07, q0.95=1.40886e+07, q0.99=1.44806e+07
- `SPY\|all_period\|last\|PUT\|all` `oi_width`: q0.01=3676.35, q0.05=3681.75, q0.25=3780.75, q0.5=3872, q0.75=3906, q0.95=3986.5, q0.99=3997.3
- `SPY\|all_period\|last\|all\|0` `oi_level_date_mean`: q0.01=1810.48, q0.05=1917.52, q0.25=2434.33, q0.5=3069.84, q0.75=3473.79, q0.95=9831.79, q0.99=12852.4
- `SPY\|all_period\|last\|all\|0` `oi_mass`: q0.01=270448, q0.05=282009, q0.25=312381, q0.5=413808, q0.75=947098, q0.95=3.77841e+06, q0.99=5.58909e+06
- `SPY\|all_period\|last\|all\|0` `oi_width`: q0.01=120, q0.05=120, q0.25=144, q0.5=149, q0.75=225.5, q0.95=372, q0.99=429.6
- `SPY\|all_period\|last\|all\|1` `oi_level_date_mean`: q0.01=1735.43, q0.05=1990.35, q0.25=2756.31, q0.5=3049.38, q0.75=3992.1, q0.95=10843.4, q0.99=12991.7
- `SPY\|all_period\|last\|all\|1` `oi_mass`: q0.01=207267, q0.05=233921, q0.25=361458, q0.5=719654, q0.75=927772, q0.95=4.49501e+06, q0.99=5.70443e+06
- `SPY\|all_period\|last\|all\|1` `oi_width`: q0.01=114.36, q0.05=115.8, q0.25=134, q0.5=194, q0.75=260, q0.95=396, q0.99=434.4
- `SPY\|all_period\|last\|all\|2-7` `oi_level_date_mean`: q0.01=1155.89, q0.05=1343.22, q0.25=1866.22, q0.5=2232.23, q0.75=4430.49, q0.95=10263.8, q0.99=10554.9
- `SPY\|all_period\|last\|all\|2-7` `oi_mass`: q0.01=331057, q0.05=342163, q0.25=700814, q0.5=1.0025e+06, q0.75=2.79275e+06, q0.95=6.04864e+06, q0.99=6.15486e+06
- `SPY\|all_period\|last\|all\|2-7` `oi_width`: q0.01=232.3, q0.05=233.5, q0.25=305, q0.5=456, q0.75=546.5, q0.95=692.5, q0.99=732.1
- `SPY\|all_period\|last\|all\|31-60` `oi_level_date_mean`: q0.01=2542.31, q0.05=2615.69, q0.25=3005.31, q0.5=3383.28, q0.75=4213.1, q0.95=5602.14, q0.99=6432
- `SPY\|all_period\|last\|all\|31-60` `oi_mass`: q0.01=1.94134e+06, q0.05=1.9749e+06, q0.25=2.07965e+06, q0.5=2.54384e+06, q0.75=3.13036e+06, q0.95=4.22519e+06, q0.99=5.86979e+06
- `SPY\|all_period\|last\|all\|31-60` `oi_width`: q0.01=588.6, q0.05=615, q0.25=693.5, q0.5=744, q0.75=809, q0.95=884.5, q0.99=933.7
- `SPY\|all_period\|last\|all\|61+` `oi_level_date_mean`: q0.01=1447.78, q0.05=1456.08, q0.25=1624.45, q0.5=1804.18, q0.75=1869.11, q0.95=1964.01, q0.99=1985.75
- `SPY\|all_period\|last\|all\|61+` `oi_mass`: q0.01=6.53802e+06, q0.05=6.60295e+06, q0.25=7.21375e+06, q0.5=7.91313e+06, q0.75=8.57834e+06, q0.95=9.19804e+06, q0.99=9.27155e+06
- `SPY\|all_period\|last\|all\|61+` `oi_width`: q0.01=4370.7, q0.05=4381.5, q0.25=4386, q0.5=4585, q0.75=4601, q0.95=4713, q0.99=4744.2
- `SPY\|all_period\|last\|all\|8-30` `oi_level_date_mean`: q0.01=967.042, q0.05=996.447, q0.25=1179.87, q0.5=2895.84, q0.75=3762.61, q0.95=3825.84, q0.99=3833.15
- `SPY\|all_period\|last\|all\|8-30` `oi_mass`: q0.01=1.45596e+06, q0.05=1.52901e+06, q0.25=1.74481e+06, q0.5=4.67187e+06, q0.75=6.48782e+06, q0.95=6.7278e+06, q0.99=6.82498e+06
- `SPY\|all_period\|last\|all\|8-30` `oi_width`: q0.01=1340.3, q0.05=1389.5, q0.25=1531, q0.5=1637, q0.75=1743.5, q0.95=1786, q0.99=1786
- `SPY\|all_period\|last\|all\|all` `oi_level_date_mean`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|all_period\|last\|all\|all` `oi_zero_fraction`: q0.01=0.213309, q0.05=0.213543, q0.25=0.220173, q0.5=0.226255, q0.75=0.232224, q0.95=0.241828, q0.99=0.248734
- `SPY\|all_period\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25358.8, q0.05=25403.2, q0.25=25754.4, q0.5=26279.6, q0.75=26480.8, q0.95=27503.9, q0.99=27604.7
- `SPY\|all_period\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|all_period\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|last\|all\|all` `oi_mass`: q0.01=1.68104e+07, q0.05=1.69687e+07, q0.25=1.7948e+07, q0.5=1.89169e+07, q0.75=1.97475e+07, q0.95=2.09327e+07, q0.99=2.10724e+07
- `SPY\|all_period\|last\|all\|all` `oi_width`: q0.01=7352.7, q0.05=7363.5, q0.25=7561.5, q0.5=7744, q0.75=7812, q0.95=7973, q0.99=7994.6
- `SPY\|all_period\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|last\|all\|all` `common_support_first`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|all_period\|last\|all\|all` `common_support_last`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|all_period\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|last\|all\|all` `next_delta`: q0.01=-17.7783, q0.05=30.5802, q0.25=76.1307, q0.5=83.2864, q0.75=93.7372, q0.95=102.644, q0.99=110.18
- `SPY\|all_period\|last\|all\|all` `next_abs_delta`: q0.01=93.1484, q0.05=98.885, q0.25=123.217, q0.5=147.824, q0.75=156.22, q0.95=219.537, q0.99=306.412
- `SPY\|all_period\|last\|all\|all` `next_positive_fraction`: q0.01=0.239033, q0.05=0.247446, q0.25=0.258937, q0.5=0.27011, q0.75=0.279803, q0.95=0.288891, q0.99=0.293245
- `SPY\|all_period\|last\|all\|all` `next_zero_fraction`: q0.01=0.60122, q0.05=0.607946, q0.25=0.62453, q0.5=0.636387, q0.75=0.653043, q0.95=0.673378, q0.99=0.682504
- `SPY\|all_period\|last\|all\|all` `next_negative_fraction`: q0.01=0.0770319, q0.05=0.0778478, q0.25=0.0845643, q0.5=0.0895753, q0.75=0.0983763, q0.95=0.11523, q0.99=0.118685
- `SPY\|all_period\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0181269, q0.75=0.0215759, q0.95=0.0398267, q0.99=0.0513353
- `SPY\|all_period\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|all_period\|last\|all\|all` `first_observed_fraction`: q0.01=0.0020172, q0.05=0.00285273, q0.25=0.00997311, q0.5=0.0210843, q0.75=0.0251762, q0.95=0.0330037, q0.99=0.0428819
- `SPY\|all_period\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|all_period\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0.00204173, q0.05=0.00297537, q0.25=0.0103494, q0.5=0.0213764, q0.75=0.0256027, q0.95=0.047073, q0.99=0.0491936
- `SPY\|all_period\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|all_period\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|all_period\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|all_period\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|all_period\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|all_period\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|all_period\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|all_period\|last\|all\|expired` `oi_level_date_mean`: q0.01=1572.62, q0.05=1654.68, q0.25=2328.37, q0.5=2794.8, q0.75=3930.54, q0.95=9973.35, q0.99=10721
- `SPY\|all_period\|last\|all\|expired` `oi_mass`: q0.01=234932, q0.05=243396, q0.25=287966, q0.5=404002, q0.75=779979, q0.95=3.69695e+06, q0.99=4.61386e+06
- `SPY\|all_period\|last\|all\|expired` `oi_width`: q0.01=120, q0.05=120, q0.25=144, q0.5=149, q0.75=225.5, q0.95=361.2, q0.99=427.44
- `SPY\|stage_confirmation\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `SPY\|stage_confirmation\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `SPY\|stage_development\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `SPY\|stage_development\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `SPY\|stage_training\|first\|all\|all` `oi_level_date_mean`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|stage_training\|first\|all\|all` `oi_zero_fraction`: q0.01=0.213309, q0.05=0.213543, q0.25=0.220173, q0.5=0.226255, q0.75=0.232224, q0.95=0.241828, q0.99=0.248734
- `SPY\|stage_training\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25358.8, q0.05=25403.2, q0.25=25754.4, q0.5=26279.6, q0.75=26480.8, q0.95=27503.9, q0.99=27604.7
- `SPY\|stage_training\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|stage_training\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|first\|all\|all` `oi_mass`: q0.01=1.68104e+07, q0.05=1.69687e+07, q0.25=1.7948e+07, q0.5=1.89169e+07, q0.75=1.97475e+07, q0.95=2.09327e+07, q0.99=2.10724e+07
- `SPY\|stage_training\|first\|all\|all` `oi_width`: q0.01=7352.7, q0.05=7363.5, q0.25=7561.5, q0.5=7744, q0.75=7812, q0.95=7973, q0.99=7994.6
- `SPY\|stage_training\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|first\|all\|all` `common_support_first`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|stage_training\|first\|all\|all` `common_support_last`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|stage_training\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|first\|all\|all` `next_delta`: q0.01=-17.7783, q0.05=30.5802, q0.25=76.1307, q0.5=83.2864, q0.75=93.7372, q0.95=102.644, q0.99=110.18
- `SPY\|stage_training\|first\|all\|all` `next_abs_delta`: q0.01=93.1484, q0.05=98.885, q0.25=123.217, q0.5=147.824, q0.75=156.22, q0.95=219.537, q0.99=306.412
- `SPY\|stage_training\|first\|all\|all` `next_positive_fraction`: q0.01=0.239033, q0.05=0.247446, q0.25=0.258937, q0.5=0.27011, q0.75=0.279803, q0.95=0.288891, q0.99=0.293245
- `SPY\|stage_training\|first\|all\|all` `next_zero_fraction`: q0.01=0.60122, q0.05=0.607946, q0.25=0.62453, q0.5=0.636387, q0.75=0.653043, q0.95=0.673378, q0.99=0.682504
- `SPY\|stage_training\|first\|all\|all` `next_negative_fraction`: q0.01=0.0770319, q0.05=0.0778478, q0.25=0.0845643, q0.5=0.0895753, q0.75=0.0983763, q0.95=0.11523, q0.99=0.118685
- `SPY\|stage_training\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0181269, q0.75=0.0215759, q0.95=0.0398267, q0.99=0.0513353
- `SPY\|stage_training\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|stage_training\|first\|all\|all` `first_observed_fraction`: q0.01=0.0020172, q0.05=0.00285273, q0.25=0.00997311, q0.5=0.0210843, q0.75=0.0251762, q0.95=0.0330037, q0.99=0.0428819
- `SPY\|stage_training\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|stage_training\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0.00204173, q0.05=0.00297537, q0.25=0.0103494, q0.5=0.0213764, q0.75=0.0256027, q0.95=0.047073, q0.99=0.0491936
- `SPY\|stage_training\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|stage_training\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|stage_training\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|stage_training\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|stage_training\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|stage_training\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|stage_training\|last\|all\|all` `oi_level_date_mean`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|stage_training\|last\|all\|all` `oi_zero_fraction`: q0.01=0.213309, q0.05=0.213543, q0.25=0.220173, q0.5=0.226255, q0.75=0.232224, q0.95=0.241828, q0.99=0.248734
- `SPY\|stage_training\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25358.8, q0.05=25403.2, q0.25=25754.4, q0.5=26279.6, q0.75=26480.8, q0.95=27503.9, q0.99=27604.7
- `SPY\|stage_training\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|stage_training\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|last\|all\|all` `oi_mass`: q0.01=1.68104e+07, q0.05=1.69687e+07, q0.25=1.7948e+07, q0.5=1.89169e+07, q0.75=1.97475e+07, q0.95=2.09327e+07, q0.99=2.10724e+07
- `SPY\|stage_training\|last\|all\|all` `oi_width`: q0.01=7352.7, q0.05=7363.5, q0.25=7561.5, q0.5=7744, q0.75=7812, q0.95=7973, q0.99=7994.6
- `SPY\|stage_training\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|last\|all\|all` `common_support_first`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|stage_training\|last\|all\|all` `common_support_last`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|stage_training\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|last\|all\|all` `next_delta`: q0.01=-17.7783, q0.05=30.5802, q0.25=76.1307, q0.5=83.2864, q0.75=93.7372, q0.95=102.644, q0.99=110.18
- `SPY\|stage_training\|last\|all\|all` `next_abs_delta`: q0.01=93.1484, q0.05=98.885, q0.25=123.217, q0.5=147.824, q0.75=156.22, q0.95=219.537, q0.99=306.412
- `SPY\|stage_training\|last\|all\|all` `next_positive_fraction`: q0.01=0.239033, q0.05=0.247446, q0.25=0.258937, q0.5=0.27011, q0.75=0.279803, q0.95=0.288891, q0.99=0.293245
- `SPY\|stage_training\|last\|all\|all` `next_zero_fraction`: q0.01=0.60122, q0.05=0.607946, q0.25=0.62453, q0.5=0.636387, q0.75=0.653043, q0.95=0.673378, q0.99=0.682504
- `SPY\|stage_training\|last\|all\|all` `next_negative_fraction`: q0.01=0.0770319, q0.05=0.0778478, q0.25=0.0845643, q0.5=0.0895753, q0.75=0.0983763, q0.95=0.11523, q0.99=0.118685
- `SPY\|stage_training\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0181269, q0.75=0.0215759, q0.95=0.0398267, q0.99=0.0513353
- `SPY\|stage_training\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|stage_training\|last\|all\|all` `first_observed_fraction`: q0.01=0.0020172, q0.05=0.00285273, q0.25=0.00997311, q0.5=0.0210843, q0.75=0.0251762, q0.95=0.0330037, q0.99=0.0428819
- `SPY\|stage_training\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|stage_training\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0.00204173, q0.05=0.00297537, q0.25=0.0103494, q0.5=0.0213764, q0.75=0.0256027, q0.95=0.047073, q0.99=0.0491936
- `SPY\|stage_training\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|stage_training\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|stage_training\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|stage_training\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|stage_training\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|stage_training\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|stage_training\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|year_2020\|first\|all\|all` `oi_level_date_mean`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|year_2020\|first\|all\|all` `oi_zero_fraction`: q0.01=0.213309, q0.05=0.213543, q0.25=0.220173, q0.5=0.226255, q0.75=0.232224, q0.95=0.241828, q0.99=0.248734
- `SPY\|year_2020\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25358.8, q0.05=25403.2, q0.25=25754.4, q0.5=26279.6, q0.75=26480.8, q0.95=27503.9, q0.99=27604.7
- `SPY\|year_2020\|first\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|year_2020\|first\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|first\|all\|all` `oi_mass`: q0.01=1.68104e+07, q0.05=1.69687e+07, q0.25=1.7948e+07, q0.5=1.89169e+07, q0.75=1.97475e+07, q0.95=2.09327e+07, q0.99=2.10724e+07
- `SPY\|year_2020\|first\|all\|all` `oi_width`: q0.01=7352.7, q0.05=7363.5, q0.25=7561.5, q0.5=7744, q0.75=7812, q0.95=7973, q0.99=7994.6
- `SPY\|year_2020\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|first\|all\|all` `common_support_first`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|year_2020\|first\|all\|all` `common_support_last`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|year_2020\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|first\|all\|all` `next_delta`: q0.01=-17.7783, q0.05=30.5802, q0.25=76.1307, q0.5=83.2864, q0.75=93.7372, q0.95=102.644, q0.99=110.18
- `SPY\|year_2020\|first\|all\|all` `next_abs_delta`: q0.01=93.1484, q0.05=98.885, q0.25=123.217, q0.5=147.824, q0.75=156.22, q0.95=219.537, q0.99=306.412
- `SPY\|year_2020\|first\|all\|all` `next_positive_fraction`: q0.01=0.239033, q0.05=0.247446, q0.25=0.258937, q0.5=0.27011, q0.75=0.279803, q0.95=0.288891, q0.99=0.293245
- `SPY\|year_2020\|first\|all\|all` `next_zero_fraction`: q0.01=0.60122, q0.05=0.607946, q0.25=0.62453, q0.5=0.636387, q0.75=0.653043, q0.95=0.673378, q0.99=0.682504
- `SPY\|year_2020\|first\|all\|all` `next_negative_fraction`: q0.01=0.0770319, q0.05=0.0778478, q0.25=0.0845643, q0.5=0.0895753, q0.75=0.0983763, q0.95=0.11523, q0.99=0.118685
- `SPY\|year_2020\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0181269, q0.75=0.0215759, q0.95=0.0398267, q0.99=0.0513353
- `SPY\|year_2020\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|year_2020\|first\|all\|all` `first_observed_fraction`: q0.01=0.0020172, q0.05=0.00285273, q0.25=0.00997311, q0.5=0.0210843, q0.75=0.0251762, q0.95=0.0330037, q0.99=0.0428819
- `SPY\|year_2020\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|year_2020\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0.00204173, q0.05=0.00297537, q0.25=0.0103494, q0.5=0.0213764, q0.75=0.0256027, q0.95=0.047073, q0.99=0.0491936
- `SPY\|year_2020\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|year_2020\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|year_2020\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|year_2020\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|year_2020\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|year_2020\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|year_2020\|last\|all\|all` `oi_level_date_mean`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|year_2020\|last\|all\|all` `oi_zero_fraction`: q0.01=0.213309, q0.05=0.213543, q0.25=0.220173, q0.5=0.226255, q0.75=0.232224, q0.95=0.241828, q0.99=0.248734
- `SPY\|year_2020\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25358.8, q0.05=25403.2, q0.25=25754.4, q0.5=26279.6, q0.75=26480.8, q0.95=27503.9, q0.99=27604.7
- `SPY\|year_2020\|last\|all\|all` `coverage_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|year_2020\|last\|all\|all` `missing_oi_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|last\|all\|all` `oi_mass`: q0.01=1.68104e+07, q0.05=1.69687e+07, q0.25=1.7948e+07, q0.5=1.89169e+07, q0.75=1.97475e+07, q0.95=2.09327e+07, q0.99=2.10724e+07
- `SPY\|year_2020\|last\|all\|all` `oi_width`: q0.01=7352.7, q0.05=7363.5, q0.25=7561.5, q0.5=7744, q0.75=7812, q0.95=7973, q0.99=7994.6
- `SPY\|year_2020\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|last\|all\|all` `common_support_first`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|year_2020\|last\|all\|all` `common_support_last`: q0.01=2167.92, q0.05=2179.23, q0.25=2397.36, q0.5=2466.28, q0.75=2539.38, q0.95=2696.3, q0.99=2705.22
- `SPY\|year_2020\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|last\|all\|all` `next_delta`: q0.01=-17.7783, q0.05=30.5802, q0.25=76.1307, q0.5=83.2864, q0.75=93.7372, q0.95=102.644, q0.99=110.18
- `SPY\|year_2020\|last\|all\|all` `next_abs_delta`: q0.01=93.1484, q0.05=98.885, q0.25=123.217, q0.5=147.824, q0.75=156.22, q0.95=219.537, q0.99=306.412
- `SPY\|year_2020\|last\|all\|all` `next_positive_fraction`: q0.01=0.239033, q0.05=0.247446, q0.25=0.258937, q0.5=0.27011, q0.75=0.279803, q0.95=0.288891, q0.99=0.293245
- `SPY\|year_2020\|last\|all\|all` `next_zero_fraction`: q0.01=0.60122, q0.05=0.607946, q0.25=0.62453, q0.5=0.636387, q0.75=0.653043, q0.95=0.673378, q0.99=0.682504
- `SPY\|year_2020\|last\|all\|all` `next_negative_fraction`: q0.01=0.0770319, q0.05=0.0778478, q0.25=0.0845643, q0.5=0.0895753, q0.75=0.0983763, q0.95=0.11523, q0.99=0.118685
- `SPY\|year_2020\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0.0181269, q0.75=0.0215759, q0.95=0.0398267, q0.99=0.0513353
- `SPY\|year_2020\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|year_2020\|last\|all\|all` `first_observed_fraction`: q0.01=0.0020172, q0.05=0.00285273, q0.25=0.00997311, q0.5=0.0210843, q0.75=0.0251762, q0.95=0.0330037, q0.99=0.0428819
- `SPY\|year_2020\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `SPY\|year_2020\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0.00204173, q0.05=0.00297537, q0.25=0.0103494, q0.5=0.0213764, q0.75=0.0256027, q0.95=0.047073, q0.99=0.0491936
- `SPY\|year_2020\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|year_2020\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|year_2020\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|year_2020\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `SPY\|year_2020\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.94931, q0.05=0.952487, q0.25=0.973817, q0.5=0.978357, q0.75=0.989456, q0.95=0.997016, q0.99=0.997928
- `SPY\|year_2020\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `SPY\|year_2020\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0.00207168, q0.05=0.00298418, q0.25=0.0105437, q0.5=0.0216429, q0.75=0.0261826, q0.95=0.0475132, q0.99=0.0506903
- `VIX\|all_period\|first\|CALL\|all` `oi_level_date_mean`: q0.01=12162.7, q0.05=12852.7, q0.25=13957.1, q0.5=15926.7, q0.75=17003, q0.95=17551.7, q0.99=17698.3
- `VIX\|all_period\|first\|CALL\|all` `oi_mass`: q0.01=3.43691e+06, q0.05=3.52385e+06, q0.25=3.8274e+06, q0.5=4.28586e+06, q0.75=4.9032e+06, q0.95=5.68184e+06, q0.99=5.74744e+06
- `VIX\|all_period\|first\|CALL\|all` `oi_width`: q0.01=220, q0.05=220, q0.25=220, q0.5=325, q0.75=325, q0.95=325, q0.99=325
- `VIX\|all_period\|first\|PUT\|all` `oi_level_date_mean`: q0.01=4626.45, q0.05=4884.23, q0.25=6158.74, q0.5=6293.99, q0.75=7660.59, q0.95=8138.29, q0.99=8230.96
- `VIX\|all_period\|first\|PUT\|all` `oi_mass`: q0.01=1.5015e+06, q0.05=1.57692e+06, q0.25=1.70406e+06, q0.5=1.86572e+06, q0.75=2.02404e+06, q0.95=2.07028e+06, q0.99=2.10238e+06
- `VIX\|all_period\|first\|PUT\|all` `oi_width`: q0.01=220, q0.05=220, q0.25=220, q0.5=325, q0.75=325, q0.95=325, q0.99=325
- `VIX\|all_period\|first\|all\|0` `oi_level_date_mean`: q0.01=35463.3, q0.05=35463.3, q0.25=35463.3, q0.5=35463.3, q0.75=35463.3, q0.95=35463.3, q0.99=35463.3
- `VIX\|all_period\|first\|all\|0` `oi_mass`: q0.01=2.83706e+06, q0.05=2.83706e+06, q0.25=2.83706e+06, q0.5=2.83706e+06, q0.75=2.83706e+06, q0.95=2.83706e+06, q0.99=2.83706e+06
- `VIX\|all_period\|first\|all\|0` `oi_width`: q0.01=80, q0.05=80, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|first\|all\|1` `oi_level_date_mean`: q0.01=35437.6, q0.05=35437.6, q0.25=35437.6, q0.5=35437.6, q0.75=35437.6, q0.95=35437.6, q0.99=35437.6
- `VIX\|all_period\|first\|all\|1` `oi_mass`: q0.01=2.83501e+06, q0.05=2.83501e+06, q0.25=2.83501e+06, q0.5=2.83501e+06, q0.75=2.83501e+06, q0.95=2.83501e+06, q0.99=2.83501e+06
- `VIX\|all_period\|first\|all\|1` `oi_width`: q0.01=80, q0.05=80, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|first\|all\|2-7` `oi_level_date_mean`: q0.01=34433.2, q0.05=34484.3, q0.25=34739.8, q0.5=35059.3, q0.75=35121.9, q0.95=35172, q0.99=35182
- `VIX\|all_period\|first\|all\|2-7` `oi_mass`: q0.01=2.75465e+06, q0.05=2.75874e+06, q0.25=2.77919e+06, q0.5=2.80474e+06, q0.75=2.80975e+06, q0.95=2.81376e+06, q0.99=2.81456e+06
- `VIX\|all_period\|first\|all\|2-7` `oi_width`: q0.01=80, q0.05=80, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|first\|all\|31-60` `oi_level_date_mean`: q0.01=13389.5, q0.05=13773.8, q0.25=15129.5, q0.5=17744.3, q0.75=20427, q0.95=23296.1, q0.99=24509
- `VIX\|all_period\|first\|all\|31-60` `oi_mass`: q0.01=1.07116e+06, q0.05=1.10191e+06, q0.25=1.21036e+06, q0.5=1.33204e+06, q0.75=1.63416e+06, q0.95=1.86369e+06, q0.99=1.96072e+06
- `VIX\|all_period\|first\|all\|31-60` `oi_width`: q0.01=70, q0.05=70, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|first\|all\|61+` `oi_level_date_mean`: q0.01=2689.6, q0.05=2757.98, q0.25=3601.05, q0.5=4450.71, q0.75=5293.59, q0.95=5861.62, q0.99=6018.38
- `VIX\|all_period\|first\|all\|61+` `oi_mass`: q0.01=1.17473e+06, q0.05=1.19238e+06, q0.25=1.38432e+06, q0.5=1.65954e+06, q0.75=1.96422e+06, q0.95=2.26607e+06, q0.99=2.31528e+06
- `VIX\|all_period\|first\|all\|61+` `oi_width`: q0.01=280, q0.05=280, q0.25=280, q0.5=420, q0.75=490, q0.95=490, q0.99=490
- `VIX\|all_period\|first\|all\|8-30` `oi_level_date_mean`: q0.01=29111.1, q0.05=30083.5, q0.25=32050.1, q0.5=33817.1, q0.75=34314.8, q0.95=34705.8, q0.99=34783.9
- `VIX\|all_period\|first\|all\|8-30` `oi_mass`: q0.01=2.32889e+06, q0.05=2.40668e+06, q0.25=2.56401e+06, q0.5=2.70537e+06, q0.75=2.74519e+06, q0.95=2.77646e+06, q0.99=2.78271e+06
- `VIX\|all_period\|first\|all\|8-30` `oi_width`: q0.01=80, q0.05=80, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|first\|all\|all` `oi_level_date_mean`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|all_period\|first\|all\|all` `oi_zero_fraction`: q0.01=0.145795, q0.05=0.147159, q0.25=0.15625, q0.5=0.28, q0.75=0.309615, q0.95=0.363846, q0.99=0.380462
- `VIX\|all_period\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261.5, q0.75=25262, q0.95=25877.8, q0.99=27355.7
- `VIX\|all_period\|first\|all\|all` `oi_mass`: q0.01=5.0554e+06, q0.05=5.18291e+06, q0.25=5.47908e+06, q0.5=6.21807e+06, q0.75=6.937e+06, q0.95=7.59801e+06, q0.99=7.73152e+06
- `VIX\|all_period\|first\|all\|all` `oi_width`: q0.01=440, q0.05=440, q0.25=440, q0.5=650, q0.75=650, q0.95=650, q0.99=650
- `VIX\|all_period\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|first\|all\|all` `common_support_first`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|all_period\|first\|all\|all` `common_support_last`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|all_period\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|first\|all\|all` `next_delta`: q0.01=-475.166, q0.05=-44.9308, q0.25=236.072, q0.5=390.392, q0.75=443.509, q0.95=644.087, q0.99=654.411
- `VIX\|all_period\|first\|all\|all` `next_abs_delta`: q0.01=265.765, q0.05=316.579, q0.25=448.727, q0.5=521.755, q0.75=538.448, q0.95=1034.21, q0.99=1231.45
- `VIX\|all_period\|first\|all\|all` `next_positive_fraction`: q0.01=0.254369, q0.05=0.281077, q0.25=0.309231, q0.5=0.324561, q0.75=0.364773, q0.95=0.413805, q0.99=0.450034
- `VIX\|all_period\|first\|all\|all` `next_zero_fraction`: q0.01=0.472925, q0.05=0.473715, q0.25=0.5375, q0.5=0.607018, q0.75=0.626154, q0.95=0.642308, q0.99=0.646615
- `VIX\|all_period\|first\|all\|all` `next_negative_fraction`: q0.01=0.0564615, q0.05=0.0607692, q0.25=0.0679371, q0.5=0.0723077, q0.75=0.102308, q0.95=0.125349, q0.99=0.130242
- `VIX\|all_period\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0328767, q0.99=0.0942466
- `VIX\|all_period\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|all_period\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.162558, q0.99=0.261435
- `VIX\|all_period\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|all_period\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|all_period\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|all_period\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|all_period\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|all_period\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|all_period\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|all_period\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|all_period\|first\|all\|expired` `oi_level_date_mean`: q0.01=27994.1, q0.05=27994.1, q0.25=27994.1, q0.5=27994.1, q0.75=27994.1, q0.95=27994.1, q0.99=27994.1
- `VIX\|all_period\|first\|all\|expired` `oi_mass`: q0.01=2.23953e+06, q0.05=2.23953e+06, q0.25=2.23953e+06, q0.5=2.23953e+06, q0.75=2.23953e+06, q0.95=2.23953e+06, q0.99=2.23953e+06
- `VIX\|all_period\|first\|all\|expired` `oi_width`: q0.01=80, q0.05=80, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|last\|CALL\|all` `oi_level_date_mean`: q0.01=12162.7, q0.05=12852.7, q0.25=13957.1, q0.5=15926.7, q0.75=17003, q0.95=17551.7, q0.99=17698.3
- `VIX\|all_period\|last\|CALL\|all` `oi_mass`: q0.01=3.43691e+06, q0.05=3.52385e+06, q0.25=3.8274e+06, q0.5=4.28586e+06, q0.75=4.9032e+06, q0.95=5.68184e+06, q0.99=5.74744e+06
- `VIX\|all_period\|last\|CALL\|all` `oi_width`: q0.01=220, q0.05=220, q0.25=220, q0.5=325, q0.75=325, q0.95=325, q0.99=325
- `VIX\|all_period\|last\|PUT\|all` `oi_level_date_mean`: q0.01=4626.45, q0.05=4884.23, q0.25=6158.74, q0.5=6293.99, q0.75=7660.59, q0.95=8138.29, q0.99=8230.96
- `VIX\|all_period\|last\|PUT\|all` `oi_mass`: q0.01=1.5015e+06, q0.05=1.57692e+06, q0.25=1.70406e+06, q0.5=1.86572e+06, q0.75=2.02404e+06, q0.95=2.07028e+06, q0.99=2.10238e+06
- `VIX\|all_period\|last\|PUT\|all` `oi_width`: q0.01=220, q0.05=220, q0.25=220, q0.5=325, q0.75=325, q0.95=325, q0.99=325
- `VIX\|all_period\|last\|all\|0` `oi_level_date_mean`: q0.01=35463.3, q0.05=35463.3, q0.25=35463.3, q0.5=35463.3, q0.75=35463.3, q0.95=35463.3, q0.99=35463.3
- `VIX\|all_period\|last\|all\|0` `oi_mass`: q0.01=2.83706e+06, q0.05=2.83706e+06, q0.25=2.83706e+06, q0.5=2.83706e+06, q0.75=2.83706e+06, q0.95=2.83706e+06, q0.99=2.83706e+06
- `VIX\|all_period\|last\|all\|0` `oi_width`: q0.01=80, q0.05=80, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|last\|all\|1` `oi_level_date_mean`: q0.01=35437.6, q0.05=35437.6, q0.25=35437.6, q0.5=35437.6, q0.75=35437.6, q0.95=35437.6, q0.99=35437.6
- `VIX\|all_period\|last\|all\|1` `oi_mass`: q0.01=2.83501e+06, q0.05=2.83501e+06, q0.25=2.83501e+06, q0.5=2.83501e+06, q0.75=2.83501e+06, q0.95=2.83501e+06, q0.99=2.83501e+06
- `VIX\|all_period\|last\|all\|1` `oi_width`: q0.01=80, q0.05=80, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|last\|all\|2-7` `oi_level_date_mean`: q0.01=34433.2, q0.05=34484.3, q0.25=34739.8, q0.5=35059.3, q0.75=35121.9, q0.95=35172, q0.99=35182
- `VIX\|all_period\|last\|all\|2-7` `oi_mass`: q0.01=2.75465e+06, q0.05=2.75874e+06, q0.25=2.77919e+06, q0.5=2.80474e+06, q0.75=2.80975e+06, q0.95=2.81376e+06, q0.99=2.81456e+06
- `VIX\|all_period\|last\|all\|2-7` `oi_width`: q0.01=80, q0.05=80, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|last\|all\|31-60` `oi_level_date_mean`: q0.01=13389.5, q0.05=13773.8, q0.25=15129.5, q0.5=17744.3, q0.75=20427, q0.95=23296.1, q0.99=24509
- `VIX\|all_period\|last\|all\|31-60` `oi_mass`: q0.01=1.07116e+06, q0.05=1.10191e+06, q0.25=1.21036e+06, q0.5=1.33204e+06, q0.75=1.63416e+06, q0.95=1.86369e+06, q0.99=1.96072e+06
- `VIX\|all_period\|last\|all\|31-60` `oi_width`: q0.01=70, q0.05=70, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|last\|all\|61+` `oi_level_date_mean`: q0.01=2689.6, q0.05=2757.98, q0.25=3601.05, q0.5=4450.71, q0.75=5293.59, q0.95=5861.62, q0.99=6018.38
- `VIX\|all_period\|last\|all\|61+` `oi_mass`: q0.01=1.17473e+06, q0.05=1.19238e+06, q0.25=1.38432e+06, q0.5=1.65954e+06, q0.75=1.96422e+06, q0.95=2.26607e+06, q0.99=2.31528e+06
- `VIX\|all_period\|last\|all\|61+` `oi_width`: q0.01=280, q0.05=280, q0.25=280, q0.5=420, q0.75=490, q0.95=490, q0.99=490
- `VIX\|all_period\|last\|all\|8-30` `oi_level_date_mean`: q0.01=29111.1, q0.05=30083.5, q0.25=32050.1, q0.5=33817.1, q0.75=34314.8, q0.95=34705.8, q0.99=34783.9
- `VIX\|all_period\|last\|all\|8-30` `oi_mass`: q0.01=2.32889e+06, q0.05=2.40668e+06, q0.25=2.56401e+06, q0.5=2.70537e+06, q0.75=2.74519e+06, q0.95=2.77646e+06, q0.99=2.78271e+06
- `VIX\|all_period\|last\|all\|8-30` `oi_width`: q0.01=80, q0.05=80, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|all_period\|last\|all\|all` `oi_level_date_mean`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|all_period\|last\|all\|all` `oi_zero_fraction`: q0.01=0.145795, q0.05=0.147159, q0.25=0.15625, q0.5=0.28, q0.75=0.309615, q0.95=0.363846, q0.99=0.380462
- `VIX\|all_period\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261.5, q0.75=25262, q0.95=25877.8, q0.99=27355.7
- `VIX\|all_period\|last\|all\|all` `oi_mass`: q0.01=5.0554e+06, q0.05=5.18291e+06, q0.25=5.47908e+06, q0.5=6.21807e+06, q0.75=6.937e+06, q0.95=7.59801e+06, q0.99=7.73152e+06
- `VIX\|all_period\|last\|all\|all` `oi_width`: q0.01=440, q0.05=440, q0.25=440, q0.5=650, q0.75=650, q0.95=650, q0.99=650
- `VIX\|all_period\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|last\|all\|all` `common_support_first`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|all_period\|last\|all\|all` `common_support_last`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|all_period\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|last\|all\|all` `next_delta`: q0.01=-475.166, q0.05=-44.9308, q0.25=236.072, q0.5=390.392, q0.75=443.509, q0.95=644.087, q0.99=654.411
- `VIX\|all_period\|last\|all\|all` `next_abs_delta`: q0.01=265.765, q0.05=316.579, q0.25=448.727, q0.5=521.755, q0.75=538.448, q0.95=1034.21, q0.99=1231.45
- `VIX\|all_period\|last\|all\|all` `next_positive_fraction`: q0.01=0.254369, q0.05=0.281077, q0.25=0.309231, q0.5=0.324561, q0.75=0.364773, q0.95=0.413805, q0.99=0.450034
- `VIX\|all_period\|last\|all\|all` `next_zero_fraction`: q0.01=0.472925, q0.05=0.473715, q0.25=0.5375, q0.5=0.607018, q0.75=0.626154, q0.95=0.642308, q0.99=0.646615
- `VIX\|all_period\|last\|all\|all` `next_negative_fraction`: q0.01=0.0564615, q0.05=0.0607692, q0.25=0.0679371, q0.5=0.0723077, q0.75=0.102308, q0.95=0.125349, q0.99=0.130242
- `VIX\|all_period\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0328767, q0.99=0.0942466
- `VIX\|all_period\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|all_period\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.162558, q0.99=0.261435
- `VIX\|all_period\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|all_period\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|all_period\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|all_period\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|all_period\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|all_period\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|all_period\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|all_period\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|all_period\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|all_period\|last\|all\|expired` `oi_level_date_mean`: q0.01=27994.1, q0.05=27994.1, q0.25=27994.1, q0.5=27994.1, q0.75=27994.1, q0.95=27994.1, q0.99=27994.1
- `VIX\|all_period\|last\|all\|expired` `oi_mass`: q0.01=2.23953e+06, q0.05=2.23953e+06, q0.25=2.23953e+06, q0.5=2.23953e+06, q0.75=2.23953e+06, q0.95=2.23953e+06, q0.99=2.23953e+06
- `VIX\|all_period\|last\|all\|expired` `oi_width`: q0.01=80, q0.05=80, q0.25=80, q0.5=80, q0.75=80, q0.95=80, q0.99=80
- `VIX\|stage_confirmation\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `VIX\|stage_confirmation\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `VIX\|stage_development\|first\|all\|all`: all metrics undefined; missing_date_count=0
- `VIX\|stage_development\|last\|all\|all`: all metrics undefined; missing_date_count=0
- `VIX\|stage_training\|first\|all\|all` `oi_level_date_mean`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|stage_training\|first\|all\|all` `oi_zero_fraction`: q0.01=0.145795, q0.05=0.147159, q0.25=0.15625, q0.5=0.28, q0.75=0.309615, q0.95=0.363846, q0.99=0.380462
- `VIX\|stage_training\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261.5, q0.75=25262, q0.95=25877.8, q0.99=27355.7
- `VIX\|stage_training\|first\|all\|all` `oi_mass`: q0.01=5.0554e+06, q0.05=5.18291e+06, q0.25=5.47908e+06, q0.5=6.21807e+06, q0.75=6.937e+06, q0.95=7.59801e+06, q0.99=7.73152e+06
- `VIX\|stage_training\|first\|all\|all` `oi_width`: q0.01=440, q0.05=440, q0.25=440, q0.5=650, q0.75=650, q0.95=650, q0.99=650
- `VIX\|stage_training\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|first\|all\|all` `common_support_first`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|stage_training\|first\|all\|all` `common_support_last`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|stage_training\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|first\|all\|all` `next_delta`: q0.01=-475.166, q0.05=-44.9308, q0.25=236.072, q0.5=390.392, q0.75=443.509, q0.95=644.087, q0.99=654.411
- `VIX\|stage_training\|first\|all\|all` `next_abs_delta`: q0.01=265.765, q0.05=316.579, q0.25=448.727, q0.5=521.755, q0.75=538.448, q0.95=1034.21, q0.99=1231.45
- `VIX\|stage_training\|first\|all\|all` `next_positive_fraction`: q0.01=0.254369, q0.05=0.281077, q0.25=0.309231, q0.5=0.324561, q0.75=0.364773, q0.95=0.413805, q0.99=0.450034
- `VIX\|stage_training\|first\|all\|all` `next_zero_fraction`: q0.01=0.472925, q0.05=0.473715, q0.25=0.5375, q0.5=0.607018, q0.75=0.626154, q0.95=0.642308, q0.99=0.646615
- `VIX\|stage_training\|first\|all\|all` `next_negative_fraction`: q0.01=0.0564615, q0.05=0.0607692, q0.25=0.0679371, q0.5=0.0723077, q0.75=0.102308, q0.95=0.125349, q0.99=0.130242
- `VIX\|stage_training\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0328767, q0.99=0.0942466
- `VIX\|stage_training\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|stage_training\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.162558, q0.99=0.261435
- `VIX\|stage_training\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|stage_training\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|stage_training\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|stage_training\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|stage_training\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|stage_training\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|stage_training\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|stage_training\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|stage_training\|last\|all\|all` `oi_level_date_mean`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|stage_training\|last\|all\|all` `oi_zero_fraction`: q0.01=0.145795, q0.05=0.147159, q0.25=0.15625, q0.5=0.28, q0.75=0.309615, q0.95=0.363846, q0.99=0.380462
- `VIX\|stage_training\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261.5, q0.75=25262, q0.95=25877.8, q0.99=27355.7
- `VIX\|stage_training\|last\|all\|all` `oi_mass`: q0.01=5.0554e+06, q0.05=5.18291e+06, q0.25=5.47908e+06, q0.5=6.21807e+06, q0.75=6.937e+06, q0.95=7.59801e+06, q0.99=7.73152e+06
- `VIX\|stage_training\|last\|all\|all` `oi_width`: q0.01=440, q0.05=440, q0.25=440, q0.5=650, q0.75=650, q0.95=650, q0.99=650
- `VIX\|stage_training\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|last\|all\|all` `common_support_first`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|stage_training\|last\|all\|all` `common_support_last`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|stage_training\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|last\|all\|all` `next_delta`: q0.01=-475.166, q0.05=-44.9308, q0.25=236.072, q0.5=390.392, q0.75=443.509, q0.95=644.087, q0.99=654.411
- `VIX\|stage_training\|last\|all\|all` `next_abs_delta`: q0.01=265.765, q0.05=316.579, q0.25=448.727, q0.5=521.755, q0.75=538.448, q0.95=1034.21, q0.99=1231.45
- `VIX\|stage_training\|last\|all\|all` `next_positive_fraction`: q0.01=0.254369, q0.05=0.281077, q0.25=0.309231, q0.5=0.324561, q0.75=0.364773, q0.95=0.413805, q0.99=0.450034
- `VIX\|stage_training\|last\|all\|all` `next_zero_fraction`: q0.01=0.472925, q0.05=0.473715, q0.25=0.5375, q0.5=0.607018, q0.75=0.626154, q0.95=0.642308, q0.99=0.646615
- `VIX\|stage_training\|last\|all\|all` `next_negative_fraction`: q0.01=0.0564615, q0.05=0.0607692, q0.25=0.0679371, q0.5=0.0723077, q0.75=0.102308, q0.95=0.125349, q0.99=0.130242
- `VIX\|stage_training\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0328767, q0.99=0.0942466
- `VIX\|stage_training\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|stage_training\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.162558, q0.99=0.261435
- `VIX\|stage_training\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|stage_training\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|stage_training\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|stage_training\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|stage_training\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|stage_training\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|stage_training\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|stage_training\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|stage_training\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|year_2020\|first\|all\|all` `oi_level_date_mean`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|year_2020\|first\|all\|all` `oi_zero_fraction`: q0.01=0.145795, q0.05=0.147159, q0.25=0.15625, q0.5=0.28, q0.75=0.309615, q0.95=0.363846, q0.99=0.380462
- `VIX\|year_2020\|first\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261.5, q0.75=25262, q0.95=25877.8, q0.99=27355.7
- `VIX\|year_2020\|first\|all\|all` `oi_mass`: q0.01=5.0554e+06, q0.05=5.18291e+06, q0.25=5.47908e+06, q0.5=6.21807e+06, q0.75=6.937e+06, q0.95=7.59801e+06, q0.99=7.73152e+06
- `VIX\|year_2020\|first\|all\|all` `oi_width`: q0.01=440, q0.05=440, q0.25=440, q0.5=650, q0.75=650, q0.95=650, q0.99=650
- `VIX\|year_2020\|first\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|first\|all\|all` `common_support_first`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|year_2020\|first\|all\|all` `common_support_last`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|year_2020\|first\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|first\|all\|all` `next_delta`: q0.01=-475.166, q0.05=-44.9308, q0.25=236.072, q0.5=390.392, q0.75=443.509, q0.95=644.087, q0.99=654.411
- `VIX\|year_2020\|first\|all\|all` `next_abs_delta`: q0.01=265.765, q0.05=316.579, q0.25=448.727, q0.5=521.755, q0.75=538.448, q0.95=1034.21, q0.99=1231.45
- `VIX\|year_2020\|first\|all\|all` `next_positive_fraction`: q0.01=0.254369, q0.05=0.281077, q0.25=0.309231, q0.5=0.324561, q0.75=0.364773, q0.95=0.413805, q0.99=0.450034
- `VIX\|year_2020\|first\|all\|all` `next_zero_fraction`: q0.01=0.472925, q0.05=0.473715, q0.25=0.5375, q0.5=0.607018, q0.75=0.626154, q0.95=0.642308, q0.99=0.646615
- `VIX\|year_2020\|first\|all\|all` `next_negative_fraction`: q0.01=0.0564615, q0.05=0.0607692, q0.25=0.0679371, q0.5=0.0723077, q0.75=0.102308, q0.95=0.125349, q0.99=0.130242
- `VIX\|year_2020\|first\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|first\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0328767, q0.99=0.0942466
- `VIX\|year_2020\|first\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|year_2020\|first\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.162558, q0.99=0.261435
- `VIX\|year_2020\|first\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|year_2020\|first\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|first\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|first\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|year_2020\|first\|all\|all` `asof_0930_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|year_2020\|first\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|first\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|year_2020\|first\|all\|all` `asof_1000_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|year_2020\|first\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|first\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|year_2020\|first\|all\|all` `asof_1500_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|year_2020\|first\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|first\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|year_2020\|last\|all\|all` `oi_level_date_mean`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|year_2020\|last\|all\|all` `oi_zero_fraction`: q0.01=0.145795, q0.05=0.147159, q0.25=0.15625, q0.5=0.28, q0.75=0.309615, q0.95=0.363846, q0.99=0.380462
- `VIX\|year_2020\|last\|all\|all` `report_seconds_after_eastern_midnight`: q0.01=25261, q0.05=25261, q0.25=25261, q0.5=25261.5, q0.75=25262, q0.95=25877.8, q0.99=27355.7
- `VIX\|year_2020\|last\|all\|all` `oi_mass`: q0.01=5.0554e+06, q0.05=5.18291e+06, q0.25=5.47908e+06, q0.5=6.21807e+06, q0.75=6.937e+06, q0.95=7.59801e+06, q0.99=7.73152e+06
- `VIX\|year_2020\|last\|all\|all` `oi_width`: q0.01=440, q0.05=440, q0.25=440, q0.5=650, q0.75=650, q0.95=650, q0.99=650
- `VIX\|year_2020\|last\|all\|all` `update_candidate_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|last\|all\|all` `common_support_first`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|year_2020\|last\|all\|all` `common_support_last`: q0.01=8455.11, q0.05=9171.27, q0.25=10082.9, q0.5=11390.2, q0.75=11980.9, q0.95=12674.6, q0.99=12832.8
- `VIX\|year_2020\|last\|all\|all` `common_support_first_minus_last`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|last\|all\|all` `next_delta`: q0.01=-475.166, q0.05=-44.9308, q0.25=236.072, q0.5=390.392, q0.75=443.509, q0.95=644.087, q0.99=654.411
- `VIX\|year_2020\|last\|all\|all` `next_abs_delta`: q0.01=265.765, q0.05=316.579, q0.25=448.727, q0.5=521.755, q0.75=538.448, q0.95=1034.21, q0.99=1231.45
- `VIX\|year_2020\|last\|all\|all` `next_positive_fraction`: q0.01=0.254369, q0.05=0.281077, q0.25=0.309231, q0.5=0.324561, q0.75=0.364773, q0.95=0.413805, q0.99=0.450034
- `VIX\|year_2020\|last\|all\|all` `next_zero_fraction`: q0.01=0.472925, q0.05=0.473715, q0.25=0.5375, q0.5=0.607018, q0.75=0.626154, q0.95=0.642308, q0.99=0.646615
- `VIX\|year_2020\|last\|all\|all` `next_negative_fraction`: q0.01=0.0564615, q0.05=0.0607692, q0.25=0.0679371, q0.5=0.0723077, q0.75=0.102308, q0.95=0.125349, q0.99=0.130242
- `VIX\|year_2020\|last\|all\|all` `censor_missing_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|last\|all\|all` `censor_expired_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.0328767, q0.99=0.0942466
- `VIX\|year_2020\|last\|all\|all` `censor_boundary_fraction`: q0.01=1, q0.05=1, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|year_2020\|last\|all\|all` `first_observed_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.162558, q0.99=0.261435
- `VIX\|year_2020\|last\|all\|all` `position_mapping_agree_fraction`: q0.01=0.15, q0.05=0.75, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|year_2020\|last\|all\|all` `event_local_mismatch_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|last\|all\|all` `future_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|last\|all\|all` `late_clock_flag_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|year_2020\|last\|all\|all` `asof_0930_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|year_2020\|last\|all\|all` `asof_0930_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|last\|all\|all` `asof_0930_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|year_2020\|last\|all\|all` `asof_1000_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|year_2020\|last\|all\|all` `asof_1000_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|last\|all\|all` `asof_1000_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655
- `VIX\|year_2020\|last\|all\|all` `asof_1500_available_fraction`: q0.01=0.956034, q0.05=0.987069, q0.25=1, q0.5=1, q0.75=1, q0.95=1, q0.99=1
- `VIX\|year_2020\|last\|all\|all` `asof_1500_stale_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0, q0.99=0
- `VIX\|year_2020\|last\|all\|all` `asof_1500_future_today_fraction`: q0.01=0, q0.05=0, q0.25=0, q0.5=0, q0.75=0, q0.95=0.012931, q0.99=0.0439655

Statistics version: options-oi-report-lifecycle-statistics-v2
