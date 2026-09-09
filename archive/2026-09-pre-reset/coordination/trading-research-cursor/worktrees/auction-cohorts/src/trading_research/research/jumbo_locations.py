"""Exact rational Location geometry and conservative minute-OHLC outcome bounds.

Static draft for registered integration. No claim of sharp intrabar identification.
Candidate arrays are K; outcome arrays K x H. Directions share geometry and data.
"""
from fractions import Fraction
import numpy as np

MINUTE = 60_000_000_000
VERSION = "jumbo-location-exact-lattice-outer-bounds-v2"
GEOMETRY_CODES = {"quarter": 1, "EQ": 2, "threequarter": 3, "open": 4,
                  "close": 5, "low": 6, "high": 7, "lower_extension": 8,
                  "upper_extension": 9, "lower_region": 10, "upper_region": 11,
                  "body25": 12, "lower_body25": 13, "wick25": 14, "custom_band": 15}
GENERATOR_CODES = {"common_range_grid": 0, "source_disclosed": 1, "improved": 2,
                   "matched_placebo": 3, "statistical": 4, "tick_snapped": 5}
REASONS = {"missing_geometry": 1, "unpublished_at_origin": 2, "contract_mismatch": 4,
           "missing_origin": 8, "future_censored": 16, "source_version_mismatch": 32, "empty_contact_lattice": 64}
PREFIX_REASONS = {"complete": 0, "missing_origin": 1, "missing_interior": 2,
                  "invalid_observation": 4, "raw_contract_transition": 8,
                  "publication_cut": 16, "window_end": 32, "contract_mismatch": 64}
I64 = np.iinfo(np.int64)


def _rational(value):
    if isinstance(value, Fraction):
        result = value
    elif type(value) is int or isinstance(value,np.integer):
        result = Fraction(int(value))
    elif isinstance(value, (tuple, list)) and len(value) == 2 and all(type(x) is int for x in value):
        result = Fraction(*value)
    else:
        raise ValueError("exact integer/Fraction/(numerator,denominator) required")
    if not I64.min <= result.numerator <= I64.max or not 0 < result.denominator <= I64.max:
        raise ValueError("rational exceeds signed int64 storage")
    return result


def _encode(rows, metadata):
    keys = ("lower_num", "lower_den", "upper_num", "upper_den", "available_at_ns")
    columns = {k: np.asarray([r[k] for r in rows], dtype=np.int64) for k in keys}
    columns["geometry_code"] = np.asarray([r["geometry_code"] for r in rows], dtype=np.int16)
    columns["generator_code"] = np.asarray([r["generator_code"] for r in rows], dtype=np.int8)
    columns["valid_geometry"] = np.asarray([r["valid_geometry"] for r in rows], dtype=np.bool_)
    columns["slot"] = np.arange(len(rows), dtype=np.int32)
    return {"columns": columns, "metadata": metadata}


