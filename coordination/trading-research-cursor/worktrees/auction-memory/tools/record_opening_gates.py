"""Record retrospective opening evidence; does not read market tapes or run tests."""

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re

from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.operations.artifacts import artifact_ref, code_manifest, digest
from trading_research.operations.ledger import Ledger
from trading_research.operations.scope import Scope


ROOT = Path(__file__).resolve().parents[1]


def extend(old, new):
    return list({digest(v): v for v in [*old, *new]}.values())


def main():
    ledger = Ledger(ROOT / 'evidence')
    artifacts = ledger.artifacts
    scope = Scope.load(ROOT.parent / 'planning/trading-model')
    checkpoint = json.loads((ROOT / 'reports/current-checkpoint.json').read_bytes())
    verification_ref = artifact_ref(checkpoint['latest_verification'])
    verification = artifacts.read_json(verification_ref)
    code_ref = artifact_ref(verification['code_snapshot'])
    assert verification['success'] and verification['tests_run'] == 247
    assert artifacts.read_json(code_ref)['manifest'] == code_manifest(ROOT)
    passed = set(verification['passed_assertion_ids'])
    source_text = (ROOT / 'validation/F02_SOURCE_CASES.md').read_text()
    aliases = {'RD': 'tests.test_rolls_definitions', 'FD': 'tests.test_foundations',
               'BR': 'tests.test_batch_review', 'DF': 'tests.test_decoder_faults'}
    cases = []
    for line in source_text.splitlines():
        if not line.startswith('| F02-'):
            continue
        columns = re.split(r'(?<!\\)\|', line.strip().strip('|'))
        assert len(columns) == 3
        assertions = [aliases[a] + '.' + s for a, s in re.findall(r'`(RD|FD|BR|DF)\.([^`]+)`', line)]
        assertions.extend(re.findall(r'`(tests\.[^`]+)`', line))
        assertions = sorted(set(assertions))
        assert set(assertions).issubset(passed), assertions
        cases.append({'case': columns[0].strip(), 'expected': columns[1].strip(),
                      'evidence_and_remaining': columns[2].strip(), 'assertion_ids': assertions,
                      'assertion_membership_confirmed': True, 'whole_case_verified': False,
                      'mapping_is_retrospective': True})
    assert len(cases) == len({c['case'] for c in cases}) == 23
    docs = {name: asdict(artifacts.put_bytes((ROOT / name).read_bytes(), kind='implementation_review_document'))
            for name in ('validation/F02_SOURCE_CASES.md', 'validation/E0_MINIMUM_GATE_REVIEW.md')}
    script_ref = artifacts.put_bytes(Path(__file__).read_bytes(), kind='evidence_assembly_script')
    catalog_path = ROOT.parent / 'data/manifests/dataset-catalog.json'
    catalog = json.loads(catalog_path.read_bytes())
    assert len(catalog['datasets']) == 111
    catalog_ref = artifacts.put_bytes(catalog_path.read_bytes(), kind='supplied_dataset_catalog')
    nq = [d for d in catalog['datasets'] if d.get('symbol') == 'NQ.c.0']
    assert len(nq) == 6
    parent_nq = [d['dataset_id'] for d in catalog['datasets'] if d.get('symbol') == 'NQ.FUT']
    assert not parent_nq
    definitions_path = ROOT / 'reports/definitions-ten-partitions.json'
    definitions_ref = artifacts.put_bytes(definitions_path.read_bytes(), kind='raw_definition_audit')
    definitions = json.loads(definitions_path.read_bytes())
    assert definitions['success'] and definitions['total_rows'] == 2579
    yearly = []
    for partition in definitions['partitions']:
        rows = [d for d in definitions['definitions'] if d['source_path'] == partition['path']]
        identities = sorted({(d['instrument_id'], d['raw_symbol']) for d in rows})
        assert len(rows) == partition['rows']
        assert len(identities) == partition['distinct_outright_instruments'] == 5
        yearly.append({'path': partition['path'], 'rows': len(rows), 'identities_observed_during_year': identities,
                       'whole_file_hash_from_prior_audit': partition['whole_file_hash'],
                       'simultaneous_parent_completeness_certified': False})
    calendar = CashCalendar(ROOT / 'configs/cash-rth-calendar.json')
    quarters = []
    for year in (2022, 2023, 2024, 2025):
        for quarter in range(1, 5):
            days = calendar.quarter_dates(year, quarter)
            quarters.append({'year': year, 'quarter': quarter, 'cash_open_dates': len(days),
                             'date_versions': {d.day.isoformat(): d.version for d in days},
                             'early_close_dates': [d.day.isoformat() for d in days if d.state == 'early_close'],
                             'e0_eligible_dates': None, 'e0_selected_dates': None})
    now = datetime.now(timezone.utc).isoformat()
    dependency = {
        'id': 'E0-COMPLETE-PARENT-OUTRIGHTS', 'scope': 'exact E0 market cohort and dependent comparisons',
        'state': 'missing_required_evidence',
        'required': 'Historically known complete NQ parent outright definitions/listings and compatible completed preceding-session volumes; selected-contract MBP for the required windows.',
        'observed': 'The scoped catalog supplies NQ.c.0 for outright data and NQ.OPT for options; it supplies no NQ.FUT acquisition. Calendar-expiry rank does not establish prior-volume selection.',
        'catalog': asdict(catalog_ref), 'definition_audit': asdict(definitions_ref),
        'next_action': 'Locate or obtain independently authorized parent coverage/equivalent causal proof. Continue opening engineering and separately registered acquired-contract diagnostics within their own gates.',
        'does_not_block': 'Independent reference implementation, native/Arrow semantic admission, deterministic measurement and later branches with their own eligible inputs.'}
    result = {
        'kind': 'opening_definition_and_e0_gate_review', 'recorded_at': now,
        'scope_version': scope.version, 'documents': docs, 'script': asdict(script_ref),
        'code_snapshot': asdict(code_ref), 'existing_verification': asdict(verification_ref),
        'code_matches_existing_verification': True, 'new_test_executions': 0,
        'retrospective_cases': cases, 'whole_unit_definition_closure': False,
        'catalog': asdict(catalog_ref), 'catalog_nq_continuous_datasets': [d['dataset_id'] for d in nq],
        'catalog_nq_parent_outright_datasets': parent_nq,
        'definition_audit': asdict(definitions_ref), 'yearly_definition_observations': yearly,
        'cash_calendar_version': calendar.version, 'timezone_version': calendar.timezone_version,
        'calendar_quarters': quarters, 'cash_open_dates': sum(q['cash_open_dates'] for q in quarters),
        'exact_e0_cohort_frozen': False, 'market_day_completeness_assessed': False,
        'exact_e0_runnable': False, 'exact_e0_dependencies': [dependency],
        'other_opening_gates': ['dated_venue_boundaries', 'actual_terms_and_definition_joins',
                                'complete_required_mbp_windows', 'source_supported_book_recovery',
                                'formation_and_prior_rth_reconciliation', 'opening_source_case_closure'],
        'primary_sources_checked_on': '2026-09-06',
        'primary_sources': [
            {'url': 'https://databento.com/docs/standards-and-conventions/symbology',
             'supports': 'c is calendar rank; v uses prior-day volume; continuous and parent/option scopes differ.',
             'extent': 'Rendered web text reviewed; no raw page hash.'},
            {'url': 'https://www.cmegroup.com/notices/ser/2022/04/SER-8975.pdf',
             'supports': 'Dated NQ listing schedule expansion effective trade date May 23, 2022.',
             'extent': 'Full one-page extracted text; direct PDF byte request HTTP 403, screenshot returned no image content; no raw PDF hash or visual-review claim.'},
            {'url': 'https://www.cmegroup.com/trading-hours.html',
             'supports': 'Current 2026/2027 schedule does not certify 2022-2025.',
             'extent': 'Relevant page text; historical cohort remains unresolved.'}],
        'model_fits': 0, 'economic_runs': 0, 'new_market_tape_reads': 0,
        'limitations': ['Calendar-open days are not complete-data or executable E0 days.',
                        'Existing actual definition audit retains its original code/version and evidence extent.',
                        'Named passing assertions are partial engineering evidence, not option/payoff or full-unit closure.',
                        'A separately named acquired-contract diagnostic cannot substitute for exact E0.']}
    ref = artifacts.put_json(result, kind='implementation_review')
    (ROOT / 'reports/opening-minimum-gates.json').write_text(json.dumps({'artifact': asdict(ref), **result}, indent=2, sort_keys=True) + '\n')
    state = ledger.current()
    changes = {}
    owners = ('F02', 'F02.PAYOFF', 'F03', 'F08', 'B03.5',
              'quantpad/cme__nq-continuous-futures__definition',
              'quantpad/cme__nq-continuous-futures__trades',
              'quantpad/cme__nq-continuous-futures__mbp-1')
    for owner in owners:
        old = state[owner]
        changes[owner] = {
            'review_artifacts': extend(old['review_artifacts'], [asdict(ref)]),
            'dependency_details': extend(old['dependency_details'], [dependency]),
            'reason': 'Opening source cases mapped retrospectively; exact E0 lacks complete parent-outright selection evidence. Engineering, evaluation and whole-unit definition states are unchanged.',
            'next_action': 'Complete the collected opening implementation/case work and eligible data admission; retain exact E0 parent/venue dependencies separately.'}
    transaction = ledger.update(changes, reason='Record opening cases and the actual continuous-versus-parent E0 dependency without promoting partial evidence.')
    checkpoint.update(ledger.audit(scope))
    checkpoint.update(recorded_at=now, latest_opening_gate_review=asdict(ref),
                      next_action='Complete opening source cases and eligible admission work; exact E0 additionally requires parent-contract selection and historical venue evidence.')
    (ROOT / 'reports/current-checkpoint.json').write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + '\n')
    conformance = json.loads((ROOT / 'reports/conformance-audit.json').read_bytes())
    conformance.update(recorded_at=now, opening_gate_review=asdict(ref), exact_e0_dependency=dependency)
    (ROOT / 'reports/conformance-audit.json').write_text(json.dumps(conformance, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'artifact': asdict(ref), 'cases': len(cases),
                      'distinct_existing_assertions': len({a for c in cases for a in c['assertion_ids']}),
                      'cash_open_dates': result['cash_open_dates'], 'exact_e0_runnable': False,
                      'transaction': transaction, 'engineering': checkpoint['engineering']}, indent=2))


if __name__ == '__main__':
    main()
