"""Small, serializable numerical backends for the Jumbo Context heads.

This module intentionally owns only numerical fitting and prediction.  Arrow
admission, causal folds, target construction, artifact storage, and research
reports remain in the caller.  Every fit record keeps explicit convergence or
fallback state so a numerical failure cannot be mistaken for a model result.

The declared provider baseline for the registered family is NumPy 2.3.3 and
SciPy 1.16.2.  The imports are intentionally ordinary provider imports: the
worker environment is responsible for enforcing the registered lockfile.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import base64
import hashlib
import json
import math
import pickle
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.optimize import minimize


NUMPY_PROVIDER = "2.3.3"
SCIPY_PROVIDER = "1.16.2"
SKLEARN_PROVIDER = "1.7.2"
_LOG_EPS = 1e-15
_HGB_MISSING_CLASS_PRIOR = 1e-12


class BackendInputError(ValueError):
    """Malformed or non-finite numerical input."""


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return [_jsonable(v) for v in value.tolist()]
    if isinstance(value, np.generic):
        return _jsonable(value.item())
    if isinstance(value, tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, float):
        if not math.isfinite(value):
            raise TypeError("non-finite values are not JSON serializable")
        return value
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise TypeError(f"value is not JSON serializable: {type(value).__name__}")


def _metadata(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise BackendInputError("metadata must be a mapping")
    result = _jsonable(dict(value))
    if not isinstance(result, dict):  # pragma: no cover - guarded by _jsonable
        raise BackendInputError("metadata must serialize as an object")
    return result


def _array_digest(*arrays: Any) -> str:
    h = hashlib.sha256()
    for value in arrays:
        array = np.ascontiguousarray(np.asarray(value))
        h.update(str(array.dtype).encode("ascii"))
        h.update(str(array.shape).encode("ascii"))
        h.update(array.tobytes(order="C"))
    return h.hexdigest()


def _matrix(X: Any, *, name: str = "X", allow_empty: bool = True) -> np.ndarray:
    try:
        array = np.asarray(X, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise BackendInputError(f"{name} must be a numeric matrix") from exc
    if array.ndim != 2 or (not allow_empty and array.shape[0] == 0):
        raise BackendInputError(f"{name} must be a two-dimensional matrix")
    if not np.isfinite(array).all():
        raise BackendInputError(f"{name} contains non-finite values")
    return np.ascontiguousarray(array)


def _vector(values: Any, n: int, *, name: str, dtype: Any = np.float64) -> np.ndarray:
    try:
        array = np.asarray(values, dtype=dtype)
    except (TypeError, ValueError) as exc:
        raise BackendInputError(f"{name} must be a vector") from exc
    if array.ndim != 1 or array.shape[0] != n:
        raise BackendInputError(f"{name} must have length {n}")
    if dtype is not bool and not np.isfinite(array).all():
        raise BackendInputError(f"{name} contains non-finite values")
    return np.ascontiguousarray(array)


def _weights(values: Any, n: int) -> np.ndarray:
    if values is None:
        return np.ones(n, dtype=np.float64)
    result = _vector(values, n, name="weights")
    if np.any(result < 0):
        raise BackendInputError("weights must be nonnegative")
    total = float(result.sum())
    if n and (not math.isfinite(total) or not total > 0):
        raise BackendInputError("positive total weight required")
    return result


def _batch_slices(n: int, batch_size: int):
    _validate_batch_size(batch_size)
    for start in range(0, n, batch_size):
        yield slice(start, min(n, start + batch_size))


def _validate_batch_size(batch_size: int) -> None:
    if type(batch_size) is not int or not 1 <= batch_size <= 1_000_000:
        raise BackendInputError("batch_size must be a positive bounded integer")


def _classes(classes: Sequence[Any]) -> tuple[Any, ...]:
    if isinstance(classes, (str, bytes)):
        raise BackendInputError("classes must be a nonempty sequence")
    try:
        result = tuple(classes)
        unique_count = len(set(result))
    except (TypeError, ValueError) as exc:
        raise BackendInputError("classes must be a hashable sequence") from exc
    if not result or unique_count != len(result):
        raise BackendInputError("classes must be nonempty and unique")
    try:
        json.dumps(_jsonable(result), sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise BackendInputError("classes must be JSON-serializable scalars") from exc
    return result


def _softmax(logits: np.ndarray) -> np.ndarray:
    if logits.shape[0] == 0:
        return np.empty_like(logits, dtype=np.float64)
    return np.exp(logits - _logsumexp_rows(logits))


def _logsumexp_rows(values: np.ndarray) -> np.ndarray:
    """Stable row-wise log-sum-exp for finite logits."""
    if values.shape[0] == 0:
        return np.empty((0, 1), dtype=np.float64)
    maximum = np.max(values, axis=1, keepdims=True)
    return maximum + np.log(np.exp(values - maximum).sum(axis=1, keepdims=True))


def _logsumexp_allowed(values: np.ndarray, allowed: np.ndarray) -> np.ndarray:
    if values.shape[0] == 0:
        return np.empty((0, 1), dtype=np.float64)
    if allowed.ndim != 2 or allowed.shape != values.shape or np.any(allowed.sum(axis=1) == 0):
        raise BackendInputError("allowed classes must match finite logits and have positive row mass")
    masked = np.where(allowed, values, -np.inf)
    maximum = np.max(masked, axis=1, keepdims=True)
    return maximum + np.log(np.exp(masked - maximum).sum(axis=1, keepdims=True))


def _sigmoid(values: np.ndarray) -> np.ndarray:
    positive = values >= 0
    result = np.empty_like(values, dtype=np.float64)
    result[positive] = 1.0 / (1.0 + np.exp(-values[positive]))
    exp_values = np.exp(values[~positive])
    result[~positive] = exp_values / (1.0 + exp_values)
    return result


def _validate_quantile_levels(values: Sequence[Any]) -> tuple[float, ...]:
    result = tuple(float(v) for v in values)
    if (not result or any(not math.isfinite(q) or not 0 < q < 1 for q in result)
            or any(a >= b for a, b in zip(result, result[1:]))):
        raise BackendInputError("quantiles must be strictly increasing in (0,1)")
    return result


def offset_array_checksum(value: Any) -> str:
    """Return the canonical checksum required for a per-call baseline array."""
    try:
        array = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise BackendInputError("offset_array must be a finite numeric array") from exc
    if array.ndim not in {2, 3} or not np.isfinite(array).all():
        raise BackendInputError("offset_array must be a finite two- or three-dimensional array")
    return _array_digest(np.ascontiguousarray(array))


def _offset_checksum(array: np.ndarray) -> str:
    """Checksum one concrete baseline array without coupling it to row IDs.

    A fit stores the checksum of the training call for auditability.  A
    prediction call may provide a different number of rows, so prediction
    validates only shape and the optional caller-supplied checksum; it does
    not require the training and prediction arrays to be byte-identical.
    """
    return _array_digest(array)


def _validate_call_checksum(array: np.ndarray, supplied: str | None) -> str:
    digest = _offset_checksum(array)
    if supplied is not None and (not isinstance(supplied, str) or supplied != digest):
        raise BackendInputError("offset checksum does not match the supplied baseline array")
    return digest


def _label_matrix(y: Any, n: int, classes: tuple[Any, ...]) -> tuple[np.ndarray, str]:
    """Return a boolean allowed-class matrix and its declared mode.

    A one-dimensional vector represents exact observed classes.  A two-
    dimensional boolean matrix represents compatible classes for a coarse or
    interval observation.  Rows allowing every class are uninformative and
    are excluded from the likelihood while remaining in diagnostics.
    """
    k = len(classes)
    raw = np.asarray(y)
    if raw.ndim == 1:
        if raw.shape[0] != n:
            raise BackendInputError(f"y must have length {n}")
        indices = []
        lookup = {value: index for index, value in enumerate(classes)}
        for value in raw.tolist():
            if value not in lookup:
                raise BackendInputError("y contains a class outside classes")
            indices.append(lookup[value])
        allowed = np.zeros((n, k), dtype=bool)
        if n:
            allowed[np.arange(n), np.asarray(indices, dtype=np.int64)] = True
        return allowed, "exact_class"
    if raw.ndim == 2 and raw.shape == (n, k) and raw.dtype == np.dtype(bool):
        allowed = np.ascontiguousarray(raw, dtype=bool)
        if np.any(allowed.sum(axis=1) == 0):
            raise BackendInputError("each allowed-class row needs at least one class")
        return allowed, "allowed_class_set"
    raise BackendInputError("y must be an exact class vector or boolean allowed-class matrix")


def _allowed_counts(allowed: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, int, float]:
    informative = allowed.sum(axis=1) < allowed.shape[1]
    counts = np.zeros(allowed.shape[1], dtype=np.float64)
    if informative.any():
        counts = (allowed[informative].astype(np.float64) * weights[informative, None]).sum(axis=0)
    return counts, int((~informative).sum()), float(weights[informative].sum())


def _softmax_objective_gradient(
    X: np.ndarray,
    allowed: np.ndarray,
    weights: np.ndarray,
    theta: np.ndarray,
    *,
    l2: float,
    batch_size: int,
    offset_logits: np.ndarray | None = None,
) -> tuple[float, np.ndarray]:
    """Weighted allowed-set cross-entropy and its coefficient-only-L2 gradient."""
    n, p = X.shape
    k = allowed.shape[1]
    parameters = np.asarray(theta, dtype=np.float64).reshape(k, p + 1)
    intercept, coefficients = parameters[:, 0], parameters[:, 1:]
    informative_weight = float(weights[allowed.sum(axis=1) < k].sum())
    if informative_weight <= 0:
        return float(0.5 * l2 * np.sum(coefficients * coefficients)), np.zeros_like(theta)
    loss = 0.0
    gradient_intercept = np.zeros(k, dtype=np.float64)
    gradient_coefficients = np.zeros((k, p), dtype=np.float64)
    for part in _batch_slices(n, batch_size):
        x_part = X[part]
        w_part = weights[part]
        allowed_part = allowed[part]
        informative = allowed_part.sum(axis=1) < k
        if not informative.any():
            continue
        logits = x_part @ coefficients.T + intercept
        if offset_logits is not None:
            logits = logits + offset_logits[part]
        log_normalizer = _logsumexp_rows(logits)
        log_allowed = _logsumexp_allowed(logits, allowed_part)
        probabilities = np.exp(logits - log_normalizer)
        active_weights = w_part[informative]
        # Computing the difference of stable log-sum-exp values keeps the
        # actual allowed-set likelihood correct even when one class has a
        # probability far below the old clipping floor.
        loss += float(np.dot(active_weights,
                             (log_normalizer - log_allowed)[informative, 0]))
        residual = np.zeros_like(probabilities)
        selected = allowed_part[informative]
        restricted = np.exp(logits[informative] - log_allowed[informative]) * selected
        residual[informative] = probabilities[informative] - restricted
        weighted_residual = residual * w_part[:, None]
        gradient_intercept += weighted_residual.sum(axis=0)
        gradient_coefficients += weighted_residual.T @ x_part
    loss /= informative_weight
    gradient_intercept /= informative_weight
    gradient_coefficients /= informative_weight
    loss += 0.5 * l2 * float(np.sum(coefficients * coefficients))
    gradient_coefficients += l2 * coefficients
    gradient = np.concatenate((gradient_intercept[:, None], gradient_coefficients), axis=1)
    return float(loss), gradient.reshape(-1)


@dataclass(frozen=True)
class SoftmaxFit:
    classes: tuple[Any, ...]
    intercept: tuple[float, ...]
    coefficients: tuple[tuple[float, ...], ...]
    l2_strength: float
    objective: float
    gradient_norm: float
    iterations: int
    converged: bool
    status: str
    label_mode: str
    n_rows: int
    informative_rows: int
    all_class_rows: int
    weight_sum: float
    informative_weight: float
    optimizer: str
    offset_identity: str | None = None
    offset_checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return _jsonable({
            "kind": "SoftmaxFitV1",
            "classes": self.classes,
            "intercept": self.intercept,
            "coefficients": self.coefficients,
            "l2_strength": self.l2_strength,
            "objective": self.objective,
            "gradient_norm": self.gradient_norm,
            "iterations": self.iterations,
            "converged": self.converged,
            "status": self.status,
            "label_mode": self.label_mode,
            "n_rows": self.n_rows,
            "informative_rows": self.informative_rows,
            "all_class_rows": self.all_class_rows,
            "weight_sum": self.weight_sum,
            "informative_weight": self.informative_weight,
            "optimizer": self.optimizer,
            "offset_identity": self.offset_identity,
            "offset_checksum": self.offset_checksum,
            "metadata": self.metadata,
        })

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "SoftmaxFit":
        if not isinstance(value, Mapping):
            raise BackendInputError("softmax fit wire value must be an object")
        if value.get("kind") != "SoftmaxFitV1":
            raise BackendInputError("wrong softmax fit wire kind")
        try:
            classes = _classes(value["classes"])
            intercept = np.asarray(value["intercept"], dtype=np.float64)
            coefficients = np.asarray(value["coefficients"], dtype=np.float64)
        except (KeyError, TypeError, ValueError) as exc:
            raise BackendInputError("malformed softmax fit dimensions") from exc
        if intercept.shape != (len(classes),) or coefficients.ndim != 2 or coefficients.shape[0] != len(classes):
            raise BackendInputError("softmax fit dimensions do not match classes")
        if not np.isfinite(intercept).all() or not np.isfinite(coefficients).all():
            raise BackendInputError("softmax fit contains non-finite parameters")
        offset_identity = value.get("offset_identity")
        offset_checksum = value.get("offset_checksum")
        if offset_identity is not None and (not isinstance(offset_identity, str) or not offset_identity):
            raise BackendInputError("softmax offset identity is invalid")
        if (offset_checksum is not None and offset_identity is None) or (
                offset_checksum is not None and (not isinstance(offset_checksum, str) or len(offset_checksum) != 64)):
            raise BackendInputError("softmax offset checksum is not bound to an identity")
        try:
            scalar_fields = (value["l2_strength"], value["objective"], value["gradient_norm"],
                             value["weight_sum"], value["informative_weight"])
            if any(not math.isfinite(float(item)) for item in scalar_fields) or float(value["l2_strength"]) <= 0:
                raise BackendInputError("softmax fit carries invalid scalar diagnostics")
        except (KeyError, TypeError, ValueError) as exc:
            raise BackendInputError("malformed softmax fit diagnostics") from exc
        return cls(
            classes, tuple(float(v) for v in intercept),
            tuple(tuple(float(v) for v in row) for row in coefficients),
            float(value["l2_strength"]), float(value["objective"]),
            float(value["gradient_norm"]), int(value["iterations"]),
            bool(value["converged"]), str(value["status"]), str(value["label_mode"]),
            int(value["n_rows"]), int(value["informative_rows"]),
            int(value["all_class_rows"]), float(value["weight_sum"]),
            float(value["informative_weight"]), str(value["optimizer"]),
            offset_identity, offset_checksum,
            _metadata(value.get("metadata", {})),
        )


def fit_softmax(
    X: Any,
    y: Any,
    weights: Any = None,
    *,
    classes: Sequence[Any],
    l2: float,
    max_iterations: int = 100,
    tolerance: float = 1e-8,
    batch_size: int = 65_536,
    offset_logits: Any = None,
    offset_identity: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> SoftmaxFit:
    """Fit weighted softmax cross-entropy over all supplied rows.

    ``y`` is either a length-N vector of exact class values or an N-by-K
    boolean compatible-class matrix.  The latter is the only supported way to
    represent interval/coarse observations.  Rows allowing all K classes are
    counted as uninformative and contribute no loss or gradient.
    """
    matrix = _matrix(X)
    n, p = matrix.shape
    declared_classes = _classes(classes)
    if not math.isfinite(float(l2)) or l2 <= 0:
        raise BackendInputError("softmax l2 must be finite and strictly positive")
    if type(max_iterations) is not int or not 1 <= max_iterations <= 2_000:
        raise BackendInputError("bounded positive max_iterations required")
    if not math.isfinite(float(tolerance)) or tolerance <= 0:
        raise BackendInputError("positive finite tolerance required")
    _validate_batch_size(batch_size)
    sample_weights = _weights(weights, n)
    allowed, label_mode = _label_matrix(y, n, declared_classes)
    if offset_logits is None:
        fixed_offset = None
        if offset_identity is not None:
            raise BackendInputError("offset_identity requires offset_logits")
    else:
        fixed_offset = _matrix(offset_logits, name="offset_logits")
        if fixed_offset.shape != (n, len(declared_classes)):
            raise BackendInputError("offset_logits must have shape (N, number of classes)")
        if not isinstance(offset_identity, str) or not offset_identity:
            raise BackendInputError("fixed softmax offsets require a nonempty offset_identity")
    fixed_offset_checksum = None if fixed_offset is None else _validate_call_checksum(fixed_offset, None)
    counts, all_class_rows, informative_weight = _allowed_counts(allowed, sample_weights)
    informative = allowed.sum(axis=1) < len(declared_classes)
    informative_rows = int(informative.sum())
    weight_sum = float(sample_weights.sum())
    k = len(declared_classes)
    smoothed = (counts + 1.0) / (float(counts.sum()) + k)
    smoothed = smoothed / smoothed.sum()
    fallback_intercept = np.log(np.maximum(smoothed, _LOG_EPS))
    fallback_intercept -= fallback_intercept.mean()
    zero_coefficients = np.zeros((k, p), dtype=np.float64)
    if n == 0 or informative_rows == 0:
        status = "empty_fallback" if n == 0 else "all_class_rows_fallback"
        objective, gradient = _softmax_objective_gradient(
            matrix, allowed, sample_weights,
            np.concatenate((fallback_intercept[:, None], zero_coefficients), axis=1).reshape(-1),
            l2=l2, batch_size=batch_size, offset_logits=fixed_offset,
        )
        return SoftmaxFit(
            declared_classes, tuple(fallback_intercept), tuple(map(tuple, zero_coefficients)),
            l2, objective, float(np.max(np.abs(gradient))), 0, True, status, label_mode,
            n, informative_rows, all_class_rows, weight_sum, informative_weight,
            "explicit_fallback", offset_identity, fixed_offset_checksum, _metadata(metadata),
        )
    if int(np.count_nonzero(counts > 0)) <= 1:
        status = "single_class_fallback"
        objective, gradient = _softmax_objective_gradient(
            matrix, allowed, sample_weights,
            np.concatenate((fallback_intercept[:, None], zero_coefficients), axis=1).reshape(-1),
            l2=l2, batch_size=batch_size, offset_logits=fixed_offset,
        )
        return SoftmaxFit(
            declared_classes, tuple(fallback_intercept), tuple(map(tuple, zero_coefficients)),
            l2, objective, float(np.max(np.abs(gradient))), 0, True, status, label_mode,
            n, informative_rows, all_class_rows, weight_sum, informative_weight,
            "explicit_fallback", offset_identity, fixed_offset_checksum, _metadata(metadata),
        )

    initial = np.concatenate((fallback_intercept[:, None], zero_coefficients), axis=1).reshape(-1)

    def objective(theta: np.ndarray):
        return _softmax_objective_gradient(
            matrix, allowed, sample_weights, theta, l2=l2, batch_size=batch_size,
            offset_logits=fixed_offset,
        )

    result = minimize(
        objective, initial, method="L-BFGS-B", jac=True,
        options={"maxiter": max_iterations, "gtol": tolerance, "ftol": 1e-15, "maxls": 50},
    )
    parameters = np.asarray(result.x, dtype=np.float64).reshape(k, p + 1)
    objective_value, gradient = objective(result.x)
    # scipy's success flag is not sufficient for a production fit: a line
    # search can report success while the returned KKT residual is still far
    # above the caller's declared tolerance.  Keep the residual explicit and
    # make it part of the consumability contract.
    gradient_norm = float(np.max(np.abs(gradient))) if gradient.size else 0.0
    converged = bool(result.success and np.isfinite(objective_value)
                     and np.isfinite(gradient).all()
                     and gradient_norm <= max(float(tolerance), 1e-6))
    status = "converged" if converged else "nonconverged"
    if not converged:
        parameters = np.concatenate((fallback_intercept[:, None], zero_coefficients), axis=1)
        fallback_theta = parameters.reshape(-1)
        objective_value, gradient = objective(fallback_theta)
        gradient_norm = float(np.max(np.abs(gradient))) if gradient.size else 0.0
        status = "nonconverged_fallback"
    result_metadata = _metadata(metadata)
    result_metadata.update({"optimizer_message": str(result.message), "provider_numpy": NUMPY_PROVIDER,
                            "provider_scipy": SCIPY_PROVIDER,
                            "fallback_used": bool(not converged)})
    return SoftmaxFit(
        declared_classes, tuple(float(v) for v in parameters[:, 0]),
        tuple(tuple(float(v) for v in row) for row in parameters[:, 1:]), l2,
        float(objective_value), float(gradient_norm), int(getattr(result, "nit", 0)),
        converged, status, label_mode, n, informative_rows, all_class_rows, weight_sum,
        informative_weight, "scipy.optimize.minimize:L-BFGS-B", offset_identity,
        # The training-call checksum is retained separately from the logical
        # baseline identity; future rows are allowed to carry a different
        # checksum at prediction time.
        fixed_offset_checksum, result_metadata,
    )


def predict_softmax(
    fit: SoftmaxFit, X: Any, *, offset_logits: Any = None,
    offset_checksum: str | None = None, offset_identity: str | None = None,
    allow_fallback: bool = False,
) -> np.ndarray:
    if type(fit) is not SoftmaxFit:
        raise BackendInputError("typed SoftmaxFit required")
    if not fit.converged and not allow_fallback:
        raise BackendInputError("softmax fit did not converge; pass allow_fallback=True explicitly")
    matrix = _matrix(X)
    coefficients = np.asarray(fit.coefficients, dtype=np.float64)
    intercept = np.asarray(fit.intercept, dtype=np.float64)
    if matrix.shape[1] != coefficients.shape[1]:
        raise BackendInputError("prediction feature count differs from fitted softmax")
    logits = matrix @ coefficients.T + intercept
    if fit.offset_identity is None:
        if offset_logits is not None or offset_checksum is not None or offset_identity is not None:
            raise BackendInputError("fit has no fixed offset but prediction supplied one")
    else:
        if offset_identity is not None and offset_identity != fit.offset_identity:
            raise BackendInputError("prediction offset identity differs from fitted softmax")
        fixed_offset = _matrix(offset_logits, name="offset_logits")
        if fixed_offset.shape != logits.shape:
            raise BackendInputError("prediction offset shape differs from fitted softmax")
        _validate_call_checksum(fixed_offset, offset_checksum)
        logits = logits + fixed_offset
    result = _softmax(logits)
    if not np.isfinite(result).all():
        raise BackendInputError("softmax prediction became non-finite")
    return result


def _pinball_objective_gradient(
    X: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    theta: np.ndarray,
    *,
    quantile: float,
    l2: float,
    batch_size: int,
    offset: np.ndarray | None = None,
) -> tuple[float, np.ndarray]:
    n, p = X.shape
    intercept = float(theta[0])
    coefficients = np.asarray(theta[1:], dtype=np.float64)
    total_weight = float(weights.sum())
    if total_weight <= 0:
        return float(0.5 * l2 * np.dot(coefficients, coefficients)), np.zeros_like(theta)
    loss = 0.0
    gradient_intercept = 0.0
    gradient_coefficients = np.zeros(p, dtype=np.float64)
    for part in _batch_slices(n, batch_size):
        prediction = intercept + X[part] @ coefficients
        if offset is not None:
            prediction = prediction + offset[part]
        residual = y[part] - prediction
        loss += float(np.dot(weights[part], np.where(residual >= 0, quantile * residual,
                                                     (quantile - 1.0) * residual)))
        # The zero residual subgradient is explicitly 0.  This keeps exact
        # zero atoms stable and makes the selected subgradient testable.
        slope = np.where(residual > 0, -quantile,
                         np.where(residual < 0, 1.0 - quantile, 0.0))
        weighted_slope = weights[part] * slope
        gradient_intercept += float(weighted_slope.sum())
        gradient_coefficients += X[part].T @ weighted_slope
    loss /= total_weight
    gradient_intercept /= total_weight
    gradient_coefficients /= total_weight
    loss += 0.5 * l2 * float(np.dot(coefficients, coefficients))
    gradient_coefficients += l2 * coefficients
    return float(loss), np.concatenate(([gradient_intercept], gradient_coefficients))


def _smooth_pinball_terms(residual: np.ndarray, quantile: float,
                          epsilon: float) -> tuple[np.ndarray, np.ndarray]:
    """Smooth pinball value and d(value)/d(residual).

    ``q*r + eps*log(1+exp(-r/eps))`` uniformly approximates the ordinary
    pinball loss with absolute error at most ``eps*log(2)``.  ``logaddexp``
    keeps the approximation finite for the large price moves present in the
    Jumbo targets.
    """
    scaled = -residual / epsilon
    values = quantile * residual + epsilon * np.logaddexp(0.0, scaled)
    derivative = quantile - _sigmoid(scaled)
    return values, derivative


def _smooth_pinball_objective_gradient(
    X: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    theta: np.ndarray,
    *,
    quantile: float,
    l2: float,
    batch_size: int,
    epsilon: float,
    offset: np.ndarray | None = None,
) -> tuple[float, np.ndarray]:
    """Smooth pinball objective used by the fused multi-head optimizer."""
    if not math.isfinite(float(epsilon)) or epsilon <= 0:
        raise BackendInputError("smooth pinball epsilon must be positive and finite")
    n, p = X.shape
    intercept = float(theta[0])
    coefficients = np.asarray(theta[1:], dtype=np.float64)
    total_weight = float(weights.sum())
    if total_weight <= 0:
        return float(0.5 * l2 * np.dot(coefficients, coefficients)), np.zeros_like(theta)
    loss = 0.0
    gradient = np.zeros(p + 1, dtype=np.float64)
    for part in _batch_slices(n, batch_size):
        prediction = intercept + X[part] @ coefficients
        if offset is not None:
            prediction = prediction + offset[part]
        residual = y[part] - prediction
        values, derivative = _smooth_pinball_terms(residual, quantile, epsilon)
        loss += float(np.dot(weights[part], values))
        weighted_slope = weights[part] * (-derivative)
        gradient[0] += float(weighted_slope.sum())
        gradient[1:] += X[part].T @ weighted_slope
    loss /= total_weight
    gradient /= total_weight
    loss += 0.5 * l2 * float(np.dot(coefficients, coefficients))
    gradient[1:] += l2 * coefficients
    return float(loss), gradient


def _smooth_pinball_stacked_objective_gradient(
    X: np.ndarray,
    targets: np.ndarray,
    weights: np.ndarray,
    theta: np.ndarray,
    *,
    quantiles: np.ndarray,
    l2: float,
    batch_size: int,
    epsilon: float,
    offsets: np.ndarray | None = None,
) -> tuple[float, np.ndarray]:
    """Fused smooth-pinball loss for T*Q heads.

    Coefficients are stored as H-by-(P+1), H=T*Q.  One matrix multiply for
    each bounded row batch computes all heads; this preserves the separable
    objective while avoiding an independent N-by-P pass for every head.
    """
    if not math.isfinite(float(epsilon)) or epsilon <= 0:
        raise BackendInputError("smooth pinball epsilon must be positive and finite")
    n, p = X.shape
    target_count, q_count = targets.shape[1], len(quantiles)
    head_count = target_count * q_count
    parameters = np.asarray(theta, dtype=np.float64).reshape(head_count, p + 1)
    total_weight = float(weights.sum())
    if total_weight <= 0:
        return float(0.5 * l2 * np.sum(parameters[:, 1:] ** 2)), np.zeros_like(theta)
    intercept = parameters[:, 0]
    coefficients = parameters[:, 1:]
    levels = np.asarray(quantiles, dtype=np.float64).reshape(1, 1, q_count)
    loss_by_head = np.zeros(head_count, dtype=np.float64)
    gradient = np.zeros_like(parameters)
    for part in _batch_slices(n, batch_size):
        batch_rows = part.stop - part.start
        prediction = X[part] @ coefficients.T + intercept
        if offsets is not None:
            prediction = prediction + offsets[part].reshape(batch_rows, head_count)
        residual = targets[part, :, None] - prediction.reshape(batch_rows, target_count, q_count)
        values, derivative = _smooth_pinball_terms(residual, levels, epsilon)
        loss_by_head += (weights[part, None, None] * values).reshape(batch_rows, head_count).sum(axis=0)
        weighted_slope = (weights[part, None, None] * (-derivative)).reshape(batch_rows, head_count)
        gradient[:, 0] += weighted_slope.sum(axis=0)
        gradient[:, 1:] += weighted_slope.T @ X[part]
    loss_by_head /= total_weight
    gradient /= total_weight
    loss = float(loss_by_head.sum() + 0.5 * l2 * np.sum(coefficients * coefficients))
    gradient[:, 1:] += l2 * coefficients
    return loss, gradient.reshape(-1)


def _smooth_pinball_head_metrics(
    X: np.ndarray,
    targets: np.ndarray,
    weights: np.ndarray,
    parameters: np.ndarray,
    *,
    quantiles: np.ndarray,
    l2: float,
    batch_size: int,
    epsilon: float,
    offsets: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return per-head smooth objectives and KKT gradient norms in one pass."""
    n, p = X.shape
    target_count, q_count = targets.shape[1], len(quantiles)
    head_count = target_count * q_count
    levels = np.asarray(quantiles, dtype=np.float64).reshape(1, 1, q_count)
    losses = np.zeros(head_count, dtype=np.float64)
    gradients = np.zeros_like(parameters)
    total_weight = float(weights.sum())
    for part in _batch_slices(n, batch_size):
        batch_rows = part.stop - part.start
        prediction = X[part] @ parameters[:, 1:].T + parameters[:, 0]
        if offsets is not None:
            prediction = prediction + offsets[part].reshape(batch_rows, head_count)
        residual = targets[part, :, None] - prediction.reshape(batch_rows, target_count, q_count)
        values, derivative = _smooth_pinball_terms(residual, levels, epsilon)
        losses += (weights[part, None, None] * values).reshape(batch_rows, head_count).sum(axis=0)
        weighted_slope = (weights[part, None, None] * (-derivative)).reshape(batch_rows, head_count)
        gradients[:, 0] += weighted_slope.sum(axis=0)
        gradients[:, 1:] += weighted_slope.T @ X[part]
    if total_weight > 0:
        losses /= total_weight
        gradients /= total_weight
    losses += 0.5 * l2 * np.sum(parameters[:, 1:] * parameters[:, 1:], axis=1)
    gradients[:, 1:] += l2 * parameters[:, 1:]
    return losses, np.max(np.abs(gradients), axis=1)


