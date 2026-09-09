"""Reuse exact completed resource units from the successful registered check.

This preserves their original CPU/attempt attribution. Only unchanged numerical
and reporting units are reused; the revised production storage path and larger
tree units must be measured in the current registered worker.
"""
import hashlib
import ast
import time

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import artifact_ref, digest
from trading_research.operations.trials import TrialRegistry
from trading_research.research.jumbo_checkpoints import _file


def _completed_expanded_rows(log):
    """Require each complete measured unit once; incomplete logs are unusable."""
    import json
    import math
    groups = {'completed_larger_tree_unit': [], 'completed_continuous_evaluation_unit': [],
              'completed_full_model_storage_unit': []}
    for line in log.splitlines():
        if line.startswith('{'):
            row = json.loads(line)
            if row.get('preflight') in groups:
                groups[row['preflight']].append(row['measurement'])
    trees = groups['completed_larger_tree_unit']
    reports = groups['completed_continuous_evaluation_unit']
    stored = groups['completed_full_model_storage_unit']
    if (len(trees) != 4 or {(r['kind'], r['iteration_cap']) for r in trees} !=
            {(kind, cap) for kind in ('hgb_classification', 'hgb_quantile') for cap in (10, 20)}
            or any(r['iterations'] != r['iteration_cap'] or r['actual_dates'] != 99
                   or r['status'] != 'completed_fixed_iter' or r['failure'] is not None
                   or not math.isfinite(r['cpu_seconds']) or r['cpu_seconds'] <= 0 for r in trees)
            or len(reports) != 2 or [r['dates'] for r in reports] != [20, 253]
            or any(r['kind'] != 'continuous' or r['metrics'] != 18 or r['groups'] != 433 for r in reports)
            or len(stored) != 3 or {r['kind'] for r in stored} !=
               {'categorical', 'interval_categorical', 'continuous'}
            or any(r['complete_frozen_family_roundtrip'] is not True for r in stored)):
        raise IntegrityError('incomplete, duplicated or different expanded model resource units')
    storage = {r['kind']: r for r in stored}
    if (storage['categorical']['targets'] != ['path']
            or storage['interval_categorical']['targets'] != ['first_duration']
            or storage['continuous']['target_count'] != 6
            or storage['continuous']['exact_prior_serving_scalar_comparisons'] != 258030
            or storage['continuous']['full_prior_validation']['full_atom_and_mass_evidence_retained'] is not True):
        raise IntegrityError('completed model-storage population or exact roundtrip differs')
    return {'larger_trees': trees, 'continuous_units': reports, 'storage_units': storage}


