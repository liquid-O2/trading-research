"""Disposable-root tests for the method-pack C02/C03 foundations."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from trading_research.research.method_pack.adapters import (
    c03_f1,
    decode_aggressor,
    inventory_acquired,
    iter_source_rows,
    _file_instrument_stats,
    normalize_mbp1_row,
    normalize_ohlcv_row,
    ownership_manifest,
    signed_size,
)
from trading_research.research.method_pack.clocks import (
    c02_f1,
    et_ns,
    range_hl,
    time_bar_from_minutes,
)
from trading_research.research.method_pack.core_fixtures import run_core_fixtures


class MethodPackAdapterTests(unittest.TestCase):
    def test_arrow_nanoseconds_and_metadata_only_instrument_inventory(self):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            self.skipTest('optional data dependencies are absent')
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'native.parquet'
            expected = 1_497_802_270_368_992_212
            pq.write_table(pa.table({'instrument_id': [42, 42],
                                     'ts_event': pa.array([expected, expected + 1], type=pa.timestamp('ns', tz='UTC'))}), path)
            rows = list(iter_source_rows(path))
            self.assertEqual([row['ts_event'] for row in rows], [expected, expected + 1])
            self.assertEqual(rows[0]['_timestamp_units']['ts_event']['source_unit'], 'ns')
            with patch('trading_research.research.method_pack.adapters.iter_source_rows', side_effect=AssertionError('must not scan the full tape')):
                stats = _file_instrument_stats([{'path': str(path), 'schema': ['instrument_id', 'ts_event']}])
            self.assertEqual(stats[0]['instrument_ids'], ['42'])
            self.assertTrue(stats[0]['complete_inventory'])

    def test_core_fixtures_are_hermetic_and_printed_rows_are_synthetic(self):
        with tempfile.TemporaryDirectory() as root:
            rows = run_core_fixtures(Path(root) / "does-not-exist")
        self.assertTrue(all(row["status"] == "pass" for row in rows))
        c03 = next(row for row in rows if row["id"] == "C03-F1")
        self.assertEqual(c03["evidence_mode"], "synthetic_fixture")
        self.assertEqual(c03["expected"]["tie_order"], "unknown_order")
        self.assertIsNone(c03["actual_value"]["path"])

    def test_c02_dst_and_missing_clock_bar(self):
        got = c02_f1()
        self.assertEqual(got["winter_0930_et_ns"], got["winter_1430_utc_ns"])
        self.assertEqual(got["summer_0930_et_ns"], got["summer_1330_utc_ns"])
        self.assertFalse(got["range_at_0945_available"])
        self.assertEqual(got["range_at_1000"], {"H": 105, "L": 100})
        self.assertFalse(got["five_minute_missing_1002_complete"])
        self.assertEqual(got["five_minute_missing_1002_ohlc"], {"O": None, "H": None, "L": None, "C": None})

    def test_exact_native_units_and_aggressor_side(self):
        bar = normalize_ohlcv_row({"t": 1_785_708_000_000, "o": 28_565.0, "h": 28_566.0, "l": 28_564.0, "c": 28_565.5, "v": 2, "instrument_id": 42})
        self.assertEqual(bar["start"], 1_785_708_000_000_000_000)
        self.assertEqual(bar["end"], 1_785_708_060_000_000_000)
        self.assertEqual(str(bar["O"]), "28565.0")
        self.assertEqual(decode_aggressor("B")["sign"], 1)
        self.assertEqual(decode_aggressor("A")["sign"], -1)
        self.assertIsNone(decode_aggressor("N")["sign"])
        self.assertEqual(signed_size("N", 3)["unknown_size"], 3)
        update = normalize_mbp1_row({"t": 10, "action": "A", "side": "B", "price": 100, "size": 5, "instrument_id": 42})
        self.assertFalse(update["is_trade"])
        self.assertIsNone(update["signed_size"])
        self.assertEqual(update["resting_side"], "B")
        trade = normalize_mbp1_row({"t": 11, "action": "T", "side": "B", "price": 100, "size": 5, "instrument_id": 42})
        self.assertEqual(trade["signed_size"], 5)

    def test_time_bar_known_empty_is_distinct_from_missing(self):
        day = date(2026, 1, 15)
        start, end = et_ns(day, 10), et_ns(day, 10, 5)
        bars = {
            et_ns(day, 10): {"O": 100, "H": 101, "L": 99, "C": 100, "V": 4},
            et_ns(day, 10, 1): {"O": 100, "H": 102, "L": 100, "C": 101, "V": 5},
            et_ns(day, 10, 3): {"O": 101, "H": 103, "L": 101, "C": 102, "V": 2},
            et_ns(day, 10, 4): {"O": 102, "H": 104, "L": 102, "C": 103, "V": 1},
        }
        missing = time_bar_from_minutes(start, end, bars, instrument_id="NQ", bar_id="x", size="5m")
        self.assertFalse(missing.complete)
        self.assertIsNone(missing.O)
        complete = time_bar_from_minutes(start, end, bars, instrument_id="NQ", bar_id="x", size="5m", known_empty=[et_ns(day, 10, 2)])
        self.assertTrue(complete.complete)
        self.assertEqual(complete.H, 104)
        self.assertEqual(complete.volume, 12)
        self.assertEqual(complete.known_at, end)

    def test_inventory_uses_disposable_root_and_detects_new_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bar_dir = root / "quantpad" / "cme__nq-continuous-futures__ohlcv-1m"
            bar_dir.mkdir(parents=True)
            bar_path = bar_dir / "2024-01.csv"
            with bar_path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=["t", "o", "h", "l", "c", "v", "instrument_id"])
                writer.writeheader()
                writer.writerow({"t": 1_704_067_200_000, "o": 100, "h": 101, "l": 99, "c": 100, "v": 1, "instrument_id": 7})
            result = inventory_acquired(root, "JJ-TBR")
        self.assertEqual(result["relevant_file_count"], 1)
        self.assertEqual(result["native_instruments"], ["NQ"])
        self.assertEqual(result["files"][0]["timestamp_unit"], "ms")
        self.assertTrue(result["files"][0]["valid"])
        self.assertEqual(result["actual_date_span"]["min_ns"], 1_704_067_200_000_000_000)
        self.assertEqual(result["years"]["2023"]["status"], "observed_bounds_only")
        self.assertFalse(result["years"]["2023"]["continuity_checked"])

    def test_fallback_overlap_is_a_hole_and_owned_spans_are_disjoint(self):
        fields = ["t", "action", "side", "price", "size", "bid_px", "ask_px", "bid_sz", "ask_sz", "instrument_id", "flags"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "quantpad" / "cme__nq-continuous-futures__mbp-1"
            directory.mkdir(parents=True)
            for name, price in (("2024-01-01.csv", 100), ("2024-01-02.csv", 101)):
                with (directory / name).open("w", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=fields)
                    writer.writeheader()
                    writer.writerow({"t": 1_704_067_200_000_000_000, "action": "T", "side": "B", "price": price, "size": 1, "bid_px": 99, "ask_px": 100, "bid_sz": 1, "ask_sz": 1, "instrument_id": 42, "flags": 0})
            audit = ownership_manifest(root)
        self.assertTrue(any("DATA_OVERLAP" in hole["reason"] for hole in audit["holes"]))
        spans = audit["owned_spans"]
        for left, right in zip(spans, spans[1:]):
            self.assertLessEqual(left["end_ns"], right["start_ns"])


if __name__ == "__main__":
    unittest.main()
