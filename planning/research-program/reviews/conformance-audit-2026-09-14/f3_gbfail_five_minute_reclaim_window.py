"""C3 — GB-FAIL only ever inspects the five-minute bar that contains the sweep.

[GB] p.25: "I wait for the 5 min close back below the PDL after sweeping above
it" / "The key for me is getting a 5 min close below, once I got it I waited a
few points and entered short."  historical_price_scanners.py:219-223 computes
confirmation_end as the next aligned five-minute boundary after the sweep bar's
start and reads exactly one candle, the one the sweep sits in.  A sweep whose
own candle closes outside and whose NEXT five-minute candle closes back inside
-- the source's own wording -- is scored fail, and no later close is read.
"""
from harness import *
from trading_research.research.method_pack.historical_price_scanners import scan_green_failure

def session(reclaim_in_sweep_candle):
    ev=[raw(t,100.0) for t in range(at('06:00'),at('09:00'),60*SECOND)]
    for t in range(at('09:00'),at('10:00'),60*SECOND):                 # NYAM box 99..101
        ev.append(raw(t,101.0 if (t//(60*SECOND))%2 else 99.0))
    ev+=[raw(t,100.0) for t in range(at('10:10'),at('16:00'),60*SECOND)]
    ev+=[raw(at('10:01'),102.0),raw(at('10:02'),102.5)]                # strict sweep above 101
    if reclaim_in_sweep_candle:
        ev+=[raw(at('10:03'),100.0),raw(at('10:04'),100.0)]            # closes back inside at 10:05
        ev+=[raw(t,100.0) for t in range(at('10:05'),at('10:10'),60*SECOND)]
    else:
        ev+=[raw(t,101.5) for t in range(at('10:03'),at('10:05'),60*SECOND)]   # 10:00-10:05 closes ABOVE
        ev+=[raw(t,100.0) for t in range(at('10:05'),at('10:10'),60*SECOND)]   # 10:05-10:10 closes BELOW
    return ev

for label,flag in (('source wording: reclaim on the NEXT five-minute close (10:05-10:10)',False),
                   ('code-admissible: reclaim inside the sweep candle (10:00-10:05)',True)):
    out=scan_green_failure(Market(session(flag)),'nyam_box')
    print(label)
    for e in out['episodes']:
        v=e['values']
        if e['side']!='short':continue
        print('   side short reference_px',v['reference_px'],'confirm_close',v['confirm_close'],
              'confirm_at=10:%02d'%(((v['confirm_at']-at('10:00'))//(60*SECOND))),'verdict',e['research_verdict'],
              'failed',[f for f in e['failed']][:3])

