from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import tempfile
import unittest

from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_arrow import value_digest
from trading_research.research.auction_flow_measurements import SOURCE_FILTERS
from trading_research.research.auction_flow_observation_tables import (
    BATCH_ROWS,
    VERSION,
    observation_column_names,
    observation_rows,
    observation_schema,
    observation_table,
    write_observation_unit,
)
from trading_research.research.auction_flow_production import (
    WINDOW_RECEIPT_KIND,
    source_variant,
    window_artifact_prefix,
)
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries, read_series_tables


SOURCE_PATH = 'quantpad/cme__nq-continuous-futures__mbp-1/2019.parquet'
SOURCE_META = 'aa' * 32
RECEIPT_SHA = 'bb' * 32
MEASUREMENT_SHA = 'cc' * 32
CANONICAL_SHA = 'dd' * 32
COORDINATE = 'ee' * 32
EXPECTED_COLUMNS = (
    'root', 'source_path', 'source_metadata_sha256', 'source_variant',
    'source_window_start_ns', 'source_window_end_ns',
    'receipt_sha256', 'measurement_sha256', 'canonical_raw_values_sha256',
    'instrument_id', 'contract_key',
    'event_start_ns', 'event_end_ns', 'known_at_ns', 'atomic_bin',
    'coordinate_complete', 'supplied_raw_coordinate_stable', 'source_instrument_presence',
    'source_coverage_complete', 'flow_history_complete', 'price_history_complete',
    'empty_observed_window', 'quote_coverage_complete',
    'full_standing_window_eligible', 'full_pressure_transition_window_eligible',
    'archive_window_complete',
    'raw_rows', 'non_snapshot_rows', 'gap_rows', 'snapshot_rows',
    'unknown_action_rows', 'invalid_trade_size_rows', 'clock_uncertain_intervals',
    'prints', 'unpriced_prints',
    'first_priced_ticks', 'first_priced_event_ns', 'first_priced_known_at_ns',
    'first_priced_source_order', 'first_priced_source_row',
    'last_priced_ticks', 'last_priced_event_ns', 'last_priced_known_at_ns',
    'last_priced_source_order', 'last_priced_source_row',
    'observed_high_ticks', 'observed_low_ticks',
    'observed_high_at_ns', 'observed_low_at_ns',
    'observed_high_source_order', 'observed_low_source_order',
    'observed_price_variation_ticks', 'observed_up_variation_ticks',
    'observed_down_variation_ticks', 'observed_squared_price_variation_ticks_squared',
    'observed_adjacent_priced_pairs', 'observed_maximum_same_side_run',
    'same_time_adjacent_prints', 'terminal_run_right_censored',
)
COHORT_SUFFIXES = (
    'buy', 'sell', 'unknown', 'volume', 'prints', 'excluded_prints', 'excluded_volume',
    'open', 'high', 'low', 'close', 'high_at_ns', 'low_at_ns',
    'high_source_order', 'low_source_order', 'coverage_complete',
    'observed_signed_lower', 'observed_signed_upper',
    'true_signed_lower', 'true_signed_upper',
)
TRAILING_COLUMNS = (
    'priced_volume', 'sum_price_volume', 'sum_price_squared_volume',
    'vwap_ticks', 'variance_ticks_squared',
    'weighted_price_quantile05', 'weighted_price_quantile25',
    'weighted_price_quantile50', 'weighted_price_quantile75',
    'weighted_price_quantile95',
    'print_size_quantile25', 'print_size_quantile50',
    'print_size_quantile75', 'print_size_quantile95',
    'count_intensity_per_second', 'volume_intensity_per_second',
    'priced_buy', 'priced_sell', 'priced_unknown',
    'unpriced_buy', 'unpriced_sell', 'unpriced_unknown',
    'occupied_price_rows',
    'poc_maximizer_count', 'poc_first_row', 'poc_last_row',
    'max_mass_fraction', 'side_concentration', 'signed_concentration',
    'quote_or_invalidation_rows', 'fresh_quote_updates', 'pressure_transitions',
    'ofi_contracts', 'price_change_ofi', 'same_price_size_ofi',
    'ofi_open', 'ofi_high', 'ofi_low', 'ofi_close',
    'ofi_high_at_ns', 'ofi_low_at_ns', 'ofi_high_source_order', 'ofi_low_source_order',
    'invalid_book_rows', 'quote_gap_rows', 'quote_snapshot_rows', 'clear_rows',
    'standing_duration_ns',
    'duration_mean_spread_ticks', 'duration_mean_imbalance',
    'update_mean_spread_ticks', 'update_mean_imbalance',
    'update_mean_microprice_residual', 'sum_depth_normalized_ofi',
)


def expected_columns():
    names = list(EXPECTED_COLUMNS)
    for cohort in SOURCE_FILTERS:
        names.extend(f'{cohort}__{suffix}' for suffix in COHORT_SUFFIXES)
    names.extend(TRAILING_COLUMNS)
    return tuple(names)


def flow(name, *, buy, sell, unknown, prints, excluded_prints, excluded_volume,
         high=None, low=None, high_at_ns=None, low_at_ns=None,
         high_source_order=None, low_source_order=None, coverage_complete=True, opening=0):
    volume = buy + sell + unknown
    close = opening + buy - sell
    if high is None:
        high = max(opening, close)
    if low is None:
        low = min(opening, close)
    return {
        'filter': name, 'buy': buy, 'sell': sell, 'unknown': unknown, 'volume': volume,
        'prints': prints, 'excluded_prints': excluded_prints, 'excluded_volume': excluded_volume,
        'open': opening, 'high': high, 'low': low, 'close': close,
        'high_at_ns': high_at_ns, 'low_at_ns': low_at_ns,
        'high_source_order': high_source_order, 'low_source_order': low_source_order,
        'coverage_complete': coverage_complete,
        'observed_signed_lower': close - unknown,
        'observed_signed_upper': close + unknown,
        'true_signed_lower': (close - unknown) if coverage_complete else None,
        'true_signed_upper': (close + unknown) if coverage_complete else None,
    }