def range_candidate_specs(formation, *, definitions=None):
    """Return all intended geometry slots; definitions optionally replace the common grid.

    Custom definition keys: name, geometry (code-map key), generator (default
    source_disclosed), lower/upper exact rational, source_ids optional. Missing
    custom bounds retain an unavailable slot. Default grid is a named research
    comparator, never a claim all source recipes disclosed every ratio.
    """
    if hasattr(formation, "summary"):
        formation = formation.summary()
    f = dict(formation)
    complete = f.get("status") == "complete"
    prices = [f.get(k + "_ticks") for k in ("low", "high", "open", "close")]
    valid = complete and all(type(v) is int for v in prices)
    if valid:
        low, high, op, close = prices
        if not low <= min(op, close) <= max(op, close) <= high:
            raise ValueError("invalid formation geometry")
        width = high - low
    else:
        low = high = op = close = width = 0
    available = f.get("available_at_ns")
    if available is None:
        valid = False
        available = 0
    if type(available) is not int or not 0 <= available <= I64.max:
        raise ValueError("exact nonnegative availability required")
    if definitions is None:
        points = [("quarter", Fraction(low) + Fraction(width, 4)), ("EQ", Fraction(low) + Fraction(width, 2)),
                  ("threequarter", Fraction(low) + Fraction(3 * width, 4)), ("open", op), ("close", close),
                  ("low", low), ("high", high)]
        definitions = [dict(name=name, geometry=name, lower=p, upper=p, generator="common_range_grid") for name, p in points]
        for ratio in (Fraction(1, 2), Fraction(1), Fraction(133, 100), Fraction(83, 50), Fraction(2), Fraction(3), Fraction(4)):
            for side in ("lower", "upper"):
                p = low - ratio * width if side == "lower" else high + ratio * width
                definitions.append(dict(name=f"{side}_k{ratio.numerator}_{ratio.denominator}", geometry=side + "_extension",
                                        lower=p, upper=p, ratio=[ratio.numerator, ratio.denominator], generator="common_range_grid"))
        definitions += [dict(name="lower_133_166", geometry="lower_region", lower=low-Fraction(83,50)*width, upper=low-Fraction(133,100)*width, generator="common_range_grid"),
                        dict(name="upper_133_166", geometry="upper_region", lower=high+Fraction(133,100)*width, upper=high+Fraction(83,50)*width, generator="common_range_grid"),
                        dict(name="body25", geometry="body25", lower=Fraction(3*close+op,4), upper=Fraction(3*close+op,4), generator="common_range_grid"),
                        dict(name="lower_body25", geometry="lower_body25", lower=Fraction(min(op,close))+Fraction(abs(close-op),4), upper=Fraction(min(op,close))+Fraction(abs(close-op),4), generator="common_range_grid"),
                        dict(name="wick25", geometry="wick25", lower=Fraction(low)+Fraction(width,4), upper=Fraction(low)+Fraction(width,4), generator="common_range_grid")]
    rows, defs = [], []
    for definition in definitions:
        d = dict(definition)
        at = d.get("available_at_ns",available)
        if type(at) is not int or not 0 <= at <= I64.max:
            raise ValueError("exact nonnegative definition availability required")
        at = max(at,available)
        ok = valid and d.get("lower") is not None and d.get("upper") is not None
        a, b = (_rational(d["lower"]), _rational(d["upper"])) if ok else (Fraction(0), Fraction(0))
        if a > b:
            raise ValueError("ascending candidate band required")
        geometry, generator = d.get("geometry", "custom_band"), d.get("generator", "source_disclosed")
        if geometry not in GEOMETRY_CODES or generator not in GENERATOR_CODES:
            raise ValueError("unknown geometry/generator code")
        rows.append(dict(lower_num=a.numerator, lower_den=a.denominator, upper_num=b.numerator, upper_den=b.denominator,
                         available_at_ns=at, geometry_code=GEOMETRY_CODES[geometry], generator_code=GENERATOR_CODES[generator], valid_geometry=ok))
        defs.append({k: v for k, v in d.items() if k not in ("lower", "upper", "available_at_ns")})
    return _encode(rows, {"version": VERSION, "definitions": defs, "geometry_codes": GEOMETRY_CODES,
                         "generator_codes": GENERATOR_CODES, "formation_id": f.get("formation_id", f.get("window_version")),
                         "source_version": f.get("source_version"), "source_ids": f.get("source_ids"),
                         "clock": f.get("clock"), "contract_key": f.get("contract_key"),
                         "formation_start_ns": f.get("formation_start_ns"), "formation_end_ns": f.get("formation_end_ns"),
                         "formation_available_at_ns": available,
                         "width_ticks": width if valid else None, "zero_width": valid and width == 0,
                         "coincident_slots_retained": True})


def append_candidate_bands(candidates, definitions, *, available_at_ns=None):
    """Append L04/refinement/placebo bands sharing this formation and raw contract.

    Each definition has exact lower/upper, name, geometry/generator codes.
    Per-definition available_at_ns overrides the shared value, allowing missing
    upstream prediction to retain an invalid slot via lower/upper=None.
    """
    columns = _validate_candidates(candidates)
    metadata = dict(candidates["metadata"])
    rows = [{k: columns[k][i].item() for k in columns if k != "slot"} for i in range(len(columns["slot"]))]
    defs = list(metadata["definitions"])
    shared = available_at_ns
    if shared is None:
        shared = int(columns["available_at_ns"][0]) if len(rows) else 0
    for d in definitions:
        at = d.get("available_at_ns", shared)
        if type(at) is not int or not 0 <= at <= I64.max:
            raise ValueError("exact availability required")
        at = max(at,metadata.get("formation_available_at_ns",0))
        ok = d.get("lower") is not None and d.get("upper") is not None
        a, b = (_rational(d["lower"]), _rational(d["upper"])) if ok else (Fraction(0), Fraction(0))
        if a > b:
            raise ValueError("ascending candidate band required")
        geometry, generator = d.get("geometry", "custom_band"), d.get("generator", "improved")
        rows.append(dict(lower_num=a.numerator, lower_den=a.denominator, upper_num=b.numerator, upper_den=b.denominator,
                         available_at_ns=at, geometry_code=GEOMETRY_CODES[geometry], generator_code=GENERATOR_CODES[generator], valid_geometry=ok))
        defs.append({k:v for k,v in d.items() if k not in ("lower", "upper", "available_at_ns")})
    metadata["definitions"] = defs
    return _encode(rows, metadata)


