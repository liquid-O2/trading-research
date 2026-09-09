"""Streaming best-quote measurements in the acquired source-order scenario.

The compact projection is the conservative BookReducer consumer: an explicit
gap/clear/unknown action remains blocked until a supported reconstruction is
supplied. This module does not invent that reconstruction. Trade-attached
quotes never enter the fresh-quote population. Prices and OFI stay integer
ticks/contracts; dimensionless ratios use compensated extended-precision
batch sums and retain their exact integer denominators in the source record.
"""
from __future__ import annotations

import math

from trading_research.errors import ContractError, IntegrityError


VERSION = "auction-flow-source-order-quote-measurements-v1"
REQUIRED = ("t", "source_order", "instrument_id", "bid", "ask", "bid_size",
            "ask_size", "book_valid", "snapshot", "raw_flags", "raw_action",
            "raw_side", "known_at_ns", "source_key", "source_row")
_SUMS = ("depth_normalized_ofi", "update_imbalance", "microprice_minus_midpoint_ticks",
         "spread_ticks", "duration_imbalance_ns", "duration_spread_ticks_ns")
_KEEP_NATIVE = object()


class QuoteWindow:
    """One instrument and explicit event-time window, published after its delay.

    Exposure follows the retained provider-normalized storage order. Missing
    exchange sequence remains a separate limitation even when equal-time
    updates have zero elapsed duration. Complete archive coverage is supplied
    by the caller; a plausible standing BBO cannot certify source completeness.
    """

    def __init__(self, *, instrument_id, start_ns, end_ns, latency_ns=250_000_000,
                 maximum_events=50_000_000, maximum_age_ns=None, row_ticks=1, origin_ticks=0,
                 native_sink=None, initial_state=None):
        if (type(instrument_id) is not int or instrument_id <= 0
                or type(start_ns) is not int or type(end_ns) is not int
                or not 0 <= start_ns < end_ns < 2**63 - 1_000_000_000
                or type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000
                or type(maximum_events) is not int or not 1 <= maximum_events <= 50_000_000
                or maximum_age_ns is not None and (type(maximum_age_ns) is not int or not 0 < maximum_age_ns < 2**63)
                or type(row_ticks) is not int or not 1 <= row_ticks <= 1024
                or type(origin_ticks) is not int or abs(origin_ticks) >= 2**53):
            raise ContractError("bounded raw instrument, event interval and delay/age scenario required")
        self.instrument_id = instrument_id
        self.start, self.end, self.delay = start_ns, end_ns, latency_ns
        self.maximum_events, self.maximum_age = maximum_events, maximum_age_ns
        self.row_ticks, self.origin_ticks = row_ticks, origin_ticks
        if native_sink is not None and (native_sink.instrument_id != instrument_id
                or native_sink.start > start_ns or native_sink.end < end_ns):
            raise ContractError('native quote consumer must contain the same raw instrument and event interval')
        self.native_sink = native_sink
        self.midpoint_durations = {}
        self.previous = None
        self.initial_projection = None
        self.events = self.fresh = self.pressure_updates = self.invalid = self.snapshots = 0
        self.gaps = self.clears = self.equal_times = 0
        self.ofi = self.same_price_ofi = self.price_change_ofi = 0
        self.ofi_high = self.ofi_low = 0
        self.ofi_high_at = self.ofi_low_at = None
        self.ofi_high_order = self.ofi_low_order = None
        self.duration = self.positive_duration = self.positive_updates = 0
        self.action_sides = {}
        self.sums = {name: [] for name in _SUMS}
        self._closed = False
        if initial_state is not None:
            self._seed(initial_state)

    def _seed(self, previous):
        """An actual preceding state, supplied by the completed source carry.

        The original quote event, known-at time and economic age remain intact.
        Restoring a projection never sets book_valid or removes an invalidation.
        """
        fields = set(REQUIRED) | {'economic_at'}
        if (not isinstance(previous, dict) or not fields <= previous.keys()
                or any(type(previous[k]) is not int for k in fields - {'raw_action', 'raw_side', 'source_key'})
                or previous['instrument_id'] != self.instrument_id or not 0 <= previous['t'] < self.start
                or previous['known_at_ns'] != previous['t'] + self.delay
                or previous['source_order'] < 0 or previous['source_row'] < 0
                or not -1 <= previous['economic_at'] <= previous['t']
                or previous['book_valid'] not in (0, 1) or previous['snapshot'] not in (0, 1)
                or not 0 <= previous['raw_flags'] <= 255
                or previous['snapshot'] != int(bool(previous['raw_flags'] & 32))
                or not isinstance(previous['source_key'], str) or not previous['source_key']):
            raise IntegrityError('preceding quote state has lost its actual source coordinate, clock or age')
        if previous['book_valid'] and (previous['raw_action'] not in ('A', 'M', 'C')
                or previous['raw_flags'] & 4 or not 0 < previous['bid'] <= previous['ask'] < 2**53
                or not 0 < previous['bid_size'] < 2**32 - 1 or not 0 < previous['ask_size'] < 2**32 - 1):
            raise IntegrityError('invalid preceding quote cannot be restored as a trusted state')
        self.previous = dict(previous)
        self.initial_projection = dict(previous)

    def continue_window(self, *, end_ns, native_sink=_KEEP_NATIVE):
        """Carry the actually processed standing state across an adjacent cut.

        Empty observed bins preserve age and source lineage. They do not mint
        a fresh quote, infer a recovery, or lose the first next-bin OFI update.
        """
        if not self._closed:
            raise IntegrityError("the preceding quote window must be closed before continuation")
        result = QuoteWindow(instrument_id=self.instrument_id, start_ns=self.end, end_ns=end_ns,
            latency_ns=self.delay, maximum_events=self.maximum_events, maximum_age_ns=self.maximum_age,
            row_ticks=self.row_ticks, origin_ticks=self.origin_ticks,
            native_sink=self.native_sink if native_sink is _KEEP_NATIVE else native_sink,
            initial_state=self.previous)
        return result

    def _sum(self, name, values):
        import numpy as np

        # Integer OFI and nanosecond exposure are summed separately, exactly.
        # This is only for rational-valued ratios and their time integrals.
        self.sums[name].append(float(np.sum(values, dtype=np.longdouble)))

    def _exposure(self, *, start, end, bid, ask, bid_size, ask_size, valid, economic_at):
        import numpy as np

        a, b = np.maximum(start, self.start), np.minimum(end, self.end)
        if self.maximum_age is not None:
            # Avoid overflowing a hypothetical near-int64-end input clock.
            room = np.maximum(0, np.minimum(self.maximum_age, self.end - economic_at))
            b = np.minimum(b, economic_at + room)
        duration = np.where(valid & (economic_at >= 0), np.maximum(0, b - a), 0)
        keep = duration > 0
        if not np.any(keep):
            return
        duration = duration[keep]
        if self.native_sink is not None:
            self.native_sink.quote_exposure(starts=a[keep], ends=b[keep], bid=bid[keep], ask=ask[keep],
                bid_size=bid_size[keep], ask_size=ask_size[keep])
        qb, qa = bid_size[keep], ask_size[keep]
        ratio = (qb.astype(np.longdouble) - qa) / (qb.astype(np.longdouble) + qa)
        self.duration += int(duration.sum(dtype=np.int64))
        rows = (bid[keep] + ask[keep] - 2 * self.origin_ticks) // (2 * self.row_ticks)
        order = np.argsort(rows, kind="stable")
        rows, mass = rows[order], duration[order]
        starts = np.r_[0, np.flatnonzero(rows[1:] != rows[:-1]) + 1]
        for row, amount in zip(rows[starts], np.add.reduceat(mass, starts), strict=True):
            if int(row) not in self.midpoint_durations and len(self.midpoint_durations) >= 250000:
                raise ContractError("displayed occupancy exceeds its finite retained row capacity")
            self.midpoint_durations[int(row)] = self.midpoint_durations.get(int(row), 0) + int(amount)
        self.positive_duration += int(duration[qb > qa].sum(dtype=np.int64))
        self._sum("duration_imbalance_ns", duration.astype(np.longdouble) * ratio)
        self._sum("duration_spread_ticks_ns", duration.astype(np.longdouble) * (ask[keep] - bid[keep]))

    def add(self, table):
        import numpy as np
        import pyarrow as pa
        import pyarrow.compute as pc

        if self._closed or not set(REQUIRED).issubset(table.schema.names):
            raise IntegrityError("open quote window and complete source-bound projection required")
        if self.events + len(table) > self.maximum_events:
            raise ContractError("quote window exceeds its registered event capacity")
        if not len(table):
            return
        if any(table[name].null_count for name in REQUIRED if name not in ("raw_action", "raw_side")):
            raise IntegrityError("required quote coordinate or clock is null")
        values = {name: table[name].to_numpy(zero_copy_only=False) for name in REQUIRED
                  if name not in ("raw_action", "raw_side", "source_key")}
        t, order = values["t"], values["source_order"]
        if (any(v.dtype.kind not in "iu" or v.ndim != 1 for v in values.values())
                or np.any(values["instrument_id"] != self.instrument_id)
                or np.any(t < self.start) or np.any(t >= self.end)
                or np.any(values["known_at_ns"] != t + self.delay)
                or np.any(order < 0) or np.any(values["source_row"] < 0)
                or np.any(t[1:] < t[:-1]) or np.any(order[1:] <= order[:-1])
                or self.previous is not None and (t[0] < self.previous["t"] or order[0] <= self.previous["source_order"])):
            raise IntegrityError("quote identity, information cut or retained order disagrees")
        valid, snapshot = values["book_valid"], values["snapshot"]
        flags = values["raw_flags"]
        if (np.any(~np.isin(valid, (0, 1))) or np.any(~np.isin(snapshot, (0, 1)))
                or np.any(flags > 255) or np.any(snapshot != ((flags & 32) != 0))):
            raise IntegrityError("quote projection flags or validity bits changed")
        valid, snapshot = valid.astype(bool), snapshot.astype(bool)
        bid, ask, qb, qa = (values[name] for name in ("bid", "ask", "bid_size", "ask_size"))
        if np.any(valid & ((bid <= 0) | (ask >= 2**53) | (bid > ask) | (qb <= 0) | (qa <= 0)
                           | (qb >= 2**32 - 1) | (qa >= 2**32 - 1) | ((flags & 4) != 0))):
            raise IntegrityError("trusted projected BBO is outside the exact admitted domain")
        actions = pc.cast(table["raw_action"], pa.string())
        updates = pc.fill_null(pc.is_in(actions, value_set=pa.array(["A", "M", "C"])), False).to_numpy()
        clears = pc.fill_null(pc.equal(actions, "R"), False).to_numpy()
        known = pc.fill_null(pc.is_in(actions, value_set=pa.array(["A", "M", "C", "R", "T", "N"])), False).to_numpy()
        if np.any(valid & (~updates | clears | ~known)):
            raise IntegrityError("a non-update projection cannot become a trusted fresh quote")
        previous = self.previous

        def lag(name, initial=0):
            return np.r_[previous[name] if previous else initial, values[name][:-1]]

        pb, pap, pqb, pqa = (lag(name) for name in ("bid", "ask", "bid_size", "ask_size"))
        before_valid = lag("book_valid").astype(bool)
        fresh = updates & valid & ~snapshot & ((flags & 4) == 0)
        measured = fresh & before_valid
        idx = np.flatnonzero(measured)
        changed_economic = (updates & ~snapshot) | clears
        latest_clock_index = np.maximum.accumulate(np.where(changed_economic, np.arange(len(t)) + 1, 0))
        clock_values = np.r_[previous["economic_at"] if previous else -1, np.where(clears, -1, t)]
        current_economic = clock_values[latest_clock_index]
        before_economic = np.r_[previous["economic_at"] if previous else -1, current_economic[:-1]]
        self._exposure(start=lag("t", self.start), end=t, bid=pb, ask=pap,
                       bid_size=pqb, ask_size=pqa, valid=before_valid, economic_at=before_economic)
        ofi = same = np.array([], dtype=np.int64)
        if len(idx):
            # The 50M event / eligible uint32 depth bound keeps int64 sums exact.
            b, a, q_b, q_a = bid[idx], ask[idx], qb[idx], qa[idx]
            b0, a0, q_b0, q_a0 = pb[idx], pap[idx], pqb[idx], pqa[idx]
            ofi = (b >= b0) * q_b - (b <= b0) * q_b0 - (a <= a0) * q_a + (a >= a0) * q_a0
            same = np.where(b == b0, q_b - q_b0, 0) - np.where(a == a0, q_a - q_a0, 0)
            path = np.cumsum(ofi, dtype=np.int64)
            hi, lo = int(np.argmax(path)), int(np.argmin(path))
            if self.ofi + int(path[hi]) > self.ofi_high:
                self.ofi_high, self.ofi_high_at, self.ofi_high_order = self.ofi + int(path[hi]), int(t[idx[hi]]), int(order[idx[hi]])
            if self.ofi + int(path[lo]) < self.ofi_low:
                self.ofi_low, self.ofi_low_at, self.ofi_low_order = self.ofi + int(path[lo]), int(t[idx[lo]]), int(order[idx[lo]])
            self.ofi += int(path[-1])
            self.same_price_ofi += int(same.sum(dtype=np.int64))
            self.price_change_ofi += int((ofi - same).sum(dtype=np.int64))
            self._sum("depth_normalized_ofi", ofi.astype(np.longdouble) / (q_b0.astype(np.longdouble) + q_a0))
            imbalance = (q_b.astype(np.longdouble) - q_a) / (q_b.astype(np.longdouble) + q_a)
            self._sum("update_imbalance", imbalance)
            # Algebraic microprice-midpoint avoids multiplying large prices by
            # sizes and retains the exact integer spread from the source grid.
            self._sum("microprice_minus_midpoint_ticks", (a - b).astype(np.longdouble) * imbalance / 2)
            self._sum("spread_ticks", a - b)
            self.positive_updates += int(np.count_nonzero(q_b > q_a))
        if self.native_sink is not None:
            self.native_sink.quote_updates(at=t, order=order, fresh=fresh, measured=measured, ofi=ofi, same=same)
        self.events += len(t)
        self.fresh += int(fresh.sum())
        self.pressure_updates += len(idx)
        self.invalid += int(np.count_nonzero(~valid))
        self.snapshots += int(snapshot.sum())
        self.gaps += int(np.count_nonzero(flags & 4))
        self.clears += int(clears.sum())
        self.equal_times += int(np.count_nonzero(t == lag("t", -1)))
        pairs = pa.table({"action": actions, "side": pc.cast(table["raw_side"], pa.string()),
                          "event_ns": table["t"]}).group_by(["action", "side"], use_threads=False).aggregate([("event_ns", "count")])
        for row in pairs.to_pylist():
            key = (row["action"], row["side"])
            self.action_sides[key] = self.action_sides.get(key, 0) + row["event_ns_count"]
        self.previous = {name: int(v[-1]) for name, v in values.items()}
        self.previous.update(economic_at=int(current_economic[-1]), source_key=table["source_key"][-1].as_py(),
                             raw_action=table["raw_action"][-1].as_py(), raw_side=table["raw_side"][-1].as_py())

    def finish(self, *, coverage_complete):
        import numpy as np

        if self._closed or type(coverage_complete) is not bool:
            raise IntegrityError("quote publication requires one explicit completed coverage decision")
        self._closed = True
        if self.previous:
            p = self.previous
            self._exposure(start=np.array([p["t"]]), end=np.array([self.end]),
                bid=np.array([p["bid"]]), ask=np.array([p["ask"]]),
                bid_size=np.array([p["bid_size"]]), ask_size=np.array([p["ask_size"]]),
                valid=np.array([bool(p["book_valid"])]), economic_at=np.array([p["economic_at"]]))
        sums = {name: math.fsum(values) for name, values in self.sums.items()}
        if self.ofi != self.same_price_ofi + self.price_change_ofi or not 0 <= self.duration <= self.end - self.start:
            raise IntegrityError("quote decomposition or standing exposure does not reconcile")
        if sum(self.midpoint_durations.values()) != self.duration:
            raise IntegrityError("displayed midpoint occupancy and standing exposure differ")
        n = self.pressure_updates
        return {"version": VERSION, "instrument_id": self.instrument_id,
            "event_start_ns": self.start, "event_end_ns": self.end,
            "known_at_ns": self.end + self.delay, "latency_scenario_ns": self.delay,
            "maximum_standing_age_ns": self.maximum_age, "coverage_complete": coverage_complete,
            "quote_or_invalidation_rows": self.events, "fresh_quote_updates": self.fresh,
            "pressure_transitions": n, "invalid_book_rows": self.invalid,
            "snapshot_rows": self.snapshots, "gap_rows": self.gaps, "clear_rows": self.clears,
            "equal_time_adjacent_quote_rows": self.equal_times,
            "action_side_counts": [{"action": a, "side": s, "rows": count}
                for (a, s), count in sorted(self.action_sides.items(), key=lambda item: repr(item[0]))],
            "ofi_contracts": self.ofi, "same_price_size_ofi": self.same_price_ofi,
            "price_change_ofi": self.price_change_ofi,
            "ofi_path": {"open": 0, "high": self.ofi_high, "low": self.ofi_low, "close": self.ofi,
                "high_at_ns": self.ofi_high_at, "low_at_ns": self.ofi_low_at,
                "high_source_order": self.ofi_high_order, "low_source_order": self.ofi_low_order},
            "per_pressure_transition_ofi": self.ofi / n if n else None,
            "per_complete_window_second_ofi": self.ofi * 1e9 / (self.end - self.start) if coverage_complete else None,
            "sum_depth_normalized_ofi": sums["depth_normalized_ofi"],
            "update_mean_imbalance": sums["update_imbalance"] / n if n else None,
            "update_positive_fraction": self.positive_updates / n if n else None,
            "update_mean_microprice_minus_midpoint_ticks": sums["microprice_minus_midpoint_ticks"] / n if n else None,
            "update_mean_spread_ticks": sums["spread_ticks"] / n if n else None,
            "observed_trusted_standing_duration_ns": self.duration,
            "duration_mean_imbalance": sums["duration_imbalance_ns"] / self.duration if self.duration else None,
            "duration_positive_fraction": self.positive_duration / self.duration if self.duration else None,
            "duration_mean_spread_ticks": sums["duration_spread_ticks_ns"] / self.duration if self.duration else None,
            "displayed_midpoint_occupancy": {"row_ticks": self.row_ticks, "origin_ticks": self.origin_ticks,
                "duration_ns_by_row": tuple(sorted(self.midpoint_durations.items())),
                "observed_assigned_duration_ns": self.duration,
                "unassigned_duration_ns": self.end - self.start - self.duration,
                "representation": "observed_displayed_quote_midpoint", "trade_residence_claim": False},
            "initial_projection": self.initial_projection,
            "terminal_projection": self.previous,
            "order_basis": "retained single-source storage order; provider sequence and strategy receipt absent",
            "exchange_order_certified": False,
            "book_recovery": "no recovery is inferred; original invalidation remains until supported source reconstruction"}
