"""Jumbo and Green Bird historical sequences over admitted event candles."""
from __future__ import annotations
from decimal import Decimal as D
from .historical_features import Q, MINUTE, SECOND, sign, first_contact, distinct_contacts, pivots
from .historical_assembly import HistoricalEpisode, absent, window_result
from .branch_coverage import setting
from .historical_flow import exact_contact, batches


def _known(ref):
    return True if ref is not None and ref['complete'] and ref['coverage']['observed_scope_complete'] else None


def _context(m):
    overnight=m.range(m.start,m.at('09:30'),'overnight')
    pre=m.range(m.at('06:00'),m.at('09:00'),'tbr-main')
    prior=m.prior('day')
    old=prior['range']
    width=None if old is None or not prior.get('range_scope_complete',prior['scope_complete']) else old['high']-old['low']
    direction=None if overnight is None or overnight['open'] is None or pre is None or pre['close'] is None else (
        'long' if pre['close']>overnight['open'] else 'short' if pre['close']<overnight['open'] else None)
    return {'overnight':overnight,'pre':pre,'prior':prior,'prior_width':width,'direction':direction}


def _ob(m,touch,side,end):
    sec=setting('tbr_sessions')['confirmation_seconds'];duration=sec*SECOND
    rows=m.bars(max(m.start,touch['start']//duration*duration-duration),end,sec)
    ambiguous=False
    for a,b,c in zip(rows,rows[1:],rows[2:]):
        if b['start']>touch['start'] or b['end']<touch['end']:continue
        if a['end']!=b['start'] or b['end']!=c['start']:continue
        if not all(r['observed_complete'] for r in (a,b,c)) or c['C'] is None:
            ambiguous=True
            continue
        stop=(b['L']-Q) if side=='long' else b['H']+Q
        inp={k:{**row,'candle_id':row['bar_id']} for k,row in zip(('c1','c2','c3'),(a,b,c))}
        result=m.domain('O056',{**inp,'sweep_side':'low' if side=='long' else 'high',
            'selected_entry_mode':'immediate','selected_stop':stop,'timeframe':sec})
        return result.get('confirmed'),c,stop,result
    return (None if ambiguous else absent(m,touch['start'],end)),None,None,None


def scan_jumbo(m,branch):
    method='JJ-TBR';episodes=[];omissions=[]
    context=_context(m);main=context['pre'];prior=context['prior'];pw=context['prior_width']
    formations=[(m.at('06:00'),m.at('09:00'),'main',m.at('09:30'),m.at('10:00'))]
    if branch=='other_session':
        formations=[]
        for lo,hi in setting('tbr_sessions')['other']:
            offset=-1 if lo>='18:00' else 0
            start,end=m.at(lo,offset),m.at(hi,offset)
            formations.append((start,end,'other-'+lo,end,min(m.end,end+setting('tbr_sessions')['other_action_minutes']*MINUTE)))
    zones=m.supplied('pzone',m.end) if branch=='timed_pzone_reversal' else []
    if branch=='timed_pzone_reversal' and getattr(m,'reconstruct',False):
        from .strategy_pzones import inferred_pzones
        zones=zones or inferred_pzones(m)
    if branch=='timed_pzone_reversal':
        formations=[]
        for zone in zones:
            formations.append((zone['formation_start'],zone['known_at'],zone['id'],zone['known_at'],min(m.end,zone['expires_at'])))
        if not formations:omissions.append({'kind':'external_operand','reason':'no dated P-zone bands/destinations','operand':'source_zone_known'})
    for start,end,label,action_start,action_end in formations:
        ref=m.range(start,end,label)
        zone=next((z for z in zones if z['id']==label),None) if branch=='timed_pzone_reversal' else None
        if zone:ref={**zone,'low':D(str(zone['low'])),'high':D(str(zone['high'])),'start':start,'end':end,'complete':True,'coverage':{'observed_scope_complete':True}}
        if ref is None:
            omissions.append({'reason':'formation_has_no_observed_executions','window':[start,end]});continue
        width=ref['high']-ref['low']
        if width<=0:
            omissions.append({'reason':'nonpositive_formation_width','reference_id':ref['id']});continue
        if branch=='judas_reversal':action_start,action_end=m.at('09:40'),m.at('09:50')
        if branch in {'internal_rotation','extension_reaction','single_extended','single_purged'}:action_end=m.at('16:00')
        if action_end<=action_start:continue
        rows=m.bars(action_start,action_end)
        sides=(zone['side'],) if zone and zone.get('inferred_zone') else ('long','short')
        if branch in {'single_extended','single_purged','judas_outbound'} and context['direction']:
            sides=(context['direction'],)
        for side in sides:
            sg=sign(side);edge=ref['low'] if side=='long' else ref['high']
            target=ref['high'] if side=='long' else ref['low']
            location=[ref['low'],ref['high']] if zone else [edge,edge]
            if branch in {'single_extended','single_purged','internal_rotation'}:
                location=[(ref['low']+ref['high'])/2]*2
            elif branch=='extension_reaction':
                location=[ref['low']-D('.66')*width,ref['low']-D('.33')*width] if side=='long' else [ref['high']+D('.33')*width,ref['high']+D('.66')*width]
            if branch=='judas_outbound':
                trigger=next(iter(rows),None)
                target=ref['high']+width*D('.5') if side=='long' else ref['low']-width*D('.5')
            elif branch in {'judas_reversal','other_session'}:
                trigger=next((r for r in rows if r['L']<edge if side=='long'),None) if side=='long' else next((r for r in rows if r['H']>edge),None)
            else:trigger=first_contact(rows,*location)
            if trigger is None:continue
            strict=('below' if side=='long' else 'above') if branch in {'judas_reversal','other_session'} else None
            contact=exact_contact(m,trigger,*location,strict=strict) if branch!='judas_outbound' else None
            if branch!='judas_outbound' and contact is None:continue
            touch=contact['at'] if contact else trigger['start'];deadline=min(action_end,trigger['end']+30*MINUTE)
            if zone:target=D(str(zone['destination_price']))
            if branch=='judas_outbound':
                openbars=m.bars(m.at('09:30'),m.at('09:30')+SECOND,1)
                confirm=next(iter(openbars),None)
                opening=batches(m.local(m.at('09:30'),m.at('09:30')+SECOND))
                first=opening[0] if opening else None
                prices={r['price'] for r in first[1]} if first else set()
                ok=True if len(prices)==1 else None
                decision=max(r['known_at'] for r in first[1]) if first else trigger['end']
                touch=first[0] if first else trigger['start']
                confirm={'C':next(iter(prices)) if len(prices)==1 else None,'known_at':decision} if first else None
                if getattr(m,'reconstruct',False) and ok is None and first and openbars and openbars[0]['O'] is not None:
                    # Published one-second open is admitted only when its H/L/V
                    # reconciles to the exact native second; wait for that bar.
                    ok=True;decision=openbars[0]['known_at']
                    confirm={'C':openbars[0]['O'],'known_at':decision,
                        'endpoint_evidence':openbars[0].get('endpoint_evidence')}
                stop=ref['low']-Q if side=='long' else ref['high']+Q
            else:
                ok,confirm,stop,ob=_ob(m,trigger,side,deadline)
                decision=confirm['known_at'] if confirm else deadline
            entry=confirm['C'] if confirm else None
            episode_trigger=trigger
            if branch=='judas_outbound' and first:
                episode_trigger={'id':f'opening-batch:{m.instrument_id}:{first[0]}','at':first[0],
                    'known_at':decision,'prices':sorted(prices),'event_ids':[r['event_id'] for r in first[1]]}
            e=HistoricalEpisode(m,method,branch,side,episode_trigger,ref)
            # Context is calculated only from pre-touch observations. The full
            # overnight range ends at 09:30, so other-session contexts use their
            # own completed formation and cannot borrow this future snapshot.
            preopen=context['overnight'] if context['overnight'] and context['overnight']['known_at']<=touch else None
            observedwidth=None if preopen is None else preopen['high']-preopen['low']
            extended=None if pw is None or observedwidth is None else observedwidth>=pw
            compressed=None if pw is None else width<=pw*D(setting('context')['compression_ratio'])
            rotation=None if pw is None else width>=pw*D(setting('context')['wide_ratio'])
            contextat=end if branch=='other_session' or zone else m.at('09:30')
            direction_ok=context['direction']==side if context['direction'] else None
            if branch=='other_session':direction_ok=ref['close'] is not None and ref['open'] is not None
            e.bind({'range_frozen':_known(ref),'range_known_at':ref['known_at'],
                'context_fixed':direction_ok if branch=='judas_outbound' else True if branch=='other_session' else None if pw is None else True,
                'context_at':contextat,'location_touched':True,'touch_at':touch,'source_confirmation':ok,
                'confirm_at':confirm['known_at'] if confirm else None,'risk_defined':None if entry is None or stop is None else sg*(entry-stop)>0,
                'objective_fixed':None if entry is None else sg*(target-entry)>0},
                operation='frozen completed range, pre-touch context and exact selected O056 full-C2 signature',
                parents=[ref['id'],trigger['bar_id']],known_at=decision,assumption='A2-CONTEXT/A2-TBR-CLOCK/A2-STRUCTURAL-RISK')
            if branch=='judas_outbound':
                e.bind({'directional_context':direction_ok,'at_rth_open':first is not None and m.at('09:30')<=first[0]<m.at('09:30')+SECOND,
                    'objective_is_selected_exhaustion':target==(ref['high']+width*D('.5') if side=='long' else ref['low']-width*D('.5')),
                    'exit_window_recorded':True},operation='opening execution policy with selected 0.5W exhaustion and 09:40 exit horizon',assumption='A2-TBR-PROJ/A2-TBR-CLOCK')
            elif branch=='judas_reversal':
                e.bind({'reversal_context':None if pw is None else width>0,'edge_swept':trigger['L']<edge if side=='long' else trigger['H']>edge,
                    'sweep_at':touch,'source_time_window':m.at('09:40')<=touch<m.at('09:50'),
                    'objective_is_opposing_draw':target==(ref['high'] if side=='long' else ref['low'])},
                    operation='strict frozen edge sweep in reversal window and opposing edge identity',assumption='A2-CONTEXT')
            elif branch=='single_extended':
                e.bind({'extended_context':extended,'entry_at_eq_or_quadrant':trigger['L']<=location[0]<=trigger['H'],
                    'objective_is_range_edge':target in (ref['low'],ref['high']),'reduced_expectations':True},
                    operation='overnight width vs prior RTH and range EQ contact; edge target policy',assumption='A2-CONTEXT/A2-TBR-PROJ')
            elif branch=='single_purged':
                old=prior['range'];purges=[]
                if old:
                    for r in m.bars(max(m.start,old['known_at']),min(touch,m.at('09:30'))):
                        if r['H']>old['high'] or r['L']<old['low']:purges.append(r)
                purgeat=purges[0]['known_at'] if purges else None
                e.bind({'purged_compressed_context':None if compressed is None or not prior.get('range_scope_complete',prior['scope_complete']) else compressed and bool(purges),
                    'purge_known_at':purgeat,'entry_at_eq_or_quadrant':trigger['L']<=location[0]<=trigger['H'],
                    'expansion_policy':True},operation='chronological prior-session liquidity sweep before compressed EQ contact',parents=[old['id']] if old else [],assumption='A2-CONTEXT')
            elif branch=='internal_rotation':
                e.bind({'rotation_context':rotation,'entry_at_named_internal_or_ev_band':trigger['L']<=location[0]<=trigger['H'],
                    'objective_is_named_rotation_target':target in (ref['low'],ref['high'])},operation='wide completed range and named EQ/edge rotation',assumption='A2-CONTEXT')
            elif branch=='extension_reaction':
                before=m.bars(end,touch) if touch>end else []
                expansion=any(r['L']<ref['low'] if side=='long' else r['H']>ref['high'] for r in before)
                target_unused=not any(r['L']<=target<=r['H'] for r in before)
                e.bind({'prior_expansion':expansion or absent(m,end,touch) if touch>end else False,
                    'touch_in_source_extension_area':trigger['L']<=location[1] and trigger['H']>=location[0],
                    'reaction_side_confirmed':ok,'objective_is_remaining_draw':target_unused},
                    operation='elapsed parent expansion, exact 1.33–1.66 band, unconsumed opposing edge',assumption='A2-TBR-PROJ')
            elif branch=='other_session':
                e.bind({'source_clock_verified':True,'source_case_verified':True},kind='policy',operation='enumerated TBR p.7 formation identity; research action/confirmation policy',assumption='A2-TBR-CLOCK')
            elif branch=='timed_pzone_reversal':
                destination=D(str(zone['destination_price']));target=destination
                e.bind({'source_zone_known':True,'zone_known_at':zone['known_at'],'source_time_window':zone['known_at']<=touch<zone['expires_at'],
                    'directed_path_recorded':bool(zone.get('destination_id'))},operation='frozen P-zone and directed anchor destination; inferred model identified in reference',parents=[zone['id']],kind='inferred_model' if zone.get('inferred_zone') else 'record',known_at=zone['known_at'])
            e.stage('contact',touch,observed=True,parents=[ref['id']]).stage('opening_context_confirmation' if branch=='judas_outbound' else 'selected_full_C2_confirmation',None if confirm is None else confirm['known_at'],observed=ok)
            if getattr(m,'reconstruct',False) and confirm:
                e.geometry['confirmation_bar']=confirm
            episodes.append(e.finish(decision_at=decision,entry=entry,stop=stop,target=target))
    if prior['omissions']:omissions.extend(prior['omissions'])
    return window_result(m,method,branch,episodes,omissions=omissions)


def _gb_refs(m,branch):
    if branch=='nyam_box':return [m.range(m.at('09:00'),m.at('10:00'),'nyam-box')],[]
    if branch=='previous_hour':return [m.range(m.at(f'{hour:02}:00'),m.at(f'{hour+1:02}:00'),f'hour-{hour}') for hour in range(8,15)],[]
    if branch=='asia_tdo_case':return [m.range(m.at('20:00',-1),m.at('00:00'),'asia')],[]
    if branch=='cash_open_reclaim_case':
        rows=m.bars(m.at('09:30'),m.at('09:30')+MINUTE)
        if not rows or rows[0]['O'] is None:return [],[{'reason':'cash_open_order_unknown'}]
        row=rows[0]
        return [{'id':row['bar_id']+':cash-open','low':row['O'],'high':row['O'],'known_at':row['known_at'],
            'start':row['start'],'end':row['end'],'complete':row['complete'],'coverage':m.coverage(row['start'],row['end'])}],[]
    prior=m.prior(branch.removeprefix('prior_').removesuffix('_level'))
    return [prior['range']],prior['omissions']


def scan_green_failure(m,branch):
    method='GB-FAIL';episodes=[]
    if branch=='mss_fvg_refinement':return scan_green_refinement(m,branch)
    refs,omissions=_gb_refs(m,branch)
    for ref in refs:
        if ref is None:continue
        begin=max(m.at('09:30'),ref['known_at']);end=m.end
        if begin>=end:continue
        if branch=='previous_hour':end=min(end,ref['known_at']+60*MINUTE)
        rows=m.bars(begin,end)
        for side in (('long',) if branch=='cash_open_reclaim_case' else ('short','long')):
            boundary=ref['high'] if side=='short' else ref['low'];sg=sign(side)
            trigger=next((r for r in rows if (r['H']>boundary if side=='short' else r['L']<boundary)),None)
            if trigger is None:continue
            contact=exact_contact(m,trigger,boundary,boundary,strict='above' if side=='short' else 'below')
            if contact is None:continue
            confirmation_end=(trigger['start']//(5*MINUTE)+1)*5*MINUTE
            confirms=m.bars(confirmation_end-5*MINUTE,confirmation_end,300)
            confirm=confirms[0] if confirms else None
            usable=confirm is not None and confirm['observed_complete'] and confirm['C'] is not None
            decision=confirmation_end;close=confirm['C'] if usable else None
            path=m.bars(trigger['start'],confirmation_end)
            high=max(r['H'] for r in path);low=min(r['L'] for r in path)
            stop=high+Q if side=='short' else low-Q
            target=ref['low'] if side=='short' else ref['high']
            if branch=='cash_open_reclaim_case':target=boundary+(boundary-low)*D('.5')
            pre=m.range(m.at('06:00'),min(begin,m.at('09:30')),'gb-precontext')
            context_known=pre is not None and pre['known_at']<=trigger['start']
            e=HistoricalEpisode(m,method,branch,side,trigger,ref)
            tdo_required=branch=='asia_tdo_case'
            tdo_rows=m.bars(m.at('00:00'),m.at('00:00')+MINUTE)
            tdo=tdo_rows[0]['O'] if tdo_rows else None
            inside=None if close is None else (ref['low']<close<ref['high'] if ref['low']!=ref['high'] else True)
            e.bind({'reference_frozen':_known(ref),'reference_known_at':ref['known_at'],'reference_px':boundary,
                'bias_recorded':context_known,'context_at':pre['known_at'] if pre else None,
                'source_session_allowed':True,'sweep_at':contact['at'],'sweep_high':high,'sweep_low':low,
                'confirmation_mode':'five_minute_close','complete_clock_five_minute_bar':True if usable else None,
                'confirm_at':confirmation_end if confirm else None,'confirm_close':close,'box_return_ok':inside,
                'tdo_required':tdo_required,'source_tdo_close_confirmed':None if tdo is None or close is None else sg*(close-tdo)>0,
                'pocket_required':False,'retracement_entry':False,'risk_defined':None if close is None else sg*(close-stop)>0,
                'objective_fixed':None if close is None else sg*(target-close)>0},
                operation='identified finished reference and first strict sweep; next aligned five-minute reclaim with branch-specific TDO',
                parents=[ref['id'],trigger['bar_id']],known_at=decision,assumption='A2-GB-CLOCK/A2-CONTEXT/A2-STRUCTURAL-RISK')
            e.stage('reference',ref['known_at'],observed=_known(ref)).stage('sweep',contact['at'],observed=True,parents=contact['event_ids'])
            e.stage('five_minute_reclaim',confirmation_end,observed=None if close is None else sg*(close-boundary)>0,
                parents=[confirm['bar_id']] if confirm else [],details={'tdo':tdo,'tdo_required':tdo_required})
            if getattr(m,'reconstruct',False):e.geometry['confirmation_bar']=confirm
            episodes.append(e.finish(decision_at=decision,entry=close,stop=stop,target=target))
    result=window_result(m,method,branch,episodes,omissions=omissions)
    if getattr(m,'reconstruct',False):result['reference_selections']=[r for r in refs if r is not None]
    return result


def scan_green_refinement(m,branch):
    parent=scan_green_failure(m,'nyam_box');episodes=[]
    for episode in parent['episodes']:
        if episode['research_verdict']!='pass':continue
        start=episode['decision_at'];end=min(m.end,start+setting('mss_fvg')['horizon_minutes']*MINUTE)
        candles=m.bars((start//(2*MINUTE)+1)*2*MINUTE,end,120)
        triple=next(((a,b,c) for a,b,c in zip(candles,candles[1:],candles[2:]) if a['end']==b['start'] and b['end']==c['start']),None)
        if not triple:continue
        a,b,c=triple;side=episode['side'];sg=sign(side)
        gap=(c['L']>a['H']) if side=='long' else (c['H']<a['L'])
        structure=None if c['C'] is None else c['C']>max(a['H'],b['H']) if side=='long' else c['C']<min(a['L'],b['L'])
        e=HistoricalEpisode(m,'GB-FAIL',branch,side,c,{**episode['reference'],'parent_attempt_id':episode['candidate_id']})
        e.bind({k:v for k,v in episode['values'].items() if k not in {'branch','decision_at'}},operation='completed causal parent reclaim; later annotation retains parent sequence',parents=[episode['candidate_id']],known_at=start,assumption='A2-MSS-FVG')
        # Refinement is an additional conjunction, represented in the existing
        # retracement/hold path rather than modifying the parent entry time.
        e.bind({'retracement_entry':True,'retest_at':c['known_at'],'source_hold_confirmed':gap and structure,
            'confirmation_mode':'reclaim_and_hold'},operation='three distinct aligned two-minute candles: actual wick gap AND break of earlier structure',
            parents=[r['bar_id'] for r in triple],known_at=c['known_at'],assumption='A2-MSS-FVG')
        e.geometry['mss_fvg']={'candles':[a,b,c],'gap':gap,'structure':structure,'parent_entry_at':start}
        e.stage('parent_entry',start,observed=True,parents=[episode['candidate_id']])
        e.stage('later_MSS_FVG_annotation',c['known_at'],observed=gap and structure,parents=[r['bar_id'] for r in triple])
        out=e.finish(decision_at=c['known_at'],entry=None,stop=None,target=None)
        out['parent_entry_at']=start;out['observation_unit']='post_parent_annotation';episodes.append(out)
    return window_result(m,'GB-FAIL',branch,episodes,omissions=parent['omissions'])


def scan_green_vwap(m,branch):
    refs={name:m.range(m.at(lo,-1 if lo>='18:00' else 0),m.at(hi),name) for name,(lo,hi) in
          ((name,setting('gb_sessions')[name]) for name in ('asia','london'))}
    if any(r is None for r in refs.values()):return window_result(m,'GB-VWAP',branch,[],omissions=[{'reason':'session_reference_missing'}])
    asia,london=refs['asia'],refs['london'];begin=max(m.at('09:30'),asia['known_at'],london['known_at'])
    rows=m.bars(begin,m.end,300);boundary=max(asia['high'],london['high'])
    breakout=next((r for r in rows if r['observed_complete'] and r['C'] is not None and r['C']>boundary),None)
    ambiguous=[r['bar_id'] for r in rows if (breakout is None or r['start']<breakout['start']) and r['C'] is None and r['H']>boundary]
    omissions=[{'kind':'input_ambiguity','reason':'earlier potential breakout close is unknown','required_fields':['C'],'candle_ids':ambiguous}] if ambiguous else []
    if breakout is None:return window_result(m,'GB-VWAP',branch,[],omissions=omissions)
    retest=None;vw=None
    for row in m.bars(breakout['end'],m.end):
        snapshot=m.vwap(row['start'])
        if snapshot['price'] is not None and row['L']<=snapshot['price']<=row['H']:
            retest=row;vw=snapshot;break
    deadline=min(m.end,breakout['end']+60*MINUTE)
    # The source defines a later return; one-hour limit is the declared
    # observation horizon, not a claim that the author's attempt expires then.
    if retest is not None and retest['known_at']>deadline:retest=None;vw=None
    decision=retest['known_at'] if retest else deadline
    e=HistoricalEpisode(m,'GB-VWAP',branch,'long',breakout,{'id':asia['id']+'+'+london['id'],'asia':asia,'london':london})
    stop=retest['L']-Q if retest else None;entry=retest['C'] if retest else None
    contact=exact_contact(m,retest,retest['L'],vw['price']) if retest else None
    retest_at=contact['at'] if contact else None
    e.geometry['vwap_snapshot']=vw
    e.bind({'reference_frozen':_known(asia) and _known(london),'london_high':london['high'],'london_known_at':london['known_at'],
        'asia_high':asia['high'],'asia_known_at':asia['known_at'],'continuation_context':breakout['C']>max(asia['high'],london['high']),
        'breakout_at':breakout['known_at'],'breakout_close':breakout['C'],'vwap_reset_verified':True,
        'vwap_known_at':vw['known_at'] if vw else None,'vwap_at_retest':vw['price'] if vw else None,
        'retest_at':retest_at,'retest_low':retest['L'] if retest else None,'retest_high':retest['H'] if retest else None,
        'risk_defined':None if entry is None else entry>stop},operation='finished Asia/London highs, five-minute break, later contemporaneous execution VWAP return',
        parents=[asia['id'],london['id'],breakout['bar_id']],known_at=decision,assumption='A2-GB-CLOCK/A2-STRUCTURAL-RISK')
    if retest is None:e.bind({'continuation_context':absent(m,breakout['end'],deadline)},operation='no later VWAP retest in declared observed horizon')
    e.stage('above_both_highs',breakout['end'],observed=True).stage('later_VWAP_return',retest_at,
        observed=True if retest else absent(m,breakout['end'],deadline),details=vw)
    return window_result(m,'GB-VWAP',branch,[e.finish(decision_at=decision,entry=entry,stop=stop)],omissions=omissions)
