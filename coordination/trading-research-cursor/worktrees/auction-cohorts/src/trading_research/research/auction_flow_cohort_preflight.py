"""Actual whole-window and one-minute unpublished cohort validation.

This is a bounded exact-arithmetic and resource probe. It does not admit F11
serving, merge source variants, or start a Context/Location study.
"""
from __future__ import annotations

from fractions import Fraction
import time

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.units import Ticks
from trading_research.measurements.cvd import (
    CohortChannel, CohortDefinition, _cohort_path, exact_number, fixed_source_cohort,
)
from trading_research.measurements.tape import Trade
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_cohorts import (
    BATCH_ROWS, MAX_PRINTS, CohortWindow, TradeSizeHistogram, fit_unpublished_cohort_definition,
)
from trading_research.research.auction_flow_storage import read_json_artifact, read_series_tables
from trading_research.research.auction_flow_windows import TRADE_FIELDS, prepare_trade_batch


VERSION = 'auction-flow-actual-cohort-validation-v1'
CONTRACT_KIND = 'auction_flow_actual_cohort_validation_contract_v1'
TRAINING_DATE = '2020-03-16'
TRAINING_KIND = 'auction_flow_source_resource_unit'
AGGREGATION_UNIT = 'provider-reported-trade-record'
FIXED_FILTERS = ('all', 'ny_ge100', 'london_ge75', 'inclusive30_through60')
SOFT_KNOTS = (1, 30, 61, 75, 100)
PREFIX_LIMIT = 4096
PREFIX_PROBE = 4097
ADAPTIVE_RECIPES = (
    ('count_quartiles', 'count', ((1, 4), (1, 2), (3, 4))),
    ('volume_quartiles', 'volume', ((1, 4), (1, 2), (3, 4))),
    ('source_top35_count_quantile', 'count', ((13, 20),)),
)
SOURCE_VARIANTS = (
    'Current units retain separate original acquired streams; selecting one complete '
    'retained 2020 training reference for this cost probe does not merge or discard source variants.')
TRAINING_SCOPE = (
    'Bounded complete timestamp groups in the first up-to-4096 eligible prints from the '
    'retained complete 2020-03-16 resource unit, separately per root. This validates exact '
    'unpublished arithmetic and resource cost; it is not the complete 2020-2022 training '
    'cohort or an admitted F11 fit.')
_BOUNDED_ARITHMETIC = 'bounded resource arithmetic, not a full historical fit'
_UNPUBLISHED = 'unpublished mathematical calculations'
_NO_INTERVAL = 'unavailable_no_positive_interval_after_training_availability'
_BEFORE_AVAIL = 'unavailable_before_training_availability'
_EMPTY_TRAIN = 'unavailable_empty_training_prefix'
_EMPTY_SCALAR = 'unavailable_empty_scalar_prefix_after_timestamp_group_trim'
_EMPTY_SCALAR_INTERVAL = 'unavailable_empty_scalar_prefix'
_COMMON = ('open', 'high', 'low', 'close', 'high_at_ns', 'low_at_ns', 'high_source_order',
           'low_source_order', 'buy', 'sell', 'unknown', 'volume', 'observed_signed_lower',
           'observed_signed_upper', 'true_signed_lower', 'true_signed_upper')
_CHANNEL_FIELDS = (
    'channel_id', 'role', 'open', 'high', 'low', 'close', 'high_at_ns', 'low_at_ns',
    'high_source_order', 'low_source_order', 'high_origin', 'low_origin', 'buy', 'sell',
    'unknown', 'volume', 'signed', 'weighted_prints', 'contributing_prints', 'count_occupancy',
    'volume_occupancy', 'observed_signed_lower', 'observed_signed_upper', 'true_signed_lower',
    'true_signed_upper', 'empty_observed_channel', 'history_complete')
_BAR_FIELDS = (
    'bin', 'event_start_ns', 'event_end_ns', 'known_at_ns', 'supported_start_ns',
    'supported_end_ns', 'clipped', 'source_coverage_complete', 'coordinate_complete',
    'prints', 'volume', 'empty_observed_window', 'partition_volume', 'partition_weighted_prints')
_CPU_NAMES = (
    'training_cache_validation_and_selection',
    'histogram_accumulation_fit_and_reference_arithmetic',
    'current_cache_decoding',
    'preparation_and_filtering',
    'whole_path_updates',
    'atomic_path_updates',
    'whole_atomic_finalization',
    'original_source_comparisons',
    'full_atom_composition',
    'bounded_scalar_reference',
    'serialization',
    'orchestration_and_report_assembly',
)


def _cpu():
    return {name: 0.0 for name in _CPU_NAMES}


def _acc(cpu, name, started):
    cpu[name] += time.process_time() - started
    return time.process_time()


def _counts():
    return {'decoded_rows': 0, 'decoded_batches': 0,
            'training_decoded_rows': 0, 'training_decoded_batches': 0,
            'current_decoded_rows': 0, 'current_decoded_batches': 0,
            'prepared_prints': 0, 'sliced_prints': 0,
            'instantiated_bars': 0, 'report_bars': 0, 'report_channels': 0,
            'full_path_print_contributions': 0, 'scalar_reference_prints': 0,
            'scalar_reference_channels': 0, 'scalar_reference_sliced_prints': 0,
            'serialized_bytes': 0}


def _exact_int(value, *, name):
    if type(value) is not int:
        raise IntegrityError(f'{name} must be an actual integer')
    return value


def _pairs(values):
    if type(values) not in (tuple, list):
        raise ContractError('declared adaptive recipes are not the registered unpublished set')
    pairs = []
    for item in values:
        if type(item) not in (tuple, list) or len(item) != 2:
            raise ContractError('declared adaptive recipes are not the registered unpublished set')
        a, b = item
        if type(a) is not int or type(b) is not int:
            raise ContractError('declared adaptive recipes are not the registered unpublished set')
        pairs.append((a, b))
    return tuple(pairs)


def _exact_int_sequence(values, expected, *, name):
    if type(values) not in (tuple, list) or len(values) != len(expected):
        raise ContractError(f'cohort validation contract changed its registered {name}')
    if any(type(item) is not int for item in values):
        raise ContractError(f'cohort validation contract changed its registered {name}')
    if tuple(values) != expected:
        raise ContractError(f'cohort validation contract changed its registered {name}')
    return tuple(values)


def _fractions(pairs):
    return tuple(Fraction(a, b) for a, b in pairs)


