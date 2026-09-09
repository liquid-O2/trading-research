"""Actual whole-window unpublished structure and memory arithmetic probe.

This is a bounded exact-arithmetic and resource probe. It does not admit F05,
F09, F10 or F11 serving, certify venue completeness, fit a Context specialist,
or start a Location-quality study. Original measurements.structure and
measurements.memory remain independent reference producers.
"""
from __future__ import annotations

from fractions import Fraction
import time

from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.bars import CausalBar, WindowCoverage
from trading_research.foundations.units import Ticks
from trading_research.measurements.common import capture_trade_window
from trading_research.measurements.memory import MemoryDefinition, build_memory
from trading_research.measurements.structure import DirectionalChanges, PricePoint, Swing, pivot_reference
from trading_research.measurements.tape import Trade, TradeLedger
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_memory import (
    AuctionFlowMemoryDefinition, AuctionFlowMemoryWindow,
)
from trading_research.research.auction_flow_quotes import REQUIRED as QUOTE_FIELDS
from trading_research.research.auction_flow_storage import read_series_tables
from trading_research.research.auction_flow_structure import (
    DirectionalChangeStream, FinalBarPivotDefinition, FinalBarPivotStream,
    FixedThresholdDefinition,
)
from trading_research.research.auction_flow_windows import TRADE_FIELDS, prepare_trade_batch


VERSION = 'auction-flow-actual-structure-memory-validation-v1'
CONTRACT_KIND = 'auction_flow_actual_structure_memory_validation_contract_v1'
AGGREGATION_UNIT = 'provider-reported-trade-record'
ATOMIC_WIDTH_NS = 60_000_000_000
SOURCE_VARIANTS = (
    'All original acquired source variants and every listed raw instrument remain '
    'separate; no economic deduplication, no selected-only full-source substitute.')
CONTINUOUS_STRUCTURE_HISTORY = (
    'Original observed prefix only, invalid permanently from the first retained '
    'F4/unknown-action/non-snapshot invalid-size source address. Clear alone does '
    'not invalidate flow. No local book restart repairs the prefix. Structurally '
    'unsupported archive/ownership/coordinate windows remain unavailable, with all '
    'trades counted. Final-bar pivots use the separately retained local atomic coverage.')
MEMORY_SCALAR_CLOCK_REFERENCE = (
    'Literal reference uses original retained event/known times and the candidate '
    'declared event-end age. Original build_memory comparator uses the same '
    'event/price/quantity/side/address content in a separately named zero-delay '
    'event-clock arithmetic view, because that original API ages at its information '
    'cut. Raw known-at values remain retained beside the view. It is not an '
    'assertion of observed receipt or zero actual latency.')
MEMORY_SCOPE = (
    'All five declared fixed constructions on each complete retained source window; '
    'all selected member content and every fixed grid cell/overflow retained. This is '
    'a bounded source-cost arithmetic probe, not selected thresholds, rolling '
    'lifetime/visits, annual inference or a venue certificate.')
SWING_THRESHOLD_TICK_PAIRS = ((4, 1), (8, 1), (16, 1), (32, 1), (5, 2))
PIVOT_LENGTHS = ((1, 1), (2, 2))
PIVOT_TIES = ('strict', 'earliest', 'latest', 'ambiguous')
MEMORY_COMMON = {'frozen_at': 0, 'max_age_ns': 86_400_000_000_000}
MEMORY_DEFINITIONS = (
    {'version': 'all_point_time_box', 'decay_clock': 'time', 'decay_kernel': 'box',
     'decay_scale': 86_400_000_000_000, 'minimum_size': 1, 'price_radius_ticks': 0,
     'spatial_kernel': 'point', 'spatial_radius_ticks': 0, 'strict_size': False,
     'time_radius_ns': 0},
    {'version': 'ge100_triangular_time', 'decay_clock': 'time', 'decay_kernel': 'half_life',
     'decay_scale': 1_800_000_000_000, 'minimum_size': 100, 'price_radius_ticks': 2,
     'spatial_kernel': 'triangular', 'spatial_radius_ticks': 2, 'strict_size': False,
     'time_radius_ns': 1_000_000_000},
    {'version': 'ge100_triangular_volume', 'decay_clock': 'volume', 'decay_kernel': 'half_life',
     'decay_scale': 1000, 'minimum_size': 100, 'price_radius_ticks': 2,
     'spatial_kernel': 'triangular', 'spatial_radius_ticks': 2, 'strict_size': False,
     'time_radius_ns': 1_000_000_000},
    {'version': 'ge75_triangular_box', 'decay_clock': 'time', 'decay_kernel': 'box',
     'decay_scale': 300_000_000_000, 'minimum_size': 75, 'price_radius_ticks': 2,
     'spatial_kernel': 'triangular', 'spatial_radius_ticks': 2, 'strict_size': False,
     'time_radius_ns': 1_000_000_000},
    {'version': 'gt100_triangular_time', 'decay_clock': 'time', 'decay_kernel': 'half_life',
     'decay_scale': 1_800_000_000_000, 'minimum_size': 100, 'price_radius_ticks': 2,
     'spatial_kernel': 'triangular', 'spatial_radius_ticks': 2, 'strict_size': True,
     'time_radius_ns': 1_000_000_000},
)
MEMORY_GRIDS = {'ES': (4096, 32767), 'NQ': (16384, 81919)}
STRUCTURE_SCALAR_LIMIT = 4096
STRUCTURE_SCALAR_PROBE = 4097
MEMORY_SCALAR_LIMIT = 256
MEMORY_SCALAR_PROBE = 257
MAX_INPUT_ROWS = 50_000_000
MAX_BATCH_ROWS = 65_536
MAX_PREPARED_BYTES = 1024 ** 3
CHILD_ADDRESS_LIMIT_BYTES = 4 * 1024 ** 3
MAX_SELECTED_PRINTS = 2_000_000
MAX_CLUSTERS = 1_000_000
MAX_RESULT_BYTES = 512 * 1024 * 1024
HALF_LIFE_ABS = 1e-12
HALF_LIFE_REL = 1e-12
_KNOWN_ACTIONS = frozenset(('A', 'M', 'C', 'R', 'T', 'N'))
_FIXTURE_GRID_KEY = '_fixture_local_memory_grid_inclusive_by_root'
_EMPTY_SOURCE_KEY = 'empty-retained-source'
_UNPUBLISHED = 'unpublished mathematical calculations'
_BAR_DEFINITION = 'auction-flow-unpublished-one-minute-arithmetic-v1'
_ZERO_DELAY_VIEW = 'zero_delay_event_clock_arithmetic_view'
_UNAVAILABLE_SCALAR = 'unavailable_empty_scalar_prefix_after_timestamp_group_trim'
_UNAVAILABLE_EMPTY = 'unavailable_empty_scalar_prefix'
_UNAVAILABLE_STRUCTURAL = 'unavailable_structural_source_ownership_or_coordinate'
_ABSENT = 'absent_data'
_NO_EMISSIONS = 'no_emissions'
_TRUE_NEGATIVE = 'true_negative_comparison'
LIMITATIONS = (
    'rolling/lifetime memory remains separate pending work',
    'visit/protection/markout remain separate pending work',
    'volatility-scaled swings remain separate pending work',
    'multiscale tree remains separate pending work',
    'divergence remains separate pending work',
    'FVG/block definitions remain separate pending work',
    'complete annual statistics remain separate pending work',
)
_CPU_NAMES = (
    'current_cache_decoding',
    'quality_selection',
    'preparation',
    'full_swing_work',
    'bar_assembly_and_reference_parity',
    'full_memory_accumulation_and_finalization',
    'bounded_scalar_reference',
    'serialization',
    'release',
    'orchestration_and_report_assembly',
)
_EXCLUDED_REQUIRED = (
    't', 'action', 'size', 'instrument_id', 'flags', 'source_row', 'source_order',
    'exclusion_bits', 'source_key',
)


def _cpu():
    return {name: 0.0 for name in _CPU_NAMES}


def _acc(cpu, name, started):
    cpu[name] += time.process_time() - started
    return time.process_time()


def _counts():
    return {
        'decoded_rows': 0, 'decoded_batches': 0,
        'trade_decoded_rows': 0, 'trade_decoded_batches': 0,
        'quote_decoded_rows': 0, 'quote_decoded_batches': 0,
        'excluded_decoded_rows': 0, 'excluded_decoded_batches': 0,
        'instrument_trade_batches': 0, 'prepared_batches': 0, 'prepared_prints': 0,
        'prepared_array_bytes': 0, 'source_rows': 0,
        'swing_definition_visits': 0, 'emitted_swings': 0, 'emitted_pivots': 0,
        'bars_assembled': 0, 'memory_input_prints': 0, 'memory_selected_prints': 0,
        'memory_reports': 0, 'scalar_structure_prints': 0, 'scalar_memory_prints': 0,
        'serialized_bytes': 0, 'serialized_artifacts': 0,
        'flag4_rows': 0, 'unknown_action_rows': 0, 'clear_rows': 0,
        'invalid_size_non_snapshot_rows': 0, 'snapshot_excluded_rows': 0,
        'exact_pivot_records_compared': 0, 'exact_swing_records_compared': 0,
        'exact_memory_fields_compared': 0,
    }


def _exact_int(value, *, name, minimum=None, maximum=None):
    if type(value) is not int:
        raise IntegrityError(f'{name} must be an actual integer')
    if minimum is not None and value < minimum:
        raise IntegrityError(f'{name} is outside its finite bound')
    if maximum is not None and value > maximum:
        raise IntegrityError(f'{name} is outside its finite bound')
    return value


def _exact_bool(value, *, name):
    if type(value) is not bool:
        raise IntegrityError(f'{name} must be an exact boolean')
    return value


def _pairs(values, expected, *, name):
    if type(values) not in (tuple, list) or len(values) != len(expected):
        raise ContractError(f'structure/memory contract changed its registered {name}')
    out = []
    for item, want in zip(values, expected, strict=True):
        if type(item) not in (tuple, list) or len(item) != len(want):
            raise ContractError(f'structure/memory contract changed its registered {name}')
        if any(type(part) is not int for part in item) or tuple(item) != tuple(want):
            raise ContractError(f'structure/memory contract changed its registered {name}')
        out.append(tuple(item))
    return tuple(out)


def _text_tuple(values, expected, *, name):
    if type(values) not in (tuple, list) or tuple(values) != expected:
        raise ContractError(f'structure/memory contract changed its registered {name}')
    return tuple(values)


def _validate_memory_spec(got, expected):
    if type(got) is not dict:
        raise ContractError('declared memory recipes are not the registered unpublished set')
    for key, want in expected.items():
        value = got.get(key)
        if key in ('strict_size',) and value is not want:
            raise ContractError('declared memory recipes are not the registered unpublished set')
        if key != 'strict_size' and value != want:
            raise ContractError('declared memory recipes are not the registered unpublished set')


