"""Bounded full-window MBP-T/standalone reconciliation preserving multiplicity."""

from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import resource
import struct
import time

from trading_research.data.events import Flags
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.foundations.time import datetime_ns, NS
from trading_research.operations.artifacts import code_manifest, code_snapshot, digest
from trading_research.operations.trials import TrialRegistry


DATASETS = tuple(f"quantpad/cme__{root}-continuous-futures__{schema}" for root in ("nq", "es") for schema in ("mbp-1", "trades"))
WINDOWS = (
    ("NQ", "2021-09-01T18:00:00+00:00"),
    ("NQ", "2022-03-10T14:30:00+00:00"),
    ("NQ", "2023-11-24T17:00:00+00:00"),
    ("NQ", "2024-03-11T13:30:00+00:00"),
    ("NQ", "2025-09-18T13:30:00+00:00"),
    ("ES", "2020-01-01T23:00:00+00:00"),
    ("ES", "2022-03-10T14:30:00+00:00"),
    ("ES", "2024-03-11T13:30:00+00:00"),
)


def footer_index(data_root: Path, *, datasets=DATASETS, max_files=500) -> dict:
    import pyarrow.parquet as pq
    data_root = data_root.resolve()
    index, files = {}, 0
    for id in datasets:
        directory = (data_root / id).resolve()
        if not directory.is_relative_to(data_root):
            raise ContractError("source path escapes the admitted data root")
        records = []
        for path in sorted(directory.glob("*.parquet")):
            if not path.resolve().is_relative_to(data_root):
                raise ContractError("source file resolves outside the admitted data root")
            files += 1
            if files > max_files:
                raise ContractError("registered footer count bound exceeded")
            before = path.stat()
            pf = pq.ParquetFile(path)
            if "t" not in pf.schema_arrow.names or str(pf.schema_arrow.field("t").type) != "int64":
                raise DependencyUnavailable("source timestamp schema is not the documented nanosecond export")
            col = pf.schema_arrow.names.index("t")
            groups = []
            for g in range(pf.num_row_groups):
                rg = pf.metadata.row_group(g)
                stat = rg.column(col).statistics
                groups.append({"group":g,"rows":rg.num_rows,"minimum":stat.min if stat and stat.has_min_max else None,
                               "maximum":stat.max if stat and stat.has_min_max else None,
                               "null_count":stat.null_count if stat else None})
            after = path.stat()
            if (before.st_size,before.st_mtime_ns) != (after.st_size,after.st_mtime_ns):
                raise IntegrityError("input file changed during metadata indexing")
            records.append({"path":str(path.relative_to(data_root)), "bytes":before.st_size,"mtime_ns":before.st_mtime_ns,
                            "rows":pf.metadata.num_rows,"schema":str(pf.schema_arrow),"fields":pf.schema_arrow.names,
                            "groups":groups,"identity_basis":"metadata only; selected-window raw bytes hashed separately"})
        index[id] = records
    return {"schema":"quantpad-four-dataset-footer-index-v1", "files":files,"datasets":index}


def select_groups(index: dict, *, dataset: str, start: int, end: int, max_scan_rows: int):
    if end <= start:
        raise ContractError("window must be nonempty and half-open")
    result, rows = [], 0
    for p in index["datasets"][dataset]:
        # Missing footer bounds cannot be interpreted as an empty file.
        if any(g["minimum"] is None or g["maximum"] is None for g in p["groups"]):
            raise DependencyUnavailable(f"missing time statistics requires a separately bounded scan: {p['path']}")
        groups = [g for g in p["groups"] if g["minimum"] < end and g["maximum"] >= start]
        if groups:
            rows += sum(g["rows"] for g in groups)
            result.append((p, [g["group"] for g in groups]))
    if rows > max_scan_rows:
        raise ContractError(f"registered physical scan bound exceeded: {rows} > {max_scan_rows}")
    return result, rows


