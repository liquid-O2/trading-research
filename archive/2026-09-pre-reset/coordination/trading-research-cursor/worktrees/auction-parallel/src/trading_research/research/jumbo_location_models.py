"""Causal model views of full factorized Location populations.

Flattening is an artifact operation, not permission to fit each chunk separately.
The caller must retain every chunk and gate the full population's measured fit
and serialization resources before using the shared fitting backend.
"""
from datetime import date
from fractions import Fraction
import numpy as np
from trading_research.errors import ContractError
from trading_research.operations.artifacts import digest
from .jumbo_matrix import PreparedPaths
from .jumbo_targets import Target, duration_classes

VERSION = "jumbo-location-model-views-v1"
BINARY = ("reach", "up_first", "down_first", "up_reach", "down_reach",
          "close_above_invalidation", "close_below_invalidation",
          "source_bar_intersection", "unconditional_upper_barrier_reach",
          "unconditional_lower_barrier_reach")
FEATURES = ("location_lower_from_anchor_ticks", "location_upper_from_anchor_ticks",
            "location_width_ticks", "location_anchor_side", "location_departure_ticks")


def prepare_location_chunk(result, context_matrix, *, plan):
    """Retain F×K×H intent rows, joining context only on causal identities.

    Context must have exactly one row per root/date/source-clock/origin at each
    requested horizon. Future availability never selects a feature row.
    """
    a, m = result["arrays"], result["manifest"]
    formations = m["formations"]
    f, k, h = len(formations), m["candidates_per_formation"], len(a["horizons_minutes"])
    if k != 26 * len(plan["location_generators"]) or tuple(m["active_generators"]) != tuple(plan["location_generators"]):
        raise ContractError("full declared Location generator population required")
    if tuple(a["horizons_minutes"]) != tuple(plan["location_horizons_minutes"]):
        raise ContractError("Location horizons differ from frozen plan")
    for name, spec in m["schema"].items():
        if name not in a or list(a[name].shape) != spec["shape"] or str(a[name].dtype) != spec["dtype"]:
            raise ContractError("Location factorized schema mismatch")
    if f != m["formation_count"] or any(row["formation_index"] != i for i,row in enumerate(formations)):
        raise ContractError("Location formation lineage is not aligned")
    cf, cc = context_matrix.fields, context_matrix.categories
    index = {}
    for i in range(context_matrix.size):
        key = (cc["root"][int(cf["root"][i])], int(cf["date"][i]),
               cc["clock"][int(cf["clock"][i])], int(cf["origin_ns"][i]),
               cc["horizon"][int(cf["horizon"][i])])
        if key in index:
            raise ContractError("duplicate causal context identity")
        index[key] = i
    fi, ki, hi = np.indices((f,k,h)).reshape(3,-1)
    rows = []
    for row in formations:
        for minutes in a["horizons_minutes"]:
            key = (m["root"], date.fromisoformat(row["date"]).toordinal(), row["clock"],
                   row["forecast_origin_ns"], f"after_{int(minutes)}m")
            if key not in index:
                raise ContractError("missing exact causal Location context identity")
            rows.append(index[key])
    context_index = np.asarray(rows,dtype=np.int64).reshape(f,h)[fi,hi]
    extra = np.full((f,k,len(FEATURES)),np.nan,dtype=np.float64)
    for i,row in enumerate(formations):
        anchor = row["anchor_ticks"]
        for j in range(k):
            if not a["geometry_valid_geometry"][i,j] or anchor is None:
                continue
            lo = Fraction(int(a["geometry_lower_num"][i,j]),int(a["geometry_lower_den"][i,j]))
            up = Fraction(int(a["geometry_upper_num"][i,j]),int(a["geometry_upper_den"][i,j]))
            extra[i,j] = (float(lo-anchor),float(up-anchor),float(up-lo),
                          int(a["anchor_side"][i,j]),row["departure_ticks"])
    x = np.concatenate((context_matrix.features[context_index],extra[fi,ki]),axis=1)
    # A global category vocabulary is supplied by the caller's full clock plan;
    # local category discovery would silently change fitted prior identities.
    clocks = tuple(cc["clock"])
    generators = tuple(plan["location_generators"])
    composites = tuple(f"{clock}|{generator}|{slot}" for clock in clocks for generator in generators for slot in range(26))
    source_codes = np.asarray([clocks.index(row["clock"]) for row in formations],dtype=np.int64)[fi]
    generator = a["generator_id"][ki].astype(np.int64)
    ancestor = a["ancestor_slot"][ki].astype(np.int64)
    fields = {name:np.asarray(values)[context_index].copy() for name,values in cf.items()}
    fields.update(clock=(source_codes*len(generators)+generator)*26+ancestor,
                  source_clock=source_codes,generator=generator,ancestor_slot=ancestor,
                  formation_index=fi,candidate_index=ki,
                  horizon=hi.astype(np.int64),planned_minutes=a["horizons_minutes"][hi].astype(np.int64),
                  maturity_at_ns=a["horizon_maturity_ns"][fi,hi],
                  prefix_maturity_at_ns=a["horizon_prefix_maturity_ns"][fi,hi])
    names = list(context_matrix.manifest["feature_columns"]) + ["x_"+name for name in FEATURES]
    groups = {name:list(columns) for name,columns in context_matrix.manifest["feature_groups"].items()}
    for group in ("own","full"):
        groups[group] = groups[group] + list(FEATURES)
    manifest = dict(version=VERSION,rows=len(fi),feature_columns=names,feature_groups=groups,
                    context_matrix_id=context_matrix.manifest["id"],source_version=m["source_version"],
                    root=m["root"],year=m["year"],formation_ids=[r["formation_id"] for r in formations],
                    flatten_order="formation,candidate,horizon",population="all declared candidates and horizons",
                    location_manifest_id=digest(m))
    manifest["id"] = digest(manifest)
    categories = dict(cc,clock=composites,horizon=tuple(f"after_{int(v)}m" for v in a["horizons_minutes"]),
                      source_clock=clocks,generator=generators)
    matrix = PreparedPaths(manifest,x,fields,categories,context_matrix.shards)
    targets = {}
    # Geometry/contact eligibility has F x K axes; horizon-specific outcomes
    # below have F x K x H axes and must select all three indices.
    contact = a["outcome_eligible"][fi,ki]
    geometry = a["outcome_geometry_eligible"][fi,ki]
    seen = a["horizon_observed_minutes"][fi,hi].astype(np.int64)
    complete = a["horizon_complete_horizon"][fi,hi]
    known = fields["prefix_maturity_at_ns"]
    def add(name,kind,values,eligible,metadata, maturity=known):
        metadata = dict(metadata,source_matrix=manifest["id"])
        metadata["id"] = digest(dict(name=name,kind=kind,metadata=metadata))
        targets[name] = Target(name,kind,values,eligible & (maturity>=0),maturity,metadata)
    for name in BINARY:
        lo,up = (a["outcome_"+name+suffix][fi,ki,hi] for suffix in ("_lower","_upper"))
        if np.any(lo>up):
            raise ContractError("Location binary bounds inverted")
        allowed = np.column_stack((lo==0,up==1))
        eligible = geometry if name.startswith(("source_bar_","unconditional_")) else contact
        add(name,"interval_categorical",allowed,eligible & (seen>0),
            dict(classes=[0,1],definition="Compatible OHLC event bounds; unknown future retains both possibilities"))
    first = a["outcome_first_possible_minute"][fi,ki,hi]
    definite = a["outcome_first_definite_minute"][fi,ki,hi]
    latest = a["outcome_latest_first_contact_minute"][fi,ki,hi]
    # Possible-only contact is not evidence that an event occurred. Preserve
    # no-event and every possible event cell until the end of the horizon.
    lower = np.where(definite>=0,first,np.nan).astype(float)
    upper = np.where(definite>=0,latest+1,np.nan).astype(float)
    censor = np.where((first>=0)&(definite<0),first,seen).astype(np.int64)
    allowed = duration_classes(lower,upper,censor,fields["planned_minutes"])
    add("first_contact_duration","interval_categorical",allowed,contact & (seen>0),
        dict(classes=list(range(7)),definition="First contact compatible horizon-fraction cells and no contact; possible-only evidence retains no-event"))
    possible = a["outcome_possible_episode_count"][fi,ki,hi]
    certain = a["outcome_definite_episode_count"][fi,ki,hi]
    add("second_observed_episode","interval_categorical",
        np.column_stack((certain<2,(possible>=2)|~complete)),contact & (seen>0),
        dict(classes=[0,1],definition="Second OHLC contact episode separated by two wholly outside bars; not latent tick revisits"))
    for name in ("up_excursion_lower","up_excursion_upper","down_excursion_lower","down_excursion_upper","terminal_from_center"):
        values = a["outcome_"+name][fi,ki,hi]
        add("observable_"+name,"continuous",values,contact & complete & np.isfinite(values),
            dict(unit="raw ticks",nonnegative=name!="terminal_from_center",
                 definition="Observable endpoint of OHLC post-contact bound; not an exact latent excursion"),
            fields["maturity_at_ns"])
    return matrix,targets


