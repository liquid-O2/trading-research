from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_production import (
    WINDOW_RECEIPT_KIND, production_window_identity,
)
from trading_research.research.auction_flow_storage import (
    BoundedOutputs, ParquetSeries, read_json_artifact,
)
from trading_research.research.auction_flow_windows import TapeWindow
from trading_research.research.auction_flow_cohort_production import (
    ADAPTIVE_RECIPES, BATCH_ROWS, CONTRACT_KIND, FIXED_FILTERS, PREFIX_CONTRACT_KIND,
    SOFT_KNOTS, VERSION, TrainingCollectionAccumulator, accumulate_training_collection,
    chronological_split, collection_from_source_path, date_end_exclusive_ns, date_start_ns,
    fit_training_collection, full_population_cohort_contract, measure_source_window_cohorts,
    persist_training_fits, persist_training_histogram, restore_training_fits,
    restore_training_histogram, select_training_fits, training_bounds,
    validate_cohort_production_contract,
)
from tests.test_auction_flow_prepared_trades import make_trade_table, trade_row


MINUTE = 60_000_000_000
DELAY = 250
INSTRUMENT = 7
DAY1 = date_start_ns('2020-01-01')
DAY2 = date_start_ns('2020-01-02')
LAST_TRAIN = date_start_ns('2022-12-31')
DEV_START = date_start_ns('2023-01-01')
MONTHLY_A = 'quantpad/cme__nq-continuous-futures__mbp-1/2020-01.parquet'
MONTHLY_B = 'quantpad/cme__nq-continuous-futures__mbp-1/2022-12.parquet'
MONTHLY_EVAL = 'quantpad/cme__nq-continuous-futures__mbp-1/2023-01.parquet'
DATED_A = 'quantpad/cme__nq-continuous-futures__mbp-1/2020-01-01.parquet'
DATED_EVAL = 'quantpad/cme__nq-continuous-futures__mbp-1/2023-01-02.parquet'


def exact(value):
    if type(value) is dict and '$fraction' in value:
        return Fraction(*value['$fraction'])
    if type(value) is list:
        return [exact(item) for item in value]
    if type(value) is dict:
        return {key: exact(item) for key, item in value.items()}
    return value


def decode_atoms(block):
    bar_fields = tuple(block['schema']['bar'])
    channel_fields = tuple(block['schema']['channel'])
    bars = []
    for row, channels in zip(block['bars'], block['channels'], strict=True):
        bar = exact(dict(zip(bar_fields, row, strict=True)))
        bar['channels'] = [exact(dict(zip(channel_fields, channel, strict=True))) for channel in channels]
        bars.append(bar)
    return bars


def row(t, *, source_order, size=1, side=1, instrument_id=INSTRUMENT, source_key='src', delay=DELAY):
    raw_side = 'B' if side == 1 else 'A' if side == -1 else 'N'
    return trade_row(t, source_order=source_order, size=size, raw_side=raw_side, delay=delay,
                     instrument_id=instrument_id, source_key=source_key, source_row=source_order)


def write_series(outputs, name, tables):
    series = ParquetSeries(outputs, name, encoding='plain')
    for table in tables:
        if len(table):
            series.append(table)
    return series.finish()


def build_measured(rows, *, start, end, delay, atoms, instrument_id=INSTRUMENT,
                   source_complete=True, coordinate_complete=True):
    owned = [item for item in rows if item['instrument_id'] == instrument_id]
    whole = TapeWindow(instrument_id=instrument_id, start_ns=start, end_ns=end, latency_ns=delay)
    if owned:
        whole.add(make_trade_table(owned))
    atomic = []
    for number, (a, b, src, coord) in enumerate(atoms):
        tape = TapeWindow(instrument_id=instrument_id, start_ns=a, end_ns=b, latency_ns=delay)
        part = [item for item in owned if a <= item['t'] < b]
        if part:
            tape.add(make_trade_table(part))
        atomic.append({
            'bin': number, 'event_start_ns': a, 'event_end_ns': b,
            'known_at_ns': b + delay, 'instrument_id': instrument_id,
            'coordinate': {'complete': coord, 'contract_key': f'TEST:{instrument_id}'},
            'trade': tape.record(source_coverage_complete=src, coordinate_complete=coord),
        })
    return {
        'event_start_ns': start, 'event_end_ns': end, 'known_at_ns': end + delay,
        'instruments': [{
            'instrument_id': instrument_id,
            'coordinate': {'complete': coordinate_complete, 'contract_key': f'TEST:{instrument_id}'},
            'whole_window': whole.record(source_coverage_complete=source_complete,
                                         coordinate_complete=coordinate_complete),
            'atomic_windows': atomic,
        }],
    }


