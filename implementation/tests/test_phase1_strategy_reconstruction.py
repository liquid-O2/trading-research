"""Source logic, scope, model numerics and predecision availability controls."""
from copy import deepcopy
from datetime import date
from decimal import Decimal as D
from types import SimpleNamespace
import pytest
from trading_research.research.method_pack.strategy_policy import EXCLUDED,observation_scope
from trading_research.research.method_pack.expressions import evaluate
from trading_research.research.method_pack.strategy_context import auction_criteria,conjunction,auction_metrics,inferred_macro
from trading_research.research.method_pack.strategy_options import bs_price,implied_vol,unit_gamma,build_gamma
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.event_time import MINUTE,SECOND


def test_scalp_qualification_ignores_personal_records_but_retains_direction_and_pullback():
    values={'direction_recorded_before_entry':True,'source_directional_pullback_observed':True,
        'small_size_recorded':None,'source_scalp_management_recorded':None}
    assert evaluate('GB-SCALP','case_description',values).value is None
    for size,management in [(None,None),(False,False),(True,True)]:
        values.update(small_size_recorded=size,source_scalp_management_recorded=management)
        r=evaluate('GB-SCALP','case_description',values,excluded_fields=EXCLUDED['GB-SCALP'])
        assert r.value is True
        assert not r.fields & EXCLUDED['GB-SCALP']
    values['source_directional_pullback_observed']=False
    assert evaluate('GB-SCALP','case_description',values,excluded_fields=EXCLUDED['GB-SCALP']).value is False


def test_context_and_account_units_cannot_enter_setup_denominator():
    for method in ['STOIC-RISK','JETBUNDLE-STATES','REFILL-STUDY','STOIC-DATA']:
        assert observation_scope(method,'first')!='entry_setup'
    assert observation_scope('SIRES','management')=='personal_execution_out_of_scope'
    assert observation_scope('GB-SCALP','bullish_small_scalp')=='entry_setup'


def metrics(**changes):
    m={'available':True,'buy':10,'sell':10,'unknown':0,'volume':20,'response':D(0),'efficiency':D(0),
        'low':D(100),'high':D(101),'last_vwap':D('100.5'),'book_available':True,'bid_added':10,'ask_added':10,
        'bid_removed':0,'ask_removed':0,'withdrawal_estimate':0,'revisit':True}
    return dict(m,**changes)


def test_jet_balance_requires_two_sides_revisits_and_low_effort():
    p=metrics();c=metrics()
    assert conjunction(*auction_criteria(c,p)['B'].values()) is True
    c['revisit']=False
    assert conjunction(*auction_criteria(c,p)['B'].values()) is False


def test_jet_absorption_requires_dynamic_refill_not_a_static_wall():
    p=metrics();c=metrics(buy=40,volume=50)
    assert conjunction(*auction_criteria(c,p)['A'].values()) is True
    c['ask_added']=0
    assert conjunction(*auction_criteria(c,p)['A'].values()) is False
    c['ask_added']=10;c['efficiency']=D('.8');c['response']=D(1)
    assert conjunction(*auction_criteria(c,p)['D'].values()) is True
    assert conjunction(*auction_criteria(c,p)['A'].values()) is False


def test_jet_exhaustion_requires_prior_effort_stopping_refill_and_level_break():
    p=metrics(buy=20,sell=5);c=metrics(bid_added=0,ask_added=0,last_vwap=D(102))
    assert conjunction(*auction_criteria(c,p)['E'].values()) is True
    c['last_vwap']=D('100.5')
    assert conjunction(*auction_criteria(c,p)['E'].values()) is False
    c=metrics(withdrawal_estimate=100)
    assert conjunction(*auction_criteria(c,p)['W'].values()) is True


def test_unknown_aggressor_does_not_create_auction_direction():
    c=metrics(buy=100,unknown=5)
    assert auction_criteria(c,metrics())['A']['high_aggression'] is None
    assert auction_criteria(c,metrics())['D']['aggression'] is None


