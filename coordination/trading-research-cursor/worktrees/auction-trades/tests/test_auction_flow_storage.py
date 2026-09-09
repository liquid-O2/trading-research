from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries, read_json_artifact
from trading_research.research.auction_flow_arrow import value_digest


class AuctionFlowStorageTests(unittest.TestCase):
    def test_structural_native_storage_restores_every_wide_clock_sentinel_float_bit_and_schema(self):
        from trading_research.research.auction_flow_storage import read_series_tables, PHYSICAL_ENCODING_KEY
        from trading_research.research.auction_flow_parity import compare_series
        count = 70003
        start = 2**60 + 1 + 100 * np.arange(count, dtype=np.int64)
        mask = np.arange(count) % 11 == 0
        bits = np.resize(np.array([0, 0x8000000000000000, 0x7ff8000000000001, 0x7ff8000000000002], dtype=np.uint64), count)
        values = pa.table({'event_start_ns': start, 'event_end_ns': start + 100,
            'known_at_ns': start + 357, 'all__high_at_ns': np.where(mask, start + 7, -1),
            'all__high_source_order': np.where(mask, 2**50 + np.arange(count), -1),
            'nullable_at_ns': pa.array([None, -1, 2**60 + 3] * 23334 + [None], type=pa.int64()),
            'raw_float': bits.view(np.float64), 'instrument_id': np.ones(count, dtype=np.int64)})
        values = values.replace_schema_metadata({b'original-clock-domain': b'exact\x00bytes'})
        with tempfile.TemporaryDirectory() as folder:
            out = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=8 * 1024**2, maximum_file_bytes=4 * 1024**2)
            original = ParquetSeries(out, 'native-original', encoding='plain')
            original.append(values)
            old = original.finish()
            candidate = ParquetSeries(out, 'native-structural', encoding='structural', maximum_rows_per_file=65536)
            candidate.append(values.slice(0, 19))
            candidate.append(values.slice(19))
            new = candidate.finish()
            restored = pa.concat_tables(list(read_series_tables(new))).combine_chunks()
            self.assertEqual(restored.schema, values.schema)
            self.assertTrue(restored.schema.equals(values.schema, check_metadata=True))
            for start in range(0, count, 65536):
                self.assertEqual(value_digest(restored.slice(start, 65536)), value_digest(values.slice(start, 65536)))
            self.assertEqual(restored['raw_float'].to_numpy().view(np.uint64).tolist(), bits.tolist())
            self.assertTrue(compare_series([old], [new])['passed'])
            physical = pq.read_table(new['files'][0]['path'])
            self.assertIn(PHYSICAL_ENCODING_KEY, physical.schema.metadata)
            self.assertGreater(physical['all__high_at_ns'].null_count, 0)
            self.assertEqual(physical['event_end_ns'][0].as_py(), 100)
            self.assertEqual(physical['known_at_ns'][0].as_py(), 257)

    def test_structural_event_addresses_keep_exact_differences_and_refuse_changed_inverse(self):
        import copy
        from trading_research.research.auction_flow_storage import read_series_tables
        from trading_research.research.auction_flow_structural_encoding import encode_table, decode_table
        table = pa.table({'t': [2**60 + 1, 2**60 + 1, 2**60 + 3],
            'known_at_ns': [2**60 + 258, 2**60 + 258, 2**60 + 260],
            'source_row': [7000, 7001, 7020], 'source_order': [15, 16, 35], 'size': [5, 5, 6]})
        with tempfile.TemporaryDirectory() as folder:
            out = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=1024**2, maximum_file_bytes=1024**2)
            series = ParquetSeries(out, 'events', encoding='structural')
            series.append(table)
            reference = series.finish()
            restored = pa.concat_tables(list(read_series_tables(reference)))
            self.assertEqual(value_digest(restored), value_digest(table))
            physical = pq.read_table(reference['files'][0]['path'])
            self.assertEqual(physical['source_order'].to_pylist(), [-6985, -6985, -6985])
            changed = copy.deepcopy(reference)
            changed['files'][0]['row_group_values'][0]['codec']['operations'][0]['reference'] = 'source_row'
            with self.assertRaises(IntegrityError):
                list(read_series_tables(changed))
            changed = copy.deepcopy(reference)
            changed['files'][0].pop('physical_encoding')
            with self.assertRaises(IntegrityError):
                list(read_series_tables(changed))
        extremes = pa.table({'t': [-(2**63) + 1], 'known_at_ns': [2**63 - 1],
                            'source_row': [0], 'source_order': [2**63 - 1]})
        encoded, descriptor = encode_table(extremes)
        self.assertNotIn('known_at_ns', [v['column'] for v in descriptor['operations']])
        self.assertEqual(value_digest(decode_table(encoded, descriptor)), value_digest(extremes))
        strict = pa.table({'event_start_ns': [2**60], 'event_end_ns': [2**60 + 100], 'high_at_ns': [-1]},
            schema=pa.schema([pa.field(n, pa.int64(), nullable=False) for n in ('event_start_ns', 'event_end_ns', 'high_at_ns')]))
        encoded, descriptor = encode_table(strict)
        self.assertEqual(encoded['high_at_ns'].null_count, 0)
        self.assertEqual(value_digest(decode_table(encoded, descriptor)), value_digest(strict))

    def test_fast_exact_measurement_json_matches_full_canonical_bytes_and_rejects_key_coercion(self):
        from trading_research.operations.artifacts import canonical_json
        from trading_research.research.auction_flow_structural_encoding import exact_measurement_json
        shared = {'cohort': '30–60', 'at': 2**60 + 1, 'mass': Fraction(2**150 + 7, 19), 'quiet': None}
        value = {'unicode': 'α\n界', 'paths': [shared, shared], 'tuple': (True, False, -0.0, 2.5), 'empty': {}}
        from trading_research.measurements.tape import ValueArea
        value['value_area'] = ValueArea(10, (10, 12), 9, 12, Fraction(7, 10), Fraction(3, 4), 'lower')
        self.assertEqual(exact_measurement_json(value), canonical_json(value))
        with tempfile.TemporaryDirectory() as folder:
            out = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=1024**2, maximum_file_bytes=1024**2)
            result = out.json_compressed('fast.json.zst', value, kind='fixture', measurement_fast_path=True)
            self.assertEqual(read_json_artifact(result), json.loads(canonical_json(value)))
            self.assertEqual(result['canonicalizer'], 'exact_measurement_domain_v1')
        for wrong in ({1: 'coerced'}, {'unsupported': object()}):
            with self.assertRaises(ContractError):
                exact_measurement_json(wrong)
        with self.assertRaises(ValueError):
            exact_measurement_json({'x': float('nan')})
        circular = []
        circular.append(circular)
        with self.assertRaises(ValueError):
            exact_measurement_json(circular)
        with self.assertRaises(ContractError):
            exact_measurement_json(value, maximum_items=1)

    def test_complete_series_parity_ignores_file_cuts_and_detects_lost_multiplicity(self):
        from trading_research.research.auction_flow_parity import compare_series
        values = pa.table({'t': pa.array(2**60 + np.arange(65539, dtype=np.int64)),
                           'same_print': np.ones(65539, dtype=np.int64)})
        with tempfile.TemporaryDirectory() as folder:
            output = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=8 * 1024**2, maximum_file_bytes=4 * 1024**2)
            def series(name, table, encoding):
                current = ParquetSeries(output, name, encoding=encoding)
                current.append(table)
                return current.finish()
            original = series('original', values, 'plain')
            first = series('first', values.slice(0, 21), 'delta')
            second = series('second', values.slice(21), 'delta')
            result = compare_series([original], [first, second])
            self.assertTrue(result['passed'])
            self.assertEqual(result['exact_field_comparisons'], 2 * len(values))
            with self.assertRaises(IntegrityError):
                compare_series([original], [second])

    def test_lossless_delta_storage_keeps_wide_signed_clocks_nulls_and_noncanonical_float_bits(self):
        bits = np.array([0, 0x8000000000000000, 0x7ff8000000000001, 0x7ff8000000000002], dtype=np.uint64)
        values = pa.table({'t': pa.array([-(2**63) + 1, 2**63 - 1, None, 2**60 + 1], type=pa.int64()),
            'raw_price': pa.array(bits.view(np.float64)), 'source_key': ['same', None, 'same', 'different'],
            'valid': [True, None, False, True], 'flags': pa.array([255, 0, None, 32], type=pa.uint8())})
        with tempfile.TemporaryDirectory() as folder:
            output = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=1024**2, maximum_file_bytes=1024**2)
            series = ParquetSeries(output, 'delta-values', encoding='delta')
            series.append(values)
            result = series.finish()
            restored = pq.read_table(result['files'][0]['path'])
            self.assertTrue(result['roundtrip_exact'])
            self.assertEqual(value_digest(values), value_digest(restored))
            self.assertEqual(restored['raw_price'].to_numpy().view(np.uint64).tolist(), bits.tolist())
            self.assertEqual(result['encoding'], 'delta')

    def test_compressed_measurement_retains_exact_canonical_bytes_and_checks_decompressed_bound(self):
        from trading_research.operations.artifacts import canonical_json
        value = {'at': 2**60 + 1, 'fraction': Fraction(2**60 + 3, 7),
                 'repeated_source': [{'source': 'actual-row', 'count': 0, 'missing': None} for _ in range(1000)]}
        with tempfile.TemporaryDirectory() as folder:
            output = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=1024**2, maximum_file_bytes=1024**2)
            reference = output.json_compressed('measurement.json.zst', value, kind='exact_measurement')
            restored = read_json_artifact(reference)
            self.assertEqual(restored, json.loads(canonical_json(value)))
            self.assertTrue(reference['roundtrip_exact'])
            self.assertLess(reference['size_bytes'], reference['uncompressed_size_bytes'])
            with self.assertRaises(ContractError):
                read_json_artifact(reference, maximum_uncompressed_bytes=100)
            changed = {**reference, 'uncompressed_sha256': '0' * 64}
            with self.assertRaises(IntegrityError):
                read_json_artifact(changed)

    def test_value_hash_ignores_slices_and_null_storage_but_preserves_exact_valid_bits(self):
        base = pa.table({'t': pa.array([None, 2**60, 2**60 + 1, None, 2**60 + 3], type=pa.int64()),
                         'sign': pa.array(['unused', 'B', None, '', 'A']),
                         'available': pa.array([True, False, None, True, False])})
        sliced = base.slice(1, 3)
        copied = pa.Table.from_pylist(sliced.to_pylist(), schema=sliced.schema)
        self.assertEqual(value_digest(sliced), value_digest(copied))
        changed = copied.set_column(0, 't', pa.array([2**60 + 1, 2**60 + 1, None], type=pa.int64()))
        self.assertNotEqual(value_digest(copied), value_digest(changed))
        changed = copied.set_column(1, 'sign', pa.array(['B', '', '']))
        self.assertNotEqual(value_digest(copied), value_digest(changed))
        bits = np.array([0, 0x8000000000000000, 0x7ff8000000000001, 0x7ff8000000000002], dtype=np.uint64)
        values = pa.table({'raw_price': pa.array(bits.view(np.float64))})
        for a, b in ((0, 1), (2, 3)):
            self.assertNotEqual(value_digest(values.slice(a, 1)), value_digest(values.slice(b, 1)))
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=1024**2, maximum_file_bytes=1024**2)
            series = ParquetSeries(outputs, 'float-bits')
            series.append(values)
            result = series.finish()
            restored = pq.read_table(result['files'][0]['path'])
            self.assertEqual(restored['raw_price'].to_numpy().view(np.uint64).tolist(), bits.tolist())

    def test_complete_ordered_multifile_roundtrip_retains_integer_clocks_nulls_and_multiplicity(self):
        with tempfile.TemporaryDirectory() as folder:
            outputs = BoundedOutputs(Path(folder) / 'outputs', maximum_total_bytes=8 * 1024**2, maximum_file_bytes=4 * 1024**2)
            values = pa.table({'t': pa.array(2**60 + np.arange(70003, dtype=np.int64)),
                'size': np.full(70003, 2**32 - 2, dtype=np.int64),
                'side': pa.array(['B', 'A', None] * 23334 + ['B']),
                'same_economic_value': np.ones(70003, dtype=np.int64)})
            series = ParquetSeries(outputs, 'events', maximum_rows_per_file=65536)
            series.append(values.slice(0, 2))
            series.append(values.slice(2))
            result = series.finish()
            self.assertTrue(result['roundtrip_exact'])
            self.assertEqual(result['rows'], 70003)
            self.assertEqual([r['rows'] for r in result['files']], [65536, 4467])
            self.assertEqual(result['compared_values'], 4 * 70003)
            self.assertEqual(result['serialized_bytes'], outputs.written)
            reference = outputs.json('exact.json', {'fraction': Fraction(2**60 + 1, 3)}, kind='exact_measurement')
            self.assertEqual(json.loads(Path(reference['path']).read_text()), {'fraction': {'$fraction': [2**60 + 1, 3]}})
            self.assertEqual(outputs.written, sum(p.stat().st_size for p in outputs.directory.iterdir()))
            with self.assertRaises(IntegrityError):
                series.append(values)

    def test_file_and_aggregate_limits_reject_bytes_before_they_are_written(self):
        for aggregate in (True, False):
            with tempfile.TemporaryDirectory() as folder:
                output = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=12, maximum_file_bytes=8)
                first = output.create('first.bin')
                first.write(b'12345678')
                first.close()
                second = output.create('second.bin')
                second.write(b'1234')
                with self.assertRaises(ContractError):
                    if aggregate:
                        second.write(b'5')
                    else:
                        with output.create('oversize.bin') as oversized:
                            oversized.write(b'123456789')
                second.close()
                self.assertEqual(output.written, 12)
                self.assertEqual(sum(p.stat().st_size for p in output.directory.iterdir()), 12)
                with self.assertRaises(IntegrityError):
                    output.reference('first.bin', kind='partial')

    def test_schema_drift_invalidates_the_complete_series(self):
        with tempfile.TemporaryDirectory() as folder:
            output = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=1024**2, maximum_file_bytes=1024**2)
            series = ParquetSeries(output, 'drift')
            series.append(pa.table({'t': [1, 2]}))
            with self.assertRaises(IntegrityError):
                series.append(pa.table({'t': [3.0]}))
            with self.assertRaises(IntegrityError):
                series.finish()


if __name__ == '__main__':
    unittest.main()
