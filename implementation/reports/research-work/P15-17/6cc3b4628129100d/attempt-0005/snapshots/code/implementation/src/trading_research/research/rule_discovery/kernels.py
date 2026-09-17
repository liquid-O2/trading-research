"""Numba kernels for stateful tape/bar loops. Decimal exists only at the JSON boundary."""

from __future__ import annotations

from math import exp, log
from typing import Any

import numpy as np
from numba import njit

LN2 = log(2.0)
C2_HALF_LIFE_NS = 300 * 1_000_000_000
UNKNOWN_GATE = 0.20
F1_MINUTES = 60
F2_MAX_MINUTES = 180
F3_LENGTHS = (15, 30, 60)
S1_SWEEP_TICKS = 1
S2_FAVORABLE_TICKS = 2
S3_C1 = 0.20
S4_PRESSURE_S = 120
S4_FAVORABLE_TICKS = 1
REARM_TICKS_FLOOR = 4
NS = 1_000_000_000
MINUTE_NS = 60 * NS

# Integer state codes for sequence kernels.
ST_CONTACTED = 0
ST_SWEPT = 1
ST_RECLAIMED = 2
ST_CONFIRMED = 3
ST_EXPIRED = 4
ST_INVALIDATED = 5
ST_INPUT_UNKNOWN = 6
ST_PRESSURE = 7
ST_STALLED = 8

PYTHON_REFERENCE_NAMES = (
    "python_lifecycle_contacts",
    "python_rearm_contacts",
    "python_sweep_displacement",
    "python_f2_walk",
    "python_f3_first",
    "python_s1_machine",
    "python_s2_machine",
    "python_s3_machine",
    "python_s4_machine",
    "python_book_observe",
    "python_profile_accumulate",
    "python_delta_imbalance",
    "python_c2_fold",
    "python_minute_bars",
    "python_markout_arrays",
)

KERNEL_NAMES = (
    "contact_lifecycle_kernel",
    "rearm_contacts_kernel",
    "sweep_displacement_kernel",
    "f2_walk_kernel",
    "f3_first_kernel",
    "s1_machine_kernel",
    "s2_machine_kernel",
    "s3_machine_kernel",
    "s4_machine_kernel",
    "book_observe_kernel",
    "profile_accumulate_kernel",
    "delta_imbalance_kernel",
    "c2_fold_kernel",
    "minute_bars_kernel",
    "markout_arrays_kernel",
)


def python_lifecycle_contacts(
    high: list[int],
    low: list[int],
    lo: int,
    hi: int,
    departure: int,
) -> list[int]:
    """One contact per approach. Rearm after a 4-tick (or given) departure. Matches distinct_contacts."""
    ready = True
    out: list[int] = []
    for i, (h, l) in enumerate(zip(high, low)):
        if l <= hi and h >= lo:
            if ready:
                out.append(i)
                ready = False
        elif l > hi + departure or h < lo - departure:
            ready = True
    return out


def python_rearm_contacts(
    high: list[int],
    low: list[int],
    lo: int,
    hi: int,
    scale_ticks: int,
) -> list[int]:
    """SPEC rearm: max(4 ticks, 0.1 S) beyond the band and one complete outside bar."""
    need = max(REARM_TICKS_FLOOR, int(0.1 * scale_ticks))
    ready = True
    outside = 0
    out: list[int] = []
    for i, (h, l) in enumerate(zip(high, low)):
        if l <= hi and h >= lo:
            if ready:
                out.append(i)
                ready = False
            outside = 0
        elif l > hi + need or h < lo - need:
            outside += 1
            if outside >= 1:
                ready = True
        else:
            outside = 0
    return out


def python_sweep_displacement(
    high: list[int],
    low: list[int],
    lo: int,
    hi: int,
    side: int,
) -> tuple[int, int, int]:
    """Return (first_sweep_index or -1, extreme_ticks, displacement_ticks). side +1 defends lo, -1 defends hi."""
    first = -1
    extreme = lo if side > 0 else hi
    for i, (h, l) in enumerate(zip(high, low)):
        if side > 0:
            if l <= lo - S1_SWEEP_TICKS:
                if first < 0:
                    first = i
                if l < extreme:
                    extreme = l
        else:
            if h >= hi + S1_SWEEP_TICKS:
                if first < 0:
                    first = i
                if h > extreme:
                    extreme = h
    if first < 0:
        return -1, extreme, 0
    if side > 0:
        return first, extreme, lo - extreme
    return first, extreme, extreme - hi


def python_f2_walk(volumes_newest_first: list[int], median_volume: int, max_minutes: int = F2_MAX_MINUTES) -> tuple[int, int, int]:
    """Return (minutes, overshoot, cumulative) or (0, 0, cumulative) if the threshold is missed."""
    acc = 0
    n = 0
    for volume in volumes_newest_first[:max_minutes]:
        acc += int(volume)
        n += 1
        if acc >= median_volume:
            return n, acc - int(median_volume), acc
    return 0, 0, acc


def python_f3_first(
    open_ticks: list[int],
    high_ticks: list[int],
    low_ticks: list[int],
    close_ticks: list[int],
) -> int:
    """First length in 15,30,60 whose trailing window meets width and efficiency. 0 if none."""
    n = len(open_ticks)
    for length in F3_LENGTHS:
        if n < length + F1_MINUTES:
            continue
        start = n - length
        scale_hi = max(high_ticks[start - F1_MINUTES : start])
        scale_lo = min(low_ticks[start - F1_MINUTES : start])
        win_hi = max(high_ticks[start:])
        win_lo = min(low_ticks[start:])
        width = win_hi - win_lo
        scale = scale_hi - scale_lo
        if width * 4 > 3 * scale:
            continue
        denom = width if width > 1 else 1
        if abs(close_ticks[-1] - open_ticks[start]) * 20 > denom * 7:
            continue
        return length
    return 0


