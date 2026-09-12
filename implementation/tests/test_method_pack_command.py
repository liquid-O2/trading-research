"""Public method-pass behavior against disposable episode and data fixtures."""

from copy import deepcopy
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from trading_research.research.method_pack.evidence import fixture_document, parse_manifest, score_episode, SchemaError
from trading_research.research.method_pack.protocol import jsonable

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / 'implementation/tools/run_phase1_objects.py'


def m01_values():
    base = 1_768_500_000_000_000_000
    at = lambda minute: base + minute * 60_000_000_000
    return dict(branch='judas_reversal', side='short', instrument_id='NQ-test',
                range_frozen=True, context_fixed=True, location_touched=True,
                source_confirmation=True, risk_defined=True, objective_fixed=True,
                range_known_at=at(0), context_at=at(20), touch_at=at(41), sweep_at=at(41),
                confirm_at=at(43), decision_at=at(44), reversal_context=True,
                edge_swept=True, source_time_window=True, objective_is_opposing_draw=True,
                range_L=Decimal('100'), range_H=Decimal('120'), sweep_high=Decimal('121'),
                stop_px=Decimal('122'), objective_px=Decimal('100'))


def contemporary_document(fid='episode-1'):
    doc = fixture_document('JJ-TBR', 'sequence', fid, m01_values())
    for records in ('candidates', 'assertions', 'evidence'):
        for record in doc[records]:
            record['evidence_mode'] = 'supplied_contemporaneous'
    doc['candidates'][0]['cohort_id'] = 'supplied-test'
    return doc


class EpisodeBindingTests(unittest.TestCase):
    def test_bound_sequence_pass_and_real_identity_failure(self):
        doc = contemporary_document()
        candidates, objects, assertions, evidence = parse_manifest(doc, 'JJ-TBR')
        scored = score_episode(candidates['episode-1'], objects, assertions, evidence)
        self.assertEqual(scored['verdict'], 'pass')
        evidence['episode-1:e:source_confirmation']['band_id'] = 'different-range'
        scored = score_episode(candidates['episode-1'], objects, assertions, evidence)
        self.assertEqual(scored['verdict'], 'fail')
        self.assertEqual(scored['base_ok'], False)
        self.assertTrue(any(h['kind'] == 'identity' for h in scored['holes']))

    def test_late_evidence_cannot_be_hidden_by_earlier_assertion(self):
        doc = contemporary_document()
        doc['evidence'][0]['known_at'] = doc['candidates'][0]['decision_at'] + 1
        candidates, objects, assertions, evidence = parse_manifest(doc, 'JJ-TBR')
        scored = score_episode(candidates['episode-1'], objects, assertions, evidence)
        self.assertEqual(scored['verdict'], 'fail')
        self.assertGreater(scored['detected_causal_violations'], 0)

    def test_context_must_exist_at_context_stage_even_before_entry(self):
        doc = contemporary_document()
        ev = next(e for e in doc['evidence'] if e['evidence_id'].endswith(':context_fixed'))
        ev['known_at'] = doc['candidates'][0]['decision_at'] - 1
        candidates, objects, assertions, evidence = parse_manifest(doc, 'JJ-TBR')
        scored = score_episode(candidates['episode-1'], objects, assertions, evidence)
        self.assertEqual(scored['verdict'], 'fail')
        self.assertGreater(scored['detected_causal_violations'], 0)

    def test_missing_required_confirmation_is_unknown(self):
        doc = contemporary_document()
        del doc['candidates'][0]['operands']['source_confirmation']
        candidates, objects, assertions, evidence = parse_manifest(doc, 'JJ-TBR')
        scored = score_episode(candidates['episode-1'], objects, assertions, evidence)
        self.assertEqual(scored['verdict'], 'unknown')
        self.assertIn('HOLE:O056:source_confirmation', scored['hole_ids'])

    def test_naked_boolean_and_unknown_producer_are_schema_errors(self):
        doc = contemporary_document()
        doc['candidates'][0]['operands']['source_confirmation'] = True
        with self.assertRaises(SchemaError):
            parse_manifest(doc, 'JJ-TBR')
        doc = contemporary_document()
        doc['objects'][0]['recipe_id'] = 'O999'
        with self.assertRaises(SchemaError):
            parse_manifest(doc, 'JJ-TBR')

    def test_retrospective_proof_is_rejected_from_contemporary_cohort(self):
        doc = contemporary_document()
        doc['evidence'][0]['evidence_mode'] = 'source_illustration'
        candidates, objects, assertions, evidence = parse_manifest(doc, 'JJ-TBR')
        scored = score_episode(candidates['episode-1'], objects, assertions, evidence)
        self.assertEqual(scored['verdict'], 'fail')
        self.assertGreater(scored['rejected_proxy_attempts'], 0)


