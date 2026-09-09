"""One durable, resource-bounded full-suite execution for three frozen families.

Use --recover SHARED_ID to finish an interrupted lifecycle without rerunning tests.
Assertion output and completion payloads survive worker/supervisor termination.
"""
from contextlib import contextmanager
from dataclasses import asdict
import ast
import fcntl
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time
from uuid import uuid4

from trading_research.operations.artifacts import (
    ArtifactStore, artifact_ref, canonical_json, code_manifest, code_snapshot, digest, sync_directory,
)
from trading_research.operations.trials import TrialRegistry

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / 'evidence/trials/shared_foundations'
SPECS = (
    ('f05', 'F05-canonical-transaction-reference-v1', 'draft_assertions',
     ('tests.test_transactions', 'tests.test_transaction_matching')),
    ('f06-f07', 'F06-F07-quality-support-reference-v1', 'expected_cases', ('tests.test_quality_joins',)),
    ('f08', 'F08-roll-coordinate-reference-v1', 'cases', ('tests.test_roll_transitions',)),
)
FAMILIES = {row[1] for row in SPECS}


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.pending-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(canonical_json(value) + b'\n')
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
        sync_directory(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@contextmanager
def group_lock():
    RUNS.mkdir(parents=True, exist_ok=True)
    with (RUNS / '.lock').open('a+b') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def validate_registrations(registry, registrations):
    names = [r['family'] for r in registrations]
    if len(names) != len(FAMILIES) or set(names) != FAMILIES:
        raise ValueError('exactly the three distinct frozen foundation families are required')
    state = registry.state()
    for registration in registrations:
        family = state['families'][registration['family']]
        if (family['protocol'] != registration or family['max_attempts'] != 3
                or family['cpu_budget_seconds'] != 600):
            raise ValueError('immutable family registration or budget differs')
        for name in ('protocol', 'golden'):
            if (ROOT / registration[name + '_path']).read_bytes() != registry.artifacts.read(artifact_ref(registration[name])):
                raise ValueError('frozen protocol or golden bytes changed')
        if tuple(registration[k] for k in ('maximum_cpu_per_attempt', 'hard_cpu_seconds',
                                          'address_space_bytes', 'wall_seconds')) != (180, 190, 4 * 1024**3, 240):
            raise ValueError('resource contract differs from the worker')


def static_methods(modules):
    result = []
    for module in modules:
        tree = ast.parse((ROOT / (module.replace('.', '/') + '.py')).read_text())
        for cls in tree.body:
            if isinstance(cls, ast.ClassDef):
                result.extend(f'{module}.{cls.name}.{m.name}' for m in cls.body
                              if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name.startswith('test_'))
    if len(result) != len(set(result)):
        raise ValueError('duplicate static test identities')
    return sorted(result)


def retain_preflight(registry, registrations, manifest):
    store = registry.artifacts
    review_path = ROOT / 'reports/f05-f08-batch-review.json'
    review = json.loads(review_path.read_bytes())
    if (review['review_complete_before_repair'] is not True or review['consolidated_repair_passes'] != 1
            or review['repair_status'] != 'complete_static_verification_ready_for_shared_run'
            or review['repaired_code_manifest_sha256'] != digest(manifest)
            or any(d['status'] != 'repaired_and_statically_verified' for d in review['dispositions'].values())):
        raise ValueError('complete review and one verified repair pass must precede execution')
    refs = {'batch_review': asdict(store.put_bytes(review_path.read_bytes(), kind='implementation_review')),
            'review_text': asdict(store.put_bytes((ROOT / 'validation/F05_F08_BATCH_REVIEW.md').read_bytes(), kind='implementation_review')),
            'recorder': asdict(store.put_bytes((ROOT / 'tools/record_foundation_extensions.py').read_bytes(), kind='evidence_assembly_script')),
            'reviews': [], 'coverage': {}}
    for identity in [*review['reviews'], *review['repair_reports'], *review['frozen_contracts']]:
        raw = (ROOT / identity['path']).read_bytes()
        ref = store.put_bytes(raw, kind='review_support')
        if ref.sha256 != identity['sha256']:
            raise ValueError('reviewed artifact changed before execution')
        refs['reviews'].append(asdict(ref))
    by_family = {r['family']: r for r in registrations}
    for prefix, family, case_key, modules in SPECS:
        raw = (ROOT / f'reports/{prefix}-implementation-coverage.json').read_bytes()
        coverage = json.loads(raw)
        source = store.read_json(artifact_ref(by_family[family]['source_cases']))['preparation'][case_key]
        expected = [case['id'] for case in source]
        actual = [case['case_id'] for case in coverage['cases']]
        if (len(expected) != len(set(expected)) or len(actual) != len(set(actual)) or set(expected) != set(actual)
                or sorted(coverage['test_modules']) != sorted(modules) or not coverage['remaining']):
            raise ValueError(f'{prefix}: exact source case, module or remaining-gate mapping differs')
        methods = static_methods(modules)
        for case in coverage['cases']:
            if not isinstance(case['remaining'], list) or (not case['test_methods'] and not case['remaining']):
                raise ValueError('every case needs assertions or an explicit remaining gate')
            for method in case['test_methods']:
                if sum(m.rsplit('.', 1)[-1] == method for m in methods) != 1:
                    raise ValueError(f'ambiguous or missing mapped method: {method}')
        refs['coverage'][prefix] = {'artifact': asdict(store.put_bytes(raw, kind='implementation_case_mapping')),
                                    'static_assertion_ids': methods, 'approved_modules': list(modules)}
    return refs


def worker(result_path):
    resource.setrlimit(resource.RLIMIT_CPU, (180, 190))
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))
    signal.alarm(240)
    # Publish group identity before importing/discovering any suite code. Even
    # if the parent dies between Popen and its PID write, descendants remain
    # attributable through this durable worker acknowledgement.
    result_path = Path(result_path)
    atomic_json(result_path.parent / 'worker-started.json',
                {'pid': os.getpid(), 'pgid': os.getpgrp(), 'result_path': str(result_path),
                 'worker_source': str(Path(__file__).resolve())})
    from trading_research.verify import run
    result = run('all', evidence_root=ROOT / 'evidence', plan_root=ROOT.parent / 'planning/trading-model',
                 require_traceability=True, progress_stream=sys.stdout)
    atomic_json(result_path, result)
    return 0 if result['success'] else 1


