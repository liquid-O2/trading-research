"""Bounded, disposable-root regressions for acquired context coverage."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
import tempfile
import unittest

from trading_research.research.method_pack.adapters import (
    _inspect_file,
    inventory_acquired,
)
from trading_research.research.method_pack.clocks import et_ns


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class MethodPackContextAdapterTests(unittest.TestCase):
    def test_date_only_csv_keeps_calendar_scope_and_marks_release_holes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources" / "fred__daily" / "series.csv"
            _write_csv(path, ["DATE", "value"], [
                {"DATE": "2020-01-02", "value": "1.0"},
                {"DATE": "2021-12-31", "value": "2.0"},
            ])

            result = inventory_acquired(root, method_id="STOIC-DATA")

        self.assertEqual(result["relevant_file_count"], 1)
        record = result["files"][0]
        self.assertEqual(record["coverage_status"], "calendar_date_only")
        self.assertIsNone(record["available_at"])
        self.assertIsNone(record["event_start_ns"])
        self.assertTrue(record["date_only"])
        self.assertEqual(record["date_min"], "2020-01-02")
        self.assertEqual(record["date_max"], "2021-12-31")
        self.assertEqual(record["calendar_start_ns"], 1577923200000000000)
        self.assertEqual(record["calendar_end_ns"], 1640995200000000000)
        reasons = {hole["reason"] for hole in record["coverage_holes"]}
        self.assertTrue({
            "date_only_observation_no_intraday_time",
            "publication_time_unknown",
            "vintage_or_revision_time_unknown",
        } <= reasons)
        self.assertEqual(set(result["years"]), {"2020", "2021"})
        self.assertEqual(result["years"]["2020"]["coverage_basis"], "calendar_date")
        self.assertEqual(result["actual_date_span"]["basis"], "calendar_date_bounds")

    def test_bls_date_and_et_clock_is_scheduled_calendar_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources" / "bls__release-calendars" / "release.csv"
            _write_csv(path, ["reference_month", "date", "time_et", "status"], [
                {"reference_month": "December 2023", "date": "2024-01-05", "time_et": "08:30", "status": "scheduled"},
                {"reference_month": "November 2024", "date": "2024-12-06", "time_et": "08:30", "status": "scheduled"},
            ])
            result = inventory_acquired(root, method_id="STOIC-DATA")

        record = result["files"][0]
        self.assertIsNone(record["event_start_ns"])
        self.assertEqual(record["calendar_start_ns"], 1704412800000000000)
        self.assertEqual(record["scheduled_start_ns"], et_ns(date(2024, 1, 5), 8, 30))
        self.assertEqual(record["scheduled_end_ns"], et_ns(date(2024, 12, 6), 8, 30) + 1)
        self.assertIsNone(record["available_at"])
        self.assertEqual(record["coverage_status"], "scheduled_calendar_only")
        self.assertIsNone(record["coverage_valid"])
        self.assertFalse(record["date_only"])
        reasons = {hole["reason"] for hole in record["coverage_holes"]}
        self.assertIn("scheduled_calendar_is_not_actual_release", reasons)
        self.assertIn("released_value_or_vintage_unavailable", reasons)
        self.assertEqual(result["years"]["2024"]["coverage_statuses"], ["scheduled_calendar_only"])

    def test_typed_ns_parquet_keeps_exact_event_and_reference_bounds(self):
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
        except ImportError:
            self.skipTest("optional data dependencies are absent")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "free-sources" / "futures-options" / "events.parquet"
            path.parent.mkdir(parents=True)
            first = 1_700_000_000_123_456_789
            second = first + 987_654_321
            table = pa.table({
                "event_ts_utc": pa.array([first, second], type=pa.timestamp("ns", tz="UTC")),
                "reference_date": pa.array([date(2024, 1, 2), date(2024, 1, 3)], type=pa.date32()),
                "value": [1.0, 2.0],
            })
            pq.write_table(table, path, row_group_size=2)
            record = _inspect_file(root, path, dataset_id="free-sources/futures-options")

        self.assertEqual(record["event_start_ns"], first)
        self.assertEqual(record["event_end_ns"], second + 1)
        self.assertEqual(record["reference_start_ns"], 1704153600000000000)
        self.assertEqual(record["reference_end_ns"], 1704326400000000000)
        self.assertEqual(record["available_at"], None)
        self.assertEqual(record["coverage_status"], "timed_observations")
        self.assertTrue(record["valid"])

    def test_manifest_and_raw_html_are_provenance_with_explicit_holes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / "free-sources" / "demo" / "MANIFEST.tsv"
            raw_html = root / "free-sources" / "demo" / "calendar.html"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("archive_path\tdataset_id\n")
            raw_html.write_text("<html><body>calendar</body></html>")
            manifest_record = _inspect_file(root, manifest, dataset_id="free-sources/demo")
            html_record = _inspect_file(root, raw_html, dataset_id="free-sources/demo")

        self.assertEqual(manifest_record["artifact_role"], "manifest")
        self.assertEqual(manifest_record["coverage_status"], "provenance_only")
        self.assertFalse(manifest_record["coverage_valid"])
        self.assertEqual(html_record["artifact_role"], "raw_provenance")
        self.assertEqual(html_record["coverage_status"], "provenance_only")
        self.assertFalse(html_record["coverage_valid"])
        for record in (manifest_record, html_record):
            reasons = {hole["reason"] for hole in record["coverage_holes"]}
            self.assertIn("provenance_artifact_not_observation_data", reasons)
            self.assertTrue(any("parser" in reason for reason in reasons))
            self.assertTrue(any("datafields" in reason for reason in reasons))

    def test_stoic_data_filter_uses_only_the_supplied_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_csv(root / "free-sources" / "daily" / "a.csv", ["date", "value"], [
                {"date": "2024-01-02", "value": "1"},
            ])
            # This valid tape-shaped file would be included by the broad
            # inventory, but STOIC-DATA owns free-source context only.
            _write_csv(root / "quantpad" / "cme__nq-continuous-futures__ohlcv-1m" / "a.csv",
                       ["t", "o", "h", "l", "c", "v"], [{
                           "t": "1704196800000", "o": "1", "h": "1", "l": "1", "c": "1", "v": "1",
                       }])
            result = inventory_acquired(root, method_id="STOIC-DATA")

        self.assertEqual(result["relevant_file_count"], 1)
        self.assertTrue(result["files"][0]["archive_path"].startswith("free-sources/"))
        self.assertEqual(result["data_root"], str(root))


if __name__ == "__main__":
    unittest.main()
