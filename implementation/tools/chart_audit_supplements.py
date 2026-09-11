"""Source-dated and native-product supplements for the Phase 1 chart audit."""
from __future__ import annotations

import json
import sys
from datetime import date

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator, EngFormatter
import numpy as np

from chart_audit_plots import OUT, PLOTS, SCORES, draw, serial, window, xhours
from trading_research.research.phase1_live.compute import load_rows
from trading_research.research.phase1_live import family_gex as gx
from trading_research.research.phase1_live import family_options as opt


def source_cases():
    rows=[]
    for rid,iso in [("R-J01","2025-01-28"),("R-J09","2025-10-08"),("R-J11","2026-07-06"),("R-J12","2026-01-02"),("R-G01","2026-08-28"),("R-G02","2026-04-23"),("R-G03","2026-08-27"),("R-G10","2026-08-20"),("R-F15","2026-07-09"),("R-F17","2025-01-10"),("R-S04","2026-07-10")]:
        s=next(r for r in SCORES if r['id']==rid);pos=s['positive_dates'];neg=s['negative_dates']
        label = "comparison-date" if rid == "R-S04" else "source-date"
        selection = ("Retained comparison date only; the K2345 source calendar refers to August 3/4 and its chart prices do not match July 10."
                     if rid == "R-S04" else "source figure calendar date; contract/session caveats retained")
        case={"id":rid,"date":iso,"case":label,"code_result":True if iso in pos else False if iso in neg else None,"selection":selection,"positive_count":len(pos),"negative_count":len(neg)}
        rows.append(draw(case));print(rid,iso,label,flush=True)
    (OUT/'source_date_plot_results.json').write_text(json.dumps(rows,indent=2)+'\n')


