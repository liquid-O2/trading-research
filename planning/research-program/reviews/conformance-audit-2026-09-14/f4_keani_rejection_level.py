"""C4 — KEANI step 2 tests the developing value-area LOW, not POC / prior VAH.

[AVG] p.21: "Value opening and building higher is the market telling you buyers
are in control and sellers are getting exhausted.  Price will probably reject
off the POC or the previous day's value area high."
historical_auction_scanners.py:258-260 implements
  rejection = higher and row['C'] is not None and row['L']<=current['val'] and row['C']>current['val']
-- a wick into the CURRENT DEVELOPING VALUE-AREA LOW.  Two sessions identical
except for the depth of one wick: the source's rejection off the developing POC
starts nothing; the same candle taken down to the developing VAL starts the
whole Keani sequence.
"""
from harness import *
from trading_research.research.method_pack.historical_auction_scanners import scan_keani

BELL=[(101.5,20),(101.75,40),(102.0,80),(102.25,120),(102.5,160),(102.75,200),(103.0,240),
      (103.25,200),(103.5,160),(103.75,120),(104.0,80),(104.25,40),(104.5,20)]
APX=[99.75,100.0,100.0,100.25]

def session(dip=None):
    ev=[raw(t,100.0) for t in range(at('06:00'),at('09:30'),60*SECOND)]
    for i,t in enumerate(range(at('09:30'),at('10:00'),10*SECOND)):
        ev.append(raw(t,APX[i%4],size=2))                       # A period 99.75-100.25
    for i,(px,sz) in enumerate(BELL):                            # one print per minute: L==C, cannot fire
        ev.append(raw(at('10:00')+i*60*SECOND,px,size=sz))
    for t in range(at('10:13'),at('10:31'),60*SECOND):
        ev.append(raw(t,104.75,size=1))
    if dip is not None:                                          # the one two-sided candidate candle
        ev+=[raw(at('10:31')+1,104.75),raw(at('10:31')+2,D(str(dip))),raw(at('10:31')+3,105.0)]
    for t in range(at('10:32'),at('16:00'),60*SECOND):
        ev.append(raw(t,105.25,size=1))
    return ev

dev=Market(session()).profile(at('09:30'),at('10:31'))
print('developing profile at 10:31  poc=',dev['poc'],' val=',dev['val'],' vah=',dev['vah'])
for label,dip in (('SOURCE stage - rejection off the developing POC',dev['poc']),
                  ("CODE gate    - same candle wicked to the developing VAL",dev['val'])):
    e=scan_keani(Market(session(float(dip))),'source_long')['episodes'][0];v=e['values']
    print(f'  {label} ({dip}): builds_higher={v["developing_value_builds_higher"]}'
          f' source_rejection_observed={v["source_rejection_observed"]}'
          f' observation_at={"none" if v["observation_at"] is None else "10:31"}')
