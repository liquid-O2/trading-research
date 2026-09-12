"""M07: two independent source reasons and an observed structural entry."""

from copy import deepcopy
from datetime import date
from decimal import Decimal

from ..clocks import et_ns
from ..evidence import fixture_document
from ..fixture_utils import method_case

METHOD = 'MEMBER-TWO-REASONS'
STAGE_LIMITS = {
    'thesis_predefined': 'touch_at', 'objective_fixed': 'decision_at',
    'risk_defined': 'decision_at', 'prior_reaction_area_known': 'area_known_at',
    'independent_minor_hvn_known': 'hvn_known_at',
    'confluence_band_defined': 'touch_at', 'actual_band_contact': 'touch_at',
    'resistance_rejection': 'reaction_at', 'buyers_absorb_and_hold': 'reaction_at',
    'planned_return_to_structure': 'touch_at',
}


def _t(hour, minute):
    return et_ns(date(2026, 1, 15), hour, minute)


def _positive(side='short'):
    return {
        'branch': 'resistance_short' if side == 'short' else 'planned_return_long',
        'side': side, 'instrument_id': 'NQ-fixture', 'band_id': 'selected-confluence',
        'thesis_predefined': True, 'objective_fixed': True, 'risk_defined': True,
        'prior_reaction_area_known': True, 'independent_minor_hvn_known': True,
        'confluence_band_defined': True, 'actual_band_contact': True,
        'area_known_at': _t(9, 30), 'hvn_known_at': _t(9, 30),
        'touch_at': _t(9, 45), 'reaction_at': _t(9, 47), 'decision_at': _t(9, 48),
        'resistance_rejection': True, 'stop_above_rejection_high': True,
        'planned_return_to_structure': True, 'buyers_absorb_and_hold': True,
        'stop_behind_long_invalidation': True,
        'reaction_band': [100, 102], 'hvn_band': [101, 103],
        'confluence_band': [101, 102], 'contact_px': Decimal('101.5'),
        'rejection_high': 102, 'long_invalidation': 100,
        'stop_px': Decimal('102.25') if side == 'short' else Decimal('99.75'),
        'objective_px': 98 if side == 'short' else 104,
    }


def _document(fid, op):
    doc = fixture_document(METHOD, 'sequence', fid, op)
    by_field = {a['field']: a for a in doc['assertions']}
    objects = {o['object_id']: o for o in doc['objects']}
    for field, assertion in by_field.items():
        assertion['object_id'] = f'{fid}:o:{field}'
    reaction = objects[f'{fid}:o:prior_reaction_area_known']
    hvn = objects[f'{fid}:o:independent_minor_hvn_known']
    hvn['recipe_id'] = by_field['independent_minor_hvn_known']['recipe_id'] = 'O066'
    reaction['value']['band'] = op['reaction_band']
    hvn['value']['band'] = op['hvn_band']
    reaction['raw_member_locators'] = [{'source_observation_id': 'prior-reaction-history'}]
    hvn['raw_member_locators'] = [{'source_observation_id': 'minor-hvn-profile'}]
    confluence = objects[f'{fid}:o:confluence_band_defined']
    confluence['value']['band'] = op['confluence_band']
    confluence['parent_ids'] = [reaction['object_id'], hvn['object_id']]
    for field in ('actual_band_contact', 'resistance_rejection', 'buyers_absorb_and_hold'):
        objects[f'{fid}:o:{field}']['parent_ids'] = [confluence['object_id']]
    return doc


