"""Actual workload measurements inside the registered consolidation check.

These are resource experiments on the declared development observations. They
never select a predictor, replace a full cohort, or establish predictive quality.
"""
from datetime import date
import gc
import gzip
import json
import math
import resource
import time

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import canonical_json


def two_size_cost(small_cost, large_cost, small_units, large_units, planned_units):
    """Separate fixed work from a measured variable term, with a noise floor.

Two timings cannot certify asymptotic complexity. The half-amortized floor
prevents timer noise from projecting zero marginal cost. The caller also
reports the actual timings and applies its declared uncertainty multiplier.
"""
    from numbers import Integral, Real
    costs = (small_cost, large_cost)
    units = (small_units, large_units, planned_units)
    if any(isinstance(v, bool) or not isinstance(v, Real) for v in costs):
        raise IntegrityError('numeric finite nonnegative timing measurements required')
    if any(isinstance(v, bool) or not isinstance(v, Integral) or v <= 0 for v in units):
        raise IntegrityError('exact positive integer workload units required')
    try:
        finite = all(math.isfinite(float(v)) for v in (*costs, *units))
    except (OverflowError, TypeError, ValueError) as exc:
        raise IntegrityError('finite representable workload measurements required') from exc
    if not finite or any(v < 0 for v in costs):
        raise IntegrityError('finite nonnegative workload measurements required')
    if not 0 < small_units < large_units or planned_units <= 0:
        raise IntegrityError('two increasing measured workloads and positive projection required')
    variable = max(0.0, (large_cost-small_cost)/(large_units-small_units), large_cost/(2*large_units))
    fixed = max(0.0, large_cost-variable*large_units, small_cost-variable*small_units)
    return {'fixed_cpu_seconds': fixed, 'variable_cpu_seconds_per_unit': variable,
            'planned_units': planned_units, 'cpu_seconds': fixed+variable*planned_units}


def iteration_cost(small, large, planned_iterations):
    """Do not multiply one-time solver/binning setup by the full iteration cap."""
    if small['iterations'] < 1 or large['iterations'] < 1:
        raise IntegrityError('actual nonempty optimizer iterations required')
    if large['iterations'] > small['iterations']:
        return two_size_cost(small['cpu_seconds'], large['cpu_seconds'],
                             small['iterations'], large['iterations'], planned_iterations)
    # Early convergence or timing noise may leave no identified iteration
    # increment. Retain an explicit conservative all-cost-per-iteration bound.
    per_iteration = max(small['cpu_seconds'], large['cpu_seconds']) / min(small['iterations'], large['iterations'])
    return {'fixed_cpu_seconds': 0.0, 'variable_cpu_seconds_per_unit': per_iteration,
            'planned_units': planned_iterations, 'cpu_seconds': per_iteration * planned_iterations,
            'identification': 'No larger completed iteration count; conservative bound instead of an inferred zero marginal cost.'}


def _subset(matrix, days):
    import numpy as np
    from trading_research.research.jumbo_matrix import PreparedPaths
    mask = np.isin(matrix.fields['date'], days)
    manifest = {**matrix.manifest, 'preflight_dates': [int(v) for v in days],
                'preflight_only': True}
    return PreparedPaths(manifest, matrix.features[mask],
                         {k: v[mask] for k, v in matrix.fields.items()}, matrix.categories, matrix.shards)


def _feature_widths(matrix, mask, plan):
    from trading_research.research.jumbo_matrix import fit_feature_transform
    from trading_research.research.jumbo_models import _basis
    widths = {}
    for spec in plan['linear_variants']:
        transform = fit_feature_transform(matrix, mask, group=spec['group'])
        values = _basis(matrix, transform, mask, spec['basis'])
        widths[spec['name']] = values.shape[1]
        del values
    return widths


