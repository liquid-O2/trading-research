import pyarrow.parquet as pq, bisect, itertools, json
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
from pathlib import Path
NY=ZoneInfo("America/New_York"); root=Path("/workspace/data/quantpad/cme__nq-continuous-futures__ohlcv-1m")
rows=[]
for y in (2023,2024,2025,2026): rows+=pq.read_table(root/f"{y}.parquet",columns=["t","instrument_id","o","h","l","c","v"]).to_pylist()
by={}
for r in rows:
    a=datetime.fromtimestamp(r["t"]/1000,timezone.utc).astimezone(NY); by.setdefault(a.date(),[]).append((a.hour*60+a.minute,r))
days=sorted(by)
def front(d):
    tot={}
    for m,r in by[d]: tot[r["instrument_id"]]=tot.get(r["instrument_id"],0)+r["v"]
    inst=max(tot,key=tot.get); return [(m,r) for m,r in by[d] if r["instrument_id"]==inst]
def anchor_px(d,a):
    pre=[r for m,r in front(d) if m<a]; return max(pre,key=lambda r:r["t"])["c"] if pre else None
def exc(d,a,end):
    fr=front(d); px=anchor_px(d,a); post=[r for m,r in fr if a<=m<end]
    if px is None or len(post)<(end-a)*0.8: return None
    return px, max(r["h"] for r in post)-px, px-min(r["l"] for r in post)
def atr(i,n):
    v=[]
    for j in range(max(0,i-n),i):
        fr=[r for m,r in front(days[j]) if 570<=m<960]
        if fr: v.append(max(r["h"] for r in fr)-min(r["l"] for r in fr))
    return sum(v)/len(v) if v else None
# printed frames: (date, anchor_min, tier, lo, hi)
F=[(date(2025,12,30),540,"T1",25740,25750),(date(2025,12,30),540,"T1",25677,25687),(date(2025,12,30),540,"T2",25785,25795),(date(2025,12,30),540,"T2",25630,25640),
   (date(2026,1,2),540,"T1",25718,25725),(date(2026,1,2),540,"T1",25660,25666),(date(2026,1,2),540,"T2",25758,25764),(date(2026,1,2),540,"T2",25620,25626),
   (date(2026,1,9),540,"T3",25655,25665),(date(2026,2,24),540,"T3",24710,24720),(date(2026,2,24),540,"T3",25000,25010),
   (date(2026,1,2),600,"T2x",25760,25768),(date(2026,1,9),600,"T2x",25625,25640),
   (date(2025,11,10),540,"T34",25632,25650),(date(2025,11,10),540,"T34",25417,25433),
   (date(2026,8,28),540,"EV",29590,29724),(date(2026,9,1),540,"EV",29058,29195)]
cache={}
def dist(i,a,end,N,norm):
    key=(a,end,N,norm)
    if key in cache and i in cache[key]: return cache[key][i]
    ups=[];dns=[]
    for j in range(max(0,i-N-30),i):
        e=exc(days[j],a,end)
        if not e: continue
        s=1.0 if norm=="raw" else (atr(j,10) or 0)
        if not s: continue
        ups.append(e[1]/s); dns.append(e[2]/s)
    ups=sorted(ups[-N:]); dns=sorted(dns[-N:]); cache.setdefault(key,{})[i]=(ups,dns); return ups,dns
def rank(v,x): return bisect.bisect_left(v,x)/len(v)
out={}
for end in (720,960):
  for N in (250,400,500):
    for norm in ("raw","atr10"):
      res={}
      for d,a,tier,lo,hi in F:
        i=days.index(d); px=anchor_px(d,a); s=1.0 if norm=="raw" else atr(i,10)
        ups,dns=dist(i,a,end,N,norm)
        if tier=="EV":
            r=(rank(dns,(px-lo)/s), rank(ups,(hi-px)/s)); res.setdefault("EV_lo",[]).append(r[0]); res.setdefault("EV_hi",[]).append(r[1]); continue
        if hi>px: r=(rank(ups,(lo-px)/s),rank(ups,(hi-px)/s))
        else: r=(rank(dns,(px-hi)/s),rank(dns,(px-lo)/s))
        res.setdefault(tier,[]).append(r)
      spread={t:(round(min(x[0] for x in v),3),round(max(x[1] for x in v),3)) for t,v in res.items() if t not in("EV_lo","EV_hi")}
      score=sum(hi-lo for lo,hi in spread.values())
      print(f"end={end//60:02d}:00 N={N} {norm:5s} score={score:.2f} ranges={spread} EV lo={[round(x,2) for x in res['EV_lo']]} hi={[round(x,2) for x in res['EV_hi']]}")

