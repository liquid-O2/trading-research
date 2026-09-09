"""Target-specific resource accounting and complete model storage probes.

All calls execute inside the registered resource worker. Probe predictions are
explicitly artificial, and smaller fitting limits measure cost only. They do
not replace any full-cohort learner, alternative, calibration or bootstrap.
"""
from copy import deepcopy
from dataclasses import asdict
import gc
import gzip
import json
import math
import resource
import time

import numpy as np

from trading_research.errors import IntegrityError
from trading_research.research.jumbo_preflight import _subset, two_size_cost, iteration_cost


def _tree_size_units(matrix, plan, days):
    from trading_research.research import jumbo_model_backend as backend
    from trading_research.research.jumbo_baselines import fit_grouped_distribution, predict_grouped_distribution
    from trading_research.research.jumbo_matrix import fit_feature_transform
    from trading_research.research.jumbo_models import _basis, date_weights
    from trading_research.research.jumbo_targets import target_catalog, group_ids
    from trading_research.research.jumbo_evaluation_storage import normalized_json_bytes
    sample = _subset(matrix, days)
    catalog = target_catalog(sample)
    result = []
    for name in ('path', 'future_high_from_known_W'):
        target = catalog[name]
        mask = target.phase(sample, 'fit')
        values = target.values[mask]
        weights = date_weights(sample.fields['date'][mask])
        groups = group_ids(sample)[mask]
        transform = fit_feature_transform(sample, mask, group='full')
        if target.kind == 'continuous':
            scale = max(float(np.quantile(values, .9)-np.quantile(values, .1)), 1e-6)
            prior = backend.fit_empirical_quantiles(values/scale, np.ones(len(values)),
                quantiles=plan['quantiles'], shrinkage=plan['prior_date_mass'],
                group_ids=groups.tolist(), global_weights=weights)
            offsets = backend.predict_empirical_quantiles(prior, groups.tolist())
            options = {'task': 'regression', 'loss': 'quantile', 'quantile': .5}
            labels, heads, kind = values/scale, 1, 'hgb_quantile'
        else:
            heads = len(target.metadata['classes'])
            prior = fit_grouped_distribution(values, groups, sample.fields['date'][mask],
                classes=heads, group_count=math.prod(len(sample.categories[k]) for k in ('root','clock','horizon')),
                shrinkage=plan['prior_date_mass'], max_iterations=plan['prior_max_iterations'], tolerance=plan['prior_tolerance'])
            offsets = np.log(predict_grouped_distribution(prior, groups, allow_declared_fallback=True))
            options = {'task': 'classification', 'classes': list(range(heads))}
            labels, kind = values, 'hgb_classification'
        x = np.column_stack((_basis(sample, transform, mask, 'linear'), offsets))
        for cap in (10, 20):
            clock = time.process_time()
            fit = backend.fit_hgb_challenger(x, labels, weights, trigger=True,
                reason='Additional actual row-size resource unit; no predictive-quality claim',
                **options, **{**plan['hgb_configuration'], 'max_iter': cap})
            cpu = time.process_time()-clock
            if fit.status in ('failed', 'not_run') or fit.iterations != cap:
                raise IntegrityError('larger actual tree resource unit did not complete')
            result.append({'purpose':'registered resource preflight only', 'target':name, 'kind':kind,
                'actual_rows':len(values), 'actual_dates':len(np.unique(sample.fields['date'][mask])),
                'features':x.shape[1], 'heads_or_classes':heads, 'iteration_cap':cap,
                'iterations':fit.iterations, 'status':fit.status, 'failure':fit.failure,
                'cpu_seconds':cpu, 'parameter_bytes':len(normalized_json_bytes(fit.as_dict())),
                'maximum_observed_tree_nodes':max(tree.nodes.size for row in fit.estimator._predictors for tree in row)})
            print(json.dumps({'preflight':'completed_larger_tree_unit', 'measurement':result[-1]}),flush=True)
        del x, prior, fit
    return result


