#!/usr/bin/env python3
"""Build the reviewable Phase 1 acceptance matrix.

The matrix deliberately keeps inventory, executable checks, and manual
obligation review separate.  A recipe being registered, having a schema, or
passing a synthetic fixture is evidence about that one check; it is not a
fidelity certification.  Manual ledgers can be added later without changing
the tool: absent ledgers remain explicit ``missing_review`` records.

The normal run executes the bounded object/core fixture checks and validates
the complete output schema on every normal object fixture.  ``--no-checks``
is available for a fast inventory pass when the package cannot be imported or
when only ledger/report shape is being inspected.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import inspect
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any


IMPLEMENTATION_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = IMPLEMENTATION_ROOT.parent
SRC_ROOT = IMPLEMENTATION_ROOT / "src"
DEFAULT_OUTPUT_JSON = IMPLEMENTATION_ROOT / "validation/phase1-completion/obligation-matrix.json"
DEFAULT_OUTPUT_MD = IMPLEMENTATION_ROOT / "reports/phase1-live/methods/COMPLETION_MATRIX.md"

OLD_OBJECTS = IMPLEMENTATION_ROOT / "reports/phase1-live/methods/charts/full-audit-objects.json"
OLD_CORE = IMPLEMENTATION_ROOT / "reports/phase1-live/methods/charts/full-audit-core.json"
OLD_METHODS = IMPLEMENTATION_ROOT / "reports/phase1-live/methods/charts/full-audit-methods.json"

OBJECT_LEDGER_PATHS = (
    IMPLEMENTATION_ROOT / "validation/phase1-completion/flow-lifecycle-obligations.json",
    IMPLEMENTATION_ROOT / "validation/phase1-completion/geometry-obligations.json",
    IMPLEMENTATION_ROOT / "validation/phase1-completion/context-process-obligations.json",
)
CORE_LEDGER_PATH = IMPLEMENTATION_ROOT / "validation/phase1-completion/native-core-obligations.json"
METHOD_FIELD_LEDGER_PATH = IMPLEMENTATION_ROOT / "validation/phase1-completion/method-field-review.json"
NATIVE_VALIDATION_DOCS = (
    IMPLEMENTATION_ROOT / "validation/phase1-completion/native-boundary.json",
    IMPLEMENTATION_ROOT / "validation/phase1-completion/native-flow.json",
    IMPLEMENTATION_ROOT / "validation/phase1-completion/native-geometry.json",
    IMPLEMENTATION_ROOT / "validation/phase1-completion/native-clock-coverage.json",
)
REGRESSION_AUDIT_PATH = IMPLEMENTATION_ROOT / "validation/phase1-completion/audit-regressions.json"

OBJECT_RE = re.compile(r"^O\d{3}$")
CORE_RE = re.compile(r"^C\d{2}$")
METHOD_RE = re.compile(r"^M\d{2}$")


def sha256_file(path: Path) -> str | None:
    """Return a file hash, or ``None`` for a missing/non-file path."""

    try:
        if not path.is_file():
            return None
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()
    except OSError:
        return None


def display_path(path: Path | str) -> str:
    """Use absolute paths in JSON so evidence links are directly reviewable."""

    return str(Path(path).resolve())


def rel_path(path: Path | str) -> str:
    try:
        return str(Path(path).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(Path(path))


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def input_record(path: Path, *, schema: str | None = None, count: int | None = None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": display_path(path),
        "path_rel": rel_path(path),
        "exists": path.is_file(),
        "sha256": sha256_file(path),
    }
    if schema is not None:
        record["schema"] = schema
    if count is not None:
        record["count"] = count
    return record


def type_name(value: Any) -> str:
    """Serialize the public name of a schema type without repr addresses."""

    if isinstance(value, type):
        return value.__name__
    name = getattr(value, "__name__", None)
    if name:
        return name
    text = str(value)
    return text.replace("<class '", "").replace("'>", "")


def serialize_output_schema(schema: dict[str, Any] | None) -> dict[str, Any]:
    """Serialize every required output field, including nullable fields."""

    if schema is None:
        return {}
    result: dict[str, Any] = {}
    for name in sorted(schema):
        field = schema[name]
        types = getattr(field, "types", ())
        result[name] = {
            "required": True,
            "types": sorted(type_name(item) for item in types),
            "nullable": bool(getattr(field, "nullable", False)),
        }
    return result


def compact_failure_list(values: Any, limit: int = 12) -> list[str]:
    if not values:
        return []
    return [str(value) for value in list(values)[:limit]]


def compact_fixture_row(row: dict[str, Any]) -> dict[str, Any]:
    """Keep check identity/results while omitting fixture payloads."""

    result = {
        "id": row.get("id"),
        "recipe": row.get("recipe"),
        "kind": row.get("kind"),
        "status": row.get("status"),
        "failures": compact_failure_list(row.get("failures")),
        "actual_state": row.get("actual_state"),
        "base_ok": row.get("base_ok"),
        "coverage_ok": row.get("coverage_ok"),
        "hole_ids": list(row.get("hole_ids") or []),
        "reason": row.get("reason"),
        "detected_causal_violation": row.get("detected_causal_violation"),
        "evidence_mode": row.get("evidence_mode"),
    }
    return result


def compact_schema_check(row: dict[str, Any]) -> dict[str, Any]:
    result = {
        "fixture_id": row.get("fixture_id"),
        "recipe_id": row.get("recipe_id"),
        "status": row.get("status"),
        "state": row.get("state"),
        "output_fields": list(row.get("output_fields") or []),
        "base_ok": row.get("base_ok"),
        "coverage_ok": row.get("coverage_ok"),
        "hole_ids": list(row.get("hole_ids") or []),
        "failures": compact_failure_list(row.get("failures")),
        "reason": row.get("reason"),
    }
    if row.get("status") != "pass" and row.get("reason") and not result["failures"]:
        result["failures"] = [str(row["reason"])]
    return result


def source_metadata(fn: Any) -> dict[str, Any]:
    """Capture function name/module/source line and the current file hash."""

    if fn is None:
        return {
            "name": None,
            "module": None,
            "source_file": None,
            "source_file_rel": None,
            "source_line": None,
            "source_end_line": None,
            "source_sha256": None,
        }
    source_file: str | None = None
    line: int | None = None
    end_line: int | None = None
    try:
        source_file = inspect.getsourcefile(fn) or inspect.getfile(fn)
    except (OSError, TypeError):
        source_file = None
    try:
        _, line = inspect.getsourcelines(fn)
        try:
            end_line = line + len(inspect.getsource(fn).splitlines()) - 1
        except (OSError, TypeError):
            end_line = line
    except (OSError, TypeError):
        pass
    source_path = Path(source_file).resolve() if source_file else None
    return {
        "name": getattr(fn, "__name__", None),
        "module": getattr(fn, "__module__", None),
        "source_file": display_path(source_path) if source_path else None,
        "source_file_rel": rel_path(source_path) if source_path else None,
        "source_line": line,
        "source_end_line": end_line,
        "source_sha256": sha256_file(source_path) if source_path else None,
    }


def load_old_reports() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return read_json(OLD_OBJECTS), read_json(OLD_CORE), read_json(OLD_METHODS)


def ledger_id(node: dict[str, Any]) -> str | None:
    for key in ("object_id", "contract_id", "core_id", "method_id", "id"):
        value = node.get(key)
        if isinstance(value, str) and (OBJECT_RE.fullmatch(value) or CORE_RE.fullmatch(value) or METHOD_RE.fullmatch(value)):
            return value
    return None


def iter_ledger_rows(node: Any, *, source_path: Path, parent_key: str = ""):
    """Yield explicit O/C/M ledger rows, tolerating future ledger envelopes."""

    if isinstance(node, dict):
        ident = ledger_id(node)
        if ident is not None:
            yield ident, {
                "ledger": deepcopy(node),
                "ledger_path": display_path(source_path),
                "ledger_path_rel": rel_path(source_path),
                "ledger_sha256": sha256_file(source_path),
                "ledger_key": parent_key or None,
            }
        for key in sorted(node):
            value = node[key]
            yield from iter_ledger_rows(value, source_path=source_path, parent_key=key)
    elif isinstance(node, list):
        for value in node:
            yield from iter_ledger_rows(value, source_path=source_path, parent_key=parent_key)


def _split_method_field_key(value: Any) -> tuple[str, str] | None:
    """Split a compact ``M##<separator>field`` review key."""

    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"(M\d{2})\s*(?:::|[|/#])\s*(.+)", value.strip())
    if not match or not match.group(2).strip():
        return None
    return match.group(1), match.group(2).strip()


def method_field_key(method_id: Any, field: Any) -> tuple[str, str] | None:
    """Return the stable in-memory key for an M##+field ledger row."""

    if not isinstance(method_id, str) or not METHOD_RE.fullmatch(method_id):
        return None
    if not isinstance(field, str) or not field.strip():
        return None
    return method_id, field.strip()


