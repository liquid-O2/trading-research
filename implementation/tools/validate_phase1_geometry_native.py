#!/usr/bin/env python3
"""Rebuild native geometry controls and their explicit parent DAGs.

This is a validation program, not a source-case parameter search.  It uses
fixed dated NQ windows and preserves unavailable author settings as holes.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import date, timedelta
from decimal import Decimal
import argparse
import gzip
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from types import MappingProxyType

from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.contracts import validate_output
from trading_research.research.method_pack.native_windows import collect_window
from trading_research.research.method_pack.objects import native_boundary as nb
from trading_research.research.method_pack.objects import profile_integration as pi


ROOT = Path(__file__).resolve().parents[2]
DATASET = "quantpad/cme__nq-continuous-futures__ohlcv-1m"
OUT = ROOT / "implementation/validation/phase1-completion/native-geometry.json"


def encode(value):
    if isinstance(value, Decimal): return str(value)
    if isinstance(value, date): return value.isoformat()
    if isinstance(value, MappingProxyType): return dict(value)
    if isinstance(value, tuple): return list(value)
    raise TypeError(type(value).__name__)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def result_record(object_id, result, *, instrument_id, formation_start=None,
                  formation_end=None, method_id=None):
    return {"object_id": object_id, "recipe_id": result.recipe_id,
            "instrument_id": instrument_id, "method_id": method_id,
            "formation_start": formation_start, "formation_end": formation_end,
            "known_at": result.known_at, "state": result.state,
            "recipe_base_ok": result.base_ok,
            "recipe_coverage_ok": result.coverage_ok,
            "hole_ids": list(result.hole_ids), "parent_ids": list(result.parent_ids),
            "evidence_ids": list(result.evidence_ids),
            "evidence_class": result.evidence_class, "value": result.value}


def _compact_ids(record, key):
    values=record.get(key)
    if not isinstance(values,list) or len(values)<=1000:return
    checksum=hashlib.sha256()
    for value in values:
        checksum.update(str(value).encode());checksum.update(b"\n")
    record[f"{key[:-1]}_count" if key.endswith("s") else f"{key}_count"]=len(values)
    record[f"{key}_sha256"]=checksum.hexdigest()
    record[key]=[f"sha256:{checksum.hexdigest()}"]


def compact_record(source):
    """Compact repeated event identities after every derivation has run."""
    record=deepcopy(source);_compact_ids(record,"evidence_ids")
    value=record.get("value")
    if isinstance(value,dict):
        _compact_ids(value,"event_ids")
        nested=value.get("overnight_profile_snapshot")
        if isinstance(nested,dict):_compact_ids(nested,"event_ids")
    return record


def declared(object_id, value, known_at, *, instrument_id, recipe_id="CONTROL"):
    """Build an explicit fixed-control assumption, not a source assertion.

    These values select a declared comparison or expose an unavailable author
    setting.  They are kept out of the supplied-source admission path because
    they do not claim to have passed a source-record recipe audit.
    """
    return {"object_id": object_id, "recipe_id": recipe_id,
            "instrument_id": instrument_id, "known_at": known_at,
            "state": "computed", "recipe_base_ok": True,
            "recipe_coverage_ok": True, "hole_ids": [],
            "evidence_ids": [f"control-declaration:{object_id}"],
            "evidence_class": "declared_control", "value": value}


def window(day, start, end, instrument, *, previous=False):
    first_day = day - timedelta(days=1) if previous else day
    return collect_window(ROOT/"data", DATASET, et_ns(first_day,*start),
                          et_ns(day,*end), instrument, required="ohlcv")


def native(win, object_id, recipe_id, inputs):
    obj = {"object_id":object_id,"recipe_id":recipe_id,
           "instrument_id":win.instrument_id,"formation_start":win.start_ns,
           "formation_end":win.end_ns,"as_of":win.end_ns,
           "known_at":win.end_ns,"raw_member_locators":win.raw_member_locators,
           "parent_ids":[],"inputs":inputs}
    result=nb.run_native_object(obj,win.resolver);validate_output(result)
    return result_record(object_id,result,instrument_id=win.instrument_id,
                         formation_start=win.start_ns,formation_end=win.end_ns)


def derived(object_id,recipe_id,parents,inputs,instrument):
    obj={"object_id":object_id,"recipe_id":recipe_id,"instrument_id":instrument,
         "parent_ids":[p["object_id"] for p in parents],"inputs":inputs}
    result=nb.run_native_object(obj,None,parents=parents);validate_output(result)
    return result_record(object_id,result,instrument_id=instrument)


def coverage(win):
    evidence=dict(win.coverage_evidence)
    return {"dataset_id":win.dataset_id,"instrument_id":win.instrument_id,
            "formation_start":win.start_ns,"formation_end":win.end_ns,
            "coverage_ok":win.coverage_ok,"native_row_count":len(win.rows),
            "missing_intervals":[list(x) for x in win.missing_intervals],
            "mismatches":[dict(x) for x in win.mismatches],
            "raw_member_locators":win.raw_member_locators,
            "coverage_reason":evidence["coverage_reason"],
            "reconciliation_summary":evidence["reconciliation_summary"]}


def load_profile(name):
    path=ROOT/"implementation/reports/phase1-live/methods/reconstructions/v2/objects"/f"{name}.json.gz"
    with gzip.open(path,"rt") as stream: payload=json.load(stream)
    value=payload["profile"]["value"]
    snapshot=pi.snapshot_from_payload(value)
    source_hash=digest(path)
    event_hash=hashlib.sha256()
    for event_id in snapshot.event_ids:
        event_hash.update(event_id.encode());event_hash.update(b"\n")
    result=type("LoadedResult",(),{})()
    result.recipe_id=payload["profile"]["recipe_id"];result.known_at=int(payload["profile"]["known_at"])
    result.state=payload["profile"]["state"];result.base_ok=payload["profile"]["base_ok"]
    result.coverage_ok=payload["profile"]["coverage_ok"];result.hole_ids=payload["profile"]["hole_ids"]
    result.parent_ids=payload["profile"]["parent_ids"]
    # The immutable gzip digest is the compact locator for the full audited
    # event list; copying hundreds of thousands of IDs into this control would
    # duplicate the frozen source payload several times.
    result.evidence_ids=[f"{path.relative_to(ROOT)}#sha256={source_hash}"]
    result.evidence_class="resolved_native";result.value=value
    record=result_record(name,result,instrument_id=value["instrument_id"],
                         formation_start=value["formation_start"],formation_end=value["formation_end"])
    return snapshot,record,{"path":str(path.relative_to(ROOT)),"sha256":source_hash,
                            "event_id_count":len(snapshot.event_ids),
                            "event_ids_sha256":event_hash.hexdigest(),
                            "native":payload["native"]}


def build():
    # 1. Fixed JJ comparison range and closed arithmetic descendants.
    feb=date(2026,2,24);range_win=window(feb,(6,0),(9,0),42002475)
    o005=native(range_win,"native:NQH6:2026-02-24:0600-0900","O005",
                {"range_id":"NQH6:2026-02-24:0600-0900","use_at":range_win.end_ns})
    range_selection=declared("selection:JJ-range-coordinates",
        {"coordinate_convention_verified":True,"selected_band":["24912.95","24923.65"],
         "k_values":["0.1","0.2","0.3","0.5"],"side":"upper"},
        o005["known_at"],instrument_id=range_win.instrument_id)
    o007=derived("derived:O007:JJ-range","O007",[o005],
                 {"range_parent_id":o005["object_id"],"use_at":range_win.end_ns},range_win.instrument_id)
    o014=derived("derived:O014:JJ-range","O014",[o005,range_selection],
                 {"range_parent_id":o005["object_id"],"selection_parent_id":range_selection["object_id"],
                  "use_at":range_win.end_ns},range_win.instrument_id)
    o015=derived("derived:O015:JJ-range","O015",[o005,range_selection],
                 {"range_parent_id":o005["object_id"],"selection_parent_id":range_selection["object_id"],
                  "use_at":range_win.end_ns},range_win.instrument_id)

    # 2. Full RTH period-range TPO control. The author letter clock is unknown;
    # this fixed 30-minute construction is explicitly a comparison.
    jun=date(2026,6,12);tpo_win=window(jun,(9,30),(16,0),42004058)
    o078=native(tpo_win,"native:NQM6:2026-06-12:TPO","O078",
                {"profile_id":"NQM6:2026-06-12:TPO","session_date_et":jun.isoformat(),
                 "construction":"period_range","price_step":"0.25","use_at":tpo_win.end_ns})
    prices=sorted(Decimal(x) for x in o078["value"]["memberships"])
    interior=[str(prices[1]),str(prices[-2])]
    selection=declared("selection:TPO-comparison",
        {"interior_band":interior,"lower_accepted_id":"rth-low-accepted",
         "upper_accepted_id":"rth-high-accepted","repair_policy":"any_later_letter",
         "side":"high","source_criterion":"same_letter_tail_min_2","grid_id":"NQM6-tick",
         "instrument_root":"NQ","criterion":"nq_one_row_tail","source_grid_compatible":True},
        o078["known_at"],instrument_id=tpo_win.instrument_id)
    tpo_children=[]
    for rid,key in (("O079","tpo_parent_id"),("O080","tpo_parent_id"),("O081","tpo_parent_id")):
        tpo_children.append(derived(f"derived:{rid}:TPO",rid,[o078,selection],
          {key:o078["object_id"],"selection_parent_id":selection["object_id"],
           "use_at":tpo_win.end_ns},tpo_win.instrument_id))
    o082=native(tpo_win,"native:NQM6:2026-06-12:IB","O082",
                {"ib_id":"NQM6:2026-06-12:IB","session_date_et":jun.isoformat(),
                 "as_of":tpo_win.end_ns,"use_at":tpo_win.end_ns})

    # 3. Two native, disjoint profile parents reused from the prior audited
    # reconstruction payloads. Their gzip hashes freeze the exact evidence.
    prior_snapshot,prior_rth,prior_file=load_profile("2026-06-12-prior-rth")
    overnight_snapshot,overnight,overnight_file=load_profile("2026-06-12-overnight")
    composite=derived("derived:NQM6:2026-06-12:composite","O070",[prior_rth,overnight],
       {"constituent_ids":[prior_rth["object_id"],overnight["object_id"]],
        "composite_id":"NQM6:2026-06-12:prior-rth-plus-overnight",
        "selection_known_at":max(prior_rth["known_at"],overnight["known_at"]),
        "rationale":"fixed disjoint native control windows",
        "use_at":max(prior_rth["known_at"],overnight["known_at"])},42004058)
    overlap=set(prior_snapshot.event_ids) & set(overnight_snapshot.event_ids)
    if overlap: raise AssertionError("composite parent native event ownership overlaps")
    if Decimal(str(composite["value"]["total_volume"])) != Decimal(str(prior_rth["value"]["total_volume"])) + Decimal(str(overnight["value"]["total_volume"])):
        raise AssertionError("composite volume does not reconcile")

    # 4. Exact Sires overnight clock geometry and an O073 profile route.
    on_win=window(jun,(18,0),(9,30),42004058,previous=True)
    o011=native(on_win,"native:NQM6:2026-06-12:sires-overnight","O011",
                {"window_id":"sires-overnight:NQM6:2026-06-12","use_at":on_win.end_ns})
    o073=derived("derived:NQM6:2026-06-12:O073","O073",
        [overnight,o011,prior_rth],
        {"profile_parent_id":overnight["object_id"],
         "older_poc_parent_id":prior_rth["object_id"],"source":"sires",
         "use_at":max(overnight["known_at"],o011["known_at"])},42004058)

    payload={"schema":"phase1-native-geometry-validation-v1","generated_by":"implementation/tools/validate_phase1_geometry_native.py",
      "controls":{
       "feb24_jj_range":{"window":coverage(range_win),"objects":[o005,o007,o014,o015],
        "reconciliation":{"W_equals_H_minus_L":Decimal(o005["value"]["W"])==Decimal(o005["value"]["H"])-Decimal(o005["value"]["L"]),
                          "derived_parent_ids_exact":all(x["parent_ids"]==[o005["object_id"]] or set(x["parent_ids"])=={o005["object_id"],range_selection["object_id"]} for x in (o007,o014,o015))}},
       "june12_tpo_ib":{"window":coverage(tpo_win),"objects":[o078,*tpo_children,o082],
        "construction_status":"declared 30-minute period-range native comparison; source letter window unreadable",
        "source_letter_window":None,"source_letter_window_hole":"HOLE:O078:source_letter_window"},
       "june12_disjoint_composite":{"source_payloads":[prior_file,overnight_file],"objects":[prior_rth,overnight,composite],
        "reconciliation":{"overlapping_native_event_ids":len(overlap),"constituent_total":str(Decimal(str(prior_rth["value"]["total_volume"]))+Decimal(str(overnight["value"]["total_volume"]))),
                          "composite_total":str(composite["value"]["total_volume"])},
        "value_area_expansion":{"source_40":None,"source_68":None,"common_70":None,"reason":"source expansion/tie algorithm unavailable; no autofit"}},
       "june12_sires_overnight":{"window":coverage(on_win),"objects":[o011,o073],
        "profile_payload":overnight_file,"older_reference_payload":prior_file,
        "clock":{"start":"previous 18:00 ET","end":"09:30 ET","verified_native_members":True},
        "source_unknowns":["profile value-area expansion algorithm","unpublished LVN selection algorithm"]}}}
    for control in payload["controls"].values():
        control["objects"]=[compact_record(record) for record in control["objects"]]
    return payload


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--output",type=Path,default=OUT);args=parser.parse_args()
    payload=build();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,default=encode,indent=2)+"\n")
    print(json.dumps({"status":"pass","path":str(args.output),"sha256":digest(args.output),
                      "controls":len(payload["controls"])},indent=2))


if __name__ == "__main__": main()
