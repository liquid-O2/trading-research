"""Graph-level native local-flow regressions using immutable Parquet members."""
from copy import deepcopy
from datetime import date
from decimal import Decimal
import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.native_resolution import NativeEvidenceError, NativeResolver, file_digest
from trading_research.research.method_pack.objects.native_boundary import run_native_object
from trading_research.research.method_pack.objects.local_flow import DERIVED_PARENT_ROLES
from trading_research.research.method_pack import objects  # noqa: F401 - install producers


START=et_ns(date(2026,1,15),10,0)
MIN=60_000_000_000
TRADES="quantpad/cme__nq-continuous-futures__trades"
OHLC="quantpad/cme__nq-continuous-futures__ohlcv-1m"
MBP="quantpad/cme__nq-continuous-futures__mbp-1"


def _write_parquet(root,dataset,name,rows):
    path=root/dataset/name; path.parent.mkdir(parents=True,exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows),path)
    return path


def _locator(path,dataset,count):
    return {"source_file":str(path),"dataset_id":dataset,"sha256":file_digest(path),
            "row_start":0,"row_end":count}


def _resolver(root,path,locator,start,end):
    return NativeResolver(root,owned_spans=[{"path":str(path),"start_ns":start,"end_ns":end}],
        coverage_records=[{"instrument_id":7,"start_ns":start,"end_ns":end,
            "sources":[{"source_file":str(path),"sha256":locator["sha256"]}],
            "member_locators":[locator],"coverage_ok":True,"missing_intervals":[]}])


def _object(rid,loc,start,end,inputs,*,parents=()):
    return {"object_id":f"test:{rid}","recipe_id":rid,"instrument_id":7,
            "formation_start":start,"formation_end":end,"as_of":end,"known_at":end,
            "raw_member_locators":[] if loc is None else [loc],
            "parent_ids":[p["object_id"] for p in parents],"inputs":inputs}


def _parent(object_id,result):
    return {"object_id":object_id,"recipe_id":result.recipe_id,"instrument_id":7,
            "state":result.state,"known_at":result.known_at,"value":result.value,
            "recipe_base_ok":result.base_ok,"recipe_coverage_ok":result.coverage_ok,
            "hole_ids":result.hole_ids,"evidence_class":result.evidence_class}


@pytest.fixture
def native_graph(tmp_path):
    definitions=tmp_path/"derived/continuous-futures__instrument-and-roll-maps/nq-instruments.json"
    definitions.parent.mkdir(parents=True)
    definitions.write_text(json.dumps([{"instrument_id":7,"root":"NQ","raw_symbol":"NQH6",
        "min_price_increment":"0.25","first_definition_ns":START-1}]))
    bars=[{"t":(START+i*MIN)//1_000_000,"o":100+i,"h":101+i,"l":99+i,
           "c":Decimal("100.5")+i,"v":10,"instrument_id":7} for i in range(2)]
    bar_path=_write_parquet(tmp_path,OHLC,"bars.parquet",bars); bar_loc=_locator(bar_path,OHLC,2)
    trades=[{"t":START+offset,"price":price,"size":size,"side":side,
             "instrument_id":7,"exchange_sequence":seq}
            for seq,(offset,price,size,side) in enumerate(((1_000_000_000,100,3,"B"),
                (20_000_000_000,Decimal("100.25"),1,"A"),(70_000_000_000,101,5,"B")),1)]
    trade_path=_write_parquet(tmp_path,TRADES,"trades.parquet",trades); trade_loc=_locator(trade_path,TRADES,3)
    bar_resolver=_resolver(tmp_path,bar_path,bar_loc,START,START+2*MIN)
    trade_resolver=_resolver(tmp_path,trade_path,trade_loc,START,START+2*MIN)
    bar=run_native_object(_object("O004",bar_loc,START,START+2*MIN,
        {"kind":"time","size_minutes":2,"bar_id":"candle","use_at":START+2*MIN}),bar_resolver)
    bar_parent=_parent("bar",bar)
    footprint_obj=_object("O120",trade_loc,START,START+2*MIN,
        {"poc_tie_policy":"lowest"},parents=[bar_parent])
    footprint=run_native_object(footprint_obj,trade_resolver,parents=[bar_parent])
    return trade_resolver,trade_loc,bar_parent,_parent("footprint",footprint),footprint