def _validate_contract(contract):
    if type(contract) is not dict or contract.get('kind') != CONTRACT_KIND:
        raise ContractError('auction structure/memory validation contract kind is not the registered v1 object')
    if (contract.get('aggregation_unit') != AGGREGATION_UNIT
            or contract.get('atomic_width_ns') != ATOMIC_WIDTH_NS
            or type(contract.get('atomic_width_ns')) is not int
            or contract.get('maximum_memory_scalar_prints') != MEMORY_SCALAR_LIMIT
            or contract.get('maximum_structure_scalar_prints') != STRUCTURE_SCALAR_LIMIT
            or type(contract.get('maximum_memory_scalar_prints')) is not int
            or type(contract.get('maximum_structure_scalar_prints')) is not int
            or contract.get('all_original_source_checks_retained') is not True
            or contract.get('context_or_location_evaluation') is not False
            or contract.get('f09_f10_f11_serving_admitted') is not False
            or contract.get('family_statistics_complete') is not False
            or contract.get('publication_status') != 'unpublished'
            or contract.get('source_variants') != SOURCE_VARIANTS
            or contract.get('continuous_structure_history') != CONTINUOUS_STRUCTURE_HISTORY
            or contract.get('memory_scalar_clock_reference') != MEMORY_SCALAR_CLOCK_REFERENCE
            or contract.get('memory_scope') != MEMORY_SCOPE):
        raise ContractError('structure/memory contract changed its registered limits or family scope')
    common = contract.get('memory_common')
    if (type(common) is not dict or common.get('frozen_at') != MEMORY_COMMON['frozen_at']
            or common.get('max_age_ns') != MEMORY_COMMON['max_age_ns']
            or type(common.get('frozen_at')) is not int
            or type(common.get('max_age_ns')) is not int):
        raise ContractError('structure/memory contract changed its registered memory common clocks')
    _pairs(contract.get('swing_threshold_tick_pairs'), SWING_THRESHOLD_TICK_PAIRS,
           name='swing threshold tick pairs')
    _pairs(contract.get('pivot_lengths'), PIVOT_LENGTHS, name='pivot lengths')
    _text_tuple(contract.get('pivot_ties'), PIVOT_TIES, name='pivot ties')
    recipes = contract.get('memory_definitions')
    if type(recipes) is not list or len(recipes) != len(MEMORY_DEFINITIONS):
        raise ContractError('declared memory recipes are not the registered unpublished set')
    for got, expected in zip(recipes, MEMORY_DEFINITIONS, strict=True):
        _validate_memory_spec(got, expected)
    grids = contract.get('memory_grid_inclusive_by_root')
    if type(grids) is not dict or set(grids) != set(MEMORY_GRIDS):
        raise ContractError('structure/memory contract changed its registered inclusive raw-tick grids')
    for root, bounds in MEMORY_GRIDS.items():
        got = grids.get(root)
        if type(got) not in (tuple, list) or len(got) != 2:
            raise ContractError('structure/memory contract changed its registered inclusive raw-tick grids')
        if type(got[0]) is not int or type(got[1]) is not int or tuple(got) != bounds:
            raise ContractError('structure/memory contract changed its registered inclusive raw-tick grids')
    return contract


def _fixture_local_contract(contract, *, memory_grid_inclusive_by_root):
    """Private fixture-only grid injection. Public frozen contract fields stay exact."""
    _validate_contract(contract)
    if type(memory_grid_inclusive_by_root) is not dict or set(memory_grid_inclusive_by_root) != set(MEMORY_GRIDS):
        raise ContractError('fixture-local grids must be declared separately for NQ and ES')
    injected = {}
    for root, bounds in memory_grid_inclusive_by_root.items():
        if type(bounds) not in (tuple, list) or len(bounds) != 2:
            raise ContractError('fixture-local grids need inclusive exact integer endpoints')
        lo, hi = bounds
        if type(lo) is not int or type(hi) is not int or hi < lo:
            raise ContractError('fixture-local grids need inclusive exact integer endpoints')
        if hi - lo + 1 > 65_536:
            raise ContractError('fixture-local grids cannot exceed the kernel cell capacity')
        injected[root] = (lo, hi)
    payload = dict(contract)
    payload[_FIXTURE_GRID_KEY] = injected
    return payload


def _grid_bounds(contract, root):
    local = contract.get(_FIXTURE_GRID_KEY)
    if type(local) is dict and root in local:
        return tuple(local[root])
    return tuple(contract['memory_grid_inclusive_by_root'][root])


def _inclusive_grid(lo, hi):
    return tuple(range(lo, hi + 1))


def _require_columns(table, names, *, label):
    missing = [name for name in names if name not in table.column_names]
    if missing:
        raise IntegrityError(f'retained {label} series lost a required raw field projection')
    if len(table) > MAX_BATCH_ROWS:
        raise IntegrityError(f'retained {label} series exceeded the source batch row bound')


def _unique_source_key(table):
    import pyarrow.compute as pc

    keys = pc.unique(table['source_key']).to_pylist()
    if len(keys) != 1 or type(keys[0]) is not str or not keys[0]:
        raise IntegrityError('a structure/memory window cannot join distinct acquired source streams')
    return keys[0]


def _filter_instrument(table, instrument_id):
    import pyarrow.compute as pc

    return table.filter(pc.equal(table['instrument_id'], instrument_id))


def _source_address(value, *, name):
    import numpy as np

    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise IntegrityError(f'{name} must be an exact nonnegative source address')
    if isinstance(value, np.unsignedinteger):
        return int(value)
    result = int(value)
    if result < 0:
        raise IntegrityError(f'{name} must be an exact nonnegative source address')
    return result


def _prepared_label(array, index):
    value = array[index]
    return value.as_py() if hasattr(value, 'as_py') else value


def _row_tuple(prepared, index):
    values = prepared.values
    return {
        't': int(values['t'][index]),
        'source_order': _source_address(values['source_order'][index], name='source_order'),
        'source_row': _source_address(values['source_row'][index], name='source_row'),
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
        't', 'source_row', 'source_order', 'source_key', 'raw_flags', 'raw_side', 'raw_action',
        'known_at_ns')}


def _prepared_bytes(prepared):
    total = 0
    for array in prepared.values.values():
        total += int(array.nbytes)
    if prepared.valid is not None:
        total += int(prepared.valid.nbytes)
    for column in (prepared._source_key, prepared._raw_side, prepared._raw_action):
        if column is not None:
            total += int(column.nbytes)
    return total


def _count_decode(counts, table, *, prefix):
    counts[f'{prefix}_decoded_batches'] += 1
    counts[f'{prefix}_decoded_rows'] += len(table)
    counts['decoded_batches'] += 1
    counts['decoded_rows'] += len(table)


def _validate_ordered_clocks(table, *, start_ns, end_ns, delay, last, label):
    import numpy as np

    t = table['t'].to_numpy(zero_copy_only=False)
    order = table['source_order'].to_numpy(zero_copy_only=False)
    rows = table['source_row'].to_numpy(zero_copy_only=False)
    if np.any(t < start_ns) or np.any(t >= end_ns):
        raise IntegrityError(f'{label} print is outside the retained unit window')
    if np.any(order[1:] <= order[:-1]) or np.any(rows[1:] <= rows[:-1]):
        raise IntegrityError(f'{label} series lost original source order')
    if last[0] is not None and (int(t[0]) < last[0] or _source_address(order[0], name='source_order') <= last[1]
                                or _source_address(rows[0], name='source_row') <= last[2]):
        raise IntegrityError(f'{label} series lost original source order')
    if 'known_at_ns' in table.column_names:
        known = table['known_at_ns'].to_numpy(zero_copy_only=False)
        if np.any(known != t + delay):
            raise IntegrityError(f'{label} series delay does not match the retained source delay')
    return (int(t[-1]), _source_address(order[-1], name='source_order'),
            _source_address(rows[-1], name='source_row'))


def _decode_current(storage, instrument_ids, delay, start_ns, end_ns, counts, *, prefix, fields, label):
    grouped = {raw_id: [] for raw_id in instrument_ids}
    keys = {raw_id: None for raw_id in instrument_ids}
    last = {raw_id: (None, None, None) for raw_id in instrument_ids}
    partitioned = 0
    overflow = False
    for table in read_series_tables(storage):
        _count_decode(counts, table, prefix=prefix)
        _require_columns(table, fields, label=label)
        if counts['decoded_rows'] > MAX_INPUT_ROWS:
            overflow = True
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
                raise IntegrityError('a structure/memory window cannot join distinct acquired source streams')
            last[raw_id] = _validate_ordered_clocks(
                kept, start_ns=start_ns, end_ns=end_ns, delay=delay, last=last[raw_id], label=label)
            grouped[raw_id].append(kept)
            if prefix == 'trade':
                counts['instrument_trade_batches'] += 1
        if assigned != len(table):
            raise IntegrityError(f'retained {label} does not belong to a declared current raw instrument')
        partitioned += assigned
    if partitioned != counts[f'{prefix}_decoded_rows']:
        raise IntegrityError(f'retained and partitioned current {label} counts do not reconcile')
    if overflow:
        raise ContractError('structure/memory input-row capacity exhausted')
    return grouped, keys


def _action_text(value):
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode()
    return value if type(value) is str else str(value)


def _earlier(candidate, current):
    if candidate is None:
        return True
    left = (candidate['source_order'], candidate['source_row'])
    right = (current['source_order'], current['source_row'])
    return right < left


def _quality_record(*, source_key, instrument_id, source_order, source_row, event_at,
                    known_at_ns, reason):
    return {
        'source_key': source_key, 'instrument_id': instrument_id,
        'source_order': source_order, 'source_row': source_row,
        'event_at': event_at, 'known_at_ns': known_at_ns, 'reason': reason,
    }


def _scan_quotes(quote_storage, instrument_ids, delay, start_ns, end_ns, counts):
    first = {raw_id: None for raw_id in instrument_ids}
    keys = {raw_id: None for raw_id in instrument_ids}
    last = {raw_id: (None, None, None) for raw_id in instrument_ids}
    flag4 = unknown = clears = 0
    overflow = False
    import pyarrow as pa
    import pyarrow.compute as pc
    import numpy as np

    for table in read_series_tables(quote_storage):
        _count_decode(counts, table, prefix='quote')
        _require_columns(table, QUOTE_FIELDS, label='quote')
        if counts['decoded_rows'] > MAX_INPUT_ROWS:
            overflow = True
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
                raise IntegrityError('a structure/memory window cannot join distinct acquired source streams')
            last[raw_id] = _validate_ordered_clocks(
                kept, start_ns=start_ns, end_ns=end_ns, delay=delay, last=last[raw_id],
                label='quote')
            flags = kept['raw_flags'].to_numpy(zero_copy_only=False)
            actions = pc.cast(kept['raw_action'], pa.string())
            known = pc.fill_null(pc.is_in(actions, value_set=pa.array(list(_KNOWN_ACTIONS))), False)
            known_np = known.to_numpy(zero_copy_only=False)
            flag4_mask = (flags & 4) != 0
            clear_mask = pc.fill_null(pc.equal(actions, 'R'), False).to_numpy(zero_copy_only=False)
            unknown_mask = ~known_np
            flag4 += int(np.count_nonzero(flag4_mask))
            unknown += int(np.count_nonzero(unknown_mask))
            clears += int(np.count_nonzero(clear_mask))
            invalid = flag4_mask | unknown_mask
            if not np.any(invalid):
                continue
            index = int(np.flatnonzero(invalid)[0])
            action = _action_text(kept['raw_action'][index].as_py())
            reasons = []
            if bool(flag4_mask[index]):
                reasons.append('flag4')
            if bool(unknown_mask[index]):
                reasons.append('unknown_action')
            record = _quality_record(
                source_key=key, instrument_id=raw_id,
                source_order=_source_address(kept['source_order'][index].as_py(), name='source_order'),
                source_row=_source_address(kept['source_row'][index].as_py(), name='source_row'),
                event_at=int(kept['t'][index].as_py()),
                known_at_ns=int(kept['known_at_ns'][index].as_py()),
                reason='+'.join(reasons) if reasons else 'unknown_action')
            if _earlier(first[raw_id], record):
                first[raw_id] = record
        if assigned != len(table):
            raise IntegrityError('retained quote does not belong to a declared current raw instrument')
    if overflow:
        raise ContractError('structure/memory input-row capacity exhausted')
    counts['flag4_rows'] += flag4
    counts['unknown_action_rows'] += unknown
    counts['clear_rows'] += clears
    return first, keys, {'flag4_rows': flag4, 'unknown_action_rows': unknown, 'clear_rows': clears}


