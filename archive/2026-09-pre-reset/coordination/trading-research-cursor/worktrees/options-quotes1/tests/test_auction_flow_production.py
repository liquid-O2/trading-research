import copy
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import tempfile
import unittest

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import canonical_json, digest
from trading_research.research.auction_flow_coordinates import RetainedCoordinateIndex
from trading_research.research.auction_flow_pipeline import measure_raw_window
from trading_research.research.auction_flow_production import (
    COMPLETE_SOURCE_FILES, COMPLETE_SOURCE_WINDOWS, EXTRACT_CHECK_LIMITS_KIND,
    LIMITS_KIND, PLAN_KIND, PRODUCER_IMPLEMENTATION_FILES, REDUNDANT_BACKWARD_SNAPSHOT_V1,
    WINDOW_RECEIPT_KIND, authenticate_reused_receipt, clock_kwargs,
    declared_allocation, file_chains_from_schedule, file_identity,
    producer_identity, production_parameters, production_window_identity,
    resolve_production_schedule, run_file_chain,
    validate_production_limits, validate_production_plan,
)
from trading_research.research.auction_flow_schedule import VERSION as SCHEDULE_VERSION
from trading_research.research.auction_flow_storage import BoundedOutputs, read_json_artifact
from tests.test_auction_flow_coordinates import record, manifest
from tests import test_auction_flow_data as data_fixture

DATASET = data_fixture.DATASET
from tests.test_auction_flow_quotes import raw


ROOT = Path(__file__).resolve().parents[1]
FAMILY = 'Research-Auction-Flow-acquired-MBP-v1'
PROTOCOL_SHA = 'a70b281899acf5417290846d4e94d159b713a453b1f18c0997f07e44acb014b5'


