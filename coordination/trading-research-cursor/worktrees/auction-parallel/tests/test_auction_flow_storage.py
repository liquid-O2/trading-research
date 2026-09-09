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

    def test_structural_cross_column_references_keep_exact_domain_and_older_descriptors(self):
        from trading_research.research.auction_flow_structural_encoding import (
            VERSION as CODEC_VERSION, encode_table, decode_table)
        start = [2**60 + 1, 2**60 + 101, 2**60 + 201, 2**60 + 301, 2**60 + 401, 2**60 + 501]
        bits = np.array([0, 0x8000000000000000, 0x7ff8000000000001, 0x7ff8000000000002, 0, 1], dtype=np.uint64)
        native = pa.table({
            'last_trade_at_ns': [-1, start[1] + 40, start[2] + 9, -1, start[4] + 99, -1],
            'last_price_ticks': [0, 404, -15, 0, 2**62 + 3, 0],
            'last_trade_source_order': [-1, 1005, -40, -1, 2**50 + 8, -1],
            'ofi_high_at_ns': [start[0] + 12, start[1] + 12, -1, -1, start[4] + 50, -1],
            'ofi_low_at_ns': [start[0] + 4, start[1] + 8, -1, -1, start[4] + 2, -1],
            'ofi_high_source_order': [-1, 77, -1, -1, 88, -1],
            'all__high_at_ns': [-1, start[1] + 15, start[2] + 6, -1, start[4] + 20, -1],
            'all__high_source_order': [-1, 1002, -45, -1, 2**50 + 3, -1],
            'known_at_ns': [s + 357 for s in start],
            'event_end_ns': [s + 100 for s in start],
            'nullable_at_ns': pa.array([None, -1, start[2] + 3, None, 2**60 + 3, -1], type=pa.int64()),
            'high_price_ticks': [0, 410, -10, 0, 2**62 + 10, 0],
            'low_price_ticks': [0, 397, -25, 0, 2**62 - 1, 0],
            'high_price_at_ns': [-1, start[1] + 20, start[2] + 4, -1, start[4] + 11, -1],
            'high_price_source_order': [-1, 1003, -48, -1, 2**50 + 1, -1],
            'low_price_at_ns': [-1, start[1] + 3, start[2] + 1, -1, start[4] + 5, -1],
            'low_price_source_order': [-1, 1001, -49, -1, 2**50 + 2, -1],
            'ny_ge100__low_at_ns': [-1, start[1] + 18, start[2] + 2, -1, start[4] + 8, -1],
            'ny_ge100__low_source_order': [-1, 1004, -47, -1, 2**50 + 4, -1],
            'raw_float': bits.view(np.float64),
            'instrument_id': np.ones(6, dtype=np.int64),
            'first_trade_source_order': [-1, 1000, -50, -1, 2**50, -1],
            'first_price_ticks': [0, 400, -20, 0, 2**62, 0],
            'first_trade_at_ns': [-1, start[1] + 7, start[2] + 3, -1, start[4] + 1, start[5] + 5],
            'event_start_ns': start,
        }).replace_schema_metadata({b'original-clock-domain': b'exact\x00bytes'})
        self.assertEqual(native.schema.names[0], 'last_trade_at_ns')
        self.assertLess(native.schema.get_field_index('last_trade_at_ns'),
                        native.schema.get_field_index('first_trade_at_ns'))
        self.assertLess(native.schema.get_field_index('event_end_ns'),
                        native.schema.get_field_index('event_start_ns'))
        encoded, descriptor = encode_table(native)
        self.assertEqual(descriptor['version'], CODEC_VERSION)
        self.assertEqual(CODEC_VERSION, 'auction-flow-exact-integer-structural-encoding-v1')
        self.assertTrue(encoded.schema.equals(native.schema, check_metadata=True))
        self.assertEqual([field.nullable for field in encoded.schema], [field.nullable for field in native.schema])
        by_col = {op['column']: op for op in descriptor['operations']}
        order = [op['column'] for op in descriptor['operations']]
        self.assertLess(order.index('event_end_ns'), order.index('known_at_ns'))
        self.assertLess(order.index('first_trade_at_ns'), order.index('last_trade_at_ns'))
        self.assertLess(order.index('first_trade_at_ns'), order.index('all__high_at_ns'))
        self.assertLess(order.index('first_trade_at_ns'), order.index('high_price_at_ns'))
        self.assertLess(order.index('first_trade_source_order'), order.index('last_trade_source_order'))
        self.assertLess(order.index('first_trade_source_order'), order.index('all__high_source_order'))
        self.assertEqual(by_col['known_at_ns']['reference'], 'event_end_ns')
        self.assertEqual(by_col['first_trade_at_ns']['reference'], 'event_start_ns')
        self.assertEqual(by_col['last_trade_at_ns']['reference'], 'first_trade_at_ns')
        self.assertEqual(by_col['high_price_at_ns']['reference'], 'first_trade_at_ns')
        self.assertEqual(by_col['low_price_at_ns']['reference'], 'first_trade_at_ns')
        self.assertEqual(by_col['all__high_at_ns']['reference'], 'first_trade_at_ns')
        self.assertEqual(by_col['ny_ge100__low_at_ns']['reference'], 'first_trade_at_ns')
        self.assertEqual(by_col['ofi_high_at_ns']['reference'], 'event_start_ns')
        self.assertEqual(by_col['ofi_low_at_ns']['reference'], 'event_start_ns')
        self.assertIsNone(by_col['ofi_high_source_order']['reference'])
        self.assertEqual(by_col['last_trade_source_order']['reference'], 'first_trade_source_order')
        self.assertEqual(by_col['high_price_source_order']['reference'], 'first_trade_source_order')
        self.assertEqual(by_col['low_price_source_order']['reference'], 'first_trade_source_order')
        self.assertEqual(by_col['all__high_source_order']['reference'], 'first_trade_source_order')
        self.assertEqual(by_col['ny_ge100__low_source_order']['reference'], 'first_trade_source_order')
        self.assertEqual(by_col['last_price_ticks']['reference'], 'first_price_ticks')
        self.assertEqual(by_col['high_price_ticks']['reference'], 'first_price_ticks')
        self.assertEqual(by_col['low_price_ticks']['reference'], 'first_price_ticks')
        self.assertNotIn('first_price_ticks', by_col)
        self.assertNotIn('event_start_ns', by_col)
        self.assertNotIn('nullable_at_ns', by_col)
        self.assertEqual(by_col['last_trade_at_ns']['null_restores_sentinel'], -1)
        self.assertIsNone(by_col['last_price_ticks']['null_restores_sentinel'])
        self.assertEqual(encoded['event_end_ns'].to_pylist(), [100] * 6)
        self.assertEqual(encoded['known_at_ns'].to_pylist(), [257] * 6)
        self.assertEqual(encoded['first_trade_at_ns'].to_pylist(), [None, 7, 3, None, 1, 5])
        self.assertEqual(encoded['last_trade_at_ns'].to_pylist(), [None, 33, 6, None, 98, None])
        self.assertEqual(encoded['high_price_at_ns'].to_pylist(), [None, 13, 1, None, 10, None])
        self.assertEqual(encoded['all__high_at_ns'].to_pylist(), [None, 8, 3, None, 19, None])
        self.assertEqual(encoded['ofi_high_at_ns'].to_pylist(), [12, 12, None, None, 50, None])
        self.assertEqual(encoded['ofi_low_at_ns'].to_pylist(), [4, 8, None, None, 2, None])
        self.assertNotEqual(encoded['ofi_high_at_ns'][0].as_py(), start[0] + 13)
        self.assertEqual(encoded['last_price_ticks'].to_pylist(), [0, 4, 5, 0, 3, 0])
        self.assertEqual(encoded['high_price_ticks'].to_pylist(), [0, 10, 10, 0, 10, 0])
        self.assertEqual(encoded['low_price_ticks'].to_pylist(), [0, -3, -5, 0, -1, 0])
        self.assertEqual(encoded['first_price_ticks'].to_pylist(), [0, 400, -20, 0, 2**62, 0])
        self.assertEqual(encoded['last_trade_source_order'].to_pylist(), [None, 5, 10, None, 8, None])
        self.assertEqual(encoded['all__high_source_order'].to_pylist(), [None, 2, 5, None, 3, None])
        self.assertEqual(encoded['ofi_high_source_order'].to_pylist(), [None, 77, None, None, 88, None])
        self.assertEqual(encoded['nullable_at_ns'].to_pylist(), [None, -1, start[2] + 3, None, 2**60 + 3, -1])
        self.assertEqual(encoded['nullable_at_ns'].null_count, native['nullable_at_ns'].null_count)
        self.assertEqual(encoded['raw_float'].to_numpy().view(np.uint64).tolist(), bits.tolist())
        restored = decode_table(encoded, descriptor)
        self.assertTrue(restored.schema.equals(native.schema, check_metadata=True))
        self.assertEqual(value_digest(restored), value_digest(native))
        self.assertEqual(restored['nullable_at_ns'].to_pylist(), native['nullable_at_ns'].to_pylist())

        quotes = pa.table({
            'ask': [107, -33, 2**62 + 6], 'known_at_ns': [2**60 + 258, 2**60 + 258, 2**60 + 260],
            'source_order': [15, 16, 35], 'bid': [100, -40, 2**62],
            't': [2**60 + 1, 2**60 + 1, 2**60 + 3], 'source_row': [7000, 7001, 7020], 'size': [5, 5, 6],
        })
        encoded, descriptor = encode_table(quotes)
        by_col = {op['column']: op for op in descriptor['operations']}
        self.assertEqual(by_col['ask']['reference'], 'bid')
        self.assertIsNone(by_col['ask']['null_restores_sentinel'])
        self.assertEqual(encoded['ask'].to_pylist(), [7, 7, 6])
        self.assertEqual(encoded['bid'].to_pylist(), [100, -40, 2**62])
        self.assertTrue(encoded.schema.equals(quotes.schema, check_metadata=True))
        self.assertEqual(value_digest(decode_table(encoded, descriptor)), value_digest(quotes))

        all_trade = pa.table({
            'event_start_ns': [2**60], 'event_end_ns': [2**60 + 100], 'known_at_ns': [2**60 + 200],
            'first_trade_at_ns': [2**60 + 7], 'ofi_high_at_ns': [2**60 + 12], 'ofi_low_at_ns': [2**60 + 4],
        })
        encoded, descriptor = encode_table(all_trade)
        by_col = {op['column']: op for op in descriptor['operations']}
        self.assertEqual(by_col['ofi_high_at_ns']['reference'], 'first_trade_at_ns')
        self.assertEqual(encoded['ofi_high_at_ns'].to_pylist(), [5])
        self.assertEqual(encoded['ofi_low_at_ns'].to_pylist(), [-3])
        self.assertEqual(value_digest(decode_table(encoded, descriptor)), value_digest(all_trade))

        missing_ref = pa.table({
            'event_start_ns': [2**60], 'event_end_ns': [2**60 + 100], 'known_at_ns': [2**60 + 200],
            'first_trade_at_ns': [-1], 'last_trade_at_ns': [-1], 'ofi_high_at_ns': [2**60 + 12],
            'first_trade_source_order': [-1], 'last_trade_source_order': [99],
            'all__high_source_order': [-1],
        })
        encoded, descriptor = encode_table(missing_ref)
        by_col = {op['column']: op for op in descriptor['operations']}
        self.assertEqual(by_col['ofi_high_at_ns']['reference'], 'event_start_ns')
        self.assertEqual(encoded['ofi_high_at_ns'].to_pylist(), [12])
        self.assertIsNone(by_col['last_trade_source_order']['reference'])
        self.assertEqual(encoded['last_trade_source_order'].to_pylist(), [99])
        self.assertEqual(value_digest(decode_table(encoded, descriptor)), value_digest(missing_ref))

        overflow = pa.table({
            'event_start_ns': [0], 'event_end_ns': [100], 'known_at_ns': [200],
            'first_trade_at_ns': [-(2**63) + 1], 'last_trade_at_ns': [2**63 - 1],
            'first_price_ticks': [-(2**63) + 1], 'last_price_ticks': [2**63 - 1],
            'high_price_ticks': [2**63 - 1], 'low_price_ticks': [2**63 - 1],
            'first_trade_source_order': [-(2**63) + 1], 'last_trade_source_order': [2**63 - 1],
        })
        encoded, descriptor = encode_table(overflow)
        by_col = {op['column']: op for op in descriptor['operations']}
        self.assertEqual(by_col['last_trade_at_ns']['reference'], 'event_start_ns')
        self.assertEqual(encoded['last_trade_at_ns'].to_pylist(), [2**63 - 1])
        self.assertNotIn('last_price_ticks', by_col)
        self.assertNotIn('high_price_ticks', by_col)
        self.assertNotIn('low_price_ticks', by_col)
        self.assertEqual(encoded['last_price_ticks'].to_pylist(), [2**63 - 1])
        self.assertIsNone(by_col['last_trade_source_order']['reference'])
        self.assertEqual(encoded['last_trade_source_order'].to_pylist(), [2**63 - 1])
        self.assertEqual(value_digest(decode_table(encoded, descriptor)), value_digest(overflow))
        ask_overflow = pa.table({'t': [1], 'known_at_ns': [2], 'source_row': [0],
                                 'source_order': [1], 'bid': [-(2**63) + 1], 'ask': [2**63 - 1]})
        encoded, descriptor = encode_table(ask_overflow)
        self.assertNotIn('ask', [op['column'] for op in descriptor['operations']])
        self.assertEqual(encoded['ask'].to_pylist(), [2**63 - 1])
        self.assertEqual(value_digest(decode_table(encoded, descriptor)), value_digest(ask_overflow))

        logical = pa.table({
            'event_start_ns': [2**60 + 1], 'event_end_ns': [2**60 + 101], 'known_at_ns': [2**60 + 201],
            'first_trade_at_ns': [2**60 + 11], 'last_trade_at_ns': [2**60 + 41],
            'first_trade_source_order': [9], 'last_trade_source_order': [12],
        })
        old_physical = pa.table({
            'event_start_ns': [2**60 + 1], 'event_end_ns': [100], 'known_at_ns': [100],
            'first_trade_at_ns': [10], 'last_trade_at_ns': [40],
            'first_trade_source_order': [9], 'last_trade_source_order': [12],
        })
        older = {'version': CODEC_VERSION, 'operations': [
            {'column': 'event_end_ns', 'reference': 'event_start_ns', 'null_restores_sentinel': None},
            {'column': 'known_at_ns', 'reference': 'event_end_ns', 'null_restores_sentinel': None},
            {'column': 'first_trade_at_ns', 'reference': 'event_start_ns', 'null_restores_sentinel': -1},
            {'column': 'last_trade_at_ns', 'reference': 'event_start_ns', 'null_restores_sentinel': -1},
            {'column': 'first_trade_source_order', 'reference': None, 'null_restores_sentinel': -1},
            {'column': 'last_trade_source_order', 'reference': None, 'null_restores_sentinel': -1},
        ]}
        self.assertEqual(value_digest(decode_table(old_physical, older)), value_digest(logical))

    def test_structural_cross_column_storage_roundtrip_files_tampering_and_quote_ask(self):
        import copy
        from trading_research.research.auction_flow_arrow import VERSION as VALUE_HASH_VERSION
        from trading_research.research.auction_flow_parity import compare_series
        from trading_research.research.auction_flow_storage import (
            LOGICAL_SCHEMA_KEY, PHYSICAL_ENCODING_KEY, VERSION as STORAGE_VERSION,
            read_series_tables)
        from trading_research.research.auction_flow_structural_encoding import (
            VERSION as CODEC_VERSION, decode_table)
        count = 65537
        start = 2**60 + 1 + 100 * np.arange(count, dtype=np.int64)
        trade = np.arange(count) % 5 != 0
        bits = np.resize(np.array([0, 0x8000000000000000, 0x7ff8000000000001, 0x7ff8000000000002], dtype=np.uint64), count)
        first_trade = np.where(trade, start + 7, -1)
        last_trade = np.where(trade, start + 40, -1)
        first_order = np.where(trade, 1000 + np.arange(count, dtype=np.int64), -1)
        last_order = np.where(trade, first_order + 5, -1)
        first_price = np.where(trade, 400 + (np.arange(count) % 10), 0).astype(np.int64)
        values = pa.table({
            'last_trade_at_ns': last_trade, 'last_price_ticks': np.where(trade, first_price + 4, 0),
            'last_trade_source_order': last_order, 'ofi_high_at_ns': start + 12,
            'all__high_at_ns': np.where(trade, start + 15, -1),
            'all__high_source_order': np.where(trade, first_order + 2, -1),
            'known_at_ns': start + 357, 'event_end_ns': start + 100,
            'nullable_at_ns': pa.array([None if i % 17 == 0 else (-1 if i % 17 == 1 else int(start[i] + 3))
                                        for i in range(count)], type=pa.int64()),
            'raw_float': bits.view(np.float64), 'instrument_id': np.ones(count, dtype=np.int64),
            'first_trade_source_order': first_order, 'first_price_ticks': first_price,
            'first_trade_at_ns': first_trade, 'event_start_ns': start,
        }).replace_schema_metadata({b'original-clock-domain': b'exact\x00bytes'})
        quotes = pa.table({
            'ask': 100 + (np.arange(count, dtype=np.int64) % 9),
            'known_at_ns': 2**60 + 258 + np.arange(count, dtype=np.int64),
            'source_order': 15 + np.arange(count, dtype=np.int64),
            'bid': 90 + (np.arange(count, dtype=np.int64) % 9),
            't': 2**60 + 1 + np.arange(count, dtype=np.int64),
            'source_row': 7000 + np.arange(count, dtype=np.int64),
            'size': np.full(count, 5, dtype=np.int64),
        })
        with tempfile.TemporaryDirectory() as folder:
            out = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=64 * 1024**2, maximum_file_bytes=32 * 1024**2)
            original = ParquetSeries(out, 'native-original', encoding='plain')
            original.append(values)
            old = original.finish()
            candidate = ParquetSeries(out, 'native-structural', encoding='structural', maximum_rows_per_file=65536)
            candidate.append(values.slice(0, 21))
            candidate.append(values.slice(21))
            new = candidate.finish()
            self.assertEqual(len(new['files']), 2)
            restored = pa.concat_tables(list(read_series_tables(new))).combine_chunks()
            self.assertTrue(restored.schema.equals(values.schema, check_metadata=True))
            for offset in range(0, count, 65536):
                self.assertEqual(value_digest(restored.slice(offset, min(65536, count - offset))),
                                 value_digest(values.slice(offset, min(65536, count - offset))))
            self.assertEqual(restored['raw_float'].to_numpy().view(np.uint64).tolist(), bits.tolist())
            self.assertTrue(compare_series([old], [new])['passed'])
            physical = pq.read_table(new['files'][0]['path'])
            self.assertIn(PHYSICAL_ENCODING_KEY, physical.schema.metadata)
            self.assertEqual(physical['last_trade_at_ns'][1].as_py(), 33)
            self.assertEqual(physical['last_price_ticks'][1].as_py(), 4)
            self.assertEqual(physical['last_trade_source_order'][1].as_py(), 5)
            self.assertEqual(physical['ofi_high_at_ns'][0].as_py(), 12)
            self.assertIsNone(physical['last_trade_at_ns'][0].as_py())
            changed = copy.deepcopy(new)
            changed['files'][0]['row_group_values'][0]['codec']['operations'] = list(
                reversed(changed['files'][0]['row_group_values'][0]['codec']['operations']))
            with self.assertRaises(IntegrityError):
                list(read_series_tables(changed))
            changed = copy.deepcopy(new)
            ops = changed['files'][0]['row_group_values'][0]['codec']['operations']
            last = next(op for op in ops if op['column'] == 'last_trade_at_ns')
            last['reference'] = 'event_start_ns'
            with self.assertRaises(IntegrityError):
                list(read_series_tables(changed))
            quote_plain = ParquetSeries(out, 'quote-original', encoding='plain')
            quote_plain.append(quotes)
            quote_old = quote_plain.finish()
            quote_series = ParquetSeries(out, 'quote-structural', encoding='structural', maximum_rows_per_file=65536)
            quote_series.append(quotes.slice(0, 8))
            quote_series.append(quotes.slice(8))
            quote_new = quote_series.finish()
            quote_restored = pa.concat_tables(list(read_series_tables(quote_new))).combine_chunks()
            self.assertTrue(quote_restored.schema.equals(quotes.schema, check_metadata=True))
            self.assertEqual(value_digest(quote_restored.slice(0, 65536)), value_digest(quotes.slice(0, 65536)))
            self.assertTrue(compare_series([quote_old], [quote_new])['passed'])
            quote_physical = pq.read_table(quote_new['files'][0]['path'])
            self.assertEqual(quote_physical['ask'][0].as_py(), 10)

            logical = values.slice(0, 2).combine_chunks()
            old_physical = pa.table({
                'last_trade_at_ns': pa.array([None, 40], type=pa.int64()),
                'last_price_ticks': logical['last_price_ticks'],
                'last_trade_source_order': pa.array([None, int(last_order[1])], type=pa.int64()),
                'ofi_high_at_ns': [12, 12], 'all__high_at_ns': pa.array([None, 15], type=pa.int64()),
                'all__high_source_order': pa.array([None, int(first_order[1] + 2)], type=pa.int64()),
                'known_at_ns': [257, 257], 'event_end_ns': [100, 100],
                'nullable_at_ns': logical['nullable_at_ns'], 'raw_float': logical['raw_float'],
                'instrument_id': logical['instrument_id'],
                'first_trade_source_order': pa.array([None, int(first_order[1])], type=pa.int64()),
                'first_price_ticks': logical['first_price_ticks'],
                'first_trade_at_ns': pa.array([None, 7], type=pa.int64()),
                'event_start_ns': logical['event_start_ns'],
            }, schema=logical.schema)
            older = {'version': CODEC_VERSION, 'operations': [
                {'column': 'event_end_ns', 'reference': 'event_start_ns', 'null_restores_sentinel': None},
                {'column': 'known_at_ns', 'reference': 'event_end_ns', 'null_restores_sentinel': None},
                {'column': 'first_trade_at_ns', 'reference': 'event_start_ns', 'null_restores_sentinel': -1},
                {'column': 'last_trade_at_ns', 'reference': 'event_start_ns', 'null_restores_sentinel': -1},
                {'column': 'all__high_at_ns', 'reference': 'event_start_ns', 'null_restores_sentinel': -1},
                {'column': 'ofi_high_at_ns', 'reference': 'event_start_ns', 'null_restores_sentinel': -1},
                {'column': 'first_trade_source_order', 'reference': None, 'null_restores_sentinel': -1},
                {'column': 'last_trade_source_order', 'reference': None, 'null_restores_sentinel': -1},
                {'column': 'all__high_source_order', 'reference': None, 'null_restores_sentinel': -1},
            ]}
            self.assertEqual(value_digest(decode_table(old_physical, older)), value_digest(logical))
            raw_schema = logical.schema.serialize().to_pybytes()
            logical_schema = pa.ipc.read_schema(pa.BufferReader(raw_schema))
            metadata = dict(logical.schema.metadata or {})
            metadata[PHYSICAL_ENCODING_KEY] = b'structural-v1'
            metadata[LOGICAL_SCHEMA_KEY] = raw_schema
            stored = old_physical.replace_schema_metadata(metadata)
            stream = out.create('older-0000.parquet')
            writer = pq.ParquetWriter(stream, stored.schema, compression='zstd', compression_level=3,
                                      write_statistics=True, version='2.6')
            writer.write_table(stored, row_group_size=len(stored))
            writer.close()
            stream.close()
            ref = out.reference('older-0000.parquet', kind='auction_flow_parquet')
            series = {'version': STORAGE_VERSION, 'series': 'older', 'rows': 2, 'row_groups': 1,
                      'encoding': 'structural', 'compression': 'zstd-level-3',
                      'schema': str(logical_schema), 'roundtrip_exact': True,
                      'files': [{**ref, 'rows': 2, 'row_groups': 1,
                                 'value_hash_version': VALUE_HASH_VERSION, 'physical_encoding': 'structural',
                                 'row_group_values': [{'rows': 2, 'sha256': value_digest(logical),
                                                       'codec': older}]}]}
            older_restored = pa.concat_tables(list(read_series_tables(series)))
            self.assertTrue(older_restored.schema.equals(logical_schema, check_metadata=True))
            self.assertEqual(value_digest(older_restored), value_digest(logical))
            tampered = copy.deepcopy(series)
            tampered['files'][0]['row_group_values'][0]['codec']['operations'][3]['reference'] = 'first_trade_at_ns'
            with self.assertRaises(IntegrityError):
                list(read_series_tables(tampered))

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
