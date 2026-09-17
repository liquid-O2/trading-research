#!/usr/bin/env python3
"""Replay the dated Sires and Saint tickets on the levels the authors drew.

Every Sires ticket (Deepchart 40-range bars, NQ) and the Saint ticket (Sierra,
NQ/MNQ) is a drawn band or line plus a short sequence read on a minute clock:

* origin of the move: the squeeze pushes THROUGH the line, fails back through
  it, and the entry is the retest of the failure box (OFM pp.7-14; K18 p.6;
  K2345 p.7; CONT p.7);
* refill / defended band: sellers (buyers) are absorbed at a band that holds,
  and the entry is the close back away from the band (NYAM p.4; BIG p.16);
* failed auction / band reclaim: a band is tagged and instantly rejected, the
  entry is the reclaim of its edge (BIG p.11);
* balance fade / resistance fade: the retest of a box that already failed
  (BIG p.15; NYAM p.11);
* microbalance break: the stop entry through the short-term balance (K2345
  p.7);
* Saint continuation retest: the break of the drawn intraday level and the
  single retest (TRAP pp.6-7).

The levels come from the records (the author's own boxes and lines), as the
P-zone fixtures did for Jumbo; generating them from the trade data is the
Phase 3 level work. The score is the user's bar: the ticketed fill reproduced
within 10 points on the right bar (one five-minute bar for a ticket time), on
the author's side, by a source-supported fill of the same opportunity.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

WORKTREE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKTREE / "implementation/src"))

from trading_research.research.rule_discovery.source_adapters.common import load_source_market  # noqa: E402

ET = ZoneInfo("America/New_York")
EXAMPLES = WORKTREE / "planning/phase-1-5/AUTHOR_EXAMPLES_2026-09-17.json"
MINUTE = 60 * 1_000_000_000
FIVE = 5 * MINUTE
TOLERANCE = Decimal("10")
BARS_ALLOWED = 1.0  # tickets carry the fill minute
FAIL_MARGIN = Decimal("1")  # a 40-range bar is ten points; one point back through the line is a failure
RETEST_INSIDE = Decimal("2")  # a resting limit fills when price comes within two points
STOP_BEYOND = Decimal("0.25")  # a resting stop one tick beyond the level


def _d(value):
    if value is None:
        return None
    return Decimal(str(value))


def ns_to_et(ns: int) -> datetime:
    return datetime.fromtimestamp(int(ns) / 1e9, tz=timezone.utc).astimezone(ET)


def et_str(ns) -> str | None:
    return None if ns is None else ns_to_et(int(ns)).strftime("%H:%M")


def sign(side: str) -> int:
    return 1 if side == "long" else -1


# ---------------------------------------------------------------------------
# levels from the record: every drawn box or line, with the side it is traded from

def fixture_levels(example: dict) -> list[dict]:
    """Every drawn level of the record as (kind, low, high). A line is a
    degenerate box; a band keeps both edges. Sides are decided by the play at
    scan time (a level can be defended from below and fail from above)."""
    out = []
    for name, value in (example.get("levels") or {}).items():
        if isinstance(value, (int, float)):
            out.append({"name": name, "low": _d(value), "high": _d(value)})
            continue
        if isinstance(value, str):
            # "retest at 29654.50", "SD+1, SD+2 on the right axis": keep the prices
            for i, m in enumerate(re.finditer(r"\b(\d{4,5}(?:\.\d+)?)\b", value)):
                out.append({"name": f"{name}[{i}]", "low": _d(m.group(1)), "high": _d(m.group(1))})
            continue
        if isinstance(value, list) and value and all(isinstance(v, (int, float)) for v in value):
            if len(value) == 2:
                lo, hi = sorted(_d(v) for v in value)
                out.append({"name": name, "low": lo, "high": hi})
            else:
                for i, v in enumerate(value):
                    out.append({"name": f"{name}[{i}]", "low": _d(v), "high": _d(v)})
            continue
        if isinstance(value, list) and value and all(isinstance(v, list) for v in value):
            for i, pair in enumerate(value):
                if len(pair) == 2:
                    lo, hi = sorted(_d(v) for v in pair)
                    out.append({"name": f"{name}[{i}]", "low": lo, "high": hi})
    return out


# ---------------------------------------------------------------------------
# one-minute mechanics at a level

def bars_between(market, start: int, end: int) -> list[dict]:
    rows = []
    for row in market.bars(start, end, seconds=60):
        if row.get("O") is None or row.get("C") is None or row.get("H") is None or row.get("L") is None:
            continue
        rows.append({"start": int(row["start"]), "end": int(row.get("end") or (int(row["start"]) + MINUTE)), "O": _d(row["O"]), "H": _d(row["H"]), "L": _d(row["L"]), "C": _d(row["C"])})
    return rows


def sweep_fail_cycles(rows: list[dict], level: Decimal, side: str, *, max_cycles: int = 30, fail_window: int = 90) -> list[dict]:
    """A raid THROUGH the line from the entry side and the first one-minute close
    back through it (by FAIL_MARGIN) within ``fail_window`` bars. ``side`` is the
    trade's side: a short's raid goes above the line, a long's below."""
    cycles = []
    i = 0
    while i < len(rows) and len(cycles) < max_cycles:
        row = rows[i]
        beyond = row["H"] > level if side == "short" else row["L"] < level
        prior_ok = i == 0 or ((rows[i - 1]["C"] <= level) if side == "short" else (rows[i - 1]["C"] >= level)) or ((row["O"] <= level) if side == "short" else (row["O"] >= level))
        if not (beyond and prior_ok):
            i += 1
            continue
        extreme = row["H"] if side == "short" else row["L"]
        fail = None
        j = i
        while j < min(len(rows), i + fail_window):
            bar = rows[j]
            extreme = max(extreme, bar["H"]) if side == "short" else min(extreme, bar["L"])
            through = (bar["C"] <= level - FAIL_MARGIN) if side == "short" else (bar["C"] >= level + FAIL_MARGIN)
            if through:
                fail = bar
                break
            j += 1
        cycles.append({"cycle": len(cycles), "sweep": row, "extreme": extreme, "fail": fail, "fail_index": j if fail else None, "sweep_index": i})
        i = (j + 1) if fail else (i + 1)
    return cycles