def _continuous_evaluation_unit(matrix, plan, days, store):
    from trading_research.research.jumbo_targets import target_catalog, group_ids
    from trading_research.research.jumbo_models import intended_universes, _assess_metrics, json_safe
    from trading_research.research.jumbo_model_evaluation import grouped_date_evaluation
    from trading_research.research.jumbo_evaluation_storage import pack_grouped_evaluation, normalized_json_bytes
    sample = _subset(matrix, days)
    target = target_catalog(sample)['future_high_from_known_W']
    mask = target.phase(sample, 'fit')
    values = target.values[mask]
    # Varying, ordered resource predictions; they are not selected forecasts.
    row = np.arange(len(values))
    prediction = ((row % 997)/37-10)[:,None] + np.asarray([-3.,-1.,0.,1.,3.])[None,:]
    if prediction.shape[1] != len(plan['quantiles']):
        raise IntegrityError('resource quantile grid differs from the fixed five-head plan')
    metrics,_ = _assess_metrics(target,values,prediction,quantiles=plan['quantiles'])
    metrics['gain_over_empirical'] = -metrics['primary_loss']
    dates,groups = sample.fields['date'][mask],group_ids(sample)[mask]
    universes = intended_universes(sample,'fit',target=target)
    clock=time.process_time()
    grouped=grouped_date_evaluation(metrics,dates,groups,universes,**plan['evaluation'])
    grouped_cpu=time.process_time()-clock
    clock=time.process_time()
    overall=grouped_date_evaluation({'primary_loss':metrics['primary_loss']},dates,np.zeros(len(dates),dtype=np.int64),
        {0:np.asarray(days,dtype=np.int64)},paired_candidate=metrics['primary_loss'],
        paired_baseline=np.zeros(len(dates)),**plan['evaluation'])
    overall_cpu=time.process_time()-clock
    clock=time.process_time()
    raw=normalized_json_bytes(pack_grouped_evaluation(grouped))
    payload=gzip.compress(raw,compresslevel=3,mtime=0)
    grouped_ref=asdict(store.put_bytes(payload,kind='jumbo_resource_continuous_grouped_gzip_v1'))
    grouped_serialization=time.process_time()-clock
    uncompressed=len(raw)
    clock=time.process_time()
    raw=normalized_json_bytes(json_safe(overall,omit_date_vectors=True))
    payload=gzip.compress(raw,compresslevel=3,mtime=0)
    overall_ref=asdict(store.put_bytes(payload,kind='jumbo_resource_continuous_overall_gzip_v1'))
    overall_serialization=time.process_time()-clock
    result={'kind':'continuous','dates':len(days),'rows':len(dates),'groups':len(universes),'classes':0,
        'metrics':len(metrics),'cpu_seconds':grouped_cpu+overall_cpu,'grouped_cpu_seconds':grouped_cpu,
        'overall_cpu_seconds':overall_cpu,'grouped_serialization_cpu_seconds':grouped_serialization,
        'overall_serialization_cpu_seconds':overall_serialization,
        'serialization_cpu_seconds':grouped_serialization+overall_serialization,
        'grouped_compressed_output_bytes':grouped_ref['size_bytes'],'overall_compressed_output_bytes':overall_ref['size_bytes'],
        'compressed_output_bytes':grouped_ref['size_bytes']+overall_ref['size_bytes'],
        'uncompressed_output_bytes':uncompressed+len(raw),'grouped_artifact':grouped_ref,'overall_artifact':overall_ref,
        'prediction_scope':'Artificial varying monotone quantiles on actual admitted labels; resource evidence only.'}
    print(json.dumps({'preflight':'completed_continuous_evaluation_unit','measurement':result}),flush=True)
    return result


