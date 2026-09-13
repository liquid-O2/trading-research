from pathlib import Path
import sys
sys.path.insert(0,'/workspace/implementation/src')
from trading_research.research.method_pack.measurement_runner import configure_runtime
from trading_research.research.method_pack import historical_charts as charts
from trading_research.research.method_pack import historical_runner as hr
import matplotlib.pyplot as plt
import matplotlib.dates as md

configure_runtime()
out=Path(__file__).resolve().parent
root=out.parent/'run-1.0.1'
m=charts._market('2020-01-02',True)
fig,ax=plt.subplots(figsize=(14,7))
charts._candles(ax,m.bars(m.at('09:20'),m.at('11:00')))
for branch,color,offset,label in [
    ('judas_outbound','#236caa',(10,-55),'09:30 outbound LONG\n8821.25; opening-rule assumption'),
    ('judas_reversal','#ad343e',(25,32),'09:45 reversal SHORT\n8843.50; confirmed pattern')]:
    doc=hr.read_job(root/'jobs/evaluation/2020-01-02'/f'JJ-TBR--branch--{branch}.json.gz')
    e=doc['episodes'][0]
    x=md.date2num(charts._time(e['decision_at']));y=float(e['geometry']['entry'])
    ax.scatter([x],[y],color=color,s=65,zorder=5)
    ax.annotate(label,(x,y),xytext=offset,textcoords='offset points',fontsize=10,color=color,
                arrowprops={'arrowstyle':'->','color':color},bbox={'facecolor':'white','edgecolor':color,'alpha':.95})
    result=doc['setup_measurements'][0]['boundary']
    xx=md.date2num(charts._time(result['resolved_at_ns']));yy=float(e['geometry']['target'])
    ax.scatter([xx],[yy],color=color,s=60,marker='x',zorder=5)
    ax.plot([x,xx],[yy,yy],color=color,linestyle='--',linewidth=1)
doc=hr.read_job(root/'jobs/evaluation/2020-01-02/JJ-TBR--branch--other_session.json.gz')
e=next(e for e in doc['episodes'] if e['side']=='long' and m.at('10:00')<e['decision_at']<m.at('11:00'))
x=md.date2num(charts._time(e['decision_at']));y=float(e['geometry']['entry'])
ax.scatter([x],[y],facecolors='none',edgecolors='#775d37',s=70,zorder=5)
ax.annotate('10:21 long candidate REJECTED\n8813.50; confirmation failed',(x,y),xytext=(25,35),textcoords='offset points',
            fontsize=10,color='#775d37',arrowprops={'arrowstyle':'->','color':'#775d37'},bbox={'facecolor':'white','edgecolor':'#775d37'})
ax.axhline(8831,color='#9d8a55',linestyle=':',label='06:00–09:00 range high 8831.00')
ax.axhline(8807.75,color='#777777',linestyle=':',label='06:00–09:00 range low 8807.75')
ax.set_title('January 2, 2020 — separate Judas legs and the rejected later long',loc='left',fontsize=15,pad=18)
ax.set_ylabel('NQ price');ax.legend(loc='lower right',fontsize=9)
ax.set_ylim(8796,8866)
fig.text(.08,.035,'All times ET. Solid dots: qualifying entry references; crosses: observed objectives; hollow dot: rejected candidate. No fills inferred.',fontsize=9)
fig.subplots_adjust(bottom=.13,top=.87,left=.08,right=.98)
fig.savefig(out/'day-entry-review.png',dpi=140)
print(out/'day-entry-review.png')
