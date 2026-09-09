"""Independent target views for the 22 declared Jumbo special payload clocks.

The common range-path table is useful as a feature source, but it is not a
certificate for any of the source-specific mechanisms.  This adapter reads the
retained JSON payloads, keeps the nominal and availability-delayed branches
separate, and emits target specifications whose classes preserve ambiguity,
censoring, and not-applicable states.

The public entry point is :func:`prepare_special_targets`.  It returns a
``PreparedSpecialTargets`` object which may also be unpacked as
``compactrows, features, targetspecs``.  A feature row is joined by the exact
``(root, date, clock, after_180m)`` identity in ``PreparedPaths``.  Missing
identity is represented by a missing feature row; the adapter never searches a
nearby prefix or future horizon.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence


class SpecialTargetInputError(ValueError):
    """Malformed special source rows or an invalid target join."""


SPECIAL_CLOCK_IDS = (
    "ONS03", "ONS20",
    "magic_00", "magic_01", "magic_02", "magic_06", "magic_07", "magic_08", "magic_23",
    "PIN073_1", "PIN073_2", "PIN073_3", "PIN073_4", "PIN073_5",
    "PIN074_ref_00", "PIN074_ref_01", "PIN074_ref_03", "PIN074_ref_04", "PIN074_ref_07",
    "PIN076_00_08", "PIN076_08_0930", "PIN078_daily_not_combined",
)

MAGIC_CLOCKS = tuple(name for name in SPECIAL_CLOCK_IDS if name.startswith("magic_"))
THREE_STAGE_CLOCKS = tuple(name for name in SPECIAL_CLOCK_IDS if name.startswith("PIN073_"))
OPEN_TO_OPEN_CLOCKS = tuple(
    name for name in SPECIAL_CLOCK_IDS
    if name.startswith("PIN074_") or name.startswith("PIN076_")
)
OVERNIGHT_CLOCKS = ("ONS03", "ONS20")
DAILY_CLOCKS = ("PIN078_daily_not_combined",)
INDEPENDENT_CASE_IDS = tuple(f"SM{at:02d}" for at in range(1, 27))

MECHANISM_BY_CLOCK = {
    **{name: "magic_break_midpoint_competing_extension_v1" for name in MAGIC_CLOCKS},
    **{name: "three_stage_midpoint_return_v1" for name in THREE_STAGE_CLOCKS},
    **{name: "open_to_open_retracement_v1" for name in OPEN_TO_OPEN_CLOCKS},
    **{name: "overnight_pivot_range_v1" for name in OVERNIGHT_CLOCKS},
    "PIN078_daily_not_combined": "source_mon_tue_daily_range_v1",
}

MAGIC_STATES = (
    "no_break_by_horizon", "midpoint_before_invalidation",
    "invalidation_before_midpoint", "break_then_neither_by_horizon",
    "competing_order_ambiguous", "first_side_ambiguous", "future_censored",
    "zero_width", "not_applicable",
)
CONTACT_STATES = (
    "no_compatible_reach", "compatible_reach", "definite_print",
    "censored", "not_applicable",
)
# These are the only classes emitted by a model head.  Source rows still
# retain the two observation states below, but they are exclusions from the
# head population rather than market-event classes.
MODEL_CONTACT_STATES = (
    "no_compatible_reach", "compatible_reach", "definite_print",
)
MODEL_MAGIC_STATES = (
    "no_break_by_horizon", "midpoint_before_invalidation",
    "invalidation_before_midpoint", "break_then_neither_by_horizon",
)
STRATA = ("neither", "high_only", "low_only", "both")
STRATUM_STATES = (*STRATA, "censored", "not_applicable")
SOURCE_SIDE_STATES = ("upper", "lower", "ambiguous", "neither", "not_applicable")
TARGET_DIRECTIONS = ("below", "above", "equal", "not_applicable")
MODEL_TARGET_DIRECTIONS = ("below", "above", "equal")
DISPLACEMENT_SIGNS = (-1, 0, 1)
DAILY_LEVELS = ("high", "low", "midpoint", "fib1_actual_30pct", "fib2_actual_70pct")


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise SpecialTargetInputError("special payload contains a non-finite number")
        return value
    # numpy scalar support without importing NumPy in this source reader.
    if hasattr(value, "item"):
        return _jsonable(value.item())
    raise SpecialTargetInputError(f"unsupported special payload value: {type(value).__name__}")


def _canonical(value: Any) -> bytes:
    return json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _as_date(value: Any) -> date:
    if isinstance(value, date) and not hasattr(value, "hour"):
        return value
    if not isinstance(value, str):
        raise SpecialTargetInputError("special row date must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SpecialTargetInputError("special row date must be an ISO date") from exc


def _parse_payload(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        try:
            parsed = json.loads(value, parse_constant=lambda token: (_ for _ in ()).throw(
                SpecialTargetInputError("special payload contains a non-finite JSON constant")))
        except SpecialTargetInputError:
            raise
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise SpecialTargetInputError("special payload is not valid JSON") from exc
    elif isinstance(value, Mapping):
        parsed = dict(value)
    else:
        raise SpecialTargetInputError("special payload must be canonical JSON text or an object")
    if not isinstance(parsed, dict) or not parsed.get("mechanism"):
        raise SpecialTargetInputError("special payload lacks its mechanism identity")
    _canonical(parsed)
    return parsed


def _status(value: Any) -> str | None:
    return value.get("status") if isinstance(value, Mapping) else None


def _causal_branch(outcome: Mapping[str, Any] | None, *, default="not_applicable") -> tuple[bool | None, list[str]]:
    if not isinstance(outcome, Mapping):
        return None, [default]
    status = outcome.get("status")
    if status == "complete":
        return True, []
    if status in {"candidate_available", "formation_unavailable", "reference_open_unavailable",
                  "forecast_open_unavailable", "conditioning_censored", "censored",
                  "no_remaining_horizon", "not_source_weekday"}:
        return False, [str(status)]
    return False, [str(status or default)]


def _contact_state(outcome: Mapping[str, Any] | None) -> str:
    if not isinstance(outcome, Mapping):
        return "not_applicable"
    status = outcome.get("status")
    if status == "complete":
        if outcome.get("definite_print") is True:
            return "definite_print"
        if outcome.get("compatible_reach") is True:
            return "compatible_reach"
        return "no_compatible_reach"
    if status in {"censored", "conditioning_censored"} or outcome.get("state") == "future_censored":
        return "censored"
    if status == "no_remaining_horizon":
        return "not_applicable"
    if status in {"reference_open_unavailable", "forecast_open_unavailable", "not_source_weekday"}:
        return "not_applicable"
    return "censored"


def _allowed_magic(outcome: Mapping[str, Any] | None) -> tuple[str, ...]:
    if not isinstance(outcome, Mapping):
        return ("not_applicable",)
    possible = outcome.get("possible_terminal_states")
    if isinstance(possible, (list, tuple)) and possible:
        values = [str(v) for v in possible]
        state = outcome.get("state")
        if state in {"competing_order_ambiguous", "first_side_ambiguous"}:
            values.append(str(state))
        return tuple(dict.fromkeys(values))
    state = outcome.get("state")
    if state is not None:
        return (str(state),)
    if outcome.get("status") in {"censored", "conditioning_censored"}:
        return ("future_censored",)
    return ("not_applicable",)


def _state_value(outcome: Mapping[str, Any] | None) -> str | None:
    if not isinstance(outcome, Mapping):
        return None
    if outcome.get("state") is not None:
        return str(outcome["state"])
    if outcome.get("status") in {"censored", "conditioning_censored"}:
        return "future_censored"
    if outcome.get("status") == "no_remaining_horizon":
        return "not_applicable"
    return None


def _formation_features(payload: Mapping[str, Any]) -> tuple[float, float, float]:
    formation = payload.get("formation") if isinstance(payload.get("formation"), Mapping) else {}
    expected = formation.get("expected_minutes")
    observed = formation.get("observed_minutes")
    fraction = (float(observed) / float(expected)
                if isinstance(expected, (int, float)) and not isinstance(expected, bool) and expected > 0
                and isinstance(observed, (int, float)) and not isinstance(observed, bool)
                else float("nan"))
    width = formation.get("width_ticks")
    width_value = float(width) if isinstance(width, (int, float)) and not isinstance(width, bool) else float("nan")
    explicit_zero = formation.get("zero_width")
    zero_width = (float(explicit_zero) if type(explicit_zero) is bool else
                  float(width == 0) if width_value == width_value else float("nan"))
    return fraction, width_value, zero_width


def _label_known_at(outcome: Mapping[str, Any] | None, fallback: Any) -> int | None:
    if not isinstance(outcome, Mapping):
        return fallback if type(fallback) is int else None
    candidates = [outcome.get("maturity_at_ns"), outcome.get("known_at_ns"),
                  outcome.get("inputs_known_at_ns"), fallback]
    # Daily source payloads are level maps.  A branch is not model-ready
    # until the latest retained level has reached its own known-at time.
    if not any(key in outcome for key in ("maturity_at_ns", "known_at_ns", "inputs_known_at_ns")):
        for child in outcome.values():
            if isinstance(child, Mapping):
                candidates.extend((child.get("maturity_at_ns"), child.get("known_at_ns"),
                                   child.get("inputs_known_at_ns")))
    values = [value for value in candidates if type(value) is int]
    return max(values) if values else None


def _nominal_origin(payload: Mapping[str, Any]) -> int | None:
    nominal = payload.get("nominal")
    return nominal.get("origin_ns") if isinstance(nominal, Mapping) and type(nominal.get("origin_ns")) is int else None


def _branch_eligibility(payload: Mapping[str, Any], branch: str) -> tuple[bool, list[str]]:
    outcome = payload.get(branch)
    # Daily-range branches are level maps rather than one outcome object.  The
    # formation-level source gate is authoritative; an unavailable weekday or
    # missing formation remains excluded without becoming a zero outcome.
    if payload.get("mechanism") == "source_mon_tue_daily_range_v1" and isinstance(outcome, Mapping):
        if payload.get("candidate_available") is not True:
            return False, [str(payload.get("status") or "candidate_unavailable")]
        complete = [v for v in outcome.values()
                    if isinstance(v, Mapping) and v.get("status") == "complete"]
        reasons = [] if complete else ["censored"]
        if branch == "nominal" and payload.get("nominal_origin_precedes_input_known_at") is True:
            reasons.append("nominal_origin_precedes_input_known_at")
        return (bool(complete) and not reasons, reasons)
    eligible, reasons = _causal_branch(outcome)
    if branch == "nominal":
        if payload.get("nominal_origin_precedes_input_known_at") is True:
            reasons.append("nominal_origin_precedes_input_known_at")
        else:
            origin = _nominal_origin(payload)
            known = payload.get("inputs_known_at_ns")
            if type(origin) is int and type(known) is int and origin < known:
                reasons.append("nominal_origin_precedes_input_known_at")
    if eligible is not True:
        return False, list(dict.fromkeys(reasons))
    if reasons:
        return False, list(dict.fromkeys(reasons))
    return True, list(dict.fromkeys(reasons))


@dataclass(frozen=True)
class SpecialTargetSpec:
    """One source-specific model head and its observation-state contract."""

    target_id: str
    clock: str
    mechanism: str
    branch: str
    field: str
    value_type: str
    classes: tuple[Any, ...] = ()
    optional: bool = False
    zero_atom: bool = False
    horizon_minutes: int | None = None
    source_field: str = ""
    causal_rule: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return _jsonable({
            "target_id": self.target_id, "clock": self.clock, "mechanism": self.mechanism,
            "branch": self.branch, "field": self.field, "value_type": self.value_type,
            "classes": self.classes, "optional": self.optional, "zero_atom": self.zero_atom,
            "horizon_minutes": self.horizon_minutes, "source_field": self.source_field,
            "causal_rule": self.causal_rule, "metadata": self.metadata,
        })


@dataclass
class PreparedSpecialTargets:
    compactrows: tuple[dict[str, Any], ...]
    features: Any
    targetspecs: tuple[SpecialTargetSpec, ...]
    feature_names: tuple[str, ...]
    manifest: dict[str, Any]

    def __iter__(self):
        yield self.compactrows
        yield self.features
        yield self.targetspecs

    def __getitem__(self, key):
        if key == "compactrows":
            return self.compactrows
        if key == "features":
            return self.features
        if key == "targetspecs":
            return self.targetspecs
        if key == "feature_names":
            return self.feature_names
        if key == "manifest":
            return self.manifest
        if isinstance(key, int):
            return (self.compactrows, self.features, self.targetspecs)[key]
        raise KeyError(key)


def _spec(target_id: str, clock: str, branch: str, field_name: str, value_type: str,
          classes: Sequence[Any] = (), *, optional=False, zero_atom=False,
          horizon_minutes=None, source_field="", causal_rule="", **metadata) -> SpecialTargetSpec:
    return SpecialTargetSpec(target_id, clock, MECHANISM_BY_CLOCK[clock], branch, field_name,
                             value_type, tuple(classes), optional, zero_atom, horizon_minutes,
                             source_field, causal_rule, metadata)


def _target_specs() -> tuple[SpecialTargetSpec, ...]:
    specs: list[SpecialTargetSpec] = []
    for clock in MAGIC_CLOCKS:
        for branch in ("nominal", "availability_delayed"):
            specs.append(_spec(f"{clock}.{branch}.state", clock, branch, f"{branch}_state", "categorical",
                               MODEL_MAGIC_STATES, source_field=f"payload.{branch}.state",
                               causal_rule="Complete source outcomes only; ambiguity, censoring and unavailability remain excluded source states.",
                               retained_observation_states=("competing_order_ambiguous", "first_side_ambiguous", "future_censored", "zero_width", "not_applicable")))
            specs.append(_spec(f"{clock}.{branch}.raw_source_state", clock, branch, f"{branch}_raw_source_state", "categorical",
                               MODEL_MAGIC_STATES, optional=True, source_field=f"payload.{branch}.source_branch_priority_comparator.state",
                               causal_rule="Optional descriptive comparator; never replaces the conservative possible-state head.",
                               retained_observation_states=("competing_order_ambiguous", "first_side_ambiguous", "future_censored", "zero_width", "not_applicable")))
        specs.append(_spec(f"{clock}.nominal.possible_states", clock, "nominal", "nominal_allowed_states", "set_categorical",
                           MODEL_MAGIC_STATES, source_field="payload.nominal.possible_terminal_states", allow_union=True,
                           retained_observation_states=("competing_order_ambiguous", "first_side_ambiguous", "future_censored", "zero_width", "not_applicable")))
        specs.append(_spec(f"{clock}.availability_delayed.possible_states", clock, "availability_delayed", "availability_delayed_allowed_states", "set_categorical",
                           MODEL_MAGIC_STATES, source_field="payload.availability_delayed.possible_terminal_states", allow_union=True,
                           retained_observation_states=("competing_order_ambiguous", "first_side_ambiguous", "future_censored", "zero_width", "not_applicable")))
    for clock in THREE_STAGE_CLOCKS:
        specs.append(_spec(f"{clock}.conditioning.stratum", clock, "conditioning", "conditioning_stratum", "categorical",
                           STRATA, source_field="payload.conditioning.stratum",
                           causal_rule="Formation-time feature only; it is not a fitted future head. Both belongs to both marginal denominators but remains one date.",
                           model_head=False, retained_observation_states=("censored", "not_applicable")))
        for branch in ("nominal", "availability_delayed"):
            specs.append(_spec(f"{clock}.{branch}.eq_intersection", clock, branch, f"{branch}_eq_intersection", "categorical",
                               MODEL_CONTACT_STATES, source_field=f"payload.{branch}.compatible_reach/definite_print",
                               causal_rule="Straddle reach and definite OHLC print are separate; censoring is not a negative.",
                               retained_observation_states=("censored", "not_applicable")))
            specs.append(_spec(f"{clock}.{branch}.true_event_set", clock, branch, f"{branch}_true_event_set", "set_categorical",
                               (False, True), source_field=f"payload.{branch}.compatible_reach/definite_print",
                               causal_rule="Compatible reach is an allowed true-event set; censoring is not a false event.",
                               retained_observation_states=("censored", "not_applicable")))
            specs.append(_spec(f"{clock}.{branch}.stratum_eq_intersection", clock, branch, f"{branch}_stratum_eq_intersection", "categorical",
                               tuple(f"{stratum}|{contact}" for stratum in STRATA for contact in MODEL_CONTACT_STATES),
                               source_field="payload.conditioning.stratum + payload.<branch>",
                               causal_rule="Four conditioning strata crossed with the delayed/nominal EQ observation state; censored/not-applicable rows remain excluded.",
                               model_head=False, measurement=True, feature_role="conditioning_feature",
                               retained_observation_states=("censored", "not_applicable")))
    for clock in OPEN_TO_OPEN_CLOCKS:
        for branch in ("nominal", "availability_delayed"):
            specs.append(_spec(f"{clock}.{branch}.eq_intersection", clock, branch, f"{branch}_eq_intersection", "categorical",
                               MODEL_CONTACT_STATES, source_field=f"payload.{branch}.compatible_reach/definite_print",
                               retained_observation_states=("censored", "not_applicable")))
            specs.append(_spec(f"{clock}.{branch}.true_event_set", clock, branch, f"{branch}_true_event_set", "set_categorical",
                               (False, True), source_field=f"payload.{branch}.compatible_reach/definite_print",
                               causal_rule="Compatible reach is an allowed true-event set; censoring is not a false event.",
                               retained_observation_states=("censored", "not_applicable")))
        specs.append(_spec(f"{clock}.nominal.zero_displacement", clock, "nominal", "zero_displacement", "binary",
                           (False, True), zero_atom=True, source_field="payload.zero_displacement",
                           causal_rule="Formation/open geometry is retained as a measured input known at its source cut; it is not a future model head.",
                           model_head=False, measurement=True, feature_role="known_open_geometry",
                           known_at_source="inputs_known_at_ns"))
        specs.append(_spec(f"{clock}.nominal.displacement_sign", clock, "nominal", "displacement_sign", "categorical",
                           DISPLACEMENT_SIGNS, zero_atom=True, source_field="payload.displacement_sign",
                           model_head=False, measurement=True, feature_role="known_open_geometry",
                           known_at_source="inputs_known_at_ns"))
        specs.append(_spec(f"{clock}.nominal.target_direction", clock, "nominal", "target_direction_from_forecast", "categorical",
                           MODEL_TARGET_DIRECTIONS, source_field="payload.target_direction_from_forecast",
                           retained_observation_states=("not_applicable",), model_head=False, measurement=True,
                           feature_role="known_open_geometry", known_at_source="inputs_known_at_ns"))
        specs.append(_spec(f"{clock}.availability_delayed.zero_displacement", clock, "availability_delayed", "zero_displacement", "binary",
                           (False, True), zero_atom=True, source_field="payload.zero_displacement",
                           model_head=False, measurement=True, feature_role="known_open_geometry",
                           known_at_source="inputs_known_at_ns"))
        specs.append(_spec(f"{clock}.availability_delayed.displacement_sign", clock, "availability_delayed", "displacement_sign", "categorical",
                           DISPLACEMENT_SIGNS, zero_atom=True, source_field="payload.displacement_sign",
                           model_head=False, measurement=True, feature_role="known_open_geometry",
                           known_at_source="inputs_known_at_ns"))
        specs.append(_spec(f"{clock}.availability_delayed.target_direction", clock, "availability_delayed", "target_direction_from_forecast", "categorical",
                           MODEL_TARGET_DIRECTIONS, source_field="payload.target_direction_from_forecast",
                           retained_observation_states=("not_applicable",), model_head=False, measurement=True,
                           feature_role="known_open_geometry", known_at_source="inputs_known_at_ns"))
    for clock in DAILY_CLOCKS:
        for branch in ("nominal", "availability_delayed"):
            for level in DAILY_LEVELS:
                for contact in ("compatible_reach", "definite_print"):
                    specs.append(_spec(f"{clock}.{branch}.{level}.{contact}", clock, branch,
                                   f"{branch}_{level}_{contact}", "binary", (False, True),
                                   horizon_minutes=180, source_field=f"payload.{branch}.{level}.{contact}",
                                   causal_rule="Retained source level measurement used to form the declared intersections; it is not a separate fitted head.",
                                   model_head=False))
            for side in ("upper", "lower", "both"):
                specs.append(_spec(f"{clock}.{branch}.{side}_intersection_180m", clock, branch,
                                   f"{branch}_{side}_intersection_180m", "binary", (False, True),
                                   horizon_minutes=180, source_field="payload.<branch>.high/low.compatible_reach",
                                   causal_rule="Upper/lower/both are intersections of the distinct daily range levels.",
                                   aggregation="unique_date_rate_and_repeated_bar_share"))
                specs.append(_spec(f"{clock}.{branch}.{side}_daily_rate", clock, branch,
                                   f"{branch}_{side}_intersection_180m", "binary", (False, True),
                                   horizon_minutes=180, source_field="payload.<branch>.high/low.compatible_reach",
                                   causal_rule="Aggregate this per-date indicator once per formation date; never weight repeated bars.",
                                   aggregation="unique_date_rate"))
    for clock in OVERNIGHT_CLOCKS:
        specs.append(_spec(f"{clock}.formation.midpoint", clock, "formation", "midpoint", "exact_rational",
                           source_field="payload.midpoint", causal_rule="Ordinary wick midpoint only; no classical pivot formula; retained as a formation measurement.",
                           model_head=False, measurement=True, feature_role="formation_measurement",
                           known_at_source="inputs_known_at_ns"))
        specs.append(_spec(f"{clock}.formation.zero_width", clock, "formation", "zero_width", "binary",
                           (False, True), zero_atom=True, source_field="payload.zero_width",
                           model_head=False, measurement=True, feature_role="formation_measurement",
                           known_at_source="inputs_known_at_ns"))
    return tuple(specs)


def _rows_from_shard(store: Any, shard: Mapping[str, Any]) -> list[dict[str, Any]]:
    direct = shard.get("special_rows")
    if direct is not None:
        if not isinstance(direct, (list, tuple)):
            raise SpecialTargetInputError("special_rows must be a sequence")
        return [dict(row) for row in direct]
    tables = shard.get("tables")
    ref = tables.get("specials") if isinstance(tables, Mapping) else None
    if ref is None:
        raise SpecialTargetInputError("shard lacks its specials table reference")
    if store is None or not hasattr(store, "read"):
        raise SpecialTargetInputError("an artifact store is required for specials table references")
    raw_ref = ref
    try:
        from trading_research.operations.artifacts import artifact_ref
        raw_ref = artifact_ref({k: ref[k] for k in ("sha256", "size_bytes", "kind")})
    except Exception:
        raw_ref = ref
    raw = store.read(raw_ref)
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
        table = pq.read_table(pa.BufferReader(raw))
        if "rows" in ref and table.num_rows != int(ref["rows"]):
            raise SpecialTargetInputError("specials artifact row count changed")
        if ref.get("schema_sha256"):
            schema_hash = hashlib.sha256(table.schema.serialize().to_pybytes()).hexdigest()
            if schema_hash != ref["schema_sha256"]:
                raise SpecialTargetInputError("specials artifact schema changed")
        return [dict(row) for row in table.to_pylist()]
    except SpecialTargetInputError:
        raise
    except Exception as exc:
        raise SpecialTargetInputError("specials artifact is not readable Parquet") from exc


def _path_view(path_matrix: Any) -> tuple[Any, dict[str, Any], tuple[str, ...]]:
    if path_matrix is None:
        raise SpecialTargetInputError("PreparedPaths is required for causal special feature joins")
    if isinstance(path_matrix, Mapping):
        fields = path_matrix.get("fields")
        categories = path_matrix.get("categories", {})
        values = path_matrix.get("features")
        manifest = path_matrix.get("manifest", {})
    else:
        fields = getattr(path_matrix, "fields", None)
        categories = getattr(path_matrix, "categories", {})
        values = getattr(path_matrix, "features", None)
        manifest = getattr(path_matrix, "manifest", {})
    if not isinstance(fields, Mapping) or values is None:
        raise SpecialTargetInputError("path matrix must expose fields, categories, and features")
    try:
        import numpy as np
        features = np.asarray(values, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise SpecialTargetInputError("path feature matrix is not numeric") from exc
    if features.ndim != 2 or not np.isfinite(features).all() and not np.isnan(features).all():
        # NaNs are the declared missing-feature mask; infinities are never valid.
        if features.ndim != 2 or np.isinf(features).any():
            raise SpecialTargetInputError("path features contain an invalid shape or infinity")
    if len(features) != len(next(iter(fields.values()))):
        raise SpecialTargetInputError("path matrix fields and features are not row aligned")
    names = tuple(manifest.get("feature_columns", ()))
    if not names:
        names = tuple(f"x_{at}" for at in range(features.shape[1]))
    if len(names) != features.shape[1]:
        raise SpecialTargetInputError("path feature names do not match feature columns")
    return features, dict(fields), {str(k): tuple(v) for k, v in dict(categories).items()}


def _code(value: Any, categories: Sequence[Any], *, name: str) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and 0 <= value < len(categories):
        return value
    try:
        return categories.index(value)
    except ValueError:
        raise SpecialTargetInputError(f"unknown {name} category in path matrix") from None


def _path_features(path_matrix: Any, rows: Sequence[Mapping[str, Any]]) -> tuple[Any, tuple[str, ...], list[dict[str, Any]]]:
    import numpy as np
    values, fields, categories = _path_view(path_matrix)
    roots = tuple(categories.get("root", ("NQ", "ES")))
    clocks = tuple(categories.get("clock", SPECIAL_CLOCK_IDS))
    horizons = tuple(categories.get("horizon", ("after_180m",)))
    if "date" not in fields or "root" not in fields or "clock" not in fields or "horizon" not in fields:
        raise SpecialTargetInputError("path matrix lacks exact date/root/clock/horizon identity fields")
    dates = fields["date"]
    feature_names = tuple(_path_view(path_matrix)[2].get("feature_columns", ()))
    # _path_view returns categories, not manifest; feature names are recovered
    # below from the path object/mapping without reading any future labels.
    if isinstance(path_matrix, Mapping):
        feature_names = tuple(path_matrix.get("manifest", {}).get("feature_columns", ()))
    else:
        feature_names = tuple(getattr(path_matrix, "manifest", {}).get("feature_columns", ()))
    if not feature_names:
        feature_names = tuple(f"x_{at}" for at in range(values.shape[1]))
    date_values = [int(v) for v in dates]
    index: dict[tuple[str, int, str], int] = {}
    for at in range(len(values)):
        try:
            key = (roots[int(fields["root"][at])], date_values[at], clocks[int(fields["clock"][at])])
            horizon = horizons[int(fields["horizon"][at])]
        except (IndexError, TypeError, ValueError) as exc:
            raise SpecialTargetInputError("path matrix category code is invalid") from exc
        if horizon != "after_180m":
            continue
        if key in index:
            raise SpecialTargetInputError("duplicate exact after_180m path feature identity")
        index[key] = at
    output = np.full((len(rows), values.shape[1] + 3), np.nan, dtype=np.float64)
    joins: list[dict[str, Any]] = []
    for row_at, row in enumerate(rows):
        day = _as_date(row["date"])
        key = (str(row["root"]), day.toordinal(), str(row["clock"]))
        at = index.get(key)
        if at is None:
            joins.append({"status": "missing_exact_after_180m", "path_row_index": None,
                          "feature_origin_ns": None, "feature_available_at_ns": None})
            continue
        output[row_at, :values.shape[1]] = values[at]
        origin = fields.get("origin_ns")
        # Label maturity is not feature availability. These features were
        # formed at the declared cut and exact anchor publication, if present.
        feature_known = [int(fields[name][at]) for name in
                         ("origin_ns", "anchor_known_at_ns", "anchor_observation_known_at_ns")
                         if name in fields and int(fields[name][at]) >= 0]
        joins.append({"status": "joined_exact_after_180m", "path_row_index": at,
                      "feature_origin_ns": None if origin is None else int(origin[at]),
                      "feature_available_at_ns": max(feature_known) if feature_known else None})
    # These three fields are formation facts, available at the source clock's
    # input cut.  They are not copied from any future path outcome.
    for row_at, row in enumerate(rows):
        fraction, width, zero_width = _formation_features(row["payload"])
        output[row_at, -3:] = (fraction, width, zero_width)
    return output, (*feature_names, "x_special_formation_observed_fraction",
                    "x_special_formation_width_ticks", "x_special_formation_zero_width"), joins


def _path_population(path_matrix: Any) -> set[tuple[str, str]]:
    """Return observed root/date identities from the prepared matrix only."""
    values, fields, categories = _path_view(path_matrix)
    roots = tuple(categories.get("root", ("NQ", "ES")))
    if "date" not in fields or "root" not in fields:
        raise SpecialTargetInputError("path matrix lacks the special date/root population")
    result = set()
    try:
        for at in range(len(values)):
            result.add((roots[int(fields["root"][at])], date.fromordinal(int(fields["date"][at])).isoformat()))
    except (IndexError, TypeError, ValueError) as exc:
        raise SpecialTargetInputError("path matrix contains an invalid date/root population") from exc
    return result


def _rational_fields(value: Any, prefix: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {prefix + "_numerator": None, prefix + "_denominator": None}
    numerator, denominator = value.get("numerator"), value.get("denominator")
    if type(numerator) is not int or type(denominator) is not int or denominator <= 0:
        raise SpecialTargetInputError(f"{prefix} must retain an exact rational numerator/denominator")
    return {prefix + "_numerator": numerator, prefix + "_denominator": denominator}


def _compact_row(source: Mapping[str, Any]) -> dict[str, Any]:
    day = _as_date(source.get("date"))
    root, clock = str(source.get("root")), str(source.get("clock"))
    if not root or clock not in SPECIAL_CLOCK_IDS:
        raise SpecialTargetInputError("special row has an undeclared root or clock")
    payload = _parse_payload(source.get("payload"))
    expected = MECHANISM_BY_CLOCK[clock]
    if payload.get("mechanism") != expected:
        raise SpecialTargetInputError(f"{clock} payload mechanism does not match its frozen recipe")
    formation_id = source.get("formation_id")
    if not isinstance(formation_id, str) or not formation_id:
        raise SpecialTargetInputError("special row lacks its formation identity")
    nominal = payload.get("nominal") if isinstance(payload.get("nominal"), Mapping) else None
    delayed = payload.get("availability_delayed") if isinstance(payload.get("availability_delayed"), Mapping) else None
    nominal_eligible, nominal_reasons = _branch_eligibility(payload, "nominal")
    delayed_eligible, delayed_reasons = _branch_eligibility(payload, "availability_delayed")
    horizon = "formation" if clock in OVERNIGHT_CLOCKS else "after_180m"
    planned_minutes = 0 if clock in OVERNIGHT_CLOCKS else 180
    row: dict[str, Any] = {
        "sample_id": _digest(("jumbo-special-target-v1", root, day.isoformat(), clock, formation_id)),
        "date": day.isoformat(), "year": day.year, "root": root, "clock": clock,
        "formation_id": formation_id, "mechanism": expected,
        "horizon": horizon, "planned_minutes": planned_minutes,
        "source_row_index": source.get("_source_row_index"),
        "source_shard": source.get("_source_shard"),
        "source_table_sha256": source.get("_source_table_sha256"),
        "payload_version": payload.get("version"), "payload_digest": _digest(payload),
        "payload": payload, "candidate_available": payload.get("candidate_available") is True,
        "inputs_known_at_ns": payload.get("inputs_known_at_ns"),
        "context_known_at_ns": payload.get("context_known_at_ns"),
        "nominal_status": _status(nominal), "nominal_state": _state_value(nominal),
        "nominal_allowed_states": list(_allowed_magic(nominal)) if clock in MAGIC_CLOCKS else [],
        "availability_delayed_status": _status(delayed), "availability_delayed_state": _state_value(delayed),
        "availability_delayed_allowed_states": list(_allowed_magic(delayed)) if clock in MAGIC_CLOCKS else [],
        "nominal_eligible": nominal_eligible, "availability_delayed_eligible": delayed_eligible,
        "nominal_causal_exclusion_reasons": nominal_reasons,
        "availability_delayed_causal_exclusion_reasons": delayed_reasons,
        "causal_exclusion_reasons": list(dict.fromkeys(nominal_reasons + delayed_reasons)),
        "causal_eligible": bool(nominal_eligible),
    }
    row["nominal_target_known_at_ns"] = _label_known_at(nominal, payload.get("inputs_known_at_ns"))
    row["availability_delayed_target_known_at_ns"] = _label_known_at(delayed, payload.get("inputs_known_at_ns"))
    row["nominal_label_known_at_ns"] = row["nominal_target_known_at_ns"]
    row["availability_delayed_label_known_at_ns"] = row["availability_delayed_target_known_at_ns"]
    row["target_known_at_ns"] = row["nominal_target_known_at_ns"]
    row["label_known_at_ns"] = row["nominal_label_known_at_ns"]
    row.update(_rational_fields(payload.get("target"), "target"))
    fraction, width, zero = _formation_features(payload)
    # NumPy features retain NaN masks, while the compact provenance record
    # keeps missing facts as JSON null. Missing width is not a zero width.
    row.update({"formation_observed_fraction": fraction if fraction == fraction else None,
                "formation_width_ticks": width if width == width else None,
                "formation_zero_width": bool(zero) if zero == zero else None})
    if clock in MAGIC_CLOCKS:
        for branch, outcome in (("nominal", nominal), ("availability_delayed", delayed)):
            if isinstance(outcome, Mapping):
                comparator = outcome.get("source_branch_priority_comparator")
                row[branch + "_raw_source_state"] = comparator.get("state") if isinstance(comparator, Mapping) else None
                row[branch + "_first_side"] = outcome.get("first_side")
                row[branch + "_possible_terminal_states"] = list(outcome.get("possible_terminal_states", ()))
            else:
                row[branch + "_raw_source_state"] = None
                row[branch + "_first_side"] = None
                row[branch + "_possible_terminal_states"] = []
    elif clock in THREE_STAGE_CLOCKS:
        conditioning = payload.get("conditioning") if isinstance(payload.get("conditioning"), Mapping) else {}
        stratum = conditioning.get("stratum")
        condition_state = stratum if stratum in STRATA else "censored" if conditioning.get("status") == "censored" else "not_applicable"
        row["conditioning_stratum"] = condition_state
        for branch, outcome in (("nominal", nominal), ("availability_delayed", delayed)):
            contact = _contact_state(outcome)
            row[branch + "_eq_intersection"] = contact
            row[branch + "_stratum_eq_intersection"] = (
                f"{condition_state}|{contact}" if condition_state in STRATA else condition_state)
    elif clock in OPEN_TO_OPEN_CLOCKS:
        row.update({"zero_displacement": payload.get("zero_displacement"),
                    "displacement_sign": payload.get("displacement_sign"),
                    "target_direction_from_forecast": payload.get("target_direction_from_forecast"),
                    "source_PIN076_stratum": payload.get("source_PIN076_stratum")})
        for branch, outcome in (("nominal", nominal), ("availability_delayed", delayed)):
            row[branch + "_eq_intersection"] = _contact_state(outcome)
    elif clock in DAILY_CLOCKS:
        levels = payload.get("nominal") if isinstance(payload.get("nominal"), Mapping) else {}
        delayed_levels = payload.get("availability_delayed") if isinstance(payload.get("availability_delayed"), Mapping) else {}
        branch_status = "candidate_available" if payload.get("candidate_available") is True else str(payload.get("status") or "candidate_unavailable")
        row["nominal_status"] = branch_status
        row["availability_delayed_status"] = branch_status
        for branch, branch_levels in (("nominal", levels), ("availability_delayed", delayed_levels)):
            for level in DAILY_LEVELS:
                outcome = branch_levels.get(level) if isinstance(branch_levels, Mapping) else None
                row[f"{branch}_{level}_status"] = _status(outcome)
                row[f"{branch}_{level}_contact_state"] = _contact_state(outcome)
                row[f"{branch}_{level}_compatible_reach"] = outcome.get("compatible_reach") if isinstance(outcome, Mapping) else None
                row[f"{branch}_{level}_definite_print"] = outcome.get("definite_print") if isinstance(outcome, Mapping) else None
            upper = row[f"{branch}_high_compatible_reach"] is True
            lower = row[f"{branch}_low_compatible_reach"] is True
            row[f"{branch}_upper_intersection_180m"] = upper
            row[f"{branch}_lower_intersection_180m"] = lower
            row[f"{branch}_both_intersection_180m"] = upper and lower
    elif clock in OVERNIGHT_CLOCKS:
        row.update(_rational_fields(payload.get("midpoint"), "midpoint"))
        row["zero_width"] = payload.get("zero_width")
        row["nominal_status"] = payload.get("status")
        row["nominal_eligible"] = payload.get("candidate_available") is True
        row["causal_eligible"] = row["nominal_eligible"]
        if not row["nominal_eligible"]:
            row["causal_exclusion_reasons"] = list(dict.fromkeys(
                row["causal_exclusion_reasons"] + [str(payload.get("status") or "candidate_unavailable")]))
    row["target_metadata"] = {
        "nominal_origin_precedes_input_known_at": payload.get("nominal_origin_precedes_input_known_at"),
        "source_comparator": payload.get("source_comparator") or payload.get("formula_scope")
                         or payload.get("threshold_scope"),
        "generic_range_path_is_not_source_mechanism": True,
    }
    return row


def _validate_plan(plan: Mapping[str, Any]) -> None:
    if not isinstance(plan, Mapping):
        raise SpecialTargetInputError("frozen Jumbo plan mapping is required")
    declared = tuple(plan.get("expected_special_clock_ids", SPECIAL_CLOCK_IDS))
    if declared != SPECIAL_CLOCK_IDS:
        raise SpecialTargetInputError("frozen plan special-clock population changed")


def prepare_special_targets(store: Any, shards: Sequence[Mapping[str, Any]], *, plan: Mapping[str, Any], path_matrix: Any) -> PreparedSpecialTargets:
    """Read and type the independent special payload population.

    The returned feature matrix contains only exact after-180-minute common
    path features plus three formation facts available at the source input
    cut.  A nominal payload whose origin precedes its full input availability
    remains in ``compactrows`` but is marked ``nominal_eligible=False`` with a
    concrete causal exclusion reason.
    """
    _validate_plan(plan)
    if not isinstance(shards, (list, tuple)) or not shards:
        raise SpecialTargetInputError("nonempty prepared special shard sequence required")
    rows: list[dict[str, Any]] = []
    seen_shards = set()
    for shard in shards:
        if not isinstance(shard, Mapping):
            raise SpecialTargetInputError("special shard must be a mapping")
        root, year = shard.get("root"), shard.get("year")
        if not isinstance(root, str) or not root or type(year) is not int:
            raise SpecialTargetInputError("special shard needs an exact root and integer year")
        if (root, year) in seen_shards:
            raise SpecialTargetInputError("duplicate special source shard")
        seen_shards.add((root, year))
        source_rows = _rows_from_shard(store, shard)
        specials_ref = shard.get("tables", {}).get("specials", {}) if isinstance(shard.get("tables"), Mapping) else {}
        for source_at, source in enumerate(source_rows):
            source["_source_row_index"] = source_at
            source["_source_shard"] = {"root": root, "year": year}
            if isinstance(specials_ref, Mapping):
                source["_source_table_sha256"] = specials_ref.get("sha256")
            if source.get("root") is None:
                source["root"] = root
            if source.get("year") is None:
                source["year"] = year
            if source.get("root") != root:
                raise SpecialTargetInputError("special row root differs from its shard")
            compact = _compact_row(source)
            if compact["year"] != int(source.get("year")):
                raise SpecialTargetInputError("special row year differs from its date")
            if compact["year"] != int(year):
                raise SpecialTargetInputError("special row year differs from its shard")
            rows.append(compact)
    rows.sort(key=lambda row: (row["root"], row["date"], row["clock"], row["formation_id"]))
    identities = [(r["root"], r["date"], r["clock"]) for r in rows]
    if len(set(identities)) != len(identities):
        raise SpecialTargetInputError("duplicate special date/clock/root identity")
    actual_clocks = {r["clock"] for r in rows}
    if actual_clocks != set(SPECIAL_CLOCK_IDS):
        raise SpecialTargetInputError("special source clock population is incomplete or has extras")
    path_population = _path_population(path_matrix)
    expected_pairs = {
        (root, day)
        for root, day in path_population
        if _as_date(day).weekday() in (0, 1)
    }
    for clock in SPECIAL_CLOCK_IDS:
        expected = expected_pairs if clock == "PIN078_daily_not_combined" else path_population
        actual = {(row["root"], row["date"]) for row in rows if row["clock"] == clock}
        if actual != expected:
            raise SpecialTargetInputError(f"special date population changed for {clock}")
    # The path matrix is the authoritative intended date/root population.  It
    # is read only for identity and feature joins; no target column is copied.
    features, feature_names, joins = _path_features(path_matrix, rows)
    for row, join in zip(rows, joins):
        row.update(join)
        row["feature_join_status"] = join["status"]
        if join["status"] != "joined_exact_after_180m":
            row["causal_exclusion_reasons"].append("missing_exact_after_180m_feature_join")
            row["causal_exclusion_reasons"] = list(dict.fromkeys(row["causal_exclusion_reasons"]))
            row["causal_eligible"] = False
        row["feature_join_horizon"] = "after_180m"
        row["feature_source"] = "prepared_paths_exact_root_date_clock_horizon"
        row["row_id"] = _digest((row["sample_id"], row["payload_digest"], join["path_row_index"]))
    targetspecs = _target_specs()
    manifest = {
        "version": "jumbo-special-targets-v1", "rows": len(rows),
        "special_clock_ids": list(SPECIAL_CLOCK_IDS),
        "independent_literal_case_ids": list(INDEPENDENT_CASE_IDS),
        "feature_names": list(feature_names),
        "feature_join": "exact (root,date,clock,after_180m); no nearest future prefix",
        "source_payloads": "distinct retained special JSON payloads; generic range labels never substitute",
        "target_spec_ids": [spec.target_id for spec in targetspecs],
        "row_sha256": _digest(rows), "targetspec_sha256": _digest([spec.as_dict() for spec in targetspecs]),
    }
    return PreparedSpecialTargets(tuple(rows), features, targetspecs, feature_names, manifest)


def compact_special_payload(clock: str, payload: Mapping[str, Any], *, date_value: str = "2024-01-01",
                            root: str = "NQ", formation_id: str = "literal-formation") -> dict[str, Any]:
    """Public arithmetic-free helper for synthetic payload and leakage tests."""
    if clock not in SPECIAL_CLOCK_IDS:
        raise SpecialTargetInputError("unknown frozen special clock")
    return _compact_row({"date": date_value, "year": _as_date(date_value).year,
                         "root": root, "clock": clock, "formation_id": formation_id,
                         "payload": payload})


__all__ = [
    "SPECIAL_CLOCK_IDS", "MAGIC_CLOCKS", "THREE_STAGE_CLOCKS", "OPEN_TO_OPEN_CLOCKS",
    "OVERNIGHT_CLOCKS", "DAILY_CLOCKS", "INDEPENDENT_CASE_IDS", "MECHANISM_BY_CLOCK",
    "MODEL_CONTACT_STATES", "MODEL_MAGIC_STATES", "MODEL_TARGET_DIRECTIONS",
    "SpecialTargetInputError",
    "SpecialTargetSpec", "PreparedSpecialTargets", "prepare_special_targets",
    "compact_special_payload",
]
