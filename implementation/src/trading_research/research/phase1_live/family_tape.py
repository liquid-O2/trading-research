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
    r_f02_grid_div,
    r_f02_fakeout_grade,
    r_f03_convergence,
    r_f04_candle_stack,
    r_f05_absorption_stack,
    r_r03_thesis,
    r_s01_refill_long,
    r_s01_refill_short,
    r_s03_second_defence,
    r_s04_ath_ofm,
    r_s05_microbalance,
    r_s06_two_reason,
    r_s07_areas,
    r_f13_trapped_buyers,
    r_f15_ofm,
    r_f16_balance_fade,
    r_f18_squeeze,
    tape_speed_pps,
    reward_3tick,
)
from trading_research.research.phase1_live.mbp1_extract import list_complete_chunks
from trading_research.research.phase1_live.mbp1_objects import absorption_a, footprint_4x, on_touch_refill
from trading_research.research.phase1_live.threshold_grid import GRID_PATH

TAPE_WORKERS = 8
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


def _delta_pack(px, sz, sd):
    if px.size == 0:
        return None
    ticks = np.round(px / TICK).astype(np.int64)
    lo = int(ticks.min())
    rel = ticks - lo
    n = int(ticks.max() - lo + 1)
    dlt = np.bincount(rel, weights=np.where(sd > 0, sz, -sz).astype(np.float64), minlength=n)
    return {"high": float(px.max()), "low": float(px.min()), "lo": lo, "delta": dlt}


def _merge_delta_packs(packs):
    lo = min(p["lo"] for p in packs)
    hi = max(p["lo"] + p["delta"].size for p in packs)
    acc = np.zeros(hi - lo, dtype=np.float64)
    for p in packs:
        a = p["lo"] - lo
        acc[a:a + p["delta"].size] += p["delta"]
    return {
        "high": max(p["high"] for p in packs),
        "low": min(p["low"] for p in packs),
        "lo": lo,
        "delta": acc,
    }


def _dp_min_near_high(pack, weekly_high, tR):
    lo = pack["lo"]
    d = pack["delta"]
    t0 = int(round((weekly_high - tR) / TICK))
    t1 = int(round(weekly_high / TICK))
    i0 = max(0, t0 - lo)
    i1 = min(d.size, t1 - lo + 1)
    if i1 <= i0:
        return None
    i = i0 + int(np.argmin(d[i0:i1]))
    return (lo + i) * TICK


def _weekly_chunk(path):
    out = []
    table = pq.read_table(path)
    for session, ev in _session_slices(table):
        day = date.fromisoformat(session)
        t, px, sz, sd = _trades(ev, _ns(day, dtime(18, 0), -1), _ns(day, dtime(16, 0)))
        pack = _delta_pack(px, sz, sd)
        if pack is None:
            continue
        pack["date"] = session
        out.append(pack)
    return out


def build_weekly_delta_table() -> list[dict]:
    cached = load_rows("weekly_delta_F")
    if cached and cached[0].get("weekly_rev") == 2:
        return cached
    chunks = list_complete_chunks()
    print(f"weekly-delta chunks={len(chunks)} workers={TAPE_WORKERS}", flush=True)
    packs = []
    with ThreadPoolExecutor(max_workers=TAPE_WORKERS) as pool:
        for part in pool.map(_weekly_chunk, chunks):
            packs.extend(part)
            print(f"  weekly {len(packs)}", flush=True)
    packs.sort(key=lambda p: p["date"])
    history = []
    rows = []
    for pack in packs:
        rec = {
            "date": pack["date"], "weekly_high": None, "weekly_low": None,
            "dp_min": None, "tR": None, "weekly_rev": 2,
        }
        if len(history) >= 5:
            merged = _merge_delta_packs(history[-5:])
            rec["weekly_high"] = merged["high"]
            rec["weekly_low"] = merged["low"]
            rec["tR"] = 0.05 * max(merged["high"] - merged["low"], TICK)
            rec["dp_min"] = _dp_min_near_high(merged, rec["weekly_high"], rec["tR"])
            rec["weekly_rev"] = 2
        history.append(pack)
        rows.append(rec)
    save_rows("weekly_delta_F", rows)
    print(f"weekly-delta n={len(rows)} ready={sum(r['weekly_high'] is not None for r in rows)}", flush=True)
    return rows


