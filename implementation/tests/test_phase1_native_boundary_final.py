"""Final C01 native admission attacks use actual Parquet bytes and definitions."""
from copy import deepcopy
from datetime import date
from decimal import Decimal
import json

import pytest
import pyarrow as pa
import pyarrow.parquet as pq

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.native_resolution import NativeResolver,NativeEvidenceError,file_digest
from trading_research.research.method_pack.objects import native_boundary as boundary
from trading_research.research.method_pack.evidence import mark_source_admitted

START=et_ns(date(2026,2,24),6)
MINUTE=60_000_000_000
BARS='quantpad/cme__nq-continuous-futures__ohlcv-1m'
TAPE='quantpad/cme__nq-continuous-futures__trades'
BBO='quantpad/cme__nq-continuous-futures__mbp-1'


@pytest.fixture
def market(tmp_path):
    values={BARS:[{'t':(START+i*MINUTE)//1_000_000,'o':100.,'h':101.,'l':99.,'c':100.5,'v':2,'instrument_id':7} for i in range(2)],
            TAPE:[{'t':START+1,'price':100.,'size':1,'side':'B','instrument_id':7},
                  {'t':START+MINUTE+1,'price':100.5,'size':1,'side':'A','instrument_id':7}],
            BBO:[{'t':START+1,'action':'A','side':'B','bid_px':100.,'ask_px':100.5,'bid_sz':5,'ask_sz':3,'instrument_id':7}]}
    locators={};owned=[]
    for dataset,rows in values.items():
        path=tmp_path/dataset/'native.parquet';path.parent.mkdir(parents=True)
        pq.write_table(pa.Table.from_pylist(rows),path,row_group_size=1)
        locators[dataset]={'source_file':str(path),'dataset_id':dataset,'sha256':file_digest(path),'row_start':0,'row_end':len(rows)}
        owned.append({'path':str(path),'start_ns':START,'end_ns':START+2*MINUTE})
    definitions=tmp_path/'derived/continuous-futures__instrument-and-roll-maps/nq-instruments.parquet'
    definitions.parent.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist([{'instrument_id':7,'root':'NQ','raw_symbol':'NQH6',
        'min_price_increment':'0.25','first_definition_ns':START-1}]),definitions)
    resolver=NativeResolver(tmp_path,owned_spans=owned)
    def obj(recipe='O004',dataset=BARS):
        return {'object_id':'native-1','recipe_id':recipe,'instrument_id':7,'method_id':'JJ-TBR',
                'formation_start':START,'formation_end':START+2*MINUTE,'as_of':START+2*MINUTE,
                'known_at':START+2*MINUTE,'parent_ids':[],
                'inputs':{'kind':'time','size_minutes':2,'use_at':START+2*MINUTE},'raw_member_locators':[deepcopy(locators[dataset])]}
    return resolver,obj,definitions


@pytest.mark.parametrize('key,value',[('q','1'),('tick_size','.5'),('q','NaN'),('tick_size',0),('q',True)])
def test_caller_cannot_override_native_instrument_tick(market,key,value):
    resolver,make,_=market;obj=make();obj['inputs'][key]=value
    with pytest.raises(NativeEvidenceError,match='tick unit'):boundary.run_native_object(obj,resolver)


def test_matching_tick_and_actual_complete_ohlcv_remain_admissible(market):
    resolver,make,_=market;obj=make();obj['inputs'].update(q='.25',tick_size=Decimal('.25'),O=999,candle={'O':999},members=[{'O':999}])
    result=boundary.run_native_object(obj,resolver)
    assert result.value['O']==100 and result.value['C']==Decimal('100.5') and result.value['V']==4
    assert result.coverage_ok is True and result.value['complete'] is True
    assert result.known_at==result.value['known_at']==START+2*MINUTE


def test_caller_tick_is_not_a_replacement_for_missing_definition(market):
    resolver,make,path=market;path.unlink();obj=make();obj['inputs']['q']='.25'
    with pytest.raises(NativeEvidenceError,match='actual native instrument definition'):boundary.run_native_object(obj,resolver)


@pytest.mark.parametrize('field',['as_of','formation_start','formation_end','start_ns','end_ns','window_start','window_end'])
def test_config_cannot_replace_envelope_window_or_snapshot(market,field):
    resolver,make,_=market;obj=make();obj['inputs'][field]=START+MINUTE
    with pytest.raises(NativeEvidenceError,match='window or snapshot mismatch'):boundary.run_native_object(obj,resolver)


def test_parent_dependencies_and_copied_native_measurements_are_not_caller_inputs(market,monkeypatch):
    resolver,make,_=market;obj=make();obj['parent_ids']=['real-parent']
    parent={'object_id':'real-parent','recipe_id':'O005','state':'computed','instrument_id':7,'method_id':'JJ-TBR',
            'value':{'H':101},'known_at':START-1,'recipe_base_ok':True,'recipe_coverage_ok':True}
    obj['inputs'].update(dependencies=[{'object_id':'real-parent','value':{'H':999},'known_at':0}],
                         parents={'fake':{'value':{'H':999}}},parent_ids=['fake'],instrument_definition={'tick_size':999},candle={'H':999},events=[{'price':999}],price=999,bid=999,ask=999,known_at=0)
    original=boundary.NATIVE_PRODUCERS['O004']
    def probe(config,resolved):
        assert config['dependencies'][0]['value']['H']==101
        assert config['parents']['real-parent']['known_at']==START-1
        assert config['parent_ids']==['real-parent']
        assert all(key not in config for key in ('candle','events','price','bid','ask'))
        assert config['known_at']==START+2*MINUTE
        assert config['instrument_definition'].tick_size==Decimal('.25')
        config['parents']['real-parent']['value']['H']=500
        return original(config,resolved)
    monkeypatch.setitem(boundary.NATIVE_PRODUCERS,'O004',probe)
    assert boundary.run_native_object(obj,resolver,parents=[parent]).coverage_ok is True
    assert parent['value']['H']==101


def test_unknown_parent_clock_cannot_be_replaced_by_claimed_dependency_clock(market):
    resolver,make,_=market;obj=make();obj['parent_ids']=['parent']
    parent={'object_id':'parent','state':'computed','instrument_id':7,'method_id':'JJ-TBR','known_at':None,
            'recipe_base_ok':True,'recipe_coverage_ok':True}
    obj['inputs']['dependencies']=[{'object_id':'parent','known_at':0}]
    result=boundary.run_native_object(obj,resolver,parents=[parent])
    assert result.known_at is None and result.value['known_at'] is None
    assert result.state=='hole' and 'HOLE:O004:availability' in result.hole_ids


def test_unverified_tape_coverage_cannot_be_promoted_by_native_adapter(market,monkeypatch):
    resolver,make,_=market;obj=make('O098',TAPE);obj['inputs'].update(coverage_ok=True,coverage_complete=True)
    original=boundary.NATIVE_PRODUCERS['O098']
    def falsely_complete(config,resolved):
        assert config['coverage_ok'] is None and config['coverage_complete'] is None
        result=original(config,resolved);result.coverage_ok=True;result.state='computed';return result
    monkeypatch.setitem(boundary.NATIVE_PRODUCERS,'O098',falsely_complete)
    result=boundary.run_native_object(obj,resolver)
    assert result.value['total']==2
    assert result.coverage_ok is None and result.state=='hole'
    assert 'HOLE:O098:native_coverage' in result.hole_ids


def test_literal_native_bbo_spread_does_not_require_complete_interval_tape(market):
    resolver,make,_=market;obj=make('O112',BBO)
    result=boundary.run_native_object(obj,resolver)
    assert result.value['spread_points']==Decimal('.5') and result.value['spread_ticks']==2
    assert result.coverage_ok is True and result.state=='computed'


def test_unknown_instrument_definition_clock_propagates_to_tick_measurement(market):
    resolver,make,path=market
    pq.write_table(pa.Table.from_pylist([{'instrument_id':7,'root':'NQ','min_price_increment':'.25','first_definition_ns':None}]),path)
    result=boundary.run_native_object(make('O112',BBO),resolver)
    assert result.value['spread_ticks']==2 and result.known_at is None and result.state=='hole'
    # A complete price bar does not consume the tick-unit definition.
    assert boundary.run_native_object(make(),resolver).known_at==START+2*MINUTE


def test_plain_clock_verified_boolean_is_not_author_source_evidence(market):
    resolver,make,_=market;obj=make('O003');obj['inputs']['clock_verified']=True
    result=boundary.run_native_object(obj,resolver)
    assert result.value['clock_verified'] is None and result.value['clock_check'] is None
    assert result.value['start_ns']==START and result.state=='hole'


def test_actual_catalog_clock_fact_is_verified_for_its_exact_native_window(market):
    resolver,make,_=market;obj=make('O003');end=et_ns(date(2026,2,24),9)
    obj.update(formation_end=end,as_of=end,known_at=end)
    obj['inputs'].update(use_at=end,source_configuration_id='jumbo-published-geometry',
                         source_configuration_version='2.0.0',source_setting_key='range_clock')
    result=boundary.run_native_object(obj,resolver)
    assert result.value['clock_verified'] is True and result.value['clock_check'] is True
    obj['formation_start']+=MINUTE
    with pytest.raises(NativeEvidenceError):boundary.run_native_object(obj,resolver)


def test_source_clock_parent_must_be_admitted_and_match_exact_window(market):
    resolver,make,_=market;obj=make('O003');obj['parent_ids']=['clock'];obj['inputs']['clock_parent_id']='clock'
    parent={'object_id':'clock','state':'supplied','method_id':'JJ-TBR','instrument_id':7,'known_at':START-1,
            'recipe_base_ok':True,'recipe_coverage_ok':True,
            'value':{'clock_verified':True,'start_ns':START,'end_ns':START+2*MINUTE}}
    with pytest.raises(NativeEvidenceError,match='full source audit'):boundary.run_native_object(obj,resolver,parents=[parent])
    for field in parent['value']:mark_source_admitted(parent,field)
    assert boundary.run_native_object(obj,resolver,parents=[parent]).value['clock_verified'] is True
    parent['value']['end_ns']-=MINUTE
    with pytest.raises(NativeEvidenceError,match='different exact window'):boundary.run_native_object(obj,resolver,parents=[parent])


def test_derived_geometry_uses_distinct_real_parent_windows_without_shared_envelope(market):
    resolver,make,_=market;parents=[]
    for i in range(2):
        obj=make();obj.update(object_id=f'bar-{i}',formation_start=START+i*MINUTE,formation_end=START+(i+1)*MINUTE,
                              as_of=START+(i+1)*MINUTE,known_at=START+(i+1)*MINUTE)
        obj['inputs'].update(size_minutes=1,use_at=START+2*MINUTE)
        obj['raw_member_locators'][0].update(row_start=i,row_end=i+1)
        result=boundary.run_native_object(obj,resolver)
        parents.append({**obj,'state':result.state,'value':result.value,'known_at':result.known_at,
                        'recipe_base_ok':result.base_ok,'recipe_coverage_ok':result.coverage_ok,
                        'evidence_class':result.evidence_class})
    derived={'object_id':'quadrants','recipe_id':'O007','instrument_id':7,'method_id':'JJ-TBR',
             'parent_ids':['bar-0','bar-1'],'inputs':{'range_parent_id':'bar-0','use_at':START+2*MINUTE}}
    result=boundary.run_native_object(derived,resolver,parents=parents)
    assert result.value['eq']==100 and result.value['q25']==Decimal('99.5')
    assert result.known_at==START+2*MINUTE and result.evidence_class=='parent_derived'
    assert 'formation_start' not in derived and 'as_of' not in derived['inputs']
    parents[1]['known_at']=None
    assert boundary.run_native_object(derived,resolver,parents=parents).known_at is None
    declared={**derived,'formation_start':START,'formation_end':START+2*MINUTE,
              'inputs':{**derived['inputs'],'window_end':START+MINUTE}}
    with pytest.raises(NativeEvidenceError,match='window or snapshot mismatch'):
        boundary.run_native_object(declared,resolver,parents=parents)


def test_raw_object_still_requires_both_envelope_endpoints(market):
    resolver,make,_=market;obj=make();del obj['formation_start']
    with pytest.raises(NativeEvidenceError,match='both endpoints'):boundary.run_native_object(obj,resolver)
