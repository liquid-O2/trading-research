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

from bisect import bisect_left
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


def _known(bar: Mapping[str, Any]) -> int:
    """When a bar is known complete: its ``known_at`` where the bar type has one (range bars), else its end."""
    return int(bar.get("known_at") or bar["end"])


def ofm_sequences(bars: list[Mapping[str, Any]], boxes: Iterable[Mapping[str, Any]], *, session_open: int, session_end: int) -> list[dict[str, Any]]:
    """Every catalyst that completes release, failure and retest inside the
    session, with each stage's time, in the order the stages complete. Bars are
    one-minute rows (start, end, O, H, L, C); boxes are rows of the box table
    (lo, hi, aggressor, known_at, n_orders, contracts, id)."""
    # a bar counts once it is known complete: a one-minute bar at its end, a
    # range bar when the next bar opens (``known_at``); an incomplete last
    # range bar is not read
    bars = [b for b in bars if b.get("complete", True)]
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
        i = bisect_left(starts, begin)
        if i >= len(bars):
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
        failure_end = _known(bars[failure_i])
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
                "release_at": _known(bars[release_i]),
                "squeeze_extreme": extreme,
                "failure_at": failure_end,
                "retest_index": retest_i,
                "retest_at": _known(bars[retest_i]),
                "retest_bar": bars[retest_i],
                "bars_after_retest": bars[retest_i + 1 : retest_i + 4],
            }
        )
    out.sort(key=lambda s: s["retest_at"])
    return out


#: the box table's construction (tools/sires_levels_fit.cluster_orders, edge anchor):
#: a big order joins a box while it lies within BOX_BAND points of the box's
#: edges and within BOX_WINDOW_S seconds of its last order
BOX_BAND = 6.0
BOX_WINDOW_S = 180


def cluster_boxes(order_t, order_sign, lots, low, high, *, band: float = BOX_BAND, window_s: int = BOX_WINDOW_S, min_orders: int = 2) -> list[dict[str, Any]]:
    """Big aggressive orders chained by PRICE into boxes, the same rule the
    box table is built with, so an area where one side's aggression printed
    repeatedly is one object with a memory. ``known_at`` is the box's last
    order (its edges are final then); the aggressor is the side of its largest
    order, and ``sides`` says whether both sides printed in it."""
    boxes: list[dict[str, Any]] = []
    for k in range(len(order_t)):
        t, lo, hi, size, sign = int(order_t[k]), float(low[k]), float(high[k]), int(lots[k]), int(order_sign[k])
        for box in boxes:
            if lo <= box["hi"] + band and hi >= box["lo"] - band and t - box["last_t"] <= window_s * 1_000_000_000:
                box["lo"], box["hi"], box["last_t"] = min(box["lo"], lo), max(box["hi"], hi), t
                box["orders"].append((t, size, sign, lo, hi))
                break
        else:
            boxes.append({"lo": lo, "hi": hi, "last_t": t, "orders": [(t, size, sign, lo, hi)]})
    out = []
    for box in boxes:
        if len(box["orders"]) < min_orders:
            continue
        largest = max(box["orders"], key=lambda o: o[1])
        signs = {o[2] for o in box["orders"]}
        out.append(
            {
                "id": f"box:{box['last_t']}:{box['lo']}:{box['hi']}",
                "lo": _d(box["lo"]),
                "hi": _d(box["hi"]),
                "known_at": box["last_t"],
                "n_orders": len(box["orders"]),
                "contracts": sum(o[1] for o in box["orders"]),
                "largest": largest[1],
                "aggressor": BUY if largest[2] > 0 else SELL,
                "sides": "AB" if len(signs) > 1 else (BUY if 1 in signs else SELL),
            }
        )
    return out


#: FITTED on his dated OFM tickets, whose whole sequence runs three to five
#: minutes ("violent and quick", p.5): seconds from the catalyst's last order to
#: the release, from the squeeze's extreme to the failure, from the failure to the retest
RUN_RELEASE_S = 180
RUN_FAILURE_S = 300
RUN_RETEST_S = 180
#: orders of one side chain into a run while the next comes within this many seconds (the box table's window)
RUN_GAP_S = 180
#: FITTED: a run's prints span at most this many points; a wider drive is not one absorbed area
RUN_SPAN = Decimal("25")


