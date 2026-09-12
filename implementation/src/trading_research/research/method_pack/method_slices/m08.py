"""M08: whole A, distinct value snapshots, and the actual imbalance retest."""

from datetime import date, timedelta
from decimal import Decimal

from ..clocks import et_ns
from ..evidence import fixture_document
from ..fixture_utils import method_case

METHOD = 'KEANI-OPEN-ABOVE-VALUE'
DAY = date(2026, 1, 15)
STAGE_LIMITS = {
    'prior_value_fixed': 'a_end_at', 'prior_vah': 'a_end_at',
    'a_period_complete': 'a_end_at', 'a_low': 'a_end_at',
    'developing_value_builds_higher': 'observation_at',
    'source_rejection_observed': 'observation_at',
    'dev_vah_at_break': 'dev_vah_known_at', 'breakout_close': 'breakout_at',
    'aggressive_buy_imbalance_break': 'breakout_at',
    'buyers_defend_same_imbalance_band': 'defense_at',
    'dom_supports_long': 'defense_at', 'time_of_day_allowed': 'decision_at',
    'objective_fixed': 'decision_at', 'risk_defined': 'decision_at',
}


def _t(hour, minute):
    return et_ns(DAY, hour, minute)


def _positive():
    return {
        'branch': 'source_long', 'side': 'long', 'instrument_id': 'NQ-fixture',
        'band_id': 'buying-imbalance-104', 'prior_value_fixed': True, 'prior_vah': 100,
        'a_period_complete': True, 'a_low': 101, 'a_end_at': _t(10, 0),
        'developing_value_builds_higher': True, 'source_rejection_observed': True,
        'observation_at': _t(10, 1), 'dev_vah_known_at': _t(10, 2), 'dev_vah_at_break': 104,
        'breakout_at': _t(10, 5), 'breakout_close': 105, 'aggressive_buy_imbalance_break': True,
        'imbalance_band_known_at': _t(10, 5), 'retest_at': _t(10, 7), 'defense_at': _t(10, 8),
        'buyers_defend_same_imbalance_band': True, 'dom_supports_long': True,
        'time_of_day_allowed': True, 'objective_fixed': True, 'risk_defined': True,
        'decision_at': _t(10, 9), 'imbalance_band': [104, Decimal('104.5')],
        'a_start_at': _t(9, 30), 'whole_a_coverage': True,
        'source_timing_convention': 'supplied source case at 10:09 ET',
        'diagonal_settings': {'source_config_id': 'synthetic-native-case-settings',
                              'candle': 'supplied completed breakout candle', 'grid': 'native'},
    }


def _document(fid, op):
    doc = fixture_document(METHOD, 'sequence', fid, op)
    objects = {o['object_id']: o for o in doc['objects']}
    assertions = {a['field']: a for a in doc['assertions']}
    evidence = {e['evidence_id']: e for e in doc['evidence']}
    for field, assertion in assertions.items():
        assertion['object_id'] = f'{fid}:o:{field}'
    prior = objects[f'{fid}:o:prior_vah']
    prior['value']['profile_role'] = 'prior_session'
    prior['raw_member_locators'] = [{'snapshot_id': 'prior-session-value'}]
    dev = objects[f'{fid}:o:dev_vah_at_break']
    dev['value']['profile_role'] = 'developing'
    dev['raw_member_locators'] = [{'snapshot_id': 'developing-value-10:02'}]
    for field in ('prior_value_fixed', 'prior_vah'):
        at = et_ns(DAY - timedelta(days=1), 16, 0)
        obj = objects[f'{fid}:o:{field}']
        obj.update(formation_start=at, formation_end=at, as_of=at, known_at=at)
        ev = evidence[f'{fid}:e:{field}']
        ev.update(observation_start=at, observation_end=at, known_at=at)
        if field in assertions:
            assertions[field].update(observation_start=at, observation_end=at, known_at=at)
    whole_a = objects[f'{fid}:o:a_period_complete']
    whole_a['value'].update(a_start_at=op['a_start_at'], a_end_at=op['a_end_at'],
                            a_low=op['a_low'], coverage_complete=op['whole_a_coverage'])
    whole_a['parent_ids'] = [f'{fid}:o:a_low']
    imbalance = objects[f'{fid}:o:aggressive_buy_imbalance_break']
    imbalance['value']['band'] = op['imbalance_band']
    imbalance['value']['source_config'] = op.get('diagonal_settings')
    imbalance['parent_ids'] = [dev['object_id']]
    for field in ('retest_at', 'buyers_defend_same_imbalance_band', 'dom_supports_long'):
        objects[f'{fid}:o:{field}']['parent_ids'] = [imbalance['object_id']]
    return doc


