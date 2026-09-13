"""Local execution/depth-one observations and twelve ordered Sires branches."""
from __future__ import annotations
from collections import defaultdict
from decimal import Decimal as D
from .historical_features import Q, MINUTE, SECOND, sign, balances, distinct_contacts, delta
from .historical_assembly import HistoricalEpisode, absent, window_result, close_selection_omissions
from .branch_coverage import setting
from .event_time import BookObservations


def batches(events):
    grouped=defaultdict(list)
    for row in events:grouped[row['event_ns']].append(row)
    return sorted(grouped.items())


def exact_contact(m,row,lo,hi,*,strict=None):
    events=m.local(row['start'],row['end'])
    for at,batch in batches(events):
        selected=[r for r in batch if (r['price']<lo if strict=='below' else r['price']>hi if strict=='above' else lo<=r['price']<=hi)]
        if selected:
            return {'at':at,'known_at':max(r['known_at'] for r in batch),'event_ids':[r['event_id'] for r in selected],
                'prices':sorted({r['price'] for r in selected}), 'batch_id':f'{m.instrument_id}:{at}'}
    return None


def local_observations(m,touch,band,side,*,horizon=None,book=True):
    """Independent effort/response intervals; no later reward chooses origin."""
    cfg=setting('flow');sg=sign(side);lo,hi=band;origin=(lo+hi)/2
    step=cfg['effort_seconds']*SECOND
    start=max(m.start,touch-step);end=min(m.end,touch+(horizon or cfg['local_horizon_seconds'])*SECOND)
    raw=m.local(start,end,book=book)
    trades=[r for r in raw if r['action']=='T']
    bookrows=[]
    if book:
        acc=BookObservations()
        for row in raw:bookrows.extend(acc.add(row))
        bookrows.extend(acc.finish())
    chunks=[]
    for a in range(start,end,step):
        b=min(a+step,end)
        rows=[r for r in trades if a<=r['event_ns']<b and r['known_at']<=b]
        if not rows:continue
        grouped=batches(rows);firstprices={r['price'] for r in grouped[0][1]};lastprices={r['price'] for r in grouped[-1][1]}
        first=next(iter(firstprices)) if len(firstprices)==1 else None
        last=next(iter(lastprices)) if len(lastprices)==1 else None
        price_basis='unique price at timestamp endpoint'
        if getattr(m,'reconstruct',False):
            from .strategy_measurements import batch_price
            first=batch_price(grouped[0][1]);last=batch_price(grouped[-1][1])
            price_basis='execution VWAP of first/last timestamp batch; no within-batch order asserted'
        nearby=[r for r in rows if lo-Q*cfg['band_halfwidth_ticks']<=r['price']<=hi+Q*cfg['band_halfwidth_ticks']]
        buys=sum(r['executed_size'] for r in nearby if r['side']=='B');sells=sum(r['executed_size'] for r in nearby if r['side']=='A')
        unknown=sum(r['executed_size'] for r in nearby if r['side']=='N')
        own=buys if side=='long' else sells;opposing=sells if side=='long' else buys
        opponent=[r for r in nearby if r['side']==('A' if side=='long' else 'B')]
        completed=[r for r in bookrows if a<=r['event_ns']<b and r['known_at']<=b and not r['bad_book'] and not r['reset']]
        passive='bid' if side=='long' else 'ask'
        displayed=[r for r in completed if r[passive] is not None and lo<=r[passive]<=hi]
        added=[r for r in displayed if (r.get(passive+'_added') or 0)>0]
        held=min(r['price'] for r in rows)>=lo-Q*cfg['no_progress_ticks'] if side=='long' else max(r['price'] for r in rows)<=hi+Q*cfg['no_progress_ticks']
        no_progress=None if first is None or last is None else -sg*(last-first)<=Q*cfg['no_progress_ticks']
        previous=chunks[-1] if chunks else None
        effort=None if unknown or (previous and previous['unknown']) else len(opponent)>=cfg['minimum_effort_events'] and opposing>own and (previous is None or opposing>=previous['opposing'])
        chunks.append({'id':f'flow:{m.instrument_id}:{a}:{b}:{lo}:{hi}:{side}','start':a,'end':b,
            'known_at':max(b,max(r['known_at'] for r in rows)),'low':min(r['price'] for r in rows),'high':max(r['price'] for r in rows),
            'first':first,'last':last,'price_basis':price_basis,
            'entry_px':(max(lastprices) if side=='long' else min(lastprices)) if getattr(m,'reconstruct',False) else last,
            'own':own,'opposing':opposing,'unknown':unknown,'delta':buys-sells,
            'opponent_mean':D(opposing)/len(opponent) if opponent else D(0),'count':len(rows),
            'opponent_count':len(opponent),'nearby_count':len(nearby),'effort':effort,'no_progress':no_progress,
            'held':held,'displayed_defense':bool(displayed) if completed else None,
            'added_at':added[0]['event_ns'] if added else None,
            'added_size':sum(r[passive+'_added'] for r in added),'book_observed':bool(completed),
            'event_ids':[r['event_id'] for r in rows],'events':rows,'book_ids':[r['event_ns'] for r in displayed],
            'book_changes':added,'origin':origin})
    return {'chunks':chunks,'raw_events':trades,'book_observations':bookrows,'start':start,'end':end,
        'band':band,'side':side,'origin':origin,'feed_complete':None,
        'book_interpretation':'displayed depth-one participation; individual passive order/hidden reserve not asserted'}


