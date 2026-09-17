#!/usr/bin/env python3
"""The shared object layer as grading features (Phase 2 on Phase 3 objects).

Every family's opportunities are graded on the same observations, computed at
the decision from what the framework already holds, nothing after it:

* profile: the prior session's value area and point of control, the
  developing session profile at the decision, and the volume nodes of both
  (local maxima and minima of volume at price after light smoothing); the
  distance from the level to the nearest node and to the value edges, and
  where the level sits inside the value area;
* delta: the footprint delta of the five minutes before the decision and of
  the thirty minutes before, and the trigger bar's own delta;
* aggression: the order-level boxes alive at the decision (the box table of
  sires_box_table.py) within five points of the level, their contracts, and
  whether any of them was carried in from an earlier session (memory);
* memory: how many one-minute bars touched the level earlier in the session;
* location: the level against the RTH open and the session's range so far,
  and the room in the trade's direction to the next major level (the prior
  day's and week's extremes, the session's extremes, the Asia and London
  extremes).

Owner: Phase 1.5 rebuilt plan. Used by build_grading_dataset_v2.py; the same
functions are the confluence operands the cross-strategy candidates use.
"""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import numpy as np

NS = 1_000_000_000
MINUTE = 60 * NS
NEAR = Decimal("5")
BOX_TABLE = Path("/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/box-table/boxes.parquet")
_BOXES = None


def _d(v):
    return None if v is None else Decimal(str(v))


def _f(v):
    try:
        return None if v is None else float(v)
    except Exception:
        return None


# --------------------------------------------------------------------------- profiles


def profile_nodes(payload: dict, *, smooth: int = 2, prominence: float = 0.20) -> tuple[list[Decimal], list[Decimal]]:
    """High- and low-volume nodes of a profile payload: local maxima and minima
    of the smoothed volume at price whose prominence against the neighbouring
    trough or peak is at least ``prominence`` of the profile's maximum (the
    P-zone fit's node recipe)."""
    rows = payload.get("rows") or []
    if len(rows) < 5:
        return [], []
    prices = [Decimal(str(r.get("price"))) for r in rows]
    vol = np.array([float(r.get("total_volume") or 0) for r in rows], dtype=float)
    if smooth > 0:
        kernel = np.ones(2 * smooth + 1) / (2 * smooth + 1)
        vol = np.convolve(vol, kernel, mode="same")
    peak = float(vol.max()) if vol.size else 0.0
    if peak <= 0:
        return [], []
    hvn, lvn = [], []
    for i in range(1, len(vol) - 1):
        if vol[i] >= vol[i - 1] and vol[i] > vol[i + 1]:
            trough = min(vol[max(0, i - 8):i].min(), vol[i + 1:i + 9].min()) if i + 1 < len(vol) else vol[i]
            if (vol[i] - trough) / peak >= prominence:
                hvn.append(prices[i])
        if vol[i] <= vol[i - 1] and vol[i] < vol[i + 1]:
            crest = max(vol[max(0, i - 8):i].max(), vol[i + 1:i + 9].max()) if i + 1 < len(vol) else vol[i]
            if (crest - vol[i]) / peak >= prominence:
                lvn.append(prices[i])
    return hvn, lvn


def nearest_distance(level: Decimal, prices: list[Decimal]) -> float | None:
    if level is None or not prices:
        return None
    return float(min(abs(p - level) for p in prices))


def prior_day_profile(market) -> dict | None:
    """The prior session's RTH profile (09:30-16:00, value area .70), from the
    prior session's own window (the pattern keani._prior_profile uses)."""
    try:
        prior = market.prior("day")
        sessions = prior.get("sessions") if isinstance(prior, dict) else None
        if not sessions:
            return None
        from datetime import date as _date

        from trading_research.research.method_pack.empirical_market import clock

        last = sessions[-1]
        win = last["window"]
        day = last.get("day")
        day = _date.fromisoformat(str(day)) if not isinstance(day, _date) else day
        payload = win.profile(int(clock(day, "09:30")), int(clock(day, "16:00")))
        return payload if payload and payload.get("poc") is not None else None
    except Exception:
        return None


