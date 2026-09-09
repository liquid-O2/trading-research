"""One durable, resource-bounded full-suite execution for four frozen families.

Use --recover SHARED_ID to finish an interrupted lifecycle without rerunning tests.
Assertion output and completion payloads survive worker/supervisor termination.
"""
from contextlib import contextmanager
from dataclasses import asdict
import ast
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

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / 'evidence/trials/shared_foundations'
SPECS = (
    ('f09', 'F09-shared-bar-reference-v1', 'expected_cases', 'id', 'id', 'self',
     ('tests.test_shared_bars',)),
    ('f10', 'F10-object-lineage-engineering-v1', 'case_proposals', 'id', 'case_id', 'source_case_id',
     ('tests.test_object_graph',)),
    ('f11', 'F11-artifact-closure-engineering-v1', 'proposed_cases', 'case_id', 'id', 'source_preparation_cases',
     ('tests.test_artifact_graph',)),
    ('f12', 'F12-arrival-trace-engineering-v1', 'case_proposals', 'case_id', 'case_id', 'source_case',
     ('tests.test_arrival',)),
)
FAMILIES = {row[1] for row in SPECS}

REQUIRED_REVIEWS = {
    'reports/f09-independent-review.json': 'findings',
    'reports/f09-root-static-review.json': 'findings',
    'reports/f10-case-test-map.json': 'static_review.findings',
    'reports/f11-initial-static-review.json': 'findings',
    'reports/f11-independent-review.json': 'additional_findings',
    'reports/f12-initial-static-review.json': 'findings',
    'reports/f09-f12-orchestration-review.json': 'findings',
}
PRE_REPAIR_REVIEW_PATH = 'reports/f09-f12-pre-repair-review.json'
PRE_REPAIR_REVIEW_SHA256 = '368c6373fd4de1a9d92bce73488667815f47d998a3ed0187ebf73bd7ad4b4f12'
REGISTRATION_PATHS = {
    'f09': 'reports/f09-shared-bar-registration.json',
    'f10': 'reports/f10-object-lineage-registration.json',
    'f11': 'reports/f11-artifact-closure-registration.json',
    'f12': 'reports/f12-arrival-trace-registration.json',
}


