"""Closed synthetic fixtures for the JJ-TBR sequence predicate."""

from copy import deepcopy
from decimal import Decimal
import unittest

from trading_research.research.method_pack.evidence import parse_manifest, score_episode
from trading_research.research.method_pack.methods import (
    M01_BRANCHES,
    _m01_identity_ok,
    m01_judas_reversal_fixture,
    m01_method_fixtures,
    score_candidate,
)


def _nested_manifest(op):
    """Build the C01 manifest exposed by the fixture helper."""

    return {
        "formula_version": "method-pack-v1",
        "candidates": [op["candidate"]],
        "objects": op["objects"],
        "assertions": op["assertions"],
        "evidence": op["evidence_records"],
    }


class MethodPackM01Tests(unittest.TestCase):
    def test_positive_fixture_has_declared_geometry_and_evidence(self):
        op = m01_judas_reversal_fixture()

        self.assertEqual(op["branch"], "judas_reversal")
        self.assertEqual(op["range_L"], 100)
        self.assertEqual(op["range_H"], 120)
        self.assertLess(op["range_known_at"], op["context_at"])
        self.assertLess(op["context_at"], op["sweep_at"])
        self.assertLess(op["sweep_at"], op["confirm_at"])
        self.assertLess(op["confirm_at"], op["decision_at"])
        self.assertEqual(op["sweep_px"], 121)
        self.assertEqual(op["sweep_depth_w"], Decimal("0.05"))
        self.assertEqual(op["side"], "short")
        self.assertEqual(op["objective_px"], 100)
        self.assertGreater(op["stop_px"], op["rejection_structure_high"])

        # A source interpretation is represented by records, not by a naked
        # Boolean.  The positive fixture must be parseable through the same
        # C01 manifest seam used for supplied episodes.
        parsed = parse_manifest(_nested_manifest(op), "JJ-TBR")
        result = score_episode(parsed[0][op["candidate_id"]], *parsed[1:])
        self.assertEqual(result["verdict"], "pass")
        self.assertIs(result["sequence_ok"], True)
        self.assertIs(result["base_ok"], True)
        self.assertTrue(all(a["evidence_ids"] for a in op["assertions"]))

    def test_naked_boolean_is_unknown(self):
        op = m01_judas_reversal_fixture()
        op.pop("assertions")
        op.pop("operand_bindings")
        op.pop("evidence")

        result = score_candidate("JJ-TBR", "sequence", op)
        self.assertIs(result["sequence_ok"], True)
        self.assertIsNone(result["evidence_ok"])
        self.assertEqual(result["verdict"], "unknown")
        self.assertIn("HOLE:M01:evidence", result["hole_ids"])

    def test_printed_fixture_rows_cover_positive_negative_holes_and_c08(self):
        rows = {row["id"]: row for row in m01_method_fixtures()}

        expected = {
            "M01-F1": "pass",
            "M01-F2-acceptance": "pass",
            "M01-F2-late-context": "pass",
            "M01-F2-identity": "pass",
            "M01-F2-later-target": "pass",
            "M01-F3-confirmation": "pass",
            "M01-F3-pzone": "pass",
            "M01-F3-ev": "pass",
            "M01-F3-session-stat": "pass",
            "M01-F1:c08-late": "pass",
            "M01-F1:c08-missing": "pass",
            "M01-F1:c08-identity": "pass",
        }
        self.assertTrue(set(expected).issubset(rows))
        self.assertTrue(all(rows[fid]["status"] == status for fid, status in expected.items()))
        self.assertEqual(rows["M01-F1"]["actual_value"]["verdict"], "pass")
        self.assertEqual(rows["M01-F2-acceptance"]["actual_value"]["verdict"], "fail")
        self.assertEqual(rows["M01-F2-late-context"]["actual_value"]["verdict"], "fail")
        self.assertEqual(rows["M01-F2-identity"]["actual_value"]["verdict"], "fail")
        self.assertEqual(rows["M01-F3-pzone"]["actual_value"]["verdict"], "unknown")
        self.assertEqual(rows["M01-F3-ev"]["actual_value"]["verdict"], "unknown")
        self.assertEqual(rows["M01-F3-session-stat"]["actual_value"]["verdict"], "unknown")

    def test_projection_parent_identity_is_a_real_join(self):
        op = m01_judas_reversal_fixture()
        self.assertIs(_m01_identity_ok(op), True)

        wrong = deepcopy(op)
        wrong["projection_parent_id"] = "different-range"
        self.assertIs(_m01_identity_ok(wrong), False)
        self.assertEqual(score_candidate("JJ-TBR", "sequence", wrong)["verdict"], "fail")

    def test_branch_inventory_is_exact_and_unsupported_is_unknown(self):
        self.assertEqual(M01_BRANCHES, (
            "judas_outbound",
            "judas_reversal",
            "single_extended",
            "single_purged",
            "internal_rotation",
            "extension_reaction",
            "other_session",
            "timed_pzone_reversal",
        ))
        op = m01_judas_reversal_fixture()
        op["branch"] = "later_path_label"
        result = score_candidate("JJ-TBR", "sequence", op)
        self.assertIsNone(result["sequence_ok"])
        self.assertEqual(result["verdict"], "unknown")