def test_real_parquet_native_and_derived_graph_uses_actual_candle_tick_and_rows(native_graph):
    resolver,loc,bar,footprint_parent,footprint=native_graph
    assert footprint.state=="computed"
    assert footprint.value["tick_size"]==Decimal("0.25")
    assert footprint.value["candle_id"]=="candle"
    assert footprint.value["candle_definition"]=={"candle_id":"candle",
        "start_ns":START,"end_ns":START+2*MIN,"defined_at":START}
    derived=_object("O109",None,START,START+2*MIN,{"ratio_min":4,"row_count":1,
        "zero_rule":"does_not_qualify","parent_roles":{"footprint":"footprint"}},parents=[footprint_parent])
    result=run_native_object(derived,None,parents=[footprint_parent])
    assert result.evidence_class=="parent_derived"
    assert result.value["candle_id"]=="candle"
    assert result.parent_ids==["footprint"]


def test_caller_tick_and_candle_cannot_replace_resolved_parents(native_graph):
    resolver,loc,bar,_,_=native_graph
    obj=_object("O120",loc,START,START+2*MIN,
        {"tick_size":"1","candle":{"bar_id":"fake","O":999,"H":999,"L":999,"C":999}},parents=[bar])
    with pytest.raises(NativeEvidenceError,match="tick"):
        run_native_object(obj,resolver,parents=[bar])
    obj["inputs"].pop("tick_size")
    result=run_native_object(obj,resolver,parents=[bar])
    assert result.value["candle_id"]=="candle"
    assert result.value["O"]==Decimal(100)


def test_latest_native_quote_timestamp_tie_requires_exchange_order(tmp_path):
    definitions=tmp_path/"derived/continuous-futures__instrument-and-roll-maps/nq-instruments.json"
    definitions.parent.mkdir(parents=True)
    definitions.write_text(json.dumps([{"instrument_id":7,"root":"NQ","min_price_increment":"0.25"}]))
    rows=[{"t":START+1,"action":"M","side":"B","price":100,"size":10,
           "bid_px":100,"ask_px":Decimal("100.25"),"bid_sz":10,"ask_sz":12,"instrument_id":7},
          {"t":START+1,"action":"M","side":"B","price":100,"size":11,
           "bid_px":100,"ask_px":Decimal("100.25"),"bid_sz":11,"ask_sz":12,"instrument_id":7}]
    path=_write_parquet(tmp_path,MBP,"quotes.parquet",rows); loc=_locator(path,MBP,2)
    resolver=_resolver(tmp_path,path,loc,START,START+MIN)
    with pytest.raises(NativeEvidenceError,match="unknown order"):
        run_native_object(_object("O112",loc,START,START+MIN,{}),resolver)


def test_native_approach_with_unknown_tied_order_preserves_only_exact_totals(tmp_path):
    definitions=tmp_path/"derived/continuous-futures__instrument-and-roll-maps/nq-instruments.json"
    definitions.parent.mkdir(parents=True)
    definitions.write_text(json.dumps([{"instrument_id":7,"root":"NQ",
        "min_price_increment":"0.25"}]))
    rows=[{"t":START+1,"price":100,"size":2,"side":"B","instrument_id":7},
          {"t":START+1,"price":Decimal("100.25"),"size":3,"side":"B","instrument_id":7},
          {"t":START+2,"price":Decimal("100.5"),"size":1,"side":"A","instrument_id":7}]
    path=_write_parquet(tmp_path,TRADES,"trades.parquet",rows); loc=_locator(path,TRADES,3)
    resolver=_resolver(tmp_path,path,loc,START,START+MIN)
    result=run_native_object(_object("O113",loc,START,START+MIN,{}),resolver)
    assert result.state=="hole"
    assert result.value["from_price"] is None
    assert result.value["path_distance"] is None
    assert result.value["aggressive_buy_volume"]==Decimal(5)
    assert result.value["aggressive_sell_volume"]==Decimal(1)
    assert "HOLE:O113:event_order" in result.hole_ids


