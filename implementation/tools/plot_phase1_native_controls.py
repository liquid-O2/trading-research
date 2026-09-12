#!/usr/bin/env python3
"""Plot stored native computations, with their source-comparison limits."""
from __future__ import annotations

import argparse
from decimal import Decimal
import hashlib
import json

import matplotlib.pyplot as plt
import numpy as np

from reconstruct_phase1_completion_cases import (
    ROOT, OUT, COLORS, candle_plot, source_image, load_catalog, save_json, ns_to_et,
)


VALIDATION=ROOT/'implementation/validation/phase1-completion'


def display(value):
    return 'unknown' if value is None else str(value)


def profile_payload_plot(ax, payload, title):
    rows=payload['rows'];px=[float(r['price']) for r in rows]
    buy=np.array([float(r['buy_volume']) for r in rows]);sell=np.array([float(r['sell_volume']) for r in rows]);unknown=np.array([float(r['unknown_volume']) for r in rows])
    height=float(payload['tick_size'])*.92
    for values,left,color,label in [(buy,None,COLORS['buy'],'B buy'),(sell,buy,COLORS['sell'],'A sell'),(unknown,buy+sell,COLORS['unknown'],'N unknown')]:
        ax.barh(px,values,left=left,height=height,color=color,label=label)
    if payload['poc'] is not None:
        ax.axhline(float(payload['poc']),color=COLORS['ink'],ls='--',lw=.9,label=f'POC {payload["poc"]}')
        poc_row=next(r for r in rows if Decimal(r['price'])==Decimal(payload['poc']))
        ax.plot(float(poc_row['total_volume']),float(payload['poc']),'o',color=COLORS['ink'],ms=3)
    ax.set_title(title,loc='left',fontsize=11);ax.set_xlabel('Executed volume');ax.grid(axis='y',alpha=.15)


def plotted_artifact(path, evidence, details):
    return dict(chart=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        evidence_path=str(evidence.relative_to(ROOT)),evidence_sha256=hashlib.sha256(evidence.read_bytes()).hexdigest(),
        historical_candidate=False,source_case_agreement='native control only; no source fill or author detector inferred',**details)


def flow():
    evidence=VALIDATION/'native-flow.json';doc=json.loads(evidence.read_text());records=[]
    for window in doc['windows']:
        chart=window['chart_data'];day=window['date'];footprint=chart['footprint_close']
        fig=plt.figure(figsize=(14,9),layout='constrained');grid=fig.add_gridspec(2,3,width_ratios=[1.2,1,1])
        ax=fig.add_subplot(grid[0,0]);bars=[{**r,**{k:Decimal(r[k]) for k in ('O','H','L','C','V')},'complete':True} for r in chart['ohlcv_1m']]
        candle_plot(ax,bars,'One-minute candles · 09:30–09:35')
        px=[float(r['price']) for r in footprint]
        buy=np.array([float(r['buy_volume']) for r in footprint]);sell=np.array([float(r['sell_volume']) for r in footprint]);unknown=np.array([float(r['unknown_volume']) for r in footprint])
        ax=fig.add_subplot(grid[:,1]);height=float(window['tick_size'])*.94
        ax.barh(px,buy,height=height,color=COLORS['buy'],label='B buy')
        ax.barh(px,sell,left=buy,height=height,color=COLORS['sell'],label='A sell')
        ax.barh(px,unknown,left=buy+sell,height=height,color=COLORS['unknown'],label='N unknown')
        ax.set_title('Full native footprint\nEvery price row retained',loc='left');ax.set_xlabel('Executed volume');ax.set_ylabel('Native price');ax.legend(fontsize=8)
        ax=fig.add_subplot(grid[:,2]);delta=buy-sell
        ax.barh(px,delta,height=height,color=[COLORS['buy'] if x>=0 else COLORS['sell'] for x in delta])
        ax.axvline(0,color=COLORS['ink'],lw=.6);ax.set_title('Signed volume by price\nUnknown volume stays unsigned',loc='left');ax.set_xlabel('B − A volume')
        ax=fig.add_subplot(grid[1,0]);minutes=chart['flow_1m'];x=np.arange(len(minutes))
        ax.bar(x-.18,[float(r['buy']) for r in minutes],.36,label='B buy',color=COLORS['buy'])
        ax.bar(x+.18,[float(r['sell']) for r in minutes],.36,label='A sell',color=COLORS['sell'])
        ax.set_xticks(x,[ns_to_et(r['start_ns']).strftime('%H:%M') for r in minutes]);ax.set_ylabel('Executed volume');ax.set_title('Minute effort and cumulative known delta',loc='left',fontsize=10)
        delta_ax=ax.twinx();delta_ax.plot(x,[float(r['cumulative_known_delta']) for r in minutes],color=COLORS['ink'],marker='o',lw=1,label='Cumulative B − A');delta_ax.set_ylabel('Cumulative known delta')
        same=chart['same_candle'];early=same['developing_2m'];close=same['complete_5m']
        for item_ax in fig.axes:item_ax.grid(axis='y',alpha=.15)
        fig.suptitle(f'{day} · native NQ control · instrument {window["instrument_id"]} · tick {window["tick_size"]}',fontsize=16,weight='bold')
        fig.supxlabel(f'Same five-minute candle: POC at 09:32 = {display(early["poc"])}; at 09:35 = {display(close["poc"])}. '
                     f'Body delta {display(early["body_delta"])} → {display(close["body_delta"])}.\n'
                     'The earlier snapshot is immutable. These executions and BBO observations do not establish hidden orders, full depth or a source entry.',fontsize=10)
        path=OUT/f'native-flow-{day}.png';fig.savefig(path,dpi=145);plt.close(fig)
        records.append(plotted_artifact(path,evidence,dict(date=day,objects=['O004','O098','O105','O108','O111','O112','O113','O120','O164'],
            source_display_setting='none inferred',native_rows=len(footprint),same_candle=same)))
    save_json(OUT/'native-flow-chart-data.json',records)