def member(root, path, start, end, date, *, sha=None):
    return {
        'root': root, 'source_path': path, 'source_metadata_sha256': sha or digest(path),
        'event_start_ns': start, 'event_end_ns': end, 'utc_date': date,
    }


def unit_from(item):
    return {
        'root': item['root'], 'source_path': item['source_path'],
        'source_metadata_sha256': item['source_metadata_sha256'],
        'event_start_ns': item['event_start_ns'], 'event_end_ns': item['event_end_ns'],
        'utc_date': item['utc_date'],
        'whole_window_inside_acquired_file': True,
    }


def write_receipt(folder, name, item, rows, *, delay=DELAY, atoms=None, source_complete=True,
                  coordinate_complete=True, mutate_measurement=None):
    outputs = BoundedOutputs(Path(folder) / name, maximum_total_bytes=8 * 1024 ** 2,
                             maximum_file_bytes=4 * 1024 ** 2)
    trades = write_series(outputs, f'{name}-trades', [make_trade_table(rows)] if rows else [])
    start, end = item['event_start_ns'], item['event_end_ns']
    atoms = atoms or ((start, end, source_complete, coordinate_complete),)
    measured = build_measured(rows, start=start, end=end, delay=delay, atoms=atoms,
                              source_complete=source_complete, coordinate_complete=coordinate_complete)
    if mutate_measurement is not None:
        mutate_measurement(measured)
    measurement = outputs.json_compressed(f'{name}-measurements.json.zst', measured,
                                          kind='auction_flow_full_window_measurements')
    unit = unit_from(item)
    receipt = {
        'kind': WINDOW_RECEIPT_KIND, 'success': True, 'unit': unit,
        'unit_identity': production_window_identity(unit),
        'parameters': {'latency_ns': delay},
        'artifacts': {'trades': trades, 'measurement': measurement},
    }
    return receipt, measured, outputs