def _validate_contract(contract):
    if type(contract) is not dict or contract.get('kind') != CONTRACT_KIND:
        raise ContractError('auction cohort validation contract kind is not the registered v1 object')
    if (contract.get('aggregation_unit') != AGGREGATION_UNIT
            or type(contract.get('atomic_width_ns')) is not int
            or contract.get('atomic_width_ns') != 60_000_000_000
            or type(contract.get('maximum_training_prefix_prints')) is not int
            or contract.get('maximum_training_prefix_prints') != PREFIX_LIMIT
            or type(contract.get('maximum_literal_reference_prints_per_definition_instrument')) is not int
            or contract.get('maximum_literal_reference_prints_per_definition_instrument') != PREFIX_LIMIT
            or tuple(contract.get('fixed_filters') or ()) != FIXED_FILTERS
            or contract.get('all_original_source_checks_retained') is not True
            or contract.get('full_window_and_all_one_minute_bars') is not True
            or contract.get('context_or_location_evaluation') is not False
            or contract.get('f11_serving_admitted') is not False
            or contract.get('family_statistics_complete') is not False
            or contract.get('source_variants') != SOURCE_VARIANTS
            or contract.get('training_scope') != TRAINING_SCOPE):
        raise ContractError('cohort validation contract changed its registered limits or family scope')
    _exact_int_sequence(contract.get('fixed_soft_knots'), SOFT_KNOTS, name='soft knots')
    recipes = contract.get('adaptive_definitions')
    if type(recipes) is not list or len(recipes) != len(ADAPTIVE_RECIPES):
        raise ContractError('declared adaptive recipes are not the registered unpublished set')
    for got, (name, weighting, pairs) in zip(recipes, ADAPTIVE_RECIPES, strict=True):
        if (type(got) is not dict or got.get('name') != name or got.get('weighting') != weighting
                or _pairs(got.get('probabilities') or ()) != pairs):
            raise ContractError('declared adaptive recipes are not the registered unpublished set')
    units = contract.get('training_resource_units')
    if type(units) is not dict or set(units) != {'ES', 'NQ'}:
        raise ContractError('training resource units must be declared separately for NQ and ES')
    for root, reference in units.items():
        if (type(reference) is not dict or reference.get('kind') != TRAINING_KIND
                or type(reference.get('path')) is not str or not reference['path']
                or type(reference.get('sha256')) is not str or len(reference['sha256']) != 64
                or type(reference.get('size_bytes')) is not int or reference['size_bytes'] < 1):
            raise ContractError(f'{root} training resource reference is not a complete size/hash-bound unit')


def _require_series(table):
    if any(name not in table.column_names for name in TRADE_FIELDS):
        raise IntegrityError('retained trade series lost a required raw field projection')
    if len(table) > BATCH_ROWS:
        raise IntegrityError('retained trade series exceeded the source batch row bound')


def _unique_source_key(table):
    import pyarrow.compute as pc

    keys = pc.unique(table['source_key']).to_pylist()
    if len(keys) != 1 or type(keys[0]) is not str or not keys[0]:
        raise IntegrityError('a cohort window cannot join distinct acquired source streams')
    return keys[0]


def _filter_instrument(table, instrument_id):
    import pyarrow.compute as pc

    return table.filter(pc.equal(table['instrument_id'], instrument_id))


def _prepared_label(array, index):
    value = array[index]
    return value.as_py() if hasattr(value, 'as_py') else value


def _row_tuple(prepared, index):
    values = prepared.values
    return {
        't': int(values['t'][index]),
        'source_order': int(values['source_order'][index]),
        'source_row': int(values['source_row'][index]),
        'source_key': prepared.source_key(index),
        'instrument_id': int(values['instrument_id'][index]),
        'size': int(values['size'][index]),
        'side': int(values['side'][index]),
        'price': int(values['price'][index]),
        'price_valid': int(values['price_valid'][index]),
        'known_at_ns': int(values['known_at_ns'][index]),
        'raw_flags': int(values['raw_flags'][index]),
        'raw_side': _prepared_label(prepared._raw_side, index),
        'raw_action': _prepared_label(prepared._raw_action, index),
    }


def _address(row):
    return {name: row[name] for name in (
        't', 'source_row', 'source_order', 'source_key', 'raw_flags', 'raw_side', 'raw_action')}


def _prefix_digest(rows):
    return digest(tuple((r['t'], r['source_order'], r['source_row'], r['source_key'],
                         r['size'], r['side'], r['raw_flags'], r['raw_side'], r['raw_action'])
                        for r in rows))


def _trim_complete_groups(rows, *, entire_unit):
    if len(rows) <= PREFIX_LIMIT:
        return list(rows), False
    if entire_unit:
        return list(rows[:PREFIX_LIMIT]), False
    if rows[PREFIX_LIMIT - 1]['t'] == rows[PREFIX_LIMIT]['t']:
        stamp = rows[PREFIX_LIMIT - 1]['t']
        return [row for row in rows[:PREFIX_LIMIT] if row['t'] != stamp], True
    return list(rows[:PREFIX_LIMIT]), False


def _literal_quantile(sizes, probabilities, weighting):
    ordered = sorted(int(size) for size in sizes)
    if not ordered:
        raise IntegrityError('literal quantile reference requires the selected training sizes')
    total = len(ordered) if weighting == 'count' else sum(ordered)
    thresholds = []
    for probability in probabilities:
        mass = 0
        chosen = None
        for size in ordered:
            mass += 1 if weighting == 'count' else size
            if mass >= probability * total:
                chosen = size + 1
                break
        if chosen is None:
            raise IntegrityError('literal quantile mass never reached the requested interior probability')
        thresholds.append(chosen)
    cuts = (1, *sorted(set(thresholds)), None)
    realized_count = []
    realized_volume = []
    for lower, upper in zip(cuts, cuts[1:]):
        count = volume = 0
        for size in ordered:
            if size >= lower and (upper is None or size < upper):
                count += 1
                volume += size
        realized_count.append(count)
        realized_volume.append(volume)
    return {'requested_thresholds': tuple(thresholds), 'cuts': cuts,
            'realized_count': tuple(realized_count), 'realized_volume': tuple(realized_volume)}


def _compare_fit(fitted, literal, definition_name):
    recipe = fitted['recipe']
    if recipe['requested_thresholds'] != literal['requested_thresholds']:
        raise IntegrityError(f'{definition_name} unpublished thresholds differ from the independent size+1 rule')
    channels = fitted['definition'].channels
    expected = tuple(zip(literal['cuts'], literal['cuts'][1:]))
    got = tuple((channel.lower_inclusive, channel.upper_exclusive) for channel in channels)
    if got != expected:
        raise IntegrityError(f'{definition_name} unpublished channel intervals differ from the independent size+1 rule')
    if fitted['realized_count'] != literal['realized_count'] or fitted['realized_volume'] != literal['realized_volume']:
        raise IntegrityError(f'{definition_name} realized count/volume differ from the independent training sizes')