def paired_generator_date_losses(matrix, losses, eligible, *, scorer_id):
    """Pair fixed-scorer losses by root/date/source-clock/ancestor/horizon.

    Returns date aggregates for downstream registered date-block inference.
    Every generator must be present and scoreable on a pair; unpaired intended
    rows are counted explicitly. This never selects a scorer or a generator.
    """
    losses, eligible = np.asarray(losses), np.asarray(eligible)
    if not isinstance(scorer_id,str) or not scorer_id or losses.shape != (matrix.size,) or eligible.shape != losses.shape:
        raise ContractError("one frozen scorer and aligned loss/eligibility required")
    fields, generators = matrix.fields, matrix.categories["generator"]
    pairs = {}
    for i in range(matrix.size):
        key = tuple(int(fields[name][i]) for name in ("root","date","source_clock","ancestor_slot","horizon"))
        generator = int(fields["generator"][i])
        bucket = pairs.setdefault(key,{})
        if generator in bucket:
            raise ContractError("duplicate generator ancestry pair")
        bucket[generator] = i
    dates, paired = {}, 0
    for key,bucket in pairs.items():
        if set(bucket) != set(range(len(generators))):
            raise ContractError("missing intended generator in ancestry pair")
        rows = [bucket[g] for g in range(len(generators))]
        if not np.all(eligible[rows]) or not np.all(np.isfinite(losses[rows])):
            continue
        paired += 1
        total,count = dates.setdefault(key[1],(np.zeros(len(generators)),0))
        dates[key[1]] = (total+losses[rows],count+1)
    return dict(scorer_id=scorer_id,generators=list(generators),intended_pairs=len(pairs),
                paired_pairs=paired,unpaired_pairs=len(pairs)-paired,
                dates=[dict(date=day,paired_ancestries=count,mean_losses=(total/count).tolist(),
                            improvement_over_raw=(total[0]/count-total/count).tolist())
                       for day,(total,count) in sorted(dates.items())],
                interpretation="Same frozen scorer; identical ancestry/date/horizon support; inference uses whole-date blocks")


