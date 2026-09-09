"""Run one durable, bounded complete suite for a frozen engineering batch.

Supply a relative batch-contract path. --recover SHARED_ID finalizes an
interrupted lifecycle without starting tests again. Older runs retain their
original supervisor ownership and immutable source.
"""
from contextlib import contextmanager
from dataclasses import asdict
import fcntl
import hashlib
import shlex
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
from engineering_batch_contract import (
    ROOT, RESOLVED, baseline_assertions, case_contract, load_batch_snapshot, local_identity, byte_identity, final_resource_error,
    package_path, retain_mapping_inputs, static_methods, validate_batch,
    validate_coverage, validate_registrations, validate_review_support,
    batch_resources, configuration_resources, resource_configuration, validate_resource_binding,
    CONFIGURATION_RESOURCE_FIELDS,
)

RUNS = ROOT / 'evidence/trials/shared_foundations'
WORKER_TOKEN_ENV = 'TRADING_RESEARCH_ENGINEERING_WORKER_TOKEN'


def launch_token(value):
    if type(value) is not str or len(value) != 32 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('exact worker launch token required')
    return value


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


def retain_preflight(registry, registrations, manifest, batch, batch_path,batch_raw):
    store = registry.artifacts
    review_raw = package_path(batch['batch_review_path']).read_bytes()
    review = json.loads(review_raw)
    if (review['review_complete_before_repair'] is not True
            or review['repair_status'] != 'complete_static_verification_ready_for_shared_run'
            or review['repaired_code_manifest_sha256'] != digest(manifest)
            or any(d['status'] not in RESOLVED for d in review['dispositions'].values())):
        raise ValueError('complete initial review and consolidated repair must precede execution')
    original_review = validate_review_support(review, store, batch)
    contract_paths = sorted({p for spec, registration in zip(batch['families'], registrations)
        for p in (spec['registration_path'], spec['preparation_path'], registration['protocol_path'], registration['golden_path'])}
        | set(batch['additional_contract_paths']))
    if review['effective_contracts'] != [local_identity(p) for p in contract_paths]:
        raise ValueError('initial review omitted or changed a frozen family contract')
    baseline = baseline_assertions(store, batch)
    all_modules = ['tests.' + p.stem for p in sorted((ROOT / 'tests').glob('test_*.py'))]
    expected_methods = static_methods(all_modules)
    if not set(baseline) <= set(expected_methods):
        raise ValueError('a previously passing assertion was removed before execution')
    refs = {'pre_repair_review': original_review,
            'batch_review': asdict(store.put_bytes(review_raw, kind='implementation_review')),
            'review_text': asdict(store.put_bytes(package_path(batch['review_text_path']).read_bytes(), kind='implementation_review')),
            'baseline_verification': batch['baseline_verification'],
            'required_existing_assertion_ids': baseline, 'expected_assertion_ids': expected_methods,
            'reviews': [], 'coverage': {}}
    for role, path in batch['tools'].items():
        raw=package_path(path).read_bytes()
        if byte_identity(path,raw) not in review['repaired_orchestration_sources']:
            raise ValueError('orchestration changed after its complete static repair')
        refs[role] = asdict(store.put_bytes(raw, kind='engineering_orchestration_source'))
    for identity in [*review['reviews'], *review['repair_reports'], *review['effective_contracts']]:
        raw = package_path(identity['path']).read_bytes()
        ref = store.put_bytes(raw, kind='review_support')
        if ref.sha256 != identity['sha256']:
            raise ValueError('reviewed artifact changed before execution')
        refs['reviews'].append(asdict(ref))
    by_family = {r['family']: r for r in registrations}
    for spec in batch['families']:
        registration = by_family[spec['family']]
        raw = package_path(spec['coverage_path']).read_bytes()
        coverage = json.loads(raw)
        originals, literals, bindings, clauses = case_contract(store, registration, spec)
        methods = static_methods(spec['test_modules'])
        validate_coverage(coverage, spec, originals, literals, bindings, clauses, methods)
        mapping_inputs = retain_mapping_inputs(store, coverage, registration, spec, batch, batch_path,batch_raw)
        refs['coverage'][spec['prefix']] = {**mapping_inputs,
            'artifact': asdict(store.put_bytes(raw, kind='implementation_case_mapping')),
            'static_assertion_ids': methods, 'approved_modules': spec['test_modules']}
    return refs


