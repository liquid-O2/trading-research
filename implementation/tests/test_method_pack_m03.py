"""Manifest and object coverage checks for the GB-VWAP slice."""

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
from trading_research.research.method_pack.method_slices.m03 import (
    STAGE_LIMITS,
    _positive_case,
    method_fixtures,
)
from trading_research.research.method_pack.objects import run_object_fixtures


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "implementation/tools/run_phase1_objects.py"


class MethodPackM03Tests(unittest.TestCase):
    def test_bound_method_rows_cover_fixtures_and_c08(self):
        rows = {row["id"]: row for row in method_fixtures()}
        expected = {
            "M03-F1": "pass",
            "M03-F2-close": "fail",
            "M03-F2-order": "fail",
            "M03-F2-side": "fail",
            "M03-F2-later-gain": "pass",
            "M03-F3-reset": "unknown",
            "M03-F1:c08-late": "fail",
            "M03-F1:c08-identity": "fail",
            "M03-F1:c08-missing": "unknown",
        }
        self.assertTrue(set(expected).issubset(rows))
        self.assertTrue(all(rows[fid]["status"] == "pass" for fid in expected))
        self.assertEqual(
            {fid: rows[fid]["actual_value"]["verdict"] for fid in expected},
            expected,
        )
        self.assertEqual(rows["M03-F1"]["actual_value"]["side"], "long")
        self.assertEqual(rows["M03-F1"]["actual_value"]["sequence_ok"], True)
        self.assertEqual(rows["M03-F3-reset"]["actual_value"]["verdict"], "unknown")
        self.assertEqual(rows["M03-F2-later-gain"]["actual_value"]["verdict"], "pass")

    def test_stage_caps_bind_to_consuming_events(self):
        positive = next(row for row in method_fixtures() if row['id'] == 'M03-F1')
        operands = positive['actual_value']['operands']
        self.assertEqual(operands['london_high']['known_at'], _positive_case()['london_known_at'])
        self.assertEqual(operands['asia_high']['known_at'], _positive_case()['asia_known_at'])
        self.assertLess(operands['vwap_at_retest']['known_at'], _positive_case()['retest_at'])
        document = fixture_document('GB-VWAP', 'sequence', 'late-price', _positive_case())
        obj = next(o for o in document['objects'] if o['object_id'].endswith(':vwap_at_retest'))
        obj['known_at'] = _positive_case()['retest_at']
        parsed = parse_manifest(document, 'GB-VWAP')
        self.assertEqual(score_episode(parsed[0]['late-price'], *parsed[1:])['verdict'], 'fail')

    def test_manifest_mutations_use_real_records(self):
        op = _positive_case()
        document = fixture_document("GB-VWAP", "sequence", "episode", op)
        parsed = parse_manifest(document, "GB-VWAP")
        self.assertEqual(score_episode(parsed[0]["episode"], *parsed[1:])["verdict"], "pass")

        late = json.loads(json.dumps(document))
        late_object = next(
            row for row in late["objects"]
            if row["object_id"].endswith(":vwap_known_at")
        )
        late_at = op["retest_at"] + 1
        late_object.update({
            "known_at": late_at,
            "as_of": late_at,
            "formation_start": late_at,
            "formation_end": late_at,
        })
        for evidence in late["evidence"]:
            if evidence["evidence_id"] in late_object["evidence_ids"]:
                evidence.update({
                    "known_at": late_at,
                    "observation_start": late_at,
                    "observation_end": late_at,
                })
        parsed = parse_manifest(late, "GB-VWAP")
        late_result = score_episode(parsed[0]["episode"], *parsed[1:])
        self.assertEqual(late_result["verdict"], "fail")
        self.assertGreater(late_result["detected_causal_violations"], 0)

        identity = json.loads(json.dumps(document))
        identity_object = next(
            row for row in identity["objects"]
            if row["object_id"].endswith(":london_high")
        )
        identity_object["band_id"] = "foreign-band"
        parsed = parse_manifest(identity, "GB-VWAP")
        identity_result = score_episode(parsed[0]["episode"], *parsed[1:])
        self.assertEqual(identity_result["verdict"], "fail")
        self.assertTrue(any(hole["kind"] == "identity" for hole in identity_result["holes"]))

        missing = json.loads(json.dumps(document))
        missing["candidates"][0]["operands"].pop("vwap_reset_verified")
        parsed = parse_manifest(missing, "GB-VWAP")
        missing_result = score_episode(parsed[0]["episode"], *parsed[1:])
        self.assertEqual(missing_result["verdict"], "unknown")
        self.assertIn("HOLE:O030:vwap_reset_verified", missing_result["hole_ids"])

    def test_all_m03_objects_have_printed_and_c08_rows(self):
        rows = run_object_fixtures(objects_for("GB-VWAP"))
        self.assertTrue(rows)
        self.assertTrue(all(row["status"] == "pass" for row in rows),
                        [row for row in rows if row["status"] != "pass"])
        for object_id in objects_for("GB-VWAP"):
            self.assertTrue(any(row["id"] == f"{object_id}-F1" for row in rows), object_id)
            for mutation in ("c08_late", "c08_missing", "c08_identity"):
                self.assertTrue(
                    any(row["recipe"] == object_id and row["kind"] == mutation for row in rows),
                    (object_id, mutation),
                )

    def test_empty_acquired_pass_separates_implementation_checks_and_discovery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = root / "data"
            reports = root / "reports"
            data.mkdir()
            run = subprocess.run([
                sys.executable, str(RUNNER), "method-pass", "--method", "GB-VWAP",
                "--scope", "acquired", "--data-root", str(data),
                "--report-root", str(reports),
            ], cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads((reports / "gb-vwap.json").read_text())
            self.assertEqual(report["status"], "checks_passed")
            self.assertEqual(report["summary"]["N"], 0)
            self.assertEqual(len(report["branches"]), 1)
            self.assertIn("source_long", report["branches"])
            self.assertEqual(report["quality"]["fixture_failures"], 0)


if __name__ == "__main__":
    unittest.main()
