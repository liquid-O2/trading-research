"""Frozen legacy/new resource limits, actual OS enforcement and durable recovery."""
from contextlib import contextmanager, redirect_stdout
from copy import deepcopy
from dataclasses import asdict
import importlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from uuid import uuid4

from tools import engineering_batch_contract as contract
from trading_research.errors import ContractError
from trading_research.operations.artifacts import ArtifactStore, canonical_json
from trading_research.operations.trials import TrialRegistry

with patch.dict(sys.modules, {'engineering_batch_contract': contract}):
    supervisor = importlib.import_module('tools.verify_engineering_batch')

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = json.loads((ROOT / 'tests/golden/e0_period_orchestration_v1.json').read_bytes())
CASES = {row['case_id']: row for row in GOLDEN['cases']}


def batch(version='v2'):
    result = deepcopy(json.loads((ROOT / 'reports/all-measurements-batch-retry-03.json').read_bytes()))
    if version == 'v2':
        result['kind'] = 'engineering_batch_contract_v2'
        result['resources'] = dict(CASES['ORCH-02']['input']['resources'])
    return result


@contextmanager
def successful_lifecycle_fixture():
    """Real retained artifacts and trial journals; no synthetic suite is executed."""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        runs = root / 'evidence/trials/shared_foundations'
        registry = TrialRegistry(root / 'evidence/trials')
        store = registry.artifacts
        shared = batch()
        shared['id'] = 'resource-terminal-fixture'
        template = shared['families'][0]
        specs, registrations = [], []
        for family in ('resource-a', 'resource-b'):
            spec = {**template, 'family': family, 'prefix': family}
            for key in ('registration_path', 'preparation_path', 'case_map_path', 'coverage_path', 'case_report_path'):
                spec[key] = f'reports/{family}-{key}.json'
            specs.append(spec)
            row = {'family': family, **dict(CASES['ORCH-02']['input']['resources'])}
            for key, relative, raw in (('protocol', f'validation/{family}.md', b'Frozen synthetic protocol.'),
                                       ('golden', f'tests/golden/{family}.json', b'{"frozen":true}')):
                destination = root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(raw)
                row[key + '_path'] = relative
                row[key] = asdict(store.put_bytes(raw, kind=key))
            registry.register_family(family, scope_ids=('V08',), protocol=row, max_attempts=3, cpu_budget_seconds=600)
            registrations.append(row)
        shared['families'] = specs
        helper = root / shared['tools']['contract_support']
        helper.parent.mkdir(parents=True, exist_ok=True)
        helper.write_bytes((ROOT / shared['tools']['contract_support']).read_bytes())
        support = store.put_bytes(helper.read_bytes(), kind='engineering_orchestration_source')
        source = store.put_bytes(Path(supervisor.__file__).read_bytes(), kind='engineering_orchestration_source')
        batch_ref = store.put_json(shared, kind='engineering_batch_contract')
        snapshot = store.put_json({'manifest': [], 'fixture': 'resource-only'}, kind='code_snapshot')
        shared_id = uuid4().hex
        assertion_ids = ['tests.synthetic.ResourceFixture.test_retained']
        configuration = {'shared_execution_id': shared_id, 'batch_id': shared['id'],
                         'batch_contract': asdict(batch_ref), 'registrations': registrations,
                         'supervisor': asdict(source), 'supervisor_path': str(Path(supervisor.__file__).resolve()),
                         'preflight': {'contract_support': asdict(support),
                                       'expected_assertion_ids': assertion_ids,
                                       'required_existing_assertion_ids': assertion_ids},
                         'worker_launch_token': uuid4().hex, **contract.resource_configuration(shared)}
        for row in registrations:
            old = registry.register(name='Retained failed resource attempt', family=row['family'], stage='engineering',
                configuration={**configuration, 'shared_execution_id': 'f' * 32}, code_hash='synthetic-code',
                data_hashes={}, fold_version='no-market-fit', target_version=shared['id'])
            old_attempt = registry.start(old, cpu_reservation_seconds=180)
            registry.finish(old_attempt, status='failed', cpu_seconds=2, wall_seconds=3, peak_rss_bytes=1024,
                            reason='Pre-existing failure retained unchanged.')
            trial = registry.register(name='Retained successful resource fixture', family=row['family'], stage='engineering',
                configuration=configuration, code_hash='synthetic-code', data_hashes={}, fold_version='no-market-fit',
                target_version=shared['id'])
            registry.start(trial, cpu_reservation_seconds=180)
        identity = {'pid': 42, 'pgid': 42, 'start_ticks': 7, 'boot_id': 'synthetic-boot'}
        ack = {'pid': 42, 'pgid': 42, 'start_identity': identity,
               'result_path': str(runs / shared_id / 'result.json'),
               'worker_source': configuration['supervisor_path'],
               'worker_launch_token': configuration['worker_launch_token'],
               'resource_limits': contract.resource_configuration(shared)}
        lifecycle = {'shared_execution_id': shared_id, 'phase': 'completed',
                     'supervisor_path': configuration['supervisor_path'], 'configuration': configuration,
                     'members': supervisor.members_for(registry, shared_id), 'code_snapshot': asdict(snapshot),
                     'worker_start_identity': identity, 'worker_resource_acknowledgement': ack}
        source_store = ArtifactStore(root / 'evidence/artifacts')
        source_store.put_bytes(store.read(snapshot), kind=snapshot.kind)
        verification = source_store.put_json({'success': True, 'tests_run': 1, 'passed_assertion_ids': assertion_ids,
            'errors': [], 'failures': [], 'skipped': [], 'code_snapshot': asdict(snapshot)}, kind='verification')
        result = {'success': True, 'tests_run': 1, 'passed': 1, 'skipped': 0, 'errors': 0, 'failures': 0,
                  'report': str(source_store.path(verification)), 'artifact': asdict(verification),
                  'code_snapshot': asdict(snapshot)}
        with patch.object(supervisor, 'ROOT', root), patch.object(supervisor, 'RUNS', runs), patch.object(contract, 'ROOT', root):
            lifecycle['completion'] = supervisor.completion(lifecycle, success=True, status='succeeded',
                reason='Synthetic retained success fixture.', cpu=1, wall=2, rss=1024, result=result, returncode=0)
            path = runs / f'{shared_id}.json'
            supervisor.atomic_json(path, lifecycle)
            yield root, registry, path, lifecycle


