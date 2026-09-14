"""Review-only counterexamples; never edits accepted artifacts or the pinned suite."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('/workspace')
PYTHON = ROOT / 'implementation/.venv/bin/python'
CLI = ROOT / 'implementation/tools/verify_research_release.py'
GRAPH = ROOT / 'planning/research-program/TASK_GRAPH.json'


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True, indent=2, allow_nan=False) + '\n')
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--p15-00', type=Path, required=True)
    ap.add_argument('--subphase', type=Path, required=True)
    ap.add_argument('--review', type=Path, required=True)
    ap.add_argument('--output-root', type=Path, required=True)
    args = ap.parse_args()
    out = args.output_root
    out.mkdir(parents=True, exist_ok=False)
    task = read(args.p15_00)
    review = read(args.review)
    entries = {Path(item['path']).name: item for item in task['artifact_manifest']}
    results = []

    def run(case, expected, command, description):
        argv = [str(PYTHON), str(CLI), *map(str, command)]
        p = subprocess.run(argv, cwd=ROOT / 'implementation', text=True, capture_output=True, timeout=60)
        row = {'id': case, 'description': description, 'expected_exit': expected,
               'actual_exit': p.returncode, 'passed': p.returncode == expected,
               'argv': argv, 'stdout': p.stdout, 'stderr': p.stderr}
        results.append(row)
        write(out / case / 'RESULT.json', row)
        print(case, 'expected', expected, 'actual', p.returncode, flush=True)

    def run_review(case, mutation, description):
        doc = copy.deepcopy(review)
        mutation(doc)
        path = write(out / case / 'GATE_REVIEW.json', doc)
        run(case, 2, ['subphase', '--receipt', args.subphase, '--gate-review', path], description)

    def run_task(case, documents, description, receipt_updates=None, matrix_mutator=None):
        r = copy.deepcopy(task)
        if receipt_updates:
            r.update(receipt_updates)
        replacements = {}
        for name, document in documents.items():
            new_path = write(out / case / name, document)
            replacements[entries[name]['path']] = new_path
        matrix = copy.deepcopy(read(entries['EVIDENCE_MATRIX.json']['path']))
        for check in matrix['checks']:
            for item in check['evidence']:
                if item['path'] in replacements:
                    item['path'] = str(replacements[item['path']])
                    item['sha256'] = sha(item['path'])
        if matrix_mutator:
            matrix_mutator(matrix)
        replacements[entries['EVIDENCE_MATRIX.json']['path']] = write(out / case / 'EVIDENCE_MATRIX.json', matrix)
        for entry in r['artifact_manifest']:
            if entry['path'] in replacements:
                path = replacements[entry['path']]
                entry.update(path=str(path), sha256=sha(path), bytes=path.stat().st_size)
        path = write(out / case / 'TASK_RECEIPT.json', r)
        run(case, 2, ['task', '--receipt', path], description)

    run('valid_task_control', 0, ['task', '--receipt', args.p15_00], 'Unmodified actual P15-00 receipt.')
    run('valid_review_control', 0, ['subphase', '--receipt', args.subphase, '--gate-review', args.review], 'Unmodified actual v2 candidate and review.')

    path = write(out / 'review_nonobject' / 'GATE_REVIEW.json', [])
    run('review_nonobject', 2, ['subphase', '--receipt', args.subphase, '--gate-review', path], 'Review is a JSON list with no review fields.')

    forged_results = write(out / 'review_null_cases' / 'INDEPENDENT_RESULTS.json', {
        'status': 'pass', 'cases': [None] * 27,
        'input_hashes': {'arbitrary_candidate_key': sha(args.subphase), 'arbitrary_graph_key': sha(GRAPH)},
    })
    run_review('review_null_cases', lambda d: d['independent_suite'].update(results_path=str(forged_results)),
               'Results have 27 null cases, no harness identity, arbitrary input keys, and disagree with the declared results SHA256.')

    def erase_bindings(d):
        for key in ('code_snapshots', 'evidence_matrices', 'graph', 'commands', 'reviewed_at', 'reviewer'):
            d.pop(key, None)
        d['subphase_id'] = 'no-such-subphase'
        d['reviewed_task_ids'] = []
    run_review('review_missing_bindings', erase_bindings,
               'Review lacks code, matrix, graph, command and reviewer bindings; substitutes an unknown subphase and no reviewed tasks.')

    def failed_matrix(d):
        for check in d['checks']:
            check.update(status='fail', evidence=[], code_refs=[], test_nodeids=[], command_indices=[])
    run_task('matrix_failed_checks', {}, 'All required matrix checks explicitly fail and contain no evidence while receipt acceptance flags remain true.', matrix_mutator=failed_matrix)

    def fictitious_refs(d):
        for check in d['checks']:
            for ref in check['code_refs']:
                ref['symbol'] = 'definitely_nonexistent_review_probe_symbol'
            check['test_nodeids'] = ['implementation/tests/rule_discovery/test_p15_00.py::test_definitely_nonexistent_review_probe']
            for evidence in check['evidence']:
                evidence['selector'] = '/definitely_nonexistent_review_probe_pointer'
    run_task('matrix_nonexistent_references', {}, 'Passing matrix rows cite nonexistent symbols, test node IDs and evidence pointers; all artifact file hashes remain valid.', matrix_mutator=fictitious_refs)

    code = read(entries['CODE_SNAPSHOT.json']['path'])
    target = 'implementation/src/trading_research/research/rule_discovery/baseline_manifest.py'
    code['files'][target] = '0' * 64
    draft = read(entries['DRAFT_MANIFEST.json']['path'])
    draft['code_sha256'] = canonical_sha(code)
    run_task('code_false_file_hash', {'CODE_SNAPSHOT.json': code, 'DRAFT_MANIFEST.json': draft},
             'Declared source hash is all zeroes; receipt, draft, run ID, artifact hashes and evidence-file hashes are rebound consistently. Relocated snapshot has no code copies.',
             receipt_updates={'code_sha256': canonical_sha(code), 'run_id': canonical_sha(draft)[:16]})

    plan = read(entries['PLAN_SNAPSHOT.json']['path'])
    plan['snapshot_paths'] = {}
    run_task('plan_no_preserved_copies', {'PLAN_SNAPSHOT.json': plan}, 'Plan files retain valid claimed digests but snapshot_paths is empty and the relocated snapshot has no preserved plan copies.')

    wrong_schema = {'schema_version': 'research-wrong-v900', 'unrelated': True}
    run_task('artifact_wrong_schema', {'SCHEMA_EXAMPLES.json': wrong_schema}, 'SCHEMA_EXAMPLES is an unrelated unsupported schema; manifest and matrix hashes are refreshed but its declared schema is unchanged.')

    leaf_file = write(out / 'lineage-evidence.json', {'records': [{'row_id': 'real-row', 'value': 1}]})
    def lineage(case, leaf, expected, description):
        doc = {'schema_version': 'research-lineage-manifest-v1', 'records': [{
            'issue_at_ns': 10, 'decision_at_ns': 10, 'features': [{'evidence': [leaf]}],
        }]}
        path = write(out / case / 'LINEAGE_MANIFEST.json', doc)
        run(case, expected, ['lineage', '--manifest', path], description)
    valid_leaf = {'artifact_path': str(leaf_file), 'artifact_sha256': sha(leaf_file), 'row_ids': ['real-row'], 'available_at_ns': 5, 'event_at_ns': 5}
    lineage('lineage_valid_control', valid_leaf, 0, 'Existing evidence artifact and row available before the root cutoff.')
    lineage('lineage_late_control', {**valid_leaf, 'available_at_ns': 100}, 2, 'An explicit late availability clock must be rejected.')
    lineage('lineage_missing_clock_and_path', {'artifact_sha256': sha(leaf_file), 'row_ids': ['no-such-row'], 'event_at_ns': 100}, 2,
            'Evidence under root issue 10 omits availability and artifact path and names a nonexistent row at event 100.')
    lineage('lineage_nonexistent_row', {**valid_leaf, 'row_ids': ['no-such-row']}, 2,
            'A real, correctly hashed artifact is paired with a row ID that does not exist.')

    inputs = {str(p): sha(p) for p in [args.p15_00, args.subphase, args.review, GRAPH,
              ROOT / 'implementation/src/trading_research/research/contracts/receipts.py', ROOT / 'tools/check_foundation_adversarial.py']}
    document = {'kind': 'additional-foundation-v2-review', 'input_hashes': inputs, 'cases': results,
                'case_count': len(results), 'matched_expectations': sum(x['passed'] for x in results),
                'invalid_acceptances': sum(x['expected_exit'] == 2 and x['actual_exit'] == 0 for x in results)}
    write(out / 'RESULTS.json', document)
    return 1 if any(not x['passed'] for x in results) else 0


if __name__ == '__main__':
    raise SystemExit(main())
