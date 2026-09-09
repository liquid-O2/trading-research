"""Registered bounded MBP reader/reducer pilot; never full-history certification."""

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import resource
import time

from trading_research.data.book import BookReducer
from trading_research.data.events import Flags, LatencyScenario, decode_fields, encode_fields
from trading_research.data.readers import native_mbp, native_records, parquet_mbp
from trading_research.operations.artifacts import code_manifest, code_snapshot, digest
from trading_research.operations.trials import TrialRegistry

ROOT = Path(__file__).resolve().parents[3]


def sample_partition(*, data_root: Path, relative_path: str, dataset_id: str, max_rows: int,
                     native: bool, row_group: int = 0) -> dict:
    scenario = LatencyScenario("engineering-prefix-provider-plus-100ms" if native else "engineering-prefix-event-plus-100ms",
                               "provider_received" if native else "event", 100_000_000, 100_000_000)
    reducer, actions, sides, flags, issues = BookReducer(), Counter(), Counter(), Counter(), Counter()
    checksum = hashlib.sha256()
    metadata = []
    addresses = []
    bounds, known_bounds = [], []
    before = time.monotonic()
    cpu = time.process_time()
    if native:
        def events():
            for record in native_records(data_root / relative_path, data_root=data_root, dataset_id=dataset_id,
                                          acquisition_version="supplied-catalog-20260906", max_records=max_rows):
                if record.kind == "Metadata":
                    metadata.append({"address": asdict(record.address), "fields": record.fields,
                                     "raw_metadata_hex": record.raw_bytes.hex()})
                else:
                    yield native_mbp(record, scenario=scenario)
        source = events()
    else:
        source = parquet_mbp(data_root / relative_path, data_root=data_root, dataset_id=dataset_id,
                             acquisition_version="supplied-catalog-20260906", scenario=scenario,
                             max_rows=max_rows, row_groups=(row_group,))
    count, without_last, raw_volume = 0, 0, 0
    for e in source:
        if encode_fields(decode_fields(e.raw_fields)) != e.raw_fields:
            raise ValueError("lossless raw-field roundtrip failed")
        checksum.update(e.raw_fields)
        if e.raw_record is not None:
            checksum.update(e.raw_record)
        checksum.update(b"\n")
        raw = decode_fields(e.raw_fields)
        if raw["action"] in ("T", b"T", ord("T")) and not int(raw["flags"]) & int(Flags.SNAPSHOT):
            raw_volume += raw["size"]
        reducer.apply(e)
        actions[str(e.action)] += 1
        sides[f"{e.action}:{e.reported_side}"] += 1
        flags[str(int(e.flags))] += 1
        issues.update(e.quality_reasons)
        if e.action == "T" and not e.flags & Flags.LAST:
            without_last += 1
        if len(addresses) < 2:
            addresses.append(asdict(e.address))
        bounds.append(e.clocks.event_at)
        known_bounds.append(e.clocks.known_at)
        count += 1
    projected = sum(state.total_volume for state in reducer.states.values())
    if projected != raw_volume:
        raise ValueError("literal raw trade volume and canonical reducer disagree")
    elapsed, cpu_used = time.monotonic() - before, time.process_time() - cpu
    return {"dataset_id": dataset_id, "relative_path": relative_path, "row_group": None if native else row_group,
            "rows": count, "actions": dict(actions), "sides_by_action": dict(sides), "combined_flags": dict(flags),
            "quality_reasons": dict(issues), "trade_rows_without_last": without_last,
            "observed_trade_volume": projected, "raw_trade_volume": raw_volume,
            "event_time_min": min(bounds, default=None), "event_time_max": max(bounds, default=None),
            "known_time_min_under_assumption": min(known_bounds, default=None),
            "known_time_max_under_assumption": max(known_bounds, default=None),
            "final_states": [asdict(s) for s in reducer.states.values()],
            "source_addresses": addresses, "metadata": metadata, "sample_sha256": checksum.hexdigest(),
            "raw_roundtrip_passed": True, "volume_reconciliation_passed": True,
            "input_identity_basis": "metadata-only container fingerprint plus exact per-row/record content hashes; no whole-file hash claim",
            "wall_seconds": elapsed, "cpu_seconds": cpu_used, "rows_per_cpu_second": count / cpu_used if cpu_used else None,
            "rows_per_wall_second": count / elapsed if elapsed else None, "latency_scenario": asdict(scenario),
            "certification_scope": "selected row prefix only; no calendar, complete flow, recovery or economic eligibility certification"}


