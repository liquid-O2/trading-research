"""One registered combined verification, supervised with process resource limits."""

from dataclasses import asdict
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time

from trading_research.operations.artifacts import (
    ArtifactStore, artifact_ref, code_manifest, code_snapshot, digest,
)
from trading_research.operations.trials import TrialRegistry


ROOT = Path(__file__).resolve().parents[1]


def worker(result_path):
    resource.setrlimit(resource.RLIMIT_CPU, (180, 190))
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024 ** 3, 4 * 1024 ** 3))
    signal.alarm(240)
    from trading_research.verify import run
    result = run('all', evidence_root=ROOT / 'evidence',
                 plan_root=ROOT.parent / 'planning/trading-model', require_traceability=True)
    Path(result_path).write_text(json.dumps(result, indent=2) + '\n')
    return 0 if result['success'] else 1


def supervise():
    registry = TrialRegistry(ROOT / 'evidence/trials')
    registration = json.loads((ROOT / 'reports/f04-replay-registration.json').read_text())
    protocol_ref = artifact_ref(registration['protocol'])
    golden_ref = artifact_ref(registration['golden'])
    # The expected equations and scope stay exactly as registered before implementation.
    for relative, ref in (('validation/F04_REPLAY_PROTOCOL.md', protocol_ref),
                          ('tests/golden/f04-replay.json', golden_ref)):
        if (ROOT / relative).read_bytes() != registry.artifacts.read(ref):
            raise RuntimeError('registered protocol or independent expectation bytes changed')
    review = registry.artifacts.put_bytes((ROOT / 'validation/F04_REPLAY_BATCH_REVIEW.md').read_bytes(), kind='implementation_review')
    harness = registry.artifacts.put_bytes(Path(__file__).read_bytes(), kind='verification_supervisor_source')
    snapshot = code_snapshot(ROOT, registry.artifacts)
    manifest = registry.artifacts.read_json(snapshot)['manifest']
    configuration = {'protocol': asdict(protocol_ref), 'golden': asdict(golden_ref),
                     'source_cases': registration['source_cases'], 'review': asdict(review), 'supervisor': asdict(harness), 'suite': 'all',
                     'cpu_reservation_seconds': 180, 'cpu_hard_seconds': 190,
                     'address_space_bytes': 4 * 1024 ** 3, 'wall_limit_seconds': 240}
    trial = registry.register(name='F04 availability merge, optional scheduling and existing combined regression suite',
        family='F04-availability-scheduler-reference-v1', stage='engineering', configuration=configuration,
        code_hash=digest(manifest), data_hashes={'independent_golden': golden_ref.sha256},
        fold_version='no-market-fit', target_version='fixed-availability-ties-and-scheduler-lineage-v1')
    attempt = registry.start(trial, cpu_reservation_seconds=180)
    started = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    result = None
    status = 'failed'
    reason = 'worker did not produce a successful result'
    output = ''
    errors = ''
    returncode = None
    process = None
    result_refs = []
    try:
        with tempfile.TemporaryDirectory(prefix='f04-verification-') as temporary:
            result_path = Path(temporary) / 'result.json'
            process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--worker', str(result_path)],
                                       cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       start_new_session=True, text=True)
            try:
                output, errors = process.communicate(timeout=240)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                output, errors = process.communicate()
                reason = 'supervisor enforced the registered 240-second wall limit'
            returncode = process.returncode
            if result_path.exists():
                result = json.loads(result_path.read_text())
                source_store = ArtifactStore(ROOT / 'evidence/artifacts')
                for field in ('artifact', 'code_snapshot'):
                    ref = artifact_ref(result[field])
                    copied = registry.artifacts.put_bytes(source_store.read(ref), kind=ref.kind)
                    result_refs.append(asdict(copied))
                success = (returncode == 0 and result['success'] and code_manifest(ROOT) == manifest
                           and result['code_snapshot'] == asdict(snapshot))
                status = 'succeeded' if success else 'failed'
                reason = ('Combined registered engineering assertions passed under the process limits.' if success
                          else 'Combined assertion failure or code identity changed; retain the full result.')
            elif returncode is not None and reason == 'worker did not produce a successful result':
                reason = f'worker exited {returncode} without a complete result'
    except BaseException as exc:
        reason = f'{type(exc).__name__}: {exc}'
        if process is not None and process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
            output, errors = process.communicate()
            returncode = process.returncode
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = (after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime)
    wall = time.monotonic() - started
    peak_rss = after.ru_maxrss * 1024
    report = {'success': status == 'succeeded', 'trial_id': trial, 'attempt_id': attempt,
              'configuration': configuration, 'code_snapshot': asdict(snapshot), 'result': result,
              'worker_exit_code': returncode, 'reason': reason, 'stdout': output, 'stderr': errors,
              'cpu_seconds': cpu, 'wall_seconds': wall, 'peak_rss_bytes': peak_rss,
              'resource_basis': 'supervised worker and reaped descendants; RUSAGE_CHILDREN',
              'market_tape_reads': 0, 'economic_runs': 0,
              'limitations': ['Fixed synthetic assertions do not admit a dated historical contract cohort.',
                              'No external side-effect, profitability, all-consumer P5 or future P7 claim.']}
    ref = registry.artifacts.put_json(report, kind='supervised_engineering_verification')
    registry.finish(attempt, status=status, cpu_seconds=cpu, wall_seconds=wall, peak_rss_bytes=peak_rss,
                    reason=reason, result_artifacts=(*result_refs, asdict(ref)))
    summary = {'success': report['success'], 'trial_id': trial, 'attempt_id': attempt, 'artifact': asdict(ref),
               'report': str(registry.artifacts.path(ref)), 'verification': result, 'reason': reason,
               'cpu_seconds': cpu, 'wall_seconds': wall, 'peak_rss_bytes': peak_rss}
    (ROOT / 'reports' / f'f04-replay-verification-{attempt[:12]}.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))
    return 0 if report['success'] else 1


if __name__ == '__main__':
    raise SystemExit(worker(sys.argv[2]) if len(sys.argv) == 3 and sys.argv[1] == '--worker' else supervise())