def _fit_units(matrix, plan, days, *, iteration_cap=10):
    """Actually optimize three declared target kinds; do not use min-fit exits."""
    import numpy as np
    import io
    from trading_research.research import jumbo_model_backend as backend
    from trading_research.research.jumbo_matrix import fit_feature_transform
    from trading_research.research.jumbo_models import _basis, date_weights, _scalar_score, date_mean
    from trading_research.research.jumbo_targets import target_catalog, group_ids
    from trading_research.research.jumbo_baselines import fit_grouped_distribution, predict_grouped_distribution
    sample = _subset(matrix, days)
    targets = target_catalog(sample)
    measurements = []
    for name in ('path', 'first_duration', 'future_high_from_known_W'):
        if name not in targets:
            raise IntegrityError('predeclared resource target absent from actual catalogue')
        target = targets[name]
        mask = target.phase(sample, 'fit')
        if target.kind == 'interval_categorical':
            mask &= target.values.sum(axis=1) < target.values.shape[1]
        if not mask.any() or len(np.unique(sample.fields['date'][mask])) < 10:
            raise IntegrityError('actual resource target lacks the declared measured date support')
        stage = time.process_time()
        transform = fit_feature_transform(sample, mask, group='full')
        x = _basis(sample, transform, mask, 'bounded_interactions_v1')
        weights = date_weights(sample.fields['date'][mask])
        values = target.values[mask]
        transform_cpu = time.process_time()-stage
        groups = group_ids(sample)[mask]
        metadata = {'purpose': 'registered resource preflight only', 'target': name,
                    'actual_rows': int(mask.sum()), 'actual_dates': len(np.unique(sample.fields['date'][mask]))}
        stage = time.process_time()
        if target.kind == 'continuous':
            scale = max(float(np.quantile(values, .9)-np.quantile(values, .1)), 1e-6)
            baseline = backend.fit_empirical_quantiles(values/scale, np.ones(len(values)),
                 quantiles=plan['quantiles'], shrinkage=plan['prior_date_mass'],
                 group_ids=groups.tolist(), global_weights=weights, metadata=metadata)
            offsets = backend.predict_empirical_quantiles(baseline, groups.tolist())[:, None, :]
            baseline_cpu = time.process_time()-stage
            # Full production heads receive all target/quantile comparator
            # features. Their exact larger width is counted in the inventory.
            x = np.column_stack((x, offsets[:, 0]))
            clock = time.process_time()
            fit = backend.fit_quantiles(x, values/scale, weights, quantiles=plan['quantiles'],
                      l2=.1, max_iterations=iteration_cap, tolerance=plan['solver_tolerance'],
                      smooth_epsilon=plan['smooth_pinball_epsilon'], offset_quantiles=offsets,
                      offset_identity='resource-preflight-actual-empirical', metadata=metadata)
            width = len(plan['quantiles'])
        else:
            width = len(target.metadata['classes'])
            group_count = len(sample.categories['root'])*len(sample.categories['clock'])*len(sample.categories['horizon'])
            baseline = fit_grouped_distribution(values, groups, sample.fields['date'][mask],
                classes=width, group_count=group_count, shrinkage=plan['prior_date_mass'],
                max_iterations=plan['prior_max_iterations'], tolerance=plan['prior_tolerance'])
            offsets = np.log(predict_grouped_distribution(baseline, groups, allow_declared_fallback=True))
            baseline_cpu = time.process_time()-stage
            clock = time.process_time()
            fit = backend.fit_softmax(x, values, weights, classes=list(range(width)), l2=.1,
                      max_iterations=iteration_cap, tolerance=plan['solver_tolerance'], metadata=metadata,
                      offset_logits=offsets, offset_identity='resource-preflight-actual-empirical')
        cpu = time.process_time()-clock
        stage = time.process_time()
        if target.kind == 'continuous':
            prediction = backend.predict_quantiles(fit, x, offset_quantiles=offsets,
                       offset_identity='resource-preflight-actual-empirical', allow_fallback=True)[:, 0]*scale
        else:
            prediction = backend.predict_softmax(fit, x, offset_logits=offsets,
                       offset_identity='resource-preflight-actual-empirical', allow_fallback=True)
        losses = _scalar_score(target, values, prediction, plan['quantiles'])
        date_mean(losses, sample.fields['date'][mask])
        prediction_cpu = time.process_time()-stage
        stage = time.process_time()
        if target.kind == 'continuous':
            calibration = backend.fit_quantile_residual_calibration(prediction, values, weights,
                    quantiles=plan['quantiles'], source_fit_id='resource-only-fit', calibration_id='resource-only-calibration')
        else:
            calibration = backend.fit_temperature(np.log(prediction), values, weights,
                    classes=list(range(width)), source_fit_id='resource-only-fit', calibration_id='resource-only-calibration')
        calibration_cpu = time.process_time()-stage
        stage = time.process_time()
        stream = io.BytesIO()
        np.savez_compressed(stream, prepared_row=np.flatnonzero(mask), date=sample.fields['date'][mask],
                            root=sample.fields['root'][mask], clock=sample.fields['clock'][mask],
                            horizon=sample.fields['horizon'][mask], origin_ns=sample.fields['origin_ns'][mask],
                            label=values, label_known_at_ns=target.label_known_at_ns[mask],
                            selected_calibrated=prediction, empirical=prediction, scored_mask=np.ones(len(values), dtype=bool))
        prediction_bytes = stream.tell()
        stream.close()
        serialization_cpu = time.process_time()-stage
        measurements.append({**metadata, 'kind': target.kind, 'features': x.shape[1],
                'heads_or_classes': width, 'iteration_cap': iteration_cap, 'iterations': fit.iterations,
                'status': fit.status, 'converged': fit.converged, 'cpu_seconds': cpu,
                'parameter_bytes': len(canonical_json(fit.as_dict())), 'baseline_cpu_seconds': baseline_cpu,
                'baseline_iterations': None if target.kind == 'continuous' else
                         {k: baseline[k]['iterations'] for k in ('global_diagnostics', 'group_diagnostics')},
                'transform_cpu_seconds': transform_cpu, 'prediction_and_tuning_score_cpu_seconds': prediction_cpu,
                'calibration_cpu_seconds': calibration_cpu, 'calibration_status': calibration.status,
                'prediction_serialization_cpu_seconds': serialization_cpu, 'prediction_bytes': prediction_bytes})
        print(json.dumps({'preflight': 'completed_optimizer_unit', 'measurement': measurements[-1]}), flush=True)
        if fit.iterations < 1:
            raise IntegrityError('resource preflight did not exercise an actual optimizer')
        if name in ('path', 'future_high_from_known_W') and len(days) == 20:
            configuration = {**plan['hgb_configuration'], 'max_iter': iteration_cap}
            # Match the production tree basis and its actual comparator
            # features; the nonlinear basis above is a different learner.
            tree_x = np.column_stack((_basis(sample, transform, mask, 'linear'),
                         offsets[:, 0] if target.kind == 'continuous' else offsets))
            tree_options = {'task': 'regression', 'loss': 'quantile', 'quantile': .5} if target.kind == 'continuous' else {
                'task': 'classification', 'classes': list(range(width))}
            clock = time.process_time()
            boosted = backend.fit_hgb_challenger(tree_x, values/scale if target.kind == 'continuous' else values, weights,
                  trigger=True, reason='Actual bounded tree resource preflight; no quality claim',
                  **tree_options, **configuration)
            measurements.append({**metadata, 'kind': 'hgb_quantile' if target.kind == 'continuous' else 'hgb_classification',
                  'features': tree_x.shape[1], 'feature_basis': 'production linear full features plus declared comparator features',
                  'heads_or_classes': 1 if target.kind == 'continuous' else width,
                  'iteration_cap': iteration_cap, 'iterations': boosted.iterations,
                  'status': boosted.status, 'failure': boosted.failure, 'cpu_seconds': time.process_time()-clock,
                  'parameter_bytes': len(canonical_json(boosted.as_dict()))})
            print(json.dumps({'preflight': 'completed_tree_unit', 'measurement': measurements[-1]}), flush=True)
            if boosted.status in ('failed', 'not_run') or boosted.iterations != iteration_cap:
                raise IntegrityError('actual tree workload did not complete its declared iterations')
            del tree_x, boosted
        del x, fit
    return measurements


