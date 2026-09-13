"""Native diagnostic figure for the frozen reconstructed context models."""
from pathlib import Path
import argparse,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from trading_research.research.method_pack.historical_runner import load_registry,file_digest,immutable_json
from trading_research.research.method_pack.historical_features import HistoricalFeatures,SECOND
from trading_research.research.method_pack.strategy_options import gamma_at
from trading_research.research.method_pack.strategy_pzones import inferred_pzones
from trading_research.research.method_pack.strategy_context import inferred_auction
from trading_research.research.method_pack.historical_process_scanners import macro_at
from trading_research.research.method_pack.protocol import jsonable
p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);p.add_argument('--date',default='2024-01-02');args=p.parse_args()
root=Path(args.run_root);registry,manifest=load_registry(root);out=root/'diagnostics/models';out.mkdir(parents=True,exist_ok=True)
m=HistoricalFeatures(args.date,records={'strategy_reconstruction':True});g=gamma_at(m,m.at('10:00'));z=inferred_pzones(m)
a=inferred_auction(m,m.at('09:30'),m.at('09:32'));macro=macro_at(m,m.at('09:30'))['inferred_context']
fig,axes=plt.subplots(2,2,figsize=(17,12),layout='constrained');fig.suptitle('Reconstructed strategy inputs · '+args.date,fontsize=21,fontweight='bold')
ax=axes[0,0]
if g['available']:
 rows=g['nodes'];xs=[r['strike'] for r in rows];ys=[r['gamma']/1e6 for r in rows]
 ax.bar(xs,ys,width=.8,color=['#287e78' if y>=0 else '#b64f48' for y in ys]);ax.axhline(0,color='#777',lw=.6)
 ax.axvline(g['spot'],color='#263b55',lw=1.6,label='QQQ spot')
 if g.get('nearest_gamma_flip') is not None:ax.axvline(g['nearest_gamma_flip'],color='#956d2f',ls='--',label='nearest modeled flip')
 ax.set_title('QQQ signed gamma by strike · '+g['expiry_kind']+' · '+str(g['regime'])+' regime')
 ax.set_xlabel('QQQ strike');ax.set_ylabel('Modeled $ gamma per 1% move (millions)');ax.legend(fontsize=9)
else:ax.text(.5,.5,g['reason'],ha='center',transform=ax.transAxes)
ax.text(0,-.2,'Call OI positive / put OI negative; prior-date OI; European midquote IV.\nAn inventory model on the acquired chain, not observed dealer positions.',transform=ax.transAxes,fontsize=9)
ax=axes[0,1];bars=m.bars(m.at('01:00'),m.end,300)
times=[datetime.fromtimestamp(r['start']/SECOND,timezone.utc) for r in bars]
ax.plot(times,[float(r['C']) if r['C'] is not None else float('nan') for r in bars],color='#253c52',lw=.9)
colors={'02:00':'#688d6d','09:00':'#487cb0','10:00':'#b57b43'}
for zone in z:
 t=datetime.fromtimestamp(zone['known_at']/SECOND,timezone.utc);label=t.astimezone(ZoneInfo('America/New_York')).strftime('%H:%M')
 ax.fill_between([t,datetime.fromtimestamp(m.end/SECOND,timezone.utc)],float(zone['low']),float(zone['high']),color=colors[label],alpha=.2)
 ax.text(t,float(zone['high']),label+' '+zone['side'],fontsize=8,color=colors[label])
ax.set_title('Time-anchored P-zones · prior-session training');ax.set_ylabel('NQ price');ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M',tz=ZoneInfo('America/New_York')))
ax.text(0,-.2,'Up to 500 prior sessions; above-median-volume training; 70–80% bands.\nDistances normalized by prior-hour range; live bands frozen at each anchor.',transform=ax.transAxes,fontsize=9)
ax=axes[1,0];ax.axis('off');ax.set_title('Jetbundle state criteria · 09:30–09:32 ET',loc='left')
lines=[]
for state,criteria in a['criteria'].items():
 verdict=a['states'][state];lines.append(state+'  '+('present' if verdict is True else 'absent' if verdict is False else 'unavailable'))
 for name,value in criteria.items():lines.append('    '+name.replace('_',' ')+': '+str(value))
ax.text(0,.97,'\n'.join(lines),va='top',fontsize=10,linespacing=1.35,transform=ax.transAxes)
ax.text(0,-.05,'Independent conditions; no forced state. Displayed depth-one changes\nsupport an inferred withdrawal measure, not identified order cancellations.',transform=ax.transAxes,fontsize=9)
ax=axes[1,1];parts=macro['components'];ax.bar([r['series'] for r in parts],[r['signed_z'] for r in parts],color=['#b64f48','#287e78'])
ax.axhline(0,color='#777',lw=.6);ax.axhline(macro['composite'],color='#243e57',ls='--',label='equal-weight composite');ax.legend()
ax.set_title('Initial-release macro context · '+str(macro['state']));ax.set_ylabel('Signed z score against 12 prior initial releases')
ax.text(0,-.2,'Growth minus inflation: payroll z score and negative CPI z score.\nOur research composite; not the source’s proprietary C-score or an entry.',transform=ax.transAxes,fontsize=9)
for ax in axes.flat:
 if ax.axison:ax.grid(axis='y',alpha=.15)
path=out/'models-2024-01-02.png';fig.savefig(path,dpi=150);plt.close(fig)
immutable_json(out/'MODEL_INPUTS.json',jsonable({'registry_sha256':registry['registry_sha256'],'gamma':g,'pzones':z,'auction':a,'macro':macro,'input_receipts':m.input_receipts}))
immutable_json(out/'manifest.json',{'path':str(path),'sha256':file_digest(path),'inputs_path':str(out/'MODEL_INPUTS.json'),'inputs_sha256':file_digest(out/'MODEL_INPUTS.json'),'script_sha256':file_digest(Path(__file__))})
print(path)