class MethodPassCommandTests(unittest.TestCase):
    def run_pass(self, directory, method='JJ-TBR', episodes=None, version='method-pack-v1'):
        data = Path(directory) / 'data'
        data.mkdir(exist_ok=True)
        cmd = [sys.executable, str(RUNNER), 'method-pass', '--method', method,
               '--scope', 'acquired', '--data-root', str(data),
               '--report-root', str(Path(directory) / 'reports'), '--formula-version', version]
        if episodes:
            cmd += ['--episodes', str(episodes)]
        return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)

    def test_m01_command_writes_verified_empty_discovery_and_all_branches(self):
        with tempfile.TemporaryDirectory() as directory:
            run = self.run_pass(directory)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads((Path(directory) / 'reports/jj-tbr.json').read_text())
            self.assertEqual(report['scope']['candidate_discovery'], 'hole')
            self.assertEqual(report['summary']['N'], 0)
            self.assertIsNone(report['summary']['rate'])
            self.assertIsNone(report['summary']['interval'])
            self.assertEqual(len(report['branches']), 8)
            self.assertEqual(report['status'], 'source_hole')
            self.assertEqual(report['years'], {})
            for name, item in report['artifacts'].items():
                raw = Path(item['path']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), item['sha256'], name)
            from trading_research.research.method_pack.pass_runner import validate_report
            fixtures = json.loads(Path(report['artifacts']['fixtures.json']['path']).read_text())
            omitted_method = [row for row in fixtures if not row['id'].startswith('M01-')]
            errors = validate_report(report, omitted_method, [])
            self.assertIn('missing printed method fixture M01-F1', errors)
            self.assertIn('missing printed method fixture M01-F2', errors)
            self.assertIn('missing printed method fixture M01-F3', errors)
            self.assertIn('missing M01 late mutation', errors)
            self.assertIn('missing M01 missing mutation', errors)
            self.assertIn('missing M01 identity mutation', errors)
            self.assertEqual(Path(report['artifacts']['candidates.jsonl']['path']).read_text(), '')
            self.assertTrue(run.stdout.startswith('method | predicate | n | rate | interval | year split | status | report path\n'))
            self.assertEqual(self.run_pass(directory).returncode, 0)

    def test_supplied_attempts_reconcile_without_entering_discovery(self):
        with tempfile.TemporaryDirectory() as directory:
            docs = [contemporary_document(f'episode-{i}') for i in range(3)]
            next(a for a in docs[1]['assertions'] if a['field'] == 'source_confirmation')['value'] = False
            for ev in docs[1]['evidence']:
                ev['payload']['source_confirmation'] = False
            del docs[2]['candidates'][0]['operands']['source_confirmation']
            document = docs[0]
            for addition in docs[1:]:
                for key in ('candidates', 'objects', 'assertions', 'evidence'):
                    document[key].extend(addition[key])
            path = Path(directory) / 'episodes.json'
            path.write_text(json.dumps(jsonable(document)))
            run = self.run_pass(directory, episodes=path)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads((Path(directory) / 'reports/jj-tbr.json').read_text())
            self.assertEqual(report['summary']['N'], 0)
            summary = next(s for s in report['summaries'] if s['cohort'] == 'supplied-test')
            self.assertEqual([summary[k] for k in ('p', 'f', 'u', 'n', 'N')], [1, 1, 1, 2, 3])
            self.assertEqual(summary['rate_exact'], [1, 2])
            self.assertEqual(summary['interval_exact'], [[1, 3], [2, 3]])
            self.assertEqual(sum(y['N'] for y in summary['years'].values()), 3)

    def test_bad_cli_or_manifest_exits_two(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(self.run_pass(directory, method='MADE-UP').returncode, 2)
            self.assertEqual(self.run_pass(directory, version='stale').returncode, 2)
            path = Path(directory) / 'bad.json'
            path.write_text('{"source_confirmation": true}')
            self.assertEqual(self.run_pass(directory, episodes=path).returncode, 2)

    def test_distinct_instruments_and_versions_keep_separate_denominators(self):
        with tempfile.TemporaryDirectory() as directory:
            documents = [contemporary_document(f'partition-{i}') for i in range(3)]
            for records in ('candidates', 'objects', 'assertions', 'evidence'):
                for record in documents[1][records]:
                    record['instrument_id'] = 'ES-test'
            for records in ('objects', 'assertions', 'evidence'):
                for record in documents[2][records]:
                    record['source_version'] = 'another-source-version'
            document = documents[0]
            for addition in documents[1:]:
                for key in ('candidates', 'objects', 'assertions', 'evidence'):
                    document[key].extend(addition[key])
            path = Path(directory) / 'episodes.json'
            path.write_text(json.dumps(jsonable(document)))
            run = self.run_pass(directory, episodes=path)
            self.assertEqual(run.returncode, 0, run.stderr)
            report = json.loads((Path(directory) / 'reports/jj-tbr.json').read_text())
            supplied = [row for row in report['summaries'] if row['cohort'] == 'supplied-test']
            self.assertEqual(len(supplied), 3)
            self.assertEqual([row['N'] for row in supplied], [1, 1, 1])


if __name__ == '__main__':
    unittest.main()