def audit_candidate(candidate, operands, objects, assertions, evidence):
    findings = []

    def issue(field, reason, recipe, *, unknown=False, kind='identity'):
        findings.append({'field': field, 'reason': reason, 'recipe_id': recipe,
                         'unknown': unknown, 'kind': kind})

    def record(field):
        binding = candidate['operands'].get(field, {})
        return assertions.get(binding.get('assertion_id')) or objects.get(binding.get('object_id'), {})

    def producer(field):
        rec = record(field)
        return objects.get(rec.get('object_id'))

    prior, dev = producer('prior_vah'), producer('dev_vah_at_break')
    start = et_ns(date.fromisoformat(candidate['session_date_et']), 9, 30)
    end = et_ns(date.fromisoformat(candidate['session_date_et']), 10, 0)
    if prior and dev:
        if (prior['object_id'] == dev['object_id']
                or set(prior['evidence_ids']) & set(dev['evidence_ids'])
                or (prior.get('raw_member_locators') and prior.get('raw_member_locators') == dev.get('raw_member_locators'))):
            issue('dev_vah_at_break', 'Prior VAH and developing VAH must retain distinct source snapshots', 'O063')
        if prior['known_at'] is not None and prior['known_at'] > start:
            issue('prior_vah', 'Prior value was not known before whole A began', 'O062', kind='ordering')
    whole_a = producer('a_period_complete')
    value = whole_a['value'] if whole_a else {}
    if operands.get('a_period_complete') is True:
        if any(value.get(key) is None for key in ('a_start_at', 'a_end_at', 'a_low', 'coverage_complete')):
            issue('a_period_complete', 'Whole-A coverage, bounds and minimum require the actual source period record', 'O078', unknown=True, kind='data_coverage')
        elif value['a_start_at'] != start or value['a_end_at'] != end or operands.get('a_end_at') != end:
            issue('a_period_complete', 'A must be the complete source 09:30–10:00 ET period', 'O003')
        elif value['coverage_complete'] is not True:
            issue('a_period_complete', 'Whole-A source observations are incomplete', 'O078', unknown=True, kind='data_coverage')
        elif operands.get('a_low') is not None and Decimal(str(value['a_low'])) != operands['a_low']:
            issue('a_low', 'Bound minimum differs from the actual whole-A source minimum', 'O078')
    imbalance = producer('aggressive_buy_imbalance_break')
    if operands.get('aggressive_buy_imbalance_break') is True:
        config = imbalance['value'].get('source_config') if imbalance else None
        supported = config and any(evidence[eid]['payload'].get('diagonal_settings') == config
                                   for eid in record('aggressive_buy_imbalance_break').get('evidence_ids', []))
        if not supported:
            issue('aggressive_buy_imbalance_break', 'Native diagonal/candle settings lack their source observation', 'O109', unknown=True, kind='source_definition')
        if imbalance and dev and dev['object_id'] not in imbalance['parent_ids']:
            issue('aggressive_buy_imbalance_break', 'Buying imbalance does not link its actual developing VAH snapshot', 'O109')
    for field in ('retest_at', 'buyers_defend_same_imbalance_band', 'dom_supports_long'):
        obj = producer(field)
        if obj and imbalance and imbalance['object_id'] not in obj['parent_ids']:
            issue(field, 'Retest/defense does not link the original buying-imbalance band', 'O091')
        elif not obj and operands.get(field) is not None:
            issue(field, 'Same-band evidence lacks its actual source producer', 'O091', unknown=True, kind='supplied_record_missing')
    timing = record('time_of_day_allowed')
    if operands.get('time_of_day_allowed') is True and not any(evidence[eid]['payload'].get('source_timing_convention') for eid in timing.get('evidence_ids', [])):
        issue('time_of_day_allowed', 'Exact source timing convention was not supplied', 'O003', unknown=True, kind='source_definition')
    return findings


def method_fixtures():
    rows = []

    def add(fid, updates=None, expected='pass', *, document=None, kind='method'):
        doc = document or _document(fid, {**_positive(), **(updates or {})})
        rows.append(method_case(METHOD, 'sequence', fid, doc, expected, kind=kind))

    add('M08-F1')
    add('M08-F2-a-low', {'a_low': Decimal('99.75')}, 'fail')
    add('M08-F2-a-equal', {'a_low': 100}, 'fail')
    alias = _document('M08-F2-prior-alias', _positive())
    prior = next(o for o in alias['objects'] if o['object_id'].endswith(':o:prior_vah'))
    prior['value']['dev_vah_at_break'] = 100
    prior['units']['dev_vah_at_break'] = 'decimal_price?'
    alias['candidates'][0]['operands']['dev_vah_at_break']['object_id'] = prior['object_id']
    for ev in alias['evidence']:
        ev['payload']['dev_vah_at_break'] = 100
    add('M08-F2-prior-alias', document=alias, expected='fail')
    add('M08-F2-before-A', {'decision_at': _t(9, 50)}, 'fail')
    add('M08-F2-short', {'side': 'short'}, 'fail')
    add('M08-F3-timing', {'source_timing_convention': None}, 'unknown')
    add('M08-F3-diagonal', {'diagonal_settings': None}, 'unknown')
    add('M08-F1:missing', {'buyers_defend_same_imbalance_band': None}, 'unknown', kind='c08_missing')
    late = _document('M08-F1:late', _positive())
    next(a for a in late['assertions'] if a['field'] == 'dom_supports_long')['known_at'] = _t(10, 10)
    add('M08-F1:late', document=late, expected='fail', kind='c08_late')
    foreign = _document('M08-F1:identity', _positive())
    next(o for o in foreign['objects'] if o['object_id'].endswith(':o:retest_at'))['band_id'] = 'different-band'
    add('M08-F1:identity', document=foreign, expected='fail', kind='c08_identity')
    return rows