class AuctionFlowCohortProductionTests(unittest.TestCase):
    def test_contract_collections_splits_and_prefix_rejection(self):
        contract = full_population_cohort_contract()
        validate_cohort_production_contract(contract)
        self.assertEqual(contract['kind'], CONTRACT_KIND)
        self.assertEqual(collection_from_source_path(MONTHLY_A), 'monthly')
        self.assertEqual(collection_from_source_path(DATED_A), 'dated')
        with self.assertRaises(ContractError):
            collection_from_source_path('quantpad/cme__nq-continuous-futures__mbp-1/weekly.bin')
        self.assertEqual(chronological_split('NQ', '2021-06-01'), 'train')
        self.assertEqual(chronological_split('NQ', '2023-06-01'), 'development')
        self.assertEqual(chronological_split('ES', '2021-06-01'), 'outside_declared_partitions')
        self.assertEqual(training_bounds('NQ')['event_period_cut_ns'], DEV_START)
        self.assertEqual(training_bounds('ES')['event_period_cut_ns'], date_end_exclusive_ns('2020-12-31'))
        self.assertEqual(BATCH_ROWS, 65536)
        broken = dict(contract)
        broken['kind'] = PREFIX_CONTRACT_KIND
        broken['maximum_training_prefix_prints'] = 4096
        with self.assertRaises(ContractError):
            validate_cohort_production_contract(broken)

    def test_full_training_thresholds_cuts_paths_and_cases(self):
        early = [
            row(DAY1 + 1, source_order=0, size=1, side=1),
            row(DAY1 + 2, source_order=1, size=2, side=-1),
        ]
        late = [row(LAST_TRAIN + 3 * MINUTE - 2, source_order=10, size=3, side=1)]
        eval_start = DEV_START - MINUTE
        available = DEV_START + DELAY
        eval_rows = [
            row(DEV_START + DELAY + 1, source_order=20, size=10, side=1),
            row(DEV_START + DELAY + 2, source_order=21, size=25, side=-1),
            row(DEV_START + DELAY + 3, source_order=22, size=5, side=1),
            row(DEV_START + DELAY + 4, source_order=23, size=7, side=0),
            row(DEV_START + DELAY + 4, source_order=24, size=4, side=1),
            row(DEV_START + MINUTE + 8, source_order=25, size=10_000, side=1),
        ]
        first = member('NQ', MONTHLY_A, DAY1, DAY1 + 3 * MINUTE, '2020-01-01')
        second = member('NQ', MONTHLY_B, LAST_TRAIN, DEV_START, '2022-12-31')
        evaluation = member('NQ', MONTHLY_EVAL, eval_start, DEV_START + 2 * MINUTE, '2023-01-01')
        eval_atoms = (
            (eval_start, DEV_START, True, True),
            (DEV_START, DEV_START + MINUTE, True, True),
            (DEV_START + MINUTE, DEV_START + 2 * MINUTE, True, True),
        )
        contract = full_population_cohort_contract()
        with TemporaryDirectory() as folder:
            receipt_a, _, _ = write_receipt(folder, 'monthly-a', first, early)
            receipt_b, _, _ = write_receipt(folder, 'monthly-b', second, late)
            receipt_e, measured, _ = write_receipt(
                folder, 'monthly-eval', evaluation, eval_rows, atoms=eval_atoms)
            acc = TrainingCollectionAccumulator(
                root='NQ', collection='monthly', expected_members=(first, second), contract=contract)
            acc.add_receipt(receipt_a)
            self.assertEqual(len(acc.remaining_members()), 1)
            acc.add_receipt(receipt_b)
            histogram = acc.complete()
            self.assertEqual(histogram['version'], VERSION)
            self.assertFalse(histogram['full_temporal_market_history_complete'])
            self.assertEqual(histogram['prints'], 3)
            self.assertEqual(histogram['contracts'], 6)
            self.assertEqual(histogram['histogram_report']['histogram'], ((1, 1), (2, 1), (3, 1)))
            self.assertEqual(histogram['coverage']['acquired_projection_complete'], True)
            prefix = accumulate_training_collection(
                root='NQ', collection='monthly', expected_members=(first,), receipts=(receipt_a,),
                contract=contract)
            prefix_fit = fit_training_collection(prefix, contract=contract)
            full_fit = fit_training_collection(histogram, contract=contract)
            self.assertEqual(prefix_fit['fits']['count_quartiles']['recipe']['requested_thresholds'], (2, 2, 3))
            self.assertEqual(full_fit['fits']['count_quartiles']['recipe']['requested_thresholds'], (2, 3, 4))
            self.assertEqual(full_fit['fits']['volume_quartiles']['recipe']['requested_thresholds'], (3, 3, 4))
            self.assertEqual(full_fit['fits']['source_top35_count_quantile']['recipe']['requested_thresholds'], (3,))
            self.assertEqual(sum(full_fit['fits']['count_quartiles']['realized_count']), 3)
            self.assertEqual(sum(full_fit['fits']['volume_quartiles']['realized_volume']), 6)
            self.assertEqual(full_fit['available_at'], available)
            self.assertEqual(full_fit['event_period_cut_ns'], DEV_START)
            self.assertGreater(full_fit['knowledge_cut_ns'], full_fit['event_period_cut_ns'])
            self.assertNotEqual(prefix_fit['fits']['count_quartiles']['recipe']['requested_thresholds'],
                                full_fit['fits']['count_quartiles']['recipe']['requested_thresholds'])
            outputs = BoundedOutputs(Path(folder) / 'persist', maximum_total_bytes=8 * 1024 ** 2,
                                     maximum_file_bytes=4 * 1024 ** 2)
            hist_ref = persist_training_histogram(outputs, histogram)
            fit_ref = persist_training_fits(outputs, full_fit)
            restored_hist = restore_training_histogram(hist_ref)
            restored_fit = restore_training_fits(fit_ref)
            self.assertEqual(restored_hist['histogram_identity'], histogram['histogram_identity'])
            self.assertEqual(restored_fit['fits']['count_quartiles']['recipe']['requested_thresholds'], (2, 3, 4))
            self.assertEqual(select_training_fits(restored_fit, root='NQ', collection='monthly')['available_at'],
                             available)
            out = BoundedOutputs(Path(folder) / 'eval', maximum_total_bytes=16 * 1024 ** 2,
                                 maximum_file_bytes=8 * 1024 ** 2)
            summary = measure_source_window_cohorts(
                receipt_e, training=restored_fit, contract=contract, outputs=out,
                expected_member=evaluation)
            self.assertTrue(summary['passed'])
            self.assertEqual(summary['definitions'], 8)
            artifact = exact(read_json_artifact(summary['reference']))
            names = [item['name'] for item in artifact['instruments'][0]['definitions']]
            self.assertEqual(names, [*FIXED_FILTERS, 'soft_benchmark_knots',
                                     *(name for name, _, _ in ADAPTIVE_RECIPES)])
            soft = next(item for item in artifact['instruments'][0]['definitions']
                        if item['name'] == 'soft_benchmark_knots')
            self.assertEqual(len(soft['whole']['channels']), len(SOFT_KNOTS))
            all_flow = next(item for item in artifact['instruments'][0]['definitions'] if item['name'] == 'all')
            channel = all_flow['whole']['channels'][0]
            original = measured['instruments'][0]['whole_window']['flows']['all']
            self.assertEqual(channel['open'], 0)
            self.assertEqual(channel['high'], 9994)
            self.assertEqual(channel['low'], -15)
            self.assertEqual(channel['close'], 9994)
            self.assertNotEqual(channel['low'], channel['close'])
            self.assertEqual(channel['unknown'], 7)
            self.assertEqual(channel['observed_signed_lower'], 9987)
            self.assertEqual(channel['observed_signed_upper'], 10001)
            self.assertEqual(all_flow['whole']['prints'], 6)
            self.assertEqual(channel['high'], original['high'])
            self.assertEqual(channel['low'], original['low'])
            self.assertEqual(channel['close'], original['close'])
            atoms = decode_atoms(all_flow['atomic'])
            self.assertEqual([bar['bin'] for bar in atoms], [0, 1, 2])
            self.assertTrue(atoms[0]['empty_observed_window'])
            self.assertEqual(atoms[1]['prints'], 5)
            self.assertEqual(atoms[2]['prints'], 1)
            self.assertEqual(atoms[1]['channels'][0]['high'], 10)
            self.assertEqual(atoms[1]['channels'][0]['low'], -15)
            self.assertEqual(atoms[1]['channels'][0]['close'], -6)
            self.assertNotEqual(atoms[1]['channels'][0]['high'], atoms[1]['channels'][0]['close'])
            adaptive = next(item for item in artifact['instruments'][0]['definitions']
                            if item['name'] == 'count_quartiles')
            self.assertEqual(adaptive['supported_start_ns'], available)
            self.assertEqual(adaptive['atomic_unavailable'][0]['disposition'],
                             'unavailable_before_training_availability')
            self.assertEqual(adaptive['atomic_unavailable'][0]['bin'], 0)
            adaptive_atoms = decode_atoms(adaptive['atomic'])
            self.assertEqual([bar['bin'] for bar in adaptive_atoms], [1, 2])
            self.assertTrue(adaptive_atoms[0]['clipped'])
            self.assertEqual(adaptive_atoms[0]['supported_start_ns'], available)
            self.assertEqual(adaptive['whole']['prints'], 6)
            self.assertEqual(adaptive['whole']['event_start_ns'], available)
            counts = summary['workload_counts']
            self.assertEqual(counts['prepared_prints'], 6)
            self.assertGreater(counts['rowset_rows'], 0)
            whole_rows = [item for item in summary['rowset']
                          if item['interval_kind'] == 'whole_window' and item['definition'] == 'all']
            self.assertTrue(any(item['independent_date_unit'] for item in whole_rows))
            self.assertTrue(all(not item['independent_date_unit']
                                for item in summary['rowset'] if item['interval_kind'] == 'atomic_minute'))
            self.assertEqual(artifact['date_aggregation']['minute_rows_are_not_independent_dates'], True)
            self.assertGreater(summary['exact_original_source_fields_compared'], 0)

    def test_monthly_and_dated_remain_distinct_and_dated_has_no_post_train_eval(self):
        early = [
            row(DAY1 + 1, source_order=0, size=1, side=1),
            row(DAY1 + 2, source_order=1, size=2, side=-1),
        ]
        late = [row(LAST_TRAIN + 10, source_order=10, size=3, side=1)]
        first = member('NQ', MONTHLY_A, DAY1, DAY1 + MINUTE, '2020-01-01')
        second = member('NQ', MONTHLY_B, LAST_TRAIN, LAST_TRAIN + MINUTE, '2022-12-31')
        dated = member('NQ', DATED_A, DAY1, DAY1 + MINUTE, '2020-01-01')
        dated_eval = member('NQ', DATED_EVAL, date_start_ns('2023-01-02'),
                            date_start_ns('2023-01-02') + MINUTE, '2023-01-02')
        contract = full_population_cohort_contract()
        with TemporaryDirectory() as folder:
            monthly_a, _, _ = write_receipt(folder, 'm-a', first, early)
            monthly_b, _, _ = write_receipt(folder, 'm-b', second, late)
            dated_a, _, _ = write_receipt(folder, 'd-a', dated, early)
            monthly = accumulate_training_collection(
                root='NQ', collection='monthly', expected_members=(first, second),
                receipts=(monthly_a, monthly_b), contract=contract)
            dated_hist = accumulate_training_collection(
                root='NQ', collection='dated', expected_members=(dated,),
                receipts=(dated_a,), contract=contract)
            self.assertEqual(monthly['histogram_report']['histogram'], ((1, 1), (2, 1), (3, 1)))
            self.assertEqual(dated_hist['histogram_report']['histogram'], ((1, 1), (2, 1)))
            self.assertNotEqual(monthly['histogram_identity'], dated_hist['histogram_identity'])
            monthly_fit = fit_training_collection(monthly, contract=contract)
            dated_fit = fit_training_collection(dated_hist, contract=contract, evaluation_members=())
            self.assertEqual(monthly_fit['fits']['count_quartiles']['recipe']['requested_thresholds'], (2, 3, 4))
            self.assertEqual(dated_fit['fits']['count_quartiles']['recipe']['requested_thresholds'], (2, 2, 3))
            self.assertIs(dated_fit['post_training_evaluation_population'], False)
            self.assertEqual(dated_fit['post_training_evaluation_disposition'],
                             'dated_collection_no_post_training_evaluation_population')
            dated_later, _, _ = write_receipt(folder, 'd-eval', dated_eval,
                                              [row(date_start_ns('2023-01-02') + 1, source_order=0, size=9)])
            out = BoundedOutputs(Path(folder) / 'cross', maximum_total_bytes=8 * 1024 ** 2,
                                 maximum_file_bytes=4 * 1024 ** 2)
            with self.assertRaises(IntegrityError):
                measure_source_window_cohorts(
                    dated_later, training=monthly_fit, contract=contract, outputs=out,
                    expected_member=dated_eval)
            out2 = BoundedOutputs(Path(folder) / 'dated-eval', maximum_total_bytes=8 * 1024 ** 2,
                                  maximum_file_bytes=4 * 1024 ** 2)
            summary = measure_source_window_cohorts(
                dated_later, training=dated_fit, contract=contract, outputs=out2,
                expected_member=dated_eval)
            adaptive = next(item for item in exact(read_json_artifact(summary['reference']))['instruments'][0]['definitions']
                            if item['name'] == 'count_quartiles')
            self.assertEqual(adaptive['whole']['disposition'],
                             'dated_collection_no_post_training_evaluation_population')

    def test_missing_tampered_and_duplicate_expected_members_reject(self):
        early = [row(DAY1 + 1, source_order=0, size=1, side=1)]
        late = [row(DAY2 + 1, source_order=1, size=2, side=-1)]
        first = member('NQ', MONTHLY_A, DAY1, DAY1 + MINUTE, '2020-01-01')
        second = member('NQ', MONTHLY_A, DAY2, DAY2 + MINUTE, '2020-01-02')
        contract = full_population_cohort_contract()
        with TemporaryDirectory() as folder:
            receipt_a, _, _ = write_receipt(folder, 'a', first, early)
            receipt_b, _, _ = write_receipt(folder, 'b', second, late)
            with self.assertRaises(IntegrityError):
                accumulate_training_collection(
                    root='NQ', collection='monthly', expected_members=(first, second),
                    receipts=(receipt_a,), contract=contract)
            with self.assertRaises(IntegrityError):
                accumulate_training_collection(
                    root='NQ', collection='monthly', expected_members=(first, second),
                    receipts=(receipt_a, receipt_a), contract=contract)
            with self.assertRaises(ContractError):
                accumulate_training_collection(
                    root='NQ', collection='monthly', expected_members=(first, first),
                    receipts=(receipt_a, receipt_b), contract=contract)
            tampered = dict(receipt_b)
            tampered['artifacts'] = dict(receipt_b['artifacts'])
            broken = dict(receipt_b['artifacts']['measurement'])
            broken['sha256'] = '0' * 64
            tampered['artifacts']['measurement'] = broken
            with self.assertRaises(IntegrityError):
                accumulate_training_collection(
                    root='NQ', collection='monthly', expected_members=(first, second),
                    receipts=(receipt_a, tampered), contract=contract)
            incomplete, _, _ = write_receipt(folder, 'incomplete', second, late, source_complete=False,
                                             coordinate_complete=False)
            with self.assertRaises(IntegrityError):
                accumulate_training_collection(
                    root='NQ', collection='monthly', expected_members=(first, second),
                    receipts=(receipt_a, incomplete), contract=contract)
            development = member('NQ', MONTHLY_A, DEV_START, DEV_START + MINUTE, '2023-01-01')
            post, _, _ = write_receipt(folder, 'post', development, late)
            with self.assertRaises(ContractError):
                accumulate_training_collection(
                    root='NQ', collection='monthly', expected_members=(development,),
                    receipts=(post,), contract=contract)
