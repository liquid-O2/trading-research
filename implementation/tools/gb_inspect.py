"""For each Green Bird ticket: the opportunities of its clock window in time order (from the lab's scan cache), which of them carries a fill that matches the ticket, and what the traded list took."""
import json, pickle, sys, importlib.util
from pathlib import Path
from decimal import Decimal
sys.path.insert(0, "tools")
spec=importlib.util.spec_from_file_location("policy_lab","tools/policy_lab.py"); lab=importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
replay=lab._module("replay_jj_gb")
from trading_research.research.rule_discovery.source_adapters import green_b02 as gb
from trading_research.research.rule_discovery.source_adapters.trade_selection import _episode_key
from trading_research.research.method_pack.clocks import ns_to_et
cache=Path("/workspace/.scratch/a537e734/lab/cache/GB")/lab.scanner_tag("GB")
markets=replay.Markets()
hm=lambda ns: ns_to_et(int(ns)).strftime("%H:%M")
examples=json.loads(replay.EXAMPLES.read_text())["examples"]
only=set(sys.argv[1].split(",")) if len(sys.argv)>1 else None
for ex in examples:
    if not ex["id"].startswith("GB") or not ex.get("inside_tape") or (only and ex["id"] not in only): continue
    for entry in gb.proper_entries(ex):
        day=replay._session_date(entry).isoformat(); m=markets.get(day)
        body=pickle.loads((cache/f"{day}.pkl").read_bytes())
        eps=[e for e in body["episodes"] if e.get("research_verdict")=="pass"]
        window=gb._printed_window_for(m, entry)
        # the clock the ticket sits in
        spans=[(int(gb._at(m,a,ao)),int(gb._at(m,b,bo))) for shift in gb.TRADE_WINDOWS.values() for a,ao,b,bo,_c in shift]
        clock=next(((s,e) for s,e in spans if s<=window[0]<e), None)
        print(f'\n=== {ex["id"]} {entry.get("time_et")} {entry["side"]} {entry.get("price")} [{entry.get("branch")}] clock {hm(clock[0])}-{hm(clock[1])}' if clock else f'\n=== {ex["id"]} outside every clock')
        if clock is None: continue
        groups={}
        for e in eps:
            if e["side"]!=entry["side"]: continue
            at=int(e["decision_at"])
            if not (clock[0]<=at<clock[1]): continue
            groups.setdefault(_episode_key(e),[]).append(e)
        rows=[]
        for key,fills in groups.items():
            match=gb.match_entry(m, fills, entry)
            first=min(fills,key=lambda e:int(e["decision_at"]))
            rows.append((int(first["decision_at"]), key, fills, replay.strict_10(entry, match)))
        rows.sort(key=lambda r:r[0])
        for n,(at,key,fills,ok) in enumerate(rows):
            modes=" ".join(f'{hm(f["decision_at"])}:{(f["values"].get("confirmation_mode") or "")[:12]}@{f["geometry"]["entry"]}' for f in sorted(fills,key=lambda e:int(e["decision_at"]))[:5])
            print(f'  {"<<HIS" if ok else "     "} #{n+1:2d} {key[0]:22s} {str(key[3])[:20]:20s} cyc {str(key[5])[:4]:4s} | {modes}')
