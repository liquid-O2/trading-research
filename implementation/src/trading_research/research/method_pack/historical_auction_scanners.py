"""Saint, independent two-reason confluence, and Keani ordered auctions."""
from __future__ import annotations
from decimal import Decimal as D
from .historical_features import Q, MINUTE, SECOND, sign, balances, pivots, distinct_contacts, first_contact, delta
from .historical_assembly import HistoricalEpisode, absent, window_result, close_selection_omissions
from .historical_flow import exact_contact, local_observations, flow_stages, flow_absent
from .branch_coverage import setting


def primary_balance(m):
    found=balances(m.bars(m.start,m.end,300))
    before=[r for r in found if r['known_at']<=m.at('09:30')]
    return (before[-1] if before else found[0] if found else None),found


def _control(m,after,end,side):
    rows=m.bars(after,end)
    for a,b in zip(rows,rows[1:]):
        if a['end']!=b['start'] or not a['complete'] or not b['complete']:continue
        if all(r['delta'] is not None and sign(side)*r['delta']>0 and sign(side)*(r['C']-r['O'])>0 for r in (a,b)):
            return b,[a,b]
    return None,[]


def _control_absence(m,after,end,side):
    if not getattr(m,'reconstruct',False):
        return absent(m,after,end,fields=('O','C','delta'))
    if end<=after:return False
    rows=m.bars(after,end);uncertain=False;sg=sign(side)
    def directional(row):
        if not row['observed_complete']:return None
        effort=None if row['delta'] is None else sg*row['delta']>0
        body=None if row['O'] is None or row['C'] is None else sg*(row['C']-row['O'])>0
        if effort is False or body is False:return False
        return True if effort is True and body is True else None
    for a,b in zip(rows,rows[1:]):
        if a['end']!=b['start']:continue
        states=(directional(a),directional(b))
        if False in states:continue
        if states==(True,True):return True
        uncertain=True
    return None if uncertain else absent(m,after,end)