def python_s1_machine(
    high: list[int],
    low: list[int],
    close: list[int],
    lo: int,
    hi: int,
    side: int,
    contact_i: int,
    deadline_i: int,
) -> tuple[int, int, int]:
    """Walk bars after contact. Return (state, sweep_i, confirm_i)."""
    state = ST_CONTACTED
    sweep_i = -1
    confirm_i = -1
    last = min(len(high) - 1, deadline_i)
    for i in range(contact_i + 1, last + 1):
        if state == ST_CONTACTED:
            if side > 0 and low[i] <= lo - S1_SWEEP_TICKS:
                state = ST_SWEPT
                sweep_i = i
            elif side < 0 and high[i] >= hi + S1_SWEEP_TICKS:
                state = ST_SWEPT
                sweep_i = i
        elif state == ST_SWEPT:
            if lo <= close[i] <= hi:
                state = ST_CONFIRMED
                confirm_i = i
                break
    if state != ST_CONFIRMED and last >= deadline_i:
        state = ST_EXPIRED
    return state, sweep_i, confirm_i


def python_s2_machine(
    high: list[int],
    low: list[int],
    close: list[int],
    lo: int,
    hi: int,
    side: int,
    contact_i: int,
    deadline_i: int,
) -> tuple[int, int, int, int]:
    """S2: S1 reclaim, then a later contact within 1 tick and a +2-tick favorable close."""
    state = ST_CONTACTED
    sweep_i = -1
    reclaim_i = -1
    confirm_i = -1
    extreme = 0
    seen_retest = False
    last = min(len(high) - 1, deadline_i)
    for i in range(contact_i + 1, last + 1):
        if state == ST_CONTACTED:
            if side > 0 and low[i] <= lo - S1_SWEEP_TICKS:
                state = ST_SWEPT
                sweep_i = i
                extreme = low[i]
            elif side < 0 and high[i] >= hi + S1_SWEEP_TICKS:
                state = ST_SWEPT
                sweep_i = i
                extreme = high[i]
        elif state == ST_SWEPT:
            if side > 0 and low[i] < extreme:
                extreme = low[i]
            if side < 0 and high[i] > extreme:
                extreme = high[i]
            if lo <= close[i] <= hi:
                state = ST_RECLAIMED
                reclaim_i = i
        elif state == ST_RECLAIMED:
            if side > 0 and close[i] < extreme:
                return ST_INVALIDATED, sweep_i, reclaim_i, i
            if side < 0 and close[i] > extreme:
                return ST_INVALIDATED, sweep_i, reclaim_i, i
            if side > 0:
                touch = low[i] <= lo + 1 and high[i] >= lo - 1
                favorable = close[i] >= lo + S2_FAVORABLE_TICKS
            else:
                touch = high[i] >= hi - 1 and low[i] <= hi + 1
                favorable = close[i] <= hi - S2_FAVORABLE_TICKS
            if touch:
                seen_retest = True
            if seen_retest and favorable:
                return ST_CONFIRMED, sweep_i, reclaim_i, i
    if state != ST_CONFIRMED and last >= deadline_i:
        state = ST_EXPIRED
    return state, sweep_i, reclaim_i, confirm_i


def python_s3_machine(
    high: list[int],
    low: list[int],
    close: list[int],
    lo: int,
    hi: int,
    side: int,
    contact_i: int,
    deadline_i: int,
    c1_value: float,
    c1_available: int,
    cohort_mean: float,
    cohort_available: int,
    cohort_after: int,
) -> tuple[int, int, int]:
    """S3: S1 reclaim plus C1 and 120s cohort gates. Scalars, not per-bar Python state."""
    state = ST_CONTACTED
    sweep_i = -1
    confirm_i = -1
    last = min(len(high) - 1, deadline_i)
    for i in range(contact_i + 1, last + 1):
        if state == ST_CONTACTED:
            if side > 0 and low[i] <= lo - S1_SWEEP_TICKS:
                state = ST_SWEPT
                sweep_i = i
            elif side < 0 and high[i] >= hi + S1_SWEEP_TICKS:
                state = ST_SWEPT
                sweep_i = i
        elif state == ST_SWEPT:
            if lo <= close[i] <= hi:
                state = ST_CONFIRMED
                confirm_i = i
                break
    if state != ST_CONFIRMED:
        if last >= deadline_i:
            return ST_EXPIRED, sweep_i, confirm_i
        return state, sweep_i, confirm_i
    if c1_available == 0 or cohort_available == 0 or cohort_after == 1:
        return ST_INPUT_UNKNOWN, sweep_i, confirm_i
    signed = float(c1_value) * side
    if signed <= S3_C1 or float(cohort_mean) <= 0:
        return ST_SWEPT, sweep_i, -1
    return ST_CONFIRMED, sweep_i, confirm_i


