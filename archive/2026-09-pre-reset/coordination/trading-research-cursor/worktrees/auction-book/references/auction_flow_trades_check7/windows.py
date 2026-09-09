"""Exact ordered trade measurements for reusable event-time windows.

An event window and its publication cut are separate. The caller supplies the
source/coordinate coverage disposition after finishing the complete raw scan.
Unpriced trades retain flow and interrupt price travel; missing observations
cannot become a zero-return or zero-activity window.
"""
from __future__ import annotations

from fractions import Fraction
from array import array
import math

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_measurements import OrderedFlow, SOURCE_FILTERS, SparseSideMass


VERSION = "auction-flow-exact-trade-windows-v1"


def exact_sample_quantiles(values, probabilities=(Fraction(1, 4), Fraction(1, 2), Fraction(3, 4), Fraction(95, 100))):
    """Exact type-7 ranks/interpolation without converting integer clocks to floats."""
    import numpy as np

    if (not isinstance(values, array) or values.typecode != 'q' or values.itemsize != 8
            or not isinstance(probabilities, tuple) or not 1 <= len(probabilities) <= 32
            or any(not isinstance(p, Fraction) or not 0 <= p <= 1 for p in probabilities)
            or len(set(probabilities)) != len(probabilities)):
        raise ContractError('bounded exact int64 samples and distinct rational quantile probabilities required')
    if not len(values):
        return {str(p): None for p in probabilities}
    at = {p: (len(values) - 1) * p for p in probabilities}
    ranks = sorted({int(x) for x in at.values()} | {min(len(values) - 1, int(x) + 1) for x in at.values()})
    ordered = np.partition(np.frombuffer(values, dtype=np.int64), ranks)
    return {str(p): Fraction(int(ordered[int(x)])) + (x - int(x)) *
            (int(ordered[min(len(values) - 1, int(x) + 1)]) - int(ordered[int(x)])) for p, x in at.items()}


def _exact_power_sum(values, power):
    """Use integer vector sums when bounded; retain Python integers otherwise."""
    import numpy as np

    if not len(values):
        return 0
    maximum = int(np.max(np.abs(values)))
    threshold = (2**63 - 1) // len(values)
    if maximum <= (threshold if power == 1 else math.isqrt(threshold)):
        terms = np.abs(values) if power == 1 else values * values
        return int(terms.sum(dtype=np.int64))
    return sum(abs(int(v)) if power == 1 else int(v)**2 for v in values)


