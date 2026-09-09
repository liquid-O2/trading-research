import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time
import unittest

from trading_research.errors import IntegrityError
from trading_research.research.auction_flow_preflight import run_measured_units, run_preflight
from trading_research.research.auction_flow_storage import BoundedOutputs


ROOT = Path(__file__).resolve().parents[1]
FAMILY = 'Research-Auction-Flow-acquired-MBP-v1'
PROTOCOL_SHA = 'a70b281899acf5417290846d4e94d159b713a453b1f18c0997f07e44acb014b5'
LITERAL_STAT = '999 (python) S 8 7 7 0 0 0 0 0 0 0 200 100 0 0 20 0 1 0 123 0 50\n'


def load_parallel():
    path = ROOT / 'tools/auction_flow_parallel.py'
    spec = importlib.util.spec_from_file_location('auction_flow_parallel', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PARALLEL = load_parallel()


def load_runner():
    path = ROOT / 'tools/run_auction_flow_study.py'
    spec = importlib.util.spec_from_file_location('run_auction_flow_study', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scientific_resources():
    return {
        'cpu_budget_seconds': 192000,
        'hard_cpu_margin_seconds': 10,
        'maximum_attempts': 32,
        'maximum_derived_output_bytes': 17179869184,
        'maximum_native_array_bytes': 2147483648,
        'maximum_output_file_bytes': 536870912,
        'maximum_raw_batch_rows': 65536,
        'maximum_source_day_scan_rows': 50000000,
        'maximum_study_output_bytes': 274877906944,
        'memory_bytes': 4294967296,
        'per_check_wall_seconds': 3600,
        'phase_cpu_seconds': {'check': 1200, 'confirm': 16000, 'extract': 12000, 'fit': 16000},
        'supervisor_output_reserve_bytes': 16777216,
    }


def hardware_allocation():
    return {
        'kind': 'auction_flow_user_hardware_execution_v1',
        'family': FAMILY,
        'parent_protocol_sha256': PROTOCOL_SHA,
        'declared_hardware': {
            'vcpus': 21, 'memory_bytes': 83000000000,
            'gpu': 'NVIDIA RTX A4000', 'vram_bytes': 16000000000,
        },
        'approval': {
            'source': 'explicit_user_instruction',
            'messages': [
                {'at': '2026-09-08T08:18:47.330996Z', 'text': 'Use the supplied hardware.'},
                {'at': '2026-09-08T08:27:26.385943Z', 'text': 'Do not use host CPU or RAM.'},
            ],
        },
        'unchanged_scientific_resources': scientific_resources(),
        'hardware_specification': {
            'path': 'validation/HARDWARE_USER_SPEC_V1.md',
            'sha256': 'f25903dccbd44f285bf875b213bfb2ac52bb39544ffff43aa78030623eaccaae',
            'size_bytes': 75,
        },
        'execution': {
            'maximum_workers': 16,
            'aggregate_memory_bytes': 68719476736,
            'coordinator_memory_bytes': 4294967296,
            'child_memory_bytes': 4294967296,
            'native_threads_per_worker': 1,
            'gpu_workers': 0,
            'maximum_child_output_bytes': 536870912,
        },
    }


def protocol_fixture():
    return {'family': FAMILY, 'resources': scientific_resources()}


def write_v1(root, *, quota, period, memory):
    root = Path(root)
    (root / 'cpu').mkdir(parents=True, exist_ok=True)
    (root / 'cpu/cpu.cfs_quota_us').write_text(f'{quota}\n')
    (root / 'cpu/cpu.cfs_period_us').write_text(f'{period}\n')
    (root / 'memory').mkdir(parents=True, exist_ok=True)
    (root / 'memory/memory.limit_in_bytes').write_text(f'{memory}\n')


def write_v2(root, *, quota, period, memory):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    quota_text = 'max' if quota is None else str(quota)
    memory_text = 'max' if memory is None else str(memory)
    (root / 'cpu.max').write_text(f'{quota_text} {period}\n')
    (root / 'memory.max').write_text(f'{memory_text}\n')


def write_stat(proc_root, pid, *, ppid=1, pgrp=1, session=1, utime=0, stime=0, rss=0):
    directory = Path(proc_root) / str(pid)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'stat').write_text(
        f'{pid} (python) S {ppid} {pgrp} {session} 0 0 0 0 0 0 0 {utime} {stime} 0 0 20 0 1 0 0 0 {rss}\n')


def fixture_job(ordinal, directory, *, delay=0.0, code=0, extra=''):
    script = (
        'import json, sys, time\n'
        'from pathlib import Path\n'
        'time.sleep(float(sys.argv[1]))\n'
        'out = Path(sys.argv[2])\n'
        'out.mkdir(parents=True, exist_ok=True)\n'
        '(out / "result.json").write_text(json.dumps({"ordinal": int(sys.argv[3])}))\n'
        f'{extra}'
        'raise SystemExit(int(sys.argv[4]))\n'
    )
    return {
        'ordinal': ordinal,
        'argv': [sys.executable, '-c', script, str(delay), str(directory), str(ordinal), str(code)],
        'output_directory': str(directory),
    }


class AuctionFlowParallelTests(unittest.TestCase):
    def test_cgroup_v1_v2_and_unlimited_use_supplied_ceilings(self):
        protocol = protocol_fixture()
        allocation = hardware_allocation()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_v1(root / 'v1', quota=1785000, period=100000, memory=82999996416)
            live = PARALLEL.live_hardware_limits(root / 'v1')
            self.assertEqual(live, {'cpu_quota_us': 1785000, 'cpu_period_us': 100000,
                                    'memory_limit_bytes': 82999996416})
            plan = PARALLEL.plan_source_unit_execution(protocol, allocation, live_limits=live,
                                                       protocol_sha256=PROTOCOL_SHA)
            self.assertEqual(plan['effective_cpu_cores'], 17)
            self.assertEqual(plan['maximum_concurrency'], 15)
            self.assertEqual(plan['allocated_address_space_bytes'], 16 * 4294967296)
            write_v2(root / 'v2', quota=1785000, period=100000, memory=82999996416)
            self.assertEqual(PARALLEL.live_hardware_limits(root / 'v2'), live)
            write_v1(root / 'v1u', quota=-1, period=100000, memory=2 ** 63 - 4096)
            unlimited = PARALLEL.live_hardware_limits(root / 'v1u')
            self.assertEqual(unlimited['cpu_quota_us'], -1)
            self.assertIsNone(unlimited['memory_limit_bytes'])
            write_v2(root / 'v2u', quota=None, period=100000, memory=None)
            self.assertEqual(PARALLEL.live_hardware_limits(root / 'v2u')['cpu_quota_us'], -1)
            self.assertIsNone(PARALLEL.live_hardware_limits(root / 'v2u')['memory_limit_bytes'])
            unbounded = PARALLEL.plan_source_unit_execution(protocol, allocation, live_limits=unlimited,
                                                            protocol_sha256=PROTOCOL_SHA)
            self.assertEqual(unbounded['effective_cpu_cores'], 21)
            self.assertEqual(unbounded['maximum_concurrency'], 15)

    def test_stricter_quota_and_memory_reduce_concurrency(self):
        protocol = protocol_fixture()
        allocation = hardware_allocation()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_v1(root / 'cpu', quota=250000, period=100000, memory=82999996416)
            plan = PARALLEL.plan_source_unit_execution(
                protocol, allocation, live_limits=PARALLEL.live_hardware_limits(root / 'cpu'),
                protocol_sha256=PROTOCOL_SHA)
            self.assertEqual(plan['effective_cpu_cores'], 2)
            self.assertEqual(plan['maximum_concurrency'], 2)
            write_v2(root / 'mem', quota=1785000, period=100000, memory=12 * 1024 ** 3)
            plan = PARALLEL.plan_source_unit_execution(
                protocol, allocation, live_limits=PARALLEL.live_hardware_limits(root / 'mem'),
                protocol_sha256=PROTOCOL_SHA)
            self.assertEqual(plan['maximum_concurrency'], 2)
            write_v1(root / 'tight', quota=1785000, period=100000, memory=5 * 1024 ** 3)
            with self.assertRaises(ValueError):
                PARALLEL.plan_source_unit_execution(
                    protocol, allocation, live_limits=PARALLEL.live_hardware_limits(root / 'tight'),
                    protocol_sha256=PROTOCOL_SHA)

    def test_zero_invalid_quota_period_and_domain_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_v1(root / 'zero', quota=0, period=100000, memory=82999996416)
            with self.assertRaises(ValueError):
                PARALLEL.live_hardware_limits(root / 'zero')
            write_v1(root / 'period', quota=1785000, period=0, memory=82999996416)
            with self.assertRaises(ValueError):
                PARALLEL.live_hardware_limits(root / 'period')
            write_v2(root / 'neg', quota=1785000, period=-1, memory=82999996416)
            with self.assertRaises(ValueError):
                PARALLEL.live_hardware_limits(root / 'neg')
            write_v1(root / 'mem', quota=1785000, period=100000, memory=0)
            with self.assertRaises(ValueError):
                PARALLEL.live_hardware_limits(root / 'mem')
            (root / 'empty').mkdir()
            with self.assertRaises(ValueError):
                PARALLEL.live_hardware_limits(root / 'empty')
            with self.assertRaises(ValueError):
                PARALLEL.live_hardware_limits(root / 'missing')
            write_v2(root / 'frac', quota=99999, period=100000, memory=82999996416)
            with self.assertRaises(ValueError):
                PARALLEL.plan_source_unit_execution(
                    protocol_fixture(), hardware_allocation(),
                    live_limits=PARALLEL.live_hardware_limits(root / 'frac'),
                    protocol_sha256=PROTOCOL_SHA)

    def test_scientific_budget_fields_stay_the_registered_literals(self):
        protocol = protocol_fixture()
        original = json.loads(json.dumps(protocol['resources']))
        live = {'cpu_quota_us': 1785000, 'cpu_period_us': 100000, 'memory_limit_bytes': 82999996416}
        plan = PARALLEL.plan_source_unit_execution(
            protocol, hardware_allocation(), live_limits=live, protocol_sha256=PROTOCOL_SHA)
        self.assertEqual(protocol['resources'], original)
        self.assertEqual(plan['check_cpu_seconds'], 1200)
        self.assertEqual(plan['hard_cpu_margin_seconds'], 10)
        self.assertEqual(plan['cpu_budget_seconds'], 192000)
        self.assertEqual(plan['maximum_attempts'], 32)
        self.assertEqual(plan['maximum_derived_output_bytes'], 17179869184)
        self.assertEqual(plan['maximum_study_output_bytes'], 274877906944)
        self.assertEqual(plan['protocol_memory_bytes'], 4294967296)
        self.assertNotEqual(plan['maximum_derived_output_bytes'],
                            17179869184 * plan['maximum_concurrency'])
        self.assertNotEqual(plan['check_cpu_seconds'], 1200 * plan['maximum_concurrency'])
        changed = protocol_fixture()
        changed['resources']['maximum_attempts'] = 64
        with self.assertRaises(ValueError):
            PARALLEL.plan_source_unit_execution(
                changed, hardware_allocation(), live_limits=live, protocol_sha256=PROTOCOL_SHA)
        wrong = hardware_allocation()
        wrong['kind'] = 'jumbo_user_hardware_execution_v1'
        with self.assertRaises(ValueError):
            PARALLEL.plan_source_unit_execution(
                protocol, wrong, live_limits=live, protocol_sha256=PROTOCOL_SHA)
        wrong = hardware_allocation()
        wrong['family'] = 'Research-Jumbo-acquired-contract-OHLC-v1'
        with self.assertRaises(ValueError):
            PARALLEL.plan_source_unit_execution(
                protocol, wrong, live_limits=live, protocol_sha256=PROTOCOL_SHA)
        wrong = hardware_allocation()
        wrong['parent_protocol_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            PARALLEL.plan_source_unit_execution(
                protocol, wrong, live_limits=live, protocol_sha256=PROTOCOL_SHA)
        source = (ROOT / 'tools/auction_flow_parallel.py').read_text()
        self.assertNotIn('os.cpu_count', source)
        self.assertNotIn('/proc/meminfo', source)

    def test_literal_proc_stat_and_aggregate_cpu_without_double_count(self):
        parsed = PARALLEL.parse_proc_stat(LITERAL_STAT)
        self.assertEqual(parsed['pid'], 999)
        self.assertEqual(parsed['ppid'], 8)
        self.assertEqual(parsed['pgrp'], 7)
        self.assertEqual(parsed['utime_ticks'], 200)
        self.assertEqual(parsed['stime_ticks'], 100)
        self.assertEqual(parsed['rss_pages'], 50)
        with tempfile.TemporaryDirectory() as folder:
            proc = Path(folder)
            write_stat(proc, 10, utime=200, stime=100, rss=50)
            write_stat(proc, 11, utime=50, stime=50, rss=20)
            live = PARALLEL.aggregate_cpu_seconds(
                coordinator_cpu_seconds=5.0, reaped_child_cpu_seconds=3.0,
                live_pids=(10, 11), proc_root=proc, clock_ticks=100)
            self.assertEqual(live, 5.0 + 3.0 + 3.0 + 1.0)
            after = PARALLEL.aggregate_cpu_seconds(
                coordinator_cpu_seconds=5.0, reaped_child_cpu_seconds=3.0 + 3.0 + 1.0,
                live_pids=(), proc_root=proc, clock_ticks=100)
            self.assertEqual(after, live)
            rss = PARALLEL.aggregate_rss_bytes(
                coordinator_pid=10, live_pids=(11,), proc_root=proc, page_size=4096)
            self.assertEqual(rss, (50 + 20) * 4096)
            self.assertNotEqual(rss, 50 * 4096)

    def test_child_ordinal_and_parent_identity_rejection(self):
        windows = [
            {'root': 'NQ', 'role': 'ordinary_pipeline_cost', 'source_path': 'a.parquet',
             'event_start_ns': 1, 'event_end_ns': 2, 'source_variant': 'aaa', 'cash_date': '2024-03-11'},
            {'root': 'ES', 'role': 'stressed_pipeline_cost', 'source_path': 'b.parquet',
             'event_start_ns': 3, 'event_end_ns': 4, 'source_variant': 'bbb', 'cash_date': '2020-03-16'},
        ]
        first = PARALLEL.unit_identity(windows[0])
        self.assertEqual(PARALLEL.require_unit_identity(windows, 0, first), windows[0])
        with self.assertRaises(ValueError):
            PARALLEL.require_unit_identity(windows, 1, first)
        with self.assertRaises(ValueError):
            PARALLEL.require_unit_identity(windows, 9, first)
        with self.assertRaises(ValueError):
            PARALLEL.require_unit_identity(windows, 0, {**first, 'source_variant': 'changed'})
        script = (
            'import os, sys\n'
            f'sys.path.insert(0, {str(ROOT / "tools")!r})\n'
            'from auction_flow_parallel import require_parent_identity\n'
            'require_parent_identity(coordinator_pid=int(sys.argv[1]), supervisor_pid=int(sys.argv[2]))\n'
        )
        ok = subprocess.run([sys.executable, '-c', script, str(os.getpid()), str(os.getppid())],
                            cwd=str(ROOT / 'tools'), capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        bad = subprocess.run([sys.executable, '-c', script, '999999', str(os.getppid())],
                             cwd=str(ROOT / 'tools'), capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn('parent identity', bad.stderr)
        runner = ROOT / 'tools/run_auction_flow_study.py'
        with tempfile.TemporaryDirectory() as folder:
            registered = Path(folder) / 'packet.json'
            child = Path(folder) / 'child.json'
            registered.write_text(json.dumps({'supervisor_pid': 1, 'attempt_id': 'x', 'trial_id': 'y'}))
            child.write_text(json.dumps({
                'kind': 'auction_flow_source_unit_packet_v1',
                'registered_packet_path': str(registered),
                'ordinal': 0, 'unit_identity': first, 'coordinator_pid': 999999,
                'attempt_id': 'x', 'trial_id': 'y', 'output_directory': folder,
            }))
            cli = subprocess.run([sys.executable, str(runner), '--source-unit', str(registered), str(child)],
                                 capture_output=True, text=True,
                                 env={**os.environ, 'PYTHONHASHSEED': '0',
                                      'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1',
                                      'MKL_NUM_THREADS': '1', 'ARROW_NUM_THREADS': '1',
                                      'NUMEXPR_NUM_THREADS': '1'})
            self.assertEqual(cli.returncode, 1)
            self.assertIn('parent identity', cli.stderr)

    def test_output_reservation_and_single_join(self):
        reserved = PARALLEL.require_output_reservation(9, 536870912, 17179869184)
        self.assertEqual(reserved, 9 * 536870912)
        self.assertLessEqual(reserved, 17179869184)
        with self.assertRaises(ValueError):
            PARALLEL.require_output_reservation(9, 536870912, 1024)
        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / 'source-unit-00'
            second = Path(folder) / 'source-unit-01'
            first.mkdir()
            second.mkdir()
            (first / 'packet.json').write_bytes(b'12345')
            (second / 'artifacts').mkdir()
            (second / 'artifacts' / 'part.bin').write_bytes(b'abcdef')
            outputs = BoundedOutputs(Path(folder) / 'out', maximum_total_bytes=1024, maximum_file_bytes=512)
            joined = PARALLEL.join_directory_bytes((first, second))
            self.assertEqual(joined, 5 + 6)
            outputs.written += joined
            self.assertEqual(outputs.written, 11)

    def test_supervisor_keeps_input_order_after_uneven_finish(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            jobs = [fixture_job(0, root / 'u0', delay=0.25),
                    fixture_job(1, root / 'u1', delay=0.02),
                    fixture_job(2, root / 'u2', delay=0.0)]
            evidence = {}
            report = PARALLEL.supervise_source_children(
                jobs, concurrency=3, cpu_soft_seconds=1200, cpu_hard_seconds=1210,
                wall_deadline_monotonic=time.monotonic() + 10,
                allocated_address_space_bytes=16 * 1024 ** 3,
                poll_seconds=0.05, evidence=evidence)
            self.assertEqual([row['ordinal'] for row in report['children']], [0, 1, 2])
            self.assertTrue(all(row['success'] for row in report['children']))
            self.assertEqual(json.loads((root / 'u0/result.json').read_text())['ordinal'], 0)
            self.assertGreaterEqual(report['pool_child_wait4_cpu_seconds'], 0.0)
            self.assertGreaterEqual(report['all_reaped_child_cpu_seconds'], 0.0)
            self.assertEqual(report['live_unreaped_cpu_seconds'], 0.0)
            self.assertEqual(report['aggregate_cpu_seconds'],
                             report['coordinator_cpu_seconds'] + report['all_reaped_child_cpu_seconds']
                             + report['live_unreaped_cpu_seconds'])
            self.assertIn('observed_aggregate_rss_bytes', report)
            self.assertIn('per_process_wait4_peak_rss_bytes', report)
            self.assertIn('allocated_address_space_bytes', report)
            self.assertGreaterEqual(report['observed_aggregate_rss_bytes'], 0)
            self.assertGreaterEqual(report['per_process_wait4_peak_rss_bytes'], 0)

    def test_failure_and_interruption_reap_every_child(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            jobs = [fixture_job(0, root / 'a', delay=2.0),
                    fixture_job(1, root / 'b', delay=0.0, code=3),
                    fixture_job(2, root / 'c', delay=2.0)]
            evidence = {}
            with self.assertRaises(ValueError):
                PARALLEL.supervise_source_children(
                    jobs, concurrency=3, cpu_soft_seconds=1200, cpu_hard_seconds=1210,
                    wall_deadline_monotonic=time.monotonic() + 10,
                    allocated_address_space_bytes=16 * 1024 ** 3,
                    poll_seconds=0.05, evidence=evidence)
            self.assertTrue(any(row['exit_code'] != 0 for row in evidence.get('children', ())))
            try:
                pid, _, _ = os.wait4(-1, os.WNOHANG)
                self.assertEqual(pid, 0)
            except ChildProcessError:
                pass
            hanging = [fixture_job(0, root / 'w', delay=8.0)]
            interrupted = {}
            with self.assertRaises(ValueError) as caught:
                PARALLEL.supervise_source_children(
                    hanging, concurrency=1, cpu_soft_seconds=1200, cpu_hard_seconds=1210,
                    wall_deadline_monotonic=time.monotonic() + 0.2,
                    allocated_address_space_bytes=16 * 1024 ** 3,
                    poll_seconds=0.05, evidence=interrupted)
            self.assertIn('wall watchdog', str(caught.exception))
            try:
                pid, _, _ = os.wait4(-1, os.WNOHANG)
                self.assertEqual(pid, 0)
            except ChildProcessError:
                pass

    def test_live_and_reaped_cpu_are_combined_once(self):
        burn = (
            'n = 0\n'
            'for i in range(400000):\n'
            '    n += i\n'
        )
        subprocess.run([sys.executable, '-c', burn], check=True)
        prior = resource.getrusage(resource.RUSAGE_CHILDREN)
        prior_cpu = prior.ru_utime + prior.ru_stime
        with tempfile.TemporaryDirectory() as folder:
            first = fixture_job(0, Path(folder) / 'one', extra=burn)
            second = fixture_job(1, Path(folder) / 'two', extra=burn)
            report = PARALLEL.supervise_source_children(
                [first, second], concurrency=2, cpu_soft_seconds=1200, cpu_hard_seconds=1210,
                wall_deadline_monotonic=time.monotonic() + 10,
                allocated_address_space_bytes=16 * 1024 ** 3, poll_seconds=0.05)
            child_wait4 = sum(row['cpu_seconds'] for row in report['children'])
            self.assertAlmostEqual(report['pool_child_wait4_cpu_seconds'], child_wait4, places=6)
            self.assertGreaterEqual(report['all_reaped_child_cpu_seconds'], prior_cpu)
            if prior_cpu > 0:
                self.assertGreater(report['all_reaped_child_cpu_seconds'], report['pool_child_wait4_cpu_seconds'])
            self.assertEqual(report['live_unreaped_cpu_seconds'], 0.0)
            self.assertEqual(report['aggregate_cpu_seconds'],
                             report['coordinator_cpu_seconds'] + report['all_reaped_child_cpu_seconds']
                             + report['live_unreaped_cpu_seconds'])
            after = PARALLEL.aggregate_cpu_seconds(
                coordinator_cpu_seconds=report['coordinator_cpu_seconds'],
                reaped_child_cpu_seconds=report['all_reaped_child_cpu_seconds'],
                live_pids=())
            self.assertEqual(after, report['aggregate_cpu_seconds'])

    def test_run_preflight_keeps_sequential_default_and_executor_order(self):
        params = inspect.signature(run_preflight).parameters
        self.assertEqual(params['unit_executor'].default, None)
        self.assertIs(params['unit_executor'].kind, inspect.Parameter.KEYWORD_ONLY)
        for name in ('protocol', 'root', 'outputs', 'load_reference', 'check_extension'):
            self.assertIn(name, params)
        windows = [
            {'root': 'NQ', 'role': 'ordinary_pipeline_cost', 'source_path': 'a',
             'event_start_ns': 1, 'event_end_ns': 2, 'source_variant': 'x'},
            {'root': 'ES', 'role': 'stressed_pipeline_cost', 'source_path': 'b',
             'event_start_ns': 3, 'event_end_ns': 4, 'source_variant': 'y'},
        ]
        finished = []
        def executor(received, **context):
            finished.extend(reversed(received))
            return ([{'unit': unit} for unit in received],
                    [{'path': f'{index}', 'kind': 'fixture'} for index, _ in enumerate(received)])
        results, refs = run_measured_units(
            windows, protocol={}, index={}, coordinates={}, outputs=None, data_root=Path('.'),
            calendar=None, unit_executor=executor)
        self.assertEqual([row['unit'] for row in results], windows)
        self.assertEqual([row['path'] for row in refs], ['0', '1'])
        self.assertEqual(finished, list(reversed(windows)))
        with self.assertRaises(IntegrityError):
            run_measured_units(
                windows, protocol={}, index={}, coordinates={}, outputs=None, data_root=Path('.'),
                calendar=None, unit_executor=lambda received, **context: ([{'unit': received[1]}], [{}]))
        with self.assertRaises(IntegrityError):
            run_measured_units(
                windows, protocol={}, index={}, coordinates={}, outputs=None, data_root=Path('.'),
                calendar=None,
                unit_executor=lambda received, **context: (
                    [{'unit': received[1]}, {'unit': received[0]}], [{}, {}]))

    def test_approval_messages_and_complete_scientific_resources(self):
        live = {'cpu_quota_us': 1785000, 'cpu_period_us': 100000, 'memory_limit_bytes': 82999996416}
        document = json.loads((ROOT / 'validation/AUCTION_FLOW_HARDWARE_EXECUTION_V1.json').read_text())
        PARALLEL.require_approval_messages(document['approval']['messages'])
        self.assertEqual(document['unchanged_scientific_resources'], scientific_resources())
        PARALLEL.plan_source_unit_execution(
            protocol_fixture(), hardware_allocation(), live_limits=live, protocol_sha256=PROTOCOL_SHA)
        strings = hardware_allocation()
        strings['approval'] = {'source': 'explicit_user_instruction',
                               'messages': ['Use the supplied hardware.']}
        with self.assertRaises(ValueError):
            PARALLEL.plan_source_unit_execution(
                protocol_fixture(), strings, live_limits=live, protocol_sha256=PROTOCOL_SHA)
        empty_text = hardware_allocation()
        empty_text['approval']['messages'] = [{'at': '2026-09-08T08:18:47.330996Z', 'text': ''}]
        with self.assertRaises(ValueError):
            PARALLEL.plan_source_unit_execution(
                protocol_fixture(), empty_text, live_limits=live, protocol_sha256=PROTOCOL_SHA)
        mismatched = hardware_allocation()
        mismatched['unchanged_scientific_resources'] = {
            **scientific_resources(), 'maximum_native_array_bytes': 1}
        with self.assertRaises(ValueError):
            PARALLEL.plan_source_unit_execution(
                protocol_fixture(), mismatched, live_limits=live, protocol_sha256=PROTOCOL_SHA)
        for declared in (None, []):
            missing = hardware_allocation()
            missing['unchanged_scientific_resources'] = declared
            with self.assertRaises(ValueError):
                PARALLEL.plan_source_unit_execution(
                    protocol_fixture(), missing, live_limits=live, protocol_sha256=PROTOCOL_SHA)

    def test_live_limit_dictionaries_reject_non_strict_integers(self):
        valid = {'cpu_quota_us': 1785000, 'cpu_period_us': 100000, 'memory_limit_bytes': 82999996416}
        self.assertEqual(PARALLEL.require_live_limits(valid), valid)
        self.assertEqual(PARALLEL.require_live_limits(
            {'cpu_quota_us': -1, 'cpu_period_us': 100000, 'memory_limit_bytes': None})['cpu_quota_us'], -1)
        for limits in (
            {'cpu_quota_us': -2, 'cpu_period_us': 100000, 'memory_limit_bytes': 82999996416},
            {'cpu_quota_us': True, 'cpu_period_us': 100000, 'memory_limit_bytes': 82999996416},
            {'cpu_quota_us': 1785000.0, 'cpu_period_us': 100000, 'memory_limit_bytes': 82999996416},
            {'cpu_quota_us': 1785000, 'cpu_period_us': 0, 'memory_limit_bytes': 82999996416},
            {'cpu_quota_us': 1785000, 'cpu_period_us': False, 'memory_limit_bytes': 82999996416},
            {'cpu_quota_us': 1785000, 'memory_limit_bytes': 82999996416},
            {'cpu_quota_us': 1785000, 'cpu_period_us': 100000},
            {'cpu_quota_us': 1785000, 'cpu_period_us': 100000, 'memory_limit_bytes': 0},
            {'cpu_quota_us': 1785000, 'cpu_period_us': 100000, 'memory_limit_bytes': True},
            {'cpu_quota_us': 1785000, 'cpu_period_us': 100000, 'memory_limit_bytes': 82999996416.0},
        ):
            with self.assertRaises(ValueError):
                PARALLEL.require_live_limits(limits)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            write_v1(root / 'neg2', quota=-2, period=100000, memory=82999996416)
            with self.assertRaises(ValueError):
                PARALLEL.live_hardware_limits(root / 'neg2')
            write_v1(root / 'bool', quota='True', period=100000, memory=82999996416)
            with self.assertRaises(ValueError):
                PARALLEL.live_hardware_limits(root / 'bool')
            write_v1(root / 'frac', quota='1785000.5', period=100000, memory=82999996416)
            with self.assertRaises(ValueError):
                PARALLEL.live_hardware_limits(root / 'frac')
            write_v2(root / 'missing-period', quota=1785000, period=100000, memory=82999996416)
            (root / 'missing-period' / 'cpu.max').write_text('1785000\n')
            with self.assertRaises(ValueError):
                PARALLEL.live_hardware_limits(root / 'missing-period')

    def test_nine_units_use_actual_concurrency_and_forty_gib(self):
        live = {'cpu_quota_us': 1785000, 'cpu_period_us': 100000, 'memory_limit_bytes': 82999996416}
        planned = PARALLEL.plan_source_unit_execution(
            protocol_fixture(), hardware_allocation(), live_limits=live, protocol_sha256=PROTOCOL_SHA)
        self.assertEqual(planned['maximum_concurrency'], 15)
        self.assertEqual(planned['allocated_address_space_bytes'], 16 * 4294967296)
        self.assertEqual(planned['aggregate_memory_ceiling_bytes'], 64 * 1024 ** 3)
        actual = PARALLEL.actual_source_unit_allocation(planned, 9)
        self.assertEqual(actual['actual_concurrency'], 9)
        self.assertEqual(actual['allocated_address_space_bytes'], 10 * 4294967296)
        self.assertEqual(actual['aggregate_memory_ceiling_bytes'], 64 * 1024 ** 3)
        self.assertEqual(actual['maximum_concurrency_ceiling'], 15)
        self.assertNotEqual(actual['allocated_address_space_bytes'], planned['allocated_address_space_bytes'])
        reduced = PARALLEL.actual_source_unit_allocation(planned, 9, concurrency_limit=2)
        self.assertEqual(reduced['actual_concurrency'], 2)
        self.assertEqual(reduced['allocated_address_space_bytes'], 3 * 4294967296)

    def test_invalid_ordinals_are_rejected_before_any_launch(self):
        with tempfile.TemporaryDirectory() as folder:
            launched = Path(folder) / 'launched'
            marker = (
                f'from pathlib import Path\nPath({str(launched)!r}).write_text("launched")\n'
            )
            jobs = [fixture_job(0, Path(folder) / 'a'),
                    fixture_job(0, Path(folder) / 'b', extra=marker)]
            jobs[1]['ordinal'] = 0
            with self.assertRaises(ValueError):
                PARALLEL.supervise_source_children(
                    jobs, concurrency=2, cpu_soft_seconds=1200, cpu_hard_seconds=1210,
                    wall_deadline_monotonic=time.monotonic() + 5,
                    allocated_address_space_bytes=16 * 1024 ** 3, poll_seconds=0.05)
            self.assertFalse(launched.exists())
            for ordinals in ([1, 2], [0, 2], [-1], [0, 1, 1]):
                bad = [fixture_job(item if item >= 0 else 0, Path(folder) / f'x{index}')
                       for index, item in enumerate(ordinals)]
                for job, item in zip(bad, ordinals):
                    job['ordinal'] = item
                with self.assertRaises(ValueError):
                    PARALLEL.require_complete_ordinals(ordinals)
                with self.assertRaises(ValueError):
                    PARALLEL.supervise_source_children(
                        bad, concurrency=1, cpu_soft_seconds=1200, cpu_hard_seconds=1210,
                        wall_deadline_monotonic=time.monotonic() + 5,
                        allocated_address_space_bytes=16 * 1024 ** 3, poll_seconds=0.05)

    def test_remaining_self_cpu_mathematical_boundaries(self):
        self.assertEqual(PARALLEL.remaining_self_cpu_rlimits(1200, 1210, 0), (1200, 1210))
        self.assertEqual(PARALLEL.remaining_self_cpu_rlimits(1200, 1210, 100), (1100, 1110))
        self.assertEqual(PARALLEL.remaining_self_cpu_rlimits(1200, 1210, 1199.0), (1, 11))
        self.assertEqual(PARALLEL.remaining_self_cpu_rlimits(1200, 1210, 0.1), (1199, 1209))
        for children in (1199.1, 1200, 1200.4, 1210, 1210.2):
            with self.assertRaises(ValueError):
                PARALLEL.remaining_self_cpu_rlimits(1200, 1210, children)
        with self.assertRaises(ValueError):
            PARALLEL.remaining_self_cpu_rlimits(1200, 1210, True)
        before = resource.getrlimit(resource.RLIMIT_CPU)
        remaining = PARALLEL.apply_remaining_coordinator_cpu_limit(
            1200, 1210, children_cpu_seconds=100, set_limit=False)
        self.assertEqual(resource.getrlimit(resource.RLIMIT_CPU), before)
        self.assertEqual(remaining[0], min(1100, before[0] if before[0] not in (-1, resource.RLIM_INFINITY) else 1100))

    def test_remaining_coordinator_cpu_enforcement_in_subprocess(self):
        script = (
            'import resource, sys\n'
            f'sys.path.insert(0, {str(ROOT / "tools")!r})\n'
            'from auction_flow_parallel import apply_remaining_coordinator_cpu_limit\n'
            'resource.setrlimit(resource.RLIMIT_CPU, (1200, 1210))\n'
            'soft, hard = apply_remaining_coordinator_cpu_limit(1200, 1210, children_cpu_seconds=100)\n'
            'assert (soft, hard) == (1100, 1110), (soft, hard)\n'
            'assert resource.getrlimit(resource.RLIMIT_CPU) == (1100, 1110)\n'
            'soft, hard = apply_remaining_coordinator_cpu_limit(1200, 1210, children_cpu_seconds=50)\n'
            'assert (soft, hard) == (1100, 1110), (soft, hard)\n'
            'try:\n'
            '    apply_remaining_coordinator_cpu_limit(1200, 1210, children_cpu_seconds=1200)\n'
            'except ValueError:\n'
            '    assert resource.getrlimit(resource.RLIMIT_CPU) == (1100, 1110)\n'
            'else:\n'
            '    raise SystemExit(2)\n'
        )
        before = resource.getrlimit(resource.RLIMIT_CPU)
        result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(resource.getrlimit(resource.RLIMIT_CPU), before)

    def test_outer_wait4_is_authoritative_and_keeps_pool_checkpoint(self):
        burn = 'n = 0\nfor i in range(350000):\n    n += i\n'
        script = (
            'import json, os, resource, sys, time\n'
            'from pathlib import Path\n'
            f'sys.path.insert(0, {str(ROOT / "tools")!r})\n'
            'from auction_flow_parallel import supervise_source_children, wait4_cpu_seconds\n'
            + burn +
            'child = (\n'
            '    "import sys, time\\n"\n'
            '    "n = 0\\n"\n'
            '    "for i in range(350000):\\n"\n'
            '    "    n += i\\n"\n'
            ')\n'
            'jobs = [{"ordinal": 0, "argv": [sys.executable, "-c", child]}]\n'
            'report = supervise_source_children(\n'
            '    jobs, concurrency=1, cpu_soft_seconds=1200, cpu_hard_seconds=1210,\n'
            '    wall_deadline_monotonic=time.monotonic() + 10,\n'
            '    allocated_address_space_bytes=16 * 1024 ** 3, poll_seconds=0.05)\n'
            + burn +
            'final_self = resource.getrusage(resource.RUSAGE_SELF)\n'
            'Path(sys.argv[1]).write_text(json.dumps({\n'
            '    "pool_aggregate_cpu_seconds": report["aggregate_cpu_seconds"],\n'
            '    "coordinator_cpu_seconds": report["coordinator_cpu_seconds"],\n'
            '    "pool_child_wait4_cpu_seconds": report["pool_child_wait4_cpu_seconds"],\n'
            '    "all_reaped_child_cpu_seconds": report["all_reaped_child_cpu_seconds"],\n'
            '    "final_self_cpu_seconds": final_self.ru_utime + final_self.ru_stime,\n'
            '}))\n'
        )
        with tempfile.TemporaryDirectory() as folder:
            evidence = Path(folder) / 'evidence.json'
            process = subprocess.Popen([sys.executable, '-c', script, str(evidence)])
            _, status, usage = os.wait4(process.pid, 0)
            process.returncode = os.waitstatus_to_exitcode(status)
            self.assertEqual(process.returncode, 0)
            final = PARALLEL.wait4_cpu_seconds(usage)
            payload = json.loads(evidence.read_text())
            self.assertGreater(payload['pool_child_wait4_cpu_seconds'], 0.0)
            self.assertGreater(final, payload['coordinator_cpu_seconds'])
            self.assertGreater(final, payload['pool_aggregate_cpu_seconds'])
            self.assertGreaterEqual(final + 1e-5,
                payload['final_self_cpu_seconds'] + payload['all_reaped_child_cpu_seconds'])
            self.assertNotEqual(final, final + payload['pool_child_wait4_cpu_seconds'])
            runner = (ROOT / 'tools/run_auction_flow_study.py').read_text()
            self.assertNotIn("cpu = parallel['aggregate_cpu_seconds']", runner)
            self.assertNotIn("wait4_cpu + parallel", runner)
            self.assertIn('wait4_registered_worker_and_reaped_descendants', runner)

    def test_packet_subtract_charge_overrun_and_bounded_reads(self):
        reservation = 536870912
        self.assertEqual(PARALLEL.artifacts_allowance_after_packet(reservation, 100), reservation - 100)
        with self.assertRaises(ValueError):
            PARALLEL.artifacts_allowance_after_packet(reservation, reservation)
        runner = load_runner()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            child = root / 'source-unit-00'
            child.mkdir()
            (child / 'packet.json').write_bytes(b'12345')
            (child / 'artifacts').mkdir()
            (child / 'artifacts' / 'part.bin').write_bytes(b'abcdef')
            outputs = BoundedOutputs(root / 'out', maximum_total_bytes=8, maximum_file_bytes=8)
            evidence = {}
            with self.assertRaises(ValueError):
                PARALLEL.charge_child_output_bytes(
                    outputs, (child,), reservation_per_child=10, evidence=evidence)
            self.assertEqual(evidence['joined_output_bytes'], 11)
            self.assertEqual(outputs.written, 11)
            self.assertTrue(outputs.failed)
            self.assertEqual(evidence['child_directory_overruns'][0]['size_bytes'], 11)
            huge = root / 'huge.json'
            huge.write_bytes(b'x' * 64)
            with self.assertRaises(ValueError):
                runner.checked(huge, maximum=8)
            good = root / 'good.json'
            payload = b'{"ok": true}\n'
            good.write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            with self.assertRaises(ValueError):
                runner.load_reference({'path': str(good), 'sha256': '0' * 64, 'size_bytes': len(payload)})
            with self.assertRaises(ValueError):
                runner.load_reference({'path': str(good), 'sha256': digest, 'size_bytes': len(payload) + 1})
            self.assertEqual(runner.load_reference(
                {'path': str(good), 'sha256': digest, 'size_bytes': len(payload)}), {'ok': True})

    def test_namespace_receipt_and_reference_rejections(self):
        unit = {'root': 'NQ', 'role': 'ordinary_pipeline_cost', 'source_path': 'a.parquet',
                'event_start_ns': 1, 'event_end_ns': 2, 'source_variant': 'aaa', 'cash_date': '2024-03-11'}
        snapshot = {'sha256': 'a' * 64, 'size_bytes': 1}
        configuration = {'mode': 'check'}
        packet = {'attempt_id': 'attempt-a', 'trial_id': 'trial-a', 'protocol_sha256': PROTOCOL_SHA,
                  'code_snapshot': snapshot, 'configuration': configuration}
        with tempfile.TemporaryDirectory() as folder:
            runs = Path(folder) / 'runs'
            expected_dir, expected_packet = PARALLEL.source_unit_namespace(
                'attempt-a', 0, runs_root=runs)
            expected_dir.mkdir(parents=True)
            other = runs / 'attempt-b' / 'outputs' / 'source-unit-00'
            other.mkdir(parents=True)
            with self.assertRaises(ValueError):
                PARALLEL.require_source_unit_namespace(
                    attempt_id='attempt-a', ordinal=0,
                    child_packet_path=other / 'packet.json', output_directory=other, runs_root=runs)
            artifacts = expected_dir / 'artifacts'
            artifacts.mkdir()
            escaped = Path(folder) / 'escape.json'
            escaped.write_text('{}')
            with self.assertRaises(ValueError):
                PARALLEL.require_reference_in_namespace({'path': str(escaped)}, artifacts)
            inside = artifacts / 'unit.json'
            inside.write_text('{}')
            self.assertEqual(PARALLEL.require_reference_in_namespace({'path': str(inside)}, artifacts),
                             inside.resolve())
            wait4_child = {'pid': 4321, 'ordinal': 0}
            receipt = {
                'success': True, 'attempt_id': 'attempt-a', 'trial_id': 'trial-a',
                'protocol_sha256': PROTOCOL_SHA, 'code_snapshot': snapshot,
                'configuration': configuration, 'coordinator_pid': 1234, 'child_pid': 4321,
                'ordinal': 0, 'unit_identity': PARALLEL.unit_identity(unit), 'unit': unit,
            }
            PARALLEL.require_joined_receipt(
                receipt, packet=packet, wait4_child=wait4_child, unit=unit, coordinator_pid=1234)
            for broken in (
                {**receipt, 'child_pid': 1},
                {**receipt, 'attempt_id': 'other'},
                {**receipt, 'configuration': {'mode': 'other'}},
                {**receipt, 'coordinator_pid': 9},
            ):
                with self.assertRaises(ValueError):
                    PARALLEL.require_joined_receipt(
                        broken, packet=packet, wait4_child=wait4_child, unit=unit, coordinator_pid=1234)
            oversized = artifacts / 'source-unit-receipt.json'
            oversized.write_bytes(b'{' + b'x' * 64 + b'}')
            runner = load_runner()
            with self.assertRaises(ValueError):
                runner.checked(oversized, maximum=8)

    def test_pool_wall_guard_and_cooperative_parent_stop(self):
        started = 1000.0
        self.assertEqual(PARALLEL.pool_wall_deadline(started, 3600), 1000.0 + 3590)
        with self.assertRaises(ValueError):
            PARALLEL.pool_wall_deadline(started, 5, guard_seconds=10)
        cooperative = (
            'import os, signal, time\n'
            'def handle(signum, frame):\n'
            '    os._exit(0)\n'
            'signal.signal(signal.SIGTERM, handle)\n'
            'time.sleep(30)\n'
        )
        process = subprocess.Popen([sys.executable, '-c', cooperative], start_new_session=True)
        time.sleep(0.1)
        stopped = PARALLEL.terminate_then_kill_group(process.pid, grace_seconds=2)
        self.assertFalse(stopped['group_killed'])
        self.assertTrue(stopped['cpu_accounting_complete'])
        self.assertIsNotNone(stopped['usage'])
        stubborn = (
            'import signal, time\n'
            'signal.signal(signal.SIGTERM, signal.SIG_IGN)\n'
            'time.sleep(30)\n'
        )
        process = subprocess.Popen([sys.executable, '-c', stubborn], start_new_session=True)
        time.sleep(0.1)
        stopped = PARALLEL.terminate_then_kill_group(process.pid, grace_seconds=1)
        self.assertTrue(stopped['group_killed'])
        self.assertFalse(stopped['cpu_accounting_complete'])
        self.assertIn('process-group kill', stopped['cpu_accounting_uncertainty'])
        charged = PARALLEL.conservative_attempt_cpu_seconds(
            wait4_usage=stopped['usage'], accounting_complete=False, hard_cpu_seconds=1210)
        self.assertEqual(charged, 1210 if stopped['usage'] is None else max(
            PARALLEL.wait4_cpu_seconds(stopped['usage']), 1210))
        runner = load_runner()
        self.assertNotIn('Popen', inspect.getsource(runner.source_unit))
        self.assertIn('install_source_worker_signal_handlers', inspect.getsource(runner.worker))
        self.assertIn('SourceWorkerInterrupt', inspect.getsource(runner.install_source_worker_signal_handlers))

    def test_unexpected_coordinator_exit_stops_unreaped_group_members(self):
        # The isolated fixture is a subreaper so its deliberately orphaned
        # grandchild is also waited for and charged to the registered check.
        coordinator = (
            'import os, subprocess, sys\n'
            'from pathlib import Path\n'
            'child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])\n'
            'Path(sys.argv[1]).write_text(str(child.pid))\n'
            'os._exit(7)\n'
        )
        script = f"""
import ctypes, json, os, signal, subprocess, sys
from pathlib import Path
sys.path.insert(0, {str(ROOT / 'tools')!r})
from auction_flow_parallel import cleanup_reaped_coordinator_group, conservative_attempt_cpu_seconds
assert ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) == 0
child_file = Path(sys.argv[1])
process = subprocess.Popen([sys.executable, '-c', {coordinator!r}, str(child_file)], start_new_session=True)
try:
    _, status, usage = os.wait4(process.pid, 0)
    process.returncode = os.waitstatus_to_exitcode(status)
    assert process.returncode == 7
    child_pid = int(child_file.read_text())
    cleanup = cleanup_reaped_coordinator_group(process.pid)
    assert child_pid in cleanup['surviving_group_pids']
    assert cleanup['group_killed'] and not cleanup['cpu_accounting_complete']
    assert conservative_attempt_cpu_seconds(wait4_usage=usage, accounting_complete=False,
                                            hard_cpu_seconds=1210) >= 1210
    waited, status, child_usage = os.wait4(child_pid, 0)
    assert waited == child_pid and os.waitstatus_to_exitcode(status) == -signal.SIGKILL
finally:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
"""
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run([sys.executable, '-c', script, str(Path(folder) / 'child.pid')],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
