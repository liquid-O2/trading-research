"""Independent literal checks for window/formation/event-timing statistics."""
from datetime import date, time
from pathlib import Path
import json
import tempfile
import unittest

from trading_research.foundations.calendar import local_timestamp
from trading_research.research.auction_flow_core_statistics import FROZEN_STAGE_POLICY
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries
from trading_research.research.auction_flow_window_statistics import (
    FEATURE_QUALITY_FLAGS,
    KIND,
    SOURCE_LATENCY_NS,
    alias_collection_dates,
    cohort_volume_fraction,
    complete_binary_flag,
    directional_concordance,
    encode_window_partition_key,
    equal_date_mean,
    event_coverage_state,
    event_in_formation,
    event_relative_bucket,
    formation_pair_eligible,
    future_displacements,
    intended_date_universe,
    known_at_available_at_cut,
    latency_pair_eligible,
    reference_inside_formation,
    run_window_statistics,
    scientific_join_eligibility,
    timed_event_eligible,
    true_path_range,
    unknown_volume_fraction,
)


ZONE = 'America/New_York'
SHA = 'ab' * 32
OTHER_SHA = 'cd' * 32
PATH = 'quantpad/test-nq-2020-01.parquet'


def _cut():
    return local_timestamp(date(2020, 6, 15), time(10, 0), ZONE)


def _identity():
    cut = _cut()
    return {
        'root': 'NQ',
        'source_path': PATH,
        'source_metadata_sha256': SHA,
        'source_variant': 'abc123def456',
        'acquired_event_start_ns': cut - 4 * 60 * 60 * 1_000_000_000,
        'acquired_event_end_ns': cut + 8 * 60 * 60 * 1_000_000_000,
    }


def _quality(**overrides):
    row = {name: True for name in FEATURE_QUALITY_FLAGS}
    row.update(
        left_censored=False, right_censored=False, contract_transition=False,
        stage_boundary=False,
    )
    row.update(overrides)
    return row


def feature_row(**overrides):
    cut = _cut()
    start = cut - 5 * 60 * 1_000_000_000
    row = {
        **_identity(),
        **_quality(),
        'instrument_id': 7,
        'contract_key': 'NQ:H0',
        'formation_minutes': 5,
        'cut_ns': cut,
        'event_start_ns': start,
        'event_end_ns': cut,
        'known_at_ns': cut + SOURCE_LATENCY_NS,
        'formation_id': 'f1',
        'reference_price_ticks': 100,
        'reference_event_ns': cut - 1_000_000_000,
        'reference_source_order': 3,
        'all__close': 4,
    }
    row.update(overrides)
    return row


def label_row(**overrides):
    cut = _cut()
    latency = overrides.get('latency_ns', SOURCE_LATENCY_NS)
    start = cut + latency
    end = start + 5 * 60 * 1_000_000_000
    row = {
        **_identity(),
        'instrument_id': 7,
        'contract_key': 'NQ:H0',
        'cut_ns': cut,
        'latency_ns': latency,
        'horizon_kind': 'fixed_minutes',
        'horizon_minutes': 5,
        'event_start_ns': start,
        'event_end_ns': end,
        'known_at_ns': end + latency,
        'label_id': 'l1',
        'complete': True,
        'left_censored': False,
        'right_censored': False,
        'contract_transition': False,
        'no_new_trade': False,
        'no_priced_trade': False,
        'last_priced_ticks': 110,
        'observed_high_ticks': 110,
        'observed_low_ticks': 100,
    }
    row.update(overrides)
    return row


def frozen_contract(**extra):
    contract = {
        'kind': 'auction_flow_window_statistics_contract_v1',
        'version': 1,
        'family_complete': False,
        'formation_minutes': [5, 15, 60, 240],
        'latency_ns': [250000000, 0, 1000000000],
        'statistics': {
            'block_length_dates': 5,
            'bootstrap_replicates': 1000,
            'confidence': 0.95,
            'minimum_dates': 100,
            'minimum_events': 20,
            'quantiles': [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99],
            'seed': 20260908,
        },
        'stage_policy': {
            root: {name: list(bounds) for name, bounds in stages.items()}
            for root, stages in FROZEN_STAGE_POLICY.items()
        },
        'source_collections': {PATH: 'monthly_acquisitions'},
        'primary_population': {'start': '2020-01-01', 'end': '2026-09-04'},
        'cash_session_table': {
            '2020-06-15': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
            '2021-06-15': {'state': 'regular', 'open': '09:30:00', 'close': '16:00:00'},
        },
        'event_rows': [],
    }
    contract.update(extra)
    return contract


