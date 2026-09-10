"""QQQ GEX from Theta OI + quote mids + QQQ 1m spot. FORMULAS.md R-R01."""

from __future__ import annotations

import math
from concurrent.futures import ProcessPoolExecutor
from datetime import date, time
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from trading_research.foundations.calendar import local_timestamp
from trading_research.research.phase1_live import ZONE
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.ohlc_index import load_years, years_for_dates
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.formulas_flow import r_r01_gex_k

QQQ_OI = Path("/workspace/data/thetadata-opra/opra__qqq-options__open-interest")
QQQ_Q = Path("/workspace/data/thetadata-opra/opra__qqq-options__quote-1m__dte14__strike-range42")
QQQ_1M = Path("/workspace/data/quantpad/nasdaq__qqq-etf__ohlcv-1m")
GEX_WORKERS = 16
R = 0.045


def _ncdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _npdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _bs_price(s, k, t, sig, call: bool) -> float:
    if t <= 1e-8 or sig <= 1e-8:
        return max(s - k, 0.0) if call else max(k - s, 0.0)
    d1 = (math.log(s / k) + (R + 0.5 * sig * sig) * t) / (sig * math.sqrt(t))
    d2 = d1 - sig * math.sqrt(t)
    disc = math.exp(-R * t)
    if call:
        return s * _ncdf(d1) - k * disc * _ncdf(d2)
    return k * disc * _ncdf(-d2) - s * _ncdf(-d1)


def _bs_gamma(s, k, t, sig) -> float:
    if t <= 1e-8 or sig <= 1e-8 or s <= 0:
        return 0.0
    d1 = (math.log(s / k) + (R + 0.5 * sig * sig) * t) / (sig * math.sqrt(t))
    return _npdf(d1) / (s * sig * math.sqrt(t))


def _iv(mid, s, k, t, call: bool) -> float | None:
    if mid <= 0 or s <= 0 or k <= 0 or t <= 0:
        return None
    intrinsic = max(s - k, 0.0) if call else max(k - s, 0.0)
    if mid < intrinsic * 0.5:
        return None
    lo, hi = 1e-4, 5.0
    for _ in range(40):
        mid_sig = 0.5 * (lo + hi)
        px = _bs_price(s, k, t, mid_sig, call)
        if px > mid:
            hi = mid_sig
        else:
            lo = mid_sig
    sig = 0.5 * (lo + hi)
    if sig <= 1e-3 or sig >= 4.9:
        return None
    return sig


def _qqq_spot(bars, day: date) -> float | None:
    t0 = local_timestamp(day, time(9, 30), ZONE) // 1_000_000
    w = bars.window(t0, t0 + 60_000)
    if w["close"] is not None:
        return float(w["close"])
    w = bars.window(t0, t0 + 10 * 60_000)
    return None if w["close"] is None else float(w["close"])


