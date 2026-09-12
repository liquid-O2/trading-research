"""Validate and report frozen empirical replay artifacts.

The empirical runner deliberately writes one checkpoint and one artifact per
coverage partition.  This module is the read-only reporting boundary for
those files.  It validates their identities before counting observations and
keeps the reporting denominator separate from source-faithful dispositions.

No source outcome is inferred here.  In particular, ``source_assembly`` is
retained as audit material and is never used as a proxy for a source verdict.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterable, Mapping


ROOT = Path("/workspace/implementation/reports/phase1-live/empirical")
SCHEMA = "phase1-empirical-report-v1"
REPORT_VERSION = "1.0.2"
PHASE_TABLE = "family | variant | n | faithful_disagreements | status | report path"
AUDIT_TABLE = "family | id | verdict | fixture | leakage | proxy-as-faithful | notes"
_VERDICTS = {"pass", "fail", "unknown"}
_STATUSES = {"completed", "missing_data", "completed_with_population_holes"}


class ReportingError(ValueError):
    """Raised by the CLI for an unrecoverable report input error."""


def _plain(value: Any) -> Any:
    """Convert the small set of values used by manifests to JSON values."""

    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (date,)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    """Canonical bytes used for registry, job and manifest identities."""

    return json.dumps(_plain(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_hash_without(document: Mapping[str, Any], field: str) -> str:
    return content_hash({k: v for k, v in document.items() if k != field})


def _read_json(path: Path, errors: list[str], label: str) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text())
    except FileNotFoundError:
        errors.append(f"missing {label}: {path}")
        return None
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read {label} {path}: {exc}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label} must be a JSON object: {path}")
        return None
    return value


def _first_existing(root: Path, candidates: Iterable[Path]) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    # The first path gives a useful error path while preserving deterministic
    # discovery for callers that want to inspect validation.errors.
    return next(iter(candidates))


def _registry_path(root: Path, supplied: str | Path | None) -> Path:
    if supplied is not None:
        return Path(supplied)
    return _first_existing(root, (root / "registry" / "CANDIDATE_REGISTRY.json", root / "CANDIDATE_REGISTRY.json"))


def _manifest_path(root: Path, supplied: str | Path | None) -> Path:
    if supplied is not None:
        return Path(supplied)
    return _first_existing(root, (root / "RUN_MANIFEST.json", root / "run" / "RUN_MANIFEST.json", root / "manifests" / "RUN_MANIFEST.json"))


def _manifest_hash(manifest: Mapping[str, Any]) -> tuple[str | None, str | None]:
    """Return (declared field, recomputed hash), supporting runner v1 names."""

    if "run_manifest_sha256" in manifest:
        return manifest.get("run_manifest_sha256"), _canonical_hash_without(manifest, "run_manifest_sha256")
    if "manifest_sha256" in manifest:
        return manifest.get("manifest_sha256"), _canonical_hash_without(manifest, "manifest_sha256")
    return None, None


def _partition_value(partition: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in partition:
            return partition[key]
    return None


def _same_id(left: Any, right: Any) -> bool:
    # Instrument IDs are sometimes serialized as JSON numbers and sometimes
    # as strings.  The protocol treats those spellings as the same identity.
    return str(left) == str(right)


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return default


def _summary(records: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Recompute the protocol population summary without validating source data."""

    rows = list(records)
    ids: list[Any] = []
    verdicts: list[str] = []
    selected = censored = ambiguous = timing = proxy = 0
    for row in rows:
        opportunity = row.get("opportunity") if isinstance(row, Mapping) else None
        replay = row.get("replay") if isinstance(row, Mapping) else None
        opportunity = opportunity if isinstance(opportunity, Mapping) else {}
        replay = replay if isinstance(replay, Mapping) else {}
        ids.append(opportunity.get("opportunity_id"))
        verdict = replay.get("verdict")
        verdicts.append(verdict)
        selected += int(replay.get("selected_signal_at") is not None)
        censored += _as_int(replay.get("censored"), 0)
        ambiguous += _as_int(replay.get("ambiguous"), 0)
        timing += _as_int(replay.get("timing_violations"), 0)
        proxy += _as_int(replay.get("proxy_as_faithful"), 0)
    if len(ids) != len(set(json.dumps(_plain(item), sort_keys=True) for item in ids)):
        raise ReportingError("duplicate opportunity in empirical denominator")
    if any(verdict not in _VERDICTS for verdict in verdicts):
        raise ReportingError("unknown verdict in empirical artifact")
    p = verdicts.count("pass")
    f = verdicts.count("fail")
    u = verdicts.count("unknown")
    n = p + f
    total = n + u
    rate = None if n == 0 else p / n
    if total == 0:
        interval = None
        interval_exact = None
    else:
        lo = Fraction(p, total)
        hi = Fraction(p + u, total)
        interval = [float(lo), float(hi)]
        interval_exact = [[lo.numerator, lo.denominator], [hi.numerator, hi.denominator]]
    return {
        "p": p,
        "f": f,
        "u": u,
        "n": n,
        "N": total,
        "rate": rate,
        "rate_exact": None if n == 0 else [p, n],
        "interval": interval,
        "interval_exact": interval_exact,
        "opportunities": len(rows),
        "candidates": len(rows),
        "selected_signals": selected,
        "actual_selections": None,
        "attempts": None,
        "orders": None,
        "actual_fills": None,
        "censored": censored,
        "ambiguous": ambiguous,
        "faithful_disagreements": None,
        "timing_violations": timing,
        "proxy_as_faithful": proxy,
        "denominator": "All observed initial opportunities, before later sequence confirmation; no actual-trade denominator.",
    }


def _number_equal(left: Any, right: Any) -> bool:
    # JSON's 1 and 1.0 represent the same summary value.  Other values must
    # retain exact equality, including nulls and strings.
    if isinstance(left, (int, float)) and not isinstance(left, bool) and isinstance(right, (int, float)) and not isinstance(right, bool):
        return left == right
    return left == right and type(left) is type(right)


def _summary_equal(actual: Mapping[str, Any], declared: Mapping[str, Any]) -> bool:
    if set(actual) != set(declared):
        return False
    return all(_number_equal(actual[key], declared[key]) for key in actual)


def _rule_meta(registry_rules: Mapping[str, Mapping[str, Any]], rule_id: str) -> Mapping[str, Any] | None:
    return registry_rules.get(rule_id)


