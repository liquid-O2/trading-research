# Auction/flow window, formation and event-timing statistics

Descriptive formation-length, availability-delay, forward-label and scheduled-event timing measurements. This does not complete the auction/flow family, select a source or clock winner, or claim causal news impact.

- family_complete: false
- complete_family_statistics: false
- population_source_windows: 3589
- processed_source_windows: 1
- unavailable_source_windows: 0
- feature_rows: 1152
- label_rows: 3456
- eligible_feature_rows: 0
- eligible_joined_rows: 0
- censored_feature_rows: 48
- unassigned_stage_rows: 48
- out_of_primary_year_rows: 1104
- independent_economic_dates: 2
- reused_partitions: 0
- new_partitions: 1
- selected_partitions: 1
- declared_partitions: 13
- cpu_seconds: 0.4317457400000002
- output_bytes: 60418

Date means give one weight per economic date. Multiple cuts or overlapping windows on the same date are dependent observations, not extra independent dates. Monthly and weekly acquisitions keep separate primary inference. Sample quantiles below are the equal-weight date-mean distribution; event mean/min/max stay separate.

Price units are raw ticks (0.25 index point). Variance is ticks squared. Cohort fractions are dimensionless. Volume intensity is contracts/second. CVD, OFI and signed flow are contracts. Labels store absolute future prices; displacements are derived from each feature reference. A complete quiet window is no-new-trade = 1 with a null price, not a zero return. Missing coverage stays missing.

True CVD/OFI path range uses high-low, never close extrema. Hard cohort volumes overlap and are not a partition. Standing and pressure metrics use their own eligible masks.

Directional concordance is the paired observed frequency that sign(formation all-CVD close) matches sign(terminal return), only when both signs are nonzero. Zero-past and zero-future are separate denominators from their own validities. This is not model accuracy or predictive gain.

Scheduled event labels are retrospective: known_at is NULL and causal_feature_eligible is false. Dates without an event record are unknown coverage. Events with no eligible receiver or no nearby window remain in the event denominator. Global no-receiver counts an event once if no selected relevant partition had a receiver.

## Source, year and stage coverage

| collection | root | year | stage | intended_dates | groups |
|---|---|---|---|---|---|
| monthly_acquisitions | ES | 2021 | training | 0 | 0 |
| monthly_acquisitions | ES | 2021 | development | 0 | 0 |
| monthly_acquisitions | ES | 2021 | calibration | 0 | 0 |
| monthly_acquisitions | ES | 2021 | confirmation | 0 | 0 |
| monthly_acquisitions | ES | 2021 | unassigned | 365 | 0 |

## Event coverage

- source_event_rows: 4755
- unique_semantic_events: 925
- events_with_receiver: 0
- events_without_receiver: 925
- events_without_window: 925
- date_only_events: 220
- unknown_event_coverage_dates: 271
- inconsistent_event_clock_rows: 2

## Representative feature measurements

| kind | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | metric | unit | date-mean | event-mean | dates | events | missing | 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined |

## Representative delay contrasts

| kind | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | metric | unit | date-mean | event-mean | dates | events | missing | 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined |

## Representative formation contrasts

| kind | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | metric | unit | date-mean | event-mean | dates | events | missing | 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined |

## Representative event outcomes

| kind | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | metric | unit | date-mean | event-mean | dates | events | missing | 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined |

## All retained groups

| kind | collection | root | year | stage | session | formation | latency | horizon | event_type | bucket | contrast | dates | events | undefined |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | undefined | true |

## Full result references