@contextmanager
def adopted_fixture_children():
    import ctypes
    libc = ctypes.CDLL(None, use_errno=True)
    previous = ctypes.c_int()
    if libc.prctl(37, ctypes.byref(previous), 0, 0, 0) != 0:  # PR_GET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), 'Could not retain fixture subreaper state')
    supervisor.become_subreaper()
    try:
        yield
    finally:
        if libc.prctl(36, previous.value, 0, 0, 0) != 0:
            raise OSError(ctypes.get_errno(), 'Could not restore fixture subreaper state')


class EngineeringResourceContractTests(unittest.TestCase):
    def test_ORCH01_legacy_schema_and_frozen_allowance(self):
        old = batch('v1')
        self.assertEqual(contract.batch_resources(old), tuple(CASES['ORCH-01']['expected']['resource_tuple']))
        self.assertIs(contract.validate_batch(old), old)
        self.assertNotIn('resource_contract_version', contract.resource_configuration(old))
        altered = {**old, 'resources': dict(CASES['ORCH-02']['input']['resources'])}
        with self.assertRaisesRegex(ValueError, 'legacy'):
            contract.validate_batch(altered)
        registration = json.loads((ROOT / 'reports/m01-m02-m10-registration.json').read_bytes())
        self.assertEqual(registration['wall_seconds'], 240)

    def test_ORCH02_exact_new_schema_cannot_coerce_or_expand(self):
        new = batch()
        self.assertIs(contract.validate_batch(new), new)
        self.assertEqual(contract.batch_resources(new), tuple(CASES['ORCH-02']['expected']['resource_tuple']))
        for bad in CASES['ORCH-02']['expected']['invalid_wall_values']:
            with self.subTest(wall=bad), self.assertRaises(ValueError):
                contract.validate_batch({**new, 'resources': {**new['resources'], 'wall_seconds': bad}})
        for values in ({k: v for k, v in new['resources'].items() if k != 'wall_seconds'},
                       {**new['resources'], 'unbounded': True}):
            with self.assertRaises(ValueError):
                contract.validate_batch({**new, 'resources': values})
        for version in (None, True, [], 'bounded_complete_suite_v3'):
            with self.assertRaises(ValueError):
                contract.resource_preset(version)
        with self.assertRaises(ValueError):
            contract.validate_batch({**new, 'kind': 'engineering_batch_contract_v3'})

    def test_ORCH03_last_observation_strict_boundaries(self):
        vectors = CASES['ORCH-03']['input']
        old, new = (contract.resource_configuration(batch(v)) for v in ('v1', 'v2'))
        self.assertIsNone(contract.final_resource_error(*vectors['v1_pass'], old))
        self.assertIsNone(contract.final_resource_error(*vectors['v2_pass'], new))
        for values in vectors['v2_fail_vectors']:
            with self.subTest(values=values):
                self.assertTrue(contract.final_resource_error(*values, new))
        self.assertIn('wall', contract.final_resource_error(*vectors['v1_wall_failure'], old))
        for values in ((float('nan'), 1, 1), (1, float('inf'), 1), (True, 1, 1),
                       (1, True, 1), (1, 1, True), (1, 1, 1.0)):
            self.assertTrue(contract.final_resource_error(*values, new))
        changed = dict(zip(contract.CONFIGURATION_RESOURCE_FIELDS, vectors['configuration_mismatch_v1']))
        self.assertTrue(contract.final_resource_error(1, 1, 1, changed))
        self.assertTrue(contract.final_resource_error(1, 1, 1, {}))

    def test_ORCH04_registration_mismatch_is_read_only_and_baseline_is_complete(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(contract, 'ROOT', Path(directory)):
            root = Path(directory)
            registry = TrialRegistry(root / 'trials')

            def register(name, wall):
                row = {'family': name, 'scope_ids': ['V08'], 'registered_at': '2026-09-07T00:00:00Z',
                       **dict(zip(contract.REGISTRATION_RESOURCE_FIELDS, (180, 190, 4294967296, wall)))}
                for key, path, raw in (('protocol', f'validation/{name}.md', b'Frozen synthetic resource protocol.'),
                                       ('golden', f'tests/golden/{name}.json', b'{"frozen":true}')):
                    destination = root / path
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(raw)
                    row[key + '_path'] = path
                    row[key] = asdict(registry.artifacts.put_bytes(raw, kind=key))
                registry.register_family(name, scope_ids=('V08',), protocol=row, max_attempts=3, cpu_budget_seconds=600)
                return row

            new_a, new_b, old = register('new-a', 360), register('new-b', 360), register('legacy', 240)
            shared = {'kind': 'engineering_batch_contract_v2', 'resources': dict(CASES['ORCH-02']['input']['resources']),
                      'families': [{'family': 'new-a'}, {'family': 'new-b'}]}
            before = registry.history()
            contract.validate_registrations(registry, [new_a, new_b], shared)
            mixed = {**shared, 'families': [{'family': 'new-a'}, {'family': 'legacy'}]}
            with self.assertRaises(ValueError):
                contract.validate_registrations(registry, [new_a, old], mixed)
            with self.assertRaises(ContractError):
                registry.register_family('legacy', scope_ids=('V08',), protocol={**old, 'wall_seconds': 360},
                                         max_attempts=3, cpu_budget_seconds=600)
            self.assertEqual(registry.history(), before)
            self.assertEqual(registry.state()['attempts'], {})
            # The explicit E0 child preserves prior counters and unknown telemetry.
            parent = register('B03-E0-full-integration-engineering-v1', 360)
            report = root / 'reports/e0-integration-registration.json'
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_bytes(canonical_json(parent))
            deviation = root / 'reports/e0-unregistered-execution-deviation.json'
            deviation.write_bytes(canonical_json({
                'verification_disposition': {'all_private_passes_rejected': True,
                                             'failed_outcomes_retained': True},
                'resources': {'cpu_seconds': None, 'peak_rss_bytes': None}}))
            second_deviation = root / 'reports/e0-policy-account-execution-deviation-v2.json'
            second_deviation.write_bytes(deviation.read_bytes())
            prior_trial = registry.register(name='prior interrupted E0', family=parent['family'],
                stage='engineering', configuration={'bounded_control': True}, code_hash='source',
                data_hashes={'native': 'frozen'}, fold_version='fold', target_version='target')
            prior_attempt = registry.start(prior_trial, cpu_reservation_seconds=180)
            registry.finish(prior_attempt, status='interrupted', cpu_seconds=None,
                wall_seconds=None, peak_rss_bytes=None, reason='unknown worker resources retained')
            prior_state = deepcopy(registry.state())
            amendment = {'schema': 'engineering_budget_amendment_v1', 'id': 'bounded-e0-extension',
                'parent_family': parent['family'], 'additional_family': 'B03-E0-full-integration-engineering-amendment-v1',
                'parent_registration': contract.local_identity('reports/e0-integration-registration.json'),
                'deviation_records': [contract.local_identity('reports/e0-unregistered-execution-deviation.json'),
                                      contract.local_identity('reports/e0-policy-account-execution-deviation-v2.json')],
                'additional_attempts': 1, 'additional_cpu_budget_seconds': 180,
                'resources': dict(zip(contract.REGISTRATION_RESOURCE_FIELDS, (180,190,4294967296,360))),
                'prior_attempts_reset': False, 'prior_private_passes_accepted': False,
                'prior_unobserved_resources': 'unknown_not_reconstructed', 'parent_budget_available': False,
                'research_scope_changed': False, 'economic_evidence': False,
                'reason': 'one explicit bounded repair validation',
                'authorization_basis': 'synthetic registered control', 'declared_at': '2026-09-07T00:00:00Z'}

            def child_for(value):
                ref = registry.artifacts.put_json(value, kind='engineering_budget_amendment')
                return {**parent, 'family': value['additional_family'], 'budget_amendment': asdict(ref)}

            child = child_for(amendment)
            self.assertEqual(contract.registration_budget(registry, child), (1, 180))
            self.assertEqual(contract.registration_budget(registry, child,
                amendment_bytes=canonical_json(amendment)), (1, 180))
            with self.assertRaises(ValueError):
                contract.registration_budget(registry, child,
                    amendment_bytes=canonical_json(amendment) + b' ')
            for key, value in (('additional_attempts', 2), ('additional_cpu_budget_seconds', 181),
                               ('prior_attempts_reset', True), ('prior_private_passes_accepted', True),
                               ('parent_budget_available', True), ('research_scope_changed', True),
                               ('parent_family', 'M01-original-budget'),
                               ('prior_unobserved_resources', 'reconstructed_zero')):
                with self.subTest(amendment_field=key), self.assertRaises(ValueError):
                    contract.registration_budget(registry, child_for({**amendment, key: value}))
            with self.assertRaises(ValueError):
                contract.registration_budget(registry, {**child, 'wall_seconds': 240})
            saved_deviation = deviation.read_bytes()
            deviation.write_bytes(saved_deviation + b' ')
            with self.assertRaises(ValueError):
                contract.registration_budget(registry, child)
            deviation.write_bytes(saved_deviation)
            alias = root / 'reports/deviation-alias.json'
            alias.symlink_to(deviation)
            with self.assertRaises(ValueError):
                contract.package_path('reports/deviation-alias.json')
            self.assertEqual(registry.state(), prior_state)
            with patch.dict(sys.modules, {'engineering_batch_contract': contract}), patch.object(contract, 'ROOT', ROOT):
                amend_tool = importlib.import_module('tools.amend_engineering_budget')
            amendment_file = root / 'reports/explicit-e0-amendment.json'
            amendment_file.write_bytes(canonical_json(amendment))
            destination = root / 'reports/explicit-e0-child-registration.json'

            def invoke_amendment(source_path, output_path):
                with patch.object(amend_tool, 'ROOT', root), patch.object(
                        amend_tool, 'TrialRegistry', return_value=registry), patch.object(
                        sys, 'argv', ['amend_engineering_budget.py', source_path, output_path]), redirect_stdout(io.StringIO()):
                    amend_tool.main()

            def retained_bytes():
                return {str(path.relative_to(registry.root)): path.read_bytes()
                        for path in registry.root.rglob('*') if path.is_file()}

            clean_bytes = retained_bytes()
            invalid_file = root / 'reports/invalid-e0-amendment.json'
            invalid_file.write_bytes(canonical_json({**amendment, 'additional_attempts': 2}))
            directory_destination = root / 'reports/directory-destination'
            directory_destination.mkdir()
            amendment_alias = root / 'reports/amendment-alias.json'
            amendment_alias.symlink_to(amendment_file)
            oversized_metadata = root / 'reports/oversized-amendment.json'
            with oversized_metadata.open('wb') as stream:
                stream.truncate(1024 ** 2 + 1)
            with patch.object(contract.os, 'fdopen') as metadata_stream:
                with self.assertRaises(ValueError):
                    contract.bounded_metadata_bytes(oversized_metadata)
                metadata_stream.assert_not_called()
            for source_path, output_path in (
                    ('reports/invalid-e0-amendment.json', 'reports/explicit-e0-child-registration.json'),
                    ('reports/explicit-e0-amendment.json', 'reports/directory-destination'),
                    ('reports/amendment-alias.json', 'reports/explicit-e0-child-registration.json'),
                    ('reports/explicit-e0-amendment.json', 'reports/e0-integration-registration.json')):
                with self.subTest(amendment_main=(source_path, output_path)), self.assertRaises(ValueError):
                    invoke_amendment(source_path, output_path)
                self.assertEqual(retained_bytes(), clean_bytes)
                self.assertEqual(registry.state(), prior_state)
                self.assertFalse(destination.exists())
            registry.register_family(child['family'], scope_ids=('V08',), protocol=child,
                                     max_attempts=1, cpu_budget_seconds=180)
            extended_history = registry.history()
            registry.register_family(child['family'], scope_ids=('V08',), protocol=child,
                                     max_attempts=1, cpu_budget_seconds=180)
            self.assertEqual(registry.history(), extended_history)
            invoke_amendment('reports/explicit-e0-amendment.json', 'reports/explicit-e0-child-registration.json')
            published = destination.read_bytes()
            after_publication = retained_bytes()
            invoke_amendment('reports/explicit-e0-amendment.json', 'reports/explicit-e0-child-registration.json')
            self.assertEqual(destination.read_bytes(), published)
            self.assertEqual(retained_bytes(), after_publication)
            self.assertEqual(registry.history(), extended_history)
            contract.validate_registrations(registry, [child],
                {**shared, 'families': [{'family': child['family']}]})
            with self.assertRaises(ValueError):
                contract.validate_registrations(registry, [parent],
                    {**shared, 'families': [{'family': parent['family']}]})
            with self.assertRaises(ValueError):
                contract.registration_budget(registry, child_for({**amendment,
                    'additional_family': 'B03-E0-second-child-v1'}))
            with self.assertRaises(ValueError):
                contract.registration_budget(registry, child_for({**amendment,
                    'parent_family': child['family'], 'additional_family': 'B03-E0-grandchild-v1'}))
            final_state = registry.state()
            self.assertEqual(final_state['attempts'], prior_state['attempts'])
            self.assertEqual(final_state['trials'], prior_state['trials'])
            for name, original_family in prior_state['families'].items():
                self.assertEqual(final_state['families'][name], original_family)
            retained = final_state['attempts'][prior_attempt]
            self.assertEqual(retained['cpu_seconds'], 180)
            self.assertEqual(retained['resource_basis'], 'reservation_charged_usage_unknown')
            self.assertIsNone(retained['peak_rss_bytes'])
            self.assertIsNone(retained['wall_seconds'])
            self.assertEqual(contract.registration_budget(registry, old), (3, 600))
            self.assertEqual(registry.history(), extended_history)
            child_trial = registry.register(name='one bounded child control', family=child['family'],
                stage='engineering', configuration={'bounded_control': True}, code_hash='source',
                data_hashes={'native': 'frozen'}, fold_version='fold', target_version='target')
            child_attempt = registry.start(child_trial, cpu_reservation_seconds=180)
            registry.finish(child_attempt, status='interrupted', cpu_seconds=None,
                wall_seconds=None, peak_rss_bytes=None, reason='child reservation exhausted without observed usage')
            exhausted_history = registry.history()
            with self.assertRaises(ContractError):
                registry.start(child_trial, cpu_reservation_seconds=180)
            self.assertEqual(registry.history(), exhausted_history)
            self.assertEqual(registry.state()['attempts'][prior_attempt], prior_state['attempts'][prior_attempt])
            result_ref = json.loads((ROOT / 'reports/all-measurements-location-label-decision-v1-verification-06e92f8701ad.json').read_bytes())['verification']['artifact']
            from trading_research.operations.artifacts import artifact_ref
            source = ArtifactStore(ROOT / 'evidence/artifacts')
            result = source.read_json(artifact_ref(result_ref))
            valid = registry.artifacts.put_json(result, kind='verification')
            ids = contract.baseline_assertions(registry.artifacts, {'baseline_verification': asdict(valid)})
            self.assertEqual(len(ids), CASES['ORCH-06']['input']['complete_baseline_count'])
            for defective in ({**result, 'passed_assertion_ids': ids[:-1]},
                              {**result, 'passed_assertion_ids': [*ids[:-1], ids[0]]}):
                ref = registry.artifacts.put_json(defective, kind='verification')
                with self.assertRaises(ValueError):
                    contract.baseline_assertions(registry.artifacts, {'baseline_verification': asdict(ref)})

    def test_ORCH05_worker_applies_real_limits_and_rejects_invalid_launch(self):
        code = '''import json,resource,signal,sys
from verify_engineering_batch import configure_worker_resources
limits=json.loads(sys.argv[1])
enforced=configure_worker_resources(limits)
print(json.dumps({'limits':enforced,'cpu':resource.getrlimit(resource.RLIMIT_CPU),
                  'as':resource.getrlimit(resource.RLIMIT_AS),'alarm':signal.alarm(0)}))
'''
        environment = {**os.environ, 'PYTHONPATH': os.pathsep.join((str(ROOT / 'src'), str(ROOT / 'tools')))}
        for version, expected_alarm in (('v1', 240), ('v2', 360)):
            limits = contract.resource_configuration(batch(version))
            run = subprocess.run([sys.executable, '-c', code, canonical_json(limits).decode()], cwd=ROOT,
                                 env=environment, capture_output=True, text=True, timeout=15, check=True)
            output = json.loads(run.stdout)
            self.assertEqual(output['limits'], limits)
            self.assertEqual(output['cpu'], CASES['ORCH-05']['expected']['actual_subprocess_rlimit_cpu'])
            self.assertEqual(output['as'], CASES['ORCH-05']['expected']['actual_subprocess_rlimit_as'])
            self.assertEqual(output['alarm'], expected_alarm)
            for values in CASES['ORCH-05']['input']['invalid_values']:
                invalid = {**limits, **dict(zip(contract.CONFIGURATION_RESOURCE_FIELDS, values))}
                bad = subprocess.run([sys.executable, '-c', code, canonical_json(invalid).decode()], cwd=ROOT,
                                     env=environment, capture_output=True, text=True, timeout=15)
                self.assertNotEqual(bad.returncode, 0)
                self.assertEqual(bad.stdout, '')
                self.assertIn('ValueError', bad.stderr)

    def test_ORCH06_binding_and_same_lifecycle_recovery(self):
        shared = batch()
        limits = contract.resource_configuration(shared)
        acknowledgement = {'resource_limits': limits}
        self.assertEqual(contract.validate_resource_binding(shared, limits, acknowledgement), limits)
        for ack in (None, {}, {'resource_limits': contract.resource_configuration(batch('v1'))}):
            with self.assertRaises(ValueError):
                contract.validate_resource_binding(shared, limits, ack)
        for bad_limits in ({**limits, 'wall_limit_seconds': 360.0},
                           {**limits, 'cpu_reservation_seconds': 180.0},
                           {**limits, 'extra': 1},
                           {k: v for k, v in limits.items() if k != 'resource_contract_version'}):
            with self.assertRaises(ValueError):
                contract.validate_resource_binding(shared, limits, {'resource_limits': bad_limits})
        with self.assertRaises(ValueError):
            contract.validate_resource_binding(shared, contract.resource_configuration(batch('v1')), acknowledgement)
        target = '/tmp/e0-resource-recovery-result.json'
        args = supervisor.worker_arguments(target, limits)
        self.assertEqual(json.loads(args[-1]), limits)
        self.assertEqual(supervisor.worker_arguments(target, contract.resource_configuration(batch('v1')))[-1], target)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            runs = root / 'shared'
            registry = TrialRegistry(root / 'evidence/trials')
            spec = shared['families'][0]
            shared = {**shared, 'id': 'synthetic-resource-recovery', 'families': [{**spec, 'family': 'recovery-new'}]}
            helper = root / shared['tools']['contract_support']
            helper.parent.mkdir(parents=True, exist_ok=True)
            helper.write_bytes((ROOT / shared['tools']['contract_support']).read_bytes())
            support_ref = registry.artifacts.put_bytes(helper.read_bytes(), kind='engineering_orchestration_source')
            supervisor_ref = registry.artifacts.put_bytes(Path(supervisor.__file__).read_bytes(), kind='engineering_orchestration_source')
            batch_ref = registry.artifacts.put_json(shared, kind='engineering_batch_contract')
            registration = {'family': 'recovery-new'}
            registry.register_family('recovery-new', scope_ids=('V08',), protocol=registration, max_attempts=3, cpu_budget_seconds=600)
            shared_id = '6' * 32
            config = {'shared_execution_id': shared_id, 'batch_id': shared['id'], 'batch_contract': asdict(batch_ref),
                      'registrations': [registration], 'supervisor': asdict(supervisor_ref),
                      'supervisor_path': str(Path(supervisor.__file__).resolve()),
                      'preflight': {'contract_support': asdict(support_ref)}, **limits}
            trial = registry.register(name='Interrupted before worker launch', family='recovery-new', stage='engineering',
                                      configuration=config, code_hash='synthetic-code', data_hashes={}, fold_version='no-market-fit',
                                      target_version=shared['id'])
            attempt = registry.start(trial, cpu_reservation_seconds=180)
            lifecycle = {'shared_execution_id': shared_id, 'supervisor_path': config['supervisor_path'],
                         'phase': 'launch_pending', 'configuration': config, 'code_snapshot': {'synthetic': True},
                         'members': [{'family': 'recovery-new', 'trial_id': trial, 'attempt_id': attempt}]}
            with patch.object(supervisor, 'ROOT', root), patch.object(supervisor, 'RUNS', runs), patch.object(contract, 'ROOT', root):
                supervisor.atomic_json(runs / f'{shared_id}.json', lifecycle)
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(supervisor.recover(registry, shared_id), 1)
                terminal = registry.state()['attempts'][attempt]
                self.assertEqual(terminal['status'], 'interrupted')
                self.assertEqual(terminal['cpu_seconds'], 180)
                self.assertEqual(terminal['resource_basis'], 'reservation_charged_usage_unknown')
                history = registry.history()
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(supervisor.recover(registry, shared_id), 1)
                self.assertEqual(registry.history(), history)
                self.assertEqual(len(registry.state()['attempts']), 1)
                self.assertFalse((runs / shared_id / 'worker-started.json').exists())

        # Finalization is exercised against real immutable artifacts and two
        # family journals, including an interrupted partial publication.
        with successful_lifecycle_fixture() as (root, registry, path, lifecycle):
            original_events = {p: p.read_bytes() for p in (registry.root / 'events').glob('*.json')}
            members = lifecycle['members']
            finish = registry.finish

            def fail_second(attempt_id, **kwargs):
                if attempt_id == members[1]['attempt_id']:
                    raise OSError('Synthetic interruption after first family commit')
                return finish(attempt_id, **kwargs)

            with patch.object(registry, 'finish', side_effect=fail_second), redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(RuntimeError, 'completion is durable'):
                    supervisor.finalize(registry, path, lifecycle)
            self.assertEqual(registry.state()['attempts'][members[0]['attempt_id']]['status'], 'succeeded')
            self.assertEqual(registry.state()['attempts'][members[1]['attempt_id']]['status'], 'running')
            with redirect_stdout(io.StringIO()):
                self.assertEqual(supervisor.recover(registry, lifecycle['shared_execution_id']), 0)
            history = registry.history()
            with redirect_stdout(io.StringIO()):
                self.assertEqual(supervisor.recover(registry, lifecycle['shared_execution_id']), 0)
            self.assertEqual(registry.history(), history)
            for member in members:
                attempt = registry.state()['attempts'][member['attempt_id']]
                self.assertEqual((attempt['status'], attempt['cpu_seconds'], attempt['wall_seconds']), ('succeeded', 1, 2))
            final = json.loads(path.read_bytes())
            self.assertEqual(final['completion']['cpu_seconds'], 1)
            self.assertEqual(len(registry.state()['attempts']), 4)  # Two old failures, two current attempts.
            self.assertTrue(all(p.read_bytes() == raw for p, raw in original_events.items()))

        # The actual terminal and recorder entry points must reject forged
        # summaries; a helper-only assertion cannot establish this boundary.
        for defect in ('missing-result', 'missing-ack', 'float-ack', 'float-pid', 'float-start',
                       'extra-ack-key', 'forged-final', 'nonzero-exit'):
            with self.subTest(defect=defect), successful_lifecycle_fixture() as (root, registry, path, lifecycle):
                report = lifecycle['completion']
                if defect == 'missing-result':
                    report['result'] = None
                elif defect == 'missing-ack':
                    lifecycle['worker_resource_acknowledgement'] = None
                    report['worker_resource_acknowledgement'] = None
                elif defect == 'float-ack':
                    lifecycle['worker_resource_acknowledgement']['resource_limits']['wall_limit_seconds'] = 360.0
                elif defect == 'float-pid':
                    lifecycle['worker_resource_acknowledgement']['pid'] = 42.0
                elif defect == 'float-start':
                    lifecycle['worker_resource_acknowledgement']['start_identity']['start_ticks'] = 7.0
                elif defect == 'extra-ack-key':
                    lifecycle['worker_resource_acknowledgement']['unregistered'] = True
                elif defect == 'forged-final':
                    report['configuration'] = {**report['configuration'], 'wall_limit_seconds': 240}
                    report['configuration'].pop('resource_contract_version')
                else:
                    report['worker_exit_code'] = 1
                forged_ref = registry.artifacts.put_json(report, kind='supervised_engineering_verification')
                summary = {key: report[key] for key in ('success', 'shared_execution_id', 'members', 'reason',
                                                        'cpu_seconds', 'wall_seconds', 'peak_rss_bytes')}
                summary.update(artifact=asdict(forged_ref), verification=report['result'])
                summary_path = root / 'forged-summary.json'
                supervisor.atomic_json(summary_path, summary)
                with patch.dict(sys.modules, {'engineering_batch_contract': contract, 'verify_engineering_batch': supervisor}):
                    recorder = importlib.import_module('tools.record_engineering_batch')
                history = registry.history()
                with patch.object(recorder, 'ROOT', root), patch.object(sys, 'argv', ['recorder', str(summary_path)]):
                    with self.assertRaises(ValueError):
                        recorder.main()
                self.assertEqual(registry.history(), history)
                self.assertFalse(list((root / 'evidence/events').glob('*.json')))
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(supervisor.finalize(registry, path, lifecycle), 1)
                for member in lifecycle['members']:
                    self.assertEqual(registry.state()['attempts'][member['attempt_id']]['status'], 'interrupted')
                self.assertIs(lifecycle['completion']['success'], False)
                self.assertIn('rejected_completion', lifecycle['completion'])

        # Real processes exist only inside the registered suite. The leader
        # exits after exec-spawning a finite child; recovery must identify the
        # inherited per-launch token and leave an unrelated session untouched.
        with successful_lifecycle_fixture() as (root, registry, path, lifecycle), adopted_fixture_children():
            lifecycle.pop('completion')
            lifecycle.pop('worker_resource_acknowledgement')
            lifecycle.pop('worker_start_identity')
            lifecycle['phase'] = 'running'
            folder = path.parent / lifecycle['shared_execution_id']
            folder.mkdir(parents=True, exist_ok=True)
            configuration = lifecycle['configuration']
            environment = {**os.environ, 'PYTHONPATH': os.pathsep.join((str(ROOT / 'src'), str(ROOT / 'tools'))),
                           supervisor.WORKER_TOKEN_ENV: configuration['worker_launch_token']}
            sentinel_environment = {k: v for k, v in environment.items() if k != supervisor.WORKER_TOKEN_ENV}
            sentinel = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(20)'],
                                        env=sentinel_environment, start_new_session=True)
            leader = None
            child_identity = None
            code = '''import json,os,subprocess,sys
from verify_engineering_batch import atomic_json,process_identity,WORKER_TOKEN_ENV
folder,source,limits=sys.argv[1:]
child=subprocess.Popen([sys.executable,'-c','import time; time.sleep(20)'])
identity=process_identity(os.getpid())
atomic_json(folder+'/child.json',process_identity(child.pid))
atomic_json(folder+'/worker-started.json',{'pid':os.getpid(),'pgid':os.getpgrp(),
 'start_identity':identity,'result_path':folder+'/result.json','worker_source':source,
 'resource_limits':json.loads(limits),'worker_launch_token':os.environ[WORKER_TOKEN_ENV]})
'''
            try:
                leader = subprocess.Popen([sys.executable, '-c', code, str(folder), configuration['supervisor_path'],
                    canonical_json(limits).decode()], env=environment, cwd=ROOT, start_new_session=True)
                self.assertEqual(leader.wait(timeout=5), 0)
                child_identity = json.loads((folder / 'child.json').read_bytes())
                self.assertTrue(supervisor.process_has_launch_token(child_identity, configuration['worker_launch_token']))
                self.assertIsNone(sentinel.poll())
                forged = deepcopy(lifecycle)
                forged['configuration']['worker_launch_token'] = uuid4().hex
                supervisor.atomic_json(path, forged)
                history = registry.history()
                with self.assertRaisesRegex(ValueError, 'immutable registered trials'):
                    supervisor.recover(registry, lifecycle['shared_execution_id'])
                self.assertEqual(registry.history(), history)
                self.assertTrue(supervisor._same_process(child_identity))
                supervisor.atomic_json(path, lifecycle)
                before_count = len(registry.state()['attempts'])
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(supervisor.recover(registry, lifecycle['shared_execution_id']), 1)
                self.assertEqual(len(registry.state()['attempts']), before_count)
                self.assertFalse(supervisor.live_groups({child_identity['pgid']}))
                self.assertIsNone(sentinel.poll())
                recovered = json.loads(path.read_bytes())
                self.assertIn(child_identity, recovered['recovery_observed_processes'])
                for member in lifecycle['members']:
                    self.assertEqual(registry.state()['attempts'][member['attempt_id']]['cpu_seconds'], 180)
                # A reused numeric PID/PGID without the retained token is not
                # positive ownership evidence and must never be signalled.
                sentinel_identity = supervisor.process_identity(sentinel.pid)
                self.assertFalse(supervisor.process_has_launch_token(sentinel_identity, configuration['worker_launch_token']))
                self.assertFalse(supervisor._same_process({**sentinel_identity, 'start_ticks': sentinel_identity['start_ticks'] + 1}))
                with successful_lifecycle_fixture() as (_, reused_registry, reused_path, reused):
                    reused.pop('completion')
                    reused.pop('worker_resource_acknowledgement')
                    reused['phase'] = 'running'
                    reused['worker_start_identity'] = {**sentinel_identity, 'start_ticks': sentinel_identity['start_ticks'] + 1}
                    supervisor.atomic_json(reused_path, reused)
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(supervisor.recover(reused_registry, reused['shared_execution_id']), 1)
                    self.assertEqual(json.loads(reused_path.read_bytes())['recovery_observed_processes'], [])
                    self.assertIsNone(sentinel.poll())
            finally:
                if leader is not None and leader.poll() is None:
                    leader.kill()
                    leader.wait(timeout=5)
                if child_identity is None and (folder / 'child.json').exists():
                    child_identity = json.loads((folder / 'child.json').read_bytes())
                if child_identity is not None and supervisor._same_process(child_identity):
                    try:
                        os.kill(child_identity['pid'], 9)
                    except ProcessLookupError:
                        pass
                if sentinel.poll() is None:
                    sentinel.kill()
                sentinel.wait(timeout=5)
                if child_identity is not None:
                    deadline = time.monotonic() + 5
                    while True:
                        try:
                            reaped, _ = os.waitpid(child_identity['pid'], os.WNOHANG)
                        except ChildProcessError:
                            break
                        if reaped:
                            break
                        if time.monotonic() >= deadline:
                            self.fail('Fixture child did not exit within its cleanup bound')
                        time.sleep(0.01)


if __name__ == '__main__':
    unittest.main()