def configure_worker_resources(resource_limits):
    if (type(resource_limits) is not dict
            or set(resource_limits) != set(CONFIGURATION_RESOURCE_FIELDS) | ({'resource_contract_version'} if 'resource_contract_version' in resource_limits else set())):
        raise ValueError('exact worker resource fields required before candidate imports')
    cpu, hard_cpu, memory, wall = configuration_resources(resource_limits)
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, hard_cpu))
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    signal.alarm(wall)
    if resource.getrlimit(resource.RLIMIT_CPU) != (cpu, hard_cpu) or resource.getrlimit(resource.RLIMIT_AS) != (memory, memory):
        raise ValueError('actual worker OS limits differ from the frozen launch contract')
    return dict(resource_limits)


def worker_arguments(result_path, configuration):
    resources = {k: configuration[k] for k in (*CONFIGURATION_RESOURCE_FIELDS, 'resource_contract_version') if k in configuration}
    configuration_resources(resources)
    tail = ['-u', str(Path(__file__).resolve()), '--worker', str(result_path)]
    if 'resource_contract_version' in resources:
        tail.append(canonical_json(resources).decode())
    return [sys.executable, *tail]


def worker(result_path, resource_json=None):
    if resource_json is None:
        limits = resource_configuration({'kind': 'engineering_batch_contract_v1'})
    else:
        if type(resource_json) is not str or len(resource_json.encode()) > 1024:
            raise ValueError('bounded exact resource launch JSON required')
        limits = json.loads(resource_json)
        if canonical_json(limits).decode() != resource_json:
            raise ValueError('canonical resource launch bytes required')
    enforced = configure_worker_resources(limits)
    # Publish group identity before importing/discovering any suite code. Even
    # if the parent dies between Popen and its PID write, descendants remain
    # attributable through this durable worker acknowledgement.
    result_path = Path(result_path)
    token = os.environ.get(WORKER_TOKEN_ENV)
    token_fields = {} if token is None else {'worker_launch_token': launch_token(token)}
    atomic_json(result_path.parent / 'worker-started.json',
                {'pid': os.getpid(), 'pgid': os.getpgrp(), 'result_path': str(result_path),
                 'worker_source': str(Path(__file__).resolve()), 'start_identity': process_identity(os.getpid()),
                 'resource_limits': enforced, **token_fields})
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


def validate_result(result, lifecycle):
    configuration = lifecycle['configuration']
    store = ArtifactStore(ROOT / 'evidence/trials/artifacts')
    batch = validate_batch(store.read_json(artifact_ref(configuration['batch_contract'])))
    acknowledgement = lifecycle.get('worker_resource_acknowledgement')
    validate_resource_binding(batch, configuration, acknowledgement)
    if acknowledgement is not None:
        keys = {'pid', 'pgid', 'result_path', 'worker_source', 'start_identity', 'resource_limits'}
        if 'worker_launch_token' in configuration:
            keys.add('worker_launch_token')
            if acknowledgement.get('worker_launch_token') != launch_token(configuration['worker_launch_token']):
                raise ValueError('acknowledgement differs from the immutable worker launch token')
        if batch['kind'] == 'engineering_batch_contract_v2' and set(acknowledgement) != keys:
            raise ValueError('exact v2 worker acknowledgement fields required')
        start = lifecycle.get('worker_start_identity')
        if batch['kind'] == 'engineering_batch_contract_v2':
            for identity in (start, acknowledgement.get('start_identity')):
                if (type(identity) is not dict or set(identity) != {'pid', 'pgid', 'start_ticks', 'boot_id'}
                        or any(type(identity[k]) is not int or identity[k] < 0 for k in ('pid', 'pgid', 'start_ticks'))
                        or identity['pid'] == 0 or identity['pgid'] == 0
                        or type(identity['boot_id']) is not str or not identity['boot_id']):
                    raise ValueError('exact v2 worker process identity fields required')
            if any(type(acknowledgement[k]) is not int for k in ('pid', 'pgid')):
                raise ValueError('exact integer worker process acknowledgement required')
        if (start is None or acknowledgement.get('start_identity') != start
                or acknowledgement.get('pid') != start['pid'] or acknowledgement.get('pgid') != start['pgid']
                or start['pid'] != start['pgid']
                or acknowledgement.get('worker_source') != configuration['supervisor_path']
                or acknowledgement.get('result_path') != str(RUNS / lifecycle['shared_execution_id'] / 'result.json')):
            raise ValueError('resource acknowledgement does not identify the actual retained worker launch')
    required = {'success', 'tests_run', 'passed', 'skipped', 'failures', 'errors', 'report', 'artifact', 'code_snapshot'}
    if type(result) is not dict or set(result) != required or type(result['success']) is not bool:
        raise ValueError('worker result summary schema differs')
    for name in ('tests_run', 'passed', 'skipped', 'failures', 'errors'):
        if type(result[name]) is not int or result[name] < 0:
            raise ValueError('worker result counts must be nonnegative exact integers')
    source = ArtifactStore(ROOT / 'evidence/artifacts')
    verification_ref, snapshot_ref = artifact_ref(result['artifact']), artifact_ref(result['code_snapshot'])
    if verification_ref.kind != 'verification' or snapshot_ref.kind != 'code_snapshot':
        raise ValueError('worker result artifact kinds differ')
    if result['code_snapshot'] != lifecycle['code_snapshot'] or result['report'] != str(source.path(verification_ref)):
        raise ValueError('worker summary artifact path or original snapshot differs')
    retained = ArtifactStore(ROOT / 'evidence/trials/artifacts')
    def read_json(ref):
        try:
            return source.read_json(ref)
        except FileNotFoundError:
            return retained.read_json(ref)
    verification, snapshot = read_json(verification_ref), read_json(snapshot_ref)
    if (type(verification) is not dict or type(snapshot) is not dict
            or verification['code_snapshot'] != result['code_snapshot']
            or verification['success'] is not result['success']
            or verification['tests_run'] != result['tests_run']
            or len(verification['passed_assertion_ids']) != result['passed']
            or any(len(verification[k]) != result[k] for k in ('errors', 'failures', 'skipped'))):
        raise ValueError('worker summary differs from verified artifact content')
    if result['success'] and (result['tests_run'] != result['passed'] or any(result[k] for k in ('errors', 'failures', 'skipped'))):
        raise ValueError('successful worker result contains incomplete assertions')
    if result['success']:
        passed = verification['passed_assertion_ids']
        preflight = lifecycle['configuration']['preflight']
        if (len(passed) != len(set(passed))
                or sorted(passed) != preflight['expected_assertion_ids']
                or not set(preflight['required_existing_assertion_ids']) <= set(passed)):
            raise ValueError('successful execution omitted or added predeclared assertion identities')
    # Verify the reconstructible snapshot bytes, not only a mutable result path.
    if snapshot != ArtifactStore(ROOT / 'evidence/trials/artifacts').read_json(snapshot_ref):
        raise ValueError('worker snapshot bytes differ from the original retained snapshot')
    return result


