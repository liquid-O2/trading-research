"""Causal VWAP, native context identities and attributed source readouts.

Price-weighted calculations consume the selected observations. Proprietary
readouts retain their source meaning; this module supplies no dealer engine.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal, InvalidOperation

from ..clocks import ns_to_et
from ..contracts import OutputField as F
from ..logic import kleene_and
from ..protocol import RecipeResult


def number(value):
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError('Boolean is not a numerical observation')
    try:
        v = Decimal(str(value)) if isinstance(value, float) else Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError('invalid numerical observation') from exc
    if not v.is_finite():
        raise ValueError('nonfinite numerical observation')
    return v


def _known(*times):
    return max(times) if times and all(type(x) is int for x in times) else None


def _result(rid, inp, value, *, missing=(), invalid=(), known=None, supplied=False, coverage=None, parents=()):
    missing, invalid = list(dict.fromkeys(missing)), list(dict.fromkeys(invalid))
    if known is not None:
        for key in ('use_at','known_at'):
            if type(inp.get(key)) is int and known > inp[key]:
                invalid.append('late_'+key)
    state = 'invalid' if invalid else 'hole' if missing else 'supplied' if supplied else 'computed'
    return RecipeResult(rid,state,value,known_at=known,base_ok=False if invalid else True,
       coverage_ok=coverage,hole_ids=[f'HOLE:{rid}:{x}' for x in missing+invalid],
       reason='; '.join(invalid or missing) or None,parent_ids=list(parents))


def _vwap(inp, anchored=False):
    rid = 'O031' if anchored else 'O030'
    reset = inp.get('anchor_price_at') if anchored else inp.get('reset_at')
    reset_id = inp.get('anchor_id') if anchored else inp.get('reset_id')
    as_of, instrument, tape = inp.get('as_of'), inp.get('instrument_id'), inp.get('canonical_tape_id')
    basis = inp.get('basis')
    missing, invalid, times, member_ids, seen = [], [], [], [], set()
    for name,v in [('reset_at',reset),('reset_id',reset_id),('as_of',as_of),('basis',basis),('instrument_id',instrument),('canonical_tape_id',tape)]:
        if v is None:missing.append(name)
    if not anchored and inp.get('reset_verified') is not True:missing.append('reset')
    if anchored:
        for k in ('anchor_known_at','anchor_reason','anchor_selected_at'):
            if inp.get(k) is None:missing.append(k)
        times.extend([inp.get('anchor_known_at'),inp.get('anchor_selected_at')])
    if reset is not None and as_of is not None and reset > as_of:invalid.append('reset_after_snapshot')
    if type(as_of) is int and type(inp.get('use_at')) is int and as_of > inp['use_at']:
        invalid.append('snapshot_after_use')
    if inp.get('coverage_complete') is not True:missing.append('coverage')
    if inp.get('gap'):missing.append('coverage_gap')
    total = weighted = squared = Decimal(0)
    chosen_basis = basis
    if basis not in {'trade_price','HLC3','HL2','OHLC4','close'}:
        missing.append('source_price_basis');chosen_basis = None
    is_comparison = inp.get('variant') == 'comparison'
    if basis != 'trade_price' and inp.get('source_basis_verified') is not True and not is_comparison:
        missing.append('source_price_basis')
    observations = inp.get('trades',inp.get('events',[])) if basis == 'trade_price' else inp.get('bars',[])
    if not isinstance(observations,list):raise ValueError('VWAP members must be a list')
    for row in observations:
        at = row.get('event_ns',row.get('t')) if basis == 'trade_price' else row.get('start',row.get('start_ns'))
        end = row.get('end',row.get('end_ns')) if basis != 'trade_price' else at
        known = row.get('known_at',at if basis == 'trade_price' else end)
        if at is None or end is None:missing.append('member_time');continue
        # A snapshot excludes later observations, including incomplete future bars.
        if reset is None or as_of is None or at < reset or end > as_of:continue
        if basis == 'trade_price' and (row.get('action','T') != 'T' or row.get('is_quote')):continue
        if basis != 'trade_price' and row.get('complete') is not True:missing.append('complete_bar');continue
        if known is None or known < end:missing.append('member_availability');continue
        if known > as_of:missing.append('member_availability');continue
        if str(row.get('instrument_id',instrument)) != str(instrument):invalid.append('cross_contract_sum');continue
        if row.get('dataset_id',tape) != tape:invalid.append('mixed_tape_ownership');continue
        eid = row.get('event_id',row.get('bar_id'))
        if eid is None:missing.append('member_identity')
        elif eid in seen:invalid.append('duplicate_member');continue
        else:seen.add(eid);member_ids.append(eid)
        if basis == 'trade_price':
            price,size = number(row.get('price')), number(row.get('size',row.get('executed_size')))
        else:
            o,h,l,c = [number(row.get(k)) for k in ('O','H','L','C')]
            size = number(row.get('V',row.get('volume')))
            if any(v is None for v in (o,h,l,c)):missing.append('bar_OHLC');continue
            if h < max(o,l,c) or l > min(o,h,c):invalid.append('bar_geometry');continue
            price = {'HLC3':(h+l+c)/3,'HL2':(h+l)/2,'OHLC4':(o+h+l+c)/4,'close':c}.get(chosen_basis)
        if price is None or size is None:missing.append('price_volume');continue
        if size < 0:invalid.append('negative_volume');continue
        total += size;weighted += price*size;squared += price*price*size;times.append(known)
    if basis != 'trade_price' and observations and reset is not None and as_of is not None:
        bars = sorted([b for b in observations if b.get('start') is not None and b.get('end') is not None and reset <= b['start'] and b['end'] <= as_of],key=lambda b:b['start'])
        cursor = reset
        for bar in bars:
            if bar['start'] != cursor:missing.append('bar_interval_coverage')
            cursor=bar['end']
        if cursor != as_of:missing.append('bar_interval_coverage')
    if not times or any(t is None for t in times):missing.append('availability')
    # A complete snapshot cannot be available before its cut-off: the absence
    # of later in-window executions is itself only known at that cut-off.
    known = _known(*times, as_of) if times else None
    if total == 0:missing.append('zero_volume')
    touch=inp.get('touch_at')
    if touch is not None and as_of is not None and (as_of>touch or as_of==touch and inp.get('source_includes_contact_trade') is not True):invalid.append('snapshot_not_before_contact')
    if known is not None and as_of is not None and known>as_of:invalid.append('anchor_not_known_at_snapshot')
    literal=None if total==0 else weighted/total
    faithful=False if invalid else None if missing or is_comparison else True
    variance=None if total==0 else max(Decimal(0),squared/total-(weighted/total)**2)
    v={'sum_v':total,'sum_pv':weighted,'sum_p2v':squared,'weighted_variance_population':variance,
       'vwap':literal if faithful is True or is_comparison and not invalid else None,
       'comparison_vwap':literal,'reset_id':reset_id,'reset_at':reset,'basis':basis,'as_of':as_of,'known_at':known,
       'member_event_ids':member_ids,'faithful':faithful,'variant':inp.get('variant','source'),
       'vwap_at_retest':literal if faithful is True else None,'vwap_known_at':known if faithful is True else None,
       'vwap_reset_verified':True if inp.get('reset_verified') is True else None,
       'source_vwap_known':faithful,'automatic_reset':None}
    if anchored:
        v.update(anchor_id=reset_id,anchor_price_at=reset,anchor_known_at=inp.get('anchor_known_at'),
                 anchor_selected_at=inp.get('anchor_selected_at'),anchor_reason=inp.get('anchor_reason'),
                 avwap=v['vwap'],usable_at=known,usable=False if invalid else None if missing else True)
    return _result(rid,inp,v,missing=missing,invalid=invalid,known=known,coverage=inp.get('coverage_complete'),parents=[reset_id] if reset_id else [])


def o030(inp):return _vwap(inp)
def o031(inp):return _vwap(inp,True)


def o032(inp):
    mu,sigma,k = [number(inp.get(x)) for x in ('mu','sigma','k')]
    convention=inp.get('variance_convention')
    missing=[x for x,v in [('mu',mu),('sigma',sigma),('k',k),('variance_convention',convention),('band_id',inp.get('band_id')),('parent_snapshot_id',inp.get('parent_snapshot_id'))] if v is None]
    invalid=[]
    if sigma is not None and sigma<0:invalid.append('negative_sigma')
    if k is not None and k<0:invalid.append('negative_multiplier')
    ready=all(x is not None for x in (mu,sigma,k)) and not invalid and convention is not None
    upper,lower=(mu+k*sigma,mu-k*sigma) if ready else (None,None)
    known=_known(inp.get('vwap_known_at'),inp.get('sigma_known_at'))
    if known is None:missing.append('snapshot_availability')
    if inp.get('touch_at') is not None and known is not None and known>=inp['touch_at']:invalid.append('snapshot_not_before_contact')
    for key in ('reset_id','weighting_universe'):
        if inp.get(key) is not None and inp.get('sigma_'+key) != inp[key]:invalid.append('mismatched_'+key)
    price=number(inp.get('price'))
    v=dict(upper=upper,lower=lower,band=[lower,upper] if ready else None,band_id=inp.get('band_id'),
           parent_snapshot_id=inp.get('parent_snapshot_id'),variance_convention=convention,as_of=inp.get('as_of'),
           touch_upper=None if price is None or upper is None else price==upper,
           touch_lower=None if price is None or lower is None else price==lower,
           faithful_band=False if invalid else None if missing else True,automatic_sigma=None,fade=False)
    return _result('O032',inp,v,missing=missing,invalid=invalid,known=known,coverage=inp.get('coverage_complete'),parents=[inp['parent_snapshot_id']] if inp.get('parent_snapshot_id') else [])


def o033(inp):
    regime=inp.get('source_regime');missing=[];invalid=[]
    if regime is None:missing.append('source_regime')
    elif regime not in {'short_gamma','long_gamma','uncertain'}:invalid.append('regime_label')
    identity=inp.get('native_identity')
    native_ok=None
    if isinstance(identity,dict):
        native_ok=kleene_and(identity.get('is_0dte'),identity.get('source_product_ok'))
        if native_ok is False:invalid.append('native_identity')
    else:missing.append('native_identity')
    ofm=fade=None
    if regime in {'short_gamma','long_gamma'}:
        ofm=regime=='short_gamma';fade=regime=='long_gamma'
    branch=inp.get('branch');permission={'ofm_aggressive':ofm,'balance_failure_fade':fade}.get(branch)
    rereads=deepcopy(inp.get('rereads',[]));as_of=inp.get('as_of',inp.get('use_at'))
    if any(r.get('known_at') is None for r in rereads):missing.append('reread_availability')
    rereads=[r for r in rereads if r.get('known_at') is not None and as_of is not None and r['known_at']<=as_of]
    v=dict(source_regime=regime,branch_regime_ok=permission,native_identity_ok=native_ok,reread_at=max([r['known_at'] for r in rereads],default=None),
           rereads=rereads,aggressive_ofm_ok=ofm,balance_fade_ok=fade,automatic_regime=None,other_gates_still_required=True)
    known=_known(inp.get('known_at'),*([identity.get('known_at')] if isinstance(identity,dict) else []),
                 *(r['known_at'] for r in rereads))
    return _result('O033',inp,v,missing=missing,invalid=invalid,known=known,supplied=True)


def o034(inp):
    record=deepcopy(inp.get('contract',inp));missing=[];invalid=[]
    symbol=record.get('symbol');expiry=record.get('expiration',record.get('expiry'));strike=number(record.get('strike'))
    right=record.get('right');option_class=record.get('option_class');osi=record.get('osi_symbol')
    for name,v in [('symbol',symbol),('expiration',expiry),('strike',strike),('right',right),('option_class',option_class),('osi_symbol',osi)]:
        if v is None:missing.append(name)
    at=record.get('available_at',record.get('known_at'));observed=record.get('observation_at',at)
    observed_date=ns_to_et(observed).date().isoformat() if type(observed) is int else record.get('observation_date')
    if observed is None:missing.append('observation_at')
    zero=None if expiry is None or observed_date is None else str(expiry)[:10]==observed_date
    if expiry is not None:
        try:date.fromisoformat(str(expiry)[:10])
        except ValueError:invalid.append('expiration')
    expected=inp.get('source_product');product_ok=None if expected is None or symbol is None else expected==symbol
    if product_ok is False:invalid.append('source_product')
    if right is not None and right not in {'C','P','call','put'}:invalid.append('option_right')
    if strike is not None and strike<=0:invalid.append('strike')
    key=None if any(x is None for x in (symbol,option_class,expiry,strike,right,osi)) else [symbol,option_class,str(expiry)[:10],str(strike),right,osi]
    mapping=inp.get('mapping');mapped=None;provenance=None
    if isinstance(mapping,dict):
        required=('mapping_id','source_ref','from_product','to_instrument_id','known_at','mapped_price')
        if any(mapping.get(k) is None for k in required):missing.append('mapping_provenance')
        elif mapping['from_product']!=symbol:invalid.append('mapping_product')
        elif inp.get('use_at') is None or mapping['known_at']>inp['use_at']:invalid.append('mapping_availability')
        else:mapped=number(mapping['mapped_price']);provenance=deepcopy(mapping)
    elif mapping is not None:missing.append('mapping_provenance')
    v=dict(native_contract_key=key,is_0dte=zero,native_strike=strike,symbol=symbol,source_product_ok=product_ok,
           mapped_price=mapped,mapping_provenance=provenance,observation_date_et=observed_date,source_units=record.get('unit'),
           provenance={k:deepcopy(record.get(k)) for k in ('source_file','source_row','dataset_id','vintage_id') if record.get(k) is not None})
    return _result('O034',inp,v,missing=missing,invalid=invalid,known=_known(at,*([mapping['known_at']] if provenance else [])))


def o035(inp):
    flip,spot=number(inp.get('flip',inp.get('flip_value'))),number(inp.get('spot'));missing=[];invalid=[]
    if flip is None:missing.append('source_flip')
    if inp.get('unit') is None:missing.append('unit')
    if inp.get('spot_unit') is not None and inp.get('unit')!=inp['spot_unit']:invalid.append('unit_mismatch')
    diff=None if flip is None or spot is None else spot-flip
    v=dict(flip_value=flip,spot_minus_flip=diff,relation=None if diff is None else 'below' if diff<0 else 'above' if diff>0 else 'on',
           source_regime_interpretation=deepcopy(inp.get('source_regime_interpretation')),automatic_flip=None,regime_from_difference=False)
    known=_known(inp.get('flip_known_at',inp.get('known_at')),*([inp.get('spot_known_at')] if spot is not None else []))
    if known is None:missing.append('availability')
    return _result('O035',inp,v,missing=missing,invalid=invalid,known=known,supplied=True)


def o036(inp):
    walls=deepcopy(inp.get('walls',[]));spot=number(inp.get('spot'));missing=[];invalid=[];out=[];times=[]
    ids=[w.get('id') for w in walls]
    if not walls:missing.append('source_walls')
    if any(not x for x in ids) or len(ids)!=len(set(ids)):invalid.append('wall_identity')
    pain=inp.get('max_pain_id')
    if pain is not None and pain in ids:invalid.append('max_pain_alias')
    for wall in walls:
        px=number(wall.get('price'));band=wall.get('band')
        if px is None and band is None:missing.append('wall_value')
        if not wall.get('unit'):missing.append('wall_unit')
        if spot is not None and inp.get('spot_unit')!=wall.get('unit'):missing.append('spot_units')
        rel=None if spot is None or px is None or inp.get('spot_unit')!=wall.get('unit') else 'below' if spot<px else 'above' if spot>px else 'on'
        out.append({**wall,'price':px,'spot_relation':rel})
        times.append(wall.get('known_at',inp.get('known_at')))
    selected=inp.get('selected_wall_id')
    if selected is not None and selected not in ids:invalid.append('selected_wall_identity')
    known=_known(*times,*([inp.get('spot_known_at')] if spot is not None else [])) if times else None
    v=dict(walls=out,wall_ids=ids,max_pain_id=pain,distinct_ids=len(set(ids+([pain] if pain else []))),
           spot_relation={w['id']:w['spot_relation'] for w in out},selected_wall_id=selected,automatic_walls=None)
    return _result('O036',inp,v,missing=missing,invalid=invalid,known=known,supplied=True)


def o037(inp):
    value=number(inp.get('max_pain'));wall=number(inp.get('put_wall'));identity=inp.get('max_pain_id');wid=inp.get('put_wall_id');missing=[];invalid=[]
    if value is None:missing.append('source_max_pain')
    if identity is None:missing.append('max_pain_identity')
    if identity is not None and identity==wid:invalid.append('wall_alias')
    diff=None if value is None or wall is None else value-wall
    v=dict(max_pain_value=value,source_known=None if missing else True,identity=identity,
           relation_to_separate_walls=[] if wall is None else [{'wall_id':wid,'difference':diff,'equal_price':value==wall,'same_identity':False}],
           difference=None if diff is None else abs(diff),equal_put_wall=None if diff is None else diff==0,
           automatic_max_pain=None,predicted_terminal=None)
    return _result('O037',inp,v,missing=missing,invalid=invalid,known=_known(inp.get('known_at'),*([inp.get('wall_known_at')] if wall is not None else [])),supplied=True)


def _readout(inp,rid,input_name,output_name,automatic_name):
    val=number(inp.get(input_name));unit=inp.get('unit',inp.get('scale'));missing=[]
    if val is None:missing.append(input_name)
    if unit is None:missing.append('scale' if rid=='O040' else 'unit')
    at=inp.get('available_at',inp.get('known_at'))
    if at is None:missing.append('availability')
    v={output_name:val,'unit':unit,'interpretation':deepcopy(inp.get('interpretation',inp.get('source_interpretation'))),automatic_name:None}
    if rid=='O038':v['computed_is_not_source']=True
    if rid=='O039':v.update(faithful_value=val if not missing else None,computed_comparison=number(inp.get('computed')))
    if rid=='O040':v.update(scale=unit,as_percent=val if unit=='percent' else None,source_interpretation=v['interpretation'] if unit else None,entry_permission=None)
    return _result(rid,inp,v,missing=missing,known=at,supplied=True)


def o038(inp):return _readout(inp,'O038','source_value','source_value','automatic_value')
def o039(inp):return _readout(inp,'O039','source_vol_gex','source_vol_gex','automatic_value')
def o040(inp):return _readout(inp,'O040','gauge','gauge_value','automatic_pressure')


def o041(inp):
    kg=inp.get('kg1');missing=[];invalid=[]
    if kg is None:missing.append('source_kg1')
    band=None if kg is None else [number(kg[0]),number(kg[1])] if isinstance(kg,(list,tuple)) else [number(kg),number(kg)]
    if band is not None and band[0]>band[1]:invalid.append('reversed_band')
    if not inp.get('kg1_id'):missing.append('kg1_identity')
    if inp.get('known_at') is None:missing.append('availability')
    ids=[inp[k] for k in ('kg1_id','hvn_id','reaction_id') if inp.get(k)]
    if len(ids)!=len(set(ids)):invalid.append('distinct_object_identity')
    # Independent reasons require their actual records, never KG1+HVN ID arithmetic.
    reasons=inp.get('reason_records',[])
    eligible={r.get('role'):r for r in reasons if r.get('object_id') and r.get('evidence_ids') and r.get('known_at') is not None and inp.get('use_at') is not None and r['known_at']<=inp['use_at']}
    two=None
    if {'prior_reaction','minor_hvn'}<=eligible.keys():
        two=eligible['prior_reaction']['object_id']!=eligible['minor_hvn']['object_id']
    v=dict(kg1_band=band,kg1=band,source_known=None if missing else not invalid,role=inp.get('role'),automatic_kg1=None,ids=ids,id_count=len(ids),two_reason_ok=two)
    return _result('O041',inp,v,missing=missing,invalid=invalid,
                   known=_known(inp.get('known_at'),*(r['known_at'] for r in eligible.values())),supplied=True)


def _available_context(inp,rid,name):
    use=inp.get('use_at');rows=deepcopy(inp.get('observations',[]));missing=[];invalid=[]
    if not rows:
        rows=[{'value':inp.get(name),'available_at':inp.get('publication_at' if name=='vix' else 'available_at'),'observation_at':inp.get('observation_at'),'unit':inp.get('unit'),'source_context':inp.get('source_context'),'source_interpretation':inp.get('source_interpretation')}]
    eligible=[]
    for r in rows:
        at=r.get('available_at',r.get('publication_at'));value=number(r.get('value',r.get(name)))
        if at is None or value is None:continue
        if use is None:continue
        if at>use:continue
        if r.get('observation_at') is not None and r['observation_at']>at:invalid.append('availability_before_observation');continue
        if at<=use:eligible.append({**r,'available_at':at,'value':value})
    if not eligible:missing.append('verified_available_observation')
    latest=max((r['available_at'] for r in eligible),default=None)
    batch=[r for r in eligible if r['available_at']==latest]
    if len({(str(r['value']),r.get('unit')) for r in batch})>1:missing.append('conflicting_vintage_tie');chosen=None
    else:chosen=batch[0] if batch else None
    value=chosen['value'] if chosen else None
    v={f'available_{name}':value,'observation_at':chosen.get('observation_at') if chosen else None,
       'available_at':latest if chosen else None,'age_ns':use-latest if use is not None and latest is not None else None,
       'source_context':chosen.get('source_context') if chosen else None,'source_interpretation':chosen.get('source_interpretation') if chosen else None,
       'ambition_adjustment':inp.get('ambition_adjustment'),'usable':None if chosen is None else True,'automatic_entry_rule':None,'entry_permission':None,
       'unit':chosen.get('unit') if chosen else None,'selected_observation':chosen}
    if name=='vix':v.update(usable_vix=value,faithful_preopen=None if chosen is None else True,later_vix_used=False,later_available=inp.get('later_at') is not None and use is not None and inp['later_at']<=use)
    else:v['vvix']=value
    return _result(rid,inp,v,missing=missing,invalid=invalid,known=latest if chosen else None)


def o042(inp):return _available_context(inp,'O042','vix')
def o045(inp):return _available_context(inp,'O045','vvix')


def o043(inp):
    vix=number(inp.get('vix'));price=number(inp.get('P'));missing=[];invalid=[]
    if vix is None:missing.append('vix')
    elif vix<0:invalid.append('negative_vix')
    pct=None if vix is None else vix/Decimal(252).sqrt()
    fraction=None if pct is None else pct/100
    if price is not None and price<=0:invalid.append('conversion_price')
    points=None if price is None or fraction is None else price*fraction
    if price is not None and not inp.get('conversion_instrument_id'):missing.append('price_identity')
    known=_known(inp.get('vix_known_at',inp.get('known_at')),*([inp.get('price_known_at')] if price is not None else []))
    v=dict(daily_move_percent=pct,percent=pct,daily_fraction=fraction,point_estimate=points,must_travel=False,
           conversion_instrument_id=inp.get('conversion_instrument_id'),vix_unit='percentage_points',estimate_unit='points')
    return _result('O043',inp,v,missing=missing,invalid=invalid,known=known)


def o044(inp):
    rows=deepcopy(inp.get('tenor_values',[]));missing=[];invalid=[]
    if not rows:
        rows=[{'tenor':inp.get('near_name'),'value':inp.get('near'),'unit':inp.get('unit'),'known_at':inp.get('near_known_at')},
              {'tenor':inp.get('far_name'),'value':inp.get('far'),'unit':inp.get('unit'),'known_at':inp.get('far_known_at')}]
    if len(rows)!=2:missing.append('selected_tenor_pair')
    for r in rows:
        r['value']=number(r.get('value'))
        if any(r.get(k) is None for k in ('tenor','value','unit','known_at')):missing.append('tenor_identity_or_availability')
    if len(rows)==2 and rows[0].get('unit')!=rows[1].get('unit'):invalid.append('tenor_unit_mismatch')
    if len(rows)==2 and rows[0].get('tenor') is not None and rows[0]['tenor']==rows[1].get('tenor'):invalid.append('duplicate_tenor')
    a,b=(r['value'] for r in rows) if len(rows)==2 else (None,None)
    operation=inp.get('operation');difference=ratio=None
    if operation not in {'difference','ratio','both'}:missing.append('selected_comparison')
    if a is not None and b is not None:
        if operation in {'difference','both'}:difference=b-a
        if operation in {'ratio','both'}:ratio=None if a==0 else b/a
    change=None;post=number(inp.get('post_near'));post_at=inp.get('post_at');use=inp.get('use_at')
    post_ok=post_at is not None and use is not None and post_at<=use
    times=[r.get('known_at') for r in rows]
    if post is not None and post_ok:
        if a is not None:change=post-a
        times.append(post_at)
    v=dict(tenor_values=rows,difference_or_ratio_when_selected={'operation':operation,'difference':difference,'ratio':ratio},
           difference=difference,far_over_near=ratio,event_change=change,change=change,post_available=post_ok,
           source_curve_label=inp.get('source_curve_label'),interpretation=inp.get('interpretation'))
    return _result('O044',inp,v,missing=missing,invalid=invalid,known=_known(*times))


REGISTRATION_OVERRIDES={f'O{n:03}':globals()[f'o{n:03}'] for n in range(30,46)}
REQUIRED_INPUTS={rid:() for rid in REGISTRATION_OVERRIDES}
NUM=F((Decimal,),True);TEXT=F((str,),True);TIME=F((int,),True);BOOL=F((bool,),True);NULL=F((type(None),),True)
OUTPUT_SCHEMAS={
 'O030':{**{k:NUM for k in ('sum_v','sum_pv','vwap')},'reset_id':TEXT,'basis':TEXT,'as_of':TIME,'known_at':TIME,'member_event_ids':F((list,))},
 'O031':{'anchor_id':TEXT,'anchor_price_at':TIME,'anchor_known_at':TIME,'avwap':NUM,'as_of':TIME,'usable_at':TIME,'sum_v':NUM,'sum_pv':NUM},
 'O032':{'upper':NUM,'lower':NUM,'band_id':TEXT,'variance_convention':TEXT,'as_of':TIME},
 'O033':{'source_regime':TEXT,'branch_regime_ok':BOOL,'native_identity_ok':BOOL,'reread_at':TIME},
 'O034':{'native_contract_key':F((list,),True),'is_0dte':BOOL,'native_strike':NUM,'source_product_ok':BOOL,'mapped_price':NUM,'mapping_provenance':F((dict,),True)},
 'O035':{'flip_value':NUM,'spot_minus_flip':NUM,'relation':TEXT,'source_regime_interpretation':F((str,dict),True)},
 'O036':{'walls':F((list,)),'spot_relation':F((dict,)),'selected_wall_id':TEXT,'automatic_walls':NULL},
 'O037':{'max_pain_value':NUM,'source_known':BOOL,'relation_to_separate_walls':F((list,)),'automatic_max_pain':NULL},
 'O038':{'source_value':NUM,'unit':TEXT,'interpretation':F((str,dict),True),'automatic_value':NULL},
 'O039':{'source_vol_gex':NUM,'unit':TEXT,'interpretation':F((str,dict),True),'automatic_value':NULL},
 'O040':{'gauge_value':NUM,'source_interpretation':F((str,dict),True),'automatic_pressure':NULL},
 'O041':{'kg1_band':F((list,),True),'source_known':BOOL,'role':TEXT,'automatic_kg1':NULL},
 'O042':{'available_vix':NUM,'observation_at':TIME,'source_context':F((str,dict),True),'ambition_adjustment':F((str,dict),True)},
 'O043':{'daily_move_percent':NUM,'daily_fraction':NUM,'point_estimate':NUM},
 'O044':{'tenor_values':F((list,)),'difference_or_ratio_when_selected':F((dict,)),'event_change':NUM,'source_curve_label':TEXT},
 'O045':{'available_vvix':NUM,'source_interpretation':F((str,dict),True),'automatic_entry_rule':NULL},
}

# Retain every membership/variance/availability quantity used by later objects
# and method admission. A schema containing just the scalar VWAP is incomplete.
_VWAP_SCHEMA={**{k:NUM for k in ('sum_v','sum_pv','sum_p2v','weighted_variance_population','vwap','comparison_vwap','vwap_at_retest')},
 'reset_id':TEXT,'reset_at':TIME,'basis':TEXT,'as_of':TIME,'known_at':TIME,'vwap_known_at':TIME,
 'member_event_ids':F((list,)),'faithful':BOOL,'variant':TEXT,'vwap_reset_verified':BOOL,'source_vwap_known':BOOL,'automatic_reset':NULL}
OUTPUT_SCHEMAS['O030']=_VWAP_SCHEMA
OUTPUT_SCHEMAS['O031']={**_VWAP_SCHEMA,'anchor_id':TEXT,'anchor_price_at':TIME,'anchor_known_at':TIME,
 'anchor_selected_at':TIME,'anchor_reason':TEXT,'avwap':NUM,'usable_at':TIME,'usable':BOOL}


def _catalog_setting_matches(config, key, expected):
    """A caller's verification Boolean cannot establish a source setting."""
    from ..source_config import load_catalog, SourceSetting
    cfg=load_catalog()['configurations'].get(config.get('source_configuration_id'))
    if cfg is None or cfg.get('version')!=config.get('source_configuration_version'):
        return False
    setting=cfg.get('settings',{}).get(key)
    return setting is not None and SourceSetting.parse(setting).status=='fact' and SourceSetting.parse(setting).resolve()==expected