def flow_stages(obs):
    chunks=obs['chunks'];sg=sign(obs['side']);origin=obs['origin'];cfg=setting('flow')
    selected={}
    defense=next((r for r in chunks if r['start']>=obs['start']+cfg['effort_seconds']*SECOND and r['effort'] and r['no_progress'] is True and r['held']),None)
    selected['defense']=defense
    later=[r for r in chunks if defense and r['start']>=defense['end']]
    refresh=next((r for r in later if r['added_at'] is not None and r['opposing']>0 and r['held']),None)
    selected['refresh']=refresh
    thinning=next((r for r in later if refresh and r['start']>=refresh['end'] and r['unknown']==0 and r['opponent_mean']<=defense['opponent_mean']*D(cfg['thinning_fraction']) and r['opposing']<defense['opposing']),None)
    selected['thinning']=thinning
    reward=next((r for r in later if r['last'] is not None and sg*(r['last']-origin)>=Q*cfg['reward_ticks'] and r['unknown']==0 and r['own']>r['opposing']),None)
    selected['reward']=reward
    reward_retest=next((r for r in later if reward and r['start']>=reward['end'] and r['low']<=reward['last']<=r['high']),None)
    selected['reward_retest']=reward_retest
    renewed=next((r for r in later if reward_retest and r['start']>=reward_retest['end'] and r['unknown']==0 and r['own']>r['opposing'] and r['held']),None)
    selected['renewed']=renewed
    liftoff=next((r for r in later if thinning and r['start']>=thinning['end'] and r['last'] is not None and D(2)*Q<=sg*(r['last']-origin)<=D(4)*Q and r['unknown']==0 and r['own']>r['opposing']),None)
    selected['liftoff']=liftoff
    return selected


def _catalyst_stages(obs,stages):
    chunks=obs['chunks'];sg=sign(obs['side']);origin=obs['origin'];catalyst=stages['defense']
    release=next((r for r in chunks if catalyst and r['start']>=catalyst['end'] and r['last'] is not None and sg*(r['last']-origin)>=Q*3 and r['unknown']==0 and r['own']>r['opposing']),None)
    failure=next((r for r in chunks if release and r['start']>=release['end'] and r['last'] is not None and sg*(r['last']-origin)<=Q),None)
    refill=next((r for r in chunks if failure and r['start']>=failure['end'] and r['held'] and r['added_at'] is not None),None)
    drive=next((r for r in chunks if refill and r['start']>=refill['end'] and r['last'] is not None and sg*(r['last']-release['last'])>0 and r['unknown']==0 and r['own']>r['opposing']),None)
    retest=next((r for r in chunks if drive and r['start']>=drive['end'] and r['low']<=drive['last']<=r['high'] and r['unknown']==0 and r['own']>r['opposing']),None)
    pullback=next((r for r in chunks if release and r['start']>=release['end'] and r['last'] is not None and sg*(r['last']-release['last'])<0),None)
    continuation=next((r for r in chunks if pullback and r['start']>=pullback['end'] and r['last'] is not None and sg*(r['last']-release['last'])>0 and r['unknown']==0 and r['own']>r['opposing']),None)
    return dict(catalyst=catalyst,release=release,failure=failure,refill=refill,drive=drive,retest=retest,pullback=pullback,continuation=continuation)


