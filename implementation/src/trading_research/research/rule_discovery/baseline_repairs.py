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
)
from trading_research.research.method_pack.historical_price_scanners import _known, _context, _gb_refs
from trading_research.research.method_pack.historical_auction_scanners import primary_balance, _control, _upper_failures
from trading_research.research.method_pack.historical_process_scanners import scan_supplied_unit, macro_at
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
JJ_TBR_REPAIRED_BRANCHES = JJ_TBR_ABSENT_BRANCHES + ("judas_outbound", "judas_reversal_deferred")
JUDAS_REVERSAL_VARIANTS = ("judas_reversal", "judas_reversal_deferred")
JJ_TBR_C2_BRANCHES = ("single_extended", "single_purged", "internal_rotation", "extension_reaction")
GB_FAIL_SWEEP_BRANCHES = (
    "nyam_box", "previous_hour", "asia_tdo_case", "cash_open_reclaim_case",
    "prior_day_level", "prior_week_level", "prior_month_level",
)
REFILL_RECORD_CONJUNCTS = (
    "zone_definition_recorded", "instrument_and_threshold_preserved",
    "thesis_recorded", "label_uses_only_post_touch_observations",
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
    "C1": {
        "branch_ids": (_cid("JJ-TBR", "judas_reversal"), _cid("JJ-TBR", "judas_reversal_deferred")),
        "frozen_symbol": "trading_research.research.method_pack.historical_price_scanners.scan_jumbo",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.scan_jumbo_repaired",
        "fixture": "f1_judas_reversal_sweep_window.py",
    },
    "C2": {
        "branch_ids": tuple(_cid("JJ-TBR", b) for b in JJ_TBR_C2_BRANCHES),
        "frozen_symbol": "trading_research.research.method_pack.historical_price_scanners.scan_jumbo",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.scan_jumbo_repaired",
        "fixture": "f2_single_breakout_action_window.py",
    },
    "C3": {
        "branch_ids": tuple(_cid("GB-FAIL", b) for b in GB_FAIL_BRANCHES),
        "frozen_symbol": "trading_research.research.method_pack.historical_price_scanners.scan_green_failure",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.scan_green_failure_repaired",
        "fixture": "f3_gbfail_five_minute_reclaim_window.py",
    },
    "C4": {
        "branch_ids": (_cid("KEANI-OPEN-ABOVE-VALUE", "source_long"),),
        "frozen_symbol": "trading_research.research.method_pack.historical_auction_scanners.scan_keani",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.scan_keani_repaired",
        "fixture": "f4_keani_rejection_level.py",
    },
    "C5": {
        "branch_ids": (_cid("SIRES", "microbalance_break"),),
        "frozen_symbol": "trading_research.research.method_pack.historical_flow.scan_microbalance",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.scan_microbalance_repaired",
        "fixture": "f6_microbalance_thesis_direction.py",
    },
    "C7": {
        "branch_ids": tuple(_cid("GB-FAIL", b) for b in GB_FAIL_BRANCHES)
        + (_cid("GB-VWAP", "source_long"),)
        + (_cid("JJ-TBR", "judas_outbound"), _cid("JJ-TBR", "other_session"))
        + tuple(_cid("SAINT-AMT", b) for b in SAINT_BRANCHES)
        + (
            _cid("SIRES", "absorption_reward_retest"),
            _cid("SIRES", "stop_four_stage"),
            _cid("SIRES", "defended_band_continuation"),
            _cid("SIRES", "kg1_retest"),
            _cid("SIRES", "microbalance_break"),
        )
        + (_cid("REFILL-STUDY", "touch_record"), _cid("STOIC-DATA", "macro_application")),
        "frozen_symbol": "trading_research.research.method_pack.historical_price_scanners.scan_green_failure",
        "corrected_symbol": "trading_research.research.rule_discovery.baseline_repairs.scan_branch_repaired",
        "fixture": "f7_constant_operand_census.py",
    },
}


def affected_branch_ids():
    seen = []
    for item in REPAIRS.values():
        for cid in item["branch_ids"]:
            if cid not in seen:
                seen.append(cid)
    return tuple(seen)


def _price_sign(value):
    """Numeric sign of a price difference. Not historical_features.sign (side)."""
    if value is None:
        return None
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


def _thesis_direction(micro, htf):
    """C5 operational rule: +1 when the microbalance midpoint is in the lower
    half of the larger balance, -1 in the upper half, None if either midpoint
    is unknown or the microbalance sits on the larger midpoint."""
    if micro is None or htf is None:
        return None
    if micro.get('low') is None or micro.get('high') is None:
        return None
    if htf.get('low') is None or htf.get('high') is None:
        return None
    micro_mid = (micro['low'] + micro['high']) / 2
    htf_mid = (htf['low'] + htf['high']) / 2
    if micro_mid < htf_mid:
        return 1
    if micro_mid > htf_mid:
        return -1
    return None


