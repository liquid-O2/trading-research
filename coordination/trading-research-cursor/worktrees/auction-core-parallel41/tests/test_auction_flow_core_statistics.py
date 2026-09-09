"""Independent literal checks for core measurement statistics helpers."""
from datetime import date, time
from pathlib import Path
import json
import tempfile
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.research.auction_flow_core_statistics import (
    CORE_PARALLEL_POLICY,
    CORE_WORKER_COUNT,
    FROZEN_STAGE_POLICY,
    REQUIRED_CASH_CALENDAR_REFERENCE,
    ExplicitCashSessions,
    alias_independent_dates,
    classify_session,
    core_partition_identity,
    core_partition_plan,
    core_partition_source_refs,
    decode_core_partition_key,
    economic_date,
    encode_core_partition_key,
    join_observations,
    labeled_date_and_event_means,
    observe_metric,
    occupancy_fractions,
    path_true_ohlc,
    project_core_parallel_resources,
    run_core_statistics,
    scientific_contract_definition,
    select_core_shard_keys,
    shared_moving_block_intervals,
    signed_close_open,
    stage_name,
)
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries
from trading_research.research.date_statistics import DEFAULT_REPLICATES


ZONE = 'America/New_York'
SHA = 'ab' * 32


def frozen_contract(**extra):
    contract = {
        'kind': 'auction_flow_core_statistics_contract_v1',
        'version': 1,
        'family_statistics_complete': False,
        'clock': {
            'atomic_width_ns': 60000000000,
            'interval': 'half-open original event interval; known_at retained separately',
        },
        'statistical_estimands': {
            'block_length': 5,
            'bootstrap_replicates': 1000,
            'confidence': 0.95,
            'minimum_events': 20,
            'minimum_independent_dates': 100,
            'quantiles': [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99],
            'seed': 20260908,
        },
        'stage_policy': {
            root: {name: list(bounds) for name, bounds in stages.items()}
            for root, stages in FROZEN_STAGE_POLICY.items()
        },
        'other_dates': 'separate unassigned descriptive rows, not training or confirmation',
    }
    contract.update(extra)
    return contract


def refuse_reference(reference):
    raise AssertionError(f'unexpected reference load {reference!r}')


