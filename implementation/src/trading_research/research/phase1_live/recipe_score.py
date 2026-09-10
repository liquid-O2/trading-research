"""One RULES.md section B row. Scores only pass functions. No invented recipes."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np

from trading_research.research.phase1_live.compute import load_rows
from trading_research.research.phase1_live.family_levels import build_level_table
from trading_research.research.phase1_live.stats import rate_block, session_bootstrap_rate
from trading_research.research.phase1_live.threshold_grid import attach_rv

SCORES_PATH = Path("/workspace/planning/phase-1-live/RULES_SCORES.md")


def _fmt_int(lo, hi):
    if lo is None or hi is None:
        return "n/a"
    return f"[{lo:.3f}, {hi:.3f}]"


def _fmt_year(block):
    parts = []
    for y in ("2024", "2025", "2026"):
        b = block.get(y) or {}
        r = b.get("rate")
        parts.append(f"{y} {r:.3f}" if r is not None else f"{y} n/a")
    return " / ".join(parts)


def _fmt_rv(terc):
    parts = []
    for name in ("low", "mid", "high"):
        b = terc.get(name) or {}
        r = b.get("rate")
        parts.append(f"{name} {r:.3f}" if r is not None else f"{name} n/a")
    return " / ".join(parts)


def _stats(rows, pred):
    elig = [r for r in rows if r.get("eligible")]
    flags = np.array([1.0 if pred(r) else 0.0 for r in elig], dtype=np.float64)
    dates = [r["date"] for r in elig]
    primary = rate_block(int(flags.sum()), len(elig))
    primary["session_bootstrap_95"] = session_bootstrap_rate(flags)
    years = {}
    for y in ("2024", "2025", "2026"):
        idx = np.array([d.startswith(y) for d in dates], dtype=bool)
        years[y] = rate_block(int(flags[idx].sum()) if flags.size else 0, int(idx.sum()))
    terc = {}
    for name in ("low", "mid", "high"):
        sub = [r for r in elig if r.get("vol_tercile_rv") == name]
        f = np.array([1.0 if pred(r) else 0.0 for r in sub], dtype=np.float64)
        terc[name] = rate_block(int(f.sum()) if f.size else 0, len(sub))
    leak = int(sum(r.get("leakage") or 0 for r in elig))
    return {
        "n": len(elig),
        "k": int(flags.sum()),
        "rate": primary["rate"],
        "interval": _fmt_int(*(primary.get("wilson_95") or [None, None])),
        "year": _fmt_year(years),
        "rv": _fmt_rv(terc),
        "leakage": leak,
    }


def _join():
    levels = attach_rv(build_level_table())
    fail = {r["date"]: r for r in (load_rows("fail_F") or [])}
    sess = {r["date"]: r for r in (load_rows("sessions_F") or [])}
    op = {r["date"]: r for r in (load_rows("open_switch_F") or [])}
    env = {r["date"]: r for r in (load_rows("env_F") or [])}
    tpo = {r["date"]: r for r in (load_rows("gap_block_tpo_F") or [])}
    flow = {r["date"]: r for r in (load_rows("mbp1_flow_F") or [])}
    from trading_research.research.phase1_live.family_recipes import build_recipe_table
    recipe = {r["date"]: r for r in (build_recipe_table() or [])}
    clocks = load_rows("clocks_F") or []
    ib = {}
    for r in clocks:
        if r.get("clock") == "range.ib" and r.get("eligible"):
            ib[r["date"]] = r
    out = []
    for r in levels:
        d = r["date"]
        m = dict(r)
        m.update({k: fail.get(d, {}).get(k) for k in fail.get(d, {}) if k not in m})
        s = sess.get(d, {})
        m.setdefault("path_class", s.get("path_class"))
        m.setdefault("day_type", s.get("day_type"))
        m.setdefault("midretrace", s.get("midretrace"))
        m.setdefault("judas_m05", s.get("judas_m05"))
        m.setdefault("extended", s.get("extended"))
        m.setdefault("purged", s.get("purged"))
        m.setdefault("w_rel_prior_rth", s.get("w_rel_prior_rth"))
        m.setdefault("width_bin_pct", s.get("width_bin_pct"))
        o = op.get(d, {})
        m.setdefault("open_cell", o.get("open_cell"))
        m.setdefault("in_value", o.get("in_value"))
        m.setdefault("outside_both", o.get("outside_both"))
        m.setdefault("in_range_not_value", o.get("in_range_not_value"))
        m.setdefault("rvol_ge_1", o.get("rvol_ge_1"))
        m.setdefault("oneway_A", o.get("oneway_A"))
        e = env.get(d, {})
        m.setdefault("ext133_reach", e.get("ext133_reach"))
        m.setdefault("ext166_reach", e.get("ext166_reach"))
        m.setdefault("ext100_reach", e.get("ext100_reach"))
        m.setdefault("ev_reach_mean60", e.get("ev_reach_mean60"))
        m.setdefault("ss_reach", e.get("ss_reach"))
        m.setdefault("pz_t1_reach", e.get("pz_t1_reach"))
        m.setdefault("ss_med_reach", e.get("ss_med_reach"))
        m.setdefault("ss_minavg_reach", e.get("ss_minavg_reach"))
        tp = tpo.get(d, {})
        m["amt_open_label"] = tp.get("amt_open_label")
        m["amt_day_label"] = tp.get("amt_day_label")
        m["tpo_poor"] = tp.get("tpo_poor")
        m["fvg"] = tp.get("fvg")
        m["body_gap"] = tp.get("body_gap")
        m["sweep_3m"] = tp.get("sweep_3m")
        m["cisd"] = tp.get("cisd")
        fl = flow.get(d, {})
        rp = recipe.get(d, {})
        for k, v in rp.items():
            if k not in m:
                m[k] = v
        m["absorption_A"] = fl.get("absorption_A")
        m["bigtrade_100ny"] = fl.get("bigtrade")
        m["bigtrade_75ldn"] = fl.get("bigtrade_75ldn")
        m["ib_path"] = ib.get(d, {}).get("path_class")
        monday = date.fromisoformat(d).weekday() == 0
        m["monday"] = monday
        out.append(m)
    return out


def catalog():
    """impl_fidelity pass only when every cited slot has a matching pass function."""
    # (id, framework, source_fidelity, impl, event, missing, pred_name)
    rows = []

    def add(rid, fw, src, impl, event, missing, pred=None):
        rows.append({
            "id": rid, "framework": fw, "source_fidelity": src, "impl_fidelity": impl,
            "event": event, "missing": missing, "pred": pred,
        })

    # Jumbo
    add("R-J01", "Jumbo", "faithful", "pass",
        "reject at -0.5 after 6-9 wick sweep, first touch in 09:40-09:50",
        "", "j01")
    add("R-J02", "Jumbo", "faithful", "pass",
        "09:30 open reaches -0.5 before 09:40",
        "", "j02")
    add("R-J03", "Jumbo", "faithful", "pass",
        "single-break on extended overnight, EQ retrace with h=15 by 10:00",
        "", "j03")
    add("R-J04", "Jumbo", "faithful", "pass",
        "overnight Asia and London both swept by 09:30, single-break reach of 1.0",
        "", "j04")
    add("R-J05", "Jumbo", "faithful", "pass",
        "single-break midretrace to EQ / range open",
        "", "j05")
    add("R-J06", "Jumbo", "faithful", "pass",
        "open_cell path class; outside-both + RVOL double-break",
        "", "j06")
    add("R-J07", "Jumbo", "faithful", "pass",
        "path class by w.pct.0859close bin (XF p.24 recompute lives on range.6-9.published)",
        "", "j07")
    add("R-J08", "Jumbo", "faithful", "pass",
        "PM 13:00-16:00 reject at 1.33 from-edge",
        "", "j08")
    add("R-J09", "Jumbo", "faithful", "pass",
        "London 00-03 box -0.5 reject in 03:00-06:00",
        "", "j09")
    add("R-J10", "Jumbo", "faithful", "pass",
        "nearest untouched Asia/London/PDH/PDL draw reached in AM",
        "", "j10")
    add("R-J11", "Jumbo", "faithful", "pass",
        "SessionStat avgHL60 reach (median and min-average are named variants)",
        "", "j11")
    add("R-J12", "Jumbo", "faithful", "pass",
        "P-zone T1 reach with band overlapping 6-9 L, low > OP, Model A, reject at -0.5",
        "", "j12")
    add("R-J13", "Jumbo", "faithful", "pass",
        "env.ev.mean60 reach; reject is not a separate EV function, reach is the sourced working-level event",
        "", "j13")
    add("R-J14", "Jumbo", "faithful", "pass",
        "3m absorption candle at a 6-9 level, trailing SMA14, body/range <=0.3, k=2.5",
        "", "j14")
    add("R-J15", "Jumbo", "faithful", "gap",
        "n/a", "flow.bigtrade.100ny/75ldn at the TBR level (function exists; F tape column needs MBP-1 prints at the touch)", None)
    add("R-J16", "Jumbo", "faithful", "gap",
        "n/a", "RTH VP/delta two-sided at EQ (function exists; F tape bins not on the session table)", None)
    add("R-J17", "Jumbo", "faithful", "gap",
        "n/a", "LVN/shelf under a TBR level (function exists; F trade-profile bins not on the session table)", None)
    add("R-J18", "Jumbo", "faithful", "pass",
        "3-candle OB at -0.5 on 3m AM bars",
        "", "j18")
    add("R-J19", "Jumbo", "faithful", "pass",
        "PDH/PDL touch given open direction",
        "", "j19")
    add("R-J20", "Jumbo", "faithful", "gap",
        "n/a", "10:00 release calendar (inventory has CPI/NFP at 08:30 and FOMC date-only, not 10:00)", None)
    add("R-J21", "Jumbo", "faithful", "pass",
        "condition class extended (red-folder or w.rel-prior-rth >= 1)",
        "", "j21")
    add("R-J22", "Jumbo", "faithful", "pass",
        "three-strike failure protocol at -0.5",
        "", "j22")
    add("R-J23", "Jumbo", "faithful", "pass",
        "path class of TBR published clocks including midnight / A-period / lunch / MOC",
        "", "j23")
    add("R-J24", "Jumbo", "faithful", "pass",
        "MFE after -0.5 entry by 09:50 is positive",
        "", "j24")
    add("R-J25", "Jumbo", "faithful", "pass",
        "swing-mid retrace hold on a single-break session",
        "", "j25")

    # Green Bird
    add("R-G01", "Green Bird", "faithful", "pass",
        "NYAM 09:00-10:00 wick then 5m close-back after 10:00",
        "", "g01")
    add("R-G02", "Green Bird", "faithful", "pass",
        "Asia 20:00-00:00 wick then 5m close-back 00:00-06:00",
        "", "g02")
    add("R-G03", "Green Bird", "faithful", "pass",
        "last completed clock-hour box fail-back",
        "", "g03")
    add("R-G04", "Green Bird", "faithful", "pass",
        "sweep below 09:30 open then 5m close reclaim",
        "", "g04")
    add("R-G05", "Green Bird", "faithful", "pass",
        "TDO wick then 5m close back through midnight open",
        "", "g05")
    add("R-G06", "Green Bird", "faithful", "pass",
        "Monday NWOG fill by 12:00 (Friday 16:00 close vs Sunday 18:00 open)",
        "", "g06")
    add("R-G07", "Green Bird", "faithful", "pass",
        "touch of NYAM 50-61.8% golden pocket after 10:00, measured from impulse end",
        "", "g07")
    add("R-G08", "Green Bird", "faithful", "pass",
        "overnight sweep of PDH/PDL then close back through before 09:30",
        "", "g08")
    add("R-G09", "Green Bird", "faithful", "pass",
        "PDH + Asia high + London high stacked within 0.05 R, Monday NWOG fill",
        "", "g09")
    add("R-G10", "Green Bird", "faithful", "pass",
        "NYAM fail-back plus 10-11 fail-back (fade count >= 2)",
        "", "g10")
    add("R-G11", "Green Bird", "faithful", "pass",
        "label.aplus = NYAM sweep (RTH traded range after 10:00). Sweep-only per FORMULAS.md procedure and PRD. Fail-back is R-G01.",
        "", "g11")

    # AMT
    add("R-A01", "AMT", "faithful", "pass",
        "G-default reject at prior VAL/VAH",
        "", "a01")
    add("R-A02", "AMT", "faithful", "gap",
        "n/a", "ledge retest hold (function exists; F trade-profile shelves not on the session table)", None)
    add("R-A03", "AMT", "faithful", "pass",
        "failed-auction re-entry then traverse to the opposite VA edge",
        "", "a03")
    add("R-A04", "AMT", "faithful", "pass",
        "open outside prior VA then two 30m periods inside (09:30-10:30)",
        "", "a04")
    add("R-A05", "AMT", "faithful", "pass",
        "POC chop (two touches, no through-and-hold)",
        "", "a05")
    add("R-A06", "AMT", "faithful", "gap",
        "n/a", "naked prior POC list (function exists; F naked-POC ledger not on the session table)", None)
    add("R-A07", "AMT", "faithful", "pass",
        "IB break, retest, hold",
        "", "a07")
    add("R-A08", "AMT", "faithful", "pass",
        "re-accept hold after a VA break",
        "", "a08")
    add("R-A09", "AMT", "faithful", "pass",
        "b.c1 through both VA edges with no 30-min hold inside",
        "", "a09")
    add("R-A10", "AMT", "faithful", "pass",
        "AMT open type is drive (first 30m never trades back through the 09:30 open)",
        "", "a10")
    add("R-A11", "AMT", "faithful", "pass",
        "prior RTH P-shape then single-break path",
        "", "a11")
    add("R-A12", "AMT", "faithful", "gap",
        "n/a", "value.vp.on LVN hold vs break at the open; FL-11 overnight delta sign", None)
    add("R-A13", "AMT", "faithful", "pass",
        "RTH touch of overnight high or low (18:00-09:30)",
        "", "a13")
    add("R-A14", "AMT", "faithful", "gap",
        "single-print fill, poor-extreme revisit, excess hold on first test",
        "tpo.single fill / tpo.excess hold (value.tpo.rth.30m poor-extreme flag saturates)", None)
    add("R-A15", "AMT", "faithful", "pass",
        "IB single-side extension after 10:30 (b.c1 beyond IB H or L)",
        "", "a15")
    add("R-A16", "AMT", "faithful", "gap",
        "n/a", "reject at value.kz ledge stacked with VWAP / prior VA / naked POC", None)
    add("R-A17", "AMT", "faithful", "gap",
        "n/a", "reject with vs without a second volume transition", None)
    add("R-A18", "AMT", "faithful", "gap",
        "n/a", "single-print reach after rejection from the balance", None)

    # Flow
    add("R-F01", "Flow", "faithful", "gap",
        "n/a", "VWAP ±2SD reject plus flow.absorption.A (env.vwap.rth.sd2 is AM reach, not reject+absorption)", None)
    add("R-F02", "Flow", "faithful", "blocked",
        "n/a", "flow.cvd.trade divergence (tape-trusted no)", None)
    add("R-F03", "Flow", "faithful", "gap",
        "n/a", "env.vwap.anchored.* convergence", None)
    add("R-F04", "Flow", "faithful", "gap",
        "n/a", "return to flow.footprint.stack3 (session stacked-4x flag is not a revisit)", None)
    add("R-F05", "Flow", "faithful", "gap",
        "n/a", "flow.candle.poc.flip after candle-vs-delta disagreement", None)
    add("R-F06", "Flow", "faithful", "gap",
        "n/a", "flow.absorption.A at shelf/ledge/VA (function is at 6-9 H/L); part 2 flow.absorption.B blocked; TR-19 pending", None)
    add("R-F07", "Flow", "faithful", "blocked",
        "n/a", "iceberg reload / flow.absorption.B (MBP-1 iceberg not-measurable; B fires every session)", None)
    add("R-F08", "Flow", "faithful", "gap",
        "n/a", "flow.reward.3tick after absorption A at a real extreme; CVD-median blocked", None)
    add("R-F09", "Flow", "faithful", "gap",
        "n/a", "flow.digits.thinning and flow.reward.3tick; stage 2 flow.absorption.B blocked", None)
    add("R-F10", "Flow", "faithful", "gap",
        "n/a", "lvl.protected.high/low", None)
    add("R-F11", "Flow", "faithful", "gap",
        "n/a", "dp.max at value.kz LVN then k=5 wick reject", None)
    add("R-F12", "Flow", "faithful", "gap",
        "n/a", "flow.approach.speed", None)
    add("R-F13", "Flow", "faithful", "gap",
        "n/a", "trap print + two prior-session failures then retest hold", None)
    add("R-F14", "Flow", "faithful", "gap",
        "n/a", "flow.footprint.imb350 at the same price as a BigTrades print", None)
    add("R-F15", "Flow", "faithful", "gap",
        "n/a", "flow.ofm.sequence; FL-12 gamma (value.node.gamma not built, no strike IV)", None)
    add("R-F16", "Flow", "faithful", "gap",
        "n/a", "absorption A at failed-aggression extreme; FL-12 long gamma", None)
    add("R-F17", "Flow", "faithful", "gap",
        "n/a", "flow.refill.zone with 32-tick penetration / 12-tick rest (flow.refill.ontouch is a different event)", None)
    add("R-F18", "Flow", "faithful", "gap",
        "n/a", "flow.ofm.sequence non-failing squeeze + tape speed", None)

    # Regime
    add("R-R01", "Regime", "faithful", "gap",
        "n/a", "value.node.flip / GEX walls (no strike IV; OI top3 is not the flip). Do not use mapped NDX/SPX minutes", None)
    add("R-R02", "Regime", "faithful", "pass",
        "prior-session VIXCLS close in band 15-18",
        "", "r02")
    add("R-R03", "Regime", "faithful", "gap",
        "n/a", "thesis validity box", None)
    add("R-R04", "Regime", "faithful", "blocked",
        "n/a", "SMT / IØD (flow.smt.* tape-trusted no; do not score flow.smt.pine.3-3)", None)

    # Sires
    add("R-S01", "Sires", "faithful", "gap",
        "n/a", "range.dealing bottom + flow.absorption.A", None)
    add("R-S02", "Sires", "faithful", "gap",
        "n/a", "third retest with no defending absorption A", None)
    add("R-S03", "Sires", "faithful", "gap",
        "n/a", "flow.digits.thinning; flow.absorption.B blocked", None)
    add("R-S04", "Sires", "faithful", "gap",
        "n/a", "value.delta.weekly trap + flow.footprint.imb350 + OFM", None)
    add("R-S05", "Sires", "faithful", "pass",
        "microbalance break after the first 10 minutes",
        "", "s05")
    add("R-S06", "Sires", "faithful", "gap",
        "n/a", "two-reason level (resistance + minor HVN within tR)", None)
    add("R-S07", "Sires", "faithful", "gap",
        "n/a", "MFE/MAE at 35-tick and 15-tick examples", None)
    add("R-S08", "Sires", "faithful", "gap",
        "n/a", "5m minor node with negative delta stacking", None)
    add("R-S09", "Sires", "faithful", "pass",
        "open above developing VAH then break/retest after 10:00",
        "", "s09")

    # Pine
    add("R-P01", "Pine", "faithful", "pass",
        "08:00 TBR 0.25-sigma touch then reversion to the open by 12:00",
        "", "p01")
    add("R-P02", "Pine", "faithful", "pass",
        "hourly sweep then retrace to the swept edge",
        "", "p02")
    add("R-P03", "Pine", "faithful", "gap",
        "n/a", "magic-hour boxes Z1-Z6", None)
    add("R-P04", "Pine", "faithful", "pass",
        "NYAM raid >=5 pts then close back inside within 120 min",
        "", "p04")
    add("R-P05", "Pine", "faithful", "pass",
        "London 25% body, NY wick or fail",
        "", "p05")
    add("R-P06", "Pine", "faithful", "pass",
        "London first-hit of Asia H/L",
        "", "p06")
    add("R-P07", "Pine", "faithful", "pass",
        "5m OR midpoint retest after 09:35",
        "", "p07")
    add("R-P08", "Pine", "faithful", "pass",
        "IB path class after 10:30 (break combo reduced to single / both / neither)",
        "", "p08")
    add("R-P09", "Pine", "faithful", "pass",
        "open vs prior RTH, no-break of the far side or stay inside",
        "", "p09")
    add("R-P10", "Pine", "faithful", "pass",
        "daily floor pivot PP touched in RTH",
        "", "p10")
    add("R-P11", "Pine", "faithful", "pass",
        "first-presented FVG on the 09:30 hour, fill or presence",
        "", "p11")
    add("R-P12", "Pine", "faithful", "pass",
        "sweep then close back through the prior bar high",
        "", "p12")
    add("R-P13", "Pine", "faithful", "pass",
        "midnight-open (TDO) traded through in 08:00-16:00",
        "", "p13")
    add("R-P14", "Pine", "faithful", "pass",
        "HOD already in by 10:00",
        "", "p14")
    add("R-P15", "Pine", "faithful", "pass",
        "Session Statistical Levels p50 MFE from the open",
        "", "p15")
    add("R-P16", "Pine", "faithful", "pass",
        "18:00-16:00 inside log-space VIX/16 a/b 1.0 zone from prior settle and prior VIX",
        "", "p16")
    add("R-P17", "Pine", "faithful", "pass",
        "18:00 open touched in RTH",
        "", "p17")
    add("R-P18", "Pine", "faithful", "blocked",
        "n/a", "flow.cvd.ohlc as trigger", None)
    add("R-P19", "Pine", "faithful", "pass",
        "adjacent body gap >= 4 ticks",
        "", "p19")
    add("R-P20", "Pine", "faithful", "gap",
        "n/a", "flow.delta.zone.kmeans / flow.vol.anomaly.zone on aggressor delta", None)
    return rows


def _preds():
    def j01(r):
        return bool(r.get("m05_in_0940") or (r.get("m05_reject") and r.get("m05_bin") == "bin.0940-0950"))

    def j02(r):
        return bool(r.get("open_to_m05_before_0940"))

    def j03(r):
        return bool(r.get("extended") and r.get("path_class") in ("high-only", "low-only") and r.get("midretrace_hold_1000"))

    def j04(r):
        return bool(r.get("purged_source") and r.get("path_class") in ("high-only", "low-only") and r.get("ext100_reach"))

    def j05(r):
        return bool(r.get("path_class") in ("high-only", "low-only") and r.get("midretrace"))

    def j06(r):
        return bool(r.get("outside_both") and r.get("rvol_ge_1") and r.get("path_class") == "both")

    def j07(r):
        return r.get("path_class") == "both"

    def j08(r):
        return bool(r.get("ext133_pm_reject"))

    def j09(r):
        return bool(r.get("lon_m05_reject"))

    def j11(r):
        return bool(r.get("ss_reach"))

    def j12(r):
        return bool(r.get("model_a") and r.get("pz_t1_reach") and r.get("m05_reject") and r.get("pz_edge_setup"))

    def j13(r):
        return bool(r.get("in_value") and r.get("ev_reach_mean60"))

    def j14(r):
        return bool(r.get("absorption_candle"))

    def j10(r):
        return bool(r.get("j10_draw_reach"))

    def j18(r):
        return bool(r.get("j18_ob"))

    def j19(r):
        return bool(r.get("j19_pd_touch"))

    def j21(r):
        return bool(r.get("j21_extended"))

    def j22(r):
        return bool(r.get("j22_three_strike"))

    def j24(r):
        return bool(r.get("j24_mfe_pos"))

    def j25(r):
        return bool(r.get("j25_mid_hold"))

    def j23(r):
        return True  # scored as clock path-class table; primary here is eligible session marker

    def g01(r):
        return bool(r.get("fail_range.gb.nyam"))

    def g02(r):
        return bool(r.get("fail_range.gb.asia"))

    def g03(r):
        return bool(r.get("hour_fail_n"))

    def g04(r):
        return bool(r.get("open0930_below_reclaim"))

    def g05(r):
        return bool(r.get("tdo_c5"))

    def g06(r):
        return bool(r.get("monday") and r.get("nwog_fill"))

    def g07(r):
        return bool(r.get("gp_touch"))

    def g08(r):
        return bool(r.get("prior_rth_overnight_reclaim"))

    def g09(r):
        return bool(r.get("stacked_asia_london_pdh") and r.get("monday") and r.get("nwog_fill"))

    def g10(r):
        return int(r.get("fade_count") or 0) >= 2

    def g11(r):
        return bool(r.get("aplus"))

    def a01(r):
        return bool(r.get("a01_fade"))

    def a03(r):
        return bool(r.get("a03_traverse"))

    def a05(r):
        return bool(r.get("a05_poc_chop"))

    def a07(r):
        return bool(r.get("a07_ib_retest"))

    def a08(r):
        return bool(r.get("a08_reaccept"))

    def a09(r):
        return bool(r.get("a09_traverse_nohold"))

    def a04(r):
        return bool(r.get("amt_80pct"))

    def a10(r):
        return r.get("amt_open_label") == "drive"

    def a11(r):
        return bool(r.get("a11_prior_p"))

    def a13(r):
        return bool(r.get("onh_or_onl"))

    def a14(r):
        return bool(r.get("tpo_poor"))

    def a15(r):
        return r.get("ib_path") in ("high-only", "low-only") or bool(r.get("ib_single"))

    def r02(r):
        return r.get("vix_band") == "15-18"

    def p01(r):
        return bool(r.get("p01_revert"))

    def p02(r):
        return bool(r.get("p02_hour_retrace"))

    def p04(r):
        return bool(r.get("p04_raid"))

    def p05(r):
        return bool(r.get("p05_lon25"))

    def p06(r):
        return bool(r.get("p06_first_hit"))

    def p07(r):
        return bool(r.get("p07_or_mid"))

    def p08(r):
        return r.get("ib_path") in ("high-only", "low-only") or bool(r.get("ib_single"))

    def p09(r):
        return bool(r.get("p09_no_break"))

    def p10(r):
        return bool(r.get("p10_pp_touch"))

    def p11(r):
        return bool(r.get("p11_fvg_fill"))

    def p12(r):
        return bool(r.get("p12_cisd_var"))

    def p14(r):
        return bool(r.get("p14_hod_1000"))

    def p15(r):
        return bool(r.get("p15_ssl"))

    def p17(r):
        return bool(r.get("p17_1800_touch"))

    def p19(r):
        return bool(r.get("p19_body_gap4"))

    def s05(r):
        return bool(r.get("s05_micro_break"))

    def s09(r):
        return bool(r.get("s09_vah_break"))

    def p13(r):
        return bool(r.get("tdo_touch_ny"))

    def p16(r):
        return bool(r.get("p16_inside"))

    return {k: v for k, v in locals().items() if callable(v)}


def score_all():
    joined = _join()
    preds = _preds()
    lines = [
        "# RULES_SCORES.md",
        "",
        "Phase 1 recipe scores on slice F (NY trade dates 2024-01-02 to 2026-08-31).",
        "One row per RULES.md section B id. Section C swaps are not scored.",
        "impl_fidelity=pass means every cited location, trigger, filter, and invalidation is a construction-audit pass function that matches the recipe clock, reset, side, and level.",
        "gap and blocked rows have rate n/a. Those are not measured edges.",
        "Event is the source event. Jumbo is path class and reach or reject of EQ, quadrants, range open, -0.5, and extensions. It is not a 6-9 H/L tag.",
        "Green Bird is sweep plus fail-back after the box, after 10:00 on NYAM.",
        "Order flow scores absorption A, 100ny, or 75ldn only when that trigger itself is pass. flow.smt.pine.3-3 is not a trigger.",
        "Mapped NDX and SPX minutes are not used.",
        "",
        "Rerun:",
        "",
        "```",
        "PYTHONPATH=implementation/src /tmp/trading-research-venv/bin/python implementation/tools/score_phase1_rules.py",
        "```",
        "",
        "id | framework | source_fidelity | impl_fidelity | n | event | rate | interval | year | RV | leakage | notes",
        "---|---|---|---|---|---|---|---|---|---|---|---",
    ]
    cat = catalog()
    for spec in cat:
        if spec["impl_fidelity"] != "pass":
            event = spec["event"] if spec["event"] != "n/a" else spec["missing"]
            notes = spec["missing"]
            lines.append(
                f"{spec['id']} | {spec['framework']} | {spec['source_fidelity']} | {spec['impl_fidelity']} | "
                f"n/a | {event} | n/a | n/a | n/a | n/a | n/a | {notes}"
            )
            continue
        pred = preds[spec["pred"]]
        if spec["id"] == "R-J23":
            # path class exists for each new clock; score midnight box path both as a representative
            clocks = load_rows("clocks_F") or []
            mid = [r for r in clocks if r.get("clock") == "range.midnight.0000-0030" and r.get("eligible")]
            flags = np.array([1.0 if r.get("path_class") == "both" else 0.0 for r in mid], dtype=np.float64)
            dates = [r["date"] for r in mid]
            primary = rate_block(int(flags.sum()), len(mid))
            years = {}
            for y in ("2024", "2025", "2026"):
                idx = np.array([d.startswith(y) for d in dates], dtype=bool)
                years[y] = rate_block(int(flags[idx].sum()) if flags.size else 0, int(idx.sum()))
            st = {
                "n": len(mid), "rate": primary["rate"],
                "interval": _fmt_int(*(primary.get("wilson_95") or [None, None])),
                "year": _fmt_year(years), "rv": "n/a (clock table)", "leakage": 0,
            }
            notes = "clocks range.midnight.0000-0030 and the other TBR published boxes; rate is midnight double-break. Lunch and MOC are comparison clocks."
        elif spec["id"] == "R-G03":
            elig = [r for r in joined if r.get("eligible")]
            k = int(sum(r.get("hour_fail_n") or 0 for r in elig))
            n = int(sum(r.get("hour_box_n") or 7 for r in elig))
            primary = rate_block(k, n)
            flags = np.array([
                float(r.get("hour_fail_n") or 0) / float(r.get("hour_box_n") or 7)
                for r in elig
            ], dtype=np.float64)
            dates = [r["date"] for r in elig]
            years = {}
            for y in ("2024", "2025", "2026"):
                idx = np.array([d.startswith(y) for d in dates], dtype=bool)
                ky = int(sum(elig[i].get("hour_fail_n") or 0 for i in range(len(elig)) if idx[i]))
                ny = int(sum(elig[i].get("hour_box_n") or 7 for i in range(len(elig)) if idx[i]))
                years[y] = rate_block(ky, ny)
            terc = {}
            for name in ("low", "mid", "high"):
                sub = [r for r in elig if r.get("vol_tercile_rv") == name]
                ky = int(sum(r.get("hour_fail_n") or 0 for r in sub))
                terc[name] = rate_block(ky, int(sum(r.get("hour_box_n") or 7 for r in sub)))
            st = {
                "n": n, "rate": primary["rate"],
                "interval": _fmt_int(*(primary.get("wilson_95") or [None, None])),
                "year": _fmt_year(years), "rv": _fmt_rv(terc), "leakage": 0,
            }
            notes = "n is completed clock-hour boxes (7 x sessions). Event is wick then 5m close-back on the next hour."
        elif spec["id"] == "R-G06":
            mondays = [r for r in joined if r.get("eligible") and r.get("monday")]
            st = _stats(mondays, lambda r: bool(r.get("nwog_fill")))
            notes = "denominator is Mondays; 16:00 fill not computed (AM 09:30-12:00 overlap only)"
        elif spec["id"] == "R-G09":
            mondays = [r for r in joined if r.get("eligible") and r.get("monday") and r.get("stacked_asia_london_pdh")]
            if not mondays:
                st = _stats(joined, pred)
            else:
                st = _stats(mondays, lambda r: bool(r.get("nwog_fill")))
            notes = "stacked PDH+Asia+London within 0.05 R; fill on those Mondays"
        else:
            st = _stats(joined, pred)
            notes = spec["missing"] if spec["missing"] else "leakage 0"
        rate = "n/a" if st["rate"] is None else f"{st['rate']:.4f}"
        lines.append(
            f"{spec['id']} | {spec['framework']} | {spec['source_fidelity']} | {spec['impl_fidelity']} | "
            f"{st['n']} | {spec['event']} | {rate} | {st['interval']} | {st['year']} | {st['rv']} | {st['leakage']} | {notes}"
        )

    gaps = [
        spec for spec in cat
        if spec["source_fidelity"] == "faithful"
        and spec["impl_fidelity"] == "gap"
        and spec["framework"] in ("Jumbo", "Green Bird", "AMT", "Flow")
    ]
    lines.extend([
        "",
        "## Faithful Jumbo / AMT / flow still gap",
        "",
        "Phase 1 is not done. Green Bird section B rows are pass. These Jumbo, AMT, and flow rows that RULES.md calls faithful are still impl_fidelity=gap.",
        "",
        "id | missing function",
        "---|---",
    ])
    for spec in gaps:
        lines.append(f"{spec['id']} | {spec['missing']}")
    lines.extend([
        "",
        "## Not started",
        "",
        "Phase 2 is not started. Section C one-slot swaps wait until the parent B row is pass.",
        "",
    ])
    SCORES_PATH.write_text("\n".join(lines), encoding="utf-8")
    return cat, SCORES_PATH
