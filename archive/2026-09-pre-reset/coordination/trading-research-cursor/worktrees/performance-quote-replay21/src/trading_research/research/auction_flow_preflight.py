"""Registered full-window measurement and storage cost, with literal event parity.

The retained ordinary/stressed windows measure the implemented shared source
path. They do not estimate unimplemented annual reporting or fitted models.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time as civil_time, timezone
from fractions import Fraction
import hashlib
import math
from pathlib import Path
import resource
import time

from trading_research.data.book import BookReducer
from trading_research.data.events import Flags, LatencyScenario, SourceAddress, normalize_mbp
from trading_research.data.reconcile import select_groups
from trading_research.errors import ContractError, IntegrityError
from trading_research.foundations.calendar import local_timestamp
from trading_research.foundations.cash_calendar import CashCalendar
from trading_research.measurements.quotes import transition_metrics
from trading_research.operations.artifacts import digest
from trading_research.research.auction_flow_coordinates import RetainedCoordinateIndex
from trading_research.research.auction_flow_data import RAW_FIELDS
from trading_research.research.auction_flow_pipeline import measure_raw_window
from trading_research.research.auction_flow_quote_replay import QuoteReplaySeries
from trading_research.research.auction_flow_storage import ParquetSeries, read_json_artifact
from trading_research.research.auction_flow_parity import compare_series
from trading_research.research.auction_flow_schedule import source_instrument_inventory, plan_source_windows
from trading_research.research.auction_flow_resources import source_cost_projection


VERSION = 'auction-flow-complete-window-source-preflight-v1'
NATIVE_WIDTH_NS = 100_000_000
REFERENCE_ROWS = 32768


class SourcePrefix:
    def __init__(self, *, start, end):
        self.start, self.end = start, end
        self.rows = self.total = 0
        self.parts, self.sources = [], {}

    def add(self, table, source):
        import pyarrow as pa

        self.total += len(table)
        self.sources[source['source_key']] = source
        amount = min(REFERENCE_ROWS - self.rows, len(table))
        if amount:
            part = table.slice(0, amount)
            self.parts.append(part.append_column('source_key', pa.array([source['source_key']] * amount)))
            self.rows += amount

    @property
    def end_at(self):
        if self.total <= REFERENCE_ROWS:
            return self.end
        return self.start + ((self.parts[-1]['t'][-1].as_py() - self.start) // NATIVE_WIDTH_NS) * NATIVE_WIDTH_NS

    def table(self):
        import pyarrow as pa
        return None if not self.parts else pa.concat_tables(self.parts).combine_chunks()


def literal_native_prefix(prefix, observed):
    """Replay actual addressed raw events with the independent typed reducer.

    Comparison closes only whole 100 ms cells inside the retained prefix. It
    includes original multiplicity, true paths and literal elapsed exposure.
    """
    end = prefix.end_at
    if end <= prefix.start or not prefix.parts:
        raise IntegrityError('declared real-data parity prefix contains no complete native cell')
    count = (end - prefix.start) // NATIVE_WIDTH_NS
    cells = {}
    def cell(instrument, number):
        key = (instrument, number)
        if key not in cells:
            value = {name: 0 for name in ('quote_rows', 'fresh_quotes', 'pressure_transitions',
                'ofi_close', 'ofi_high', 'ofi_low', 'same_price_ofi', 'price_change_ofi', 'standing_ns', 'priced_prints')}
            value.update({name: -1 for name in ('ofi_high_at_ns', 'ofi_low_at_ns', 'ofi_high_source_order',
                'ofi_low_source_order', 'first_trade_at_ns', 'last_trade_at_ns', 'high_price_at_ns',
                'low_price_at_ns', 'first_trade_source_order', 'last_trade_source_order',
                'high_price_source_order', 'low_price_source_order')})
            value.update({name: 0 for name in ('first_price_ticks', 'last_price_ticks', 'high_price_ticks', 'low_price_ticks')})
            for cohort in ('all', 'ny_ge100', 'london_ge75', 'inclusive30_through60'):
                for field in ('volume', 'unknown', 'prints', 'close', 'high', 'low'):
                    value[cohort + '__' + field] = 0
                for field in ('high_at_ns', 'low_at_ns', 'high_source_order', 'low_source_order'):
                    value[cohort + '__' + field] = -1
            value['imbalance_terms'] = []
            value['spread_mass'] = 0
            cells[key] = value
        return cells[key]

    def tick(value):
        if value is None:
            return None
        scaled = Fraction(value) * 4
        return int(scaled) if scaled.denominator == 1 and 0 < scaled < 2**53 else None

    def common_quote(state):
        q = state.quote if state and state.trusted else None
        return bool(q and q.valid and tick(q.bid) is not None and tick(q.ask) is not None
                    and q.bid_size < 2**32 - 1 and q.ask_size < 2**32 - 1)

    def path(value, prefix_name, increment, at, order):
        value[prefix_name + 'close'] += increment
        for field, better in (('high', value[prefix_name + 'close'] > value[prefix_name + 'high']),
                              ('low', value[prefix_name + 'close'] < value[prefix_name + 'low'])):
            if better:
                value[prefix_name + field] = value[prefix_name + 'close']
                value[prefix_name + field + '_at_ns'] = at
                value[prefix_name + field + '_source_order'] = order

    def exposure(instrument, state, a, b):
        b = min(b, end)
        if not common_quote(state) or state.economic_quote_at is None:
            return
        q = state.quote
        while a < b:
            number = (a - prefix.start) // NATIVE_WIDTH_NS
            terminal = min(b, prefix.start + (number + 1) * NATIVE_WIDTH_NS)
            duration = terminal - a
            value = cell(instrument, number)
            value['standing_ns'] += duration
            value['imbalance_terms'].append(float(duration * Fraction(q.bid_size - q.ask_size, q.bid_size + q.ask_size)))
            value['spread_mass'] += duration * (tick(q.ask) - tick(q.bid))
            a = terminal

    reducer, last, events = BookReducer(), {}, 0
    table = prefix.table()
    for row in table.to_pylist():
        at = row['t']
        if at >= end:
            break
        source = prefix.sources[row['source_key']]
        address = SourceAddress(source['dataset'], source['metadata_version'], source['path'],
            source['metadata_version'], 'physical_file', row['source_row'], 'retained-eleven-field-MBP-export')
        event = normalize_mbp({name: row[name] for name in RAW_FIELDS}, address, native=False,
            scenario=LatencyScenario('retained-event-plus-250ms', 'event', 250_000_000, 0))
        instrument, number = event.instrument_id, (at - prefix.start) // NATIVE_WIDTH_NS
        value = cell(instrument, number)
        exposure(instrument, reducer.states.get(instrument), last.get(instrument, prefix.start), at)
        tr = reducer.apply(event)
        if tr.duplicate:
            raise IntegrityError('actual reference prefix contains a repeated physical address')
        order = row['source_order']
        if event.trade_eligible:
            quantity, sign = event.size, event.aggressor or 0
            for cohort, included in (('all', True), ('ny_ge100', quantity >= 100),
                    ('london_ge75', quantity >= 75), ('inclusive30_through60', 30 <= quantity <= 60)):
                if included:
                    value[cohort + '__volume'] += quantity
                    value[cohort + '__unknown'] += quantity if sign == 0 else 0
                    value[cohort + '__prints'] += 1
                    path(value, cohort + '__', quantity * sign, at, order)
            price = tick(event.price)
            if value['all__prints'] == 1:
                value.update(first_price_ticks=price or 0, first_trade_at_ns=at, first_trade_source_order=order)
            value.update(last_price_ticks=price or 0, last_trade_at_ns=at, last_trade_source_order=order)
            if price is not None:
                for field, better in (('high', not value['priced_prints'] or price > value['high_price_ticks']),
                                      ('low', not value['priced_prints'] or price < value['low_price_ticks'])):
                    if better:
                        value[field + '_price_ticks'] = price
                        value[field + '_price_at_ns'] = at
                        value[field + '_price_source_order'] = order
                value['priced_prints'] += 1
        update = event.action in ('A', 'M', 'C')
        invalidation = bool(event.flags & Flags.MAYBE_BAD_BOOK) or event.action in ('R', None)
        value['quote_rows'] += int(update or invalidation)
        fresh = update and common_quote(tr.after) and not (event.flags & (Flags.SNAPSHOT | Flags.MAYBE_BAD_BOOK))
        value['fresh_quotes'] += int(fresh)
        pressure = transition_metrics(event, tr) if fresh and common_quote(tr.before) else None
        if pressure is not None:
            previous, current = tr.before.quote, tr.after.quote
            same = (current.bid_size - previous.bid_size if current.bid == previous.bid else 0)
            same -= current.ask_size - previous.ask_size if current.ask == previous.ask else 0
            value['pressure_transitions'] += 1
            value['same_price_ofi'] += same
            value['price_change_ofi'] += pressure.ofi_contracts - same
            path(value, 'ofi_', pressure.ofi_contracts, at, order)
        last[instrument] = at
        events += 1
    for instrument, state in reducer.states.items():
        exposure(instrument, state, last[instrument], end)
    if not set(reducer.states) <= set(observed):
        raise IntegrityError('native prefix omitted an actually observed raw instrument')
    compared, floating, maximum_error = 0, 0, 0.0
    for instrument, rows in observed.items():
        if len(rows) != count:
            raise IntegrityError('native reference population differs from its completed cell prefix')
        for number, emitted in enumerate(rows):
            expected = cell(instrument, number)
            for name, value in expected.items():
                if name not in ('imbalance_terms', 'spread_mass'):
                    if emitted[name] != value:
                        raise IntegrityError(f'actual native reference mismatch: instrument={instrument}, cell={number}, field={name}, expected={value}, got={emitted[name]}')
                    compared += 1
            for name, value in (('duration_imbalance_ns', math.fsum(expected['imbalance_terms'])),
                                ('duration_spread_ticks_ns', expected['spread_mass'])):
                difference = abs(emitted[name] - value)
                maximum_error = max(maximum_error, difference)
                if not math.isclose(emitted[name], value, rel_tol=1e-12, abs_tol=1e-6):
                    raise IntegrityError('actual native quote integral differs from literal elapsed intervals')
                floating += 1
    return {'passed': True, 'raw_events': events, 'complete_cells_per_instrument': count,
            'end_ns': end, 'exact_field_comparisons': compared, 'floating_field_comparisons': floating,
            'maximum_float_absolute_error': maximum_error, 'float_relative_tolerance': 1e-12,
            'float_absolute_tolerance': 1e-6, 'source_order_scenario': True,
            'exchange_order_or_receipt_certified': False}


def resource_windows(protocol, index, calendar):
    result = []
    for cohort in protocol['resource_cohorts']:
        if 'cash_date' in cohort:
            day = date.fromisoformat(cohort['cash_date'])
            cash = calendar.resolve(day, cut=local_timestamp(day, civil_time(9), 'America/New_York'))
            if cash.state == 'closed':
                raise IntegrityError('fixed actual cash-day resource cohort is not an available cash session')
            start, end, calendar_version = cash.open_at, cash.close_at, cash.version
        else:
            start, end = (int(datetime.fromisoformat(cohort[key]).timestamp()) * 10**9
                          for key in ('start_local', 'end_local'))
            calendar_version = None
        dataset = f"quantpad/cme__{cohort['root'].lower()}-continuous-futures__mbp-1"
        selection, _ = select_groups(index, dataset=dataset, start=start, end=end,
                                    max_scan_rows=protocol['resources']['maximum_source_day_scan_rows'])
        if not selection:
            raise IntegrityError('declared cost cohort has no acquired source; cannot silently substitute another date')
        for record, groups in selection:
            result.append({'root': cohort['root'], 'role': cohort['role'], 'cash_date': cohort.get('cash_date'),
                'event_start_ns': start, 'event_end_ns': end, 'source_path': record['path'],
                'source_metadata_version': digest(record), 'source_groups': groups,
                'calendar_version': calendar_version,
                'source_variant': hashlib.sha256(record['path'].encode()).hexdigest()[:12],
                'coverage_basis': 'separately observed acquired source; overlapping acquisitions are not concatenated'})
    return result


def measured_unit(unit, *, protocol, index, coordinates, outputs, data_root, storage_encoding='structural',
                  anchor_calendar=None, cohort_contract=None, diagnostic_profiler=None, quote_storage='parquet'):
    import pyarrow.compute as pc

    if quote_storage not in ('parquet', 'replay'):
        raise ContractError("quote_storage must be 'parquet' or 'replay'")
    started = time.process_time()
    name = f"{unit['root']}-{unit['event_start_ns']}-{unit['source_variant']}"
    events = {kind: ParquetSeries(outputs, f'{name}-{kind}', encoding=storage_encoding) for kind in ('trades', 'quotes', 'excluded')}
    if quote_storage == 'replay':
        events['quotes'] = QuoteReplaySeries(
            outputs, f'{name}-quotes', data_root=data_root,
            source_index_reference=protocol['source_index'], root=unit['root'],
            start_ns=unit['event_start_ns'], end_ns=unit['event_end_ns'],
            source_paths=(unit['source_path'],),
            maximum_scan_rows=protocol['resources']['maximum_source_day_scan_rows'],
            continuation=None)
    prefix = SourcePrefix(start=unit['event_start_ns'], end=unit['event_end_ns'])
    native_prefix, native_storage = {}, []
    byte_start = outputs.written
    native_prefix_cpu = 0.0
    def native(table, metadata):
        nonlocal native_prefix_cpu
        sampled = time.process_time()
        native_prefix[metadata['instrument_id']] = table.filter(pc.less_equal(table['event_end_ns'], prefix.end_at)).to_pylist()
        native_prefix_cpu += time.process_time() - sampled
        series = ParquetSeries(outputs, f"{name}-native-{metadata['instrument_id']}", encoding=storage_encoding)
        series.append(table)
        result = series.finish()
        native_storage.append(result)
        return result
    try:
        if diagnostic_profiler is not None:
            diagnostic_profiler.enable()
        measured = measure_raw_window(data_root=data_root, index=index, coordinates=coordinates, root=unit['root'],
            start_ns=unit['event_start_ns'], end_ns=unit['event_end_ns'],
            source_paths=(unit['source_path'],),
            maximum_scan_rows=protocol['resources']['maximum_source_day_scan_rows'],
            native_width_ns=protocol['native_width_ns'], atomic_width_ns=protocol['atomic_width_ns'],
            maximum_native_array_bytes=protocol['resources']['maximum_native_array_bytes'],
            retain_trade_batch=events['trades'].append, retain_quote_batch=events['quotes'].append,
            retain_excluded_batch=events['excluded'].append, retain_native_table=native,
            inspect_raw_batch=prefix.add)
        tail_started = time.process_time()
        storage = {}
        for kind, series in events.items():
            if quote_storage == 'replay' and kind == 'quotes':
                storage[kind] = series.finish(measured['source_manifest'])
            else:
                storage[kind] = series.finish()
        event_storage_finalization_cpu = time.process_time() - tail_started
        replay_validation_cpu = storage['quotes'].get('quote_replay_validation_cpu_seconds', 0.0) if quote_storage == 'replay' else 0.0
        event_storage_finalization_cpu = max(0.0, event_storage_finalization_cpu - replay_validation_cpu)
    except BaseException:
        for series in events.values():
            if not series.closed:
                series.abort()
        raise
    finally:
        if diagnostic_profiler is not None:
            diagnostic_profiler.disable()
    measured_cpu = time.process_time() - started
    original = prefix.table()
    sample_storage = ParquetSeries(outputs, name + '-actual-reference-prefix')
    if original is not None:
        sample_storage.append(original)
    sample_ref = sample_storage.finish()
    parity_start = time.process_time()
    parity = literal_native_prefix(prefix, native_prefix)
    parity_cpu = time.process_time() - parity_start
    counts = measured['source_manifest']['projection']['counts']
    if (storage['trades']['rows'] != counts['trades'] or storage['quotes']['rows'] != counts['quote_rows']
            or storage['excluded']['rows'] != measured['source_manifest']['trade_exclusions'].get('unique_excluded_trade_rows', 0)):
        raise IntegrityError('complete source scan and retained event-cache populations differ')
    serialization_start = time.process_time()
    baseline_measurement = outputs.json(name + '-measurements.json', measured, kind='auction_flow_plain_json_storage_comparator')
    plain_serialization_cpu = time.process_time() - serialization_start
    measurement_ref = outputs.json_compressed(name + '-measurements.json.zst', measured,
        kind='auction_flow_full_window_measurements', measurement_fast_path=True)
    serialization_cpu = measurement_ref['cpu_seconds']
    storage_cpu = sum(r['cpu_seconds'] for r in [*storage.values(), *native_storage])
    anchor_check = None
    if anchor_calendar is not None:
        from trading_research.research.auction_flow_anchor_preflight import check_anchor_unit
        anchor_check = check_anchor_unit(measured, unit, measurement_reference=measurement_ref,
            trade_storage=storage['trades'], calendar=anchor_calendar, outputs=outputs)
    cohort_check = None
    if cohort_contract is not None:
        from trading_research.research.auction_flow_cohort_preflight import check_cohort_unit
        cohort_check = check_cohort_unit(measured, unit, measurement_reference=measurement_ref,
            trade_storage=storage['trades'], outputs=outputs, contract=cohort_contract)
    result = {'unit': unit, 'measurement': measurement_ref, 'event_storage': storage,
        'native_storage': native_storage, 'actual_reference_prefix': sample_ref, 'actual_reference': parity,
        'source_manifest': measured['source_manifest'],
        'raw_physical_rows': measured['source_manifest']['physical_scan_rows'], 'counts': counts,
        'pipeline_cpu_seconds_including_event_storage': measured_cpu,
        'pipeline_cpu_components': measured['pipeline_cpu_components'],
        'scan_cpu_components_disjoint': measured['scan_cpu_components_disjoint'],
        'workload_counts': measured['workload_counts'],
        'native_reference_sample_collection_cpu_seconds': native_prefix_cpu,
        'event_storage_finalization_cpu_seconds': event_storage_finalization_cpu,
        'quote_replay_validation_cpu_seconds': replay_validation_cpu,
        'parquet_and_roundtrip_cpu_seconds': storage_cpu,
        'measurement_json_serialization_cpu_seconds': serialization_cpu,
        'plain_json_storage_comparator': {**baseline_measurement, 'cpu_seconds': plain_serialization_cpu},
        'storage_encoding': storage_encoding,
        'actual_anchor_composition_check': anchor_check,
        'actual_cohort_validation': cohort_check,
        'reference_cpu_seconds': parity_cpu,
        'measurement_and_cache_bytes': storage['trades']['serialized_bytes'] + storage['quotes']['serialized_bytes']
            + storage['excluded']['serialized_bytes'] + sum(r['serialized_bytes'] for r in native_storage) + measurement_ref['size_bytes'],
        'all_unit_derived_bytes_before_unit_report': outputs.written - byte_start,
        'native_cells': sum(r['rows'] for r in native_storage),
        'native_array_bytes': measured['native_allocated_array_bytes'],
        'peak_process_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        'instrument_quality': [{ 'instrument_id': i['instrument_id'],
            'coordinate': i['coordinate'], 'whole_flow_complete': i['whole_window']['flow_history_complete'],
            'whole_price_complete': i['whole_window']['price_history_complete'],
            'native_quality': i['native_event_measurements']['quality_counts']} for i in measured['instruments']],
        'role': 'source_pipeline_cost_and_integrity_only', 'family_statistics_or_model_complete': False}
    reference = outputs.json(name + '-resource-unit.json', result, kind='auction_flow_source_resource_unit')
    label = 'AUCTION_FLOW_FIXTURE_UNIT' if unit.get('role') == 'fixture' else 'AUCTION_FLOW_RESOURCE_UNIT'
    print(f"{label} {reference['path']}", flush=True)
    return result, reference


def partition_parity(full, *, protocol, index, coordinates, outputs, data_root, quote_storage='parquet'):
    if quote_storage not in ('parquet', 'replay'):
        raise ContractError("quote_storage must be 'parquet' or 'replay'")
    unit = full['unit']
    start, end = unit['event_start_ns'], unit['event_end_ns']
    day = 86_400_000_000_000
    cut = (start // day + 1) * day
    if not start < cut < end:
        cut = start + ((end - start) // 2 // protocol['atomic_width_ns']) * protocol['atomic_width_ns']
    if not start < cut < end:
        raise ContractError('registered continuation unit lacks an internal aligned source cut')
    started, byte_start = time.process_time(), outputs.written
    parts, continuation, source_carry = [], None, None
    prefix = f"{unit['root']}-{start}-{unit['source_variant']}-partition"
    for number, (a, b) in enumerate(((start, cut), (cut, end))):
        events = {kind: ParquetSeries(outputs, f'{prefix}-{number}-{kind}', encoding='structural')
                  for kind in ('trades', 'quotes', 'excluded')}
        if quote_storage == 'replay':
            events['quotes'] = QuoteReplaySeries(
                outputs, f'{prefix}-{number}-quotes', data_root=data_root,
                source_index_reference=protocol['source_index'], root=unit['root'],
                start_ns=a, end_ns=b, source_paths=(unit['source_path'],),
                maximum_scan_rows=protocol['resources']['maximum_source_day_scan_rows'],
                continuation=source_carry)
        natives = []
        def retain_native(table, metadata):
            store = ParquetSeries(outputs, f"{prefix}-{number}-native-{metadata['instrument_id']}", encoding='structural')
            store.append(table)
            result = store.finish()
            natives.append({'instrument_id': metadata['instrument_id'], 'storage': result})
            return result
        try:
            measured = measure_raw_window(data_root=data_root, index=index, coordinates=coordinates, root=unit['root'],
                start_ns=a, end_ns=b, source_paths=(unit['source_path'],), continuation=continuation,
                maximum_scan_rows=protocol['resources']['maximum_source_day_scan_rows'],
                native_width_ns=protocol['native_width_ns'], atomic_width_ns=protocol['atomic_width_ns'],
                maximum_native_array_bytes=protocol['resources']['maximum_native_array_bytes'],
                retain_trade_batch=events['trades'].append, retain_quote_batch=events['quotes'].append,
                retain_excluded_batch=events['excluded'].append, retain_native_table=retain_native)
            stores = {}
            for kind, series in events.items():
                if quote_storage == 'replay' and kind == 'quotes':
                    stores[kind] = series.finish(measured['source_manifest'])
                else:
                    stores[kind] = series.finish()
        except BaseException:
            for series in events.values():
                if not series.closed:
                    series.abort()
            raise
        source_carry = measured['source_manifest']['source_continuation']
        continuation = measured['measurement_continuation']
        measurement = outputs.json_compressed(f'{prefix}-{number}-measurements.json.zst', measured,
                                              kind='auction_flow_continuation_partition_measurements', measurement_fast_path=True)
        parts.append({'start_ns': a, 'end_ns': b, 'measurement': measurement, 'event_storage': stores,
                      'native_storage': natives, 'carry_sha256': continuation['sha256']})
        del measured
    comparisons = {kind: compare_series([full['event_storage'][kind]], [p['event_storage'][kind] for p in parts])
                   for kind in ('trades', 'quotes', 'excluded')}
    full_measurement = read_json_artifact(full['measurement'])
    for instrument in full_measurement['instruments']:
        raw_id = instrument['instrument_id']
        expected = [instrument['native_event_measurements']['retained_artifact']]
        observed = [r['storage'] for p in parts for r in p['native_storage'] if r['instrument_id'] == raw_id]
        comparisons[f'native-{raw_id}'] = compare_series(expected, observed, float_tolerances=(1e-6, 1e-12))
    result = {'version': 'auction-flow-complete-source-continuation-parity-v1', 'unit': unit,
        'cut_ns': cut, 'parts': parts, 'comparisons': comparisons,
        'cpu_seconds': time.process_time() - started, 'output_bytes_before_report': outputs.written - byte_start,
        'passed': True, 'source_partitions_are_scientific_formation_anchors': False,
        'book_recovery_from_partition_cut': False,
        'role': 'complete market-window continuity/storage verification; no statistical independence or quality claim'}
    reference = outputs.json(f'{prefix}-parity.json', result, kind='auction_flow_actual_continuation_parity')
    print(f'AUCTION_FLOW_CONTINUATION_UNIT {reference["path"]}', flush=True)
    return reference


def compare_prior_values(results, references, prior, *, outputs, load_reference):
    if prior.get('success') is not True or prior.get('source_component_verified') is not True:
        raise IntegrityError('source-value reuse requires its retained successful complete component check')
    saved = {}
    for reference in prior['actual_source_preflight']['resource_units']:
        value = load_reference(reference)
        unit = value['unit']
        saved[(unit['root'], unit['source_path'], unit['event_start_ns'], unit['event_end_ns'])] = (value, reference)
    matches = []
    for current, reference in zip(results, references, strict=True):
        unit = current['unit']
        key = (unit['root'], unit['source_path'], unit['event_start_ns'], unit['event_end_ns'])
        if key not in saved:
            raise IntegrityError('current source cohort has no matching prior complete value population')
        old, previous = saved[key]
        if (current['counts'] != old['counts'] or current['source_manifest']['canonical_selected_raw_stream']
                != old['source_manifest']['canonical_selected_raw_stream']):
            raise IntegrityError('current source projection or original all-field stream differs from its retained check')
        comparisons = {kind: compare_series([old['event_storage'][kind]], [current['event_storage'][kind]])
                       for kind in ('trades', 'quotes', 'excluded')}
        comparisons['native'] = compare_series(old['native_storage'], current['native_storage'], float_tolerances=(1e-6, 1e-12))
        old_measurement, new_measurement = read_json_artifact(old['measurement']), read_json_artifact(current['measurement'])
        semantic_fields = ('whole_window', 'atomic_windows', 'time_at_price', 'coordinate', 'instrument_id')
        logical_old = [{k: i[k] for k in semantic_fields} for i in old_measurement['instruments']]
        logical_new = [{k: i[k] for k in semantic_fields} for i in new_measurement['instruments']]
        measurement_sha = digest(logical_new)
        if digest(logical_old) != measurement_sha or old_measurement['measurement_continuation'] != new_measurement['measurement_continuation']:
            raise IntegrityError('complete original atomic/whole/TPO/coverage/coordinate or continuation values changed')
        del old_measurement, new_measurement, logical_old, logical_new
        if current['measurement']['uncompressed_sha256'] != current['plain_json_storage_comparator']['sha256']:
            raise IntegrityError('plain and compressed measurement storage candidates did not serialize identical canonical bytes')
        matches.append({'unit': unit, 'previous_resource_unit': previous, 'current_resource_unit': reference,
            'all_original_source_fields_equal': True, 'comparisons': comparisons,
            'complete_semantic_measurement_fields_equal': semantic_fields,
            'complete_semantic_measurement_sha256': measurement_sha, 'complete_measurement_continuation_equal': True,
            'previous_event_and_native_bytes': sum(v['serialized_bytes'] for v in [*old['event_storage'].values(), *old['native_storage']]),
            'current_event_and_native_bytes': sum(v['serialized_bytes'] for v in [*current['event_storage'].values(), *current['native_storage']]),
            'current_exact_plain_json_bytes': current['plain_json_storage_comparator']['size_bytes'],
            'current_exact_compressed_json_bytes': current['measurement']['size_bytes']})
    return outputs.json('retained-source-value-reuse-comparison.json',
        {'kind': 'auction_flow_complete_retained_value_comparison_v1', 'passed': True, 'matches': matches,
         'prior_attempt_id': prior['attempt_id'], 'prior_outputs_modified': False},
        kind='auction_flow_retained_value_reuse_comparison')


def run_measured_units(windows, *, protocol, index, coordinates, outputs, data_root, calendar,
                       unit_executor=None, cohort_contract=None):
    """Run each complete source window, sequentially unless a runner executor is supplied."""
    if unit_executor is None:
        results, refs = [], []
        for unit in windows:
            result, reference = measured_unit(unit, protocol=protocol, index=index,
                coordinates=coordinates[unit['root']], outputs=outputs, data_root=data_root,
                storage_encoding='structural', anchor_calendar=calendar, cohort_contract=cohort_contract)
            results.append(result)
            refs.append(reference)
        return results, refs
    results, refs = unit_executor(windows, protocol=protocol, index=index, coordinates=coordinates,
                                  outputs=outputs, data_root=data_root, calendar=calendar,
                                  cohort_contract=cohort_contract)
    if (not isinstance(results, list) or not isinstance(refs, list)
            or len(results) != len(windows) or len(refs) != len(windows)):
        raise IntegrityError('source unit executor changed the complete unit population')
    for result, reference, unit in zip(results, refs, windows, strict=True):
        if result is None or reference is None:
            raise IntegrityError('source unit executor counted a skipped or failed unit as a result')
        if result.get('unit') != unit:
            raise IntegrityError('source unit executor changed unit identity or order')
    return results, refs


def run_preflight(*, protocol, root, outputs, load_reference, check_extension, unit_executor=None):
    """Complete source units, then retained-value, continuation, inventory and schedule.

    Ordinary callers keep the sequential in-process default. The registered
    runner may pass an executor for the independent full source-window units.
    """
    index = load_reference(protocol['source_index'])
    previous = load_reference(check_extension['prior_accepted_worker'])
    receipt = load_reference(check_extension['prior_accepted_execution'])
    if (receipt.get('success') is not True or receipt.get('within_declared_limits') is not True
            or receipt.get('worker_identity_joined') is not True or receipt.get('exit_code') != 0
            or receipt.get('attempt_id') != previous.get('attempt_id')
            or receipt.get('protocol_sha256') != check_extension['parent_protocol_sha256']
            or previous.get('protocol_sha256') != receipt['protocol_sha256']
            or receipt.get('worker_report_path') != check_extension['prior_accepted_worker']['path']):
        raise IntegrityError('retained source-value comparison lacks its successful bounded supervisor receipt')
    calendar = CashCalendar(Path(protocol['cash_calendar']['path']))
    coordinates = {}
    for symbol, reference in protocol['coordinate_admissions'].items():
        coordinates[symbol] = RetainedCoordinateIndex(load_reference(reference), source_version=reference['sha256'],
            snapshot_supplement=load_reference(protocol['nq_snapshot_supplement']) if symbol == 'NQ' else None,
            snapshot_version=protocol['nq_snapshot_supplement']['sha256'] if symbol == 'NQ' else None)
    windows = resource_windows(protocol, index, calendar)
    results, refs = run_measured_units(windows, protocol=protocol, index=index, coordinates=coordinates,
        outputs=outputs, data_root=root.parent / 'data', calendar=calendar, unit_executor=unit_executor,
        cohort_contract=check_extension.get('cohort_validation'))
    cohorts = [result.get('actual_cohort_validation') for result in results]
    if check_extension.get('cohort_validation') is not None and (
            not cohorts or any(not row or row.get('passed') is not True for row in cohorts)):
        raise IntegrityError('declared full-unit cohort validation was skipped or failed')
    comparison = compare_prior_values(results, refs, previous, outputs=outputs, load_reference=load_reference)
    continuation = []
    for result in results:
        unit = result['unit']
        if (unit['role'] == 'full_observed_futures_clock_cost'
                or unit['root'] == 'NQ' and unit['role'] == 'ordinary_pipeline_cost'):
            continuation.append(partition_parity(result, protocol=protocol, index=index,
                coordinates=coordinates[unit['root']], outputs=outputs, data_root=root.parent / 'data'))
    inventory = source_instrument_inventory(protocol, index, root.parent / 'data',
        maximum_decoded_identity_rows=check_extension['maximum_additional_identity_column_rows'])
    inventory_ref = outputs.json('complete-source-instrument-inventory.json', inventory, kind='auction_flow_source_identity_inventory')
    schedule = plan_source_windows(protocol, index, instrument_inventory=inventory)
    schedule_ref = outputs.json_compressed('complete-physical-source-day-schedule.json.zst', schedule,
                                           kind='auction_flow_complete_physical_source_schedule')
    projection = source_cost_projection(results, protocol, schedule,
        excluded_storage_reserve_bytes_per_source_year=check_extension['excluded_output_reserve_bytes_per_root_year'])
    groups = defaultdict(list)
    for result in results:
        u = result['unit']
        groups[(u['root'], u['event_start_ns'], u['event_end_ns'])].append(result)
    overlaps = []
    for (symbol, start, end), variants in groups.items():
        if len(variants) > 1:
            overlaps.append({'root': symbol, 'start_ns': start, 'end_ns': end,
                'variants': [{'source_path': r['unit']['source_path'],
                    'raw_stream': r['source_manifest']['canonical_selected_raw_stream'],
                    'counts': r['counts'], 'measurement': r['measurement']} for r in variants],
                'ordered_all_eleven_fields_equal': len({digest(r['source_manifest']['canonical_selected_raw_stream']) for r in variants}) == 1,
                'deduplication_or_source_supersession_claim': False})
    return {'version': VERSION, 'passed': True, 'resource_units': refs,
        'observed_source_overlap_comparisons': overlaps,
        'source_cost_projection': projection,
        'actual_continuation_parity_units': continuation,
        'actual_cohort_validation_units': cohorts,
        'complete_retained_source_value_comparison': comparison,
        'complete_instrument_inventory': inventory_ref, 'complete_source_schedule': schedule_ref,
        'resource_probe_only': True, 'complete_family_statistics': False,
        'actual_model_fits': 0, 'actual_location_quality_evaluations': 0}
