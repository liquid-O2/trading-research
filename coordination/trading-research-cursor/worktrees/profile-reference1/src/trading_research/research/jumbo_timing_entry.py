"""Registered root partitions for Deliverable 1 Jumbo timing statistics."""
import hashlib
import json
from pathlib import Path
import time
import unittest

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import ArtifactStore, artifact_ref, digest
from trading_research.operations.trials import TrialRegistry
from trading_research.research.auction_flow_storage import BoundedOutputs
from trading_research.research.jumbo_timing_statistics import run_timing_statistics, split_source_variants, PRIMARY_VARIANT


def _retained(root, ref, *, maximum=64 * 1024**2):
    path = Path(ref['path'])
    path = (root/path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(root) or 'archive' in path.parts or not path.is_file() or path.stat().st_size > maximum:
        raise IntegrityError('bounded retained timing input required')
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != ref['sha256'] or len(raw) != ref.get('size_bytes', len(raw)):
        raise IntegrityError('retained timing input changed')
    return raw


def _execution_worker(root, ref, registry, family):
    execution = json.loads(_retained(root, ref))
    state = registry.state()
    attempt = state['attempts'].get(execution.get('attempt_id'))
    trial = state['trials'].get(execution.get('trial_id'))
    if (execution.get('success') is not True or execution.get('family') != family
            or attempt is None or trial is None or attempt['status'] != 'succeeded'
            or attempt['family'] != family or attempt['trial_id'] != execution['trial_id']
            or trial['code_hash'] != execution['code_snapshot']['sha256']
            or not any(r['kind'] == 'research_study_execution' and r['sha256'] == digest(execution)
                       for r in attempt['result_artifacts'])):
        raise IntegrityError('timing input lacks its exact successful registered execution')
    worker = registry.artifacts.read_json(artifact_ref(execution['worker_report']))
    if (worker.get('success') is not True or worker.get('attempt_id') != execution['attempt_id']
            or worker.get('trial_id') != execution['trial_id']):
        raise IntegrityError('timing source worker identity mismatch')
    return execution, worker


def _rows_for_root(development, confirmation, root):
    return sum(int(shard['intended_cash_dates']) * 16
               for _, shards in split_source_variants(development, confirmation)
               for shard in shards if shard['root'] == root)


def run(packet, protocol, root):
    root = Path(root).resolve()
    mode = packet['mode']
    if mode not in ('timing-pilot', 'timing-full'):
        raise IntegrityError('registered timing partition mode required')
    registry = TrialRegistry(root/'evidence/trials')
    store = registry.artifacts
    contract = store.read_json(artifact_ref(packet['timing_contract']))
    if (contract.get('kind') != 'jumbo_deliverable1_timing_contract_v1' or contract.get('version') != 1
            or contract.get('family') != protocol['family'] or contract.get('root_order') != ['NQ', 'ES']
            or contract.get('family_statistics_complete') is not False):
        raise IntegrityError('frozen timing definition changed')
    selection = contract['phases'][mode]
    if selection['resource_phase'] != packet['phase']:
        raise IntegrityError('timing phase does not match its registered resource partition')
    analysis = store.read_json(artifact_ref(packet['analysis_plan']))
    _retained(root, contract['analysis_plan'])
    if contract['analysis_plan']['sha256'] != packet['analysis_plan']['sha256']:
        raise IntegrityError('timing analysis identity differs from the admitted plan')
    development_execution, development = _execution_worker(root, contract['development_execution'], registry, protocol['family'])
    confirmation_execution, confirmation = _execution_worker(root, contract['confirmation_execution'], registry, protocol['family'])
    expected_rows = _rows_for_root(development, confirmation, selection['root'])
    predecessor_execution, predecessor_worker = _execution_worker(root, packet['predecessor'], registry, protocol['family'])
    tests = None
    reused = None
    if mode == 'timing-pilot':
        if predecessor_execution != confirmation_execution:
            raise IntegrityError('timing NQ partition needs the frozen descriptive confirmation predecessor')
        began = time.process_time()
        result = unittest.TextTestRunner(verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromNames(contract['tests']))
        tests = {'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
                 'skipped': len(result.skipped), 'passed': result.wasSuccessful() and not result.skipped,
                 'cpu_seconds': time.process_time()-began}
        if not tests['passed']:
            raise IntegrityError('timing verification failed; preserve evidence and reassess')
    else:
        if (predecessor_execution['mode'] != 'timing-pilot'
                or predecessor_execution['verification_contracts']['timing'] != packet['verification_contracts']['timing']
                or predecessor_execution['tools_snapshot'] != packet['tools_snapshot']
                or predecessor_worker.get('timing_contract') != packet['timing_contract']):
            raise IntegrityError('ES timing needs an exact successfully verified NQ implementation and definition')
        reused = predecessor_worker['actual_timing_statistics']
        if reused['success'] is not True or predecessor_worker.get('completed_roots') != ['NQ']:
            raise IntegrityError('first timing partition is incomplete')
        ratio = expected_rows / reused['resources']['date_rows']
        projected_cpu = 1.5 * predecessor_execution['cpu_seconds'] * ratio + 60
        projected_output = 1.5 * reused['resources']['output_bytes'] * ratio + 16*1024**2
        if projected_cpu > packet['limits']['cpu_seconds'] or projected_output > packet['limits']['maximum_output_bytes']:
            raise IntegrityError(f'ES timing measured resource projection exceeds registered allowance: {projected_cpu}, {projected_output}')
        for ref in reused['refs'].values():
            _retained(root, ref, maximum=packet['limits']['maximum_output_bytes'])
    outputs = BoundedOutputs(Path(packet['worker_report']).parent/'timing-outputs',
        maximum_total_bytes=packet['limits']['maximum_output_bytes'] - 16*1024**2,
        maximum_file_bytes=min(packet['limits']['maximum_output_bytes'],512*1024**2))
    actual = run_timing_statistics(store=store, development=development, confirmation=confirmation,
        analysis_plan=analysis, outputs=outputs, roots=(selection['root'],))
    if not actual['success'] or actual['resources']['date_rows'] != expected_rows:
        raise IntegrityError('timing partition did not preserve every declared common-clock/root/date/source row')
    completed = ['NQ'] if reused is None else ['NQ', 'ES']
    partition_refs = [{'root': selection['root'], 'refs': actual['refs']}]
    if reused is not None:
        partition_refs.insert(0, {'root':'NQ','refs':reused['refs'],'accepted_execution':packet['predecessor']})
    combined = {'kind':'jumbo_deliverable1_timing_population_v1', 'completed_roots':completed,
        'all_declared_timing_roots_complete':completed == ['NQ','ES'], 'scientific_contract':packet['timing_contract'],
        'common_date_rows':actual['resources']['date_rows'] + (0 if reused is None else reused['resources']['date_rows']),
        'transition_rows':actual['resources']['transition_rows'] + (0 if reused is None else reused['resources']['transition_rows']),
        'partitions':partition_refs, 'remaining':contract['remaining'], 'family_statistics_complete':False,
        'context_models_complete':False,'location_quality_complete':False,'model_fits':0}
    combined_ref = outputs.json('timing-population.json',combined,kind=combined['kind'])
    report_lines = ['# Jumbo common-clock geometry and transition statistics','',
        'Complete declared roots: '+', '.join(completed)+'.',
        f"Common-clock/source/date observations: {combined['common_date_rows']}; JTR transition observations: {combined['transition_rows']}.",
        'The original NQ2024 acquisition is reported separately from the corrected primary population. Each date contributes once within its source variant. Existing annual formation/path statistics are reused.',
        'These are descriptive timing and geometry results. Predictive Context and Location quality remain later.', '']
    for partition in partition_refs:
        report_lines.extend([f"## {partition['root']}",'',_retained(root,partition['refs']['report']).decode(), ''])
    with outputs.create('jumbo-timing-combined-report.md') as stream:
        stream.write(('\n'.join(report_lines)+'\n').encode())
    combined_report = outputs.reference('jumbo-timing-combined-report.md',kind='jumbo_timing_combined_report_v1')
    return {'success':True,'actual_timing_statistics':actual,'timing_population':combined_ref,
        'timing_report':combined_report,'completed_roots':completed,'tests':tests,
        'tests_reused_from':None if reused is None else packet['predecessor'],
        'timing_contract':packet['timing_contract'],'derived_output_bytes':outputs.written,
        'model_fits':0,'family_statistics_complete':False,'context_models_complete':False,
        'location_quality_complete':False,'economic_or_live_runs':0,
        'scope':'Full declared root-partition common-clock geometry and JTR transition statistics; exact remaining source dependencies retained.'}