def _weighted_quantile(values: np.ndarray, weights: np.ndarray, level: float) -> float:
    if not 0 <= level <= 1:
        raise BackendInputError("quantile must be in [0,1]")
    if values.size == 0 or float(weights.sum()) <= 0:
        raise BackendInputError("weighted quantile needs positive support")
    order = np.argsort(values, kind="mergesort")
    ordered_values = values[order]
    ordered_weights = weights[order]
    cumulative = np.cumsum(ordered_weights)
    index = min(len(ordered_values) - 1, int(np.searchsorted(cumulative, level * cumulative[-1], side="left")))
    return float(ordered_values[index])


@dataclass(frozen=True)
class QuantileFit:
    quantiles: tuple[float, ...]
    intercept: tuple[tuple[float, ...], ...]
    coefficients: tuple[tuple[tuple[float, ...], ...], ...]
    l2_strength: float
    objective: float
    gradient_norm: float
    iterations: int
    converged: bool
    status: str
    n_rows: int
    target_count: int
    feature_count: int
    weight_sum: float
    diagnostics: tuple[dict[str, Any], ...]
    offset_identity: str | None = None
    offset_checksum: str | None = None
    smooth_epsilon: float = 1e-3
    loss_error_bound: float = 1e-3 * math.log(2.0)
    kkt_residual: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return _jsonable({
            "kind": "QuantileFitV1", "quantiles": self.quantiles,
            "intercept": self.intercept, "coefficients": self.coefficients,
            "l2_strength": self.l2_strength, "objective": self.objective,
            "gradient_norm": self.gradient_norm, "iterations": self.iterations,
            "converged": self.converged, "status": self.status,
            "n_rows": self.n_rows, "target_count": self.target_count,
            "feature_count": self.feature_count, "weight_sum": self.weight_sum,
            "diagnostics": self.diagnostics, "offset_identity": self.offset_identity,
            "offset_checksum": self.offset_checksum, "smooth_epsilon": self.smooth_epsilon,
            "loss_error_bound": self.loss_error_bound, "kkt_residual": self.kkt_residual,
            "metadata": self.metadata,
        })

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "QuantileFit":
        if not isinstance(value, Mapping):
            raise BackendInputError("quantile fit wire value must be an object")
        if value.get("kind") != "QuantileFitV1":
            raise BackendInputError("wrong quantile fit wire kind")
        try:
            quantiles = _validate_quantile_levels(value["quantiles"])
            intercept = np.asarray(value["intercept"], dtype=np.float64)
            coefficients = np.asarray(value["coefficients"], dtype=np.float64)
        except (KeyError, TypeError, ValueError) as exc:
            raise BackendInputError("malformed quantile fit dimensions") from exc
        if intercept.ndim != 2 or coefficients.ndim != 3 or intercept.shape[:2] != coefficients.shape[:2]:
            raise BackendInputError("quantile fit parameter dimensions are inconsistent")
        if intercept.shape[1] != len(quantiles) or not np.isfinite(intercept).all() or not np.isfinite(coefficients).all():
            raise BackendInputError("quantile fit dimensions or parameters are invalid")
        if int(value.get("target_count", -1)) != intercept.shape[0] or int(value.get("feature_count", -1)) != coefficients.shape[2]:
            raise BackendInputError("quantile fit feature/target counts do not match parameters")
        smooth_epsilon = float(value.get("smooth_epsilon", 1e-3))
        if not math.isfinite(smooth_epsilon) or smooth_epsilon <= 0:
            raise BackendInputError("quantile fit smooth epsilon is invalid")
        target_count_wire = int(value.get("target_count", intercept.shape[0]))
        aggregate_bound_default = smooth_epsilon * math.log(2.0) * target_count_wire * len(quantiles)
        scalar_fields = (value.get("l2_strength"), value.get("objective"), value.get("gradient_norm"),
                         value.get("weight_sum"), value.get("loss_error_bound", aggregate_bound_default),
                         value.get("kkt_residual", value.get("gradient_norm", 0.0)))
        try:
            if any(not math.isfinite(float(item)) for item in scalar_fields):
                raise BackendInputError("quantile fit carries non-finite diagnostics")
            if float(value.get("l2_strength")) < 0:
                raise BackendInputError("quantile fit l2 strength is invalid")
            diagnostics_wire = value["diagnostics"]
            if not isinstance(diagnostics_wire, (list, tuple)):
                raise BackendInputError("quantile diagnostics must be a sequence")
        except (KeyError, TypeError, ValueError) as exc:
            raise BackendInputError("malformed quantile fit diagnostics") from exc
        offset_identity = value.get("offset_identity")
        offset_checksum = value.get("offset_checksum")
        if offset_identity is not None and (not isinstance(offset_identity, str) or not offset_identity):
            raise BackendInputError("quantile offset identity is invalid")
        if offset_checksum is not None and (offset_identity is None or not isinstance(offset_checksum, str) or len(offset_checksum) != 64):
            raise BackendInputError("quantile offset checksum is not bound to an identity")
        return cls(
            quantiles,
            tuple(tuple(float(v) for v in row) for row in intercept),
            tuple(tuple(tuple(float(v) for v in row) for row in target)
                  for target in coefficients),
            float(value["l2_strength"]), float(value["objective"]),
            float(value["gradient_norm"]), int(value["iterations"]),
            bool(value["converged"]), str(value["status"]), int(value["n_rows"]),
            int(value["target_count"]), int(value["feature_count"]), float(value["weight_sum"]),
            tuple(_metadata(v) for v in diagnostics_wire), offset_identity,
            offset_checksum, smooth_epsilon,
            float(value.get("loss_error_bound", aggregate_bound_default)),
            float(value.get("kkt_residual", value.get("gradient_norm", 0.0))),
            _metadata(value.get("metadata", {})),
        )


