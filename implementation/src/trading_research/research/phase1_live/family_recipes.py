"""Session flags for FORMULAS.md gap recipes that 1m OHLC can compute."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

import numpy as np

from trading_research.research.phase1_live import TICK, ZONE
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_open import ohlc_vp
from trading_research.research.phase1_live.formulas import (
    resample_ohlcv,
    vp_p_shape,
)
from trading_research.research.phase1_live.formulas_flow import (
    MAGIC_HOURS,
    r_p01_sigma_bands,
    r_p01_touch_revert,
    r_p02_hourly_sweep,
    r_p03_magic_hour,
    r_p04_raid,
    r_p05_london_25,
    r_p06_first_hit,
    r_p07_or_mid,
    r_p09_no_break,
    r_p10_pivots,
    r_p11_first_fvg,
    r_p12_sweep_cisd,
    r_p14_hod_checkpoint,
    r_p15_ssl,
    r_p18_ohlc_cvd,
    r_p19_body_gap,
    r_f02_grid_div,
    r_f02_fakeout_grade,
    r_r04_smt_prior,
    sample_stdev,
)
from trading_research.research.phase1_live.formulas_jumbo import (
    a01_fade,
    a03_reentry_traverse,
    a05_poc_tell,
    a07_break_retest,
    a08_reaccept,
    a09_traverse_nohold,
    j10_draw,
    j18_ob_bear,
    j18_ob_bull,
    j19_pd_touch,
    j20_delayed,
    j21_class,
    j22_three_strike,
    j24_management,
    j25_fractal_swings,
    j25_mid_retrace_hold,
)
from trading_research.research.phase1_live.grid import first_close_break, to_ticks
from trading_research.research.phase1_live.family_levels import load_red_folder
from trading_research.research.phase1_live.ohlc_index import OHLC1M, SISTERS_1M, load_years, years_for_dates
from trading_research.research.phase1_live.sessions import projections
from trading_research.research.phase1_live.slice import load_calendar, slice_dates

ET = ZoneInfo(ZONE)


def _hours(t_ms: np.ndarray) -> np.ndarray:
    out = np.empty(t_ms.size, dtype=np.int32)
    for i, ms in enumerate(t_ms):
        dt = datetime.fromtimestamp(int(ms) / 1000.0, tz=timezone.utc).astimezone(ET)
        out[i] = dt.hour
    return out


def _clock(bars, day, cid):
    b = clock_bounds(day, CLOCKS[cid])
    return bars.window(b["start_ms"], b["end_ms"]), bars.window(b["outcome_start_ms"], b["outcome_end_ms"])


def build_recipe_table() -> list[dict]:
    cached = load_rows("recipe_flags_F")
    if cached and cached[0].get("recipe_rev") == 5:
        return cached
    f_rows = load_rows("sessions_F")
    open_rows = {r["date"]: r for r in (load_rows("open_switch_F") or [])}
    prior_vp = {r["date"]: r for r in (load_rows("prior_rth_trade_vp_F") or [])}
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    years = years_for_dates(dates)
    bars = load_years(OHLC1M, years)
    sisters = {}
    for name, root in SISTERS_1M.items():
        try:
            sisters[name] = load_years(root, years)
        except FileNotFoundError:
            sisters[name] = None
    folder = load_red_folder()
    by_date = {r["date"]: r for r in f_rows}
    closes = []
    rows = []
    prev = None
    rng_hist = []
    for day in dates:
        row = by_date[day.isoformat()]
        op = open_rows.get(day.isoformat(), {})
        rec = {
            "date": row["date"], "year": row["year"], "eligible": row["eligible"],
            "recipe_rev": 5,
            "j10_draw_reach": False, "j18_ob": False, "j19_pd_touch": False,
            "j21_extended": False, "j22_three_strike": False, "j24_mfe_pos": False,
            "j25_mid_hold": False,
            "a01_fade": False, "a03_traverse": False, "a05_poc_chop": False,
            "a07_ib_retest": False, "a08_reaccept": False, "a09_traverse_nohold": False,
            "a11_prior_p": False,
            "p01_revert": False, "p02_hour_retrace": False, "p04_raid": False,
            "p05_lon25": False, "p06_first_hit": False, "p07_or_mid": False,
            "p09_no_break": False, "p10_pp_touch": False, "p11_fvg_fill": False,
            "p12_cisd_var": False, "p14_hod_1000": False, "p15_ssl": False,
            "p17_1800_touch": False, "p19_body_gap4": False,
            "s05_micro_break": False, "s09_vah_break": False, "p03_magic_win": False,
            "release_1000": False, "j20_delayed": False,
            "smt_pdh": False, "smt_pdl": False, "p18_cvd_div": False, "p18_fakeout": False,
        }
        h69, l69, w = row.get("H"), row.get("L"), row.get("W69")
        levels = None if h69 is None or l69 is None or not w else projections(h69, l69)
        am = bars.window(*[clock_bounds(day, CLOCKS["range.6-9.published"])[k] for k in ("outcome_start_ms", "outcome_end_ms")])
        rth = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        overnight = bars.window(*[clock_bounds(day, CLOCKS["range.on.1800-0930"])[k] for k in ("start_ms", "end_ms")])
        ib, ib_out = _clock(bars, day, "range.ib")
        or5, or5_out = _clock(bars, day, "range.or.5m")
        nyam, nyam_out = _clock(bars, day, "range.gb.nyam")
        lon_box, lon_out = _clock(bars, day, "range.london.00-03")
        asia_box, _ = _clock(bars, day, "range.gb.asia")
        win0812 = bars.window(wall_ns(day, time(8, 0), 0) // 1_000_000, wall_ns(day, time(12, 0), 0) // 1_000_000)
        sess = bars.window(wall_ns(day, time(18, 0), -1) // 1_000_000, wall_ns(day, time(17, 0), 0) // 1_000_000)
        first20 = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(9, 50), 0) // 1_000_000)
        open_px = row.get("open_0930")
        pv = prior_vp.get(prev.isoformat() if prev is not None else "", {})
        val, vah, poc = op.get("VAL"), op.get("VAH"), pv.get("poc")
        pdh, pdl = row.get("prior_rth_high"), row.get("prior_rth_low")
        path = row.get("path_class")

        if levels and am["n"]:
            fire = float(open_px) if open_px is not None else levels["EQ"]
            side = "long" if row.get("m05_side") == "low" or path == "low-only" else "short"
            cands = []
            if row.get("london_high") is not None:
                cands.append(("london_h", float(row["london_high"]), "high"))
            if row.get("asia_high") is not None:
                cands.append(("asia_h", float(row["asia_high"]), "high"))
            if pdh is not None:
                cands.append(("pdh", float(pdh), "high"))
            if row.get("london_low") is not None:
                cands.append(("london_l", float(row["london_low"]), "low"))
            if row.get("asia_low") is not None:
                cands.append(("asia_l", float(row["asia_low"]), "low"))
            if pdl is not None:
                cands.append(("pdl", float(pdl), "low"))
            draw = j10_draw(fire, cands, side=side)
            if draw is not None:
                name, lvl = draw
                if name.endswith("h") or name == "pdh":
                    rec["j10_draw_reach"] = bool(am["high"] >= lvl - 2 * TICK)
                else:
                    rec["j10_draw_reach"] = bool(am["low"] <= lvl + 2 * TICK)
            b3 = resample_ohlcv(am, 3)
            if b3 and b3["n"] >= 3:
                for i in range(2, b3["n"]):
                    c1 = {"h": float(b3["h"][i - 2]), "l": float(b3["l"][i - 2]), "c": float(b3["c"][i - 2])}
                    c2 = {"h": float(b3["h"][i - 1]), "l": float(b3["l"][i - 1]), "c": float(b3["c"][i - 1])}
                    c3 = {"h": float(b3["h"][i]), "l": float(b3["l"][i]), "c": float(b3["c"][i])}
                    if j18_ob_bull(c1, c2, c3, levels["m05_low"])["ob_bull"] or j18_ob_bear(c1, c2, c3, levels["m05_high"])["ob_bear"]:
                        rec["j18_ob"] = True
                        break
            if pdh is not None and pdl is not None and open_px is not None:
                direction = "down" if open_px < pdl else ("up" if open_px > pdh else ("down" if path == "low-only" else "up"))
                touch = j19_pd_touch(direction, pdh, pdl, am["high"], am["low"])
                rec["j19_pd_touch"] = bool(touch["pdh_touch"] or touch["pdl_touch"])
            rec["j21_extended"] = j21_class(
                red_folder_0830=False,
                w_rel_prior_rth=row.get("w_rel_prior_rth"),
                single_break=path in ("high-only", "low-only"),
                eq_return_by_1000=bool(row.get("midretrace")),
            ) == "extended" or bool(row.get("extended"))
            m05 = levels["m05_low"] if path == "low-only" else levels["m05_high"]
            returns = []
            if am["n"]:
                ht, lt = am["h"], am["l"]
                for i in range(am["n"]):
                    if abs(ht[i] - m05) <= 2 * TICK or abs(lt[i] - m05) <= 2 * TICK:
                        if path == "low-only":
                            returns.append(float(ht[i] - m05) if i + 1 < am["n"] else 0.0)
                        else:
                            returns.append(float(m05 - lt[i]) if i + 1 < am["n"] else 0.0)
            rec["j22_three_strike"] = bool(j22_three_strike(returns[:3], w)["three_strike"]) if len(returns) >= 3 else False
            if first20["n"] and open_px is not None:
                side = "long" if path == "low-only" else "short"
                entry = levels["m05_low"] if side == "long" else levels["m05_high"]
                mg = j24_management(
                    entry, side=side, r=w,
                    high_0950=float(first20["high"]), low_0950=float(first20["low"]),
                    high_1200=float(am["high"]), low_1200=float(am["low"]),
                    eq=levels["EQ"], clean_edge=h69 if side == "long" else l69,
                )
                rec["j24_mfe_pos"] = bool((mg["MFE_0950"] or 0) > 0)
            swings = j25_fractal_swings(am["h"], am["l"])
            if swings["highs"] and swings["lows"] and path in ("high-only", "low-only"):
                lo = swings["lows"][0]["px"]
                hi = swings["highs"][0]["px"]
                rec["j25_mid_hold"] = bool(j25_mid_retrace_hold(lo, hi, am, w, uptrend=path == "high-only")["mid_retrace_hold"])

        if val is not None and vah is not None and am["n"] and poc is not None:
            fade = a01_fade(am, val, vah, poc)
            rec["a01_fade"] = bool(fade["val_reject"] or fade["vah_reject"])
            trav = a03_reentry_traverse(rth if rth["n"] else am, val, vah, open_px=open_px)
            rec["a03_traverse"] = bool(trav["traverse"])
            tell = a05_poc_tell(am, poc, val, vah)
            rec["a05_poc_chop"] = tell["poc_case"] == "chop"
            rec["a08_reaccept"] = bool(a08_reaccept(rth if rth["n"] else am, val, vah, break_side=-1 if (open_px or 0) < val else 1)["reaccept"])
            rec["a09_traverse_nohold"] = bool(a09_traverse_nohold(am, val, vah)["traverse_nohold"])
        if ib["high"] is not None and ib_out["n"] and val is not None:
            rec["a07_ib_retest"] = bool(a07_break_retest(
                ib_out, ib_out, ib["high"], (ib["high"] - ib["low"]) or 1.0, vah or ib["high"], rth if rth["n"] else ib_out, break_side=1,
            )["retest_hold"] or a07_break_retest(
                ib_out, ib_out, ib["low"], (ib["high"] - ib["low"]) or 1.0, val or ib["low"], rth if rth["n"] else ib_out, break_side=-1,
            )["retest_hold"])
        if prev is not None:
            pr = bars.window(wall_ns(prev, time(9, 30), 0) // 1_000_000, wall_ns(prev, time(16, 0), 0) // 1_000_000)
            if pr["n"] >= 9:
                acc = {}
                ticks = to_ticks((pr["h"] + pr["l"] + pr["c"]) / 3.0)
                for tk, v in zip(ticks, pr["v"]):
                    acc[int(tk)] = acc.get(int(tk), 0.0) + float(v)
                vols = [acc[k] for k in sorted(acc)]
                rec["a11_prior_p"] = vp_p_shape(vols) == "P" and path in ("high-only", "low-only")

        if win0812["n"] and len(closes) >= 5:
            chg = np.diff(np.log(np.maximum(np.array(closes[-20:], dtype=np.float64), 1e-9))) * 100.0
            sig = sample_stdev(chg) if chg.size >= 2 else None
            open8 = bars.window(wall_ns(day, time(8, 0), 0) // 1_000_000, wall_ns(day, time(8, 1), 0) // 1_000_000)["open"]
            if sig and open8 is not None:
                bands = r_p01_sigma_bands(open8, sig, 0.25)
                hr = _hours(win0812["t"])
                tr = r_p01_touch_revert(open8, bands["upper"], bands["lower"], bands["sigma_px"], hr, win0812["h"], win0812["l"])
                rec["p01_revert"] = bool(tr.get("reverted"))
        hour_ok = False
        for hr in range(9, 16):
            prev_h = bars.window(wall_ns(day, time(hr - 1, 0), 0) // 1_000_000, wall_ns(day, time(hr, 0), 0) // 1_000_000)
            this_h = bars.window(wall_ns(day, time(hr, 0), 0) // 1_000_000, wall_ns(day, time(hr + 1, 0), 0) // 1_000_000)
            if prev_h["high"] is None or this_h["n"] == 0:
                continue
            sw = r_p02_hourly_sweep(
                prev_h=prev_h["high"], prev_l=prev_h["low"], prev_open=prev_h["open"] or 0.0,
                hour_open=this_h["open"] or 0.0, highs=this_h["h"], lows=this_h["l"],
            )
            if sw["high_ret_swept"] or sw["low_sweep"] and sw.get("high_ret_50"):
                hour_ok = True
                break
            if sw["high_sweep"] and sw["high_ret_swept"]:
                hour_ok = True
                break
        rec["p02_hour_retrace"] = hour_ok
        magic = False
        for hr in MAGIC_HOURS:
            off = -1 if hr == 23 else 0
            box = bars.window(wall_ns(day, time(hr, 0), off) // 1_000_000, wall_ns(day, time((hr + 1) % 24, 0), 0 if hr != 23 else 0) // 1_000_000)
            if hr == 23:
                box = bars.window(wall_ns(day, time(23, 0), -1) // 1_000_000, wall_ns(day, time(0, 0), 0) // 1_000_000)
            nxt = bars.window(wall_ns(day, time((hr + 1) % 24, 0), 0 if hr != 23 else 0) // 1_000_000, wall_ns(day, time((hr + 2) % 24, 0), 0) // 1_000_000)
            if hr == 23:
                nxt = bars.window(wall_ns(day, time(0, 0), 0) // 1_000_000, wall_ns(day, time(1, 0), 0) // 1_000_000)
            if box["high"] is None or nxt["n"] == 0:
                continue
            brk = "high" if (nxt["high"] or 0) > box["high"] else "low"
            exc = (nxt["high"] - box["high"]) if brk == "high" else (box["low"] - nxt["low"])
            got = r_p03_magic_hour(
                hour=hr, box_h=box["high"], box_l=box["low"], break_side=brk, excursion=exc or 0.0,
                later_high=nxt["high"], later_low=nxt["low"], t_break_min=hr * 60 + 4, t_target_min=hr * 60 + 20,
            )
            if got.get("win"):
                magic = True
                break
        rec["p03_magic_win"] = magic
        if nyam["high"] is not None and nyam_out["n"]:
            t_min = (nyam_out["t"] - nyam_out["t"][0]) / 60_000.0
            raid = r_p04_raid(
                box_h=nyam["high"], box_l=nyam["low"], highs=nyam_out["h"], lows=nyam_out["l"],
                closes=nyam_out["c"], t_min=t_min, cutoff_min=120.0,
            )
            rec["p04_raid"] = bool(raid.get("raid_hi_conf") or raid.get("raid_hi"))
        if lon_box["open"] is not None and lon_box["close"] is not None and am["n"]:
            lon25 = r_p05_london_25(lon_box["open"], lon_box["close"], am["low"], am["high"], am["close"])
            rec["p05_lon25"] = bool(lon25.get("wick_lon25_bull") or lon25.get("wick_lon25_bear") or lon25.get("fail"))
        if asia_box["high"] is not None and lon_box["n"]:
            rec["p06_first_hit"] = r_p06_first_hit(
                asia_h=asia_box["high"], asia_l=asia_box["low"], lon_open=lon_box["open"] or 0.0,
                lon_highs=lon_box["h"], lon_lows=lon_box["l"],
            )["london_first_hit"] is not None
        if or5["high"] is not None and or5_out["n"]:
            rec["p07_or_mid"] = bool(r_p07_or_mid(
                o=or5["open"], h=or5["high"], l=or5["low"], c=or5["close"],
                later_h=or5_out["h"], later_l=or5_out["l"], later_c=or5_out["c"],
            )["mid_retest"])
        if open_px is not None and pdh is not None and pdl is not None and rth["n"]:
            nb = r_p09_no_break(open_px, pdh, pdl, rth["high"], rth["low"])
            rec["p09_no_break"] = bool(nb.get("no_break_prev_high") or nb.get("no_break_prev_low") or nb.get("inside_stay"))
        if prev is not None and rth["n"] and open_px is not None:
            pr = bars.window(wall_ns(prev, time(18, 0), -1) // 1_000_000, wall_ns(prev, time(17, 0), 0) // 1_000_000)
            if pr["n"]:
                piv = r_p10_pivots(pr["high"], pr["low"], pr["close"], rth_open=open_px, rth_high=rth["high"])
                rec["p10_pp_touch"] = bool(piv.get("pp_touch"))
        hour9 = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(10, 0), 0) // 1_000_000)
        if hour9["n"] >= 3:
            hr = _hours(hour9["t"])
            fv = r_p11_first_fvg(hour9["h"], hour9["l"], hour9["c"], hr)
            rec["p11_fvg_fill"] = bool(fv.get("near_edge_fill") or fv.get("w1_fvg"))
        if rth["n"] >= 2:
            rec["p12_cisd_var"] = bool(r_p12_sweep_cisd(
                prev_h=float(rth["h"][0]), prev_l=float(rth["l"][0]), prev_o=float(rth["o"][0]), prev_c=float(rth["c"][0]),
                o=float(rth["o"][1]), h=float(rth["h"][1]), l=float(rth["l"][1]), c=float(rth["c"][1]),
            )["sweep_close"])
        if rth["n"]:
            first30 = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(10, 0), 0) // 1_000_000)
            hod = float(rth["high"])
            rec["p14_hod_1000"] = bool(first30["n"] and first30["high"] >= hod - TICK)
            if rng_hist:
                p_rng = float(np.median(rng_hist[-60:]))
                rec["p15_ssl"] = bool(r_p15_ssl(
                    open_px=open_px or 0.0, p_rng=p_rng, p_mfe=0.6 * p_rng, p_mae=0.4 * p_rng,
                    session_high=rth["high"], session_low=rth["low"],
                )["mfe_p50_hit"])
        open18 = bars.window(wall_ns(day, time(18, 0), -1) // 1_000_000, wall_ns(day, time(18, 1), -1) // 1_000_000)["open"]
        if open18 is not None and rth["n"]:
            rec["p17_1800_touch"] = bool(rth["high"] >= open18 >= rth["low"] or np.any((rth["h"] >= open18) & (rth["l"] <= open18)))
        if am["n"] >= 2:
            rec["p19_body_gap4"] = bool(r_p19_body_gap(am["o"], am["h"], am["l"], am["c"], min_ticks=4).get("gap"))
        if am["n"] >= 20:
            micro = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(9, 40), 0) // 1_000_000)
            rest = bars.window(wall_ns(day, time(9, 40), 0) // 1_000_000, wall_ns(day, time(12, 0), 0) // 1_000_000)
            if micro["high"] is not None and rest["n"]:
                rec["s05_micro_break"] = bool(np.any(rest["c"] > micro["high"]) or np.any(rest["c"] < micro["low"]))
        if rth["n"] >= 40 and open_px is not None:
            pre = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(10, 0), 0) // 1_000_000)
            post = bars.window(wall_ns(day, time(10, 0), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
            poc, dval, dvah = ohlc_vp(pre, 0.70) if pre["n"] else (None, None, None)
            if dvah is not None and post["n"] and open_px > dvah:
                rec["s09_vah_break"] = bool(np.any(post["c"] > dvah) and np.any(post["l"] <= dvah + 2 * TICK))

        if rth["n"] and rth["high"] is not None and rth["low"] is not None:
            rng_hist.append(rth["high"] - rth["low"])
        iso = day.isoformat()
        rec["release_1000"] = iso in folder["1000"]
        rec["j20_delayed"] = j20_delayed(rec["release_1000"], row.get("reversal_bin"))
        if prev is not None:
            nq_pr = bars.window(wall_ns(prev, time(9, 30), 0) // 1_000_000, wall_ns(prev, time(16, 0), 0) // 1_000_000)
            nq_am_h = am["high"] if am["n"] else None
            nq_am_l = am["low"] if am["n"] else None
            pdh_n, pdl_n = nq_pr.get("high"), nq_pr.get("low")
            for sname, sb in sisters.items():
                if sb is None or pdh_n is None:
                    continue
                spr = sb.window(wall_ns(prev, time(9, 30), 0) // 1_000_000, wall_ns(prev, time(16, 0), 0) // 1_000_000)
                sam = sb.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(12, 0), 0) // 1_000_000)
                if spr["high"] is None or sam["n"] == 0:
                    continue
                if r_r04_smt_prior(pdh_n, spr["high"], nq_am_h, sam["high"], side="high"):
                    rec["smt_pdh"] = True
                if r_r04_smt_prior(pdl_n, spr["low"], nq_am_l, sam["low"], side="low"):
                    rec["smt_pdl"] = True
        on_am = bars.window(wall_ns(day, time(18, 0), -1) // 1_000_000, wall_ns(day, time(12, 0), 0) // 1_000_000)
        if on_am["n"] >= 10:
            p18 = r_p18_ohlc_cvd(on_am["o"], on_am["c"], on_am["v"])
            running = np.cumsum(p18["delta"])
            t0930 = wall_ns(day, time(9, 30), 0) // 1_000_000
            i_am = int(np.searchsorted(on_am["t"], t0930, "left"))
            if h69 is not None:
                hits = np.flatnonzero((np.arange(on_am["n"]) >= i_am) & (on_am["h"] > h69))
                if hits.size:
                    rec["p18_cvd_div"] = r_f02_grid_div(on_am["h"], running, int(hits[0]), side="high")
            if not rec["p18_cvd_div"] and l69 is not None:
                hits = np.flatnonzero((np.arange(on_am["n"]) >= i_am) & (on_am["l"] < l69))
                if hits.size:
                    rec["p18_cvd_div"] = r_f02_grid_div(on_am["l"], running, int(hits[0]), side="low")
            if h69 is not None:
                ct = on_am["c"]
                brk = np.flatnonzero((np.arange(on_am["n"]) >= i_am) & (ct > h69))
                if brk.size:
                    i = int(brk[0])
                    i0 = max(i_am, i - 5)
                    rec["p18_fakeout"] = r_f02_fakeout_grade(float(running[i] - running[i0]))
        if sess["n"]:
            closes.append(sess["close"])
        elif rth["n"]:
            closes.append(rth["close"])
        rows.append(rec)
        prev = day
    save_rows("recipe_flags_F", rows)
    print(
        "recipe n="
        f"{len(rows)} release_1000={sum(bool(r.get('release_1000')) for r in rows)}"
        f" j20={sum(bool(r.get('j20_delayed')) for r in rows)}"
        f" smt={sum(bool(r.get('smt_pdh') or r.get('smt_pdl')) for r in rows)}"
        f" p18={sum(bool(r.get('p18_cvd_div')) for r in rows)}",
        flush=True,
    )
    return rows
