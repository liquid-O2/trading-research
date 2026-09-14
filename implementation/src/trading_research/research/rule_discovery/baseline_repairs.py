"""Versioned B0.1 repairs for accepted Phase 1 baseline defects.

Accepted method_pack scanners stay frozen. Each corrected function is a copy of
the frozen body with the minimal change; unchanged helpers are imported from
the frozen module.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal as D

from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.event_time import BookObservations
from trading_research.research.method_pack.historical_assembly import HistoricalEpisode, window_result, close_selection_omissions
from trading_research.research.method_pack.historical_features import Q, MINUTE, SECOND, sign, balances, distinct_contacts, first_contact, pivots
from trading_research.research.method_pack.historical_flow import (
    batches,
    exact_contact,
    flow_stages,
    _catalyst_stages,
    _timestamp,
    _seen,
    _base,
    scan_microbalance,
)
from trading_research.research.method_pack.historical_price_scanners import _known, _context, _gb_refs
from trading_research.research.method_pack.historical_auction_scanners import primary_balance, _control, _upper_failures
from trading_research.research.method_pack.branch_coverage import setting
from trading_research.research.method_pack.native_discovery import scan_branch as native_scan_branch

BASELINE_REPAIR_VERSION = "B0.1-2026-09-14"
B0_VERSION = "B0"

SIRES_LOCAL_BRANCHES = (
    "dom_rejection", "absorption_reward_retest", "stop_four_stage",
    "footprint_confirmed_reaction", "vwap_deviation_fade", "ofm_aggressive",
    "ofm_passive", "clean_squeeze", "balance_failure_fade",
    "defended_band_continuation", "kg1_retest",
)
GB_FAIL_BRANCHES = (
    "nyam_box", "previous_hour", "asia_tdo_case", "prior_day_level",
    "prior_week_level", "prior_month_level", "cash_open_reclaim_case", "mss_fvg_refinement",
)
SAINT_BRANCHES = ("continuation_retest", "trapped_buyers_retest", "failed_auction_return", "poc_traversal")
MEMBER_BRANCHES = ("resistance_short", "planned_return_long")
JJ_TBR_ABSENT_BRANCHES = (
    "judas_reversal", "single_extended", "single_purged", "internal_rotation",
    "extension_reaction", "other_session", "timed_pzone_reversal",
)


def _cid(method, branch):
    return f"{method}:branch:{branch}"


REPAIRS = {
    "D1": {
        "branch_ids": (_cid("GB-VWAP", "source_long"),),
        "frozen_symbol": "trading_research.research.method_pack.historical_price_scanners.scan_green_vwap",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.scan_green_vwap_repaired",
        "fixture": "repro_d1.py",
    },
    "P4": {
        "branch_ids": tuple(_cid("GB-FAIL", b) for b in GB_FAIL_BRANCHES),
        "frozen_symbol": "trading_research.research.method_pack.historical_price_scanners.scan_green_failure",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.scan_green_failure_repaired",
        "fixture": "f4_green_failure_empty_path.py",
    },
    "P1": {
        "branch_ids": tuple(_cid("SIRES", b) for b in SIRES_LOCAL_BRANCHES)
        + tuple(_cid("MEMBER-TWO-REASONS", b) for b in MEMBER_BRANCHES)
        + (_cid("KEANI-OPEN-ABOVE-VALUE", "source_long"),),
        "frozen_symbol": "trading_research.research.method_pack.historical_flow.local_observations",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.local_observations_repaired",
        "fixture": "f7_previous_chunk_skips_empty.py",
    },
    "P6": {
        "branch_ids": (_cid("SIRES", "kg1_retest"),),
        "frozen_symbol": "trading_research.research.method_pack.historical_flow.scan_sires",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.scan_sires_repaired",
        "fixture": "f3_kg1_reference_collapse.py",
    },
    "P2": {
        "branch_ids": tuple(_cid("SAINT-AMT", b) for b in SAINT_BRANCHES)
        + tuple(_cid("MEMBER-TWO-REASONS", b) for b in MEMBER_BRANCHES)
        + (_cid("KEANI-OPEN-ABOVE-VALUE", "source_long"), _cid("GB-VWAP", "source_long"))
        + tuple(_cid("JJ-TBR", b) for b in JJ_TBR_ABSENT_BRANCHES),
        "frozen_symbol": "trading_research.research.method_pack.historical_assembly.absent",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.absent_repaired",
        "fixture": "f2_absent_empty_interval.py",
        "fixtures": ("f2_absent_empty_interval.py", "repro_p2_saint.py"),
    },
}


def affected_branch_ids():
    seen = []
    for item in REPAIRS.values():
        for cid in item["branch_ids"]:
            if cid not in seen:
                seen.append(cid)
    return tuple(seen)


def absent_repaired(market, start, end, *, fields=(), seconds=60):
    """P2: event_time.py:298 consumed by historical_assembly.py:91-94.

    Frozen absent() returns False when coverage of a zero-length interval is
    certified complete (`range` over an empty minute walk). Change: return None
    for a zero-length or unobservable interval so unknown stays unknown.
    """
    if end <= start:
        return None
    if fields and any(row.get(field) is None for row in market.bars(start, end, seconds) for field in fields):
        return None
    return False if market.coverage(start, end)["observed_scope_complete"] else None


def _reference_identity(ref):
    """P6 helper: reference id, else a hash of bounds and kind."""
    ident = ref.get("id")
    if ident is not None:
        return ident
    return content_hash({"low": ref.get("low"), "high": ref.get("high"), "kind": ref.get("kind")})

def local_observations_repaired(m,touch,band,side,*,horizon=None,book=True):
    """P1: historical_flow.py:63-64. Frozen local_observations skips empty 5-second windows (`if not rows: continue`) so the effort baseline is the previous non-empty chunk. Change: record an empty window as a chunk with opposing=0 and compare each window with the immediately preceding equal-duration window."""
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
        if not rows:
            passive='bid' if side=='long' else 'ask'
            completed=[r for r in bookrows if a<=r['event_ns']<b and r['known_at']<=b and not r['bad_book'] and not r['reset']]
            displayed=[r for r in completed if r[passive] is not None and lo<=r[passive]<=hi]
            added=[r for r in displayed if (r.get(passive+'_added') or 0)>0]
            previous=chunks[-1] if chunks else None
            effort=None if (previous and previous['unknown']) else False
            chunks.append({'id':f'flow:{m.instrument_id}:{a}:{b}:{lo}:{hi}:{side}','start':a,'end':b,
                'known_at':b,'low':hi+Q,'high':lo-Q,'first':None,'last':None,
                'price_basis':'unique price at timestamp endpoint','entry_px':None,
                'own':0,'opposing':0,'unknown':0,'delta':0,
                'opponent_mean':D(0),'count':0,'opponent_count':0,'nearby_count':0,
                'effort':effort,'no_progress':None,'held':None,
                'displayed_defense':bool(displayed) if completed else None,
                'added_at':added[0]['event_ns'] if added else None,
                'added_size':sum(r[passive+'_added'] for r in added),'book_observed':bool(completed),
                'event_ids':[],'events':[],'book_ids':[r['event_ns'] for r in displayed],
                'book_changes':added,'origin':origin,'empty_window':True})
            continue
        grouped=batches(rows);firstprices={r['price'] for r in grouped[0][1]};lastprices={r['price'] for r in grouped[-1][1]}
        first=next(iter(firstprices)) if len(firstprices)==1 else None
        last=next(iter(lastprices)) if len(lastprices)==1 else None
        price_basis='unique price at timestamp endpoint'
        if getattr(m,'reconstruct',False):
            from trading_research.research.method_pack.strategy_measurements import batch_price
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

def flow_absent_repaired(m,start,end,chunks):
    """P2: historical_flow.py:115-117 via historical_assembly.absent. Change: call absent_repaired so a zero-length or unobservable interval stays unknown."""
    if any(r['first'] is None or r['last'] is None or r['unknown']>0 for r in chunks):return None
    return absent_repaired(m,start,end)

def _flow_episode_repaired(m,branch,ref,trigger,side,band,*,vwap=None):
    """P1: historical_flow.py:140. Frozen _flow_episode calls local_observations. Change: call local_observations_repaired and flow_absent_repaired."""
    contact=exact_contact(m,trigger,*band)
    if not contact:return None
    obs=local_observations_repaired(m,contact['at'],band,side);st=flow_stages(obs);cat=_catalyst_stages(obs,st)
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
    missing=flow_absent_repaired(m,trigger['start'],min(m.end,((decision+MINUTE-1)//MINUTE)*MINUTE),chunks)
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
        from trading_research.research.method_pack.strategy_options import gamma_at
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

def scan_sires_repaired(m,branch):
    """P6: historical_flow.py:306. Frozen per-side dedup keys on the pivot-id tuple, so pivot-less KG1 references collapse. Change: key on the reference's own identifier (id, else a hash of bounds and kind) plus side. P1: dispatch through _flow_episode_repaired."""
    episodes=[];omissions=[]
    allbars=m.bars(m.start,m.end,300);auction=balances(allbars)
    if branch=='microbalance_break':return scan_microbalance(m,branch,auction)
    if branch=='kg1_retest':
        refs=[{**r,'external_record':True,'low':D(str(r['low'])),'high':D(str(r['high']))} for r in m.supplied('kg1',m.end)]
        if not refs and getattr(m,'reconstruct',False):
            from trading_research.research.method_pack.strategy_options import key_gamma_reference
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
                    seen.add(side);result=_flow_episode_repaired(m,branch,ref,row,side,[px-Q,px+Q],vwap=vw)
                    if result:episodes.append(result)
    else:
        used=set()
        for ref in refs:
            start=max(ref['known_at'],m.at('09:30'))
            if start>=m.end:continue
            for side in (('long',) if branch=='ofm_passive' else ('long','short')):
                key=_reference_identity(ref),side
                if key in used:continue
                edge=ref['low'] if side=='long' else ref['high'];band=[ref['low'],ref['high']] if branch=='kg1_retest' else [edge-Q,edge+Q]
                contacts=list(distinct_contacts(m.bars(start,m.end),*band))
                if not contacts:continue
                trigger=contacts[0]
                if branch=='defended_band_continuation':
                    if len(contacts)<2:continue
                    prior=_flow_episode_repaired(m,'dom_rejection',ref,contacts[0],side,band)
                    if prior is None:continue
                    prior_defense=next((r for r in prior['stages'] if r['stage']=='defense' and r['observed'] is True),None)
                    if not prior_defense:continue
                    ref={**ref,'prior_defense_at':prior_defense['at']};trigger=contacts[1]
                used.add(key)
                result=_flow_episode_repaired(m,branch,ref,trigger,side,band)
                if result:episodes.append(result)
    if not auction and branch!='kg1_retest':omissions.append({'reason':'no confirmed alternating-pivot auction in observed prefix','kind':'measured_selection'})
    return window_result(m,'SIRES',branch,episodes,omissions=omissions)

