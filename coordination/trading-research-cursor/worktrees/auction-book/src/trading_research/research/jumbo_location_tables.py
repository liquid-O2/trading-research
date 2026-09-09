"""Factorized yearly Location extraction; execution belongs to registered checks.

Array axis 0 is the original formation row. Candidate axis 1 has 26 common
research comparators, reflections, explicit snapped variants and their reflections. No rows are dropped.
"""
from fractions import Fraction
from datetime import date
import time
import numpy as np
from .jumbo_locations import range_candidate_specs, append_candidate_bands, evaluate_location_bands

MINUTE = 60_000_000_000
VERSION = "jumbo-location-tables-v2"
GROUP_OUTCOMES = frozenset(("observed_minutes", "complete_horizon", "horizon_reason",
                            "prefix_stop_reason", "coverage_gap", "maturity_ns", "endpoint_ns", "prefix_maturity_ns"))
I64_MAX = np.iinfo(np.int64).max
GENERATORS = ("raw", "mirrored_raw", "tick_snapped", "mirrored_tick_snapped")


def _integer(value, name, *, nullable=False):
    if nullable and value is None:
        return None
    if type(value) is not int or not 0 <= value <= I64_MAX:
        raise ValueError(f"{name} requires exact nonnegative int64")
    return value


def _rows(rows):
    if hasattr(rows, "to_pylist"):
        return rows.to_pylist()
    return list(rows)


def _configuration(plan):
    hs = tuple(plan.get("location_horizons_minutes", (15,30,60,180)))
    if not hs or len(set(hs)) != len(hs) or any(type(h) is not int or not 1 <= h <= 180 for h in hs):
        raise ValueError("distinct integer Location horizons in 1..180 required")
    raw = plan.get("location_departure_width_ratio", [1,4])
    if isinstance(raw, Fraction):
        distance = raw
    elif type(raw) is int:
        distance = Fraction(raw)
    elif isinstance(raw, (list,tuple)) and len(raw)==2 and all(type(v) is int for v in raw):
        if raw[1] <= 0:
            raise ValueError("positive rational denominator required")
        distance = Fraction(*raw)
    else:
        raise ValueError("exact Location departure width ratio required")
    if not 0 < distance.numerator <= I64_MAX or not 0 < distance.denominator <= I64_MAX:
        raise ValueError("positive departure ratio with int64 numerator/denominator required")
    generators = tuple(plan.get("location_generators", GENERATORS))
    if generators not in (GENERATORS[:2],GENERATORS):
        raise ValueError("Location generators must be declared raw/mirror pair or all four ordered generators")
    return hs, distance, generators


