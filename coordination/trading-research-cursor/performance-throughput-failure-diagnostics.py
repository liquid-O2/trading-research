def source_clock_diagnostic(unit, *, maximum_rows):
    """Bounded timestamp-only diagnosis; preserves physical order and all rows."""
    import pyarrow.parquet as pq
    import pyarrow.compute as pc
    from trading_research.operations.artifacts import file_digest
    path = ROOT.parent / 'data' / unit['source_path']
    parquet = pq.ParquetFile(path)
    before = file_digest(path) if path.stat().st_size <= 64 * 1024**2 else None
    scanned, selected, previous, previous_address = 0, 0, None, None
    violations = []
    offsets, offset = {}, 0
    for group in range(parquet.num_row_groups):
        offsets[group] = offset
        offset += parquet.metadata.row_group(group).num_rows
    for group in unit['source_groups']:
        within = 0
        for batch in parquet.iter_batches(batch_size=65536, row_groups=[group], columns=['t'], use_threads=False):
            scanned += len(batch)
            if scanned > maximum_rows:
                raise ValueError('timestamp diagnosis exceeds the original source scan ceiling')
            values = batch.column(0).to_pylist()
            for number, value in enumerate(values):
                address = offsets[group] + within + number
                if value is None:
                    if len(violations) < 16:
                        violations.append({'kind': 'null_clock', 'source_row': address})
                    continue
                if not unit['event_start_ns'] <= value < unit['event_end_ns']:
                    continue
                selected += 1
                if previous is not None and value < previous and len(violations) < 16:
                    violations.append({'kind': 'backward_clock', 'previous_t': previous, 't': value,
                        'previous_source_row': previous_address, 'source_row': address,
                        'backward_ns': previous - value})
                previous, previous_address = value, address
            within += len(values)
            if len(violations) == 16:
                break
        if len(violations) == 16:
            break
    return {'unit': unit, 'timestamp_only_diagnostic': True, 'source_values_modified': False,
        'sorted_or_dropped_observations': False, 'physical_rows_scanned': scanned,
        'selected_timestamp_rows_examined': selected, 'first_up_to_16_violations': violations,
        'source_file_size': path.stat().st_size, 'small_file_sha256': before,
        'scope': 'Diagnostic only; no event-time/source-order reconciliation or scientific source exclusion admitted.'}


