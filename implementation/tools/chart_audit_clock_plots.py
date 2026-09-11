"""Read-only clock geometry supplements using existing production helpers."""
from __future__ import annotations
import json
from datetime import date
import matplotlib.pyplot as plt
from chart_audit_plots import Drawing, OUT, PLOTS, paint, projections, serial, xhours
from trading_research.research.phase1_live.clocks import CLOCKS, clock_bounds
from trading_research.research.phase1_live.compute import load_rows

CLOCKS_TO_SHOW = (
 ('asia', 'range.asia.2000-2030'),
 ('midnight', 'range.midnight.0000-0030'),
 ('london', 'range.london.0300-0330'),
 ('rth_a', 'range.rth.0930-1000'),
 ('rth_b', 'range.rth.1000-1030'),
 ('lunch', 'range.lunch.1200-1230'),
 ('moc', 'range.moc.1500-1530'),
)

def main():
    retained={(r['date'],r['clock']):r for r in load_rows('clocks_F')}
    results=[]
    for iso in ('2025-01-10','2026-07-10'):
        for name,cid in CLOCKS_TO_SHOW:
            spec={'id':'R-J23','date':iso,'case':'clock-'+name,'code_result':None,
                  'selection':'Existing projection helper on this clock; response unscored',
                  'positive_count':None,'negative_count':None,'clock':cid}
            bounds=clock_bounds(date.fromisoformat(iso),CLOCKS[cid])
            a,b,end=map(float,xhours([bounds['start_ms'],bounds['end_ms'],bounds['outcome_end_ms']],date.fromisoformat(iso)))
            fig,axes=plt.subplots(3,1,figsize=(16.8,11.8))
            traces=[]
            for panel,ax in enumerate(axes):
                dw=Drawing(spec);dw.a,dw.b=a-.05,end
                w,_,_=dw.clock(cid,inner=panel==0)
                p=projections(w['high'],w['low'])
                if panel==0:
                    for key in ('Q25','Q75'):dw.line(key,p[key],b,end)
                    dw.line('build first open',w['open'],b,end,style=':')
                    title='Frozen box, EQ, quadrants and forming-window first open'
                elif panel==1:
                    for key,value in p.items():
                        if key.startswith(('mr','m05')):dw.line(key,value,b,end)
                    title='Existing helper mean-reversal ladder, using this box width'
                else:
                    for key,value in p.items():
                        if key.startswith('ext'):dw.line(key,value,b,end)
                    for side,color in (('low','#007d73'),('high','#8453a4')):
                        values=[p['band133_166_'+side+'_near'],p['band133_166_'+side+'_far']]
                        dw.band('helper 1.33–1.66 '+side,min(values),max(values),b,end,color)
                    title='Existing helper outer levels and bands, using this box width'
                paint(ax,dw,dw.a,dw.b)
                # Include every requested helper level even when price never approaches it.
                low=min([w['low']]+[q['price'] for q in dw.lines])
                high=max([w['high']]+[q['price'] for q in dw.lines])
                y0,y1=ax.get_ylim();pad=max((high-low)*.035,.5)
                ax.set_ylim(min(y0,low-pad),max(y1,high+pad))
                ax.set_title(title,fontsize=9)
                traces.append({'panel':panel,'geometry':dw.trace['geometry'],'helpers':dw.trace['helpers']})
            old=retained.get((iso,cid),{})
            fig.suptitle(f'R-J23 · {iso} · {cid}\nRetained close-break path: {old.get("path_class")} · helper responses unscored',fontsize=13,y=.985)
            fig.text(.055,.015,'Clocks are America/New_York. Levels start at each build cutoff and extend only through its named code outcome horizon.\n'
                     'clocks_F stores H/L and path; these additional levels come from sessions.projections(), not a scored clock response. Source ±2 is absent from that helper.\n'
                     'Source clock/version must be matched separately. Build first open is not automatically the source range-finish OP.',fontsize=8)
            fig.subplots_adjust(top=.91,bottom=.11,left=.065,right=.97,hspace=.37)
            base=f'R-J23-clock-{name}-{iso}';plot=f'plots/{base}.png';trace=f'plots/{base}.json'
            fig.savefig(OUT/plot,dpi=125);plt.close(fig)
            payload={'case':spec,'plot':plot,'clock_bounds':bounds,'retained_clock_row':old,
                     'panels':traces,'helper':'sessions.py::projections','projection_response_scored':False}
            (OUT/trace).write_text(json.dumps(payload,indent=2,default=serial)+'\n')
            results.append({**spec,'plot':plot,'trace':trace,'notes':['Existing helper geometry only; no new production recipe.']})
            print(iso,name,old.get('path_class'),flush=True)
    (OUT/'clock_plot_results.json').write_text(json.dumps(results,indent=2)+'\n')

if __name__=='__main__':main()