def aggression_runs(order_t, order_sign, lots, low, high, *, gap_s: int = RUN_GAP_S, span: Decimal = RUN_SPAN) -> list[dict[str, Any]]:
    """Runs of same-side big aggressive orders chained in TIME: the next order
    of the side joins while it arrives within ``gap_s`` of the last and keeps
    the run's prints inside ``span`` points. The paper's catalyst is "multiple
    buyers' aggression being absorbed" and it is "drawn at the lowest
    aggression" (p.8): for a buy run the line is its lowest print, for a sell
    run its highest. Each run lists its orders in time order so a reader can
    take it as it stood at any moment."""
    open_runs: dict[int, dict[str, Any]] = {}
    runs: list[dict[str, Any]] = []
    for k in range(len(order_t)):
        sign = int(order_sign[k])
        order = {"t": int(order_t[k]), "lots": int(lots[k]), "low": _d(float(low[k])), "high": _d(float(high[k]))}
        run = open_runs.get(sign)
        if run is not None:
            lo = min(run["orders"][0]["low"], *[o["low"] for o in run["orders"]], order["low"])
            hi = max(run["orders"][0]["high"], *[o["high"] for o in run["orders"]], order["high"])
            if order["t"] - run["orders"][-1]["t"] <= gap_s * 1_000_000_000 and hi - lo <= span:
                run["orders"].append(order)
                continue
        run = {"sign": sign, "orders": [order]}
        open_runs[sign] = run
        runs.append(run)
    return [r for r in runs if len(r["orders"]) >= 2]


def ofm_sequences_from_runs(bars: list[Mapping[str, Any]], runs: Iterable[Mapping[str, Any]], *, session_open: int, session_end: int, release_s: int | None = None, failure_s: int | None = None, retest_s: int | None = None) -> list[dict[str, Any]]:
    """The four stages on runs of aggressive orders. The catalyst is the run as
    it stands when price releases (orders that join later are the squeeze
    itself: "more aggression joins them at worse prices"); its line is the
    lowest buy print (highest sell print) and its top the other extreme."""
    release_ns = (RUN_RELEASE_S if release_s is None else release_s) * 1_000_000_000
    failure_ns = (RUN_FAILURE_S if failure_s is None else failure_s) * 1_000_000_000
    retest_ns = (RUN_RETEST_S if retest_s is None else retest_s) * 1_000_000_000
    bars = [b for b in bars if b.get("complete", True)]
    starts = [int(b["start"]) for b in bars]
    out = []
    for run in runs:
        orders = run["orders"]
        up = int(run["sign"]) > 0
        known = int(orders[1]["t"])  # a run exists from its second order
        if known >= session_end or known < session_open:
            continue
        i = bisect_left(starts, known)
        release_i = None
        members = 2
        for k in range(i, len(bars)):
            bar = bars[k]
            while members < len(orders) and orders[members]["t"] <= int(bar["start"]):
                members += 1
            last_member_t = orders[members - 1]["t"]
            if int(bar["start"]) > last_member_t + release_ns:
                break
            part = orders[:members]
            line = min(o["low"] for o in part) if up else max(o["high"] for o in part)
            top = max(o["high"] for o in part) if up else min(o["low"] for o in part)
            reached = (bar["H"] >= top + RELEASE_POINTS) if up else (bar["L"] <= top - RELEASE_POINTS)
            if reached:
                release_i = k
                break
        if release_i is None:
            continue
        extreme = bars[release_i]["H"] if up else bars[release_i]["L"]
        extreme_at = int(bars[release_i]["start"])
        failure_i = None
        for k in range(release_i, len(bars)):
            bar = bars[k]
            if (bar["H"] > extreme) if up else (bar["L"] < extreme):
                extreme, extreme_at = (bar["H"] if up else bar["L"]), int(bar["start"])
            if int(bar["start"]) > extreme_at + failure_ns:
                break
            through = (bar["C"] <= line - FAIL_MARGIN) if up else (bar["C"] >= line + FAIL_MARGIN)
            if through:
                failure_i = k
                break
        if failure_i is None:
            continue
        failure_known = _known(bars[failure_i])
        retest_i = None
        for k in range(failure_i + 1, len(bars)):
            bar = bars[k]
            if int(bar["start"]) > failure_known + retest_ns:
                break
            reclaimed = (bar["C"] >= top + FAIL_MARGIN) if up else (bar["C"] <= top - FAIL_MARGIN)
            if reclaimed:
                break
            reached = (bar["H"] >= line - RETEST_REACH) if up else (bar["L"] <= line + RETEST_REACH)
            if reached:
                retest_i = k
                break
        if retest_i is None:
            continue
        lo, hi = (line, top) if up else (top, line)
        out.append(
            {
                "box": f"run:{orders[0]['t']}:{'B' if up else 'A'}",
                "box_lo": lo,
                "box_hi": hi,
                "line": line,
                "aggressor": BUY if up else SELL,
                "n_orders": members,
                "contracts": sum(o["lots"] for o in orders[:members]),
                "side": "short" if up else "long",
                "catalyst_at": known,
                "release_at": _known(bars[release_i]),
                "squeeze_extreme": extreme,
                "failure_at": failure_known,
                "retest_index": retest_i,
                "retest_at": _known(bars[retest_i]),
                "retest_bar": bars[retest_i],
                "bars_after_retest": bars[retest_i + 1 : retest_i + 4],
            }
        )
    out.sort(key=lambda s: s["retest_at"])
    return out


