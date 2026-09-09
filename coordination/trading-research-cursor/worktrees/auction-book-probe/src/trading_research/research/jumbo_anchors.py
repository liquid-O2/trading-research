"""Exact causal anchor and explicitly named relationship supplements.

Original annual path/formation artifacts are immutable inputs. This supplement
joins exact admitted minutes; normalized float features are reconciliation
checks only and are never inverted to produce a price.
"""
from bisect import bisect_left
from datetime import date
import hashlib
import json
import math

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest
from trading_research.research.jumbo_tables import FEATURES
from trading_research.research.ohlc_ranges import MINUTE

VERSION = "jumbo-exact-anchor-supplement-v1"
RELATIONSHIP_CLOCKS = ("OR5", "OR15", "JTR_fixed_04", "futures08", "NY08")
RELATION_METRICS = ("width_ratio", "price_overlap_fraction", "shared_time_fraction", "last_close_position", "age_minutes")
PRIOR_ALIASES = {
    "prior_width_ticks": "prior_actual_RTH_width_ticks",
    "width_prior_ratio": "width_prior_actual_RTH_ratio",
    "last_close_in_prior_position": "last_close_in_prior_actual_RTH_position",
    "prior_last_close_displacement_ticks": "prior_actual_RTH_last_close_displacement_ticks",
    "observed_cash_open_gap_ticks": "observed_cash_open_gap_from_prior_actual_RTH_ticks",
    "prior_age_minutes": "prior_actual_RTH_age_minutes",
    "prior_5_mean_width_ticks": "prior_actual_RTH_5_mean_width_ticks",
    "prior_20_mean_width_ticks": "prior_actual_RTH_20_mean_width_ticks",
}
LEGACY_REFERENCE_FEATURES = frozenset(name for name in FEATURES if
    name.startswith(("asia_", "morning_", "opening_")) or name in ("activity_threshold", "activity_reference_dates"))
IDENTITY_COLUMNS = ("root", "year", "date", "clock", "horizon", "formation_id", "source_row_id", "source_path_row", "origin_ns", "endpoint_ns")
ANCHOR_INTEGER_COLUMNS = ("anchor_ticks", "anchor_start_ns", "anchor_end_ns", "anchor_known_at_ns", "anchor_observation_known_at_ns")


def _clocks(clocks):
    result = tuple(clocks)
    if not result or len(set(result))!=len(result) or any(type(c) is not str or not c or not c.replace("_", "").isalnum() for c in result):
        raise ContractError("unique explicitly named relationship clocks required")
    return result


def supplement_feature_names(relationship_clocks=RELATIONSHIP_CLOCKS):
    clocks = _clocks(relationship_clocks)
    return tuple(PRIOR_ALIASES.values()) + tuple(f"anchor_{clock}_{metric}" for clock in clocks for metric in RELATION_METRICS)


def supplement_feature_groups(relationship_clocks=RELATIONSHIP_CLOCKS):
    clocks = _clocks(relationship_clocks)
    controls = ("width_ticks", "formation_minutes", "prior_width_ticks", "last_close_age_minutes", "weekday", "month", "cut_ny_minutes", "early_close")
    own = controls + ("log_volume", "open_position", "close_position", "body_fraction", "up_fraction", "down_fraction", "last_close_position")
    rename = lambda names: tuple(PRIOR_ALIASES.get(name,name) for name in names)
    active = rename(name for name in FEATURES if name not in LEGACY_REFERENCE_FEATURES)
    relations = tuple(f"anchor_{clock}_{metric}" for clock in clocks for metric in RELATION_METRICS)
    groups = {"controls": list(rename(controls)), "own": list(rename(own)),
              "full": list(active + relations), "anchor_relationships": list(rename(own)+relations),
              "legacy_references": list(FEATURES)}
    for clock in clocks:
        groups["named_anchor_"+clock] = list(rename(own)+tuple(f"anchor_{clock}_{metric}" for metric in RELATION_METRICS))
    return groups


