"""Actual acquired-contract OHLC research, run only by the bounded supervisor.

Admission persists full-source quality records and compact canonical Parquet
tables. Later statistics and models reuse those exact admitted observations.
"""
from collections import Counter
from dataclasses import asdict
from datetime import date, datetime, timezone
import gc
import hashlib
import json
from pathlib import Path
import resource
import time

from trading_research.data.ohlc import read_definition_index, read_ohlc_partition
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.operations.artifacts import ArtifactStore, artifact_ref, canonical_json, digest, publish_new
from trading_research.research.ohlc_ranges import MINUTE, MinuteBars

TRADE_HOUR_SHA256 = "4d281c613bf084a8106b7f009a7528e121b1fc8fd1cd620a2777ac9aed7a3e3f"


def _root_of(path):
    value = Path(path).parent.name
    if value.startswith("cme__nq-"):
        return "NQ"
    if value.startswith("cme__es-"):
        return "ES"
    raise ContractError("source lacks a declared NQ/ES root")


def _ns(value):
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ContractError("explicit UTC evaluation cut required")
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    delta = stamp - epoch
    return (delta.days * 86400 + delta.seconds) * 1_000_000_000 + delta.microseconds * 1000


def _put_table(store, table, *, kind, remaining_bytes):
    import pyarrow as pa
    import pyarrow.parquet as pq
    sink = pa.BufferOutputStream()
    pq.write_table(table, sink, compression="zstd", use_dictionary=True,
                   write_statistics=True, row_group_size=65536)
    payload = sink.getvalue().to_pybytes()
    if len(payload) > remaining_bytes:
        raise DependencyUnavailable("declared aggregate derived-output allowance exceeded")
    ref = store.put_bytes(payload, kind=kind)
    return {**asdict(ref), "rows": table.num_rows,
            "schema_sha256": hashlib.sha256(table.schema.serialize().to_pybytes()).hexdigest()}


def _ref(value):
    return artifact_ref({k: value[k] for k in ("sha256", "size_bytes", "kind")})


def _read_table(store, value):
    import pyarrow as pa
    import pyarrow.parquet as pq
    table = pq.read_table(pa.BufferReader(store.read(_ref(value))))
    if (table.num_rows != value["rows"] or
            hashlib.sha256(table.schema.serialize().to_pybytes()).hexdigest() != value["schema_sha256"]):
        raise IntegrityError("retained admitted table identity differs")
    return table



def _put_statistics(store, value, *, remaining_bytes):
    import gzip
    payload = canonical_json(value)
    compressed = gzip.compress(payload, compresslevel=3, mtime=0)
    if len(compressed) > remaining_bytes:
        raise DependencyUnavailable("complete statistics exceed remaining output allowance")
    ref = store.put_bytes(compressed, kind="jumbo_actual_year_statistics_gzip_v2")
    return {**asdict(ref), "encoding": "gzip-json", "uncompressed_sha256": hashlib.sha256(payload).hexdigest(),
            "uncompressed_size_bytes": len(payload)}


def _read_statistics(store, ref):
    payload = store.read(_ref(ref))
    if ref.get("encoding") == "gzip-json":
        import gzip
        import io
        maximum = ref.get("uncompressed_size_bytes", -1)
        if type(maximum) is not int or not 0 <= maximum <= 128*1024*1024:
            raise IntegrityError("bounded annual statistics required")
        with gzip.GzipFile(fileobj=io.BytesIO(payload)) as stream:
            payload = stream.read(maximum+1)
        if len(payload) != maximum or hashlib.sha256(payload).hexdigest() != ref["uncompressed_sha256"]:
            raise IntegrityError("expanded annual statistics identity differs")
    return json.loads(payload)


def _attach_anchors(series, record, store, packet, protocol, *, formation_rows=None, path_rows=None, remaining_bytes):
    from trading_research.research.jumbo_anchors import build_anchor_supplement
    execution = store.read_json(artifact_ref(packet["execution_plan"]))
    if formation_rows is None:
        formation_rows = _read_table(store, record["tables"]["formations"]).to_pylist()
    if path_rows is None:
        path_rows = _read_table(store, record["tables"]["paths"]).to_pylist()
    start = time.process_time()
    result = build_anchor_supplement(series, formation_rows, path_rows, root=record["root"], year=record["year"],
                   path_ref=record["tables"]["paths"], formation_ref=record["tables"]["formations"],
                   relationship_clocks=execution["anchor_supplement"]["relationship_clocks"],
                   frozen_analysis_id=packet["analysis_plan"]["sha256"])
    ref = _put_table(store, result["table"], kind="jumbo_exact_anchor_supplement_parquet_v2", remaining_bytes=remaining_bytes)
    supplement = {"table_ref":ref, "manifest":result["manifest"]}
    record["anchor_supplement"] = supplement
    record["anchor_supplement_cpu_seconds"] = time.process_time()-start
    return ref["size_bytes"]