def python_s4_machine(
    opposing: list[int],
    quantile: int,
    adverse_ticks: list[int],
    cap_ticks: int,
    close: list[int],
    contact_extreme: int,
    side: int,
    contact_i: int,
    pressure_last_i: int,
    deadline_i: int,
) -> tuple[int, int]:
    """S4: pressure, stall, then a favorable close beyond the contact extreme."""
    state = ST_CONTACTED
    event_i = -1
    last = min(len(close) - 1, deadline_i)
    for i in range(contact_i + 1, last + 1):
        if state == ST_CONTACTED:
            if opposing[i] < 0:
                return ST_INPUT_UNKNOWN, i
            if i <= pressure_last_i and opposing[i] > quantile:
                state = ST_PRESSURE
                event_i = i
        elif state == ST_PRESSURE:
            if adverse_ticks[i] <= cap_ticks:
                state = ST_STALLED
                event_i = i
            else:
                return ST_INVALIDATED, i
        elif state == ST_STALLED:
            if side > 0 and close[i] >= contact_extreme + S4_FAVORABLE_TICKS:
                return ST_CONFIRMED, i
            if side < 0 and close[i] <= contact_extreme - S4_FAVORABLE_TICKS:
                return ST_CONFIRMED, i
    if state != ST_CONFIRMED:
        return ST_EXPIRED, event_i
    return state, event_i


def python_book_observe(
    bid_ticks: list[int],
    ask_ticks: list[int],
    bid_sz: list[int],
    ask_sz: list[int],
    level_ticks: int,
    side: int,
) -> tuple[int, int, int, int]:
    """Watch one price level. Return (n_present, n_depleted, n_replenished, last_present)."""
    present_prev = 0
    n_present = 0
    n_depleted = 0
    n_replenished = 0
    last_present = 0
    for i in range(len(bid_ticks)):
        if side > 0:
            present = 1 if bid_ticks[i] == level_ticks and bid_sz[i] > 0 else 0
        else:
            present = 1 if ask_ticks[i] == level_ticks and ask_sz[i] > 0 else 0
        if present:
            n_present += 1
            last_present = 1
            if present_prev == 0 and i > 0:
                n_replenished += 1
        else:
            last_present = 0
            if present_prev == 1:
                n_depleted += 1
        present_prev = present
    return n_present, n_depleted, n_replenished, last_present


def python_profile_accumulate(ticks: list[int], sizes: list[int], min_tick: int, n_bins: int) -> list[int]:
    raw = [0] * n_bins
    for tick, size in zip(ticks, sizes):
        b = int(tick) - min_tick
        if 0 <= b < n_bins:
            raw[b] += int(size)
    return raw


def python_delta_imbalance(sizes: list[int], sides: list[int]) -> tuple[int, int, int, float, int]:
    """Return (signed, volume, unknown, known_ratio, admitted). admitted is 0/1."""
    signed = 0
    volume = 0
    unknown = 0
    for size, side in zip(sizes, sides):
        volume += size
        if side == 0:
            unknown += size
        else:
            signed += side * size
    known = volume - unknown
    ratio = signed / max(known, 1)
    share = (unknown / volume) if volume else 1.0
    admitted = 1 if volume > 0 and share <= UNKNOWN_GATE else 0
    return signed, volume, unknown, ratio, admitted


def python_c2_fold(
    t_ns: list[int],
    delta: list[int],
    known: list[int],
    half_life_ns: int = C2_HALF_LIFE_NS,
) -> tuple[list[float], list[float], list[float]]:
    z = 0.0
    k = 0.0
    t_prev = None
    zs: list[float] = []
    ks: list[float] = []
    norms: list[float] = []
    for t, d, kn in zip(t_ns, delta, known):
        dt = 0 if t_prev is None else t - t_prev
        factor = exp(-LN2 * dt / half_life_ns) if half_life_ns > 0 else 0.0
        z = factor * z + float(d)
        k = factor * k + float(kn)
        zs.append(z)
        ks.append(k)
        norms.append(z / k if k > 0 else float("nan"))
        t_prev = t
    return zs, ks, norms


def python_minute_bars(
    t_ns: list[int],
    ticks: list[int],
    size: list[int],
    side: list[int],
    known_at: list[int],
    start_ns: int,
    end_ns: int,
) -> dict[str, list[int]]:
    width = MINUTE_NS
    grouped: dict[int, list[tuple[int, int, int, int]]] = {}
    for event_ns, px, sz, sd, kn in zip(t_ns, ticks, size, side, known_at):
        if event_ns < start_ns or event_ns >= end_ns:
            continue
        bucket = (event_ns - start_ns) // width
        grouped.setdefault(bucket, []).append((px, sz, sd, kn))
    starts: list[int] = []
    ends: list[int] = []
    opens: list[int] = []
    highs: list[int] = []
    lows: list[int] = []
    closes: list[int] = []
    volumes: list[int] = []
    signed: list[int] = []
    unknown: list[int] = []
    known: list[int] = []
    for bucket in sorted(grouped):
        members = grouped[bucket]
        bar_start = start_ns + bucket * width
        bar_end = min(bar_start + width, end_ns)
        starts.append(bar_start)
        ends.append(bar_end)
        opens.append(members[0][0])
        highs.append(max(item[0] for item in members))
        lows.append(min(item[0] for item in members))
        closes.append(members[-1][0])
        volumes.append(sum(item[1] for item in members))
        signed.append(sum(item[2] * item[1] for item in members if item[2] != 0))
        unknown.append(sum(item[1] for item in members if item[2] == 0))
        known.append(max(max(item[3] for item in members), bar_end))
    return {
        "start_ns": starts,
        "end_ns": ends,
        "open_ticks": opens,
        "high_ticks": highs,
        "low_ticks": lows,
        "close_ticks": closes,
        "volume": volumes,
        "signed": signed,
        "unknown": unknown,
        "known_at_ns": known,
    }


