"""Reuse accepted source-window artifacts for new anchor/profile/cohort consumers.

This mode reads immutable check-9 resource, measurement and trade-cache
artifacts. It does not rescan raw files, rebuild native grids or replace the
registered storage contract. Current consumer code is snapshotted by the
parent receipt; accepted producer artifacts stay valid when only downstream
code changed.
"""
from __future__ import annotations

from pathlib import Path
import time

from trading_research.errors import IntegrityError
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.auction_flow_anchor_preflight import check_anchor_unit
from trading_research.research.auction_flow_cohort_preflight import check_cohort_unit
from trading_research.research.auction_flow_storage import read_json_artifact


VERSION = 'auction-flow-accepted-source-downstream-reuse-v1'
KIND = 'auction_flow_accepted_source_downstream_reuse_v1'
COMPARISON_KIND = 'auction_flow_accepted_source_downstream_reuse_comparison_v1'
REQUIRED_RESOURCE_UNITS = 9
_CPU_NAMES = (
    'prior_identity_and_resource_authentication',
    'measurement_authentication_and_source_join',
    'anchor_profile_recalculation',
    'cohort_recalculation',
    'complete_payload_comparison',
    'orchestration_and_report_assembly',
)


def _cpu():
    return {name: 0.0 for name in _CPU_NAMES}


def _acc(cpu, name, started):
    cpu[name] += time.process_time() - started
    return time.process_time()


def _require_reference(reference, *, name):
    if (type(reference) is not dict or type(reference.get('path')) is not str or not reference['path']
            or type(reference.get('sha256')) is not str or len(reference['sha256']) != 64
            or type(reference.get('size_bytes')) is not int or reference['size_bytes'] < 1):
        raise IntegrityError(f'{name} is not a complete size/hash-bound reference')
    return reference


def _join_available(left, right, *, name):
    if left is None or right is None or left != right:
        raise IntegrityError(f'retained supervisor {name} does not join')
    return left


def join_prior_identity(previous, receipt, check_extension):
    """Authenticate a successful prior execution/worker pair and its hashes."""
    worker_ref = _require_reference(check_extension.get('downstream_prior_worker'),
                                    name='downstream_prior_worker')
    execution_ref = _require_reference(check_extension.get('downstream_prior_execution'),
                                       name='downstream_prior_execution')
    if (type(previous) is not dict or type(receipt) is not dict
            or previous.get('success') is not True or previous.get('source_component_verified') is not True
            or receipt.get('success') is not True or receipt.get('within_declared_limits') is not True
            or receipt.get('worker_identity_joined') is not True or receipt.get('exit_code') != 0):
        raise IntegrityError('downstream reuse lacks its successful bounded supervisor receipt')
    preflight = previous.get('actual_source_preflight')
    if type(preflight) is not dict or preflight.get('passed') is not True:
        raise IntegrityError('downstream reuse requires the retained successful complete source component')
    _join_available(previous.get('attempt_id'), receipt.get('attempt_id'), name='attempt_id')
    _join_available(previous.get('trial_id'), receipt.get('trial_id'), name='trial_id')
    protocol = _join_available(previous.get('protocol_sha256'), receipt.get('protocol_sha256'),
                               name='protocol_sha256')
    parent_protocol = check_extension.get('parent_protocol_sha256')
    if parent_protocol is not None and parent_protocol != protocol:
        raise IntegrityError('retained supervisor protocol does not join the registered parent protocol')
    _join_available(previous.get('code_snapshot'), receipt.get('code_snapshot'), name='code_snapshot')
    _join_available(previous.get('tools_snapshot'), receipt.get('tools_snapshot'), name='tools_snapshot')
    _join_available(previous.get('configuration'), receipt.get('configuration'), name='configuration')
    report = receipt.get('worker_report')
    # The worker path has a trailing newline; the supervisor's CAS JSON does
    # not. Authenticate each representation against its actual bytes.
    if (type(report) is not dict or report.get('sha256') != digest(previous)
            or report.get('size_bytes') != len(canonical_json(previous))
            or report.get('kind') != 'auction_flow_worker_report'):
        raise IntegrityError('retained execution worker hash reference does not join')
    path = receipt.get('worker_report_path')
    if path is not None and path != worker_ref['path']:
        raise IntegrityError('retained execution worker path does not join')
    refs = preflight.get('resource_units')
    if type(refs) is not list or len(refs) != REQUIRED_RESOURCE_UNITS:
        raise IntegrityError('downstream reuse requires the retained nine source-window resource units')
    for index, reference in enumerate(refs):
        _require_reference(reference, name=f'retained resource unit {index}')
    return {
        'worker': worker_ref, 'execution': execution_ref, 'resource_units': refs,
        'attempt_id': previous['attempt_id'], 'trial_id': previous.get('trial_id'),
        'protocol_sha256': protocol, 'code_snapshot': previous.get('code_snapshot'),
        'tools_snapshot': previous.get('tools_snapshot'),
        'runtime_versions': previous.get('runtime_versions'),
        'configuration': previous.get('configuration'),
    }


