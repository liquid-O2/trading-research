"""Deterministic predicate diagnostics from the selected completed replay."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime,timezone
from functools import lru_cache
from pathlib import Path
import textwrap
from zoneinfo import ZoneInfo

from .historical_runner import load_registry,selected_root,immutable_json
from .historical_reporting import completed_jobs
from .historical_features import HistoricalFeatures,MINUTE,SECOND
from .native_resolution import file_digest


def _number(value):
    try:return float(value)
    except (TypeError,ValueError):return None


def _time(at):return datetime.fromtimestamp(at/SECOND,timezone.utc).astimezone(ZoneInfo('America/New_York'))


def _short(value,field=''):
    if value is True:return 'true'
    if value is False:return 'false'
    if value is None:return 'unknown'
    if isinstance(value,int) and value>10**16 and ('at' in field or 'key' in field):return _time(value).strftime('%H:%M:%S.%f')[:-3]
    if isinstance(value,(list,dict)):return str(value)[:65]
    return str(value)[:65]


def _candles(ax,bars):
    import matplotlib.dates as md
    if not bars:
        ax.text(.5,.5,'No observed candles in this window',ha='center',va='center',transform=ax.transAxes)
        return
    x=[md.date2num(_time(r['start'])) for r in bars]
    colors=['#167d8d' if r['O'] is not None and r['C'] is not None and r['C']>=r['O'] else '#b44444' for r in bars]
    ax.vlines(x,[float(r['L']) for r in bars],[float(r['H']) for r in bars],colors=colors,linewidth=.8,alpha=.9)
    ax.plot(x,[float(r['C']) if r['C'] is not None else float('nan') for r in bars],color='#263c50',linewidth=.55,alpha=.5)
    ax.xaxis.set_major_formatter(md.DateFormatter('%H:%M',tz=ZoneInfo('America/New_York')))
    lo=min(float(r['L']) for r in bars);hi=max(float(r['H']) for r in bars);pad=max(.5,(hi-lo)*.08)
    ax.set_ylim(lo-pad,hi+pad)
    ax.set_ylabel('NQ price')
    ax.grid(alpha=.15)


@lru_cache(maxsize=2)
def _market(day,reconstruct=False):return HistoricalFeatures(day,records={'strategy_reconstruction':reconstruct})


def choose_examples(jobs):
    groups=defaultdict(list)
    for row,doc,receipt in jobs:groups[row['coverage_id']].append((row,doc,receipt))
    examples=[]
    for key,records in groups.items():
        records.sort(key=lambda r:(0 if r[1]['cohort']=='evaluation' else 1,r[1]['session_date']))
        candidates=defaultdict(list)
        for row,doc,receipt in records:
            for episode in sorted(doc['episodes'],key=lambda e:(e['decision_at'],e['candidate_id'])):
                candidates[episode['research_verdict']].append((row,doc,receipt,episode))
        if candidates:
            for verdict in ('pass','fail','unknown'):
                if candidates.get(verdict):examples.append(candidates[verdict][0])
        else:
            row,doc,receipt=next((r for r in records if r[1]['native_executions']>0),records[0])
            examples.append((row,doc,receipt,None))
    return examples


def render_example(root,row,doc,receipt,episode):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as md
    verdict=(episode.get('strategy_assessment') or {}).get('status',episode['research_verdict']) if episode else 'no_observed_candidate'
    process=row['method_id'] in {'STOIC-DATA','STOIC-RISK'} or row['extra_unit']
    geometry=episode.get('geometry',{}) if episode else {}
    fig=plt.figure(figsize=(16,11),facecolor='white')
    grid=fig.add_gridspec(3,2,height_ratios=[1.05,1.05,1.15],hspace=.42,wspace=.25,
        left=.06,right=.975,top=.88,bottom=.055)
    top,detail,profile,flow=(fig.add_subplot(grid[0,0]),fig.add_subplot(grid[1,0]),
        fig.add_subplot(grid[0,1]),fig.add_subplot(grid[1,1]))
    ledger=fig.add_subplot(grid[2,:]);ledger.axis('off')
    fig.suptitle(row['method_id']+' / '+row['branch']+'\n'+verdict.replace('_',' '),x=.06,y=.975,ha='left',fontsize=17,fontweight='bold')
    display_date=('Market input '+doc['session_date']+'; record '+_time(episode['decision_at']).strftime('%Y-%m-%d %H:%M ET')) if process and episode else doc['session_date']
    fig.text(.06,.912,f"{display_date}  |  {row['observation_unit']}  |  {doc['cohort']} example  |  "+row['source_definition']['citation'],fontsize=10,color='#4b5563')
    if process:
        top.axis('off');detail.axis('off');profile.axis('off');flow.axis('off')
        top.set_title('Actual unit and population',loc='left',fontsize=11)
        text=[f"Observed records: {doc['N_observed']}",f"p/f/u: {doc['p']}/{doc['f']}/{doc['u']}",
            'Source-inspired strategy context; personal account/order audits are outside setup scope.' if doc.get('reconstruction_scope') else 'No account, order, fill or classifier was reconstructed.',row['source_definition']['operation']]
        top.text(0,.95,'\n\n'.join(textwrap.fill(t,65) for t in text),va='top',transform=top.transAxes,fontsize=10)
        limit=[o.get('reason',o.get('required','')) for o in doc['omissions']
            if not doc.get('reconstruction_scope') or o.get('kind')!='original_source_audit_requirement']
        detail.set_title('Scope / evidence' if doc.get('reconstruction_scope') else 'Exact input limits',loc='left',fontsize=11)
        scope_text=('Personal execution audit: outside the requested strategy setup scope.'
            if doc.get('reconstruction_scope')=='personal_execution_out_of_scope' else
            '\n\n'.join(textwrap.fill(t,70) for t in limit[:4]) or 'Collection records available; see checks below.')
        detail.text(0,.95,scope_text,va='top',fontsize=9,transform=detail.transAxes)
        quantities=doc.get('published_arithmetic',geometry.get('macro',{}))
        if not quantities and doc.get('measured_quantities'):quantities=doc['measured_quantities']
        profile.set_title('Published arithmetic / observed macro quantities',loc='left',fontsize=11)
        lines=[]
        if 'initial_publication_observations' in quantities:
            for observation in quantities['initial_publication_observations']:
                current=observation.get('current') or {}
                lines.append(observation['series_id']+': '+str(current.get('value','unknown'))+' ('+str(current.get('reference_period','unknown'))+')')
                lines.append('Prior available comparisons: '+str(len(observation['baseline'])))
            inferred=quantities.get('inferred_context')
            if inferred:
                lines+=['Our macro composite: '+_short(inferred.get('composite')),
                    'Our context state: '+_short(inferred.get('state'))]
            else:lines.append('Custom source cycle/C-score: unknown')
        else:lines=[k+': '+_short(v,k) for k,v in quantities.items()]
        profile.text(0,.95,'\n'.join(lines[:15]) or ('No arithmetic input is required for this collection review.' if row['branch']=='process_review' else 'No supplied arithmetic/account quantities in this unit.'),va='top',fontsize=10,transform=profile.transAxes)
    else:
        market=_market(doc['session_date'],bool(doc.get('reconstruction_scope')))
        daybars=market.bars(market.start if row['branch']=='other_session' else market.at('09:30'),market.end)
        _candles(top,daybars);top.set_title('Event-time session and preselected reference',loc='left',fontsize=11)
        ref=episode.get('reference',{}) if episode else {}
        if not episode and row['method_id']=='GB-FAIL' and row['branch'] in {'prior_day_level','prior_week_level','prior_month_level'}:
            from .historical_price_scanners import _gb_refs
            references=doc.get('reference_selections')
            if references is None:references,_=_gb_refs(market,row['branch'])
            ref=next((r for r in references if r is not None),{})
        at=episode['decision_at'] if episode else market.at('09:30')
        at=at if market.start<=at<=market.end else market.at('09:30')
        duration=3*MINUTE if geometry.get('local_flow') else 20*MINUTE
        begin=max(market.start,(at-duration)//MINUTE*MINUTE)
        end=min(market.end,((at+duration)//MINUTE+1)*MINUTE)
        seconds=1 if geometry.get('local_flow') else 120 if row['branch']=='mss_fvg_refinement' else 60
        _candles(detail,market.bars(begin,end,seconds))
        detail.set_title('Local price detail'+(' (2-minute candles)' if seconds==120 else ''),loc='left',fontsize=11)
        levels={k:_number(ref.get(k)) for k in ('low','high')}
        for name in ('asia','london'):
            if ref.get(name):levels[name+' high']=_number(ref[name].get('high'))
        levels.update({k:_number(geometry.get(k)) for k in ('entry','stop','target')})
        vw=geometry.get('vwap_snapshot') or {}
        if vw:levels['VWAP']=_number(vw.get('price'))
        if geometry.get('selected_band'):
            levels.update({'band low':_number(geometry['selected_band'][0]),'band high':_number(geometry['selected_band'][1])})
        annotation=geometry.get('mss_fvg')
        if annotation:
            a,b,c=annotation['candles'];long=episode['side']=='long'
            levels['MSS structure']=max(float(a['H']),float(b['H'])) if long else min(float(a['L']),float(b['L']))
            detail.axvspan(md.date2num(_time(a['start'])),md.date2num(_time(c['end'])),color='#d8d5eb',alpha=.2)
            if annotation['gap']:
                lo,hi=(float(a['H']),float(c['L'])) if long else (float(c['H']),float(a['L']))
                detail.axhspan(lo,hi,color='#9782bf',alpha=.18,label='Selected wick FVG')
        for stage in episode.get('stages',[]) if episode else []:
            if isinstance(stage.get('details'),dict) and stage['details'].get('tdo') is not None:levels['TDO']=_number(stage['details']['tdo'])
        colors={'stop':'#b44444','target':'#167d8d','entry':'#111827','VWAP':'#8b5eae','TDO':'#9c6500'}
        for ax in (top,detail):
            ylim=ax.get_ylim()
            visible=[];outside=[]
            for name,value in levels.items():
                if value is None:continue
                if ylim[0]<=value<=ylim[1]:
                    ax.axhline(value,color=colors.get(name,'#8d793d'),lw=.85,ls='--',label=name+' '+f'{value:.2f}');visible.append(name)
                else:outside.append(name+' '+f'{value:.2f}')
            if visible:ax.legend(fontsize=7,loc='best',ncol=2,framealpha=.9)
            if outside:ax.text(.01,.99,'Outside this price view: '+', '.join(outside),transform=ax.transAxes,va='top',fontsize=7,color='#6b7280')
            if episode and begin<=episode['decision_at']<=end:
                ax.axvline(md.date2num(_time(episode['decision_at'])),color='#44546a',ls=':',lw=1)
        p=geometry.get('htf_profile') or geometry.get('developing_profile') or geometry.get('prior_profile') or ref.get('hvn_profile')
        inferred_state=geometry.get('inferred_state')
        if inferred_state:
            profile.axis('off');profile.set_title('Reconstructed state criteria',loc='left',fontsize=11)
            criteria=inferred_state['criteria'][row['branch']]
            lines=[key+': '+_short(value) for key,value in criteria.items()]
            lines+=['', 'Current: '+_time(inferred_state['current']['start']).strftime('%H:%M:%S')+'–'+_time(inferred_state['current']['end']).strftime('%H:%M:%S')+' ET',
                'Prior: '+_time(inferred_state['prior']['start']).strftime('%H:%M:%S')+'–'+_time(inferred_state['prior']['end']).strftime('%H:%M:%S')+' ET',
                '', 'Independent state tests using the versioned source-inspired model.']
            profile.text(0,.95,'\n\n'.join(textwrap.fill(t,70) for t in lines),va='top',fontsize=10,transform=profile.transAxes)
        elif p and p.get('rows'):
            data=p['rows'];price=[float(r['price']) for r in data];volume=[float(r.get('total_volume',r.get('volume',0))) for r in data]
            profile.barh(price,volume,height=.22,color='#6e879f',alpha=.8)
            for key in ('poc','val','vah'):
                value=_number(p.get(key))
                if value is not None:profile.axhline(value,lw=1,ls='--',label=key.upper()+' '+f'{value:.2f}')
            profile.set_xlabel('Executed volume');profile.set_ylabel('Reference price')
            profile.legend(fontsize=8);profile.set_title('Identified causal profile snapshot',loc='left',fontsize=11)
        else:
            profile.axis('off');profile.set_title('Reference / ordered stages',loc='left',fontsize=11)
            stages=episode.get('stages',[]) if episode else []
            lines=[s['stage']+': '+_short(s.get('observed'))+' @ '+_short(s.get('at'),'at') for s in stages]
            if annotation:
                lines+=['MSS structural break: '+_short(annotation['structure']),'Wick FVG: '+_short(annotation['gap'])]
                lines+=['C'+str(i+1)+': '+_time(r['start']).strftime('%H:%M')+'–'+_time(r['end']).strftime('%H:%M') for i,r in enumerate(annotation['candles'])]
            if not lines:
                lines=([f"Observed prior low / high: {ref.get('low')} / {ref.get('high')}",
                    'Reference known: '+_time(ref['known_at']).strftime('%Y-%m-%d %H:%M ET'),
                    'Observed extrema only; coverage limits remain separate.',
                    'Main price axes preserve local detail; distant levels are labelled.'] if ref else [])
                lines+=[o.get('reason',o.get('required','')) for o in doc['omissions'][:5]]
            profile.text(0,.95,'\n'.join(textwrap.fill(t,75) for t in lines[:15]) or 'No episode selected from this observed window.',va='top',fontsize=9,transform=profile.transAxes)
        chunks=geometry.get('local_flow',[])
        if chunks:
            x=[md.date2num(_time(r['end'])) for r in chunks]
            width=2/86400
            flow.bar(x,[r['own'] for r in chunks],width=width,color='#167d8d',label='own-side executions')
            flow.bar(x,[-r['opposing'] for r in chunks],width=width,color='#b44444',label='opposing executions')
            flow.xaxis.set_major_formatter(md.DateFormatter('%H:%M:%S',tz=ZoneInfo('America/New_York')))
            flow.set_ylabel('Quantity in fixed local band');flow.legend(fontsize=8)
            snapshots=geometry.get('poc_snapshots',[])
            if snapshots:
                flow.text(.02,.98,'Same candle POC: '+', '.join(_time(t).strftime('%H:%M:%S')+' = '+str(px) for t,px in snapshots),
                    va='top',transform=flow.transAxes,fontsize=8,bbox={'facecolor':'white','alpha':.9,'edgecolor':'none'})
            flow.set_title('Ordered local effort / response windows',loc='left',fontsize=11);flow.grid(alpha=.15)
        elif inferred_state:
            flow.axis('off');flow.set_title('Current and prior market measurements',loc='left',fontsize=11)
            current=inferred_state['current'];prior=inferred_state['prior']
            fields=('buy','sell','volume','first_vwap','last_vwap','response','efficiency','bid_added','ask_added','withdrawal_estimate')
            lines=[key+': '+_short(current.get(key))+'  |  prior '+_short(prior.get(key)) for key in fields]
            flow.text(0,.95,'\n'.join(lines),va='top',fontsize=9,linespacing=1.35,transform=flow.transAxes)
        elif geometry.get('participation'):
            flow.axis('off');flow.set_title('Native participation / response; source label separate',loc='left',fontsize=11)
            part=geometry['participation'];response=geometry.get('response',{})
            lines=[k+': '+_short(v,k) for k,v in part.items() if not isinstance(v,(list,dict))]
            lines+=['source state: '+_short(geometry.get('source_label')),'individual order identity: unknown']
            flow.text(0,.95,'\n'.join(lines[:17]),va='top',fontsize=8.5,transform=flow.transAxes)
        else:
            flow.axis('off');flow.set_title('Outcome remains separate from sequence',loc='left',fontsize=11)
            out=next((r for r in doc['outcomes'] if episode and r['candidate_id']==episode['candidate_id']),None)
            lines=[f'Sequence verdict: {verdict}',f"Post-sequence observation: {out['result'] if out else 'not applicable'}",
                'No profitable-trade or fill label is inferred.',f"Observed n/p/f/u: {doc['n']}/{doc['p']}/{doc['f']}/{doc['u']}",
                f"Full population scope known: {doc['population_complete']}"]
            flow.text(0,.95,'\n\n'.join(lines),va='top',fontsize=10,transform=flow.transAxes)
    values=episode.get('values',{}) if episode else {}
    assessment=episode.get('strategy_assessment') if episode else None
    if assessment:values={key:value for key,value in values.items() if key in episode['selected_fields']}
    ordered=sorted(values.items(),key=lambda item:(0 if item[1] is False else 1 if item[1] is None else 2,item[0]))
    rejected=assessment and assessment['status'] in {'no_setup','condition_absent'}
    ledger.set_title('Consumed strategy inputs; n/a values cannot change the rejection' if rejected else
        'Consumed strategy inputs at decision' if assessment else 'Predicate operands at decision (false and unknown first)',loc='left',fontsize=11,pad=12)
    if ordered:
        columns=3;per=(len(ordered)+columns-1)//columns
        for i,(key,value) in enumerate(ordered):
            col,position=divmod(i,per)
            failed_input=any(key in condition.split() for condition in assessment['failed_conditions']) if assessment else value is False
            color='#b44444' if failed_input else '#956313' if value is None else '#273746'
            shown='n/a' if rejected and value is None else _short(value,key)
            ledger.text(col/columns,.94-position*(.87/max(per,1)),key+': '+shown,va='top',fontsize=7.8,color=color,transform=ledger.transAxes)
    else:
        limits=[] if doc.get('reconstruction_scope') else [r['required'] for r in row['input_limits']]
        ledger.text(0,.95,textwrap.fill('No selected episode. '+(' '.join(limits) if limits else row['source_definition']['operation']),150),va='top',fontsize=10,transform=ledger.transAxes)
    footer=('Reconstructed strategy; all clocks ET. Qualifying setup does not imply a fill or profit. Full precision, source records and model provenance are in the linked job.'
        if doc.get('reconstruction_scope') else 'Frozen research assumptions; actual author trade/fill unknown. Example selection: earliest declared date and candidate for each available verdict. Full precision and provenance remain in the linked job.')
    fig.text(.06,.02,footer,fontsize=8,color='#5f6b76')
    path=root/'charts'/(row['coverage_id'].replace(':','--')+'--'+verdict+'.png')
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,dpi=150,metadata={'Software':'Phase 1 native replay v2'});plt.close(fig)
    return {'coverage_id':row['coverage_id'],'method_id':row['method_id'],'branch':row['branch'],'verdict':verdict,
        'candidate_id':episode['candidate_id'] if episode else None,'cohort':doc['cohort'],'date':doc['session_date'],
        'job':receipt,'path':str(path),'sha256':file_digest(path),'observed_predicate_plot':episode is not None}


def render(run_root):
    root=selected_root(run_root);registry,manifest=load_registry(root)
    jobs=completed_jobs(root,registry,manifest,'evaluation')+completed_jobs(root,registry,manifest,'pilot')
    examples=[]
    for row,doc,receipt,episode in choose_examples(jobs):
        example=render_example(root,row,doc,receipt,episode);examples.append(example)
        print('chart',example['coverage_id'],example['verdict'],flush=True)
    report={'schema':'phase1-predicate-charts-v2','registry_sha256':registry['registry_sha256'],
        'selection':'earliest evaluation then pilot date, earliest candidate per available research verdict; zero-observation inputs shown separately',
        'examples':examples}
    immutable_json(root/'charts/manifest.json',report)
    return report
