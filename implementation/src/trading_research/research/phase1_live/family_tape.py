"""FORMULAS.md tape recipes from retained MBP-1 week extracts.

21 vCPU / 80 GiB. One week parquet per worker (up to ~214 MB). 16 workers
keeps peak well under 40 GiB. Do not load the 13 GB of extracts at once.
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import date, time as dtime, timedelta

import numpy as np
import pyarrow.parquet as pq

from trading_research.foundations.calendar import local_timestamp
from trading_research.research.phase1_live import TICK, ZONE
from trading_research.research.phase1_live.clocks import wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.formulas_jumbo import (
    a16_stacked,
    a17_second_transition,
    j16_two_sided_at_eq,
    j17_node_under,
    profile_nodes,
)
from trading_research.research.phase1_live.formulas_flow import (
    digits_thinning,
    r_f01_vwap_fade,
    r_f03_convergence,
    r_f04_candle_stack,
    r_f05_absorption_stack,
    r_r03_thesis,
    r_s01_refill_long,
    r_s06_two_reason,
    r_s07_areas,
    reward_3tick,
)
from trading_research.research.phase1_live.mbp1_extract import list_complete_chunks
from trading_research.research.phase1_live.mbp1_objects import absorption_a, footprint_4x, on_touch_refill
from trading_research.research.phase1_live.threshold_grid import GRID_PATH

TAPE_WORKERS = 16
NS2M = 2 * 60 * 1_000_000_000


def _ns(day: date, clock: dtime, offset: int = 0) -> int:
    return local_timestamp(day + timedelta(days=offset), clock, ZONE)


def _trades(ev, t0, t1):
    tr = ev["is_trade"]
    t = ev["t"][tr]
    m = (t >= t0) & (t < t1)
    return t[m], ev["price"][tr][m], ev["size"][tr][m].astype(np.float64), ev["side"][tr][m]


def _bins(px, sz, side=None):
    if px.size == 0:
        return None
    ticks = np.round(px / TICK).astype(np.int64)
    lo = int(ticks.min())
    rel = ticks - lo
    n = int(ticks.max() - lo + 1)
    vol = np.bincount(rel, weights=sz, minlength=n)
    buy = sell = None
    if side is not None:
        buy = np.bincount(rel, weights=np.where(side > 0, sz, 0.0), minlength=n)
        sell = np.bincount(rel, weights=np.where(side < 0, sz, 0.0), minlength=n)
    return lo, vol, buy, sell


def _bin_dict(lo, vol):
    return {(lo + i) * TICK: float(v) for i, v in enumerate(vol) if v > 0}


def _big_at(px, sz, level, cut=100.0) -> bool:
    if px.size == 0 or level is None:
        return False
    return bool(np.any((sz >= cut) & (np.abs(px - level) <= 2 * TICK)))


def _session_slices(table):
    sess = np.asarray(table.column("session").combine_chunks().to_numpy(zero_copy_only=False))
    n = sess.size
    if n == 0:
        return
    order = None
    if n > 1 and np.any(sess[1:] < sess[:-1]):
        order = np.argsort(sess, kind="mergesort")
        sess = sess[order]
    breaks = np.flatnonzero(sess[1:] != sess[:-1]) + 1 if n > 1 else np.empty(0, dtype=np.int64)
    starts = np.concatenate(([0], breaks))
    ends = np.concatenate((breaks, [n]))
    cols = {}
    for name in ("t", "price", "size", "side", "bid", "ask", "bid_sz", "ask_sz", "is_trade"):
        arr = table.column(name).to_numpy()
        cols[name] = arr[order] if order is not None else arr
    for a, b in zip(starts, ends):
        yield str(sess[a]), {k: v[a:b] for k, v in cols.items()}


def _score_one(session, ev, f_rows, open_rows, grid):
    row = f_rows.get(session)
    if row is None:
        return None
    day = date.fromisoformat(session)
    am0, am1 = _ns(day, dtime(9, 30)), _ns(day, dtime(12, 0))
    rth_end = _ns(day, dtime(16, 0))
    globex = _ns(day, dtime(18, 0), -1)
    t69_0 = wall_ns(day, dtime(6, 0), 0)
    t69_1 = wall_ns(day, dtime(9, 0), 0)
    op = open_rows.get(session, {})
    val, vah = op.get("VAL"), op.get("VAH")
    h, l, w, eq = row.get("H"), row.get("L"), row.get("W69"), row.get("EQ")
    m05h = (h + 0.5 * w) if h is not None and w else None
    m05l = (l - 0.5 * w) if l is not None and w else None
    q_buy = grid.get("abs_q90_buy")
    q_sell = grid.get("abs_q90_sell")
    rec = {
        "date": session, "year": session[:4], "eligible": row.get("eligible"),
        "tape_rev": 1,
        "j15_bigtrade_level": False, "j16_two_sided_eq": False, "j17_node_under": False,
        "a02_ledge_hold": False, "a06_naked_poc": False, "a12_on_lvn": False,
        "a16_stacked": False, "a17_second_tx": False, "a18_single_reach": False,
        "f01_vwap_fade": False, "f03_vwap_conv": False, "f04_stack_revisit": False,
        "f05_poc_flip": False, "f06_abs_va": False, "f08_reward_3tick": False,
        "f09_thinning": False, "f10_protected": False, "f11_delta_lvn": False,
        "f12_arrival_aggr": False, "f13_trap_retest": False, "f14_imb350": False,
        "f15_ofm": False, "f16_fade": False, "f17_refill_zone": False, "f18_squeeze": False,
        "r03_thesis_alive": False,
        "s01_refill": False, "s02_third_retest": False, "s03_thinning": False,
        "s04_imb_trap": False, "s06_two_reason": False, "s07_mfe": False, "s08_node": False,
        "p20_mvfl": False,
    }
    _, px_am, sz_am, sd_am = _trades(ev, am0, am1)
    _, px_rth, sz_rth, sd_rth = _trades(ev, am0, rth_end)
    _, px_69, sz_69, _ = _trades(ev, t69_0, t69_1)
    _, px_on, sz_on, _ = _trades(ev, globex, am0)
    _, px_ldn, sz_ldn, _ = _trades(ev, _ns(day, dtime(2, 0)), _ns(day, dtime(5, 0)))
    if px_am.size:
        rec["j15_bigtrade_level"] = (
            _big_at(px_am, sz_am, m05l) or _big_at(px_am, sz_am, m05h) or _big_at(px_am, sz_am, eq)
            or _big_at(px_ldn, sz_ldn, m05l, 75) or _big_at(px_ldn, sz_ldn, m05h, 75)
        )
    if px_rth.size and eq is not None:
        packed = _bins(px_rth, sz_rth, sd_rth)
        if packed is not None:
            lo, vol, buy, sell = packed
            eq_t = int(round(eq / TICK))
            i0 = max(0, eq_t - lo - 2)
            i1 = min(vol.size, eq_t - lo + 3)
            if i1 > i0 and buy is not None and sell is not None:
                med_b = float(np.median(buy[buy > 0])) if np.any(buy > 0) else 0.0
                med_s = float(np.median(sell[sell > 0])) if np.any(sell > 0) else 0.0
                bb = {(lo + i) * TICK: float(buy[i]) for i in range(i0, i1)}
                ss = {(lo + i) * TICK: float(sell[i]) for i in range(i0, i1)}
                rec["j16_two_sided_eq"] = bool(j16_two_sided_at_eq(bb, ss, med_b, med_s, 2))
            poc = (lo + int(np.argmax(vol))) * TICK
            nodes = profile_nodes(_bin_dict(lo, vol))
            rec["a17_second_tx"] = bool(a17_second_transition([float(v) for v in vol if v > 0])["second_transition"])
            rec["s08_node"] = bool(len(nodes.get("hvn") or []) >= 2)
            if px_on.size:
                rec["a06_naked_poc"] = not bool(np.any(np.abs(px_on - poc) <= TICK))
                on_b = _bins(px_on, sz_on)
                if on_b is not None:
                    on_nodes = profile_nodes(_bin_dict(on_b[0], on_b[1]))
                    open_px = row.get("open_0930")
                    rec["a12_on_lvn"] = bool(open_px is not None and any(abs(open_px - p) <= 2 * TICK for p in on_nodes["lvn"]))
            if buy is not None and sell is not None:
                ask = {(lo + i) * TICK: float(buy[i]) for i in range(buy.size) if buy[i] > 0}
                bid = {(lo + i) * TICK: float(sell[i]) for i in range(sell.size) if sell[i] > 0}
                st = r_f04_candle_stack(ask, bid, k=4.0)
                rec["f04_stack_revisit"] = bool(st.get("stack3") and st.get("zone") and px_am.size and (
                    float(px_am.min()) <= st["zone"][1] and float(px_am.max()) >= st["zone"][0]
                ))
                imb = (sell >= 3.5 * np.maximum(buy, 1e-9)) | (buy >= 3.5 * np.maximum(sell, 1e-9))
                rec["f14_imb350"] = bool(np.any(imb) and rec["j15_bigtrade_level"])
                rec["s04_imb_trap"] = rec["f14_imb350"]
            rec["f11_delta_lvn"] = bool(nodes["lvn"] and poc is not None and any(abs(poc - p) <= 0.05 * (w or 20) for p in nodes["lvn"]))
            if h is not None and w and nodes["hvn"]:
                rec["s06_two_reason"] = bool(r_s06_two_reason(
                    swing_high=h, prior_reject=0.3 * w, r_width=w, hvn=nodes["hvn"][0], tR=0.05 * w,
                    touch_high=float(px_am.max()) if px_am.size else h,
                    reject_close=float(px_am[-1]) if px_am.size else h,
                    entry=float(px_am[0]) if px_am.size else h,
                )["two_reason"])
        else:
            poc = None
    else:
        poc = None
    if px_69.size and eq is not None and w:
        packed69 = _bins(px_69, sz_69)
        if packed69 is not None:
            d69 = _bin_dict(packed69[0], packed69[1])
            rec["j17_node_under"] = bool(
                j17_node_under(d69, eq, w)
                or (m05l is not None and j17_node_under(d69, m05l, w))
                or (m05h is not None and j17_node_under(d69, m05h, w))
            )
    if val is not None and vah is not None:
        if px_am.size:
            ledge = val if (row.get("open_0930") or eq or 0) <= (val + vah) / 2 else vah
            rec["a02_ledge_hold"] = bool(np.any(np.abs(px_am - ledge) <= 2 * TICK))
            rec["a18_single_reach"] = bool(float(px_am.max()) >= vah)
        rec["f06_abs_va"] = bool(absorption_a(
            ev, am0, am1, vah, val, (vah - val) or w or 20.0,
            vol_cut_buy=q_buy, vol_cut_sell=q_sell,
        ))
        rec["r03_thesis_alive"] = not bool(r_r03_thesis(
            val=val, vah=vah, open_px=row.get("open_0930") or eq or 0.0,
            am_high=float(px_am.max()) if px_am.size else 0.0,
            am_low=float(px_am.min()) if px_am.size else 0.0,
            any_close_beyond=False, news=False,
        )["death"])
    if px_am.size:
        vwap = float(np.average(px_am, weights=np.maximum(sz_am, 1e-9)))
        sd = float(np.sqrt(np.average((px_am - vwap) ** 2, weights=np.maximum(sz_am, 1e-9))))
        abs_band = bool(absorption_a(
            ev, am0, am1, vwap + 2 * sd, vwap - 2 * sd, max(4 * sd, w or 20.0),
            vol_cut_buy=q_buy, vol_cut_sell=q_sell,
        )) if sd > 0 else False
        fade = r_f01_vwap_fade(
            vwap, sd or TICK, bar_high=float(px_am.max()), bar_low=float(px_am.min()),
            abs_result={"vol_ok": abs_band, "advance_ok": True},
        )
        rec["f01_vwap_fade"] = bool(fade["touch"] and abs_band)
        if val is not None and vah is not None:
            vwap_on = float(np.average(px_on, weights=np.maximum(sz_on, 1e-9))) if px_on.size else vwap
            rec["f03_vwap_conv"] = bool(r_f03_convergence(
                vwap, vwap_on, 0.5 * (val + vah), (vah - val) or w or 1.0, touch_px=float(px_am[-1]),
            )["convergence"])
            rec["a16_stacked"] = bool(a16_stacked(val, [vwap, vah], (vah - val) or w or 1.0))
        rec["f08_reward_3tick"] = bool(reward_3tick(
            px_am[-min(80, px_am.size):].tolist(),
            absorption_px=float(px_am[0]),
            direction=1 if float(sd_am[: min(20, sd_am.size)].sum()) >= 0 else -1,
        )["reward_3tick"])
        if sz_am.size >= 40:
            rec["f09_thinning"] = bool(digits_thinning(float(np.median(sz_am[:20])), float(np.median(sz_am[-20:]))))
            rec["s03_thinning"] = rec["f09_thinning"]
        rec["f17_refill_zone"] = bool(on_touch_refill(ev, am0, am1))
        rec["f04_stack_revisit"] = rec["f04_stack_revisit"] or bool(footprint_4x(ev, am0, am1))
        rec["f05_poc_flip"] = bool(r_f05_absorption_stack(
            o=float(px_am[0]), c=float(px_am[-1]), delta=float((sz_am * sd_am).sum()),
            poc=poc if poc is not None else float(px_am[0]),
            low=float(px_am.min()), high=float(px_am.max()),
        ).get("disagree_bull") or r_f05_absorption_stack(
            o=float(px_am[0]), c=float(px_am[-1]), delta=float((sz_am * sd_am).sum()),
            poc=poc if poc is not None else float(px_am[0]),
            low=float(px_am.min()), high=float(px_am.max()),
        ).get("disagree_bear"))
        if l is not None:
            rec["s01_refill"] = bool(r_s01_refill_long(
                range_low=l,
                abs_ok=bool(absorption_a(ev, am0, am1, h, l, w or 20.0, vol_cut_buy=q_buy, vol_cut_sell=q_sell)),
                min_print=float(px_am.min()), close_above=float(px_am[-1]),
                objective=h or float(px_am.max()), later_high=float(px_am.max()), later_low=float(px_am.min()),
            )["refill_long"])
        if h is not None:
            rec["s02_third_retest"] = int(np.sum(np.abs(px_am - h) <= 2 * TICK)) >= 3
            rec["f13_trap_retest"] = bool(float(px_am.max()) >= h - 2 * TICK and float(px_am[-1]) < h)
            rec["f16_fade"] = bool(float(px_am.max()) >= h - 2 * TICK and rec["f06_abs_va"])
        rec["s07_mfe"] = bool(r_s07_areas(
            trigger_close=float(px_am[0]), later_high=float(px_am.max()), later_low=float(px_am.min()),
        )["survived_15"])
        rec["p20_mvfl"] = bool(float(sz_am.max()) >= 100 and (float(px_am.max()) - float(px_am.min())) >= 8 * TICK)
        rec["f12_arrival_aggr"] = bool(sz_am.size >= 5 and float(np.median(sz_am[-5:]) - np.median(sz_am[:5])) >= 0)
        rec["f10_protected"] = bool(px_am.size > 10 and float(px_am[-5:].min()) > float(px_am.min()) + 2 * TICK)
        rec["f18_squeeze"] = bool(rec["f04_stack_revisit"] and not rec["f17_refill_zone"])
        rec["f15_ofm"] = rec["f18_squeeze"]
    rec["s08_node"] = bool(rec["s08_node"] or rec["j17_node_under"])
    return rec


def _score_chunk(path, f_rows, open_rows, grid):
    out = []
    table = pq.read_table(path)
    for session, ev in _session_slices(table):
        try:
            rec = _score_one(session, ev, f_rows, open_rows, grid)
        except Exception as exc:
            print(f"tape fail {session} {type(exc).__name__}: {exc}", flush=True)
            continue
        if rec is not None:
            out.append(rec)
    del table
    return out


def build_tape_table() -> list[dict]:
    cached = load_rows("tape_flags_F")
    if cached and cached[0].get("tape_rev") in (1, 2):
        return cached
    f_rows = {r["date"]: r for r in (load_rows("sessions_F") or [])}
    open_rows = {r["date"]: r for r in (load_rows("open_switch_F") or [])}
    grid = {}
    if GRID_PATH.is_file():
        grid = json.loads(GRID_PATH.read_text())
    chunks = list_complete_chunks()
    print(f"tape chunks={len(chunks)} workers={TAPE_WORKERS}", flush=True)
    by_date = {}
    with ThreadPoolExecutor(max_workers=TAPE_WORKERS) as pool:
        parts = list(pool.map(lambda p: _score_chunk(p, f_rows, open_rows, grid), chunks))
    n = 0
    for recs in parts:
        for rec in recs:
            by_date[rec["date"]] = rec
            n += 1
        print(f"  tape {n}", flush=True)
    rows = [by_date[d] for d in sorted(by_date)]
    save_rows("tape_flags_F", rows)
    return rows
