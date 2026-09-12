"""Replay the preserved independent Phase 1 lifecycle counterexamples.

This checker is deliberately separate from the original negative diagnostic.
The original probe and its output are preserved below ``original-check/`` and
are the only source of inputs here.  The checker reruns those exact mappings
through the registered recipe wrappers, validates the complete output
contract, and repeats the source admission path used by the original probe.

The input records are synthetic object-level counterexamples.  A passing run
is evidence that the repaired domain and admission paths reject the specified
violations; it makes no candidate or historical method-performance claim.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "implementation" / "src"
VALIDATION_DIR = ROOT / "implementation" / "validation" / "phase1-post-implementation-check"
ORIGINAL_DIR = VALIDATION_DIR / "original-check"
ORIGINAL_INPUTS = ORIGINAL_DIR / "lifecycle-probes.json"
PRESERVATION = ORIGINAL_DIR / "preservation.json"
REPORT = VALIDATION_DIR / "repair-regressions.json"

REVIEWED_COMMIT = "662463b545394e663937be2d83e0677f50492dc3"
EXPECTED_PROBES = (
    "order_control",
    "foreign_order_fill",
    "future_fill_backdated",
    "transition_control",
    "transition_missing_labels",
    "transition_backdated",
)
EXPECTED_RECIPES = {name: "O150" for name in EXPECTED_PROBES[:3]}
EXPECTED_RECIPES.update({name: "O166" for name in EXPECTED_PROBES[3:]})
VALID_PROBES = {"order_control", "transition_control"}
ORDER_PROBES = {"order_control", "foreign_order_fill", "future_fill_backdated"}
INVALID_PROBES = set(EXPECTED_PROBES) - VALID_PROBES

# These are the implementation files whose behavior this checker exercises.
# Keep this list explicit so the evidence records exactly what was tested.
IMPLEMENTATION_SOURCES = (
    "implementation/src/trading_research/research/method_pack/objects/lifecycles.py",
    "implementation/src/trading_research/research/method_pack/evidence.py",
    "implementation/src/trading_research/research/method_pack/protocol.py",
    "implementation/src/trading_research/research/method_pack/contracts.py",
    "implementation/src/trading_research/research/method_pack/logic.py",
    "implementation/src/trading_research/research/method_pack/source_config.py",
    "implementation/src/trading_research/research/method_pack/semantic_views.py",
    "implementation/src/trading_research/research/method_pack/objects/__init__.py",
    "implementation/src/trading_research/research/method_pack/objects/native_boundary.py",
    "implementation/src/trading_research/research/method_pack/assembly.py",
)


def _ensure_import_path() -> None:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> bytes:
    """Return the stable JSON encoding used for saved-input fingerprints."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def input_sha256(inputs: dict[str, Any]) -> str:
    return _sha256_bytes(canonical_json(inputs))


def _file_reference(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "sha256": sha256_file(path),
        "exists": path.is_file(),
    }


