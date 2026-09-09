"""Compact, causally typed views of the admitted Jumbo research tables.

Row positions refer to the exact retained Parquet manifests. Numerical model
features never include a future observation or a label-availability mask.
"""
from dataclasses import dataclass
from datetime import date
import hashlib

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest
from trading_research.research.jumbo_tables import FEATURES, VERSION

PATH_CLASSES = ("no_break", "high_only", "low_only", "high_then_low", "low_then_high", "ambiguous")
FLOAT_LABELS = ("maximum_up_W", "maximum_down_W", "terminal_W", "remaining_range_W",
                "upper_overshoot_W", "lower_overshoot_W", "first_lower_minutes", "first_upper_minutes",
                "second_lower_minutes", "second_upper_minutes", "prefix_first_lower_minutes",
                "prefix_first_upper_minutes")
INTEGER_LABELS = ("origin_ns", "endpoint_ns", "planned_minutes", "maturity_at_ns", "prefix_maturity_at_ns",
                  "observed_prefix_minutes", "label_origin_open_ticks", "maximum_up_ticks", "maximum_down_ticks",
                  "terminal_ticks", "squared_close_returns_ticks2")
FEATURE_GROUPS = {
    "controls": ("width_ticks", "formation_minutes", "prior_width_ticks", "last_close_age_minutes",
                 "weekday", "month", "cut_ny_minutes", "early_close"),
    "own": ("width_ticks", "formation_minutes", "prior_width_ticks", "last_close_age_minutes",
            "weekday", "month", "cut_ny_minutes", "early_close", "log_volume", "open_position",
            "close_position", "body_fraction", "up_fraction", "down_fraction", "last_close_position"),
    "full": FEATURES,
}


def exact_known_anchor(low_ticks, width_ticks, positions):
    """REFERENCE-ONLY inverse retained for historical comparison fixtures.

    The active prepare_paths pipeline never calls this function.
    Invert an extracted normalized integer price only if uniquely implied.

    Extraction converted the exact rational (A-L)/W to binary64. An outward
    rounding bound includes both that conversion and this multiplication. If
    it cannot identify one integer tick, the caller needs a raw-source lookup;
    it must not invent a price by ordinary floating rounding.
    """
    import numpy as np
    low, width, position = np.asarray(low_ticks), np.asarray(width_ticks), np.asarray(positions, dtype=np.float64)
    if low.dtype != np.int64 or width.dtype != np.int64 or low.shape != width.shape or low.shape != position.shape:
        raise ContractError("exact aligned int64 range coordinates required")
    valid = (width > 0) & np.isfinite(position)
    product = np.zeros(position.shape, dtype=np.float64)
    np.multiply(width, position, out=product, where=valid)
    rounded = np.rint(product)
    bound = np.abs(width.astype(np.float64)) * np.abs(np.spacing(np.abs(position)))
    bound += np.abs(np.spacing(np.abs(product)))
    bound = np.nextafter(bound, np.inf)
    valid &= np.isfinite(bound) & (np.abs(product - rounded) + bound < .5)
    valid &= np.abs(rounded) < 2**62
    # Uniqueness is not evidence that an arbitrary float originated from an
    # integer price. Require the recovered ratio to reproduce the source
    # binary64 observation. Larger denominators need a raw-source lookup.
    valid &= (width <= 2**53) & (np.abs(rounded) <= 2**53)
    roundtrip = np.full(position.shape, np.nan)
    np.divide(rounded, width, out=roundtrip, where=valid)
    valid &= roundtrip == position
    offset = np.zeros(low.shape, dtype=np.int64)
    offset[valid] = rounded[valid].astype(np.int64)
    upper_ok = (offset <= 0) | (low <= np.iinfo(np.int64).max - np.maximum(offset, 0))
    lower_ok = (offset >= 0) | (low >= np.iinfo(np.int64).min - np.minimum(offset, 0))
    valid &= upper_ok & lower_ok
    anchor = np.zeros(low.shape, dtype=np.int64)
    np.add(low, offset, out=anchor, where=valid)
    return anchor, valid