def _one(series, row, *, horizons, distance, evaluation_cut, generators):
    declared = _integer(row.get("origin_ns"), "origin_ns")
    available = _integer(row.get("available_at_ns"), "available_at_ns", nullable=True)
    creation = max(declared, available if available is not None else declared)
    origin = ((creation + MINUTE - 1)//MINUTE)*MINUTE
    if origin + max(horizons)*MINUTE > I64_MAX:
        raise ValueError("Location horizon overflow")
    candidates = range_candidate_specs(row)
    c = candidates["columns"]
    if len(c["slot"]) != 26:
        raise ValueError("common research grid must retain 26 slots")
    formation_end = _integer(row.get("formation_end_ns"), "formation_end_ns", nullable=True)
    anchor = anchor_time = anchor_known = None
    if (bool(c["valid_geometry"].all()) and formation_end is not None
            and available is not None and formation_end <= available <= min(origin,evaluation_cut)):
        anchor = row.get("close_ticks")
        anchor_time = formation_end
        anchor_known = available
    fallback = True
    if origin >= 2*MINUTE and row.get("contract_key") is not None:
        latest = series.window(origin-2*MINUTE, origin-MINUTE,
                               contract_key=row["contract_key"], available_at=min(origin,evaluation_cut))
        if latest.complete:
            anchor = int(series.close[latest.right-1])
            anchor_time = latest.end
            anchor_known = latest.available_at_ns
            fallback = False
    if anchor is not None and (type(anchor) is not int or not -I64_MAX-1 <= anchor <= I64_MAX):
        raise ValueError("exact int64 causal anchor required")
    originals = list(candidates["metadata"]["definitions"])
    raw = [(Fraction(int(c["lower_num"][i]),int(c["lower_den"][i])),
            Fraction(int(c["upper_num"][i]),int(c["upper_den"][i]))) for i in range(26)]
    definitions = []
    for generator in generators[1:]:
        for i, definition in enumerate(originals):
            valid = bool(c["valid_geometry"][i]) and anchor is not None
            a,b = raw[i]
            if "tick_snapped" in generator:
                if a == b:
                    snapped = (-(-a.numerator//a.denominator) if a>anchor else
                               a.numerator//a.denominator if a<anchor else anchor) if valid else 0
                    a=b=Fraction(snapped)
                else:
                    a,b=Fraction(a.numerator//a.denominator),Fraction(-(-b.numerator//b.denominator))
            if generator.startswith("mirrored") and valid:
                a,b=2*anchor-b,2*anchor-a
            definitions.append(dict(name=generator+"_"+definition["name"],geometry=definition["geometry"],
                                    generator="matched_placebo" if generator.startswith("mirrored") else "tick_snapped",
                                    location_generator=generator,ancestor_slot=i,
                                    available_at_ns=max(int(c["available_at_ns"][i]),anchor_known if anchor_known is not None else 0),
                                    lower=a if valid else None,upper=b if valid else None))
    candidates = append_candidate_bands(candidates,definitions)
    candidate_count = 26*len(generators)
    forecast = series.window(origin,origin+max(horizons)*MINUTE,
                             contract_key=row.get("contract_key"),available_at=evaluation_cut)
    width = candidates["metadata"].get("width_ticks")
    scaled = distance * (width if width is not None else 0)
    barrier = max(1,-(-scaled.numerator//scaled.denominator))
    out = evaluate_location_bands(forecast,candidates,horizons=horizons,
                                  available_cut=evaluation_cut,departure_ticks=barrier)
    arrays = {"geometry_"+name: value for name,value in candidates["columns"].items()}
    arrays.update({("horizon_" if name in GROUP_OUTCOMES else "outcome_")+name:value
                   for name,value in out["columns"].items()})
    sides = np.zeros(candidate_count,dtype=np.int8)
    changes = {name:np.zeros(candidate_count,dtype=np.int64) for name in
               ("width_change_num","anchor_distance_change_num")}
    changes.update({name:np.ones(candidate_count,dtype=np.int64) for name in
                    ("width_change_den","anchor_distance_change_den")})
    if anchor is not None:
        cols = candidates["columns"]
        for i in range(candidate_count):
            if cols["valid_geometry"][i]:
                center = (Fraction(int(cols["lower_num"][i]),int(cols["lower_den"][i]))+
                          Fraction(int(cols["upper_num"][i]),int(cols["upper_den"][i])))/2
                sides[i] = (center > anchor)-(center < anchor)
                ca=Fraction(int(cols["lower_num"][i]),int(cols["lower_den"][i]))
                cb=Fraction(int(cols["upper_num"][i]),int(cols["upper_den"][i]))
                ra,rb=raw[i%26]
                for name,change in (("width_change",cb-ca-(rb-ra)),
                                    ("anchor_distance_change",abs(center-anchor)-abs((ra+rb)/2-anchor))):
                    if not -I64_MAX-1<=change.numerator<=I64_MAX or change.denominator>I64_MAX:
                        raise ValueError("exact geometry change exceeds int64 storage")
                    changes[name+"_num"][i]=change.numerator
                    changes[name+"_den"][i]=change.denominator
    arrays["anchor_side"] = sides
    arrays.update(changes)
    metadata = dict(formation_id=row["formation_id"],date=row["date"],clock=row["clock"],
                    source_version=row["source_version"],window_version=row.get("window_version"),
                    contract_key=row.get("contract_key"),source_ids=row.get("source_ids"),
                    formation_start_ns=row.get("formation_start_ns"),formation_end_ns=row.get("formation_end_ns"),
                    declared_origin_ns=declared,available_at_ns=available,creation_cut_ns=creation,
                    forecast_origin_ns=origin,anchor_ticks=anchor,anchor_observation_end_ns=anchor_time,
                    anchor_known_at_ns=anchor_known,
                    anchor_age_ns=origin-anchor_time if anchor_time is not None else None,
                    anchor_fallback=fallback,departure_ticks=barrier,
                    departure_width_ratio=[barrier,width] if width else None,
                    formation_status=row.get("status"),
                    formation_exclusion_reasons=row.get("exclusion_reasons"))
    return arrays, metadata, candidates["metadata"]["definitions"], out["metadata"]


def _validate_rows(series, rows, *, root, year):
    if type(root) is not str or not root or type(year) is not int or not 1<=year<=9999:
        raise ValueError("nonempty root string and valid integer year required")
    if type(series.source_version) is not str or not series.source_version:
        raise ValueError("nonempty immutable series identity required")
    if not rows:
        raise ValueError("declared full source year must contain formations")
    seen = set()
    for row in rows:
        if not isinstance(row,dict):
            raise ValueError("formation row mapping required")
        day = row.get("date")
        if type(day) is not str:
            raise ValueError("exact ISO date string required")
        try:
            parsed = date.fromisoformat(day)
        except ValueError as exc:
            raise ValueError("valid formation ISO date required") from exc
        if (parsed.isoformat()!=day or parsed.year!=year or type(row.get("root")) is not str
                or row["root"]!=root or type(row.get("year")) is not int or row["year"]!=year):
            raise ValueError("formation root/year/date mismatch")
        identity = row.get("source_version")
        if type(identity) is not str or not identity or identity != series.source_version:
            raise ValueError("immutable series identity mismatch")
        key = row.get("formation_id")
        if type(key) is not str or not key or key in seen:
            raise ValueError("unique nonempty formation IDs required")
        seen.add(key)


def extract_location_year(series, formation_rows, *, root, year, evaluation_cut, plan):
    """Return dense factorized NumPy arrays and JSON-safe manifest; no file writes.

    Root caller owns CAS, artifact hashes and phase registration. Formation order
    is unchanged, and manifest formation_index joins each original formation_id.
    Float outcomes remain float64. Missing geometry and censored future are kept.
    """
    _integer(evaluation_cut,"evaluation_cut")
    horizons, distance, generators = _configuration(plan)
    candidate_count = 26*len(generators)
    rows = _rows(formation_rows)
    _validate_rows(series,rows,root=root,year=year)
    arrays, lineage, definitions, semantics = {}, [], [], {}
    n = len(rows)
    for index,row in enumerate(rows):
        block, meta, defs, semantics = _one(series,row,horizons=horizons,distance=distance,evaluation_cut=evaluation_cut,generators=generators)
        if index == 0:
            required = sum(value.nbytes for value in block.values())*n + candidate_count*3 + len(horizons)*2
            cap = plan.get("location_max_output_bytes")
            if cap is not None and (type(cap) is not int or cap < 1 or required > cap):
                raise ValueError(f"Location arrays require {required} bytes; exceeds declared output cap")
            arrays = {name:np.empty((n,)+value.shape,dtype=value.dtype) for name,value in block.items()}
            definitions = defs
        for name,value in block.items():
            if value.shape != arrays[name].shape[1:] or value.dtype != arrays[name].dtype:
                raise ValueError("Location output schema changed within shard")
            arrays[name][index] = value
        meta["formation_index"] = index
        lineage.append(meta)
    # These axes are global, never duplicated per candidate or outcome horizon.
    arrays["generator_id"] = np.repeat(np.arange(len(generators),dtype=np.int8),26)
    arrays["ancestor_slot"] = np.tile(np.arange(26,dtype=np.int16),len(generators))
    arrays["horizons_minutes"] = np.asarray(horizons,dtype=np.int16)
    population = {}
    for generator_index,generator in enumerate(generators):
        z=slice(generator_index*26,(generator_index+1)*26)
        population[generator]=dict(intended_candidates=n*26,
            valid_geometry=int(arrays["geometry_valid_geometry"][:,z].sum()) if n else 0,
            causal_geometry=int(arrays["outcome_geometry_eligible"][:,z].sum()) if n else 0,
            empty_contact_lattice=int(arrays["outcome_contact_ineligible_empty_lattice"][:,z].sum()) if n else 0,
            contact_eligible=int(arrays["outcome_eligible"][:,z].sum()) if n else 0)
    manifest = dict(version=VERSION,root=root,year=year,source_version=series.source_version,
                    evaluation_cut_ns=evaluation_cut,formation_count=n,candidates_per_formation=candidate_count,
                    candidate_count=candidate_count*n,outcome_count=candidate_count*n*len(horizons),formations=lineage,
                    candidate_definitions=definitions,departure_width_ratio=[distance.numerator,distance.denominator],
                    departure_rule="max(1,ceil(formation_width * declared ratio)) raw ticks",
                    array_bytes=sum(a.nbytes for a in arrays.values()),
                    schema={k:dict(dtype=str(v.dtype),shape=list(v.shape)) for k,v in arrays.items()},
                    generator_definitions={"0":"common 26-slot research grid; not universal source disclosure",
                       "1":"raw exact reflection about causal anchor; width/count/absolute distance/age matched, side flipped",
                       "2":"explicit outward side-preserving point snap or minimal outer integer-cover band",
                       "3":"exact reflection of snapped generator about causal anchor"},
                    active_generators=list(generators),generator_population_counts=population,
                    snapping_rule="point above anchor ceil, below floor, equal unchanged; nonpoint band floor(lower),ceil(upper)",
                    snapping_caveat="changes distance and/or width; exact per-candidate deltas retained; no raw-versus-snapped matching claim",
                    side_codes={"-1":"center below anchor","0":"center equal or invalid; validity mask distinguishes","1":"center above anchor"},
                    semantics=semantics,
                    axis_layout="per-formation arrays F x K [x H]; horizon_ arrays F x H; global axes separately",
                    origin_rule="ceil-minute max(declared origin, formation availability)",
                    anchor_rule="expected origin-2m..origin-1m published close, otherwise complete formation close with exact end and known publication; derived generators no earlier than anchor publication",
                    control_caveat="report side strata and population imbalance; reflection does not identify unconditional geometry effect")
    return {"arrays":arrays,"manifest":manifest}


def preflight_location_year(series, formation_rows, *, root, year, evaluation_cut, plan, dates):
    """Registered check only: caller supplies the six predeclared cash dates.

    Includes every clock on those dates. Measures this actual output allocation;
    extrapolation reports assumptions and does not authorize a full execution.
    """
    dates = tuple(dates)
    if any(type(day) is not str for day in dates):
        raise ValueError("predeclared cash dates must be exact ISO strings")
    if len(dates)!=6 or len(set(dates))!=6:
        raise ValueError("six distinct predeclared cash dates required")
    rows = _rows(formation_rows)
    _validate_rows(series,rows,root=root,year=year)
    selected = [row for row in rows if row.get("date") in dates]
    if set(row["date"] for row in selected) != set(dates):
        raise ValueError("preflight date lacks declared formations")
    start_cpu, start_wall = time.process_time(), time.perf_counter()
    result = extract_location_year(series,selected,root=root,year=year,evaluation_cut=evaluation_cut,plan=plan)
    cpu, wall = time.process_time()-start_cpu,time.perf_counter()-start_wall
    import io
    compression_start = time.process_time()
    buffer = io.BytesIO()
    np.savez_compressed(buffer, **result["arrays"])
    compressed_bytes = buffer.tell()
    buffer.close()
    compression_cpu = time.process_time()-compression_start
    count = len(selected)
    result["preflight"] = dict(dates=list(dates),formation_count=count,full_formation_count=len(rows),
       cpu_seconds=cpu,wall_seconds=wall,array_bytes=result["manifest"]["array_bytes"],
       compressed_npz_bytes=compressed_bytes,compression_cpu_seconds=compression_cpu,
       projected_full_compressed_npz_bytes=compressed_bytes*len(rows)/count,
       projected_full_cpu_seconds=cpu*len(rows)/count,
       projected_full_array_bytes=result["manifest"]["array_bytes"]*len(rows)/count,
       caveat="linear formation-count extrapolation; excludes series loading, CAS persistence and downstream models; NPZ compression measured separately")
    return result
