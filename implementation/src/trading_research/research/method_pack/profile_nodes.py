"""Profile structure the authors read: high- and low-volume nodes, shelves and
ledges, and the profile's shape.

Sources: an HVN is "a price where volume built up ... price gets drawn back to
these shelves"; an LVN "a price where volume fell away ... price tends to react
at these and traverse them quickly" (Sires, VP2 p.3); "out of balance the
ledges of the prior balance are what hold for the move to continue" (AMT1
p.9); a P-zone is kept where it "sits on an HVN or on the shelf next to an
LVN" (Jumbo, FIND p.8); the shapes are balanced, double distribution (two
shelves and a leg), trending, P and B (Saint, RTVP pp.7-11). The node recipe
(smoothing b, prominence) is the P-zone fit's; both are declared parameters,
not fitted here.

Input: a profile payload as the framework's ``profile()`` returns it (``rows``
of ``price`` and ``total_volume``, ``poc``, ``vah``, ``val``).
"""
from __future__ import annotations

from decimal import Decimal

import numpy as np

try:
    from numba import njit as _njit
except Exception:  # numba absent: the same function, interpreted
    def _njit(*_args, **_kwargs):
        def wrap(fn):
            return fn
        return wrap

SMOOTH = 2
PROMINENCE = 0.20
LEDGE_DROP = 0.5
VALUE_FRACTION = Decimal("0.70")


def composite(payloads: list[dict], *, fraction: Decimal = VALUE_FRACTION) -> dict | None:
    """Several sessions' profiles merged by price (Sires' composite, VP2 p.6;
    Saint's daily/weekly profile, WIC): rows, POC (the largest bin, lowest
    price on a tie) and the value area holding ``fraction`` of the volume,
    grown from the POC by the larger adjacent bin."""
    merged: dict[Decimal, Decimal] = {}
    for payload in payloads or []:
        for r in payload.get("rows") or []:
            px = Decimal(str(r.get("price")))
            merged[px] = merged.get(px, Decimal(0)) + Decimal(str(r.get("total_volume") or 0))
    if not merged:
        return None
    rows = [{"price": px, "total_volume": v} for px, v in sorted(merged.items())]
    total = sum(r["total_volume"] for r in rows)
    poc_i = min(range(len(rows)), key=lambda i: (-rows[i]["total_volume"], rows[i]["price"]))
    lo = hi = poc_i
    acc = rows[poc_i]["total_volume"]
    while acc < total * fraction and (lo > 0 or hi < len(rows) - 1):
        left = rows[lo - 1]["total_volume"] if lo > 0 else None
        right = rows[hi + 1]["total_volume"] if hi < len(rows) - 1 else None
        if right is None or (left is not None and left >= right):
            lo -= 1
            acc += left
        else:
            hi += 1
            acc += right
    return {"rows": rows, "poc": rows[poc_i]["price"], "val": rows[lo]["price"], "vah": rows[hi]["price"], "sessions": len(payloads or [])}


def _series(payload: dict, smooth: int = SMOOTH):
    rows = payload.get("rows") or []
    prices = [Decimal(str(r.get("price"))) for r in rows]
    vol = np.array([float(r.get("total_volume") or 0) for r in rows], dtype=float)
    if smooth > 0 and vol.size:
        kernel = np.ones(2 * smooth + 1) / (2 * smooth + 1)
        vol = np.convolve(vol, kernel, mode="same")
    return prices, vol


def _prominence(vol, i: int) -> float:
    """Topographic prominence of the local maximum at ``i``: its height above
    the higher of the two troughs met before the volume rises above it again
    (or the profile's edge) on each side."""
    n = len(vol)
    left = vol[i]
    k = i - 1
    while k >= 0 and vol[k] <= vol[i]:
        left = min(left, vol[k])
        k -= 1
    right = vol[i]
    k = i + 1
    while k < n and vol[k] <= vol[i]:
        right = min(right, vol[k])
        k += 1
    return float(vol[i] - max(left, right))


@_njit(cache=True)
def _mark_extrema(vol, floor):  # pragma: no cover - compiled
    """1 where ``vol`` has a local maximum of prominence >= floor, 2 where it
    has a local minimum of prominence >= floor (on the negated series), else 0;
    index for index the decisions of the ``nodes`` loop over ``_prominence``."""
    n = vol.shape[0]
    out = np.zeros(n, dtype=np.int8)
    for i in range(1, n - 1):
        v = vol[i]
        if v >= vol[i - 1] and v > vol[i + 1]:
            left = v
            k = i - 1
            while k >= 0 and vol[k] <= v:
                if vol[k] < left:
                    left = vol[k]
                k -= 1
            right = v
            k = i + 1
            while k < n and vol[k] <= v:
                if vol[k] < right:
                    right = vol[k]
                k += 1
            trough = left if left > right else right
            if v - trough >= floor:
                out[i] = 1
        elif v <= vol[i - 1] and v < vol[i + 1]:
            # the same walk on -vol: troughs of -vol are crests of vol
            left = v
            k = i - 1
            while k >= 0 and vol[k] >= v:
                if vol[k] > left:
                    left = vol[k]
                k -= 1
            right = v
            k = i + 1
            while k < n and vol[k] >= v:
                if vol[k] > right:
                    right = vol[k]
                k += 1
            crest = left if left < right else right
            if crest - v >= floor:
                out[i] = 2
    return out