def developing_profile(market, start_ns: int, at_ns: int) -> dict | None:
    if at_ns - start_ns < 5 * MINUTE:
        return None
    try:
        return market.profile(int(start_ns), int(at_ns))
    except Exception:
        return None


def profile_features(level: Decimal, prior: dict | None, developing: dict | None) -> dict:
    out = {}
    for name, prof in (("prior_day", prior), ("developing", developing)):
        if not prof:
            out.update({f"{name}_poc_distance": None, f"{name}_vah_distance": None, f"{name}_val_distance": None, f"{name}_inside_value": None, f"{name}_hvn_distance": None, f"{name}_lvn_distance": None})
            continue
        poc, vah, val = _d(prof.get("poc")), _d(prof.get("vah")), _d(prof.get("val"))
        hvn, lvn = profile_nodes(prof)
        out[f"{name}_poc_distance"] = None if poc is None or level is None else float(level - poc)
        out[f"{name}_vah_distance"] = None if vah is None or level is None else float(level - vah)
        out[f"{name}_val_distance"] = None if val is None or level is None else float(level - val)
        out[f"{name}_inside_value"] = None if (vah is None or val is None or level is None) else bool(val <= level <= vah)
        out[f"{name}_hvn_distance"] = nearest_distance(level, hvn)
        out[f"{name}_lvn_distance"] = nearest_distance(level, lvn)
    return out


# --------------------------------------------------------------------------- delta


def delta_between(market, start_ns: int, end_ns: int) -> float | None:
    rows = [r for at, r in market.window.footprints.items() if at >= start_ns and r["end"] <= end_ns and r["known_at"] <= end_ns]
    if not rows:
        return None
    return float(sum(b - a for r in rows for _px, b, a, _u in r["rows"]))


def delta_features(market, at_ns: int, trigger_start_ns: int | None) -> dict:
    return {
        "delta_5m": delta_between(market, at_ns - 5 * MINUTE, at_ns),
        "delta_30m": delta_between(market, at_ns - 30 * MINUTE, at_ns),
        "delta_trigger_bar": None if trigger_start_ns is None else delta_between(market, trigger_start_ns, trigger_start_ns + MINUTE * 5),
    }


# --------------------------------------------------------------------------- aggression boxes (the box table)


def boxes_table():
    global _BOXES
    if _BOXES is None:
        import pandas as pd

        _BOXES = pd.read_parquet(BOX_TABLE) if BOX_TABLE.exists() else None
    return _BOXES


def aggression_features(level: Decimal, at_ns: int, session_open_ns: int, lookback_days: int = 14) -> dict:
    table = boxes_table()
    if table is None or level is None:
        return {"aggression_boxes_near": None, "aggression_contracts_near": None, "aggression_carried_in": None, "aggression_nearest_distance": None}
    lo_t = at_ns - lookback_days * 86400 * NS
    sub = table[(table["known_at"] >= lo_t) & (table["known_at"] < at_ns)]
    consumed = sub["consumed_at"].to_numpy()
    alive = (np.isnan(consumed)) | (consumed > at_ns)
    sub = sub[alive]
    lv = float(level)
    near = sub[(sub["lo"] <= lv + float(NEAR)) & (sub["hi"] >= lv - float(NEAR))]
    dist = None
    if len(sub):
        d = np.minimum(np.abs(sub["lo"].to_numpy() - lv), np.abs(sub["hi"].to_numpy() - lv))
        inside = (sub["lo"].to_numpy() <= lv) & (sub["hi"].to_numpy() >= lv)
        d = np.where(inside, 0.0, d)
        dist = float(d.min())
    return {
        "aggression_boxes_near": int(len(near)),
        "aggression_contracts_near": int(near["contracts"].sum()) if len(near) else 0,
        "aggression_carried_in": bool((near["known_at"] < session_open_ns).any()) if len(near) else False,
        "aggression_nearest_distance": dist,
    }


# --------------------------------------------------------------------------- memory and location


def bars_before(market, start_ns: int, at_ns: int) -> list[dict]:
    out = []
    for row in market.bars(int(start_ns), int(at_ns), 60) or []:
        if row.get("H") is None or row.get("L") is None:
            continue
        if int(row.get("end") or 0) > at_ns:
            continue
        out.append(row)
    return out


