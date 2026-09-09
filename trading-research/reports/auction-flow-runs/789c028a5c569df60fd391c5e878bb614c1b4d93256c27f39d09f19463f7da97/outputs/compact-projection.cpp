
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
    if (window_start < 0 || window_end <= window_start
            || window_end > 9223372036854775807LL - 1000000000LL
            || row_ticks < 1 || row_ticks > 1024 || origin <= -9007199254740992LL || origin >= 9007199254740992LL)
        return 1;
    const int64_t prev_t = prev[0], prev_bid = prev[1], prev_ask = prev[2];
    const int64_t prev_qb = prev[3], prev_qa = prev[4], prev_valid = prev[5], prev_economic = prev[6];
    // Validate the complete population before writing any caller-owned output.
    if (has_previous != 0 && has_previous != 1) return 1;
    if (prev_valid < 0 || prev_valid > 1 || maximum_age < -1) return 1;
    if (has_previous && (prev_t > t[0] || prev_t < 0)) return 1;
    if (has_previous && prev_valid && (prev_bid <= 0 || prev_ask >= 9007199254740992LL
            || prev_bid > prev_ask || prev_qb <= 0 || prev_qa <= 0
            || prev_qb >= 4294967295LL || prev_qa >= 4294967295LL)) return 1;
    for (int64_t i = 0; i < n; ++i) {
        if (t[i] < window_start || t[i] >= window_end || order[i] < 0
                || (i && (t[i] < t[i-1] || order[i] <= order[i-1]))
                || flags[i] < 0 || flags[i] > 255 || valid[i] > 1 || snapshot[i] > 1
                || updates[i] > 1 || clears[i] > 1
                || (snapshot[i] != ((flags[i] & 32) != 0))) return 1;
        if (valid[i] && (!updates[i] || clears[i] || (flags[i] & 4)
                || bid[i] <= 0 || ask[i] >= 9007199254740992LL || bid[i] > ask[i]
                || bid_size[i] <= 0 || ask_size[i] <= 0
                || bid_size[i] >= 4294967295LL || ask_size[i] >= 4294967295LL)) return 1;
    }
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
