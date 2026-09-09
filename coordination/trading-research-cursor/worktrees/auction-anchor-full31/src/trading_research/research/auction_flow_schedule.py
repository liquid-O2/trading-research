"""Physical source-file/day extraction schedule and measured workload counts.

Every overlapping acquisition has its own ordered lineage. A file boundary
never supplies a recovery certificate or silently selects a preferred variant.
This schedule contains the full registered source population, including empty
days inside acquired file ranges and explicitly partial first/last windows.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import time

from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest


DAY_NS = 86_400_000_000_000
VERSION = 'auction-flow-physical-source-day-schedule-v2'


def _records(protocol, index):
    first, last = protocol['primary_start_ns'], protocol['frozen_available_cut_ns']
    for root in protocol['roots']:
        dataset = f'quantpad/cme__{root.lower()}-continuous-futures__mbp-1'
        for record in index['datasets'][dataset]:
            groups = record['groups']
            if any(g['minimum'] is None or g['maximum'] is None for g in groups):
                raise IntegrityError('unlocated original source requires an explicit bounded admission disposition')
            if groups and min(g['minimum'] for g in groups) < last and max(g['maximum'] for g in groups) >= first:
                yield root, dataset, record


def source_instrument_inventory(protocol, index, data_root, *, maximum_decoded_identity_rows=50_000_000):
    """Check all relevant original footers; decode only nonconstant ID groups.

    A single-valued, non-null instrument footer is an exact ID-set statement.
    A min/max interval containing several numbers is not. Such groups receive
    a bounded complete instrument-column read, without reading target outcomes.
    Their counts and cost are charged to the current registered source check.
    """
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    if type(maximum_decoded_identity_rows) is not int or not 0 <= maximum_decoded_identity_rows <= 50_000_000:
        raise ContractError('bounded supplemental raw-identity scan required')
    started = time.process_time()
    data_root = Path(data_root).resolve()
    result, decoded, footer_groups = [], 0, 0
    first, last = protocol['primary_start_ns'], protocol['frozen_available_cut_ns']
    for root, dataset, record in _records(protocol, index):
        path = (data_root / record['path']).resolve()
        if not path.is_relative_to(data_root):
            raise ContractError('original source identity escapes the registered data root')
        stamp = (record['bytes'], record['mtime_ns'])
        current = path.stat()
        if (current.st_size, current.st_mtime_ns) != stamp:
            raise IntegrityError('source identity inventory differs from its frozen file stamp')
        groups, all_ids = [], set()
        with pq.ParquetFile(path) as source:
            if (source.metadata.num_rows != record['rows'] or str(source.schema_arrow) != record['schema']
                    or source.metadata.num_row_groups != len(record['groups'])):
                raise IntegrityError('source identity inventory schema or row population changed')
            at_column = source.schema_arrow.get_field_index('t')
            id_column = source.schema_arrow.get_field_index('instrument_id')
            flags_column = source.schema_arrow.get_field_index('flags')
            if min(at_column, id_column, flags_column) < 0:
                raise IntegrityError('source identity inventory lacks its original clock or instrument')
            for group in record['groups']:
                if not group['minimum'] < last or not group['maximum'] >= first:
                    continue
                footer_groups += 1
                metadata = source.metadata.row_group(group['group'])
                clock = metadata.column(at_column).statistics
                if (metadata.num_rows != group['rows'] or clock is None or not clock.has_min_max
                        or (clock.min, clock.max) != (group['minimum'], group['maximum'])):
                    raise IntegrityError('retained source group clock or physical count changed')
                identity = metadata.column(id_column).statistics
                ids = set()
                method = 'constant_nonnull_footer'
                if (identity is not None and identity.has_min_max and identity.null_count == 0
                        and identity.min == identity.max):
                    ids.add(identity.min)
                else:
                    method = 'complete_bounded_identity_column'
                    if decoded + group['rows'] > maximum_decoded_identity_rows:
                        raise ContractError('ambiguous instrument groups exceed the registered identity-read allowance')
                    seen = 0
                    for batch in source.iter_batches(row_groups=[group['group']], columns=['instrument_id'],
                                                     batch_size=65536, use_threads=False):
                        values = batch.column(0)
                        if values.null_count:
                            raise IntegrityError(f"unlocated raw instrument in {record['path']} group {group['group']}: {values.null_count} null rows in this batch")
                        ids.update(pc.unique(values).to_pylist())
                        seen += len(batch)
                    if seen != group['rows']:
                        raise IntegrityError('complete source identity scan lost physical rows')
                    decoded += seen
                if any(type(value) is not int or not 0 < value < 2**63 for value in ids):
                    raise IntegrityError(f"invalid raw instrument in {record['path']} group {group['group']}: {sorted(ids, key=repr)}")
                flag_stats = metadata.column(flags_column).statistics
                flag_evidence = {'minimum': None, 'maximum': None, 'null_count': None,
                    'contains_proven_non_snapshot': False, 'all_rows_proven_snapshot': False}
                if flag_stats is not None:
                    flag_evidence['null_count'] = flag_stats.null_count
                    if flag_stats.has_min_max:
                        low, high = flag_stats.min, flag_stats.max
                        flag_evidence.update(minimum=low, maximum=high)
                        if type(low) is int and type(high) is int and 0 <= low <= high <= 255:
                            # Each attained non-null endpoint proves at least
                            # one actual record with that flag. We do not
                            # infer every intervening bitset was observed.
                            flag_evidence['contains_proven_non_snapshot'] = not low & 32 or not high & 32
                            flag_evidence['all_rows_proven_snapshot'] = (
                                flag_stats.null_count == 0 and all(value & 32 for value in range(low, high + 1)))
                groups.append({'group': group['group'], 'rows': group['rows'], 'instrument_ids': sorted(ids),
                    'basis': method, 'ownership_flag_footer_evidence': flag_evidence})
                all_ids.update(ids)
        current = path.stat()
        if (current.st_size, current.st_mtime_ns) != stamp:
            raise IntegrityError('source changed during the complete identity inventory')
        result.append({'root': root, 'dataset': dataset, 'source_path': record['path'],
            'source_metadata_sha256': digest(record), 'instrument_ids': sorted(all_ids), 'groups': groups})
    return {'version': 'auction-flow-complete-source-identity-inventory-v2', 'files': result,
        'checked_files': len(result), 'checked_groups': footer_groups, 'decoded_identity_rows': decoded,
        'maximum_decoded_identity_rows': maximum_decoded_identity_rows,
        'cpu_seconds': time.process_time() - started, 'target_outcomes_read': False,
        'source_instrument_sets_complete': True, 'exchange_completeness_claim': False}


def _window_instrument_bound(record, identity, start, end):
    """Bound allocations from actual group IDs and earlier ordinary ownership.

    This is resource metadata, never a feature or a causal contract selector.
    A completed constant-ID group with an attained non-snapshot flag endpoint
    proves the owner after that group. Snapshot-only groups cannot replace it;
    unknown flags conservatively keep both the prior and possible new owners.
    Missing evidence falls back to all file IDs, preserving the old bound.
    """
    rows = record['groups']
    metadata = {g['group']: g for g in identity['groups']}
    located = all(g['group'] in metadata and 'ownership_flag_footer_evidence' in metadata[g['group']] for g in rows)
    ordered = all(a['maximum'] <= b['minimum'] for a, b in zip(rows[:-1], rows[1:]))
    if not located or not ordered:
        return list(identity['instrument_ids']), 'all_file_ids_missing_ownership_or_boundary_order_evidence'
    prior, selected = set(), set()
    for group in rows:
        ids = set(metadata[group['group']]['instrument_ids'])
        evidence = metadata[group['group']]['ownership_flag_footer_evidence']
        if group['maximum'] < start:
            if len(ids) == 1 and evidence['contains_proven_non_snapshot']:
                prior = ids
            elif not evidence['all_rows_proven_snapshot']:
                prior |= ids
        elif group['minimum'] < end and group['maximum'] >= start:
            selected |= ids
    return sorted(prior | selected), 'selected_group_ids_plus_pre_window_ordinary_owner_candidates'


def plan_source_windows(protocol, index, *, instrument_inventory=None):
    first, last = protocol['primary_start_ns'], protocol['frozen_available_cut_ns']
    native_width, atomic_width = protocol['native_width_ns'], protocol['atomic_width_ns']
    identities = {} if instrument_inventory is None else {r['source_path']: r for r in instrument_inventory['files']}
    windows, bounds = [], defaultdict(lambda: defaultdict(int))
    for root, dataset, record in _records(protocol, index):
        minimum = min(g['minimum'] for g in record['groups'])
        maximum = max(g['maximum'] for g in record['groups']) + 1
        a, b = max(first, minimum), min(last, maximum)
        identity = identities.get(record['path'])
        if instrument_inventory is not None and (identity is None or identity['source_metadata_sha256'] != digest(record)):
            raise IntegrityError('source schedule has no exact matching complete instrument inventory')
        group_id_counts = {} if identity is None else {g['group']: len(g['instrument_ids']) for g in identity['groups']}
        if identity is not None and not identity['instrument_ids']:
            raise IntegrityError('nonempty source has no admitted raw instrument')
        for day in range(a // DAY_NS, (b - 1) // DAY_NS + 1):
            start, end = max(first, day * DAY_NS), min(last, (day + 1) * DAY_NS)
            instrument_ids, instrument_basis = (None, 'unresolved') if identity is None else _window_instrument_bound(
                record, identity, start, end)
            instrument_bound = None if instrument_ids is None else len(instrument_ids)
            groups = [g for g in record['groups'] if g['minimum'] < end and g['maximum'] >= start]
            scan = sum(g['rows'] for g in groups)
            if scan > protocol['resources']['maximum_source_day_scan_rows']:
                raise ContractError('complete source day requires a finer declared extraction partition')
            native = (end - start + native_width - 1) // native_width
            atomic = (end - start + atomic_width - 1) // atomic_width
            date = datetime.fromtimestamp(start // 10**9, timezone.utc).date()
            window = {'root': root, 'dataset': dataset, 'source_path': record['path'],
                'source_metadata_sha256': digest(record), 'utc_date': date.isoformat(), 'year': date.year,
                'event_start_ns': start, 'event_end_ns': end,
                'observed_file_start_ns': minimum, 'observed_file_end_ns': maximum,
                'whole_window_inside_acquired_file': minimum <= start and end <= maximum,
                'source_groups': [g['group'] for g in groups], 'physical_scan_rows': scan,
                'selected_raw_rows_upper': scan,
                'reader_batches_upper': (scan + 65535) // 65536 + max(0, len(groups) - 1),
                'reader_batch_bound_basis': 'fixed 65,536-row reader grid plus at most one split per intervening selected row-group boundary; pinned decoder checked before publication',
                'instrument_batches_upper': None if identity is None else sum(
                    ((g['rows'] + 65535) // 65536 + 1) * group_id_counts[g['group']] for g in groups),
                'atomic_cells_per_instrument': atomic, 'native_cells_per_instrument': native,
                'raw_instruments_per_window_upper': instrument_bound,
                'raw_instrument_allocation_ids_upper': instrument_ids,
                'instrument_allocation_bound_basis': instrument_basis,
                'native_instrument_cells_upper': None if instrument_bound is None else native * instrument_bound,
                'raw_variant_policy': 'separate physical acquisition; continuous carry within the same explicit source lineage',
                'first_window_of_physical_source': day == a // DAY_NS,
                'last_window_of_physical_source': day == (b - 1) // DAY_NS}
            windows.append(window)
            key = (root, date.year)
            part = bounds[key]
            part['source_windows'] += 1
            part['physical_scan_rows'] += scan
            part['selected_raw_rows_upper'] += scan
            part['reader_batches_upper'] += window['reader_batches_upper']
            part['source_groups_read'] += len(groups)
            part['native_cells_per_single_instrument'] += native
            if instrument_bound is not None:
                part['instrument_atomic_cells_upper'] += atomic * instrument_bound
                part['instrument_native_cells_upper'] += native * instrument_bound
                part['instrument_window_allocations_upper'] += instrument_bound
                part['instrument_batches_upper'] += window['instrument_batches_upper']
                # A sorted source batch can split an active cadence cell once
                # per represented instrument. Three consumers have separate
                # costs; they do not multiply this raw-part count again.
                part['atomic_parts_per_consumer_upper'] += instrument_bound * (atomic + window['reader_batches_upper'])
    partitions = [{'root': root, 'year': year, **dict(value)} for (root, year), value in sorted(bounds.items())]
    return {'version': VERSION, 'windows': sorted(windows, key=lambda r: (r['root'], r['source_path'], r['event_start_ns'])),
        'partitions': partitions, 'source_windows': len(windows),
        'instrument_allocation_bound_established': instrument_inventory is not None,
        'calendar': 'UTC extraction cuts; named economic formations remain separate',
        'independent_economic_dates': None,
        'source_overlap_aliases_applied': False,
        'full_extraction_authorized_by_this_schedule': False}
