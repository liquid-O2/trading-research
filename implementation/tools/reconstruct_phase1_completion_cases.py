#!/usr/bin/env python3
"""Rebuild reviewed Phase 1 source comparisons without a parameter search.

All market objects originate in immutable native windows. Unreadable source
clocks, absent MNQ fills and undated illustrations remain explicit limitations.
Run with the workspace Python environment containing matplotlib and PyMuPDF.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, replace
from datetime import date, timedelta
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
from types import MappingProxyType

import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import pymupdf

from trading_research.research.method_pack.clocks import et_ns, ns_to_et
from trading_research.research.method_pack.contracts import validate_output
from trading_research.research.method_pack.native_resolution import ResolvedMembers
from trading_research.research.method_pack.native_windows import collect_window
from trading_research.research.method_pack.objects import native_boundary as nb
from trading_research.research.method_pack.objects import profiles as p
from trading_research.research.method_pack.objects import profile_integration as pi
from trading_research.research.method_pack.objects import context_observations as context
from trading_research.research.method_pack.source_config import load_catalog

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'implementation/reports/phase1-live/methods/reconstructions/v2'
OHLC='quantpad/cme__nq-continuous-futures__ohlcv-1m'
TRADES='quantpad/cme__nq-continuous-futures__trades'
MINUTE=60_000_000_000
COLORS={'buy':'#1a8b71','sell':'#c6545b','unknown':'#88929c','ink':'#183047','blue':'#426caa','gold':'#b48728'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
 'axes.titleweight':'bold','axes.labelcolor':COLORS['ink'],'text.color':COLORS['ink'],'savefig.facecolor':'white'})


def encode(value):
    if isinstance(value,Decimal):return str(value)
    if isinstance(value,date):return value.isoformat()
    if isinstance(value,MappingProxyType):return dict(value)
    if isinstance(value,set):return sorted(value)
    if isinstance(value,tuple):return list(value)
    raise TypeError(type(value).__name__)


def save_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w') as stream:json.dump(value,stream,default=encode,indent=2)
    return {'path':str(path.relative_to(OUT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def save_payload(name,value):
    path=OUT/'objects'/(name+'.json.gz');path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('wb') as raw:
        with gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as zipped:
            import io
            with io.TextIOWrapper(zipped,encoding='utf-8') as text:json.dump(value,text,default=encode,separators=(',',':'))
    return {'path':str(path.relative_to(OUT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'encoding':'gzip JSON; Decimal fields stored as exact decimal strings'}


def source_image(catalog,ref,clip=None):
    key,page=ref.split(':');source=catalog['sources'][key]
    with pymupdf.open(source['path']) as pdf:
        p=pdf[int(page)-1]
        bounds=p.rect if clip is None else pymupdf.Rect(*(clip[i]*(p.rect.width if i%2==0 else p.rect.height) for i in range(4)))
        pix=p.get_pixmap(matrix=pymupdf.Matrix(2,2),clip=bounds,alpha=False)
        target=OUT/'source-images'/f'{key}-{page}{"-figure" if clip else "-page"}.png';target.parent.mkdir(parents=True,exist_ok=True)
        pix.save(target)
        array=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)
    return array,{'source_ref':ref,'source_sha256':source['sha256'],'rendered_page':str(target.relative_to(OUT)),
      'page_clip_fraction':clip,'original_page':int(page)}


def window(dataset,day,start,end,*,instrument=None,previous_start=False):
    start_day=day-timedelta(days=1) if previous_start else day
    first=et_ns(start_day,*start);last=et_ns(day,*end)
    got=collect_window(ROOT/'data',dataset,first,last,instrument,required='ohlcv' if dataset==OHLC else 'trades')
    if got.resolved is None:raise ValueError(f'no native members for {day} {start} {end}')
    return got


def bars_from_window(win,minutes):
    groups={}
    for row in win.rows:
        if 'start' not in row:continue
        at=(row['start']//(minutes*MINUTE))*(minutes*MINUTE)
        if at<win.start_ns or at+minutes*MINUTE>win.end_ns:continue
        groups.setdefault(at,[]).append(row)
    bars=[]
    for at,rows in sorted(groups.items()):
        end=at+minutes*MINUTE
        resolved=ResolvedMembers(tuple(rows),win.instrument_id,at,end,
          max(r['known_at'] for r in rows),None,(),instrument_definition=win.instrument_definition)
        result=nb.o004({'kind':'time','size_minutes':minutes},resolved)
        validate_output(result)
        bars.append(result.value)
    return bars


def candle_plot(ax,bars,title):
    for row in bars:
        if not row['complete'] or row['O'] is None:continue
        x=mdates.date2num(ns_to_et(row['start']));width=(row['end']-row['start'])/86_400_000_000_000*.7
        o,h,l,c=map(float,(row['O'],row['H'],row['L'],row['C']))
        color=COLORS['buy'] if c>=o else COLORS['sell']
        ax.vlines(x,l,h,color=color,lw=.85)
        ax.add_patch(Rectangle((x-width/2,min(o,c)),width,max(abs(c-o),.10),facecolor=color,edgecolor=color,lw=.5))
    ax.autoscale_view();ax.xaxis_date();ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M',tz=ns_to_et(bars[0]['start']).tzinfo))
    ax.grid(axis='y',color='#d9e0e6',lw=.6);ax.set_title(title,loc='left');ax.set_ylabel('Native NQ price');ax.set_xlabel('America/New_York · complete bars only')


def native_summary(win):
    return dict(instrument_id=win.instrument_id,instrument_definition=None if win.instrument_definition is None else asdict(win.instrument_definition),
      formation_start=win.start_ns,formation_end=win.end_ns,coverage_ok=win.coverage_ok,member_count=len(win.rows),
      raw_member_locators=win.raw_member_locators,coverage_evidence=dict(win.coverage_evidence))


def profile(win,name,kind,session_day,*,fraction=None,source_clock_id=None):
    cfg={'as_of':win.end_ns,'variant':'comparison','profile_definition':dict(profile_id=name,selection_known_at=win.start_ns,
      source_id='phase1-v2-explicit-native-control',window=dict(window_id=name+':window',kind=kind,
      session_date=session_day.isoformat(),start=win.start_ns,end=win.end_ns,source_clock_id=source_clock_id),
      value_area=None if fraction is None else dict(config_id='comparison-reference-sires-fraction-'+fraction,fraction=fraction,algorithm=None,tie_policy=None))}
    result=pi._native('O063' if kind=='developing_rth' else 'O061',cfg,win.resolved)
    validate_output(result)
    snapshot=pi.snapshot_from_payload(result.value)
    signed=p.o077({'profile':snapshot});validate_output(signed)
    payload=save_payload(name,dict(schema='phase1-complete-native-profile-result-v2',configuration=cfg,
       profile=asdict(result),signed_profile=asdict(signed),native=native_summary(win)))
    summary={key:result.value[key] for key in ('profile_id','snapshot_id','kind','instrument_id','formation_start','formation_end','as_of','known_at','total_volume','H','L','poc','poc_candidates','value_area_fraction','val','vah','coverage_ok')}
    summary.update(known_delta=signed.value['known_window_delta'],full_delta=signed.value['window_delta'],delta_interval=signed.value['delta_interval'],
       unknown_volume=sum((row.unknown_volume for row in snapshot.rows),Decimal(0)),native_rows=len(snapshot.rows),member_count=len(snapshot.event_ids),payload=payload,
       holes=result.hole_ids,variant='comparison',configuration_interpretation='Native control windows are explicit; this does not recover unreadable source profile clocks. The overnight 40% fraction references the documented Sires setting, not a recovered Jumbo setting; its expansion remains unknown.')
    return snapshot,summary


def profile_plot(ax,snapshot,title):
    px=[float(r.price) for r in snapshot.rows];buy=np.array([float(r.buy_volume) for r in snapshot.rows]);sell=np.array([float(r.sell_volume) for r in snapshot.rows]);unknown=np.array([float(r.unknown_volume) for r in snapshot.rows])
    h=float(snapshot.tick_size)*.92
    ax.barh(px,buy,height=h,color=COLORS['buy'],label='B buy')
    ax.barh(px,sell,left=buy,height=h,color=COLORS['sell'],label='A sell')
    ax.barh(px,unknown,left=buy+sell,height=h,color=COLORS['unknown'],label='N unknown')
    if snapshot.poc is not None:ax.axhline(float(snapshot.poc),color=COLORS['ink'],lw=.8,ls='--')
    ax.set_title(title,fontsize=10,loc='left');ax.set_xlabel('Executed volume');ax.ticklabel_format(axis='x',style='sci',scilimits=(0,0))
    ax.grid(axis='y',color='#e6ebef',lw=.5)


def gb_failure(catalog):
    day=date(2025,11,20);win=window(OHLC,day,(8,0),(11,2),instrument=158704);bars=bars_from_window(win,2)
    ref=[r for r in win.rows if et_ns(day,9,0)<=r['start']<et_ns(day,10,0)]
    rh,rl=max(r['H'] for r in ref),min(r['L'] for r in ref)
    sweep=[r for r in bars if r['start']>=et_ns(day,10,0) and r['H']>rh]
    # The source eye/position is on the later sweep near 10:40. The earlier
    # post-10:00 touch is not this annotated attempt. This broad source reading
    # selects a comparison region retrospectively, never a historical signal.
    source_region=[r for r in sweep if et_ns(day,10,30)<=r['start']<et_ns(day,10,44)]
    first=max(source_region,key=lambda r:r['H']) if source_region else None
    fig,axes=plt.subplots(2,1,figsize=(13,10),gridspec_kw={'height_ratios':[1.0,1.3]},layout='constrained')
    original,source=source_image(catalog,'GB:43',(.085,.083,.915,.34));axes[0].imshow(original);axes[0].axis('off');axes[0].set_title('Original GB p.43 · MNQZ2025 · 2-minute display',loc='left')
    candle_plot(axes[1],bars,'Repaired native comparison · NQZ5 · 2-minute complete bars')
    axes[1].axhline(float(rh),color=COLORS['blue'],ls='--',lw=1,label='Frozen 09–10 NQ high')
    axes[1].axhline(float(rl),color=COLORS['blue'],ls=':',lw=1,label='Frozen 09–10 NQ low')
    axes[1].axhline(25301.75,color=COLORS['gold'],lw=1.2,label='Source MNQ displayed short price 25301.75')
    if first:
        axes[1].axvspan(mdates.date2num(ns_to_et(first['start'])),mdates.date2num(ns_to_et(first['end'])),alpha=.12,color=COLORS['gold'])
        axes[1].annotate('Native peak in the source-annotated\nlater sweep region; exact fill time unknown',xy=(mdates.date2num(ns_to_et(first['start'])),float(first['H'])),xytext=(-245,-70),textcoords='offset points',arrowprops={'arrowstyle':'->','color':COLORS['ink']},fontsize=9)
    axes[1].legend(loc='lower left',fontsize=8)
    fig.suptitle('November 20: preserve the sweep entry and later annotations separately',fontsize=15,weight='bold')
    fig.supxlabel('MNQ is the source display. NQ is a price comparison; no NQ fill, exact entry timestamp or trade return is inferred.',fontsize=10)
    path=OUT/'GB-FAIL-2025-11-20.png';fig.savefig(path,dpi=150);plt.close(fig)
    result=dict(case_id='GB-FAIL-2025-11-20',source=source,native=native_summary(win),bars=bars,
      frozen_09_10_range={'L':rl,'H':rh,'known_at':et_ns(day,10,0)},source_region_native_peak_bar=first,
      source_region={'start_et':'10:30','end_et':'10:44','status':'inference','reason':'Broad region around the visible eye/position annotation; selected retrospectively from original figure.'},
      observed_source_position_price='25301.75',source_instrument='MNQZ2025',comparison_instrument='NQZ5',
      entry_requirement='sweep; later MSS/FVG annotations are not imposed on this observed entry',
      exact_source_fill=None,source_case_agreement='price path and sweep region comparable; native fill identity not comparable',
      implementation_evidence=['O004 complete clock bars','native resolved locator/window coverage'],historical_discovery='unavailable_selector',chart=path.name)
    save_json(OUT/'GB-FAIL-2025-11-20.json',result);print('rendered',path.name,flush=True)
    return result


def gb_vwap(catalog):
    day=date(2026,2,24);win=window(OHLC,day,(18,0),(10,30),instrument=42002475,previous_start=True)
    all_bars=bars_from_window(win,1);bars=[b for b in all_bars if b['start']>=et_ns(day,8,30)]
    cfg=dict(reset_id='comparison-prior-1800',reset_at=win.start_ns,reset_verified=True,basis='HLC3',variant='comparison',as_of=win.end_ns)
    # One frozen prior comparison only: no reset/basis/timeframe fitting grid.
    result=context.native_vwap(cfg,win.resolved);validate_output(result)
    curve=[];pv=v=Decimal(0)
    for bar in all_bars:
        pv+=(bar['H']+bar['L']+bar['C'])/3*bar['V'];v+=bar['V']
        curve.append({'as_of':bar['end'],'vwap':None if v==0 else pv/v})
    asia=[b for b in all_bars if et_ns(day-timedelta(days=1),20,0)<=b['start']<et_ns(day,0,0)]
    london=[b for b in all_bars if et_ns(day,2,0)<=b['start']<et_ns(day,5,0)]
    ah=max(b['H'] for b in asia);lh=max(b['H'] for b in london)
    confirmations=[b for b in bars if b['start']>=et_ns(day,9,30) and b['C']>max(ah,lh)]
    confirmation=confirmations[0] if confirmations else None
    previous={c['as_of']:c['vwap'] for c in curve}
    retest=None
    if confirmation:
        retest=next((dict(bar_id=b['bar_id'],start=b['start'],known_at=b['end'],prior_vwap=previous.get(b['start'])) for b in bars
          if b['start']>=confirmation['end'] and previous.get(b['start']) is not None and b['L']<=previous[b['start']]<=b['H']),None)
    fig,axes=plt.subplots(2,1,figsize=(13,10),gridspec_kw={'height_ratios':[1.0,1.3]},layout='constrained')
    original,source=source_image(catalog,'GB:33',(.09,.515,.91,.77));axes[0].imshow(original);axes[0].axis('off');axes[0].set_title('Original GB p.33 · timeframe label not readable',loc='left')
    candle_plot(axes[1],bars,'Frozen prior comparison · NQH6 · 1-minute bars, HLC3, previous 18:00 reset')
    visible=[c for c in curve if et_ns(day,8,30)<=c['as_of']<=win.end_ns]
    axes[1].plot([ns_to_et(c['as_of']) for c in visible],[float(c['vwap']) for c in visible],color=COLORS['blue'],lw=1.5,label='Comparison VWAP at bar close')
    axes[1].axhline(float(ah),color=COLORS['gold'],ls='--',lw=.8,label='Comparison Asia high (20–00)')
    axes[1].axhline(float(lh),color=COLORS['ink'],ls=':',lw=.8,label='Comparison London high (02–05)')
    if retest:axes[1].annotate('First later bar touches\nprior completed VWAP',xy=(ns_to_et(retest['start']),float(retest['prior_vwap'])),xytext=(45,-55),textcoords='offset points',arrowprops={'arrowstyle':'->'},fontsize=9)
    axes[1].legend(loc='upper left',fontsize=8)
    fig.suptitle('February 24: continuation sequence retained; VWAP settings remain a comparison',fontsize=15,weight='bold')
    fig.supxlabel('No new fitting grid. Source session clocks, price basis, exact fill and timeframe remain unverified.',fontsize=10)
    path=OUT/'GB-VWAP-2026-02-24.png';fig.savefig(path,dpi=150);plt.close(fig)
    payload=dict(case_id='GB-VWAP-2026-02-24',source=source,native=native_summary(win),bars=bars,comparison_configuration=cfg,
      full_window_vwap=asdict(result),curve=curve,asia_high=ah,london_high=lh,close_above_both=confirmation,later_retest=retest,
      source_case_agreement='same opening reversal/pullback/continuation shape; author settings not identified',
      no_new_parameter_search=True,comparison_sequence_window_start=et_ns(day,9,30),
      sequence_window_reason='Frozen prior reconstruction evaluates the source opening reversal and continuation after 09:30.',
      exact_fill=None,historical_discovery='unavailable_selector',chart=path.name)
    save_json(OUT/'GB-VWAP-2026-02-24.json',payload);print('rendered',path.name,flush=True)
    return payload


def dated_profiles(catalog):
    day=date(2026,6,12);prior=day-timedelta(days=1)
    specs=[('prior-rth','prior_rth',prior,(9,30),(16,0),False),
           ('prior-eth','prior_eth',prior,(18,0),(17,0),True),
           ('overnight','overnight',day,(18,0),(9,30),True),
           ('developing-rth','developing_rth',day,(9,30),(11,55),False),
           ('selected-range','selected_range',day,(6,0),(9,0),False)]
    snapshots=[];summaries=[]
    for name,kind,session,start,end,previous_start in specs:
        print('collect profile',name,flush=True)
        win=window(TRADES,session,start,end,instrument=42004058,previous_start=previous_start)
        snapshot,summary=profile(win,'2026-06-12-'+name,kind,session,fraction='.40' if kind=='overnight' else None,
          source_clock_id='O011:sires_overnight_1800_0930_et' if kind=='overnight' else 'explicit_native_control')
        snapshots.append(snapshot);summaries.append(summary)
    fig=plt.figure(figsize=(16,11),layout='constrained');gs=fig.add_gridspec(2,5,height_ratios=[.9,1.6])
    original,source=source_image(catalog,'JR:4',(.13,.52,.87,.80));ax=fig.add_subplot(gs[0,:]);ax.imshow(original);ax.axis('off');ax.set_title('Original Jumbo June 12 profile panels · their exact formation clocks are not readable',loc='left')
    for i,(snapshot,(name,*_)) in enumerate(zip(snapshots,specs)):
        ax=fig.add_subplot(gs[1,i]);start,end=ns_to_et(snapshot.formation_start),ns_to_et(snapshot.formation_end)
        profile_plot(ax,snapshot,name.replace('-',' ').title()+'\n'+start.strftime('%m/%d %H:%M')+'–'+end.strftime('%m/%d %H:%M'))
        if i==0:ax.set_ylabel('Native NQM6 price');ax.legend(fontsize=7,loc='lower right')
    fig.suptitle('Distinct dated profiles from native rows · no equal-price identity joins',fontsize=16,weight='bold')
    fig.supxlabel('These explicit native windows validate profile production and separation. They are not claimed as the author’s unreadable profile settings.\nGreen B=buy, red A=sell, gray N=unknown. Dashed line is a unique volume POC; unknown VA expansion remains unplotted.',fontsize=10)
    path=OUT/'JJ-profiles-2026-06-12.png';fig.savefig(path,dpi=145);plt.close(fig)
    result=dict(case_id='JJ-profiles-2026-06-12',source=source,profiles=summaries,chart=path.name,
      source_case_agreement='separate native profile structure verified; source exact-window/value-area agreement not measurable',
      source_unknowns=['formation windows of each source profile','chart timeframe','VA expansion and POC tie policy'],
      historical_discovery='unavailable_selector')
    save_json(OUT/'JJ-profiles-2026-06-12.json',result);print('rendered',path.name,flush=True)
    return result


def dated_loss_context(catalog):
    day=date(2026,7,23);win=window(OHLC,day,(9,30),(11,0),instrument=42004177);bars=bars_from_window(win,1)
    case=next(c for c in catalog['cases'] if c['case_id']=='SIRES-losses-2026-07-23')
    attempts=case['observed_decision']['value']['attempts']
    fig=plt.figure(figsize=(14,10),layout='constrained');gs=fig.add_gridspec(3,1,height_ratios=[.9,.4,1.4])
    ax=fig.add_subplot(gs[0]);original,source=source_image(catalog,'ANAT:6',(.08,.39,.92,.64));ax.imshow(original);ax.axis('off');ax.set_title('Original source attempt outcomes · five losses and four wins, preserved in order',loc='left')
    ax=fig.add_subplot(gs[1]);ax.axis('off')
    for i,attempt in enumerate(attempts):
        color=COLORS['buy'] if attempt['outcome']=='win' else COLORS['sell']
        ax.text((i+.5)/9,.7,str(i+1)+' · '+attempt['display_clock']+'\n'+attempt['outcome'].upper(),ha='center',va='center',transform=ax.transAxes,color=color,fontsize=10,weight='bold')
    ax.text(.5,.08,'Caption says the first four hurt; the third plotted result is positive. Both source statements remain recorded.',ha='center',transform=ax.transAxes,fontsize=9)
    ax=fig.add_subplot(gs[2]);candle_plot(ax,bars,'Native NQU6 date context · one-minute control; source chart timeframe and clock zone unknown')
    fig.suptitle('July 23: retain early attempts and losses without inventing fill records',fontsize=15,weight='bold')
    fig.supxlabel('Source display times are not overlaid as exchange fills. This native panel provides dated context only; no attempt price or PnL is inferred.',fontsize=10)
    path=OUT/'SIRES-losses-2026-07-23.png';fig.savefig(path,dpi=150);plt.close(fig)
    payload=dict(case_id=case['case_id'],source=source,attempts=attempts,native=native_summary(win),bars=bars,
      source_conflict=case['later_annotations'][-1],source_case_agreement='source sequence retained; execution-level alignment unavailable',
      chart=path.name,exact_fills=[],historical_discovery='unavailable_selector')
    save_json(OUT/(case['case_id']+'.json'),payload);print('rendered',path.name,flush=True)
    return payload


def source_limitations(catalog):
    selected={'JJ-range-control-2026-02-24','GB-FAIL-2025-11-20','GB-VWAP-2026-02-24','JJ-profiles-2026-06-12','SIRES-losses-2026-07-23'}
    rows=[]
    for case in catalog['cases']:
        if case['case_id'] in selected:continue
        ref=case['source_refs'][0];image,provenance=source_image(catalog,ref)
        rows.append(dict(case_id=case['case_id'],method_id=case['method_id'],evidence_mode=case['evidence_mode'],
          source=provenance,observed_decision=case['observed_decision'],timeframe=case['timeframe'],
          source_case_agreement='not measurable as a dated native source comparison',
          reason='; '.join(case['missing_fields']),implementation_validation='see obligation matrix for object computations and invariant fixtures'))
    save_json(OUT/'source-case-limitations.json',rows)
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',choices=['gb-failure','gb-vwap','profiles','losses','source-records','all'],default='all');args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);catalog=load_catalog(verify_sources=True)
    functions={'gb-failure':gb_failure,'gb-vwap':gb_vwap,'profiles':dated_profiles,'losses':dated_loss_context,'source-records':source_limitations}
    selected=functions if args.case=='all' else {args.case:functions[args.case]}
    for _,fn in selected.items():fn(catalog)


if __name__=='__main__':main()