def test_option_iv_roundtrip_and_call_put_gamma_symmetry():
    for call in (False,True):
        mid=bs_price(100,101,.05,.25,call)
        iv=implied_vol(100,101,.05,mid,call)
        assert iv==pytest.approx(.25,abs=1e-10)
    assert unit_gamma(100,101,.05,.25)>0
    assert implied_vol(100,90,.05,9,True) is None


def option_fixture():
    day=date(2024,1,2);at=et_ns(day,10,0);expiry=date(2024,1,5)
    quotes=[];oi=[]
    for right,interest in [('CALL',200),('PUT',100)]:
        years=(et_ns(expiry,16,0)-at)/(365.25*86400*SECOND)
        mid=bs_price(100,100,years,.25,right=='CALL')
        quotes.append({'ts_event':at-MINUTE,'expiration':expiry,'strike':100.,'right':right,
            'bid':mid-.01,'ask':mid+.01,'bid_size':10,'ask_size':10,'osi_symbol':right})
        oi.append({'request_date':date(2023,12,29),'ts_event':at-4*86400*SECOND,'osi_symbol':right,'open_interest':interest})
    return quotes,oi,at,day


def test_gamma_causal_quotes_oi_and_expiry_are_explicit():
    q,oi,at,day=option_fixture();base=build_gamma(q,oi,100,at,day)
    assert base['regime']=='long' and base['expiry_kind']=='front_expiry_approximation'
    future=deepcopy(q[0]);future.update(ts_event=at,bid=100,ask=101)
    futureoi=deepcopy(oi[0]);futureoi.update(request_date=day,ts_event=at,open_interest=1_000_000)
    assert build_gamma(q+[future],oi+[futureoi],100,at,day)==base
    assert build_gamma(q,oi,100,at-SECOND,day)['available'] is False
    oi[1]['open_interest']=1000
    assert build_gamma(q,oi,100,at,day)['regime']=='short'


def test_gamma_one_sided_chain_cannot_assert_regime():
    q,oi,at,day=option_fixture()
    result=build_gamma(q[:1],oi,100,at,day)
    assert result['available'] is True and result['regime'] is None


def test_reconstruction_calendar_is_separate_from_exchange_evidence():
    from trading_research.research.method_pack.session_policy import NQSessionPolicy,ReconstructionSessionPolicy
    assert NQSessionPolicy().previous_session('2021-01-04')['date']=='2021-01-01'
    modeled=ReconstructionSessionPolicy()
    assert modeled.previous_session('2021-01-04')['date']=='2020-12-31'
    assert modeled.day('2021-01-01')['calendar_model']=='strategy-reconstruction-v1'


def test_macro_is_our_composite_and_missing_series_is_not_zero():
    observations=[{'series_id':series,'baseline':[{'value':v} for v in range(1,13)],
        'current':{'value':13,'available_at':100}} for series in ('CPIAUCSL','PAYEMS')]
    result=inferred_macro(observations)
    assert result['composite']==0 and result['is_source_C_score'] is False
    observations[0]['current']=None
    assert inferred_macro(observations)['composite'] is None


def test_pzone_quantiles_are_ordered_and_do_not_depend_on_input_order():
    from trading_research.research.method_pack.strategy_pzones import quantile
    assert quantile([4,1,3,2],.75)==quantile([1,2,3,4],.75)==3.25


def test_incomplete_prior_profile_is_unavailable_not_failed_keani_condition():
    from test_phase1_historical_replay import Market,raw,TOUCH
    from trading_research.research.method_pack.historical_auction_scanners import scan_keani
    m=Market([raw(at,100) for at in range(TOUCH-30*MINUTE,TOUCH,MINUTE)])
    old=SimpleNamespace(start=0,end=1,profile=lambda *args:{'vah':None,'profile_id':'unavailable-prior'})
    m.prior=lambda kind:{'sessions':[{'window':old}],'scope_complete':False,'range':None,'omissions':[]}
    e=scan_keani(m,'source_long')['episodes'][0]
    assert e['values']['prior_value_fixed'] is None and e['values']['prior_vah'] is None
    assert 'prior_value_fixed' not in e['failed']