def semantic_key(row: dict, *, side: bool = True):
    if not isinstance(row["price"], float):
        raise ContractError("expected the preserved QuantPad float64 price field")
    return (row["t"], row["instrument_id"], struct.pack(">d", row["price"]).hex(), row["size"], *([row["side"]] if side else []))


def compare_multisets(mbp: Counter, standalone: Counter) -> dict:
    matched = sum((mbp & standalone).values())
    m_base, s_base = Counter(), Counter()
    for key, count in mbp.items():
        m_base[key[:-1]] += count
    for key, count in standalone.items():
        s_base[key[:-1]] += count
    return {"mbp_trade_rows":sum(mbp.values()), "standalone_trade_rows":sum(standalone.values()),
            "matched_rows":matched, "extra_mbp_rows":sum((mbp-standalone).values()),
            "extra_standalone_rows":sum((standalone-mbp).values()),
            "side_mismatch_rows":sum((m_base & s_base).values())-matched,
            "mbp_duplicate_economic_keys":sum(n-1 for n in mbp.values() if n>1),
            "standalone_duplicate_economic_keys":sum(n-1 for n in standalone.values() if n>1),
            "mbp_volume":sum(key[3]*n for key,n in mbp.items()),
            "standalone_volume":sum(key[3]*n for key,n in standalone.items()),
            "mbp_signed_volume":sum(({"B":1,"A":-1}.get(key[4],0))*key[3]*n for key,n in mbp.items()),
            "mbp_unknown_volume":sum(key[3]*n for key,n in mbp.items() if key[4] not in {"A","B"}),
            "exact_multiset_match":mbp==standalone,
            "mismatch_examples":{"mbp":[[list(k),n] for k,n in list((mbp-standalone).items())[:5]],
                                 "standalone":[[list(k),n] for k,n in list((standalone-mbp).items())[:5]]}}