def python_markout_arrays(
    sign: list[int],
    qty: list[int],
    price: list[float],
    event_ns: list[int],
    mid: list[float],
    mid_available_ns: list[int],
    horizon_ns: int,
    snapshot_ns: int,
) -> tuple[float, int, float, int, int]:
    """Return (buy_sum, buy_vol, sell_sum, sell_vol, unresolved)."""
    buy_sum = 0.0
    sell_sum = 0.0
    buy_vol = 0
    sell_vol = 0
    unresolved = 0
    for i, s in enumerate(sign):
        if s not in (1, -1):
            continue
        due = event_ns[i] + horizon_ns
        m = mid[i]
        avail = mid_available_ns[i]
        if m != m or avail > snapshot_ns or due > snapshot_ns:
            unresolved += 1
            continue
        unit = s * (m - price[i])
        contrib = qty[i] * unit
        if s == 1:
            buy_sum += contrib
            buy_vol += qty[i]
        else:
            sell_sum += contrib
            sell_vol += qty[i]
    return buy_sum, buy_vol, sell_sum, sell_vol, unresolved


@njit(cache=True)
def contact_lifecycle_kernel(high, low, lo, hi, departure):
    n = high.shape[0]
    out = np.empty(n, dtype=np.int64)
    count = 0
    ready = True
    for i in range(n):
        h = high[i]
        l = low[i]
        if l <= hi and h >= lo:
            if ready:
                out[count] = i
                count += 1
                ready = False
        elif l > hi + departure or h < lo - departure:
            ready = True
    return out[:count]


@njit(cache=True)
def rearm_contacts_kernel(high, low, lo, hi, scale_ticks):
    need = REARM_TICKS_FLOOR
    tenth = scale_ticks // 10
    if tenth > need:
        need = tenth
    n = high.shape[0]
    out = np.empty(n, dtype=np.int64)
    count = 0
    ready = True
    outside = 0
    for i in range(n):
        h = high[i]
        l = low[i]
        if l <= hi and h >= lo:
            if ready:
                out[count] = i
                count += 1
                ready = False
            outside = 0
        elif l > hi + need or h < lo - need:
            outside += 1
            if outside >= 1:
                ready = True
        else:
            outside = 0
    return out[:count]


@njit(cache=True)
def sweep_displacement_kernel(high, low, lo, hi, side):
    first = np.int64(-1)
    extreme = lo if side > 0 else hi
    n = high.shape[0]
    for i in range(n):
        if side > 0:
            if low[i] <= lo - S1_SWEEP_TICKS:
                if first < 0:
                    first = i
                if low[i] < extreme:
                    extreme = low[i]
        else:
            if high[i] >= hi + S1_SWEEP_TICKS:
                if first < 0:
                    first = i
                if high[i] > extreme:
                    extreme = high[i]
    if first < 0:
        return np.int64(-1), np.int64(extreme), np.int64(0)
    if side > 0:
        return first, np.int64(extreme), np.int64(lo - extreme)
    return first, np.int64(extreme), np.int64(extreme - hi)


@njit(cache=True)
def f2_walk_kernel(volumes_newest_first, median_volume, max_minutes):
    acc = np.int64(0)
    n = np.int64(0)
    limit = volumes_newest_first.shape[0]
    if max_minutes < limit:
        limit = max_minutes
    for i in range(limit):
        acc += volumes_newest_first[i]
        n += 1
        if acc >= median_volume:
            return n, acc - median_volume, acc
    return np.int64(0), np.int64(0), acc


@njit(cache=True)
def f3_first_kernel(open_ticks, high_ticks, low_ticks, close_ticks):
    n = open_ticks.shape[0]
    lengths = np.empty(3, dtype=np.int64)
    lengths[0] = 15
    lengths[1] = 30
    lengths[2] = 60
    for li in range(3):
        length = lengths[li]
        if n < length + F1_MINUTES:
            continue
        start = n - length
        scale_hi = high_ticks[start - F1_MINUTES]
        scale_lo = low_ticks[start - F1_MINUTES]
        for j in range(start - F1_MINUTES + 1, start):
            if high_ticks[j] > scale_hi:
                scale_hi = high_ticks[j]
            if low_ticks[j] < scale_lo:
                scale_lo = low_ticks[j]
        win_hi = high_ticks[start]
        win_lo = low_ticks[start]
        for j in range(start + 1, n):
            if high_ticks[j] > win_hi:
                win_hi = high_ticks[j]
            if low_ticks[j] < win_lo:
                win_lo = low_ticks[j]
        width = win_hi - win_lo
        scale = scale_hi - scale_lo
        if width * 4 > 3 * scale:
            continue
        denom = width if width > 1 else 1
        body = close_ticks[n - 1] - open_ticks[start]
        if body < 0:
            body = -body
        if body * 20 > denom * 7:
            continue
        return length
    return np.int64(0)


@njit(cache=True)
def s1_machine_kernel(high, low, close, lo, hi, side, contact_i, deadline_i):
    state = np.int64(ST_CONTACTED)
    sweep_i = np.int64(-1)
    confirm_i = np.int64(-1)
    last = high.shape[0] - 1
    if deadline_i < last:
        last = deadline_i
    i = contact_i + 1
    while i <= last:
        if state == ST_CONTACTED:
            if side > 0 and low[i] <= lo - S1_SWEEP_TICKS:
                state = np.int64(ST_SWEPT)
                sweep_i = i
            elif side < 0 and high[i] >= hi + S1_SWEEP_TICKS:
                state = np.int64(ST_SWEPT)
                sweep_i = i
        elif state == ST_SWEPT:
            if close[i] >= lo and close[i] <= hi:
                state = np.int64(ST_CONFIRMED)
                confirm_i = i
                break
        i += 1
    if state != ST_CONFIRMED and last >= deadline_i:
        state = np.int64(ST_EXPIRED)
    return state, sweep_i, confirm_i


