def throughput_windows(authenticated, index):
    """Reconstruct each frozen held-out window from the admitted source index."""
    from trading_research.data.reconcile import select_groups
    from trading_research.operations.artifacts import digest
    protocol = authenticated['protocol']
    declared = authenticated['extension']['throughput_windows']
    if len(declared) != 17 or len({w['source_path'] for w in declared}) != 17:
        raise ValueError('throughput requires all 17 distinct declared physical sources')
    result = []
    for value in declared:
        if value['event_end_ns'] - value['event_start_ns'] != 86_400_000_000_000 or not value['whole_window_inside_acquired_file']:
            raise ValueError('complete held-out UTC day required')
        selected, _ = select_groups(index, dataset=value['dataset'], start=value['event_start_ns'],
            end=value['event_end_ns'], max_scan_rows=protocol['resources']['maximum_source_day_scan_rows'])
        matched = [(record, groups) for record, groups in selected if record['path'] == value['source_path']]
        if len(matched) != 1:
            raise ValueError('held-out source is absent or ambiguous')
        record, groups = matched[0]
        if digest(record) != value['source_metadata_sha256'] or list(groups) != value['source_groups']:
            raise ValueError('held-out source metadata or row groups changed')
        result.append({'root': value['root'], 'role': 'independent_full_day_throughput_cost',
            'cash_date': None, 'event_start_ns': value['event_start_ns'], 'event_end_ns': value['event_end_ns'],
            'source_path': record['path'], 'source_metadata_version': digest(record), 'source_groups': groups,
            'calendar_version': None, 'source_variant': hashlib.sha256(record['path'].encode()).hexdigest()[:12],
            'coverage_basis': 'Explicitly initialized observed prefix of one retained physical source; no inferred pre-window book coverage. Full UTC day cost holdout, not complete annual family validation.'})
    return result


def throughput_source(authenticated, packet_path, worker_started):
    from trading_research.foundations.cash_calendar import CashCalendar
    from trading_research.research.auction_flow_storage import BoundedOutputs
    from trading_research.operations.artifacts import canonical_json, publish_new
    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    extension = authenticated['extension']
    index = load_reference(protocol['source_index'])
    windows = throughput_windows(authenticated, index)
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs',
        maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'],
        maximum_file_bytes=cap['maximum_output_file_bytes'])
    compiled = compile_source_projection(packet_path, outputs)
    evidence = {}
    results, references = execute_source_units_parallel(windows, protocol=protocol, index=index,
        coordinates=None, outputs=outputs, data_root=ROOT.parent / 'data', calendar=None,
        packet_path=packet_path, packet=packet, planned=authenticated['registered_plan'],
        concurrency=authenticated['concurrency'], cap=cap, worker_started=worker_started,
        evidence=evidence, compiled_projection=compiled)
    prior = load_reference(extension['throughput_calibration_worker'])
    rates = prior['actual_source_preflight']['source_cost_projection']['cpu_coefficients']
    comparisons = []
    for result, counts in zip(results, extension['throughput_windows'], strict=True):
        instruments = counts['raw_instruments_per_window_upper']
        prospective = {**counts, 'source_windows': 1,
            'instrument_window_allocations_upper': instruments,
            'instrument_atomic_cells_upper': instruments * counts['atomic_cells_per_instrument'],
            'instrument_native_cells_upper': counts['native_instrument_cells_upper'],
            'atomic_parts_per_consumer_upper': instruments * (counts['atomic_cells_per_instrument'] + counts['reader_batches_upper'])}
        allowance = 1.5 * sum(rate['cpu_seconds_per_work_unit'] * prospective[rate['prospective_count_field']] for rate in rates.values())
        pipeline = result['pipeline_cpu_components']
        actual = (sum(pipeline[key] for key in ('initialization', 'instrument_allocation', 'scan_and_consumers', 'finalization_and_native_storage'))
            - result['scan_cpu_components_disjoint']['reference_sample_collection']
            - result['native_reference_sample_collection_cpu_seconds']
            + result['event_storage_finalization_cpu_seconds'] + result.get('quote_replay_validation_cpu_seconds', 0)
            + result['measurement_json_serialization_cpu_seconds'])
        bounds = (result['raw_physical_rows'] <= counts['physical_scan_rows']
            and result['source_manifest']['physical_reader_batches'] <= counts['reader_batches_upper']
            and result['native_cells'] <= counts['native_instrument_cells_upper'])
        if not bounds:
            raise ValueError('held-out source exceeds frozen metadata allocation bounds')
        comparisons.append({'unit': result['unit'], 'source_stage_cpu_seconds': actual,
            'frozen_allowance_cpu_seconds': allowance, 'within_frozen_allowance': actual <= allowance,
            'allocation_bounds_passed': bounds,
            'quote_descriptor_bytes': result['event_storage']['quotes']['serialized_bytes']})
    average_cores = evidence['pool_child_wait4_cpu_seconds'] / evidence['wall_seconds']
    report = {key: packet[key] for key in ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration')}
    report.update(family=protocol['family'], mode='throughput', success=True,
        source_component_verified=False, complete_family_statistics=False,
        compiled_projection=compiled, runtime_versions=authenticated['versions'],
        resource_units=references, source_unit_parallel_execution=evidence,
        held_out_calibration=comparisons,
        all_held_out_source_costs_within_frozen_allowance=all(r['within_frozen_allowance'] for r in comparisons),
        actual_average_busy_cpu_cores=average_cores,
        effective_cpu_utilization=average_cores / authenticated['registered_plan']['effective_cpu_cores'],
        derived_output_bytes=outputs.written,
        scope='17 independent complete UTC source windows with source/native/measurement calculations and exact verified quote replay. Actual source throughput holdout; no all-family, Context or Location completion.')
    publish_new(Path(packet['worker_report']), canonical_json(report) + b'\n')
    return 0
