"""Deterministic review charts from the exact scored artifact records."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from .empirical_protocol import write_json,content_hash
from .empirical_runner import ROOT,file_hash


def build_charts(root=ROOT):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    root=Path(root);manifest=json.loads((root/'RUN_MANIFEST.json').read_text())
    seen=set();years=set();selected=[]
    for job in manifest['jobs']:
        cp=root/'checkpoints'/f'{job["job_id"]}.json'
        if not cp.exists():continue
        checkpoint=json.loads(cp.read_text());path=Path(checkpoint['artifact_path'])
        if file_hash(path)!=checkpoint['artifact_sha256']:raise ValueError('chart source artifact changed')
        doc=json.loads(path.read_text())
        for record in sorted(doc['records'],key=lambda r:(r['opportunity']['available_at'],r['opportunity']['opportunity_id'])):
            op,replay=record['opportunity'],record['replay'];key=op['rule_id'],replay['verdict'];year=op['session_date'][:4]
            if key not in seen or year not in years:
                seen.add(key);years.add(year);selected.append((record,doc['bars'],str(path),checkpoint['artifact_sha256']))
    selected=selected[:80];index=[]
    et=ZoneInfo('America/New_York')
    def dt(t):return datetime.fromtimestamp(t/1e9,tz=et)
    for record,bars,source,digest in selected:
        op,replay=record['opportunity'],record['replay'];ref=op['reference']
        lo=op['available_at']-45*60*10**9;hi=replay['completed_at']+15*60*10**9
        view=[b for b in bars if lo<=b['start']<=hi and b['complete'] and b['C'] is not None]
        fig,ax=plt.subplots(figsize=(12,6));fig.subplots_adjust(bottom=.29)
        for b in view:
            color='#147d62' if float(b['C'])>=float(b['O']) else '#b83f40';x=mdates.date2num(dt(b['start']))
            ax.vlines(x,float(b['L']),float(b['H']),color=color,linewidth=.7)
            ax.plot([x-0.00018,x],[float(b['O'])]*2,color=color,linewidth=1)
            ax.plot([x,x+0.00018],[float(b['C'])]*2,color=color,linewidth=1)
        for key in ('high','low','poc','midpoint'):
            if ref.get(key) is not None:ax.axhline(float(ref[key]),ls='--',lw=.9,label='reference '+key)
        for key in ('upper_band','lower_band'):
            if ref.get(key):ax.axhspan(*map(float,ref[key]),alpha=.08,color='purple',label=key)
        ax.axvline(dt(op['available_at']),color='#2057a4',label='initial opportunity available')
        ax.axvline(dt(replay['completed_at']),color='#8d3ea8',ls=':',label='replay endpoint / expiry')
        ax.set_title(f"{op['method_id']} / {op['branch']} — {op['session_date']} — {replay['verdict'].upper()}",fontsize=11)
        ax.set_ylabel('Native NQ price');ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M',tz=et))
        ax.set_xlabel('America/New_York — native minute OHLC overview');ax.grid(alpha=.18)
        ax.legend(loc='best',fontsize=8)
        note=(f"{op['opportunity_id']} | instrument {op['instrument_id']} | {op['side']} | {op['observation_unit']}\n"
              f"Endpoint: {replay['reason']} | source method: {replay['source_method_verdict']}\n"
              'Research comparison only. No actual selection, attempt, order, fill or profitability claim.\n'
              f"Scored-record SHA256: {content_hash(record)}\nSource artifact SHA256: {digest}")
        fig.text(.08,.055,note,fontsize=8,va='bottom',family='monospace')
        path=root/'charts'/f'{op["opportunity_id"]}.png';path.parent.mkdir(parents=True,exist_ok=True)
        fig.savefig(path,dpi=140);plt.close(fig)
        index.append({'opportunity_id':op['opportunity_id'],'rule_id':op['rule_id'],'verdict':replay['verdict'],
                      'year':op['session_date'][:4],'source_artifact':source,'source_sha256':digest,
                      'record_sha256':content_hash(record),'chart_path':str(path),'chart_sha256':file_hash(path),
                      'visual_review':'pending'})
    write_json(root/'charts/INDEX.json',{'selection':manifest['chart_selection'],'charts':index})
    return index


if __name__=='__main__':print(json.dumps({'charts':len(build_charts())}))
