"""F01 native golden-prefix audit, with fixed prior observations and budgets."""

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
import resource
import signal
import time

from trading_research.data.events import encode_fields
from trading_research.data.native_fields import reassemble_native_fields, typed_native_fields
from trading_research.data.readers import _stamp, native_records
from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import code_manifest, code_snapshot, digest, file_digest
from trading_research.operations.trials import TrialRegistry

ROOT = Path(__file__).resolve().parents[3]
_RTYPE = {"mbp-0": 0, "instrument-def": 19, "statistics": 24, "ohlcv-1m": 33}


def compare_prior_row(fields: dict, expected: dict) -> int:
    """The prior audit stores raw prices and some enum reprs, not scaled values."""
    for key, value in expected.items():
        if key not in fields:
            raise IntegrityError(f"native decoder omitted prior-audit field {key}")
        current = fields[key]
        if key == "rtype":
            if value not in _RTYPE:
                raise ContractError("prior audit rtype needs an explicit comparison mapping")
            value = _RTYPE[value]
        elif key in {"stat_type", "update_action"}:
            match = re.fullmatch(r"<(?:StatType|StatUpdateAction)\.[A-Z0-9_]+: (\d+)>", value)
            if match is None:
                raise ContractError("unregistered prior native enum representation")
            value = int(match[1])
        elif isinstance(current, bytes) and isinstance(value, str):
            # Raw fixed arrays retain their NUL tails; compare the audit's text.
            current = current.split(b"\0", 1)[0].decode("ascii")
        if current != value:
            raise IntegrityError(f"native field {key} differs from the fixed prior-audit value: {current!r} vs {value!r}")
    return len(expected)