def _record_c7(e, decision, unevaluated=(), structural_false=(), *, by_construction=(),
               operational_assumption=(), assumption_id=None, context_direction_unevaluated=False):
    """Attach C7 details. literal_operand_kind is a map of operand name to kind so a
    mixed stage can carry by_construction beside context_direction_unevaluated,
    unevaluated_operand, structural_not_required, or operational_assumption."""
    details = {}
    kinds = {}
    for name in by_construction:
        kinds[name] = 'by_construction'
    for name in operational_assumption:
        kinds[name] = 'operational_assumption'
    if kinds:
        details['literal_operand_kind'] = kinds
    if assumption_id is not None:
        details['assumption_id'] = assumption_id
    if context_direction_unevaluated:
        details['context_direction_unevaluated'] = True
    if unevaluated:
        details['unevaluated_operand'] = list(unevaluated)
    if structural_false:
        details['structural_not_required'] = list(structural_false)
    if details:
        e.stage('baseline_repair', decision, observed=None, details=details)
    return e


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
    """P1: historical_flow.py:140. Frozen _flow_episode calls local_observations. Change: call local_observations_repaired and flow_absent_repaired.
    C7: historical_flow.py:130,170,177,204,240,244. Frozen binds location_touched, real_extreme, selected_deviation_touched, same_band_retest and kg1_retest as literals or by-construction expressions. Change: keep those frozen values and record literal_operand_kind=by_construction."""
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
    by_construction=['location_touched']
    if branch in {'absorption_reward_retest','stop_four_stage'}:by_construction.append('real_extreme')
    elif branch=='vwap_deviation_fade':by_construction.append('selected_deviation_touched')
    elif branch=='defended_band_continuation':by_construction.append('same_band_retest')
    elif branch=='kg1_retest':by_construction.append('kg1_retest')
    _record_c7(e,decision,by_construction=by_construction)
    return e.finish(decision_at=decision,entry=entry,stop=stop,target=target)

def scan_sires_repaired(m,branch):
    """P6: historical_flow.py:306. Frozen per-side dedup keys on the pivot-id tuple, so pivot-less KG1 references collapse. Change: key on the reference's own identifier (id, else a hash of bounds and kind) plus side. P1: dispatch through _flow_episode_repaired. C5: microbalance_break dispatches to scan_microbalance_repaired."""
    episodes=[];omissions=[]
    allbars=m.bars(m.start,m.end,300);auction=balances(allbars)
    if branch=='microbalance_break':return scan_microbalance_repaired(m,branch,auction)
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

def scan_microbalance_repaired(m,branch,auction=None):
    """C5: historical_flow.py:337,346. Frozen selects the trigger with sg*(C-boundary)>0 and then binds breakout_in_thesis_direction to the same expression, so it can never refuse. Change: thesis direction is an independent operational conjunct, +1 when the microbalance midpoint lies in the lower half of the larger balance and -1 in the upper half; the conjunct is sign(C-boundary) equal to that direction, and None when the larger balance or the microbalance midpoint is unknown.
    C7: historical_flow.py:130,346. Frozen binds location_touched and microbalance_frozen as by-construction literals. Change: keep those frozen values and record literal_operand_kind=by_construction."""
    auction=auction if auction is not None else balances(m.bars(m.start,m.end,300));episodes=[];omissions=[]
    used=set()
    for ref in auction:
        if ref['known_at']>=m.end:continue
        prior=[r for r in auction if r['known_at']<ref['start'] and r['width']>ref['width']]
        if not prior:continue
        htf=prior[-1]
        thesis_dir=_thesis_direction(ref,htf)
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
            break_sign=_price_sign(trigger['C']-boundary)
            in_thesis=None if thesis_dir is None or break_sign is None else break_sign==thesis_dir
            e.bind({'microbalance_frozen':True,'directional_strength':strength,'breakout_in_thesis_direction':in_thesis,
                'stop_behind_microbalance':stop<ref['low'] if side=='long' else stop>ref['high'],
                'microbalance_known_at':ref['known_at'],'breakout_at':trigger['known_at']},operation='price-defined alternating pivots inside earlier larger balance; C5 operational thesis direction from larger-balance half; C7 microbalance_frozen by construction',
                parents=[ref['id'],htf['id'],trigger['bar_id']],known_at=trigger['known_at'],assumption='A2-BALANCE')
            e.stage('confirmed_price_balance',ref['known_at'],observed=True).stage('directional_break',trigger['known_at'],observed=strength,details={'thesis_direction':thesis_dir})
            _record_c7(e,trigger['known_at'],by_construction=('location_touched','microbalance_frozen'))
            episodes.append(e.finish(decision_at=trigger['known_at'],entry=trigger['C'],stop=stop,target=target))
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

def _bind_judas_entry_window(m,e,decision,*,fail_reason=None):
    """C1 round 4: TBR p.8 reversal trade is 09:40-09:50. entry_in_reversal_window is not an M01 field, so bind() raises; the operand is stored on values and the reversal_entry_window stage. A False window fails the episode after evaluate(); entry/stop/decision_at are not moved on the strict variant."""
    in_window=m.at('09:40')<=decision<m.at('09:50')
    bind_rejected=False
    try:
        e.bind({'entry_in_reversal_window':in_window},
            operation='TBR p.8 places the reversal trade between 09:40 and 09:50; decision_at is the O056 confirmation known_at, or the deferred 09:40-bar known_at',
            known_at=decision,assumption='A2-TBR-CLOCK')
    except ValueError:
        bind_rejected=True
        e.values['entry_in_reversal_window']=in_window
    details={'entry_in_reversal_window':in_window,'bind_rejected_unknown_operand':bind_rejected}
    if bind_rejected:
        details['bind_rejected_operand']='entry_in_reversal_window'
    if not in_window:
        details['reason']=fail_reason or 'entry_outside_reversal_window'
    e.stage('reversal_entry_window',decision,observed=in_window,details=details)
    return in_window

def _strategy_status_for_verdict(verdict, scope='entry_setup'):
    """Map a research verdict onto the reconstruct strategy status so no_setup matches fail."""
    if scope!='entry_setup':
        return {'pass':'condition_present','fail':'condition_absent','unknown':'data_unavailable'}.get(verdict)
    return {'pass':'setup','fail':'no_setup','unknown':'data_unavailable'}.get(verdict)

