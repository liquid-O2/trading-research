from dataclasses import replace
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.auction_flow_anchor_preflight import check_anchor_unit
from trading_research.research.auction_flow_anchor_tpo import AnchorTPO, BRACKET_MINUTES
from trading_research.research.auction_flow_anchor_trades import AtomicTrades
from trading_research.research.auction_flow_anchors import AuctionAnchor, MINUTE_NS
from trading_research.research.auction_flow_downstream import (
    REQUIRED_RESOURCE_UNITS, compare_complete_payloads, join_prior_identity,
    join_resource_identity, run_downstream, unit_key,
)
from trading_research.research.auction_flow_storage import BoundedOutputs, read_json_artifact
from tests.test_auction_flow_anchors import CalendarFixture, SCOPE, trade_atoms


START, END, DELAY = 0, 30, 250
VALUES = [(1, 400, 100, 'B'), (11, 404, 100, 'A'), (21, 401, 50, 'B')]
PROTOCOL_SHA = 'aa' * 32
SNAPSHOT = {'kind': 'code_snapshot', 'sha256': 'bb' * 32, 'size_bytes': 10}
TOOLS = {'kind': 'auction_flow_tools_snapshot', 'sha256': 'cc' * 32, 'size_bytes': 11}
CONFIG = {'check_extension': {'kind': 'ext', 'sha256': 'dd' * 32, 'size_bytes': 12}}
WORKER_REF = {'path': '/retained/worker.json', 'sha256': 'ee' * 32, 'size_bytes': 8,
              'kind': 'auction_flow_worker_report'}
EXECUTION_REF = {'path': '/retained/execution.json', 'sha256': 'ff' * 32, 'size_bytes': 9,
                 'kind': 'auction_flow_execution'}
CALENDAR = {'kind': 'cash_rth_calendar',
            'path': '/workspace/trading-research/configs/cash-rth-calendar-research-v1.json'}
EMPTY_TRADES = {
    'version': 'auction-flow-bounded-parquet-storage-v1', 'series': 'empty', 'rows': 0,
    'row_groups': 0, 'encoding': 'plain', 'compression': 'zstd-level-3', 'schema': None,
    'files': [], 'compared_values': 0, 'roundtrip_exact': True, 'cpu_seconds': 0.0,
    'serialized_bytes': 0,
}
MEASUREMENT_REF = {
    'kind': 'auction_flow_full_window_measurements', 'path': '/retained/measurements.json',
    'sha256': '11' * 32, 'size_bytes': 4,
}


def fixture_unit():
    return {
        'root': 'NQ', 'cash_date': '2024-01-08', 'source_path': SCOPE['source_lineage'],
        'source_metadata_version': 'fixed-fixture-clock-v1', 'source_variant': 'fixture',
        'event_start_ns': START, 'event_end_ns': END,
    }


def composition_anchor(unit, measured, instrument_id, contract_key):
    start, end, cut = measured['event_start_ns'], measured['event_end_ns'], measured['known_at_ns']
    scope = dict(root=unit['root'], instrument_id=instrument_id, contract_key=contract_key,
                 source_lineage=unit['source_path'])
    selected = AuctionAnchor(
        'registered_source_window_composition_check', 'event', spans=((start, end),),
        selection_known_at_ns=cut, source_versions=(unit['source_metadata_version'],),
        selection_evidence=digest(unit), **scope)
    return replace(selected, source_versions=tuple(sorted(set(selected.source_versions + (
        measured['coordinate_manifest_version'], unit['source_metadata_version'])))))


def tpo_literals(atoms, selected, *, end, cut, latency):
    rows = []
    for minutes in BRACKET_MINUTES:
        tpo = AnchorTPO(selected, bracket_minutes=minutes)
        for atom in atoms:
            tpo.add(atom)
        result = tpo.record(event_end_ns=end, decision_cut_ns=cut, latency_ns=latency)
        observed = tuple((row, tuple(i for i in range(len(result['bracket_schedule'])) if bits & (1 << i)))
                         for row, _, bits in result['rows'])
        rows.append({'bracket_width_ns': minutes * MINUTE_NS, 'row_bracket_incidence': observed,
                     'minimum_completed_brackets': 2})
    return rows


