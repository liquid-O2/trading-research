"""Four original legacy helper holes retain complete, typed partial outputs."""
from copy import deepcopy
from datetime import date
from decimal import Decimal
import json
from pathlib import Path

import pytest

from trading_research.research.method_pack import objects  # noqa: F401
from trading_research.research.method_pack.clocks import et_ns
from trading_research.research.method_pack.contracts import (
    OUTPUT_SCHEMAS, OutputContractError, validate_output,
)
from trading_research.research.method_pack.native_resolution import NativeResolver, file_digest
from trading_research.research.method_pack.objects.native_boundary import run_native_object
from trading_research.research.method_pack.protocol import REQUIRED, RecipeResult, guard, run_recipe

PROBES = Path(__file__).parents[1] / 'reports/phase1-live/methods/charts/full-audit-probes.json'
MINUTE = 60_000_000_000
START = et_ns(date(2026, 1, 15), 10)


def original(probe_id):
    row = next(row for row in json.loads(PROBES.read_text())['probes'] if row['id'] == probe_id)
    return row['object_id'], deepcopy(row['input'])


@pytest.mark.parametrize('probe_id', ['P01', 'P03', 'P04', 'P08'])
def test_original_legacy_counterexample_returns_its_full_hole_schema(probe_id):
    rid, inputs = original(probe_id)
    before = deepcopy(inputs)
    result = validate_output(run_recipe(rid, inputs))
    assert inputs == before
    assert result.recipe_id == rid
    assert result.state == 'hole'
    assert result.coverage_ok is None
    assert result.hole_ids
    assert set(OUTPUT_SCHEMAS[rid]) <= set(result.value)
    assert result.evidence_class == 'research_helper'


def test_untimed_coverage_keeps_guard_unknowns_and_supplied_bar_literals():
    rid, inputs = original('P01')
    blocked = guard(inputs, rid, REQUIRED[rid])
    result = validate_output(run_recipe(rid, inputs))
    assert result.value['bars'] == inputs['bars']
    assert result.base_ok is result.coverage_ok is result.known_at is None
    assert result.hole_ids == blocked.hole_ids
    assert result.value['coverage_ok'] is None
    assert result.value['base_identity_ok'] is None
    assert result.value['price_coverage'] is None
    assert result.value['side_coverage'] is None
    assert result.value['missing_intervals'] == []
    assert result.value['available_depth'] == 'unresolved'
    assert set(result.value['missing_fields']) == {'instrument_id', 'start_ns', 'end_ns', 'required_fields'}


def test_unverified_scalar_clock_preserves_prices_without_inventing_native_identity():
    rid, inputs = original('P03')
    result = validate_output(run_recipe(rid, inputs))
    assert result.recipe_id == 'O006'
    assert result.value['L'] == Decimal(200)
    assert result.value['H'] == Decimal(208)
    assert result.value['formation_start'] == inputs['start_ns']
    assert result.value['formation_end'] == inputs['end_ns']
    for name in ('range_id', 'instrument_id', 'source_clock_id', 'W', 'known_at',
                 'range_known_at', 'source_clock_verified'):
        assert result.value[name] is None
    assert result.value['range_frozen'] is False
    assert result.value['member_ids'] == []
    assert result.base_ok is result.coverage_ok is result.known_at is None
    assert all(hole.startswith('HOLE:O006:') for hole in result.hole_ids)


def test_unknown_coordinate_convention_does_not_choose_a_foreign_width():
    rid, inputs = original('P04')
    result = validate_output(run_recipe(rid, inputs))
    assert result.value['upper_band'] is result.value['lower_band'] is None
    assert result.value['parent_id'] == 'inner'
    assert result.known_at == result.value['known_at'] == inputs['known_at']
    assert result.base_ok is True
    assert result.hole_ids == ['HOLE:O015:coordinate_convention']


def test_thin_three_candle_record_retains_literals_and_unknown_confirmation():
    rid, inputs = original('P08')
    blocked = guard(inputs, rid, REQUIRED[rid])
    result = validate_output(run_recipe(rid, inputs))
    assert result.value['c2'] == inputs['c2']
    assert result.known_at == inputs['known_at'] == blocked.known_at
    assert result.base_ok is result.coverage_ok is None
    assert result.hole_ids == blocked.hole_ids
    for name in ('ob_band', 'ob_mid', 'confirmation_at', 'confirmed', 'sweep_side',
                 'selected_entry_mode', 'selected_stop', 'timeframe'):
        assert result.value[name] is None
    assert result.value['candle_ids'] == []


@pytest.mark.parametrize('rid', ['O001', 'O006', 'O015', 'O056'])
def test_full_schema_still_rejects_blank_computed_payloads(rid):
    with pytest.raises(OutputContractError, match='missing required output'):
        validate_output(RecipeResult(rid, 'computed', {}))


