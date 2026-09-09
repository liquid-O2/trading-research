"""Ordered native-cadence trade/quote channels computed during the raw scan.

The 100 ms grid is an explicit measurement clock, not event-time reconstruction
from minute bars. Exact event order supplies cumulative OHLC and quote pressure.
Unavailable cells remain masked; their initialized zeros never certify quiet.
"""
from __future__ import annotations

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_measurements import SOURCE_FILTERS
from trading_research.measurements.cvd import fixed_source_cohort


VERSION = "auction-flow-native-cadence-v1"
FLOW_FIELDS = ('volume', 'unknown', 'prints', 'close', 'high', 'low', 'high_at_ns', 'low_at_ns',
               'high_source_order', 'low_source_order')
QUOTE_FIELDS = ('quote_rows', 'fresh_quotes', 'pressure_transitions', 'ofi_close', 'ofi_high', 'ofi_low',
                'ofi_high_at_ns', 'ofi_low_at_ns', 'ofi_high_source_order', 'ofi_low_source_order',
                'same_price_ofi', 'price_change_ofi', 'standing_ns')
PRICE_FIELDS = ('priced_prints', 'first_price_ticks', 'last_price_ticks', 'high_price_ticks', 'low_price_ticks',
                'first_trade_at_ns', 'last_trade_at_ns', 'high_price_at_ns', 'low_price_at_ns',
                'first_trade_source_order', 'last_trade_source_order', 'high_price_source_order', 'low_price_source_order')


def _clock_count(start, end, width):
    if (any(type(v) is not int for v in (start, end, width))
            or not 0 <= start < end < 2**63 - 1_000_000_000 or width < 1):
        raise ContractError('bounded native event clock required')
    count = (end - start + width - 1) // width
    if count > 1_000_000:
        raise ContractError('native measurement exceeds its finite cadence-cell capacity')
    return count


def _integers(*arrays):
    import numpy as np

    if (any(not isinstance(a, np.ndarray) or a.ndim != 1 or a.dtype.kind not in 'iu' for a in arrays)
            or any(len(a) != len(arrays[0]) for a in arrays)
            or any(np.any(a > 2**63 - 1) for a in arrays)):
        raise IntegrityError('equal one-dimensional exact int64-domain event arrays required')


def _open(method):
    # Any partial mutation invalidates the complete measurement publication.
    def call(self, *args, **kwargs):
        if self._failed or self._closed:
            raise IntegrityError('failed or published native measurements cannot resume')
        try:
            return method(self, *args, **kwargs)
        except BaseException:
            self._failed = True
            raise
    return call


def _groups(bins):
    import numpy as np

    starts = np.r_[0, np.flatnonzero(bins[1:] != bins[:-1]) + 1]
    return starts, np.r_[starts[1:], len(bins)], bins[starts]


def _add_sum(destination, bins, values):
    import numpy as np

    if len(bins):
        starts, _, unique = _groups(bins)
        destination[unique] += np.add.reduceat(values, starts)


def _ordered_path(columns, bins, increments, at, order, *, prefix):
    import numpy as np

    if not len(bins):
        return
    starts, ends, unique = _groups(bins)
    cumulative = np.cumsum(increments, dtype=np.int64)
    before = cumulative[starts] - increments[starts]
    path = cumulative - np.repeat(before, ends - starts) + columns[prefix + 'close'][bins]
    hi, lo = np.maximum.reduceat(path, starts), np.minimum.reduceat(path, starts)
    index = np.arange(len(path), dtype=np.int64)
    high_index = np.minimum.reduceat(np.where(path == np.repeat(hi, ends - starts), index, len(path)), starts)
    low_index = np.minimum.reduceat(np.where(path == np.repeat(lo, ends - starts), index, len(path)), starts)
    new_high, new_low = hi > columns[prefix + 'high'][unique], lo < columns[prefix + 'low'][unique]
    columns[prefix + 'high_at_ns'][unique[new_high]] = at[high_index[new_high]]
    columns[prefix + 'low_at_ns'][unique[new_low]] = at[low_index[new_low]]
    columns[prefix + 'high_source_order'][unique[new_high]] = order[high_index[new_high]]
    columns[prefix + 'low_source_order'][unique[new_low]] = order[low_index[new_low]]
    columns[prefix + 'high'][unique] = np.maximum(columns[prefix + 'high'][unique], hi)
    columns[prefix + 'low'][unique] = np.minimum(columns[prefix + 'low'][unique], lo)
    columns[prefix + 'close'][unique] = path[ends - 1]