def _model_storage_unit(matrix, plan, days, store, *, kind):
    from trading_research.research.jumbo_targets import target_catalog,group_ids
    from trading_research.research.jumbo_models import (fit_categorical_family,fit_continuous_family,
        predict_model,_scalar_score,date_mean)
    from trading_research.research.jumbo_fitting import _families,put_json_compressed,read_json_compressed
    from trading_research.research.jumbo_prior_storage import validate_family_priors,predict_quantile_serving
    from trading_research.research.jumbo_model_backend import EmpiricalQuantileFit,predict_empirical_quantiles
    from trading_research.research.jumbo_evaluation_storage import normalized_json_bytes
    sample=_subset(matrix,days)
    catalog=target_catalog(sample)
    if kind=='continuous':
        candidates=[values for names,values in _families(sample,catalog) if 'future_high_from_known_W' in names]
        if len(candidates)!=1:raise IntegrityError('one complete measured continuous fitting family required')
        targets=candidates[0]
    else:
        targets=(catalog['path' if kind=='categorical' else 'first_duration'],)
    resource_plan=deepcopy(plan)
    resource_plan.update(minimum_fit_dates=10,solver_max_iterations=10)
    resource_plan['hgb_configuration']['max_iter']=10
    prior_refs=[]
    prior_serialization_cpu=0.
    def retain(evidence):
        nonlocal prior_serialization_cpu
        clock=time.process_time()
        ref=put_json_compressed(store,evidence,kind='jumbo_resource_complete_empirical_distributions_gzip_v1',
            remaining_bytes=64*1024*1024,normalized=True)
        prior_serialization_cpu+=time.process_time()-clock
        prior_refs.append(ref)
        return ref
    clock=time.process_time()
    family=(fit_continuous_family(sample,targets,plan=resource_plan,prior_writer=retain) if kind=='continuous'
            else fit_categorical_family(sample,targets[0],plan=resource_plan))
    family_cpu=time.process_time()-clock
    if not family.get('models'):raise IntegrityError('complete storage resource unit did not fit its actual population')
    clock=time.process_time()
    validation=validate_family_priors(family,store=store)
    frozen=put_json_compressed(store,family,kind='jumbo_resource_complete_frozen_family_gzip_v1',
        remaining_bytes=64*1024*1024,normalized=True)
    restored=read_json_compressed(store,frozen)
    validate_family_priors(restored,store=store)
    if normalized_json_bytes(restored)!=normalized_json_bytes(family):
        raise IntegrityError('complete model storage changed its published values')
    publication_cpu=time.process_time()-clock
    # Compare the full original empirical calculator with the compact serving
    # view at exact binary64 precision on actual group identities and a new one.
    serving_comparisons=0
    if kind=='continuous':
        full=read_json_compressed(store,prior_refs[0])
        groups=group_ids(sample).tolist()+[-1]
        for wire,serving in zip(full,family['models']['empirical']['baseline'],strict=True):
            expected=predict_empirical_quantiles(EmpiricalQuantileFit.from_dict(wire),groups)
            actual=predict_quantile_serving(serving,groups)
            if not np.array_equal(expected.view(np.uint64),actual.view(np.uint64)):
                raise IntegrityError('actual compact prior changed an emitted quantile')
            serving_comparisons+=expected.size
        del full,expected,actual
    clock=time.process_time()
    prediction_by_model={name:0. for name in family['models']}
    for index,target in enumerate(targets):
        mask=target.phase(sample,'fit')
        for name,model in family['models'].items():
            model_clock=time.process_time()
            prediction,_=predict_model(model,sample,mask)
            if kind=='continuous':prediction=prediction[:,index]
            date_mean(_scalar_score(target,target.values[mask],prediction,plan['quantiles']),sample.fields['date'][mask])
            prediction_by_model[name]+=time.process_time()-model_clock
    prediction_cpu=time.process_time()-clock
    first=targets[0]
    rows=int(first.phase(sample,'fit').sum())
    first_model=family['models']['empirical']
    metadata_bytes=sum(len(normalized_json_bytes({k:v for k,v in model.items() if k not in ('baseline','backend')}))
                       for model in family['models'].values())
    serving_bytes=len(normalized_json_bytes(first_model['baseline']))
    linear_backend_upper=0
    for model in family['models'].values():
        if model['kind'] in ('softmax','quantile'):
            wire=model['backend']
            cells=np.asarray(wire['coefficients']).size+np.asarray(wire['intercept']).size
            # Numerical failure can serialize zeros. Budget full-length finite
            # coefficients instead of relying on that unusually short payload.
            linear_backend_upper+=len(normalized_json_bytes(wire))+28*cells
    tree_records=[]
    tree=family['models'].get('hgb_full')
    if tree is not None:
        tree_records=([tree['backend']] if kind=='categorical' else
                      [wire for row in tree['backend'] if row is not None for wire in row])
        if any(wire['status'] in ('failed','not_run') for wire in tree_records):
            raise IntegrityError('complete resource family has an unavailable declared tree head')
    tree_bytes=sum(len(normalized_json_bytes(wire)) for wire in tree_records)
    optimizer_calls=len(plan['linear_variants'])+len(tree_records)
    algorithm_cpu=sum(model['cpu_seconds'] for model in family['models'].values())
    result={'kind':kind,'actual_rows':rows,'actual_dates':len(np.unique(sample.fields['date'][first.phase(sample,'fit')])),
        'targets':[target.name for target in targets],'target_count':len(targets),'models':len(family['models']),
        'classes':len(first.metadata.get('classes',())),'quantiles':len(plan['quantiles']) if kind=='continuous' else 0,
        'groups':len(np.unique(group_ids(sample)[first.applicable(sample)])),
        'categorical_group_slots':math.prod(len(sample.categories[k]) for k in ('root','clock','horizon')),
        'family_cpu_seconds':family_cpu,'prior_serialization_cpu_seconds':prior_serialization_cpu,
        'publication_and_restore_cpu_seconds':publication_cpu,
        'model_identity_and_container_cpu_seconds':max(0.,family_cpu-algorithm_cpu),
        'all_models_all_targets_prediction_and_score_cpu_seconds':prediction_cpu,
        'prediction_by_model_cpu_seconds':prediction_by_model,
        'metadata_bytes':metadata_bytes,'serving_prior_bytes':serving_bytes,
        'linear_backend_full_length_coefficients_bytes_upper':linear_backend_upper,
        'tree_wire_bytes':tree_bytes,'tree_records':len(tree_records),'tree_iteration_cap':10,
        'empirical_evidence_compressed_bytes':sum(ref['size_bytes'] for ref in prior_refs),
        'empirical_evidence_uncompressed_bytes':sum(ref['uncompressed_size_bytes'] for ref in prior_refs),
        'frozen_family':frozen,'empirical_evidence':prior_refs,
        'derived_output_bytes':frozen['size_bytes']+sum(ref['size_bytes'] for ref in prior_refs),
        'actual_optimizer_calls':optimizer_calls,'actual_empirical_distribution_calls':len(targets),
        'model_statuses':{name:model['status'] for name,model in family['models'].items()},
        'full_prior_validation':validation,'exact_prior_serving_scalar_comparisons':serving_comparisons,
        'complete_frozen_family_roundtrip':True,'scope':'Production storage/prediction consumers on actual 20-date resource cohort; no tuning, selection or quality claim.'}
    print(json.dumps({'preflight':'completed_full_model_storage_unit','measurement':result}),flush=True)
    del family,restored
    gc.collect()
    return result


