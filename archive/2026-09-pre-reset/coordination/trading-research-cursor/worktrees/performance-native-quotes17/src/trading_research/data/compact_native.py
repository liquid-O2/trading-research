"""Fused C++ MBP projection and chronological quote-exposure reduction.

The registered runner builds and authenticates the shared library. Other
schemas retain the Arrow reference path. The kernel has no clock, holdings,
recovery or scientific-definition policy of its own.
"""
from __future__ import annotations

import ctypes
import hashlib
from pathlib import Path

from trading_research.errors import IntegrityError

_LIBRARY = None
_FUNCTION = None
_EXPOSURE = None
_FAST_CALLS = _FAST_ROWS = 0
_EXPOSURE_CALLS = _EXPOSURE_INTERVALS = _EXPOSURE_CELLS = 0

CPP_SOURCE = r'''
#include <cstdint>
#include <cmath>
#include <cstddef>

static inline int64_t ticks(double price, bool &valid) {
    const double scaled = price * 4.0;
    valid = std::isfinite(scaled) && scaled > 0.0 && scaled < 9007199254740992.0
        && scaled == std::floor(scaled);
    return valid ? static_cast<int64_t>(scaled) : 0;
}

extern "C" int project_mbp(
    int64_t n, const int64_t* at, const int16_t* flags, const int32_t* size,
    const double* bid_px, const double* ask_px, const double* price,
    const int32_t* bid_sz, const int32_t* ask_sz,
    const uint8_t* action, const uint8_t* side,
    int64_t instrument, int64_t first_order, int already_blocked,
    int64_t* quote, uint8_t* quote_bits, int64_t* trade, uint8_t* trade_bits,
    int64_t* stats) {
    // Python checks the exact primitive types, array extents and order bound.
    if (n < 0 || n > 65536 || instrument <= 0 || first_order < 0) return 1;
    for (int k = 0; k < 11; ++k) stats[k] = 0;
    stats[2] = -1;
    stats[10] = 1;
    bool blocked = already_blocked != 0;
    for (int64_t i = 0; i < n; ++i) {
        const int16_t flag = flags[i];
        const uint8_t a = action[i];
        const bool gap = (flag & 4) != 0, snapshot = (flag & 32) != 0;
        const bool unknown = a == 0, clear = a == 4, is_trade = a == 5;
        const bool invalidation = gap || unknown || clear;
        if (invalidation && stats[2] < 0) stats[2] = i;
        blocked = blocked || invalidation;
        stats[3] += gap;
        stats[4] += is_trade && snapshot;
        if (gap || unknown || (is_trade && !snapshot && size[i] <= 0)) stats[10] = 0;
        if ((a >= 1 && a <= 3) || invalidation) {
            const int64_t q = stats[0]++;
            bool bv, av;
            const int64_t bid = ticks(bid_px[i], bv), ask = ticks(ask_px[i], av);
            quote[0*n+q] = at[i];
            quote[1*n+q] = first_order+i;
            quote[2*n+q] = instrument;
            quote[3*n+q] = bid;
            quote[4*n+q] = ask;
            quote[5*n+q] = bid_sz[i];
            quote[6*n+q] = ask_sz[i];
            quote_bits[0*n+q] = !blocked && bv && av && bid < ask && bid_sz[i] > 0 && ask_sz[i] > 0;
            quote_bits[1*n+q] = snapshot;
        }
        if (is_trade && !snapshot && size[i] > 0) {
            const int64_t t = stats[1]++;
            bool pv;
            const int64_t px = ticks(price[i], pv);
            const int64_t sign = side[i] == 1 ? 1 : side[i] == 2 ? -1 : 0;
            trade[0*n+t] = at[i];
            trade[1*n+t] = first_order+i;
            trade[2*n+t] = instrument;
            trade[3*n+t] = px;
            trade[4*n+t] = size[i];
            trade[5*n+t] = sign;
            trade_bits[t] = pv;
            stats[5] += size[i];
            stats[6] += sign == 1 ? size[i] : 0;
            stats[7] += sign == -1 ? size[i] : 0;
            stats[8] += sign == 0 ? size[i] : 0;
            stats[9] += !pv ? size[i] : 0;
        }
    }
    return 0;
}

extern "C" int64_t reduce_quote_exposure(
    int64_t n, const int64_t* starts, const int64_t* ends,
    const int64_t* bid, const int64_t* ask, const int64_t* bid_size, const int64_t* ask_size,
    int64_t grid_start, int64_t grid_end, int64_t width, int64_t cell_count,
    int64_t* standing_ns, long double* duration_imbalance_ns, long double* duration_spread_ticks_ns) {
    // Python keeps economic, order and poisoning checks. Reject before any write.
    if (n < 0 || n > 50000000 || cell_count < 0 || cell_count > 1000000 || width < 1) return -1;
    if (grid_start < 0 || grid_end <= grid_start
            || grid_end > 9223372036854775807LL - 1000000000LL) return -1;
    if (((__int128)grid_end - grid_start + width - 1) / width != (__int128)cell_count) return -1;
    int64_t touched = 0;
    for (int64_t i = 0; i < n; ++i) {
        if (bid[i] <= 0 || ask[i] >= 9007199254740992LL || ask[i] < bid[i]
                || bid_size[i] <= 0 || ask_size[i] <= 0
                || bid_size[i] >= 4294967295LL || ask_size[i] >= 4294967295LL) return -1;
        if (starts[i] < grid_start || ends[i] > grid_end || ends[i] <= starts[i]) return -1;
        if (i > 0 && starts[i] < ends[i - 1]) return -1;
        const int64_t first = (starts[i] - grid_start) / width;
        const int64_t last = (ends[i] - 1 - grid_start) / width;
        if (first < 0 || last < first || last >= cell_count) return -1;
        touched += last - first + 1;
    }
    for (int64_t i = 0; i < n; ++i) {
        const int64_t first = (starts[i] - grid_start) / width;
        const int64_t last = (ends[i] - 1 - grid_start) / width;
        const long double qb = (long double)bid_size[i], qa = (long double)ask_size[i];
        const long double imbalance = (qb - qa) / (qb + qa);
        const long double spread = (long double)(ask[i] - bid[i]);
        for (int64_t bin = first; bin <= last; ++bin) {
            const __int128 cell_start = (__int128)grid_start + (__int128)bin * width;
            __int128 cell_end = cell_start + width;
            if (cell_end > grid_end) cell_end = grid_end;
            const __int128 left = starts[i] > cell_start ? (__int128)starts[i] : cell_start;
            const __int128 right = ends[i] < cell_end ? (__int128)ends[i] : cell_end;
            if (right <= left) continue;
            const int64_t duration = (int64_t)(right - left);
            standing_ns[bin] += duration;
            duration_imbalance_ns[bin] += (long double)duration * imbalance;
            duration_spread_ticks_ns[bin] += (long double)duration * spread;
        }
    }
    return touched;
}
'''


