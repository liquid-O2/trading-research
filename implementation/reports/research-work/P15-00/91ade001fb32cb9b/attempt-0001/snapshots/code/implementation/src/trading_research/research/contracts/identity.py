"""Canonical JSON identity, receipt serialization and immutable artifact writes."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from trading_research.errors import ContractError, IntegrityError
from trading_research.research.contracts.types import Coverage, freeze_json_value

SCHEMA_TASK_RECEIPT = "research-task-receipt-v2"
ASSURANCE_VERSION = "research-assurance-2026-09-14-v2"
HEX_CHARS = frozenset("0123456789abcdef")
DISPOSITIONS = frozenset({
    "implemented_verified",
    "retained_baseline",
    "rejected_by_evidence",
    "inconclusive_support",
    "unsupported_owned_input",
    "blocked_implementation",
})
RECEIPT_KEYS = (
    "schema_version",
    "assurance_version",
    "task_id",
    "run_id",
    "plan_sha256",
    "code_sha256",
    "predecessor_receipts",
    "command_results",
    "artifact_manifest",
    "acceptance_checks",
    "disposition",
    "reason",
    "coverage",
    "unresolved",
)


def canonical_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return canonical_value(value.value)
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: canonical_value(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ContractError("nonfinite decimal")
        return str(value)
    if isinstance(value, (dict, MappingProxyType)):
        if any(not isinstance(k, str) for k in value):
            raise ContractError("JSON keys must be strings")
        return {k: canonical_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [canonical_value(v) for v in value]
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ContractError("nonfinite float")
        return value
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise ContractError(f"unsupported canonical type: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_value(value),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def digest(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path | str) -> str:
    hasher = sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def semantic_run_id(manifest: Mapping[str, Any]) -> str:
    return digest(manifest)[:16]


def record_id(payload: Mapping[str, Any]) -> str:
    return digest(payload)


def write_bytes_new(path: Path, payload: bytes) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise IntegrityError(f"immutable path already contains other bytes: {path}")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def write_json_document(path: Path, document: Any, *, indent: int | None = 2) -> bytes:
    text = json.dumps(
        canonical_value(document),
        sort_keys=True,
        ensure_ascii=False,
        indent=indent,
        allow_nan=False,
    )
    if indent is not None:
        text += "\n"
    payload = text.encode("utf-8")
    write_bytes_new(path, payload)
    return payload


def artifact_entry(path: Path, *, schema: str, row_count: int | None = None) -> dict[str, Any]:
    path = Path(path)
    payload = path.read_bytes()
    return {
        "path": str(path),
        "sha256": sha256(payload).hexdigest(),
        "bytes": len(payload),
        "rows": row_count,
        "schema": schema,
    }


def git_dirty_patch(paths: Iterable[str], *, cwd: Path) -> str:
    listed = [str(p) for p in paths]
    result = subprocess.run(
        ["git", "diff", "--", *listed],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode not in (0, 1):
        raise ContractError(f"git diff failed: {result.stderr.strip()}")
    return result.stdout


def code_identity(owned_paths: Iterable[str], *, root: Path) -> dict[str, Any]:
    files: dict[str, str] = {}
    for rel in owned_paths:
        path = root / rel
        files[rel] = file_digest(path)
    patch = git_dirty_patch(owned_paths, cwd=root)
    return {
        "files": files,
        "dirty_patch_sha256": digest(patch),
        "dirty_patch_empty": patch == "",
    }


def plan_identity(paths: Iterable[str], *, root: Path) -> dict[str, Any]:
    files = {rel: file_digest(root / rel) for rel in paths}
    return {"files": files, "sha256": digest(files)}


def validate_receipt_shape(receipt: Mapping[str, Any]) -> dict[str, Any]:
    missing = [key for key in RECEIPT_KEYS if key not in receipt]
    if missing:
        raise ContractError(f"task receipt missing keys: {missing}")
    extra = [key for key in receipt if key not in RECEIPT_KEYS]
    if extra:
        raise ContractError(f"task receipt has unknown keys: {extra}")
    if receipt["schema_version"] != SCHEMA_TASK_RECEIPT:
        raise ContractError("schema_version must be research-task-receipt-v2")
    if receipt.get("assurance_version") != ASSURANCE_VERSION:
        raise ContractError("assurance_version must be research-assurance-2026-09-14-v2")
    if not isinstance(receipt["task_id"], str) or not receipt["task_id"]:
        raise ContractError("task_id must be nonempty")
    if not _hex_id(receipt.get("run_id"), 16):
        raise ContractError("run_id must be 16 lowercase hex characters")
    for key in ("plan_sha256", "code_sha256"):
        if not _hex_id(receipt.get(key), 64):
            raise ContractError(f"{key} must be a lowercase SHA-256 hex digest")
    if not isinstance(receipt["predecessor_receipts"], dict):
        raise ContractError("predecessor_receipts must be a mapping")
    for key, value in receipt["predecessor_receipts"].items():
        if not isinstance(key, str) or not _hex_id(value, 64):
            raise ContractError("predecessor_receipts values must be SHA-256 hex digests")
    if not isinstance(receipt["command_results"], list):
        raise ContractError("command_results must be a list")
    if not isinstance(receipt["artifact_manifest"], list):
        raise ContractError("artifact_manifest must be a list")
    checks = receipt["acceptance_checks"]
    if not isinstance(checks, dict) or any(type(v) is not bool for v in checks.values()):
        raise ContractError("acceptance_checks must map names to bool")
    if receipt["disposition"] not in DISPOSITIONS:
        raise ContractError("unknown disposition")
    if not isinstance(receipt["reason"], str) or not receipt["reason"]:
        raise ContractError("reason must be nonempty")
    if not isinstance(receipt["coverage"], dict):
        raise ContractError("coverage must be a mapping")
    if not isinstance(receipt["unresolved"], list):
        raise ContractError("unresolved must be a list")
    return dict(receipt)


def _hex_id(value: object, length: int) -> bool:
    return isinstance(value, str) and len(value) == length and set(value) <= HEX_CHARS


def make_task_receipt(
    *,
    task_id: str,
    run_id: str,
    plan_sha256: str,
    code_sha256: str,
    predecessor_receipts: Mapping[str, str],
    command_results: list[dict[str, Any]],
    artifact_manifest: list[dict[str, Any]],
    acceptance_checks: Mapping[str, bool],
    disposition: str,
    reason: str,
    coverage: Mapping[str, Any],
    unresolved: list[str],
    assurance_version: str = ASSURANCE_VERSION,
) -> dict[str, Any]:
    receipt = {
        "schema_version": SCHEMA_TASK_RECEIPT,
        "assurance_version": assurance_version,
        "task_id": task_id,
        "run_id": run_id,
        "plan_sha256": plan_sha256,
        "code_sha256": code_sha256,
        "predecessor_receipts": dict(predecessor_receipts),
        "command_results": list(command_results),
        "artifact_manifest": list(artifact_manifest),
        "acceptance_checks": dict(acceptance_checks),
        "disposition": disposition,
        "reason": reason,
        "coverage": dict(coverage),
        "unresolved": list(unresolved),
    }
    return validate_receipt_shape(receipt)


def write_task_receipt(path: Path, receipt: Mapping[str, Any]) -> dict[str, Any]:
    checked = validate_receipt_shape(receipt)
    write_json_document(path, checked)
    return checked


def write_snapshot_tree(staging: Path, kind: str, files: Mapping[str, str], *, root: Path) -> dict[str, str]:
    copies: dict[str, str] = {}
    for rel in files:
        source = root / rel
        relative = Path("snapshots") / kind / rel
        dest = staging / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(source.read_bytes())
        copies[rel] = relative.as_posix()
    return copies


def plan_snapshot_document(files: Mapping[str, str], snapshot_paths: Mapping[str, str]) -> dict[str, Any]:
    return {
        "schema_version": "research-plan-snapshot-v2",
        "assurance_version": ASSURANCE_VERSION,
        "files": dict(files),
        "snapshot_paths": dict(snapshot_paths),
    }


def code_snapshot_document(
    files: Mapping[str, str],
    snapshot_paths: Mapping[str, str],
    *,
    runtime: Mapping[str, Any],
    dependency_lock_sha256: str,
    imported_modules: list[str],
) -> dict[str, Any]:
    return {
        "schema_version": "research-code-snapshot-v2",
        "files": dict(files),
        "snapshot_paths": dict(snapshot_paths),
        "runtime": dict(runtime),
        "dependency_lock_sha256": dependency_lock_sha256,
        "imported_modules": list(imported_modules),
    }


def freeze_mapping(value: Mapping[str, Any]) -> MappingProxyType:
    frozen = freeze_json_value(dict(value))
    if not isinstance(frozen, MappingProxyType):
        raise ContractError("expected frozen mapping")
    return frozen