def unit_key(unit):
    return (unit['root'], unit['source_path'], unit['event_start_ns'], unit['event_end_ns'])


def join_resource_identity(resource, measured):
    """Join root/window/instrument/count/manifest/coordinate versions and latency."""
    unit = resource.get('unit')
    if type(unit) is not dict or type(measured) is not dict:
        raise IntegrityError('retained resource unit lost its unit or measurement identity')
    if (unit.get('root') not in ('ES', 'NQ') or unit.get('root') != measured.get('root')
            or unit.get('event_start_ns') != measured.get('event_start_ns')
            or unit.get('event_end_ns') != measured.get('event_end_ns')
            or type(unit.get('source_variant')) is not str or not unit['source_variant']
            or type(unit.get('source_path')) is not str or not unit['source_path']
            or type(unit.get('source_metadata_version')) is not str
            or not unit['source_metadata_version']):
        raise IntegrityError('retained resource unit does not join its measurement window or source variant')
    manifest = resource.get('source_manifest')
    if type(manifest) is not dict:
        raise IntegrityError('retained resource unit lost its source_manifest')
    measured_manifest = measured.get('source_manifest')
    if measured_manifest is not None and measured_manifest != manifest:
        raise IntegrityError('resource source_manifest differs from the retained measurement source_manifest')
    if type(measured.get('known_at_ns')) is not int or type(measured.get('event_end_ns')) is not int:
        raise IntegrityError('retained measurement lost its source latency')
    delay = measured['known_at_ns'] - measured['event_end_ns']
    if type(delay) is not int or not 0 <= delay <= 1_000_000_000:
        raise IntegrityError('retained measurement lost its source latency')
    if manifest.get('event_latency_scenario_ns') != delay:
        raise IntegrityError('source_manifest event_latency_scenario_ns does not equal known_at-end')
    if (manifest.get('start_ns') != unit['event_start_ns']
            or manifest.get('end_ns') != unit['event_end_ns']):
        raise IntegrityError('source_manifest window does not join the retained unit')
    counts = resource.get('counts')
    projection = (manifest.get('projection') or {}).get('counts')
    if type(counts) is not dict or counts != projection:
        raise IntegrityError('resource counts do not join the source-manifest projection')
    if (type(measured.get('coordinate_manifest_version')) is not str
            or not measured['coordinate_manifest_version']):
        raise IntegrityError('measurement lost its coordinate manifest version')
    instruments = measured.get('instruments')
    quality = resource.get('instrument_quality')
    if type(instruments) is not list or type(quality) is not list or len(instruments) != len(quality):
        raise IntegrityError('resource instruments do not join the retained measurement population')
    for instrument, row in zip(instruments, quality, strict=True):
        coordinate = instrument.get('coordinate') or {}
        declared = row.get('coordinate') or {}
        if (instrument.get('instrument_id') != row.get('instrument_id')
                or coordinate.get('complete') != declared.get('complete')
                or coordinate.get('contract_key') != declared.get('contract_key')
                or ('source_versions' in coordinate and 'source_versions' in declared
                    and coordinate['source_versions'] != declared['source_versions'])):
            raise IntegrityError('instrument or coordinate identity does not join the retained resource quality')
    measurement = _require_reference(resource.get('measurement'), name='retained measurement')
    trades = (resource.get('event_storage') or {}).get('trades')
    if type(trades) is not dict or trades.get('roundtrip_exact') is not True:
        raise IntegrityError('retained resource unit lost its verified trade-cache series')
    prior_anchor = resource.get('actual_anchor_composition_check')
    prior_cohort = resource.get('actual_cohort_validation')
    if (type(prior_anchor) is not dict or prior_anchor.get('passed') is not True
            or type(prior_cohort) is not dict or prior_cohort.get('passed') is not True):
        raise IntegrityError('retained resource unit lacks its accepted anchor and cohort results')
    return {
        'unit': unit, 'delay': delay, 'measurement': measurement, 'trades': trades,
        'prior_anchor': _require_reference(prior_anchor.get('reference'), name='retained anchor result'),
        'prior_cohort': _require_reference(prior_cohort.get('reference'), name='retained cohort result'),
        'source_variant': unit['source_variant'],
    }