def iter_method_field_rows(
    node: Any,
    *,
    source_path: Path,
    method_hint: str | None = None,
    field_hint: str | None = None,
    parent_key: str = "",
):
    """Yield review rows from direct and keyed method-field ledger shapes.

    The method-field ledger is intentionally separate from object/core ledgers.
    It may be a list of ``{method_id, field, review_status}`` rows, or a
    compact mapping such as ``{"M01": {"at_rth_open": {"status": ...}}}``.
    A yielded row always contains explicit ``method_id`` and ``field`` keys so
    callers can apply the same manual-review parser to either shape.
    """

    if isinstance(node, dict):
        direct_method = node.get("method_id")
        if not isinstance(direct_method, str) or not METHOD_RE.fullmatch(direct_method):
            direct_method = method_hint
        direct_field = node.get("field")
        if not isinstance(direct_field, str) or not direct_field.strip():
            direct_field = field_hint
        compact_key = _split_method_field_key(parent_key)
        if compact_key:
            direct_method, direct_field = compact_key
        stable_key = method_field_key(direct_method, direct_field)
        if stable_key is not None:
            row = deepcopy(node)
            row.setdefault("method_id", stable_key[0])
            row.setdefault("field", stable_key[1])
            yield stable_key, {
                "ledger": row,
                "ledger_path": display_path(source_path),
                "ledger_path_rel": rel_path(source_path),
                "ledger_sha256": sha256_file(source_path),
                "ledger_key": parent_key or None,
            }
            # A direct row owns its nested review/evidence payload.  Descending
            # into it would mistake keys such as ``review`` for field names.
            return

        envelope_keys = {
            "schema", "scope", "fields", "method_fields", "reviews",
            "review", "metadata", "notes", "status", "version",
        }
        for key in sorted(node):
            value = node[key]
            child_method = direct_method
            child_field = direct_field
            split_key = _split_method_field_key(key)
            if split_key:
                child_method, child_field = split_key
            elif METHOD_RE.fullmatch(str(key)):
                # Compact form: {"M01": {"field_name": {"status": ...}}}.
                child_method, child_field = key, None
            elif child_method and key not in envelope_keys and not key.startswith("_"):
                # Compact form: {"M01": {"field_name": {"status": ...}}}.
                child_field = key
            yield from iter_method_field_rows(
                value,
                source_path=source_path,
                method_hint=child_method,
                field_hint=child_field,
                parent_key=key,
            )
    elif isinstance(node, list):
        for value in node:
            yield from iter_method_field_rows(
                value,
                source_path=source_path,
                method_hint=method_hint,
                field_hint=field_hint,
                parent_key=parent_key,
            )


def load_ledgers(
    extra_paths: list[Path] | None = None,
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[tuple[str, str], dict[str, Any]],
    list[dict[str, Any]],
]:
    """Load available manual rows and retain absent-ledger evidence."""

    paths: list[Path] = list(OBJECT_LEDGER_PATHS) + [CORE_LEDGER_PATH, METHOD_FIELD_LEDGER_PATH]
    paths.extend(extra_paths or [])
    # Preserve first occurrence deterministically when a caller repeats a path.
    unique_paths: list[Path] = []
    for path in paths:
        path = Path(path).resolve()
        if path not in unique_paths:
            unique_paths.append(path)
    # The compact keyed parser is intentionally restricted to the dedicated
    # method-field ledger and explicitly supplied extras.  Walking every O/C
    # schema recursively would add needless work and could mistake arbitrary
    # nested keys for method field names.
    method_field_scan_paths = {METHOD_FIELD_LEDGER_PATH.resolve()}
    method_field_scan_paths.update(Path(path).resolve() for path in (extra_paths or []))

    object_rows: dict[str, dict[str, Any]] = {}
    core_rows: dict[str, dict[str, Any]] = {}
    method_field_rows: dict[tuple[str, str], dict[str, Any]] = {}
    ledger_inputs: list[dict[str, Any]] = []
    for path in unique_paths:
        if not path.is_file():
            ledger_inputs.append(input_record(path))
            continue
        try:
            document = read_json(path)
        except (OSError, ValueError) as exc:
            ledger_inputs.append({**input_record(path), "read_error": f"{type(exc).__name__}: {exc}"})
            continue
        ledger_inputs.append({
            **input_record(path),
            "top_level_schema": document.get("schema") if isinstance(document, dict) else None,
            "object_count": document.get("object_count") if isinstance(document, dict) else None,
            "contract_count": document.get("contract_count") if isinstance(document, dict) else None,
            "row_count": sum(1 for _ in iter_ledger_rows(document, source_path=path)),
        })
        for ident, row in iter_ledger_rows(document, source_path=path):
            # Later explicitly supplied --ledger files may refine or resolve
            # a default row, so deterministic path order gives the caller an
            # intentional override without fabricating rows for uncovered IDs.
            if ident.startswith("O"):
                object_rows[ident] = row
            elif ident.startswith("C"):
                core_rows[ident] = row
            elif ident.startswith("M"):
                field = (row.get("ledger") or {}).get("field")
                key = method_field_key(ident, field)
                if key is not None:
                    method_field_rows[key] = row
        if path in method_field_scan_paths:
            # Keyed method-field ledgers do not have an M## identifier on the
            # enclosing mapping node.  Index these separately without allowing
            # them to overwrite an O## obligation with the same source path.
            for key, row in iter_method_field_rows(document, source_path=path):
                method_field_rows[key] = row
    return object_rows, core_rows, method_field_rows, ledger_inputs


def explicit_review_status(entry: dict[str, Any] | None) -> dict[str, Any]:
    """Read a manual resolution marker without inferring one from presence."""

    if not entry:
        return {
            "status": "missing_review",
            "label": "needs_review",
            "needs_review": True,
            "missing_review": True,
            "resolved": False,
            "reason": "manual obligation ledger is absent",
            "reviewed": False,
        }
    ledger = entry.get("ledger") or {}
    nested = ledger.get("review") if isinstance(ledger.get("review"), dict) else {}
    candidates: list[tuple[str, Any]] = []
    for key in (
        "review_status", "acceptance_status", "obligation_status", "implementation_status",
        "review_marker", "explicit_review_marker", "status", "verdict",
    ):
        if key in ledger:
            candidates.append((key, ledger[key]))
        if key in nested:
            candidates.append((f"review.{key}", nested[key]))
    bool_reviewed = any(
        ledger.get(key) is True or nested.get(key) is True
        for key in ("reviewed", "resolved", "accepted", "explicit_review")
    )
    values = [str(value).strip().lower() for _, value in candidates if isinstance(value, (str, bool))]
    resolved_words = {"resolved", "reviewed", "accepted", "complete", "completed", "pass", "passed", "true"}
    unresolved_words = {"needs_review", "missing_review", "unreviewed", "open", "pending", "unknown", "incomplete", "fail", "failed"}
    resolved = bool_reviewed or any(value in resolved_words for value in values)
    if any(value in unresolved_words for value in values):
        resolved = False
    status = "resolved" if resolved else "unreviewed"
    return {
        "status": status,
        "label": status,
        "needs_review": not resolved,
        "missing_review": False,
        "resolved": resolved,
        "reviewed": bool_reviewed,
        "declared_status": candidates[0][1] if candidates else None,
        "reason": "explicit manual resolution marker" if resolved else "ledger obligation is present without an explicit resolved/pass review marker",
    }


def dimension_entry(entry: dict[str, Any] | None, dimension: str) -> dict[str, Any]:
    """Return only an explicitly supplied dimension status."""

    if not entry:
        return {"status": "unavailable", "resolved": False, "reason": "manual ledger absent; dimension review unavailable"}
    ledger = entry.get("ledger") or {}
    candidates: list[Any] = []
    for container in (ledger, ledger.get("dimensions", {}), ledger.get("review", {})):
        if isinstance(container, dict) and dimension in container:
            candidates.append(container[dimension])
    if not candidates:
        return {"status": "unavailable", "resolved": False, "reason": f"ledger has no explicit {dimension} resolution"}
    value = candidates[0]
    if isinstance(value, dict):
        result = deepcopy(value)
        result.setdefault("status", "unavailable")
        result.setdefault("resolved", result.get("status") in {"resolved", "complete", "pass", "passed"})
        return result
    status = str(value).strip().lower()
    return {"status": status, "resolved": status in {"resolved", "complete", "pass", "passed"}, "declared": value}


def review_evidence(entry: dict[str, Any] | None) -> dict[str, Any]:
    if not entry:
        return {"status": "missing_review", "ledger_path": None, "ledger_sha256": None, "tests": [], "evidence": []}
    ledger = entry.get("ledger") or {}
    tests = ledger.get("sensitive_regression_tests")
    if not isinstance(tests, list):
        tests = ledger.get("regression_tests")
    if not isinstance(tests, list):
        tests = ledger.get("tests")
    if tests is None and ledger.get("sensitive_regression_evidence") is not None:
        tests = [ledger.get("sensitive_regression_evidence")]
    evidence = ledger.get("evidence")
    if not isinstance(evidence, list):
        evidence = ledger.get("sensitive_regression_evidence")
        evidence = [] if evidence is None else [evidence]
    return {
        "status": explicit_review_status(entry)["status"],
        "ledger_path": entry.get("ledger_path"),
        "ledger_sha256": entry.get("ledger_sha256"),
        "tests": [str(value) for value in (tests or [])],
        "evidence": [str(value) for value in evidence],
    }


