"""Shared G-default touch / reject / hold / break on 1-minute bars."""

from __future__ import annotations

import numpy as np

TICK = 0.25
G_DEFAULT = {
    "touch": "t2",
    "touch_ticks": 2,
    "break": "b.c1",
    "reject_r": 0.5,
    "reject_k_min": 15,
    "hold_h_min": 30,
    "failback": "b.c5",
    "failback_k_min": 30,
}


def to_ticks(price) -> np.ndarray:
    return np.round(np.asarray(price, dtype=np.float64) / TICK).astype(np.int64)


def first_close_break(close_ticks: np.ndarray, t_ms: np.ndarray, edge: int, side: int) -> int | None:
    """side +1 breaks above edge, -1 breaks below. Returns bar start ms or None."""
    if side == 1:
        hit = close_ticks > edge
    else:
        hit = close_ticks < edge
    idx = np.flatnonzero(hit)
    if idx.size == 0:
        return None
    return int(t_ms[int(idx[0])])


def first_wick_break(high_ticks: np.ndarray, low_ticks: np.ndarray, t_ms: np.ndarray,
                     edge: int, side: int, depth_ticks: int = 2) -> int | None:
    if side == 1:
        hit = high_ticks >= edge + depth_ticks
    else:
        hit = low_ticks <= edge - depth_ticks
    idx = np.flatnonzero(hit)
    if idx.size == 0:
        return None
    return int(t_ms[int(idx[0])])


def resample_close(t_ms: np.ndarray, close_ticks: np.ndarray, every_ms: int) -> tuple[np.ndarray, np.ndarray]:
    if t_ms.size == 0:
        return t_ms, close_ticks
    bucket = (t_ms - t_ms[0]) // every_ms
    ends = np.r_[np.flatnonzero(bucket[1:] != bucket[:-1]) + 1, bucket.size]
    return t_ms[ends - 1], close_ticks[ends - 1]


def path_class_from_closes(close_ticks: np.ndarray, t_ms: np.ndarray, high: int, low: int) -> dict:
    up = first_close_break(close_ticks, t_ms, high, 1)
    down = first_close_break(close_ticks, t_ms, low, -1)
    if up is None and down is None:
        klass, order = "neither", None
    elif up is None:
        klass, order = "low-only", "low"
    elif down is None:
        klass, order = "high-only", "high"
    else:
        klass = "both"
        if up == down:
            order = "ambiguous"
        elif up < down:
            order = "high-then-low"
        else:
            order = "low-then-high"
    return {
        "path_class": klass,
        "break_order": order,
        "first_high_break_ms": up,
        "first_low_break_ms": down,
    }


def touch_level(high_ticks, low_ticks, t_ms, level: int, tol_ticks: int) -> int | None:
    hit = (low_ticks <= level + tol_ticks) & (high_ticks >= level - tol_ticks)
    idx = np.flatnonzero(hit)
    if idx.size == 0:
        return None
    return int(t_ms[int(idx[0])])


def reject_after_touch(close_ticks, t_ms, touch_ms, level: int, side: int, r_ticks: int, k_ms: int) -> bool:
    """After touch, close returns r_ticks onto the original side within k_ms without b.c1."""
    if touch_ms is None:
        return False
    start = int(np.searchsorted(t_ms, touch_ms, "left"))
    end_ms = touch_ms + k_ms
    i = start
    while i < t_ms.size and t_ms[i] <= end_ms:
        c = int(close_ticks[i])
        if side == 1 and c > level:
            return False
        if side == -1 and c < level:
            return False
        if side == 1 and c <= level - r_ticks:
            return True
        if side == -1 and c >= level + r_ticks:
            return True
        i += 1
    return False


def hold_after_break(close_ticks, t_ms, break_ms, level: int, side: int, h_ms: int) -> bool:
    """After b.c1, every 1-minute close stays beyond the level for h_ms."""
    if break_ms is None or t_ms.size == 0:
        return False
    start = int(np.searchsorted(t_ms, break_ms, "left"))
    end_ms = break_ms + h_ms
    if start >= t_ms.size:
        return False
    i = start
    last = None
    while i < t_ms.size and t_ms[i] <= end_ms:
        c = int(close_ticks[i])
        if side == 1 and c <= level:
            return False
        if side == -1 and c >= level:
            return False
        last = int(t_ms[i])
        i += 1
    return last is not None and last >= end_ms - 60_000


def failback_wick_c5(high_ticks, low_ticks, close_ticks, t_ms, high: int, low: int, k_min: int = 30) -> tuple[bool, bool]:
    """Wick beyond high or low, then a 5-minute close back inside within k_min."""
    if t_ms.size < 5:
        return False, False
    wick_up = first_wick_break(high_ticks, low_ticks, t_ms, high, 1, 2)
    wick_dn = first_wick_break(high_ticks, low_ticks, t_ms, low, -1, 2)
    first = None
    if wick_up is None:
        first = wick_dn
    elif wick_dn is None:
        first = wick_up
    else:
        first = min(wick_up, wick_dn)
    if first is None:
        return False, False
    t5, c5 = resample_close(t_ms, close_ticks, 5 * 60_000)
    limit = first + k_min * 60_000
    for ts, cl in zip(t5, c5):
        if ts < first:
            continue
        if ts > limit:
            break
        if low < int(cl) < high:
            return True, True
    return True, False


def outcomes_at_level(window: dict, level_px: float, *, width: float, side: int,
                      reject_r: float = 0.5, reject_k_min: int = 15, hold_h_min: int = 30) -> dict:
    """G-default at one price. side +1 is resistance (reject down), -1 is support (reject up)."""
    empty = {"touch": False, "touch_ms": None, "wick": False, "close_break": False,
             "reject": False, "hold": False}
    if window["n"] == 0 or level_px is None or not width:
        return empty
    level = int(round(level_px / TICK))
    ht = to_ticks(window["h"])
    lt = to_ticks(window["l"])
    ct = to_ticks(window["c"])
    t = window["t"]
    touch_ms = touch_level(ht, lt, t, level, G_DEFAULT["touch_ticks"])
    wick_ms = first_wick_break(ht, lt, t, level, side, 2)
    c1_ms = first_close_break(ct, t, level, side)
    r_ticks = max(1, int(round(reject_r * width / TICK)))
    return {
        "touch": touch_ms is not None,
        "touch_ms": touch_ms,
        "wick": wick_ms is not None,
        "close_break": c1_ms is not None,
        "reject": reject_after_touch(ct, t, touch_ms, level, side, r_ticks, reject_k_min * 60_000),
        "hold": hold_after_break(ct, t, c1_ms, level, side, hold_h_min * 60_000),
    }