def _scan_excluded(excluded_storage, instrument_ids, delay, start_ns, end_ns, counts):
    first = {raw_id: None for raw_id in instrument_ids}
    keys = {raw_id: None for raw_id in instrument_ids}
    last = {raw_id: (None, None, None) for raw_id in instrument_ids}
    invalid_n = snapshot_n = 0
    overflow = False
    import numpy as np

    for table in read_series_tables(excluded_storage):
        _count_decode(counts, table, prefix='excluded')
        _require_columns(table, _EXCLUDED_REQUIRED, label='excluded')
        if counts['decoded_rows'] > MAX_INPUT_ROWS:
            overflow = True
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
                raise IntegrityError('a structure/memory window cannot join distinct acquired source streams')
            last[raw_id] = _validate_ordered_clocks(
                kept, start_ns=start_ns, end_ns=end_ns, delay=delay, last=last[raw_id],
                label='excluded')
            bits = kept['exclusion_bits'].to_numpy(zero_copy_only=False)
            snapshot = (bits & 1) != 0
            invalid_size = (bits & 2) != 0
            non_snapshot_invalid = invalid_size & ~snapshot
            invalid_n += int(np.count_nonzero(non_snapshot_invalid))
            snapshot_n += int(np.count_nonzero(snapshot))
            if not np.any(non_snapshot_invalid):
                continue
            index = int(np.flatnonzero(non_snapshot_invalid)[0])
            event_at = int(kept['t'][index].as_py())
            record = _quality_record(
                source_key=key, instrument_id=raw_id,
                source_order=_source_address(kept['source_order'][index].as_py(), name='source_order'),
                source_row=_source_address(kept['source_row'][index].as_py(), name='source_row'),
                event_at=event_at, known_at_ns=event_at + delay,
                reason='invalid_size_non_snapshot')
            if _earlier(first[raw_id], record):
                first[raw_id] = record
        if assigned != len(table):
            raise IntegrityError('retained excluded trade does not belong to a declared current raw instrument')
    if overflow:
        raise ContractError('structure/memory input-row capacity exhausted')
    counts['invalid_size_non_snapshot_rows'] += invalid_n
    counts['snapshot_excluded_rows'] += snapshot_n
    return first, keys, {'invalid_size_non_snapshot_rows': invalid_n, 'snapshot_excluded_rows': snapshot_n}


def _join_manifest(measured, counts, delay, start_ns, end_ns):
    manifest = measured.get('source_manifest')
    if type(manifest) is not dict:
        raise IntegrityError('current measurement lost its retained source_manifest')
    declared_delay = manifest.get('event_latency_scenario_ns')
    if type(declared_delay) is not int or declared_delay != delay:
        raise IntegrityError('source_manifest event_latency_scenario_ns does not equal known_at-end')
    if manifest.get('start_ns') is not None and manifest.get('start_ns') != start_ns:
        raise IntegrityError('source_manifest start does not equal the retained unit window')
    if manifest.get('end_ns') is not None and manifest.get('end_ns') != end_ns:
        raise IntegrityError('source_manifest end does not equal the retained unit window')
    projection = manifest.get('projection')
    if type(projection) is not dict or type(projection.get('counts')) is not dict:
        raise IntegrityError('source_manifest lost its projection counts')
    trade_counts = projection['counts']
    if trade_counts.get('trades') != counts['trade_decoded_rows']:
        raise IntegrityError('retained trade population disagrees with source_manifest projection counts')
    if trade_counts.get('quote_rows') != counts['quote_decoded_rows']:
        raise IntegrityError('retained quote population disagrees with source_manifest projection counts')
    exclusions = manifest.get('trade_exclusions')
    if type(exclusions) is not dict:
        raise IntegrityError('source_manifest lost its trade_exclusions')
    if exclusions.get('unique_excluded_trade_rows', 0) != counts['excluded_decoded_rows']:
        raise IntegrityError('retained excluded population disagrees with source_manifest exclusion counts')
    if exclusions.get('invalid_size_trade_rows') is not None:
        if type(exclusions['invalid_size_trade_rows']) is not int:
            raise IntegrityError('source_manifest invalid_size_trade_rows is not an exact count')
        if exclusions['invalid_size_trade_rows'] < counts['invalid_size_non_snapshot_rows']:
            raise IntegrityError('invalid-size non-snapshot rows exceed the retained exclusion count')
    if exclusions.get('snapshot_trade_rows') is not None:
        if exclusions['snapshot_trade_rows'] != counts['snapshot_excluded_rows']:
            raise IntegrityError('snapshot excluded rows disagree with source_manifest exclusion counts')
    return manifest


def _merge_first_invalid(quote_first, excluded_first, instrument_ids):
    merged = {}
    for raw_id in instrument_ids:
        left, right = quote_first.get(raw_id), excluded_first.get(raw_id)
        if left is None:
            merged[raw_id] = right
        elif right is None or _earlier(right, left):
            merged[raw_id] = left
        else:
            merged[raw_id] = right
    return merged


def _archive_covers(intervals, start_ns, end_ns):
    if type(intervals) not in (tuple, list):
        return None
    return any(type(pair) in (tuple, list) and len(pair) == 2
               and type(pair[0]) is int and type(pair[1]) is int
               and pair[0] <= start_ns and end_ns <= pair[1] for pair in intervals)


def _structural_unavailability(instrument, measured, start_ns, end_ns):
    coordinate = instrument.get('coordinate')
    if type(coordinate) is not dict or coordinate.get('complete') is not True:
        return True, _UNAVAILABLE_STRUCTURAL
    intervals = measured.get('source_archive_intervals')
    covered = _archive_covers(intervals, start_ns, end_ns)
    if intervals is not None and covered is not True:
        return True, _UNAVAILABLE_STRUCTURAL
    atoms = instrument.get('atomic_windows')
    if type(atoms) is list and atoms:
        ownership = []
        for atom in atoms:
            if 'supplied_raw_coordinate_stable' in atom or 'source_instrument_presence' in atom:
                ownership.append(atom.get('supplied_raw_coordinate_stable') is True
                                 and atom.get('source_instrument_presence') is True)
        if ownership and not any(ownership) and instrument.get('whole_window', {}).get('prints', 0) == 0:
            if all(atom.get('coordinate', {}).get('complete') is False for atom in atoms):
                return True, _UNAVAILABLE_STRUCTURAL
    return False, None


def _prepare_groups(grouped, counts):
    prepared = {}
    retained = 0
    try:
        for raw_id, tables in grouped.items():
            items = []
            prepared[raw_id] = items
            for table in tables:
                batch = prepare_trade_batch(table)
                size = _prepared_bytes(batch)
                if retained + size > MAX_PREPARED_BYTES:
                    batch.close()
                    raise ContractError('cumulative retained prepared-array bytes exceed the 1GiB bound')
                if retained + size > CHILD_ADDRESS_LIMIT_BYTES:
                    batch.close()
                    raise ContractError('prepared source arrays exceed the existing 4GiB child address limit')
                items.append(batch)
                retained += size
                counts['prepared_batches'] += 1
                counts['prepared_prints'] += len(batch)
                counts['prepared_array_bytes'] = retained
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


def _order_right(prepared, max_order):
    import numpy as np

    if not len(prepared):
        return 0
    order = prepared.values['source_order']
    return int(np.searchsorted(order, max_order, side='right'))


def _history_slices(prepared, left, right, *, first_invalid, structural):
    if left == right:
        return ()
    if structural:
        return ((left, right, False),)
    if first_invalid is None:
        return ((left, right, True),)
    import numpy as np

    order = prepared.values['source_order'][left:right]
    cut = int(np.searchsorted(order, first_invalid['source_order'], side='left'))
    parts = []
    if cut > 0:
        parts.append((left, left + cut, True))
    if cut < right - left:
        parts.append((left + cut, right, False))
    return tuple(parts)


def _swing_definitions(contract):
    frozen_at = contract['memory_common']['frozen_at']
    items = []
    for numerator, denominator in SWING_THRESHOLD_TICK_PAIRS:
        threshold = Fraction(numerator, denominator)
        version = f'fixed_{numerator}_{denominator}'
        items.append(FixedThresholdDefinition(version, threshold, frozen_at))
    return tuple(items)


def _memory_definition(spec, grid, *, frozen_at, max_age_ns):
    return AuctionFlowMemoryDefinition(
        version=spec['version'], minimum_size=spec['minimum_size'], strict_size=spec['strict_size'],
        price_radius_ticks=spec['price_radius_ticks'], time_radius_ns=spec['time_radius_ns'],
        max_age_ns=max_age_ns, spatial_grid=grid, spatial_kernel=spec['spatial_kernel'],
        spatial_radius_ticks=spec['spatial_radius_ticks'], decay_clock=spec['decay_clock'],
        decay_scale=spec['decay_scale'], decay_kernel=spec['decay_kernel'], frozen_at=frozen_at)


def _pack_swing(item):
    return {
        'unpublished_arithmetic': item.unpublished_arithmetic,
        'side': item.side, 'price_ticks': item.price_ticks,
        'extreme_event_at': item.extreme_event_at, 'extreme_known_at': item.extreme_known_at,
        'extreme_source_order': item.extreme_source_order, 'extreme_source_row': item.extreme_source_row,
        'extreme_source_key': item.extreme_source_key,
        'confirmation_event_at': item.confirmation_event_at,
        'confirmation_known_at': item.confirmation_known_at,
        'confirmation_source_order': item.confirmation_source_order,
        'confirmation_source_row': item.confirmation_source_row,
        'confirmation_source_key': item.confirmation_source_key,
        'origin_event_at': item.origin_event_at, 'origin_known_at': item.origin_known_at,
        'origin_ticks': item.origin_ticks, 'origin_source_order': item.origin_source_order,
        'origin_source_row': item.origin_source_row, 'origin_source_key': item.origin_source_key,
        'origin_kind': item.origin_kind, 'threshold': item.threshold,
        'definition_id': item.definition_id, 'definition_version': item.definition_version,
        'instrument_id': item.instrument_id, 'delay_ns': item.delay_ns, 'status': item.status,
    }


