"""Execute every frozen bar-based observation unit on one native partition."""
from __future__ import annotations

from dataclasses import replace
from datetime import timedelta
from decimal import Decimal

from .empirical_market import clock, previous_weekday
from .empirical_protocol import ReplayResult
from .empirical_selectors import (MINUTE, _bar_ok, compact_bar, first_excursions,
                                 later_touch, make_opportunity, next_aligned_close)


def _unknown(opportunity, at, reason, *, ambiguous=False):
    return ReplayResult(opportunity.opportunity_id,'unknown',min(at,opportunity.expiry_at),None,reason,
                        censored=not ambiguous,ambiguous=ambiguous).validate(opportunity)


def _endpoint(opportunity,bar,passed,reason):
    return ReplayResult(opportunity.opportunity_id,'pass' if passed else 'fail',bar['known_at'],
                        compact_bar(bar),reason,selected_signal_at=bar['known_at'] if passed else None).validate(opportunity)


def _full_later(opportunity,bars):
    """Yield only later complete bars, raising a witnessed coverage stop."""
    cursor=opportunity.available_at
    for bar in bars:
        if bar['start'] < cursor:continue
        if bar['start'] >= opportunity.expiry_at:break
        if bar['start']!=cursor or not _bar_ok(bar,opportunity.instrument_id):
            yield None,cursor
            return
        if bar['known_at']>opportunity.expiry_at:break
        cursor=bar['end']
        yield bar,cursor
    if cursor<opportunity.expiry_at:yield None,cursor


def _detect(rule,market,registry,ref,start,end,*,trigger='strict_sweep',sides=('short','long'),minutes=1):
    return first_excursions(rule,market.partition,ref,market.bars(start,end,minutes),
        registry_sha256=registry['registry_sha256'],action_start=start,expiry_at=end,trigger=trigger,sides=sides)


def _rows(rows,holes=(),references=()):
    return {'records':rows,'population_holes':list(dict.fromkeys(holes)),
            'references':list(references),'search_executed':True}


def _verified_prior_rth_profile(rule, market, prior_profile, *, require_value_area=False):
    """Admit only the exact same-contract previous-RTH profile frozen by a rule."""
    profile=(prior_profile or {}).get('profile',{})
    if not profile or profile.get('coverage',{}).get('ok') is not True:
        return None
    prior_day=previous_weekday(market.day)
    start=clock(prior_day,'09:30')
    end=clock(prior_day,'16:00')
    required_identity=('profile_id','snapshot_id','formation_start','formation_end',
                       'as_of','known_at','instrument_id','kind','session_date')
    if any(profile.get(key) is None for key in required_identity):
        raise ValueError('prior RTH profile lacks exact snapshot/session identity')
    if str(profile['instrument_id'])!=str(market.instrument_id):
        raise ValueError('prior RTH profile has foreign instrument')
    if profile['known_at']>clock(market.day,'09:30'):
        raise ValueError('prior RTH profile is late')
    if (profile['formation_start'],profile['formation_end'],profile['as_of'])!=(start,end,end):
        raise ValueError('prior RTH profile formation differs from frozen session')
    if profile['kind']!='prior_rth' or profile['session_date']!=str(prior_day):
        raise ValueError('prior RTH profile has foreign kind/session')
    if profile['known_at']<profile['formation_end']:
        raise ValueError('prior RTH profile availability precedes formation')
    if require_value_area:
        parameters=rule['parameters']
        expected_fraction=Decimal(str(parameters['value_fraction']))
        expected_algorithm=parameters['va_expansion']
        expected_poc='lowest' if parameters['poc_tie']=='lowest_price' else parameters['poc_tie']
        if (Decimal(str(profile.get('value_area_fraction'))) != expected_fraction
                or profile.get('value_area_algorithm') != expected_algorithm
                or profile.get('value_area_tie_policy') != 'both'
                or profile.get('poc_tie_policy') != expected_poc):
            raise ValueError('prior value-area profile configuration differs from frozen VA70 rule')
        if profile.get('val') is None or profile.get('vah') is None:
            return None
    elif profile.get('poc') is None:
        return None
    return profile


