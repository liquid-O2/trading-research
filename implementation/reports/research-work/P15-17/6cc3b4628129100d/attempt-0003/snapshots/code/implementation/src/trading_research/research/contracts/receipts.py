"""Task, subphase, phase and lineage verification. Failures are data, not report text."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Iterable, Literal, Mapping
import ast
import json
import os

from trading_research.errors import ContractError
from trading_research.research.contracts.identity import (
    ASSURANCE_VERSION,
    DISPOSITIONS,
    SCHEMA_TASK_RECEIPT,
    artifact_entry,
    code_snapshot_document,
    digest,
    file_digest as _identity_file_digest,
    make_task_receipt,
    plan_snapshot_document,
    semantic_run_id,
    validate_receipt_shape,
    write_json_document,
    write_snapshot_tree,
    write_task_receipt,
)

_DIGEST_STATE: ContextVar["_VerifyState | None"] = ContextVar("receipt_digest_state", default=None)


def _verification_file_cache(fn):
    """Reuse read-only parses within a verification, never across public calls.

    Read and fingerprint bytes on every access. Filesystem timestamps can be
    too coarse to distinguish successive same-size edits; only parsing is
    cached, never the assertion that bytes are unchanged.
    """
    @wraps(fn)
    def read(path: Path):
        state = _DIGEST_STATE.get()
        if state is None:
            return fn(path)
        try:
            text = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return fn(path)
        payload = text.encode("utf-8")
        key = (fn.__name__, os.path.abspath(path), sha256(payload).digest())
        if key in state._parsed_files:
            return state._parsed_files[key]
        result = fn(path, _text=text)
        size = len(payload)
        # Large population artifacts should not accumulate in memory merely
        # because a verification visits them. Bound retained input bytes.
        if len(state._parsed_files) < 1024 and state._parsed_bytes + size <= 16 * 1024 * 1024:
            state._parsed_files[key] = result
            state._parsed_bytes += size
        return result
    return read


def file_digest(path: Path) -> str:
    state = _DIGEST_STATE.get()
    if state is None:
        return _identity_file_digest(path)
    return state.cached_file_digest(path)

SCHEMA_SUBPHASE_RECEIPT = "research-subphase-receipt-v2"
SCHEMA_PHASE_RECEIPT = "research-phase-receipt-v2"
SCHEMA_LINEAGE_MANIFEST = "research-lineage-manifest-v1"
SCHEMA_TASK_GRAPH = "research-task-graph-v1"
SCHEMA_GATE_REVIEW = "research-gate-review-v2"
SCHEMA_EVIDENCE_MATRIX = "research-evidence-matrix-v2"
PINNED_CHECKER_SHA256 = "c9441fea0a79674991522ae8db5347cdd1060f372d6aa5cffd425c7f30d6b800"
PINNED_CHECKER_CASES = 27
PINNED_CHECKER_CASE_IDS = (
    "valid_p15_00",
    "valid_p15_01",
    "valid_subphase",
    "required_artifacts_omitted",
    "required_baseline_binding_omitted",
    "plan_sha256_replaced",
    "code_sha256_replaced",
    "run_id_replaced",
    "non_hex_plan_identity",
    "failed_test_excused_as_implemented",
    "command_logs_omitted",
    "false_acceptance_flag",
    "failed_parent_control",
    "child_of_failed_parent",
    "phase_2_closed_using_one_phase_1_5_receipt",
    "unknown_subphase_with_no_tasks",
    "subphase_reuses_wrong_task_receipt",
    "valid_lineage",
    "lineage_child_overrides_ancestor_clock",
    "lineage_invalid_availability_type",
    "lineage_artifact_hash_omitted",
    "trade_valid_evidence",
    "reference_valid_evidence",
    "trade_late_evidence",
    "reference_late_evidence",
    "valid_forecast",
    "forecast_training_ends_after_issue",
)
PINNED_CHECKER_CASE_SET = frozenset(PINNED_CHECKER_CASE_IDS)
EVIDENCE_STATUSES = frozenset({"pass", "fail", "unsupported", "accepted-limit"})
ACCEPTED_MATRIX_STATUSES = frozenset({"pass", "accepted-limit"})
PREDICTOR_EDGE_KEYS = frozenset({"features", "parameters", "parents", "evidence", "predictors"})
OUTCOME_EDGE_KEYS = frozenset({"outcomes", "outcome", "targets", "outcome_edges"})
#: The amendment chain is exempt from the PLAN_SNAPSHOT hash comparison: it is
#: appended to by every amendment and is the document that excuses other plan
#: drift, so a snapshot of it can never match the live file it is checked against.
AMENDMENTS_REL = "planning/research-program/AMENDMENTS.json"
CANONICAL_GRAPH_REL = "planning/research-program/TASK_GRAPH.json"
CANONICAL_REGISTRY_REL = "planning/research-program/ASSURANCE_CASES.json"
SCHEMA_CONTENT_MARKERS = {
    "research-schema-examples-v2": ("native_replay",),
    "research-engineering-dates-v2": ("input_groups", "classified_dates"),
    "research-evidence-matrix-v2": ("checks",),
    "research-draft-manifest-v2": ("task_id", "plan_sha256"),
    "research-plan-snapshot-v2": ("files", "snapshot_paths"),
    "research-code-snapshot-v2": ("files", "runtime"),
    "research-baseline-binding-v1": ("identities", "census"),
    "research-exposure-ledger-v1": ("registry_sha256",),
    "research-verifier-cases-v2": ("cases",),
    "research-gate-review-v2": ("candidate", "verdict"),
    "research-task-receipt-v2": ("task_id", "run_id"),
    "research-subphase-receipt-v2": ("subphase_id", "task_receipts"),
    "research-lineage-manifest-v1": ("records",),
}
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
DEFAULT_AMENDMENTS_PATH = DEFAULT_ROOT / "planning/research-program/AMENDMENTS.json"
EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

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
    card_path: str = ""
    reads: tuple[str, ...] = ()
    owns: tuple[str, ...] = ()


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


@_verification_file_cache
def load_json_document(path: Path, *, _text: str | None = None) -> tuple[Any | None, tuple[CheckFailure, ...]]:
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8") if _text is None else _text
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
            card_path=str(raw.get("path") or ""),
            reads=tuple(str(item) for item in (raw.get("reads") or ())),
            owns=tuple(str(item) for item in (raw.get("owns") or ())),
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


_RECEIPT_WALK_SKIP = frozenset({"jobs", "snapshots", "decoded", "__pycache__"})


def locate_task_receipts(task_id: str, receipts_root: Path) -> tuple[Path, ...]:
    base = Path(receipts_root) / task_id
    if base.is_file():
        return (base,)
    if not base.exists():
        return ()
    return tuple(sorted(path for path in base.rglob("TASK_RECEIPT.json") if path.is_file()))


def locate_all_task_receipts(receipts_root: Path) -> tuple[Path, ...]:
    root = Path(receipts_root)
    if not root.exists():
        return ()
    return tuple(sorted(path for path in root.rglob("TASK_RECEIPT.json") if path.is_file()))


def _index_task_receipts(receipts_root: Path) -> tuple[Path, ...]:
    root = Path(receipts_root)
    found: list[Path] = []
    if root.is_file() and root.name == "TASK_RECEIPT.json":
        return (root,)
    if not root.exists():
        return ()
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = [name for name in dirnames if name not in _RECEIPT_WALK_SKIP and not name.startswith("_work")]
        if "TASK_RECEIPT.json" in filenames:
            found.append(Path(dirpath) / "TASK_RECEIPT.json")
    return tuple(sorted(found))


def _unique_failures(failures: Iterable[CheckFailure]) -> tuple[CheckFailure, ...]:
    seen: set[tuple[str, str, str]] = set()
    ordered: list[CheckFailure] = []
    for item in failures:
        key = (item.code, item.path, item.detail)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(item)
    return tuple(ordered)


def _unpinned_owned_paths(
    owns: Iterable[str],
    code_files: Mapping[str, Any],
    workspace: Path,
    *,
    superseded: Callable[[str, str], bool] | None = None,
) -> list[str]:
    """Owned paths a receipt did not pin.

    A file that appeared under an owned directory after the receipt closed is not
    a failure when a verified later receipt that lists this task as a direct or
    transitive predecessor pins that path at the live digest -- the same rule the
    drift check uses for a changed file, applied to an added one.
    """
    missing: list[str] = []
    for rel in owns:
        if str(rel).endswith("/"):
            directory = workspace / rel
            if not directory.is_dir():
                missing.append(str(rel))
                continue
            for child in directory.rglob("*"):
                if any(part == "__pycache__" for part in child.parts):
                    continue
                if child.suffix == ".pyc" or not child.is_file():
                    continue
                key = child.relative_to(workspace).as_posix()
                if key in code_files:
                    continue
                if superseded is not None and superseded(key, file_digest(child)):
                    continue
                missing.append(key)
        elif rel not in code_files:
            path = workspace / str(rel)
            if superseded is not None and path.is_file() and superseded(str(rel), file_digest(path)):
                continue
            missing.append(str(rel))
    return missing


class _VerifyState:
    def __init__(
        self,
        *,
        receipts_root: Path,
        graph: TaskGraph | None,
        amendments_path: Path,
    ) -> None:
        self.receipts_root = Path(receipts_root)
        self.graph = graph
        self.amendments_path = Path(amendments_path)
        self.visiting: set[str] = set()
        self.pending_ok: set[str] = set()
        self.identity_checked: dict[str, dict[str, Any]] = {}
        self._amendments: Mapping[str, Any] | None = None
        self._amendments_loaded = False
        self._all_receipts: tuple[Path, ...] | None = None
        self._receipts_by_task: dict[str, tuple[Path, ...]] = {}
        self._receipt_buckets: dict[str, list[Path]] | None = None
        self._parsed_files: dict[tuple[Any, ...], Any] = {}
        self._parsed_bytes = 0
        self._receipt_results: dict[tuple[str, tuple[str, ...], tuple[str, ...]], VerificationResult] = {}
        self._predecessor_results: dict[tuple[str, str, str, str], VerificationResult] = {}

    def receipt_memo_key(self, resolved: str) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
        """Memo key for one receipt result.

        A result is reusable only under the same assumption set: ``pending_ok``
        makes ``_check_predecessors`` skip a predecessor and ``visiting`` makes
        ``_code_superseded_by_successor`` skip a candidate, so both belong in the
        key. Within one successor search both are constant, which is where the
        repeated verification is.
        """
        return (resolved, tuple(sorted(self.pending_ok)), tuple(sorted(self.visiting)))

    def cached_file_digest(self, path: Path) -> str:
        # Kept as an internal compatibility entry point. Rehash actual bytes:
        # neither path-only nor timestamp-only memoization proves integrity.
        return _identity_file_digest(Path(path))

    def all_receipts(self) -> tuple[Path, ...]:
        if self._all_receipts is None:
            self._all_receipts = _index_task_receipts(self.receipts_root)
        return self._all_receipts

    def receipts_for(self, task_id: str) -> tuple[Path, ...]:
        if task_id in self._receipts_by_task:
            return self._receipts_by_task[task_id]
        root = self.receipts_root
        found: list[Path] = []
        direct = root / task_id
        if direct.is_file():
            found.append(direct)
        if self._receipt_buckets is None:
            self._receipt_buckets = {}
            try:
                root_resolved = root.resolve()
            except OSError:
                root_resolved = root
            for path in self.all_receipts():
                try:
                    rel = path.resolve().relative_to(root_resolved)
                except ValueError:
                    continue
                if rel.parts:
                    self._receipt_buckets.setdefault(rel.parts[0], []).append(path)
        found.extend(self._receipt_buckets.get(task_id, ()))
        result = tuple(sorted(set(found)))
        self._receipts_by_task[task_id] = result
        return result

    def amendments(self) -> Mapping[str, Any] | None:
        if not self._amendments_loaded:
            self._amendments_loaded = True
            if self.amendments_path.is_file():
                document, failures = load_json_document(self.amendments_path)
                if not failures and isinstance(document, dict):
                    self._amendments = document
        return self._amendments


def _draft_date(draft: Mapping[str, Any]) -> str | None:
    raw = draft.get("drafted_at") or draft.get("created_at")
    if isinstance(raw, str) and len(raw) >= 10:
        return raw[:10]
    return None


def _is_new_shape_amendment(entry: Any) -> bool:
    if not isinstance(entry, dict):
        return False
    if "previous_entry_sha256" not in entry:
        return False
    changed = entry.get("changed_files")
    if not isinstance(changed, list):
        return False
    for item in changed:
        if not isinstance(item, dict):
            return False
        if not isinstance(item.get("path"), str) or not item.get("path"):
            return False
        if "sha256_before" not in item or "sha256_after" not in item:
            return False
    return (
        isinstance(entry.get("date"), str)
        and isinstance(entry.get("id"), str)
        and isinstance(entry.get("assurance_version"), str)
        and entry.get("id")
        and entry.get("date")
        and entry.get("assurance_version")
    )


def _load_amendments_document(path: Path | None) -> Mapping[str, Any] | None:
    target = Path(path) if path is not None else DEFAULT_AMENDMENTS_PATH
    if not target.is_file():
        return None
    document, failures = load_json_document(target)
    if failures or not isinstance(document, dict):
        return None
    return document


def _plan_superseded_by_amendments(
    rel: str,
    declared: str,
    live: str,
    *,
    draft_date: str | None,
    amendments: Mapping[str, Any] | None,
) -> bool:
    if amendments is None:
        return False
    entries = amendments.get("amendments")
    if not isinstance(entries, list) or not entries:
        return False
    chained_started = False
    for index, entry in enumerate(entries):
        if not _is_new_shape_amendment(entry):
            continue
        chained_started = True
        previous = entries[index - 1] if index > 0 else None
        expected_previous = None if previous is None else digest(previous)
        if entry.get("previous_entry_sha256") != expected_previous:
            return False
    if not chained_started:
        return False
    current = declared
    started = False
    for entry in entries:
        if not _is_new_shape_amendment(entry):
            continue
        hit = None
        for item in entry.get("changed_files") or []:
            if not isinstance(item, dict):
                return False
            if item.get("path") != rel:
                continue
            before = item.get("sha256_before")
            after = item.get("sha256_after")
            if not _hex_digest(before) or not _hex_digest(after):
                return False
            hit = item
            break
        if hit is None:
            continue
        entry_date = str(entry.get("date") or "")[:10]
        predates = bool(draft_date and entry_date and entry_date < draft_date)
        supplies_declared_successor = not started and hit["sha256_before"] == declared
        if predates:
            if supplies_declared_successor:
                return False
            continue
        if not started:
            if hit["sha256_before"] != declared:
                continue
            started = True
            current = str(hit["sha256_after"])
            continue
        if hit["sha256_before"] != current:
            return False
        current = str(hit["sha256_after"])
    return current == live


def _graph_hash_connected(
    declared: str,
    live: str,
    *,
    draft_date: str | None,
    amendments: Mapping[str, Any] | None,
    graph_path: Path,
) -> bool:
    if declared == live:
        return True
    rels = [CANONICAL_GRAPH_REL, str(graph_path)]
    try:
        rels.append(str(Path(graph_path).resolve().relative_to(DEFAULT_ROOT)))
    except ValueError:
        pass
    seen: set[str] = set()
    for rel in rels:
        if rel in seen:
            continue
        seen.add(rel)
        if _plan_superseded_by_amendments(
            rel,
            declared,
            live,
            draft_date=draft_date,
            amendments=amendments,
        ):
            return True
    return False


def _code_files_from_receipt(document: Mapping[str, Any]) -> dict[str, Any]:
    named = _manifest_by_name(document.get("artifact_manifest"))
    entry = named.get("CODE_SNAPSHOT.json")
    if entry is None or not isinstance(entry.get("path"), str):
        return {}
    snapshot, failures = load_json_document(Path(entry["path"]))
    if failures or not isinstance(snapshot, dict):
        return {}
    files = snapshot.get("files")
    return files if isinstance(files, dict) else {}


def _receipt_lists_predecessor(
    document: Mapping[str, Any],
    document_path: Path,
    task_id: str,
    expected_digest: str,
    state: _VerifyState,
    *,
    seen: set[str] | None = None,
) -> bool:
    walking = set() if seen is None else seen
    loc = str(document_path)
    if loc in walking:
        return False
    walking.add(loc)
    declared = document.get("predecessor_receipts")
    if not isinstance(declared, dict):
        return False
    if task_id in declared and _predecessor_digest(declared[task_id]) == expected_digest:
        return True
    for dep, value in declared.items():
        digest_value = _predecessor_digest(value)
        if digest_value is None:
            continue
        search: list[Path] = []
        hinted = _predecessor_path(value)
        if hinted is not None:
            search.append(hinted)
        search.extend(state.receipts_for(str(dep)))
        matched = _matching_receipt(str(dep), digest_value, search)
        if matched is None:
            continue
        child, failures = load_json_document(matched)
        if failures or not isinstance(child, dict):
            continue
        if _receipt_lists_predecessor(child, matched, task_id, expected_digest, state, seen=walking):
            return True
    return False


def _code_superseded_by_successor(
    rel: str,
    live: str,
    *,
    receipt_path: Path,
    receipt: Mapping[str, Any],
    state: _VerifyState,
) -> bool:
    current_id = str(receipt.get("task_id") or "")
    current_digest = file_digest(receipt_path)
    for other_path, info in state.identity_checked.items():
        if other_path == str(receipt_path):
            continue
        files = info.get("code_files") or {}
        if files.get(rel) != live:
            continue
        predecessors = info.get("predecessors") or {}
        if current_id in predecessors and _predecessor_digest(predecessors[current_id]) == current_digest:
            return True
        other_doc_path = Path(str(info.get("path") or other_path))
        synthetic = {"predecessor_receipts": predecessors, "artifact_manifest": []}
        if _receipt_lists_predecessor(synthetic, other_doc_path, current_id, current_digest, state):
            return True
    for candidate in state.all_receipts():
        cand = str(candidate)
        if cand == str(receipt_path) or cand in state.visiting:
            continue
        document, failures = load_json_document(candidate)
        if failures or not isinstance(document, dict):
            continue
        files = _code_files_from_receipt(document)
        if files.get(rel) != live:
            continue
        # Most historical attempts cannot authorize these live bytes. Reject
        # them before walking their (often shared) predecessor DAG.
        if not _receipt_lists_predecessor(document, candidate, current_id, current_digest, state):
            continue
        state.pending_ok.add(str(receipt_path))
        try:
            result = verify_task_receipt(
                candidate,
                graph=state.graph,
                receipts_root=state.receipts_root,
                amendments_path=state.amendments_path,
                _state=state,
            )
        finally:
            state.pending_ok.discard(str(receipt_path))
        if result.ok:
            return True
    return False


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
        actual = file_digest(artifact)
        declared = entry.get("sha256")
        if not _hex_digest(declared):
            _append(failures, FailureCode.ARTIFACT_HASH, raw_path, "artifact sha256 is not a lowercase digest")
        elif actual != declared:
            _append(failures, FailureCode.ARTIFACT_HASH, raw_path, "artifact sha256 does not match file bytes")
        declared_bytes = entry.get("bytes")
        actual_bytes = artifact.stat().st_size
        if type(declared_bytes) is int and declared_bytes != actual_bytes:
            _append(failures, FailureCode.ARTIFACT_BYTES, raw_path, f"declared {declared_bytes} bytes, file has {actual_bytes}")
        if artifact.name == RESULT_CARD_NAME:
            for detail in result_card_failures(artifact):
                _append(failures, FailureCode.INVENTORY, raw_path, detail)


RESULT_CARD_NAME = "RESULT_CARD.json"
RESULT_CARD_SCHEMA = "research-result-card-v1"
RESULT_CARD_VERDICTS = ("done_well", "needs_upgrade", "not_reaching_target", "not_applicable")
RESULT_CARD_MET = ("yes", "no", "partial", "not_applicable")


def result_card_failures(path: Path) -> list[str]:
    """The result card of DELIVERABLES.md: a task cannot close without a judgeable result.

    Shape: schema_version; question (text); headline (1 to 5 rows, each with value, unit, an
    interval or a support count, and an artifact pointer with sha256); target (text and met in
    yes/no/partial/not_applicable); verdict (done_well, needs_upgrade, not_reaching_target,
    not_applicable) with a reason; lever (required unless the verdict is done_well); limits."""
    problems: list[str] = []
    try:
        card = json.loads(path.read_text())
    except Exception as exc:
        return [f"result card is not valid JSON: {exc}"]
    if not isinstance(card, dict):
        return ["result card must be an object"]
    if card.get("schema_version") != RESULT_CARD_SCHEMA:
        problems.append(f"result card schema_version must be {RESULT_CARD_SCHEMA}")
    if not isinstance(card.get("question"), str) or not card["question"].strip():
        problems.append("result card question must be a non-empty string")
    headline = card.get("headline")
    if not isinstance(headline, list) or not 1 <= len(headline) <= 5:
        problems.append("result card headline must list 1 to 5 numbers")
    else:
        for index, row in enumerate(headline):
            if not isinstance(row, dict):
                problems.append(f"headline[{index}] must be an object")
                continue
            if not isinstance(row.get("value"), (int, float)) or isinstance(row.get("value"), bool):
                problems.append(f"headline[{index}].value must be a number")
            if not isinstance(row.get("unit"), str) or not row["unit"]:
                problems.append(f"headline[{index}].unit must name the unit")
            if not (isinstance(row.get("interval"), (list, tuple)) and len(row["interval"]) == 2) and not isinstance(row.get("support"), int):
                problems.append(f"headline[{index}] needs an interval [low, high] or a support count")
            if not isinstance(row.get("artifact"), str) or not _hex_digest(row.get("sha256")):
                problems.append(f"headline[{index}] needs an artifact path and its sha256")
    target = card.get("target")
    if not isinstance(target, dict) or not isinstance(target.get("text"), str) or target.get("met") not in RESULT_CARD_MET:
        problems.append("result card target needs text and met in yes/no/partial/not_applicable")
    verdict = card.get("verdict")
    if not isinstance(verdict, dict) or verdict.get("value") not in RESULT_CARD_VERDICTS or not isinstance(verdict.get("reason"), str) or not verdict["reason"].strip():
        problems.append("result card verdict needs value in done_well/needs_upgrade/not_reaching_target/not_applicable and a reason")
    elif verdict["value"] != "done_well":
        lever = card.get("lever")
        if not isinstance(lever, dict) or not isinstance(lever.get("change"), str) or not lever["change"].strip() or not isinstance(lever.get("evidence"), str) or not lever["evidence"].strip():
            problems.append("result card lever (change and evidence) is required unless the verdict is done_well")
    if not isinstance(card.get("limits"), list):
        problems.append("result card limits must be a list")
    return problems


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
    *,
    state: _VerifyState | None = None,
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
        if state is not None:
            search.extend(state.receipts_for(dep))
        else:
            search.extend(locate_task_receipts(dep, receipts_root))
        search.extend(artifact_paths)
        matched = _matching_receipt(dep, expected, search)
        if matched is not None and graph is not None:
            if state is not None and str(matched) in state.pending_ok:
                continue
            cache_key = (str(matched), expected, graph.path, graph.assurance_version)
            cache = state._predecessor_results if state is not None else _VERIFY_CACHE
            cached = cache.get(cache_key)
            if cached is None:
                cache[cache_key] = VerificationResult(
                    "task",
                    False,
                    str(matched),
                    (CheckFailure(FailureCode.GRAPH_CYCLE, str(matched), f"cycle while verifying predecessor {dep}"),),
                )
                cached = verify_task_receipt(
                    matched,
                    graph=graph,
                    receipts_root=receipts_root,
                    amendments_path=state.amendments_path if state is not None else None,
                    _state=state,
                )
                cache[cache_key] = cached
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


def _manifest_path_components(entries: Any) -> set[str]:
    """Every directory name that appears in a manifest entry's path.

    A required artifact that names a directory is satisfied when the manifest
    carries the hashed files inside it; the entry's own `.name` is then the file,
    never the directory.
    """
    out: set[str] = set()
    if not isinstance(entries, list):
        return out
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        parts = Path(entry["path"]).parts
        out.update(parts[:-1])
        for member in entry.get("directory_index") or []:
            if isinstance(member, dict) and isinstance(member.get("path"), str):
                out.update(Path(member["path"]).parts[:-1])
    return out


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


def _unique_paths(items: Iterable[str]) -> tuple[str, ...]:
    seen: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.append(item)
    return tuple(seen)


def _is_canonical_graph(graph: TaskGraph) -> bool:
    return Path(graph.path).resolve() == DEFAULT_GRAPH_PATH.resolve()


def _required_plan_files(spec: TaskSpec, graph: TaskGraph) -> tuple[str, ...]:
    items = [spec.card_path, *spec.reads]
    if _is_canonical_graph(graph):
        items.extend((CANONICAL_GRAPH_REL, CANONICAL_REGISTRY_REL))
    return _unique_paths(items)


@_verification_file_cache
def _module_symbols(path: Path, *, _text: str | None = None) -> set[str] | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8") if _text is None else _text)
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Assign)):
                        if isinstance(child, ast.Assign):
                            for target in child.targets:
                                if isinstance(target, ast.Name):
                                    names.add(f"{node.name}.{target.id}")
                        else:
                            names.add(child.name)
                            names.add(f"{node.name}.{child.name}")
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _test_node_names(path: Path) -> set[str] | None:
    symbols = _module_symbols(path)
    if symbols is None:
        return None
    names = set(symbols)
    for item in symbols:
        if "." in item:
            names.add(item.split(".", 1)[1])
    return names


def _resolve_json_pointer(document: Any, pointer: str) -> bool:
    if pointer == "":
        return True
    if not pointer.startswith("/"):
        return False
    current = document
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            if not token.isdigit():
                return False
            index = int(token)
            if index < 0 or index >= len(current):
                return False
            current = current[index]
        elif isinstance(current, dict):
            if token not in current:
                return False
            current = current[token]
        else:
            return False
    return True


def _json_row_ids(document: Any) -> set[str]:
    found: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key in ("row_id", "id", "record_id"):
                value = node.get(key)
                if isinstance(value, str) and value:
                    found.add(value)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(document)
    return found


def _load_json_or_jsonl(path: Path) -> Any | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    try:
        return json.loads(text)
    except ValueError:
        rows: list[Any] = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                return None
        return rows or None


def _row_ids_resolve(path: Path, row_ids: list[Any]) -> bool:
    document = _load_json_or_jsonl(path)
    if document is None:
        return False
    known = _json_row_ids(document)
    return all(isinstance(item, str) and item in known for item in row_ids)


def _selector_resolves(path: Path, selector: str) -> bool:
    if not isinstance(selector, str) or not selector:
        return False
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    document = None
    try:
        document = json.loads(text)
    except ValueError:
        document = None
    if document is not None:
        if selector in {"/", ""}:
            return True
        if selector.startswith("/"):
            return _resolve_json_pointer(document, selector)
        return selector in _json_row_ids(document)
    if selector in {"/", ""}:
        return True
    return selector in text


def _resolve_workspace_file(raw: str, workspace: Path) -> Path | None:
    path = Path(raw)
    if path.is_file():
        return path
    alt = workspace / raw
    if alt.is_file():
        return alt
    return None


def _audit_command(command: Mapping[str, Any]) -> bool:
    argv = command.get("argv")
    if not isinstance(argv, list):
        return False
    joined = " ".join(str(item) for item in argv)
    return "verify_research_release.py" in joined or "check_foundation_adversarial.py" in joined


def _check_snapshot_copies(
    files: Mapping[str, Any],
    copies: Any,
    snapshot_path: Path,
    failures: list[CheckFailure],
    *,
    kind: str,
) -> None:
    loc = str(snapshot_path)
    if not isinstance(copies, dict) or not copies:
        _append(failures, FailureCode.ARTIFACT_MISSING, loc, f"{kind} snapshot_paths is missing or empty")
        return
    missing = [rel for rel in files if rel not in copies]
    extra = [rel for rel in copies if rel not in files]
    if missing or extra:
        _append(
            failures,
            FailureCode.IDENTITY,
            loc,
            f"{kind} snapshot_paths keys mismatch missing={missing} extra={extra}",
        )
    root = snapshot_path.parent
    for rel, copy_rel in copies.items():
        if not isinstance(copy_rel, str) or not copy_rel:
            _append(failures, FailureCode.ARTIFACT_MISSING, loc, f"{kind} snapshot copy path missing for {rel}")
            continue
        copy_path = root / copy_rel
        if not copy_path.is_file():
            _append(failures, FailureCode.ARTIFACT_MISSING, str(copy_path), f"{kind} snapshot copy missing for {rel}")
            continue
        declared = files.get(rel)
        if _hex_digest(declared) and file_digest(copy_path) != declared:
            _append(failures, FailureCode.ARTIFACT_HASH, str(copy_path), f"{kind} snapshot copy hash mismatch for {rel}")


def _check_declared_source_files(
    files: Mapping[str, Any],
    failures: list[CheckFailure],
    snapshot_path: str,
    *,
    kind: str,
    receipt_path: Path | None = None,
    receipt: Mapping[str, Any] | None = None,
    draft_date: str | None = None,
    state: _VerifyState | None = None,
) -> None:
    if not isinstance(files, dict) or not files:
        _append(failures, FailureCode.IDENTITY, snapshot_path, f"{kind} snapshot files mapping is empty")
        return
    for rel, declared in files.items():
        if kind == "plan" and str(rel) == AMENDMENTS_REL:
            # The amendment chain grows with every amendment and is the document
            # this check reads to excuse other plan drift; it cannot verify
            # through itself. It is loaded and validated separately.
            continue
        source = DEFAULT_ROOT / str(rel)
        if not source.is_file():
            _append(failures, FailureCode.ARTIFACT_MISSING, str(source), f"{kind} source {rel} does not exist")
            continue
        actual = file_digest(source)
        if not _hex_digest(declared):
            _append(failures, FailureCode.IDENTITY, snapshot_path, f"{kind} declared hash for {rel} is not a digest")
            continue
        if actual == declared:
            continue
        superseded = False
        if kind == "plan" and state is not None:
            superseded = _plan_superseded_by_amendments(
                str(rel),
                str(declared),
                actual,
                draft_date=draft_date,
                amendments=state.amendments(),
            )
        elif kind == "code" and state is not None and receipt_path is not None and receipt is not None:
            superseded = _code_superseded_by_successor(
                str(rel),
                actual,
                receipt_path=receipt_path,
                receipt=receipt,
                state=state,
            )
        if not superseded:
            _append(
                failures,
                FailureCode.IDENTITY,
                str(source),
                f"{kind} declared hash does not match workspace bytes for {rel}",
            )


def _check_input_identities(draft: Mapping[str, Any], failures: list[CheckFailure], loc: str) -> None:
    identities = draft.get("input_identities")
    if identities is None:
        return
    if not isinstance(identities, dict):
        _append(failures, FailureCode.IDENTITY, loc, "input_identities must be an object")
        return
    for key, value in identities.items():
        if isinstance(value, dict) and isinstance(value.get("path"), str) and value.get("path"):
            path = Path(value["path"])
            digest_value = value.get("sha256")
            if not path.is_file():
                _append(failures, FailureCode.ARTIFACT_MISSING, str(path), f"input identity {key} path does not exist")
                continue
            if not _hex_digest(digest_value):
                _append(failures, FailureCode.IDENTITY, loc, f"input identity {key} sha256 is not a digest")
            elif file_digest(path) != digest_value:
                _append(failures, FailureCode.ARTIFACT_HASH, str(path), f"input identity {key} hash does not match file bytes")
        else:
            _append(
                failures,
                FailureCode.IDENTITY,
                loc,
                f"input identity {key} must bind a preserved path and sha256",
            )


def _parsed_schema_labels(document: Mapping[str, Any]) -> list[Any]:
    labels = []
    if "schema_version" in document:
        labels.append(document.get("schema_version"))
    if "schema" in document:
        labels.append(document.get("schema"))
    return labels


def _schema_contents_match(document: Mapping[str, Any], schema: str) -> bool:
    markers = SCHEMA_CONTENT_MARKERS.get(schema)
    if not markers:
        return True
    return any(marker in document for marker in markers)


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
        status = check.get("status")
        if status not in EVIDENCE_STATUSES:
            _append(failures, FailureCode.SCHEMA, loc, "check status is not supported")
        check_id = check.get("id")
        acceptance = receipt.get("acceptance_checks") if isinstance(receipt.get("acceptance_checks"), dict) else {}
        accepted = receipt.get("disposition") in SUCCESS_DISPOSITIONS
        if status == "fail" and accepted:
            _append(
                failures,
                FailureCode.ACCEPTANCE,
                loc,
                f"matrix check {check_id} is fail while receipt disposition is accepted",
            )
        if isinstance(check_id, str) and acceptance.get(check_id) is True and status not in ACCEPTED_MATRIX_STATUSES:
            _append(
                failures,
                FailureCode.ACCEPTANCE,
                loc,
                f"matrix check {check_id} status {status} disagrees with acceptance_checks[{check_id}]=true",
            )
        if status == "unsupported" and accepted:
            _append(
                failures,
                FailureCode.ACCEPTANCE,
                loc,
                f"matrix check {check_id} is unsupported while receipt disposition is accepted",
            )
        refs = check.get("code_refs")
        if not isinstance(refs, list):
            _append(failures, FailureCode.INVENTORY, loc, "code_refs must be a list")
        else:
            if status in {"pass", "accepted-limit"} and not refs:
                _append(failures, FailureCode.INVENTORY, loc, "passing check has no code_refs")
            for ref in refs:
                if not isinstance(ref, dict) or not ref.get("path") or not ref.get("symbol"):
                    _append(failures, FailureCode.INVENTORY, loc, "code_ref needs path and symbol")
                    continue
                code_path = _resolve_workspace_file(str(ref["path"]), workspace)
                if code_path is None:
                    _append(failures, FailureCode.ARTIFACT_MISSING, str(ref["path"]), "code_ref path does not exist")
                    continue
                symbols = _module_symbols(code_path)
                if symbols is None or str(ref["symbol"]) not in symbols:
                    _append(
                        failures,
                        FailureCode.INVENTORY,
                        loc,
                        f"code_ref symbol {ref['symbol']} does not exist in {ref['path']}",
                    )
        nodes = check.get("test_nodeids")
        if not isinstance(nodes, list) or any(not isinstance(item, str) or not item for item in nodes):
            _append(failures, FailureCode.INVENTORY, loc, "test_nodeids must be a list of strings")
            nodes = []
        indices = check.get("command_indices")
        if not isinstance(indices, list) or any(type(item) is not int for item in indices):
            _append(failures, FailureCode.INVENTORY, loc, "command_indices must be a list of ints")
            indices = []
        else:
            for item in indices:
                if item < 0 or item >= len(commands):
                    _append(failures, FailureCode.INVENTORY, loc, f"command index {item} is not an executed command")
        referenced_commands = [
            commands[item]
            for item in indices
            if type(item) is int and 0 <= item < len(commands) and isinstance(commands[item], dict)
        ]
        has_audit = any(_audit_command(command) for command in referenced_commands)
        if status in {"pass", "accepted-limit"} and not indices:
            _append(failures, FailureCode.INVENTORY, loc, "passing check has no executed command_indices")
        if status in {"pass", "accepted-limit"} and not nodes and not has_audit:
            _append(failures, FailureCode.INVENTORY, loc, "passing check has no test_nodeids or audit command")
        for nodeid in nodes:
            if not isinstance(nodeid, str) or "::" not in nodeid:
                _append(failures, FailureCode.INVENTORY, loc, f"test nodeid {nodeid!r} is malformed")
                continue
            file_part, _, test_part = nodeid.partition("::")
            test_path = _resolve_workspace_file(file_part, workspace)
            if test_path is None:
                _append(failures, FailureCode.ARTIFACT_MISSING, file_part, "test nodeid path does not exist")
                continue
            names = _test_node_names(test_path)
            wanted = test_part.split("::")[-1]
            if names is None or wanted not in names:
                _append(failures, FailureCode.INVENTORY, loc, f"test nodeid {nodeid} does not resolve")
        evidence = check.get("evidence")
        if not isinstance(evidence, list):
            _append(failures, FailureCode.INVENTORY, loc, "evidence must be a list")
            continue
        if status in {"pass", "accepted-limit"} and not evidence:
            _append(failures, FailureCode.INVENTORY, loc, "passing check has no evidence")
        for item in evidence:
            if not isinstance(item, dict):
                _append(failures, FailureCode.INVENTORY, loc, "evidence item must be an object")
                continue
            selector = item.get("selector")
            if not isinstance(selector, str) or not selector:
                _append(failures, FailureCode.INVENTORY, loc, "evidence selector is missing")
                selector = None
            raw_path = item.get("path")
            digest_value = item.get("sha256")
            if not isinstance(raw_path, str) or not raw_path:
                _append(failures, FailureCode.ARTIFACT_MISSING, loc, "evidence path is missing")
                continue
            evidence_path = _resolve_workspace_file(raw_path, workspace)
            if evidence_path is None:
                _append(failures, FailureCode.ARTIFACT_MISSING, raw_path, "evidence file does not exist")
                continue
            if not _hex_digest(digest_value):
                _append(failures, FailureCode.ARTIFACT_HASH, raw_path, "evidence sha256 is not a lowercase digest")
            elif file_digest(evidence_path) != digest_value:
                _append(failures, FailureCode.ARTIFACT_HASH, raw_path, "evidence sha256 does not match file bytes")
            if selector is not None and not _selector_resolves(evidence_path, selector):
                _append(failures, FailureCode.INVENTORY, loc, f"evidence selector {selector} does not resolve")


def _check_inventory(receipt: Mapping[str, Any], spec: TaskSpec, graph: TaskGraph, receipt_path: Path, failures: list[CheckFailure]) -> None:
    entries = receipt.get("artifact_manifest")
    if not isinstance(entries, list) or not entries:
        _append(failures, FailureCode.INVENTORY, str(receipt_path), "artifact_manifest is empty")
        return
    named = _manifest_by_name(entries)
    components = _manifest_path_components(entries)
    required = list(graph.required_task_artifacts) + list(spec.artifacts)
    missing = [
        name
        for name in required
        if name not in named and str(name).rstrip("/") not in components
    ]
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
            if isinstance(document, dict) and isinstance(schema, str) and schema.startswith("research-"):
                labels = _parsed_schema_labels(document)
                if not labels:
                    _append(failures, FailureCode.SCHEMA, str(path), f"parsed artifact is missing schema for declared {schema}")
                elif any(label != schema for label in labels):
                    _append(
                        failures,
                        FailureCode.SCHEMA,
                        str(path),
                        f"parsed schema {document.get('schema_version') or document.get('schema')} != declared {schema}",
                    )
                elif not _schema_contents_match(document, schema):
                    _append(failures, FailureCode.SCHEMA, str(path), f"parsed contents do not match declared {schema}")
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


def _check_identities(
    receipt: Mapping[str, Any],
    receipt_path: Path,
    graph: TaskGraph,
    failures: list[CheckFailure],
    *,
    state: _VerifyState | None = None,
) -> None:
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
        spec = graph.require(str(receipt.get("task_id") or ""))
        if spec is not None:
            required_plan = _required_plan_files(spec, graph)
            missing_plan = [rel for rel in required_plan if rel not in files]
            if missing_plan:
                _append(
                    failures,
                    FailureCode.INVENTORY,
                    plan_entry["path"],
                    f"PLAN_SNAPSHOT missing required files: {missing_plan}",
                )
        _check_declared_source_files(
            files,
            failures,
            plan_entry["path"],
            kind="plan",
            receipt_path=receipt_path,
            receipt=receipt,
            draft_date=_draft_date(draft_doc),
            state=state,
        )
        _check_snapshot_copies(files, plan_doc.get("snapshot_paths"), Path(plan_entry["path"]), failures, kind="plan")
    code_files = code_doc.get("files")
    if not isinstance(code_files, dict):
        _append(failures, FailureCode.IDENTITY, code_entry["path"], "CODE_SNAPSHOT.files must be a mapping")
    else:
        spec = graph.require(str(receipt.get("task_id") or ""))
        if spec is not None:
            def _added_is_superseded(rel: str, live: str, _receipt=receipt, _path=receipt_path) -> bool:
                if state is None:
                    return False
                return _code_superseded_by_successor(
                    rel, live, receipt_path=_path, receipt=_receipt, state=state
                )

            missing_code = _unpinned_owned_paths(
                spec.owns, code_files, DEFAULT_ROOT, superseded=_added_is_superseded
            )
            if missing_code:
                _append(
                    failures,
                    FailureCode.INVENTORY,
                    code_entry["path"],
                    f"CODE_SNAPSHOT missing owned files: {missing_code}",
                )
        if state is not None:
            state.identity_checked[str(receipt_path)] = {
                "task_id": str(receipt.get("task_id") or ""),
                "digest": file_digest(receipt_path),
                "predecessors": receipt.get("predecessor_receipts") or {},
                "code_files": code_files,
                "path": str(receipt_path),
            }
        _check_declared_source_files(
            code_files,
            failures,
            code_entry["path"],
            kind="code",
            receipt_path=receipt_path,
            receipt=receipt,
            draft_date=_draft_date(draft_doc),
            state=state,
        )
        _check_snapshot_copies(code_files, code_doc.get("snapshot_paths"), Path(code_entry["path"]), failures, kind="code")
    runtime = code_doc.get("runtime")
    if not isinstance(runtime, dict) or not isinstance(runtime.get("python"), str) or not runtime.get("python"):
        _append(failures, FailureCode.IDENTITY, code_entry["path"], "CODE_SNAPSHOT.runtime.python is missing")
    lock_digest = code_doc.get("dependency_lock_sha256")
    lock_path = DEFAULT_ROOT / "implementation/uv.lock"
    fallback_lock = DEFAULT_ROOT / "implementation/pyproject.toml"
    expected_lock = file_digest(lock_path) if lock_path.is_file() else (file_digest(fallback_lock) if fallback_lock.is_file() else None)
    if not _hex_digest(lock_digest):
        _append(failures, FailureCode.IDENTITY, code_entry["path"], "dependency_lock_sha256 is not a digest")
    elif expected_lock is not None and lock_digest != expected_lock:
        _append(failures, FailureCode.IDENTITY, code_entry["path"], "dependency_lock_sha256 does not match the workspace lock")
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
    _check_input_identities(draft_doc, failures, draft_entry["path"])


_VERIFY_CACHE: dict[tuple[str, str, str, str], VerificationResult] = {}


def _resolved_path(path: Path) -> str:
    try:
        return str(Path(path).resolve())
    except OSError:
        return str(path)


def verify_task_receipt(
    receipt_path: Path,
    *,
    graph: TaskGraph | None = None,
    graph_path: Path | None = None,
    receipts_root: Path | None = None,
    amendments_path: Path | None = None,
    _state: _VerifyState | None = None,
) -> VerificationResult:
    path = Path(receipt_path)
    resolved_root = Path(receipts_root) if receipts_root is not None else DEFAULT_RECEIPTS_ROOT
    resolved_amendments = Path(amendments_path) if amendments_path is not None else DEFAULT_AMENDMENTS_PATH
    resolved = _resolved_path(path)
    state = _state
    if state is None:
        state = _VerifyState(
            receipts_root=resolved_root,
            graph=graph,
            amendments_path=resolved_amendments,
        )
    memo_key = state.receipt_memo_key(resolved)
    cached = state._receipt_results.get(memo_key)
    if cached is not None:
        return cached
    token = _DIGEST_STATE.set(state)
    try:
        failures: list[CheckFailure] = []
        document, parse_failures = load_json_document(path)
        failures.extend(parse_failures)
        loaded_graph = graph
        graph_failures: tuple[CheckFailure, ...] = ()
        if loaded_graph is None:
            loaded_graph, graph_failures = load_task_graph(graph_path)
            failures.extend(graph_failures)
        if state.graph is None and loaded_graph is not None:
            state.graph = loaded_graph
        if document is None or loaded_graph is None:
            result = VerificationResult("task", False, str(path), tuple(failures))
            state._receipt_results[memo_key] = result
            return result
        if not isinstance(document, dict):
            _append(failures, FailureCode.SCHEMA, str(path), "task receipt must be a JSON object")
            result = VerificationResult("task", False, str(path), tuple(failures))
            state._receipt_results[memo_key] = result
            return result
        try:
            receipt = validate_receipt_shape(document)
        except ContractError as exc:
            _append(failures, FailureCode.SCHEMA, str(path), str(exc))
            result = VerificationResult("task", False, str(path), tuple(failures))
            state._receipt_results[memo_key] = result
            return result
        if receipt.get("assurance_version") != ASSURANCE_VERSION:
            _append(failures, FailureCode.IDENTITY, str(path), "assurance_version is not current")
        task_id = receipt["task_id"]
        spec = loaded_graph.require(task_id)
        if spec is None:
            _append(failures, FailureCode.UNKNOWN_TASK, str(path), f"{task_id} is not in TASK_GRAPH")
            result = VerificationResult("task", False, str(path), tuple(failures))
            state._receipt_results[memo_key] = result
            return result
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
        state.visiting.add(str(path))
        try:
            _check_identities(receipt, path, loaded_graph, failures, state=state)
            _check_evidence_matrix(receipt, spec, path, failures)
            unresolved = receipt["unresolved"] if isinstance(receipt["unresolved"], list) else []
            _check_commands(receipt["command_results"], unresolved, path, receipt["disposition"], failures)
            _check_predecessors(
                receipt,
                spec,
                path,
                resolved_root,
                failures,
                graph=loaded_graph,
                state=state,
            )
        finally:
            state.visiting.discard(str(path))
        unique = _unique_failures(failures)
        result = VerificationResult("task", not unique, str(path), unique)
        state._receipt_results[memo_key] = result
        return result
    finally:
        _DIGEST_STATE.reset(token)


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


def _bind_review_file(
    raw: Any,
    failures: list[CheckFailure],
    loc: str,
    *,
    label: str,
    require_hash_match: bool = True,
) -> Path | None:
    if not isinstance(raw, dict) or not isinstance(raw.get("path"), str) or not raw.get("path"):
        _append(failures, FailureCode.GATE_REVIEW, loc, f"{label} path is missing")
        return None
    path = Path(raw["path"])
    if not path.is_file():
        _append(failures, FailureCode.ARTIFACT_MISSING, str(path), f"{label} file does not exist")
        return None
    digest_value = raw.get("sha256")
    if not _hex_digest(digest_value):
        _append(failures, FailureCode.GATE_REVIEW, loc, f"{label} sha256 is not a digest")
        return path
    if require_hash_match and file_digest(path) != digest_value:
        _append(failures, FailureCode.ARTIFACT_HASH, str(path), f"{label} hash does not match file bytes")
    return path


def _registry_cases_by_id(document: Mapping[str, Any] | None) -> dict[str, Mapping[str, Any]]:
    if not isinstance(document, dict):
        return {}
    rows = document.get("cases")
    if not isinstance(rows, list):
        return {}
    mapped: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("id"), str) and row["id"] not in mapped:
            mapped[row["id"]] = row
    return mapped


def _review_bound_case_ids(
    graph: TaskGraph,
    expected_tasks: list[str],
    comparison_cases: Mapping[str, Mapping[str, Any]],
) -> list[str]:
    expected = {str(item) for item in expected_tasks}
    ordered: list[str] = []
    seen: set[str] = set()
    for task_id in expected_tasks:
        spec = graph.require(task_id)
        if spec is None:
            continue
        for case_id in spec.assurance_cases:
            if case_id in seen:
                continue
            seen.add(case_id)
            ordered.append(case_id)
    for case_id, row in comparison_cases.items():
        tasks = row.get("tasks")
        if not isinstance(tasks, list):
            continue
        if not expected.intersection(str(item) for item in tasks):
            continue
        if case_id in seen:
            continue
        seen.add(case_id)
        ordered.append(case_id)
    return ordered


def _pinned_registry_snapshot_copy(
    review_path: Path,
    candidate_path: Path,
    candidate_doc: Mapping[str, Any] | None,
    pinned_hash: str,
) -> Path | None:
    candidates = (
        review_path.parent / "snapshots/plan" / CANONICAL_REGISTRY_REL,
        review_path.parent / "snapshots" / CANONICAL_REGISTRY_REL,
        candidate_path.parent / "snapshots/plan" / CANONICAL_REGISTRY_REL,
        candidate_path.parent / "snapshots" / CANONICAL_REGISTRY_REL,
    )
    for path in candidates:
        if path.is_file() and file_digest(path) == pinned_hash:
            return path
    if not isinstance(candidate_doc, dict):
        return None
    refs = candidate_doc.get("task_receipts")
    if not isinstance(refs, dict):
        return None
    for ref in refs.values():
        if not isinstance(ref, dict) or not isinstance(ref.get("path"), str):
            continue
        receipt_path = Path(ref["path"])
        if not receipt_path.is_file():
            continue
        receipt, receipt_fail = load_json_document(receipt_path)
        if receipt_fail or not isinstance(receipt, dict):
            continue
        named = _manifest_by_name(receipt.get("artifact_manifest"))
        plan_entry = named.get("PLAN_SNAPSHOT.json")
        if plan_entry is None or not isinstance(plan_entry.get("path"), str):
            continue
        snapshot, snapshot_fail = load_json_document(Path(plan_entry["path"]))
        if snapshot_fail or not isinstance(snapshot, dict):
            continue
        copies = snapshot.get("snapshot_paths")
        if not isinstance(copies, dict):
            continue
        rel = copies.get(CANONICAL_REGISTRY_REL)
        if not isinstance(rel, str) or not rel:
            continue
        copy = receipt_path.parent / rel
        if copy.is_file() and file_digest(copy) == pinned_hash:
            return copy
    return None


def _check_review_bound_registry_cases(
    failures: list[CheckFailure],
    *,
    review_path: Path,
    candidate_path: Path,
    candidate_doc: Mapping[str, Any] | None,
    pinned_hash: str,
    live_path: Path,
    graph: TaskGraph,
    expected_tasks: list[str],
) -> None:
    live_doc, live_fail = load_json_document(live_path)
    live_ok = not live_fail and isinstance(live_doc, dict)
    live_cases = _registry_cases_by_id(live_doc if live_ok else None)
    pinned_copy = _pinned_registry_snapshot_copy(review_path, candidate_path, candidate_doc, pinned_hash)
    used_live_fallback = pinned_copy is None
    comparison_doc: Mapping[str, Any] | None = None
    if pinned_copy is not None:
        pinned_doc, pinned_fail = load_json_document(pinned_copy)
        if not pinned_fail and isinstance(pinned_doc, dict):
            comparison_doc = pinned_doc
        else:
            used_live_fallback = True
    if comparison_doc is None:
        comparison_doc = live_doc if live_ok else None
        used_live_fallback = True
    comparison_cases = _registry_cases_by_id(comparison_doc)
    loc = str(review_path)
    for case_id in _review_bound_case_ids(graph, expected_tasks, comparison_cases):
        live_case = live_cases.get(case_id)
        if live_case is None:
            detail = f"review-bound case {case_id} changed after the gate closed"
            if used_live_fallback:
                detail = f"{detail}; no pinned registry snapshot copy; fell back to live registry"
            _append(failures, FailureCode.GATE_REVIEW, loc, detail)
            continue
        pinned_case = comparison_cases.get(case_id)
        if pinned_case is None:
            continue
        if pinned_case.get("probe") != live_case.get("probe") or pinned_case.get("expected") != live_case.get("expected"):
            _append(
                failures,
                FailureCode.GATE_REVIEW,
                loc,
                f"review-bound case {case_id} changed after the gate closed",
            )


def verify_gate_review(
    review_path: Path,
    candidate_path: Path,
    candidate_hash: str,
    graph: TaskGraph,
    *,
    amendments_path: Path | None = None,
) -> tuple[CheckFailure, ...]:
    failures: list[CheckFailure] = []
    document, parse_failures = load_json_document(review_path)
    failures.extend(parse_failures)
    if not isinstance(document, dict):
        if not parse_failures:
            _append(failures, FailureCode.GATE_REVIEW, str(review_path), "gate review must be a JSON object")
        return tuple(failures)
    amendments = _load_amendments_document(amendments_path)
    review_date = _draft_date({"drafted_at": document.get("reviewed_at")})
    if document.get("schema_version") != SCHEMA_GATE_REVIEW:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "schema_version must be research-gate-review-v2")
    if document.get("assurance_version") != ASSURANCE_VERSION:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review assurance_version is not current")
    if document.get("verdict") != "pass":
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review verdict is not pass")
    if not isinstance(document.get("reviewed_at"), str) or not document.get("reviewed_at"):
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "reviewed_at is missing")
    if not isinstance(document.get("reviewer"), str) or not document.get("reviewer"):
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "reviewer is missing")
    candidate = document.get("candidate") if isinstance(document.get("candidate"), dict) else {}
    if candidate.get("path") != str(candidate_path) or candidate.get("sha256") != candidate_hash:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review candidate does not match the receipt under verification")
    subphase_id = document.get("subphase_id") if isinstance(document.get("subphase_id"), str) else ""
    phase = document.get("phase") if isinstance(document.get("phase"), str) else ""
    expected_tasks: list[str] = []
    if subphase_id:
        if subphase_id not in graph.known_subphases():
            _append(failures, FailureCode.GATE_REVIEW, str(review_path), f"unknown review subphase {subphase_id}")
        else:
            expected_tasks = [spec.id for spec in graph.for_subphase(subphase_id)]
    elif phase:
        expected_tasks = [spec.id for spec in graph.for_phase(phase)]
        if not expected_tasks:
            _append(failures, FailureCode.GATE_REVIEW, str(review_path), f"unknown review phase {phase}")
    else:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review subphase_id or phase is missing")
    reviewed = document.get("reviewed_task_ids")
    if not isinstance(reviewed, list):
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "reviewed_task_ids is missing")
        reviewed = []
    elif not expected_tasks or set(str(item) for item in reviewed) != set(expected_tasks):
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "reviewed_task_ids do not match the candidate task set")
    findings = document.get("findings") if isinstance(document.get("findings"), list) else []
    open_findings = [item for item in findings if isinstance(item, dict) and item.get("resolution") not in {"resolved", "accepted-limit"}]
    if open_findings:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review has unresolved findings")
    graph_binding = document.get("graph")
    graph_file = _bind_review_file(
        graph_binding,
        failures,
        str(review_path),
        label="graph",
        require_hash_match=False,
    )
    live_graph_hash = file_digest(Path(graph.path))
    if graph_file is not None and graph_file.resolve() != Path(graph.path).resolve():
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review graph is not the current task graph")
    elif isinstance(graph_binding, dict) and _hex_digest(graph_binding.get("sha256")):
        bound_graph_hash = str(graph_binding["sha256"])
        if bound_graph_hash != live_graph_hash and not _graph_hash_connected(
            bound_graph_hash,
            live_graph_hash,
            draft_date=review_date,
            amendments=amendments,
            graph_path=Path(graph.path),
        ):
            _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review graph hash is not the current task graph")
    registry = document.get("registry")
    registry_path = DEFAULT_ROOT / CANONICAL_REGISTRY_REL
    bound_registry = _bind_review_file(
        registry,
        failures,
        str(review_path),
        label="registry",
        require_hash_match=False,
    )
    check_registry_cases = False
    pinned_registry_hash = ""
    if bound_registry is not None and bound_registry.resolve() != registry_path.resolve():
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review registry is not ASSURANCE_CASES.json")
    elif isinstance(registry, dict) and _hex_digest(registry.get("sha256")) and registry_path.is_file():
        pinned_registry_hash = str(registry["sha256"])
        live_registry_hash = file_digest(registry_path)
        if pinned_registry_hash != live_registry_hash:
            connected = _plan_superseded_by_amendments(
                CANONICAL_REGISTRY_REL,
                pinned_registry_hash,
                live_registry_hash,
                draft_date=review_date,
                amendments=amendments,
            )
            if not connected:
                _append(
                    failures,
                    FailureCode.ARTIFACT_HASH,
                    str(registry_path),
                    "registry hash does not match file bytes",
                )
                _append(
                    failures,
                    FailureCode.GATE_REVIEW,
                    str(review_path),
                    "review registry hash is not the current assurance registry",
                )
            else:
                check_registry_cases = True
    commands = document.get("commands")
    if not isinstance(commands, list) or not commands:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review commands are missing")
    elif any(not isinstance(item, dict) or not isinstance(item.get("argv"), list) or not item.get("argv") for item in commands):
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "review commands must include argv")
    snapshots = document.get("code_snapshots")
    matrices = document.get("evidence_matrices")
    if not isinstance(snapshots, dict) or not snapshots:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "code_snapshots binding is missing")
        snapshots = {}
    if not isinstance(matrices, dict) or not matrices:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "evidence_matrices binding is missing")
        matrices = {}
    candidate_doc, candidate_fail = load_json_document(Path(candidate_path))
    failures.extend(candidate_fail)
    if check_registry_cases:
        _check_review_bound_registry_cases(
            failures,
            review_path=review_path,
            candidate_path=Path(candidate_path),
            candidate_doc=candidate_doc if isinstance(candidate_doc, dict) else None,
            pinned_hash=pinned_registry_hash,
            live_path=registry_path,
            graph=graph,
            expected_tasks=expected_tasks,
        )
    task_refs: dict[str, Mapping[str, Any]] = {}
    if isinstance(candidate_doc, dict) and isinstance(candidate_doc.get("task_receipts"), dict):
        task_refs = candidate_doc["task_receipts"]
    for task_id in expected_tasks:
        snap = snapshots.get(task_id)
        _bind_review_file(snap, failures, str(review_path), label=f"code_snapshots[{task_id}]")
        matrix = matrices.get(task_id)
        _bind_review_file(matrix, failures, str(review_path), label=f"evidence_matrices[{task_id}]")
        ref = task_refs.get(task_id)
        if isinstance(ref, dict) and isinstance(ref.get("path"), str) and Path(ref["path"]).is_file():
            child, child_fail = load_json_document(Path(ref["path"]))
            failures.extend(child_fail)
            if isinstance(child, dict):
                named = _manifest_by_name(child.get("artifact_manifest"))
                if isinstance(snap, dict) and named.get("CODE_SNAPSHOT.json"):
                    if snap.get("path") != named["CODE_SNAPSHOT.json"]["path"] or snap.get("sha256") != named["CODE_SNAPSHOT.json"]["sha256"]:
                        _append(
                            failures,
                            FailureCode.GATE_REVIEW,
                            str(review_path),
                            f"code_snapshots[{task_id}] does not match the candidate receipt",
                        )
                    if snap.get("code_sha256") not in {None, child.get("code_sha256")} and snap.get("code_sha256") != child.get("code_sha256"):
                        _append(
                            failures,
                            FailureCode.GATE_REVIEW,
                            str(review_path),
                            f"code_snapshots[{task_id}].code_sha256 does not match the candidate receipt",
                        )
                if isinstance(matrix, dict) and named.get("EVIDENCE_MATRIX.json"):
                    if matrix.get("path") != named["EVIDENCE_MATRIX.json"]["path"] or matrix.get("sha256") != named["EVIDENCE_MATRIX.json"]["sha256"]:
                        _append(
                            failures,
                            FailureCode.GATE_REVIEW,
                            str(review_path),
                            f"evidence_matrices[{task_id}] does not match the candidate receipt",
                        )
    independent = document.get("independent_suite") if isinstance(document.get("independent_suite"), dict) else {}
    if independent.get("checker_sha256") != PINNED_CHECKER_SHA256:
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "independent checker hash is not the pinned suite")
    results_path = independent.get("results_path")
    results_digest = independent.get("results_sha256")
    if not isinstance(results_path, str) or not Path(results_path).is_file():
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "independent suite results path is missing")
        return tuple(failures)
    if _hex_digest(results_digest) and file_digest(Path(results_path)) != results_digest:
        _append(failures, FailureCode.GATE_REVIEW, results_path, "independent results_sha256 does not match file bytes")
    elif not _hex_digest(results_digest):
        _append(failures, FailureCode.GATE_REVIEW, str(review_path), "independent results_sha256 is missing")
    results, result_fail = load_json_document(Path(results_path))
    failures.extend(result_fail)
    if not isinstance(results, dict):
        _append(failures, FailureCode.GATE_REVIEW, results_path, "independent results must be a JSON object")
        return tuple(failures)
    if results.get("harness_sha256") != PINNED_CHECKER_SHA256:
        _append(failures, FailureCode.GATE_REVIEW, results_path, "independent results harness_sha256 is not the pinned suite")
    if results.get("status") != "pass":
        _append(failures, FailureCode.GATE_REVIEW, results_path, "independent suite status is not pass")
    cases = results.get("cases") if isinstance(results.get("cases"), list) else []
    if len(cases) != PINNED_CHECKER_CASES:
        _append(failures, FailureCode.GATE_REVIEW, results_path, "independent suite did not pass all pinned cases")
    seen_cases: list[str] = []
    for index, row in enumerate(cases):
        if not isinstance(row, dict):
            _append(failures, FailureCode.GATE_REVIEW, results_path, f"independent case[{index}] is not an object")
            continue
        name = row.get("case")
        if name not in PINNED_CHECKER_CASE_SET:
            _append(failures, FailureCode.GATE_REVIEW, results_path, f"independent case {name!r} is not a pinned checker case")
        else:
            seen_cases.append(str(name))
        if row.get("passed") is not True:
            _append(failures, FailureCode.GATE_REVIEW, results_path, f"independent case {name} did not pass")
    missing_cases = [name for name in PINNED_CHECKER_CASE_IDS if name not in seen_cases]
    if missing_cases:
        _append(failures, FailureCode.GATE_REVIEW, results_path, f"independent results missing pinned cases: {missing_cases}")
    inputs = results.get("input_hashes") if isinstance(results.get("input_hashes"), dict) else {}
    graph_digest = file_digest(Path(graph.path))
    _require_paired_input_hash(inputs, Path(candidate_path), candidate_hash, failures, results_path, "candidate receipt")
    _require_paired_input_hash(
        inputs,
        Path(graph.path),
        graph_digest,
        failures,
        results_path,
        "current graph",
        superseded_rel=CANONICAL_GRAPH_REL,
        draft_date=review_date,
        amendments=amendments,
        graph_path=Path(graph.path),
    )
    for task_id, ref in task_refs.items():
        if isinstance(ref, dict) and isinstance(ref.get("path"), str) and _hex_digest(ref.get("sha256")):
            _require_paired_input_hash(inputs, Path(ref["path"]), str(ref["sha256"]), failures, results_path, f"task receipt {task_id}")
    return tuple(failures)


def _require_paired_input_hash(
    inputs: Mapping[str, Any],
    path: Path,
    digest_value: str,
    failures: list[CheckFailure],
    results_path: str,
    label: str,
    *,
    superseded_rel: str | None = None,
    draft_date: str | None = None,
    amendments: Mapping[str, Any] | None = None,
    graph_path: Path | None = None,
) -> None:
    candidates = {str(path), str(path.resolve())}
    matched = [key for key in candidates if key in inputs]
    if not matched:
        _append(failures, FailureCode.GATE_REVIEW, results_path, f"independent results keys do not name the {label}")
        return
    for key in matched:
        bound = inputs.get(key)
        if bound == digest_value:
            continue
        connected = False
        if superseded_rel is not None and _hex_digest(bound):
            connected = _plan_superseded_by_amendments(
                superseded_rel,
                str(bound),
                digest_value,
                draft_date=draft_date,
                amendments=amendments,
            )
            if not connected and graph_path is not None:
                connected = _graph_hash_connected(
                    str(bound),
                    digest_value,
                    draft_date=draft_date,
                    amendments=amendments,
                    graph_path=graph_path,
                )
        if not connected:
            _append(
                failures,
                FailureCode.GATE_REVIEW,
                results_path,
                f"independent results {label} path and hash are not bound together",
            )


def verify_subphase_receipt(
    receipt_path: Path,
    *,
    graph: TaskGraph | None = None,
    graph_path: Path | None = None,
    receipts_root: Path | None = None,
    gate_review: Path | None = None,
    amendments_path: Path | None = None,
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
    resolved_amendments = Path(amendments_path) if amendments_path is not None else DEFAULT_AMENDMENTS_PATH
    state = _VerifyState(receipts_root=root, graph=loaded_graph, amendments_path=resolved_amendments)
    blocked = False
    disallowed = False
    for spec in required:
        ref = refs.get(spec.id)
        if ref is None or not Path(ref.path).is_file():
            continue
        child = verify_task_receipt(
            Path(ref.path),
            graph=loaded_graph,
            receipts_root=root,
            amendments_path=resolved_amendments,
            _state=state,
        )
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
        failures.extend(
            verify_gate_review(
                Path(gate_review),
                path,
                file_digest(path),
                loaded_graph,
                amendments_path=resolved_amendments,
            )
        )
    unique = _unique_failures(failures)
    return VerificationResult("subphase", not unique, str(path), unique)


def verify_phase_receipt(
    receipt_path: Path,
    *,
    graph: TaskGraph | None = None,
    graph_path: Path | None = None,
    receipts_root: Path | None = None,
    gate_review: Path | None = None,
    amendments_path: Path | None = None,
) -> VerificationResult:
    path = Path(receipt_path)
    failures: list[CheckFailure] = []
    document, parse_failures = load_json_document(path)
    failures.extend(parse_failures)
    loaded_graph = graph
    if loaded_graph is None:
        loaded_graph, graph_failures = load_task_graph(graph_path)
        failures.extend(graph_failures)
    resolved_amendments = Path(amendments_path) if amendments_path is not None else DEFAULT_AMENDMENTS_PATH
    if document is None or loaded_graph is None:
        return VerificationResult("phase", False, str(path), tuple(failures))
    state = _VerifyState(
        receipts_root=Path(receipts_root) if receipts_root is not None else DEFAULT_RECEIPTS_ROOT,
        graph=loaded_graph,
        amendments_path=resolved_amendments,
    )
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
                                amendments_path=resolved_amendments,
                                _state=state,
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
        failures.extend(
            verify_gate_review(
                Path(gate_review),
                path,
                file_digest(path),
                loaded_graph,
                amendments_path=resolved_amendments,
            )
        )
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
    allows_future_target: bool = False,
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
                allows_future_target=allows_future_target,
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
    cutoffs = issues + decisions
    is_leaf = any(key in node for key in ("artifact_path", "artifact_sha256", "row_ids"))
    if is_leaf and type(node.get("available_at_ns")) is not int:
        _append(failures, FailureCode.LINEAGE_CLOCK, loc, "evidence leaf is missing available_at_ns")
    if available_at_ns is not None:
        for cutoff in cutoffs:
            if available_at_ns > cutoff:
                _append(
                    failures,
                    FailureCode.LINEAGE_CLOCK,
                    loc,
                    f"available_at_ns {available_at_ns} exceeds ancestor cutoff {cutoff}",
                )
    event_at_ns = node.get("event_at_ns") if type(node.get("event_at_ns")) is int else None
    if event_at_ns is not None and not allows_future_target:
        for cutoff in cutoffs:
            if event_at_ns > cutoff:
                _append(
                    failures,
                    FailureCode.LINEAGE_CLOCK,
                    loc,
                    f"event_at_ns {event_at_ns} exceeds ancestor cutoff {cutoff}",
                )
        if available_at_ns is not None and event_at_ns > available_at_ns:
            _append(
                failures,
                FailureCode.LINEAGE_CLOCK,
                loc,
                f"event_at_ns {event_at_ns} exceeds available_at_ns {available_at_ns}",
            )
    digest_value = node.get("artifact_sha256") if _hex_digest(node.get("artifact_sha256")) else node.get("sha256")
    raw_path = node.get("artifact_path") if isinstance(node.get("artifact_path"), str) and node.get("artifact_path") else None
    if raw_path is None and not is_leaf:
        raw_path = node.get("path") if isinstance(node.get("path"), str) and node.get("path") else None
    if is_leaf:
        if not isinstance(node.get("artifact_path"), str) or not node.get("artifact_path"):
            _append(failures, FailureCode.LINEAGE_HASH, loc, "evidence leaf is missing artifact_path")
        if not _hex_digest(node.get("artifact_sha256")) and not _hex_digest(node.get("sha256")):
            _append(failures, FailureCode.LINEAGE_HASH, loc, "evidence leaf is missing artifact_sha256")
        row_ids = node.get("row_ids")
        if not isinstance(row_ids, list) or not row_ids or any(not isinstance(item, str) or not item for item in row_ids):
            _append(failures, FailureCode.LINEAGE_HASH, loc, "evidence leaf is missing row_ids")
            row_ids = []
    if isinstance(raw_path, str) and raw_path:
        file_path = Path(raw_path)
        if not file_path.is_file():
            _append(failures, FailureCode.ARTIFACT_MISSING, raw_path, "lineage artifact does not exist")
        else:
            if _hex_digest(digest_value) and file_digest(file_path) != digest_value:
                _append(failures, FailureCode.LINEAGE_HASH, raw_path, "lineage sha256 does not match file bytes")
            elif digest_value is not None and not _hex_digest(digest_value):
                _append(failures, FailureCode.LINEAGE_HASH, loc, "lineage sha256 is not a lowercase digest")
            if is_leaf and isinstance(node.get("row_ids"), list) and node.get("row_ids"):
                if not _row_ids_resolve(file_path, list(node["row_ids"])):
                    _append(failures, FailureCode.LINEAGE_HASH, loc, "evidence leaf row_ids do not resolve in the artifact")
    for key, value in node.items():
        if key in {"path", "artifact_path", "sha256", "artifact_sha256"}:
            continue
        child_future = True if key in OUTCOME_EDGE_KEYS else False if key in PREDICTOR_EDGE_KEYS else allows_future_target
        _walk_lineage(
            value,
            ancestor_issues=issues,
            ancestor_decisions=decisions,
            manifest_path=manifest_path,
            failures=failures,
            trail=f"{trail}.{key}",
            allows_future_target=child_future,
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
        "drafted_at": "2026-09-14",
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