- partitions: [{'path': '/workspace/trading-research/reports/auction-flow-runs/9c23254897fa93ff20a30214a7e73ca1adb4baf1c6d3b24bc23a3b464ee2939b/outputs/window-statistics-shard-01/window-000-monthly_acquisitions-ES-2021-partition.json', 'sha256': 'ed0909e6ab7d6ffa967f2c7d7c8d775d484e73cb3414a6c0ec5df76a3c5cbaa8', 'size_bytes': 13777, 'kind': 'auction_flow_window_partition_v1'}]
- groups: [{'path': '/workspace/trading-research/reports/auction-flow-runs/9c23254897fa93ff20a30214a7e73ca1adb4baf1c6d3b24bc23a3b464ee2939b/outputs/window-statistics-shard-01/window-000-monthly_acquisitions-ES-2021-groups.json', 'sha256': 'd0cf854a5430c6a00d9cf8bce4500ecab03d523489cb46524b295d52df2375a6', 'size_bytes': 9996, 'kind': 'auction_flow_window_group_statistics_v1'}]
- denominators: [{'version': 'auction-flow-bounded-parquet-storage-v1', 'series': 'window-000-monthly_acquisitions-ES-2021-date-metrics', 'rows': 0, 'row_groups': 0, 'encoding': 'plain', 'compression': 'zstd-level-3', 'schema': 'group_kind: string\nsource_collection: string\nroot: string\nyear: int64\nstage: string\nsession: string\nformation_minutes: int64\nlatency_ns: int64\nhorizon_kind: string\nhorizon_minutes: int64\nevent_type: string\ntime_precision: string\nstatus: string\nrelative_bucket: string\ncontrast: string\nmetric: string\neconomic_date: string\nobservation_count: int64\nsum: double\nmean: double', 'files': [], 'compared_values': 0, 'roundtrip_exact': True, 'cpu_seconds': 0.0, 'serialized_bytes': 0}]
- paired: [{'path': '/workspace/trading-research/reports/auction-flow-runs/9c23254897fa93ff20a30214a7e73ca1adb4baf1c6d3b24bc23a3b464ee2939b/outputs/window-statistics-shard-01/window-000-monthly_acquisitions-ES-2021-paired.json', 'sha256': '054d8baaecf23ddeb3ab1d28b8e609b121aae83f5cdec9f295aa1f7d02dc287d', 'size_bytes': 350, 'kind': 'auction_flow_window_paired_contrasts_v1'}]
- event_links: [{'version': 'auction-flow-bounded-parquet-storage-v1', 'series': 'window-000-monthly_acquisitions-ES-2021-event-links', 'rows': 138, 'row_groups': 1, 'encoding': 'plain', 'compression': 'zstd-level-3', 'schema': 'semantic_id: string\nevent_type: string\nevent_date: string\nevent_ts_utc_ns: int64\ntime_basis: string\ntime_precision: string\nstatus: string\nsource_path: string\nsource_metadata_sha256: string\ninstrument_id: int64\ncontract_key: string\nformation_id: string\nlabel_id: string\ncut_ns: int64\nformation_minutes: int64\nlatency_ns: int64\nhorizon_kind: string\nhorizon_minutes: int64\nrelative_bucket: string\nin_formation: bool\nhas_eligible_receiver: bool\nno_window: bool\nknown_at_ns: int64\ncausal_feature_eligible: bool\nprovenance_json: string', 'files': [{'path': '/workspace/trading-research/reports/auction-flow-runs/9c23254897fa93ff20a30214a7e73ca1adb4baf1c6d3b24bc23a3b464ee2939b/outputs/window-statistics-shard-01/window-000-monthly_acquisitions-ES-2021-event-links-0000.parquet', 'sha256': 'd1704617d0f434014bbfe49cd93b9aeda7a94fe52708ca48fc8fef7f1b3daee5', 'size_bytes': 11568, 'kind': 'auction_flow_parquet', 'rows': 138, 'row_groups': 1, 'value_hash_version': 'arrow-scalar-value-and-validity-v1', 'row_group_values': [{'rows': 138, 'sha256': 'de8f056c0369df39f4d2863458c5e02a4151d0e416ea5f7a6f3caf41ad01331e'}]}], 'compared_values': 3450, 'roundtrip_exact': True, 'cpu_seconds': 0.005843431000000621, 'serialized_bytes': 11568}]
- event_denominators: {'version': 'auction-flow-bounded-parquet-storage-v1', 'series': 'window-event-denominators', 'rows': 925, 'row_groups': 1, 'encoding': 'plain', 'compression': 'zstd-level-3', 'schema': 'semantic_id: string\nevent_type: string\nevent_date: string\nevent_ts_utc_ns: int64\ntime_basis: string\ntime_precision: string\nstatus: string\nprimary_population: bool\nindependent_support: bool\ndate_only: bool\nclock_consistent: bool\nhas_eligible_receiver_any_selected: bool\nhas_window_any_selected: bool\noutside_acquired_or_no_window: bool\nknown_at_ns: int64\ncausal_feature_eligible: bool\nprovenance_json: string', 'files': [{'path': '/workspace/trading-research/reports/auction-flow-runs/9c23254897fa93ff20a30214a7e73ca1adb4baf1c6d3b24bc23a3b464ee2939b/outputs/window-statistics-shard-01/window-event-denominators-0000.parquet', 'sha256': '3750afd949f8ec28f4c719898a59b62883318649f1b7e2103eddce67dd26c6af', 'size_bytes': 23431, 'kind': 'auction_flow_parquet', 'rows': 925, 'row_groups': 1, 'value_hash_version': 'arrow-scalar-value-and-validity-v1', 'row_group_values': [{'rows': 925, 'sha256': 'f1e3c960a831be2ff9f29f69423e670095c16cfe4fe049a70f523b7b59772e49'}]}], 'compared_values': 15725, 'roundtrip_exact': True, 'cpu_seconds': 0.010638232999999886, 'serialized_bytes': 23431}
- completeness: {'path': '/workspace/trading-research/reports/auction-flow-runs/9c23254897fa93ff20a30214a7e73ca1adb4baf1c6d3b24bc23a3b464ee2939b/outputs/window-statistics-shard-01/window-statistics-completeness.json', 'sha256': 'a9301ee1a5672a82c5d87a90d1cb5b3de77bbaa6a2d2d091d85d933968351d5b', 'size_bytes': 1296, 'kind': 'auction_flow_window_completeness_v1'}
- event_source: {'kind': 'scheduled_event_observed_rows_v1', 'path': '/workspace/trading-research/reports/scheduled-event-runs/1189e608a417b6848bed51d549f1967728a5549f8edc0b7e0d4d0e70d9b9c2db/outputs/observed-source-events.parquet', 'sha256': '8e7dbbf5f91668f1e11186b3f5d577ad80db9d278c4830ba5ae4dcbe5053a0bc', 'rows': 4755}
- cash_calendar: {'kind': 'cash_rth_calendar', 'path': '/workspace/trading-research/configs/cash-rth-calendar-research-v1.json', 'sha256': 'f069df0ccbb8318f1c675a05d9deed64ad681ebe1e47dd8573a6b18266665818', 'size_bytes': 6922}

Latency contrasts compare 0 ns and 1 s against 250 ms on the same physical source/cut/instrument/raw contract, formation, horizon and actual reference. Own supports are recorded before the intersection. Formation contrasts compare feature metrics on the common cut and reference; a zero future-target difference is a control, not evidence that formations are equivalent. A repeated forward target is not counted as independent evidence. Formation contrasts named left_vs_right report right minus left.