def memory_location_features(market, level: Decimal, side: str, at_ns: int, session_open_ns: int, majors: list[tuple[str, Decimal]]) -> dict:
    rows = bars_before(market, session_open_ns, at_ns)
    touches = sum(1 for r in rows if Decimal(str(r["L"])) <= level <= Decimal(str(r["H"]))) if level is not None else None
    rth_open_ns = int(market.at("09:30"))
    rth = [r for r in rows if int(r["start"]) >= rth_open_ns]
    rth_open = Decimal(str(rth[0]["O"])) if rth and rth[0].get("O") is not None else None
    highs = [Decimal(str(r["H"])) for r in rows]
    lows = [Decimal(str(r["L"])) for r in rows]
    span = (max(highs) - min(lows)) if highs and lows else None
    room = None
    if level is not None and majors:
        beyond = [px for _k, px in majors if (px > level if side == "long" else px < level)]
        if beyond:
            nearest = min(beyond) if side == "long" else max(beyond)
            room = float(abs(nearest - level))
    return {
        "prior_touches_session": touches,
        "level_vs_rth_open": None if rth_open is None or level is None else float(level - rth_open),
        "range_position": None if not span or level is None else float((level - min(lows)) / span),
        "session_range_so_far": None if span is None else float(span),
        "room_to_next_major": room,
    }


# --------------------------------------------------------------------------- the authors' own profile and delta objects
#
# Jumbo: "Just RTH session VP and delta profile" (JR 2077828415923581206);
# P-zones are kept where they sit on an HVN or on the shelf next to an LVN
# (FIND p.8); the levels drawn every day include the prior RTH value and the
# overnight profile's shelves, ledges and nodes (FIDELITY_AUDIT S1 ledger).
# Sires: the delta print is the highest point of the delta profile, the side
# that produced it was rewarded (DELTA p.7); a large delta print at an LVN or
# minor node of the dealing range's VP gives repeatable wick reactions (p.9).
# Saint: VAH / POC / VAL at 68%, the double distribution's two shelves (VP
# pp.4-8).


def delta_profile(market, start_ns: int, end_ns: int) -> dict[Decimal, float]:
    """Delta per price over [start, end): the footprint's ask minus bid volume
    at each price, summed over the window's minutes known by ``end``."""
    out: dict[Decimal, float] = {}
    for at, r in market.window.footprints.items():
        if at < start_ns or r["end"] > end_ns or r["known_at"] > end_ns:
            continue
        for px, b, a, _u in r["rows"]:
            key = Decimal(str(px))
            out[key] = out.get(key, 0.0) + float(a) - float(b)
    return out


def delta_print(profile: dict[Decimal, float]) -> tuple[Decimal | None, float | None]:
    """The highest point of the delta profile: the price with the largest
    absolute delta and that delta (positive = buyers produced it)."""
    if not profile:
        return None, None
    px = max(profile, key=lambda p: abs(profile[p]))
    return px, profile[px]


def delta_at(profile: dict[Decimal, float], level: Decimal, band: Decimal = Decimal("2")) -> float | None:
    if not profile or level is None:
        return None
    inside = [v for p, v in profile.items() if abs(p - level) <= band]
    return float(sum(inside)) if inside else 0.0


def ledges(payload: dict, *, smooth: int = 2, prominence: float = 0.20, drop: float = 0.5) -> list[Decimal]:
    """Shelf edges: from each low-volume node walk toward the neighbouring
    high-volume shelf on each side; the ledge is the first price where the
    smoothed volume reaches ``drop`` of that shelf's peak."""
    rows = payload.get("rows") or []
    if len(rows) < 5:
        return []
    prices = [Decimal(str(r.get("price"))) for r in rows]
    vol = np.array([float(r.get("total_volume") or 0) for r in rows], dtype=float)
    if smooth > 0:
        kernel = np.ones(2 * smooth + 1) / (2 * smooth + 1)
        vol = np.convolve(vol, kernel, mode="same")
    hvn, lvn = profile_nodes(payload, smooth=smooth, prominence=prominence)
    index = {p: i for i, p in enumerate(prices)}
    out: list[Decimal] = []
    for low in lvn:
        i = index.get(low)
        if i is None:
            continue
        for direction in (-1, 1):
            j = i
            peak = None
            # the nearest HVN on this side
            for h in sorted(hvn, key=lambda p: abs(p - low)):
                if (h < low and direction < 0) or (h > low and direction > 0):
                    peak = index.get(h)
                    break
            if peak is None:
                continue
            step = 1 if peak > j else -1
            k = j
            while k != peak:
                k += step
                if vol[k] >= drop * vol[peak]:
                    out.append(prices[k])
                    break
    return sorted(set(out))


