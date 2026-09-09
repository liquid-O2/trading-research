"""One chronological fit/calibrate/evaluate path for admitted Jumbo targets.

This module is invoked only by the registered worker. Numerical records and
all comparisons are returned to the caller for immutable, bounded publication.
There is no hidden random validation split or row subsampling.
"""
from datetime import date
import hashlib
import math
import time
import numpy as np

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest
from trading_research.research import jumbo_model_backend as backend
from trading_research.research.jumbo_baselines import fit_grouped_distribution, predict_grouped_distribution
from trading_research.research.jumbo_matrix import FEATURES, feature_names, fit_feature_transform, transformed_features
from trading_research.research.jumbo_model_evaluation import categorical_metrics, quantile_metrics, grouped_date_evaluation
from trading_research.research.jumbo_targets import PHASES, boundary_ns, group_ids, decode_group


VERSION = "jumbo-chronological-context-v1"


def json_safe(value, *, omit_date_vectors=False):
    """Retain missing numerical results as JSON null with support alongside."""
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist(), omit_date_vectors=omit_date_vectors)
    if isinstance(value, np.generic):
        return json_safe(value.item(), omit_date_vectors=omit_date_vectors)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): json_safe(v, omit_date_vectors=omit_date_vectors) for k, v in value.items()
                if not (omit_date_vectors and k in ("date_values", "intended_dates"))}
    if isinstance(value, (list, tuple)):
        return [json_safe(v, omit_date_vectors=omit_date_vectors) for v in value]
    return value


def date_weights(dates):
    days = np.asarray(dates)
    if days.dtype != np.int64 or days.ndim != 1 or np.any(days <= 0):
        raise ContractError("exact positive date ordinals required")
    if not len(days):
        return np.empty(0)
    _, inverse, counts = np.unique(days, return_inverse=True, return_counts=True)
    # Mean row weight one helps tree leaf regularization retain its declared
    # scale; each date nevertheless has exactly the same total weight.
    return len(days) / len(counts) / counts[inverse]


def date_mean(values, dates):
    values, dates = np.asarray(values, dtype=np.float64), np.asarray(dates)
    if values.shape != dates.shape:
        raise ContractError("score/date alignment required")
    keep = np.isfinite(values)
    if not keep.any():
        return None
    unique, inverse = np.unique(dates[keep], return_inverse=True)
    total = np.bincount(inverse, weights=values[keep], minlength=len(unique))
    count = np.bincount(inverse, minlength=len(unique))
    return float(np.mean(total / count))


def _phase_rows(matrix, phase):
    first, last, _ = PHASES[phase]
    return matrix.phase(first, last)


def _identity(record):
    value = dict(record)
    value.pop("id", None)
    return digest(value)


def _seal(record):
    record = json_safe(record)
    record["id"] = _identity(record)
    return record


def _fit_metadata(matrix, target, mask, *, phase="fit"):
    if not mask.any():
        return {"phase": phase, "rows": 0, "dates": 0, "matrix_id": matrix.manifest["id"]}
    return {"phase": phase, "rows": int(mask.sum()), "dates": int(len(np.unique(matrix.fields["date"][mask]))),
            "first_date": date.fromordinal(int(matrix.fields["date"][mask].min())).isoformat(),
            "last_date": date.fromordinal(int(matrix.fields["date"][mask].max())).isoformat(),
            "latest_label_known_at_ns": int(target.label_known_at_ns[mask].max()),
            "matrix_id": matrix.manifest["id"], "target_id": target.metadata["id"],
            "original_row_indices_sha256": hashlib.sha256(np.flatnonzero(mask).astype(np.int64).tobytes()).hexdigest()}


def _target_binding(target, target_index):
    """Bind calibration to target semantics without binding it to a matrix ID."""
    if type(target_index) is not int or target_index < 0:
        raise ContractError("nonnegative target index required")
    metadata = dict(target.metadata)
    # target_catalog derives ``metadata['id']`` from the full metadata,
    # including source_matrix.  That artifact identity legitimately differs
    # between first/held-out PreparedPaths, so remove it (and the derived id)
    # before calculating the semantic definition digest.
    metadata.pop("id", None)
    metadata.pop("source_matrix", None)
    target_id = metadata.get("target", target.name)
    if not isinstance(target_id, str) or not target_id:
        raise IntegrityError("target metadata needs a stable semantic name")
    return {
        "target_id": target_id,
        "target_name": target.name,
        "target_index": int(target_index),
        "target_kind": target.kind,
        "definition_digest": digest(metadata),
    }


