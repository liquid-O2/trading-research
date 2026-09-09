"""Bounded publication of independent chronological Context comparisons.

The outer worker supplies already admitted matrices and owns resource limits.
Every fixed alternative is retained. Confirmation only restores frozen models.
"""
from dataclasses import asdict
import gc
import gzip
import hashlib
import time

import numpy as np

from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.operations.artifacts import artifact_ref, canonical_json, digest
from trading_research.research.jumbo_models import (fit_categorical_family, fit_continuous_family,
    choose_tuning_model, calibration_for, evaluate_target, predict_model, apply_calibration, json_safe, _phase_rows)
from trading_research.research.jumbo_targets import Target

VERSION = 'jumbo-independent-fits-v1'


def put_json_compressed(store, value, *, kind, remaining_bytes, normalized=False):
    if normalized:
        from trading_research.research.jumbo_evaluation_storage import normalized_json_bytes
        raw = normalized_json_bytes(value)
    else:
        raw = canonical_json(json_safe(value))
    payload = gzip.compress(raw, compresslevel=3, mtime=0)
    if len(payload) > remaining_bytes:
        raise DependencyUnavailable('compressed research result exceeds remaining aggregate output allowance')
    ref = store.put_bytes(payload, kind=kind)
    return {**asdict(ref), 'encoding': 'gzip-json', 'uncompressed_sha256': hashlib.sha256(raw).hexdigest(),
            'uncompressed_size_bytes': len(raw)}


def read_json_compressed(store, value):
    import json
    ref = artifact_ref({k:value[k] for k in ('sha256','size_bytes','kind')})
    payload = store.read(ref)
    if value.get('encoding') != 'gzip-json' or value.get('uncompressed_size_bytes',-1) > 512*1024*1024:
        raise IntegrityError('bounded declared compressed research artifact required')
    import io
    with gzip.GzipFile(fileobj=io.BytesIO(payload)) as stream:
        raw = stream.read(value['uncompressed_size_bytes']+1)
    if len(raw)!=value['uncompressed_size_bytes'] or hashlib.sha256(raw).hexdigest()!=value['uncompressed_sha256']:
        raise IntegrityError('retained research artifact expanded identity differs')
    return json.loads(raw)


def common_targets(matrix):
    output = {}
    for name in ('common_high_priorW','common_low_priorW','common_terminal_priorW'):
        if name not in matrix.fields:
            raise IntegrityError('declared common receiver target absent')
        metadata = {'target':name,'unit':'prior actual cash-session widths','nonnegative':False,
                    'definition':'common 10:01 New York to actual cash close receiver outcome relative to available exact close',
                    'source_matrix':matrix.manifest['id']}
        metadata['id'] = digest(metadata)
        output[name] = Target(name,'continuous',matrix.fields[name],matrix.fields['common_target_eligible'],
                              matrix.fields['common_maturity_at_ns'],metadata)
    return output


def _families(matrix, targets):
    """Only identical fit populations may share the fused numerical optimizer."""
    continuous = {}
    for name,target in targets.items():
        if target.kind!='continuous':
            yield (name,), (target,)
        else:
            mask = target.phase(matrix,'fit')
            key = hashlib.sha256(mask.tobytes()).hexdigest()
            if key in continuous and not np.array_equal(mask,continuous[key][0]):
                raise IntegrityError('training population digest collision')
            continuous.setdefault(key,(mask,[]))[1].append(target)
    for _,values in continuous.values():
        yield tuple(t.name for t in values),tuple(values)


def _summary(evaluation):
    comparisons = {}
    for name,value in evaluation.get('comparisons',{}).items():
        overall = value.get('overall',{}).get('groups',{}).get('0',{})
        comparisons[name] = {'status':value['status'],'model_id':value['model_id'],
            'primary_loss':overall.get('metrics',{}).get('primary_loss'), 'paired':overall.get('paired')}
    return {'target':evaluation['target'],'phase':evaluation['phase'],'status':evaluation['status'],
            'eligible_rows':evaluation.get('eligible_rows',0),'intended_rows':evaluation['intended_rows'],
            'comparisons':comparisons}