def _read_columns(store, ref, columns):
    import pyarrow as pa
    import pyarrow.parquet as pq
    from trading_research.research.jumbo_study import _ref
    raw = store.read(_ref(ref))
    reader = pa.BufferReader(raw)
    schema = pq.read_schema(reader)
    if hashlib.sha256(schema.serialize().to_pybytes()).hexdigest() != ref["schema_sha256"]:
        raise IntegrityError("prepared table schema changed")
    reader.seek(0)
    table = pq.read_table(reader, columns=columns)
    if table.num_rows != ref["rows"]:
        raise IntegrityError("prepared table row population changed")
    return table


def _codes(column, names):
    import numpy as np
    mapping = {name: at for at, name in enumerate(names)}
    encoded = column.combine_chunks().dictionary_encode()
    values = encoded.dictionary.to_pylist()
    try:
        lookup = np.asarray([mapping[name] for name in values], dtype=np.int16)
    except KeyError as exc:
        raise IntegrityError("undeclared category in prepared population") from exc
    return lookup[encoded.indices.to_numpy(zero_copy_only=False)]


def _ints(column):
    import numpy as np
    import pyarrow as pa
    import pyarrow.compute as pc
    value = pc.fill_null(column, pa.scalar(-1, type=pa.int64())).to_numpy(zero_copy_only=False)
    if value.dtype != np.int64:
        raise IntegrityError("integer timestamps or ticks passed through a lossy conversion")
    return value


@dataclass
class PreparedPaths:
    manifest: dict
    features: object
    fields: dict
    categories: dict
    shards: tuple

    @property
    def size(self):
        return len(self.features)

    def phase(self, first, last, *, maturity_before=None, label_known=None):
        import numpy as np
        first_day, last_day = date.fromisoformat(first).toordinal(), date.fromisoformat(last).toordinal()
        chosen = (self.fields["date"] >= first_day) & (self.fields["date"] <= last_day)
        if maturity_before is not None:
            if type(maturity_before) is not int or maturity_before < 0:
                raise ContractError("maturity boundary must be exact nonnegative integer nanoseconds")
            known = self.fields["maturity_at_ns"] if label_known is None else np.asarray(label_known)
            if known.dtype != np.int64 or known.shape != self.fields["date"].shape:
                raise ContractError("label maturity must be an aligned exact int64 vector")
            chosen &= (known >= 0) & (known < maturity_before)
        return chosen

    def equal_date_weights(self, mask):
        import numpy as np
        days = self.fields["date"][mask]
        _, inverse, counts = np.unique(days, return_inverse=True, return_counts=True)
        weights = 1.0 / counts[inverse]
        return weights / weights.sum() if len(weights) else weights