def artifact_path_value(value: Any) -> str | None:
    if isinstance(value, str) and ("/" in value or value.endswith((".json", ".json.gz", ".parquet", ".csv"))):
        return value
    return None


def collect_explicit_artifacts(value: Any, *, source_path: Path, context_ids: set[str] | None = None) -> list[dict[str, Any]]:
    """Collect artifact path/hash pairs from explicit artifact-shaped keys.

    Source-member locators in native summaries are intentionally not treated as
    durable output artifacts.  They remain cited in their source documents;
    only ``artifact``/``native_artifacts``/``durable_artifacts`` shaped values
    enter this compact inventory.
    """

    found: list[dict[str, Any]] = []
    context_ids = set(context_ids or set())
    artifact_keys = {
        "artifact", "artifacts", "artifact_path", "full_artifact", "native_artifact",
        "native_artifacts", "durable_artifact", "durable_artifacts", "control_artifact",
        "validation_artifact", "validation_artifacts",
    }

    def walk(node: Any, ids: set[str], key_context: str = "") -> None:
        if isinstance(node, dict):
            next_ids = set(ids)
            for key in ("object_id", "recipe_id", "id"):
                value_id = node.get(key)
                if isinstance(value_id, str) and OBJECT_RE.fullmatch(value_id):
                    next_ids.add(value_id)
            sha = node.get("sha256") or node.get("file_sha256")
            candidate_paths: list[str] = []
            for key, child in node.items():
                if key in {"path", "file", "source_file", "artifact_path"}:
                    path_value = artifact_path_value(child)
                    if path_value:
                        candidate_paths.append(path_value)
                if key in artifact_keys and isinstance(child, str):
                    path_value = artifact_path_value(child)
                    if path_value:
                        candidate_paths.append(path_value)
            is_artifact_context = key_context in artifact_keys or any(key in artifact_keys for key in node)
            if sha and candidate_paths and is_artifact_context:
                for path_value in candidate_paths:
                    found.append({
                        "path": display_path(resolve_path(path_value)),
                        "path_rel": rel_path(resolve_path(path_value)),
                        "sha256": str(sha),
                        "exists": resolve_path(path_value).is_file(),
                        "sha256_verified": sha256_file(resolve_path(path_value)) == str(sha),
                        "source": display_path(source_path),
                        "object_ids": sorted(next_ids),
                    })
            for key, child in node.items():
                walk(child, next_ids, key)
        elif isinstance(node, list):
            for child in node:
                walk(child, set(ids), key_context)

    walk(value, context_ids)
    return found


def resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (REPO_ROOT / path).resolve()