def validate_successful_completion(registry, lifecycle):
    """No success publication may bypass the immutable launch and result checks."""
    report = lifecycle['completion']
    if report.get('success') is not True or report.get('status') != 'succeeded':
        raise ValueError('exact successful completion required')
    for key in ('shared_execution_id', 'configuration', 'members', 'code_snapshot'):
        if canonical_json(report.get(key)) != canonical_json(lifecycle[key]):
            raise ValueError('completion differs from retained lifecycle: ' + key)
    for key in ('worker_start_identity', 'worker_resource_acknowledgement'):
        if canonical_json(report.get(key)) != canonical_json(lifecycle.get(key)):
            raise ValueError('completion differs from retained worker evidence: ' + key)
    if type(report.get('worker_exit_code')) is not int or report['worker_exit_code'] != 0:
        raise ValueError('successful completion requires an observed zero worker exit code')
    configuration = lifecycle['configuration']
    batch = validate_batch(registry.artifacts.read_json(artifact_ref(configuration['batch_contract'])))
    validate_registrations(registry, configuration['registrations'], batch)
    members = members_for(registry, lifecycle['shared_execution_id'])
    if (len(members) != len(batch['families'])
            or {m['family'] for m in members} != {s['family'] for s in batch['families']}
            or canonical_json(members) != canonical_json(lifecycle['members'])):
        raise ValueError('completion membership differs from registered attempts')
    state = registry.state()
    for member in members:
        trial = state['trials'][member['trial_id']]
        if canonical_json(trial['configuration']) != canonical_json(configuration):
            raise ValueError('completion configuration differs from immutable trial')
    error = final_resource_error(report['cpu_seconds'], report['wall_seconds'], report['peak_rss_bytes'], configuration)
    if error is not None:
        raise ValueError(error)
    if type(report.get('result')) is not dict or report['result'].get('success') is not True:
        raise ValueError('successful completion requires its successful worker result')
    validate_result(report['result'], lifecycle)
    return report


