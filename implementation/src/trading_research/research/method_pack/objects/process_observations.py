"""Observed process outcomes, causal validation and native participation records.

No return series, Monte Carlo run, macro classifier or trading rule is created.
Numerical checks below reconcile supplied outcomes or native event quantities.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
from decimal import Decimal

from ..contracts import OutputField as F
from ..logic import kleene_and
from .context_observations import number, _known, _result


CATEGORIES={'win','loss','flat','open','censored','missing_result','miss','breach'}


def o153(inp):
    records=deepcopy(inp.get('outcomes',[]));missing=[];invalid=[];times=[]
    category_counts=Counter({k:0 for k in CATEGORIES});ids=[]
    process=inp.get('process_id');version=inp.get('process_version');cohort=inp.get('cohort_id')
    if records:
        for row in records:
            rid=row.get('outcome_id',row.get('attempt_id'));category=row.get('category',row.get('outcome'))
            if not rid or rid in ids:invalid.append('outcome_identity')
            else:ids.append(rid)
            if category not in CATEGORIES:invalid.append('outcome_category');continue
            category_counts[category]+=1
            if row.get('process_id')!=process or row.get('process_version')!=version:invalid.append('process_identity')
            at=row.get('known_at');times.append(at)
            if at is None:missing.append('outcome_availability')
            if category in {'win','loss','flat'}:
                if row.get('closed_at') is None:missing.append('closed_outcome_time')
                elif at is not None and row['closed_at']>at:invalid.append('availability_before_close')
    else:
        counts=inp.get('category_counts')
        if counts is None:
            counts={k:inp.get({'win':'wins','loss':'losses','flat':'flat'}.get(k,k),0) for k in CATEGORIES}
            if inp.get('wins') is None or inp.get('losses') is None:missing.append('denominator')
        for category,n in counts.items():
            if category not in CATEGORIES or type(n) is not int or n<0:invalid.append('outcome_count')
            else:category_counts[category]=n
        if not inp.get('supplied_summary_ref'):missing.append('supplied_summary_provenance')
        times=[inp.get('known_at')]
    for name,v in [('process_id',process),('process_version',version),('cohort_id',cohort)]:
        if not v:missing.append(name)
    convention=inp.get('closed_denominator')
    if convention not in {'win_loss','win_loss_flat'}:missing.append('closed_denominator')
    wins,losses,flats=(category_counts[k] for k in ('win','loss','flat'))
    n=wins+losses+(flats if convention=='win_loss_flat' else 0)
    # Literal comparison may remain useful with compact aggregate inputs; its
    # missing convention stays a hole and cannot certify process completeness.
    wr=None if n==0 else Decimal(wins)/n
    mw,ml=number(inp.get('mean_win')),number(inp.get('mean_loss'))
    if mw is not None and mw<0 or ml is not None and ml>0:invalid.append('outcome_sign')
    ev=None if n==0 or mw is None or ml is None else (wins*mw+losses*ml)/n
    gw=None if mw is None else wins*mw;gl=None if ml is None else abs(losses*ml)
    pf=None if gw is None or gl in (None,0) else gw/gl
    supplied=deepcopy(inp.get('reported_metrics',{}))
    if inp.get('reported_ev') is not None:supplied['ev']=inp['reported_ev']
    computed={'win_rate':wr,'ev':ev,'profit_factor':pf};checks=[];unavailable=[]
    for name,v in supplied.items():
        if name in computed and computed[name] is not None:checks.append(number(v)==computed[name])
        else:unavailable.append(name)
    consistency=kleene_and(*checks) if checks else None
    initial=deepcopy(inp.get('initial_R_provenance'))
    if initial is None:missing.append('initial_R_provenance')
    elif not all(initial.get(k) is not None for k in ('definition_id','known_at','unit')):missing.append('initial_R_definition')
    if isinstance(initial,dict):times.append(initial.get('known_at'))
    if inp.get('rebased_initial_R') is True:invalid.append('initial_R_rebased')
    corrections=deepcopy(inp.get('causal_corrections',[]))
    if inp.get('source_family') in {'Refill','OFM'} and not corrections:missing.append('causal_correction_provenance')
    for correction in corrections:
        if not isinstance(correction,dict) or correction.get('known_at') is None:
            missing.append('causal_correction_availability');times.append(None)
        else:times.append(correction['known_at'])
    v=dict(reported_metrics=supplied,denominator_identity={'process_id':process,'process_version':version,'cohort_id':cohort,
           'closed_convention':convention,'closed_n':n,'observed_record_ids':ids,'categories':dict(category_counts),'all_record_count':sum(category_counts.values())},
           initial_R_provenance=initial,summary_consistency=consistency,causal_correction_retained=bool(corrections),
           causal_corrections=corrections,unavailable_metrics=unavailable,win_rate=wr,ev=ev,profit_factor=pf,consistent=consistency,
           from_market_prices=False,new_return_series=False,outcome_records=records,
           aggregate_winner_loser_comparison_recorded=True if wins and losses and mw is not None and ml is not None and not missing and not invalid else None)
    return _result('O153',inp,v,missing=missing,invalid=invalid,known=_known(*times),supplied=True)


def o154(inp):
    record=deepcopy(inp.get('validation_record',inp));missing=[];invalid=[]
    sample=record.get('sample',[]);process=record.get('process_id');version=record.get('process_version')
    if not process:missing.append('process_id')
    if not version:missing.append('process_version')
    ids=[];times=[]
    for row in sample:
        rid=row.get('sample_id',row.get('attempt_id'))
        if not rid or rid in ids:invalid.append('sample_identity')
        else:ids.append(rid)
        if row.get('process_id')!=process or row.get('process_version')!=version:invalid.append('foreign_process_sample')
        if row.get('outcome') not in {'win','loss','flat'}:invalid.append('sample_not_closed')
        close=row.get('closed_at');known=row.get('known_at')
        if type(close) is not int or type(known) is not int:missing.append('sample_availability')
        elif known<close:invalid.append('sample_known_before_close')
        times.append(known)
    if not sample:missing.append('prior_closed_sample_records')
    declared=record.get('n');n=len(sample) if sample else declared
    if sample and declared is not None and declared!=len(sample):invalid.append('sample_count_mismatch')
    if type(n) is not int or n<0:missing.append('sample_n')
    if record.get('min_n',100)!=100:invalid.append('printed_minimum_is_100')
    wr=number(record.get('win_rate'));rr=number(record.get('avg_rr',record.get('average_rr')))
    if wr is None:missing.append('win_rate')
    elif not 0<=wr<=1:invalid.append('win_rate')
    if rr is None:missing.append('average_rr')
    elif rr<=0:invalid.append('average_rr')
    for field in ('win_rate_definition','average_rr_definition'):
        if not record.get(field):missing.append(field)
    counts=Counter(r.get('outcome') for r in sample)
    convention=record.get('closed_denominator','win_loss' if not counts['flat'] else None)
    if convention not in {'win_loss','win_loss_flat'}:missing.append('closed_denominator')
    denominator=counts['win']+counts['loss']+(counts['flat'] if convention=='win_loss_flat' else 0)
    observed_wr=Decimal(counts['win'])/denominator if denominator else None
    if sample and wr is not None and observed_wr is not None and wr!=observed_wr:
        invalid.append('win_rate_sample_mismatch')
    mc=record.get('monte_carlo');streak=None
    if not isinstance(mc,dict):missing.append('supplied_mc_design_and_result')
    else:
        streak=mc.get('max_loss_streak');times.append(mc.get('known_at'))
        if type(streak) is not int or streak<0:missing.append('mc_max_loss_streak')
        for key in ('design','source_ref','result_id','known_at'):
            if mc.get(key) is None or mc.get(key) == '':missing.append('mc_'+key)
        if mc.get('process_id')!=process or mc.get('process_version')!=version:invalid.append('mc_process_identity')
        if len(mc.get('sample_ids',[]))!=len(ids) or set(mc.get('sample_ids',[]))!=set(ids):invalid.append('mc_sample_identity')
    available=record.get('known_at');times.append(available);known=_known(*times)
    use=inp.get('use_at',record.get('risk_decision_at'))
    before=None if known is None or use is None else known<use
    if use is None:missing.append('risk_decision_at')
    if before is False:invalid.append('validation_not_prior')
    if record.get('same_process') is False:invalid.append('foreign_process_sample')
    if record.get('simulation_invented') is True:invalid.append('new_simulation')
    minimum=None if type(n) is not int else n>=100
    overlay=False if invalid or minimum is False else None if missing else True
    v=dict(sample_n=n,sample_at_least100=minimum,winrate_known=wr is not None,average_rr_known=rr is not None,
           mc_result_known=streak is not None,validation_before_risk=before,overlay_validation=overlay,
           win_rate=wr,average_rr=rr,mc_max_loss_streak=streak,simulation_run=False,sample_ids=ids,
           process_id=process,process_version=version,validation_record_id=record.get('validation_id'),
           observed_sample_win_rate=observed_wr,sample_outcome_counts=dict(counts),closed_denominator=convention,
           validation_record=record)
    return _result('O154',inp,v,missing=missing,invalid=invalid,known=known,supplied=True)


def _indicator_records(inp):
    records=deepcopy(inp.get('indicator_records',inp.get('available',[])));as_of=inp.get('as_of',inp.get('use_at'))
    eligible=[];missing=[];invalid=[];ids=[]
    for row in records:
        rid=row.get('series_id',row.get('id'));at=row.get('available_at',row.get('at'))
        if at is not None and as_of is not None and at>as_of:continue
        if rid is None or rid in ids:invalid.append('indicator_identity');continue
        ids.append(rid)
        if at is None:missing.append('vintage_availability');continue
        if as_of is None or at>as_of:continue
        if row.get('value') is None or not row.get('unit') or not row.get('vintage_id'):missing.append('indicator_value_unit_vintage')
        eligible.append({**row,'series_id':rid,'available_at':at})
    return eligible,missing,invalid


def o157(inp):
    records,missing,invalid=_indicator_records(inp)
    roles=inp.get('required_series');present=None
    if not isinstance(roles,dict) or not roles:missing.append('source_series_definition')
    else:
        actual={r['series_id'] for r in records};selected=set(roles.values())
        if not set(roles)<= {'leverage','credit_borrowing','housing','valuation'}:invalid.append('macro_role')
        records=[r for r in records if r['series_id'] in selected]
        if selected<=actual and not missing:present=True
        else:missing.append('required_series')
    count=len(records);expected=len(roles) if isinstance(roles,dict) else inp.get('required_n')
    v=dict(indicator_records=records,required_series_present=present,vintage_causal=None if missing else True,
           source_historical_verdict=deepcopy(inp.get('source_historical_verdict')),automatic_current_verdict=None,
           automatic_verdict=None,available_series_count=count,of=expected,later_replaces=False,
           macro_collection='deferred')
    return _result('O157',inp,v,missing=missing,invalid=invalid,known=_known(*(r['available_at'] for r in records)) if records else None,supplied=True)


def o158(inp):
    records,missing,invalid=_indicator_records(inp);label=inp.get('source_cycle_label')
    if label is None:missing.append('source_cycle_label')
    if not inp.get('rationale'):missing.append('source_rationale')
    if not records:missing.append('input_vintages')
    v=dict(source_cycle_label=label,rationale=deepcopy(inp.get('rationale')),inputs_available=None if missing else True,
           indicator_records=records,automatic_cycle=None,majority_vote=False)
    return _result('O158',inp,v,missing=missing,invalid=invalid,known=_known(inp.get('known_at'),*(r['available_at'] for r in records)),supplied=True)


def o159(inp):
    value=number(inp.get('c_score'));unit=inp.get('unit');missing=['custom_score_formula']
    if value is None:missing.append('source_c_score')
    if unit is None:missing.append('source_score_unit')
    v=dict(source_c_score=value,source_score_unit=unit,automatic_c_score=None,distinct=True,z_is_c=False,
           custom_score_formula=None,source_context=deepcopy(inp.get('source_context')))
    invalid=['z_score_substituted_for_custom_score'] if value is not None and inp.get('metric_kind') == 'z_score' else []
    return _result('O159',inp,v,missing=missing,invalid=invalid,known=inp.get('known_at'),supplied=True)


def o160(inp):
    rows=deepcopy(inp.get('baseline_records',[]));current=deepcopy(inp.get('current_record',{}));missing=[];invalid=[]
    x=number(current.get('value',inp.get('x')));times=[];ids=[];values=[]
    if x is None:missing.append('current_value')
    if rows:
        current_id=current.get('observation_id');current_time=current.get('observation_at');series=current.get('series_id')
        for r in rows:
            rid=r.get('observation_id');known=r.get('available_at');at=r.get('observation_at')
            if not rid or rid in ids or rid==current_id:invalid.append('baseline_identity')
            else:ids.append(rid)
            if r.get('series_id')!=series:invalid.append('baseline_series')
            if type(at) is not int or type(current_time) is not int:missing.append('baseline_observation_time')
            elif at>=current_time:invalid.append('nonprior_baseline')
            if type(known) is not int:missing.append('baseline_availability')
            times.append(known)
            values.append(number(r.get('value')))
        times.append(current.get('available_at'))
    else:
        values=[number(x) for x in inp.get('baseline',[])];missing.append('selected_baseline_records');times=[inp.get('known_at')]
    if not values or any(v is None for v in values):missing.append('baseline_values')
    convention=inp.get('convention');mean=sd=raw=z=None
    if values and all(v is not None for v in values):
        mean=sum(values,Decimal(0))/len(values);raw=None if x is None else x-mean
        if convention not in {'sample','population'}:missing.append('convention')
        elif convention=='sample' and len(values)<2:invalid.append('sample_size')
        else:
            divisor=len(values)-(convention=='sample');variance=sum(((v-mean)**2 for v in values),Decimal(0))/divisor
            sd=variance.sqrt();z=None if sd==0 or raw is None else raw/sd
    known=_known(*times)
    if known is None:missing.append('availability')
    v=dict(baseline_mean=mean,baseline_sd=sd,raw_deviation=raw,standardized_deviation=z,standardized=z,
           source_transform_known=None if missing else not invalid,baseline_ids=ids,baseline_count=len(values),convention=convention,
           zero_scale=sd==0 if sd is not None else None,author_exact_z=z if not missing and not invalid else None)
    return _result('O160',inp,v,missing=missing,invalid=invalid,known=known)


def o161(inp):
    val=number(inp.get('strength'));unit=inp.get('unit',inp.get('scale'));horizon=inp.get('horizon')
    missing=['source_strength_formula']
    for key,v in [('source_strength',val),('unit',unit),('horizon',horizon),('availability',inp.get('known_at'))]:
        if v is None:missing.append(key)
    v=dict(source_strength=val,horizon=horizon,unit=unit,scale=unit,automatic_strength=None,equivalent_to_slope=False,
           regression_slope=number(inp.get('regression_slope')))
    return _result('O161',inp,v,missing=missing,known=inp.get('known_at'),supplied=True)


def o162(inp):
    releases=deepcopy(inp.get('releases',[]));as_of=inp.get('as_of');series=inp.get('series_id');period=inp.get('reference_period')
    missing=[];invalid=[];history=[];seen=[];assumed=False;unknown_clock=False
    if not series:missing.append('series_id')
    if not period:missing.append('reference_period')
    if as_of is None:missing.append('as_of')
    for row in releases:
        if row.get('series_id')!=series or row.get('reference_period')!=period:continue
        at=row.get('available_at');released=row.get('released_at');vintage=row.get('vintage_at',released)
        if type(at) is not int and inp.get('release_as_availability') is True and type(released) is int and row.get('release_clock_source'):
            at=released;row['available_at']=at;assumed=True
        if type(at) is int and as_of is not None and at>as_of:continue
        if type(at) is not int:
            if type(released) is int and as_of is not None and released>as_of:continue
            missing.append('available_at');unknown_clock=True;continue
        if type(released) is not int:missing.append('released_at')
        elif at<released:invalid.append('available_before_release')
        if type(vintage) is int and vintage>at:invalid.append('available_before_vintage')
        if row.get('vintage_id') is None:missing.append('vintage_id')
        if row.get('value') is None or not row.get('unit'):missing.append('value_unit')
        history.append(row)
        if as_of is not None and at<=as_of:seen.append(row)
    policy=inp.get('vintage_policy');chosen=None
    if not seen:missing.append('vintage')
    elif policy not in {'latest_available','initial_release'}:missing.append('vintage_policy')
    else:
        at=(max if policy=='latest_available' else min)(r['available_at'] for r in seen)
        batch=[r for r in seen if r['available_at']==at]
        if len({(str(r.get('value')),r.get('unit'),r.get('vintage_id')) for r in batch})>1:missing.append('vintage_order')
        else:chosen=batch[0]
    literal=number(chosen['value']) if chosen is not None and not invalid and not unknown_clock else None
    value=literal if not missing and not assumed else None
    known=chosen['available_at'] if chosen else None
    v=dict(latest_available_vintage_at_decision=chosen.get('vintage_id') if chosen else None,
           reference_period=period,series_id=series,actual_value=value,value=literal,available_at=known,vintage_at=known,
           vintage_history=sorted(history,key=lambda r:r['available_at']),
           availability_assumption='verified_publication_as_availability' if assumed else None)
    if assumed:missing.append('observed_availability')
    return _result('O162',inp,v,missing=missing,invalid=invalid,known=known)


_ORDER_ACTIONS={'A':'add','add':'add','provide':'add','submit':'add','C':'cancel','cancel':'cancel','withdraw':'cancel','remove':'cancel',
                'E':'execute','F':'execute','execute':'execute','consume':'execute','fill':'execute','M':'modify','modify':'modify'}
_BOOK_SIDES={'B':'buy','bid':'buy','buy':'buy','A':'sell','ask':'sell','sell':'sell'}


def o163(inp):
    rows=deepcopy(inp.get('events',[]));orders={};seen_events=set();all_orders=set();missing=[];invalid=[];times=[];history=[]
    counts=Counter();totals={side:{action:Decimal(0) for action in ('provided','withdrawn','consumed')} for side in ('buy','sell')}
    previous_seq=previous_time=None
    if not rows:missing.append('native_lifecycle_log')
    for row in rows:
        at=row.get('event_ns',row.get('t'));known=row.get('known_at',at);seq=row.get('exchange_seq',row.get('exchange_sequence'))
        eid,oid=row.get('event_id'),row.get('order_id');action=_ORDER_ACTIONS.get(row.get('action',row.get('kind')));side=_BOOK_SIDES.get(row.get('side'))
        price,size=number(row.get('price')),number(row.get('size'));depth=row.get('depth_level')
        required=(eid,oid,at,known,seq,action,side,price,size,depth,row.get('instrument_id'))
        if any(v is None for v in required):missing.append('native_order_action_identity');continue
        if eid in seen_events:invalid.append('duplicate_event');continue
        seen_events.add(eid)
        if type(at) is not int or type(seq) is not int or type(known) is not int:invalid.append('event_time_or_sequence');continue
        if previous_seq is not None and seq<=previous_seq or previous_time is not None and at<previous_time:invalid.append('event_order')
        previous_seq,previous_time=seq,at
        if known<at:invalid.append('availability_before_event')
        if str(row['instrument_id'])!=str(inp.get('instrument_id')):invalid.append('instrument_identity')
        if type(depth) is not int or depth<1:invalid.append('depth_level')
        if size<0 or price<=0:invalid.append('price_quantity')
        if inp.get('start_ns') is not None and at<inp['start_ns'] or inp.get('end_ns') is not None and at>=inp['end_ns']:invalid.append('outside_interval')
        times.append(known)
        state=orders.get(oid)
        if action=='add':
            if oid in all_orders:invalid.append('reused_order_id');continue
            if size<=0:invalid.append('zero_add');continue
            all_orders.add(oid);orders[oid]=dict(side=side,price=price,remaining=size,instrument_id=row['instrument_id'])
            totals[side]['provided']+=size;counts['add']+=1
        elif state is None:missing.append('order_start_history');continue
        else:
            if state['side']!=side or state['price']!=price:invalid.append('order_side_price_identity');continue
            if action=='modify':
                new_size=number(row.get('new_quantity'));new_price=number(row.get('new_price',price))
                if new_size is None or new_price is None or new_size<0 or new_price<=0:invalid.append('modify_definition');continue
                old=state['remaining']
                if new_price!=price:
                    totals[side]['withdrawn']+=old;totals[side]['provided']+=new_size
                elif new_size>=old:totals[side]['provided']+=new_size-old
                else:totals[side]['withdrawn']+=old-new_size
                state.update(remaining=new_size,price=new_price);counts['modify']+=1
            else:
                if size<=0 or size>state['remaining']:invalid.append('lifecycle_quantity');continue
                state['remaining']-=size;totals[side]['withdrawn' if action=='cancel' else 'consumed']+=size;counts[action]+=1
        history.append({**row,'normalized_action':action,'normalized_side':side,'remaining':orders[oid]['remaining']})
    required_depth=inp.get('required_depth_levels');depth=inp.get('depth_coverage',inp.get('depth_levels'))
    if type(required_depth) is not int or required_depth<1:missing.append('required_depth_levels')
    if type(depth) is not int or depth<1 or type(required_depth) is int and depth<required_depth:missing.append('depth_coverage')
    if type(depth) is int and any(type(r.get('depth_level')) is int and r['depth_level']>depth for r in rows):invalid.append('outside_declared_depth')
    if inp.get('coverage_complete') is not True or inp.get('depth_complete') is not True:missing.append('complete_lifecycle_coverage')
    provided=sum((v['provided'] for v in totals.values()),Decimal(0));withdrawn=sum((v['withdrawn'] for v in totals.values()),Decimal(0));consumed=sum((v['consumed'] for v in totals.values()),Decimal(0))
    remaining=sum((o['remaining'] for o in orders.values()),Decimal(0))
    if provided-withdrawn-consumed!=remaining:invalid.append('quantity_reconciliation')
    v=dict(provide_events=counts['add'],withdraw_events=counts['cancel'],consume_events=counts['execute'],modify_events=counts['modify'],
           per_side_volumes=totals,depth_coverage=depth,required_depth_levels=required_depth,
           source_process_complete=False if invalid else None if missing else True,
           provided=provided,withdrawn=withdrawn,consumed=consumed,remaining=remaining,
           order_states=orders,event_ledger=history,native_event_ids=list(seen_events),native_event_count=len(history),
           source_symbol=inp.get('source_symbol'),snapshot_reconstruction=False,all_unknown=not history,
           two_sided_executions=bool(totals['buy']['consumed'] and totals['sell']['consumed']) if not missing and not invalid else None)
    return _result('O163',inp,v,missing=missing,invalid=invalid,known=_known(*times) if times else None,coverage=True if not missing else None)


def o164(inp):
    events=deepcopy(inp.get('events',[]));start=inp.get('start_ns');end=inp.get('end_ns');side=inp.get('side');basis=inp.get('response_basis');missing=[];invalid=[]
    direction={'long':1,'buy':1,'short':-1,'sell':-1}.get(side)
    if direction is None:missing.append('direction')
    if start is None or end is None:missing.append('interval')
    elif start>=end:invalid.append('interval')
    selected=[];times=[];volume=unknown=Decimal(0);seen=set()
    for r in events:
        at=r.get('event_ns',r.get('t'));known=r.get('known_at',at)
        if at is None:missing.append('event_time');continue
        if start is None or end is None or not start<=at<end:continue
        if known is None or known<at:missing.append('event_availability');continue
        if r.get('event_id') in seen:invalid.append('duplicate_event');continue
        if r.get('event_id') is None:missing.append('event_identity')
        else:seen.add(r['event_id'])
        if str(r.get('instrument_id'))!=str(inp.get('instrument_id')):invalid.append('instrument_identity')
        selected.append({**r,'event_ns':at,'known_at':known});times.append(known)
        if r.get('action','T')!='T':continue
        size=number(r.get('size',r.get('executed_size')))
        if size is None or size<0:invalid.append('execution_size');continue
        aggressor=r.get('aggressor',{'B':'buy','A':'sell','N':'unknown'}.get(r.get('side'),'unknown'))
        if aggressor=='unknown':unknown+=size
        if inp.get('effort_side')=='total' or aggressor==('buy' if direction==1 else 'sell'):volume+=size
    if inp.get('coverage_complete') is not True:missing.append('coverage')
    price_rows=[r for r in selected if r.get('action','T')=='T'] if basis=='trade_price' else [r for r in selected if r.get('bid') is not None and r.get('ask') is not None] if basis=='mid' else []
    if basis not in {'trade_price','mid'}:missing.append('response_basis')
    response=None
    if price_rows:
        sequence=lambda r:r.get('exchange_seq',r.get('exchange_sequence'))
        price_rows.sort(key=lambda r:(r['event_ns'],sequence(r) if type(sequence(r)) is int else 0));first,last=price_rows[0],price_rows[-1]
        def price(row):return number(row['price']) if basis=='trade_price' else (number(row['bid'])+number(row['ask']))/2
        for at in {first['event_ns'],last['event_ns']}:
            batch=[r for r in price_rows if r['event_ns']==at]
            if len({price(r) for r in batch})>1:
                seq=[sequence(r) for r in batch]
                if any(type(s) is not int for s in seq) or len(set(seq))!=len(seq):missing.append('response_endpoint_order')
        if 'response_endpoint_order' not in missing and direction is not None:response=direction*(price(last)-price(first))
    else:missing.append('response_observations')
    tick=number(inp.get('instrument_tick_size'));ticks=None if response is None or tick is None or tick<=0 else response/tick
    if tick is None:missing.append('instrument_definition')
    elif tick<=0:invalid.append('tick_size');ticks=None
    if unknown and inp.get('effort_side')!='total':missing.append('unknown_aggressor_effort')
    ratio=None if response is None or volume==0 else response/volume
    v=dict(aggressive_volume=volume,unknown_side_volume=unknown,price_response_points=response,price_response_ticks=ticks,
           mid_response=response if basis=='mid' else None,named_response_per_volume=ratio,response_per_volume=ratio,
           source_efficiency_class=deepcopy(inp.get('source_class')),automatic_class=None,absorption=None,
           interval={'start':start,'end':end},response_basis=basis,effort_side=inp.get('effort_side',side),
           member_event_ids=[r.get('event_id') for r in selected],opposing_liquidity_observation=deepcopy(inp.get('opposing_liquidity_observation')),
           response_record_complete=False if invalid else None if missing else True)
    return _result('O164',inp,v,missing=missing,invalid=invalid,known=_known(*times,end) if times else None,coverage=inp.get('coverage_complete'))


REGISTRATION_OVERRIDES={f'O{n:03}':globals()[f'o{n:03}'] for n in (153,154,*range(157,165))}
REQUIRED_INPUTS={rid:() for rid in REGISTRATION_OVERRIDES}
NUM=F((Decimal,),True);TEXT=F((str,),True);TIME=F((int,),True);BOOL=F((bool,),True);NULL=F((type(None),),True)
OUTPUT_SCHEMAS={
 'O153':{'reported_metrics':F((dict,)),'denominator_identity':F((dict,)),'initial_R_provenance':F((dict,),True),'summary_consistency':BOOL,'causal_correction_retained':F((bool,)),'unavailable_metrics':F((list,))},
 'O154':{'sample_n':F((int,),True),**{k:BOOL for k in ('sample_at_least100','winrate_known','average_rr_known','mc_result_known','validation_before_risk','overlay_validation')}},
 'O157':{'indicator_records':F((list,)),'required_series_present':BOOL,'vintage_causal':BOOL,'source_historical_verdict':F((str,dict),True),'automatic_current_verdict':NULL},
 'O158':{'source_cycle_label':TEXT,'rationale':F((str,dict),True),'inputs_available':BOOL,'automatic_cycle':NULL},
 'O159':{'source_c_score':NUM,'source_score_unit':TEXT,'automatic_c_score':NULL,'custom_score_formula':NULL},
 'O160':{**{k:NUM for k in ('baseline_mean','baseline_sd','raw_deviation','standardized_deviation')},'source_transform_known':BOOL},
 'O161':{'source_strength':NUM,'horizon':TEXT,'unit':TEXT,'automatic_strength':NULL},
 'O162':{'latest_available_vintage_at_decision':TEXT,'reference_period':TEXT,'actual_value':NUM,'available_at':TIME,'vintage_history':F((list,))},
 'O163':{**{k:F((int,),True) for k in ('provide_events','withdraw_events','consume_events')},'per_side_volumes':F((dict,)),'depth_coverage':F((int,),True),'source_process_complete':BOOL},
 'O164':{**{k:NUM for k in ('aggressive_volume','price_response_points','price_response_ticks','mid_response','named_response_per_volume')},'source_efficiency_class':TEXT},
}
OUTPUT_SCHEMAS['O153'].update(outcome_records=F((list,)),aggregate_winner_loser_comparison_recorded=BOOL)
OUTPUT_SCHEMAS['O154'].update(validation_record=F((dict,)),observed_sample_win_rate=NUM,
                             sample_outcome_counts=F((dict,)),closed_denominator=TEXT)
OUTPUT_SCHEMAS['O163'].update(two_sided_executions=BOOL,event_ledger=F((list,)),order_states=F((dict,)))
OUTPUT_SCHEMAS['O164'].update(response_record_complete=BOOL,interval=F((dict,)),response_basis=TEXT,
                            member_event_ids=F((list,)),unknown_side_volume=NUM,effort_side=TEXT)


def native_o163(config,resolved):
    """Retain executed consumption without inventing order-book lifecycles.

    B/A describes the aggressor in this acquired tape. Consumption at the
    passive book side is the opposite side; N cannot identify that side.
    Neither executions nor BBO snapshots identify hidden reserves or a full
    add/cancel/order-state history.
    """
    from .local_flow import o098
    tape=o098(dict(events=resolved.rows(),instrument_id=resolved.instrument_id,
                    start_ns=resolved.start_ns,end_ns=resolved.end_ns,
                    coverage_complete=resolved.coverage_ok,use_at=config.get('use_at')))
    values=tape.value
    buy,sell,unknown=(values[key] for key in ('buy','sell','unknown'))
    ledger=[]
    for row in values['event_records']:
        aggressor=row.get('aggressor',row.get('side'))
        passive={'buy':'sell','sell':'buy','B':'sell','A':'buy'}.get(aggressor)
        ledger.append({**deepcopy(row),'normalized_action':'execute',
                       'passive_book_side':passive,'order_id':None})
    two_sided=(True if buy>0 and sell>0 else
               False if unknown==0 and resolved.coverage_ok is True else None)
    value=dict(provide_events=None,withdraw_events=None,consume_events=len(ledger),modify_events=None,
        per_side_volumes={'buy':{'provided':None,'withdrawn':None,'consumed':sell},
                         'sell':{'provided':None,'withdrawn':None,'consumed':buy}},
        executed_by_aggressor={'buy':buy,'sell':sell,'unknown':unknown},
        unknown_consumed_side_volume=unknown,depth_coverage=None,required_depth_levels=None,
        source_process_complete=None,provided=None,withdrawn=None,consumed=values['total'],remaining=None,
        order_states={},event_ledger=ledger,native_event_ids=[row['event_id'] for row in ledger],
        native_event_count=len(ledger),source_symbol=None,snapshot_reconstruction=False,
        all_unknown=not ledger,two_sided_executions=two_sided,
        observation_scope='executed_consumption_only',per_side_volume_axis='passive_book_side')
    result=_result('O163',config,value,missing=['native_order_add_cancel_history','full_depth_coverage'],
        known=_known(tape.known_at,resolved.end_ns),coverage=resolved.coverage_ok)
    result.base_ok=tape.base_ok
    result.hole_ids=list(dict.fromkeys(result.hole_ids+tape.hole_ids))
    if tape.base_ok is False:result.state='invalid'
    return result


def native_o164(config,resolved):
    settings={k:deepcopy(v) for k,v in config.items() if k in ('side','effort_side','response_basis','use_at')}
    definition=getattr(resolved,'instrument_definition',None)
    if definition is not None:tick=definition.get('tick_size') if isinstance(definition,dict) else definition.tick_size
    else:tick=None
    settings.update(events=resolved.rows(),instrument_id=resolved.instrument_id,start_ns=resolved.start_ns,end_ns=resolved.end_ns,
                    coverage_complete=resolved.coverage_ok,instrument_tick_size=tick)
    return o164(settings)


NATIVE_PRODUCERS={'O163':native_o163,'O164':native_o164}