@njit(cache=True)
def s2_machine_kernel(high, low, close, lo, hi, side, contact_i, deadline_i):
    state = np.int64(ST_CONTACTED)
    sweep_i = np.int64(-1)
    reclaim_i = np.int64(-1)
    confirm_i = np.int64(-1)
    extreme = np.int64(0)
    seen_retest = 0
    last = high.shape[0] - 1
    if deadline_i < last:
        last = deadline_i
    i = contact_i + 1
    while i <= last:
        if state == ST_CONTACTED:
            if side > 0 and low[i] <= lo - S1_SWEEP_TICKS:
                state = np.int64(ST_SWEPT)
                sweep_i = i
                extreme = low[i]
            elif side < 0 and high[i] >= hi + S1_SWEEP_TICKS:
                state = np.int64(ST_SWEPT)
                sweep_i = i
                extreme = high[i]
        elif state == ST_SWEPT:
            if side > 0 and low[i] < extreme:
                extreme = low[i]
            if side < 0 and high[i] > extreme:
                extreme = high[i]
            if close[i] >= lo and close[i] <= hi:
                state = np.int64(ST_RECLAIMED)
                reclaim_i = i
        elif state == ST_RECLAIMED:
            if side > 0 and close[i] < extreme:
                return np.int64(ST_INVALIDATED), sweep_i, reclaim_i, i
            if side < 0 and close[i] > extreme:
                return np.int64(ST_INVALIDATED), sweep_i, reclaim_i, i
            if side > 0:
                touch = 1 if low[i] <= lo + 1 and high[i] >= lo - 1 else 0
                favorable = 1 if close[i] >= lo + S2_FAVORABLE_TICKS else 0
            else:
                touch = 1 if high[i] >= hi - 1 and low[i] <= hi + 1 else 0
                favorable = 1 if close[i] <= hi - S2_FAVORABLE_TICKS else 0
            if touch == 1:
                seen_retest = 1
            if seen_retest == 1 and favorable == 1:
                return np.int64(ST_CONFIRMED), sweep_i, reclaim_i, i
        i += 1
    if state != ST_CONFIRMED and last >= deadline_i:
        state = np.int64(ST_EXPIRED)
    return state, sweep_i, reclaim_i, confirm_i


@njit(cache=True)
def s3_machine_kernel(
    high,
    low,
    close,
    lo,
    hi,
    side,
    contact_i,
    deadline_i,
    c1_value,
    c1_available,
    cohort_mean,
    cohort_available,
    cohort_after,
):
    state = np.int64(ST_CONTACTED)
    sweep_i = np.int64(-1)
    confirm_i = np.int64(-1)
    last = high.shape[0] - 1
    if deadline_i < last:
        last = deadline_i
    i = contact_i + 1
    while i <= last:
        if state == ST_CONTACTED:
            if side > 0 and low[i] <= lo - S1_SWEEP_TICKS:
                state = np.int64(ST_SWEPT)
                sweep_i = i
            elif side < 0 and high[i] >= hi + S1_SWEEP_TICKS:
                state = np.int64(ST_SWEPT)
                sweep_i = i
        elif state == ST_SWEPT:
            if close[i] >= lo and close[i] <= hi:
                state = np.int64(ST_CONFIRMED)
                confirm_i = i
                break
        i += 1
    if state != ST_CONFIRMED:
        if last >= deadline_i:
            return np.int64(ST_EXPIRED), sweep_i, confirm_i
        return state, sweep_i, confirm_i
    if c1_available == 0 or cohort_available == 0 or cohort_after == 1:
        return np.int64(ST_INPUT_UNKNOWN), sweep_i, confirm_i
    signed = float(c1_value) * float(side)
    if signed <= S3_C1 or float(cohort_mean) <= 0.0:
        return np.int64(ST_SWEPT), sweep_i, np.int64(-1)
    return np.int64(ST_CONFIRMED), sweep_i, confirm_i


@njit(cache=True)
def s4_machine_kernel(
    opposing,
    quantile,
    adverse_ticks,
    cap_ticks,
    close,
    contact_extreme,
    side,
    contact_i,
    pressure_last_i,
    deadline_i,
):
    state = np.int64(ST_CONTACTED)
    event_i = np.int64(-1)
    last = close.shape[0] - 1
    if deadline_i < last:
        last = deadline_i
    i = contact_i + 1
    while i <= last:
        if state == ST_CONTACTED:
            if opposing[i] < 0:
                return np.int64(ST_INPUT_UNKNOWN), i
            if i <= pressure_last_i and opposing[i] > quantile:
                state = np.int64(ST_PRESSURE)
                event_i = i
        elif state == ST_PRESSURE:
            if adverse_ticks[i] <= cap_ticks:
                state = np.int64(ST_STALLED)
                event_i = i
            else:
                return np.int64(ST_INVALIDATED), i
        elif state == ST_STALLED:
            if side > 0 and close[i] >= contact_extreme + S4_FAVORABLE_TICKS:
                return np.int64(ST_CONFIRMED), i
            if side < 0 and close[i] <= contact_extreme - S4_FAVORABLE_TICKS:
                return np.int64(ST_CONFIRMED), i
        i += 1
    if state != ST_CONFIRMED:
        return np.int64(ST_EXPIRED), event_i
    return state, event_i


@njit(cache=True)
def book_observe_kernel(bid_ticks, ask_ticks, bid_sz, ask_sz, level_ticks, side):
    present_prev = 0
    n_present = 0
    n_depleted = 0
    n_replenished = 0
    last_present = 0
    n = bid_ticks.shape[0]
    for i in range(n):
        if side > 0:
            present = 1 if bid_ticks[i] == level_ticks and bid_sz[i] > 0 else 0
        else:
            present = 1 if ask_ticks[i] == level_ticks and ask_sz[i] > 0 else 0
        if present == 1:
            n_present += 1
            last_present = 1
            if present_prev == 0 and i > 0:
                n_replenished += 1
        else:
            last_present = 0
            if present_prev == 1:
                n_depleted += 1
        present_prev = present
    return n_present, n_depleted, n_replenished, last_present