def finalize(registry, path, lifecycle):
    """A durable completion can be retried even if artifact publication/finish failed."""
    report = lifecycle['completion']
    if report['success'] != (report['status'] == 'succeeded'):
        raise ValueError('success and terminal status must describe one consistent outcome')
    if report['success']:
        error=final_resource_error(report['cpu_seconds'],report['wall_seconds'],report['peak_rss_bytes'],report['configuration'])
        if error is not None:
            states=registry.state()['attempts']
            if any(states[m['attempt_id']]['status']!='running' for m in report['members']):
                raise RuntimeError('accepted final resources differ after partial finalization')
            report={**report,'success':False,'status':'failed','reason':error}
            lifecycle['completion']=report;atomic_json(path,lifecycle)
    if report['success'] or report['result'] is not None:
        try:
            if report['success']:
                validate_successful_completion(registry, lifecycle)
            else:
                validate_result(report['result'], lifecycle)
        except Exception as exc:
            # A malformed legacy completion must not permanently strand its
            # reservations. Never rewrite outcomes already terminalized.
            states = registry.state()['attempts']
            if any(states[m['attempt_id']]['status'] != 'running' for m in lifecycle['members']):
                raise RuntimeError('accepted evidence changed after partial finalization; restore retained artifacts before recovery') from exc
            rejected = report
            same_binding = all(canonical_json(report.get(k)) == canonical_json(lifecycle[k])
                               for k in ('configuration', 'members', 'shared_execution_id', 'code_snapshot'))
            measured = same_binding and final_resource_error(report.get('cpu_seconds'), report.get('wall_seconds'),
                report.get('peak_rss_bytes'), lifecycle['configuration']) is None
            report = completion(lifecycle, reason=str(report['reason']) + '; invalid completion retained separately: '
                                + type(exc).__name__ + ': ' + str(exc),
                                cpu=report['cpu_seconds'] if measured else None,
                                wall=report['wall_seconds'] if measured else None,
                                rss=report['peak_rss_bytes'] if measured else None)
            report['rejected_result_summary'] = rejected.get('result')
            report['rejected_completion'] = rejected
            lifecycle['completion'] = report
            atomic_json(path, lifecycle)
    supporting = []
    if report['result'] is not None:
        try:
            # result was validated before durable completion. Copy errors remain
            # a retryable publication step; no worker is started by recovery.
            source_store = ArtifactStore(ROOT / 'evidence/artifacts')
            for name in ('artifact', 'code_snapshot'):
                item = artifact_ref(report['result'][name])
                try:
                    registry.artifacts.read(item)
                except FileNotFoundError:
                    registry.artifacts.put_bytes(source_store.read(item), kind=item.kind)
                supporting.append(asdict(item))
        except Exception as exc:
            lifecycle.update(phase='completed', finalization_errors=[{'stage': 'artifact_copy',
                'error': f'{type(exc).__name__}: {exc}'}])
            atomic_json(path, lifecycle)
            raise RuntimeError('validated result publication incomplete; recover without rerun: ' + recovery_command(lifecycle)) from exc
    ref = registry.artifacts.put_json(report, kind='supervised_engineering_verification')
    refs = [asdict(ref), *supporting]
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
    summary_path = ROOT / f'reports/{report["configuration"]["batch_id"]}-verification-{report["shared_execution_id"][:12]}.json'
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
            'resource_basis': 'Linux process-group self plus reaped-descendant CPU; parent-before-child snapshots avoid duplicate charging; final adopted descendants reaped by supervisor. Unknown hard-crash use charges every reservation. RSS is the larger of sampled aggregate group RSS and reaped-child high-water RSS; shared pages may be counted conservatively more than once.',
            'cpu_guard': lifecycle.get('cpu_guard'), 'worker_start_identity': lifecycle.get('worker_start_identity'),
            'worker_resource_acknowledgement': lifecycle.get('worker_resource_acknowledgement'),
            'market_tape_reads': 0, 'economic_runs': 0,
            'limitations': ['Finite synthetic engineering only; source, native cohort, all-consumer and economic gates remain.']}


def proc_row(pid):
    path = Path('/proc') / str(pid)
    fields = (path / 'stat').read_text().rsplit(')', 1)[1].split()
    return {'pid': int(pid), 'state': fields[0], 'ppid': int(fields[1]), 'pgid': int(fields[2]),
            'start_ticks': int(fields[19]), 'self_ticks': int(fields[11]) + int(fields[12]),
            'reaped_ticks': int(fields[13]) + int(fields[14]), 'rss_bytes': max(0, int(fields[21])) * os.sysconf('SC_PAGE_SIZE')}


def boot_identity():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def process_identity(pid):
    row = proc_row(pid)
    return {k: row[k] for k in ('pid', 'pgid', 'start_ticks')} | {'boot_id': boot_identity()}


def group_rows(groups):
    rows = {}
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            row = proc_row(int(entry.name))
            if row['pgid'] in groups:
                rows[row['pid']] = row
        except (FileNotFoundError, ProcessLookupError):
            continue
    return rows


def live_groups(groups):
    return {row['pgid'] for row in group_rows(groups).values() if row['state'] not in {'Z', 'X'}}