def _load_training(contract, unit):
    root = unit.get('root')
    if root not in ('ES', 'NQ'):
        raise ContractError('current unit root is not a declared training resource root')
    declared = contract['training_resource_units'][root]
    loaded = read_json_artifact(declared)
    training_unit = loaded.get('unit')
    quality = loaded.get('instrument_quality')
    storage = (loaded.get('event_storage') or {}).get('trades')
    measurement_ref = loaded.get('measurement')
    if (type(training_unit) is not dict or type(quality) is not list or type(storage) is not dict
            or type(measurement_ref) is not dict):
        raise IntegrityError('declared training resource unit lost its retained unit, series or measurement identity')
    if (training_unit.get('root') != root or training_unit.get('cash_date') != TRAINING_DATE
            or declared.get('kind') != TRAINING_KIND):
        raise IntegrityError('declared training resource is not the complete 2020-03-16 unit for this root')
    complete = [row for row in quality if (row.get('coordinate') or {}).get('complete') is True]
    if len(complete) != 1:
        raise IntegrityError('training member must contain exactly one complete coordinate')
    member = complete[0]
    if member.get('whole_flow_complete') is not True:
        raise IntegrityError('training member source window is not complete')
    measured = read_json_artifact(measurement_ref)
    instruments = [row for row in measured.get('instruments') or []
                   if row.get('instrument_id') == member['instrument_id']]
    if len(instruments) != 1:
        raise IntegrityError('training measurement does not retain the declared complete instrument')
    instrument = instruments[0]
    if (instrument.get('coordinate', {}).get('complete') is not True
            or instrument.get('whole_window', {}).get('source_coverage_complete') is not True
            or instrument.get('whole_window', {}).get('flow_history_complete') is not True):
        raise IntegrityError('training member is not a complete retained source/coordinate window')
    unit_start = _exact_int(training_unit.get('event_start_ns'), name='training unit event_start_ns')
    unit_end = _exact_int(training_unit.get('event_end_ns'), name='training unit event_end_ns')
    meas_start = _exact_int(measured.get('event_start_ns'), name='training measurement event_start_ns')
    meas_end = _exact_int(measured.get('event_end_ns'), name='training measurement event_end_ns')
    meas_known = _exact_int(measured.get('known_at_ns'), name='training measurement known_at_ns')
    if (unit_start, unit_end) != (meas_start, meas_end):
        raise IntegrityError('training measurement bounds do not equal the training unit bounds')
    if meas_known < meas_end:
        raise IntegrityError('training known_at must be at or after the retained training end')
    manifest = loaded.get('source_manifest')
    if type(manifest) is not dict:
        raise IntegrityError('training resource lost its retained source_manifest')
    delay = manifest.get('event_latency_scenario_ns')
    if type(delay) is not int:
        raise IntegrityError('training source_manifest event_latency_scenario_ns is missing')
    if delay != meas_known - meas_end:
        raise IntegrityError('training event_latency_scenario_ns does not equal known_at-end')
    if not 0 <= delay <= 1_000_000_000:
        raise IntegrityError('training resource lost its retained source delay')
    return {
        'declared': declared, 'loaded': loaded, 'unit': training_unit, 'storage': storage,
        'measurement_reference': measurement_ref, 'measured': measured, 'instrument': instrument,
        'instrument_id': _exact_int(member.get('instrument_id'), name='training instrument_id'),
        'delay': delay, 'start_ns': unit_start, 'end_ns': unit_end,
        'source_complete': True, 'coordinate_complete': True,
    }


def _count_decode(counts, table, *, prefix):
    counts[f'{prefix}_decoded_batches'] += 1
    counts[f'{prefix}_decoded_rows'] += len(table)
    counts['decoded_batches'] += 1
    counts['decoded_rows'] += len(table)


def _collect_training_prefix(training, counts):
    rows = []
    collecting = True
    source_key = None
    last_t = last_order = None
    eligible = 0
    for table in read_series_tables(training['storage']):
        _count_decode(counts, table, prefix='training')
        _require_series(table)
        kept = _filter_instrument(table, training['instrument_id'])
        if not len(kept):
            continue
        key = _unique_source_key(kept)
        if source_key is None:
            source_key = key
        elif key != source_key:
            raise IntegrityError('a cohort window cannot join distinct acquired source streams')
        t = kept['t'].to_pylist()
        order = kept['source_order'].to_pylist()
        if any(stamp < training['start_ns'] or stamp >= training['end_ns'] for stamp in t):
            raise IntegrityError('training series print is outside the retained training window')
        if last_t is not None and (t[0] < last_t or order[0] <= last_order):
            raise IntegrityError('training series lost original source order')
        if any(t[i] < t[i - 1] or order[i] <= order[i - 1] for i in range(1, len(t))):
            raise IntegrityError('training series lost original source order')
        last_t, last_order = t[-1], order[-1]
        delay = kept['known_at_ns'].to_pylist()
        if any(known != stamp + training['delay'] for stamp, known in zip(t, delay)):
            raise IntegrityError('training series delay does not match the retained source delay')
        eligible += len(kept)
        if not collecting:
            continue
        prepared = prepare_trade_batch(kept)
        try:
            for index in range(len(prepared)):
                if len(rows) >= PREFIX_PROBE:
                    collecting = False
                    break
                rows.append(_row_tuple(prepared, index))
        finally:
            prepared.close()
    entire = eligible <= PREFIX_LIMIT
    selected, truncated = _trim_complete_groups(rows, entire_unit=entire)
    return selected, eligible, source_key, entire, truncated


def _training_member(training, selected, contract, *, truncated):
    if not selected:
        return None
    end = selected[-1]['t'] + 1
    published = end + training['delay']
    identity = digest({
        'unit': {'path': training['declared']['path'], 'sha256': training['declared']['sha256'],
                 'size_bytes': training['declared']['size_bytes'], 'kind': training['declared']['kind']},
        'series_rows': training['storage']['rows'], 'series_sha': tuple(f['sha256'] for f in training['storage']['files']),
        'selected_count': len(selected),
        'first': {name: selected[0][name] for name in ('source_row', 'source_order', 'source_key')},
        'last': {name: selected[-1][name] for name in ('source_row', 'source_order', 'source_key')},
        'prefix_digest': _prefix_digest(selected), 'end': end, 'published_at': published,
        'data_scope': training['unit'].get('source_path'), 'fold_scope': TRAINING_SCOPE,
        'root': training['unit']['root'], 'cash_date': TRAINING_DATE,
    })
    return {
        'id': identity, 'start_ns': training['start_ns'], 'end_ns': end, 'published_at': published,
        'train_end': published, 'available_at': published, 'selected_count': len(selected),
        'first': _address(selected[0]), 'last': _address(selected[-1]),
        'prefix_digest': _prefix_digest(selected),
        'truncated_final_timestamp_group': truncated,
        'history_complete': True,
        'source_window_complete': True,
        'aggregation_unit': contract['aggregation_unit'],
        'training_scope': TRAINING_SCOPE,
    }


