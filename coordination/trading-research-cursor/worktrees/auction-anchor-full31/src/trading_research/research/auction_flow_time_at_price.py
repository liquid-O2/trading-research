"""Actual bracket visits and bounded last-observed-trade dwell.

Sparse rows use an exact origin and width. Displayed midpoint occupancy is
measured independently by QuoteWindow. Missing source history never becomes
quiet trading, and neither construction claims actual residence or inventory.
"""
from __future__ import annotations

from fractions import Fraction

from trading_research.errors import ContractError, IntegrityError
from trading_research.measurements.tape import value_area


VERSION = "auction-flow-actual-visits-and-bounded-dwell-v1"


def _cover(intervals, start, end):
    return any(a <= start and end <= b for a, b in intervals)


def _tails(incidence):
    if not incidence:
        return {"low": (), "high": (), "low_same_bracket": None, "high_same_bracket": None}
    result = {}
    for side, at, step in (("low", min(incidence), 1), ("high", max(incidence), -1)):
        rows = []
        while at in incidence and len(incidence[at]) == 1:
            rows.append(at)
            at += step
        result[side] = tuple(sorted(rows))
        result[side + "_same_bracket"] = len({incidence[r][0] for r in rows}) == 1 if rows else None
    return result


class TimeAtPrice:
    def __init__(self, *, instrument_id, start_ns, end_ns, atomic_width_ns=60_000_000_000,
                 bracket_widths_ns=(300_000_000_000, 900_000_000_000, 1800_000_000_000, 3600_000_000_000),
                 stale_caps_ns=(1_000_000_000, 5_000_000_000, 30_000_000_000),
                 row_ticks=1, origin_ticks=0, maximum_cells=1_000_000, latency_ns=250_000_000,
                 initial_balance_ns=3600_000_000_000, initial_state=None, initial_raw=None):
        if (type(instrument_id) is not int or instrument_id <= 0
                or type(start_ns) is not int or type(end_ns) is not int or not 0 <= start_ns < end_ns < 2**63 - 1_000_000_000
                or type(atomic_width_ns) is not int or atomic_width_ns < 1
                or type(row_ticks) is not int or not 1 <= row_ticks <= 1024
                or type(origin_ticks) is not int or abs(origin_ticks) >= 2**53
                or type(maximum_cells) is not int or not 1 <= maximum_cells <= 1_000_000
                or type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000
                or type(initial_balance_ns) is not int or not 0 < initial_balance_ns < 2**63
                or not 1 <= len(bracket_widths_ns) <= 8 or not 1 <= len(stale_caps_ns) <= 8
                or any(type(v) is not int or not 0 < v < 2**63 for v in (*bracket_widths_ns, *stale_caps_ns))
                or len(set(bracket_widths_ns)) != len(bracket_widths_ns) or len(set(stale_caps_ns)) != len(stale_caps_ns)):
            raise ContractError("bounded exact raw coordinate, clocks and time-at-price variants required")
        if ((end_ns - start_ns + atomic_width_ns - 1) // atomic_width_ns > 100000
                or sum((end_ns - start_ns + v - 1) // v for v in bracket_widths_ns) > 16384):
            raise ContractError("atomic time-at-price grid exceeds its finite window capacity")
        self.instrument_id, self.start, self.end = instrument_id, start_ns, end_ns
        self.atomic_width, self.width, self.origin = atomic_width_ns, row_ticks, origin_ticks
        self.maximum_cells, self.latency = maximum_cells, latency_ns
        self.initial_balance_ns = initial_balance_ns
        self.ib_end = min(self.end, self.start + initial_balance_ns)
        self.ib_low = self.ib_high = None
        self.ib_unpriced = self.ib_invalid = 0
        self.visits = {v: {} for v in bracket_widths_ns}
        self.dwell = {v: {} for v in stale_caps_ns}
        self.unpriced_by_bracket = {v: {} for v in bracket_widths_ns}
        self.invalid_by_bracket = {v: {} for v in bracket_widths_ns}
        self.last_raw = self.last_state = None
        self.eligible_prints = self.unpriced_prints = self.invalidating_rows = 0
        self._failed = self._closed = False
        if initial_raw is not None:
            if (not isinstance(initial_raw, (tuple, list)) or len(initial_raw) != 2
                    or any(type(v) is not int for v in initial_raw)
                    or not 0 <= initial_raw[0] < self.start or initial_raw[1] < 0):
                raise IntegrityError('trade dwell continuation requires a past actual raw event and original order')
            self.last_raw = tuple(initial_raw)
        if initial_state is not None:
            if (not isinstance(initial_state, (tuple, list)) or len(initial_state) != 3
                    or type(initial_state[0]) is not int or type(initial_state[1]) is not int
                    or type(initial_state[2]) is not bool or not 0 <= initial_state[0] < self.start
                    or initial_raw is None or initial_state[0] > initial_raw[0]
                    or initial_state[2] and not 0 < initial_state[1] < 2**53):
                raise IntegrityError('trade dwell continuation cannot invent a price, age or earlier event')
            self.last_state = tuple(initial_state)
        self.initial_state = self.last_state

    def add(self, raw, trades, *, source_key):
        if self._failed or self._closed:
            raise IntegrityError("time-at-price input requires a live successful accumulator")
        try:
            self._add(raw, trades, source_key=source_key)
        except BaseException:
            self._failed = True
            raise

    def _add(self, raw, trades, *, source_key):
        import numpy as np
        import pyarrow as pa
        import pyarrow.compute as pc

        required = ("t", "source_order", "instrument_id", "flags", "size", "source_row", "action")
        if not set(required).issubset(raw.schema.names) or type(source_key) is not str or not 1 <= len(source_key) <= 128:
            raise ContractError("original source-order raw records and identity required")
        if not len(raw):
            if trades is not None and len(trades):
                raise IntegrityError("trades have no corresponding raw records")
            return
        if any(raw[name].null_count for name in required if name not in ("action", "size")):
            raise IntegrityError("raw event address, flag or clock is missing")
        t, order, flags = (raw[name].to_numpy(zero_copy_only=False) for name in ("t", "source_order", "flags"))
        if (any(v.dtype.kind not in "iu" for v in (t, order, flags)) or np.any(t < self.start) or np.any(t >= self.end)
                or np.any(t[1:] < t[:-1]) or np.any(order < 0) or np.any(order[1:] <= order[:-1]) or np.any(flags > 255)
                or np.any(raw['instrument_id'].to_numpy(zero_copy_only=False) != self.instrument_id) or np.any(raw['source_row'].to_numpy(zero_copy_only=False) < 0)
                or self.last_raw is not None and (int(t[0]) < self.last_raw[0] or int(order[0]) <= self.last_raw[1])):
            raise IntegrityError("time-at-price source identity/order/window differs")
        actions = pc.cast(raw['action'], pa.string())
        is_trade = pc.fill_null(pc.equal(actions, 'T'), False).to_numpy(zero_copy_only=False)
        known = pc.fill_null(pc.is_in(actions, value_set=pa.array(['A', 'M', 'C', 'R', 'T', 'N'])), False).to_numpy(zero_copy_only=False)
        size_ok = pc.fill_null(pc.and_(pc.greater(raw['size'], 0), pc.less(raw['size'], 2**32 - 1)), False).to_numpy(zero_copy_only=False)
        snapshot = (flags & 32) != 0
        eligible = is_trade & ~snapshot & size_ok
        positions = np.flatnonzero(eligible)
        if len(positions) != (0 if trades is None else len(trades)):
            raise IntegrityError("raw and retained eligible trade populations differ")
        price, priced = np.zeros(len(t), dtype=np.int64), np.zeros(len(t), dtype=bool)
        if len(positions):
            if (not np.array_equal(trades['source_order'].to_numpy(zero_copy_only=False), order[positions])
                    or not np.array_equal(trades['t'].to_numpy(zero_copy_only=False), t[positions])
                    or not np.array_equal(trades['size'].to_numpy(zero_copy_only=False), raw['size'].take(pa.array(positions)).to_numpy(zero_copy_only=False))
                    or not np.array_equal(trades['source_row'].to_numpy(zero_copy_only=False), raw['source_row'].take(pa.array(positions)).to_numpy(zero_copy_only=False))
                    or not pc.all(pc.equal(trades['source_key'], source_key)).as_py()
                    or np.any(trades['instrument_id'].to_numpy(zero_copy_only=False) != self.instrument_id)
                    or np.any(trades['known_at_ns'].to_numpy(zero_copy_only=False) != t[positions] + self.latency)):
                raise IntegrityError("trade projection does not join its original raw source address/cut")
            price[positions] = trades['price'].to_numpy(zero_copy_only=False)
            valid = trades['price_valid'].to_numpy(zero_copy_only=False)
            if np.any(~np.isin(valid, (0, 1))):
                raise IntegrityError("trade price-validity channel changed")
            priced[positions] = valid.astype(bool)
            if np.any(priced & ((price <= 0) | (price >= 2**53))):
                raise IntegrityError("trade dwell price is outside the exact tick domain")
            good = positions[priced[positions]]
            ib_prices = price[good[t[good] < self.ib_end]]
            if len(ib_prices):
                self.ib_low = min(int(ib_prices.min()), self.ib_low) if self.ib_low is not None else int(ib_prices.min())
                self.ib_high = max(int(ib_prices.max()), self.ib_high) if self.ib_high is not None else int(ib_prices.max())
            self.ib_unpriced += int(np.count_nonzero((t < self.ib_end) & eligible & ~priced))
            rows = (price[good] - self.origin) // self.width
            for width, cells in self.visits.items():
                brackets = (t[good] - self.start) // width
                # First original row for each bracket/price is causal. Crossing
                # intermediate prices creates neither visits nor trade mass.
                sorted_indices = np.lexsort((rows, brackets))
                sorted_bins, sorted_rows = brackets[sorted_indices], rows[sorted_indices]
                starts = np.r_[0, np.flatnonzero((sorted_bins[1:] != sorted_bins[:-1]) | (sorted_rows[1:] != sorted_rows[:-1])) + 1]
                first = sorted_indices[starts] if len(sorted_indices) else ()
                for i in first:
                    key = (int(brackets[i]), int(rows[i]))
                    if key not in cells:
                        if len(cells) >= self.maximum_cells:
                            raise ContractError("TPO incidence exceeds its retained cell capacity")
                        at = int(good[i])
                        cells[key] = (int(t[at]), int(order[at]), int(raw['source_row'][at].as_py()), source_key)
                bad_brackets, counts = np.unique((t[positions[~priced[positions]]] - self.start) // width, return_counts=True)
                for bracket, count in zip(bad_brackets, counts, strict=True):
                    by = self.unpriced_by_bracket[width]
                    by[int(bracket)] = by.get(int(bracket), 0) + int(count)
        broken = ((flags & 4) != 0) | ~known | (is_trade & ~snapshot & ~size_ok)
        self.ib_invalid += int(np.count_nonzero(broken & (t < self.ib_end)))
        for width, counts in self.invalid_by_bracket.items():
            ids, amounts = np.unique((t[broken] - self.start) // width, return_counts=True)
            for number, amount in zip(ids, amounts, strict=True):
                counts[int(number)] = counts.get(int(number), 0) + int(amount)
        transitions = np.flatnonzero(eligible | broken)
        if len(transitions):
            at, px, valid = t[transitions], price[transitions], (priced & ~broken)[transitions]
            if self.last_state is not None:
                old_t, old_p, old_valid = self.last_state
                at, px, valid = np.r_[old_t, at], np.r_[old_p, px], np.r_[old_valid, valid]
            self._durations(at[:-1], at[1:], px[:-1], valid[:-1])
            self.last_state = (int(at[-1]), int(px[-1]), bool(valid[-1]))
        self.last_raw = (int(t[-1]), int(order[-1]))
        self.eligible_prints += len(positions)
        self.unpriced_prints += int(np.count_nonzero(eligible & ~priced))
        self.invalidating_rows += int(np.count_nonzero(broken))

    def _durations(self, starts, ends, prices, valid):
        import numpy as np

        for cap, cells in self.dwell.items():
            a = np.maximum(starts, self.start)
            # The bounded event window avoids timestamp-plus-cap overflow.
            b = np.minimum(ends, starts + np.minimum(cap, self.end - starts))
            keep = valid & (b > a)
            aa, bb = a[keep], b[keep]
            rows = (prices[keep] - self.origin) // self.width
            if not len(rows):
                continue
            first, last = (aa - self.start) // self.atomic_width, (bb - 1 - self.start) // self.atomic_width
            same = first == last
            cross_bins, cross_rows, cross_durations = [], [], []
            # Non-overlapping dwell intervals cross each atomic boundary at
            # most once, so only this small boundary population needs splitting.
            for start, end, row, low, high in zip(aa[~same], bb[~same], rows[~same], first[~same], last[~same], strict=True):
                for number in range(int(low), int(high) + 1):
                    left, right = self.start + number * self.atomic_width, self.start + (number + 1) * self.atomic_width
                    cross_bins.append(number)
                    cross_rows.append(int(row))
                    cross_durations.append(int(min(end, right) - max(start, left)))
            bins = np.r_[first[same], np.asarray(cross_bins, dtype=np.int64)]
            cell_rows = np.r_[rows[same], np.asarray(cross_rows, dtype=np.int64)]
            durations = np.r_[(bb - aa)[same], np.asarray(cross_durations, dtype=np.int64)]
            order = np.lexsort((cell_rows, bins))
            bins, cell_rows = bins[order], cell_rows[order]
            split = np.r_[0, np.flatnonzero((bins[1:] != bins[:-1]) | (cell_rows[1:] != cell_rows[:-1])) + 1]
            totals = np.add.reduceat(durations[order], split)
            for number, row, duration in zip(bins[split], cell_rows[split], totals, strict=True):
                pair = (int(number), int(row))
                if pair not in cells and len(cells) >= self.maximum_cells:
                    raise ContractError("dwell profile exceeds its retained atomic cell capacity")
                cells[pair] = cells.get(pair, 0) + int(duration)

    def finish(self, *, covered_intervals, minimum_brackets=5):
        import numpy as np

        if self._failed or self._closed or type(minimum_brackets) is not int or minimum_brackets < 1:
            raise IntegrityError("time-at-price publication needs a successful complete source pass")
        intervals = tuple(covered_intervals)
        if any(type(a) is not int or type(b) is not int or not self.start <= a < b <= self.end for a, b in intervals):
            raise ContractError("explicit eligible source-and-coordinate intervals required")
        from trading_research.measurements.profiles import union_intervals
        intervals = tuple(union_intervals(intervals))
        self._closed = True
        if self.last_state is not None:
            at, price, valid = self.last_state
            self._durations(np.array([at]), np.array([self.end]), np.array([price]), np.array([valid]))
        tpo = []
        for width, cells in self.visits.items():
            count = (self.end - self.start + width - 1) // width
            brackets, incidence = [], {}
            for number in range(count):
                a, b = self.start + number * width, min(self.end, self.start + (number + 1) * width)
                complete = (_cover(intervals, a, b) and not self.unpriced_by_bracket[width].get(number, 0)
                            and not self.invalid_by_bracket[width].get(number, 0))
                brackets.append({'bracket': number, 'start_ns': a, 'end_ns': b,
                    'history_complete': complete, 'unpriced_prints': self.unpriced_by_bracket[width].get(number, 0),
                    'invalidating_rows': self.invalid_by_bracket[width].get(number, 0)})
            for (bracket, row), address in sorted(cells.items()):
                incidence.setdefault(row, []).append(bracket)
            histogram = {r: len(ids) for r, ids in incidence.items()}
            span_ok = not histogram or max(histogram) - min(histogram) < self.maximum_cells
            areas = {str(fraction): value_area(histogram, fraction=fraction, tie_rule='lower') if span_ok else None
                     for fraction in (Fraction(68, 100), Fraction(7, 10))}
            singles = tuple(sorted(r for r, ids in incidence.items() if len(ids) == 1))
            complete = all(row['history_complete'] for row in brackets)
            ready = sum(row['history_complete'] for row in brackets) >= minimum_brackets
            tpo.append({'bracket_width_ns': width, 'brackets': brackets,
                'row_bracket_incidence': tuple((r, tuple(ids)) for r, ids in sorted(incidence.items())),
                'first_visits': tuple((b, r, *address) for (b, r), address in sorted(cells.items())),
                'value_areas': areas, 'geometry_span_supported': span_ok, 'history_complete': complete,
                'source_display_ready': ready, 'final': True, 'provisional_single_rows': singles,
                'confirmed_single_rows': singles if complete and ready else None,
                'observed_tails': _tails(incidence), 'confirmed_tails': _tails(incidence) if complete and ready else None,
                'representation': 'actual_eligible_trade_bracket_visits', 'minimum_completed_brackets': minimum_brackets})
        dwell = []
        for cap, cells in self.dwell.items():
            mass = sum(cells.values())
            if not 0 <= mass <= self.end - self.start:
                raise IntegrityError("dwell assigned more than the actual elapsed window")
            dwell.append({'stale_cap_ns': cap, 'atomic_duration_ns_by_row': tuple((b, r, v) for (b, r), v in sorted(cells.items())),
                'observed_assigned_duration_ns': mass, 'unassigned_duration_ns': self.end - self.start - mass,
                'history_complete': _cover(intervals, self.start, self.end) and not self.unpriced_prints and not self.invalidating_rows,
                'representation': 'last_observed_trade_price_with_stale_cap',
                'true_per_row_lower_ns': 0 if _cover(intervals, self.start, self.end) else None,
                'true_per_row_upper_ns': self.end - self.start if _cover(intervals, self.start, self.end) else None})
        return {'version': VERSION, 'instrument_id': self.instrument_id, 'start_ns': self.start, 'end_ns': self.end,
            'known_at_ns': self.end + self.latency, 'row_ticks': self.width, 'origin_ticks': self.origin,
            'atomic_width_ns': self.atomic_width, 'eligible_prints': self.eligible_prints,
            'initial_observed_dwell_state': self.initial_state,
            'terminal_observed_dwell_state': self.last_state, 'terminal_raw_event': self.last_raw,
            'unpriced_prints': self.unpriced_prints, 'invalidating_rows': self.invalidating_rows,
            'covered_source_coordinate_intervals': intervals, 'tpo': tpo, 'dwell': dwell,
            'initial_balance': {'formation_ns': self.initial_balance_ns, 'event_end_ns': self.ib_end,
                'known_at_ns': self.ib_end + self.latency, 'observed_low_ticks': self.ib_low,
                'observed_high_ticks': self.ib_high,
                'formation_complete': self.end - self.start >= self.initial_balance_ns,
                'history_complete': _cover(intervals, self.start, self.ib_end) and not self.ib_unpriced and not self.ib_invalid,
                'nonempty': self.ib_low is not None, 'source': 'actual eligible prints in the explicitly declared initial window'},
            'order_basis': 'original source storage order; exchange sequence and strategy receipt are unavailable',
            'true_residence_claim': False, 'exact_subatomic_reconstruction': 'retained ordered trades and original raw invalidations'}
