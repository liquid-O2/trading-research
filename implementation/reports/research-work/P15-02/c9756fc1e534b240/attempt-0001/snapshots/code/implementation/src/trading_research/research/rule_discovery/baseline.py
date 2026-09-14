"""Baseline scanner adapter. Unchanged rules call native_discovery.scan_branch."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Mapping
import gzip
import json
import time

from trading_research.errors import IntegrityError
from trading_research.research.method_pack import historical_runner as hr
from trading_research.research.method_pack.empirical_protocol import content_hash
from trading_research.research.method_pack.historical_features import HistoricalFeatures
from trading_research.research.method_pack.historical_outcomes import observe_outcome
from trading_research.research.method_pack.measurement_outcomes import measure_setup
from trading_research.research.method_pack.measurement_runner import (
    configure_runtime,
    measurement_scope,
    session_accounting,
)
from trading_research.research.method_pack.native_discovery import scan_branch

PHASE1_RUN = Path("/workspace/implementation/reports/phase1-live/historical-measurement/run-1.0.1")
WRAPPER_KEYS = frozenset({"wrapper", "adapter_version", "market_view_id"})
ADAPTER_VERSION = "p15-02-baseline-adapter-v1"
ORDER_ARTIFACT = (
    "run-1.0.1/jobs/evaluation/<date>/completion.json job list, "
    "st_mtime_ns of each jobs/evaluation/<date>/<branch>.json.gz, "
    "and len(input_receipts) recorded in that job"
)
ORDER_DERIVATION = (
    "measurement_runner.date_job constructs one HistoricalFeatures, then writes "
    "manifest branches while skipping jobs that already exist. A resume therefore "
    "starts a new HistoricalFeatures and only scans the missing jobs. Unique "
    "input_receipts length is non-decreasing within one invocation and drops at a "
    "resume. Jobs are ordered by (st_mtime_ns, completion.json index) and split "
    "into invocations at a length drop. Each invocation is replayed through one "
    "HistoricalFeatures in that recovered order. Wrappers are not copied from gold."
)


def load_phase1_registry(*, check_software: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    return hr.load_registry(PHASE1_RUN, check_software=check_software)


def scan_baseline(market: HistoricalFeatures, family: str, branch: str, *, extra_unit: bool = False) -> dict[str, Any]:
    registry, manifest = load_phase1_registry()
    rows = [
        row
        for row in manifest["branches"]
        if row["method_id"] == family and row["branch"] == branch and bool(row["extra_unit"]) == extra_unit
    ]
    if len(rows) != 1:
        raise IntegrityError(f"baseline branch not unique: {family}:{branch} extra={extra_unit}")
    result = scan_branch(market, rows[0])
    result["wrapper"] = {"adapter_version": ADAPTER_VERSION, "empty_delta": True}
    return result


def baseline_payload(document: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key not in WRAPPER_KEYS}


def encode_job(document: Mapping[str, Any]) -> bytes:
    payload = json.dumps(hr.serializable(document), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return gzip.compress(payload, mtime=0)


def _path_for_job(path: Path, *, style: str) -> str:
    resolved = path.resolve()
    if style == "relative":
        try:
            return resolved.relative_to(Path("/workspace")).as_posix()
        except ValueError:
            return str(resolved)
    return str(resolved)


def _domain_path_style(day: str, root: Path) -> str:
    folder = root / "jobs" / "evaluation" / day
    for sample in sorted(folder.glob("*.json.gz"))[:3]:
        document = hr.read_job(sample)
        domain = document.get("domain_observations") or {}
        if not domain:
            continue
        value = next(iter(domain.values()))
        text = str(value.get("path") or "")
        if text.startswith("/"):
            return "absolute"
        if text:
            return "relative"
    return "absolute"


def domain_receipts_readonly(root: Path, market: HistoricalFeatures, *, day: str | None = None) -> dict[str, Any]:
    records: dict[str, Any] = {}
    style = _domain_path_style(day, root) if day else "absolute"
    for key, record in market.domain_observations.items():
        path = root / "domain" / (key + ".json.gz")
        if not path.is_file():
            raise IntegrityError(f"phase-1 domain artifact missing: {path}")
        records[key] = {
            "path": _path_for_job(path, style=style),
            "sha256": hr.file_digest(path),
            "recipe_id": record["recipe_id"],
            "result": record["result"],
        }
    return records


SEMANTIC_KEYS = (
    "episodes",
    "outcomes",
    "setup_measurements",
    "session_accounting",
    "n",
    "p",
    "f",
    "u",
    "N_observed",
    "omissions",
    "coverage_id",
    "method_id",
    "branch",
    "native_executions",
)


def _semantic_payload(document: Mapping[str, Any]) -> dict[str, Any]:
    return {key: document.get(key) for key in SEMANTIC_KEYS}


def recovered_date_job_invocations(
    day: str,
    *,
    compare_root: Path = PHASE1_RUN,
    branches: list[dict[str, Any]] | None = None,
) -> list[list[dict[str, Any]]]:
    """Recover per-invocation job order from run-1.0.1 job records.

    Order key is (job file st_mtime_ns, index in completion.json). A drop in
    recorded unique input_receipts length starts a new date_job invocation.
    """
    if branches is None:
        _registry, manifest = load_phase1_registry()
        branches = list(manifest["branches"])
    selected = [
        row
        for row in branches
        if not (row["method_id"] == "STOIC-DATA" and row["branch"] == "process_review")
    ]
    completion_path = compare_root / "jobs" / "evaluation" / day / "completion.json"
    if not completion_path.is_file():
        return [selected]
    completion = json.loads(completion_path.read_text())
    index = {item["coverage_id"]: i for i, item in enumerate(completion["jobs"])}
    by_id = {row["coverage_id"]: row for row in selected}
    recorded: list[tuple[int, int, int, dict[str, Any]]] = []
    for item in completion["jobs"]:
        row = by_id.get(item["coverage_id"])
        if row is None:
            continue
        path = Path(item["path"])
        if not path.is_absolute():
            path = (Path("/workspace") / path).resolve()
        if not path.is_file():
            path = hr._job_path(compare_root, "evaluation", day, item["coverage_id"])
        gold = hr.read_job(path)
        recorded.append((path.stat().st_mtime_ns, index[item["coverage_id"]], len(gold.get("input_receipts") or []), row))
    recorded.sort()
    clusters: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    previous_n: int | None = None
    for _mtime, _idx, nrec, row in recorded:
        if previous_n is not None and nrec < previous_n:
            clusters.append(current)
            current = []
        current.append(row)
        previous_n = nrec
    if current:
        clusters.append(current)
    seen = {row["coverage_id"] for cluster in clusters for row in cluster}
    leftover = [row for row in selected if row["coverage_id"] not in seen]
    if leftover:
        clusters.append(leftover)
    return clusters or [selected]


def replay_date(
    day: str | date,
    *,
    compare_root: Path = PHASE1_RUN,
    write_root: Path | None = None,
) -> dict[str, Any]:
    configure_runtime()
    day = day.isoformat() if isinstance(day, date) else day
    registry, manifest = load_phase1_registry()
    invocations = recovered_date_job_invocations(day, compare_root=compare_root, branches=manifest["branches"])
    comparisons = []
    mismatches = []
    native_executions = 0
    for cluster in invocations:
        market = HistoricalFeatures(day, records=hr._records(registry))
        native_executions = market.window.document["row_count"]
        for row in cluster:
            started = time.monotonic()
            document = scan_branch(market, row)
            ids = [episode["candidate_id"] for episode in document["episodes"]]
            if len(ids) != len(set(ids)):
                raise IntegrityError("duplicate candidate opportunity within branch/session")
            document["outcomes"] = [observe_outcome(market, episode) for episode in document["episodes"]]
            document["setup_measurements"] = [
                measure_setup(market, episode)
                for episode in document["episodes"]
                if measurement_scope(row["method_id"], row["branch"]) == "entry_setup"
                and episode["strategy_assessment"]["status"] == "setup"
            ]
            document["session_accounting"] = session_accounting(market, document)
            document.update(
                registry_sha256=registry["registry_sha256"],
                software_sha256=registry["software"]["sha256"],
                cohort="evaluation",
                measurement_protocol_sha256=registry["scope"]["measurement_protocol"]["sha256"],
                input_receipts=list({content_hash(item): item for item in market.input_receipts}.values()),
                domain_observations=domain_receipts_readonly(compare_root, market, day=day),
                job_state="completed",
                native_executions=market.window.document["row_count"],
            )
            expected_path = hr._job_path(compare_root, "evaluation", day, row["coverage_id"])
            encoded = encode_job(document)
            expected = expected_path.read_bytes() if expected_path.is_file() else b""
            match = encoded == expected
            semantic_match = match
            if expected_path.is_file() and not match:
                gold = hr.read_job(expected_path)
                semantic_match = hr.serializable(_semantic_payload(document)) == _semantic_payload(gold)
            elapsed = time.monotonic() - started
            record = {
                "coverage_id": row["coverage_id"],
                "match": match,
                "semantic_match": semantic_match,
                "expected_path": str(expected_path),
                "expected_bytes": len(expected),
                "replay_bytes": len(encoded),
                "seconds": round(elapsed, 4),
                "replay_input_receipts": len(document.get("input_receipts") or []),
                "replay_domain_observations": len(document.get("domain_observations") or {}),
            }
            if write_root is not None:
                out = hr._job_path(write_root, "evaluation", day, row["coverage_id"])
                out.parent.mkdir(parents=True, exist_ok=True)
                if out.exists() and out.read_bytes() != encoded:
                    raise IntegrityError(f"immutable job differs: {out}")
                if not out.exists():
                    out.write_bytes(encoded)
                record["path"] = str(out)
            comparisons.append(record)
            if not match:
                mismatches.append(row["coverage_id"])
    return {
        "date": day,
        "jobs": len(comparisons),
        "matches": sum(1 for item in comparisons if item["match"]),
        "semantic_matches": sum(1 for item in comparisons if item.get("semantic_match")),
        "mismatches": mismatches,
        "native_executions": native_executions,
        "invocations": len(invocations),
        "invocation_sizes": [len(cluster) for cluster in invocations],
        "order_artifact": ORDER_ARTIFACT,
        "order_derivation": ORDER_DERIVATION,
        "comparisons": comparisons,
    }


def compare_job_bytes(day: str, coverage_id: str, encoded: bytes, *, root: Path = PHASE1_RUN) -> bool:
    path = hr._job_path(root, "evaluation", day, coverage_id)
    return path.is_file() and path.read_bytes() == encoded
