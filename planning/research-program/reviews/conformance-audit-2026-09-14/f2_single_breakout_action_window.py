"""C2 — JJ-TBR single_extended/single_purged admit EQ entries until 16:00.

[TBR] p.12 (Single Breakout Model): "you want to be in the trade before 10am an
look to close position around 9:40-9:50 window" and "after 10am all interest in
being in a position is not longer present.  Price tends to consolidate all the
way through lunch/PM session."  historical_price_scanners.py:72 overrides the
action window with action_end = 16:00 for single_extended, single_purged,
internal_rotation and extension_reaction, so a first EQ contact in the afternoon
is still emitted as a candidate.
"""
from harness import *
from trading_research.research.method_pack.historical_price_scanners import scan_jumbo

ev=[]
for t in range(at('06:00'),at('09:00'),60*SECOND):        # formation: 99/101, never EQ
    ev.append(raw(t,101.0 if (t//(60*SECOND))%2 else 99.0))
ev+=[raw(t,101.5) for t in range(at('09:00'),at('16:00'),60*SECOND)]   # held above EQ
ev+=[raw(at('14:00')+i,100.0) for i in range(1,4)]        # first EQ contact, 14:00

m=Market(ev)
for branch in ('single_extended','single_purged','internal_rotation'):
    out=scan_jumbo(m,branch)
    for e in out['episodes']:
        touch=e['values'].get('touch_at');decision=e['decision_at']
        print(branch,'side',e['side'],'touch_at=',(touch-at('09:30'))//(60*SECOND),'min after 09:30',
              'decision_at=',(decision-at('09:30'))//(60*SECOND),'min after 09:30','verdict',e['research_verdict'])
    if not out['episodes']:print(branch,'N=0')
