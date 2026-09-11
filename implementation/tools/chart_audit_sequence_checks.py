"""Read-only dated event checks; do not write production tables or new inputs."""
import sys,json
from pathlib import Path
from datetime import date
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'implementation/src'),str(ROOT/'implementation/tools')]
import chart_audit_plots as p
from trading_research.research.phase1_live.grid import outcomes_at_level
def sub(w,i):
 return {**w,**{k:v[i:] for k,v in w.items() if isinstance(v,np.ndarray)},'n':int(w['n']-i)}
def event(w,j,kind,level=None,**kw):
 return dict(date=iso,kind=kind,bar_index=int(j),clock=float(p.xhours([w['t'][j]],d)[0]),known_clock=float(p.xhours([w['t'][j]],d)[0])+1/60,level=level,**kw)
def held(w,i,L,side):
 return i+30<w['n'] and np.all(np.diff(w['t'][i:i+31])==60000) and np.all((w['c'][i:i+31]-L)*side>0)
def reject(w,start,L,side,W):
 if start>=w['n']:return None
 q=outcomes_at_level(sub(w,start),L,width=W,side=-side)
 if not q['reject']:return None
 j=int(np.searchsorted(w['t'],q['touch_ms']));end=int(np.searchsorted(w['t'],q['touch_ms']+15*60000,side='right'))
 idx=np.flatnonzero((w['c'][j:end]-L)*side>=.5*W)
 if not len(idx):return None
 return (j,j+int(idx[0]))