def members_for(registry, shared_id):
    state = registry.state()
    trials = {t['id'] for t in state['trials'].values()
              if t['configuration'].get('shared_execution_id') == shared_id}
    return sorted(({'family': a['family'], 'trial_id': a['trial_id'], 'attempt_id': a['id']}
                   for a in state['attempts'].values() if a['trial_id'] in trials), key=lambda m: m['family'])


def finalize(registry, path, lifecycle):
    """A durable completion can be retried even if artifact publication/finish failed."""
    report = lifecycle['completion']
    if report['success'] != (report['status'] == 'succeeded'):
        raise ValueError('success and terminal status must describe one consistent outcome')
    ref = registry.artifacts.put_json(report, kind='supervised_engineering_verification')
    refs = [asdict(ref)]
    if report['result'] is not None:
        source_store = ArtifactStore(ROOT / 'evidence/artifacts')
        for name in ('artifact', 'code_snapshot'):
            item = artifact_ref(report['result'][name])
            refs.append(asdict(registry.artifacts.put_bytes(source_store.read(item), kind=item.kind)))
    errors = []
    status = 'succeeded' if report['success'] else report['status']
    for member in report['members']:
        try:
            attempt = registry.state()['attempts'][member['attempt_id']]
            if attempt['status'] == 'running':
                registry.finish(member['attempt_id'], status=status, cpu_seconds=report['cpu_seconds'],
                                wall_seconds=report['wall_seconds'], peak_rss_bytes=report['peak_rss_bytes'],
                                reason=report['reason'], result_artifacts=tuple(refs))
            else:
                expected_cpu = report['cpu_seconds'] if report['cpu_seconds'] is not None else attempt['cpu_reservation_seconds']
                if (attempt['status'] != status or attempt['result_artifacts'] != refs
                        or attempt['cpu_seconds'] != expected_cpu or attempt['wall_seconds'] != report['wall_seconds']
                        or attempt['peak_rss_bytes'] != report['peak_rss_bytes']):
                    raise ValueError('prior family outcome differs from durable completion')
        except Exception as exc:
            errors.append({'member': member, 'error': f'{type(exc).__name__}: {exc}'})
    lifecycle.update(supervised_artifact=asdict(ref), finalization_errors=errors,
                     phase='completed' if errors else 'finalized')
    atomic_json(path, lifecycle)
    if errors:
        raise RuntimeError(f'completion is durable; use --recover {lifecycle["shared_execution_id"]}: {errors}')
    summary = {key: report[key] for key in ('success', 'shared_execution_id', 'members', 'reason',
                                           'cpu_seconds', 'wall_seconds', 'peak_rss_bytes')}
    summary.update(artifact=asdict(ref), report=str(registry.artifacts.path(ref)), verification=report['result'])
    summary_path = ROOT / f'reports/f05-f08-verification-{report["shared_execution_id"][:12]}.json'
    atomic_json(summary_path, summary)
    print(json.dumps(summary | {'summary': str(summary_path)}, indent=2))
    return 0 if report['success'] else 1