def test_derived_role_map_rejects_unselected_actual_parent(native_graph):
    _,_,bar,footprint,wholesale=native_graph
    obj=_object("O106",None,START,START+2*MIN,
        {"parent_roles":{"candle":"bar","footprint":"footprint"}},parents=[bar,footprint])
    extra={**footprint,"object_id":"extra"}
    obj["parent_ids"].append("extra")
    result=run_native_object(obj,None,parents=[bar,footprint,extra])
    assert result.state=="invalid"
    assert "cover each actual parent" in result.reason


def test_o108_requires_one_identical_full_candle_definition(native_graph):
    _,_,_,footprint,_=native_graph
    first=deepcopy(footprint); first["object_id"]="snapshot-1"
    second=deepcopy(footprint); second["object_id"]="snapshot-2"
    first["known_at"]=START+2*MIN-1
    second["known_at"]=START+2*MIN
    parents=[first,second]
    obj=_object("O108",None,START,START+2*MIN,{"parent_roles":{
        "snapshots":["snapshot-1","snapshot-2"]}},parents=parents)
    same=run_native_object(obj,None,parents=parents)
    assert same.state=="computed"
    assert same.value["same_candle"] is True
    assert same.value["candle_definition"]==first["value"]["candle_definition"]

    mismatched=deepcopy(parents)
    mismatched[1]["value"]["candle_definition"]["end_ns"]+=MIN
    rejected=run_native_object(obj,None,parents=mismatched)
    assert rejected.state=="invalid"
    assert rejected.value["same_candle"] is False

    missing=deepcopy(parents)
    missing[1]["value"].pop("candle_definition")
    unresolved=run_native_object(obj,None,parents=missing)
    assert unresolved.state=="hole"
    assert unresolved.value["same_candle"] is None


def test_every_supported_local_arithmetic_has_a_registered_derived_route():
    expected={"O099","O100","O101","O102","O103","O104","O106","O107","O108",
              "O109","O110","O114","O115","O116","O117","O118","O119"}
    assert set(DERIVED_PARENT_ROLES)==expected


def test_source_composite_ignores_manifest_scalar_facts():
    def parent(object_id,recipe_id,known_at,value):
        return {"object_id":object_id,"recipe_id":recipe_id,"instrument_id":7,"state":"computed",
                "known_at":known_at,"value":value,"recipe_base_ok":True,
                "recipe_coverage_ok":True,"hole_ids":[]}
    parents=[
        parent("defense","O100",1,{"band":[100,100],"defense_interpretation":"buy",
            "local_executions":[{"event_ns":1}]}),
        parent("replenishment","O102",2,{"price":100,"verified_replenishment":True,
            "refresh_events":[{"event_ns":2}]}),
        parent("exhaustion","O114",3,{"declining":True,"source_classification":True,
            "window_end":3}),
        parent("aggression","O098",4,{"event_records":[{"event_id":"buy","event_key":4,
            "known_at":4,"price":Decimal("100.75"),"executed_size":2,"side":"B"}]}),
        parent("liftoff","O104",4,{"direction":"long","reward_price":101,
            "reward_at":4,"directional_reward":True}),
        parent("decision","O004",5,{"C":Decimal("101.25"),"decision_at":5}),
        parent("tick","O120",5,{"tick_size":Decimal("0.25")}),
    ]
    roles={name:name for name in ("defense","replenishment","exhaustion","aggression","liftoff","decision","tick")}
    obj=_object("O115",None,START,START+MIN,{"parent_roles":roles,"origin":999,
        "direction":"short","reward_price":0,"stage_ledger":{"defense":99}},parents=parents)
    result=run_native_object(obj,None,parents=parents)
    assert result.value["origin"]==Decimal(100)
    assert result.value["direction"]=="long"
    assert result.value["reward_price"]==Decimal(101)
    assert result.value["stage_ledger"]=={"defense":1,"replenishment":2,"exhaustion":3,
                                          "liftoff":4,"entry":5}

    absent=deepcopy(parents)
    absent[1]["value"]["verified_replenishment"]=None
    absent[3]["value"]["event_records"]=[]
    hole=run_native_object(obj,None,parents=absent)
    assert hole.state=="hole"
    assert hole.value["stage_ledger"]["replenishment"] is None
    assert hole.value["defender_aggression_events"]==[]


