from decimal import Decimal

from trading_research.research.method_pack.objects import RECIPES


def test_source_fraction_is_required_and_supplied_bins_are_summed():
    values = {'known_at': 10, 'total': 100, 'covered': 68}
    unspecified = RECIPES['O062'](values)
    assert unspecified.value['achieved_fraction'] == Decimal('.68')
    assert unspecified.value['meets_required'] is None
    assert RECIPES['O062']({**values, 'required_fraction': '.68'}).value['meets_required'] is True
    assert RECIPES['O062']({**values, 'required_fraction': '.70'}).value['meets_required'] is False
    bins = RECIPES['O062']({'known_at': 10, 'bins': {'100': 32, '101': 40, '102': 28},
                           'val': 101, 'vah': 102, 'boundary_convention': 'closed', 'required_fraction': '.68'})
    assert bins.value['volume_inside'] == 68 and bins.value['achieved_fraction'] == Decimal('.68')
    assert bins.value['construction_known'] is False
    for total, covered in [(0, 0), (10, 11), (10, -1)]:
        result = RECIPES['O062']({'known_at': 10, 'total': total, 'covered': covered})
        assert result.value['achieved_fraction'] is None
        assert result.state == ('hole' if total == 0 else 'invalid')


def test_poc_ties_preserve_all_candidates_and_only_apply_the_given_rule():
    values = {'bins': {'100': 4, '101': 10, '102': 10}, 'known_at': 10}
    unknown = RECIPES['O064']({**values, 'tie_rule': 'unpublished'})
    assert unknown.value['poc'] is None
    assert unknown.value['poc_candidates'] == [Decimal(101), Decimal(102)]
    assert RECIPES['O064']({**values, 'tie_rule': 'highest'}).value['poc'] == 102
    assert RECIPES['O064']({'bins': {}, 'known_at': 10}).state == 'hole'
    assert RECIPES['O064']({'bins': {'100': -1, '101': 1}, 'known_at': 10}).state == 'invalid'


def test_poc_tests_are_distinct_and_future_passage_is_not_visible():
    result = RECIPES['O095']({'poc': 105, 'failed_crosses': [1, 1, 2], 'passage_at': 4,
                              'retest_at': 5, 'as_of': 3, 'known_at': 3, 'use_at': 3})
    assert result.value['failed_test_count'] == 2
    assert result.value['passage_at'] is None and result.value['current_poc_read'] is None
    reverse = RECIPES['O095']({'poc': 105, 'passage_at': 5, 'retest_at': 4, 'use_at': 6})
    assert reverse.base_ok is False


def test_trapped_history_cannot_alias_one_resolved_failure_or_change_its_band():
    values = {'prior_failures': [{'id': 'a', 't': 1}, {'id': 'b', 't': 1}],
              'fail_at': 3, 'breakdown_at': 4, 'retest_at': 5, 'confirm_at': 6, 'entry_at': 7}
    assert RECIPES['O119'](values).value['distinct_failures'] == 1
    values['band_id'] = 'current'
    values['prior_failures'][0]['band_id'] = 'foreign'
    assert RECIPES['O119'](values).base_ok is False