def fixture_measured(unit):
    _, records = trade_atoms(VALUES, (0, 10, 20, 30))
    _, whole = trade_atoms(VALUES, (0, 30))
    atomic_windows = [{'bin': index, 'trade': record} for index, record in enumerate(records)]
    measured = {
        'event_start_ns': START, 'event_end_ns': END, 'known_at_ns': END + DELAY,
        'coordinate_manifest_version': 'coord-fixture-v1', 'root': 'NQ',
        'instruments': [{
            'instrument_id': 1,
            'coordinate': {'complete': True, 'contract_key': SCOPE['contract_key']},
            'whole_window': whole[0], 'atomic_windows': atomic_windows,
            'time_at_price': {'tpo': [], 'initial_balance': {}},
        }],
    }
    selected = composition_anchor(unit, measured, 1, SCOPE['contract_key'])
    atoms = tuple(
        AtomicTrades.from_record(
            row['trade'], root=unit['root'], contract_key=SCOPE['contract_key'],
            source_lineage=unit['source_path'],
            evidence_id=digest({'measurement': MEASUREMENT_REF['sha256'],
                                'instrument_id': 1, 'atomic_bin': row['bin']}))
        for row in atomic_windows)
    measured['instruments'][0]['time_at_price']['tpo'] = tpo_literals(
        atoms, selected, end=END, cut=END + DELAY, latency=DELAY)
    return measured