def _ob_repaired(m,touch,side,end):
    """P2: historical_price_scanners.py:40. Frozen _ob certifies confirmation absence via absent(). Change: call absent_repaired so a zero-length window is unknown."""
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
    return (None if ambiguous else absent_repaired(m,touch['start'],end)),None,None,None

def scan_jumbo_repaired(m,branch):
    """P2: historical_price_scanners.py:40,171. Frozen scan_jumbo calls absent() from _ob and from the extension_reaction prior_expansion conjunct. Change: use _ob_repaired and absent_repaired."""
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
        from trading_research.research.method_pack.strategy_pzones import inferred_pzones
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
                ok,confirm,stop,ob=_ob_repaired(m,trigger,side,deadline)
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
                e.bind({'prior_expansion':expansion or absent_repaired(m,end,touch) if touch>end else False,
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

def scan_green_failure_repaired(m,branch):
    """P4: historical_price_scanners.py:224-225. Frozen scan_green_failure raises ValueError on max()/min() of an empty sweep path. Change: record an availability omission and emit the episode as input-unknown."""
    method='GB-FAIL';episodes=[]
    if branch=='mss_fvg_refinement':return scan_green_refinement_repaired(m,branch)
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
            if not path:
                omissions.append({'kind':'availability','reason':'sweep path empty: no bars known at or before confirmation_end','window':[trigger['start'],confirmation_end],'side':side,'reference_id':ref.get('id')})
                high=low=stop=None
                target=None if branch=='cash_open_reclaim_case' else (ref['low'] if side=='short' else ref['high'])
            else:
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
                'pocket_required':False,'retracement_entry':False,'risk_defined':None if close is None or stop is None else sg*(close-stop)>0,
                'objective_fixed':None if close is None or target is None else sg*(target-close)>0},
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

def scan_green_refinement_repaired(m,branch):
    """P4: historical_price_scanners.py:257. Frozen scan_green_refinement calls scan_green_failure as parent. Change: call scan_green_failure_repaired."""
    parent=scan_green_failure_repaired(m,'nyam_box');episodes=[]
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

def scan_green_vwap_repaired(m,branch):
    """D1: historical_price_scanners.py:314. Frozen scan_green_vwap rebinds continuation_context with the retest-absence answer, overwriting the breakout-context conjunct from line 308. Change: keep continuation_context as the breakout comparison and record the retest conjunct on retest_at/retest_low/retest_high. P2: the later_VWAP_return stage uses absent_repaired."""
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
    if retest is None:e.bind({'retest_at':None,'retest_low':None,'retest_high':None},operation='no later VWAP retest in declared observed horizon')
    e.stage('above_both_highs',breakout['end'],observed=True).stage('later_VWAP_return',retest_at,
        observed=True if retest else absent_repaired(m,breakout['end'],deadline),details=vw)
    return window_result(m,'GB-VWAP',branch,[e.finish(decision_at=decision,entry=entry,stop=stop)],omissions=omissions)

def _control_absence_repaired(m,after,end,side):
    """P2: historical_auction_scanners.py:28. Frozen _control_absence returns False when end<=after. Change: return None for a zero-length window and call absent_repaired for coverage."""
    if not getattr(m,'reconstruct',False):
        return absent_repaired(m,after,end,fields=('O','C','delta'))
    if end<=after:return None
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
    return None if uncertain else absent_repaired(m,after,end)

def _saint_base_repaired(e,m,ref,arrival,control,decision,side,entry,stop,target,*,control_start=None):
    """P2: historical_auction_scanners.py:50. Frozen _saint_base calls _control_absence. Change: call _control_absence_repaired."""
    profile=m.profile(ref['start'],ref['known_at'],'.68')
    permission=None if profile['poc'] is None else ref['low']<=profile['poc']<=ref['high']
    e.bind({'balance_fixed_before_use':ref['known_at']<=arrival,'balance_known_at':ref['known_at'],
        'profile_allows_trade':permission,'arrival_read_recorded':True,'arrival_at':arrival,
        'control_evidence_recorded':True if control else _control_absence_repaired(m,arrival//MINUTE*MINUTE if control_start is None else control_start,decision,side),
        'control_at':control['known_at'] if control else None,'alignment_ok':True if control else None,
        'risk_defined':None if entry is None else sign(side)*(entry-stop)>0,
        'objective_fixed':None if entry is None else sign(side)*(target-entry)>0},
        operation='distinct HTF price balance with 68% profile and current repeated directional body/delta control',
        parents=[ref['id'],profile['id']],known_at=decision,assumption='A2-BALANCE/A2-STRUCTURAL-RISK')
    e.geometry['htf_profile']=profile

def scan_saint_repaired(m,branch):
    """P2: historical_auction_scanners.py:98,108,109,158,161,162,168. Frozen scan_saint calls absent() and _control_absence, certifying absence from a zero-length window as False. Change: call absent_repaired and _control_absence_repaired."""
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
            _saint_base_repaired(e,m,ref,trigger['start'],control,decision,side,entry,stop,target,
                control_start=control_start if getattr(m,'reconstruct',False) else None)
            held=None if not retest or not control else all(r['L']>=boundary-Q*2 if side=='long' else r['H']<=boundary+Q*2 for r in m.bars(retest['start'],control['end']))
            e.bind({'same_boundary_retest_held':held if retest else absent_repaired(m,trigger['end'],end),
                'breakout_at':trigger['known_at'],'retest_at':touch['at'] if touch else None,
                'confirm_at':control['known_at'] if control else None},operation='actual LTF boundary break, later same-boundary return and current repeated body/delta control',
                parents=[ltf['id'],trigger['bar_id']],known_at=decision,assumption='A2-BALANCE')
            if branch=='continuation_retest':
                e.bind({'ltf_balance_broken':True,'ltf_balance_known_at':ltf['known_at'],
                    'repeated_aggression_in_trade_direction':True if control else _control_absence_repaired(m,control_start if getattr(m,'reconstruct',False) else trigger['end'],end,side)},
                    operation='distinct confirmed LTF structure and two successive native directional bodies',parents=[ltf['id']],assumption='A2-FLOW')
            else:
                failures=_upper_failures(m,ref,trigger['start'])
                e.bind({'prior_buying_at_upper_extreme':True if failures else absent_repaired(m,ref['known_at'],trigger['start'],fields=('C','delta')),
                    'two_distinct_prior_failures':True if len(failures)>=2 else absent_repaired(m,ref['known_at'],trigger['start'],fields=('C','delta')),
                    'prior_failures_known_at':failures[-1]['known_at'] if failures else None,'ltf_break_down':trigger['C']<ltf['low'],
                    'repeated_body_selling':True if control else _control_absence_repaired(m,control_start if getattr(m,'reconstruct',False) else trigger['end'],end,side)},
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
            from trading_research.research.method_pack.historical_features import HistoricalFeatures
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
            _saint_base_repaired(e,m,ref,trigger['start'],control,decision,side,entry,stop,target,
                control_start=control_start if getattr(m,'reconstruct',False) else None)
            e.bind({'original_balance_reaccepted':True if reaccept else absent_repaired(m,trigger['end'],end,fields=('C',)),
                'reaccept_at':reaccept['known_at'] if reaccept else None},operation='outside original auction, followed by a later completed inside close',parents=[ref['id'],trigger['bar_id']],known_at=decision)
            if branch=='failed_auction_return':
                e.bind({'older_value_tested':True if oldtouch else None if old is None else absent_repaired(m,trigger['start'],end),
                    'older_value_rejected':True if rejection else None if old is None else absent_repaired(m,trigger['start'],end,fields=('C',)),
                    'older_value_known_at':old['known_at'] if old else None,'older_value_touch_at':oldtouch['start'] if oldtouch else None,
                    'rejection_at':rejection['known_at'] if rejection else None,'local_control_confirms_return':True if control else _control_absence_repaired(m,control_start if getattr(m,'reconstruct',False) else trigger['end'],end,side)},
                    operation='distinct older value exploration/rejection precedes original balance reacceptance and local control',parents=[old['id']] if old else [],known_at=decision,assumption='A2-BALANCE')
            else:
                held=None if not passage or not control else all(sg*(r['C']-poc)>=0 for r in controlbars)
                e.bind({'aggressive_poc_passage':True if passage else None if poc is None else absent_repaired(m,trigger['end'],end,fields=('C','delta')),
                    'source_poc_hold_confirmed':held,'target_is_far_balance_edge':target in (ref['low'],ref['high']),
                    'poc_passage_at':passage['known_at'] if passage else None},operation='aggressive original POC passage after reacceptance; two subsequent same-side body/delta closes hold',parents=[profile['id']],known_at=decision,assumption='A2-FLOW')
            e.geometry.update(older_balance=old,older_profile=oldprofile)
            if getattr(m,'reconstruct',False):
                e.geometry.update(control_bars=controlbars,control_search_window=[control_start,decision])
            for name,row in [('exploration',trigger),('older_touch',oldtouch),('older_rejection',rejection),('reacceptance',reaccept),('poc_passage',passage),('control',control)]:
                e.stage(name,row['known_at'] if row else None,observed=True if row else None)
            episodes.append(e.finish(decision_at=decision,entry=entry,stop=stop,target=target))
    return window_result(m,'SAINT-AMT',branch,episodes,omissions=omissions)

def scan_member_repaired(m,branch):
    """P1: historical_auction_scanners.py:219. Frozen scan_member calls local_observations. P2: flow_absent uses absent(). Change: call local_observations_repaired and flow_absent_repaired."""
    prior=m.prior('day');episodes=[];omissions=list(prior['omissions'])
    if not prior['sessions']:return window_result(m,'MEMBER-TWO-REASONS',branch,[],omissions=omissions)
    day=prior['sessions'][-1];win=day['window'];from trading_research.research.method_pack.empirical_market import clock
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
    obs=local_observations_repaired(m,contact['at'],[lo,hi],side);stages=flow_stages(obs);defense=stages['defense']
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
    if side=='short':e.bind({'resistance_rejection':selected is not None or flow_absent_repaired(m,trigger['start'],min(m.end,(decision+MINUTE-1)//MINUTE*MINUTE),observed),
        'stop_above_rejection_high':stop>high},operation='current rejection and strictly outside observed high',known_at=decision,assumption='A2-FLOW')
    else:e.bind({'planned_return_to_structure':reaction['known_at']<contact['at'],
        'buyers_absorb_and_hold':defense['held'] if defense else flow_absent_repaired(m,trigger['start'],min(m.end,(decision+MINUTE-1)//MINUTE*MINUTE),observed),
        'stop_behind_long_invalidation':stop<low},operation='actual later return and buyers absorb/hold, with structural stop',known_at=decision,assumption='A2-FLOW')
    e.stage('prior_reaction',reaction['known_at'],observed=True).stage('independent_HVN',profile['known_at'],observed=independent)
    e.stage('current_contact',contact['at'],observed=True).stage('local_response',selected['known_at'] if selected else None,observed=selected is not None)
    if getattr(m,'reconstruct',False):
        e.geometry['local_flow']=[{k:v for k,v in r.items() if k not in {'events','event_ids','book_changes'}} for r in observed]
    return window_result(m,'MEMBER-TWO-REASONS',branch,[e.finish(decision_at=decision,entry=entry,stop=stop,target=target)],omissions=omissions)

def scan_keani_repaired(m,branch):
    """P1: historical_auction_scanners.py:278. Frozen scan_keani calls local_observations. P2: absent() and flow_absent certify a collapsed window as False. Change: call local_observations_repaired, flow_absent_repaired and absent_repaired."""
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
                obs=local_observations_repaired(m,contact['at'],band,'long');st=flow_stages(obs);defense=st['defense']
    decision=defense['known_at'] if defense else min(m.end,limit+60*MINUTE);entry=defense.get('entry_px',defense['last']) if defense else None
    stop=band[0]-Q if band else a['low']-Q
    target=(prior['range']['high'] if prior['range'] and entry is not None and prior['range']['high']>entry else
            a['high']+(a['high']-a['low']))
    e=HistoricalEpisode(m,'KEANI-OPEN-ABOVE-VALUE',branch,'long',{'bar_id':a['id'],'start':a['start'],'end':a['end']},a)
    absent_stage=None if ambiguous_imbalance else absent_repaired(m,a['end'],limit,fields=('C',))
    absent_defense=flow_absent_repaired(m,retest['start'],min(m.end,(decision+MINUTE-1)//MINUTE*MINUTE),[r for r in obs['chunks'] if r['known_at']<=decision]) if obs else absent_stage
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


def _attach(result, row, version):
    result.update(coverage_id=row['coverage_id'], scanner=row['scanner'],
        source_definition=row['source_definition'], observation_unit=row['observation_unit'],
        assumption_ids=row['assumption_ids'], baseline_version=version)
    return result


def _scanner_for(row):
    if row.get('extra_unit'):
        return None
    method, branch = row['method_id'], row['branch']
    if method == 'GB-VWAP' and branch == 'source_long':
        return scan_green_vwap_repaired
    if method == 'GB-FAIL' and branch in GB_FAIL_BRANCHES:
        return scan_green_failure_repaired
    if method == 'SIRES' and branch in SIRES_LOCAL_BRANCHES:
        return scan_sires_repaired
    if method == 'SAINT-AMT' and branch in SAINT_BRANCHES:
        return scan_saint_repaired
    if method == 'MEMBER-TWO-REASONS' and branch in MEMBER_BRANCHES:
        return scan_member_repaired
    if method == 'KEANI-OPEN-ABOVE-VALUE' and branch == 'source_long':
        return scan_keani_repaired
    if method == 'JJ-TBR' and branch in JJ_TBR_ABSENT_BRANCHES:
        return scan_jumbo_repaired
    return None


def scan_branch_repaired(market, row):
    """Dispatch to a corrected scanner for a REPAIRS branch, else native scan_branch.

    Records match the frozen scan_branch schema with one added field
    baseline_version: B0.1-2026-09-14 on a repaired branch, B0 otherwise.
    """
    scanner = _scanner_for(row)
    if scanner is None:
        return _attach(native_scan_branch(market, row), row, B0_VERSION)
    return _attach(scanner(market, row['branch']), row, BASELINE_REPAIR_VERSION)