def load_runner():
    path = ROOT / 'tools/run_auction_flow_study.py'
    spec = importlib.util.spec_from_file_location('run_auction_flow_study_production', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scientific_resources():
    return {
        'cpu_budget_seconds': 192000,
        'hard_cpu_margin_seconds': 10,
        'maximum_attempts': 32,
        'maximum_derived_output_bytes': 17179869184,
        'maximum_native_array_bytes': 1024 ** 2,
        'maximum_output_file_bytes': 536870912,
        'maximum_source_day_scan_rows': 100,
        'maximum_study_output_bytes': 274877906944,
        'memory_bytes': 4294967296,
        'per_check_wall_seconds': 3600,
        'phase_cpu_seconds': {'check': 1200, 'extract': 12000},
        'supervisor_output_reserve_bytes': 16777216,
    }


def write_index_reference(directory, index):
    path = Path(directory) / 'source-index.json'
    payload = canonical_json(index) + b'\n'
    path.write_bytes(payload)
    return {'path': str(path), 'sha256': hashlib.sha256(payload).hexdigest(),
            'size_bytes': len(payload), 'kind': 'four_dataset_full_footer_index'}


def schedule_window(record, *, start, end, first=False, last=False, groups=None):
    return {
        'root': 'NQ', 'dataset': DATASET, 'source_path': record['path'],
        'source_metadata_sha256': digest(record),
        'utc_date': '1970-01-01', 'year': 1970,
        'event_start_ns': start, 'event_end_ns': end,
        'observed_file_start_ns': start, 'observed_file_end_ns': end,
        'whole_window_inside_acquired_file': True,
        'source_groups': groups or [0],
        'physical_scan_rows': 8,
        'first_window_of_physical_source': first,
        'last_window_of_physical_source': last,
        'raw_variant_policy': 'separate physical acquisition; continuous carry within the same explicit source lineage',
    }


def frozen_schedule(windows):
    return {'version': SCHEDULE_VERSION, 'windows': windows, 'source_windows': len(windows),
            'partitions': [], 'instrument_allocation_bound_established': False,
            'calendar': 'UTC extraction cuts; named economic formations remain separate',
            'independent_economic_dates': None, 'source_overlap_aliases_applied': False,
            'full_extraction_authorized_by_this_schedule': False}


def coordinates():
    return RetainedCoordinateIndex(manifest([record(0, known=0, activation=0, expiry=1000,
        instrument=1, symbol='NQH0')]), source_version='actual-retained-fixture')


def invalidation_rows():
    return [raw(0), raw(2, action='T', flags=0), raw(4, flags=132), raw(9),
            raw(20), raw(20, action='T', flags=0), raw(25, action='T', flags=0, side='A'), raw(29)]


def production_context(folder, rows=None):
    root = Path(folder)
    index = data_fixture.AuctionFlowDataTests().write(root, rows or invalidation_rows())
    record = index['datasets'][DATASET][0]
    index_ref = write_index_reference(root, index)
    protocol = {
        'family': FAMILY, 'roots': ['NQ'], 'protocol_sha256': PROTOCOL_SHA,
        'native_width_ns': 10, 'atomic_width_ns': 10,
        'resources': scientific_resources(), 'source_index': index_ref,
        'runtime_versions': {'pyarrow': 'test'}, 'python_version': 'test',
    }
    windows = [
        schedule_window(record, start=0, end=20, first=True, last=False),
        schedule_window(record, start=20, end=30, first=False, last=True),
    ]
    attempt = {'attempt_id': 'attempt-a', 'trial_id': 'trial-a',
               'family': FAMILY, 'protocol_sha256': PROTOCOL_SHA}
    registered = {'attempt-a': {'id': 'attempt-a', 'trial_id': 'trial-a',
                                'family': FAMILY, 'status': 'failed'}}
    identity = producer_identity(ROOT)
    runtime = {'numpy': 'test', 'pyarrow': 'test'}
    return {
        'root': root, 'index': index, 'record': record, 'protocol': protocol,
        'windows': windows, 'chain': file_chains_from_schedule(frozen_schedule(windows))[0],
        'attempt': attempt, 'registered': registered, 'identity': identity,
        'runtime': runtime, 'coordinates': coordinates(),
    }


class AuctionFlowProductionTests(unittest.TestCase):
    def test_adjacent_windows_use_true_first_carry_and_write_required_artifacts(self):
        calls = []
        original = measure_raw_window

        def wrapped(**kwargs):
            calls.append(kwargs.get('start_ns'))
            return original(**kwargs)

        with tempfile.TemporaryDirectory() as folder:
            ctx = production_context(folder)
            outputs = BoundedOutputs(ctx['root'] / 'out', maximum_total_bytes=4 * 1024 ** 2,
                                     maximum_file_bytes=2 * 1024 ** 2)
            import trading_research.research.auction_flow_production as production
            production.measure_raw_window = wrapped
            try:
                report = run_file_chain(
                    ctx['chain'], protocol=ctx['protocol'], index=ctx['index'],
                    coordinates=ctx['coordinates'], outputs=outputs, data_root=ctx['root'],
                    registered_attempts=ctx['registered'], producer_identity_value=ctx['identity'],
                    runtime_versions=ctx['runtime'], attempt=ctx['attempt'], latency_ns=250)
            finally:
                production.measure_raw_window = original
            self.assertTrue(report['success'])
            self.assertEqual(calls, [0, 20])
            first, second = report['windows']
            self.assertEqual(first['status'], 'completed')
            self.assertEqual(second['status'], 'completed')
            self.assertEqual(second['receipt']['initial_continuation_identity'],
                             first['receipt']['final_continuation_identity'])
            first_carry = first['continuation']
            self.assertTrue(first_carry['source']['blocked'])
            self.assertEqual(second['continuation']['source']['blocked'],
                             first_carry['source']['blocked'])
            self.assertEqual(second['continuation']['previous_continuation_sha256'],
                             first_carry['sha256'])
            quote_desc = read_json_artifact(second['receipt']['artifacts']['quotes']['replay_descriptor'])
            self.assertEqual(quote_desc['initial_continuation'], first_carry['source'])
            self.assertNotEqual(quote_desc['initial_continuation'],
                                second['continuation']['source'])
            independent = original(
                data_root=ctx['root'], index=ctx['index'], coordinates=ctx['coordinates'],
                root='NQ', start_ns=20, end_ns=30, source_paths=(ctx['record']['path'],),
                continuation=first_carry, maximum_scan_rows=100, latency_ns=250,
                atomic_width_ns=10, native_width_ns=10, maximum_native_array_bytes=1024 ** 2)
            self.assertEqual(second['counts'], independent['source_manifest']['projection']['counts'])
            self.assertEqual(second['receipt']['counts']['trades'],
                             second['event_storage']['trades']['rows'])
            self.assertEqual(second['receipt']['counts']['quote_rows'],
                             second['event_storage']['quotes']['rows'])
            self.assertTrue(first['receipt']['artifacts']['trades']['roundtrip_exact'])
            self.assertTrue(first['receipt']['artifacts']['excluded']['roundtrip_exact'])
            self.assertTrue(any(name.endswith('measurements.json.zst')
                                for name in outputs.names))
            self.assertFalse(any(name.endswith('measurements.json') and not name.endswith('.json.zst')
                                 for name in outputs.names))
            self.assertNotIn('actual-reference-prefix', ' '.join(outputs.names))
            self.assertEqual(first['receipt']['kind'], WINDOW_RECEIPT_KIND)
            self.assertIsNone(report['source_clock_policy'])
            for name in ('trades', 'excluded', 'quotes', 'measurement', 'continuation'):
                self.assertIn(name, first['receipt']['artifacts'])
            self.assertIn('replay_descriptor', first['receipt']['artifacts']['quotes'])
            self.assertFalse(first['receipt']['family_statistics_or_model_complete'])

    def test_named_snapshot_policy_keeps_production_carry_and_exact_raw_counts(self):
        rows = [raw(0), raw(2, action='T', flags=0), raw(22),
                raw(21, action='A', side='N', flags=168), raw(25, action='T', flags=0), raw(29)]
        with tempfile.TemporaryDirectory() as folder:
            ctx = production_context(folder, rows)
            outputs = BoundedOutputs(ctx['root'] / 'named-out', maximum_total_bytes=8 * 1024 ** 2,
                                     maximum_file_bytes=2 * 1024 ** 2)
            report = run_file_chain(ctx['chain'], protocol=ctx['protocol'], index=ctx['index'],
                coordinates=ctx['coordinates'], outputs=outputs, data_root=ctx['root'],
                registered_attempts=ctx['registered'], producer_identity_value=ctx['identity'],
                runtime_versions=ctx['runtime'], attempt=ctx['attempt'], latency_ns=250,
                source_clock_policy=REDUNDANT_BACKWARD_SNAPSHOT_V1)
            self.assertTrue(report['success'], report.get('failures'))
            first, second = report['windows']
            self.assertEqual(second['counts']['raw_rows'], 4)
            self.assertEqual(second['counts']['disposed_snapshot_rows'], 1)
            self.assertEqual(second['counts']['trades'], 1)
            self.assertEqual(second['continuation']['source']['next_source_order'], 6)
            descriptor = read_json_artifact(second['event_storage']['quotes']['replay_descriptor'])
            self.assertEqual(descriptor['source_clock_policy'], REDUNDANT_BACKWARD_SNAPSHOT_V1)
            self.assertEqual(descriptor['initial_continuation'], first['continuation']['source'])

    def test_explicit_compatible_producer_reuses_prefix_but_other_identity_rejects(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx = production_context(folder)
            def run(name, identity, prior=(), compatible=()):
                return run_file_chain(ctx['chain'], protocol=ctx['protocol'], index=ctx['index'],
                    coordinates=ctx['coordinates'], outputs=BoundedOutputs(ctx['root']/name,
                    maximum_total_bytes=4*1024**2, maximum_file_bytes=2*1024**2), data_root=ctx['root'],
                    registered_attempts=ctx['registered'], producer_identity_value=identity,
                    runtime_versions=ctx['runtime'], attempt=ctx['attempt'], latency_ns=250,
                    prior_receipts=prior, compatible_producer_identities=compatible)
            original = run('original', ctx['identity'])
            receipt = original['windows'][0]['receipt']
            current = {'kind': 'changed-producer-for-contract-check'}
            self.assertFalse(run('reject', current, (receipt,))['success'])
            accepted = run('compatible', current, (receipt,), (ctx['identity'],))
            self.assertTrue(accepted['success'], accepted.get('failures'))
            self.assertEqual(accepted['reused_windows'], 1)
            self.assertEqual(accepted['windows'][0]['receipt'], receipt)
            self.assertFalse(run('wrong', current, (receipt,), ({'wrong': 'producer'},))['success'])

    def test_restart_reuses_leading_window_without_recomputation(self):
        calls = []
        original = measure_raw_window

        def wrapped(**kwargs):
            calls.append(kwargs.get('start_ns'))
            return original(**kwargs)

        with tempfile.TemporaryDirectory() as folder:
            ctx = production_context(folder)
            first_out = BoundedOutputs(ctx['root'] / 'first', maximum_total_bytes=4 * 1024 ** 2,
                                       maximum_file_bytes=2 * 1024 ** 2)
            import trading_research.research.auction_flow_production as production
            production.measure_raw_window = wrapped
            try:
                first_report = run_file_chain(
                    ctx['chain'], protocol=ctx['protocol'], index=ctx['index'],
                    coordinates=ctx['coordinates'], outputs=first_out, data_root=ctx['root'],
                    registered_attempts=ctx['registered'], producer_identity_value=ctx['identity'],
                    runtime_versions=ctx['runtime'], attempt=ctx['attempt'], latency_ns=250)
                first_receipt = first_report['windows'][0]['receipt']
                first_bytes = {
                    Path(ref['path']).read_bytes()
                    for ref in first_receipt['artifacts']['trades']['files']
                }
                first_paths = {ref['path'] for ref in first_receipt['artifacts']['trades']['files']}
                measurement_path = Path(first_receipt['artifacts']['measurement']['path'])
                measurement_before = measurement_path.read_bytes()
                second_out = BoundedOutputs(ctx['root'] / 'restart', maximum_total_bytes=4 * 1024 ** 2,
                                            maximum_file_bytes=2 * 1024 ** 2)
                restart = run_file_chain(
                    ctx['chain'], protocol=ctx['protocol'], index=ctx['index'],
                    coordinates=ctx['coordinates'], outputs=second_out, data_root=ctx['root'],
                    prior_receipts=(first_receipt,), registered_attempts=ctx['registered'],
                    producer_identity_value=ctx['identity'], runtime_versions=ctx['runtime'],
                    attempt=ctx['attempt'], latency_ns=250)
            finally:
                production.measure_raw_window = original
            self.assertEqual(calls, [0, 20, 20])
            self.assertEqual(restart['windows'][0]['status'], 'reused')
            self.assertEqual(restart['windows'][1]['status'], 'completed')
            self.assertEqual(restart['reused_windows'], 1)
            self.assertEqual({ref['path'] for ref in first_receipt['artifacts']['trades']['files']},
                             first_paths)
            self.assertEqual({Path(ref['path']).read_bytes()
                              for ref in first_receipt['artifacts']['trades']['files']}, first_bytes)
            self.assertEqual(measurement_path.read_bytes(), measurement_before)
            self.assertFalse(any(name.endswith(Path(next(iter(first_paths))).name)
                                 for name in second_out.names))

    def test_tampered_and_noncontiguous_inputs_reject(self):
        with tempfile.TemporaryDirectory() as folder:
            ctx = production_context(folder)
            outputs = BoundedOutputs(ctx['root'] / 'out', maximum_total_bytes=4 * 1024 ** 2,
                                     maximum_file_bytes=2 * 1024 ** 2)
            report = run_file_chain(
                ctx['chain'], protocol=ctx['protocol'], index=ctx['index'],
                coordinates=ctx['coordinates'], outputs=outputs, data_root=ctx['root'],
                registered_attempts=ctx['registered'], producer_identity_value=ctx['identity'],
                runtime_versions=ctx['runtime'], attempt=ctx['attempt'], latency_ns=250)
            first = report['windows'][0]['receipt']
            second = report['windows'][1]['receipt']
            parameters = production_parameters(ctx['protocol'], latency_ns=250)
            kwargs = dict(window=ctx['windows'][0], chain=ctx['chain'], protocol=ctx['protocol'],
                          producer_identity_value=ctx['identity'], runtime_versions=ctx['runtime'],
                          source_clock_policy=None, parameters=parameters,
                          registered_attempts=ctx['registered'], prior_carry_identity=None)
            with self.assertRaises(IntegrityError):
                authenticate_reused_receipt({**first, 'source_clock_policy': REDUNDANT_BACKWARD_SNAPSHOT_V1}, **kwargs)
            with self.assertRaises(IntegrityError):
                authenticate_reused_receipt(first, **{**kwargs, 'registered_attempts': {}})
            changed_source = copy.deepcopy(first)
            changed_source['unit'] = {**first['unit'], 'source_path': 'other.parquet'}
            changed_source['unit_identity'] = production_window_identity(changed_source['unit'])
            with self.assertRaises(IntegrityError):
                authenticate_reused_receipt(changed_source, **kwargs)
            with self.assertRaises(IntegrityError):
                authenticate_reused_receipt(second, **{**kwargs, 'window': ctx['windows'][1],
                                                       'prior_carry_identity': None})
            with self.assertRaises(IntegrityError):
                run_file_chain(
                    ctx['chain'], protocol=ctx['protocol'], index=ctx['index'],
                    coordinates=ctx['coordinates'], outputs=outputs, data_root=ctx['root'],
                    prior_receipts=(second,), registered_attempts=ctx['registered'],
                    producer_identity_value=ctx['identity'], runtime_versions=ctx['runtime'],
                    attempt=ctx['attempt'], latency_ns=250)
            measurement = Path(first['artifacts']['measurement']['path'])
            original = measurement.read_bytes()
            measurement.write_bytes(b'tampered' + original[8:])
            try:
                with self.assertRaises(IntegrityError):
                    authenticate_reused_receipt(first, **kwargs)
            finally:
                measurement.write_bytes(original)
            quotes = Path(first['artifacts']['quotes']['replay_descriptor']['path'])
            quote_original = quotes.read_bytes()
            quotes.write_bytes(b'x' + quote_original[1:])
            try:
                with self.assertRaises(IntegrityError):
                    authenticate_reused_receipt(first, **kwargs)
            finally:
                quotes.write_bytes(quote_original)
            carry = Path(first['artifacts']['continuation']['path'])
            carry.write_bytes(b'\x00' + carry.read_bytes()[1:])
            with self.assertRaises(IntegrityError):
                authenticate_reused_receipt(first, **kwargs)

    def test_schedule_grouping_conserves_windows_and_rejects_bad_lineages(self):
        first = {'path': 'quantpad/cme__nq-continuous-futures__mbp-1/a.parquet'}
        second = {'path': 'quantpad/cme__nq-continuous-futures__mbp-1/b.parquet'}
        first['groups'] = [{'group': 0}]
        windows = [
            schedule_window({**first, 'stamp': 1}, start=0, end=10, first=True, last=False),
            schedule_window({**first, 'stamp': 1}, start=10, end=20, first=False, last=False),
            schedule_window({**first, 'stamp': 1}, start=20, end=30, first=False, last=True),
            schedule_window({**second, 'stamp': 2}, start=0, end=10, first=True, last=False),
            schedule_window({**second, 'stamp': 2}, start=10, end=20, first=False, last=True),
        ]
        # Force distinct metadata by using explicit hashes already set from digest(record).
        chains = file_chains_from_schedule(frozen_schedule(windows))
        self.assertEqual(len(chains), 2)
        self.assertEqual(sum(len(chain['windows']) for chain in chains), 5)
        self.assertEqual([len(chain['windows']) for chain in chains], [3, 2])
        self.assertEqual({window['source_path'] for chain in chains for window in chain['windows']},
                         {first['path'], second['path']})
        overlap = [windows[0], {**windows[0], 'source_metadata_sha256': 'b' * 64,
                                'first_window_of_physical_source': True,
                                'last_window_of_physical_source': True,
                                'event_start_ns': 40, 'event_end_ns': 50}]
        with self.assertRaises(IntegrityError):
            file_chains_from_schedule(frozen_schedule(overlap))
        missing = [windows[0], {**windows[1], 'event_start_ns': 40, 'event_end_ns': 50,
                                'first_window_of_physical_source': False,
                                'last_window_of_physical_source': True}]
        with self.assertRaises(IntegrityError):
            file_chains_from_schedule(frozen_schedule(missing))

    def test_allocation_and_clock_policy_fail_closed(self):
        protocol = {'family': FAMILY, 'roots': ['NQ'], 'resources': scientific_resources()}
        with self.assertRaises(ValueError):
            declared_allocation({}, 'extract')
        with self.assertRaises(ValueError):
            validate_production_limits({}, protocol, mode='extract')
        runner = load_runner()
        with self.assertRaises(ValueError):
            runner.limits(protocol, 'extract', extension={})
        limits = {
            'kind': EXTRACT_CHECK_LIMITS_KIND, 'cpu_seconds': 30, 'hard_cpu_seconds': 40,
            'wall_seconds': 60, 'memory_bytes': 4294967296,
            'maximum_output_file_bytes': 536870912, 'maximum_output_bytes': 8 * 1024 ** 2,
            'supervisor_output_reserve_bytes': 1024 ** 2,
        }
        cap = validate_production_limits(limits, protocol, mode='extract-check')
        self.assertEqual(cap['cpu_seconds'], 30)
        too_much = {**limits, 'kind': LIMITS_KIND, 'cpu_seconds': 192001, 'hard_cpu_seconds': 192011}
        with self.assertRaises(ValueError):
            validate_production_limits(too_much, protocol, mode='extract')
        self.assertEqual(clock_kwargs(None, measure_raw_window), {})
        if 'source_clock_policy' in inspect.signature(measure_raw_window).parameters:
            self.assertEqual(
                clock_kwargs(REDUNDANT_BACKWARD_SNAPSHOT_V1, measure_raw_window),
                {'source_clock_policy': REDUNDANT_BACKWARD_SNAPSHOT_V1})
        else:
            with self.assertRaises(ContractError):
                clock_kwargs(REDUNDANT_BACKWARD_SNAPSHOT_V1, measure_raw_window)
        self.assertNotIn('src/trading_research/research/auction_flow_anchors.py',
                         PRODUCER_IMPLEMENTATION_FILES)
        self.assertIn('src/trading_research/research/auction_flow_pipeline.py',
                      PRODUCER_IMPLEMENTATION_FILES)
        identity = producer_identity(ROOT)
        self.assertEqual(identity['kind'], 'auction_flow_source_producer_identity_v1')
        self.assertNotIn('src/trading_research/research/auction_flow_downstream.py', identity['files'])

    def test_plan_reservations_join_reconstructed_file_chains(self):
        first = {'path': 'quantpad/cme__nq-continuous-futures__mbp-1/a.parquet', 'stamp': 1}
        windows = [
            schedule_window(first, start=0, end=10, first=True, last=False),
            schedule_window(first, start=10, end=20, first=False, last=True),
        ]
        chains = file_chains_from_schedule(frozen_schedule(windows))
        protocol = {'roots': ['NQ'], 'resources': scientific_resources()}
        plan = {
            'kind': PLAN_KIND, 'mode': 'extract-check',
            'coordinator_reserve_bytes': 1024,
            'required_window_count': 2, 'required_file_count': 1,
            'source_clock_policy': None,
            'schedule': frozen_schedule(windows),
            'files': [{
                'root': 'NQ', 'source_path': windows[0]['source_path'],
                'source_metadata_sha256': windows[0]['source_metadata_sha256'],
                'maximum_output_bytes': 4096, 'window_count': 2,
            }],
        }
        reserved = validate_production_plan(plan, chains, protocol, mode='extract-check',
                                            available_output_bytes=8192)
        self.assertEqual(reserved['file_maximums'], [4096])
        self.assertEqual(resolve_production_schedule(plan)['source_windows'], 2)
        with self.assertRaises(ValueError):
            validate_production_plan(plan, chains, protocol, mode='extract',
                                     available_output_bytes=8192)
        self.assertEqual(COMPLETE_SOURCE_WINDOWS, 3589)
        self.assertEqual(COMPLETE_SOURCE_FILES, 167)
        self.assertEqual(file_identity(chains[0])['window_count'], 2)


class AuctionFlowProductionDispatchTests(unittest.TestCase):
    def test_extract_dispatch_and_file_child_reject_unauthenticated_parent(self):
        runner = load_runner()
        source = Path(runner.__file__).read_text() if hasattr(runner, '__file__') else (
            ROOT / 'tools/run_auction_flow_study.py').read_text()
        self.assertIn("'extract'", source)
        self.assertIn("'extract-check'", source)
        self.assertIn('--source-file', source)
        self.assertIn('BOOTSTRAP_SOFT_CPU_SECONDS', source)
        self.assertIn('FAMILY_HARD_CPU_SECONDS', source)
        identity = {
            'root': 'NQ', 'source_path': 'a.parquet', 'source_metadata_sha256': 'a' * 64,
            'event_start_ns': 1, 'event_end_ns': 2, 'source_variant': 'x',
        }
        with tempfile.TemporaryDirectory() as folder:
            registered = Path(folder) / 'packet.json'
            child = Path(folder) / 'child.json'
            registered.write_text(json.dumps({'supervisor_pid': 1, 'attempt_id': 'x', 'trial_id': 'y'}))
            child.write_text(json.dumps({
                'kind': 'auction_flow_source_file_packet_v1',
                'registered_packet_path': str(registered),
                'ordinal': 0, 'file_identity': identity, 'coordinator_pid': 999999,
                'attempt_id': 'x', 'trial_id': 'y', 'output_directory': folder,
            }))
            import os
            import subprocess
            import sys
            cli = subprocess.run(
                [sys.executable, str(ROOT / 'tools/run_auction_flow_study.py'),
                 '--source-file', str(registered), str(child)],
                capture_output=True, text=True,
                env={**os.environ, 'PYTHONHASHSEED': '0', 'OMP_NUM_THREADS': '1',
                     'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
                     'ARROW_NUM_THREADS': '1', 'NUMEXPR_NUM_THREADS': '1'})
            self.assertEqual(cli.returncode, 1)
            self.assertIn('parent identity', cli.stderr)