def _fit_training(selected, member, contract, counts):
    if member is None:
        return None, _EMPTY_TRAIN
    manifests = {
        'kind': 'bounded_resource_arithmetic',
        'statement': _BOUNDED_ARITHMETIC,
        'admitted_historical_training_sample': False,
        'training_scope': TRAINING_SCOPE,
        'member_id': member['id'],
        'root_date': TRAINING_DATE,
    }
    histogram = TradeSizeHistogram(source_manifest=manifests, fold_manifest=dict(manifests),
                                   aggregation_unit=contract['aggregation_unit'])
    histogram.add_sizes([row['size'] for row in selected], member_id=member['id'])
    report = histogram.record(coverage_complete=True)
    histogram.close()
    sizes = [row['size'] for row in selected]
    fits = {}
    windows = {member['id']: {'end': member['end_ns'], 'published_at': member['published_at'],
                              'history_complete': True}}
    for spec in contract['adaptive_definitions']:
        name, weighting, pairs = spec['name'], spec['weighting'], _pairs(spec['probabilities'])
        probabilities = _fractions(pairs)
        fitted = fit_unpublished_cohort_definition(
            report, train_end=member['train_end'], available_at=member['available_at'],
            member_identities=(member['id'],), aggregation_unit=contract['aggregation_unit'],
            probabilities=probabilities, weighting=weighting, version=name, member_windows=windows)
        literal = _literal_quantile(sizes, probabilities, weighting)
        _compare_fit(fitted, literal, name)
        fits[name] = {
            'definition': fitted['definition'], 'recipe': fitted['recipe'],
            'realized_count': fitted['realized_count'], 'realized_volume': fitted['realized_volume'],
            'realized_count_occupancy': fitted['realized_count_occupancy'],
            'realized_volume_occupancy': fitted['realized_volume_occupancy'],
            'publication_status': fitted['publication_status'],
            'literal_requested_thresholds': literal['requested_thresholds'],
            'histogram_identity': fitted['histogram_identity'],
        }
    return fits, None


def _all_definition(unit_name):
    return CohortDefinition(unit_name, AGGREGATION_UNIT, (CohortChannel('all', 1, None),))


def _soft_definition():
    return CohortDefinition('soft-benchmark-knots-v1', AGGREGATION_UNIT, (), SOFT_KNOTS)


def _definition_plan(fits, unavailable, unit_start, unit_end):
    plan = []
    for name in FIXED_FILTERS:
        definition = _all_definition('all') if name == 'all' else fixed_source_cohort(name)
        plan.append({'name': name, 'kind': 'fixed_source', 'definition': definition,
                     'start_ns': unit_start, 'end_ns': unit_end, 'unavailable': None,
                     'compare_original': True})
    plan.append({'name': 'soft_benchmark_knots', 'kind': 'fixed_soft', 'definition': _soft_definition(),
                 'start_ns': unit_start, 'end_ns': unit_end, 'unavailable': None,
                 'compare_original': False})
    for name, _, _ in ADAPTIVE_RECIPES:
        if unavailable is not None:
            plan.append({'name': name, 'kind': 'adaptive', 'definition': None,
                         'start_ns': None, 'end_ns': None, 'unavailable': unavailable,
                         'compare_original': False})
            continue
        definition = fits[name]['definition']
        start = max(unit_start, definition.available_at)
        if start >= unit_end:
            plan.append({'name': name, 'kind': 'adaptive', 'definition': definition,
                         'start_ns': start, 'end_ns': unit_end, 'unavailable': _NO_INTERVAL,
                         'compare_original': False})
            continue
        if start < definition.available_at:
            raise IntegrityError('adaptive cohort start preceded training availability')
        plan.append({'name': name, 'kind': 'adaptive', 'definition': definition,
                     'start_ns': start, 'end_ns': unit_end, 'unavailable': None,
                     'compare_original': False})
    if len(plan) != 8:
        raise IntegrityError('current unit must evaluate the eight registered cohort definitions')
    return plan


def _decode_current(trade_storage, instrument_ids, delay, start_ns, end_ns, counts):
    grouped = {raw_id: [] for raw_id in instrument_ids}
    keys = {raw_id: None for raw_id in instrument_ids}
    last = {raw_id: (None, None) for raw_id in instrument_ids}
    partitioned = 0
    for table in read_series_tables(trade_storage):
        _count_decode(counts, table, prefix='current')
        _require_series(table)
        assigned = 0
        for raw_id in instrument_ids:
            kept = _filter_instrument(table, raw_id)
            if not len(kept):
                continue
            assigned += len(kept)
            key = _unique_source_key(kept)
            if keys[raw_id] is None:
                keys[raw_id] = key
            elif key != keys[raw_id]:
                raise IntegrityError('a cohort window cannot join distinct acquired source streams')
            t = kept['t'].to_pylist()
            order = kept['source_order'].to_pylist()
            known = kept['known_at_ns'].to_pylist()
            prev_t, prev_order = last[raw_id]
            if prev_t is not None and (t[0] < prev_t or order[0] <= prev_order):
                raise IntegrityError('current series lost original source order')
            if any(t[i] < t[i - 1] or order[i] <= order[i - 1] for i in range(1, len(t))):
                raise IntegrityError('current series lost original source order')
            if any(stamp < start_ns or stamp >= end_ns for stamp in t):
                raise IntegrityError('current series print is outside the retained unit window')
            if any(item != stamp + delay for stamp, item in zip(t, known)):
                raise IntegrityError('current series delay does not match the retained source delay')
            last[raw_id] = (t[-1], order[-1])
            grouped[raw_id].append(kept)
        if assigned != len(table):
            raise IntegrityError('retained trade does not belong to a declared current raw instrument')
        partitioned += assigned
    if partitioned != counts['current_decoded_rows']:
        raise IntegrityError('retained and partitioned current trade counts do not reconcile')
    return grouped, keys


