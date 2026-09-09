"""Bounded real-observation parity and immutable annual checkpoint joins.

Called only inside the registered Jumbo worker after its resource limits.
The preserved reference is an executed earlier implementation, not an
independent scientific oracle; independent literal cases remain in the check.
"""
from datetime import date
import hashlib
import json
import math
import time

from trading_research.errors import IntegrityError
from trading_research.operations.artifacts import artifact_ref, canonical_json, digest
from trading_research.operations.trials import TrialRegistry


from trading_research.research.jumbo_checkpoints import _file, checked_checkpoints
from tools.jumbo_resources import cpu_limit


def _same(left, right, path, counts, tolerance):
    if isinstance(left, float) and isinstance(right, (int, float)) and not isinstance(right, bool):
        error = abs(left - right)
        if not math.isfinite(error) or error > tolerance:
            raise IntegrityError(f"real-data parity numeric mismatch at {path}")
        counts["floating_values"] += 1
        counts["maximum_absolute_float_error"] = max(counts["maximum_absolute_float_error"], error)
    elif isinstance(left, dict) and isinstance(right, dict):
        if left.keys() != right.keys():
            raise IntegrityError(f"real-data parity keys differ at {path}")
        for key in left:
            _same(left[key], right[key], f"{path}/{key}", counts, tolerance)
    elif isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        if len(left) != len(right):
            raise IntegrityError(f"real-data parity length differs at {path}")
        for at, (a, b) in enumerate(zip(left, right, strict=True)):
            _same(a, b, f"{path}/{at}", counts, tolerance)
    elif type(left) is not type(right) or left != right:
        raise IntegrityError(f"real-data parity identity/integer mismatch at {path}")
    else:
        counts["exact_values"] += 1


def resource_check_route(execution):
    """Unknown execution schemas must not silently select a historical check."""
    version=execution.get('version')
    if version in ('jumbo-extraction-resume-performance-v2','jumbo-extraction-resume-performance-v3',
            'jumbo-extraction-resume-performance-v4','jumbo-extraction-resume-performance-v5',
            'jumbo-extraction-resume-performance-v6','jumbo-extraction-resume-performance-v7',
            'jumbo-complete-model-workload-v8'):
        return 'annual_and_models'
    if version=='jumbo-extraction-resume-performance-v1':
        return 'legacy_60_dates'
    raise IntegrityError('unsupported resource execution schema; no data check was selected')


