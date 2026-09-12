from trading_research.research.method_pack.objects import RECIPES


def test_version_hash_is_stable_and_admin_fields_are_not_strategy_changes():
    first = {'A': True, 'T': 1, 'version': 'v1', 'frozen_at': 1}
    second = {'version': 'v2', 'frozen_at': 8, 'T': 2, 'A': True}
    values = {'v1': first, 'v2': second, 'frozen_at': 1, 'sample_start_at': 2,
              'sample_end_at': 5, 'comparison_at': 6, 'revision_at': 8,
              'review_block_id': 'block', 'revision_parent': 'block'}
    result = RECIPES['O137'](values)
    assert result.value['changed_fields'] == ['T']
    assert result.value['revision_causal'] is True
    reordered = {**values, 'v2': dict(reversed(list(second.items())))}
    assert RECIPES['O137'](reordered).value['definition_hash'] == result.value['definition_hash']
    assert RECIPES['O137']({**values, 'revision_at': 4}).base_ok is False
    assert RECIPES['O137']({**values, 'revision_parent': 'different-block'}).base_ok is False


def test_journal_keeps_late_rationale_and_outcome_identity_separate():
    row = {'decision_at': 5, 'feature_known_at': 6, 'outcome_at': 9,
           'input_record_id': 'input', 'outcome_record_id': 'outcome'}
    result = RECIPES['O146']({'eligible': ['a'], 'journal': {'a': row}})
    assert result.value['completeness'] is True
    assert result.value['pre_entry_fields_valid'] is False
    assert result.value['inputs_outcomes_separate'] is True
    row['outcome_record_id'] = 'input'
    assert RECIPES['O146']({'eligible': ['a'], 'journal': {'a': row}}).base_ok is False


def test_vintage_order_is_chronological_and_series_period_is_preserved():
    rows = [{'series_id': 'x', 'reference_period': '2026-03', 'available_at': 20, 'value': '1.5'},
            {'series_id': 'y', 'reference_period': '2026-03', 'available_at': 25, 'value': '99'},
            {'series_id': 'x', 'reference_period': '2026-03', 'available_at': 10, 'value': '2.0'}]
    values = {'series_id': 'x', 'reference_period': '2026-03', 'releases': rows,
              'as_of': 30, 'vintage_policy': 'latest_available'}
    assert str(RECIPES['O162'](values).value['value']) == '1.5'
    assert str(RECIPES['O162']({**values, 'as_of': 15}).value['value']) == '2.0'
    assert RECIPES['O162']({**values, 'as_of': 5}).state == 'hole'
    assert RECIPES['O162']({**values, 'vintage_policy': None}).state == 'hole'


def test_period_date_never_supplies_an_intraday_release_time():
    result = RECIPES['O162']({'releases': [{'at': '2026-03-31', 'value': 2}], 'as_of': 100})
    assert result.state == 'hole' and result.value['value'] is None