def completion(lifecycle, *, success=False, status='interrupted', reason, cpu=None, wall=None, rss=None,
               result=None, returncode=None):
    folder = RUNS / lifecycle['shared_execution_id']
    def retained_text(name):
        p = folder / name
        return p.read_text(errors='replace') if p.exists() else ''
    return {'success': success, 'status': status, 'shared_execution_id': lifecycle['shared_execution_id'],
            'members': lifecycle['members'], 'configuration': lifecycle['configuration'],
            'code_snapshot': lifecycle['code_snapshot'], 'result': result, 'worker_exit_code': returncode,
            'reason': reason, 'stdout': retained_text('stdout.log'), 'stderr': retained_text('stderr.log'),
            'partial_result_bytes_hex': (folder / 'result.json').read_bytes().hex() if (folder / 'result.json').exists() else '',
            'cpu_seconds': cpu, 'wall_seconds': wall, 'peak_rss_bytes': rss,
            'resource_basis': 'One reaped worker RUSAGE_CHILDREN; unknown hard-crash use charges every reservation.',
            'market_tape_reads': 0, 'economic_runs': 0,
            'limitations': ['Finite synthetic engineering only; source, native cohort, all-consumer and economic gates remain.']}


def live_groups(groups):
    """Runnable group members; a dead zombie cannot continue a test or child."""
    live = set()
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            # comm may itself contain spaces/parentheses; parse after its last ).
            fields = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
            state, group = fields[0], int(fields[2])
            if group in groups and state not in {'Z', 'X'}:
                live.add(group)
        except (FileNotFoundError, ProcessLookupError):
            continue
    return live


def recover(registry, shared_id):
    if len(shared_id) != 32 or any(c not in '0123456789abcdef' for c in shared_id):
        raise ValueError('invalid shared execution identity')
    path = RUNS / f'{shared_id}.json'
    lifecycle = json.loads(path.read_bytes())
    if 'completion' not in lifecycle:
        # Recovery never starts another worker. Kill only an exact retained worker
        # command, never an unverified/reused PID. Scan also covers launch-record gaps.
        target = str(RUNS / shared_id / 'result.json').encode()
        worker_file = str(Path(__file__).resolve()).encode()
        groups = {lifecycle['pid']} if lifecycle.get('pid') is not None else set()
        handshake_path = RUNS / shared_id / 'worker-started.json'
        if handshake_path.exists():
            handshake = json.loads(handshake_path.read_bytes())
            if (handshake['result_path'].encode() != target or handshake['worker_source'].encode() != worker_file
                    or type(handshake['pid']) is not int or handshake['pid'] <= 0
                    or handshake['pgid'] != handshake['pid']):
                raise ValueError('worker startup acknowledgement differs from the retained launch')
            groups.add(handshake['pgid'])
        for entry in Path('/proc').iterdir():
            if not entry.name.isdigit():
                continue
            try:
                command = (entry / 'cmdline').read_bytes().split(b'\0')
                if worker_file in command and b'--worker' in command and target in command:
                    groups.add(int(entry.name))
                    os.killpg(int(entry.name), signal.SIGKILL)
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                continue
        if live_groups(groups):
            # Keep the gate if any group still has executable members. Do not
            # kill an unverified/reused leader merely because a PID was recorded.
            raise RuntimeError('a launched process group still has live members; retain the recovery gate')
        lifecycle['members'] = members_for(registry, shared_id)
        never_launched = lifecycle['phase'] == 'reserving'
        lifecycle['completion'] = completion(lifecycle, reason='Recovered interrupted supervisor; no worker rerun.',
            cpu=0 if never_launched else None, wall=0 if never_launched else None, rss=0 if never_launched else None)
        lifecycle['phase'] = 'completed'
        atomic_json(path, lifecycle)
    return finalize(registry, path, lifecycle)