@njit(cache=True)
def profile_accumulate_kernel(ticks, sizes, min_tick, n_bins):
    raw = np.zeros(n_bins, dtype=np.int64)
    for i in range(ticks.shape[0]):
        b = ticks[i] - min_tick
        if b >= 0 and b < n_bins:
            raw[b] += sizes[i]
    return raw


@njit(cache=True)
def delta_imbalance_kernel(sizes, sides):
    signed = np.int64(0)
    volume = np.int64(0)
    unknown = np.int64(0)
    for i in range(sizes.shape[0]):
        volume += sizes[i]
        if sides[i] == 0:
            unknown += sizes[i]
        else:
            signed += sides[i] * sizes[i]
    known = volume - unknown
    denom = known if known > 1 else np.int64(1)
    ratio = float(signed) / float(denom)
    share = float(unknown) / float(volume) if volume > 0 else 1.0
    admitted = 1 if volume > 0 and share <= UNKNOWN_GATE else 0
    return signed, volume, unknown, ratio, admitted


@njit(cache=True)
def c2_fold_kernel(t_ns, delta, known, half_life_ns):
    n = t_ns.shape[0]
    zs = np.empty(n, dtype=np.float64)
    ks = np.empty(n, dtype=np.float64)
    norms = np.empty(n, dtype=np.float64)
    z = 0.0
    k = 0.0
    t_prev = np.int64(0)
    have_prev = False
    for i in range(n):
        dt = np.int64(0) if not have_prev else t_ns[i] - t_prev
        factor = np.exp(-LN2 * float(dt) / float(half_life_ns)) if half_life_ns > 0 else 0.0
        z = factor * z + float(delta[i])
        k = factor * k + float(known[i])
        zs[i] = z
        ks[i] = k
        norms[i] = z / k if k > 0.0 else np.nan
        t_prev = t_ns[i]
        have_prev = True
    return zs, ks, norms


@njit(cache=True)
def minute_bars_kernel(t_ns, ticks, size, side, known_at, start_ns, end_ns):
    width = MINUTE_NS
    span = end_ns - start_ns
    n_min = span // width
    if span % width:
        n_min += 1
    if n_min < 0:
        n_min = 0
    present = np.zeros(n_min, dtype=np.uint8)
    open_ticks = np.zeros(n_min, dtype=np.int64)
    high_ticks = np.zeros(n_min, dtype=np.int64)
    low_ticks = np.zeros(n_min, dtype=np.int64)
    close_ticks = np.zeros(n_min, dtype=np.int64)
    volume = np.zeros(n_min, dtype=np.int64)
    signed = np.zeros(n_min, dtype=np.int64)
    unknown = np.zeros(n_min, dtype=np.int64)
    known = np.zeros(n_min, dtype=np.int64)
    n = t_ns.shape[0]
    for i in range(n):
        event_ns = t_ns[i]
        if event_ns < start_ns or event_ns >= end_ns:
            continue
        b = (event_ns - start_ns) // width
        px = ticks[i]
        sz = size[i]
        sd = side[i]
        kn = known_at[i]
        if present[b] == 0:
            present[b] = 1
            open_ticks[b] = px
            high_ticks[b] = px
            low_ticks[b] = px
            known[b] = kn
        else:
            if px > high_ticks[b]:
                high_ticks[b] = px
            if px < low_ticks[b]:
                low_ticks[b] = px
            if kn > known[b]:
                known[b] = kn
        close_ticks[b] = px
        volume[b] += sz
        if sd == 0:
            unknown[b] += sz
        else:
            signed[b] += sd * sz
    count = 0
    for b in range(n_min):
        if present[b] == 1:
            count += 1
    start_out = np.empty(count, dtype=np.int64)
    end_out = np.empty(count, dtype=np.int64)
    open_out = np.empty(count, dtype=np.int64)
    high_out = np.empty(count, dtype=np.int64)
    low_out = np.empty(count, dtype=np.int64)
    close_out = np.empty(count, dtype=np.int64)
    vol_out = np.empty(count, dtype=np.int64)
    signed_out = np.empty(count, dtype=np.int64)
    unknown_out = np.empty(count, dtype=np.int64)
    known_out = np.empty(count, dtype=np.int64)
    j = 0
    for b in range(n_min):
        if present[b] == 0:
            continue
        bar_start = start_ns + b * width
        bar_end = bar_start + width
        if bar_end > end_ns:
            bar_end = end_ns
        start_out[j] = bar_start
        end_out[j] = bar_end
        open_out[j] = open_ticks[b]
        high_out[j] = high_ticks[b]
        low_out[j] = low_ticks[b]
        close_out[j] = close_ticks[b]
        vol_out[j] = volume[b]
        signed_out[j] = signed[b]
        unknown_out[j] = unknown[b]
        known_out[j] = known[b] if known[b] > bar_end else bar_end
        j += 1
    return start_out, end_out, open_out, high_out, low_out, close_out, vol_out, signed_out, unknown_out, known_out