def ofm_fills(bars: list[Mapping[str, Any]], sequence: Mapping[str, Any]) -> list[dict[str, Any]]:
    """The two entries the source gives for one completed sequence, each with
    his stop. ``passive`` rests at the box's failure-side edge and is filled by
    the retest itself (p.14); ``aggressive`` rests one tick beyond the retest
    bar's wick once that bar is complete and is filled only if one of the next
    bars trades through it (p.12). ``bars`` is kept for callers of the first
    version; the sequence carries its own retest bar and the bars after it."""
    side = sequence["side"]
    lo, hi = sequence["box_lo"], sequence["box_hi"]
    retest = sequence["retest_bar"]
    fills = []
    if side == "short":
        if retest["H"] >= lo:  # a resting limit fills only if price trades at it
            fills.append({"mode": "ofm_passive", "entry": lo, "at": int(retest["end"]), "stop": hi + TICK})
        trigger, wick_stop = retest["L"] - TICK, retest["H"] + TICK
    else:
        if retest["L"] <= hi:
            fills.append({"mode": "ofm_passive", "entry": hi, "at": int(retest["end"]), "stop": lo - TICK})
        trigger, wick_stop = retest["H"] + TICK, retest["L"] - TICK
    for nxt in sequence["bars_after_retest"]:
        hit = (nxt["L"] <= trigger) if side == "short" else (nxt["H"] >= trigger)
        if hit:
            fills.append({"mode": "ofm_aggressive", "entry": trigger, "at": int(nxt["end"]), "stop": wick_stop})
            break
        undone = (nxt["C"] >= hi + FAIL_MARGIN) if side == "short" else (nxt["C"] <= lo - FAIL_MARGIN)
        if undone:
            break
    return fills


#: his stated bubble filter for the New York morning ("a minimum of 30 contracts", OFM p.4); the fast runs use it
NY_MIN_LOTS = 30
RANGE_TICKS = 40  # his chart: "the 40-range chart" (p.7)


def scan_session(market, *, min_lots: int | None = None) -> dict[str, Any]:
    """One session's OFM opportunities from the trade tape: the 40-tick range
    bars, the big aggressive orders, and two views of the catalyst -- FAST runs
    of one side's orders chained in time (the open-drive squeezes that live and
    die inside three minutes) and AREA boxes chained by price (an area that
    remembers: 2026-07-10's buyers at 29,905-29,934 from 09:49 fail at 10:19).
    A sequence found by both is reported once. Returns the sequences with
    their fills; nothing here knows a ticket."""
    from trading_research.research.method_pack import trade_tape as tt

    start, end = int(market.start), int(market.end)
    tape = tt.trades_between(market.data_root, int(market.instrument_id), start - 3600 * 1_000_000_000, end)
    if tape is None:
        return {"sequences": [], "reason": "no owned trades file covers the session", "n_bars": 0}
    t, px, size, sign = tape
    inside = t >= start
    bars = tt.range_bars(t[inside], px[inside], size[inside], sign[inside], ticks=RANGE_TICKS)
    ot, osg, lots, olo, ohi = tt.aggressive_orders(t, px, size, sign)
    floor = NY_MIN_LOTS if min_lots is None else int(min_lots)
    fast_mask = (lots >= floor) & (ot >= start)
    runs = aggression_runs(ot[fast_mask], osg[fast_mask], lots[fast_mask], olo[fast_mask], ohi[fast_mask])
    fast = ofm_sequences_from_runs(bars, runs, session_open=start, session_end=end)
    big = tt.big_order_mask(ot, lots)
    boxes = [b for b in cluster_boxes(ot[big], osg[big], lots[big], olo[big], ohi[big]) if b["known_at"] >= start]  # the dominant aggressor names the box: his absorbed-buying band of 2026-07-10 has sell prints in it too
    area = ofm_sequences(bars, boxes, session_open=start, session_end=end)
    for s in fast:
        s["catalyst_kind"] = "fast_run"
    for s in area:
        s["catalyst_kind"] = "area_box"
    seen: set[tuple] = set()
    out = []
    for s in sorted(fast + area, key=lambda s: (s["retest_at"], s["catalyst_kind"])):
        key = (s["side"], int(s["retest_bar"]["start"]))
        if key in seen:
            continue
        seen.add(key)
        s["fills"] = ofm_fills(bars, s)
        out.append(s)
    return {"sequences": out, "n_bars": len(bars), "n_runs": len(runs), "n_boxes": len(boxes)}