class NativeEventBins:
    def __init__(self, *, instrument_id, start_ns, end_ns, width_ns=100_000_000):
        import numpy as np

        if type(instrument_id) is not int or not 0 < instrument_id < 2**63:
            raise ContractError("bounded native event clock and raw instrument required")
        self.instrument_id, self.start, self.end, self.width = instrument_id, start_ns, end_ns, width_ns
        self.count = _clock_count(start_ns, end_ns, width_ns)
        names = [name + '__' + field for name in SOURCE_FILTERS for field in FLOW_FIELDS] + list(QUOTE_FIELDS) + list(PRICE_FIELDS)
        self.columns = {name: np.zeros(self.count, dtype=np.int64) for name in names}
        for name in names:
            if name.endswith('_at_ns') or name.endswith('_source_order'):
                self.columns[name].fill(-1)
        self.columns['duration_imbalance_ns'] = np.zeros(self.count, dtype=np.longdouble)
        self.columns['duration_spread_ticks_ns'] = np.zeros(self.count, dtype=np.longdouble)
        self._last_trade_order = self._last_quote_order = None
        self._last_trade_at = self._last_quote_at = self._last_exposure_end = None
        self._trade_count = self._quote_count = 0
        self._failed = self._closed = False
        self.filters = {}
        for name in SOURCE_FILTERS:
            if name == 'all':
                self.filters[name] = (1, None)
            else:
                included, = [c for c in fixed_source_cohort(name).channels if c.id == 'included']
                self.filters[name] = (included.lower_inclusive, included.upper_exclusive)

    @staticmethod
    def required_array_bytes(*, start_ns, end_ns, width_ns):
        import numpy as np

        count = _clock_count(start_ns, end_ns, width_ns)
        return count * (8 * (len(SOURCE_FILTERS) * len(FLOW_FIELDS) + len(QUOTE_FIELDS) + len(PRICE_FIELDS))
                        + 2 * np.dtype(np.longdouble).itemsize)

    @property
    def array_bytes(self):
        return sum(values.nbytes for values in self.columns.values())

    def indices(self, at):
        import numpy as np

        _integers(at)
        if (np.any(at < self.start) or np.any(at >= self.end)
                or np.any(at[1:] < at[:-1])):
            raise IntegrityError("native measurement event clock is outside its original ordered window")
        return (at.astype(np.int64) - self.start) // self.width

    @_open
    def add_trades(self, table):
        self._add_trades(table)

    def _add_trades(self, table):
        import numpy as np

        if not len(table):
            return
        at, size, side, price, valid, order = (table[name].to_numpy(zero_copy_only=False)
            for name in ('t', 'size', 'side', 'price', 'price_valid', 'source_order'))
        _integers(at, size, side, price, valid, order)
        at, size, side, price, valid, order = (v.astype(np.int64, copy=False) for v in (at, size, side, price, valid, order))
        bins = self.indices(at)
        if (np.any(table['instrument_id'].to_numpy(zero_copy_only=False) != self.instrument_id)
                or np.any(size <= 0) or np.any(size >= 2**32 - 1) or np.any(~np.isin(side, (-1, 0, 1)))
                or np.any(~np.isin(valid, (0, 1))) or np.any(order < 0) or np.any(order[1:] <= order[:-1])
                or self._trade_count + len(at) > 50_000_000
                or self._last_trade_order is not None and (int(order[0]) <= self._last_trade_order
                                                           or int(at[0]) < self._last_trade_at)):
            raise IntegrityError("native trade cells require the original eligible ordered population")
        self._last_trade_order = int(order[-1])
        self._last_trade_at = int(at[-1])
        self._trade_count += len(at)
        selected = {name: (size >= lower) & (True if upper is None else size < upper)
                    for name, (lower, upper) in self.filters.items()}
        c = self.columns
        first, ends, unique = _groups(bins)
        new = c['all__prints'][unique] == 0
        c['first_price_ticks'][unique[new]] = np.where(valid[first[new]], price[first[new]], 0)
        c['first_trade_at_ns'][unique[new]] = at[first[new]]
        c['first_trade_source_order'][unique[new]] = order[first[new]]
        c['last_price_ticks'][unique] = np.where(valid[ends - 1], price[ends - 1], 0)
        c['last_trade_at_ns'][unique] = at[ends - 1]
        c['last_trade_source_order'][unique] = order[ends - 1]
        for name, keep in selected.items():
            b, q, s, t = bins[keep], size[keep], side[keep], at[keep]
            for field, values in (('volume', q), ('unknown', np.where(s == 0, q, 0)), ('prints', np.ones(len(q), dtype=np.int64))):
                _add_sum(c[name + '__' + field], b, values)
            _ordered_path(c, b, q * s, t, order[keep], prefix=name + '__')
        keep = valid.astype(bool)
        if np.any(keep):
            b, p, t = bins[keep], price[keep], at[keep]
            if np.any((p <= 0) | (p >= 2**53)):
                raise IntegrityError("native trade geometry left the exact tick domain")
            starts, ends, unique = _groups(b)
            hi, lo = np.maximum.reduceat(p, starts), np.minimum.reduceat(p, starts)
            idx = np.arange(len(p))
            high_at = np.minimum.reduceat(np.where(p == np.repeat(hi, ends - starts), idx, len(p)), starts)
            low_at = np.minimum.reduceat(np.where(p == np.repeat(lo, ends - starts), idx, len(p)), starts)
            high = hi > c['high_price_ticks'][unique]
            low = (c['priced_prints'][unique] == 0) | (lo < c['low_price_ticks'][unique])
            c['high_price_ticks'][unique[high]] = hi[high]
            c['high_price_at_ns'][unique[high]] = t[high_at[high]]
            c['high_price_source_order'][unique[high]] = order[keep][high_at[high]]
            c['low_price_ticks'][unique[low]] = lo[low]
            c['low_price_at_ns'][unique[low]] = t[low_at[low]]
            c['low_price_source_order'][unique[low]] = order[keep][low_at[low]]
            c['priced_prints'][unique] += ends - starts

    @_open
    def quote_updates(self, *, at, order, fresh, measured, ofi, same):
        import numpy as np

        _integers(at, order)
        _integers(ofi, same)
        if (any(not isinstance(a, np.ndarray) or a.ndim != 1 or a.dtype != bool or len(a) != len(at)
                for a in (fresh, measured)) or np.any(measured & ~fresh)
                or len(ofi) != np.count_nonzero(measured) or np.any(ofi < -4 * (2**32 - 2))
                or np.any(ofi > 4 * (2**32 - 2)) or np.any(same < -2 * (2**32 - 2))
                or np.any(same > 2 * (2**32 - 2)) or self._quote_count + len(at) > 50_000_000):
            raise IntegrityError('native quote transitions differ from their bounded measured population')
        at, order, ofi, same = (a.astype(np.int64, copy=False) for a in (at, order, ofi, same))
        if not len(at):
            return
        bins = self.indices(at)
        if (np.any(order < 0) or np.any(order[1:] <= order[:-1])
                or self._last_quote_order is not None and (int(order[0]) <= self._last_quote_order
                                                           or int(at[0]) < self._last_quote_at)):
            raise IntegrityError("native quote projection repeated or changed source order")
        self._last_quote_order = int(order[-1])
        self._last_quote_at = int(at[-1])
        self._quote_count += len(at)
        self._fill_quote_updates(bins, at, order, fresh, measured, ofi, same)

    @_open
    def quote_exposure(self, *, starts, ends, bid, ask, bid_size, ask_size):
        import numpy as np

        _integers(starts, ends, bid, ask, bid_size, ask_size)
        starts, ends, bid, ask, bid_size, ask_size = (a.astype(np.int64, copy=False)
            for a in (starts, ends, bid, ask, bid_size, ask_size))
        if not len(starts):
            return
        if (np.any(starts < self.start) or np.any(ends > self.end) or np.any(ends <= starts)
                or np.any(starts[1:] < ends[:-1])
                or self._last_exposure_end is not None and int(starts[0]) < self._last_exposure_end
                or np.any(bid <= 0) or np.any(ask >= 2**53) or np.any(ask < bid)
                or np.any(bid_size <= 0) or np.any(ask_size <= 0)
                or np.any(bid_size >= 2**32 - 1) or np.any(ask_size >= 2**32 - 1)):
            raise IntegrityError("native quote exposure exceeds its actual observed intervals")
        self._last_exposure_end = int(ends[-1])
        from trading_research.data.compact_native import reduce_quote_exposure
        if reduce_quote_exposure(
                starts, ends, bid, ask, bid_size, ask_size,
                start=self.start, end=self.end, width=self.width,
                standing_ns=self.columns['standing_ns'],
                duration_imbalance_ns=self.columns['duration_imbalance_ns'],
                duration_spread_ticks_ns=self.columns['duration_spread_ticks_ns']):
            return
        self._fill_quote_exposure(starts, ends, bid, ask, bid_size, ask_size)

    def _fill_quote_updates(self, bins, at, order, fresh, measured, ofi, same):
        import numpy as np

        _add_sum(self.columns['quote_rows'], bins, np.ones(len(bins), dtype=np.int64))
        _add_sum(self.columns['fresh_quotes'], bins, fresh.astype(np.int64))
        idx = np.flatnonzero(measured)
        if len(idx):
            _add_sum(self.columns['pressure_transitions'], bins[idx], np.ones(len(idx), dtype=np.int64))
            _add_sum(self.columns['same_price_ofi'], bins[idx], same)
            _add_sum(self.columns['price_change_ofi'], bins[idx], ofi - same)
            _ordered_path(self.columns, bins[idx], ofi, at[idx], order[idx], prefix='ofi_')

    def _fill_quote_exposure(self, starts, ends, bid, ask, bid_size, ask_size):
        import numpy as np

        first, last = (starts - self.start) // self.width, (ends - 1 - self.start) // self.width
        same = first == last
        index = np.flatnonzero(same)
        crossing = np.flatnonzero(~same)
        counts = last[crossing] - first[crossing] + 1
        offsets = np.cumsum(counts, dtype=np.int64) - counts
        extra_index = np.repeat(crossing, counts)
        extra_bin = (np.repeat(first[crossing] - offsets, counts)
                     + np.arange(len(extra_index), dtype=np.int64))
        extra_start = self.start + extra_bin * self.width
        extra_duration = (np.minimum(ends[extra_index], extra_start + self.width)
                          - np.maximum(starts[extra_index], extra_start))
        bins = np.r_[first[same], extra_bin]
        duration = np.r_[(ends - starts)[same], extra_duration]
        source = np.r_[index, extra_index]
        order = np.argsort(bins, kind='stable')
        bins, duration, source = bins[order], duration[order], source[order]
        imbalance = (bid_size[source].astype(np.longdouble) - ask_size[source]) / (bid_size[source].astype(np.longdouble) + ask_size[source])
        _add_sum(self.columns['standing_ns'], bins, duration)
        _add_sum(self.columns['duration_imbalance_ns'], bins, duration.astype(np.longdouble) * imbalance)
        _add_sum(self.columns['duration_spread_ticks_ns'], bins, duration.astype(np.longdouble) * (ask[source] - bid[source]))

    def _check_quote_updates(self, at, order, fresh, measured, ofi, same):
        import numpy as np

        _integers(at, order)
        _integers(ofi, same)
        if (any(not isinstance(a, np.ndarray) or a.ndim != 1 or a.dtype != bool or len(a) != len(at)
                for a in (fresh, measured)) or np.any(measured & ~fresh)
                or len(ofi) != np.count_nonzero(measured) or np.any(ofi < -4 * (2**32 - 2))
                or np.any(ofi > 4 * (2**32 - 2)) or np.any(same < -2 * (2**32 - 2))
                or np.any(same > 2 * (2**32 - 2)) or self._quote_count + len(at) > 50_000_000):
            raise IntegrityError('native quote transitions differ from their bounded measured population')
        at, order, ofi, same = (a.astype(np.int64, copy=False) for a in (at, order, ofi, same))
        if not len(at):
            return at, order, fresh, measured, ofi, same, None
        bins = self.indices(at)
        if (np.any(order < 0) or np.any(order[1:] <= order[:-1])
                or self._last_quote_order is not None and (int(order[0]) <= self._last_quote_order
                                                           or int(at[0]) < self._last_quote_at)):
            raise IntegrityError("native quote projection repeated or changed source order")
        return at, order, fresh, measured, ofi, same, bins

    def _check_quote_exposure(self, starts, ends, bid, ask, bid_size, ask_size):
        import numpy as np

        _integers(starts, ends, bid, ask, bid_size, ask_size)
        starts, ends, bid, ask, bid_size, ask_size = (a.astype(np.int64, copy=False)
            for a in (starts, ends, bid, ask, bid_size, ask_size))
        if not len(starts):
            return starts, ends, bid, ask, bid_size, ask_size
        if (np.any(starts < self.start) or np.any(ends > self.end) or np.any(ends <= starts)
                or np.any(starts[1:] < ends[:-1])
                or self._last_exposure_end is not None and int(starts[0]) < self._last_exposure_end
                or np.any(bid <= 0) or np.any(ask >= 2**53) or np.any(ask < bid)
                or np.any(bid_size <= 0) or np.any(ask_size <= 0)
                or np.any(bid_size >= 2**32 - 1) or np.any(ask_size >= 2**32 - 1)):
            raise IntegrityError("native quote exposure exceeds its actual observed intervals")
        return starts, ends, bid, ask, bid_size, ask_size

    @_open
    def apply_compiled_quote_channels(self, *, at, order, fresh, measured, ofi, same,
                                      starts, ends, bid, ask, bid_size, ask_size):
        import numpy as np
        from trading_research.data.compact_native import fuse_native_quote_updates, reduce_quote_exposure

        if fresh.dtype != bool:
            fresh = fresh.astype(bool, copy=False)
        if measured.dtype != bool:
            measured = measured.astype(bool, copy=False)
        at, order, fresh, measured, ofi, same, bins = self._check_quote_updates(
            at, order, fresh, measured, ofi, same)
        if len(starts):
            starts, ends, bid, ask, bid_size, ask_size = self._check_quote_exposure(
                starts, ends, bid, ask, bid_size, ask_size)
        if len(at):
            c = self.columns
            if fuse_native_quote_updates(
                    at, order, fresh, measured, ofi, same,
                    start=self.start, end=self.end, width=self.width,
                    quote_rows=c['quote_rows'], fresh_quotes=c['fresh_quotes'],
                    pressure_transitions=c['pressure_transitions'],
                    same_price_ofi=c['same_price_ofi'], price_change_ofi=c['price_change_ofi'],
                    ofi_close=c['ofi_close'], ofi_high=c['ofi_high'], ofi_low=c['ofi_low'],
                    ofi_high_at=c['ofi_high_at_ns'], ofi_low_at=c['ofi_low_at_ns'],
                    ofi_high_order=c['ofi_high_source_order'], ofi_low_order=c['ofi_low_source_order']):
                pass
            else:
                self._fill_quote_updates(bins, at, order, fresh, measured, ofi, same)
            self._last_quote_order = int(order[-1])
            self._last_quote_at = int(at[-1])
            self._quote_count += len(at)
        if len(starts):
            if not reduce_quote_exposure(
                    starts, ends, bid, ask, bid_size, ask_size,
                    start=self.start, end=self.end, width=self.width,
                    standing_ns=self.columns['standing_ns'],
                    duration_imbalance_ns=self.columns['duration_imbalance_ns'],
                    duration_spread_ticks_ns=self.columns['duration_spread_ticks_ns']):
                self._fill_quote_exposure(starts, ends, bid, ask, bid_size, ask_size)
            self._last_exposure_end = int(ends[-1])

    @_open
    def table(self, *, source_eligible, coordinate_eligible, latency_ns):
        import numpy as np
        import pyarrow as pa

        if (any(not isinstance(a, np.ndarray) or a.ndim != 1 or a.dtype != bool or len(a) != self.count
                for a in (source_eligible, coordinate_eligible))
                or type(latency_ns) is not int or not 0 <= latency_ns <= 1_000_000_000):
            raise IntegrityError("native measurement publication needs its exact completed quality masks")
        starts = self.start + np.arange(self.count, dtype=np.int64) * self.width
        ends = np.minimum(starts + self.width, self.end)
        c = self.columns
        if (np.any(c['standing_ns'] < 0) or np.any(c['standing_ns'] > ends - starts)
                or np.any(c['ofi_close'] != c['same_price_ofi'] + c['price_change_ofi'])):
            raise IntegrityError("native quote exposure or OFI decomposition does not reconcile")
        for name in SOURCE_FILTERS:
            if (np.any(c[name + '__high'] < c[name + '__close']) or np.any(c[name + '__low'] > c[name + '__close'])
                    or np.any(np.abs(c[name + '__close']) > c[name + '__volume'] - c[name + '__unknown'])):
                raise IntegrityError("native cohort cumulative path lost exact side mass or extrema")
        self._closed = True
        output = {name: values.astype(np.float64) if values.dtype.kind == 'f' else values for name, values in c.items()}
        output.update(event_start_ns=starts, event_end_ns=ends, known_at_ns=ends + latency_ns,
            instrument_id=np.full(self.count, self.instrument_id, dtype=np.int64),
            source_eligible=source_eligible, coordinate_eligible=coordinate_eligible,
            price_history_complete=source_eligible & coordinate_eligible & (c['priced_prints'] == c['all__prints']),
            quote_standing_complete=source_eligible & coordinate_eligible & (c['standing_ns'] == ends - starts),
            quote_pressure_complete=source_eligible & coordinate_eligible & (c['standing_ns'] == ends - starts)
                & (c['fresh_quotes'] == c['pressure_transitions']))
        return pa.table(output)