def become_subreaper():
    # Linux subreaper adoption lets the supervisor account for orphaned fork
    # workers after leader death, rather than losing their resource charges.
    import ctypes
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), 'Linux child-subreaper setup failed')


def reap_group_children(pgid, leader_pid):
    # Popen owns the leader wait status; only reap adopted descendants here.
    for pid, row in group_rows({pgid}).items():
        if pid != leader_pid and row['ppid'] == os.getpid():
            try:
                os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                pass


def aggregate_group_cpu(pgid, baseline):
    # Supervisor performs no waits during this snapshot. Read every parent
    # before its children: a child reaped during scanning can be omitted in
    # this sample, but its CPU cannot also appear in an already-read parent.
    reaped = resource.getrusage(resource.RUSAGE_CHILDREN)
    total = reaped.ru_utime + reaped.ru_stime - baseline
    rows = group_rows({pgid})
    def depth(row):
        seen, current = set(), row
        while current['ppid'] in rows and current['ppid'] not in seen:
            seen.add(current['ppid']); current = rows[current['ppid']]
        return len(seen)
    ticks = 0
    for prior in sorted(rows.values(), key=lambda row: (depth(row), row['pid'])):
        try:
            row = proc_row(prior['pid'])
            if row['pgid'] == pgid and row['start_ticks'] == prior['start_ticks']:
                ticks += row['self_ticks'] + row['reaped_ticks']
        except (FileNotFoundError, ProcessLookupError):
            continue
    return total + ticks / os.sysconf('SC_CLK_TCK')


def owning_supervisor(lifecycle):
    configuration = lifecycle.get('configuration', {})
    owner = lifecycle.get('supervisor_path') or configuration.get('supervisor_path')
    if owner is None:
        acknowledgement = RUNS / lifecycle['shared_execution_id'] / 'worker-started.json'
        if acknowledgement.exists():
            owner = json.loads(acknowledgement.read_bytes()).get('worker_source')
    legacy = {
        str(ROOT / 'tools/verify_f09_f12.py'): {
            'F09-shared-bar-reference-v1', 'F10-object-lineage-engineering-v1',
            'F11-artifact-closure-engineering-v1', 'F12-arrival-trace-engineering-v1'},
        str(ROOT / 'tools/verify_foundation_extensions.py'): {
            'F05-canonical-transaction-reference-v1', 'F06-F07-quality-support-reference-v1',
            'F08-roll-coordinate-reference-v1'},
    }
    families = {r['family'] for r in configuration.get('registrations', [])}
    if owner is None:
        owner = next((path for path, values in legacy.items() if values == families), None)
    current = str(Path(__file__).resolve())
    if owner not in {*legacy, current}:
        raise ValueError('unresolved lifecycle has an unknown owning supervisor')
    if configuration.get('supervisor_path', owner) != owner or lifecycle.get('supervisor_path', owner) != owner:
        raise ValueError('lifecycle and configuration supervisor identities disagree')
    store = ArtifactStore(ROOT / 'evidence/trials/artifacts')
    if Path(owner).read_bytes() != store.read(artifact_ref(configuration['supervisor'])):
        raise ValueError('owning recovery source differs from retained bytes; restore recorded source first')
    if owner == current:
        batch = validate_batch(store.read_json(artifact_ref(configuration['batch_contract'])))
        if batch['id'] != configuration['batch_id'] or families != {s['family'] for s in batch['families']}:
            raise ValueError('batch identity or family membership differs from retained contract')
        support = package_path(batch['tools']['contract_support'])
        if support.read_bytes() != store.read(artifact_ref(configuration['preflight']['contract_support'])):
            raise ValueError('recovery contract helper differs from its retained source')
    elif families != legacy[owner]:
        raise ValueError('legacy supervisor does not own the retained families')
    return owner


def recovery_command(lifecycle):
    return shlex.join([sys.executable, owning_supervisor(lifecycle), '--recover', lifecycle['shared_execution_id']])


def _same_process(identity):
    try:
        return process_identity(identity['pid']) == identity
    except (FileNotFoundError, ProcessLookupError):
        return False


def process_has_launch_token(identity, token):
    """Exec preserves the per-launch environment; recheck identity around its read."""
    expected = (WORKER_TOKEN_ENV + '=' + launch_token(token)).encode()
    try:
        if not _same_process(identity):
            return False
        values = (Path('/proc') / str(identity['pid']) / 'environ').read_bytes().split(b'\0')
        return values.count(expected) == 1 and _same_process(identity)
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return False


