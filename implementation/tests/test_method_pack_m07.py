import json
from pathlib import Path
import subprocess
import sys

from trading_research.research.method_pack.evidence import parse_manifest, score_episode
from trading_research.research.method_pack.method_slices import m07


def _score(document):
    candidates, objects, assertions, evidence = parse_manifest(document, m07.METHOD)
    return score_episode(next(iter(candidates.values())), objects, assertions, evidence)


def test_m07_printed_cases_use_real_independent_links_and_literal_prices():
    rows = {r['id']: r for r in m07.method_fixtures()}
    assert all(r['status'] == 'pass' for r in rows.values())
    assert rows['M07-F1']['actual_value']['verdict'] == 'pass'
    for fid in ('M07-F2-identity', 'M07-F2-contact', 'M07-F2-stop', 'M07-F2-late-hvn'):
        assert rows[fid]['actual_value']['verdict'] == 'fail'
    identity = rows['M07-F2-identity']
    assertion = next(a for a in identity['inputs']['assertions'] if a['field'] == 'independent_minor_hvn_known')
    assert assertion['value'] is True
    assert any('reused as both' in h['reason'] for h in identity['actual_value']['holes'])
    # The observed prices, not rewritten predicate flags, reject bad contact/risk.
    for fid, field in [('M07-F2-contact', 'actual_band_contact'), ('M07-F2-stop', 'stop_above_rejection_high')]:
        assert next(a for a in rows[fid]['inputs']['assertions'] if a['field'] == field)['value'] is True


def test_m07_target_conflict_is_separate_and_long_has_no_imported_sires_gate():
    result = _score(m07._document('long', m07._positive('long')))
    assert result['verdict'] == 'pass'
    policy = next(h for h in result['holes'] if h['kind'] == 'source_conflict')
    assert policy['affected_output'] == 'target_policy'
    assert not any('lift' in field or 'reward' in field or 'cvd' in field for field in result['operands'])
    missing = m07._positive('long')
    missing['buyers_absorb_and_hold'] = None
    assert _score(m07._document('missing', missing))['verdict'] == 'unknown'


def test_m07_parent_identity_and_preselection_are_enforced():
    document = m07._document('parents', m07._positive())
    confluence = next(o for o in document['objects'] if o['object_id'].endswith(':o:confluence_band_defined'))
    confluence['parent_ids'] = confluence['parent_ids'][:1]
    result = _score(document)
    assert result['verdict'] == 'fail'
    assert any('both actual reason parents' in h['reason'] for h in result['holes'])


def test_m07_public_command_with_disposable_episode(tmp_path):
    data = tmp_path / 'data'
    data.mkdir()
    manifest = tmp_path / 'episode.json'
    from trading_research.research.method_pack.protocol import jsonable
    manifest.write_text(json.dumps(jsonable(m07._document('supplied', m07._positive()))))
    reports = tmp_path / 'reports'
    root = Path(__file__).resolve().parents[2]
    command = [sys.executable, str(root / 'implementation/tools/run_phase1_objects.py'), 'method-pass',
               '--method', m07.METHOD, '--scope', 'acquired', '--data-root', str(data),
               '--episodes', str(manifest), '--report-root', str(reports), '--formula-version', 'method-pack-v1']
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads((reports / 'member-two-reasons.json').read_text())
    assert report['summary']['N'] == 0
    assert report['summaries'][1]['p'] == report['summaries'][1]['N'] == 1
    holes = [json.loads(line) for line in Path(report['artifacts']['holes.jsonl']['path']).read_text().splitlines()]
    assert any(h.get('affected_output') == 'target_policy' for h in holes)
