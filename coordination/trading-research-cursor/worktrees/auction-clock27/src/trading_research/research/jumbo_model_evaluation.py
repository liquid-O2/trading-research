"""Array-only scoring and date-grouped evaluation for the Jumbo study.

This draft deliberately stops at numerical scoring and report assembly.  It
does not read market data, create chronological folds, fit a model, or decide
whether a research comparison is useful.  Callers supply the already aligned
predictions, labels, date ordinals, and group IDs.

The date bootstrap follows the retained ``date_statistics`` convention:
equal-date estimands, consecutive moving blocks, no wrap from the last date to
the first, seed 20260907, block length five, and 1,000 replicates by default.
Missing cells remain missing; they are never converted to zero or a fractional
binary label.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import math
import random
from typing import Any

import numpy as np


DEFAULT_SEED = 20260907
DEFAULT_BLOCK_LENGTH = 5
DEFAULT_REPLICATES = 1000
DEFAULT_CONFIDENCE = 0.95
DEFAULT_MINIMUM_DATES = 100
DEFAULT_MINIMUM_EVENTS = 20
DEFAULT_LOG_FLOOR = 1e-15
DEFAULT_CALIBRATION_EDGES = tuple(float(v) for v in np.linspace(0.0, 1.0, 11))
EVALUATION_VERSION = "jumbo-array-evaluation-v1"


class EvaluationInputError(ValueError):
    """Malformed, non-finite, or semantically incompatible score input."""


def _finite_array(value: Any, *, name: str, ndim: int | None = None,
                  allow_nan: bool = False) -> np.ndarray:
    try:
        array = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise EvaluationInputError(f"{name} must be numeric") from exc
    if ndim is not None and array.ndim != ndim:
        raise EvaluationInputError(f"{name} must have {ndim} dimensions")
    if np.isinf(array).any() or (not allow_nan and np.isnan(array).any()):
        raise EvaluationInputError(f"{name} contains non-finite values")
    return np.ascontiguousarray(array)


def _vector(value: Any, *, name: str, n: int | None = None,
            allow_nan: bool = False) -> np.ndarray:
    array = _finite_array(value, name=name, ndim=1, allow_nan=allow_nan)
    if n is not None and array.shape[0] != n:
        raise EvaluationInputError(f"{name} must have length {n}")
    return array


def _positive_floor(value: float) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise EvaluationInputError("log_floor must be numeric") from exc
    if not math.isfinite(result) or not 0.0 < result < 1.0:
        raise EvaluationInputError("log_floor must be finite and in (0,1)")
    return result


def _probabilities(value: Any, *, name: str = "probabilities",
                   simplex_tolerance: float = 1e-9) -> tuple[np.ndarray, dict[str, Any]]:
    probabilities = _finite_array(value, name=name, ndim=2)
    if probabilities.shape[1] < 1:
        raise EvaluationInputError(f"{name} must contain at least one class")
    if np.any(probabilities < 0.0) or np.any(probabilities > 1.0):
        raise EvaluationInputError(f"{name} must lie in [0,1]")
    if not math.isfinite(float(simplex_tolerance)) or simplex_tolerance < 0:
        raise EvaluationInputError("simplex_tolerance must be finite and nonnegative")
    row_sums = probabilities.sum(axis=1)
    errors = np.abs(row_sums - 1.0)
    valid = errors <= float(simplex_tolerance)
    if not bool(np.all(valid)):
        raise EvaluationInputError(
            f"{name} rows do not satisfy the probability simplex within tolerance"
        )
    return probabilities, {
        "rows": int(probabilities.shape[0]),
        "classes": int(probabilities.shape[1]),
        "rows_checked": int(probabilities.shape[0]),
        "rows_valid": int(np.count_nonzero(valid)),
        "max_abs_sum_error": float(errors.max()) if errors.size else 0.0,
        "tolerance": float(simplex_tolerance),
    }


def _class_indices(observed_class: Any, n: int, k: int) -> np.ndarray:
    raw = _vector(observed_class, name="observed_class", n=n, allow_nan=False)
    if np.any(raw != np.floor(raw)) or np.any(raw < 0) or np.any(raw >= k):
        raise EvaluationInputError("observed_class must contain integer class indices")
    return raw.astype(np.int64)


def _allowed_matrix(value: Any, n: int, k: int) -> np.ndarray:
    raw = np.asarray(value)
    if raw.ndim != 2 or raw.shape != (n, k):
        raise EvaluationInputError("allowed_class_matrix must have shape (N,K)")
    if raw.dtype != np.dtype(bool):
        try:
            numeric = np.asarray(raw, dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise EvaluationInputError("allowed_class_matrix must be boolean") from exc
        if np.isnan(numeric).any() or np.isinf(numeric).any() or not np.all(np.isin(numeric, (0.0, 1.0))):
            raise EvaluationInputError("allowed_class_matrix must contain only 0/1 values")
        raw = numeric.astype(bool)
    allowed = np.ascontiguousarray(raw, dtype=bool)
    if np.any(allowed.sum(axis=1) == 0):
        raise EvaluationInputError("each allowed-class row needs at least one class")
    return allowed


def _quantiles(value: Any) -> np.ndarray:
    result = _vector(value, name="quantiles", allow_nan=False)
    if result.size == 0 or np.any(result <= 0.0) or np.any(result >= 1.0):
        raise EvaluationInputError("quantiles must be nonempty and strictly inside (0,1)")
    if np.any(result[:-1] >= result[1:]):
        raise EvaluationInputError("quantiles must be strictly increasing")
    return result


def _summary_mean(values: np.ndarray) -> float:
    valid = np.isfinite(values)
    return float(values[valid].mean()) if bool(valid.any()) else float("nan")


def categorical_metrics(
    probabilities: Any,
    observed_class: Any = None,
    allowed_class_matrix: Any = None,
    *,
    log_floor: float = DEFAULT_LOG_FLOOR,
    simplex_tolerance: float = 1e-9,
) -> dict[str, Any]:
    """Score point or interval/allowed-class categorical outcomes.

    ``observed_class`` contains zero-based class indices.  Alternatively,
    ``allowed_class_matrix`` contains one boolean row per observation.  Rows
    allowing all classes are retained as no-information rows: their interval
    probability is one, but their interval score and point Brier score are
    ``NaN``.  The log floor is applied only while scoring and its use is
    counted; it never enters a model objective or gradient.
    """
    if (observed_class is None) == (allowed_class_matrix is None):
        raise EvaluationInputError("supply exactly one of observed_class or allowed_class_matrix")
    probabilities, simplex = _probabilities(probabilities, simplex_tolerance=simplex_tolerance)
    n, k = probabilities.shape
    floor = _positive_floor(log_floor)
    if observed_class is not None:
        indices = _class_indices(observed_class, n, k)
        allowed = np.zeros((n, k), dtype=bool)
        if n:
            allowed[np.arange(n), indices] = True
        mode = "point"
    else:
        allowed = _allowed_matrix(allowed_class_matrix, n, k)
        indices = np.full(n, -1, dtype=np.int64)
        singleton = allowed.sum(axis=1) == 1
        if bool(singleton.any()):
            indices[singleton] = np.argmax(allowed[singleton], axis=1)
        mode = "allowed_class_set"

    counts = allowed.sum(axis=1)
    all_class = counts == k
    point_identified = counts == 1
    interval_mass = np.sum(probabilities * allowed, axis=1)
    interval_scored = ~all_class

    entropy_terms = np.zeros_like(probabilities)
    positive = probabilities > 0.0
    entropy_terms[positive] = probabilities[positive] * np.log(probabilities[positive])
    entropy = -entropy_terms.sum(axis=1)

    interval_probability = interval_mass.copy()
    interval_log_score = np.full(n, np.nan, dtype=np.float64)
    interval_log_loss = np.full(n, np.nan, dtype=np.float64)
    scored_mass = np.maximum(interval_mass[interval_scored], floor)
    interval_log_score[interval_scored] = np.log(scored_mass)
    interval_log_loss[interval_scored] = -interval_log_score[interval_scored]
    floor_applied_interval = interval_scored & (interval_mass < floor)
    interval_zero_probability = interval_scored & (interval_mass == 0.0)

    log_score = np.full(n, np.nan, dtype=np.float64)
    log_loss = np.full(n, np.nan, dtype=np.float64)
    brier = np.full(n, np.nan, dtype=np.float64)
    zero_probability = np.zeros(n, dtype=bool)
    floor_applied_point = np.zeros(n, dtype=bool)
    if bool(point_identified.any()):
        point_index = indices[point_identified]
        point_probability = probabilities[point_identified, point_index]
        zero_probability[point_identified] = point_probability == 0.0
        floor_applied_point[point_identified] = point_probability < floor
        point_scored_probability = np.maximum(point_probability, floor)
        log_score[point_identified] = np.log(point_scored_probability)
        log_loss[point_identified] = -log_score[point_identified]
        one_hot = np.zeros((point_index.shape[0], k), dtype=np.float64)
        one_hot[np.arange(point_index.shape[0]), point_index] = 1.0
        brier[point_identified] = np.sum(
            (probabilities[point_identified] - one_hot) ** 2, axis=1
        )

    zero_probability |= interval_zero_probability

    per_row = {
        "log_score": log_score,
        "log_loss": log_loss,
        "brier": brier,
        "entropy": entropy,
        "interval_probability": interval_probability,
        "interval_log_score": interval_log_score,
        "interval_log_loss": interval_log_loss,
        "point_identified": point_identified,
        "all_class": all_class,
        "no_information": all_class,
        "allowed_class_count": counts.astype(np.int64),
        "zero_probability": zero_probability,
        "interval_zero_probability": interval_zero_probability,
        "log_floor_applied": floor_applied_point | floor_applied_interval,
    }
    return {
        "schema": EVALUATION_VERSION,
        "kind": "categorical_metrics",
        "mode": mode,
        "n_rows": int(n),
        "n_classes": int(k),
        "per_row": per_row,
        "summary": {
            "log_score": _summary_mean(log_score),
            "log_loss": _summary_mean(log_loss),
            "brier": _summary_mean(brier),
            "entropy": _summary_mean(entropy),
            "interval_log_score": _summary_mean(interval_log_score),
            "interval_log_loss": _summary_mean(interval_log_loss),
            "all_class_count": int(np.count_nonzero(all_class)),
            "noinfo_count": int(np.count_nonzero(all_class)),
            "point_identified_count": int(np.count_nonzero(point_identified)),
            "brier_defined_count": int(np.count_nonzero(np.isfinite(brier))),
            "informative_interval_count": int(np.count_nonzero(interval_scored)),
            "zero_probability_count": int(np.count_nonzero(zero_probability)),
            "interval_zero_probability_count": int(np.count_nonzero(interval_zero_probability)),
            "log_floor_applied_count": int(np.count_nonzero(floor_applied_point | floor_applied_interval)),
            "interval_floor_applied_count": int(np.count_nonzero(floor_applied_interval)),
            "log_floor": floor,
        },
        "simplex": simplex,
    }


def _crossing_diagnostics(predictions: np.ndarray) -> dict[str, Any]:
    complete = np.isfinite(predictions).all(axis=2)
    cell_crossing = np.zeros(predictions.shape[:2], dtype=bool)
    if predictions.shape[2] > 1:
        cell_crossing = complete & np.any(predictions[:, :, :-1] > predictions[:, :, 1:], axis=2)
    return {
        "rows": int(predictions.shape[0]),
        "targets": int(predictions.shape[1]),
        "complete_row_target_count": int(np.count_nonzero(complete)),
        "rows_with_crossing": int(np.count_nonzero(np.any(cell_crossing, axis=1))),
        "target_heads_with_crossing": int(np.count_nonzero(cell_crossing)),
        "crossing_cell_count": int(np.count_nonzero(cell_crossing)),
        "missing_row_target_count": int(np.count_nonzero(~complete)),
    }


def _target_matrix(value: Any, *, name: str, target_count: int | None = None) -> np.ndarray:
    array = _finite_array(value, name=name, allow_nan=True)
    if array.ndim == 1:
        array = array.reshape(-1, 1)
    if array.ndim != 2 or array.shape[1] < 1:
        raise EvaluationInputError(f"{name} must have shape (N,T)")
    if target_count is not None and array.shape[1] != target_count:
        raise EvaluationInputError(f"{name} target count differs from predictions")
    return np.ascontiguousarray(array)


def _central_indices(quantiles: np.ndarray, central_interval: Sequence[float] | None) -> tuple[int, int, float, float]:
    if central_interval is None:
        return 0, len(quantiles) - 1, float(quantiles[0]), float(quantiles[-1])
    try:
        levels = tuple(float(v) for v in central_interval)
    except (TypeError, ValueError) as exc:
        raise EvaluationInputError("central_interval must contain two quantile levels") from exc
    if len(levels) != 2 or not all(math.isfinite(v) for v in levels) or not 0 < levels[0] < levels[1] < 1:
        raise EvaluationInputError("central_interval must be two increasing levels in (0,1)")
    matches = []
    for level in levels:
        index = int(np.argmin(np.abs(quantiles - level)))
        if abs(float(quantiles[index]) - level) > 1e-12:
            raise EvaluationInputError("central interval levels must be present in quantiles")
        matches.append(index)
    return matches[0], matches[1], levels[0], levels[1]


def quantile_metrics(
    Y: Any,
    Q: Any,
    quantiles: Sequence[float],
    *,
    final_predictions: Any = None,
    central_interval: Sequence[float] | None = None,
) -> dict[str, Any]:
    """Score target matrix ``Y`` against final quantile predictions ``Q``.

    ``NaN`` target or prediction cells are retained as missing.  Pinball
    losses average over the available heads; coverage reports strict and
    inclusive bounds so exact ties, including zero-atom ties, are visible.
    ``final_predictions`` may be supplied when ``Q`` is a pre-projection fit;
    crossing diagnostics then report both the raw and emitted predictions.
    """
    targets = _target_matrix(Y, name="Y")
    predictions = _finite_array(Q, name="Q", ndim=3, allow_nan=True)
    if predictions.shape[0] != targets.shape[0] or predictions.shape[1] != targets.shape[1]:
        raise EvaluationInputError("Q must have shape (N,T,K) matching Y")
    levels = _quantiles(quantiles)
    if predictions.shape[2] != len(levels):
        raise EvaluationInputError("Q quantile axis differs from quantiles")
    if final_predictions is None:
        emitted = predictions
        final_is_supplied = False
    else:
        emitted = _finite_array(final_predictions, name="final_predictions", ndim=3, allow_nan=True)
        if emitted.shape != predictions.shape:
            raise EvaluationInputError("final_predictions must have the same shape as Q")
        final_is_supplied = True

    n, target_count, q_count = emitted.shape
    valid = np.isfinite(targets)[:, :, None] & np.isfinite(emitted)
    residual = targets[:, :, None] - emitted
    q_grid = levels.reshape(1, 1, -1)
    pinball = np.where(
        valid,
        np.where(residual >= 0.0, q_grid * residual, (q_grid - 1.0) * residual),
        np.nan,
    )
    target_head_count = np.sum(np.isfinite(pinball), axis=2)
    target_head_sum = np.nansum(pinball, axis=2)
    per_target_mean = np.full((n, target_count), np.nan, dtype=np.float64)
    np.divide(target_head_sum, target_head_count, out=per_target_mean, where=target_head_count > 0)
    row_count = np.sum(np.isfinite(per_target_mean), axis=1)
    row_sum = np.nansum(per_target_mean, axis=1)
    per_row_mean = np.full(n, np.nan, dtype=np.float64)
    np.divide(row_sum, row_count, out=per_row_mean, where=row_count > 0)

    coverage_strict = np.full((target_count, q_count), np.nan, dtype=np.float64)
    coverage_inclusive = np.full((target_count, q_count), np.nan, dtype=np.float64)
    coverage_count = np.zeros((target_count, q_count), dtype=np.int64)
    tie_count = np.zeros((target_count, q_count), dtype=np.int64)
    zero_atom_count = np.zeros((target_count, q_count), dtype=np.int64)
    zero_atom_tie_count = np.zeros((target_count, q_count), dtype=np.int64)
    for target_index in range(target_count):
        y = targets[:, target_index]
        for q_index in range(q_count):
            mask = valid[:, target_index, q_index]
            coverage_count[target_index, q_index] = int(np.count_nonzero(mask))
            if not bool(mask.any()):
                continue
            forecast = emitted[:, target_index, q_index]
            values = y[mask]
            forecasts = forecast[mask]
            coverage_strict[target_index, q_index] = float(np.mean(values < forecasts))
            coverage_inclusive[target_index, q_index] = float(np.mean(values <= forecasts))
            ties = values == forecasts
            zeros = values == 0.0
            tie_count[target_index, q_index] = int(np.count_nonzero(ties))
            zero_atom_count[target_index, q_index] = int(np.count_nonzero(zeros))
            zero_atom_tie_count[target_index, q_index] = int(np.count_nonzero(zeros & ties))

    lower_index, upper_index, lower_level, upper_level = _central_indices(levels, central_interval)
    lower_forecast = emitted[:, :, lower_index]
    upper_forecast = emitted[:, :, upper_index]
    interval_valid = np.isfinite(targets) & np.isfinite(lower_forecast) & np.isfinite(upper_forecast)
    interval_width = np.where(interval_valid, upper_forecast - lower_forecast, np.nan)
    interval_inclusive = np.where(
        interval_valid, (targets >= lower_forecast) & (targets <= upper_forecast), False
    )
    interval_strict = np.where(
        interval_valid, (targets > lower_forecast) & (targets < upper_forecast), False
    )
    central_counts = interval_valid.sum(axis=0)
    central_coverage_inclusive = np.full(target_count, np.nan, dtype=np.float64)
    central_coverage_strict = np.full(target_count, np.nan, dtype=np.float64)
    central_width = np.full(target_count, np.nan, dtype=np.float64)
    for target_index in range(target_count):
        if central_counts[target_index]:
            central_coverage_inclusive[target_index] = float(
                interval_inclusive[:, target_index].sum() / central_counts[target_index]
            )
            central_coverage_strict[target_index] = float(
                interval_strict[:, target_index].sum() / central_counts[target_index]
            )
            central_width[target_index] = float(
                np.nansum(interval_width[:, target_index]) / central_counts[target_index]
            )

    raw_crossings = _crossing_diagnostics(predictions)
    final_crossings = _crossing_diagnostics(emitted)
    return {
        "schema": EVALUATION_VERSION,
        "kind": "quantile_metrics",
        "n_rows": int(n),
        "target_count": int(target_count),
        "quantiles": levels,
        "nominal_central_interval": float(upper_level - lower_level),
        "per_row_mean_pinball": per_row_mean,
        "per_target_mean_pinball": np.asarray(
            [_summary_mean(per_target_mean[:, t]) for t in range(target_count)], dtype=np.float64
        ),
        "per_row_target_mean_pinball": per_target_mean,
        "pinball": pinball,
        "q_coverage": {
            "strict": coverage_strict,
            "inclusive": coverage_inclusive,
            "lower_bound": coverage_strict,
            "upper_bound": coverage_inclusive,
            "counts": coverage_count,
            "tie_count": tie_count,
            "zero_atom_count": zero_atom_count,
            "zero_atom_tie_count": zero_atom_tie_count,
        },
        "central_interval": {
            "lower_index": int(lower_index),
            "upper_index": int(upper_index),
            "lower_quantile": float(lower_level),
            "upper_quantile": float(upper_level),
            "coverage_strict": central_coverage_strict,
            "coverage_inclusive": central_coverage_inclusive,
            "coverage_lower_bound": central_coverage_strict,
            "coverage_upper_bound": central_coverage_inclusive,
            "width_mean": central_width,
            "per_row_width": interval_width,
            "valid_counts": central_counts.astype(np.int64),
            "tie_count": np.sum(
                interval_valid & ((targets == lower_forecast) | (targets == upper_forecast)), axis=0
            ).astype(np.int64),
        },
        "crossings": {
            "raw_predictions": raw_crossings,
            "final_predictions": final_crossings,
            "final_predictions_supplied": final_is_supplied,
        },
        "missingness": {
            "target_missing_cells": int(np.count_nonzero(~np.isfinite(targets))),
            "prediction_missing_cells": int(np.count_nonzero(~np.isfinite(emitted))),
            "rows_without_any_valid_target": int(np.count_nonzero(row_count == 0)),
            "target_valid_counts": np.isfinite(targets).sum(axis=0).astype(np.int64),
        },
    }


def _binary_bounds(lower: np.ndarray, upper: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if np.any(lower < 0.0) or np.any(lower > 1.0) or np.any(upper < 0.0) or np.any(upper > 1.0):
        raise EvaluationInputError("binary feasible bounds must lie in [0,1]")
    if np.any(lower > upper):
        raise EvaluationInputError("binary lower bounds cannot exceed upper bounds")
    feasible_zero = lower <= 0.0
    feasible_one = upper >= 1.0
    invalid = ~(feasible_zero | feasible_one)
    if bool(np.any(invalid)):
        raise EvaluationInputError(
            "a binary bound interval contains no feasible endpoint; fractional labels are not substituted"
        )
    return feasible_zero, feasible_one, feasible_zero & feasible_one


def binary_bound_metrics(
    p: Any,
    lower: Any,
    upper: Any,
    *,
    log_floor: float = DEFAULT_LOG_FLOOR,
) -> dict[str, Any]:
    """Return sharp proper-score loss bounds over feasible binary endpoints.

    For a row with ``lower=0`` and ``upper=1``, the score interval is the
    minimum and maximum of the two actual endpoint losses at y=0 and y=1.  No
    fractional label is manufactured.  NaN rows are retained as missing.
    """
    probabilities = _vector(p, name="p", allow_nan=True)
    lows = _vector(lower, name="lower", n=len(probabilities), allow_nan=True)
    highs = _vector(upper, name="upper", n=len(probabilities), allow_nan=True)
    floor = _positive_floor(log_floor)
    finite = np.isfinite(probabilities) & np.isfinite(lows) & np.isfinite(highs)
    if np.any(probabilities[finite] < 0.0) or np.any(probabilities[finite] > 1.0):
        raise EvaluationInputError("probability must lie in [0,1]")
    feasible_zero = np.zeros(len(probabilities), dtype=bool)
    feasible_one = np.zeros(len(probabilities), dtype=bool)
    both = np.zeros(len(probabilities), dtype=bool)
    if bool(finite.any()):
        f0, f1, fb = _binary_bounds(lows[finite], highs[finite])
        feasible_zero[finite], feasible_one[finite], both[finite] = f0, f1, fb
    point = feasible_zero ^ feasible_one
    l0 = -np.log(np.maximum(1.0 - probabilities, floor))
    l1 = -np.log(np.maximum(probabilities, floor))
    b0 = probabilities ** 2
    b1 = (1.0 - probabilities) ** 2
    log_lower = np.full(len(probabilities), np.nan, dtype=np.float64)
    log_upper = np.full(len(probabilities), np.nan, dtype=np.float64)
    brier_lower = np.full(len(probabilities), np.nan, dtype=np.float64)
    brier_upper = np.full(len(probabilities), np.nan, dtype=np.float64)
    for mask, first, second in (
        (both, np.minimum(l0, l1), np.maximum(l0, l1)),
        (feasible_zero & ~both, l0, l0),
        (feasible_one & ~both, l1, l1),
    ):
        log_lower[mask], log_upper[mask] = first[mask], second[mask]
    for mask, first, second in (
        (both, np.minimum(b0, b1), np.maximum(b0, b1)),
        (feasible_zero & ~both, b0, b0),
        (feasible_one & ~both, b1, b1),
    ):
        brier_lower[mask], brier_upper[mask] = first[mask], second[mask]
    floor_count = finite & (
        ((probabilities < floor) & feasible_one)
        | (((1.0 - probabilities) < floor) & feasible_zero)
    )
    return {
        "schema": EVALUATION_VERSION,
        "kind": "binary_bound_metrics",
        "n_rows": int(len(probabilities)),
        "per_row": {
            "log_loss_lower": log_lower,
            "log_loss_upper": log_upper,
            "brier_lower": brier_lower,
            "brier_upper": brier_upper,
            "feasible_zero": feasible_zero,
            "feasible_one": feasible_one,
            "both_endpoints_feasible": both,
            "point_identified": point,
            "log_floor_applied": floor_count,
            "missing": ~finite,
        },
        "summary": {
            "valid_count": int(np.count_nonzero(finite)),
            "missing_count": int(np.count_nonzero(~finite)),
            "point_identified_count": int(np.count_nonzero(point)),
            "both_endpoint_count": int(np.count_nonzero(both)),
            "log_floor": floor,
            "log_floor_endpoint_count": int(np.count_nonzero(floor_count)),
            "log_loss_lower": _summary_mean(log_lower),
            "log_loss_upper": _summary_mean(log_upper),
            "brier_lower": _summary_mean(brier_lower),
            "brier_upper": _summary_mean(brier_upper),
            "fractional_label_used": False,
        },
    }


def _integer_vector(value: Any, *, name: str, n: int | None = None) -> np.ndarray:
    raw = _finite_array(value, name=name, ndim=1, allow_nan=False)
    if np.any(raw != np.floor(raw)):
        raise EvaluationInputError(f"{name} must contain integer IDs")
    if n is not None and len(raw) != n:
        raise EvaluationInputError(f"{name} must have length {n}")
    return raw.astype(np.int64)


def _date_universe(universe: Any, observed_groups: np.ndarray) -> dict[int, np.ndarray]:
    if not isinstance(universe, Mapping):
        raise EvaluationInputError("intended_date_universe must map each group ID to ordered date ordinals")
    try:
        keys = set(int(key) for key in universe)
    except (TypeError, ValueError) as exc:
        raise EvaluationInputError("intended_date_universe keys must be integer group IDs") from exc
    observed = set(int(value) for value in observed_groups.tolist())
    if not observed.issubset(keys):
        raise EvaluationInputError("intended_date_universe must include every observed group ID")
    result: dict[int, np.ndarray] = {}
    for key, values in universe.items():
        group = int(key)
        dates = _integer_vector(values, name=f"intended_date_universe[{group}]")
        if len(dates) == 0 or np.any(dates[1:] <= dates[:-1]):
            raise EvaluationInputError("each intended date universe must be nonempty and strictly ordered")
        result[group] = dates
    return result


def _validate_bootstrap(seed: int, block_length: int, replicates: int,
                        confidence: float, minimum_dates: int, minimum_events: int) -> None:
    if type(seed) is not int:
        raise EvaluationInputError("seed must be an exact integer")
    if type(block_length) is not int or block_length < 1:
        raise EvaluationInputError("block_length must be a positive integer")
    if type(replicates) is not int or not 200 <= replicates <= 20_000:
        raise EvaluationInputError("replicates must be between 200 and 20000")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not .5 < float(confidence) < 1:
        raise EvaluationInputError("confidence must be strictly between .5 and 1")
    if type(minimum_dates) is not int or minimum_dates < 1 or type(minimum_events) is not int or minimum_events < 1:
        raise EvaluationInputError("minimum support thresholds must be positive integers")


def _linear_quantile(values: np.ndarray, level: float) -> float:
    ordered = np.sort(np.asarray(values, dtype=np.float64))
    if ordered.size == 0:
        return float("nan")
    index = (ordered.size - 1) * float(level)
    low = int(math.floor(index))
    high = int(math.ceil(index))
    return float(ordered[low] + (ordered[high] - ordered[low]) * (index - low))


def _moving_weights(date_count: int, *, seed: int, block_length: int,
                    replicates: int) -> np.ndarray | None:
    """Return the reference moving-block occurrence matrix for one date axis.

    The registered date-statistics implementation owns the random-start
    convention.  A small local fallback keeps this array-only module usable in
    an isolated test environment; it is byte-for-byte equivalent in its block
    construction and uses a fresh RNG only once per exact date-universe key.
    """
    if date_count < block_length:
        return None
    try:
        from trading_research.research.date_statistics import _moving_weights as reference_moving_weights
    except (ImportError, ModuleNotFoundError):
        reference_moving_weights = None
    if reference_moving_weights is not None:
        weights, _starts = reference_moving_weights(
            np, date_count, seed=seed, block_length=block_length, replicates=replicates
        )
        return np.asarray(weights, dtype=np.int64)
    rng = random.Random(seed)
    weights = np.zeros((replicates, date_count), dtype=np.int64)
    for row in range(replicates):
        selected: list[int] = []
        while len(selected) < date_count:
            start = rng.randrange(date_count - block_length + 1)
            selected.extend(range(start, start + block_length))
        weights[row, :] = np.bincount(selected[:date_count], minlength=date_count)
    return weights


def _bootstrap_batch(date_values: np.ndarray, date_events: np.ndarray,
                     intended_count: int, names: tuple[str, ...], *,
                     weights: np.ndarray | None, confidence: float,
                     block_length: int, replicates: int, seed: int,
                     minimum_dates: int, minimum_events: int) -> dict[str, dict[str, Any]]:
    """Summarize all metric columns using one shared date-weight matrix.

    ``date_values`` and ``date_events`` have shape ``(M,D)``.  The bootstrap
    uses two matrix products for all M metrics, so it never materializes an
    ``(R,D)`` sampled-value matrix once per metric.
    """
    if date_values.ndim != 2 or date_events.shape != date_values.shape:
        raise EvaluationInputError("internal bootstrap batch shapes differ")
    valid = np.isfinite(date_values)
    valid_dates = valid.sum(axis=1).astype(np.int64)
    observed_events = date_events.sum(axis=1).astype(np.int64)
    estimates = np.full(len(names), np.nan, dtype=np.float64)
    for metric_index in range(len(names)):
        if valid_dates[metric_index]:
            estimates[metric_index] = float(
                date_values[metric_index, valid[metric_index]].mean()
            )
    if weights is None:
        lower = np.full(len(names), np.nan, dtype=np.float64)
        upper = np.full(len(names), np.nan, dtype=np.float64)
        valid_replicates = np.zeros(len(names), dtype=np.int64)
        invalid_replicates = np.zeros(len(names), dtype=np.int64)
    else:
        numerator_values = np.where(valid, date_values, 0.0)
        denominator_values = valid.astype(np.float64)
        numerators = weights @ numerator_values.T
        denominators = weights @ denominator_values.T
        good = denominators > 0.0
        replicate_values = np.full(numerators.shape, np.nan, dtype=np.float64)
        np.divide(numerators, denominators, out=replicate_values, where=good)
        valid_replicates = good.sum(axis=0).astype(np.int64)
        invalid_replicates = np.asarray(replicates - valid_replicates, dtype=np.int64)
        alpha = (1.0 - float(confidence)) / 2.0
        lower = np.full(len(names), np.nan, dtype=np.float64)
        upper = np.full(len(names), np.nan, dtype=np.float64)
        for metric_index in range(len(names)):
            finite_replicates = replicate_values[good[:, metric_index], metric_index]
            lower[metric_index] = _linear_quantile(finite_replicates, alpha)
            upper[metric_index] = _linear_quantile(finite_replicates, 1.0 - alpha)
    results: dict[str, dict[str, Any]] = {}
    for metric_index, name in enumerate(names):
        reasons: list[str] = []
        if valid_dates[metric_index] < minimum_dates:
            reasons.append("fewer_than_minimum_independent_dates")
        if observed_events[metric_index] < minimum_events:
            reasons.append("fewer_than_minimum_events")
        if weights is None:
            reasons.append("fewer_than_one_full_block")
        elif invalid_replicates[metric_index]:
            reasons.append("invalid_bootstrap_denominator_replicates")
        results[name] = {
            "estimate": float(estimates[metric_index]),
            "lower": float(lower[metric_index]),
            "upper": float(upper[metric_index]),
            "valid_dates": int(valid_dates[metric_index]),
            "missing_dates": int(intended_count - valid_dates[metric_index]),
            "valid_events": int(observed_events[metric_index]),
            "support": {
                "independent_dates": int(valid_dates[metric_index]),
                "events": int(observed_events[metric_index]),
                "minimum_independent_dates": int(minimum_dates),
                "minimum_events": int(minimum_events),
                "sparse": bool(reasons),
                "reasons": reasons,
            },
            "bootstrap": {
                "lower": float(lower[metric_index]),
                "upper": float(upper[metric_index]),
                "confidence": float(confidence),
                "replicates": int(replicates),
                "valid_replicates": int(valid_replicates[metric_index]),
                "invalid_replicates": int(invalid_replicates[metric_index]),
                "seed": int(seed),
                "block_length": int(block_length),
                "method": "shared_moving_consecutive_date_block_percentile_bootstrap",
                "circular_end_wrap": False,
            },
        }
    return results


def _reliability_for_rows(probability: np.ndarray, observed: np.ndarray | None,
                          lower: np.ndarray | None, upper: np.ndarray | None,
                          row_indices: np.ndarray, *, edges: tuple[float, ...],
                          dates: np.ndarray | None = None) -> dict[str, Any]:
    p = probability[row_indices]
    if observed is not None:
        valid = np.isfinite(p) & np.isfinite(observed[row_indices])
        y_low = y_high = observed[row_indices]
        calibration_kind = "point"
    else:
        assert lower is not None and upper is not None
        lo = lower[row_indices]
        hi = upper[row_indices]
        valid = np.isfinite(p) & np.isfinite(lo) & np.isfinite(hi)
        y_low, y_high = np.full(len(row_indices), np.nan), np.full(len(row_indices), np.nan)
        feasible_zero = (lo <= 0.0) & (hi >= 0.0)
        feasible_one = (lo <= 1.0) & (hi >= 1.0)
        invalid = valid & ~(feasible_zero | feasible_one)
        if bool(np.any(invalid)):
            raise EvaluationInputError("binary reliability bounds contain no feasible endpoint")
        y_low[valid] = np.where(feasible_one[valid] & ~feasible_zero[valid], 1.0, 0.0)
        y_high[valid] = np.where(feasible_zero[valid] & ~feasible_one[valid], 0.0, 1.0)
        calibration_kind = "interval_bounds"
    p_valid = p[valid]
    y_low_valid = y_low[valid]
    y_high_valid = y_high[valid]
    bin_index = np.minimum((p_valid * 10.0).astype(np.int64), 9)
    cells = []
    ece_lower = 0.0
    ece_upper = 0.0
    total = len(p_valid)
    for index in range(10):
        selected = bin_index == index
        count = int(np.count_nonzero(selected))
        if count == 0:
            cells.append({"lower": edges[index], "upper": edges[index + 1], "count": 0,
                          "dates": 0, "mean_probability": None,
                          "observed_rate": None, "observed_rate_lower": None,
                          "observed_rate_upper": None, "ece_lower": None, "ece_upper": None})
            continue
        mean_p = float(np.mean(p_valid[selected]))
        rate_low = float(np.mean(y_low_valid[selected]))
        rate_high = float(np.mean(y_high_valid[selected]))
        cell_low = max(0.0, rate_low - mean_p, mean_p - rate_high)
        cell_high = max(abs(mean_p - rate_low), abs(mean_p - rate_high))
        ece_lower += count * cell_low
        ece_upper += count * cell_high
        cell_dates = (
            int(len(np.unique(dates[row_indices[valid][selected]])))
            if dates is not None else int(len(set(row_indices[valid][selected].tolist())))
        )
        cells.append({
            "lower": edges[index], "upper": edges[index + 1], "count": count,
            "dates": cell_dates,
            "mean_probability": mean_p,
            "observed_rate": rate_low if calibration_kind == "point" else None,
            "observed_rate_lower": rate_low,
            "observed_rate_upper": rate_high,
            "ece_lower": cell_low,
            "ece_upper": cell_high,
        })
    return {
        "kind": calibration_kind,
        "bins": cells,
        "ece": ece_lower / total if total and calibration_kind == "point" else float("nan"),
        "ece_lower": ece_lower / total if total else float("nan"),
        "ece_upper": ece_upper / total if total else float("nan"),
        "valid_count": int(total),
        "missing_count": int(len(row_indices) - total),
        "fractional_label_used": False,
        "edges": edges,
    }


def grouped_date_evaluation(
    metrics: Mapping[str, Any],
    dates: Any,
    groups: Any,
    intended_date_universe: Mapping[int, Sequence[int]],
    *,
    paired: Mapping[str, Any] | None = None,
    paired_candidate: Any = None,
    paired_baseline: Any = None,
    probability: Any = None,
    observed_binary: Any = None,
    lower: Any = None,
    upper: Any = None,
    probability_matrix: Any = None,
    observed_binary_matrix: Any = None,
    lower_matrix: Any = None,
    upper_matrix: Any = None,
    seed: int = DEFAULT_SEED,
    block_length: int = DEFAULT_BLOCK_LENGTH,
    replicates: int = DEFAULT_REPLICATES,
    confidence: float = DEFAULT_CONFIDENCE,
    minimum_dates: int = DEFAULT_MINIMUM_DATES,
    minimum_events: int = DEFAULT_MINIMUM_EVENTS,
    calibration_edges: Sequence[float] = DEFAULT_CALIBRATION_EDGES,
) -> dict[str, Any]:
    """Evaluate all supplied per-row metrics by group and intended date set.

    Rows are sorted once by ``(group, date)``.  All metric cells, paired gains,
    and reliability rows are then assembled from those contiguous slices; no
    metric performs an independent full-population scan per group.  Each group
    receives one shared moving-block bootstrap matrix so metric and paired
    confidence intervals preserve same-date dependence.
    """
    if not isinstance(metrics, Mapping) or not metrics:
        raise EvaluationInputError("metrics must be a nonempty name-to-array mapping")
    _validate_bootstrap(seed, block_length, replicates, confidence, minimum_dates, minimum_events)
    metric_names = tuple(metrics)
    if any(not isinstance(name, str) or not name for name in metric_names) or len(set(metric_names)) != len(metric_names):
        raise EvaluationInputError("metric names must be unique nonempty strings")
    date_array = _integer_vector(dates, name="dates")
    group_array = _integer_vector(groups, name="groups", n=len(date_array))
    n = len(date_array)
    if n == 0:
        raise EvaluationInputError("at least one row is required")
    metric_arrays = {
        name: _vector(value, name=f"metrics[{name}]", n=n, allow_nan=True)
        for name, value in metrics.items()
    }
    if paired is not None:
        if not isinstance(paired, Mapping) or set(paired) != {"candidate", "baseline"}:
            raise EvaluationInputError("paired must contain exactly candidate and baseline arrays")
        if paired_candidate is not None or paired_baseline is not None:
            raise EvaluationInputError("supply paired or paired_candidate/paired_baseline, not both")
        paired_candidate = paired["candidate"]
        paired_baseline = paired["baseline"]
    if (paired_candidate is None) != (paired_baseline is None):
        raise EvaluationInputError("paired_candidate and paired_baseline must be supplied together")
    candidate = baseline = None
    if paired_candidate is not None:
        candidate = _vector(paired_candidate, name="paired_candidate", n=n, allow_nan=True)
        baseline = _vector(paired_baseline, name="paired_baseline", n=n, allow_nan=True)

    reliability_enabled = probability is not None or observed_binary is not None or lower is not None or upper is not None
    if reliability_enabled and probability is None:
        raise EvaluationInputError("probability is required for reliability metrics")
    matrix_reliability_enabled = (
        probability_matrix is not None or observed_binary_matrix is not None
        or lower_matrix is not None or upper_matrix is not None
    )
    if matrix_reliability_enabled and probability_matrix is None:
        raise EvaluationInputError("probability_matrix is required for classwise reliability metrics")
    if matrix_reliability_enabled and reliability_enabled:
        raise EvaluationInputError("supply scalar or classwise reliability inputs, not both")
    probabilities = _vector(probability, name="probability", n=n, allow_nan=True) if probability is not None else None
    if probabilities is not None:
        finite_probability = probabilities[np.isfinite(probabilities)]
        if np.any(finite_probability < 0.0) or np.any(finite_probability > 1.0):
            raise EvaluationInputError("reliability probabilities must lie in [0,1]")
    if observed_binary is not None and (lower is not None or upper is not None):
        raise EvaluationInputError("supply observed_binary or lower/upper bounds, not both")
    observed = _vector(observed_binary, name="observed_binary", n=n, allow_nan=True) if observed_binary is not None else None
    if observed is not None:
        valid_observed = np.isfinite(observed)
        if np.any(observed[valid_observed] != np.floor(observed[valid_observed])) or np.any((observed[valid_observed] < 0) | (observed[valid_observed] > 1)):
            raise EvaluationInputError("observed_binary must contain only 0/1 labels or NaN")
    bound_lower = bound_upper = None
    if lower is not None or upper is not None:
        if lower is None or upper is None:
            raise EvaluationInputError("lower and upper reliability bounds are both required")
        bound_lower = _vector(lower, name="lower", n=n, allow_nan=True)
        bound_upper = _vector(upper, name="upper", n=n, allow_nan=True)
        finite_bounds = np.isfinite(bound_lower) & np.isfinite(bound_upper)
        finite_lower = np.isfinite(bound_lower)
        finite_upper = np.isfinite(bound_upper)
        if np.any(bound_lower[finite_lower] < 0.0) or np.any(bound_lower[finite_lower] > 1.0):
            raise EvaluationInputError("lower reliability bounds must lie in [0,1]")
        if np.any(bound_upper[finite_upper] < 0.0) or np.any(bound_upper[finite_upper] > 1.0):
            raise EvaluationInputError("upper reliability bounds must lie in [0,1]")
        if np.any(bound_lower[finite_bounds] > bound_upper[finite_bounds]):
            raise EvaluationInputError("lower reliability bounds cannot exceed upper bounds")

    probability_matrix_array = None
    observed_matrix_array = None
    lower_matrix_array = upper_matrix_array = None
    if matrix_reliability_enabled:
        probability_matrix_array = _finite_array(
            probability_matrix, name="probability_matrix", ndim=2, allow_nan=True
        )
        if probability_matrix_array.shape[0] != n or probability_matrix_array.shape[1] < 1:
            raise EvaluationInputError("probability_matrix must have shape (N,K) with K >= 1")
        finite_probability_matrix = probability_matrix_array[np.isfinite(probability_matrix_array)]
        if np.any(finite_probability_matrix < 0.0) or np.any(finite_probability_matrix > 1.0):
            raise EvaluationInputError("classwise reliability probabilities must lie in [0,1]")
        if observed_binary_matrix is not None and (lower_matrix is not None or upper_matrix is not None):
            raise EvaluationInputError("supply observed_binary_matrix or lower_matrix/upper_matrix, not both")
        if observed_binary_matrix is not None:
            observed_matrix_array = _finite_array(
                observed_binary_matrix, name="observed_binary_matrix", ndim=2, allow_nan=True
            )
            if observed_matrix_array.shape != probability_matrix_array.shape:
                raise EvaluationInputError("observed_binary_matrix must match probability_matrix shape")
            valid_observed_matrix = np.isfinite(observed_matrix_array)
            if np.any(observed_matrix_array[valid_observed_matrix] != np.floor(observed_matrix_array[valid_observed_matrix])) or np.any(
                (observed_matrix_array[valid_observed_matrix] < 0)
                | (observed_matrix_array[valid_observed_matrix] > 1)
            ):
                raise EvaluationInputError("observed_binary_matrix must contain only 0/1 labels or NaN")
        elif lower_matrix is not None or upper_matrix is not None:
            if lower_matrix is None or upper_matrix is None:
                raise EvaluationInputError("lower_matrix and upper_matrix are both required")
            lower_matrix_array = _finite_array(
                lower_matrix, name="lower_matrix", ndim=2, allow_nan=True
            )
            upper_matrix_array = _finite_array(
                upper_matrix, name="upper_matrix", ndim=2, allow_nan=True
            )
            if lower_matrix_array.shape != probability_matrix_array.shape or upper_matrix_array.shape != probability_matrix_array.shape:
                raise EvaluationInputError("classwise reliability bounds must match probability_matrix shape")
            finite_lower_matrix = np.isfinite(lower_matrix_array)
            finite_upper_matrix = np.isfinite(upper_matrix_array)
            finite_bounds_matrix = finite_lower_matrix & finite_upper_matrix
            if np.any(lower_matrix_array[finite_lower_matrix] < 0.0) or np.any(lower_matrix_array[finite_lower_matrix] > 1.0):
                raise EvaluationInputError("lower_matrix reliability bounds must lie in [0,1]")
            if np.any(upper_matrix_array[finite_upper_matrix] < 0.0) or np.any(upper_matrix_array[finite_upper_matrix] > 1.0):
                raise EvaluationInputError("upper_matrix reliability bounds must lie in [0,1]")
            if np.any(lower_matrix_array[finite_bounds_matrix] > upper_matrix_array[finite_bounds_matrix]):
                raise EvaluationInputError("lower_matrix reliability bounds cannot exceed upper_matrix bounds")
        else:
            raise EvaluationInputError("classwise reliability labels or bounds are required")

    try:
        edges = tuple(float(v) for v in calibration_edges)
    except (TypeError, ValueError) as exc:
        raise EvaluationInputError("calibration_edges must be numeric") from exc
    if len(edges) != len(DEFAULT_CALIBRATION_EDGES) or any(
        not math.isfinite(v) or abs(v - expected) > 1e-12
        for v, expected in zip(edges, DEFAULT_CALIBRATION_EDGES)
    ):
        raise EvaluationInputError("calibration_edges are fixed at 0,.1,...,1")

    order = np.lexsort((date_array, group_array))
    sorted_groups = group_array[order]
    sorted_dates = date_array[order]
    boundary = np.flatnonzero(
        (np.r_[True, sorted_groups[1:] != sorted_groups[:-1]]) |
        (np.r_[True, sorted_dates[1:] != sorted_dates[:-1]])
    )
    ends = np.r_[boundary[1:], len(order)]
    group_rows: dict[int, list[np.ndarray]] = {}
    group_date_cells: dict[int, dict[int, np.ndarray]] = {}
    for start, end in zip(boundary.tolist(), ends.tolist(), strict=True):
        group = int(sorted_groups[start])
        day = int(sorted_dates[start])
        group_date_cells.setdefault(group, {})[day] = order[start:end]
        group_rows.setdefault(group, []).append(order[start:end])
    universes = _date_universe(intended_date_universe, group_array)
    # Cache by the exact ordered date universe, rather than by group or loop
    # order.  The bound keeps memory predictable when a study has many sparse
    # group calendars; an evicted key is regenerated from the same seed.
    weight_cache: dict[tuple[int, ...], np.ndarray | None] = {}
    # Probability-bin membership depends only on the already supplied rows,
    # not on the reporting group. Compute it once, retaining every invalid
    # row as -1. Per-date means below use the exact same ordered row indices.
    class_bin_indices = []
    if probability_matrix_array is not None:
        for class_index in range(probability_matrix_array.shape[1]):
            p_column = probability_matrix_array[:, class_index]
            if observed_matrix_array is not None:
                low_column = high_column = observed_matrix_array[:, class_index]
            else:
                low_column = lower_matrix_array[:, class_index]
                high_column = upper_matrix_array[:, class_index]
            finite = np.isfinite(p_column) & np.isfinite(low_column) & np.isfinite(high_column)
            bins = np.full(n, -1, dtype=np.int8)
            bins[finite] = np.minimum((p_column[finite] * 10.0).astype(np.int64), 9)
            class_bin_indices.append(bins)
    group_results: dict[str, Any] = {}
    for group in sorted(universes):
        intended = universes[group]
        intended_tuple = tuple(int(v) for v in intended.tolist())
        date_cells = group_date_cells.get(group, {})
        rows_for_group = group_rows.get(group, [])
        if intended_tuple not in weight_cache:
            if len(weight_cache) >= 8:
                weight_cache.pop(next(iter(weight_cache)))
            weight_cache[intended_tuple] = _moving_weights(
                len(intended_tuple), seed=seed, block_length=block_length,
                replicates=replicates,
            )
        weights = weight_cache[intended_tuple]
        day_index = {day: index for index, day in enumerate(intended_tuple)}
        batch_names = metric_names + (("__paired_gain__",) if candidate is not None else ())
        date_values_batch = np.full((len(batch_names), len(intended_tuple)), np.nan, dtype=np.float64)
        date_events_batch = np.zeros((len(batch_names), len(intended_tuple)), dtype=np.int64)
        baseline_values_by_date = np.full(len(intended_tuple), np.nan, dtype=np.float64)
        candidate_values_by_date = np.full(len(intended_tuple), np.nan, dtype=np.float64)
        for day, row_indices in date_cells.items():
            index = day_index.get(day)
            if index is None:
                raise EvaluationInputError("observed date lies outside its intended group universe")
            metric_values = np.asarray(
                [metric_arrays[name][row_indices] for name in metric_names], dtype=np.float64
            )
            finite = np.isfinite(metric_values)
            counts = finite.sum(axis=1).astype(np.int64)
            sums = np.where(finite, metric_values, 0.0).sum(axis=1, dtype=np.float64)
            means = np.full(len(metric_names), np.nan, dtype=np.float64)
            np.divide(sums, counts, out=means, where=counts > 0)
            date_values_batch[:len(metric_names), index] = means
            date_events_batch[:len(metric_names), index] = counts
            if candidate is not None and baseline is not None:
                candidate_values = candidate[row_indices]
                baseline_values = baseline[row_indices]
                pair_finite = np.isfinite(candidate_values) & np.isfinite(baseline_values)
                pair_count = int(np.count_nonzero(pair_finite))
                if pair_count:
                    date_values_batch[-1, index] = float(
                        np.mean(baseline_values[pair_finite] - candidate_values[pair_finite])
                    )
                    date_events_batch[-1, index] = pair_count
                    baseline_values_by_date[index] = float(np.mean(baseline_values[pair_finite]))
                    candidate_values_by_date[index] = float(np.mean(candidate_values[pair_finite]))

        # Classwise calibration cells are appended to the same date-level
        # batch as ordinary metrics and paired gains.  This gives every class
        # and probability bin the same moving-block bootstrap weights without
        # starting a new bootstrap for each class.
        if probability_matrix_array is not None:
            group_indices = np.concatenate(rows_for_group) if rows_for_group else np.asarray([], dtype=np.int64)
            group_date_indices = np.searchsorted(intended, date_array[group_indices])
            for class_index in range(probability_matrix_array.shape[1]):
                p_column = probability_matrix_array[:, class_index]
                if observed_matrix_array is not None:
                    low_column = high_column = observed_matrix_array[:, class_index]
                else:
                    assert lower_matrix_array is not None and upper_matrix_array is not None
                    low_column = lower_matrix_array[:, class_index]
                    high_column = upper_matrix_array[:, class_index]
                bins = class_bin_indices[class_index][group_indices]
                usable = bins >= 0
                codes = group_date_indices[usable] * 10 + bins[usable]
                selected_rows = group_indices[usable]
                order_within_cells = np.argsort(codes, kind='stable')
                codes, selected_rows = codes[order_within_cells], selected_rows[order_within_cells]
                p_values = np.full((10, len(intended_tuple)), np.nan, dtype=np.float64)
                low_values, high_values = p_values.copy(), p_values.copy()
                counts = np.zeros((10, len(intended_tuple)), dtype=np.int64)
                if len(codes):
                    starts = np.r_[0, np.flatnonzero(np.diff(codes)) + 1]
                    cell_ends = np.r_[starts[1:], len(codes)]
                    for first, last in zip(starts, cell_ends, strict=True):
                        date_index, bin_index = divmod(int(codes[first]), 10)
                        count = int(last - first)
                        if count == 1:
                            row_index = selected_rows[first]
                            p_values[bin_index, date_index] = p_column[row_index]
                            low_values[bin_index, date_index] = low_column[row_index]
                            high_values[bin_index, date_index] = high_column[row_index]
                        else:
                            # Stable grouping keeps exactly the old mean's
                            # ordered rows, including multiple events/date.
                            rows = selected_rows[first:last]
                            p_values[bin_index, date_index] = float(np.mean(p_column[rows]))
                            low_values[bin_index, date_index] = float(np.mean(low_column[rows]))
                            high_values[bin_index, date_index] = float(np.mean(high_column[rows]))
                        counts[bin_index, date_index] = count
                values = np.stack((p_values, low_values, high_values), axis=1).reshape(30, len(intended_tuple))
                date_values_batch = np.vstack((date_values_batch, values))
                date_events_batch = np.vstack((date_events_batch, np.repeat(counts, 3, axis=0)))
                batch_names += tuple(f"__calibration__class_{class_index}__bin_{bin_index}__{field}"
                                     for bin_index in range(10)
                                     for field in ('predicted_mean', 'outcome_lower', 'outcome_upper'))

        batch_results = _bootstrap_batch(
            date_values_batch, date_events_batch, len(intended_tuple), batch_names,
            weights=weights, confidence=float(confidence), block_length=block_length,
            replicates=replicates, seed=seed, minimum_dates=minimum_dates,
            minimum_events=minimum_events,
        )
        actual_row_count = int(sum(len(rows) for rows in rows_for_group))
        metric_results: dict[str, Any] = {}
        for metric_index, name in enumerate(metric_names):
            metric_result = batch_results[name]
            metric_result["intended_dates"] = intended_tuple
            metric_result["actual_row_count"] = actual_row_count
            metric_result["missing_event_count"] = int(actual_row_count - metric_result["valid_events"])
            metric_result["date_values"] = date_values_batch[metric_index]
            metric_results[name] = metric_result

        paired_result = None
        if candidate is not None and baseline is not None:
            pair_result = batch_results["__paired_gain__"]
            pair_date_values = date_values_batch[batch_names.index("__paired_gain__")]
            baseline_estimate = _summary_mean(baseline_values_by_date)
            pair_result.update({
                "gain_definition": "baseline_minus_candidate_loss",
                "baseline_estimate": baseline_estimate,
                "candidate_estimate": _summary_mean(candidate_values_by_date),
                "relative_gain": (
                    pair_result["estimate"] / abs(baseline_estimate)
                    if math.isfinite(pair_result["estimate"]) and math.isfinite(baseline_estimate) and baseline_estimate != 0.0
                    else float("nan")
                ),
                "one_percent_relative_gain_threshold": 0.01,
                "date_values": pair_date_values,
                "missing_pair_event_count": int(actual_row_count - pair_result["valid_events"]),
            })
            paired_result = pair_result

        reliability = None
        if probabilities is not None and (observed is not None or bound_lower is not None):
            rows = np.concatenate(rows_for_group) if rows_for_group else np.asarray([], dtype=np.int64)
            reliability = _reliability_for_rows(
                probabilities, observed, bound_lower, bound_upper, rows, edges=edges, dates=date_array
            )

        classwise_calibration = None
        if probability_matrix_array is not None:
            rows = np.concatenate(rows_for_group) if rows_for_group else np.asarray([], dtype=np.int64)
            classwise_calibration = {}
            for class_index in range(probability_matrix_array.shape[1]):
                if observed_matrix_array is not None:
                    low_column = high_column = observed_matrix_array[:, class_index]
                    class_result = _reliability_for_rows(
                        probability_matrix_array[:, class_index],
                        observed_matrix_array[:, class_index], None, None,
                        rows, edges=edges, dates=date_array,
                    )
                else:
                    assert lower_matrix_array is not None and upper_matrix_array is not None
                    low_column = lower_matrix_array[:, class_index]
                    high_column = upper_matrix_array[:, class_index]
                    class_result = _reliability_for_rows(
                        probability_matrix_array[:, class_index], None,
                        low_column, high_column, rows, edges=edges,
                        dates=date_array,
                    )
                for bin_index, cell in enumerate(class_result["bins"]):
                    prefix = f"__calibration__class_{class_index}__bin_{bin_index}__"
                    predicted = batch_results[prefix + "predicted_mean"]
                    outcome_lower = batch_results[prefix + "outcome_lower"]
                    outcome_upper = batch_results[prefix + "outcome_upper"]
                    # The primary cell estimand is equal-date, matching the
                    # bootstrap point estimate.  Preserve pooled-row values
                    # separately for auditability when dates have unequal row
                    # multiplicity.
                    cell["row_weighted_predicted_mean"] = cell["mean_probability"]
                    cell["row_weighted_outcome_lower"] = cell["observed_rate_lower"]
                    cell["row_weighted_outcome_upper"] = cell["observed_rate_upper"]
                    cell["predicted_mean"] = predicted["estimate"]
                    cell["outcome_lower"] = outcome_lower["estimate"]
                    cell["outcome_upper"] = outcome_upper["estimate"]
                    cell["dates"] = predicted["valid_dates"]
                    cell["date_bootstrap"] = {
                        "predicted_mean": predicted,
                        "outcome_lower": outcome_lower,
                        "outcome_upper": outcome_upper,
                        "shared_weights": True,
                    }
                class_result["class_index"] = int(class_index)
                class_result["estimand"] = "equal_date"
                class_result["bootstrap_policy"] = "all class/bin cells share one moving date-block weight matrix"
                classwise_calibration[str(class_index)] = class_result

        group_results[str(group)] = {
            "group_id": group,
            "intended_dates": intended_tuple,
            "actual_dates_with_rows": int(len(date_cells)),
            "missing_intended_dates": int(len(intended_tuple) - len(date_cells)),
            "actual_row_count": int(sum(len(rows) for rows in rows_for_group)),
            "metrics": metric_results,
            "paired": paired_result,
            "reliability": reliability,
            "calibration_by_class": classwise_calibration,
            "calibration": classwise_calibration,
        }

    return {
        "schema": EVALUATION_VERSION,
        "kind": "grouped_date_evaluation",
        "groups": group_results,
        "group_count": int(len(group_results)),
        "row_count": int(n),
        "metric_names": metric_names,
        "configuration": {
            "seed": int(seed),
            "block_length": int(block_length),
            "replicates": int(replicates),
            "confidence": float(confidence),
            "minimum_independent_dates": int(minimum_dates),
            "minimum_events": int(minimum_events),
            "bootstrap_method": "moving_consecutive_date_block_percentile_bootstrap",
            "bootstrap_weight_convention": "date_statistics._moving_weights",
            "bootstrap_weight_cache_key": "exact_ordered_intended_date_tuple",
            "bootstrap_weight_cache_limit": 8,
            "circular_end_wrap": False,
            "date_estimand": "equal_date",
            "row_subsampling": False,
            "calibration_edges": edges,
            "classwise_calibration": probability_matrix_array is not None,
            "classwise_calibration_bootstrap": "one shared moving date-block weight matrix across every class/bin cell",
        },
        "missingness": {
            "groups_with_no_observed_rows": int(sum(len(group_date_cells.get(group, {})) == 0 for group in universes)),
            "metric_missing_cells": {
                name: int(np.count_nonzero(~np.isfinite(metric_arrays[name]))) for name in metric_names
            },
        },
        "calibration_policy": {
            "point_labels_or_binary_endpoint_bounds_only": True,
            "fractional_labels_used": False,
            "training_calibration_claim": False,
            "chronological_maturity_boundaries": "supplied and enforced by the caller/root study; this array scorer does not infer them",
        },
    }


__all__ = [
    "DEFAULT_CALIBRATION_EDGES",
    "DEFAULT_BLOCK_LENGTH",
    "DEFAULT_CONFIDENCE",
    "DEFAULT_LOG_FLOOR",
    "DEFAULT_MINIMUM_DATES",
    "DEFAULT_MINIMUM_EVENTS",
    "DEFAULT_REPLICATES",
    "DEFAULT_SEED",
    "EVALUATION_VERSION",
    "EvaluationInputError",
    "binary_bound_metrics",
    "categorical_metrics",
    "grouped_date_evaluation",
    "quantile_metrics",
]