def fills_after_failure(rows: list[dict], cycle: dict, level: Decimal, side: str, *, box_low: Decimal | None, box_high: Decimal | None, horizon: int = 30) -> list[dict]:
    """The source-supported fills of one failed cycle."""
    fail = cycle["fail"]
    if fail is None:
        return []
    out = []
    k = cycle["fail_index"]
    out.append({"mode": "failure_close_1m", "entry": fail["C"], "at": fail["end"]})
    # the resting stop AT the line, triggered as price comes back through it
    # (2026-07-10 10:24: SQ C 29,908.64, filled 29,909.75, stop seven ticks above)
    out.append({"mode": "stop_at_line", "entry": level, "at": fail["end"]})
    if k + 1 < len(rows):
        out.append({"mode": "next_bar_open", "entry": rows[k + 1]["O"], "at": rows[k + 1]["start"] + MINUTE})
    # the resting limit at the line, and at the failure box's near edge, filled
    # on the retest ("short on the retest of the failed squeeze", OFM p.7)
    near_edge = None
    if box_low is not None and box_high is not None and box_low < box_high:
        near_edge = box_low if side == "short" else box_high  # the edge the retest reaches first
    for label, px in (("retest_limit_line", level), ("retest_limit_box_edge", near_edge)):
        if px is None:
            continue
        for bar in rows[k + 1 : k + 1 + horizon]:
            reached = (bar["H"] >= px - RETEST_INSIDE) if side == "short" else (bar["L"] <= px + RETEST_INSIDE)
            if reached:
                out.append({"mode": label, "entry": px, "at": bar["end"]})
                break
            gone = (bar["C"] > level + FAIL_MARGIN * 4) if side == "short" else (bar["C"] < level - FAIL_MARGIN * 4)
            if gone:
                break
    # the resting stop beyond the retest bar: "stop entry below the buyers"
    # (OFM p.14) -- after the failure, the first retest bar's extreme, one
    # tick beyond, triggered by the next bar
    for idx in range(k + 1, min(len(rows) - 1, k + 1 + horizon)):
        bar, nxt = rows[idx], rows[idx + 1]
        touched = (bar["H"] >= level - RETEST_INSIDE * 3) if side == "short" else (bar["L"] <= level + RETEST_INSIDE * 3)
        if not touched:
            continue
        trigger = (bar["L"] - STOP_BEYOND) if side == "short" else (bar["H"] + STOP_BEYOND)
        hit = (nxt["L"] <= trigger) if side == "short" else (nxt["H"] >= trigger)
        if hit:
            out.append({"mode": "stop_beyond_retest_bar", "entry": trigger, "at": nxt["end"]})
        break
    return out