def fit_quantiles(
    X: Any,
    Y: Any,
    weights: Any = None,
    *,
    quantiles: Sequence[float],
    l2: float,
    max_iterations: int = 100,
    tolerance: float = 1e-8,
    batch_size: int = 65_536,
    fallback_value: float = 0.0,
    offset_quantiles: Any = None,
    offset_identity: str | None = None,
    smooth_epsilon: float = 1e-3,
    metadata: Mapping[str, Any] | None = None,
) -> QuantileFit:
    """Fit all target/quantile heads over the full supplied matrix.

    ``Y`` is N-by-T (a one-dimensional vector is treated as one target).  The
    returned coefficient array is T-by-Q-by-P and is never backed by a
    subsample.  All heads are optimized in one fused matrix-matrix objective;
    each head still receives a separate objective, gradient, and KKT record.
    The smooth loss differs from ordinary pinball by at most
    ``smooth_epsilon*log(2)`` per weighted observation.
    """
    matrix = _matrix(X)
    n, p = matrix.shape
    targets = np.asarray(Y, dtype=np.float64)
    if targets.ndim == 1:
        targets = targets.reshape(n, 1)
    if targets.ndim != 2 or targets.shape[0] != n:
        raise BackendInputError("Y must have N rows and one or more target columns")
    if targets.shape[1] == 0:
        raise BackendInputError("Y must contain at least one target column")
    if not np.isfinite(targets).all():
        raise BackendInputError("Y contains non-finite values")
    declared_quantiles = _validate_quantile_levels(quantiles)
    if not math.isfinite(float(l2)) or l2 < 0:
        raise BackendInputError("quantile l2 must be finite and nonnegative")
    if type(max_iterations) is not int or not 1 <= max_iterations <= 2_000:
        raise BackendInputError("bounded positive max_iterations required")
    if not math.isfinite(float(tolerance)) or tolerance <= 0:
        raise BackendInputError("positive finite tolerance required")
    _validate_batch_size(batch_size)
    if not math.isfinite(float(smooth_epsilon)) or smooth_epsilon <= 0:
        raise BackendInputError("smooth_epsilon must be positive and finite")
    if not math.isfinite(float(fallback_value)):
        raise BackendInputError("finite fallback value required")
    sample_weights = _weights(weights, n)
    target_count = targets.shape[1]
    if offset_quantiles is None:
        fixed_offsets = None
        if offset_identity is not None:
            raise BackendInputError("offset_identity requires offset_quantiles")
    else:
        try:
            raw_offsets = np.asarray(offset_quantiles, dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise BackendInputError("offset_quantiles must be a finite numeric array") from exc
        if raw_offsets.ndim == 2 and target_count == 1 and raw_offsets.shape == (n, len(declared_quantiles)):
            raw_offsets = raw_offsets[:, None, :]
        if raw_offsets.shape != (n, target_count, len(declared_quantiles)) or not np.isfinite(raw_offsets).all():
            raise BackendInputError("offset_quantiles must have finite shape (N, targets, quantiles)")
        if not isinstance(offset_identity, str) or not offset_identity:
            raise BackendInputError("fixed quantile offsets require a nonempty offset_identity")
        fixed_offsets = np.ascontiguousarray(raw_offsets)
    fixed_offset_checksum = None if fixed_offsets is None else _validate_call_checksum(fixed_offsets, None)
    head_count = target_count * len(declared_quantiles)
    has_support = n > 0 and float(sample_weights.sum()) > 0
    if not has_support:
        parameters = np.zeros((head_count, p + 1), dtype=np.float64)
        parameters[:, 0] = float(fallback_value)
        status = "empty_fallback"
        all_converged = True
        iterations_used = 0
        objective_total = 0.0
        head_objectives = np.zeros(head_count, dtype=np.float64)
        head_gradients = np.zeros(head_count, dtype=np.float64)
        optimizer_message = "empty input; explicit fallback"
    else:
        initial = np.zeros((head_count, p + 1), dtype=np.float64)
        residual_constant_flags = []
        for target_index in range(target_count):
            values = targets[:, target_index]
            if fixed_offsets is None:
                base_atoms, base_masses = _weighted_atoms(values, sample_weights)
                base_cdf = np.cumsum(base_masses)
            for q_index, level in enumerate(declared_quantiles):
                head = target_index * len(declared_quantiles) + q_index
                if fixed_offsets is None:
                    residual_values = values
                    initial[head, 0] = base_atoms[min(len(base_atoms) - 1,
                                                        int(np.searchsorted(base_cdf, level, side="left")))]
                else:
                    residual_values = values - fixed_offsets[:, target_index, q_index]
                    initial[head, 0] = _weighted_quantile(residual_values, sample_weights, level)
                residual_is_constant = bool(np.all(residual_values == residual_values[0]))
                residual_constant_flags.append(residual_is_constant)
                if residual_is_constant:
                    # The smooth pinball minimizer has residual
                    # r*=-epsilon*logit(q), rather than the ordinary
                    # pinball atom at r=0.  Using the exact closed form
                    # avoids labelling this branch converged with a large
                    # intercept KKT residual.
                    logit = math.log(level / (1.0 - level))
                    initial[head, 0] = float(residual_values[0] + smooth_epsilon * logit)
        if all(residual_constant_flags):
            parameters = initial
            head_objectives, head_gradients = _smooth_pinball_head_metrics(
                matrix, targets, sample_weights, parameters,
                quantiles=np.asarray(declared_quantiles), l2=l2, batch_size=batch_size,
                epsilon=smooth_epsilon, offsets=fixed_offsets,
            )
            objective_total = float(head_objectives.sum())
            maximum_kkt = float(np.max(head_gradients)) if head_gradients.size else 0.0
            all_converged = bool(np.isfinite(head_gradients).all()
                                 and maximum_kkt <= max(float(tolerance), 1e-6))
            status = "converged" if all_converged else "nonconverged_fallback"
            iterations_used = 0
            optimizer_message = ("constant residual smooth closed-form fallback"
                                 if all_converged else
                                 "constant residual fallback failed KKT tolerance")
            skip_optimizer = True
        else:
            skip_optimizer = False
        initial_flat = initial.reshape(-1)

        def objective(theta: np.ndarray):
            return _smooth_pinball_stacked_objective_gradient(
                matrix, targets, sample_weights, theta,
                quantiles=np.asarray(declared_quantiles), l2=l2, batch_size=batch_size,
                epsilon=smooth_epsilon, offsets=fixed_offsets,
            )

        if not skip_optimizer:
            result = minimize(
                objective, initial_flat, method="L-BFGS-B", jac=True,
                options={"maxiter": max_iterations, "gtol": tolerance, "ftol": 1e-15, "maxls": 50},
            )
            parameters = np.asarray(result.x, dtype=np.float64).reshape(head_count, p + 1)
            objective_total, full_gradient = objective(result.x)
            head_objectives, head_gradients = _smooth_pinball_head_metrics(
                matrix, targets, sample_weights, parameters,
                quantiles=np.asarray(declared_quantiles), l2=l2, batch_size=batch_size,
                epsilon=smooth_epsilon, offsets=fixed_offsets,
            )
            kkt = float(np.max(head_gradients)) if head_gradients.size else 0.0
            all_converged = bool(result.success and np.isfinite(objective_total)
                                 and np.isfinite(full_gradient).all() and kkt <= max(tolerance, 1e-6))
            status = "converged" if all_converged else "nonconverged"
            iterations_used = int(getattr(result, "nit", 0))
            optimizer_message = str(result.message)
            if not all_converged:
                # Keep the numerical failure explicit while replacing the
                # consumable coefficients with the full-sample empirical
                # intercept fallback.  Prediction still rejects this record
                # unless allow_fallback=True is supplied deliberately.
                parameters = initial
                objective_total, full_gradient = objective(initial_flat)
                head_objectives, head_gradients = _smooth_pinball_head_metrics(
                    matrix, targets, sample_weights, parameters,
                    quantiles=np.asarray(declared_quantiles), l2=l2, batch_size=batch_size,
                    epsilon=smooth_epsilon, offsets=fixed_offsets,
                )
                kkt = float(np.max(head_gradients)) if head_gradients.size else 0.0
                status = "nonconverged_fallback"
                optimizer_message = f"{optimizer_message}; full-sample fallback retained"
    if not has_support:
        kkt = 0.0
    else:
        kkt = float(np.max(head_gradients)) if head_gradients.size else 0.0
    intercepts = tuple(tuple(float(parameters[target_index * len(declared_quantiles) + q_index, 0])
                            for q_index in range(len(declared_quantiles)))
                       for target_index in range(target_count))
    coefficient_heads = tuple(tuple(tuple(float(v) for v in parameters[target_index * len(declared_quantiles) + q_index, 1:])
                                    for q_index in range(len(declared_quantiles)))
                              for target_index in range(target_count))
    diagnostics: list[dict[str, Any]] = []
    for target_index in range(target_count):
        values = targets[:, target_index]
        for q_index, level in enumerate(declared_quantiles):
            head = target_index * len(declared_quantiles) + q_index
            residual_values = (values if fixed_offsets is None
                               else values - fixed_offsets[:, target_index, q_index])
            residual_constant = bool(n > 0 and np.all(residual_values == residual_values[0]))
            head_converged = bool(not has_support or
                                  (np.isfinite(head_gradients[head])
                                   and head_gradients[head] <= max(float(tolerance), 1e-6)))
            diagnostics.append({
                "target_index": target_index, "quantile": level,
                "status": "empty_fallback" if not has_support else (
                    "constant_target_fallback" if residual_constant and head_converged else status),
                "converged": head_converged,
                "objective": float(head_objectives[head]),
                "gradient_norm": float(head_gradients[head]),
                "kkt_residual": float(head_gradients[head]),
                "iterations": int(iterations_used), "zero_atoms": int(np.count_nonzero(values == 0)),
                "weighted_support": float(sample_weights.sum()),
                "smooth_epsilon": float(smooth_epsilon),
                "loss_error_bound": float(smooth_epsilon * math.log(2.0)),
                "optimizer_message": optimizer_message,
            })
    if not has_support:
        objective_total = 0.0
    result_metadata = _metadata(metadata)
    aggregate_loss_error_bound = float(smooth_epsilon * math.log(2.0) * head_count)
    result_metadata.update({"provider_numpy": NUMPY_PROVIDER, "provider_scipy": SCIPY_PROVIDER,
                            "prediction_crossing_correction": "maximum_accumulate",
                            "optimizer": "fused_scipy.optimize.minimize:L-BFGS-B",
                            "smooth_pinball": True, "smooth_epsilon": float(smooth_epsilon),
                            "loss_error_bound": aggregate_loss_error_bound,
                            "loss_error_bound_per_head": float(smooth_epsilon * math.log(2.0)),
                            "offset_identity": offset_identity,
                            "offset_training_checksum": fixed_offset_checksum,
                            "fallback_used": bool(status == "nonconverged_fallback")})
    return QuantileFit(
        declared_quantiles, tuple(intercepts), tuple(coefficient_heads), float(l2),
        float(objective_total), float(max(head_gradients) if head_gradients.size else 0.0), int(iterations_used),
        bool(all_converged), status, n, target_count, p, float(sample_weights.sum()),
        tuple(diagnostics), offset_identity, fixed_offset_checksum, float(smooth_epsilon),
        aggregate_loss_error_bound, float(kkt), result_metadata,
    )


def _crossing_count(values: np.ndarray) -> int:
    if values.shape[-1] < 2:
        return 0
    return int(np.count_nonzero(np.any(values[..., :-1] > values[..., 1:], axis=-1)))


def predict_quantiles(
    fit: QuantileFit,
    X: Any,
    *,
    offset_quantiles: Any = None,
    offset_checksum: str | None = None,
    offset_identity: str | None = None,
    correct_crossing: bool = True,
    return_diagnostics: bool = False,
    return_raw: bool = False,
    allow_fallback: bool = False,
) -> np.ndarray | tuple[np.ndarray, dict[str, Any]] | tuple[np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    """Predict and optionally expose both raw and monotone-projected heads.

    ``return_raw=True`` returns ``(projected, raw)``; with
    ``return_diagnostics=True`` it returns ``(projected, raw, diagnostics)``.
    A nonconverged fit is rejected unless the caller explicitly opts into its
    recorded fallback with ``allow_fallback=True``.
    """
    if type(fit) is not QuantileFit:
        raise BackendInputError("typed QuantileFit required")
    if not fit.converged and not allow_fallback:
        raise BackendInputError("quantile fit did not converge; pass allow_fallback=True explicitly")
    matrix = _matrix(X)
    coefficients = np.asarray(fit.coefficients, dtype=np.float64)
    intercept = np.asarray(fit.intercept, dtype=np.float64)
    if matrix.shape[1] != coefficients.shape[2]:
        raise BackendInputError("prediction feature count differs from fitted quantiles")
    raw = np.einsum("np,tqp->ntq", matrix, coefficients) + intercept[None, :, :]
    if fit.offset_identity is None:
        if offset_quantiles is not None or offset_checksum is not None or offset_identity is not None:
            raise BackendInputError("fit has no fixed quantile offset but prediction supplied one")
    else:
        if offset_identity is not None and offset_identity != fit.offset_identity:
            raise BackendInputError("prediction offset identity differs from fitted quantiles")
        try:
            fixed_offsets = np.asarray(offset_quantiles, dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise BackendInputError("prediction offset_quantiles must be numeric") from exc
        if fixed_offsets.ndim == 2 and fit.target_count == 1 and fixed_offsets.shape == (matrix.shape[0], len(fit.quantiles)):
            fixed_offsets = fixed_offsets[:, None, :]
        if fixed_offsets.shape != raw.shape or not np.isfinite(fixed_offsets).all():
            raise BackendInputError("prediction offset shape differs from fitted quantiles")
        _validate_call_checksum(fixed_offsets, offset_checksum)
        raw = raw + fixed_offsets
    before = _crossing_count(raw)
    result = np.maximum.accumulate(raw, axis=-1) if correct_crossing else raw
    after = _crossing_count(result)
    diagnostics = {"crossing_correction": "maximum_accumulate" if correct_crossing else "none",
                   "rows_with_crossing_before": before, "rows_with_crossing_after": after,
                   "rows": int(matrix.shape[0]), "targets": fit.target_count,
                   "projection_applied": bool(before > 0 and correct_crossing),
                   "projection_adjustment_linf": float(np.max(np.abs(result - raw))) if raw.size else 0.0,
                   "raw_quantiles": raw.copy(), "projected_quantiles": result.copy(),
                   "offset_checksum": None if fit.offset_identity is None else _offset_checksum(fixed_offsets)}
    if return_diagnostics and return_raw:
        return result, raw, diagnostics
    if return_diagnostics:
        return result, diagnostics
    if return_raw:
        return result, raw
    return result


def _groups(group_ids: Any, n: int) -> tuple[Any, ...]:
    if group_ids is None:
        return tuple("__global__" for _ in range(n))
    values = tuple(group_ids)
    if len(values) != n:
        raise BackendInputError(f"group_ids must have length {n}")
    for value in values:
        try:
            hash(value)
            json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            raise BackendInputError("group IDs must be hashable JSON values") from exc
    return values


def _factor_group_ids(group_values: tuple[Any, ...]) -> tuple[tuple[Any, ...], np.ndarray, tuple[slice, ...]]:
    """Factor groups once and return contiguous slices for each factor.

    The previous implementation materialized one N-length boolean mask per
    group.  This factorization keeps the same deterministic first-seen group
    order while doing one pass plus one stable sort, so empirical baselines
    do not scale as N*G when the Jumbo population has many dates/clocks.
    """
    lookup: dict[Any, int] = {}
    ordered: list[Any] = []
    codes = np.empty(len(group_values), dtype=np.int64)
    for index, value in enumerate(group_values):
        try:
            code = lookup[value]
        except KeyError:
            code = len(ordered)
            lookup[value] = code
            ordered.append(value)
        codes[index] = code
    order = np.argsort(codes, kind="stable")
    counts = np.bincount(codes, minlength=len(ordered)) if ordered else np.empty(0, dtype=np.int64)
    slices: list[slice] = []
    cursor = 0
    for count in counts.tolist():
        slices.append(slice(cursor, cursor + int(count)))
        cursor += int(count)
    return tuple(ordered), order, tuple(slices)


def _weighted_atoms(values: np.ndarray, weights: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return sorted atom locations and normalized masses in one aggregation."""
    if values.size == 0 or float(weights.sum()) <= 0:
        return np.empty(0, dtype=np.float64), np.empty(0, dtype=np.float64)
    order = np.argsort(values, kind="mergesort")
    ordered_values = np.asarray(values[order], dtype=np.float64)
    ordered_weights = np.asarray(weights[order], dtype=np.float64)
    starts = np.r_[0, np.flatnonzero(ordered_values[1:] != ordered_values[:-1]) + 1]
    atoms = ordered_values[starts]
    masses = np.add.reduceat(ordered_weights, starts)
    masses = masses / float(masses.sum())
    return atoms, masses


def _mixture_quantiles(global_atoms: np.ndarray, global_masses: np.ndarray,
                       local_atoms: np.ndarray, local_masses: np.ndarray,
                       local_total: float, shrinkage: float,
                       levels: Sequence[float]) -> np.ndarray:
    """Invert a global-plus-local empirical CDF without copying global atoms.

    Every local atom is present in the global support because the global
    baseline is formed from the same admitted rows.  We therefore binary
    search the global support for each requested level and evaluate the local
    CDF with ``searchsorted``.  This keeps memory O(N + G*Q) rather than
    concatenating the N-row global support for every one of G groups.
    """
    if global_atoms.size == 0:
        return np.zeros(len(tuple(levels)), dtype=np.float64)
    global_cdf = np.cumsum(global_masses)
    denominator = local_total + shrinkage
    if local_atoms.size == 0 or local_total <= 0:
        return np.asarray([global_atoms[min(len(global_atoms) - 1,
                                            int(np.searchsorted(global_cdf, level, side="left")))]
                           for level in levels], dtype=np.float64)
    local_cdf = np.cumsum(local_masses)
    answers: list[float] = []
    for level in levels:
        low, high = 0, len(global_atoms) - 1
        while low < high:
            middle = (low + high) // 2
            local_index = int(np.searchsorted(local_atoms, global_atoms[middle], side="right"))
            local_mass = 0.0 if local_index == 0 else float(local_cdf[local_index - 1])
            mixture_cdf = (local_total * local_mass + shrinkage * global_cdf[middle]) / denominator
            if mixture_cdf >= level:
                high = middle
            else:
                low = middle + 1
        answers.append(float(global_atoms[low]))
    return np.asarray(answers, dtype=np.float64)


@dataclass(frozen=True)
class EmpiricalCategoricalFit:
    classes: tuple[Any, ...]
    groups: tuple[Any, ...]
    probabilities: tuple[tuple[float, ...], ...]
    global_probabilities: tuple[float, ...]
    shrinkage: float
    status: str
    n_rows: int
    weight_sum: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return _jsonable({"kind": "EmpiricalCategoricalFitV1", **self.__dict__})

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "EmpiricalCategoricalFit":
        if not isinstance(value, Mapping) or value.get("kind") != "EmpiricalCategoricalFitV1":
            raise BackendInputError("wrong empirical categorical wire value")
        classes = _classes(value.get("classes", ()))
        groups = tuple(value.get("groups", ()))
        probabilities = np.asarray(value.get("probabilities", ()), dtype=np.float64)
        global_probabilities = np.asarray(value.get("global_probabilities", ()), dtype=np.float64)
        if probabilities.shape != (len(groups), len(classes)) or global_probabilities.shape != (len(classes),):
            raise BackendInputError("empirical categorical dimensions do not match classes/groups")
        if not np.isfinite(probabilities).all() or not np.isfinite(global_probabilities).all():
            raise BackendInputError("empirical categorical probabilities are non-finite")
        if np.any(probabilities < 0) or np.any(global_probabilities < 0):
            raise BackendInputError("empirical categorical probabilities are negative")
        if (not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-10)
                or not math.isclose(float(global_probabilities.sum()), 1.0, abs_tol=1e-10)):
            raise BackendInputError("empirical categorical probabilities are not simplex rows")
        shrinkage = float(value["shrinkage"])
        if not math.isfinite(shrinkage) or shrinkage <= 0:
            raise BackendInputError("empirical categorical shrinkage is invalid")
        return cls(classes, groups, tuple(tuple(float(v) for v in row) for row in probabilities),
                   tuple(float(v) for v in global_probabilities), shrinkage, str(value["status"]),
                   int(value["n_rows"]), float(value["weight_sum"]), _metadata(value.get("metadata", {})))


def fit_empirical_categorical(
    y: Any,
    weights: Any = None,
    *,
    classes: Sequence[Any],
    shrinkage: float,
    prior: Sequence[float] | None = None,
    group_ids: Sequence[Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> EmpiricalCategoricalFit:
    declared_classes = _classes(classes)
    values = np.asarray(y, dtype=object).reshape(-1)
    n = values.shape[0]
    if not math.isfinite(float(shrinkage)) or shrinkage <= 0:
        raise BackendInputError("categorical shrinkage must be positive and finite")
    sample_weights = _weights(weights, n)
    lookup = {value: index for index, value in enumerate(declared_classes)}
    indices = np.empty(n, dtype=np.int64)
    for i, value in enumerate(values.tolist()):
        if value not in lookup:
            raise BackendInputError("categorical baseline contains an unknown class")
        indices[i] = lookup[value]
    if prior is None:
        prior_array = np.full(len(declared_classes), 1.0 / len(declared_classes))
    else:
        prior_array = _vector(prior, len(declared_classes), name="prior")
        if np.any(prior_array < 0) or not float(prior_array.sum()) > 0:
            raise BackendInputError("categorical prior must be nonnegative with positive mass")
        prior_array = prior_array / prior_array.sum()
    global_counts = np.bincount(indices, weights=sample_weights, minlength=len(declared_classes)).astype(float)
    global_total = float(global_counts.sum())
    global_probabilities = (global_counts + shrinkage * prior_array) / (global_total + shrinkage)
    group_values = _groups(group_ids, n)
    unique_groups, order, group_slices = _factor_group_ids(group_values)
    if not unique_groups:
        unique_groups, group_slices = ("__global__",), (slice(0, 0),)
    rows = []
    for group_slice in group_slices:
        selected_indices = order[group_slice]
        counts = np.bincount(indices[selected_indices], weights=sample_weights[selected_indices], minlength=len(declared_classes)).astype(float)
        total = float(counts.sum())
        rows.append(tuple(float(v) for v in (counts + shrinkage * global_probabilities) / (total + shrinkage)))
    observed_classes = int(np.count_nonzero(global_counts > 0))
    status = "empty_fallback" if n == 0 else "single_class_shrinkage" if observed_classes <= 1 else "smoothed_empirical"
    return EmpiricalCategoricalFit(declared_classes, unique_groups, tuple(rows),
                                   tuple(float(v) for v in global_probabilities), float(shrinkage),
                                   status, n, global_total, _metadata(metadata))


def predict_empirical_categorical(fit: EmpiricalCategoricalFit, group_ids: Sequence[Any] | None = None) -> np.ndarray:
    if type(fit) is not EmpiricalCategoricalFit:
        raise BackendInputError("typed EmpiricalCategoricalFit required")
    if group_ids is None:
        return np.asarray([fit.global_probabilities], dtype=np.float64)
    values = tuple(group_ids)
    lookup = {group: row for group, row in zip(fit.groups, fit.probabilities)}
    global_row = np.asarray(fit.global_probabilities, dtype=np.float64)
    return np.asarray([lookup.get(group, global_row) for group in values], dtype=np.float64)


@dataclass(frozen=True)
class EmpiricalQuantileFit:
    quantiles: tuple[float, ...]
    groups: tuple[Any, ...]
    values: tuple[tuple[float, ...], ...]
    global_values: tuple[float, ...]
    shrinkage: float
    status: str
    n_rows: int
    weight_sum: float
    zero_atoms: int
    atoms: tuple[tuple[float, ...], ...] = ()
    atom_masses: tuple[tuple[float, ...], ...] = ()
    global_atoms: tuple[float, ...] = ()
    global_atom_masses: tuple[float, ...] = ()
    zero_atom_masses: tuple[float, ...] = ()
    global_zero_atom_mass: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return _jsonable({"kind": "EmpiricalQuantileFitV1", **self.__dict__})

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "EmpiricalQuantileFit":
        if not isinstance(value, Mapping) or value.get("kind") != "EmpiricalQuantileFitV1":
            raise BackendInputError("wrong empirical quantile wire value")
        quantiles = _validate_quantile_levels(value.get("quantiles", ()))
        groups = tuple(value.get("groups", ()))
        values = np.asarray(value.get("values", ()), dtype=np.float64)
        global_values = np.asarray(value.get("global_values", ()), dtype=np.float64)
        atoms = tuple(tuple(float(v) for v in row) for row in value.get("atoms", ()))
        atom_masses = tuple(tuple(float(v) for v in row) for row in value.get("atom_masses", ()))
        global_atoms = np.asarray(value.get("global_atoms", ()), dtype=np.float64)
        global_atom_masses = np.asarray(value.get("global_atom_masses", ()), dtype=np.float64)
        zero_atom_masses = tuple(float(v) for v in value.get("zero_atom_masses", ()))
        if values.shape != (len(groups), len(quantiles)) or global_values.shape != (len(quantiles),):
            raise BackendInputError("empirical quantile values do not match groups/quantiles")
        if len(atoms) != len(groups) or len(atom_masses) != len(groups) or len(zero_atom_masses) != len(groups):
            raise BackendInputError("empirical quantile atom rows do not match groups")
        if global_atoms.ndim != 1 or global_atom_masses.shape != global_atoms.shape:
            raise BackendInputError("empirical quantile global atoms have invalid dimensions")
        if any(len(atom_row) != len(mass_row) for atom_row, mass_row in zip(atoms, atom_masses)):
            raise BackendInputError("empirical quantile atom/mass rows have different lengths")
        all_arrays = [values, global_values, global_atoms, global_atom_masses]
        if not all(np.isfinite(array).all() for array in all_arrays):
            raise BackendInputError("empirical quantile wire contains non-finite values")
        if np.any(global_atom_masses < 0) or any(any(m < 0 or not math.isfinite(m) for m in row) for row in atom_masses):
            raise BackendInputError("empirical quantile atom masses are invalid")
        shrinkage = float(value["shrinkage"])
        global_zero_atom_mass = float(value.get("global_zero_atom_mass", 0.0))
        if (not math.isfinite(shrinkage) or shrinkage <= 0 or not math.isfinite(global_zero_atom_mass)
                or any(not math.isfinite(m) or m < 0 or m > 1 for m in zero_atom_masses)):
            raise BackendInputError("empirical quantile shrinkage/zero mass is invalid")
        return cls(
            quantiles, groups, tuple(tuple(float(v) for v in row) for row in values),
            tuple(float(v) for v in global_values), shrinkage, str(value["status"]),
            int(value["n_rows"]), float(value["weight_sum"]), int(value.get("zero_atoms", 0)),
            atoms, atom_masses, tuple(float(v) for v in global_atoms),
            tuple(float(v) for v in global_atom_masses), zero_atom_masses,
            global_zero_atom_mass, _metadata(value.get("metadata", {})),
        )


def fit_empirical_quantiles(
    y: Any,
    weights: Any = None,
    *,
    quantiles: Sequence[float],
    shrinkage: float,
    group_ids: Sequence[Any] | None = None,
    global_weights: Any = None,
    fallback_quantiles: Sequence[float] | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> EmpiricalQuantileFit:
    values = np.asarray(y, dtype=np.float64).reshape(-1)
    n = values.shape[0]
    if values.size and not np.isfinite(values).all():
        raise BackendInputError("quantile baseline contains non-finite values")
    declared_quantiles = _validate_quantile_levels(quantiles)
    if not math.isfinite(float(shrinkage)) or shrinkage <= 0:
        raise BackendInputError("quantile shrinkage must be positive and finite")
    sample_weights = _weights(weights, n)
    pooled_weights = sample_weights if global_weights is None else _weights(global_weights, n)
    if n == 0:
        if fallback_quantiles is None:
            fallback = np.zeros(len(declared_quantiles), dtype=np.float64)
        else:
            fallback = _vector(fallback_quantiles, len(declared_quantiles), name="fallback_quantiles")
        global_values = np.maximum.accumulate(fallback)
        global_atoms = global_values.copy()
        global_atom_masses = np.full(len(global_atoms), 1.0 / len(global_atoms))
    else:
        global_atoms, global_atom_masses = _weighted_atoms(values, pooled_weights)
        global_cdf = np.cumsum(global_atom_masses)
        global_values = np.asarray([
            global_atoms[min(len(global_atoms) - 1,
                             int(np.searchsorted(global_cdf, q, side="left")))]
            for q in declared_quantiles
        ])
        global_values = np.maximum.accumulate(global_values)
    global_zero_atom_mass = float(global_atom_masses[global_atoms == 0].sum()) if global_atoms.size else 0.0
    group_values = _groups(group_ids, n)
    unique_groups, order, group_slices = _factor_group_ids(group_values)
    if not unique_groups:
        unique_groups, group_slices = ("__global__",), (slice(0, 0),)
    rows = []
    atom_rows: list[tuple[float, ...]] = []
    atom_mass_rows: list[tuple[float, ...]] = []
    zero_atom_masses: list[float] = []
    for group_slice in group_slices:
        selected_indices = order[group_slice]
        local_values = values[selected_indices]
        local_weights = sample_weights[selected_indices]
        total = float(local_weights.sum())
        local_atoms, local_masses = _weighted_atoms(local_values, local_weights)
        row = _mixture_quantiles(
            global_atoms, global_atom_masses, local_atoms, local_masses,
            total, shrinkage, declared_quantiles)
        row = np.maximum.accumulate(row)
        # Store the local atoms and masses; the shared global atoms/masses are
        # stored once on the fit and combined by the declared shrinkage rule.
        atom_rows.append(tuple(float(v) for v in local_atoms))
        atom_mass_rows.append(tuple(float(v) for v in local_masses))
        local_zero_mass = float(local_masses[local_atoms == 0].sum()) if local_atoms.size else 0.0
        mixture_zero_mass = ((total * local_zero_mass) + shrinkage * global_zero_atom_mass) / (total + shrinkage)
        zero_atom_masses.append(float(mixture_zero_mass))
        rows.append(tuple(float(v) for v in row))
    weighted_zero_count = int(np.count_nonzero((values == 0) & (sample_weights > 0)))
    status = "empty_fallback" if n == 0 else "zero_atom_supported" if weighted_zero_count else "smoothed_empirical"
    result_metadata = _metadata(metadata)
    result_metadata.update({"global_weight_sum": float(pooled_weights.sum()),
                            "local_weight_sum": float(sample_weights.sum()),
                            "global_weighting": "explicit" if global_weights is not None else "local"})
    return EmpiricalQuantileFit(declared_quantiles, unique_groups, tuple(rows),
                                tuple(float(v) for v in global_values), float(shrinkage), status,
                                n, float(sample_weights.sum()), weighted_zero_count,
                                tuple(atom_rows), tuple(atom_mass_rows),
                                tuple(float(v) for v in global_atoms),
                                tuple(float(v) for v in global_atom_masses),
                                tuple(zero_atom_masses), float(global_zero_atom_mass), result_metadata)


def predict_empirical_quantiles(fit: EmpiricalQuantileFit, group_ids: Sequence[Any] | None = None,
                                *, correct_crossing: bool = True) -> np.ndarray:
    if type(fit) is not EmpiricalQuantileFit:
        raise BackendInputError("typed EmpiricalQuantileFit required")
    if group_ids is None:
        result = np.asarray([fit.global_values], dtype=np.float64)
    else:
        values = tuple(group_ids)
        lookup = {group: row for group, row in zip(fit.groups, fit.values)}
        global_row = np.asarray(fit.global_values, dtype=np.float64)
        result = np.asarray([lookup.get(group, global_row) for group in values], dtype=np.float64)
    return np.maximum.accumulate(result, axis=-1) if correct_crossing else result


def _temperature_objective_gradient(logits: np.ndarray, allowed: np.ndarray, weights: np.ndarray,
                                    log_temperature: float, *, batch_size: int) -> tuple[float, float]:
    """Stable exact or allowed-set temperature cross-entropy and derivative."""
    allowed = np.asarray(allowed)
    if allowed.ndim == 1:
        indices = allowed.astype(np.int64)
        if indices.shape[0] != logits.shape[0] or np.any(indices < 0) or np.any(indices >= logits.shape[1]):
            raise BackendInputError("temperature class indices are out of range")
        exact_allowed = np.zeros_like(logits, dtype=bool)
        exact_allowed[np.arange(logits.shape[0]), indices] = True
        allowed = exact_allowed
    if allowed.shape != logits.shape or allowed.dtype != np.dtype(bool):
        raise BackendInputError("temperature allowed labels must be a boolean logits-shaped matrix")
    temperature = math.exp(float(log_temperature))
    informative_rows = allowed.sum(axis=1) < logits.shape[1]
    # Compatible rows admitting every class carry no temperature information:
    # their numerator and denominator are identical.  Normalize by the
    # informative weight only so they cannot dilute the calibration KKT.
    informative_weight = float(weights[informative_rows].sum())
    objective = 0.0
    gradient = 0.0
    for part in _batch_slices(logits.shape[0], batch_size):
        z = logits[part] / temperature
        log_all = _logsumexp_rows(z)
        log_allowed = _logsumexp_allowed(z, allowed[part])
        informative = informative_rows[part]
        if not informative.any():
            continue
        objective += float(np.dot(weights[part][informative], (log_all - log_allowed)[informative, 0]))
        probabilities = np.exp(z - log_all)
        restricted = np.exp(z - log_allowed) * allowed[part]
        expected_all = np.sum(probabilities * z, axis=1)
        expected_allowed = np.sum(restricted * z, axis=1)
        gradient += float(np.dot(weights[part][informative],
                                 (expected_allowed - expected_all)[informative]))
    if informative_weight <= 0:
        return 0.0, 0.0
    return objective / informative_weight, gradient / informative_weight


@dataclass(frozen=True)
class TemperatureCalibration:
    classes: tuple[Any, ...]
    temperature: float
    objective: float
    gradient: float
    iterations: int
    converged: bool
    status: str
    source_fit_id: str
    calibration_id: str
    input_digest: str
    n_rows: int
    weight_sum: float
    label_mode: str = "exact_class"
    log_temperature: float = 0.0
    bound_status: str = "interior"
    kkt_residual: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return _jsonable({"kind": "TemperatureCalibrationV1", **self.__dict__})

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "TemperatureCalibration":
        if not isinstance(value, Mapping):
            raise BackendInputError("temperature wire value must be an object")
        if value.get("kind") != "TemperatureCalibrationV1":
            raise BackendInputError("wrong temperature calibration wire kind")
        temperature = float(value["temperature"])
        if not math.isfinite(temperature) or temperature <= 0:
            raise BackendInputError("temperature calibration must carry a positive finite temperature")
        return cls(
            tuple(value["classes"]), temperature, float(value["objective"]),
            float(value["gradient"]), int(value["iterations"]), bool(value["converged"]),
            str(value["status"]), str(value["source_fit_id"]), str(value["calibration_id"]),
            str(value["input_digest"]), int(value["n_rows"]), float(value["weight_sum"]),
            str(value.get("label_mode", "exact_class")),
            float(value.get("log_temperature", math.log(temperature))),
            str(value.get("bound_status", "interior")),
            float(value.get("kkt_residual", abs(float(value.get("gradient", 0.0))))),
            _metadata(value.get("metadata", {})),
        )


def fit_temperature(
    logits: Any,
    y: Any,
    weights: Any = None,
    *,
    classes: Sequence[Any],
    source_fit_id: str,
    calibration_id: str,
    metadata: Mapping[str, Any] | None = None,
    max_iterations: int = 100,
    tolerance: float = 1e-8,
    batch_size: int = 65_536,
) -> TemperatureCalibration:
    matrix = _matrix(logits, name="logits")
    n, k = matrix.shape
    declared_classes = _classes(classes)
    if k != len(declared_classes):
        raise BackendInputError("logit column count differs from classes")
    if not isinstance(source_fit_id, str) or not source_fit_id or not isinstance(calibration_id, str) or not calibration_id:
        raise BackendInputError("temperature calibration needs source and calibration identities")
    if type(max_iterations) is not int or not 1 <= max_iterations <= 2_000:
        raise BackendInputError("bounded positive max_iterations required")
    if not math.isfinite(float(tolerance)) or tolerance <= 0:
        raise BackendInputError("positive finite tolerance required")
    _validate_batch_size(batch_size)
    sample_weights = _weights(weights, n)
    allowed, mode = _label_matrix(y, n, declared_classes)
    informative = (sample_weights > 0) & (allowed.sum(axis=1) < k)
    informative_counts = (allowed[informative].astype(np.float64) * sample_weights[informative, None]).sum(axis=0) if informative.any() else np.zeros(k)
    input_digest = _array_digest(matrix, allowed, sample_weights)
    if n == 0:
        return TemperatureCalibration(
            classes=declared_classes, temperature=1.0, objective=0.0, gradient=0.0,
            iterations=0, converged=True, status="empty_fallback", source_fit_id=source_fit_id,
            calibration_id=calibration_id, input_digest=input_digest, n_rows=n, weight_sum=0.0,
            label_mode=mode, log_temperature=0.0, bound_status="interior", kkt_residual=0.0,
            metadata=_metadata(metadata),
        )
    if np.count_nonzero(informative) == 0 or np.count_nonzero(informative_counts > 0) <= 1:
        objective, gradient = _temperature_objective_gradient(matrix, allowed, sample_weights, 0.0, batch_size=batch_size)
        return TemperatureCalibration(
            classes=declared_classes, temperature=1.0, objective=float(objective), gradient=float(gradient),
            iterations=0, converged=True, status="single_class_fallback", source_fit_id=source_fit_id,
            calibration_id=calibration_id, input_digest=input_digest, n_rows=n,
            weight_sum=float(sample_weights.sum()), label_mode=mode, log_temperature=0.0,
            bound_status="interior", kkt_residual=float(abs(gradient)), metadata=_metadata(metadata),
        )

    def objective(value: np.ndarray):
        result, gradient = _temperature_objective_gradient(matrix, allowed, sample_weights, float(value[0]), batch_size=batch_size)
        return result, np.asarray([gradient], dtype=np.float64)

    result = minimize(objective, np.asarray([0.0]), method="L-BFGS-B", jac=True,
                      bounds=[(-5.0, 5.0)], options={"maxiter": max_iterations, "gtol": tolerance, "ftol": 1e-15})
    fitted_log_temperature = float(result.x[0])
    objective_value, gradient = _temperature_objective_gradient(matrix, allowed, sample_weights,
                                                                  float(result.x[0]), batch_size=batch_size)
    lower, upper = -5.0, 5.0
    at_lower = fitted_log_temperature <= lower + 1e-8
    at_upper = fitted_log_temperature >= upper - 1e-8
    bound_status = "lower" if at_lower else "upper" if at_upper else "interior"
    kkt_residual = max(0.0, -gradient) if at_lower else max(0.0, gradient) if at_upper else abs(gradient)
    converged = bool(result.success and np.isfinite(objective_value) and np.isfinite(gradient)
                     and kkt_residual <= max(tolerance, 1e-6))
    status = "converged" if converged else "nonconverged"
    if not converged:
        fitted_log_temperature = 0.0
        objective_value, gradient = _temperature_objective_gradient(
            matrix, allowed, sample_weights, fitted_log_temperature, batch_size=batch_size)
        bound_status = "interior"
        kkt_residual = abs(gradient)
        status = "nonconverged_fallback"
    result_metadata = _metadata(metadata)
    result_metadata.update({"label_mode": mode, "provider_numpy": NUMPY_PROVIDER, "provider_scipy": SCIPY_PROVIDER,
                            "optimizer_message": str(result.message), "bound_status": bound_status,
                            "kkt_residual": float(kkt_residual),
                            "allowed_class_rows": int(np.count_nonzero(allowed.sum(axis=1) == k)),
                            "fallback_used": bool(not converged)})
    return TemperatureCalibration(
        classes=declared_classes, temperature=float(math.exp(fitted_log_temperature)),
        objective=float(objective_value), gradient=float(gradient),
        iterations=int(getattr(result, "nit", 0)), converged=converged,
        status=status, source_fit_id=source_fit_id,
        calibration_id=calibration_id, input_digest=input_digest, n_rows=n,
        weight_sum=float(sample_weights.sum()), label_mode=mode,
        log_temperature=fitted_log_temperature, bound_status=bound_status,
        kkt_residual=float(kkt_residual), metadata=result_metadata,
    )


def predict_temperature(calibration: TemperatureCalibration, logits: Any, *, allow_fallback: bool = False) -> np.ndarray:
    if type(calibration) is not TemperatureCalibration:
        raise BackendInputError("typed TemperatureCalibration required")
    if not calibration.converged and not allow_fallback:
        raise BackendInputError("temperature calibration did not converge; pass allow_fallback=True explicitly")
    if not math.isfinite(float(calibration.temperature)) or calibration.temperature <= 0:
        raise BackendInputError("temperature calibration carries an invalid temperature")
    matrix = _matrix(logits, name="logits")
    if matrix.shape[1] != len(calibration.classes):
        raise BackendInputError("logit column count differs from calibration classes")
    return _softmax(matrix / float(calibration.temperature))


@dataclass(frozen=True)
class QuantileResidualCalibration:
    quantiles: tuple[float, ...]
    corrections: tuple[float, ...]
    source_fit_id: str
    calibration_id: str
    input_digest: str
    n_rows: int
    weight_sum: float
    status: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return _jsonable({"kind": "QuantileResidualCalibrationV1", **self.__dict__})

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "QuantileResidualCalibration":
        if not isinstance(value, Mapping) or value.get("kind") != "QuantileResidualCalibrationV1":
            raise BackendInputError("wrong quantile residual wire value")
        quantiles = _validate_quantile_levels(value.get("quantiles", ()))
        corrections = np.asarray(value.get("corrections", ()), dtype=np.float64)
        if corrections.shape != (len(quantiles),) or not np.isfinite(corrections).all():
            raise BackendInputError("quantile residual corrections have invalid dimensions")
        weight_sum = float(value["weight_sum"])
        if not math.isfinite(weight_sum) or weight_sum < 0:
            raise BackendInputError("quantile residual weight sum is invalid")
        return cls(
            quantiles, tuple(float(v) for v in corrections), str(value["source_fit_id"]),
            str(value["calibration_id"]), str(value["input_digest"]), int(value["n_rows"]),
            weight_sum, str(value["status"]), _metadata(value.get("metadata", {})),
        )


def fit_quantile_residual_calibration(
    predicted_quantiles: Any,
    y: Any,
    weights: Any = None,
    *,
    quantiles: Sequence[float],
    source_fit_id: str,
    calibration_id: str,
    metadata: Mapping[str, Any] | None = None,
) -> QuantileResidualCalibration:
    predictions = _matrix(predicted_quantiles, name="predicted_quantiles")
    n, q_count = predictions.shape
    target = _vector(y, n, name="calibration_y")
    declared_quantiles = _validate_quantile_levels(quantiles)
    if len(declared_quantiles) != q_count:
        raise BackendInputError("quantiles do not match supplied prediction columns")
    if not isinstance(source_fit_id, str) or not source_fit_id or not isinstance(calibration_id, str) or not calibration_id:
        raise BackendInputError("quantile calibration needs source and calibration identities")
    sample_weights = _weights(weights, n)
    input_digest = _array_digest(predictions, target, sample_weights)
    total = float(sample_weights.sum())
    if n == 0:
        corrections = np.zeros(q_count, dtype=np.float64)
        status = "empty_fallback"
    else:
        # Calibrate each declared quantile with the same quantile of its
        # weighted residual distribution.  A weighted mean would erase the
        # tail-specific correction needed for the first/second movement
        # targets and was therefore not an admissible calibration rule.
        corrections = np.asarray([
            _weighted_quantile(target - predictions[:, j], sample_weights, declared_quantiles[j])
            for j in range(q_count)
        ])
        status = "converged"
    result_metadata = _metadata(metadata)
    result_metadata.update({"method": "weighted_residual_quantile", "input_digest": input_digest,
                            "residual_quantile_levels": list(declared_quantiles),
                            "crossing_correction": "prediction_only_maximum_accumulate"})
    return QuantileResidualCalibration(declared_quantiles, tuple(float(v) for v in corrections),
                                       source_fit_id, calibration_id, input_digest, n, total, status,
                                       result_metadata)


def predict_quantile_residual(calibration: QuantileResidualCalibration, predicted_quantiles: Any,
                              *, correct_crossing: bool = True,
                              return_diagnostics: bool = False,
                              allow_fallback: bool = False) -> np.ndarray | tuple[np.ndarray, dict[str, Any]]:
    if type(calibration) is not QuantileResidualCalibration:
        raise BackendInputError("typed QuantileResidualCalibration required")
    if calibration.status != "converged" and not allow_fallback:
        raise BackendInputError("quantile calibration did not converge; pass allow_fallback=True explicitly")
    predictions = _matrix(predicted_quantiles, name="predicted_quantiles")
    if predictions.shape[1] != len(calibration.quantiles):
        raise BackendInputError("prediction columns differ from calibration quantiles")
    raw = predictions + np.asarray(calibration.corrections, dtype=np.float64)[None, :]
    before = _crossing_count(raw)
    corrected = np.maximum.accumulate(raw, axis=-1) if correct_crossing else raw
    after = _crossing_count(corrected)
    diagnostics = {"crossing_correction": "maximum_accumulate" if correct_crossing else "none",
                   "rows_with_crossing_before": before, "rows_with_crossing_after": after}
    return (corrected, diagnostics) if return_diagnostics else corrected


@dataclass(frozen=True)
class HGBChallenger:
    task: str
    status: str
    trigger: bool
    reason: str
    configuration: dict[str, Any]
    n_rows: int
    feature_count: int
    iterations: int | None
    failure: str | None
    estimator: Any = field(default=None, repr=False, compare=False)
    provider_versions: dict[str, str] = field(default_factory=lambda: {
        "numpy": NUMPY_PROVIDER, "scikit_learn": SKLEARN_PROVIDER,
    })
    payload_sha256: str | None = None
    payload_b64: str | None = field(default=None, repr=False, compare=False)
    local_origin: str = "local_sklearn"
    # The registered challenger keeps its declared output simplex explicit.
    # sklearn may omit a class that is absent from a particular training fold;
    # prediction expands the estimator output back to this tuple.
    classes: tuple[Any, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        payload = self.payload_b64
        payload_hash = self.payload_sha256
        if self.estimator is not None and payload is None:
            raw = pickle.dumps(self.estimator, protocol=5)
            payload = base64.b64encode(raw).decode("ascii")
            payload_hash = hashlib.sha256(raw).hexdigest()
        return _jsonable({"kind": "HGBChallengerV1", "task": self.task, "status": self.status,
                          "trigger": self.trigger, "reason": self.reason,
                          "configuration": self.configuration, "n_rows": self.n_rows,
                          "feature_count": self.feature_count, "iterations": self.iterations,
                          "failure": self.failure, "provider_versions": self.provider_versions,
                          "payload_sha256": payload_hash, "estimator_payload": payload,
                          "local_origin": self.local_origin, "classes": self.classes})

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], *, require_local_origin: bool = True) -> "HGBChallenger":
        if not isinstance(value, Mapping):
            raise BackendInputError("HGB wire value must be an object")
        if value.get("kind") != "HGBChallengerV1":
            raise BackendInputError("wrong HGB challenger wire kind")
        provider_versions = dict(value.get("provider_versions", {}))
        expected_versions = {"numpy": NUMPY_PROVIDER, "scikit_learn": SKLEARN_PROVIDER}
        if provider_versions != expected_versions:
            raise BackendInputError("HGB provider versions do not match the registered backend")
        local_origin = value.get("local_origin")
        if require_local_origin and local_origin != "local_sklearn":
            raise BackendInputError("HGB payload lacks the required local-origin marker")
        payload = value.get("estimator_payload")
        payload_hash = value.get("payload_sha256")
        estimator = None
        if payload is not None:
            if not isinstance(payload, str) or not isinstance(payload_hash, str):
                raise BackendInputError("HGB estimator payload and hash must be paired")
            try:
                raw = base64.b64decode(payload.encode("ascii"), validate=True)
            except (ValueError, UnicodeError) as exc:
                raise BackendInputError("invalid HGB estimator payload encoding") from exc
            if hashlib.sha256(raw).hexdigest() != payload_hash:
                raise BackendInputError("HGB estimator payload hash mismatch")
            try:
                estimator = pickle.loads(raw)
            except Exception as exc:
                raise BackendInputError("HGB estimator payload could not be restored") from exc
        elif str(value.get("status", "")).startswith("completed"):
            raise BackendInputError("completed HGB challenger must carry a restorable payload")
        task = str(value["task"])
        configuration = _metadata(value.get("configuration", {}))
        if task not in {"classification", "regression"}:
            raise BackendInputError("invalid HGB task in wire record")
        loss = configuration.get("loss", "squared_error" if task == "regression" else "log_loss")
        configuration.setdefault("loss", loss)
        configuration.setdefault("quantile", None)
        prior = configuration.get("missing_class_prior", _HGB_MISSING_CLASS_PRIOR)
        if (not isinstance(prior, (int, float)) or isinstance(prior, bool)
                or not math.isfinite(float(prior)) or float(prior) < 0):
            raise BackendInputError("invalid HGB missing-class prior in wire record")
        configuration["missing_class_prior"] = float(prior)
        min_samples_leaf = configuration.get("min_samples_leaf", 20)
        if (type(min_samples_leaf) is not int or not 1 <= min_samples_leaf <= 10_000):
            raise BackendInputError("invalid HGB min_samples_leaf in wire record")
        configuration["min_samples_leaf"] = min_samples_leaf
        quantile = configuration.get("quantile")
        if task == "regression":
            if loss not in {"squared_error", "quantile"}:
                raise BackendInputError("invalid HGB regression loss in wire record")
            if loss == "quantile" and (not isinstance(quantile, (int, float))
                                        or isinstance(quantile, bool)
                                        or not math.isfinite(float(quantile))
                                        or not 0 < float(quantile) < 1):
                raise BackendInputError("quantile HGB wire record needs a quantile in (0,1)")
            if loss == "squared_error" and quantile is not None:
                raise BackendInputError("squared-error HGB wire record cannot carry a quantile")
        elif loss != "log_loss" or quantile is not None:
            raise BackendInputError("classification HGB wire record must use log_loss")
        classes_value = value.get("classes", configuration.get("declared_classes", ()))
        if task == "classification" and not classes_value and estimator is not None:
            classes_value = getattr(estimator, "classes_", ())
        classes = _classes(classes_value) if task == "classification" else ()
        return cls(
            task=task, status=str(value["status"]), trigger=bool(value["trigger"]),
            reason=str(value["reason"]), configuration=configuration,
            n_rows=int(value["n_rows"]), feature_count=int(value["feature_count"]),
            iterations=None if value.get("iterations") is None else int(value["iterations"]),
            failure=value.get("failure"), estimator=estimator,
            provider_versions=provider_versions, payload_sha256=payload_hash,
            payload_b64=payload, local_origin=str(local_origin), classes=classes,
        )


def fit_hgb_challenger(
    X: Any,
    y: Any,
    weights: Any = None,
    *,
    task: str,
    trigger: bool,
    reason: str,
    max_iter: int = 200,
    max_leaf_nodes: int = 15,
    min_samples_leaf: int = 20,
    learning_rate: float = 0.05,
    max_bins: int = 64,
    l2_regularization: float = 1.0,
    random_state: int = 20260907,
    loss: str | None = None,
    quantile: float | None = None,
    classes: Sequence[Any] | None = None,
) -> HGBChallenger:
    """Optional fixed-capacity sklearn challenger; no trigger means no fit."""
    matrix = _matrix(X)
    n, p = matrix.shape
    values = np.asarray(y)
    if values.ndim != 1 or len(values) != n:
        raise BackendInputError("HGB y must be a length-N vector")
    sample_weights = _weights(weights, n)
    if task not in {"classification", "regression"}:
        raise BackendInputError("HGB task must be classification or regression")
    if task == "regression":
        resolved_loss = "squared_error" if loss is None else loss
        if resolved_loss not in {"squared_error", "quantile"}:
            raise BackendInputError("HGB regression loss must be squared_error or quantile")
        if resolved_loss == "quantile":
            if (not isinstance(quantile, (int, float)) or isinstance(quantile, bool)
                    or not math.isfinite(float(quantile)) or not 0 < float(quantile) < 1):
                raise BackendInputError("quantile HGB regression needs a quantile in (0,1)")
            resolved_quantile = float(quantile)
        else:
            if quantile is not None:
                raise BackendInputError("squared-error HGB cannot carry a quantile")
            resolved_quantile = None
        declared_classes = ()
    else:
        resolved_loss = "log_loss" if loss is None else loss
        if resolved_loss != "log_loss" or quantile is not None:
            raise BackendInputError("classification HGB must use log_loss")
        observed_classes = tuple(np.unique(values).tolist())
        declared_classes = _classes(observed_classes if classes is None else classes)
        try:
            declared_set = set(declared_classes)
            if any(value not in declared_set for value in values.tolist()):
                raise BackendInputError("classification labels are outside declared classes")
        except TypeError as exc:
            raise BackendInputError("classification labels must be hashable") from exc
        resolved_quantile = None
    configuration = {"early_stopping": False, "max_iter": max_iter, "max_leaf_nodes": max_leaf_nodes,
                     "min_samples_leaf": min_samples_leaf,
                     "learning_rate": learning_rate, "max_bins": max_bins,
                     "l2_regularization": l2_regularization, "random_state": random_state,
                     "loss": resolved_loss, "quantile": resolved_quantile,
                     "declared_classes": list(declared_classes),
                     "missing_class_prior": _HGB_MISSING_CLASS_PRIOR,
                     "thread_policy": "threadpoolctl.limits(1)", "thread_limit": 1}
    if not trigger:
        return HGBChallenger(task, "not_run", False, reason, configuration, n, p, None, None,
                             classes=declared_classes)
    if (type(max_iter) is not int or not 1 <= max_iter <= 500
            or type(max_leaf_nodes) is not int or not 2 <= max_leaf_nodes <= 64
            or type(min_samples_leaf) is not int or not 1 <= min_samples_leaf <= 10_000):
        raise BackendInputError("HGB capacity is outside the fixed bound")
    if not math.isfinite(float(learning_rate)) or learning_rate <= 0 or type(max_bins) is not int or not 2 <= max_bins <= 255:
        raise BackendInputError("invalid HGB capacity/configuration")
    if not math.isfinite(float(l2_regularization)) or l2_regularization < 0:
        raise BackendInputError("invalid HGB l2 regularization")
    try:
        from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
        estimator_type = HistGradientBoostingClassifier if task == "classification" else HistGradientBoostingRegressor
        estimator_configuration = {key: value for key, value in configuration.items()
                                   if key not in {"thread_policy", "thread_limit", "declared_classes", "quantile",
                                                  "missing_class_prior"}}
        if task == "regression" and resolved_loss == "quantile":
            estimator_configuration["quantile"] = resolved_quantile
        estimator = estimator_type(**estimator_configuration)
        from threadpoolctl import threadpool_limits
        with threadpool_limits(limits=1):
            estimator.fit(matrix, values, sample_weight=sample_weights)
        iterations = int(getattr(estimator, "n_iter_", max_iter))
        status = "completed_fixed_iter" if iterations == max_iter else "completed"
        raw_payload = pickle.dumps(estimator, protocol=5)
        payload_b64 = base64.b64encode(raw_payload).decode("ascii")
        payload_hash = hashlib.sha256(raw_payload).hexdigest()
        return HGBChallenger(task, status, True, reason, configuration, n, p, iterations, None,
                             estimator, {"numpy": NUMPY_PROVIDER, "scikit_learn": SKLEARN_PROVIDER},
                             payload_hash, payload_b64, "local_sklearn", declared_classes)
    except Exception as exc:  # The caller must report, rather than hide, a failed challenger.
        return HGBChallenger(task, "failed", True, reason, configuration, n, p, None,
                             f"{type(exc).__name__}: {exc}", None, classes=declared_classes)


def predict_hgb_challenger(fit: HGBChallenger, X: Any) -> np.ndarray:
    if type(fit) is not HGBChallenger or fit.estimator is None or fit.status in {"not_run", "failed"}:
        raise BackendInputError("a completed HGB challenger is required for prediction")
    matrix = _matrix(X)
    if matrix.shape[1] != fit.feature_count:
        raise BackendInputError("prediction feature count differs from HGB challenger")
    from threadpoolctl import threadpool_limits
    with threadpool_limits(limits=1):
        if fit.task == "classification":
            observed = np.asarray(fit.estimator.predict_proba(matrix), dtype=np.float64)
            estimator_classes = tuple(np.asarray(getattr(fit.estimator, "classes_", fit.classes)).tolist())
            declared = fit.classes or estimator_classes
            if observed.ndim != 2 or observed.shape[1] != len(estimator_classes):
                raise BackendInputError("HGB classifier returned an invalid probability simplex")
            if len(declared) < len(estimator_classes):
                raise BackendInputError("declared HGB classes omit an estimator class")
            try:
                indices = [declared.index(value) for value in estimator_classes]
            except ValueError as exc:
                raise BackendInputError("HGB estimator returned an undeclared class") from exc
            epsilon = float(fit.configuration.get("missing_class_prior", _HGB_MISSING_CLASS_PRIOR))
            if not math.isfinite(epsilon) or epsilon < 0:
                raise BackendInputError("HGB missing-class prior is invalid")
            values = np.full((len(matrix), len(declared)), epsilon, dtype=np.float64)
            values[:, indices] += observed
            values /= values.sum(axis=1, keepdims=True)
        else:
            values = fit.estimator.predict(matrix)
    result = np.asarray(values)
    if not np.isfinite(result).all():
        raise BackendInputError("HGB prediction became non-finite")
    return result