def excluded_from_all(name, all_flow, *, coverage_complete=True):
    return flow(name, buy=0, sell=0, unknown=0, prints=0,
                excluded_prints=all_flow['prints'], excluded_volume=all_flow['volume'],
                coverage_complete=coverage_complete)


def empty_quote(*, instrument_id, start, end, known, coverage_complete, standing=False, pressure=False,
                duration=0, ofi_path=None, rows=0, means=None):
    path = {'open': 0, 'high': 0, 'low': 0, 'close': 0,
            'high_at_ns': None, 'low_at_ns': None, 'high_source_order': None, 'low_source_order': None}
    if ofi_path is not None:
        path = ofi_path
    return {
        'instrument_id': instrument_id, 'event_start_ns': start, 'event_end_ns': end, 'known_at_ns': known,
        'coverage_complete': coverage_complete,
        'full_standing_window_eligible': standing,
        'full_pressure_transition_window_eligible': pressure,
        'quote_or_invalidation_rows': rows, 'fresh_quote_updates': 0, 'pressure_transitions': 0,
        'ofi_contracts': path['close'], 'price_change_ofi': 0, 'same_price_size_ofi': 0,
        'ofi_path': path,
        'invalid_book_rows': 0, 'gap_rows': 0, 'snapshot_rows': 0, 'clear_rows': 0,
        'observed_trusted_standing_duration_ns': duration,
        'duration_mean_spread_ticks': None if means is None else means.get('duration_spread'),
        'duration_mean_imbalance': None if means is None else means.get('duration_imbalance'),
        'update_mean_spread_ticks': None if means is None else means.get('update_spread'),
        'update_mean_imbalance': None if means is None else means.get('update_imbalance'),
        'update_mean_microprice_minus_midpoint_ticks': None if means is None else means.get('microprice'),
        'sum_depth_normalized_ofi': None if means is None else means.get('normalized'),
    }


def empty_weighted():
    return {
        'priced_volume': 0, 'sum_price_volume': 0, 'sum_price_squared_volume': 0,
        'vwap_ticks': None, 'variance_ticks_squared': None,
        'weighted_quantile_ticks': {'1/20': None, '1/4': None, '1/2': None, '3/4': None, '19/20': None},
    }


def empty_profile(*, coverage_complete=True):
    return {
        'coverage_complete': coverage_complete, 'origin_ticks': 0, 'row_ticks': 1,
        'rows': [], 'unpriced_buy_sell_unknown': [0, 0, 0], 'total_volume': 0,
    }


def tape(*, instrument_id, start, end, known, flows, prints, coverage_complete, coordinate_complete,
         empty_observed_window, unpriced=0, first_priced=None, last_priced=None,
         high=None, low=None, high_at=None, low_at=None, high_order=None, low_order=None,
         variation=0, up=0, down=0, squared=0, pairs=0, run=0, same_time=0, censored=False,
         weighted=None, profile=None, size_quantiles=None, count_intensity=None, volume_intensity=None):
    return {
        'instrument_id': instrument_id, 'event_start_ns': start, 'event_end_ns': end, 'known_at_ns': known,
        'source_coverage_complete': coverage_complete, 'coordinate_complete': coordinate_complete,
        'flow_history_complete': coverage_complete,
        'price_history_complete': bool(coverage_complete and coordinate_complete and unpriced == 0),
        'empty_observed_window': empty_observed_window,
        'prints': prints, 'unpriced_prints': unpriced,
        'first_priced_trade': first_priced, 'last_priced_trade': last_priced,
        'observed_high_ticks': high, 'observed_low_ticks': low,
        'observed_high_at_ns': high_at, 'observed_low_at_ns': low_at,
        'observed_high_source_order': high_order, 'observed_low_source_order': low_order,
        'observed_price_variation_ticks': variation, 'observed_up_variation_ticks': up,
        'observed_down_variation_ticks': down, 'observed_squared_price_variation_ticks_squared': squared,
        'observed_adjacent_priced_pairs': pairs, 'observed_maximum_same_side_run': run,
        'same_time_adjacent_prints': same_time, 'terminal_run_right_censored': censored,
        'flows': flows, 'weighted_price': empty_weighted() if weighted is None else weighted,
        'sparse_profile': empty_profile(coverage_complete=coverage_complete and coordinate_complete and unpriced == 0)
        if profile is None else profile,
        'count_weighted_size_quantiles': (
            {'1/4': None, '1/2': None, '3/4': None, '19/20': None} if size_quantiles is None else size_quantiles),
        'count_intensity_per_second': count_intensity,
        'volume_intensity_per_second': volume_intensity,
    }


def atom(*, instrument_id, number, start, end, known, trade, quote, coordinate, quality=None,
         presence=True, stable=True):
    return {
        'bin': number, 'instrument_id': instrument_id,
        'event_start_ns': start, 'event_end_ns': end, 'known_at_ns': known,
        'coordinate': coordinate, 'trade': trade, 'quote': quote,
        'source_quality': {} if quality is None else quality,
        'source_instrument_presence': presence,
        'supplied_raw_coordinate_stable': stable,
    }


def coordinate(*, complete, contract_key='NQ:NQH0:7:0:1000'):
    return {
        'complete': complete, 'contract_key': contract_key,
        'availability_rule': 'retained conservative definition known-at <= event time; physical lifetime checked separately',
        'source_versions': [],
    }