def payload_for_comparison(payload, *, kind):
    if type(payload) is not dict:
        raise IntegrityError(f'complete {kind} consumer payload is not an object')
    if kind == 'anchor':
        return {key: value for key, value in payload.items() if key != 'cpu_components_disjoint'}
    return payload


def compare_complete_payloads(current, previous, *, kind):
    """Full semantic equality; anchors omit only cpu_components_disjoint."""
    current_payload = payload_for_comparison(current, kind=kind)
    previous_payload = payload_for_comparison(previous, kind=kind)
    current_sha, previous_sha = digest(current_payload), digest(previous_payload)
    if current_sha != previous_sha:
        raise IntegrityError(f'{kind} consumer result differs from the retained accepted payload')
    return {
        'kind': kind, 'passed': True, 'current_semantic_sha256': current_sha,
        'previous_semantic_sha256': previous_sha, 'complete_payloads_compared': 1,
    }


def _process_unit(resource, reference, *, calendar, outputs, contract, cpu):
    started = time.process_time()
    measurement = _require_reference(resource.get('measurement'), name='retained measurement')
    measured = read_json_artifact(measurement)
    joined = join_resource_identity(resource, measured)
    started = _acc(cpu, 'measurement_authentication_and_source_join', started)
    anchor = check_anchor_unit(
        measured, joined['unit'], measurement_reference=resource['measurement'],
        trade_storage=resource['event_storage']['trades'], calendar=calendar, outputs=outputs)
    started = _acc(cpu, 'anchor_profile_recalculation', started)
    cohort = check_cohort_unit(
        measured, joined['unit'], measurement_reference=resource['measurement'],
        trade_storage=resource['event_storage']['trades'], outputs=outputs, contract=contract)
    started = _acc(cpu, 'cohort_recalculation', started)
    if anchor.get('passed') is not True or cohort.get('passed') is not True:
        raise IntegrityError('downstream consumer recalculation failed')
    prior_anchor = read_json_artifact(joined['prior_anchor'])
    prior_cohort = read_json_artifact(joined['prior_cohort'])
    current_anchor = read_json_artifact(anchor['reference'])
    current_cohort = read_json_artifact(cohort['reference'])
    anchor_cmp = compare_complete_payloads(current_anchor, prior_anchor, kind='anchor')
    cohort_cmp = compare_complete_payloads(current_cohort, prior_cohort, kind='cohort')
    _acc(cpu, 'complete_payload_comparison', started)
    return {
        'unit': joined['unit'], 'previous_resource_unit': reference,
        'measurement_reference': resource['measurement'],
        'source_latency_ns': joined['delay'],
        'coordinate_manifest_version': measured['coordinate_manifest_version'],
        'previous_anchor_reference': joined['prior_anchor'],
        'current_anchor_reference': anchor['reference'],
        'previous_cohort_reference': joined['prior_cohort'],
        'current_cohort_reference': cohort['reference'],
        'previous_anchor_semantic_sha256': anchor_cmp['previous_semantic_sha256'],
        'current_anchor_semantic_sha256': anchor_cmp['current_semantic_sha256'],
        'previous_cohort_semantic_sha256': cohort_cmp['previous_semantic_sha256'],
        'current_cohort_semantic_sha256': cohort_cmp['current_semantic_sha256'],
        'complete_payloads_compared': (
            anchor_cmp['complete_payloads_compared'] + cohort_cmp['complete_payloads_compared']),
        'exact_whole_tape_fields_compared': sum(
            (item.get('exact_whole_tape_fields_compared') or 0)
            for item in current_anchor.get('instruments') or []),
        'rolling_actual_tape_comparisons': anchor.get('rolling_actual_tape_comparisons'),
        'exact_original_source_fields_compared': cohort.get('exact_original_source_fields_compared'),
        'exact_original_source_channels_compared': cohort.get('exact_original_source_channels_compared'),
        'atom_count': anchor.get('atom_count'),
        'atom_price_rows': anchor.get('atom_price_rows'),
        'anchor_cpu_components_disjoint': anchor.get('cpu_components_disjoint'),
        'cohort_cpu_components_disjoint': cohort.get('cpu_components_disjoint'),
        'anchor_output_bytes': anchor.get('output_bytes'),
        'cohort_output_bytes': cohort.get('output_bytes'),
        'passed': True,
    }