def enable_compiled_projection(path, expected_sha256):
    """Called only after compilation inside the registered, bounded attempt."""
    global _LIBRARY, _FUNCTION, _EXPOSURE
    import numpy as np

    path = Path(path)
    if path.stat().st_size > 16 * 1024**2 or hashlib.sha256(path.read_bytes()).hexdigest() != expected_sha256:
        raise IntegrityError('compiled projection artifact differs from its registered build')
    library = ctypes.CDLL(str(path))
    function = library.project_mbp
    def array(dtype):
        return np.ctypeslib.ndpointer(dtype=dtype, flags='C_CONTIGUOUS')
    function.argtypes = [ctypes.c_int64, array(np.int64), array(np.int16), array(np.int32),
        array(np.float64), array(np.float64), array(np.float64), array(np.int32), array(np.int32),
        array(np.uint8), array(np.uint8), ctypes.c_int64, ctypes.c_int64, ctypes.c_int,
        array(np.int64), array(np.uint8), array(np.int64), array(np.uint8), array(np.int64)]
    function.restype = ctypes.c_int
    exposure = library.reduce_quote_exposure
    in64 = np.ctypeslib.ndpointer(dtype=np.int64, ndim=1, flags='ALIGNED, C_CONTIGUOUS')
    out64 = np.ctypeslib.ndpointer(dtype=np.int64, ndim=1, flags='ALIGNED, C_CONTIGUOUS, WRITEABLE')
    outld = np.ctypeslib.ndpointer(dtype=np.longdouble, ndim=1, flags='ALIGNED, C_CONTIGUOUS, WRITEABLE')
    exposure.argtypes = [ctypes.c_int64, in64, in64, in64, in64, in64, in64,
        ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, out64, outld, outld]
    exposure.restype = ctypes.c_int64
    _LIBRARY, _FUNCTION = library, function
    _EXPOSURE = exposure if np.dtype(np.longdouble).itemsize == ctypes.sizeof(ctypes.c_longdouble) else None