def _basis(matrix, transform, mask, kind):
    x = transformed_features(matrix, transform, mask)
    if kind == "linear":
        return x
    if kind != "bounded_interactions_v1":
        raise ContractError("unknown nonlinear basis")
    chosen = [name for name in ("width_prior_ratio", "last_close_position", "open_position",
                                "cut_ny_minutes", "prefix_return_W", "prefix_up_W", "prefix_down_W")
              if name in transform["names"]]
    indices = [transform["names"].index(name) for name in chosen]
    # A fixed smooth bounded basis adds capacity without changing information.
    # Original unbounded standardized features and missing masks are retained.
    z = np.tanh(x[:, indices] / 3)
    extras = [z * z, z * z * z]
    products = [z[:, a] * z[:, b] for a in range(len(indices)) for b in range(a + 1, len(indices))]
    if products:
        extras.append(np.column_stack(products))
    return np.column_stack((x, *extras))


def _baseline_prob(record, groups):
    return predict_grouped_distribution(record["baseline"], groups, allow_declared_fallback=True)


def _baseline_quantiles(record, groups):
    from trading_research.research.jumbo_prior_storage import SCHEMA, predict_quantile_serving
    values = []
    for wire in record["baseline"]:
        if wire.get('kind') == SCHEMA:
            values.append(predict_quantile_serving(wire, groups.tolist()))
        else:
            fit = backend.EmpiricalQuantileFit.from_dict(wire)
            values.append(backend.predict_empirical_quantiles(fit, groups.tolist()))
    return np.stack(values, axis=1)


def _append_baseline_quantile_features(features, baseline, scales):
    """Append the complete target-by-quantile prior in a fixed column order."""
    features = np.asarray(features, dtype=np.float64)
    baseline = np.asarray(baseline, dtype=np.float64)
    scales = np.asarray(scales, dtype=np.float64)
    if baseline.ndim != 3 or baseline.shape[0] != features.shape[0] or baseline.shape[1] != len(scales):
        raise ContractError("baseline quantile feature shape is not aligned with rows/targets")
    if not np.isfinite(scales).all() or np.any(scales <= 0):
        raise IntegrityError("target scales must be positive finite values")
    scaled = baseline / scales[None, :, None]
    return np.column_stack((features, scaled.reshape(features.shape[0], -1)))


