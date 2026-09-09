"""Mass-conserving research views of the exact sparse event profile.

These are pure calculations over admitted cells. The study worker binds their
input coordinates, coverage and source manifests. They do not fabricate the
legacy capture objects used by the retained live measurement interfaces.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction
from typing import NamedTuple

from trading_research.errors import ContractError, IntegrityError
from trading_research.measurements.footprint import imbalance_rows, stacked_imbalances
from trading_research.measurements.profiles import (
    FrozenGrid, ProfileCell, ProfileDefinition, _transport, _validate_mass_rows,
    profile_geometry_rows, side_geometry_rows, transform_profile_rows,
)


VERSION = "auction-flow-exact-mass-views-v1"


class SideCell(NamedTuple):
    price: int
    buy: Fraction
    sell: Fraction
    unknown: Fraction


@dataclass(frozen=True)
class MassView:
    coordinate_identity: str
    grid: FrozenGrid
    rows: tuple
    low_overflow: tuple
    high_overflow: tuple
    unpriced: tuple
    coverage_complete: bool
    representation: tuple

    def __post_init__(self):
        if (type(self.coordinate_identity) is not str or not self.coordinate_identity
                or type(self.coverage_complete) is not bool or type(self.representation) is not tuple
                or not self.representation or len(self.representation) > 32):
            raise ContractError("mass view needs an explicit raw coordinate, coverage and representation")
        normalized = _validate_mass_rows(self.rows, grid=self.grid)
        object.__setattr__(self, "rows", normalized)
        for name in ("low_overflow", "high_overflow", "unpriced"):
            values = getattr(self, name)
            if (type(values) is not tuple or len(values) != 3
                    or any(type(v) not in (int, Fraction) or v < 0 for v in values)):
                raise ContractError("side-separated overflow and unpriced mass must be exact and nonnegative")
            object.__setattr__(self, name, tuple(map(Fraction, values)))

    @property
    def total_mass(self):
        return sum(r.mass for r in self.rows) + sum(self.low_overflow + self.high_overflow + self.unpriced)

    def record(self):
        return {"version": VERSION, **{name: getattr(self, name) for name in self.__dataclass_fields__},
                "total_mass": self.total_mass, "normalization_scope": "retained in-grid nonnegative mass",
                "source_eligibility": "separately bound by the registered study worker"}


def view_sparse(profile, *, coordinate_identity, grid, coverage_complete):
    """Rebin exact original cells only when target boundaries preserve them."""
    from trading_research.research.auction_flow_measurements import SparseSideMass

    if type(profile) is not SparseSideMass or type(grid) is not FrozenGrid:
        raise ContractError("exact retained sparse mass and fixed target grid required")
    grid.__post_init__()
    if (grid.width_ticks % profile.row_ticks
            or (grid.origin_ticks - profile.origin_ticks) % profile.row_ticks):
        raise ContractError("a coarse cell cannot be split or shifted into unobserved finer prices")
    record = profile.record(coverage_complete=coverage_complete)
    cells = {row: [0, 0, 0] for row in range(grid.lower_row, grid.upper_row + 1)}
    low, high = [0, 0, 0], [0, 0, 0]
    for row, buy, sell, unknown in record["rows"]:
        at = grid.row(profile.origin_ticks + row * profile.row_ticks)
        target = low if at < grid.lower_row else high if at > grid.upper_row else cells[at]
        for i, mass in enumerate((buy, sell, unknown)):
            target[i] += mass
    result = MassView(coordinate_identity, grid, tuple(ProfileCell(row, *mass) for row, mass in cells.items()),
        tuple(low), tuple(high), record["unpriced_buy_sell_unknown"], coverage_complete,
        (("original_sparse_grid", profile.row_ticks, profile.origin_ticks), ("target_grid", grid.width_ticks, grid.origin_ticks)))
    if result.total_mass != record["total_volume"]:
        raise IntegrityError("rebinned profile lost original or overflow trade mass")
    return result


def transform_mass(view, *, kind, scale):
    """Literal triangular redistribution or nested coarsening, retaining tails."""
    if type(view) is not MassView or kind not in ("coarsen", "triangular") or type(scale) is not int or not 1 <= scale <= 32:
        raise ContractError("bounded supported mass transformation required")
    view.__post_init__()
    grid, rows, low, high, _ = transform_profile_rows(view.rows, grid=view.grid,
        low_overflow=view.low_overflow, high_overflow=view.high_overflow, kind=kind, scale=scale)
    result = replace(view, grid=grid, rows=rows,
                     low_overflow=low, high_overflow=high, representation=view.representation + ((kind, scale),))
    if result.total_mass != view.total_mass:
        raise IntegrityError("profile transformation does not conserve all three side channels")
    for channel in ("buy", "sell", "unknown"):
        i = ("buy", "sell", "unknown").index(channel)
        def mass(v):
            return sum(getattr(r, channel) for r in v.rows) + v.low_overflow[i] + v.high_overflow[i] + v.unpriced[i]
        if mass(result) != mass(view):
            raise IntegrityError("profile transformation changed a side partition")
    return result


def geometry(view, *, definition=ProfileDefinition("auction-flow-value-70-v1")):
    if type(view) is not MassView:
        raise ContractError("retained exact mass view required")
    view.__post_init__()
    return {**profile_geometry_rows(view.rows, grid=view.grid, definition=definition),
            "low_overflow": view.low_overflow, "high_overflow": view.high_overflow,
            "unpriced": view.unpriced, "coverage_complete": view.coverage_complete,
            "definition": definition, "normalization_scope": "in-grid mass; overflow and unpriced channels retained separately"}


def side_geometry(view, *, pseudo_mass=Fraction(0)):
    if type(view) is not MassView:
        raise ContractError("retained exact side mass required")
    view.__post_init__()
    return {**side_geometry_rows(view.rows, grid=view.grid,
        history_complete=view.coverage_complete and not sum(view.unpriced), pseudo_mass=pseudo_mass),
        "unpriced": view.unpriced, "low_overflow": view.low_overflow, "high_overflow": view.high_overflow,
        "normalization_scope": "separately normalized observed buy and sell in-grid mass; signed delta is not a probability"}


def footprint_geometry(view, *, ratio, minimum_volume, comparison, zero_opponent, minimum_stack_rows):
    if type(view) is not MassView:
        raise ContractError("retained exact footprint cells required")
    view.__post_init__()
    # The literal footprint kernel consumes structural side cells, not a
    # fabricated trade-ID list or a source-eligibility certificate.
    cells = tuple(SideCell(view.grid.origin_ticks + r.row * view.grid.width_ticks, r.buy, r.sell, r.unknown)
                  for r in view.rows if r.mass)
    result = imbalance_rows({"rows": cells, "row_ticks": view.grid.width_ticks}, ratio=ratio,
        minimum_volume=minimum_volume, comparison=comparison, zero_opponent=zero_opponent)
    return {"rows": result, "buy_stacks": stacked_imbalances(result, side="buy", row_ticks=view.grid.width_ticks,
            minimum_rows=minimum_stack_rows), "sell_stacks": stacked_imbalances(result, side="sell", row_ticks=view.grid.width_ticks,
            minimum_rows=minimum_stack_rows), "unpriced": view.unpriced,
            "geometry_history_complete": view.coverage_complete and not sum(view.unpriced),
            "ratio": ratio, "minimum_volume": minimum_volume, "comparison": comparison,
            "zero_opponent": zero_opponent, "minimum_stack_rows": minimum_stack_rows}


def shape_distance(a, b):
    if type(a) is not MassView or type(b) is not MassView:
        raise ContractError("two retained nonnegative mass views required")
    a.__post_init__()
    b.__post_init__()
    if a.coordinate_identity != b.coordinate_identity or a.grid != b.grid:
        raise ContractError("cumulative-mass distance requires the same raw contract and frozen grid")
    if (not a.coverage_complete or not b.coverage_complete
            or any(sum(v) for p in (a, b) for v in (p.low_overflow, p.high_overflow, p.unpriced))):
        return None
    return _transport(tuple(r.mass for r in a.rows), tuple(r.mass for r in b.rows), a.grid.width_ticks)