def run_downstream(*, protocol, outputs, load_reference, check_extension):
    """Recalculate all nine accepted windows from frozen source artifacts."""
    cpu, byte_start, entry = _cpu(), outputs.written, time.process_time()
    started = entry
    previous = load_reference(_require_reference(check_extension.get('downstream_prior_worker'),
                                                 name='downstream_prior_worker'))
    receipt = load_reference(_require_reference(check_extension.get('downstream_prior_execution'),
                                                name='downstream_prior_execution'))
    identity = join_prior_identity(previous, receipt, check_extension)
    contract = check_extension.get('cohort_validation')
    if type(contract) is not dict:
        raise IntegrityError('downstream reuse requires the unchanged cohort validation contract')
    calendar_ref = protocol.get('cash_calendar')
    if type(calendar_ref) is not dict or type(calendar_ref.get('path')) is not str:
        raise IntegrityError('downstream reuse requires the frozen registered cash calendar')
    calendar = CashCalendar(Path(calendar_ref['path']))
    started = _acc(cpu, 'prior_identity_and_resource_authentication', started)
    matches, variants, seen = [], [], {}
    for reference in identity['resource_units']:
        resource = load_reference(reference)
        started = _acc(cpu, 'prior_identity_and_resource_authentication', started)
        match = _process_unit(resource, reference, calendar=calendar, outputs=outputs,
                              contract=contract, cpu=cpu)
        key = unit_key(match['unit'])
        if key in seen:
            raise IntegrityError('duplicate retained source variant or window')
        seen[key] = match['unit']['source_variant']
        variants.append(match['unit']['source_variant'])
        matches.append(match)
        started = time.process_time()
    if len(matches) != REQUIRED_RESOURCE_UNITS:
        raise IntegrityError('downstream reuse lost a retained source-window variant')
    comparison = outputs.json(
        'accepted-source-downstream-reuse-comparison.json',
        {'kind': COMPARISON_KIND, 'passed': True, 'matches': matches,
         'prior_attempt_id': identity['attempt_id'], 'prior_trial_id': identity['trial_id'],
         'prior_outputs_modified': False, 'raw_producer_rerun': False,
         'source_producer_code_snapshot': identity['code_snapshot'],
         'source_producer_runtime_versions': identity['runtime_versions'],
         'exact_source_variants': variants,
         'current_consumer_snapshot_via_parent_receipt': True},
        kind='auction_flow_accepted_source_downstream_reuse_comparison')
    helper = time.process_time() - entry
    named = sum(cpu[name] for name in _CPU_NAMES if name != 'orchestration_and_report_assembly')
    cpu['orchestration_and_report_assembly'] = helper - named
    if cpu['orchestration_and_report_assembly'] < 0:
        raise IntegrityError('disjoint downstream helper CPU stages exceed the measured helper total')
    return {
        'version': VERSION, 'kind': KIND, 'passed': True,
        'resource_units': identity['resource_units'],
        'exact_source_variants': variants, 'units': matches,
        'complete_retained_downstream_comparison': comparison,
        'source_producer': {
            'attempt_id': identity['attempt_id'], 'trial_id': identity['trial_id'],
            'protocol_sha256': identity['protocol_sha256'],
            'code_snapshot': identity['code_snapshot'],
            'tools_snapshot': identity['tools_snapshot'],
            'runtime_versions': identity['runtime_versions'],
            'configuration': identity['configuration'],
            'worker': identity['worker'], 'execution': identity['execution'],
            'raw_producer_rerun': False,
        },
        'current_consumer_snapshot_via_parent_receipt': True,
        'frozen_accepted_input_artifacts': True,
        'raw_producer_rerun': False,
        'downstream_code_change_does_not_invalidate_accepted_source_artifacts': True,
        'cpu_components_disjoint': cpu, 'helper_cpu_seconds': helper,
        'output_bytes': outputs.written - byte_start,
        'resource_probe_only': True, 'complete_family_statistics': False,
        'annual_or_model_workload_projection_complete': False,
        'actual_model_fits': 0, 'actual_location_quality_evaluations': 0,
        'context_or_location_evaluation': False, 'f11_serving_admitted': False,
    }
