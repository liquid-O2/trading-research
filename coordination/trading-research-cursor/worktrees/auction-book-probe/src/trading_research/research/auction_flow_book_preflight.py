"""Actual full-source reported-BBO comparison against an unpublished candidate.

This is a bounded validation probe. It does not replace the accepted source
projection, repair observed-flow history, certify venue sequence, or start a
Context or Location study. Provider-flagged records stay distinct from
invalidation episodes and are never counted as missing downloads or lost trades.
"""
from __future__ import annotations

import math
import resource
import time

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.auction_flow_book_recovery import (
    POLICY, ReportedBBOReinitializer, VERSION as CANDIDATE_VERSION,
)
from trading_research.research.auction_flow_quotes import (
    REQUIRED, QuoteWindow, prepare_quote_batch,
)
from trading_research.research.auction_flow_storage import BoundedOutputs, ParquetSeries, read_series_tables


VERSION = 'auction-flow-actual-reported-bbo-validation-v1'
CONTRACT_KIND = 'auction_flow_actual_reported_bbo_validation_contract_v1'
ATOMIC_WIDTH_NS = 60_000_000_000
DAY_NS = 86_400_000_000_000
BATCH_ROWS = 65_536
PREFIX_LIMIT = 4096
MAX_SOURCE_KEY = 4096
MAX_ACTION = 64
_SIZE_LIMIT = 2 ** 32 - 1
_PRICE_LIMIT = 2 ** 53
_KNOWN = ('A', 'M', 'C', 'R', 'T', 'N')
_UPDATES = ('A', 'M', 'C')
_MASK_FIELDS = (
    'source_key', 'instrument_id', 'source_row', 'source_order', 't', 'known_at_ns', 'book_valid',
)
_LOGICAL_TERMINAL = (
    'observed_history_complete', 'blocked', 'terminal_episode_unresolved', 'rows',
    'candidate_valid_rows', 'candidate_invalid_rows', 'changed_book_valid_rows',
    'original_valid_rows', 'provider_flagged_records', 'clear_rows', 'unknown_action_rows',
    'episode_count', 'resolved_episode_count', 'unresolved_episode_count', 'episodes',
    'first_unresolved_invalidation', 'last_source_address', 'source_key', 'prefix_start_ns',
    'cumulative_coverage_complete', 'policy', 'policy_version', 'version',
)
_INTERVAL_ONLY = (
    'event_start_ns', 'event_end_ns', 'known_at_ns', 'empty_observed_window',
    'current_interval_rows', 'coverage_complete',
)
_EQUAL_QUOTE_FIELDS = (
    'quote_or_invalidation_rows', 'snapshot_rows', 'gap_rows', 'clear_rows',
    'equal_time_adjacent_quote_rows', 'action_side_counts',
)
_INTEGER_COMPOSITION = (
    'quote_or_invalidation_rows', 'fresh_quote_updates', 'pressure_transitions',
    'invalid_book_rows', 'snapshot_rows', 'gap_rows', 'clear_rows',
    'equal_time_adjacent_quote_rows', 'ofi_contracts', 'same_price_size_ofi',
    'price_change_ofi', 'observed_trusted_standing_duration_ns',
)
_WEIGHTED_UPDATE_MEANS = (
    'update_mean_imbalance', 'update_mean_microprice_minus_midpoint_ticks',
    'update_mean_spread_ticks', 'update_positive_fraction',
)
_WEIGHTED_DURATION_MEANS = (
    'duration_mean_imbalance', 'duration_mean_spread_ticks', 'duration_positive_fraction',
)
_MINUTE_RETAINED = (
    'quote_or_invalidation_rows', 'fresh_quote_updates', 'pressure_transitions',
    'ofi_contracts', 'same_price_size_ofi', 'price_change_ofi', 'ofi_path',
    'invalid_book_rows', 'snapshot_rows', 'gap_rows', 'clear_rows',
    'observed_trusted_standing_duration_ns', 'update_mean_imbalance',
    'update_mean_spread_ticks', 'update_mean_microprice_minus_midpoint_ticks',
    'sum_depth_normalized_ofi', 'duration_mean_imbalance', 'duration_mean_spread_ticks',
    'update_positive_fraction', 'duration_positive_fraction', 'terminal_projection',
)
_NON_COMPOSABLE = (
    'per_complete_window_second_ofi',
    'per_pressure_transition_ofi',
)
_PRIMARY_SOURCES = (
    'https://databento.com/docs/schemas-and-data-formats/mbp-1',
    'https://databento.com/docs/standards-and-conventions/common-fields-enums-types',
    'https://databento.com/docs/standards-and-conventions/mbo-snapshot',
    'https://databento.com/docs/standards-and-conventions/mbo-snapshot',
    'https://databento.com/blog/data-cleaning',
)
# The contract lists the snapshot URL once; keep the frozen tuple exact below.
_CONTRACT_SOURCES = (
    'https://databento.com/docs/schemas-and-data-formats/mbp-1',
    'https://databento.com/docs/standards-and-conventions/common-fields-enums-types',
    'https://databento.com/docs/standards-and-conventions/mbo-snapshot',
    'https://databento.com/blog/data-cleaning',
)
_CONTRACT_ASSUMPTION = (
    'A clean completed ordinary A/M/C record supplies the provider-reported full '
    'current BBO. It may restart local BBO trust under this candidate; it does not '
    'reconstruct missing trades or certify exchange order. Recovery requires bit4 '
    'clear, snapshot clear, LAST set, 0<bid<=ask<2**53 and sizes0<size<2**32-1.'
)
_CONTRACT_KEYS = frozenset((
    'all_columns_except_book_valid_exact', 'all_original_source_checks_retained',
    'atomic_width_ns', 'candidate_global_source_replacement', 'comparison_tolerances',
    'context_or_location_evaluation', 'family_statistics_complete',
    'full_candidate_and_adjacent_cut_comparison', 'full_source_projection_comparison',
    'kind', 'maximum_episodes_per_instrument', 'maximum_rows_per_instrument',
    'maximum_scalar_prefix_rows', 'only_derived_validity_and_measurements_persisted',
    'policy', 'policy_version', 'primary_sources', 'publication_status',
    'source_assumption', 'source_evidence_checked_at', 'source_history_repaired',
    'unchanged_quote_window_consumer', 'venue_or_exchange_order_certified',
))
CANDIDATE_BOOK_RECOVERY = (
    'reported local BBO reinitialization candidate after a clean completed '
    'ordinary full-BBO record; not a source-certified venue recovery'
)
ORIGINAL_CONSUMER_BOOK_RECOVERY = (
    'no recovery is inferred; original invalidation remains until supported source reconstruction'
)
LIMITATIONS = (
    'unpublished reported-BBO reinitialization candidate; not an accepted global source replacement',
    'provider-flagged records are stored F4 warnings, not missing downloads or a count of lost trades',
    'invalidation episodes are distinct from provider-flagged record counts',
    'local BBO trust recovery does not repair observed-flow history or certify venue sequence',
    'no reconstructed trade history, gross replenishment or participant-intent claim',
    'complete family statistics remain separate pending work',
    'Context fitting remains separate pending work',
    'Location evaluation remains separate pending work',
    'no annual native or model workload projection is claimed',
    'original source projection and quote consumer numeric behavior are unchanged',
)
_CPU_NAMES = (
    'entry_validation',
    'retained_cache_decoding',
    'filtering_and_preparation',
    'candidate_masks',
    'independent_full_masks',
    'adjacent_carry',
    'scalar_reference',
    'whole_atomic_quote_work',
    'finalization_and_comparisons',
    'serialization',
    'release',
    'orchestration_and_report_assembly',
)


def _cpu():
    return {name: 0.0 for name in _CPU_NAMES}


def _acc(cpu, name, started):
    cpu[name] += time.process_time() - started
    return time.process_time()


