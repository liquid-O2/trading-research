"""Bounded algebra/coverage audit of three existing VIX quote days; no strategy.

Assumptions deliberately differ from an official VIX/VVIX reconstruction.
Uses arithmetic quote screens, one-minute assumed availability lag, ACT/365,
09:30 New York settlement, and discount factors 1 and exp(-.05*T).
No actual receipt chronology, quote-condition certification, rates curve,
official venue filters, executable arbitrage, or statistical edge is claimed.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DATA = Path('/workspace/data/thetadata-opra')
QDIR = DATA/'opra__vix-options__quote-1m__dte60-full-chain'
OIDIR = DATA/'opra__vix-options__open-interest__dte60-full-chain'
DAYS = ['2020-01-02', '2023-05-02', '2026-09-03']

def normal_cdf(x):
    return .5*(1+math.erf(x/math.sqrt(2)))

def black(f,k,t,vol,d,right):
    if vol<=0:
        return d*max((f-k) if right=='CALL' else (k-f),0.)
    z=vol*math.sqrt(t); d1=math.log(f/k)/z+z/2; d2=d1-z
    return d*(f*normal_cdf(d1)-k*normal_cdf(d2)) if right=='CALL' else d*(k*normal_cdf(-d2)-f*normal_cdf(-d1))

def iv(price,f,k,t,d,right):
    intrinsic=black(f,k,t,0.,d,right)
    upper=d*(f if right=='CALL' else k)
    if not(intrinsic<price<upper) or t<=0:return None
    lo,hi=1e-9,10.
    if black(f,k,t,hi,d,right)<price:return None
    for _ in range(80):
        mid=(lo+hi)/2
        if black(f,k,t,mid,d,right)<price:lo=mid
        else:hi=mid
    return (lo+hi)/2

reports=[]; inputs=[]; total=0
for day in DAYS:
    file=QDIR/(day+'.parquet'); df=pd.read_parquet(file); total+=len(df)
    oi_file=OIDIR/(day+'.parquet'); oi=pd.read_parquet(oi_file)
    oi_dtes=(pd.to_datetime(oi.expiration)-pd.Timestamp(day)).dt.days
    inputs.append({'day':day,'quote_path':str(file),'quote_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
        'rows':len(df),'oi_rows':len(oi),'oi_sha256':hashlib.sha256(oi_file.read_bytes()).hexdigest(),
        'oi_min_dte':int(oi_dtes.min()),'oi_max_dte':int(oi_dtes.max()),
        'quote_conditions':{str(k):int(v) for k,v in df.bid_condition.value_counts().items()}})
    for hour in (15,17,19):
        cut=pd.Timestamp(f'{day}T{hour:02}:00:00Z'); available_end=cut-pd.Timedelta(minutes=1)
        # Latest actual row first; invalid latest quotes cannot revive an older valid quote.
        snap=df[df.ts_event<=available_end].sort_values('ts_event').drop_duplicates(['expiration','strike','right'],keep='last')
        age=(available_end-snap.ts_event).dt.total_seconds()
        eligible=snap[(age<=60)&(snap.bid>0)&(snap.ask>snap.bid)&(snap.bid_size>0)&(snap.ask_size>0)].copy()
        for expiry in sorted(snap.expiration.unique()):
            expiry_ts=pd.Timestamp(expiry).tz_localize('America/New_York')+pd.Timedelta(hours=9,minutes=30)
            t=(expiry_ts.tz_convert('UTC')-cut).total_seconds()/(365*86400)
            if t<=0:continue
            x=eligible[eligible.expiration==expiry].copy(); x['mid']=(x.bid+x.ask)/2
            calls=x[x.right=='CALL'];puts=x[x.right=='PUT']
            pairs=calls.merge(puts,on='strike',suffixes=('_c','_p'))
            rec={'day':day,'cut':str(cut),'expiry':str(expiry),'T_years':t,
                'total_contracts_at_cut':int((snap.expiration==expiry).sum()),'screened_contracts':len(x),
                'paired_strikes':len(pairs),'rate_scenarios':[]}
            if len(pairs)<3:
                rec['status']='insufficient_pairs';reports.append(rec);continue
            pairs['abs_cp']=(pairs.mid_c-pairs.mid_p).abs();pairs=pairs.sort_values(['abs_cp','strike'])
            a=pairs.iloc[0]
            for rate in (0.,.05):
                disc=math.exp(-rate*t);f=float(a.strike+(a.mid_c-a.mid_p)/disc)
                flo=float((pairs.strike+(pairs.bid_c-pairs.ask_p)/disc).max())
                fhi=float((pairs.strike+(pairs.ask_c-pairs.bid_p)/disc).min())
                vals=[]
                for row in x.itertuples():
                    if not ((row.right=='PUT' and row.strike<=f) or (row.right=='CALL' and row.strike>=f)):continue
                    v=iv(row.mid,f,row.strike,t,disc,row.right)
                    if v is not None:
                        vals.append({'strike':row.strike,'right':row.right,'iv':v,'log_moneyness':math.log(row.strike/f),
                                     'reprice_error':abs(black(f,row.strike,t,v,disc,row.right)-row.mid)})
                near=sorted(vals,key=lambda y:abs(y['log_moneyness']))
                atm=near[0] if near else None
                rec['rate_scenarios'].append({'rate_assumption':rate,'discount':disc,'forward_mid':f,
                    'forward_reference_strike':float(a.strike),'all_pair_interval_low':flo,'all_pair_interval_high':fhi,
                    'all_pair_intersection_nonempty':flo<=fhi,'otm_iv_count':len(vals),
                    'put_iv_count':sum(y['right']=='PUT' for y in vals),'call_iv_count':sum(y['right']=='CALL' for y in vals),
                    'nearest_supported_iv':atm,'max_reprice_error':max((y['reprice_error'] for y in vals),default=None)})
            rec['status']='illustrative_iv_computed';reports.append(rec)

summary={'created_at':datetime.now(timezone.utc).isoformat(),'scope':'bounded parity/Black-IV algebra and coverage; no model training/trades',
    'assumptions':__doc__,'quote_rows_read':total,'days':3,'decision_cuts':9,'expiry_cuts':len(reports),
    'cuts_with_iv':sum(r['status']=='illustrative_iv_computed' for r in reports),
    'inputs':inputs,'records':reports}
(OUT/'vix_feasibility.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
lines=['# Bounded VIX-option intraday feasibility audit','',
       'Completed audit of three existing quote-day files and their OI files; no fitted trading model, strategy replay or official VVIX replication.',
       '',f'Read **{total:,} quote rows**, at nine fixed UTC decision cuts across {len(reports)} expiry/cut combinations. Latest snapshots were selected before screening, so an invalid current quote cannot silently revive an old valid one.',
       '', 'The arithmetic screen requires positive bid, a strictly positive spread, positive displayed sizes and no more than one extra minute of snapshot age. Availability assumes a one-minute lag; actual receipts are absent. Quote condition codes, exchange-source rules and historical rates/settlement conventions are not certified here. Zero/invalid quotes remain excluded rather than interpolated into observations.',
       '', 'For each eligible expiry, infer a forward from the call/put pair with smallest absolute midpoint difference and retain the intersection of every eligible pair’s bid/ask parity interval. Fit individual OTM Black IVs by bisection under ACT/365, a declared 09:30 New York expiry assumption, and two discount-rate scenarios (0% and 5%). Rates are sensitivity assumptions, not historical rates. Nearest supported IV is not an interpolated ATM quote.',
       '', '| Day | Quote rows | OI rows | Actual OI DTE range |', '|---|---|---|---|']
for x in inputs:lines.append(f"| {x['day']} | {x['rows']:,} | {x['oi_rows']:,} | {x['oi_min_dte']}–{x['oi_max_dte']} |")
lines += ['', '| Cut UTC | Expiry | Paired strikes | Screened contracts | OTM IVs, 0% scenario | All-pair parity interval consistent? |','|---|---|---|---|---|---|']
for r in reports:
    a=r['rate_scenarios'][0] if r['rate_scenarios'] else {}
    lines.append(f"| {r['cut']} | {r['expiry']} | {r['paired_strikes']} | {r['screened_contracts']}/{r['total_contracts_at_cut']} | {a.get('otm_iv_count',0)} | {a.get('all_pair_intersection_nonempty','unavailable')} |")
lines += ['', 'The directory name `dte60-full-chain` does not bound every OI expiry in these actual files. Quote eligibility and OI eligibility must be audited separately. This small deterministic selection shows which inputs are calculable in these snapshots, not representativeness across the archive.',
          '', 'An empty parity intersection means the entire screened set is inconsistent under that rate/synchronization scenario. A robust illustrative midpoint IV can still be calculated, but the inconsistency must reach O21 and be resolved or modeled before any certified surface is used. Small repricing error checks numerical inversion only; it does not establish a true IV, valid quote or predictive benefit.',
          '', 'Next research gate: certify quote/contract/source semantics and historical availability, run broader prespecified coverage cohorts, quantify bid/ask/rate/clock uncertainty, and then compare the C15/C16 specialists against physical-volatility and daily-VX baselines. VIX signed flow remains unavailable from these quote/OI files.',
          '', 'Detailed assumptions, numerical outputs and source hashes: [JSON evidence](vix_feasibility.json). Reproduction: [audit script](audit_vix_surface_feasibility.py).']
(OUT/'VIX_FEASIBILITY.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:summary[k] for k in ['quote_rows_read','decision_cuts','expiry_cuts','cuts_with_iv']}))