def native_vwap(config,resolved,*,anchored=False):
    # Observed scalars and member arrays in config are intentionally discarded.
    setting_keys={'as_of','reset_at','reset_id','reset_verified','basis','anchor_price_at','anchor_id','anchor_known_at','anchor_selected_at','anchor_reason','touch_at','source_includes_contact_trade','variant','source_basis_verified','use_at'}
    inp={k:deepcopy(v) for k,v in config.items() if k in setting_keys}
    if config.get('variant') != 'comparison':
        inp['source_basis_verified']=_catalog_setting_matches(config,'price_basis',config.get('basis'))
        if not anchored:
            inp['reset_verified']=_catalog_setting_matches(config,'reset',config.get('reset_at'))
    inp['instrument_id']=resolved.instrument_id
    if anchored and config.get('variant') != 'comparison':
        from ..native_resolution import NativeEvidenceError
        parents=config.get('parents',{})
        parent=parents.get(config.get('anchor_parent_id'))
        if parent is None or parent.get('evidence_class') not in {'resolved_native','parent_derived','supplied_source_audit'}:
            raise NativeEvidenceError('source anchored VWAP requires its actual selected anchor parent')
        selector=config.get('anchor_selector')
        if selector=='formation_start':
            anchor_at=parent.get('formation_start')
        elif selector=='selected_event':
            anchor_at=parent['value'].get('anchor_price_at')
        else:
            raise NativeEvidenceError('anchor must select the declared formation start or identified source event')
        if anchor_at != resolved.start_ns:
            raise NativeEvidenceError('selected native anchor differs from resolved formation start')
        inp.update(anchor_id=parent['object_id'],anchor_price_at=anchor_at,
                   anchor_known_at=parent.get('known_at'),anchor_selected_at=parent.get('known_at'),
                   anchor_reason=f'{selector} of selected parent {parent["object_id"]}')
    reset=inp.get('anchor_price_at') if anchored else inp.get('reset_at')
    if reset != resolved.start_ns or inp.get('as_of',resolved.end_ns) != resolved.end_ns:
        from ..native_resolution import NativeEvidenceError
        raise NativeEvidenceError('VWAP formation must exactly match its resolved reset-to-snapshot window')
    rows=resolved.rows();datasets={r['dataset_id'] for r in rows}
    if len(datasets)!=1:raise ValueError('VWAP must use a single canonical tape')
    inp.update(canonical_tape_id=next(iter(datasets)),coverage_complete=resolved.coverage_ok)
    if inp.get('basis')=='trade_price':inp['trades']=rows
    else:
        inp['bars']=rows
        # Exact contiguous complete OHLC membership itself establishes bar coverage.
        from .native_boundary import _interval_coverage
        inp['coverage_complete']=kleene_and(resolved.coverage_ok,
            _interval_coverage(rows,resolved.start_ns,resolved.end_ns)[0])
    inp.setdefault('as_of',resolved.end_ns)
    if anchored:return o031(inp)
    return o030(inp)