def _range_path(rule,market,registry,reference,start,end):
    if not reference['complete']:return _rows([],['reference_incomplete'],[reference])
    eq=(reference['high']+reference['low'])/2
    reference=dict(reference,midpoint=eq)
    bars=market.bars(start,end)
    opportunity=None
    for bar in bars:
        if not _bar_ok(bar,market.instrument_id):return _rows([],['missing_initial_opportunity_interval'],[reference])
        if bar['L']<=eq<=bar['H']:
            side='long' if bar['C']>=eq else 'short'
            opportunity=make_opportunity(rule,market.partition,reference,bar,side,registry['registry_sha256'],end)
            break
    if opportunity is None:return _rows([],[],[reference])
    for bar,at in _full_later(opportunity,bars):
        if bar is None:return _rows([(opportunity,_unknown(opportunity,at,'missing_range_path_interval'))],[],[reference])
        upper,lower=bar['H']>=reference['high'],bar['L']<=reference['low']
        if upper and lower:return _rows([(opportunity,_unknown(opportunity,at,'both_range_edges_in_one_bar',ambiguous=True))],[],[reference])
        if upper or lower:
            passed=upper if opportunity.side=='long' else lower
            return _rows([(opportunity,_endpoint(opportunity,bar,passed,'chosen_edge_first' if passed else 'opposite_edge_first'))],[],[reference])
    return _rows([(opportunity,ReplayResult(opportunity.opportunity_id,'fail',end,None,'no_range_edge_before_expiry').validate(opportunity))],[],[reference])


