"""Reuse the completed, source-bound readmission from registered check10.

The failed check remains failed. Only its exact completed source stage and
immutable corrected table are reused, with the original reader and validator
dependencies unchanged. No new raw-source observation is claimed.
"""
import hashlib
import json
import time

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import artifact_ref, digest
from trading_research.operations.trials import TrialRegistry
from trading_research.research.jumbo_checkpoints import _file


def validate_source_receipt(packet, protocol, prior, old_packet, state, stage, report):
    attempt = state['attempts'].get(prior['attempt_id'])
    trial = state['trials'].get(prior['trial_id'])
    if (prior['success'] is not False or prior['mode'] != 'check'
            or prior['family'] != protocol['family'] or not prior['within_declared_limits']
            or attempt is None or attempt['status'] != 'failed' or trial is None
            or trial['code_hash'] != prior['code_snapshot']['sha256']
            or attempt['trial_id'] != prior['trial_id'] or attempt['family'] != protocol['family']
            or old_packet['attempt_id'] != prior['attempt_id'] or old_packet['trial_id'] != prior['trial_id']
            or old_packet['analysis_plan'] != packet['analysis_plan']
            or old_packet['protocol_sha256'] != packet['protocol_sha256']
            or not any(r['kind'] == 'research_study_execution' and r['sha256'] == digest(prior)
                       for r in attempt['result_artifacts'])):
        raise IntegrityError('source stage lacks its exact failed registered receipt')
    if (stage['accepted'] is not True or stage['status'] != 'price_readmitted'
            or report.get('actual_accepted') is not True or report.get('actual_status') != 'price_readmitted'
            or report.get('original_admission_unchanged') is not True
            or report.get('generic_rows_unchanged_outside_target_ambiguity') is not True
            or stage['recovered_primary_minutes'] != report['recovered_primary_minutes']
            or stage['cpu_seconds'] != report['cpu_seconds_internal']):
        raise IntegrityError('retained source stage is not the completed narrow readmission')


def source_supplement(packet, protocol, root, store, admission, *, remaining_bytes):
    from trading_research.research.jumbo_study import _definition_supplement, _read_table
    from tools.jumbo_verification import retained_function_fingerprint
    execution = store.read_json(artifact_ref(packet['execution_plan']))
    if not execution.get('retained_source_stage_review'):
        return _definition_supplement(store, protocol, root, admission, remaining_bytes=remaining_bytes,
            snapshot_binding=_file(root, execution['source_snapshot_contract'])
                if execution.get('source_snapshot_contract') else None)
    start = time.process_time()
    review = _file(root, execution['retained_source_stage_review'])
    prior = _file(root, review['execution'])
    old_packet = _file(root, review['packet'])
    stage = review['completed_source_readmission']
    report = store.read_json(artifact_ref(stage['artifact']))
    validate_source_receipt(packet, protocol, prior, old_packet,
                            TrialRegistry(root / 'evidence/trials').state(), stage, report)
    log = store.read(artifact_ref(prior['worker_log']))
    logged = [json.loads(line) for line in log.decode().splitlines()
              if line.startswith('{') and '"actual_definition_supersession"' in line]
    if logged != [stage]:
        raise IntegrityError('retained source result differs from its registered worker log')
    old_execution = store.read_json(artifact_ref(old_packet['execution_plan']))
    if old_execution['source_snapshot_contract'] != execution['source_snapshot_contract']:
        raise IntegrityError('source snapshot acquisition/semantics binding changed')
    snapshot = store.read_json(artifact_ref(prior['code_snapshot']))
    for path in execution['source_stage_dependency_closure']:
        if (path not in snapshot['manifest']
                or packet['code_manifest'].get(path) != snapshot['manifest'][path]):
            raise IntegrityError('retained source validator/reader dependency changed')
    path = 'src/trading_research/research/jumbo_study.py'
    old = bytes.fromhex(snapshot['files'][path]['$bytes'])
    current = (root / path).read_bytes()
    if (hashlib.sha256(old).hexdigest() != snapshot['manifest'][path]
            or hashlib.sha256(current).hexdigest() != packet['code_manifest'][path]):
        raise IntegrityError('retained source wrapper is outside its complete snapshot')
    for name in ('_definition_supplement', '_read_table', '_put_table', '_coverage', '_ns'):
        if retained_function_fingerprint(old, name) != retained_function_fingerprint(current, name):
            raise IntegrityError('source readmission validation/serialization wrapper changed')
    source = [r for r in admission['partitions'] if r['root'] == 'NQ'
              and r['canonical_table'] == report['original_canonical_table']]
    if (len(source) != 1 or source[0]['source_path'] != report['generic_source_path']
            or admission['primary_rows'] != report['original_primary_rows']
            or admission['valid_primary_rows'] != report['original_valid_primary_rows']):
        raise IntegrityError('source correction belongs to a different admitted population')
    table_ref = report['corrected_canonical_table']
    output_bytes = stage['artifact']['size_bytes'] + table_ref['size_bytes']
    if output_bytes > remaining_bytes:
        raise IntegrityError('reused source artifacts exceed the aggregate output ceiling')
    table = _read_table(store, table_ref)
    if (table.num_rows != table_ref['rows'] or table.num_rows != report['corrected_coverage']['rows']
            or report['corrected_rows'] != report['recovered_primary_minutes']):
        raise IntegrityError('retained corrected source row count differs')
    return {'report': report, 'artifact': stage['artifact'], 'corrected_table': table,
            'derived_output_bytes': output_bytes, 'raw_read_attempts_current': 0,
            'cpu_seconds_current': time.process_time() - start,
            'reuse': {'original_attempt_id': prior['attempt_id'], 'original_attempt_status': 'failed',
                     'original_source_stage_cpu_seconds': stage['cpu_seconds'],
                     'scope': 'Exact completed source readmission and corrected table only; original attempt remains failed.'}}
