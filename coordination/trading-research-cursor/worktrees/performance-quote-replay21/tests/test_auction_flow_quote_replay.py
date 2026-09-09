from pathlib import Path
import copy
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

from trading_research.data.reconcile import footer_index
from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_arrow import value_digest
from trading_research.research.auction_flow_data import AuctionFlowStream
from trading_research.research.auction_flow_quote_replay import (
    ENCODING, QuoteReplaySeries, _verify_quote_replay_descriptor)
from trading_research.research.auction_flow_resources import source_cost_projection
from trading_research.research.auction_flow_storage import (
    BoundedOutputs, ParquetSeries, read_json_artifact, read_series_tables)
from tests.test_auction_flow_data import AuctionFlowDataTests, DATASET, raw


def produce(root, index, start, end, continuation=None, source_paths=None):
    kwargs = {}
    if continuation is not None:
        kwargs['continuation'] = continuation
    if source_paths is not None:
        kwargs['source_paths'] = source_paths
    stream = AuctionFlowStream(
        data_root=root, index=index, dataset=DATASET, start_ns=start, end_ns=end,
        maximum_scan_rows=100, latency_ns=250, batch_rows=65536, **kwargs)
    quotes = []
    for batch in stream:
        quotes.extend(batch.quotes)
    return quotes, stream.manifest(), stream.carry()


def parquet_expected(outputs, name, quotes):
    series = ParquetSeries(outputs, name, encoding='plain')
    for table in quotes:
        series.append(table)
    return series.finish()


def concat(tables):
    return None if not tables else pa.concat_tables(tables).combine_chunks()