def _prepare_groups(grouped, counts):
    prepared = {}
    try:
        for raw_id, tables in grouped.items():
            items = []
            prepared[raw_id] = items
            for table in tables:
                batch = prepare_trade_batch(table)
                items.append(batch)
                counts['prepared_prints'] += len(batch)
        return prepared
    except BaseException:
        _release(prepared)
        raise


def _release(prepared):
    for items in prepared.values():
        for batch in items:
            if not batch.released:
                batch.close()


def _bounds(prepared, start_ns, end_ns):
    import numpy as np

    if not len(prepared):
        return 0, 0
    stamps = prepared.values['t']
    left = int(np.searchsorted(stamps, start_ns, side='left'))
    right = int(np.searchsorted(stamps, end_ns, side='left'))
    return left, right


def _add_slices(window, batches, start_ns, end_ns, counts, *, contribution=True, slice_key='sliced_prints'):
    added = 0
    for prepared in batches:
        left, right = _bounds(prepared, start_ns, end_ns)
        if left == right:
            continue
        window.add_prepared(prepared, left, right)
        counts[slice_key] += right - left
        added += right - left
    if contribution:
        counts['full_path_print_contributions'] += added
    return added


def _window(definition, instrument_id, start_ns, end_ns, delay):
    return CohortWindow(definition=definition, instrument_id=instrument_id, start_ns=start_ns,
                        end_ns=end_ns, latency_ns=delay, maximum_prints=MAX_PRINTS)


def _included(channels):
    matches = [channel for channel in channels if channel['role'] == 'included']
    if len(matches) != 1:
        raise IntegrityError('source-filter comparison needs exactly one included channel')
    return matches[0]


def _compare_common(channel, flow, *, prints_key):
    checked = 0
    for name in _COMMON:
        if channel[name] != flow[name]:
            raise IntegrityError(f'cohort {channel["channel_id"]} {name} differs from the original measured flow')
        checked += 1
    if channel[prints_key] != flow['prints']:
        raise IntegrityError(f'cohort {channel["channel_id"]} prints differ from the original measured flow')
    checked += 1
    if channel['history_complete'] != flow['coverage_complete']:
        raise IntegrityError('cohort history flag differs from the original measured flow coverage')
    checked += 1
    return checked


def _compare_source_record(record, original, name):
    flows = original['flows']
    if name == 'all':
        channel = record['channels'][0]
        checked = _compare_common(channel, flows['all'], prints_key='weighted_prints')
        if record['prints'] != original['prints'] or record['volume'] != flows['all']['volume']:
            raise IntegrityError('all-flow cohort population differs from the original measured window')
        return checked + 2, 1
    channel = _included(record['channels'])
    checked = _compare_common(channel, flows[name], prints_key='weighted_prints')
    excluded_volume = sum((item['volume'] for item in record['channels'] if item['role'] != 'included'), Fraction(0))
    excluded_prints = sum((item['weighted_prints'] for item in record['channels'] if item['role'] != 'included'),
                          Fraction(0))
    if channel['volume'] + excluded_volume != flows['all']['volume']:
        raise IntegrityError('excluded source channels do not reconcile to all-flow volume')
    if channel['weighted_prints'] + excluded_prints != original['prints']:
        raise IntegrityError('excluded source channels do not reconcile to all-flow prints')
    if record['prints'] != original['prints'] or record['volume'] != flows['all']['volume']:
        raise IntegrityError('source-filter window population differs from the original all-flow population')
    return checked + 4, len(record['channels'])


def _compose_atoms(atom_records):
    if not atom_records:
        return None
    composed = []
    total_prints = sum(atom['prints'] for atom in atom_records)
    total_volume = sum(atom['volume'] for atom in atom_records)
    n = len(atom_records[0]['channels'])
    for index in range(n):
        opening = atom_records[0]['openings'][index]
        close = exact_number(opening)
        high = low = close
        high_at = low_at = None
        high_order = low_order = None
        buy = sell = unknown = weighted = Fraction(0)
        contributing = 0
        for atom in atom_records:
            channel = atom['channels'][index]
            offset = close - channel['open']
            translated_high = channel['high'] + offset
            translated_low = channel['low'] + offset
            translated_close = channel['close'] + offset
            if translated_high > high:
                high = translated_high
                high_at = channel['high_at_ns']
                high_order = channel['high_source_order']
            if translated_low < low:
                low = translated_low
                low_at = channel['low_at_ns']
                low_order = channel['low_source_order']
            buy += channel['buy']
            sell += channel['sell']
            unknown += channel['unknown']
            weighted += channel['weighted_prints']
            contributing += channel['contributing_prints']
            close = translated_close
        composed.append({
            'channel_id': atom_records[0]['channels'][index]['channel_id'],
            'open': exact_number(opening), 'high': high, 'low': low, 'close': close,
            'high_at_ns': high_at, 'low_at_ns': low_at,
            'high_source_order': high_order, 'low_source_order': low_order,
            'buy': buy, 'sell': sell, 'unknown': unknown, 'volume': buy + sell + unknown,
            'weighted_prints': weighted, 'contributing_prints': contributing,
            'observed_signed_lower': (buy - sell) - unknown,
            'observed_signed_upper': (buy - sell) + unknown,
        })
    return {'channels': composed, 'prints': total_prints, 'volume': total_volume}


def _compare_composed(whole, composed):
    if composed is None:
        raise IntegrityError('atom composition produced no path for a supported whole interval')
    if whole['prints'] != composed['prints'] or whole['volume'] != composed['volume']:
        raise IntegrityError('composed atom populations differ from the whole cohort window')
    if len(whole['channels']) != len(composed['channels']):
        raise IntegrityError('composed atom channels differ from the whole cohort window')
    for channel, item in zip(whole['channels'], composed['channels'], strict=True):
        for name in ('channel_id', 'open', 'high', 'low', 'close', 'high_at_ns', 'low_at_ns',
                     'high_source_order', 'low_source_order', 'buy', 'sell', 'unknown', 'volume',
                     'weighted_prints', 'contributing_prints', 'observed_signed_lower',
                     'observed_signed_upper'):
            if channel[name] != item[name]:
                raise IntegrityError(f'composed atom {name} differs from the whole cohort window')
    partition = sum((channel['volume'] for channel in composed['channels']), Fraction(0))
    unknown = sum((channel['unknown'] for channel in composed['channels']), Fraction(0))
    if whole['partition'] and partition != whole['volume']:
        raise IntegrityError('composed atom partition mass differs from the whole cohort window')
    if unknown != sum((channel['unknown'] for channel in whole['channels']), Fraction(0)):
        raise IntegrityError('composed atom unknown mass differs from the whole cohort window')


