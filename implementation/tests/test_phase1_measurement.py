"""Full-history measurement: no fabricated fills, ordering, or complete futures."""
from decimal import Decimal as D
from trading_research.research.method_pack.measurement_outcomes import (
    SECOND, MINUTE, signed_excursions, interval_extrema, boundary_order, measure_setup,
)


class Market:
    start = 0
    end = 120*MINUTE

    def __init__(self, rows=(), complete=True):
        self.rows = [dict(event_ns=t, known_at=t, price=D(str(p)), executed_size=q,
                          event_id=str(i)) for i, (t, p, q) in enumerate(rows)]
        self.complete = complete

    def local(self, start, end):
        return [r for r in self.rows if start <= r['event_ns'] < end]

    def coverage(self, start, end):
        return {'observed_scope_complete': self.complete, 'unknown_intervals': [] if self.complete else [[start, end]]}

    def bars(self, start, end, seconds=1):
        groups = {}
        for r in self.rows:
            t = r['event_ns']//SECOND*SECOND
            if start <= t and t+SECOND <= end:
                groups.setdefault(t, []).append(r['price'])
        return [dict(start=t, end=t+SECOND, H=max(ps), L=min(ps), bar_id=str(t)) for t, ps in sorted(groups.items())]

    def at(self, clock):
        return 10*MINUTE


def episode(**changes):
    return dict({'candidate_id': 'x', 'decision_at': MINUTE, 'side': 'long',
                 'method': 'GB-FAIL', 'branch': 'nyam_box', 'trigger': {},
                 'geometry': {'entry': 100, 'stop': 98, 'target': 103}}, **changes)


def test_excursions_signed_and_floored():
    assert signed_excursions(97, 106, 100, 'long')['favorable_points'] == 6
    assert signed_excursions(97, 106, 100, 'short')['favorable_points'] == 3
    assert signed_excursions(101, 102, 100, 'long')['adverse_points'] == 0


def test_extrema_exclude_decision_batch_and_include_fixed_endpoint():
    m = Market([(MINUTE, 300, 1), (MINUTE+1, 101, 1), (MINUTE+SECOND, 99, 1),
                (2*MINUTE, 105, 1), (2*MINUTE+1, 500, 1)])
    x = interval_extrema(m, MINUTE, 2*MINUTE)
    assert (x['low'], x['high']) == (99, 105)


def test_extrema_subsecond_horizon_does_not_duplicate_boundary():
    m = Market([(MINUTE+1, 101, 1), (MINUTE+2, 102, 1), (MINUTE+3, 99, 1)])
    assert interval_extrema(m, MINUTE+1, MINUTE+2)['low'] == 102


def test_same_timestamp_crossing_preserves_unresolved_order():
    m = Market([(MINUTE+SECOND, 103, 1), (MINUTE+SECOND, 98, 1)])
    x = boundary_order(m, episode(), {'at': MINUTE})
    assert x['result'] == 'unresolved_timestamp_order'
    assert len(x['event_ids']) == 2


def test_earlier_gap_does_not_certify_first_boundary():
    m = Market([(MINUTE+SECOND, 103, 1)], complete=False)
    x = boundary_order(m, episode(), {'at': MINUTE})
    assert x['result'] == 'unresolved_prior_coverage'
    assert x['observed_result'] == 'objective_observed'


def test_missing_target_preserves_defined_invalidation():
    m = Market([(MINUTE+SECOND, 97, 1)])
    x = boundary_order(m, episode(geometry={'entry': 100, 'stop': 98}), {'at': MINUTE})
    assert x['result'] == 'invalidation_observed'
    assert x['target'] is None and not x['both_boundaries_defined']


def test_favorable_extremum_never_implies_target_hit():
    m = Market([(MINUTE+SECOND, 101, 1)])
    assert boundary_order(m, episode(), {'at': MINUTE})['result'] == 'expired_without_observed_boundary'


def test_published_outbound_expiry_is_retained():
    m = Market([(11*MINUTE, 104, 1)])
    x = boundary_order(m, episode(method='JJ-TBR', branch='judas_outbound'), {'at': MINUTE})
    assert x['end_ns'] == 10*MINUTE
    assert x['result'] == 'expired_without_observed_boundary'


def test_horizon_truncation_never_reported_complete():
    m = Market([(119*MINUTE+SECOND, 101, 1)])
    x = measure_setup(m, episode(decision_at=119*MINUTE))
    assert all(r['horizon_truncated'] and r['extrema_are_lower_bounds'] for r in x['horizons'])


def test_price_only_pullback_is_measured_without_inventing_entry_or_target():
    m = Market([(MINUTE+SECOND, 101, 1)])
    x = measure_setup(m, episode(geometry={}, trigger={'C': 100, 'known_at': MINUTE, 'bar_id': 'close'}))
    assert x['origin']['kind'] == 'measurement_only_completed_trigger_close'
    assert x['boundary']['result'] == 'boundaries_not_defined'
    assert x['simulated_return'] is None


def test_missing_entry_fallback_is_whole_batch_not_favorable_print():
    m = Market([(MINUTE+SECOND, 99, 1), (MINUTE+SECOND, 103, 3), (MINUTE+2*SECOND, 104, 1)])
    x = measure_setup(m, episode(geometry={}))
    assert x['origin']['price'] == 102
    assert x['origin']['at'] == MINUTE+SECOND


def test_terminal_setup_remains_unresolved():
    m = Market()
    x = measure_setup(m, episode(decision_at=m.end))
    assert x['boundary']['result'] == 'missing_future_coverage'
    assert all(r['status'] == 'incomplete_future_coverage' for r in x['horizons'])


def test_annotation_and_missing_market_model_are_not_entry_denominators():
    from trading_research.research.method_pack.measurement_runner import measurement_scope, effective_omissions
    assert measurement_scope('GB-FAIL', 'mss_fvg_refinement') == 'supplemental_observation'
    m = Market(); m._earlier = {}
    missing = {'kind': 'original_source_audit_requirement', 'reason': 'no dated P-zone bands/destinations', 'operand': 'source_zone_known'}
    legacy = {'kind': 'original_source_audit_requirement', 'id': 'personal_limit'}
    active, resolved = effective_omissions(m, {'method_id': 'JJ-TBR', 'omissions': [missing, legacy]})
    assert active == [missing] and len(resolved) == 1
