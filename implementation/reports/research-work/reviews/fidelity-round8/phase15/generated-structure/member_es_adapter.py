"""Member (K10) on the ES tape through the adapter's own generation path: the
prior ten sessions supplied as b02_prior_sessions, the composite minor HVNs
from _look_left_hvns, reactions from _look_left_reactions, pairs from
_pair_reasons; do his two drawn pairs come out before he traded them?"""
import sys
sys.argv = ["x"]
exec(open("/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/member_es_generated.py").read().split("m = ESMarket(")[0])
from decimal import Decimal
HIS = {"short": (Decimal("7558.75"), Decimal("7564")), "long": (Decimal("7544.75"), Decimal("7547.75"))}
DECIDE = {"short": ns_at("2026-08-03", "09:25"), "long": ns_at("2026-08-03", "09:30")}
prior_days = ["2026-07-31","2026-07-30","2026-07-29","2026-07-28","2026-07-27","2026-07-24","2026-07-23","2026-07-22","2026-07-21","2026-07-20"]
m = ESMarket("2026-08-03", "2026-07-31")
m.b02_prior_sessions = [{"date": d, "start": ns_at(d, "00:00") - 6*3600*NS, "end": ns_at(d, "16:00"), "known_at": ns_at(d, "16:00"), "window": Win(ns_at(d, "00:00") - 6*3600*NS, ns_at(d, "16:00"))} for d in prior_days]
hvns = member._look_left_hvns(m)
print("composite minor HVNs:", len(hvns), "parent", hvns[0]["parent"] if hvns else None, "near his pairs:", sorted({str(n["price"]) for n in hvns if any(lo - 2 <= n["price"] <= hi + 2 for lo, hi in HIS.values())}))
for side in ("short", "long"):
    reactions = [r for r in member._look_left_reactions(m, side) if int(r["known_at"]) <= DECIDE[side]]
    pairs = member._pair_reasons(reactions, hvns, member._kg1_levels(m), side)
    lo, hi = HIS[side]
    hits = [(str(r["price"]), et(int(r["at"])), str(n["price"])) for r, n, k in pairs if lo - 2 <= Decimal(str(r["price"])) <= hi + 2]
    print(f"{side}: reactions known {len(reactions)}, pairs {len(pairs)}, at his pair {HIS[side]}: {hits}")