def _tree_projection(fits,kind,planned_rows,iterations):
    units=sorted((value for value in fits if value['kind']==kind),key=lambda value:(value['actual_rows'],value['iteration_cap']))
    if (len(units)!=4 or units[0]['actual_rows']!=units[1]['actual_rows']
            or units[2]['actual_rows']!=units[3]['actual_rows'] or units[1]['actual_rows']>=units[2]['actual_rows']):
        raise IntegrityError('two actual tree row sizes and iteration caps are required')
    small=iteration_cost(units[0],units[1],iterations)
    large=iteration_cost(units[2],units[3],iterations)
    return two_size_cost(small['cpu_seconds'],large['cpu_seconds'],units[1]['actual_rows'],units[3]['actual_rows'],planned_rows),units[-1],[small,large]


def _evaluation_projection(units,*,groups,dates,capacity,metric_factor):
    a,b=units
    small=(a['grouped_cpu_seconds']+a['grouped_serialization_cpu_seconds'])/a['groups']
    large=(b['grouped_cpu_seconds']+b['grouped_serialization_cpu_seconds'])/b['groups']
    grouped=two_size_cost(small,large,a['dates'],b['dates'],dates)['cpu_seconds']*groups
    overall=two_size_cost(a['overall_cpu_seconds']+a['overall_serialization_cpu_seconds'],
        b['overall_cpu_seconds']+b['overall_serialization_cpu_seconds'],a['dates'],b['dates'],dates)['cpu_seconds']
    # Byte growth has a fixed group/report component and a measured date term,
    # too. Longer confirmation universes do not inherit a one-year byte count.
    grouped_bytes=two_size_cost(a['grouped_compressed_output_bytes']/a['groups'],
        b['grouped_compressed_output_bytes']/b['groups'],a['dates'],b['dates'],dates)['cpu_seconds']*groups
    overall_bytes=two_size_cost(a['overall_compressed_output_bytes'],b['overall_compressed_output_bytes'],
        a['dates'],b['dates'],dates)['cpu_seconds']
    return (grouped+overall)*capacity*metric_factor,(grouped_bytes+overall_bytes)*capacity*metric_factor