def _counts():
    return {
        'decoded_rows': 0, 'decoded_batches': 0,
        'instrument_slices': 0, 'instrument_slice_rows': 0,
        'prepared_batches': 0, 'prepared_array_bytes': 0,
        'candidate_rows': 0, 'independent_mask_rows': 0, 'adjacent_rows': 0,
        'full_source_vector_mask_rows_compared': 0, 'bounded_scalar_reference_rows': 0,
        'scalar_reference_visits': 0, 'python_reference_visits': 0,
        'python_episode_transition_visits': 0, 'compared_cells': 0,
        'emitted_mask_rows': 0, 'emitted_mask_bytes': 0,
        'quote_rows_whole': 0, 'quote_rows_atomic': 0,
        'first_recoveries_verified': 0, 'serialized_bytes': 0, 'serialized_artifacts': 0,
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


def _u64(value, *, name):
    import numpy as np

    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise IntegrityError(f'{name} must be an exact nonnegative source address')
    if isinstance(value, np.unsignedinteger):
        return int(value)
    result = int(value)
    if result < 0:
        raise IntegrityError(f'{name} must be an exact nonnegative source address')
    return result


def _text(value, *, limit=MAX_SOURCE_KEY):
    if isinstance(value, bytes):
        if len(value) > limit:
            raise IntegrityError('a reported-BBO window cannot join distinct acquired source streams')
        try:
            value = value.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise IntegrityError('a reported-BBO window cannot join distinct acquired source streams') from exc
    if type(value) is not str or not value or len(value) > limit:
        raise IntegrityError('a reported-BBO window cannot join distinct acquired source streams')
    return value


def _action_text(value):
    if value is None:
        return None
    if isinstance(value, bytes):
        if len(value) > MAX_ACTION:
            raise IntegrityError('quote identity, information cut or retained order disagrees')
        try:
            value = value.decode('utf-8')
        except UnicodeDecodeError as exc:
            raise IntegrityError('quote identity, information cut or retained order disagrees') from exc
    if type(value) is not str or len(value) > MAX_ACTION:
        raise IntegrityError('quote identity, information cut or retained order disagrees')
    return value


def _float_close(left, right, *, absolute, relative):
    if left is None and right is None:
        return True
    if left is None or right is None:
        return False
    return math.isclose(float(left), float(right), rel_tol=relative, abs_tol=absolute)


def _validate_contract(contract):
    if type(contract) is not dict or set(contract) != _CONTRACT_KEYS:
        raise ContractError('auction reported-BBO validation contract is not the registered v1 object')
    if contract.get('kind') != CONTRACT_KIND:
        raise ContractError('auction reported-BBO validation contract kind is not the registered v1 object')
    tolerances = contract.get('comparison_tolerances')
    if (type(tolerances) is not dict
            or tolerances.get('integer_fields') != 'exact'
            or type(tolerances.get('floating_absolute')) is not float
            or type(tolerances.get('floating_relative')) is not float
            or tolerances.get('floating_absolute') != 1e-6
            or tolerances.get('floating_relative') != 1e-12):
        raise ContractError('reported-BBO validation contract changed its registered comparison tolerances')
    sources = contract.get('primary_sources')
    if type(sources) not in (tuple, list) or tuple(sources) != _CONTRACT_SOURCES:
        raise ContractError('reported-BBO validation contract changed its registered primary sources')
    if (contract.get('all_columns_except_book_valid_exact') is not True
            or contract.get('all_original_source_checks_retained') is not True
            or type(contract.get('atomic_width_ns')) is not int
            or contract.get('atomic_width_ns') != ATOMIC_WIDTH_NS
            or contract.get('candidate_global_source_replacement') is not False
            or contract.get('context_or_location_evaluation') is not False
            or contract.get('family_statistics_complete') is not False
            or contract.get('full_candidate_and_adjacent_cut_comparison') is not True
            or contract.get('full_source_projection_comparison') is not True
            or type(contract.get('maximum_episodes_per_instrument')) is not int
            or contract.get('maximum_episodes_per_instrument') != 50_000
            or type(contract.get('maximum_rows_per_instrument')) is not int
            or contract.get('maximum_rows_per_instrument') != 50_000_000
            or type(contract.get('maximum_scalar_prefix_rows')) is not int
            or contract.get('maximum_scalar_prefix_rows') != PREFIX_LIMIT
            or contract.get('only_derived_validity_and_measurements_persisted') is not True
            or contract.get('policy') != POLICY
            or contract.get('policy_version') != CANDIDATE_VERSION
            or contract.get('publication_status') != 'unpublished_validation_candidate'
            or contract.get('source_assumption') != _CONTRACT_ASSUMPTION
            or contract.get('source_evidence_checked_at') != '2026-09-08'
            or contract.get('source_history_repaired') is not False
            or contract.get('unchanged_quote_window_consumer') is not True
            or contract.get('venue_or_exchange_order_certified') is not False):
        raise ContractError('reported-BBO validation contract changed its registered limits or family scope')
    return contract


def _require_quote_columns(table):
    missing = [name for name in REQUIRED if name not in table.column_names]
    if missing:
        raise IntegrityError('retained quote series lost a required raw field projection')
    if len(table) > BATCH_ROWS:
        raise IntegrityError('retained quote series exceeded the source batch row bound')


def _unique_source_key(table):
    import pyarrow.compute as pc

    keys = pc.unique(table['source_key'])
    if keys.null_count or len(keys) != 1:
        raise IntegrityError('a reported-BBO window cannot join distinct acquired source streams')
    return _text(keys[0].as_py())


def _filter_instrument(table, instrument_id):
    import pyarrow.compute as pc

    return table.filter(pc.equal(table['instrument_id'], instrument_id))


def _interior_cut(start_ns, end_ns):
    midnight = (start_ns // DAY_NS + 1) * DAY_NS
    if start_ns < midnight < end_ns:
        return midnight, 'utc_midnight'
    cut = start_ns + (end_ns - start_ns) // 2
    if not start_ns < cut < end_ns:
        raise ContractError('reported-BBO unit lacks an interior adjacent cut')
    return cut, 'interval_midpoint'


def _validate_clocks(table, *, start_ns, end_ns, delay, last, instrument_id):
    import numpy as np

    t = table['t'].to_numpy(zero_copy_only=False)
    order = table['source_order'].to_numpy(zero_copy_only=False)
    rows = table['source_row'].to_numpy(zero_copy_only=False)
    known = table['known_at_ns'].to_numpy(zero_copy_only=False)
    instruments = table['instrument_id'].to_numpy(zero_copy_only=False)
    if np.any(instruments != instrument_id):
        raise IntegrityError('retained quote does not belong to a declared current raw instrument')
    if np.any(t < start_ns) or np.any(t >= end_ns):
        raise IntegrityError('quote identity, information cut or retained order disagrees')
    if np.any(known != t + delay):
        raise IntegrityError('quote series delay does not match the retained source delay')
    if np.any(t[1:] < t[:-1]) or np.any(order[1:] <= order[:-1]) or np.any(rows[1:] <= rows[:-1]):
        raise IntegrityError('quote series lost original source order')
    first_order = _u64(order[0], name='source_order')
    first_row = _u64(rows[0], name='source_row')
    first_t = int(t[0])
    if last[0] is not None and (first_t < last[0] or first_order <= last[1] or first_row <= last[2]):
        raise IntegrityError('quote series lost original source order')
    return (int(t[-1]), _u64(order[-1], name='source_order'), _u64(rows[-1], name='source_row'))


def _split_cut(table, cut_ns):
    import pyarrow.compute as pc

    return (table.filter(pc.less(table['t'], cut_ns)),
            table.filter(pc.greater_equal(table['t'], cut_ns)))


def _prepared_bytes(prepared):
    total = 0
    for array in prepared.values.values():
        if array is not None:
            total += int(array.nbytes)
    for array in (prepared.updates, prepared.clears, prepared.known, prepared.pair_codes):
        if array is not None:
            total += int(array.nbytes)
    return total


def _action_masks(table):
    import numpy as np
    import pyarrow as pa
    import pyarrow.compute as pc

    actions = pc.cast(table['raw_action'].combine_chunks() if hasattr(table['raw_action'], 'combine_chunks')
                      else table['raw_action'], pa.string())
    updates = pc.fill_null(pc.is_in(actions, value_set=pa.array(list(_UPDATES))), False).to_numpy(zero_copy_only=False)
    clears = pc.fill_null(pc.equal(actions, 'R'), False).to_numpy(zero_copy_only=False)
    known = pc.fill_null(pc.is_in(actions, value_set=pa.array(list(_KNOWN))), False).to_numpy(zero_copy_only=False)
    return actions, updates, clears, known, (~known.astype(bool))


def _numeric_column(table, name):
    import numpy as np

    array = table[name]
    if hasattr(array, 'combine_chunks'):
        array = array.combine_chunks()
    values = array.to_numpy(zero_copy_only=False)
    if values.ndim != 1 or values.dtype.kind not in 'iu':
        raise IntegrityError('quote identity, information cut or retained order disagrees')
    return values


def _independent_vector_mask(table, state):
    """Full-source expected book_valid from vector cumulative maxima.

    Does not call ReportedBBOReinitializer private helpers. Same-time order is
    the retained physical/source_order, not a timestamp group.
    """
    import numpy as np

    n = len(table)
    if n == 0:
        return np.zeros(0, dtype=np.uint8), np.zeros(0, dtype=bool)
    flags = _numeric_column(table, 'raw_flags').astype(np.int64, copy=False)
    original = _numeric_column(table, 'book_valid').astype(np.uint8, copy=False)
    bid = _numeric_column(table, 'bid')
    ask = _numeric_column(table, 'ask')
    qb = _numeric_column(table, 'bid_size')
    qa = _numeric_column(table, 'ask_size')
    snapshot = _numeric_column(table, 'snapshot').astype(np.uint8, copy=False)
    _actions, updates, clears, _known, unknown = _action_masks(table)
    bit4 = (flags & np.int64(4)) != 0
    last_bit = (flags & np.int64(128)) != 0
    snap_bit = (flags & np.int64(32)) != 0
    if np.any(snapshot != snap_bit.astype(np.uint8)):
        raise IntegrityError('quote projection flags or validity bits changed')
    invalidation = bit4 | clears.astype(bool) | unknown
    domain = ((bid > 0) & (ask < _PRICE_LIMIT) & (bid <= ask)
              & (qb > 0) & (qa > 0) & (qb < _SIZE_LIMIT) & (qa < _SIZE_LIMIT))
    valid_update = updates.astype(bool) & ~bit4 & domain
    if np.any(original.astype(bool) & ~valid_update):
        raise IntegrityError('trusted projected BBO is outside the exact admitted domain')
    recovery = updates.astype(bool) & ~bit4 & ~snap_bit & last_bit & domain
    pos = np.arange(state['next_pos'], state['next_pos'] + n, dtype=np.int64)
    inv_mark = np.where(invalidation, pos, np.int64(-1))
    rec_mark = np.where(recovery, pos, np.int64(-1))
    last_inv = np.maximum.accumulate(np.concatenate([[np.int64(state['last_inv'])], inv_mark]))[1:]
    last_rec = np.maximum.accumulate(np.concatenate([[np.int64(state['last_rec'])], rec_mark]))[1:]
    before_first = last_inv < 0
    trusted = last_rec > last_inv
    expected = np.where(before_first, original, (trusted & valid_update).astype(np.uint8)).astype(np.uint8)
    before_inv = np.empty(n, dtype=np.int64)
    before_rec = np.empty(n, dtype=np.int64)
    before_inv[0] = state['last_inv']
    before_rec[0] = state['last_rec']
    if n > 1:
        before_inv[1:] = last_inv[:-1]
        before_rec[1:] = last_rec[:-1]
    untrusted_before = (before_inv >= 0) & (before_rec <= before_inv)
    first_recovery = recovery & untrusted_before
    lag_valid = np.empty(n, dtype=np.uint8)
    lag_valid[0] = np.uint8(state['last_candidate_valid'])
    if n > 1:
        lag_valid[1:] = expected[:-1]
    if np.any(first_recovery & (lag_valid != 0)):
        raise IntegrityError('first recovered quote is not preceded by an invalid pressure state')
    if np.any(first_recovery & (original != 0)):
        raise IntegrityError('first recovered quote is not an originally invalid completed ordinary row')
    if np.any(bit4) or np.any(unknown):
        state['history_complete'] = False
    state['last_inv'] = int(last_inv[-1])
    state['last_rec'] = int(last_rec[-1])
    state['next_pos'] += n
    state['last_candidate_valid'] = int(expected[-1])
    state['provider_flagged'] += int(np.count_nonzero(bit4))
    state['clear_rows'] += int(np.count_nonzero(clears))
    state['unknown_rows'] += int(np.count_nonzero(unknown))
    return expected, first_recovery


def _row_address(table, index, *, source_key, delay):
    return {
        'source_key': source_key,
        'source_row': _u64(table['source_row'][index].as_py(), name='source_row'),
        'source_order': _u64(table['source_order'][index].as_py(), name='source_order'),
        't': int(table['t'][index].as_py()),
        'known_at': int(table['known_at_ns'][index].as_py()),
        'raw_flags': int(table['raw_flags'][index].as_py()),
        'raw_action': _action_text(table['raw_action'][index].as_py()),
    }


def _row_bbo(table, index):
    return {
        'bid': int(table['bid'][index].as_py()),
        'ask': int(table['ask'][index].as_py()),
        'bid_size': int(table['bid_size'][index].as_py()),
        'ask_size': int(table['ask_size'][index].as_py()),
        'book_valid': int(table['book_valid'][index].as_py()),
        'raw_flags': int(table['raw_flags'][index].as_py()),
        'raw_action': _action_text(table['raw_action'][index].as_py()),
        'snapshot': int(table['snapshot'][index].as_py()),
    }


def _qualifying_restart_row(row):
    flags = int(row['raw_flags'])
    action = row['raw_action']
    return (action in _UPDATES and not (flags & 4) and not (flags & 32) and bool(flags & 128)
            and 0 < int(row['bid']) <= int(row['ask']) < _PRICE_LIMIT
            and 0 < int(row['bid_size']) < _SIZE_LIMIT and 0 < int(row['ask_size']) < _SIZE_LIMIT)


def _independent_scalar_mask(rows, *, delay):
    """Literal per-row recurrence over retained physical prefix rows."""
    out = []
    episodes = []
    blocked = False
    history_complete = True
    visits = 0
    for row in rows:
        visits += 1
        flags = int(row['raw_flags'])
        action = row['raw_action']
        bit4 = bool(flags & 4)
        snapshot = bool(flags & 32) or bool(row['snapshot'])
        last = bool(flags & 128)
        unknown = action not in _KNOWN
        update = action in _UPDATES
        invalidation = bit4 or action == 'R' or unknown
        domain = (0 < int(row['bid']) <= int(row['ask']) < _PRICE_LIMIT
                  and 0 < int(row['bid_size']) < _SIZE_LIMIT and 0 < int(row['ask_size']) < _SIZE_LIMIT)
        recovery = update and not bit4 and not snapshot and last and domain
        address = {
            'source_key': row['source_key'], 'source_row': int(row['source_row']),
            'source_order': int(row['source_order']), 't': int(row['t']),
            'known_at': int(row['known_at_ns']) if row.get('known_at_ns') is not None else int(row['t']) + delay,
            'raw_flags': flags, 'raw_action': action,
        }
        if blocked:
            if recovery:
                out.append(1)
                episodes[-1] = {**episodes[-1], 'recovery': dict(address), 'unresolved': False}
                blocked = False
            else:
                out.append(0)
                if bit4 or unknown:
                    history_complete = False
                if bit4:
                    episodes[-1]['provider_flagged_records'] += 1
        elif invalidation:
            out.append(0)
            if bit4 or unknown:
                history_complete = False
            episodes.append({
                'episode_index': len(episodes) + 1, 'invalidation': dict(address),
                'recovery': None, 'unresolved': True,
                'provider_flagged_records': 1 if bit4 else 0,
            })
            blocked = True
        elif not episodes:
            out.append(int(row['book_valid']))
        else:
            out.append(1 if update and not bit4 and domain else 0)
    return out, {
        'blocked': blocked, 'observed_history_complete': history_complete, 'episodes': episodes,
        'visits': visits,
    }


def _four_indicator_ofi(previous, current):
    b0, a0 = int(previous['bid']), int(previous['ask'])
    qb0, qa0 = int(previous['bid_size']), int(previous['ask_size'])
    b, a = int(current['bid']), int(current['ask'])
    qb, qa = int(current['bid_size']), int(current['ask_size'])
    return ((b >= b0) * qb - (b <= b0) * qb0 - (a <= a0) * qa + (a >= a0) * qa0,
            ((qb - qb0) if b == b0 else 0) - ((qa - qa0) if a == a0 else 0))


def _independent_quote_scalar(rows, *, instrument_id, start_ns, end_ns, delay, initial=None):
    """Bounded independent QuoteWindow arithmetic. Does not call QuoteWindow or the candidate."""
    if initial is not None:
        if not isinstance(initial, dict):
            raise IntegrityError('unsupported initial measurement-state domain')
        previous = dict(initial)
        initial_projection = dict(initial)
    else:
        previous = None
        initial_projection = None
    events = fresh = pressure = invalid = snapshots = gaps = clears = equal_times = 0
    ofi = same_ofi = price_ofi = 0
    ofi_high = ofi_low = 0
    ofi_high_at = ofi_low_at = None
    ofi_high_order = ofi_low_order = None
    duration = positive_duration = positive_updates = 0
    action_sides = {}
    midpoint = {}
    dn_ofi = []
    imbalance = []
    micro = []
    spreads = []
    dur_imb = []
    dur_spread = []
    increments = []
    visits = 0

    def expose(state, a, b):
        nonlocal duration, positive_duration
        if state is None or not state['book_valid'] or int(state['economic_at']) < 0:
            return
        left = max(int(a), start_ns)
        right = min(int(b), end_ns)
        dt = max(0, right - left)
        if dt <= 0:
            return
        qb, qa = int(state['bid_size']), int(state['ask_size'])
        duration += dt
        if qb > qa:
            positive_duration += dt
        ratio = (qb - qa) / (qb + qa)
        dur_imb.append(dt * ratio)
        dur_spread.append(dt * (int(state['ask']) - int(state['bid'])))
        row = (int(state['bid']) + int(state['ask'])) // 2
        midpoint[row] = midpoint.get(row, 0) + dt

    for index, row in enumerate(rows):
        visits += 1
        if int(row['instrument_id']) != instrument_id:
            raise IntegrityError('quote identity, information cut or retained order disagrees')
        t = int(row['t'])
        order = int(row['source_order'])
        flags = int(row['raw_flags'])
        valid = bool(int(row['book_valid']))
        snapshot = bool(int(row['snapshot'])) or bool(flags & 32)
        action = row['raw_action']
        update = action in _UPDATES
        clear = action == 'R'
        if previous is not None and (t < int(previous['t']) or order <= int(previous['source_order'])):
            raise IntegrityError('quote identity, information cut or retained order disagrees')
        before_valid = bool(previous['book_valid']) if previous is not None else False
        before_economic = int(previous['economic_at']) if previous is not None else -1
        expose(previous, previous['t'] if previous is not None else start_ns, t)
        fresh_row = update and valid and not snapshot and not (flags & 4)
        measured = fresh_row and before_valid
        if measured:
            increment, same = _four_indicator_ofi(previous, row)
            ofi += increment
            same_ofi += same
            price_ofi += increment - same
            if ofi > ofi_high:
                ofi_high, ofi_high_at, ofi_high_order = ofi, t, order
            if ofi < ofi_low:
                ofi_low, ofi_low_at, ofi_low_order = ofi, t, order
            qb0 = int(previous['bid_size']) + int(previous['ask_size'])
            qb, qa = int(row['bid_size']), int(row['ask_size'])
            dn_ofi.append(increment / qb0)
            imb = (qb - qa) / (qb + qa)
            imbalance.append(imb)
            micro.append((int(row['ask']) - int(row['bid'])) * imb / 2)
            spreads.append(int(row['ask']) - int(row['bid']))
            if qb > qa:
                positive_updates += 1
            pressure += 1
            increments.append({'index': index, 'ofi': increment, 'same': same, 't': t, 'source_order': order})
        changed_economic = (update and not snapshot) or clear
        if clear:
            economic_at = -1
        elif changed_economic:
            economic_at = t
        else:
            economic_at = before_economic
        events += 1
        fresh += int(fresh_row)
        invalid += int(not valid)
        snapshots += int(snapshot)
        gaps += int(bool(flags & 4))
        clears += int(clear)
        equal_times += int(previous is not None and t == int(previous['t']))
        key = (action, row['raw_side'])
        action_sides[key] = action_sides.get(key, 0) + 1
        previous = {
            't': t, 'source_order': order, 'instrument_id': instrument_id,
            'bid': int(row['bid']), 'ask': int(row['ask']),
            'bid_size': int(row['bid_size']), 'ask_size': int(row['ask_size']),
            'book_valid': int(valid), 'snapshot': int(snapshot), 'raw_flags': flags,
            'raw_action': action, 'raw_side': row['raw_side'],
            'known_at_ns': int(row['known_at_ns']), 'source_key': row['source_key'],
            'source_row': int(row['source_row']), 'economic_at': int(economic_at),
        }
    expose(previous, previous['t'] if previous is not None else start_ns, end_ns)
    n = pressure
    return {
        'instrument_id': instrument_id, 'event_start_ns': start_ns, 'event_end_ns': end_ns,
        'known_at_ns': end_ns + delay, 'latency_scenario_ns': delay,
        'quote_or_invalidation_rows': events, 'fresh_quote_updates': fresh,
        'pressure_transitions': n, 'invalid_book_rows': invalid, 'snapshot_rows': snapshots,
        'gap_rows': gaps, 'clear_rows': clears, 'equal_time_adjacent_quote_rows': equal_times,
        'action_side_counts': [{'action': a, 'side': s, 'rows': count}
                               for (a, s), count in sorted(action_sides.items(), key=lambda item: repr(item[0]))],
        'ofi_contracts': ofi, 'same_price_size_ofi': same_ofi, 'price_change_ofi': price_ofi,
        'ofi_path': {'open': 0, 'high': ofi_high, 'low': ofi_low, 'close': ofi,
                     'high_at_ns': ofi_high_at, 'low_at_ns': ofi_low_at,
                     'high_source_order': ofi_high_order, 'low_source_order': ofi_low_order},
        'sum_depth_normalized_ofi': math.fsum(dn_ofi),
        'update_mean_imbalance': (math.fsum(imbalance) / n) if n else None,
        'update_positive_fraction': (positive_updates / n) if n else None,
        'update_mean_microprice_minus_midpoint_ticks': (math.fsum(micro) / n) if n else None,
        'update_mean_spread_ticks': (math.fsum(spreads) / n) if n else None,
        'observed_trusted_standing_duration_ns': duration,
        'duration_mean_imbalance': (math.fsum(dur_imb) / duration) if duration else None,
        'duration_mean_spread_ticks': (math.fsum(dur_spread) / duration) if duration else None,
        'duration_positive_fraction': (positive_duration / duration) if duration else None,
        'displayed_midpoint_occupancy': {
            'duration_ns_by_row': tuple(sorted(midpoint.items())),
            'observed_assigned_duration_ns': duration,
            'unassigned_duration_ns': end_ns - start_ns - duration,
        },
        'initial_projection': initial_projection, 'terminal_projection': previous,
        'pressure_increments': increments, 'visits': visits,
    }


def _compare_other_columns(original, projected, counts):
    if not original.schema.equals(projected.schema, check_metadata=True):
        raise IntegrityError('candidate projection changed the original quote schema')
    index = original.schema.get_field_index('book_valid')
    if (original.schema.field(index).type != projected.schema.field(index).type
            or original.schema.field(index).metadata != projected.schema.field(index).metadata):
        raise IntegrityError('candidate projection changed the original book_valid type')
    counts['compared_cells'] += 1
    for name in original.schema.names:
        if name == 'book_valid':
            continue
        if not original[name].equals(projected[name]):
            raise IntegrityError(f'candidate changed original column {name}')
        counts['compared_cells'] += len(original)


def _compact_mask(table, projected):
    import pyarrow as pa

    columns = {
        'source_key': table['source_key'],
        'instrument_id': table['instrument_id'],
        'source_row': table['source_row'],
        'source_order': table['source_order'],
        't': table['t'],
        'known_at_ns': table['known_at_ns'],
        'book_valid': projected['book_valid'],
    }
    return pa.table(columns)


def _initial_quote_state(measured, instrument, start_ns):
    carry = measured.get('measurement_continuation')
    if carry is not None:
        if type(carry) is not dict or type(carry.get('instruments')) not in (dict, type(None)):
            raise IntegrityError('unsupported initial measurement-state domain')
        instruments = carry.get('instruments') or {}
        state = instruments.get(str(instrument['instrument_id']))
        if state is not None:
            if type(state) is not dict:
                raise IntegrityError('unsupported initial measurement-state domain')
            quote = state.get('quote')
            if quote is not None:
                if type(quote) is not dict:
                    raise IntegrityError('unsupported initial measurement-state domain')
                return quote
    atoms = instrument.get('atomic_windows')
    if type(atoms) is list and atoms:
        first = atoms[0]
        if type(first) is not dict:
            raise IntegrityError('current measurement lost its one-minute atomic windows')
        quote = first.get('quote')
        if type(quote) is dict:
            initial = quote.get('initial_projection')
            if initial is not None:
                if type(initial) is not dict:
                    raise IntegrityError('unsupported initial measurement-state domain')
                if int(initial.get('t', -1)) >= start_ns:
                    raise IntegrityError('unsupported initial measurement-state domain')
                return initial
    return None


def _atom_bounds(atoms, *, start_ns, end_ns, width):
    expected = (end_ns - start_ns + width - 1) // width
    if type(atoms) is not list or len(atoms) != expected:
        raise IntegrityError('atomic cadence shifted away from the measured one-minute bounds')
    bounds = []
    for number, atom in enumerate(atoms):
        if type(atom) is not dict:
            raise IntegrityError('current measurement lost its one-minute atomic windows')
        a = _exact_int(atom.get('event_start_ns'), name='atom event_start_ns')
        b = _exact_int(atom.get('event_end_ns'), name='atom event_end_ns')
        want_a = start_ns + number * width
        want_b = min(want_a + width, end_ns)
        if a != want_a or b != want_b:
            raise IntegrityError('atomic cadence shifted away from the measured one-minute bounds')
        if type(atom.get('quote')) is not dict:
            raise IntegrityError('current measurement lost its original minute quote record')
        bounds.append((a, b, atom))
    return bounds


def _wrap_quote(record, *, source_complete, coordinate_complete, start_ns, end_ns):
    wrapped = dict(record)
    wrapped['coverage_complete'] = source_complete
    wrapped['per_complete_window_second_ofi'] = (
        wrapped['ofi_contracts'] * 1e9 / (end_ns - start_ns) if source_complete else None)
    wrapped['full_standing_window_eligible'] = bool(
        source_complete and coordinate_complete
        and wrapped['observed_trusted_standing_duration_ns'] == end_ns - start_ns)
    wrapped['full_pressure_transition_window_eligible'] = bool(
        wrapped['full_standing_window_eligible']
        and wrapped['initial_projection'] is not None
        and wrapped['initial_projection']['book_valid'])
    wrapped['original_consumer_book_recovery'] = record.get('book_recovery', ORIGINAL_CONSUMER_BOOK_RECOVERY)
    wrapped['book_recovery'] = CANDIDATE_BOOK_RECOVERY
    wrapped['policy'] = POLICY
    wrapped['policy_version'] = CANDIDATE_VERSION
    wrapped['publication_status'] = 'unpublished_validation_candidate'
    wrapped['source_history_repaired'] = False
    wrapped['admitted_for_serving'] = False
    wrapped['venue_or_exchange_order_certified'] = False
    return wrapped


def _copy_minute(record):
    return {name: record[name] for name in _MINUTE_RETAINED if name in record}


def _compose_ofi_path(records):
    running = 0
    high = 0
    low = 0
    high_at = high_order = low_at = low_order = None
    for record in records:
        path = record['ofi_path']
        if record['pressure_transitions']:
            cand_high = running + path['high']
            cand_low = running + path['low']
            if cand_high > high:
                high = cand_high
                high_at = path['high_at_ns']
                high_order = path['high_source_order']
            if cand_low < low:
                low = cand_low
                low_at = path['low_at_ns']
                low_order = path['low_source_order']
        running += path['close']
    return {'open': 0, 'high': high, 'low': low, 'close': running,
            'high_at_ns': high_at, 'low_at_ns': low_at,
            'high_source_order': high_order, 'low_source_order': low_order}


def _merge_action_sides(records):
    merged = {}
    for record in records:
        for item in record['action_side_counts']:
            key = (item['action'], item['side'])
            merged[key] = merged.get(key, 0) + item['rows']
    return [{'action': a, 'side': s, 'rows': count}
            for (a, s), count in sorted(merged.items(), key=lambda item: repr(item[0]))]


def _merge_occupancy(records):
    mass = {}
    duration = 0
    for record in records:
        occupancy = record['displayed_midpoint_occupancy']
        duration += occupancy['observed_assigned_duration_ns']
        for row, amount in occupancy['duration_ns_by_row']:
            mass[int(row)] = mass.get(int(row), 0) + int(amount)
    return tuple(sorted(mass.items())), duration


def _weighted_mean(records, name, weights):
    total = 0.0
    weight = 0
    for record, amount in zip(records, weights, strict=True):
        value = record[name]
        if amount and value is not None:
            total += float(value) * amount
            weight += amount
    return None if weight == 0 else total / weight


def _compare_quote_fields(original, candidate, *, absolute, relative, counts):
    equal = {}
    differ = {}
    for name in _EQUAL_QUOTE_FIELDS:
        if original[name] != candidate[name]:
            raise IntegrityError(f'candidate changed a source-population quote field: {name}')
        equal[name] = original[name]
        counts['compared_cells'] += 1
    for name in (
            'fresh_quote_updates', 'pressure_transitions', 'invalid_book_rows', 'ofi_contracts',
            'same_price_size_ofi', 'price_change_ofi', 'observed_trusted_standing_duration_ns',
            'sum_depth_normalized_ofi', 'update_mean_imbalance', 'update_mean_spread_ticks',
            'update_mean_microprice_minus_midpoint_ticks', 'duration_mean_imbalance',
            'duration_mean_spread_ticks', 'update_positive_fraction', 'duration_positive_fraction',
            'terminal_projection', 'ofi_path'):
        left, right = original.get(name), candidate.get(name)
        if name in ('sum_depth_normalized_ofi',) or (isinstance(left, float) or isinstance(right, float)):
            same = _float_close(left, right, absolute=absolute, relative=relative)
        else:
            same = left == right
        if same:
            equal[name] = left
        else:
            differ[name] = {'original': left, 'candidate': right}
        counts['compared_cells'] += 1
    return equal, differ


def _compare_composed(whole, atoms, *, start_ns, end_ns, source_complete, absolute, relative, counts):
    for name in _INTEGER_COMPOSITION:
        expected = sum(item[name] for item in atoms)
        if whole[name] != expected:
            raise IntegrityError(f'whole candidate {name} disagrees with carried minute composition')
        counts['compared_cells'] += 1
    if _merge_action_sides(atoms) != whole['action_side_counts']:
        raise IntegrityError('whole candidate action_side_counts disagree with carried minute composition')
    counts['compared_cells'] += 1
    composed_path = _compose_ofi_path(atoms)
    if composed_path != whole['ofi_path']:
        raise IntegrityError('whole candidate OFI path disagrees with composed minute paths')
    counts['compared_cells'] += 1
    occupancy, duration = _merge_occupancy(atoms)
    if duration != whole['observed_trusted_standing_duration_ns']:
        raise IntegrityError('whole candidate standing exposure disagrees with carried minute composition')
    if occupancy != tuple(whole['displayed_midpoint_occupancy']['duration_ns_by_row']):
        raise IntegrityError('whole candidate midpoint occupancy disagrees with carried minute composition')
    counts['compared_cells'] += 2
    n_weights = [item['pressure_transitions'] for item in atoms]
    d_weights = [item['observed_trusted_standing_duration_ns'] for item in atoms]
    for name in _WEIGHTED_UPDATE_MEANS:
        expected = _weighted_mean(atoms, name, n_weights)
        if not _float_close(whole[name], expected, absolute=absolute, relative=relative):
            raise IntegrityError(f'whole candidate {name} is not a denominator-weighted minute composition')
        counts['compared_cells'] += 1
    for name in _WEIGHTED_DURATION_MEANS:
        expected = _weighted_mean(atoms, name, d_weights)
        if not _float_close(whole[name], expected, absolute=absolute, relative=relative):
            raise IntegrityError(f'whole candidate {name} is not a denominator-weighted minute composition')
        counts['compared_cells'] += 1
    expected_sum = math.fsum(item['sum_depth_normalized_ofi'] for item in atoms)
    if not _float_close(whole['sum_depth_normalized_ofi'], expected_sum, absolute=absolute, relative=relative):
        raise IntegrityError('whole candidate sum_depth_normalized_ofi disagrees with carried minute composition')
    counts['compared_cells'] += 1
    n = whole['pressure_transitions']
    expected_per = whole['ofi_contracts'] / n if n else None
    if not _float_close(whole['per_pressure_transition_ofi'], expected_per, absolute=absolute, relative=relative):
        raise IntegrityError('whole candidate per-pressure OFI is not recomputed from composed totals')
    expected_rate = (whole['ofi_contracts'] * 1e9 / (end_ns - start_ns)) if source_complete else None
    if not _float_close(whole['per_complete_window_second_ofi'], expected_rate, absolute=absolute, relative=relative):
        raise IntegrityError('whole candidate per-second OFI is not recomputed from composed totals and original coverage')
    counts['compared_cells'] += 2
    return {
        'integer_composition_equal': True,
        'ofi_path_composed_from_minute_paths': True,
        'floating_denominator_weighted': True,
        'not_composable_from_published_sufficient_statistics': list(_NON_COMPOSABLE),
        'non_composable_resolution': (
            'per-minute rates are not summed; per_pressure_transition_ofi and '
            'per_complete_window_second_ofi are recomputed from composed integer totals '
            'and the original source-coverage decision'
        ),
    }


def _compare_quote_records(actual, expected, *, absolute, relative, counts, label):
    for name in _INTEGER_COMPOSITION + (
            'action_side_counts',):
        if actual[name] != expected[name]:
            raise IntegrityError(f'{label} quote field {name} disagrees with the independent scalar loop')
        counts['compared_cells'] += 1
    if actual['ofi_path'] != expected['ofi_path']:
        raise IntegrityError(f'{label} OFI path disagrees with the independent scalar loop')
    counts['compared_cells'] += 1
    for name in ('sum_depth_normalized_ofi', *_WEIGHTED_UPDATE_MEANS, *_WEIGHTED_DURATION_MEANS):
        if not _float_close(actual[name], expected[name], absolute=absolute, relative=relative):
            raise IntegrityError(f'{label} quote field {name} disagrees with the independent scalar loop')
        counts['compared_cells'] += 1


def _logical_terminal(report):
    return {name: report[name] for name in _LOGICAL_TERMINAL}


def _prefix_episodes(episodes, last_order):
    kept = []
    for item in episodes:
        inv_order = item['invalidation']['source_order']
        if inv_order > last_order:
            continue
        recovery = item['recovery']
        if recovery is None or recovery['source_order'] > last_order:
            kept.append({**item, 'recovery': None, 'unresolved': True})
        else:
            kept.append(item)
    return kept


def _join_manifest(measured, quote_storage, *, delay, start_ns, end_ns, decoded_rows):
    manifest = measured.get('source_manifest')
    if type(manifest) is not dict:
        raise IntegrityError('current measurement lost its source_manifest')
    if 'event_latency_scenario_ns' in manifest:
        if type(manifest['event_latency_scenario_ns']) is not int or manifest['event_latency_scenario_ns'] != delay:
            raise IntegrityError('source_manifest event_latency_scenario_ns does not equal known_at-end')
    if 'start_ns' in manifest and manifest['start_ns'] != start_ns:
        raise IntegrityError('source_manifest start_ns does not join the retained unit')
    if 'end_ns' in manifest and manifest['end_ns'] != end_ns:
        raise IntegrityError('source_manifest end_ns does not join the retained unit')
    projection = manifest.get('projection')
    if type(projection) is not dict or type(projection.get('counts')) is not dict:
        raise IntegrityError('source_manifest lost projection quote_rows')
    quote_rows = projection['counts'].get('quote_rows')
    if type(quote_rows) is not int or quote_rows < 0:
        raise IntegrityError('source_manifest lost projection quote_rows')
    if type(quote_storage.get('rows')) is not int or quote_storage['rows'] != quote_rows:
        raise IntegrityError('retained quote series disagrees with source_manifest projection counts')
    if decoded_rows != quote_rows:
        raise IntegrityError('decoded quote rows disagree with source_manifest projection counts')
    return manifest


def _require_measurement_reference(reference):
    if (type(reference) is not dict or type(reference.get('path')) is not str or not reference['path']
            or type(reference.get('sha256')) is not str or len(reference['sha256']) != 64
            or type(reference.get('size_bytes')) is not int or reference['size_bytes'] < 0
            or type(reference.get('kind')) is not str or not reference['kind']):
        raise IntegrityError('complete size/hash-bound measurement reference required')
    return reference


class _InstrumentWork:
    def __init__(self, *, instrument, start_ns, end_ns, delay, cut_ns, maximum_rows,
                 maximum_episodes, prefix_limit, initial):
        raw_id = _exact_int(instrument.get('instrument_id'), name='instrument_id', minimum=1)
        coordinate = instrument.get('coordinate')
        if type(coordinate) is not dict:
            raise IntegrityError('current measurement lost its raw coordinate identity')
        whole = instrument.get('whole_window')
        if type(whole) is not dict:
            raise IntegrityError('current measurement lost its whole-window tape')
        self.instrument_id = raw_id
        self.coordinate = coordinate
        self.whole_source = _exact_bool(whole.get('source_coverage_complete'),
                                        name='whole source_coverage_complete')
        self.whole_coord = _exact_bool(whole.get('coordinate_complete'),
                                       name='whole coordinate_complete')
        self.atoms = _atom_bounds(instrument.get('atomic_windows'), start_ns=start_ns,
                                  end_ns=end_ns, width=ATOMIC_WIDTH_NS)
        self.full = ReportedBBOReinitializer(
            instrument_id=raw_id, start_ns=start_ns, end_ns=end_ns, latency_ns=delay,
            maximum_rows=maximum_rows, maximum_episodes=maximum_episodes)
        self.left = ReportedBBOReinitializer(
            instrument_id=raw_id, start_ns=start_ns, end_ns=cut_ns, latency_ns=delay,
            maximum_rows=maximum_rows, maximum_episodes=maximum_episodes)
        self.right = None
        self.left_finished = False
        self.left_report = None
        self.left_carry = None
        self.right_report = None
        self.full_report = None
        self.vector = {
            'last_inv': -1, 'last_rec': -1, 'next_pos': 0, 'history_complete': True,
            'last_candidate_valid': 0, 'provider_flagged': 0, 'clear_rows': 0, 'unknown_rows': 0,
        }
        self.prefix_parts = []
        self.prefix_candidate = []
        self.prefix_n = 0
        self.prefix_limit = prefix_limit
        self.recoveries = []
        self.last_clock = (None, None, None)
        self.last_bbo = None
        self.source_key = None
        self.rows = 0
        self.original_valid = 0
        self.candidate_valid = 0
        self.changed = 0
        self.whole_quote = QuoteWindow(
            instrument_id=raw_id, start_ns=start_ns, end_ns=end_ns, latency_ns=delay,
            initial_state=initial)
        first_start, first_end, _ = self.atoms[0]
        self.atom = QuoteWindow(
            instrument_id=raw_id, start_ns=first_start, end_ns=first_end, latency_ns=delay,
            initial_state=initial)
        self.atom_bin = 0
        self.closed_atoms = {}
        self.empty = True
        self.start_ns = start_ns
        self.end_ns = end_ns
        self.cut_ns = cut_ns
        self.delay = delay
        self.maximum_rows = maximum_rows
        self.maximum_episodes = maximum_episodes

    def _ensure_right(self):
        if self.left_finished:
            return
        self.left_report = self.left.finish(coverage_complete=self.whole_source)
        self.left_carry = self.left.carry()
        self.right = ReportedBBOReinitializer(
            instrument_id=self.instrument_id, start_ns=self.cut_ns, end_ns=self.end_ns,
            latency_ns=self.delay, maximum_rows=self.maximum_rows,
            maximum_episodes=self.maximum_episodes, continuation=self.left_carry)
        self.left_finished = True

    def _advance_atoms(self, number, counts):
        while self.atom_bin < number:
            self.closed_atoms[self.atom_bin] = self.atom.finish(coverage_complete=False)
            self.atom_bin += 1
            if self.atom_bin < len(self.atoms):
                self.atom = self.atom.continue_window(end_ns=self.atoms[self.atom_bin][1])

    def add(self, table, *, counts, cpu):
        import numpy as np

        if not len(table):
            return None
        started = time.process_time()
        key = _unique_source_key(table)
        if self.source_key is None:
            self.source_key = key
        elif key != self.source_key:
            raise IntegrityError('a reported-BBO window cannot join distinct acquired source streams')
        self.last_clock = _validate_clocks(
            table, start_ns=self.start_ns, end_ns=self.end_ns, delay=self.delay,
            last=self.last_clock, instrument_id=self.instrument_id)
        saved_valid = table['book_valid'].combine_chunks() if hasattr(table['book_valid'], 'combine_chunks') else table['book_valid']
        started = _acc(cpu, 'filtering_and_preparation', started)
        projected = self.full.add(table)
        if not table['book_valid'].equals(saved_valid):
            raise IntegrityError('original input book_valid was mutated')
        _compare_other_columns(table, projected, counts)
        counts['candidate_rows'] += len(table)
        started = _acc(cpu, 'candidate_masks', started)
        expected, first_recovery = _independent_vector_mask(table, self.vector)
        actual = projected['book_valid'].combine_chunks().to_numpy(zero_copy_only=False).astype(np.uint8, copy=False)
        if not np.array_equal(actual, expected):
            raise IntegrityError('candidate book_valid disagrees with the independent full-source vector mask')
        counts['independent_mask_rows'] += len(table)
        counts['full_source_vector_mask_rows_compared'] += len(table)
        counts['compared_cells'] += len(table)
        original = saved_valid.to_numpy(zero_copy_only=False).astype(np.uint8, copy=False)
        self.rows += len(table)
        self.original_valid += int(np.count_nonzero(original))
        self.candidate_valid += int(np.count_nonzero(actual))
        self.changed += int(np.count_nonzero(actual != original))
        self.empty = False
        if self.prefix_n < self.prefix_limit:
            take = min(self.prefix_limit - self.prefix_n, len(table))
            self.prefix_parts.append(table.slice(0, take))
            self.prefix_candidate.append(expected[:take].copy())
            self.prefix_n += take
        recovery_idx = np.flatnonzero(first_recovery)
        counts['python_episode_transition_visits'] += int(recovery_idx.size)
        for index in recovery_idx.tolist():
            current = _row_bbo(table, int(index))
            current['book_valid'] = int(actual[int(index)])
            self.recoveries.append({
                'address': _row_address(table, int(index), source_key=key, delay=self.delay),
                'original_bbo': _row_bbo(table, int(index)),
                'candidate_bbo': current,
                'preceding_bbo': None if self.last_bbo is None and index == 0 else (
                    self.last_bbo if index == 0 else _row_bbo(table, int(index) - 1)),
                'qualifying_original_completed_ordinary': _qualifying_restart_row(_row_bbo(table, int(index))),
                'preceding_invalid_for_pressure': True,
                'ofi_from_missing_interval': 0,
            })
            counts['first_recoveries_verified'] += 1
        last = _row_bbo(table, len(table) - 1)
        last['book_valid'] = int(actual[-1])
        self.last_bbo = last
        started = _acc(cpu, 'independent_full_masks', started)
        left, right = _split_cut(table, self.cut_ns)
        if len(left):
            if self.left_finished:
                raise IntegrityError('adjacent cut lost original source order')
            left_projected = self.left.add(left)
            left_valid = left_projected['book_valid'].combine_chunks().to_numpy(zero_copy_only=False)
            if not np.array_equal(left_valid.astype(np.uint8, copy=False), actual[:len(left)]):
                raise IntegrityError('adjacent left candidate book_valid disagrees with the unpartitioned candidate')
            counts['adjacent_rows'] += len(left)
            counts['compared_cells'] += len(left)
        if len(right):
            self._ensure_right()
            right_projected = self.right.add(right)
            right_valid = right_projected['book_valid'].combine_chunks().to_numpy(zero_copy_only=False)
            if not np.array_equal(right_valid.astype(np.uint8, copy=False), actual[len(left):]):
                raise IntegrityError('adjacent right candidate book_valid disagrees with the unpartitioned candidate')
            counts['adjacent_rows'] += len(right)
            counts['compared_cells'] += len(right)
        started = _acc(cpu, 'adjacent_carry', started)
        with prepare_quote_batch(projected) as prepared:
            counts['prepared_batches'] += 1
            counts['prepared_array_bytes'] += _prepared_bytes(prepared)
            self.whole_quote.add_prepared(prepared, 0, len(prepared))
            counts['quote_rows_whole'] += len(prepared)
            for number, left_i, right_i in prepared.atomic_slices(start=self.start_ns, width=ATOMIC_WIDTH_NS):
                self._advance_atoms(number, counts)
                self.atom.add_prepared(prepared, left_i, right_i)
                counts['quote_rows_atomic'] += right_i - left_i
        _acc(cpu, 'whole_atomic_quote_work', started)
        return projected

    def finish_quotes(self, counts):
        self._advance_atoms(len(self.atoms), counts)
        raw_whole = self.whole_quote.finish(coverage_complete=False)
        whole = _wrap_quote(
            raw_whole, source_complete=self.whole_source, coordinate_complete=self.whole_coord,
            start_ns=self.start_ns, end_ns=self.end_ns)
        minutes = []
        for number, (a, b, atom) in enumerate(self.atoms):
            raw = self.closed_atoms[number]
            source = _atom_source_complete(atom, self.whole_source)
            coord = _atom_coordinate_complete(atom, self.whole_coord)
            wrapped = _wrap_quote(raw, source_complete=source, coordinate_complete=coord, start_ns=a, end_ns=b)
            minutes.append((atom, wrapped, source, coord))
        return whole, minutes

    def finish_candidates(self):
        self.full_report = self.full.finish(coverage_complete=self.whole_source)
        self._ensure_right()
        if self.right is None:
            raise IntegrityError('adjacent right candidate was not restored from the left carry')
        self.right_report = self.right.finish(coverage_complete=self.whole_source)
        return self.full_report, self.left_report, self.right_report, self.left_carry


def _atom_source_complete(atom, fallback):
    quote = atom['quote']
    if 'coverage_complete' in quote:
        return _exact_bool(quote['coverage_complete'], name='atom coverage_complete')
    if 'source_coverage_complete' in quote:
        return _exact_bool(quote['source_coverage_complete'], name='atom source_coverage_complete')
    if type(atom.get('source_quality')) is dict and 'source_complete' in atom['source_quality']:
        return _exact_bool(atom['source_quality']['source_complete'], name='atom source_quality')
    return fallback


def _atom_coordinate_complete(atom, fallback):
    coordinate = atom.get('coordinate')
    if type(coordinate) is dict and 'complete' in coordinate:
        return _exact_bool(coordinate['complete'], name='atom coordinate complete')
    quote = atom['quote']
    if 'coordinate_complete' in quote:
        return _exact_bool(quote['coordinate_complete'], name='atom coordinate_complete')
    return fallback


def _compare_adjacent(full_report, left_report, right_report, left_carry, *, start_ns, cut_ns, end_ns, counts):
    if not start_ns < cut_ns < end_ns:
        raise IntegrityError('adjacent cut is not a positive interior split')
    if (left_report['event_end_ns'] != cut_ns or right_report['event_start_ns'] != cut_ns
            or left_carry['next_start_ns'] != cut_ns or left_carry['event_end_ns'] != cut_ns
            or left_report['prefix_start_ns'] != full_report['prefix_start_ns']
            or right_report['prefix_start_ns'] != full_report['prefix_start_ns']):
        raise IntegrityError('adjacent reported-BBO intervals are not source-continuous')
    left_logical = _logical_terminal(full_report)
    right_logical = _logical_terminal(right_report)
    if left_logical != right_logical:
        raise IntegrityError('adjacent carry lost a logical terminal episode, address, count or history field')
    counts['compared_cells'] += len(_LOGICAL_TERMINAL)
    if right_report['current_interval_rows'] != right_report['rows'] - left_report['rows']:
        raise IntegrityError('adjacent right current_interval_rows is not the current interval population')
    if left_report['current_interval_rows'] != left_report['rows']:
        raise IntegrityError('adjacent left current_interval_rows is not the current interval population')
    if left_report['empty_observed_window'] != (left_report['current_interval_rows'] == 0):
        raise IntegrityError('empty left interval is not explicit')
    if right_report['empty_observed_window'] != (right_report['current_interval_rows'] == 0):
        raise IntegrityError('empty right interval is not explicit')
    return {
        'cut_ns': cut_ns,
        'positive_adjacency': True,
        'source_continuity': True,
        'left_empty_observed_window': left_report['empty_observed_window'],
        'right_empty_observed_window': right_report['empty_observed_window'],
        'left_current_interval_rows': left_report['current_interval_rows'],
        'right_current_interval_rows': right_report['current_interval_rows'],
        'interval_specific_fields_not_byte_equal_to_full': list(_INTERVAL_ONLY),
        'carry_hash_differs_with_interval': True,
        'logical_terminal_equal': True,
    }


def _compare_scalar_prefix(work, full_report, *, delay, absolute, relative, counts, whole=None):
    import pyarrow as pa

    if not work.prefix_parts:
        return {
            'validation_kind': 'bounded_independent_scalar',
            'rows': 0, 'vector_equal': True, 'entire_unit_at_or_under_prefix_limit': work.rows == 0,
            'episodes': [], 'observed_history_complete': True,
            'distinct_from_full_source_vector': True,
        }
    prefix = pa.concat_tables(work.prefix_parts).combine_chunks()
    rows = prefix.to_pylist()
    expected = [int(value) for part in work.prefix_candidate for value in part.tolist()]
    scalar, status = _independent_scalar_mask(rows, delay=delay)
    counts['bounded_scalar_reference_rows'] += len(rows)
    counts['scalar_reference_visits'] += status['visits']
    counts['python_reference_visits'] += status['visits']
    if scalar != expected:
        raise IntegrityError('bounded scalar mask disagrees with the independent full-source vector prefix')
    counts['compared_cells'] += len(rows)
    last_order = int(rows[-1]['source_order'])
    candidate_prefix = _prefix_episodes(full_report['episodes'], last_order)
    if status['episodes'] != candidate_prefix:
        raise IntegrityError('bounded scalar episodes disagree with the prefix of the candidate lineage')
    if status['observed_history_complete'] != (not any(bool(row['raw_flags'] & 4) or row['raw_action'] not in _KNOWN for row in rows)):
        raise IntegrityError('bounded scalar observed-history completeness disagrees with the retained prefix')
    counts['compared_cells'] += 1 + len(status['episodes'])
    projected_rows = []
    offset = 0
    for row, flag in zip(rows, expected, strict=True):
        item = dict(row)
        item['book_valid'] = int(flag)
        projected_rows.append(item)
        offset += 1
    prefix_end = work.end_ns if work.prefix_n == work.rows else min(work.end_ns, int(rows[-1]['t']) + 1)
    if prefix_end <= work.start_ns:
        prefix_end = work.start_ns + 1
    scalar_quote = _independent_quote_scalar(
        projected_rows, instrument_id=work.instrument_id, start_ns=work.start_ns,
        end_ns=prefix_end, delay=delay, initial=work.whole_quote.initial_projection)
    counts['python_reference_visits'] += scalar_quote['visits']
    prefix_window = QuoteWindow(
        instrument_id=work.instrument_id, start_ns=work.start_ns, end_ns=prefix_end,
        latency_ns=delay, initial_state=work.whole_quote.initial_projection)
    index = prefix.schema.get_field_index('book_valid')
    field = prefix.schema.field(index)
    import numpy as np
    replaced = prefix.set_column(index, field, pa.array(expected, type=field.type))
    prefix_window.add(replaced)
    prefix_record = prefix_window.finish(coverage_complete=False)
    _compare_quote_records(prefix_record, scalar_quote, absolute=absolute, relative=relative,
                           counts=counts, label='bounded scalar prefix')
    if whole is not None and work.prefix_n == work.rows:
        _compare_quote_records(whole, scalar_quote, absolute=absolute, relative=relative,
                               counts=counts, label='whole candidate versus bounded scalar')
    neighborhoods = []
    for recovery in work.recoveries:
        order = recovery['address']['source_order']
        if order > last_order:
            continue
        match = next((index for index, row in enumerate(projected_rows) if int(row['source_order']) == order), None)
        if match is None:
            continue
        if not recovery['qualifying_original_completed_ordinary']:
            raise IntegrityError('first recovered quote is not a qualifying original completed ordinary row')
        if recovery['preceding_bbo'] is not None and recovery['preceding_bbo']['book_valid']:
            raise IntegrityError('first recovered quote is not preceded by an invalid pressure state')
        local = _independent_quote_scalar(
            projected_rows[:match + 2], instrument_id=work.instrument_id, start_ns=work.start_ns,
            end_ns=prefix_end, delay=delay, initial=work.whole_quote.initial_projection)
        counts['python_reference_visits'] += local['visits']
        if any(item['index'] == match for item in local['pressure_increments']):
            raise IntegrityError('first recovery contributed OFI across the missing interval')
        later = [item for item in local['pressure_increments'] if item['index'] > match]
        if later:
            prev = projected_rows[later[0]['index'] - 1]
            curr = projected_rows[later[0]['index']]
            expected_ofi, expected_same = _four_indicator_ofi(prev, curr)
            if later[0]['ofi'] != expected_ofi or later[0]['same'] != expected_same:
                raise IntegrityError('later eligible ordinary transition lost the literal four-indicator OFI')
        neighborhoods.append({
            'source_order': order, 'zero_ofi_from_missing_interval': True,
            'later_four_indicator_ofi': None if not later else later[0]['ofi'],
        })
    return {
        'validation_kind': 'bounded_independent_scalar',
        'rows': len(rows),
        'vector_equal': True,
        'entire_unit_at_or_under_prefix_limit': work.prefix_n == work.rows,
        'episodes': status['episodes'],
        'observed_history_complete': status['observed_history_complete'],
        'blocked': status['blocked'],
        'distinct_from_full_source_vector': True,
        'quote_scalar_equal': True,
        'recovery_neighborhoods': neighborhoods,
    }


def check_book_unit(measured, unit, *, measurement_reference, quote_storage, outputs, contract):
    """Full-source reported-BBO candidate comparison for one retained unit."""
    cpu, counts = _cpu(), _counts()
    wall_start = time.perf_counter()
    entry = started = time.process_time()
    byte_start = outputs.written
    if not isinstance(outputs, BoundedOutputs):
        raise ContractError('bounded registered outputs required')
    _validate_contract(contract)
    _require_measurement_reference(measurement_reference)
    if type(measured) is not dict or type(unit) is not dict:
        raise IntegrityError('current measured window does not join the retained unit identity')
    root = unit.get('root')
    if type(root) is not str or not root:
        raise IntegrityError('current unit lost its retained root')
    if measured.get('root') not in (None, root):
        raise IntegrityError('current measured root does not join the retained unit identity')
    start_ns = _exact_int(measured.get('event_start_ns'), name='current event_start_ns')
    end_ns = _exact_int(measured.get('event_end_ns'), name='current event_end_ns')
    known_at = _exact_int(measured.get('known_at_ns'), name='current known_at_ns')
    if start_ns != unit.get('event_start_ns') or end_ns != unit.get('event_end_ns'):
        raise IntegrityError('current measured window does not join the retained unit identity')
    delay = known_at - end_ns
    if type(delay) is not int or not 0 <= delay <= 1_000_000_000:
        raise IntegrityError('current unit lost its retained source delay')
    instruments = measured.get('instruments')
    if type(instruments) is not list:
        raise IntegrityError('current measurement lost its raw-instrument population')
    if any(type(item.get('instrument_id')) is not int or item['instrument_id'] <= 0 for item in instruments):
        raise IntegrityError('current measurement lost an exact raw instrument identity')
    raw_ids = tuple(item['instrument_id'] for item in instruments)
    if len(set(raw_ids)) != len(raw_ids):
        raise IntegrityError('duplicate current instrument IDs')
    listed = set(raw_ids)
    cut_ns, cut_kind = _interior_cut(start_ns, end_ns)
    absolute = contract['comparison_tolerances']['floating_absolute']
    relative = contract['comparison_tolerances']['floating_relative']
    variant = unit.get('source_variant') or 'unit'
    if type(variant) is not str or not variant:
        raise IntegrityError('current unit lost its retained source variant')
    started = _acc(cpu, 'entry_validation', started)
    mask_series = None
    works = {}
    live = []
    try:
        mask_series = ParquetSeries(outputs, f'{root}-{start_ns}-{variant}-book-validity', encoding='plain')
        for instrument in instruments:
            initial = _initial_quote_state(measured, instrument, start_ns)
            works[instrument['instrument_id']] = _InstrumentWork(
                instrument=instrument, start_ns=start_ns, end_ns=end_ns, delay=delay,
                cut_ns=cut_ns, maximum_rows=contract['maximum_rows_per_instrument'],
                maximum_episodes=contract['maximum_episodes_per_instrument'],
                prefix_limit=contract['maximum_scalar_prefix_rows'], initial=initial)
        started = _acc(cpu, 'entry_validation', started)
        decoder = read_series_tables(quote_storage)
        while True:
            decode_at = time.process_time()
            try:
                table = next(decoder)
            except StopIteration:
                cpu['retained_cache_decoding'] += time.process_time() - decode_at
                break
            cpu['retained_cache_decoding'] += time.process_time() - decode_at
            counts['decoded_batches'] += 1
            counts['decoded_rows'] += len(table)
            started = time.process_time()
            _require_quote_columns(table)
            started = _acc(cpu, 'retained_cache_decoding', started)
            assigned = 0
            for raw_id in raw_ids:
                kept = _filter_instrument(table, raw_id)
                if not len(kept):
                    continue
                assigned += len(kept)
                counts['instrument_slices'] += 1
                counts['instrument_slice_rows'] += len(kept)
                started = _acc(cpu, 'filtering_and_preparation', started)
                projected = works[raw_id].add(kept, counts=counts, cpu=cpu)
                started = time.process_time()
                compact = _compact_mask(kept, projected)
                mask_series.append(compact)
                counts['emitted_mask_rows'] += len(compact)
                started = _acc(cpu, 'serialization', started)
            leftover = len(table) - assigned
            if leftover:
                raise IntegrityError('retained quote does not belong to a declared current raw instrument')
            started = _acc(cpu, 'filtering_and_preparation', started)
        _join_manifest(measured, quote_storage, delay=delay, start_ns=start_ns, end_ns=end_ns,
                       decoded_rows=counts['decoded_rows'])
        started = _acc(cpu, 'retained_cache_decoding', started)
        reports = []
        for instrument in instruments:
            work = works[instrument['instrument_id']]
            if work.source_key is None and not work.empty:
                raise IntegrityError('a reported-BBO window cannot join distinct acquired source streams')
            started = time.process_time()
            work.full_report = work.full.finish(coverage_complete=work.whole_source)
            started = _acc(cpu, 'candidate_masks', started)
            work._ensure_right()
            work.right_report = work.right.finish(coverage_complete=work.whole_source)
            full_report, left_report, right_report, left_carry = (
                work.full_report, work.left_report, work.right_report, work.left_carry)
            counts['python_episode_transition_visits'] += work.full.episode_transition_visits
            adjacent = _compare_adjacent(
                full_report, left_report, right_report, left_carry,
                start_ns=start_ns, cut_ns=cut_ns, end_ns=end_ns, counts=counts)
            started = _acc(cpu, 'adjacent_carry', started)
            whole, minutes = work.finish_quotes(counts)
            started = _acc(cpu, 'whole_atomic_quote_work', started)
            minute_reports = []
            atom_records = []
            for number, (atom, wrapped, source, coord) in enumerate(minutes):
                original = atom['quote']
                equal, differ = _compare_quote_fields(
                    original, wrapped, absolute=absolute, relative=relative, counts=counts)
                minute_reports.append({
                    'bin': atom.get('bin', number), 'event_start_ns': atom['event_start_ns'],
                    'event_end_ns': atom['event_end_ns'],
                    'original': _copy_minute(original),
                    'candidate': wrapped,
                    'equal_source_population_fields': equal,
                    'trust_pressure_exposure_differences': differ,
                    'inherited_source_coverage_complete': source,
                    'inherited_coordinate_complete': coord,
                    'source_quality': atom.get('source_quality'),
                })
                atom_records.append(wrapped)
            composition = _compare_composed(
                whole, atom_records, start_ns=start_ns, end_ns=end_ns,
                source_complete=work.whole_source, absolute=absolute, relative=relative, counts=counts)
            started = _acc(cpu, 'finalization_and_comparisons', started)
            scalar = _compare_scalar_prefix(
                work, full_report, delay=delay, absolute=absolute, relative=relative,
                counts=counts, whole=whole)
            started = _acc(cpu, 'scalar_reference', started)
            reports.append({
                'instrument_id': work.instrument_id,
                'coordinate': work.coordinate,
                'source_key': work.source_key,
                'empty_observed_window': work.empty,
                'full_source_vector': {
                    'validation_kind': 'full_source_vector_mask',
                    'rows_compared': work.rows,
                    'equal': True,
                    'distinct_from_bounded_scalar': True,
                },
                'bounded_scalar_reference': scalar,
                'candidate_report': full_report,
                'adjacent': adjacent,
                'changed_book_valid_rows': work.changed,
                'original_valid_rows': work.original_valid,
                'candidate_valid_rows': work.candidate_valid,
                'provider_flagged_records': full_report['provider_flagged_records'],
                'invalidation_episodes': full_report['episode_count'],
                'provider_flagged_records_are_not_missing_downloads': True,
                'provider_flagged_records_are_not_lost_trades': True,
                'first_recoveries': work.recoveries,
                'quotes': {
                    'whole': whole,
                    'atomic': minute_reports,
                    'composition': composition,
                },
                'source_lineage': {
                    'prefix_start_ns': full_report['prefix_start_ns'],
                    'last_source_address': full_report['last_source_address'],
                    'episodes': full_report['episodes'],
                    'observed_history_complete': full_report['observed_history_complete'],
                    'blocked': full_report['blocked'],
                },
            })
        mask_ref = mask_series.finish()
        counts['emitted_mask_bytes'] = mask_ref['serialized_bytes']
        counts['serialized_bytes'] += mask_ref['serialized_bytes']
        counts['serialized_artifacts'] += 1
        started = _acc(cpu, 'serialization', started)
        result = {
            'version': VERSION, 'kind': CONTRACT_KIND,
            'publication_status': 'unpublished_validation_candidate',
            'admitted_for_serving': False,
            'candidate_global_source_replacement': False,
            'context_or_location_evaluation': False,
            'family_statistics_complete': False,
            'annual_or_model_workload_projection_complete': False,
            'venue_or_exchange_order_certified': False,
            'source_history_repaired': False,
            'policy': POLICY, 'policy_version': CANDIDATE_VERSION,
            'source_assumption': contract['source_assumption'],
            'unit': {'root': root, 'event_start_ns': start_ns, 'event_end_ns': end_ns,
                     'known_at_ns': known_at, 'source_variant': variant,
                     'source_path': unit.get('source_path'), 'cash_date': unit.get('cash_date')},
            'measurement_reference': measurement_reference,
            'original_quote_series': {
                'rows': quote_storage['rows'], 'schema': quote_storage.get('schema'),
                'files': [{'path': item.get('path'), 'sha256': item.get('sha256'),
                           'size_bytes': item.get('size_bytes'), 'rows': item.get('rows')}
                          for item in quote_storage.get('files', [])],
            },
            'mask_series': mask_ref,
            'cut_ns': cut_ns, 'cut_kind': cut_kind,
            'instruments': reports,
            'full_source_vector_mask_rows_compared': counts['full_source_vector_mask_rows_compared'],
            'bounded_scalar_reference_rows': counts['bounded_scalar_reference_rows'],
            'compared_cells': counts['compared_cells'],
            'passed': True,
            'limitations': list(LIMITATIONS),
            'scope': 'bounded unpublished reported-BBO comparison; not a full family study',
        }
        reference = outputs.json_compressed(
            f'{root}-{start_ns}-{variant}-book-validation.json.zst',
            result, kind='auction_flow_actual_reported_bbo_validation')
        counts['serialized_bytes'] += reference['size_bytes']
        counts['serialized_artifacts'] += 1
        started = _acc(cpu, 'serialization', started)
    except BaseException:
        if mask_series is not None and not mask_series.closed:
            mask_series.abort()
        raise
    finally:
        release_at = time.process_time()
        for prepared in live:
            prepared.release()
        cpu['release'] += time.process_time() - release_at
    helper_cpu = time.process_time() - entry
    named = sum(cpu[name] for name in _CPU_NAMES if name != 'orchestration_and_report_assembly')
    cpu['orchestration_and_report_assembly'] = helper_cpu - named
    if cpu['orchestration_and_report_assembly'] < 0:
        raise IntegrityError('disjoint reported-BBO helper CPU stages exceed the measured helper total')
    return {
        'passed': True,
        'reference': reference,
        'mask_series': mask_ref,
        'cpu_components_disjoint': cpu,
        'helper_cpu_seconds': helper_cpu,
        'wall_seconds': time.perf_counter() - wall_start,
        'serialization_cpu_seconds': reference['cpu_seconds'] + mask_ref['cpu_seconds'],
        'output_bytes': outputs.written - byte_start,
        'peak_process_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        'workload_counts': counts,
        'instruments': len(reports),
        'compared_cells': counts['compared_cells'],
        'emitted_mask_rows': counts['emitted_mask_rows'],
        'limitations': list(LIMITATIONS),
    }
