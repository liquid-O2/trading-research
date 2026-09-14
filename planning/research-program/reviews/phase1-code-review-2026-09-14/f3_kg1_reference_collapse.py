"""F3: scan_sires de-duplicates references by their pivot-id tuple. References
that carry no pivots (KG1 levels) all hash to the same empty key, so only the
first supplied KG1 level ever produces an episode per side."""
import sys; sys.path.insert(0, '/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/code-review-phase1')
import json, pathlib
from harness import *
from trading_research.research.method_pack.native_resolution import file_digest
from trading_research.research.method_pack.historical_flow import scan_sires

S = pathlib.Path(__file__).parent
levels = [{'id': 'kg1-a', 'known_at': clock(DAY, '09:00'), 'instrument_id': 17, 'low': '100', 'high': '100.5'},
          {'id': 'kg1-b', 'known_at': clock(DAY, '09:00'), 'instrument_id': 17, 'low': '120', 'high': '120.5'}]
path = S / 'kg1.json'
path.write_text(json.dumps(levels))
digest = file_digest(path)
records = {'kg1': [dict(r, evidence_path=str(path), evidence_sha256=digest) for r in levels]}

ev = []
at = START
while at < END:                                    # complete coverage baseline at 100.25
    ev.append(raw(at, '100.25'))
    at += MINUTE
# distinct visits far outside both bands, then an exact visit to level B
for k in range(40):
    ev.append(raw(clock(DAY, '10:00') + k * MINUTE + SECOND, '150'))
for k in range(40):
    ev.append(raw(clock(DAY, '11:00') + k * MINUTE + SECOND, '120.25'))
m = Market(ev, records=records)

res = scan_sires(m, 'kg1_retest')
print('supplied KG1 references     :', [r['id'] for r in m.supplied('kg1', m.end)])
print('episodes emitted            :', len(res['episodes']))
print('reference ids in episodes   :', sorted({e['reference_id'] for e in res['episodes']}))
print('sides in episodes           :', sorted({e['side'] for e in res['episodes']}))
print()
print('EXPECTED: both kg1-a and kg1-b enumerate their own long/short populations (up to 4 episodes)')
print('OBSERVED: only', sorted({e["reference_id"] for e in res["episodes"]}), 'is ever reached')