def normalized_table_ref(ref):
    if not isinstance(ref,dict):
        raise ContractError("table artifact reference required")
    value = dict(ref)
    if "artifact_ref" in value:
        nested = value.pop("artifact_ref")
        if not isinstance(nested,dict):
            raise ContractError("nested artifact reference must be an object")
        if any(k in value and value[k]!=v for k,v in nested.items()):
            raise IntegrityError("conflicting nested table reference identity")
        value = {**nested,**value}
    for name in ("sha256", "schema_sha256"):
        item = value.get(name)
        if type(item) is not str or len(item)!=64 or any(c not in "0123456789abcdef" for c in item):
            raise ContractError("canonical table hash/schema identity required")
    if type(value.get("kind")) is not str or not value["kind"]:
        raise ContractError("artifact kind required")
    if any(type(value.get(k)) is not int or value[k]<0 for k in ("rows","size_bytes")):
        raise ContractError("exact table rows/size required")
    return value


def _ref_identity(ref):
    value=normalized_table_ref(ref)
    return {k:value[k] for k in ("kind","sha256","size_bytes","rows","schema_sha256")}


def anchor_schema(relationship_clocks=RELATIONSHIP_CLOCKS):
    import pyarrow as pa
    fields=[pa.field(name,pa.string()) for name in
       ("root","date","clock","horizon","formation_id","source_row_id","source_version","anchor_source_kind","anchor_contract_key")]
    fields += [pa.field(name,pa.int64()) for name in
       ("year","source_path_row","origin_ns","endpoint_ns",*ANCHOR_INTEGER_COLUMNS)]
    fields += [pa.field("anchor_available",pa.bool_()),pa.field("saved_position_reconciled",pa.bool_())]
    fields += [pa.field("x_"+name,pa.float64()) for name in supplement_feature_names(relationship_clocks)]
    return pa.schema(fields)


def _rows(value):
    return value.to_pylist() if hasattr(value,"to_pylist") else list(value)


def _identity_row(row,root,year):
    if (type(row.get("root")) is not str or row["root"]!=root
            or type(row.get("year")) is not int or row["year"]!=year or type(row.get("date")) is not str):
        raise IntegrityError("supplement source root/year/date identity mismatch")
    try:
        day=date.fromisoformat(row["date"])
    except ValueError as exc:
        raise IntegrityError("invalid source cash date") from exc
    if day.isoformat()!=row["date"] or day.year!=year:
        raise IntegrityError("source cash date does not match shard")


def _integer(value,name,*,nullable=False):
    if nullable and value is None:
        return None
    if type(value) is not int or not -(2**63)<=value<2**63:
        raise IntegrityError(f"exact int64 {name} required")
    return value


def _minute(series,start,*,contract,cut):
    at=bisect_left(series.start,start)
    if (at==len(series.start) or series.start[at]!=start or series.end[at]!=start+MINUTE
            or series.known[at]>cut or series.bad[at+1]!=series.bad[at]
            or series.contract_names[series.contract[at]]!=contract):
        return None
    return at


def _ready(formation,origin):
    available=formation.get("available_at_ns")
    return (formation.get("status")=="complete" and type(available) is int and 0<=available<=origin)


