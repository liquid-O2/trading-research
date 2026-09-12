from copy import deepcopy
from decimal import Decimal as D

import pytest

from trading_research.research.method_pack.objects import context_observations as c
from trading_research.research.method_pack.source_config import (
    SourceConfigurationError, SourceSetting, case_record, configuration, load_catalog,
)


def test_context_snapshot_ignores_future_vintage_and_retains_supporting_clocks():
    inp=dict(use_at=20,observations=[dict(value=18,available_at=10,observation_at=9,unit='index_points')])
    before=c.o042(inp)
    inp['observations'].append(dict(value=25,available_at=30,observation_at=31,unit='index_points'))
    after=c.o042(inp)
    assert after.value==before.value and after.state==before.state and after.known_at==10
    regime=c.o033(dict(source_regime='short_gamma',branch='ofm_aggressive',known_at=5,use_at=20,
       native_identity=dict(is_0dte=True,source_product_ok=True,known_at=4),rereads=[dict(known_at=15)]))
    assert regime.known_at==15
    kg=c.o041(dict(kg1=100,kg1_id='kg',known_at=5,use_at=20,reason_records=[
       dict(role='prior_reaction',object_id='reaction',known_at=12,evidence_ids=['reaction-record']),
       dict(role='minor_hvn',object_id='hvn',known_at=15,evidence_ids=['hvn-record'])]))
    assert kg.known_at==15 and kg.value['two_reason_ok'] is True


def test_native_vwap_requires_exact_resolved_window_and_catalog_source_settings():
    from trading_research.research.method_pack.native_resolution import ResolvedMembers, NativeEvidenceError
    rows=tuple(dict(event_id=str(i),dataset_id='bars',instrument_id='nq',start=i,end=i+1,
                    known_at=i+1,O=D(100),H=D(102),L=D(99),C=D(101),V=D(10),complete=True) for i in range(2))
    resolved=ResolvedMembers(rows,'nq',0,2,2,True,())
    cfg=dict(reset_at=0,reset_id='r',reset_verified=True,as_of=2,basis='HLC3',source_basis_verified=True)
    source=c.native_vwap(cfg,resolved)
    assert source.value['faithful'] is None and source.value['vwap'] is None
    assert source.value['comparison_vwap']==D(302)/3
    cfg['variant']='comparison'
    assert c.native_vwap(cfg,resolved).value['vwap']==D(302)/3
    cfg['reset_at']=1
    with pytest.raises(NativeEvidenceError,match='exactly match'):
        c.native_vwap(cfg,resolved)


def tape():
    return dict(instrument_id='nq',canonical_tape_id='trades',reset_id='r',reset_at=0,
        reset_verified=True,basis='trade_price',coverage_complete=True,as_of=20,use_at=21,
        trades=[dict(event_id='a',event_ns=10,known_at=10,instrument_id='nq',dataset_id='trades',price=100,size=2,side='B',action='T'),
                dict(event_id='b',event_ns=20,known_at=20,instrument_id='nq',dataset_id='trades',price=104,size=1,side='N',action='T')])


def test_vwap_unknown_volume_quotes_and_future_tail_snapshot_invariance():
    inp=tape();first=c.o030(inp)
    assert first.state=='computed'
    assert first.value['vwap']==D(304)/3
    inp['trades'] += [dict(event_id='future',event_ns=30,known_at=30,price=1000,size=99,action='T'),
                     dict(event_id='quote',event_ns=11,known_at=11,price=2000,size=99,action='A')]
    assert c.o030(inp).value == first.value
    assert first.known_at==20
    inp['coverage_complete']=None
    hole=c.o030(inp)
    assert hole.value['vwap'] is None and hole.value['comparison_vwap']==D(304)/3
    assert hole.coverage_ok is None


def test_vwap_rejects_duplicate_cross_contract_and_contact_batch():
    inp=tape();inp['trades'].append(deepcopy(inp['trades'][0]))
    assert c.o030(inp).base_ok is False
    inp=tape();inp['trades'][0]['instrument_id']='es'
    assert c.o030(inp).base_ok is False
    inp=tape();inp['touch_at']=20
    assert c.o030(inp).base_ok is False