def recover(registry, shared_id):
    if len(shared_id) != 32 or any(c not in '0123456789abcdef' for c in shared_id):
        raise ValueError('invalid shared execution identity')
    path = RUNS / f'{shared_id}.json'
    lifecycle = json.loads(path.read_bytes())
    owner = owning_supervisor(lifecycle)
    if owner != str(Path(__file__).resolve()):
        raise RuntimeError('foreign shared lifecycle; use its owning recovery command: ' + recovery_command(lifecycle))
    # Recovery may signal processes, so the mutable lifecycle must not supply
    # a replacement launch token/configuration for a different registered run.
    trials = [t for t in registry.state()['trials'].values()
              if t['configuration'].get('shared_execution_id') == shared_id]
    if (any(canonical_json(t['configuration']) != canonical_json(lifecycle['configuration']) for t in trials)
            or not trials and lifecycle['phase'] != 'reserving'):
        raise ValueError('recovery launch configuration differs from immutable registered trials')
    if 'completion' not in lifecycle:
        target = str(RUNS / shared_id / 'result.json')
        identity = lifecycle.get('worker_start_identity')
        token = lifecycle['configuration'].get('worker_launch_token')
        if token is not None:
            launch_token(token)
        acknowledgement = RUNS / shared_id / 'worker-started.json'
        if acknowledgement.exists():
            handshake = json.loads(acknowledgement.read_bytes())
            if handshake['result_path'] != target or handshake['worker_source'] != owner:
                raise ValueError('worker acknowledgement differs from retained launch')
            if token is not None and handshake.get('worker_launch_token') != token:
                raise ValueError('worker acknowledgement differs from retained launch token')
            recorded = handshake.get('start_identity')
            if recorded is None:
                raise ValueError('legacy current-tool acknowledgement has no start identity; retain manual reconciliation gate')
            if (recorded['pid'] != handshake['pid'] or recorded['pgid'] != handshake['pgid']
                    or recorded['pid'] != recorded['pgid'] or identity is not None and identity != recorded):
                raise ValueError('worker acknowledgement process identity differs')
            identity = recorded
            lifecycle['worker_resource_acknowledgement'] = handshake
        expected_command = [v.encode() for v in worker_arguments(target, lifecycle['configuration'])[1:]]
        candidates = []
        for entry in Path('/proc').iterdir():
            if not entry.name.isdigit():
                continue
            try:
                command = (entry / 'cmdline').read_bytes().split(b'\0')
                # Exact argv tail survives a normal fork; use actual PGID,
                # never assume the surviving child's PID is its group ID.
                if command[-1:] == [b'']:
                    command.pop()
                row_identity = process_identity(int(entry.name))
                token_match = token is not None and process_has_launch_token(row_identity, token)
                if (token is not None and not token_match
                        or token is None and command[1:] != expected_command):
                    continue
                if identity is None:
                    lower = lifecycle.get('launch_start_bound')
                    if (lower is None or row_identity['pid'] != row_identity['pgid']
                            or row_identity['boot_id'] != lower['boot_id'] or row_identity['start_ticks'] < lower['start_ticks']):
                        raise ValueError('unacknowledged worker lacks a retained launch identity bound')
                    identity = row_identity
                if (row_identity['pgid'] == identity['pgid'] and row_identity['boot_id'] == identity['boot_id']
                        and row_identity['start_ticks'] >= identity['start_ticks']):
                    candidates.append(row_identity)
            except (FileNotFoundError, ProcessLookupError):
                continue
        lifecycle['recovery_observed_processes'] = candidates
        lifecycle['worker_start_identity'] = identity
        atomic_json(path, lifecycle)
        for candidate in candidates:
            if (_same_process(candidate)
                    and (token is None or process_has_launch_token(candidate, token))):
                try:
                    os.killpg(candidate['pgid'], signal.SIGKILL)
                except ProcessLookupError:
                    pass
        groups = set() if identity is None or identity['boot_id'] != boot_identity() else {identity['pgid']}
        if identity is not None and not candidates and groups:
            try:
                current_leader = process_identity(identity['pid'])
                if current_leader != identity:
                    groups.clear()  # Original PID/PGID has been reused; do not touch it.
            except (FileNotFoundError, ProcessLookupError):
                pass
        deadline = time.monotonic() + 5
        while live_groups(groups) and time.monotonic() < deadline:
            time.sleep(0.01)
        if live_groups(groups):
            raise RuntimeError('the retained group still has executable members; keep recovery gate: ' + recovery_command(lifecycle))
        lifecycle['members'] = members_for(registry, shared_id)
        never_launched = lifecycle['phase'] == 'reserving'
        recovered_result, recovery_reason = None, 'Recovered interrupted supervisor; no worker rerun; exit/resource outcome unknown.'
        result_path = RUNS / shared_id / 'result.json'
        if result_path.exists():
            try:
                recovered_result = validate_result(json.loads(result_path.read_bytes()), lifecycle)
                recovery_reason += ' Valid completed verification artifact retained as diagnostic evidence.'
            except Exception as exc:
                recovery_reason += ' Partial/invalid result retained as raw bytes: ' + type(exc).__name__ + ': ' + str(exc)
        lifecycle['completion'] = completion(lifecycle, reason=recovery_reason, result=recovered_result,
            cpu=0 if never_launched else None, wall=0 if never_launched else None, rss=0 if never_launched else None)
        lifecycle['phase'] = 'completed'
        atomic_json(path, lifecycle)
    return finalize(registry, path, lifecycle)