def test_native_o105_and_o113_reject_caller_measurements(native_graph):
    resolver,loc,_,_,_=native_graph
    cvd=_object("O105",loc,START,START+2*MIN,{"reset_policy":{"policy_id":"window",
        "start_ns":START,"kind":"declared_comparison"}})
    result=run_native_object(cvd,resolver)
    assert result.value["known_cvd"]==Decimal(7)
    assert result.value["reference"] is None
    assert result.state=="hole"
    cvd["inputs"]["reference"]=999
    with pytest.raises(NativeEvidenceError,match="caller observation"):
        run_native_object(cvd,resolver)

    approach=_object("O113",loc,START,START+2*MIN,{})
    actual=run_native_object(approach,resolver)
    assert actual.value["from_price"]==Decimal(100)
    assert actual.value["to_price"]==Decimal(101)
    approach["inputs"]["from_px"]=999
    with pytest.raises(NativeEvidenceError,match="actual native executions"):
        run_native_object(approach,resolver)


def test_o117_uses_actual_touch_ledger_and_o118_requires_observed_stage_qualifiers():
    def parent(object_id,recipe_id,known_at,value):
        return {"object_id":object_id,"recipe_id":recipe_id,"instrument_id":7,"state":"computed",
                "known_at":known_at,"value":value,"recipe_base_ok":True,
                "recipe_coverage_ok":True,"hole_ids":[]}
    zone=parent("zone","O116",0,{"zone_id":"z","zone":[100,101],
        "zone_definition_recorded":True,"zone_frozen":True})
    current=parent("current","O002",10,{"contact_at":10})
    cutoff=parent("cutoff","O003",9,{"bar_close_at":9})
    history=parent("history","O116",12,{"zone_id":"z","touch_ledger":[
        {"id":"a","zone_id":"z","start":1,"defense_at":3},
        {"id":"b","zone_id":"z","start":5,"defense_at":12}]})
    parents=[zone,current,cutoff,history]
    obj=_object("O117",None,START,START+MIN,{"parent_roles":{"zone":"zone",
        "current_touch":"current","feature_cutoff":"cutoff","history":["history"]}},parents=parents)
    memory=run_native_object(obj,None,parents=parents)
    assert memory.value["eligible_history_ids"]==["a"]
    assert memory.value["unresolved_history_ids"]==["b"]
    assert memory.value["prior_resolved_defense_count"]==1
    no_ledger=deepcopy(parents);no_ledger[-1]["value"]={"zone_id":"z","touch_ids":["a","b"],"touch_at":1}
    assert run_native_object(obj,None,parents=no_ledger).state=="hole"

    stages=[zone,
        parent("failure","O107",2,{"source_spike":True}),
        parent("release","O104",1,{"directional_reward":True,"reward_at":1}),
        parent("refill","O102",4,{"verified_replenishment":True,
            "refresh_events":[{"event_ns":4}]}),
        parent("drive","O104",5,{"directional_reward":True,"reward_at":5}),
        parent("hold","O002",6,{"source_hold":True,"contact_at":6}),
        parent("decision","O150",7,{"decision_at":7})]
    roles={"origin":"zone","failed_pushes":["failure"],"release":"release","refill":"refill",
           "drive":"drive","hold":"hold","decision":"decision"}
    origin_obj=_object("O118",None,START,START+MIN,{"parent_roles":roles},parents=stages)
    complete=run_native_object(origin_obj,None,parents=stages)
    assert complete.value["branch_ok"] is True
    missing=deepcopy(stages);missing[3]["value"]["verified_replenishment"]=None
    hole=run_native_object(origin_obj,None,parents=missing)
    assert hole.state=="hole"
    assert "refill" in hole.value["missing_stages"]