print("\n=== predictive check: raw points, 09:00->16:00, N=250; tiers as percentile bands ===")
Q={"T1":(0.10,0.18),"T2":(0.30,0.38),"T3":(0.52,0.59)}
def q(v,p): return v[min(len(v)-1,int(round(p*(len(v)-1))))]
for d,a,tier,lo,hi in F:
    if a!=540 or tier not in Q and tier!="EV": continue
    i=days.index(d); px=anchor_px(d,a); ups,dns=dist(i,540,960,250,"raw")
    if tier=="EV":
        plo,phi=px-q(dns,0.25), px+q(ups,0.25); p50=px+q(ups,0.50)
        print(f"{d} EV printed {lo}-{hi} | predicted {plo:.0f}-{phi:.0f} (err {plo-lo:+.0f}/{phi-hi:+.0f}) | +50% predicted {p50:.0f}" + (" vs printed 29290" if d==date(2026,9,1) else "")); continue
    up = hi>px; v=ups if up else dns; s=1 if up else -1
    p0,p1=Q[tier]
    e0,e1=(px+s*q(v,p0), px+s*q(v,p1)); plo,phi=min(e0,e1),max(e0,e1)
    print(f"{d} {tier}{'+' if up else '-'} printed {lo}-{hi} (w {hi-lo}) | predicted {plo:.0f}-{phi:.0f} (w {phi-plo:.0f}) | edge err {plo-lo:+.0f}/{phi-hi:+.0f} | overlap {'yes' if plo<=hi and phi>=lo else 'NO'}")

print("\n=== grid: zone = [p_k, p_(k+delta)] per tier, raw points 09:00->16:00 N=250 ===")
import numpy as np
zones={}
for d,a,tier,lo,hi in F:
    if a!=540 or tier not in Q: continue
    i=days.index(d); px=anchor_px(d,a); ups,dns=dist(i,540,960,250,"raw")
    up=hi>px; v=np.array(ups if up else dns); s=1 if up else -1
    zones.setdefault(tier,[]).append((d,px,s,v,lo,hi))
def qv(v,p): return float(np.quantile(v,p))
for tier,zs in zones.items():
    best=None
    for k in np.arange(0.03,0.75,0.005):
        for delta in np.arange(0.005,0.12,0.005):
            err=0
            for d,px,s,v,lo,hi in zs:
                e=sorted([px+s*qv(v,k), px+s*qv(v,k+delta)]); err+=abs(e[0]-lo)+abs(e[1]-hi)
            if best is None or err<best[0]: best=(err,k,delta)
    err,k,delta=best
    print(f"{tier}: best k={k:.3f} delta={delta:.3f} mean edge err={err/(2*len(zs)):.1f} pts over {len(zs)} zones")
    for d,px,s,v,lo,hi in zs:
        e=sorted([px+s*qv(v,k), px+s*qv(v,k+delta)]); print(f"    {d} printed {lo}-{hi} predicted {e[0]:.0f}-{e[1]:.0f}")
    # centred variant: p_c +/- h points
    best2=None
    for c in np.arange(0.03,0.75,0.005):
        for h in (3,4,5):
            err=sum(abs(px+s*qv(v,c)-(lo+hi)/2) for d,px,s,v,lo,hi in zs)
            if best2 is None or err<best2[0]: best2=(err,c,h)
    print(f"    centred: p_c={best2[1]:.3f} mean centre err={best2[0]/len(zs):.1f} pts")
print("\n=== EVRange +50% candidates on 2026-09-01 (printed 29290) ===")
i=days.index(date(2026,9,1)); px=anchor_px(date(2026,9,1),540); ups,dns=dist(i,540,960,250,"raw"); ups=np.array(ups)
for p in (0.50,0.55,0.60,0.62,0.65): print(f"  anchor + p{int(p*100)}(up) = {px+qv(ups,p):.1f}")
print(f"  hi + 0.5*width = {29195+0.5*137:.1f}; anchor + 1.5*p25(up) = {px+1.5*qv(ups,0.25):.1f}; anchor + 2*p25 = {px+2*qv(ups,0.25):.1f}")
i=days.index(date(2026,8,28)); px=anchor_px(date(2026,8,28),540); ups,dns=dist(i,540,960,250,"raw"); ups=np.array(ups)
print(f"  08-28 for reference: anchor + p50(up) = {px+qv(ups,0.5):.1f}, +p60 = {px+qv(ups,0.6):.1f}")