def _s04_from_am(t, px, sz, sd, wk, row, w):
    if wk is None or wk.get("weekly_high") is None or wk.get("dp_min") is None or px.size < 50:
        return False
    prior = row.get("prior_rth_high")
    minute = t // 60_000_000_000
    order = np.argsort(minute, kind="mergesort")
    minute, px, sz, sd = minute[order], px[order], sz[order], sd[order]
    br = np.flatnonzero(minute[1:] != minute[:-1]) + 1
    st = np.concatenate(([0], br))
    en = np.concatenate((br, [minute.size]))
    n = st.size
    o = np.empty(n); hi = np.empty(n); lo = np.empty(n); cl = np.empty(n)
    for i, (a, b) in enumerate(zip(st, en)):
        o[i] = float(px[a]); hi[i] = float(px[a:b].max()); lo[i] = float(px[a:b].min()); cl[i] = float(px[b - 1])
    touches = 0
    no_close_below = True
    if prior is not None:
        for i in range(n):
            if cl[i] < prior:
                no_close_below = False
            if hi[i] >= prior - 2 * TICK:
                touches += 1
    packed = _bins(px, sz, sd)
    imb350_buy = False
    if packed is not None:
        blo, _vol, buy, sell = packed
        i = int(round(wk["dp_min"] / TICK)) - blo
        if buy is not None and 0 <= i < buy.size:
            imb350_buy = float(buy[i]) >= 3.5 * max(float(sell[i]), 1e-9)
    r_h = float(w) if w else float(wk["weekly_high"] - wk["weekly_low"])
    s05 = r_s05_microbalance(
        cl, lo, hi, r_height=max(r_h, 1.0), break_close=float(cl[-1]),
        htf=float(prior or wk["weekly_high"]), later_high=float(hi.max()), later_low=float(lo.min()),
    )
    box = s05.get("box") or [float(lo.min()), float(hi.max())]
    got = r_s04_ath_ofm(
        weekly_high=float(wk["weekly_high"]), dp_min=float(wk["dp_min"]), tR=float(wk["tR"]),
        left_px=float(px.min()), r_height=max(r_h, 1.0),
        prior_high=float(prior or 0.0), touches=int(touches), no_close_below=bool(no_close_below),
        imb350_buy=bool(imb350_buy), micro_hi=float(box[1]), break_close=float(cl[-1]),
        next_level=float(prior or wk["weekly_high"]), later_high=float(hi.max()),
    )
    return bool(got["ofm_long"])


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
    names = [n for n in ("t", "price", "size", "side", "bid", "ask", "bid_sz", "ask_sz", "is_trade") if n in table.column_names]
    for name in names:
        arr = table.column(name).to_numpy()
        cols[name] = arr[order] if order is not None else arr
    for a, b in zip(starts, ends):
        yield str(sess[a]), {k: v[a:b] for k, v in cols.items()}