def _direct_anchor(series,formation,origin):
    empty={name:None for name in ANCHOR_INTEGER_COLUMNS}
    empty.update(anchor_available=False,anchor_source_kind="formation_unavailable",anchor_contract_key=formation.get("contract_key"))
    if not _ready(formation,origin):
        return empty
    start,end=(_integer(formation.get(name),name) for name in ("formation_start_ns","formation_end_ns"))
    if not 0<=start<end<=formation["available_at_ns"]<=origin or start%MINUTE or end%MINUTE:
        raise IntegrityError("complete formation has impossible exact time/availability")
    contract=formation.get("contract_key")
    if type(contract) is not str or not contract:
        raise IntegrityError("complete formation needs raw contract identity")
    last=_minute(series,origin-2*MINUTE,contract=contract,cut=origin) if origin>=2*MINUTE else None
    kind="expected_published_minute"
    if last is None:
        last=_minute(series,end-MINUTE,contract=contract,cut=formation["available_at_ns"])
        if last is None or int(series.close[last])!=formation.get("close_ticks"):
            raise IntegrityError("saved complete formation close has no agreeing canonical last minute")
        kind="formation_close_fallback"
    return dict(anchor_ticks=int(series.close[last]),anchor_start_ns=int(series.start[last]),
                anchor_end_ns=int(series.end[last]),anchor_observation_known_at_ns=int(series.known[last]),
                anchor_known_at_ns=max(int(series.known[last]),formation["available_at_ns"]),
                anchor_available=True,anchor_source_kind=kind,anchor_contract_key=contract)


def _reconcile(path,formation,anchor):
    position=path.get("x_last_close_position")
    age=path.get("x_last_close_age_minutes")
    present=lambda value:value is not None and math.isfinite(value)
    if not anchor["anchor_available"]:
        if present(position) or present(age):
            raise IntegrityError("saved anchor feature exists before formation availability")
        return True
    width=_integer(formation.get("width_ticks"),"formation width")
    low=_integer(formation.get("low_ticks"),"formation low")
    if width<0:
        raise IntegrityError("negative saved formation width")
    if width:
        expected=(anchor["anchor_ticks"]-low)/width
        if not present(position) or position!=expected:
            raise IntegrityError("saved normalized anchor differs from directly joined exact price")
    elif present(position):
        raise IntegrityError("zero-width formation has a normalized anchor")
    expected_age=(path["origin_ns"]-anchor["anchor_end_ns"])/MINUTE
    if not present(age) or age!=expected_age:
        raise IntegrityError("saved anchor age differs from directly joined observation")
    return True


def _relations(formation,origin,anchor,by_clock,clocks):
    result={"x_"+name:None for name in supplement_feature_names(clocks) if name.startswith("anchor_")}
    if not anchor["anchor_available"] or not _ready(formation,origin):
        return result
    width=formation.get("width_ticks")
    if type(width) is not int or width<=0:
        return result
    for clock in clocks:
        other=by_clock.get((formation["date"],clock))
        if (other is None or not _ready(other,origin) or other.get("contract_key")!=formation.get("contract_key")
                or type(other.get("width_ticks")) is not int or other["width_ticks"]<=0):
            continue
        ow=other["width_ticks"]
        overlap=max(0,min(formation["high_ticks"],other["high_ticks"])-max(formation["low_ticks"],other["low_ticks"]))
        time_overlap=max(0,min(formation["formation_end_ns"],other["formation_end_ns"])-max(formation["formation_start_ns"],other["formation_start_ns"]))
        vals=(ow/width,overlap/width,time_overlap/(formation["formation_end_ns"]-formation["formation_start_ns"]),
              (anchor["anchor_ticks"]-other["low_ticks"])/ow,(origin-other["formation_end_ns"])/MINUTE)
        for name,value in zip(RELATION_METRICS,vals,strict=True):
            result[f"x_anchor_{clock}_{name}"]=value
    return result