def flow_absent(m,start,end,chunks):
    if any(r['first'] is None or r['last'] is None or r['unknown']>0 for r in chunks):return None
    return absent(m,start,end)


def _timestamp(row):return row['known_at'] if row else None


def _seen(row,fallback):return True if row else fallback


def _base(e,m,ref,touch,side,decision,entry,stop,target,*,gamma=False):
    sg=sign(side)
    e.bind({'thesis_alive':None if entry is None else sg*(entry-stop)>0,'auction_route_ok':ref.get('complete',True),
        'branch_regime_allowed':None if gamma else True,'location_fixed':ref['known_at']<=touch['at'],
        'location_touched':True,'objective_fixed':None if entry is None else sg*(target-entry)>0,
        'risk_defined':None if entry is None else sg*(entry-stop)>0,'thesis_known_at':ref['known_at'],
        'location_known_at':ref['known_at'],'touch_at':touch['at'],'confirm_at':decision},
        operation='pre-touch price-defined auction/reference; side-specific death beyond structure and opposite known boundary objective',
        parents=[ref['id'],*touch['event_ids']],known_at=decision,assumption='A2-BALANCE/A2-STRUCTURAL-RISK')


def _flow_episode(m,branch,ref,trigger,side,band,*,vwap=None):
    contact=exact_contact(m,trigger,*band)
    if not contact:return None
    obs=local_observations(m,contact['at'],band,side);st=flow_stages(obs);cat=_catalyst_stages(obs,st)
    end=obs['end'];sg=sign(side);origin=obs['origin']
    selected={'dom_rejection':st['reward'],'absorption_reward_retest':st['renewed'],'stop_four_stage':st['liftoff'],
        'footprint_confirmed_reaction':st['reward'],'vwap_deviation_fade':st['reward'],'ofm_aggressive':cat['retest'],
        'ofm_passive':next((r for r in obs['chunks'] if cat['failure'] and r['start']>=cat['failure']['end'] and r['last'] is not None and r['last']>band[1]),None),'clean_squeeze':cat['continuation'],'balance_failure_fade':cat['refill'],
        'defended_band_continuation':st['refresh'],'kg1_retest':st['reward']}.get(branch)
    decision=_timestamp(selected) or end
    if branch=='footprint_confirmed_reaction':
        decision=min(m.end,max(decision,(contact['at']//MINUTE+1)*MINUTE))
    # Do not let a later successful stage rewrite the earlier evidence used by
    # another branch's decision; restrict every summary to this cutoff.
    chunks=[r for r in obs['chunks'] if r['known_at']<=decision]
    missing=flow_absent(m,trigger['start'],min(m.end,((decision+MINUTE-1)//MINUTE)*MINUTE),chunks)
    for collection in (st,cat):
        for k,r in collection.items():
            if r and r['known_at']>decision:collection[k]=None
    entry=selected.get('entry_px',selected['last']) if selected else (chunks[-1].get('entry_px',chunks[-1]['last']) if chunks else None)
    stop=band[0]-Q if side=='long' else band[1]+Q
    target=ref.get('long_target',ref['high']) if side=='long' else ref.get('short_target',ref['low'])
    if vwap:target=vwap['price']
    e=HistoricalEpisode(m,'SIRES',branch,side,trigger,ref)
    _base(e,m,ref,contact,side,decision,entry,stop,target,gamma=branch in {'ofm_aggressive','balance_failure_fade'})
    defense=st['defense'];reward=st['reward'];refresh=st['refresh'];thinning=st['thinning'];liftoff=st['liftoff']
    own_delta=None if not chunks or any(r['unknown']>0 for r in chunks) else sum(r['delta'] for r in chunks)*sg>0
    checks={}
    if branch=='dom_rejection':
        checks={'arriving_aggression':_seen(defense,missing),'little_progress':defense['no_progress'] if defense else missing,
            'local_rejection':_seen(reward,missing),'source_dom_confirmation':defense['displayed_defense'] if defense else missing,
            'aggression_at':_timestamp(defense),'rejection_at':_timestamp(reward)}
    elif branch=='absorption_reward_retest':
        checks={'real_extreme':origin<=ref['low']+Q or origin>=ref['high']-Q,
            'passive_wall_confirmed':defense['displayed_defense'] if defense else missing,
            'opposing_effort_no_result':_seen(defense,missing),'own_reward_confirmed':_seen(reward,missing),
            'reward_near_origin':None if reward is None else abs(reward['first']-origin)<=Q*setting('flow')['near_origin_ticks'] if reward['first'] is not None else None,
            'fresh_reward_retest_defended':_seen(st['renewed'],missing),'cvd_filter_ok':own_delta,
            'absorption_at':_timestamp(defense),'reward_at':_timestamp(reward),'retest_at':_timestamp(st['reward_retest'])}
    elif branch=='stop_four_stage':
        checks={'real_extreme':origin<=ref['low']+Q or origin>=ref['high']-Q,
            'defense':_seen(defense,missing),'replenishment':_seen(refresh,missing),'opponent_thinning':_seen(thinning,missing),
            'absorber_aggressive':liftoff['own']>liftoff['opposing'] if liftoff else missing,'delta_filter_ok':own_delta,
            'lift_off':_seen(liftoff,missing),'reward_ticks':sg*(liftoff['last']-origin)/Q if liftoff else None,
            'entry_distance_ticks':abs(entry-liftoff['last'])/Q if liftoff and entry is not None else None,
            'daily_r_before':None,'defense_at':_timestamp(defense),'replenish_at':_timestamp(refresh),
            'exhaust_at':_timestamp(thinning),'liftoff_at':_timestamp(liftoff)}
        account=m.supplied('account',decision)
        if account:checks['daily_r_before']=D(str(account[-1]['daily_r_before']))
    elif branch=='footprint_confirmed_reaction':
        candle_start=contact['at']//MINUTE*MINUTE;candle_end=candle_start+MINUTE
        candle=m.bars(candle_start,candle_end)
        same=m.local(candle_start,min(candle_end,m.end))
        snapshots=[]
        for at in (candle_start+30*SECOND,candle_end):
            if at>decision:continue
            levels=defaultdict(int)
            for row in same:
                if row['event_ns']<at and row['known_at']<=at:levels[row['price']]+=row['executed_size']
            snapshots.append((at,min(levels,key=lambda p:(-levels[p],p)) if levels else None))
        flip=None if len(snapshots)!=2 or any(px is None for at,px in snapshots) else sg*(snapshots[1][1]-snapshots[0][1])>0
        c=candle[0] if candle and candle_end<=decision else None
        checks={'at_valid_level':ref['known_at']<=contact['at'],'candle_delta_disagreement':None if not c or c['C'] is None or c['O'] is None or c['delta'] is None else (c['C']-c['O'])*c['delta']<0,
            'local_absorption':_seen(defense,missing),'intrabar_poc_flip':flip,'source_flow_confirmation':own_delta,
            'level_known_at':ref['known_at'],'absorption_at':_timestamp(defense),'flip_at':snapshots[-1][0] if flip else None}
        e.geometry.update(candle_id=c['bar_id'] if c else None,poc_snapshots=[list(r) for r in snapshots])
    elif branch=='vwap_deviation_fade':
        checks={'source_vwap_known':vwap is not None,'selected_deviation_touched':True,
            'absorption_at_that_band':_seen(defense,missing),'cvd_filter_ok':own_delta,
            'ladder_confirmation':defense['displayed_defense'] if defense else missing,'band_known_at':vwap['known_at']}
        e.geometry.update(vwap_snapshot=vwap,selected_band=band)
    elif branch=='ofm_aggressive':
        checks={'short_gamma':None,'repeated_effort_no_reward':True if sum(r['effort'] is True and r['no_progress'] is True for r in chunks if cat['release'] and r['end']<=cat['release']['start'])>=2 else missing,
            'first_squeeze':_seen(cat['release'],missing),'squeeze_failed':_seen(cat['failure'],missing),
            'catalyst_reclaimed':_seen(cat['refill'],missing),'refill_held':cat['refill']['held'] if cat['refill'] else missing,
            'initiative_drive':_seen(cat['drive'],missing),'intervening_wicks_taken':None if not cat['drive'] or not any(cat['failure']['end']<=r['end']<cat['drive']['start'] for r in chunks) else (
                cat['drive']['last']>max(r['high'] for r in chunks if cat['failure']['end']<=r['end']<cat['drive']['start']) if side=='long' else
                cat['drive']['last']<min(r['low'] for r in chunks if cat['failure']['end']<=r['end']<cat['drive']['start'])),
            'drive_retest_defended':_seen(cat['retest'],missing),'own_aggression_rewarded':_seen(cat['drive'],missing),'cvd_filter_ok':own_delta,
            'catalyst_at':_timestamp(cat['catalyst']),'first_release_at':_timestamp(cat['release']),'failure_at':_timestamp(cat['failure']),
            'refill_at':_timestamp(cat['refill']),'drive_at':_timestamp(cat['drive']),'retest_at':_timestamp(cat['retest'])}
    elif branch=='ofm_passive':
        failure=cat['failure'];release=cat['release'];buyers=[r for r in chunks if failure and r['end']<=failure['end'] and r['unknown']==0 and r['own']>r['opposing']]
        trigger_above=next((r for r in chunks if failure and r['start']>=failure['end'] and r['last'] is not None and r['last']>band[1]),None)
        checks={'source_squeeze_failed':_seen(failure,missing),'tape_died_at_failure':None if not failure or not release else failure['count']<release['count']*D('.5'),
            'no_aggression_at_failure':None if not failure or (failure['opponent_count']==0 and failure['unknown']>0) else failure['opponent_count']==0,'buyers_area_identified':True if buyers else missing,
            'entry_above_buyers':None if entry is None else entry>band[1],'stop_below_aggression':stop<band[0],
            'failure_at':_timestamp(failure),'entry_trigger_at':_timestamp(trigger_above)}
    elif branch=='clean_squeeze':
        release=cat['release'];pullback=cat['pullback'];catalyst=cat['catalyst']
        checks={'catalyst_known':_seen(catalyst,missing),'fast_release':None if not release or not catalyst else release['count']>catalyst['count'],
            'no_prior_squeeze_failure':False if cat['failure'] else True if missing is False else None,
            'first_pullback':_seen(pullback,missing),'opposing_pullback_aggression_absorbed':None if not pullback or pullback['unknown']>0 else pullback['opposing']>pullback['own'] and pullback['held'],
            'continuation_confirmed':_seen(cat['continuation'],missing),'catalyst_at':_timestamp(catalyst),
            'release_at':_timestamp(release),'pullback_at':_timestamp(pullback)}
    elif branch=='balance_failure_fade':
        leave=cat['release'];retest=cat['failure']
        checks={'long_gamma':None,'balance_context':bool(ref.get('pivots')),'failed_aggression_at_extreme':_seen(defense,missing),
            'left_failed_area':_seen(leave,missing),'retest_same_failed_area':_seen(retest,missing),
            'aggression_still_unrewarded':None if not retest else retest['no_progress'],'target_is_prior_opposite_control':target in (ref['low'],ref['high']),
            'failure_at':_timestamp(defense),'leave_at':_timestamp(leave),'retest_at':_timestamp(retest)}
    elif branch=='defended_band_continuation':
        prior_at=ref.get('prior_defense_at')
        checks={'prior_band_control':prior_at is not None,'same_band_retest':True,'fresh_same_side_defense':_seen(defense,missing),
            'executed_aggression':own_delta,'refresh_consistent':_seen(refresh,missing),'control_side_matches_thesis':own_delta,
            'prior_defense_at':prior_at,'retest_at':contact['at']}
    elif branch=='kg1_retest':
        checks={'source_kg1_level_known':ref.get('external_record') is True or ref.get('inferred_level') is True,'kg1_retest':True,'aggression_confirms':own_delta,
            'level_known_at':ref['known_at'],'retest_at':contact['at']}
    else:raise ValueError('unsupported local branch '+branch)
    gamma=m.supplied('gamma',contact['at']) if branch in {'ofm_aggressive','balance_failure_fade'} else []
    if not gamma and getattr(m,'reconstruct',False) and branch in {'ofm_aggressive','balance_failure_fade'}:
        from .strategy_options import gamma_at
        inferred=gamma_at(m,contact['at'])
        e.geometry['inferred_gamma']=inferred
        if inferred['available'] and inferred.get('regime') is not None:gamma=[inferred]
    if gamma:
        key='short_gamma' if branch=='ofm_aggressive' else 'long_gamma'
        checks[key]=gamma[-1]['regime']==key.removesuffix('_gamma')
        e.bind({'branch_regime_allowed':checks[key]},operation='pre-touch gamma regime; source record or explicitly identified QQQ option model',kind='inferred_model' if gamma[-1].get('model') else 'record',parents=[gamma[-1]['id']],known_at=gamma[-1]['known_at'])
    e.bind(checks,operation='ordered native effort, response, depth-one additions, thinning, reward and distinct retest observations',
        parents=[r['id'] for r in chunks],known_at=decision,assumption='A2-FLOW')
    for name,row in {**st,**cat}.items():
        e.stage(name,_timestamp(row),observed=_seen(row,missing),parents=[row['id']] if row else [])
    e.geometry['local_flow']=[{k:v for k,v in r.items() if k not in {'events','event_ids','book_changes'}} for r in chunks]
    e.geometry['local_flow_membership']=[r['event_id'] for r in obs['raw_events'] if r['known_at']<=decision and r['event_ns']<decision]
    # Route actual numeric members through existing object producers as well.
    if defense:
        m.domain('O098',{'events':defense['events'],'instrument_id':m.instrument_id,'known_at':defense['known_at']})
        m.domain('O101',{'events':defense['events'],'band':band,'aggressive_side':'sell' if side=='long' else 'buy',
            'origin':defense['first'],'later_px':defense['last'],'q':Q,'passive_defense':defense['displayed_defense'],
            'source_absorption':None,'known_at':defense['known_at']})
    return e.finish(decision_at=decision,entry=entry,stop=stop,target=target)


def scan_sires(m,branch):
    episodes=[];omissions=[]
    allbars=m.bars(m.start,m.end,300);auction=balances(allbars)
    if branch=='microbalance_break':return scan_microbalance(m,branch,auction)
    if branch=='kg1_retest':
        refs=[{**r,'external_record':True,'low':D(str(r['low'])),'high':D(str(r['high']))} for r in m.supplied('kg1',m.end)]
        if not refs and getattr(m,'reconstruct',False):
            from .strategy_options import key_gamma_reference
            refs=key_gamma_reference(m)
        if not refs:omissions.append({'reason':'KG1/key-gamma model input unavailable','operand':'source_kg1_level_known'})
    else:
        before=[r for r in auction if r['known_at']<=m.at('09:30')]
        refs=before[-1:] if before else auction[:1]
    if branch=='vwap_deviation_fade':
        # One first distinct visit per side to a band frozen before that minute.
        seen=set()
        for row in m.bars(m.at('09:30'),m.end):
            vw=m.vwap(row['start'])
            if vw['price'] is None or vw['sd'] in (None,0):continue
            before=[r for r in auction if r['known_at']<=row['start']]
            if not before:continue
            ref=before[-1]
            for side in ('long','short'):
                if side in seen:continue
                px=vw['price']-vw['sd'] if side=='long' else vw['price']+vw['sd']
                if row['L']<=px<=row['H']:
                    seen.add(side);result=_flow_episode(m,branch,ref,row,side,[px-Q,px+Q],vwap=vw)
                    if result:episodes.append(result)
    else:
        used=set()
        for ref in refs:
            start=max(ref['known_at'],m.at('09:30'))
            if start>=m.end:continue
            for side in (('long',) if branch=='ofm_passive' else ('long','short')):
                key=tuple(p['id'] for p in ref.get('pivots',[])),side
                if key in used:continue
                edge=ref['low'] if side=='long' else ref['high'];band=[ref['low'],ref['high']] if branch=='kg1_retest' else [edge-Q,edge+Q]
                contacts=list(distinct_contacts(m.bars(start,m.end),*band))
                if not contacts:continue
                trigger=contacts[0]
                if branch=='defended_band_continuation':
                    if len(contacts)<2:continue
                    prior=_flow_episode(m,'dom_rejection',ref,contacts[0],side,band)
                    if prior is None:continue
                    prior_defense=next((r for r in prior['stages'] if r['stage']=='defense' and r['observed'] is True),None)
                    if not prior_defense:continue
                    ref={**ref,'prior_defense_at':prior_defense['at']};trigger=contacts[1]
                used.add(key)
                result=_flow_episode(m,branch,ref,trigger,side,band)
                if result:episodes.append(result)
    if not auction and branch!='kg1_retest':omissions.append({'reason':'no confirmed alternating-pivot auction in observed prefix','kind':'measured_selection'})
    return window_result(m,'SIRES',branch,episodes,omissions=omissions)


def scan_microbalance(m,branch,auction=None):
    auction=auction if auction is not None else balances(m.bars(m.start,m.end,300));episodes=[];omissions=[]
    used=set()
    for ref in auction:
        if ref['known_at']>=m.end:continue
        prior=[r for r in auction if r['known_at']<ref['start'] and r['width']>ref['width']]
        if not prior:continue
        htf=prior[-1]
        for side in ('long','short'):
            boundary=ref['high'] if side=='long' else ref['low'];sg=sign(side)
            selection=m.bars(max(ref['known_at'],m.at('09:30')),m.end)
            trigger=next((r for r in selection if r['observed_complete'] and r['C'] is not None and sg*(r['C']-boundary)>0),None)
            omissions.extend(close_selection_omissions(selection,trigger,boundary,side))
            if trigger is None or trigger['bar_id'] in used:continue
            used.add(trigger['bar_id']);stop=ref['low']-Q if side=='long' else ref['high']+Q
            target=htf['high'] if side=='long' else htf['low']
            e=HistoricalEpisode(m,'SIRES',branch,side,trigger,ref)
            contact={'at':trigger['start'],'event_ids':[trigger['bar_id']]}
            _base(e,m,ref,contact,side,trigger['known_at'],trigger['C'],stop,target)
            strength=None if trigger['delta'] is None else sg*trigger['delta']>0
            e.bind({'microbalance_frozen':True,'directional_strength':strength,'breakout_in_thesis_direction':sg*(trigger['C']-boundary)>0,
                'stop_behind_microbalance':stop<ref['low'] if side=='long' else stop>ref['high'],
                'microbalance_known_at':ref['known_at'],'breakout_at':trigger['known_at']},operation='price-defined alternating pivots inside earlier larger balance; directional executed delta and structural breakout',
                parents=[ref['id'],htf['id'],trigger['bar_id']],known_at=trigger['known_at'],assumption='A2-BALANCE')
            e.stage('confirmed_price_balance',ref['known_at'],observed=True).stage('directional_break',trigger['known_at'],observed=strength)
            episodes.append(e.finish(decision_at=trigger['known_at'],entry=trigger['C'],stop=stop,target=target))
    return window_result(m,'SIRES',branch,episodes,omissions=omissions)