def _saint_base(e,m,ref,arrival,control,decision,side,entry,stop,target,*,control_start=None):
    profile=m.profile(ref['start'],ref['known_at'],'.68')
    permission=None if profile['poc'] is None else ref['low']<=profile['poc']<=ref['high']
    e.bind({'balance_fixed_before_use':ref['known_at']<=arrival,'balance_known_at':ref['known_at'],
        'profile_allows_trade':permission,'arrival_read_recorded':True,'arrival_at':arrival,
        'control_evidence_recorded':True if control else _control_absence(m,arrival//MINUTE*MINUTE if control_start is None else control_start,decision,side),
        'control_at':control['known_at'] if control else None,'alignment_ok':True if control else None,
        'risk_defined':None if entry is None else sign(side)*(entry-stop)>0,
        'objective_fixed':None if entry is None else sign(side)*(target-entry)>0},
        operation='distinct HTF price balance with 68% profile and current repeated directional body/delta control',
        parents=[ref['id'],profile['id']],known_at=decision,assumption='A2-BALANCE/A2-STRUCTURAL-RISK')
    e.geometry['htf_profile']=profile


def _upper_failures(m,ref,before):
    episodes=[]
    band=[ref['high']-Q,ref['high']+Q]
    for row in distinct_contacts(m.bars(max(m.start,ref['known_at']),before),*band):
        if row['delta'] is None or row['delta']<=0:continue
        response=next((r for r in m.bars(row['end'],min(before,row['end']+30*MINUTE)) if r['C'] is not None and r['C']<ref['high']-4*Q),None)
        if response and (not episodes or row['start']>episodes[-1]['known_at']):
            episodes.append({'id':row['bar_id']+':buying-failure','touch_at':row['start'],'known_at':response['known_at'],
                'aggression_bar':row,'response_bar':response,'band_id':ref['id']+':high'})
    return episodes


def scan_saint(m,branch):
    ref,allbalances=primary_balance(m);episodes=[];omissions=[]
    if ref is None:return window_result(m,'SAINT-AMT',branch,[],omissions=[{'reason':'no confirmed HTF price balance in observed prefix','kind':'measured_selection'}])
    begin=max(ref['known_at'],m.at('09:30'))
    if branch in {'continuation_retest','trapped_buyers_retest'}:
        ltfs=balances(m.bars(m.start,m.end,60),ref['width'])
        candidates=[r for r in ltfs if r['known_at']<=begin and r['start']>=ref['start']]
        ltf=candidates[-1] if candidates else next((r for r in ltfs if r['known_at']>begin),None)
        if ltf is None:return window_result(m,'SAINT-AMT',branch,[],omissions=[{'reason':'no distinct confirmed LTF price balance','kind':'measured_selection'}])
        for side in (('short',) if branch=='trapped_buyers_retest' else ('long','short')):
            sg=sign(side);boundary=ltf['high'] if side=='long' else ltf['low'];start=max(begin,ltf['known_at'])
            selection=m.bars(start,m.end)
            trigger=next((r for r in selection if r['observed_complete'] and r['C'] is not None and sg*(r['C']-boundary)>0),None)
            omissions.extend(close_selection_omissions(selection,trigger,boundary,side))
            if trigger is None:continue
            end=min(m.end,trigger['end']+60*MINUTE)
            retest=first_contact(m.bars(trigger['end'],end),boundary-Q,boundary+Q)
            touch=exact_contact(m,retest,boundary-Q,boundary+Q) if retest else None
            if retest and touch is None:retest=None
            control,controlbars=_control(m,retest['end'],end,side) if retest else (None,[])
            decision=control['known_at'] if control else end;entry=control['C'] if control else None
            stop=ltf['low']-Q if side=='long' else ltf['high']+Q;target=ref['high'] if side=='long' else ref['low']
            e=HistoricalEpisode(m,'SAINT-AMT',branch,side,trigger,ref)
            control_start=retest['end'] if retest else end
            _saint_base(e,m,ref,trigger['start'],control,decision,side,entry,stop,target,
                control_start=control_start if getattr(m,'reconstruct',False) else None)
            held=None if not retest or not control else all(r['L']>=boundary-Q*2 if side=='long' else r['H']<=boundary+Q*2 for r in m.bars(retest['start'],control['end']))
            e.bind({'same_boundary_retest_held':held if retest else absent(m,trigger['end'],end),
                'breakout_at':trigger['known_at'],'retest_at':touch['at'] if touch else None,
                'confirm_at':control['known_at'] if control else None},operation='actual LTF boundary break, later same-boundary return and current repeated body/delta control',
                parents=[ltf['id'],trigger['bar_id']],known_at=decision,assumption='A2-BALANCE')
            if branch=='continuation_retest':
                e.bind({'ltf_balance_broken':True,'ltf_balance_known_at':ltf['known_at'],
                    'repeated_aggression_in_trade_direction':True if control else _control_absence(m,control_start if getattr(m,'reconstruct',False) else trigger['end'],end,side)},
                    operation='distinct confirmed LTF structure and two successive native directional bodies',parents=[ltf['id']],assumption='A2-FLOW')
            else:
                failures=_upper_failures(m,ref,trigger['start'])
                e.bind({'prior_buying_at_upper_extreme':True if failures else absent(m,ref['known_at'],trigger['start'],fields=('C','delta')),
                    'two_distinct_prior_failures':True if len(failures)>=2 else absent(m,ref['known_at'],trigger['start'],fields=('C','delta')),
                    'prior_failures_known_at':failures[-1]['known_at'] if failures else None,'ltf_break_down':trigger['C']<ltf['low'],
                    'repeated_body_selling':True if control else _control_absence(m,control_start if getattr(m,'reconstruct',False) else trigger['end'],end,side)},
                    operation='two disjoint earlier upper-band buying failures before current down break/retest',parents=[r['id'] for r in failures],assumption='A2-FLOW/A2-REACTION-HVN')
                e.geometry['prior_failures']=failures
            e.geometry['ltf_balance']=ltf
            if getattr(m,'reconstruct',False):
                e.geometry.update(control_bars=controlbars,control_search_window=[control_start,decision])
            e.stage('ltf_break',trigger['end'],observed=True).stage('same_boundary_retest',touch['at'] if touch else None,observed=held)
            e.stage('current_control',control['end'] if control else None,observed=bool(controlbars))
            episodes.append(e.finish(decision_at=decision,entry=entry,stop=stop,target=target))
    else:
        older=[r for r in allbalances if r['known_at']<ref['start'] and r['id']!=ref['id']]
        old=older[-1] if older else None
        oldprofile=m.profile(old['start'],old['known_at'],setting('auction_selection')['saint_value_fraction']) if old else None
        if old is None:
            previous=m.prior('day');omissions.extend(previous['omissions'])
            from .historical_features import HistoricalFeatures
            for session in reversed(previous['sessions']):
                win=session['window']
                alternatives=[r for r in balances(win.bars(win.start,win.end,300)) if r['known_at']<ref['start']]
                if alternatives:
                    old=alternatives[-1]
                    past=HistoricalFeatures(m.day,data_root=m.data_root,document=win.document)
                    oldprofile=past.profile(old['start'],old['known_at'],setting('auction_selection')['saint_value_fraction'])
                    break
        if old is None:omissions.append({'reason':'no distinct older completed auction in current admitted prefix','required_input':'earlier same-contract auction history'})
        for side in ('long','short'):
            sg=sign(side);boundary=ref['low'] if side=='long' else ref['high']
            trigger=next((r for r in m.bars(begin,m.end) if (r['L']<boundary if side=='long' else r['H']>boundary)),None)
            if trigger is None:continue
            end=min(m.end,trigger['end']+60*MINUTE)
            oldtouch=first_contact(m.bars(trigger['start'],end),oldprofile['val'],oldprofile['vah']) if oldprofile and oldprofile['val'] is not None else None
            rejection=next((r for r in m.bars(oldtouch['end'],end) if r['C'] is not None and sg*(r['C']-(oldprofile['vah'] if side=='long' else oldprofile['val']))>0),None) if oldtouch else None
            # Reacceptance must follow an observed excursion. For traversal,
            # older-auction contact is not a source gate, but reacceptance is.
            route_start=rejection['end'] if branch=='failed_auction_return' and rejection else trigger['end']
            reaccept=next((r for r in m.bars(route_start,end) if r['C'] is not None and ref['low']<r['C']<ref['high']),None)
            profile=m.profile(ref['start'],ref['known_at'],'.68');poc=profile['poc']
            passage=next((r for r in m.bars(reaccept['end'],end) if r['observed_complete'] and r['C'] is not None and poc is not None and sg*(r['C']-poc)>0 and r['delta'] is not None and sg*r['delta']>0),None) if reaccept else None
            control,controlbars=_control(m,(passage if branch=='poc_traversal' else reaccept)['end'],end,side) if (passage if branch=='poc_traversal' else reaccept) else (None,[])
            decision=control['known_at'] if control else end;entry=control['C'] if control else None
            stop=min(trigger['L'],old['low'] if old else trigger['L'])-Q if side=='long' else max(trigger['H'],old['high'] if old else trigger['H'])+Q
            target=ref['high'] if side=='long' else ref['low']
            e=HistoricalEpisode(m,'SAINT-AMT',branch,side,trigger,ref)
            control_parent=passage if branch=='poc_traversal' else reaccept
            control_start=control_parent['end'] if control_parent else end
            _saint_base(e,m,ref,trigger['start'],control,decision,side,entry,stop,target,
                control_start=control_start if getattr(m,'reconstruct',False) else None)
            e.bind({'original_balance_reaccepted':True if reaccept else absent(m,trigger['end'],end,fields=('C',)),
                'reaccept_at':reaccept['known_at'] if reaccept else None},operation='outside original auction, followed by a later completed inside close',parents=[ref['id'],trigger['bar_id']],known_at=decision)
            if branch=='failed_auction_return':
                e.bind({'older_value_tested':True if oldtouch else None if old is None else absent(m,trigger['start'],end),
                    'older_value_rejected':True if rejection else None if old is None else absent(m,trigger['start'],end,fields=('C',)),
                    'older_value_known_at':old['known_at'] if old else None,'older_value_touch_at':oldtouch['start'] if oldtouch else None,
                    'rejection_at':rejection['known_at'] if rejection else None,'local_control_confirms_return':True if control else _control_absence(m,control_start if getattr(m,'reconstruct',False) else trigger['end'],end,side)},
                    operation='distinct older value exploration/rejection precedes original balance reacceptance and local control',parents=[old['id']] if old else [],known_at=decision,assumption='A2-BALANCE')
            else:
                held=None if not passage or not control else all(sg*(r['C']-poc)>=0 for r in controlbars)
                e.bind({'aggressive_poc_passage':True if passage else None if poc is None else absent(m,trigger['end'],end,fields=('C','delta')),
                    'source_poc_hold_confirmed':held,'target_is_far_balance_edge':target in (ref['low'],ref['high']),
                    'poc_passage_at':passage['known_at'] if passage else None},operation='aggressive original POC passage after reacceptance; two subsequent same-side body/delta closes hold',parents=[profile['id']],known_at=decision,assumption='A2-FLOW')
            e.geometry.update(older_balance=old,older_profile=oldprofile)
            if getattr(m,'reconstruct',False):
                e.geometry.update(control_bars=controlbars,control_search_window=[control_start,decision])
            for name,row in [('exploration',trigger),('older_touch',oldtouch),('older_rejection',rejection),('reacceptance',reaccept),('poc_passage',passage),('control',control)]:
                e.stage(name,row['known_at'] if row else None,observed=True if row else None)
            episodes.append(e.finish(decision_at=decision,entry=entry,stop=stop,target=target))
    return window_result(m,'SAINT-AMT',branch,episodes,omissions=omissions)


def scan_member(m,branch):
    prior=m.prior('day');episodes=[];omissions=list(prior['omissions'])
    if not prior['sessions']:return window_result(m,'MEMBER-TWO-REASONS',branch,[],omissions=omissions)
    day=prior['sessions'][-1];win=day['window'];from .empirical_market import clock
    from datetime import date
    split=clock(date.fromisoformat(day['day']),setting('auction_selection')['member_prior_split'])
    reactionbars=win.bars(win.start,split,300)
    reactions=pivots(reactionbars)
    qualified=[]
    for reaction in reactions:
        after=[r for r in reactionbars if r['start']>=reaction['at'] and r['known_at']<=reaction['known_at']]
        distance=(reaction['price']-min(r['L'] for r in after) if reaction['side']=='high' else max(r['H'] for r in after)-reaction['price']) if after else D(0)
        if distance>=Q*setting('reaction')['reaction_ticks']:
            qualified.append(dict(reaction,reaction_distance=distance))
    reactions=qualified
    profile=win.profile(split,win.end)
    levels={r['price']:r['total_volume'] for r in profile['rows']};radius=setting('reaction')['hvn_radius_ticks']
    nodes=[p for p,v in levels.items() if v>0 and all(v>levels.get(p+Q*i,D(0)) for i in range(-radius,radius+1) if i)]
    side='short' if branch=='resistance_short' else 'long';sg=sign(side)
    reactions=[r for r in reactions if r['side']==('high' if side=='short' else 'low')]
    candidates=[]
    for reaction in reactions:
        # Reaction confirmation and HVN profile use disjoint physical periods.
        matching=[p for p in nodes if abs(p-reaction['price'])<=Q*setting('reaction')['confluence_ticks']]
        if not matching:continue
        node=min(matching,key=lambda p:(abs(p-reaction['price']),p))
        candidates.append((reaction,node))
    # Choose the most recently confirmed independent reaction before looking
    # at current contacts; a failed/missing attempt is never replaced.
    if not candidates:return window_result(m,'MEMBER-TWO-REASONS',branch,[],omissions=omissions)
    reaction,node=candidates[-1];lo=min(reaction['price'],node)-Q;hi=max(reaction['price'],node)+Q
    ref={'id':reaction['id']+':independent-hvn:'+str(node),'low':lo,'high':hi,'known_at':win.end,
        'reaction':reaction,'hvn':node,'hvn_profile':profile,'reaction_window':[win.start,split],'hvn_window':[split,win.end]}
    contacts=list(distinct_contacts(m.bars(m.at('09:30'),m.end),lo,hi))
    # For planned return the earlier source reaction itself establishes first
    # visit; the current visit is a distinct later-session return.
    if not contacts:return window_result(m,'MEMBER-TWO-REASONS',branch,[],omissions=omissions)
    trigger=contacts[0];contact=exact_contact(m,trigger,lo,hi)
    if contact is None:return window_result(m,'MEMBER-TWO-REASONS',branch,[],omissions=[*omissions,{'reason':'bar contact has no exact band execution'}])
    obs=local_observations(m,contact['at'],[lo,hi],side);stages=flow_stages(obs);defense=stages['defense']
    # The member long requires absorption/hold, without adding Sires reward or
    # defended reward-retest. The short requires the actual rejection.
    selected=defense if side=='long' else stages['reward']
    decision=selected['known_at'] if selected else obs['end'];entry=selected.get('entry_px',selected['last']) if selected else None
    observed=[r for r in obs['chunks'] if r['end']<=decision]
    high=max((r['high'] for r in observed),default=hi);low=min((r['low'] for r in observed),default=lo)
    stop=high+Q if side=='short' else low-Q
    target=entry+sg*abs(entry-stop)*D(setting('reaction')['target_r']) if entry is not None else None
    e=HistoricalEpisode(m,'MEMBER-TWO-REASONS',branch,side,trigger,ref)
    independent=reaction['known_at']<=split and profile['formation_start']>=split
    e.bind({'thesis_predefined':ref['known_at']<contact['at'],'objective_fixed':None if entry is None else target is not None and sg*(target-entry)>0,
        'risk_defined':None if entry is None else sg*(entry-stop)>0,'prior_reaction_area_known':reaction['known_at']<contact['at'],
        'area_known_at':reaction['known_at'],'independent_minor_hvn_known':independent,'hvn_known_at':profile['known_at'],
        'confluence_band_defined':abs(node-reaction['price'])<=Q*setting('reaction')['confluence_ticks'],
        'actual_band_contact':True,'touch_at':contact['at'],'reaction_at':selected['known_at'] if selected else None},
        operation='earlier confirmed reaction and later disjoint-period local HVN, frozen before current band contact',
        parents=[reaction['id'],profile['profile_id'],*contact['event_ids']],known_at=decision,assumption='A2-REACTION-HVN/A2-STRUCTURAL-RISK')
    if side=='short':e.bind({'resistance_rejection':selected is not None or flow_absent(m,trigger['start'],min(m.end,(decision+MINUTE-1)//MINUTE*MINUTE),observed),
        'stop_above_rejection_high':stop>high},operation='current rejection and strictly outside observed high',known_at=decision,assumption='A2-FLOW')
    else:e.bind({'planned_return_to_structure':reaction['known_at']<contact['at'],
        'buyers_absorb_and_hold':defense['held'] if defense else flow_absent(m,trigger['start'],min(m.end,(decision+MINUTE-1)//MINUTE*MINUTE),observed),
        'stop_behind_long_invalidation':stop<low},operation='actual later return and buyers absorb/hold, with structural stop',known_at=decision,assumption='A2-FLOW')
    e.stage('prior_reaction',reaction['known_at'],observed=True).stage('independent_HVN',profile['known_at'],observed=independent)
    e.stage('current_contact',contact['at'],observed=True).stage('local_response',selected['known_at'] if selected else None,observed=selected is not None)
    if getattr(m,'reconstruct',False):
        e.geometry['local_flow']=[{k:v for k,v in r.items() if k not in {'events','event_ids','book_changes'}} for r in observed]
    return window_result(m,'MEMBER-TWO-REASONS',branch,[e.finish(decision_at=decision,entry=entry,stop=stop,target=target)],omissions=omissions)


def scan_keani(m,branch):
    prior=m.prior('day');old=prior['sessions'][-1]['window'] if prior['sessions'] else None
    p=old.profile(old.start,old.end) if old else None
    a=m.range(m.at('09:30'),m.at('10:00'),'Keani-A')
    if a is None:return window_result(m,'KEANI-OPEN-ABOVE-VALUE',branch,[],omissions=[*prior['omissions'],{'reason':'A period has no observed executions'}])
    initial=m.profile(a['start'],a['end']);limit=m.at(setting('keani_time')['latest_break'])
    observation=breakout=band=retest=defense=contact=None;dev=None;imbalance=None;obs=None;ambiguous_imbalance=[]
    for row in m.bars(a['end'],limit):
        current=m.profile(a['start'],row['start'])
        higher=current['val'] is not None and initial['val'] is not None and current['val']>initial['val'] and current['vah']>=initial['vah']
        rejection=higher and row['C'] is not None and row['L']<=current['val'] and row['C']>current['val']
        if observation is None and rejection:observation=row;continue
        if observation and row['observed_complete'] and row['C'] is not None and current['vah'] is not None and row['C']>current['vah']:
            footprint=m.window.footprints.get(row['start'])
            if footprint:
                if any(u>0 for px,b,s,u in footprint['rows']):
                    ambiguous_imbalance.append(row['bar_id'])
                    continue
                cfg=setting('imbalance')
                im=m.domain('O109',{'candle_id':row['bar_id'],'footprint_rows':[{'price':px,'B':b,'A':s} for px,b,s,u in footprint['rows']],
                    'q':Q,'ratio_min':D(cfg['ratio']),'row_count':cfg['consecutive_rows'],'zero_rule':cfg['zero'],'known_at':row['known_at']})
                runs=im.get('buy_runs',[])
                if runs:
                    breakout=row;dev=current;imbalance=im;band=[D(str(v)) for v in runs[0]['band']];break
    if breakout:
        retest=first_contact(m.bars(breakout['end'],min(m.end,breakout['end']+60*MINUTE)),*band)
        if retest:
            contact=exact_contact(m,retest,*band)
            if contact:
                obs=local_observations(m,contact['at'],band,'long');st=flow_stages(obs);defense=st['defense']
    decision=defense['known_at'] if defense else min(m.end,limit+60*MINUTE);entry=defense.get('entry_px',defense['last']) if defense else None
    stop=band[0]-Q if band else a['low']-Q
    target=(prior['range']['high'] if prior['range'] and entry is not None and prior['range']['high']>entry else
            a['high']+(a['high']-a['low']))
    e=HistoricalEpisode(m,'KEANI-OPEN-ABOVE-VALUE',branch,'long',{'bar_id':a['id'],'start':a['start'],'end':a['end']},a)
    absent_stage=None if ambiguous_imbalance else absent(m,a['end'],limit,fields=('C',))
    absent_defense=flow_absent(m,retest['start'],min(m.end,(decision+MINUTE-1)//MINUTE*MINUTE),[r for r in obs['chunks'] if r['known_at']<=decision]) if obs else absent_stage
    e.bind({'prior_value_fixed':True if p and p.get('vah') is not None and prior['scope_complete'] else None,'prior_vah':p['vah'] if p and prior['scope_complete'] else None,
        'a_period_complete':True if a['coverage']['observed_scope_complete'] else None,'a_low':a['low'],'a_end_at':a['known_at'],
        'developing_value_builds_higher':True if observation else absent_stage,'source_rejection_observed':True if observation else absent_stage,
        'observation_at':observation['known_at'] if observation else None,'dev_vah_known_at':dev['known_at'] if dev else None,
        'dev_vah_at_break':dev['vah'] if dev else None,'breakout_at':breakout['known_at'] if breakout else None,
        'breakout_close':breakout['C'] if breakout else None,'aggressive_buy_imbalance_break':True if breakout else absent_stage,
        'imbalance_band_known_at':breakout['known_at'] if breakout else None,'retest_at':contact['at'] if contact else None,
        'defense_at':defense['known_at'] if defense else None,'buyers_defend_same_imbalance_band':defense['held'] if defense else absent_defense,
        'dom_supports_long':defense['displayed_defense'] if defense else absent_defense,
        'time_of_day_allowed':breakout['known_at']<=limit if breakout else absent_stage,
        'objective_fixed':None if entry is None else target>entry,'risk_defined':None if entry is None else entry>stop},
        operation='whole A above prior value, later higher-building/rejected developing value, actual diagonal buy stack break, same-stack-band defended return',
        parents=[a['id'],p['profile_id']] if p else [a['id']],known_at=decision,
        assumption='A2-KEANI-TIME/A2-PROFILE/A2-IMBALANCE/A2-FLOW/A2-STRUCTURAL-RISK')
    e.geometry.update(prior_profile=p,a_profile=initial,developing_profile=dev,imbalance=imbalance,imbalance_band=band)
    if getattr(m,'reconstruct',False):e.geometry.update(observation_bar=observation,breakout_bar=breakout)
    for name,row in [('developing_value_rejection',observation),('imbalance_break',breakout),('same_band_return',retest),('buyer_defense',defense)]:
        e.stage(name,row['known_at'] if row else None,observed=True if row else absent_stage)
    omissions=[*prior['omissions']]
    if ambiguous_imbalance:omissions.append({'kind':'input_ambiguity','reason':'candidate footprint has unknown aggressor quantity; diagonal imbalance cannot be certified','candle_ids':ambiguous_imbalance,'required_fields':['aggressor_side']})
    return window_result(m,'KEANI-OPEN-ABOVE-VALUE',branch,[e.finish(decision_at=decision,entry=entry,stop=stop,target=target)],omissions=omissions)