def _pack_channels(channels):
    return [[channel[name] for name in _CHANNEL_FIELDS] for channel in channels]


def _pack_bar(meta, record):
    return [meta[name] if name in meta else record[name] for name in _BAR_FIELDS]


def _definition_identity(item):
    definition = item['definition']
    if definition is None:
        return {'name': item['name'], 'kind': item['kind'], 'unavailable': item['unavailable'],
                'publication_status': 'unpublished', 'output_kind': _UNPUBLISHED}
    return {
        'name': item['name'], 'kind': item['kind'], 'definition_id': definition.id,
        'definition_version': definition.version, 'definition_origin': definition.origin,
        'definition_available_at': definition.available_at, 'fit_recipe_id': definition.fit_recipe_id,
        'aggregation_unit': definition.aggregation_unit, 'partition': definition.partition,
        'channels': tuple((c.id, c.lower_inclusive, c.upper_exclusive, c.role) for c in definition.channels),
        'knots': definition.knots, 'start_ns': item['start_ns'], 'end_ns': item['end_ns'],
        'unavailable': item['unavailable'], 'publication_status': 'unpublished',
        'output_kind': _UNPUBLISHED, 'admitted_for_serving': False,
    }


def _collect_scalar_probe(batches, start_ns, end_ns):
    rows = []
    for prepared in batches:
        left, right = _bounds(prepared, start_ns, end_ns)
        for index in range(left, right):
            rows.append(_row_tuple(prepared, index))
            if len(rows) == PREFIX_PROBE:
                return rows, False
    return rows, True


def _scalar_reference_record(selected, *, start_ns, truncated, entire, disposition=None):
    if not selected:
        return {
            'selected_count': 0, 'event_start_ns': start_ns, 'event_end_ns': None,
            'first': None, 'last': None, 'prefix_digest': _prefix_digest(()),
            'truncated_final_timestamp_group': truncated,
            'entire_supported_interval_at_or_under_prefix_limit': entire,
            'disposition': disposition or _EMPTY_SCALAR,
        }
    return {
        'selected_count': len(selected), 'event_start_ns': start_ns,
        'event_end_ns': selected[-1]['t'] + 1,
        'first': _address(selected[0]), 'last': _address(selected[-1]),
        'prefix_digest': _prefix_digest(selected),
        'truncated_final_timestamp_group': truncated,
        'entire_supported_interval_at_or_under_prefix_limit': entire,
        'disposition': disposition,
    }


def _as_trades(rows, *, aggregation_unit, history_complete):
    trades = []
    for row in rows:
        price = Ticks(row['price']) if row['price_valid'] else None
        trades.append(Trade(
            id=f"{row['source_key']}:{row['source_row']}:{row['source_order']}",
            source_content_version=row['source_key'], instrument=str(row['instrument_id']),
            event_at=row['t'], known_at=row['known_at_ns'], price=price, size=row['size'],
            side=None if row['side'] == 0 else row['side'], order=row['source_order'],
            aggregation_unit=aggregation_unit, history_complete=history_complete))
    return tuple(trades)


def _literal_orders(trades, weights, opening):
    value = exact_number(opening)
    high = low = value
    high_order = low_order = None
    for trade, weight in zip(trades, weights, strict=True):
        if not weight:
            continue
        value += trade.signed * weight
        if value > high:
            high = value
            high_order = trade.order
        if value < low:
            low = value
            low_order = trade.order
    return high_order, low_order


def _compare_scalar(record, trades, definition, counts):
    n = len(definition.channels) or len(definition.knots)
    openings = record['openings']
    weight_rows = tuple(definition.weights(trade.size) for trade in trades)
    ids = [channel.id for channel in definition.channels] if definition.channels else [
        f'knot:{knot}' for knot in definition.knots]
    complete = record['source_coverage_complete']
    for index, channel in enumerate(record['channels']):
        weights = tuple(row[index] for row in weight_rows)
        path = _cohort_path(trades, weights, openings[index], ids[index], complete)
        if (path.close != channel['close'] or path.high_bounds != channel['high_bounds']
                or path.low_bounds != channel['low_bounds'] or path.high_at != channel['high_at_ns']
                or path.low_at != channel['low_at_ns'] or path.buy != channel['buy']
                or path.sell != channel['sell'] or path.unknown != channel['unknown']
                or path.weighted_prints != channel['weighted_prints']
                or path.contributing_prints != channel['contributing_prints']
                or path.open != channel['open']):
            raise IntegrityError('bounded scalar cohort path differs from the unpublished window')
        high_order, low_order = _literal_orders(trades, weights, openings[index])
        if high_order != channel['high_source_order'] or low_order != channel['low_source_order']:
            raise IntegrityError('literal first-attainment source order differs from the unpublished window')
        counts['scalar_reference_channels'] += 1
    counts['scalar_reference_prints'] += len(trades)


def _atom_support(atom, start_ns, end_ns):
    original_start, original_end = atom['event_start_ns'], atom['event_end_ns']
    if original_end <= start_ns or original_start >= end_ns:
        return None
    supported_start = max(original_start, start_ns)
    supported_end = min(original_end, end_ns)
    if supported_start >= supported_end:
        return None
    return {
        'bin': atom['bin'], 'event_start_ns': original_start, 'event_end_ns': original_end,
        'known_at_ns': atom['known_at_ns'], 'supported_start_ns': supported_start,
        'supported_end_ns': supported_end, 'clipped': supported_start != original_start,
        'source_coverage_complete': atom['trade']['source_coverage_complete'],
        'coordinate_complete': atom['trade']['coordinate_complete'],
        'original': atom,
    }


def _publish_path(record):
    return {
        'event_start_ns': record['event_start_ns'], 'event_end_ns': record['event_end_ns'],
        'known_at_ns': record['known_at_ns'], 'source_delay_ns': record['source_delay_ns'],
        'definition_id': record['definition_id'], 'definition_origin': record['definition_origin'],
        'definition_available_at': record['definition_available_at'],
        'fit_recipe_id': record['fit_recipe_id'], 'publication_status': record['publication_status'],
        'source_coverage_complete': record['source_coverage_complete'],
        'coordinate_complete': record['coordinate_complete'],
        'flow_history_complete': record['flow_history_complete'],
        'prints': record['prints'], 'volume': record['volume'],
        'partition_volume': record['partition_volume'],
        'partition_weighted_prints': record['partition_weighted_prints'],
        'empty_observed_window': record['empty_observed_window'],
        'source_key': record['source_key'],
        'first_print': record['first_print'], 'last_print': record['last_print'],
        'openings': record['openings'],
        'channels': record['channels'],
        'output_kind': record['output_kind'],
        'admitted_for_serving': record['admitted_for_serving'],
    }