def test_anchored_vwap_availability_is_latest_incorporated_fact():
    inp=tape();inp.update(anchor_id='swing',anchor_price_at=0,anchor_known_at=5,
        anchor_selected_at=5,anchor_reason='cited confirmed swing')
    result=c.o031(inp)
    assert result.value['avwap']==D(304)/3
    assert result.known_at==result.value['usable_at']==20
    inp.update(use_at=15,known_at=5)
    assert c.o031(inp).base_ok is False


def test_complete_bar_basis_is_explicit_and_uses_close_availability():
    inp=tape();inp.pop('trades');inp.update(basis='HLC3',variant='comparison',as_of=20,
        bars=[dict(bar_id='a',instrument_id='nq',dataset_id='trades',start=0,end=10,known_at=10,complete=True,O=98,H=104,L=98,C=101,V=2),
              dict(bar_id='b',instrument_id='nq',dataset_id='trades',start=10,end=20,known_at=20,complete=True,O=101,H=108,L=100,C=104,V=1)])
    r=c.o030(inp)
    assert r.value['vwap']==D(306)/3 and r.value['faithful'] is None
    assert r.known_at==20
    inp['variant']='source'
    assert c.o030(inp).value['vwap'] is None
    inp['source_basis_verified']=True
    assert c.o030(inp).value['faithful'] is True
    inp['bars'][1]['start']=11
    assert c.o030(inp).value['vwap'] is None


def test_deviation_parent_reset_and_snapshot_cannot_be_mixed():
    inp=dict(mu=100,sigma=2,k='2.5',variance_convention='supplied-platform',band_id='b',parent_snapshot_id='v',
        vwap_known_at=10,sigma_known_at=12,as_of=12,use_at=15,touch_at=14,
        reset_id='r',sigma_reset_id='r',weighting_universe='tape',sigma_weighting_universe='tape')
    r=c.o032(inp)
    assert r.value['band']==[D(95),D(105)] and r.known_at==12
    inp['sigma_reset_id']='another'
    assert c.o032(inp).base_ok is False


def test_option_native_key_and_contemporaneous_explicit_mapping():
    inp=dict(symbol='QQQ',option_class='QQQ',expiration='2026-01-15',strike='500',right='C',
        osi_symbol='QQQ260115C00500000',observation_at=1768489200000000000,
        available_at=1768489200000000000,source_product='QQQ',use_at=1768489260000000000,unit='ETF_price')
    r=c.o034(inp)
    assert r.value['is_0dte'] is True and len(r.value['native_contract_key'])==6
    inp['mapping']=25000
    assert c.o034(inp).value['mapped_price'] is None
    inp['mapping']=dict(mapping_id='m',source_ref='source',from_product='QQQ',to_instrument_id='NQH6',known_at=1768489200000000000,mapped_price='25000')
    assert c.o034(inp).value['mapped_price']==D(25000)
    inp['mapping']['from_product']='SPY'
    assert c.o034(inp).base_ok is False


def test_latest_available_context_and_ambiguous_ties():
    inp=dict(use_at=20,observations=[dict(value=20,unit='index_points',observation_at=9,available_at=10),
                                   dict(value=25,unit='index_points',observation_at=29,available_at=30)])
    r=c.o042(inp)
    assert r.value['available_vix']==20 and r.value['age_ns']==10
    inp['observations'].append(dict(value=21,unit='index_points',observation_at=9,available_at=10))
    assert c.o042(inp).value['available_vix'] is None
    assert c.o045(dict(vvix=100,use_at=20)).value['usable'] is None
    assert c.o042(dict(vix=20,publication_at=30,use_at=20)).value['faithful_preopen'] is None


def test_daily_fraction_and_event_change_have_distinct_units_and_availability():
    r=c.o043(dict(vix=20,P=5000,conversion_instrument_id='ES',vix_known_at=10,price_known_at=11,use_at=12))
    assert r.value['daily_fraction']==r.value['daily_move_percent']/100
    assert r.value['point_estimate']==5000*r.value['daily_fraction']
    assert r.known_at==11
    inp=dict(tenor_values=[dict(tenor='near',value=20,unit='index',known_at=10),dict(tenor='far',value=22,unit='index',known_at=10)],
             operation='both',post_near=16,post_at=30,use_at=20)
    r=c.o044(inp)
    assert r.value['difference']==2 and r.value['far_over_near']==D('1.1') and r.value['event_change'] is None
    assert r.known_at==10
    inp['use_at']=30
    assert c.o044(inp).value['event_change']==-4 and c.o044(inp).known_at==30