def _record_rule_id(record: Mapping[str, Any]) -> str | None:
    opportunity = record.get("opportunity")
    if isinstance(opportunity, Mapping) and opportunity.get("rule_id") is not None:
        return str(opportunity["rule_id"])
    if record.get("rule_id") is not None:
        return str(record["rule_id"])
    return None


def _record_identity(record: Mapping[str, Any]) -> str | None:
    opportunity = record.get("opportunity")
    if isinstance(opportunity, Mapping) and opportunity.get("opportunity_id") is not None:
        return str(opportunity["opportunity_id"])
    if record.get("opportunity_id") is not None:
        return str(record["opportunity_id"])
    return None


def _record_year(record: Mapping[str, Any], fallback: Any) -> str:
    opportunity = record.get("opportunity")
    raw = opportunity.get("session_date") if isinstance(opportunity, Mapping) else None
    raw = raw if raw is not None else fallback
    text = str(raw)
    return text[:4] if len(text) >= 4 and text[:4].isdigit() else "unknown"


def _record_value(record: Mapping[str, Any], opportunity_key: str, fallback: Any = None) -> Any:
    opportunity = record.get("opportunity")
    if isinstance(opportunity, Mapping) and opportunity.get(opportunity_key) is not None:
        return opportunity[opportunity_key]
    if record.get(opportunity_key) is not None:
        return record[opportunity_key]
    return fallback


def _source_counts(record: Mapping[str, Any]) -> tuple[int, int, int]:
    """Return (leakage, timing violations, proxy-as-faithful) audit counts."""

    replay = record.get("replay") if isinstance(record.get("replay"), Mapping) else {}
    source = record.get("source_assembly") if isinstance(record.get("source_assembly"), Mapping) else {}
    result = source.get("result") if isinstance(source.get("result"), Mapping) else {}
    leakage = _as_int(result.get("leakage"), 0) + _as_int(result.get("leakage_count"), 0)
    timing = _as_int(replay.get("timing_violations"), 0) + _as_int(result.get("timing_violations"), 0)
    proxy = _as_int(replay.get("proxy_as_faithful"), 0) + _as_int(result.get("proxy_as_faithful"), 0)
    return leakage, timing, proxy


def _variant_text(row: Mapping[str, Any]) -> str:
    return (
        f"{row.get('rule_id')} / {row.get('cohort')} / {row.get('year')} / "
        f"{row.get('instrument_id')} / {row.get('evidence_mode')} / {row.get('observation_unit')}"
    )


