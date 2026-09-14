"""F5: window_result measures coverage only over 09:30->market end, so a
formation window that is partly unobserved still reports
population_complete=True and a definite population_candidate_count."""
import sys; sys.path.insert(0, '/tmp/claude-1001/-workspace/a537e734-3756-42f3-86a8-d5066915b22a/scratchpad/code-review-phase1')
from harness import *
from trading_research.research.method_pack.historical_price_scanners import scan_green_vwap

ev = []
at = START
hole_lo, hole_hi = clock(DAY - __import__('datetime').timedelta(days=1), '22:00'), clock(DAY - __import__('datetime').timedelta(days=1), '23:00')
while at < END:
    if not (hole_lo <= at < hole_hi):      # one-hour hole inside the Asia formation (20:00-00:00)
        ev.append(raw(at, 100))
    at += MINUTE
for k in range(5):
    ev.append(raw(clock(DAY, '11:00') + k * MINUTE + SECOND, 105))
m = Market(ev)

print('coverage(whole window)     complete =', m.coverage(m.start, m.end)['observed_scope_complete'],
      ' holes =', len(m.coverage(m.start, m.end)['unknown_intervals']))
print('coverage(Asia 20:00-00:00) complete =',
      m.coverage(clock(DAY - __import__('datetime').timedelta(days=1), '20:00'), clock(DAY, '00:00'))['observed_scope_complete'])
res = scan_green_vwap(m, 'asia_london_vwap_return')
print('window_result.coverage     complete =', res['coverage']['observed_scope_complete'], '(09:30 -> end only)')
print('population_complete                 =', res['population_complete'])
print('population_candidate_count          =', res['population_candidate_count'])
print('omissions                           =', res['omissions'])
print('episode reference_frozen            =', res['episodes'][0]['values'].get('reference_frozen'))
print()
print('EXPECTED: an unobserved hour inside the Asia reference window makes the population incomplete')
print('OBSERVED: population_complete', res['population_complete'], 'with count', res['population_candidate_count'])