def refuse_reference(reference, **kwargs):
    raise AssertionError(f'unexpected reference load {reference!r}')


class WindowStatisticsLiteralTests(unittest.TestCase):
    def test_literal_future_100_to_110_is_plus_10_terminal_and_up10_down0(self):
        result = future_displacements(100, 110, 110, 100)
        self.assertEqual(result['terminal_return_ticks'], 10)
        self.assertEqual(result['future_up_excursion_ticks'], 10)
        self.assertEqual(result['future_down_excursion_ticks'], 0)

    def test_all_future_above_reference_clamps_down_to_zero(self):
        result = future_displacements(100, 112, 120, 101)
        self.assertEqual(result['future_down_excursion_ticks'], 0)
        self.assertEqual(result['future_up_excursion_ticks'], 20)
        self.assertEqual(result['terminal_return_ticks'], 12)

    def test_quiet_complete_is_no_new_trade_one_and_null_price(self):
        quiet = future_displacements(100, None, None, None)
        self.assertIsNone(quiet['terminal_return_ticks'])
        self.assertIsNone(quiet['future_up_excursion_ticks'])
        self.assertEqual(complete_binary_flag(True, complete=True), 1.0)
        self.assertIsNone(complete_binary_flag(True, complete=False))

    def test_missing_is_not_zero(self):
        missing = future_displacements(None, None, None, None)
        self.assertIsNone(missing['terminal_return_ticks'])
        self.assertIsNone(unknown_volume_fraction(0, 0))
        self.assertIsNone(complete_binary_flag(False, complete=False))
        self.assertEqual(complete_binary_flag(False, complete=True), 0.0)
        self.assertNotEqual(missing['terminal_return_ticks'], 0)

    def test_eligibility_failures_are_explicit(self):
        cut = _cut()
        self.assertFalse(known_at_available_at_cut(cut + 1, cut))
        self.assertTrue(known_at_available_at_cut(cut, cut))
        self.assertFalse(known_at_available_at_cut(None, cut))
        before = scientific_join_eligibility(feature_row(), label_row(complete=False, known_at_ns=None))
        self.assertFalse(before['eligible'])
        early = scientific_join_eligibility(
            feature_row(), label_row(known_at_ns=label_row()['event_end_ns'] - 1))
        self.assertFalse(early['eligible'])
        self.assertEqual(early['scientific_reason'], 'label_before_maturity')
        crossed = scientific_join_eligibility(
            feature_row(),
            label_row(known_at_ns=local_timestamp(date(2024, 2, 1), time(10, 0), ZONE)),
        )
        self.assertFalse(crossed['eligible'])
        hashed = scientific_join_eligibility(
            feature_row(), label_row(source_metadata_sha256=OTHER_SHA))
        self.assertFalse(hashed['eligible'])
        self.assertEqual(hashed['reason'], 'source_identity_mismatch')
        contract = scientific_join_eligibility(feature_row(), label_row(contract_key='NQ:M0'))
        self.assertFalse(contract['eligible'])
        censored = scientific_join_eligibility(feature_row(left_censored=True), label_row())
        self.assertFalse(censored['eligible'])
        self.assertEqual(censored['scientific_reason'], 'feature_censored_or_roll')
        good = scientific_join_eligibility(feature_row(), label_row())
        self.assertTrue(good['eligible'])

    def test_matched_latency_changes_use_same_cut_and_reference(self):
        feat = feature_row()
        left = label_row(latency_ns=0)
        mid = label_row(latency_ns=SOURCE_LATENCY_NS)
        right = label_row(latency_ns=1_000_000_000)
        self.assertTrue(latency_pair_eligible(feat, left, mid))
        self.assertTrue(latency_pair_eligible(feat, right, mid))
        self.assertEqual(left['cut_ns'], mid['cut_ns'])
        self.assertEqual(feat['reference_price_ticks'], 100)
        other_cut = label_row(cut_ns=feat['cut_ns'] + 5 * 60 * 1_000_000_000, latency_ns=0)
        self.assertFalse(latency_pair_eligible(feat, other_cut, mid))

    def test_formation_comparisons_with_different_prior_reference_are_not_paired(self):
        label = label_row()
        left = feature_row(formation_minutes=5, reference_event_ns=_cut() - 2_000_000_000,
                           reference_source_order=1, reference_price_ticks=100)
        same = feature_row(formation_minutes=15, reference_event_ns=_cut() - 2_000_000_000,
                           reference_source_order=1, reference_price_ticks=100)
        different = feature_row(formation_minutes=60, reference_event_ns=_cut() - 9_000_000_000,
                                reference_source_order=9, reference_price_ticks=90)
        self.assertTrue(formation_pair_eligible(left, same, label))
        self.assertFalse(formation_pair_eligible(left, different, label))

    def test_equal_date_mean_balances_one_versus_one_hundred_duplicate_cuts(self):
        result = equal_date_mean({
            '2020-01-02': [10.0],
            '2020-01-03': [0.0] * 100,
        })
        self.assertEqual(result['date_mean'], 5.0)
        self.assertEqual(result['independent_dates'], 2)
        self.assertEqual(result['events'], 101)
        self.assertNotEqual(result['date_mean'], result['event_mean'])

    def test_monthly_weekly_aliases_do_not_double_date_support(self):
        result = alias_collection_dates([
            {'root': 'NQ', 'year': 2020, 'identity': 'raw-a', 'economic_date': '2020-01-02',
             'collection': 'monthly_acquisitions'},
            {'root': 'NQ', 'year': 2020, 'identity': 'raw-a', 'economic_date': '2020-01-02',
             'collection': 'weekly_acquisitions'},
            {'root': 'NQ', 'year': 2020, 'identity': 'raw-a', 'economic_date': '2020-01-03',
             'collection': 'monthly_acquisitions'},
        ])
        cell = next(iter(result.values()))
        self.assertEqual(cell['independent_economic_date_count'], 2)
        self.assertEqual(cell['source_window_rows'], 3)
        self.assertNotEqual(cell['independent_economic_date_count'], 3)
        self.assertTrue(cell['aliases_are_not_extra_independent_support'])

    def test_true_cvd_high7_low_minus2_close1_has_range9(self):
        self.assertEqual(true_path_range(7, -2, close=1), 9)
        self.assertNotEqual(true_path_range(7, -2, close=1), abs(1))
        self.assertNotEqual(true_path_range(7, -2, close=1), abs(1 - 0))

    def test_distinct_source_cohorts_overlap(self):
        ny = cohort_volume_fraction(60, 100)
        london = cohort_volume_fraction(50, 100)
        mid = cohort_volume_fraction(80, 100)
        self.assertEqual(ny, 0.6)
        self.assertGreater(ny + london + mid, 1.0)
        self.assertNotEqual(ny + london + mid, 1.0)

    def test_event_at_cut_is_excluded_from_formation(self):
        cut = _cut()
        start = cut - 5 * 60 * 1_000_000_000
        self.assertFalse(event_in_formation(cut, start, cut))
        self.assertTrue(event_in_formation(cut - 1, start, cut))
        self.assertTrue(event_in_formation(start, start, cut))
        self.assertFalse(event_in_formation(start - 1, start, cut))

    def test_timed_relative_boundaries_are_half_open(self):
        cut = _cut()
        minute = 60 * 1_000_000_000
        self.assertEqual(event_relative_bucket(cut - 60 * minute, cut), '[-60,-15)')
        self.assertEqual(event_relative_bucket(cut - 15 * minute, cut), '[-15,0)')
        self.assertEqual(event_relative_bucket(cut - 1, cut), '[-15,0)')
        self.assertEqual(event_relative_bucket(cut, cut), '[0,15)')
        self.assertEqual(event_relative_bucket(cut + 15 * minute, cut), '[15,60)')
        self.assertIsNone(event_relative_bucket(cut + 60 * minute, cut))
        self.assertIsNone(event_relative_bucket(cut - 60 * minute - 1, cut))

    def test_date_only_remains_date_only(self):
        event = {
            'time_basis': 'date_only', 'time_precision': 'date_only',
            'event_ts_utc_ns': None, 'intraday_functions_defined': False,
        }
        self.assertFalse(timed_event_eligible(event))
        self.assertIsNone(event_relative_bucket(None, _cut()))

    def test_missing_event_calendar_is_unknown(self):
        self.assertEqual(event_coverage_state(False), 'unknown')
        self.assertEqual(event_coverage_state(True), 'recorded')
        self.assertNotEqual(event_coverage_state(False), 'ordinary')

    def test_zero_past_and_zero_future_signs_are_explicit(self):
        both = directional_concordance(4, 10)
        self.assertTrue(both['concordant'])
        self.assertTrue(both['both_nonzero'])
        past = directional_concordance(0, 10)
        self.assertTrue(past['zero_past'])
        self.assertFalse(past['both_nonzero'])
        self.assertIsNone(past['concordant'])
        future = directional_concordance(4, 0)
        self.assertTrue(future['zero_future'])
        self.assertIsNone(future['concordant'])
        zeros = directional_concordance(0, 0)
        self.assertEqual(zeros['category'], 'zero_past_and_future')

    def test_year_stage_date_universe_excludes_unrelated_years_and_keeps_gaps(self):
        training = intended_date_universe(2020, 'training', 'NQ')
        self.assertIn('2020-01-02', training)
        self.assertIn('2020-06-15', training)
        self.assertNotIn('2021-06-15', training)
        self.assertNotIn('2019-12-31', training)
        self.assertGreater(len(training), 300)
        es_2021_training = intended_date_universe(2021, 'training', 'ES')
        self.assertEqual(es_2021_training, ())
        es_2021_unassigned = intended_date_universe(2021, 'unassigned', 'ES')
        self.assertIn('2021-06-15', es_2021_unassigned)

    def test_reference_must_be_strictly_inside_formation(self):
        cut = _cut()
        start = cut - 5 * 60 * 1_000_000_000
        self.assertTrue(reference_inside_formation(cut - 1, start, cut))
        self.assertFalse(reference_inside_formation(cut, start, cut))
        self.assertFalse(reference_inside_formation(start - 1, start, cut))

    def test_selected_partition_keys_do_not_invent_full_completion(self):
        import pyarrow as pa
        cut = _cut()
        later = local_timestamp(date(2021, 6, 15), time(10, 0), ZONE)
        feature_schema, label_schema = _tiny_schemas(pa)
        with tempfile.TemporaryDirectory() as folder:
            pop_out = BoundedOutputs(Path(folder) / 'pop', maximum_total_bytes=8 * 1024 ** 2,
                                     maximum_file_bytes=4 * 1024 ** 2)
            first = _write_unit_series(pop_out, 'u0', feature_schema, label_schema, cut, pa)
            second = _write_unit_series(pop_out, 'u1', feature_schema, label_schema, later, pa, year=2021)
            stats_out = BoundedOutputs(Path(folder) / 'stats', maximum_total_bytes=16 * 1024 ** 2,
                                       maximum_file_bytes=8 * 1024 ** 2)
            large_ts = 2 ** 62
            result = run_window_statistics(
                population={
                    'kind': 'auction_flow_window_population_v1',
                    'family_complete': False,
                    'population_source_windows': 2,
                    'units': [first, second],
                },
                contract=frozen_contract(
                    source_collections={PATH: 'monthly_acquisitions'},
                    event_rows=[{
                        'semantic_id': 'ev-large',
                        'event_type': 'test',
                        'event_date': '2020-06-15',
                        'event_ts_utc_ns': large_ts,
                        'time_basis': 'source_timestamp',
                        'time_precision': 'intraday_timestamp',
                        'status': 'observed',
                        'primary_population': True,
                        'independent_support': True,
                        'intraday_functions_defined': True,
                        'source_path': PATH,
                        'source_sha256': SHA,
                        'physical_row': 0,
                    }, {
                        'semantic_id': 'ev-none',
                        'event_type': 'orphan',
                        'event_date': '2020-06-16',
                        'event_ts_utc_ns': None,
                        'time_basis': 'date_only',
                        'time_precision': 'date_only',
                        'status': 'observed',
                        'primary_population': True,
                        'independent_support': True,
                        'intraday_functions_defined': False,
                    }],
                ),
                outputs=stats_out, load_reference=refuse_reference,
                selected_partition_keys=[['monthly_acquisitions', 'NQ', 2020]],
            )
            self.assertTrue(result['passed'])
            self.assertFalse(result['family_complete'])
            self.assertFalse(result['complete_family_statistics'])
            self.assertFalse(result['full_window_population_reduced'])
            self.assertTrue(result['selected_partition_subset'])
            self.assertEqual(result['kind'], KIND)
            self.assertIn('partition_measurements', result)
            self.assertEqual(len(result['partition_keys']), 1)
            self.assertEqual(result['partition_keys'][0], encode_window_partition_key(
                ('monthly_acquisitions', 'NQ', 2020)))
            links = result['refs']['event_links'][0]
            import pyarrow.parquet as pq
            table = pq.read_table(Path(links['files'][0]['path']))
            stamps = table.column('event_ts_utc_ns').to_pylist()
            self.assertIn(large_ts, stamps)
            self.assertEqual(stamps[stamps.index(large_ts)], large_ts)
            causal = table.column('causal_feature_eligible').to_pylist()
            known = table.column('known_at_ns').to_pylist()
            self.assertTrue(all(flag is False for flag in causal))
            self.assertTrue(all(value is None for value in known))
            types = table.column('event_type').to_pylist()
            self.assertIn('orphan', types)
            no_window = table.column('no_window').to_pylist()
            self.assertTrue(any(no_window))
            groups = json.loads(Path(result['refs']['groups'][0]['path']).read_bytes())['groups']
            intended = None
            for group in groups:
                if group.get('stage') == 'training' and group.get('year') == 2020:
                    intended = group['intended_dates']
                    break
            self.assertIsNotNone(intended)
            self.assertIn('2020-01-03', intended)
            self.assertNotIn('2021-06-15', intended)
            report = Path(result['refs']['report']['path']).read_text()
            self.assertIn('family_complete: false', report)
            completeness = json.loads(Path(result['refs']['completeness']['path']).read_bytes())
            self.assertGreater(completeness['unknown_event_coverage_dates'], 0)


