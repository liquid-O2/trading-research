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