def native_artifact_inventory(
    object_ledger_rows: dict[str, dict[str, Any]],
    native_docs: list[Path],
    core_ledger_rows: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for entry in list(object_ledger_rows.values()) + list((core_ledger_rows or {}).values()):
        refs.extend(collect_explicit_artifacts(entry.get("ledger", {}), source_path=Path(entry["ledger_path"])))
    for path in native_docs:
        if not path.is_file():
            continue
        try:
            document = read_json(path)
        except (OSError, ValueError):
            continue
        # The validation summary itself is durable evidence even where its
        # envelope does not repeat a path/hash pair for every object.
        object_ids: set[str] = set()

        def collect_ids(node: Any) -> None:
            if isinstance(node, dict):
                for key in ("object_id", "recipe_id", "id"):
                    value = node.get(key)
                    if isinstance(value, str):
                        match = re.search(r"(?:^|:)O\d{3}(?:$|:)", value)
                        if match:
                            object_ids.add(match.group(0).strip(":"))
                for child in node.values():
                    collect_ids(child)
            elif isinstance(node, list):
                for child in node:
                    collect_ids(child)

        collect_ids(document)
        refs.append({
            "path": display_path(path),
            "path_rel": rel_path(path),
            "sha256": sha256_file(path),
            "exists": True,
            "sha256_verified": True,
            "source": display_path(path),
            "object_ids": sorted(object_ids),
            "kind": "native_validation_summary",
        })
        refs.extend(collect_explicit_artifacts(document, source_path=path, context_ids=object_ids))
    # native-flow names the compressed artifact in its envelope; it is not a
    # JSON object we should load as a normal report.
    flow_path = IMPLEMENTATION_ROOT / "validation/phase1-completion/native-flow.json"
    if flow_path.is_file():
        try:
            flow_document = read_json(flow_path)
            full_artifact = flow_document.get("full_artifact", {}) if isinstance(flow_document, dict) else {}
            if isinstance(full_artifact, dict) and full_artifact.get("path") and full_artifact.get("sha256"):
                refs.extend(collect_explicit_artifacts({"full_artifact": full_artifact}, source_path=flow_path))
        except (OSError, ValueError):
            pass
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for ref in refs:
        key = (str(ref.get("path")), str(ref.get("sha256")))
        existing = merged.get(key)
        if existing is None:
            merged[key] = deepcopy(ref)
        else:
            existing["object_ids"] = sorted(set(existing.get("object_ids", [])) | set(ref.get("object_ids", [])))
            existing.setdefault("sources", []).append(ref.get("source"))
    return [merged[key] for key in sorted(merged)]


def compact_regression_row(row: Any) -> dict[str, Any]:
    """Keep fresh-probe identity and verdicts without copying probe payloads."""

    if not isinstance(row, dict):
        return {"value": str(row)}
    result: dict[str, Any] = {}
    for key in (
        "id", "probe_id", "object_id", "contract_id", "method_id", "fixture_id",
        "status", "verdict", "result", "expected", "actual", "gap_observed",
        "implementation_fail", "causal_violation", "leakage", "proxy_as_faithful",
        "notes", "reason", "failures",
    ):
        if key in row:
            value = row[key]
            if key in {"failures"}:
                result[key] = compact_failure_list(value)
            elif isinstance(value, (dict, list)):
                # Retain small verdict metadata while omitting fixture inputs
                # and full recipe outputs from the completion matrix.
                if key in {"expected", "actual"}:
                    result[key] = json.dumps(value, sort_keys=True, default=str)[:600]
                else:
                    result[key] = value
            else:
                result[key] = value
    if not result:
        return {"value": str(row)[:600]}
    return result


def regression_audit_summary(path: Path = REGRESSION_AUDIT_PATH) -> dict[str, Any]:
    """Load an optional fresh 27-probe validation artifact.

    The audit is supplementary evidence: an absent artifact stays explicitly
    missing and never receives synthetic pass rows or a fabricated denominator.
    Different callers may use ``probes``, ``results``, or ``checks`` as the
    row key, so the envelope is normalized while its source hash is retained.
    """

    base = input_record(path)
    if not path.is_file():
        return {
            **base,
            "schema": None,
            "status": "missing_review",
            "label": "needs_review",
            "needs_review": True,
            "missing_review": True,
            "expected_probe_count": 27,
            "probe_count": None,
            "status_counts": {},
            "result_ids": [],
            "results": [],
            "reason": "fresh 27-probe validation artifact is absent",
        }
    try:
        document = read_json(path)
    except (OSError, ValueError) as exc:
        return {
            **base,
            "schema": None,
            "status": "implementation_fail",
            "label": "implementation_fail",
            "needs_review": True,
            "missing_review": False,
            "expected_probe_count": 27,
            "probe_count": None,
            "status_counts": {"implementation_fail": 1},
            "result_ids": [],
            "results": [],
            "reason": f"cannot read fresh regression audit: {type(exc).__name__}: {exc}",
        }
    rows: Any = []
    if isinstance(document, dict):
        for key in ("probes", "results", "checks", "regressions", "audits"):
            candidate = document.get(key)
            if isinstance(candidate, list):
                rows = candidate
                break
    elif isinstance(document, list):
        rows = document
    compact_rows = [compact_regression_row(row) for row in rows]
    status_counts: Counter[str] = Counter()
    for row in compact_rows:
        if not isinstance(row, dict):
            continue
        status = row.get("status")
        if status is None:
            status = row.get("verdict")
        if status is not None:
            status_counts[str(status)] += 1
    explicit_failures = sum(
        count for key, count in status_counts.items()
        if str(key).strip().lower() in {"implementation_fail", "fail", "failed", "error"}
    )
    if explicit_failures:
        status = "implementation_fail"
    elif len(compact_rows) == 27 and compact_rows and not status_counts:
        status = "unreviewed"
    elif len(compact_rows) == 27 and status_counts and all(
        str(key).strip().lower() in {"pass", "passed", "resolved", "complete", "ok", "reproduced_expected_gap"}
        for key in status_counts
    ):
        status = "pass"
    else:
        status = "unreviewed"
    result_ids = []
    for row in compact_rows:
        if isinstance(row, dict):
            ident = row.get("id") or row.get("probe_id") or row.get("object_id")
            result_ids.append(ident)
        else:
            result_ids.append(None)
    return {
        **base,
        "schema": document.get("schema") if isinstance(document, dict) else None,
        "status": status,
        "label": status,
        "needs_review": status != "pass",
        "missing_review": False,
        "expected_probe_count": 27,
        "probe_count": len(compact_rows),
        "status_counts": dict(sorted(status_counts.items())),
        "result_ids": result_ids,
        "results": compact_rows,
        "reason": None if len(compact_rows) == 27 else "fresh audit does not contain all 27 probe rows",
    }


def compact_ledger(entry: dict[str, Any] | None) -> dict[str, Any]:
    if not entry:
        return {
            "status": "missing_review",
            "label": "needs_review",
            "needs_review": True,
            "missing_review": True,
            "exists": False,
            "path": None,
            "sha256": None,
            "row": None,
        }
    row = deepcopy(entry.get("ledger"))
    review = explicit_review_status(entry)
    return {
        "status": review["status"],
        "label": review.get("label", review["status"]),
        "needs_review": review.get("needs_review", review["status"] != "resolved"),
        "missing_review": False,
        "exists": True,
        "path": entry.get("ledger_path"),
        "path_rel": entry.get("ledger_path_rel"),
        "sha256": entry.get("ledger_sha256"),
        "row": row,
    }


def code_check_status(checks: dict[str, Any]) -> tuple[str, list[str]]:
    failures = [name for name, value in checks.items() if name.endswith("_ok") and value is False]
    return ("implementation_fail" if failures else "pass"), failures


def status_from_evidence(code_status: str, review_status: str) -> str:
    if code_status == "implementation_fail":
        return "implementation_fail"
    if code_status != "pass" or review_status != "resolved":
        return "unreviewed"
    return "complete"


def object_source_evidence(
    oid: str,
    *,
    recipe_fn: Any,
    producer_fns: list[Any],
    required: tuple[str, ...],
    schema: dict[str, Any] | None,
    native_ids: set[str],
    derived_ids: set[str],
    fixture_results: list[dict[str, Any]],
    schema_results: list[dict[str, Any]],
    ledger_entry: dict[str, Any] | None,
    artifacts: list[dict[str, Any]],
    coverage_rows: list[dict[str, Any]],
    checks_enabled: bool,
) -> dict[str, Any]:
    recipe_source = source_metadata(recipe_fn)
    producer_sources = [source_metadata(fn) for fn in producer_fns]
    primary_source = producer_sources[0] if producer_sources else recipe_source
    fixture_statuses = Counter(row.get("status") for row in fixture_results)
    schema_statuses = Counter(row.get("status") for row in schema_results)
    if checks_enabled:
        fixture_ok = not any(row.get("status") != "pass" for row in fixture_results)
        schema_ok = not any(row.get("status") != "pass" for row in schema_results)
    else:
        fixture_ok = None
        schema_ok = None
    checks = {
        "recipe_registered_ok": recipe_fn is not None,
        "output_schema_registered_ok": schema is not None,
        "fixture_checks_ok": fixture_ok,
        "output_schema_checks_ok": schema_ok,
    }
    if checks_enabled:
        executable_status, executable_failures = code_check_status(checks)
    else:
        executable_status, executable_failures = "not_run", []
    review = explicit_review_status(ledger_entry)
    linked_coverage = [row for row in coverage_rows if oid in row.get("producers", ())]
    # ``producer_coverage_matrix`` gives one row per method field, so the
    # compact object view records exact referenced fields and route counts.
    route_counts: Counter[str] = Counter()
    for row in linked_coverage:
        for producer in row.get("producer_status", []):
            if producer.get("recipe_id") == oid:
                for route in producer.get("routes", []):
                    route_counts[route] += 1
    object_artifacts = [ref for ref in artifacts if oid in (ref.get("object_ids") or [])]
    result = {
        "recipe_registered": recipe_fn is not None,
        "required_inputs": list(required),
        "registered_required_inputs": list(required),
        "full_required_output_schema": serialize_output_schema(schema),
        "output_schema": serialize_output_schema(schema),
        "source_file": primary_source.get("source_file"),
        "source_file_rel": primary_source.get("source_file_rel"),
        "source_name": primary_source.get("name"),
        "source_module": primary_source.get("module"),
        "source_line": primary_source.get("source_line"),
        "source_sha256": primary_source.get("source_sha256"),
        "source": recipe_source,
        "recipe_source": recipe_source,
        "producer_sources": producer_sources,
        "native_producer_registered": oid in native_ids,
        "derived_producer_registered": oid in derived_ids,
        "producer_kinds": [kind for kind, enabled in (("native", oid in native_ids), ("derived", oid in derived_ids)) if enabled],
        "producer_coverage": {
            "method_field_count": len(linked_coverage),
            "field_names": sorted({row.get("field") for row in linked_coverage}),
            "route_counts": dict(sorted(route_counts.items())),
        },
        "checks": checks,
        "executable_status": executable_status,
        "executable_failures": executable_failures,
        "manual_review": review,
        "manual_ledger": compact_ledger(ledger_entry),
        "fixture_checks": fixture_results if checks_enabled else [],
        "fixture_check_ids": [row.get("id") for row in fixture_results] if checks_enabled else [],
        "fixture_status_counts": dict(sorted(fixture_statuses.items())),
        "output_schema_checks": schema_results if checks_enabled else [],
        "output_schema_check_ids": [row.get("fixture_id") for row in schema_results] if checks_enabled else [],
        "output_schema_status_counts": dict(sorted(schema_statuses.items())),
        "regression_tests": review_evidence(ledger_entry)["tests"],
        "regression_test_ids": review_evidence(ledger_entry)["tests"],
        "native_artifacts": object_artifacts,
    }
    result["status"] = status_from_evidence(executable_status, review["status"]) if checks_enabled else "unreviewed"
    return result


def object_rows(
    old_objects: dict[str, Any],
    *,
    recipes: dict[str, Any],
    required: dict[str, tuple[str, ...]],
    schemas: dict[str, Any],
    native_producers: dict[str, Any],
    derived_producers: dict[str, Any],
    fixture_results_by_object: dict[str, list[dict[str, Any]]],
    schema_results_by_object: dict[str, list[dict[str, Any]]],
    ledger_rows: dict[str, dict[str, Any]],
    artifacts: list[dict[str, Any]],
    coverage_rows: list[dict[str, Any]],
    checks_enabled: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for old in sorted(old_objects.get("objects", []), key=lambda row: row.get("id", "")):
        oid = old["id"]
        recipe_fn = recipes.get(oid)
        producers = []
        if oid in native_producers:
            producers.append(native_producers[oid])
        if oid in derived_producers and derived_producers[oid] not in producers:
            producers.append(derived_producers[oid])
        evidence = object_source_evidence(
            oid,
            recipe_fn=recipe_fn,
            producer_fns=producers,
            required=required.get(oid, ()),
            schema=schemas.get(oid),
            native_ids=set(native_producers),
            derived_ids=set(derived_producers),
            fixture_results=fixture_results_by_object.get(oid, []),
            schema_results=schema_results_by_object.get(oid, []),
            ledger_entry=ledger_rows.get(oid),
            artifacts=artifacts,
            coverage_rows=coverage_rows,
            checks_enabled=checks_enabled,
        )
        old_contract = deepcopy(old.get("contract", {}))
        old_review = deepcopy(old.get("review", {}))
        dimension_statuses = {name: dimension_entry(ledger_rows.get(oid), name) for name in ("source_ambiguity", "data", "source_agreement")}
        row = {
            "id": oid,
            "title": old.get("title"),
            "methods": list(old.get("methods", [])),
            "linked_old_contract_obligation": old_contract,
            "legacy_implementation": deepcopy(old.get("implementation", {})),
            "legacy_review": old_review,
            "inspection_class": old_review.get("status"),
            "evidence": {
                "old_contract": {
                    "path": old_contract.get("path"),
                    "line": old_contract.get("line"),
                    "section_sha256": old_contract.get("section_sha256"),
                },
                "old_review_basis": old_review.get("review_basis"),
                "old_review_note": old_review.get("note"),
                "manual_ledger_path": (ledger_rows.get(oid) or {}).get("ledger_path"),
                "manual_ledger_sha256": (ledger_rows.get(oid) or {}).get("ledger_sha256"),
                "regression_tests": evidence["regression_tests"],
            },
            "implementation": evidence,
            "dimensions": dimension_statuses,
            "status": evidence["status"],
            "legacy_notes": old_review.get("note"),
            "notes": ((evidence.get("manual_ledger") or {}).get("row") or {}).get("implemented_obligation"),
        }
        rows.append(row)
    return rows


def core_fixture_rows(checks_enabled: bool) -> list[dict[str, Any]]:
    if not checks_enabled:
        return []
    from trading_research.research.method_pack.core_fixtures import run_core_fixtures

    rows = [
        {
            "id": row.get("id"),
            "recipe": row.get("recipe"),
            "kind": row.get("kind"),
            "status": row.get("status"),
            "failures": compact_failure_list(row.get("failures")),
            "evidence_mode": row.get("evidence_mode"),
        }
        for row in run_core_fixtures()
    ]
    # Four shared contracts have no small printed fixture. Link their actual
    # executed boundary regressions from the final suite, with current input
    # hashes, rather than treating a manual marker as executable evidence.
    evidence_path = IMPLEMENTATION_ROOT / 'validation/phase1-completion/test-run.json'
    if not evidence_path.is_file():
        return rows
    run = read_json(evidence_path)
    checks = {
        'C00': ('test_all_twelve_method_contracts_have_every_operand_and_alternative',
                'test_complete_source_fixture_assembles_and_replays_without_using_outcome'),
        'C01': ('test_actual_native_result_ignores_supplied_summary_and_retains_members',
                'test_locator_false_provenance_rejected',
                'test_missing_schema_and_domain_state_are_implementation_errors',
                'test_supplied_parent_cannot_launder_unrelated_prices_as_native_selection'),
        'C05': ('test_relabelled_fixture_cannot_enter_contemporary_cohort',
                'test_raw_derived_cohort_cannot_be_built_from_supplied_assertions',
                'test_supplied_attempts_reconcile_without_entering_discovery'),
        'C08': ('test_m05_f3_and_c08_mutations_preserve_false_unknown_and_identity',
                'test_m11_c08_late_missing_and_identity_mutations',
                'test_m12_method_c08_mutates_late_missing_and_identity_records'),
    }
    current = run.get('status') == 'pass' and run.get('exit_code') == 0
    source_hashes = run.get('tested_source_files', {})
    current = current and bool(source_hashes) and all(
        sha256_file(REPO_ROOT / path) == expected for path, expected in source_hashes.items())
    junit = IMPLEMENTATION_ROOT / 'validation/phase1-completion/pytest.xml'
    current = current and any(record.get('path') == str(junit) and
        record.get('sha256') == sha256_file(junit) for record in run.get('artifacts', []))
    cases = list(ET.parse(junit).getroot().iter('testcase')) if junit.is_file() else []
    for contract, names in checks.items():
        for name in names:
            matches = [case for case in cases if case.get('name', '').split('[', 1)[0] == name]
            passed = current and bool(matches) and all(
                not any(child.tag in {'failure', 'error', 'skipped'} for child in case) for case in matches)
            rows.append({'id': f'{contract}:pytest:{name}', 'recipe': contract,
                'kind': 'verified_regression', 'status': 'pass' if passed else 'fail',
                'failures': [] if passed else ['missing, stale or unsuccessful final-suite regression evidence'],
                'evidence_mode': 'executed_test_evidence', 'parameterized_case_count': len(matches),
                'test_run': input_record(evidence_path), 'junit': input_record(junit),
                'testcases': [{'classname': case.get('classname'), 'name': case.get('name')} for case in matches]})
    return rows


def run_object_checks(
    *,
    object_ids: list[str],
    checks_enabled: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not checks_enabled:
        return [], []
    from trading_research.research.method_pack.contracts import validate_output
    from trading_research.research.method_pack.objects import FIXTURES, run_object_fixtures
    from trading_research.research.method_pack.protocol import c08_mutations, run_fixture_spec
    from trading_research.research.method_pack.protocol import run_recipe

    try:
        fixture_rows = [compact_fixture_row(row) for row in run_object_fixtures(object_ids)]
    except Exception as exc:
        # Keep the acceptance report reviewable when one fixture raises during
        # an in-progress implementation edit.  Re-run each spec in isolation
        # so unaffected fixture IDs remain useful evidence and the raising
        # spec becomes an explicit implementation_fail row.
        fixture_rows = []
        wanted = set(object_ids)
        for spec in FIXTURES:
            if spec.get("recipe") not in wanted:
                continue
            try:
                fixture_rows.append(compact_fixture_row(run_fixture_spec(spec)))
            except Exception as spec_exc:
                fixture_rows.append({
                    "id": spec.get("id"),
                    "recipe": spec.get("recipe"),
                    "kind": spec.get("kind", "positive"),
                    "status": "implementation_fail",
                    "failures": [f"{type(spec_exc).__name__}: {spec_exc}"],
                    "actual_state": None,
                    "base_ok": None,
                    "coverage_ok": None,
                    "hole_ids": [],
                    "reason": str(spec_exc),
                    "detected_causal_violation": None,
                    "evidence_mode": spec.get("evidence_mode", "synthetic_fixture"),
                })
            try:
                fixture_rows.extend(compact_fixture_row(row) for row in c08_mutations(spec))
            except Exception as mutation_exc:
                fixture_rows.append({
                    "id": f"{spec.get('id')}:c08_runner",
                    "recipe": spec.get("recipe"),
                    "kind": "c08_runner",
                    "status": "implementation_fail",
                    "failures": [f"{type(mutation_exc).__name__}: {mutation_exc}"],
                    "actual_state": None,
                    "base_ok": None,
                    "coverage_ok": None,
                    "hole_ids": [],
                    "reason": str(mutation_exc),
                    "detected_causal_violation": None,
                    "evidence_mode": "synthetic_fixture",
                })
    schema_rows: list[dict[str, Any]] = []
    for spec in FIXTURES:
        try:
            result = validate_output(run_recipe(spec["recipe"], deepcopy(spec["inputs"])))
            row = {
                "fixture_id": spec["id"],
                "recipe_id": spec["recipe"],
                "status": "pass",
                "state": result.state,
                "output_fields": sorted(result.value),
                "base_ok": result.base_ok,
                "coverage_ok": result.coverage_ok,
                "hole_ids": list(result.hole_ids),
                "reason": result.reason,
            }
        except Exception as exc:
            row = {
                "fixture_id": spec.get("id"),
                "recipe_id": spec.get("recipe"),
                "status": "implementation_fail",
                "state": None,
                "output_fields": [],
                "base_ok": None,
                "coverage_ok": None,
                "hole_ids": [],
                "failures": [f"{type(exc).__name__}: {exc}"],
                "reason": str(exc),
            }
        schema_rows.append(compact_schema_check(row))
    return fixture_rows, schema_rows


def _method_field_review_entry(
    field_ledger_rows: dict[tuple[str, str], dict[str, Any]] | None,
    method_id: str,
    field: str,
) -> dict[str, Any] | None:
    """Look up one explicit M##+field review row.

    ``load_ledgers`` stores tuple keys, while this helper also accepts the
    compact string/nested mappings useful to callers constructing an in-memory
    matrix or a focused unit test.
    """

    if not field_ledger_rows:
        return None
    key = (method_id, field)
    direct = field_ledger_rows.get(key)
    if direct is not None:
        return direct
    for compact in (f"{method_id}:{field}", f"{method_id}|{field}", f"{method_id}/{field}"):
        direct = field_ledger_rows.get(compact)  # type: ignore[arg-type]
        if direct is not None:
            return direct
    nested = field_ledger_rows.get(method_id)  # type: ignore[arg-type]
    if isinstance(nested, dict):
        if "ledger" in nested and isinstance(nested.get("ledger"), dict):
            ledger = nested["ledger"]
            if ledger.get("field") == field:
                return nested
        candidate = nested.get(field)
        if isinstance(candidate, dict):
            return candidate if "ledger" in candidate else {"ledger": candidate}
    return None


def fields_for_methods(
    coverage_rows: list[dict[str, Any]],
    *,
    checks_enabled: bool,
    ledger_rows: dict[str, dict[str, Any]],
    field_ledger_rows: dict[tuple[str, str], dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    # ``producer_coverage_matrix`` uses the catalog's readable method names
    # (for example ``GB-FAIL``), while the retained full-audit report indexes
    # methods as M01..M12.  Keep both forms, but use M## as the stable join
    # key so each method row receives its complete field binding list.
    from trading_research.research.method_pack.catalog import METHOD_BY_ID

    result: list[dict[str, Any]] = []
    def field_sort_key(row: dict[str, Any]) -> tuple[str, str]:
        raw_id = row.get("method_id")
        canonical_id = raw_id if METHOD_RE.fullmatch(str(raw_id or "")) else METHOD_BY_ID.get(raw_id, raw_id)
        return (str(canonical_id or ""), str(row.get("field", "")))

    for raw in sorted(coverage_rows, key=field_sort_key):
        method_name = raw.get("method_id")
        method_id = method_name if METHOD_RE.fullmatch(str(method_name or "")) else METHOD_BY_ID.get(method_name, method_name)
        producer_status = deepcopy(raw.get("producer_status", []))
        binding_failures: list[str] = []
        if not raw.get("producers"):
            binding_failures.append("no declared producer alternative")
        # A field may publish several alternatives.  An unavailable
        # alternative is evidence to retain in ``source_alternatives``; it is
        # an executable binding failure only when every declared alternative
        # is unavailable (the same rule used by assembly's binding_status).
        if raw.get("producers") and raw.get("binding_status") != "implemented":
            binding_failures.append("all declared producer alternatives unavailable")
        if raw.get("producers") and producer_status and not any(
            producer.get("complete_schema") and producer.get("binding_implemented")
            for producer in producer_status
        ):
            binding_failures.append("no declared producer alternative has a complete schema and binding route")
        code_status = "not_run" if not checks_enabled else ("implementation_fail" if binding_failures else "pass")
        # Field review is a separate ledger dimension.  Object ledgers may
        # contain method_id/field-shaped explanatory text, but that presence
        # must never resolve or overwrite an O## obligation row.
        matching_entry = _method_field_review_entry(field_ledger_rows, method_id, str(raw.get("field")))
        review = explicit_review_status(matching_entry)
        status = status_from_evidence(code_status, review["status"]) if checks_enabled else "unreviewed"
        result.append({
            "method_id": method_id,
            "method": method_name,
            "field": raw.get("field"),
            "type": raw.get("type"),
            "units": raw.get("units"),
            "semantic_role": raw.get("semantic_role"),
            "branches": list(raw.get("branches", [])),
            "rule": raw.get("rule"),
            "identity_keys": list(raw.get("identity_keys", [])),
            "availability_rule": raw.get("availability_rule"),
            "producers": list(raw.get("producers", [])),
            "source_alternatives": producer_status,
            "binding_status": raw.get("binding_status"),
            "native_status": raw.get("native_status"),
            "supplied_source_alternative": raw.get("supplied_source_alternative"),
            "code_status": code_status,
            "code_failures": binding_failures,
            "manual_review": review,
            "manual_ledger": compact_ledger(matching_entry),
            "regression_tests": review_evidence(matching_entry)["tests"],
            "regression_evidence": review_evidence(matching_entry)["evidence"],
            "status": status,
        })
    return result


def method_rows(
    old_methods: dict[str, Any],
    *,
    fields: list[dict[str, Any]],
    object_rows: list[dict[str, Any]],
    core_rows: list[dict[str, Any]],
    checks_enabled: bool,
) -> list[dict[str, Any]]:
    method_findings = {row.get("id"): row for row in old_methods.get("method_findings", [])}
    retained = {row.get("method"): row for row in old_methods.get("retained_methods", [])}
    by_method: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in fields:
        by_method[row["method_id"]].append(row)
    old_to_name = {f"M{i:02d}": None for i in range(1, 13)}
    for finding in old_methods.get("method_findings", []):
        old_to_name[finding.get("id")] = finding.get("method")
    rows: list[dict[str, Any]] = []
    for method_id in sorted(old_to_name):
        method_name = old_to_name[method_id]
        method_fields = by_method.get(method_id, [])
        # Method acceptance is gated by every bound field and every object
        # reused by that method.  A retained N=0 report is evidence of no
        # historical denominator, not evidence of a pass.
        method_objects = [row for row in object_rows if method_id in row.get("methods", [])]
        object_statuses = Counter(row.get("status") for row in method_objects)
        field_statuses = Counter(row.get("status") for row in method_fields)
        code_fail = any(row.get("status") == "implementation_fail" for row in method_objects + method_fields)
        unresolved = any(row.get("status") != "complete" for row in method_objects + method_fields)
        status = "implementation_fail" if code_fail else "unreviewed" if unresolved or not checks_enabled else "complete"
        finding = method_findings.get(method_id, {})
        retained_row = retained.get(method_name, {})
        rows.append({
            "id": method_id,
            "method": method_name,
            "status": status,
            "field_count": len(method_fields),
            "field_status_counts": dict(sorted(field_statuses.items())),
            "object_count": len(method_objects),
            "object_status_counts": dict(sorted(object_statuses.items())),
            "field_bindings": method_fields,
            "linked_old_method_obligation": {
                "finding": finding.get("finding"),
                "first_implementation_focus": finding.get("first_implementation_focus"),
                "object_memberships": finding.get("object_memberships"),
                "report": retained_row.get("report"),
                "retained_status": retained_row.get("status"),
            },
            "retained_historical": {
                "n": None,
                "retained_n": retained_row.get("n"),
                "retained_N": retained_row.get("N"),
                "source_selector_holes": retained_row.get("source_selector_holes"),
                "fixture_failures": retained_row.get("fixture_failures"),
                "leakage": retained_row.get("leakage"),
                "proxy_as_faithful": retained_row.get("proxy_as_faithful"),
                "report": retained_row.get("report"),
                "json_sha256": retained_row.get("json_sha256"),
            },
            "evidence": {
                "old_finding": finding.get("finding"),
                "old_report": OLD_METHODS.as_posix(),
                "retained_report": retained_row.get("report"),
            },
        })
    return rows


def _has_explicit_limitation(ledger: Any) -> bool:
    """Whether a ledger explicitly records a limitation for the row."""

    if not isinstance(ledger, dict):
        return False
    limitation_keys = {
        "remaining_limitation", "remaining_limitations", "genuine_limits",
        "limitations", "limitation", "source_limitations", "data_limitations",
    }
    return any(bool(ledger.get(key)) for key in limitation_keys)


def _evidence_status(row: dict[str, Any]) -> str:
    """Classify explicit producer/review evidence without calling it acceptance."""

    implementation = row.get("implementation") if isinstance(row.get("implementation"), dict) else row
    manual = implementation.get("manual_review") if isinstance(implementation.get("manual_review"), dict) else {}
    ledger = implementation.get("manual_ledger") if isinstance(implementation.get("manual_ledger"), dict) else {}
    ledger_row = ledger.get("row")
    if implementation.get("executable_status") == "implementation_fail":
        return "gaps"
    if implementation.get("binding_status") in {"missing_implementation", "missing_native_implementation"}:
        return "gaps"
    if implementation.get("native_status") == "missing_native_implementation":
        return "gaps"
    # These counts describe reviewed routes, not successful native runs.
    if manual.get("status") == "resolved" and _has_explicit_limitation(ledger_row):
        return "reviewed_with_limitations"
    if implementation.get("native_status") == "implemented" or implementation.get("native_producer_registered"):
        return "native_route"
    native_status = implementation.get("native_status")
    if native_status == "parent_derived" or implementation.get("derived_producer_registered"):
        return "parent_derived_route"
    if native_status == "supplied_record":
        return "supplied_record_route"
    route_counts = implementation.get("producer_coverage", {}).get("route_counts", {})
    if native_status == "source_only" or route_counts.get("supplied_source_interpretation", 0):
        return "supplied_source_route"
    if implementation.get("recipe_registered") is False or implementation.get("output_schema_registered_ok") is False:
        return "gaps"
    return "unclassified"


def summary_dimension(rows: list[dict[str, Any]], dimension: str, *, checks_enabled: bool) -> dict[str, Any]:
    statuses = Counter()
    evidence_statuses = Counter()
    for row in rows:
        if dimension == "software":
            status = row.get("status")
        else:
            status = (row.get("dimensions", {}).get(dimension) or {}).get("status", "unavailable")
        statuses[status] += 1
        evidence_statuses[_evidence_status(row)] += 1
    # Keep the named evidence classes visible even when a current run has no
    # row in one class; a missing key would be easy to misread as zero
    # evidence or as a completed review.
    for evidence_class in ("native_route", "parent_derived_route", "supplied_record_route", "supplied_source_route", "gaps", "reviewed_with_limitations"):
        evidence_statuses.setdefault(evidence_class, 0)
    resolved_count = sum(value for key, value in statuses.items() if key in {"resolved", "complete", "pass", "passed"})
    implementation_fail = statuses.get("implementation_fail", 0) or statuses.get("fail", 0)
    unreviewed = sum(value for key, value in statuses.items() if key in {"unreviewed", "missing_review"})
    unavailable = statuses.get("unavailable", 0)
    reviewed_limits = sum(value for key, value in statuses.items() if key in {
        "reviewed_with_limitations", "native_validation_with_gaps", "source_or_process_records_required",
        "qualitative_source_required", "case_review_separate", "native_controls_reviewed",
    })
    unresolved = sum(statuses.values()) - resolved_count - implementation_fail - unreviewed - unavailable - reviewed_limits
    # ``unavailable`` means that this dimension has no explicit resolution
    # row.  It is kept separate from an obligation that was reviewed and left
    # open, and from a software implementation failure.
    status = (
        "implementation_fail" if implementation_fail
        else "unreviewed" if unreviewed or unresolved
        else "reviewed_with_limitations" if reviewed_limits
        else "resolved" if not unavailable
        else "unavailable"
    )
    if not checks_enabled and dimension == "software":
        status = "unreviewed"
    return {
        "status": status,
        "n": sum(statuses.values()),
        "resolved": resolved_count,
        "unreviewed": unreviewed,
        "unavailable": unavailable,
        "reviewed_with_limitations": reviewed_limits,
        "implementation_fail": implementation_fail,
        "status_counts": dict(sorted(statuses.items())),
        "evidence_status_counts": dict(sorted(evidence_statuses.items())),
        "evidence": "object rows and explicit manual ledger dimension statuses",
    }


def historical_summary(old_methods: dict[str, Any]) -> dict[str, Any]:
    retained = old_methods.get("retained_methods", [])
    return {
        "status": "unavailable",
        "n": None,
        "retained_method_count": len(retained),
        "retained_n_total": sum((row.get("n") or 0) for row in retained),
        "retained_N_total": sum((row.get("N") or 0) for row in retained),
        "unavailable": 1,
        "evidence_status_counts": {"unavailable": 1},
        "reason": "retained method reports contain no historical candidates; an empty denominator is not an acceptance result",
        "evidence": display_path(OLD_METHODS),
    }


def top_status(
    object_rows: list[dict[str, Any]],
    core_rows: list[dict[str, Any]],
    fields: list[dict[str, Any]],
    *,
    checks_enabled: bool,
    historical: dict[str, Any],
) -> str:
    all_rows = object_rows + core_rows + fields
    if any(row.get("status") == "implementation_fail" for row in all_rows):
        return "implementation_fail"
    # Historical discovery is a separate dimension.  An unavailable retained
    # cohort must not downgrade or upgrade software obligation status.
    if not checks_enabled:
        return "unreviewed"
    if any(row.get("status") != "complete" for row in all_rows):
        return "unreviewed"
    return "complete"


def markdown_escape(value: Any) -> str:
    text = "—" if value is None or value == "" else str(value)
    return text.replace("|", "\\|").replace("\n", " ")


def short_note(value: Any, limit: int = 280) -> str:
    text = markdown_escape(value)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    out.extend("| " + " | ".join(short_note(value) for value in row) + " |" for row in rows)
    return out


def build_markdown(matrix: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Phase 1 completion matrix",
        "",
        f"Status: **{matrix['status']}**. Registered inventory, fixture passes, and source-hole handlers remain separate from obligation resolution.",
        "",
        "The JSON companion contains the complete typed schemas, field bindings, fixture check IDs/results, ledger rows, and artifact hashes. This document keeps the review table readable by omitting fixture payloads.",
        "",
        "## Inventory and checks",
        "",
    ]
    summary = matrix["summary"]
    lines.extend(md_table(
        ["dimension", "status", "n", "resolved", "unreviewed", "unavailable", "implementation_fail", "evidence status counts"],
        [[name, values.get("status"), values.get("n"), values.get("resolved"), values.get("unreviewed"), values.get("unavailable"), values.get("implementation_fail"), values.get("evidence_status_counts")]
         for name, values in summary.items()],
    ))
    lines.extend([
        "",
        f"Object obligations: {matrix['counts']['objects']}; core contracts: {matrix['counts']['core_contracts']}; methods: {matrix['counts']['methods']}; method fields: {matrix['counts']['method_fields']}.",
        f"Registered normal fixtures: {matrix['checks']['object_fixtures']['registered_fixture_count']}; normal object fixtures checked: {matrix['checks']['object_fixtures']['normal_fixture_count']}; object fixture result rows including C08 mutations: {matrix['checks']['object_fixtures']['result_row_count']}; output schema checks: {matrix['checks']['output_schema']['check_count']}.",
        f"Fresh regression audit: {matrix['checks']['regression_audit']['status']}; probes: {matrix['checks']['regression_audit']['probe_count'] if matrix['checks']['regression_audit']['probe_count'] is not None else '—'} / {matrix['checks']['regression_audit']['expected_probe_count']} expected.",
        "",
        "## Objects",
        "",
    ])
    lines.extend(md_table(
        ["id", "title", "legacy", "code", "manual review", "status", "fixtures", "schema", "tests", "native/derived", "current implementation"],
        [[
            row["id"], row.get("title"), row.get("inspection_class"), row["implementation"].get("executable_status"),
            row["implementation"].get("manual_review", {}).get("status"), row.get("status"),
            sum(row["implementation"].get("fixture_status_counts", {}).values()),
            sum(row["implementation"].get("output_schema_status_counts", {}).values()),
            len(row["implementation"].get("regression_tests", [])),
            "/".join(row["implementation"].get("producer_kinds", [])) or "—", row.get("notes"),
        ] for row in matrix["objects"]],
    ))
    lines.extend(["", "## Core contracts", ""])
    lines.extend(md_table(
        ["id", "legacy status", "executable evidence/status", "manual review", "status", "current implementation"],
        [[
            row["id"], row.get("legacy_status"),
            ", ".join(f"{check['id']}:{check['status']}" for check in row.get("fixture_checks", [])) or "—",
            row.get("manual_review", {}).get("status"), row.get("status"),
            ((row.get("manual_ledger") or {}).get("row") or {}).get("implemented_obligation"),
        ] for row in matrix["core_contracts"]],
    ))
    lines.extend(["", "## Methods", ""])
    lines.extend(md_table(
        ["id", "method", "status", "fields", "objects", "field statuses", "retained N", "retained source holes", "retained leakage", "retained proxy-as-faithful", "original audit finding"],
        [[
            row["id"], row.get("method"), row.get("status"), row.get("field_count"), row.get("object_count"),
            row.get("field_status_counts"), row.get("retained_historical", {}).get("retained_N"),
            row.get("retained_historical", {}).get("source_selector_holes"), row.get("retained_historical", {}).get("leakage"),
            row.get("retained_historical", {}).get("proxy_as_faithful"), row.get("linked_old_method_obligation", {}).get("finding"),
        ] for row in matrix["methods"]],
    ))
    lines.extend(["", "## Method field bindings", ""])
    lines.extend(md_table(
        ["method", "field", "type", "producers", "binding", "native", "source alternative", "code", "status"],
        [[
            row.get("method_id"), row.get("field"), row.get("type"), ", ".join(row.get("producers", [])),
            row.get("binding_status"), row.get("native_status"), short_note(row.get("supplied_source_alternative"), 120),
            row.get("code_status"), row.get("status"),
        ] for row in matrix["method_fields"]],
    ))
    lines.extend(["", "## PHASE — retained historical run (not an acceptance result)", ""])
    phase_rows = []
    for row in matrix["methods"]:
        retained = row.get("retained_historical", {})
        retained_status = retained.get("retained_status") or "not recorded"
        phase_rows.append([
            row.get("method"), "historical/source", None, None,
            f"unavailable (retained report: {retained_status})", retained.get("report"),
        ])
    lines.extend(md_table(["family", "variant", "n", "faithful_disagreements", "status", "report path"], phase_rows))
    lines.extend(["", "## Audit — current contract coverage", ""])
    audit_rows = []
    for row in matrix["methods"]:
        retained = row.get("retained_historical", {})
        retained_status = retained.get("retained_status") or "not recorded"
        audit_rows.append([
            row.get("method"), row.get("id"), row.get("status"),
            f"current contract checks: {row.get('status')}", "unavailable (no historical cohort)",
            "unavailable (no historical cohort)",
            f"retained report status: {retained_status}; original audit: {row.get('linked_old_method_obligation', {}).get('finding') or 'current contract coverage is separate from historical discovery'}",
        ])
    lines.extend(md_table(["family", "id", "verdict", "fixture", "leakage", "proxy-as-faithful", "notes"], audit_rows))
    lines.append("")
    return "\n".join(lines)


def build_matrix(*, checks_enabled: bool, extra_ledgers: list[Path] | None = None) -> dict[str, Any]:
    # Importing the object package is part of the inventory operation.  It is
    # intentionally kept here so --no-checks can still fail clearly on a
    # malformed registry while skipping expensive fixture execution.
    sys.path.insert(0, str(SRC_ROOT))
    from trading_research.research.method_pack.assembly import producer_coverage_matrix
    from trading_research.research.method_pack.contracts import OUTPUT_SCHEMAS
    from trading_research.research.method_pack.objects import FIXTURES, RECIPES
    from trading_research.research.method_pack.objects.native_boundary import DERIVED_PRODUCERS, NATIVE_PRODUCERS
    from trading_research.research.method_pack.protocol import REQUIRED

    old_objects, old_core, old_methods = load_old_reports()
    object_ledger_rows, core_ledger_rows, method_field_ledger_rows, ledger_inputs = load_ledgers(extra_ledgers)
    regression_audit = regression_audit_summary()
    old_object_ids = [row.get("id") for row in old_objects.get("objects", [])]
    expected_object_ids = [f"O{i:03d}" for i in range(1, 167)]
    old_inventory_errors = []
    if old_object_ids != expected_object_ids:
        old_inventory_errors.append("old object audit does not contain ordered O001..O166")

    object_ids = list(expected_object_ids)
    coverage_rows = producer_coverage_matrix()
    fixture_rows, schema_rows = run_object_checks(object_ids=object_ids, checks_enabled=checks_enabled)
    fixture_by_object: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in fixture_rows:
        if OBJECT_RE.fullmatch(str(row.get("recipe", ""))):
            fixture_by_object[row["recipe"]].append(row)
    schema_by_object: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in schema_rows:
        recipe_id = row.get("recipe_id")
        if OBJECT_RE.fullmatch(str(recipe_id)):
            schema_by_object[recipe_id].append(row)
    native_docs = [path for path in NATIVE_VALIDATION_DOCS if path.is_file()]
    artifacts = native_artifact_inventory(object_ledger_rows, native_docs, core_ledger_rows)
    objects = object_rows(
        old_objects,
        recipes=RECIPES,
        required=REQUIRED,
        schemas=OUTPUT_SCHEMAS,
        native_producers=NATIVE_PRODUCERS,
        derived_producers=DERIVED_PRODUCERS,
        fixture_results_by_object=fixture_by_object,
        schema_results_by_object=schema_by_object,
        ledger_rows=object_ledger_rows,
        artifacts=artifacts,
        coverage_rows=coverage_rows,
        checks_enabled=checks_enabled,
    )
    # If an old audit is malformed, retain an explicit failure row instead of
    # silently padding the inventory with synthetic object records.
    if len(objects) != 166:
        old_inventory_errors.append(f"old object audit row count is {len(objects)}")

    core_checks = core_fixture_rows(checks_enabled)
    core_by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in core_checks:
        core_by_id[str(row.get("recipe"))].append(row)
    core_contracts: list[dict[str, Any]] = []
    for contract in sorted(old_core.get("contracts", []), key=lambda row: row.get("id", "")):
        cid = contract.get("id")
        checks = core_by_id.get(cid, [])
        review = explicit_review_status(core_ledger_rows.get(cid))
        if not checks_enabled:
            code_status = "not_run"
        elif not checks:
            # C00/C01/C05/C08 have no printed core fixture.  A manual row can
            # describe the obligation, but cannot turn absent executable
            # evidence into a completed acceptance check.
            code_status = "unreviewed"
        else:
            code_status = "implementation_fail" if any(row.get("status") != "pass" for row in checks) else "pass"
        status = status_from_evidence(code_status, review["status"]) if checks_enabled else "unreviewed"
        core_contracts.append({
            "id": cid,
            "line": contract.get("line"),
            "finding": contract.get("finding"),
            "legacy_status": contract.get("status"),
            "linked_old_contract_obligation": deepcopy(contract),
            "fixture_checks": checks,
            "fixture_check_ids": [row.get("id") for row in checks],
            "code_status": code_status,
            "code_evidence": ("printed core fixtures and/or verified final-suite regressions"
                              if checks else "no executable evidence for this contract"),
            "manual_review": review,
            "manual_ledger": compact_ledger(core_ledger_rows.get(cid)),
            "regression_tests": review_evidence(core_ledger_rows.get(cid))["tests"],
            "regression_evidence": review_evidence(core_ledger_rows.get(cid))["evidence"],
            "evidence": {
                "old_contract_path": OLD_CORE.as_posix(),
                "old_contract_sha256": sha256_file(OLD_CORE),
                "manual_ledger_path": (core_ledger_rows.get(cid) or {}).get("ledger_path"),
                "manual_ledger_sha256": (core_ledger_rows.get(cid) or {}).get("ledger_sha256"),
            },
            "status": status,
        })

    fields = fields_for_methods(
        coverage_rows,
        checks_enabled=checks_enabled,
        ledger_rows=object_ledger_rows,
        field_ledger_rows=method_field_ledger_rows,
    )
    methods = method_rows(old_methods, fields=fields, object_rows=objects, core_rows=core_contracts, checks_enabled=checks_enabled)
    historical = historical_summary(old_methods)
    overall_status = top_status(objects, core_contracts, fields, checks_enabled=checks_enabled, historical=historical)
    fixture_statuses = Counter(row.get("status") for row in fixture_rows)
    schema_statuses = Counter(row.get("status") for row in schema_rows)
    core_statuses = Counter(row.get("status") for row in core_checks)
    summary = {
        "software": summary_dimension(objects + core_contracts + fields, "software", checks_enabled=checks_enabled),
        "source_ambiguity": summary_dimension(objects, "source_ambiguity", checks_enabled=checks_enabled),
        "data": summary_dimension(objects, "data", checks_enabled=checks_enabled),
        "source_agreement": summary_dimension(objects, "source_agreement", checks_enabled=checks_enabled),
        "historical": historical,
    }
    matrix: dict[str, Any] = {
        "schema": "phase1-obligation-matrix-v1",
        "status": overall_status,
        "status_rule": "complete requires every object/core/method-field obligation to have an explicit resolved review marker plus passing code, fixture, and schema evidence; registration or fixture-green evidence alone never completes a row",
        "scope": {
            "objects": "O001..O166",
            "core_contracts": "C00..C08",
            "methods": "M01..M12",
            "method_fields": "all published operand bindings",
            "historical": "retained report snapshot only; no historical denominator is asserted",
        },
        "counts": {
            "objects": len(objects),
            "core_contracts": len(core_contracts),
            "methods": len(methods),
            "method_fields": len(fields),
            "recipes_registered": len(RECIPES),
            "output_schemas_registered": len(OUTPUT_SCHEMAS),
            "native_producers_registered": len(NATIVE_PRODUCERS),
            "derived_producers_registered": len(DERIVED_PRODUCERS),
            "normal_fixture_specs": len(FIXTURES),
            "object_fixture_result_rows": len(fixture_rows),
        },
        "checks": {
            "enabled": checks_enabled,
            "object_fixtures": {
                "normal_fixture_count": len({row.get("id") for row in fixture_rows if row.get("kind") == "positive"}),
                "registered_fixture_count": len(FIXTURES),
                "result_row_count": len(fixture_rows),
                "mutation_row_count": sum(row.get("kind", "").startswith("c08_") for row in fixture_rows),
                "detected_causal_violation_count": sum(bool(row.get("detected_causal_violation")) for row in fixture_rows),
                "status_counts": dict(sorted(fixture_statuses.items())),
                "failure_count": sum(value for key, value in fixture_statuses.items() if key != "pass"),
                "results": fixture_rows,
            },
            "output_schema": {
                "check_count": len(schema_rows),
                "expected_normal_fixture_count": 329,
                "status_counts": dict(sorted(schema_statuses.items())),
                "failure_count": sum(value for key, value in schema_statuses.items() if key != "pass"),
                "results": schema_rows,
            },
            "core_fixtures": {
                "check_count": len(core_checks),
                "status_counts": dict(sorted(core_statuses.items())),
                "failure_count": sum(value for key, value in core_statuses.items() if key != "pass"),
                "results": core_checks,
            },
            "regression_audit": regression_audit,
        },
        "summary": summary,
        "inputs": {
            "old_contracts": {
                "objects": {**input_record(OLD_OBJECTS, schema=old_objects.get("schema"), count=len(old_objects.get("objects", [])))},
                "core": {**input_record(OLD_CORE, schema=old_core.get("schema"), count=len(old_core.get("contracts", [])))},
                "methods": {**input_record(OLD_METHODS, schema=old_methods.get("schema"), count=len(old_methods.get("method_findings", [])))},
            },
            "ledgers": ledger_inputs,
            "native_validation_docs": [input_record(path) for path in NATIVE_VALIDATION_DOCS],
            "regression_audit": input_record(REGRESSION_AUDIT_PATH),
            "inventory_errors": old_inventory_errors,
        },
        "native_artifacts": artifacts,
        "objects": objects,
        "core_contracts": core_contracts,
        "methods": methods,
        "method_fields": fields,
    }
    return matrix


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-checks", action="store_true", help="build inventory/ledger matrix without fixture or schema execution")
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT_JSON, help="matrix JSON destination")
    parser.add_argument("--output-md", type=Path, default=DEFAULT_OUTPUT_MD, help="readable matrix Markdown destination")
    parser.add_argument("--ledger", action="append", type=Path, default=[], help="additional manual ledger JSON (repeatable)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        matrix = build_matrix(checks_enabled=not args.no_checks, extra_ledgers=args.ledger)
        output_json = args.output_json.resolve()
        output_md = args.output_md.resolve()
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        output_md.write_text(build_markdown(matrix), encoding="utf-8")
        print(json.dumps({
            "status": matrix["status"],
            "json": str(output_json),
            "markdown": str(output_md),
            "counts": matrix["counts"],
            "remaining_review": {
                "objects": sum(row.get("status") != "complete" for row in matrix["objects"]),
                "core_contracts": sum(row.get("status") != "complete" for row in matrix["core_contracts"]),
                "methods": sum(row.get("status") != "complete" for row in matrix["methods"]),
                "method_fields": sum(row.get("status") != "complete" for row in matrix["method_fields"]),
            },
        }, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        print(f"implementation_fail: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
