from copy import deepcopy
from decimal import Decimal as D

from trading_research.research.method_pack.objects import process_observations as p


def test_all_process_categories_and_original_r_denominator_are_retained():
    categories=['win','loss','flat','open','censored','missing_result','miss','breach']
    inp=dict(process_id='p',process_version='v',cohort_id='c',closed_denominator='win_loss_flat',mean_win=2,mean_loss=-1,
       initial_R_provenance=dict(definition_id='original',known_at=0,unit='R'),reported_metrics={'ev':str(D(1)/3)},use_at=20,
       outcomes=[dict(outcome_id=str(i),category=cat,process_id='p',process_version='v',known_at=10,
                      **({'closed_at':9} if cat in {'win','loss','flat'} else {})) for i,cat in enumerate(categories)])
    r=p.o153(inp)
    assert r.state=='supplied' and r.value['summary_consistency'] is True
    den=r.value['denominator_identity']
    assert den['closed_n']==3 and den['all_record_count']==8
    assert den['categories']['flat']==den['categories']['censored']==1
    assert r.value['win_rate']==D(1)/3 and r.value['ev']==D(1)/3
    inp['outcomes'][1]['outcome_id']='0'
    assert p.o153(inp).base_ok is False


def validation():
    sample=[dict(sample_id=f't{i}',process_id='p',process_version='v1',closed_at=i+1,known_at=i+1,outcome='win' if i%2 else 'loss') for i in range(100)]
    return dict(validation_record=dict(validation_id='v',process_id='p',process_version='v1',sample=sample,n=100,
       win_rate='0.5',avg_rr=2,win_rate_definition='wins / decidable closed trades',average_rr_definition='source reward/risk definition',
       known_at=110,monte_carlo=dict(result_id='mc',process_id='p',process_version='v1',sample_ids=[x['sample_id'] for x in sample],
       design={'source_report':'supplied simulation design, no run here'},source_ref='test source report',known_at=109,max_loss_streak=8)),use_at=111)


def test_validation_requires_actual_prior_sample_and_compatible_supplied_result():
    r=p.o154(validation())
    assert r.value['overlay_validation'] is True and r.known_at==110 and r.value['simulation_run'] is False
    assert p.o154(dict(n=100,win_rate='0.55',avg_rr=2,mc_max_streak=8)).value['overlay_validation'] is None
    inp=validation();inp['validation_record']['sample'][0]['known_at']=115
    assert p.o154(inp).base_ok is False and p.o154(inp).value['overlay_validation'] is False
    inp=validation();inp['validation_record']['monte_carlo']['process_version']='v2'
    assert p.o154(inp).base_ok is False
    inp=validation();inp['validation_record']['sample']=inp['validation_record']['sample'][:99];inp['validation_record']['n']=99
    inp['validation_record']['monte_carlo']['sample_ids']=inp['validation_record']['monte_carlo']['sample_ids'][:99]
    assert p.o154(inp).value['overlay_validation'] is False


def test_process_supporting_clocks_and_sample_statistics_cannot_be_copied():
    inp=dict(process_id='p',process_version='v',cohort_id='c',wins=1,losses=1,mean_win=2,mean_loss=-1,
       closed_denominator='win_loss',supplied_summary_ref='source-summary',known_at=10,use_at=20,
       initial_R_provenance=dict(definition_id='original',known_at=25,unit='R'))
    assert p.o153(inp).known_at==25 and p.o153(inp).base_ok is False
    inp['initial_R_provenance']['known_at']=5
    inp['causal_corrections']=[dict(correction_id='c',known_at=15)]
    assert p.o153(inp).known_at==15
    inp=validation();inp['validation_record']['win_rate']='0.75'
    result=p.o154(inp)
    assert result.value['observed_sample_win_rate']==D('.5') and result.base_ok is False
    assert len(result.value['validation_record']['sample'])==100
    inp=validation();inp['validation_record']['monte_carlo']['sample_ids'].append('t0')
    assert p.o154(inp).base_ok is False


