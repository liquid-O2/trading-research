"""Fused C++ MBP projection for the exact acquired primitive schema.

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
'''


def enable_compiled_projection(path, expected_sha256):
    """Called only after compilation inside the registered, bounded attempt."""
    global _LIBRARY, _FUNCTION
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
    _LIBRARY, _FUNCTION = library, function


def project_part(part, *, instrument, first_order, blocked):
    """Return exact acquired-schema quote/trade projections, or use reference.

    Null categorical values are unknown categories. Null numeric columns and
    different primitive types use the original reference implementation.
    Arrays backing the Arrow output remain owned by its buffers.
    """
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
        positions = value.indices.fill_null(len(keys)).to_numpy(zero_copy_only=False)
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
    return quote, trade, int(stats[2]), bool(stats[10]), counts