def _sync_strategy_status(episode):
    """Generic post-finish repair: strategy status follows research verdict. One place, not per reason."""
    assessment=episode.get('strategy_assessment')
    if not assessment:
        return episode
    status=_strategy_status_for_verdict(episode.get('research_verdict'), assessment.get('scope') or 'entry_setup')
    if status is not None:
        assessment['status']=status
    return episode

def _fail_after_finish(episode, reason):
    """Force a fail after finish() and keep strategy status aligned with the research verdict."""
    episode['research_verdict']='fail'
    failed=list(episode.get('failed') or [])
    if reason not in failed:
        failed.append(reason)
    episode['failed']=failed
    assessment=episode.get('strategy_assessment')
    if assessment is not None:
        conditions=list(assessment.get('failed_conditions') or [])
        if reason not in conditions:
            conditions.append(reason)
        assessment['failed_conditions']=conditions
    return _sync_strategy_status(episode)

def _close_holds_swept_edge(bar, side, edge):
    """Reversal side of the swept 6-9 edge: long close above the swept low, short close below the swept high."""
    close=bar.get('C')
    if close is None:
        return False
    return close>edge if side=='long' else close<edge

def _relabel_episode_branch(episode, branch):
    """Keep M01 evaluate() on the judas_reversal CASE, then label the deferred variant."""
    identity={'method':episode['method'],'branch':branch,'predicate':episode['predicate'],
        'side':episode['side'],'session_date':episode['session_date'],
        'instrument_id':episode['instrument_id'],'reference_id':episode['reference_id'],
        'trigger_id':episode['trigger_id'],'occurrence_at':episode['occurrence_at']}
    episode['branch']=branch
    episode['candidate_id']='native-v2:'+content_hash(identity)[:32]
    return episode

def _deferred_judas_entry(m, confirm, entry, decision, side, edge):
    """If O056 completes before 09:40, enter at the first complete bar at or after 09:40 still on the reversal side of the swept edge. Stop and objective stay with the caller. Returns (entry, decision, fail_reason)."""
    window_start,window_end=m.at('09:40'),m.at('09:50')
    if confirm is None or decision is None or not (decision<window_start):
        return entry,decision,None
    for bar in m.bars(window_start,window_end):
        if not bar.get('observed_complete') or bar.get('C') is None:
            continue
        if _close_holds_swept_edge(bar, side, edge):
            return bar['C'],bar['known_at'],None
    return entry,decision,'reclaim_not_held_at_window'

