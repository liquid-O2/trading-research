"""Exact ordered flow and sparse side mass for bounded event batches.

These adapters preserve the existing literal trade calculators' estimands.
All source filters retain excluded mass. Publication belongs to the caller's
completed covered window; an accumulator alone certifies no data coverage.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction

from trading_research.errors import ContractError, IntegrityError
from trading_research.measurements.cvd import fixed_source_cohort
from trading_research.measurements.tape import value_area
from trading_research.measurements.vwap import weighted_quantile


VERSION = "auction-flow-ordered-measurements-v1"
SOURCE_FILTERS = ("all", "ny_ge100", "london_ge75", "inclusive30_through60")
_TRADE_ARRAYS_ERROR = "bounded equal exact arrays of eligible reported-side trades required"
_VALIDATED_TRADE_TOKEN = object()


class _ValidatedTradeArrays:
    """Owned-or-viewed integer columns after the public add() domain checks.

    Only validated_trade_arrays may construct this handle. It is not a raw
    array consumer: ordinary OrderedFlow.add still runs those checks itself.
    """

    __slots__ = ("size", "side", "event_ns", "source_order")

    def __init__(self, size, side, event_ns, source_order, *, _token=None):
        if _token is not _VALIDATED_TRADE_TOKEN:
            raise ContractError(_TRADE_ARRAYS_ERROR)
        self.size = size
        self.side = side
        self.event_ns = event_ns
        self.source_order = source_order

    def __len__(self):
        return len(self.size)


def validated_trade_arrays(*, size, side, event_ns, source_order):
    """Accept equal eligible integer trade columns once for every cohort."""
    import numpy as np

    columns = tuple(np.asarray(a) for a in (size, side, event_ns, source_order))
    size, side, event_ns, source_order = columns
    if (any(a.ndim != 1 or a.dtype.kind not in "iu" for a in columns)
            or any(len(a) != len(size) for a in columns)
            or np.any(size <= 0) or np.any(size >= 2**32 - 1)
            or np.any(~np.isin(side, (-1, 0, 1)))
            or np.any(event_ns < 0) or np.any(source_order < 0)):
        raise ContractError(_TRADE_ARRAYS_ERROR)
    return _ValidatedTradeArrays(size, side, event_ns, source_order, _token=_VALIDATED_TRADE_TOKEN)


def add_validated_trade_arrays(flow, prepared):
    """Apply one already-checked batch to a single cohort without repeating domain tests."""
    if type(flow) is not OrderedFlow or type(prepared) is not _ValidatedTradeArrays:
        raise ContractError(_TRADE_ARRAYS_ERROR)
    flow._add_validated(prepared)


@dataclass
class OrderedFlow:
    """One raw instrument and declared local window, with exact integer paths."""
    name: str = "all"
    opening: int = 0
    maximum_prints: int = 50_000_000
    buy: int = 0
    sell: int = 0
    unknown: int = 0
    prints: int = 0
    excluded_prints: int = 0
    excluded_volume: int = 0
    value: int = field(init=False)
    high: int = field(init=False)
    low: int = field(init=False)
    high_at_ns: int | None = None
    low_at_ns: int | None = None
    high_source_order: int | None = None
    low_source_order: int | None = None
    last_at_ns: int | None = None
    last_source_order: int | None = None
    _lower: int = field(init=False, repr=False)
    _upper: int | None = field(init=False, repr=False)

    def __post_init__(self):
        if (self.name not in SOURCE_FILTERS or type(self.opening) is not int
                or type(self.maximum_prints) is not int or not 1 <= self.maximum_prints <= 50_000_000):
            raise ContractError("explicit supported filter, exact opening and print bound required")
        self.value = self.high = self.low = self.opening
        if self.name == "all":
            self._lower, self._upper = 1, None
        else:
            included = [c for c in fixed_source_cohort(self.name).channels if c.id == "included"]
            self._lower, self._upper = included[0].lower_inclusive, included[0].upper_exclusive

    def add(self, *, size, side, event_ns, source_order):
        add_validated_trade_arrays(self, validated_trade_arrays(
            size=size, side=side, event_ns=event_ns, source_order=source_order))

    def _add_validated(self, prepared):
        import numpy as np

        if type(prepared) is not _ValidatedTradeArrays:
            raise ContractError(_TRADE_ARRAYS_ERROR)
        columns = (prepared.size, prepared.side, prepared.event_ns, prepared.source_order)
        size, side, event_ns, source_order = columns
        if self.prints + self.excluded_prints + len(size) > self.maximum_prints:
            raise ContractError(_TRADE_ARRAYS_ERROR)
        if not len(size):
            return
        if (np.any(event_ns[1:] < event_ns[:-1]) or np.any(source_order[1:] <= source_order[:-1])
                or self.last_at_ns is not None and int(event_ns[0]) < self.last_at_ns
                or self.last_source_order is not None and int(source_order[0]) <= self.last_source_order):
            raise IntegrityError("ordered cumulative paths cannot invent or duplicate source order")
        self.last_at_ns, self.last_source_order = int(event_ns[-1]), int(source_order[-1])
        chosen = size >= self._lower
        if self._upper is not None:
            chosen &= size < self._upper
        self.excluded_prints += int(np.count_nonzero(~chosen))
        self.excluded_volume += int(size[~chosen].sum(dtype=np.int64))
        size, side, event_ns, source_order = (a[chosen].astype(np.int64, copy=False) for a in columns)
        if not len(size):
            return
        self.prints += len(size)
        for sign, attr in ((1, "buy"), (-1, "sell"), (0, "unknown")):
            setattr(self, attr, getattr(self, attr) + int(size[side == sign].sum(dtype=np.int64)))
        # The stated print/size bound limits cumulative integer magnitude below
        # 2**58. Opening offsets use Python integers and are added afterwards.
        path = np.cumsum(size * side, dtype=np.int64)
        hi, lo = int(np.argmax(path)), int(np.argmin(path))
        candidate_high, candidate_low = self.value + int(path[hi]), self.value + int(path[lo])
        if candidate_high > self.high:
            self.high, self.high_at_ns, self.high_source_order = candidate_high, int(event_ns[hi]), int(source_order[hi])
        if candidate_low < self.low:
            self.low, self.low_at_ns, self.low_source_order = candidate_low, int(event_ns[lo]), int(source_order[lo])
        self.value += int(path[-1])

    def record(self, *, coverage_complete: bool):
        if type(coverage_complete) is not bool:
            raise ContractError("window coverage is an explicit separate input")
        total = self.buy + self.sell + self.unknown
        if self.value != self.opening + self.buy - self.sell:
            raise IntegrityError("ordered path and side-mass arithmetic disagree")
        return {"version": VERSION, "filter": self.name, "open": self.opening,
                "high": self.high, "low": self.low, "close": self.value,
                "high_at_ns": self.high_at_ns, "low_at_ns": self.low_at_ns,
                "high_source_order": self.high_source_order, "low_source_order": self.low_source_order,
                "buy": self.buy, "sell": self.sell, "unknown": self.unknown,
                "prints": self.prints, "volume": total, "excluded_prints": self.excluded_prints,
                "excluded_volume": self.excluded_volume, "coverage_complete": coverage_complete,
                "observed_signed_lower": self.value - self.unknown,
                "observed_signed_upper": self.value + self.unknown,
                "true_signed_lower": self.value - self.unknown if coverage_complete else None,
                "true_signed_upper": self.value + self.unknown if coverage_complete else None,
                "known_side_fraction": (self.buy + self.sell) / total if total else None,
                "empty_observed_cohort": coverage_complete and self.prints == 0,
                "ordering_basis": "preserved source storage order; absent exchange sequence remains unknown"}


class SparseSideMass:
    """Exact nonnegative side cells; price-invalid volume is never zeroed out."""

    def __init__(self, *, row_ticks=1, origin_ticks=0, maximum_cells=250000):
        if (type(row_ticks) is not int or not 1 <= row_ticks <= 1024
                or type(origin_ticks) is not int or abs(origin_ticks) >= 2**53 or type(maximum_cells) is not int
                or not 1 <= maximum_cells <= 1_000_000):
            raise ContractError("explicit exact fixed grid and cell bound required")
        self.row_ticks, self.origin_ticks = row_ticks, origin_ticks
        self.maximum_cells = maximum_cells
        self.rows = {}
        self.unpriced = [0, 0, 0]
        self.total = 0

    def add(self, *, price_ticks, price_valid, size, side):
        import numpy as np

        columns = tuple(np.asarray(a) for a in (price_ticks, price_valid, size, side))
        price_ticks, price_valid, size, side = columns
        if (any(a.ndim != 1 or a.dtype.kind not in "ibu" for a in columns)
                or any(len(a) != len(size) for a in columns)
                or len(size) > 50_000_000 or np.any(size <= 0) or np.any(size >= 2**32 - 1)
                or np.any(~np.isin(side, (-1, 0, 1))) or np.any(~np.isin(price_valid, (0, 1)))):
            raise ContractError("exact bounded eligible trade arrays required")
        mask = price_valid.astype(bool)
        if np.any(price_ticks[mask] <= 0) or np.any(price_ticks[mask] >= 2**53):
            raise ContractError("valid raw prices must retain positive exact tick coordinates")
        self.total += int(size.sum(dtype=np.int64))
        for sign, channel in ((1, 0), (-1, 1), (0, 2)):
            self.unpriced[channel] += int(size[(side == sign) & ~mask].sum(dtype=np.int64))
            kept = mask & (side == sign)
            if not np.any(kept):
                continue
            # Integer sorting and reduceat preserve exact contract mass. Floating
            # histogram weights would silently lose exactness for large totals.
            rows = (price_ticks[kept].astype(np.int64) - self.origin_ticks) // self.row_ticks
            mass = size[kept].astype(np.int64)
            order = np.argsort(rows, kind="stable")
            rows, mass = rows[order], mass[order]
            starts = np.r_[0, np.flatnonzero(rows[1:] != rows[:-1]) + 1]
            totals = np.add.reduceat(mass, starts)
            for row, amount in zip(rows[starts], totals, strict=True):
                row = int(row)
                if row not in self.rows:
                    if len(self.rows) >= self.maximum_cells:
                        raise ContractError("profile exceeds its fixed cell capacity")
                    self.rows[row] = [0, 0, 0]
                self.rows[row][channel] += int(amount)

    def record(self, *, coverage_complete: bool):
        if type(coverage_complete) is not bool:
            raise ContractError("explicit profile window coverage required")
        rows = tuple((r, *mass) for r, mass in sorted(self.rows.items()))
        if sum(sum(mass) for mass in self.rows.values()) + sum(self.unpriced) != self.total:
            raise IntegrityError("trade/side/profile mass is not conserved")
        return {"version": VERSION, "row_ticks": self.row_ticks, "origin_ticks": self.origin_ticks,
                "rows": rows, "unpriced_buy_sell_unknown": tuple(self.unpriced),
                "total_volume": self.total, "coverage_complete": coverage_complete}

    def geometry(self, *, value_fraction=Fraction(7, 10), tie_rule="lower"):
        histogram = {int(r): int(sum(mass)) for r, mass in self.rows.items()}
        if histogram and max(histogram) - min(histogram) + 1 > self.maximum_cells:
            raise ContractError("value-area traversal exceeds the registered grid span; raw sparse mass remains available")
        area = value_area(histogram, fraction=value_fraction, tie_rule=tie_rule)
        return {"poc_row": None if area is None else area.poc,
                "poc_maximizers": () if area is None else area.poc_maximizers,
                "value_low_row": None if area is None else area.lower_row,
                "value_high_row": None if area is None else area.upper_row,
                "value_requested_fraction": value_fraction,
                "value_achieved_fraction": None if area is None else area.achieved_fraction,
                "tie_rule": tie_rule, "value_expansion": "neighbor mass; zero rows crossed without invented volume"}

    def weighted_price(self):
        if self.row_ticks != 1:
            raise ContractError("coarse row centers cannot replace actual trade prices in VWAP")
        weighted = tuple((self.origin_ticks + row, sum(mass)) for row, mass in sorted(self.rows.items()))
        total = sum(mass for _, mass in weighted)
        first = sum(price * mass for price, mass in weighted)
        second = sum(price * price * mass for price, mass in weighted)
        mean = Fraction(first, total) if total else None
        return {"priced_volume": total, "sum_price_volume": first, "sum_price_squared_volume": second,
                "vwap_ticks": mean, "variance_ticks_squared": Fraction(second, total) - mean**2 if total else None,
                "weighted_quantile_ticks": {str(p): weighted_quantile(weighted, p)
                    for p in (Fraction(5, 100), Fraction(25, 100), Fraction(1, 2), Fraction(75, 100), Fraction(95, 100))}}