def geometry():
    evidence=VALIDATION/'native-geometry.json';doc=json.loads(evidence.read_text());controls=doc['controls'];records=[]
    control=controls['feb24_jj_range'];objects={x['recipe_id']:x['value'] for x in control['objects']}
    r,q,l,e=(objects[k] for k in ('O005','O007','O014','O015'))
    fig,ax=plt.subplots(figsize=(10,8),layout='constrained')
    low,high=float(r['L']),float(r['H']);ax.axhspan(low,high,color=COLORS['blue'],alpha=.12)
    lines=[('Range low',r['L']),('Q25',q['q25']),('Equilibrium',q['eq']),('Q75',q['q75']),('Range high',r['H'])]
    lines += [(f'Upper {k} W',v) for k,v in l['upper_ladder'].items()]
    lines += [(f'Lower {k} W',v) for k,v in l['lower_ladder'].items()]
    for i,(label,price) in enumerate(sorted(lines,key=lambda x:float(x[1]))):
        px=float(price);ax.hlines(px,.05,.63,color=COLORS['blue'] if label.startswith(('Range','Q','Equil')) else COLORS['gold'],lw=1)
        ax.text(.66,px,f'{label}: {price}',va='center',fontsize=9)
    for side,key in [('Upper','upper_band'),('Lower','lower_band')]:
        a,b=map(float,e[key]);ax.axhspan(a,b,color=COLORS['sell'],alpha=.1)
        ax.text(.1,(a+b)/2,f'{side} extension area\n{a:.2f}–{b:.2f}',va='center',fontsize=9)
    ax.set_xlim(0,1);ax.set_xticks([]);ax.set_ylabel('Native NQH6 price');ax.set_title('February 24 · frozen 06:00–09:00 ET range\nActual parent-derived geometry',loc='left',fontsize=15)
    fig.supxlabel(f'Native width = {r["W"]} points. Both branches preserve the selected range identity.\nThis is the dated range-control case, not an observed author trade or fitted entry.',fontsize=10)
    path=OUT/'JJ-range-control-2026-02-24.png';fig.savefig(path,dpi=150);plt.close(fig)
    records.append(plotted_artifact(path,evidence,dict(control='feb24_jj_range',objects=list(objects))))
    control=controls['june12_tpo_ib'];objects={x['recipe_id']:x['value'] for x in control['objects']};tpo=objects['O078'];ib=objects['O082']
    fig,(ax,dist)=plt.subplots(1,2,figsize=(13,9),gridspec_kw={'width_ratios':[1.7,1]},layout='constrained')
    periods=tpo['period_ranges'];labels=[r['period_id'] for r in periods]
    for i,row in enumerate(periods):
        ax.vlines(i,float(row['L']),float(row['H']),lw=9,alpha=.65,color=COLORS['blue']);ax.text(i,float(row['H'])+3,row['period_id'],ha='center',fontsize=9)
    ax.set_xticks(range(len(labels)),[ns_to_et(r['start']).strftime('%H:%M') for r in periods],rotation=45);ax.set_ylabel('Native NQM6 price');ax.set_xlabel('America/New_York · 30-minute period ranges')
    ax.set_title('Complete period extrema · all underlying minute bars',loc='left',fontsize=12)
    for name,key in [('IB high','ibh'),('IB low','ibl')]:ax.axhline(float(ib[key]),ls='--',lw=1,color=COLORS['gold'],label=f'{name}: {ib[key]}')
    ax.legend(fontsize=8)
    counts=sorted(tpo['count_by_price'].items(),key=lambda r:float(r[0]));dist.barh([float(p) for p,n in counts],[n for p,n in counts],height=float(tpo['price_step'])*.92,color=COLORS['blue'])
    dist.set_xlabel('Distinct dated letter memberships');dist.set_title('TPO count by native price row',loc='left',fontsize=12)
    fig.suptitle('June 12 · TPO and initial balance from complete native bars',fontsize=15,weight='bold')
    fig.supxlabel('Declared comparison: 30-minute period-range construction and native 0.25-point grid.\nThe source letter window and source-specific distribution selections remain unverified.',fontsize=10)
    path=OUT/'native-TPO-IB-2026-06-12.png';fig.savefig(path,dpi=150);plt.close(fig)
    records.append(plotted_artifact(path,evidence,dict(control='june12_tpo_ib',objects=list(objects))))
    control=controls['june12_disjoint_composite'];payloads=[x['value'] for x in control['objects']]
    fig,axes=plt.subplots(1,3,figsize=(15,10),sharey=True,layout='constrained')
    labels=['Prior RTH · June 11 09:30–16:00','Overnight · June 11 18:00–June 12 09:30','Explicit composite · those two snapshots']
    for ax,payload,label in zip(axes,payloads,labels):
        profile_payload_plot(ax,payload,label+'\nVolume '+payload['total_volume'])
    axes[0].set_ylabel('Native NQM6 price');axes[0].legend(fontsize=8)
    fig.suptitle('Disjoint dated profile composition · O070',fontsize=16,weight='bold')
    fig.supxlabel('498,476 + 104,734 = 603,210 contracts. Zero shared native event identities; each constituent keeps its own formation window.\nAll price rows are retained. Trade coverage remains unknown after independent bar reconciliation; no source-selected composite or VA expansion is inferred.',fontsize=10)
    path=OUT/'native-composite-2026-06-12.png';fig.savefig(path,dpi=145);plt.close(fig)
    records.append(plotted_artifact(path,evidence,dict(control='june12_disjoint_composite',objects=['O061','O070'],reconciliation=control['reconciliation'])))
    control=controls['june12_sires_overnight'];objects={x['recipe_id']:x['value'] for x in control['objects']};rng=objects['O011'];overnight=objects['O073']['overnight_profile_snapshot']
    fig=plt.figure(figsize=(14,10),layout='constrained');grid=fig.add_gridspec(2,2,height_ratios=[.9,1.5])
    ax=fig.add_subplot(grid[0,:]);original,source=source_image(load_catalog(verify_sources=True),'MAMT:14')
    ax.imshow(original);ax.axis('off');ax.set_title('Original Sires p.14 · 18:00–09:30 ET\nSource date and chart timeframe unknown',loc='center',fontsize=10)
    ax=fig.add_subplot(grid[1,0]);profile_payload_plot(ax,overnight,'Dated native overnight profile\nJune 11 18:00–June 12 09:30 ET')
    ax.set_ylabel('Native NQM6 price');ax.legend(fontsize=8)
    ax=fig.add_subplot(grid[1,1]);ax.axis('off')
    text='O011 → O073: the same overnight window\n\n'
    text+=f'O011 high: {rng["on_high"]}\nO011 low: {rng["on_low"]}\nWidth: {rng["on_width"]} points\n\n'
    text+=f'Profile POC: {overnight["poc"]}\nExecuted volume: {overnight["total_volume"]}\n\n'
    text+='Source VA fraction: 40%\nSource expansion / tie policy: unknown\nVA bounds and LVN selection: unavailable\n\n'
    text+='The prior RTH POC remains a separate reference.\nAn undisclosed alignment or opening-response\ncriterion does not become a computed signal.\n\n'
    text+='Clock bars: complete. Trade coverage: unknown\nafter independent minute reconciliation.'
    ax.text(.03,.96,text,va='top',fontsize=12,linespacing=1.6,transform=ax.transAxes)
    fig.suptitle('Sires overnight binding · documented clock, dated native control',fontsize=16,weight='bold')
    fig.supxlabel('The June 12 control is not a recovered date for the undated source illustration. O073 keeps the actual O011 parent and immutable profile identity.',fontsize=10)
    path=OUT/'native-SIRES-overnight-2026-06-12.png';fig.savefig(path,dpi=145);plt.close(fig)
    records.append(plotted_artifact(path,evidence,dict(control='june12_sires_overnight',objects=['O011','O073'],source=source,source_unknowns=control['source_unknowns'])))
    save_json(OUT/'native-geometry-chart-data.json',records)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--kind',choices=['flow','geometry','all'],default='all');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if args.kind in {'flow','all'}:flow()
    if args.kind in {'geometry','all'}:geometry()


if __name__=='__main__':main()