def retained_expanded_model_units(packet, protocol, root, store, inventory):
    """Reuse completed check15 units without promoting its failed overall run.

    Receipt, exact raw log, source population, runtime and numerical dependency
    bytes remain required. Only the declared orchestration wrapper has changed.
    All unchanged production measurement functions are additionally AST-bound.
    """
    from tools.jumbo_verification import retained_function_fingerprint
    start = time.process_time()
    execution = store.read_json(artifact_ref(packet['execution_plan']))
    binding = execution.get('retained_expanded_model_units')
    if binding is None:
        return None
    review = _file(root, binding['review'])
    prior = _file(root, review['execution'])
    state = TrialRegistry(root / 'evidence/trials').state()
    attempt = state['attempts'].get(prior['attempt_id'])
    trial = state['trials'].get(prior['trial_id'])
    if (prior.get('success') is not False or prior.get('mode') != 'check'
            or prior['family'] != protocol['family'] or attempt is None or trial is None
            or attempt['status'] != 'failed' or attempt['trial_id'] != prior['trial_id']
            or attempt['family'] != protocol['family'] or trial['code_hash'] != prior['code_snapshot']['sha256']
            or any(prior[key] != packet[key] for key in ('protocol_sha256', 'analysis_plan', 'model_plan'))
            or prior['verification_contracts']['fit']['runtime_versions'] !=
               packet['verification_contracts']['fit']['runtime_versions']
            or not any(ref['kind'] == 'research_study_execution' and ref['sha256'] == digest(prior)
                       for ref in attempt['result_artifacts'])):
        raise IntegrityError('completed expanded units lack their original failed registered receipt')
    old_execution = store.read_json(artifact_ref(prior['execution_plan']))
    for key in ('completed_shards', 'source_snapshot_contract', 'reference_manifest',
                'anchor_supplement', 'retained_model_workload', 'completed_development_extraction_review'):
        if execution[key] != old_execution[key]:
            raise IntegrityError('expanded resource units have a different numerical input population')
    snapshot = store.read_json(artifact_ref(prior['code_snapshot']))
    for path in binding['unchanged_full_files']:
        if path not in snapshot['manifest'] or packet['code_manifest'].get(path) != snapshot['manifest'][path]:
            raise IntegrityError('expanded resource dependency changed: ' + path)
    for path, names in binding['unchanged_functions'].items():
        old = bytes.fromhex(snapshot['files'][path]['$bytes'])
        current = (root / path).read_bytes()
        if (hashlib.sha256(old).hexdigest() != snapshot['manifest'][path]
                or hashlib.sha256(current).hexdigest() != packet['code_manifest'][path]):
            raise IntegrityError('expanded resource wrapper is outside its retained snapshot')
        def globals_ast(source):
            tree = ast.parse(source)
            return ast.dump(ast.Module(body=[node for node in tree.body
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))],
                type_ignores=[]), include_attributes=False)
        if globals_ast(old) != globals_ast(current):
            raise IntegrityError('expanded resource module globals or imports changed')
        for name in names:
            if retained_function_fingerprint(old, name) != retained_function_fingerprint(current, name):
                raise IntegrityError('expanded resource measurement function changed: ' + name)
    log = store.read(artifact_ref(prior['worker_log'])).decode()
    if ('Ran 440 tests' not in log or '\nOK\n' not in log
            or 'IntegrityError: completed extraction dependency changed: tests/test_trial_budget_amendment.py' not in log
            or len(inventory) != 116):
        raise IntegrityError('expanded resource log or target inventory differs from its exact completed scope')
    result = _completed_expanded_rows(log)
    if result != review['completed_expanded_resource_units']:
        raise IntegrityError('expanded resource review differs from the original worker log')
    for unit in result['continuous_units']:
        for key in ('grouped_artifact', 'overall_artifact'):
            store.read(artifact_ref(unit[key]))
    for unit in result['storage_units'].values():
        for ref in (unit['frozen_family'], *unit['empirical_evidence']):
            store.read(artifact_ref({k: ref[k] for k in ('sha256', 'size_bytes', 'kind')}))
    result['reuse'] = {'original_attempt_id': prior['attempt_id'], 'original_attempt_status': 'failed',
        'original_attempt_cpu_seconds': prior['cpu_seconds'],
        'original_optimizer_calls': 4 + sum(u['actual_optimizer_calls'] for u in result['storage_units'].values()),
        'original_empirical_distribution_calls': 2 + sum(u['actual_empirical_distribution_calls'] for u in result['storage_units'].values()),
        'cpu_seconds_current_validation': time.process_time() - start,
        'scope': 'Exact completed larger-tree, continuous-report and full production storage/prediction units only; failed check15 remains failed.'}
    print(__import__('json').dumps({'preflight': 'retained_completed_expanded_resource_units',
                                  'reuse': result['reuse']}), flush=True)
    return result