def native_options():
    retained={r['date']:r for r in load_rows('options_F')};manifest=[]
    for iso in ('2026-07-10','2026-01-28'):
        r=retained[iso];d=date.fromisoformat(iso)
        for product,_,_,_,symbol,_ in opt.PRODUCTS:
            nodes=r.get(product+'_node_rows') or []
            fig=plt.figure(figsize=(15,8));gs=fig.add_gridspec(2,2,width_ratios=[1.6,1])
            ax=fig.add_subplot(gs[0,0]);az=fig.add_subplot(gs[1,0]);ap=fig.add_subplot(gs[:,1]);index=product in opt.INDEX
            if index:
                cash=opt._cash_ohlc(symbol);days=sorted(k for k in cash if k<=iso)[-15:]
                for i,k in enumerate(days):
                    w=cash[k];c='#187d68' if w['close']>=w['open'] else '#bf443b'
                    for aa in (ax,az):
                        aa.plot([i,i],[w['low'],w['high']],color=c,lw=1)
                        aa.add_patch(Rectangle((i-.2,min(w['open'],w['close'])),.4,max(abs(w['close']-w['open']),.01),color=c))
                for aa in (ax,az):aa.set_xticks(range(len(days)),[k[5:] for k in days],rotation=40,fontsize=7)
                a,b=len(days)-1,len(days)+2
                plo=min(cash[k]['low'] for k in days);phi=max(cash[k]['high'] for k in days)
                ax.set_title(f'{symbol} actual daily cash OHLC; intraday unavailable',fontsize=10)
                note='Current daily candle is an outcome only. No native intraday touch time can be established.'
            else:
                root=opt.QQQ_1M if product=='qqq' else opt.SPY_1M;w=window(d,9.5,16,str(root));xx=xhours(w['t'],d)
                for aa in (ax,az):aa.plot(xx,w['c'],color='#202c3c',lw=.8)
                a,b=9.5,17.1;plo=float(w['c'].min());phi=float(w['c'].max())
                ax.set_title(f'{symbol} actual one-minute spot close',fontsize=10);note='Native ETF coordinates; OI nodes are not gamma or flow-revised orbs.'
            for q in nodes:
                ax.plot([a,b],[q['strike']]*2,ls='--',lw=.8,label=f"K {q['strike']:g}; OI {q['oi']:,}")
                az.plot([a,b],[q['strike']]*2,ls='--',lw=.8)
            if nodes:ax.legend(loc='best',fontsize=7)
            else:ax.text(.03,.95,'No retained eligible OI nodes on this date',transform=ax.transAxes,va='top',fontsize=9)
            ax.grid(alpha=.15);ax.set_ylabel(symbol+' price')
            pad=max((phi-plo)*.12,phi*.0002);az.set_ylim(plo-pad,phi+pad);az.grid(alpha=.15);az.set_ylabel(symbol+' price')
            az.set_title('Price detail: same native data; far strikes clipped only in this panel',fontsize=9)
            if not index:az.set_xlabel('New York decimal hour; one-minute close series',fontsize=8)
            ap.barh([str(q['strike']) for q in nodes],[q['oi'] for q in nodes],color='#285fa8')
            ap.xaxis.set_major_locator(MaxNLocator(5));ap.xaxis.set_major_formatter(EngFormatter())
            ap.set_title('Retained top-OI strikes (rights summed)',fontsize=10);ap.set_xlabel('Open interest');ap.grid(axis='x',alpha=.15)
            if not nodes:
                ap.set_axis_off();ap.text(.5,.5,'No retained eligible strike observations\nMissing nodes are not a measured zero.',ha='center',va='center',transform=ap.transAxes,fontsize=11)
            fig.suptitle(f'R-R01 supplement · {product.upper()} · {iso} · native product only',fontsize=14)
            fig.text(.06,.035,note+'\nSource: options_F; each strike retains its own vintage and product. No NQ conversion.',fontsize=8)
            fig.subplots_adjust(bottom=.17,top=.88,wspace=.3,hspace=.45)
            path=f'plots/R-R01-native-{product}-{iso}.png';fig.savefig(OUT/path,dpi=130);plt.close(fig)
            manifest.append({'product':product,'date':iso,'plot':path,'nodes':nodes,'spot_source':r.get(product+'_spot_source'),'limitation':note})
        # Capture the exact current producer's local strike vector, rather than
        # independently rebuilding its gamma formula in the plotting script.
        captured={}
        def trace(frame,event,arg):
            if frame.f_code is gx._gex_day.__code__ and event=='return':
                captured.update({k:frame.f_locals.get(k) for k in ('gex_by_k','s','n')})
            return trace
        spot=gx._qqq_spot(__import__('chart_audit_plots').bars(str(gx.QQQ_1M)),d)
        sys.settrace(trace)
        try: result=gx._gex_day(d,spot)
        finally:sys.settrace(None)
        by=captured.get('gex_by_k') or {};ks=sorted(by);values=np.array([by[k] for k in ks]);fig,ax=plt.subplots(figsize=(13,5))
        ax.bar(ks,values/1e6,color=np.where(values>=0,'#187d68','#bf443b'),width=.65)
        for label in ('spot','flip','call_wall','put_wall'):
            if result.get(label) is not None:ax.axvline(result[label],label=f'{label}={result[label]:g}',ls='--',lw=1)
        ax.set_xlabel('Native QQQ strike');ax.set_ylabel('Code signed GEX / $1m');ax.legend(fontsize=8);ax.grid(alpha=.15)
        ax.set_title(f'R-R01 · {iso} · exact current _gex_day strike vector (cumulative-strike flip)')
        fig.tight_layout();path=f'plots/R-R01-native-QQQ-gex-vector-{iso}.png';fig.savefig(OUT/path,dpi=140);plt.close(fig)
        manifest.append({'product':'QQQ','date':iso,'plot':path,'fresh_gex':result,'gex_by_k':by,'limitation':'Code flip is not a spot-repricing root; dealer sign is an assumption.'})
        fig,ax=plt.subplots(figsize=(13,5));w=window(d,9.5,16);xx=xhours(w['t'],d)
        ax.plot(xx,w['c'],color='#202c3c',lw=.8);ax.grid(alpha=.15)
        ax.set_xlabel('New York decimal hour; one-minute bar starts');ax.set_ylabel('Retained NQ continuous price')
        ax.set_title(f'R-R01 · NQ options input gap · {iso}')
        ax.text(.02,.96,'NQ option statistics remain unparsed DBN. No strike/OI/GEX nodes are produced.\nContinuous NQ price is diagnostic; expiry-specific option-underlying matching is unavailable.',transform=ax.transAxes,va='top',fontsize=9,bbox=dict(facecolor='white',alpha=.85))
        fig.tight_layout();path=f'plots/R-R01-native-NQOPT-gap-{iso}.png';fig.savefig(OUT/path,dpi=140);plt.close(fig)
        manifest.append({'product':'NQOPT','date':iso,'plot':path,'nodes':[],'limitation':'Unparsed option statistics; no matched-contract option nodes. Continuous NQ price only; no event scored.'})
    (OUT/'native_options_plot_manifest.json').write_text(json.dumps(manifest,indent=2,default=serial)+'\n')


if __name__=='__main__':
    source_cases();native_options()
