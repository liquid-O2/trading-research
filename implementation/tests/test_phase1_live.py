"""Ticket 01 fixtures and report contract. Literal expected values."""

from pathlib import Path
import unittest

from trading_research.research.phase1_live.fixtures import run_ticket01_fixtures
from trading_research.research.phase1_live.formulas import formula_fixtures
from trading_research.research.phase1_live.mbp1_objects import mbp1_fixtures
from trading_research.research.phase1_live.grid import outcomes_at_level
from trading_research.research.phase1_live.recipe_score import catalog
from trading_research.research.phase1_live.sessions import projections, width_bin
from trading_research.research.phase1_live.stats import rate_block, wilson


class Phase1LiveFixtureTests(unittest.TestCase):
    def test_ticket01_fixtures(self):
        result = run_ticket01_fixtures()
        failed = [c for g in result["groups"] for c in g["cases"] if not c["pass"]]
        self.assertTrue(result["pass"], failed)

    def test_projections_literals(self):
        got = projections(110.0, 90.0)
        self.assertEqual(got["W"], 20.0)
        self.assertEqual(got["EQ"], 100.0)
        self.assertEqual(got["Q25"], 95.0)
        self.assertEqual(got["Q75"], 105.0)
        self.assertEqual(got["m05_low"], 80.0)
        self.assertEqual(got["ext133_high"], 136.6)
        self.assertAlmostEqual(got["ext166_low"], 56.8)

    def test_width_bins_are_not_mixed(self):
        self.assertEqual(width_bin(0.2), "0-0.3")
        self.assertEqual(width_bin(0.4), "0.3-0.5")
        self.assertEqual(width_bin(1.2), "1.2+")

    def test_wilson_n_zero(self):
        self.assertEqual(wilson(0, 0), (None, None))
        block = rate_block(0, 0)
        self.assertIsNone(block["rate"])

    def test_mbp1_tape_fixtures(self):
        result = mbp1_fixtures()
        failed = [c for g in result["groups"] for c in g["cases"] if not c["pass"]]
        self.assertTrue(result["pass"], failed)

    def test_projection_reject_on_resistance(self):
        import numpy as np
        h = np.array([100.5, 99.0, 92.0, 90.0])
        l = np.array([99.0, 91.0, 89.0, 88.0])
        c = np.array([99.75, 92.0, 90.0, 89.5])
        t = np.array([0, 60_000, 120_000, 180_000])
        got = outcomes_at_level({"n": 4, "h": h, "l": l, "c": c, "t": t}, 100.0, width=20.0, side=1)
        self.assertTrue(got["touch"])
        self.assertTrue(got["reject"])

    def test_formula_fixtures(self):
        result = formula_fixtures()
        failed = [c for g in result["groups"] for c in g["cases"] if not c["pass"]]
        self.assertTrue(result["pass"], failed)

    def test_every_section_b_id_is_catalogued(self):
        ids = [r["id"] for r in catalog()]
        self.assertEqual(len(ids), 105)
        self.assertEqual(ids[0], "R-J01")
        self.assertEqual(ids[-1], "R-P20")
        self.assertEqual(len(set(ids)), 105)


if __name__ == "__main__":
    unittest.main()