def local_identity(relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts or str(path) != relative:
        raise ValueError('retained support path must be canonical and relative')
    raw = (ROOT / path).read_bytes()
    return {'path': relative, 'sha256': hashlib.sha256(raw).hexdigest(), 'size_bytes': len(raw)}


def validate_review_support(review, store):
    original_raw = (ROOT / PRE_REPAIR_REVIEW_PATH).read_bytes()
    if hashlib.sha256(original_raw).hexdigest() != PRE_REPAIR_REVIEW_SHA256:
        raise ValueError('frozen pre-repair review changed')
    receipt = json.loads(original_raw)
    if (type(receipt) is not dict or set(receipt) != {'artifact', 'code_snapshot', 'findings'}
            or receipt['artifact']['kind'] != 'implementation_review'
            or receipt['code_snapshot']['kind'] != 'code_snapshot'
            or type(receipt['findings']) is not int or receipt['findings'] != 92):
        raise ValueError('frozen pre-repair receipt schema differs')
    original = store.read_json(artifact_ref(receipt['artifact']))
    if original['pre_repair_code_snapshot'] != receipt['code_snapshot']:
        raise ValueError('original review and receipt code snapshot differ')
    if (set(review['required_review_paths']) != set(REQUIRED_REVIEWS)
            or len(review['required_review_paths']) != len(REQUIRED_REVIEWS)
            or review['reviews'] != original['reviews']
            or review['frozen_contracts'] != original['frozen_contracts']):
        raise ValueError('all seven original reviews and frozen contract supports are required exactly')
    rows = review['reviews']
    if len(rows) != len(REQUIRED_REVIEWS) or {r['path'] for r in rows} != set(REQUIRED_REVIEWS):
        raise ValueError('review support omitted, duplicated or substituted')
    findings = {}
    for row in rows:
        raw = (ROOT / row['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['sha256'] or raw != store.read(artifact_ref(row['artifact'])):
            raise ValueError('original reviewer bytes differ from retained input')
        if row['finding_key'] != REQUIRED_REVIEWS[row['path']]:
            raise ValueError('review finding selector differs')
        values = json.loads(raw)
        for part in row['finding_key'].split('.'):
            values = values[part]
        ids = [v['id'] for v in values]
        if (not ids or len(ids) != len(set(ids)) or sorted(ids) != sorted(row['finding_ids'])
                or set(ids) & set(findings)):
            raise ValueError('review finding IDs omitted or duplicated')
        findings.update({v['id']: v for v in values})
    if len(findings) != receipt['findings'] or set(review['dispositions']) != set(findings):
        raise ValueError('dispositions must equal the complete original finding-ID union')
    repair_rows = review['repair_reports']
    if not repair_rows or len({r['path'] for r in repair_rows}) != len(repair_rows):
        raise ValueError('distinct repair support reports required')
    repair_ids, repair_entries = {}, {}
    for row in repair_rows:
        identity = local_identity(row['path'])
        if identity['sha256'] != row['sha256']:
            raise ValueError('repair support bytes changed')
        value = json.loads((ROOT / row['path']).read_bytes())['dispositions']
        ids = list(value) if type(value) is dict else [d['id'] for d in value]
        if len(ids) != len(set(ids)):
            raise ValueError('repair report duplicates a finding disposition')
        entries = value if type(value) is dict else {d['id']: d for d in value}
        repair_ids[row['path']] = set(ids)
        repair_entries[row['path']] = entries
    used = set()
    for id, disposition in review['dispositions'].items():
        support = disposition['repair_report']
        if (disposition['status'] != 'repaired_and_statically_verified'
                or support not in repair_ids or id not in repair_ids[support]
                or repair_entries[support][id].get('status') != 'repaired_and_statically_verified'):
            raise ValueError('finding lacks its explicit retained repair disposition')
        used.add(support)
    if used != set(repair_ids):
        raise ValueError('unused or omitted repair support report')
    return asdict(store.put_bytes(original_raw, kind='implementation_review'))


def retain_mapping_inputs(store, coverage, registration, spec):
    prefix, _, _, _, _, _, modules = spec
    expected_paths = [REGISTRATION_PATHS[prefix], registration['golden_path'], registration['protocol_path'],
                      f'reports/{prefix}-source-preparation.json', f'reports/{prefix}-case-test-map.json',
                      *(m.replace('.', '/') + '.py' for m in modules)]
    expected = [local_identity(path) for path in expected_paths]
    if coverage['inputs'] != expected or coverage['mapping_script'] != local_identity('tools/map_f09_f12.py'):
        raise ValueError('normalizer source or exact normalized input bytes differ')
    source_ref = artifact_ref(registration['source_cases'])
    source = store.read_json(source_ref)
    preparation_ref = artifact_ref(source['preparation_bytes'])
    preparation_raw = store.read(preparation_ref)
    if (ROOT / f'reports/{prefix}-source-preparation.json').read_bytes() != preparation_raw:
        raise ValueError('normalized local preparation differs from frozen source bytes')
    if json.loads(preparation_raw) != source['preparation']:
        raise ValueError('frozen source preparation object differs from its retained exact bytes')
    if (json.loads((ROOT / REGISTRATION_PATHS[prefix]).read_bytes()) != registration
            or coverage['registered_source_cases'] != registration['source_cases']
            or coverage['registered_preparation_bytes'] != source['preparation_bytes']):
        raise ValueError('normalizer input provenance differs from frozen registration')
    return {'inputs': [{'identity': identity,
                       'artifact': asdict(store.put_bytes((ROOT / identity['path']).read_bytes(), kind='mapping_input'))}
                       for identity in expected],
            'registered_source_cases': asdict(source_ref), 'registered_preparation_bytes': asdict(preparation_ref)}


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
        raise ValueError('exactly the four distinct frozen foundation families are required')
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


def case_contract(store, registration, spec):
    """Derive exact golden-to-preparation bindings from retained frozen bytes."""
    prefix, _, case_key, source_id_key, golden_id_key, binding_key, _ = spec
    source = store.read_json(artifact_ref(registration['source_cases']))['preparation'][case_key]
    golden = store.read_json(artifact_ref(registration['golden']))['cases']
    originals = {case[source_id_key]: case for case in source}
    literals = {case[golden_id_key]: case for case in golden}
    if len(originals) != len(source) or len(literals) != len(golden) or not originals or not literals:
        raise ValueError(f'{prefix}: duplicate or empty frozen cases')
    bindings = {}
    for case_id, case in literals.items():
        value = case_id if binding_key == 'self' else case[binding_key]
        ids = value if type(value) is list else ([] if value is None else [value])
        if (any(type(item) is not str or item not in originals for item in ids)
                or len(ids) != len(set(ids))):
            raise ValueError(f'{prefix}: invalid frozen source binding')
        bindings[case_id] = sorted(ids)
    if {item for ids in bindings.values() for item in ids} != set(originals):
        raise ValueError(f'{prefix}: a prepared source case has no frozen assertion')
    return originals, literals, bindings


def validate_coverage(coverage, spec, originals, literals, bindings, methods):
    """All frozen cases require concrete assertions; broader phase gates stay open."""
    prefix, family, *_, modules = spec
    if (coverage['family'] != family or sorted(coverage['test_modules']) != sorted(modules)
            or type(coverage['remaining']) is not list or not coverage['remaining']
            or any(type(value) is not str or not value for value in coverage['remaining'])):
        raise ValueError(f'{prefix}: family, modules or broader remaining gates differ')
    cases = coverage['cases']
    ids = [case['case_id'] for case in cases]
    if len(ids) != len(set(ids)) or set(ids) != set(literals):
        raise ValueError(f'{prefix}: exact mandatory golden coverage differs')
    claimed = set()
    for case in cases:
        selected = case['assertion_ids']
        if (type(selected) is not list or not selected or len(selected) != len(set(selected))
                or not set(selected) <= set(methods)
                or case['source_case_ids'] != bindings[case['case_id']]
                or type(case['remaining']) is not list or not case['remaining']):
            raise ValueError(f'{prefix}: missing, ambiguous or incorrectly bound assertions')
        claimed.update(selected)
    if coverage['additional_assertion_ids'] != sorted(set(methods) - claimed):
        raise ValueError(f'{prefix}: undeclared additional assertion methods')
    expected_source = {source: sorted(case for case, sources in bindings.items() if source in sources)
                       for source in sorted(originals)}
    if coverage['source_case_mapping'] != expected_source:
        raise ValueError(f'{prefix}: prepared source coverage mapping differs')


def retain_preflight(registry, registrations, manifest):
    store = registry.artifacts
    review_path = ROOT / 'reports/f09-f12-batch-review.json'
    review = json.loads(review_path.read_bytes())
    if (review['review_complete_before_repair'] is not True or review['consolidated_repair_passes'] != 1
            or review['repair_status'] != 'complete_static_verification_ready_for_shared_run'
            or review['repaired_code_manifest_sha256'] != digest(manifest)
            or any(d['status'] != 'repaired_and_statically_verified' for d in review['dispositions'].values())):
        raise ValueError('complete review and one verified repair pass must precede execution')
    original_review = validate_review_support(review, store)
    refs = {'pre_repair_review': original_review,
            'normalizer': asdict(store.put_bytes((ROOT / 'tools/map_f09_f12.py').read_bytes(), kind='mapping_normalizer_source')),
            'batch_review': asdict(store.put_bytes(review_path.read_bytes(), kind='implementation_review')),
            'review_text': asdict(store.put_bytes((ROOT / 'validation/F09_F12_BATCH_REVIEW.md').read_bytes(), kind='implementation_review')),
            'recorder': asdict(store.put_bytes((ROOT / 'tools/record_f09_f12.py').read_bytes(), kind='evidence_assembly_script')),
            'reviews': [], 'coverage': {}}
    for identity in [*review['reviews'], *review['repair_reports'], *review['frozen_contracts']]:
        raw = (ROOT / identity['path']).read_bytes()
        ref = store.put_bytes(raw, kind='review_support')
        if ref.sha256 != identity['sha256']:
            raise ValueError('reviewed artifact changed before execution')
        refs['reviews'].append(asdict(ref))
    by_family = {r['family']: r for r in registrations}
    for spec in SPECS:
        prefix, family, *_, modules = spec
        raw = (ROOT / f'reports/{prefix}-implementation-coverage.json').read_bytes()
        coverage = json.loads(raw)
        originals, literals, bindings = case_contract(store, by_family[family], spec)
        methods = static_methods(modules)
        validate_coverage(coverage, spec, originals, literals, bindings, methods)
        mapping_inputs = retain_mapping_inputs(store, coverage, by_family[family], spec)
        refs['coverage'][prefix] = {**mapping_inputs, 'artifact': asdict(store.put_bytes(raw, kind='implementation_case_mapping')),
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
                 'worker_source': str(Path(__file__).resolve()), 'start_identity': process_identity(os.getpid())})
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
    # Verify the reconstructible snapshot bytes, not only a mutable result path.
    if snapshot != ArtifactStore(ROOT / 'evidence/trials/artifacts').read_json(snapshot_ref):
        raise ValueError('worker snapshot bytes differ from the original retained snapshot')
    return result


def finalize(registry, path, lifecycle):
    """A durable completion can be retried even if artifact publication/finish failed."""
    report = lifecycle['completion']
    if report['success'] != (report['status'] == 'succeeded'):
        raise ValueError('success and terminal status must describe one consistent outcome')
    if report['result'] is not None:
        try:
            validate_result(report['result'], lifecycle)
        except Exception as exc:
            # A malformed legacy completion must not permanently strand its
            # reservations. Never rewrite outcomes already terminalized.
            states = registry.state()['attempts']
            if any(states[m['attempt_id']]['status'] != 'running' for m in report['members']):
                raise RuntimeError('accepted evidence changed after partial finalization; restore retained artifacts before recovery') from exc
            report = {**report, 'rejected_result_summary': report['result'], 'result': None,
                      'success': False, 'status': 'interrupted',
                      'reason': report['reason'] + '; invalid result retained separately: ' + type(exc).__name__ + ': ' + str(exc)}
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
    summary_path = ROOT / f'reports/f09-f12-verification-{report["shared_execution_id"][:12]}.json'
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
            'resource_basis': 'Linux process-group self plus reaped-descendant CPU; parent-before-child snapshots avoid duplicate charging; final adopted descendants reaped by supervisor. Unknown hard-crash use charges every reservation.',
            'cpu_guard': lifecycle.get('cpu_guard'), 'worker_start_identity': lifecycle.get('worker_start_identity'),
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
    owner = lifecycle.get('supervisor_path') or lifecycle.get('configuration', {}).get('supervisor_path')
    if owner is None:
        acknowledgement = RUNS / lifecycle['shared_execution_id'] / 'worker-started.json'
        if acknowledgement.exists():
            owner = json.loads(acknowledgement.read_bytes()).get('worker_source')
    if owner is None:
        families = {r['family'] for r in lifecycle.get('configuration', {}).get('registrations', [])}
        if families == FAMILIES:
            owner = str(Path(__file__).resolve())
        elif families == {'F05-canonical-transaction-reference-v1', 'F06-F07-quality-support-reference-v1', 'F08-roll-coordinate-reference-v1'}:
            owner = str(ROOT / 'tools/verify_foundation_extensions.py')
    allowed = {str(ROOT / 'tools/verify_f09_f12.py'), str(ROOT / 'tools/verify_foundation_extensions.py')}
    if owner not in allowed:
        raise ValueError('unresolved lifecycle has an unknown owning supervisor; no worker may launch')
    configuration = lifecycle.get('configuration', {})
    if (configuration.get('supervisor_path', owner) != owner or lifecycle.get('supervisor_path', owner) != owner):
        raise ValueError('lifecycle and configuration supervisor identities disagree')
    expected_families = FAMILIES if owner.endswith('/verify_f09_f12.py') else {
        'F05-canonical-transaction-reference-v1', 'F06-F07-quality-support-reference-v1', 'F08-roll-coordinate-reference-v1'}
    if {r['family'] for r in configuration['registrations']} != expected_families:
        raise ValueError('owning recovery tool does not match retained family membership')
    retained_source = ArtifactStore(ROOT / 'evidence/trials/artifacts').read(artifact_ref(configuration['supervisor']))
    if Path(owner).read_bytes() != retained_source:
        raise ValueError('owning recovery source differs from retained bytes; restore its recorded source before recovery')
    return owner


def recovery_command(lifecycle):
    return shlex.join([sys.executable, owning_supervisor(lifecycle), '--recover', lifecycle['shared_execution_id']])


def _same_process(identity):
    try:
        return process_identity(identity['pid']) == identity
    except (FileNotFoundError, ProcessLookupError):
        return False


def recover(registry, shared_id):
    if len(shared_id) != 32 or any(c not in '0123456789abcdef' for c in shared_id):
        raise ValueError('invalid shared execution identity')
    path = RUNS / f'{shared_id}.json'
    lifecycle = json.loads(path.read_bytes())
    owner = owning_supervisor(lifecycle)
    if owner != str(Path(__file__).resolve()):
        raise RuntimeError('foreign shared lifecycle; use its owning recovery command: ' + recovery_command(lifecycle))
    if 'completion' not in lifecycle:
        target = str(RUNS / shared_id / 'result.json')
        identity = lifecycle.get('worker_start_identity')
        acknowledgement = RUNS / shared_id / 'worker-started.json'
        if acknowledgement.exists():
            handshake = json.loads(acknowledgement.read_bytes())
            if handshake['result_path'] != target or handshake['worker_source'] != owner:
                raise ValueError('worker acknowledgement differs from retained launch')
            recorded = handshake.get('start_identity')
            if recorded is None:
                raise ValueError('legacy current-tool acknowledgement has no start identity; retain manual reconciliation gate')
            if (recorded['pid'] != handshake['pid'] or recorded['pgid'] != handshake['pgid']
                    or recorded['pid'] != recorded['pgid'] or identity is not None and identity != recorded):
                raise ValueError('worker acknowledgement process identity differs')
            identity = recorded
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
                if command[1:] != [b'-u', owner.encode(), b'--worker', target.encode()]:
                    continue
                row_identity = process_identity(int(entry.name))
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
            if _same_process(candidate):
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
        for path in RUNS.glob('*.json'):
            old = json.loads(path.read_bytes())
            if old['phase'] != 'finalized':
                raise RuntimeError('unresolved shared execution; use owning command: ' + recovery_command(old))
        if any(a['family'] in FAMILIES and a['status'] == 'running' for a in registry.state()['attempts'].values()):
            raise RuntimeError('a participating family has an unresolved attempt; reconcile before any launch')
        become_subreaper()
        registrations = [json.loads((ROOT / name).read_bytes()) for name in arguments]
        validate_registrations(registry, registrations)
        snapshot = code_snapshot(ROOT, registry.artifacts)
        manifest = registry.artifacts.read_json(snapshot)['manifest']
        preflight = retain_preflight(registry, registrations, manifest)
        shared_id = uuid4().hex
        configuration = {'shared_execution_id': shared_id, 'supervisor_path': str(Path(__file__).resolve()), 'registrations': registrations, 'preflight': preflight,
                         'supervisor': asdict(registry.artifacts.put_bytes(Path(__file__).read_bytes(), kind='verification_supervisor_source')),
                         'suite': 'all', 'cpu_reservation_seconds': 180, 'cpu_hard_seconds': 190,
                         'address_space_bytes': 4 * 1024**3, 'wall_limit_seconds': 240,
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
        reason = 'worker did not produce a successful result'
        try:
            for registration in registrations:
                trial = registry.register(name='Combined foundation reference and existing regression suite',
                    family=registration['family'], stage='engineering', configuration=configuration,
                    code_hash=digest(manifest), data_hashes={'independent_golden': registration['golden']['sha256']},
                    fold_version='no-market-fit', target_version='fixed-foundation-f09-f12-v1')
                registry.start(trial, cpu_reservation_seconds=180)
                lifecycle['members'] = members_for(registry, shared_id)
                atomic_json(path, lifecycle)
            lifecycle['phase'] = 'launch_pending'
            lifecycle['launch_start_bound'] = {'boot_id': boot_identity(),
                'start_ticks': int(float(Path('/proc/uptime').read_text().split()[0]) * os.sysconf('SC_CLK_TCK'))}
            atomic_json(path, lifecycle)
            with (folder / 'stdout.log').open('wb') as output, (folder / 'stderr.log').open('wb') as errors:
                process = subprocess.Popen([sys.executable, '-u', str(Path(__file__).resolve()), '--worker', str(folder / 'result.json')],
                                           cwd=ROOT, stdout=output, stderr=errors, start_new_session=True)
                lifecycle.update(phase='running', pid=process.pid, worker_start_identity=process_identity(process.pid))
                atomic_json(path, lifecycle)
                while process.poll() is None:
                    reap_group_children(process.pid, process.pid)
                    cpu_peak = max(cpu_peak, aggregate_group_cpu(process.pid, cpu_baseline))
                    cpu_samples += 1
                    if cpu_peak >= 180 or time.monotonic() - started >= 240:
                        guard_reason = ('aggregate process-group CPU reached the frozen 180-second limit'
                                        if cpu_peak >= 180 else 'registered 240-second wall limit reached')
                        os.killpg(process.pid, signal.SIGKILL)
                        returncode = process.wait()
                        break
                    time.sleep(0.05)
                if returncode is None:
                    returncode = process.returncode
                lifecycle['cpu_guard'] = {'sampled_peak_cpu_seconds': cpu_peak, 'samples': cpu_samples,
                    'sample_interval_seconds': 0.05, 'soft_limit_seconds': 180, 'termination': guard_reason,
                    'basis': 'supervisor reaped CPU plus group self/reaped CPU, parents read before children; scopes never summed twice'}
            if (folder / 'result.json').exists():
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
                'sample_interval_seconds': 0.05, 'soft_limit_seconds': 180, 'termination': guard_reason,
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
        lifecycle['members'] = members_for(registry, shared_id)
        lifecycle['completion'] = completion(lifecycle, success=success, status=status, reason=reason,
            cpu=max(cpu_peak, after.ru_utime + after.ru_stime - cpu_baseline) if process is not None else 0,
            wall=time.monotonic() - started if process is not None else 0,
            rss=after.ru_maxrss * 1024 if process is not None else 0, result=result, returncode=returncode)
        lifecycle['phase'] = 'completed'
        atomic_json(path, lifecycle)
        return finalize(registry, path, lifecycle)


if __name__ == '__main__':
    raise SystemExit(worker(sys.argv[2]) if len(sys.argv) == 3 and sys.argv[1] == '--worker' else supervise(sys.argv[1:]))