def predict_model(record, matrix, mask):
    """Return final and raw forecasts; no estimation or calibration fitting."""
    if record.get("id") != _identity(record):
        raise IntegrityError("stored Context model record changed")
    selected = np.asarray(mask)
    if selected.dtype != np.bool_ or selected.shape != (matrix.size,):
        raise ContractError("aligned explicit prediction row mask required")
    if record["feature_names"] != list(feature_names(matrix)):
        raise IntegrityError("Context feature layout changed")
    if not selected.any():
        shape = (0, record["baseline"]["classes"]) if record["target_kind"] != "continuous" else (0, len(record["target_names"]), len(record["quantiles"]))
        empty = np.empty(shape, dtype=np.float64)
        return empty, empty
    g = group_ids(matrix)[selected]
    kind = record["kind"]
    if record["target_kind"] in ("categorical", "interval_categorical"):
        base = _baseline_prob(record, g)
        if kind == "empirical":
            return base, base
        x = _basis(matrix, record["transform"], selected, record.get("basis", "linear"))
        if kind == "softmax":
            if not record["backend"]["converged"]:
                # Failure is visible in the model status and retains the
                # already fitted common comparator as the emitted fallback.
                return base, base
            offset = np.log(base)
            p = backend.predict_softmax(backend.SoftmaxFit.from_dict(record["backend"]), x,
                    offset_logits=offset, offset_identity=record["baseline"]["id"],
                    offset_checksum=backend.offset_array_checksum(offset))
        elif kind == "hgb":
            if record["backend"]["status"] in ("failed", "not_run"):
                return base, base
            fit = backend.HGBChallenger.from_dict(record["backend"])
            raw = backend.predict_hgb_challenger(fit, np.column_stack((x, np.log(base))))
            # The backend owns restoration of estimator classes into the
            # declared simplex.  Re-scattering here would double-place those
            # columns when a fold omitted a class.
            p = np.asarray(raw, dtype=np.float64)
            if p.shape != base.shape or not np.isfinite(p).all():
                raise IntegrityError("HGB emitted a non-declared categorical simplex")
            smoothing = record["probability_prior_mix"]
            p = (1 - smoothing) * p + smoothing * base
        else:
            raise ContractError("unknown categorical learner")
        return p, p
    base = _baseline_quantiles(record, g)
    if kind == "empirical":
        raw = base
    else:
        x = _basis(matrix, record["transform"], selected, record.get("basis", "linear"))
        scales = np.asarray(record["target_scales"])
        x = _append_baseline_quantile_features(x, base, scales)
        if kind == "quantile":
            if not record["backend"]["converged"]:
                raw = base
            else:
                offset = base / scales[None, :, None]
                _, scaled_raw = backend.predict_quantiles(backend.QuantileFit.from_dict(record["backend"]), x,
                      offset_quantiles=offset, offset_identity=record["baseline_id"],
                      offset_checksum=backend.offset_array_checksum(offset), return_raw=True)
                raw = scaled_raw * scales[None, :, None]
        elif kind == "hgb_quantiles":
            raw = np.empty_like(base)
            for t, fits in enumerate(record["backend"]):
                if fits is None:
                    raw[:, t, :] = base[:, t, :]
                    continue
                for q, wire in enumerate(fits):
                    if wire["status"] in ("failed", "not_run"):
                        raw[:, t, q] = base[:, t, q]
                    else:
                        fit = backend.HGBChallenger.from_dict(wire)
                        # Same available information as the regularized head,
                        # including its shrunken source/horizon prior.
                        features = x
                        raw[:, t, q] = backend.predict_hgb_challenger(fit, features) * scales[t]
        else:
            raise ContractError("unknown continuous learner")
    final = np.maximum.accumulate(raw, axis=-1)
    for t, nonnegative in enumerate(record["nonnegative"]):
        if nonnegative:
            final[:, t] = np.maximum(final[:, t], 0)
    return final, raw


def _class_score(target, values, prediction):
    if target.kind == "interval_categorical":
        scored = categorical_metrics(prediction, allowed_class_matrix=values)
        primary = scored["per_row"]["interval_log_loss"]
    else:
        scored = categorical_metrics(prediction, observed_class=values)
        primary = scored["per_row"]["log_loss"]
    return primary, scored


def _scalar_score(target, values, prediction, quantiles):
    if target.kind in ("categorical", "interval_categorical"):
        return _class_score(target, values, prediction)[0]
    q = np.asarray(quantiles)
    residual = values[:, None] - prediction
    return np.mean(np.maximum(q * residual, (q - 1) * residual), axis=1)