def _tiny_schemas(pa):
    feature_fields = [
        ('root', pa.string()), ('source_path', pa.string()),
        ('source_metadata_sha256', pa.string()), ('source_variant', pa.string()),
        ('acquired_event_start_ns', pa.int64()), ('acquired_event_end_ns', pa.int64()),
        ('instrument_id', pa.int64()), ('contract_key', pa.string()),
        ('formation_minutes', pa.int64()), ('cut_ns', pa.int64()),
        ('event_start_ns', pa.int64()), ('event_end_ns', pa.int64()),
        ('known_at_ns', pa.int64()), ('formation_id', pa.string()),
        ('left_censored', pa.bool_()), ('right_censored', pa.bool_()),
        ('contract_transition', pa.bool_()),
        ('reference_price_ticks', pa.int64()), ('reference_event_ns', pa.int64()),
        ('reference_source_order', pa.int64()),
        ('all__volume', pa.int64()), ('all__unknown', pa.int64()), ('all__close', pa.int64()),
        ('all__high', pa.int64()), ('all__low', pa.int64()),
        ('observed_high_ticks', pa.int64()), ('observed_low_ticks', pa.int64()),
        ('ofi_high', pa.int64()), ('ofi_low', pa.int64()),
        ('variance_ticks_squared', pa.float64()),
        ('duration_mean_spread_ticks', pa.float64()),
        ('full_standing_window_eligible', pa.bool_()),
        ('full_pressure_transition_window_eligible', pa.bool_()),
    ]
    for name in FEATURE_QUALITY_FLAGS:
        feature_fields.append((name, pa.bool_()))
    for cohort in ('ny_ge100', 'london_ge75', 'inclusive30_through60'):
        for field in ('volume', 'buy', 'sell', 'high', 'low', 'close'):
            feature_fields.append((f'{cohort}__{field}', pa.int64()))
    label_fields = [
        ('root', pa.string()), ('source_path', pa.string()),
        ('source_metadata_sha256', pa.string()), ('source_variant', pa.string()),
        ('acquired_event_start_ns', pa.int64()), ('acquired_event_end_ns', pa.int64()),
        ('instrument_id', pa.int64()), ('contract_key', pa.string()),
        ('cut_ns', pa.int64()), ('latency_ns', pa.int64()),
        ('horizon_kind', pa.string()), ('horizon_minutes', pa.int64()),
        ('event_start_ns', pa.int64()), ('event_end_ns', pa.int64()),
        ('known_at_ns', pa.int64()), ('label_id', pa.string()),
        ('complete', pa.bool_()), ('left_censored', pa.bool_()),
        ('right_censored', pa.bool_()), ('contract_transition', pa.bool_()),
        ('no_new_trade', pa.bool_()), ('no_priced_trade', pa.bool_()),
        ('last_priced_ticks', pa.int64()),
        ('observed_high_ticks', pa.int64()), ('observed_low_ticks', pa.int64()),
        ('signed_open', pa.int64()), ('signed_close', pa.int64()),
        ('buy', pa.int64()), ('sell', pa.int64()),
    ]
    return pa.schema(feature_fields), pa.schema(label_fields)


