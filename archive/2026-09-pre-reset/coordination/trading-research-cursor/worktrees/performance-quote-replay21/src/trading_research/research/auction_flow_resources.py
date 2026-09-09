"""Resource allowances from disjoint actual source/consumer/storage workloads.

No complete-window report is divided by its number of market events. Physical
reader batches, per-instrument batches, atomic consumers, native cells and
fixed source metadata have separate counts. Coefficients are measured maxima
with a stated margin; they are estimates, not mathematical complexity bounds.
"""
from __future__ import annotations

from trading_research.errors import IntegrityError


def source_cost_projection(units, protocol, schedule, *, excluded_storage_reserve_bytes_per_source_year=512 * 1024**2):
    if not units or not schedule['instrument_allocation_bound_established']:
        raise IntegrityError('complete measured units and physical instrument counts are required for source costing')
    if (type(excluded_storage_reserve_bytes_per_source_year) is not int
            or not 0 < excluded_storage_reserve_bytes_per_source_year <= protocol['resources']['maximum_derived_output_bytes']):
        raise IntegrityError('explicit bounded failure-population output reserve required')
    required_components = {'raw_atomic_batch_reduction', 'raw_atomic_counter_updates'}
    if any('raw_atomic_consumers' in u['scan_cpu_components_disjoint']
           or not required_components.issubset(u['scan_cpu_components_disjoint']) for u in units):
        raise IntegrityError('source costing needs the current disjoint batch/counter instrumentation; old parent regions cannot become zero cost')
    rates = {}
    detail = []

    def coefficient(name, values, scale, description):
        candidates = []
        for unit, cpu, count in values:
            if cpu < -1e-7 or count < 0:
                raise IntegrityError('measured source resource components overlap or have an invalid population')
            if count:
                candidates.append((max(0.0, cpu) / count, unit['unit']['source_path'], unit['unit']['event_start_ns']))
            elif cpu > 1e-3:
                raise IntegrityError('nonzero source component has no prospective workload count')
        rate, path, start = max(candidates, default=(0.0, None, None))
        rates[name] = {'cpu_seconds_per_work_unit': rate, 'prospective_count_field': scale,
                       'maximizing_source_path': path, 'maximizing_window_start_ns': start,
                       'work_unit': description}

    def source_value(u, name):
        return u['source_manifest']['source_cpu_components'].get(name, 0.0)

    coefficient('source_metadata_and_open', [(u, source_value(u, 'source_metadata_and_open'),
        len(u['source_manifest']['sources'])) for u in units], 'source_windows', 'one exact original source file in a requested interval')
    for name in ('physical_batch_decode', 'physical_address_and_selection'):
        coefficient(name, [(u, source_value(u, name), u['source_manifest']['physical_reader_batches']) for u in units],
            'reader_batches_upper', 'one bounded physical reader batch of at most 65,536 rows')
    coefficient('selected_projection', [(u, source_value(u, 'selected_projection'),
        u['workload_counts']['raw_instrument_batches']) for u in units], 'instrument_batches_upper',
        'one represented raw-instrument batch of at most 65,536 selected rows')
    for name, actual, prospective in (
            ('native_source_ownership', 'raw_batches', 'reader_batches_upper'),
            ('time_at_price_consumers', 'raw_instrument_batches', 'instrument_batches_upper'),
            ('whole_trade_and_native_consumers', 'raw_instrument_batches', 'instrument_batches_upper'),
            ('event_storage', 'raw_instrument_batches', 'instrument_batches_upper'),
            ('raw_atomic_batch_reduction', 'raw_instrument_batches', 'instrument_batches_upper'),
            ('raw_atomic_counter_updates', 'raw_atomic_parts', 'atomic_parts_per_consumer_upper'),
            ('trade_atomic_consumers', 'trade_atomic_parts', 'atomic_parts_per_consumer_upper'),
            ('quote_atomic_consumers', 'quote_atomic_parts', 'atomic_parts_per_consumer_upper')):
        coefficient(name, [(u, u['scan_cpu_components_disjoint'].get(name, 0.0),
            u['workload_counts'].get(actual, 0)) for u in units], prospective, actual.replace('_', ' '))
    # File-closing and manifest dispatch remainder is explicitly fixed per
    # source window. Large old literal-prefix conversion is separately removed.
    coefficient('scan_dispatch_and_manifest', [(u,
        max(0.0, u['scan_cpu_components_disjoint']['source_decode_and_projection']
            - sum(u['source_manifest']['source_cpu_components'].values()))
            + u['scan_cpu_components_disjoint']['unassigned_scan_routing'],
        len(u['source_manifest']['sources'])) for u in units], 'source_windows', 'one source-window dispatch/manifest')
    coefficient('initialization_and_carry', [(u, u['pipeline_cpu_components']['initialization'],
        len(u['source_manifest']['sources'])) for u in units], 'source_windows', 'one measurement/source/carry initialization')
    coefficient('native_array_allocation', [(u, u['pipeline_cpu_components']['instrument_allocation'],
        u['native_cells']) for u in units], 'instrument_native_cells_upper', 'one allocated native instrument cell')
    coefficient('finalization_and_native_storage', [(u,
        u['pipeline_cpu_components']['finalization_and_native_storage'] - u['native_reference_sample_collection_cpu_seconds'],
        u['native_cells']) for u in units], 'instrument_native_cells_upper', 'one native cell with its final measurement and exact storage')
    coefficient('tail_event_storage', [(u, u['event_storage_finalization_cpu_seconds'],
        len(u['instrument_quality'])) for u in units], 'instrument_window_allocations_upper', 'one final partial event-file set per instrument/window')
    coefficient('exact_measurement_serialization', [(u, u['measurement_json_serialization_cpu_seconds'],
        u['workload_counts']['instrument_atomic_cells']) for u in units], 'instrument_atomic_cells_upper',
        'one instrument atomic cell in the exact compressed measurement report')
    quote_encodings = {u['event_storage']['quotes'].get('encoding') for u in units}
    replay_quotes = quote_encodings == {'raw-source-quote-replay-v1'}
    if 'raw-source-quote-replay-v1' in quote_encodings and not replay_quotes:
        raise IntegrityError('quote storage representations cannot be mixed in one source cost projection')

    def replay_validation_cpu(u):
        value = u.get('quote_replay_validation_cpu_seconds')
        if value is None:
            value = u['event_storage']['quotes'].get('quote_replay_validation_cpu_seconds', 0.0)
        if (type(value) is not int and type(value) is not float) or value < -1e-7:
            raise IntegrityError('quote replay validation CPU must be an explicit non-negative measurement')
        return max(0.0, float(value))

    if replay_quotes:
        batch_items, empty_items = [], []
        for u in units:
            cpu = replay_validation_cpu(u)
            batches = u['source_manifest']['physical_reader_batches']
            windows = len(u['source_manifest']['sources'])
            if batches:
                batch_items.append((u, cpu, batches))
                empty_items.append((u, 0.0, windows))
            else:
                batch_items.append((u, 0.0, 0))
                if cpu > 1e-3 and windows == 0:
                    raise IntegrityError('nonzero quote replay validation has no physical reader batch or source window')
                empty_items.append((u, cpu, windows))
        coefficient('quote_replay_validation', batch_items, 'reader_batches_upper',
            'one required finish replay of recorded logical quotes against the original physical source')
        coefficient('quote_replay_empty_window', empty_items, 'source_windows',
            'one required finish replay of a source window with no physical reader batch')
    # Each quantity enters exactly one term. The old plain JSON comparison,
    # literal event reference, sampled-prefix cache and integrity-only native
    # prefix conversion are retained study-check cost, not extraction work.
    for u in units:
        source = u['source_manifest']['source_cpu_components']
        selected = u['scan_cpu_components_disjoint']
        detail.append({'source_path': u['unit']['source_path'], 'start_ns': u['unit']['event_start_ns'],
            'physical_rows': u['raw_physical_rows'], 'selected_rows': u['counts']['raw_rows'],
            'source_cpu_sum': sum(source.values()),
            'reported_source_dispatch_cpu': selected['source_decode_and_projection'],
            'disjoint_scan_cpu_sum': sum(selected.values()),
            'reported_scan_cpu': u['pipeline_cpu_components']['scan_and_consumers'],
            'plain_json_comparator_excluded_from_extraction': u['plain_json_storage_comparator']['cpu_seconds'],
            'literal_reference_excluded_from_extraction': u['reference_cpu_seconds']})
        if (sum(source.values()) > selected['source_decode_and_projection'] + 1e-5
                or sum(selected.values()) > u['pipeline_cpu_components']['scan_and_consumers'] + 1e-5):
            raise IntegrityError('resource instrumentation counts a source or consumer region twice')

    event_rates = {}
    for kind in ('quotes', 'trades', 'excluded'):
        if kind == 'quotes' and replay_quotes:
            event_rates[kind] = {
                'bytes_per_actual_event_max': None,
                'actual_rows_per_selected_raw_max': max((u['event_storage'][kind]['rows'] / u['counts']['raw_rows']
                                                       for u in units if u['counts']['raw_rows']), default=0),
                'complete_actual_storage_unit_available': True,
                'representation': 'raw-source-quote-replay-v1',
                'quote_parquet_bytes': 0,
                'descriptor_forecast_basis': (
                    'conservative maximum serialized quote-replay descriptor bytes per complete source window; '
                    'not per-quote density; no quote Parquet bytes')}
            continue
        observed = [u for u in units if u['event_storage'][kind]['rows']]
        event_rates[kind] = {
            'bytes_per_actual_event_max': max((u['event_storage'][kind]['serialized_bytes'] / u['event_storage'][kind]['rows']
                                              for u in observed), default=None),
            'actual_rows_per_selected_raw_max': max((u['event_storage'][kind]['rows'] / u['counts']['raw_rows']
                                                   for u in observed), default=0),
            'complete_actual_storage_unit_available': bool(observed)}
    native_byte_rate = max(sum(v['serialized_bytes'] for v in u['native_storage']) / u['native_cells'] for u in units)
    json_byte_rate = max(u['measurement']['size_bytes'] / u['workload_counts']['instrument_atomic_cells'] for u in units)
    # No observed excluded trades means no empirically established excluded
    # output cost. It remains explicitly unresolved, never a zero-byte forecast.
    complete_event_storage_cost = all(r['complete_actual_storage_unit_available'] for r in event_rates.values())

    def physical_parquet_bytes(u):
        total = 0
        for series in u['event_storage'].values():
            if series.get('encoding') == 'raw-source-quote-replay-v1':
                continue
            total += series['serialized_bytes']
        return total + sum(v['serialized_bytes'] for v in u['native_storage'])

    event_storage_cpu_per_byte = max(u['parquet_and_roundtrip_cpu_seconds'] / max(1, physical_parquet_bytes(u))
                                     for u in units)
    max_quote_descriptor = (max(u['event_storage']['quotes']['serialized_bytes'] for u in units)
                            if replay_quotes else None)
    partitions = []
    for value in schedule['partitions']:
        components = {name: rate['cpu_seconds_per_work_unit'] * value[rate['prospective_count_field']]
                      for name, rate in rates.items()}
        # A fixed byte allowance is a resource reserve, not a fitted prevalence
        # for unobserved malformed/snapshot trades. No failure row is dropped
        # when its observed rate differs; actual ceilings still stop the worker.
        components['failure_output_reserve'] = excluded_storage_reserve_bytes_per_source_year * event_storage_cpu_per_byte
        cache = {}
        for name, rate in event_rates.items():
            if name == 'quotes' and replay_quotes:
                cache[name] = max_quote_descriptor * value['source_windows']
            else:
                cache[name] = (None if rate['bytes_per_actual_event_max'] is None else
                    value['selected_raw_rows_upper'] * rate['actual_rows_per_selected_raw_max'] * rate['bytes_per_actual_event_max'])
        native = native_byte_rate * value['instrument_native_cells_upper']
        measurement = json_byte_rate * value['instrument_atomic_cells_upper']
        bytes_measured = sum(v for v in cache.values() if v is not None) + native + measurement
        partitions.append({**value, 'disjoint_source_cpu_components': components,
            'source_cpu_allowance_with_1_5_margin': 1.5 * sum(components.values()),
            'event_cache_bytes_by_kind': cache, 'native_cache_bytes': native, 'exact_measurement_bytes': measurement,
            'measured_storage_allowance_with_1_5_margin': 1.5 * bytes_measured,
            'additional_failure_output_reserve_bytes': excluded_storage_reserve_bytes_per_source_year,
            'total_storage_allowance_with_failure_reserve': 1.5 * bytes_measured + excluded_storage_reserve_bytes_per_source_year})
    maximum_native_arrays = max(w['native_cells_per_instrument'] * (41 + 560 * w['raw_instruments_per_window_upper'])
                                for w in schedule['windows'])
    residual_rss = max(u['peak_process_rss_bytes'] - u['native_array_bytes'] for u in units)
    result = {'kind': 'measured_disjoint_source_workload_projection_v3', 'partitions': partitions,
        'cpu_coefficients': rates, 'instrumentation_reconciliation': detail,
        'event_output_rates': event_rates, 'native_bytes_per_cell_max': native_byte_rate,
        'compressed_json_bytes_per_atomic_cell_max': json_byte_rate,
        'source_pipeline_cpu_allowance': sum(p['source_cpu_allowance_with_1_5_margin'] for p in partitions),
        'source_storage_allowance_including_failure_reserve': sum(
            p['total_storage_allowance_with_failure_reserve'] for p in partitions),
        'all_event_output_populations_measured': complete_event_storage_cost,
        'failure_output_reserve_bytes_per_source_year': excluded_storage_reserve_bytes_per_source_year,
        'failure_output_reserve_is_prevalence_estimate': False,
        'failure_output_cpu_reserve_basis': (
            'maximum observed exact Parquet write/read/hash CPU per serialized byte; separate fixed failure-output allowance'
            if not replay_quotes else
            'maximum observed exact physical Parquet write/read/hash CPU per physical Parquet byte; quote replay descriptor bytes excluded from this denominator; separate fixed failure-output allowance'),
        'maximum_scheduled_instrument_bound_native_array_bytes': maximum_native_arrays,
        'maximum_observed_nonarray_rss_bytes': residual_rss,
        'array_bound_plus_max_observed_other_rss_bytes': maximum_native_arrays + residual_rss,
        'full_extraction_feasibility_established': False, 'complete_study_cpu_or_output_projection': False,
        'pending': ['Full anchor/rolling/causal-structure calculations, annual/date-block statistics and complete target matrices.',
            'Actual fit, calibration, confirmation and final reporting costs; size-based extraction partition packing.'],
        'basis': 'Disjoint actual component CPU times multiplied by corresponding complete source/batch/cadence counts, with 1.5 margin. Maxima are empirical allowances, not theoretical runtime bounds. No whole-window fixed report is scaled by market-event rows.',
        'source_alias_savings_assumed': False, 'economic_independence_from_duplicate_acquisitions_assumed': False}
    if replay_quotes:
        result['quote_replay_descriptor_bytes_per_source_window_max'] = max_quote_descriptor
        result['quote_replay_storage_basis'] = (
            'conservative maximum complete-source-window quote-replay descriptor; no quote Parquet bytes; '
            'production projection counts one required finish replay; later equivalence or downstream rereads '
            'remain charged to the running study stage')
        result['quote_parquet_bytes_in_projection'] = False
    return result
