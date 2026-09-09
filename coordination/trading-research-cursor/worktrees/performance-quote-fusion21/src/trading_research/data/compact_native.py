"""Fused C++ MBP projection, quote-slice terms and chronological exposure.

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
_SLICE = None
_NATIVE_QUOTES = None
_FAST_CALLS = _FAST_ROWS = 0
_EXPOSURE_CALLS = _EXPOSURE_INTERVALS = _EXPOSURE_CELLS = 0
_SLICE_CALLS = _SLICE_ROWS = 0
_NATIVE_QUOTE_CALLS = _NATIVE_QUOTE_ROWS = 0

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

static inline int64_t floor_div_int64(__int128 num, int64_t den) {
    __int128 q = num / den, r = num % den;
    if (r != 0 && num < 0) --q;
    return (int64_t)q;
}

extern "C" int fuse_quote_slice(
    int64_t n,
    const int64_t* t, const int64_t* order, const int64_t* bid, const int64_t* ask,
    const int64_t* bid_size, const int64_t* ask_size, const int64_t* flags,
    const uint8_t* valid, const uint8_t* snapshot, const uint8_t* updates, const uint8_t* clears,
    const int64_t* prev, const int64_t* win,
    int64_t* exp_starts, int64_t* exp_ends, int64_t* exp_bid, int64_t* exp_ask,
    int64_t* exp_qb, int64_t* exp_qa, int64_t* exp_duration,
    long double* exp_dur_imbalance, long double* exp_dur_spread, int64_t* exp_mid,
    int64_t* meas_ofi, int64_t* meas_same,
    long double* meas_depth, long double* meas_imbalance, long double* meas_micro,
    int64_t* meas_spread, uint8_t* fresh_out, uint8_t* measured_out, int64_t* stats) {
    if (n < 1 || n > 50000000) return 1;
    const int64_t window_start = win[0], window_end = win[1], maximum_age = win[2];
    const int64_t origin = win[3], row_ticks = win[4], has_previous = win[5];
    const int64_t origin_abs = origin < 0 ? -origin : origin;
    if (window_start < 0 || window_end <= window_start
            || window_end > 9223372036854775807LL - 1000000000LL
            || row_ticks < 1 || row_ticks > 1024 || origin_abs >= 9007199254740992LL)
        return 1;
    const int64_t prev_t = prev[0], prev_bid = prev[1], prev_ask = prev[2];
    const int64_t prev_qb = prev[3], prev_qa = prev[4], prev_valid = prev[5], prev_economic = prev[6];
    const int64_t twice_row = row_ticks * 2;
    int64_t n_keep = 0, n_meas = 0;
    int64_t fresh_count = 0, invalid_count = 0, snap_count = 0, gap_count = 0, clear_count = 0, equal_count = 0;
    int64_t ofi_sum = 0, same_sum = 0, price_sum = 0, pos_upd = 0, dur_sum = 0, pos_dur = 0;
    int64_t path = 0, best_hi = 0, best_lo = 0, hi_at = 0, hi_ord = 0, lo_at = 0, lo_ord = 0;
    int64_t current_econ = has_previous ? prev_economic : -1;
    int64_t before_econ = current_econ;
    int64_t latest_src = -1;
    int64_t lag_t = has_previous ? prev_t : window_start;
    int64_t lag_bid = has_previous ? prev_bid : 0, lag_ask = has_previous ? prev_ask : 0;
    int64_t lag_qb = has_previous ? prev_qb : 0, lag_qa = has_previous ? prev_qa : 0;
    int64_t lag_valid = has_previous ? prev_valid : 0;
    int64_t lag_equal_t = has_previous ? prev_t : -1;
    for (int64_t i = 0; i < n; ++i) {
        const int64_t ti = t[i], fl = flags[i];
        const bool is_upd = updates[i] != 0, is_snap = snapshot[i] != 0, is_clear = clears[i] != 0;
        const bool is_valid = valid[i] != 0, gap = (fl & 4) != 0;
        const bool is_fresh = is_upd && is_valid && !is_snap && !gap;
        const bool is_meas = is_fresh && lag_valid != 0;
        fresh_out[i] = is_fresh;
        measured_out[i] = is_meas;
        fresh_count += is_fresh;
        invalid_count += !is_valid;
        snap_count += is_snap;
        gap_count += gap;
        clear_count += is_clear;
        equal_count += ti == lag_equal_t;
        if ((is_upd && !is_snap) || is_clear) latest_src = i;
        if (latest_src < 0) current_econ = has_previous ? prev_economic : -1;
        else current_econ = clears[latest_src] ? -1 : t[latest_src];
        __int128 left = lag_t, right = ti;
        if (left < window_start) left = window_start;
        if (right > window_end) right = window_end;
        if (maximum_age >= 0) {
            __int128 room_end = (__int128)window_end - before_econ;
            __int128 room = (__int128)maximum_age < room_end ? (__int128)maximum_age : room_end;
            if (room < 0) room = 0;
            __int128 aged = (__int128)before_econ + room;
            if (right > aged) right = aged;
        }
        int64_t duration = 0;
        if (lag_valid && before_econ >= 0 && right > left) duration = (int64_t)(right - left);
        if (duration > 0) {
            const int64_t k = n_keep++;
            exp_starts[k] = (int64_t)left;
            exp_ends[k] = (int64_t)right;
            exp_bid[k] = lag_bid;
            exp_ask[k] = lag_ask;
            exp_qb[k] = lag_qb;
            exp_qa[k] = lag_qa;
            exp_duration[k] = duration;
            const long double qb_ld = (long double)lag_qb;
            const long double qa_ld = (long double)lag_qa;
            const long double ratio = (qb_ld - qa_ld) / (qb_ld + qa_ld);
            const long double dur_ld = (long double)duration;
            exp_dur_imbalance[k] = dur_ld * ratio;
            exp_dur_spread[k] = dur_ld * (long double)(lag_ask - lag_bid);
            exp_mid[k] = floor_div_int64((__int128)lag_bid + lag_ask - (__int128)origin * 2, twice_row);
            dur_sum += duration;
            if (lag_qb > lag_qa) pos_dur += duration;
        }
        if (is_meas) {
            const int64_t b = bid[i], a = ask[i], q_b = bid_size[i], q_a = ask_size[i];
            const int64_t b0 = lag_bid, a0 = lag_ask, q_b0 = lag_qb, q_a0 = lag_qa;
            int64_t ofi = 0, samev = 0;
            if (b >= b0) ofi += q_b;
            if (b <= b0) ofi -= q_b0;
            if (a <= a0) ofi -= q_a;
            if (a >= a0) ofi += q_a0;
            if (b == b0) samev += q_b - q_b0;
            if (a == a0) samev -= q_a - q_a0;
            const int64_t k = n_meas++;
            meas_ofi[k] = ofi;
            meas_same[k] = samev;
            const long double qb0_ld = (long double)q_b0, qa0_ld = (long double)q_a0;
            meas_depth[k] = (long double)ofi / (qb0_ld + qa0_ld);
            const long double qb_ld = (long double)q_b, qa_ld = (long double)q_a;
            const long double imbalance = (qb_ld - qa_ld) / (qb_ld + qa_ld);
            meas_imbalance[k] = imbalance;
            const long double prod = (long double)(a - b) * imbalance;
            meas_micro[k] = prod / (long double)2;
            meas_spread[k] = a - b;
            path += ofi;
            if (k == 0 || path > best_hi) { best_hi = path; hi_at = ti; hi_ord = order[i]; }
            if (k == 0 || path < best_lo) { best_lo = path; lo_at = ti; lo_ord = order[i]; }
            ofi_sum += ofi;
            same_sum += samev;
            price_sum += ofi - samev;
            if (q_b > q_a) ++pos_upd;
        }
        lag_t = ti;
        lag_bid = bid[i];
        lag_ask = ask[i];
        lag_qb = bid_size[i];
        lag_qa = ask_size[i];
        lag_valid = is_valid;
        lag_equal_t = ti;
        before_econ = current_econ;
    }
    stats[0] = n_keep;
    stats[1] = n_meas;
    stats[2] = fresh_count;
    stats[3] = invalid_count;
    stats[4] = snap_count;
    stats[5] = gap_count;
    stats[6] = clear_count;
    stats[7] = equal_count;
    stats[8] = ofi_sum;
    stats[9] = same_sum;
    stats[10] = price_sum;
    stats[11] = pos_upd;
    stats[12] = dur_sum;
    stats[13] = pos_dur;
    stats[14] = best_hi;
    stats[15] = hi_at;
    stats[16] = hi_ord;
    stats[17] = best_lo;
    stats[18] = lo_at;
    stats[19] = lo_ord;
    stats[20] = current_econ;
    stats[21] = n_meas > 0;
    return 0;
}

extern "C" int64_t fuse_native_quote_updates(
    int64_t n, const int64_t* at, const int64_t* order,
    const uint8_t* fresh, const uint8_t* measured,
    int64_t n_measured, const int64_t* ofi, const int64_t* same,
    int64_t grid_start, int64_t grid_end, int64_t width, int64_t cell_count,
    int64_t* quote_rows, int64_t* fresh_quotes, int64_t* pressure_transitions,
    int64_t* same_price_ofi, int64_t* price_change_ofi,
    int64_t* ofi_close, int64_t* ofi_high, int64_t* ofi_low,
    int64_t* ofi_high_at, int64_t* ofi_low_at,
    int64_t* ofi_high_order, int64_t* ofi_low_order) {
    if (n < 0 || n > 50000000 || n_measured < 0 || n_measured > n
            || cell_count < 0 || cell_count > 1000000 || width < 1) return -1;
    if (grid_start < 0 || grid_end <= grid_start
            || grid_end > 9223372036854775807LL - 1000000000LL) return -1;
    if (((__int128)grid_end - grid_start + width - 1) / width != (__int128)cell_count) return -1;
    const int64_t ofi_lim = 4 * (4294967294LL), same_lim = 2 * (4294967294LL);
    int64_t seen = 0;
    for (int64_t i = 0; i < n; ++i) {
        if (at[i] < grid_start || at[i] >= grid_end) return -1;
        if (i > 0 && at[i] < at[i - 1]) return -1;
        const int64_t bin = (at[i] - grid_start) / width;
        if (bin < 0 || bin >= cell_count) return -1;
        if (measured[i] && !fresh[i]) return -1;
        if (measured[i]) {
            if (seen >= n_measured || ofi[seen] < -ofi_lim || ofi[seen] > ofi_lim
                    || same[seen] < -same_lim || same[seen] > same_lim) return -1;
            ++seen;
        }
    }
    if (seen != n_measured) return -1;
    int64_t m = 0;
    for (int64_t i = 0; i < n; ++i) {
        const int64_t bin = (at[i] - grid_start) / width;
        quote_rows[bin] += 1;
        if (fresh[i]) fresh_quotes[bin] += 1;
        if (measured[i]) {
            const int64_t inc = ofi[m], sm = same[m];
            pressure_transitions[bin] += 1;
            same_price_ofi[bin] += sm;
            price_change_ofi[bin] += inc - sm;
            ofi_close[bin] += inc;
            const int64_t path = ofi_close[bin];
            if (path > ofi_high[bin]) {
                ofi_high[bin] = path;
                ofi_high_at[bin] = at[i];
                ofi_high_order[bin] = order[i];
            }
            if (path < ofi_low[bin]) {
                ofi_low[bin] = path;
                ofi_low_at[bin] = at[i];
                ofi_low_order[bin] = order[i];
            }
            ++m;
        }
    }
    return n;
}
'''


def enable_compiled_projection(path, expected_sha256):
    """Called only after compilation inside the registered, bounded attempt."""
    global _LIBRARY, _FUNCTION, _EXPOSURE, _SLICE, _NATIVE_QUOTES
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
    slice_fn = library.fuse_quote_slice
    native_fn = library.fuse_native_quote_updates
    in64 = np.ctypeslib.ndpointer(dtype=np.int64, ndim=1, flags='ALIGNED, C_CONTIGUOUS')
    in8 = np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, flags='ALIGNED, C_CONTIGUOUS')
    out64 = np.ctypeslib.ndpointer(dtype=np.int64, ndim=1, flags='ALIGNED, C_CONTIGUOUS, WRITEABLE')
    out8 = np.ctypeslib.ndpointer(dtype=np.uint8, ndim=1, flags='ALIGNED, C_CONTIGUOUS, WRITEABLE')
    outld = np.ctypeslib.ndpointer(dtype=np.longdouble, ndim=1, flags='ALIGNED, C_CONTIGUOUS, WRITEABLE')
    exposure.argtypes = [ctypes.c_int64, in64, in64, in64, in64, in64, in64,
        ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, out64, outld, outld]
    exposure.restype = ctypes.c_int64
    slice_fn.argtypes = [ctypes.c_int64, in64, in64, in64, in64, in64, in64, in64,
        in8, in8, in8, in8, in64, in64,
        out64, out64, out64, out64, out64, out64, out64, outld, outld, out64,
        out64, out64, outld, outld, outld, out64, out8, out8, out64]
    slice_fn.restype = ctypes.c_int
    native_fn.argtypes = [ctypes.c_int64, in64, in64, in8, in8, ctypes.c_int64, in64, in64,
        ctypes.c_int64, ctypes.c_int64, ctypes.c_int64, ctypes.c_int64,
        out64, out64, out64, out64, out64, out64, out64, out64, out64, out64, out64, out64]
    native_fn.restype = ctypes.c_int64
    abi_ok = np.dtype(np.longdouble).itemsize == ctypes.sizeof(ctypes.c_longdouble)
    _LIBRARY, _FUNCTION = library, function
    _EXPOSURE = exposure if abi_ok else None
    _SLICE = slice_fn if abi_ok else None
    _NATIVE_QUOTES = native_fn


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


def _contiguous_i64(array):
    import numpy as np

    if not isinstance(array, np.ndarray) or array.ndim != 1 or array.dtype.kind not in 'iu':
        return None
    if array.dtype == np.int64 and array.flags.c_contiguous and array.flags.aligned:
        return array
    return np.require(np.asarray(array, dtype=np.int64), requirements=('C', 'ALIGNED'))


def _contiguous_u8(array):
    import numpy as np

    if not isinstance(array, np.ndarray) or array.ndim != 1:
        return None
    if array.dtype == np.uint8 and array.flags.c_contiguous and array.flags.aligned:
        return array
    if array.dtype == bool or array.dtype == np.uint8 or array.dtype.kind in 'iu':
        return np.require(np.asarray(array, dtype=np.uint8), requirements=('C', 'ALIGNED'))
    return None


def _writeable_i64(array, n):
    import numpy as np

    return (isinstance(array, np.ndarray) and array.ndim == 1 and len(array) >= n
            and array.dtype == np.int64 and array.flags.c_contiguous
            and array.flags.aligned and array.flags.writeable)


def _writeable_ld(array, n):
    import numpy as np

    return (isinstance(array, np.ndarray) and array.ndim == 1 and len(array) >= n
            and array.dtype == np.dtype(np.longdouble) and array.flags.c_contiguous
            and array.flags.aligned and array.flags.writeable)


def _writeable_u8(array, n):
    import numpy as np

    return (isinstance(array, np.ndarray) and array.ndim == 1 and len(array) >= n
            and array.dtype == np.uint8 and array.flags.c_contiguous
            and array.flags.aligned and array.flags.writeable)


def fuse_quote_slice(*, t, order, bid, ask, bid_size, ask_size, flags,
                     valid, snapshot, updates, clears, previous,
                     window_start, window_end, maximum_age, origin_ticks, row_ticks,
                     exp_starts, exp_ends, exp_bid, exp_ask, exp_qb, exp_qa, exp_duration,
                     exp_dur_imbalance, exp_dur_spread, exp_mid,
                     meas_ofi, meas_same, meas_depth, meas_imbalance, meas_micro, meas_spread,
                     fresh_out, measured_out, stats):
    """Fill one guarded slice's packed terms. False leaves output buffers unused."""
    global _SLICE_CALLS, _SLICE_ROWS
    if _SLICE is None:
        return False
    import numpy as np

    if (any(type(v) is not int for v in (window_start, window_end, origin_ticks, row_ticks))
            or maximum_age is not None and type(maximum_age) is not int
            or np.dtype(np.longdouble).itemsize != ctypes.sizeof(ctypes.c_longdouble)):
        return False
    inputs = tuple(_contiguous_i64(a) for a in (t, order, bid, ask, bid_size, ask_size, flags))
    bits = tuple(_contiguous_u8(a) for a in (valid, snapshot, updates, clears))
    if any(a is None for a in inputs + bits):
        return False
    n = int(len(inputs[0]))
    if n < 1 or any(len(a) != n for a in inputs + bits):
        return False
    int_outs = (exp_starts, exp_ends, exp_bid, exp_ask, exp_qb, exp_qa, exp_duration, exp_mid,
                meas_ofi, meas_same, meas_spread, stats)
    ld_outs = (exp_dur_imbalance, exp_dur_spread, meas_depth, meas_imbalance, meas_micro)
    if (any(not _writeable_i64(a, n if a is not stats else 22) for a in int_outs)
            or any(not _writeable_ld(a, n) for a in ld_outs)
            or not _writeable_u8(fresh_out, n) or not _writeable_u8(measured_out, n)
            or len(stats) < 22):
        return False
    prev = np.require(np.asarray([
        0 if previous is None else int(previous['t']),
        0 if previous is None else int(previous['bid']),
        0 if previous is None else int(previous['ask']),
        0 if previous is None else int(previous['bid_size']),
        0 if previous is None else int(previous['ask_size']),
        0 if previous is None else int(previous['book_valid']),
        -1 if previous is None else int(previous['economic_at']),
    ], dtype=np.int64), requirements=('C', 'ALIGNED'))
    win = np.require(np.asarray([
        window_start, window_end, -1 if maximum_age is None else maximum_age,
        origin_ticks, row_ticks, 0 if previous is None else 1,
    ], dtype=np.int64), requirements=('C', 'ALIGNED'))
    status = _SLICE(n, *inputs, *bits, prev, win,
                    exp_starts, exp_ends, exp_bid, exp_ask, exp_qb, exp_qa, exp_duration,
                    exp_dur_imbalance, exp_dur_spread, exp_mid,
                    meas_ofi, meas_same, meas_depth, meas_imbalance, meas_micro, meas_spread,
                    fresh_out, measured_out, stats)
    if status:
        raise IntegrityError('compiled quote slice rejected its bounded input domain')
    _SLICE_CALLS += 1
    _SLICE_ROWS += n
    return True


