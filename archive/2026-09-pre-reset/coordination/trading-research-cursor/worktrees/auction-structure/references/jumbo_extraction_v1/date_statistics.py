"""Observed-date means, ratios and paired score-gain uncertainty.

The inputs to this module are already formed observations.  A caller supplies
the complete intended date order explicitly; a missing cell is represented by
an absent key or ``None`` and is excluded from that metric's denominator.  It
is never converted to a zero.  The moving-block resampler uses one shared
weight matrix for every metric and ratio, so paired dependence between
metrics survives the resampling step.

This module deliberately has no market-data reader.  It is a small numerical
adapter for admitted date/event summaries and keeps its public result JSON
serializable.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from datetime import date, datetime
import math
import random
from numbers import Real
from typing import Any

from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.research.scoring import IntervalSpec, block_interval, quantile


DEFAULT_SEED = 20260907
DEFAULT_BLOCK_LENGTH = 5
DEFAULT_REPLICATES = 1000
DEFAULT_CONFIDENCE = 0.95
DEFAULT_MINIMUM_DATES = 100
DEFAULT_MINIMUM_EVENTS = 20
DATE_STATISTICS_VERSION = "observed-date-statistics-v1"


def _numpy():
    """Load the registered numerical dependency only when computation starts."""
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - exercised without the research extra
        raise DependencyUnavailable("date statistics require the pinned NumPy 2.3.3 research extra") from exc
    if getattr(np, "__version__", None) != "2.3.3":
        raise ContractError("date statistics require the pinned NumPy 2.3.3 provider")
    return np


def _finite(value: Any) -> float:
    if isinstance(value, (bool, str, bytes)) or not isinstance(value, Real):
        raise ContractError("date statistic observations must be finite real numbers")
    result = float(value)
    if not math.isfinite(result):
        raise ContractError("date statistic observations must be finite real numbers")
    return result


def _json_date(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return str(value)


def _date_order(intended_dates: Sequence[Any]) -> tuple[tuple[Any, ...], tuple[str, ...]]:
    if isinstance(intended_dates, (str, bytes)):
        raise ContractError("date statistics require an explicit non-string date sequence")
    try:
        dates = tuple(intended_dates)
    except TypeError as exc:
        raise ContractError("date statistics require an explicit date sequence") from exc
    if not dates:
        raise ContractError("date statistics require at least one intended date")
    try:
        if len(set(dates)) != len(dates):
            raise ContractError("intended date order contains duplicates")
    except TypeError as exc:
        raise ContractError("intended date identifiers must be hashable") from exc
    labels = tuple(_json_date(value) for value in dates)
    if len(set(labels)) != len(labels):
        raise ContractError("intended date identifiers have duplicate JSON labels")
    return dates, labels


def _cell_values(value: Any) -> tuple[float, ...]:
    """Convert one scalar/event cell while preserving missing cells as empty."""
    if value is None:
        return ()
    if isinstance(value, (bool, str, bytes)):
        raise ContractError("metric cells must be numeric scalars or numeric event sequences")
    if isinstance(value, Real):
        return (_finite(value),)
    if not isinstance(value, Iterable):
        raise ContractError("metric cells must be numeric scalars or numeric event sequences")
    values = []
    for item in value:
        if item is None:
            continue
        values.append(_finite(item))
    return tuple(values)


def _normalise_metric(name: str, cells: Mapping[Any, Any], dates: tuple[Any, ...]):
    if not isinstance(name, str) or not name:
        raise ContractError("metric names must be nonempty strings")
    if not isinstance(cells, Mapping):
        raise ContractError("each metric requires a date-to-cell mapping")
    date_set = set(dates)
    extras = set(cells).difference(date_set)
    if extras:
        raise ContractError(f"metric {name} contains cells outside the intended date universe")
    normalised = tuple(_cell_values(cells.get(day)) for day in dates)
    sums = tuple(math.fsum(values) if values else 0.0 for values in normalised)
    counts = tuple(len(values) for values in normalised)
    valid_dates = sum(count > 0 for count in counts)
    valid_events = sum(counts)
    return {
        "name": name,
        "cells": normalised,
        "sums": sums,
        "counts": counts,
        "valid_dates": valid_dates,
        "valid_events": valid_events,
    }


def _validate_config(*, seed: int, block_length: int, replicates: int,
                     confidence: float, minimum_dates: int, minimum_events: int) -> None:
    if type(seed) is not int:
        raise ContractError("bootstrap seed must be an exact integer")
    if type(block_length) is not int or block_length < 1:
        raise ContractError("moving block length must be a positive integer")
    if type(replicates) is not int or not 200 <= replicates <= 20_000:
        raise ContractError("bootstrap replicates must be bounded between 200 and 20000")
    if type(confidence) not in (float, int) or isinstance(confidence, bool) or not .5 < float(confidence) < 1:
        raise ContractError("bootstrap confidence must be strictly between one half and one")
    if type(minimum_dates) is not int or minimum_dates < 1:
        raise ContractError("minimum independent-date support must be positive")
    if type(minimum_events) is not int or minimum_events < 1:
        raise ContractError("minimum event support must be positive")


def _moving_weights(np, date_count: int, *, seed: int, block_length: int, replicates: int):
    """Return shared occurrence weights and Python-random block starts.

    Starts are generated with the same nonwrapping rule as
    ``research.scoring.block_interval``.  The matrix arithmetic after this
    point is vectorized over all replicates.
    """
    weights = np.zeros((replicates if date_count >= block_length else 0, date_count), dtype=np.int64)
    starts_by_rep: list[tuple[int, ...]] = []
    if date_count < block_length:
        starts_by_rep = [tuple() for _ in range(replicates)]
        return weights, tuple(starts_by_rep)
    rng = random.Random(seed)
    for row in range(replicates):
        starts: list[int] = []
        indices: list[int] = []
        while len(indices) < date_count:
            start = rng.randrange(date_count - block_length + 1)
            starts.append(start)
            indices.extend(range(start, start + block_length))
        selected = indices[:date_count]
        np.add.at(weights[row], np.asarray(selected, dtype=np.int64), 1)
        starts_by_rep.append(tuple(starts))
    return weights, tuple(starts_by_rep)


def _batch_bootstrap_components(np, metrics: Mapping[str, dict[str, Any]], names: tuple[str, ...],
                                *, estimator: str, weights, replicates: int):
    """Build all metric bootstrap columns with two shared matrix products."""
    sums = np.asarray(tuple(metrics[name]["sums"] for name in names), dtype=np.float64)
    counts = np.asarray(tuple(metrics[name]["counts"] for name in names), dtype=np.float64)
    valid = counts > 0
    date_means = np.zeros_like(sums, dtype=np.float64)
    np.divide(sums, counts, out=date_means, where=valid)
    if estimator == "date_mean":
        numerators = np.where(valid, date_means, 0.0)
        denominators = valid.astype(np.float64)
    elif estimator == "event_mean":
        numerators = sums
        denominators = counts
    else:
        raise ContractError("estimator must be date_mean or event_mean")
    if weights.shape[0]:
        # Shape is (replicates, metrics); every metric sees the same date
        # occurrence weights, preserving paired dependence.
        bootstrap_numerators = weights @ numerators.T
        bootstrap_denominators = weights @ denominators.T
    else:
        bootstrap_numerators = np.zeros((replicates, len(names)), dtype=np.float64)
        bootstrap_denominators = np.zeros((replicates, len(names)), dtype=np.float64)
    return bootstrap_numerators, bootstrap_denominators


def _percentile(values: Sequence[float], level: float) -> float | None:
    if not values:
        return None
    return float(quantile(tuple(float(value) for value in values), level))


def _reference_interval(date_values: tuple[float, ...], dates: tuple[str, ...], *, seed: int,
                        block_length: int, replicates: int, confidence: float):
    """Use the established scoring reference for all-valid date means."""
    if len(dates) < block_length or replicates < 200:
        return None
    spec = IntervalSpec(confidence, replicates, seed, block_length, 2, "equal_date")
    return block_interval({day: (value,) for day, value in zip(dates, date_values, strict=True)},
                          spec, ordered_dates=dates)


def _metric_result(np, metric: dict[str, Any], labels: tuple[str, ...], weights,
                   starts_by_rep: tuple[tuple[int, ...], ...], *, estimator: str,
                   seed: int, block_length: int, replicates: int, confidence: float,
                   minimum_dates: int, minimum_events: int,
                   bootstrap_numerator=None, bootstrap_denominator=None,
                   validate_reference: bool = False):
    if estimator not in {"date_mean", "event_mean"}:
        raise ContractError("estimator must be date_mean or event_mean")
    sums = np.asarray(metric["sums"], dtype=np.float64)
    counts = np.asarray(metric["counts"], dtype=np.int64)
    valid_mask = counts > 0
    date_means = np.zeros(len(labels), dtype=np.float64)
    np.divide(sums, counts, out=date_means, where=valid_mask)
    if estimator == "date_mean":
        numerator_values = np.where(valid_mask, date_means, 0.0)
        denominator_values = valid_mask.astype(np.int64)
        point_denominator = int(metric["valid_dates"])
        point_numerator = float(np.sum(numerator_values, dtype=np.float64))
        denominator_name = "valid_dates"
    else:
        numerator_values = sums
        denominator_values = counts
        point_denominator = int(metric["valid_events"])
        point_numerator = float(np.sum(sums, dtype=np.float64))
        denominator_name = "valid_events"
    point = None if point_denominator == 0 else point_numerator / point_denominator

    if bootstrap_numerator is not None or bootstrap_denominator is not None:
        if bootstrap_numerator is None or bootstrap_denominator is None:
            raise ContractError("bootstrap numerator and denominator must be supplied together")
        numerator = bootstrap_numerator
        denominator = bootstrap_denominator
    elif weights.shape[0]:
        numerator = weights @ numerator_values
        denominator = weights @ denominator_values
    else:
        denominator = np.zeros(replicates, dtype=np.float64)
        numerator = np.zeros(replicates, dtype=np.float64)
    valid_replicates = denominator > 0
    replicate_array = np.full(replicates, np.nan, dtype=np.float64)
    replicate_array[valid_replicates] = numerator[valid_replicates] / denominator[valid_replicates]
    invalid_denominator = int(np.count_nonzero(~valid_replicates))
    replicate_values = [float(value) if math.isfinite(float(value)) else None for value in replicate_array]
    valid_values = [value for value in replicate_values if value is not None]
    alpha = (1 - float(confidence)) / 2
    lower = _percentile(valid_values, alpha)
    upper = _percentile(valid_values, 1 - alpha)

    reference_checked = False
    reference_matches = None
    all_valid = bool(np.all(valid_mask))
    if validate_reference and all_valid and (estimator == "date_mean" or bool(np.all(counts == 1))):
        reference = _reference_interval(tuple(float(value) for value in date_means), labels,
                                        seed=seed, block_length=block_length,
                                        replicates=replicates, confidence=float(confidence))
        if reference is not None:
            reference_checked = True
            reference_matches = (
                (lower is None and reference["lower"] is None or
                 lower is not None and math.isclose(lower, float(reference["lower"]), rel_tol=0, abs_tol=1e-12))
                and
                (upper is None and reference["upper"] is None or
                 upper is not None and math.isclose(upper, float(reference["upper"]), rel_tol=0, abs_tol=1e-12))
            )
            if not reference_matches:
                raise ContractError("vectorized date-block bootstrap diverges from scoring.block_interval")
            lower, upper = reference["lower"], reference["upper"]

    reasons = []
    if metric["valid_dates"] < minimum_dates:
        reasons.append("fewer_than_minimum_independent_dates")
    if metric["valid_events"] < minimum_events:
        reasons.append("fewer_than_minimum_events")
    if len(labels) < block_length:
        reasons.append("block_length_exceeds_intended_date_universe")
    if invalid_denominator:
        reasons.append("invalid_bootstrap_denominator_replicates")
    support = {
        "independent_dates": int(metric["valid_dates"]),
        "events": int(metric["valid_events"]),
        "minimum_independent_dates": int(minimum_dates),
        "minimum_events": int(minimum_events),
        "sparse": bool(reasons[:2]),
        "reasons": reasons[:2],
    }
    return {
        "estimate": None if point is None else float(point),
        "actual_valid_date_count": int(metric["valid_dates"]),
        "actual_valid_event_count": int(metric["valid_events"]),
        "valid_date_count": int(metric["valid_dates"]),
        "valid_event_count": int(metric["valid_events"]),
        "missing_date_count": int(len(labels) - metric["valid_dates"]),
        "estimator": estimator,
        "support": support,
        "bootstrap": {
            "lower": None if lower is None else float(lower),
            "upper": None if upper is None else float(upper),
            "confidence": float(confidence),
            "replicates": int(replicates),
            "valid_replicates": int(len(valid_values)),
            "invalid_denominator_replicates": invalid_denominator,
            "null_replicates": invalid_denominator,
            "seed": int(seed),
            "block_length": int(block_length),
            "denominator": denominator_name,
            "method": "moving_consecutive_date_block_percentile_bootstrap",
            "circular_end_wrap": False,
            "reference_parity_checked": reference_checked,
            "reference_parity_matches": reference_matches,
            "replicate_estimates": replicate_values,
        },
    }, replicate_array, valid_mask


def _normalise_ratios(ratios: Mapping[str, Any] | Sequence[Sequence[str]] | None):
    if ratios is None:
        return ()
    if isinstance(ratios, Mapping):
        items = tuple((name, value) for name, value in ratios.items())
    else:
        try:
            items = tuple((item[0], (item[1], item[2])) for item in ratios)
        except (TypeError, IndexError) as exc:
            raise ContractError("ratios must map names to (numerator, denominator) pairs") from exc
    result = []
    seen = set()
    for name, pair in items:
        if not isinstance(name, str) or not name or name in seen:
            raise ContractError("ratio names must be unique nonempty strings")
        if not isinstance(pair, Sequence) or isinstance(pair, (str, bytes)) or len(pair) != 2:
            raise ContractError("each ratio must declare exactly one numerator and denominator metric")
        numerator, denominator = pair
        if not all(isinstance(value, str) and value for value in (numerator, denominator)) or numerator == denominator:
            raise ContractError("ratio metrics must be two distinct named metrics")
        result.append((name, numerator, denominator))
        seen.add(name)
    return tuple(result)


def _ratio_result(np, name: str, numerator_name: str, denominator_name: str,
                  numerator: dict[str, Any], denominator: dict[str, Any],
                  numerator_replicates, denominator_replicates, *, labels: tuple[str, ...],
                  weights, seed: int, block_length: int, replicates: int,
                  confidence: float, minimum_dates: int, minimum_events: int):
    numerator_point = numerator["estimate"]
    denominator_point = denominator["estimate"]
    point_invalid = (numerator_point is None or denominator_point is None or denominator_point == 0)
    estimate = None if point_invalid else float(numerator_point / denominator_point)
    valid_denominator = np.isfinite(denominator_replicates) & (denominator_replicates != 0)
    valid_numerator = np.isfinite(numerator_replicates)
    valid = valid_denominator & valid_numerator
    values = np.full(replicates, np.nan, dtype=np.float64)
    values[valid] = numerator_replicates[valid] / denominator_replicates[valid]
    invalid_denominator = int(np.count_nonzero(~valid_denominator))
    invalid_total = int(np.count_nonzero(~valid))
    serial = [float(value) if math.isfinite(float(value)) else None for value in values]
    valid_values = [value for value in serial if value is not None]
    alpha = (1 - float(confidence)) / 2
    reasons = []
    independent_dates = min(numerator["actual_valid_date_count"], denominator["actual_valid_date_count"])
    events = min(numerator["actual_valid_event_count"], denominator["actual_valid_event_count"])
    if independent_dates < minimum_dates:
        reasons.append("fewer_than_minimum_independent_dates")
    if events < minimum_events:
        reasons.append("fewer_than_minimum_events")
    if point_invalid:
        reasons.append("invalid_point_denominator")
    if invalid_denominator:
        reasons.append("invalid_bootstrap_denominator_replicates")
    return {
        "numerator": numerator_name,
        "denominator": denominator_name,
        "estimate": estimate,
        "actual_valid_date_count": independent_dates,
        "actual_valid_event_count": events,
        "valid_date_count": independent_dates,
        "valid_event_count": events,
        "support": {
            "independent_dates": independent_dates,
            "events": events,
            "minimum_independent_dates": int(minimum_dates),
            "minimum_events": int(minimum_events),
            "sparse": bool(reasons[:2]),
            "reasons": reasons[:2],
        },
        "bootstrap": {
            "lower": _percentile(valid_values, alpha),
            "upper": _percentile(valid_values, 1 - alpha),
            "confidence": float(confidence),
            "replicates": int(replicates),
            "valid_replicates": len(valid_values),
            "invalid_denominator_replicates": invalid_denominator,
            "invalid_replicates": invalid_total,
            "null_replicates": invalid_total,
            "seed": int(seed),
            "block_length": int(block_length),
            "method": "shared_moving_consecutive_date_block_percentile_bootstrap",
            "circular_end_wrap": False,
            "replicate_estimates": serial,
        },
    }


def observed_date_statistics(
    metrics: Mapping[str, Mapping[Any, Any]],
    intended_dates: Sequence[Any],
    *,
    ratios: Mapping[str, Any] | Sequence[Sequence[str]] | None = None,
    estimator: str = "date_mean",
    seed: int = DEFAULT_SEED,
    block_length: int = DEFAULT_BLOCK_LENGTH,
    replicates: int = DEFAULT_REPLICATES,
    confidence: float = DEFAULT_CONFIDENCE,
    minimum_independent_dates: int = DEFAULT_MINIMUM_DATES,
    minimum_events: int = DEFAULT_MINIMUM_EVENTS,
    include_weights: bool = False,
    return_weights: bool | None = None,
    validate_reference: bool = False,
) -> dict[str, Any]:
    """Summarize observed metric cells and shared date-block uncertainty.

    ``metrics`` maps a metric name to ``date -> value`` or ``date -> values``.
    A sequence value represents multiple events on that date.  The default
    date estimator gives each valid date one weight; ``event_mean`` instead
    gives each valid event one weight.  Ratios are ratios of the corresponding
    bootstrap means.  Missing cells contribute neither numerator nor
    denominator.
    """
    np = _numpy()
    if not isinstance(metrics, Mapping) or not metrics:
        raise ContractError("at least one named metric is required")
    if return_weights is not None:
        if type(return_weights) is not bool:
            raise ContractError("return_weights must be boolean when supplied")
        include_weights = return_weights
    if type(validate_reference) is not bool:
        raise ContractError("validate_reference must be boolean")
    _validate_config(seed=seed, block_length=block_length, replicates=replicates,
                     confidence=confidence, minimum_dates=minimum_independent_dates,
                     minimum_events=minimum_events)
    dates, labels = _date_order(intended_dates)
    names = tuple(metrics)
    if len(set(names)) != len(names) or any(not isinstance(name, str) or not name for name in names):
        raise ContractError("metric names must be unique nonempty strings")
    normalised = {name: _normalise_metric(name, metrics[name], dates) for name in names}
    ratio_specs = _normalise_ratios(ratios)
    for _, numerator, denominator in ratio_specs:
        if numerator not in normalised or denominator not in normalised:
            raise ContractError("ratio references a metric absent from the metric population")
    weights, starts_by_rep = _moving_weights(np, len(dates), seed=seed,
                                             block_length=block_length, replicates=replicates)
    bootstrap_numerators, bootstrap_denominators = _batch_bootstrap_components(
        np, normalised, names, estimator=estimator, weights=weights, replicates=replicates,
    )
    metric_results: dict[str, Any] = {}
    internal: dict[str, tuple[Any, Any]] = {}
    for index, name in enumerate(names):
        result, replicate_array, valid_mask = _metric_result(
            np, normalised[name], labels, weights, starts_by_rep,
            estimator=estimator, seed=seed, block_length=block_length,
            replicates=replicates, confidence=float(confidence),
            minimum_dates=minimum_independent_dates, minimum_events=minimum_events,
            bootstrap_numerator=bootstrap_numerators[:, index],
            bootstrap_denominator=bootstrap_denominators[:, index],
            validate_reference=validate_reference,
        )
        metric_results[name] = result
        internal[name] = (replicate_array, valid_mask)
    ratio_results = {}
    for name, numerator_name, denominator_name in ratio_specs:
        numerator_array, _ = internal[numerator_name]
        denominator_array, _ = internal[denominator_name]
        ratio_results[name] = _ratio_result(
            np, name, numerator_name, denominator_name,
            metric_results[numerator_name], metric_results[denominator_name],
            numerator_array, denominator_array, labels=labels, weights=weights,
            seed=seed, block_length=block_length, replicates=replicates,
            confidence=float(confidence), minimum_dates=minimum_independent_dates,
            minimum_events=minimum_events,
        )
    result: dict[str, Any] = {
        "schema": DATE_STATISTICS_VERSION,
        "intended_dates": list(labels),
        "intended_date_count": len(labels),
        "configuration": {
            "seed": int(seed),
            "block_length": int(block_length),
            "replicates": int(replicates),
            "confidence": float(confidence),
            "minimum_independent_dates": int(minimum_independent_dates),
            "minimum_events": int(minimum_events),
            "estimator": estimator,
            "validate_reference": validate_reference,
        },
        "metrics": metric_results,
        "ratios": ratio_results,
    }
    if include_weights:
        result["bootstrap_weights"] = {
            "date_order": list(labels),
            "weights": weights.tolist(),
            "block_starts": [list(starts) for starts in starts_by_rep],
            "seed": int(seed),
            "block_length": int(block_length),
            "replicates": int(replicates),
            "circular_end_wrap": False,
        }
    return result


def paired_score_gain_interval(
    baseline: Mapping[Any, Any],
    challenger: Mapping[Any, Any],
    intended_dates: Sequence[Any],
    *,
    seed: int = DEFAULT_SEED,
    block_length: int = DEFAULT_BLOCK_LENGTH,
    replicates: int = DEFAULT_REPLICATES,
    confidence: float = DEFAULT_CONFIDENCE,
    minimum_independent_dates: int = DEFAULT_MINIMUM_DATES,
    minimum_events: int = DEFAULT_MINIMUM_EVENTS,
    include_weights: bool = False,
    return_weights: bool | None = None,
    validate_reference: bool = False,
) -> dict[str, Any]:
    """Return a date-clustered percentile interval for baseline minus challenger.

    Paired events on one date must have equal cardinality.  A date missing
    from either arm is excluded from the gain denominator and remains visible
    through ``missing_pair_date_count``.
    """
    np = _numpy()
    if return_weights is not None:
        if type(return_weights) is not bool:
            raise ContractError("return_weights must be boolean when supplied")
        include_weights = return_weights
    if type(validate_reference) is not bool:
        raise ContractError("validate_reference must be boolean")
    _validate_config(seed=seed, block_length=block_length, replicates=replicates,
                     confidence=confidence, minimum_dates=minimum_independent_dates,
                     minimum_events=minimum_events)
    dates, labels = _date_order(intended_dates)
    if not isinstance(baseline, Mapping) or not isinstance(challenger, Mapping):
        raise ContractError("paired score arms require date-to-cell mappings")
    base = _normalise_metric("baseline", baseline, dates)
    alt = _normalise_metric("challenger", challenger, dates)
    gains = {}
    mismatched = []
    for day, base_values, alt_values in zip(dates, base["cells"], alt["cells"], strict=True):
        if not base_values or not alt_values:
            continue
        if len(base_values) != len(alt_values):
            mismatched.append(_json_date(day))
            continue
        gains[day] = tuple(a - b for a, b in zip(base_values, alt_values, strict=True))
    if mismatched:
        raise ContractError("paired score arms have unequal event counts on dates: " + ",".join(mismatched))
    metric = _normalise_metric("score_gain", gains, dates)
    weights, starts_by_rep = _moving_weights(np, len(dates), seed=seed,
                                             block_length=block_length, replicates=replicates)
    result, _, _ = _metric_result(
        np, metric, labels, weights, starts_by_rep, estimator="date_mean",
        seed=seed, block_length=block_length, replicates=replicates,
        confidence=float(confidence), minimum_dates=minimum_independent_dates,
        minimum_events=minimum_events,
        validate_reference=validate_reference,
    )
    result = {
        "schema": DATE_STATISTICS_VERSION,
        "kind": "date_clustered_paired_score_gain",
        "gain_definition": "baseline_minus_challenger",
        **result,
        "missing_pair_date_count": len(labels) - metric["valid_dates"],
    }
    if include_weights:
        result["bootstrap_weights"] = {
            "date_order": list(labels),
            "weights": weights.tolist(),
            "block_starts": [list(starts) for starts in starts_by_rep],
            "seed": int(seed),
            "block_length": int(block_length),
            "replicates": int(replicates),
            "circular_end_wrap": False,
        }
    return result


# Short aliases keep the adapter convenient for callers while preserving one
# implementation and one JSON schema.
date_statistics = observed_date_statistics
paired_gain_interval = paired_score_gain_interval


__all__ = [
    "DATE_STATISTICS_VERSION",
    "DEFAULT_BLOCK_LENGTH",
    "DEFAULT_CONFIDENCE",
    "DEFAULT_MINIMUM_DATES",
    "DEFAULT_MINIMUM_EVENTS",
    "DEFAULT_REPLICATES",
    "DEFAULT_SEED",
    "date_statistics",
    "observed_date_statistics",
    "paired_gain_interval",
    "paired_score_gain_interval",
]