def author_profile_features(market, level: Decimal, side: str, at_ns: int, prior: dict | None) -> dict:
    """Jumbo's and Sires' objects at the decision: the RTH session profile
    (from 09:30) and its delta profile, the overnight profile (18:00-09:30),
    the prior RTH profile's ledges, and the delta print of each window."""
    out: dict = {}
    rth_open = int(market.at("09:30"))
    session_open = int(market.start)
    windows = {"rth": (rth_open, at_ns) if at_ns - rth_open >= 5 * MINUTE else None, "overnight": (session_open, min(at_ns, rth_open)) if min(at_ns, rth_open) - session_open >= 30 * MINUTE else None}
    for name, span in windows.items():
        if span is None:
            out.update({f"{name}_poc_distance": None, f"{name}_hvn_distance": None, f"{name}_lvn_distance": None, f"{name}_ledge_distance": None, f"{name}_delta_print_distance": None, f"{name}_delta_print_with_side": None, f"{name}_delta_at_level": None})
            continue
        try:
            payload = market.profile(int(span[0]), int(span[1]))
        except Exception:
            payload = None
        if payload and payload.get("poc") is not None:
            hvn, lvn = profile_nodes(payload)
            out[f"{name}_poc_distance"] = float(level - _d(payload["poc"]))
            out[f"{name}_hvn_distance"] = nearest_distance(level, hvn)
            out[f"{name}_lvn_distance"] = nearest_distance(level, lvn)
            out[f"{name}_ledge_distance"] = nearest_distance(level, ledges(payload))
        else:
            out.update({f"{name}_poc_distance": None, f"{name}_hvn_distance": None, f"{name}_lvn_distance": None, f"{name}_ledge_distance": None})
        dp = delta_profile(market, int(span[0]), int(span[1]))
        px, value = delta_print(dp)
        out[f"{name}_delta_print_distance"] = None if px is None else float(abs(px - level))
        out[f"{name}_delta_print_with_side"] = None if value is None else bool((value > 0) == (side == "long"))
        out[f"{name}_delta_at_level"] = delta_at(dp, level)
    out["prior_day_ledge_distance"] = nearest_distance(level, ledges(prior)) if prior else None
    return out


# --------------------------------------------------------------------------- naked POCs, the composite, the overnight inventory
#
# Sires VP2 p.6: a naked POC is a prior session's POC price has not traded
# back to, a ready-made target list; a composite profile merges several days
# and the HVNs and LVNs that survive across it are the heavyweight levels.
# AMT1 p.9: out of balance the ledges of the prior balance carry the move.
# MAMT p.14: the overnight profile (18:00-09:30) nets long or short and that
# carries into the open; the LVN between its two distributions is the level
# respected or disrespected at the open. MAMT p.16: an RTH open inside the
# previous ETH balance reaches that profile's mid 73% of the time.

_PRIOR_CACHE: dict = {}


def prior_session_profiles(market, n: int = 5) -> list[dict]:
    """The prior ``n`` sessions' RTH profiles (09:30-16:00), oldest last,
    from their own session markets; cached per session date."""
    from datetime import date as _date, timedelta as _td

    from trading_research.research.method_pack.empirical_market import clock
    from trading_research.research.rule_discovery.source_adapters.common import load_source_market, require_native_session

    out = []
    day = _date.fromisoformat(str(market.day)) if not isinstance(market.day, _date) else market.day
    probe = day
    tries = 0
    while len(out) < n and tries < 14:
        probe -= _td(days=1)
        tries += 1
        key = probe.isoformat()
        if key in _PRIOR_CACHE:
            if _PRIOR_CACHE[key] is not None:
                out.append(_PRIOR_CACHE[key])
            continue
        try:
            require_native_session(key)
            prior = load_source_market(key)
            payload = prior.profile(int(clock(probe, "09:30")), int(clock(probe, "16:00")))
            payload = dict(payload, day=key) if payload and payload.get("poc") is not None else None
        except Exception:
            payload = None
        _PRIOR_CACHE[key] = payload
        if len(_PRIOR_CACHE) > 40:
            _PRIOR_CACHE.pop(next(iter(_PRIOR_CACHE)))
        if payload is not None:
            out.append(payload)
    return out