def project_part(part, *, instrument, first_order, blocked):
    """Return exact acquired-schema quote/trade projections, or use reference.

    Null categorical values are unknown categories. Null numeric columns and
    different primitive types use the original reference implementation.
    Arrays backing the Arrow output remain owned by its buffers.
    """
    global _FAST_CALLS, _FAST_ROWS
    if _FUNCTION is None:
        return None
    import numpy as np
    import pyarrow as pa

    expected = {'t': pa.int64(), 'flags': pa.int16(), 'size': pa.int32(),
                'bid_px': pa.float64(), 'ask_px': pa.float64(), 'price': pa.float64(),
                'bid_sz': pa.int32(), 'ask_sz': pa.int32(), 'instrument_id': pa.int32()}
    n = len(part)
    if (not 0 < n <= 65536 or not 0 <= first_order <= 2**63-1-n
            or any(part.schema.field(name).type != dtype or part[name].null_count
                   for name, dtype in expected.items())):
        return None
    if any(not (pa.types.is_string(part.schema.field(name).type)
                    or pa.types.is_dictionary(part.schema.field(name).type)
                    and pa.types.is_string(part.schema.field(name).type.value_type))
           for name in ('action', 'side')):
        return None
    def codes(name, mapping):
        value = part[name].combine_chunks()
        if not pa.types.is_dictionary(value.type):
            value = value.dictionary_encode()
        keys = value.dictionary.to_pylist()
        # Fill null indices with a dedicated last entry; no category conflation.
        positions = value.indices.cast(pa.int64()).fill_null(len(keys)).to_numpy(zero_copy_only=False)
        lookup = np.array([mapping.get(key, 0) for key in keys] + [0], dtype=np.uint8)
        return np.ascontiguousarray(lookup[positions])
    actions = codes('action', {'A':1, 'M':2, 'C':3, 'R':4, 'T':5, 'N':6})
    sides = codes('side', {'B':1, 'A':2})
    arrays = [np.ascontiguousarray(part[name].to_numpy(zero_copy_only=False)) for name in
              ('t', 'flags', 'size', 'bid_px', 'ask_px', 'price', 'bid_sz', 'ask_sz')]
    q = np.empty((7, n), dtype=np.int64)
    qb = np.empty((2, n), dtype=np.uint8)
    t = np.empty((6, n), dtype=np.int64)
    tb = np.empty(n, dtype=np.uint8)
    stats = np.empty(11, dtype=np.int64)
    result = _FUNCTION(n, *arrays, actions, sides, instrument, first_order, int(blocked), q, qb, t, tb, stats)
    if result:
        raise IntegrityError('compiled projection rejected its bounded input domain')
    nq, nt = int(stats[0]), int(stats[1])
    quote = pa.table({name: q[k,:nq] for k, name in enumerate(
        ('t','source_order','instrument_id','bid','ask','bid_size','ask_size'))})
    # The reference retains the raw instrument_id type, rather than int64.
    quote = quote.set_column(2, 'instrument_id', quote['instrument_id'].cast(pa.int32()))
    quote = quote.append_column('book_valid', pa.array(qb[0,:nq])).append_column('snapshot', pa.array(qb[1,:nq]))
    trade = pa.table({name: t[k,:nt] for k, name in enumerate(
        ('t','source_order','instrument_id','price','size','side'))})
    trade = trade.set_column(2, 'instrument_id', trade['instrument_id'].cast(pa.int32()))
    trade = trade.append_column('price_valid', pa.array(tb[:nt]))
    counts = dict(zip(('gap_rows','snapshot_trade_rows','volume','buy_volume','sell_volume','unknown_volume','unpriced_volume'),
                      (int(value) for value in stats[3:10]), strict=True))
    counts.update(trades=nt, quote_rows=nq)
    _FAST_CALLS += 1
    _FAST_ROWS += n
    return quote, trade, int(stats[2]), bool(stats[10]), counts