def test_unobserved_member_response_does_not_fail_objective(monkeypatch):
    from test_phase1_historical_replay import Market,raw,TOUCH
    from trading_research.research.method_pack import historical_auction_scanners as scanners
    from trading_research.research.method_pack.empirical_market import clock
    previous=date(2026,1,14);split=clock(previous,'12:45');start=clock(previous,'09:30');end=clock(previous,'16:00')
    reaction={'id':'reaction','side':'high','price':D(100),'at':start,'known_at':start+5*MINUTE,'members':['earlier']}
    oldbars=[{'start':start,'known_at':start+5*MINUTE,'L':D(98),'H':D(100)}]
    profile={'rows':[{'price':D(100),'total_volume':D(10)}],'formation_start':split,'known_at':end,'profile_id':'independent-hvn'}
    old=SimpleNamespace(start=start,end=end,bars=lambda *args:oldbars,profile=lambda *args:profile)
    m=Market([raw(at,100,1,'A') for at in range(TOUCH,TOUCH+2*MINUTE,SECOND)])
    m.prior=lambda kind:{'sessions':[{'window':old,'day':str(previous)}],'scope_complete':True,'range':None,'omissions':[]}
    monkeypatch.setattr(scanners,'pivots',lambda rows:[reaction])
    e=scanners.scan_member(m,'resistance_short')['episodes'][0]
    assert e['geometry']['entry'] is None
    assert e['values']['objective_fixed'] is None
    assert 'objective_fixed' not in e['failed']


def test_o056_consumed_third_close_remains_unknown():
    from test_phase1_historical_replay import Market,raw,TOUCH
    from trading_research.research.method_pack.historical_price_scanners import _ob
    from trading_research.research.method_pack.branch_coverage import setting
    duration=setting('tbr_sessions')['confirmation_seconds']*SECOND;start=TOUCH//duration*duration-duration
    events=[raw(at,100) for at in range(start,start+3*duration,MINUTE)]
    events.append(raw(start+3*duration-MINUTE,101))
    m=Market(events);touch=m.bars(start+duration,start+2*duration)[0]
    assert _ob(m,touch,'long',start+3*duration)[0] is None


def test_auction_metrics_ignore_future_and_unavailable_native_rows():
    from test_phase1_historical_replay import raw,TOUCH
    rows=[raw(TOUCH+i*SECOND,100+i*.25,2,'B') for i in (1,31,61,91)]
    base=auction_metrics(rows,TOUCH,TOUCH+120*SECOND)
    future=raw(TOUCH+121*SECOND,200,10000,'A');late=raw(TOUCH+60*SECOND,200,10000,'A');late['known_at']=TOUCH+121*SECOND
    assert auction_metrics(rows+[future,late],TOUCH,TOUCH+120*SECOND)==base


def test_new_year_calendar_does_not_skip_the_traded_friday_before_saturday():
    from trading_research.research.method_pack.session_policy import ReconstructionSessionPolicy
    policy=ReconstructionSessionPolicy()
    assert policy.previous_session('2022-01-03')['date']=='2021-12-31'
    assert policy.rth('2021-12-31')['state']=='regular'


def test_early_pzone_uses_its_own_clock_and_whole_band(monkeypatch):
    from test_phase1_historical_replay import Market,raw,DAY
    from trading_research.research.method_pack.empirical_market import clock
    from trading_research.research.method_pack.historical_price_scanners import scan_jumbo
    from trading_research.research.method_pack import strategy_pzones
    at=clock(DAY,'02:00')
    events=[raw(t,101 if t<at else 100 if t<at+3*MINUTE else 102) for t in range(at-3*MINUTE,at+9*MINUTE,MINUTE)]
    m=Market(events,records={'strategy_reconstruction':True})
    m.prior=lambda kind:{'range':{'high':D(108),'low':D(98)},'scope_complete':True,'omissions':[]}
    zone={'id':'test-model-zone','formation_start':at-60*MINUTE,'known_at':at,'expires_at':at+9*MINUTE,
        'low':D('99.5'),'high':D('100.5'),'destination_price':D(105),'destination_id':'test-anchor',
        'side':'long','inferred_zone':True}
    monkeypatch.setattr(strategy_pzones,'inferred_pzones',lambda market:[zone])
    episodes=scan_jumbo(m,'timed_pzone_reversal')['episodes']
    assert len(episodes)==1  # The first 100 print touches the band, not its 99.5 far edge.
    e=episodes[0]
    assert e['values']['context_at']==at and e['values']['touch_at']==at
    assert e['strategy_assessment']['status']=='setup'