class CoreMeasurementLiteralTests(unittest.TestCase):
    def test_cvd_path_range7_close1_loss6(self):
        result = path_true_ohlc([0, 5, -2, 1])
        self.assertEqual(result['open'], 0)
        self.assertEqual(result['high'], 5)
        self.assertEqual(result['low'], -2)
        self.assertEqual(result['close'], 1)
        self.assertEqual(result['true_cvd_excursion'], 7)
        self.assertEqual(result['close_excursion'], 1)
        self.assertEqual(result['information_loss'], 6)
        self.assertTrue(result['information_loss_positive'])

    def test_unknown_side_is_not_assigned_a_sign(self):
        self.assertEqual(signed_close_open(buy=3, sell=2, unknown=99), 1)
        self.assertEqual(signed_close_open(buy=0, sell=0, unknown=4), 0)
        self.assertEqual(signed_close_open(buy=5, sell=8, unknown=1), -3)
        self.assertNotEqual(signed_close_open(buy=3, sell=2, unknown=99), 3 + 99)
        self.assertNotEqual(signed_close_open(buy=3, sell=2, unknown=99), 3 - 99)

    def test_overlapping_hard_cohorts_are_not_a_partition(self):
        fractions = occupancy_fractions(
            all_prints=10, all_volume=100,
            cohorts={
                'ny_ge100': (6, 60),
                'london_ge75': (5, 40),
                'inclusive30_through60': (8, 80),
            },
        )
        count_sum = fractions['ny_ge100']['count'] + fractions['london_ge75']['count'] + fractions['inclusive30_through60']['count']
        size_sum = fractions['ny_ge100']['size'] + fractions['london_ge75']['size'] + fractions['inclusive30_through60']['size']
        self.assertEqual(fractions['ny_ge100']['count'], 0.6)
        self.assertEqual(fractions['london_ge75']['count'], 0.5)
        self.assertEqual(fractions['inclusive30_through60']['count'], 0.8)
        self.assertGreater(count_sum, 1.0)
        self.assertGreater(size_sum, 1.0)
        self.assertNotEqual(count_sum, 1.0)
        self.assertIsNone(occupancy_fractions(
            all_prints=0, all_volume=0, cohorts={'ny_ge100': (0, 0)},
        )['ny_ge100']['count'])

    def test_complete_zero_is_kept_and_partial_is_excluded(self):
        complete_zero, complete_reason = observe_metric(
            0, eligible=True, reason='incomplete_flow_history')
        partial_zero, partial_reason = observe_metric(
            0, eligible=False, reason='incomplete_flow_history')
        self.assertEqual(complete_zero, 0.0)
        self.assertIsNone(complete_reason)
        self.assertIsNone(partial_zero)
        self.assertEqual(partial_reason, 'incomplete_flow_history')
        self.assertNotEqual((complete_zero, complete_reason), (partial_zero, partial_reason))

    def test_missing_metric_is_distinct_from_true_zero(self):
        missing, missing_reason = observe_metric(None, eligible=True, reason='missing_vwap')
        zero, zero_reason = observe_metric(0, eligible=True, reason='missing_vwap')
        self.assertIsNone(missing)
        self.assertEqual(missing_reason, 'missing_value')
        self.assertEqual(zero, 0.0)
        self.assertIsNone(zero_reason)
        self.assertNotEqual(missing, zero)

    def test_date_equal_mean_differs_from_event_mean(self):
        result = labeled_date_and_event_means(
            {'2020-01-02': 3.0, '2020-01-03': 7.0},
            {'2020-01-02': 3, '2020-01-03': 1},
        )
        self.assertEqual(result['date_mean'], 4.0)
        self.assertEqual(result['event_mean'], 2.5)
        self.assertEqual(result['independent_dates'], 2)
        self.assertEqual(result['events'], 4)
        self.assertNotEqual(result['date_mean'], result['event_mean'])

    def test_ny_dst_and_cross_1800_use_event_start_not_known_at(self):
        before = local_timestamp(date(2020, 6, 15), time(17, 59), ZONE)
        at_roll = local_timestamp(date(2020, 6, 15), time(18, 0), ZONE)
        self.assertEqual(economic_date(before), '2020-06-15')
        self.assertEqual(economic_date(at_roll), '2020-06-16')
        spring_1800 = local_timestamp(date(2020, 3, 8), time(18, 0), ZONE)
        fall_1800 = local_timestamp(date(2020, 11, 1), time(18, 0), ZONE)
        spring_1730 = local_timestamp(date(2020, 3, 8), time(17, 30), ZONE)
        fall_0130 = local_timestamp(date(2020, 11, 1), time(1, 30), ZONE, fold=0)
        fall_0130_repeat = local_timestamp(date(2020, 11, 1), time(1, 30), ZONE, fold=1)
        self.assertEqual(economic_date(spring_1800), '2020-03-09')
        self.assertEqual(economic_date(spring_1730), '2020-03-08')
        self.assertEqual(economic_date(fall_1800), '2020-11-02')
        self.assertEqual(economic_date(fall_0130), '2020-11-01')
        self.assertEqual(economic_date(fall_0130_repeat), '2020-11-01')
        self.assertNotEqual(fall_0130, fall_0130_repeat)
        later_known = local_timestamp(date(2020, 6, 16), time(12, 0), ZONE)
        self.assertEqual(economic_date(before), '2020-06-15')
        self.assertGreater(later_known, before)

    def test_holiday_and_missing_calendar_do_not_invent_cash_rth(self):
        calendar = ExplicitCashSessions({
            '2020-01-01': {'state': 'closed'},
            '2020-01-02': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2020-11-27': {'state': 'early_close', 'open': '09:30:00', 'close': '13:00:00'},
        })
        holiday_1000 = local_timestamp(date(2020, 1, 1), time(10, 0), ZONE)
        regular_1000 = local_timestamp(date(2020, 1, 2), time(10, 0), ZONE)
        pre = local_timestamp(date(2020, 1, 2), time(7, 0), ZONE)
        after_early = local_timestamp(date(2020, 11, 27), time(14, 0), ZONE)
        late = local_timestamp(date(2020, 1, 2), time(17, 30), ZONE)
        holiday = classify_session(holiday_1000, holiday_1000 + 60 * 10**9,
                                   calendar=calendar, known_at_ns=holiday_1000 + 1)
        regular = classify_session(regular_1000, regular_1000 + 60 * 10**9,
                                   calendar=calendar, known_at_ns=regular_1000 + 1)
        morning = classify_session(pre, pre + 60 * 10**9, calendar=calendar, known_at_ns=pre + 1)
        early = classify_session(after_early, after_early + 60 * 10**9,
                                 calendar=calendar, known_at_ns=after_early + 1)
        off = classify_session(late, late + 60 * 10**9, calendar=calendar, known_at_ns=late + 1)
        self.assertEqual(holiday['calendar_state'], 'closed')
        self.assertNotEqual(holiday['session'], 'cash_rth')
        self.assertFalse(holiday['in_cash_rth'])
        self.assertEqual(regular['session'], 'cash_rth')
        self.assertEqual(morning['session'], 'pre_rth')
        self.assertNotEqual(early['session'], 'cash_rth')
        self.assertEqual(off['session'], 'off_session')
        missing = ExplicitCashSessions({'2020-01-02': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'}})
        absent = classify_session(holiday_1000, holiday_1000 + 60 * 10**9,
                                  calendar=missing, known_at_ns=holiday_1000 + 1)
        self.assertEqual(absent['calendar_state'], 'missing')
        self.assertNotEqual(absent['session'], 'cash_rth')
        self.assertFalse(absent['in_cash_rth'])
        with self.assertRaises(ContractError):
            ExplicitCashSessions({'2020-01-02': {'state': 'regular'}}).resolve(
                date(2020, 1, 2), cut=1)

    def test_stage_boundaries_are_half_open(self):
        self.assertEqual(stage_name('NQ', '2022-12-31'), 'training')
        self.assertEqual(stage_name('NQ', '2023-01-01'), 'development')
        self.assertEqual(stage_name('NQ', '2024-01-01'), 'calibration')
        self.assertEqual(stage_name('NQ', '2025-01-01'), 'confirmation')
        self.assertEqual(stage_name('ES', '2020-12-31'), 'training')
        self.assertEqual(stage_name('ES', '2021-01-01'), 'unassigned')
        self.assertEqual(stage_name('ES', '2023-07-01'), 'development')
        self.assertEqual(stage_name('ES', '2024-04-01'), 'confirmation')
        self.assertEqual(stage_name('ES', '2024-08-31'), 'confirmation')
        self.assertEqual(stage_name('ES', '2024-09-01'), 'unassigned')

    def test_shared_date_block_bootstrap_is_paired_and_deterministic(self):
        dates = [f'2020-01-0{index}' for index in range(2, 8)]
        loss_sums = {day: 6.0 for day in dates}
        close_sums = {day: 1.0 for day in dates}
        counts = {day: 1 for day in dates}
        first = shared_moving_block_intervals(
            {'information_loss': loss_sums, 'close_excursion': close_sums,
             'true_ohlc_minus_close': {day: 5.0 for day in dates}},
            {'information_loss': counts, 'close_excursion': counts,
             'true_ohlc_minus_close': counts},
            seed=20260908, block_length=5, replicates=1000, confidence=0.95,
            minimum_independent_dates=1, minimum_events=1, return_weights=True,
        )
        second = shared_moving_block_intervals(
            {'information_loss': loss_sums, 'close_excursion': close_sums,
             'true_ohlc_minus_close': {day: 5.0 for day in dates}},
            {'information_loss': counts, 'close_excursion': counts,
             'true_ohlc_minus_close': counts},
            seed=20260908, block_length=5, replicates=1000, confidence=0.95,
            minimum_independent_dates=1, minimum_events=1, return_weights=True,
        )
        self.assertEqual(first, second)
        self.assertEqual(first['bootstrap_weights']['weights'], second['bootstrap_weights']['weights'])
        self.assertFalse(first['bootstrap_weights']['circular_end_wrap'])
        self.assertEqual(first['metrics']['information_loss']['date_mean']['estimate'], 6.0)
        self.assertEqual(first['metrics']['close_excursion']['date_mean']['estimate'], 1.0)
        paired = first['metrics']['true_ohlc_minus_close']['date_mean']
        self.assertEqual(paired['estimate'], 5.0)
        self.assertEqual((paired['bootstrap']['lower'], paired['bootstrap']['upper']), (5.0, 5.0))
        self.assertEqual(first['replicates'], DEFAULT_REPLICATES)
        self.assertEqual(len(first['bootstrap_weights']['weights']), 1000)
        self.assertTrue(all(sum(row) == 6 for row in first['bootstrap_weights']['weights']))

    def test_aliases_do_not_add_independent_date_support(self):
        rows = [
            {'canonical_raw_values_sha256': SHA, 'source_variant': 'v1', 'economic_date': '2020-01-02'},
            {'canonical_raw_values_sha256': SHA, 'source_variant': 'v2', 'economic_date': '2020-01-02'},
            {'canonical_raw_values_sha256': SHA, 'source_variant': 'v1', 'economic_date': '2020-01-03'},
        ]
        result = alias_independent_dates(rows)
        self.assertEqual(result[SHA]['independent_economic_date_count'], 2)
        self.assertEqual(result[SHA]['alias_source_variant_count'], 2)
        self.assertEqual(result[SHA]['independent_economic_dates'], ['2020-01-02', '2020-01-03'])
        self.assertNotEqual(result[SHA]['independent_economic_date_count'], 3)
        self.assertEqual(result[SHA]['source_window_rows'], 3)

    def test_matched_metric_mismatch_and_mismatched_contract_are_not_joined(self):
        left = {
            'root': 'NQ', 'instrument_id': 7, 'event_start_ns': 10, 'event_end_ns': 20,
            'coordinate_complete': True, 'contract_key': 'NQ:A',
            'all__close': 5, 'all__high': 8, 'source_variant': 'v1',
            'receipt_sha256': 'aa' * 32, 'raw_rows': 12,
        }
        equal = {
            **left, 'source_variant': 'v2', 'receipt_sha256': 'bb' * 32, 'raw_rows': 99,
        }
        different = {**equal, 'all__close': 9}
        other_contract = {**equal, 'contract_key': 'NQ:B'}
        incomplete = {**equal, 'coordinate_complete': False}
        same = join_observations([left], [equal], value_fields=('all__close', 'all__high'))
        self.assertEqual(same['matched_equal'], 1)
        self.assertEqual(same['matched_different'], 0)
        changed = join_observations([left], [different], value_fields=('all__close', 'all__high'))
        self.assertEqual(changed['matched_equal'], 0)
        self.assertEqual(changed['matched_different'], 1)
        self.assertEqual(changed['metric_disagreements']['all__close'], 1)
        self.assertEqual(changed['magnitude_summaries']['all__close']['mean_abs_difference'], 4.0)
        contracts = join_observations([left], [other_contract], value_fields=('all__close',))
        self.assertEqual(contracts['mismatched_contract'], 1)
        self.assertEqual(contracts['matched_equal'], 0)
        self.assertEqual(contracts['matched_different'], 0)
        coverage = join_observations([left], [incomplete], value_fields=('all__close',))
        self.assertEqual(coverage['incompatible_coordinates'], 1)
        self.assertEqual(coverage['matched_equal'], 0)
        self.assertEqual(coverage['unmatched_left'], 1)

    def test_production_requires_materialized_population_and_calendar_reference(self):
        contract = frozen_contract()
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=1024 ** 2,
                                     maximum_file_bytes=512 * 1024)
            with self.assertRaises(IntegrityError) as materialized:
                run_core_statistics(
                    population={
                        'kind': 'auction_flow_observation_population_v1',
                        'all_population_materialized': False,
                        'complete_family_statistics': False,
                        'units': [],
                    },
                    contract=frozen_contract(cash_session_table={'2020-01-02': {
                        'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'}}),
                    outputs=outputs, load_reference=refuse_reference,
                )
            self.assertIn('all_population_materialized', str(materialized.exception))
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'out2', maximum_total_bytes=1024 ** 2,
                                     maximum_file_bytes=512 * 1024)
            with self.assertRaises(ContractError) as calendar:
                run_core_statistics(
                    population={
                        'kind': 'auction_flow_observation_population_v1',
                        'all_population_materialized': True,
                        'complete_family_statistics': False,
                        'units': [],
                    },
                    contract=contract, outputs=outputs, load_reference=refuse_reference,
                )
            message = str(calendar.exception)
            self.assertIn(REQUIRED_CASH_CALENDAR_REFERENCE['path'], message)
            self.assertIn(REQUIRED_CASH_CALENDAR_REFERENCE['sha256'], message)

    def test_tiny_materialized_population_keeps_complete_zero_and_does_not_claim_family(self):
        import pyarrow as pa
        from trading_research.research.auction_flow_observation_tables import (
            observation_schema, observation_table,
        )

        start = local_timestamp(date(2020, 1, 2), time(10, 0), ZONE)
        end = start + 60_000_000_000
        known = end + 250_000_000
        schema = observation_schema()

        def row(**overrides):
            item = {}
            for field in schema:
                if field.nullable:
                    item[field.name] = None
                elif pa.types.is_boolean(field.type):
                    item[field.name] = False
                elif pa.types.is_integer(field.type):
                    item[field.name] = 0
                elif pa.types.is_floating(field.type):
                    item[field.name] = None
                else:
                    item[field.name] = ''
            item.update({
                'root': 'NQ',
                'source_path': 'quantpad/example.parquet',
                'source_metadata_sha256': SHA,
                'source_variant': 'abc123def456',
                'source_window_start_ns': start,
                'source_window_end_ns': end,
                'receipt_sha256': SHA,
                'measurement_sha256': 'cd' * 32,
                'canonical_raw_values_sha256': 'ef' * 32,
                'instrument_id': 7,
                'contract_key': 'NQ:A',
                'event_start_ns': start,
                'event_end_ns': end,
                'known_at_ns': known,
            })
            item.update(overrides)
            return item

        complete = row(
            all__open=0, all__high=5, all__low=-2, all__close=1,
            all__buy=8, all__sell=7, all__unknown=0, all__volume=15, all__prints=3,
            all__coverage_complete=True, flow_history_complete=True,
            source_coverage_complete=True, coordinate_complete=True,
            price_history_complete=True, archive_window_complete=True,
            source_instrument_presence=True,
        )
        partial = row(
            instrument_id=8, all__coverage_complete=False, flow_history_complete=False,
            source_coverage_complete=False, coordinate_complete=False,
        )
        table = observation_table([complete, partial])
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'obs', maximum_total_bytes=4 * 1024 ** 2,
                                     maximum_file_bytes=2 * 1024 ** 2)
            series = ParquetSeries(outputs, 'tiny-observations', encoding='plain')
            series.append(table)
            stored = series.finish()
            stats_out = BoundedOutputs(Path(folder) / 'stats', maximum_total_bytes=8 * 1024 ** 2,
                                       maximum_file_bytes=4 * 1024 ** 2)
            result = run_core_statistics(
                population={
                    'kind': 'auction_flow_observation_population_v1',
                    'all_population_materialized': True,
                    'complete_family_statistics': False,
                    'population_source_windows': 2,
                    'population_source_files': 1,
                    'source_catalog': {'path': '/catalog', 'sha256': SHA, 'size_bytes': 1,
                                       'kind': 'auction_flow_complete_production_receipt_catalog_v1'},
                    'units': [
                        {
                            'root': 'NQ', 'source_path': 'quantpad/example.parquet',
                            'source_variant': 'abc123def456',
                            'source_window_start_ns': start, 'source_window_end_ns': end,
                            'source_window_status': 'measured', 'atomic_rows': 2,
                            'series': stored,
                        },
                        {
                            'root': 'NQ', 'source_path': 'quantpad/example.parquet',
                            'source_variant': 'abc123def456',
                            'source_window_start_ns': start, 'source_window_end_ns': end,
                            'source_window_status': 'unavailable_source_window',
                            'atomic_rows': 0,
                        },
                    ],
                    'inventory': [{
                        'canonical_raw_values': {'sha256': 'ef' * 32},
                        'unit': {
                            'root': 'NQ', 'source_path': 'quantpad/example.parquet',
                            'source_variant': 'abc123def456',
                            'event_start_ns': start, 'event_end_ns': end,
                        },
                    }],
                },
                contract=frozen_contract(cash_session_table={
                    '2020-01-02': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
                }),
                outputs=stats_out, load_reference=refuse_reference,
            )
            self.assertTrue(result['passed'])
            self.assertFalse(result['complete_family_statistics'])
            self.assertEqual(result['processed_observations'], 2)
            self.assertEqual(result['no_instrument_source_windows'], 1)
            self.assertEqual(result['processed_source_windows'], 2)
            self.assertIn('groups', result['refs'])
            self.assertIn('report', result['refs'])
            self.assertIn('denominators', result['refs'])
            import json
            groups = json.loads(Path(result['refs']['groups'][0]['path']).read_bytes())['groups']
            metric = groups[0]['metrics']['complete_all_information_loss']
            self.assertEqual(metric['eligible_observations'], 1)
            self.assertEqual(metric['observation_moments']['mean'], 6.)
            observed = groups[0]['metrics']['all_volume']
            self.assertEqual(observed['eligible_observations'], 1)
            self.assertEqual(observed['excluded_reason_counts'], {'no_observed_instrument': 1})

    def test_empty_metric_store_does_not_allocate_65536_values_per_missing_group(self):
        import numpy as np
        from trading_research.research.auction_flow_core_statistics import _MetricStore, _moments
        store = _MetricStore(np)
        self.assertEqual(store.parts, [])
        self.assertFalse(any(isinstance(value, np.ndarray) for value in vars(store).values()))
        store.extend(np.array([1000000000001., 1000000000002., 1000000000003.]), '2020-01-02')
        values = store.array()
        self.assertEqual(_moments(store, values)['variance'], 1.)
        self.assertEqual(store.date_count, {'2020-01-02': 3})

    def test_missing_dates_stay_in_shared_bootstrap_universe(self):
        result = shared_moving_block_intervals(
            {'metric': {'2020-01-02': 0.}, 'absent': {}},
            {'metric': {'2020-01-02': 1}, 'absent': {}},
            intended_dates=['2020-01-02', '2020-01-03'],
            seed=20260908, block_length=5, replicates=1000, confidence=.95,
            minimum_independent_dates=100, minimum_events=20)
        self.assertEqual(result['intended_date_count'], 2)
        self.assertEqual(result['metrics']['metric']['date_mean']['missing_date_count'], 1)
        self.assertIsNone(result['metrics']['absent']['date_mean']['estimate'])

    def test_year_boundary_unit_belongs_to_each_economic_year_and_join_is_exact(self):
        start_2020 = local_timestamp(date(2020, 12, 31), time(17, 0), ZONE)
        start_2021 = local_timestamp(date(2021, 1, 1), time(10, 0), ZONE)
        end = start_2021 + 60_000_000_000
        self.assertEqual(economic_date(start_2020)[:4], '2020')
        self.assertEqual(economic_date(end - 1)[:4], '2021')
        unit = {
            'root': 'NQ', 'source_path': 'quantpad/example.parquet',
            'source_variant': 'abc123def456',
            'source_window_start_ns': start_2020, 'source_window_end_ns': end,
            'source_window_status': 'measured', 'atomic_rows': 2,
            'series': {'roundtrip_exact': True, 'files': []},
        }
        plan = core_partition_plan([unit], collections={'quantpad/example.parquet': 'monthly_acquisitions'})
        self.assertEqual(plan['intended_rows'], 2)
        self.assertEqual(plan['keys'], [
            ('monthly_acquisitions', 'NQ', 2020),
            ('monthly_acquisitions', 'NQ', 2021),
        ])
        self.assertEqual(plan['members'][('monthly_acquisitions', 'NQ', 2020)], [unit])
        self.assertEqual(plan['members'][('monthly_acquisitions', 'NQ', 2021)], [unit])
        shards = [select_core_shard_keys(plan['keys'], ordinal=index) for index in range(CORE_WORKER_COUNT)]
        joined = [key for shard in shards for key in shard]
        self.assertEqual(joined, plan['keys'])
        self.assertEqual(sum(len(shard) for shard in shards), len(plan['keys']))
        self.assertEqual(len({key for shard in shards for key in shard}), len(plan['keys']))

    def test_sorted_keys_modulo_eight_has_no_duplicate_or_missing_join(self):
        keys = [(f'collection-{index % 3}', 'NQ' if index % 2 == 0 else 'ES', 2020 + (index % 7))
                for index in range(23)]
        keys = sorted(set(keys))
        shards = [select_core_shard_keys(keys, ordinal=index) for index in range(8)]
        self.assertEqual([key for shard in shards for key in shard], keys)
        seen = []
        for shard in shards:
            seen.extend(shard)
        self.assertEqual(len(seen), len(keys))
        self.assertEqual(set(seen), set(keys))
        self.assertEqual(select_core_shard_keys(keys, ordinal=0), keys[0::8])
        with self.assertRaises(IntegrityError):
            select_core_shard_keys(keys, ordinal=8)
        with self.assertRaises(IntegrityError):
            select_core_shard_keys(keys, ordinal=0, worker_count=7)

    def test_parallel_execution_is_excluded_from_partition_identity(self):
        members = [{
            'root': 'NQ', 'source_path': 'quantpad/example.parquet',
            'source_window_start_ns': 1, 'atomic_rows': 4,
            'receipt': {'source_path': 'quantpad/example.parquet', 'start': 1, 'rows': 4},
        }]
        refs = core_partition_source_refs(members)
        plain = frozen_contract()
        parallel = frozen_contract(parallel_execution={
            'worker_count': CORE_WORKER_COUNT, 'policy': CORE_PARALLEL_POLICY,
        })
        self.assertEqual(scientific_contract_definition(plain), scientific_contract_definition(parallel))
        self.assertNotIn('parallel_execution', scientific_contract_definition(parallel))
        self.assertEqual(
            core_partition_identity(plain, collection='monthly_acquisitions', root='NQ',
                                    year=2023, source_refs=refs),
            core_partition_identity(parallel, collection='monthly_acquisitions', root='NQ',
                                    year=2023, source_refs=refs),
        )
        self.assertEqual(encode_core_partition_key(('monthly_acquisitions', 'NQ', 2023)),
                         ['monthly_acquisitions', 'NQ', 2023])
        self.assertEqual(decode_core_partition_key(['monthly_acquisitions', 'NQ', 2023]),
                         ('monthly_acquisitions', 'NQ', 2023))

    def test_parallel_projection_accounts_reused_rows_and_does_not_require_serial_wall(self):
        annual = [{'cpu_seconds': 100., 'wall_seconds': 100., 'observations': 100000,
                   'output_bytes': 100000}]
        small = [{'cpu_seconds': 2., 'wall_seconds': 2., 'observations': 10, 'output_bytes': 10}]
        remaining = project_core_parallel_resources(
            annual_measurements=annual, small_measurements=small, remaining_rows=200000,
            remaining_partition_rows=[100000, 100000], declared_partition_count=3)
        self.assertEqual(remaining['cpu_seconds'], 1.5 * (100. / 100000 * 200000 + 3 * 2.))
        walls = [1.5 * (100. / 100000 * 100000 + 2.), 1.5 * (100. / 100000 * 100000 + 2.)]
        self.assertEqual(remaining['parallel_wall_seconds'], sum(walls) / 8 + max(walls) + 120)
        serial_wall = 1.5 * (100. / 100000 * 300000 + 3 * 2.)
        self.assertLess(remaining['parallel_wall_seconds'], serial_wall)
        reused = project_core_parallel_resources(
            annual_measurements=annual, small_measurements=small, remaining_rows=0,
            remaining_partition_rows=[], declared_partition_count=3)
        self.assertEqual(reused['cpu_seconds'], 1.5 * (0 + 3 * 2.))
        self.assertEqual(reused['parallel_wall_seconds'], 120)
        self.assertEqual(reused['remaining_rows'], 0)

    def test_serial_and_partition_finalize_are_numerically_identical_on_tiny_fixture(self):
        with tempfile.TemporaryDirectory() as folder:
            population, calendar = _tiny_year_boundary_population(Path(folder) / 'obs')
            contract = frozen_contract(cash_session_table=calendar)
            serial_out = BoundedOutputs(Path(folder) / 'serial', maximum_total_bytes=8 * 1024 ** 2,
                                        maximum_file_bytes=4 * 1024 ** 2)
            serial = run_core_statistics(
                population=population, contract=contract, outputs=serial_out,
                load_reference=refuse_reference)
            plan = core_partition_plan(
                population['units'], collections=contract.get('source_collections', {}))
            self.assertGreaterEqual(len(plan['keys']), 2)
            child_refs = []
            for index, key in enumerate(plan['keys']):
                child_out = BoundedOutputs(Path(folder) / f'child-{index}',
                                           maximum_total_bytes=8 * 1024 ** 2,
                                           maximum_file_bytes=4 * 1024 ** 2)
                child = run_core_statistics(
                    population=population, contract=contract, outputs=child_out,
                    load_reference=refuse_reference, partition_keys=[key], finalize=False)
                self.assertTrue(child['finalize'] is False)
                self.assertEqual(child['partition_keys'], [encode_core_partition_key(key)])
                self.assertFalse((Path(folder) / f'child-{index}' / 'core-statistics-aliases.json').exists())
                self.assertFalse((Path(folder) / f'child-{index}' / 'core-measurement-statistics-report.md').exists())
                child_refs.extend(child['refs']['partitions'])
            join_out = BoundedOutputs(Path(folder) / 'join', maximum_total_bytes=8 * 1024 ** 2,
                                      maximum_file_bytes=4 * 1024 ** 2)
            joined = run_core_statistics(
                population=population,
                contract=frozen_contract(
                    cash_session_table=calendar, accepted_partitions=child_refs,
                    parallel_execution={'worker_count': 8, 'policy': CORE_PARALLEL_POLICY}),
                outputs=join_out, load_reference=_load_accepted_partitions(child_refs),
            )
            self.assertEqual(joined['reused_partitions'], len(plan['keys']))
            self.assertEqual(joined['new_partitions'], 0)
            self.assertEqual(joined['processed_observations'], serial['processed_observations'])
            self.assertEqual(joined['processed_observations'], population['units'][0]['atomic_rows'])
            self.assertEqual(_group_payloads(serial['refs']['groups']),
                             _group_payloads(joined['refs']['groups']))
            self.assertEqual(_denominator_values(serial['refs']['denominators']),
                             _denominator_values(joined['refs']['denominators']))
            self.assertEqual(
                [json.loads(Path(ref['path']).read_bytes())['identity'] for ref in serial['refs']['partitions']],
                [json.loads(Path(ref['path']).read_bytes())['identity'] for ref in joined['refs']['partitions']],
            )
            reuse_out = BoundedOutputs(Path(folder) / 'reuse', maximum_total_bytes=8 * 1024 ** 2,
                                       maximum_file_bytes=4 * 1024 ** 2)
            reused = run_core_statistics(
                population=population,
                contract=frozen_contract(
                    cash_session_table=calendar, accepted_partitions=serial['refs']['partitions'],
                    parallel_execution={'worker_count': 8, 'policy': CORE_PARALLEL_POLICY}),
                outputs=reuse_out, load_reference=_load_accepted_partitions(serial['refs']['partitions']),
            )
            self.assertEqual(reused['reused_partitions'], len(serial['refs']['partitions']))
            self.assertEqual(reused['new_partitions'], 0)
            self.assertEqual(_group_payloads(serial['refs']['groups']),
                             _group_payloads(reused['refs']['groups']))
            with self.assertRaises(IntegrityError):
                run_core_statistics(
                    population=population, contract=contract,
                    outputs=BoundedOutputs(Path(folder) / 'partial', maximum_total_bytes=8 * 1024 ** 2,
                                           maximum_file_bytes=4 * 1024 ** 2),
                    load_reference=refuse_reference, partition_keys=[plan['keys'][0]], finalize=True,
                )


