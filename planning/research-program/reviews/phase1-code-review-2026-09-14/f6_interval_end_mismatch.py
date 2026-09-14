"""F6: within measure_setup, interval_extrema uses (start,end] while
boundary_order scans [start,end). A print exactly at the horizon end is an
excursion but can never be a first passage."""
import sys; sys.path.insert(0, '/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/code-review-phase1')
from harness import *
from decimal import Decimal as D
from trading_research.research.method_pack.measurement_outcomes import interval_extrema, boundary_order, measure_setup

DEC = clock(DAY, '10:00')
HOR = DEC + 60 * MINUTE
ev = []
at = START
while at < END:
    ev.append(raw(at, 100))
    at += MINUTE
ev = [r for r in ev if r['event_ns'] != HOR]     # keep exactly one print at the horizon end
ev.append(raw(HOR, 101))
m = Market(ev)

ep = {'candidate_id': 'repro-f6', 'decision_at': DEC, 'side': 'long', 'method': 'SIRES',
      'branch': 'dom_rejection', 'trigger': {},
      'geometry': {'entry': D('100'), 'stop': D('99'), 'target': D('101')}}

x = interval_extrema(m, DEC, HOR)
b = boundary_order(m, ep, {'at': DEC})
print('interval_extrema(DEC,HOR).high  =', x['high'], ' <- print at exactly end_ns is included')
print('boundary_order.result           =', b['result'], ' resolved_at', b['resolved_at_ns'])
ms = measure_setup(m, ep)
h60 = [r for r in ms['horizons'] if r['minutes'] == 60][0]
print('measure_setup h=60 favorable    =', h60['favorable_points'], 'points (target distance 1)')
print('measure_setup boundary result   =', ms['boundary']['result'])
print()
print('EXPECTED: one convention for the closing endpoint across the same measurement record')
print('OBSERVED: extrema say the target price traded; first passage says it expired')
