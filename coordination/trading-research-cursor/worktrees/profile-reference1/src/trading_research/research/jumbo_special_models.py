"""Model-ready views for the retained Jumbo source-specific mechanisms.

The source payload adapter keeps every special row, including unavailable,
censored, and ambiguous rows.  This module turns those rows into ordinary
``PreparedPaths``/``Target`` pairs without turning observation states into
market-event classes.  A target's eligible mask contains only a legal,
causally known observation; the full ``PreparedPaths`` row population remains
available to evaluation code for intended denominators.

The public entry point is :func:`prepare_special_model_views`.  It returns a
flat mapping whose keys are ``"<mechanism>/<branch>"`` and whose values are
``(PreparedPaths, {target_name: Target})``.  The returned mapping also exposes
``by_mechanism`` for callers that prefer a nested mechanism/branch view.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from fractions import Fraction
import hashlib
import math
from typing import Any, Mapping, Sequence

import numpy as np

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest
from trading_research.research.jumbo_matrix import PreparedPaths
from trading_research.research.jumbo_targets import Target
from trading_research.research.jumbo_special_targets import (
    DAILY_CLOCKS,
    MAGIC_CLOCKS,
    MAGIC_STATES,
    MECHANISM_BY_CLOCK,
    OPEN_TO_OPEN_CLOCKS,
    OVERNIGHT_CLOCKS,
    SPECIAL_CLOCK_IDS,
    STRATA,
    THREE_STAGE_CLOCKS,
    CONTACT_STATES,
    MODEL_TARGET_DIRECTIONS,
)


VERSION = "jumbo-special-model-views-v1"
_CENSOR_STATES = {"censored", "future_censored", "not_applicable", "conditioning_censored"}
_AMBIGUOUS_MAGIC_STATES = {"competing_order_ambiguous", "first_side_ambiguous"}
_MAGIC_EVENT_STATES = (
    "no_break_by_horizon", "midpoint_before_invalidation",
    "invalidation_before_midpoint", "break_then_neither_by_horizon",
)
_CONTACT_POINT_STATES = ("no_compatible_reach", "compatible_reach", "definite_print")
_DIRECTION_CLASSES = MODEL_TARGET_DIRECTIONS
_DAILY_LEVELS = ("high", "low", "midpoint", "fib1_actual_30pct", "fib2_actual_70pct")


class SpecialModelInputError(ContractError):
    """Special rows or matrix identities cannot form a causal model view."""


def _measurement_disposition(view: Any, target: Target) -> dict[str, Any]:
    """Summarize a retained measurement without turning it into a fit head.

    The aligned source-year counts are part of the view contract so a
    measurement-only quantity remains auditable after the model target map is
    filtered by the worker.  Raw values stay in the typed ``Target`` owned by
    the adapter; the disposition is the bounded manifest representation.
    """
    applicable = target.applicable(view)
    values = np.asarray(target.values)[applicable]
    eligible = np.asarray(target.eligible, dtype=bool)[applicable]
    known = np.asarray(target.label_known_at_ns)[applicable]
    if values.ndim == 0 or eligible.ndim != 1 or known.ndim != 1:
        raise SpecialModelInputError("measurement target arrays must retain aligned rows")
    if len(values) != len(eligible) or len(values) != len(known):
        raise SpecialModelInputError("measurement target arrays are not row aligned")
    dates = np.asarray(view.fields.get("date", ()))[applicable]
    if len(dates) != len(values):
        raise SpecialModelInputError("measurement disposition dates are not row aligned")
    rows_by_year: dict[str, int] = {}
    eligible_by_year: dict[str, int] = {}
    known_by_year: dict[str, int] = {}
    for at, ordinal in enumerate(dates):
        try:
            year = str(date.fromordinal(int(ordinal)).year)
        except (TypeError, ValueError, OverflowError) as exc:
            raise SpecialModelInputError("measurement disposition date is invalid") from exc
        rows_by_year[year] = rows_by_year.get(year, 0) + 1
        if bool(eligible[at]):
            eligible_by_year[year] = eligible_by_year.get(year, 0) + 1
        if isinstance(known[at], (int, np.integer)) and int(known[at]) >= 0:
            known_by_year[year] = known_by_year.get(year, 0) + 1
    known_values = known[(known >= 0)] if np.issubdtype(known.dtype, np.number) else np.asarray([], dtype=np.int64)
    return {
        "name": target.name,
        "kind": target.kind,
        "model_head": False,
        "measurement": True,
        "rows": int(len(values)),
        "eligible_rows": int(eligible.sum()),
        "known_rows": int(len(known_values)),
        "rows_by_year": rows_by_year,
        "eligible_rows_by_year": eligible_by_year,
        "known_rows_by_year": known_by_year,
        "known_at_min_ns": int(known_values.min()) if len(known_values) else None,
        "known_at_max_ns": int(known_values.max()) if len(known_values) else None,
        "metadata": dict(target.metadata),
    }


class SpecialModelViews(dict):
    """Flat mechanism/branch mapping with an explicit nested lookup."""

    def __init__(self, domains: Mapping[str, Mapping[str, tuple[PreparedPaths, dict[str, Target]]]]):
        self.by_mechanism = {str(mechanism): dict(branches)
                             for mechanism, branches in domains.items()}
        flat = {f"{mechanism}/{branch}": value
                for mechanism, branches in self.by_mechanism.items()
                for branch, value in branches.items()}
        super().__init__(flat)
        self.model_target_ids = {
            name: tuple(target_name for target_name, target in targets.items()
                       if target.metadata.get("model_head", True))
            for name, (view, targets) in flat.items()
        }
        self.measurement_dispositions = {
            name: {
                target_name: _measurement_disposition(view, target)
                for target_name, target in targets.items()
                if target.metadata.get("model_head", True) is False
            }
            for name, (view, targets) in flat.items()
        }

    def for_mechanism(self, mechanism: str) -> dict[str, tuple[PreparedPaths, dict[str, Target]]]:
        return dict(self.by_mechanism[mechanism])

    def items(self):
        """Iterate only domains that contain at least one future model head.

        Measurement-only domains remain addressable through ``[]`` and are
        retained in ``measurement_dispositions`` for the source report.  The
        worker's fit-domain iterator must not present such a domain as a
        vanished or empty forecast population.
        """
        return ((name, value) for name, value in super().items()
                if self.model_target_ids.get(name))

    def __getitem__(self, key):
        if key in self.by_mechanism:
            return self.by_mechanism[key]
        return super().__getitem__(key)


def _as_date(value: Any) -> date:
    if isinstance(value, date) and not hasattr(value, "hour"):
        return value
    if not isinstance(value, str):
        raise SpecialModelInputError("special model row date must be an ISO date")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SpecialModelInputError("special model row date must be an ISO date") from exc


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, (int, np.integer)) and not isinstance(value, bool) and int(value) >= 0:
        return int(value)
    return None


def _int64(values: Sequence[int | None], *, missing: int = -1) -> np.ndarray:
    output = np.full(len(values), missing, dtype=np.int64)
    for at, value in enumerate(values):
        if value is not None:
            if not isinstance(value, (int, np.integer)) or isinstance(value, bool) or int(value) < 0:
                raise SpecialModelInputError("exact nonnegative timestamp required")
            output[at] = int(value)
    return output


def _row_payload(row: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = row.get("payload")
    if not isinstance(payload, Mapping):
        raise SpecialModelInputError("special model rows must retain parsed payloads")
    return payload


def _rows_from_input(special_rows: Any) -> tuple[dict[str, Any], ...]:
    if hasattr(special_rows, "compactrows"):
        rows = getattr(special_rows, "compactrows")
    elif isinstance(special_rows, Mapping) and "compactrows" in special_rows:
        rows = special_rows["compactrows"]
    else:
        rows = special_rows
    if not isinstance(rows, (list, tuple)) or not rows:
        raise SpecialModelInputError("nonempty compact special-row population required")
    output = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise SpecialModelInputError("special model row must be a mapping")
        if "sample_id" not in row or "clock" not in row or "mechanism" not in row:
            raise SpecialModelInputError("prepare_special_model_views requires compact source rows")
        output.append(dict(row))
    return tuple(output)


def _declared_model_target_ids(special_rows: Any) -> set[str] | None:
    """Return the declared model-head IDs when the compact bundle retains them.

    ``targetspecs`` is optional for callers that already hold compact rows,
    but a complete PreparedSpecialTargets bundle must close every declared
    model head against the actual view. Formation-only conditioning specs are
    marked ``model_head=False`` and intentionally remain features.
    """
    if hasattr(special_rows, "targetspecs"):
        specs = getattr(special_rows, "targetspecs")
    elif isinstance(special_rows, Mapping):
        specs = special_rows.get("targetspecs")
    else:
        specs = None
    if specs is None:
        return None
    if not isinstance(specs, (list, tuple)):
        raise SpecialModelInputError("special targetspecs must be a sequence")
    declared: set[str] = set()
    for spec in specs:
        if hasattr(spec, "target_id"):
            target_id = getattr(spec, "target_id")
            metadata = getattr(spec, "metadata", {})
        elif isinstance(spec, Mapping):
            target_id = spec.get("target_id")
            metadata = spec.get("metadata", {})
        else:
            raise SpecialModelInputError("special targetspec must retain a target_id")
        if not isinstance(target_id, str) or not target_id:
            raise SpecialModelInputError("special targetspec target_id must be nonempty text")
        if not isinstance(metadata, Mapping):
            raise SpecialModelInputError("special targetspec metadata must be a mapping")
        if metadata.get("model_head", True):
            if target_id in declared:
                raise SpecialModelInputError("duplicate declared special model target")
            declared.add(target_id)
    return declared


def _path_view(matrix: Any) -> tuple[np.ndarray, dict[str, Any], dict[str, tuple[Any, ...]], dict[str, Any]]:
    if isinstance(matrix, Mapping):
        features = matrix.get("features")
        fields = matrix.get("fields")
        categories = matrix.get("categories")
        manifest = matrix.get("manifest")
    else:
        features = getattr(matrix, "features", None)
        fields = getattr(matrix, "fields", None)
        categories = getattr(matrix, "categories", None)
        manifest = getattr(matrix, "manifest", None)
    if features is None or not isinstance(fields, Mapping) or not isinstance(categories, Mapping):
        raise SpecialModelInputError("PreparedPaths with features, fields, and categories is required")
    try:
        array = np.asarray(features, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise SpecialModelInputError("prepared path features must be numeric") from exc
    if array.ndim != 2 or np.isinf(array).any():
        raise SpecialModelInputError("prepared path features must be a finite 2-D matrix with NaN masks")
    if "date" not in fields or "root" not in fields or "clock" not in fields or "horizon" not in fields:
        raise SpecialModelInputError("prepared path identity fields are incomplete")
    if any(len(np.asarray(value)) != len(array) for value in fields.values()):
        raise SpecialModelInputError("prepared path fields are not row aligned")
    normalized_categories = {str(key): tuple(value) for key, value in categories.items()}
    return array, dict(fields), normalized_categories, dict(manifest or {})


def _category_code(value: Any, categories: Sequence[Any], name: str) -> int:
    if isinstance(value, (int, np.integer)) and not isinstance(value, bool) and 0 <= int(value) < len(categories):
        return int(value)
    try:
        return int(categories.index(value))
    except ValueError as exc:
        raise SpecialModelInputError(f"unknown {name} category {value!r}") from exc


def _path_index(matrix: Any) -> tuple[dict[tuple[str, int, str], int], tuple[str, ...]]:
    features, fields, categories, manifest = _path_view(matrix)
    roots = tuple(categories.get("root", ()))
    clocks = tuple(categories.get("clock", ()))
    horizons = tuple(categories.get("horizon", ()))
    if not roots or not clocks or not horizons:
        raise SpecialModelInputError("prepared path categories are empty")
    if "after_180m" not in horizons:
        raise SpecialModelInputError("special features require an exact after_180m path horizon")
    names = tuple(manifest.get("feature_columns", ()))
    if len(names) != features.shape[1]:
        names = tuple(f"x_{at}" for at in range(features.shape[1]))
    index: dict[tuple[str, int, str], int] = {}
    for at in range(len(features)):
        root = roots[_category_code(fields["root"][at], roots, "root")]
        clock = clocks[_category_code(fields["clock"][at], clocks, "clock")]
        horizon = horizons[_category_code(fields["horizon"][at], horizons, "horizon")]
        if horizon != "after_180m":
            continue
        key = (str(root), int(fields["date"][at]), str(clock))
        if key in index:
            raise SpecialModelInputError("duplicate exact after_180m path identity")
        index[key] = at
    return index, names


def _feature_known_at(fields: Mapping[str, Any], row_index: int) -> int | None:
    known_values: list[int] = []
    for name in ("anchor_observation_known_at_ns", "anchor_known_at_ns", "origin_ns"):
        values = fields.get(name)
        if values is not None:
            value = values[row_index]
            if isinstance(value, (int, np.integer)) and not isinstance(value, bool) and int(value) >= 0:
                known_values.append(int(value))
    return max(known_values) if known_values else None


def _special_cut(row: Mapping[str, Any], branch: str) -> int | None:
    if branch == "nominal":
        payload = _row_payload(row)
        nominal = payload.get("nominal")
        origin = _int_or_none(nominal.get("origin_ns")) if isinstance(nominal, Mapping) else None
        inputs_known = _int_or_none(row.get("inputs_known_at_ns"))
        if origin is not None:
            # A nominal forecast is legal only when all inputs were known by
            # its actual forecast origin.  Do not let a later publication cut
            # admit features after that forecast was made.
            if inputs_known is not None and inputs_known > origin:
                return None
            return origin
        return inputs_known
    if branch == "availability_delayed":
        payload = _row_payload(row)
        delayed = payload.get("availability_delayed")
        if isinstance(delayed, Mapping):
            delayed_cut = _int_or_none(delayed.get("inputs_known_at_ns"))
            if delayed_cut is not None:
                return delayed_cut
        return _int_or_none(row.get("inputs_known_at_ns"))
    if branch == "conditioning":
        payload = _row_payload(row)
        conditioning = payload.get("conditioning")
        if isinstance(conditioning, Mapping):
            return _int_or_none(conditioning.get("known_at_ns")) or _int_or_none(row.get("inputs_known_at_ns"))
        return _int_or_none(row.get("inputs_known_at_ns"))
    return _int_or_none(row.get("inputs_known_at_ns"))


def _branch_known_at(row: Mapping[str, Any], branch: str) -> int | None:
    if branch == "nominal":
        return _int_or_none(row.get("nominal_target_known_at_ns"))
    if branch == "availability_delayed":
        return _int_or_none(row.get("availability_delayed_target_known_at_ns"))
    if branch == "conditioning":
        payload = _row_payload(row)
        condition = payload.get("conditioning")
        return _int_or_none(condition.get("known_at_ns")) if isinstance(condition, Mapping) else None
    return _int_or_none(row.get("target_known_at_ns"))


def _branch_window(row: Mapping[str, Any], branch: str) -> tuple[int | None, int | None]:
    """Return the complete source window, including daily level maps."""
    payload = _row_payload(row)
    outcome = payload.get(branch)
    mappings = [outcome] if isinstance(outcome, Mapping) else []
    if mappings and not any(key in outcome for key in ("origin_ns", "endpoint_ns")):
        mappings = [value for value in outcome.values() if isinstance(value, Mapping)]
    origins = [_int_or_none(value.get("origin_ns")) for value in mappings]
    endpoints = [_int_or_none(value.get("endpoint_ns")) for value in mappings]
    origins = [value for value in origins if value is not None]
    endpoints = [value for value in endpoints if value is not None]
    return (min(origins) if origins else None, max(endpoints) if endpoints else None)


def _row_clock_code(row: Mapping[str, Any], clocks: tuple[str, ...]) -> int:
    try:
        return clocks.index(str(row["clock"]))
    except ValueError as exc:
        raise SpecialModelInputError("special row clock is outside the frozen path view") from exc


def _state_code(value: Any, classes: Sequence[Any]) -> int | None:
    try:
        return classes.index(value)
    except ValueError:
        return None


def _point_target(name: str, values: np.ndarray, eligible: np.ndarray, known: np.ndarray,
                  *, classes: Sequence[Any], metadata: Mapping[str, Any]) -> Target:
    return Target(name, "categorical", values.astype(np.int64), eligible.astype(bool), known.astype(np.int64),
                  {"classes": list(classes), **dict(metadata)})


def _set_target(name: str, values: np.ndarray, eligible: np.ndarray, known: np.ndarray,
                *, classes: Sequence[Any], metadata: Mapping[str, Any]) -> Target:
    return Target(name, "interval_categorical", values.astype(bool), eligible.astype(bool), known.astype(np.int64),
                  {"classes": list(classes), **dict(metadata)})


def _continuous_target(name: str, values: np.ndarray, eligible: np.ndarray, known: np.ndarray,
                       *, metadata: Mapping[str, Any]) -> Target:
    return Target(name, "continuous", values.astype(np.float64), eligible.astype(bool), known.astype(np.int64),
                  dict(metadata))


def _base_metadata(row: Mapping[str, Any], *, mechanism: str, branch: str, field: str,
                   source_field: str, matrix_id: str) -> dict[str, Any]:
    return {
        "target": field, "mechanism": mechanism, "branch": branch,
        "source_field": source_field, "source_matrix": matrix_id,
        "observation_rule": "censoring/unavailability excluded from target classes and retained in intended rows",
        "definition": "independent retained source payload; generic range/path labels are not substitutes",
        "id": digest({"target": field, "mechanism": mechanism, "branch": branch,
                      "source_field": source_field}),
    }


def _magic_targets(rows, clock: str, branch: str, *, matrix_id: str, row_clock: np.ndarray,
                   known: np.ndarray, legal: np.ndarray) -> dict[str, Target]:
    classes = _MAGIC_EVENT_STATES
    point = np.full(len(rows), -1, dtype=np.int64)
    compatible = np.zeros((len(rows), len(classes)), dtype=bool)
    raw_point = np.full(len(rows), -1, dtype=np.int64)
    raw_classes = classes
    raw_compatible = np.zeros((len(rows), len(raw_classes)), dtype=bool)
    eligible_point = np.zeros(len(rows), dtype=bool)
    eligible_set = np.zeros(len(rows), dtype=bool)
    eligible_raw = np.zeros(len(rows), dtype=bool)
    for at, row in enumerate(rows):
        if row_clock[at] != clock:
            continue
        outcome = _row_payload(row).get(branch)
        state = row.get(f"{branch}_state")
        possible = tuple(str(value) for value in row.get(f"{branch}_possible_terminal_states", ()))
        if row.get(f"{branch}_status") == "complete" and legal[at]:
            allowed = tuple(value for value in possible if value in classes)
            if not allowed and state in classes:
                allowed = (state,)
            for value in allowed:
                compatible[at, classes.index(value)] = True
            eligible_set[at] = bool(allowed)
            if len(allowed) == 1:
                point[at] = classes.index(allowed[0])
                eligible_point[at] = True
        raw = row.get(f"{branch}_raw_source_state")
        if raw in raw_classes and row.get(f"{branch}_status") == "complete" and legal[at]:
            raw_point[at] = raw_classes.index(raw)
            raw_compatible[at, raw_point[at]] = True
            eligible_raw[at] = True
        # Keep the payload access explicit so future source schema changes
        # cannot silently turn a missing outcome into a negative label.
        if outcome is not None and not isinstance(outcome, Mapping):
            raise SpecialModelInputError("magic branch outcome must be an object")
    common = {"mechanism": MECHANISM_BY_CLOCK[clock], "branch": branch,
              "clock": clock, "classes_exclude_censoring": True}
    return {
        f"{clock}.{branch}.state": _point_target(
            f"{clock}.{branch}.state", point, eligible_point, known,
            classes=classes, metadata=_base_metadata(rows[0], mechanism=MECHANISM_BY_CLOCK[clock],
                                                     branch=branch, field=f"{clock}.{branch}.state",
                                                     source_field=f"payload.{branch}.state", matrix_id=matrix_id) | common),
        f"{clock}.{branch}.possible_states": _set_target(
            f"{clock}.{branch}.possible_states", compatible, eligible_set, known,
            classes=classes, metadata=_base_metadata(rows[0], mechanism=MECHANISM_BY_CLOCK[clock],
                                                     branch=branch, field=f"{clock}.{branch}.possible_states",
                                                     source_field=f"payload.{branch}.possible_terminal_states", matrix_id=matrix_id) | common),
        f"{clock}.{branch}.raw_source_state": _point_target(
            f"{clock}.{branch}.raw_source_state", raw_point, eligible_raw, known,
            classes=raw_classes, metadata=_base_metadata(rows[0], mechanism=MECHANISM_BY_CLOCK[clock],
                                                         branch=branch, field=f"{clock}.{branch}.raw_source_state",
                                                         source_field=f"payload.{branch}.source_branch_priority_comparator.state", matrix_id=matrix_id) | common),
    }


def _contact_targets(rows, clock: str, branch: str, *, mechanism: str, row_clock: np.ndarray,
                     known: np.ndarray, legal: np.ndarray, matrix_id: str, include_stratum: bool = False) -> dict[str, Target]:
    point = np.full(len(rows), -1, dtype=np.int64)
    event_set = np.zeros((len(rows), 2), dtype=bool)
    stratum_classes = tuple(f"{stratum}|{contact}" for stratum in STRATA for contact in _CONTACT_POINT_STATES)
    stratum_values = np.full(len(rows), -1, dtype=np.int64)
    eligible = np.zeros(len(rows), dtype=bool)
    eligible_set = np.zeros(len(rows), dtype=bool)
    eligible_stratum = np.zeros(len(rows), dtype=bool)
    for at, row in enumerate(rows):
        if row_clock[at] != clock or not legal[at]:
            continue
        contact = row.get(f"{branch}_eq_intersection")
        if contact not in _CONTACT_POINT_STATES:
            continue
        point[at] = _CONTACT_POINT_STATES.index(contact)
        eligible[at] = True
        if contact == "no_compatible_reach":
            event_set[at, 0] = True
        elif contact == "compatible_reach":
            # A compatible intersection is an interval observation: both a
            # true and a false definite-print event remain possible.
            event_set[at, :] = True
        else:
            event_set[at, 1] = True
        eligible_set[at] = True
        if include_stratum:
            stratum = row.get("conditioning_stratum")
            if stratum in STRATA:
                stratum_values[at] = stratum_classes.index(f"{stratum}|{contact}")
                eligible_stratum[at] = True
    common = {"mechanism": mechanism, "branch": branch, "clock": clock,
              "classes_exclude_censoring": True}
    output = {
        f"{clock}.{branch}.eq_intersection": _point_target(
            f"{clock}.{branch}.eq_intersection", point, eligible, known,
            classes=_CONTACT_POINT_STATES, metadata=_base_metadata(rows[0], mechanism=mechanism,
                branch=branch, field=f"{clock}.{branch}.eq_intersection",
                source_field=f"payload.{branch}.compatible_reach/definite_print", matrix_id=matrix_id) | common),
        f"{clock}.{branch}.true_event_set": _set_target(
            f"{clock}.{branch}.true_event_set", event_set, eligible_set, known,
            classes=(False, True), metadata=_base_metadata(rows[0], mechanism=mechanism,
                branch=branch, field=f"{clock}.{branch}.true_event_set",
                source_field=f"payload.{branch}.compatible_reach/definite_print", matrix_id=matrix_id) | {
                    **common, "observation": "compatible true-event set; censoring is excluded"}),
    }
    if include_stratum:
        output[f"{clock}.{branch}.stratum_eq_intersection"] = _point_target(
            f"{clock}.{branch}.stratum_eq_intersection", stratum_values, eligible_stratum, known,
            classes=stratum_classes, metadata=_base_metadata(
                rows[0], mechanism=mechanism, branch=branch,
                field=f"{clock}.{branch}.stratum_eq_intersection",
                source_field="payload.conditioning.stratum + payload.<branch>",
                matrix_id=matrix_id) | {
                    **common,
                    "conditioning_feature": "four source strata retained as a causal input feature",
                    "conditioning_strata": list(STRATA),
                    "classes": list(stratum_classes),
                    "model_head": False,
                    "measurement": True,
                    "feature_role": "conditioning_interaction_measurement",
                })
    return output
    

def _three_stage_targets(rows, clock: str, branch: str, *, row_clock, known, legal, matrix_id) -> dict[str, Target]:
    output = _contact_targets(rows, clock, branch, mechanism=MECHANISM_BY_CLOCK[clock], row_clock=row_clock,
                              known=known, legal=legal, matrix_id=matrix_id, include_stratum=True)
    values = np.full(len(rows), -1, dtype=np.int64)
    eligible = np.zeros(len(rows), dtype=bool)
    measurement_known = np.full(len(rows), -1, dtype=np.int64)
    for at, row in enumerate(rows):
        if row_clock[at] != clock:
            continue
        conditioning = _row_payload(row).get("conditioning")
        stratum = row.get("conditioning_stratum")
        source_known = (_int_or_none(conditioning.get("known_at_ns"))
                        if isinstance(conditioning, Mapping) else None)
        cut = _special_cut(row, branch)
        if (stratum in STRATA and source_known is not None and cut is not None
                and source_known <= cut):
            values[at] = STRATA.index(stratum)
            eligible[at] = True
            measurement_known[at] = source_known
    name = f"{clock}.conditioning.stratum"
    output[name] = _point_target(
        name, values, eligible, measurement_known, classes=STRATA,
        metadata=_base_metadata(rows[0], mechanism=MECHANISM_BY_CLOCK[clock], branch="conditioning",
            field=name, source_field="payload.conditioning.stratum", matrix_id=matrix_id) | {
                "model_head": False, "measurement": True,
                "feature_role": "conditioning_feature",
                "known_at_source": "payload.conditioning.known_at_ns",
                "known_cut_rule": "conditioning known_at_ns <= branch forecast cut",
            })
    return output


def _open_targets(rows, clock: str, branch: str, *, row_clock, known, legal, matrix_id) -> dict[str, Target]:
    output = _contact_targets(rows, clock, branch, mechanism=MECHANISM_BY_CLOCK[clock], row_clock=row_clock,
                              known=known, legal=legal, matrix_id=matrix_id)
    sign = np.full(len(rows), -1, dtype=np.int64)
    direction = np.full(len(rows), -1, dtype=np.int64)
    zero = np.zeros(len(rows), dtype=np.int64)
    sign_ok = np.zeros(len(rows), dtype=bool)
    direction_ok = np.zeros(len(rows), dtype=bool)
    zero_ok = np.zeros(len(rows), dtype=bool)
    measurement_known = np.full(len(rows), -1, dtype=np.int64)
    for at, row in enumerate(rows):
        if row_clock[at] != clock:
            continue
        cut = _special_cut(row, branch)
        source_known = _int_or_none(row.get("inputs_known_at_ns"))
        # These fields are source geometry.  They may be used only when the
        # source publication is known by the forecast's branch cut; outcome
        # maturity and contact eligibility do not make a known measurement a
        # future label.
        measurement_ok = (row.get("candidate_available") is True
                          and source_known is not None and cut is not None
                          and source_known <= cut)
        if measurement_ok:
            measurement_known[at] = source_known
        if not measurement_ok:
            continue
        value = row.get("displacement_sign")
        if type(value) is int and value in (-1, 0, 1):
            sign[at] = (-1, 0, 1).index(value)
            sign_ok[at] = True
        value = row.get("target_direction_from_forecast")
        if value in _DIRECTION_CLASSES:
            direction[at] = _DIRECTION_CLASSES.index(value)
            direction_ok[at] = True
        if type(row.get("zero_displacement")) is bool:
            zero[at] = int(row["zero_displacement"])
            zero_ok[at] = True
    common = {"mechanism": MECHANISM_BY_CLOCK[clock], "branch": branch, "clock": clock,
              "forecast_open_availability_required": True, "classes_exclude_censoring": True}
    measurement_metadata = {
        "model_head": False, "measurement": True,
        "feature_role": "known_open_geometry",
        "known_at_source": "inputs_known_at_ns",
        "known_cut_rule": "source inputs_known_at_ns <= branch forecast cut",
    }
    output[f"{clock}.{branch}.displacement_sign"] = _point_target(
        f"{clock}.{branch}.displacement_sign", sign, sign_ok, measurement_known,
        classes=(-1, 0, 1), metadata=_base_metadata(rows[0], mechanism=MECHANISM_BY_CLOCK[clock],
            branch=branch, field=f"{clock}.{branch}.displacement_sign",
            source_field="payload.displacement_sign", matrix_id=matrix_id) | common | measurement_metadata)
    output[f"{clock}.{branch}.target_direction"] = _point_target(
        f"{clock}.{branch}.target_direction", direction, direction_ok, measurement_known,
        classes=_DIRECTION_CLASSES, metadata=_base_metadata(rows[0], mechanism=MECHANISM_BY_CLOCK[clock],
            branch=branch, field=f"{clock}.{branch}.target_direction_from_forecast",
            source_field="payload.target_direction_from_forecast", matrix_id=matrix_id) | common | measurement_metadata)
    output[f"{clock}.{branch}.zero_displacement"] = _point_target(
        f"{clock}.{branch}.zero_displacement", zero, zero_ok, measurement_known,
        classes=(False, True), metadata=_base_metadata(rows[0], mechanism=MECHANISM_BY_CLOCK[clock],
            branch=branch, field=f"{clock}.{branch}.zero_displacement",
            source_field="payload.zero_displacement", matrix_id=matrix_id) | (common | {"zero_atom": True}) | measurement_metadata)
    return output


def _daily_targets(rows, clock: str, branch: str, *, row_clock, known, legal, matrix_id) -> dict[str, Target]:
    output = {}
    mechanism = MECHANISM_BY_CLOCK[clock]
    for level in _DAILY_LEVELS:
        for outcome_name, source_name in (("compatible_reach", "compatible_reach"), ("definite_print", "definite_print")):
            values = np.zeros(len(rows), dtype=np.int64)
            eligible = np.zeros(len(rows), dtype=bool)
            for at, row in enumerate(rows):
                if row_clock[at] != clock or not legal[at]:
                    continue
                state = row.get(f"{branch}_{level}_{outcome_name}")
                status = row.get(f"{branch}_{level}_status")
                if status == "complete" and type(state) is bool:
                    values[at] = int(state)
                    eligible[at] = True
            name = f"{clock}.{branch}.{level}.{outcome_name}"
            output[name] = _point_target(name, values, eligible, known, classes=(False, True),
                metadata=_base_metadata(rows[0], mechanism=mechanism, branch=branch, field=name,
                  source_field=f"payload.{branch}.{level}.{source_name}", matrix_id=matrix_id) | {
                      "horizon_minutes": 180, "unique_date_aggregation": "one formation date per row",
                      "model_head": False, "measurement": True,
                      "feature_role": "source_level_measurement"})
    for side in ("upper", "lower", "both"):
        values = np.zeros(len(rows), dtype=np.int64)
        eligible = np.zeros(len(rows), dtype=bool)
        for at, row in enumerate(rows):
            high_complete = row.get(f"{branch}_high_status") == "complete"
            low_complete = row.get(f"{branch}_low_status") == "complete"
            if (row_clock[at] == clock and legal[at] and high_complete and low_complete
                    and type(row.get(f"{branch}_{side}_intersection_180m")) is bool):
                values[at] = int(row[f"{branch}_{side}_intersection_180m"])
                eligible[at] = True
        name = f"{clock}.{branch}.{side}_intersection_180m"
        output[name] = _point_target(name, values, eligible, known, classes=(False, True),
            metadata=_base_metadata(rows[0], mechanism=mechanism, branch=branch, field=name,
              source_field=f"payload.{branch}.high/low.compatible_reach", matrix_id=matrix_id) | {
                  "horizon_minutes": 180, "unique_date_aggregation": "unique_date_rate_and_repeated_bar_share"})
        # Keep a distinct model head for the source's per-formation-date rate.
        # The values are the same one-row-per-date indicators as the
        # intersection head, while the target identity tells the evaluator to
        # report one observation per formation date rather than treating a
        # repeated bar population as a new source mechanism.
        rate_name = f"{clock}.{branch}.{side}_daily_rate"
        output[rate_name] = _point_target(rate_name, values, eligible, known, classes=(False, True),
            metadata=_base_metadata(rows[0], mechanism=mechanism, branch=branch, field=rate_name,
              source_field=f"payload.{branch}.high/low.compatible_reach", matrix_id=matrix_id) | {
                  "horizon_minutes": 180, "aggregation": "unique_date_rate",
                  "denominator": "one formation date per source row",
                  "repeated_bar_diagnostic": "retained separately; never used as a second date"})
    return output


def _overnight_targets(rows, clock: str, *, row_clock, known, legal, matrix_id) -> dict[str, Target]:
    midpoint = np.full(len(rows), np.nan, dtype=np.float64)
    zero = np.zeros(len(rows), dtype=np.int64)
    midpoint_ok = np.zeros(len(rows), dtype=bool)
    zero_ok = np.zeros(len(rows), dtype=bool)
    measurement_known = np.full(len(rows), -1, dtype=np.int64)
    for at, row in enumerate(rows):
        if row_clock[at] != clock:
            continue
        cut = _special_cut(row, "formation")
        source_known = _int_or_none(row.get("inputs_known_at_ns"))
        measurement_ok = (row.get("candidate_available") is True
                          and source_known is not None and cut is not None
                          and source_known <= cut)
        if measurement_ok:
            measurement_known[at] = source_known
        if not measurement_ok:
            continue
        numerator, denominator = row.get("midpoint_numerator"), row.get("midpoint_denominator")
        if type(numerator) is int and type(denominator) is int and denominator > 0:
            midpoint[at] = numerator / denominator
            midpoint_ok[at] = True
        if type(row.get("zero_width")) is bool:
            zero[at] = int(row["zero_width"])
            zero_ok[at] = True
    mechanism = MECHANISM_BY_CLOCK[clock]
    measurement_metadata = {
        "model_head": False, "measurement": True,
        "feature_role": "formation_measurement",
        "known_at_source": "inputs_known_at_ns",
        "known_cut_rule": "source inputs_known_at_ns <= formation cut",
    }
    return {
        f"{clock}.formation.midpoint": _continuous_target(
            f"{clock}.formation.midpoint", midpoint, midpoint_ok, measurement_known,
            metadata=_base_metadata(rows[0], mechanism=mechanism, branch="formation",
                field=f"{clock}.formation.midpoint", source_field="payload.midpoint.numerator/denominator",
                matrix_id=matrix_id) | {"exact_rational": True} | measurement_metadata),
        f"{clock}.formation.zero_width": _point_target(
            f"{clock}.formation.zero_width", zero, zero_ok, measurement_known, classes=(False, True),
            metadata=_base_metadata(rows[0], mechanism=mechanism, branch="formation",
                field=f"{clock}.formation.zero_width", source_field="payload.zero_width",
                matrix_id=matrix_id) | {"zero_atom": True} | measurement_metadata),
    }


def _domain_rows(matrix: PreparedPaths, rows: Sequence[Mapping[str, Any]], *, mechanism: str, branch: str,
                 plan: Mapping[str, Any]) -> tuple[PreparedPaths, tuple[dict[str, Any], ...], np.ndarray, np.ndarray]:
    features, fields, categories, manifest = _path_view(matrix)
    index, names = _path_index(matrix)
    clocks = tuple(clock for clock in SPECIAL_CLOCK_IDS if MECHANISM_BY_CLOCK[clock] == mechanism)
    domain_rows = tuple(row for row in rows if row.get("mechanism") == mechanism)
    if not domain_rows:
        raise SpecialModelInputError(f"special mechanism has no rows: {mechanism}")
    domain_rows = tuple(sorted(domain_rows, key=lambda row: (str(row["root"]), str(row["date"]), str(row["clock"]))))
    root_categories = tuple(categories.get("root", ()))
    clock_categories = clocks
    horizon_name = "formation" if mechanism == MECHANISM_BY_CLOCK["ONS03"] else "after_180m"
    horizon_categories = (horizon_name,)
    joined = np.full((len(domain_rows), features.shape[1]), np.nan, dtype=np.float64)
    condition_features = np.zeros((len(domain_rows), 5), dtype=np.float64)
    # Formation/open geometry is retained as a measured causal input.  Each
    # value is masked until its source-known timestamp is at or before the
    # branch cut; the final column is an explicit availability gate.
    measurement_features = np.full((len(domain_rows), 6), np.nan, dtype=np.float64)
    out_fields: dict[str, list[Any]] = {"date": [], "root": [], "clock": [], "horizon": [],
                                        "planned_minutes": [],
                                        "origin_ns": [], "endpoint_ns": [], "maturity_at_ns": [],
                                        "special_cut_ns": [], "feature_known_at_ns": [], "source_row_index": [],
                                        "measurement_known_at_ns": [], "measurement_available": [],
                                        "causal_eligible": [], "candidate_available": []}
    legal = np.zeros(len(domain_rows), dtype=bool)
    row_clock = np.empty(len(domain_rows), dtype=object)
    for at, row in enumerate(domain_rows):
        day = _as_date(row["date"])
        root = str(row["root"])
        if root not in root_categories:
            raise SpecialModelInputError("special row root is absent from PreparedPaths")
        path_at = index.get((root, day.toordinal(), str(row["clock"])))
        cut = _special_cut(row, branch)
        feature_known = _feature_known_at(fields, path_at) if path_at is not None else None
        joined_here = path_at is not None and cut is not None and feature_known is not None and feature_known <= cut
        if joined_here:
            joined[at] = features[path_at]
        measurement_cut = cut
        measurement_known_at = _int_or_none(row.get("inputs_known_at_ns"))
        measurement_available = bool(
            row.get("candidate_available") is True
            and measurement_known_at is not None
            and measurement_cut is not None
            and measurement_known_at <= measurement_cut
        )
        if measurement_available:
            measurement_features[at, 5] = 1.0
            if mechanism in {MECHANISM_BY_CLOCK["PIN074_ref_00"], MECHANISM_BY_CLOCK["PIN076_00_08"]}:
                sign = row.get("displacement_sign")
                direction = row.get("target_direction_from_forecast")
                zero = row.get("zero_displacement")
                if type(sign) is int and sign in (-1, 0, 1):
                    measurement_features[at, 0] = float(sign)
                if direction in _DIRECTION_CLASSES:
                    measurement_features[at, 1] = float(_DIRECTION_CLASSES.index(direction))
                if type(zero) is bool:
                    measurement_features[at, 2] = float(int(zero))
            if mechanism == MECHANISM_BY_CLOCK["ONS03"]:
                numerator = row.get("midpoint_numerator")
                denominator = row.get("midpoint_denominator")
                if type(numerator) is int and type(denominator) is int and denominator > 0:
                    measurement_features[at, 3] = float(numerator) / float(denominator)
                zero_width = row.get("zero_width")
                if type(zero_width) is bool:
                    measurement_features[at, 4] = float(int(zero_width))
        if str(row["clock"]) in THREE_STAGE_CLOCKS and row.get("conditioning_stratum") in STRATA:
            conditioning = _row_payload(row).get("conditioning")
            conditioning_known = (_int_or_none(conditioning.get("known_at_ns"))
                                 if isinstance(conditioning, Mapping) else None)
            if (conditioning_known is not None and cut is not None
                    and conditioning_known <= cut):
                condition_features[at, STRATA.index(row["conditioning_stratum"])] = 1.0
                condition_features[at, 4] = 1.0
        clock_code = _row_clock_code(row, clock_categories)
        row_clock[at] = str(row["clock"])
        branch_eligible = (bool(row.get(f"{branch}_eligible", False))
                           if branch in {"nominal", "availability_delayed"}
                           else bool(row.get("causal_eligible", False)))
        known = _branch_known_at(row, branch)
        if branch_eligible and known is None:
            raw_reasons = row.get("causal_exclusion_reasons", ())
            reasons = list(raw_reasons) if isinstance(raw_reasons, (list, tuple)) else []
            reason = f"{branch}_target_known_at_missing"
            if reason not in reasons:
                reasons.append(reason)
            row["causal_exclusion_reasons"] = reasons
        legal[at] = bool(joined_here and branch_eligible and known is not None)
        origin, endpoint = _branch_window(row, branch)
        planned = row.get("planned_minutes", 0 if horizon_name == "formation" else 180)
        if origin is not None and endpoint is not None and endpoint >= origin:
            duration_ns = endpoint - origin
            if duration_ns % 60_000_000_000 == 0:
                planned = duration_ns // 60_000_000_000
        out_fields["date"].append(day.toordinal())
        out_fields["root"].append(root_categories.index(root))
        out_fields["clock"].append(clock_code)
        out_fields["horizon"].append(0)
        out_fields["planned_minutes"].append(planned)
        out_fields["origin_ns"].append(_int_or_none(origin))
        out_fields["endpoint_ns"].append(_int_or_none(endpoint))
        out_fields["maturity_at_ns"].append(known)
        out_fields["special_cut_ns"].append(cut)
        out_fields["feature_known_at_ns"].append(feature_known)
        out_fields["source_row_index"].append(row.get("source_row_index", -1))
        out_fields["measurement_known_at_ns"].append(measurement_known_at)
        out_fields["measurement_available"].append(measurement_available)
        out_fields["causal_eligible"].append(legal[at])
        out_fields["candidate_available"].append(bool(row.get("candidate_available")))
    joined = np.column_stack((joined, condition_features, measurement_features))
    joined_names = (*names, "x_special_conditioning_neither", "x_special_conditioning_high_only",
                    "x_special_conditioning_low_only", "x_special_conditioning_both",
                    "x_special_conditioning_known", "x_special_geometry_displacement_sign",
                    "x_special_geometry_target_direction", "x_special_geometry_zero_displacement",
                    "x_special_formation_midpoint", "x_special_formation_zero_width",
                    "x_special_measurement_available")
    field_arrays: dict[str, np.ndarray] = {}
    for name, values in out_fields.items():
        if name in {"date", "root", "clock", "horizon", "planned_minutes", "source_row_index"}:
            field_arrays[name] = np.asarray([(-1 if value is None else value) for value in values], dtype=np.int64)
        elif name in {"causal_eligible", "candidate_available", "measurement_available"}:
            field_arrays[name] = np.asarray(values, dtype=bool)
        else:
            field_arrays[name] = _int64(values)
    field_arrays["special_row_id"] = np.asarray([str(row["row_id"]) for row in domain_rows], dtype=object)
    joined_feature_columns = tuple(
        name if str(name).startswith("x_") else f"x_{name}" for name in joined_names
    )
    model_feature_names = tuple(name[2:] for name in joined_feature_columns)
    path_manifest = {
        "version": VERSION, "source_matrix": manifest.get("id"), "mechanism": mechanism,
        "branch": branch, "feature_columns": list(joined_feature_columns),
        "feature_groups": {"controls": list(model_feature_names), "own": list(model_feature_names),
                            "full": list(model_feature_names)},
        "measurement_feature_columns": ["x_special_geometry_displacement_sign",
                                        "x_special_geometry_target_direction",
                                        "x_special_geometry_zero_displacement",
                                        "x_special_formation_midpoint",
                                        "x_special_formation_zero_width",
                                        "x_special_measurement_available"],
        "measurement_cut_rule": "source inputs_known_at_ns <= branch cut; unavailable values remain NaN",
        "rows": len(domain_rows), "row_identity": "special source_row_index + root/date/clock; exact after_180m join",
        "feature_join_rule": "known feature timestamp <= branch special cut; no nearest prefix or future substitute",
        "source_row_indices": [row.get("source_row_index") for row in domain_rows],
    }
    path_manifest["id"] = digest(path_manifest)
    matrix_shards = matrix.get("shards", ()) if isinstance(matrix, Mapping) else getattr(matrix, "shards", ())
    view = PreparedPaths(path_manifest, joined, field_arrays,
                         {"root": root_categories, "clock": clock_categories, "horizon": horizon_categories},
                         tuple(matrix_shards))
    return view, domain_rows, row_clock, legal


def _validate_plan(plan: Mapping[str, Any]) -> None:
    if not isinstance(plan, Mapping):
        raise SpecialModelInputError("special model plan mapping required")
    expected = tuple(plan.get("expected_special_clock_ids", SPECIAL_CLOCK_IDS))
    if expected != SPECIAL_CLOCK_IDS:
        raise SpecialModelInputError("special model clock population differs from the frozen plan")


def prepare_special_model_views(matrix: PreparedPaths, special_rows: Any, *, plan: Mapping[str, Any]) -> SpecialModelViews:
    """Return causal model views for every declared special mechanism/branch.

    The adapter does not infer missing target values.  A source row stays in
    the view with ``causal_eligible=False`` when its branch is unavailable,
    censored, ambiguous for a point head, or lacks the exact known feature
    join.  Compatible true-event heads use boolean allowed-class matrices;
    censoring and unavailability never become event classes.
    """
    _validate_plan(plan)
    if not isinstance(matrix, (PreparedPaths, Mapping)):
        raise SpecialModelInputError("PreparedPaths or its structural mapping view is required")
    rows = _rows_from_input(special_rows)
    clocks = {str(row.get("clock")) for row in rows}
    if clocks != set(SPECIAL_CLOCK_IDS):
        raise SpecialModelInputError("special rows do not close the frozen clock population")
    mechanisms = tuple(dict.fromkeys(MECHANISM_BY_CLOCK[clock] for clock in SPECIAL_CLOCK_IDS))
    nested: dict[str, dict[str, tuple[PreparedPaths, dict[str, Target]]]] = {}
    _, _, _, matrix_manifest = _path_view(matrix)
    matrix_id = str(matrix_manifest.get("id", "unknown-matrix"))
    for mechanism in mechanisms:
        # PIN073 conditioning is represented by causal feature columns in
        # each forecast branch; it is not an independent future target domain.
        branches = ["formation"] if mechanism == MECHANISM_BY_CLOCK["ONS03"] else [
            "nominal", "availability_delayed"
        ]
        nested[mechanism] = {}
        for branch in branches:
            view, domain_rows, row_clock, legal = _domain_rows(matrix, rows, mechanism=mechanism, branch=branch, plan=plan)
            known = view.fields["maturity_at_ns"]
            targets: dict[str, Target] = {}
            if mechanism == MECHANISM_BY_CLOCK["ONS03"]:
                for clock in OVERNIGHT_CLOCKS:
                    targets.update(_overnight_targets(domain_rows, clock, row_clock=row_clock, known=known,
                                                      legal=legal, matrix_id=view.manifest["id"]))
            elif mechanism == MECHANISM_BY_CLOCK["magic_00"]:
                for clock in MAGIC_CLOCKS:
                    targets.update(_magic_targets(domain_rows, clock, branch, matrix_id=view.manifest["id"],
                                                  row_clock=row_clock, known=known, legal=legal))
            elif mechanism == MECHANISM_BY_CLOCK["PIN073_1"]:
                for clock in THREE_STAGE_CLOCKS:
                    targets.update(_three_stage_targets(domain_rows, clock, branch, row_clock=row_clock,
                                                        known=known, legal=legal, matrix_id=view.manifest["id"]))
            elif mechanism in {MECHANISM_BY_CLOCK["PIN074_ref_00"], MECHANISM_BY_CLOCK["PIN076_00_08"]}:
                for clock in OPEN_TO_OPEN_CLOCKS:
                    targets.update(_open_targets(domain_rows, clock, branch, row_clock=row_clock,
                                                 known=known, legal=legal, matrix_id=view.manifest["id"]))
            elif mechanism == MECHANISM_BY_CLOCK["PIN078_daily_not_combined"]:
                targets.update(_daily_targets(domain_rows, "PIN078_daily_not_combined", branch,
                                              row_clock=row_clock, known=known, legal=legal,
                                              matrix_id=view.manifest["id"]))
            else:
                raise SpecialModelInputError(f"unsupported frozen special mechanism {mechanism}")
            for name, target in targets.items():
                clock = name.split(".", 1)[0]
                if clock not in SPECIAL_CLOCK_IDS:
                    raise SpecialModelInputError("target lacks its declared source clock")
                target.metadata["applicable_clocks"] = [clock]
                target.metadata["population_rule"] = "all rows of this source clock before causal or label eligibility"
                target.metadata["id"] = digest({k: v for k, v in target.metadata.items() if k != "id"})
            nested[mechanism][branch] = (view, targets)
    views = SpecialModelViews(nested)
    declared = _declared_model_target_ids(special_rows)
    if declared is not None:
        actual = {
            target_name
            for _, (_, targets) in views.items()
            for target_name, target in targets.items()
            if target.metadata.get("model_head", True)
        }
        if actual != declared:
            missing = sorted(declared - actual)
            extra = sorted(actual - declared)
            raise SpecialModelInputError(
                "special model target contract differs from declared targetspecs: "
                f"missing={missing}, extra={extra}"
            )
    return views


__all__ = ["VERSION", "SpecialModelInputError", "SpecialModelViews", "prepare_special_model_views"]