def run_pilot(*, data_root: Path, output_root: Path, max_rows: int = 4096) -> dict:
    selections = [
        ("quantpad/cme__nq-continuous-futures__mbp-1/2019-12-30.parquet", False, 0),
        ("quantpad/cme__nq-continuous-futures__mbp-1/2021-02-08.parquet", False, 88),
        ("quantpad/cme__es-continuous-futures__mbp-1/2020-01.parquet", False, 0),
        ("databento/cme__hg-futures__mbp-1/glbx-mdp3-20210101-20211231.mbp-1.dbn.zst", True, 0),
    ]
    if type(max_rows) is not int or not 1 <= max_rows <= 65536:
        raise ValueError("pilot max_rows must be 1..65536 per declared partition")
    registry = TrialRegistry(output_root)
    registry.register_family("B01-mbp-reader-pilot-v1", scope_ids=("F01.DECODER", "F06.GAP_RECOVERY", "V08"),
                              protocol={"purpose": "engineering-prefix-fidelity-and-throughput", "partitions": selections,
                                        "maximum_rows_per_partition": 65536, "maximum_compressed_native_bytes": 16 * 1024**2,
                                        "expansion": "requires measured estimate and separately registered configuration",
                                        "economic_evaluation": False}, max_attempts=12, cpu_budget_seconds=600)
    snapshot = code_snapshot(ROOT, registry.artifacts)
    configuration = {"selections": selections, "rows_per_partition": max_rows, "implementation": "literal-reference"}
    source_versions = {}
    for relative, _, _ in selections:
        stat = (data_root / relative).stat()
        source_versions[relative] = digest({"size": stat.st_size, "mtime_ns": stat.st_mtime_ns,
                                            "basis": "metadata_only; sampled_content_in_result"})
    trial = registry.register(name="MBP literal reader pilot", family="B01-mbp-reader-pilot-v1", stage="engineering",
                              configuration=configuration, code_hash=digest(code_manifest(ROOT)),
                              data_hashes={"selection_manifest": digest(selections), **source_versions}, fold_version="engineering-no-fit",
                              target_version="lossless-mbp-prefix-fidelity-v1")
    attempt = registry.start(trial, cpu_reservation_seconds=120)
    start, cpu = time.monotonic(), time.process_time()
    reports = []
    try:
        for path, native, group in selections:
            reports.append(sample_partition(data_root=data_root, relative_path=path, dataset_id=str(Path(path).parent),
                                             native=native, row_group=group, max_rows=max_rows))
        report = {"kind": "completed_bounded_engineering_pilot", "success": True, "trial_id": trial, "attempt_id": attempt,
                  "code_snapshot": asdict(snapshot), "partitions": reports, "observed_rows": sum(r["rows"] for r in reports),
                  "scope": "Four fixed row prefixes, including the documented NQ bit-4 prefix; no full-file or full-history claim.",
                  "economic_runs": 0, "model_fits": 0,
                  "limitations": ["Missing strategy receipts remain missing; timing uses named engineering assumptions.",
                                  "A matched full-hour embedded/standalone trade reconciliation remains required.",
                                  "No real source recovery certificate, complete calendar/roll cohort or verified fee input is supplied by this pilot.",
                                  "Reference per-row hashing and retained idempotency keys are not an optimized full-history engine."]}
        ref = registry.artifacts.put_json(report, kind="bounded_data_pilot")
        registry.finish(attempt, status="succeeded", cpu_seconds=time.process_time() - cpu, wall_seconds=time.monotonic() - start,
                         peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                         reason="Four declared prefix reads and raw roundtrip/volume assertions completed.", result_artifacts=(asdict(ref),))
        return {"success": True, "observed_rows": report["observed_rows"], "trial_id": trial, "attempt_id": attempt,
                "report": str(registry.artifacts.path(ref)), "artifact": asdict(ref),
                "partitions": [{k: r[k] for k in ("dataset_id", "row_group", "rows", "observed_trade_volume",
                                                 "trade_rows_without_last", "rows_per_cpu_second")} for r in reports]}
    except BaseException as exc:
        failure = registry.artifacts.put_json({"error": type(exc).__name__, "reason": str(exc), "completed_partitions": reports,
                                               "code_snapshot": asdict(snapshot)}, kind="failed_data_pilot")
        registry.finish(attempt, status="interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed",
                         cpu_seconds=time.process_time() - cpu, wall_seconds=time.monotonic() - start,
                         peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                         reason=f"{type(exc).__name__}: {exc}", result_artifacts=(asdict(failure),))
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("mbp-pilot",))
    parser.add_argument("--data-root", type=Path, default=ROOT.parent / "data")
    parser.add_argument("--output-root", type=Path, default=ROOT / "evidence/trials")
    parser.add_argument("--max-rows", type=int, default=4096)
    args = parser.parse_args(argv)
    print(json.dumps(run_pilot(data_root=args.data_root, output_root=args.output_root, max_rows=args.max_rows), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