def retained_model_units(packet, protocol, root, store, inventory):
    from tools.jumbo_verification import retained_function_fingerprint
    start = time.process_time()
    execution = store.read_json(artifact_ref(packet['execution_plan']))
    binding = execution.get('retained_model_workload')
    if not binding:
        raise IntegrityError('explicit completed model-resource reuse binding required')
    review = _file(root, binding['review'])
    prior = _file(root, review['execution'])
    state = TrialRegistry(root / 'evidence/trials').state()
    attempt = state['attempts'].get(prior['attempt_id'])
    trial = state['trials'].get(prior['trial_id'])
    if (prior.get('success') is not True or prior['mode'] != 'check'
            or prior['family'] != protocol['family'] or attempt is None or trial is None
            or attempt['status'] != 'succeeded' or attempt['trial_id'] != prior['trial_id']
            or attempt['family'] != protocol['family'] or trial['code_hash'] != prior['code_snapshot']['sha256']
            or any(prior[key] != packet[key] for key in ('protocol_sha256', 'analysis_plan', 'model_plan'))
            or not any(ref['kind'] == 'research_study_execution' and ref['sha256'] == digest(prior)
                       for ref in attempt['result_artifacts'])):
        raise IntegrityError('resource units lack their exact successful registered receipt')
    worker = store.read_json(artifact_ref(prior['worker_report']))
    if worker != _file(root, review['worker']) or worker.get('success') is not True:
        raise IntegrityError('retained resource worker differs from its registered artifact')
    old_execution = store.read_json(artifact_ref(prior['execution_plan']))
    for key in ('completed_shards', 'source_snapshot_contract', 'reference_manifest'):
        if execution[key] != old_execution[key]:
            raise IntegrityError('resource units belong to a different admitted input population')
    snapshot = store.read_json(artifact_ref(prior['code_snapshot']))
    for path in binding['unchanged_full_files']:
        if path not in snapshot['manifest'] or packet['code_manifest'].get(path) != snapshot['manifest'][path]:
            raise IntegrityError('retained resource numerical/data dependency changed: ' + path)
    for path, names in binding['unchanged_functions'].items():
        old = bytes.fromhex(snapshot['files'][path]['$bytes'])
        current = (root / path).read_bytes()
        if (hashlib.sha256(old).hexdigest() != snapshot['manifest'][path]
                or hashlib.sha256(current).hexdigest() != packet['code_manifest'][path]):
            raise IntegrityError('resource wrapper is outside its complete code snapshot')
        def globals_ast(source):
            tree=ast.parse(source)
            return ast.dump(ast.Module(body=[node for node in tree.body
                if not isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))],type_ignores=[]),include_attributes=False)
        if globals_ast(old)!=globals_ast(current):
            raise IntegrityError('retained resource module globals or imports changed')
        for name in names:
            if retained_function_fingerprint(old, name) != retained_function_fingerprint(current, name):
                raise IntegrityError('retained resource wrapper changed: ' + path + ':' + name)
    parity = worker['actual_extraction_parity']
    model = parity['model_preflight']
    if (parity.get('passed') is not True or model['actual_prepared_rows'] != 108784
            or len(inventory) != len(model['targets']) or len(model['fits']) != 16
            or [row['dates'] for row in model['evaluation_units']] != [20, 253]
            or model['evaluation_units'][0]['storage_verification']['passed'] is not True):
        raise IntegrityError('retained complete annual resource population differs')
    for current, old in zip(inventory, model['targets'], strict=True):
        # Added accounting fields do not change old target/cohort quantities.
        if any(current[key] != old[key] for key in current if key in old):
            raise IntegrityError('current independent target inventory differs from retained resource units')
    output_bytes = 0
    for unit in model['evaluation_units']:
        for key in ('grouped_artifact', 'overall_artifact'):
            store.read(artifact_ref(unit[key]))
            output_bytes += unit[key]['size_bytes']
    reuse = {'original_attempt_id': prior['attempt_id'], 'original_attempt_status': 'succeeded',
             'original_optimizer_calls': 16, 'original_empirical_distribution_calls': 12,
             'original_calibration_calls': 12, 'original_evaluation_units': 2,
             'scope': 'Unchanged actual optimizer and categorical-report resource units only. New tree-size and full model-storage consumers are measured in the current worker.',
             'cpu_seconds_current_validation': time.process_time() - start,
             'reused_evaluation_artifacts_bytes': output_bytes}
    return model['fits'], model['evaluation_units'], reuse


def completed_development_extraction(packet,protocol,root,store):
    """A completed extraction contributes zero remaining CPU, with its receipt."""
    execution=store.read_json(artifact_ref(packet['execution_plan']))
    if not execution.get('completed_development_extraction_review'):
        return None
    review=_file(root,execution['completed_development_extraction_review'])
    prior=_file(root,review['execution'])
    state=TrialRegistry(root/'evidence/trials').state()
    attempt=state['attempts'].get(prior['attempt_id'])
    trial=state['trials'].get(prior['trial_id'])
    if (prior.get('success') is not True or prior.get('mode')!='develop' or prior.get('phase')!='extract'
            or prior['family']!=protocol['family'] or attempt is None or trial is None
            or attempt['status']!='succeeded' or attempt['trial_id']!=prior['trial_id']
            or trial['code_hash']!=prior['code_snapshot']['sha256']
            or any(prior[key]!=packet[key] for key in ('protocol_sha256','analysis_plan','model_plan'))
            or not any(ref['kind']=='research_study_execution' and ref['sha256']==digest(prior)
                       for ref in attempt['result_artifacts'])):
        raise IntegrityError('completed development extraction lacks its exact registered receipt')
    for path,sha in prior['verification_contracts']['extract']['source_and_test_files'].items():
        if packet['code_manifest'].get(path)!=sha:
            raise IntegrityError('completed extraction dependency changed: '+path)
    worker=store.read_json(artifact_ref(prior['worker_report']))
    if (worker!=_file(root,review['worker']) or not worker.get('success')
            or len(worker['shards'])!=10 or len(worker['model_shards'])!=10
            or {(row['root'],row['year']) for row in worker['shards']}!={(root,year) for root in ('NQ','ES') for year in range(2020,2025)}
            or worker['heldout_target_rows_inspected']!=0):
        raise IntegrityError('completed development population is incomplete or differs')
    return {'attempt_id':prior['attempt_id'],'execution':review['execution'],
            'actual_cpu_seconds':prior['cpu_seconds'],'actual_derived_output_bytes':worker['derived_output_bytes'],
            'annual_shards':10,'row_counts':worker['row_counts'],'narrative':review['narrative'],
            'source_sensitivity_narrative':review['source_sensitivity_narrative'],
            'remaining_extraction_cpu_seconds':0.,'scope':'Complete original and corrected development extraction already executed; no repeat extraction is budgeted.'}