def _pack_pivot(item):
    reference = item.reference_swing()
    return {
        'unpublished_arithmetic': item.unpublished_arithmetic,
        'f09_producer_authenticated': item.f09_producer_authenticated,
        'id': item.id, 'instrument': item.instrument, 'side': item.side,
        'price_ticks': item.price_ticks, 'extreme_start': item.extreme_start,
        'extreme_end': item.extreme_end, 'confirmed_at': item.confirmed_at,
        'source_versions': item.source_versions, 'definition_version': item.definition_version,
        'status': item.status, 'center_start': item.center_start, 'center_end': item.center_end,
        'support_version_ids': item.support_version_ids, 'max_published_at': item.max_published_at,
        'definition_id': item.definition_id, 'left': item.left, 'right': item.right,
        'ties': item.ties, 'interval_ns': item.interval_ns, 'version': item.version,
        'reference_swing': {
            'id': reference.id, 'instrument': reference.instrument, 'side': reference.side,
            'price_ticks': reference.price_ticks, 'extreme_start': reference.extreme_start,
            'extreme_end': reference.extreme_end, 'confirmed_at': reference.confirmed_at,
            'source_versions': reference.source_versions,
            'definition_version': reference.definition_version, 'status': reference.status,
        },
    }


def _swing_point_complete(row, *, history_complete):
    return history_complete and row['price_valid'] == 1 and (row['raw_flags'] & 4) == 0


def _literal_swings(rows, threshold, *, history_at):
    direction = 0
    high = low = origin = None
    output = []
    for row in rows:
        complete = _swing_point_complete(row, history_complete=history_at(row))
        if not complete:
            direction = 0
            high = low = origin = None
            continue
        if high is None:
            high = low = origin = row
            continue
        if row['price'] > high['price']:
            high = row
        if row['price'] < low['price']:
            low = row
        if direction >= 0 and high['price'] - row['price'] >= threshold:
            kind = 'segment_first' if direction == 0 else 'previous_extreme'
            output.append({'side': 'high', 'extreme': high, 'confirmation': row,
                           'origin': origin, 'origin_kind': kind, 'threshold': Fraction(threshold)})
            direction = -1
            origin = high
            high = low = row
        elif direction <= 0 and row['price'] - low['price'] >= threshold:
            kind = 'segment_first' if direction == 0 else 'previous_extreme'
            output.append({'side': 'low', 'extreme': low, 'confirmation': row,
                           'origin': origin, 'origin_kind': kind, 'threshold': Fraction(threshold)})
            direction = 1
            origin = low
            high = low = row
    return tuple(output)


def _compare_literal_swing(candidate, literal):
    if (candidate.side != literal['side'] or candidate.price_ticks != literal['extreme']['price']
            or candidate.extreme_event_at != literal['extreme']['t']
            or candidate.extreme_known_at != literal['extreme']['known_at_ns']
            or candidate.extreme_source_order != literal['extreme']['source_order']
            or candidate.extreme_source_row != literal['extreme']['source_row']
            or candidate.extreme_source_key != literal['extreme']['source_key']
            or candidate.confirmation_event_at != literal['confirmation']['t']
            or candidate.confirmation_known_at != max(literal['extreme']['known_at_ns'],
                                                      literal['confirmation']['known_at_ns'])
            or candidate.confirmation_source_order != literal['confirmation']['source_order']
            or candidate.confirmation_source_row != literal['confirmation']['source_row']
            or candidate.confirmation_source_key != literal['confirmation']['source_key']
            or candidate.origin_event_at != literal['origin']['t']
            or candidate.origin_known_at != literal['origin']['known_at_ns']
            or candidate.origin_ticks != literal['origin']['price']
            or candidate.origin_source_order != literal['origin']['source_order']
            or candidate.origin_source_row != literal['origin']['source_row']
            or candidate.origin_source_key != literal['origin']['source_key']
            or candidate.origin_kind != literal['origin_kind']
            or candidate.threshold != literal['threshold']
            or candidate.status != 'confirmed'):
        raise IntegrityError('candidate swing differs from the independent literal recurrence')


def _compare_original_swing(candidate, original, extreme, confirmation):
    if (candidate.side != original.side or candidate.price_ticks != original.price_ticks
            or candidate.extreme_event_at != original.extreme_start
            or candidate.extreme_event_at != original.extreme_end
            or candidate.confirmation_known_at != original.confirmed_at
            or candidate.status != original.status
            or candidate.extreme_source_order != extreme.order
            or candidate.extreme_event_at != extreme.event_at
            or candidate.extreme_known_at != extreme.known_at
            or candidate.confirmation_event_at != confirmation.event_at
            or candidate.confirmation_source_order != confirmation.order):
        raise IntegrityError('candidate integer swing differs from original DirectionalChanges/PricePoint')


def _trim_complete_groups(rows, *, limit, entire_unit):
    if len(rows) <= limit:
        return list(rows), False
    if entire_unit:
        return list(rows[:limit]), False
    if rows[limit - 1]['t'] == rows[limit]['t']:
        stamp = rows[limit - 1]['t']
        return [row for row in rows[:limit] if row['t'] != stamp], True
    return list(rows[:limit]), False


def _collect_prefix(batches, probe_limit):
    rows = []
    for prepared in batches:
        for index in range(len(prepared)):
            rows.append(_row_tuple(prepared, index))
            if len(rows) == probe_limit:
                return rows, False
    return rows, True


def _history_fn(first_invalid, structural):
    def history_at(row):
        if structural:
            return False
        if first_invalid is None:
            return True
        return (row['source_order'], row['source_row']) < (
            first_invalid['source_order'], first_invalid['source_row'])
    return history_at


def _add_stream(stream, batches, *, first_invalid, structural, counts, max_order=None,
                charge=True):
    emitted = []
    for prepared in batches:
        right = len(prepared) if max_order is None else _order_right(prepared, max_order)
        if right == 0:
            continue
        for left, stop, complete in _history_slices(
                prepared, 0, right, first_invalid=first_invalid, structural=structural):
            if left == stop:
                continue
            produced = stream.add_prepared(prepared, left, stop, history_complete=complete)
            emitted.extend(produced)
            if charge:
                counts['source_rows'] += stop - left
                counts['emitted_swings'] += len(produced)
    work = stream.work()
    if charge:
        counts['swing_definition_visits'] += int(work.get('definition_visits_attempted', 0))
    return tuple(emitted)


def _replay_atom(batches, start_ns, end_ns):
    import numpy as np

    prints = volume = unpriced_volume = unpriced_prints = 0
    open_ticks = close_ticks = high_ticks = low_ticks = None
    unknown_volume = 0
    for prepared in batches:
        left, right = _bounds(prepared, start_ns, end_ns)
        if left == right:
            continue
        values = prepared.values
        size = values['size'][left:right]
        valid = values['price_valid'][left:right]
        price = values['price'][left:right]
        side = values['side'][left:right]
        prints += right - left
        volume += int(np.sum(size, dtype=np.uint64))
        unknown_volume += int(np.sum(size[side == 0], dtype=np.uint64))
        priced = valid == 1
        unpriced = ~priced
        unpriced_prints += int(np.count_nonzero(unpriced))
        unpriced_volume += int(np.sum(size[unpriced], dtype=np.uint64)) if np.any(unpriced) else 0
        if not np.any(priced):
            continue
        ticks = price[priced]
        if open_ticks is None:
            open_ticks = int(ticks[0])
        close_ticks = int(ticks[-1])
        high = int(ticks.max())
        low = int(ticks.min())
        high_ticks = high if high_ticks is None or high > high_ticks else high_ticks
        low_ticks = low if low_ticks is None or low < low_ticks else low_ticks
    return {
        'prints': prints, 'volume': volume, 'unpriced_volume': unpriced_volume,
        'unpriced_prints': unpriced_prints, 'unknown_volume': unknown_volume,
        'open_ticks': open_ticks, 'close_ticks': close_ticks,
        'high_ticks': high_ticks, 'low_ticks': low_ticks,
    }


def _reconcile_atom(geom, atom):
    trade = atom.get('trade')
    if type(trade) is not dict:
        raise IntegrityError('current measurement lost a retained one-minute trade record')
    if geom['prints'] != trade.get('prints'):
        raise IntegrityError('prepared atom print count differs from the retained atom')
    flows = trade.get('flows') or {}
    all_flow = flows.get('all') or {}
    if geom['volume'] != all_flow.get('volume'):
        raise IntegrityError('prepared atom volume differs from the retained atom')
    if geom['unpriced_prints'] != trade.get('unpriced_prints'):
        raise IntegrityError('prepared atom unpriced count differs from the retained atom')
    if geom['high_ticks'] != trade.get('observed_high_ticks') or geom['low_ticks'] != trade.get('observed_low_ticks'):
        raise IntegrityError('prepared atom raw extrema differ from the retained atom')


def _causal_bar(*, instrument, start, end, delay, geom, atom, measurement_reference, raw_id):
    source_complete = _exact_bool(atom['trade']['source_coverage_complete'], name='atom source_coverage_complete')
    coordinate_complete = _exact_bool(atom['trade']['coordinate_complete'], name='atom coordinate_complete')
    width = end - start
    unpriced = geom['unpriced_volume']
    price_complete = source_complete and coordinate_complete and unpriced == 0
    observed = width if price_complete else (width - 1 if width > 1 else 0)
    lineage = digest({
        'measurement': measurement_reference, 'instrument_id': raw_id, 'bin': atom['bin'],
        'event_start_ns': start, 'event_end_ns': end,
    })
    coverage_version = digest({
        'source_coverage_complete': source_complete, 'coordinate_complete': coordinate_complete,
        'unpublished_arithmetic': True, 'f09_producer_authenticated': False,
    })
    return CausalBar(
        instrument, start, end, _BAR_DEFINITION, 0, end, end, True,
        geom['open_ticks'], geom['high_ticks'], geom['low_ticks'], geom['close_ticks'],
        geom['volume'], geom['prints'], unpriced, True, price_complete, observed,
        (f'artifact-atom:{lineage}',), coverage_version, (), end + delay)


def _compare_pivots(emitted, reference):
    got = tuple(item.reference_swing() for item in emitted)
    if len(got) != len(reference):
        raise IntegrityError('final-bar pivot population differs from original pivot_reference')
    checked = 0
    for candidate, original in zip(got, reference, strict=True):
        if type(original) is not Swing:
            raise IntegrityError('original pivot_reference lost a Swing record')
        for name in ('id', 'instrument', 'side', 'price_ticks', 'extreme_start', 'extreme_end',
                     'confirmed_at', 'source_versions', 'definition_version', 'status'):
            if getattr(candidate, name) != getattr(original, name):
                raise IntegrityError(f'final-bar pivot {name} differs from original pivot_reference')
            checked += 1
    return checked