def test_o116_needs_source_zone_qualifier_and_literal_touch_event():
    def parent(object_id,recipe_id,known_at,value):
        return {"object_id":object_id,"recipe_id":recipe_id,"instrument_id":7,"state":"computed",
                "known_at":known_at,"value":value,"recipe_base_ok":True,
                "recipe_coverage_ok":True,"hole_ids":[]}
    formation=parent("formation","O099",1,{"source_setting_id":"source-zone-rule",
        "source_display_known":None,"marker_events":[
            {"event_ids":["m1"],"event_ns":1,"price":100},
            {"event_ids":["m2"],"event_ns":1,"price":101}]})
    departure=parent("departure","O104",2,{"reward_price":102,"reward_at":2})
    touch=parent("touch","O002",3,{"touch_id":"t1","touch_at":3,"touch_price":Decimal("100.5")})
    parents=[formation,departure,touch]
    obj=_object("O116",None,START,START+MIN,{"parent_roles":{"formation":"formation",
        "departure":"departure","touches":["touch"]}},parents=parents)
    unknown=run_native_object(obj,None,parents=parents)
    assert unknown.state=="hole"
    assert unknown.value["zone"] is None
    actual=deepcopy(parents);actual[0]["value"]["source_display_known"]=True
    result=run_native_object(obj,None,parents=actual)
    assert result.value["zone"]==[Decimal(100),Decimal(101)]
    assert result.value["touch_ids"]==["t1"]
    missing_touch=deepcopy(actual);missing_touch[-1]["value"]={"contact_at":3}
    assert run_native_object(obj,None,parents=missing_touch).state=="hole"


def test_bbo_consumption_requires_explicit_side_and_preserves_unknown_aggressor():
    def parent(object_id,recipe_id,known_at,value):
        return {"object_id":object_id,"recipe_id":recipe_id,"instrument_id":7,"state":"computed",
                "known_at":known_at,"value":value,"recipe_base_ok":True,
                "recipe_coverage_ok":True,"hole_ids":[]}
    records=[{"event_id":"sell","event_key":2,"known_at":2,"price":Decimal(100),"executed_size":3,"side":"A"},
             {"event_id":"buy","event_key":2,"known_at":2,"price":Decimal(100),"executed_size":2,"side":"B"},
             {"event_id":"unknown","event_key":2,"known_at":2,"price":Decimal(100),"executed_size":1,"side":"N"}]
    tape=parent("tape","O098",2,{"event_records":records})
    before=parent("before","O112",1,{"quote_id":"q1","bid":Decimal(100),"ask":Decimal("100.25"),"bid_size":10,"ask_size":10})
    after=parent("after","O112",3,{"quote_id":"q2","bid":Decimal(100),"ask":Decimal("100.25"),"bid_size":12,"ask_size":10})
    parents=[tape,before,after]
    obj=_object("O102",None,START,START+MIN,{"comparison_side":"bid","parent_roles":{
        "executions":"tape","quote_before":"before","quote_after":"after"}},parents=parents)
    replenishment=run_native_object(obj,None,parents=parents)
    assert [row["event_id"] for row in replenishment.value["consumption_events"]]==["sell","unknown"]
    assert replenishment.value["consumption"]==Decimal(4)
    assert replenishment.value["bbo_reload_inference"] is None
    assert "HOLE:O102:aggressor_side" in replenishment.hole_ids

    tick=parent("tick","O120",3,{"tick_size":Decimal("0.25")})
    iceberg_parents=[tape,after,tick]
    no_side=_object("O103",None,START,START+MIN,{"parent_roles":{"executions":"tape",
        "quote":"after","tick":"tick"}},parents=iceberg_parents)
    assert run_native_object(no_side,None,parents=iceberg_parents).value["area"] is None
    no_side["inputs"]["comparison_side"]="bid"
    selected=run_native_object(no_side,None,parents=iceberg_parents)
    assert selected.value["area"]==Decimal(100)
    assert selected.value["executed_total"]==Decimal(6)