def statistical_location_definitions(*, anchor_ticks, width_ticks, origin_ns, provider=None):
    """Twelve explicitly gridded frozen-forecast geometries, never raw P zones.

    Provider is an attested prediction record: original_fit_id, model_id,
    source_analysis_id, prediction_id, forecast_origin_ns, available_at_ns,
    fit_labels_before_ns, historical_training_calibration_closure_ns, actual_artifact_created_at_ns, retrospective_reconstruction, creation_period, and two heads. Each head
    contains target, model_id, quantiles and binary64 values. The caller verifies
    these identities against retained model/prediction artifacts before calling.
    Absent pre-selection predictions keep all twelve unavailable intent slots.
    """
    import struct
    from .jumbo_targets import boundary_ns
    qs = (.25,.5,.75,.95)
    limit = np.iinfo(np.int64)
    if any(type(v) is not int for v in (anchor_ticks,width_ticks,origin_ns)) or width_ticks <= 0 or origin_ns < 0:
        raise ContractError("exact causal anchor, positive width, and origin required")
    if not limit.min <= anchor_ticks <= limit.max or width_ticks > limit.max or origin_ns > limit.max:
        raise ContractError("statistical geometry input exceeds int64")
    reason = "independent_frozen_prediction_unavailable"
    provenance = None
    heads = {}
    if provider is not None:
        for name in ("original_fit_id","model_id","source_analysis_id","prediction_id"):
            if not isinstance(provider.get(name),str) or not provider[name]:
                raise ContractError("retained statistical prediction identity required")
        for name in ("forecast_origin_ns","available_at_ns","fit_labels_before_ns","historical_training_calibration_closure_ns","actual_artifact_created_at_ns"):
            if type(provider.get(name)) is not int or not 0 <= provider[name] <= limit.max:
                raise ContractError("exact statistical chronology required")
        if (provider["forecast_origin_ns"] != origin_ns or provider["available_at_ns"] > origin_ns
                or provider["historical_training_calibration_closure_ns"] > provider["available_at_ns"]
                or provider["fit_labels_before_ns"] > provider["historical_training_calibration_closure_ns"]
                or provider["fit_labels_before_ns"] > boundary_ns("2023-01-01")
                or origin_ns < boundary_ns("2024-07-01")
                or provider["historical_training_calibration_closure_ns"] > boundary_ns("2024-07-01")
                or provider.get("retrospective_reconstruction") is not True
                or provider.get("creation_period") not in ("select","heldout")):
            raise ContractError("statistical zones require independent frozen selection/heldout predictions")
        for side,target in (("high","future_high_from_known_W"),("low","future_low_from_known_W")):
            head = provider.get(side)
            if (not isinstance(head,dict) or head.get("target") != target
                    or not isinstance(head.get("model_id"),str) or not head["model_id"]
                    or len(head.get("quantiles",())) != len(head.get("values",()))):
                raise ContractError("identified independent high/low quantile heads required")
            quantiles = list(head["quantiles"])
            if len(set(quantiles)) != len(quantiles) or not set(qs) <= set(quantiles):
                raise ContractError("declared statistical quantiles absent or duplicated")
            values = [head["values"][quantiles.index(q)] for q in qs]
            if any(type(v) not in (float,np.float64) or not np.isfinite(v) for v in values):
                raise ContractError("finite original binary64 prediction values required")
            heads[side] = values
        provenance = {key:provider[key] for key in ("original_fit_id","model_id","source_analysis_id",
            "prediction_id","forecast_origin_ns","available_at_ns","fit_labels_before_ns","historical_training_calibration_closure_ns","actual_artifact_created_at_ns","creation_period")}
        provenance["retrospective_reconstruction"] = True
        provenance["chronology_interpretation"] = "Historical training/tuning/calibration closure, reconstructed later; actual artifact creation is not backdated"
        provenance["quantile_crossing"] = {side:any(values[i]>values[i+1] for i in range(len(values)-1)) for side,values in heads.items()}
        provenance["heads"] = {side:dict(target=provider[side]["target"],model_id=provider[side]["model_id"]) for side in heads}
        reason = None
    def coordinate(side, qi):
        if provider is None:
            return None,None
        prediction = float(heads[side][qi])
        raw = Fraction(anchor_ticks) + (1 if side=="high" else -1)*width_ticks*Fraction.from_float(prediction)
        gridded = Fraction(round(raw*1024),1024)
        error = gridded-raw
        metadata = dict(prediction_ieee754_hex=struct.pack(">d",prediction).hex(),
                        prediction_quantile=qs[qi],raw_bound_numerator=str(raw.numerator),
                        raw_bound_denominator=str(raw.denominator),
                        grid_error_numerator=str(error.numerator),grid_error_denominator=str(error.denominator),
                        raw_bound_finite=True,storage_representable=(limit.min<=gridded.numerator<=limit.max and gridded.denominator<=limit.max))
        if abs(error)>Fraction(1,2048):
            raise ContractError("declared statistical grid error exceeded")
        return (gridded if metadata["storage_representable"] else None),metadata
    defs = []
    for qi,q in enumerate(qs):
        low,lmeta = coordinate("low",qi)
        high,hmeta = coordinate("high",qi)
        inverted = low is not None and high is not None and low>high
        for kind,lo,up in (("low_point",low,low),("high_point",high,high),
                           ("paired_band",None if inverted else low,None if inverted else high)):
            defs.append(dict(name=f"frozen_statistical_{kind}_q{q:g}",geometry="custom_band",generator="improved",
                location_generator="frozen_statistical_grid_1_over_1024_tick",ancestor_slot=qi*3+(0 if kind=="low_point" else 1 if kind=="high_point" else 2),
                lower=lo,upper=up,available_at_ns=origin_ns if provider is None else provider["available_at_ns"],
                unavailable_reason=reason or ("inverted_predicted_band" if kind=="paired_band" and inverted else
                    "grid_coordinate_exceeds_int64" if lo is None or up is None else None),
                provenance=provenance,quantile=q,kind=kind,inverted_band=bool(inverted),
                low_coordinate=lmeta,high_coordinate=hmeta,
                definition="A-W*q_low and A+W*q_high; signed head values retained; points not forced to opposite sides",
                rounding="nearest 1/1024 tick, ties to even; absolute error <=1/2048 tick",
                source_claim="new statistical forecast geometry; not an unmodified disclosed source P zone"))
    return defs