@njit(cache=True)
def markout_arrays_kernel(sign, qty, price, event_ns, mid, mid_available_ns, horizon_ns, snapshot_ns):
    buy_sum = 0.0
    sell_sum = 0.0
    buy_vol = np.int64(0)
    sell_vol = np.int64(0)
    unresolved = np.int64(0)
    for i in range(sign.shape[0]):
        s = sign[i]
        if s != 1 and s != -1:
            continue
        due = event_ns[i] + horizon_ns
        m = mid[i]
        avail = mid_available_ns[i]
        if m != m or avail > snapshot_ns or due > snapshot_ns:
            unresolved += 1
            continue
        unit = float(s) * (m - price[i])
        contrib = float(qty[i]) * unit
        if s == 1:
            buy_sum += contrib
            buy_vol += qty[i]
        else:
            sell_sum += contrib
            sell_vol += qty[i]
    return buy_sum, buy_vol, sell_sum, sell_vol, unresolved


def _i64(values) -> np.ndarray:
    return np.asarray(values, dtype=np.int64)


def _f64(values) -> np.ndarray:
    return np.asarray(values, dtype=np.float64)


def lifecycle_contact_indices(high, low, lo: int, hi: int, departure: int = 4) -> np.ndarray:
    return contact_lifecycle_kernel(_i64(high), _i64(low), np.int64(lo), np.int64(hi), np.int64(departure))


def rearm_contact_indices(high, low, lo: int, hi: int, scale_ticks: int) -> np.ndarray:
    return rearm_contacts_kernel(_i64(high), _i64(low), np.int64(lo), np.int64(hi), np.int64(scale_ticks))


def relative_close(left: float, right: float) -> bool:
    if left != left and right != right:
        return True
    scale = max(abs(left), abs(right), 1e-18)
    return abs(left - right) <= 1e-12 * scale


def warmup_kernels() -> None:
    """Compile every kernel once so measurement excludes LLVM time."""
    high = np.array([100, 101, 90, 100], dtype=np.int64)
    low = np.array([99, 100, 80, 99], dtype=np.int64)
    contact_lifecycle_kernel(high, low, np.int64(99), np.int64(100), np.int64(4))
    rearm_contacts_kernel(high, low, np.int64(99), np.int64(100), np.int64(10))
    sweep_displacement_kernel(high, low, np.int64(99), np.int64(100), np.int64(1))
    f2_walk_kernel(np.array([8, 3, 3], dtype=np.int64), np.int64(10), np.int64(180))
    o = np.array([100] * 90, dtype=np.int64)
    h = np.array([110] * 60 + [104] * 30, dtype=np.int64)
    l = np.array([90] * 60 + [100] * 30, dtype=np.int64)
    c = np.array([100] * 90, dtype=np.int64)
    f3_first_kernel(o, h, l, c)
    s1_machine_kernel(high, low, np.array([99, 100, 100, 100], dtype=np.int64), np.int64(99), np.int64(100), np.int64(1), np.int64(0), np.int64(3))
    s2_machine_kernel(high, low, np.array([99, 100, 100, 102], dtype=np.int64), np.int64(99), np.int64(100), np.int64(1), np.int64(0), np.int64(3))
    s3_machine_kernel(
        high,
        low,
        np.array([99, 100, 100, 100], dtype=np.int64),
        np.int64(99),
        np.int64(100),
        np.int64(1),
        np.int64(0),
        np.int64(3),
        0.5,
        np.int64(1),
        0.1,
        np.int64(1),
        np.int64(0),
    )
    s4_machine_kernel(
        np.array([0, 5, 1, 1], dtype=np.int64),
        np.int64(2),
        np.array([0, 1, 1, 1], dtype=np.int64),
        np.int64(2),
        np.array([100, 99, 99, 102], dtype=np.int64),
        np.int64(100),
        np.int64(1),
        np.int64(0),
        np.int64(2),
        np.int64(3),
    )
    book_observe_kernel(high, low, np.ones(4, dtype=np.int64), np.ones(4, dtype=np.int64), np.int64(100), np.int64(1))
    profile_accumulate_kernel(high, np.ones(4, dtype=np.int64), np.int64(90), np.int64(20))
    delta_imbalance_kernel(np.array([10, 4, 6], dtype=np.int64), np.array([1, -1, 0], dtype=np.int64))
    c2_fold_kernel(np.array([0, C2_HALF_LIFE_NS], dtype=np.int64), np.array([10, 0], dtype=np.int64), np.array([10, 0], dtype=np.int64), np.int64(C2_HALF_LIFE_NS))
    minute_bars_kernel(
        np.array([0, MINUTE_NS], dtype=np.int64),
        np.array([400, 401], dtype=np.int64),
        np.array([1, 2], dtype=np.int64),
        np.array([1, -1], dtype=np.int64),
        np.array([0, MINUTE_NS], dtype=np.int64),
        np.int64(0),
        np.int64(2 * MINUTE_NS),
    )
    markout_arrays_kernel(
        np.array([1, -1], dtype=np.int64),
        np.array([2, 3], dtype=np.int64),
        np.array([100.0, 101.0], dtype=np.float64),
        np.array([0, 0], dtype=np.int64),
        np.array([101.0, 100.0], dtype=np.float64),
        np.array([30 * NS, 30 * NS], dtype=np.int64),
        np.int64(30 * NS),
        np.int64(60 * NS),
    )


def kernel_inventory() -> dict[str, Any]:
    return {
        "python_references": list(PYTHON_REFERENCE_NAMES),
        "kernels": list(KERNEL_NAMES),
    }


# --------------------------------------------------------------------------
# P15-17 breadth-run kernels (added 2026-09-16). Each one replaces a Python
# loop the P15-17 profile showed on the critical path; each reproduces its
# scalar reference statement for statement so the documents keep their bytes.
# --------------------------------------------------------------------------