def naked_pocs(profiles: list[dict], market, at_ns: int) -> list[Decimal]:
    """Prior sessions' POCs price has not traded back to before ``at_ns``:
    a POC is naked when no bar between its session's end and the decision
    spans it (the session's own bars from the account-day window)."""
    rows = bars_before(market, int(market.start), at_ns)
    out = []
    for prof in profiles:
        poc = _d(prof.get("poc"))
        if poc is None:
            continue
        touched = any(Decimal(str(r["L"])) <= poc <= Decimal(str(r["H"])) for r in rows)
        if not touched:
            out.append(poc)
    return out


def composite_payload(profiles: list[dict]) -> dict | None:
    """Several sessions' profiles merged by price (Sires' composite)."""
    if not profiles:
        return None
    merged: dict[Decimal, float] = {}
    for prof in profiles:
        for r in prof.get("rows") or []:
            px = Decimal(str(r.get("price")))
            merged[px] = merged.get(px, 0.0) + float(r.get("total_volume") or 0)
    rows = [{"price": px, "total_volume": v} for px, v in sorted(merged.items())]
    if not rows:
        return None
    return {"rows": rows, "poc": max(rows, key=lambda r: r["total_volume"])["price"]}


def context_profile_features(market, level: Decimal, side: str, at_ns: int) -> dict:
    out: dict = {}
    profiles = prior_session_profiles(market, 5)
    naked = naked_pocs(profiles, market, at_ns)
    out["naked_poc_distance"] = nearest_distance(level, naked)
    out["naked_poc_ahead"] = None
    if level is not None and naked:
        ahead = [p for p in naked if (p > level if side == "long" else p < level)]
        out["naked_poc_ahead"] = float(min(abs(p - level) for p in ahead)) if ahead else None
    comp = composite_payload(profiles)
    if comp:
        hvn, lvn = profile_nodes(comp)
        out["composite_hvn_distance"] = nearest_distance(level, hvn)
        out["composite_lvn_distance"] = nearest_distance(level, lvn)
        out["composite_ledge_distance"] = nearest_distance(level, ledges(comp))
        out["composite_poc_distance"] = None if level is None else float(level - Decimal(str(comp["poc"])))
    else:
        out.update({"composite_hvn_distance": None, "composite_lvn_distance": None, "composite_ledge_distance": None, "composite_poc_distance": None})
    # the overnight inventory: net delta 18:00-09:30 and the ETH profile's mid
    session_open = int(market.start)
    rth_open = int(market.at("09:30"))
    end = min(at_ns, rth_open)
    net = delta_between(market, session_open, end) if end - session_open >= 30 * MINUTE else None
    out["overnight_net_delta"] = net
    out["overnight_net_with_side"] = None if net is None else bool((net > 0) == (side == "long"))
    try:
        eth = market.profile(session_open, end) if end - session_open >= 30 * MINUTE else None
    except Exception:
        eth = None
    if eth and eth.get("H") is not None and eth.get("L") is not None:
        mid = (_d(eth["H"]) + _d(eth["L"])) / 2
        out["eth_mid_distance"] = None if level is None else float(level - mid)
        rth = [r for r in bars_before(market, rth_open, rth_open + 2 * MINUTE)]
        open_px = _d(rth[0]["O"]) if rth else None
        val, vah = _d(eth.get("val")), _d(eth.get("vah"))
        out["rth_open_inside_eth_value"] = None if (open_px is None or val is None or vah is None) else bool(val <= open_px <= vah)
    else:
        out["eth_mid_distance"] = None
        out["rth_open_inside_eth_value"] = None
    return out