def _evaluation_unit(matrix, plan, days, *, store, verify_storage=False):
    """Measure complete group/bootstrap/serialization work at two date sizes."""
    import numpy as np
    from trading_research.research.jumbo_targets import target_catalog, group_ids
    from trading_research.research.jumbo_models import intended_universes, _assess_metrics, json_safe
    from trading_research.research.jumbo_model_evaluation import grouped_date_evaluation
    from trading_research.research.jumbo_evaluation_storage import (
        pack_grouped_evaluation, verify_packed_evaluation, normalized_json_bytes)
    from dataclasses import asdict
    sample = _subset(matrix, days)
    target = target_catalog(sample)['path']
    mask = target.phase(sample, 'fit')
    y = target.values[mask]
    k = len(target.metadata['classes'])
    # These explicitly artificial simplex predictions exercise reliability
    # bins. They are never evidence of a fitted market predictor or its score.
    row = np.arange(len(y))
    dominant = row % k
    probability = .1+.8*((row//k) % 10)/9
    p = np.repeat(((1-probability)/(k-1))[:, None], k, axis=1)
    p[row, dominant] = probability
    metrics, _ = _assess_metrics(target, y, p, quantiles=plan['quantiles'])
    ds, groups = sample.fields['date'][mask], group_ids(sample)[mask]
    universes = intended_universes(sample, 'fit')
    observed = y[:, None] == np.arange(k)
    clock = time.process_time()
    grouped = grouped_date_evaluation(metrics, ds, groups, universes,
                    probability_matrix=p, observed_binary_matrix=observed, **plan['evaluation'])
    grouped_cpu = time.process_time()-clock
    clock = time.process_time()
    overall = grouped_date_evaluation({'primary_loss': metrics['primary_loss']}, ds, np.zeros(len(ds), dtype=np.int64),
                    {0: np.asarray(days, dtype=np.int64)}, paired_candidate=metrics['primary_loss'],
                    paired_baseline=metrics['primary_loss'], probability_matrix=p,
                    observed_binary_matrix=observed, **plan['evaluation'])
    overall_cpu = time.process_time()-clock
    print(json.dumps({'preflight': 'completed_evaluation_scoring', 'dates': len(days),
                      'groups': len(universes), 'grouped_cpu_seconds': grouped_cpu,
                      'overall_cpu_seconds': overall_cpu}), flush=True)
    clock = time.process_time()
    packed = pack_grouped_evaluation(grouped)
    raw_grouped = normalized_json_bytes(packed)
    payload_grouped = gzip.compress(raw_grouped, compresslevel=3, mtime=0)
    grouped_ref = asdict(store.put_bytes(payload_grouped, kind='jumbo_resource_evaluation_grouped_gzip_v1'))
    grouped_serialization_cpu = time.process_time()-clock
    clock = time.process_time()
    raw_overall = normalized_json_bytes(json_safe(overall, omit_date_vectors=True))
    payload_overall = gzip.compress(raw_overall, compresslevel=3, mtime=0)
    overall_ref = asdict(store.put_bytes(payload_overall, kind='jumbo_resource_evaluation_overall_gzip_v1'))
    overall_serialization_cpu = time.process_time()-clock
    clock = time.process_time()
    if verify_storage:
        from references.jumbo_evaluation_check11.evaluation import grouped_date_evaluation as reference_evaluation
        reference = reference_evaluation(metrics, ds, groups, universes,
                        probability_matrix=p, observed_binary_matrix=observed, **plan['evaluation'])
        verification = verify_packed_evaluation(reference, packed)
        del reference
        verification['reference'] = 'Exact registered check11 scorer; same20-date rows, metrics, predictions, group universes and1000 bootstrap weights.'
    else:
        verification = None
    storage_verification_cpu = time.process_time()-clock
    return {'dates': len(days), 'rows': len(ds), 'groups': len(universes), 'classes': k,
            'metrics': len(metrics), 'cpu_seconds': grouped_cpu+overall_cpu,
            'grouped_cpu_seconds': grouped_cpu, 'overall_cpu_seconds': overall_cpu,
            'grouped_serialization_cpu_seconds': grouped_serialization_cpu,
            'overall_serialization_cpu_seconds': overall_serialization_cpu,
            'serialization_cpu_seconds': grouped_serialization_cpu+overall_serialization_cpu,
            'grouped_compressed_output_bytes': len(payload_grouped), 'overall_compressed_output_bytes': len(payload_overall),
            'compressed_output_bytes': len(payload_grouped)+len(payload_overall),
            'uncompressed_output_bytes': len(raw_grouped)+len(raw_overall),
            'grouped_artifact': grouped_ref, 'overall_artifact': overall_ref,
            'storage_schema': packed['schema'], 'storage_verification': verification,
            'storage_verification_cpu_seconds': storage_verification_cpu,
            'prediction_scope': 'Artificial varying simplex resource probe on actual admitted labels; no quality claim'}


def model_workload_preflight(matrix, store, shards, analysis, plan, *, train_dates, select_dates, heldout_dates,
                             packet, protocol, root):
    import numpy as np
    from trading_research.research.jumbo_pipeline import _domains
    from trading_research.research.jumbo_fitting import _families
    from trading_research.research.jumbo_targets import group_ids
    annual_days = np.unique(matrix.fields['date'])
    if len(annual_days) != 253:
        raise IntegrityError('whole annual actual model preflight required')
    chosen = annual_days[-20:]
    start = time.process_time()
    inventory = []
    for domain, view, targets in _domains(matrix, store, shards, analysis, plan):
        fitting_mask = view.phase('2020-01-01', '2022-12-31')
        widths = _feature_widths(view, fitting_mask, plan)
        for names, family in _families(view, targets):
            for target in family:
                applicable = target.applicable(view)
                classes = len(target.metadata.get('classes', ()))
                continuous_heads = len(family) if target.kind == 'continuous' else 0
                effective_widths = {k: v+continuous_heads*len(plan['quantiles']) for k, v in widths.items()}
                inventory.append({'domain': domain, 'target': target.name, 'kind': target.kind,
                    'intended_annual_rows': int(applicable.sum()), 'eligible_annual_rows': int(target.phase(view, 'fit').sum()),
                    'classes': classes, 'groups_per_root': len(np.unique(group_ids(view)[applicable])), 'feature_widths': effective_widths,
                    'categorical_group_slots_per_root': math.prod(len(view.categories[key]) for key in ('root', 'clock', 'horizon')),
                    'hgb_feature_width': widths['full_linear'] + (continuous_heads*len(plan['quantiles']) if target.kind == 'continuous' else classes),
                    'fused_continuous_targets': continuous_heads,
                    'hgb_heads': len(plan['quantiles']) if target.name in plan['hgb_continuous_targets'] else
                                classes if target.name in plan['hgb_categorical_targets'] else 0})
        del targets
        gc.collect()
    inventory_cpu = time.process_time()-start
    print(json.dumps({'preflight': 'completed_target_inventory', 'targets': len(inventory),
                      'domains': sorted({v['domain'] for v in inventory}),
                      'intended_annual_target_rows': sum(v['intended_annual_rows'] for v in inventory),
                      'cpu_seconds': inventory_cpu}), flush=True)
    from trading_research.research.jumbo_preflight_v8 import complete_model_workload_preflight
    return complete_model_workload_preflight(matrix, store, inventory, plan,
        inventory_cpu=inventory_cpu, train_dates=train_dates, select_dates=select_dates,
        heldout_dates=heldout_dates, packet=packet, protocol=protocol, root=root, start=start)