def _validate_candidates(candidates):
    """Reject lossy or malformed caller arrays before rational conversion."""
    c = candidates["columns"]
    expected = {name:np.dtype(np.int64) for name in ("lower_num","lower_den","upper_num","upper_den","available_at_ns")}
    expected.update(geometry_code=np.dtype(np.int16),generator_code=np.dtype(np.int8),valid_geometry=np.dtype(np.bool_),slot=np.dtype(np.int32))
    if not set(expected)<=set(c):
        raise ValueError("required candidate columns missing")
    if any(not isinstance(v,np.ndarray) or v.ndim!=1 for v in c.values()):
        raise ValueError("one-dimensional candidate NumPy columns required")
    if any(c[name].dtype!=dtype for name,dtype in expected.items()):
        raise ValueError("candidate columns require their exact declared dtypes")
    k = len(c["slot"])
    if any(len(v)!=k for v in c.values()):
        raise ValueError("unequal candidate column lengths")
    if (np.any(c["lower_den"]<=0) or np.any(c["upper_den"]<=0) or np.any(c["available_at_ns"]<0)
            or np.any(c["slot"]<0) or len(np.unique(c["slot"]))!=k):
        raise ValueError("positive denominators, nonnegative availability and unique slots required")
    if (not np.isin(c["geometry_code"],tuple(GEOMETRY_CODES.values())).all()
            or not np.isin(c["generator_code"],tuple(GENERATOR_CODES.values())).all()):
        raise ValueError("unknown candidate code")
    meta = candidates["metadata"]
    if meta.get("version")!=VERSION or len(meta["definitions"])!=k:
        raise ValueError("candidate definition/version identity differs")
    return c


def _first(mask):
    return np.where(mask.any(axis=1), mask.argmax(axis=1), -1).astype(np.int16)


def _last(mask):
    return np.where(mask.any(axis=1), mask.shape[1]-1-mask[:, ::-1].argmax(axis=1), -1).astype(np.int16)


