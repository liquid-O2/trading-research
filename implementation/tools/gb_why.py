"""For every Green Bird ticket not on the traded list: what happened to HIS opportunity (not in the traded pool, or skipped by the selector and why, and which trade was in the way)."""
import json, pickle, sys, importlib.util
from pathlib import Path
sys.path.insert(0, "tools")
spec=importlib.util.spec_from_file_location("policy_lab","tools/policy_lab.py"); lab=importlib.util.module_from_spec(spec); spec.loader.exec_module(lab)
replay=lab._module("replay_jj_gb")
from trading_research.research.rule_discovery.source_adapters import green_b02 as gb, trade_selection as ts
from trading_research.research.rule_discovery.source_adapters.trade_selection import _episode_key
from trading_research.research.method_pack.clocks import ns_to_et
cache=Path("/workspace/.scratch/a537e734/lab/cache/GB")/lab.scanner_tag("GB")
markets=replay.Markets(); hm=lambda ns: ns_to_et(int(ns)).strftime("%H:%M")
examples=json.loads(replay.EXAMPLES.read_text())["examples"]
orig=ts.select_session_trades
for ex in examples:
    if not ex["id"].startswith("GB") or not ex.get("inside_tape"): continue
    for entry in gb.proper_entries(ex):
        day=replay._session_date(entry).isoformat(); m=markets.get(day)
        body=pickle.loads((cache/f"{day}.pkl").read_bytes())
        eps=[e for e in body["episodes"] if e.get("research_verdict")=="pass"]
        groups={}
        for e in eps:
            if e["side"]==entry["side"]: groups.setdefault(_episode_key(e),[]).append(e)
        his={k for k,f in groups.items() if replay.strict_10(entry, gb.match_entry(m,f,entry))}
        calls=[]
        def wrapped(episodes,*a,**k):
            if k.get("windows"):
                tr=[]; k["trace"]=tr; r=orig(episodes,*a,**k); calls.append((list(episodes),r,tr)); return r
            return orig(episodes,*a,**k)
        gb.select_session_trades=wrapped
        sel=gb.selection_for(m, eps)
        gb.select_session_trades=orig
        taken_keys=set(); 
        ok=replay.strict_10(entry, gb.match_entry(m, replay._selection_for_session(gb, m, body["episodes"], body["read"]).get("executed_episodes") or [], entry))
        line=f'{"EXEC" if ok else "MISS"} {ex["id"]:18s} {str(entry.get("time_et")):14s} {entry["side"]:5s} his opportunities: {len(his)}'
        if not ok:
            reasons=[]
            for pool,r,tr in calls:
                in_pool=[e for e in pool if _episode_key(e) in his]
                if not in_pool: continue
                ids={e.get("candidate_id") for e in in_pool}
                for x in tr:
                    if x["candidate_id"] in ids:
                        blockers=[f'{hm(t["decision_at"])}{t["side"][0]}:{t["branch"][:9]}:{t["outcome"][:1]}' for t in r["entries"] if int(t["decision_at"])<=x["decision_at"]][-2:]
                        reasons.append(f'{hm(x["decision_at"])} {x["skipped"]} (before it: {" ".join(blockers)})')
            if not his: reasons=["no fill of any same-side opportunity matches the ticket (scan or record)"]
            elif not reasons: reasons=["his opportunity never reached the traded pool (segment branches or fill modes)"]
            line+=" | "+"; ".join(reasons[:3])
        print(line)
