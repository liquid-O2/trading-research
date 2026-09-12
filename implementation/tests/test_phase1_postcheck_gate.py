"""Completion must reject absent, stale, or inconsistent independent evidence."""
from copy import deepcopy
import json
from pathlib import Path
import sys

import pytest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import build_phase1_acceptance as acceptance
import validate_phase1_post_implementation_regressions as checker


@pytest.fixture
def repair_document():
    _, cases, failures = checker.load_saved_cases()
    assert not failures
    rows, failures = checker.run_checks(cases)
    assert not failures
    hashes, failures = checker._source_hashes()
    assert not failures
    return dict(status='pass', passed=6, failures=0,
                saved_input_hashes={case.name: case.input_sha256 for case in cases},
                tested_implementation_source_hashes=hashes, results=rows)


def test_postcheck_gate_requires_preserved_passing_current_evidence(tmp_path, repair_document):
    path = tmp_path / 'repair.json'
    assert acceptance.postcheck_summary(path)['status'] == 'missing_review'
    path.write_text(json.dumps(repair_document))
    assert acceptance.postcheck_summary(path)['status'] == 'pass'


@pytest.mark.parametrize('defect', ['stale_code', 'changed_input', 'missing_case', 'forged_green_fill', 'forged_green_labels'])
def test_postcheck_gate_rechecks_evidence_instead_of_trusting_green_status(tmp_path, repair_document, defect):
    document = deepcopy(repair_document)
    if defect == 'stale_code':
        document['tested_implementation_source_hashes'][checker.IMPLEMENTATION_SOURCES[0]] = 'stale'
    elif defect == 'changed_input':
        document['results'][0]['inputs']['quantity'] = 99
    elif defect == 'missing_case':
        document['results'].pop()
    elif defect == 'forged_green_fill':
        row = next(row for row in document['results'] if row['probe'] == 'foreign_order_fill')
        row['result']['value']['filled_quantity'] = '1'
    else:
        row = next(row for row in document['results'] if row['probe'] == 'transition_missing_labels')
        row['result']['value']['transition_valid'] = True
    path = tmp_path / 'repair.json'
    path.write_text(json.dumps(document))
    assert acceptance.postcheck_summary(path)['status'] == 'implementation_fail'


@pytest.fixture
def original_audit_document(tmp_path, monkeypatch):
    import validate_phase1_audit_regressions as original_audit
    path = tmp_path / 'original-audit.json'
    monkeypatch.setattr(original_audit, 'OUTPUT', path)
    assert original_audit.main() == 0
    return json.loads(path.read_text())


@pytest.mark.parametrize('defect', ['stale_code', 'missing_schema', 'failed_quantity_control'])
def test_original_audit_gate_requires_current_schema_and_quantity_evidence(tmp_path, original_audit_document, defect):
    document = deepcopy(original_audit_document)
    path = tmp_path / 'audit.json'
    path.write_text(json.dumps(document))
    assert acceptance.regression_audit_summary(path)['status'] == 'pass'
    if defect == 'stale_code':
        key = next(iter(document['tested_implementation_source_hashes']))
        document['tested_implementation_source_hashes'][key] = 'stale'
    elif defect == 'missing_schema':
        document['probes'][0]['original']['actual']['schema_validated'] = False
    else:
        row = next(row for row in document['probes'] if row['id'] == 'P21')
        row['control']['status'] = 'fail'
    path.write_text(json.dumps(document))
    assert acceptance.regression_audit_summary(path)['status'] == 'implementation_fail'