def scan_jumbo_repaired(m,branch):
    """P2: historical_price_scanners.py:40,171. Frozen scan_jumbo calls absent() from _ob and from the extension_reaction prior_expansion conjunct. Change: use _ob_repaired and absent_repaired.
    C1: historical_price_scanners.py:71,89-90. Frozen judas_reversal searches the sweep only inside 09:40-09:50. Change: search the outbound sweep in 09:30-09:40 and keep the reversal window 09:40-09:50; a sweep found only in 09:40-09:50 stays accepted and is flagged sweep_in_reversal_window. source_time_window is True for a sweep in 09:30-09:50. Confirmation remains the frozen O056 search around the sweep bar. Round 4: the strict reversal entry itself must fall in 09:40-09:50 (TBR p.8). entry_in_reversal_window is recorded on the reversal_entry_window stage; bind() rejects the unknown M01 operand so the verdict is forced fail with reason entry_outside_reversal_window when decision_at is outside that window. Round 5: when branch is judas_reversal, also produce judas_reversal_deferred as a separate episode set. For an O056 confirmation before 09:40, the deferred variant enters at the first complete bar at or after 09:40 whose close is still on the reversal side of the swept 6-9 edge (long close above that low, short close below that high); entry is that bar's close, decision its known_at, stop and objective unchanged. No such bar by 09:50 fails with reclaim_not_held_at_window. Confirmations already inside 09:40-09:50 are identical in both variants.
    C2: historical_price_scanners.py:72. Frozen overrides action_end=16:00 for single_extended, single_purged, internal_rotation and extension_reaction. Change: leave the formation action_end at 10:00; the 16:00 population stays B0.
    C7: historical_price_scanners.py:137,145,153,163,176,179. Frozen binds exit_window_recorded, source_clock_verified, source_case_verified and the restating flags location_touched, reduced_expectations, expansion_policy, source_zone_known as by-construction literals. Change: keep those frozen values and record literal_operand_kind=by_construction."""
    method='JJ-TBR';episodes=[];omissions=[];deferred_episodes=[]
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
        if branch in JUDAS_REVERSAL_VARIANTS:
            action_start,action_end=m.at('09:30'),m.at('09:50')
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
            sweep_in_reversal_window=None
            if branch=='judas_outbound':
                trigger=next(iter(rows),None)
                target=ref['high']+width*D('.5') if side=='long' else ref['low']-width*D('.5')
            elif branch in JUDAS_REVERSAL_VARIANTS:
                def _edge_sweep(bar_rows):
                    return next((r for r in bar_rows if r['L']<edge),None) if side=='long' else next((r for r in bar_rows if r['H']>edge),None)
                trigger=_edge_sweep(m.bars(m.at('09:30'),m.at('09:40')))
                sweep_in_reversal_window=False
                if trigger is None:
                    trigger=_edge_sweep(m.bars(m.at('09:40'),m.at('09:50')))
                    sweep_in_reversal_window=True
            elif branch=='other_session':
                trigger=next((r for r in rows if r['L']<edge if side=='long'),None) if side=='long' else next((r for r in rows if r['H']>edge),None)
            else:trigger=first_contact(rows,*location)
            if trigger is None:continue
            strict=('below' if side=='long' else 'above') if branch in {'judas_reversal','judas_reversal_deferred','other_session'} else None
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
            variant_jobs=[(branch,entry,decision,None)]
            if branch in JUDAS_REVERSAL_VARIANTS:
                d_entry,d_decision,d_fail=_deferred_judas_entry(m,confirm,entry,decision,side,edge)
                if branch=='judas_reversal':
                    variant_jobs=[('judas_reversal',entry,decision,None),
                                  ('judas_reversal_deferred',d_entry,d_decision,d_fail)]
                else:
                    variant_jobs=[('judas_reversal_deferred',d_entry,d_decision,d_fail)]
            for variant,var_entry,var_decision,var_fail in variant_jobs:
                eval_branch='judas_reversal' if variant in JUDAS_REVERSAL_VARIANTS else variant
                e=HistoricalEpisode(m,method,eval_branch,side,episode_trigger,ref)
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
                    'confirm_at':confirm['known_at'] if confirm else None,'risk_defined':None if var_entry is None or stop is None else sg*(var_entry-stop)>0,
                    'objective_fixed':None if var_entry is None else sg*(target-var_entry)>0},
                    operation='frozen completed range, pre-touch context and exact selected O056 full-C2 signature',
                    parents=[ref['id'],trigger['bar_id']],known_at=var_decision,assumption='A2-CONTEXT/A2-TBR-CLOCK/A2-STRUCTURAL-RISK')
                by_construction=['location_touched']
                if branch=='judas_outbound':
                    e.bind({'directional_context':direction_ok,'at_rth_open':first is not None and m.at('09:30')<=first[0]<m.at('09:30')+SECOND,
                        'objective_is_selected_exhaustion':target==(ref['high']+width*D('.5') if side=='long' else ref['low']-width*D('.5')),
                        'exit_window_recorded':True},operation='opening execution policy with selected 0.5W exhaustion and 09:40 exit horizon; C7 exit_window_recorded by construction',assumption='A2-TBR-PROJ/A2-TBR-CLOCK')
                    by_construction.append('exit_window_recorded')
                elif variant in JUDAS_REVERSAL_VARIANTS:
                    e.bind({'reversal_context':None if pw is None else width>0,'edge_swept':trigger['L']<edge if side=='long' else trigger['H']>edge,
                        'sweep_at':touch,'source_time_window':m.at('09:30')<=touch<m.at('09:50'),
                        'objective_is_opposing_draw':target==(ref['high'] if side=='long' else ref['low'])},
                        operation='strict frozen edge sweep in Judas 09:30-09:40 or reversal 09:40-09:50 and opposing edge identity',assumption='A2-CONTEXT')
                elif branch=='single_extended':
                    e.bind({'extended_context':extended,'entry_at_eq_or_quadrant':trigger['L']<=location[0]<=trigger['H'],
                        'objective_is_range_edge':target in (ref['low'],ref['high']),'reduced_expectations':True},
                        operation='overnight width vs prior RTH and range EQ contact; edge target policy',assumption='A2-CONTEXT/A2-TBR-PROJ')
                    by_construction.append('reduced_expectations')
                elif branch=='single_purged':
                    old=prior['range'];purges=[]
                    if old:
                        for r in m.bars(max(m.start,old['known_at']),min(touch,m.at('09:30'))):
                            if r['H']>old['high'] or r['L']<old['low']:purges.append(r)
                    purgeat=purges[0]['known_at'] if purges else None
                    e.bind({'purged_compressed_context':None if compressed is None or not prior.get('range_scope_complete',prior['scope_complete']) else compressed and bool(purges),
                        'purge_known_at':purgeat,'entry_at_eq_or_quadrant':trigger['L']<=location[0]<=trigger['H'],
                        'expansion_policy':True},operation='chronological prior-session liquidity sweep before compressed EQ contact',parents=[old['id']] if old else [],assumption='A2-CONTEXT')
                    by_construction.append('expansion_policy')
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
                    e.bind({'source_clock_verified':True,'source_case_verified':True},kind='policy',operation='enumerated TBR p.7 formation identity; C7 source_clock_verified and source_case_verified by construction',assumption='A2-TBR-CLOCK')
                    by_construction.extend(['source_clock_verified','source_case_verified'])
                elif branch=='timed_pzone_reversal':
                    destination=D(str(zone['destination_price']));target=destination
                    e.bind({'source_zone_known':True,'zone_known_at':zone['known_at'],'source_time_window':zone['known_at']<=touch<zone['expires_at'],
                        'directed_path_recorded':bool(zone.get('destination_id'))},operation='frozen P-zone and directed anchor destination; inferred model identified in reference',parents=[zone['id']],kind='inferred_model' if zone.get('inferred_zone') else 'record',known_at=zone['known_at'])
                    by_construction.append('source_zone_known')
                contact_details=None if sweep_in_reversal_window is None else {'sweep_in_reversal_window':sweep_in_reversal_window}
                e.stage('contact',touch,observed=True,parents=[ref['id']],details=contact_details).stage('opening_context_confirmation' if branch=='judas_outbound' else 'selected_full_C2_confirmation',None if confirm is None else confirm['known_at'],observed=ok)
                if getattr(m,'reconstruct',False) and confirm:
                    e.geometry['confirmation_bar']=confirm
                _record_c7(e,var_decision,by_construction=by_construction)
                in_reversal_window=True
                if variant in JUDAS_REVERSAL_VARIANTS:
                    in_reversal_window=_bind_judas_entry_window(m,e,var_decision,fail_reason=var_fail)
                episode=e.finish(decision_at=var_decision,entry=var_entry,stop=stop,target=target)
                if var_fail:
                    episode=_fail_after_finish(episode,var_fail)
                elif variant in JUDAS_REVERSAL_VARIANTS and not in_reversal_window:
                    episode=_fail_after_finish(episode,'entry_outside_reversal_window')
                if variant=='judas_reversal_deferred':
                    episode=_relabel_episode_branch(episode,'judas_reversal_deferred')
                if variant==branch:
                    episodes.append(episode)
                elif variant=='judas_reversal_deferred':
                    deferred_episodes.append(episode)
    if prior['omissions']:omissions.extend(prior['omissions'])
    result=window_result(m,method,branch,episodes,omissions=omissions)
    if branch=='judas_reversal':
        result['deferred_variant']=window_result(m,method,'judas_reversal_deferred',deferred_episodes,omissions=omissions)
    return result

