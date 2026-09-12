"""Disposable spec-review checks for the M02 object slice."""

from __future__ import annotations

import unittest

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack import objects as _objects  # noqa: F401
from trading_research.research.method_pack.protocol import run_recipe


DAY = __import__("datetime").date(2026, 1, 15)


def _t(hour: int, minute: int = 0) -> int:
    return et_ns(DAY, hour, minute)


class M02ReviewTests(unittest.TestCase):
    def test_o046_real_member_path_is_reachable_without_fixture_hl(self):
        result = run_recipe("O046", {
            "start_ns": _t(9),
            "end_ns": _t(10),
            "use_at": _t(10, 5),
            "members": [{
                "start_ns": _t(9),
                "end_ns": _t(10),
                "H": 110,
                "L": 100,
                "complete": True,
                "coverage_state": "complete",
            }],
        })
        self.assertEqual(result.state, "computed")
        self.assertTrue(result.value["complete"])

    def test_o049_required_close_cannot_be_missing(self):
        result = run_recipe("O049", {
            "tdo": 100,
            "tdo_required": True,
            "side": "short",
            "known_at": _t(0),
            "use_at": _t(10, 5),
        })
        self.assertEqual(result.state, "hole")
        self.assertIn("HOLE:O049:confirm_close", result.hole_ids)

    def test_o049_required_close_needs_completed_source_bar(self):
        result = run_recipe("O049", {
            "tdo": 100,
            "tdo_required": True,
            "side": "short",
            "confirm_close": 99,
            "complete_clock_five_minute_bar": False,
            "known_at": _t(0),
            "use_at": _t(10, 5),
        })
        self.assertFalse(result.value["source_tdo_close_confirmed"])

    def test_o051_equal_endpoints_are_no_gap(self):
        result = run_recipe("O051", {
            "friday_close": 100,
            "sunday_open": 100,
            "friday_convention": "source-supplied",
        })
        self.assertFalse(result.value["automatic_gap"])

    def test_o051_near_edge_is_contact(self):
        result = run_recipe("O051", {
            "friday_close": 100,
            "sunday_open": 104,
            "friday_convention": "source-supplied",
            "price": 104,
        })
        self.assertTrue(result.value["partial_contact"])
        self.assertFalse(result.value["full_fill"])

    def test_o051_reaching_past_far_edge_is_full_fill(self):
        result = run_recipe("O051", {
            "friday_close": 100,
            "sunday_open": 104,
            "friday_convention": "source-supplied",
            "price": 99,
        })
        self.assertTrue(result.value["full_fill"])

    def test_o054_failure_must_precede_structure_confirmation(self):
        result = run_recipe("O054", {
            "failure_at": _t(10, 5),
            "swing_confirmed_at": _t(10, 5),
            "break_at": _t(10, 7),
            "entry_at": _t(10, 8),
        })
        self.assertFalse(result.base_ok)

    def test_o054_bare_detector_flag_does_not_recover_engine(self):
        result = run_recipe("O054", {
            "failure_at": _t(10, 5),
            "swing_confirmed_at": _t(10, 6),
            "break_at": _t(10, 7),
            "entry_at": _t(10, 8),
            "automatic_detector": True,
        })
        self.assertEqual(result.state, "hole")
        self.assertIsNone(result.value["automatic_mss"])

    def test_o054_can_retain_a_supplied_source_confirmation(self):
        result = run_recipe("O054", {
            "failure_at": _t(10, 5),
            "swing_confirmed_at": _t(10, 6),
            "break_at": _t(10, 7),
            "entry_at": _t(10, 8),
            "structure_reference": "source-swing-108",
            "source_mss_confirmed": True,
        })
        self.assertEqual(result.state, "supplied")
        self.assertTrue(result.value["mss_after_failure"])
        self.assertIsNone(result.value["automatic_mss"])

    def test_o059_bare_automatic_grade_does_not_recover_engine(self):
        result = run_recipe("O059", {
            "necessary_ok": True,
            "automatic_grade": True,
        })
        self.assertEqual(result.state, "hole")
        self.assertIsNone(result.value["grade_ok"])

    def test_o136_bias_needs_side_and_origin_evidence(self):
        result = run_recipe("O136", {
            "bias_at": _t(9, 15),
            "use_at": _t(9, 40),
        })
        self.assertEqual(result.state, "hole")
        self.assertIsNone(result.value.get("bias_recorded"))

    def test_o136_wrong_side_is_witnessed_false(self):
        result = run_recipe("O136", {
            "bias_at": _t(9, 15),
            "use_at": _t(9, 40),
            "direction": "long",
            "candidate_side": "short",
            "origin_reference_id": "PDL-2026-01-14",
        })
        self.assertFalse(result.value["bias_recorded"])
        self.assertFalse(result.base_ok)


if __name__ == "__main__":
    unittest.main()
