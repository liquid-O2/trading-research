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
        win = sessions[-1]["window"]
        payload = win.profile(win.at("09:30"), win.at("16:00"), ".70")
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
