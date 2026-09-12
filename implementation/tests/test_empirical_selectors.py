"""Opportunity accounting and future controls for deterministic comparisons."""
from copy import deepcopy
from decimal import Decimal
import pytest

from trading_research.research.method_pack.empirical_protocol import population_summary
from trading_research.research.method_pack.empirical_selectors import (
    MINUTE, first_excursions, later_touch, next_aligned_close,
)

START = 1_800_000_000_000_000_000  # aligned to five minutes
RULE = {'rule_id':'test-rule', 'method_id':'GB-FAIL', 'branch':'previous_hour', 'assumption_ids':['A-test']}
PARTITION = {'partition_id':'test-partition','instrument_id':42,'session_date':'2027-01-15'}
REFERENCE = {'reference_id':'prior-hour','instrument_id':42,'known_at':START,
             'high':Decimal(110),'low':Decimal(90),'complete':True}


def bars(count=10, *, mirrored=False):
    out = []
    for i in range(count):
        o,c,h,l = (100,101,111,99) if i == 1 else (101,100,102,99)
        if mirrored: o,c,h,l = 200-o,200-c,200-l,200-h
        out.append({'bar_id':f'b{i}','instrument_id':42,'start':START+i*MINUTE,
                    'end':START+(i+1)*MINUTE,'known_at':START+(i+1)*MINUTE,
                    'complete':True,'O':o,'H':h,'L':l,'C':c,'V':10})
    return out


def detect(rows, sides=('short',)):
    return first_excursions(RULE, PARTITION, REFERENCE, rows, registry_sha256='a'*64,
        action_start=START, expiry_at=START+10*MINUTE, sides=sides)


@pytest.mark.parametrize('mirrored,side', [(False,'short'),(True,'long')])
def test_initial_sweep_positive_and_mirrored_endpoint(mirrored, side):
    rows = bars(mirrored=mirrored)
    opportunities, holes = detect(rows, (side,))
    assert len(opportunities) == 1 and not holes
    assert opportunities[0].available_at == START+2*MINUTE
    result = next_aligned_close(opportunities[0], rows, minutes=5)
    assert result.verdict == 'pass' and result.completed_at == START+5*MINUTE


def test_failed_confirmation_remains_in_initial_population():
    rows = bars()
    original, _ = detect(rows)
    rows[4].update(C=112,H=113)
    changed, _ = detect(rows)
    assert original[0].to_dict() == changed[0].to_dict()
    failure = next_aligned_close(changed[0],rows,minutes=5)
    assert failure.verdict == 'fail' and failure.selected_signal_at is None
    # Later favorable closes cannot change the first endpoint failure.
    rows[9].update(C=95,L=94)
    assert next_aligned_close(changed[0],rows,minutes=5) == failure
    summary = population_summary([{'opportunity':changed[0].to_dict(),
                                   'replay':failure.to_dict(changed[0])}])
    assert summary['opportunities'] == summary['f'] == summary['N'] == 1
    assert summary['selected_signals'] == 0 and summary['actual_fills'] is None


def test_future_append_and_perturb_preserve_incorporated_fields():
    rows = bars()
    before, _ = detect(rows[:2])
    rows[-1].update(O=500,H=600,L=400,C=550)
    after, _ = detect(rows)
    assert [o.to_dict() for o in before] == [o.to_dict() for o in after]


def test_missing_firstness_interval_cannot_be_skipped_for_later_sweep():
    rows = bars()
    opportunities, holes = detect(rows[1:])
    assert opportunities == [] and holes == ['missing_initial_opportunity_interval']


def test_missing_confirmation_minute_is_unknown_not_later_success():
    rows = bars()
    opportunities, _ = detect(rows)
    result = next_aligned_close(opportunities[0],rows[:3]+rows[4:],minutes=5)
    assert result.verdict == 'unknown' and result.censored


def test_earlier_unavailable_reference_is_rejected_before_selection():
    reference = dict(REFERENCE, known_at=START+MINUTE)
    opportunities, holes = first_excursions(RULE,PARTITION,reference,bars(),registry_sha256='a'*64,
        action_start=START,expiry_at=START+10*MINUTE,sides=('short',))
    assert not opportunities and holes == ['reference_incomplete_or_unavailable']


def test_duplicate_and_foreign_bar_reject():
    rows = bars()
    with pytest.raises(ValueError,match='duplicate|overlapping'):
        detect(rows[:2]+rows[1:])
    rows[1]['instrument_id']=99
    with pytest.raises(ValueError,match='foreign'): detect(rows)


def test_later_vwap_touch_does_not_require_close_retake():
    opportunities, _ = detect(bars())
    opportunity = opportunities[0]
    rows = bars()
    rows[2].update(O=100,H=102,L=98,C=99)
    result = later_touch(opportunity,rows,lambda at: (Decimal(101),at))
    assert result.verdict == 'pass' and result.completed_at == START+3*MINUTE
    assert result.endpoint['C'] < result.endpoint['boundary_price']


def test_boundary_must_exist_before_contact():
    opportunity = detect(bars())[0][0]
    with pytest.raises(ValueError,match='future boundary'):
        later_touch(opportunity,bars(),lambda at:(101,at+1))


def test_duplicate_opportunity_rejected_from_denominator():
    opportunity = detect(bars())[0][0]
    result = next_aligned_close(opportunity,bars(),minutes=5)
    row = {'opportunity':opportunity.to_dict(),'replay':result.to_dict(opportunity)}
    with pytest.raises(ValueError,match='duplicate opportunity'): population_summary([row,row])