def defended_band_fills(rows: list[dict], low: Decimal, high: Decimal, side: str, *, horizon: int = 90) -> list[dict]:
    """A band touched from the entry side and held: the first one-minute close
    back away from it is the fill ("sellers absorbed at the bottom, no result
    for the push", NYAM p.4). Long: the bar dips into or onto the band and
    closes above its top; short: the mirror."""
    out = []
    seen = 0
    away = True  # a new touch needs price to have left the band first
    depart = (high - low) + RETEST_INSIDE * 4
    for i, bar in enumerate(rows):
        if side == "long":
            touched = bar["L"] <= high + RETEST_INSIDE and bar["L"] >= low - RETEST_INSIDE * 2
            left = bar["C"] > high + depart
        else:
            touched = bar["H"] >= low - RETEST_INSIDE and bar["H"] <= high + RETEST_INSIDE * 2
            left = bar["C"] < low - depart
        if left:
            away = True
        if not touched or not away:
            continue
        away = False
        seen += 1
        # the fill is the close of the first bar that touches and holds, or of
        # the next bar that closes away when the touch bar itself does not
        for j in range(i, min(len(rows), i + 3)):
            b = rows[j]
            closes_away = (b["C"] > high) if side == "long" else (b["C"] < low)
            if closes_away:
                out.append({"mode": "band_defence_close", "entry": b["C"], "at": b["end"], "touch_at": bar["start"], "cycle": seen - 1})
                if j + 1 < len(rows):
                    out.append({"mode": "band_defence_next_open", "entry": rows[j + 1]["O"], "at": rows[j + 1]["start"] + MINUTE, "touch_at": bar["start"], "cycle": seen - 1})
                # the resting limit at the band's near edge
                out.append({"mode": "band_edge_limit", "entry": high if side == "long" else low, "at": bar["end"], "touch_at": bar["start"], "cycle": seen - 1})
                break
        if seen >= 40:
            break
    return out


def reclaim_fills(rows: list[dict], low: Decimal, high: Decimal, side: str, *, horizon: int = 60) -> list[dict]:
    """A band tagged THROUGH its near edge and reclaimed: the first close back
    beyond the edge after the tag (BIG p.11 'tag of an older balance's POC,
    instant rejection'). Long: price drops into the band, closes back above its
    top; the fill is that close, the next open, or a stop one tick above the
    edge."""
    out = []
    cyc = 0
    i = 0
    while i < len(rows) and cyc < 4:
        bar = rows[i]
        tagged = (bar["L"] < high) if side == "long" else (bar["H"] > low)
        from_outside = i == 0 or ((rows[i - 1]["C"] >= high) if side == "long" else (rows[i - 1]["C"] <= low))
        if not (tagged and from_outside):
            i += 1
            continue
        for j in range(i, min(len(rows), i + horizon)):
            b = rows[j]
            back = (b["C"] > high + FAIL_MARGIN) if side == "long" else (b["C"] < low - FAIL_MARGIN)
            if back:
                out.append({"mode": "reclaim_close", "entry": b["C"], "at": b["end"], "cycle": cyc})
                if j + 1 < len(rows):
                    out.append({"mode": "reclaim_next_open", "entry": rows[j + 1]["O"], "at": rows[j + 1]["start"] + MINUTE, "cycle": cyc})
                    edge = high if side == "long" else low
                    trig = edge + STOP_BEYOND if side == "long" else edge - STOP_BEYOND
                    out.append({"mode": "stop_beyond_edge", "entry": trig, "at": rows[j]["end"], "cycle": cyc})
                i = j + 1
                break
        else:
            i += 1
        cyc += 1
    return out