def check_actual_extraction(packet, protocol, root, store):
    execution = store.read_json(artifact_ref(packet["execution_plan"]))
    if resource_check_route(execution)=='annual_and_models':
        return _check_actual_annual_extraction(packet, protocol, root, store, execution)
    import pyarrow as pa
    import pyarrow.compute as pc
    from references.jumbo_extraction_v1 import jumbo_report as old_report
    from references.jumbo_extraction_v1 import jumbo_tables as old_tables
    from references.jumbo_extraction_v1.ohlc_ranges import MinuteBars as OldBars
    from trading_research.foundations.cash_calendar import CashCalendar
    from trading_research.research import jumbo_report, jumbo_tables
    from trading_research.research.jumbo_study import _ns, _read_table, _rows_table
    from trading_research.research.ohlc_ranges import MinuteBars
    pa.set_cpu_count(1)
    pa.set_io_thread_count(1)
    start = time.process_time()
    records = checked_checkpoints(packet, protocol, root, store)
    execution = store.read_json(artifact_ref(packet["execution_plan"]))
    settings = execution["reference_check"]
    if (settings["root"], settings["year"], settings["intended_cash_dates"]) != ("NQ", 2020, 60):
        raise IntegrityError("real-data reference check population changed")
    plan = store.read_json(artifact_ref(packet["analysis_plan"]))
    checkpoint = records[(settings["root"], settings["year"])]["record"]
    calendar = CashCalendar(root / protocol["calendar_path"])
    dates = jumbo_tables.cash_dates(calendar, date(2020, 1, 1), date(2020, 12, 31))[:60]
    intended = tuple(c.day.isoformat() for c in dates)
    table = _read_table(store, checkpoint["canonical_sources"][0])
    if table.num_rows != 346579:
        raise IntegrityError("reference cohort differs from admitted NQ2020 partition")
    current = MinuteBars.from_table(table, source_version=checkpoint["source_version"])
    original = OldBars.from_table(table, source_version=checkpoint["source_version"])
    del table
    kwargs = dict(root="NQ", recipes=protocol["clock_recipes"], plan=plan,
                  evaluation_cut=_ns("2025-01-01T00:00:00Z"))
    def batch(module, series, **extra):
        rows = {"formations": [], "paths": [], "specials": []}
        for result in module.extract_dates(series, dates, **kwargs, **extra):
            for name in rows:
                rows[name].extend(result[name])
        return rows
    clock = time.process_time()
    reference_rows = batch(old_tables, original)
    timing = {"reference_extraction_cpu_seconds": time.process_time() - clock}
    print(json.dumps({"parity": "reference60dates", **timing}), flush=True)
    clock = time.process_time()
    current_rows = batch(jumbo_tables, current)
    timing["optimized_extraction_cpu_seconds"] = time.process_time() - clock
    counts = {"floating_values": 0, "exact_values": 0, "maximum_absolute_float_error": 0.0}
    tolerance = settings["float_absolute_tolerance"]
    _same(reference_rows, current_rows, "extraction", counts, tolerance)
    for name in current_rows:
        saved = _read_table(store, checkpoint["tables"][name])
        saved = saved.filter(pc.is_in(saved["date"], value_set=pa.array(intended)))
        regenerated = _rows_table(current_rows[name], kind=name)
        if not saved.schema.equals(regenerated.schema):
            raise IntegrityError("saved checkpoint schema differs from regenerated real data")
        _same(saved.to_pylist(), regenerated.to_pylist(), "saved/" + name, counts, tolerance)
        del saved, regenerated
    clock = time.process_time()
    resumed = batch(jumbo_tables, current, emit_first_date=dates[30].day)
    expected = {name: [r for r in current_rows[name] if r["date"] >= intended[30]] for name in current_rows}
    _same(expected, resumed, "resumed", counts, tolerance)
    timing["resumed30dates_cpu_seconds"] = time.process_time() - clock
    del resumed, expected
    clock = time.process_time()
    reference_statistics = old_report.year_statistics(reference_rows, intended, plan=plan)
    timing["reference_statistics_cpu_seconds"] = time.process_time() - clock
    clock = time.process_time()
    current_statistics = jumbo_report.year_statistics(current_rows, intended, plan=plan)
    timing["optimized_statistics_cpu_seconds"] = time.process_time() - clock
    _same(reference_statistics, current_statistics, "statistics", counts, tolerance)
    per_day = (timing["optimized_extraction_cpu_seconds"] + timing["optimized_statistics_cpu_seconds"]) / 60
    remaining_dates = sum(len(jumbo_tables.cash_dates(calendar, date(y, 1, 1), date(y, 12, 31)))
                          for r in protocol["roots"] for y in range(2020, 2025) if (r, y) not in records)
    # The first60 dates include unavailable/initial-history cases. A1.25
    # factor plus50CPU seconds allows indexing, serialization and shard reuse.
    projected = per_day * remaining_dates * 1.25 + 50
    report = {"passed": True, "root": "NQ", "year": 2020, "intended_cash_dates": 60,
              "first_date": intended[0], "last_date": intended[-1],
              "actual_admitted_tables_read": 4, "market_model_fits": 0,
              "row_counts": {name: len(rows) for name, rows in current_rows.items()},
              "comparisons": counts, "timing": timing,
              "remaining_intended_dates": remaining_dates,
              "projected_remaining_extraction_cpu_seconds_conservative": projected,
              "within_declared_extract_cap": projected <= cpu_limit(protocol, 'extract'),
              "scope": "All fields and statistics from identical60date real cohort; optimized vs preserved reference, saved2020 table rows, and30date resumed continuation. Whole study completion and model quality are not asserted.",
              "total_cpu_seconds_internal": time.process_time() - start}
    print(json.dumps({"parity": "complete", **report}), flush=True)
    return report