def fit_categorical_family(matrix, target, *, plan):
    eligible_mask = target.phase(matrix, "fit")
    mask = eligible_mask.copy()
    if target.kind == "interval_categorical":
        mask &= target.values.sum(axis=1) < target.values.shape[1]
    metadata = _fit_metadata(matrix, target, mask)
    metadata.update(eligible_training_rows=int(eligible_mask.sum()),
                    all_class_uninformative_rows=int((eligible_mask & ~mask).sum()))
    if metadata["dates"] < plan["minimum_fit_dates"]:
        return {"target": target.name, "status": "insufficient_training_dates", "fit": metadata, "models": {}}
    g = group_ids(matrix)
    classes = list(range(len(target.metadata["classes"])))
    clock_count = len(matrix.categories["root"]) * len(matrix.categories["clock"]) * len(matrix.categories["horizon"])
    start = time.process_time()
    baseline = fit_grouped_distribution(target.values[mask], g[mask], matrix.fields["date"][mask],
                 classes=len(classes), group_count=clock_count, shrinkage=plan["prior_date_mass"],
                 max_iterations=plan["prior_max_iterations"], tolerance=plan["prior_tolerance"])
    shared = {"version": VERSION, "target_names": [target.name], "target_kind": target.kind,
              "target_metadata": [target.metadata], "feature_names": list(feature_names(matrix)), "fit": metadata,
              "baseline": baseline, "fallback": "exact declared grouped comparator; numerical failure is not a successful capacity comparison"}
    models = {"empirical": _seal({**shared, "kind": "empirical", "name": "empirical",
                                    "status": "fitted" if baseline["converged"] else "failed_uniform_fallback",
                                    "cpu_seconds": time.process_time() - start})}
    weights = date_weights(matrix.fields["date"][mask])
    offset = np.log(_baseline_prob(shared, g[mask]))
    for configuration in plan["linear_variants"]:
        start = time.process_time()
        group, basis, name = configuration["group"], configuration["basis"], configuration["name"]
        transform = fit_feature_transform(matrix, mask, group=group)
        x = _basis(matrix, transform, mask, basis)
        fitted = backend.fit_softmax(x, target.values[mask], weights, classes=classes,
                  l2=configuration["l2"], max_iterations=plan["solver_max_iterations"], tolerance=plan["solver_tolerance"],
                  offset_logits=offset, offset_identity=baseline["id"], metadata=metadata)
        models[name] = _seal({**shared, "kind": "softmax", "name": name, "transform": transform,
                             "basis": basis, "backend": fitted.as_dict(),
                             "status": "fitted" if fitted.converged else "failed_empirical_fallback",
                             "cpu_seconds": time.process_time() - start})
        del x
    if target.kind == "categorical" and target.name in plan["hgb_categorical_targets"]:
        start = time.process_time()
        transform = fit_feature_transform(matrix, mask, group="full")
        x = np.column_stack((_basis(matrix, transform, mask, "linear"), offset))
        hgb = backend.fit_hgb_challenger(x, target.values[mask], weights, task="classification", trigger=True,
                 reason=plan["hgb_reason"], classes=classes, **plan["hgb_configuration"])
        models["hgb_full"] = _seal({**shared, "kind": "hgb", "name": "hgb_full", "transform": transform,
                       "basis": "linear", "backend": hgb.as_dict(), "probability_prior_mix": plan["hgb_probability_prior_mix"],
                       "status": "fitted" if hgb.status not in ("failed", "not_run") else "failed_empirical_fallback",
                       "cpu_seconds": time.process_time() - start})
        del x
    return {"target": target.name, "status": "compared", "fit": metadata, "models": models}