def check_cohort_unit(measured, unit, *, measurement_reference, trade_storage, outputs, contract):
    """Whole-window and one-minute unpublished cohort paths for one retained unit."""
    cpu, counts = _cpu(), _counts()
    byte_start = outputs.written
    entry = started = time.process_time()
    _validate_contract(contract)
    if type(measured) is not dict or type(unit) is not dict:
        raise IntegrityError('current measured window does not join the retained unit identity')
    start_ns = _exact_int(measured.get('event_start_ns'), name='current event_start_ns')
    end_ns = _exact_int(measured.get('event_end_ns'), name='current event_end_ns')
    cut_ns = _exact_int(measured.get('known_at_ns'), name='current known_at_ns')
    if start_ns != unit.get('event_start_ns') or end_ns != unit.get('event_end_ns'):
        raise IntegrityError('current measured window does not join the retained unit identity')
    delay = cut_ns - end_ns
    if type(delay) is not int or not 0 <= delay <= 1_000_000_000:
        raise IntegrityError('current unit lost its retained source delay')
    instruments = measured.get('instruments')
    if type(instruments) is not list:
        raise IntegrityError('current measurement lost its raw-instrument population')
    if any(type(item.get('instrument_id')) is not int for item in instruments):
        raise IntegrityError('current measurement lost an exact raw instrument identity')
    raw_ids = tuple(item['instrument_id'] for item in instruments)
    if len(set(raw_ids)) != len(raw_ids):
        raise IntegrityError('duplicate current instrument IDs')
    training = _load_training(contract, unit)
    selected, eligible, training_key, entire, truncated = _collect_training_prefix(training, counts)
    member = _training_member(training, selected, contract, truncated=truncated)
    started = _acc(cpu, 'training_cache_validation_and_selection', started)
    fits, train_unavailable = _fit_training(selected, member, contract, counts)
    started = _acc(cpu, 'histogram_accumulation_fit_and_reference_arithmetic', started)
    plan = _definition_plan(fits, train_unavailable, start_ns, end_ns)
    started = _acc(cpu, 'orchestration_and_report_assembly', started)
    grouped, source_keys = _decode_current(trade_storage, raw_ids, delay, start_ns, end_ns, counts)
    started = _acc(cpu, 'current_cache_decoding', started)
    prepared = {}
    reports = []
    compared_fields = compared_channels = 0
    try:
        prepared = _prepare_groups(grouped, counts)
        started = _acc(cpu, 'preparation_and_filtering', started)
        for instrument in instruments:
            raw_id = int(instrument['instrument_id'])
            batches = prepared[raw_id]
            atoms = instrument.get('atomic_windows')
            if type(atoms) is not list:
                raise IntegrityError('current measurement lost its one-minute atomic windows')
            whole_original = instrument['whole_window']
            instrument_report = {
                'instrument_id': raw_id, 'coordinate': instrument['coordinate'],
                'source_key': source_keys[raw_id],
                'whole_source_coverage_complete': whole_original['source_coverage_complete'],
                'whole_coordinate_complete': whole_original['coordinate_complete'],
                'definitions': [],
            }
            for item in plan:
                identity = _definition_identity(item)
                if item['unavailable'] is not None:
                    early = []
                    for atom in atoms:
                        early.append({
                            'bin': atom['bin'], 'event_start_ns': atom['event_start_ns'],
                            'event_end_ns': atom['event_end_ns'],
                            'disposition': item['unavailable'],
                            'inherited_source_coverage_complete': atom['trade']['source_coverage_complete'],
                            'inherited_coordinate_complete': atom['trade']['coordinate_complete'],
                        })
                    instrument_report['definitions'].append({
                        **identity, 'whole': {'disposition': item['unavailable']},
                        'atomic_unavailable': early,
                        'atomic': {'schema': {'bar': _BAR_FIELDS, 'channel': _CHANNEL_FIELDS},
                                   'bars': [], 'channels': []},
                    })
                    counts['report_bars'] += 1 + len(early)
                    continue
                definition, supported_start, supported_end = item['definition'], item['start_ns'], item['end_ns']
                supported = [_atom_support(atom, supported_start, supported_end) for atom in atoms]
                present = [row for row in supported if row is not None]
                missing = []
                for atom, row in zip(atoms, supported, strict=True):
                    if row is None and atom['event_end_ns'] <= supported_start:
                        missing.append({
                            'bin': atom['bin'], 'event_start_ns': atom['event_start_ns'],
                            'event_end_ns': atom['event_end_ns'], 'disposition': _BEFORE_AVAIL,
                            'inherited_source_coverage_complete': atom['trade']['source_coverage_complete'],
                            'inherited_coordinate_complete': atom['trade']['coordinate_complete'],
                        })
                    elif row is None:
                        raise IntegrityError('atomic cadence shifted away from the measured one-minute bounds')
                whole_source = whole_original['source_coverage_complete'] if item['kind'] != 'adaptive' else (
                    all(row['source_coverage_complete'] for row in present) if present else False)
                whole_coord = whole_original['coordinate_complete'] if item['kind'] != 'adaptive' else (
                    all(row['coordinate_complete'] for row in present) if present else False)
                whole = _window(definition, raw_id, supported_start, supported_end, delay)
                counts['instantiated_bars'] += 1
                started = _acc(cpu, 'orchestration_and_report_assembly', started)
                _add_slices(whole, batches, supported_start, supported_end, counts)
                started = _acc(cpu, 'whole_path_updates', started)
                atom_windows = []
                for row in present:
                    atom_window = _window(definition, raw_id, row['supported_start_ns'],
                                          row['supported_end_ns'], delay)
                    counts['instantiated_bars'] += 1
                    _add_slices(atom_window, batches, row['supported_start_ns'], row['supported_end_ns'], counts)
                    atom_windows.append((row, atom_window))
                started = _acc(cpu, 'atomic_path_updates', started)
                whole_record = whole.record(source_coverage_complete=whole_source,
                                            coordinate_complete=whole_coord)
                atom_records = []
                packed_bars, packed_channels = [], []
                for row, atom_window in atom_windows:
                    record = atom_window.record(source_coverage_complete=row['source_coverage_complete'],
                                                coordinate_complete=row['coordinate_complete'])
                    atom_records.append(record)
                    meta = {**row, 'prints': record['prints'], 'volume': record['volume'],
                            'empty_observed_window': record['empty_observed_window'],
                            'partition_volume': record['partition_volume'],
                            'partition_weighted_prints': record['partition_weighted_prints']}
                    packed_bars.append(_pack_bar(meta, record))
                    packed_channels.append(_pack_channels(record['channels']))
                    counts['report_channels'] += len(record['channels'])
                started = _acc(cpu, 'whole_atomic_finalization', started)
                if item['compare_original']:
                    fields, channels = _compare_source_record(whole_record, whole_original, item['name'])
                    compared_fields += fields
                    compared_channels += channels
                    for row, record in zip(present, atom_records, strict=True):
                        if row['clipped']:
                            continue
                        fields, channels = _compare_source_record(record, row['original']['trade'], item['name'])
                        compared_fields += fields
                        compared_channels += channels
                started = _acc(cpu, 'original_source_comparisons', started)
                _compare_composed(whole_record, _compose_atoms(atom_records))
                started = _acc(cpu, 'full_atom_composition', started)
                probe, scalar_entire = _collect_scalar_probe(batches, supported_start, supported_end)
                prefix, scalar_truncated = _trim_complete_groups(probe, entire_unit=scalar_entire)
                if not prefix:
                    scalar_meta = _scalar_reference_record(
                        prefix, start_ns=supported_start, truncated=scalar_truncated,
                        entire=scalar_entire,
                        disposition=_EMPTY_SCALAR if scalar_truncated else _EMPTY_SCALAR_INTERVAL)
                else:
                    prefix_end = prefix[-1]['t'] + 1
                    prefix_window = _window(definition, raw_id, supported_start, prefix_end, delay)
                    added = _add_slices(prefix_window, batches, supported_start, prefix_end, counts,
                                        contribution=False, slice_key='scalar_reference_sliced_prints')
                    if added != len(prefix):
                        raise IntegrityError('scalar prefix slice lost or invented prints relative to the trimmed groups')
                    prefix_record = prefix_window.record(
                        source_coverage_complete=whole_source, coordinate_complete=whole_coord)
                    trades = _as_trades(prefix, aggregation_unit=contract['aggregation_unit'],
                                        history_complete=whole_source)
                    _compare_scalar(prefix_record, trades, definition, counts)
                    scalar_meta = _scalar_reference_record(
                        prefix, start_ns=supported_start, truncated=scalar_truncated, entire=scalar_entire)
                started = _acc(cpu, 'bounded_scalar_reference', started)
                counts['report_bars'] += 1 + len(packed_bars) + len(missing)
                counts['report_channels'] += len(whole_record['channels'])
                instrument_report['definitions'].append({
                    **identity, 'whole': _publish_path(whole_record),
                    'atomic': {'schema': {'bar': _BAR_FIELDS, 'channel': _CHANNEL_FIELDS},
                               'bars': packed_bars, 'channels': packed_channels},
                    'atomic_unavailable': missing,
                    'supported_start_ns': supported_start, 'supported_end_ns': supported_end,
                    'atom_count': len(packed_bars), 'channel_count': len(whole_record['channels']),
                    'scalar_reference': scalar_meta,
                    'scalar_reference_prints': scalar_meta['selected_count'],
                })
            reports.append(instrument_report)
    finally:
        _release(prepared)
    result = {
        'version': VERSION, 'kind': CONTRACT_KIND, 'publication_status': 'unpublished',
        'output_kind': _UNPUBLISHED, 'admitted_for_serving': False,
        'f11_serving_admitted': False, 'context_or_location_evaluation': False,
        'family_statistics_complete': False, 'annual_or_model_workload_projection_complete': False,
        'unit': {'root': unit['root'], 'event_start_ns': start_ns, 'event_end_ns': end_ns,
                 'source_variant': unit.get('source_variant'), 'source_path': unit.get('source_path'),
                 'cash_date': unit.get('cash_date')},
        'measurement_reference': measurement_reference,
        'training': {
            'resource_unit': training['declared'],
            'unit': {'root': training['unit']['root'], 'cash_date': TRAINING_DATE,
                     'event_start_ns': training['start_ns'], 'event_end_ns': training['end_ns'],
                     'source_path': training['unit'].get('source_path'),
                     'source_variant': training['unit'].get('source_variant')},
            'instrument_id': training['instrument_id'],
            'source_key': training_key,
            'eligible_prints_seen': eligible,
            'entire_unit_at_or_under_prefix_limit': entire,
            'member': member,
            'unavailable': train_unavailable,
            'fits': None if fits is None else {name: {
                'definition_id': item['definition'].id, 'available_at': item['definition'].available_at,
                'requested_thresholds': item['recipe']['requested_thresholds'],
                'literal_requested_thresholds': item['literal_requested_thresholds'],
                'realized_count': item['realized_count'], 'realized_volume': item['realized_volume'],
                'realized_count_occupancy': item['realized_count_occupancy'],
                'realized_volume_occupancy': item['realized_volume_occupancy'],
                'publication_status': item['publication_status'],
                'histogram_identity': item['histogram_identity'],
            } for name, item in fits.items()},
            'manifest_kind': _BOUNDED_ARITHMETIC,
        },
        'definitions': [_definition_identity(item) for item in plan],
        'channel_schema': _CHANNEL_FIELDS, 'bar_schema': _BAR_FIELDS,
        'instruments': reports, 'exact_original_source_fields_compared': compared_fields,
        'exact_original_source_channels_compared': compared_channels,
        'passed': True,
        'scope': 'bounded exact unpublished cohort arithmetic and resource cost; not a full 2020-2022 fit',
    }
    reference = outputs.json_compressed(
        f"{unit['root']}-{start_ns}-{unit['source_variant']}-cohort-validation.json.zst",
        result, kind='auction_flow_actual_cohort_validation')
    cpu['serialization'] += reference['cpu_seconds']
    counts['serialized_bytes'] = reference['size_bytes']
    helper_cpu = time.process_time() - entry
    named = sum(cpu[name] for name in _CPU_NAMES if name != 'orchestration_and_report_assembly')
    cpu['orchestration_and_report_assembly'] = helper_cpu - named
    if cpu['orchestration_and_report_assembly'] < 0:
        raise IntegrityError('disjoint cohort helper CPU stages exceed the measured helper total')
    return {
        'reference': reference,
        'cpu_components_disjoint': cpu,
        'helper_cpu_seconds': helper_cpu,
        'serialization_cpu_seconds': reference['cpu_seconds'],
        'output_bytes': outputs.written - byte_start,
        'workload_counts': counts,
        'instruments': len(reports),
        'definitions': 8,
        'exact_original_source_fields_compared': compared_fields,
        'exact_original_source_channels_compared': compared_channels,
        'training_prefix_prints': 0 if member is None else member['selected_count'],
        'passed': True,
    }
