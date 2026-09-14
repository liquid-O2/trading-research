"""F2: an empty observation interval is certified as fully observed, so
historical_assembly.absent() answers False ("definitely did not happen")
from zero minutes of evidence, turning unknown episodes into fails."""
import sys; sys.path.insert(0, '/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/code-review-phase1')
from harness import *
from decimal import Decimal as D
from trading_research.research.method_pack.historical_assembly import absent
from trading_research.research.method_pack.measurement_outcomes import rounded_coverage
from trading_research.research.method_pack.historical_price_scanners import scan_green_vwap

# --- direct: coverage of a zero-length interval ------------------------------
m0 = Market([raw(START + i * MINUTE, 100) for i in range(60)])
t = clock(DAY, '10:00')
print('EventWindow.coverage(t,t)  =', m0.coverage(t, t))
print('absent(m,t,t)              =', absent(m0, t, t), '   (False == certified absence)')
print('rounded_coverage(m,t,t)    =', rounded_coverage(m0, t, t)['observed_scope_complete'],
      '  <- measurement_outcomes guards this case, coverage() does not')
print()

# --- reachable in an accepted scanner: GB-VWAP breakout on the last 5m bar ---
ev = []
at = START
while at < END:                       # complete minute coverage
    ev.append(raw(at, 100))
    at += MINUTE
# Asia 20:00-00:00 and London 02:00-05:00 highs stay at 100; break above at 15:55-16:00
for k in range(5):
    ev.append(raw(clock(DAY, '15:55') + k * MINUTE + SECOND, 105))
m = Market(ev)
res = scan_green_vwap(m, 'asia_london_vwap_return')
e = res['episodes'][0]
br = e['values']
print('breakout_at                =', br['breakout_at'], ' (== market end', m.end, ')')
print('continuation_context       =', br['continuation_context'])
print('research_verdict           =', e['research_verdict'])
print()
print('EXPECTED: no observable post-breakout window -> continuation_context None -> verdict unknown')
print('OBSERVED: continuation_context', br['continuation_context'], '-> verdict', e['research_verdict'])
