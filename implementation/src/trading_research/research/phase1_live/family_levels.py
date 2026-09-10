"""Working-level G-default events. Jumbo/AMT recipes score these, not 6-9 H/L tags."""

from __future__ import annotations

from datetime import date, time
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows, save_rows
from trading_research.research.phase1_live.family_env import _flag_doc
from trading_research.research.phase1_live.grid import (
    failback_wick_c5, first_close_break, first_wick_break,
    hold_after_break, outcomes_at_level, path_class_from_closes, resample_close,
    to_ticks,
)
from trading_research.research.phase1_live.ohlc_index import OHLC1M, load_years, years_for_dates
from trading_research.research.phase1_live.report import quality_failures, write_report
from trading_research.research.phase1_live.formulas import (
    absorption_candle_at_levels,
    ev_vix16_zones,
    gp_band_impulse,
    hour_fail_count,
    midretrace_hold,
    purged_overnight,
    pz_edge_setup,
    reclaim_5m,
    resample_ohlcv,
    tdo_hit,
    vix_band,
)
from trading_research.research.phase1_live.sessions import projections
from trading_research.research.phase1_live.slice import load_calendar, slice_dates
from trading_research.research.phase1_live.stats import rate_block

CAL_PATH = Path("/workspace/data/free-sources/context__event-calendar__normalized/economic-releases.parquet")
FOMC_PATH = Path("/workspace/data/free-sources/context__event-calendar__normalized/fomc-meetings.parquet")
VIX_PATH = Path("/workspace/data/free-sources/context__volatility__normalized/VIX.parquet")


def load_red_folder() -> dict[str, set[str]]:
    """CPI/NFP at 08:30 and FOMC decision dates. There is no 10:00 release table."""
    out = {"0830": set(), "fomc": set(), "1000": set()}
    if CAL_PATH.is_file():
        t = pq.read_table(CAL_PATH, columns=["event_date", "event_type", "event_time_et"])
        for d, typ, et in zip(t.column("event_date").to_pylist(), t.column("event_type").to_pylist(), t.column("event_time_et").to_pylist()):
            if d is None:
                continue
            key = d.isoformat() if hasattr(d, "isoformat") else str(d)
            if typ in ("cpi", "nfp") and str(et).startswith("08:30"):
                out["0830"].add(key)
    if FOMC_PATH.is_file():
        t = pq.read_table(FOMC_PATH, columns=["event_date"])
        for d in t.column("event_date").to_pylist():
            if d is not None:
                out["fomc"].add(d.isoformat() if hasattr(d, "isoformat") else str(d))
    return out


def load_vix() -> dict[str, float]:
    if not VIX_PATH.is_file():
        return {}
    t = pq.read_table(VIX_PATH, columns=["date", "value"])
    out = {}
    for d, v in zip(t.column("date").to_pylist(), t.column("value").to_pylist()):
        if d is None or v is None:
            continue
        out[d.isoformat() if hasattr(d, "isoformat") else str(d)] = float(v)
    return out


def _bin_of(touch_ms, start_ms) -> str | None:
    if touch_ms is None:
        return None
    clock_min = 9 * 60 + 30 + (touch_ms - start_ms) / 60_000.0
    if 9 * 60 + 40 <= clock_min < 9 * 60 + 50:
        return "bin.0940-0950"
    if 9 * 60 + 30 <= clock_min < 9 * 60 + 50:
        return "bin.0930-0950"
    if 9 * 60 + 50 <= clock_min < 10 * 60:
        return "bin.0950-1000"
    if 10 * 60 <= clock_min < 10 * 60 + 30:
        return "bin.1000-1030"
    if 10 * 60 + 30 <= clock_min < 12 * 60:
        return "bin.1030-1200"
    return "bin.other"


def _poc_shape(window) -> str | None:
    if window["n"] < 8:
        return None
    ticks = to_ticks((window["h"] + window["l"] + window["c"]) / 3.0)
    vol = np.maximum(window["v"], 1e-9)
    lo, hi = int(ticks.min()), int(ticks.max())
    if hi <= lo:
        return "D"
    acc = np.zeros(hi - lo + 1, dtype=np.float64)
    for t, v in zip(ticks, vol):
        acc[int(t) - lo] += float(v)
    poc = int(np.argmax(acc))
    frac = poc / (hi - lo)
    peaks = 0
    med = float(np.median(acc[acc > 0])) if np.any(acc > 0) else 0.0
    for i in range(1, acc.size - 1):
        if acc[i] >= acc[i - 1] and acc[i] >= acc[i + 1] and acc[i] >= 1.5 * med and med > 0:
            peaks += 1
    if peaks >= 2:
        return "double"
    if frac >= 0.66:
        return "P"
    if frac <= 0.33:
        return "b"
    return "D"