def break_stop_fills(rows: list[dict], level: Decimal, side: str, *, max_breaks: int = 30, retest_window: int = 90) -> list[dict]:
    """The stop entry through a level from the inside (K2345 p.7, the
    microbalance; NYAM p.9, the third retest of the support band failing), one
    tick beyond, on every break after price has re-entered; and the single
    retest of the broken level from the other side (TRAP pp.6-7: "wait for a
    breakout of the intraday range, then wait again for price to come back and
    retest it"): the retest bar's extreme, its close and the next open."""
    out = []
    n = 0
    i = 0
    while i < len(rows) and n < max_breaks:
        bar = rows[i]
        inside_before = i == 0 or ((rows[i - 1]["C"] <= level) if side == "long" else (rows[i - 1]["C"] >= level))
        through = (bar["H"] > level) if side == "long" else (bar["L"] < level)
        if not (inside_before and through):
            i += 1
            continue
        trig = level + STOP_BEYOND if side == "long" else level - STOP_BEYOND
        out.append({"mode": "break_stop", "entry": trig, "at": bar["end"], "cycle": n})
        # the retest: after the break, price first leaves the level (fifteen
        # points or more away: "wait again for price to come back", TRAP p.6),
        # then the first bar that comes back within fifteen points of it from
        # the broken side without closing back through it
        # (a retest needs a real departure -- twenty-five points, half the
        # spacing of his intraday levels -- and each new departure allows one
        # more retest; 2026-08-10 retests the broken 29,740 at 19:0x and again
        # at 19:47 after the 19:23 low, and the second is the ticket)
        departed = False
        retests = 0
        for j in range(i + 1, min(len(rows), i + 1 + retest_window)):
            b = rows[j]
            back_through = (b["C"] < level - FAIL_MARGIN) if side == "long" else (b["C"] > level + FAIL_MARGIN)
            if back_through:
                break
            away = (b["H"] >= level + RETEST_INSIDE * 12) if side == "long" else (b["L"] <= level - RETEST_INSIDE * 12)
            if away:
                departed = True
            near = departed and ((b["L"] <= level + RETEST_INSIDE * 7) if side == "long" else (b["H"] >= level - RETEST_INSIDE * 7))
            if near:
                extreme = b["L"] if side == "long" else b["H"]
                out.append({"mode": "break_retest_extreme", "entry": extreme, "at": b["end"], "cycle": n, "retest": retests})
                out.append({"mode": "break_retest_close", "entry": b["C"], "at": b["end"], "cycle": n, "retest": retests})
                if j + 1 < len(rows):
                    out.append({"mode": "break_retest_next_open", "entry": rows[j + 1]["O"], "at": rows[j + 1]["start"] + MINUTE, "cycle": n, "retest": retests})
                retests += 1
                departed = False
                if retests >= 3:
                    break
        n += 1
        # the next break needs a re-entry: a close back on the inside
        i += 1
        while i < len(rows) and not ((rows[i]["C"] <= level) if side == "long" else (rows[i]["C"] >= level)):
            i += 1
    return out


# ---------------------------------------------------------------------------
# the replay

def entry_windows(example: dict):
    for a in example.get("actions") or []:
        if not a.get("proper_entry"):
            continue
        yield a


def session_day(example: dict, action: dict) -> str:
    day = example["date"]
    hh = int(str(action["time_et"])[:2])
    if hh >= 18:
        d = date.fromisoformat(day) + timedelta(days=1)
        while d.weekday() >= 5:
            d += timedelta(days=1)
        return d.isoformat()
    return day


