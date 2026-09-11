"""Draw the audited implementation, without rebuilding tables or adding recipes.

The code-result labels are observations of recipe_score, not source validation.
Geometry comes from retained production tables and production helper calls.
Unimplemented source objects are described in the audit, never invented here.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import inspect
import json
import math
import sys
import textwrap
from datetime import date, time, timedelta
from functools import lru_cache
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
import numpy as np
import pyarrow.parquet as pq

from trading_research.research.phase1_live import TICK
from trading_research.research.phase1_live import formulas as fm
from trading_research.research.phase1_live import formulas_flow as ff
from trading_research.research.phase1_live import formulas_jumbo as fj
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds, wall_ns
from trading_research.research.phase1_live.compute import load_rows
from trading_research.research.phase1_live.family_tape import _bins, _trades
from trading_research.research.phase1_live.mbp1_extract import list_complete_chunks
from trading_research.research.phase1_live.ohlc_index import OHLC1M, SISTERS_1M, load_years
from trading_research.research.phase1_live.sessions import projections
from trading_research.research.phase1_live.grid import outcomes_at_level

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "implementation/reports/phase1-live/chart-audit"
PLOTS = OUT / "plots"
SCORES = json.loads((OUT / "score_snapshot.json").read_text())
JOIN = {r["date"]: r for r in json.loads((OUT / "joined_snapshot.json").read_text())}
FRESH_JOIN = {r["date"]: r for r in json.loads((OUT / "fresh_assembly_selected_tape.json").read_text())} if (OUT / "fresh_assembly_selected_tape.json").exists() else {}
TABLES = {n: {r["date"]: r for r in load_rows(n)} for n in
          ("sessions_F", "open_switch_F", "env_F", "prior_rth_trade_vp_F", "weekly_delta_F", "gex_qqq_F")}
DATES = sorted(TABLES["sessions_F"])
PREV = {d: DATES[i - 1] if i else None for i, d in enumerate(DATES)}
CHUNKS = list_complete_chunks()
COLORS = ["#285fa8", "#be4b33", "#007d73", "#8453a4", "#ad7400", "#5e7c22"]


def serial(v):
    if isinstance(v, np.generic): return v.item()
    if isinstance(v, np.ndarray): return v.tolist()
    if isinstance(v, Path): return str(v)
    raise TypeError(type(v).__name__)


@lru_cache(maxsize=4)
def bars(root=str(OHLC1M)):
    return load_years(Path(root), [2023, 2024, 2025, 2026])


def ns(d, hour):
    offset = math.floor(hour / 24)
    m = round((hour - offset * 24) * 60)
    return wall_ns(d, time((m // 60) % 24, m % 60), offset)


def window(d, a, b, root=str(OHLC1M)):
    return bars(root).window(ns(d, a) // 1_000_000, ns(d, b) // 1_000_000)


def xhours(t, d, unit=1_000_000):
    return (np.asarray(t, dtype=np.float64) * unit - ns(d, 0)) / 3_600_000_000_000


@lru_cache(maxsize=1)
def absorption_observer():
    """Return the original scan's successful indices without changing its decisions."""
    from numba import njit
    from trading_research.research.phase1_live.mbp1_objects import _absorption_a_scan
    source=inspect.getsource(_absorption_a_scan.py_func)
    tree=ast.parse(source);fn=tree.body[0];fn.decorator_list=[]
    class Observe(ast.NodeTransformer):
        def visit_Return(self,node):
            if isinstance(node.value,ast.Constant) and isinstance(node.value.value,bool):
                expr='(i,k,pmax,pmin,1 if toward_high else -1)' if node.value.value else '(-1,-1,0.0,0.0,0)'
                node.value=ast.parse(expr,mode='eval').body
            return node
    tree=Observe().visit(tree);ast.fix_missing_locations(tree);scope={}
    exec(compile(tree,'<audit original absorption scan>','exec'),scope)
    return njit(cache=False)(scope[fn.name]),hashlib.sha256(source.encode()).hexdigest()


@lru_cache(maxsize=3)
def tape(iso):
    # Match the production last-chunk-wins choice; never concatenate overlaps.
    candidates = [p for p in CHUNKS if p.name[:10] <= iso <= p.name[11:21]]
    result = None
    for p in candidates:
        tab = pq.read_table(p, filters=[("session", "=", iso)])
        if tab.num_rows:
            result = {k: tab[k].to_numpy() for k in tab.column_names if k != "session"}
            result["source_path"] = str(p)
    return result


def candidates():
    preferred = ["2026-07-10", "2026-01-28", "2025-10-08", "2025-01-10", "2026-01-02", "2026-08-11", "2026-07-09"]
    available = {iso for iso in DATES if window(date.fromisoformat(iso),9.5,16)["n"] >= 360
                 and PREV.get(iso) and window(date.fromisoformat(PREV[iso]),9.5,16)["n"] >= 360}
    specs = []
    for s in SCORES:
        pos, neg = s["positive_dates"], s["negative_dates"]
        def pick(arr):
            valid=[d for d in arr if d in available]
            return next((d for d in preferred if d in valid),valid[-1] if valid else arr[-1] if arr else None)
        a, b = pick(pos), pick(neg)
        if a is None:
            a = "2026-07-10"
            if s["id"] in ("R-J03", "R-J25"):
                pool = [r["date"] for r in TABLES["sessions_F"].values()
                        if r.get("eligible") and r.get("path_class") in ("high-only", "low-only")
                        and r.get("midretrace") and (s["id"] != "R-J03" or r.get("extended"))]
                a = pick(pool) or a
        if b is None or b == a:
            b = next(d for d in preferred if d != a)
        for role, iso in [("A", a), ("B", b)]:
            specs.append({"id": s["id"], "case": role, "date": iso,
                          "code_result": True if iso in pos else False if iso in neg else None,
                          "selection": "code-positive" if role == "A" and pos else "code-negative" if role == "B" and neg else "available-data diagnostic",
                          "positive_count": len(pos), "negative_count": len(neg)})
    return specs