def reduce_quote_exposure(starts, ends, bid, ask, bid_size, ask_size, *,
                          start, end, width,
                          standing_ns, duration_imbalance_ns, duration_spread_ticks_ns):
    """Add validated half-open quote intervals onto the declared grid.

    Returns True only when the compiled reducer actually wrote. False leaves
    the output arrays untouched so the NumPy reference path can run.
    """
    global _EXPOSURE_CALLS, _EXPOSURE_INTERVALS, _EXPOSURE_CELLS
    if _EXPOSURE is None:
        return False
    import numpy as np

    if (any(type(v) is not int for v in (start, end, width))
            or not 0 <= start < end < 2**63 - 1_000_000_000 or not 1 <= width < 2**63):
        return False
    inputs = (starts, ends, bid, ask, bid_size, ask_size)
    outputs = (standing_ns, duration_imbalance_ns, duration_spread_ticks_ns)
    if (any(not isinstance(a, np.ndarray) or a.ndim != 1 or a.dtype != np.int64 for a in inputs)
            or any(len(a) != len(starts) for a in inputs)
            or any(not isinstance(a, np.ndarray) or a.ndim != 1 for a in outputs)
            or len(duration_imbalance_ns) != len(standing_ns)
            or len(duration_spread_ticks_ns) != len(standing_ns)
            or standing_ns.dtype != np.int64
            or duration_imbalance_ns.dtype != np.dtype(np.longdouble)
            or duration_spread_ticks_ns.dtype != np.dtype(np.longdouble)
            or np.dtype(np.longdouble).itemsize != ctypes.sizeof(ctypes.c_longdouble)):
        return False
    cell_count = len(standing_ns)
    if cell_count != (end - start + width - 1) // width or cell_count > 1_000_000:
        return False
    if any(not (a.flags.c_contiguous and a.flags.aligned and a.flags.writeable) for a in outputs):
        return False
    starts, ends, bid, ask, bid_size, ask_size = (
        np.require(a, requirements=('C', 'ALIGNED')) for a in inputs)
    n = int(len(starts))
    status = _EXPOSURE(n, starts, ends, bid, ask, bid_size, ask_size,
                       start, end, width, cell_count,
                       standing_ns, duration_imbalance_ns, duration_spread_ticks_ns)
    if status < 0:
        raise IntegrityError('compiled quote exposure rejected its bounded input domain')
    _EXPOSURE_CALLS += 1
    _EXPOSURE_INTERVALS += n
    _EXPOSURE_CELLS += status
    return True


def execution_counts():
    return {'fused_batches': _FAST_CALLS, 'fused_rows': _FAST_ROWS,
            'compiled_exposure_calls': _EXPOSURE_CALLS,
            'compiled_exposure_intervals': _EXPOSURE_INTERVALS,
            'compiled_exposure_cells': _EXPOSURE_CELLS}