def _emit_predictions(store, matrix, target, family, tuned, calibration, *, phase, target_index, plan, remaining_bytes):
    """Save exact source row coordinates and final selected/baseline forecasts."""
    import io
    mask = _phase_rows(matrix,phase) & target.applicable(matrix)
    scored = target.phase(matrix,phase)[mask]
    model = family['models'][tuned['winner']]
    pred,_ = predict_model(model,matrix,mask)
    prediction = apply_calibration(calibration,pred,model=model,target=target,target_index=target_index)
    base,_ = predict_model(family['models']['empirical'],matrix,mask)
    if target.kind=='continuous':
        prediction,base = prediction[:,0],base[:,target_index]
    arrays = {'prepared_row':np.flatnonzero(mask).astype(np.int64),'date':matrix.fields['date'][mask],
              'root':matrix.fields['root'][mask], 'clock':matrix.fields['clock'][mask],
              'horizon':matrix.fields['horizon'][mask], 'origin_ns':matrix.fields['origin_ns'][mask],
              'label_known_at_ns':target.label_known_at_ns[mask], 'label':target.values[mask],
              'scored_mask':scored,
              'selected_calibrated':prediction,'empirical':base}
    if 'anchor_identified' in matrix.fields:
        arrays['causal_geometry_available'] = (matrix.fields['anchor_identified'][mask]
                       & (matrix.fields['formation_width_ticks'][mask] > 0))
        for name in ('anchor_ticks','formation_width_ticks','anchor_known_at_ns'):
            if name in matrix.fields:
                arrays[name] = matrix.fields[name][mask]
    # This provider population uses intended phase dates and source clocks.
    # Future truth never determines whether a frozen prediction is retained;
    # scored_mask separately identifies the actual matured assessment rows.
    stream = io.BytesIO()
    np.savez_compressed(stream,**arrays)
    payload = stream.getvalue()
    if len(payload)>remaining_bytes:
        raise DependencyUnavailable('retained independent predictions exceed the aggregate output allowance')
    ref=store.put_bytes(payload,kind='jumbo_independent_target_predictions_npz_v1')
    return {**asdict(ref),'matrix_id':matrix.manifest['id'],'target':target.name,'phase':phase,
            'model_id':model['id'],'scored_rows':int(scored.sum()),'intended_prediction_rows':int(mask.sum()),
            'prediction_population':'all intended source-clock phase rows before outcome eligibility; causal geometry mask retained separately',
            'retrospective_reconstruction':True,'actual_artifact_created_at_ns':time.time_ns(),
            'historical_training_calibration_closure_ns':1719792000000000000,'array_schema':{k:{'dtype':str(a.dtype),'shape':list(a.shape)} for k,a in arrays.items()},
            'calibration':calibration,'categories':matrix.categories,'target_metadata':target.metadata}


def fit_domain(matrix, targets, store, *, domain, plan, maximum_output_bytes, checkpoint=None):
    start=time.process_time()
    output_bytes=0
    records=[]
    expected=tuple(targets)
    if not expected:
        raise ContractError('a Context domain must declare independent targets')
    for names,values in _families(matrix,targets):
        clock=time.process_time()
        def retain_prior(evidence):
            nonlocal output_bytes
            reference=put_json_compressed(store,evidence,kind='jumbo_full_empirical_quantile_distributions_gzip_v1',
                    remaining_bytes=maximum_output_bytes-output_bytes,normalized=True)
            output_bytes+=reference['size_bytes']
            return reference
        family=(fit_continuous_family(matrix,values,plan=plan,prior_writer=retain_prior) if values[0].kind=='continuous'
                else fit_categorical_family(matrix,values[0],plan=plan))
        from trading_research.research.jumbo_prior_storage import validate_family_priors
        validate_family_priors(family,store=store)
        family_ref=put_json_compressed(store,family,kind='jumbo_frozen_model_family_gzip_v1',remaining_bytes=maximum_output_bytes-output_bytes,normalized=True)
        output_bytes+=family_ref['size_bytes']
        # Complete atoms/masses have been retained in family_ref. Predictions
        # use the exact small serving view, so release the audit-only arrays.
        family.pop('empirical_distribution_evidence', None)
        for index,target in enumerate(values):
            if not family['models']:
                record={'target':target.name,'target_index':index,'family':family_ref,'status':family['status'],
                        'fit':family['fit'],'target_metadata':target.metadata,'domain':domain}
            else:
                tuned=choose_tuning_model(matrix,target,family,plan=plan,target_index=index)
                selected=family['models'][tuned['winner']]
                calibration=calibration_for(matrix,target,selected,plan=plan,target_index=index)
                evaluation=evaluate_target(matrix,target,family,phase='select',plan=plan,tuned=tuned,
                                            calibration=calibration,target_index=index)
                assessment=put_json_compressed(store,evaluation,kind='jumbo_context_selection_evaluation_gzip_v1',remaining_bytes=maximum_output_bytes-output_bytes,normalized=True)
                output_bytes+=assessment['size_bytes']
                predictions=_emit_predictions(store,matrix,target,family,tuned,calibration,phase='select',target_index=index,plan=plan,remaining_bytes=maximum_output_bytes-output_bytes)
                output_bytes+=predictions['size_bytes']
                record={'target':target.name,'target_index':index,'family':family_ref,'status':'independently_evaluated',
                        'domain':domain,'target_metadata':target.metadata,'tuning':tuned,'calibration':calibration,
                        'selection_evaluation':assessment,'selection_predictions':predictions,'summary':_summary(evaluation)}
                del evaluation
            record=json_safe(record)
            records.append(record)
            if checkpoint is not None:
                expected_bytes=len(canonical_json(record))
                if expected_bytes>maximum_output_bytes-output_bytes:
                    raise DependencyUnavailable('target checkpoint exceeds aggregate output allowance before publication')
                written=checkpoint(record)
                if type(written) is not int or written!=expected_bytes:
                    raise IntegrityError('checkpoint writer must retain exactly the canonical target record bytes')
                output_bytes+=written
        print(__import__('json').dumps({'stage':'independent_context_family','domain':domain,'targets':names,
               'cpu_seconds':time.process_time()-clock,'output_bytes':output_bytes}),flush=True)
        del family
        gc.collect()
    if set(r['target'] for r in records)!=set(expected):
        raise IntegrityError('independent target population did not close')
    return {'version':VERSION,'domain':domain,'matrix_manifest':matrix.manifest,'targets':records,
            'model_plan':plan,'derived_output_bytes':output_bytes,'cpu_seconds':time.process_time()-start,
            'heldout_rows_used':0,'fixed_fit_cut':'2022-12-31','tuning_cut':'2023-12-31',
            'calibration_cut':'2024-06-30','selection_cut':'2024-12-31',
            'confirmation_rule':'Restore unchanged model+calibration records; evaluate frozen alternatives and winner, with no refit or reselection'}