def _write_unit_series(outputs, name, feature_schema, label_schema, cut, pa, *, year=2020):
    ident = _identity()
    if year == 2021:
        ident = {
            **ident,
            'acquired_event_start_ns': cut - 4 * 60 * 60 * 1_000_000_000,
            'acquired_event_end_ns': cut + 8 * 60 * 60 * 1_000_000_000,
        }
    start = cut - 5 * 60 * 1_000_000_000
    feature = {field.name: None for field in feature_schema}
    feature.update(ident)
    feature.update(_quality())
    feature.update({
        'instrument_id': 7, 'contract_key': 'NQ:H0', 'formation_minutes': 5,
        'cut_ns': cut, 'event_start_ns': start, 'event_end_ns': cut,
        'known_at_ns': cut + SOURCE_LATENCY_NS, 'formation_id': f'{name}-f',
        'reference_price_ticks': 100, 'reference_event_ns': cut - 1_000_000_000,
        'reference_source_order': 3, 'all__volume': 20, 'all__unknown': 2, 'all__close': 4,
        'all__high': 7, 'all__low': -2, 'observed_high_ticks': 105, 'observed_low_ticks': 95,
        'ofi_high': 3, 'ofi_low': -1, 'variance_ticks_squared': 1.5,
        'duration_mean_spread_ticks': 2.0,
        'full_standing_window_eligible': True,
        'full_pressure_transition_window_eligible': True,
        'ny_ge100__volume': 8, 'london_ge75__volume': 7, 'inclusive30_through60__volume': 12,
        'ny_ge100__buy': 5, 'ny_ge100__sell': 3, 'london_ge75__buy': 4, 'london_ge75__sell': 2,
        'inclusive30_through60__buy': 6, 'inclusive30_through60__sell': 4,
        'ny_ge100__high': 7, 'ny_ge100__low': -2, 'ny_ge100__close': 1,
        'london_ge75__high': 2, 'london_ge75__low': 0, 'london_ge75__close': 1,
        'inclusive30_through60__high': 3, 'inclusive30_through60__low': -1,
        'inclusive30_through60__close': 1,
    })
    labels = []
    for latency in (0, SOURCE_LATENCY_NS, 1_000_000_000):
        target_start = cut + latency
        target_end = target_start + 5 * 60 * 1_000_000_000
        label = {field.name: None for field in label_schema}
        label.update(ident)
        label.update({
            'instrument_id': 7, 'contract_key': 'NQ:H0', 'cut_ns': cut,
            'latency_ns': latency, 'horizon_kind': 'fixed_minutes', 'horizon_minutes': 5,
            'event_start_ns': target_start, 'event_end_ns': target_end,
            'known_at_ns': target_end + latency, 'label_id': f'{name}-{latency}',
            'complete': True, 'left_censored': False, 'right_censored': False,
            'contract_transition': False, 'no_new_trade': False, 'no_priced_trade': False,
            'last_priced_ticks': 110, 'observed_high_ticks': 110, 'observed_low_ticks': 100,
            'signed_open': 0, 'signed_close': 2, 'buy': 3, 'sell': 1,
        })
        labels.append(label)
    features = pa.table({field.name: [feature[field.name]] for field in feature_schema},
                        schema=feature_schema)
    labels_table = pa.table(
        {field.name: [row[field.name] for row in labels] for field in label_schema},
        schema=label_schema,
    )
    feat_series = ParquetSeries(outputs, f'{name}-features', encoding='plain')
    feat_series.append(features)
    stored_features = feat_series.finish()
    lab_series = ParquetSeries(outputs, f'{name}-labels', encoding='plain')
    lab_series.append(labels_table)
    stored_labels = lab_series.finish()
    return {
        'kind': 'auction_flow_window_unit_v1',
        'unit_id': [PATH, ident['acquired_event_start_ns'], ident['acquired_event_end_ns']],
        'source_identity': ident,
        'root': 'NQ',
        'source_path': PATH,
        'cut_start_ns': ident['acquired_event_start_ns'],
        'cut_end_ns': ident['acquired_event_end_ns'],
        'features': stored_features,
        'labels': stored_labels,
        'feature_rows': 1,
        'label_rows': 3,
        'instrument_count': 1,
        'cut_count': 1,
        'complete_feature_rows': 1,
        'complete_label_rows': 3,
        'censored_feature_rows': 0,
        'censored_label_rows': 0,
    }


if __name__ == '__main__':
    unittest.main()