def test_readouts_preserve_missing_units_and_kg1_is_not_two_reasons():
    assert 'HOLE:O038:unit' in c.o038(dict(source_value=500,known_at=10)).hole_ids
    r=c.o039(dict(source_vol_gex=12,unit='U',interpretation='source uncertain',known_at=10))
    assert r.value['interpretation']=='source uncertain'
    r=c.o041(dict(kg1=[100,101],kg1_id='kg',hvn_id='h',known_at=10,use_at=20))
    assert r.value['two_reason_ok'] is None
    r=c.o036(dict(walls=[dict(id='w',price=100,rank=1,unit='ETF',known_at=10)],max_pain_id='w'))
    assert r.base_ok is False


def test_wall_flip_and_max_pain_identities_units_and_clocks():
    flip=c.o035(dict(flip=100,spot=99,unit='QQQ',spot_unit='QQQ',flip_known_at=5,spot_known_at=10,use_at=11))
    assert flip.value['relation']=='below' and flip.value['spot_minus_flip']==-1 and flip.known_at==10
    assert c.o035(dict(flip=100,spot=101,unit='QQQ',spot_unit='NQ',known_at=5,spot_known_at=5)).base_ok is False
    walls=c.o036(dict(walls=[dict(id='put',price=100,unit='QQQ',known_at=5),
                             dict(id='call',price=100,unit='QQQ',known_at=6)],
                      max_pain_id='pain',spot=101,spot_unit='QQQ',spot_known_at=7,use_at=8))
    assert walls.value['distinct_ids']==3 and walls.known_at==7
    assert walls.value['spot_relation']==dict(put='above',call='above')
    pain=c.o037(dict(max_pain=100,put_wall=100,max_pain_id='pain',put_wall_id='put',known_at=5,wall_known_at=6))
    assert pain.value['equal_put_wall'] is True and pain.value['relation_to_separate_walls'][0]['same_identity'] is False
    assert c.o037(dict(max_pain=100,max_pain_id='same',put_wall_id='same',known_at=5)).base_ok is False
    gauge=c.o040(dict(gauge=80,scale='custom_score',known_at=5))
    assert gauge.value['as_percent'] is None and gauge.value['entry_permission'] is None


def test_configuration_facts_do_not_upgrade_inferences_or_other_authors():
    from trading_research.research.method_pack import METHOD_IDS
    cases=load_catalog()['cases']
    assert len(cases)==22
    assert {case['method_id'] for case in cases}==set(METHOD_IDS)
    assert {case['case_id'] for case in cases if case['method_id']=='GB-SCALP'}=={
        'GB-SCALP-bearish','GB-SCALP-bullish'}
    cfg=configuration('sires-vwap-illustration',author='Sires')
    assert cfg['settings']['anchor']=='Session' and cfg['settings']['price_basis'] is None
    assert cfg['settings']['source_price_label']=='(H + L + …)'
    with pytest.raises(SourceConfigurationError):configuration('sires-vwap-illustration',author='Green Bird')
    assert configuration('gb-vwap-continuation',author='Green Bird')['settings']['prior_comparison'] is None
    assert configuration('gb-vwap-continuation',author='Green Bird',comparison=True)['settings']['prior_comparison']['basis']=='HLC3'
    with pytest.raises(SourceConfigurationError):SourceSetting.parse(dict(status='unknown',value='HLC3',source_refs=['VWAP:8'],reason='truncated'))
    case=case_record('GB-FAIL-2025-11-20')
    assert case['observed_decision']['value']['sequence']=='entry_at_high_sweep'
    assert case['instrument']['value']=='MNQZ2025' and case['historical_candidate'] is False
    assert case['later_annotations'][0]['entry_prerequisite'] is False
    loss=case_record('SIRES-losses-2026-07-23')
    assert [a['outcome'] for a in loss['observed_decision']['value']['attempts']][:3]==['loss','loss','win']