def fuse_native_quote_updates(at, order, fresh, measured, ofi, same, *,
                              start, end, width,
                              quote_rows, fresh_quotes, pressure_transitions,
                              same_price_ofi, price_change_ofi,
                              ofi_close, ofi_high, ofi_low,
                              ofi_high_at, ofi_low_at, ofi_high_order, ofi_low_order):
    """Add validated quote-row counters and per-bin OFI paths. False does not write."""
    global _NATIVE_QUOTE_CALLS, _NATIVE_QUOTE_ROWS
    if _NATIVE_QUOTES is None:
        return False
    import numpy as np

    if (any(type(v) is not int for v in (start, end, width))
            or not 0 <= start < end < 2**63 - 1_000_000_000 or not 1 <= width < 2**63):
        return False
    at, order = _contiguous_i64(at), _contiguous_i64(order)
    ofi, same = _contiguous_i64(ofi), _contiguous_i64(same)
    fresh, measured = _contiguous_u8(fresh), _contiguous_u8(measured)
    if any(a is None for a in (at, order, ofi, same, fresh, measured)):
        return False
    n = int(len(at))
    if any(len(a) != n for a in (order, fresh, measured)):
        return False
    n_measured = int(len(ofi))
    if len(same) != n_measured:
        return False
    if n_measured == 0:
        ofi = same = np.require(np.zeros(1, dtype=np.int64), requirements=('C', 'ALIGNED'))
    outputs = (quote_rows, fresh_quotes, pressure_transitions, same_price_ofi, price_change_ofi,
               ofi_close, ofi_high, ofi_low, ofi_high_at, ofi_low_at, ofi_high_order, ofi_low_order)
    cell_count = len(quote_rows)
    if (any(not _writeable_i64(a, cell_count) or len(a) != cell_count for a in outputs)
            or cell_count != (end - start + width - 1) // width or cell_count > 1_000_000):
        return False
    status = _NATIVE_QUOTES(n, at, order, fresh, measured, n_measured, ofi, same,
                            start, end, width, cell_count, *outputs)
    if status < 0:
        raise IntegrityError('compiled native quote updates rejected their bounded input domain')
    _NATIVE_QUOTE_CALLS += 1
    _NATIVE_QUOTE_ROWS += n
    return True


def execution_counts():
    return {'fused_batches': _FAST_CALLS, 'fused_rows': _FAST_ROWS,
            'compiled_exposure_calls': _EXPOSURE_CALLS,
            'compiled_exposure_intervals': _EXPOSURE_INTERVALS,
            'compiled_exposure_cells': _EXPOSURE_CELLS,
            'compiled_quote_slice_calls': _SLICE_CALLS,
            'compiled_quote_slice_rows': _SLICE_ROWS,
            'compiled_native_quote_calls': _NATIVE_QUOTE_CALLS,
            'compiled_native_quote_rows': _NATIVE_QUOTE_ROWS}
