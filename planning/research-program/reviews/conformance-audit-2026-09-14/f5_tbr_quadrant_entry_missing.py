"""C5 — JJ-TBR: `entry_at_eq_or_quadrant` only ever accepts EQ.

[TBR] p.12: "In the case of having an extended overnight range, the EQ or
quadrants become our levels on interest"; Scenario #2 "we can anticipate price
expanding from the inner range levels (EQ, Quadrants)".
A2-TBR-PROJ declares internal = ['.25','.5','.75'], but
historical_price_scanners.py:82-83 sets location = [(low+high)/2]*2 for
single_extended, single_purged and internal_rotation, and nothing in the pack
reads tbr_projection['internal'].  A session whose only inner-range contact is
the 0.25 quadrant produces no candidate at all.
"""
from harness import *
from trading_research.research.method_pack.historical_price_scanners import scan_jumbo
from trading_research.research.method_pack.branch_coverage import setting

print("A2-TBR-PROJ internal levels declared:",setting('tbr_projection')['internal'])

def session(touch_px):
    ev=[]
    for t in range(at('06:00'),at('09:00'),60*SECOND):        # formation 96..104, EQ=100, Q1=98
        ev.append(raw(t,104.0 if (t//(60*SECOND))%2 else 96.0))
    ev+=[raw(t,103.0) for t in range(at('09:00'),at('16:00'),60*SECOND)]
    ev+=[raw(at('11:00')+i,D(str(touch_px))) for i in range(1,4)]
    return ev

for label,px in (('lower quadrant (0.25W) contact only  -> source: a level of interest',98.0),
                 ('EQ (0.50W) contact                   -> the only level the code reads',100.0)):
    for branch in ('single_extended','internal_rotation'):
        out=scan_jumbo(Market(session(px)),branch)
        print(f'  {label}  {branch}: N_observed={out["N_observed"]}')
