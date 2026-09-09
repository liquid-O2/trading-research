"""Fixed golden prefixes for the 22 acquired flat Parquet field/type profiles."""

import argparse
from dataclasses import asdict
from datetime import date, datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import resource
import signal
import struct
import time

from trading_research.data.arrow_fields import parquet_raw_rows, schema_identity
from trading_research.data.readers import _stamp
from trading_research.errors import ContractError, DependencyUnavailable, IntegrityError
from trading_research.operations.artifacts import code_manifest, code_snapshot, digest, file_digest
from trading_research.operations.trials import TrialRegistry

ROOT = Path(__file__).resolve().parents[3]


def _timestamp_integer(text: str, unit: str) -> int:
    match = re.fullmatch(r"(\d{4}-\d\d-\d\d)[ T](\d\d:\d\d:\d\d)(?:\.(\d{1,9}))?(?:\+00:00|Z)", text)
    if match is None:
        raise ContractError("prior timestamp needs an explicit UTC text representation mapping")
    whole = datetime.fromisoformat(match[1]+"T"+match[2]).replace(tzinfo=timezone.utc)
    delta = whole-datetime(1970,1,1,tzinfo=timezone.utc)
    ns = (delta.days*86400+delta.seconds)*1_000_000_000+int((match[3] or "").ljust(9,"0"))
    divisor = {"ns":1,"us":1000}[unit]
    if ns%divisor:
        raise IntegrityError("prior timestamp cannot be represented exactly by the declared physical unit")
    return ns//divisor


def compare_prior_values(values: dict, prior: dict) -> int:
    if set(values) != set(prior):
        raise IntegrityError("raw Arrow columns differ from the fixed complete prior row")
    for field, expected in prior.items():
        cell = values[field]
        current, type_name = cell["value"], cell["type"]
        if expected is not None:
            if type_name.startswith("timestamp["):
                expected = _timestamp_integer(expected, type_name.split("[")[1].split(",")[0])
            elif type_name == "date32[day]":
                expected = (date.fromisoformat(expected)-date(1970,1,1)).days
            elif type_name == "double":
                if current is not None:
                    current = struct.unpack("<d", bytes.fromhex(current["bits_le"]))[0]
                if isinstance(expected,float) and math.isnan(expected) and isinstance(current,float) and math.isnan(current):
                    continue  # Prior JSON did not preserve a NaN payload; separate fixtures do.
        if current != expected:
            raise IntegrityError(f"raw Arrow {field} differs from its fixed prior value: {current!r} vs {expected!r}")
    return len(prior)


def nominate_profiles(catalog: dict, prior_samples: list) -> dict:
    """Choose using prior schema text and paths before reading current source rows."""
    profiles = {}
    for dataset, variants in catalog.items():
        for fields in variants:
            key = digest(fields)
            profiles.setdefault(key,{"fields":fields,"datasets":[]})["datasets"].append(dataset)
    if len(profiles) != 22 or len(prior_samples) != 216:
        raise ContractError("this pilot requires the original fixed 22-profile and 216-sample registries")
    chosen, missing = [], []
    for profile_id, profile in sorted(profiles.items()):
        expected = [(f["name"],f["type"]) for f in profile["fields"]]
        candidates = []
        for sample in prior_samples:
            if sample["dataset"] not in profile["datasets"] or not sample["head"]:
                continue
            displayed = []
            for line in sample["schema"].splitlines():
                if line.startswith("-- schema metadata --"):
                    break
                if line and not line[0].isspace() and ": " in line:
                    name, value = line.split(": ",1)
                    displayed.append((name,value))
            if displayed == expected:
                candidates.append(sample)
        if not candidates:
            missing.append({"profile_id":profile_id,"profile":profile,
                            "reason":"physical profile lacks a fixed nonempty prior golden sample"})
            continue
        selected = min(candidates,key=lambda p:(p["dataset"],p["file"]))
        chosen.append({"profile_id":profile_id,"profile":profile,"prior":selected})
    return {"choices":chosen,"missing_profiles":missing,"declared_profile_count":len(profiles)}