def fit_continuous_family(matrix, targets, *, plan, prior_writer=None):
    if not targets or any(t.kind != "continuous" for t in targets):
        raise ContractError("one or more continuous targets required")
    masks = [t.phase(matrix, "fit") for t in targets]
    if any(not np.array_equal(masks[0], m) for m in masks[1:]):
        raise ContractError("joint numerical fitting requires exactly equal training row populations; do not intersect targets")
    mask = masks[0]
    metadata = [_fit_metadata(matrix, t, mask) for t in targets]
    if metadata[0]["dates"] < plan["minimum_fit_dates"]:
        return {"targets": [t.name for t in targets], "status": "insufficient_training_dates", "fit": metadata, "models": {}}
    g = group_ids(matrix)
    y = np.column_stack([t.values[mask] for t in targets])
    levels = plan["quantiles"]
    weights = date_weights(matrix.fields["date"][mask])
    start = time.process_time()
    # Local group/date masses stay equal (one admitted row per group/date),
    # while the pooled prior gives each calendar date equal influence even
    # when that date contributes a different number of clocks.
    local_weights = np.ones(len(y), dtype=np.float64)
    global_weights = date_weights(matrix.fields["date"][mask])
    baselines = [backend.fit_empirical_quantiles(
                    y[:, t], local_weights, quantiles=levels,
                    shrinkage=plan["prior_date_mass"], group_ids=g[mask].tolist(),
                    global_weights=global_weights, metadata=metadata[t]).as_dict()
                 for t in range(len(targets))]
    baseline_id = digest(baselines)
    from trading_research.research.jumbo_prior_storage import quantile_serving_record, FAMILY_SCHEMA
    serving_baselines = [quantile_serving_record(wire) for wire in baselines]
    if prior_writer is None:
        retained_priors = {'empirical_distribution_evidence': baselines}
    else:
        # Publish the complete calculator output once before larger numerical
        # designs are allocated. Models use its exact serving fields below.
        retained_priors = {'empirical_distribution_artifact': prior_writer(baselines)}
    del baselines
    scales = np.maximum(np.quantile(y, .9, axis=0) - np.quantile(y, .1, axis=0), 1e-6)
    shared = {"version": VERSION, "target_names": [t.name for t in targets], "target_kind": "continuous",
              "target_metadata": [t.metadata for t in targets], "feature_names": list(feature_names(matrix)), "fit": metadata,
              "baseline": serving_baselines, "baseline_id": baseline_id, "quantiles": levels,
              "target_scales": scales.tolist(), "nonnegative": [t.metadata.get("nonnegative", False) for t in targets],
              "target_scale_rule": "Fit-only pooled type7 q90-q10, minimum1e-6; no clipping or sample removal; emitted outputs scored in original target units",
              "fallback": "same grouped empirical quantiles, explicitly counted as a numerical failure"}
    models = {"empirical": _seal({**shared, "kind": "empirical", "name": "empirical", "status": "fitted",
                                    "cpu_seconds": time.process_time() - start})}
    offset = _baseline_quantiles(shared, g[mask]) / scales[None, :, None]
    for configuration in plan["linear_variants"]:
        start = time.process_time()
        group, basis, name = configuration["group"], configuration["basis"], configuration["name"]
        transform = fit_feature_transform(matrix, mask, group=group)
        x = _append_baseline_quantile_features(
            _basis(matrix, transform, mask, basis),
            _baseline_quantiles(shared, g[mask]), scales,
        )
        fitted = backend.fit_quantiles(x, y / scales, weights, quantiles=levels, l2=configuration["l2"],
                   max_iterations=plan["solver_max_iterations"], tolerance=plan["solver_tolerance"],
                   smooth_epsilon=plan["smooth_pinball_epsilon"], offset_quantiles=offset,
                   offset_identity=baseline_id, metadata={"targets": metadata})
        models[name] = _seal({**shared, "kind": "quantile", "name": name, "transform": transform,
                             "basis": basis, "backend": fitted.as_dict(),
                             "status": "fitted" if fitted.converged else "failed_empirical_fallback",
                             "cpu_seconds": time.process_time() - start})
        del x
    hgb_targets = [t.name in plan["hgb_continuous_targets"] for t in targets]
    if any(hgb_targets):
        start = time.process_time()
        transform = fit_feature_transform(matrix, mask, group="full")
        x = _append_baseline_quantile_features(
            _basis(matrix, transform, mask, "linear"),
            _baseline_quantiles(shared, g[mask]), scales,
        )
        hgb_fits = []
        for t in range(len(targets)):
            if not hgb_targets[t]:
                hgb_fits.append(None)
                continue
            features = x
            fits = [backend.fit_hgb_challenger(features, y[:, t] / scales[t], weights, task="regression",
                       trigger=True, reason=plan["hgb_reason"], loss="quantile", quantile=q,
                       **plan["hgb_configuration"]).as_dict()
                    for q in levels]
            hgb_fits.append(fits)
        target_statuses = ['not_declared_for_target' if row is None else
                           'failed_empirical_fallback' if any(f['status'] in ('failed', 'not_run') for f in row)
                           else 'fitted' for row in hgb_fits]
        failed = 'failed_empirical_fallback' in target_statuses
        models["hgb_full"] = _seal({**shared, "kind": "hgb_quantiles", "name": "hgb_full", "transform": transform,
                                    "basis": "linear", "backend": hgb_fits,
                                    "target_statuses": target_statuses,
                                    "target_applicability": 'Each prespecified target receives its own quantile-tree fits even when its fused linear family contains other targets. Undeclared siblings retain baseline slots for array alignment and are not tree comparisons.',
                                    "status": "partial_failure_empirical_fallback" if failed else "fitted",
                                    "cpu_seconds": time.process_time() - start})
    return {"targets": [t.name for t in targets], "status": "compared", "fit": metadata, "models": models,
            "prior_storage_schema": FAMILY_SCHEMA, **retained_priors}