def nodes(payload: dict, *, smooth: int = SMOOTH, prominence: float = PROMINENCE) -> tuple[list[Decimal], list[Decimal]]:
    """(HVN prices, LVN prices): local maxima and minima of the smoothed
    volume at price whose prominence (against the neighbouring troughs, or
    crests for a minimum, however far they sit) is at least ``prominence`` of
    the profile's peak. A trough between two overnight distributions can be
    tens of points wide (MAMT p.16), so prominence is not measured inside a
    fixed window."""
    prices, vol = _series(payload, smooth)
    if len(prices) < 5:
        return [], []
    peak = float(vol.max())
    if peak <= 0:
        return [], []
    floor = prominence * peak
    hvn, lvn = [], []
    # one compiled pass marks every qualifying extremum (the per-index Python
    # walk cost 35 s a session on the selection dataset, 2026-09-18); the
    # comparisons are the ones _prominence makes, on the same float64 values
    marks = _mark_extrema(np.ascontiguousarray(vol, dtype=np.float64), float(floor))
    for i in np.nonzero(marks)[0]:
        (hvn if marks[i] == 1 else lvn).append(prices[int(i)])
    return hvn, lvn


def ledges(payload: dict, *, smooth: int = SMOOTH, prominence: float = PROMINENCE, drop: float = LEDGE_DROP) -> list[Decimal]:
    """Shelf edges: from each LVN walk toward the nearest HVN on each side; the
    ledge is the first price where the smoothed volume reaches ``drop`` of that
    shelf's peak."""
    prices, vol = _series(payload, smooth)
    if len(prices) < 5:
        return []
    hvn, lvn = nodes(payload, smooth=smooth, prominence=prominence)
    index = {p: i for i, p in enumerate(prices)}
    out: list[Decimal] = []
    for low in lvn:
        i = index.get(low)
        if i is None:
            continue
        for direction in (-1, 1):
            peak = None
            for h in sorted(hvn, key=lambda p: abs(p - low)):
                if (h < low and direction < 0) or (h > low and direction > 0):
                    peak = index.get(h)
                    break
            if peak is None:
                continue
            step = 1 if peak > i else -1
            k = i
            while k != peak:
                k += step
                if vol[k] >= drop * vol[peak]:
                    out.append(prices[k])
                    break
    return sorted(set(out))


def on_node_or_ledge(price: Decimal, payload: dict, tolerance: Decimal) -> bool:
    """Jumbo's P-zone keep rule (FIND p.8): the price sits on an HVN or on the
    shelf next to an LVN (a ledge) within ``tolerance``."""
    hvn, _lvn = nodes(payload)
    if any(abs(p - price) <= tolerance for p in hvn):
        return True
    return any(abs(p - price) <= tolerance for p in ledges(payload))


def shape(payload: dict, *, smooth: int = SMOOTH) -> str:
    """Saint's five shapes (RTVP pp.7-11), read from the smoothed volume at
    price: ``trending`` (no bell: the peak's share of the range is low and
    volume is spread), ``double_distribution`` (two separated shelves with a
    trough between), ``p`` (the bulge in the upper third with a thin stem
    below), ``b`` (the bulge in the lower third), else ``balanced``."""
    prices, vol = _series(payload, smooth)
    if len(prices) < 8 or float(vol.max()) <= 0:
        return "unknown"
    total = float(vol.sum())
    n = len(vol)
    # where the volume sits: the share of volume in each third of the price range
    thirds = [float(vol[: n // 3].sum()) / total, float(vol[n // 3: 2 * n // 3].sum()) / total, float(vol[2 * n // 3:].sum()) / total]
    peak = float(vol.max())
    # the two largest separated peaks (prominence rule) tell a double distribution
    hvn, lvn = nodes(payload, smooth=smooth, prominence=0.30)
    if len(hvn) >= 2 and lvn:
        top_two = sorted(hvn, key=lambda p: -vol[prices.index(p)])[:2]
        lo, hi = min(top_two), max(top_two)
        between = [p for p in lvn if lo < p < hi]
        if between and (hi - lo) >= (prices[-1] - prices[0]) * Decimal("0.25"):
            return "double_distribution"
    spread = float((vol > 0.35 * peak).mean())  # share of the price range holding at least 35% of the peak volume
    if spread >= 0.7:
        return "trending"
    if thirds[2] >= 0.5 and thirds[0] <= 0.2:
        return "p"
    if thirds[0] >= 0.5 and thirds[2] <= 0.2:
        return "b"
    return "balanced"