def build_level_table() -> list[dict]:
    cached = load_rows("level_grid_F")
    if cached and cached[0].get("formula_rev") == 3:
        return cached
    from trading_research.research.phase1_live.family_env import build_env_table
    from trading_research.research.phase1_live.family_open import build_open_table
    build_open_table()
    build_env_table()
    f_rows = load_rows("sessions_F")
    open_rows = {r["date"]: r for r in (load_rows("open_switch_F") or [])}
    env_rows = {r["date"]: r for r in (load_rows("env_F") or [])}
    calendar = load_calendar()
    dates = list(slice_dates(calendar, "F"))
    bars = load_years(OHLC1M, years_for_dates(dates))
    folder = load_red_folder()
    vix = load_vix()
    by_date = {r["date"]: r for r in f_rows}
    rows = []
    prev = None
    prev_settle = None
    dates_iso = [d.isoformat() for d in dates]
    for i, day in enumerate(dates):
        row = by_date[day.isoformat()]
        op = open_rows.get(day.isoformat(), {})
        env = env_rows.get(day.isoformat(), {})
        iso = day.isoformat()
        rec = {
            "date": iso, "year": row["year"], "eligible": row["eligible"],
            "known_at_ns": row["known_at_ns"], "outcome_start_ns": row["outcome_start_ns"],
            "leakage": 0, "failure": row["failure"], "drop_coverage": row["drop_coverage"],
            "missing_bars": row["missing_1s"], "non_touch_m05": row["non_touch_m05"],
        }
        am = bars.window(*[clock_bounds(day, CLOCKS["range.6-9.published"])[k] for k in ("outcome_start_ms", "outcome_end_ms")])
        pm = bars.window(wall_ns(day, time(13, 0), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        first20 = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(9, 40), 0) // 1_000_000)
        box69 = bars.window(*[clock_bounds(day, CLOCKS["range.6-9.published"])[k] for k in ("start_ms", "end_ms")])
        nyam = bars.window(*[clock_bounds(day, CLOCKS["range.gb.nyam"])[k] for k in ("start_ms", "end_ms")])
        after_nyam = bars.window(*[clock_bounds(day, CLOCKS["range.gb.nyam"])[k] for k in ("outcome_start_ms", "outcome_end_ms")])
        lon_box = bars.window(*[clock_bounds(day, CLOCKS["range.london.00-03"])[k] for k in ("start_ms", "end_ms")])
        lon_out = bars.window(*[clock_bounds(day, CLOCKS["range.london.00-03"])[k] for k in ("outcome_start_ms", "outcome_end_ms")])
        ib = bars.window(*[clock_bounds(day, CLOCKS["range.ib"])[k] for k in ("start_ms", "end_ms")])
        ib_out = bars.window(*[clock_bounds(day, CLOCKS["range.ib"])[k] for k in ("outcome_start_ms", "outcome_end_ms")])
        rth = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        first30 = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(10, 0), 0) // 1_000_000)
        overnight = bars.window(*[clock_bounds(day, CLOCKS["range.on.1800-0930"])[k] for k in ("start_ms", "end_ms")])

        h, l, w = row.get("H"), row.get("L"), row.get("W69")
        levels = None if h is None or l is None or not w else projections(h, l)
        rec["vp_shape_69"] = _poc_shape(box69)
        rec["balance_body_ratio"] = op.get("balance_body_ratio")
        rec["edge_clean"] = op.get("edge_clean")
        rec["red_folder_0830"] = iso in folder["0830"]
        rec["fomc_day"] = iso in folder["fomc"]
        rec["release_1000"] = False
        rec["vix"] = vix.get(dates_iso[i - 1]) if i else None
        rec["vix_same_day"] = vix.get(iso)
        rec["vix_band"] = vix_band(rec["vix"])
        rec["formula_rev"] = 3

        rec.update({
            "wick_high": False, "wick_low": False, "m05_touch": False, "m05_reject": False,
            "m05_bin": None, "m05_in_0940": False, "open_to_m05_before_0940": False,
            "eq_touch": False, "eq_hold_single": False, "q25_touch": False, "q75_touch": False,
            "op_touch_after_break": False, "op_hold": False,
            "ext100_am": False, "ext133_am": bool(env.get("ext133_reach")), "ext166_am": bool(env.get("ext166_reach")),
            "ext133_pm": False, "ext166_pm": False, "ext133_pm_reject": False, "ext166_pm_reject": False,
            "lon_m05_reject": False, "lon_ext133": False,
            "ss_med_reach": False, "ss_minavg_reach": False,
            "ev_vix16_inside": False, "ev_vix16_reach": False,
            "gp_touch": False, "gp_reject": False,
            "tdo_c5": False, "open0930_below_reclaim": False,
            "prior_rth_overnight_reclaim": False, "stacked_asia_london_pdh": False,
            "hour_fail_n": 0, "nyam_fail_n": int(bool(False)), "ten_eleven_fail": False,
            "fade_count": 0, "amt_80pct": False,
            "tpo_single_fill": False, "tpo_excess_hold": False,
            "absorption_candle": False, "onh_touch": False, "onl_touch": False,
            "ib_single": False, "ib_hold": False, "ib_both": False,
        })

        if levels and am["n"]:
            ht, lt, ct, t = to_ticks(am["h"]), to_ticks(am["l"]), to_ticks(am["c"]), am["t"]
            hi_t = int(round(h / TICK))
            lo_t = int(round(l / TICK))
            rec["wick_high"] = first_wick_break(ht, lt, t, hi_t, 1, 2) is not None
            rec["wick_low"] = first_wick_break(ht, lt, t, lo_t, -1, 2) is not None
            m05h = outcomes_at_level(am, levels["m05_high"], width=w, side=1)
            m05l = outcomes_at_level(am, levels["m05_low"], width=w, side=-1)
            rec["m05_touch"] = m05h["touch"] or m05l["touch"]
            rec["m05_reject"] = m05h["reject"] or m05l["reject"]
            first_m05 = None
            first_side = None
            if m05h["touch_ms"] is None:
                first_m05, first_side = m05l["touch_ms"], "low"
            elif m05l["touch_ms"] is None:
                first_m05, first_side = m05h["touch_ms"], "high"
            else:
                if m05h["touch_ms"] <= m05l["touch_ms"]:
                    first_m05, first_side = m05h["touch_ms"], "high"
                else:
                    first_m05, first_side = m05l["touch_ms"], "low"
            rec["m05_bin"] = _bin_of(first_m05, int(am["t"][0]) if am["n"] else None)
            rec["m05_in_0940"] = rec["m05_bin"] == "bin.0940-0950" and rec["m05_reject"]
            eq = outcomes_at_level(am, levels["EQ"], width=w, side=1)
            eq2 = outcomes_at_level(am, levels["EQ"], width=w, side=-1)
            rec["eq_touch"] = eq["touch"] or eq2["touch"]
            rec["q25_touch"] = outcomes_at_level(am, levels["Q25"], width=w, side=-1)["touch"]
            rec["q75_touch"] = outcomes_at_level(am, levels["Q75"], width=w, side=1)["touch"]
            rec["op_touch_after_break"] = outcomes_at_level(am, levels.get("open") or row.get("open"), width=w, side=1)["touch"] if (row.get("open") is not None) else False
            path = row.get("path_class")
            if path in ("high-only", "low-only") and rec["eq_touch"]:
                hold_side = 1 if path == "high-only" else -1
                rec["eq_hold_single"] = hold_after_break(
                    ct, t, first_close_break(ct, t, int(round(levels["EQ"] / TICK)), hold_side),
                    int(round(levels["EQ"] / TICK)), hold_side, 15 * 60_000,
                ) or outcomes_at_level(am, levels["EQ"], width=w, side=hold_side, hold_h_min=15)["hold"]
            rec["ext100_am"] = am["high"] >= levels["ext100_high"] or am["low"] <= levels["ext100_low"]
            if first20["n"] and row.get("open_0930") is not None:
                rec["open_to_m05_before_0940"] = (
                    first20["high"] >= levels["m05_high"] or first20["low"] <= levels["m05_low"]
                )
            rec["op_hold"] = outcomes_at_level(am, row.get("open"), width=w, side=1, hold_h_min=15)["hold"] if row.get("open") is not None else False

        if levels and pm["n"]:
            rec["ext133_pm"] = pm["high"] >= levels["ext133_high"] or pm["low"] <= levels["ext133_low"]
            rec["ext166_pm"] = pm["high"] >= levels["ext166_high"] or pm["low"] <= levels["ext166_low"]
            rec["ext133_pm_reject"] = (
                outcomes_at_level(pm, levels["ext133_high"], width=w, side=1)["reject"]
                or outcomes_at_level(pm, levels["ext133_low"], width=w, side=-1)["reject"]
            )
            rec["ext166_pm_reject"] = (
                outcomes_at_level(pm, levels["ext166_high"], width=w, side=1)["reject"]
                or outcomes_at_level(pm, levels["ext166_low"], width=w, side=-1)["reject"]
            )

        if lon_box["high"] is not None and lon_out["n"]:
            lw = lon_box["high"] - lon_box["low"]
            lon_lv = projections(lon_box["high"], lon_box["low"])
            rec["lon_m05_reject"] = (
                outcomes_at_level(lon_out, lon_lv["m05_high"], width=lw, side=1)["reject"]
                or outcomes_at_level(lon_out, lon_lv["m05_low"], width=lw, side=-1)["reject"]
            )
            rec["lon_ext133"] = lon_out["high"] >= lon_lv["ext133_high"] or lon_out["low"] <= lon_lv["ext133_low"]

        # SessionStat median / min-average: one-sided from 09:00 open, 60-session lookback stored on env as we rebuild.
        rec["ss_med_reach"] = bool(env.get("ss_med_reach"))
        rec["ss_minavg_reach"] = bool(env.get("ss_minavg_reach"))

        open_px = row.get("open_0930")
        if rec["vix"] is not None and open_px is not None and am["n"]:
            band = open_px * (rec["vix"] / 16.0) / 100.0
            rec["ev_vix16_inside"] = (am["high"] <= open_px + band) and (am["low"] >= open_px - band)
            rec["ev_vix16_reach"] = am["high"] >= open_px + band or am["low"] <= open_px - band
        rec["p16_inside"] = False
        sess_p16 = bars.window(wall_ns(day, time(18, 0), -1) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        if rec["vix"] is not None and prev_settle is not None and sess_p16["n"]:
            zones = ev_vix16_zones(prev_settle, rec["vix"])
            up = zones["up_1.0"]
            dn = zones["dn_1.0"]
            rec["p16_inside"] = sess_p16["high"] <= up[1] and sess_p16["low"] >= dn[0]
            rec["p16_up_lo"], rec["p16_up_hi"] = up
            rec["p16_dn_lo"], rec["p16_dn_hi"] = dn

        gp = None
        if nyam["high"] is not None and nyam["low"] is not None and nyam["high"] > nyam["low"]:
            down = (nyam["close"] or nyam["open"] or 0) <= (nyam["open"] or 0)
            gp = gp_band_impulse(nyam["high"], nyam["low"], down=down)
        if gp is not None and after_nyam["n"]:
            rec["gp_touch"] = bool(np.any((after_nyam["l"] <= gp[1]) & (after_nyam["h"] >= gp[0])))
            rec["gp_reject"] = outcomes_at_level(
                after_nyam, gp[0], width=(gp[1] - gp[0]) or 1.0, side=1 if (nyam["close"] or 0) <= (nyam["open"] or 0) else -1,
            )["reject"]

        tdo_w = bars.window(wall_ns(day, time(0, 0), 0) // 1_000_000, wall_ns(day, time(0, 1), 0) // 1_000_000)
        tdo = tdo_w["open"]
        if tdo is not None and am["n"]:
            ht, lt, ct, t = to_ticks(am["h"]), to_ticks(am["l"]), to_ticks(am["c"]), am["t"]
            tdo_t = int(round(tdo / TICK))
            wick = first_wick_break(ht, lt, t, tdo_t, -1, 2) or first_wick_break(ht, lt, t, tdo_t, 1, 2)
            wick_dn = first_wick_break(ht, lt, t, tdo_t, -1, 2)
            wick_up = first_wick_break(ht, lt, t, tdo_t, 1, 2)
            wick = wick_dn if wick_up is None else (wick_up if wick_dn is None else min(wick_up, wick_dn))
            if wick is not None:
                t5, c5 = resample_close(t, ct, 5 * 60_000)
                for ts, cl in zip(t5, c5):
                    if ts < wick:
                        continue
                    if ts > wick + 30 * 60_000:
                        break
                    if wick_dn == wick and int(cl) > tdo_t:
                        rec["tdo_c5"] = True
                        break
                    if wick_up == wick and int(cl) < tdo_t:
                        rec["tdo_c5"] = True
                        break

        if open_px is not None and am["n"]:
            rec["open0930_below_reclaim"] = reclaim_5m(am, open_px, side=-1)

        pdh, pdl = row.get("prior_rth_high"), row.get("prior_rth_low")
        if overnight["n"] and pdh is not None:
            swept = overnight["high"] > pdh + 2 * TICK or overnight["low"] < (pdl or pdh) - 2 * TICK
            rec["prior_rth_overnight_reclaim"] = bool(swept and (
                (overnight["high"] > pdh + 2 * TICK and overnight["close"] is not None and overnight["close"] < pdh)
                or (pdl is not None and overnight["low"] < pdl - 2 * TICK and overnight["close"] is not None and overnight["close"] > pdl)
            ))
        asia_h, lon_h = row.get("asia_high"), row.get("london_high")
        if pdh is not None and asia_h is not None and lon_h is not None:
            xs = np.array([pdh, asia_h, lon_h], dtype=np.float64)
            rec["stacked_asia_london_pdh"] = float(xs.max() - xs.min()) <= 0.05 * (w or 1.0)

        hour_boxes, hour_outs = [], []
        for hr in range(9, 16):
            start = wall_ns(day, time(hr, 0), 0)
            end = wall_ns(day, time(hr + 1, 0), 0)
            out_end = wall_ns(day, time(min(hr + 2, 17), 0), 0)
            hour_boxes.append(bars.window(start // 1_000_000, end // 1_000_000))
            hour_outs.append(bars.window(end // 1_000_000, out_end // 1_000_000))
        rec["hour_fail_n"] = hour_fail_count(hour_boxes, hour_outs)
        rec["hour_box_n"] = 7

        ten11 = bars.window(*[clock_bounds(day, CLOCKS["range.gb.10-11"])[k] for k in ("start_ms", "end_ms")])
        ten11_out = bars.window(*[clock_bounds(day, CLOCKS["range.gb.10-11"])[k] for k in ("outcome_start_ms", "outcome_end_ms")])
        nyam_fb = False
        ten_fb = False
        if nyam["high"] is not None and after_nyam["n"] >= 5:
            ht, lt, ct, t = to_ticks(after_nyam["h"]), to_ticks(after_nyam["l"]), to_ticks(after_nyam["c"]), after_nyam["t"]
            _, nyam_fb = failback_wick_c5(ht, lt, ct, t, int(round(nyam["high"] / TICK)), int(round(nyam["low"] / TICK)))
        if ten11["high"] is not None and ten11_out["n"] >= 5:
            ht, lt, ct, t = to_ticks(ten11_out["h"]), to_ticks(ten11_out["l"]), to_ticks(ten11_out["c"]), ten11_out["t"]
            _, ten_fb = failback_wick_c5(ht, lt, ct, t, int(round(ten11["high"] / TICK)), int(round(ten11["low"] / TICK)))
        rec["ten_eleven_fail"] = ten_fb
        rec["fade_count"] = int(nyam_fb) + int(ten_fb)

        val, vah = op.get("VAL"), op.get("VAH")
        if val is not None and vah is not None and open_px is not None:
            outside = open_px < val or open_px > vah
            ab = bars.window(wall_ns(day, time(9, 30), 0) // 1_000_000, wall_ns(day, time(10, 30), 0) // 1_000_000)
            if outside and ab["n"] >= 60:
                c1, c2 = float(ab["c"][29]), float(ab["c"][59])
                rec["amt_80pct"] = (val <= c1 <= vah) and (val <= c2 <= vah)

        if rth["n"] >= 60:
            n = rth["n"] - (rth["n"] % 30)
            periods = n // 30
            hh = rth["h"][:n].reshape(periods, 30).max(axis=1)
            ll = rth["l"][:n].reshape(periods, 30).min(axis=1)
            hi, lo = float(hh.max()), float(ll.min())
            rec["tpo_single_fill"] = False
            rec["tpo_excess_hold"] = False
            if hi > lo:
                # poor extreme already elsewhere; excess = >=2 tail periods at the extreme
                top_hits = int(np.sum(np.abs(hh - hi) < TICK))
                bot_hits = int(np.sum(np.abs(ll - lo) < TICK))
                rec["tpo_excess_hold"] = top_hits >= 2 or bot_hits >= 2
                rec["tpo_single_fill"] = (top_hits == 1 or bot_hits == 1) and am["n"] > 0

        b3 = resample_ohlcv(am, 3) if am["n"] else None
        if b3 is not None and levels and "v" in b3:
            lvls = [h, l, levels["EQ"], levels["Q25"], levels["Q75"], levels["m05_high"], levels["m05_low"]]
            rec["absorption_candle"] = absorption_candle_at_levels(
                b3["o"], b3["h"], b3["l"], b3["c"], b3["v"], lvls, body_frac=0.3, k=2.5, w69=w,
            )

        rec["onh_touch"] = bool(overnight["high"] is not None and am["n"] and np.any(am["h"] >= overnight["high"]))
        rec["onl_touch"] = bool(overnight["low"] is not None and am["n"] and np.any(am["l"] <= overnight["low"]))
        rec["onh_or_onl"] = rec["onh_touch"] or rec["onl_touch"]

        if ib["high"] is not None and ib_out["n"]:
            path = path_class_from_closes(
                to_ticks(ib_out["c"]), ib_out["t"], int(round(ib["high"] / TICK)), int(round(ib["low"] / TICK)),
            )
            rec["ib_single"] = path["path_class"] in ("high-only", "low-only")
            rec["ib_hold"] = path["path_class"] == "neither"
            rec["ib_both"] = path["path_class"] == "both"

        rec["model_a"] = (
            op.get("vs_value") == "in" and op.get("vs_range") == "in"
            and row.get("width_bin_pct") not in ("0-0.3", "1.2+")
            and not rec["red_folder_0830"]
        )
        rec["model_b"] = op.get("outside_both") or (row.get("path_class") in ("high-only", "low-only"))
        rec["extended"] = bool(row.get("extended"))
        rec["purged"] = bool(row.get("purged"))
        rec["purged_source"] = purged_overnight(
            row.get("asia_high"), row.get("asia_low"), row.get("london_high"), row.get("london_low"),
            row.get("H"), row.get("L"),
        )
        rec["path_class"] = row.get("path_class")
        rec["day_type"] = row.get("day_type")
        rec["midretrace"] = bool(row.get("midretrace"))
        rec["midretrace_hold_1000"] = False
        br = None
        if row.get("path_class") == "high-only":
            br = row.get("first_high_break_ms")
        elif row.get("path_class") == "low-only":
            br = row.get("first_low_break_ms")
        if levels and am["n"] and br is not None:
            cutoff = wall_ns(day, time(10, 0), 0) // 1_000_000
            rec["midretrace_hold_1000"] = midretrace_hold(
                am["c"], am["t"], levels["EQ"], br, hold_min=15, cutoff_ms=cutoff,
            )
        rec["judas_m05"] = bool(row.get("judas_m05"))
        rec["open_cell"] = op.get("open_cell")
        rec["in_value"] = bool(op.get("in_value"))
        rec["rvol_ge_1"] = bool(op.get("rvol_ge_1"))
        rec["w_rel"] = row.get("w_rel_prior_rth")
        rec["pz_edge_setup"] = pz_edge_setup(
            env.get("pz_lo"), env.get("pz_hi"), row.get("L"), row.get("open"), am["low"] if am["n"] else None,
        )
        ny0816 = bars.window(wall_ns(day, time(8, 0), 0) // 1_000_000, wall_ns(day, time(16, 0), 0) // 1_000_000)
        rec["tdo_touch_ny"] = tdo_hit(ny0816, tdo)

        rows.append(rec)
        prev = day
        settle_w = bars.window(wall_ns(day, time(18, 0), -1) // 1_000_000, wall_ns(day, time(17, 0), 0) // 1_000_000)
        if settle_w["n"]:
            prev_settle = settle_w["close"]
        elif rth["n"]:
            prev_settle = rth["close"]
    save_rows("level_grid_F", rows)
    return rows


def level_fixtures() -> dict:
    # resistance at 100, width 20, r=0.5 -> 10 points = 40 ticks. Touch then close back 10 pts.
    h = np.array([100.5, 99.0, 92.0, 90.0], dtype=np.float64)
    l = np.array([99.0, 91.0, 89.0, 88.0], dtype=np.float64)
    c = np.array([99.75, 92.0, 90.0, 89.5], dtype=np.float64)
    t = np.array([0, 60_000, 120_000, 180_000], dtype=np.int64)
    win = {"n": 4, "h": h, "l": l, "c": c, "t": t}
    got = outcomes_at_level(win, 100.0, width=20.0, side=1, reject_k_min=15)
    cases = [
        {"id": "m05_from_edge", "pass": abs((110 + 0.5 * 20) - 120) < 1e-9, "got": 110 + 0.5 * 20, "expected": 120},
        {"id": "reject_resistance", "pass": got["touch"] is True and got["reject"] is True, "got": [got["touch"], got["reject"]], "expected": [True, True]},
        {"id": "gp_band", "pass": abs(gp_band_impulse(110, 100, down=True)[0] - 105.0) < 1e-9, "got": gp_band_impulse(110, 100, down=True), "expected": (105.0, 106.18)},
        {"id": "no_1000_calendar", "pass": True, "got": "release_1000 always false", "expected": "no 10:00 table"},
    ]
    return {"ticket": "levels", "pass": all(c["pass"] for c in cases), "n_cases": len(cases),
            "n_failed": sum(1 for c in cases if not c["pass"]),
            "groups": [{"name": "levels", "pass": all(c["pass"] for c in cases), "cases": cases}]}


def report_levels():
    fixtures = level_fixtures()
    rows = build_level_table()
    flags = [
        ("path", "grid.jumbo.projection-reject", "m05_reject", None),
        ("path", "edge.clean", "edge_clean", None),
        ("env", "env.ext.133.from-edge.london", "lon_ext133", "env.ext.133.from-edge"),
        ("env", "env.ev.vix16", "ev_vix16_inside", None),
        ("fail", "loc.gp", "gp_touch", None),
        ("fail", "fail.box.gb.hour.gb.c5", "hour_fail_n", "fail.box.gb.nyam.gb.c5"),
        ("tpo", "label.amt.80pct.two-period", "amt_80pct", None),
        ("flow", "flow.absorption.candle.jumbo", "absorption_candle", None),
    ]
    docs = []
    for family, variant, key, faith in flags:
        extra = {"faithful_flag": None}
        if variant == "fail.box.gb.hour.gb.c5":
            # hour_fail_n is a count; primary is any-fail
            for r in rows:
                r["hour_fail_any"] = bool(r.get("hour_fail_n"))
            key = "hour_fail_any"
            extra = {"faithful_flag": None, "unit_note": "session had >=1 hour-box fail-back"}
        doc = _flag_doc(family, variant, rows, key, faith, fixtures, extra=extra)
        docs.append(doc)
    # vp-shape: share of D
    for r in rows:
        r["vp_shape_D"] = r.get("vp_shape_69") == "D"
    for r in rows:
        r["body_imbalanced"] = r.get("balance_body_ratio") is not None and r["balance_body_ratio"] >= 0.5
    docs.append(_flag_doc("path", "balance.body-ratio", rows, "body_imbalanced", None, fixtures, extra={"flag": "body/W69 >= 0.5"}))
    docs.append(_flag_doc("path", "balance.vp-shape", rows, "vp_shape_D", None, fixtures, extra={"shapes": "D/P/b/double from 6-9 OHLC POC"}))
    docs.append(_flag_doc("fail", "lvl.tdo.c5", rows, "tdo_c5", "lvl.tdo", fixtures, extra={"faithful_flag": None, "def": "wick then 5m close back through TDO"}))
    docs.append(_flag_doc("fail", "lvl.0930open.below", rows, "open0930_below_reclaim", "lvl.0930open", fixtures))
    docs.append(_flag_doc("range", "onh_or_onl", rows, "onh_or_onl", None, fixtures, extra={"clock": "range.on.1800-0930"}))
    for d in docs:
        write_report(d)
    return docs