class TapeWindow:
    def __init__(self, *, instrument_id, start_ns, end_ns, latency_ns=250_000_000,
                 maximum_trades=50_000_000, maximum_profile_cells=250000):
        if (type(instrument_id) is not int or instrument_id <= 0
                or type(start_ns) is not int or type(end_ns) is not int
                or not 0 <= start_ns < end_ns < 2**63 - 1_000_000_000
                or type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000):
            raise ContractError("exact raw instrument, bounded event interval and delay scenario required")
        self.instrument_id, self.start, self.end, self.delay = instrument_id, start_ns, end_ns, latency_ns
        self.flows = {name: OrderedFlow(name, maximum_prints=maximum_trades) for name in SOURCE_FILTERS}
        self.profile = SparseSideMass(maximum_cells=maximum_profile_cells)
        self.maximum_trades = maximum_trades
        self.prints = self.unpriced = self.same_time_pairs = self.priced_pairs = 0
        self.variation = self.squared_variation = self.up_variation = self.down_variation = 0
        self.sum_squared_sizes = 0
        self.print_sizes, self.interarrival_ns = array('q'), array('q')
        self.current_same_side_run = self.maximum_same_side_run = self.last_side = 0
        self.first = self.last = self.first_priced = self.last_priced = None
        self.high = self.low = None
        self.high_at = self.low_at = self.high_order = self.low_order = None
        self._failed = False

    def add(self, table):
        if self._failed:
            raise IntegrityError("a failed trade accumulator cannot publish or resume partial state")
        try:
            self._add(table)
        except BaseException:
            self._failed = True
            raise

    def _add(self, table):
        import numpy as np
        import pyarrow as pa
        import pyarrow.compute as pc

        fields = ("t", "source_order", "instrument_id", "price", "size", "side", "price_valid",
                  "source_row", "source_key", "raw_flags", "raw_side", "raw_action", "known_at_ns")
        if not set(fields).issubset(table.schema.names):
            raise ContractError("the complete source-bound eligible trade projection is required")
        if any(table[name].null_count for name in fields if name != "raw_side"):
            raise IntegrityError("required trade coordinate, clock or source address is null")
        if not len(table):
            return
        values = {name: table[name].to_numpy(zero_copy_only=False) for name in fields
                  if name not in ("source_key", "raw_side", "raw_action")}
        t, price, valid, size, side, order = (values[name] for name in ("t", "price", "price_valid", "size", "side", "source_order"))
        expected_side = pc.if_else(pc.equal(table["raw_side"], "B"), 1,
                                  pc.if_else(pc.equal(table["raw_side"], "A"), -1, 0))
        expected_side = pc.fill_null(expected_side, 0).to_numpy()
        if (any(v.dtype.kind not in "iu" or v.ndim != 1 for v in values.values())
                or np.any(values["instrument_id"] != self.instrument_id)
                or np.any(t < self.start) or np.any(t >= self.end)
                or np.any(values["known_at_ns"] != t + self.delay)
                or np.any(values["source_row"] < 0) or np.any(values["raw_flags"] > 255)
                or np.any(values["raw_flags"] & 32) or np.any(side != expected_side)
                or not pc.all(pc.equal(pc.cast(table["raw_action"], pa.string()), "T")).as_py()):
            raise IntegrityError("trade source mapping, snapshot inclusion, identity or information cut changed")
        a = dict(size=size, side=side, event_ns=t, source_order=order)
        # This shared public arithmetic boundary checks integer size/order and
        # strict original multiplicity. A failure poisons the complete window.
        for flow in self.flows.values():
            flow.add(**a)
        self.profile.add(price_ticks=price, price_valid=valid, size=size, side=side)
        previous = self.last
        deltas = np.diff(t) if previous is None else np.diff(np.r_[previous['event_ns'], t])
        self.interarrival_ns.frombytes(np.ascontiguousarray(deltas, dtype=np.int64).tobytes())
        self.print_sizes.frombytes(np.ascontiguousarray(size, dtype=np.int64).tobytes())
        segments = np.r_[0, np.flatnonzero(side[1:] != side[:-1]) + 1]
        run_sizes = np.diff(np.r_[segments, len(side)])
        if side[0] != 0 and side[0] == self.last_side:
            run_sizes[0] += self.current_same_side_run
        known = side[segments] != 0
        if np.any(known):
            self.maximum_same_side_run = max(self.maximum_same_side_run, int(run_sizes[known].max()))
        self.current_same_side_run = int(run_sizes[-1]) if side[-1] else 0
        self.last_side = int(side[-1])
        before_price = np.r_[previous["price_ticks"] if previous and previous["price_valid"] else 0, price[:-1]]
        before_valid = np.r_[bool(previous and previous["price_valid"]), valid[:-1]].astype(bool)
        valid = valid.astype(bool)
        paired = valid & before_valid
        changes = price[paired] - before_price[paired]
        self.variation += _exact_power_sum(changes, 1)
        self.squared_variation += _exact_power_sum(changes, 2)
        self.up_variation += _exact_power_sum(changes[changes > 0], 1)
        self.down_variation += _exact_power_sum(changes[changes < 0], 1)
        self.priced_pairs += int(paired.sum())
        self.same_time_pairs += int(np.count_nonzero(t[1:] == t[:-1])) + int(previous is not None and previous["event_ns"] == int(t[0]))
        self.sum_squared_sizes += _exact_power_sum(size, 2)

        def observation(i):
            return {"event_ns": int(t[i]), "known_at_ns": int(values["known_at_ns"][i]),
                    "price_ticks": int(price[i]) if valid[i] else None, "price_valid": bool(valid[i]),
                    "source_order": int(order[i]), "source_row": int(values["source_row"][i]),
                    "source_key": table["source_key"][i].as_py()}

        if self.first is None:
            self.first = observation(0)
        self.last = observation(len(table) - 1)
        indices = np.flatnonzero(valid)
        if len(indices):
            if self.first_priced is None:
                self.first_priced = observation(int(indices[0]))
            self.last_priced = observation(int(indices[-1]))
            hi, lo = int(indices[np.argmax(price[indices])]), int(indices[np.argmin(price[indices])])
            if self.high is None or int(price[hi]) > self.high:
                self.high, self.high_at, self.high_order = int(price[hi]), int(t[hi]), int(order[hi])
            if self.low is None or int(price[lo]) < self.low:
                self.low, self.low_at, self.low_order = int(price[lo]), int(t[lo]), int(order[lo])
        self.prints += len(table)
        self.unpriced += int(np.count_nonzero(~valid))

    def record(self, *, source_coverage_complete, coordinate_complete):
        if self._failed or type(source_coverage_complete) is not bool or type(coordinate_complete) is not bool:
            raise IntegrityError("trade publication needs successful arithmetic and explicit completed coverage/coordinate checks")
        source_complete = source_coverage_complete and coordinate_complete
        priced_complete = source_complete and not self.unpriced
        flows = {name: flow.record(coverage_complete=source_coverage_complete) for name, flow in self.flows.items()}
        mass = self.profile.record(coverage_complete=source_complete)
        if flows["all"]["volume"] != mass["total_volume"] or self.variation != self.up_variation + self.down_variation:
            raise IntegrityError("window flow, mass or price-variation decomposition does not reconcile")
        volume = flows["all"]["volume"]
        if len(self.print_sizes) != self.prints or len(self.interarrival_ns) != max(0, self.prints - 1):
            raise IntegrityError("exact marked-size/interarrival population differs from the tape")
        for flow in flows.values():
            flow["count_occupancy"] = Fraction(flow["prints"], self.prints) if self.prints else None
            flow["volume_occupancy"] = Fraction(flow["volume"], volume) if volume else None
        displacement = self.last["price_ticks"] - self.first["price_ticks"] if self.first and self.last and self.first["price_valid"] and self.last["price_valid"] else None
        return {"version": VERSION, "instrument_id": self.instrument_id,
                "event_start_ns": self.start, "event_end_ns": self.end, "known_at_ns": self.end + self.delay,
                "source_coverage_complete": source_coverage_complete, "coordinate_complete": coordinate_complete,
                "flow_history_complete": source_coverage_complete, "price_history_complete": priced_complete,
                "prints": self.prints, "unpriced_prints": self.unpriced,
                "same_time_adjacent_prints": self.same_time_pairs,
                "first_trade": self.first, "last_trade": self.last,
                "first_priced_trade": self.first_priced, "last_priced_trade": self.last_priced,
                "observed_high_ticks": self.high, "observed_low_ticks": self.low,
                "observed_high_at_ns": self.high_at, "observed_low_at_ns": self.low_at,
                "observed_high_source_order": self.high_order, "observed_low_source_order": self.low_order,
                "observed_endpoints_displacement_ticks": displacement,
                "complete_path_displacement_ticks": displacement if priced_complete else None,
                "observed_adjacent_priced_pairs": self.priced_pairs,
                "observed_price_variation_ticks": self.variation,
                "observed_squared_price_variation_ticks_squared": self.squared_variation,
                "observed_up_variation_ticks": self.up_variation, "observed_down_variation_ticks": self.down_variation,
                "sum_squared_trade_sizes": self.sum_squared_sizes,
                "count_weighted_size_quantiles": exact_sample_quantiles(self.print_sizes),
                "observed_interarrival_quantiles_ns": exact_sample_quantiles(self.interarrival_ns),
                "observed_interarrival_pairs": len(self.interarrival_ns),
                "observed_maximum_same_side_run": self.maximum_same_side_run,
                "observed_terminal_same_side_run": self.current_same_side_run,
                "complete_maximum_same_side_run": self.maximum_same_side_run if source_coverage_complete else None,
                "terminal_run_right_censored": bool(self.current_same_side_run),
                "mean_print_size": Fraction(volume, self.prints) if self.prints else None,
                "count_intensity_per_second": Fraction(self.prints * 10**9, self.end - self.start) if source_coverage_complete else None,
                "volume_intensity_per_second": Fraction(volume * 10**9, self.end - self.start) if source_coverage_complete else None,
                "absolute_displacement_per_observed_contract": Fraction(abs(displacement), volume) if displacement is not None and volume else None,
                "flows": flows, "sparse_profile": mass, "weighted_price": self.profile.weighted_price(),
                "order_basis": "original single-source storage order; provider sequence absent",
                "empty_observed_window": source_coverage_complete and not self.prints}