def _origin_references() -> tuple[dict[str, Any], list[str]]:
    """Validate and describe the preserved negative baseline files."""

    failures: list[str] = []
    if not PRESERVATION.is_file():
        return {
            "reviewed_commit": REVIEWED_COMMIT,
            "preservation_manifest": {"path": str(PRESERVATION), "exists": False},
            "files": [],
        }, [f"missing preservation manifest: {PRESERVATION}"]

    try:
        manifest = json.loads(PRESERVATION.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "reviewed_commit": REVIEWED_COMMIT,
            "preservation_manifest": {"path": str(PRESERVATION), "exists": True},
            "files": [],
        }, [f"cannot read preservation manifest: {type(exc).__name__}: {exc}"]

    manifest_commit = manifest.get("reviewed_commit")
    if manifest_commit != REVIEWED_COMMIT:
        failures.append(f"preservation manifest reviewed_commit {manifest_commit!r} != {REVIEWED_COMMIT!r}")

    listed: list[dict[str, Any]] = []
    for item in manifest.get("files", []):
        preserved_path = Path(item.get("preserved_path", ""))
        expected_hash = item.get("sha256")
        row: dict[str, Any] = {
            "path": item.get("path"),
            "preserved_path": str(preserved_path),
            "manifest_sha256": expected_hash,
        }
        if not preserved_path.is_file():
            row.update({"exists": False, "sha256": None, "hash_matches_manifest": False})
            failures.append(f"missing preserved origin file: {preserved_path}")
        else:
            actual_hash = sha256_file(preserved_path)
            row.update({
                "exists": True,
                "sha256": actual_hash,
                "hash_matches_manifest": actual_hash == expected_hash,
            })
            if actual_hash != expected_hash:
                failures.append(f"preserved origin hash changed: {preserved_path}")
        listed.append(row)

    required_paths = {
        str(ORIGINAL_DIR / "probe_lifecycles.py"),
        str(ORIGINAL_INPUTS),
        str(ORIGINAL_DIR / "POST_IMPLEMENTATION_CHECK.md"),
    }
    present_paths = {str(row.get("preserved_path")) for row in listed}
    for required in sorted(required_paths - present_paths):
        failures.append(f"preservation manifest omits origin file: {required}")

    origin = {
        "reviewed_commit": REVIEWED_COMMIT,
        "preservation_manifest": _file_reference(PRESERVATION),
        "files": listed,
    }
    return origin, failures


@dataclass(frozen=True)
class SavedCase:
    name: str
    recipe_id: str
    inputs: dict[str, Any]
    original_expected: str
    original_check_passed: bool
    source_index: int

    @property
    def input_sha256(self) -> str:
        return input_sha256(self.inputs)


