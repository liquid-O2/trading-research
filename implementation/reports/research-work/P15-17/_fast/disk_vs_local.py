"""Open-item evidence: is the in-process B0.2 scan identical to the P15-16A job on disk?"""
import hashlib, json, sys
from trading_research.research.rule_discovery import search, search_run

day = sys.argv[1]
resolved = [r for r in search.resolve_bank() if r.supported]
branches = sorted({(r.family, r.branch) for r in resolved})
market = search.load_b02_market(day, warm=True, branches=branches)
warm = market._p15_17_warm["baselines"]
same = diff = missing = 0
rows = []
for family, branch in branches:
    doc, prov = search_run._load_b02_document(list(search_run.B02_ROOTS_DEFAULT), day, family, branch)
    local = warm.get((family, branch))
    if doc is None or local is None:
        missing += 1
        continue
    a = search.serialize_scan_bytes(search_run.ensure_candidate_ids(dict(doc), family, branch))
    b = search.serialize_scan_bytes(search_run.ensure_candidate_ids(dict(local), family, branch))
    if a == b:
        same += 1
    else:
        diff += 1
        rows.append(f"{family}:{branch} episodes disk={len(doc.get('episodes') or [])} local={len(local.get('episodes') or [])}")
print(f"DISKVSLOCAL {day} branches={len(branches)} identical={same} different={diff} missing={missing}")
for r in rows[:8]:
    print("   ", r)
