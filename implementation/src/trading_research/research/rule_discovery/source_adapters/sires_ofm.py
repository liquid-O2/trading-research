"""Sires' OFM (order flow model) as the sequence his source describes, on the
order-level aggression boxes.

Origin of the Move pp.3-14, in his words: aggression that "gets nothing" at
one area is the squeeze catalyst ("that cluster of absorbed aggression is the
squeeze catalyst"); the squeeze "releases in one fast move"; "the squeeze
fails often ... That is the trade": "buyers punch to the wall, and this time
the wall wins: sellers regain control and price rolls back through the
catalyst area"; the entry is "on the retest of the failed squeeze" ("Short on
the retest of the failed squeeze, stop above the sellers' aggression"), taken
with an order resting beyond the retest's wick "so only aggressive
continuation can tag it in" (p.12), or passively at the area when "the squeeze
fails with no aggressive orders at the failure at all" (p.14); the stop is
beyond the aggression ("below the aggression is the point where the read is
simply wrong"), or beyond the intermediate wick (p.12).

So one OFM opportunity is ONE catalyst going through FOUR stages in order:

  catalyst  a box of same-side aggressive orders (the box table: two or more
            orders of thirty lots or more inside six points, by one aggressor)
  release   price leaves the box in the aggressors' direction
  failure   a one-minute close back through the box's far side
  retest    price returns to the box from the failure side and is turned

and the trade is AGAINST the catalyst's aggressors (failed buy squeeze: short).
This replaces "every play at every box" (about 970 fills a session on his side
from his own levels; a placebo ticket reproduced 38% of the time).

What the source does not print is the size of "one fast move" and the clocks.
Those are the FITTED constants below, fitted on his eight dated OFM tickets
and named as such; everything else is his sequence.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable, Mapping

TICK = Decimal("0.25")
MINUTE = 60 * 1_000_000_000

#: FITTED: the release must carry price this far beyond the box in the
#: aggressors' direction ("releases in one fast move"); points
RELEASE_POINTS = Decimal("10")
#: FITTED: the release must begin within this many minutes of the catalyst
RELEASE_WINDOW_MIN = 45
#: FITTED: the failure (close back through the box) must follow the release's extreme within this many minutes
FAILURE_WINDOW_MIN = 60
#: FITTED: the retest must follow the failure within this many minutes
RETEST_WINDOW_MIN = 30
#: a retest reaches the box from the failure side to within this distance (points)
RETEST_REACH = Decimal("2")
#: a close back through the box by this much is the failure (the same one-point margin the other Sires mechanics use)
FAIL_MARGIN = Decimal("1")
#: Databento trade side: "B" is a buy aggressor, "A" a sell aggressor
BUY, SELL = "B", "A"


def _d(value) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def ofm_sequences(bars: list[Mapping[str, Any]], boxes: Iterable[Mapping[str, Any]], *, session_open: int, session_end: int) -> list[dict[str, Any]]:
    """Every catalyst that completes release, failure and retest inside the
    session, with each stage's time, in the order the stages complete. Bars are
    one-minute rows (start, end, O, H, L, C); boxes are rows of the box table
    (lo, hi, aggressor, known_at, n_orders, contracts, id)."""
    starts = [int(b["start"]) for b in bars]
    out = []
    for box in boxes:
        aggressor = str(box.get("aggressor"))
        if aggressor not in (BUY, SELL):
            continue  # a box both sides built is not one side's failed squeeze
        lo, hi = _d(box["lo"]), _d(box["hi"])
        known = int(box["known_at"])
        if known >= session_end:
            continue
        up = aggressor == BUY  # buyers squeeze up; their failure is traded short
        side = "short" if up else "long"
        begin = max(known, session_open)
        i = next((k for k, s in enumerate(starts) if s >= begin), None)
        if i is None:
            continue
        # release: price beyond the box by RELEASE_POINTS in the aggressors' direction
        release_i = None
        for k in range(i, len(bars)):
            if int(bars[k]["start"]) > begin + RELEASE_WINDOW_MIN * MINUTE:
                break
            reached = (bars[k]["H"] >= hi + RELEASE_POINTS) if up else (bars[k]["L"] <= lo - RELEASE_POINTS)
            if reached:
                release_i = k
                break
            # a close through the far side before any release: absorbed and broken, not a squeeze
            broken = (bars[k]["C"] <= lo - FAIL_MARGIN) if up else (bars[k]["C"] >= hi + FAIL_MARGIN)
            if broken:
                break
        if release_i is None:
            continue
        # failure: the first close back through the box's far side; the squeeze's extreme is tracked on the way
        extreme = bars[release_i]["H"] if up else bars[release_i]["L"]
        extreme_at = int(bars[release_i]["start"])
        failure_i = None
        for k in range(release_i, len(bars)):
            bar = bars[k]
            if (bar["H"] > extreme) if up else (bar["L"] < extreme):
                extreme, extreme_at = (bar["H"] if up else bar["L"]), int(bar["start"])
            if int(bar["start"]) > extreme_at + FAILURE_WINDOW_MIN * MINUTE:
                break
            through = (bar["C"] <= lo - FAIL_MARGIN) if up else (bar["C"] >= hi + FAIL_MARGIN)
            if through:
                failure_i = k
                break
        if failure_i is None:
            continue
        # retest: price returns to the box from the failure side and does not close back through it
        failure_end = int(bars[failure_i]["end"])
        retest_i = None
        for k in range(failure_i + 1, len(bars)):
            bar = bars[k]
            if int(bar["start"]) > failure_end + RETEST_WINDOW_MIN * MINUTE:
                break
            reclaimed = (bar["C"] >= hi + FAIL_MARGIN) if up else (bar["C"] <= lo - FAIL_MARGIN)
            if reclaimed:
                break  # the squeeze was not a failure after all
            reached = (bar["H"] >= lo - RETEST_REACH) if up else (bar["L"] <= hi + RETEST_REACH)
            if reached:
                retest_i = k
                break
        if retest_i is None:
            continue
        out.append(
            {
                "box": box.get("id"),
                "box_lo": lo,
                "box_hi": hi,
                "aggressor": aggressor,
                "n_orders": int(box.get("n_orders") or 0),
                "contracts": int(box.get("contracts") or 0),
                "side": side,
                "catalyst_at": known,
                "release_at": int(bars[release_i]["end"]),
                "squeeze_extreme": extreme,
                "failure_at": failure_end,
                "retest_index": retest_i,
                "retest_at": int(bars[retest_i]["end"]),
            }
        )
    out.sort(key=lambda s: s["retest_at"])
    return out


def ofm_fills(bars: list[Mapping[str, Any]], sequence: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The two entries the source gives for one completed sequence, each with
    his stop. ``passive`` rests at the box's failure-side edge and is filled by
    the retest itself (p.14); ``aggressive`` rests one tick beyond the retest
    bar's wick and is filled only if the next bars trade through it (p.12)."""
    side = sequence["side"]
    lo, hi = sequence["box_lo"], sequence["box_hi"]
    k = int(sequence["retest_index"])
    retest = bars[k]
    fills = []
    if side == "short":
        edge, beyond_box = lo, hi + TICK
        fills.append({"mode": "ofm_passive", "entry": edge, "at": int(retest["end"]), "stop": beyond_box})
        trigger = retest["L"] - TICK
        wick_stop = retest["H"] + TICK
    else:
        edge, beyond_box = hi, lo - TICK
        fills.append({"mode": "ofm_passive", "entry": edge, "at": int(retest["end"]), "stop": beyond_box})
        trigger = retest["H"] + TICK
        wick_stop = retest["L"] - TICK
    for nxt in bars[k + 1 : k + 4]:
        hit = (nxt["L"] <= trigger) if side == "short" else (nxt["H"] >= trigger)
        if hit:
            fills.append({"mode": "ofm_aggressive", "entry": trigger, "at": int(nxt["end"]), "stop": wick_stop})
            break
        undone = (nxt["C"] >= hi + FAIL_MARGIN) if side == "short" else (nxt["C"] <= lo - FAIL_MARGIN)
        if undone:
            break
    return fills