def read_window(data_root: Path, index: dict, *, dataset: str, start: int, end: int, max_scan_rows: int) -> dict:
    import pyarrow as pa
    import pyarrow.compute as pc
    import pyarrow.parquet as pq
    selection, expected_scan = select_groups(index,dataset=dataset,start=start,end=end,max_scan_rows=max_scan_rows)
    stream, flags, sides, actions = Counter(), Counter(), Counter(), Counter()
    checksum = hashlib.sha256()
    scanned = kept = t_without_last = gap_rows = snapshot_trade_rows = invalid_prices = crossed = nulls = 0
    source_refs = []
    minimum = maximum = prior_at = None
    decreases = 0
    physical_time_nulls = 0
    for record, groups in selection:
        path = data_root / record["path"]
        if not path.resolve().is_relative_to(data_root.resolve()):
            raise ContractError("indexed source file escapes the admitted data root")
        before = path.stat()
        if (before.st_size,before.st_mtime_ns)!=(record["bytes"],record["mtime_ns"]):
            raise IntegrityError("indexed source changed before scanning")
        pf = pq.ParquetFile(path)
        required = {"t","price","size","side","flags","instrument_id"}
        if not required.issubset(pf.schema_arrow.names):
            raise DependencyUnavailable("full trade semantics absent from source")
        for batch in pf.iter_batches(batch_size=65536,row_groups=groups,use_threads=False):
            scanned += batch.num_rows
            clock = batch.column(batch.schema.get_field_index("t"))
            physical_time_nulls += clock.null_count
            keep = pc.and_(pc.greater_equal(clock,start),pc.less(clock,end))
            selected = batch.filter(keep)
            if not selected.num_rows:
                continue
            kept += selected.num_rows
            # Preserve every supplied column and physical type in the window hash.
            sink = pa.BufferOutputStream()
            with pa.ipc.new_stream(sink, selected.schema) as writer:
                writer.write_batch(selected)
            raw = sink.getvalue()
            checksum.update(len(raw).to_bytes(8,"big")); checksum.update(raw)
            names = selected.schema.names
            times = selected.column(names.index("t")).to_pylist()
            if prior_at is not None and times[0] < prior_at:
                decreases += 1
            decreases += sum(b<a for a,b in zip(times,times[1:]))
            prior_at = times[-1]
            minimum = min(times) if minimum is None else min(minimum,min(times))
            maximum = max(times) if maximum is None else max(maximum,max(times))
            flag_values = selected.column(names.index("flags")).to_pylist()
            if any(f is None or not 0 <= f <= 255 for f in flag_values):
                raise IntegrityError("source flags do not fit the documented uint8 bitset")
            flags.update(flag_values)
            gap_rows += sum(bool(f & int(Flags.MAYBE_BAD_BOOK)) for f in flag_values)
            nulls += sum(c.null_count for c in selected.columns)
            if "bid_px" in names:
                crossed += pc.sum(pc.greater(selected.column(names.index("bid_px")),selected.column(names.index("ask_px")))).as_py() or 0
            if "action" in names:
                actions.update(selected.column(names.index("action")).to_pylist())
                selected = selected.filter(pc.equal(selected.column(names.index("action")),"T"))
            for row in selected.to_pylist():
                if row["flags"] & int(Flags.SNAPSHOT):
                    snapshot_trade_rows += 1
                    continue
                if row["size"] is None or row["size"] <= 0:
                    raise IntegrityError("trade has invalid event size")
                if row["price"] is None or not math.isfinite(row["price"]):
                    invalid_prices += 1
                if row["price"] is None:
                    raise IntegrityError("unpriced trade cannot enter exact float-bit price reconciliation")
                if not row["flags"] & int(Flags.LAST):
                    t_without_last += 1
                sides[row["side"]] += row["size"]
                stream[semantic_key(row)] += 1
        after = path.stat()
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
            raise IntegrityError("input changed while reading complete selected window")
        source_refs.append({"path":record["path"],"row_groups":groups,"metadata_version":digest(record)})
    if scanned != expected_scan:
        raise IntegrityError("selected row-group scan count disagrees with footer")
    return {"dataset":dataset,"counter":stream,"physical_rows_scanned":scanned,"selected_rows":kept,
            "trade_rows_without_last":t_without_last,"gap_flag_rows":gap_rows,"snapshot_trade_rows_excluded":snapshot_trade_rows,
            "invalid_trade_prices":invalid_prices,"crossed_quote_rows":crossed,"null_cells":nulls,"time_decreases":decreases,
            "flag_cohorts":{str(k):v for k,v in flags.items()},"side_volume":{str(k):v for k,v in sides.items()},
            "actions":{str(k):v for k,v in actions.items()},"physical_timestamp_nulls":physical_time_nulls,
            "first_event_at":minimum,"last_event_at":maximum,
            "selected_all_field_arrow_stream_hash":checksum.hexdigest(),"source_refs":source_refs,
            "complete_selected_row_groups":True,"source_clock_basis":"event timestamps; actual strategy receipt not supplied"}


