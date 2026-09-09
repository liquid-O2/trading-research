def audit_clock_records(authenticated, packet_path):
    import pyarrow.parquet as pq
    from trading_research.research.auction_flow_storage import BoundedOutputs
    from trading_research.operations.artifacts import canonical_json, publish_new
    packet, protocol, cap = authenticated['packet'], authenticated['protocol'], authenticated['cap']
    prior_ref = authenticated['extension']['throughput_observed_execution']
    observed = load_reference(prior_ref)
    if (observed['protocol_sha256'] != packet['protocol_sha256'] or observed['success'] is not False
            or observed['mode'] != 'throughput' or observed['cpu_accounting_complete'] is not True
            or observed['within_declared_limits'] is not True):
        raise ValueError('clock audit requires its retained bounded partial throughput attempt')
    prior_dir = Path(prior_ref['path']).parent
    outputs = BoundedOutputs(Path(packet_path).parent / 'outputs', maximum_total_bytes=cap['maximum_output_bytes'] - cap['supervisor_output_reserve_bytes'], maximum_file_bytes=cap['maximum_output_file_bytes'])
    records, completed = [], []
    for folder in sorted((prior_dir / 'outputs').glob('source-unit-*')):
        child = json.loads(checked(folder / 'packet.json', maximum=1024**2)[0])
        if child['attempt_id'] != observed['attempt_id'] or child['configuration'] != observed['configuration'] or child['code_snapshot'] != observed['code_snapshot']:
            raise ValueError('retained child packet differs from its bounded partial execution')
        failure_path, receipt_path = folder / 'source-clock-failure.json', folder / 'artifacts/source-unit-receipt.json'
        if failure_path.exists():
            raw, sha = checked(failure_path, maximum=1024**2)
            failure = json.loads(raw)
            if failure['unit'] != child['unit'] or failure['attempt_id'] != child['attempt_id'] or failure['ordinal'] != child['ordinal'] or failure['success'] is not False:
                raise ValueError('retained source failure identity differs')
            unit = failure['unit']
            parquet = pq.ParquetFile(ROOT.parent / 'data' / unit['source_path'])
            offsets, at = [], 0
            for group in range(parquet.num_row_groups):
                offsets.append(at)
                at += parquet.metadata.row_group(group).num_rows
            wanted = {row for issue in failure['diagnostic']['first_up_to_16_violations']
                for anchor in (issue.get('previous_source_row', issue['source_row']), issue['source_row'])
                for row in range(max(0, anchor - 2), min(at, anchor + 3))}
            rows, read_groups = [], []
            for group, start in enumerate(offsets):
                stop = start + parquet.metadata.row_group(group).num_rows
                selected = sorted(row for row in wanted if start <= row < stop)
                if not selected:
                    continue
                table = parquet.read_row_group(group, use_threads=False)
                read_groups.append(group)
                for row in selected:
                    rows.append({'source_row': row, 'row_group': group, 'record': table.slice(row - start, 1).to_pylist()[0]})
            records.append({'unit': unit, 'original_failure_reference': {'path': str(failure_path), 'sha256': sha, 'size_bytes': len(raw)},
                'timestamp_diagnostic': failure['diagnostic'], 'read_groups': read_groups, 'unchanged_all_field_neighbor_records': rows})
        elif receipt_path.exists():
            raw, sha = checked(receipt_path, maximum=1024**2)
            receipt = json.loads(raw)
            if receipt['success'] is not True or receipt['unit'] != child['unit'] or receipt['attempt_id'] != child['attempt_id']:
                raise ValueError('completed child source receipt identity differs')
            require_reference_in_namespace(receipt['resource_unit'], folder / 'artifacts')
            resource_unit = load_reference(receipt['resource_unit'])
            require_reference_in_namespace(receipt['compiled_execution_counts'], folder / 'artifacts')
            counters = load_reference(receipt['compiled_execution_counts'])
            if any(counters[key] <= 0 for key in ('fused_rows', 'compiled_quote_slice_calls', 'compiled_native_quote_calls')):
                raise ValueError('completed child did not execute its compiled source paths')
            completed.append({'ordinal': child['ordinal'], 'unit': child['unit'],
                'receipt': {'path': str(receipt_path), 'sha256': sha, 'size_bytes': len(raw)},
                'resource_unit': receipt['resource_unit'], 'compiled_execution_counts': receipt['compiled_execution_counts'],
                'source_result_passed_before_coordinator_summary_failure': True})
        else:
            raise ValueError('partial throughput child has no completed result or explicit source failure')
    if len(records) + len(completed) != 17:
        raise ValueError('clock audit must account for all original17held-out windows')
    detail = outputs.json('clock-neighbor-records.json', records, kind='auction_flow_clock_neighbor_record_audit')
    report = {key: packet[key] for key in ('attempt_id', 'trial_id', 'protocol_sha256', 'code_snapshot', 'tools_snapshot', 'configuration')}
    report.update(family=protocol['family'], mode='clock-audit', success=True, source_component_verified=False,
        runtime_versions=authenticated['versions'], derived_output_bytes=outputs.written,
        audited_execution=prior_ref, completed_source_units=completed, source_clock_failure_count=len(records),
        clock_neighbor_records=detail, retained_original_window_count=17,
        observed_attempt_cpu_seconds=observed['cpu_seconds'], observed_attempt_wall_seconds=observed['wall_seconds'],
        observed_average_busy_cores=observed['cpu_seconds'] / observed['wall_seconds'],
        observed_allocation_utilization=observed['cpu_seconds'] / observed['wall_seconds'] / 17.85,
        scope='All-field read-only diagnosis of five retained source-clock failures and identity audit of twelve completed children. Partial throughput scope retained; missing per-child wait4/pool checkpoint not reconstructed. No sorting, dropping, source exclusion, clock repair, full source acceptance or end-to-end ETA admitted.')
    publish_new(Path(packet['worker_report']), canonical_json(report) + b'\n')
    return 0