class Drawing:
    def __init__(self, spec):
        self.spec = spec
        self.id, self.iso = spec["id"], spec["date"]
        self.d = date.fromisoformat(self.iso)
        self.r = TABLES["sessions_F"].get(self.iso, {})
        self.op = TABLES["open_switch_F"].get(self.iso, {})
        self.env = TABLES["env_F"].get(self.iso, {})
        self.join = JOIN.get(self.iso, {})
        self.prev = date.fromisoformat(PREV[self.iso]) if PREV.get(self.iso) else None
        self.lines, self.boxes, self.curves, self.marks, self.notes = [], [], [], [], []
        self.trace = {"case": spec, "production_session": self.r, "geometry": [], "helpers": {}, "sources": []}
        self.root = str(OHLC1M)
        self.a, self.b = 9.25, 12
        self.profile = None
        self.feature = "volume"
        self.focus_start = None
        self.levels = projections(self.r["H"], self.r["L"]) if self.r.get("H") and self.r.get("L") else {}

    def line(self, label, p, a=None, b=None, color=None, style="--"):
        if p is None or not np.isfinite(p): return
        a, b = self.a if a is None else a, self.b if b is None else b
        color = color or COLORS[len(self.lines) % len(COLORS)]
        item = dict(kind="line", label=label, price=float(p), start=a, end=b, color=color, style=style)
        self.lines.append(item); self.trace["geometry"].append(item)

    def band(self, label, lo, hi, a, b, color=None):
        if lo is None or hi is None: return
        item = dict(kind="box", label=label, low=float(lo), high=float(hi), start=a, end=b,
                    color=color or COLORS[len(self.boxes) % len(COLORS)])
        self.boxes.append(item); self.trace["geometry"].append(item)

    def clock(self, cid, inner=True, extend=True):
        cb = clock_bounds(self.d, CLOCKS[cid]); w = bars().window(cb["start_ms"], cb["end_ms"])
        a, b = xhours([cb["start_ms"], cb["end_ms"]], self.d)
        end = float(xhours([cb["outcome_end_ms"]], self.d)[0]) if extend else b
        tag = cid.removeprefix("range.")
        self.band(tag + " formation", w["low"], w["high"], a, b)
        if w["n"]:
            for name, px in [("H", w["high"]), ("L", w["low"])]: self.line(tag + " " + name, px, b, end)
            if inner: self.line(tag + " EQ", (w["high"] + w["low"]) / 2, b, end)
        self.trace["helpers"][cid] = {k: w[k] for k in ("n", "missing", "open", "high", "low", "close")}
        return w, a, b

    def prior_value(self):
        self.b = max(self.b, 12)
        pv = TABLES["prior_rth_trade_vp_F"].get(PREV.get(self.iso), {})
        self.line("prior trade VAL", self.op.get("VAL"), color=COLORS[0])
        self.line("prior trade VAH", self.op.get("VAH"), color=COLORS[0])
        self.line("prior trade POC", pv.get("poc"), color=COLORS[2])
        self.line("09:30 open", self.r.get("open_0930"), color="#656565", style=":")
        self.trace["helpers"]["prior_profile_date"] = PREV.get(self.iso)

    def jumbo(self):
        n = int(self.id[-2:]); self.a = 6; self.b = 16 if n == 8 else 12
        self.clock("range.6-9.published", inner=False)
        if n in (3, 4, 5, 6, 7, 10, 12, 14, 15, 16, 17, 19, 21, 25):
            for k in ("EQ", "Q25", "Q75"): self.line(k, self.r.get(k), 9, self.b)
            self.line("06:00 open", self.r.get("open"), 9, self.b)
        if n in (1,2,4,8,10,12,14,15,17,18,20,22,24):
            for k, p in self.levels.items():
                prefixes = ("mr","m05") if n in (1,2) else ("ext100",) if n==4 else ("ext133","ext166") if n==8 else ("m05",)
                if k.startswith(prefixes):
                    self.line(k, p, 9, self.b)
            self.notes.append("Projection labels are the production dictionary keys; no missing ±2 levels added.")
        if n in (1, 2, 20, 24):
            self.band("09:40–09:50 clock gate", self.r.get("L"), self.r.get("H"), 9 + 40/60, 9 + 50/60, "#bf921e")
        if n in (4, 6, 10, 19, 21):
            for k in ("asia_high", "asia_low", "london_high", "london_low", "prior_rth_high", "prior_rth_low"):
                self.line(k, self.r.get(k), 9, self.b, style=":")
        if n==6:
            self.line("09:30 open", self.r.get("open_0930"), 9.5, 12, color="#000000")
            for k in ("VAL","VAH"): self.line("prior "+k,self.op.get(k),9.5,12)
            self.trace["helpers"]["open_context"]={k:self.op.get(k) for k in ("open_cell","rvol_0930","rvol_ge_1","outside_both")}
        if n == 8:
            # Match family_levels.build_level_table's actual PM cutoff.
            pm = window(self.d, 13, 16)
            self.trace['helpers']['PM_window_NY'] = [13, 16]
            for side, color in (('high', '#9368bd'), ('low', '#159d9b')):
                self.band('implemented 1.33–1.66 '+side,
                          min(self.levels['band133_166_'+side+'_near'], self.levels['band133_166_'+side+'_far']),
                          max(self.levels['band133_166_'+side+'_near'], self.levels['band133_166_'+side+'_far']),
                          9, 16, color)
            events = {k: outcomes_at_level(pm, self.levels[k], width=self.r["W69"], side=side)
                      for k, side in (("ext133_high", 1), ("ext133_low", -1), ("ext166_high", 1), ("ext166_low", -1))}
            self.trace["helpers"]["PM_level_events"] = events
            hits = [(q["touch_ms"], k) for k, q in events.items() if q["touch_ms"]]
            if hits:
                tm, key = min(hits); self.focus_start = float(xhours([tm], self.d)[0])
                self.marks.append((self.focus_start, self.levels[key], "first PM touch", "#000000"))
            else: self.focus_start = 13
        if n == 9:
            self.lines.clear(); self.boxes.clear(); self.trace["geometry"].clear(); self.a, self.b = 0, 6
            w, _, end = self.clock("range.london.00-03")
            if w["n"]:
                for k,p in projections(w["high"],w["low"]).items():
                    if k.startswith(("m05", "ext")): self.line(k,p,end,6)
            self.notes.append("Code freezes at action start 03:00 NY. Source-display projections 02:00 precede action marker 03:00; axis zone unresolved.")
            self.focus_start = 3.25
        if n in (11, 12, 13):
            prefix = {11:"ss", 12:"pz", 13:"ev"}[n]
            if n != 12:
                self.lines.clear(); self.boxes.clear(); self.trace["geometry"].clear(); self.a = 8.75 if n == 11 else 9.25
            for k,v in self.env.items():
                if k.startswith(prefix) and isinstance(v, (int,float)) and not isinstance(v,bool) and k not in ("pz_history",):
                    if k.endswith(("hi","lo","mid","hi_median","lo_median","mid_median")):
                        self.line(k,v,9 if n==11 else 9.5,self.b)
            self.notes.append("Retained envelope approximation. Unpublished author algorithm remains unverified.")
            if n == 12:
                self.band("code upper T1 p50–p75", self.env.get("pz_hi"), self.env.get("pz_t1_hi"), 9.5, self.b)
                self.band("code lower T1 p75–p50", self.env.get("pz_t1_lo"), self.env.get("pz_lo"), 9.5, self.b)
        if n in (15,16,17): self.feature = "tapeJ15" if n==15 else "profile69" if n==17 else "profileRTH"
        if n == 16:
            self.feature = "footprint"
            self.band("code EQ ±2 ticks", self.r["EQ"]-2*TICK, self.r["EQ"]+2*TICK, 9.5, 12)
        if n == 17:
            ev = tape(self.iso)
            if ev is not None:
                _,p,v,s = _trades(ev, ns(self.d,6), ns(self.d,9))
                packed = _bins(p,v,s)
                if packed is not None:
                    low_tick,vol,_,_ = packed
                    nodes = fj.profile_nodes({(low_tick+i)*TICK:float(x) for i,x in enumerate(vol) if x>0})
                    self.trace["helpers"]["code_profile_nodes"] = nodes
                    displayed=set(); matched={}
                    for kind in ("lvn", "shelf_edges"):
                        matched[kind]=[px for px in nodes[kind] if any(abs(px-ref)<=.05*self.r["W69"] for ref in (self.r["EQ"],self.levels["m05_low"],self.levels["m05_high"]))]
                        for ref in (self.r["EQ"],self.levels["m05_low"],self.levels["m05_high"]):
                            near=[px for px in matched[kind] if abs(px-ref)<=.05*self.r["W69"]]
                            if near:
                                px=min(near,key=lambda x:(abs(x-ref),x))
                                if (kind,px) not in displayed:self.line("nearest code " + kind,px,9,12,style=":");displayed.add((kind,px))
                    self.trace['helpers']['matched_profile_nodes']=matched
                    self.notes.append('Price labels show the nearest matching node per reference/type. Every matching node is marked on the VP panel; all exact prices are in the JSON trace.')
        if n == 14: self.feature = "absorption3m"
        if n == 18:
            am=window(self.d,9.5,12); b3=fm.resample_ohlcv(am,3)
            for i in range(2,b3["n"]):
                cs=[{k:float(b3[k][j]) for k in ("h","l","c")} for j in (i-2,i-1,i)]
                up=fj.j18_ob_bull(*cs,self.levels["m05_low"]);dn=fj.j18_ob_bear(*cs,self.levels["m05_high"])
                if up["ob_bull"] or dn["ob_bear"]:
                    t=float(xhours([b3["t"][i]],self.d)[0])+3/60
                    self.band("first code OB; C2 H/L",cs[1]["l"],cs[1]["h"],t,12,"#bf921e")
                    self.line("C2 high",cs[1]["h"],t,12);self.line("C2 low",cs[1]["l"],t,12)
                    self.focus_start=t-.15
                    self.trace["helpers"]["first_OB"]={"known_clock":t,"bull":up,"bear":dn};break
        if n == 20:
            self.focus_start=10
            self.notes.append("10:00 calendar gate is retained; a touch timestamp is not a confirmed reversal timestamp.")
        if n == 23:
            self.lines.clear();self.boxes.clear();self.trace["geometry"].clear();self.a,self.b=-4,16
            for cid in ("range.asia.2000-2030","range.midnight.0000-0030","range.london.0300-0330","range.rth.0930-1000","range.rth.1000-1030","range.lunch.1200-1230","range.moc.1500-1530"): self.clock(cid,inner=True)
        if n == 25:
            am=window(self.d,9.5,12);sw=fj.j25_fractal_swings(am["h"],am["l"]);self.trace["helpers"]["swings"]=sw
            if sw["highs"] and sw["lows"]:
                hi,lo=sw["highs"][0]["px"],sw["lows"][0]["px"]
                self.line("first independent swing H",hi,9.5,12);self.line("first independent swing L",lo,9.5,12)
                self.line("code swing midpoint",(hi+lo)/2,9.5,12)
                self.notes.append("Midpoint back-applied to AM by production; source confirmation times are not enforced.")

    def greenbird(self):
        n=int(self.id[-2:]);self.a,self.b=(8.5,12)
        if n==1:self.clock("range.gb.nyam")
        elif n==2:self.a,self.b=-4,6;self.clock("range.gb.asia")
        elif n==3:
            self.a,self.b=8.5,17
            for h in range(9,16):
                w=window(self.d,h,h+1);self.band(f"{h:02d}:00 hour",w["low"],w["high"],h,h+1)
                for k in ("high","low"):self.line(f"{h:02d} {k}",w[k],h+1,min(h+2,17))
        elif n in (4,5):
            self.a=9.25 if n==4 else 8
            self.line("09:30 open" if n==4 else "TDO 00:00 open",self.r.get("open_0930") if n==4 else self.join.get("tdo"),9.5 if n==4 else self.a)
        elif n in (6,9):
            self.a,self.b=-6,12;friday=self.d-timedelta(days=3)
            a=window(self.d,-6,-6+1/60)["open"];b=window(friday,15+59/60,16)["close"]
            if self.d.weekday()==0:
                self.band("code NWOG: Friday 15:59 C → Sunday 18:00 O",min(a,b),max(a,b),-6,12)
                self.line("Friday 15:59 close",b,-6,12)
                self.line("Sunday 18:00 open",a,-6,12)
            else:self.notes.append("Not Monday: no NWOG event is eligible on this diagnostic date.")
            if n==9:
                for k in ("prior_rth_high","asia_high","london_high"):self.line(k,self.r.get(k),9,12)
        elif n==7:
            w,_,_=self.clock("range.gb.nyam");g=fm.gp_band_impulse(w["high"],w["low"],down=w["close"]<w["open"])
            if g:
                self.band("code GP (NYAM candle sign)",*g,10,12,"#bf921e")
                self.line("code GP lower",g[0],10,12);self.line("code GP upper",g[1],10,12)
                self.trace["helpers"]["code_gp_bounds"]=g
        elif n==8:
            self.a,self.b=-6,9.5
            for k in ("prior_rth_high","prior_rth_low"):self.line(k,self.r.get(k))
        elif n in (10,11):
            if n==11:self.a=-4;self.clock("range.gb.asia")
            self.clock("range.gb.nyam");self.clock("range.gb.10-11")
        self.notes.append("Compared with GB raw posts and figures. Axis is the implementation's New York clock; source snapshot offsets are audited separately. Extended lines show retained geometry, not proof that a previously visited high/low remains active.")
        self.focus_start = {1:10,2:0,3:10,7:10,10:11,11:10}.get(n)
        if n == 3 and self.spec['case'] == 'source-date':
            self.focus_start = 11
        if n==7:
            ow=window(self.d,10,12);g=self.trace["helpers"].get("code_gp_bounds")
            if g:
                hit=np.flatnonzero((ow["h"]>=g[0])&(ow["l"]<=g[1]))
                if len(hit):
                    i=int(hit[0]);x=float(xhours([ow["t"][i]],self.d)[0]);self.focus_start=x
                    self.marks.append((x,max(g[0],min(g[1],float(ow["c"][i]))),"first GP overlap","#000000"))
        if n in (1,2,10,11):
            cid="range.gb.asia" if n==2 else "range.gb.10-11" if n==10 else "range.gb.nyam"
            cb=clock_bounds(self.d,CLOCKS[cid]);bw=bars().window(cb["start_ms"],cb["end_ms"]);ow=bars().window(cb["outcome_start_ms"],cb["outcome_end_ms"])
            if bw["n"] and ow["n"]:
                hit=np.flatnonzero((ow["h"]>bw["high"])|(ow["l"]<bw["low"]))
                if len(hit):
                    i=int(hit[0]);ts=int(ow["t"][i]);x=float(xhours([ts],self.d)[0]);p=float(ow["h"][i] if ow["h"][i]>bw["high"] else ow["l"][i])
                    self.marks.append((x,p,"first code wick","#000000"));self.focus_start=x-.05
                    for j in range(0,ow["n"]-4,5):
                        tc=int(ow["t"][j]);cc=float(ow["c"][j+4])
                        if ts<=tc<=ts+30*60_000 and bw["low"]<cc<bw["high"]:
                            xc=float(xhours([tc],self.d)[0]);self.marks.append((xc+5/60,cc,"5m close known","#8453a4"))
                            self.trace["helpers"]["failback_time"]={"wick_bar_start_ms":ts,"code_5m_start_ms":tc,"actual_5m_close_ms":tc+300_000,"close":cc};break

    def auction(self):
        n=int(self.id[-2:]);self.a,self.b=9.25,16;self.prior_value();self.feature="profilePrior"
        if n in (7,15):self.clock("range.ib")
        if n==10:self.line("first 30-minute open-type reference",self.r.get("open_0930"),9.5,10)
        if n==11:self.feature="shapePrior"
        if n==12:
            self.a=-6;self.feature="profileON"
            ev=tape(self.iso)
            if ev is not None:
                _,px,sz,_=_trades(ev,ns(self.d,-6),ns(self.d,9.5));pack=_bins(px,sz)
                if pack is not None:
                    from trading_research.research.phase1_live.family_tape import _bin_dict
                    nodes=fj.profile_nodes(_bin_dict(pack[0],pack[1]));self.trace["helpers"]["overnight_nodes"]=nodes
                    for p in sorted(nodes["lvn"],key=lambda p:abs(p-self.r["open_0930"]))[:3]:self.line("code ON LVN",p,9.5,16)
        if n==13:
            self.lines.clear();self.trace["geometry"].clear();self.a=-6;self.clock("range.on.1800-0930")
            for line in self.lines:line["end"]=16
        if n==14:self.feature="tpoCode";self.notes.append("Current scorer is bool(tpo_poor) from today's full RTH; no next-session fill/hold event.")
        if n==16:
            self.feature="profilePrior";self.notes.append("Prior VAL is the code ledge; full-AM VWAP is known at noon. No source shelf is implemented.")
            ev=tape(self.iso)
            if ev is not None:
                _,px,sz,_=_trades(ev,ns(self.d,9.5),ns(self.d,12))
                if len(px):
                    vwap=float(np.average(px,weights=np.maximum(sz,1e-9)));self.line("code AM VWAP (known 12:00)",vwap,9.5,16,color="#c00040")
                    self.trace["helpers"]["a16_inputs"]={"ledge":self.op.get("VAL"),"vwap":vwap,"vah":self.op.get("VAH")}
        if n==17:
            self.feature="profileRTH";self.notes.append("Production second-transition test uses final RTH occupied bins, known at16:00; red line is its selected minimum.")
            ev=tape(self.iso)
            if ev is not None:
                _,px,sz,_=_trades(ev,ns(self.d,9.5),ns(self.d,16));pack=_bins(px,sz)
                if pack is not None:
                    lo,vol=pack[:2];occupied=np.flatnonzero(vol>0);res=fj.a17_second_transition([float(vol[i]) for i in occupied])
                    self.trace["helpers"]["a17_exact"]=res
                    if res["lvn_i"] is not None:
                        p=(lo+int(occupied[res["lvn_i"]]))*TICK;self.line("code minimum (known16:00)",p,9.5,16,color="#c00040")
                        self.trace["helpers"]["a17_exact"]["price"]=p
        if n==18:
            vals=[int(round((self.op[k]+(1 if k=="VAH" else -1))/TICK)) for k in ("VAH","VAL") if self.op.get(k) is not None]
            self.trace["helpers"]["fabricated_single_inputs"]=vals
            self.notes.append(f"Fresh code passes synthetic tick integers {vals} as single-print prices; both calls test bullish VAL rejection. No real singles ledger.")
        if n in (2,6,18):
            key={2:"a02_ledge_hold",6:"a06_naked_poc",18:"a18_single_reach"}[n]
            fresh=FRESH_JOIN.get(self.iso,{}).get(key)
            self.trace["helpers"]["fresh_assembled_flag"]={"key":key,"value":fresh}
            self.notes.append(f"Fresh assembled {key} = {fresh}; title retains the original scorer result.")
        if n in (3,8):
            rw=window(self.d,9.5,16);va,ha=self.op.get("VAL"),self.op.get("VAH")
            if va is not None and ha is not None and rw["n"]:
                hits=np.flatnonzero((rw["c"]>va)&(rw["c"]<ha))
                if len(hits):self.focus_start=float(xhours([rw["t"][int(hits[0])]],self.d)[0])
        if n in (7,15):self.focus_start=10.5

    def flow(self):
        n=int(self.id[-2:]);self.a,self.b=9.5,12;self.prior_value();self.feature="tape"
        if n in (1,3):
            self.a=-6 if n==1 else 9.25
            w=window(self.d,-6,12);vw,sd=ff.running_vwap(w["h"],w["l"],w["c"],w["v"]);xx=xhours(w["t"],self.d)
            prefix='CODE ETH HLC3 VWAP' if n==1 else 'unscored ETH helper VWAP'
            for k in (-2,0,2):self.curves.append((xx,vw+k*sd,f"{prefix} {k:+d}σ",COLORS[(k+2)//2]))
            self.notes.append("F01 scorer ORs ETH running-band touch with final-AM trade-band absorption; neither branch requires the full source sequence." if n==1 else "Curves are an unscored ETH helper comparison. F03 uses final-AM / overnight trade VWAP and prior VA midpoint.")
        if n in (4,5,11,14):self.feature="footprint" if n in (4,14) else "profileRTH"
        if n==10:
            w=window(self.d,9.5,12);self.line("final AM low + 2 ticks",w["low"]+2*TICK)
        if n in (13,15,16,18):
            for k in ("H","L"):self.line("6–9 "+k,self.r.get(k))
            self.line("prior RTH high",self.r.get("prior_rth_high"))
            self.notes.append("Wick/catalyst inputs use completed AM aggregates. Plot does not invent missing ordered stages.")
            diagnostic_path = OUT / "tape_locals.json"
            if diagnostic_path.exists() and n in (15,18):
                diag = json.loads(diagnostic_path.read_text()).get(self.iso, {})
                self.trace["helpers"]["fresh_ofm_inputs"] = diag
                for key in ("ofm_h", "ofm_l"):
                    cat = diag.get(key, {}).get("catalyst")
                    if cat:
                        self.band("code final-AM " + key + " catalyst", min(cat), max(cat), 9.5, 12)
                        self.line(key+" catalyst low", min(cat),9.5,12)
                        self.line(key+" catalyst high", max(cat),9.5,12)
                fresh = diag.get("out", {}).get("f15_ofm" if n == 15 else "f18_squeeze")
                self.notes.append(f"Fresh producer result = {fresh}; title retains the original scorer result.")
        if n in (2,7):self.notes.append("Scorer is blocked. Available tape is diagnostic only; no faithful trigger generated.")
        ev=tape(self.iso)
        if ev is None:return
        ta,pa,va,sa=_trades(ev,ns(self.d,9.5),ns(self.d,12))
        if not len(pa):return
        if n==1:
            vw=float(np.average(pa,weights=np.maximum(va,1e-9)));sd=float(np.sqrt(np.average((pa-vw)**2,weights=np.maximum(va,1e-9))))
            self.trace['helpers']['f01_final_am']={'vwap':vw,'sigma':sd,'lower':vw-2*sd,'upper':vw+2*sd}
            for k in (-2,0,2):self.line(f'CODE final-AM trade VWAP {k:+d}σ',vw+k*sd,9.5,12,color='#c00040')
        if n in (3,5,8,9,12):
            self.trace["helpers"]["am_aggregates"]={"first":float(pa[0]),"last":float(pa[-1]),"delta":float((va*sa).sum()),"first5_size_median":float(np.median(va[:5])),"last5_size_median":float(np.median(va[-5:])),"first20_size_median":float(np.median(va[:20])),"last20_size_median":float(np.median(va[-20:]))}
        if n==3:
            _,po,vo,_=_trades(ev,ns(self.d,-6),ns(self.d,9.5))
            amvw=float(np.average(pa,weights=np.maximum(va,1e-9)));onvw=float(np.average(po,weights=np.maximum(vo,1e-9))) if len(po) else amvw
            for label,p in [('code final AM VWAP (noon)',amvw),('code overnight VWAP',onvw),('code prior VA midpoint',(self.op['VAL']+self.op['VAH'])/2)]:self.line(label,p,9.5,12)
            self.trace['helpers']['f03_scalars']={'am_vwap':amvw,'on_vwap':onvw,'va_mid':(self.op['VAL']+self.op['VAH'])/2}
        if n==5:self.notes.append(f"Code treats AM as one candle: O={pa[0]:.2f}, C={pa[-1]:.2f}, signed delta={float((va*sa).sum()):.0f}; no source intrabar POC flip.")
        if n in (4,5,11,14):
            _,pr,vr,sr=_trades(ev,ns(self.d,9.5),ns(self.d,16));pack=_bins(pr,vr,sr)
            if pack is not None:
                lo,vol,buy,sell=pack;poc=(lo+int(np.argmax(vol)))*TICK
                self.line('code final RTH POC (16:00)',poc,9.5,12,color='#c00040')
                if n==4:
                    ask={(lo+i)*TICK:float(buy[i]) for i in range(len(buy)) if buy[i]>0};bid={(lo+i)*TICK:float(sell[i]) for i in range(len(sell)) if sell[i]>0}
                    st=ff.r_f04_candle_stack(ask,bid,k=4.0);self.trace['helpers']['f04_rth_stack']=st
                    if st.get('zone'):
                        self.band('code stack zone from full RTH',*st['zone'],9.5,12)
                        self.line('code RTH stack low',st['zone'][0],9.5,12)
                        self.line('code RTH stack high',st['zone'][1],9.5,12)
                if n==11:
                    from trading_research.research.phase1_live.family_tape import _bin_dict
                    nodes=fj.profile_nodes(_bin_dict(lo,vol));self.trace['helpers']['f11_rth_nodes']=nodes
                    for p in sorted(nodes['lvn'],key=lambda p:abs(p-poc))[:3]:self.line('code nearest LVN to POC',p,9.5,12)
        if n==6:
            from trading_research.research.phase1_live.mbp1_objects import _roll_aggressive,_absorption_a_scan
            from trading_research.research.phase1_live.threshold_grid import GRID_PATH
            grid=json.loads(GRID_PATH.read_text());br,sr=_roll_aggressive(ta,va,sa,120_000_000_000)
            args=(ta.astype(np.int64),pa.astype(float),br.astype(float),sr.astype(float),float(grid['abs_q90_buy']),float(grid['abs_q90_sell']),float(self.op['VAH']),float(self.op['VAL']),2*TICK,float(self.op['VAH']-self.op['VAL']),900_000_000_000,TICK)
            observer,sha=absorption_observer();i,k,pmax,pmin,side=observer(*args);raw=bool(_absorption_a_scan(*args));assert raw==(i>=0)
            self.trace['helpers']['f06_observed_scan']={'result':raw,'original_scan_sha256':sha,'i':i,'k':k,'side':side,'pmax':pmax,'pmin':pmin,'q_buy':grid['abs_q90_buy'],'q_sell':grid['abs_q90_sell']}
            if i>=0:
                x=float(xhours([ta[i]],self.d,1)[0]);self.focus_start=x;self.marks.append((x,float(pa[i]),'code qualifying print','#000000'))
                self.trace['helpers']['f06_observed_scan'].update(time_ns=int(ta[i]),price=float(pa[i]),buy_roll=float(br[i]),sell_roll=float(sr[i]))
            self.notes.append('Code rolling aggression sums all prices over two minutes; 15-minute future extrema establish its reversal flag.')
        if n==8:
            direction=1 if float(sa[:min(20,len(sa))].sum())>=0 else -1
            got=ff.reward_3tick(pa[-min(80,len(pa)):].tolist(),absorption_px=float(pa[0]),direction=direction)
            self.line('code reward origin = first AM trade',float(pa[0]),9.5,12)
            for p,label in [(float(pa[-80:].min()),'last80 minimum'),(float(pa[-80:].max()),'last80 maximum')]:self.marks.append((float(xhours([ta[-1]],self.d,1)[0]),p,label,'#c00040'))
            self.trace['helpers']['f08_exact']={**got,'direction':direction,'last80_start_ns':int(ta[-min(80,len(ta))]),'last_ns':int(ta[-1])}
        if n in (9,12):
            count=20 if n==9 else 5;self.notes.append(f"Actual first{count} / last{count} AM print-size medians = {np.median(va[:count]):g} / {np.median(va[-count:]):g}; no level-specific arrival/stage.")
        if n==10:
            self.marks.append((float(xhours([ta[-1]],self.d,1)[0]),float(pa[-5:].min()),'last5 print minimum','#c00040'))
            self.trace['helpers']['f10_exact']={'am_low':float(pa.min()),'last5_min':float(pa[-5:].min()),'last5_start_ns':int(ta[-5]),'last_ns':int(ta[-1])}
        if n==14:
            for key,p in [('EQ',self.r.get('EQ')),('m05 high',self.levels.get('m05_high')),('m05 low',self.levels.get('m05_low'))]:self.line('independent Jumbo BigTrades '+key,p,9,12)
            self.notes.append('350% uses full-RTH same-price volumes; BigTrades is an independent Jumbo-level flag, not matched to that imbalance.')
        if n==17:
            from trading_research.research.phase1_live.mbp1_objects import on_touch_refill
            cap={}
            def trace(frame,event,arg):
                if frame.f_code is on_touch_refill.__code__ and event=='return' and arg:
                    loc=frame.f_locals;ix=loc['i'];tt,pp=loc['t'],loc['px'];ret=np.flatnonzero((tt>loc['leave_t'])&(pp>=loc['lo'])&(pp<=loc['hi']))
                    cap.update(lo=loc['lo'],hi=loc['hi'],cluster_start_ns=int(loc['lt'][ix]),leave_ns=int(loc['leave_t']),return_ns=int(tt[int(ret[0])]),cluster_window=loc['window'].tolist(),first3_sides=loc['same'][:3].tolist())
                return trace
            sys.settrace(trace)
            try:raw=on_touch_refill(ev,ns(self.d,9.5),ns(self.d,12))
            finally:sys.settrace(None)
            self.trace['helpers']['f17_actual']={'result':raw,**cap}
            if raw:
                x=float(xhours([cap['cluster_start_ns']],self.d,1)[0]);xr=float(xhours([cap['return_ns']],self.d,1)[0]);self.band('code >=100-lot refill cluster',cap['lo'],cap['hi'],x,12);self.focus_start=xr
                self.line('code refill cluster low',cap['lo'],x,12);self.line('code refill cluster high',cap['hi'],x,12)
                self.marks.append((xr,(cap['lo']+cap['hi'])/2,'first code return','#000000'))

    def sires(self):
        n=int(self.id[-2:]);self.a,self.b=9.5,12;self.prior_value();self.feature="tape"
        if n in (3,4,6,7,8):self.feature="profilePrior"
        am=window(self.d,9.5,12)
        if n==1:
            self.line('code final AM trade/close',am['close'],9.5,12)
            self.notes.append('One either-side absorption Boolean is reused for both VA-edge directions; entry is the last AM print.')
        if n==2:
            for key,above in [('VAL',True),('VAH',False)]:
                v=self.op.get(key)
                if v:
                    self.band(key+' ±2 tick band',v-2*TICK,v+2*TICK,9.5,12)
                    got=ff.r_s02_third_retest(am['h'].tolist(),am['l'].tolist(),[0.0]*am['n'],level=v,r_width=self.r.get('W69') or 20.,band_lo=v-2*TICK,band_hi=v+2*TICK,from_above=above,later_close=am['close'],later_high=am['high'])
                    self.trace['helpers']['s02_'+key]=got
                    self.notes.append(f"Code {key}: {got['tests']} counted tests; defence volumes hard-coded zero. No close-through required by the scored return.")
        if n==3:
            self.feature='tape'
            self.notes.append('Current producer uses whole-AM extrema/sell sizes at an OFM catalyst, not a second level-specific retest; resting refill unavailable.')
        if n==4:
            wk=TABLES["weekly_delta_F"].get(self.iso,{})
            for k in ("weekly_high","weekly_low","dp_min"):self.line(k,wk.get(k))
            from trading_research.research.phase1_live.family_tape import _s04_from_am
            ev=tape(self.iso);cap={}
            def trace(frame,event,arg):
                if frame.f_code is _s04_from_am.__code__ and event=='return':
                    cap.update({k:frame.f_locals.get(k) for k in ('touches','no_close_below','imb350_buy','r_h','box','got','s05')})
                return trace
            if ev:
                ta,pa,va,sa=_trades(ev,ns(self.d,9.5),ns(self.d,12));sys.settrace(trace)
                try: result=_s04_from_am(ta,pa,va,sa,wk,self.r,self.r.get('W69'))
                finally:sys.settrace(None)
                self.trace['helpers']['s04_actual']={'result':result,**cap,'weekly':wk}
                if cap.get('box'):
                    for label,p in zip(('low','high'),cap['box']):self.line('code micro/fallback '+label,p,9.5,12)
            self.notes.append("Retained five-session delta reference; no new weekly profile built.")
        if n==5:
            w=window(self.d,9+40/60,12);early=window(self.d,9.5,9+40/60)
            got=ff.r_s05_microbalance(w["c"],w["l"],w["h"],r_height=self.r.get("W69") or 20,break_close=w["close"],htf=early["high"],later_high=w["high"],later_low=w["low"])
            self.trace["helpers"]["r_s05_microbalance"]=got
            if got.get("box"):
                self.band("last qualifying close-run box (unfrozen)",*got["box"],9+40/60,12)
                for label,p in zip(('low','high'),got['box']):self.line('code last microbalance '+label,p,9+40/60,12)
                last=None
                for i in range(w['n']-4):
                    for j in range(5,w['n']-i+1):
                        if np.ptp(w['c'][i:i+j])<=.1*(self.r.get('W69') or 20)+1e-12:last=(i,j)
                if last:
                    i,j=last;assert got['box']==[float(w['l'][i:i+j].min()),float(w['h'][i:i+j].max())]
                    known=float(xhours([w['t'][i+j-1]],self.d)[0])+1/60
                    self.trace['helpers']['microbalance_last_run']={'start_index':i,'n':j,'known_hour':known}
                    self.focus_start=max(9.5,known-.05);self.notes.append(f'Last selected close-run completes at {int(known):02d}:{round((known%1)*60):02d}; score compares only final AM close.')
        if n in (6,8) and self.prev:
            pr=window(self.prev,9.5,16);acc={}
            for tk,v in zip(fm.to_ticks((pr['h']+pr['l']+pr['c'])/3),pr['v']):acc[int(tk)]=acc.get(int(tk),0)+float(v)
            nodes=fj.profile_nodes({k*TICK:v for k,v in acc.items()});hvn=(nodes.get('hvn') or [None])[0]
            self.trace['helpers']['sire_prior_ohlc_nodes']=nodes
            self.line('code first occupied-bin HVN',hvn,9.5,12)
            self.line('code prior RTH high',pr['high'],9.5,12);self.line('code prior RTH low',pr['low'],9.5,12)
            rw=self.r.get('W69') or max(pr['high']-pr['low'],1.)
            if n==6:
                self.line('code short rejection threshold',pr['high']-.5*rw,9.5,12)
                self.line('code long rejection threshold',pr['low']+.5*rw,9.5,12)
                self.notes.append('Code prior rejection is high/low to final prior close; no current actual touch or ordered 15-minute reversal gate.')
            else:
                b5=fm.resample_ohlcv(am,5);d5=(b5['c'][-3:]-b5['o'][-3:]).tolist()
                self.line('code first LVN', (nodes.get('lvn') or [pr['low']])[0],9.5,12)
                self.trace['helpers']['s08_inputs']={'deltas':d5,'prior_rej':int(np.sum(am['h']>=pr['high']-2*TICK)),'hvn':hvn}
                self.notes.append('Actual delta inputs are final three 5m close-minus-open values: '+', '.join(f'{x:g}' for x in d5)+'. These are price changes, not executed delta.')
        if n==7:self.b=16;w=window(self.d,9.5,12);self.line("AM final-close entry",w["close"],12,16)
        if n==9:
            from trading_research.research.phase1_live.family_open import ohlc_vp
            self.b=16;pre=window(self.d,9.5,10);poc,dval,dvah=ohlc_vp(pre,.70)
            self.line('code 09:30–10:00 VAH (known 10:00)',dvah,9.5,16)
            self.trace['helpers']['s09_open_profile']={'poc':poc,'val':dval,'vah':dvah,'a_low':pre['low'],'open':self.r.get('open_0930')}
            self.notes.append("Opening comparison uses developing 10:00 VAH. Displayed prior VA remains separate.")

    def pine(self):
        n=int(self.id[-2:]);self.a,self.b=8,16
        if n==1:
            self.b=12;hist=[]
            for iso in DATES:
                if iso>=self.iso:break
                w=window(date.fromisoformat(iso),-6,17)
                if w["close"] is not None:hist.append(w["close"])
            chg=np.diff(np.log(np.maximum(hist[-20:],1e-9)))*100;sig=ff.sample_stdev(chg)
            o=window(self.d,8,8+1/60)["open"]
            if sig and o:
                got=ff.r_p01_sigma_bands(o,sig,.25);self.trace["helpers"]["code_sigma"]=got
                self.line("08:00 open",o);self.line("code +0.25σ",got["upper"]);self.line("code −0.25σ",got["lower"])
                self.notes.append(f"Code SD uses {len(chg)} log changes of prior selected-session closes.")
                w=window(self.d,8,12);hr=xhours(w['t'],self.d);tr=ff.r_p01_touch_revert(o,got['upper'],got['lower'],got['sigma_px'],hr,w['h'],w['l'])
                self.trace['helpers']['p01_touch_revert']=tr
                hits=np.flatnonzero((w['h']>=got['upper'])|(w['l']<=got['lower']))
                if len(hits):
                    i=int(hits[0]);self.focus_start=float(hr[i]);self.marks.append((float(hr[i]),got[tr['side']],'code first band touch','#000000'))
                    after=np.flatnonzero(w['l'][i:]<=o) if tr['side']=='upper' else np.flatnonzero(w['h'][i:]>=o)
                    if len(after):self.marks.append((float(hr[i+int(after[0])]),o,'code open reversion','#c00040'))
        elif n==2:
            selected=False
            for h in range(9,16):
                w=window(self.d,h-1,h)
                for k in ("high","low"):self.line(f"{h-1:02d} prior hour {k}",w[k],h,h+1)
                cur=window(self.d,h,h+1)
                if not w['n'] or not cur['n']:continue
                got=ff.r_p02_hourly_sweep(prev_h=w['high'],prev_l=w['low'],prev_open=w['open'],hour_open=cur['open'],highs=cur['h'],lows=cur['l'])
                self.trace['helpers'][f'p02_hour_{h}']=got
                if not selected and got['high_ret_swept']:
                    self.line('selected prior-hour mid',(w['high']+w['low'])/2,h,h+1)
                    self.line('selected current-hour open',cur['open'],h,h+1)
                    i=int(np.flatnonzero(cur['h']>w['high'])[0]);x=float(xhours([cur['t'][i]],self.d)[0]);self.focus_start=x;selected=True
                    self.marks.append((x,w['high'],'first scored high sweep','#000000'))
            self.notes.append('Only high-sweep return is effectively scored; the same bar may supply sweep and return. Prior-hour low return is missing.')
        elif n==3:
            self.a=-1;selected=False
            for h in ff.MAGIC_HOURS:
                a=-1 if h==23 else h;w=window(self.d,a,a+1)
                self.band(f"magic {h:02d} code box",w["low"],w["high"],a,a+1)
                if w["n"]:
                    self.line(f"{h:02d} midpoint",(w["high"]+w["low"])/2,a+1,a+2)
                    for lab,p in [('H',w['high']),('L',w['low'])]:self.line(f'{h:02d} code {lab}',p,a+1,a+2)
                    nxt=window(self.d,a+1,a+2)
                    if nxt['n']:
                        side='high' if nxt['high']>w['high'] else 'low';exc=nxt['high']-w['high'] if side=='high' else w['low']-nxt['low']
                        got=ff.r_p03_magic_hour(hour=h,box_h=w['high'],box_l=w['low'],break_side=side,excursion=exc,later_high=nxt['high'],later_low=nxt['low'],t_break_min=h*60+4,t_target_min=h*60+20)
                        self.trace['helpers'][f'p03_hour_{h}']=got
                        if got['win'] and not selected:self.focus_start=a+1;selected=True
            self.notes.append("Code passes synthetic break/target times (+4/+20 minutes), not observed event times.")
        elif n==4:
            self.a,self.b=9,12;w,_,end=self.clock("range.gb.nyam");self.line('code high-raid threshold H+5pt',w['high']+5,end,12)
            nxt=window(self.d,end,12);got=ff.r_p04_raid(box_h=w['high'],box_l=w['low'],highs=nxt['h'],lows=nxt['l'],closes=nxt['c'],t_min=(nxt['t']-nxt['t'][0])/60_000.,cutoff_min=120.)
            self.trace['helpers']['p04_raid']=got
            hit=np.flatnonzero(nxt['h']>w['high']+5)
            if len(hit):self.focus_start=float(xhours([nxt['t'][int(hit[0])]],self.d)[0])
            self.notes.append("Code substitutes a 60-minute NYAM box for the Pine raid windows; upper raid alone is scored even without confirmation.")
        elif n==5:
            self.a=0;w,_,_=self.clock("range.london.00-03");ny=window(self.d,9.5,12)
            if w["n"]:
                got=ff.r_p05_london_25(w["open"],w["close"],ny["low"],ny["high"],ny["close"])
                self.line("code London body 25%",got["level"],3,12)
        elif n==6:
            self.a=-4;self.b=6;asia,_,_=self.clock("range.gb.asia");lon,_,_=self.clock("range.london.00-03")
            got=ff.r_p06_first_hit(asia_h=asia['high'],asia_l=asia['low'],lon_open=lon['open'],lon_highs=lon['h'],lon_lows=lon['l']);self.trace['helpers']['p06_first_hit']=got
            later=window(self.d,0,self.b)
            visits=np.flatnonzero(((later['l']<=asia['high']) & (later['h']>=asia['high'])) |
                                 ((later['l']<=asia['low']) & (later['h']>=asia['low'])))
            self.focus_start=float(xhours([later['t'][int(visits[0])]],self.d)[0]) if len(visits) else 2.0
            self.notes.append('Actual clock substitutes: Asia20:00–00:00, London00:00–03:00; no source NY-vs-London table.')
            self.notes.append('Detail centers on the first later contact of the implemented Asia edges, including contacts after the legacy London window.')
        elif n==7:
            self.a,self.b=9.5,16;w,_,end=self.clock("range.or.5m");nxt=window(self.d,end,12)
            got=ff.r_p07_or_mid(o=w['open'],h=w['high'],l=w['low'],c=w['close'],later_h=nxt['h'],later_l=nxt['l'],later_c=nxt['c']);self.trace['helpers']['p07_or_mid']=got
            self.line('helper 0.411% upper (unscored)',got['ext_up'],end,16)
            self.line('helper 0.450% lower (unscored)',got['ext_dn'],end,16)
            self.notes.append('Midpoint score scans only to12:00. Helper extreme_first is after OR; source final-extreme order is within OR. Extension helpers are unscored.')
        elif n==8:
            self.a=9.5;self.clock("range.ib");self.focus_start=10.5
            self.notes.append('Code scores post-IB close-based single-side path only; source intra-IB extreme order, close-vs-mid, retest band and price-percentile extensions are absent.')
        elif n==9:
            for k in ("prior_rth_high","prior_rth_low","open_0930"):self.line(k,self.r.get(k),9.5,16)
        elif n==10 and self.prev:
            w=window(self.prev,-6,17);rth=window(self.d,9.5,16)
            if not w["n"]:
                self.notes.append("Prior Globex bars absent: pivot undefined; code false is not a valid no-touch observation.")
                return
            got=ff.r_p10_pivots(w["high"],w["low"],w["close"],rth_open=rth["open"],rth_high=rth["high"])
            self.trace["helpers"]["daily_floor_pivots"]=got
            for k,v in got.items():
                if k not in ("context","pp_touch"):self.line(k,v,9.5,16)
        elif n==11:
            self.a,self.b=9.5,10;w=window(self.d,9.5,10)
            got=ff.r_p11_first_fvg(w["h"],w["l"],w["c"],[9]*w["n"]);self.trace["helpers"]["first_fvg"]=got
            if got["box"]:
                self.band("first code FVG (formation time not retained)",*got["box"],9.5,10)
                for lab,p in zip(('low','high'),got['box']):self.line('code first 1m FVG '+lab,p,9.5,10)
            self.notes.append('Caller uses1m09:30–10:00 and scores FVG existence; no fill prices or direction outcome supplied.')
        elif n==12:
            self.a,self.b=9.5,9.75;w=window(self.d,9.5,16)
            self.band("first 09:30 candle reference",w["l"][0],w["h"][0],9.5+1/60,9.75)
            for lab,p in [('H',w['h'][0]),('L',w['l'][0])]:self.line('code previous 1m '+lab,p,9.5+1/60,9.75)
            got=ff.r_p12_sweep_cisd(prev_h=w['h'][0],prev_l=w['l'][0],prev_o=w['o'][0],prev_c=w['c'][0],o=w['o'][1],h=w['h'][1],l=w['l'][1],c=w['c'][1]);self.trace['helpers']['p12_sweep_cisd']=got
            self.band('helper previous-body-mid to current-open',*got['mid_box'],9.5+2/60,9.75)
            for lab,p in zip(('low','high'),got['mid_box']):self.line('unscored helper midbox '+lab,p,9.5+2/60,9.75)
            self.notes.append("Code inspects only the first two one-minute RTH candles; no literal HTF CISD run.")
        elif n==13:self.line("00:00 open",self.join.get("tdo"),8,16)
        elif n==14:
            self.a=9.5;w=window(self.d,9.5,16);f=window(self.d,9.5,10)
            self.line("final RTH HOD (outcome)",w["high"]);self.line("first-30m high",f["high"],10,16)
        elif n==15:
            self.a=9.5;hist=[]
            for iso in DATES:
                if iso>=self.iso:break
                w=window(date.fromisoformat(iso),9.5,16)
                if w["n"]:hist.append(w["high"]-w["low"])
            if hist:
                q=float(np.median(hist[-60:]));w=window(self.d,9.5,16)
                got=ff.r_p15_ssl(open_px=self.r.get("open_0930") or 0,p_rng=q,p_mfe=.6*q,p_mae=.4*q,session_high=w["high"],session_low=w["low"])
                for k in ("rng_hi","rng_lo","mfe_lv","mae_lv"):self.line("code "+k,got[k])
                self.trace["helpers"]["SSL_proxy"]=got
        elif n==16 and self.prev:
            self.a=-6;w=window(self.prev,-6,17);vix=self.join.get("vix")
            if w["close"] and vix:
                got=fm.ev_vix16_zones(w["close"],vix);self.trace["helpers"]["ev_vix16_zones"]=got
                self.line("prior Globex last close",w["close"])
                for k,v in got.items():
                    if isinstance(v,tuple):
                        self.band(k,*v,-6,16)
                        self.line(k+' low',v[0],-6,16);self.line(k+' high',v[1],-6,16)
                self.notes.append('Current helper log-space VIX substitute; retained level cache lacks four newest1.0-zone bound fields. Score uses whole-session containment.')
        elif n==17:
            self.a=-6;self.line("18:00 open",window(self.d,-6,-6+1/60)["open"],-6,16);self.feature="profileRTH"
            self.notes.append("Pine OHLC profile is not implemented by this scored flag; trade VP shown as available diagnostic.")
        elif n==18:
            self.a,self.b=9.5,12;self.feature="ohlcCVD"
            self.clock('range.6-9.published')
            self.notes.append("Blocked OHLC-CVD substitute. Actual producer sign(C−O)×V series shown; source Confluence close-position/persistence rules are not this formula.")
        elif n==19:
            self.a,self.b=9.5,10;w=window(self.d,9.5,12);got=ff.r_p19_body_gap(w["o"],w["h"],w["l"],w["c"])
            self.trace["helpers"]["body_gap"]=got
            if got.get("zone"):
                self.band("first two bodies: code gap",*got["zone"],9.5+2/60,10)
                for lab,p in zip(('low','high'),got['zone']):self.line('code two-body gap '+lab,p,9.5+2/60,10)
        elif n==20:
            self.a,self.b=9.5,12;self.feature="tape";ev=tape(self.iso)
            if ev:
                ta,pa,va,sa=_trades(ev,ns(self.d,9.5),ns(self.d,12));self.trace['helpers']['p20_actual']={'max_print':float(va.max()),'range_ticks':float((pa.max()-pa.min())/TICK),'n100':int(np.sum(va>=100))}
                self.notes.append(f"Actual max AM print={va.max():g}, range={(pa.max()-pa.min())/TICK:g}ticks. Scored cut is>=100 lots and>=8ticks; no MVFL zones exist.")

    def regime(self):
        n=int(self.id[-2:]);self.a,self.b=9.5,16
        if n==1:
            self.root="/workspace/data/quantpad/nasdaq__qqq-etf__ohlcv-1m"
            for k in ("flip","call_wall","put_wall","spot"):self.line("QQQ "+k,self.join.get(k))
            self.notes.append("Native QQQ coordinates. Code flip is cumulative across strike, not a repriced spot root.")
            self.feature="gex"
        elif n==2:self.feature="vix";self.notes.append("Prior-session daily VIX context; no intraday VIX boundary is implied.")
        elif n==3:self.b=12;self.prior_value()
        elif n==4:
            self.feature="sisters";self.notes.append("Blocked triad definition. Native products shown in own normalized returns, not compared as absolute prices.")

    def make(self):
        {"J":self.jumbo,"G":self.greenbird,"A":self.auction,"F":self.flow,"R":self.regime,"S":self.sires,"P":self.pine}[self.id[2]]()
        return self


def candles(ax,w,d):
    if not w["n"]:return
    x=xhours(w["t"],d);up=w["c"]>=w["o"];col=np.where(up,"#187d68","#bf443b")
    ax.add_collection(LineCollection([[(a,l),(a,h)] for a,l,h in zip(x,w["l"],w["h"])],colors=col,linewidths=.6))
    for a,o,c,color in zip(x,w["o"],w["c"],col):
        ax.add_patch(Rectangle((a-.005,min(o,c)),.01,max(abs(c-o),TICK/4),facecolor=color,edgecolor=color,linewidth=.2))


def paint(ax,dw,a,b,zoom=False):
    w=window(dw.d,a,b,dw.root);candles(ax,w,dw.d)
    if not w["n"]:
        ax.text(.5,.5,"No retained one-minute bars for this dated window\nSource screenshot cannot be replayed from the available input.",ha="center",va="center",transform=ax.transAxes,fontsize=12)
    lo=w["low"] if w["n"] else 0;hi=w["high"] if w["n"] else 1
    visible=[]
    for q in dw.boxes:
        if q["end"]<a or q["start"]>b:continue
        ax.add_patch(Rectangle((q["start"],q["low"]),q["end"]-q["start"],q["high"]-q["low"],facecolor=q["color"],edgecolor=q["color"],alpha=.13))
        visible.extend([q["low"],q["high"]])
    for q in dw.lines:
        if q["end"]<a or q["start"]>b:continue
        ax.plot([q["start"],q["end"]],[q["price"]]*2,color=q["color"],lw=.8,ls=q["style"])
        visible.append(q["price"])
    for x,y,label,c in dw.curves:ax.plot(x,y,label=label,color=c,lw=1)
    if dw.curves:ax.legend(loc='lower left',fontsize=6,framealpha=.85)
    for x,y,label,c in dw.marks:
        if a<=x<=b:
            ax.scatter([x],[y],marker="x",s=40,color=c,zorder=5)
            offset=(5,-22) if label=='last80 minimum' else (5,15)
            ax.annotate(label,(x,y),xytext=offset,textcoords="offset points",fontsize=7,color=c,arrowprops=dict(arrowstyle="-",lw=.5,color=c))
    if visible and not zoom:lo=min(lo,min(visible));hi=max(hi,max(visible))
    pad=max((hi-lo)*.09,2*TICK);ax.set_ylim(lo-pad,hi+pad);ax.set_xlim(a,b+(b-a)*.20)
    # Labels at numeric line positions, spread only vertically for legibility.
    labs=[q for q in dw.lines if q["end"]>=a and q["start"]<=b and lo-pad<=q["price"]<=hi+pad]
    labs.sort(key=lambda q:q["price"])
    ys=np.array([q["price"] for q in labs]);gap=(hi-lo+2*pad)*.045
    for i in range(1,len(ys)):ys[i]=max(ys[i],ys[i-1]+gap)
    if len(ys) and ys[-1]>hi+pad:ys-=ys[-1]-(hi+pad)
    for q,y in zip(labs,ys):
        ax.annotate(f'{q["label"]} {q["price"]:.2f}',xy=(b,q["price"]),xytext=(b+(b-a)*.012,y),fontsize=6.7,color=q["color"],va="center",arrowprops=dict(arrowstyle="-",color=q["color"],lw=.35),annotation_clip=False)
    ticks=np.linspace(a,b,7);minutes=[round(x*60)%1440 for x in ticks]
    ax.set_xticks(ticks,[f"{m//60:02d}:{m%60:02d}" for m in minutes]);ax.grid(alpha=.15);ax.tick_params(labelsize=8)
    ax.set_xlabel("New York clock (bar-start timestamps)",fontsize=8)
    return w


def feature(ax,dw):
    kind=dw.feature;ev=None
    if kind=='ohlcCVD':
        w=window(dw.d,-6,12);got=ff.r_p18_ohlc_cvd(w['o'],w['c'],w['v']);running=np.cumsum(got['delta']);xx=xhours(w['t'],dw.d)
        ax.plot(xx,running,color='#8453a4',lw=.9);ax.axhline(0,color='gray',lw=.5)
        ax.set_title('Actual code ETH OHLC-sign cumulative volume; blocked',fontsize=9)
        ax.set_xlabel('New York decimal hour; zero reset at prior18:00',fontsize=8)
        ax.set_ylabel('Signed bar volume (not aggressor delta)',fontsize=8)
        dw.trace['helpers']['p18_ohlc_series']={'hours':xx,'delta':got['delta'],'cvd':running}
        return
    if kind=="shapePrior":
        w=window(dw.prev,9.5,16);acc={}
        for tk,v in zip(fm.to_ticks((w["h"]+w["l"]+w["c"])/3),w["v"]):acc[int(tk)]=acc.get(int(tk),0)+float(v)
        ks=sorted(acc);vv=[acc[k] for k in ks];shape=fm.vp_p_shape(vv)
        ax.barh(np.array(ks)*TICK,vv,height=TICK,color="#285fa8")
        ax.set_title(f"Actual code prior HLC3-volume profile; shape={shape}",fontsize=9)
        ax.set_xlabel("Bar volume assigned to rounded HLC3; zero bins omitted",fontsize=8)
        dw.trace["helpers"]["shape_input"]={"prices":[k*TICK for k in ks],"volumes":vv,"shape":shape}
        return
    if kind=="tpoCode":
        from trading_research.research.phase1_live.family_gap import _tpo_poor
        capture={}
        def trace(frame,event,arg):
            if frame.f_code is _tpo_poor.__code__ and event=="return":capture.update({k:frame.f_locals.get(k) for k in ("count","top","bot","h","l")})
            return trace
        sys.settrace(trace)
        try: result=_tpo_poor(window(dw.d,9.5,16))
        finally:sys.settrace(None)
        counts=capture.get("count")
        if counts is not None:
            prices=np.arange(capture["bot"],capture["top"]+1)
            ax.barh(prices,counts,height=.9,color=np.where(counts==1,"#be4b33","#285fa8"))
        ax.set_title(f"Exact code current-RTH 1-point TPO rows; poor={result}",fontsize=9)
        ax.set_xlabel("30-minute range coverage count; red=one period",fontsize=8)
        dw.trace["helpers"]["code_tpo_current"]={**capture,"result":result}
        return
    if kind == "absorption3m":
        w = fm.resample_ohlcv(window(dw.d, 9.5, 12), 3)
        baseline = np.full(w["n"], np.nan)
        for i in range(14, w["n"]): baseline[i] = np.mean(w["v"][i-14:i])
        xx = xhours(w["t"], dw.d)
        ax.bar(xx, w["v"], width=3/60, color="#6e7e90")
        ax.plot(xx, baseline, color="#b35321", label="prior 14 × 3m SMA; AM reset")
        ax.legend(fontsize=7);ax.set_title("Actual code volume window: first baseline at 10:12",fontsize=9)
        ax.set_xlabel("New York decimal hour",fontsize=8)
        dw.trace["helpers"]["volume_3m"]={"times":xx,"volume":w["v"],"sma14":baseline}
        return
    if kind == "tapeJ15":
        ev = tape(dw.iso)
        if ev is None: return
        for a,b,threshold,label in [(2,5,75,"London ≥75"),(9.5,12,100,"AM ≥100")]:
            t,p,v,s = _trades(ev,ns(dw.d,a),ns(dw.d,b));mask=v>=threshold
            ax.scatter(xhours(t[mask],dw.d,1),p[mask],s=np.minimum(v[mask],250)*.4,
                       c=np.where(s[mask]>0,"#007d73",np.where(s[mask]<0,"#be4b33","gray")),alpha=.7)
            dw.trace["helpers"][label]={"print_count":int(mask.sum()),"threshold":threshold,"hours":[a,b]}
        for key in ("m05_high","m05_low"):
            ax.axhline(dw.levels[key],ls="--",lw=.6,label=key+" (known 09:00)")
        ax.legend(fontsize=7);ax.set_title("Code London + AM prints; future 6–9 levels expose leakage",fontsize=9)
        ax.set_xlabel("New York decimal hour",fontsize=8);ax.set_ylabel("NQ price",fontsize=8)
        return
    if kind in ("tape","profile69","profileRTH","profilePrior","profileON","footprint","tpo"):
        iso=PREV.get(dw.iso) if kind in ("profilePrior","tpo") else dw.iso
        ev=tape(iso) if iso else None
        if ev is None:ax.text(.05,.5,"Retained tape unavailable for this session",transform=ax.transAxes);return
        dd=date.fromisoformat(iso)
        a,b=(6,9) if kind=="profile69" else (-6,9.5) if kind=="profileON" else (9.5,16) if kind.startswith("profile") or kind in ("footprint","tpo") else (9.5,12)
        t,p,v,s=_trades(ev,ns(dd,a),ns(dd,b));dw.trace["sources"].append(ev["source_path"])
        dw.trace["helpers"]["tape_window"]={"date":iso,"from":a,"to":b,"trades":len(t),"buy_volume":float(v[s>0].sum()),"sell_volume":float(v[s<0].sum()),"unknown_volume":float(v[s==0].sum())}
        if not len(t):ax.text(.05,.5,"No retained executions in window",transform=ax.transAxes);return
        if kind=="tape":
            big=v>=30;xx=xhours(t[big],dd,1);cc=np.where(s[big]>0,"#007d73",np.where(s[big]<0,"#be4b33","gray"))
            ax.scatter(xx,p[big],s=np.minimum(v[big],250)*.3,c=cc,alpha=.65,edgecolors="none")
            for threshold in (30,75,100):dw.trace["helpers"][f"prints_ge_{threshold}"]=int((v>=threshold).sum())
            ax.set_title(f"Actual AM prints ≥30 lots: {int(big.sum())}; green buy / red sell",fontsize=9)
            ax.set_xlabel("New York decimal hour",fontsize=8);ax.set_ylabel("NQ price",fontsize=8)
            if big.sum()<=20:
                for x,y,q in zip(xx,p[big],v[big]):ax.annotate(str(int(q)),(x,y),fontsize=7)
        else:
            pack=_bins(p,v,s);lo,vol,buy,sell=pack;prices=(lo+np.arange(len(vol)))*TICK
            if kind=="tpo":
                periods=(t-ns(dd,9.5))//(30*60*1_000_000_000);ticks=np.round(p/TICK).astype(int);levels=np.unique(ticks)
                counts=np.array([len(np.unique(periods[ticks==z])) for z in levels]);ax.barh(levels*TICK,counts,height=TICK,color="#285fa8")
                ax.set_title(f"{iso} executed-price TPO count by 30m; diagnostic",fontsize=9);ax.set_xlabel("Distinct periods at tick",fontsize=8)
            elif kind=="footprint":
                # Production aggregates RTH, despite calling it a candle footprint.
                ax.barh(prices,buy,height=TICK,color="#007d73",alpha=.65);ax.barh(prices,-sell,height=TICK,color="#be4b33",alpha=.65)
                ax.set_title(f"{iso} full-RTH buy/sell by tick (code input)",fontsize=9);ax.set_xlabel("Sell ← volume → Buy",fontsize=8)
            else:
                ax.barh(prices,vol,height=TICK,color="#285fa8",alpha=.7)
                ax.set_title(f"{iso} {a:g}–{b:g} actual trade VP",fontsize=9);ax.set_xlabel("Executed volume / tick",fontsize=8)
            for q in dw.lines:
                if prices.min()<=q["price"]<=prices.max():ax.axhline(q["price"],color=q["color"],lw=.5,ls=":")
            if dw.id=='R-J17':
                for j,(name,ps) in enumerate(dw.trace['helpers'].get('matched_profile_nodes',{}).items()):
                    if ps:ax.scatter(np.full(len(ps),float(vol.max())*(.88+.08*j)),ps,s=10,marker='|' if j else '.',label=f'all matched {name}: {len(ps)}')
                if any(dw.trace['helpers'].get('matched_profile_nodes',{}).values()):ax.legend(fontsize=7,loc='lower right')
            ax.set_ylabel("NQ price",fontsize=8)
    elif kind=="sisters":
        for name,root in {"NQ":OHLC1M,**SISTERS_1M}.items():
            w=window(dw.d,9.5,12,str(root))
            if w["n"]:ax.plot(xhours(w["t"],dw.d),(w["c"]/w["open"]-1)*100,label=name)
        ax.legend(fontsize=7);ax.set_title("Native instruments: return from each own 09:30 open",fontsize=9);ax.set_ylabel("%",fontsize=8)
    elif kind=="vix":
        vals=[(s,JOIN[s].get("vix")) for s in DATES if s<=dw.iso and JOIN.get(s,{}).get("vix") is not None][-40:]
        ax.plot(range(len(vals)),[v for _,v in vals]);ax.axhspan(15,18,alpha=.15,color="orange");ax.set_title(f"Lagged VIX at {dw.iso}: {dw.join.get('vix')} (band 15–18)",fontsize=9);ax.set_xlabel("Last 40 eligible records",fontsize=8)
    elif kind=="gex":
        g={k:dw.join.get(k) for k in ("spot","flip","call_wall","put_wall","net_gex","n_strikes")}
        ax.axis("off");ax.text(.02,.94,"Retained native QQQ result\n\n"+"\n".join(f"{k}: {v}" for k,v in g.items())+"\n\nOther products' native intraday boards are not\nimplemented here; their inputs stay separate.",va="top",transform=ax.transAxes,fontsize=10)
    else:
        w=window(dw.d,dw.a,dw.b,dw.root);ax.bar(xhours(w["t"],dw.d),w["v"],width=1/60,color="#6e7e90")
        if not w["n"]:ax.text(.5,.5,"No retained volume for this window",ha="center",transform=ax.transAxes)
        ax.set_title("Observed one-minute volume",fontsize=9);ax.set_xlabel("New York decimal hour",fontsize=8)
    ax.tick_params(labelsize=7);ax.grid(alpha=.12)


def draw(spec):
    dw=Drawing(spec).make();score=next(r for r in SCORES if r["id"]==dw.id)
    fig=plt.figure(figsize=(18,10.5));gs=fig.add_gridspec(2,2,height_ratios=[1.35,1],width_ratios=[1.6,1],hspace=.29,wspace=.23)
    ax=fig.add_subplot(gs[0,:]);paint(ax,dw,dw.a,dw.b)
    # Detail around the first post-formation interaction, otherwise the open.
    start=dw.focus_start if dw.focus_start is not None else max(dw.a,9.5) if dw.b>9.5 else dw.a
    zw=window(dw.d,start,dw.b,dw.root);focus=start
    targets=[q for q in dw.lines if q["start"]<=start and q["end"]>start]
    for i in range(zw["n"]):
        if any(zw["l"][i]<=q["price"]<=zw["h"][i] for q in targets):focus=float(xhours([zw["t"][i]],dw.d)[0]);break
    z0=max(dw.a,focus-.1);z1=min(dw.b,z0+.5)
    if z1-z0<.15:z0=max(dw.a,z1-.5)
    az=fig.add_subplot(gs[1,0]);paint(az,dw,z0,z1,zoom=True);az.set_title("Price detail: first plotted reference interaction / opening diagnostic",fontsize=9)
    af=fig.add_subplot(gs[1,1]);feature(af,dw)
    result="UNSCORED ON THIS DATE" if spec["code_result"] is None else str(spec["code_result"]).upper()
    fig.suptitle(f"{dw.id} · {dw.iso} · case {spec['case']} · CODE = {result}",fontsize=15,fontweight="bold",x=.06,ha="left",y=.985)
    display_event = ("Implemented NYAM high raid >5 points; scorer accepts raid even without a close back"
                     if dw.id == "R-P04" else score["event"])
    fig.text(.06,.945,"\n".join(textwrap.wrap(display_event,145)),fontsize=9,va="top")
    note=" | ".join(dw.notes)
    footer=f"Observed implementation, not a certified source trigger. Code positives / negatives: {spec['positive_count']} / {spec['negative_count']}. " + note
    fig.text(.06,.015,"\n".join(textwrap.wrap(footer,185)),fontsize=7.6,va="bottom")
    fig.subplots_adjust(left=.065,right=.97,top=.89,bottom=.105)
    PLOTS.mkdir(parents=True,exist_ok=True);base=f"{dw.id}-{spec['case']}-{dw.iso}"
    fig.savefig(PLOTS/(base+".png"),dpi=140);plt.close(fig)
    dw.trace.update(plot=f"plots/{base}.png",notes=dw.notes,root=dw.root,
                    predicate=score.get("predicate_source"),event=score["event"],display_event=display_event,detail_window=[z0,z1])
    (PLOTS/(base+".json")).write_text(json.dumps(dw.trace,indent=2,default=serial)+"\n")
    return {**spec,"plot":f"plots/{base}.png","trace":f"plots/{base}.json","notes":dw.notes}


def main():
    p=argparse.ArgumentParser();p.add_argument("--ids",nargs="*");p.add_argument("--force",action="store_true");args=p.parse_args()
    specs=candidates();(OUT/"chart_cases.json").write_text(json.dumps(specs,indent=2)+"\n")
    results=[]
    for spec in specs:
        if args.ids and spec["id"] not in args.ids:continue
        try:
            result=draw(spec);results.append(result);print(spec["id"],spec["case"],spec["date"],"written",flush=True)
        except Exception as e:
            import traceback;traceback.print_exc();results.append({**spec,"error":f"{type(e).__name__}: {e}"})
    dest=OUT/("plot_results-"+"_".join(args.ids)+".json" if args.ids else "plot_results.json")
    dest.write_text(json.dumps(results,indent=2)+"\n")
    if any("error" in r for r in results):raise SystemExit(1)


if __name__=="__main__":main()
