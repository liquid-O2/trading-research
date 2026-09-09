"""Source-derived F01 faults; expectations are in validation/F01_SOURCE_CASES.md.

These assertions intentionally do not stand in for all acquired-schema golden
rows, atomic partition materialization, or future/live parity.
"""

from dataclasses import replace
from decimal import Decimal
import hashlib
import io
from pathlib import Path
import tempfile
import unittest

from trading_research.data.book import BookReducer
from trading_research.data.events import decode_fields, normalize_mbp
from trading_research.data.readers import native_records, parquet_mbp
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.units import NQ_REFERENCE
from tests.test_market_data import SCENARIO, event


def native_fields(**updates):
    fields = {"ts_event": 100, "ts_recv": 102, "action": "T", "side": "B",
              "price": 100_250_000_000, "size": 2, "flags": 0,
              "instrument_id": 42, "publisher_id": 1, "sequence": 7, "depth": 0,
              "bid_px_00": 100_000_000_000, "ask_px_00": 100_250_000_000,
              "bid_sz_00": 4, "ask_sz_00": 5, "bid_ct_00": 2, "ask_ct_00": 3}
    return {**fields, **updates}


class SourceIdentityFaultTests(unittest.TestCase):
    def test_verified_same_bytes_two_paths_count_once_but_two_physical_prints_count_twice(self):
        # File hash is independently fixed, while locator metadata differs.
        sha = hashlib.sha256(b"two distinct equal-looking trade rows").hexdigest()
        source = event(0, at=10, action="T", side="B", size=3, flags=0)
        a = replace(source.address, full_file_sha256=sha)
        alias = replace(a, relative_path="copied/renamed.parquet", container_version="other-inode-and-mtime")
        self.assertEqual(a.id, alias.id)
        values = [replace(source, address=address) for address in (a, alias, replace(a, row=1))]
        self.assertEqual(values[0].id, values[1].id)
        self.assertNotEqual(values[0].id, values[2].id)
        reducer = BookReducer()
        for value in values:
            reducer.apply(value)
        self.assertEqual((reducer.states[1].total_volume, reducer.states[1].trade_count), (6, 2))

    def test_metadata_only_locator_does_not_claim_verified_alias_equivalence(self):
        a = event(0).address
        self.assertIsNone(a.full_file_sha256)
        self.assertNotEqual(a.id, replace(a, relative_path="unverified-copy.parquet").id)

    def test_malformed_claimed_content_hash_is_rejected(self):
        for bad in ("metadata-v1", "0" * 63, "G" * 64):
            with self.subTest(hash=bad), self.assertRaises(ContractError):
                replace(event(0).address, full_file_sha256=bad)


class NativeSemanticFaultTests(unittest.TestCase):
    def test_negative_spread_price_and_distinct_price_timestamp_sentinels(self):
        negative = normalize_mbp(native_fields(price=-1_250_000_000), event(0).address,
                                 native=True, scenario=SCENARIO)
        self.assertEqual(negative.price, Decimal("-1.25"))
        missing = normalize_mbp(native_fields(price=2**63-1, ts_recv=2**64-1),
                                event(0).address, native=True, scenario=SCENARIO)
        self.assertIsNone(missing.price)
        self.assertIsNone(missing.clocks.provider_received_at)
        self.assertEqual(decode_fields(missing.raw_fields)["price"], 2**63-1)
        self.assertEqual(decode_fields(missing.raw_fields)["ts_recv"], 2**64-1)
        adjacent = normalize_mbp(native_fields(price=2**63-2), event(0).address,
                                 native=True, scenario=SCENARIO)
        self.assertEqual(adjacent.price, Decimal("9223372036.854775806"))
        with self.assertRaises(ContractError):
            normalize_mbp(native_fields(ts_event=2**64-1), event(0).address,
                          native=True, scenario=SCENARIO)

    def test_native_export_common_fields_match_without_inventing_missing_fields(self):
        fields = native_fields()
        native = normalize_mbp(fields, event(0).address, native=True, scenario=SCENARIO)
        exported = normalize_mbp({"t": 100, "action": ord("T"), "side": b"B",
                                  "price": 100.25, "size": 2, "flags": 0, "instrument_id": 42,
                                  "bid_px": 100.0, "ask_px": 100.25, "bid_sz": 4, "ask_sz": 5},
                                 event(1).address, native=False, scenario=SCENARIO)
        self.assertEqual((native.clocks.event_at, native.price, native.size, native.action,
                          native.aggressor, native.instrument_id),
                         (exported.clocks.event_at, exported.price, exported.size, exported.action,
                          exported.aggressor, exported.instrument_id))
        self.assertEqual((native.quote.bid, native.quote.ask, native.quote.bid_size, native.quote.ask_size),
                         (exported.quote.bid, exported.quote.ask, exported.quote.bid_size, exported.quote.ask_size))
        self.assertEqual((native.provider_sequence, native.clocks.provider_received_at, native.quote.bid_count), (7, 102, 2))
        self.assertEqual((exported.provider_sequence, exported.clocks.provider_received_at,
                          exported.quote.bid_count, exported.clocks.received_at), (None, None, None, None))

    def test_off_tick_export_residual_survives_and_tick_conversion_rejects_it(self):
        decoded = event(0, price=100.25000000000001)
        self.assertEqual(decoded.price, Decimal.from_float(100.25000000000001))
        with self.assertRaises(ContractError):
            NQ_REFERENCE.ticks(decoded.price)


class ContainerFaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
            import databento_dbn as dbn
        except ImportError:
            raise unittest.SkipTest("pinned data dependencies unavailable")
        cls.pa, cls.pq, cls.dbn = pa, pq, dbn

    def read_parquet(self, path, **kwargs):
        return list(parquet_mbp(path, data_root=path.parent, dataset_id="fixture",
                                acquisition_version="v1", scenario=SCENARIO, **kwargs))

    def dbn_bytes(self, records=1, *, incomplete_record=False):
        d = self.dbn
        metadata = d.Metadata(dataset="GLBX.MDP3", start=0, end=1000,
                              stype_in=d.SType.RAW_SYMBOL, stype_out=d.SType.INSTRUMENT_ID,
                              schema=d.Schema.MBP_1, version=3)
        record = d.MBP1Msg(publisher_id=1, instrument_id=42, ts_event=100,
                           price=100_250_000_000, size=2, action=d.Action.TRADE, side=d.Side.BID,
                           depth=0, ts_recv=102, flags=0, sequence=7,
                           levels=d.BidAskPair(100_000_000_000, 100_250_000_000, 4, 5, 2, 3))
        raw = bytes(metadata) + bytes(record) * records
        if incomplete_record:
            raw += bytes(record)[:25]
            # Compress bytes directly: a DBN transcoder would omit an incomplete
            # final record and accidentally repair the deliberately bad fixture.
            return bytes(self.pa.compress(raw, codec="zstd"))
        stream = io.BytesIO()
        with d.Transcoder(stream, encoding=d.Encoding.DBN, compression=d.Compression.ZSTD,
                          upgrade_policy=d.VersionUpgradePolicy.AS_IS) as writer:
            writer.write(raw)
        return stream.getvalue()

    def test_empty_parquet_has_zero_rows_and_zero_byte_file_is_corrupt(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "empty.parquet"
            schema = self.pa.Table.from_pylist([decode_fields(event(0).raw_fields)]).schema
            self.pq.write_table(self.pa.Table.from_pylist([], schema=schema), path)
            self.assertEqual(self.read_parquet(path), [])
            with self.pq.ParquetWriter(path, schema):
                pass
            self.assertEqual(self.read_parquet(path), [])
            path.write_bytes(b"")
            with self.assertRaises(IntegrityError):
                self.read_parquet(path)

    def test_missing_or_changed_declared_schema_never_silently_coerces(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "changed.parquet"
            table = self.pa.Table.from_pylist([decode_fields(event(0).raw_fields)])
            expected = table.schema
            for changed in (table.drop(["flags"]), table.set_column(0, "t", self.pa.array([10], type=self.pa.int32()))):
                self.pq.write_table(changed, path)
                with self.subTest(schema=str(changed.schema)), self.assertRaises(ContractError):
                    self.read_parquet(path, expected_schema=expected)
            # A profile change in metadata must not silently change scale either.
            self.pq.write_table(table.replace_schema_metadata({b"timestamp_profile": b"bar-ms"}), path)
            with self.assertRaises(ContractError):
                self.read_parquet(path, expected_schema=expected)

    def test_truncated_parquet_footer_is_explicit_integrity_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "truncated.parquet"
            self.pq.write_table(self.pa.Table.from_pylist([decode_fields(event(0).raw_fields)]), path)
            path.write_bytes(path.read_bytes()[:-6])
            with self.assertRaises(IntegrityError):
                self.read_parquet(path)

    def test_partial_groups_batch_sizes_duplicate_reads_and_reordered_files_preserve_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = [Path(folder) / name for name in ("a.parquet", "b.parquet")]
            for j, path in enumerate(paths):
                rows = [decode_fields(event(i+j*10, at=10).raw_fields) for i in range(5)]
                self.pq.write_table(self.pa.Table.from_pylist(rows), path, row_group_size=3)
            outputs = []
            for order, batch_size in ((paths, 1), (paths[::-1], 3), (paths, 2)):
                values = [row for p in order for row in self.read_parquet(p, max_rows=4, row_groups=(0,1), batch_size=batch_size)]
                self.assertEqual(len(values), 8)
                self.assertEqual({(v.address.partition, v.address.row) for v in values},
                                 {("row_group:0",0),("row_group:0",1),("row_group:0",2),("row_group:1",0)})
                outputs.append({v.id: v.raw_fields for v in values})
            self.assertEqual(outputs[0], outputs[1])
            self.assertEqual(outputs[1], outputs[2])

    def test_native_metadata_only_is_valid_empty_but_truncated_compressed_frame_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.dbn.zst"
            path.write_bytes(self.dbn_bytes(0))
            records = list(native_records(path, data_root=path.parent, dataset_id="fixture", acquisition_version="v1"))
            self.assertEqual([r.kind for r in records], ["Metadata"])
            complete = self.dbn_bytes(2)
            for removed in (1, 4, 11):
                path.write_bytes(complete[:-removed])
                with self.subTest(removed=removed), self.assertRaises(IntegrityError):
                    list(native_records(path, data_root=path.parent, dataset_id="fixture", acquisition_version="v1"))

    def test_native_zero_byte_and_incomplete_metadata_are_not_valid_empty_archives(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.dbn.zst"
            for payload in (b"", self.dbn_bytes(0)[:10]):
                path.write_bytes(payload)
                with self.subTest(length=len(payload)), self.assertRaises(IntegrityError):
                    list(native_records(path, data_root=path.parent, dataset_id="fixture", acquisition_version="v1"))

    def test_complete_compressed_frame_with_incomplete_dbn_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.dbn.zst"
            path.write_bytes(self.dbn_bytes(1, incomplete_record=True))
            with self.assertRaises(IntegrityError):
                list(native_records(path, data_root=path.parent, dataset_id="fixture", acquisition_version="v1"))

    def test_native_declared_schema_version_and_midstream_type_change_are_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.dbn.zst"
            path.write_bytes(self.dbn_bytes(1))
            valid = list(native_records(path, data_root=path.parent, dataset_id="fixture", acquisition_version="v1",
                                        expected_schema="mbp-1", expected_version=3))
            self.assertEqual([r.kind for r in valid], ["Metadata", "MBP1Msg"])
            for contract in ({"expected_schema": "statistics"}, {"expected_version": 2}):
                with self.subTest(contract=contract), self.assertRaises(ContractError):
                    list(native_records(path, data_root=path.parent, dataset_id="fixture", acquisition_version="v1", **contract))
            with self.pa.CompressedInputStream(io.BytesIO(self.dbn_bytes(1)), "zstd") as stream:
                raw = stream.read()
            d = self.dbn
            trade = d.TradeMsg(publisher_id=1, instrument_id=42, ts_event=101, price=100_000_000_000,
                               size=2, action=d.Action.TRADE, side=d.Side.BID, depth=0, ts_recv=103)
            path.write_bytes(bytes(self.pa.compress(raw + bytes(trade), codec="zstd")))
            with self.assertRaises(IntegrityError):
                list(native_records(path, data_root=path.parent, dataset_id="fixture", acquisition_version="v1"))

    def test_native_byte_budget_is_distinct_from_valid_eof_and_record_prefix(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "source.dbn.zst"
            path.write_bytes(self.dbn_bytes(2000))
            kwargs = dict(data_root=path.parent, dataset_id="fixture", acquisition_version="v1",
                          max_decompressed_bytes=65536)
            prefix = list(native_records(path, max_records=2, **kwargs))
            self.assertEqual([r.kind for r in prefix], ["Metadata", "MBP1Msg", "MBP1Msg"])
            with self.assertRaises(DependencyUnavailable):
                list(native_records(path, max_records=2001, **kwargs))


if __name__ == "__main__":
    unittest.main()