def _retained_annual_stage(packet, protocol, root, store, execution, state):
    """Reuse only the completed annual stage of the retained failed check9."""
    from tools.jumbo_verification import annual_stage_fingerprint, retained_function_fingerprint
    review = _file(root, execution['retained_annual_stage_review'])
    prior = _file(root, review['execution'])
    old_packet = _file(root, review['packet'])
    attempt = state['attempts'].get(prior['attempt_id'])
    trial = state['trials'].get(prior['trial_id'])
    if (prior['success'] is not False or prior['mode'] != 'check'
            or prior['family'] != protocol['family'] or not prior['within_declared_limits']
            or attempt is None or attempt['status'] != 'failed'
            or trial is None or trial['code_hash'] != prior['code_snapshot']['sha256']
            or old_packet['attempt_id'] != attempt['id'] or old_packet['trial_id'] != prior['trial_id']
            or old_packet['analysis_plan'] != packet['analysis_plan']
            or old_packet['protocol_sha256'] != packet['protocol_sha256']
            or not any(r['kind'] == 'research_study_execution' and r['sha256'] == digest(prior)
                       for r in attempt['result_artifacts'])):
        raise IntegrityError('retained annual stage lacks its exact failed registered receipt')
    raw_log = store.read(artifact_ref(prior['worker_log']))
    if (len(raw_log) != review['worker_log']['size_bytes']
            or hashlib.sha256(raw_log).hexdigest() != review['worker_log']['sha256']):
        raise IntegrityError('retained annual measurement log changed')
    stages = []
    for line in raw_log.decode().splitlines():
        if not line.startswith('{'):
            continue
        value = json.loads(line)
        if value.get('annual_preflight') == 'all_tables_and_statistics_match':
            stages.append(value)
    if len(stages) != 1 or stages[0] != review['completed_annual_stage']:
        raise IntegrityError('complete annual measurements differ from registered log')
    snapshot = store.read_json(artifact_ref(prior['code_snapshot']))
    for name in execution['annual_stage_dependency_closure']:
        if (name not in snapshot['manifest']
                or packet['code_manifest'].get(name) != snapshot['manifest'][name]):
            raise IntegrityError('retained annual proof has a changed measurement dependency')
    def old_source(path):
        raw = bytes.fromhex(snapshot['files'][path]['$bytes'])
        if hashlib.sha256(raw).hexdigest() != snapshot['manifest'][path]:
            raise IntegrityError('old annual source bytes differ from its snapshot')
        return raw.decode()
    def current_source(path):
        raw = (root/path).read_bytes()
        if hashlib.sha256(raw).hexdigest() != packet['code_manifest'][path]:
            raise IntegrityError('current annual source bytes differ from its snapshot')
        return raw.decode()
    parity_path = 'src/trading_research/research/jumbo_parity.py'
    if annual_stage_fingerprint(old_source(parity_path)) != annual_stage_fingerprint(current_source(parity_path)):
        raise IntegrityError('annual measurement/serialization block changed')
    for path, names in {
        parity_path: ('_same',),
        'src/trading_research/research/jumbo_study.py': ('_ns', '_read_table', '_read_statistics', '_rows_table'),
        'src/trading_research/operations/artifacts.py': ('canonical_json',),
    }.items():
        previous, current = old_source(path), current_source(path)
        for name in names:
            if retained_function_fingerprint(previous, name) != retained_function_fingerprint(current, name):
                raise IntegrityError('retained annual serializer/reader/parity helper changed')
    return {**stages[0], 'original_attempt_id': prior['attempt_id'],
            'original_attempt_status': 'failed', 'original_worker_log': prior['worker_log'],
            'reuse_scope': 'completed annual computation only; no promotion of the failed overall attempt',
            'runtime_and_semantics': 'unchanged analysis/protocol pins; relevant code and annual statement AST checked'}