def scan_green_failure_repaired(m,branch):
    """P4: historical_price_scanners.py:224-225. Frozen scan_green_failure raises ValueError on max()/min() of an empty sweep path. Change: record an availability omission and emit the episode as input-unknown.
    C3: historical_price_scanners.py:219-223. Frozen reads only the five-minute candle containing the sweep. Change: take the first complete five-minute close back through the level at or after the sweep candle, forward to the branch end bound, and record confirm_bar_offset (0 = sweep candle). Round 4: after that confirming bar is found, recompute high/low/stop/sweep_high/sweep_low (and the cash_open_reclaim_case target from low) over m.bars(trigger['start'], confirmation_end), the whole excursion through the confirming bar. confirm_bar_offset 0 is unchanged. details['excursion_bars'] = confirm_bar_offset + 1. Empty-path P4 still does not search later bars.
    C7: historical_price_scanners.py:230,238,242. Frozen binds bias_recorded to computed pre-touch presence, source_session_allowed=True, and structural pocket_required/retracement_entry=False. Change: keep bias_recorded as that computed presence and record context_direction_unevaluated; keep source_session_allowed with literal_operand_kind=by_construction; keep the structural flags and record them in structural_not_required when False."""
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
            aligned=trigger['start']//(5*MINUTE)*5*MINUTE
            sweep_candle_end=aligned+5*MINUTE
            path=m.bars(trigger['start'],sweep_candle_end)
            confirm=None;close=None;usable=False;confirm_bar_offset=None;confirmation_end=sweep_candle_end
            high=low=stop=None
            target=None if branch=='cash_open_reclaim_case' else (ref['low'] if side=='short' else ref['high'])
            if not path:
                omissions.append({'kind':'availability','reason':'sweep path empty: no bars known at or before confirmation_end','window':[trigger['start'],sweep_candle_end],'side':side,'reference_id':ref.get('id')})
                cand=m.bars(aligned,sweep_candle_end,300)
                row=cand[0] if cand else None
                if row is not None and row['observed_complete'] and row['C'] is not None:
                    confirm=row;close=row['C'];usable=True;confirm_bar_offset=0
            else:
                offset=0
                while True:
                    bar_start=aligned+offset*5*MINUTE
                    bar_end=bar_start+5*MINUTE
                    if bar_start>=end:break
                    cand=m.bars(bar_start,bar_end,300)
                    row=cand[0] if cand else None
                    ok_bar=row is not None and row['observed_complete'] and row['C'] is not None
                    if ok_bar and sg*(row['C']-boundary)>0:
                        confirm=row;close=row['C'];usable=True;confirm_bar_offset=offset;confirmation_end=bar_end
                        break
                    if ok_bar and confirm is None:
                        confirm=row;close=row['C'];usable=True;confirm_bar_offset=offset;confirmation_end=bar_end
                    offset+=1
                excursion=m.bars(trigger['start'],confirmation_end) or path
                high=max(r['H'] for r in excursion);low=min(r['L'] for r in excursion)
                stop=high+Q if side=='short' else low-Q
                target=ref['low'] if side=='short' else ref['high']
                if branch=='cash_open_reclaim_case':target=boundary+(boundary-low)*D('.5')
            decision=confirmation_end
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
                operation='identified finished reference and first strict sweep; first complete five-minute reclaim at or after the sweep candle; C7 bias_recorded is computed presence with unevaluated direction',
                parents=[ref['id'],trigger['bar_id']],known_at=decision,assumption='A2-GB-CLOCK/A2-CONTEXT/A2-STRUCTURAL-RISK')
            e.stage('reference',ref['known_at'],observed=_known(ref)).stage('sweep',contact['at'],observed=True,parents=contact['event_ids'])
            reclaim_details={'tdo':tdo,'tdo_required':tdo_required,'confirm_bar_offset':confirm_bar_offset}
            if confirm_bar_offset is not None:
                reclaim_details['excursion_bars']=confirm_bar_offset+1
            e.stage('five_minute_reclaim',confirmation_end,observed=None if close is None else sg*(close-boundary)>0,
                parents=[confirm['bar_id']] if confirm else [],details=reclaim_details)
            if getattr(m,'reconstruct',False):e.geometry['confirmation_bar']=confirm
            structural_false=['pocket_required','retracement_entry']
            if not tdo_required:structural_false.append('tdo_required')
            _record_c7(e,decision,(),structural_false,by_construction=('source_session_allowed',),
                context_direction_unevaluated=True)
            episodes.append(e.finish(decision_at=decision,entry=close,stop=stop,target=target))
    result=window_result(m,method,branch,episodes,omissions=omissions)
    if getattr(m,'reconstruct',False):result['reference_selections']=[r for r in refs if r is not None]
    return result