def _ordinary_totals(batches):
    import numpy as np

    prints = volume = unknown = unpriced_prints = unpriced_volume = 0
    ge75 = ge100 = gt100 = 0
    ge75_n = ge100_n = gt100_n = 0
    for prepared in batches:
        if not len(prepared):
            continue
        size = prepared.values['size']
        side = prepared.values['side']
        valid = prepared.values['price_valid']
        prints += len(prepared)
        volume += int(np.sum(size, dtype=np.uint64))
        unknown += int(np.sum(size[side == 0], dtype=np.uint64))
        unpriced = valid == 0
        unpriced_prints += int(np.count_nonzero(unpriced))
        unpriced_volume += int(np.sum(size[unpriced], dtype=np.uint64)) if np.any(unpriced) else 0
        priced = valid == 1
        ge75_n += int(np.count_nonzero(priced & (size >= 75)))
        ge100_n += int(np.count_nonzero(priced & (size >= 100)))
        gt100_n += int(np.count_nonzero(priced & (size > 100)))
        ge75 += int(np.sum(size[priced & (size >= 75)], dtype=np.uint64)) if np.any(priced) else 0
        ge100 += int(np.sum(size[priced & (size >= 100)], dtype=np.uint64)) if np.any(priced) else 0
        gt100 += int(np.sum(size[priced & (size > 100)], dtype=np.uint64)) if np.any(priced) else 0
    return {
        'prints': prints, 'volume': volume, 'unknown_volume': unknown,
        'unpriced_prints': unpriced_prints, 'unpriced_volume': unpriced_volume,
        'ge75_prints': ge75_n, 'ge75_volume': ge75,
        'ge100_prints': ge100_n, 'ge100_volume': ge100,
        'gt100_prints': gt100_n, 'gt100_volume': gt100,
    }


def _compare_profile(report, sparse, grid):
    cells = {price: tuple(raw) for price, raw, _decayed in report['field_cells']}
    overflow = list(report['overflow'][0])
    checked = 0
    for row in sparse.get('rows') or ():
        if type(row) not in (tuple, list) or len(row) != 4:
            raise IntegrityError('retained sparse trade profile lost a priced cell')
        price, buy, sell, unknown = row
        expected = (buy, sell, unknown)
        if price in cells:
            if cells[price] != expected:
                raise IntegrityError('all-point raw field mass differs from the ordinary sparse profile cell')
            checked += 3
        else:
            overflow[0] -= buy
            overflow[1] -= sell
            overflow[2] -= unknown
            checked += 3
    if tuple(overflow) != (0, 0, 0):
        raise IntegrityError('all-point overflow does not reconcile the ordinary sparse profile')
    checked += 3
    return checked


def _reconcile_memory(report, spec, totals, whole, sparse, grid, counts):
    checked = 0
    if report['input_prints'] != totals['prints'] or report['input_volume'] != totals['volume']:
        raise IntegrityError('memory input population differs from retained ordinary source totals')
    checked += 2
    if report['unknown_side_volume'] != totals['unknown_volume']:
        raise IntegrityError('memory unknown volume differs from retained ordinary source totals')
    checked += 1
    if report['unpriced_prints'] != totals['unpriced_prints'] or report['unpriced_volume'] != totals['unpriced_volume']:
        raise IntegrityError('memory unpriced population differs from retained ordinary source totals')
    checked += 2
    if whole.get('prints') != totals['prints']:
        raise IntegrityError('ordinary source print total differs from the retained whole window')
    flows = (whole.get('flows') or {})
    if flows.get('all', {}).get('volume') != totals['volume']:
        raise IntegrityError('ordinary source volume differs from the retained whole window')
    checked += 2
    version = spec['version']
    if version == 'all_point_time_box':
        priced = totals['prints'] - totals['unpriced_prints']
        priced_volume = totals['volume'] - totals['unpriced_volume']
        if report['selected_prints'] != priced or report['selected_volume'] != priced_volume:
            raise IntegrityError('all-point selected mass differs from the ordinary priced source')
        checked += 2
        if sparse is not None:
            checked += _compare_profile(report, sparse, grid)
    elif version in ('ge100_triangular_time', 'ge100_triangular_volume'):
        if report['selected_prints'] != totals['ge100_prints'] or report['selected_volume'] != totals['ge100_volume']:
            raise IntegrityError('>=100 selected mass differs from the matching source cohort')
        ny = flows.get('ny_ge100')
        if ny is not None and type(ny.get('prints')) is int and ny['prints'] < report['selected_prints']:
            raise IntegrityError('>=100 selected prints exceed the retained ny_ge100 cohort')
        checked += 2
    elif version == 'ge75_triangular_box':
        if report['selected_prints'] != totals['ge75_prints'] or report['selected_volume'] != totals['ge75_volume']:
            raise IntegrityError('>=75 selected mass differs from the matching source cohort')
        checked += 2
    elif version == 'gt100_triangular_time':
        if report['selected_prints'] != totals['gt100_prints'] or report['selected_volume'] != totals['gt100_volume']:
            raise IntegrityError('>100 selected mass differs from the distinct strict source comparator')
        if report['selected_prints'] > totals['ge100_prints']:
            raise IntegrityError('>100 selected prints cannot exceed the >=100 cohort')
        checked += 2
    unknown_clusters = sum(1 for cluster in report['clusters'] if cluster['side'] == 0)
    if unknown_clusters and version == 'all_point_time_box' and totals['unknown_volume'] == 0:
        raise IntegrityError('unknown-side clusters were invented without unknown ordinary mass')
    counts['exact_memory_fields_compared'] += checked
    return checked


def _size_ok(size, *, minimum_size, strict_size):
    return size > minimum_size if strict_size else size >= minimum_size


def _spatial_weight(price, support, radius):
    denominator = (radius + 1) ** 2
    return Fraction(radius + 1 - abs(support - price), denominator)


def _decay_weight(age, *, scale, kernel):
    if kernel == 'box':
        return int(age <= scale)
    return 2 ** (-float(Fraction(age, scale)))


def _half_life_error(got, expected):
    if got is None and expected is None:
        return 0.0
    if got is None or expected is None:
        raise IntegrityError('half-life decay channel missingness disagrees')
    error = abs(float(got) - float(expected))
    scale = max(abs(float(expected)), abs(float(got)), 0.0)
    relative = 0.0 if scale == 0.0 else error / scale
    if error > HALF_LIFE_ABS and relative > HALF_LIFE_REL:
        raise IntegrityError('half-life decay differs from the independent literal loop')
    return error


def _compare_decay_channel(got, expected, *, kernel, maximum):
    if kernel == 'box':
        if got != expected:
            raise IntegrityError('box decay differs from the independent literal loop')
        return maximum
    return max(maximum, _half_life_error(got, expected))