def receipt_and_measured(*, instruments, start, end, width, latency=250, archive=None, counts=None,
                         quote_rows=None, raw_rows=None):
    trades = sum(inst['whole_window']['prints'] for inst in instruments)
    volume = sum(inst['whole_window']['flows']['all']['volume'] for inst in instruments)
    quotes = sum(w['quote']['quote_or_invalidation_rows'] for inst in instruments for w in inst['atomic_windows'])
    if quote_rows is None:
        quote_rows = quotes
    unit = {
        'root': 'NQ', 'source_path': SOURCE_PATH, 'source_metadata_sha256': SOURCE_META,
        'event_start_ns': start, 'event_end_ns': end,
    }
    stream = {'sha256': CANONICAL_SHA, 'rows': 1, 'version': 'all-eleven-fields-fixed-65536-row-values-v2',
              'comparison_scope': 'actual ordered selected values and multiplicity'}
    receipt = {
        'kind': WINDOW_RECEIPT_KIND, 'success': True, 'status': 'measured',
        'unit': unit,
        'unit_identity': {**unit, 'source_variant': source_variant(SOURCE_PATH)},
        'source_metadata_sha256': SOURCE_META,
        'parameters': {'latency_ns': latency, 'atomic_width_ns': width, 'native_width_ns': 10,
                       'source_clock_policy': None},
        'coordinate_version': COORDINATE, 'coordinate_snapshot_version': None,
        'counts': {'trades': trades, 'volume': volume, 'quote_rows': quote_rows,
                   **({} if raw_rows is None else {'raw_rows': raw_rows})},
        'artifacts': {'measurement': {'sha256': MEASUREMENT_SHA, 'uncompressed_sha256': MEASUREMENT_SHA}},
        'source_manifest_identity': {'canonical_selected_raw_stream': stream},
    }
    if counts is not None:
        receipt['counts'] = counts
    measured = {
        'status': 'measured', 'root': 'NQ',
        'event_start_ns': start, 'event_end_ns': end, 'known_at_ns': end + latency,
        'atomic_width_ns': width,
        'coordinate_manifest_version': COORDINATE, 'coordinate_snapshot_supplement_version': None,
        'source_archive_intervals': [(0, 10**12)] if archive is None else archive,
        'source_manifest': {'canonical_selected_raw_stream': stream},
        'instruments': instruments,
    }
    reference = {'path': '/tmp/receipt.json', 'sha256': RECEIPT_SHA, 'size_bytes': 12,
                 'kind': WINDOW_RECEIPT_KIND}
    return receipt, measured, reference


def one_instrument(*, instrument_id=7, start=0, end=100, width=100, latency=250, atoms, whole=None):
    if whole is None:
        whole = {
            'instrument_id': instrument_id, 'event_start_ns': start, 'event_end_ns': end,
            'known_at_ns': end + latency,
            'prints': sum(a['trade']['prints'] for a in atoms),
            'flows': {
                name: {
                    'filter': name,
                    'buy': sum(a['trade']['flows'][name]['buy'] for a in atoms),
                    'sell': sum(a['trade']['flows'][name]['sell'] for a in atoms),
                    'unknown': sum(a['trade']['flows'][name]['unknown'] for a in atoms),
                    'volume': sum(a['trade']['flows'][name]['volume'] for a in atoms),
                    'prints': sum(a['trade']['flows'][name]['prints'] for a in atoms),
                    'excluded_prints': sum(a['trade']['flows'][name]['excluded_prints'] for a in atoms),
                    'excluded_volume': sum(a['trade']['flows'][name]['excluded_volume'] for a in atoms),
                    'open': 0,
                    'close': sum(a['trade']['flows'][name]['close'] - a['trade']['flows'][name]['open'] for a in atoms),
                    'high': max(a['trade']['flows'][name]['high'] for a in atoms),
                    'low': min(a['trade']['flows'][name]['low'] for a in atoms),
                    'high_at_ns': None, 'low_at_ns': None,
                    'high_source_order': None, 'low_source_order': None,
                    'coverage_complete': all(a['trade']['flows'][name]['coverage_complete'] for a in atoms),
                }
                for name in SOURCE_FILTERS
            },
        }
        for name in SOURCE_FILTERS:
            item = whole['flows'][name]
            item['observed_signed_lower'] = item['close'] - item['unknown']
            item['observed_signed_upper'] = item['close'] + item['unknown']
            complete = item['coverage_complete']
            item['true_signed_lower'] = item['observed_signed_lower'] if complete else None
            item['true_signed_upper'] = item['observed_signed_upper'] if complete else None
            if item['high'] < max(item['open'], item['close']):
                item['high'] = max(item['open'], item['close'])
            if item['low'] > min(item['open'], item['close']):
                item['low'] = min(item['open'], item['close'])
    return {'instrument_id': instrument_id, 'whole_window': whole, 'atomic_windows': atoms,
            'coordinate': coordinate(complete=True, contract_key=f'NQ:NQH0:{instrument_id}:0:1000')}


def volume6_flows(*, coverage_complete=True):
    all_flow = flow('all', buy=3, sell=2, unknown=1, prints=3, excluded_prints=0, excluded_volume=0,
                    high=3, low=0, high_at_ns=10, high_source_order=1, coverage_complete=coverage_complete)
    return {
        'all': all_flow,
        'ny_ge100': excluded_from_all('ny_ge100', all_flow, coverage_complete=coverage_complete),
        'london_ge75': excluded_from_all('london_ge75', all_flow, coverage_complete=coverage_complete),
        'inclusive30_through60': excluded_from_all('inclusive30_through60', all_flow,
                                                  coverage_complete=coverage_complete),
    }