def _tiny_year_boundary_population(series_dir):
    import pyarrow as pa
    from trading_research.research.auction_flow_observation_tables import (
        observation_schema, observation_table,
    )
    start_2020 = local_timestamp(date(2020, 12, 31), time(17, 0), ZONE)
    start_2021 = local_timestamp(date(2021, 1, 1), time(10, 0), ZONE)
    end = start_2021 + 60_000_000_000
    known_2020 = start_2020 + 60_000_000_000 + 250_000_000
    known_2021 = end + 250_000_000
    schema = observation_schema()

    def row(event_start, event_end, known, **overrides):
        item = {}
        for field in schema:
            if field.nullable:
                item[field.name] = None
            elif pa.types.is_boolean(field.type):
                item[field.name] = False
            elif pa.types.is_integer(field.type):
                item[field.name] = 0
            elif pa.types.is_floating(field.type):
                item[field.name] = None
            else:
                item[field.name] = ''
        item.update({
            'root': 'NQ',
            'source_path': 'quantpad/example.parquet',
            'source_metadata_sha256': SHA,
            'source_variant': 'abc123def456',
            'source_window_start_ns': start_2020,
            'source_window_end_ns': end,
            'receipt_sha256': SHA,
            'measurement_sha256': 'cd' * 32,
            'canonical_raw_values_sha256': 'ef' * 32,
            'instrument_id': 7,
            'contract_key': 'NQ:A',
            'event_start_ns': event_start,
            'event_end_ns': event_end,
            'known_at_ns': known,
            'all__open': 0, 'all__high': 5, 'all__low': -2, 'all__close': 1,
            'all__buy': 8, 'all__sell': 7, 'all__unknown': 0, 'all__volume': 15, 'all__prints': 3,
            'all__coverage_complete': True, 'flow_history_complete': True,
            'source_coverage_complete': True, 'coordinate_complete': True,
            'price_history_complete': True, 'archive_window_complete': True,
            'source_instrument_presence': True,
        })
        item.update(overrides)
        return item

    table = observation_table([
        row(start_2020, start_2020 + 60_000_000_000, known_2020),
        row(start_2021, end, known_2021),
    ])
    outputs = BoundedOutputs(series_dir, maximum_total_bytes=4 * 1024 ** 2,
                             maximum_file_bytes=2 * 1024 ** 2)
    series = ParquetSeries(outputs, 'tiny-boundary-observations', encoding='plain')
    series.append(table)
    stored = series.finish()
    population = {
        'kind': 'auction_flow_observation_population_v1',
        'all_population_materialized': True,
        'complete_family_statistics': False,
        'population_source_windows': 1,
        'population_source_files': 1,
        'source_catalog': {'path': '/catalog', 'sha256': SHA, 'size_bytes': 1,
                           'kind': 'auction_flow_complete_production_receipt_catalog_v1'},
        'units': [{
            'root': 'NQ', 'source_path': 'quantpad/example.parquet',
            'source_variant': 'abc123def456',
            'source_window_start_ns': start_2020, 'source_window_end_ns': end,
            'source_window_status': 'measured', 'atomic_rows': 2,
            'series': stored,
        }],
        'inventory': [{
            'canonical_raw_values': {'sha256': 'ef' * 32},
            'unit': {
                'root': 'NQ', 'source_path': 'quantpad/example.parquet',
                'source_variant': 'abc123def456',
                'event_start_ns': start_2020, 'event_end_ns': end,
            },
        }],
    }
    calendar = {
        '2020-12-31': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
        '2021-01-01': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
    }
    return population, calendar


def _load_accepted_partitions(refs):
    by_path = {Path(ref['path']).resolve(): ref for ref in refs}

    def load(reference, maximum=None):
        path = Path(reference['path']).resolve()
        if path not in by_path:
            raise AssertionError(f'unexpected reference load {reference!r}')
        return json.loads(path.read_bytes())
    return load


def _group_payloads(refs):
    return [json.loads(Path(ref['path']).read_bytes())['groups'] for ref in refs]


def _denominator_values(refs):
    return [(item['rows'], [(file['rows'], file['row_group_values']) for file in item['files']])
            for item in refs]


if __name__ == '__main__':
    unittest.main()