NATIVE_PRODUCERS={'O030':lambda c,r:native_vwap(c,r),'O031':lambda c,r:native_vwap(c,r,anchored=True)}


def derived_vwap_band(config, parents):
    """Derive dispersion from the identical weighted parent membership.

    A caller's sigma or VWAP is never substituted. Undisclosed platform
    dispersion remains unknown unless a named comparison was selected.
    """
    from ..native_resolution import NativeEvidenceError
    matches=[p for p in parents if p['recipe_id'] in {'O030','O031'} and p['object_id']==config.get('vwap_parent_id')]
    if len(matches)!=1:raise NativeEvidenceError('deviation needs its explicit native VWAP snapshot parent')
    parent=matches[0];v=parent['value']
    if parent.get('evidence_class') not in {'resolved_native','parent_derived'}:
        raise NativeEvidenceError('deviation requires a computed membership-based VWAP')
    convention=config.get('variance_convention')
    variance=v.get('weighted_variance_population')
    usable=convention=='volume_weighted_population' and (config.get('variant')=='comparison' or
             _catalog_setting_matches(config,'variance_convention',convention))
    inp={k:deepcopy(config[k]) for k in ('band_id','k','touch_at','use_at') if k in config}
    mean=v.get('comparison_vwap') if config.get('variant')=='comparison' else v.get('vwap')
    inp.update(mu=mean,sigma=number(variance).sqrt() if usable and variance is not None else None,
      variance_convention=convention if usable else None,parent_snapshot_id=parent['object_id'],
      vwap_known_at=parent['known_at'],sigma_known_at=parent['known_at'],as_of=v['as_of'],
      reset_id=v.get('reset_id'),sigma_reset_id=v.get('reset_id'),
      weighting_universe=v.get('member_event_ids'),sigma_weighting_universe=v.get('member_event_ids'),
      coverage_complete=parent.get('recipe_coverage_ok'))
    result=o032(inp);result.value['variant']=config.get('variant','source')
    result.value['member_event_ids']=deepcopy(v.get('member_event_ids',[]))
    return result


DERIVED_PRODUCERS={'O032':derived_vwap_band}
