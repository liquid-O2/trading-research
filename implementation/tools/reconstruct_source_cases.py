#!/usr/bin/env python3
"""Compare explicit research reconstructions with dated, retained source figures.

This is within-example calibration, not candidate discovery or performance
validation. No source-authored execution timestamp or fill is manufactured.
Run from /workspace with the chart_method_pack.py runtime.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
import pymupdf

import chart_method_pack as chart

ROOT, DATA, ET = chart.ROOT, chart.DATA, chart.ET
OUT = ROOT / 'implementation/reports/phase1-live/methods/reconstructions'
GB = ROOT / chart.GB
MINUTE = 60_000_000_000


def write_json(name, value):
    path = OUT / name
    chart.save_json(path, value)
    return chart.source_meta(path)


def csv(name, frame):
    path = OUT / name
    frame.to_csv(path, index=False)
    return {**chart.source_meta(path), 'rows': len(frame)}


def embedded_figure(page, xref, mask=0):
    with pymupdf.open(GB) as doc:
        assert any(item[0] == xref for item in doc[page-1].get_images())
        pix = pymupdf.Pixmap(doc, xref)
        if mask:
            pix = pymupdf.Pixmap(pix, pymupdf.Pixmap(doc, mask))
        return Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGB')


def finish(fig, name):
    fig.canvas.draw()
    for ax in fig.axes:
        bounds = getattr(ax, '_method_price_bounds', None)
        if bounds:
            lo, hi = ax.get_ylim()
            assert lo <= bounds[0] and hi >= bounds[1], 'Clipped price wicks'
    path = OUT / name
    fig.savefig(path, dpi=160, facecolor='#fcfcfa')
    plt.close(fig)
    return chart.source_meta(path)


def bars_between(day, start, end):
    return chart.read_window(day, start, end)


def clock(ms):
    return chart.dt(int(ms) * 1_000_000).strftime('%H:%M')


def vwap_case():
    day = '2026-02-24'
    start, end = chart.ns('2026-02-23', '18:00'), chart.ns(day, '10:30')
    bars = chart.read_bounds(DATA/'quantpad/cme__nq-continuous-futures__ohlcv-1m/2026.parquet', start, end, 1_000_000, 'bars')
    trades = chart.read_bounds(DATA/'quantpad/cme__nq-continuous-futures__trades/2026-02-23.parquet', start, end, 1, 'trades')
    ident = chart.identity(bars)
    assert int(trades.instrument_id.iloc[0]) == ident['instrument_id']
    figure = embedded_figure(33, 54)
    assert figure.size == (1200, 483)
    # Clock columns come from the source grid, independent of candidate VWAP.
    samples = [('08:30',72),('08:40',135),('08:50',197),('09:00',260),
               ('09:10',322),('09:20',385),('09:35',478),('09:40',510),
               ('09:45',541),('09:50',572),('09:55',604),('10:00',635),
               ('10:05',666),('10:10',697),('10:15',729),('10:20',760),('10:25',791)]
    pixels = np.asarray(figure)
    points, excluded = [], []
    for label, x in samples:
        candidates = []
        for y in range(233,282):
            r,g,b = map(int, pixels[y,x])
            if r>25 and 5<=g-r<=45 and 0<=b-g<=20 and b<190:
                candidates.append((r+g+b,y))
        if not candidates:
            excluded.append({'bar_open_et':label,'x':x,'reason':'curve occluded / no gray-curve pixel in fixed mask'})
            continue
        y = max(candidates)[1]
        points.append({'bar_open_et':label,'x':x,'y':y,
                       'bar_open_ns':chart.ns(day,label), 'known_at_ns':chart.ns(day,label)+MINUTE,
                       'source_price':25000-(y-33)/1.3125})
    points = pd.DataFrame(points)
    # All points were already seen in exploration. None is called held out.
    assert len(points) == 13
    asofs = (bars.t.to_numpy()+60000)*1_000_000
    resets = {'previous-18:00':start, 'midnight-00:00':chart.ns(day,'00:00'),
              'london-02:00':chart.ns(day,'02:00'), 'cash-09:30':chart.ns(day,'09:30')}
    curves, fits = {}, []
    for reset_name, reset in resets.items():
        eligible = bars.t.to_numpy()*1_000_000 >= reset
        volume = bars.v.where(eligible, 0).cumsum()
        for basis in ['HLC3','close','OHLC4','native-trades']:
            if basis == 'native-trades':
                vals = chart.comparison_vwap(trades,reset,asofs,chart.D(ident['q']))
                curve = pd.Series(pd.to_numeric(vals.vwap,errors='coerce').to_numpy(),index=asofs)
            else:
                price = {'HLC3':(bars.h+bars.l+bars.c)/3,
                         'close':bars.c, 'OHLC4':(bars.o+bars.h+bars.l+bars.c)/4}[basis]
                value = (price*bars.v).where(eligible,0).cumsum()/volume.replace(0,np.nan)
                curve = pd.Series(value.to_numpy(),index=asofs)
            curves[(reset_name,basis)] = curve
            prediction = curve.reindex(points.known_at_ns.to_numpy()).to_numpy()
            error = prediction-points.source_price.to_numpy()
            valid = np.isfinite(error)
            fits.append({'reset':reset_name,'basis':basis,'n_points':int(valid.sum()),
                         'total_source_points':len(points),'full_coverage':bool(valid.all()),
                         'rmse_points':float(np.sqrt(np.mean(error[valid]**2))),
                         'mae_points':float(np.mean(np.abs(error[valid]))),
                         'max_abs_error_points':float(np.max(np.abs(error[valid]))),
                         'validation':'within-example fit; no holdout; no performance claim'})
    fits = pd.DataFrame(fits).sort_values(['full_coverage','rmse_points'],ascending=[False,True])
    chosen = curves[('previous-18:00','HLC3')]
    points['reconstructed_hlc3'] = chosen.reindex(points.known_at_ns.to_numpy()).to_numpy()
    points['error_points'] = points.reconstructed_hlc3-points.source_price
    curve_table = pd.DataFrame({'bar_open_ns':asofs-MINUTE,'known_at_ns':asofs})
    for key, curve in curves.items(): curve_table[' / '.join(key)] = curve.to_numpy()

    # Compare explicit session-clock hypotheses. Touch uses the prior completed
    # VWAP, which was observable before the touch minute; bar OHLC is end-known.
    asia = bars[(bars.t>=chart.ns('2026-02-23','20:00')//1_000_000)&(bars.t<chart.ns(day,'00:00')//1_000_000)]
    later = bars[bars.t>=chart.ns(day,'09:30')//1_000_000].copy()
    later['prior_vwap'] = chosen.reindex(later.t.to_numpy()*1_000_000).to_numpy()
    sessions = []
    for lo,hi in [('02:00','05:00'),('03:00','05:00'),('02:00','08:00')]:
        london = bars[(bars.t>=chart.ns(day,lo)//1_000_000)&(bars.t<chart.ns(day,hi)//1_000_000)]
        threshold = max(float(asia.h.max()),float(london.h.max()))
        breaks = later[later.c>threshold]
        assert len(breaks)
        first = breaks.iloc[0]
        touches = later[(later.t>first.t)&(later.l<=later.prior_vwap)&(later.h>=later.prior_vwap)]
        assert len(touches)
        touch = touches.iloc[0]
        sessions.append({'asia_window_et':'previous 20:00–00:00','london_window_et':f'{lo}–{hi}',
                         'asia_high':float(asia.h.max()),'london_high':float(london.h.max()),
                         'first_close_above_both_bar_open_et':clock(first.t),
                         'breakout_known_at_ns':int(first.t+60000)*1_000_000,
                         'first_prior_vwap_touch_bar_open_et':clock(touch.t),
                         'touch_known_at_ns':int(touch.t+60000)*1_000_000,
                         'prior_completed_vwap':float(touch.prior_vwap),
                         'source_clock_settings_verified':False,'entry_fill':None})

    fig = plt.figure(figsize=(15,12),facecolor='#fcfcfa')
    grid = fig.add_gridspec(3,1,height_ratios=[1.05,1.15,.45],left=.07,right=.95,top=.91,bottom=.13,hspace=.28)
    top,ax,err = [fig.add_subplot(grid[i]) for i in range(3)]
    fig.suptitle('GB VWAP · February 24, 2026 · source-fit reconstruction',x=.07,ha='left',fontsize=19,weight='bold')
    top.imshow(figure); top.scatter(points.x,points.y,s=27,facecolors='none',edgecolors='#ffd33d',linewidths=1)
    top.set_xlim(0,1199); top.set_ylim(482,0); top.axis('off')
    top.set_title('Retained source figure, p.33 · yellow rings mark the 13 digitized VWAP points',loc='left',fontsize=10)
    view = bars[bars.t>=chart.ns(day,'08:20')//1_000_000]
    chart.candles(ax,view)
    for key,col,style in [(('previous-18:00','HLC3'),chart.BLUE,'-'),
                          (('previous-18:00','native-trades'),chart.GREEN,':'),
                          (('cash-09:30','HLC3'),chart.ORANGE,'--')]:
        use = curves[key].reindex((view.t.to_numpy()+60000)*1_000_000)
        ax.plot([chart.dt(int(n)-MINUTE) for n in use.index],use.to_numpy(),color=col,ls=style,lw=1.4,label=' / '.join(key))
    ax.scatter([chart.dt(int(n)) for n in points.bar_open_ns],points.source_price,s=23,facecolors='none',edgecolors='black',zorder=5,label='Source pixels')
    chart.clock_axis(ax,day,'08:20','10:30'); ax.legend(fontsize=8,loc='upper left',ncols=2)
    err.axhline(0,color=chart.GRAY,lw=.7)
    err.axhspan(-1/1.3125,1/1.3125,color=chart.GRAY,alpha=.15,label='±1 source pixel (0.76 pt)')
    err.plot([chart.dt(int(n)) for n in points.bar_open_ns],points.error_points,color=chart.BLUE,marker='o',ms=4)
    err.set_ylabel('Fit error (pt)'); chart.clock_axis(err,day,'08:20','10:30'); err.legend(fontsize=8,loc='lower left')
    selected_fit = fits[(fits.reset=='previous-18:00')&(fits.basis=='HLC3')].iloc[0].to_dict()
    fig.text(.07,.065,f"18:00 HLC3: RMSE {selected_fit['rmse_points']:.2f} pt across all 13 points. Price-basis differences are too small to identify the author's basis.\nBar-open display clocks; each computed value is available at bar end (+1 minute). Pixel alignment is approximate (±1 bar).\nThe dated example was used to select a plausible reset. This is neither a held-out check nor a historical trade result.",fontsize=10,va='center',linespacing=1.45)
    return {'case_id':'GB-VWAP-2026-02-24','fidelity':'research_reconstruction','historical_method_N':0,
            'source':{'pdf':chart.source_meta(GB),'page':33,'post_id':'2026329904690712970',
                      'published_at_utc':'2026-02-24T16:14:31Z','image_xref':54,
                      'known_intent':['close above London and Asia highs','retrace to VWAP','long','30-point stop'],
                      'reported_outcome':'Original post says 150 points; reply on p.34 says 100 points. Neither defines a planned target.',
                      'price_basis':None,'session_clock_settings':None,'actual_entry_timestamp':None},
            'native_identity':ident,'adopted_hypothesis':{'reset':'previous day 18:00 America/New_York','basis':'HLC3','bar_minutes':1,
                    'basis_reason':'Sires VWAP lesson p.8 shows HLC3; this is an explicit borrowed platform-style hypothesis, not GB verification.',
                    'price_basis_identified_by_fit':False,'selected_using_this_example':True},
            'selected_fit':selected_fit,'digitization':{'x_axis':'source clock grid','price_anchors':[[33,25000],[243,24840],[453,24680]],
                    'minimum_pixel_uncertainty_points':1/1.3125,'clock_uncertainty_bars':1,
                    'mask':'x columns fixed; y 233..281; r>25, 5<=g-r<=45, 0<=b-g<=20, b<190; brightest valid pixel; excludes horizontal order line',
                    'excluded_columns':excluded},
            'session_clock_hypotheses':sessions,'figure':finish(fig,'GB-VWAP-2026-02-24.png'),
            'artifacts':[csv('vwap-source-points.csv',points),csv('vwap-fit-grid.csv',fits),csv('vwap-curves.csv',curve_table),csv('vwap-source-day-minutes.csv',bars)],
            'raw_inputs':[{'source':bars.attrs['source'],'start_ns':start,'end_ns':end,'rows':len(bars)},
                          {'source':trades.attrs['source'],'start_ns':start,'end_ns':end,'rows':len(trades)}],
            'unresolved':['GB session bounds and exact price basis remain inferred','entry order/fill and target not reconstructed','single-example fit does not establish generalization']}


def fail_case():
    day = '2025-11-20'
    bars = bars_between(day,'09:00','11:02')
    ident = chart.identity(bars)
    two = bars.copy(); two['bucket'] = two.t//120000*120000
    two = two.groupby('bucket',as_index=False).agg(t=('t','min'),o=('o','first'),h=('h','max'),l=('l','min'),c=('c','last'),v=('v','sum'),members=('t','count'))
    assert (two.members == 2).all()
    two['bar_open_et'] = two.t.map(clock)
    two['known_at_ns'] = (two.t+120000)*1_000_000
    two['bearish_gap_low'] = two.h.where(two.h<two.l.shift(2))
    two['bearish_gap_high'] = two.l.shift(2).where(two.h<two.l.shift(2))
    parent = bars[bars.t<chart.ns(day,'10:00')//1_000_000]
    H,L = float(parent.h.max()),float(parent.l.min())
    # The author figure selects the later upper test. This is a retrospective
    # annotation window, not a rule selecting the largest future peak per day.
    attempt = two[(two.t>=chart.ns(day,'10:36')//1_000_000)&(two.t<chart.ns(day,'10:40')//1_000_000)]
    peak = attempt.loc[attempt.h.idxmax()]
    failed = two[(two.t>peak.t)&(two.c<H)].iloc[0]
    # A local low is not known until its right-hand bar closes.
    pivots = two[(two.l<two.l.shift(1))&(two.l<two.l.shift(-1))].copy()
    pivots['pivot_known_at_ns'] = (pivots.t+240000)*1_000_000
    pivots = pivots[(pivots.t>peak.t)&(pivots.pivot_known_at_ns<=chart.ns(day,'10:48'))]
    pivot = pivots.iloc[-1]
    shifts = two[(two.t*1_000_000>=pivot.pivot_known_at_ns)&(two.c<pivot.l)]
    shift = shifts.iloc[0]
    gaps = two[(two.t>=chart.ns(day,'10:48')//1_000_000)&(two.t<=chart.ns(day,'10:52')//1_000_000)&two.bearish_gap_low.notna()].copy()
    assert gaps.bar_open_et.to_list() == ['10:48','10:50','10:52']
    # Chart grid: 25200 at y259 and 25100 at y425. Rectangle edges are
    # approximate readings of the retained MNQ figure (about ±1 pixel).
    source_edges = [(117,143),(157,197),(213,217)]
    comparisons = []
    for row,(y_hi,y_lo) in zip(gaps.itertuples(),source_edges):
        src_hi,src_lo = 25200+(259-y_hi)/1.66,25200+(259-y_lo)/1.66
        after = two[two.t*1_000_000>=row.known_at_ns]
        later_touches = after[(after.h>=row.bearish_gap_low)&(after.l<=row.bearish_gap_high)]
        comparisons.append({'bar_open_et':row.bar_open_et,'known_at_ns':int(row.known_at_ns),
                'nq_gap_low':row.bearish_gap_low,'nq_gap_high':row.bearish_gap_high,
                'source_pixel_top':y_hi,'source_pixel_bottom':y_lo,'mnq_source_low_approx':src_lo,'mnq_source_high_approx':src_hi,
                'low_error_points':row.bearish_gap_low-src_lo,'high_error_points':row.bearish_gap_high-src_hi,
                'later_bar_touches_gap_before_11:02':bool(len(later_touches)),
                'source_order_fill':None})
    first_gap = gaps.iloc[0]
    entry_limit = float((first_gap.bearish_gap_low+first_gap.bearish_gap_high)/2)
    after = two[two.t*1_000_000>=max(int(first_gap.known_at_ns),int(shift.known_at_ns))]
    possible_fills = after[(after.l<=entry_limit)&(after.h>=entry_limit)]
    assert possible_fills.empty
    target_touch = two[(two.t>peak.t)&(two.l<=L)].iloc[0]
    figure = embedded_figure(43,71,72)
    assert figure.size == (1200,535)
    fig = plt.figure(figsize=(15,11),facecolor='#fcfcfa')
    grid = fig.add_gridspec(2,1,height_ratios=[1,1.05],left=.07,right=.95,top=.91,bottom=.17,hspace=.26)
    top,ax = [fig.add_subplot(grid[i]) for i in range(2)]
    fig.suptitle('GB failure · November 20, 2025 · two-minute source reconstruction',x=.07,ha='left',fontsize=19,weight='bold')
    top.imshow(figure); top.axis('off')
    top.set_title('Author figure: MNQZ2025, 2-minute toolbar/header · later upper sweep and three red FVG bands',loc='left',fontsize=10)
    view = bars[bars.t>=chart.ns(day,'09:30')//1_000_000]
    chart.candles(ax,view,2)
    chart.frozen_line(ax,day,'10:00','11:02',H,f'09–10 high {H:.2f}',chart.BLUE)
    chart.frozen_line(ax,day,'10:00','11:02',L,f'09–10 low {L:.2f}',chart.ORANGE)
    ax.axvspan(chart.dt(chart.ns(day,'10:36')),chart.dt(chart.ns(day,'10:40')),color=chart.GRAY,alpha=.15)
    for row in gaps.itertuples():
        ax.fill_between([chart.dt(int(row.known_at_ns)),chart.dt(chart.ns(day,'11:02'))],row.bearish_gap_low,row.bearish_gap_high,color=chart.RED,alpha=.2)
        ax.plot([chart.dt(int(row.known_at_ns))]*2,[row.bearish_gap_low,row.bearish_gap_high],color=chart.RED,lw=1)
    ax.scatter(chart.dt(int(failed.known_at_ns)),failed.c,marker='D',color=chart.BLUE,s=40,label=f'Close back below H known {chart.dt(int(failed.known_at_ns)).strftime("%H:%M")}')
    ax.scatter(chart.dt(int(shift.known_at_ns)),shift.c,marker='v',color=chart.RED,s=55,label=f'MSS comparison known {chart.dt(int(shift.known_at_ns)).strftime("%H:%M")}')
    chart.clock_axis(ax,day,'09:30','11:02'); ax.legend(fontsize=9,loc='lower left')
    fig.text(.07,.09,'NQ reproduces the later sweep, failure and all three FVG bands; MNQ and NQ are distinct native instruments.\nBands begin only when all three candles have closed. The source-selected attempt is a retrospective annotation.\nA limit at the first completed gap midpoint (25278.625) receives no touch by 11:02; the author’s exact entry rule remains unproven.',fontsize=10,va='center',linespacing=1.5)
    return {'case_id':'GB-FAIL-2025-11-20','fidelity':'research_reconstruction','historical_method_N':0,
            'source':{'pdf':chart.source_meta(GB),'text_page':31,'figure_page':43,'post_id':'1991589280142315537',
                      'published_at_utc':'2025-11-20T19:27:40Z','image_xref':71,'image_mask_xref':72,
                      'instrument':'MNQZ2025','bar_minutes':2,'known_intent':['later sweep of 09–10 highs','failed breakout','MSS + FVG entry','opposing 09–10 lows'],
                      'actual_entry_timestamp':None,'reported_points':'>250, reported result; not a prescribed target'},
            'native_identity':ident,'native_instrument_equals_source':False,
            'retrospective_source_annotation':{'upper_test_window_et':['10:36','10:40'],'automatic_candidate_selector':False},
            'geometry':{'nyam_high':H,'nyam_low':L,'nyam_known_at_ns':chart.ns(day,'10:00'),
                        'later_peak':float(peak.h),'peak_bar_open_et':clock(peak.t),'peak_known_at_ns':int(peak.known_at_ns),
                        'failure_bar_open_et':clock(failed.t),'failure_known_at_ns':int(failed.known_at_ns),
                        'comparison_pivot_low':float(pivot.l),'pivot_bar_open_et':clock(pivot.t),'pivot_known_at_ns':int(pivot.pivot_known_at_ns),
                        'mss_known_at_ns':int(shift.known_at_ns),'mss_definition':'first 2-minute close below a 1-left/1-right confirmed local low after the annotated upper test',
                        'fvg_definition':'bearish three-candle wick gap: high[i] < low[i-2]; known at close of i',
                        'opposing_low_touch_bar_open_et':clock(target_touch.t),'opposing_low_touch_known_at_ns':int(target_touch.known_at_ns)},
            'gap_comparisons':comparisons,'source_pixel_uncertainty_points':1/1.66,
            'entry_hypothesis_check':{'kind':'limit at first gap midpoint after completed MSS and gap','limit_price':entry_limit,
                                     'tick_rounded_order_submitted':False,'post_decision_bar_touch_count':len(possible_fills),'window_end_et':'11:02',
                                     'conclusion':'No touch even before tick rounding; cannot explain the source entry with this delayed limit rule.'},
            'figure':finish(fig,'GB-FAIL-2025-11-20.png'),
            'artifacts':[csv('fail-source-day-minutes.csv',bars),csv('fail-two-minute-geometry.csv',two),csv('fail-gap-comparisons.csv',pd.DataFrame(comparisons))],
            'raw_inputs':[{'source':bars.attrs['source'],'rows':len(bars),'start_ns':chart.ns(day,'09:00'),'end_ns':chart.ns(day,'11:02')}],
            'unresolved':['exact MSS/entry order and source fill unknown','NQ price comparison does not substitute MNQ volume or PnL','source last bar is partial at 11:03:14; excluded from full-bar comparison']}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    results = [vwap_case(),fail_case()]
    for result in results:
        write_json(result['case_id']+'.json',result)
    ledger = OUT/'source-case-ledger.jsonl'
    ledger.write_text(''.join(json.dumps({'case_id':r['case_id'],'fidelity':r['fidelity'],'source':r['source'],
                      'historical_method_N':0,'evidence_role':'dated source-fit case, not actual execution journal'},sort_keys=True)+'\n' for r in results))
    import importlib.metadata
    write_json('manifest.json',{'version':'source-fit-v1','scope':'Two dated source examples; macro work deprioritized by user',
               'builder':chart.source_meta(Path(__file__)),'shared_chart_builder':chart.source_meta(Path(chart.__file__)),
               'runtime':{n:importlib.metadata.version(n) for n in ['matplotlib','pandas','pyarrow','PyMuPDF','numpy','Pillow']},
               'fidelity':'research_reconstruction','fit_selection_uses_source_example':True,'held_out_examples':0,
               'faithful_method_candidates_created':0,'actual_execution_records_created':0,
               'cases':[chart.source_meta(OUT/(r['case_id']+'.json')) for r in results],
               'source_case_ledger':chart.source_meta(ledger),'visual_review':'requires separate primary-assistant visual inspection'})
    for result in results:
        print(result['case_id'],result.get('selected_fit',result.get('geometry')),flush=True)


if __name__=='__main__':
    main()
