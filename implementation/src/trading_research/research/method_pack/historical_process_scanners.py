"""Research/process interfaces, native participation and immutable refill zones."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime,timezone
from decimal import Decimal as D
from functools import lru_cache
import json
from pathlib import Path

from .historical_features import Q, MINUTE, SECOND, sign, pivots, first_contact
from .historical_assembly import HistoricalEpisode, absent, window_result
from .historical_flow import batches
from .branch_coverage import setting
from .catalog import PRIMARY
from .contracts import fields_for
from .empirical_protocol import content_hash
from .event_time import BookObservations
from .native_resolution import file_digest, NativeEvidenceError
from .macro_backfill import releases_for_decision


def scan_refill(m,branch):
    if branch!='touch_record':return scan_supplied_unit(m,'REFILL-STUDY',branch,extra=False)
    from .empirical_tape import m09_research_comparison
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
            'label_uses_only_post_touch_observations':True},operation='existing immutable nonoverlapping large-execution-pair state machine; exact departure/return and earlier resolved memory',
            parents=ref['formation_event_ids'],known_at=at,assumption='A2-REFILL')
        e.stage('zone_formation',ref['known_at'],observed=True).stage('departure',ref.get('departure_at'),observed=True)
        e.stage('distinct_return',opp['occurrence_start'],observed=True)
        out=e.finish(decision_at=at,entry=D(str(trigger['price'])))
        out['refill_response']=replay;out['prior_resolved_memory']=old
        episodes.append(out)
        # Label stays outside the input ledger. Only a later opportunity may
        # consume it after its independently measured resolution time.
        resolved=replay.get('completed_at',replay.get('completion_at',opp['expiry_at']))
        prior_by_zone[opp['reference_id']].append({'id':opp['opportunity_id'],'resolved_at':resolved,'verdict':replay.get('verdict')})
    out=window_result(m,'REFILL-STUDY',branch,episodes)
    out['zone_formation_count']=len(result['zones']);out['formation_ambiguities']=result['ambiguities']
    out['native_execution_members']=result['physical_member_count']
    return out


def scan_scalp(m,branch):
    side='short' if branch=='bearish_small_scalp' else 'long';sg=sign(side)
    end=m.at('09:30') if side=='short' else m.at('10:00')
    start=m.at('06:00') if side=='short' else m.at('09:00')
    ps=pivots(m.bars(start,end,60))
    impulse=None
    for a,b in zip(ps,ps[1:]):
        if a['side']==('high' if side=='short' else 'low') and b['side']==('low' if side=='short' else 'high') and sg*(b['price']-a['price'])>0:
            impulse=(a,b)
    if impulse is None:return window_result(m,'GB-SCALP',branch,[],omissions=[{'reason':'no confirmed directional impulse in declared pre-entry context','kind':'measured_selection'}])
    a,b=impulse;lo=min(a['price'],b['price']);hi=max(a['price'],b['price']);eq=(lo+hi)/2
    trigger=first_contact(m.bars(max(end,b['known_at']),m.end),eq,hi if side=='short' else eq) if side=='short' else first_contact(m.bars(max(end,b['known_at']),m.end),lo,eq)
    if trigger is None:return window_result(m,'GB-SCALP',branch,[])
    ref={'id':a['id']+'>'+b['id'],'low':lo,'high':hi,'known_at':b['known_at'],'impulse':list(impulse)}
    records=m.supplied('scalp_process',trigger['known_at']);record=records[-1] if records else None
    e=HistoricalEpisode(m,'GB-SCALP',branch,side,trigger,ref)
    e.bind({'direction_recorded_before_entry':b['known_at']<=trigger['start'],
        'source_directional_pullback_observed':trigger['H']>=eq if side=='short' else trigger['L']<=eq,
        'small_size_recorded':None if record is None else D(str(record['quantity']))<=D(str(record['small_quantity_limit'])),
        'source_scalp_management_recorded':None if record is None else bool(record.get('management_actions'))},
        operation='completed same-direction swing impulse and later premium/discount pullback; actual supplied small-exposure record only',
        parents=[a['id'],b['id']],known_at=trigger['known_at'],assumption='A2-CONTEXT')
    e.stage('prior_direction',b['known_at'],observed=True).stage('directional_pullback',trigger['known_at'],observed=True)
    out=e.finish(decision_at=trigger['known_at'])
    out['automatic_entry_admission']=None;out['observation_unit']='directional_pullback_and_process_record'
    return window_result(m,'GB-SCALP',branch,[out])


@lru_cache(maxsize=1)
def admitted_macro():
    root=Path('/workspace/implementation/reports/phase1-live/macro-backfill')
    verification=json.loads((root/'verification.json').read_text());rows=[];receipts=[]
    for bundle in verification['bundles']:
        path=Path(bundle['normalized_manifest'])
        if file_digest(path)!=bundle['normalized_manifest_sha256']:raise NativeEvidenceError('macro manifest changed')
        manifest=json.loads(path.read_text());receipts.append({'path':str(path),'sha256':file_digest(path)})
        for member in manifest['artifacts']:
            if not member['path'].endswith('.jsonl'):continue
            artifact=path.parent/member['path']
            if file_digest(artifact)!=member['sha256']:raise NativeEvidenceError('macro normalized artifact changed')
            receipts.append({'path':str(artifact),'sha256':member['sha256']})
            rows.extend(json.loads(line) for line in artifact.read_text().splitlines())
    byid={}
    for row in rows:
        if row['vintage_id'] in byid and row!=byid[row['vintage_id']]:raise NativeEvidenceError('conflicting macro vintage identity')
        byid[row['vintage_id']]=row
    return list(byid.values()),receipts


def macro_at(m,at):
    rows,receipts=admitted_macro();observations=[]
    for series in ('CPIAUCSL','PAYEMS'):
        periods=sorted({r['reference_period'] for r in rows if r['series_id']==series})
        values=[]
        for period in periods:
            releases=releases_for_decision(rows,series,period,at,initial_only=True)
            normalized=[{**r,'unit':r['units']} for r in releases]
            result=m.domain('O162',{'series_id':series,'reference_period':period,'as_of':at,
                'release_as_availability':True,'vintage_policy':'initial_release','releases':normalized})
            if result.get('value') is not None and result.get('available_at') is not None:
                values.append({'observation_id':result['latest_available_vintage_at_decision'],'series_id':series,
                    'value':D(str(result['value'])),'available_at':result['available_at'],
                    'observation_at':int(datetime.fromisoformat(period).replace(tzinfo=timezone.utc).timestamp()*SECOND),
                    'reference_period':period,'availability_assumption':result['availability_assumption']})
        values.sort(key=lambda r:r['observation_at'])
        count=setting('macro')['standardization_prior_values']
        current=values[-1] if values else None;prior=values[-count-1:-1]
        comparison=m.domain('O160',{'current_record':current or {},'baseline_records':prior,'convention':'sample','known_at':at})
        observations.append({'series_id':series,'current':current,'baseline':prior,'comparison':comparison,
            'comparison_history_complete':len(prior)==count,'source_custom_cycle':None,'source_C_score':None})
    inferred=None
    if getattr(m,'reconstruct',False):
        from .strategy_context import inferred_macro
        inferred=inferred_macro(observations)
    # Daily ALFRED context remains usable as a date-vintage record, without an
    # invented timestamp. It never enters the intraday source indicator gate.
    day=str(m.day)
    daily={series:sum(r['realtime_start']<=day<=r['realtime_end'] for r in rows if r['series_id']==series)
        for series in sorted({r['series_id'] for r in rows}) if series not in {'CPIAUCSL','PAYEMS'}}
    m.input_receipts.extend(receipts)
    return {'initial_publication_observations':observations,'daily_vintage_observation_counts':daily,
        'input_rows':len(rows),'input_series':len({r['series_id'] for r in rows}),'source_C_score':None,'inferred_context':inferred}


def scan_stoic_data(m,branch,*,extra=False):
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
                'cycle_and_indicator_rules_recorded':True if getattr(m,'reconstruct',False) else None},operation='existing verified initial BLS vintages and 12-prior-observation O160 comparison; custom source rules remain external',
                parents=[r['current']['observation_id'] for r in observations if r['current']],known_at=m.at('09:30'),assumption='A2-MACRO')
            e.geometry['macro']=macro
        episodes.append(e.finish(decision_at=decision))
    out=window_result(m,'STOIC-DATA',branch,episodes,extra=extra,omissions=[] if records else [{'reason':'collection review is emitted after this date job finishes','kind':'pending_process_record'}])
    if macro:out['measured_quantities']=macro
    return out


def scan_jetbundle(m,branch):
    start=m.at('09:30');end=start+2*MINUTE
    if getattr(m,'reconstruct',False):
        calendar=m.policy.rth(m.day)
        if calendar['state']=='closed_rth' and not m.local(start,end,book=True):
            return window_result(m,'JETBUNDLE-STATES',branch,[],omissions=[{
                'kind':'not_applicable','reason':'scheduled RTH closure; no market-state observation',
                'calendar':calendar,'observation_window':[start,end]}])
    if hasattr(m,'_jet_features'):
        events,updates,participation,response,display=m._jet_features
    else:
        events=m.local(start,end,book=True)
        books=BookObservations();updates=[]
        for row in events:updates.extend(books.add(row))
        updates.extend(books.finish())
        participation=m.domain('O163',{'events':events,'instrument_id':m.instrument_id,'start_ns':start,'end_ns':end,
            'required_depth_levels':1,'depth_levels':1,'coverage_complete':None,'depth_complete':True})
        response={side:m.domain('O164',{'events':events,'start_ns':start,'end_ns':end,'side':side,
            'response_basis':'trade_price','instrument_id':m.instrument_id,'instrument_tick_size':Q,
            'coverage_complete':True,'effort_side':'directional'}) for side in ('long','short')}
        display={key:sum(r.get(key) or 0 for r in updates) for key in ('bid_added','ask_added','bid_removed','ask_removed')}
        m._jet_features=events,updates,participation,response,display
    labels=[r for r in m.supplied('state_label',end) if r['state_label']==branch and r.get('start_ns')==start and r.get('end_ns')==end]
    label=labels[-1] if labels else None
    state=m.domain('O165',label['inputs']) if label else None
    e=HistoricalEpisode(m,'JETBUNDLE-STATES',branch,'not_applicable',{'id':f'participation:{start}:{end}','at':start},
        {'id':f'local-state-scope:{m.instrument_id}:{start}:{end}','known_at':end})
    e.bind({'participation_record_complete':participation['source_process_complete'],'participation_known_at':end,
        'response_record_complete':True if all(r.get('price_response_points') is not None for r in response.values()) else None,
        'response_known_at':end,'state':branch if label else None,'state_at':end},operation='actual native local executions and displayed depth-one updates; source label only from dated records',
        parents=[r['event_id'] for r in events],known_at=end)
    if label:
        criteria={r.get('criterion',r.get('name')):r.get('observed') for r in state['criteria_ledger']}
        selected={'B':['two_sided_executions','recent_revisits','low_aggression_both_sides'],
            'A':['high_aggression','low_response_efficiency','opposite_liquidity_holds_and_refills'],
            'D':['aggression','efficient_displacement'],'E':['prior_absorption_or_effort','replenishment_stops','level_gives_way'],
            'W':['cancellations_dominate']}[branch]
        e.bind({k:criteria.get(k) for k in selected},operation='audited O165 actual dated source criteria',kind='record',parents=[label['id']],known_at=end)
    if getattr(m,'reconstruct',False):
        from .strategy_context import inferred_auction
        inferred=inferred_auction(m,start,end)
        e.bind({'participation_record_complete':True if inferred['current']['available'] else None,
            'response_record_complete':True if inferred['current'].get('response') is not None else None,
            'state':branch,**inferred['criteria'][branch]},operation='source-inspired independent auction state classifier over causal native executions and displayed depth-one changes',
            kind='inferred_model',parents=inferred['current'].get('event_ids',[]),known_at=end,assumption='strategy-auction-v1')
        e.geometry['inferred_state']=inferred
    e.geometry.update(participation=participation,response=response,displayed_changes=display,
        source_label=state,cancellation_volume=None,individual_order_identity=None)
    return window_result(m,'JETBUNDLE-STATES',branch,[e.finish(decision_at=end)])


def scan_risk(m,branch):
    records=[r for r in m.supplied('risk_stage',m.end) if r['inputs'].get('risk_stage')==branch];episodes=[]
    for record in records:
        inp=record['inputs'];at=inp['decision_at'];ladder=m.domain('O155',inp);validation=m.domain('O154',record['validation_inputs'])
        e=HistoricalEpisode(m,'STOIC-RISK',branch,'not_applicable',{'id':record['id'],'at':at},{'id':record['baseline_id'],'known_at':record['known_at']})
        values={'validated_process':validation.get('overlay_validation'),'prior_sample_n':validation.get('sample_n'),
            'win_rate_known':validation.get('win_rate') is not None,'average_rr_known':validation.get('average_rr') is not None,
            'mc_loss_streak_known':validation.get('mc_max_loss_streak') is not None,'base_risk_fraction':ladder['base_risk_fraction'],
            'risk_stage':branch,'risk_units':inp.get('risk_units'),'planned_reward_r':inp.get('planned_reward_r'),
            'next_risk_units':inp.get('next_risk_units'),'first_trade_closed':ladder['first_trade_closed'],
            'first_trade_result_units':ladder['first_trade_result_units'],'first_trade_close_at':ladder['first_trade_close_at'],
            'second_trade_result_units':ladder['second_trade_result_units']}
        e.bind(values,operation='existing O154 prior validation and O155 fixed-baseline closed-result ladder',parents=[record['id']],known_at=record['known_at'],kind='record')
        e.geometry.update(ladder=ladder,validation=validation);episodes.append(e.finish(decision_at=at))
    result=window_result(m,'STOIC-RISK',branch,episodes,omissions=[] if records else [{'reason':'no actual validated process and risk-stage ledger','kind':'external_operand'}])
    result['published_arithmetic']={'risk_units':4 if branch=='second' else 1,'planned_reward_R':3,
        'reward_baseline_units':12 if branch=='second' else 3,'baseline_fraction_max':'.01',
        'next_after_second_win':1,'actual_account_or_trade':False}
    return result


UNIT_RECIPES={('JJ-TBR','management'):'O142',('SIRES','management'):'O142',('SIRES','reentry'):'O144',
    ('SIRES','case_description'):'O133',('REFILL-STUDY','selected_order_configuration'):'O150',
    ('REFILL-STUDY','supplied_selected_order'):'O150',('JETBUNDLE-STATES','transition_observation'):'O166'}


def scan_supplied_unit(m,method,branch,*,extra=True):
    rid=UNIT_RECIPES.get((method,branch));records=m.supplied(method+':'+branch,m.end);episodes=[]
    if method=='GB-SCALP' and branch=='automatic_admission':
        # Literal NULL is the published automatic-admission contract. Retain
        # independently observable directional/pullback paths in main branches.
        return window_result(m,method,branch,[],extra=True,omissions=[{'kind':'external_definition',
            'operand':'automatic_entry_rule','reason':'GB p.40 discloses no complete repeatable scalp entry'}])
    for record in records:
        # Reuse full existing source assembly, including counterpart/parent
        # checks. An isolated order/reentry object is not a method verdict.
        from .assembly import read_assembled_manifest
        from .native_resolution import NativeResolver
        path=Path(record['assembly_manifest_path'])
        if file_digest(path)!=record['assembly_manifest_sha256']:
            raise NativeEvidenceError('supplied process assembly manifest changed')
        document,assembled,digest=read_assembled_manifest(path,method,resolver=NativeResolver(m.data_root))
        candidates=[a for a in assembled if a.result['candidate_id']==record['candidate_id']]
        if len(candidates)!=1:raise NativeEvidenceError('no unique requested process candidate')
        audit=candidates[0];result=audit.result
        if result.get('evidence_mode')=='synthetic_fixture':
            raise NativeEvidenceError('fixture cannot enter an actual-record cohort')
        expected='selected_order_configuration' if method=='REFILL-STUDY' else branch
        if result['predicate']!=expected:
            raise NativeEvidenceError('supplied process predicate differs from selected unit')
        if str(result['instrument_id'])!=str(m.instrument_id):
            raise NativeEvidenceError('supplied process instrument differs')
        at=result['decision_at']
        if not m.start<=at<m.end or record['known_at']>at:
            raise NativeEvidenceError('supplied process outside date/availability scope')
        m.input_receipts.append({'path':str(path),'sha256':digest})
        episode={'schema':'phase1-historical-episode-v2','candidate_id':'process-v2:'+content_hash(record),
            'method':method,'branch':branch,'predicate':expected,'side':result.get('side','not_applicable'),
            'session_date':str(m.day),'instrument_id':m.instrument_id,'decision_at':at,'occurrence_at':at,
            'values':{k:v['value'] for k,v in result.get('operands',{}).items()},
            'operand_derivations':{},'selected_fields':sorted(result.get('operands',{})),'stages':[],
            'research_verdict':result['verdict'],'author_exact_verdict':'unknown','faithful_eligible':False,'actual_trade':False,
            'reference':{'id':record['id']},'trigger':{'id':record['id']},'geometry':{'assembled_process':result},
            'input_sha256':m.window.document['input_sha256'],'assembly_sha256':content_hash(result),
            'limitations':result.get('holes',[]),'failed':[],'unknown':result.get('hole_ids',[])}
        episodes.append(episode)
    return window_result(m,method,branch,episodes,extra=extra,omissions=[] if records else [{
        'kind':'external_record','reason':'actual dated process/source records absent','record_key':method+':'+branch,
        'connected_recipe':rid,'connected_assembler':'assembly:read_assembled_manifest',
        'required_input':'record ID and original evidence path/hash; assembly_manifest_path/hash and candidate_id; full typed parent/current entry or state counterparts, original source evidence and actual ledger'}])
