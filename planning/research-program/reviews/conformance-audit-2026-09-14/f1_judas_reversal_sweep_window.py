"""C1 — JJ-TBR judas_reversal: the range-edge sweep is forced into 09:40-09:50.

[TBR] p.8: "the judas trades from 9:30 to the reversal window and the actual
reversal trade between the 9:40 and 9:50" -- the false breakout (edge sweep)
happens BEFORE the 09:40-09:50 window; only the reversal entry is inside it.
historical_price_scanners.py:71 sets action_start/action_end = 09:40/09:50 and
line 90 searches the sweep only inside those rows, so a 09:35 sweep with a
09:42 reversal produces no candidate at all.
"""
from harness import *
from trading_research.research.method_pack.historical_price_scanners import scan_jumbo

def session(sweep_text):
    ev=[]
    ev+=minute_series(at('06:00'),at('09:00'))            # 6-9 formation, flat 100
    ev+=[raw(at('07:00'),101.0),raw(at('08:00'),99.0)]    # range high 101 / low 99
    ev+=minute_series(at('09:00'),at('16:00'))
    s=at(sweep_text)
    ev+=[raw(s+1,101.5),raw(s+2,101.75)]                  # strict sweep above 101
    for k in range(1,9):                                  # reversal back down through EQ
        ev.append(raw(s+k*30*SECOND,D('100.5')-D('.25')*k))
    return ev

for label,t in (('source sequence: sweep 09:35, reversal window 09:40-09:50','09:35'),
                ('code-admissible: sweep moved inside 09:40-09:50','09:42')):
    m=Market(session(t))
    out=scan_jumbo(m,'judas_reversal')
    print(f'{label}: N_observed={out["N_observed"]} omissions={[o.get("reason") for o in out["omissions"]]}')
    for e in out['episodes']:
        print('   side',e['side'],'sweep_at',e['values'].get('sweep_at'),'source_time_window',
              e['values'].get('source_time_window'),'verdict',e['research_verdict'])
