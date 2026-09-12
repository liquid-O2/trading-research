"""Bound fixture and object coverage checks for the GB-FAIL slice."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from trading_research.research.method_pack.catalog import objects_for
from trading_research.research.method_pack.evidence import (
    fixture_document,
    parse_manifest,
    score_episode,
)
from trading_research.research.method_pack.method_slices.m02 import (
    STAGE_LIMITS,
    _positive_case,
    method_fixtures,
)
from trading_research.research.method_pack.objects import run_object_fixtures
from trading_research.research.method_pack.protocol import jsonable


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "implementation/tools/run_phase1_objects.py"


class MethodPackM02Tests(unittest.TestCase):
    def test_bound_method_rows_cover_positive_negatives_and_named_holes(self):
        rows = {row["id"]: row for row in method_fixtures()}
        expected = {
            "M02-F1": "pass",
            "M02-F2-box-unavailable": "fail",
            "M02-F2-close-outside": "fail",
            "M02-F2-pocket-no-fail": "fail",
            "M02-F2-grouped-rows": "fail",
            "M02-F3-hold": "unknown",
            "M02-F3-london-clock": "unknown",
            "M02-F3-prior-period-scope": "unknown",
            "M02-F3-stop-policy": "unknown",
        }
        self.assertTrue(set(expected).issubset(rows))
        self.assertTrue(all(rows[fid]["status"] == "pass" for fid in expected))
        self.assertEqual({fid: rows[fid]["actual_value"]["verdict"] for fid in expected}, expected)
        self.assertEqual(rows["M02-F1"]["actual_value"]["verdict"], "pass")
        self.assertTrue(rows["M02-F1"]["inputs"]["candidates"])
        self.assertEqual(rows["M02-F1"]["evidence_mode"], "synthetic_fixture")
        self.assertIn("source_hold_confirmed", rows["M02-F3-hold"]["actual_value"]["hole_ids"][-1])

    def test_availability_caps_bind_to_actual_stage(self):
        self.assertEqual(STAGE_LIMITS["reference_frozen"], "reference_known_at")
        self.assertEqual(STAGE_LIMITS["bias_recorded"], "context_at")
        self.assertEqual(STAGE_LIMITS["sweep_high"], "sweep_at")
        self.assertEqual(STAGE_LIMITS["confirm_close"], "confirm_at")
        self.assertEqual(STAGE_LIMITS["box_return_ok"], "confirm_at")
        self.assertEqual(STAGE_LIMITS["risk_defined"], "decision_at")

    def test_manifest_mutations_use_real_records(self):
        op = _positive_case()
        doc = fixture_document("GB-FAIL", "sequence", "episode", op)

        parsed = parse_manifest(doc, "GB-FAIL")
        self.assertEqual(score_episode(parsed[0]["episode"], *parsed[1:])["verdict"], "pass")

        # Identity is changed on the actual producer record, with no private
        # mutation flag or nearest-price join involved.
        wrong = json.loads(json.dumps(jsonable(doc)))
        wrong_object = next(o for o in wrong["objects"] if o["object_id"].endswith(":reference_px"))
        wrong_object["band_id"] = "foreign-band"
        parsed = parse_manifest(wrong, "GB-FAIL")
        result = score_episode(parsed[0]["episode"], *parsed[1:])
        self.assertEqual(result["verdict"], "fail")
        self.assertGreater(result["rejected_proxy_attempts"], -1)
        self.assertTrue(any(h["kind"] == "identity" for h in result["holes"]))

        # Availability is changed on the bound source record after its actual
        # consuming stage, which must be a causal failure.
        late = json.loads(json.dumps(jsonable(doc)))
        late_object = next(o for o in late["objects"] if o["object_id"].endswith(":bias_recorded"))
        late_evidence = late["evidence"][0]
        for evidence in late["evidence"]:
            if evidence["evidence_id"] in late_object["evidence_ids"]:
                late_evidence = evidence
                break
        late_at = op["decision_at"] + 1
        late_object.update({"known_at": late_at, "as_of": late_at,
                            "formation_start": late_at, "formation_end": late_at})
        late_evidence.update({"known_at": late_at, "observation_start": late_at,
                              "observation_end": late_at})
        parsed = parse_manifest(late, "GB-FAIL")
        result = score_episode(parsed[0]["episode"], *parsed[1:])
        self.assertEqual(result["verdict"], "fail")
        self.assertGreater(result["detected_causal_violations"], 0)

        missing = json.loads(json.dumps(jsonable(doc)))
        missing["candidates"][0]["operands"].pop("source_session_allowed")
        parsed = parse_manifest(missing, "GB-FAIL")
        result = score_episode(parsed[0]["episode"], *parsed[1:])
        self.assertEqual(result["verdict"], "unknown")
        self.assertIn("HOLE:O046:source_session_allowed", result["hole_ids"])

    def test_all_m02_objects_have_printed_and_c08_rows(self):
        rows = run_object_fixtures(objects_for("GB-FAIL"))
        self.assertTrue(rows)
        self.assertTrue(all(row["status"] == "pass" for row in rows),
                        [row for row in rows if row["status"] != "pass"])
        for object_id in objects_for("GB-FAIL"):
            self.assertTrue(any(row["id"] == f"{object_id}-F1" for row in rows), object_id)
            for mutation in ("c08_late", "c08_missing", "c08_identity"):
                self.assertTrue(any(row["recipe"] == object_id and row["kind"] == mutation for row in rows),
                                (object_id, mutation))

    def test_empty_acquired_pass_reports_all_m02_branches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            run = subprocess.run([
                sys.executable, str(RUNNER), "method-pass", "--method", "GB-FAIL",
                "--scope", "acquired", "--data-root", str(data),
                "--report-root", str(reports),
            ], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads((reports / "gb-fail.json").read_text())
            self.assertEqual(report["status"], "source_hole")
            self.assertEqual(report["summary"]["N"], 0)
            self.assertEqual(len(report["branches"]), 8)
            self.assertEqual(report["quality"]["fixture_failures"], 0)


if __name__ == "__main__":
    unittest.main()