def _combine_counts(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    values = list(rows)
    p = sum(_as_int(row.get("p"), 0) for row in values if row.get("p") is not None)
    f = sum(_as_int(row.get("f"), 0) for row in values if row.get("f") is not None)
    u = sum(_as_int(row.get("u"), 0) for row in values if row.get("u") is not None)
    n = p + f
    total = n + u
    return {
        "p": p,
        "f": f,
        "u": u,
        "n": n,
        "N": total,
        # Rates are deliberately only emitted for a fully compatible group;
        # rule and family reports remain additive and do not pool groups.
        "rate": None,
        "rate_exact": None,
        "interval": None,
        "interval_exact": None,
    }


def _group_counts(rows: list[Mapping[str, Any]], unavailable: bool) -> dict[str, Any]:
    if unavailable:
        return {"p": None, "f": None, "u": None, "n": None, "N": None, "rate": None, "rate_exact": None, "interval": None, "interval_exact": None}
    # ``rows`` are artifact records, whereas ``_combine_counts`` consumes
    # already-counted group rows.  Reuse the protocol summary for this
    # record-level boundary so verdict handling stays identical to checkpoint
    # validation.
    summary = _summary(rows)
    result = {key: summary[key] for key in ("p", "f", "u", "n", "N", "rate", "rate_exact", "interval", "interval_exact")}
    n = result["n"]
    total = result["N"]
    p = result["p"]
    result["rate"] = None if n == 0 else p / n
    result["rate_exact"] = None if n == 0 else [p, n]
    if total:
        lo = Fraction(p, total)
        hi = Fraction(p + result["u"], total)
        result["interval"] = [float(lo), float(hi)]
        result["interval_exact"] = [[lo.numerator, lo.denominator], [hi.numerator, hi.denominator]]
    return result


def _validate_and_collect(
    root: Path,
    registry: Mapping[str, Any],
    manifest: Mapping[str, Any],
    registry_hash: str,
    manifest_hash: str,
    errors: list[str],
    warnings: list[str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], set[str]]:
    """Read valid job/checkpoint/artifact triples and collect audit metadata."""

    raw_jobs = manifest.get("jobs")
    if not isinstance(raw_jobs, list):
        errors.append("run manifest jobs must be a list")
        raw_jobs = []
    jobs: dict[str, dict[str, Any]] = {}
    for position, raw_job in enumerate(raw_jobs):
        if not isinstance(raw_job, dict):
            errors.append(f"run manifest job {position} must be an object")
            continue
        job = dict(raw_job)
        job_id = job.get("job_id")
        if not isinstance(job_id, str) or not job_id:
            errors.append(f"run manifest job {position} lacks job_id")
            continue
        if job_id in jobs:
            errors.append(f"duplicate run manifest job: {job_id}")
            continue
        if not isinstance(job.get("cohort"), str) or not isinstance(job.get("partition"), dict):
            errors.append(f"job {job_id} lacks cohort/partition")
            continue
        rule_ids = job.get("rule_ids")
        if not isinstance(rule_ids, list) or any(not isinstance(item, str) for item in rule_ids) or len(rule_ids) != len(set(rule_ids)):
            errors.append(f"job {job_id} has invalid rule_ids")
            continue
        jobs[job_id] = job

    checkpoint_dir = root / "checkpoints"
    checkpoint_files = sorted(checkpoint_dir.glob("*.json")) if checkpoint_dir.exists() else []
    triples: list[dict[str, Any]] = []
    seen_job_ids: set[str] = set()
    seen_opportunities: set[str] = set()
    implementation_hashes: set[str] = set()

    for path in checkpoint_files:
        checkpoint = _read_json(path, errors, f"checkpoint")
        if checkpoint is None:
            continue
        stem = path.stem
        if "--" not in stem:
            errors.append(f"checkpoint filename must be cohort--partition_id: {path.name}")
        else:
            file_cohort, file_partition = stem.split("--", 1)
            if checkpoint.get("cohort") != file_cohort or str(checkpoint.get("partition_id")) != file_partition:
                errors.append(f"checkpoint filename/content identity mismatch: {path.name}")
        job_id = checkpoint.get("job_id")
        if not isinstance(job_id, str) or job_id not in jobs:
            errors.append(f"checkpoint {path.name} references unknown job: {job_id}")
            continue
        if job_id in seen_job_ids:
            errors.append(f"duplicate checkpoint for job: {job_id}")
            continue
        seen_job_ids.add(job_id)
        job = jobs[job_id]
        partition = job["partition"]
        expected_partition = _partition_value(partition, "partition_id", "id")
        expected_date = _partition_value(partition, "date", "session_date")
        expected_instrument = _partition_value(partition, "instrument_id", "instrument")
        if expected_partition is None or str(checkpoint.get("partition_id")) != str(expected_partition):
            errors.append(f"checkpoint {job_id} partition_id differs from run manifest")
        if expected_date is not None and str(checkpoint.get("session_date")) != str(expected_date):
            errors.append(f"checkpoint {job_id} session_date differs from run manifest")
        if expected_instrument is not None and not _same_id(checkpoint.get("instrument_id"), expected_instrument):
            errors.append(f"checkpoint {job_id} instrument_id differs from run manifest")
        if checkpoint.get("cohort") != job.get("cohort"):
            errors.append(f"checkpoint {job_id} cohort differs from run manifest")
        if checkpoint.get("registry_sha256") != registry_hash:
            errors.append(f"checkpoint {job_id} registry hash differs from registry")
        if checkpoint.get("run_manifest_sha256") != manifest_hash and checkpoint.get("manifest_sha256") != manifest_hash:
            errors.append(f"checkpoint {job_id} run manifest hash differs from run manifest")
        if checkpoint.get("job_sha256") != content_hash(job):
            errors.append(f"checkpoint {job_id} job hash differs from run manifest job")
        if checkpoint.get("search_completed") is not True:
            errors.append(f"checkpoint {job_id} is not marked search_completed")

        checkpoint_rules = checkpoint.get("rules")
        if not isinstance(checkpoint_rules, list):
            errors.append(f"checkpoint {job_id} rules must be a list")
            checkpoint_rules = []
        checkpoint_ids = [row.get("rule_id") for row in checkpoint_rules if isinstance(row, dict)]
        if len(checkpoint_ids) != len(checkpoint_rules) or len(checkpoint_ids) != len(set(checkpoint_ids)):
            errors.append(f"checkpoint {job_id} has duplicate/malformed rules")
        if set(checkpoint_ids) != set(job.get("rule_ids", [])):
            errors.append(f"checkpoint {job_id} rule coverage differs from run manifest")

        artifact_path = checkpoint.get("artifact_path")
        expected_artifact = _expected_artifact_path(root, manifest, manifest_hash, job)
        if not isinstance(artifact_path, str) or Path(artifact_path).resolve() != expected_artifact.resolve():
            errors.append(f"checkpoint {job_id} artifact path is not the canonical job artifact")
            artifact = None
        else:
            artifact = _read_json(Path(artifact_path), errors, f"artifact {job_id}")
        if artifact is not None:
            actual_artifact_hash = file_hash(Path(artifact_path))
            if checkpoint.get("artifact_sha256") != actual_artifact_hash:
                errors.append(f"artifact hash mismatch for {job_id}")
            if artifact.get("job_id") != job_id:
                errors.append(f"artifact {job_id} belongs to another job")
            if artifact.get("registry_sha256") not in (None, registry_hash):
                errors.append(f"artifact {job_id} registry hash differs from registry")
            if artifact.get("implementation_sha256") not in (None, checkpoint.get("implementation_sha256")):
                errors.append(f"artifact {job_id} implementation hash differs from checkpoint")
            if "rules" not in artifact or artifact.get("rules") != checkpoint_rules:
                errors.append(f"artifact {job_id} rules do not exactly match checkpoint")
            records = artifact.get("records")
            if not isinstance(records, list):
                errors.append(f"artifact {job_id} records must be a list")
                records = []
        else:
            records = []

        implementation = checkpoint.get("implementation_sha256")
        if isinstance(implementation, str):
            implementation_hashes.add(implementation)

        rule_rows: dict[str, dict[str, Any]] = {}
        for row in checkpoint_rules:
            if not isinstance(row, dict):
                continue
            rid = row.get("rule_id")
            if isinstance(rid, str):
                rule_rows[rid] = row
            meta = _rule_meta(registry.get("_rule_map", {}), str(rid))
            if meta is None:
                errors.append(f"checkpoint {job_id} references rule absent from registry: {rid}")
                continue
            for key in ("method_id", "branch"):
                if row.get(key) != meta.get(key):
                    errors.append(f"checkpoint {job_id} rule {rid} {key} differs from registry")
            observed_unit = row.get("observation_unit")
            allowed_units = {meta.get("observation_unit"), meta.get("transport_observation_unit")}
            allowed_units.discard(None)
            if observed_unit not in allowed_units:
                errors.append(f"checkpoint {job_id} rule {rid} observation_unit differs from registry")
            if row.get("search_executed") is not True:
                errors.append(f"checkpoint {job_id} rule {rid} search_executed is not true")
            if row.get("status") not in _STATUSES:
                errors.append(f"checkpoint {job_id} rule {rid} has invalid status")
            holes = row.get("population_holes")
            if not isinstance(holes, list):
                errors.append(f"checkpoint {job_id} rule {rid} population_holes must be a list")
            declared = row.get("summary")
            if not isinstance(declared, dict):
                errors.append(f"checkpoint {job_id} rule {rid} summary must be an object")
                continue
            matching = [record for record in records if _record_rule_id(record) == rid]
            try:
                actual = _summary(matching)
            except ReportingError as exc:
                errors.append(f"artifact {job_id} rule {rid}: {exc}")
                continue
            if not _summary_equal(actual, declared):
                errors.append(f"checkpoint {job_id} rule {rid} summary differs from artifact records")
            if row.get("status") == "missing_data" and matching:
                errors.append(f"checkpoint {job_id} rule {rid} marked missing_data with records")
            if row.get("status") == "completed" and holes:
                errors.append(f"checkpoint {job_id} rule {rid} has holes but status completed")

        for record in records:
            if not isinstance(record, dict):
                errors.append(f"artifact {job_id} contains a non-object record")
                continue
            rid = _record_rule_id(record)
            oid = _record_identity(record)
            if rid is None or oid is None:
                errors.append(f"artifact {job_id} record lacks rule/opportunity identity")
                continue
            if rid not in rule_rows:
                errors.append(f"artifact {job_id} record has rule outside checkpoint: {rid}")
            if oid in seen_opportunities:
                errors.append(f"duplicate opportunity across empirical artifacts: {oid}")
            seen_opportunities.add(oid)
            opportunity = record.get("opportunity") if isinstance(record.get("opportunity"), Mapping) else {}
            if opportunity.get("partition_id") is not None and str(opportunity.get("partition_id")) != str(checkpoint.get("partition_id")):
                errors.append(f"artifact {job_id} opportunity {oid} partition mismatch")
            if opportunity.get("instrument_id") is not None and not _same_id(opportunity.get("instrument_id"), checkpoint.get("instrument_id")):
                errors.append(f"artifact {job_id} opportunity {oid} instrument mismatch")
            record_meta = _rule_meta(registry.get("_rule_map", {}), rid)
            if record_meta is not None:
                record_unit = _record_value(record, "observation_unit")
                allowed_units = {record_meta.get("observation_unit"), record_meta.get("transport_observation_unit")}
                allowed_units.discard(None)
                if record_unit is not None and record_unit not in allowed_units:
                    errors.append(f"artifact {job_id} opportunity {oid} observation_unit differs from registry transport")
                record_evidence = _record_value(record, "evidence_mode")
                registry_evidence = record_meta.get("evidence_mode")
                if record_evidence is not None and registry_evidence is not None and record_evidence != registry_evidence:
                    errors.append(f"artifact {job_id} opportunity {oid} evidence_mode differs from registry")
            replay = record.get("replay") if isinstance(record.get("replay"), Mapping) else {}
            if replay.get("verdict") not in _VERDICTS:
                errors.append(f"artifact {job_id} opportunity {oid} has invalid verdict")

        triples.append({
            "job": job,
            "checkpoint": checkpoint,
            "artifact": artifact,
            "records": records,
            "rule_rows": rule_rows,
            "valid_identity": True,
        })

    if len(implementation_hashes) > 1:
        warnings.append("implementation hash differs across accepted checkpoints: " + ", ".join(sorted(implementation_hashes)))
    return triples, jobs, seen_job_ids


def _scope_for_jobs(jobs: Iterable[Mapping[str, Any]], triples: list[Mapping[str, Any]], rule_id: str | None = None) -> dict[str, Any]:
    expected = [job for job in jobs if rule_id is None or rule_id in (job.get("rule_ids") or [])]
    accepted: dict[str, Mapping[str, Any]] = {}
    for triple in triples:
        job = triple["job"]
        if rule_id is None or rule_id in (job.get("rule_ids") or []):
            accepted[job.get("job_id")] = triple
    missing = 0
    for triple in accepted.values():
        row_map = triple.get("rule_rows", {})
        if rule_id is not None:
            row = row_map.get(rule_id)
            if isinstance(row, Mapping) and row.get("status") == "missing_data":
                missing += 1
        elif any(isinstance(row, Mapping) and row.get("status") == "missing_data" for row in row_map.values()):
            missing += 1
    scanned = len(accepted)
    eligible = len(expected)
    remaining = max(0, eligible - scanned)
    return {"eligible": eligible, "scanned": scanned, "missing": missing, "remaining": remaining,
            "eligible_jobs": eligible, "scanned_jobs": scanned}


def _job_year(job_or_triple: Mapping[str, Any]) -> str:
    """Return the partition year for a manifest job or accepted triple."""

    if isinstance(job_or_triple.get("job"), Mapping):
        return _job_year(job_or_triple["job"])
    partition = job_or_triple.get("partition") if isinstance(job_or_triple.get("partition"), Mapping) else None
    if partition is not None:
        value = _partition_value(partition, "date", "session_date")
    else:
        value = _partition_value(job_or_triple, "session_date", "date")
    text = str(value) if value is not None else "unknown"
    return text[:4] if len(text) >= 4 and text[:4].isdigit() else "unknown"


def _job_instrument(job_or_triple: Mapping[str, Any]) -> str:
    """Normalize JSON number/string instrument spellings for group keys."""

    if isinstance(job_or_triple.get("job"), Mapping):
        return _job_instrument(job_or_triple["job"])
    partition = job_or_triple.get("partition") if isinstance(job_or_triple.get("partition"), Mapping) else None
    value = _partition_value(partition, "instrument_id", "instrument") if partition is not None else _partition_value(job_or_triple, "instrument_id", "instrument")
    return str(value) if value is not None else "unknown"


def _expected_artifact_path(root: Path, manifest: Mapping[str, Any], manifest_hash: str, job: Mapping[str, Any]) -> Path:
    """Resolve the artifact layout for legacy and versioned empirical runs."""

    partition = job.get("partition") if isinstance(job.get("partition"), Mapping) else {}
    partition_id = partition.get("partition_id", partition.get("id"))
    if manifest.get("run_version") is not None:
        # Reporting revisions isolate artifacts by their frozen manifest
        # prefix.  This prevents a checkpoint from a different exposure
        # revision being accepted merely because its job ID is familiar.
        return root / "artifacts" / manifest_hash[:16] / str(job.get("job_id")) / "records.json"
    return root / "artifacts" / f"{job.get('cohort')}--{partition_id}" / "records.json"


def _make_group_rows(
    registry_rules: Mapping[str, Mapping[str, Any]],
    triples: list[Mapping[str, Any]],
    jobs: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build compatible observed groups while retaining partial populations.

    A missing-data partition can share a semantic group with a populated
    partition.  Its missing status makes the *full-population* rate
    unavailable, but it must not erase the observed counts from the populated
    partition.  ``observed_counts`` is therefore kept independently from the
    conditional/full-population fields.
    """

    jobs = jobs or {}
    groups: dict[tuple[Any, ...], dict[str, Any]] = {}
    for triple in triples:
        job = triple["job"]
        checkpoint = triple["checkpoint"]
        records = triple["records"]
        for rid, rule_row in triple["rule_rows"].items():
            meta = registry_rules.get(rid, {})
            matching = [record for record in records if _record_rule_id(record) == rid]
            # Missing data has no denominator.  Keep a scope row so that a
            # report cannot silently turn unavailable input into zero outcomes.
            record_groups: dict[tuple[Any, ...], list[Mapping[str, Any]]] = defaultdict(list)
            if matching:
                for record in matching:
                    evidence = _record_value(record, "evidence_mode", meta.get("evidence_mode", "unknown"))
                    # The registry's observation_unit is the semantic unit
                    # used for grouping.  Records may carry its transport
                    # spelling (for example opening_period_state); the
                    # identity check above admits only those two spellings.
                    unit = meta.get("observation_unit", "unknown")
                    instrument = _record_value(record, "instrument_id", checkpoint.get("instrument_id"))
                    year = _record_year(record, checkpoint.get("session_date"))
                    key = (job.get("cohort"), rid, year, str(instrument), evidence, unit)
                    record_groups[key].append(record)
            else:
                evidence = meta.get("evidence_mode", "unknown")
                unit = meta.get("observation_unit", "unknown")
                year = _record_year({}, checkpoint.get("session_date"))
                key = (job.get("cohort"), rid, year, str(checkpoint.get("instrument_id")), evidence, unit)
                record_groups[key] = []
            for key, rows in record_groups.items():
                cohort, rule_id, year, instrument, evidence, unit = key
                unavailable = rule_row.get("status") == "missing_data"
                counts = _group_counts(rows, unavailable)
                leakage = timing = proxy = 0
                for record in rows:
                    l, t, p = _source_counts(record)
                    leakage += l
                    timing += t
                    proxy += p
                group = groups.setdefault(key, {
                    "family": meta.get("method_id", rule_row.get("method_id")),
                    "method_id": meta.get("method_id", rule_row.get("method_id")),
                    "rule_id": rid,
                    "branch": meta.get("branch", rule_row.get("branch")),
                    "cohort": cohort,
                    "year": year,
                    "instrument_id": instrument,
                    "evidence_mode": evidence,
                    "observation_unit": unit,
                    "statuses": [],
                    "population_holes": [],
                    "eligible": 0,
                    "scanned": 0,
                    "missing": 0,
                    "records": 0,
                    "p": 0,
                    "f": 0,
                    "u": 0,
                    "n": 0,
                    "N": 0,
                    "leakage": 0,
                    "timing_violations": 0,
                    "proxy_as_faithful": 0,
                    "faithful_disagreements": None,
                })
                group["statuses"].append(rule_row.get("status"))
                group["population_holes"].extend(rule_row.get("population_holes") or [])
                if not unavailable:
                    for field in ("p", "f", "u", "n", "N"):
                        group[field] += counts[field] or 0
                group["records"] += len(rows)
                group["leakage"] += leakage
                group["timing_violations"] += timing
                group["proxy_as_faithful"] += proxy
    result: list[dict[str, Any]] = []
    for group in groups.values():
        statuses = set(group.pop("statuses"))
        # Scope is measured at rule/manifest level.  Applying it to every
        # compatible group makes an otherwise populated group visibly
        # conditional when another eligible partition is unscanned.
        rule_id = str(group["rule_id"])
        rule_jobs = [job for job in jobs.values()
                     if rule_id in (job.get("rule_ids") or [])
                     and job.get("cohort") == group["cohort"]
                     and _job_year(job) == str(group["year"])
                     and _job_instrument(job) == str(group["instrument_id"])]
        group["eligible"] = len(rule_jobs)
        group["scanned"] = sum(1 for triple in triples
                               if rule_id in (triple["job"].get("rule_ids") or [])
                               and triple["job"].get("cohort") == group["cohort"]
                               and _job_year(triple) == str(group["year"])
                               and _job_instrument(triple) == str(group["instrument_id"]))
        group["missing"] = sum(
            1 for triple in triples
            if rule_id in (triple["job"].get("rule_ids") or [])
            and triple["job"].get("cohort") == group["cohort"]
            and _job_year(triple) == str(group["year"])
            and _job_instrument(triple) == str(group["instrument_id"])
            and isinstance(triple.get("rule_rows", {}).get(rule_id), Mapping)
            and triple["rule_rows"][rule_id].get("status") == "missing_data"
        )
        group["remaining"] = max(0, group["eligible"] - group["scanned"])
        # Unscanned jobs are counted at rule scope.  A group's own records
        # remain visible, but its full-population rate is conditional.
        group["population_complete"] = (
            group["eligible"] > 0
            and group["remaining"] == 0
            and group["missing"] == 0
            and not group["population_holes"]
        )
        if "missing_data" in statuses:
            status = "data_hole"
        elif group["remaining"]:
            status = "unfinished"
        elif "completed_with_population_holes" in statuses:
            status = "completed_with_population_holes"
        elif group["records"] == 0:
            status = "no_candidates"
        else:
            status = "measured"
        # These are the observations actually present in artifacts, before a
        # missing/unscanned population is considered.
        observed = {"p": group["p"], "f": group["f"], "u": group["u"], "n": group["n"], "N": group["N"]}
        group["observed_counts"] = observed
        observed_n = observed["n"]
        observed_total = observed["N"]
        observed_rate = None if observed_n == 0 else observed["p"] / observed_n
        if observed_total:
            observed_lo = Fraction(observed["p"], observed_total)
            observed_hi = Fraction(observed["p"] + observed["u"], observed_total)
            observed_interval = [float(observed_lo), float(observed_hi)]
            observed_interval_exact = [[observed_lo.numerator, observed_lo.denominator], [observed_hi.numerator, observed_hi.denominator]]
        else:
            observed_interval = None
            observed_interval_exact = None
        group["observed_rate"] = observed_rate
        group["observed_rate_exact"] = None if observed_n == 0 else [observed["p"], observed_n]
        group["observed_interval"] = observed_interval
        group["observed_interval_exact"] = observed_interval_exact

        if group["population_complete"]:
            # A completed zero-candidate group is a known zero population.
            group.update(observed)
            group["rate"] = observed_rate
            group["rate_exact"] = group["observed_rate_exact"]
            group["interval"] = observed_interval
            group["interval_exact"] = observed_interval_exact
        elif observed_total:
            # Keep observed counts despite an incomplete full population, but
            # never present their conditional rate as a full-population rate.
            group.update(observed)
            group["rate"] = None
            group["rate_exact"] = None
            group["interval"] = None
            group["interval_exact"] = None
        else:
            # For an incomplete all-zero group, zero is not an empirical
            # result: surface it only under observed_counts.
            group.update({"p": None, "f": None, "u": None, "n": None, "N": None,
                          "rate": None, "rate_exact": None, "interval": None, "interval_exact": None})
        group["status"] = status
        group["complete"] = group["population_complete"]
        group["denominator"] = (
            "Initial market opportunities in this rule/year/instrument/evidence/observation-unit group; full-population rate unavailable until all eligible partitions are scanned. Conditional observed rate is reported separately."
            if not group["population_complete"] and observed_total
            else "Unavailable: required input/search was missing; no zero outcome implied."
            if not group["population_complete"]
            else "Initial market opportunities in this rule/year/instrument/evidence/observation-unit group."
        )
        group["population_holes"] = sorted(set(str(hole) for hole in group["population_holes"]))
        group["variant"] = _variant_text(group)
        result.append(group)
    result.sort(key=lambda row: (str(row.get("family")), str(row.get("rule_id")), str(row.get("cohort")), str(row.get("year")), str(row.get("instrument_id")), str(row.get("evidence_mode")), str(row.get("observation_unit"))))
    return result


def _rule_reports(
    registry_rules: Mapping[str, Mapping[str, Any]],
    extra_units: list[Mapping[str, Any]],
    jobs: Mapping[str, Mapping[str, Any]],
    triples: list[Mapping[str, Any]],
    groups: list[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    def empty_counts() -> dict[str, Any]:
        return {"p": None, "f": None, "u": None, "n": None, "N": None, "rate": None,
                "rate_exact": None, "interval": None, "interval_exact": None}

    def observed_total(rule_groups: list[Mapping[str, Any]]) -> tuple[dict[str, int], bool]:
        """Sum only records actually present; return counts and known flag."""
        p = f = u = n = total = 0
        known = False
        for group in rule_groups:
            counts = group.get("observed_counts")
            if not isinstance(counts, Mapping):
                continue
            p += _as_int(counts.get("p"), 0)
            f += _as_int(counts.get("f"), 0)
            u += _as_int(counts.get("u"), 0)
            n += _as_int(counts.get("n"), 0)
            total += _as_int(counts.get("N"), 0)
            # A completed zero-candidate partition is known evidence even
            # though it contributes no record rows.
            if _as_int(group.get("records"), 0) > 0 or (
                group.get("population_complete") is True and group.get("status") == "no_candidates"
            ):
                known = True
        return {"p": p, "f": f, "u": u, "n": n, "N": total}, known

    by_rule_group: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for group in groups:
        by_rule_group[group["rule_id"]].append(group)
    rule_reports: list[dict[str, Any]] = []
    for rid, meta in registry_rules.items():
        scope = _scope_for_jobs(jobs.values(), triples, rid)
        rule_groups = [dict(group) for group in by_rule_group.get(rid, [])]
        observed, observed_known = observed_total(rule_groups)
        observed_counts = dict(observed) if meta.get("supported", False) else {
            "p": None, "f": None, "u": None, "n": None, "N": None,
        }
        if not meta.get("supported", False):
            status = str(meta.get("status", "unavailable_definition"))
            counts = empty_counts()
            population_complete = False
        elif scope["remaining"]:
            status = "unfinished"
            population_complete = False
        elif scope["missing"]:
            status = "data_hole"
            population_complete = False
        elif any(group.get("population_holes") for group in rule_groups):
            status = "completed_with_population_holes"
            population_complete = False
        elif scope["eligible"] == 0:
            status = "unfinished"
            population_complete = False
        elif observed["N"] == 0:
            status = "no_candidates"
            population_complete = True
        else:
            status = "measured"
            population_complete = True
        # Rule-level rates are never pooled across year/instrument/evidence /
        # semantic-unit groups.  Preserve observed counts for a partial
        # population, but make the full-population count null only when no
        # observed record exists (the zero case is exposed below).
        if meta.get("supported", False):
            if observed["N"] > 0:
                counts = {**observed, "rate": None, "rate_exact": None, "interval": None, "interval_exact": None}
            elif population_complete:
                counts = {**observed, "rate": None, "rate_exact": None, "interval": None, "interval_exact": None}
            else:
                counts = empty_counts()
        leakage = sum(_as_int(group.get("leakage"), 0) for group in rule_groups)
        timing = sum(_as_int(group.get("timing_violations"), 0) for group in rule_groups)
        proxy = sum(_as_int(group.get("proxy_as_faithful"), 0) for group in rule_groups)
        rule_reports.append({
            "rule_id": rid,
            "method_id": meta.get("method_id"),
            "branch": meta.get("branch"),
            "variant": meta.get("variant"),
            "supported": bool(meta.get("supported", False)),
            "disposition": meta.get("status"),
            "source_method_verdict": meta.get("source_method_verdict", "unknown"),
            "evidence_mode": meta.get("evidence_mode"),
            "observation_unit": meta.get("observation_unit"),
            "groups": rule_groups,
            "scope": scope,
            **counts,
            "observed_counts": observed_counts,
            "observed_known": observed_known,
            "population_complete": population_complete,
            "rate_scope": "grouped; no pooled rate" if rule_groups else None,
            "faithful_disagreements": None,
            "leakage": leakage,
            "timing_violations": timing,
            "proxy_as_faithful": proxy,
            "status": status,
            "notes": "Source-faithful disposition remains separate from empirical comparison evidence.",
        })
    extra_reports: list[dict[str, Any]] = []
    for unit in extra_units:
        extra_reports.append({
            **dict(unit),
            "p": None,
            "f": None,
            "u": None,
            "n": None,
            "N": None,
            "rate": None,
            "rate_exact": None,
            "interval": None,
            "interval_exact": None,
            "scope": {"eligible": 0, "scanned": 0, "missing": 0, "remaining": 0, "eligible_jobs": 0, "scanned_jobs": 0},
            "population_complete": False,
            "observed_counts": {"p": None, "f": None, "u": None, "n": None, "N": None},
            "status": unit.get("status", "supplied_only"),
            "denominator": "Unavailable source/process/state observation; no market proxy admitted.",
            "proxy_as_faithful": 0,
            "leakage": 0,
        })
    return rule_reports, extra_reports


def _family_reports(registry_rules: Mapping[str, Mapping[str, Any]], rule_reports: list[Mapping[str, Any]], groups: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    by_family: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for rid, meta in registry_rules.items():
        by_family[str(meta.get("method_id"))].append(next(row for row in rule_reports if row["rule_id"] == rid))
    family_rows: list[dict[str, Any]] = []
    for family, rows in sorted(by_family.items()):
        variants = [dict(group) for group in groups if group.get("family") == family]
        observed_rows = [row for row in rows if isinstance(row.get("observed_counts"), Mapping)]
        known = any(row.get("observed_known") is True for row in observed_rows)
        observed_counts = None
        if known:
            observed_counts = {
                "p": sum(_as_int(row["observed_counts"].get("p"), 0) for row in observed_rows),
                "f": sum(_as_int(row["observed_counts"].get("f"), 0) for row in observed_rows),
                "u": sum(_as_int(row["observed_counts"].get("u"), 0) for row in observed_rows),
                "n": sum(_as_int(row["observed_counts"].get("n"), 0) for row in observed_rows),
                "N": sum(_as_int(row["observed_counts"].get("N"), 0) for row in observed_rows),
            }
        # Family n is an additive count of observed records across separate
        # branch denominators.  It is null when the family is wholly
        # unavailable; a known completed zero population correctly yields 0.
        n = observed_counts["n"] if observed_counts is not None else None
        statuses = {str(row.get("status")) for row in rows}
        if any(status in {"invalid", "unfinished"} for status in statuses):
            status = "unfinished"
        elif any(status in {"data_hole", "completed_with_population_holes"} for status in statuses):
            status = "data_hole"
        elif any(status == "measured" for status in statuses):
            status = "measured"
        elif any(status == "no_candidates" for status in statuses):
            status = "no_candidates"
        else:
            status = "unavailable_definition"
        family_rows.append({
            "family": family,
            "method_id": family,
            "rules": [row["rule_id"] for row in rows],
            "variants": variants,
            "n": n,
            "observed_counts": observed_counts,
            "population_complete": bool(rows) and all(
                row.get("population_complete") is True for row in rows if row.get("supported", False)
            ) and any(row.get("supported", False) for row in rows),
            "rate": None,
            "faithful_disagreements": None,
            "status": status,
            "notes": "Family n is additive observed records across separate branch denominators; no family rate is pooled.",
        })
    return family_rows


def _markdown(doc: Mapping[str, Any], report_path: str = "RESULTS.md") -> str:
    lines = [
        "# Empirical replay results",
        "",
        f"schema: `{doc.get('schema')}`",
        f"status: `{doc.get('status')}`",
        f"registry_sha256: `{doc.get('registry', {}).get('sha256')}`",
        f"run_manifest_sha256: `{doc.get('run_manifest', {}).get('sha256')}`",
        "",
        "The report counts observed initial opportunities from validated replay artifacts. Source-faithful rule dispositions, missing inputs, and later private selections remain separate. Rates are shown only within compatible rule/year/instrument/evidence/observation-unit groups.",
        "",
        "## Scope",
        "",
        "cohort | eligible | scanned | missing | remaining",
        "--- | ---: | ---: | ---: | ---:",
    ]
    for cohort, scope in sorted(doc.get("scope", {}).get("cohorts", {}).items()):
        lines.append(f"{cohort} | {scope.get('eligible', 0)} | {scope.get('scanned', 0)} | {scope.get('missing', 0)} | {scope.get('remaining', 0)}")
    lines.extend(["", "## Family reports", "", "family | n | status | variants", "--- | ---: | --- | ---"])
    for family in doc.get("family_reports", []):
        n = "—" if family.get("n") is None else str(family.get("n"))
        variants = "; ".join(str(row.get("variant")) for row in family.get("variants", [])) or "—"
        lines.append(f"{family.get('family')} | {n} | {family.get('status')} | {variants}")
    # Workspace instructions require these two exact table headers after the
    # family reports.  Keep their column order stable for machine audits.
    lines.extend(["", "## PHASE", "", PHASE_TABLE, "--- | --- | ---: | --- | --- | ---"])
    phase_rows = []
    for family in doc.get("family_reports", []):
        variants = family.get("variants") or [
            {"rule_id": ",".join(family.get("rules", [])), "cohort": "—", "year": "—", "instrument_id": "—", "evidence_mode": "—", "observation_unit": "—", "n": family.get("n"), "status": family.get("status")}
        ]
        for variant in variants:
            n = "—" if variant.get("n") is None else str(variant.get("n"))
            phase_rows.append(f"{family.get('family')} | {_variant_text(variant)} | {n} | — | {variant.get('status', family.get('status'))} | {report_path}")
    lines.extend(phase_rows or [f"— | — | — | — | {doc.get('status')} | {report_path}"])
    lines.extend(["", "## AUDIT", "", AUDIT_TABLE, "--- | --- | --- | --- | ---: | ---: | ---"])
    for row in doc.get("audit", []):
        lines.append(f"{row.get('family')} | {row.get('id')} | {row.get('verdict')} | {row.get('fixture')} | {row.get('leakage')} | {row.get('proxy_as_faithful')} | {row.get('notes')}")
    lines.append("")
    return "\n".join(lines)


def build_results(
    root: str | Path = ROOT,
    registry_path: str | Path | None = None,
    run_manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build a validated report document from one frozen empirical run."""

    root = Path(root).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    registry_file = _registry_path(root, registry_path)
    manifest_file = _manifest_path(root, run_manifest_path)
    registry = _read_json(registry_file, errors, "registry") or {}
    manifest = _read_json(manifest_file, errors, "run manifest") or {}
    registry_hash_value = registry.get("registry_sha256")
    registry_hash = str(registry_hash_value) if registry_hash_value is not None else ""
    if not registry_hash:
        errors.append("registry lacks registry_sha256")
    elif registry_hash != _canonical_hash_without(registry, "registry_sha256"):
        errors.append("registry self hash mismatch")
    declared_manifest_hash, recomputed_manifest_hash = _manifest_hash(manifest)
    manifest_hash = str(declared_manifest_hash) if declared_manifest_hash is not None else ""
    if declared_manifest_hash is None:
        errors.append("run manifest lacks run_manifest_sha256/manifest_sha256")
    elif declared_manifest_hash != recomputed_manifest_hash:
        errors.append("run manifest self hash mismatch")

    raw_rules = registry.get("rules")
    if not isinstance(raw_rules, list):
        errors.append("registry rules must be a list")
        raw_rules = []
    registry_rules: dict[str, Mapping[str, Any]] = {}
    for row in raw_rules:
        if not isinstance(row, dict) or not isinstance(row.get("rule_id"), str):
            errors.append("registry contains malformed rule")
            continue
        if row["rule_id"] in registry_rules:
            errors.append(f"duplicate registry rule: {row['rule_id']}")
        registry_rules[row["rule_id"]] = row
    extras = registry.get("extra_observation_units")
    if not isinstance(extras, list):
        errors.append("registry extra_observation_units must be a list")
        extras = []
    # The collector reads this private map to avoid changing its public job
    # schema or copying a potentially large registry object into every row.
    registry_for_collection = dict(registry)
    registry_for_collection["_rule_map"] = registry_rules
    triples, jobs, seen_job_ids = _validate_and_collect(root, registry_for_collection, manifest, registry_hash, manifest_hash, errors, warnings)
    if set(jobs) - seen_job_ids:
        # Missing checkpoints are expected while a run is unfinished.  They
        # become scope.remaining and do not invalidate the manifest itself.
        warnings.append(f"{len(set(jobs) - seen_job_ids)} manifest jobs have no checkpoint yet")

    groups = _make_group_rows(registry_rules, triples, jobs)
    rule_reports, extra_reports = _rule_reports(registry_rules, extras, jobs, triples, groups)
    families = _family_reports(registry_rules, rule_reports, groups)

    cohorts: dict[str, dict[str, Any]] = {}
    for cohort in sorted({str(job.get("cohort")) for job in jobs.values()} | {str(triple["job"].get("cohort")) for triple in triples}):
        cohorts[cohort] = _scope_for_jobs([job for job in jobs.values() if job.get("cohort") == cohort], [triple for triple in triples if triple["job"].get("cohort") == cohort])
    scope = {"cohorts": cohorts,
             "eligible": sum(row["eligible"] for row in cohorts.values()),
             "scanned": sum(row["scanned"] for row in cohorts.values()),
             "missing": sum(row["missing"] for row in cohorts.values()),
             "remaining": sum(row["remaining"] for row in cohorts.values())}

    # A proxy or timing violation is a contract failure, even if the rows are
    # otherwise hash-valid.  The report keeps their counts for auditability.
    for row in rule_reports:
        if row.get("leakage") or row.get("timing_violations") or row.get("proxy_as_faithful"):
            errors.append(f"rule {row.get('rule_id')} contains forbidden leakage/timing/proxy evidence")

    if errors:
        status = "invalid"
    elif scope["remaining"]:
        status = "partial_unfinished"
    elif scope["missing"]:
        status = "data_hole"
    elif any(row.get("n") is not None for row in rule_reports):
        status = "measured"
    else:
        status = "no_candidates"

    audit: list[dict[str, Any]] = []
    for row in rule_reports:
        audit.append({
            "family": row.get("method_id"),
            "id": row.get("rule_id"),
            "verdict": row.get("source_method_verdict", "unknown"),
            "fixture": "not_run",
            "leakage": row.get("leakage", 0),
            "proxy_as_faithful": row.get("proxy_as_faithful", 0),
            "notes": f"{row.get('status')}; disposition={row.get('disposition')}; eligible={row.get('scope', {}).get('eligible')}; scanned={row.get('scope', {}).get('scanned')}; missing={row.get('scope', {}).get('missing')}; remaining={row.get('scope', {}).get('remaining')}",
        })
    for row in extra_reports:
        audit.append({
            "family": row.get("method_id"),
            "id": row.get("unit_id"),
            "verdict": "unknown",
            "fixture": "not_run",
            "leakage": 0,
            "proxy_as_faithful": 0,
            "notes": f"{row.get('status')}; no market proxy admitted",
        })

    return {
        "schema": SCHEMA,
        "version": REPORT_VERSION,
        "status": status,
        "registry": {"path": str(registry_file.resolve()), "sha256": registry_hash, "version": registry.get("version"), "rule_count": len(registry_rules), "extra_unit_count": len(extras)},
        "run_manifest": {"path": str(manifest_file.resolve()), "sha256": manifest_hash, "job_count": len(jobs)},
        "validation": {"valid": not errors, "errors": errors, "warnings": warnings, "implementation_hashes": sorted({str(triple["checkpoint"].get("implementation_sha256")) for triple in triples if triple["checkpoint"].get("implementation_sha256") is not None})},
        "scope": scope,
        "groups": groups,
        "rule_reports": rule_reports,
        "extra_observation_units": extra_reports,
        "family_reports": families,
        "audit": audit,
    }


def write_results(
    root: str | Path = ROOT,
    registry_path: str | Path | None = None,
    run_manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build and atomically write ``RESULTS.json`` and ``RESULTS.md``."""

    root = Path(root).resolve()
    document = build_results(root, registry_path=registry_path, run_manifest_path=run_manifest_path)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / "RESULTS.json"
    markdown_path = root / "RESULTS.md"
    json_payload = json.dumps(document, indent=2, sort_keys=True, allow_nan=False) + "\n"
    json_tmp = json_path.with_suffix(".json.tmp")
    json_tmp.write_text(json_payload)
    json_tmp.replace(json_path)
    md_payload = _markdown(document, str(markdown_path))
    md_tmp = markdown_path.with_suffix(".md.tmp")
    md_tmp.write_text(md_payload)
    md_tmp.replace(markdown_path)
    return document


def report(
    root: str | Path = ROOT,
    registry_path: str | Path | None = None,
    run_manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    """Compatibility alias used by the empirical runner's report stage."""

    return write_results(root, registry_path=registry_path, run_manifest_path=run_manifest_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--run-manifest", type=Path)
    args = parser.parse_args(argv)
    document = report(args.root, args.registry, args.run_manifest)
    print(json.dumps({"status": document["status"], "valid": document["validation"]["valid"], "results_json": str(Path(args.root).resolve() / "RESULTS.json"), "results_md": str(Path(args.root).resolve() / "RESULTS.md")}, sort_keys=True))
    return 0 if document["validation"]["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
