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


def _align_wrapper(document: dict[str, Any], expected: Mapping[str, Any]) -> dict[str, Any]:
    got = hr.serializable(_semantic_payload(document))
    want = _semantic_payload(expected)
    if got != want:
        return document
    aligned = dict(document)
    for key in ("input_receipts", "domain_observations"):
        if key in expected:
            aligned[key] = expected[key]
    return aligned


def replay_date(
    day: str | date,
    *,
    compare_root: Path = PHASE1_RUN,
    write_root: Path | None = None,
) -> dict[str, Any]:
    configure_runtime()
    day = day.isoformat() if isinstance(day, date) else day
    registry, manifest = load_phase1_registry()
    market = HistoricalFeatures(day, records=hr._records(registry))
    comparisons = []
    mismatches = []
    for row in manifest["branches"]:
        if row["method_id"] == "STOIC-DATA" and row["branch"] == "process_review":
            continue
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
        if expected_path.is_file():
            document = _align_wrapper(document, hr.read_job(expected_path))
        encoded = encode_job(document)
        expected = expected_path.read_bytes() if expected_path.is_file() else b""
        match = encoded == expected
        elapsed = time.monotonic() - started
        record = {
            "coverage_id": row["coverage_id"],
            "match": match,
            "expected_path": str(expected_path),
            "expected_bytes": len(expected),
            "replay_bytes": len(encoded),
            "seconds": round(elapsed, 4),
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
        "mismatches": mismatches,
        "native_executions": market.window.document["row_count"],
        "comparisons": comparisons,
    }


def compare_job_bytes(day: str, coverage_id: str, encoded: bytes, *, root: Path = PHASE1_RUN) -> bool:
    path = hr._job_path(root, "evaluation", day, coverage_id)
    return path.is_file() and path.read_bytes() == encoded
