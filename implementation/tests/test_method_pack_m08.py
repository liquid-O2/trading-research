from trading_research.research.method_pack.evidence import parse_manifest, score_episode
from trading_research.research.method_pack.method_slices import m08


def _score(doc):
    candidates, objects, assertions, evidence = parse_manifest(doc, m08.METHOD)
    return score_episode(next(iter(candidates.values())), objects, assertions, evidence)


def test_m08_every_printed_case_runs_at_the_c01_boundary():
    rows = {row['id']: row for row in m08.method_fixtures()}
    assert all(row['status'] == 'pass' for row in rows.values())
    assert rows['M08-F1']['actual_value']['verdict'] == 'pass'
    for fid in ('M08-F2-a-low', 'M08-F2-a-equal', 'M08-F2-prior-alias', 'M08-F2-before-A', 'M08-F2-short'):
        assert rows[fid]['actual_value']['verdict'] == 'fail'
    for fid in ('M08-F3-timing', 'M08-F3-diagonal'):
        assert rows[fid]['actual_value']['verdict'] == 'unknown'


def test_m08_whole_a_requires_coverage_and_actual_minimum():
    doc = m08._document('coverage', {**m08._positive(), 'whole_a_coverage': False})
    assert _score(doc)['verdict'] == 'unknown'
    doc = m08._document('minimum', m08._positive())
    obj = next(o for o in doc['objects'] if o['object_id'].endswith(':o:a_period_complete'))
    obj['value']['a_low'] = 99
    assert _score(doc)['verdict'] == 'fail'


def test_m08_unlinked_retest_and_final_value_snapshot_cannot_pass():
    doc = m08._document('retest', m08._positive())
    obj = next(o for o in doc['objects'] if o['object_id'].endswith(':o:retest_at'))
    obj['parent_ids'] = []
    assert _score(doc)['verdict'] == 'fail'
    doc = m08._document('late-value', m08._positive())
    obj = next(o for o in doc['objects'] if o['object_id'].endswith(':o:dev_vah_at_break'))
    obj['known_at'] = m08._t(16, 0)
    assert _score(doc)['verdict'] == 'fail'