def model_target_status(model, target_index=0):
    """A separate tree head's failure or applicability is target-specific."""
    if model.get('kind') == 'hgb_quantiles' and 'target_statuses' in model:
        statuses = model['target_statuses']
        if (len(statuses) != len(model['target_names']) or not 0 <= target_index < len(statuses)
                or any(s not in ('fitted', 'failed_empirical_fallback', 'not_declared_for_target') for s in statuses)):
            raise IntegrityError('tree target applicability/status coordinates differ')
        return statuses[target_index]
    return model['status']


def calibration_for(matrix, target, model, *, plan, target_index=0):
    if model_target_status(model, target_index) == 'not_declared_for_target':
        raise ContractError('tree calibration is not declared for this target')
    binding = _target_binding(target, target_index)
    mask = target.phase(matrix, "calibrate")
    if target.kind == "interval_categorical":
        mask &= target.values.sum(axis=1) < target.values.shape[1]
    info = _fit_metadata(matrix, target, mask, phase="calibrate")
    if info["dates"] < plan["minimum_calibration_dates"]:
        return {"kind": "unavailable", "reason": "insufficient_calibration_dates", "fit": info,
                "source_model_id": model["id"], "target_binding": binding}
    prediction, _ = predict_model(model, matrix, mask)
    weights = date_weights(matrix.fields["date"][mask])
    if target.kind in ("categorical", "interval_categorical"):
        fit = backend.fit_temperature(np.log(prediction), target.values[mask], weights,
                classes=list(range(prediction.shape[1])), source_fit_id=model["id"], calibration_id=digest(info), metadata=info)
    else:
        fit = backend.fit_quantile_residual_calibration(prediction[:, target_index], target.values[mask],
                weights, quantiles=plan["quantiles"], source_fit_id=model["id"], calibration_id=digest(info), metadata=info)
    return {"kind": "temperature" if target.kind != "continuous" else "quantile_residual",
            "fit": info, "source_model_id": model["id"], "target_binding": binding,
            "backend": fit.as_dict()}


def apply_calibration(calibration, prediction, *, model, target, target_index=0):
    if calibration["source_model_id"] != model["id"]:
        raise IntegrityError("calibration is attached to a different fitted model")
    expected_binding = _target_binding(target, target_index)
    if calibration.get("target_binding") != expected_binding:
        raise IntegrityError("calibration is attached to a different target definition")
    p = prediction if target.kind != "continuous" else prediction[:, target_index:target_index + 1]
    if calibration["kind"] == "unavailable":
        return p
    if calibration["kind"] == "temperature":
        fit = backend.TemperatureCalibration.from_dict(calibration["backend"])
        if not fit.converged:
            return p
        return backend.predict_temperature(fit, np.log(p))
    fit = backend.QuantileResidualCalibration.from_dict(calibration["backend"])
    if fit.status != "converged":
        return p
    result = backend.predict_quantile_residual(fit, p[:, 0])[:, None, :]
    if target.metadata.get("nonnegative", False):
        result = np.maximum(result, 0)
    return result


