"""The Refill Effect's zones and touches, from the trade tape.

The paper (Ethos Order Flow, The Refill Effect, pp.5-12, 23): "When a burst of
large aggressive market orders trades at one price area ... that area stops
being a random price ... We call the cluster of prints a zone. The next time
price returns to the zone, exactly one question matters: are the defenders
still there?" "Price leaves, then returns: that is the touch." Every touch is
an event with a known outcome, "the level held, or it broke", and about twenty
pre-touch features in four families (memory, construction, location, flow and
state) grade it. Its published numbers are the acceptance test of any
reconstruction: 41,152 touches over 235 regular sessions (about 175 a
session), 42% of touches hold, the median eventual winner dips 18 ticks past
the touch, and the deployed trade rests a limit 12 ticks inside the level with
a 32-tick stop and a 96-tick target, cancelled after 30 minutes.

The paper does not print its numeric definitions of "leaves", "returns" and
"held". Those are the CALIBRATED constants below: chosen so that the
reconstruction lands on the paper's own base rates over the paper's own
period, and named as such. Everything a touch knows is known before it
resolves; the outcome fields carry the ``label_`` prefix.
"""
from __future__ import annotations

from typing import Any

import numpy as np

try:
    from numba import njit as _njit
except Exception:  # numba absent: the same loops, interpreted

    def _njit(*_args, **_kwargs):
        def wrap(fn):
            return fn

        return wrap


TICK = 0.25
#: CALIBRATED: price has left a zone once it trades this many points beyond the zone's edge
LEAVE_POINTS = 5.0
#: CALIBRATED: a touch holds when price moves this far back out of the zone (from the touched edge) ...
HOLD_POINTS = 8.0
#: ... before it trades this far through the zone's far edge (the break); 32 ticks each, the paper's 1R
BREAK_POINTS = 8.0
#: the break is measured from the TOUCHED edge (a symmetric bounce-or-penetrate test), not from the zone's far edge
BREAK_FROM_EDGE = True
#: a touch still unresolved this long after it happened is neither (the paper cancels a resting order after 30 minutes)
RESOLVE_SECONDS = 1800


@_njit(cache=True)
def _touches(t, px, zone_lo, zone_hi, zone_known, leave, hold, brk, resolve_ns, from_edge):  # pragma: no cover - compiled
    """For every zone, every touch: (zone index, trade index of the touch, side
    +1 support / -1 resistance, outcome 1 held / -1 broke / 0 unresolved, trade
    index of the resolution, deepest penetration past the touched edge in
    points before the resolution)."""
    n = t.shape[0]
    cap = 64 * zone_lo.shape[0] + 1024
    zi = np.empty(cap, dtype=np.int64)
    ti = np.empty(cap, dtype=np.int64)
    side = np.empty(cap, dtype=np.int8)
    outcome = np.empty(cap, dtype=np.int8)
    ri = np.empty(cap, dtype=np.int64)
    dip = np.empty(cap, dtype=np.float64)
    count = 0
    for z in range(zone_lo.shape[0]):
        lo = zone_lo[z]
        hi = zone_hi[z]
        start = np.searchsorted(t, zone_known[z])
        state = 0  # 0 inside or near, +1 away above, -1 away below
        i = start
        while i < n and count < cap:
            p = px[i]
            if p >= hi + leave:
                state = 1
            elif p <= lo - leave:
                state = -1
            elif state == 1 and p <= hi:
                # came down into the zone from above: a support touch at the top edge
                edge = hi
                deepest = 0.0
                res = 0
                j = i
                limit = t[i] + resolve_ns
                while j < n and t[j] <= limit:
                    q = px[j]
                    if edge - q > deepest:
                        deepest = edge - q
                    if q <= (edge if from_edge else lo) - brk:
                        res = -1
                        break
                    if q >= edge + hold:
                        res = 1
                        break
                    j += 1
                if j >= n:
                    j = n - 1
                zi[count] = z
                ti[count] = i
                side[count] = 1
                outcome[count] = res
                ri[count] = j
                dip[count] = deepest
                count += 1
                state = 0
                i = j
            elif state == -1 and p >= lo:
                edge = lo
                deepest = 0.0
                res = 0
                j = i
                limit = t[i] + resolve_ns
                while j < n and t[j] <= limit:
                    q = px[j]
                    if q - edge > deepest:
                        deepest = q - edge
                    if q >= (edge if from_edge else hi) + brk:
                        res = -1
                        break
                    if q <= edge - hold:
                        res = 1
                        break
                    j += 1
                if j >= n:
                    j = n - 1
                zi[count] = z
                ti[count] = i
                side[count] = -1
                outcome[count] = res
                ri[count] = j
                dip[count] = deepest
                count += 1
                state = 0
                i = j
            i += 1
    return zi[:count], ti[:count], side[:count], outcome[:count], ri[:count], dip[:count]


def zone_touches(t, px, zones: list[dict[str, Any]], *, begin: int, end: int, leave: float | None = None, hold: float | None = None, brk: float | None = None, resolve_s: int | None = None, break_from_edge: bool | None = None) -> list[dict[str, Any]]:
    """Every touch of every zone between ``begin`` and ``end``, in time order.
    A zone is touchable from the moment it is known. The side is the fade:
    a zone reached from above is support (long), from below resistance
    (short), "buying every support touch, selling every resistance touch"."""
    if not zones or len(t) == 0:
        return []
    lo = np.array([float(z["lo"]) for z in zones])
    hi = np.array([float(z["hi"]) for z in zones])
    known = np.array([max(int(z["known_at"]) + 1, begin) for z in zones], dtype=np.int64)
    zi, ti, side, outcome, ri, dip = _touches(
        np.ascontiguousarray(t, dtype=np.int64),
        np.ascontiguousarray(px, dtype=np.float64),
        lo,
        hi,
        known,
        float(LEAVE_POINTS if leave is None else leave),
        float(HOLD_POINTS if hold is None else hold),
        float(BREAK_POINTS if brk is None else brk),
        int((RESOLVE_SECONDS if resolve_s is None else resolve_s) * 1_000_000_000),
        bool(BREAK_FROM_EDGE if break_from_edge is None else break_from_edge),
    )
    out = []
    for k in range(len(zi)):
        at = int(t[ti[k]])
        if not (begin <= at < end):
            continue
        out.append(
            {
                "zone": int(zi[k]),
                "at": at,
                "trade_index": int(ti[k]),
                "side": "long" if side[k] > 0 else "short",
                "edge": float(hi[zi[k]] if side[k] > 0 else lo[zi[k]]),
                "label_outcome": "held" if outcome[k] > 0 else ("broke" if outcome[k] < 0 else "unresolved"),
                "label_resolved_at": int(t[ri[k]]),
                "label_dip_points": float(dip[k]),
            }
        )
    out.sort(key=lambda r: r["at"])
    return out