def test_calendar_model_has_a_distinct_provenance_hash():
    from trading_research.research.method_pack.session_policy import NQSessionPolicy,ReconstructionSessionPolicy
    assert NQSessionPolicy().sha256!=ReconstructionSessionPolicy().sha256


def test_reconciliation_preserves_distinct_units_sharing_an_episode_id(tmp_path,monkeypatch):
    import gzip,json
    from trading_research.research.method_pack import strategy_reporting as reporting
    monkeypatch.setattr(reporting,'BASE',tmp_path/'baseline')
    monkeypatch.setattr(reporting,'ROOT',tmp_path)
    baseline=tmp_path/'baseline/run-2.0.0-r9';baseline.mkdir(parents=True)
    (baseline/'RESULTS.json').write_text('{}')
    selected=[];branches=[]
    for unit in ('branch','unit'):
        coverage='STOIC-DATA:'+unit+':macro_application'
        row={'coverage_id':coverage,'method_id':'STOIC-DATA','branch':'macro_application',
            'source_definition':{'citation':'test source','operation':'context audit'}}
        e={'candidate_id':'shared-context-id','method':'STOIC-DATA','branch':'macro_application',
            'session_date':'2024-01-02','research_verdict':'unknown',
            'strategy_assessment':{'scope':'context_or_research','status':'condition_present','failed_conditions':[],'unavailable_conditions':[]}}
        doc={'coverage_id':coverage,'episodes':[e]};branches.append(row);selected.append((row,doc,{}))
        for cohort in ('pilot','evaluation'):
            path=baseline/'jobs'/cohort/(unit+'.json.gz');path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(gzip.compress(json.dumps(doc).encode()))
    result=reporting.report_strategy(tmp_path/'report',{'registry_sha256':'test'}, {'branches':branches},selected,selected)
    for cohort in ('pilot','evaluation'):
        assert result[cohort]['baseline_observations']==2
        assert result[cohort]['current_observations']==2
        assert not result[cohort]['retired_baseline_observations']
        assert sum(r['n'] for r in result[cohort]['transitions'])==2


def test_published_close_requires_matching_clock_contract_population_and_availability():
    from trading_research.research.method_pack.strategy_measurements import reconcile_bar
    native={'start':0,'end':MINUTE,'instrument_id':17,'observed_complete':True,
        'O':D(100),'H':D(102),'L':D(99),'C':None,'V':25}
    published={**native,'C':D(101),'known_at':MINUTE}
    result=reconcile_bar(native,published)
    assert result['C']==101 and native['C'] is None
    assert result['endpoint_evidence']['raw_tick_order_recovered'] is False
    for field,value in [('start',SECOND),('instrument_id',18),('V',26),('H',D(103)),('O',D(99)),('known_at',MINUTE+1)]:
        assert reconcile_bar(native,{**published,field:value}) is native


def test_timestamp_batch_price_is_order_independent_and_uses_only_selected_events():
    from trading_research.research.method_pack.strategy_measurements import batch_price
    rows=[{'price':D(100),'executed_size':3},{'price':D(101),'executed_size':1}]
    assert batch_price(rows)==D('100.25')
    assert batch_price(rows[::-1])==batch_price(rows)
    assert batch_price([{'price':D(100),'executed_size':1}])==100


def test_reconstructed_flow_resolves_tied_endpoints_without_future_or_file_order():
    from test_phase1_historical_replay import Market,raw,TOUCH
    from trading_research.research.method_pack.historical_flow import local_observations
    events=[raw(TOUCH+i*SECOND,100,3,'A') for i in range(-5,16)]
    events.append(raw(TOUCH+SECOND,100.25,1,'B'))
    base=Market(events,records={'strategy_reconstruction':True})
    before=local_observations(base,TOUCH,[D(100),D(101)],'long',horizon=10,book=False)
    later=Market(events+[raw(TOUCH+11*SECOND,200,9999,'B')],records={'strategy_reconstruction':True})
    after=local_observations(later,TOUCH,[D(100),D(101)],'long',horizon=10,book=False)
    keep=lambda obs:[(r['first'],r['last'],r['own'],r['opposing'],r['entry_px']) for r in obs['chunks']]
    assert keep(before)==keep(after)
    assert all(r['first'] is not None and r['last'] is not None for r in before['chunks'])
    assert all(r['entry_px']%D('.25')==0 for r in before['chunks'])