def _literal_memory(rows, definition, *, end, history_complete):
    selected = []
    for row in rows:
        if row['price_valid'] != 1:
            continue
        if end - row['t'] > definition.max_age_ns:
            continue
        if not _size_ok(row['size'], minimum_size=definition.minimum_size,
                        strict_size=definition.strict_size):
            continue
        selected.append(row)
    parent = list(range(len(selected)))

    def root(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for i, a in enumerate(selected):
        for j in range(i):
            b = selected[j]
            if (a['side'] == b['side'] and abs(a['t'] - b['t']) <= definition.time_radius_ns
                    and abs(a['price'] - b['price']) <= definition.price_radius_ticks):
                ra, rb = root(i), root(j)
                parent[max(ra, rb)] = min(ra, rb)
    components = {}
    for index, row in enumerate(selected):
        components.setdefault(root(index), []).append(row)
    clusters = []
    for members in components.values():
        quantity = sum(item['size'] for item in members)
        clusters.append({
            'members': tuple(sorted(members, key=lambda item: (
                item['source_key'], item['source_row'], item['source_order']))),
            'side': members[0]['side'],
            'center_ticks': Fraction(sum(item['size'] * item['price'] for item in members), quantity),
            'low_ticks': min(item['price'] for item in members),
            'high_ticks': max(item['price'] for item in members),
            'first_at': min(item['t'] for item in members),
            'last_at': max(item['t'] for item in members),
            'gross': quantity,
            'raw_count': len(members),
        })
    clusters.sort(key=lambda cluster: (cluster['first_at'], cluster['low_ticks']))
    volume_available = definition.decay_clock != 'volume' or history_complete
    group_end = {}
    running = 0
    last_t = None
    pending = []
    for row in rows:
        if last_t is None:
            last_t = row['t']
        if row['t'] != last_t:
            for item in pending:
                group_end[id(item)] = running
            pending = []
            last_t = row['t']
        pending.append(row)
        running += row['size']
    for item in pending:
        group_end[id(item)] = running
    raw = [0, 0, 0]
    decayed = [0, 0, 0]
    cells = {price: [[Fraction(0)] * 3, [0] * 3] for price in definition.spatial_grid}
    overflow = [[Fraction(0)] * 3, [0] * 3]
    radius = 0 if definition.spatial_kernel == 'point' else definition.spatial_radius_ticks
    channel_of = {1: 0, -1: 1, 0: 2}
    for row in selected:
        channel = channel_of[row['side']]
        raw[channel] += row['size']
        if definition.decay_clock == 'time':
            age = end - row['t']
        elif volume_available:
            age = running - group_end[id(row)]
        else:
            age = None
        weight = None if age is None else _decay_weight(
            age, scale=definition.decay_scale, kernel=definition.decay_kernel)
        if weight is None:
            decayed[channel] = None
        elif decayed[channel] is not None:
            decayed[channel] += row['size'] * weight
        for support in range(row['price'] - radius, row['price'] + radius + 1):
            spatial = _spatial_weight(row['price'], support, radius)
            target = cells[support] if support in cells else overflow
            target[0][channel] += row['size'] * spatial
            if weight is None:
                target[1][channel] = None
            elif target[1][channel] is not None:
                target[1][channel] += row['size'] * spatial * weight
    return {
        'clusters': tuple(clusters), 'raw_mass': tuple(raw), 'decayed_mass': tuple(decayed),
        'field_cells': tuple((price, tuple(values[0]), tuple(values[1])) for price, values in cells.items()),
        'overflow': (tuple(overflow[0]), tuple(overflow[1])),
    }


def _cluster_sort_key(cluster):
    if isinstance(cluster, dict):
        return (cluster['first_at'], cluster['low_ticks'], cluster['side'], cluster['gross'],
                cluster['raw_count'])
    return (cluster.first_at, cluster.low_ticks, 0 if cluster.side is None else cluster.side,
            cluster.gross, cluster.raw_count)


def _compare_literal_memory(report, literal, *, kernel):
    if len(report['clusters']) != len(literal['clusters']):
        raise IntegrityError('candidate clusters differ from the independent all-pairs reference')
    maximum = 0.0
    got_clusters = sorted(report['clusters'], key=_cluster_sort_key)
    expected_clusters = sorted(literal['clusters'], key=_cluster_sort_key)
    for got, expected in zip(got_clusters, expected_clusters, strict=True):
        if (got['side'] != expected['side'] or got['center_ticks'] != expected['center_ticks']
                or got['low_ticks'] != expected['low_ticks'] or got['high_ticks'] != expected['high_ticks']
                or got['first_at'] != expected['first_at'] or got['last_at'] != expected['last_at']
                or got['gross'] != expected['gross'] or got['raw_count'] != expected['raw_count']
                or len(got['members']) != len(expected['members'])):
            raise IntegrityError('candidate cluster quantitative fields differ from the independent reference')
        for member, row in zip(got['members'], expected['members'], strict=True):
            if (member['source_key'] != row['source_key'] or member['source_row'] != row['source_row']
                    or member['source_order'] != row['source_order'] or member['event_at'] != row['t']
                    or member['known_at_ns'] != row['known_at_ns'] or member['price'] != row['price']
                    or member['size'] != row['size'] or member['raw_flags'] != row['raw_flags']
                    or member['raw_action'] != row['raw_action'] or member['raw_side'] != row['raw_side']
                    or member['side'] != row['side']):
                raise IntegrityError('candidate cluster member content differs from the independent reference')
    if report['raw_mass'] != literal['raw_mass']:
        raise IntegrityError('candidate raw mass differs from the independent literal loop')
    for got, expected in zip(report['decayed_mass'], literal['decayed_mass'], strict=True):
        maximum = _compare_decay_channel(got, expected, kernel=kernel, maximum=maximum)
    if len(report['field_cells']) != len(literal['field_cells']):
        raise IntegrityError('candidate field cells differ from the independent literal loop')
    for (price, raw, decayed), (exp_price, exp_raw, exp_decayed) in zip(
            report['field_cells'], literal['field_cells'], strict=True):
        if price != exp_price or raw != exp_raw:
            raise IntegrityError('candidate raw field cell differs from the independent literal loop')
        for got, expected in zip(decayed, exp_decayed, strict=True):
            maximum = _compare_decay_channel(got, expected, kernel=kernel, maximum=maximum)
    if report['overflow'][0] != literal['overflow'][0]:
        raise IntegrityError('candidate raw overflow differs from the independent literal loop')
    for got, expected in zip(report['overflow'][1], literal['overflow'][1], strict=True):
        maximum = _compare_decay_channel(got, expected, kernel=kernel, maximum=maximum)
    return maximum


def _as_event_clock_trades(rows, *, instrument, history_at):
    trades = []
    for row in rows:
        price = Ticks(row['price']) if row['price_valid'] else None
        trades.append(Trade(
            id=f"{row['source_key']}:{row['source_row']}:{row['source_order']}",
            source_content_version=row['source_key'], instrument=instrument,
            event_at=row['t'], known_at=row['t'], price=price, size=row['size'],
            side=None if row['side'] == 0 else row['side'], order=row['source_order'],
            aggregation_unit=AGGREGATION_UNIT, history_complete=history_at(row)))
    return tuple(trades)


def _original_memory(rows, spec, grid, *, start, end, instrument, history_at, frozen_at, max_age_ns):
    view = TradeLedger(max_events=max(MEMORY_SCALAR_PROBE, 1))
    for trade in _as_event_clock_trades(rows, instrument=instrument, history_at=history_at):
        view.add(trade)
    coverage = WindowCoverage(instrument, start, end, ((start, end),) if start < end else (),
                              end, _ZERO_DELAY_VIEW)
    capture = capture_trade_window(
        view, instrument=instrument, start=start, end=end, cut=end, published_at=end,
        definition_version=_ZERO_DELAY_VIEW, aggregation_unit=AGGREGATION_UNIT, coverage=coverage,
        max_inputs=MEMORY_SCALAR_PROBE, max_bytes=8_388_608 if len(grid) <= 4096 else 64 * 1024 * 1024)
    original = MemoryDefinition(
        spec['version'], minimum_size=spec['minimum_size'], strict_size=spec['strict_size'],
        price_radius_ticks=spec['price_radius_ticks'], time_radius_ns=spec['time_radius_ns'],
        max_age_ns=max_age_ns, spatial_grid=grid, spatial_kernel=spec['spatial_kernel'],
        spatial_radius_ticks=spec['spatial_radius_ticks'], decay_clock=spec['decay_clock'],
        decay_scale=spec['decay_scale'], decay_kernel=spec['decay_kernel'], frozen_at=frozen_at,
        max_inputs=MEMORY_SCALAR_PROBE, max_clusters=1024, max_cells=max(len(grid), 1),
        max_bytes=8_388_608 if len(grid) <= 4096 else 64 * 1024 * 1024)
    return build_memory((capture,), views=(view,), definition=original, cut=end, published_at=end)


def _compare_original_memory(report, original, rows, *, kernel):
    if len(report['clusters']) != len(original.clusters):
        raise IntegrityError('candidate clusters differ from original build_memory')
    by_id = {f"{row['source_key']}:{row['source_row']}:{row['source_order']}": row for row in rows}
    maximum = 0.0
    got_clusters = sorted(report['clusters'], key=_cluster_sort_key)
    expected_clusters = sorted(original.clusters, key=_cluster_sort_key)
    for got, expected in zip(got_clusters, expected_clusters, strict=True):
        if (got['center_ticks'] != expected.center_ticks or got['low_ticks'] != expected.low_ticks
                or got['high_ticks'] != expected.high_ticks or got['first_at'] != expected.first_at
                or got['last_at'] != expected.last_at or got['gross'] != expected.gross
                or got['raw_count'] != expected.raw_count):
            raise IntegrityError('candidate cluster quantitative fields differ from original build_memory')
        got_side = None if got['side'] == 0 else got['side']
        if got_side != expected.side:
            raise IntegrityError('candidate cluster side differs from original build_memory')
        members = tuple(sorted(
            f"{member['source_key']}:{member['source_row']}:{member['source_order']}"
            for member in got['members']))
        if members != expected.member_ids:
            raise IntegrityError('candidate cluster membership differs from original build_memory')
        for identity in expected.member_ids:
            row = by_id[identity]
            if row['raw_flags'] is None or row['raw_side'] in (None,) or row['raw_action'] in (None,):
                raise IntegrityError('original scalar comparator cannot fabricate zero raw flags, sides or actions')
    if tuple(report['raw_mass']) != tuple(original.raw_mass):
        raise IntegrityError('candidate raw mass differs from original build_memory')
    for got, expected in zip(report['decayed_mass'], original.decayed_mass, strict=True):
        maximum = _compare_decay_channel(got, expected, kernel=kernel, maximum=maximum)
    if len(report['field_cells']) != len(original.field_cells):
        raise IntegrityError('candidate field cells differ from original build_memory')
    for (price, raw, decayed), (exp_price, exp_raw, exp_decayed) in zip(
            report['field_cells'], original.field_cells, strict=True):
        if price != exp_price or raw != exp_raw:
            raise IntegrityError('candidate raw field cell differs from original build_memory')
        for got, expected in zip(decayed, exp_decayed, strict=True):
            maximum = _compare_decay_channel(got, expected, kernel=kernel, maximum=maximum)
    if report['overflow'][0] != original.overflow[0]:
        raise IntegrityError('candidate raw overflow differs from original build_memory')
    for got, expected in zip(report['overflow'][1], original.overflow[1], strict=True):
        maximum = _compare_decay_channel(got, expected, kernel=kernel, maximum=maximum)
    return maximum


def _scalar_structure(prefix, batches, *, start_ns, delay, instrument_id, source_key,
                      definitions, first_invalid, structural, full_emitted, counts):
    if not prefix:
        return {
            'selected_count': 0, 'disposition': _UNAVAILABLE_EMPTY,
            'truncated_final_timestamp_group': False,
            'clock_view_limitation': MEMORY_SCALAR_CLOCK_REFERENCE,
        }
    last_order = prefix[-1]['source_order']
    prefix_end = prefix[-1]['t'] + 1
    history_at = _history_fn(first_invalid, structural)
    stream = DirectionalChangeStream(
        instrument_id=instrument_id, source_key=source_key, start=start_ns, end=prefix_end,
        delay_ns=delay, definitions=definitions)
        emitted = _add_stream(stream, batches, first_invalid=first_invalid, structural=structural,
                          counts=counts, max_order=last_order, charge=False)
    if any(item.confirmation_source_order > last_order for item in emitted):
        raise IntegrityError('scalar swing prefix consumed a later source address')
    full_prefix = tuple(item for item in full_emitted if item.confirmation_source_order <= last_order)
    if tuple(_pack_swing(item) for item in emitted) != tuple(_pack_swing(item) for item in full_prefix):
        raise IntegrityError('a future suffix changed an earlier emitted swing record')
    compared = 0
    for definition in definitions:
        subset = tuple(item for item in emitted if item.definition_id == definition.id)
        threshold = definition.threshold
        literal = _literal_swings(prefix, threshold, history_at=history_at)
        if len(subset) != len(literal):
            raise IntegrityError('candidate prefix swings differ from the independent literal recurrence')
        for candidate, expected in zip(subset, literal, strict=True):
            _compare_literal_swing(candidate, expected)
            compared += 1
        if type(definition.reversal_ticks) is int or (
                type(definition.reversal_ticks) is Fraction and definition.reversal_ticks.denominator == 1):
            engine = DirectionalChanges(
                instrument=str(instrument_id), threshold_ticks=int(definition.threshold),
                definition_version=definition.version)
            original = []
            points = []
            for row in prefix:
                point = PricePoint(
                    f"{row['source_key']}:{row['source_row']}:{row['source_order']}",
                    str(instrument_id), row['t'], row['known_at_ns'], row['price'],
                    row['source_order'], _swing_point_complete(row, history_complete=history_at(row)))
                points.append(point)
                original.extend(engine.add(point))
            if len(subset) != len(original):
                raise IntegrityError('candidate integer swings differ from original DirectionalChanges')
            by_id = {point.id: point for point in points}
            for candidate, expected in zip(subset, original, strict=True):
                extreme_id, confirmation_id = expected.source_versions
                _compare_original_swing(candidate, expected, by_id[extreme_id], by_id[confirmation_id])
                compared += 1
    counts['exact_swing_records_compared'] += compared
    counts['scalar_structure_prints'] += len(prefix)
    return {
        'selected_count': len(prefix), 'event_start_ns': start_ns, 'event_end_ns': prefix_end,
        'first': _address(prefix[0]), 'last': _address(prefix[-1]),
        'truncated_final_timestamp_group': False, 'disposition': None,
        'compared_records': compared, 'emitted_rows': len(emitted),
        'clock_view_limitation': MEMORY_SCALAR_CLOCK_REFERENCE,
        'venue_certified': False, 'f09_producer_authenticated': False,
    }


def _scalar_memory(prefix, batches, *, start_ns, delay, instrument_id, source_key, contract,
                   first_invalid, structural, instrument_label, counts, outputs, unit_name):
    if not prefix:
        return {
            'selected_count': 0, 'disposition': _UNAVAILABLE_EMPTY,
            'truncated_final_timestamp_group': False,
            'clock_view_limitation': MEMORY_SCALAR_CLOCK_REFERENCE,
            'zero_delay_event_clock_arithmetic_view': None,
            'f05_admitted': False, 'f10_admitted': False, 'f11_admitted': False,
        }
    last_order = prefix[-1]['source_order']
    prefix_end = prefix[-1]['t'] + 1
    history_at = _history_fn(first_invalid, structural)
    inherited = all(history_at(row) for row in prefix)
    frozen_at = contract['memory_common']['frozen_at']
    max_age_ns = contract['memory_common']['max_age_ns']
    grid = _inclusive_grid(*_grid_bounds(contract, unit_name))
    comparisons = []
    max_error = 0.0
    for spec in contract['memory_definitions']:
        definition = _memory_definition(spec, grid, frozen_at=frozen_at, max_age_ns=max_age_ns)
        window = AuctionFlowMemoryWindow(
            definition=definition, instrument_id=instrument_id, source_key=source_key,
            start_ns=start_ns, end_ns=prefix_end, latency_ns=delay,
            max_selected_prints=MAX_SELECTED_PRINTS, max_clusters=MAX_CLUSTERS,
            max_result_bytes=MAX_RESULT_BYTES)
        for prepared in batches:
            right = _order_right(prepared, last_order)
            if right == 0:
                continue
            window.add_prepared(prepared, 0, right, history_complete=inherited)
        report = window.finish()
        counts['scalar_memory_prints'] += report['input_prints']
        literal = _literal_memory(prefix, definition, end=prefix_end, history_complete=inherited)
        error = _compare_literal_memory(report, literal, kernel=spec['decay_kernel'])
        max_error = max(max_error, error)
        original = _original_memory(
            prefix, spec, grid, start=start_ns, end=prefix_end, instrument=instrument_label,
            history_at=history_at, frozen_at=frozen_at, max_age_ns=max_age_ns)
        error = _compare_original_memory(report, original, prefix, kernel=spec['decay_kernel'])
        max_error = max(max_error, error)
        for cluster in report['clusters']:
            for member in cluster['members']:
                match = next(row for row in prefix
                             if row['source_order'] == member['source_order']
                             and row['source_row'] == member['source_row'])
                if member['known_at_ns'] != match['known_at_ns']:
                    raise IntegrityError('candidate raw known-at differs from the retained source mapping')
        comparisons.append({
            'version': spec['version'], 'selected_prints': report['selected_prints'],
            'clusters': len(report['clusters']), 'input_prints': report['input_prints'],
        })
    return {
        'selected_count': len(prefix), 'event_start_ns': start_ns, 'event_end_ns': prefix_end,
        'first': _address(prefix[0]), 'last': _address(prefix[-1]),
        'truncated_final_timestamp_group': False, 'disposition': None,
        'definitions': comparisons,
        'maximum_observed_half_life_error': max_error,
        'clock_view_limitation': MEMORY_SCALAR_CLOCK_REFERENCE,
        'zero_delay_event_clock_arithmetic_view': {
            'name': _ZERO_DELAY_VIEW,
            'known_at': 'event_at',
            'cut': 'closed_prefix_event_end',
            'raw_known_at_retained_beside_mapping': True,
            'validates': 'original numerical recurrence, not observed latency or serving admission',
            'f05_admitted': False, 'f10_admitted': False, 'f11_admitted': False,
        },
        'f05_admitted': False, 'f10_admitted': False, 'f11_admitted': False,
        'venue_certified': False,
    }


def _memory_history_complete(instrument, first_invalid, structural):
    whole = instrument['whole_window']
    source_complete = _exact_bool(whole.get('source_coverage_complete'), name='whole source_coverage_complete')
    coordinate_complete = _exact_bool(whole.get('coordinate_complete'), name='whole coordinate_complete')
    if structural:
        return False
    if first_invalid is not None:
        if source_complete is True:
            raise IntegrityError('measurement completeness disagrees with the first invalid source address')
        return False
    return bool(source_complete and coordinate_complete)


def _capacity_failure(exc, window):
    text = str(exc)
    if 'exhausted' not in text:
        raise exc
    return {
        'failed': True, 'error': text,
        'input_prints': window.input_prints, 'input_volume': window.input_volume,
        'selected_prints': window.selected_prints, 'selected_volume': window.selected_volume,
        'unknown_side_prints': window.unknown_side_prints,
        'unpriced_prints': window.unpriced_prints, 'flag4_prints': window.flag4_prints,
        'slices': window._slices,
    }


def _write(outputs, name, value, *, kind, cpu, counts):
    reference = outputs.json_compressed(name, value, kind=kind)
    cpu['serialization'] += reference['cpu_seconds']
    counts['serialized_bytes'] += reference['size_bytes']
    counts['serialized_artifacts'] += 1
    return {
        'path': reference['path'], 'sha256': reference['sha256'],
        'size_bytes': reference['size_bytes'], 'kind': reference['kind'],
        'encoding': reference.get('encoding'),
        'uncompressed_size_bytes': reference.get('uncompressed_size_bytes'),
        'uncompressed_sha256': reference.get('uncompressed_sha256'),
    }


def _source_key_for(trade_keys, quote_keys, raw_id):
    key = trade_keys.get(raw_id) or quote_keys.get(raw_id)
    if type(key) is str and key:
        return key
    return _EMPTY_SOURCE_KEY


def check_structure_memory_unit(measured, unit, *, measurement_reference, trade_storage,
                                quote_storage, excluded_storage, outputs, contract):
    """Whole-window unpublished swings, final-bar pivots and historical memory."""
    cpu, counts = _cpu(), _counts()
    wall_start = time.perf_counter()
    entry = started = time.process_time()
    byte_start = outputs.written
    _validate_contract(contract)
    if type(measured) is not dict or type(unit) is not dict:
        raise IntegrityError('current measured window does not join the retained unit identity')
    root = unit.get('root')
    if root not in MEMORY_GRIDS:
        raise ContractError('current unit root is not a declared structure/memory grid root')
    if measured.get('root') not in (None, root):
        raise IntegrityError('current measured root does not join the retained unit identity')
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
    definitions = _swing_definitions(contract)
    grid = _inclusive_grid(*_grid_bounds(contract, root))
    frozen_at = contract['memory_common']['frozen_at']
    max_age_ns = contract['memory_common']['max_age_ns']
    trade_groups, trade_keys = _decode_current(
        trade_storage, raw_ids, delay, start_ns, end_ns, counts,
        prefix='trade', fields=TRADE_FIELDS, label='trade')
    started = _acc(cpu, 'current_cache_decoding', started)
    quote_first, quote_keys, _quote_counts = _scan_quotes(
        quote_storage, raw_ids, delay, start_ns, end_ns, counts)
    excluded_first, _excluded_keys, _excluded_counts = _scan_excluded(
        excluded_storage, raw_ids, delay, start_ns, end_ns, counts)
    first_invalid = _merge_first_invalid(quote_first, excluded_first, raw_ids)
    manifest = _join_manifest(measured, counts, delay, start_ns, end_ns)
    started = _acc(cpu, 'quality_selection', started)
    prepared = {}
    instrument_reports = []
    swing_payload = []
    pivot_payload = []
    memory_refs = []
    comparison_payload = []
    passed = True
    try:
        prepared = _prepare_groups(trade_groups, counts)
        declared_volume = (manifest.get('projection') or {}).get('counts', {}).get('volume')
        if declared_volume is not None:
            actual_volume = sum(_ordinary_totals(prepared[raw_id])['volume'] for raw_id in raw_ids)
            if actual_volume != declared_volume:
                raise IntegrityError('retained trade volume disagrees with source_manifest projection counts')
        started = _acc(cpu, 'preparation', started)
        for instrument in instruments:
            raw_id = int(instrument['instrument_id'])
            batches = prepared[raw_id]
            source_key = _source_key_for(trade_keys, quote_keys, raw_id)
            first = first_invalid.get(raw_id)
            structural, structural_reason = _structural_unavailability(instrument, measured, start_ns, end_ns)
            atoms = instrument.get('atomic_windows')
            if type(atoms) is not list:
                raise IntegrityError('current measurement lost its one-minute atomic windows')
            whole = instrument.get('whole_window')
            if type(whole) is not dict:
                raise IntegrityError('current measurement lost its whole-window tape')
            coordinate = instrument.get('coordinate')
            if type(coordinate) is not dict:
                raise IntegrityError('current measurement lost its raw coordinate identity')
            bar_instrument = coordinate.get('contract_key') or f'{root}:{raw_id}'
            totals = _ordinary_totals(batches)
            stream = DirectionalChangeStream(
                instrument_id=raw_id, source_key=source_key, start=start_ns, end=end_ns,
                delay_ns=delay, definitions=definitions)
            emitted = _add_stream(
                stream, batches, first_invalid=first, structural=structural, counts=counts)
            snapshot = stream.snapshot()
            started = _acc(cpu, 'full_swing_work', started)
            bars = []
            for atom in atoms:
                a = _exact_int(atom.get('event_start_ns'), name='atom event_start_ns')
                b = _exact_int(atom.get('event_end_ns'), name='atom event_end_ns')
                if b - a != ATOMIC_WIDTH_NS:
                    raise IntegrityError('atomic cadence shifted away from the measured one-minute bounds')
                geom = _replay_atom(batches, a, b)
                _reconcile_atom(geom, atom)
                bars.append(_causal_bar(
                    instrument=bar_instrument, start=a, end=b, delay=delay, geom=geom, atom=atom,
                    measurement_reference=measurement_reference, raw_id=raw_id))
                counts['bars_assembled'] += 1
            pivot_records = []
            pivot_compared = 0
            for left, right in PIVOT_LENGTHS:
                for ties in PIVOT_TIES:
                    definition = FinalBarPivotDefinition(
                        f'pivot_{left}_{right}_{ties}', left, right, ties, frozen_at)
                    engine = FinalBarPivotStream(
                        instrument=bar_instrument, interval_ns=ATOMIC_WIDTH_NS, definition=definition)
                    produced = []
                    for bar in bars:
                        produced.extend(engine.add(bar))
                    reference = pivot_reference(tuple(bars), left=left, right=right, cut=cut_ns, ties=ties)
                    pivot_compared += _compare_pivots(produced, reference)
                    counts['emitted_pivots'] += len(produced)
                    pivot_records.append({
                        'left': left, 'right': right, 'ties': ties,
                        'definition_id': definition.id,
                        'reference_definition_id': definition.reference_definition_id,
                        'record': engine.record(),
                        'emitted': [_pack_pivot(item) for item in produced],
                        'comparison': _TRUE_NEGATIVE if not produced and not reference else (
                            _NO_EMISSIONS if not produced else 'equal'),
                    })
            counts['exact_pivot_records_compared'] += pivot_compared
            started = _acc(cpu, 'bar_assembly_and_reference_parity', started)
            memory_history = _memory_history_complete(instrument, first, structural)
            memory_items = []
            for spec in contract['memory_definitions']:
                definition = _memory_definition(spec, grid, frozen_at=frozen_at, max_age_ns=max_age_ns)
                window = AuctionFlowMemoryWindow(
                    definition=definition, instrument_id=raw_id, source_key=source_key,
                    start_ns=start_ns, end_ns=end_ns, latency_ns=delay,
                    max_selected_prints=MAX_SELECTED_PRINTS, max_clusters=MAX_CLUSTERS,
                    max_result_bytes=MAX_RESULT_BYTES)
                try:
                    for prepared_batch in batches:
                        window.add_prepared(prepared_batch, history_complete=memory_history)
                    report = window.finish()
                except ContractError as exc:
                    failure = _capacity_failure(exc, window)
                    counts['memory_input_prints'] += window.input_prints
                    counts['memory_selected_prints'] += window.selected_prints
                    memory_items.append({
                        'version': spec['version'], 'failed': True, 'failure': failure,
                        'reference': None,
                    })
                    passed = False
                    continue
                counts['memory_input_prints'] += report['input_prints']
                counts['memory_selected_prints'] += report['selected_prints']
                _reconcile_memory(report, spec, totals, whole, whole.get('sparse_profile'), grid, counts)
                ref = _write(
                    outputs,
                    f"{root}-{start_ns}-{unit.get('source_variant')}-i{raw_id}-m-{spec['version']}.json.zst",
                    report, kind='auction_flow_actual_memory_report', cpu=cpu, counts=counts)
                memory_refs.append(ref)
                memory_items.append({
                    'version': spec['version'], 'failed': False, 'reference': ref,
                    'definition_id': report['definition_id'],
                    'input_prints': report['input_prints'], 'selected_prints': report['selected_prints'],
                    'clusters': len(report['clusters']), 'history_complete': report['history_complete'],
                    'empty_observed_window': report['empty_observed_window'],
                    'venue_certified': False,
                })
                counts['memory_reports'] += 1
            started = _acc(cpu, 'full_memory_accumulation_and_finalization', started)
            structure_probe, structure_entire = _collect_prefix(batches, STRUCTURE_SCALAR_PROBE)
            structure_prefix, structure_truncated = _trim_complete_groups(
                structure_probe, limit=STRUCTURE_SCALAR_LIMIT, entire_unit=structure_entire)
            if not structure_prefix and structure_truncated:
                structure_scalar = {
                    'selected_count': 0, 'disposition': _UNAVAILABLE_SCALAR,
                    'truncated_final_timestamp_group': True,
                    'entire_supported_interval_at_or_under_prefix_limit': structure_entire,
                    'clock_view_limitation': MEMORY_SCALAR_CLOCK_REFERENCE,
                }
            elif not structure_prefix:
                structure_scalar = {
                    'selected_count': 0, 'disposition': _UNAVAILABLE_EMPTY if structure_probe else _ABSENT,
                    'truncated_final_timestamp_group': structure_truncated,
                    'entire_supported_interval_at_or_under_prefix_limit': structure_entire,
                    'clock_view_limitation': MEMORY_SCALAR_CLOCK_REFERENCE,
                }
            else:
                structure_scalar = _scalar_structure(
                    structure_prefix, batches, start_ns=start_ns, delay=delay,
                    instrument_id=raw_id, source_key=source_key, definitions=definitions,
                    first_invalid=first, structural=structural, full_emitted=emitted, counts=counts)
                structure_scalar['truncated_final_timestamp_group'] = structure_truncated
                structure_scalar['entire_supported_interval_at_or_under_prefix_limit'] = structure_entire
            memory_probe, memory_entire = _collect_prefix(batches, MEMORY_SCALAR_PROBE)
            memory_prefix, memory_truncated = _trim_complete_groups(
                memory_probe, limit=MEMORY_SCALAR_LIMIT, entire_unit=memory_entire)
            if not memory_prefix and memory_truncated:
                memory_scalar = {
                    'selected_count': 0, 'disposition': _UNAVAILABLE_SCALAR,
                    'truncated_final_timestamp_group': True,
                    'entire_supported_interval_at_or_under_prefix_limit': memory_entire,
                    'clock_view_limitation': MEMORY_SCALAR_CLOCK_REFERENCE,
                    'zero_delay_event_clock_arithmetic_view': {
                        'name': _ZERO_DELAY_VIEW, 'unavailable': True,
                        'f05_admitted': False, 'f10_admitted': False, 'f11_admitted': False,
                    },
                    'f05_admitted': False, 'f10_admitted': False, 'f11_admitted': False,
                }
            elif not memory_prefix:
                memory_scalar = {
                    'selected_count': 0,
                    'disposition': _UNAVAILABLE_EMPTY if memory_probe else _ABSENT,
                    'truncated_final_timestamp_group': memory_truncated,
                    'entire_supported_interval_at_or_under_prefix_limit': memory_entire,
                    'clock_view_limitation': MEMORY_SCALAR_CLOCK_REFERENCE,
                    'zero_delay_event_clock_arithmetic_view': {
                        'name': _ZERO_DELAY_VIEW, 'unavailable': True,
                        'f05_admitted': False, 'f10_admitted': False, 'f11_admitted': False,
                    },
                    'f05_admitted': False, 'f10_admitted': False, 'f11_admitted': False,
                }
            else:
                memory_scalar = _scalar_memory(
                    memory_prefix, batches, start_ns=start_ns, delay=delay,
                    instrument_id=raw_id, source_key=source_key, contract=contract,
                    first_invalid=first, structural=structural, instrument_label=bar_instrument,
                    counts=counts, outputs=outputs, unit_name=root)
                memory_scalar['truncated_final_timestamp_group'] = memory_truncated
                memory_scalar['entire_supported_interval_at_or_under_prefix_limit'] = memory_entire
            started = _acc(cpu, 'bounded_scalar_reference', started)
            swing_item = {
                'instrument_id': raw_id, 'source_key': source_key,
                'continuous_unavailable': structural_reason,
                'first_invalid_source_address': first,
                'record': snapshot,
                'emitted': [_pack_swing(item) for item in emitted],
                'comparison': _ABSENT if totals['prints'] == 0 else (
                    _NO_EMISSIONS if not emitted else 'retained'),
            }
            swing_payload.append(swing_item)
            pivot_payload.append({
                'instrument_id': raw_id, 'instrument': bar_instrument, 'definitions': pivot_records,
            })
            comparison_payload.append({
                'instrument_id': raw_id,
                'ordinary_totals': totals,
                'structure_scalar': structure_scalar,
                'memory_scalar': memory_scalar,
                'pivot_records_compared': pivot_compared,
            })
            instrument_reports.append({
                'instrument_id': raw_id, 'coordinate': coordinate, 'source_key': source_key,
                'whole_source_coverage_complete': whole['source_coverage_complete'],
                'whole_coordinate_complete': whole['coordinate_complete'],
                'continuous_unavailable': structural_reason,
                'first_invalid_source_address': first,
                'ordinary_prints': totals['prints'],
                'emitted_swings': len(emitted),
                'emitted_pivots': sum(len(item['emitted']) for item in pivot_records),
                'bars_assembled': len(bars),
                'memory': memory_items,
                'structure_scalar': structure_scalar,
                'memory_scalar': memory_scalar,
                'venue_certified': False,
                'f09_producer_authenticated': False,
                'f05_admitted': False, 'f10_admitted': False, 'f11_admitted': False,
            })
    finally:
        release_started = time.process_time()
        _release(prepared)
        cpu['release'] += time.process_time() - release_started
    swing_ref = _write(
        outputs, f"{root}-{start_ns}-{unit.get('source_variant')}-swings.json.zst",
        {'version': VERSION, 'publication_status': 'unpublished', 'instruments': swing_payload},
        kind='auction_flow_actual_structure_swings', cpu=cpu, counts=counts)
    pivot_ref = _write(
        outputs, f"{root}-{start_ns}-{unit.get('source_variant')}-pivots.json.zst",
        {'version': VERSION, 'publication_status': 'unpublished', 'instruments': pivot_payload},
        kind='auction_flow_actual_structure_pivots', cpu=cpu, counts=counts)
    comparison_ref = _write(
        outputs, f"{root}-{start_ns}-{unit.get('source_variant')}-structure-memory-comparisons.json.zst",
        {'version': VERSION, 'publication_status': 'unpublished',
         'memory_scalar_clock_reference': MEMORY_SCALAR_CLOCK_REFERENCE,
         'instruments': comparison_payload},
        kind='auction_flow_actual_structure_memory_comparisons', cpu=cpu, counts=counts)
    result = {
        'version': VERSION, 'kind': CONTRACT_KIND, 'publication_status': 'unpublished',
        'output_kind': _UNPUBLISHED, 'admitted_for_serving': False,
        'f09_f10_f11_serving_admitted': False, 'f05_admitted': False, 'f10_admitted': False,
        'f11_admitted': False, 'context_or_location_evaluation': False,
        'family_statistics_complete': False, 'annual_or_model_workload_projection_complete': False,
        'venue_certified': False,
        'unit': {'root': root, 'event_start_ns': start_ns, 'event_end_ns': end_ns,
                 'known_at_ns': cut_ns, 'source_variant': unit.get('source_variant'),
                 'source_path': unit.get('source_path'), 'cash_date': unit.get('cash_date')},
        'measurement_reference': measurement_reference,
        'source_manifest_delay_ns': manifest.get('event_latency_scenario_ns'),
        'aggregation_unit': AGGREGATION_UNIT,
        'swing_definitions': tuple({
            'id': item.id, 'version': item.version, 'threshold': item.threshold,
            'frozen_at': item.frozen_at,
        } for item in definitions),
        'pivot_definitions': tuple({
            'left': left, 'right': right, 'ties': ties,
        } for left, right in PIVOT_LENGTHS for ties in PIVOT_TIES),
        'memory_definitions': tuple(dict(item) for item in contract['memory_definitions']),
        'memory_grid_inclusive': list(_grid_bounds(contract, root)),
        'memory_grid_cell_count': len(grid),
        'artifacts': {
            'swings': swing_ref, 'pivots': pivot_ref, 'comparisons': comparison_ref,
            'memory': memory_refs,
        },
        'instruments': instrument_reports,
        'limitations': LIMITATIONS,
        'continuous_structure_history': CONTINUOUS_STRUCTURE_HISTORY,
        'memory_scalar_clock_reference': MEMORY_SCALAR_CLOCK_REFERENCE,
        'memory_scope': MEMORY_SCOPE,
        'passed': passed,
        'scope': 'bounded exact unpublished structure/memory arithmetic and resource cost; not a full-family statistic',
    }
    summary_ref = _write(
        outputs, f"{root}-{start_ns}-{unit.get('source_variant')}-structure-memory-validation.json.zst",
        result, kind='auction_flow_actual_structure_memory_validation', cpu=cpu, counts=counts)
    helper_cpu = time.process_time() - entry
    named = sum(cpu[name] for name in _CPU_NAMES if name != 'orchestration_and_report_assembly')
    cpu['orchestration_and_report_assembly'] = helper_cpu - named
    if cpu['orchestration_and_report_assembly'] < 0:
        raise IntegrityError('disjoint structure/memory helper CPU stages exceed the measured helper total')
    return {
        'reference': {**summary_ref, 'cpu_seconds': cpu['serialization']},
        'cpu_components_disjoint': cpu,
        'helper_cpu_seconds': helper_cpu,
        'helper_wall_seconds': time.perf_counter() - wall_start,
        'serialization_cpu_seconds': cpu['serialization'],
        'output_bytes': outputs.written - byte_start,
        'workload_counts': counts,
        'instruments': len(instrument_reports),
        'definitions': len(MEMORY_DEFINITIONS),
        'swing_definitions': len(definitions),
        'pivot_definitions': len(PIVOT_LENGTHS) * len(PIVOT_TIES),
        'exact_pivot_records_compared': counts['exact_pivot_records_compared'],
        'exact_swing_records_compared': counts['exact_swing_records_compared'],
        'exact_memory_fields_compared': counts['exact_memory_fields_compared'],
        'passed': passed,
        'annual_or_model_workload_projection_complete': False,
        'family_statistics_complete': False,
        'limitations': LIMITATIONS,
    }