def confirm_domain(matrix, targets, frozen, store, *, plan, maximum_output_bytes, checkpoint=None):
    if frozen['version']!=VERSION or frozen['model_plan']!=plan or set(targets)!={r['target'] for r in frozen['targets']}:
        raise IntegrityError('confirmation target/model-plan contract differs from frozen development')
    records=[]
    output_bytes=0
    cached_ref,cached_family=None,None
    for original in frozen['targets']:
        target=targets[original['target']]
        if original['status']!='independently_evaluated':
            records.append({**original,'phase':'heldout','status':'development_model_unavailable'})
            continue
        ref=original['family']
        if cached_ref!=ref['sha256']:
            cached_family=read_json_compressed(store,ref)
            from trading_research.research.jumbo_prior_storage import validate_family_priors
            validate_family_priors(cached_family,store=store)
            cached_family.pop('empirical_distribution_evidence', None)
            cached_ref=ref['sha256']
        family=cached_family
        evaluation=evaluate_target(matrix,target,family,phase='heldout',plan=plan,tuned=original['tuning'],
                      calibration=original['calibration'],target_index=original['target_index'])
        assessment=put_json_compressed(store,evaluation,kind='jumbo_context_heldout_evaluation_gzip_v1',remaining_bytes=maximum_output_bytes-output_bytes,normalized=True)
        output_bytes+=assessment['size_bytes']
        predictions=_emit_predictions(store,matrix,target,family,original['tuning'],original['calibration'],phase='heldout',
                      target_index=original['target_index'],plan=plan,remaining_bytes=maximum_output_bytes-output_bytes)
        output_bytes+=predictions['size_bytes']
        record={'target':target.name,'phase':'heldout','domain':frozen['domain'],'status':'independently_evaluated',
                'frozen_development':original,'heldout_evaluation':assessment,'heldout_predictions':predictions,
                'summary':_summary(evaluation)}
        record=json_safe(record)
        records.append(record)
        if checkpoint is not None:
            expected_bytes=len(canonical_json(record))
            if expected_bytes>maximum_output_bytes-output_bytes:
                raise DependencyUnavailable('confirmation checkpoint exceeds aggregate output allowance before publication')
            written=checkpoint(record)
            if type(written) is not int or written!=expected_bytes:
                raise IntegrityError('checkpoint writer must retain exact canonical record bytes')
            output_bytes+=written
        del evaluation
    return {'version':VERSION,'domain':frozen['domain'],'phase':'heldout','matrix_manifest':matrix.manifest,
            'targets':records,'derived_output_bytes':output_bytes,'new_fits':0,'new_calibrations':0,'reselections':0}
