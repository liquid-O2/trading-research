"""Task, subphase, phase and lineage verification. Failures are data, not report text."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping
import json

from trading_research.errors import ContractError
from trading_research.research.contracts.identity import (
    ASSURANCE_VERSION,
    DISPOSITIONS,
    SCHEMA_TASK_RECEIPT,
    artifact_entry,
    code_snapshot_document,
    digest,
    file_digest,
    make_task_receipt,
    plan_snapshot_document,
    semantic_run_id,
    validate_receipt_shape,
    write_json_document,
    write_snapshot_tree,
    write_task_receipt,
)

SCHEMA_SUBPHASE_RECEIPT = "research-subphase-receipt-v2"
SCHEMA_PHASE_RECEIPT = "research-phase-receipt-v2"
SCHEMA_LINEAGE_MANIFEST = "research-lineage-manifest-v1"
SCHEMA_TASK_GRAPH = "research-task-graph-v1"
SCHEMA_GATE_REVIEW = "research-gate-review-v2"
SCHEMA_EVIDENCE_MATRIX = "research-evidence-matrix-v2"
PINNED_CHECKER_SHA256 = "c9441fea0a79674991522ae8db5347cdd1060f372d6aa5cffd425c7f30d6b800"
PINNED_CHECKER_CASES = 27
EVIDENCE_STATUSES = frozenset({"pass", "fail", "unsupported", "accepted-limit"})
MATRIX_CHECK_FIELDS = (
    "id",
    "requirement",
    "code_refs",
    "test_nodeids",
    "command_indices",
    "evidence",
    "expected",
    "observed",
    "oracle",
    "status",
)

DEFAULT_ROOT = Path("/workspace")
DEFAULT_GRAPH_PATH = DEFAULT_ROOT / "planning/research-program/TASK_GRAPH.json"
DEFAULT_RECEIPTS_ROOT = DEFAULT_ROOT / "implementation/reports/research-work"

GATES = frozenset({"pass", "closed_with_limits", "fail"})
PHASE_1_5_GATES = frozenset({"pass", "closed_with_limits", "fail", "missing"})
PHASES = frozenset({"phase-1-5", "phase-2"})
SHA256_LEN = 64
RUN_ID_LEN = 16
HEX_CHARS = frozenset("0123456789abcdef")
SUCCESS_DISPOSITIONS = frozenset({
    "implemented_verified",
    "retained_baseline",
    "rejected_by_evidence",
    "inconclusive_support",
    "unsupported_owned_input",
})
SOFTWARE_MARKERS = (
    "not implemented",
    "missing software",
    "blocked_implementation",
    "no receipt",
    "missing task",
    "tests not run",
    "missing test",
    "verifier pending",
    "not yet created",
)
INPUT_MARKERS = (
    "owned input",
    "unsupported_owned_input",
    "input limit",
    "input_limit",
    "native",
    "mbp",
    "feed gap",
    "missing date",
    "coverage gap",
    "calendar",
    "session prefix",
)

Kind = Literal["task", "subphase", "phase", "lineage"]


class FailureCode:
    JSON_PARSE = "JSON_PARSE"
    SCHEMA = "SCHEMA"
    MISSING_KEY = "MISSING_KEY"
    UNKNOWN_TASK = "UNKNOWN_TASK"
    ACCEPTANCE = "ACCEPTANCE"
    DISPOSITION = "DISPOSITION"
    ARTIFACT_MISSING = "ARTIFACT_MISSING"
    ARTIFACT_HASH = "ARTIFACT_HASH"
    ARTIFACT_BYTES = "ARTIFACT_BYTES"
    COMMAND_EXIT = "COMMAND_EXIT"
    COMMAND_MISSING = "COMMAND_MISSING"
    COMMAND_SHAPE = "COMMAND_SHAPE"
    PREDECESSOR_MISSING = "PREDECESSOR_MISSING"
    PREDECESSOR_HASH = "PREDECESSOR_HASH"
    GATE = "GATE"
    BLOCKED_IMPLEMENTATION = "BLOCKED_IMPLEMENTATION"
    SOFTWARE_MISSING = "SOFTWARE_MISSING"
    PHASE_1_5_GATE = "PHASE_1_5_GATE"
    TASK_MISSING = "TASK_MISSING"
    LINEAGE_CLOCK = "LINEAGE_CLOCK"
    LINEAGE_HASH = "LINEAGE_HASH"
    GRAPH_CYCLE = "GRAPH_CYCLE"
    COVERAGE = "COVERAGE"
    USAGE = "USAGE"
    IDENTITY = "IDENTITY"
    INVENTORY = "INVENTORY"
    TASK_MISMATCH = "TASK_MISMATCH"
    UNKNOWN_SUBPHASE = "UNKNOWN_SUBPHASE"
    GATE_REVIEW = "GATE_REVIEW"


@dataclass(frozen=True, slots=True)
class CheckFailure:
    code: str
    path: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "detail": self.detail}


@dataclass(frozen=True, slots=True)
class VerificationResult:
    kind: Kind
    ok: bool
    path: str
    failures: tuple[CheckFailure, ...]

    def payload(self) -> list[dict[str, str]] | dict[str, Any]:
        if self.ok:
            return {"ok": True, "kind": self.kind, "path": self.path}
        return [item.to_dict() for item in self.failures]


@dataclass(frozen=True, slots=True)
class TaskSpec:
    id: str
    phase: str
    subphase: str
    dependencies: tuple[str, ...]
    required_acceptance_keys: tuple[str, ...]
    allowed_terminal_statuses: frozenset[str]
    native: bool
    artifacts: tuple[str, ...]
    assurance_cases: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TaskGraph:
    path: str
    tasks: Mapping[str, TaskSpec]
    cycles: tuple[tuple[str, ...], ...]
    required_task_artifacts: tuple[str, ...]
    assurance_version: str
    coordinator_artifacts: Mapping[str, tuple[str, ...]]

    def require(self, task_id: str) -> TaskSpec | None:
        return self.tasks.get(task_id)

    def for_subphase(self, subphase_id: str) -> tuple[TaskSpec, ...]:
        return tuple(spec for spec in self.tasks.values() if spec.subphase == subphase_id)

    def known_subphases(self) -> frozenset[str]:
        return frozenset(spec.subphase for spec in self.tasks.values() if spec.subphase)

    def for_phase(self, phase: str) -> tuple[TaskSpec, ...]:
        return tuple(spec for spec in self.tasks.values() if spec.phase == phase)


@dataclass(frozen=True, slots=True)
class TaskRef:
    task_id: str
    path: str
    sha256: str
    disposition: str | None = None


@dataclass(frozen=True, slots=True)
class TaskReceiptView:
    path: str
    document: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class SubphaseReceiptView:
    path: str
    schema_version: str
    subphase_id: str
    run_id: str
    task_receipts: Mapping[str, TaskRef]
    accepted_schema_versions: tuple[Any, ...]
    native_slice_ids: tuple[Any, ...]
    test_evidence: tuple[Mapping[str, Any], ...]
    coverage: Mapping[str, Any]
    single_writer_audit: Mapping[str, Any]
    gate: str
    unresolved: tuple[Any, ...]
    reason: str
    document: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class PhaseReceiptView:
    path: str
    schema_version: str
    phase: str
    gate: str
    task_receipts: Mapping[str, TaskRef]
    phase_1_5_gate: str
    document: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class LineageManifestView:
    path: str
    schema_version: str
    records: tuple[Any, ...]
    document: Mapping[str, Any]


_SUBPHASE_KEYS = (
    "schema_version",
    "assurance_version",
    "subphase_id",
    "run_id",
    "task_receipts",
    "accepted_schema_versions",
    "native_slice_ids",
    "test_evidence",
    "coverage",
    "single_writer_audit",
    "gate",
    "unresolved",
    "reason",
)
_PHASE_KEYS = (
    "schema_version",
    "phase",
    "gate",
    "task_receipts",
    "phase_1_5_gate",
)


def _hex_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == SHA256_LEN and set(value) <= HEX_CHARS


def _run_id(value: object) -> bool:
    return isinstance(value, str) and len(value) == RUN_ID_LEN and set(value) <= HEX_CHARS


def load_json_document(path: Path) -> tuple[Any | None, tuple[CheckFailure, ...]]:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return None, (CheckFailure(FailureCode.JSON_PARSE, str(path), f"cannot read file: {exc}"),)
    try:
        document = json.loads(
            text,
            parse_constant=lambda constant: (_ for _ in ()).throw(ValueError(constant)),
        )
    except ValueError as exc:
        return None, (CheckFailure(FailureCode.JSON_PARSE, str(path), f"invalid JSON: {exc}"),)
    return document, ()


def _cycles(tasks: Mapping[str, TaskSpec]) -> tuple[tuple[str, ...], ...]:
    visiting: set[str] = set()
    seen: set[str] = set()
    found: list[tuple[str, ...]] = []

    def walk(node: str, stack: list[str]) -> None:
        if node in visiting:
            start = stack.index(node)
            found.append(tuple(stack[start:] + [node]))
            return
        if node in seen or node not in tasks:
            return
        visiting.add(node)
        stack.append(node)
        for dep in tasks[node].dependencies:
            walk(dep, stack)
        stack.pop()
        visiting.remove(node)
        seen.add(node)

    for task_id in tasks:
        walk(task_id, [])
    return tuple(found)


def load_task_graph(path: Path | None = None) -> tuple[TaskGraph | None, tuple[CheckFailure, ...]]:
    graph_path = Path(path) if path is not None else DEFAULT_GRAPH_PATH
    document, failures = load_json_document(graph_path)
    if failures:
        return None, failures
    if not isinstance(document, dict) or not isinstance(document.get("tasks"), list):
        return None, (CheckFailure(FailureCode.SCHEMA, str(graph_path), "task graph must be an object with a tasks list"),)
    specs: dict[str, TaskSpec] = {}
    problems: list[CheckFailure] = []
    for index, raw in enumerate(document["tasks"]):
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str):
            problems.append(CheckFailure(FailureCode.SCHEMA, str(graph_path), f"tasks[{index}] is not a task object"))
            continue
        allowed = raw.get("allowed_terminal_statuses")
        keys = raw.get("required_acceptance_keys")
        deps = raw.get("dependencies") or ()
        if not isinstance(allowed, list) or not isinstance(keys, list) or not isinstance(deps, (list, tuple)):
            problems.append(CheckFailure(FailureCode.SCHEMA, str(graph_path), f"{raw['id']} missing graph fields"))
            continue
        specs[raw["id"]] = TaskSpec(
            id=raw["id"],
            phase=str(raw.get("phase") or ""),
            subphase=str(raw.get("subphase") or ""),
            dependencies=tuple(str(item) for item in deps),
            required_acceptance_keys=tuple(str(item) for item in keys),
            allowed_terminal_statuses=frozenset(str(item) for item in allowed),
            native=bool(raw.get("native", False)),
            artifacts=tuple(str(item) for item in (raw.get("artifacts") or ())),
            assurance_cases=tuple(str(item) for item in (raw.get("assurance_cases") or ())),
        )
    required_common = document.get("required_task_artifacts") or ()
    coordinator = document.get("coordinator_artifacts") or {}
    mapped = {str(key): tuple(str(item) for item in value) for key, value in coordinator.items()} if isinstance(coordinator, dict) else {}
    graph = TaskGraph(
        path=str(graph_path),
        tasks=specs,
        cycles=_cycles(specs),
        required_task_artifacts=tuple(str(item) for item in required_common),
        assurance_version=str(document.get("assurance_version") or ""),
        coordinator_artifacts=mapped,
    )
    for cycle in graph.cycles:
        problems.append(CheckFailure(FailureCode.GRAPH_CYCLE, str(graph_path), " -> ".join(cycle)))
    return graph, tuple(problems)


def _append(failures: list[CheckFailure], code: str, path: str, detail: str) -> None:
    failures.append(CheckFailure(code, path, detail))


def _is_software_limit(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in SOFTWARE_MARKERS)


def _is_input_limit(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in INPUT_MARKERS)


def _unresolved_text(item: Any) -> str:
    if isinstance(item, str):
        return item
    return json.dumps(item, sort_keys=True, default=str)


def locate_task_receipts(task_id: str, receipts_root: Path) -> tuple[Path, ...]:
    base = Path(receipts_root) / task_id
    if base.is_file():
        return (base,)
    if not base.exists():
        return ()
    return tuple(sorted(path for path in base.rglob("TASK_RECEIPT.json") if path.is_file()))


def _command_excused(command: Mapping[str, Any], unresolved: list[Any]) -> bool:
    return False


def _check_artifacts(entries: Any, receipt_path: Path, failures: list[CheckFailure]) -> None:
    if not isinstance(entries, list):
        _append(failures, FailureCode.SCHEMA, str(receipt_path), "artifact_manifest must be a list")
        return
    for index, entry in enumerate(entries):
        loc = f"{receipt_path}#artifact_manifest[{index}]"
        if not isinstance(entry, dict):
            _append(failures, FailureCode.SCHEMA, loc, "artifact entry must be an object")
            continue
        raw_path = entry.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            _append(failures, FailureCode.ARTIFACT_MISSING, loc, "artifact path missing")
            continue
        artifact = Path(raw_path)
        if not artifact.is_file():
            _append(failures, FailureCode.ARTIFACT_MISSING, raw_path, "artifact file does not exist")
            continue
        payload = artifact.read_bytes()
        actual = file_digest(artifact)
        declared = entry.get("sha256")
        if not _hex_digest(declared):
            _append(failures, FailureCode.ARTIFACT_HASH, raw_path, "artifact sha256 is not a lowercase digest")
        elif actual != declared:
            _append(failures, FailureCode.ARTIFACT_HASH, raw_path, "artifact sha256 does not match file bytes")
        declared_bytes = entry.get("bytes")
        if type(declared_bytes) is int and declared_bytes != len(payload):
            _append(failures, FailureCode.ARTIFACT_BYTES, raw_path, f"declared {declared_bytes} bytes, file has {len(payload)}")


def _check_commands(
    commands: Any,
    unresolved: list[Any],
    receipt_path: Path,
    disposition: str,
    failures: list[CheckFailure],
) -> None:
    if not isinstance(commands, list):
        _append(failures, FailureCode.SCHEMA, str(receipt_path), "command_results must be a list")
        return
    if disposition in SUCCESS_DISPOSITIONS and not commands:
        _append(failures, FailureCode.COMMAND_MISSING, str(receipt_path), "implemented receipt has no command_results")
        return
    for index, command in enumerate(commands):
        loc = f"{receipt_path}#command_results[{index}]"
        if not isinstance(command, dict):
            _append(failures, FailureCode.COMMAND_SHAPE, loc, "command result must be an object")
            continue
        argv = command.get("argv")
        if not isinstance(argv, list) or not argv:
            _append(failures, FailureCode.COMMAND_SHAPE, loc, "argv must be a nonempty list")
        if not isinstance(command.get("cwd"), str) or not command.get("cwd"):
            _append(failures, FailureCode.COMMAND_SHAPE, loc, "cwd must be a nonempty string")
        exit_code = command.get("exit_code")
        if type(exit_code) is not int:
            _append(failures, FailureCode.COMMAND_SHAPE, loc, "exit_code must be an int")
            continue
        seconds = command.get("seconds")
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds < 0:
            _append(failures, FailureCode.COMMAND_SHAPE, loc, "seconds must be a nonnegative number")
        if exit_code != 0:
            _append(
                failures,
                FailureCode.COMMAND_EXIT,
                loc,
                f"required command exit_code {exit_code} cannot be excused",
            )
        log_path = command.get("log_path")
        log_sha = command.get("log_sha256")
        if not isinstance(log_path, str) or not log_path:
            _append(failures, FailureCode.COMMAND_MISSING, loc, "required command log_path is missing")
            continue
        log_file = Path(log_path)
        if not log_file.is_file():
            _append(failures, FailureCode.ARTIFACT_MISSING, log_path, "command log_path does not exist")
        elif not _hex_digest(log_sha):
            _append(failures, FailureCode.ARTIFACT_HASH, loc, "command log_sha256 is not a lowercase digest")
        elif file_digest(log_file) != log_sha:
            _append(failures, FailureCode.ARTIFACT_HASH, log_path, "command log_sha256 does not match log bytes")


def _predecessor_digest(value: Any) -> str | None:
    if _hex_digest(value):
        return value
    if isinstance(value, dict) and _hex_digest(value.get("sha256")):
        return str(value["sha256"])
    return None


def _predecessor_path(value: Any) -> Path | None:
    if isinstance(value, dict) and isinstance(value.get("path"), str) and value["path"]:
        return Path(value["path"])
    return None


def _matching_receipt(task_id: str, expected: str, candidates: Iterable[Path]) -> Path | None:
    for candidate in candidates:
        if not candidate.is_file():
            continue
        if file_digest(candidate) != expected:
            continue
        document, failures = load_json_document(candidate)
        if failures or not isinstance(document, dict):
            continue
        if document.get("task_id") == task_id:
            return candidate
    return None


def _check_predecessors(
    receipt: Mapping[str, Any],
    spec: TaskSpec,
    receipt_path: Path,
    receipts_root: Path,
    failures: list[CheckFailure],
    graph: TaskGraph | None = None,
) -> None:
    declared = receipt.get("predecessor_receipts")
    if not isinstance(declared, dict):
        _append(failures, FailureCode.SCHEMA, str(receipt_path), "predecessor_receipts must be a mapping")
        return
    artifact_paths = []
    for entry in receipt.get("artifact_manifest") or []:
        if isinstance(entry, dict) and isinstance(entry.get("path"), str):
            artifact_paths.append(Path(entry["path"]))
    for dep in spec.dependencies:
        if dep not in declared:
            _append(
                failures,
                FailureCode.PREDECESSOR_MISSING,
                str(receipt_path),
                f"TASK_GRAPH dependency {dep} is absent from predecessor_receipts",
            )
            continue
        expected = _predecessor_digest(declared[dep])
        if expected is None:
            _append(
                failures,
                FailureCode.PREDECESSOR_HASH,
                str(receipt_path),
                f"predecessor_receipts[{dep}] is not a SHA-256 digest",
            )
            continue
        hinted = _predecessor_path(declared[dep])
        search = []
        if hinted is not None:
            search.append(hinted)
        search.extend(locate_task_receipts(dep, receipts_root))
        search.extend(artifact_paths)
        matched = _matching_receipt(dep, expected, search)
        if matched is not None and graph is not None:
            cache_key = (expected, graph.path, graph.assurance_version)
            cached = _VERIFY_CACHE.get(cache_key)
            if cached is None:
                _VERIFY_CACHE[cache_key] = VerificationResult(
                    "task",
                    False,
                    str(matched),
                    (CheckFailure(FailureCode.GRAPH_CYCLE, str(matched), f"cycle while verifying predecessor {dep}"),),
                )
                cached = verify_task_receipt(matched, graph=graph, receipts_root=receipts_root)
                _VERIFY_CACHE[cache_key] = cached
            if not cached.ok:
                _append(
                    failures,
                    FailureCode.PREDECESSOR_HASH,
                    str(matched),
                    f"predecessor {dep} receipt failed recursive verification",
                )
                failures.extend(cached.failures)
        if matched is None:
            found = [path for path in search if path.is_file()]
            if not found:
                _append(
                    failures,
                    FailureCode.PREDECESSOR_MISSING,
                    str(receipt_path),
                    f"predecessor {dep} file was not found for digest {expected}",
                )
            else:
                actual = file_digest(found[0])
                _append(
                    failures,
                    FailureCode.PREDECESSOR_HASH,
                    str(found[0]),
                    f"predecessor {dep} digest {actual} does not match declared {expected}",
                )
            continue
        if file_digest(matched) != expected:
            _append(
                failures,
                FailureCode.PREDECESSOR_HASH,
                str(matched),
                f"predecessor {dep} file bytes do not match declared digest",
            )


def _manifest_by_name(entries: Any) -> dict[str, dict[str, Any]]:
    named: dict[str, dict[str, Any]] = {}
    if not isinstance(entries, list):
        return named
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get("path"), str):
            named[Path(entry["path"]).name] = entry
    return named


def _count_rows(document: Any) -> int | None:
    if isinstance(document, list):
        return len(document)
    if not isinstance(document, dict):
        return None
    if isinstance(document.get("checks"), list):
        return len(document["checks"])
    if isinstance(document.get("cases"), list):
        return len(document["cases"])
    if isinstance(document.get("classified_dates"), list):
        return len(document["classified_dates"])
    units = document.get("units")
    if isinstance(units, dict) and isinstance(units.get("units"), list):
        return len(units["units"])
    if isinstance(units, list):
        return len(units)
    if isinstance(document.get("coverage_rows"), list):
        return len(document["coverage_rows"])
    return None


def required_matrix_ids(spec: TaskSpec) -> tuple[str, ...]:
    return tuple(spec.required_acceptance_keys) + tuple(spec.assurance_cases)


def _check_evidence_matrix(
    receipt: Mapping[str, Any],
    spec: TaskSpec,
    receipt_path: Path,
    failures: list[CheckFailure],
) -> None:
    named = _manifest_by_name(receipt.get("artifact_manifest"))
    entry = named.get("EVIDENCE_MATRIX.json")
    if entry is None:
        return
    path = Path(entry["path"])
    if not path.is_file():
        return
    document, parse_failures = load_json_document(path)
    failures.extend(parse_failures)
    if not isinstance(document, dict):
        if document is not None:
            _append(failures, FailureCode.SCHEMA, str(path), "EVIDENCE_MATRIX.json must be an object")
        return
    if document.get("schema_version") != SCHEMA_EVIDENCE_MATRIX:
        _append(failures, FailureCode.SCHEMA, str(path), "schema_version must be research-evidence-matrix-v2")
    if document.get("task_id") != receipt.get("task_id"):
        _append(failures, FailureCode.INVENTORY, str(path), "evidence matrix task_id does not match the receipt")
    if document.get("assurance_version") != ASSURANCE_VERSION:
        _append(failures, FailureCode.SCHEMA, str(path), "evidence matrix assurance_version is not current")
    checks = document.get("checks")
    if not isinstance(checks, list) or not checks:
        _append(failures, FailureCode.INVENTORY, str(path), "evidence matrix checks are missing")
        return
    ids = [item.get("id") for item in checks if isinstance(item, dict)]
    required = required_matrix_ids(spec)
    if required:
        missing = [item for item in required if item not in ids]
        extra = [item for item in ids if item not in required]
        if missing or extra:
            _append(
                failures,
                FailureCode.INVENTORY,
                str(path),
                f"evidence matrix ids mismatch missing={missing} extra={extra}",
            )
    if len(ids) != len(set(ids)):
        _append(failures, FailureCode.INVENTORY, str(path), "evidence matrix check ids are not unique")
    commands = receipt.get("command_results") if isinstance(receipt.get("command_results"), list) else []
    workspace = DEFAULT_ROOT
    for index, check in enumerate(checks):
        loc = f"{path}#checks[{index}]"
        if not isinstance(check, dict):
            _append(failures, FailureCode.SCHEMA, loc, "check must be an object")
            continue
        absent = [field for field in MATRIX_CHECK_FIELDS if field not in check]
        if absent:
            _append(failures, FailureCode.INVENTORY, loc, f"check missing fields: {absent}")
        if check.get("status") not in EVIDENCE_STATUSES:
            _append(failures, FailureCode.SCHEMA, loc, "check status is not supported")
        refs = check.get("code_refs")
        if not isinstance(refs, list):
            _append(failures, FailureCode.INVENTORY, loc, "code_refs must be a list")
        else:
            for ref in refs:
                if not isinstance(ref, dict) or not ref.get("path") or not ref.get("symbol"):
                    _append(failures, FailureCode.INVENTORY, loc, "code_ref needs path and symbol")
                    continue
                code_path = workspace / str(ref["path"])
                if not code_path.is_file():
                    _append(failures, FailureCode.ARTIFACT_MISSING, str(code_path), "code_ref path does not exist")
        nodes = check.get("test_nodeids")
        if not isinstance(nodes, list) or any(not isinstance(item, str) or not item for item in nodes):
            _append(failures, FailureCode.INVENTORY, loc, "test_nodeids must be a list of strings")
        indices = check.get("command_indices")
        if not isinstance(indices, list) or any(type(item) is not int for item in indices):
            _append(failures, FailureCode.INVENTORY, loc, "command_indices must be a list of ints")
        else:
            for item in indices:
                if item < 0 or item >= len(commands):
                    _append(failures, FailureCode.INVENTORY, loc, f"command index {item} is not an executed command")
        evidence = check.get("evidence")
        if not isinstance(evidence, list):
            _append(failures, FailureCode.INVENTORY, loc, "evidence must be a list")
            continue
        if check.get("status") == "pass" and not evidence:
            _append(failures, FailureCode.INVENTORY, loc, "passing check has no evidence")
        for item in evidence:
            if not isinstance(item, dict):
                _append(failures, FailureCode.INVENTORY, loc, "evidence item must be an object")
                continue
            if not isinstance(item.get("selector"), str) or not item.get("selector"):
                _append(failures, FailureCode.INVENTORY, loc, "evidence selector is missing")
            raw_path = item.get("path")
            digest_value = item.get("sha256")
            if not isinstance(raw_path, str) or not raw_path:
                _append(failures, FailureCode.ARTIFACT_MISSING, loc, "evidence path is missing")
                continue
            evidence_path = Path(raw_path)
            if not evidence_path.is_file():
                evidence_path = workspace / raw_path
            if not evidence_path.is_file():
                _append(failures, FailureCode.ARTIFACT_MISSING, raw_path, "evidence file does not exist")
                continue
            if not _hex_digest(digest_value):
                _append(failures, FailureCode.ARTIFACT_HASH, raw_path, "evidence sha256 is not a lowercase digest")
            elif file_digest(evidence_path) != digest_value:
                _append(failures, FailureCode.ARTIFACT_HASH, raw_path, "evidence sha256 does not match file bytes")


def _check_inventory(receipt: Mapping[str, Any], spec: TaskSpec, graph: TaskGraph, receipt_path: Path, failures: list[CheckFailure]) -> None:
    entries = receipt.get("artifact_manifest")
    if not isinstance(entries, list) or not entries:
        _append(failures, FailureCode.INVENTORY, str(receipt_path), "artifact_manifest is empty")
        return
    named = _manifest_by_name(entries)
    required = list(graph.required_task_artifacts) + list(spec.artifacts)
    missing = [name for name in required if name not in named]
    if missing:
        _append(failures, FailureCode.INVENTORY, str(receipt_path), f"required artifacts missing: {missing}")
    for name, entry in named.items():
        path = Path(entry["path"])
        if path.is_dir():
            index = entry.get("directory_index")
            if not isinstance(index, list) or not index:
                _append(failures, FailureCode.INVENTORY, str(path), "directory artifact needs a hashed file index")
            continue
        if not path.is_file():
            continue
        schema = entry.get("schema")
        if name.endswith(".json") and path.is_file():
            document, parse_failures = load_json_document(path)
            if parse_failures:
                failures.extend(parse_failures)
                continue
            if isinstance(document, dict) and isinstance(schema, str) and schema.startswith("research-") and document.get("schema") not in {schema, None} and document.get("schema_version") not in {schema, None}:
                if document.get("schema_version") != schema and document.get("schema") != schema:
                    _append(failures, FailureCode.SCHEMA, str(path), f"parsed schema {document.get('schema_version') or document.get('schema')} != declared {schema}")
            declared_rows = entry.get("rows")
            if type(declared_rows) is int:
                counted = _count_rows(document)
                if counted is not None and counted != declared_rows:
                    _append(
                        failures,
                        FailureCode.INVENTORY,
                        str(path),
                        f"declared {declared_rows} rows, parsed {counted}",
                    )


def _check_identities(receipt: Mapping[str, Any], receipt_path: Path, graph: TaskGraph, failures: list[CheckFailure]) -> None:
    named = _manifest_by_name(receipt.get("artifact_manifest"))
    plan_entry = named.get("PLAN_SNAPSHOT.json")
    code_entry = named.get("CODE_SNAPSHOT.json")
    draft_entry = named.get("DRAFT_MANIFEST.json")
    required = set(graph.required_task_artifacts)
    if plan_entry is None or code_entry is None or draft_entry is None:
        if {"PLAN_SNAPSHOT.json", "CODE_SNAPSHOT.json", "DRAFT_MANIFEST.json"} & required:
            _append(failures, FailureCode.IDENTITY, str(receipt_path), "PLAN_SNAPSHOT, CODE_SNAPSHOT and DRAFT_MANIFEST are required identity bindings")
        return
    plan_doc, plan_fail = load_json_document(Path(plan_entry["path"]))
    code_doc, code_fail = load_json_document(Path(code_entry["path"]))
    draft_doc, draft_fail = load_json_document(Path(draft_entry["path"]))
    failures.extend(plan_fail)
    failures.extend(code_fail)
    failures.extend(draft_fail)
    if not isinstance(plan_doc, dict) or not isinstance(code_doc, dict) or not isinstance(draft_doc, dict):
        return
    files = plan_doc.get("files")
    if not isinstance(files, dict):
        _append(failures, FailureCode.IDENTITY, plan_entry["path"], "PLAN_SNAPSHOT.files must be a mapping")
    else:
        recomputed = digest(files)
        if recomputed != receipt.get("plan_sha256"):
            _append(failures, FailureCode.IDENTITY, str(receipt_path), "plan_sha256 does not recompute from PLAN_SNAPSHOT.files")
        copies = plan_doc.get("snapshot_paths")
        if isinstance(copies, dict):
            root = Path(plan_entry["path"]).parent
            for rel, copy_rel in copies.items():
                copy_path = root / str(copy_rel)
                if not copy_path.is_file():
                    _append(failures, FailureCode.ARTIFACT_MISSING, str(copy_path), f"plan snapshot copy missing for {rel}")
                elif files.get(rel) and file_digest(copy_path) != files[rel]:
                    _append(failures, FailureCode.ARTIFACT_HASH, str(copy_path), f"plan snapshot copy hash mismatch for {rel}")
    recomputed_code = digest(code_doc)
    if recomputed_code != receipt.get("code_sha256"):
        _append(failures, FailureCode.IDENTITY, str(receipt_path), "code_sha256 does not recompute from CODE_SNAPSHOT")
    if digest(draft_doc)[:16] != receipt.get("run_id"):
        _append(failures, FailureCode.IDENTITY, str(receipt_path), "run_id does not recompute from DRAFT_MANIFEST")
    if draft_doc.get("plan_sha256") != receipt.get("plan_sha256"):
        _append(failures, FailureCode.IDENTITY, str(receipt_path), "draft plan_sha256 does not match receipt")
    if draft_doc.get("code_sha256") != receipt.get("code_sha256"):
        _append(failures, FailureCode.IDENTITY, str(receipt_path), "draft code_sha256 does not match receipt")
    if draft_doc.get("task_id") != receipt.get("task_id"):
        _append(failures, FailureCode.IDENTITY, str(receipt_path), "draft task_id does not match receipt")
    if draft_doc.get("assurance_version") != receipt.get("assurance_version"):
        _append(failures, FailureCode.IDENTITY, str(receipt_path), "draft assurance_version does not match receipt")
    draft_pred = draft_doc.get("predecessor_receipts")
    if draft_pred != receipt.get("predecessor_receipts"):
        _append(failures, FailureCode.IDENTITY, str(receipt_path), "draft predecessor_receipts do not match receipt")


_VERIFY_CACHE: dict[tuple[str, str, str], VerificationResult] = {}


def verify_task_receipt(
    receipt_path: Path,
    *,
    graph: TaskGraph | None = None,
    graph_path: Path | None = None,
    receipts_root: Path | None = None,
) -> VerificationResult:
    path = Path(receipt_path)
    failures: list[CheckFailure] = []
    document, parse_failures = load_json_document(path)
    failures.extend(parse_failures)
    loaded_graph = graph
    graph_failures: tuple[CheckFailure, ...] = ()
    if loaded_graph is None:
        loaded_graph, graph_failures = load_task_graph(graph_path)
        failures.extend(graph_failures)
    if document is None or loaded_graph is None:
        return VerificationResult("task", False, str(path), tuple(failures))
    if not isinstance(document, dict):
        _append(failures, FailureCode.SCHEMA, str(path), "task receipt must be a JSON object")
        return VerificationResult("task", False, str(path), tuple(failures))
    try:
        receipt = validate_receipt_shape(document)
    except ContractError as exc:
        _append(failures, FailureCode.SCHEMA, str(path), str(exc))
        return VerificationResult("task", False, str(path), tuple(failures))
    task_id = receipt["task_id"]
    spec = loaded_graph.require(task_id)
    if spec is None:
        _append(failures, FailureCode.UNKNOWN_TASK, str(path), f"{task_id} is not in TASK_GRAPH")
        return VerificationResult("task", False, str(path), tuple(failures))
    checks = receipt["acceptance_checks"]
    for key in spec.required_acceptance_keys:
        if key not in checks:
            _append(failures, FailureCode.ACCEPTANCE, str(path), f"required acceptance key {key} is missing")
        elif checks[key] is not True:
            _append(failures, FailureCode.ACCEPTANCE, str(path), f"required acceptance key {key} is not true")
    if receipt["disposition"] not in spec.allowed_terminal_statuses:
        _append(
            failures,
            FailureCode.DISPOSITION,
            str(path),
            f"disposition {receipt['disposition']} is not allowed for {task_id}",
        )
    if receipt["disposition"] == "blocked_implementation":
        _append(failures, FailureCode.BLOCKED_IMPLEMENTATION, str(path), "blocked_implementation is not an accepted terminal")
    if not isinstance(receipt["coverage"], dict):
        _append(failures, FailureCode.COVERAGE, str(path), "coverage must be an object")
    _check_artifacts(receipt["artifact_manifest"], path, failures)
    _check_inventory(receipt, spec, loaded_graph, path, failures)
    _check_identities(receipt, path, loaded_graph, failures)
    _check_evidence_matrix(receipt, spec, path, failures)
    unresolved = receipt["unresolved"] if isinstance(receipt["unresolved"], list) else []
    _check_commands(receipt["command_results"], unresolved, path, receipt["disposition"], failures)
    _check_predecessors(
        receipt,
        spec,
        path,
        Path(receipts_root) if receipts_root is not None else DEFAULT_RECEIPTS_ROOT,
        failures,
        graph=loaded_graph,
    )
    return VerificationResult("task", not failures, str(path), tuple(failures))


def _parse_task_ref(task_id: str, raw: Any, receipt_path: Path, failures: list[CheckFailure], *, want_disposition: bool) -> TaskRef | None:
    if not isinstance(raw, dict):
        _append(failures, FailureCode.SCHEMA, str(receipt_path), f"task_receipts[{task_id}] must be an object")
        return None
    path = raw.get("path")
    digest = raw.get("sha256")
    if not isinstance(path, str) or not path:
        _append(failures, FailureCode.MISSING_KEY, str(receipt_path), f"task_receipts[{task_id}].path missing")
        path = ""
    if not _hex_digest(digest):
        _append(failures, FailureCode.ARTIFACT_HASH, str(receipt_path), f"task_receipts[{task_id}].sha256 is not a digest")
        digest = digest if isinstance(digest, str) else ""
    disposition = raw.get("disposition")
    if want_disposition and disposition is not None and disposition not in DISPOSITIONS:
        _append(failures, FailureCode.DISPOSITION, str(receipt_path), f"task_receipts[{task_id}] has unknown disposition")
    return TaskRef(task_id=task_id, path=path, sha256=str(digest), disposition=disposition if isinstance(disposition, str) else None)


def _hash_task_ref(ref: TaskRef, failures: list[CheckFailure]) -> None:
    if not ref.path:
        return
    path = Path(ref.path)
    if not path.is_file():
        _append(failures, FailureCode.ARTIFACT_MISSING, ref.path, f"task receipt file for {ref.task_id} does not exist")
        return
    actual = file_digest(path)
    if _hex_digest(ref.sha256) and actual != ref.sha256:
        _append(failures, FailureCode.ARTIFACT_HASH, ref.path, f"{ref.task_id} receipt digest {actual} != declared {ref.sha256}")


def _gate_for_missing_software(gate: str, receipt_path: str, detail: str, failures: list[CheckFailure]) -> None:
    _append(failures, FailureCode.SOFTWARE_MISSING, receipt_path, detail)
    if gate == "closed_with_limits":
        _append(
            failures,
            FailureCode.GATE,
            receipt_path,
            "closed_with_limits cannot excuse missing software checks",
        )
    elif gate == "pass":
        _append(failures, FailureCode.GATE, receipt_path, "pass is inconsistent with missing software")


def verify_gate_review(review_path: Path, candidate_path: Path, candidate_hash: str, graph: TaskGraph) -> tuple[CheckFailure, ...]:
    failures: list[CheckFailure] = []
    document, parse_failures = load_json_document(review_path)
    failures.extend(parse_failures)
    if not isinstance(document, dict):
        return tuple(failures)
    if document.get("schema_version") != SCHEMA_GATE_REVIEW:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "schema_version must be research-gate-review-v2")
    if document.get("assurance_version") != ASSURANCE_VERSION:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review assurance_version is not current")
    if document.get("verdict") != "pass":
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review verdict is not pass")
    candidate = document.get("candidate") if isinstance(document.get("candidate"), dict) else {}
    if candidate.get("path") != str(candidate_path) or candidate.get("sha256") != candidate_hash:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review candidate does not match the receipt under verification")
    reviewed = document.get("reviewed_task_ids")
    expected_tasks = [spec.id for spec in graph.for_subphase(str(document.get("subphase_id") or ""))]
    if not expected_tasks:
        expected_tasks = [spec.id for spec in graph.for_phase(str(document.get("phase") or ""))]
    if isinstance(reviewed, list):
        if expected_tasks and set(reviewed) != set(expected_tasks):
            _append(failures, FailureCode.GATE_REVIEW, str(review_path), "reviewed_task_ids do not match the candidate task set")
    else:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "reviewed_task_ids is missing")
    findings = document.get("findings") if isinstance(document.get("findings"), list) else []
    open_findings = [item for item in findings if isinstance(item, dict) and item.get("resolution") not in {"resolved", "accepted-limit"}]
    if open_findings:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review has unresolved findings")
    independent = document.get("independent_suite") if isinstance(document.get("independent_suite"), dict) else {}
    if independent.get("checker_sha256") != PINNED_CHECKER_SHA256:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "independent checker hash is not the pinned suite")
    results_path = independent.get("results_path")
    if isinstance(results_path, str) and Path(results_path).is_file():
        results, result_fail = load_json_document(Path(results_path))
        failures.extend(result_fail)
        if isinstance(results, dict):
            cases = results.get("cases") if isinstance(results.get("cases"), list) else []
            if (
                len(cases) != PINNED_CHECKER_CASES
                or results.get("status") != "pass"
                or results.get("harness_sha256") not in {None, PINNED_CHECKER_SHA256}
                or not all(row.get("passed") for row in cases if isinstance(row, dict))
            ):
                _append(failures, FailureCode.GATE_REVIEW, results_path, "independent suite did not pass all pinned cases")
            inputs = results.get("input_hashes") if isinstance(results.get("input_hashes"), dict) else {}
            if candidate_hash not in inputs.values():
                _append(failures, FailureCode.GATE_REVIEW, results_path, "independent results do not bind this candidate receipt")
            if file_digest(Path(graph.path)) not in inputs.values():
                _append(failures, FailureCode.GATE_REVIEW, results_path, "independent results do not bind the current graph")
    else:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "independent suite results path is missing")
    return tuple(failures)


def verify_subphase_receipt(
    receipt_path: Path,
    *,
    graph: TaskGraph | None = None,
    graph_path: Path | None = None,
    receipts_root: Path | None = None,
    gate_review: Path | None = None,
) -> VerificationResult:
    path = Path(receipt_path)
    failures: list[CheckFailure] = []
    document, parse_failures = load_json_document(path)
    failures.extend(parse_failures)
    loaded_graph = graph
    if loaded_graph is None:
        loaded_graph, graph_failures = load_task_graph(graph_path)
        failures.extend(graph_failures)
    if document is None or loaded_graph is None:
        return VerificationResult("subphase", False, str(path), tuple(failures))
    if not isinstance(document, dict):
        _append(failures, FailureCode.SCHEMA, str(path), "subphase receipt must be a JSON object")
        return VerificationResult("subphase", False, str(path), tuple(failures))
    missing = [key for key in _SUBPHASE_KEYS if key not in document]
    if missing:
        _append(failures, FailureCode.MISSING_KEY, str(path), f"missing keys: {missing}")
    if document.get("schema_version") != SCHEMA_SUBPHASE_RECEIPT:
        _append(failures, FailureCode.SCHEMA, str(path), "schema_version must be research-subphase-receipt-v2")
    if not isinstance(document.get("subphase_id"), str) or not document.get("subphase_id"):
        _append(failures, FailureCode.SCHEMA, str(path), "subphase_id must be nonempty")
        return VerificationResult("subphase", False, str(path), tuple(failures))
    if document.get("subphase_id") not in loaded_graph.known_subphases():
        _append(failures, FailureCode.UNKNOWN_SUBPHASE, str(path), f"unknown subphase {document.get('subphase_id')}")
        return VerificationResult("subphase", False, str(path), tuple(failures))
    if not _run_id(document.get("run_id")):
        _append(failures, FailureCode.SCHEMA, str(path), "run_id must be 16 lowercase hex characters")
    if document.get("gate") not in GATES:
        _append(failures, FailureCode.GATE, str(path), "gate must be pass, closed_with_limits, or fail")
    if not isinstance(document.get("accepted_schema_versions"), list):
        _append(failures, FailureCode.SCHEMA, str(path), "accepted_schema_versions must be a list")
    if not isinstance(document.get("native_slice_ids"), list):
        _append(failures, FailureCode.SCHEMA, str(path), "native_slice_ids must be a list")
    if not isinstance(document.get("test_evidence"), list):
        _append(failures, FailureCode.SCHEMA, str(path), "test_evidence must be a list")
    if not isinstance(document.get("coverage"), dict):
        _append(failures, FailureCode.COVERAGE, str(path), "coverage must be an object")
    if not isinstance(document.get("single_writer_audit"), dict):
        _append(failures, FailureCode.SCHEMA, str(path), "single_writer_audit must be an object")
    if not isinstance(document.get("unresolved"), list):
        _append(failures, FailureCode.SCHEMA, str(path), "unresolved must be a list")
    if not isinstance(document.get("reason"), str) or not document.get("reason"):
        _append(failures, FailureCode.SCHEMA, str(path), "reason must be nonempty")
    if document.get("assurance_version") != ASSURANCE_VERSION:
        _append(failures, FailureCode.SCHEMA, str(path), "subphase assurance_version is not current")
    raw_refs = document.get("task_receipts")
    refs: dict[str, TaskRef] = {}
    if not isinstance(raw_refs, dict):
        _append(failures, FailureCode.SCHEMA, str(path), "task_receipts must be an object")
    else:
        for task_id, raw in raw_refs.items():
            parsed = _parse_task_ref(str(task_id), raw, path, failures, want_disposition=False)
            if parsed is not None:
                refs[parsed.task_id] = parsed
                _hash_task_ref(parsed, failures)
                if parsed.path and Path(parsed.path).is_file():
                    child_doc, child_parse = load_json_document(Path(parsed.path))
                    if not child_parse and isinstance(child_doc, dict) and child_doc.get("task_id") != parsed.task_id:
                        _append(
                            failures,
                            FailureCode.TASK_MISMATCH,
                            parsed.path,
                            f"task_receipts[{parsed.task_id}] points to task_id {child_doc.get('task_id')}",
                        )
    required = loaded_graph.for_subphase(str(document.get("subphase_id")))
    gate = document.get("gate") if document.get("gate") in GATES else "fail"
    missing_tasks = [spec.id for spec in required if spec.id not in refs]
    if missing_tasks:
        _append(failures, FailureCode.TASK_MISSING, str(path), f"missing required tasks: {missing_tasks}")
        _gate_for_missing_software(gate, str(path), f"required tasks absent: {missing_tasks}", failures)
    root = Path(receipts_root) if receipts_root is not None else DEFAULT_RECEIPTS_ROOT
    blocked = False
    disallowed = False
    for spec in required:
        ref = refs.get(spec.id)
        if ref is None or not Path(ref.path).is_file():
            continue
        child = verify_task_receipt(Path(ref.path), graph=loaded_graph, receipts_root=root)
        if not child.ok:
            failures.extend(child.failures)
        child_doc, child_parse = load_json_document(Path(ref.path))
        if child_parse or not isinstance(child_doc, dict):
            continue
        disposition = child_doc.get("disposition")
        if disposition == "blocked_implementation":
            blocked = True
            _append(failures, FailureCode.BLOCKED_IMPLEMENTATION, ref.path, f"{spec.id} is blocked_implementation")
        if disposition not in spec.allowed_terminal_statuses:
            disallowed = True
            _append(failures, FailureCode.DISPOSITION, ref.path, f"{spec.id} disposition is not an allowed terminal")
    if blocked or disallowed:
        _gate_for_missing_software(gate, str(path), "a required task is blocked or not an allowed terminal", failures)
    unresolved = document.get("unresolved") if isinstance(document.get("unresolved"), list) else []
    if gate == "closed_with_limits":
        for item in unresolved:
            text = _unresolved_text(item)
            if _is_software_limit(text) and not _is_input_limit(text):
                _append(
                    failures,
                    FailureCode.SOFTWARE_MISSING,
                    str(path),
                    f"closed_with_limits unresolved item is a software gap: {text}",
                )
        if not unresolved and not missing_tasks and not blocked:
            pass
    evidence = document.get("test_evidence") if isinstance(document.get("test_evidence"), list) else []
    _check_commands(evidence, unresolved, path, "implemented_verified" if evidence else "blocked_implementation", failures)
    if gate == "fail" and not (missing_tasks or blocked or disallowed or any(item.code != FailureCode.GATE for item in failures)):
        _append(failures, FailureCode.GATE, str(path), "gate=fail without a recorded task or software failure")
    if gate_review is not None:
        failures.extend(verify_gate_review(Path(gate_review), path, file_digest(path), loaded_graph))
    return VerificationResult("subphase", not failures, str(path), tuple(failures))


def verify_phase_receipt(
    receipt_path: Path,
    *,
    graph: TaskGraph | None = None,
    graph_path: Path | None = None,
    receipts_root: Path | None = None,
    gate_review: Path | None = None,
) -> VerificationResult:
    path = Path(receipt_path)
    failures: list[CheckFailure] = []
    document, parse_failures = load_json_document(path)
    failures.extend(parse_failures)
    loaded_graph = graph
    if loaded_graph is None:
        loaded_graph, graph_failures = load_task_graph(graph_path)
        failures.extend(graph_failures)
    if document is None or loaded_graph is None:
        return VerificationResult("phase", False, str(path), tuple(failures))
    if not isinstance(document, dict):
        _append(failures, FailureCode.SCHEMA, str(path), "phase receipt must be a JSON object")
        return VerificationResult("phase", False, str(path), tuple(failures))
    missing = [key for key in _PHASE_KEYS if key not in document]
    if missing:
        _append(failures, FailureCode.MISSING_KEY, str(path), f"missing keys: {missing}")
    if document.get("schema_version") != SCHEMA_PHASE_RECEIPT:
        _append(failures, FailureCode.SCHEMA, str(path), "schema_version must be research-phase-receipt-v2")
    phase = document.get("phase")
    if phase not in PHASES:
        _append(failures, FailureCode.SCHEMA, str(path), "phase must be phase-1-5 or phase-2")
        return VerificationResult("phase", False, str(path), tuple(failures))
    gate = document.get("gate")
    if gate not in GATES:
        _append(failures, FailureCode.GATE, str(path), "gate must be pass, closed_with_limits, or fail")
        gate = "fail"
    phase_gate = document.get("phase_1_5_gate")
    if phase_gate not in PHASE_1_5_GATES:
        _append(failures, FailureCode.PHASE_1_5_GATE, str(path), "phase_1_5_gate must be pass, closed_with_limits, fail, or missing")
        phase_gate = "missing"
    if phase == "phase-2":
        release = document.get("phase_1_5_release")
        if not isinstance(release, dict) or not isinstance(release.get("path"), str) or not _hex_digest(release.get("sha256")):
            _append(
                failures,
                FailureCode.PHASE_1_5_GATE,
                str(path),
                "phase-2 receipts require an actual Phase 1.5 release path/hash",
            )
        else:
            release_path = Path(release["path"])
            if not release_path.is_file() or file_digest(release_path) != release["sha256"]:
                _append(failures, FailureCode.PHASE_1_5_GATE, str(release_path), "Phase 1.5 release hash does not match")
            else:
                nested = verify_phase_receipt(release_path, graph=loaded_graph)
                if not nested.ok:
                    _append(failures, FailureCode.PHASE_1_5_GATE, str(release_path), "Phase 1.5 release failed recursive verification")
                    failures.extend(nested.failures)
        if phase_gate not in {"pass", "closed_with_limits"}:
            _append(
                failures,
                FailureCode.PHASE_1_5_GATE,
                str(path),
                "phase-2 receipts require phase_1_5_gate in {pass, closed_with_limits}",
            )
    raw_refs = document.get("task_receipts")
    refs: dict[str, TaskRef] = {}
    if not isinstance(raw_refs, dict):
        _append(failures, FailureCode.SCHEMA, str(path), "task_receipts must be an object")
    else:
        for task_id, raw in raw_refs.items():
            parsed = _parse_task_ref(str(task_id), raw, path, failures, want_disposition=True)
            if parsed is not None:
                refs[parsed.task_id] = parsed
                _hash_task_ref(parsed, failures)
                if parsed.path and Path(parsed.path).is_file():
                    child_doc, child_parse = load_json_document(Path(parsed.path))
                    if not child_parse and isinstance(child_doc, dict):
                        if child_doc.get("task_id") != parsed.task_id:
                            _append(
                                failures,
                                FailureCode.TASK_MISMATCH,
                                parsed.path,
                                f"task_receipts[{parsed.task_id}] points to task_id {child_doc.get('task_id')}",
                            )
                        else:
                            nested = verify_task_receipt(
                                Path(parsed.path),
                                graph=loaded_graph,
                                receipts_root=Path(receipts_root) if receipts_root is not None else DEFAULT_RECEIPTS_ROOT,
                            )
                            if not nested.ok:
                                failures.extend(nested.failures)
    required = loaded_graph.for_phase(phase)
    missing_tasks = [spec.id for spec in required if spec.id not in refs]
    if missing_tasks:
        _append(failures, FailureCode.TASK_MISSING, str(path), f"missing phase tasks: {missing_tasks}")
        _gate_for_missing_software(gate, str(path), f"phase tasks absent: {missing_tasks}", failures)
    blocked = False
    for spec in required:
        ref = refs.get(spec.id)
        if ref is None:
            continue
        disposition = ref.disposition
        if disposition is None and ref.path and Path(ref.path).is_file():
            child_doc, child_parse = load_json_document(Path(ref.path))
            if not child_parse and isinstance(child_doc, dict):
                disposition = child_doc.get("disposition") if isinstance(child_doc.get("disposition"), str) else None
        if disposition == "blocked_implementation":
            blocked = True
            _append(failures, FailureCode.BLOCKED_IMPLEMENTATION, ref.path or str(path), f"{spec.id} is blocked_implementation")
        elif disposition is not None and disposition not in spec.allowed_terminal_statuses:
            _append(failures, FailureCode.DISPOSITION, ref.path or str(path), f"{spec.id} disposition is not an allowed terminal")
            if gate in {"pass", "closed_with_limits"}:
                _append(failures, FailureCode.GATE, str(path), f"{spec.id} is not an allowed terminal for a passing phase gate")
    if blocked and gate in {"pass", "closed_with_limits"}:
        _append(failures, FailureCode.GATE, str(path), "blocked_implementation never passes a phase gate")
        _append(
            failures,
            FailureCode.SOFTWARE_MISSING,
            str(path),
            "scoped input limitations cannot excuse blocked_implementation",
        )
    if gate == "fail":
        _append(failures, FailureCode.GATE, str(path), "phase gate is fail")
    if gate_review is not None:
        failures.extend(verify_gate_review(Path(gate_review), path, file_digest(path), loaded_graph))
    return VerificationResult("phase", not failures, str(path), tuple(failures))


def _clocks_of(record: Mapping[str, Any]) -> tuple[int | None, int | None, int | None]:
    def as_ns(name: str) -> int | None:
        value = record.get(name)
        return value if type(value) is int else None

    return as_ns("available_at_ns"), as_ns("issue_at_ns"), as_ns("decision_at_ns")


def _walk_lineage(
    node: Any,
    *,
    ancestor_issues: tuple[int, ...],
    ancestor_decisions: tuple[int, ...],
    manifest_path: Path,
    failures: list[CheckFailure],
    trail: str,
) -> None:
    if isinstance(node, list):
        for index, item in enumerate(node):
            _walk_lineage(
                item,
                ancestor_issues=ancestor_issues,
                ancestor_decisions=ancestor_decisions,
                manifest_path=manifest_path,
                failures=failures,
                trail=f"{trail}[{index}]",
            )
        return
    if not isinstance(node, dict):
        return
    loc = f"{manifest_path}#{trail}"
    for name in ("available_at_ns", "issue_at_ns", "decision_at_ns", "event_at_ns"):
        if name in node and type(node[name]) is not int:
            _append(failures, FailureCode.LINEAGE_CLOCK, loc, f"{name} must be an int nanosecond clock")
    available_at_ns, local_issue, local_decision = _clocks_of(node)
    issues = ancestor_issues + ((local_issue,) if local_issue is not None else ())
    decisions = ancestor_decisions + ((local_decision,) if local_decision is not None else ())
    if available_at_ns is not None:
        for cutoff in issues + decisions:
            if available_at_ns > cutoff:
                _append(
                    failures,
                    FailureCode.LINEAGE_CLOCK,
                    loc,
                    f"available_at_ns {available_at_ns} exceeds ancestor cutoff {cutoff}",
                )
    digest_value = node.get("artifact_sha256") if _hex_digest(node.get("artifact_sha256")) else node.get("sha256")
    raw_path = node.get("artifact_path") or node.get("path")
    is_leaf = any(key in node for key in ("artifact_path", "artifact_sha256", "row_ids"))
    if is_leaf:
        if not _hex_digest(node.get("artifact_sha256")) and not _hex_digest(node.get("sha256")):
            _append(failures, FailureCode.LINEAGE_HASH, loc, "evidence leaf is missing artifact_sha256")
        if not isinstance(node.get("row_ids"), list) or not node.get("row_ids"):
            _append(failures, FailureCode.LINEAGE_HASH, loc, "evidence leaf is missing row_ids")
    if isinstance(raw_path, str) and raw_path:
        file_path = Path(raw_path)
        if not file_path.is_file():
            _append(failures, FailureCode.ARTIFACT_MISSING, raw_path, "lineage artifact does not exist")
        elif _hex_digest(digest_value) and file_digest(file_path) != digest_value:
            _append(failures, FailureCode.LINEAGE_HASH, raw_path, "lineage sha256 does not match file bytes")
        elif digest_value is not None and not _hex_digest(digest_value):
            _append(failures, FailureCode.LINEAGE_HASH, loc, "lineage sha256 is not a lowercase digest")
    for key, value in node.items():
        if key in {"path", "artifact_path", "sha256", "artifact_sha256"}:
            continue
        _walk_lineage(
            value,
            ancestor_issues=issues,
            ancestor_decisions=decisions,
            manifest_path=manifest_path,
            failures=failures,
            trail=f"{trail}.{key}",
        )


def verify_lineage_manifest(manifest_path: Path) -> VerificationResult:
    path = Path(manifest_path)
    failures: list[CheckFailure] = []
    document, parse_failures = load_json_document(path)
    failures.extend(parse_failures)
    if document is None:
        return VerificationResult("lineage", False, str(path), tuple(failures))
    if not isinstance(document, dict):
        _append(failures, FailureCode.SCHEMA, str(path), "lineage manifest must be a JSON object")
        return VerificationResult("lineage", False, str(path), tuple(failures))
    if document.get("schema_version") != SCHEMA_LINEAGE_MANIFEST:
        _append(failures, FailureCode.SCHEMA, str(path), "schema_version must be research-lineage-manifest-v1")
    records = document.get("records")
    if not isinstance(records, list):
        _append(failures, FailureCode.SCHEMA, str(path), "records must be a list")
        return VerificationResult("lineage", False, str(path), tuple(failures))
    _walk_lineage(
        records,
        ancestor_issues=(),
        ancestor_decisions=(),
        manifest_path=path,
        failures=failures,
        trail="records",
    )
    return VerificationResult("lineage", not failures, str(path), tuple(failures))


def dumps_result(result: VerificationResult) -> str:
    return json.dumps(result.payload(), sort_keys=True, indent=2, ensure_ascii=False) + "\n"


P15_01_PLAN_PATHS = (
    "planning/phase-1-5/tasks/P15-01.md",
    "AGENTS.md",
    "planning/ROADMAP.md",
    "planning/research-program/PSTACK_EXECUTION.md",
    "planning/research-program/WORKFLOW.md",
    "planning/research-program/DATA_CONTRACTS.md",
    "planning/research-program/ASSURANCE.md",
    "planning/research-program/SILENT_FAILURES.md",
    "planning/research-program/TASK_GRAPH.json",
    "planning/research-program/ASSURANCE_CASES.json",
)
P15_01_CODE_PATHS = (
    "implementation/src/trading_research/research/contracts/receipts.py",
    "implementation/tools/verify_research_release.py",
    "implementation/tests/rule_discovery/test_p15_01.py",
    "implementation/src/trading_research/research/contracts/identity.py",
    "implementation/src/trading_research/research/contracts/types.py",
    "implementation/src/trading_research/errors.py",
    "implementation/pyproject.toml",
)
SUPERSEDED_P15_01 = {
    "path": "implementation/reports/research-work/P15-01/039267553e8bf721/attempt-0001/TASK_RECEIPT.json",
    "sha256": "549429da5d43ff6fc347723fe4f4c8eda4550b31190bb94324ab82e2afba2c4f",
}


def draft_p15_01_manifest(
    *,
    plan_sha256: str,
    code_sha256: str,
    predecessor_receipts: Mapping[str, str],
    input_identities: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "research-draft-manifest-v2",
        "task_id": "P15-01",
        "assurance_version": ASSURANCE_VERSION,
        "plan_sha256": plan_sha256,
        "code_sha256": code_sha256,
        "predecessor_receipts": dict(predecessor_receipts),
        "input_identities": dict(input_identities),
        "coverage_identity": None,
        "registered_candidate_config": None,
        "declared_study_dates": None,
    }


def write_p15_01_artifacts(
    run_root: Path,
    *,
    predecessor_receipt: Path,
) -> dict[str, Any]:
    import sys
    root = DEFAULT_ROOT
    predecessor_receipt = Path(predecessor_receipt)
    predecessor_hash = file_digest(predecessor_receipt)
    plan_files = {rel: file_digest(root / rel) for rel in P15_01_PLAN_PATHS}
    code_files = {rel: file_digest(root / rel) for rel in P15_01_CODE_PATHS}
    attempt = Path(run_root)
    attempt.mkdir(parents=True, exist_ok=True)
    plan_copies = write_snapshot_tree(attempt, "plan", plan_files, root=root)
    code_copies = write_snapshot_tree(attempt, "code", code_files, root=root)
    plan_doc = plan_snapshot_document(plan_files, plan_copies)
    lock = root / "implementation/uv.lock"
    lock_sha = file_digest(lock) if lock.is_file() else file_digest(root / "implementation/pyproject.toml")
    code_doc = code_snapshot_document(
        code_files,
        code_copies,
        runtime={"python": sys.version.split()[0]},
        dependency_lock_sha256=lock_sha,
        imported_modules=[
            "trading_research.errors",
            "trading_research.research.contracts.identity",
            "trading_research.research.contracts.types",
            "trading_research.research.contracts.receipts",
        ],
    )
    plan_sha256 = digest(plan_files)
    code_sha256 = digest(code_doc)
    draft = draft_p15_01_manifest(
        plan_sha256=plan_sha256,
        code_sha256=code_sha256,
        predecessor_receipts={"P15-00": predecessor_hash},
        input_identities={
            "P15-00": {"path": str(predecessor_receipt), "sha256": predecessor_hash},
        },
    )
    run_id = semantic_run_id(draft)
    write_json_document(attempt / "PLAN_SNAPSHOT.json", plan_doc)
    write_json_document(attempt / "CODE_SNAPSHOT.json", code_doc)
    write_json_document(attempt / "DRAFT_MANIFEST.json", draft)
    snapshot = {
        "schema": "research-worktree-snapshot-v1",
        "owned_paths": list(P15_01_CODE_PATHS[:3]),
        "supersedes": SUPERSEDED_P15_01,
    }
    write_json_document(attempt / "WORKTREE_SNAPSHOT.json", snapshot)
    return {
        "run_id": run_id,
        "attempt": attempt,
        "draft": draft,
        "plan_sha256": plan_sha256,
        "code_sha256": code_sha256,
        "predecessor_hash": predecessor_hash,
    }


def write_p15_01_receipt(
    attempt: Path,
    *,
    run_id: str,
    plan_sha256: str,
    code_sha256: str,
    predecessor_receipts: Mapping[str, str],
    command_results: list[dict[str, Any]],
    acceptance_checks: Mapping[str, bool],
    coverage: Mapping[str, Any],
    unresolved: list[str],
    reason: str,
) -> dict[str, Any]:
    named = [
        ("DRAFT_MANIFEST.json", "research-draft-manifest-v2", None),
        ("PLAN_SNAPSHOT.json", "research-plan-snapshot-v2", None),
        ("CODE_SNAPSHOT.json", "research-code-snapshot-v2", None),
        ("EVIDENCE_MATRIX.json", "research-evidence-matrix-v2", None),
        ("VERIFIER_CASES.json", "research-verifier-cases-v2", None),
        ("WORK_LOG.md", "research-work-log-v1", None),
        ("DECISIONS.tsv", "research-decisions-tsv-v1", None),
        ("WORKTREE_SNAPSHOT.json", "research-worktree-snapshot-v1", None),
        ("REPORT.md", "research-task-report-v1", None),
        ("pytest.log", "pytest-log", None),
        ("verify_p15_00.log", "verify-log", None),
    ]
    manifest = [
        artifact_entry(attempt / name, schema=schema, row_count=rows)
        for name, schema, rows in named
        if (attempt / name).exists()
    ]
    receipt = make_task_receipt(
        task_id="P15-01",
        run_id=run_id,
        plan_sha256=plan_sha256,
        code_sha256=code_sha256,
        predecessor_receipts=dict(predecessor_receipts),
        command_results=command_results,
        artifact_manifest=manifest,
        acceptance_checks=dict(acceptance_checks),
        disposition="implemented_verified" if all(acceptance_checks.values()) else "blocked_implementation",
        reason=reason,
        coverage=dict(coverage),
        unresolved=list(unresolved),
    )
    write_task_receipt(attempt / "TASK_RECEIPT.json", receipt)
    return receipt
