from decimal import Decimal

from trading_research.research.method_pack.objects import RECIPES


def test_zone_requires_actual_departure_and_strict_later_contact():
    values = {'known_at': 1, 'formed_at': 1, 'zone_id': 'zone-1', 'zone': [100, 101],
              'source_setting_id': 'setting-1', 'formation_event_ids': ['formation-1'],
              'departure_event_id': 'departure-1', 'departure_at': 2,
              'departure_price': 102, 'touches': [
                  {'touch_id': 'ignored-at-departure', 't': 2, 'price': 100},
                  {'touch_id': 'touch-1', 't': 3, 'price': 100.5},
                  {'touch_id': 'same-episode-row', 't': 4, 'price': 100.75}], 'use_at': 5}
    result = RECIPES['O116'](values)
    assert result.value['later_touches'] == 1
    assert result.value['touch_ids'] == ['touch-1']
    assert RECIPES['O116']({**values, 'departure_price': 100.5}).base_ok is False


def test_memory_keeps_unresolved_touch_and_excludes_current_outcome():
    values = {'cutoff': 9, 'current_touch_at': 10, 'current_touch_id': 'C', 'zone_id': 'z',
              'priors': [{'id': 'A', 'start': 1, 'defense_at': 3},
                         {'id': 'duplicate', 'start': 1, 'defense_at': 3},
                         {'id': 'B', 'start': 5, 'defense_at': 11},
                         {'id': 'C', 'start': 10, 'defense_at': 12}]}
    result = RECIPES['O117'](values)
    assert result.value['prior_touch_count'] == 2
    assert result.value['eligible_history_ids'] == ['A']
    assert result.value['unresolved_history_ids'] == ['B']
    assert result.value['resolved_defense_count'] == 1
    assert RECIPES['O117']({**values, 'selected_history_ids': ['A', 'C']}).base_ok is False


def test_equal_cohort_counts_do_not_prove_common_identities():
    values = {'eligible': 2, 'selected': 2, 'orders': 2, 'filled': 2, 'common_ids': True}
    assert RECIPES['O148'](values).value['pairable'] is None
    wrong = {**values, 'selected_ids': ['a', 'b'], 'filled_candidate_ids': ['c', 'd'],
             'common_ids': ['a', 'b'], 'claim_paired': True}
    assert RECIPES['O148'](wrong).base_ok is False
    partial = {'eligible': 1, 'selected': 1, 'orders': 1, 'filled': 1, 'eligible_ids': ['a'],
               'selected_ids': ['a'], 'common_ids': ['a'], 'order_records': [{'order_id': 'o', 'candidate_id': 'a'}],
               'fill_records': [{'fill_id': 'f1', 'order_id': 'o'}, {'fill_id': 'f2', 'order_id': 'o'}]}
    result = RECIPES['O148'](partial)
    assert result.value['filled'] == 1 and result.value['pairable'] is True


def test_cost_ticks_are_explicit_and_stop_slippage_is_not_a_target_charge():
    values = {'r_unit': 32, 'target_outcome': 95, 'stop_outcome': -34, 'quantity': 3,
              'tick_value': 2, 'round_trip_cost_ticks': 1, 'stop_slippage_ticks': 1,
              'gross_target_ticks': 96, 'gross_stop_ticks': 32}
    result = RECIPES['O152'](values)
    assert result.value['round_trip_cost'] == 6
    assert result.value['target_r'] == Decimal('2.96875')
    assert result.value['supplied_gross_net_consistency'] is True
    assert RECIPES['O152']({**values, 'target_outcome': 94}).base_ok is False
    assert RECIPES['O152']({**values, 'round_trip_cost_ticks': 2}).value['round_trip_cost'] == 12
