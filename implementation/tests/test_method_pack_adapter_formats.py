"""Format-specific adapter regressions on disposable roots."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from trading_research.research.method_pack.adapters import (
    _inspect_file,
    inventory_acquired,
    normalize_mbp1_row,
    normalize_trade_row,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class MethodPackAdapterFormatTests(unittest.TestCase):
    def test_context_calendar_timestamps_are_schedules_not_observed_market_history(self):
        import json
        import pyarrow as pa
        import pyarrow.parquet as pq
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "free-sources/context__event-calendar__normalized"
            directory.mkdir(parents=True)
            row = {"event_date": "2028-07-03", "event_ts_utc": "2028-07-03T17:00:00Z",
                   "status": "scheduled_or_observed", "time_basis": "standard_closing_time"}
            text = directory / "market-calendar.json"
            text.write_text(json.dumps([row]))
            parquet = directory / "market-calendar.parquet"
            pq.write_table(pa.table({"event_date": [datetime(2028, 7, 3).date()],
                                     "event_ts_utc": [datetime(2028, 7, 3, 17, tzinfo=timezone.utc)],
                                     "status": [row["status"]], "time_basis": [row["time_basis"]]}), parquet)
            for path in (text, parquet):
                with self.subTest(format=path.suffix):
                    record = _inspect_file(root, path, dataset_id="free-sources/context__event-calendar__normalized")
                    self.assertIsNone(record["event_start_ns"])
                    self.assertIsNone(record["event_end_ns"])
                    self.assertIsNone(record["available_at"])
                    self.assertEqual(record["scheduled_start_ns"], 1_846_256_400_000_000_000)
                    self.assertEqual(record["coverage_status"], "scheduled_calendar_only")
                    self.assertIsNone(record["coverage_valid"])
                    self.assertIn("scheduled_calendar_is_not_actual_release", {h["reason"] for h in record["coverage_holes"]})
            unrelated = _inspect_file(root, parquet, dataset_id="free-sources/demo-events")
            self.assertEqual(unrelated["event_start_ns"], 1_846_256_400_000_000_000)
            self.assertIsNone(unrelated["scheduled_start_ns"])

    def test_nested_fred_observations_are_read_instead_of_response_metadata(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources/fred__usd-rates__raw/DFF.json"
            _write(path, json.dumps({"series": {"seriess": [{"id": "DFF", "last_updated": "2026-09-03T00:00:00Z"}]},
                                    "observations": {"count": 2, "observations": [
                                        {"date": "2010-01-01", "value": "0.05"},
                                        {"date": "2026-09-02", "value": "3.50"}]}}))
            record = _inspect_file(root, path, dataset_id="free-sources/fred__usd-rates__raw")
            receipt = root / "free-sources/fred__usd-rates__raw/FETCH_RECEIPT.json"
            _write(receipt, '{"fetched_utc":"2026-09-03T00:00:00Z"}')
            metadata = _inspect_file(root, receipt, dataset_id="free-sources/fred__usd-rates__raw")
        self.assertEqual(record["rows"], 2)
        self.assertEqual(record["date_min"], "2010-01-01")
        self.assertEqual(record["date_max"], "2026-09-02")
        self.assertIsNone(record["available_at"])
        self.assertEqual(metadata["artifact_role"], "raw_provenance")

    def test_live_roll_segment_is_open_ended_not_truncated_to_last_closed_end(self):
        import pyarrow as pa
        import pyarrow.parquet as pq
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "derived/continuous-futures__instrument-and-roll-maps/nq-rolls.parquet"
            path.parent.mkdir(parents=True)
            pq.write_table(pa.table({"segment_start_ms": [1_700_000_000_000, 1_700_001_000_000],
                                     "segment_end_exclusive_ms": [1_700_001_000_000, None],
                                     "instrument_id": [42, 43]}), path)
            record = _inspect_file(root, path, dataset_id="derived/continuous-futures__instrument-and-roll-maps")
        self.assertTrue(record["roll_open_ended"])
        self.assertIsNone(record["roll_end_ns"])
        self.assertEqual(record["roll_open_segment_start_ns"], 1_700_001_000_000_000_000)
        self.assertEqual(record["roll_closed_end_ns"], 1_700_001_000_000_000_000)
        self.assertEqual(record["roll_unknown_end_count"], 0)
        self.assertFalse(record["coverage_holes"])

    def test_cboe_preamble_is_skipped_before_legal_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources" / "cboe__vx-futures__raw" / "cfevoloi.csv"
            _write(path, """CFE data is compiled for the convenience of site visitors and is furnished without responsibility for accuracy,,,,\nDate,VOLATILITY INDEX VOLUME\n\n3/26/2004,461\n3/29/2004,117\n""")
            record = _inspect_file(root, path, dataset_id="free-sources/cboe__vx-futures__raw")

        self.assertEqual(record["rows"], 2)
        self.assertEqual(record["schema"], ["Date", "VOLATILITY INDEX VOLUME"])
        self.assertEqual(record["date_min"], "2004-03-26")
        self.assertEqual(record["date_max"], "2004-03-29")
        self.assertEqual(record["coverage_status"], "calendar_date_only")

    def test_cftc_yymmdd_requires_and_matches_same_row_iso_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources" / "cftc__commitments-of-traders" / "cot_2021.txt"
            _write(path, "As of Date in Form YYMMDD,As of Date in Form YYYY-MM-DD,value\n211228,2021-12-28,1\n220104,2022-01-04,2\n")
            record = _inspect_file(root, path, dataset_id="free-sources/cftc__commitments-of-traders")

        self.assertEqual(record["date_min"], "2021-12-28")
        self.assertEqual(record["date_max"], "2022-01-04")
        self.assertNotIn("temporal_value_unparseable:As of Date in Form YYMMDD", {h["reason"] for h in record["coverage_holes"]})

    def test_bls_reference_month_is_reference_lane_and_et_clock_is_schedule(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources" / "bls__release-calendars" / "bls_release_dates.csv"
            _write(path, "release_name,reference_month,date,time_et,status\nCPI,October 2020,2020-11-12,08:30,actual\nCPI,November 2020,2020-12-10,08:30,actual\n")
            record = _inspect_file(root, path, dataset_id="free-sources/bls__release-calendars")

        self.assertEqual(record["reference_start_ns"], 1601510400000000000)
        self.assertEqual(record["reference_end_ns"], 1604275200000000000)
        self.assertIsNone(record["event_start_ns"])
        self.assertEqual(record["coverage_status"], "scheduled_calendar_only")
        self.assertIsNone(record["available_at"])

    def test_fomc_split_calendar_parts_form_inclusive_civil_interval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources" / "central-banks__fomc-and-boj-calendars" / "calendar_fomc.csv"
            _write(path, "year,month,days\n2023,Jan/Feb,31-1\n2024,April,30\n")
            record = _inspect_file(root, path, dataset_id="free-sources/central-banks__fomc-and-boj-calendars")

        self.assertEqual(record["date_min"], "2023-01-31")
        self.assertEqual(record["date_max"], "2024-04-30")
        self.assertEqual(record["calendar_start_ns"], 1675123200000000000)
        self.assertEqual(record["calendar_end_ns"], 1714521600000000000)
        self.assertTrue(record["date_only"])

    def test_sina_naive_datetime_uses_only_documented_asia_shanghai_zone(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources" / "cross-asset__copper" / "shfe_cu_main_15min_sina.csv"
            _write(path, "datetime,open,high,low,close,volume,hold\n2026-06-26 21:30:00,1,2,0,1,3,4\n2026-06-26 21:45:00,1,2,0,1,3,4\n")
            record = _inspect_file(root, path, dataset_id="free-sources/cross-asset__copper")

        expected = int(datetime(2026, 6, 26, 13, 30, tzinfo=timezone.utc).timestamp() * 1_000_000_000)
        self.assertEqual(record["event_start_ns"], expected)
        self.assertEqual(record["source_timezone"], "Asia/Shanghai")
        self.assertEqual(
            record["timezone_basis"],
            "documented_manifest:Asia/Shanghai:data/free-sources/cross-asset__copper/MANIFEST.tsv",
        )
        self.assertEqual(record["coverage_status"], "timed_observations")

    def test_undocumented_naive_datetime_remains_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources" / "example" / "events.csv"
            _write(path, "datetime,value\n2026-06-26 21:30:00,1\n")
            record = _inspect_file(root, path, dataset_id="free-sources/example")

        self.assertIsNone(record["event_start_ns"])
        self.assertEqual(record["coverage_status"], "no_temporal_bounds")
        self.assertIn("temporal_value_unparseable:datetime", {h["reason"] for h in record["coverage_holes"]})

    def test_unrelated_sina_naive_datetime_remains_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources" / "cross-asset__nikkei-and-fx" / "n225_intraday_sina.csv"
            _write(path, "datetime,open,high,low,close\n2026-06-26 21:30:00,1,2,0,1\n")
            record = _inspect_file(root, path, dataset_id="free-sources/cross-asset__nikkei-and-fx")

        self.assertIsNone(record["event_start_ns"])
        self.assertIsNone(record["source_timezone"])
        self.assertEqual(record["coverage_status"], "no_temporal_bounds")

    def test_malformed_receive_timestamp_is_rejected(self):
        with self.assertRaises(ValueError):
            normalize_trade_row({
                "t": 1_700_000_000_000_000_000,
                "ts_recv": "not-a-timestamp",
                "side": "B",
                "size": 1,
                "price": "1",
            })

    def test_definition_and_roll_metadata_have_separate_roles_and_bounds(self):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            self.skipTest("optional data dependencies are absent")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            definition = root / "quantpad" / "cme__nq-continuous-futures__definition" / "2024.parquet"
            definition.parent.mkdir(parents=True)
            pq.write_table(pa.table({
                "t": [1_700_000_000_000_000_000],
                "ts_recv": [1_700_000_000_100_000_000],
                "instrument_id": [42],
                "min_price_increment": [0.25],
            }), definition)
            rolls = root / "derived" / "continuous-futures__instrument-and-roll-maps" / "nq-rolls.parquet"
            rolls.parent.mkdir(parents=True)
            pq.write_table(pa.table({
                "segment_start_ms": [1_700_000_000_000, 1_700_001_000_000],
                "segment_end_exclusive_ms": [1_700_001_000_000, 1_700_002_000_000],
                "instrument_id": [42, 43],
            }), rolls)
            definition_record = _inspect_file(root, definition, dataset_id="quantpad/cme__nq-continuous-futures__definition")
            roll_record = _inspect_file(root, rolls, dataset_id="derived/continuous-futures__instrument-and-roll-maps")

        self.assertEqual(definition_record["artifact_role"], "contract_definition")
        self.assertEqual(definition_record["timestamp_unit"], "ns")
        self.assertEqual(definition_record["definition_start_ns"], 1_700_000_000_000_000_000)
        self.assertEqual(definition_record["available_at"], 1_700_000_000_100_000_000)
        self.assertEqual(roll_record["artifact_role"], "roll_metadata")
        self.assertEqual(roll_record["timestamp_unit"], "ms")
        self.assertEqual(roll_record["roll_start_ns"], 1_700_000_000_000_000_000)
        self.assertEqual(roll_record["roll_end_ns"], 1_700_002_000_000_000_000)
        self.assertFalse(roll_record["coverage_holes"])

    def test_known_at_uses_later_receive_time_and_preserves_missing_receive(self):
        event = 1_700_000_000_000_000_000
        later = normalize_trade_row({"t": event, "ts_recv": event + 5, "side": "B", "size": 1, "price": "1"})
        missing = normalize_mbp1_row({"t": event, "action": "T", "side": "A", "size": 1, "price": "1"})
        self.assertEqual(later["ts_recv"], event + 5)
        self.assertEqual(later["known_at"], event + 5)
        self.assertIsNone(missing["ts_recv"])
        self.assertEqual(missing["known_at"], event)


if __name__ == "__main__":
    unittest.main()
