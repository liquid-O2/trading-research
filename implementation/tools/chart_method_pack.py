#!/usr/bin/env python3
"""Dated geometry diagnostics for method-pack-v1; never creates method candidates.

Run from the repo root with the implementation/data, matplotlib and PyMuPDF
runtime. Selection is fixed below before reading market values. Every diagnostic
writes its actual inputs, native identities, source references and null method
claims. Visual judgments belong in CHART_CHECK.md after manual inspection.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'implementation/src'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pymupdf
from trading_research.research.method_pack import objects  # registration only; no fixtures run
from trading_research.research.method_pack.adapters import normalize_ohlcv_row, instrument_tick
from trading_research.research.method_pack.protocol import RECIPES
from trading_research.research.method_pack.report import sha256_file

OUT = ROOT / 'implementation/reports/phase1-live/methods/charts'
DATA = ROOT / 'data'
ET = 'America/New_York'
D = Decimal
BLUE, ORANGE, GREEN, RED, GRAY = '#1768a6', '#d17b24', '#167d68', '#b74b4b', '#657384'
COMMON_DATE = '2026-02-24'  # Date printed in GB p.33, selected before outcomes.
GB = 'sources/x-raw-2026-09-11/greenbirdtrader-complete.pdf'
DISC = 'sources/documents/discretionary/'
TBR = 'sources/documents/jumbo/Time-Based ranges Framework (JJumbo).pdf'
PLANS = [
 {'id':'M01','method':'JJ-TBR','date':COMMON_DATE,'view':['06:00','12:00'], 'geometry':['O005','O007','O014','O015'], 'references':[(TBR,4),(TBR,21)], 'selection':'Common source-dated diagnostic session, not a Jumbo source case.'},
 {'id':'M02','method':'GB-FAIL','date':'2025-11-20','view':['08:00','12:00'], 'geometry':['O046','O048'], 'references':[(GB,43),(GB,25)], 'selection':'Date visible in p.43. Source chart is MNQZ5; acquired chart is native NQZ5 price comparison, not the same instrument or an admitted source attempt.'},
 {'id':'M03','method':'GB-VWAP','date':COMMON_DATE,'view':['08:20','10:40'], 'geometry':['O030'], 'references':[(GB,33)], 'selection':'Date printed in the continuation source post. Two explicitly named comparison resets; neither is a verified Green Bird reset.'},
 {'id':'M04','method':'GB-SCALP','date':'2026-09-02','view':['09:00','11:00'], 'geometry':['O046','O053'], 'references':[(GB,40)], 'selection':'Source bearish-scalp date; fully covered morning only. Completed 09:00-10:00 parent is a comparison choice, not the unpublished selected impulse.'},
 {'id':'M05','method':'SIRES','date':COMMON_DATE,'view':['09:30','10:30'], 'geometry':['O078','O082'], 'references':[(DISC+'tpo-lesson-3.pdf',3)], 'selection':'Common source-dated diagnostic. Published A/B clocks and initial-balance extrema only; no inferred TPO row construction or execution branch.'},
 {'id':'M06','method':'SAINT-AMT','date':COMMON_DATE,'view':['09:30','11:00'], 'geometry':['O061','O064'], 'references':[(DISC+'reading-the-volume-profile.pdf',4)], 'selection':'Common source-dated diagnostic. Native volume-at-price over chosen 09:30-10:00 display interval; source auction/bin/VA selection remains unknown.'},
 {'id':'M07','method':'MEMBER-TWO-REASONS','date':COMMON_DATE,'view':['09:30','11:00'], 'geometry':['O061'], 'references':[(DISC+'10k-first-month.pdf',7),(DISC+'10k-first-month.pdf',8)], 'selection':'Common source-dated diagnostic. Native volume map only. The source ticket is ES; no ES reaction area, minor HVN or ticket is transferred to NQ.'},
 {'id':'M08','method':'KEANI-OPEN-ABOVE-VALUE','date':COMMON_DATE,'view':['09:30','11:00'], 'geometry':['O078','O050'], 'references':[(DISC+'average-unprofitable-trader.pdf',22)], 'selection':'Common source-dated diagnostic. Complete A low and opening price; no guessed prior/developing VAH or imbalance band.'},
 {'id':'M09','method':'REFILL-STUDY','date':COMMON_DATE,'view':['09:30','09:40'], 'geometry':['O098','O099'], 'references':[(DISC+'refill-effect.pdf',7),(DISC+'refill-effect.pdf',12),(DISC+'origin-of-the-move.pdf',18)], 'selection':'Common source-dated diagnostic, fixed first ten minutes. All native executions displayed without size threshold or cluster/zone selector.'},
 {'id':'M10','method':'JETBUNDLE-STATES','date':COMMON_DATE,'view':['09:30','10:00'], 'geometry':['O098','O164'], 'references':[(DISC+'the-math-behind-auction-market-theory.pdf',10)], 'selection':'Native NQ input diagnostic only. Missing AAPL ten-level sample and state classifier prevent source-state geometry/transition reproduction.'},
 {'id':'M11','method':'STOIC-DATA','date':COMMON_DATE,'geometry':['O162'], 'references':[(DISC+'data-engine.pdf',5)], 'selection':'Civil-date CPI vintage illustration as of the common date, not a session decision or disclosed Stoic series/score model.'},
 {'id':'M12','method':'STOIC-RISK','date':None,'geometry':['O155'], 'references':[(DISC+'data-engine.pdf',7),(DISC+'data-engine.pdf',8)], 'selection':'Printed baseline arithmetic only. No acquired process journal or risk decisions exist, so no dated historical session can be charted.'},
]
CACHE = {}
RESULTS = []
HOLES = []
SOURCE_META = {}


def ns(day, clock):
    return int(pd.Timestamp(f'{day} {clock}', tz=ET).value)


def dt(value):
    return pd.to_datetime(value, unit='ns', utc=True).tz_convert(ET)


def serial(value):
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.floating,)): return float(value)
    if isinstance(value, D): return str(value)
    if isinstance(value, Path): return str(value)
    if isinstance(value, (pd.Timestamp, date)): return value.isoformat()
    if isinstance(value, np.ndarray): return value.tolist()
    raise TypeError(type(value).__name__)


def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=serial)+'\n')


def source_meta(path):
    path = Path(path)
    key = str(path)
    if key not in SOURCE_META:
        SOURCE_META[key] = {'path':key,'sha256':sha256_file(path),'bytes':path.stat().st_size}
    return SOURCE_META[key]


def read_window(day, start, end, kind='bars'):
    a, b = ns(day,start), ns(day,end)
    if kind == 'bars':
        path = DATA/f'quantpad/cme__nq-continuous-futures__ohlcv-1m/{day[:4]}.parquet'
        unit=1_000_000
    else:
        monday=date.fromisoformat(day)-timedelta(days=date.fromisoformat(day).weekday())
        path=DATA/f'quantpad/cme__nq-continuous-futures__trades/{monday.isoformat()}.parquet'
        unit=1
    return read_bounds(path,a,b,unit,kind)


def read_bounds(path,a,b,unit,kind):
    key=(str(path),a,b)
    if key in CACHE: return CACHE[key].copy()
    frame=pq.read_table(path,filters=[('t','>=',a//unit),('t','<',b//unit)]).to_pandas().sort_values('t',kind='stable').reset_index(drop=True)
    assert len(frame), (path,a,b)
    assert frame.instrument_id.nunique()==1, 'Cross-contract diagnostic'
    if kind=='bars':
        assert frame.t.is_unique
        expected=np.arange(a//unit,b//unit,60_000,dtype=np.int64)
        assert np.array_equal(frame.t.to_numpy(),expected), 'Incomplete minute interval'
        assert frame[['o','h','l','c','v']].notna().all().all()
        assert ((frame.l<=frame[['o','c']].min(axis=1)) & (frame.h>=frame[['o','c']].max(axis=1))).all()
    else:
        assert (frame['flags']==0).all(), 'Unresolved native trade flags'
        assert frame.side.isin(['A','B','N']).all()
        assert (frame['size']>0).all()
    frame.attrs={'source':source_meta(path),'start_ns':a,'end_ns':b,'time_unit':'ms' if unit==1_000_000 else 'ns','kind':kind}
    CACHE[key]=frame
    return frame.copy()


def identity(frame):
    mid=int(frame.instrument_id.iloc[0])
    path=DATA/'derived/continuous-futures__instrument-and-roll-maps/nq-instruments.parquet'
    item=pq.read_table(path,filters=[('instrument_id','=',mid)]).to_pylist()[0]
    q=instrument_tick(DATA,mid)
    assert q is not None and q>0
    return {'instrument_id':mid,'symbol':item['raw_symbol'],'q':str(q),'definition_map':source_meta(path),'source_instrument_match':None}


def record_input(plan,name,frame):
    path=OUT/f"{plan['id']}-{name}.csv"
    frame.to_csv(path,index=False)
    return {'path':str(path),'sha256':sha256_file(path),'row_count':len(frame),**frame.attrs}


def hole(plan,fields,reason,kind='source_definition'):
    row={'hole_id':f"CHART:{plan['id']}:{':'.join(fields)}",'method_id':plan['method'],'recipe_id':plan['id'],'candidate_id':None,'kind':kind,'missing_fields':fields,'reason':reason,'affected_output':'source_chart_reconstruction','excluded_from_historical_sample':True}
    HOLES.append(row)
    return row['hole_id']


def setup(plan,subtitle,nrows=1,widths=None):
    fig=plt.figure(figsize=(14,8),facecolor='#fcfcfa')
    if widths:
        grid=fig.add_gridspec(1,len(widths),width_ratios=widths,left=.07,right=.95,bottom=.21,top=.80,wspace=.18)
        axes=[fig.add_subplot(grid[0,i]) for i in range(len(widths))]
    else:
        axes=fig.subplots(nrows,1,squeeze=False).ravel().tolist()
        fig.subplots_adjust(left=.075,right=.95,bottom=.23,top=.79,hspace=.30)
    fig.text(.075,.94,f"{plan['id']}  {plan['method']}",fontsize=21,weight='bold',color='#24384a')
    fig.text(.075,.89,subtitle,fontsize=12,color='#43576a')
    for ax in axes:
        ax.set_facecolor('#fcfcfa'); ax.grid(axis='y',alpha=.14)
        ax.spines[['top','right']].set_visible(False)
        ax.tick_params(labelsize=9)
    return fig,axes


def clock_axis(ax,day,start,end):
    ax.set_xlim(dt(ns(day,start)),dt(ns(day,end)))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M',tz=ET))
    if ns(day,end)-ns(day,start)<=20*60_000_000_000:
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=2,tz=ET))
    else:
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=5,maxticks=10))
    ax.set_xlabel('America/New_York (ET)')
    ax.ticklabel_format(axis='y',style='plain',useOffset=False)


def candles(ax,frame,minutes=1):
    bars=frame.copy()
    if minutes>1:
        bars['bucket']=bars.t//(minutes*60_000)*(minutes*60_000)
        bars=bars.groupby('bucket',as_index=False).agg(t=('t','min'),o=('o','first'),h=('h','max'),l=('l','min'),c=('c','last'),v=('v','sum'))
    # Glyph occupies its interval. Its full OHLC is available only at the end.
    # Establish date units before adding wick collections. Changing units
    # afterwards invokes Matplotlib relim(), which omits collections and can
    # clip the wicks to candle-body bounds.
    ax.xaxis.update_units(pd.to_datetime(bars.t,unit='ms',utc=True).dt.tz_convert(ET).to_list())
    x=mdates.date2num(pd.to_datetime(bars.t+minutes*30_000,unit='ms',utc=True))
    colors=np.where(bars.c>=bars.o,GREEN,RED)
    ax.vlines(x,bars.l,bars.h,colors=colors,lw=.6)
    ax.bar(x,(bars.c-bars.o).abs().clip(lower=.05),bottom=bars[['o','c']].min(axis=1),width=minutes*.67/1440,color=colors,alpha=.88,zorder=3)
    ax.set_ylabel('Native NQ price (points)')
    ax._method_price_bounds=(float(bars.l.min()),float(bars.h.max()))


def frozen_line(ax,day,start,end,value,label,color=BLUE,style='-'):
    ax.plot([dt(ns(day,start)),dt(ns(day,end))],[float(value)]*2,color=color,ls=style,lw=1,label=label)


def finish(plan,fig,notes,values,inputs,ident=None):
    refs='; '.join(f"{Path(p).name} p.{n}" for p,n in plan['references'])
    fig.text(.075,.125,notes,fontsize=10,color='#30465a',va='top',linespacing=1.5)
    fig.text(.075,.047,'Geometry / input diagnostic only. No candidate IDs, entry verdicts or historical method observations.',fontsize=9,color='#a14a24')
    fig.text(.075,.021,'Source comparison: '+refs,fontsize=8,color=GRAY)
    path=OUT/f"{plan['id']}-{plan['method'].lower()}.png"
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    for ax in fig.axes:
        bounds=getattr(ax,'_method_price_bounds',None)
        if bounds:
            low,high=ax.get_ylim()
            assert low<=bounds[0] and high>=bounds[1], 'Chart clips native candle wicks'
    for text in fig.texts:
        box=text.get_window_extent(renderer)
        assert box.x0>=0 and box.x1<=fig.bbox.width and box.y0>=0 and box.y1<=fig.bbox.height, 'Clipped chart text'
    fig.savefig(path,dpi=160,facecolor=fig.get_facecolor())
    plt.close(fig)
    RESULTS.append({**plan,'chart':str(path),'chart_sha256':sha256_file(path),'native_identity':ident,'measurements':values,'inputs':inputs,'hole_ids':[h['hole_id'] for h in HOLES if h['recipe_id']==plan['id']], 'visual_review':'requires manual inspection; see CHART_CHECK.md','historical_N':0,'method_rate':None,'method_interval':None})
    print(path.name,flush=True)


def closed_range(frame,start,end,day,rid='O005'):
    a,b=ns(day,start),ns(day,end)
    part=frame[(frame.t>=a//1_000_000)&(frame.t<b//1_000_000)]
    members=[normalize_ohlcv_row(row,source_file=frame.attrs['source']['path'],source_row=i) for i,row in enumerate(part.to_dict('records'))]
    out=RECIPES[rid]({'members':members,'start_ns':a,'end_ns':b,'use_at':b,'session_id':f'{day}:{start}-{end}'}).value
    assert out['H']==D(str(part.h.max())) and out['L']==D(str(part.l.min()))
    return out


def chart_m01(plan):
    day=plan['date']; bars=read_window(day,*plan['view']); ident=identity(bars)
    r=closed_range(bars,'06:00','09:00',day)
    L,H=r['L'],r['H']; W=H-L
    parent=f"{ident['symbol']}:{day}:06:00-09:00_ET"
    eq=RECIPES['O007']({'L':L,'H':H,'parent_id':parent,'known_at':ns(day,'09:00')}).value
    ext=RECIPES['O015']({'L':L,'H':H,'parent_id':parent,'known_at':ns(day,'09:00')}).value
    assert ext['upper_band']==[H+D('1.33')*W,H+D('1.66')*W]
    fig,(ax,)=setup(plan,f"{day} | {ident['symbol']} | 06:00-09:00 range, frozen at 09:00 | 5-minute display from complete minutes")
    candles(ax,bars,5); ax.axvspan(dt(ns(day,'06:00')),dt(ns(day,'09:00')),color=GRAY,alpha=.09)
    for name,v,col,ls in [('H',H,GRAY,'-'),('75%',eq['q75'],ORANGE,':'),('EQ',eq['eq'],BLUE,'-'),('25%',eq['q25'],ORANGE,':'),('L',L,GRAY,'-'),('H + 0.5W',H+W/2,GRAY,'--'),('L - 0.5W',L-W/2,GRAY,'--')]:
        frozen_line(ax,day,'09:00','12:00',v,f'{name}: {v}',col,ls)
    for name,band in [('Upper 1.33-1.66',ext['upper_band']),('Lower 1.33-1.66',ext['lower_band'])]:
        ax.fill_between([dt(ns(day,'09:00')),dt(ns(day,'12:00'))],float(band[0]),float(band[1]),color=GREEN,alpha=.12,label=f'{name}: {band[0]} to {band[1]}')
    ax.axvline(dt(ns(day,'09:00')),color=GRAY,lw=1)
    ax.legend(loc='upper left',fontsize=8,ncol=2,framealpha=.94)
    clock_axis(ax,day,*plan['view'])
    hole(plan,['context_selector','confirmation_selector'],'Computed range and all displayed projection coordinates do not select a Jumbo branch or permitted reaction.')
    values={**r,**eq,**ext,'width_ticks':W/D(ident['q']),'source_location_selected':None,'rounded_projection_prices':False}
    finish(plan,fig,'Source p.21 shows projections measured beyond H/L. Both sides use the same frozen W.\nOff-tick endpoints remain exact; the shaded bands are geometry, not selected trade locations.',values,[record_input(plan,'minutes',bars)],ident)


def chart_m02(plan):
    day=plan['date']; bars=read_window(day,*plan['view']); trades=read_window(day,'10:00','12:00','trades'); ident=identity(bars)
    assert int(trades.instrument_id.iloc[0])==ident['instrument_id']
    r=closed_range(bars,'09:00','10:00',day,'O046'); H,L=r['H'],r['L']
    five=bars.copy(); five['bucket']=five.t//300000*300000
    five=five.groupby('bucket',as_index=False).agg(t=('t','min'),c=('c','last'),h=('h','max'),l=('l','min'),members=('t','count'))
    assert (five.members==5).all()
    fig,(ax,)=setup(plan,f"{day} | {ident['symbol']} | source p.43 is MNQZ5 | NYAM 09:00-10:00 and completed 5-minute closes")
    candles(ax,bars,5); ax.axvspan(dt(ns(day,'09:00')),dt(ns(day,'10:00')),color=GRAY,alpha=.09)
    frozen_line(ax,day,'10:00','12:00',H,f'NYAM H {H}'); frozen_line(ax,day,'10:00','12:00',L,f'NYAM L {L}',ORANGE)
    events=[]
    for side,bound,test,col in [('upper',H,trades.price>float(H),BLUE),('lower',L,trades.price<float(L),ORANGE)]:
        crossed=trades[test]
        if crossed.empty:
            events.append({'side':side,'first_sweep_ns':None,'first_complete_return_close_ns':None}); continue
        first=crossed.iloc[0]; at=int(first.t)
        close=five[((five.t+300000)*1_000_000>at)&(five.t>=ns(day,'10:00')//1_000_000)&(five.c<float(H))&(five.c>float(L))]
        item={'side':side,'first_sweep_ns':at,'first_sweep_price':float(first.price),'first_complete_return_close_ns':None}
        ax.scatter(dt(at),first.price,color=col,marker='^',s=55,zorder=5,label=f'{side} first literal sweep {dt(at).strftime("%H:%M:%S")}')
        if not close.empty:
            row=close.iloc[0]; close_at=int(row.t+300000)*1_000_000
            item.update(first_complete_return_close_ns=close_at,close=float(row.c))
            ax.scatter(dt(close_at),row.c,color=col,marker='D',s=38,zorder=5,label=f'{side} first 5m close back inside {dt(close_at).strftime("%H:%M")}')
        events.append(item)
    ax.legend(loc='lower left',fontsize=9,framealpha=.94); clock_axis(ax,day,*plan['view'])
    hole(plan,['source_bias','session_admission','risk_objective'],'Literal sweeps and five-minute closes are measurement events, not source-complete GB-FAIL candidates.')
    hole(plan,['native_source_instrument'],'The source screenshot is MNQZ5, while the selected NQ study data is NQZ5; only price-geometry comparison is claimed.','identity')
    finish(plan,fig,'NYAM boundaries start at 10:00; later bars cannot alter them. Diamonds mark close availability.\nBoth boundary observations are retained. No bias, trade selection, MSS/FVG, stop or objective is inferred.',{**r,'literal_boundary_events':events,'source_candidate':None},[record_input(plan,'minutes',bars),record_input(plan,'five-minute-closes',five),{'native_trade_window':trades.attrs,'rows':len(trades)}],ident)


def comparison_vwap(trades,reset,asofs,q):
    chosen=trades[trades.t>=reset].copy()
    ticks=np.rint(chosen.price/float(q)).astype('int64')
    assert np.all(chosen.price.to_numpy()==ticks.to_numpy()*float(q))
    sizes=chosen['size'].to_numpy(dtype=np.int64)
    total=np.cumsum(sizes); weighted=np.cumsum(ticks.to_numpy()*sizes)
    times=chosen.t.to_numpy(); out=[]
    for at in asofs:
        i=np.searchsorted(times,at,side='left')-1
        if i<0: out.append({'as_of_ns':int(at),'volume':0,'price_ticks_times_volume':0,'vwap':None}); continue
        value=D(int(weighted[i]))*q/D(int(total[i]))
        out.append({'as_of_ns':int(at),'volume':int(total[i]),'price_ticks_times_volume':int(weighted[i]),'vwap':str(value)})
    return pd.DataFrame(out)


def chart_m03(plan):
    day=plan['date']; bars=read_window(day,*plan['view']); ident=identity(bars)
    a=ns('2026-02-23','18:00'); b=ns(day,'10:40')
    trades=read_bounds(DATA/'quantpad/cme__nq-continuous-futures__trades/2026-02-23.parquet',a,b,1,'trades')
    proof=read_bounds(DATA/'quantpad/cme__nq-continuous-futures__ohlcv-1m/2026.parquet',a,b,1_000_000,'bars')
    assert int(trades.instrument_id.iloc[0])==ident['instrument_id']
    asofs=np.arange(ns(day,'08:21'),b+1,60_000_000_000,dtype=np.int64)
    fig,(ax,)=setup(plan,f"{day} | {ident['symbol']} | source-dated continuation view | exact trade weighting, two unverified resets")
    candles(ax,bars)
    inputs=[record_input(plan,'minutes',bars),{'native_trade_window':trades.attrs,'rows':len(trades)},{'coverage_minute_window':proof.attrs,'rows':len(proof)}]
    endpoints={}
    for name,reset,col in [('previous-18:00',a,BLUE),('cash-09:30',ns(day,'09:30'),ORANGE)]:
        vals=comparison_vwap(trades,reset,asofs,D(ident['q']))
        use=vals[vals.vwap.notna()]
        ax.plot([dt(int(v)) for v in use.as_of_ns],use.vwap.astype(float),color=col,lw=1.6,label=f'Comparison VWAP: {name} reset (unverified)')
        row=vals[vals.as_of_ns==ns(day,'10:00')].iloc[0].to_dict(); endpoints[name]=row
        source_result=RECIPES['O030']({'trades':trades[trades.t<ns(day,'10:00')].to_dict('records'),'as_of':ns(day,'10:00')-1,'reset_at':reset,'reset_id':name,'reset_verified':False,'basis':'trade_price','instrument_id':ident['instrument_id'],'canonical_tape_id':'quantpad-native-trades'}).value
        assert source_result['vwap'] is None and source_result['comparison_vwap']==D(row['vwap'])
        inputs.append(record_input(plan,name+'-vwap',vals))
    # Independent provider-bar reconciliation; do not hide adjacent boundary differences.
    t=trades.copy(); t['minute']=t.t//60_000_000_000*60000
    grouped=t.groupby('minute').agg(v_trade=('size','sum'),h_trade=('price','max'),l_trade=('price','min'))
    join=proof.set_index('t')[['v','h','l']].join(grouped)
    assert ((join.h==join.h_trade)&(join.l==join.l_trade)).all()
    mismatches=join[join.v!=join.v_trade].reset_index().to_dict('records')
    if mismatches: hole(plan,['minute_volume_boundary_reconciliation'],'Trade and minute-bar volumes differ by +1/-1 in adjacent 10:34/10:35 minutes. Native trade tape is retained for VWAP; no boundary reassignment is inferred.','data_reconciliation')
    hole(plan,['vwap_reset','source_price_basis','asia_london_bounds','breakout_bar'],'The plotted reset alternatives do not identify the source VWAP or complete the session-high breakout/retest sequence.')
    clock_axis(ax,day,*plan['view']); ax.legend(loc='upper left',fontsize=9)
    finish(plan,fig,'The source screenshot has one VWAP. Its reset and price basis are not specified in FORMULAS.\nThese two named comparisons show reset sensitivity; neither is assigned to the source entry.',{'comparison_values_at_10:00':endpoints,'source_vwap':None,'london_high':None,'asia_high':None,'provider_bar_volume_mismatches':mismatches,'trade_high_low_match_all_minutes':True},inputs,ident)


def chart_m04(plan):
    day=plan['date']; bars=read_window(day,*plan['view']); ident=identity(bars); r=closed_range(bars,'09:00','10:00',day,'O046')
    L,H=r['L'],r['H']; mid=(L+H)/2
    later=bars[bars.t>=ns(day,'10:00')//1_000_000].copy(); later['known_at_ns']=(later.t+60000)*1_000_000
    later['position']=[float(RECIPES['O053']({'L':L,'H':H,'price':str(p)}).value['position']) for p in later.c]
    fig,(ax,sub)=setup(plan,f"{day} | {ident['symbol']} | source bearish-scalp date | chosen comparison parent: completed 09:00-10:00",2)
    candles(ax,bars)
    for name,v,col in [('H',H,GRAY),('50%',mid,BLUE),('L',L,GRAY)]: frozen_line(ax,day,'10:00','11:00',v,f'{name}: {v}',col)
    ax.legend(loc='upper left',fontsize=9)
    sub.plot([dt(int(n)) for n in later.known_at_ns],later.position,color=BLUE,lw=1.4)
    sub.axhline(.5,color=ORANGE,ls='--'); sub.set_ylabel('(close - L) / (H - L)')
    for a in [ax,sub]: clock_axis(a,day,*plan['view'])
    hole(plan,['source_selected_impulse','automatic_scalp_admission','position_journal'],'NYAM is a named comparison parent only. M04 gives no automatic scalp trigger or complete dated size/management journal.')
    finish(plan,fig,'The 50% line demonstrates literal range algebra. This does not establish the source pullback parent.\nThe September 10 long case is outside the acquired minute endpoint; this is the covered September 2 morning.',{**r,'comparison_midpoint':mid,'source_parent':None,'automatic_admission':None},[record_input(plan,'minutes',bars),record_input(plan,'range-position',later)],ident)


def chart_m05(plan):
    day=plan['date']; bars=read_window(day,*plan['view']); ident=identity(bars)
    rows=[]
    for label,start,end in [('A','09:30','10:00'),('B','10:00','10:30'),('IB','09:30','10:30')]:
        r=closed_range(bars,start,end,day)
        rows.append({'period':label,'start_et':start,'known_at_et':end,'H':str(r['H']),'L':str(r['L']),'W':str(r['H']-r['L'])})
    fig,(ax,period)=setup(plan,f"{day} | {ident['symbol']} | source 30-minute A/B clocks and first-hour initial balance",widths=[3,1])
    candles(ax,bars)
    ax.axvspan(dt(ns(day,'09:30')),dt(ns(day,'10:00')),color=BLUE,alpha=.08,label='A completes 10:00')
    ax.axvspan(dt(ns(day,'10:00')),dt(ns(day,'10:30')),color=ORANGE,alpha=.08,label='B completes 10:30')
    ax.legend(fontsize=9,loc='upper left'); clock_axis(ax,day,*plan['view'])
    for x,row,col in zip(range(3),rows,[BLUE,ORANGE,GREEN]):
        period.vlines(x,float(row['L']),float(row['H']),lw=6,color=col)
        period.text(x,float(row['H'])+4,row['H'],ha='center',fontsize=8)
        period.text(x,float(row['L'])-7,row['L'],ha='center',va='top',fontsize=8)
    period.set_xticks(range(3),['A\nknown 10:00','B\nknown 10:30','IB\nknown 10:30'])
    period.set_xlim(-.6,2.6); period.margins(y=.12); period.set_ylabel('Completed-period high / low')
    assert D(rows[2]['H'])==max(D(r['H']) for r in rows[:2]); assert D(rows[2]['L'])==min(D(r['L']) for r in rows[:2])
    hole(plan,['tpo_grid_visitation','auction_route','local_flow_confirmation'],'Period extrema and IB are computable; exact plotted TPO membership and complete Sires entry routes are not supplied.')
    finish(plan,fig,'Each letter retains its own period. IB is the union of A and B, available at 10:30.\nNo TPO value area, single-print detector, gamma permission or confirmed Sires entry is inferred.',{'periods':rows,'tpo_membership_construction':None},[record_input(plan,'minutes',bars)],ident)


def profile_for(day,start,end):
    trades=read_window(day,start,end,'trades')
    result=RECIPES['O061']({'trades':trades.to_dict('records'),'native':True,'known_at':ns(day,end)}).value
    bins={D(k):D(v) for k,v in result['bins'].items()}
    assert sum(bins.values())==D(int(trades['size'].sum()))
    assert {float(k):int(v) for k,v in bins.items()}==trades.groupby('price')['size'].sum().to_dict()
    poc=RECIPES['O064']({'bins':result['bins'],'known_at':ns(day,end)}).value
    frame=pd.DataFrame([{'price':float(p),'volume':int(v)} for p,v in sorted(bins.items())])
    return trades,frame,poc


def chart_profile(plan):
    day=plan['date']; bars=read_window(day,*plan['view']); ident=identity(bars)
    trades,profile,poc=profile_for(day,'09:30','10:00')
    fig,(hist,ax)=setup(plan,f"{day} | {ident['symbol']} | exact native volume by price | diagnostic window 09:30-10:00, frozen at 10:00",widths=[1.2,3.5])
    hist.barh(profile.price,profile.volume,height=float(ident['q'])*.92,color=BLUE,alpha=.8)
    hist.set_xlabel('Executed contracts'); hist.set_ylabel('Native price (0.25-point rows)')
    candles(ax,bars); clock_axis(ax,day,*plan['view']); ax.axvline(dt(ns(day,'10:00')),color=GRAY,ls='--',label='Profile available 10:00')
    common_y=(min(bars.l.min(),profile.price.min())-7,max(bars.h.max(),profile.price.max())+7)
    hist.set_ylim(common_y); ax.set_ylim(common_y)
    values={'native_volume':int(profile.volume.sum()),'native_price_rows':len(profile),'profile_known_at_ns':ns(day,'10:00'),'profile_interval':['09:30','10:00'],'source_profile_interval':None,'source_value_area':None,'source_hvn':None}
    if plan['id']=='M06':
        if poc['poc'] is not None:
            frozen_line(ax,day,'10:00','11:00',poc['poc'],f"Native-row POC {poc['poc']}",ORANGE)
            hist.axhline(float(poc['poc']),color=ORANGE,lw=1)
        values['native_row_poc']=poc
        notes='The histogram counts executions at price; the unique maximum gives this diagnostic POC.\nSaint specifies 68% value, but the source VA algorithm/auction selection is missing. VAH/VAL are left null.'
        hole(plan,['source_auction_interval','source_bins','value_area_algorithm','balance_control_selector'],'The native histogram/maximum can be compared to the figure shape, but the selected Saint value and trade route cannot be reconstructed.')
    else:
        notes='The source figures require an independently selected reaction area and minor HVN, then contact.\nOnly the native volume map is computable here. No POC, arbitrary peak or prior high is relabeled as two reasons.'
        values['prior_reaction_band']=None; values['independent_minor_hvn']=None; values['confluence_band']=None
        hole(plan,['source_reaction_area','independent_minor_hvn','confluence_tolerance','native_ES_case'],'The source ES ticket has no reconstructable dated pre-use reaction/HVN record. Native NQ volume is a prerequisite diagnostic only; no source price or ticket is transferred.')
    ax.legend(loc='upper left',fontsize=9)
    finish(plan,fig,notes,values,[record_input(plan,'minutes',bars),record_input(plan,'native-profile',profile),{'native_trade_window':trades.attrs,'rows':len(trades)}],ident)


def chart_m08(plan):
    day=plan['date']; bars=read_window(day,*plan['view']); ident=identity(bars)
    A=bars[bars.t<ns(day,'10:00')//1_000_000]
    low=D(str(A.l.min())); opening=D(str(A.o.iloc[0])); start=ns(day,'09:30'); end=ns(day,'10:00')
    fig,(ax,sub)=setup(plan,f"{day} | {ident['symbol']} | entire A = 09:30-10:00 | A-low becomes available at 10:00",2)
    candles(ax,bars)
    ax.axvspan(dt(start),dt(end),color=BLUE,alpha=.07,label='A observation interval')
    frozen_line(ax,day,'10:00','11:00',low,f'Whole A low {low}',ORANGE)
    frozen_line(ax,day,'09:31','11:00',opening,f'09:30 bar open {opening}; bar known 09:31',GRAY,':')
    sub.step(pd.to_datetime(A.t+60000,unit='ms',utc=True).dt.tz_convert(ET),A.l.cummin(),where='post',color=BLUE,label='Running A low (unfinished before 10:00)')
    sub.scatter(dt(end),float(low),color=ORANGE,s=35,label='Final whole-A low')
    sub.set_ylabel('A low (points)')
    for a in [ax,sub]:
        clock_axis(a,day,*plan['view']); a.legend(loc='upper left',fontsize=8)
    hole(plan,['prior_VAH','developing_VAH','imbalance_band'],'The complete A low is available, but missing source VA construction prevents a_low > prior_vah and the distinct later breakout/retest check.')
    finish(plan,fig,'Open above value and the whole A period above value are different comparisons.\nPrior VAH and later developing VAH remain distinct unknowns; no 70% helper or prior range edge fills either one.',{'A_low':low,'A_open':opening,'A_high':str(A.h.max()),'A_minutes':len(A),'A_known_at_ns':end,'open_bar_known_at_ns':start+60_000_000_000,'prior_vah':None,'developing_vah':None,'a_low_above_prior_vah':None},[record_input(plan,'minutes',bars)],ident)


def chart_m09(plan):
    day=plan['date']; trades=read_window(day,*plan['view'],'trades'); bars=read_window(day,*plan['view']); ident=identity(trades)
    fig,(ax,)=setup(plan,f"{day} | {ident['symbol']} | every acquired execution in 09:30-09:40 | marker area proportional to native size")
    for side,label,col in [('B','Buy aggressor (B)',BLUE),('A','Sell aggressor (A)',ORANGE),('N','Unknown aggressor',GRAY)]:
        part=trades[trades.side==side]
        if not part.empty: ax.scatter(pd.to_datetime(part.t,unit='ns',utc=True),part.price,s=part['size']*4,color=col,alpha=.22,linewidths=0,label=label,rasterized=True)
    clock_axis(ax,day,*plan['view']); ax.set_ylabel('Native executed price (points)'); ax.legend(loc='upper left',fontsize=9)
    byside=trades.groupby('side')['size'].sum().to_dict()
    hole(plan,['source_cluster_rule','NQ_MNQ_normalization','frozen_zone','grade_model'],'Raw prints have computable price/time/size geometry. They do not define source zones, distinct zone-touch episodes, grades or orders.')
    finish(plan,fig,'All sizes are retained: no 100-contract / two-minute / two-tick substitute and no inferred zone rectangles.\nThe later OFM correction remains applicable: this chart supplies no evidence of a positive mechanical-entry edge.',{'executions_displayed':len(trades),'native_volume_by_side':byside,'size_filter':None,'downsampling':None,'source_zones':None,'distinct_source_touches':None,'source_grade':None},[record_input(plan,'minutes',bars),{'native_trade_window':trades.attrs,'rows':len(trades)}],ident)


def chart_m10(plan):
    day=plan['date']; bars=read_window(day,*plan['view']); trades=read_window(day,*plan['view'],'trades'); ident=identity(trades)
    t=trades.copy(); t['minute']=t.t//60_000_000_000*60000
    totals=t.groupby(['minute','side'])['size'].sum().unstack(fill_value=0).reindex(columns=['A','B','N'],fill_value=0)
    totals['signed_delta']=totals.B-totals.A
    frame=totals.reset_index(); frame['known_at_ns']=(frame.minute+60000)*1_000_000
    fig,(ax,sub)=setup(plan,f"{day} | {ident['symbol']} input diagnostic | source requires AAPL ten-level book; state reconstruction blocked",2)
    candles(ax,bars)
    x=pd.to_datetime(frame.minute+30000,unit='ms',utc=True)
    sub.bar(x,frame.B,width=.7/1440,color=BLUE,label='Buy executed volume')
    sub.bar(x,-frame.A,width=.7/1440,color=ORANGE,label='Sell executed volume (shown below zero)')
    sub.axhline(0,color=GRAY,lw=.6); sub.set_ylabel('Contracts / minute'); sub.legend(loc='upper left',fontsize=8)
    for a in [ax,sub]: clock_axis(a,day,*plan['view'])
    hole(plan,['AAPL_ten_level_events','state_windows_thresholds','provide_cancel_consume_identity'],'Native NQ executed effort and price are plotted only as inputs. AAPL source states, efficiency classifications and transitions remain unavailable.','source_and_data')
    finish(plan,fig,'Signed execution totals preserve B=buy and A=sell; OHLC direction does not assign aggression.\nNo B/A/D/E/W labels, cancellation counts, refill inference, response threshold or transition matrix is generated.',{'executed_volume':int(trades['size'].sum()),'buy_volume':int(totals.B.sum()),'sell_volume':int(totals.A.sum()),'unknown_volume':int(totals.N.sum()),'source_state':None,'native_source_instrument_match':False,'display_bucket_minutes':1,'source_state_bucket_minutes':None},[record_input(plan,'minutes',bars),record_input(plan,'execution-volumes',frame),{'native_trade_window':trades.attrs,'rows':len(trades)}],ident)


def chart_m11(plan):
    path=ROOT/'implementation/reports/phase1-live/macro-backfill/fred-h233aw4x/normalized-p0wb8u84/CPIAUCSL.jsonl'
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    use=[r for r in rows if '2025-01-01'<=r['reference_period']<='2026-01-01' and r['realtime_start']<=plan['date']<=r['realtime_end']]
    assert len({r['reference_period'] for r in use})==len(use)
    assert all(r['realtime_start']<=plan['date'] for r in use)
    frame=pd.DataFrame(use).sort_values('reference_period')
    # Reindex without filling an absent/missing month; gaps remain visible.
    idx=pd.date_range('2025-01-01','2026-01-01',freq='MS')
    vals=pd.Series([float(r['value']) if r['value'] is not None else np.nan for r in use],index=pd.to_datetime([r['reference_period'] for r in use])).reindex(idx)
    fig,(ax,)=setup(plan,f"Civil-date vintage view: {plan['date']} | CPIAUCSL native index | illustrative acquired input, not Stoic's C-score")
    ax.plot(idx,vals,color=BLUE,marker='o',lw=1.5)
    ax.set_ylabel('CPI index, 1982-1984 = 100 (seasonally adjusted)')
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2)); ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlabel('Observation reference month (different from publication/vintage date)')
    ax.text(.04,.90,'Custom C-score: unknown\nMacro cycle: unknown\nTrend strength: unknown\nIntraday availability: unproven',transform=ax.transAxes,va='top',fontsize=11,bbox={'facecolor':'#f8eedb','edgecolor':'none','pad':12})
    hole(plan,['source_series_transforms','custom_C_score_cycle_trend','process_journal','intraday_available_at'],'A native civil-date FRED snapshot can be plotted, but it is not Stoic process validation or a source macro decision. No availability assumption or custom model is introduced.')
    finish(plan,fig,'Reference months and vintage dates stay separate. The absent October 2025 value is not interpolated.\nThis is a civil-date snapshot only: publication evidence does not supply observed feed arrival or a trading decision.',{'as_of_civil_date':plan['date'],'series':'CPIAUCSL','reference_months_requested':13,'nonmissing_values':int(vals.notna().sum()),'missing_reference_months':[str(d.date()) for d in vals.index[vals.isna()]],'source_model_output':None,'intraday_known_at':None},[{'native_vintage_source':source_meta(path)},record_input(plan,'civil-date-vintages',frame)])


def chart_m12(plan):
    fig,(ax,)=setup(plan,'Printed source arithmetic only | fixed original baseline B | no acquired dated process/risk journal')
    stages=['First risk\n(before first result)','Second risk\n(after closed +3B)','Reset risk\n(after closed second +12B)']
    bars=ax.bar(range(3),[1,4,1],color=[BLUE,ORANGE,GREEN],width=.5)
    for bar,value in zip(bars,[1,4,1]): ax.text(bar.get_x()+bar.get_width()/2,value+.07,f'{value}B',ha='center',fontsize=15,weight='bold')
    ax.set_xticks(range(3),stages); ax.set_ylabel('Risk in original baseline units'); ax.set_ylim(0,5.5)
    ax.text(.98,.90,'First win: +3B\nSecond win: +12B\nPrinted two-win total: +15B\nSecond loss from +3B: -1B net',transform=ax.transAxes,ha='right',va='top',fontsize=11,bbox={'facecolor':'#eef2f4','edgecolor':'none','pad':10})
    hole(plan,['dated_process_journal','prior_validation_MC','activation_conflict','other_outcome_transitions'],'No dated underlying trades/risk-stage records are acquired. Only the printed 1/4/1 baseline arithmetic is reconstructable; no source-native dated session can be fabricated.','source_and_process_data')
    finish(plan,fig,'The heading says activation after a two-trade winning streak; the ladder increases risk after the first win.\nThat conflict remains open. This undated arithmetic illustration is not a Monte Carlo run or historical method result.',{'dated_session':None,'printed_risk_units':[1,4,1],'printed_closed_win_units':[3,12],'printed_cumulative_two_win_units':15,'printed_second_loss_net_units':-1,'source_activation':None,'rebase_to_updated_equity':False},[])


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    spec={'version':'method-geometry-2026-09-12','purpose':'Geometry diagnostics excluded from historical method sample','selection_frozen_before_chart_calculation':True,'plans':PLANS}
    spec_path=OUT/'chart-spec.json'
    serialized=json.dumps(spec,sort_keys=True,default=serial)
    if spec_path.exists():
        assert json.dumps(json.loads(spec_path.read_text()),sort_keys=True)==serialized, 'Frozen chart selection changed'
    else: save_json(spec_path,spec)
    # Render source references from immutable PDFs. Only the primary source page
    # is copied to the chart bundle; all supporting pages remain linked by path.
    refs=[]
    for plan in PLANS:
        path,page=plan['references'][0]
        doc=pymupdf.open(ROOT/path); target=OUT/f"{plan['id']}-source-p{page:02}.png"
        doc[page-1].get_pixmap(matrix=pymupdf.Matrix(1.4,1.4)).save(target)
        refs.append({'method':plan['id'],'pdf':source_meta(ROOT/path),'page':page,'render':str(target),'render_sha256':sha256_file(target)})
        for source,_ in plan['references']: source_meta(ROOT/source)
    for plan in PLANS:
        fn={'M01':chart_m01,'M02':chart_m02,'M03':chart_m03,'M04':chart_m04,'M05':chart_m05,'M06':chart_profile,'M07':chart_profile,'M08':chart_m08,'M09':chart_m09,'M10':chart_m10,'M11':chart_m11,'M12':chart_m12}[plan['id']]
        fn(plan)
    # The manifest is reproducibility evidence, never a visual approval.
    import importlib.metadata
    runtime={name:importlib.metadata.version(name) for name in ['matplotlib','pandas','pyarrow','PyMuPDF','numpy']}
    manifest={'version':spec['version'],'runtime':runtime,'chart_spec':source_meta(spec_path),'builder':source_meta(Path(__file__)),'formulas':source_meta(ROOT/'planning/phase-1-live/FORMULAS.md'),'charts':RESULTS,'source_references':refs,'sources':list(SOURCE_META.values()),'historical_candidates_created':0,'visual_review':'Manual review recorded separately in CHART_CHECK.md'}
    save_json(OUT/'measurements.json',manifest)
    (OUT/'holes.jsonl').write_text(''.join(json.dumps(row,sort_keys=True)+'\n' for row in HOLES))
    print(f'{len(RESULTS)} charts; {len(HOLES)} explicit chart holes; zero historical candidates',flush=True)


if __name__=='__main__':
    main()
