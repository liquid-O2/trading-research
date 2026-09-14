"""F4: scan_green_failure computes max()/min() over m.bars(trigger.start,
confirmation_end) without guarding the empty case. A sweep bar whose members
become available after the aligned 5-minute boundary is filtered out of that
read, so the sweep-extreme computation raises and kills the branch job."""
import sys; sys.path.insert(0, '/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/code-review-phase1')
from harness import *
from trading_research.research.method_pack.historical_price_scanners import scan_green_failure

ev = []
at = START
while at < END:
    ev.append(raw(at, 100))          # baseline: nyam box 09:00-10:00 high == 100
    at += MINUTE
# sweep above the box high inside the LAST minute of the 10:00-10:05 block,
# with provider receive time after that block's close
sweep = clock(DAY, '10:04') + 30 * SECOND
ev.append(raw(sweep, 101, ts_recv=clock(DAY, '10:06')))
m = Market(ev)

bar = [b for b in m.bars(clock(DAY, '10:00'), clock(DAY, '11:00')) if b['H'] == 101]
print('sweep bar known_at        =', bar[0]['known_at'], '> confirmation_end', clock(DAY, '10:05'))
print('m.bars(10:04,10:05) size  =', len(m.bars(clock(DAY, '10:04'), clock(DAY, '10:05'))),
      ' (empty: the read is bounded by confirmation_end)')
try:
    scan_green_failure(m, 'nyam_box')
    print('no error (unexpected)')
except Exception as exc:
    print('OBSERVED', type(exc).__name__, ':', exc)
    print('EXPECTED: the branch records an availability omission, not an aborted job')