def audit_candidate(candidate, operands, objects, assertions, evidence):
    findings = []

    def issue(field, reason, *, kind='identity', unknown=False, recipe='O072'):
        findings.append({'field': field, 'kind': kind, 'reason': reason,
                         'unknown': unknown, 'recipe_id': recipe})

    def producer(field):
        binding = candidate['operands'].get(field, {})
        rec = assertions.get(binding.get('assertion_id'), {})
        return objects.get(binding.get('object_id') or rec.get('object_id'))

    def payload_value(field, names):
        binding = candidate['operands'].get(field, {})
        rec = assertions.get(binding.get('assertion_id')) or objects.get(binding.get('object_id'), {})
        records = [rec.get('value', {})] if isinstance(rec.get('value'), dict) else []
        obj = producer(field)
        if obj:
            records.append(obj['value'])
        records.extend(evidence[eid]['payload'] for eid in rec.get('evidence_ids', []))
        for record in records:
            for name in names:
                if record.get(name) is not None:
                    return record[name]
        return None

    reaction = producer('prior_reaction_area_known')
    hvn = producer('independent_minor_hvn_known')
    confluence = producer('confluence_band_defined')
    if not reaction or not hvn or not confluence:
        issue('independent_minor_hvn_known',
              'Independent reaction/HVN producers and their selected confluence parents are required',
              kind='supplied_record_missing', unknown=True, recipe='O066')
    else:
        same = reaction['object_id'] == hvn['object_id']
        same |= bool(set(reaction['evidence_ids']) & set(hvn['evidence_ids']))
        left = reaction.get('raw_member_locators', [])
        right = hvn.get('raw_member_locators', [])
        same |= bool(left and right and left == right)
        if same:
            issue('independent_minor_hvn_known', 'One source line was reused as both independent reasons', recipe='O066')
        if not {reaction['object_id'], hvn['object_id']} <= set(confluence['parent_ids']):
            issue('confluence_band_defined', 'Selected confluence does not link both actual reason parents', recipe='O071')
        if confluence.get('known_at') is not None and operands.get('touch_at') is not None and confluence['known_at'] > operands['touch_at']:
            issue('confluence_band_defined', 'Confluence was selected after the actual touch', kind='ordering', recipe='O071')
    band = confluence['value'].get('band') if confluence else None
    contact = payload_value('actual_band_contact', ('contact_px', 'price'))
    if operands.get('actual_band_contact') is True:
        if not isinstance(band, (list, tuple)) or len(band) != 2 or contact is None:
            issue('actual_band_contact', 'Actual selected-band bounds and contact price are unavailable',
                  kind='supplied_record_missing', unknown=True, recipe='O002')
        elif not Decimal(str(band[0])) <= Decimal(str(contact)) <= Decimal(str(band[1])):
            issue('actual_band_contact', 'Observed price never contacts the selected confluence band', recipe='O002')
    side = operands.get('side')
    stop_field = 'stop_above_rejection_high' if side == 'short' else 'stop_behind_long_invalidation'
    if operands.get(stop_field) is True:
        stop = payload_value(stop_field, ('stop_px', 'stop'))
        reference = payload_value(stop_field, ('rejection_high',) if side == 'short' else ('long_invalidation',))
        if stop is None or reference is None:
            issue(stop_field, 'Actual source stop and structural invalidation prices are unavailable',
                  kind='supplied_record_missing', unknown=True, recipe='O139')
        elif not (Decimal(str(stop)) > Decimal(str(reference)) if side == 'short' else Decimal(str(stop)) < Decimal(str(reference))):
            issue(stop_field, 'Actual stop is not strictly behind the selected source invalidation', recipe='O139')
    findings.append({'field': 'general_target_policy', 'kind': 'source_conflict',
                     'recipe_id': 'O141', 'reason': 'Source target prose/ticket conflict remains unresolved; the actual preselected case objective is audited separately',
                     'affected_output': 'target_policy', 'affects_admission': False})
    return findings


def method_fixtures():
    rows = []

    def add(fid, op=None, expected='pass', *, document=None, kind='method'):
        rows.append(method_case(METHOD, 'sequence', fid,
                                document or _document(fid, op or _positive()), expected, kind=kind))

    add('M07-F1')
    add('M07-F1-long', _positive('long'))
    duplicate = _document('M07-F2-identity', _positive())
    objects = {o['object_id']: o for o in duplicate['objects']}
    objects['M07-F2-identity:o:independent_minor_hvn_known']['raw_member_locators'] = \
        deepcopy(objects['M07-F2-identity:o:prior_reaction_area_known']['raw_member_locators'])
    add('M07-F2-identity', expected='fail', document=duplicate)
    for fid, updates in [
        ('M07-F2-contact', {'contact_px': 104}),
        ('M07-F2-stop', {'stop_px': Decimal('101.75')}),
        ('M07-F2-late-hvn', {'hvn_known_at': _t(9, 50)}),
    ]:
        add(fid, {**_positive(), **updates}, 'fail')
    add('M07-F3-target-policy', expected='pass')
    add('M07-F3-long-hold', {**_positive('long'), 'buyers_absorb_and_hold': None}, 'unknown')
    add('M07-F1:missing', {**_positive(), 'independent_minor_hvn_known': None}, 'unknown', kind='c08_missing')
    late = _document('M07-F1:late', _positive())
    assertion = next(a for a in late['assertions'] if a['field'] == 'resistance_rejection')
    assertion['known_at'] = _t(9, 49)
    add('M07-F1:late', document=late, expected='fail', kind='c08_late')
    identity = _document('M07-F1:identity', _positive())
    obj = next(o for o in identity['objects'] if o['object_id'].endswith(':o:confluence_band_defined'))
    obj['band_id'] = 'foreign-confluence'
    add('M07-F1:identity', document=identity, expected='fail', kind='c08_identity')
    return rows
