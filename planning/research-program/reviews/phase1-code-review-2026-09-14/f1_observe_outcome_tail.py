"""F1: historical_outcomes.observe_outcome never scans the final partial second
of its horizon, so a first-passage inside (end//SECOND*SECOND, end) is lost."""
import sys; sys.path.insert(0, '/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/code-review-phase1')
from harness import *
from decimal import Decimal as D
from trading_research.research.method_pack.historical_outcomes import observe_outcome
from trading_research.research.method_pack.measurement_outcomes import boundary_order

T0 = clock(DAY, '10:00')
DECISION = T0 + 123_456_789           # deliberately NOT second aligned
END = DECISION + 60 * MINUTE          # horizon end = 11:00:00.123456789

events = []
# one print per whole minute of the admitted window -> complete coverage
at = START
while at < END:
    events.append(raw(at, 100))
    at += MINUTE
# target print inside the final partial second [11:00:00.000, 11:00:00.1234...)
events.append(raw(END - 23_456_789, 101))
m = Market(events)

ep = {'candidate_id': 'repro-f1', 'research_verdict': 'pass', 'side': 'long',
      'method': 'SIRES', 'branch': 'dom_rejection', 'decision_at': DECISION,
      'geometry': {'entry': D('100'), 'stop': D('99'), 'target': D('101')}}

out = observe_outcome(m, ep)
print('observe_outcome.result      =', out['result'])
print('observe_outcome.resolved_at =', out['resolved_at'])
print('horizon end_ns              =', out['end_ns'], '  tail second starts at', END // SECOND * SECOND)
print('target print event_ns       =', END - 23_456_789, '(inside the horizon, before end_ns)')

b = boundary_order(m, ep, {'at': DECISION})
print('measurement boundary_order  =', b['result'], 'resolved_at', b.get('resolved_at_ns'))
print()
print('EXPECTED observe_outcome.result == target_observed (same as boundary_order);',
      'OBSERVED', repr(out['result']))