def audit_arrow(*,data_root:Path,schemas_path:Path,prior_audit:Path,output_root:Path) -> dict:
    import pyarrow.parquet as pq
    start=time.monotonic();cpu=time.process_time()
    registry=TrialRegistry(output_root);code=code_manifest(ROOT);snapshot=code_snapshot(ROOT,registry.artifacts)
    # Freeze available registry bytes for trial identity, retaining read failures
    # as an explicit input state. Parsing and nomination run inside the attempt.
    inputs={};input_bytes={};input_errors=[]
    for name,path in (("schema_catalog",schemas_path),("prior_audit",prior_audit)):
        try:
            input_bytes[name]=path.read_bytes();inputs[name]=hashlib.sha256(input_bytes[name]).hexdigest()
        except OSError as exc:
            input_errors.append({"input":name,"path":str(path),"exception":type(exc).__name__,"reason":str(exc)})
    protocol={"purpose":"complete-flat-field-preservation-on-fixed-prefixes",
              "source_review":"validation/F01_ARROW_PROTOCOL.md","inputs":inputs,"input_errors":input_errors,
              "selection_rule":"lexicographically first nonempty previously audited file per declared field/type profile",
              "missing_profile_rule":"retain the unmet golden prerequisite, inspect available profiles, and fail the full-coverage claim",
              "expected_catalog_profiles":22,"expected_prior_samples":216,
              "max_files":22,"max_rows_per_file":3,"max_batch_rows":3,"max_output_bytes_per_file":8*1024**2,
              "hard_process_limits_cli":{"cpu_soft_seconds":60,"cpu_hard_seconds":65,"address_space_bytes":2*1024**3,"wall_seconds":120},
              "metadata_extent":"exact current serialized schema; prior audit had only display text",
              "economic_evaluation":False}
    family="F01-arrow-golden-prefixes-v2"
    registry.register_family(family,scope_ids=("F01","F01.DECODER","B00.5","B01.1"),protocol=protocol,max_attempts=8,cpu_budget_seconds=480)
    trial=registry.register(name="Acquired Parquet physical profile golden prefixes",family=family,stage="engineering",configuration=protocol,
                            code_hash=digest(code),data_hashes={**inputs,"preflight_input_state":digest(input_errors)},fold_version="no-fit",target_version="raw-arrow-field-fidelity-v1")
    attempt=registry.start(trial,cpu_reservation_seconds=60);reports=[];failures=[];nomination=None
    try:
        if input_errors:
            raise DependencyUnavailable("raw Arrow audit input registry could not be read; see retained input errors")
        catalog=json.loads(input_bytes['schema_catalog']);prior=json.loads(input_bytes['prior_audit'])
        nomination=nominate_profiles(catalog,prior)
        for choice in nomination['choices']:
            previous=choice["prior"];path=data_root/previous["file"]
            details=[];checks=0
            try:
                if not path.resolve().is_relative_to(data_root.resolve()):
                    raise ContractError("nominated source path escapes the admitted data root")
                stamp=_stamp(path)
                with pq.ParquetFile(path) as pf:
                    schema=pf.schema_arrow;count=pf.metadata.num_rows
                fields=[{"name":f.name,"type":str(f.type),"nullable":f.nullable} for f in schema]
                if fields!=choice["profile"]["fields"] or str(schema)!=previous["schema"] or count!=previous["footer_rows"]:
                    raise IntegrityError("current footer differs from the nominated prior schema/count contract")
                expected_rows=previous["head"][:3]
                rows=list(parquet_raw_rows(path,data_root=data_root,dataset_id=previous["dataset"],acquisition_version="supplied-catalog-20260906",
                                           expected_schema=schema,max_rows=len(expected_rows),batch_size=3,max_output_bytes=8*1024**2))
                if len(rows)!=len(expected_rows):raise IntegrityError("current raw prefix is shorter than its fixed prior observations")
                for row,expected in zip(rows,expected_rows,strict=True):
                    values=row.values();checks+=compare_prior_values(values,expected)
                    ipc=registry.artifacts.put_bytes(row.raw_ipc,kind="diagnostic_arrow_row")
                    details.append({"address":asdict(row.address),"row_id":row.id,"raw_fields":json.loads(row.raw_fields),
                                    "raw_fields_hash":row.content_hash,"raw_ipc":asdict(ipc),"prior_fields_compared":len(expected),
                                    "checked_raw_ipc":True})
                if _stamp(path)!=stamp:raise IntegrityError("source metadata changed across the nominated footer/prefix read")
                reports.append({"dataset_id":previous["dataset"],"path":previous["file"],"profile_id":choice["profile_id"],
                                "schema_id":schema_identity(schema),"schema_arrow":schema.serialize().to_pybytes().hex(),
                                "schema_display":str(schema),"source_footer_rows":count,"source_metadata_stamp":stamp,"rows":details,
                                "prior_field_assertions":checks,"depth":"row_prefix","whole_partition_admitted":False})
            except TimeoutError:
                raise
            except (ContractError,OSError,ValueError) as exc:
                failures.append({"dataset_id":previous['dataset'],"path":previous['file'],"profile_id":choice['profile_id'],
                                 "exception":type(exc).__name__,"reason":str(exc),"partial_rows":details})
        if code_manifest(ROOT)!=code or file_digest(schemas_path)!=inputs["schema_catalog"] or file_digest(prior_audit)!=inputs["prior_audit"]:
            raise IntegrityError("code or fixed input registry changed during raw Arrow audit")
        complete=not nomination['missing_profiles'] and not failures
        report={"kind":"bounded_arrow_field_validation","success":complete,"execution_completed":True,
                "all_declared_profiles_validated":complete,"missing_profiles":nomination['missing_profiles'],"profile_failures":failures,
                "declared_profile_count":nomination['declared_profile_count'],"validated_profile_count":len(reports),
                "trial_id":trial,"attempt_id":attempt,"protocol":protocol,
                "code_snapshot":asdict(snapshot),"partitions":reports,"rows":sum(len(p["rows"]) for p in reports),
                "prior_field_assertions":sum(p["prior_field_assertions"] for p in reports),
                "cpu_seconds":time.process_time()-cpu,"wall_seconds":time.monotonic()-start,"peak_rss_bytes":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                "code_unchanged_during_run":True,"model_fits":0,"economic_runs":0,
                "limitations":["One fixed prefix per catalogued physical signature; not every dataset or schema metadata variant.",
                               "Source identity is metadata-only plus exact retained row/schema content; no whole-file hash claim.",
                               "Publication, revision, correction and market eligibility meanings still require source-specific adapters.",
                               "Date/ns/us preservation is physical evidence, not an actual strategy receipt or completeness certificate."]}
        ref=registry.artifacts.put_json(report,kind="arrow_field_validation")
        registry.finish(attempt,status="succeeded" if complete else "failed",cpu_seconds=report["cpu_seconds"],wall_seconds=report["wall_seconds"],peak_rss_bytes=report["peak_rss_bytes"],
                         reason="Every declared physical profile matched its fixed golden prefix." if complete else "Full declared profile coverage remains unmet; inspect missing golden prerequisites and per-profile failures.",result_artifacts=(asdict(ref),))
        return {"success":complete,"execution_completed":True,"rows":report["rows"],"prior_field_assertions":report["prior_field_assertions"],"profiles":len(reports),
                "declared_profiles":nomination['declared_profile_count'],"missing_golden_profiles":len(nomination['missing_profiles']),"failed_profiles":len(failures),
                "report":str(registry.artifacts.path(ref)),"artifact":asdict(ref)}
    except BaseException as exc:
        ref=registry.artifacts.put_json({"success":False,"exception":type(exc).__name__,"reason":str(exc),"completed_profiles":reports,
                                        "trial_id":trial,"attempt_id":attempt,"code_snapshot":asdict(snapshot),"protocol":protocol,
                                        "nomination":nomination,"profile_failures":failures},kind="failed_arrow_field_validation")
        registry.finish(attempt,status="interrupted" if isinstance(exc,(KeyboardInterrupt,SystemExit)) else "failed",cpu_seconds=time.process_time()-cpu,
                         wall_seconds=time.monotonic()-start,peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,
                         reason=f"{type(exc).__name__}: {exc}",result_artifacts=(asdict(ref),))
        raise


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root",type=Path,default=ROOT.parent/"data")
    parser.add_argument("--schemas",type=Path,default=ROOT.parent/"data/manifests/schema-catalog.json")
    parser.add_argument("--prior-audit",type=Path,default=ROOT.parent/"planning/trading-model/review/data-audit/parquet-samples.json")
    parser.add_argument("--output-root",type=Path,default=ROOT/"evidence/trials")
    args=parser.parse_args(argv)
    def exceeded(signum,frame):raise TimeoutError(f"raw Arrow audit deadline reached (signal {signum})")
    signal.signal(signal.SIGALRM,exceeded);signal.signal(signal.SIGXCPU,exceeded)
    resource.setrlimit(resource.RLIMIT_CPU,(60,65));resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3));signal.alarm(120)
    try:print(json.dumps(audit_arrow(data_root=args.data_root,schemas_path=args.schemas,prior_audit=args.prior_audit,output_root=args.output_root),indent=2))
    finally:signal.alarm(0)


if __name__=="__main__":main()
