"""Shrunken grouped probabilities with compatible-set observations.

Rows represent one declared root/clock/horizon/date. Group pseudo-counts
therefore have units of dates; the pooled prior separately uses equal-date
weights so repeated clocks do not turn into independent dates.
"""
import numpy as np

from trading_research.errors import ContractError
from trading_research.operations.artifacts import digest


def _allowed(values, classes):
    value = np.asarray(values)
    if value.dtype == np.bool_:
        if value.ndim != 2 or value.shape[1] != classes or np.any(~value.any(axis=1)):
            raise ContractError("nonempty compatible classes required")
        return value
    if value.ndim != 1 or value.dtype.kind not in "iu" or np.any(value < 0) or np.any(value >= classes):
        raise ContractError("integer class index or compatible boolean matrix required")
    return value[:, None] == np.arange(classes)


def _em(allowed, groups, weights, prior, strength, initial, iterations, tolerance):
    p = initial.copy()
    n_groups, classes = p.shape
    informative = ~allowed.all(axis=1)
    a, g, w = allowed[informative], groups[informative], weights[informative]
    counts = np.bincount(g, weights=w, minlength=n_groups)
    change, objective, gain, converged = 0.0, None, None, not len(a)
    used = 0
    for at in range(iterations if len(a) else 0):
        joint = p[g] * a
        normalizer = joint.sum(axis=1)
        if np.any(normalizer <= 0):
            raise ContractError("positive compatible likelihood required")
        responsibilities = joint * (w / normalizer)[:, None]
        expected = np.column_stack([np.bincount(g, weights=responsibilities[:, k], minlength=n_groups)
                                    for k in range(classes)])
        updated = (expected + strength * prior) / (counts[:, None] + strength)
        change = float(np.max(np.abs(updated - p)))
        p = updated
        used = at + 1
        value = float(np.dot(w, np.log((p[g] * a).sum(axis=1)))
                      + strength * np.sum(prior * np.log(p)))
        if objective is not None:
            gain = value - objective
            if gain < -1e-9 * max(1.0, abs(value)):
                raise ContractError("compatible-set EM decreased its penalized likelihood")
        objective = value
        if change <= tolerance:
            converged = True
            break
    return p, {"converged": converged, "iterations": used, "maximum_probability_change": change,
               "penalized_log_likelihood": objective, "last_objective_gain": gain,
               "informative_rows": int(informative.sum()), "all_class_rows": int((~informative).sum()),
               "group_information_weight": counts.tolist()}


def fit_grouped_distribution(values, groups, dates, *, classes, group_count, shrinkage=20.0,
                             max_iterations=120, tolerance=1e-7):
    if (type(classes) is not int or classes < 2 or type(group_count) is not int or group_count < 1
            or not np.isfinite(shrinkage) or shrinkage <= 0
            or type(max_iterations) is not int or not 1 <= max_iterations <= 1000
            or not np.isfinite(tolerance) or tolerance <= 0):
        raise ContractError("bounded categorical prior specification required")
    allowed = _allowed(values, classes)
    g, d = np.asarray(groups), np.asarray(dates)
    if (g.dtype != np.int64 or d.dtype != np.int64 or g.shape != (len(allowed),) or d.shape != g.shape
            or np.any(g < 0) or np.any(g >= group_count) or np.any(d <= 0)):
        raise ContractError("aligned exact group and date identities required")
    if len(np.unique(np.column_stack((g, d)), axis=0)) != len(g):
        raise ContractError("group-frequency observations require one row per intended group/date")
    # Global prior mass counts each actual date once across its available
    # groups. An all-class row supplies no likelihood information.
    informative = ~allowed.all(axis=1)
    global_weights = np.zeros(len(d))
    if informative.any():
        _, inverse, counts = np.unique(d[informative], return_inverse=True, return_counts=True)
        global_weights[informative] = 1.0 / counts[inverse]
    uniform = np.full((1, classes), 1.0 / classes)
    pooled, pooled_diagnostics = _em(allowed, np.zeros(len(g), dtype=np.int64), global_weights,
                                     uniform, 1.0, uniform, max_iterations, tolerance)
    probabilities, diagnostics = _em(allowed, g, np.ones(len(g)), pooled[0], shrinkage,
                                      np.repeat(pooled, group_count, axis=0), max_iterations, tolerance)
    record = {"kind": "jumbo-grouped-compatible-distribution-v1", "classes": classes,
              "group_count": group_count, "probabilities": probabilities.tolist(),
              "global_probabilities": pooled[0].tolist(), "shrinkage_date_mass": shrinkage,
              "training_rows": len(g), "training_date_count": len(np.unique(d)),
              "max_iterations": max_iterations, "tolerance": tolerance,
              "global_diagnostics": pooled_diagnostics, "group_diagnostics": diagnostics,
              "converged": pooled_diagnostics["converged"] and diagnostics["converged"],
              "weighting": "One group row per date; equal-date pooled prior over informative rows; all-class rows have no influence. Per-group Dirichlet MAP alpha_k=1+shrinkage_date_mass*pooled_p_k",
              "fit_digest": digest({"allowed": allowed.tobytes(), "groups": g.tobytes(), "dates": d.tobytes()})}
    record["id"] = digest(record)
    return record


def predict_grouped_distribution(record, groups, *, allow_declared_fallback=False):
    if record.get("kind") != "jumbo-grouped-compatible-distribution-v1":
        raise ContractError("wrong grouped-distribution model kind")
    if not record["converged"] and not allow_declared_fallback:
        raise ContractError("nonconverged grouped distribution cannot emit accepted predictions")
    g = np.asarray(groups)
    if g.dtype != np.int64 or g.ndim != 1 or np.any(g < 0) or np.any(g >= record["group_count"]):
        raise ContractError("declared exact prediction groups required")
    # A failed fit can only fall back to a declared uniform law. Failed EM
    # parameters are not relabeled as a successfully estimated baseline.
    if not record["converged"]:
        return np.full((len(g), record["classes"]), 1.0 / record["classes"])
    p = np.asarray(record["probabilities"], dtype=np.float64)
    if (p.shape != (record["group_count"], record["classes"]) or not np.isfinite(p).all()
            or np.any(p <= 0) or not np.allclose(p.sum(axis=1), 1, atol=1e-12, rtol=0)):
        raise ContractError("invalid stored grouped probability simplex")
    return p[g]