def prepare_paths(store, shards, *, plan, phase, anchor_supplements):
    import numpy as np
    import pyarrow as pa
    from trading_research.research.jumbo_tables import table_schema
    from trading_research.research.jumbo_anchors import (anchor_schema, normalized_table_ref,
        supplement_feature_names, validate_anchor_manifest, validate_anchor_content, ANCHOR_INTEGER_COLUMNS)
    if not isinstance(anchor_supplements,dict):
        raise ContractError("explicit exact anchor supplement mapping required")
    supplement_specs=[]
    for shard in shards:
        key=(shard["root"],shard["year"])
        spec=anchor_supplements.get(key)
        if not isinstance(spec,dict) or not {"manifest","table_ref"}<=set(spec):
            raise IntegrityError("source shard has no explicit exact anchor supplement")
        meta=validate_anchor_manifest(spec["manifest"],root=key[0],year=key[1],
              path_ref=shard["tables"]["paths"],formation_ref=shard["tables"]["formations"],table_ref=spec["table_ref"])
        supplement_specs.append((meta,normalized_table_ref(spec["table_ref"])))
    if not supplement_specs:
        raise ContractError("nonempty prepared source population required")
    anchor_definition=supplement_specs[0][0]
    if any(meta["feature_columns"]!=anchor_definition["feature_columns"] or meta["feature_groups"]!=anchor_definition["feature_groups"]
           or meta["frozen_analysis_id"]!=anchor_definition["frozen_analysis_id"] for meta,_ in supplement_specs):
        raise IntegrityError("supplement feature/original-analysis definitions differ across shards")
    added_features=supplement_feature_names(anchor_definition["relationship_clocks"])
    clocks = tuple(plan["expected_formation_clock_ids"])
    horizons = tuple([f"after_{m}m" for m in plan["horizons_minutes"]] + ["to_actual_cash_close", "common_1001_to_actual_cash_close"]
                     + [f"prefix_{m}m_to_actual_cash_close" for m in plan["prefix_delays_minutes"]])
    categories = {"clock": clocks, "horizon": horizons, "root": ("NQ", "ES"),
                  "path": (*PATH_CLASSES, "censored", "zero_width"),
                  "inclusive_path": (*PATH_CLASSES, "censored", "zero_width"),
                  "prefix_first_side": ("neither", "upper", "lower", "ambiguous", "unavailable")}
    required = (*["x_" + name for name in FEATURES], *FLOAT_LABELS, *INTEGER_LABELS,
                "date", "year", "clock", "horizon", "root", "path", "inclusive_path", "prefix_first_side", "formation_id",
                "prefix_both_breach", "reclaim_observed", "label_version", "row_id", "contract_key")
    if not set(required) <= set(table_schema("paths").names):
        raise IntegrityError("target adapter references fields absent from the actual path schema")
    if (len({(s["root"], s["year"]) for s in shards}) != len(shards)
            or len({s["tables"]["paths"]["sha256"] for s in shards}) != len(shards)):
        raise IntegrityError("duplicate prepared source shard")
    rows = sum(s["tables"]["paths"]["rows"] for s in shards)
    if not 0 < rows <= 1_200_000:
        raise ContractError("prepared matrix exceeds the declared complete-population domain")
    x = np.full((rows, len(FEATURES)+len(added_features)), np.nan, dtype=np.float32)
    fields = {name: np.full(rows, np.nan, dtype=np.float64) for name in FLOAT_LABELS}
    fields.update({name: np.full(rows, -1, dtype=np.int64) for name in (*INTEGER_LABELS, "date", "anchor_ticks", "formation_low_ticks", "formation_width_ticks", "prior_width_ticks", "anchor_start_ns", "anchor_end_ns", "anchor_known_at_ns", "anchor_observation_known_at_ns")})
    fields.update({name: np.full(rows, -1, dtype=np.int16) for name in categories})
    fields.update({name: np.full(rows, -1, dtype=np.int8) for name in ("prefix_both_breach", "reclaim_observed")})
    fields["anchor_identified"] = np.zeros(rows, dtype=bool)
    fields["anchor_source_kind"] = np.full(rows,-1,dtype=np.int8)
    offsets, start = [], 0
    for shard,(anchor_meta,anchor_ref) in zip(shards,supplement_specs,strict=True):
        table = _read_columns(store, shard["tables"]["paths"], list(required))
        n = table.num_rows
        take = slice(start, start + n)
        if set(table["label_version"].unique().to_pylist()) != {VERSION}:
            raise IntegrityError("prepared path label version changed")
        if (table["root"].unique().to_pylist() != [shard["root"]]
                or table["year"].unique().to_pylist() != [shard["year"]]):
            raise IntegrityError("prepared table root/year differs from its declared shard")
        import pyarrow.compute as pc
        observed_here = pc.is_in(table["path"], value_set=pa.array(PATH_CLASSES)).to_numpy(zero_copy_only=False)
        for name in INTEGER_LABELS:
            nulls = table[name].is_null().to_numpy(zero_copy_only=False)
            if np.any(nulls & (True if name in ("origin_ns", "endpoint_ns", "planned_minutes", "observed_prefix_minutes") else observed_here)):
                raise IntegrityError("observed target or mandatory clock contains a missing integer")
        for j, name in enumerate(FEATURES):
            values = table["x_" + name].to_numpy(zero_copy_only=False)
            if np.any(np.isinf(values)) or np.any(np.abs(values[np.isfinite(values)]) > np.finfo(np.float32).max):
                raise IntegrityError("available feature is outside the declared finite model representation")
            x[take, j] = values
        prior_width = table["x_prior_width_ticks"].to_numpy(zero_copy_only=False)
        valid_prior_width = np.isfinite(prior_width)
        if np.any(valid_prior_width & ((prior_width < 0) | (prior_width > 2**53) | (prior_width != np.floor(prior_width)))):
            raise IntegrityError("known prior width is not an exactly represented integer tick distance")
        prior_values = np.full(n, -1, dtype=np.int64)
        prior_values[valid_prior_width] = prior_width[valid_prior_width].astype(np.int64)
        fields["prior_width_ticks"][take] = prior_values
        for name in FLOAT_LABELS:
            values = table[name].to_numpy(zero_copy_only=False)
            if name in FLOAT_LABELS[:6] and np.any(observed_here & ~np.isfinite(values)):
                raise IntegrityError("complete observed target has a missing continuous outcome")
            fields[name][take] = values
        for name in INTEGER_LABELS:
            fields[name][take] = _ints(table[name])
        for name, values in categories.items():
            column = table[name]
            if name == "prefix_first_side":
                import pyarrow.compute as pc
                column = pc.fill_null(column, "unavailable")
            fields[name][take] = _codes(column, values)
        date_values = sorted(table["date"].unique().to_pylist())
        if any(date.fromisoformat(day).year != shard["year"] for day in date_values):
            raise IntegrityError("prepared civil date differs from its declared shard year")
        ordinal = np.asarray([date.fromisoformat(day).toordinal() for day in date_values], dtype=np.int64)
        fields["date"][take] = ordinal[_codes(table["date"], tuple(date_values))]
        for name in ("prefix_both_breach", "reclaim_observed"):
            column = table[name]
            import pyarrow.compute as pc
            values = pc.fill_null(pc.cast(column, pa.int8()), -1).to_numpy(zero_copy_only=False)
            fields[name][take] = values
        formation = _read_columns(store, shard["tables"]["formations"],
                                  ["formation_id", "low_ticks", "width_ticks", "source_version"])
        # This joins known formation geometry, never a future receiver price.
        parents = {key: at for at, key in enumerate(formation["formation_id"].to_pylist())}
        if len(parents) != formation.num_rows:
            raise IntegrityError("duplicate formation ancestor in retained shard")
        try:
            parent_index = np.fromiter((parents[key] for key in table["formation_id"].to_pylist()), dtype=np.int64, count=n)
        except KeyError as exc:
            raise IntegrityError("path has no retained formation ancestor") from exc
        low = _ints(formation["low_ticks"])[parent_index]
        width = _ints(formation["width_ticks"])[parent_index]
        geometry_valid = (formation["low_ticks"].is_valid().to_numpy(zero_copy_only=False)[parent_index]
                          & formation["width_ticks"].is_valid().to_numpy(zero_copy_only=False)[parent_index])
        if np.any(observed_here & ~geometry_valid):
            raise IntegrityError("observed target has missing formation geometry")
        if formation["source_version"].unique().to_pylist()!=[anchor_meta["source_version"]]:
            raise IntegrityError("exact supplement and saved formation source versions differ")
        supplement=_read_columns(store,anchor_ref,anchor_schema(anchor_meta["relationship_clocks"]).names)
        validate_anchor_content(supplement,anchor_meta)
        if supplement.num_rows!=n or not np.array_equal(_ints(supplement["source_path_row"]),np.arange(n,dtype=np.int64)):
            raise IntegrityError("exact supplement source row positions changed")
        for name in ("root","year","date","clock","horizon","formation_id","origin_ns","endpoint_ns"):
            if not supplement[name].equals(table[name]):
                raise IntegrityError("exact supplement path row/clock/receiver identity differs")
        if not supplement["source_row_id"].equals(table["row_id"]):
            raise IntegrityError("exact supplement source row ID differs")
        if not supplement["anchor_contract_key"].equals(table["contract_key"]):
            raise IntegrityError("exact supplement raw coordinate differs from source formation")
        if supplement["source_version"].unique().to_pylist()!=[anchor_meta["source_version"]]:
            raise IntegrityError("exact supplement source version changed")
        if supplement["anchor_available"].null_count or supplement["saved_position_reconciled"].null_count:
            raise IntegrityError("exact supplement requires explicit availability/reconciliation")
        identified=supplement["anchor_available"].to_numpy(zero_copy_only=False)
        if np.any(identified & ~geometry_valid):
            raise IntegrityError("available exact anchor lacks saved formation geometry")
        source_codes={"formation_unavailable":0,"expected_published_minute":1,"formation_close_fallback":2}
        try:
            fields["anchor_source_kind"][take]=[source_codes[value] for value in supplement["anchor_source_kind"].to_pylist()]
        except KeyError as exc:
            raise IntegrityError("undeclared exact anchor source kind") from exc
        if not supplement["saved_position_reconciled"].to_numpy(zero_copy_only=False).all():
            raise IntegrityError("saved features were not reconciled against direct anchors")
        for name in ANCHOR_INTEGER_COLUMNS:
            if np.any(supplement[name].is_null().to_numpy(zero_copy_only=False)&identified):
                raise IntegrityError("available exact anchor lacks an exact observation field")
            fields[name][take]=_ints(supplement[name])
        if np.any(identified & ((fields["anchor_end_ns"][take]>fields["origin_ns"][take])
                  | (fields["anchor_known_at_ns"][take]>fields["origin_ns"][take]))):
            raise IntegrityError("exact anchor is not known at receiver creation")
        fields["formation_low_ticks"][take], fields["formation_width_ticks"][take] = low, width
        fields["anchor_identified"][take] = identified
        for j,name in enumerate(added_features,start=len(FEATURES)):
            values=supplement["x_"+name].to_numpy(zero_copy_only=False)
            if np.any(np.isinf(values)) or np.any(np.abs(values[np.isfinite(values)])>np.finfo(np.float32).max):
                raise IntegrityError("supplementary feature is outside finite model representation")
            x[take,j]=values
        offsets.append({"root": shard["root"], "year": shard["year"], "start": start, "rows": n,
                        "paths": shard["tables"]["paths"], "formations": shard["tables"]["formations"],
                        "anchor_supplement": {"table_ref":anchor_ref,"manifest_id":anchor_meta["id"]}})
        start += n
        del table, formation, supplement
    observed = fields["path"] < len(PATH_CLASSES)
    if (np.any(observed & (fields["maturity_at_ns"] < fields["endpoint_ns"]))
            or np.any(observed & (fields["origin_ns"] >= fields["endpoint_ns"]))
            or np.any(observed & (fields["formation_width_ticks"] <= 0))):
        raise IntegrityError("observed target has impossible maturity, horizon or source geometry")
    # Signed future extrema from an available price are the causal statistical
    # zone estimands. Their positive parts retain an explicit no-travel atom.
    valid = observed & fields["anchor_identified"]
    width = fields["formation_width_ticks"]
    if any(np.any(observed & (fields[name] < 0)) for name in
           ("maximum_up_ticks", "maximum_down_ticks", "squared_close_returns_ticks2")):
        raise IntegrityError("nonnegative observed excursion/variation target is negative")
    def exact_difference(a, b, mask):
        positive, negative = np.maximum(b, 0), np.minimum(b, 0)
        safe = (a >= np.iinfo(np.int64).min + positive) & (a <= np.iinfo(np.int64).max + negative)
        if np.any(mask & ~safe):
            raise IntegrityError("exact target difference exceeds the declared int64 domain")
        result = np.zeros(a.shape, dtype=np.int64)
        np.subtract(a, b, out=result, where=mask)
        return result
    def exact_add(a, b, mask):
        safe = (a >= np.iinfo(np.int64).min - np.minimum(b, 0)) & (a <= np.iinfo(np.int64).max - np.maximum(b, 0))
        if np.any(mask & ~safe):
            raise IntegrityError("exact target price exceeds the declared int64 domain")
        result = np.zeros(a.shape, dtype=np.int64)
        np.add(a, b, out=result, where=mask)
        return result
    future_high = exact_add(fields["label_origin_open_ticks"], fields["maximum_up_ticks"], valid)
    future_low = exact_difference(fields["label_origin_open_ticks"], fields["maximum_down_ticks"], valid)
    future_close = exact_add(fields["label_origin_open_ticks"], fields["terminal_ticks"], valid)
    fields["future_high_ticks"] = future_high
    fields["future_low_ticks"] = future_low
    fields["future_close_ticks"] = future_close
    for name, value in (
        ("future_high_from_known_W", exact_difference(future_high, fields["anchor_ticks"], valid)),
        ("future_low_from_known_W", exact_difference(fields["anchor_ticks"], future_low, valid)),
        ("terminal_from_known_W", exact_difference(future_close, fields["anchor_ticks"], valid)),
    ):
        target = np.full(rows, np.nan)
        np.divide(value, width, out=target, where=valid)
        fields[name] = target
    qv = np.full(rows, np.nan)
    np.divide(fields["squared_close_returns_ticks2"], width.astype(np.float64)**2, out=qv, where=observed)
    fields["quadratic_variation_W2"] = qv
    manifest = {"version": "jumbo-prepared-matrix-exact-supplement-v2", "phase": phase, "rows": rows,
                "source_shards": offsets, "feature_columns": anchor_definition["feature_columns"],
                "feature_groups":anchor_definition["feature_groups"],"frozen_source_analysis_id":anchor_definition["frozen_analysis_id"],
                "model_storage": "float32 features with explicit NaN masks; original binary64/exact source fields remain in admitted Parquet",
                "categories": categories, "feature_sha256": hashlib.sha256(x.tobytes()).hexdigest(),
                "field_sha256": {k: hashlib.sha256(v.tobytes()).hexdigest() for k, v in fields.items()},
                "anchor_source_kind_codes":{"0":"formation_unavailable","1":"expected_published_minute","2":"formation_close_fallback"},
                "known_anchor_rule": "Required explicit supplement directly joins expected published canonical minute or verified formation close, with exact raw price and observation/publication times. Saved normalized position/age are reconciliation checks only. No primary float inversion.",
                "unidentified_anchor_observed_rows": int(np.count_nonzero(observed & ~fields["anchor_identified"])),
                "row_identity": "Ordered source Parquet reference plus original row position; original row_id/formation_id remain resolvable without duplicating strings"}
    manifest["id"] = digest(manifest)
    return PreparedPaths(manifest, x, fields, categories, tuple(offsets))


