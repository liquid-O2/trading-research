import sys,json,argparse
from pathlib import Path
from datetime import date
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'implementation/src'),str(ROOT/'implementation/tools')]
import chart_audit_plots as p
data=json.loads((p.OUT/'additional_sequence_candidates.json').read_text());found=data['candidate_events']
orig=p.Drawing.make
def make(self):
 orig(self)
 q=self.spec.get('audit_sequence')
 if not q:return self
 self.trace['helpers']['audit_sequence']=q
 self.a,self.b=9.5,16
 self.notes.append('Additional chronological audit of existing bars/levels; marks show a named sequence, while the header retains the original session scorer.')
 if self.id=='R-P02':
  hr=q['hour'];w=p.window(self.d,hr-1,hr);n=p.window(self.d,hr,hr+1)
  self.a,self.b=hr-1,hr+1;self.lines=[];self.boxes=[];self.marks=[];self.trace['geometry']=[]
  self.band('actual prior-hour code box',w['low'],w['high'],hr-1,hr)
  for k,x in [('prior H',w['high']),('prior L',w['low']),('prior mid',(w['high']+w['low'])/2),('current hour open',n['open'])]:self.line(k,x,hr,hr+1)
  self.trace['helpers']['selected_hour']=p.ff.r_p02_hourly_sweep(prev_h=w['high'],prev_l=w['low'],prev_open=w['open'],hour_open=n['open'],highs=n['h'],lows=n['l'])
  self.focus_start=hr;self.notes.append('Selected 11:00 hour has neither high nor low sweep; daily OR scorer may still be true from another hour.')
 elif self.id=='R-P19':
  self.notes.append('Read-only scan of every adjacent complete RTH pair finds zero gaps of 4 ticks or more on this date.')
 elif self.id=='R-P06':
  self.a,self.b=-4,8;self.focus_start=2
  self.band('source Asia 20:00-02:00 comparison',q['asia_low'],q['asia_high'],-4,2)
  self.line('source Asia H, known02:00',q['asia_high'],2,8)
  self.line('source Asia L, known02:00',q['asia_low'],2,8)
  self.notes.append('Source-clock comparison uses the existing complete bars: London02:00-08:00 reaches neither completed Asia bound. Legacy code boxes remain drawn separately.')
 elif self.id=='R-A10':
  self.a,self.b=9.5,10;self.focus_start=9.5
  self.notes.append('Named first-30-minute no-through-open positive, including the first bar. Equality at the initial opening print is allowed; minute bars do not resolve an intraminute retouch. This observation does not certify all qualitative opening/day labels.')
 else:
  if self.id=='R-A07':
   self.line('audit continuation of known IB low',q['IBL'],10.5,16)
   self.line('audit continuation of known IB high',q['IBH'],10.5,16)
  w=p.window(self.d,9.5,16)
  labels=[]
  for number,e in enumerate(q['events'],1):
   x=e['known_clock'];idx=int(np.searchsorted(p.xhours(w['t'],self.d),e['clock']));idx=min(idx,w['n']-1)
   # Close-based stages belong at the actual close, not at the reference edge.
   at_edge=e['kind'] in ('retest','later retest','later opposite edge')
   px=e['level'] if at_edge else float(w['c'][idx])
   self.marks.append((x,px,str(number),'#171717'))
   minutes=round(x*60)
   labels.append(f"{number} {e['kind']} known {minutes//60:02d}:{minutes%60:02d}")
   e['marker_price']=px
  self.notes.append('Numbered stages: '+', '.join(labels)+'. Close stages use actual closes; retest/target marks use the touched edge.')
  self.focus_start=q['events'][-2]['clock']-.05
 return self
p.Drawing.make=make
ap=argparse.ArgumentParser();ap.add_argument('--ids',nargs='*');args=ap.parse_args()
rs=[]
for id in ['R-A07','R-A08','R-A09','R-A10','R-P02','R-P06','R-P19']:
 if args.ids and id not in args.ids:continue
 q=found[id] if id!='R-P19' else {'date':data['p19_zero_gap_RTH_dates'][0],'kind':'all-RTH-pairs-no-gap'}
 s=next(x for x in p.SCORES if x['id']==id);iso=q['date']
 spec={'id':id,'date':iso,'case':'sequence-positive' if id.startswith('R-A') else 'event-negative','code_result':True if iso in s['positive_dates'] else False if iso in s['negative_dates'] else None,'selection':'independent chronological named-event audit','positive_count':len(s['positive_dates']),'negative_count':len(s['negative_dates']),'audit_sequence':q}
 rs.append(p.draw(spec));print(id,iso,'written',flush=True)
dest=p.OUT/'extra_plot_results.json';a=json.loads(dest.read_text());keys={(x['id'],x['case'],x['date']) for x in rs};a=[x for x in a if (x['id'],x['case'],x['date']) not in keys]+rs;dest.write_text(json.dumps(a,indent=2,default=p.serial)+'\n')