def parse_window(market, action: dict) -> tuple[int, int]:
    text = str(action["time_et"])
    first, _, last = text.partition("-")
    off = -1 if int(first[:2]) >= 18 else 0
    a = int(market.at(first.strip()[:5], off))
    b = int(market.at(last.strip()[:5], off)) if last.strip()[:5].replace(":", "").isdigit() else a
    return a, b


def bars_from_window(at_ns: int, window: tuple[int, int]) -> float:
    if window[0] <= at_ns <= window[1] + MINUTE:
        return 0.0
    gap = window[0] - at_ns if at_ns < window[0] else at_ns - window[1] - MINUTE
    return round(gap / FIVE, 1)


def generated_levels(example: dict, action: dict, window: tuple[int, int], params: dict) -> list[dict]:
    """The aggression boxes generated from order-level prints before the ticket
    (tools/sires_levels_fit.py), as the level set: each box known before the
    ticket window opens is a level."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("sires_levels_fit", str(Path(__file__).resolve().parent / "sires_levels_fit.py"))
    fit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fit)
    day = session_day(example, action)
    # the boxes he carries into a session include earlier days' aggression
    # bands ("prior_day_aggression_band", BIG p.11; on 2026-08-06 the band is
    # the morning of 2026-08-04, two sessions back): generate from
    # ``lookback_days`` calendar days before the session's cash open and, with
    # ``drop_consumed``, keep only boxes price has not traded through (both
    # edges by CONSUMED_POINTS) since they formed -- a memory rule, not a clock
    start = fit.ns_at(day, "09:30", -int(params.get("lookback_days") or 1))
    key = (day, start)
    cached = _ORDER_CACHE.get(key)
    if cached is None:
        import pandas as pd
        frames = []
        from datetime import date as _date, timedelta as _td
        d0 = _date.fromisoformat(day) - _td(days=int(params.get("lookback_days") or 1))
        d1 = _date.fromisoformat(day)
        seen = set()
        d = d0
        while d <= d1:
            wf = fit.week_file(d.isoformat())
            if wf not in seen:
                seen.add(wf)
                o = fit.orders_between(d.isoformat(), start, fit.ns_at(day, "16:00"))
                if o is not None and not o.empty:
                    frames.append(o)
            d += _td(days=1)
        cached = pd.concat(frames).drop_duplicates(subset=["t", "side"]).sort_values("t").reset_index(drop=True) if frames else None
        _ORDER_CACHE.clear()
        _ORDER_CACHE[key] = cached
    if cached is None or cached.empty:
        return []
    orders = cached[cached["t"] < window[1] + 60 * fit.NS]
    adaptive = {"quantile": params["quantile"], "lookback_s": params["lookback"], "floor": params["floor"]} if params.get("adaptive") else None
    boxes = fit.cluster_orders(orders, min_size=params["min_size"], band=params["band"], window_s=params["window"], min_orders=params["min_orders"], adaptive=adaptive)
    if params.get("absorbed"):
        boxes = fit.absorbed(orders, boxes, follow_s=params["follow"], give=params["give"], give_in_ranges=bool(params.get("adaptive")))
    out = []
    lo_px = orders["lo"].to_numpy(); hi_px = orders["hi"].to_numpy(); t_ns = orders["t"].to_numpy()
    for i, b in enumerate(boxes):
        if int(b["known_at"]) >= window[0]:
            continue  # not drawn yet when he traded
        if params.get("drop_consumed"):
            after = (t_ns > int(b["known_at"])) & (t_ns < window[0])
            if (hi_px[after] >= b["hi"] + CONSUMED_POINTS).any() and (lo_px[after] <= b["lo"] - CONSUMED_POINTS).any():
                continue  # traded through both edges since: no longer drawn
        out.append({"name": f"gen[{i}] {b['first']}-{b['last']} {b['sides']}{b['largest']}", "low": _d(b["lo"]), "high": _d(b["hi"])})
    return out


LEVEL_SOURCE = {"mode": "drawn", "params": {}}
_ORDER_CACHE: dict = {}
CONSUMED_POINTS = 5.0  # a box price has traded through on both sides by this much is no longer drawn


def candidates_for(example: dict, market, rows: list[dict], action: dict, window: tuple[int, int] | None = None) -> list[dict]:
    """Every fill the mechanics admit at every level, on the ticket's side. The
    level set is the author's drawn boxes (``drawn``) or the boxes generated
    from order-level prints before the ticket (``generated``)."""
    side = action["side"]
    branch = action.get("branch")
    out = []
    levels = fixture_levels(example) if LEVEL_SOURCE["mode"] == "drawn" else (generated_levels(example, action, window, LEVEL_SOURCE["params"]) if window else [])
    for lvl in levels:
        lo, hi = lvl["low"], lvl["high"]
        is_box = hi > lo
        # OFM / band failure / balance fade / resistance fade: the raid through
        # the level from the entry side, the failure back, the retest
        for line_label, line in ((("line" if not is_box else "box_far_edge"), (hi if side == "short" else lo)),):
            for cycle in sweep_fail_cycles(rows, line, side):
                for fill in fills_after_failure(rows, cycle, line, side, box_low=lo if is_box else None, box_high=hi if is_box else None):
                    out.append({**fill, "level": lvl["name"], "level_px": line, "play": "failure", "cycle": cycle["cycle"]})
        if is_box:
            for fill in defended_band_fills(rows, lo, hi, side):
                out.append({**fill, "level": lvl["name"], "level_px": (hi if side == "long" else lo), "play": "defence"})
            for fill in reclaim_fills(rows, lo, hi, side):
                out.append({**fill, "level": lvl["name"], "level_px": (hi if side == "long" else lo), "play": "reclaim"})
            for fill in break_stop_fills(rows, hi if side == "long" else lo, side):
                out.append({**fill, "level": lvl["name"], "level_px": (hi if side == "long" else lo), "play": "break"})
        else:
            for fill in break_stop_fills(rows, lo, side):
                out.append({**fill, "level": lvl["name"], "level_px": lo, "play": "break"})
            for fill in defended_band_fills(rows, lo - RETEST_INSIDE, lo + RETEST_INSIDE, side):
                out.append({**fill, "level": lvl["name"], "level_px": lo, "play": "defence"})
    return out


def replay(example: dict, markets: dict) -> list[dict]:
    rows_out = []
    for action in entry_windows(example):
        day = session_day(example, action)
        if day not in markets:
            markets[day] = load_source_market(day)
        market = markets[day]
        window = parse_window(market, action)
        start = int(market.start)
        end = min(int(market.end), window[1] + 60 * MINUTE)
        rows = bars_between(market, start, end)
        cands = candidates_for(example, market, rows, action, window)
        price = _d(action.get("price"))
        scored = []
        for c in cands:
            bars = bars_from_window(int(c["at"]), window)
            delta = None if price is None else abs(c["entry"] - price)
            scored.append({**c, "bars": bars, "delta": delta, "strict_10": bars <= BARS_ALLOWED and (delta is None or delta <= TOLERANCE)})
        hits = [c for c in scored if c["strict_10"]]
        in_time = [c for c in scored if c["bars"] <= BARS_ALLOWED]
        best = min(hits, key=lambda c: (c["delta"] or 0, c["bars"])) if hits else (min(in_time, key=lambda c: (c["delta"] or 0)) if in_time else (min(scored, key=lambda c: (c["bars"], c["delta"] or 0)) if scored else None))
        rows_out.append(
            {
                "example_id": example["id"],
                "session": day,
                "time_et": action["time_et"],
                "side": action["side"],
                "branch": action.get("branch"),
                "price": None if price is None else float(price),
                "strict_10": bool(hits),
                "n_candidates_side": len(scored),
                "n_in_window": len(in_time),
                "best": None if best is None else {"mode": best["mode"], "play": best["play"], "level": best["level"], "level_px": float(best["level_px"]), "entry": float(best["entry"]), "at": et_str(best["at"]), "delta": None if best["delta"] is None else float(best["delta"]), "bars": best["bars"]},
                "in_window": [{"mode": c["mode"], "play": c["play"], "level": c["level"], "entry": float(c["entry"]), "at": et_str(c["at"]), "delta": None if c["delta"] is None else float(c["delta"])} for c in sorted(in_time, key=lambda c: (c["delta"] or 0))[:8]],
            }
        )
    return rows_out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--only", default=None)
    parser.add_argument("--levels", choices=("drawn", "generated"), default="drawn")
    parser.add_argument("--min-size", type=int, default=30)
    parser.add_argument("--band", type=float, default=6.0)
    parser.add_argument("--window", type=int, default=180)
    parser.add_argument("--min-orders", type=int, default=2)
    parser.add_argument("--absorbed", action="store_true")
    parser.add_argument("--follow", type=int, default=120)
    parser.add_argument("--give", type=float, default=1.5)
    parser.add_argument("--adaptive", action="store_true")
    parser.add_argument("--quantile", type=float, default=0.995)
    parser.add_argument("--lookback", type=int, default=3600)
    parser.add_argument("--floor", type=int, default=20)
    parser.add_argument("--lookback-days", type=int, default=1, help="calendar days before the session's open the boxes are generated from")
    parser.add_argument("--drop-consumed", action="store_true", help="drop boxes price has traded through on both sides since they formed")
    args = parser.parse_args(argv)
    LEVEL_SOURCE["mode"] = args.levels
    LEVEL_SOURCE["params"] = {k: getattr(args, k) for k in ("min_size", "band", "window", "min_orders", "absorbed", "follow", "give", "adaptive", "quantile", "lookback", "floor", "lookback_days", "drop_consumed")}
    examples = json.loads(EXAMPLES.read_text())["examples"]
    wanted = set(args.only.split(",")) if args.only else None
    markets: dict = {}
    table = []
    for ex in examples:
        if not ex.get("inside_tape") or not ex["id"].startswith(("SI", "SA")):
            continue
        if wanted and ex["id"] not in wanted:
            continue
        if not any(a.get("proper_entry") for a in ex.get("actions") or []):
            continue
        for row in replay(ex, markets):
            table.append(row)
            b = row["best"] or {}
            print(json.dumps({"id": row["example_id"], "time": row["time_et"], "side": row["side"], "price": row["price"], "strict_10": row["strict_10"], "best": f'{b.get("play")}/{b.get("mode")}@{b.get("entry")} on {b.get("level")} d={b.get("delta")} b={b.get("bars")} at {b.get("at")}', "n_side": row["n_candidates_side"], "n_window": row["n_in_window"]}), flush=True)
    args.out.mkdir(parents=True, exist_ok=True)
    summary = {"n_entries": len(table), "n_strict_10": sum(1 for r in table if r["strict_10"]), "levels": LEVEL_SOURCE, "rows": table}
    (args.out / "REPLAY_SIRES.json").write_text(json.dumps(summary, indent=1, default=str) + "\n")
    lines = [f"# Sires and Saint ticket replay on the {LEVEL_SOURCE['mode']} levels", "", f"{summary['n_strict_10']} of {summary['n_entries']} ticketed fills reproduced within 10 points on the right bar (one five-minute bar) by a source-supported fill at one of the author's drawn levels, on his side.", "", "| ticket | side | printed | our fill | mode / play | level | d | bars | ok |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in table:
        b = r["best"] or {}
        lines.append(f"| `{r['example_id']}` {r['time_et']} | {r['side']} | {r['price']} | {b.get('entry')} at {b.get('at')} | {b.get('mode')} / {b.get('play')} | {b.get('level')} {b.get('level_px')} | {b.get('delta')} | {b.get('bars')} | {'yes' if r['strict_10'] else 'no'} |")
    (args.out / "REPLAY_SIRES.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({"event": "replay_complete", "n": summary["n_entries"], "strict_10": summary["n_strict_10"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