def volume6_atom(*, instrument_id=7, number=0, start=0, end=100, latency=250, coverage_complete=True,
                 coordinate_complete=True, contract_key='NQ:NQH0:7:0:1000', quality=None,
                 archive_means=True, fractions='objects'):
    known = end + latency
    flows = volume6_flows(coverage_complete=coverage_complete)
    vwap = Fraction(10) if fractions == 'objects' else {'$fraction': [10, 1]}
    variance = Fraction(0) if fractions == 'objects' else {'$fraction': [0, 1]}
    q = Fraction(3, 2) if fractions == 'objects' else {'$fraction': [3, 2]}
    intensity = Fraction(3 * 10**9, end - start) if coverage_complete else None
    volume_intensity = Fraction(6 * 10**9, end - start) if coverage_complete else None
    if coverage_complete and fractions == 'tagged' and intensity is not None:
        intensity = {'$fraction': [intensity.numerator, intensity.denominator]}
        volume_intensity = {'$fraction': [volume_intensity.numerator, volume_intensity.denominator]}
    weighted = {
        'priced_volume': 6, 'sum_price_volume': 60, 'sum_price_squared_volume': 600,
        'vwap_ticks': vwap, 'variance_ticks_squared': variance,
        'weighted_quantile_ticks': {'1/20': 10, '1/4': 10, '1/2': 10, '3/4': 10, '19/20': 10},
    }
    profile = {
        'coverage_complete': coverage_complete and coordinate_complete,
        'origin_ticks': 0, 'row_ticks': 1,
        'rows': [[10, 3, 2, 1]],
        'unpriced_buy_sell_unknown': [0, 0, 0],
        'total_volume': 6,
    }
    trade = tape(
        instrument_id=instrument_id, start=start, end=end, known=known, flows=flows, prints=3,
        coverage_complete=coverage_complete, coordinate_complete=coordinate_complete,
        empty_observed_window=False,
        first_priced={'price_ticks': 10, 'event_ns': 10, 'known_at_ns': 10 + latency,
                      'source_order': 1, 'source_row': 1},
        last_priced={'price_ticks': 10, 'event_ns': 40, 'known_at_ns': 40 + latency,
                     'source_order': 3, 'source_row': 3},
        high=10, low=10, high_at=10, low_at=10, high_order=1, low_order=1,
        variation=0, pairs=2, run=1, same_time=0, censored=False,
        weighted=weighted, profile=profile,
        size_quantiles={'1/4': q, '1/2': Fraction(2), '3/4': Fraction(5, 2), '19/20': Fraction(29, 10)},
        count_intensity=intensity, volume_intensity=volume_intensity,
    )
    quote = empty_quote(instrument_id=instrument_id, start=start, end=end, known=known,
                        coverage_complete=coverage_complete, standing=False, rows=4,
                        means={'normalized': 0.0} if archive_means else None)
    return atom(instrument_id=instrument_id, number=number, start=start, end=end, known=known,
                trade=trade, quote=quote,
                coordinate=coordinate(complete=coordinate_complete, contract_key=contract_key),
                quality={'raw_rows': 8, 'non_snapshot_rows': 8, 'gap_rows': 0, 'snapshot_rows': 0,
                         'unknown_action_rows': 0, 'invalid_trade_size_rows': 0} if quality is None else quality)


def quiet_atom(*, instrument_id, number, start, end, latency, coverage_complete, coordinate_complete=True,
               contract_key='NQ:NQH0:7:0:1000', quality=None, clock_uncertain=None, quote_intervals=None):
    known = end + latency
    all_flow = flow('all', buy=0, sell=0, unknown=0, prints=0, excluded_prints=0, excluded_volume=0,
                    coverage_complete=coverage_complete)
    flows = {name: all_flow if name == 'all' else excluded_from_all(name, all_flow, coverage_complete=coverage_complete)
             for name in SOURCE_FILTERS}
    intensity = Fraction(0, 1) if coverage_complete else None
    trade = tape(
        instrument_id=instrument_id, start=start, end=end, known=known, flows=flows, prints=0,
        coverage_complete=coverage_complete, coordinate_complete=coordinate_complete,
        empty_observed_window=coverage_complete,
        count_intensity=intensity, volume_intensity=intensity,
        profile=empty_profile(coverage_complete=coverage_complete and coordinate_complete),
    )
    quote = empty_quote(instrument_id=instrument_id, start=start, end=end, known=known,
                        coverage_complete=coverage_complete)
    if quote_intervals is not None:
        quote['source_clock_uncertain_intervals'] = quote_intervals
    quality = {} if quality is None else dict(quality)
    if clock_uncertain is not None:
        quality['clock_uncertain_intervals'] = clock_uncertain
    return atom(instrument_id=instrument_id, number=number, start=start, end=end, known=known,
                trade=trade, quote=quote,
                coordinate=coordinate(complete=coordinate_complete, contract_key=contract_key),
                quality=quality, presence=coverage_complete, stable=True)


