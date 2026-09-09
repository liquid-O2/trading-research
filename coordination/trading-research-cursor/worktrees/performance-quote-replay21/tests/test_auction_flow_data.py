from pathlib import Path
import tempfile
import unittest

import pyarrow as pa
import pyarrow.parquet as pq

from trading_research.data.reconcile import footer_index
from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_data import AuctionFlowStream, RAW_FIELDS


DATASET = "quantpad/cme__nq-continuous-futures__mbp-1"


def raw(at, *, action="A", side="B", size=5, price=100.0, flags=128, instrument=1):
    return {"t": at, "action": action, "side": side, "price": price, "size": size,
            "bid_px": 100.0, "ask_px": 100.25, "bid_sz": 7, "ask_sz": 9,
            "instrument_id": instrument, "flags": flags}


class AuctionFlowDataTests(unittest.TestCase):
    def test_adjacent_source_parts_keep_global_order_gap_lineage_and_separate_local_flow_reset(self):
        rows = [raw(0), raw(2, action='T', flags=0), raw(4, flags=132), raw(9),
                raw(20), raw(20, action='T', flags=0), raw(25, action='T', flags=0, side='A'), raw(29)]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.write(root, rows)
            full = self.stream(root, index, start=0, end=30)
            expected = list(full)
            first = self.stream(root, index, start=0, end=20)
            left = list(first)
            carry = first.carry()
            second = self.stream(root, index, start=20, end=30, continuation=carry)
            right = list(second)
            for field in ('raw', 'quotes', 'trades', 'excluded_trades'):
                def values(batches):
                    return [r for b in batches for t in (getattr(b, field) if field in ('quotes', 'trades')
                            else (getattr(b, field),)) for r in t.to_pylist()]
                self.assertEqual(values(left + right), values(expected))
            manifest = second.manifest()
            self.assertTrue(manifest['projection']['observed_prefix_flow_complete']['1'])
            self.assertFalse(second.carry()['prefix_flow_complete']['1'])
            self.assertEqual(second.carry()['blocked']['1'], carry['blocked']['1'])
            self.assertEqual(second.carry()['next_source_order'], len(rows))
            self.assertEqual(manifest['projection']['unrecovered_book_instruments']['1'], 2)

    def test_source_continuation_cannot_skip_a_cut_switch_an_acquisition_or_publish_a_partial_prefix(self):
        from trading_research.operations.artifacts import digest
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.write(root, [raw(0), raw(2), raw(8), raw(12), raw(20)])
            first = self.stream(root, index, start=0, end=10)
            iterator = iter(first)
            next(iterator)
            with self.assertRaises(IntegrityError):
                first.carry()
            list(iterator)
            carry = first.carry()
            with self.assertRaises(IntegrityError):
                self.stream(root, index, start=11, end=20, continuation=carry)
            corrupt = {**carry, 'next_source_order': 7}
            with self.assertRaises(IntegrityError):
                self.stream(root, index, start=10, end=20, continuation=corrupt)
            corrupt['sha256'] = digest({k: v for k, v in corrupt.items() if k != 'sha256'})
            with self.assertRaises(IntegrityError):
                self.stream(root, index, start=10, end=20, continuation=corrupt)
            pq.write_table(pq.read_table(root / DATASET / 'fixture.parquet'), root / DATASET / 'copy.parquet')
            copies = footer_index(root, datasets=(DATASET,), max_files=2)
            with self.assertRaises(IntegrityError):
                self.stream(root, copies, start=10, end=20, continuation=carry,
                            source_paths=(f'{DATASET}/copy.parquet',))

    def test_empty_interval_between_row_groups_still_verifies_the_containing_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.write(root, [raw(t) for t in (0, 1, 2, 80, 81, 82)])
            first = self.stream(root, index, start=0, end=10)
            list(first)
            empty = self.stream(root, index, start=10, end=60, continuation=first.carry())
            self.assertEqual(list(empty), [])
            self.assertEqual(empty.manifest()['physical_scan_rows'], 0)
            self.assertEqual(len(empty.manifest()['sources']), 1)
            self.assertEqual(empty.carry()['next_source_order'], 3)
            (root / DATASET / 'fixture.parquet').touch()
            with self.assertRaises(IntegrityError):
                list(self.stream(root, index, start=10, end=60, continuation=first.carry()))

    def test_overlapping_acquisitions_are_explicit_variants_and_all_field_identity_ignores_reader_batching(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            rows = [raw(0), raw(2, action='T', flags=0), raw(2, action='T', flags=0), raw(8)]
            self.write(root, rows)
            original = root / DATASET / 'fixture.parquet'
            alias = root / DATASET / 'other.parquet'
            pq.write_table(pq.read_table(original), alias, row_group_size=2)
            index = footer_index(root, datasets=(DATASET,), max_files=2)
            with self.assertRaises(IntegrityError):
                self.stream(root, index, start=0, end=10)
            fingerprints = []
            for name, batch_rows in (('fixture.parquet', 1), ('fixture.parquet', 17), ('other.parquet', 2)):
                stream = AuctionFlowStream(data_root=root, index=index, dataset=DATASET, start_ns=0, end_ns=10,
                    maximum_scan_rows=100, latency_ns=250, batch_rows=batch_rows, source_paths=(f'{DATASET}/{name}',))
                batches = list(stream)
                fingerprints.append(stream.manifest()['canonical_selected_raw_stream'])
                self.assertEqual(sum(len(t) for b in batches for t in b.trades), 2)
                self.assertEqual([r['source_order'] for b in batches for r in b.raw.to_pylist()], [0, 1, 2, 3])
            self.assertEqual(fingerprints[0], fingerprints[1])
            self.assertEqual(fingerprints[0], fingerprints[2])

    def write(self, root, rows):
        path = root / DATASET / "fixture.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        schema = pa.schema([pa.field(name, pa.string() if name in ("action", "side")
                                     else pa.float64() if name in ("price", "bid_px", "ask_px")
                                     else pa.int64()) for name in RAW_FIELDS])
        pq.write_table(pa.Table.from_pylist(rows, schema=schema), path, row_group_size=3)
        return footer_index(root, datasets=(DATASET,), max_files=1)

    def stream(self, root, index, start=2, end=10, **kwargs):
        return AuctionFlowStream(data_root=root, index=index, dataset=DATASET, start_ns=start,
                                 end_ns=end, maximum_scan_rows=100, latency_ns=250, batch_rows=2, **kwargs)

    def test_filter_keeps_actual_physical_addresses_multiplicity_and_original_sides(self):
        rows = [raw(0), raw(1), raw(2, action="T", flags=0), raw(2, action="T", flags=0),
                raw(3, action="T", flags=0, side="N", size=8), raw(5)]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stream = self.stream(root, self.write(root, rows))
            batches = list(stream)
            self.assertTrue(all(isinstance(t, pa.Table) for b in batches for t in
                                (b.raw, b.excluded_trades, *b.trades, *b.quotes)))
            trades = [r for batch in batches for table in batch.trades for r in table.to_pylist()]
            report = stream.manifest()
        self.assertEqual([r["source_row"] for r in trades], [2, 3, 4])
        self.assertEqual([r["source_order"] for r in trades], [0, 1, 2])
        self.assertEqual([r["raw_side"] for r in trades], ["B", "B", "N"])
        self.assertEqual([r["known_at_ns"] for r in trades], [252, 252, 253])
        self.assertEqual(report["projection"]["counts"]["volume"], 18)
        self.assertFalse(report["strategy_receipt_observed"])

    def test_gap_snapshot_invalid_size_and_offgrid_volume_keep_different_channels(self):
        rows = [raw(2), raw(3, action="T", flags=0, side="?", price=100.1, size=3),
                raw(4, flags=132), raw(5), raw(6, action="T", flags=32, size=9),
                raw(7, action="T", flags=0, size=0), raw(8, action="T", flags=4, size=2), raw(9)]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            stream = self.stream(root, self.write(root, rows))
            batches = list(stream)
            report = stream.manifest()
            excluded = [r for b in batches for r in b.excluded_trades.to_pylist()]
            trades = [r for b in batches for t in b.trades for r in t.to_pylist()]
            quotes = [r for b in batches for q in b.quotes for r in q.to_pylist()]
        self.assertEqual([(r["source_row"], r["exclusion_bits"]) for r in excluded], [(4, 1), (5, 2)])
        self.assertEqual([r["source_row"] for r in trades], [1, 6])
        self.assertEqual((trades[0]["price_valid"], report["projection"]["counts"]["unpriced_volume"]), (0, 3))
        self.assertEqual(report["projection"]["counts"]["volume"], 5)
        self.assertEqual([bool(q["book_valid"]) for q in quotes], [True, False, False, False, False])
        self.assertFalse(report["projection"]["observed_prefix_flow_complete"]["1"])

    def test_partial_iteration_and_source_change_cannot_publish_complete_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.write(root, [raw(t) for t in range(2, 9)])
            stream = self.stream(root, index)
            iterator = iter(stream)
            next(iterator)
            with self.assertRaises(IntegrityError):
                stream.manifest()
            iterator.close()
            with self.assertRaises(IntegrityError):
                stream.manifest()
            path = root / DATASET / "fixture.parquet"
            path.touch()
            with self.assertRaises(IntegrityError):
                list(self.stream(root, index))

    def test_absent_window_is_unavailable_not_observed_zero_flow(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.write(root, [raw(2), raw(3)])
            stream = self.stream(root, index, start=20, end=30)
            self.assertEqual(list(stream), [])
            report = stream.manifest()
        self.assertFalse(report["source_window_nonempty"])
        self.assertFalse(report["no_new_volume_claim_from_missing_source"])

    def test_overlapping_queries_preserve_one_physical_print_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.write(root, [raw(t, action="T", flags=0) for t in range(1, 10)])
            left = [r for b in self.stream(root, index, start=1, end=5) for t in b.trades for r in t.to_pylist()]
            right = [r for b in self.stream(root, index, start=4, end=10) for t in b.trades for r in t.to_pylist()]
        a = next(r for r in left if r["t"] == 4)
        b = next(r for r in right if r["t"] == 4)
        self.assertEqual((a["source_key"], a["source_row"]), (b["source_key"], b["source_row"]))


if __name__ == "__main__":
    unittest.main()