def _gex_day(day: date, spot: float | None) -> dict:
    empty = {
        "date": day.isoformat(), "spot": spot, "net_gex": None, "flip": None,
        "call_wall": None, "put_wall": None, "short_gamma": False,
        "n_strikes": 0, "gex_rev": 1, "below_flip": False,
    }
    if spot is None or not np.isfinite(spot):
        return empty
    oi_path = QQQ_OI / f"{day.isoformat()}.parquet"
    q_path = QQQ_Q / f"{day.isoformat()}.parquet"
    if not oi_path.is_file() or not q_path.is_file():
        return empty
    oi_t = pq.read_table(oi_path, columns=["strike", "right", "open_interest", "expiration"])
    q_t = pq.read_table(q_path, columns=["strike", "right", "expiration", "bid", "ask", "ts_event"])
    t0 = local_timestamp(day, time(9, 30), ZONE)
    t1 = t0 + 5 * 60 * 1_000_000_000
    ts = q_t.column("ts_event").to_numpy()
    try:
        ts_ns = ts.astype("datetime64[ns]").astype(np.int64)
    except Exception:
        ts_ns = np.array([int(x) if x is not None else 0 for x in q_t.column("ts_event").to_pylist()], dtype=np.int64)
    before = (ts_ns >= t0) & (ts_ns < t1)
    strikes = q_t.column("strike").to_numpy()
    rights = q_t.column("right").to_pylist()
    exps = q_t.column("expiration").to_pylist()
    bid = q_t.column("bid").to_numpy()
    ask = q_t.column("ask").to_numpy()
    last = {}
    for i in np.flatnonzero(before):
        e = exps[i]
        dte = (e - day).days if hasattr(e, "year") else -1
        if dte < 0 or dte > 14:
            continue
        key = (float(strikes[i]), rights[i], dte)
        last[key] = (float(bid[i]), float(ask[i]), dte)
    oi_s = oi_t.column("strike").to_numpy()
    oi_r = oi_t.column("right").to_pylist()
    oi_v = oi_t.column("open_interest").to_numpy()
    oi_e = oi_t.column("expiration").to_pylist()
    gex_by_k = {}
    n = 0
    s = float(spot)
    for i in range(len(oi_v)):
        e = oi_e[i]
        dte = (e - day).days if hasattr(e, "year") else -1
        if dte < 0 or dte > 14 or int(oi_v[i]) <= 0:
            continue
        k = float(oi_s[i])
        right = oi_r[i]
        q = last.get((k, right, dte))
        if q is None:
            continue
        b, a, _ = q
        if not np.isfinite(b) or not np.isfinite(a) or a <= 0:
            continue
        mid = 0.5 * (max(b, 0.0) + a)
        texp = max(dte, 0.25) / 365.0
        call = str(right).upper().startswith("C")
        sig = _iv(mid, s, k, texp, call)
        if sig is None:
            continue
        gamma = _bs_gamma(s, k, texp, sig)
        gex = r_r01_gex_k(gamma, float(oi_v[i]), s, call=call)
        gex_by_k[k] = gex_by_k.get(k, 0.0) + gex
        n += 1
    if not gex_by_k:
        return empty
    ks = sorted(gex_by_k)
    nets = [gex_by_k[k] for k in ks]
    net = float(sum(nets))
    calls = {k: v for k, v in gex_by_k.items() if v > 0 and k > s}
    puts = {k: v for k, v in gex_by_k.items() if v < 0 and k < s}
    call_wall = max(calls, key=calls.get) if calls else None
    put_wall = min(puts, key=puts.get) if puts else None
    cum = 0.0
    flip = None
    for k, g in zip(ks, nets):
        prev = cum
        cum += g
        if prev <= 0 < cum or prev >= 0 > cum:
            flip = k
            break
    if flip is None:
        flip = ks[int(np.argmin(np.abs(np.cumsum(nets))))]
    return {
        "date": day.isoformat(), "spot": s, "net_gex": net, "flip": float(flip),
        "call_wall": None if call_wall is None else float(call_wall),
        "put_wall": None if put_wall is None else float(put_wall),
        "short_gamma": bool(net < 0),
        "below_flip": bool(s < float(flip)),
        "n_strikes": n, "gex_rev": 1,
    }


def _gex_job(item):
    day, spot = item
    return _gex_day(day, spot)


def build_gex_table() -> list[dict]:
    cached = load_rows("gex_qqq_F")
    if cached and cached[0].get("gex_rev") == 1:
        return cached
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(QQQ_1M, years_for_dates(dates))
    spots = {d.isoformat(): _qqq_spot(bars, d) for d in dates}
    print(f"gex days={len(dates)} workers={GEX_WORKERS}", flush=True)
    payload = [(d, spots.get(d.isoformat())) for d in dates]
    with ProcessPoolExecutor(max_workers=GEX_WORKERS) as pool:
        rows = list(pool.map(_gex_job, payload))
    n_ok = sum(1 for r in rows if r.get("n_strikes"))
    print(f"gex ok {n_ok}/{len(rows)}", flush=True)
    save_rows("gex_qqq_F", rows)
    return rows