def _predecessor(packet, root, store):
    identity = packet.get("predecessor")
    if identity is None:
        return None
    raw = (root / identity["path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != identity["sha256"]:
        raise IntegrityError("study predecessor changed after registration")
    execution = json.loads(raw)
    if execution.get("success") is not True:
        raise DependencyUnavailable("successful preceding study step required")
    return store.read_json(artifact_ref(execution["worker_report"]))


def _reconcile(table, protocol, root, store):
    """Reconcile each of 60 minute OHLCV records to actual retained trades."""
    import pyarrow as pa
    import pyarrow.compute as pc
    source_report = json.loads((root / protocol["pilot"]["reconciliation_report"]).read_bytes())
    trade_ref = artifact_ref(source_report["trades_artifact"])
    if (trade_ref.sha256 != TRADE_HOUR_SHA256 or trade_ref.size_bytes != 2524376
            or trade_ref.kind != "arrow_compact_trades" or source_report["success"] is not True
            or source_report["version"] != "quantpad-quarter-point-compact-v1"
            or source_report["dataset"] != "quantpad/cme__nq-continuous-futures__mbp-1"
            or source_report["tick_denominator"] != 4 or source_report["counts"]["trades"] != 56077
            or source_report["counts"]["unpriced_volume"] != 0
            or source_report["counts"]["gap_rows"] != 0):
        raise IntegrityError("retained independent trade hour differs from the declared source")
    payload = store.read(trade_ref)
    trades = pa.ipc.open_stream(pa.BufferReader(payload)).read_all()
    if (trades.num_rows != source_report["counts"]["trades"]
            or pc.sum(trades["size"]).as_py() != source_report["counts"]["volume"]):
        raise IntegrityError("retained trade source report does not reconcile to its actual artifact")
    start, end = (protocol["pilot"][k] for k in ("reconciliation_start_ns", "reconciliation_end_ns"))
    if source_report["start"] != start or source_report["end"] != end:
        raise IntegrityError("retained trade hour has another exact interval")
    grouped = {}
    previous = None
    for row in trades.to_pylist():
        at = row["t"]
        order = (at, row["source_order"])
        if previous is not None and order < previous:
            raise IntegrityError("trade-hour source order decreased")
        previous = order
        if not start <= at < end or row["price_valid"] != 1:
            raise IntegrityError("trade-hour interval/price domain mismatch")
        key = (at // MINUTE * MINUTE, row["instrument_id"])
        p, v = row["price"], row["size"]
        old = grouped.get(key)
        grouped[key] = [p, p, p, p, v] if old is None else [old[0], max(old[1], p), min(old[2], p), p, old[4] + v]
    hour = table.filter(pc.and_(pc.greater_equal(table["start_ns"], start), pc.less(table["start_ns"], end)))
    matches, differences = [], []
    for row in hour.to_pylist():
        key = (row["start_ns"], row["instrument_id"])
        actual = [row[k] for k in ("open_ticks", "high_ticks", "low_ticks", "close_ticks", "volume")]
        expected = grouped.pop(key, None)
        value = {"start_ns": key[0], "instrument_id": key[1], "source_ohlcv": actual, "trade_ohlcv": expected,
                 "source_valid": row["valid"], "source_row": row["source_row"], "contract_key": row["contract_key"]}
        (matches if actual == expected and row["valid"] else differences).append(value)
    success = len(matches) == 60 and not differences and not grouped and hour.num_rows == 60
    return {"success": success, "start_ns": start, "end_ns": end,
            "actual_trade_source": asdict(trade_ref), "actual_trade_count": trades.num_rows,
            "matched_minutes": len(matches), "mismatched_minutes": differences,
            "unmatched_trade_groups": [{"start_ns": k[0], "instrument_id": k[1], "ohlcv": v} for k, v in grouped.items()],
            "all_compared_minutes": matches + differences,
            "scope": "OHLCV parity for this actual hour only; not a price-path ordering certificate or whole-history trade reconciliation"}


def _coverage(table):
    import pyarrow.compute as pc
    n = table.num_rows
    if n > 1:
        starts, prior_starts = table["start_ns"].slice(1), table["start_ns"].slice(0, n - 1)
        prior_ends = table["end_ns"].slice(0, n - 1)
        delta = pc.subtract(starts, prior_ends)
        gaps = pc.greater(delta, 0)
        gap_count = pc.sum(pc.cast(gaps, "int64")).as_py()
        gap_ns = pc.sum(pc.if_else(gaps, delta, 0)).as_py()
        nonincreasing = pc.any(pc.less_equal(starts, prior_starts)).as_py()
        changes = pc.fill_null(pc.not_equal(table["contract_key"].slice(1), table["contract_key"].slice(0, n - 1)), False)
        roll_count = pc.sum(pc.cast(changes, "int64")).as_py()
    else:
        gap_count = gap_ns = roll_count = 0
        nonincreasing = False
    valid = pc.sum(pc.cast(table["valid"], "int64")).as_py() or 0
    return {"rows": table.num_rows,
            "first_start_ns": None if not table.num_rows else pc.min(table["start_ns"]).as_py(),
            "last_end_ns": None if not table.num_rows else pc.max(table["end_ns"]).as_py(),
            "last_known_at_ns": None if not table.num_rows else pc.max(table["known_at_ns"]).as_py(),
            "valid_rows": valid, "invalid_rows": n - valid, "strictly_time_ordered": not nonincreasing,
            "positive_interval_gap_count": gap_count, "total_between_row_gap_ns": gap_ns,
            "raw_contract_change_count": roll_count,
            "gap_scope": "Unobserved between-row intervals include scheduled closures; no inference of zero activity or venue status.",
            "raw_contracts": sorted(v for v in pc.unique(table["contract_key"]).to_pylist() if v is not None)}


def _definition_supplement(store, protocol, root, admission, *, remaining_bytes, snapshot_binding=None):
    """Publish actual source evidence; admit only the narrowly proved correction."""
    import pyarrow.compute as pc
    from trading_research.research.jumbo_definition_supersession import run_supersession_probe
    start = time.process_time()
    result = run_supersession_probe(store, protocol, root, admission, snapshot_binding=snapshot_binding)
    report = dict(result['report'])
    report.update(original_primary_rows=admission['primary_rows'],
                  original_valid_primary_rows=admission['valid_primary_rows'])
    table = result['corrected_table']
    output_bytes = 0
    if table is not None:
        source = [r for r in admission['partitions'] if r['root']=='NQ' and Path(r['source_path']).stem=='2024']
        if len(source) != 1:
            raise IntegrityError('one original admitted NQ2024 partition required')
        original = _read_table(store, source[0]['canonical_table'])
        allowed = {'contract_key', 'definition_version', 'known_at_ns', 'valid', 'reasons'}
        untouched = [name for name in original.column_names if name not in allowed]
        if (not original.schema.equals(table.schema) or original.num_rows != table.num_rows
                or not original.select(untouched).equals(table.select(untouched))):
            raise IntegrityError('source supplement changed observed prices, ordering, physical IDs or table schema')
        changed = pc.not_equal(original['valid'], table['valid'])
        expected = pc.fill_null(pc.and_(pc.equal(original['instrument_id'], 106364),
                   pc.and_(pc.equal(original['reasons'], 'ambiguous_definition'), table['valid'])), False)
        if pc.any(pc.and_(changed, pc.invert(expected))).as_py():
            raise IntegrityError('source supplement changed a different exclusion population')
        unmodified_rows = pc.invert(expected)
        if not original.filter(unmodified_rows).equals(table.filter(unmodified_rows)):
            raise IntegrityError('source supplement modified rows outside the exact original conflict')
        if (pc.any(pc.greater(table['known_at_ns'], _ns(protocol['frozen_available_cut_utc']))).as_py()
                or pc.any(pc.less(table['known_at_ns'], original['known_at_ns'])).as_py()):
            raise IntegrityError('source supplement moved availability backwards or beyond the admitted cut')
        ref = _put_table(store, table, kind='jumbo_nq2024_source_supersession_canonical_parquet_v1',
                         remaining_bytes=remaining_bytes)
        output_bytes += ref['size_bytes']
        before, after = _coverage(original), _coverage(table)
        report.update(status='actual_source_supersession_price_readmitted', actual_status='price_readmitted',
                 actual_accepted=True, original_canonical_table=source[0]['canonical_table'], corrected_canonical_table=ref,
                 original_coverage=before, corrected_coverage=after,
                 recovered_primary_minutes=after['valid_rows']-before['valid_rows'],
                 corrected_valid_primary_rows=admission['valid_primary_rows']+after['valid_rows']-before['valid_rows'],
                 original_admission_unchanged=True,
                 research_use='Explicit source sensitivity; original frozen population remains separately reproducible')
        del original
    report['cpu_seconds_internal'] = time.process_time()-start
    payload = canonical_json(report)
    if len(payload) > remaining_bytes-output_bytes:
        raise DependencyUnavailable('source supersession report exceeds remaining output allowance')
    ref = store.put_bytes(payload, kind='jumbo_actual_definition_supersession_report_v1')
    output_bytes += ref.size_bytes
    return {'report': report, 'artifact': asdict(ref), 'corrected_table': table, 'derived_output_bytes': output_bytes}


def _run_admission(packet, protocol, root, store):
    import pyarrow as pa
    import pyarrow.compute as pc
    pa.set_cpu_count(1)
    pa.set_io_thread_count(1)
    pilot = packet["mode"] == "pilot"
    previous = _predecessor(packet, root, store)
    if not pilot:
        estimate = previous["expansion_estimate"]
        if (not previous["success"] or not previous["reconciliation"]["success"]
                or estimate["within_declared_allowance"] is not True
                or estimate["remaining_cpu_seconds_conservative"] > protocol["resources"]["mode_cpu_seconds"]["admit"]):
            raise DependencyUnavailable("pilot does not establish declared full-admission feasibility")
    source_paths = protocol["pilot"]["ohlc_paths"] if pilot else protocol["ohlc_source_paths"]
    definitions = protocol["definition_source_paths"]
    if pilot:
        definitions = [p for p in definitions if int(Path(p).stem) in protocol["pilot"]["definition_years"][_root_of(p)]]
    data_root = root.parent / "data"
    metadata = {r["path"]: r for r in protocol["source_file_metadata"]}
    cut = _ns(protocol["frozen_available_cut_utc"])
    start = _ns(protocol["primary_start_date"] + "T00:00:00Z")
    # Physical file identity/size checks precede value reads in this worker.
    for p in [*source_paths, *definitions]:
        stat = (data_root / p).stat()
        if stat.st_size != metadata[p]["size_bytes"] or stat.st_mtime_ns != metadata[p]["mtime_ns"]:
            raise IntegrityError("declared original source metadata changed")
    results, definition_refs, reconciliation = [], {}, None
    prior_tables = {} if pilot else {r["source_path"]: r for r in previous["partitions"]}
    output_bytes = 0
    cpu_started = time.process_time()
    for instrument in protocol["roots"]:
        subset = [p for p in definitions if _root_of(p) == instrument]
        clock = time.process_time()
        index = read_definition_index([data_root / p for p in subset], data_root=data_root, root=instrument,
                                      maximum_rows=protocol["resources"]["maximum_definition_rows_per_root"])
        definition_cpu = time.process_time() - clock
        definition_ref = store.put_json(index.manifest, kind="jumbo_complete_definition_admission")
        definition_refs[instrument] = {"artifact": asdict(definition_ref), "cpu_seconds": definition_cpu,
                                       "source_files": subset, "source_rows": index.manifest["source_rows"],
                                       "indexed_records": index.manifest["indexed_records"],
                                       "unresolved_rows": index.manifest["unresolved_rows"]}
        output_bytes += definition_ref.size_bytes
        for p in [p for p in source_paths if _root_of(p) == instrument]:
            clock = time.process_time()
            reused = False
            previous_table = prior_tables.get(p)
            if previous_table:
                previous_defs = set(previous["definitions"][instrument]["source_files"])
                old_definitions = store.read_json(artifact_ref(previous["definitions"][instrument]["artifact"]))
                old_hashes = {f["source_path"]: f["source_sha256"] for f in old_definitions["files"]}
                current_hashes = {f["source_path"]: f["source_sha256"] for f in index.manifest["files"]}
                if any(current_hashes.get(p) != sha for p, sha in old_hashes.items()):
                    raise IntegrityError("a pilot definition source changed before full-cohort reuse")
                added = [r for r in index.records if r.source_path not in previous_defs]
                c = previous_table["primary_coverage"]
                # New reference facts may not change a reused bar's past
                # identity. An unresolved extra source prevents this proof.
                unresolved_extra = any(r["source_path"] not in previous_defs for r in index.manifest["unresolved"])
                changes_past = any(r.known_at_ns <= c["last_end_ns"] and r.valid_from_ns < c["last_end_ns"]
                                   and r.valid_until_ns > c["first_start_ns"] for r in added)
                if not unresolved_extra and not changes_past:
                    source_sha = hashlib.sha256((data_root / p).read_bytes()).hexdigest()
                    if source_sha != previous_table["source_sha256"]:
                        raise IntegrityError("pilot source bytes changed before full-cohort reuse")
                    table = _read_table(store, previous_table["canonical_table"])
                    manifest = store.read_json(artifact_ref(previous_table["admission_manifest"]))
                    reused = True
            if not reused:
                table, manifest = read_ohlc_partition(data_root / p, data_root=data_root, root=instrument,
                                                     definition_index=index,
                                                     maximum_rows=protocol["resources"]["maximum_rows_per_ohlc_file"],
                                                     maximum_file_bytes=protocol["resources"]["maximum_file_bytes"])
            full_coverage = _coverage(table)
            eligible = table.filter(pc.and_(pc.greater_equal(table["start_ns"], start), pc.less_equal(table["known_at_ns"], cut)))
            primary_coverage = _coverage(eligible)
            # Run the exact immutable index interface over every admitted row,
            # including quarantined slots; this does not certify each window.
            series = MinuteBars.from_table(eligible, source_version=digest({"source": manifest["source_sha256"], "admission": manifest}))
            del series
            if pilot and instrument == "NQ" and Path(p).stem == "2024":
                reconciliation = _reconcile(eligible, protocol, root, store)
            if reused:
                table_ref = previous_table["canonical_table"]
                manifest_ref = previous_table["admission_manifest"]
            else:
                table_ref = _put_table(store, table, kind="jumbo_canonical_ohlc_parquet",
                                       remaining_bytes=protocol["resources"]["maximum_derived_output_bytes"] - output_bytes)
                manifest_ref = asdict(store.put_json(manifest, kind="jumbo_complete_ohlc_admission"))
            output_bytes += table_ref["size_bytes"] + manifest_ref["size_bytes"]
            results.append({"root": instrument, "source_path": p, "source_sha256": manifest["source_sha256"],
                            "source_bytes": manifest["source_bytes"], "full_coverage": full_coverage,
                            "primary_coverage": primary_coverage, "excluded_by_period_or_available_cut": table.num_rows - eligible.num_rows,
                            "canonical_table": table_ref, "admission_manifest": manifest_ref,
                            "quality_counts": manifest["quality_counts"], "reused_pilot_admission": reused,
                            "cpu_seconds": time.process_time() - clock})
            print(json.dumps({"partition": p, "rows": table.num_rows, "valid_rows": primary_coverage["valid_rows"],
                              "reused": reused, "cpu_seconds": results[-1]["cpu_seconds"]}), flush=True)
            del table, eligible, manifest
            gc.collect()
    if not pilot:
        reconciliation = previous["reconciliation"]
    if reconciliation is None:
        raise IntegrityError("declared reconciliation partition was not processed")
    cpu = time.process_time() - cpu_started
    actual_source_bytes = sum(r["source_bytes"] for r in results)
    total_bytes = sum(metadata[p]["size_bytes"] for p in protocol["ohlc_source_paths"])
    remaining_ratio = max(0, total_bytes - actual_source_bytes) / actual_source_bytes
    conservative_cpu = cpu * remaining_ratio * 2.0 + 15.0
    expected_output = output_bytes * total_bytes / actual_source_bytes * 1.25
    return {"success": reconciliation["success"], "study_id": protocol["study_id"],
            "scope": "bounded full-partition admission pilot" if pilot else "full declared acquired-contract OHLC cohort admission",
            "economic_or_live_runs": 0, "model_fits": 0, "family_statistics_complete": False,
            "definitions": definition_refs, "partitions": results, "reconciliation": reconciliation,
            "primary_rows": sum(r["primary_coverage"]["rows"] for r in results),
            "valid_primary_rows": sum(r["primary_coverage"]["valid_rows"] for r in results),
            "derived_output_bytes": output_bytes, "cpu_seconds_internal": cpu,
            "expansion_estimate": {"basis": "actual full-partition pilot; remaining source-byte ratio x2 plus15CPU seconds; output x1.25",
                                   "remaining_cpu_seconds_conservative": conservative_cpu,
                                   "total_derived_bytes_conservative": expected_output,
                                   "memory_basis": "same sequential per-file admission, at most declared600000rows; root-level research indexing measured later",
                                   "within_declared_allowance": conservative_cpu <= protocol["resources"]["mode_cpu_seconds"]["admit"]
                                   and expected_output <= protocol["resources"]["maximum_derived_output_bytes"]},
            "coverage_limit": "Rows and partitions are admitted here. Complete formation/future windows, roll exclusions, statistics and predictive evidence are separate outputs."}


def _descriptive_confirmation_authorized(packet, predecessor):
    """Packet flag must match the exact loaded predecessor; it cannot open a model gate."""
    expected = (predecessor is not None
                and predecessor.get("success") is True
                and predecessor.get("mode") == "develop"
                and predecessor.get("phase") == "extract")
    flag = packet.get("descriptive_confirmation") is True
    if flag is not expected:
        raise IntegrityError("descriptive_confirmation does not match the exact predecessor")
    return expected


def _admission_from_extract(extract_worker, root, store):
    identity = extract_worker.get("admission_predecessor")
    if identity is None:
        raise IntegrityError("extract predecessor lacks admission_predecessor")
    raw = (root / identity["path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != identity["sha256"]:
        raise IntegrityError("admission predecessor identity changed")
    execution = json.loads(raw)
    if execution.get("success") is not True:
        raise IntegrityError("admission predecessor was not successful")
    if execution.get("mode") != "admit":
        raise IntegrityError("admission predecessor mode differs")
    phase = execution.get("phase")
    if phase is not None and phase != "full_admission":
        raise IntegrityError("admission predecessor phase differs")
    admitted = store.read_json(artifact_ref(execution["worker_report"]))
    if admitted.get("mode") != "admit" or admitted.get("success") is not True:
        raise IntegrityError("admission worker is not a successful admit report")
    return admitted


def _source_supplement_from_extract(extract_worker, store):
    ref = extract_worker.get("source_supersession")
    if not ref:
        raise IntegrityError("extract predecessor lacks source_supersession")
    if ref.get("kind") != "jumbo_actual_definition_supersession_report_v1":
        raise IntegrityError("source supersession kind differs")
    report = store.read_json(artifact_ref(ref))
    if report.get("actual_accepted") is not True:
        raise IntegrityError("source supersession was not actually accepted")
    return ref


def _descriptive_confirmation_report(extracted, packet, predecessor):
    if extracted.get('success') is not True or extracted.get('model_fits') != 0:
        raise IntegrityError('descriptive confirmation did not complete without model fitting')
    result = dict(extracted)
    result.update(
        mode=packet["mode"], phase=packet["phase"], descriptive_confirmation=True,
        development_predecessor=packet["predecessor"],
        admission_predecessor=predecessor.get("admission_predecessor"),
        family_statistics_complete=False, model_fits=0,
        context_models_complete=False, location_quality_complete=False,
        scope="Complete declared heldout descriptive extraction; Context and Location scoring remain later",
        remaining=["Pooled training/development phase objects and year-to-year stability remain for later supervisor assessment of the complete catalogue",
                   "Ordinary/event-day and width-regime timing comparisons when those labels exist",
                   "Chronological independent model comparisons, calibration and incremental information",
                   "Full conditional range/internal/extension/statistical Location catalogue quality",
                   "Exact unresolved source formulas retain their separately evidenced dependencies; generic ranges do not close them"])
    return result


def run(packet, protocol, root):
    store = ArtifactStore(root / "evidence/trials/artifacts")
    if packet["mode"] in ("pilot", "admit"):
        return _run_admission(packet, protocol, root, store)
    if packet["mode"] == "develop" and packet["phase"] == "extract":
        return _run_extraction(packet, protocol, root, store)
    if packet["mode"] == "develop" and packet["phase"] == "fit":
        from trading_research.research.jumbo_pipeline import run_fit
        return run_fit(packet, protocol, root, store)
    if packet["mode"] == "confirm":
        predecessor = _predecessor(packet, root, store)
        if _descriptive_confirmation_authorized(packet, predecessor):
            admitted = _admission_from_extract(predecessor, root, store)
            supplement = _source_supplement_from_extract(predecessor, store)
            extracted = _run_extraction(packet, protocol, root, store, admitted=admitted,
                                        heldout=True, frozen_source_supplement=supplement)
            return _descriptive_confirmation_report(extracted, packet, predecessor)
        from trading_research.research.jumbo_pipeline import run_confirmation
        return run_confirmation(packet, protocol, root, store)
    raise DependencyUnavailable("undeclared registered research mode/phase")


def encoded_checkpoint(record):
    return (json.dumps(record, indent=2, sort_keys=True, allow_nan=False)+"\n").encode()


def _rows_table(rows, *, kind):
    """Use the fixed nullable schema, including initially missing columns."""
    import pyarrow as pa
    from trading_research.research.jumbo_tables import table_schema
    if not rows:
        raise ContractError("an intended output table must have actual rows")
    schema = table_schema(kind)
    if {key for row in rows for key in row} - set(schema.names):
        raise ContractError("new fields require an explicit research table schema version")
    return pa.Table.from_pylist(rows, schema=schema)


def _run_extraction(packet, protocol, root, store, *, admitted=None, heldout=False, frozen_source_supplement=None):
    import pyarrow as pa
    import pyarrow.compute as pc
    from trading_research.foundations.cash_calendar import CashCalendar
    from trading_research.research.jumbo_report import year_statistics
    from trading_research.research.jumbo_tables import FEATURES, VERSION, cash_dates, extract_dates
    from trading_research.research.jumbo_checkpoints import checked_checkpoints, _file
    pa.set_cpu_count(1)
    pa.set_io_thread_count(1)
    plan = store.read_json(artifact_ref(packet["analysis_plan"]))
    execution = store.read_json(artifact_ref(packet["execution_plan"]))
    if plan["same_registered_family"] != protocol["family"]:
        raise IntegrityError("analysis plan changed the registered family")
    admission = _predecessor(packet, root, store) if admitted is None else admitted
    if (admission.get("mode") != "admit" or admission.get("success") is not True
            or len(admission["partitions"]) != len(protocol["ohlc_source_paths"])
            or {r["source_path"] for r in admission["partitions"]} != set(protocol["ohlc_source_paths"])):
        raise IntegrityError("full declared source admission required for extraction")
    source_resolution = None
    if heldout and frozen_source_supplement is not None:
        resolution = store.read_json(artifact_ref(frozen_source_supplement))
        if resolution.get('actual_accepted') is True:
            parts = [dict(p) for p in admission['partitions']]
            affected = [p for p in parts if p['root']=='NQ' and Path(p['source_path']).stem=='2024']
            if len(affected)!=1 or affected[0]['canonical_table']!=resolution['original_canonical_table']:
                raise IntegrityError('heldout warmup source correction differs from frozen original admission')
            affected[0]['canonical_table'] = resolution['corrected_canonical_table']
            affected[0]['primary_coverage'] = resolution['corrected_coverage']
            admission = {**admission, 'partitions':parts,
                         'valid_primary_rows':resolution['corrected_valid_primary_rows']}
        source_resolution = {'report':resolution, 'artifact':frozen_source_supplement, 'derived_output_bytes':0}
    calendar = CashCalendar(root / protocol["calendar_path"])
    first = date.fromisoformat(protocol["primary_start_date"])
    if heldout:
        if packet["mode"] != "confirm" or packet["phase"] != "confirmation":
            raise IntegrityError("heldout outcomes require the registered confirmation mode")
        last_end = max(p["primary_coverage"]["last_end_ns"] for p in admission["partitions"])
        last = datetime.fromtimestamp(last_end // 1_000_000_000, tz=timezone.utc).date()
        evaluation_cut = _ns(protocol["frozen_available_cut_utc"])
        emit_first = date(2025, 1, 1)
        if last < emit_first or last > datetime.fromtimestamp(evaluation_cut // 1_000_000_000, tz=timezone.utc).date():
            raise IntegrityError("actual admitted endpoint is outside the frozen heldout period")
    else:
        last = date.fromisoformat(plan["chronology"]["extract_development_last_date"])
        if first.isoformat() != "2020-01-01" or last.isoformat() != "2024-12-31":
            raise IntegrityError("development extraction may not inspect heldout target outcomes")
        evaluation_cut = _ns("2025-01-01T00:00:00Z")
        emit_first = first
    dates = cash_dates(calendar, first, last)
    retained = {} if heldout else checked_checkpoints(packet, protocol, root, store)
    annual_dates = {year: [cash.day.isoformat() for cash in dates if cash.day.year == year]
                    for year in range(first.year, last.year + 1)}
    output_bytes, shards, profiles, sensitivity_shards = 0, [], [], []
    run_cpu = time.process_time()
    if not heldout:
        from trading_research.research.jumbo_source_reuse import source_supplement
        source_resolution = source_supplement(packet, protocol, root, store, admission,
                              remaining_bytes=protocol['resources']['maximum_derived_output_bytes'])
        output_bytes += source_resolution['derived_output_bytes']
        print(json.dumps({'stage':'actual_definition_supersession', 'status':source_resolution['report']['actual_status'],
                          'accepted':source_resolution['report']['actual_accepted'],
                          'recovered_primary_minutes':source_resolution['report'].get('recovered_primary_minutes',0),
                          'source_report':source_resolution['artifact']}), flush=True)
    total_rows = Counter()
    index_preflight = None
    for instrument in protocol["roots"]:
        clock = time.process_time()
        sources = [r for r in admission["partitions"] if r["root"] == instrument and first.year <= int(Path(r["source_path"]).stem) <= last.year]
        sources.sort(key=lambda r: r["source_path"])
        planned_rows = sum(r["canonical_table"]["rows"] for r in sources)
        if len(sources) != last.year-first.year+1 or planned_rows > 3_000_000:
            raise DependencyUnavailable("declared combined development root exceeds bounded index domain")
        source_version = digest({"table_definition": VERSION, "sources": [r["canonical_table"] for r in sources],
                                 "period_start": first.isoformat(), "period_end": last.isoformat(), "available_cut": evaluation_cut,
                                 "calendar_version": calendar.version, "analysis_plan": packet["analysis_plan"],
                                 "clock_recipes": protocol["clock_recipes"]})
        reused_years = sorted(y for r, y in retained if r == instrument)
        if reused_years != list(range(first.year, first.year + len(reused_years))):
            raise IntegrityError("continuation requires a complete prefix of retained annual checkpoints")
        for year in reused_years:
            reused = retained[(instrument, year)]
            record = reused["record"]
            if (record["source_version"] != source_version
                    or record["canonical_sources"] != [r["canonical_table"] for r in sources]
                    or record["intended_cash_dates"] != len(annual_dates[year])):
                raise IntegrityError("retained annual checkpoint changed source/analysis/date identity")
            record = {**record, "reused_from": {k: reused[k] for k in ("checkpoint", "original_attempt_id")}}
            payload = (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
            retained_bytes = sum(v["size_bytes"] for v in (*record["tables"].values(), record["statistics"]))
            if retained_bytes + len(payload) > protocol["resources"]["maximum_derived_output_bytes"] - output_bytes:
                raise DependencyUnavailable("reused artifacts exceed the unchanged aggregate output allowance")
            output_bytes += retained_bytes
            total_rows.update({name: ref["rows"] for name, ref in record["tables"].items()})
            shards.append(record)
            print(json.dumps({"root": instrument, "year": year, "stage": "verified_checkpoint_reuse",
                              "original_attempt_id": reused["original_attempt_id"], "counted_output_bytes": retained_bytes}), flush=True)
        first_missing_year = max(emit_first.year, first.year + len(reused_years))
        if first_missing_year > last.year:
            continue
        # Profile an actual, previously admitted annual partition before the
        # larger root-level representation. Admission's reader cost is not
        # substituted for this different array/list/index memory footprint.
        if index_preflight is None:
            baseline_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
            pilot_clock = time.process_time()
            pilot_table = _read_table(store, sources[0]["canonical_table"])
            pilot_index = MinuteBars.from_table(pilot_table, source_version=digest(sources[0]["canonical_table"]))
            index_preflight = {"pilot_root": instrument, "pilot_rows": pilot_table.num_rows,
                               "pilot_table": sources[0]["canonical_table"], "baseline_rss_bytes": baseline_rss,
                               "pilot_cpu_seconds": time.process_time() - pilot_clock,
                               "pilot_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}
            del pilot_index, pilot_table
            gc.collect()
            pa.default_memory_pool().release_unused()
        if any(r["canonical_table"]["schema_sha256"] != index_preflight["pilot_table"]["schema_sha256"] for r in sources):
            raise DependencyUnavailable("root index schema differs from its measured pilot")
        ratio = planned_rows / index_preflight["pilot_rows"]
        baseline_rss = index_preflight["baseline_rss_bytes"]
        conservative_rss = int(baseline_rss + max(0, index_preflight["pilot_peak_rss_bytes"] - baseline_rss) * ratio * 1.5 + 256 * 1024 * 1024)
        profiles.append({"root": instrument, "stage": "actual_index_preflight" if instrument == index_preflight["pilot_root"] else "same_schema_index_preflight_reuse",
                         **index_preflight, "planned_rows": planned_rows,
                         "root_index_cpu_seconds_conservative": index_preflight["pilot_cpu_seconds"] * ratio * 2,
                         "root_index_rss_bytes_conservative": conservative_rss,
                         "estimate_rule": "Observed first annual-index incremental RSS x row ratio x1.5 plus baseline and256MiB; CPU x row ratio x2. Reused only for identical schema and same sequential index algorithm. Actual worker caps remain binding."})
        print(json.dumps(profiles[-1]), flush=True)
        if conservative_rss > protocol["resources"]["memory_bytes"]:
            raise DependencyUnavailable("actual index pilot does not establish full-root memory feasibility")
        tables = [_read_table(store, r["canonical_table"]) for r in sources]
        table = pa.concat_tables(tables)
        del tables
        table = table.filter(pc.and_(pc.greater_equal(table["start_ns"], _ns("2020-01-01T00:00:00Z")),
                                    pc.less_equal(table["known_at_ns"], evaluation_cut)))
        series = MinuteBars.from_table(table, source_version=source_version, maximum_rows=3_000_000)
        indexed_rows = table.num_rows
        del table
        gc.collect()
        profiles.append({"root": instrument, "stage": "index", "source_tables": len(sources),
                         "indexed_rows": indexed_rows, "cpu_seconds": time.process_time() - clock})
        print(json.dumps(profiles[-1]), flush=True)
        for reused_record in [s for s in shards if s["root"] == instrument and s["year"] in reused_years]:
            output_bytes += _attach_anchors(series, reused_record, store, packet, protocol,
                              remaining_bytes=protocol["resources"]["maximum_derived_output_bytes"]-output_bytes)
            payload = encoded_checkpoint(reused_record)
            if len(payload) > protocol["resources"]["maximum_derived_output_bytes"]-output_bytes:
                raise DependencyUnavailable("supplemented checkpoint exceeds aggregate output allowance")
            publish_new(Path(packet["worker_report"]).parent / f"{instrument}-{reused_record['year']}-shard.json", payload)
            output_bytes += len(payload)
        batch = {"formations": [], "paths": [], "specials": []}
        year = first_missing_year
        year_cpu = time.process_time()
        def finish_year(year, batch, year_cpu, *, sensitivity=False, canonical_sources=None):
            nonlocal output_bytes
            tables_out = {}
            for name in batch:
                tables_out[name] = _put_table(store, _rows_table(batch[name], kind=name),
                    kind="jumbo_" + name + "_parquet_v1",
                    remaining_bytes=protocol["resources"]["maximum_derived_output_bytes"] - output_bytes)
                output_bytes += tables_out[name]["size_bytes"]
                if not sensitivity:
                    total_rows[name] += len(batch[name])
            statistics_cpu = time.process_time()
            statistics = year_statistics(batch, tuple(annual_dates[year]), plan=plan)
            stats_ref = _put_statistics(store, statistics,
                             remaining_bytes=protocol["resources"]["maximum_derived_output_bytes"]-output_bytes)
            output_bytes += stats_ref["size_bytes"]
            record = {"root": instrument, "year": year, "intended_cash_dates": len(annual_dates[year]),
                      "source_version": source_version, "canonical_sources": canonical_sources or [r["canonical_table"] for r in sources],
                      "tables": tables_out, "statistics": stats_ref,
                      "statistics_cpu_seconds": time.process_time() - statistics_cpu,
                      "year_cpu_seconds": time.process_time() - year_cpu}
            output_bytes += _attach_anchors(series, record, store, packet, protocol,
                              formation_rows=batch["formations"], path_rows=batch["paths"],
                              remaining_bytes=protocol["resources"]["maximum_derived_output_bytes"]-output_bytes)
            if sensitivity:
                record['source_supersession'] = source_resolution['artifact']
                record['population_role'] = 'Source-corrected NQ2024; primary Context cohort after verified resolution; original shard retained'
                sensitivity_shards.append(record)
            else:
                shards.append(record)
            # Retain an immutable usable checkpoint even if a later bounded
            # stage fails; a partial shard is never whole-family completion.
            checkpoint_payload = (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
            if len(checkpoint_payload) > protocol["resources"]["maximum_derived_output_bytes"] - output_bytes:
                raise DependencyUnavailable("checkpoint exceeds remaining aggregate output allowance")
            suffix = '-source-supersession' if sensitivity else ''
            publish_new(Path(packet["worker_report"]).parent / f"{instrument}-{year}{suffix}-shard.json", checkpoint_payload)
            output_bytes += len(checkpoint_payload)
            print(json.dumps({"root": instrument, "year": year, "tables": {k: v["rows"] for k, v in tables_out.items()},
                              "cpu_seconds": record["year_cpu_seconds"], "statistics_cpu_seconds": record["statistics_cpu_seconds"],
                              "output_bytes": output_bytes}), flush=True)
        count, sample_cpu = 0, time.process_time()
        for result in extract_dates(series, dates, root=instrument, recipes=protocol["clock_recipes"],
                                    plan=plan, evaluation_cut=evaluation_cut,
                                    emit_first_date=date(first_missing_year, 1, 1)):
            current_year = result["cash_date"].day.year
            if current_year != year:
                finish_year(year, batch, year_cpu)
                batch = {"formations": [], "paths": [], "specials": []}
                year, year_cpu = current_year, time.process_time()
                gc.collect()
            for name in batch:
                batch[name].extend(result[name])
            count += 1
            if count == 30:
                cpu = time.process_time() - sample_cpu
                estimate = cpu / count * sum(c.day.year >= first_missing_year for c in dates)
                profiles.append({"root": instrument, "stage": "first_30_actual_dates", "dates": count,
                                 "cpu_seconds": cpu, "estimated_root_extraction_cpu_seconds": estimate,
                                 "scope": "Actual extraction only; yearly statistics measured and reported separately."})
                print(json.dumps(profiles[-1]), flush=True)
        finish_year(year, batch, year_cpu)
        del series, batch
        gc.collect()
        if (not heldout and instrument=='NQ' and source_resolution['report'].get('actual_accepted') is True):
            clock = time.process_time()
            corrected = source_resolution.pop('corrected_table')
            corrected_ref = source_resolution['report']['corrected_canonical_table']
            refs = [corrected_ref if Path(r['source_path']).stem=='2024' else r['canonical_table'] for r in sources]
            tables = [corrected if Path(r['source_path']).stem=='2024' else _read_table(store,r['canonical_table']) for r in sources]
            source_version = digest({'original_source_version':source_version, 'canonical_sources':refs,
                                     'verified_source_supersession':source_resolution['artifact']})
            series = MinuteBars.from_table(pa.concat_tables(tables), source_version=source_version, maximum_rows=3_000_000)
            del corrected, tables
            batch = {'formations':[], 'paths':[], 'specials':[]}
            for value in extract_dates(series, dates, root=instrument, recipes=protocol['clock_recipes'],
                                       plan=plan, evaluation_cut=evaluation_cut, emit_first_date=date(2024,1,1)):
                for name in batch:
                    batch[name].extend(value[name])
            finish_year(2024, batch, clock, sensitivity=True, canonical_sources=refs)
            del series, batch
            gc.collect()
    if {(s["root"], s["year"]) for s in shards} != {(r, y) for r in protocol["roots"] for y in range(emit_first.year, last.year+1)}:
        raise IntegrityError("declared development cohort did not complete")
    from trading_research.research.jumbo_narrative import descriptive_report
    narrative_payload = descriptive_report(shards, store, protocol=protocol, analysis_plan=plan,
                            stage="confirmation" if heldout else "development", supplements=("exact per-row anchor and named range relationships",)).encode()
    if 2 * len(narrative_payload) > protocol["resources"]["maximum_derived_output_bytes"] - output_bytes:
        raise DependencyUnavailable("aggregate extraction output exceeded declared allowance")
    narrative_ref = store.put_bytes(narrative_payload, kind="jumbo_development_report_markdown_v1")
    output_bytes += 2 * narrative_ref.size_bytes
    publish_new(Path(packet["worker_report"]).parent / "report.md", store.read(narrative_ref))
    sensitivity_narrative_ref = None
    if sensitivity_shards:
        payload = descriptive_report(sensitivity_shards, store, protocol=protocol, analysis_plan=plan,
                      stage='development', supplements=('Actual source-supersession cohort; original NQ2024 exclusions and report remain separately available',)).encode()
        if 2*len(payload) > protocol['resources']['maximum_derived_output_bytes']-output_bytes:
            raise DependencyUnavailable('source-correction narrative exceeds aggregate output allowance')
        sensitivity_narrative_ref = store.put_bytes(payload,kind='jumbo_source_corrected_development_report_markdown_v1')
        publish_new(Path(packet['worker_report']).parent/'source-supersession-report.md',payload)
        output_bytes += 2*len(payload)
    by_key = {(s['root'],s['year']):s for s in shards}
    by_key.update({(s['root'],s['year']):s for s in sensitivity_shards})
    return {"success": True, "study_id": protocol["study_id"], "table_version": VERSION,
            "scope": "Complete declared heldout extraction" if heldout else "Complete declared training/development extraction and per-year descriptive statistics",
            "first_date": emit_first.isoformat(), "last_date": last.isoformat(), "available_cut_ns": evaluation_cut,
            "intended_cash_dates_per_root": sum(c.day >= emit_first for c in dates), "roots": protocol["roots"], "source_clock_count": 69,
            "analysis_plan": packet["analysis_plan"], "admission_predecessor": packet["predecessor"] if not heldout else None,
            "admission_manifest": {"attempt_id":admission["attempt_id"],"partitions":admission["partitions"]},
            "shards": shards, "row_counts": dict(total_rows), "profiles": profiles,
            'source_supersession':None if source_resolution is None else source_resolution['artifact'],
            'source_supersession_summary':None if source_resolution is None else source_resolution['report'],
            'source_sensitivity_shards':sensitivity_shards, 'model_shards':[by_key[k] for k in sorted(by_key)],
            'source_sensitivity_narrative':None if sensitivity_narrative_ref is None else asdict(sensitivity_narrative_ref),
            "reused_completed_annual_shards": len(retained),
            "narrative": asdict(narrative_ref), "derived_output_bytes": output_bytes,
            "cpu_seconds_internal": time.process_time() - run_cpu,
            "causal_feature_columns": ["x_" + name for name in FEATURES],
            "model_fits": 0, "economic_or_live_runs": 0,
            "heldout_target_rows_inspected": int(total_rows["paths"]) if heldout else 0, "family_statistics_complete": False,
            "context_models_complete": False, "location_quality_complete": False,
            "remaining": ["Chronological independent model comparisons, calibration and incremental information",
                          "Heldout2025 onward confirmation after model/selection freeze",
                          "Full conditional range/internal/extension/statistical Location catalogue quality",
                          "Exact unresolved source formulas retain their separately evidenced dependencies; generic ranges do not close them"]}