def _check_actual_annual_extraction(packet, protocol, root, store, execution):
    """Measure a whole annual report, whose bootstrap cost is not per-date."""
    import pyarrow as pa
    import gzip
    import gc
    from trading_research.foundations.cash_calendar import CashCalendar
    from trading_research.research.jumbo_tables import cash_dates, extract_dates
    from trading_research.research.jumbo_report import year_statistics
    from trading_research.research.jumbo_study import (_ns, _read_table, _rows_table,
                         _read_statistics, _attach_anchors, _definition_supplement)
    from trading_research.research.ohlc_ranges import MinuteBars
    pa.set_cpu_count(1)
    pa.set_io_thread_count(1)
    start = time.process_time()
    prior = _file(root, execution["prior_reference_check"])
    state = TrialRegistry(root / "evidence/trials").state()
    attempt = state["attempts"].get(prior["attempt_id"])
    if (prior.get("success") is not True or prior["mode"] != "check"
            or prior["family"] != protocol["family"] or attempt is None
            or attempt["status"] != "succeeded" or attempt["family"] != protocol["family"]
            or not any(r["kind"] == "research_study_execution" and r["sha256"] == digest(prior)
                       for r in attempt["result_artifacts"])):
        raise IntegrityError("prior reference comparison lacks a successful registered receipt")
    previous_worker = store.read_json(artifact_ref(prior["worker_report"]))
    if previous_worker.get("actual_extraction_parity", {}).get("passed") is not True:
        raise IntegrityError("prior reference comparison did not pass")
    previous_code = store.read_json(artifact_ref(prior["code_snapshot"]))["manifest"]
    for name in execution["unchanged_extraction_dependencies"]:
        if packet["code_manifest"].get(name) != previous_code.get(name) or name not in previous_code:
            raise IntegrityError("earlier reference proof does not apply to a changed extraction dependency")
    records = checked_checkpoints(packet, protocol, root, store)
    plan = store.read_json(artifact_ref(packet["analysis_plan"]))
    # Validate completed extraction reuse before any new resource work. Its
    # numerical inputs remain immutable when authorization tests are extended.
    from trading_research.research.jumbo_workload_reuse import completed_development_extraction
    completed_development = completed_development_extraction(packet, protocol, root, store)
    checkpoint = records[("NQ", 2020)]["record"]
    from dataclasses import asdict
    from trading_research.research.jumbo_narrative import descriptive_report
    from trading_research.research.jumbo_preflight import two_size_cost
    completed_records = [v['record'] for _, v in sorted(records.items())]
    clock = time.process_time()
    one_annual_narrative = descriptive_report(completed_records[:1], store,
                    protocol=protocol, analysis_plan=plan, stage='development',
                    supplements=('Partial annual reporting resource measurement; no study-completion claim.',)).encode()
    single_narrative_cpu, single_narrative_bytes = time.process_time()-clock, len(one_annual_narrative)
    del one_annual_narrative
    clock = time.process_time()
    narrative = descriptive_report(completed_records, store,
                    protocol=protocol, analysis_plan=plan, stage='development',
                    supplements=('Partial development checkpoint: NQ2020–2022 only, three of ten intended instrument-years. '
                                 'This registered check publishes the retained descriptive evidence. '
                                 'Source correction, remaining annuals, independent fitting and heldout confirmation remain separate outstanding work.',)).encode()
    narrative_cpu = time.process_time()-clock
    narrative_bytes = len(narrative)
    if 2*narrative_bytes > packet['limits']['maximum_output_bytes']:
        raise IntegrityError('retained descriptive report exceeds declared output allowance')
    report_artifact = asdict(store.put_bytes(narrative, kind='jumbo_partial_question_based_report_markdown_v1'))
    report_path = root/'reports/jumbo-runs'/packet['attempt_id']/'research-report.md'
    report_path.write_bytes(narrative)
    print(json.dumps({'stage': 'retained_descriptive_report_published', 'path': str(report_path),
                      'artifact': report_artifact, 'annual_shards': len(records),
                      'cpu_seconds': narrative_cpu,
                      'single_annual_report_cpu_seconds': single_narrative_cpu}), flush=True)
    del narrative
    calendar = CashCalendar(root / protocol["calendar_path"])
    dates = cash_dates(calendar, date(2020, 1, 1), date(2020, 12, 31))
    intended = tuple(c.day.isoformat() for c in dates)
    if len(dates) != 253:
        raise IntegrityError("annual preflight changed its declared full cash-date population")
    table = _read_table(store, checkpoint["canonical_sources"][0])
    series = MinuteBars.from_table(table, source_version=checkpoint["source_version"])
    del table
    index_cpu = time.process_time() - start
    retained_annual = None
    if execution.get('retained_annual_stage_review'):
        retained_annual = _retained_annual_stage(packet, protocol, root, store, execution, state)
        extraction_cpu = retained_annual['extraction_cpu_seconds']
        statistics_cpu = retained_annual['statistics_cpu_seconds']
        serialization_cpu = retained_annual['serialization_cpu_seconds']
        output_bytes = retained_annual['annual_output_bytes']
        counts = retained_annual['comparisons']
        batch = {name: _read_table(store, ref).to_pylist() for name, ref in checkpoint['tables'].items()}
        print(json.dumps({'annual_preflight': 'reused_exact_registered_completed_stage',
                          'evidence': retained_annual}), flush=True)
    else:
        batch = {"formations": [], "paths": [], "specials": []}
        clock = time.process_time()
        for value in extract_dates(series, dates, root="NQ", recipes=protocol["clock_recipes"],
                                   plan=plan, evaluation_cut=_ns("2025-01-01T00:00:00Z")):
            for name in batch:
                batch[name].extend(value[name])
        extraction_cpu = time.process_time() - clock
        print(json.dumps({"annual_preflight": "extracted", "dates": len(dates),
                          "extraction_cpu_seconds": extraction_cpu}), flush=True)
        counts = {"floating_values": 0, "exact_values": 0, "maximum_absolute_float_error": 0.0}
        serialization_cpu, output_bytes = 0.0, 0
        for name in batch:
            import pyarrow.parquet as pq
            clock = time.process_time()
            regenerated = _rows_table(batch[name], kind=name)
            sink = pa.BufferOutputStream()
            pq.write_table(regenerated, sink, compression="zstd", use_dictionary=True,
                           write_statistics=True, row_group_size=65536)
            output_bytes += sink.tell()
            serialization_cpu += time.process_time() - clock
            saved = _read_table(store, checkpoint["tables"][name])
            # Exact Arrow equality is cheaper than reconstructing millions of
            # Python values. On failure, retain a precise typed diagnostic.
            if not saved.equals(regenerated):
                _same(saved.to_pylist(), regenerated.to_pylist(), "annual_saved/" + name, counts, 1e-12)
            counts["exact_values"] += saved.num_rows * saved.num_columns
            del saved, regenerated, sink
        clock = time.process_time()
        statistics = year_statistics(batch, intended, plan=plan)
        statistics_cpu = time.process_time() - clock
        clock = time.process_time()
        payload = canonical_json(statistics)
        compressed_statistics = gzip.compress(payload, compresslevel=3, mtime=0)
        output_bytes += len(compressed_statistics)
        serialization_cpu += time.process_time() - clock
        original_statistics = _read_statistics(store, checkpoint["statistics"])
        _same(original_statistics, statistics, "annual_statistics", counts, 1e-12)
        print(json.dumps({'annual_preflight':'all_tables_and_statistics_match',
                         'extraction_cpu_seconds':extraction_cpu,'statistics_cpu_seconds':statistics_cpu,
                         'serialization_cpu_seconds':serialization_cpu,'annual_output_bytes':output_bytes,
                         'comparisons':counts}),flush=True)
        del payload, compressed_statistics, original_statistics, statistics
    supplemented = dict(checkpoint)
    clock = time.process_time()
    anchor_bytes = _attach_anchors(series, supplemented, store, packet, protocol,
                      formation_rows=batch['formations'], path_rows=batch['paths'],
                      remaining_bytes=packet['limits']['maximum_output_bytes'])
    anchor_cpu = time.process_time()-clock
    print(json.dumps({'preflight': 'completed_annual_anchor_supplement',
                      'record': supplemented, 'cpu_seconds': anchor_cpu,
                      'derived_output_bytes': anchor_bytes}), flush=True)
    from trading_research.research.jumbo_location_tables import preflight_location_year
    location = preflight_location_year(series, batch['formations'], root='NQ', year=2020,
                    evaluation_cut=_ns('2025-01-01T00:00:00Z'),
                    plan=store.read_json(artifact_ref(packet['model_plan'])),
                    dates=[intended[i] for i in execution['preflight']['location_cash_date_ordinals_in_annual_population']])
    location_profile = location['preflight']
    print(json.dumps({'preflight': 'completed_location_resource_unit', 'measurement': location_profile}), flush=True)
    del location, batch, series
    gc.collect()
    review = _file(root, execution['interrupted_attempt_review'])
    old_packet = _file(root, review['packet'])
    predecessor = old_packet['predecessor']
    raw = (root/predecessor['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != predecessor['sha256']:
        raise IntegrityError('source audit lost its original admitted predecessor')
    admission_execution = json.loads(raw)
    admission = store.read_json(artifact_ref(admission_execution['worker_report']))
    from trading_research.research.jumbo_source_reuse import source_supplement
    source = source_supplement(packet, protocol, root, store, admission,
                       remaining_bytes=packet['limits']['maximum_output_bytes']-anchor_bytes-2*narrative_bytes)
    source_report = source['report']
    print(json.dumps({'stage': 'actual_definition_supersession',
                      'status': source_report.get('actual_status'),
                      'accepted': source_report.get('actual_accepted'),
                      'recovered_primary_minutes': source_report.get('recovered_primary_minutes', 0),
                      'raw_definition_audit_files': len(source_report.get('raw_definition_audit_attempts', ())),
                      'raw_ohlc_read_attempts': len(source_report.get('raw_ohlc_read_attempts', ())),
                      'cpu_seconds': source_report['cpu_seconds_internal'],
                      'artifact': source['artifact'], 'reuse': source.get('reuse'),
                      'cpu_seconds_current': source.get('cpu_seconds_current', source_report['cpu_seconds_internal'])}), flush=True)
    raw_read_attempts = source.get('raw_read_attempts_current', sum(len(source_report.get(key,())) for key in
                  ('raw_definition_audit_attempts','raw_definition_index_read_files','raw_ohlc_read_attempts')))
    source_bytes = source['derived_output_bytes']
    has_correction = source['corrected_table'] is not None
    del source['corrected_table']
    from trading_research.research.jumbo_matrix import prepare_paths
    from trading_research.research.jumbo_preflight import model_workload_preflight
    if execution.get('evaluation_reference_manifest'):
        reference = _file(root, execution['evaluation_reference_manifest'])
        if packet['code_manifest'].get(reference['same_external_numerical_dependency']) != reference['same_external_numerical_dependency_sha256']:
            raise IntegrityError('retained evaluation reference has a changed numerical dependency')
    clock = time.process_time()
    matrix = prepare_paths(store, [supplemented], plan=plan, phase='development',
                        anchor_supplements={('NQ',2020):supplemented['anchor_supplement']})
    matrix_cpu = time.process_time()-clock
    train_dates = len(cash_dates(calendar, date(2020,1,1), date(2022,12,31)))
    select_dates = len(cash_dates(calendar, date(2024,7,1), date(2024,12,31)))
    last_ns = max(p['primary_coverage']['last_end_ns'] for p in admission['partitions'])
    from datetime import datetime, timezone
    endpoint = datetime.fromtimestamp(last_ns//1_000_000_000, tz=timezone.utc).date()
    heldout_dates = len(cash_dates(calendar, date(2025,1,1), endpoint))
    model = model_workload_preflight(matrix, store, [supplemented], plan,
                   store.read_json(artifact_ref(packet['model_plan'])), train_dates=train_dates,
                   select_dates=select_dates, heldout_dates=heldout_dates, packet=packet, protocol=protocol, root=root)
    matrix_array_bytes = matrix.features.nbytes+sum(v.nbytes for v in matrix.fields.values())
    del matrix
    gc.collect()
    annual_cpu = extraction_cpu + serialization_cpu + statistics_cpu
    remaining_years = 10 - len(records)
    # The optional corrected NQ2024 cohort is a separately retained sensitivity
    # to the original admission. It never overwrites a frozen original shard.
    sensitivity_years = int(has_correction)
    narrative_cost = [two_size_cost(single_narrative_cpu, narrative_cpu, 1, len(records), 5+int(instrument=='NQ')*sensitivity_years)
                      for instrument in protocol['roots']]
    projected = (annual_cpu*(remaining_years+sensitivity_years)+anchor_cpu*(10+sensitivity_years)
                 +source.get('cpu_seconds_current', source_report['cpu_seconds_internal'])+sum(v['cpu_seconds'] for v in narrative_cost))*1.25+25
    if completed_development is not None:
        projected=0.
        remaining_years=0
    heldout_years = len(protocol['roots'])*(endpoint.year-2025+1)
    # A partial final year still incurs one whole annual bootstrap/report.
    confirmation_narrative_cost = two_size_cost(single_narrative_cpu, narrative_cpu, 1, len(records), heldout_years//len(protocol['roots']))
    confirmation_extraction = (annual_cpu*heldout_years+anchor_cpu*heldout_years+confirmation_narrative_cost['cpu_seconds']*len(protocol['roots']))*1.25+25
    model['projected_fit_cpu_seconds_conservative'] += matrix_cpu*10*1.25
    model['projected_confirmation_model_cpu_seconds_conservative'] += matrix_cpu*heldout_years*1.25
    confirmation_total = confirmation_extraction+model['projected_confirmation_model_cpu_seconds_conservative']
    reused_bytes = sum(sum(r['record'][k]['size_bytes'] for k in ('statistics',))+
                       sum(v['size_bytes'] for v in r['record']['tables'].values()) for r in records.values())
    narrative_output_bound = sum(two_size_cost(single_narrative_bytes, narrative_bytes, 1, len(records),
                                 5+int(instrument=='NQ')*sensitivity_years)['cpu_seconds'] for instrument in protocol['roots'])
    projected_extraction_bytes = reused_bytes+(output_bytes+anchor_bytes)*(remaining_years+sensitivity_years)*1.25+anchor_bytes*len(records)+2*narrative_output_bound+source_bytes
    if completed_development is not None:
        projected_extraction_bytes=completed_development['actual_derived_output_bytes']
    model['projected_matrix_array_bytes'] = math.ceil(matrix_array_bytes*10*1.5)
    model['projected_full_model_peak_bytes_conservative'] = math.ceil((matrix_array_bytes*10*1.25+
                   model['projected_model_working_array_bytes']+256*1024*1024)*1.15)
    model['memory_projection_rule'] = 'Exact measured compact annual arrays x10 x1.25, largest intended full target design and offsets, bounded65536-row solver buffers,256MiB fixed provider allowance, then1.15. Includes simultaneous design copies; actual4GiB worker limit remains binding.'
    model['within_declared_fit_cap'] = (model['projected_fit_cpu_seconds_conservative'] <= cpu_limit(protocol, 'fit')
                         and model['projected_fit_output_bytes_conservative'] <= packet['limits']['maximum_output_bytes']
                         and model['projected_full_model_peak_bytes_conservative'] <= protocol['resources']['memory_bytes'])
    model['projected_confirmation_total_cpu_seconds_conservative'] = confirmation_total
    model['projected_confirmation_extraction_cpu_seconds_conservative'] = confirmation_extraction
    model['projected_confirmation_output_bytes_conservative'] = (
        model['projected_confirmation_model_output_bytes_conservative']
        +(output_bytes+anchor_bytes)*heldout_years*1.25+2*single_narrative_bytes*heldout_years)
    model['within_declared_confirmation_cap'] = (confirmation_total <= cpu_limit(protocol, 'confirmation')
                         and model['projected_confirmation_output_bytes_conservative'] <= packet['limits']['maximum_output_bytes']
                         and model['projected_full_model_peak_bytes_conservative'] <= protocol['resources']['memory_bytes'])
    charged = sum(a['cpu_reservation_seconds'] if a['status'] == 'running' else a['cpu_seconds']
                  for a in state['attempts'].values() if a['family'] == protocol['family'])
    remaining_cpu = protocol['resources']['cpu_budget_seconds'] - charged
    combined_projection = projected + model['projected_fit_cpu_seconds_conservative'] + confirmation_total
    return {"passed": True, "root": "NQ", "year": 2020,
            "intended_cash_dates": len(dates), "first_date": intended[0], "last_date": intended[-1],
            "actual_admitted_tables_read": 8+int(has_correction), "market_model_fits": model['actual_optimizer_calls']+model['actual_empirical_distribution_calls'],
            'actual_market_data_read_attempts':8+int(has_correction)+raw_read_attempts,
            "actual_table_read_inventory": {'annual_canonical_index':1,'saved_annual_parity_tables':3,
                         'prepared_paths_formations_and_anchors':3,'source_specials':1,'original_nq2024_source_comparison':int(has_correction)},
            "source_raw_read_report": source['artifact'],
            "row_counts": {name: value['rows'] for name, value in checkpoint['tables'].items()},
            "prior_reference_check": execution["prior_reference_check"],
            'retained_annual_stage': retained_annual,
            'descriptive_report': {'artifact': report_artifact, 'path': str(report_path),
                                   'completed_annual_shards': len(records), 'study_complete': False},
            'narrative_workload': {'single_annual_cpu_seconds': single_narrative_cpu,
                                  'three_annual_cpu_seconds': narrative_cpu,
                                  'development_projection': narrative_cost,
                                  'confirmation_projection': confirmation_narrative_cost,
                                  'projected_report_bytes_upper': narrative_output_bound,
                                  'rule': 'actual one- and three-annual-input final reports; fixed and variable terms separated per root; sum per-root bounds conservatively repeats header overhead, never scales by cash dates'},
            "comparisons": counts,
            "timing": {"index_and_provenance_cpu_seconds": index_cpu,
                       "extraction_cpu_seconds": extraction_cpu, "statistics_cpu_seconds": statistics_cpu,
                       "serialization_cpu_seconds": serialization_cpu, "whole_annual_work_cpu_seconds": annual_cpu,
                       "annual_anchor_cpu_seconds":anchor_cpu,'three_annual_narrative_cpu_seconds':narrative_cpu,
                       'annual_model_matrix_cpu_seconds':matrix_cpu},
            "measured_annual_output_bytes": output_bytes,
            'source_supersession':source_report,'source_supersession_artifact':source['artifact'],
            'source_stage_reuse': source.get('reuse'),
            'completed_development_extraction':completed_development,
            'location_preflight':location_profile,'model_preflight':model,
            'derived_output_bytes':anchor_bytes+source_bytes+2*narrative_bytes+model.get('derived_output_bytes',0),
            'projected_extraction_output_bytes_conservative':projected_extraction_bytes,
            'remaining_cumulative_cpu_after_current_reservation': remaining_cpu,
            'projected_remaining_extract_fit_confirmation_cpu_seconds': combined_projection,
            'all_remaining_stage_projections_fit_cumulative_allowance': combined_projection <= remaining_cpu,
            "remaining_root_years": remaining_years,
            "projected_remaining_extraction_cpu_seconds_conservative": projected,
            "within_declared_extract_cap": projected <= cpu_limit(protocol, 'extract') and projected_extraction_bytes <= packet['limits']['maximum_output_bytes'],
            "projection_rule": "Complete development extraction contributes zero remaining work only after its exact registered receipt and unchanged extraction dependencies are verified. Otherwise retain whole-annual extraction/reporting estimates. Confirmation counts each full or partial heldout year, exact anchors and narrative with1.25 uncertainty. Model reports, production storage and20/100-date trees are measured separately with1.5 uncertainty.",
            "scope": "Entire253date NQ2020 parity and unchanged prior60date proof; retained exact numerical/categorical resource units plus current20/100-date trees, continuous20/253-date reports and complete20-date model storage/prediction consumers. No heldout outcomes, predictor selection or predictive-quality claim.",
            "total_cpu_seconds_internal": time.process_time() - start}
