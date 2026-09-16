"""RA-1 negative control: with no override installed, every family's B0.2 scan
must serialise to the same bytes as before the speedup. Run once per worktree
and compare the printed digests."""
import hashlib, json, sys
from trading_research.research.rule_discovery import search
from trading_research.research.rule_discovery.source_adapters.common import install_write_guard

install_write_guard()
out = {}
for day in search.CONTROL_DATES:
    market = search.load_b02_market(day, warm=False)
    for family in search.B02_FAMILIES:
        branch = search.CONTROL_BRANCH[family]
        document = search.scan_b02_baseline(market, family, branch)
        blob = search.serialize_scan_bytes(document)
        out[f"{day}|{family}|{branch}"] = {
            "sha256": hashlib.sha256(blob).hexdigest(),
            "episodes": len(document.get("episodes") or []),
        }
print("RA1 " + json.dumps(out, sort_keys=True), flush=True)