def feature_names(matrix):
    columns = matrix.manifest.get("feature_columns", ["x_" + name for name in FEATURES])
    if (not isinstance(columns, (list, tuple)) or len(columns) != matrix.features.shape[1]
            or any(not isinstance(c, str) or not c.startswith("x_") or len(c) <= 2 for c in columns)
            or len(set(columns)) != len(columns)):
        raise ContractError("declared unique feature schema must match numerical matrix")
    return tuple(c[2:] for c in columns)


def fit_feature_transform(matrix, mask, *, group):
    import numpy as np
    all_names = feature_names(matrix)
    groups = matrix.manifest.get("feature_groups", FEATURE_GROUPS)
    if group not in groups:
        raise ContractError("undeclared available information group")
    names = groups[group]
    if len(set(names)) != len(names) or not set(names) <= set(all_names):
        raise ContractError("information group differs from declared feature schema")
    indices = [all_names.index(n) for n in names]
    values = matrix.features[mask][:, indices].astype(np.float64)
    if not len(values):
        raise ContractError("a training-only feature transform needs observed rows")
    present = np.isfinite(values)
    count = present.sum(axis=0)
    means = np.divide(np.where(present, values, 0).sum(axis=0), count, out=np.zeros(len(indices)), where=count > 0)
    centered = np.where(present, values - means, 0)
    scales = np.sqrt(np.divide((centered**2).sum(axis=0), count, out=np.ones(len(indices)), where=count > 0))
    scales[scales < 1e-12] = 1
    return {"group": group, "names": list(names), "means": means.tolist(), "scales": scales.tolist(),
            "training_rows": int(mask.sum()), "training_last_date": int(matrix.fields["date"][mask].max()),
            "matrix_id": matrix.manifest["id"], "missingness": "Separate indicator per feature; fit-only mean replacement",
            "extra_features": ["log1p_planned_minutes", "root_ES"]}


def transformed_features(matrix, transform, mask=None):
    import numpy as np
    selected = slice(None) if mask is None else mask
    names = feature_names(matrix)
    if not set(transform["names"]) <= set(names):
        raise ContractError("prediction schema lacks a trained feature")
    indices = [names.index(n) for n in transform["names"]]
    raw = matrix.features[selected][:, indices].astype(np.float64)
    missing = ~np.isfinite(raw)
    means, scales = np.asarray(transform["means"]), np.asarray(transform["scales"])
    raw -= means
    raw /= scales
    raw[missing] = 0
    planned = np.log1p(np.maximum(0, matrix.fields["planned_minutes"][selected])).reshape(-1, 1)
    es_code = matrix.categories["root"].index("ES") if "ES" in matrix.categories["root"] else None
    receiver = ((matrix.fields["root"][selected] == es_code) if es_code is not None else np.zeros(len(raw), dtype=bool)).astype(np.float64).reshape(-1, 1)
    return np.column_stack((raw, missing.astype(np.float64), planned, receiver))