found={};negp19=[];cnt=[]
dates=sorted(p.DATES,reverse=True)
for iso in dates:
 d=date.fromisoformat(iso);row=p.TABLES['sessions_F'][iso];op=p.TABLES['open_switch_F'].get(iso,{})
 if not row.get('eligible'):continue
 w=p.window(d,9.5,16)
 if w['n']!=390 or np.any(np.diff(w['t'])!=60000):continue
 c=w['c'];h=w['h'];l=w['l'];n=w['n'];VAL=op.get('VAL');VAH=op.get('VAH')
 if 'R-A10' not in found:
  opx=float(w['o'][0]);first=c[0]
  up=first>opx and l[0]>=opx and np.all(l[1:30]>opx)
  down=first<opx and h[0]<=opx and np.all(h[1:30]<opx)
  if up or down:
   found['R-A10']={'date':iso,'kind':'named-no-through-open-first30','side':1 if up else -1,'open':opx,'first30_high':float(h[:30].max()),'first30_low':float(l[:30].min()),'known_clock':10,'first_bar_ohlc':[float(w[k][0]) for k in ('o','h','l','c')]}
 if 'R-P06' not in found:
  asia=p.window(d,-4,2);london=p.window(d,2,8)
  if all(v['n']==360 and np.all(np.diff(v['t'])==60000) for v in (asia,london)) and london['high']<asia['high'] and london['low']>asia['low']:
   found['R-P06']={'date':iso,'kind':'source-clock-London-no-Asia-hit','asia_high':asia['high'],'asia_low':asia['low'],'london_high':london['high'],'london_low':london['low']}
 # P19: invoke the actual two-candle geometry for every pair. Source outcomes remain labelled.
 bot=np.minimum(w['o'],c);top=np.maximum(w['o'],c)
 gaps=np.flatnonzero((bot[1:]-top[:-1]>=1)|(bot[:-1]-top[1:]>=1))+1
 cnt.append({'date':iso,'rth_gap_count':len(gaps)})
 if len(gaps)==0:negp19.append(iso)
 if iso=='2026-07-10':found['P19_July10_all_pairs']=[event(w,int(i),'body_gap',**p.ff.r_p19_body_gap(w['o'][i-1:i+1],h[i-1:i+1],l[i-1:i+1],c[i-1:i+1])) for i in gaps[:6]]
 if 'R-P02' not in found:
  for hr in range(9,16):
   prev=p.window(d,hr-1,hr);cur=p.window(d,hr,hr+1)
   if prev['n']==60 and cur['n']==60 and cur['high']<=prev['high'] and cur['low']>=prev['low']:
    found['R-P02']={'date':iso,'kind':'hour-neither-sweep','hour':hr,'prior_high':prev['high'],'prior_low':prev['low']};break
 if VAL is not None and VAH is not None and VAH>VAL:
  W=VAH-VAL
  if 'R-A08' not in found:
   for side,L,opp in [(1,VAH,VAL),(-1,VAL,VAH)]:
    for i in range(1,n-63):
     if (c[i]-L)*side<=0 or (c[i-1]-L)*side>0 or not held(w,i,L,side):continue
     for j in range(i+31,n-31):
      if not (VAL<c[j]<VAH) or VAL<c[j-1]<VAH:continue
      if not np.all((c[j:j+31]>VAL)&(c[j:j+31]<VAH)):continue
      targets=np.flatnonzero((l[j+31:]<=opp+.5)&(h[j+31:]>=opp-.5))
      if not len(targets):continue
      k=j+31+int(targets[0])
      if np.any((c[j+31:k+1]-L)*side>0):continue
      found['R-A08']={'date':iso,'kind':'named-held-reaccept','side':side,'VAL':VAL,'VAH':VAH,'events':[event(w,i,'outside break',L),event(w,i+30,'outside hold complete',L),event(w,j,'reentry',L),event(w,j+30,'inside hold complete',L),event(w,k,'later opposite edge',opp)]};break
     if 'R-A08' in found:break
    if 'R-A08' in found:break
  if 'R-A09' not in found:
   ups=np.flatnonzero(c>VAH);dns=np.flatnonzero(c<VAL)
   if len(ups) and len(dns):
    i,j=sorted([int(ups[0]),int(dns[0])]);side=1 if j==int(ups[0]) else -1;inside=(c[i:j+1]>VAL)&(c[i:j+1]<VAH)
    hashold=any(np.all(inside[k:k+31]) for k in range(max(0,len(inside)-30)))
    if not hashold:
     for L in ([VAH,VAL] if side>0 else [VAL,VAH]):
      q=reject(w,j+1,L,side,W)
      if q:
       a,b=q;found['R-A09']={'date':iso,'kind':'named-traverse-retest','side':side,'VAL':VAL,'VAH':VAH,'events':[event(w,i,'first outside close'),event(w,j,'opposite outside close'),event(w,a,'retest',L),event(w,b,'half-width rejection',L)]};break
 if 'R-A07' not in found:
  ib=p.window(d,9.5,10.5);b=p.window(d,10.5,16);W=ib['high']-ib['low']
  for side,L in [(1,ib['high']),(-1,ib['low'])]:
   for i in range(1,b['n']-46):
    if (b['c'][i]-L)*side<=0 or (b['c'][i-1]-L)*side>0 or not held(b,i,L,side):continue
    q=reject(b,i+31,L,side,W)
    if q:
     a,z=q;found['R-A07']={'date':iso,'kind':'named-IB-held-break-later-retest','side':side,'IBH':ib['high'],'IBL':ib['low'],'events':[event(b,i,'break',L),event(b,i+30,'30-minute hold',L),event(b,a,'later retest',L),event(b,z,'half-width rejection',L)]};break
   if 'R-A07' in found:break
 if 'R-J03' not in found and row.get('extended') and row.get('path_class') in ['high-only','low-only']:
  am=p.window(d,9.5,12);side=1 if row['path_class']=='high-only' else -1;L=row['H'] if side>0 else row['L'];eq=row['EQ']
  breaks=np.flatnonzero((am['c']-L)*side>0)
  if len(breaks):
   i=int(breaks[0]);hits=np.flatnonzero((am['l']<=eq+.5)&(am['h']>=eq-.5)&(np.arange(am['n'])>i))
   for j in hits:
    if j>=30 or j+15>=am['n']:continue
    if np.all((am['c'][j:j+16]-eq)*side>=0):
     found['R-J03']={'date':iso,'kind':'named-extended-EQ-15minute-hold','path':row['path_class'],'width_ratio':row.get('w_rel_prior_rth'),'events':[event(am,i,'edge break',L),event(am,int(j),'EQ retrace',eq),event(am,int(j+15),'15-minute hold',eq)]};break
out={'candidate_events':found,'p19_zero_gap_RTH_dates':negp19,'p19_counts':cnt,'method':'Read-only chronological audit on complete existing bars; no source-missing profile/tape inputs constructed. Named default event checks, not certified author trade entries.'}
(p.OUT/'additional_sequence_candidates.json').write_text(json.dumps(out,indent=2,default=p.serial)+'\n')
print(json.dumps({'found':found,'p19_zero_gap_RTH_count':len(negp19),'p19_zero_sample':negp19[:5]},indent=2,default=p.serial),flush=True)