def choose_tuning_model(matrix, target, family, *, plan, target_index=0):
    mask = target.phase(matrix, "tune")
    records = []
    for name, model in family["models"].items():
        status = model_target_status(model, target_index)
        if status == 'not_declared_for_target':
            records.append({'model': name, 'model_id': model['id'], 'status': status,
                            'date_mean_primary_loss': None, 'scored_rows': 0, 'dates': 0, 'raw_crossings': None})
            continue
        prediction, raw = predict_model(model, matrix, mask)
        p = prediction if target.kind != "continuous" else prediction[:, target_index]
        loss = _scalar_score(target, target.values[mask], p, plan["quantiles"])
        records.append({"model": name, "model_id": model["id"], "status": status,
                        "date_mean_primary_loss": date_mean(loss, matrix.fields["date"][mask]),
                        "scored_rows": int(np.isfinite(loss).sum()),
                        "dates": int(len(np.unique(matrix.fields["date"][mask][np.isfinite(loss)]))),
                        "raw_crossings": int(np.count_nonzero(np.any(np.diff(raw[:, target_index], axis=-1) < 0, axis=1)))
                            if target.kind == "continuous" else None})
    eligible = [r for r in records if r["status"] == "fitted" and r["date_mean_primary_loss"] is not None
                and r["dates"] >= plan["minimum_tuning_dates"]]
    winner = min(eligible, key=lambda r: (r["date_mean_primary_loss"], r["model"]))["model"] if eligible else "empirical"
    return {"phase": "tune", "winner": winner, "comparisons": records,
            "rule": "Lowest equal-date target-specific proper loss on2023 among successfully fitted fixed variants; one winner per target, not per clock/date", "used_heldout": False}


def intended_universes(matrix, phase, *, clocks=None, target=None):
    """Use declared rows before target eligibility to preserve failed dates."""
    phase_mask = _phase_rows(matrix, phase)
    if target is not None:
        phase_mask &= target.applicable(matrix)
    groups = group_ids(matrix)
    result = {}
    order = np.argsort(groups[phase_mask], kind="stable")
    gs, ds = groups[phase_mask][order], matrix.fields["date"][phase_mask][order]
    if len(gs):
        starts = np.r_[0, np.flatnonzero(np.diff(gs)) + 1]
        ends = np.r_[starts[1:], len(gs)]
        for a, b in zip(starts, ends, strict=True):
            group = int(gs[a])
            if clocks is None or decode_group(matrix, group)["clock"] in clocks:
                result[group] = np.unique(ds[a:b])
    return result


def _assess_metrics(target, values, prediction, *, quantiles):
    if target.kind != "continuous":
        primary, scored = _class_score(target, values, prediction)
        metrics = {"primary_loss": primary, "brier": scored["per_row"]["brier"]}
        if target.kind == "interval_categorical":
            allowed = values
        else:
            allowed = values[:, None] == np.arange(prediction.shape[1])
        single = allowed.sum(axis=1) == 1
        for k in range(prediction.shape[1]):
            # Reliability residual bounds apply even if the class is not
            # point identified; an all-class row retains [0,1].
            lower = (single & allowed[:, k]).astype(float)
            upper = allowed[:, k].astype(float)
            metrics[f"class_{k}_probability"] = prediction[:, k]
            metrics[f"class_{k}_observed_lower"] = lower
            metrics[f"class_{k}_observed_upper"] = upper
        return metrics, scored["summary"]
    scored = quantile_metrics(values[:, None], prediction[:, None, :], quantiles)
    metrics = {"primary_loss": scored["per_row_mean_pinball"],
               "central_interval_width": scored["central_interval"]["per_row_width"][:, 0]}
    for q, level in enumerate(quantiles):
        metrics[f"q{level}_pinball"] = scored["pinball"][:, 0, q]
        metrics[f"q{level}_coverage_lower"] = (values < prediction[:, q]).astype(float)
        metrics[f"q{level}_coverage_upper"] = (values <= prediction[:, q]).astype(float)
    return metrics, {"q_coverage": scored["q_coverage"], "central_interval": {k: v for k, v in scored["central_interval"].items() if k != "per_row_width"},
                     "crossings": scored["crossings"], "missingness": scored["missingness"]}


