
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
