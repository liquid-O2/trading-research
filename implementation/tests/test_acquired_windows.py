"""Algorithm tests for the acquired-window audit; no production data reads."""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from audit_acquired_windows import (  # noqa: E402
    MINUTE_NS,
    build_audit,
    coalesce_values,
    expected_labels,
    inspect_completed_recoveries,
    inspect_native_comparison,
    mbp_nominal_inventory_text,
    occupied_minute_keys,
    reject_outputs_within_data_root,
    session_bounds_ns,
    subtract_interval,
    supported_mbp1_gap_conclusion,
    trade_date_et,
)


class AcquiredWindowAuditTests(unittest.TestCase):
    def test_contract_identity_is_part_of_occupied_minute_key(self):
        values_ms = np.array([0, 1_000, 59_000, 59_000, 60_000], dtype=np.int64)
        instruments = np.array([10, 10, 10, 11, 11], dtype=np.int64)
        self.assertEqual(
            occupied_minute_keys(values_ms, instruments),
            {(0, 10), (0, 11), (MINUTE_NS, 11)},
        )

    def test_nominal_label_enumeration_crosses_years(self):
        self.assertEqual(
            expected_labels("monthly", "2020-11", "2021-02"),
            ["2020-11", "2020-12", "2021-01", "2021-02"],
        )
        self.assertEqual(
            expected_labels("weekly", "2024-12-30", "2025-01-13"),
            ["2024-12-30", "2025-01-06", "2025-01-13"],
        )

    def test_interval_subtraction_does_not_manufacture_coverage(self):
        self.assertEqual(
            subtract_interval((0, 100), [(10, 20), (40, 90)]),
            [(0, 10), (20, 40), (90, 100)],
        )
        self.assertEqual(
            coalesce_values([0, MINUTE_NS, 3 * MINUTE_NS], MINUTE_NS),
            [(0, MINUTE_NS, 2), (3 * MINUTE_NS, 3 * MINUTE_NS, 1)],
        )

    def test_globex_trade_date_uses_et_and_retains_dst_duration(self):
        day = date(2026, 3, 9)
        start, end = session_bounds_ns(day)
        self.assertEqual((end - start) // MINUTE_NS, 1_380)
        self.assertEqual(trade_date_et(start), day)
        self.assertEqual(trade_date_et(end - 1), day)

    def test_optional_external_evidence_is_not_invented(self):
        self.assertEqual(inspect_native_comparison(None)["status"], "not_checked")
        recoveries = inspect_completed_recoveries(None, None)
        self.assertTrue(
            all(row["status"] == "not_checked" for row in recoveries.values())
        )

    def test_comparison_counts_come_from_supplied_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "manifest.json").write_text(
                json.dumps(
                    {
                        "plan": {"start_ns": 1, "end_ns": 2},
                        "artifacts": {"trades": {"rows": 7}},
                    }
                )
            )
            comparison = {
                "equal_fields": 3,
                "unresolved_fields": [{"field": "O", "instrument_id": 42}],
                "mismatches": [{"field": "V", "instrument_id": 42}],
                "start_ms": 1_000,
                "end_ms_exclusive": 2_000,
            }
            (root / "native-bar-comparison.json").write_text(json.dumps(comparison))
            (root / "native-second-comparison.json").write_text(json.dumps(comparison))
            result = inspect_native_comparison(root)
        self.assertEqual(result["status"], "checked")
        self.assertEqual(result["derived_from_mbp1"]["trades"], 7)
        self.assertEqual(result["native_one_minute_fields_equal"], 3)
        self.assertEqual(result["native_one_minute_fields_compared"], 5)
        self.assertEqual(result["instrument_ids_in_comparison"], [42])

    def test_outputs_inside_data_root_are_rejected_before_audit_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_root = root / "data"
            data_root.mkdir()
            inside = data_root / "reports"
            outside = root / "outside"
            with self.assertRaisesRegex(ValueError, "outside --data-root"):
                build_audit(data_root, inside / "rows.json", outside / "keys.json")
            self.assertFalse(inside.exists())

            link = root / "linked-data"
            link.symlink_to(data_root, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "outside --data-root"):
                reject_outputs_within_data_root(
                    data_root, (link / "coverage-audit.json",)
                )

    def test_fake_audit_with_contradictions_cannot_render_a_no_gap_conclusion(self):
        mbp = {
            "empty_files": ["2025-02.parquet"],
            "row_groups_missing_t_statistics": 2,
        }
        ownership = {
            "monthly_track": {
                "status": "present",
                "file_count": 2,
                "first_label": "2025-01",
                "last_label": "2025-03",
                "missing_between_physical_endpoints": ["2025-02"],
                "empty_files": ["2025-02.parquet"],
            },
            "weekly_track": {
                "status": "present",
                "file_count": 1,
                "first_label": "2025-01-06",
                "last_label": "2025-01-06",
                "missing_between_physical_endpoints": [],
                "empty_files": ["2025-01-06.parquet"],
            },
        }
        sessions = {
            "nq_1m_session_count_within_mbp1_endpoint_bounds": 2,
            "one_minute_sessions_without_mbp1_row_group_endpoint": ["2025-02-03"],
        }
        envelope = {
            "monthly_primary_row_group_count": 1,
            "gaps_containing_a_complete_existing_1m_bar": [{"start_ns": 1}],
        }
        fake_audit = {
            "nq": {
                "datasets": {"nq_mbp1": mbp},
                "mbp1_ownership": ownership,
                "session_presence": sessions,
                "mbp1_row_group_envelope_check": envelope,
            }
        }
        conclusion = supported_mbp1_gap_conclusion(
            fake_audit["nq"]["datasets"]["nq_mbp1"],
            fake_audit["nq"]["mbp1_ownership"],
            fake_audit["nq"]["session_presence"],
            fake_audit["nq"]["mbp1_row_group_envelope_check"],
        )
        inventory = mbp_nominal_inventory_text(
            fake_audit["nq"]["datasets"]["nq_mbp1"],
            fake_audit["nq"]["mbp1_ownership"],
        )
        self.assertIn("Missing nominal NQ MBP-1 month labels", conclusion)
        self.assertIn("1 MBP-1 file(s) are empty", conclusion)
        self.assertIn("remain unverified", conclusion)
        self.assertIn("1 gap(s)", conclusion)
        self.assertNotIn("No nominal NQ MBP-1 month", conclusion)
        self.assertIn("missing labels", inventory)
        self.assertIn("empty files", inventory)


if __name__ == "__main__":
    unittest.main()
