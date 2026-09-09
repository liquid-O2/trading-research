"""Independent tests for the bounded QuantPad one-minute OHLC admission."""

import hashlib
from pathlib import Path
import tempfile
import unittest

from trading_research.data.ohlc import (
    read_definition_index,
    read_ohlc_partition,
)
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError


class OHLCAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            raise unittest.SkipTest("pinned Arrow dependency unavailable")
        cls.pa, cls.pq = pa, pq
        cls.definition_schema = pa.schema([
            pa.field("t", pa.int64()),
            pa.field("ts_recv", pa.int64()),
            pa.field("raw_symbol", pa.string()),
            pa.field("instrument_id", pa.int32()),
            pa.field("instrument_class", pa.string()),
            pa.field("security_update_action", pa.string()),
            pa.field("activation", pa.int64()),
            pa.field("expiration", pa.int64()),
            pa.field("min_price_increment", pa.float64()),
            pa.field("contract_multiplier", pa.float64()),
        ])
        cls.ohlc_schema = pa.schema([
            pa.field("t", pa.int64()),
            pa.field("o", pa.float64()),
            pa.field("h", pa.float64()),
            pa.field("l", pa.float64()),
            pa.field("c", pa.float64()),
            pa.field("v", pa.float64()),
            pa.field("instrument_id", pa.int32()),
        ])

    def definition(self, instrument_id=7, *, symbol="NQH1", activation=0,
                   expiration=300_000_000_000, tick=0.25, event=1_000_000_000,
                   received=1_100_000_000, action="A"):
        return {
            "t": event,
            "ts_recv": received,
            "raw_symbol": symbol,
            "instrument_id": instrument_id,
            "instrument_class": "F",
            "security_update_action": action,
            "activation": activation,
            "expiration": expiration,
            "min_price_increment": tick,
            "contract_multiplier": None,
        }

    def write_definitions(self, folder, rows):
        path = Path(folder) / "definitions.parquet"
        self.pq.write_table(self.pa.Table.from_pylist(rows, schema=self.definition_schema), path)
        return path

    def write_ohlc(self, folder, rows, *, name="ohlc.parquet", schema=None):
        path = Path(folder) / name
        self.pq.write_table(
            self.pa.Table.from_pylist(rows, schema=self.ohlc_schema if schema is None else schema),
            path,
        )
        return path

    def index(self, folder, rows):
        definition_path = self.write_definitions(folder, rows)
        return read_definition_index((definition_path,), data_root=Path(folder), root="NQ")

    def ordinary_row(self, at, *, instrument_id=7, open_price=100.0,
                     high=101.0, low=99.5, close=100.5, volume=3.0):
        return {
            "t": at,
            "o": open_price,
            "h": high,
            "l": low,
            "c": close,
            "v": volume,
            "instrument_id": instrument_id,
        }

    def test_complete_source_and_definition_index_retain_identity_and_bitemporal_lineage(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            definitions = [
                self.definition(event=1_000_000_000, received=1_100_000_000),
                self.definition(event=2_000_000_000, received=2_100_000_000),
            ]
            index = self.index(root, definitions)
            selected = index.resolve(7, 60_000_000_000)
            self.assertIsNotNone(selected)
            self.assertEqual(selected.source_row, 1)
            self.assertEqual(selected.known_at_ns, 2_350_000_000)
            self.assertEqual(index.manifest["indexed_records"], 2)
            self.assertEqual(index.manifest["files"][0]["source_rows"], 2)
            self.assertTrue(index.manifest["files"][0]["all_row_ipc_sha256"])

            source = self.write_ohlc(root, [
                self.ordinary_row(60_000),
                self.ordinary_row(120_000),
            ])
            table, manifest = read_ohlc_partition(
                source, data_root=root, root="NQ", definition_index=index,
            )
            self.assertEqual(
                tuple(table.schema.names),
                ("start_ns", "end_ns", "known_at_ns", "open_ticks", "high_ticks",
                 "low_ticks", "close_ticks", "volume", "instrument_id", "contract_key",
                 "definition_version", "source_row", "valid", "reasons"),
            )
            self.assertEqual(tuple(str(field.type) for field in table.schema), (
                "int64", "int64", "int64", "int64", "int64", "int64", "int64",
                "int64", "int64", "string", "string", "int64", "bool", "string",
            ))
            rows = table.to_pylist()
            self.assertEqual(rows[0]["start_ns"], 60_000_000_000)
            self.assertEqual(rows[0]["end_ns"], 120_000_000_000)
            self.assertEqual(rows[0]["known_at_ns"], 180_000_000_000)
            self.assertEqual(
                (rows[0]["open_ticks"], rows[0]["high_ticks"], rows[0]["low_ticks"],
                 rows[0]["close_ticks"], rows[0]["volume"]),
                (400, 404, 398, 402, 3),
            )
            self.assertTrue(all(row["valid"] for row in rows))
            self.assertIn("NQH1", rows[0]["contract_key"])
            self.assertEqual([row["source_row"] for row in rows], [0, 1])
            self.assertEqual(manifest["status"], "accepted")
            self.assertEqual((manifest["source_rows"], manifest["output_rows"], manifest["valid_rows"]), (2, 2, 2))
            self.assertEqual(manifest["source_sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(manifest["raw_file_sha256"], manifest["source_sha256"])
            self.assertTrue(manifest["raw_file_retained"])
            self.assertEqual(manifest["all_row_ipc_rows"], 2)
            self.assertEqual(len(manifest["all_row_ipc_sha256"]), 64)

    def test_bad_grid_prices_volume_and_identity_remain_as_quarantined_quality_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.index(root, [self.definition(expiration=500_000_000_000)])
            source = self.write_ohlc(root, [
                self.ordinary_row(60_001, open_price=100.125),
                self.ordinary_row(120_000, high=99.5, low=101.0, volume=0),
                self.ordinary_row(180_000, instrument_id=999),
            ])
            table, manifest = read_ohlc_partition(
                source, data_root=root, root="NQ", definition_index=index,
            )
            rows = table.to_pylist()
            self.assertEqual(len(rows), 3)
            self.assertFalse(rows[0]["valid"])
            self.assertEqual(set(rows[0]["reasons"].split("|")), {"off_minute_grid", "off_tick_open"})
            self.assertFalse(rows[1]["valid"])
            self.assertEqual(
                set(rows[1]["reasons"].split("|")),
                {"nonpositive_volume", "high_below_ohlc_envelope", "low_above_ohlc_envelope"},
            )
            self.assertFalse(rows[2]["valid"])
            self.assertEqual(rows[2]["reasons"], "definition_not_available_at_bar_start")
            self.assertEqual([row["source_row"] for row in rows], [0, 1, 2])
            self.assertEqual((manifest["valid_rows"], manifest["invalid_rows"], manifest["status"]), (0, 3, "quarantined"))
            self.assertEqual(manifest["quality_counts"]["off_minute_grid"], 1)

    def test_roll_lifetimes_and_missing_tick_terms_cannot_be_forward_filled(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.index(root, [
                self.definition(
                    instrument_id=7, symbol="NQH1", expiration=119_000_000_000,
                ),
                self.definition(
                    instrument_id=7, symbol="NQM1", activation=120_000_000_000,
                    expiration=400_000_000_000, event=120_100_000_000,
                    received=120_200_000_000,
                ),
                self.definition(
                    instrument_id=8, symbol="NQU1", expiration=400_000_000_000,
                    tick=0.5, event=1_500_000_000, received=1_600_000_000,
                ),
            ])
            source = self.write_ohlc(root, [
                self.ordinary_row(60_000, instrument_id=7),
                self.ordinary_row(180_000, instrument_id=7),
                self.ordinary_row(240_000, instrument_id=8),
            ])
            table, manifest = read_ohlc_partition(
                source, data_root=root, root="NQ", definition_index=index,
            )
            rows = table.to_pylist()
            self.assertFalse(rows[0]["valid"])
            self.assertEqual(rows[0]["reasons"], "definition_not_active_through_bar_end")
            self.assertTrue(rows[1]["valid"])
            self.assertIn("NQM1", rows[1]["contract_key"])
            self.assertFalse(rows[2]["valid"])
            self.assertEqual(rows[2]["reasons"], "definition_tick_not_quarter")
            self.assertEqual(manifest["quality_counts"]["definition_not_active_through_bar_end"], 1)
            self.assertEqual(manifest["quality_counts"]["definition_tick_not_quarter"], 1)

    def test_overlapping_reused_id_is_an_explicit_ambiguous_definition(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.index(root, [
                self.definition(instrument_id=7, symbol="NQH1"),
                self.definition(instrument_id=7, symbol="NQM1"),
            ])
            source = self.write_ohlc(root, [self.ordinary_row(60_000)])
            table, manifest = read_ohlc_partition(
                source, data_root=root, root="NQ", definition_index=index,
            )
            row = table.to_pylist()[0]
            self.assertFalse(row["valid"])
            self.assertEqual(row["reasons"], "ambiguous_definition")
            self.assertEqual(manifest["quality_counts"]["ambiguous_definition"], 1)

    def test_unlocatable_or_unsorted_timestamps_are_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.index(root, [self.definition(expiration=500_000_000_000)])
            unsorted = self.write_ohlc(root, [self.ordinary_row(60_000), self.ordinary_row(0)], name="unsorted.parquet")
            with self.assertRaises(IntegrityError):
                read_ohlc_partition(unsorted, data_root=root, root="NQ", definition_index=index)

            null_time = self.write_ohlc(root, [self.ordinary_row(None)], name="null-time.parquet")
            with self.assertRaises(IntegrityError):
                read_ohlc_partition(null_time, data_root=root, root="NQ", definition_index=index)

            overflowing = self.write_ohlc(
                root, [self.ordinary_row((2**63 - 1) // 1_000_000)], name="overflow.parquet",
            )
            with self.assertRaises(IntegrityError):
                read_ohlc_partition(overflowing, data_root=root, root="NQ", definition_index=index)

    def test_corrupt_missing_wrong_schema_and_unbounded_sources_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.index(root, [self.definition(expiration=500_000_000_000)])
            missing = root / "missing.parquet"
            with self.assertRaises(DependencyUnavailable):
                read_ohlc_partition(missing, data_root=root, root="NQ", definition_index=index)

            corrupt = root / "corrupt.parquet"
            corrupt.write_bytes(b"not a parquet container")
            with self.assertRaises(IntegrityError):
                read_ohlc_partition(corrupt, data_root=root, root="NQ", definition_index=index)

            wrong_schema = root / "wrong-schema.parquet"
            wrong = self.ohlc_schema.set(0, self.pa.field("t", self.pa.int32()))
            self.write_ohlc(root, [self.ordinary_row(0)], name=wrong_schema.name, schema=wrong)
            with self.assertRaises(ContractError):
                read_ohlc_partition(wrong_schema, data_root=root, root="NQ", definition_index=index)

            bounded = self.write_ohlc(root, [self.ordinary_row(0), self.ordinary_row(60_000)], name="bounded.parquet")
            with self.assertRaises(DependencyUnavailable):
                read_ohlc_partition(bounded, data_root=root, root="NQ", definition_index=index, maximum_rows=1)
            with self.assertRaises(DependencyUnavailable):
                read_ohlc_partition(bounded, data_root=root, root="NQ", definition_index=index, maximum_file_bytes=1)

    def test_deleted_definition_is_retained_as_unresolved_evidence_and_cannot_admit_a_bar(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.index(root, [
                self.definition(instrument_id=7),
                self.definition(instrument_id=8, symbol="NQM1", action="D"),
            ])
            self.assertEqual(len(index), 1)
            self.assertEqual(index.manifest["unresolved_rows"], 1)
            self.assertEqual(index.manifest["unresolved"][0]["source_row"], 1)
            source = self.write_ohlc(root, [self.ordinary_row(0, instrument_id=8)])
            table, manifest = read_ohlc_partition(
                source, data_root=root, root="NQ", definition_index=index,
            )
            self.assertFalse(table.to_pylist()[0]["valid"])
            self.assertEqual(table.to_pylist()[0]["reasons"], "definition_not_available_at_bar_start")
            self.assertEqual(manifest["status"], "quarantined")

    def test_same_id_delete_blocks_old_lifetime_until_a_later_known_update(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            index = self.index(root, [
                self.definition(
                    instrument_id=7, symbol="NQH1", activation=0,
                    expiration=300_000_000_000, event=1_000_000_000,
                    received=1_100_000_000,
                ),
                self.definition(
                    instrument_id=7, symbol="NQH1", activation=0,
                    expiration=300_000_000_000, event=60_000_000_000,
                    received=60_100_000_000, action="D",
                ),
                self.definition(
                    instrument_id=7, symbol="NQM1", activation=60_000_000_000,
                    expiration=400_000_000_000, event=120_000_000_000,
                    received=120_100_000_000,
                ),
            ])
            self.assertEqual(len(index), 2)
            self.assertEqual(len(index.blocks), 1)
            self.assertIsNone(index.resolve(7, 90_000_000_000))
            self.assertIsNotNone(index.resolve(7, 180_000_000_000))
            source = self.write_ohlc(root, [
                self.ordinary_row(120_000, instrument_id=7),
                self.ordinary_row(180_000, instrument_id=7),
            ])
            table, manifest = read_ohlc_partition(
                source, data_root=root, root="NQ", definition_index=index,
            )
            rows = table.to_pylist()
            self.assertFalse(rows[0]["valid"])
            self.assertEqual(rows[0]["reasons"], "definition_blocked_by_unresolved_update")
            self.assertTrue(rows[1]["valid"])
            self.assertIn("NQM1", rows[1]["contract_key"])
            self.assertEqual(manifest["quality_counts"]["definition_blocked_by_unresolved_update"], 1)

    def test_unknown_update_and_newly_inactive_definition_never_restore_an_older_lifetime(self):
        with tempfile.TemporaryDirectory() as folder:
            index = self.index(folder, [
                self.definition(),
                self.definition(action="X", event=60_000_000_000, received=60_100_000_000),
                self.definition(event=120_000_000_000, received=120_100_000_000),
            ])
            self.assertIsNotNone(index.resolve(7, 60_000_000_000))
            self.assertIsNone(index.resolve(7, 90_000_000_000))
            self.assertIsNotNone(index.resolve(7, 180_000_000_000))
            inactive = self.index(folder, [
                self.definition(expiration=300_000_000_000),
                self.definition(expiration=120_000_000_000, event=30_000_000_000, received=30_100_000_000),
            ])
            self.assertIsNone(inactive.resolve(7, 180_000_000_000))

    def test_unidentifiable_definition_is_rejected_and_unknown_clock_quarantines_the_exact_id(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fractional_schema = self.definition_schema.set(3, self.pa.field("instrument_id", self.pa.float64()))
            path = root / "fractional-id.parquet"
            self.pq.write_table(self.pa.Table.from_pylist([self.definition(instrument_id=7.5)], schema=fractional_schema), path)
            with self.assertRaises(IntegrityError):
                read_definition_index((path,), data_root=root, root="NQ")
            row = self.definition()
            row["t"] = None
            index = self.index(root, [self.definition(), row])
            self.assertEqual(index.unknown_instrument_ids, (7,))
            self.assertIsNone(index.resolve(7, 60_000_000_000))


if __name__ == "__main__":
    unittest.main()