def run_reconciliation(*, data_root: Path, package_root: Path, output_root: Path) -> dict:
    registry = TrialRegistry(output_root)
    family = "B01-complete-window-trade-reconciliation-v1"
    registry.register_family(family,scope_ids=("B01.4","B01.5","F01.DECODER","F05.CROSS_VENDOR"),
                             protocol={"windows":WINDOWS,"duration_seconds":3600,"maximum_footer_files":500,
                                       "maximum_physical_rows_per_dataset_window":4_000_000,"batch_rows":65536,
                                       "full_schema_required":True,"price_equality":"preserved float64 bits",
                                       "multiplicity":"exact Counter, no deduplication by economic key",
                                       "economic_evaluation":False},max_attempts=4,cpu_budget_seconds=1200)
    snapshot = code_snapshot(package_root,registry.artifacts)
    cpu, wall = time.process_time(),time.monotonic()
    index = footer_index(data_root)
    index_ref = registry.artifacts.put_json(index,kind="four_dataset_full_footer_index")
    trial = registry.register(name="Eight fixed one-hour trade reconciliation cohorts",family=family,stage="engineering",
                              configuration={"windows":WINDOWS,"duration_seconds":3600},code_hash=digest(code_manifest(package_root)),
                              data_hashes={"footer_index":index_ref.sha256},fold_version="no-fit-engineering",
                              target_version="exact-tape-multiset-reconciliation-v1")
    attempt = registry.start(trial,cpu_reservation_seconds=300)
    reports = []
    try:
        for root,start_text in WINDOWS:
            start = datetime_ns(datetime.fromisoformat(start_text)); end = start+3600*NS
            a_id,b_id = (f"quantpad/cme__{root.lower()}-continuous-futures__{s}" for s in ("mbp-1","trades"))
            parts = [read_window(data_root,index,dataset=d,start=start,end=end,max_scan_rows=4_000_000) for d in (a_id,b_id)]
            comparison = compare_multisets(parts[0].pop("counter"),parts[1].pop("counter"))
            reports.append({"root":root,"start":start_text,"end_at":end,"parts":parts,**comparison,
                            "nonempty_paired_window":comparison["mbp_trade_rows"]>0 and comparison["standalone_trade_rows"]>0,
                            "scope":"complete selected UTC hour, conditional on supplied files; not a calendar/session, broker, recovery or full-history certification"})
        report = {"success":True,"all_observed_windows_match":all(r["exact_multiset_match"] for r in reports),
                  "nonempty_paired_windows":sum(r["nonempty_paired_window"] for r in reports),
                  "trial_id":trial,"attempt_id":attempt,"index_artifact":asdict(index_ref),"code_snapshot":asdict(snapshot),
                  "cohorts":reports,"cpu_seconds":time.process_time()-cpu,"wall_seconds":time.monotonic()-wall,
                  "peak_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                  "economic_runs":0,"models_fitted":0,
                  "limitations":["Missing or extra prints are diagnostic outcomes; successful audit execution does not mean certified equality.",
                                 "A matching empty pair does not establish coverage; source bounds and selected row counts remain explicit.",
                                 "Raw gap/crossed/snapshot cohorts are retained and do not acquire book recovery from volume equality.",
                                 "UTC cohort labels do not certify holiday, session, roll or exchange auction semantics.",
                                 "Selected data hashes include all supplied columns; source container identities remain metadata-only."]}
        ref = registry.artifacts.put_json(report,kind="full_window_trade_reconciliation")
        registry.finish(attempt,status="succeeded",cpu_seconds=time.process_time()-cpu,wall_seconds=time.monotonic()-wall,
                         peak_rss_bytes=report["peak_rss_bytes"],reason="All eight declared bounded comparisons executed; inspect mismatch and coverage outcomes.",result_artifacts=(asdict(ref),asdict(index_ref)))
        return {"success":True,"report":str(registry.artifacts.path(ref)),"artifact":asdict(ref),
                "all_observed_windows_match":report["all_observed_windows_match"],"cpu_seconds":report["cpu_seconds"],
                "nonempty_paired_windows":report["nonempty_paired_windows"],
                "peak_rss_bytes":report["peak_rss_bytes"],"windows":[{k:r[k] for k in ("root","start","mbp_trade_rows","standalone_trade_rows","extra_mbp_rows","extra_standalone_rows","side_mismatch_rows")} for r in reports]}
    except BaseException as exc:
        ref = registry.artifacts.put_json({"success":False,"error":type(exc).__name__,"reason":str(exc),"completed_cohorts":reports,
                                           "code_snapshot":asdict(snapshot),"index_artifact":asdict(index_ref)},kind="failed_reconciliation")
        registry.finish(attempt,status="interrupted" if isinstance(exc,(KeyboardInterrupt,SystemExit)) else "failed",
                         cpu_seconds=time.process_time()-cpu,wall_seconds=time.monotonic()-wall,
                         peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,reason=str(exc),result_artifacts=(asdict(ref),))
        raise