def load_saved_cases() -> tuple[dict[str, Any], list[SavedCase], list[str]]:
    """Load the exact six mappings from the preserved original output."""

    origin, failures = _origin_references()
    if not ORIGINAL_INPUTS.is_file():
        failures.append(f"missing preserved input document: {ORIGINAL_INPUTS}")
        return origin, [], failures
    try:
        document = json.loads(ORIGINAL_INPUTS.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        failures.append(f"cannot read preserved input document: {type(exc).__name__}: {exc}")
        return origin, [], failures

    if document.get("reviewed_commit") != REVIEWED_COMMIT:
        failures.append(f"preserved input reviewed_commit {document.get('reviewed_commit')!r} != {REVIEWED_COMMIT!r}")
    rows = document.get("results")
    if not isinstance(rows, list):
        failures.append("preserved input document has no results array")
        return origin, [], failures
    if len(rows) != len(EXPECTED_PROBES):
        failures.append(f"preserved input count {len(rows)} != {len(EXPECTED_PROBES)}")

    cases: list[SavedCase] = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            failures.append(f"preserved result {index} is not a mapping")
            continue
        name = row.get("probe")
        recipe_id = row.get("recipe_id")
        inputs = row.get("inputs")
        expected_name = EXPECTED_PROBES[index] if index < len(EXPECTED_PROBES) else None
        if expected_name is None or name != expected_name:
            failures.append(f"preserved result {index} has unexpected probe order/name: {name!r}")
        if name not in EXPECTED_RECIPES:
            failures.append(f"preserved result {index} has unknown probe name: {name!r}")
            continue
        if recipe_id != EXPECTED_RECIPES[name]:
            failures.append(f"{name}: recipe {recipe_id!r} != {EXPECTED_RECIPES[name]!r}")
        if not isinstance(inputs, dict):
            failures.append(f"{name}: inputs are not a mapping")
            continue
        cases.append(SavedCase(
            name=name,
            recipe_id=recipe_id,
            inputs=deepcopy(inputs),
            original_expected=str(row.get("expected", "")),
            original_check_passed=row.get("check_passed") is True,
            source_index=index,
        ))

    by_name = {case.name: case for case in cases}
    if set(by_name) != set(EXPECTED_PROBES):
        failures.append(f"preserved probe names differ: {sorted(by_name)}")
    baseline_passed = sum(case.original_check_passed for case in cases)
    baseline_failures = len(cases) - baseline_passed
    if baseline_passed != 2 or baseline_failures != 4:
        failures.append(
            f"preserved negative baseline is {baseline_passed} passed/{baseline_failures} failed; expected 2/4"
        )
    if any(case.original_check_passed != (case.name in VALID_PROBES) for case in cases):
        failures.append("preserved baseline pass/fail polarity differs from the two-control/four-regression split")
    return origin, cases, failures


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        converted = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return converted if converted.is_finite() else None


def _zero_or_unknown(value: Any) -> bool:
    if value is None:
        return True
    converted = _decimal(value)
    return converted is not None and converted == 0


def _no_applied_fill(value: Any) -> tuple[bool, list[str]]:
    """Check that an invalid O150 result did not apply the supplied fill."""

    if not isinstance(value, dict):
        return False, ["result payload is not a mapping"]
    failures: list[str] = []
    # The public aliases are both checked because the domain keeps a legacy
    # spelling alongside the complete O150 schema.
    for key in ("filled_quantity", "filled", "position_quantity"):
        if key in value and not _zero_or_unknown(value.get(key)):
            failures.append(f"{key} records an applied quantity: {value.get(key)!r}")
    timeline = value.get("order_state_timeline")
    if timeline is not None:
        if not isinstance(timeline, list):
            failures.append("order_state_timeline is not a list")
        else:
            for index, row in enumerate(timeline):
                if not isinstance(row, dict):
                    failures.append(f"timeline row {index} is not a mapping")
                    continue
                kind = str(row.get("kind", "")).strip().lower().replace("-", "_")
                if kind in {"fill", "partial_fill"}:
                    # A rejected event may be retained for audit, but it must
                    # not show a filled/partially-filled resulting state or a
                    # positive resulting position quantity.
                    after = row.get("state_after")
                    if after in {"filled", "partially_filled"}:
                        failures.append(f"timeline row {index} applies a fill: state_after={after!r}")
                    if not _zero_or_unknown(row.get("position_quantity_after")):
                        failures.append(
                            f"timeline row {index} applies a position quantity: "
                            f"{row.get('position_quantity_after')!r}"
                        )
    return not failures, failures


def _result_value(result: Any) -> dict[str, Any]:
    value = getattr(result, "value", None)
    return value if isinstance(value, dict) else {}


def _result_snapshot(result: Any, *, schema_ok: bool, schema_error: str | None) -> dict[str, Any]:
    from trading_research.research.method_pack.protocol import jsonable

    return {
        "state": getattr(result, "state", None),
        "base_ok": getattr(result, "base_ok", None),
        "coverage_ok": getattr(result, "coverage_ok", None),
        "known_at": getattr(result, "known_at", None),
        "hole_ids": list(getattr(result, "hole_ids", []) or []),
        "reason": getattr(result, "reason", None),
        "schema_validation": {"ok": schema_ok, "error": schema_error},
        "value": jsonable(_result_value(result)),
    }


def _admission_snapshot(result: Any, *, accepted: bool, error: str | None) -> dict[str, Any]:
    from trading_research.research.method_pack.protocol import jsonable

    value = _result_value(result) if result is not None else {}
    return {
        "accepted": accepted,
        "error": error,
        "state": getattr(result, "state", None) if result is not None else None,
        "base_ok": getattr(result, "base_ok", None) if result is not None else None,
        "coverage_ok": getattr(result, "coverage_ok", None) if result is not None else None,
        "known_at": getattr(result, "known_at", None) if result is not None else None,
        "filled_quantity": jsonable(value.get("filled_quantity")) if value else None,
        "value": jsonable(value) if value else {},
    }


def evaluate_case(
    case: SavedCase,
    result: Any,
    *,
    schema_ok: bool,
    schema_error: str | None,
    source_audit: dict[str, Any] | None,
) -> list[str]:
    """Return failures for one case's repaired-behavior invariants.

    This function intentionally requires the two valid controls to remain
    computed and admitted.  An implementation that rejects every input cannot
    satisfy the checker.
    """

    failures: list[str] = []
    recipe_id = case.recipe_id
    state = getattr(result, "state", None)
    base_ok = getattr(result, "base_ok", None)
    coverage_ok = getattr(result, "coverage_ok", None)
    value = _result_value(result)

    if not schema_ok:
        failures.append(f"full output schema validation failed: {schema_error}")

    if case.name in VALID_PROBES:
        if state != "computed":
            failures.append(f"valid control must be computed, got {state!r}")
        if base_ok is not True:
            failures.append(f"valid control base_ok must be true, got {base_ok!r}")
        if coverage_ok is not True:
            failures.append(f"valid control coverage_ok must be true, got {coverage_ok!r}")
        if case.name == "order_control":
            filled = _decimal(value.get("filled_quantity"))
            if filled != Decimal("1"):
                failures.append(f"valid order control must apply one fill, got {value.get('filled_quantity')!r}")
            if value.get("lifecycle_valid") is not True:
                failures.append("valid order control must have lifecycle_valid=true")
        else:
            if value.get("from_state") != "D":
                failures.append(f"valid transition control from_state must be 'D', got {value.get('from_state')!r}")
            if value.get("to_state") != "A":
                failures.append(f"valid transition control to_state must be 'A', got {value.get('to_state')!r}")
            if value.get("transition_valid") is not True:
                failures.append("valid transition control must have transition_valid=true")
            if getattr(result, "hole_ids", None):
                failures.append(f"valid transition control has holes: {getattr(result, 'hole_ids', None)!r}")
        if case.name == "order_control":
            if source_audit is None or source_audit.get("accepted") is not True:
                failures.append("valid order control must pass supplied-source admission")
            elif source_audit.get("state") != "computed" or source_audit.get("base_ok") is not True:
                failures.append("admitted valid order control must remain computed/base_ok=true")
        return failures

    if case.name not in INVALID_PROBES:
        failures.append(f"unknown checker case {case.name!r}")
        return failures

    if state != "invalid" and case.name != "transition_missing_labels":
        failures.append(f"regression must be invalid, got {state!r}")
    if case.name == "transition_missing_labels":
        if state not in {"hole", "invalid"}:
            failures.append(f"missing transition labels must be hole/invalid, got {state!r}")
        if value.get("from_state") is not None or value.get("to_state") is not None:
            failures.append("missing transition labels must remain explicit nulls")
        if value.get("transition_valid") is not None:
            failures.append(
                f"missing transition labels must leave transition_valid unknown, got {value.get('transition_valid')!r}"
            )
        holes = {str(hole) for hole in getattr(result, "hole_ids", []) or []}
        label_holes = {
            hole for hole in holes
            if any(token in hole.lower() for token in ("from_state", "to_state", "state_label", "label"))
        }
        if not label_holes:
            failures.append(f"missing transition labels need explicit label holes, got {sorted(holes)!r}")
    else:
        if base_ok is not False:
            failures.append(f"invalid {case.name} must have base_ok=false, got {base_ok!r}")
        no_fill, no_fill_failures = _no_applied_fill(value)
        if not no_fill:
            failures.extend(f"invalid {case.name} applied supplied fill: {failure}" for failure in no_fill_failures)

    if recipe_id == "O150":
        if source_audit is None or source_audit.get("accepted") is not False:
            failures.append(f"invalid {case.name} must be rejected by supplied-source admission")
    return failures


def _run_order_admission(case: SavedCase, result: Any) -> tuple[Any | None, dict[str, Any]]:
    from trading_research.research.method_pack.evidence import audit_source_domain_object
    from trading_research.research.method_pack.semantic_views import AUTHORS
    from trading_research.research.method_pack.source_config import load_catalog

    source = load_catalog()["sources"]["REF"]
    citation = {
        "source_key": "REF",
        "source_file": source["path"],
        "sha256": source["sha256"],
        "page": 7,
        "image_id": "REF:7:page",
    }
    supplied = {
        "object_id": "supplied-" + case.name,
        "recipe_id": case.recipe_id,
        "method_id": "REFILL-STUDY",
        "author": sorted(AUTHORS["REFILL-STUDY"])[0],
        "instrument_id": "NQ",
        "known_at": getattr(result, "known_at", None),
        "value": {},
        "evidence_ids": ["evidence"],
    }
    evidence = {
        "evidence": {
            "payload": {
                "recipe_id": case.recipe_id,
                "recipe_inputs": deepcopy(case.inputs),
                "source_citation": citation,
            }
        }
    }
    try:
        admitted = audit_source_domain_object(supplied, evidence)
    except Exception as exc:  # admission rejection is the expected invalid path
        return None, _admission_snapshot(None, accepted=False,
                                         error=f"{type(exc).__name__}: {exc}")
    return admitted, _admission_snapshot(admitted, accepted=True, error=None)


def _source_hashes() -> tuple[dict[str, str | None], list[str]]:
    hashes: dict[str, str | None] = {}
    failures: list[str] = []
    for relative in IMPLEMENTATION_SOURCES:
        path = ROOT / relative
        if not path.is_file():
            hashes[relative] = None
            failures.append(f"missing implementation source: {path}")
        else:
            hashes[relative] = sha256_file(path)
    return hashes, failures


def _case_source_references() -> dict[str, Any]:
    """Capture the immutable REF citation used by the original order probe."""

    try:
        _ensure_import_path()
        from trading_research.research.method_pack.source_config import load_catalog

        source = load_catalog()["sources"]["REF"]
        path = Path(source["path"])
        return {
            "source_key": "REF",
            "source_file": source["path"],
            "catalog_sha256": source["sha256"],
            "file_exists": path.is_file(),
            "file_sha256": sha256_file(path) if path.is_file() else None,
            "page": 7,
            "image_id": "REF:7:page",
        }
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def run_checks(cases: list[SavedCase]) -> tuple[list[dict[str, Any]], list[str]]:
    """Run all saved cases while retaining failures for the final artifact."""

    _ensure_import_path()
    from trading_research.research.method_pack import objects  # noqa: F401
    from trading_research.research.method_pack.contracts import validate_output
    from trading_research.research.method_pack.protocol import RECIPES, run_recipe

    rows: list[dict[str, Any]] = []
    setup_failures: list[str] = []
    for case in cases:
        recipe_registered = case.recipe_id in RECIPES
        result: Any = SimpleNamespace(state=None, base_ok=None, coverage_ok=None,
                                      known_at=None, hole_ids=[], reason=None, value={})
        schema_ok = False
        schema_error: str | None = None
        run_error: str | None = None
        if not recipe_registered:
            run_error = f"recipe {case.recipe_id} is not registered"
            setup_failures.append(f"{case.name}: {run_error}")
        else:
            try:
                result = run_recipe(case.recipe_id, deepcopy(case.inputs))
            except Exception as exc:
                run_error = f"{type(exc).__name__}: {exc}"
                setup_failures.append(f"{case.name}: recipe raised {run_error}")
            else:
                try:
                    validate_output(result)
                    schema_ok = True
                except Exception as exc:
                    schema_error = f"{type(exc).__name__}: {exc}"

        source_audit: dict[str, Any] | None = None
        admission_result: Any | None = None
        if case.name in ORDER_PROBES and run_error is None:
            try:
                admission_result, source_audit = _run_order_admission(case, result)
            except Exception as exc:
                source_audit = _admission_snapshot(
                    None,
                    accepted=False,
                    error=f"admission setup {type(exc).__name__}: {exc}",
                )
                setup_failures.append(f"{case.name}: admission setup raised {type(exc).__name__}: {exc}")

        failures = evaluate_case(
            case,
            result,
            schema_ok=schema_ok,
            schema_error=schema_error or run_error,
            source_audit=source_audit,
        )
        row = {
            "probe": case.name,
            "recipe_id": case.recipe_id,
            "source_index": case.source_index,
            "input_sha256": case.input_sha256,
            "input_hash_algorithm": "sha256(canonical-json; UTF-8; sorted keys; compact separators)",
            "inputs": deepcopy(case.inputs),
            "origin_expected": case.original_expected,
            "origin_check_passed": case.original_check_passed,
            "recipe_registered": recipe_registered,
            "result": _result_snapshot(result, schema_ok=schema_ok, schema_error=schema_error or run_error),
            "source_audit": source_audit,
            "check_passed": not failures,
            "failures": failures,
            "historical_candidate_claim": False,
        }
        rows.append(row)
        print(case.name, "PASS" if not failures else "FAIL",
              f"state={getattr(result, 'state', None)} known_at={getattr(result, 'known_at', None)}")
    return rows, setup_failures


def main() -> int:
    _ensure_import_path()
    source_hashes, source_failures = _source_hashes()
    origin, cases, origin_failures = load_saved_cases()
    fatal_failures = [*source_failures, *origin_failures]
    rows: list[dict[str, Any]] = []
    setup_failures: list[str] = []
    if cases and not fatal_failures:
        try:
            rows, setup_failures = run_checks(cases)
        except Exception as exc:
            fatal_failures.append(f"checker setup failed: {type(exc).__name__}: {exc}")

    failures = [*fatal_failures, *setup_failures,
                *(f"{row['probe']}: {failure}" for row in rows for failure in row["failures"])]
    passed = sum(row["check_passed"] for row in rows)
    report = {
        "schema_version": "phase1-postcheck-repair-regressions.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_commit": REVIEWED_COMMIT,
        "status": "pass" if not failures and len(rows) == len(EXPECTED_PROBES) else "fail",
        "checks": len(rows),
        "expected_checks": len(EXPECTED_PROBES),
        "passed": passed,
        "failures": len(failures),
        "failure_reasons": failures,
        "scope": {
            "synthetic_inputs_only": True,
            "candidate_claims": False,
            "historical_claims": False,
            "description": "Object-level lifecycle regression evidence only; no candidate/history performance claim.",
        },
        "original_negative_baseline": {
            "checks": len(cases),
            "passed": sum(case.original_check_passed for case in cases),
            "failures": sum(not case.original_check_passed for case in cases),
            "valid_controls": sorted(name for name in (case.name for case in cases) if name in VALID_PROBES),
            "source": str(ORIGINAL_INPUTS),
            "sha256": sha256_file(ORIGINAL_INPUTS) if ORIGINAL_INPUTS.is_file() else None,
        },
        "origin_evidence": origin,
        "origin_paths": {
            "report": str(ORIGINAL_DIR / "POST_IMPLEMENTATION_CHECK.md"),
            "probe_script": str(ORIGINAL_DIR / "probe_lifecycles.py"),
            "probe_inputs": str(ORIGINAL_INPUTS),
            "preservation_manifest": str(PRESERVATION),
        },
        "saved_input_hash_algorithm": "sha256(canonical-json; UTF-8; sorted keys; compact separators)",
        "saved_input_hashes": {case.name: case.input_sha256 for case in cases},
        "tested_implementation_source_hashes": source_hashes,
        "runtime": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "pythonpath_source": str(SRC),
        },
        "source_citation": _case_source_references(),
        "results": rows,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"{passed} checks passed; {len(failures)} failures")
    print(f"repair regression evidence: {REPORT}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
