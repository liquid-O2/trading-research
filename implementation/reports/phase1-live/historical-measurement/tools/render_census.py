#!/usr/bin/env python3
"""Deterministic native trigger charts and separate observed-price outcome panels."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import textwrap
sys.path.insert(0,'/workspace/implementation/src')
from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.method_pack import historical_charts as charts
from trading_research.research.method_pack.measurement_runner import configure_runtime, measurement_scope
from trading_research.research.method_pack.historical_features import MINUTE, SECOND


def outcome_panel(root,row,doc,episode,measurement,name):
    import matplotlib.pyplot as plt
    import matplotlib.dates as md
    market=charts._market(doc['session_date'],True)
    decision=episode['decision_at'];origin=measurement['origin'];boundary=measurement.get('boundary',{})
    start=max(market.start,decision-20*MINUTE);end=min(market.end,decision+60*MINUTE)
    bars=market.bars(start//MINUTE*MINUTE,end) if end>start else []
    fig=plt.figure(figsize=(15,10),facecolor='white')
    gs=fig.add_gridspec(3,2,height_ratios=[2.6,1.1,1.2],left=.07,right=.97,top=.88,bottom=.08,hspace=.5,wspace=.3)
    ax=fig.add_subplot(gs[0,:]);table=fig.add_subplot(gs[1,:]);detail=fig.add_subplot(gs[2,0]);coverage=fig.add_subplot(gs[2,1])
    for a in (table,detail,coverage):a.axis('off')
    fig.suptitle(row['method_id']+' / '+row['branch']+' — observed prices after qualification',x=.07,y=.975,ha='left',fontsize=15,fontweight='bold')
    fig.text(.07,.92,doc['session_date']+' | NQ instrument '+str(doc['instrument_id'])+' | '+boundary.get('result',measurement['status']).replace('_',' '),fontsize=11,color='#45556b')
    charts._candles(ax,bars)
    ax.axvline(md.date2num(charts._time(decision)),color='#243b53',linestyle='--',linewidth=1.2,label='confirmation / decision')
    for key,color,label in [('price','#45556b','measurement price'),('stop','#b44444','structural invalidation'),('target','#167d8d','preselected objective')]:
        value=origin.get(key) if key=='price' else episode['geometry'].get(key)
        if value is not None:ax.axhline(float(value),color=color,linestyle=':' if key=='price' else '--',linewidth=1.1,label=label)
    if boundary.get('resolved_at_ns'):
        ax.axvline(md.date2num(charts._time(boundary['resolved_at_ns'])),color='#c28324',linewidth=1.3,label='first observed boundary batch')
    if boundary.get('end_ns') is not None and boundary['end_ns']<=end:
        ax.axvline(md.date2num(charts._time(boundary['end_ns'])),color='#847996',linestyle=':',label='boundary measurement expiry')
    for lo,hi in boundary.get('coverage',{}).get('unknown_intervals',[]):
        if lo<end and hi>start:ax.axvspan(md.date2num(charts._time(max(start,lo))),md.date2num(charts._time(min(end,hi))),color='#e9bd68',alpha=.22)
    ax.set_title('Owned native minute extrema; all times America/New_York',loc='left',fontsize=10)
    ax.legend(loc='best',fontsize=8,ncol=3)
    data=[]
    for r in measurement['horizons']:
        def f(k):return '—' if r.get(k) is None else f"{float(r[k]):.2f}"
        data.append([str(r['minutes']),f('favorable_points'),f('adverse_points'),
                     'complete' if r['status']=='complete_observed_horizon' else 'lower bound / incomplete',
                     'yes' if r['horizon_truncated'] else 'no'])
    if data:
        t=table.table(cellText=data,colLabels=['Horizon (min)','Favorable (points)','Adverse (points)','Future coverage','Truncated at session end'],loc='center',cellLoc='center')
        t.auto_set_font_size(False);t.set_fontsize(9);t.scale(1,1.4)
    else:table.text(0,.8,'No subsequent price origin available; no excursion or return is fabricated.',fontsize=11)
    detail.set_title('Price origin and structural outcome',loc='left',fontsize=11)
    lines=[origin['kind'].replace('_',' '),
           'Price-origin delay from decision: '+f"{(origin['at']-decision)/SECOND:.3f}"+' seconds',
           'Objective: '+str(episode['geometry'].get('target','undefined'))+'; invalidation: '+str(episode['geometry'].get('stop','undefined')),
           'Seconds to observed boundary: '+str(boundary.get('seconds_to_resolution','unresolved')),
           'Expiry: '+boundary.get('expiry_kind','not applicable').replace('_',' ')]
    detail.text(0,.92,'\n\n'.join(textwrap.fill(x,72) for x in lines),va='top',fontsize=9)
    coverage.set_title('Coverage and interpretation',loc='left',fontsize=11)
    lines=[doc['session_accounting']['status'].replace('_',' '),
           'Timestamp ties do not establish objective / invalidation order. Earlier gaps prevent claiming the population-first boundary.',
           'Favorable and adverse excursions are observed price distances. This is not a fill, a simulated return or an actual trade.']
    coverage.text(0,.92,'\n\n'.join(textwrap.fill(x,73) for x in lines),va='top',fontsize=9)
    fig.text(.07,.025,'Selection fixed by branch/outcome category, then earliest session, decision and candidate ID. Native operands and source assumptions are on the paired trigger chart.',fontsize=8,color='#536375')
    path=root/'charts'/name;fig.savefig(path,dpi=140);plt.close(fig)
    return {'path':str(path),'sha256':hr.file_digest(path),'kind':'descriptive_price_outcomes',
            'candidate_id':episode['candidate_id'],'coverage_id':row['coverage_id'],'date':doc['session_date']}


def main(root,only_method=None):
    configure_runtime();root=Path(root).resolve();registry,manifest=hr.load_registry(root)
    if (root/'protocol/CALENDAR_RECOVERY_COMPOSITION.json').exists():
        script=Path(__file__).with_name('recover_calendars.py')
        spec=importlib.util.spec_from_file_location('calendar_recovery_render',script);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        charts.HistoricalFeatures=mod.RecoveredFeatures
    selection=hr.read(root/'charts/SELECTION.json');rows={r['coverage_id']:r for r in manifest['branches']}
    previous=hr.read(root/'charts/manifest.json') if only_method else None
    output=[]
    for i,item in enumerate(sorted(selection['charts'],key=lambda r:r['order'])):
        row=rows[item['coverage_id']]
        if only_method and row['method_id']!=only_method:continue
        doc=hr.read_job(item['job']['path'])
        episode=next((e for e in doc['episodes'] if e['candidate_id']==item['candidate_id']),None)
        # The old renderer's population field describes the broader source
        # audit. Display the census accounting here, while keeping the original
        # immutable job and its original population flag in the manifest.
        display_doc=dict(doc)
        if 'session_accounting' in doc:
            display_doc['population_complete']=doc['session_accounting']['status']=='completed_search'
        display_episode=episode
        if episode and measurement_scope(row['method_id'],row['branch'])=='supplemental_observation':
            display_episode=dict(episode,strategy_assessment={**episode.get('strategy_assessment',{}),
                'status':'supplemental_observation'})
        original_short=charts._short
        def display_short(value,field=''):
            # Display only; immutable job operands retain full precision.
            from decimal import Decimal, InvalidOperation
            if isinstance(value,(str,float)) and len(str(value))>12:
                try:
                    number=Decimal(str(value))
                    if number.is_finite():return format(number,'.6g')
                except InvalidOperation:pass
            return original_short(value,field)
        if row['method_id']=='JETBUNDLE-STATES':charts._short=display_short
        try:result=charts.render_example(root,row,display_doc,item['job'],display_episode)
        finally:charts._short=original_short
        result['population_display']={'original_source_audit_complete':doc['population_complete'],
            'displayed_complete_observed_input_scope':display_doc['population_complete'],
            'basis':'census session accounting; source job unchanged'}
        slug=item['coverage_id'].replace(':','--')+'--'+item['outcome']+'--'+hashlib.sha256(str(item['candidate_id']).encode()).hexdigest()[:8]
        destination=root/'charts'/(slug+'--trigger.png');Path(result['path']).replace(destination)
        result.update(path=str(destination),kind='native_trigger_context',selection=item)
        output.append(result)
        measurement=next((m for m in doc['setup_measurements'] if m['candidate_id']==item['candidate_id']),None)
        if episode and measurement:
            output.append(outcome_panel(root,row,doc,episode,measurement,slug+'--outcomes.png'))
        print(json.dumps({'rendered':i+1,'selected':len(selection['charts']),'branch':item['coverage_id']}),flush=True)
    if previous:
        replacements={r['path']:r for r in output}
        assert set(replacements)<=set(r['path'] for r in previous['charts'])
        output=[replacements.get(r['path'],r) for r in previous['charts']]
        for r in output:assert hr.file_digest(r['path'])==r['sha256']
    body={'numeric_display':'JET state decimals longer than 12 characters shown to six significant digits; immutable jobs retain full precision','schema':'phase1-full-census-chart-manifest-v1','registry_sha256':registry['registry_sha256'],
          'selection_sha256':hr.file_digest(root/'charts/SELECTION.json'),'charts':output,'visual_review':'see VISUAL_QA.json for the completed manual inspection receipt'}
    (root/'charts/manifest.json').write_text(json.dumps(body,indent=2)+'\n')
    text='# Full historical measurement charts\n\nDeterministic earliest example in each branch/outcome category, plus zero-candidate and limitation examples. Each qualifying example has a native trigger/context chart and a separate subsequent-price panel.\n\n'
    text+='Full native bars retain timestamp ambiguity. Amber future shading marks unknown coverage. No observed price outcome implies a fill or return.\n\n'
    text+='JET state decimals longer than 12 characters are displayed to six significant digits. Full precision remains in the immutable native jobs.\n\n'
    for r in output:text+=f"- [{r['coverage_id']} — {r['date']} — {r['kind']}]({r['path']})\n"
    (root/'charts/README.md').write_text(text)
    print('charts',len(output))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-root',required=True);p.add_argument('--only-method');args=p.parse_args();main(args.run_root,args.only_method)