def build_anchor_supplement(series,formation_rows,path_rows,*,root,year,path_ref,formation_ref,
                            relationship_clocks=RELATIONSHIP_CLOCKS,frozen_analysis_id):
    import pyarrow as pa
    if type(root) is not str or not root or type(year) is not int or not 1<=year<=9999:
        raise ContractError("declared instrument/year required")
    if type(series.source_version) is not str or not series.source_version:
        raise IntegrityError("admitted source identity required")
    if type(frozen_analysis_id) is not str or not frozen_analysis_id:
        raise ContractError("original frozen analysis identity required")
    clocks=_clocks(relationship_clocks)
    path_ref,formation_ref=normalized_table_ref(path_ref),normalized_table_ref(formation_ref)
    formations,paths=_rows(formation_rows),_rows(path_rows)
    if len(paths)!=path_ref["rows"] or len(formations)!=formation_ref["rows"] or not paths:
        raise IntegrityError("supplement must cover exact nonempty source row populations")
    parents,by_clock={},{}
    for f in formations:
        _identity_row(f,root,year)
        key=f.get("formation_id")
        if type(key) is not str or not key or key in parents or (f["date"],f.get("clock")) in by_clock:
            raise IntegrityError("duplicate or missing formation identity")
        if f.get("source_version")!=series.source_version:
            raise IntegrityError("formation source identity differs from admitted series; do not overwrite it")
        if type(f.get("clock")) is not str or not f["clock"]:
            raise IntegrityError("formation clock identity required")
        if f.get("status")=="complete":
            start,end,known=(_integer(f.get(name),name) for name in ("formation_start_ns","formation_end_ns","available_at_ns"))
            if not 0<=start<end<=known or start%MINUTE or end%MINUTE:
                raise IntegrityError("invalid complete formation source time/availability")
            for name in ("open_ticks","high_ticks","low_ticks","close_ticks","width_ticks"):_integer(f.get(name),name)
            if (f["high_ticks"]-f["low_ticks"]!=f["width_ticks"] or
                    not f["low_ticks"]<=min(f["open_ticks"],f["close_ticks"])<=max(f["open_ticks"],f["close_ticks"])<=f["high_ticks"]):
                raise IntegrityError("complete saved formation geometry is inconsistent")
        parents[key]=f;by_clock[(f["date"],f["clock"])]=f
    records,cache=[],{}
    content_hash=hashlib.sha256()
    rowids,keys=set(),set()
    key_hash=hashlib.sha256()
    for index,p in enumerate(paths):
        _identity_row(p,root,year)
        rowid=p.get("row_id")
        if any(type(p.get(name)) is not str or not p[name] for name in ("clock","horizon","formation_id")):
            raise IntegrityError("exact path clock/horizon/formation identity required")
        key=(root,p["date"],p.get("clock"),p.get("horizon"))
        if type(rowid) is not str or not rowid or rowid in rowids or key in keys:
            raise IntegrityError("duplicate or missing exact path row identity")
        rowids.add(rowid);keys.add(key)
        f=parents.get(p.get("formation_id"))
        if f is None or f["date"]!=p["date"] or f["clock"]!=p.get("clock") or f.get("contract_key")!=p.get("contract_key"):
            raise IntegrityError("path/formation ancestor identity differs")
        origin,endpoint=(_integer(p.get(name),name) for name in ("origin_ns","endpoint_ns"))
        if origin<0 or origin%MINUTE or endpoint<0 or endpoint%MINUTE:
            raise IntegrityError("exact whole-minute receiver endpoints required")
        cachekey=(p["formation_id"],origin)
        if cachekey not in cache:
            anchor=_direct_anchor(series,f,origin)
            cache[cachekey]=(anchor,_relations(f,origin,anchor,by_clock,clocks))
        anchor,relationships=cache[cachekey]
        reconciled=_reconcile(p,f,anchor)
        record={"root":root,"year":year,"date":p["date"],"clock":p["clock"],"horizon":p["horizon"],
                "formation_id":p["formation_id"],"source_row_id":rowid,"source_path_row":index,
                "source_version":series.source_version,"origin_ns":origin,"endpoint_ns":endpoint,
                **anchor,"saved_position_reconciled":reconciled,**relationships}
        for old,new in PRIOR_ALIASES.items():
            value=p.get("x_"+old)
            record["x_"+new]=None if value is None else float(value)
        records.append(record)
        content_hash.update(json.dumps(record,sort_keys=True,separators=(",", ":"),allow_nan=False).encode())
        key_hash.update(json.dumps([record[name] for name in IDENTITY_COLUMNS],separators=(",", ":")).encode())
    schema=anchor_schema(clocks)
    table=pa.Table.from_pylist(records,schema=schema)
    manifest={"version":VERSION,"root":root,"year":year,"rows":len(paths),"source_version":series.source_version,
              "source_paths":path_ref,"source_formations":formation_ref,"frozen_analysis_id":frozen_analysis_id,
              "schema_sha256":hashlib.sha256(schema.serialize().to_pybytes()).hexdigest(),
              "row_key_sha256":key_hash.hexdigest(),"content_sha256":content_hash.hexdigest(),"relationship_clocks":list(clocks),
              "feature_columns":["x_"+name for name in (*FEATURES,*supplement_feature_names(clocks))],
              "feature_groups":supplement_feature_groups(clocks),
              "relationship_source_ids":{clock:sorted({str(f.get("source_ids","")) for f in formations if f["clock"]==clock}) for clock in clocks},
              "anchor_rule":"direct exact expected [origin-2m,origin-1m) published minute, else verified saved formation close; no ratio inversion",
              "reconciliation":"saved binary64 normalized position and age must reproduce the directly joined price/time; unavailable and zero-width remain explicit",
              "reference_policy":"five equally explicit named clocks; OR15 is a named source benchmark, not a generic opening default; original activity references retained only in legacy feature group",
              "source_windows_vs_forecasts":"anchor source formation intervals and receiver origin/end are distinct fields; no postformation horizon is relabeled as a source window"}
    manifest["id"]=digest(manifest)
    return {"table":table,"manifest":manifest}


