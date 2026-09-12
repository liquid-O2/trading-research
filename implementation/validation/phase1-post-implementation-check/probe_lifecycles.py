"""Independent lifecycle regression probes; exit 1 while defects reproduce.

These synthetic records exercise the registered recipes, complete output-schema
validation and (for orders) the real supplied-source admission function. They
do not assert that a historical method candidate passed.
"""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path

from trading_research.research.method_pack import objects  # noqa: F401
from trading_research.research.method_pack.contracts import validate_output
from trading_research.research.method_pack.evidence import audit_source_domain_object
from trading_research.research.method_pack.protocol import jsonable, run_recipe
from trading_research.research.method_pack.semantic_views import AUTHORS
from trading_research.research.method_pack.source_config import load_catalog


def main():
    results = []

    def check(name, recipe_id, inputs, expected):
        result = validate_output(run_recipe(recipe_id, deepcopy(inputs)))
        row = dict(probe=name, recipe_id=recipe_id, inputs=jsonable(inputs),
                   expected=expected, state=result.state, base_ok=result.base_ok,
                   coverage_ok=result.coverage_ok, known_at=result.known_at,
                   holes=result.hole_ids, value=jsonable(result.value))
        results.append(row)
        return result, row

    order = dict(candidate_id='candidate-A', order_id='order-A', position_id='position-A',
                 instrument_id='NQ', source_id='refill', method_id='REFILL-STUDY', side='long',
                 order_type='limit', limit=100, q=Decimal('.25'), quantity=3, placed_at=10,
                 use_at=30, other_open_positions=0,
                 source_policy=dict(policy_id='refill-v1', source_id='refill',
                                    method_id='REFILL-STUDY', stop_ticks=32, target_ticks=96,
                                    cancel_minutes=30, one_position_at_a_time=True))
    fill = dict(event_id='fill-A', kind='fill', qty=1, at=15, known_at=15,
                order_id='order-A', position_id='position-A', instrument_id='NQ')
    source = load_catalog()['sources']['REF']
    citation = dict(source_key='REF', source_file=source['path'], sha256=source['sha256'],
                    page=7, image_id='REF:7:page')
    variants = [
        ('order_control', {**order, 'events': [fill]}, 'Complete valid order record.'),
        ('foreign_order_fill', {**order, 'events': [{**fill, 'order_id': 'order-B',
         'position_id': 'position-B', 'instrument_id': 'ES'}]},
         'Reject a fill that names another order, position and instrument.'),
        ('future_fill_backdated', {**order, 'use_at': 15,
         'events': [{**fill, 'at': 20, 'known_at': 12}]},
         'Reject availability before the event; do not count the fill at snapshot 15.'),
    ]
    for name, inputs, expected in variants:
        result, row = check(name, 'O150', inputs, expected)
        supplied = dict(object_id='supplied-' + name, recipe_id='O150',
                        method_id='REFILL-STUDY', author=sorted(AUTHORS['REFILL-STUDY'])[0],
                        instrument_id='NQ', known_at=result.known_at,
                        value={}, evidence_ids=['evidence'])
        evidence = {'evidence': {'payload': dict(recipe_id='O150',
                    recipe_inputs=deepcopy(inputs), source_citation=citation)}}
        try:
            admitted = audit_source_domain_object(supplied, evidence)
            row['source_audit'] = dict(accepted=True, state=admitted.state,
                                      base_ok=admitted.base_ok, known_at=admitted.known_at,
                                      filled_quantity=str(admitted.value['filled_quantity']))
        except Exception as exc:
            row['source_audit'] = dict(accepted=False, error=type(exc).__name__ + ': ' + str(exc))
        bad_acceptance = result.base_ok is True and result.value['filled_quantity'] == 1
        row['check_passed'] = (bad_acceptance and row['source_audit']['accepted']) if name == 'order_control' else (
            not bad_acceptance and not row['source_audit']['accepted'])

    current = dict(state_label='D', state_id='state-current', state_at=10, known_at=10,
                   sequence=1, instrument_id='NQ', cohort_id='cohort', reset_id='session')
    nxt = dict(state_label='A', state_id='state-next', state_at=20, known_at=20,
               sequence=2, instrument_id='NQ', cohort_id='cohort', reset_id='session')
    transition = dict(current_observation=current, next_observation=nxt,
                      cadence='adjacent-state-observations',
                      conditioning_evidence=[dict(evidence_id='condition', known_at=9)])
    variants = [
        ('transition_control', transition, 'Complete valid observed transition.'),
        ('transition_missing_labels', {**transition,
         'current_observation': {k: v for k, v in current.items() if k != 'state_label'},
         'next_observation': {k: v for k, v in nxt.items() if k != 'state_label'}},
         'Missing state labels must leave transition_valid unknown.'),
        ('transition_backdated', {**transition, 'current_observation': {**current, 'known_at': 5},
         'next_observation': {**nxt, 'known_at': 6},
         'conditioning_evidence': [dict(evidence_id='condition', known_at=4)],
         'known_at': 6, 'use_at': 7},
         'Reject an observed transition claimed available before its state events.'),
    ]
    for name, inputs, expected in variants:
        result, row = check(name, 'O166', inputs, expected)
        admitted = result.base_ok is True and result.value['transition_valid'] is True
        row['check_passed'] = admitted if name == 'transition_control' else not admitted

    document = dict(reviewed_commit='662463b545394e663937be2d83e0677f50492dc3',
                    checks=len(results), passed=sum(row['check_passed'] for row in results),
                    failures=sum(not row['check_passed'] for row in results), results=results)
    Path(__file__).with_name('lifecycle-probes.json').write_text(json.dumps(document, indent=2) + '\n')
    for row in results:
        print(row['probe'], 'PASS' if row['check_passed'] else 'FAIL',
              f"state={row['state']} known_at={row['known_at']}")
    print(f"{document['passed']} controls passed; {document['failures']} regression checks failed")
    return int(bool(document['failures']))


if __name__ == '__main__':
    raise SystemExit(main())