@njit(cache=True)
def compact_day_kernel(t_ns, known_at_ns, bid_ticks, ask_ticks, price_ticks, is_trade, bid_sz, ask_sz, tick):
    """Group one account day's tick arrays by event timestamp.

    Scalar reference: the `for gi, start in enumerate(starts)` loop of
    `exits.compact_from_view`. Same grouping, same per-group extrema, same
    single-quote admission test.
    """
    n = t_ns.shape[0]
    g = 0
    for i in range(n):
        if i == 0 or t_ns[i] != t_ns[i - 1]:
            g += 1
    event_ns = np.empty(g, dtype=np.int64)
    available_at_ns = np.empty(g, dtype=np.int64)
    min_bid = np.full(g, np.nan)
    max_bid = np.full(g, np.nan)
    min_ask = np.full(g, np.nan)
    max_ask = np.full(g, np.nan)
    min_trade = np.full(g, np.nan)
    max_trade = np.full(g, np.nan)
    q_avail = np.empty(g, dtype=np.int64)
    q_bid = np.empty(g, dtype=np.float64)
    q_ask = np.empty(g, dtype=np.float64)
    q_n = 0
    gi = -1
    start = 0
    while start < n:
        end = start + 1
        while end < n and t_ns[end] == t_ns[start]:
            end += 1
        gi += 1
        event = t_ns[start]
        event_ns[gi] = event
        known = known_at_ns[start]
        for k in range(start + 1, end):
            if known_at_ns[k] > known:
                known = known_at_ns[k]
        available_at_ns[gi] = event if event > known else known
        b_lo = 0
        b_hi = 0
        b_seen = 0
        a_lo = 0
        a_hi = 0
        a_seen = 0
        t_lo = 0
        t_hi = 0
        t_seen = 0
        for k in range(start, end):
            v = bid_ticks[k]
            if v > 0:
                if b_seen == 0:
                    b_lo = v
                    b_hi = v
                    b_seen = 1
                else:
                    if v < b_lo:
                        b_lo = v
                    if v > b_hi:
                        b_hi = v
            w = ask_ticks[k]
            if w > 0:
                if a_seen == 0:
                    a_lo = w
                    a_hi = w
                    a_seen = 1
                else:
                    if w < a_lo:
                        a_lo = w
                    if w > a_hi:
                        a_hi = w
            p = price_ticks[k]
            if is_trade[k] and p > 0:
                if t_seen == 0:
                    t_lo = p
                    t_hi = p
                    t_seen = 1
                else:
                    if p < t_lo:
                        t_lo = p
                    if p > t_hi:
                        t_hi = p
        if b_seen == 1:
            min_bid[gi] = np.float64(b_lo) * tick
            max_bid[gi] = np.float64(b_hi) * tick
        if a_seen == 1:
            min_ask[gi] = np.float64(a_lo) * tick
            max_ask[gi] = np.float64(a_hi) * tick
        if t_seen == 1:
            min_trade[gi] = np.float64(t_lo) * tick
            max_trade[gi] = np.float64(t_hi) * tick
        last = end - 1
        bt = bid_ticks[last]
        at = ask_ticks[last]
        bsz = bid_sz[last]
        asz = ask_sz[last]
        # `np.unique(pos).size <= 1` for positive ints is exactly min == max;
        # an empty group leaves both at 0, which the bt > 0 test then rejects.
        unique_b_over_one = b_hi != b_lo
        unique_a_over_one = a_hi != a_lo
        if (
            bt > 0
            and at > 0
            and at >= bt
            and bsz > 0
            and asz > 0
            and not unique_b_over_one
            and not unique_a_over_one
        ):
            q_avail[q_n] = available_at_ns[gi]
            q_bid[q_n] = np.float64(bt) * tick
            q_ask[q_n] = np.float64(at) * tick
            q_n += 1
        start = end
    return (
        event_ns,
        available_at_ns,
        min_bid,
        max_bid,
        min_ask,
        max_ask,
        min_trade,
        max_trade,
        q_avail[:q_n].copy(),
        q_bid[:q_n].copy(),
        q_ask[:q_n].copy(),
    )


@njit(cache=True)
def fixed_stop_first_passage_kernel(
    min_bid,
    max_bid,
    min_ask,
    max_ask,
    min_trade,
    max_trade,
    available_at_ns,
    start,
    side,
    stop,
    has_stop,
    objective,
    has_objective,
    bound_ns,
):
    """First batch that resolves a fixed-stop, fixed-objective entry.

    Scalar reference: the `for index in range(start, n)` loop of
    `exits.evaluate_policy_compact` for a policy that never moves the stop
    (E0/E1/E2: `_manage` returns immediately and no update is ever queued).
    The three tests keep the source order -- stop, then objective, then the
    binding deadline -- so a batch that touches both stop and objective is the
    pessimistic stop, and a batch whose availability is already past the
    deadline still loses to a stop printed in that same batch. NaN never
    compares true, which is the `_finite_le`/`_finite_ge` guard.

    Returns (index, code): code 1 stop, 2 objective, 3 deadline, 0 exhausted.
    """
    n = available_at_ns.shape[0]
    for i in range(start, n):
        if has_stop:
            if side == 1:
                v = min_bid[i]
                w = min_trade[i]
                if (v == v and v <= stop) or (w == w and w <= stop):
                    return i, 1
            else:
                v = max_ask[i]
                w = max_trade[i]
                if (v == v and v >= stop) or (w == w and w >= stop):
                    return i, 1
        if has_objective:
            if side == 1:
                v = max_bid[i]
                w = max_trade[i]
                if (v == v and v >= objective) or (w == w and w >= objective):
                    return i, 2
            else:
                v = min_ask[i]
                w = min_trade[i]
                if (v == v and v <= objective) or (w == w and w <= objective):
                    return i, 2
        if available_at_ns[i] >= bound_ns:
            return i, 3
    return -1, 0