class NativeSourceOwnership:
    """Causal supplied-contract ownership and flags at the native measurement grid."""
    def __init__(self, *, start_ns, end_ns, width_ns, initial_owner=None):
        import numpy as np

        self.start, self.end, self.width = start_ns, end_ns, width_ns
        count = _clock_count(start_ns, end_ns, width_ns)
        if initial_owner is not None and (type(initial_owner) is not int or not 0 < initial_owner < 2**63):
            raise ContractError('preceding source owner must identify an actual raw instrument')
        self.initial_owner = 0 if initial_owner is None else initial_owner
        self.raw_count, self.ordinary_count, self.last = (np.zeros(count, dtype=np.int64) for _ in range(3))
        self.low, self.high = np.full(count, np.iinfo(np.int64).max), np.zeros(count, dtype=np.int64)
        self.invalid = np.zeros(count, dtype=bool)
        self._failed = self._closed = False
        self._last_order = self._last_at = None
        self._raw_count = 0

    @property
    def array_bytes(self):
        return sum(a.nbytes for a in (self.raw_count, self.ordinary_count, self.last, self.low, self.high, self.invalid))

    @_open
    def add(self, raw):
        import numpy as np
        import pyarrow as pa
        import pyarrow.compute as pc

        if not len(raw):
            return
        at, flags, instruments, order = (raw[name].to_numpy(zero_copy_only=False) for name in ('t', 'flags', 'instrument_id', 'source_order'))
        _integers(at, flags, instruments, order)
        if (np.any(at < self.start) or np.any(at >= self.end) or np.any(at[1:] < at[:-1])
                or np.any(flags < 0) or np.any(flags > 255) or np.any(instruments <= 0)
                or np.any(order < 0) or np.any(order[1:] <= order[:-1]) or self._raw_count + len(at) > 50_000_000
                or self._last_order is not None and (int(order[0]) <= self._last_order or int(at[0]) < self._last_at)):
            raise IntegrityError('native source ownership lost original ordered raw identity or clock')
        at, flags, instruments = (a.astype(np.int64, copy=False) for a in (at, flags, instruments))
        self._last_order, self._last_at = int(order[-1]), int(at[-1])
        self._raw_count += len(at)
        bins = (at - self.start) // self.width
        _add_sum(self.raw_count, bins, np.ones(len(bins), dtype=np.int64))
        actions = pc.cast(raw['action'], pa.string())
        known = pc.fill_null(pc.is_in(actions, value_set=pa.array(['A', 'M', 'C', 'R', 'T', 'N'])), False).to_numpy(zero_copy_only=False)
        trade = pc.fill_null(pc.equal(actions, 'T'), False).to_numpy(zero_copy_only=False)
        size_ok = pc.fill_null(pc.and_(pc.greater(raw['size'], 0), pc.less(raw['size'], 2**32 - 1)), False).to_numpy(zero_copy_only=False)
        ordinary = (flags & 32) == 0
        bad = ((flags & 4) != 0) | ~known | (trade & ordinary & ~size_ok)
        first, _, unique = _groups(bins)
        self.invalid[unique] |= np.logical_or.reduceat(bad, first)
        if np.any(ordinary):
            b, ids = bins[ordinary], instruments[ordinary]
            starts, ends, unique = _groups(b)
            self.ordinary_count[unique] += ends - starts
            self.last[unique] = ids[ends - 1]
            self.low[unique] = np.minimum(self.low[unique], np.minimum.reduceat(ids, starts))
            self.high[unique] = np.maximum(self.high[unique], np.maximum.reduceat(ids, starts))

    def owners(self):
        import numpy as np

        if self._failed:
            raise IntegrityError('failed native source ownership cannot certify coverage')
        seen = np.maximum.accumulate(np.where(self.ordinary_count > 0, np.arange(len(self.last)) + 1, 0))
        after = np.r_[self.initial_owner, self.last][seen]
        before = np.r_[self.initial_owner, after[:-1]]
        return before, after

    def eligible(self, instrument_id, intervals):
        import numpy as np

        if type(instrument_id) is not int or not 0 < instrument_id < 2**63:
            raise ContractError('exact positive source instrument required')
        starts = self.start + np.arange(len(self.last), dtype=np.int64) * self.width
        ends = np.minimum(starts + self.width, self.end)
        coverage = np.zeros(len(starts), dtype=bool)
        prior = None
        for a, b in intervals:
            if (type(a) is not int or type(b) is not int or not 0 <= a < b < 2**63
                    or prior is not None and a <= prior):
                raise IntegrityError('source eligibility requires normalized disjoint archive intervals')
            prior = b
            coverage |= (starts >= a) & (ends <= b)
        before, after = self.owners()
        ordinary = self.ordinary_count > 0
        presence = ordinary | ((self.raw_count == 0) & (before == instrument_id) & (after == instrument_id))
        stable = ((before == 0) | (before == instrument_id)) & (after == instrument_id)
        stable &= ~ordinary | ((self.low == instrument_id) & (self.high == instrument_id))
        return coverage & presence & stable & ~self.invalid
