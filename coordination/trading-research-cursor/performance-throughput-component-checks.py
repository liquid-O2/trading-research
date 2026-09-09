        source, scan, pipe = result['source_manifest']['source_cpu_components'], result['scan_cpu_components_disjoint'], result['pipeline_cpu_components']
        quotes = result['event_storage']['quotes']
        actual_components = {name: source[name] for name in ('source_metadata_and_open', 'physical_batch_decode', 'physical_address_and_selection', 'selected_projection')}
        actual_components.update({name: scan[name] for name in ('native_source_ownership', 'time_at_price_consumers', 'whole_trade_and_native_consumers', 'event_storage', 'raw_atomic_batch_reduction', 'raw_atomic_counter_updates', 'trade_atomic_consumers', 'quote_atomic_consumers')})
        replay = result['quote_replay_validation_cpu_seconds']
        fixed_replay = quotes['quote_replay_metadata_cpu_seconds'] if result['source_manifest']['physical_reader_batches'] else replay
        actual_components.update(scan_dispatch_and_manifest=max(0.0, scan['source_decode_and_projection'] - sum(source.values())) + scan['unassigned_scan_routing'],
            initialization_and_carry=pipe['initialization'], native_array_allocation=pipe['instrument_allocation'],
            finalization_and_native_storage=pipe['finalization_and_native_storage'] - result['native_reference_sample_collection_cpu_seconds'],
            tail_event_storage=result['event_storage_finalization_cpu_seconds'], exact_measurement_serialization=result['measurement_json_serialization_cpu_seconds'],
            quote_replay_validation=max(0.0, replay - fixed_replay), quote_replay_metadata_and_dispatch=fixed_replay)
        component_allowances = {name: 1.5 * rate['cpu_seconds_per_work_unit'] * prospective[rate['prospective_count_field']] for name, rate in rates.items()}
        component_checks = {name: {'actual_cpu_seconds': value, 'allowance_cpu_seconds': component_allowances[name], 'passed': value <= component_allowances[name]}
            for name, value in actual_components.items()}
        # This separately frozen empirical envelope models both slice overhead
        # and quote-row work; it does not alter calculation or coverage scope.
        envelope = extension['quote_cost_envelope']
        quote_allowance = 1.5 * (envelope['cpu_seconds_per_slice'] * prospective['atomic_parts_per_consumer_upper']
            + envelope['cpu_seconds_per_quote_row'] * prospective['selected_raw_rows_upper'])
        component_checks['quote_atomic_dual_count_envelope'] = {'actual_cpu_seconds': scan['quote_atomic_consumers'],
            'allowance_cpu_seconds': quote_allowance, 'passed': scan['quote_atomic_consumers'] <= quote_allowance}
        quote_adjusted_allowance = allowance - component_allowances['quote_atomic_consumers'] + quote_allowance
        workload = result['workload_counts']
        observed_ids = {row['instrument_id'] for row in result['instrument_quality']}
        additional_bounds = (result['counts']['raw_rows'] <= prospective['selected_raw_rows_upper']
            and workload['raw_instrument_batches'] <= prospective['instrument_batches_upper']
            and workload['instrument_atomic_cells'] <= prospective['instrument_atomic_cells_upper']
            and observed_ids <= set(counts['raw_instrument_allocation_ids_upper'])
            and all(workload[key] <= prospective['atomic_parts_per_consumer_upper'] for key in ('raw_atomic_parts', 'quote_atomic_parts', 'trade_atomic_parts')))
        if not additional_bounds:
            raise ValueError('held-out source consumer population exceeds its frozen count bounds')
        output_pairs = {
            'native': (sum(x['serialized_bytes'] for x in result['native_storage']), 1.5 * frozen['native_bytes_per_cell_max'] * prospective['instrument_native_cells_upper']),
            'measurement': (result['measurement']['size_bytes'], 1.5 * frozen['compressed_json_bytes_per_atomic_cell_max'] * prospective['instrument_atomic_cells_upper']),
            'quote_descriptor': (quotes['serialized_bytes'], 1.5 * frozen['quote_replay_descriptor_bytes_per_source_window_max'])}
        for kind in ('trades', 'excluded'):
            rate = frozen['event_output_rates'][kind]
            output_pairs[kind] = (result['event_storage'][kind]['serialized_bytes'], None if rate['bytes_per_actual_event_max'] is None else
                1.5 * prospective['selected_raw_rows_upper'] * rate['actual_rows_per_selected_raw_max'] * rate['bytes_per_actual_event_max'])
        output_checks = {name: {'actual_bytes': pair[0], 'allowance_bytes': pair[1], 'passed': None if pair[1] is None else pair[0] <= pair[1]}
            for name, pair in output_pairs.items()}
        comparisons[-1].update(component_checks=component_checks, output_checks=output_checks,
            quote_adjusted_source_allowance_cpu_seconds=quote_adjusted_allowance,
            within_quote_adjusted_source_allowance=actual <= quote_adjusted_allowance,
            all_measured_output_bounds_passed=all(row['passed'] is not False for row in output_checks.values()),
            all_component_allowances_passed=all(row['passed'] for row in component_checks.values()))