def complete_model_workload_preflight(matrix,store,inventory,plan,*,inventory_cpu,train_dates,select_dates,heldout_dates,
                                      packet,protocol,root,start):
    from trading_research.research.jumbo_workload_reuse import retained_model_units, retained_expanded_model_units
    fits,categorical_units,reuse=retained_model_units(packet,protocol,root,store,inventory)
    days=np.unique(matrix.fields['date'])
    chosen=days[-20:]
    expanded=retained_expanded_model_units(packet,protocol,root,store,inventory)
    larger_trees=(expanded['larger_trees'] if expanded is not None
                  else _tree_size_units(matrix,plan,days[-100:]))
    all_fits=fits+larger_trees
    continuous_units=(expanded['continuous_units'] if expanded is not None else
                      [_continuous_evaluation_unit(matrix,plan,cohort,store) for cohort in (chosen,days)])
    storage_units=(expanded['storage_units'] if expanded is not None else
                   {kind:_model_storage_unit(matrix,plan,chosen,store,kind=kind)
                    for kind in ('categorical','interval_categorical','continuous')})
    estimates=[]
    for target in inventory:
        kind=target['kind']
        measured=sorted((value for value in fits if value['kind']==kind),key=lambda value:(value['actual_rows'],value['iteration_cap']))
        small,large=measured[1],measured[3]
        rows=math.ceil(target['intended_annual_rows']*2*train_dates/253)
        selected_rows=math.ceil(target['intended_annual_rows']*2*select_dates/253)
        heldout_rows=math.ceil(target['intended_annual_rows']*2*heldout_dates/253)
        heads=len(plan['quantiles']) if kind=='continuous' else target['classes']
        width_ratio=sum(target['feature_widths'].values())/large['features']
        small_iterations=iteration_cost(measured[0],measured[1],plan['solver_max_iterations'])
        large_iterations=iteration_cost(measured[2],measured[3],plan['solver_max_iterations'])
        row_cost=two_size_cost(small_iterations['cpu_seconds'],large_iterations['cpu_seconds'],small['actual_rows'],large['actual_rows'],rows)
        solver=row_cost['cpu_seconds']*heads/large['heads_or_classes']*width_ratio
        baseline=two_size_cost(small['baseline_cpu_seconds'],large['baseline_cpu_seconds'],small['actual_rows'],large['actual_rows'],rows)['cpu_seconds']
        prior_iteration_rule='Full allowed-set iteration ceiling retained.'
        if kind!='continuous':
            used=max(1,max(large['baseline_iterations'].values()))
            maximum=plan['prior_max_iterations']
            if kind=='categorical':
                if used>3:raise IntegrityError('point-class prior differs from its fixed-responsibility workload')
                maximum=min(maximum,3)
                prior_iteration_rule='Point observations have fixed one-hot responsibilities; allow three full passes, retaining the unchanged production200-iteration safety ceiling.'
            baseline*=maximum/used*heads/large['heads_or_classes']
        tree_kind='hgb_quantile' if kind=='continuous' else 'hgb_classification'
        tree_cost,tree_measure,tree_iterations=_tree_projection(all_fits,tree_kind,rows,plan['hgb_configuration']['max_iter'])
        tree=tree_cost['cpu_seconds']*target['hgb_heads']/tree_measure['heads_or_classes']*max(1,target['hgb_feature_width']/tree_measure['features'])
        capacity=len(plan['linear_variants'])+2+bool(target['hgb_heads'])
        units=continuous_units if kind=='continuous' else categorical_units
        metric_factor=1. if kind=='continuous' else max(1,(3*heads+3+30*heads)/(units[-1]['metrics']+30*units[-1]['classes']))
        selected_report,selected_bytes=_evaluation_projection(units,groups=target['groups_per_root']*2,dates=select_dates,capacity=capacity,metric_factor=metric_factor)
        heldout_report,heldout_bytes=_evaluation_projection(units,groups=target['groups_per_root']*2,dates=heldout_dates,capacity=capacity,metric_factor=metric_factor)
        unit=storage_units[kind]
        row_ratio=rows/unit['actual_rows']
        group_ratio=target['groups_per_root']*2/max(1,unit['groups'])
        slot_ratio=target['categorical_group_slots_per_root']*2/unit['categorical_group_slots']
        head_ratio=heads/(unit['quantiles'] or unit['classes'])/unit['target_count']
        # Complete baseline atoms are published once, before model design
        # allocation. Their size follows rows; serving priors follow groups.
        empirical_bytes=unit['empirical_evidence_compressed_bytes']*row_ratio/unit['target_count']
        model_bytes=(unit['metadata_bytes']*max(1,heads/(unit['quantiles'] or unit['classes']))/unit['target_count']
            +unit['serving_prior_bytes']*(group_ratio if kind=='continuous' else slot_ratio)*unit['models']*head_ratio
            +unit['linear_backend_full_length_coefficients_bytes_upper']*head_ratio*max(1,max(target['feature_widths'].values())/large['features']))
        if target['hgb_heads']:
            model_bytes+=unit['tree_wire_bytes']/unit['tree_records']*target['hgb_heads']/(unit['classes'] if kind=='categorical' else 1)*plan['hgb_configuration']['max_iter']/unit['tree_iteration_cap']*max(1,target['hgb_feature_width']/tree_measure['features'])*2
        # Measured production model identity, prior persistence, restore and
        # prediction work were absent from the old backend-only fit units.
        publication=(unit['prior_serialization_cpu_seconds']+unit['publication_and_restore_cpu_seconds']
                     +unit['model_identity_and_container_cpu_seconds'])*max(1,row_ratio)/unit['target_count']
        prediction_rate=sum(cpu*(plan['hgb_configuration']['max_iter']/unit['tree_iteration_cap'] if name=='hgb_full' else 1)
            for name,cpu in unit['prediction_by_model_cpu_seconds'].items())/unit['actual_rows']/unit['target_count']
        tuning_rows=math.ceil(target['intended_annual_rows']*2)
        prediction=prediction_rate*(tuning_rows+3*selected_rows)*max(1,capacity/unit['models'])
        heldout_prediction=prediction_rate*heldout_rows*(capacity+2)/unit['models']
        def ancillary(key,count):
            return two_size_cost(small[key],large[key],small['actual_rows'],large['actual_rows'],count)['cpu_seconds']
        # A failed small linear fit emits a cheap baseline. Retain the actual
        # backend's full matrix-prediction measurement as an additional bound
        # for converged full-cohort coefficients and all fused output heads.
        prediction=max(prediction,ancillary('prediction_and_tuning_score_cpu_seconds',tuning_rows+3*selected_rows)
            *capacity*max(1,width_ratio/len(plan['linear_variants']))*max(1,target['fused_continuous_targets']))
        heldout_prediction=max(heldout_prediction,ancillary('prediction_and_tuning_score_cpu_seconds',heldout_rows)
            *(capacity+2)*max(1,width_ratio/len(plan['linear_variants']))*max(1,target['fused_continuous_targets']))
        transforms=ancillary('transform_cpu_seconds',rows)*width_ratio
        calibration=ancillary('calibration_cpu_seconds',selected_rows)*max(1,heads/large['heads_or_classes'])
        selected_prediction_bytes=large['prediction_bytes']*selected_rows/large['actual_rows']*1.5
        heldout_prediction_bytes=large['prediction_bytes']*heldout_rows/large['actual_rows']*1.5
        estimates.append({**target,'planned_fit_rows_upper':rows,'linear_fit_cpu_seconds':solver,
            'solver_iteration_projection_at_two_row_sizes':[small_iterations,large_iterations],
            'tree_iteration_projection_at_two_row_sizes':tree_iterations,'tree_row_projection':tree_cost,
            'boosted_fit_cpu_seconds':tree,'empirical_baseline_cpu_seconds':baseline,'prior_iteration_cost_rule':prior_iteration_rule,
            'selection_report_cpu_seconds':selected_report,'heldout_report_cpu_seconds':heldout_report,
            'evaluation_output_bytes':selected_bytes,'heldout_evaluation_output_bytes':heldout_bytes,
            'frozen_model_and_prior_output_bytes':model_bytes+empirical_bytes,
            'publication_and_model_identity_cpu_seconds':publication,'transform_cpu_seconds':transforms,
            'tuning_and_selected_predictions_cpu_seconds':prediction,'calibration_cpu_seconds':calibration,
            'prediction_serialization_cpu_seconds':ancillary('prediction_serialization_cpu_seconds',selected_rows),
            'heldout_prediction_cpu_seconds':heldout_prediction+ancillary('prediction_serialization_cpu_seconds',heldout_rows),
            'prediction_output_bytes_upper':selected_prediction_bytes,'heldout_prediction_output_bytes_upper':heldout_prediction_bytes})
    numerical=sum(value['linear_fit_cpu_seconds']+value['boosted_fit_cpu_seconds'] for value in estimates)
    selected=sum(value['selection_report_cpu_seconds'] for value in estimates)
    confirmation=sum(value['heldout_report_cpu_seconds']+value['heldout_prediction_cpu_seconds'] for value in estimates)
    ancillary=sum(sum(value[key] for key in ('empirical_baseline_cpu_seconds','transform_cpu_seconds','tuning_and_selected_predictions_cpu_seconds',
        'calibration_cpu_seconds','prediction_serialization_cpu_seconds','publication_and_model_identity_cpu_seconds')) for value in estimates)
    parameter_output=sum(value['frozen_model_and_prior_output_bytes'] for value in estimates)
    publication_metadata_bound=8*1024*1024
    return {'purpose':'Complete target-specific resource measurements; no market-model selection or predictive-quality result',
        'resource_unit_reuse':reuse,'expanded_resource_unit_reuse':None if expanded is None else expanded['reuse'],
        'actual_optimizer_calls':0 if expanded is not None else len(larger_trees)+sum(unit['actual_optimizer_calls'] for unit in storage_units.values()),
        'actual_empirical_distribution_calls':0 if expanded is not None else 2+sum(unit['actual_empirical_distribution_calls'] for unit in storage_units.values()),
        'actual_calibration_calls':0,'actual_prepared_rows':matrix.size,'actual_inventory_cpu_seconds':inventory_cpu,
        'actual_optimizer_dates':[int(day) for day in days[-100:]],'fits':all_fits,'evaluation_units':categorical_units,
        'continuous_evaluation_units':continuous_units,'complete_storage_units':storage_units,'targets':estimates,
        'derived_output_bytes':reuse['reused_evaluation_artifacts_bytes']+sum(unit['compressed_output_bytes'] for unit in continuous_units)+sum(unit['derived_output_bytes'] for unit in storage_units.values()),
        'projected_fit_cpu_seconds_conservative':(numerical+selected+ancillary+inventory_cpu*10)*1.5,
        'projected_confirmation_model_cpu_seconds_conservative':(confirmation+inventory_cpu*4)*1.5,
        'projected_frozen_model_and_prior_output_bytes_conservative':parameter_output*1.5,
        'projected_fit_output_bytes_conservative':(parameter_output+sum(value['evaluation_output_bytes']+value['prediction_output_bytes_upper'] for value in estimates))*1.5+publication_metadata_bound,
        'projected_confirmation_model_output_bytes_conservative':sum(value['heldout_evaluation_output_bytes']+value['heldout_prediction_output_bytes_upper'] for value in estimates)*1.5+publication_metadata_bound,
        'projected_model_working_array_bytes':max(math.ceil(value['planned_fit_rows_upper']*(16*max(value['feature_widths'].values())+
            16*(value['fused_continuous_targets']*len(plan['quantiles']) if value['kind']=='continuous' else value['classes'])+64)
            +48*min(value['planned_fit_rows_upper'],65536)*(value['fused_continuous_targets']*len(plan['quantiles']) if value['kind']=='continuous' else value['classes'])) for value in estimates),
        'uncertainty_factor':1.5,'observed_worker_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
        'limitations':['Two actual tree row sizes and iteration counts identify fixed/variable terms but do not certify asymptotic complexity.',
            'Continuous reports are measured directly with all18 metrics and1000 date-block replicates; categorical and interval reports retain class-calibration work.',
            'Storage measurements include full empirical atoms/masses, complete serving models, restore validation and all-model prediction; failed coefficients are charged at full finite-number length.',
            'Empirical atoms/masses are retained once and released before allocating solver designs; their complete artifact is verified at freeze/restore.',
            'All actual per-stage, cumulative CPU, memory and aggregate output limits remain binding.'],
        'cpu_seconds_internal':time.process_time()-start}