class AuctionFlowObservationTableTests(unittest.TestCase):
    def test_unavailable_source_window_has_no_invented_instrument_rows(self):
        receipt, measured, reference = receipt_and_measured(
            instruments=[], start=0, end=100, width=100, raw_rows=0)
        receipt['status'] = measured['status'] = 'unavailable_source_window'
        self.assertEqual(observation_rows(receipt, measured, receipt_reference=reference), [])
        with tempfile.TemporaryDirectory() as folder:
            out = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=1024**2,
                                 maximum_file_bytes=1024**2)
            result = write_observation_unit(receipt, measured, receipt_reference=reference, outputs=out)
            self.assertEqual(result['atomic_rows'], 0)
            self.assertEqual(result['root'], 'NQ')
            self.assertEqual(result['source_window_status'], 'unavailable_source_window')
            self.assertEqual(result['series']['rows'], 0)
            self.assertIsNotNone(result['series']['schema'])
        receipt['counts']['trades'] = 1
        with self.assertRaises(IntegrityError):
            observation_rows(receipt, measured, receipt_reference=reference)

    def test_adjacent_archive_spans_and_nonfinite_mean(self):
        item = volume6_atom()
        receipt, measured, reference = receipt_and_measured(
            instruments=[one_instrument(atoms=[item])], start=0, end=100, width=100,
            archive=[(0, 40), (40, 100)])
        self.assertTrue(observation_rows(receipt, measured, receipt_reference=reference)[0]['archive_window_complete'])
        item['quote']['duration_mean_imbalance'] = float('nan')
        with self.assertRaises(IntegrityError):
            observation_rows(receipt, measured, receipt_reference=reference)

    def test_literal_columns_and_denominators(self):
        self.assertEqual(observation_column_names(), expected_columns())
        self.assertEqual(observation_schema().names, list(expected_columns()))
        self.assertEqual(SOURCE_FILTERS, ('all', 'ny_ge100', 'london_ge75', 'inclusive30_through60'))
        self.assertEqual(BATCH_ROWS, 65536)
        self.assertEqual(VERSION, 'auction-flow-observation-tables-v1')
        for field in observation_schema():
            if field.name.endswith('_ns') or field.name in (
                    'instrument_id', 'atomic_bin', 'prints', 'unpriced_prints', 'priced_volume',
                    'sum_price_volume', 'sum_price_squared_volume', 'raw_rows'):
                self.assertEqual(str(field.type), 'int64')

    def test_buy3_sell2_unknown1_volume6_delta1_and_excluded_identity(self):
        item = volume6_atom()
        instrument = one_instrument(atoms=[item])
        receipt, measured, reference = receipt_and_measured(instruments=[instrument], start=0, end=100, width=100)
        rows = observation_rows(receipt, measured, receipt_reference=reference)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row['all__buy'], 3)
        self.assertEqual(row['all__sell'], 2)
        self.assertEqual(row['all__unknown'], 1)
        self.assertEqual(row['all__volume'], 6)
        self.assertEqual(row['all__close'] - row['all__open'], 1)
        self.assertEqual(row['all__volume'], row['all__buy'] + row['all__sell'] + row['all__unknown'])
        self.assertEqual(row['all__close'], row['all__open'] + row['all__buy'] - row['all__sell'])
        self.assertEqual((row['all__observed_signed_lower'], row['all__observed_signed_upper']), (0, 2))
        self.assertEqual((row['all__true_signed_lower'], row['all__true_signed_upper']), (0, 2))
        self.assertEqual(row['all__high'], 3)
        self.assertEqual(row['all__low'], 0)
        self.assertGreater(row['all__high'], max(row['all__open'], row['all__close']))
        for name in ('ny_ge100', 'london_ge75', 'inclusive30_through60'):
            self.assertEqual(row[f'{name}__volume'] + row[f'{name}__excluded_volume'], 6)
            self.assertEqual(row[f'{name}__prints'] + row[f'{name}__excluded_prints'], 3)
            self.assertEqual(row[f'{name}__volume'], 0)
            self.assertEqual(row[f'{name}__excluded_volume'], 6)
        self.assertEqual(row['ny_ge100__volume'] + row['london_ge75__volume']
                         + row['inclusive30_through60__volume'], 0)
        self.assertEqual(row['source_variant'], source_variant(SOURCE_PATH))
        self.assertEqual(row['receipt_sha256'], RECEIPT_SHA)
        self.assertEqual(row['measurement_sha256'], MEASUREMENT_SHA)
        self.assertEqual(row['canonical_raw_values_sha256'], CANONICAL_SHA)
        self.assertTrue(row['archive_window_complete'])
        self.assertEqual(row['quote_or_invalidation_rows'], 4)

    def test_unknown_bounds_null_when_coverage_incomplete(self):
        item = volume6_atom(coverage_complete=False)
        instrument = one_instrument(atoms=[item])
        receipt, measured, reference = receipt_and_measured(instruments=[instrument], start=0, end=100, width=100)
        row = observation_rows(receipt, measured, receipt_reference=reference)[0]
        self.assertEqual((row['all__observed_signed_lower'], row['all__observed_signed_upper']), (0, 2))
        self.assertIsNone(row['all__true_signed_lower'])
        self.assertIsNone(row['all__true_signed_upper'])
        self.assertFalse(row['empty_observed_window'])
        self.assertIsNone(row['count_intensity_per_second'])
        self.assertIsNone(row['volume_intensity_per_second'])

    def test_true_ohlc_interior_reversal_is_not_close(self):
        all_flow = flow('all', buy=8, sell=7, unknown=0, prints=3, excluded_prints=0, excluded_volume=0,
                        high=5, low=-2, high_at_ns=10, low_at_ns=20, high_source_order=1, low_source_order=2)
        self.assertEqual(all_flow['close'], 1)
        self.assertNotEqual(all_flow['high'], all_flow['close'])
        self.assertNotEqual(all_flow['low'], all_flow['close'])
        self.assertGreater(all_flow['high'], max(all_flow['open'], all_flow['close']))
        self.assertLess(all_flow['low'], min(all_flow['open'], all_flow['close']))
        flows = {
            'all': all_flow,
            'ny_ge100': excluded_from_all('ny_ge100', all_flow),
            'london_ge75': excluded_from_all('london_ge75', all_flow),
            'inclusive30_through60': excluded_from_all('inclusive30_through60', all_flow),
        }
        trade = tape(instrument_id=7, start=0, end=100, known=350, flows=flows, prints=3,
                     coverage_complete=True, coordinate_complete=True, empty_observed_window=False,
                     first_priced={'price_ticks': 400, 'event_ns': 10, 'known_at_ns': 260,
                                   'source_order': 1, 'source_row': 1},
                     last_priced={'price_ticks': 399, 'event_ns': 30, 'known_at_ns': 280,
                                  'source_order': 3, 'source_row': 3},
                     high=400, low=398, high_at=10, low_at=20, high_order=1, low_order=2,
                     variation=3, up=1, down=2, squared=5, pairs=2, run=1,
                     weighted={'priced_volume': 15, 'sum_price_volume': 5983, 'sum_price_squared_volume': 2386431,
                               'vwap_ticks': Fraction(5983, 15), 'variance_ticks_squared': Fraction(176, 225),
                               'weighted_quantile_ticks': {'1/20': 398, '1/4': 399, '1/2': 399, '3/4': 400, '19/20': 400}},
                     profile={'coverage_complete': True, 'rows': [[398, 0, 7, 0], [399, 3, 0, 0], [400, 5, 0, 0]],
                              'unpriced_buy_sell_unknown': [0, 0, 0], 'total_volume': 15},
                     count_intensity=Fraction(3 * 10**9, 100), volume_intensity=Fraction(15 * 10**9, 100))
        item = atom(instrument_id=7, number=0, start=0, end=100, known=350, trade=trade,
                    quote=empty_quote(instrument_id=7, start=0, end=100, known=350, coverage_complete=True),
                    coordinate=coordinate(complete=True))
        receipt, measured, reference = receipt_and_measured(
            instruments=[one_instrument(atoms=[item])], start=0, end=100, width=100)
        row = observation_rows(receipt, measured, receipt_reference=reference)[0]
        self.assertEqual((row['all__open'], row['all__high'], row['all__low'], row['all__close']), (0, 5, -2, 1))
        self.assertNotEqual(row['all__high'], row['all__close'])
        self.assertNotEqual(row['all__low'], row['all__close'])

    def test_priced_moments_and_multiple_poc_ties(self):
        item = volume6_atom()
        all_flow = flow('all', buy=6, sell=0, unknown=0, prints=3,
                        excluded_prints=0, excluded_volume=0, high=6, low=0)
        item['trade']['flows'] = {name: all_flow if name == 'all' else excluded_from_all(name, all_flow)
                                  for name in SOURCE_FILTERS}
        item['trade']['last_priced_trade']['price_ticks'] = 12
        item['trade'].update(observed_high_ticks=12, observed_price_variation_ticks=2,
                             observed_up_variation_ticks=2, observed_squared_price_variation_ticks_squared=2)
        item['trade']['sparse_profile'] = {
            'coverage_complete': True, 'rows': [[10, 2, 0, 0], [11, 2, 0, 0], [12, 2, 0, 0]],
            'unpriced_buy_sell_unknown': [0, 0, 0], 'total_volume': 6,
        }
        item['trade']['weighted_price'] = {
            'priced_volume': 6, 'sum_price_volume': 66, 'sum_price_squared_volume': 730,
            'vwap_ticks': Fraction(11), 'variance_ticks_squared': Fraction(2, 3),
            'weighted_quantile_ticks': {'1/20': 10, '1/4': 10, '1/2': 11, '3/4': 12, '19/20': 12},
        }
        receipt, measured, reference = receipt_and_measured(
            instruments=[one_instrument(atoms=[item])], start=0, end=100, width=100)
        row = observation_rows(receipt, measured, receipt_reference=reference)[0]
        self.assertEqual((row['priced_volume'], row['sum_price_volume'], row['sum_price_squared_volume']), (6, 66, 730))
        self.assertEqual(row['vwap_ticks'], 11.0)
        self.assertEqual(row['variance_ticks_squared'], float(Fraction(2, 3)))
        self.assertEqual(row['weighted_price_quantile05'], 10.0)
        self.assertEqual(row['weighted_price_quantile50'], 11.0)
        self.assertEqual(row['weighted_price_quantile95'], 12.0)
        self.assertEqual(row['print_size_quantile25'], 1.5)
        self.assertEqual((row['priced_buy'], row['priced_sell'], row['priced_unknown']), (6, 0, 0))
        self.assertEqual(row['occupied_price_rows'], 3)
        self.assertEqual(row['poc_maximizer_count'], 3)
        self.assertEqual((row['poc_first_row'], row['poc_last_row']), (10, 12))
        self.assertEqual(row['max_mass_fraction'], 2 / 6)
        self.assertEqual(row['side_concentration'], 1.0)
        self.assertEqual(row['signed_concentration'], 1.0)

    def test_fraction_tags_and_native_fractions_are_accepted(self):
        item = volume6_atom(fractions='tagged')
        receipt, measured, reference = receipt_and_measured(
            instruments=[one_instrument(atoms=[item])], start=0, end=100, width=100)
        row = observation_rows(receipt, measured, receipt_reference=reference)[0]
        self.assertEqual(row['vwap_ticks'], 10.0)
        self.assertEqual(row['variance_ticks_squared'], 0.0)
        self.assertEqual(row['count_intensity_per_second'], float(Fraction(3 * 10**9, 100)))
        self.assertEqual(row['volume_intensity_per_second'], float(Fraction(6 * 10**9, 100)))

    def test_zero_quiet_observed_is_not_missing(self):
        quiet = quiet_atom(instrument_id=7, number=0, start=0, end=100, latency=250, coverage_complete=True)
        missing = quiet_atom(instrument_id=8, number=0, start=0, end=100, latency=250, coverage_complete=False,
                             contract_key=None, coordinate_complete=False)
        missing['coordinate']['contract_key'] = None
        receipt, measured, reference = receipt_and_measured(
            instruments=[one_instrument(atoms=[quiet]), one_instrument(instrument_id=8, atoms=[missing])],
            start=0, end=100, width=100)
        rows = observation_rows(receipt, measured, receipt_reference=reference)
        self.assertEqual([row['instrument_id'] for row in rows], [7, 8])
        self.assertTrue(rows[0]['empty_observed_window'])
        self.assertEqual(rows[0]['count_intensity_per_second'], 0.0)
        self.assertEqual(rows[0]['volume_intensity_per_second'], 0.0)
        self.assertFalse(rows[1]['empty_observed_window'])
        self.assertIsNone(rows[1]['count_intensity_per_second'])
        self.assertIsNone(rows[1]['contract_key'])
        self.assertFalse(rows[1]['coordinate_complete'])

    def test_incomplete_clock_and_span_masks_stay_null_and_false(self):
        item = quiet_atom(instrument_id=7, number=0, start=0, end=100, latency=250, coverage_complete=False,
                          clock_uncertain=2, quote_intervals=[(10, 20), (40, 50)])
        item['quote']['duration_mean_spread_ticks'] = None
        item['quote']['update_mean_imbalance'] = None
        receipt, measured, reference = receipt_and_measured(
            instruments=[one_instrument(atoms=[item])], start=0, end=100, width=100,
            archive=[(200, 300)])
        row = observation_rows(receipt, measured, receipt_reference=reference)[0]
        self.assertEqual(row['clock_uncertain_intervals'], 2)
        self.assertFalse(row['archive_window_complete'])
        self.assertFalse(row['source_coverage_complete'])
        self.assertFalse(row['full_standing_window_eligible'])
        self.assertFalse(row['full_pressure_transition_window_eligible'])
        self.assertIsNone(row['duration_mean_spread_ticks'])
        self.assertIsNone(row['update_mean_imbalance'])
        item['source_quality'].pop('clock_uncertain_intervals')
        receipt, measured, reference = receipt_and_measured(
            instruments=[one_instrument(atoms=[item])], start=0, end=100, width=100, archive=[(200, 300)])
        self.assertEqual(observation_rows(receipt, measured, receipt_reference=reference)[0]['clock_uncertain_intervals'], 2)

    def test_null_coordinates_and_partial_final_atom_are_retained(self):
        first = volume6_atom(start=0, end=100, number=0)
        second = quiet_atom(instrument_id=7, number=1, start=100, end=150, latency=250,
                            coverage_complete=True, coordinate_complete=False, contract_key=None)
        second['coordinate']['contract_key'] = None
        instrument = one_instrument(atoms=[first, second], start=0, end=150, width=100)
        receipt, measured, reference = receipt_and_measured(
            instruments=[instrument], start=0, end=150, width=100, archive=[(0, 100)])
        rows = observation_rows(receipt, measured, receipt_reference=reference)
        self.assertEqual(len(rows), 2)
        self.assertEqual([row['atomic_bin'] for row in rows], [0, 1])
        self.assertEqual((rows[0]['event_start_ns'], rows[0]['event_end_ns'], rows[0]['known_at_ns']), (0, 100, 350))
        self.assertEqual((rows[1]['event_start_ns'], rows[1]['event_end_ns'], rows[1]['known_at_ns']), (100, 150, 400))
        self.assertEqual(rows[1]['event_end_ns'] - rows[1]['event_start_ns'], 50)
        self.assertIsNone(rows[1]['contract_key'])
        self.assertFalse(rows[1]['coordinate_complete'])
        self.assertTrue(rows[0]['archive_window_complete'])
        self.assertFalse(rows[1]['archive_window_complete'])
        self.assertEqual(rows[0]['prints'] + rows[1]['prints'], 3)
        self.assertEqual(rows[0]['all__volume'] + rows[1]['all__volume'], 6)

    def test_two_instruments_keep_distinct_receipt_identity(self):
        a = volume6_atom(instrument_id=7, contract_key='NQ:NQH0:7:0:1000')
        b = volume6_atom(instrument_id=11, contract_key='NQ:NQH1:11:0:1000')
        b['quote']['quote_or_invalidation_rows'] = 1
        receipt, measured, reference = receipt_and_measured(
            instruments=[one_instrument(instrument_id=7, atoms=[a]),
                         one_instrument(instrument_id=11, atoms=[b])],
            start=0, end=100, width=100)
        rows = observation_rows(receipt, measured, receipt_reference=reference)
        self.assertEqual([row['instrument_id'] for row in rows], [7, 11])
        self.assertEqual({row['contract_key'] for row in rows}, {'NQ:NQH0:7:0:1000', 'NQ:NQH1:11:0:1000'})
        self.assertEqual(sum(row['prints'] for row in rows), 6)
        self.assertEqual(sum(row['all__volume'] for row in rows), 12)
        self.assertEqual(sum(row['quote_or_invalidation_rows'] for row in rows), 5)
        self.assertEqual(receipt['counts']['trades'], 6)
        self.assertEqual(receipt['counts']['volume'], 12)
        self.assertEqual(receipt['counts']['quote_rows'], 5)

    def test_tampered_joins_counts_and_duplicate_atoms_fail(self):
        item = volume6_atom()
        instrument = one_instrument(atoms=[item])
        receipt, measured, reference = receipt_and_measured(instruments=[instrument], start=0, end=100, width=100)
        bad = deepcopy(measured)
        bad['root'] = 'ES'
        with self.assertRaises(IntegrityError):
            observation_rows(receipt, bad, receipt_reference=reference)
        bad_latency = deepcopy(receipt)
        bad_latency['parameters']['latency_ns'] = 1
        with self.assertRaises(IntegrityError):
            observation_rows(bad_latency, measured, receipt_reference=reference)
        dup = deepcopy(measured)
        dup['instruments'][0]['atomic_windows'].append(deepcopy(item))
        with self.assertRaises(IntegrityError):
            observation_rows(receipt, dup, receipt_reference=reference)
        counts = deepcopy(receipt)
        counts['counts']['volume'] = 7
        with self.assertRaises(IntegrityError):
            observation_rows(counts, measured, receipt_reference=reference)
        quotes = deepcopy(receipt)
        quotes['counts']['quote_rows'] = 0
        with self.assertRaises(IntegrityError):
            observation_rows(quotes, measured, receipt_reference=reference)
        whole = deepcopy(measured)
        whole['instruments'][0]['whole_window']['prints'] = 2
        with self.assertRaises(IntegrityError):
            observation_rows(receipt, whole, receipt_reference=reference)
        cohort = deepcopy(measured)
        cohort['instruments'][0]['atomic_windows'][0]['trade']['flows']['ny_ge100']['excluded_volume'] = 5
        with self.assertRaises(IntegrityError):
            observation_rows(receipt, cohort, receipt_reference=reference)
        unknown = deepcopy(measured)
        unknown['instruments'][0]['atomic_windows'][0]['trade']['flows']['all']['unknown'] = None
        with self.assertRaises(IntegrityError):
            observation_rows(receipt, unknown, receipt_reference=reference)
        standing = deepcopy(measured)
        standing['instruments'][0]['atomic_windows'][0]['quote']['full_standing_window_eligible'] = True
        standing['instruments'][0]['atomic_windows'][0]['trade']['source_coverage_complete'] = False
        standing['instruments'][0]['atomic_windows'][0]['trade']['flow_history_complete'] = False
        standing['instruments'][0]['atomic_windows'][0]['trade']['price_history_complete'] = False
        standing['instruments'][0]['atomic_windows'][0]['trade']['empty_observed_window'] = False
        standing['instruments'][0]['atomic_windows'][0]['quote']['coverage_complete'] = False
        for name in SOURCE_FILTERS:
            flow_row = standing['instruments'][0]['atomic_windows'][0]['trade']['flows'][name]
            flow_row['coverage_complete'] = False
            flow_row['true_signed_lower'] = None
            flow_row['true_signed_upper'] = None
        standing['instruments'][0]['atomic_windows'][0]['trade']['count_intensity_per_second'] = None
        standing['instruments'][0]['atomic_windows'][0]['trade']['volume_intensity_per_second'] = None
        standing['instruments'][0]['whole_window']['flows'] = standing['instruments'][0]['atomic_windows'][0]['trade']['flows']
        with self.assertRaises(IntegrityError):
            observation_rows(receipt, standing, receipt_reference=reference)

    def test_parquet_roundtrip_keeps_explicit_schema_across_batch_sizes(self):
        first = volume6_atom()
        second = quiet_atom(instrument_id=7, number=1, start=100, end=150, latency=250, coverage_complete=True)
        instrument = one_instrument(atoms=[first, second], start=0, end=150, width=100)
        receipt, measured, reference = receipt_and_measured(
            instruments=[instrument], start=0, end=150, width=100)
        rows = observation_rows(receipt, measured, receipt_reference=reference)
        full = observation_table(rows)
        self.assertEqual(full.schema, observation_schema())
        self.assertTrue(full.schema.equals(observation_schema(), check_metadata=True))
        self.assertEqual(full.schema.field('known_at_ns').type.bit_width, 64)
        self.assertTrue(full.schema.field('contract_key').nullable)
        self.assertFalse(full.schema.field('prints').nullable)
        self.assertEqual(full.schema.field('vwap_ticks').type, observation_schema().field('vwap_ticks').type)
        parts = [observation_table(rows[i:i + 1]) for i in range(len(rows))]
        import pyarrow as pa
        rebuilt = pa.concat_tables(parts).combine_chunks()
        self.assertEqual(value_digest(rebuilt), value_digest(full))
        with tempfile.TemporaryDirectory() as folder:
            out = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=4 * 1024**2,
                                 maximum_file_bytes=2 * 1024**2)
            summary = write_observation_unit(receipt, measured, receipt_reference=reference, outputs=out)
            self.assertEqual(summary['atomic_rows'], 2)
            self.assertEqual(summary['trade_prints'], 3)
            self.assertEqual(summary['trade_volume'], 6)
            self.assertEqual(summary['quote_rows'], 4)
            self.assertEqual(summary['receipt_counts']['trades'], 3)
            self.assertTrue(summary['whole_mass_checks']['atomic_prints_equal_receipt_trades'])
            self.assertTrue(summary['whole_mass_checks']['source_raw_rows_not_equated_to_receipt'])
            self.assertEqual(summary['eligibility_counts']['empty_observed_window'], 1)
            self.assertEqual(summary['original_refs']['receipt_sha256'], RECEIPT_SHA)
            self.assertGreater(summary['output_bytes'], 0)
            self.assertGreaterEqual(summary['cpu_seconds'], 0.0)
            self.assertFalse(summary['family_statistics_or_model_complete'])
            self.assertEqual(summary['series']['encoding'], 'structural')
            self.assertEqual(summary['series']['series'], f'{window_artifact_prefix(receipt["unit"])}-observations')
            restored = pa.concat_tables(list(read_series_tables(summary['series']))).combine_chunks()
            self.assertTrue(restored.schema.equals(observation_schema(), check_metadata=True))
            self.assertEqual(value_digest(restored), value_digest(full))
            self.assertEqual(restored['all__volume'].to_pylist(), [6, 0])
            self.assertEqual(restored['all__unknown'].to_pylist(), [1, 0])
            self.assertEqual(restored['contract_key'].to_pylist(), ['NQ:NQH0:7:0:1000', 'NQ:NQH0:7:0:1000'])
            self.assertEqual(restored['empty_observed_window'].to_pylist(), [False, True])
            other = BoundedOutputs(Path(folder) / 'out2', maximum_total_bytes=4 * 1024**2,
                                   maximum_file_bytes=2 * 1024**2)
            series = ParquetSeries(other, 'batch-check', encoding='structural')
            series.append(observation_table(rows[:1]))
            series.append(observation_table(rows[1:]))
            batched = pa.concat_tables(list(read_series_tables(series.finish()))).combine_chunks()
            self.assertEqual(value_digest(batched), value_digest(full))


if __name__ == '__main__':
    unittest.main()