def test_control_absence_ignores_earlier_candle_and_irrelevant_endpoint():
    from trading_research.research.method_pack.historical_auction_scanners import _control_absence
    # Earlier ambiguous candle is outside the actual post-reacceptance search.
    rows=[{'start':0,'end':MINUTE,'observed_complete':True,'O':None,'C':D(100),'delta':1},
          {'start':MINUTE,'end':2*MINUTE,'observed_complete':True,'O':None,'C':D(101),'delta':-10},
          {'start':2*MINUTE,'end':3*MINUTE,'observed_complete':True,'O':D(100),'C':D(101),'delta':10}]
    m=SimpleNamespace(reconstruct=True,bars=lambda a,b:[r for r in rows if a<=r['start'] and r['end']<=b],
        coverage=lambda a,b:{'observed_scope_complete':True})
    assert _control_absence(m,MINUTE,3*MINUTE,'long') is False
    # Ambiguity that could actually complete a pair remains honest uncertainty.
    rows[1]['delta']=10
    assert _control_absence(m,MINUTE,3*MINUTE,'long') is None
    rows[1]['O']=D(100)
    assert _control_absence(m,MINUTE,3*MINUTE,'long') is True


def test_closed_rth_does_not_create_an_unknown_market_state():
    from test_phase1_historical_replay import Market
    from trading_research.research.method_pack.historical_process_scanners import scan_jetbundle
    m=Market([],records={'strategy_reconstruction':True})
    m.policy=SimpleNamespace(rth=lambda day:{'state':'closed_rth','known':True,'windows':[]})
    result=scan_jetbundle(m,'A')
    assert result['episodes']==[] and result['u']==0
    assert result['omissions'][0]['kind']=='not_applicable'