def _mss(rule,market,registry):
    parent_rule=next(r for r in registry['rules'] if r['method_id']=='GB-FAIL' and r['branch']=='nyam_box')
    parent_run=run_bar_rule(parent_rule,market,registry)
    out=[]
    for parent,replay in parent_run['records']:
        if replay.verdict!='pass':continue
        bar=replay.endpoint
        expiry=min(replay.completed_at+30*MINUTE,market.end)
        ref=dict(parent.reference,reference_id=parent.opportunity_id+':completed-reclaim',
                 known_at=replay.completed_at,parent_opportunity_id=parent.opportunity_id,
                 parent_completion_at=replay.completed_at,initial_event_kind='completion')
        child=make_opportunity(rule,market.partition,ref,bar,parent.side,registry['registry_sha256'],expiry)
        duration=2*MINUTE
        start=((replay.completed_at+duration-1)//duration)*duration
        end=(expiry//duration)*duration
        candles=market.bars(start,end,2) if start<end else []
        result=None
        for i,c in enumerate(candles):
            if not _bar_ok(c,market.instrument_id):
                result=_unknown(child,max(child.available_at,c['start']),'missing_refinement_candle');break
            if i<2:continue
            a,b=candles[i-2:i]
            if parent.side=='long':passed=c['L']>a['H'] and c['C']>max(a['H'],b['H'])
            else:passed=c['H']<a['L'] and c['C']<min(a['L'],b['L'])
            if passed:result=_endpoint(child,c,True,'observed_post_reclaim_wick_gap_and_two_bar_break');break
        if result is None:
            result=ReplayResult(child.opportunity_id,'fail',expiry,None,'no_refinement_on_complete_declared_candle_grid').validate(child)
        out.append((child,result))
    return _rows(out,parent_run['population_holes'],parent_run['references'])


def _vwap_continuation(rule,market,registry):
    day=market.day
    asia=market.range_reference(rule,clock(day-timedelta(days=1),'20:00'),clock(day,'00:00'),label='asia')
    london=market.range_reference(rule,clock(day,'02:00'),clock(day,'05:00'),label='london')
    ref={'reference_id':f'{rule["rule_id"]}:{market.instrument_id}:{day}:asia-london',
         'instrument_id':market.instrument_id,'known_at':max(asia['known_at'],london['known_at']),
         'complete':asia['complete'] and london['complete'], 'asia_high':asia['high'],'london_high':london['high'],
         'high':None if not (asia['complete'] and london['complete']) else max(asia['high'],london['high']),
         'low':None if not (asia['complete'] and london['complete']) else min(asia['low'],london['low']),
         'object_ids':asia['object_ids']+london['object_ids'],
         'constituent_reference_ids':[asia['reference_id'],london['reference_id']]}
    start=clock(day,'05:00')
    opportunities,holes=_detect(rule,market,registry,ref,start,market.end,trigger='close_above_both',sides=('long',))
    def boundary(at):
        value=market.vwap(rule,at)
        return None if value is None else (value['price'],value['known_at'])
    bars=market.bars(start,market.end)
    return _rows([(o,later_touch(o,bars,boundary)) for o in opportunities],holes,[asia,london,ref])


def _band_fade(rule,market,registry):
    start=clock(market.day,'09:30');end=market.end
    bars=market.bars(start,end,5);seen=set();out=[];holes=[];refs=[]
    for bar in bars:
        if not _bar_ok(bar,market.instrument_id):holes.append('missing_initial_opportunity_interval');break
        vw=market.vwap(rule,bar['start'])
        if vw is None or vw['variance'] is None:holes.append('vwap_prefix_incomplete');break
        sd=vw['variance'].sqrt();upper=vw['price']+sd;lower=vw['price']-sd
        touches={side:bar['L']<=level<=bar['H'] for side,level in [('short',upper),('long',lower)]}
        for side in ('short','long'):
            if side in seen or not touches[side]:continue
            ref={'reference_id':f'{rule["rule_id"]}:{market.instrument_id}:{bar["start"]}:{side}',
                 'instrument_id':market.instrument_id,'known_at':bar['start'],'complete':True,
                 'high':upper,'low':lower,'vwap':vw['price'],'sigma':sd,'object_ids':[vw['object_id']],
                 'snapshot_at':bar['start'],'band_side':side}
            expiry=min(end,bar['end']+15*MINUTE)
            o=make_opportunity(rule,market.partition,ref,bar,side,registry['registry_sha256'],expiry)
            if all(touches.values()):r=_unknown(o,o.available_at,'both_deviation_bands_in_trigger_bar',ambiguous=True)
            else:r=next_aligned_close(o,market.bars(start,end),minutes=5)
            out.append((o,r));refs.append(ref);seen.add(side)
        if len(seen)==2:break
    return _rows(out,holes,refs)


def _continuation(rule,market,registry,reference):
    start=clock(market.day,'09:30');end=market.end
    opportunities,holes=_detect(rule,market,registry,reference,start,end,trigger='close_outside',minutes=5,sides=('long','short'))
    bars=market.bars(start,end,5);out=[]
    for o in opportunities:
        o=replace(o,expiry_at=min(end,o.available_at+60*MINUTE)).validate()
        boundary=reference['high'] if o.side=='long' else reference['low']
        out.append((o,later_touch(o,bars,lambda at:(boundary,reference['known_at']),require_close_side=True)))
    return _rows(out,holes,[reference])


def run_bar_rule(rule,market,registry,*,tape=None,prior_profile=None):
    """Return typed opportunity/replay pairs; no records are source trades."""
    method,branch=rule['method_id'],rule['branch']
    day=market.day;end=market.end
    if method=='JJ-TBR':
        ref=market.range_reference(rule,clock(day,'06:00'),clock(day,'09:00'),recipe='O005',label='06-09')
        if branch=='internal_rotation':return _range_path(rule,market,registry,ref,clock(day,'09:30'),end)
        if branch=='extension_reaction':
            if ref['complete']:
                width=ref['high']-ref['low']
                ref=dict(ref,width=width,upper_band=[ref['high']+Decimal('1.33')*width,ref['high']+Decimal('1.66')*width],
                         lower_band=[ref['low']-Decimal('1.66')*width,ref['low']-Decimal('1.33')*width])
                if width<=0:ref['complete']=False
            start=clock(day,'09:00');trigger='extension_band';endpoint='extension_rejection'
        else:start=clock(day,'09:40');end=clock(day,'09:50');trigger='strict_sweep';endpoint='reclaim'
        opportunities,holes=_detect(rule,market,registry,ref,start,end,trigger=trigger)
        # Endpoint grid can begin before the action interval; native members
        # are collected from the full frozen context, not five available rows.
        bars=market.bars(clock(day,'09:00'),market.end)
        return _rows([(o,next_aligned_close(o,bars,minutes=3,endpoint=endpoint)) for o in opportunities],holes,[ref])
    if method=='GB-FAIL':
        if branch=='mss_fvg_refinement':return _mss(rule,market,registry)
        refs=[];windows=[]
        if branch=='nyam_box':
            ref=market.range_reference(rule,clock(day,'09:00'),clock(day,'10:00'),label='nyam',require_inside=True)
            windows=[(ref,clock(day,'10:00'),end,('short','long'))]
        elif branch=='previous_hour':
            for hour in range(9,16):
                ref=market.range_reference(rule,clock(day,f'{hour-1:02d}:00'),clock(day,f'{hour:02d}:00'),label=f'hour-{hour-1}',require_inside=True)
                windows.append((ref,max(clock(day,'09:30'),clock(day,f'{hour:02d}:00')),clock(day,f'{hour+1:02d}:00'),('short','long')))
        elif branch in {'prior_day_level','prior_week_level','prior_month_level'}:
            kind=branch.split('_')[1];ref=market.prior_reference(rule,kind)
            windows=[(ref,clock(day,'09:30'),end,('short','long'))]
        elif branch=='cash_open_reclaim_case':
            ref=market.minute_open_reference(rule,clock(day,'09:30'),'cash-minute-open')
            windows=[(ref,clock(day,'09:31'),clock(day,'10:30'),('long',))]
        elif branch=='asia_tdo_case':
            ref=market.range_reference(rule,clock(day-timedelta(days=1),'20:00'),clock(day,'00:00'),label='asia',require_inside=True)
            tdo=market.minute_open_reference(rule,clock(day,'00:00'),'midnight-minute-open')
            ref=dict(ref,tdo=tdo['high'],known_at=tdo['known_at'],complete=ref['complete'] and tdo['complete'],
                     object_ids=ref['object_ids']+tdo['object_ids'])
            windows=[(ref,clock(day,'00:01'),end,('short','long'))]
        else:raise ValueError('unimplemented supported GB branch')
        records=[];holes=[]
        allbars=market.bars(clock(day,'00:00'),end)
        for ref,start,expiry,sides in windows:
            opportunities,missing=_detect(rule,market,registry,ref,start,expiry,sides=sides)
            holes.extend(missing);refs.append(ref)
            for o in opportunities:
                extra=(lambda close,reference,side:close<reference['tdo'] if side=='short' else close>reference['tdo']) if branch=='asia_tdo_case' else None
                result=next_aligned_close(o,allbars,minutes=5,extra_condition=extra)
                records.append((o,result))
        return _rows(records,holes,refs)
    if method=='GB-VWAP':return _vwap_continuation(rule,market,registry)
    if method=='SIRES':return _band_fade(rule,market,registry)
    if method=='SAINT-AMT' and branch=='continuation_retest':return _continuation(rule,market,registry,market.prior_reference(rule))
    if method=='SAINT-AMT':return _saint_tape(rule,market,registry,tape,prior_profile)
    if method=='KEANI-OPEN-ABOVE-VALUE':return _opening_state(rule,market,registry,prior_profile)
    raise ValueError(f'no supported bar rule implementation: {method}/{branch}')


def _saint_tape(rule,market,registry,tape,prior_profile):
    branch=rule['branch'];start=clock(market.day,'09:30');end=market.end
    reference=market.prior_reference(rule)
    if not reference['complete']:return _rows([],['prior_RTH_bar_reference_incomplete'],[reference])
    profile={}
    if branch!='trapped_buyers_retest':
        profile=_verified_prior_rth_profile(rule,market,prior_profile)
        if profile is None:
            return _rows([],['prior_RTH_trade_profile_unverified'],[reference])
        reference=dict(reference,poc=profile['poc'],profile_id=profile['profile_id'],
                       profile_known_at=profile['known_at'],profile_snapshot_id=profile['snapshot_id'])
    bars=market.bars(start,end,5);out=[];holes=[];seen=set();previous=None;streak={'long':0,'short':0}
    minute_rows={r['minute_start']:r for r in (tape or {}).get('minutes',[])}
    reconciled={r['minute_start']:r for r in (tape or {}).get('coverage',{}).get('reconciliation',[])}
    def delta(bar):
        observations=[minute_rows.get(t) for t in range(bar['start'],bar['end'],MINUTE)]
        checks=[reconciled.get(t) for t in range(bar['start'],bar['end'],MINUTE)]
        if any(r is None or r.get('delta') is None for r in observations) or any(r is None or r.get('matched') is not True for r in checks):
            return None
        if any(r['known_at']>bar['end'] for r in observations):raise ValueError('executed delta unavailable at bar close')
        return sum((r['delta'] for r in observations),Decimal(0))
    for bar in bars:
        if not _bar_ok(bar,market.instrument_id):holes.append('missing_initial_opportunity_interval');break
        selected=[]
        if branch=='trapped_buyers_retest':
            d=delta(bar)
            if d is None:holes.append('initial_delta_coverage_unknown');break
            if 'short' not in seen and bar['H']>reference['high'] and bar['C']<reference['high'] and d>0:selected=['short']
        elif branch=='failed_auction_return':
            for side in ('long','short'):
                outside=bar['C']>reference['high'] if side=='long' else bar['C']<reference['low']
                streak[side]=streak[side]+1 if outside else 0
                if side not in seen and streak[side]==2:selected.append(side)
        elif branch=='poc_traversal':
            if previous is not None and reference['low']<bar['C']<reference['high']:
                if previous['C']<reference['poc']<bar['C'] and 'long' not in seen:selected.append('long')
                if previous['C']>reference['poc']>bar['C'] and 'short' not in seen:selected.append('short')
        else:raise ValueError('unsupported Saint tape branch')
        for side in selected:
            expiry=min(end,bar['end']+60*MINUTE) if branch=='trapped_buyers_retest' else end
            o=make_opportunity(rule,market.partition,reference,bar,side,registry['registry_sha256'],expiry)
            if branch=='trapped_buyers_retest':
                result=None
                for later,at in _full_later(o,bars):
                    if later is None:result=_unknown(o,at,'missing_trap_retest_interval');break
                    if later['L']<=reference['high']<=later['H']:
                        flow=delta(later)
                        result=_unknown(o,at,'retest_delta_unverified') if flow is None else _endpoint(o,later,later['C']<reference['high'] and flow<0,'first_high_retest_close_and_delta')
                        break
                if result is None:result=ReplayResult(o.opportunity_id,'fail',expiry,None,'no_high_retest_before_expiry').validate(o)
            elif branch=='failed_auction_return':
                inside_at=None;result=None
                for later,at in _full_later(o,bars):
                    if later is None:result=_unknown(o,at,'missing_boundary_return_path');break
                    if inside_at is None:
                        if reference['low']<later['C']<reference['high']:inside_at=at
                        # POC touched in the same return bar is not a later
                        # POC event; its unobserved intrabar order is excluded.
                        continue
                    if later['L']<=reference['poc']<=later['H']:
                        result=_endpoint(o,later,True,'prior_boundary_return_then_later_POC_contact');break
                if result is None:result=ReplayResult(o.opportunity_id,'fail',expiry,None,'no_ordered_boundary_return_and_POC_contact').validate(o)
            else:
                destination=origin=0;result=None
                for later,at in _full_later(o,bars):
                    if later is None:result=_unknown(o,at,'missing_POC_hold_interval');break
                    c=later['C'];poc=reference['poc']
                    if c==poc:destination=origin=0
                    elif (c>poc)==(side=='long'):destination+=1;origin=0
                    else:origin+=1;destination=0
                    if destination==2 or origin==2:
                        result=_endpoint(o,later,destination==2,'two_destination_closes' if destination==2 else 'two_origin_closes');break
                if result is None:result=_unknown(o,expiry,'no_resolved_two_close_streak_before_expiry',ambiguous=True)
            out.append((o,result));seen.add(side)
        previous=bar
        if len(seen)==(1 if branch=='trapped_buyers_retest' else 2):break
    return _rows(out,holes,[reference])


def _opening_state(rule,market,registry,prior_profile):
    start=clock(market.day,'09:30');end=clock(market.day,'10:00')
    first=market.bars(start,start+MINUTE)[0]
    if not _bar_ok(first,market.instrument_id):return _rows([],['session_opening_minute_unavailable'])
    supplied=(prior_profile or {}).get('profile',{})
    profile=_verified_prior_rth_profile(rule,market,prior_profile,require_value_area=True)
    complete=profile is not None
    # Session openings, not above-value openings, define the population. The
    # clock-only reference remains identifiable even with absent prior value.
    reference={'reference_id':f'{rule["rule_id"]}:{market.instrument_id}:{market.day}:opening-clock',
               'instrument_id':market.instrument_id,'known_at':start,'complete':True,
               'high':profile.get('vah') if complete else None,'low':profile.get('val') if complete else None,
               'object_ids':[],'profile_id':profile.get('profile_id') if complete else supplied.get('profile_id'),'prior_value_verified':complete,
               'prior_value_known_at':profile.get('known_at') if complete else None,
               'reference_definition':'Clock-based opening population; unverified prior values are not incorporated.'}
    o=make_opportunity(rule,market.partition,reference,first,'long',registry['registry_sha256'],end)
    if not complete:return _rows([(o,_unknown(o,end,'prior_value_profile_unverified'))],[],[reference])
    bars=market.bars(start,end)
    if any(not _bar_ok(b,market.instrument_id) for b in bars):return _rows([(o,_unknown(o,end,'opening_A_membership_incomplete'))],[],[reference])
    obj,result=market.object(rule['method_id'],rule['branch'],'O004',start,end,
                            {'kind':'time','size_minutes':30},label='completed-A')
    if result.coverage_ok is not True:return _rows([(o,_unknown(o,end,'opening_A_membership_incomplete'))],[],[reference])
    passed=result.value['L']>profile['vah']
    return _rows([(o,_endpoint(o,result.value,passed,'complete_A_low_above_prior_VAH' if passed else 'complete_A_low_not_above_prior_VAH'))],[],[reference])
