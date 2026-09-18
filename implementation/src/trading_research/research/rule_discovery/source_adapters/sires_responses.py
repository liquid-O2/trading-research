"""Sires' entry at failed aggression, from the trade tape.

His words (Only Trade Big Trades p.4, p.13; NY AM Session p.4): "Aggression is
effort. The candle that follows is the reward, or the absence of one. Effort
that gets paid is control. Effort that gets nothing is exhaustion." "The
version he wants is a sequence, and the order matters. First the opposition's
aggression fails, so they are exhausted, trapped or absorbed. Then your side
arrives aggressively." "Sellers had pushed lower and gotten nothing for it, so
price refilled straight back into the buyers defending that level ... stop
just below these buyers that are in control."

On the tape that is two facts, both known when they happen:

* the FAILURE: a big aggressive order (his Big Trades floor, 30 lots on NQ)
  is traded back through. Sellers who hit 29,249 and see 29,250 print again
  within minutes were paid nothing, whatever happened in between;
* the ARRIVAL: the first big aggressive order of the other side after that.

An opportunity is one failure: orders taken back by the same trade are one,
and a later failure beside a live one adds nothing (it never rewrites what
was decided; once the live one's stop trades, the next failure is new). It
has two fills: ``reclaim`` (the trade that takes the failed order's price back) and
``arrival`` (the arriving order's price, when one comes). The stop rests a
tick beyond the extreme made since the failed order printed, "just below
these buyers". His tickets that are this entry: 2026-08-06 09:33 (S53 at
29,249 and S30 at 29,242 fail, B31 arrives at 29,254.25, he buys 29,258 with
the stop at 29,242), 2026-08-06 10:04, 2026-08-04 09:31, 2026-07-09 09:51
(S44 at 29,855.25 taken back, he buys 29,856), 2026-07-14 09:37,
2026-08-06 09:36.

Everything an event carries is known at its ``decision_at``. Where the
failure sits (the session extreme, a zone, the higher-timeframe thesis) is
his selection, recorded as features by the population runner, not gated here.
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
#: his Big Trades floor on NQ ("a minimum of 30 contracts", Big Trades p.3)
MIN_LOTS = 30
#: CALIBRATED: the failed order's own price must be taken back by this much (a tick is noise at a 30-lot print)
RECLAIM_POINTS = 1.0
#: CALIBRATED: how long an order has to be paid before a reclaim no longer reads as ITS failure
FAIL_WINDOW_S = 300
#: CALIBRATED: the other side's first big order counts as the arrival this long after the reclaim
ARRIVAL_WINDOW_S = 120
#: failures of one side this close in time and price are one opportunity
MERGE_S = 60
MERGE_POINTS = 10.0


@_njit(cache=True)
def _reclaims(t, px, order_t, order_sign, order_ref, reclaim, window_ns):  # pragma: no cover - compiled
    """For every big order: the index of the first trade that takes its
    reference price back by ``reclaim`` within the window (-1 if none), the
    extreme traded in the order's direction before that, and whether the
    order was ever paid (a trade beyond its reference in its own direction)."""
    n = order_t.shape[0]
    hit = np.full(n, -1, dtype=np.int64)
    extreme = np.empty(n, dtype=np.float64)
    m = t.shape[0]
    for k in range(n):
        s = order_sign[k]
        ref = order_ref[k]
        i = np.searchsorted(t, order_t[k], side="right")
        limit = order_t[k] + window_ns
        worst = ref
        while i < m and t[i] <= limit:
            p = px[i]
            if s < 0:
                if p < worst:
                    worst = p
                if p >= ref + reclaim:
                    hit[k] = i
                    break
            else:
                if p > worst:
                    worst = p
                if p <= ref - reclaim:
                    hit[k] = i
                    break
            i += 1
        extreme[k] = worst
    return hit, extreme


def failed_aggression(t, px, size, sign, *, begin: int, end: int, min_lots: int | None = None, reclaim: float | None = None, fail_window_s: int | None = None, arrival_window_s: int | None = None) -> list[dict[str, Any]]:
    """Every failure of big aggression decided in [begin, end), in time
    order, with its two fills. ``t, px, size, sign`` is the tape from far
    enough before ``begin`` that an order printed before it can fail inside."""
    from trading_research.research.method_pack.trade_tape import aggressive_orders

    min_lots = MIN_LOTS if min_lots is None else min_lots
    reclaim = RECLAIM_POINTS if reclaim is None else reclaim
    fail_ns = int((FAIL_WINDOW_S if fail_window_s is None else fail_window_s) * 1_000_000_000)
    arrival_ns = int((ARRIVAL_WINDOW_S if arrival_window_s is None else arrival_window_s) * 1_000_000_000)
    if len(t) == 0:
        return []
    ot, osg, lots, olo, ohi = aggressive_orders(t, px, size, sign)
    big = lots >= min_lots
    ot, osg, lots, olo, ohi = ot[big], osg[big], lots[big], olo[big], ohi[big]
    if len(ot) == 0:
        return []
    # sellers are wrong once their BEST price is taken back, buyers once theirs is
    ref = np.where(osg < 0, ohi, olo).astype(np.float64)
    hit, extreme = _reclaims(np.ascontiguousarray(t, dtype=np.int64), np.ascontiguousarray(px, dtype=np.float64), np.ascontiguousarray(ot, dtype=np.int64), np.ascontiguousarray(osg, dtype=np.int64), ref, float(reclaim), fail_ns)
    failed = [k for k in np.flatnonzero(hit >= 0) if begin <= int(t[hit[k]]) < end]
    failed.sort(key=lambda k: (int(hit[k]), int(k)))
    events: list[dict[str, Any]] = []
    alive: dict[str, dict[str, Any]] = {}
    for k in failed:
        at = int(t[hit[k]])
        side = "long" if osg[k] < 0 else "short"
        last = alive.get(side)
        if last is not None and int(hit[k]) == last["trade_index"]:
            # failing on the SAME trade: one opportunity, every fact of it known at that trade
            last["failed_orders"] += 1
            last["failed_contracts"] += int(lots[k])
            last["failed_largest"] = max(last["failed_largest"], int(lots[k]))
            last["extreme"] = min(last["extreme"], float(extreme[k])) if side == "long" else max(last["extreme"], float(extreme[k]))
            last["first_failed_at"] = min(last["first_failed_at"], int(ot[k]))
            continue
        if last is not None and at - last["decision_at"] <= MERGE_S * 1_000_000_000 and abs(float(ref[k]) - last["failed_ref"]) <= MERGE_POINTS:
            # a later failure beside a live one is the same opportunity and changes nothing already decided;
            # once the live one's stop has traded, the next failure is a new opportunity with its own extreme
            between = px[last["trade_index"] + 1 : int(hit[k]) + 1]
            stop = last["extreme"] - TICK if side == "long" else last["extreme"] + TICK
            stopped = bool(len(between)) and (float(between.min()) <= stop if side == "long" else float(between.max()) >= stop)
            if not stopped:
                continue
        event = {
            "side": side,
            "decision_at": at,
            "trade_index": int(hit[k]),
            "entry": float(px[hit[k]]),
            "failed_ref": float(ref[k]),
            "failed_orders": 1,
            "failed_contracts": int(lots[k]),
            "failed_largest": int(lots[k]),
            "first_failed_at": int(ot[k]),
            "extreme": float(extreme[k]),
        }
        events.append(event)
        alive[side] = event
    for event in events:
        long = event["side"] == "long"
        event["stop"] = event["extreme"] - TICK if long else event["extreme"] + TICK
        event["seconds_to_fail"] = round((event["decision_at"] - event["first_failed_at"]) / 1e9, 1)
        # how far the failed side was paid before it lost it all
        event["paid_points"] = round(event["failed_ref"] - event["extreme"], 2) if long else round(event["extreme"] - event["failed_ref"], 2)
        want = 1 if long else -1
        a = int(np.searchsorted(ot, event["decision_at"], side="left"))
        arrival = None
        while a < len(ot) and ot[a] <= event["decision_at"] + arrival_ns:
            if osg[a] == want:
                arrival = a
                break
            a += 1
        if arrival is None:
            event["arrival"] = None
            continue
        # the arrival is decided at ITS time: its stop is beyond the extreme made up to then
        upto = px[event["trade_index"] : int(np.searchsorted(t, ot[arrival], side="right"))]
        worst = min(event["extreme"], float(upto.min())) if long else max(event["extreme"], float(upto.max()))
        event["arrival"] = {"decision_at": int(ot[arrival]), "entry": float(ohi[arrival] if long else olo[arrival]), "lots": int(lots[arrival]), "stop": worst - TICK if long else worst + TICK}
    return events