def scan_green_refinement_repaired(m,branch):
    """P4: historical_price_scanners.py:257. Frozen scan_green_refinement calls scan_green_failure as parent. Change: call scan_green_failure_repaired.
    C3 applies through the nyam_box parent reclaim. C7: parent bias_recorded stays the frozen computed presence with context_direction_unevaluated; retracement_entry is required True for this annotation."""
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
        structural_false=['pocket_required'] if episode['values'].get('pocket_required') is False else []
        _record_c7(e,c['known_at'],(),structural_false,by_construction=('source_session_allowed',),
            context_direction_unevaluated=True)
        out=e.finish(decision_at=c['known_at'],entry=None,stop=None,target=None)
        out['parent_entry_at']=start;out['observation_unit']='post_parent_annotation';episodes.append(out)
    return window_result(m,'GB-FAIL',branch,episodes,omissions=parent['omissions'])

def scan_green_vwap_repaired(m,branch):
    """D1: historical_price_scanners.py:314. Frozen scan_green_vwap rebinds continuation_context with the retest-absence answer, overwriting the breakout-context conjunct from line 308. Change: keep continuation_context as the breakout comparison and record the retest conjunct on retest_at/retest_low/retest_high. P2: the later_VWAP_return stage uses absent_repaired.
    C7: historical_price_scanners.py:309. Frozen binds vwap_reset_verified to True. Change: keep True as the A2-GB-CLOCK 18:00 reset operational assumption and record literal_operand_kind=operational_assumption."""
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
        'risk_defined':None if entry is None else entry>stop},operation='finished Asia/London highs, five-minute break, later contemporaneous execution VWAP return; C7 vwap_reset_verified is A2-GB-CLOCK operational assumption',
        parents=[asia['id'],london['id'],breakout['bar_id']],known_at=decision,assumption='A2-GB-CLOCK/A2-STRUCTURAL-RISK')
    if retest is None:e.bind({'retest_at':None,'retest_low':None,'retest_high':None},operation='no later VWAP retest in declared observed horizon')
    e.stage('above_both_highs',breakout['end'],observed=True).stage('later_VWAP_return',retest_at,
        observed=True if retest else absent_repaired(m,breakout['end'],deadline),details=vw)
    _record_c7(e,decision,operational_assumption=('vwap_reset_verified',),assumption_id='A2-GB-CLOCK')
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
    """P2: historical_auction_scanners.py:50. Frozen _saint_base calls _control_absence. Change: call _control_absence_repaired.
    C7: historical_auction_scanners.py:46,49,51. Frozen binds profile_allows_trade from the HTF profile, arrival_read_recorded=True and alignment_ok=True if control else None. Change: bind those three to None as unevaluated market stages until P15-13."""
    profile=m.profile(ref['start'],ref['known_at'],'.68')
    permission=None if profile['poc'] is None else ref['low']<=profile['poc']<=ref['high']
    e.bind({'balance_fixed_before_use':ref['known_at']<=arrival,'balance_known_at':ref['known_at'],
        'profile_allows_trade':None,'arrival_read_recorded':None,'arrival_at':arrival,
        'control_evidence_recorded':True if control else _control_absence_repaired(m,arrival//MINUTE*MINUTE if control_start is None else control_start,decision,side),
        'control_at':control['known_at'] if control else None,'alignment_ok':None,
        'risk_defined':None if entry is None else sign(side)*(entry-stop)>0,
        'objective_fixed':None if entry is None else sign(side)*(target-entry)>0},
        operation='distinct HTF price balance with 68% profile and current repeated directional body/delta control; C7 profile_allows_trade, arrival_read_recorded, alignment_ok unevaluated',
        parents=[ref['id'],profile['id']],known_at=decision,assumption='A2-BALANCE/A2-STRUCTURAL-RISK')
    e.geometry['htf_profile']=profile

def scan_saint_repaired(m,branch):
    """P2: historical_auction_scanners.py:98,108,109,158,161,162,168. Frozen scan_saint calls absent() and _control_absence, certifying absence from a zero-length window as False. Change: call absent_repaired and _control_absence_repaired.
    C7: historical_auction_scanners.py:46,49,51,103. arrival_read_recorded, alignment_ok and profile_allows_trade stay None with unevaluated_operand. ltf_balance_broken stays True with literal_operand_kind=by_construction."""
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
            by_construction=('ltf_balance_broken',) if branch=='continuation_retest' else ()
            _record_c7(e,decision,('profile_allows_trade','arrival_read_recorded','alignment_ok'),
                by_construction=by_construction)
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
            _record_c7(e,decision,('profile_allows_trade','arrival_read_recorded','alignment_ok'))
            episodes.append(e.finish(decision_at=decision,entry=entry,stop=stop,target=target))
    return window_result(m,'SAINT-AMT',branch,episodes,omissions=omissions)

def scan_member_repaired(m,branch):
    """P1: historical_auction_scanners.py:219. Frozen scan_member calls local_observations. P2: flow_absent uses absent(). Change: call local_observations_repaired and flow_absent_repaired.
    C7: historical_auction_scanners.py:234. Frozen binds actual_band_contact=True. Change: keep the frozen value and record literal_operand_kind=by_construction."""
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
    _record_c7(e,decision,by_construction=('actual_band_contact',))
    return window_result(m,'MEMBER-TWO-REASONS',branch,[e.finish(decision_at=decision,entry=entry,stop=stop,target=target)],omissions=omissions)

def scan_keani_repaired(m,branch):
    """P1: historical_auction_scanners.py:278. Frozen scan_keani calls local_observations. P2: absent() and flow_absent certify a collapsed window as False. Change: call local_observations_repaired, flow_absent_repaired and absent_repaired.
    C4: historical_auction_scanners.py:258-260. Frozen tests a wick into the developing value-area low. Change: the rejection candle wicks into the developing POC or the previous day's value-area high and closes back above it; record which level. The developing-VAL variant stays B0."""
    prior=m.prior('day');old=prior['sessions'][-1]['window'] if prior['sessions'] else None
    p=old.profile(old.start,old.end) if old else None
    a=m.range(m.at('09:30'),m.at('10:00'),'Keani-A')
    if a is None:return window_result(m,'KEANI-OPEN-ABOVE-VALUE',branch,[],omissions=[*prior['omissions'],{'reason':'A period has no observed executions'}])
    initial=m.profile(a['start'],a['end']);limit=m.at(setting('keani_time')['latest_break'])
    observation=breakout=band=retest=defense=contact=None;dev=None;imbalance=None;obs=None;ambiguous_imbalance=[]
    rejection_level=None
    for row in m.bars(a['end'],limit):
        current=m.profile(a['start'],row['start'])
        higher=current['val'] is not None and initial['val'] is not None and current['val']>initial['val'] and current['vah']>=initial['vah']
        poc=current.get('poc')
        prior_vah=p['vah'] if p and p.get('vah') is not None and prior.get('scope_complete') else None
        hit_poc=poc is not None and row['C'] is not None and row['L']<=poc and row['C']>poc
        hit_vah=prior_vah is not None and row['C'] is not None and row['L']<=prior_vah and row['C']>prior_vah
        rejection=higher and row['C'] is not None and (hit_poc or hit_vah)
        if observation is None and rejection:
            observation=row
            names=[]
            if hit_poc:names.append('developing_poc')
            if hit_vah:names.append('prior_day_vah')
            rejection_level=names[0] if len(names)==1 else names
            continue
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
    e.geometry.update(prior_profile=p,a_profile=initial,developing_profile=dev,imbalance=imbalance,imbalance_band=band,rejection_level=rejection_level)
    if getattr(m,'reconstruct',False):e.geometry.update(observation_bar=observation,breakout_bar=breakout)
    for name,row in [('developing_value_rejection',observation),('imbalance_break',breakout),('same_band_return',retest),('buyer_defense',defense)]:
        details={'rejection_level':rejection_level} if name=='developing_value_rejection' else None
        e.stage(name,row['known_at'] if row else None,observed=True if row else absent_stage,details=details)
    omissions=[*prior['omissions']]
    if ambiguous_imbalance:omissions.append({'kind':'input_ambiguity','reason':'candidate footprint has unknown aggressor quantity; diagonal imbalance cannot be certified','candle_ids':ambiguous_imbalance,'required_fields':['aggressor_side']})
    return window_result(m,'KEANI-OPEN-ABOVE-VALUE',branch,[e.finish(decision_at=decision,entry=entry,stop=stop,target=target)],omissions=omissions)

def scan_refill_repaired(m,branch):
    """C7: historical_process_scanners.py:38-43. Frozen binds four REFILL record conjuncts to True. Change: keep those frozen values and record literal_operand_kind=by_construction."""
    if branch!='touch_record':return scan_supplied_unit(m,'REFILL-STUDY',branch,extra=False)
    from trading_research.research.method_pack.empirical_tape import m09_research_comparison
    rule={'rule_id':'v2:REFILL-STUDY:touch_record','method_id':'REFILL-STUDY','branch':branch,
        'evidence_mode':'research_comparison','assumption_ids':['A2-REFILL'],'parameters':{**setting('refill'),'retain_stage_receipts':True}}
    start=m.at('09:30');end=m.end
    events=m.local(start,end)
    result=m09_research_comparison(events,rule=rule,partition={'partition_id':str(m.day),
        'session_date':str(m.day),'instrument_id':m.instrument_id},registry_sha256=m.records['registry_sha256'],
        tick_size=Q,coverage_ok=True if m.coverage(start,end)['observed_scope_complete'] else None,session_end=end)
    episodes=[];prior_by_zone=defaultdict(list)
    for record in result['records']:
        opp=record['opportunity'];replay=record['replay'];ref=opp['reference'];trigger=opp['trigger'];at=opp['available_at']
        old=[r for r in prior_by_zone[opp['reference_id']] if r['resolved_at']<opp['occurrence_start']]
        e=HistoricalEpisode(m,'REFILL-STUDY',branch,opp['side'],{'id':opp['opportunity_id'],'at':opp['occurrence_start']},
            {**ref,'id':ref['reference_id']})
        e.bind({'zone_definition_recorded':True,'zone_frozen':ref['immutable'],'zone_known_at':ref['known_at'],
            'instrument_and_threshold_preserved':True,'departure_observed':ref.get('departure_at') is not None,
            'departure_at':ref.get('departure_at'),'distinct_touch_id':opp['opportunity_id'] not in {r['id'] for r in old},
            'touch_at':opp['occurrence_start'],'thesis_recorded':True,'feature_max_known_at':max([ref['known_at']]+[r['resolved_at'] for r in old]),
            'memory_uses_only_prior_resolved_touches':all(r['resolved_at']<opp['occurrence_start'] for r in old),
            'label_uses_only_post_touch_observations':True},operation='existing immutable nonoverlapping large-execution-pair state machine; C7 four record conjuncts by construction',
            parents=ref['formation_event_ids'],known_at=at,assumption='A2-REFILL')
        e.stage('zone_formation',ref['known_at'],observed=True).stage('departure',ref.get('departure_at'),observed=True)
        e.stage('distinct_return',opp['occurrence_start'],observed=True)
        _record_c7(e,at,by_construction=REFILL_RECORD_CONJUNCTS)
        out=e.finish(decision_at=at,entry=D(str(trigger['price'])))
        out['refill_response']=replay;out['prior_resolved_memory']=old
        episodes.append(out)
        resolved=replay.get('completed_at',replay.get('completion_at',opp['expiry_at']))
        prior_by_zone[opp['reference_id']].append({'id':opp['opportunity_id'],'resolved_at':resolved,'verdict':replay.get('verdict')})
    out=window_result(m,'REFILL-STUDY',branch,episodes)
    out['zone_formation_count']=len(result['zones']);out['formation_ambiguities']=result['ambiguities']
    out['native_execution_members']=result['physical_member_count']
    return out

def scan_stoic_data_repaired(m,branch,*,extra=False):
    """C7: historical_process_scanners.py:165. Frozen binds cycle_and_indicator_rules_recorded to True on the reconstruct path, else None. Change: keep that frozen value and record literal_operand_kind=by_construction."""
    records=m.records.get('process_review',[]);episodes=[]
    macro=macro_at(m,m.at('09:30')) if branch=='macro_application' else None
    for record in records:
        start=record['collection_started_at'];decision=record['collection_completed_at']
        eligible=record['eligible_ids'];included=record['included_ids'];feature_rows=record['features'];outcomes=record['outcomes']
        e=HistoricalEpisode(m,'STOIC-DATA',branch,'not_applicable',{'id':record['id'],'at':start},
            {'id':record['spec_sha256'],'known_at':record['spec_frozen_at']},predicate='macro_application' if branch=='macro_application' else 'process')
        e.bind({'process_spec_frozen':bool(record['spec_sha256']),'spec_known_at':record['spec_frozen_at'],
            'sample_start_at':start,'inclusion_rule_fixed':record['inclusion_sha256']==record['frozen_inclusion_sha256'],
            'uniform_schema':len(set(record['record_schemas']))<=1,'all_eligible_observations_retained':set(eligible)==set(included) and len(included)==len(set(included)),
            'features_available_before_decisions':all(r['known_at']<=r['decision_at'] for r in feature_rows),
            'outcomes_separated_from_inputs':not set(record['feature_fields'])&set(record['outcome_fields']),
            'aggregate_winner_loser_comparison_recorded':sum(record['comparison_counts'].values())==len(outcomes),
            'revision_uses_only_prior_sample':all(r['sample_completed_at']<r['revised_at'] for r in record['revisions'])},
            operation='actual collection manifest, exact eligible/retained membership, feature clocks and separate outcome tables',
            parents=[record['id']],known_at=decision,kind='process')
        if macro:
            observations=macro['initial_publication_observations']
            e.bind({'release_vintages_recorded':all(r['current'] is not None for r in observations),
                'historical_comparison_defined':all(r['comparison_history_complete'] for r in observations),
                'cycle_and_indicator_rules_recorded':True if getattr(m,'reconstruct',False) else None},operation='existing verified initial BLS vintages and 12-prior-observation O160 comparison; C7 cycle_and_indicator_rules_recorded by construction',
                parents=[r['current']['observation_id'] for r in observations if r['current']],known_at=m.at('09:30'),assumption='A2-MACRO')
            e.geometry['macro']=macro
            _record_c7(e,decision,by_construction=('cycle_and_indicator_rules_recorded',))
        episodes.append(e.finish(decision_at=decision))
    out=window_result(m,'STOIC-DATA',branch,episodes,extra=extra,omissions=[] if records else [{'reason':'collection review is emitted after this date job finishes','kind':'pending_process_record'}])
    if macro:out['measured_quantities']=macro
    return out


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
    if method == 'SIRES' and branch == 'microbalance_break':
        return scan_microbalance_repaired
    if method == 'SIRES' and branch in SIRES_LOCAL_BRANCHES:
        return scan_sires_repaired
    if method == 'SAINT-AMT' and branch in SAINT_BRANCHES:
        return scan_saint_repaired
    if method == 'MEMBER-TWO-REASONS' and branch in MEMBER_BRANCHES:
        return scan_member_repaired
    if method == 'KEANI-OPEN-ABOVE-VALUE' and branch == 'source_long':
        return scan_keani_repaired
    if method == 'JJ-TBR' and branch in JJ_TBR_REPAIRED_BRANCHES:
        return scan_jumbo_repaired
    if method == 'REFILL-STUDY' and branch == 'touch_record':
        return scan_refill_repaired
    if method == 'STOIC-DATA' and branch == 'macro_application':
        return scan_stoic_data_repaired
    return None


def scan_branch_repaired(market, row):
    """Dispatch to a corrected scanner for a REPAIRS branch, else native scan_branch.

    Records match the frozen scan_branch schema with one added field
    baseline_version: B0.1-2026-09-14 on a repaired branch, B0 otherwise.
    Judas reversal returns two labelled sets: judas_reversal (strict) and
    judas_reversal_deferred (window entry), each with its own coverage_id.
    """
    scanner = _scanner_for(row)
    if scanner is None:
        return _attach(native_scan_branch(market, row), row, B0_VERSION)
    if row.get('method_id')=='JJ-TBR' and row.get('branch')=='judas_reversal_deferred':
        produced=scan_jumbo_repaired(market,'judas_reversal')
        deferred=produced.get('deferred_variant') or scan_jumbo_repaired(market,'judas_reversal_deferred')
        return _attach(deferred, row, BASELINE_REPAIR_VERSION)
    result=scanner(market, row['branch'])
    if isinstance(result, dict):
        result.pop('deferred_variant', None)
    return _attach(result, row, BASELINE_REPAIR_VERSION)