def _thresholds(values):
    floors = [v.numerator // v.denominator for v in values]
    ceils = [-(-v.numerator // v.denominator) for v in values]
    if any(not I64.min <= x <= I64.max for x in floors + ceils):
        raise ValueError("threshold outside int64 comparison domain")
    return np.asarray(floors, dtype=np.int64), np.asarray(ceils, dtype=np.int64)


def evaluate_location_bands(window, candidates, *, horizons=(15,30,60,180), available_cut, departure_ticks):
    """Conservative all-candidate bounds using contiguous known minute prefixes.

    Bands are closed, barrier attainment inclusive, invalidation strict close.
    Gap crosses the whole band strictly. Upper/lower barriers are upper+d/lower-d.
    Excursions use the center and share both directional roles. -1 times mean
    no observed event, NaN floats unavailable, eligible separates missing slots.
    """
    if type(available_cut) is not int or not 0<=available_cut<=I64.max:
        raise ValueError("nonnegative exact availability cut required")
    hs = tuple(horizons)
    if not hs or any(type(h) is not int or not 1 <= h <= 180 for h in hs) or len(set(hs)) != len(hs):
        raise ValueError("distinct bounded integer horizons required")
    if type(window.start) is not int or not 0<=window.start<window.end<=I64.max:
        raise ValueError("forecast endpoints require the nonnegative int64 domain")
    endpoints = [window.start+h*MINUTE for h in hs]
    if any(t>I64.max for t in endpoints):
        raise ValueError("horizon endpoint exceeds signed int64 storage")
    c = _validate_candidates(candidates)
    k, nh = len(c["slot"]), len(hs)
    lower = [Fraction(int(n),int(d)) for n,d in zip(c["lower_num"],c["lower_den"],strict=True)]
    upper = [Fraction(int(n),int(d)) for n,d in zip(c["upper_num"],c["upper_den"],strict=True)]
    if any(a>b for a,b in zip(lower,upper,strict=True)):
        raise ValueError("ascending band required")
    if type(departure_ticks) is int or isinstance(departure_ticks,(Fraction,np.integer)):
        ds = [_rational(departure_ticks)] * k
    else:
        if len(departure_ticks) != k:
            raise ValueError("one departure distance per candidate required")
        ds = [_rational(x) for x in departure_ticks]
    if any(d<=0 for d in ds):
        raise ValueError("positive exact departure distance required")
    lf, lc = _thresholds(lower)
    uf, uc = _thresholds(upper)
    bf, bc = _thresholds([a-d for a,d in zip(lower,ds,strict=True)])
    tf, tc = _thresholds([b+d for b,d in zip(upper,ds,strict=True)])
    center = [(a+b)/2 for a,b in zip(lower,upper,strict=True)]
    cf, _ = _thresholds(center)
    frac = np.asarray([float(v-int(q)) for v,q in zip(center,cf,strict=True)])
    s = window.series
    cut = min(available_cut, window.observation_cut_ns) if window.observation_cut_ns is not None else available_cut
    max_h = max(hs)
    count = 0
    stop_reason = PREFIX_REASONS["complete"]
    for i in range(window.left, min(window.right, window.left+max_h)):
        if s.start[i] != window.start+count*MINUTE:
            stop_reason = PREFIX_REASONS["missing_origin" if count==0 else "missing_interior"]
            break
        if s.end[i]>window.end:
            stop_reason = PREFIX_REASONS["window_end"]
            break
        if s.known[i]>cut:
            stop_reason = PREFIX_REASONS["publication_cut"]
            break
        if s.bad[i+1]!=s.bad[i]:
            stop_reason = PREFIX_REASONS["invalid_observation"]
            break
        if s.contract[i]!=s.contract[window.left]:
            stop_reason = PREFIX_REASONS["raw_contract_transition"]
            break
        count += 1
    if count<max_h and stop_reason==PREFIX_REASONS["complete"]:
        stop_reason = PREFIX_REASONS["window_end"] if window.start+count*MINUTE>=window.end else PREFIX_REASONS["missing_origin" if count==0 else "missing_interior"]
    if "different_raw_contract" in window.reasons:
        count = 0
        stop_reason = PREFIX_REASONS["contract_mismatch"]
    obs = {name:np.asarray(getattr(s,name)[window.left:window.left+count],dtype=np.int64) for name in ("open","high","low","close")}
    # Differences below must not wrap in signed arithmetic; exact comparison
    # kernels themselves never multiply prices by rational denominators.
    if count and k:
        lo = min(int(obs["low"].min()), int(cf.min()))
        hi = max(int(obs["high"].max()), int(cf.max()))
        if hi-lo > I64.max:
            raise ValueError("excursion difference exceeds signed int64 domain")
    eligible = np.asarray(c["valid_geometry"],dtype=bool).copy()
    reason = np.where(eligible,0,REASONS["missing_geometry"]).astype(np.uint32)
    late = c["available_at_ns"] > min(window.start,cut)
    eligible &= ~late
    reason[late] |= REASONS["unpublished_at_origin"]
    expected_contract = candidates["metadata"].get("contract_key")
    if (expected_contract is None or (window.count and expected_contract != window.contract_key)
            or "different_raw_contract" in window.reasons):
        eligible[:] = False
        reason[:] |= REASONS["contract_mismatch"]
    if candidates["metadata"].get("source_version")!=s.source_version:
        eligible[:] = False
        reason[:] |= REASONS["source_version_mismatch"]
    if not count:
        reason[:] |= REASONS["missing_origin"]
    geometry_eligible = eligible.copy()
    has_lattice = np.asarray(c["valid_geometry"],dtype=bool) & (lc<=uf)
    contact_ineligible = np.asarray(c["valid_geometry"],dtype=bool) & ~has_lattice
    eligible &= has_lattice
    reason[contact_ineligible] |= REASONS["empty_contact_lattice"]
    names = ("reach_lower","reach_upper","up_first_lower","up_first_upper","down_first_lower","down_first_upper",
             "up_reach_lower","up_reach_upper","down_reach_lower","down_reach_upper","close_above_invalidation_lower",
             "close_above_invalidation_upper","close_below_invalidation_lower","close_below_invalidation_upper","gap_through", "source_bar_intersection",
             "source_bar_intersection_lower", "source_bar_intersection_upper",
             "unconditional_upper_barrier_reach_lower","unconditional_upper_barrier_reach_upper",
             "unconditional_lower_barrier_reach_lower","unconditional_lower_barrier_reach_upper")
    out = {name:np.zeros((k,nh),dtype=np.uint8) for name in names}
    for name in ("first_possible_minute","first_definite_minute","last_possible_minute","latest_first_contact_minute"):
        out[name] = np.full((k,nh),-1,dtype=np.int16)
    for name in ("compatible_count","definite_count","possible_episode_count","definite_episode_count","source_bar_intersection_count"):
        out[name] = np.zeros((k,nh),dtype=np.int16)
    for name in ("up_excursion_lower","up_excursion_upper","down_excursion_lower","down_excursion_upper","terminal_from_center"):
        out[name] = np.full((k,nh),np.nan,dtype=np.float64)
    out["observed_minutes"] = np.asarray([min(count,h) for h in hs],dtype=np.int16)
    out["complete_horizon"] = np.asarray([count>=h for h in hs],dtype=np.bool_)
    out["horizon_reason"] = np.asarray([0 if count>=h else REASONS["future_censored"] for h in hs],dtype=np.uint32)
    out["prefix_stop_reason"] = np.asarray([0 if count>=h else stop_reason for h in hs],dtype=np.uint8)
    out["coverage_gap"] = np.asarray([count<h and stop_reason in (PREFIX_REASONS["missing_origin"],PREFIX_REASONS["missing_interior"],PREFIX_REASONS["invalid_observation"],PREFIX_REASONS["raw_contract_transition"]) for h in hs],dtype=np.bool_)
    out["eligible"] = eligible
    out["geometry_eligible"] = geometry_eligible
    out["has_lattice_price"] = has_lattice
    out["contact_ineligible_empty_lattice"] = contact_ineligible
    out["candidate_reason"] = reason
    out["endpoint_ns"] = np.asarray(endpoints,dtype=np.int64)
    known_prefix = [max(s.known[window.left:window.left+min(count,h)]) if min(count,h)>0 else -1 for h in hs]
    out["prefix_maturity_ns"] = np.asarray(known_prefix,dtype=np.int64)
    out["maturity_ns"] = np.asarray([known if count>=h else -1 for known,h in zip(known_prefix,hs,strict=True)],dtype=np.int64)
    if not count or not k:
        out["source_bar_intersection_upper"][:] = geometry_eligible[:,None]
        out["unconditional_upper_barrier_reach_upper"][:] = geometry_eligible[:,None]
        out["unconditional_lower_barrier_reach_upper"][:] = geometry_eligible[:,None]
        for name in ("reach_upper","up_first_upper","down_first_upper","up_reach_upper","down_reach_upper",
                     "close_above_invalidation_upper","close_below_invalidation_upper"):
            out[name][:] = eligible[:,None]
        return {"columns":out,"metadata":_out_metadata(hs,cut,window,candidates)}
    for start in range(0,k,256):
        stop = min(k,start+256)
        z = slice(start,stop)
        oo, hh, ll, cc = (obs[n][None,:] for n in ("open","high","low","close"))
        source_intersection = (ll<=uf[z,None]) & (hh>=lc[z,None])
        comp = source_intersection & has_lattice[z,None]
        definite = np.zeros_like(comp)
        for prices in (oo,hh,ll,cc):
            definite |= (prices>=lc[z,None]) & (prices<=uf[z,None])
        open_contact = (oo>=lc[z,None]) & (oo<=uf[z,None])
        gap = np.zeros_like(comp)
        previous = window.left-1
        if (previous>=0 and s.end[previous]==window.start and s.known[previous]<=min(cut,window.start)
                and s.bad[previous+1]==s.bad[previous] and s.contract[previous]==s.contract[window.left]):
            prior_close = int(s.close[previous])
            gap[:,0] = ((prior_close<lc[z]) & (obs["open"][0]>uf[z])) | ((prior_close>uf[z]) & (obs["open"][0]<lc[z]))
        if count>1:
            gap[:,1:] = ((cc[:,:-1]<lc[z,None]) & (oo[:,1:]>uf[z,None])) | ((cc[:,:-1]>uf[z,None]) & (oo[:,1:]<lc[z,None]))
        up = hh>=tc[z,None]
        down = ll<=bf[z,None]
        ca = cc>tf[z,None]
        cb = cc<bc[z,None]
        for hj,h in enumerate(hs):
            n = min(count,h)
            mask, definite_h = comp[:,:n], definite[:,:n]
            first, certain, last = _first(mask), _first(definite_h), _last(mask)
            exists, guaranteed = first>=0, certain>=0
            idx = np.arange(n)[None,:]
            possible_after = exists[:,None] & (idx>=first[:,None])
            known_open = np.zeros(stop-start,dtype=bool)
            good = np.flatnonzero(guaranteed)
            known_open[good] = open_contact[good,certain[good]]
            certain_after = guaranteed[:,None] & ((idx>certain[:,None]) | ((idx==certain[:,None]) & known_open[:,None]))
            pu, pd = _first(up[:,:n]&possible_after), _first(down[:,:n]&possible_after)
            gu, gd = _first(up[:,:n]&certain_after), _first(down[:,:n]&certain_after)
            complete = count>=h
            active = eligible[z]
            def put(name,value):
                out[name][z,hj] = np.where(active,value,0)
            put("reach_lower",guaranteed)
            put("reach_upper",exists | (not complete))
            put("up_reach_lower",gu>=0)
            put("down_reach_lower",gd>=0)
            put("up_reach_upper",(pu>=0) | (not complete))
            put("down_reach_upper",(pd>=0) | (not complete))
            put("up_first_lower",(gu>=0)&((pd<0)|(gu<pd)))
            put("down_first_lower",(gd>=0)&((pu<0)|(gd<pu)))
            put("up_first_upper",((pu>=0)&((gd<0)|(pu<=gd))) | ((not complete)&(gd<0)))
            put("down_first_upper",((pd>=0)&((gu<0)|(pd<=gu))) | ((not complete)&(gu<0)))
            close_after = guaranteed[:,None] & (idx>=certain[:,None])
            for key,hit in (("above",ca[:,:n]),("below",cb[:,:n])):
                put("close_"+key+"_invalidation_lower",(hit&close_after).any(axis=1))
                put("close_"+key+"_invalidation_upper",(hit&possible_after).any(axis=1)|(not complete))
            source_active = geometry_eligible[z]
            source_any = source_intersection[:,:n].any(axis=1)
            for side,attained in (("upper",up[:,:n].any(axis=1)),("lower",down[:,:n].any(axis=1))):
                out["unconditional_"+side+"_barrier_reach_lower"][z,hj] = np.where(source_active,attained,0)
                out["unconditional_"+side+"_barrier_reach_upper"][z,hj] = np.where(source_active,attained | (not complete),0)
            out["gap_through"][z,hj] = np.where(source_active,gap[:,:n].any(axis=1),0)
            out["source_bar_intersection_count"][z,hj] = np.where(source_active,source_intersection[:,:n].sum(axis=1),0)
            for key,val in (("source_bar_intersection",source_any),("source_bar_intersection_lower",source_any),
                            ("source_bar_intersection_upper",source_any | (not complete))):
                out[key][z,hj] = np.where(source_active,val,0)
            for name,value in (("first_possible_minute",first),("first_definite_minute",certain),("last_possible_minute",last),
                               ("latest_first_contact_minute",np.where(guaranteed,certain,last))):
                out[name][z,hj] = np.where(active,value,-1)
            put("compatible_count",mask.sum(axis=1))
            put("definite_count",definite_h.sum(axis=1))
            # Episode reset only after two full wholly-outside bars. This is a
            # minute-observable grouping, not a count of hidden tick revisits.
            last_contact = np.maximum.accumulate(np.where(mask,idx,-3),axis=1)
            previous_contact = np.concatenate((np.full((stop-start,1),-3),last_contact[:,:-1]),axis=1)
            new_episode = mask & (idx-previous_contact>=3)
            episode_start = np.maximum.accumulate(np.where(new_episode,idx,-1),axis=1)
            last_definite = np.maximum.accumulate(np.where(definite_h,idx,-1),axis=1)
            previous_definite = np.concatenate((np.full((stop-start,1),-1),last_definite[:,:-1]),axis=1)
            put("possible_episode_count",new_episode.sum(axis=1))
            put("definite_episode_count",(definite_h & (previous_definite<episode_start)).sum(axis=1))
            # Union over possible first contact bars is bounded by suffix from
            # earliest compatible; guaranteed lower uses bars after first
            # definite contact, including its close (and all extrema if open).
            sufhi = np.maximum.accumulate(obs["high"][:n][::-1])[::-1]
            suflo = np.minimum.accumulate(obs["low"][:n][::-1])[::-1]
            p, f = np.maximum(first,0), np.maximum(certain,0)
            hi_after, lo_after = obs["close"][f].copy(), obs["close"][f].copy()
            hi_after = np.where(known_open,np.maximum(hi_after,obs["high"][f]),hi_after)
            lo_after = np.where(known_open,np.minimum(lo_after,obs["low"][f]),lo_after)
            next_i = np.minimum(f+1,n-1)
            hi_after = np.where(f+1<n,np.maximum(hi_after,sufhi[next_i]),hi_after)
            lo_after = np.where(f+1<n,np.minimum(lo_after,suflo[next_i]),lo_after)
            keep = active & exists
            out["up_excursion_lower"][z,hj] = np.where(keep,np.where(guaranteed,np.maximum(0.,(hi_after-cf[z]).astype(float)-frac[z]),0.),np.nan)
            out["down_excursion_lower"][z,hj] = np.where(keep,np.where(guaranteed,np.maximum(0.,(cf[z]-lo_after).astype(float)+frac[z]),0.),np.nan)
            if complete:
                out["up_excursion_upper"][z,hj] = np.where(keep,np.maximum(0.,(sufhi[p]-cf[z]).astype(float)-frac[z]),np.nan)
                out["down_excursion_upper"][z,hj] = np.where(keep,np.maximum(0.,(cf[z]-suflo[p]).astype(float)+frac[z]),np.nan)
                out["terminal_from_center"][z,hj] = np.where(keep,(obs["close"][n-1]-cf[z]).astype(float)-frac[z],np.nan)
    return {"columns":out,"metadata":_out_metadata(hs,cut,window,candidates)}


def _out_metadata(horizons,cut,window,candidates):
    return {"version":VERSION,"horizons_minutes":list(horizons),"observation_cut_ns":cut,
            "forecast_start_ns":window.start,"forecast_end_ns":window.end,
            "contract_key":candidates["metadata"].get("contract_key"),"reason_codes":REASONS,"prefix_reason_codes":PREFIX_REASONS,
            "candidate_source_version":candidates["metadata"].get("source_version"),"forecast_source_version":window.series.source_version,
            "lineage_scope":"same immutable admitted series identity required; formation/forecast window versions may differ; revision ancestry owned by caller",
            "identification":"integer-tick exact trade contact; conservative outer bounds, not sharp intrabar order",
            "lattice":"empty integer intersection is structural contact impossibility even with missing future; raw geometry retained",
            "source_bar_intersection":"separate closed bar-range geometric intersection; does not imply any actual trade print",
            "eligibility":"eligible means causal geometry and nonempty contact lattice; geometry_eligible retains source intersection population",
            "departure":"inclusive upper+distance/lower-distance; close invalidation strict beyond barrier",
            "unconditional_barriers":"raw band upper+distance and lower-distance attainment regardless of contact; geometry_eligible population includes empty contact lattice",
            "excursion":"nonnegative center-relative; conditional on contact, NaN upper for censored tail",
            "episode":"compatible bars grouped until two wholly-outside bars; not exact tick retests",
            "time":"minute indexes are label intervals; endpoint_ns is forecast endpoint, maturity_ns actual max publication for complete horizon else -1; prefix_maturity_ns actual known-prefix publication",
            "directions":"up/down columns share candidate record; reversal needs separately known arrival side"}
