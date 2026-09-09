from dataclasses import replace
from fractions import Fraction as F
import unittest

import numpy as np

from references import auction_measurements_literal as literal
from trading_research.errors import ContractError
from trading_research.measurements.profiles import FrozenGrid, ProfileDefinition, bar_allocation_rows, profile_geometry, transform_profile
from trading_research.research.auction_flow_measurements import SparseSideMass
from trading_research.research.auction_flow_profiles import (
    footprint_geometry, geometry, shape_distance, side_geometry, transform_mass, view_sparse,
)
from tests.measurement_sources import Sources


class AuctionFlowProfileTests(unittest.TestCase):
    def test_factored_bar_allocation_retains_literal_body_wicks_and_source_flat_loss(self):
        grid = FrozenGrid(0, 1, 100, 104, 'observed-bar-geometry', 0)
        bar = ((101, 104, 100, 103, 100, 7),)
        # Body length 2, both wick lengths 1: denominator 6. Each body
        # tick gets 100/6 buy; each wick tick gets 100/6 per side.
        rows = bar_allocation_rows(bar, grid=grid, variant='pin066_source')
        self.assertEqual(tuple((r.row, r.buy, r.sell, r.unknown) for r in rows['rows']),
            ((100, F(50, 3), F(50, 3), 0), (101, F(50, 3), 0, 0),
             (102, F(50, 3), 0, 0), (103, F(50, 3), F(50, 3), 0), (104, 0, 0, 0)))
        self.assertEqual(rows['unpriced'], (0, 0, 7))
        equal = bar_allocation_rows(bar, grid=grid, variant='equal_inclusive_rows')
        self.assertEqual(tuple(r.mass for r in equal['rows']), (20, 20, 20, 20, 20))
        continuous = bar_allocation_rows(bar, grid=grid, variant='continuous_overlap')
        self.assertEqual(tuple(r.mass for r in continuous['rows']), (25, 25, 25, 25, 0))
        flat = ((102, 102, 102, 102, 11, 0),)
        self.assertEqual(bar_allocation_rows(flat, grid=grid, variant='pin066_source')['source_flat_bar_lost_mass'], 11)
        corrected = bar_allocation_rows(flat, grid=grid, variant='pin066_corrected')
        self.assertEqual((corrected['rows'][2].mass, corrected['source_flat_bar_lost_mass']), (11, 0))

    def sparse(self, trades, *, width=1, origin=0):
        result = SparseSideMass(row_ticks=width, origin_ticks=origin)
        result.add(price_ticks=np.array([p or 0 for p, _, _ in trades], dtype=np.int64),
            price_valid=np.array([p is not None for p, _, _ in trades], dtype=np.uint8),
            size=np.array([q for _, q, _ in trades], dtype=np.int64),
            side=np.array([s or 0 for _, _, s in trades], dtype=np.int64))
        return result

    def view(self, trades, *, grid=None, complete=True):
        grid = grid or FrozenGrid(100, 1, 0, 4, "frozen-grid", 0)
        return view_sparse(self.sparse(trades), coordinate_identity="NQH0:raw-coordinate",
                           grid=grid, coverage_complete=complete)

    def test_all_poc_and_expansion_conventions_match_independent_mass_equations(self):
        for mass in ([5, 0, 5], [5, 5, 1], [9, 1, 0], [0, 0, 0]):
            for fraction in (F(68, 100), F(7, 10)):
                for poc_tie in ("lower", "upper"):
                    for value_tie in ("lower", "upper", "both"):
                        for stop in (False, True):
                            with self.subTest(mass=mass, fraction=fraction, poc_tie=poc_tie, value_tie=value_tie, stop=stop):
                                definition = ProfileDefinition("literal-values", value_fraction=fraction,
                                    poc_tie=poc_tie, value_tie=value_tie, gap_policy="stop_empty" if stop else "cross")
                                grid = FrozenGrid(100, 1, 0, 2, "fixed", 0)
                                view = self.view([(100 + i, q, 1) for i, q in enumerate(mass) if q], grid=grid)
                                result = geometry(view, definition=definition)
                                expected = literal.value_area(mass, fraction, poc_tie=poc_tie, value_tie=value_tie, stop_empty=stop)
                                self.assertEqual((result["poc_set"], result["scalar_poc"], result["value_rows"], result["achieved_mass"]), expected)
                                self.assertEqual(result["requested_mass"], sum(mass) * fraction)

    def test_grid_phase_unpriced_and_side_overflow_reconcile_with_original_trade_inputs(self):
        trades = [(99, 2, 1), (100, 3, -1), (101, 5, None), (102, 7, 1), (None, 11, -1)]
        for origin in (100, 101):
            grid = FrozenGrid(origin, 2, 0, 0, "phase:" + str(origin), 0)
            view = self.view(trades, grid=grid)
            rows, overflow = literal.mass_profile(trades, origin, 2, 0, 0)
            self.assertEqual(tuple((r.row, r.buy, r.sell, r.unknown) for r in view.rows), rows)
            self.assertEqual((sum(view.low_overflow), sum(view.high_overflow), sum(view.unpriced)), overflow)
            self.assertEqual(view.total_mass, 28)
            self.assertIsNone(shape_distance(view, view))
            self.assertTrue(all(row["true_bounds"] is None for row in side_geometry(view)["rows"]))
        original = self.sparse([(100, 2, 1), (101, 3, -1)], width=2)
        with self.assertRaises(ContractError):
            view_sparse(original, coordinate_identity="NQH0", grid=FrozenGrid(100, 1, 0, 2, "finer", 0), coverage_complete=True)

    def test_smoothing_retains_each_side_and_boundary_mass_and_coarsening_is_exact(self):
        view = self.view([(100, 8, 1), (101, 4, -1), (102, 12, None)],
                         grid=FrozenGrid(100, 1, 0, 2, "fixed", 0))
        smoothed = transform_mass(view, kind="triangular", scale=1)
        for channel in ("buy", "sell", "unknown"):
            self.assertEqual(tuple(getattr(r, channel) for r in smoothed.rows),
                             literal.smooth([getattr(r, channel) for r in view.rows]))
        self.assertEqual(smoothed.low_overflow, (2, 0, 0))
        self.assertEqual(smoothed.high_overflow, (0, 0, 3))
        self.assertEqual((view.total_mass, smoothed.total_mass), (24, 24))
        coarse = transform_mass(self.view([(100 + i, i + 1, 1) for i in range(4)]), kind="coarsen", scale=2)
        self.assertEqual(tuple(r.mass for r in coarse.rows), (3, 7, 0))

    def test_actual_legacy_source_producer_and_event_mass_adapter_share_full_geometry(self):
        source = Sources(self)
        trades = [(100, 10, 1), (101, 3, -1), (102, 5, 1), (103, 4, None)]
        grid = FrozenGrid(100, 1, 0, 4, "literal-full", -100)
        original, *_ = source.profile(trades, grid=grid)
        view = self.view(trades, grid=grid)
        result = geometry(view)
        for key, value in profile_geometry(original).items():
            self.assertEqual(result[key], value, key)
        peak = next(p for p in result["local_peaks"] if p["rows"] == (2, 2))
        self.assertEqual((peak["height"], peak["prominence"]), (5, 2))
        smoothed = transform_mass(view, kind="triangular", scale=2)
        old_smoothed = transform_profile(original, kind="triangular", scale=2)
        self.assertEqual((smoothed.rows, smoothed.low_overflow, smoothed.high_overflow),
                         (old_smoothed.rows, old_smoothed.low_overflow, old_smoothed.high_overflow))

    def test_side_normalization_and_transport_do_not_treat_delta_as_probability(self):
        grid = FrozenGrid(100, 1, 0, 1, "fixed", 0)
        a = self.view([(100, 10, 1), (101, 10, -1)], grid=grid)
        b = self.view([(100, 20, 1), (101, 20, -1)], grid=grid)
        c = self.view([(101, 20, 1)], grid=grid)
        sides = side_geometry(a)
        self.assertEqual((sides["cdf_buy"], sides["cdf_sell"], sides["overlap"], sides["total_variation"], sides["wasserstein_ticks"]),
                         ((1, 1), (0, 1), 0, 1, 1))
        self.assertEqual(tuple(row["cumulative_signed"] for row in sides["rows"]), (10, 0))
        self.assertEqual(shape_distance(a, b), 0)
        self.assertEqual(shape_distance(a, c), literal.transport([10, 10], [0, 20]))
        with self.assertRaises(ContractError):
            shape_distance(a, replace(b, coordinate_identity="NQM0:another-contract"))
        self.assertIsNone(shape_distance(a, replace(b, coverage_complete=False)))
        self.assertIsNone(shape_distance(a, self.view([], grid=grid)))

    def test_footprint_unknown_opponents_and_missing_physical_rows_break_stacks(self):
        grid = FrozenGrid(100, 2, 0, 3, "two-tick", 0)
        view = self.view([(100, 10, 1), (102, 10, 1), (106, 10, 1)], grid=grid)
        args = dict(ratio=F(3), minimum_volume=1, comparison="same_price",
                    zero_opponent="infinite_if_minimum", minimum_stack_rows=2)
        result = footprint_geometry(view, **args)
        self.assertEqual(result["buy_stacks"], ((100, 102),))
        unknown = self.view([(100, 10, 1), (102, 10, 1), (102, 5, None), (106, 10, 1)], grid=grid)
        result = footprint_geometry(unknown, **args)
        row = next(r for r in result["rows"] if r["price"] == 102)
        self.assertEqual(row["buy"]["ratio_lower_bound"], 2)
        self.assertFalse(row["buy"]["qualifying"])
        self.assertEqual(result["buy_stacks"], ())


if __name__ == "__main__":
    unittest.main()