def load_reference(reference):
    raw = Path(reference['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != reference['sha256'] or len(raw) != reference['size_bytes']:
        raise IntegrityError('retained reference changed')
    return json.loads(raw)


def supervisor_pair(*, success=True, worker=None, execution=None):
    previous = {
        'success': success, 'source_component_verified': True, 'attempt_id': 'attempt-1',
        'trial_id': 'trial-1', 'protocol_sha256': PROTOCOL_SHA, 'code_snapshot': SNAPSHOT,
        'tools_snapshot': TOOLS, 'configuration': CONFIG, 'runtime_versions': {'numpy': '2.3.3'},
        'actual_source_preflight': {'passed': True, 'resource_units': []},
    }
    receipt = {
        'success': success, 'within_declared_limits': True, 'worker_identity_joined': True,
        'exit_code': 0, 'attempt_id': 'attempt-1', 'trial_id': 'trial-1',
        'protocol_sha256': PROTOCOL_SHA, 'code_snapshot': SNAPSHOT, 'tools_snapshot': TOOLS,
        'configuration': CONFIG,
        'worker_report': {key: WORKER_REF[key] for key in ('kind', 'sha256', 'size_bytes')},
        'worker_report_path': WORKER_REF['path'],
    }
    if worker:
        previous.update(worker)
    receipt['worker_report'] = {'kind': 'auction_flow_worker_report', 'sha256': digest(previous),
                                'size_bytes': len(canonical_json(previous))}
    if execution:
        receipt.update(execution)
    return previous, receipt


def extension(**extra):
    payload = {
        'downstream_prior_worker': WORKER_REF, 'downstream_prior_execution': EXECUTION_REF,
        'cohort_validation': {'kind': 'auction_flow_actual_cohort_validation_contract_v1'},
        'parent_protocol_sha256': PROTOCOL_SHA,
    }
    payload.update(extra)
    return payload


def complete_anchor(unit, *, cpu=1.0):
    return {
        'version': 'auction-flow-actual-anchor-composition-check-v1', 'unit': unit,
        'passed': True, 'instruments': [{'instrument_id': 1, 'exact_whole_tape_fields_compared': 3}],
        'coordinate_exclusions': [], 'known_at_ns': unit['event_end_ns'] + DELAY,
        'cpu_components_disjoint': {'fixed_path_mass_and_tpo_updates': cpu},
        'scope': 'fixture-complete-anchor',
    }


def complete_cohort(unit):
    return {
        'version': 'auction-flow-actual-cohort-validation-v1',
        'unit': {'root': unit['root'], 'event_start_ns': unit['event_start_ns'],
                 'event_end_ns': unit['event_end_ns'], 'source_variant': unit['source_variant']},
        'passed': True, 'instruments': [], 'exact_original_source_fields_compared': 4,
    }


def retained_spec(index):
    start, end = 1_000 + index, 2_000 + index
    return {
        'root': 'NQ' if index % 2 == 0 else 'ES',
        'source_path': f'source/{index}.parquet',
        'event_start_ns': start, 'event_end_ns': end,
        'source_variant': f'var{index:02d}', 'source_metadata_version': f'meta-{index}',
    }


def write_resource(prior, spec, *, mutate=None):
    unit = dict(spec)
    delay = DELAY
    counts = {'trades': 1 + spec['event_start_ns'] % 7, 'quotes': 0}
    coordinate = {'complete': True, 'contract_key': f"{unit['root']}:TEST"}
    measured = {
        'root': unit['root'], 'event_start_ns': unit['event_start_ns'],
        'event_end_ns': unit['event_end_ns'], 'known_at_ns': unit['event_end_ns'] + delay,
        'coordinate_manifest_version': f"coord-{unit['source_variant']}",
        'instruments': [{'instrument_id': 7, 'coordinate': coordinate}],
        'source_manifest': {
            'start_ns': unit['event_start_ns'], 'end_ns': unit['event_end_ns'],
            'event_latency_scenario_ns': delay,
            'projection': {'counts': counts},
        },
    }
    if mutate is not None:
        mutate(measured, unit, counts)
    name = f"{unit['root']}-{unit['event_start_ns']}-{unit['source_variant']}"
    measurement = prior.json(f'{name}-measurements.json', measured,
                             kind='auction_flow_full_window_measurements')
    prior_anchor = prior.json_compressed(
        f'{name}-anchor-check.json.zst', complete_anchor(unit),
        kind='auction_flow_actual_anchor_composition_check')
    prior_cohort = prior.json_compressed(
        f'{name}-cohort-validation.json.zst', complete_cohort(unit),
        kind='auction_flow_actual_cohort_validation')
    resource = {
        'unit': unit, 'measurement': measurement, 'counts': counts,
        'source_manifest': measured['source_manifest'],
        'event_storage': {'trades': EMPTY_TRADES},
        'instrument_quality': [{'instrument_id': 7, 'coordinate': coordinate}],
        'actual_anchor_composition_check': {'passed': True, 'reference': prior_anchor},
        'actual_cohort_validation': {'passed': True, 'reference': prior_cohort},
    }
    return prior.json(f'{name}-resource-unit.json', resource, kind='auction_flow_source_resource_unit')


def fake_anchor(measured, unit, **kwargs):
    outputs = kwargs['outputs']
    payload = complete_anchor(unit, cpu=2.5)
    reference = outputs.json_compressed(
        f"{unit['root']}-{unit['event_start_ns']}-{unit['source_variant']}-anchor-check.json.zst",
        payload, kind='auction_flow_actual_anchor_composition_check')
    return {'reference': reference, 'passed': True,
            'cpu_components_disjoint': payload['cpu_components_disjoint'],
            'output_bytes': reference['size_bytes'], 'atom_count': 0, 'atom_price_rows': 0,
            'rolling_actual_tape_comparisons': 0}


def fake_cohort(measured, unit, **kwargs):
    outputs = kwargs['outputs']
    payload = complete_cohort(unit)
    reference = outputs.json_compressed(
        f"{unit['root']}-{unit['event_start_ns']}-{unit['source_variant']}-cohort-validation.json.zst",
        payload, kind='auction_flow_actual_cohort_validation')
    return {'reference': reference, 'passed': True, 'cpu_components_disjoint': {},
            'output_bytes': reference['size_bytes'],
            'exact_original_source_fields_compared': 4,
            'exact_original_source_channels_compared': 1}


class AuctionFlowDownstreamTests(unittest.TestCase):
    def test_cache_loaded_anchor_payloads_are_equal_after_cpu_removal(self):
        unit = fixture_unit()
        measured = fixture_measured(unit)
        loaded = json.loads(canonical_json(measured))
        self.assertIsInstance(loaded['instruments'], list)
        self.assertIsInstance(loaded['instruments'][0]['atomic_windows'], list)
        with TemporaryDirectory() as folder:
            live_out = BoundedOutputs(Path(folder) / 'live', maximum_total_bytes=8 * 1024**2,
                                      maximum_file_bytes=4 * 1024**2)
            cached_out = BoundedOutputs(Path(folder) / 'cached', maximum_total_bytes=8 * 1024**2,
                                        maximum_file_bytes=4 * 1024**2)
            live = check_anchor_unit(
                measured, unit, measurement_reference=MEASUREMENT_REF,
                trade_storage=EMPTY_TRADES, calendar=CalendarFixture(), outputs=live_out)
            cached = check_anchor_unit(
                loaded, unit, measurement_reference=MEASUREMENT_REF,
                trade_storage=EMPTY_TRADES, calendar=CalendarFixture(), outputs=cached_out)
            live_payload = read_json_artifact(live['reference'])
            cached_payload = read_json_artifact(cached['reference'])
            compared = compare_complete_payloads(cached_payload, live_payload, kind='anchor')
            self.assertEqual(compared['current_semantic_sha256'], compared['previous_semantic_sha256'])
            self.assertEqual(live['atom_count'], cached['atom_count'])
            self.assertGreater(live['atom_count'], 0)
            self.assertIn('cpu_components_disjoint', live_payload)
            self.assertIn('cpu_components_disjoint', cached_payload)

    def test_changed_semantic_complete_payload_is_rejected(self):
        base = complete_anchor(fixture_unit(), cpu=1.0)
        same_semantics = complete_anchor(fixture_unit(), cpu=9.0)
        compared = compare_complete_payloads(same_semantics, base, kind='anchor')
        self.assertEqual(compared['current_semantic_sha256'], compared['previous_semantic_sha256'])
        self.assertEqual(compared['current_semantic_sha256'],
                         digest({k: v for k, v in base.items() if k != 'cpu_components_disjoint'}))
        changed = dict(base)
        changed['known_at_ns'] = base['known_at_ns'] + 1
        with self.assertRaises(IntegrityError):
            compare_complete_payloads(changed, base, kind='anchor')
        dropped = {key: value for key, value in base.items() if key != 'known_at_ns'}
        with self.assertRaises(IntegrityError):
            compare_complete_payloads(dropped, base, kind='anchor')
        cohort = complete_cohort(fixture_unit())
        cohort_cpu = dict(cohort)
        cohort_cpu['cpu_components_disjoint'] = {'serialization': 1.0}
        with self.assertRaises(IntegrityError):
            compare_complete_payloads(cohort_cpu, cohort, kind='cohort')

    def test_failed_supervisor_receipt_is_rejected(self):
        previous, receipt = supervisor_pair(success=False)
        with self.assertRaises(IntegrityError):
            join_prior_identity(previous, receipt, extension())
        previous, receipt = supervisor_pair(execution={'exit_code': 1, 'success': False})
        with self.assertRaises(IntegrityError):
            join_prior_identity(previous, receipt, extension())
        previous, receipt = supervisor_pair(worker={'source_component_verified': False})
        with self.assertRaises(IntegrityError):
            join_prior_identity(previous, receipt, extension())

    def test_mismatched_supervisor_identity_is_rejected(self):
        cases = (
            {'execution': {'attempt_id': 'other-attempt'}},
            {'execution': {'trial_id': 'other-trial'}},
            {'execution': {'protocol_sha256': '99' * 32}},
            {'execution': {'code_snapshot': {**SNAPSHOT, 'sha256': '00' * 32}}},
            {'execution': {'tools_snapshot': {**TOOLS, 'sha256': '00' * 32}}},
            {'execution': {'configuration': {'check_extension': {'sha256': '00' * 32}}}},
            {'execution': {'worker_report': {**WORKER_REF, 'sha256': '00' * 32}}},
            {'execution': {'worker_report_path': '/retained/other-worker.json'}},
        )
        for override in cases:
            previous, receipt = supervisor_pair(**override)
            with self.assertRaises(IntegrityError):
                join_prior_identity(previous, receipt, extension())

    def test_mismatched_source_identity_is_rejected(self):
        previous, receipt = supervisor_pair()
        previous['actual_source_preflight'] = {
            'passed': True,
            'resource_units': [dict(WORKER_REF, path=f'/retained/u{index}.json')
                               for index in range(REQUIRED_RESOURCE_UNITS - 1)],
        }
        with self.assertRaises(IntegrityError):
            join_prior_identity(previous, receipt, extension())
        unit = retained_spec(0)
        measured = {
            'root': 'ES', 'event_start_ns': unit['event_start_ns'],
            'event_end_ns': unit['event_end_ns'], 'known_at_ns': unit['event_end_ns'] + DELAY,
            'coordinate_manifest_version': 'coord',
            'instruments': [{'instrument_id': 7, 'coordinate': {'complete': True, 'contract_key': 'NQ:TEST'}}],
            'source_manifest': {
                'start_ns': unit['event_start_ns'], 'end_ns': unit['event_end_ns'],
                'event_latency_scenario_ns': DELAY, 'projection': {'counts': {'trades': 1}},
            },
        }
        resource = {
            'unit': unit, 'counts': {'trades': 1}, 'source_manifest': measured['source_manifest'],
            'measurement': MEASUREMENT_REF, 'event_storage': {'trades': EMPTY_TRADES},
            'instrument_quality': [{'instrument_id': 7, 'coordinate': {
                'complete': True, 'contract_key': 'NQ:TEST'}}],
            'actual_anchor_composition_check': {'passed': True, 'reference': MEASUREMENT_REF},
            'actual_cohort_validation': {'passed': True, 'reference': MEASUREMENT_REF},
        }
        with self.assertRaises(IntegrityError):
            join_resource_identity(resource, measured)
        measured['root'] = 'NQ'
        measured['event_start_ns'] = unit['event_start_ns'] + 5
        with self.assertRaises(IntegrityError):
            join_resource_identity(resource, measured)

    def test_orchestration_reuses_nine_retained_variants_without_producer_rerun(self):
        with TemporaryDirectory() as folder:
            prior = BoundedOutputs(Path(folder) / 'prior', maximum_total_bytes=8 * 1024**2,
                                   maximum_file_bytes=4 * 1024**2)
            current = BoundedOutputs(Path(folder) / 'current', maximum_total_bytes=8 * 1024**2,
                                     maximum_file_bytes=4 * 1024**2)
            refs = [write_resource(prior, retained_spec(index)) for index in range(REQUIRED_RESOURCE_UNITS)]
            worker, execution = supervisor_pair()
            worker['actual_source_preflight'] = {'passed': True, 'resource_units': refs}
            worker_ref = prior.json('worker.json', worker, kind='auction_flow_worker_report')
            execution['worker_report'] = {'kind': 'auction_flow_worker_report', 'sha256': digest(worker),
                                          'size_bytes': len(canonical_json(worker))}
            execution['worker_report_path'] = worker_ref['path']
            execution_ref = prior.json('execution.json', execution, kind='auction_flow_execution')
            check = extension(downstream_prior_worker=worker_ref,
                              downstream_prior_execution=execution_ref)
            with patch('trading_research.research.auction_flow_downstream.check_anchor_unit',
                       side_effect=fake_anchor), \
                 patch('trading_research.research.auction_flow_downstream.check_cohort_unit',
                       side_effect=fake_cohort):
                report = run_downstream(
                    protocol={'cash_calendar': CALENDAR}, outputs=current,
                    load_reference=load_reference, check_extension=check)
            self.assertTrue(report['passed'])
            self.assertEqual(len(report['units']), REQUIRED_RESOURCE_UNITS)
            self.assertEqual(report['exact_source_variants'],
                             [retained_spec(index)['source_variant'] for index in range(9)])
            self.assertFalse(report['raw_producer_rerun'])
            self.assertTrue(report['current_consumer_snapshot_via_parent_receipt'])
            self.assertTrue(report['downstream_code_change_does_not_invalidate_accepted_source_artifacts'])
            self.assertEqual(report['source_producer']['code_snapshot'], SNAPSHOT)
            self.assertEqual(report['source_producer']['runtime_versions'], {'numpy': '2.3.3'})
            self.assertEqual(report['actual_model_fits'], 0)
            self.assertFalse(report['complete_family_statistics'])
            self.assertEqual({unit_key(row['unit']) for row in report['units']},
                             {unit_key(retained_spec(index)) for index in range(9)})
            for row in report['units']:
                self.assertEqual(row['previous_anchor_semantic_sha256'],
                                 row['current_anchor_semantic_sha256'])
                self.assertEqual(row['previous_cohort_semantic_sha256'],
                                 row['current_cohort_semantic_sha256'])
                self.assertEqual(row['complete_payloads_compared'], 2)

    def test_run_downstream_rejects_failed_supervisor_before_consumers(self):
        with TemporaryDirectory() as folder:
            prior = BoundedOutputs(Path(folder) / 'prior', maximum_total_bytes=1024**2,
                                   maximum_file_bytes=1024**2)
            current = BoundedOutputs(Path(folder) / 'current', maximum_total_bytes=1024**2,
                                     maximum_file_bytes=1024**2)
            worker, execution = supervisor_pair(success=False)
            worker_ref = prior.json('worker.json', worker, kind='auction_flow_worker_report')
            execution_ref = prior.json('execution.json', execution, kind='auction_flow_execution')
            check = extension(downstream_prior_worker=worker_ref,
                              downstream_prior_execution=execution_ref)
            with patch('trading_research.research.auction_flow_downstream.check_anchor_unit') as anchors:
                with self.assertRaises(IntegrityError):
                    run_downstream(protocol={'cash_calendar': CALENDAR}, outputs=current,
                                   load_reference=load_reference, check_extension=check)
            anchors.assert_not_called()

    def test_run_downstream_rejects_mismatched_source_window(self):
        def mutate(measured, unit, counts):
            measured['event_start_ns'] = unit['event_start_ns'] + 1

        with TemporaryDirectory() as folder:
            prior = BoundedOutputs(Path(folder) / 'prior', maximum_total_bytes=8 * 1024**2,
                                   maximum_file_bytes=4 * 1024**2)
            current = BoundedOutputs(Path(folder) / 'current', maximum_total_bytes=8 * 1024**2,
                                     maximum_file_bytes=4 * 1024**2)
            refs = [write_resource(prior, retained_spec(index),
                                   mutate=mutate if index == 0 else None)
                    for index in range(REQUIRED_RESOURCE_UNITS)]
            worker, execution = supervisor_pair()
            worker['actual_source_preflight'] = {'passed': True, 'resource_units': refs}
            worker_ref = prior.json('worker.json', worker, kind='auction_flow_worker_report')
            execution['worker_report'] = {'kind': 'auction_flow_worker_report', 'sha256': digest(worker),
                                          'size_bytes': len(canonical_json(worker))}
            execution['worker_report_path'] = worker_ref['path']
            execution_ref = prior.json('execution.json', execution, kind='auction_flow_execution')
            check = extension(downstream_prior_worker=worker_ref,
                              downstream_prior_execution=execution_ref)
            with patch('trading_research.research.auction_flow_downstream.check_anchor_unit') as anchors:
                with self.assertRaises(IntegrityError):
                    run_downstream(protocol={'cash_calendar': CALENDAR}, outputs=current,
                                   load_reference=load_reference, check_extension=check)
            anchors.assert_not_called()

    def test_orchestration_rejects_changed_semantic_payload(self):
        def changed_anchor(measured, unit, **kwargs):
            if unit['source_variant'] != 'var00':
                return fake_anchor(measured, unit, **kwargs)
            outputs = kwargs['outputs']
            payload = complete_anchor(unit, cpu=2.5)
            payload['known_at_ns'] = payload['known_at_ns'] + 1
            reference = outputs.json_compressed(
                f"{unit['root']}-{unit['event_start_ns']}-{unit['source_variant']}-anchor-check.json.zst",
                payload, kind='auction_flow_actual_anchor_composition_check')
            return {'reference': reference, 'passed': True, 'cpu_components_disjoint': payload['cpu_components_disjoint'],
                    'output_bytes': reference['size_bytes'], 'atom_count': 0, 'atom_price_rows': 0,
                    'rolling_actual_tape_comparisons': 0}

        with TemporaryDirectory() as folder:
            prior = BoundedOutputs(Path(folder) / 'prior', maximum_total_bytes=8 * 1024**2,
                                   maximum_file_bytes=4 * 1024**2)
            current = BoundedOutputs(Path(folder) / 'current', maximum_total_bytes=8 * 1024**2,
                                     maximum_file_bytes=4 * 1024**2)
            refs = [write_resource(prior, retained_spec(index)) for index in range(REQUIRED_RESOURCE_UNITS)]
            worker, execution = supervisor_pair()
            worker['actual_source_preflight'] = {'passed': True, 'resource_units': refs}
            worker_ref = prior.json('worker.json', worker, kind='auction_flow_worker_report')
            execution['worker_report'] = {'kind': 'auction_flow_worker_report', 'sha256': digest(worker),
                                          'size_bytes': len(canonical_json(worker))}
            execution['worker_report_path'] = worker_ref['path']
            execution_ref = prior.json('execution.json', execution, kind='auction_flow_execution')
            check = extension(downstream_prior_worker=worker_ref,
                              downstream_prior_execution=execution_ref)
            with patch('trading_research.research.auction_flow_downstream.check_anchor_unit',
                       side_effect=changed_anchor), \
                 patch('trading_research.research.auction_flow_downstream.check_cohort_unit',
                       side_effect=fake_cohort):
                with self.assertRaises(IntegrityError):
                    run_downstream(protocol={'cash_calendar': CALENDAR}, outputs=current,
                                   load_reference=load_reference, check_extension=check)