class AuctionFlowQuoteReplayTests(unittest.TestCase):
    def test_replay_preserves_instrument_order_split_ties_against_physical_parquet(self):
        rows = [raw(2, instrument=2), raw(2, instrument=1), raw(3, instrument=2),
                raw(3, instrument=1), raw(5, instrument=2, action='T', flags=0), raw(6, instrument=1)]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = AuctionFlowDataTests().write(root, rows)
            path = index['datasets'][DATASET][0]['path']
            quotes, manifest, _ = produce(root, index, 2, 10, source_paths=(path,))
            order = [t['instrument_id'][0].as_py() for t in quotes]
            self.assertGreaterEqual(len(quotes), 2)
            self.assertEqual(order[0], 2)
            self.assertIn(1, order)
            self.assertNotEqual(order, sorted(order))
            outputs = BoundedOutputs(root / 'out', maximum_total_bytes=4 * 1024**2, maximum_file_bytes=2 * 1024**2)
            index_ref = outputs.json('source-index.json', index, kind='four_dataset_full_footer_index')
            expected = parquet_expected(outputs, 'expected-quotes', quotes)
            expected_tables = list(read_series_tables(expected))
            series = QuoteReplaySeries(
                outputs, 'quotes', data_root=root, source_index_reference=index_ref, root='NQ',
                start_ns=2, end_ns=10, source_paths=(path,), maximum_scan_rows=100, latency_ns=250)
            encoded = quotes[0].set_column(
                quotes[0].schema.get_field_index('source_key'), 'source_key',
                quotes[0]['source_key'].dictionary_encode())
            series.append(encoded)
            for table in quotes[1:]:
                series.append(table)
            published = series.finish(manifest)
            self.assertTrue(published['roundtrip_exact'])
            self.assertEqual(published['encoding'], ENCODING)
            self.assertEqual(published['files'], [])
            self.assertEqual(published['serialized_bytes'], published['replay_descriptor']['size_bytes'])
            self.assertGreater(published['serialized_bytes'], 0)
            self.assertEqual(published['rows'], expected['rows'])
            self.assertGreaterEqual(published['quote_replay_validation_cpu_seconds'], 0)
            self.assertEqual(type(published['quote_replay_validation_cpu_seconds']), float)
            restored = list(read_series_tables(published))
            self.assertEqual([t['instrument_id'][0].as_py() for t in restored], order)
            self.assertTrue(concat(restored).schema.equals(concat(expected_tables).schema, check_metadata=True))
            self.assertEqual(value_digest(concat(restored)), value_digest(concat(quotes)))
            self.assertEqual(value_digest(concat(restored)), value_digest(concat(expected_tables)))
            descriptor = read_json_artifact(published['replay_descriptor'])
            self.assertNotIn('roundtrip_exact', descriptor)
            self.assertEqual(_verify_quote_replay_descriptor(descriptor), published['compared_values'])

    def test_empty_quiet_interval_still_verifies_the_raw_stream(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = AuctionFlowDataTests().write(root, [raw(t) for t in (0, 1, 2, 80, 81, 82)])
            path = index['datasets'][DATASET][0]['path']
            first_quotes, _, carry = produce(root, index, 0, 10, source_paths=(path,))
            empty_quotes, empty_manifest, _ = produce(
                root, index, 10, 60, continuation=carry, source_paths=(path,))
            self.assertEqual(empty_quotes, [])
            self.assertEqual(empty_manifest['physical_scan_rows'], 0)
            outputs = BoundedOutputs(root / 'out', maximum_total_bytes=4 * 1024**2, maximum_file_bytes=2 * 1024**2)
            index_ref = outputs.json('source-index.json', index, kind='four_dataset_full_footer_index')
            expected = parquet_expected(outputs, 'expected-empty', empty_quotes)
            series = QuoteReplaySeries(
                outputs, 'empty-quotes', data_root=root, source_index_reference=index_ref, root='NQ',
                start_ns=10, end_ns=60, source_paths=(path,), maximum_scan_rows=100, latency_ns=250,
                continuation=carry)
            published = series.finish(empty_manifest)
            self.assertEqual(published['rows'], 0)
            self.assertIsNone(published['schema'])
            self.assertEqual(list(read_series_tables(published)), [])
            self.assertEqual(expected['rows'], 0)
            self.assertEqual(first_quotes[0]['instrument_id'][0].as_py(), 1)

    def test_source_continuation_after_invalidation_matches_physical_quotes(self):
        rows = [raw(0), raw(2, action='T', flags=0), raw(4, flags=132), raw(9),
                raw(20), raw(20, action='T', flags=0), raw(25, action='T', flags=0, side='A'), raw(29)]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = AuctionFlowDataTests().write(root, rows)
            path = index['datasets'][DATASET][0]['path']
            first_quotes, first_manifest, carry = produce(root, index, 0, 20, source_paths=(path,))
            second_quotes, second_manifest, _ = produce(
                root, index, 20, 30, continuation=carry, source_paths=(path,))
            outputs = BoundedOutputs(root / 'out', maximum_total_bytes=4 * 1024**2, maximum_file_bytes=2 * 1024**2)
            index_ref = outputs.json('source-index.json', index, kind='four_dataset_full_footer_index')
            expected = parquet_expected(outputs, 'expected-continued', second_quotes)
            series = QuoteReplaySeries(
                outputs, 'continued-quotes', data_root=root, source_index_reference=index_ref, root='NQ',
                start_ns=20, end_ns=30, source_paths=(path,), maximum_scan_rows=100, latency_ns=250,
                continuation=carry)
            for table in second_quotes:
                series.append(table)
            published = series.finish(second_manifest)
            restored = concat(list(read_series_tables(published)))
            self.assertEqual(value_digest(restored), value_digest(concat(second_quotes)))
            self.assertEqual(value_digest(restored), value_digest(concat(list(read_series_tables(expected)))))
            wrong = QuoteReplaySeries(
                outputs, 'wrong-carry', data_root=root, source_index_reference=index_ref, root='NQ',
                start_ns=20, end_ns=30, source_paths=(path,), maximum_scan_rows=100, latency_ns=250)
            for table in second_quotes:
                wrong.append(table)
            with self.assertRaises(IntegrityError):
                wrong.finish(second_manifest)
            self.assertTrue(wrong.failed)
            with self.assertRaises((ContractError, IntegrityError)):
                QuoteReplaySeries(
                    outputs, 'terminal', data_root=root, source_index_reference=index_ref, root='NQ',
                    start_ns=0, end_ns=20, source_paths=(path,), maximum_scan_rows=100, latency_ns=250,
                    continuation=carry)
            with self.assertRaises(ContractError):
                QuoteReplaySeries(
                    outputs, 'measurement', data_root=root, source_index_reference=index_ref, root='NQ',
                    start_ns=0, end_ns=20, source_paths=(path,), maximum_scan_rows=100, latency_ns=250,
                    continuation={'version': 'auction-flow-measurement-continuation-v1',
                                  'completed': True, 'next_start_ns': 0, 'instruments': {}, 'sha256': 'x'})
            self.assertTrue(first_manifest['source_continuation']['blocked'])

    def test_tamper_and_raw_trade_size_fail_before_publication_or_at_exhausted_read(self):
        rows = [raw(2), raw(3, action='T', flags=0, size=5), raw(5), raw(6, action='T', flags=0, size=8), raw(8)]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = AuctionFlowDataTests().write(root, rows)
            path = index['datasets'][DATASET][0]['path']
            quotes, manifest, _ = produce(root, index, 2, 10, source_paths=(path,))
            outputs = BoundedOutputs(root / 'out', maximum_total_bytes=4 * 1024**2, maximum_file_bytes=2 * 1024**2)
            index_ref = outputs.json('source-index.json', index, kind='four_dataset_full_footer_index')
            series = QuoteReplaySeries(
                outputs, 'quotes', data_root=root, source_index_reference=index_ref, root='NQ',
                start_ns=2, end_ns=10, source_paths=(path,), maximum_scan_rows=100, latency_ns=250)
            for table in quotes:
                series.append(table)
            published = series.finish(manifest)
            descriptor = read_json_artifact(published['replay_descriptor'])

            def reject(mutator):
                changed = copy.deepcopy(descriptor)
                mutator(changed)
                reference = outputs.json(f'tampered-{id(mutator)}.json', changed,
                                         kind='auction_flow_quote_replay_descriptor')
                series_copy = {**published, 'replay_descriptor': reference}
                with self.assertRaises(IntegrityError):
                    list(read_series_tables(series_copy))

            reject(lambda d: d.update(start_ns=d['start_ns'] + 1))
            reject(lambda d: d['chunks'].__setitem__(0, {**d['chunks'][0], 'rows': d['chunks'][0]['rows'] + 1})
                   if d['chunks'] else d.update(rows=3))
            reject(lambda d: d['chunks'].__setitem__(0, {**d['chunks'][0], 'sha256': '0' * 64})
                   if d['chunks'] else d.update(source_identity_sha256='0' * 64))
            reject(lambda d: d['logical_schema'].__setitem__('text', 'tampered-schema')
                   if d['logical_schema'] else d.update(logical_schema={'ipc_hex': '00', 'text': 'x'}))
            reject(lambda d: d['implementation']['files']['data/compact.py'].__setitem__('sha256', '0' * 64))
            reject(lambda d: d.update(initial_continuation={
                'version': 'auction-flow-source-continuation-v1', 'completed': True,
                'next_start_ns': 2, 'sha256': '0' * 64}))
            reject(lambda d: d['source_identity'].__setitem__(
                'source_all_field_arrow_stream_sha256', '0' * 64))
            reject(lambda d: d.update(source_identity_sha256='0' * 64))
            bad_index = copy.deepcopy(index)
            bad_index['datasets'][DATASET][0] = {**bad_index['datasets'][DATASET][0], 'schema': 'tampered'}
            bad_index_ref = outputs.json('tampered-index.json', bad_index, kind='four_dataset_full_footer_index')
            reject(lambda d: d.update(source_index_reference=bad_index_ref))

            parquet_path = root / DATASET / 'fixture.parquet'
            table = pq.read_table(parquet_path)
            sizes = table['size'].to_pylist()
            actions = table['action'].to_pylist()
            trade = next(i for i, action in enumerate(actions) if action == 'T')
            sizes[trade] = sizes[trade] + 17
            pq.write_table(table.set_column(table.schema.get_field_index('size'), 'size',
                                            pa.array(sizes, type=pa.int64())), parquet_path, row_group_size=3)
            rewritten = footer_index(root, datasets=(DATASET,), max_files=1)
            raw_index_ref = outputs.json('rewritten-index.json', rewritten, kind='four_dataset_full_footer_index')
            raw_desc = copy.deepcopy(descriptor)
            raw_desc['source_index_reference'] = raw_index_ref
            raw_ref = outputs.json('rewritten-descriptor.json', raw_desc, kind='auction_flow_quote_replay_descriptor')
            yielded = []
            with self.assertRaises(IntegrityError):
                for item in read_series_tables({**published, 'replay_descriptor': raw_ref}):
                    yielded.append(item)
            failing = QuoteReplaySeries(
                outputs, 'bad-manifest', data_root=root, source_index_reference=index_ref, root='NQ',
                start_ns=2, end_ns=10, source_paths=(path,), maximum_scan_rows=100, latency_ns=250)
            for table in quotes:
                failing.append(table)
            mutated = copy.deepcopy(manifest)
            mutated['source_all_field_arrow_stream_sha256'] = '0' * 64
            before = outputs.written
            with self.assertRaises(IntegrityError):
                failing.finish(mutated)
            self.assertTrue(failing.failed)
            self.assertTrue(outputs.failed)
            self.assertGreater(outputs.written, before)
            with self.assertRaises(IntegrityError):
                failing.finish(manifest)
            unpublished = {**published, 'roundtrip_exact': False}
            with self.assertRaises(IntegrityError):
                list(read_series_tables(unpublished))
            with self.assertRaises(IntegrityError):
                series.finish(manifest)

    def test_output_bounds_and_failure_state_charge_the_descriptor(self):
        rows = [raw(2), raw(4), raw(6)]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = AuctionFlowDataTests().write(root, rows)
            path = index['datasets'][DATASET][0]['path']
            quotes, manifest, _ = produce(root, index, 2, 10, source_paths=(path,))
            large = BoundedOutputs(root / 'idx', maximum_total_bytes=2 * 1024**2, maximum_file_bytes=1024**2)
            index_ref = large.json('source-index.json', index, kind='four_dataset_full_footer_index')
            tiny = BoundedOutputs(root / 'tiny', maximum_total_bytes=80, maximum_file_bytes=40)
            bounded = QuoteReplaySeries(
                tiny, 'quotes', data_root=root, source_index_reference=index_ref, root='NQ',
                start_ns=2, end_ns=10, source_paths=(path,), maximum_scan_rows=100, latency_ns=250)
            for table in quotes:
                bounded.append(table)
            with self.assertRaises((ContractError, IntegrityError)):
                bounded.finish(manifest)
            self.assertTrue(bounded.failed)
            self.assertTrue(tiny.failed)
            aborted = QuoteReplaySeries(
                large, 'aborted', data_root=root, source_index_reference=index_ref, root='NQ',
                start_ns=2, end_ns=10, source_paths=(path,), maximum_scan_rows=100, latency_ns=250)
            aborted.abort()
            self.assertTrue(aborted.failed)
            with self.assertRaises(IntegrityError):
                aborted.finish(manifest)

    def test_resource_projection_keeps_physical_rates_and_forecasts_replay_by_window(self):
        def unit(*, quote_encoding='structural', quote_bytes=8000, quote_rows=40, replay_cpu=0.0,
                 parquet_cpu=0.5, reader_batches=4, sources=1, raw_rows=80, finalization=0.2,
                 decode_cpu=0.04, instrument_batches=4):
            source_cpu = {'source_metadata_and_open': 0.01, 'physical_batch_decode': decode_cpu,
                          'physical_address_and_selection': 0.02 if reader_batches else 0.0,
                          'selected_projection': 0.03 if instrument_batches else 0.0}
            scan = {'source_decode_and_projection': 0.12, 'native_source_ownership': 0.01 if reader_batches else 0.0,
                    'time_at_price_consumers': 0.02 if instrument_batches else 0.0,
                    'whole_trade_and_native_consumers': 0.02 if instrument_batches else 0.0,
                    'event_storage': 0.03 if instrument_batches else 0.0,
                    'raw_atomic_batch_reduction': 0.02 if instrument_batches else 0.0,
                    'raw_atomic_counter_updates': 0.01, 'trade_atomic_consumers': 0.01,
                    'quote_atomic_consumers': 0.01, 'unassigned_scan_routing': 0.01,
                    'reference_sample_collection': 0.0}
            quotes = {'encoding': quote_encoding, 'rows': quote_rows, 'serialized_bytes': quote_bytes,
                      'cpu_seconds': 0.05}
            if quote_encoding == ENCODING:
                quotes['quote_replay_validation_cpu_seconds'] = replay_cpu
            return {
                'unit': {'source_path': f'{DATASET}/fixture.parquet', 'event_start_ns': 0, 'event_end_ns': 10},
                'source_manifest': {'sources': [{}] * sources, 'source_cpu_components': source_cpu,
                                    'physical_reader_batches': reader_batches},
                'scan_cpu_components_disjoint': scan,
                'workload_counts': {'raw_instrument_batches': instrument_batches, 'raw_batches': reader_batches,
                                    'raw_atomic_parts': 2, 'trade_atomic_parts': 2, 'quote_atomic_parts': 2,
                                    'instrument_atomic_cells': 4},
                'pipeline_cpu_components': {'initialization': 0.01, 'instrument_allocation': 0.01,
                                            'scan_and_consumers': 0.30, 'finalization_and_native_storage': 0.05},
                'native_reference_sample_collection_cpu_seconds': 0.01,
                'event_storage_finalization_cpu_seconds': finalization,
                'measurement_json_serialization_cpu_seconds': 0.02,
                'instrument_quality': [{'instrument_id': 1}], 'native_cells': 8,
                'event_storage': {
                    'quotes': quotes,
                    'trades': {'encoding': 'structural', 'rows': 10, 'serialized_bytes': 1000, 'cpu_seconds': 0.05},
                    'excluded': {'encoding': 'structural', 'rows': 2, 'serialized_bytes': 200, 'cpu_seconds': 0.02}},
                'native_storage': [{'serialized_bytes': 400, 'rows': 8}],
                'parquet_and_roundtrip_cpu_seconds': parquet_cpu,
                'quote_replay_validation_cpu_seconds': replay_cpu,
                'counts': {'raw_rows': raw_rows}, 'measurement': {'size_bytes': 500},
                'raw_physical_rows': raw_rows,
                'plain_json_storage_comparator': {'cpu_seconds': 0.01}, 'reference_cpu_seconds': 0.01,
                'peak_process_rss_bytes': 50_000_000, 'native_array_bytes': 10_000_000}

        schedule = {'instrument_allocation_bound_established': True,
            'windows': [{'native_cells_per_instrument': 8, 'raw_instruments_per_window_upper': 1}],
            'partitions': [{'root': 'NQ', 'year': 2020, 'source_windows': 2, 'reader_batches_upper': 8,
                'instrument_batches_upper': 8, 'atomic_parts_per_consumer_upper': 8,
                'instrument_native_cells_upper': 16, 'instrument_window_allocations_upper': 2,
                'instrument_atomic_cells_upper': 8, 'selected_raw_rows_upper': 1000}]}
        protocol = {'resources': {'maximum_derived_output_bytes': 1024**2}}
        physical = source_cost_projection([unit()], protocol, schedule, excluded_storage_reserve_bytes_per_source_year=1024)
        self.assertNotIn('quote_replay_validation', physical['cpu_coefficients'])
        self.assertEqual(physical['event_output_rates']['quotes']['bytes_per_actual_event_max'], 200.0)
        self.assertEqual(physical['partitions'][0]['event_cache_bytes_by_kind']['quotes'], 1000 * 0.5 * 200.0)
        self.assertEqual(
            physical['failure_output_cpu_reserve_basis'],
            'maximum observed exact Parquet write/read/hash CPU per serialized byte; separate fixed failure-output allowance')
        physical_bytes = 8000 + 1000 + 200 + 400
        self.assertEqual(
            physical['partitions'][0]['disjoint_source_cpu_components']['failure_output_reserve'],
            1024 * (0.5 / physical_bytes))

        replay = source_cost_projection(
            [unit(quote_encoding=ENCODING, quote_bytes=2500, replay_cpu=2.0, parquet_cpu=0.4)],
            protocol, schedule, excluded_storage_reserve_bytes_per_source_year=1024)
        self.assertEqual(replay['cpu_coefficients']['quote_replay_validation']['cpu_seconds_per_work_unit'], 0.5)
        self.assertEqual(replay['partitions'][0]['disjoint_source_cpu_components']['quote_replay_validation'], 4.0)
        self.assertEqual(replay['event_output_rates']['quotes']['bytes_per_actual_event_max'], None)
        self.assertEqual(replay['event_output_rates']['quotes']['quote_parquet_bytes'], 0)
        self.assertEqual(replay['partitions'][0]['event_cache_bytes_by_kind']['quotes'], 5000)
        self.assertNotEqual(replay['partitions'][0]['event_cache_bytes_by_kind']['quotes'], 1000 * 0.5 * (2500 / 40))
        self.assertEqual(replay['quote_replay_descriptor_bytes_per_source_window_max'], 2500)
        self.assertFalse(replay['quote_parquet_bytes_in_projection'])
        physical_only = 1000 + 200 + 400
        self.assertEqual(
            replay['partitions'][0]['disjoint_source_cpu_components']['failure_output_reserve'],
            1024 * (0.4 / physical_only))

        mixed = [unit(), unit(quote_encoding=ENCODING, quote_bytes=2500, replay_cpu=2.0, parquet_cpu=0.4)]
        with self.assertRaises(IntegrityError):
            source_cost_projection(mixed, protocol, schedule, excluded_storage_reserve_bytes_per_source_year=1024)

        empty = source_cost_projection(
            [unit(quote_encoding=ENCODING, quote_bytes=1800, replay_cpu=0.25, parquet_cpu=0.2,
                  reader_batches=0, decode_cpu=0.0, instrument_batches=0, sources=1, finalization=0.05)],
            protocol, schedule, excluded_storage_reserve_bytes_per_source_year=1024)
        self.assertEqual(empty['cpu_coefficients']['quote_replay_validation']['cpu_seconds_per_work_unit'], 0.0)
        self.assertEqual(empty['cpu_coefficients']['quote_replay_empty_window']['cpu_seconds_per_work_unit'], 0.25)
        self.assertEqual(empty['partitions'][0]['disjoint_source_cpu_components']['quote_replay_empty_window'], 0.5)

        zero = unit(quote_encoding=ENCODING, quote_bytes=1800, replay_cpu=0.25, parquet_cpu=0.2,
                    reader_batches=0, decode_cpu=0.0, instrument_batches=0, sources=0, finalization=0.05)
        with self.assertRaises(IntegrityError):
            source_cost_projection([zero], protocol, schedule, excluded_storage_reserve_bytes_per_source_year=1024)


if __name__ == '__main__':
    unittest.main()
