"""C6 — SIRES microbalance_break never compares the break with the larger auction.

[K2345] pp.4-7 / wiki: "Within the established directional auction, a small price
balance forms; price shows strength and breaks it; use the opposite side of that
structure for risk and the pre-existing HTF objective."
historical_flow.py:337 selects the trigger with sg*(C-boundary)>0 and line 346
then binds `breakout_in_thesis_direction` to the same expression, and
`stop_behind_microbalance` to the stop it just constructed.  Both operands are
true by construction: the long and the short break of the SAME microbalance
inside the SAME larger balance both satisfy them, so the source's directional
gate carries no information.
"""
from harness import *
from trading_research.research.method_pack.historical_flow import scan_microbalance

def balance(identity,lo,hi,start,end):
    return {'id':identity,'low':D(str(lo)),'high':D(str(hi)),'width':D(str(hi))-D(str(lo)),
            'start':start,'end':end,'known_at':end,
            'pivots':[{'id':identity+':p%d'%i} for i in range(4)],'selection':'A2-BALANCE'}

ev=[raw(t,100.0) for t in range(at('06:00'),at('09:30'),60*SECOND)]
ev+=[raw(t,100.0) for t in range(at('09:30'),at('10:00'),60*SECOND)]
ev+=[raw(at('10:00')+i*SECOND,102.0) for i in range(5)]      # up-break of the micro band
ev+=[raw(t,102.0) for t in range(at('10:01'),at('10:30'),60*SECOND)]
ev+=[raw(at('10:30')+i*SECOND,97.0) for i in range(5)]       # down-break of the same band
ev+=[raw(t,97.0) for t in range(at('10:31'),at('16:00'),60*SECOND)]

htf=balance('balance:htf',90,110,at('06:00'),at('08:00'))    # larger, earlier auction
micro=balance('balance:micro',99,101,at('08:30'),at('09:00'))
out=scan_microbalance(Market(ev),'microbalance_break',[htf,micro])
for e in out['episodes']:
    v=e['values']
    print(f"side={e['side']:5s} target={e['geometry']['target']} (htf edge)"
          f"  breakout_in_thesis_direction={v['breakout_in_thesis_direction']}"
          f"  directional_strength={v['directional_strength']}"
          f"  stop_behind_microbalance={v['stop_behind_microbalance']}")
print('Both directions out of one microbalance inside one larger balance bind the same True.')