def supervise(arguments):
    registry = TrialRegistry(ROOT / 'evidence/trials')
    with group_lock():
        if len(arguments) == 2 and arguments[0] == '--recover':
            return recover(registry, arguments[1])
        if len(arguments) != 1:
            raise ValueError('supply one frozen relative batch-contract path or --recover SHARED_ID')
        batch_path = arguments[0]
        batch_raw,batch = load_batch_snapshot(batch_path)
        families = {s['family'] for s in batch['families']}
        for path in RUNS.glob('*.json'):
            old = json.loads(path.read_bytes())
            if old['phase'] != 'finalized':
                raise RuntimeError('unresolved shared execution; use owning command: ' + recovery_command(old))
        if any(a['family'] in families and a['status'] == 'running' for a in registry.state()['attempts'].values()):
            raise RuntimeError('a participating family has an unresolved attempt; reconcile before any launch')
        become_subreaper()
        registrations = [json.loads(package_path(s['registration_path']).read_bytes()) for s in batch['families']]
        validate_registrations(registry, registrations, batch)
        cpu_limit, hard_cpu, memory_limit, wall_limit = batch_resources(batch)
        frozen_resources = resource_configuration(batch)
        snapshot = code_snapshot(ROOT, registry.artifacts)
        manifest = registry.artifacts.read_json(snapshot)['manifest']
        preflight = retain_preflight(registry, registrations, manifest, batch, batch_path,batch_raw)
        shared_id = uuid4().hex
        configuration = {'shared_execution_id': shared_id, 'supervisor_path': str(Path(__file__).resolve()), 'registrations': registrations, 'preflight': preflight,
                         'worker_launch_token': uuid4().hex,
                         'batch_id': batch['id'], 'batch_path': batch_path,
                         'batch_contract': asdict(registry.artifacts.put_bytes(batch_raw, kind='engineering_batch_contract')),
                         'supervisor': preflight['supervisor'],
                         'suite': 'all', **frozen_resources,
                         'accounting': 'One physical execution; identical observed worker use charged to every family, never summed.'}
        lifecycle = {'shared_execution_id': shared_id, 'supervisor_path': str(Path(__file__).resolve()), 'phase': 'reserving', 'members': [],
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
        cpu_baseline = before.ru_utime + before.ru_stime
        cpu_peak, cpu_samples, guard_reason = 0.0, 0, None
        rss_peak = 0
        reason = 'worker did not produce a successful result'
        try:
            for registration in registrations:
                trial = registry.register(name='Combined registered engineering and complete existing regression suite',
                    family=registration['family'], stage='engineering', configuration=configuration,
                    code_hash=digest(manifest), data_hashes={'independent_golden': registration['golden']['sha256']},
                    fold_version='no-market-fit', target_version=batch['id'])
                registry.start(trial, cpu_reservation_seconds=cpu_limit)
                lifecycle['members'] = members_for(registry, shared_id)
                atomic_json(path, lifecycle)
            lifecycle['phase'] = 'launch_pending'
            lifecycle['launch_start_bound'] = {'boot_id': boot_identity(),
                'start_ticks': int(float(Path('/proc/uptime').read_text().split()[0]) * os.sysconf('SC_CLK_TCK'))}
            atomic_json(path, lifecycle)
            with (folder / 'stdout.log').open('wb') as output, (folder / 'stderr.log').open('wb') as errors:
                process = subprocess.Popen(worker_arguments(folder / 'result.json', configuration),
                                           cwd=ROOT, stdout=output, stderr=errors, start_new_session=True,
                                           env={**os.environ, WORKER_TOKEN_ENV: configuration['worker_launch_token']})
                lifecycle.update(phase='running', pid=process.pid, worker_start_identity=process_identity(process.pid))
                atomic_json(path, lifecycle)
                while process.poll() is None:
                    reap_group_children(process.pid, process.pid)
                    cpu_peak = max(cpu_peak, aggregate_group_cpu(process.pid, cpu_baseline))
                    cpu_samples += 1
                    rss_peak = max(rss_peak, sum(row['rss_bytes'] for row in group_rows({process.pid}).values()))
                    if cpu_peak >= cpu_limit or rss_peak >= memory_limit or time.monotonic() - started >= wall_limit:
                        guard_reason = (f'aggregate process-group CPU reached the frozen {cpu_limit}-second limit'
                                        if cpu_peak >= cpu_limit else 'sampled group RSS reached the frozen 4-GiB limit'
                                        if rss_peak >= memory_limit else f'registered {wall_limit}-second wall limit reached')
                        os.killpg(process.pid, signal.SIGKILL)
                        returncode = process.wait()
                        break
                    time.sleep(0.05)
                if returncode is None:
                    returncode = process.returncode
                lifecycle['cpu_guard'] = {'sampled_peak_cpu_seconds': cpu_peak, 'samples': cpu_samples,
                    'sample_interval_seconds': 0.05, 'soft_limit_seconds': cpu_limit, 'termination': guard_reason,
                    'sampled_peak_group_rss_bytes': rss_peak,
                    'basis': 'supervisor reaped CPU plus group self/reaped CPU, parents read before children; scopes never summed twice'}
            if (folder / 'result.json').exists():
                acknowledgement = folder / 'worker-started.json'
                if acknowledgement.exists():
                    lifecycle['worker_resource_acknowledgement'] = json.loads(acknowledgement.read_bytes())
                    atomic_json(path, lifecycle)
                result = validate_result(json.loads((folder / 'result.json').read_bytes()), lifecycle)
                success = (guard_reason is None and returncode == 0 and result['success'] and code_manifest(ROOT) == manifest
                           and result['code_snapshot'] == asdict(snapshot))
                status = 'succeeded' if success else 'failed'
                reason = 'Registered combined assertions passed.' if success else guard_reason or 'Assertion failure or code identity changed; output retained.'
            elif guard_reason is not None:
                reason = guard_reason
            elif returncode is not None and reason == 'worker did not produce a successful result':
                reason = f'worker exited {returncode} without a complete result'
        except BaseException as exc:
            reason = f'{type(exc).__name__}: {exc}'
            success, status = False, 'interrupted'
            result = None
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL); returncode = process.wait()
        finally:
            lifecycle['cpu_guard'] = {'sampled_peak_cpu_seconds': cpu_peak, 'samples': cpu_samples,
                'sample_interval_seconds': 0.05, 'soft_limit_seconds': cpu_limit, 'termination': guard_reason,
                    'sampled_peak_group_rss_bytes': rss_peak,
                'basis': 'supervisor reaped CPU plus group self/reaped CPU, parents read before children; scopes never summed twice'}
            for s, handler in prior_handlers.items():
                signal.signal(s, handler)
        if process is not None:
            # Also stop adopted forks left after a normal or failed leader exit.
            if live_groups({process.pid}):
                os.killpg(process.pid, signal.SIGKILL)
                success, status, result = False, 'interrupted', None
                reason = 'worker left live descendants; group terminated after leader exit'
            deadline = time.monotonic() + 5
            while group_rows({process.pid}) and time.monotonic() < deadline:
                reap_group_children(process.pid, process.pid)
                time.sleep(0.01)
            if live_groups({process.pid}):
                atomic_json(path, lifecycle)
                raise RuntimeError('worker descendants remain executable; retain recovery gate: ' + recovery_command(lifecycle))
            reap_group_children(process.pid, process.pid)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        final_cpu=max(cpu_peak,after.ru_utime+after.ru_stime-cpu_baseline) if process is not None else 0
        final_wall=time.monotonic()-started if process is not None else 0
        final_rss=max(rss_peak,after.ru_maxrss*1024) if process is not None else 0
        final_error=final_resource_error(final_cpu,final_wall,final_rss,configuration)
        if final_error is not None:
            success,status,reason=False,'failed',final_error
        lifecycle['members'] = members_for(registry, shared_id)
        lifecycle['completion'] = completion(lifecycle, success=success, status=status, reason=reason,
            cpu=final_cpu,wall=final_wall,rss=final_rss,result=result,returncode=returncode)
        lifecycle['phase'] = 'completed'
        atomic_json(path, lifecycle)
        return finalize(registry, path, lifecycle)


if __name__ == '__main__':
    raise SystemExit(worker(sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else None)
                     if len(sys.argv) in (3, 4) and sys.argv[1] == '--worker' else supervise(sys.argv[1:]))