def test_domain_hole_normalization_does_not_soften_invalid_identity_guard():
    rid, inputs = original('P01')
    inputs.update(instrument_id='NQ', dependencies=[{'instrument_id': 'ES'}])
    result = validate_output(run_recipe(rid, inputs))
    assert result.state == 'invalid'
    assert result.base_ok is False
    assert result.value == {}


@pytest.fixture
def native_rows(tmp_path):
    dataset = 'quantpad/cme__nq-continuous-futures__ohlcv-1m'
    path = tmp_path / dataset / 'three-candles.json'
    path.parent.mkdir(parents=True)
    prices = [(102, 103, 101, 102), (102, 104, 100, 103), (103, 106, 102, 105)]
    rows = [dict(t=(START + i * MINUTE) // 1_000_000, o=o, h=h, l=l, c=c, v=100,
                 instrument_id=7) for i, (o, h, l, c) in enumerate(prices)]
    path.write_text(json.dumps(rows))
    end = START + 3 * MINUTE
    locator = dict(source_file=str(path), dataset_id=dataset, sha256=file_digest(path),
                   row_start=0, row_end=3)
    resolver = NativeResolver(tmp_path, owned_spans=[dict(path=str(path), start_ns=START, end_ns=end)])
    obj = dict(instrument_id=7, formation_start=START, formation_end=end, as_of=end,
               known_at=end, raw_member_locators=[locator])
    return resolver, obj


def test_computed_native_coverage_and_bar_controls_keep_exact_measurements(native_rows):
    resolver, obj = native_rows
    coverage = validate_output(run_native_object({**obj, 'recipe_id': 'O001',
        'inputs': {'required_fields': ['ohlcv']}}, resolver))
    assert coverage.state == 'computed'
    assert coverage.base_ok is coverage.coverage_ok is True
    assert coverage.value['price_coverage'] is True
    assert coverage.value['missing_intervals'] == []
    bar = validate_output(run_native_object({**obj, 'recipe_id': 'O004',
        'inputs': {'kind': 'time', 'size_minutes': 3}}, resolver))
    assert bar.state == 'computed'
    assert bar.value['O'] == 102 and bar.value['H'] == 106
    assert bar.value['L'] == 100 and bar.value['C'] == 105 and bar.value['V'] == 300
    assert coverage.known_at == bar.known_at == obj['formation_end']
    assert coverage.evidence_class == bar.evidence_class == 'resolved_native'


def test_native_range_and_identified_candles_keep_geometry_and_source_limits(native_rows):
    resolver, obj = native_rows
    manual = validate_output(run_native_object({**obj, 'recipe_id': 'O006',
        'inputs': {'source_clock_verified': True}}, resolver))
    assert manual.value['L'] == 100 and manual.value['H'] == 106 and manual.value['W'] == 6
    assert manual.value['range_id'] and len(manual.value['member_ids']) == 3
    # Ownership locators do not themselves attest the source range's coverage.
    assert manual.value['range_frozen'] is False
    assert manual.value['source_clock_verified'] is None
    assert manual.state == 'hole'  # Caller flags still cannot verify a source clock.
    resolved = resolver.resolve(obj['raw_member_locators'], instrument_id=7,
        start_ns=START, end_ns=obj['formation_end'], as_of=obj['as_of'])
    candle_rows = resolved.rows()
    ids = [row['bar_id'] for row in candle_rows]
    pattern = validate_output(run_native_object({**obj, 'recipe_id': 'O056',
        'inputs': {'candle_ids': ids, 'variant': 'comparison', 'measurement_side': 'low'}}, resolver))
    assert pattern.value['ob_band'] == [Decimal(100), Decimal(104)]
    assert pattern.value['ob_mid'] == 102
    assert pattern.value['confirmed'] is True
    assert pattern.value['candle_ids'] == ids
    assert pattern.value['confirmation_at'] == obj['formation_end']
    assert pattern.value['selected_entry_mode'] is pattern.value['selected_stop'] is None
    assert pattern.state == 'hole'
    # Full identified helper records still compute their declared policy; they
    # keep the research-helper class rather than acquiring native provenance.
    candles = [{**row, 'candle_id': row['bar_id']} for row in candle_rows]
    helper = validate_output(run_recipe('O056', dict(c1=candles[0], c2=candles[1], c3=candles[2],
        sweep_side='low', selected_entry_mode='midpoint', selected_stop=100)))
    assert helper.state == 'computed' and helper.value['confirmed'] is True
    assert helper.evidence_class == 'research_helper'
    bands = validate_output(run_recipe('O015', dict(L=100, H=106, parent_id=manual.value['range_id'],
        coordinate_convention_verified=True, known_at=obj['known_at'])))
    assert bands.state == 'computed'
    assert bands.value['upper_band'] == [Decimal('113.98'), Decimal('115.96')]
    assert bands.value['lower_band'] == [Decimal('90.04'), Decimal('92.02')]