def evaluate_target(matrix, target, family, *, phase, plan, tuned, calibration=None, target_index=0):
    universes = intended_universes(matrix, phase, target=target)
    intended_mask = _phase_rows(matrix, phase) & target.applicable(matrix)
    mask = target.phase(matrix, phase)
    g, ds = group_ids(matrix)[mask], matrix.fields["date"][mask]
    if not mask.any():
        return {"target": target.name, "phase": phase, "status": "no_eligible_labels", "intended_rows": int(intended_mask.sum()),
                "eligible_rows": 0,
                "excluded_or_unmatured_rows": int(intended_mask.sum()),
                "target_metadata": target.metadata, "comparisons": {},
                "intended_date_universes": {str(group): dates.tolist() for group, dates in universes.items()}}
    base, _ = predict_model(family["models"]["empirical"], matrix, mask)
    if target.kind == "continuous":
        base = base[:, target_index]
    base_loss = _scalar_score(target, target.values[mask], base, plan["quantiles"])
    output = {}
    applicability = {name: model_target_status(model, target_index) for name, model in family['models'].items()}
    options = [(name, None) for name in family["models"] if applicability[name] != 'not_declared_for_target']
    if calibration is not None:
        if applicability[tuned['winner']] == 'not_declared_for_target':
            raise IntegrityError('selected tree is not declared for this target')
        options.append((tuned["winner"], calibration))
    for name, cal in options:
        model = family["models"][name]
        prediction, raw = predict_model(model, matrix, mask)
        if cal is not None:
            prediction = apply_calibration(cal, prediction, model=model, target=target, target_index=target_index)
            p = prediction[:, 0] if target.kind == "continuous" else prediction
        else:
            p = prediction[:, target_index] if target.kind == "continuous" else prediction
        metrics, summary = _assess_metrics(target, target.values[mask], p, quantiles=plan["quantiles"])
        metrics["gain_over_empirical"] = base_loss - metrics["primary_loss"]
        evaluation = dict(plan["evaluation"])
        if target.kind != "continuous":
            for key_to_remove in ("probability", "observed_binary", "lower", "upper"):
                evaluation.pop(key_to_remove, None)
            target_values = np.asarray(target.values[mask])
            if target.kind == "interval_categorical":
                allowed = np.asarray(target_values, dtype=bool)
                if allowed.ndim != 2 or allowed.shape != p.shape:
                    raise ContractError("interval target classes and probabilities are not aligned")
                single = allowed.sum(axis=1) == 1
                lower_matrix = (single[:, None] & allowed).astype(float)
                upper_matrix = allowed.astype(float)
                evaluation.update({"probability_matrix": p, "lower_matrix": lower_matrix,
                                   "upper_matrix": upper_matrix})
            else:
                if target_values.ndim != 1 or p.ndim != 2 or len(target_values) != len(p):
                    raise ContractError("categorical target classes and probabilities are not aligned")
                observed_matrix = np.equal(target_values[:, None], np.arange(p.shape[1])[None, :]).astype(float)
                evaluation["probability_matrix"] = p
                evaluation["observed_binary_matrix"] = observed_matrix
        grouped = grouped_date_evaluation(metrics, ds, g, universes, **evaluation)
        all_dates = np.unique(matrix.fields["date"][intended_mask])
        overall = grouped_date_evaluation({"primary_loss": metrics["primary_loss"]}, ds, np.zeros(len(ds), dtype=np.int64),
                        {0: all_dates}, paired_candidate=metrics["primary_loss"], paired_baseline=base_loss, **evaluation)
        key = name + ("__calibrated" if cal is not None else "")
        from trading_research.research.jumbo_evaluation_storage import pack_grouped_evaluation
        stored_groups = pack_grouped_evaluation(grouped)
        output[key] = {"model_id": model["id"], "status": applicability[name], "calibration": cal,
                       "overall": overall, "by_root_clock_horizon": stored_groups, "summary": summary}
        del grouped
    return json_safe({"version": VERSION, "target": target.name, "target_metadata": target.metadata, "phase": phase,
                      "status": "evaluated", "intended_rows": int(intended_mask.sum()), "eligible_rows": int(mask.sum()),
                      "excluded_or_unmatured_rows": int((intended_mask & ~mask).sum()),
                      "tuning": tuned, "comparisons": output, "model_target_applicability": applicability,
                      "intended_date_universes": {str(g): d.tolist() for g, d in universes.items()},
                      "interpretation": "Independently scored target; research comparison is not a trading-policy or profitability result"},
                     omit_date_vectors=True)
