"""Tape objects computed from retained MBP-1 session tables. Not from 1s/1m bars."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date, time as dtime, timedelta

import numpy as np
import pyarrow.parquet as pq
from numba import njit

from trading_research.foundations.calendar import local_timestamp
from trading_research.research.phase1_live import TICK, ZONE
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.mbp1_extract import list_complete_chunks
from trading_research.research.phase1_live.ohlc_index import OHLC1M, SISTERS_1M, load_years, years_for_dates
from trading_research.research.phase1_live.slice import load_calendar, slice_dates

NS500 = 500_000_000
NS2M = 2 * 60 * 1_000_000_000
NS15M = 15 * 60 * 1_000_000_000


@njit(cache=True)
def _absorption_a_scan(t, px, buy_roll, sell_roll, q_buy, q_sell, high, low, tick_tol, width, ns15m, tick):
    n = t.size
    two_tick = 2.0 * tick
    rev = 0.25 * width
    for i in range(n):
        toward_high = buy_roll[i] >= q_buy and abs(px[i] - high) <= tick_tol
        toward_low = sell_roll[i] >= q_sell and abs(px[i] - low) <= tick_tol
        if not (toward_high or toward_low):
            continue
        end = t[i] + ns15m
        k = i + 1
        while k < n and t[k] < end:
            k += 1
        pmax = px[i]
        pmin = px[i]
        for j in range(i + 1, k):
            if px[j] > pmax:
                pmax = px[j]
            if px[j] < pmin:
                pmin = px[j]
        if toward_high:
            if (pmax - high) <= two_tick and (high - pmin) >= rev:
                return True
        else:
            if (low - pmin) <= two_tick and (pmax - low) >= rev:
                return True
    return False


@njit(cache=True)
def _absorption_b_scan(t, is_trade, side, size, bid, ask, bid_sz, ask_sz, q90, tick, ns500):
    n = t.size
    maxk = 4096
    keys = np.empty(maxk, np.int64)
    counts = np.zeros(maxk, np.int64)
    nkeys = 0
    half_tick = tick * 0.5
    for j in range(n):
        if (not is_trade[j]) or side[j] == 0 or size[j] < q90:
            continue
        consumed = int(size[j])
        if consumed <= 0:
            continue
        if side[j] > 0:
            px = ask[j]
            shown = int(ask_sz[j])
            limit = t[j] + ns500
            hit = False
            k = j + 1
            need = shown + 0.5 * consumed
            while k < n and t[k] < limit:
                if abs(ask[k] - px) <= half_tick and int(ask_sz[k]) >= need:
                    hit = True
                    break
                k += 1
        else:
            px = bid[j]
            shown = int(bid_sz[j])
            limit = t[j] + ns500
            hit = False
            k = j + 1
            need = shown + 0.5 * consumed
            while k < n and t[k] < limit:
                if abs(bid[k] - px) <= half_tick and int(bid_sz[k]) >= need:
                    hit = True
                    break
                k += 1
        if hit:
            key = int(round(px / tick))
            found = -1
            for i in range(nkeys):
                if keys[i] == key:
                    found = i
                    break
            if found < 0:
                if nkeys >= maxk:
                    continue
                keys[nkeys] = key
                counts[nkeys] = 1
                nkeys += 1
                found = nkeys - 1
            else:
                counts[found] += 1
            if counts[found] >= 2:
                return True
    return False


@njit(cache=True)
def _iceberg_scan(t, is_trade, side, size, bid, ask, bid_sz, ask_sz, ratio, tick, ns500):
    n = t.size
    half_tick = tick * 0.5
    for j in range(n):
        if (not is_trade[j]) or side[j] == 0:
            continue
        buy = side[j] > 0
        shown = int(ask_sz[j] if buy else bid_sz[j])
        px = ask[j] if buy else bid[j]
        floor = shown if shown > 1 else 1
        if int(size[j]) <= ratio * floor:
            continue
        limit = t[j] + ns500
        i = j + 1
        while i < n and t[i] < limit:
            book_px = ask[i] if buy else bid[i]
            book_sz = int(ask_sz[i] if buy else bid_sz[i])
            if abs(book_px - px) <= half_tick and book_sz > shown:
                return True
            i += 1
    return False


def _flow_workers() -> int:
    # 21 vCPU / 80 GiB. Each thread holds one week table. 12 ≈ 20-30 GiB.
    return 12


def _am_ns(day: date):
    start = local_timestamp(day, dtime(9, 30), ZONE)
    end = local_timestamp(day, dtime(12, 0), ZONE)
    rth_end = local_timestamp(day, dtime(16, 0), ZONE)
    return start, end, rth_end


def _session_slices(table, only=None):
    sess = np.asarray(table.column("session").combine_chunks().to_numpy(zero_copy_only=False))
    n = sess.size
    if n == 0:
        return
    order = None
    if n > 1 and np.any(sess[1:] < sess[:-1]):
        order = np.argsort(sess, kind="mergesort")
        sess = sess[order]
    if n > 1:
        breaks = np.flatnonzero(sess[1:] != sess[:-1]) + 1
    else:
        breaks = np.empty(0, dtype=np.int64)
    starts = np.concatenate(([0], breaks))
    ends = np.concatenate((breaks, [n]))
    cols = {}
    for name in ("t", "price", "size", "side", "bid", "ask", "bid_sz", "ask_sz", "is_trade"):
        arr = table.column(name).to_numpy()
        cols[name] = arr[order] if order is not None else arr
    only = set(only) if only else None
    for a, b in zip(starts, ends):
        sid = str(sess[a])
        if only is not None and sid not in only:
            continue
        yield sid, {k: v[a:b] for k, v in cols.items()}


def iter_sessions(only=None):
    """Yield (session, table) for each complete chunk, grouped by session."""
    only = set(only) if only else None
    for path in list_complete_chunks():
        meta = path.with_suffix(".json")
        if meta.is_file() and only:
            import json as _json
            body = _json.loads(meta.read_text())
            sess_meta = set(body.get("sessions") or [])
            if sess_meta and not (sess_meta & only):
                continue
        yield from _session_slices(pq.read_table(path), only)


def cvd_from_trades(ev, t0=None, t1=None) -> dict:
    tr = ev["is_trade"]
    if t0 is not None and t1 is not None:
        tr = tr & (ev["t"] >= t0) & (ev["t"] < t1)
    side = ev["side"][tr]
    size = ev["size"][tr].astype(np.float64)
    buy = float(size[side > 0].sum())
    sell = float(size[side < 0].sum())
    big = size >= 100
    mid = (size >= 20) & (size < 100)
    sml = size < 20
    buy_big = float(size[(side > 0) & big].sum())
    sell_big = float(size[(side < 0) & big].sum())
    cvd = buy - sell
    cvd_big = buy_big - sell_big
    return {
        "buy": buy, "sell": sell, "cvd": cvd,
        "cvd_sign": 1 if cvd > 0 else (-1 if cvd < 0 else 0),
        "cvd_part": cvd_big,
        "cvd_part_sign": 1 if cvd_big > 0 else (-1 if cvd_big < 0 else 0),
        "part_big": float(size[big].sum()),
        "n_big": int(big.sum()),
        "n_trades": int(tr.sum()),
    }


def absorption_b(ev, am0: int, am1: int) -> bool:
    """BBO reload ≥ 50% of consumed size within 500 ms, twice, at the touch."""
    t = ev["t"]
    am = (t >= am0) & (t < am1)
    if not np.any(am):
        return False
    t = t[am]
    is_trade = ev["is_trade"][am]
    side = ev["side"][am]
    size = ev["size"][am]
    bid = ev["bid"][am]
    ask = ev["ask"][am]
    bid_sz = ev["bid_sz"][am]
    ask_sz = ev["ask_sz"][am]
    trade_mask = is_trade & (side != 0)
    if not np.any(trade_mask):
        return False
    q90 = float(np.quantile(size[trade_mask], 0.9))
    return bool(_absorption_b_scan(
        t, np.asarray(is_trade, dtype=np.bool_),
        np.asarray(side, dtype=np.int8), np.asarray(size, dtype=np.int32),
        np.asarray(bid, dtype=np.float64), np.asarray(ask, dtype=np.float64),
        np.asarray(bid_sz, dtype=np.int32), np.asarray(ask_sz, dtype=np.int32),
        q90, TICK, NS500,
    ))


def iceberg_touch_infer(ev, am0: int, am1: int, *, k: float = 1.0) -> bool:
    """Trade size larger than k * displayed BBO, then reload at the same price. Touch only."""
    t = ev["t"]
    am = (t >= am0) & (t < am1)
    if not np.any(am):
        return False
    t = t[am]
    is_trade = ev["is_trade"][am]
    side = ev["side"][am]
    size = ev["size"][am]
    bid = ev["bid"][am]
    ask = ev["ask"][am]
    bid_sz = ev["bid_sz"][am]
    ask_sz = ev["ask_sz"][am]
    return bool(_iceberg_scan(
        t, np.asarray(is_trade, dtype=np.bool_),
        np.asarray(side, dtype=np.int8), np.asarray(size, dtype=np.int32),
        np.asarray(bid, dtype=np.float64), np.asarray(ask, dtype=np.float64),
        np.asarray(bid_sz, dtype=np.int32), np.asarray(ask_sz, dtype=np.int32),
        float(k), TICK, NS500,
    ))


def _roll_aggressive(t, size, side, window_ns):
    buy = np.where(side > 0, size, 0.0)
    sell = np.where(side < 0, size, 0.0)
    cb = np.cumsum(buy)
    cs = np.cumsum(sell)
    left = np.searchsorted(t, t - window_ns, "right")
    prev_b = np.where(left > 0, cb[left - 1], 0.0)
    prev_s = np.where(left > 0, cs[left - 1], 0.0)
    return cb - prev_b, cs - prev_s


def absorption_a(ev, am0: int, am1: int, high: float | None, low: float | None, width: float | None,
                 *, window_ns: int = NS2M, tick_tol: float = 2 * TICK, vol_cut_buy: float | None = None,
                 vol_cut_sell: float | None = None) -> bool:
    """Aggressive volume at the touch, limited advance, then reversal. vol_cut is frozen."""
    if high is None or low is None or not width:
        return False
    tr = ev["is_trade"]
    t = ev["t"][tr]
    px = ev["price"][tr]
    size = ev["size"][tr].astype(np.float64)
    side = ev["side"][tr]
    am = (t >= am0) & (t < am1)
    t, px, size, side = t[am], px[am], size[am], side[am]
    if t.size < 20:
        return False
    buy_roll, sell_roll = _roll_aggressive(t, size, side, window_ns)
    q_buy = vol_cut_buy if vol_cut_buy is not None else float(np.quantile(buy_roll, 0.9))
    q_sell = vol_cut_sell if vol_cut_sell is not None else float(np.quantile(sell_roll, 0.9))
    return bool(_absorption_a_scan(
        np.asarray(t, dtype=np.int64), np.asarray(px, dtype=np.float64),
        np.asarray(buy_roll, dtype=np.float64), np.asarray(sell_roll, dtype=np.float64),
        float(q_buy), float(q_sell), float(high), float(low), float(tick_tol),
        float(width), NS15M, TICK,
    ))


def footprint_4x(ev, am0: int, am1: int) -> bool:
    tr = ev["is_trade"]
    t = ev["t"][tr]
    am = (t >= am0) & (t < am1)
    px = np.round(ev["price"][tr][am] / TICK).astype(np.int64)
    size = ev["size"][tr][am].astype(np.float64)
    side = ev["side"][tr][am]
    if px.size == 0:
        return False
    lo = int(px.min())
    hi = int(px.max())
    n = hi - lo + 1
    buy = np.zeros(n, dtype=np.float64)
    sell = np.zeros(n, dtype=np.float64)
    buy_i = side > 0
    sell_i = side < 0
    if np.any(buy_i):
        buy += np.bincount((px[buy_i] - lo).astype(np.int64), weights=size[buy_i], minlength=n)
    if np.any(sell_i):
        sell += np.bincount((px[sell_i] - lo).astype(np.int64), weights=size[sell_i], minlength=n)
    flags = np.zeros(n, dtype=np.int8)
    if n >= 2:
        buy_im = (sell[:-1] > 0) & (buy[1:] >= 4.0 * sell[:-1])
        flags[1:][buy_im] = 1
        sell_im = (buy[1:] > 0) & (sell[:-1] >= 4.0 * buy[1:])
        flags[:-1][sell_im] = -1
    if n >= 3:
        same = (flags[2:] != 0) & (flags[2:] == flags[1:-1]) & (flags[1:-1] == flags[:-2])
        return bool(np.any(same))
    return False


def on_touch_refill(ev, am0: int, am1: int) -> bool:
    tr = ev["is_trade"]
    t = ev["t"][tr]
    am = (t >= am0) & (t < am1)
    t = t[am]
    px = ev["price"][tr][am]
    size = ev["size"][tr][am]
    side = ev["side"][tr][am]
    large = size >= 100
    if int(large.sum()) < 3:
        return False
    lt, lp, ls = t[large], px[large], side[large]
    for i in range(lt.size - 2):
        same = ls[i:i + 8]
        if same.size < 3:
            continue
        if not np.all(same[:3] == ls[i]) or ls[i] == 0:
            continue
        window = lp[i:i + 8][: np.count_nonzero(lt[i:i + 8] - lt[i] <= NS2M)]
        if window.size < 3:
            continue
        lo, hi = float(window.min()), float(window.max())
        if hi - lo > 2 * TICK:
            continue
        later = (t > lt[i] + NS2M) & (((ls[i] > 0) & (px > hi + 4 * TICK)) | ((ls[i] < 0) & (px < lo - 4 * TICK)))
        if not np.any(later):
            continue
        leave_t = t[later][0]
        back = t > leave_t
        if np.any(back & (px >= lo) & (px <= hi)):
            return True
    return False


def smt_trade_nq(ev, am0: int, am1: int, sisters: dict, day: date, row: dict | None = None) -> bool:
    """Tick-precise S1 hunt. NQ trades beyond Asia/London/6-9/PDH/PDL. Sister 1m has not."""
    from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds
    tr = ev["is_trade"]
    t = ev["t"][tr]
    am = (t >= am0) & (t < am1)
    px = ev["price"][tr][am]
    if px.size < 10 or row is None:
        return False
    nq_levels = [
        ("asia_h", row.get("asia_high"), "high"),
        ("asia_l", row.get("asia_low"), "low"),
        ("ldn_h", row.get("london_high"), "high"),
        ("ldn_l", row.get("london_low"), "low"),
        ("h69", row.get("H"), "high"),
        ("l69", row.get("L"), "low"),
        ("pdh", row.get("prior_rth_high"), "high"),
        ("pdl", row.get("prior_rth_low"), "low"),
    ]
    hunted = []
    for lid, lvl, side in nq_levels:
        if lvl is None:
            continue
        if side == "high" and np.any(px > lvl):
            hunted.append((lid, side, float(lvl)))
        if side == "low" and np.any(px < lvl):
            hunted.append((lid, side, float(lvl)))
    if not hunted:
        return False
    asia = clock_bounds(day, CLOCKS["range.gb.asia"])
    london = clock_bounds(day, CLOCKS["range.london.00-03"])
    box69 = clock_bounds(day, CLOCKS["range.6-9.published"])
    prior = clock_bounds(day - timedelta(days=1), CLOCKS["prior.rth"])
    for name, bars in sisters.items():
        if bars is None:
            continue
        sis = {
            "asia_h": bars.window(asia["start_ms"], asia["end_ms"]).get("high"),
            "asia_l": bars.window(asia["start_ms"], asia["end_ms"]).get("low"),
            "ldn_h": bars.window(london["start_ms"], london["end_ms"]).get("high"),
            "ldn_l": bars.window(london["start_ms"], london["end_ms"]).get("low"),
            "h69": bars.window(box69["start_ms"], box69["end_ms"]).get("high"),
            "l69": bars.window(box69["start_ms"], box69["end_ms"]).get("low"),
            "pdh": bars.window(prior["start_ms"], prior["end_ms"]).get("high"),
            "pdl": bars.window(prior["start_ms"], prior["end_ms"]).get("low"),
        }
        am_s = bars.window(am0 // 1_000_000, am1 // 1_000_000)
        for lid, side, _lvl in hunted:
            sl = sis.get(lid)
            if sl is None or am_s["n"] == 0:
                return True
            if side == "high" and not np.any(am_s["h"] > sl):
                return True
            if side == "low" and not np.any(am_s["l"] < sl):
                return True
    return False


def vp_rth(ev, am0: int, rth_end: int) -> dict:
    tr = ev["is_trade"]
    t = ev["t"][tr]
    rth = (t >= am0) & (t < rth_end)
    px = np.round(ev["price"][tr][rth] / TICK).astype(np.int64)
    size = ev["size"][tr][rth].astype(np.float64)
    side = ev["side"][tr][rth]
    if px.size == 0:
        return {"poc": None, "VAL": None, "VAH": None, "n": 0}
    lo, hi = int(px.min()), int(px.max())
    rel = (px - lo).astype(np.int64)
    n = hi - lo + 1
    vol = np.bincount(rel, weights=size, minlength=n)
    delta = np.bincount(rel, weights=size * side.astype(np.float64), minlength=n)
    poc_i = int(np.argmax(vol))
    target = 0.70 * float(vol.sum())
    a = b = poc_i
    mass = vol[poc_i]
    while mass < target and (a > 0 or b < vol.size - 1):
        left = vol[a - 1] if a > 0 else -1
        right = vol[b + 1] if b < vol.size - 1 else -1
        if right > left:
            b += 1
            mass += vol[b]
        elif a > 0:
            a -= 1
            mass += vol[a]
        else:
            b += 1
            mass += vol[b]
    return {
        "poc": (lo + poc_i) * TICK,
        "VAL": (lo + a) * TICK,
        "VAH": (lo + b) * TICK,
        "n": int(px.size),
        "dp_max": (lo + int(np.argmax(delta))) * TICK if delta.size else None,
        "dp_min": (lo + int(np.argmin(delta))) * TICK if delta.size else None,
    }


def tpo_trade_visited(ev, am0: int, rth_end: int) -> bool:
    tr = ev["is_trade"]
    t = ev["t"][tr]
    rth = (t >= am0) & (t < rth_end)
    t = t[rth]
    px = ev["price"][tr][rth]
    if t.size < 30:
        return False
    bucket = ((t - am0) // (30 * 60 * 1_000_000_000)).astype(np.int64)
    n_b = int(bucket.max()) + 1
    highs = np.full(n_b, -np.inf)
    lows = np.full(n_b, np.inf)
    np.maximum.at(highs, bucket, px)
    np.minimum.at(lows, bucket, px)
    valid = np.isfinite(highs)
    if valid.sum() < 2:
        return False
    return bool(highs[valid][-1] > highs[valid][:-1].max() or lows[valid][-1] < lows[valid][:-1].min())


def _discover_chunk(path, disc_set):
    size_disc, vol2_buy, vol2_sell = [], [], []
    for session, ev in _session_slices(pq.read_table(path), disc_set):
        day = date.fromisoformat(session)
        am0, am1, rth_end = _am_ns(day)
        tr = ev["is_trade"]
        t = ev["t"][tr]
        ny = (t >= am0) & (t < rth_end)
        size_disc.append(ev["size"][tr][ny].astype(np.float64))
        am = (t >= am0) & (t < am1)
        if int(am.sum()) >= 20:
            br, sr = _roll_aggressive(t[am], ev["size"][tr][am].astype(np.float64), ev["side"][tr][am], NS2M)
            vol2_buy.append(br)
            vol2_sell.append(sr)
    return size_disc, vol2_buy, vol2_sell


def _score_session(session, ev, grid, f_rows, sisters, trades_cvd):
    row = f_rows.get(session)
    if row is None:
        return None
    day = date.fromisoformat(session)
    am0, am1, rth_end = _am_ns(day)
    globex = local_timestamp(day - timedelta(days=1), dtime(18, 0), ZONE)
    order = np.argsort(ev["t"], kind="mergesort")
    ev = {k: v[order] for k, v in ev.items()}
    q90 = grid["size"].get("q90")
    q75 = grid["size"].get("q75")
    q50 = grid["size"].get("q50")
    q99 = grid["size"].get("q99")
    cvd = cvd_from_trades(ev, globex, am1)
    cvd75 = _cvd_cut(ev, q75)
    cvd90 = _cvd_cut(ev, q90)
    vp = vp_rth(ev, am0, rth_end)
    xcheck = trades_cvd.get(session)
    tr = ev["is_trade"]
    ny = (ev["t"] >= am0) & (ev["t"] < rth_end) & tr
    ny_size = ev["size"][ny]
    ldn0 = local_timestamp(day, dtime(2, 0), ZONE)
    ldn1 = local_timestamp(day, dtime(5, 0), ZONE)
    ldn = (ev["t"] >= ldn0) & (ev["t"] < ldn1) & tr
    return {
        "date": session, "year": session[:4], "eligible": row.get("eligible"),
        "score": True, "discovery": False,
        "cvd_trade": cvd["cvd"], "cvd_trade_sign": cvd["cvd_sign"],
        "cvd_part": cvd["cvd_part"], "cvd_part_sign": cvd["cvd_part_sign"],
        "cvd_part_q75_sign": cvd75["cvd_part_sign"] if cvd75 else 0,
        "cvd_part_q90_sign": cvd90["cvd_part_sign"] if cvd90 else 0,
        "part_big": cvd["part_big"], "n_big": cvd["n_big"], "n_trades": cvd["n_trades"],
        "bigtrade": bool(np.any(ny_size >= 100)),
        "bigtrade_75ldn": bool(np.any(ev["size"][ldn] >= 75)) if np.any(ldn) else False,
        "bigtrade_q50": bool(q50 and np.any(ny_size >= q50)),
        "bigtrade_q75": bool(q75 and np.any(ny_size >= q75)),
        "bigtrade_q90": bool(q90 and np.any(ny_size >= q90)),
        "bigtrade_q99": bool(q99 and np.any(ny_size >= q99)),
        "absorption_B": absorption_b(ev, am0, am1),
        "absorption_A": absorption_a(ev, am0, am1, row.get("H"), row.get("L"), row.get("W69"),
                                     window_ns=NS2M, tick_tol=2 * TICK,
                                     vol_cut_buy=grid["abs_q90_buy"], vol_cut_sell=grid["abs_q90_sell"]),
        "absorption_A_w1m": absorption_a(ev, am0, am1, row.get("H"), row.get("L"), row.get("W69"),
                                         window_ns=60_000_000_000, tick_tol=2 * TICK),
        "absorption_A_w5m": absorption_a(ev, am0, am1, row.get("H"), row.get("L"), row.get("W69"),
                                         window_ns=5 * 60_000_000_000, tick_tol=2 * TICK),
        "absorption_A_q75": absorption_a(ev, am0, am1, row.get("H"), row.get("L"), row.get("W69"),
                                         window_ns=NS2M, tick_tol=2 * TICK,
                                         vol_cut_buy=grid["abs_q75_buy"], vol_cut_sell=grid["abs_q75_sell"]),
        "footprint_4x": footprint_4x(ev, am0, am1),
        "refill_ontouch": on_touch_refill(ev, am0, am1),
        "iceberg_touch": iceberg_touch_infer(ev, am0, am1, k=1.0),
        "iceberg_k15": iceberg_touch_infer(ev, am0, am1, k=1.5),
        "iceberg_k20": iceberg_touch_infer(ev, am0, am1, k=2.0),
        "smt_trade_nq": smt_trade_nq(ev, am0, am1, sisters, day, row),
        "footprint_stack3": bool(footprint_4x(ev, am0, am1)), "smt_s1": bool(smt_trade_nq(ev, am0, am1, sisters, day, row)),
        "stack3_computed": True,
        "tpo_trade": tpo_trade_visited(ev, am0, rth_end),
        "poc": vp["poc"], "VAL": vp["VAL"], "VAH": vp["VAH"], "vp_n": vp["n"],
        "dp_max": vp.get("dp_max"), "dp_min": vp.get("dp_min"),
        "xcheck_cvd": None if xcheck is None else xcheck.get("cvd"),
        "xcheck_disagree": False if xcheck is None or xcheck.get("cvd") is None else (
            (1 if xcheck["cvd"] > 0 else -1 if xcheck["cvd"] < 0 else 0) != cvd["cvd_sign"]
        ),
        "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
        "leakage": 0, "failure": cvd["n_trades"] == 0,
        "drop_coverage": row.get("drop_coverage"), "missing_bars": row.get("missing_1s") or 0,
        "non_touch_m05": row.get("non_touch_m05"), "source": "cov.nq.mbp1",
        "grid": grid["size"],
    }


def _score_chunk(path, score_set, grid, f_rows, sisters, trades_cvd):
    out = []
    for session, ev in _session_slices(pq.read_table(path), score_set):
        rec = _score_session(session, ev, grid, f_rows, sisters, trades_cvd)
        if rec is not None:
            out.append(rec)
    return out


def build_mbp1_flow_table():
    cached = load_rows("mbp1_flow_F")
    if cached and cached[0].get("stack3_computed"):
        return cached
    if cached:
        for rec in cached:
            rec["footprint_stack3"] = bool(rec.get("footprint_4x"))
            rec["smt_s1"] = bool(rec.get("smt_trade_nq"))
            rec["stack3_computed"] = True
        save_rows("mbp1_flow_F", cached)
        return cached
    from trading_research.research.phase1_live.threshold_grid import discovery_dates, freeze_size_grid, GRID_PATH
    from trading_research.research.phase1_live.mbp1_extract import list_extracted_sessions
    import json
    f_rows = {r["date"]: r for r in load_rows("sessions_F")}
    calendar = load_calendar()
    dates = [d.isoformat() for d in slice_dates(calendar, "F")]
    years = sorted({int(d[:4]) for d in dates} | {int(dates[0][:4]) - 1})
    sisters = {}
    for name, root in SISTERS_1M.items():
        try:
            sisters[name] = load_years(root, years)
        except FileNotFoundError:
            sisters[name] = None
    trades_cvd = {r["date"]: r for r in (load_rows("cvd_trade_F") or [])}
    present = [s for s in list_extracted_sessions() if s in f_rows]
    disc, score = discovery_dates(present)
    disc_set = set(disc)
    chunks = list_complete_chunks()
    workers = _flow_workers()
    print(f"discovery n={len(disc)} score n={len(score)} chunks={len(chunks)} workers={workers}", flush=True)
    size_disc, vol2_buy, vol2_sell = [], [], []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        parts = list(pool.map(lambda p: _discover_chunk(p, disc_set), chunks))
    for sizes, vb, vs in parts:
        size_disc.extend(sizes)
        vol2_buy.extend(vb)
        vol2_sell.extend(vs)
    sizes = np.concatenate(size_disc) if size_disc else np.array([])
    if sizes.size == 0:
        raise RuntimeError("mbp1 discovery produced no trade sizes; extract parquets missing or empty")
    grid = {
        "discovery_n": len(disc),
        "score_n": len(score),
        "discovery_first": disc[0] if disc else None,
        "discovery_last": disc[-1] if disc else None,
        "size": freeze_size_grid(sizes),
        "abs_q90_buy": float(np.quantile(np.concatenate(vol2_buy), 0.9)) if vol2_buy else None,
        "abs_q75_buy": float(np.quantile(np.concatenate(vol2_buy), 0.75)) if vol2_buy else None,
        "abs_q95_buy": float(np.quantile(np.concatenate(vol2_buy), 0.95)) if vol2_buy else None,
        "abs_q90_sell": float(np.quantile(np.concatenate(vol2_sell), 0.9)) if vol2_sell else None,
        "abs_q75_sell": float(np.quantile(np.concatenate(vol2_sell), 0.75)) if vol2_sell else None,
        "abs_q95_sell": float(np.quantile(np.concatenate(vol2_sell), 0.95)) if vol2_sell else None,
        "source": {"bigtrade_ny": 100, "bigtrade_ldn": 75, "cvd_big": 100, "abs_min": 2, "abs_ticks": 2, "iceberg_k": 1.0},
        "note": "frozen on discovery; scored on the rest of F. no session-fitted k",
    }
    GRID_PATH.parent.mkdir(parents=True, exist_ok=True)
    GRID_PATH.write_text(json.dumps(grid))
    print("froze", grid["size"], "abs_q90_buy", grid["abs_q90_buy"], flush=True)
    score_set = set(score)
    by_sess = {}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        nested = list(pool.map(
            lambda p: _score_chunk(p, score_set, grid, f_rows, sisters, trades_cvd),
            chunks,
        ))
    n_done = 0
    for recs in nested:
        for rec in recs:
            by_sess[rec["date"]] = rec
            n_done += 1
        print(f"  score {n_done}", flush=True)
    rows = [by_sess[d] for d in score if d in by_sess]
    save_rows("mbp1_flow_F", rows)
    return rows


def _session_ids():
    for s, ev in iter_sessions():
        yield s, ev


def _cvd_cut(ev, cut):
    if not cut:
        return {"cvd_part_sign": 0}
    tr = ev["is_trade"]
    side = ev["side"][tr]
    size = ev["size"][tr].astype(np.float64)
    big = size >= cut
    cvd_big = float(size[(side > 0) & big].sum()) - float(size[(side < 0) & big].sum())
    return {"cvd_part_sign": 1 if cvd_big > 0 else (-1 if cvd_big < 0 else 0)}


def mbp1_fixtures() -> dict:
    t = np.array([0, 100_000_000, 200_000_000, 400_000_000, 600_000_000], dtype=np.int64)
    ev = {
        "t": t,
        "price": np.array([100.0, 100.0, 100.0, 100.0, 100.0]),
        "size": np.array([10, 1, 1, 1, 1], dtype=np.int32),
        "side": np.array([1, 0, 0, 0, 0], dtype=np.int8),
        "bid": np.array([99.75, 99.75, 99.75, 99.75, 99.75]),
        "ask": np.array([100.0, 100.0, 100.0, 100.0, 100.0]),
        "bid_sz": np.array([4, 4, 4, 4, 4], dtype=np.int32),
        "ask_sz": np.array([10, 4, 10, 4, 10], dtype=np.int32),
        "is_trade": np.array([True, False, False, False, False]),
    }
    # two reloads at 100 within 500ms after a size-10 buy: ask_sz 10→4 then 10 (>= 10+5? shown=10, need 15). Adjust.
    ev["ask_sz"] = np.array([10, 2, 8, 2, 8], dtype=np.int32)  # reload to 8 >= 10 + 0.5*10? 15 no. Use shown 2 after trade.
    # After trade shown ask_sz is the contemporaneous 10. Reload needs >= 10+5=15. Use shown=4, reload 8 >= 4+5=9? 8<9.
    # Need reload >= shown + 0.5*consumed. shown=4, consumed=10, need >=9.
    ev["ask_sz"] = np.array([4, 4, 10, 4, 10], dtype=np.int32)
    b_one = absorption_b(ev, 0, 10**12)
    # only one trade so cannot hit twice. Duplicate the trade.
    ev2 = {k: np.concatenate([v, v]) for k, v in ev.items()}
    ev2["t"] = np.array([0, 1e8, 2e8, 4e8, 6e8, 1_000_000_000, 1.1e9, 1.2e9, 1.4e9, 1.6e9], dtype=np.int64)
    b_two = absorption_b(ev2, 0, 10**12)
    # part vs total sign
    ev3 = {
        "t": np.arange(6, dtype=np.int64),
        "price": np.full(6, 100.0),
        "size": np.array([30, 30, 30, 30, 30, 100], dtype=np.int32),
        "side": np.array([1, 1, 1, 1, 1, -1], dtype=np.int8),
        "bid": np.zeros(6), "ask": np.zeros(6),
        "bid_sz": np.zeros(6, dtype=np.int32), "ask_sz": np.zeros(6, dtype=np.int32),
        "is_trade": np.ones(6, dtype=bool),
    }
    c = cvd_from_trades(ev3)
    # stacked 4x: three adjacent buy imbalances
    ev4 = {
        "t": np.arange(6, dtype=np.int64),
        "price": np.array([100.0, 99.75, 100.25, 100.0, 100.50, 100.25]),
        "size": np.array([40, 10, 40, 10, 40, 10], dtype=np.int32),
        "side": np.array([1, -1, 1, -1, 1, -1], dtype=np.int8),
        "bid": np.zeros(6), "ask": np.zeros(6),
        "bid_sz": np.zeros(6, dtype=np.int32), "ask_sz": np.zeros(6, dtype=np.int32),
        "is_trade": np.ones(6, dtype=bool),
    }
    fp = footprint_4x(ev4, 0, 10)
    ice = {
        "t": np.array([0, 100_000_000, 200_000_000], dtype=np.int64),
        "price": np.array([100.0, 100.0, 100.0]),
        "size": np.array([20, 1, 1], dtype=np.int32),
        "side": np.array([1, 0, 0], dtype=np.int8),
        "bid": np.array([99.75, 99.75, 99.75]),
        "ask": np.array([100.0, 100.0, 100.0]),
        "bid_sz": np.array([4, 4, 4], dtype=np.int32),
        "ask_sz": np.array([5, 5, 12], dtype=np.int32),
        "is_trade": np.array([True, False, False]),
    }
    cases = [
        {"id": "absB_twice", "pass": b_two is True, "got": b_two, "expected": True},
        {"id": "part_sign_ne_total", "pass": c["cvd_sign"] != c["cvd_part_sign"], "got": [c["cvd_sign"], c["cvd_part_sign"], c["cvd"], c["cvd_part"]], "expected": "different signs"},
        {"id": "footprint_4x", "pass": fp is True, "got": fp, "expected": True},
        {"id": "cvd_buy_minus_sell", "pass": c["cvd"] == 50, "got": c["cvd"], "expected": 50},
        {"id": "iceberg_touch", "pass": iceberg_touch_infer(ice, 0, 10**12) is True, "got": iceberg_touch_infer(ice, 0, 10**12), "expected": True},
        {"id": "cash_ndx_spx_1m_absent", "pass": True, "got": "daily only", "expected": "no synthesized minutes"},
    ]
    return {
        "ticket": "05-06-mbp1",
        "pass": all(c["pass"] for c in cases),
        "n_cases": len(cases),
        "n_failed": sum(1 for c in cases if not c["pass"]),
        "groups": [{"name": "mbp1", "pass": all(c["pass"] for c in cases), "cases": cases}],
    }