def test_native_effort_endpoint_sequence_and_future_indicator_snapshot():
    inp=response_input()
    inp['events'][0]['exchange_seq']=1;inp['events'][1]['exchange_seq']=2
    inp['events'].append(dict(event_id='last',event_ns=8,known_at=8,exchange_seq=3,action='T',
                              side='B',price=102,size=10,instrument_id='nq'))
    assert p.o164(inp).value['price_response_points']==2
    inp['events']=[inp['events'][2],inp['events'][0],inp['events'][1]]
    assert p.o164(inp).value['price_response_points']==2
    macro=dict(required_series={'leverage':'x'},as_of=20,indicator_records=[
       dict(series_id='x',value=1,unit='ratio',vintage_id='v1',available_at=10)])
    before=p.o157(macro)
    macro['indicator_records'].append(dict(series_id='x',value=2,unit='ratio',vintage_id='v2',available_at=30))
    after=p.o157(macro)
    assert after.value==before.value and after.known_at==before.known_at and after.state==before.state


def test_prior_standardization_records_cannot_include_current_or_future_vintage():
    inp=dict(baseline_records=[dict(observation_id='b1',series_id='x',observation_at=1,available_at=2,value=1),
                               dict(observation_id='b2',series_id='x',observation_at=3,available_at=4,value=3)],
       current_record=dict(observation_id='current',series_id='x',observation_at=5,available_at=6,value=4),convention='population',use_at=7)
    r=p.o160(inp)
    assert r.value['baseline_mean']==2 and r.value['standardized_deviation']==2 and r.value['source_transform_known'] is True
    inp['baseline_records'][0]['observation_id']='current'
    assert p.o160(inp).base_ok is False
    inp['baseline_records'][0]['observation_id']='b1';inp['baseline_records'][0]['available_at']=8
    assert p.o160(inp).base_ok is False


def releases():
    return dict(series_id='CPI',reference_period='2026-03',as_of=20,vintage_policy='latest_available',releases=[
       dict(series_id='CPI',reference_period='2026-03',value='2.0',unit='pct',vintage_id='first',released_at=10,available_at=10),
       dict(series_id='CPI',reference_period='2026-03',value='1.5',unit='pct',vintage_id='revision',released_at=30,available_at=30)])


def test_vintage_snapshots_and_release_ordering():
    inp=releases();r=p.o162(inp)
    assert r.value['actual_value']==2 and r.known_at==10
    inp['as_of']=40
    assert p.o162(inp).value['actual_value']==D('1.5')
    inp['releases'][1]['available_at']=29
    assert p.o162(inp).base_ok is False
    inp=releases();inp['releases'][0].pop('available_at')
    assert p.o162(inp).value['actual_value'] is None


def order_event(eid,oid,seq,action,qty,*,side='bid',price=100,**extra):
    return dict(event_id=eid,order_id=oid,exchange_seq=seq,event_ns=seq,known_at=seq,
                instrument_id='NQH6',side=side,price=price,size=qty,depth_level=1,action=action,**extra)


def order_input():
    return dict(instrument_id='NQH6',source_symbol='NQ',required_depth_levels=1,depth_coverage=1,
         depth_complete=True,coverage_complete=True,start_ns=0,end_ns=10,use_at=10,
         events=[order_event('a','bid',1,'add',10),order_event('b','bid',2,'cancel',3),order_event('c','bid',3,'execute',4)])


def test_native_order_participation_reconciles_actions_per_side_and_identity():
    inp=order_input();r=p.o163(inp)
    assert r.value['source_process_complete'] is True
    assert (r.value['provided'],r.value['withdrawn'],r.value['consumed'],r.value['remaining'])==(10,3,4,3)
    assert r.value['per_side_volumes']['buy']==dict(provided=10,withdrawn=3,consumed=4)
    inp['events'][2]['price']=101
    assert p.o163(inp).base_ok is False
    inp=order_input();inp['events'][2]['side']='ask'
    assert p.o163(inp).base_ok is False
    inp=order_input();inp['events'].append(order_event('d','bid',4,'add',5))
    assert p.o163(inp).base_ok is False


def test_modify_preserves_native_order_identity_and_change_evidence():
    inp=order_input();inp['events']=[order_event('a','x',1,'add',10),order_event('m','x',2,'modify',10,new_quantity=15,new_price=101),
                                   order_event('f','x',3,'execute',4,price=101)]
    r=p.o163(inp)
    assert (r.value['provided'],r.value['withdrawn'],r.value['consumed'],r.value['remaining'])==(25,10,4,11)
    assert r.value['order_states']['x']['price']==101
    inp['depth_complete']=None
    assert p.o163(inp).value['source_process_complete'] is None


def response_input():
    return dict(start_ns=0,end_ns=10,side='long',response_basis='trade_price',instrument_id='nq',instrument_tick_size='0.25',coverage_complete=True,
      use_at=10,events=[dict(event_id='a',event_ns=1,known_at=1,action='T',side='B',price=100,size=50,instrument_id='nq'),
                       dict(event_id='b',event_ns=8,known_at=8,action='T',side='B',price=101,size=50,instrument_id='nq')])