def test_owned_partial_minute_is_enumerated_without_creating_a_future_candle(monkeypatch):
    from test_phase1_historical_replay import Market,raw,TOUCH
    from trading_research.research.method_pack.strategy_measurements import StrategyWindow
    from trading_research.research.method_pack import event_cache
    m=Market([raw(TOUCH,100),raw(TOUCH+2*MINUTE,101)])
    doc=deepcopy(m.window.document);doc['plan']['owned_spans']=[{'start_ns':m.start,'end_ns':m.end}]
    monkeypatch.setattr(event_cache,'contract_at',lambda root,at:{'instrument_id':17})
    win=StrategyWindow(doc,schedule=m.policy,owner=m)
    assert win.coverage(TOUCH,TOUCH+MINUTE//2)['observed_scope_complete'] is True
    assert win.bars(TOUCH,TOUCH+MINUTE//2)==[]
    assert win.coverage(TOUCH+MINUTE,TOUCH+2*MINUTE)['observed_scope_complete'] is True
    assert win.coverage(TOUCH,TOUCH+MINUTE)['market_coverage_complete'] is None
    doc['plan']['unowned_intervals']=[{'start_ns':TOUCH,'end_ns':TOUCH+MINUTE}]
    assert win.coverage(TOUCH,TOUCH+MINUTE)['observed_scope_complete'] is False


def test_published_prior_range_discloses_contracts_and_cannot_make_a_volume_profile(monkeypatch):
    from trading_research.research.method_pack import strategy_measurements as sm
    rows=[{'start':0,'known_at':MINUTE,'instrument_id':16,'o':100,'h':102,'l':99,'c':101,'v':10},
          {'start':MINUTE,'known_at':2*MINUTE,'instrument_id':17,'o':103,'h':105,'l':102,'c':104,'v':20}]
    monkeypatch.setattr(sm,'vendor_rows',lambda *args:(rows,[{'path':'owned-bars','sha256':'fixture'}]))
    market=SimpleNamespace(data_root='fixture',input_receipts=[],instrument_id=17)
    ref=sm.published_prior_range(market,[(0,2*MINUTE)],'month')
    assert ref['high']==105 and ref['low']==99 and ref['known_at']==2*MINUTE
    assert ref['contract_ids']==[16,17] and ref['same_current_contract'] is False
    assert ref['not_a_volume_profile'] is True and ref['price_adjustment'] is None
    monkeypatch.setattr(sm,'vendor_rows',lambda *args:([],[]))
    assert sm.published_prior_range(market,[(0,2*MINUTE)],'month') is None


def test_missing_published_prior_session_uses_covered_native_extrema(monkeypatch):
    from trading_research.research.method_pack import strategy_measurements as sm
    monkeypatch.setattr(sm,'vendor_rows',lambda *args:([],[]))
    market=SimpleNamespace(data_root='fixture',input_receipts=[],instrument_id=17)
    window=SimpleNamespace(start=0,end=MINUTE,instrument_id=17,document={'input_sha256':'native-fixture'})
    native={'window':window,'coverage':{'observed_scope_complete':True},'rows':[
        {'start':0,'end':MINUTE,'known_at':MINUTE,'bar_id':'native-bar','O':None,'C':None,'H':D(105),'L':D(100),'V':10}]}
    ref=sm.published_prior_range(market,[(0,MINUTE)],'month',[native])
    assert ref['low']==100 and ref['high']==105
    assert ref['open'] is None and ref['close'] is None
    assert ref['native_supplement_input_sha256s']==['native-fixture']
    native['coverage']['observed_scope_complete']=False
    assert sm.published_prior_range(market,[(0,MINUTE)],'month',[native]) is None


def test_empty_expired_chart_window_is_disclosed_but_unexplained_gap_is_unknown(monkeypatch):
    from trading_research.research.method_pack import strategy_measurements as sm
    rows=[{'start':0,'known_at':MINUTE,'instrument_id':16,'o':100,'h':102,'l':99,'c':101,'v':10}]
    monkeypatch.setattr(sm,'vendor_rows',lambda root,start,end:(rows if start==0 else [],[]))
    market=SimpleNamespace(data_root='fixture',input_receipts=[],instrument_id=17)
    exclusion={'start':MINUTE,'end':2*MINUTE,'instrument_id':16,'expiration_ns':MINUTE,'path':'roll','sha256':'fixture'}
    monkeypatch.setattr(sm,'expired_chart_window',lambda *args:exclusion)
    ref=sm.published_prior_range(market,[(0,MINUTE),(MINUTE,2*MINUTE)],'month')
    assert ref['low']==99 and ref['high']==102
    assert ref['expired_continuous_chart_windows']==[exclusion]
    assert {'path':'roll','sha256':'fixture'} in market.input_receipts
    monkeypatch.setattr(sm,'expired_chart_window',lambda *args:None)
    assert sm.published_prior_range(market,[(0,MINUTE),(MINUTE,2*MINUTE)],'month') is None


def test_expired_chart_exclusion_requires_expiry_before_window_and_same_mapping(tmp_path,monkeypatch):
    from trading_research.research.method_pack import strategy_measurements as sm,event_cache
    from datetime import datetime,timezone
    path=tmp_path/'derived/continuous-futures__instrument-and-roll-maps/nq-rolls.parquet'
    path.parent.mkdir(parents=True);path.touch()
    contract={'expiration_ts_utc':datetime.fromtimestamp(60,timezone.utc),'segment_end_exclusive_ms':120000,
        'instrument_id':16,'roll_source_path':str(path),'roll_source_sha256':'fixture'}
    monkeypatch.setattr(event_cache,'contract_at',lambda *args:contract)
    m=SimpleNamespace(data_root=tmp_path)
    assert sm.expired_chart_window(m,MINUTE,2*MINUTE)['instrument_id']==16
    assert sm.expired_chart_window(m,0,MINUTE) is None
    assert sm.expired_chart_window(m,MINUTE,3*MINUTE) is None
    contract['expiration_ts_utc']=None
    assert sm.expired_chart_window(m,MINUTE,2*MINUTE) is None
