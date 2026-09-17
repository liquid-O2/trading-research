"""Member (K10) on the ES tape, 2026-08-03: do the adapter's generated reasons
(look-left reactions on five-minute pivots, minor HVNs of the prior day's
profile, paired within two ticks) produce his two drawn pairs before he traded
them? A duck-typed ES market: bars from the ES ohlcv-1m parquet, the prior
session's profile from the ES trades parquet (instrument 42140870, ESU6)."""
from __future__ import annotations
import sys
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
import pyarrow.parquet as pq, pyarrow.compute as pc
from trading_research.research.rule_discovery.source_adapters import member
ET = ZoneInfo("America/New_York"); NS = 10**9; MIN = 60 * NS
ROOT = "/workspace/data/quantpad"
INSTR = 42140870
def ns_at(day, hhmm):
    y, m, d = (int(x) for x in day.split("-")); return int(datetime(y, m, d, int(hhmm[:2]), int(hhmm[3:]), tzinfo=ET).timestamp()) * NS
def et(ns): return datetime.fromtimestamp(ns / NS, ET).strftime("%m-%d %H:%M")
def load_bars(start, end):
    t = pq.read_table(f"{ROOT}/cme__es-continuous-futures__ohlcv-1m/2026.parquet")
    unit = 1 if pc.max(t["t"]).as_py() > 10**15 else 10**6
    sub = t.filter(pc.and_(pc.and_(pc.greater_equal(t["t"], start // unit), pc.less(t["t"], end // unit)), pc.equal(t["instrument_id"], INSTR))).to_pandas().sort_values("t")
    return [{"start": int(r.t) * unit, "end": int(r.t) * unit + MIN, "known_at": int(r.t) * unit + MIN, "observed_complete": True, "bar_id": f"es:{int(r.t)}", "O": Decimal(str(r.o)), "H": Decimal(str(r.h)), "L": Decimal(str(r.l)), "C": Decimal(str(r.c)), "V": int(r.v)} for r in sub.itertuples(index=False)]
def aggregate(rows, seconds):
    out = []; span = seconds * NS
    for r in rows:
        b = r["start"] // span * span
        if out and out[-1]["start"] == b:
            o = out[-1]; o["H"] = max(o["H"], r["H"]); o["L"] = min(o["L"], r["L"]); o["C"] = r["C"]; o["end"] = r["end"]; o["known_at"] = r["end"]
        else:
            out.append({"start": b, "end": r["end"], "known_at": r["end"], "observed_complete": True, "bar_id": f"es{seconds}:{b}", "O": r["O"], "H": r["H"], "L": r["L"], "C": r["C"]})
    return out
def load_profile(start, end):
    t = pq.read_table(f"{ROOT}/cme__es-continuous-futures__trades/2026.parquet", columns=["t", "price", "size", "instrument_id"], filters=[("instrument_id", "=", INSTR)])
    unit = 1 if pc.max(t["t"]).as_py() > 10**15 else 10**6
    sub = t.filter(pc.and_(pc.greater_equal(t["t"], start // unit), pc.less(t["t"], end // unit))).to_pandas()
    vol = sub.groupby("price")["size"].sum().sort_index()
    rows = [{"price": Decimal(str(p)), "total_volume": int(v)} for p, v in vol.items()]
    return {"rows": rows, "poc": max(rows, key=lambda r: r["total_volume"])["price"] if rows else None, "known_at": end, "profile_id": f"es-profile:{start}:{end}"}
class Win:
    def __init__(self, start, end):
        self.start, self.end = start, end; self._bars = load_bars(start, end); self._profile = None
    def bars(self, start, end, seconds=60):
        rows = [r for r in self._bars if start <= r["start"] < end]
        return rows if seconds == 60 else aggregate(rows, seconds)
    def profile(self, start, end, fraction=None):
        return load_profile(start, end)
class ESMarket(Win):
    b02_fixtures = None
    def __init__(self, day, prior_day):
        super().__init__(ns_at(prior_day, "18:00") + 0 if False else ns_at(day, "00:00") - 6 * 3600 * NS, ns_at(day, "16:00"))
        self._prior = Win(ns_at(prior_day, "00:00") - 6 * 3600 * NS, ns_at(prior_day, "16:00"))
        self.day = day
    def prior(self, kind="day"):
        return {"sessions": [{"window": self._prior}]}
    def at(self, hhmm, offset=0):
        return ns_at(self.day, hhmm)
m = ESMarket("2026-08-03", "2026-07-31")
print("session bars", len(m._bars), et(m.start), "->", et(m.end), "| prior bars", len(m._prior._bars))
HIS = {"short": (Decimal("7558.75"), Decimal("7564")), "long": (Decimal("7544.75"), Decimal("7547.75"))}
DECIDE = {"short": ns_at("2026-08-03", "09:25"), "long": ns_at("2026-08-03", "09:30")}
hvns = member._look_left_hvns(m)
print("prior-day minor HVNs:", len(hvns), "near his pairs:", sorted({str(n["price"]) for n in hvns if any(lo - 2 <= n["price"] <= hi + 2 for lo, hi in HIS.values())}))
kg1 = member._kg1_levels(m); print("kg1:", kg1[:3])
for side in ("short", "long"):
    reactions = member._look_left_reactions(m, side)
    known = [r for r in reactions if int(r["known_at"]) <= DECIDE[side]]
    print(f"\n{side}: reactions {len(reactions)} (known by {et(DECIDE[side])}: {len(known)})")
    lo, hi = HIS[side]
    near = [r for r in known if lo - 2 <= Decimal(str(r["price"])) <= hi + 2]
    for r in near: print("  reaction near his pair:", r["price"], "at", et(int(r["at"])), "known", et(int(r["known_at"])), "distance", r.get("reaction_distance"))
    pairs = member._pair_reasons(known, hvns, kg1, side)
    print("  pairs (known):", len(pairs))
    for reaction, second, kind in pairs:
        px = Decimal(str(reaction["price"]))
        flag = "<== his pair" if lo - 2 <= px <= hi + 2 else ""
        print(f"   {px} reaction@{et(int(reaction['at']))} + {kind} {second.get('price')} {flag}")