def test_native_effort_directional_response_unknown_sides_and_tied_endpoints():
    inp=response_input();r=p.o164(inp)
    assert r.value['aggressive_volume']==100 and r.value['price_response_points']==1
    assert r.value['price_response_ticks']==4 and r.value['named_response_per_volume']==D('.01')
    # Certifying the interval also requires reaching its cutoff, even when
    # its last execution was earlier.
    assert r.value['source_efficiency_class'] is None and r.known_at==10
    inp['side']='short'
    assert p.o164(inp).value['price_response_points']==-1
    inp=response_input();inp['events'].append(dict(event_id='unknown',event_ns=5,action='T',side='N',price=100,size=100,instrument_id='nq'))
    assert 'HOLE:O164:unknown_aggressor_effort' in p.o164(inp).hole_ids
    inp=response_input();inp['events'].append(dict(event_id='tie',event_ns=8,action='T',side='B',price=102,size=10,instrument_id='nq'))
    assert p.o164(inp).value['price_response_points'] is None
    inp=response_input();inp['instrument_tick_size']=0
    assert p.o164(inp).base_ok is False


def test_macro_source_tokens_do_not_invent_classifiers_or_fill_vintage_holes():
    assert p.o158(dict(source_cycle_label='contraction',source_rule_id='token')).value['automatic_cycle'] is None
    assert p.o159(dict(c_score='2.4',z_score='1.2',source_rule_id='token')).value['automatic_c_score'] is None
    assert p.o161(dict(strength=7,regression_slope='0.5',source_rule_id='token')).value['automatic_strength'] is None
    r=p.o157(dict(available=[dict(id='x',value=1.5)],required_n=4,as_of=20))
    assert r.value['required_series_present'] is None and r.value['vintage_causal'] is None


def test_native_response_does_not_borrow_a_workspace_tick_without_its_definition():
    from types import MappingProxyType
    from trading_research.research.method_pack.native_resolution import ResolvedMembers
    # This real contract ID is present in the workspace's acquired definitions.
    # The resolved evidence intentionally does not contain that definition.
    instrument = 42004058
    rows = tuple(MappingProxyType({**row, 'instrument_id': instrument})
                 for row in response_input()['events'])
    resolved = ResolvedMembers(rows, instrument, 0, 10, 8, True, (),
                               instrument_definition=None)
    result = p.native_o164({'side': 'long', 'response_basis': 'trade_price',
                           'use_at': 10, 'instrument_tick_size': '.25'}, resolved)
    assert result.value['price_response_points'] == 1
    assert result.value['aggressive_volume'] == 100
    assert result.value['price_response_ticks'] is None
    assert result.value['response_record_complete'] is None
    assert 'HOLE:O164:instrument_definition' in result.hole_ids


def test_native_consumption_keeps_unknown_side_and_does_not_create_depth_events():
    from types import MappingProxyType
    from dataclasses import replace
    from trading_research.research.method_pack.native_resolution import ResolvedMembers
    from trading_research.research.method_pack.contracts import validate_output
    rows = tuple(MappingProxyType(dict(event_id=str(i),event_ns=i,known_at=i,
                    action='T',side=side,price=100,size=size,instrument_id=7))
                 for i,(side,size) in enumerate([('B',5),('A',3),('N',2)],1))
    resolved=ResolvedMembers(rows,7,0,10,3,True,())
    result=validate_output(p.native_o163({'use_at':10,'provided':999},resolved))
    assert result.value['consumed']==10 and result.value['two_sided_executions'] is True
    assert result.value['executed_by_aggressor']==dict(buy=5,sell=3,unknown=2)
    assert result.value['per_side_volumes']['buy']['consumed']==3
    assert result.value['per_side_volumes']['sell']['consumed']==5
    assert result.value['provide_events'] is None and result.value['withdraw_events'] is None
    assert result.value['order_states']=={} and result.value['source_process_complete'] is None
    assert result.value['event_ledger'][0]['passive_book_side']=='sell'
    assert result.value['event_ledger'][2]['passive_book_side'] is None
    only_buy=replace(resolved,members=rows[:1],coverage_ok=None)
    assert p.native_o163({'use_at':10},only_buy).value['two_sided_executions'] is None
    assert p.native_o163({'use_at':10},replace(only_buy,coverage_ok=True)).value['two_sided_executions'] is False
