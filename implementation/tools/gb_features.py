"""Green Bird: every opportunity of each ticket's clock (both sides), with his stated discriminators, his own marked."""
import json, pickle, sys, importlib.util, statistics as st
from pathlib import Path
sys.path.insert(0, "tools")
spec=importlib.util.spec_from_file_location("policy_lab","tools/policy_lab.py"); lab=importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
replay=lab._module("replay_jj_gb")
from trading_research.research.rule_discovery.source_adapters import green_b02 as gb
from trading_research.research.rule_discovery.source_adapters.trade_selection import _episode_key
from trading_research.research.method_pack.clocks import ns_to_et
cache=Path("/workspace/.scratch/a537e734/lab/cache/GB")/lab.scanner_tag("GB")
markets=replay.Markets(); hm=lambda ns: ns_to_et(int(ns)).strftime("%H:%M")
examples=json.loads(replay.EXAMPLES.read_text())["examples"]
out=[]
for ex in examples:
    if not ex["id"].startswith("GB") or not ex.get("inside_tape"): continue
    for entry in gb.proper_entries(ex):
        day=replay._session_date(entry).isoformat(); m=markets.get(day)
        body=pickle.loads((cache/f"{day}.pkl").read_bytes())
        eps=gb._traded_fills([e for e in body["episodes"] if e.get("research_verdict")=="pass" and str((e.get("values") or {}).get("reference_kind",""))!="ny_box_09_10_running"])
        window=gb._printed_window_for(m, entry)
        spans=[(int(gb._at(m,a,ao)),int(gb._at(m,b,bo))) for shift in gb.TRADE_WINDOWS.values() for a,ao,b,bo,_c in shift]
        clock=next(((s,e) for s,e in spans if s<=window[0]<e), None)
        if clock is None: continue
        bars=[r for r in m.bars(int(m.start), clock[1], 60) if r.get("H") is not None]
        groups={}
        for e in eps:
            if clock[0]<=int(e["decision_at"])<clock[1]: groups.setdefault(_episode_key(e),[]).append(e)
        levels=sorted({float(e["values"]["reference_px"]) for e in body["episodes"] if (e.get("values") or {}).get("reference_px") is not None and not str(e["values"].get("reference_kind","")).endswith("_running")})
        for key,fills in groups.items():
            first=min(fills,key=lambda e:int(e["decision_at"])); at=int(first["decision_at"]); v=first["values"]; side=first["side"]; s=1 if side=="long" else -1
            seen=[r for r in bars if int(r.get("known_at") or r["end"])<=at]
            hi=max(float(r["H"]) for r in seen); lo=min(float(r["L"]) for r in seen); px=float(first["geometry"]["entry"])
            pos=(px-lo)/(hi-lo) if hi>lo else 0.5
            base=int(m.at("09:30")) if at>=int(m.at("09:30")) else int(m.start)
            ref_bar=next((r for r in seen if int(r["start"])>=base and r.get("O") is not None), None)
            move=None if ref_bar is None else (px-float(ref_bar["O"]))
            level=float(v["reference_px"]) if v.get("reference_px") is not None else px
            ext=float(v["sweep_extreme"]) if v.get("sweep_extreme") is not None else level
            co=[l for l in levels if abs(l-level)>0.01 and min(level,ext)-2<=l<=max(level,ext)+2]
            his=(first["side"]==entry["side"]) and replay.strict_10(entry, gb.match_entry(m,fills,entry))
            out.append({"ticket":ex["id"]+" "+str(entry.get("time_et")),"his":his,"at":hm(at),"side":side,"branch":first["branch"],"kind":str(v.get("reference_kind")),"cycle":v.get("cycle"),
                        "extreme_side":round(pos if side=="short" else 1-pos,2),"fade_of_move":None if move is None else round(-s*move,1),"co_swept":len(co),"depth":float(v["sweep_depth"]) if v.get("sweep_depth") is not None else None,
                        "mins_in_clock":round((at-clock[0])/6e10,1)})
json.dump(out, open("/workspace/.scratch/a537e734/lab/gb_features.json","w"), default=str)
his=[r for r in out if r["his"]]; oth=[r for r in out if not r["his"]]
print(len(his),"his opportunity rows;",len(oth),"others")
for k in ("extreme_side","fade_of_move","co_swept","depth","mins_in_clock"):
    a=[r[k] for r in his if r[k] is not None]; b=[r[k] for r in oth if r[k] is not None]
    print(f"{k:14s} his median {st.median(a):7.2f} (q25 {sorted(a)[len(a)//4]:.2f})   others median {st.median(b):7.2f}")
import collections
print("kind  his:",collections.Counter(r["kind"] for r in his).most_common(12)); print("kind  oth:",collections.Counter(r["kind"] for r in oth).most_common(14))
print("cycle his:",collections.Counter(str(r["cycle"]) for r in his).most_common(6),"| oth:",collections.Counter(str(r["cycle"]) for r in oth).most_common(6))