def supervise(arguments):
    registry = TrialRegistry(ROOT / 'evidence/trials')
    with group_lock():
        if len(arguments) == 2 and arguments[0] == '--recover':
            return recover(registry, arguments[1])
        for path in RUNS.glob('*.json'):
            old = json.loads(path.read_bytes())
            if old['phase'] != 'finalized':
                raise RuntimeError(f'unresolved shared execution: use --recover {old["shared_execution_id"]}')
        if any(a['family'] in FAMILIES and a['status'] == 'running' for a in registry.state()['attempts'].values()):
            raise RuntimeError('a participating family has an unresolved attempt; reconcile before any launch')
        registrations = [json.loads((ROOT / name).read_bytes()) for name in arguments]
        validate_registrations(registry, registrations)
        snapshot = code_snapshot(ROOT, registry.artifacts)
        manifest = registry.artifacts.read_json(snapshot)['manifest']
        preflight = retain_preflight(registry, registrations, manifest)
        shared_id = uuid4().hex
        configuration = {'shared_execution_id': shared_id, 'registrations': registrations, 'preflight': preflight,
                         'supervisor': asdict(registry.artifacts.put_bytes(Path(__file__).read_bytes(), kind='verification_supervisor_source')),
                         'suite': 'all', 'cpu_reservation_seconds': 180, 'cpu_hard_seconds': 190,
                         'address_space_bytes': 4 * 1024**3, 'wall_limit_seconds': 240,
                         'accounting': 'One physical execution; identical observed worker use charged to every family, never summed.'}
        lifecycle = {'shared_execution_id': shared_id, 'phase': 'reserving', 'members': [],
                     'configuration': configuration, 'code_snapshot': asdict(snapshot)}
        path = RUNS / f'{shared_id}.json'
        atomic_json(path, lifecycle)
        process = None
        folder = RUNS / shared_id
        folder.mkdir()
        started, before = time.monotonic(), resource.getrusage(resource.RUSAGE_CHILDREN)
        def interrupted(signum, frame):
            raise KeyboardInterrupt(f'supervisor received signal {signum}')
        prior_handlers = {s: signal.signal(s, interrupted) for s in (signal.SIGTERM, signal.SIGINT)}
        result, returncode, success, status = None, None, False, 'failed'
        reason = 'worker did not produce a successful result'
        try:
            for registration in registrations:
                trial = registry.register(name='Combined foundation reference and existing regression suite',
                    family=registration['family'], stage='engineering', configuration=configuration,
                    code_hash=digest(manifest), data_hashes={'independent_golden': registration['golden']['sha256']},
                    fold_version='no-market-fit', target_version='fixed-foundation-extensions-v1')
                registry.start(trial, cpu_reservation_seconds=180)
                lifecycle['members'] = members_for(registry, shared_id)
                atomic_json(path, lifecycle)
            lifecycle['phase'] = 'launch_pending'
            atomic_json(path, lifecycle)
            with (folder / 'stdout.log').open('wb') as output, (folder / 'stderr.log').open('wb') as errors:
                process = subprocess.Popen([sys.executable, '-u', str(Path(__file__).resolve()), '--worker', str(folder / 'result.json')],
                                           cwd=ROOT, stdout=output, stderr=errors, start_new_session=True)
                lifecycle.update(phase='running', pid=process.pid)
                atomic_json(path, lifecycle)
                try:
                    returncode = process.wait(timeout=240)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL); returncode = process.wait()
                    reason = 'supervisor enforced the registered 240-second wall limit'
            if (folder / 'result.json').exists():
                result = json.loads((folder / 'result.json').read_bytes())
                success = (returncode == 0 and result['success'] and code_manifest(ROOT) == manifest
                           and result['code_snapshot'] == asdict(snapshot))
                status = 'succeeded' if success else 'failed'
                reason = 'Registered combined assertions passed.' if success else 'Assertion failure or code identity changed; output retained.'
            elif returncode is not None and reason == 'worker did not produce a successful result':
                reason = f'worker exited {returncode} without a complete result'
        except BaseException as exc:
            reason = f'{type(exc).__name__}: {exc}'
            success, status = False, 'interrupted'
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL); returncode = process.wait()
        finally:
            for s, handler in prior_handlers.items():
                signal.signal(s, handler)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        if process is not None and live_groups({process.pid}):
            # The completed leader may have left descendants. Stop its known
            # group and retain the unresolved lifecycle if they have not exited.
            os.killpg(process.pid, signal.SIGKILL)
            raise RuntimeError(f'worker left live descendants; use --recover {shared_id} after termination')
        lifecycle['members'] = members_for(registry, shared_id)
        lifecycle['completion'] = completion(lifecycle, success=success, status=status, reason=reason,
            cpu=after.ru_utime + after.ru_stime - before.ru_utime - before.ru_stime,
            wall=time.monotonic() - started if process is not None else 0,
            rss=after.ru_maxrss * 1024 if process is not None else 0, result=result, returncode=returncode)
        lifecycle['phase'] = 'completed'
        atomic_json(path, lifecycle)
        return finalize(registry, path, lifecycle)


if __name__ == '__main__':
    raise SystemExit(worker(sys.argv[2]) if len(sys.argv) == 3 and sys.argv[1] == '--worker' else supervise(sys.argv[1:]))