def validate_anchor_manifest(manifest,*,root,year,path_ref,formation_ref,table_ref=None):
    if not isinstance(manifest,dict) or manifest.get("version")!=VERSION:
        raise IntegrityError("explicit exact anchor supplement manifest required")
    payload=dict(manifest);identity=payload.pop("id",None)
    if identity!=digest(payload) or manifest.get("root")!=root or manifest.get("year")!=year:
        raise IntegrityError("anchor supplement manifest identity changed")
    if (_ref_identity(manifest["source_paths"])!=_ref_identity(path_ref)
            or _ref_identity(manifest["source_formations"])!=_ref_identity(formation_ref)):
        raise IntegrityError("anchor supplement belongs to different immutable source shards")
    if type(manifest.get("source_version")) is not str or not manifest["source_version"] or not manifest.get("frozen_analysis_id"):
        raise IntegrityError("supplement lacks admitted source/original analysis identity")
    expected=anchor_schema(manifest["relationship_clocks"])
    if (manifest.get("feature_columns") != ["x_"+name for name in (*FEATURES,*supplement_feature_names(manifest["relationship_clocks"]))]
            or manifest.get("feature_groups") != supplement_feature_groups(manifest["relationship_clocks"])):
        raise IntegrityError("supplement active feature definitions changed")
    if manifest["schema_sha256"]!=hashlib.sha256(expected.serialize().to_pybytes()).hexdigest():
        raise IntegrityError("supplement schema/relationship definition changed")
    if table_ref is not None:
        ref=normalized_table_ref(table_ref)
        if ref["rows"]!=manifest["rows"] or ref["schema_sha256"]!=manifest["schema_sha256"]:
            raise IntegrityError("supplement artifact rows/schema differ from its manifest")
    return manifest


def validate_anchor_content(table,manifest):
    """Check canonical logical rows independently of Parquet compression/chunks."""
    key_hash,content_hash=hashlib.sha256(),hashlib.sha256()
    for record in table.to_pylist():
        key_hash.update(json.dumps([record[name] for name in IDENTITY_COLUMNS],separators=(",", ":")).encode())
        content_hash.update(json.dumps(record,sort_keys=True,separators=(",", ":"),allow_nan=False).encode())
    if key_hash.hexdigest()!=manifest["row_key_sha256"] or content_hash.hexdigest()!=manifest["content_sha256"]:
        raise IntegrityError("supplement logical content differs from registered manifest")