def audit_native(*, data_root: Path, prior_audit: Path, output_root: Path) -> dict:
    prior_bytes = prior_audit.read_bytes()
    selections = json.loads(prior_bytes)
    if (len(selections) != 24 or any(len(s["rows"]) != 3 for s in selections)
            or len({s["file"] for s in selections}) != 24
            or {s["schema"] for s in selections} != {"definition", "trades", "statistics", "ohlcv-1m"}):
        raise ContractError("this registered native pilot requires the original fixed 24-file, three-record selection")
    data_root = data_root.resolve()
    for item in selections:
        if not Path(item["file"]).resolve().is_relative_to(data_root):
            raise ContractError("nominated native source is outside the declared data root")
    protocol = {"purpose": "source-field-fidelity-before-semantic-consumers",
                "source_review": "validation/F01_NATIVE_PROTOCOL.md",
                "prior_audit_sha256": hashlib.sha256(prior_bytes).hexdigest(),
                "selections": [{"file": str(Path(s["file"]).relative_to(data_root)), "schema": s["schema"]} for s in selections],
                "max_records_per_file": 3, "max_compressed_bytes_per_file": 16*1024**2,
                "max_decompressed_bytes_per_file": 64*1024**2,
                "expected_result": "all prior selected fields agree; every raw field reconstructs exact record bytes",
                "hard_process_limits_cli": {"cpu_soft_seconds": 60, "cpu_hard_seconds": 65,
                                             "address_space_bytes": 2*1024**3, "wall_seconds": 120},
                "market_eligibility": "unassessed", "economic_evaluation": False}
    registry = TrialRegistry(output_root)
    family = "F01-native-golden-prefixes-v1"
    registry.register_family(family, scope_ids=("F01", "F01.DECODER", "B00.5", "B01.1"),
                             protocol=protocol, max_attempts=8, cpu_budget_seconds=480)
    snapshot = code_snapshot(ROOT, registry.artifacts)
    code = code_manifest(ROOT)
    sources = {s["file"]: digest({"stamp": _stamp(Path(s["file"])), "basis": "metadata_only"}) for s in selections}
    trial = registry.register(name="Native original field and golden-prefix fidelity", family=family, stage="engineering",
                              configuration=protocol, code_hash=digest(code),
                              data_hashes={"prior_audit": file_digest(prior_audit), **sources},
                              fold_version="no-fit", target_version="native-field-preservation-v1")
    attempt = registry.start(trial, cpu_reservation_seconds=60)
    start, cpu = time.monotonic(), time.process_time()
    reports = []
    try:
        for selection in selections:
            path = Path(selection["file"])
            relative = path.relative_to(data_root)
            records = list(native_records(path, data_root=data_root, dataset_id=str(relative.parent),
                                          acquisition_version="supplied-catalog-20260906", max_records=3,
                                          max_compressed_bytes=protocol["max_compressed_bytes_per_file"],
                                          max_decompressed_bytes=protocol["max_decompressed_bytes_per_file"],
                                          expected_schema=selection["schema"]))
            if len(records) != 4 or records[0].kind != "Metadata":
                raise IntegrityError("native prefix has fewer records than the fixed prior sample")
            metadata, rows = records[0], records[1:]
            for key, expected in (("start", selection["start_ns"]), ("end", selection["end_ns"]),
                                  ("schema", selection["schema"])):
                if metadata.fields[key] != expected:
                    raise IntegrityError("source metadata differs from the fixed prior audit")
            checks = 0
            row_details = []
            for record, expected in zip(rows, selection["rows"], strict=True):
                raw = reassemble_native_fields(record)
                checks += compare_prior_row(record.fields, expected)
                row_details.append({"address": asdict(record.address), "kind": record.kind,
                                    "dbn_version": record.dbn_version, "layout_id": record.layout_id,
                                    "raw_record_sha256": hashlib.sha256(raw).hexdigest(),
                                    "all_raw_fields": record.fields, "raw_fields_hash": digest(encode_fields(record.fields)),
                                    "explicit_typed_fields": typed_native_fields(record),
                                    "prior_fields_compared": sorted(expected), "reassembly_equal": True})
            prefix = registry.artifacts.put_bytes(b"".join(r.raw_bytes for r in records), kind="native_diagnostic_prefix")
            reports.append({"path": str(relative), "metadata": {k: v for k, v in metadata.fields.items()
                                                               if k not in {"mappings", "symbols", "partial", "not_found"}},
                            "metadata_raw_sha256": hashlib.sha256(metadata.raw_bytes).hexdigest(),
                            "mapping_count": len(metadata.fields["mappings"]), "metadata_full_fields_in_prefix": True,
                            "rows": row_details, "prior_field_assertions": checks, "raw_prefix": asdict(prefix),
                            "source_identity_extent": "metadata-only container; exact original metadata and three record bytes retained",
                            "complete_partition_admitted": False})
        if code_manifest(ROOT) != code or file_digest(prior_audit) != hashlib.sha256(prior_bytes).hexdigest():
            raise IntegrityError("code or fixed comparison inputs changed during the native audit")
        report = {"kind": "bounded_native_field_validation", "success": True, "trial_id": trial,
                  "attempt_id": attempt, "code_snapshot": asdict(snapshot), "protocol": protocol,
                  "partitions": reports, "native_records": sum(len(p["rows"]) for p in reports),
                  "prior_field_assertions": sum(p["prior_field_assertions"] for p in reports),
                  "cpu_seconds": time.process_time()-cpu, "wall_seconds": time.monotonic()-start,
                  "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                  "code_unchanged_during_run": True, "model_fits": 0, "economic_runs": 0,
                  "limitations": ["Fixed first/middle/last file prefixes only; no whole-native-partition admission.",
                                  "Reference audit was made with provider decoding; hand-packed tests supply separate golden values.",
                                  "Raw definitions and statistics do not establish valuation, OI assimilation or exact expiration precision.",
                                  "No actual strategy receipt, full-cohort integrity or market-operation eligibility is certified."]}
        ref = registry.artifacts.put_json(report, kind="native_field_validation")
        registry.finish(attempt, status="succeeded", cpu_seconds=report["cpu_seconds"], wall_seconds=report["wall_seconds"],
                         peak_rss_bytes=report["peak_rss_bytes"], reason="All fixed native prefix field assertions passed.",
                         result_artifacts=(asdict(ref),))
        return {"success": True, "native_records": report["native_records"],
                "prior_field_assertions": report["prior_field_assertions"], "partitions": len(reports),
                "report": str(registry.artifacts.path(ref)), "artifact": asdict(ref)}
    except BaseException as exc:
        ref = registry.artifacts.put_json({"success": False, "exception": type(exc).__name__, "reason": str(exc),
                                          "trial_id": trial, "attempt_id": attempt, "completed_partitions": reports,
                                          "code_snapshot": asdict(snapshot)}, kind="failed_native_field_validation")
        registry.finish(attempt, status="interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed",
                         cpu_seconds=time.process_time()-cpu, wall_seconds=time.monotonic()-start,
                         peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                         reason=f"{type(exc).__name__}: {exc}", result_artifacts=(asdict(ref),))
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=ROOT.parent/"data")
    parser.add_argument("--prior-audit", type=Path, default=ROOT.parent/"planning/trading-model/review/data-audit/dbn-header-samples.json")
    parser.add_argument("--output-root", type=Path, default=ROOT/"evidence/trials")
    args = parser.parse_args(argv)
    def exceeded(signum, frame):
        raise TimeoutError(f"native audit process resource deadline reached (signal {signum})")
    signal.signal(signal.SIGALRM, exceeded)
    signal.signal(signal.SIGXCPU, exceeded)
    resource.setrlimit(resource.RLIMIT_CPU, (60, 65))
    resource.setrlimit(resource.RLIMIT_AS, (2*1024**3, 2*1024**3))
    signal.alarm(120)
    try:
        print(json.dumps(audit_native(data_root=args.data_root, prior_audit=args.prior_audit,
                                     output_root=args.output_root), indent=2))
    finally:
        signal.alarm(0)


if __name__ == "__main__":
    main()