def _ofm_and_trap(t, px, sz, sd, h, l, w, row, rec, ev, am0, am1, q_buy, q_sell):
    out = {"f13_trap_retest": False, "f15_ofm": False, "f16_fade": False, "f18_squeeze": False, "s03_thinning": False}
    if t.size < 50:
        return out
    minute = t // 60_000_000_000
    order = np.argsort(minute, kind="mergesort")
    minute, px, sz, sd = minute[order], px[order], sz[order], sd[order]
    br = np.flatnonzero(minute[1:] != minute[:-1]) + 1
    st = np.concatenate(([0], br))
    en = np.concatenate((br, [minute.size]))
    n = st.size
    o = np.empty(n); hi = np.empty(n); lo = np.empty(n); cl = np.empty(n)
    tm = np.empty(n, dtype=np.int64)
    for i, (a, b) in enumerate(zip(st, en)):
        o[i] = float(px[a]); hi[i] = float(px[a:b].max()); lo[i] = float(px[a:b].min()); cl[i] = float(px[b - 1])
        tm[i] = int(t[a] // 1_000_000)
    r_h = float(w) if w else float(hi.max() - lo.min())
    if r_h <= 0:
        r_h = 20.0
    sec = t // 1_000_000_000
    bucket = sec // 30
    rates = np.bincount((bucket - int(bucket.min())).astype(np.int64)) / 30.0
    tape_cut = float(np.quantile(rates, 0.90)) if rates.size else 0.0
    pps = float(rates[-1]) if rates.size else 0.0
    swing_h = float(h) if h is not None else float(hi.max())
    swing_l = float(l) if l is not None else float(lo.min())
    wick_hi, wick_lo = [], []
    for i, (a, b) in enumerate(zip(st, en)):
        body_lo, body_hi = min(o[i], cl[i]), max(o[i], cl[i])
        for j in range(a, b):
            if sz[j] < 30:
                continue
            if px[j] > body_hi or px[j] < body_lo:
                item = (float(px[j]), float(sz[j]), float(tm[i]))
                if sd[j] > 0:
                    wick_hi.append(item)
                else:
                    wick_lo.append(item)
    ofm_h = r_f15_ofm(
        swing=swing_h, r_height=r_h, wick_prints=wick_hi[-8:],
        release_close=float(cl.max()), tape_pps=pps, tape_cut=tape_cut,
        fail_close=float(cl.min()), refill_touch=float(hi.min()),
        resqueeze_close=float(cl[-1]), fail_wick=float(hi.max()),
        stop=swing_h - 2 * TICK, later_high=float(hi.max()), later_low=float(lo.min()),
    )
    ofm_l = r_f15_ofm(
        swing=swing_l, r_height=r_h, wick_prints=wick_lo[-8:],
        release_close=float(cl.min()), tape_pps=pps, tape_cut=tape_cut,
        fail_close=float(cl.max()), refill_touch=float(lo.max()),
        resqueeze_close=float(cl[-1]), fail_wick=float(lo.min()),
        stop=swing_l + 2 * TICK, later_high=float(hi.max()), later_low=float(lo.min()),
    )
    out["f15_ofm"] = bool(ofm_h.get("ofm_entry") or ofm_l.get("ofm_entry"))
    out["f18_squeeze"] = False
    if ofm_h.get("catalyst"):
        sq_h = r_f18_squeeze(
            catalyst=ofm_h["catalyst"],
            release_close=float(cl.max()), tape_pps=pps, tape_cut=tape_cut,
            any_close_through=bool(np.any(cl < min(ofm_h["catalyst"]))),
            trigger_abs=bool(rec.get("f06_abs_va")), next_level=row.get("prior_rth_high") or swing_h,
            later_touch=float(hi.max()),
        )
        out["f18_squeeze"] = bool(sq_h.get("trigger") and sq_h.get("no_failure"))
    if not out["f18_squeeze"] and ofm_l.get("catalyst"):
        sq_l = r_f18_squeeze(
            catalyst=ofm_l["catalyst"],
            release_close=float(cl.min()), tape_pps=pps, tape_cut=tape_cut,
            any_close_through=bool(np.any(cl > max(ofm_l["catalyst"]))),
            trigger_abs=bool(rec.get("f06_abs_va")), next_level=row.get("prior_rth_low") or swing_l,
            later_touch=float(lo.min()),
        )
        out["f18_squeeze"] = bool(sq_l.get("trigger") and sq_l.get("no_failure"))
    abs_ok = bool(absorption_a(ev, am0, am1, swing_h, swing_l, r_h, vol_cut_buy=q_buy, vol_cut_sell=q_sell))
    fade_h = r_f16_balance_fade(
        range_lo=swing_l, range_hi=swing_h, wick_ok=len(wick_hi) >= 2, no_close_beyond=not bool(np.any(cl > swing_h)),
        left_px=float(cl.min()), test_high=float(hi.max()), abs_ok=abs_ok, target=swing_l,
        later_low=float(lo.min()), side="high",
    )
    fade_l = r_f16_balance_fade(
        range_lo=swing_l, range_hi=swing_h, wick_ok=len(wick_lo) >= 2, no_close_beyond=not bool(np.any(cl < swing_l)),
        left_px=float(cl.max()), test_low=float(lo.min()), abs_ok=abs_ok, target=swing_h,
        later_high=float(hi.max()), side="low",
    )
    out["f16_fade"] = bool(fade_h.get("fade_trigger") or fade_l.get("fade_trigger"))
    pdh = row.get("prior_rth_high")
    pdl = row.get("prior_rth_low")
    if pdh is not None:
        trap = r_f13_trapped_buyers(
            band_high=float(pdh), dp_max=float(px.max()), tR=0.05 * r_h,
            am_high=float(hi.max()), pm_high=float(hi.max()), any_close_above=bool(np.any(cl > pdh)),
            intra_lo=float(lo.min()), intra_hi=float(hi.max()),
            break_close=float(cl.min()), retest_high=float(hi.max()),
            sell_in_body=bool(cl[-1] < o[-1]), body=(float(min(o[-1], cl[-1])), float(max(o[-1], cl[-1]))),
            reject_close=float(cl[-1]),
        )
        out["f13_trap_retest"] = bool(trap.get("two_failures") and trap.get("retest_hold"))
    cat = ofm_h.get("catalyst") or ofm_l.get("catalyst")
    if cat is not None:
        lvl = float(max(cat) if ofm_h.get("catalyst") else min(cat))
        sells = sz[sd < 0]
        q75 = float(np.quantile(sells, 0.75)) if sells.size else 0.0
        sizes = [float(x) for x in sz[sd < 0][-8:]] or [1.0]
        s03 = r_s03_second_defence(
            level=lvl, break_close=float(cl.min()), retest_high=float(hi.max()),
            sell_vol=float(sz[sd < 0].sum()), q75=q75, print_sizes=sizes,
            later_low=float(lo.min()), r_width=r_h,
        )
        out["s03_thinning"] = bool(s03.get("second_defence"))
    return out


def _score_one(session, ev, f_rows, open_rows, grid, weekly=None):
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
        "tape_rev": 4,
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
    t_am, px_am, sz_am, sd_am = _trades(ev, am0, am1)
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
                rec["s04_imb_trap"] = False
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
            rec["s03_thinning"] = False
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
            rec["s01_refill"] = False
            if val is not None:
                rec["s01_refill"] = bool(r_s01_refill_long(
                    range_low=float(val),
                    abs_ok=bool(absorption_a(ev, am0, am1, vah or h, val, (vah - val) if vah else (w or 20.0), vol_cut_buy=q_buy, vol_cut_sell=q_sell)),
                    min_print=float(px_am.min()), close_above=float(px_am[-1]),
                    objective=vah or float(px_am.max()), later_high=float(px_am.max()), later_low=float(px_am.min()),
                )["refill_long"])
            if not rec["s01_refill"] and vah is not None:
                rec["s01_refill"] = bool(r_s01_refill_short(
                    range_high=float(vah),
                    abs_ok=bool(absorption_a(ev, am0, am1, vah, val or l, (vah - val) if val else (w or 20.0), vol_cut_buy=q_buy, vol_cut_sell=q_sell)),
                    max_print=float(px_am.max()), close_below=float(px_am[-1]),
                    objective=val or float(px_am.min()), later_high=float(px_am.max()), later_low=float(px_am.min()),
                )["refill_short"])
        if h is not None:
            rec["s02_third_retest"] = False
        rec["f13_trap_retest"] = False
        rec["f15_ofm"] = False
        rec["f16_fade"] = False
        rec["f18_squeeze"] = False
        rec["s03_thinning"] = False
        rec["s07_mfe"] = False
        if px_am.size >= 50 and (h is not None or l is not None):
            rec.update(_ofm_and_trap(t_am, px_am, sz_am, sd_am, h, l, w, row, rec, ev, am0, am1, q_buy, q_sell))
        rec["s04_imb_trap"] = bool(_s04_from_am(t_am, px_am, sz_am, sd_am, (weekly or {}).get(session), row, w))
        rec["p20_mvfl"] = bool(float(sz_am.max()) >= 100 and (float(px_am.max()) - float(px_am.min())) >= 8 * TICK)
        rec["f12_arrival_aggr"] = bool(sz_am.size >= 5 and float(np.median(sz_am[-5:]) - np.median(sz_am[:5])) >= 0)
        rec["f10_protected"] = bool(px_am.size > 10 and float(px_am[-5:].min()) > float(px_am.min()) + 2 * TICK)
    rec["s08_node"] = bool(rec["s08_node"] or rec["j17_node_under"])
    return rec


def _score_chunk(path, f_rows, open_rows, grid, weekly=None):
    out = []
    table = pq.read_table(path)
    for session, ev in _session_slices(table):
        try:
            rec = _score_one(session, ev, f_rows, open_rows, grid, weekly)
        except Exception as exc:
            print(f"tape fail {session} {type(exc).__name__}: {exc}", flush=True)
            continue
        if rec is not None:
            out.append(rec)
    del table
    return out


def _s04_chunk(path, f_rows, weekly):
    out = {}
    table = pq.read_table(path)
    for session, ev in _session_slices(table):
        row = f_rows.get(session) or {}
        day = date.fromisoformat(session)
        t, px, sz, sd = _trades(ev, _ns(day, dtime(9, 30)), _ns(day, dtime(12, 0)))
        out[session] = bool(_s04_from_am(t, px, sz, sd, weekly.get(session), row, row.get("W69")))
    return out


def _apply_s04(rows, weekly):
    f_rows = {r["date"]: r for r in (load_rows("sessions_F") or [])}
    chunks = list_complete_chunks()
    print(f"s04 chunks={len(chunks)} workers={TAPE_WORKERS}", flush=True)
    by = {}
    with ThreadPoolExecutor(max_workers=TAPE_WORKERS) as pool:
        parts = list(pool.map(lambda p: _s04_chunk(p, f_rows, weekly), chunks))
    for part in parts:
        by.update(part)
    n = 0
    for rec in rows:
        rec["s04_imb_trap"] = bool(by.get(rec["date"]))
        rec["s04_rev"] = 2
        n += int(rec["s04_imb_trap"])
    save_rows("tape_flags_F", rows)
    print(f"s04 n={len(rows)} ofm_long={n}", flush=True)
    return rows


def build_tape_table() -> list[dict]:
    cached = load_rows("tape_flags_F")
    weekly = {r["date"]: r for r in build_weekly_delta_table()}
    if cached and cached[0].get("tape_rev") == 4 and cached[0].get("s04_rev") == 2:
        return cached
    if cached and cached[0].get("tape_rev") == 4:
        return _apply_s04(cached, weekly)
    f_rows = {r["date"]: r for r in (load_rows("sessions_F") or [])}
    open_rows = {r["date"]: r for r in (load_rows("open_switch_F") or [])}
    grid = {}
    if GRID_PATH.is_file():
        grid = json.loads(GRID_PATH.read_text())
    chunks = list_complete_chunks()
    print(f"tape chunks={len(chunks)} workers={TAPE_WORKERS}", flush=True)
    by_date = {}
    with ThreadPoolExecutor(max_workers=TAPE_WORKERS) as pool:
        parts = list(pool.map(lambda p: _score_chunk(p, f_rows, open_rows, grid, weekly), chunks))
    n = 0
    for recs in parts:
        for rec in recs:
            by_date[rec["date"]] = rec
            n += 1
        print(f"  tape {n}", flush=True)
    rows = [by_date[d] for d in sorted(by_date)]
    save_rows("tape_flags_F", rows)
    return rows


def _f02_one(session, ev, f_rows):
    row = f_rows.get(session)
    if row is None:
        return None
    day = date.fromisoformat(session)
    globex = _ns(day, dtime(18, 0), -1)
    am1 = _ns(day, dtime(12, 0))
    t, px, sz, sd = _trades(ev, globex, am1)
    rec = {"date": session, "eligible": row.get("eligible"), "f02_divergence": False, "f02_fakeout": False, "cvd_step_rev": 3}
    if t.size < 50:
        return rec
    minute = t // 60_000_000_000
    order = np.argsort(minute, kind="mergesort")
    minute, px, sz, sd = minute[order], px[order], sz[order], sd[order]
    breaks = np.flatnonzero(minute[1:] != minute[:-1]) + 1
    starts = np.concatenate(([0], breaks))
    ends = np.concatenate((breaks, [minute.size]))
    n = starts.size
    hi = np.empty(n, dtype=np.float64)
    lo = np.empty(n, dtype=np.float64)
    dlt = np.empty(n, dtype=np.float64)
    cl = np.empty(n, dtype=np.float64)
    mins = np.empty(n, dtype=np.int64)
    for i, (a, b) in enumerate(zip(starts, ends)):
        hi[i] = float(px[a:b].max())
        lo[i] = float(px[a:b].min())
        cl[i] = float(px[b - 1])
        mins[i] = int(minute[a])
        signed = np.where(sd[a:b] > 0, sz[a:b], 0.0) - np.where(sd[a:b] < 0, sz[a:b], 0.0)
        dlt[i] = float(signed.sum())
    cvd = np.cumsum(dlt)
    t0930 = _ns(day, dtime(9, 30)) // 60_000_000_000
    i_am = int(np.searchsorted(mins, t0930, "left"))
    h69, l69 = row.get("H"), row.get("L")
    if h69 is not None:
        hits = np.flatnonzero((np.arange(n) >= i_am) & (hi > h69))
        if hits.size:
            rec["f02_divergence"] = r_f02_grid_div(hi, cvd, int(hits[0]), side="high")
    if not rec["f02_divergence"] and l69 is not None:
        hits = np.flatnonzero((np.arange(n) >= i_am) & (lo < l69))
        if hits.size:
            rec["f02_divergence"] = r_f02_grid_div(lo, cvd, int(hits[0]), side="low")
    if h69 is not None:
        brk = np.flatnonzero((np.arange(n) >= i_am) & (cl > h69))
        if brk.size:
            i = int(brk[0])
            i0 = max(i_am, i - 5)
            rec["f02_fakeout"] = r_f02_fakeout_grade(float(cvd[i] - cvd[i0]))
    return rec


def _f02_chunk(path, f_rows):
    out = []
    table = pq.read_table(path, columns=["session", "t", "price", "size", "side", "is_trade"])
    for session, ev in _session_slices(table):
        try:
            rec = _f02_one(session, ev, f_rows)
        except Exception as exc:
            print(f"f02 fail {session} {type(exc).__name__}: {exc}", flush=True)
            continue
        if rec is not None:
            out.append(rec)
    del table
    return out


def build_f02_table() -> list[dict]:
    cached = load_rows("cvd_step_F")
    if cached and cached[0].get("cvd_step_rev") == 3:
        return cached
    f_rows = {r["date"]: r for r in (load_rows("sessions_F") or [])}
    chunks = list_complete_chunks()
    print(f"f02 chunks={len(chunks)} workers={TAPE_WORKERS}", flush=True)
    by_date = {}
    with ThreadPoolExecutor(max_workers=TAPE_WORKERS) as pool:
        parts = list(pool.map(lambda p: _f02_chunk(p, f_rows), chunks))
    for recs in parts:
        for rec in recs:
            by_date[rec["date"]] = rec
    rows = [by_date[d] for d in sorted(by_date)]
    save_rows("cvd_step_F", rows)
    print(f"f02 n={len(rows)}", flush=True)
    return rows
